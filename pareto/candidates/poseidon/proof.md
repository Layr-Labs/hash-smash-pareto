# Orchard Poseidon, r = 7: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, value-domain powering on truncated point sets with radix-16/32 passes, a Graeffe prefix, inversion-free half-gcd on three rows, one centre

## 1. Claim

Target: `poseidon-orchard-r7-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, seven partial rounds 4, 5, 6, 7, 8, 9 and 10, full rounds 60-63, state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is an algorithm (sections 2-4) with an operation count that bounds every run (sections 6-7) and a success probability derived from two score-critical premises: `H-ONE` (section 9.1), a statement about the fraction of centres at which the fixed digest polynomial has between 1 and 16 usable roots, and `H-NORMAL` (section 9.5), a statement about the normality of the remainder sequence that enters only the success probability. Section 9.2 derives the success probability from them.

* The algorithm: draw a centre `c` from two fresh random words, `c = (w1 2^256 + w2) mod p` (within statistical distance `p/2^512` of uniform on `F_p`, 4.1.1), build the odd part `g_c` of the line polynomial by evaluation and one inverse transform, replace `g_c` by its 27-fold Graeffe transform `g = g_c^(27)` (monic, degree `m`, its roots the `2^27`-th powers of those of `g_c`; section 4.3G), compute `R = S^((p-1)/2^28) mod g` in the value domain by Montgomery powering on two truncated point sets `O1`, `O2` of `n' = 1165 * 2^19 = 610,795,520` points (1165 of the 2048 depth-11 nodes of the subgroup of order `2^30` and of its coset; the method of bradcush `b30de9bf`/`a41aecdd`, there 15 of 16 nodes, section 4.3T; radix-16 and radix-32 passes under the declared 64-word register file, 4.2), take `G = gcd(g, R - 1)` by the inversion-free half-gcd on three rows of bradcush `4bcabff8`, node row transforms in the block form of `27fbfbe7` (outer step `k = 2^j - 1 <= 2^26 - 1`, each matrix applied to the whole pair in place, applies longer than `3 * 2^26` by the in-place block products of block length `3 * 2^23` of the memory cap of weijiekoh `a78f526e`, section 4.4), charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, and if `G` has degree between 1 and `DMAX = 16` isolate a root `y` of `G` in at most `Z = 64` rounds, find `s` with `s^(2^28) = y` and `F(c + s) = F(c - s)` among at most `2^27` candidates (4.1.3), map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39009`: a lower bound for the probability, over the algorithm's fresh random words, that the centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1), `delta = 0.003` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `eps_iso <= 2.371e-15`, `eps_coin <= 65 p / 2^512 <= 1.404e-76`, `eps_g <= 2^27 n' (D - 1) / p < 2^-167` (the centre makes `g` vanish at a point of `O1`, 4.3G) (sections 4.1.1, 4.3T, 9.2). The value the formula gives is `0.390099999999997629` (at or above the organizer floor 0.39); the claim is that value floored at five decimals.
* `time_log2 = 37.33834` in target-compression units (`C(7) = 363` primitive operations per unit): the operation count that bounds every run, derived in section 6 as `T_fixed + K * T_trial + T_off` with `K = 1`, stage C a Graeffe prefix of 27 steps (4.3G) and value-domain powering on truncated point sets (4.3T), stage D the inversion-free half-gcd on three rows charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (4.4, 6.3; the time bound holds for every sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work), stage E at its cap of `Z` rounds at degree `DMAX`, and the scan of stage F at its cap of `2^27` candidates (4.1.3). `N_max = 63,076,203,120,819` operations, `log2(N_max / 363) = 37.33833...`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is bounded by 1,000,000 operations; that bound is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 36.266` (`82,593,207,820` bytes, section 7). The normalized cost is `37.33834 + max(0, 36.266 - 20) = 37.33834 + 16.266 = 53.60434`.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; every random field element is drawn from two fresh words, at most `65` field elements (`130` words) per run (section 4.1.1), and a draw costs 63 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^13`, then the roots of its odd part about a centre, found, after a Graeffe prefix (Dandelin-Graeffe root squaring), with a gcd against `S^((p-1)/2^28) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Against the previous version of this entry (normalized cost 53.58080, the same algorithm and package), one change of the charge: the node charge `node_bf(j)` of stage D, `j = 7, ..., 26`, is charged in this package (E.2.1) as the per-block upper bound of the rules of 4.2 and 4.4, in which every block is charged for the twiddles its position shares, so the charge can only exceed the schedule's count, with a one per cent allowance; it is not fitted, and no integer is taken from the node column of `27fbfbe7`, whose construction is credited. Row D `20,419,615,490,996` (was `19,398,840,003,317`), `N_max` `63,076,203,120,819` (was `62,055,427,633,140`), `time_log2` `37.33834` (was `37.31480`), normalized cost `53.60434` (was `53.58080`), still `0.06157` below the frontier's `53.66591`; memory unchanged at `2^36.266`, and every other charge, the premises, the coins and the experiments are unchanged.
* Against our r = 7 entry `706a2b7c` (normalized cost 53.69942), one change to its algorithm: a Graeffe prefix (4.3G). Stage C first applies 27 Graeffe steps `g(Y) <- E(Y)^2 - Y O(Y)^2` on `O1` (`127,253,062,382` operations each) and then raises `S` to `(p-1)/2^28` (199 squaring steps in place of 226); the gcd keeps exactly the `2^27`-th powers of the usable roots (`1 <= deg G <= k(c)`), and stage F finds the root of `g_c` above the isolated one by a scan of at most `2^27` candidates on the line map (4.1.3). Row C `41,812,848,268,920` (was `43,442,204,569,481`), row F `82,679,483,798` (was `47,012`); memory unchanged. `H-NORMAL` is stated for the pair of the transformed polynomial and its organizer-run tests compute that pair (9.5, 10.5.1); `H-ONE`, every other charge and the other experiments are unchanged.
* Prior entries: `706a2b7c` (53.69942) is our r = 7 entry `3901ce7c` (normalized cost 53.75572, the same algorithm and package) with three changes in stage D (4.2, 4.4, 7): (i) the stage-D twiddle table is that of its largest transform, the `3*2^25` points of the products of the `j = 26` node (`2^24` entries), in place of a table for `3*2^28` points; (ii) the block products of the memory cap run at the block length `3 * 2^23` (transforms of `3 * 2^24` points) in place of `3 * 2^22`; (iii) each `3*2^a`-point block transform is charged as the radix-3 layer and three rows of `2^a` points, as every `3*2^a`-point transform of this model, and the block size enters the plan_invN misses as one more size. Row D `23,169,854,954,737` (was `22,811,543,133,445`); memory `2^36.266` (was `2^36.330`), the allocator high-water mark of one trial, reached in stage D at the allocation of the `j = 26` node arena (section 7). Every other charge, the premises and the experiments are unchanged. `3901ce7c` (normalized cost 53.75572) is our r = 7 entry `2bacc5bb` (54.23018) with three changes: (i) the loads and stores of the data words of the transform-pass blocks of 4.3T are charged one operation each, base plus index (4.2; the wording of the accepted `89b451ff` and `070a02b2`); (ii) the outer steps of stage D run bradcush's inversion-free half-gcd on three rows (entry `4bcabff8`; the transform reuse of `b30de9bf`), as in our r = 3 entry `bcf8e01c`, ported to `r = 7` and charged in this cost model (section 4.4), in place of the lean cofactor-free node of bradcush `e6dcb600`/`1aa56884`; (iii) layers 1-7 of the truncated transforms run class-batch by class-batch with the positions above `n'` of the batch in a `3,604,480`-word buffer and the `1,572,864` positions above `n'` below layer 7 in a tail buffer, in place of the scratch of `N - n' = 462,946,304` words (4.3T, 7). `2bacc5bb` improves our r = 7 entry `538ef0ed` (the one-centre algorithm of our r = 6 entry `c318f442` with bradcush's truncated-point-set stage C, entries `b30de9bf`, `a41aecdd`, the lean cofactor-free half-gcd with the memory cap of weijiekoh's entry `a78f526e`, and the memory schedule of 0xshikhar's entries `52120fad`, `716c3818`) by three changes: (i) the kernel charges of stage C (4.3T): the pruned top pass, the recovery with the path value in a register, the scaling fused into the adjacent pass, and the batch-inversion chunk in the scratch above `n'`; (ii) each line evaluation of stage B charged at the operations it executes, `155 + 21 r = 302`, in place of `C(7) = 363` (section 3), as in our r = 4 entry; (iii) the transforms of stage C run radix-16 and radix-32 passes on the 64-register machine stated as a restriction in claim.json (4.2, 4.3T), as in our r = 3 entry `ef123c2b`. The premises, the coins, stages A and E-G and the organizer-run tests are those of `538ef0ed` (`H-ONE` at `q = 0.3931`, `H-NORMAL` at `delta = 0.003` with the split of cryptogakusei's entry `4888e783`, the ABORT discipline of bradcush's `e6dcb600` and the test form of gta6rp's entry `bef31fdd`). The memory is the allocator high-water mark of the one trial (section 7).
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1), a statement about the fraction of good centres, and `H-NORMAL` (score-critical for the success probability only, section 9.5), bradcush's premise on the normality of the remainder sequence stated with the allowance `delta = 0.003` and supported by organizer-run tests. Both are statements about probability. The machine (64 registers of 256 bits and constants as immediates; every load, store and spill counted) is stated as a restriction in claim.json, as the accepted entries `89b451ff` and `fb176310` state theirs, not as a heuristic (4.2). The costs are the declared cost model of this entry: the charging rules of section 4.2 with that register file, the inversion-free half-gcd of stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (Appendix E). Everything else is proved or counted here.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`. `(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`. The algorithm uses the line `j = 0`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant `M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS, nonzero on the deployed constants, checked). Let `(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, `d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i` (the supports are disjoint). After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8, 9, 10 (partial), 60, 61, 62, 63 (full) put thirteen S-box layers on top of an affine map, and the digest is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^13 = D = 1,220,703,125`. The leading coefficient is obtained by propagating leading coefficients through the thirteen layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used: `f_D(0) = 0x28cf6129b49568f76cbbcb977dae09a15d9b0b6c18a191886de5f7aae3a6297b` (computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau` against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`), hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 610,351,562`, `g_c` has degree exactly `m` and leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`, `W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The useful roots are the roots in `F_p` with `S^((p-1)/2) = 1`: they are the roots of `gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p`; `S = 0` is not a root of `S^((p-1)/2) - 1`). This gcd divides the squarefree `S^((p-1)/2) - 1`, so it is a product of `k(c)` distinct linear factors over `F_p` (9.1); stage D computes instead the gcd of 4.3G, whose roots are their `2^27`-th powers.

Construction of `g_c` by evaluation. `H = 805,306,368 = 3 * 2^28` divides `p - 1` (`p - 1 = 2^32 * 3 * q`) and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`; one inverse transform of size `H` returns the coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). Each of the `2H = 1,610,612,736` evaluations of `F` is charged at the operations it executes (the line evaluation `tail_eval`): the affine start `alpha + beta W` (3 multiplications, 3 additions: 6), round 2 (three S-boxes `x^5` of 3 operations each and the MDS, 9 multiplications and 6 additions: 24; its constants are in `alpha`), round 3 (3 constant additions, 9, 15: 27), the seven partial rounds (3 + 3 + 15 = 21 each), rounds 60-62 (27 each) and round 63 (3 + 9 and row 0 of the MDS, 3 multiplications and 2 additions: 17), `155 + 21 r = 302` operations at `r = 7`; rounds 0 and 1 are not executed (section 2). The loop work (two point additions, one subtraction, one multiplication by `1/(2 zeta^i)`, the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, the store with its address, the loop control and the bit-reversed index) is charged on top (stage B, section 6), with the twiddle table of the transform, built by stage B (4.2).

## 4. The algorithm (one centre, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   constants (once; no twiddle table: each stage builds the table of its own transforms, 4.2)
setup:  the line (line_setup) (once)
for t = 1, ..., K (K = 1):            [the test t <= K is made at the start of the trial; no exit except success]
  A  c := (w1 * 2^256 + w2) mod p from two fresh random words w1, w2 (4.1.1)
  B  g := monic g_c, by section 3 (1,610,612,736 evaluations + one inverse NTT of size 805,306,368 + the nonzero-leading-coefficient test + normalisation)
  C  g := g^(27): 27 Graeffe steps on O1 (section 4.3G); R := S^((p-1)/2^28) mod g, in the value domain on the truncated point sets O1, O2 of n' = 610,795,520 points (section 4.3T): 199 squaring steps, 45 of them also multiplying by S
  D  G := gcd(g, R - 1) (monic): the inversion-free half-gcd on three rows with the in-place applies of the memory cap (section 4.4), charged for the normal remainder sequence with the quotient and return tests; on any other case ABORT (6.3)
  E  if deg G = 0 or deg G > DMAX: trial ends. Otherwise isolate a root y of G (4.1.2); if none within Z = 64 rounds: trial ends.
  F  u := a 2^28-th root of y (28 Tonelli-Shanks square roots, 2-adicity 32); for j = 0, ..., 2^27 - 1: s := u mu^j, W1 = c + s, W2 = c - s, until F(W1) = F(W2) (4.1.3); tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (300 operations each) are equal and the pairs differ -> output; otherwise the trial ends
```

4.1.1 Coins (ruling `04c0dd43`, finding F-EVAL-001). The only randomness is the cost-model random-word primitive. Every random field element of the algorithm (the centre `c` of stage A and each shift of stage E) is drawn from two fresh 256-bit words `w1, w2`: each is reduced mod `p` by three conditional subtractions (exact, `2^256 < 4p`), and `x = (w1 mod p) * (2^256 mod p) + (w2 mod p)` in `F_p`, i.e. `x = (w1 2^256 + w2) mod p` with `w1 2^256 + w2` uniform on `[0, 2^512)`. There is no rejection and no retry. A draw is 63 operations: per word 1 random-word operation, 1 load, 1 store, 3 control, the reduction 9 and its loop control 11 (26 per word, 52), two Montgomery conversions 2, the load of the constant `2^256 mod p` 1, one multiplication 1, one addition 1, entry 2, the two addresses 4. At most `1 + Z = 65` draws (`130` words) per run. With `2^512 = Q p + r`, each residue has `Q` or `Q + 1` preimages, so one draw is within statistical distance `r (p - r) / (p 2^512) <= p / 2^512 = 2^-258.0` of uniform on `F_p`; the 65 draws are independent, so the joint distribution of all the coins of a run is within `eps_coin = 65 p / 2^512 <= 1.404e-76` of the distribution with every draw exactly uniform (total variation is subadditive over independent components).

4.1.2 Stage E: isolating a root of `G`. With `1 <= deg G <= DMAX = 16`, a Cantor-Zassenhaus split with random shifts isolates one linear factor in at most `Z = 64` rounds at degree `<= 16`; `eps_iso <= 2.371e-15` bounds the probability that 64 rounds fail to isolate a root when `deg G >= 1` (section 9.4).

4.1.3 Stage F: the root of `g_c` above `y`. By 4.3G, `y = S^(2^27)` for a usable root `S` of `g_c`, and the solutions of `S'^(2^27) = y` are `u^2 mu^(2j)`, `j < 2^27`, where `u^(2^28) = y` and `mu` is a fixed primitive `2^28`-th root of unity (`2^28 | p - 1`; a constant of the offline derivation, 6.2). `u` comes from 28 successive Tonelli-Shanks square roots: `y` is a `2^28`-th power, and if `x` is a `2^k`-th power with `1 <= k <= 28`, both square roots of `x` are `2^(k-1)`-th powers (`-1` is a `2^(k-1)`-th power, `2^k | p - 1`). The scan takes `s = u mu^j` for `j = 0, 1, ..., 2^27 - 1` and stops at the first `j` with `F(c + s) = F(c - s)` (two line evaluations of section 3). For `S' = s^2` a root of `g_c` this holds, because `F(c + s) - F(c - s) = 2 s g_c(s^2)`, so the scan stops at the latest at the `j` of `S`; any stop has `s != 0` (`y != 0`) and `F(c + s) = F(c - s)`, a collision by 2.4. Charge per candidate: `s <- s mu` 1, `c + s` and `c - s` 2, two line evaluations `2 * 302`, their calls 4, the comparison and branch 2, the loop control 3: `616`; at most `2^27` candidates, `82,678,120,448`, and the loop exit 2. The 28 square roots are charged `47,012` each (the whole row F of the algorithm without the prefix, a square root and the back-map), `1,316,336`, and the back-map `47,012`: row F = `82,679,483,798`.

### 4.2 Machine model and charging rules (summary; `C(7) = 363`)

Every field operation, load, store, control operation and random word is one primitive operation; `C(r) = 216 + 21 r = 363` primitive operations is one target-compression unit. The register file is 64 words of 256 bits (the machine restriction of claim.json: it holds the 32 values and 28 of the 31 twiddles of a radix-32 block, or the 16 values and 15 twiddles of a radix-16 block or group; every other value, the 3 spilled twiddles of a radix-32 group included, is charged as a load or store; a load or store of a data word of a block of a transform pass of 4.3T is one operation, its address the base plus index of the load or store itself: one load per word fetched from memory and one store per word written, the wording of the accepted entries `89b451ff` and `070a02b2`), the only register assumption; the algorithm runs on one thread, no dispatch. Allocation: one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes. A block of more than `2^19` bytes is served by the two-ended pool (one region, two ends, first-fit in address order, the statements marked `# pool:H` using the high end and, with the depth-parity placement of section 7, the end `(j + bit8) mod 2` of a half-gcd node at depth `j`); every smaller block by its slab class (the least `j >= 7` with `2^j >= need`, a slot of `2^j` bytes). The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows (a pool request `97` operations besides the walk and `13` per block examined, a slab request at most `126`, a free `81` for a slab block and at most `105` for a pool block). The memory of both allocators is the arena of section 7. Twiddle tables: none is built in init; stage B, the Newton and quotient products of stage C and stage D each build the table of their own largest transform (`2^(a-1)` entries for `3*2^a` points: its root, 5 operations per entry and the loop; stage D: `a = 25`, the products of the `j = 26` node, 4.4) and free it at the end of that work, charged in the stage's row; the passes of 4.3T use two-level root tables of `4 x 4,096` words (stage C).

### 4.3G The Graeffe prefix

Definition. For `h` monic of even degree `m` write `h(X) = E(X^2) + X O(X^2)`; its Graeffe transform is `h~(Y) = E(Y)^2 - Y O(Y)^2`, so `h~(X^2) = h(X) h(-X)` and `h~` is monic of degree `m` with roots the squares of the roots of `h` (with multiplicity). Stage C first replaces `g = g_c` by `g^(27)`, 27 Graeffe steps, then computes `R = S^e mod g^(27)`, `e = (p-1)/2^28` (2-adicity 32), and stage D takes `G = gcd(g^(27), R - 1)`.

Lemma. `G` is the product of `(Y - y)` over the distinct values `y = S^(2^27)`, `S` a usable root of `g_c` (a nonzero square in `F_p` with `g_c(S) = 0`, section 3). Proof: `g^(27)(Y) = prod_i (Y - S_i^(2^27))` over the roots `S_i` of `g_c` in an algebraic closure; `Y^e - 1` is squarefree and its roots are the `2^28`-th powers of `F_p^*`. If `S_i^(2^27) = u^(2^28)` with `u` in `F_p^*`, then `S_i = u^2 zeta` with `zeta^(2^27) = 1`, so `zeta` is in `F_p` and `zeta = xi^2` with `xi^(2^28) = 1` (`2^28 | p - 1`), and `S_i = (u xi)^2` is a nonzero square of `F_p`; conversely `S = v^2` gives `S^(2^27) = v^(2^28)`. So `deg G` is the number of distinct `2^27`-th powers of the usable roots: `1 <= deg G <= k(c)` when `k(c) >= 1`, and `deg G = 0` when `k(c) = 0`; the event `E_c` of 9.2 gives `1 <= deg G <= DMAX`.

Execution (on the point set `O1` of 4.3T). One step: `E` (`m/2 + 1` coefficients) and `O` (`m/2`) are read from `g` at stride 2 by the top passes of two truncated forwards, which load only the input blocks below the length (3 or 2 of the 8 per offset, two offset ranges per batch; butterflies only on nonzero inputs; no zero-fill); the fused bottom pass forms `G = (E^2 - y O^2)/N` at each point `y` of `O1` between the forward and the inverse bottom layers (`y` is the last-layer twiddle of its butterfly, in a register: two squarings, two multiplications, one subtraction, 5 per point); one truncated inverse stores the new coefficients into the array of `g` (those above `m` come out zero). `E` and `O` on `O1` use the arrays of `A` on `O2` and of `A` on `O1` before stage C fills them, with a batch buffer of `5,177,344` words of their own, used by one transform at a time and freed after the prefix; no array is added and the high-water mark of section 7 is unchanged. One step is `127,253,062,382` operations (Appendix E.1), 27 steps; stage C then runs 199 squaring steps in place of 226 (the exponent loses 27 low zero bits). A step saves one squaring step (`187,599,592,060`) for `127,253,062,382` and doubles the scan of 4.1.3 (`2^s * 616`); `s = 27` minimises the total.

Every map is exact; no premise is added to the time or the memory. The zero test of `k1` (4.3T) now concerns `g^(27)`: `g^(27)(y) = 0` for `y` in `O1` only if `g_c(x) = 0` for one of the `2^27` values `x` with `x^(2^27) = y` (in `F_p` or an extension); for each such `x`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g^(27) vanishes on O1) <= 2^27 n' (D - 1) / p = eps_g < 2^-167`.

### 4.3T Stage C in the value domain on truncated point sets (the method of bradcush `b30de9bf`/`a41aecdd`, 1165 of 2048 nodes)

Point sets. `N = 2^30` divides `p - 1` (2-adicity 32). Let `psi` have order `2^31`, `H_N = <psi^2>` and `Y = X^(2^19)`. `H_N` is the union of the 2048 depth-11 nodes `{x : x^(2^19) = r_j}`, `r_j` the 2048-th roots of unity in transform (bit-reversed) order; `O1` is the union of the first 1165 nodes, `n' = 1165 * 2^19 = 610,795,520 >= m + 1 = 610,351,563` points, and `O2` the same 1165 nodes of the coset `psi H_N` (`x^(2^19) = r'_j`, `r'_j^2048 = -1`), disjoint from `O1`. `P1 = prod_{j<1165} (Y - r_j)` has degree `n'`, vanishes on `O1` and is the nonzero constant `P1(r'_j)` on node `j` of `O2`; `delta_j = 1/P1(r'_j)` (1165 table constants).

Truncated transforms (bradcush `b30de9bf` 4.3, generalized as the truncated Fourier transform of van der Hoeven, ISSAC 2004). A polynomial of degree `< n'` is `sum_{k<2048} P_k Y^k` with `deg P_k < 2^19` and `P_k = 0` for `k >= 1165`; its values on the 1165 nodes determine it and are determined by it (the CRT for the 1165 coprime moduli `Y - r_j`, whose product `P1` has degree `n'`). The forward transform runs the top 3 layers on all `N/8` offsets (no truncation saving is charged), the middle layers only on the blocks above present nodes, and the bottom 3 layers on the `n'` points. The inverse runs the same layers in reverse, scales each 8-point block of its bottom pass by `diag(1, c^-1 J)` (`c = y^8` of the block, `V^T V = 8 diag(1, cJ)`; 7 multiplications and the load of `c^-1`, 9 operations per block), and recovers the residues of the dropped part `[1165, 2048)`, the maximal subtrees `{1165}`, `{1166..1167}`, `{1168..1183}`, `{1184..1215}`, `{1216..1279}`, `{1280..1535}`, `{1536..2047}` (depths 11, 10, 7, 6, 5, 3, 2), from the known zero chunks `P_k = 0` along their paths to the root, as bradcush recovers the one dropped leaf; with the value of the path held in a register this is charged 8 operations (3 multiplications, 3 additions, the load of the known value) per point of a dropped subtree per layer of its path and one store (2) per point. The positions above `n'` that a transform touches are held in two buffers (one transform runs at a time). Layers 1-7 (the top pass, the first middle pass and the recoveries of the dropped subtrees of depths 7, 6, 5, 3, 2) act on each class of the `128` positions with equal low 23 bits separately (`73` below `73 * 2^23`, `55` above: the depth-7 nodes 73-127), so they run class-batch by class-batch, `128` batches of `65,536` classes, the `55` positions above of each class of the batch held in a batch buffer of `3,604,480` words and discarded after the batch; the `3 * 2^19 = 1,572,864` positions in `[n', 73 * 2^23)` that the passes below layer 7 touch (the dropped depth-11 nodes 1165-1167, the subtrees of depths 11 and 10) are a tail buffer held whole. Charged once per batch: the 8 groups, the pass overhead and the batch loop of the first middle pass (`8 * 20 + 20 + 3`), the top-pass overhead with its 16 inner loops, one per range of `65,536` consecutive offsets (`60 + 20 + 16 * 5`), and the path constants of the five in-batch recoveries reloaded (`163`: 23 levels, 3 constants each loaded at 2, and 5 loops at 5); before the top of each truncated forward the zero-fill of lane 4 above `n'` (the `7` positions of each class of the batch, per batch, and the tail once; a store, 2, each and the loop). The passes are fused as in `b30de9bf` 4.5 under the declared 64-word register file (4.2), the 30 layers split 3 | 4, 4, 5, 5, 5 | 4: a bottom pass (16-point blocks: forward layers, the pointwise map, inverse layers; one set of 15 twiddles for both directions, 19 operations per block: two loads from the two-level table, one multiplication, three squarings, eleven multiplications by register constants; `V^T V = 16 diag(1, cJ)` with `c = y^16` of the block, so every inverse bottom pass scales each block by `diag(1, c^-1 J)`: 15 multiplications and the load of `c^-1`, 17 operations per block), two middle passes of radix 16 (per block 16 loads and 16 stores at one operation each, 32 butterflies and 5 control, 133; the 15 twiddles of a group in registers, formed from the running group root by one multiplication, 3 squarings and 11 multiplications by register constants, 20 per group with its control), three middle passes of radix 32 (per block 32 loads and 32 stores at one operation each, 80 butterflies, the loads of the 3 twiddles that do not fit beside the 32 values (6) and 5 control, 315; per group the 31 twiddles from the running group root, 1 + 4 + 22 operations, the stores of the 3 spilled ones and control, 38), and a pruned top pass that fuses the inverse top of one set with the forward top of the other: only the `b = 5` depth-3 subtrees that hold points of the 1165 nodes are formed or read (the butterflies of the 8-point top block counted on the needed and nonzero lanes, `_top_counts`), and the coset twiddle is applied on those `b` blocks.

Montgomery powering (`b30de9bf` 4.5). For residues of degree `< n'`, `Mont(A, B) = (A B + u g)/P1` with `u = -A B / g mod P1` (`deg u < n'`); the division by `P1` is exact, `Mont(A, B) = A B / P1 mod g`, and `deg Mont(A, A) <= n' - 2`, so `X Mont(A, A)` has degree `< n'`. A residue `A` (representing `S^e P1`) is held by its values on `O1` and on `O2`, each up to a tracked scalar. One step: `U = A^2 k1` on `O1` (`k1 = -1/(N^3 g)` there; `u` is determined by its values on `O1`); `U` to `O2` (truncated inverse on `O1`, truncated forward on `O2`); `B2 = (A2^2 + U g) delta_j` on node `j` of `O2`, which is `Mont(A, A)` up to the tracked scalar because `P1 = 1/delta_j` there, times the point `x` when the exponent bit is 1; `B2` to `O1` (truncated inverse on `O2`, truncated forward on `O1`). No `1/N` is executed inside the steps (the scalars are tracked, 2 operations per step). Per point and step: on `O1` `sqr, LD k1, mul` (4); on `O2` `LD A2, sqr, LD g, mul, add`, the multiplication by `delta_j`, `ST` (10) and the load of `delta_j` per block (2); 3 more for a 1-bit (the load of the point and a multiplication).

Entry and exit. `g` (coefficients after the Graeffe prefix of 4.3G, its slots above `m` zero) goes to `O1` and `O2` (a truncated forward each; every scaling of this section, `1/N` and the coset twist, is a running product fused into the adjacent pass, 2 operations per point). The start residue is `A0 = X^v P1 mod g`, `v = 2^27 = 134,217,728` (VSHIFT = 2): `q = floor(X^v P1 / g)` has `ell = v + n' - m + 1 = 134,661,687` coefficients and is formed from the Newton reciprocal of the reversed `g` and one product (transforms of up to `3*2^27` points, with their own twiddle table, freed after the quotient); on node `j` of `O2`, `x^v P1(x) = r'_j^256 P1(r'_j)` is a constant, so `A0 = x^v P1 - q g` there is one truncated forward of `q` and one pointwise pass (8 per point); then `A0` goes to `O1`. `k1` is formed by chunked batch inversion on `O1` (chunks of `2^16` points: prefix products, one inversion, two multiplications per point; the `2^16` prefixes are kept in the tail and batch buffer, which no transform uses at that time); each chunk product is tested for zero before its inversion (2 per chunk), and a zero ends the trial: for fixed `x != 0`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g vanishes on O1) <= eps_g < 2^-167` for the transformed `g` (4.3G, 9.2). The exit is one step with multiplier 1 (`Mont(A, 1)`) and two truncated inverses with their scaling, which return `kappa R` (`kappa` the tracked scalar) and `g` in coefficient form; the gcd is scale-invariant, so stage D receives `kappa R - kappa`. There are `199` squaring steps (the exponent `(p-1)/2^28`, 4.3G), `45` of them also multiplying by `S`.

Exactness and memory. Every map above is exact (Montgomery products of polynomials of degree `< n'`, held bijectively by their values on 1165 nodes); no premise is added to stage C. The live set of the stage is four arrays of `n'` words (`g` on `O2`, `A` on `O2`, `A` on `O1`, `k1` on `O1`), the tail and batch buffer of `5,177,344` words, the tables (`1,195 + 16,384` words: 30 constants, the 1165 `delta_j`, the two-level root tables) and, while `q` is formed, the Newton arrays. The step-by-step count is expanded in Appendix E.1 and totals **row C = 41,812,848,268,920** (section 6).

### 4.4 Stage D: the inversion-free half-gcd on three rows (bradcush `4bcabff8`), with the in-place applies of the memory cap

`G = gcd(g, R - 1)` is computed by bradcush's inversion-free half-gcd (entry `4bcabff8`, with the transform reuse of `b30de9bf`; read as text only, ported and charged in this cost model as in our r = 3 entry `bcf8e01c`). Matrices and remainders are kept up to nonzero scalars with pseudo-division (`b^2 a = Q b + e`, `Q` of degree 1 on the normal sequence), so no field inversion runs inside the recursion; the gcd is the same up to a scalar and is made monic at the end. A node of budget `k = 2^j - 1` makes two child calls of budget `2^(j-1) - 1`; its products run on `3 * 2^(j-1)` points, the rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), each a power-of-two transform of `n` points in block form after a twist, joined by a 3-row CRT: `(c, d) = adj(M1)(a, b)` on the top window, the pseudo-division, and `M = M1 [[Q, 1], [b^2, 0]] M2`; the row `Y - 1` values of each child's matrix are returned by the child, and the row values of `M1` are kept from the apply and reused in the product. Block form, the product passes of `27fbfbe7` section 4.2, on the same 64-word register file: a pass of `k <= 4` layers at level `l0` of a `2^a`-point row forms its twiddles as running factors. The schedule forms the twiddles of a position once and shares them among the `2^l0` blocks that use them; the charge uses the conservative per-block reading, in which every block forms them itself. Per pass and per layer the step and chain constants are 150 operations. Per block, and there are `2^(a-k)` blocks, the `2^k - 1` twiddles and 5 control cost `2^k + 4`; each block loads `2^k` values, stores `2^k` values and makes `k*2^(k-1)` butterflies at 3, plus 5 control, which is `2*2^k + 3*k*2^(k-1) + 5`. Sharing the twiddles per position can only reduce the count, so the per-block charge is an upper bound. The passes of a row of `2^a` points run in one loop from level 0 with `k = min(4, a - l0)` layers per pass. The node charge `node_bf(j)`, one integer at each `j = 7, ..., 26`, is charged in this package as that per-block upper bound (E.2.1: the two child calls, the row transforms of the top window, the pointwise passes, the inverse transforms, the 3-row CRT, the pseudo-division and the allocations), with a one per cent allowance, the kernel of `27fbfbe7` being credited for the construction and for no integer; the top window of the node at `j` is `L(j) = 2^(j+1) - 1` coefficients, and E.2.1 shows `L(j)` at most the shorter operand of the call at every `j` of the trial. The outer applies stay on the shared-table transforms of this section and still read the stage-D twiddle table of `2^24` entries. The bump arena stays `1,073,741,568` words at `j = 26`, which is `16*2^26 - 256`, the same size that kernel uses (`16*2^28 - 256 = 4,294,967,040` words at `j = 28` in `27fbfbe7`). The twist roots of order `2n` and `4n` come from the squaring chain of those running factors; the scales `1/2^a` (`a <= 27`) are a table of 27 words built at the entry of stage D (`1/2 = (p + 1)/2` an immediate, 26 multiplications). The base case (budget 63) runs two remainder steps per pass over its window. Driver: while `(n - 1)/2 >= 127`, one outer step calls the node on the top window of the pair with `k = 2^j - 1` the largest with `k <= min(2^26 - 1, (n - 1)/2)`, applies `adj(M)` to the whole pair in place, and makes one division with the quotient test; the apply is that of the memory cap (the method of weijiekoh `a78f526e`, its `mat_apply` LMAX, as in `2bacc5bb`): an apply to a pair longer than `LMAX = 3 * 2^26` coefficients is done by the block products of scheme (a) at the block length `3 * 2^23` (transforms of `3 * 2^24` points: the radix-3 layer and three rows of `2^24` points, charged as every `3*2^a`-point transform of this model), each block of the operands transformed once, the transforms of a slot multiplied pointwise and summed, and each output slot inverse transformed and overlap-added in place into the output array. The last outer step (degree below `255`) is the lean cofactor-free half-gcd of bradcush `e6dcb600`/`1aa56884` as in `2bacc5bb`, and below degree `192` classical division steps finish. The working arrays of a node live in one bump arena (an allocation or release is 10 operations) of `1,073,741,568` words at `j = 26`, the peak of its recursion; the cap `j <= 26` bounds the arena, which with the pair, the matrix of the outer step and the stage-D twiddle table sets the high-water mark of the trial (section 7). On the normal sequence every length, budget and allocation is a function of `m` alone. The row is charged for the normal remainder sequence (every quotient of degree 1), the case of the premise `H-NORMAL` (9.5): every division and pseudo-division tests that its quotient has degree 1 and every call tests on return that it removed exactly its budget (2 operations each), and a zero remainder also ends the trial; on any other case the trial ABORTs (the allocator is reset and the run ends without output, section 6.3). By the prefix lemma of 6.3 every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, so the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The total is **row D = 20,419,615,490,996** (section 6.3, 6; Appendix E.2).

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G = gcd(g, R - 1)`, whose roots are the values `y = S^(2^27)` of the usable roots `S` of `g_c` (4.3G); stage F stops only at an `s != 0` with `F(c + s) = F(c - s)` (4.1.3), so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Ledger: operation count (primitive operations; `C(7) = 363`)

| row | what is charged | operations |
| --- | --- | --- |
| init | constants and bookkeeping (once; no twiddle table, 4.2) | 17,978 |
| setup | the line (`line_setup`, once) | 4,910 |
| A (per trial) | stage bookkeeping, loop test and update, the coin draw (63, two words), one allocation | 1,228 |
| B (per trial) | `1,610,612,736` evaluations of `F` on the line at their executed `155 + 21 r = 302` operations each (section 3), the loop work, the twiddle table and the inverse transform of size `805,306,368`, the normalisation | 760,889,235,868 |
| C (per trial) | the Graeffe prefix, 27 steps (section 4.3G), then `S^((p-1)/2^28) mod g` in the value domain on the truncated point sets `O1`, `O2` (1165 of 2048 nodes, `n' = 610,795,520`), VSHIFT = 2, 199 squaring steps, radix-16/32 passes (section 4.3T); expanded in Appendix E | 41,812,848,268,920 |
| D (per trial) | inversion-free half-gcd of `(g, R - 1)` on three rows with the in-place applies of the memory cap, charged for the normal remainder sequence with the quotient and return tests (sections 4.4, 6.3); expanded in Appendix E | 20,419,615,490,996 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16`, each with one draw of 63 (two words) | 166,081,821 |
| F (per trial) | the `2^28`-th root of `y` (28 square roots at 47,012), the scan of at most `2^27` candidates at 616 and its exit, the back-map 47,012 (4.1.3) | 82,679,483,798 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 363 + 32` | 8,292 |
| trial-loop (per trial) | trial-loop bookkeeping (12) and the allocator reset after an ABORT (1,000), charged in every trial | 1,012 |
| plan_invN misses | one per distinct plan size (and the block size `3 * 2^24` of 4.4) | 135,916 |
| output rows | the fixed output rows (stages H and I) | 3,390,080 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + 1 * T_trial + T_off` | **63,076,203,120,819** |

`T_off = 1,000,000`; `T_trial = A + B + C + D + E + F + G + trial-loop = 63,076,198,571,935`; `T_fixed = init + setup + plan_invN misses + output rows = 3,548,884`; `K = 1`, so `N_max = 3,548,884 + 63,076,198,571,935 + 1,000,000 = 63,076,203,120,819`. `log2(N_max / 363) = 37.33833...`, rounded up at five decimals to `37.33834`. Rows C and D are expanded part by part in Appendix E (E.1, E.2) from the dimensions of 4.3T and the half-gcd levels with the kernel charges of 4.2; the parts add up exactly to `41,812,848,268,920` and `20,419,615,490,996`.

### 6.1 Validation
The kernel charges and the allocator rules are those compared with the instrumented totals of our executed runs at `r = 3, 4, 5` (the arena rule within 64 bytes of the measured heap peaks there); the truncated-set stage C (4.3T) has no executed counterpart, and its count is the formula of Appendix E.

### 6.2 Offline derivation
The literals of the sources (Montgomery forms of the organizer constants, `5^q`, `2^65`, the exponent `(4(p-1)+1)/5`) are derived offline in at most `1,000,000` operations, declared `preprocessing_log2 = 20` and inside `N_max`.

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry `e6dcb600`)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g, R - 1)`, `g = g_c^(27)` (4.3G): every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the re-centring division of a node, the division of each repetition of the outer loop, each step of the base case) tests, before it does any work beyond reading the two leading coefficients, that its quotient has degree 1 (2 operations); (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); a zero remainder inside `hgcd` or in the outer-loop division also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state at the start of the trial (`1,000` operations, charged in every trial). Lemma (prefix; `e6dcb600`, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each node of budget `2^j - 1` splits into two calls of budget `2^(j-1) - 1` (each lean call at `k1 = ceil(k/2)`) and, with every quotient of degree 1, every degree in the tree is fixed by `m` and the number of quotients so far, and the budgets of the outer loop (`k = 2^j - 1 <= min(2^26 - 1, (n - 1)/2)`, then `ceil((n+1)/2)`, section 4.4) are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's `hgcd` calls and divisions produce has degree at least the base-case bound, so every gcd of degree at most `DMAX = 16` first appears in the classical Euclid below the base-case degree, after a prefix of the degree-0 work; a zero remainder earlier ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The node follows `4bcabff8`, the lean call `1aa56884` proof 4.4 and the in-place applies `a78f526e` proof 4.4, all read as text only (no entry script was run, compiled or imported). Appendix E.2 expands, for `r = 7`, the charge of stage D for the normal sequence with the tests, `20,419,615,490,996`, repetition by repetition.

The `r = 7` trial (`~82.6 GB`, `~6.2e13` operations) exceeds the organizer sandbox (128 MiB, 20 s), so the costs are the exact formula counts of sections 6 and 7; zero-fill clearing is charged (ruling `3476cad8`) and the 64-word register file is the machine restriction of claim.json.

## 7. Memory: the arena of one trial

The arena is the capacity of the allocator of 4.2 on the allocation/free sequence of the trial. Appendix E.3 runs the allocator on every allocation and free of the trial in the order of the program and reports the two-ended-pool high-water mark (the largest sum of the extents of the two ends over the trial), the slab area and the peaks of the live set per stage. The two-ended pool takes the blocks of more than `2^19` bytes and is placed with depth-parity ends and in-place `R*Q` with two spare slots charged (the `POOL_PLACE = 20` discipline). Under the H-NORMAL ABORT stage D the stage-D live set holds the **normal-case division arrays**: on the normal sequence every quotient has degree 1, so each division forms only the quotient of two coefficients and the remainder, and a trial with any other sequence ends (ABORT) after a prefix of these allocations (6.3), so the normal-case walk bounds every trial. With the node arena of 4.4 (`j <= 26`) and the in-place applies of the memory cap the stage-D live peak is `82,577,450,688` bytes (in the two-ended pool `82,577,449,728` bytes: the pair `g`, `R` carried in at the two ends, `39,090,913,408`; the stage-D twiddle table of `2^24` entries, `536,870,976`; the four entries of the matrix of the outer step, `8,589,935,104`; the bump arena of the `j = 26` node, `34,359,730,240`; in the slab classes `960` bytes of small blocks), above the stage-C peak `82,287,666,560` (4.3T: the tail and batch buffer in place of a scratch of `N - n'` words); the one event of the stage-D trace of Appendix E.3 that raises the pool's high-water mark is the allocation of the arena of the `j = 26` node. The high-water mark is `82,577,449,728` bytes, reached in stage D (the pair carried in at the two ends, the stage-D twiddle table, the matrix of the outer step and the node arena), plus 128 bytes so the unused middle is always at least 128 bytes. The Graeffe prefix (4.3G) holds `E` and `O` on `O1` in the arrays of `A` on `O2` and on `O1` before stage C fills them, with a batch buffer of `5,177,344` words that it frees: it adds no array and leaves the high-water mark unchanged (Appendix E.3). The slab classes take the smaller blocks: `10,425,088` bytes. Stages E and later hold at most 16 small arrays and the free-list heads: `16,896` bytes. The arena is `82,587,891,840` bytes (two-ended pool `82,577,449,728 + 128`, slab `10,425,088`, stages E and later `16,896`). Peaks of the live set per stage (bytes): A `19,545,456,704`; B `49,610,227,904`; C `82,287,666,560`; D `82,577,450,688`. With `5,250,444` bytes of code and static data and a `65,536`-byte stack, the footprint is `82,593,207,820` bytes `= 2^36.266`, rounded up at three decimals. No stored advice; each twiddle table is built at run time by the stage that uses it and charged in that stage's row (4.2).

## 8. Review points, answered by location

1. Row D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (6.3): by the prefix lemma every trial executes a prefix of the normal-case work, so the time and memory bounds hold for every sequence; `H-NORMAL` (9.5) enters only the success probability.
2. The node budget cap and the memory cap (4.4) are constants of the algorithm (`k = 2^j - 1 <= 2^26 - 1`, `LMAX = 3 * 2^26`, block length `3 * 2^23`); its extra transform work is charged in row D, and its effect on the memory is read from the allocation walk of Appendix E (the high-water mark `82,577,449,728` is set in stage D, at the allocation of the `j = 26` node arena, the stage-D live peak `82,577,450,688`; the stage-C peak `82,287,666,560` is below it).
3. Row B reproducible from sections 3 and 6 (evaluations * 302, the operations of one line evaluation, + the loop work, the twiddle table and the inverse transform + normalisation). The 64-word register file (the machine restriction of claim.json, 4.2) is the only register assumption; every value beyond it is charged as a load or store.
4. The 1,000,000-op offline figure is a declared bound (`preprocessing_log2 = 20`), score effect < 4e-7 bit.
5. The mem penalty uses the rounded-up `mem_log2`, a self-penalizing over-charge.
6. `success = q - delta - eps_coin - eps_iso - eps_g >= 0.39` from the premises `H-ONE` and `H-NORMAL` (9.2, 9.5) with `K = 1`, `q = 0.3931`, `delta = 0.003`; the value is `0.390099999999997629`. The `H-ONE` allowance below the law value is stated exactly (`0.3934693 - 0.3931 = 0.0003693`; `q <= 151/384 = 0.3932292`, the four-moment Bonferroni bound, 9.1), and `delta = 0.003` is the declared premise; the 3,072 organizer-seeded sequences are reproducible observations consistent with it (10.5.1).
7. The organizer-checkable output is the returned witness-pair count; the premises hold under trusted execution of the submitted program, disclosed, not claimed as an organizer-verified proof.
8. The Graeffe prefix (4.3G) is exact and adds nothing to the premises of the time or the memory; the success bound uses `H-NORMAL` stated for the pair of the transformed polynomial (9.5), whose organizer-run tests compute that pair (10.5.1).

## 9. The premise and the success bound

### 9.1 H-ONE
The number of centres `c` with `1 <= k(c) <= 16` is at least `q p = 0.3931 p`, `k(c)` the number of nonzero squares `S` with `g_c(S) = 0` (stage D returns `G` with `1 <= deg G <= k(c)` when `k(c) >= 1`, 4.3G). The premise states `q = 0.3931`, the law value `1 - e^(-1/2) = 0.3934693` (9.3) less the extrapolation allowance stated exactly as `0.0003693`; it is also `0.0001292` below the four-moment Bonferroni bound `151/384 = 0.3932292`. The split of the allowance between `H-ONE` and `H-NORMAL` follows cryptogakusei's entry `4888e783`: with `delta = 0.003` (9.5) the bound of 9.2 needs `P(E_c) >= 0.3931` at `K = 1`. The extrapolation, the monodromy theorem at N = 2, 3 and the toy-field and organizer-run evidence are in the claim.json heuristic `H-ONE` and sections 10.3, 10.5.1.

### 9.2 The success bound
The centre is a fresh draw. For a centre `c` let `E_c` be the event `1 <= k(c) <= DMAX` (H-ONE, `P(E_c) >= q = 0.3931`) and `N_c` the event that the remainder sequence of `(g, R_c - 1)` (`g = g_c^(27)`, 4.3G) is normal down to its gcd (H-NORMAL, 9.5, `P(not N_c) <= delta = 0.003`). The Graeffe prefix and the value-domain stage C reproduce `g^(27)` and `R = S^((p-1)/2^28) mod g^(27)` exactly (4.3G, 4.3T) and add no premise; stage C needs `g^(27)` nonzero on `O1`, which fails with probability at most `eps_g = 2^27 n' (D - 1) / p < 2^-167` over the centre (4.3G). If `E_c` and `N_c` hold and `g^(27)` has no zero on `O1`, stages C and D run to their end and return `G = gcd(g^(27), R_c - 1)` with `1 <= deg G <= DMAX` (4.3G); a successful isolation and the scan of 4.1.3 then end in a verified collision. For `c` uniform `P(E_c and N_c) >= q - delta`, so with one centre (the event `g^(27)` zero on `O1` subtracted as `eps_g`)

`success = 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g`, `K = 1`.

Transfer to the written sampler (F-EVAL-001): `q - delta - eps_iso - eps_g` bounds the success probability of the run whose draws are exactly uniform on `F_p` (the premises and the isolation lemma are stated for uniform draws). The success of a run is an event of the vector of its draws, and the actual draws of 4.1.1 are within total variation `eps_coin` of the uniform vector, so the actual success probability is at least the ideal one minus `eps_coin`.

With `q = 0.3931`, `delta = 0.003`, `eps_iso <= 2.371e-15`, `eps_coin <= 1.404e-76`, `eps_g < 2^-167`: `q - delta = 0.3901`, and the value is `0.390099999999997629 >= 0.39`. The bound stays at or above `0.39` for every `delta <= 0.0030999` at `q = 0.3931`. The probability is over the random words of 4.1.1 for the fixed target, not over targets and not a sampled frequency.

### 9.3 Monodromy (support for H-ONE)
The roots of `G(c,t) = g_c(t^2)` come in pairs `+-t_i`, so the monodromy lies in the hyperoctahedral group `B_m` and `k(c)` counts positive Frobenius fixed points; for `B_m` this is Poisson(1/2) in the limit, `P(k >= 1) = 1 - e^(-1/2) = 0.3934693`, and Bonferroni at order 4 gives `P >= 151/384 = 0.3932292`. A theorem at two and three layers (Aubry-Perret, monodromy `B_12`, `B_62`); false for permutation polynomials, for decomposable `F` with imprimitive monodromy, and at one layer.

### 9.4 Isolation lemma
With `1 <= deg G <= 16`, a random-shift split isolates a linear factor within `Z = 64` rounds except with probability `eps_iso <= 2.371e-15`. Finite derivation: `G` divides `Y^((p-1)/2^28) - 1` (4.3G), a divisor of `Y^(p-1) - 1`, so it is squarefree and splits into `d = deg G <= 16` distinct linear factors `X - t_i` over `F_p`. A round with shift `a` keeps a nontrivial part of the current factor `H` under `gcd(H, (X + a)^((p-1)/2) - 1)` (or `X + a` itself when `a = -t_i`), so two roots `t_i != t_j` stay together only if `chi(t_i + a) = chi(t_j + a)` or `a` is in `{-t_i, -t_j}`. Since `sum_a chi((a + t_i)(a + t_j)) = -1` for `t_i != t_j`, exactly `(p - 3)/2` shifts give equal nonzero characters, so for `a` uniform on `F_p` the pair stays together with probability at most `((p - 3)/2 + 2)/p = 1/2 + 1/(2p)`; each shift is a fresh random word reduced mod `p`, within statistical distance `2^-128` of uniform (4.1.1), so per round the bound is `1/2 + 2^-127`, independently across rounds. The parts are nested, so the factor kept after 64 rounds holds two roots only if one of the at most `C(16,2) = 120` pairs was never separated in 64 rounds. By the union bound `eps_iso <= 120 (1/2 + 2^-127)^64 < 6.6e-18 <= 2.371e-15`; the looser stated value `2.371e-15` is kept, so every other number is unchanged.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries `e6dcb600` and `1aa56884`; allowance split of cryptogakusei's `4888e783`; organizer-run tests in the form of gta6rp's `bef31fdd`)
**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(h_c, R_c - 1)`, where `h_c = g_c^(27)` is the 27-fold Graeffe transform (4.3G) of the monic odd part `g_c` of section 3 (monic, degree `m = 610,351,562`) and `R_c = S^((p-1)/2^28) mod h_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.003` (`2^-8.38`). Stage D is charged for the normal sequence; every division tests its quotient degree and every call of the half-gcd its return, and on any other case the trial ends (ABORT, sections 4.4, 6.3). The premise enters only the success probability (9.2): the time and memory bounds hold for every remainder sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work (6.3). For a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes, each a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-194`; the premise extrapolates a much weaker form of this random-pair behaviour (`delta = 0.003`) to the structured pair `(h_c, R_c - 1)`. Measured support is organizer-run (10.5.1): the six experiments `euclid-normal-n2-t256-l2-g27-a` to `-f` compute the complete Euclidean sequence of `(h_c, R_c - 1)` for this construction (27 Graeffe steps, exponent `(p-1)/2^28`) on the truncation `F_2` (`m = 12`) for 256 organizer-seeded trials of two centres each (3,072 sequences in all) and return a witness pair exactly when both sequences of a trial are normal; `euclid-normal-n3-t24-g27` and `euclid-normal-n4-t2-g27` do the same at `m = 62, 312`. Zero abnormal in the 3,072 sequences is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (`delta = 0.003` is the declared premise). Not verified at `r = 7`, which would need the computation itself; the organizer-run tests are at `m = 12` to `312`, far below `m`.

## 10. Experiments

Program `experiments/exp_euclid.py` (euclid-normal, one-centre) and `experiments/exp_line.py` / `experiments/exp_lowbits.py` (line-ladder and lowbits-birthday), with `experiments/manifest.json`.

10.3 The truncations. `F_N(c + X)` is coordinate 0 after the first `N` S-box layers on the line `j = 0`; `F_2`, `F_3`, `F_4` have odd parts of degree `m = 12, 62, 312`. The arithmetic monodromy at `N = 2, 3` is `B_12`, `B_62` (Grok jobs 136, 137, re-run on the deployed constants).

10.5.1 Organizer-run set. euclid-normal-n2-t256-l2-g27-a to -f compute the complete Euclidean sequence of `(h_c, R_c - 1)` (the pair of 9.5: 27 Graeffe steps, exponent `(p-1)/2^28`) for this construction at depth `N = 2` (`m = 12`), each for 256 organizer-seeded trials of two centres (512 sequences per entry, 3,072 in all; the final letter only changes the organizer seeds); euclid-normal-n2-t256-g27, -n3-t24-g27 and -n4-t2-g27 compute one sequence per trial at `m = 12, 62, 312`. A trial returns a witness pair exactly when its sequences are normal; the count of trials that return a pair is a reproducible observation consistent with the premise H-NORMAL (9.5). We do not treat the organizer-seeded centres as independent unselected samples and draw no population bound from these runs: `delta = 0.003` is the declared premise (9.5), carried by its stated support, not by an interval computed from the experiments. one-centre-n2-t256 and one-centre-n3-t24 run one trial of the algorithm with the Graeffe prefix off (`s = 0`: the gcd against `S^((p-1)/2) - 1` and a square root in place of the scan; they test `H-ONE`, a statement about `g_c` that the prefix does not change, 4.3G) at depth `N = 2, 3` per organizer seed and return a witness pair exactly when the sequence is normal, `1 <= k(c) <= 16` and the isolated root gives a verified collision of `F_N`; the returned count is a reproducible observation (9.1), reported as an observation with no interval inferred. line-ladder-w6/-w8/-w10/-w12 and lowbits-birthday corroborate the antipodal structure, not the score-critical basis. Our runs of the six -l2-g27 entries with local seeds (one CPU; 9.24 to 10.41 s each on our workstation): 3,072 sequences, all normal, 256 pairs per entry; the gcd had positive degree for 1,181 of the 3,072 centres. Our runs of -n2-t256-g27, -n3-t24-g27 and -n4-t2-g27: 256, 24 and 2 sequences, all normal. The organizer-checkable output is the returned witness-pair count; the premises H-ONE and H-NORMAL hold under trusted execution of the submitted program.

## Appendix E: rows C and D expanded, and the allocation walk of one trial

Rows C and D and the arena of section 7 are exact counts of the algorithm of sections 4.2-4.4 at `r = 7`. E.1 and E.2 expand each row into its parts, each part a count from the dimensions of 4.3G, 4.3T and the half-gcd levels with the charges of 4.2; each table adds up exactly to its row. E.3 is the allocator of 4.2 run on every allocation and free of the trial in program order: the totals, the live-set peaks per stage, the two-ended-pool high-water mark, the slab classes, and the stage-D allocation/free trace against the high-water mark.

### E.1 Row C = 41,812,848,268,920

Row C is the sum of the steps of section 4.3T in the order the stage runs them:

| part of stage C | operations |
| --- | ---: |
| plans of the passes, the exponent, the node constants and the two-level root tables (built), the zero-fill of `g` above `m`, the first allocations | 544,472,830 |
| the allocation of `A` on `O1`; the Graeffe prefix (4.3G): `27` steps (below) and the allocation and free of its batch buffer | 3,435,832,685,025 |
| the Newton reciprocal of the reversed `g` to `ell` coefficients (doubling steps, products with running twiddle factors) | 399,878,785,853 |
| the product `q = floor(X^v P1 / g)` (one product of `2 ell - 1` points) and its copy | 117,213,396,532 |
| `g` to `O1` and `O2` (two scaling passes, two truncated forwards; the tail and batch buffer allocated) | 81,575,564,080 |
| the start residue `A0` on `O2` (zero-fill, scaling, truncated forward of `q`, pointwise pass at 8) | 47,034,012,102 |
| `A0` to `O1` (one extension: truncated inverse, scaling, truncated forward) | 93,659,733,965 |
| `k1` on `O1` by chunked batch inversion (chunks of `2^16`, zero tests) | 9,034,164,922 |
| the squaring steps (step 6; below) | 37,414,776,215,140 |
| the exit step `Mont(A, 1)` (pointwise passes and one extension), the frees | 105,112,150,328 |
| two truncated inverses with scaling (`kappa R` and `g` in coefficient form), the frees, the closing control | 108,187,087,143 |
| stage bookkeeping (entry, exit) | 1,000 |
| **row C** | **41,812,848,268,920** |

The squaring steps: `154` steps with exponent bit 0 and `45` with bit 1, `154 * 187,599,592,060 + 45 * 189,431,978,620 = 37,414,776,215,140`. One step (`tr_step`, 4.3T) is:

| part of one step (bit 0) | operations |
| --- | ---: |
| bottom pass on `O1` (`U = A^2 k1`, 4 per point) | 12,559,482,900 |
| four middle-pass sets (inverse and forward, both sides), 28,788,577,744 each | 115,154,310,976 |
| two fused top passes (inverse top, coset twiddle, forward top), 10,603,220,992 each | 21,206,441,984 |
| bottom pass on `O2` (`B2 = (A2^2 + U g) delta_j`, 10 per point for bit 0) | 16,224,256,020 |
| loads of `delta_j` (2 per block of 16 points) | 76,349,440 |
| two recoveries of the dropped subtrees, 11,189,375,360 each | 22,378,750,720 |
| step control | 20 |
| **one step, bit 0** | **187,599,592,060** |

A step with bit 1 adds 3 per point of `O2` in its bottom pass: `189,431,978,620 - 187,599,592,060 = 1,832,386,560 = 3 * 610,795,520`.

The Graeffe prefix (4.3G): `27` steps of `127,253,062,382` each, `3,435,832,684,314`; with the allocation of `A` on `O1` and the allocation and free of the batch buffer of the prefix, `3,435,832,685,025`. One Graeffe step (`gt2_step`) is:

| part of one Graeffe step | operations |
| --- | ---: |
| two forward top passes, `E` and `O` read from `g` at stride 2 (`tr_top_half`) | 5,809,635,266 |
| three middle-pass sets (forward `E`, forward `O`, inverse), 28,788,577,744 each | 86,365,733,232 |
| fused bottom pass (forward bottom layers of `E` and `O`, `G = (E^2 - y O^2)/N` at 5 per point, inverse bottom layers) | 17,445,847,060 |
| inverse top pass (stores into `g`) | 6,442,471,424 |
| recovery of the dropped subtrees | 11,189,375,360 |
| step control | 40 |
| **one Graeffe step** | **127,253,062,382** |

Pass charges (4.3T, `TR_CFG`: top `3` | middle 4, 4, 5, 5, 5 | bottom `4` of the 30 layers, `n' = 610,795,520`): bottom block of `2^4` points with its twiddles, middle blocks and groups of radix 16/32, top blocks of `2^3` points over all `N / 2^3` offsets; the positions above `n'` that layers 1-7 touch are those of the batch buffer, one batch of classes at a time, and below layer 7 those of the tail buffer (4.3T). Middle-pass sets `tr_middle = 28,788,577,744`; top pass, fused, `10,603,220,992`; one recovery `11,189,375,360`.

### E.2 Row D = 20,419,615,490,996

The Euclid driver of 4.4 makes 36 repetitions. Repetitions 1-35: the inversion-free node of budget `k = 2^j - 1` (the largest with `k <= min(2^26 - 1, (n - 1)/2)`) on the top window, the apply of `adj(M)` to the whole pair in place, then one division with the quotient and return tests; `node` is `node_bf(j)`, the per-block upper bound of the node charged in E.2.1, `apply` that of the apply, the last column the repetition with the call, the matrix allocations, the arena, the division and the tests. Repetition 36 (`(n - 1)/2 < 127`) is the lean half-gcd of `2bacc5bb`; below degree `192` the classical Euclid runs 100 steps.

| repetition | operand lengths | j | k | node | apply | repetition total |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 610,351,563, 610,351,562 | 26 | 67,108,863 | 1,924,381,774,770 | 603,803,376,098 | 2,536,333,795,978 |
| 2 | 543,242,699, 543,242,698 | 26 | 67,108,863 | 1,924,381,774,770 | 531,194,917,050 | 2,462,718,703,970 |
| 3 | 476,133,835, 476,133,834 | 26 | 67,108,863 | 1,924,381,774,770 | 473,560,049,299 | 2,404,077,203,259 |
| 4 | 409,024,971, 409,024,970 | 26 | 67,108,863 | 1,924,381,774,770 | 409,062,337,666 | 2,338,572,858,666 |
| 5 | 341,916,107, 341,916,106 | 26 | 67,108,863 | 1,924,381,774,770 | 336,453,878,610 | 2,264,957,766,650 |
| 6 | 274,807,243, 274,807,242 | 26 | 67,108,863 | 1,924,381,774,770 | 278,819,010,859 | 2,206,316,265,939 |
| 7 | 207,698,379, 207,698,378 | 26 | 67,108,863 | 1,924,381,774,770 | 214,321,299,226 | 2,140,811,921,346 |
| 8 | 140,589,515, 140,589,514 | 26 | 67,108,863 | 1,924,381,774,770 | 141,712,840,170 | 2,067,196,829,330 |
| 9 | 73,480,651, 73,480,650 | 25 | 33,554,431 | 900,333,132,147 | 77,857,522,378 | 978,789,552,435 |
| 10 | 39,926,219, 39,926,218 | 24 | 16,777,215 | 422,287,751,373 | 37,897,028,764 | 460,532,019,807 |
| 11 | 23,149,003, 23,149,002 | 23 | 8,388,607 | 197,363,294,165 | 18,843,422,983 | 216,428,127,698 |
| 12 | 14,760,395, 14,760,394 | 22 | 4,194,303 | 91,823,096,254 | 12,664,370,811 | 104,645,963,055 |
| 13 | 10,566,091, 10,566,090 | 22 | 4,194,303 | 91,823,096,254 | 9,255,802,710 | 101,174,480,394 |
| 14 | 6,371,787, 6,371,786 | 21 | 2,097,151 | 42,450,470,455 | 6,220,311,905 | 48,734,906,510 |
| 15 | 4,274,635, 4,274,634 | 21 | 2,097,151 | 42,450,470,455 | 4,200,593,059 | 46,683,730,384 |
| 16 | 2,177,483, 2,177,482 | 20 | 1,048,575 | 19,685,298,618 | 2,015,802,139 | 21,718,038,987 |
| 17 | 1,128,907, 1,128,906 | 19 | 524,287 | 9,082,582,333 | 970,375,052 | 10,062,031,295 |
| 18 | 604,619, 604,618 | 18 | 262,143 | 4,163,217,559 | 466,103,300 | 4,634,462,609 |
| 19 | 342,475, 342,474 | 17 | 131,071 | 1,890,561,890 | 243,632,112 | 2,137,369,672 |
| 20 | 211,403, 211,402 | 16 | 65,535 | 861,649,115 | 163,882,254 | 1,027,723,999 |
| 21 | 145,867, 145,866 | 16 | 65,535 | 861,649,115 | 105,325,574 | 968,184,279 |
| 22 | 80,331, 80,330 | 15 | 32,767 | 389,607,871 | 50,763,061 | 441,089,002 |
| 23 | 47,563, 47,562 | 14 | 16,383 | 174,299,901 | 25,900,772 | 200,672,983 |
| 24 | 31,179, 31,178 | 13 | 8,191 | 76,755,539 | 17,446,439 | 94,551,408 |
| 25 | 22,987, 22,986 | 13 | 8,191 | 76,755,539 | 12,679,087 | 89,661,176 |
| 26 | 14,795, 14,794 | 12 | 4,095 | 33,908,447 | 8,538,481 | 42,612,038 |
| 27 | 10,699, 10,698 | 12 | 4,095 | 33,908,447 | 5,354,917 | 39,367,034 |
| 28 | 6,603, 6,602 | 11 | 2,047 | 14,743,091 | 3,600,774 | 18,416,815 |
| 29 | 4,555, 4,554 | 11 | 2,047 | 14,743,091 | 2,542,382 | 17,327,703 |
| 30 | 2,507, 2,506 | 10 | 1,023 | 6,259,996 | 1,204,454 | 7,491,320 |
| 31 | 1,483, 1,482 | 9 | 511 | 2,554,241 | 646,798 | 3,220,229 |
| 32 | 971, 970 | 8 | 255 | 1,025,073 | 435,284 | 1,475,707 |
| 33 | 715, 714 | 8 | 255 | 1,025,073 | 270,564 | 1,307,147 |
| 34 | 459, 458 | 7 | 127 | 379,741 | 181,545 | 570,876 |
| 35 | 331, 330 | 7 | 127 | 379,741 | 132,297 | 519,708 |

| part of row D | operations |
| --- | ---: |
| the 35 repetitions above (outer step: node, apply, call; then the division with the quotient and return tests) | 20,419,480,219,408 |
| repetition 36: operands 203, 202, the lean half-gcd of `1aa56884` with `k = 101` (charge 666,600), the division and tests | 671,141 |
| the classical Euclid below degree 192 (100 steps, quotient test each) | 377,670 |
| driver entry (the table of the 27 scales `1/2^a`: one allocation, 26 multiplications, 27 stores, the loop) | 381 |
| driver exit (the frees, inversion of the leading coefficient, normalisation) | 2,863 |
| stage bookkeeping (entry, the stage-D twiddle table of 4.2, exit, the free of `g`) | 134,219,533 |
| **row D** | **20,419,615,490,996** |

The components of row D outside the node column, `135,271,588` in all, are charged by the rules of 4.2 for the operations they execute, and none of them reads `node_bf(j)`: repetition 36 (`671,141`) is the lean cofactor-free half-gcd of `1aa56884` at `k = 101` on the operands `203, 202`, the kernel charge `666,600` of that call (its own two remainder steps per pass over its window) plus the division and its two tests, and it runs below `127`, where the three-row node is not called; the classical Euclid (`377,670`) is 100 division steps below degree `192`, each with its quotient test, charged over the lengths of the pair; the driver entry (`381`) is the build of the table of the 27 scales `1/2^a` (`a <= 27` at `r = 7`: one allocation, 26 multiplications, 27 stores and the loop, 4.2); the driver exit (`2,863`) is the frees, the inversion of the leading coefficient and the normalisation; the stage bookkeeping (`134,219,533`) is the entry and exit of stage D, the stage-D twiddle table of `2^24` entries built at the rate of 4.2 and the free of `g`. These six parts are functions of `m`, of the degree at which the driver stops and of the tables of 4.2 alone — none of them calls the node, reads its charge or depends on the pass schedule of E.2.1 — so they are unchanged when the node column is charged as the per-block upper bound, and only the `node` column of the 35 repetitions above moves. The 35 repetition totals sum to `20,419,480,219,408`; adding the tail `135,271,588` gives row D `20,419,615,490,996`.

#### E.2.1 The node charge `node_bf(j)`, a per-block upper bound

`node_bf(j)`, one integer at each `j = 7, ..., 26`, is the charge of the node of budget `2^j - 1` of 4.4, computed here from the charging rules of 4.2 and 4.4; the construction (the inversion-free half-gcd on three rows of `4bcabff8`, the node structure of `27fbfbe7`) is credited, and no integer is taken from its column. The schedule shares the twiddles of a position among the `2^l0` blocks that use them; the charge uses the conservative per-block reading, in which every block forms the twiddles of its position itself, so it is an upper bound on the operations the schedule executes. A one per cent allowance, declared in the recursion below, covers the control not modelled block by block. The charged integers are:
`j = 7`: `379,741`; `j = 8`: `1,025,073`; `j = 9`: `2,554,241`; `j = 10`: `6,259,996`; `j = 11`: `14,743,091`; `j = 12`: `33,908,447`; `j = 13`: `76,755,539`; `j = 14`: `174,299,901`; `j = 15`: `389,607,871`; `j = 16`: `861,649,115`; `j = 17`: `1,890,561,890`; `j = 18`: `4,163,217,559`; `j = 19`: `9,082,582,333`; `j = 20`: `19,685,298,618`; `j = 21`: `42,450,470,455`; `j = 22`: `91,823,096,254`; `j = 23`: `197,363,294,165`; `j = 24`: `422,287,751,373`; `j = 25`: `900,333,132,147`; `j = 26`: `1,924,381,774,770`.

*Passes.* A node of budget `2^j - 1` works on `n = 2^(j-1)` and `a = j - 1`; its products run on `3 n` points, the rows `Y - 1`, `Y + 1`, `Y - i` of `n` points each. One row transform of `2^a` points runs its `a` layers in one loop from level 0, `k = min(4, a - l0)` layers per pass, so the levels are `0, 4, 8, ...` and the last pass has width `a mod 4` when `4` does not divide `a`. A pass of `k` layers at level `l0` has `2^(a-l0-k)` positions, each with `2^k - 1` twiddles, and `2^(a-k)` blocks of `2^k` points. The schedule forms the twiddles of a position once and shares them among the `2^l0` blocks; charging every block as if it formed them itself, the pass costs
`P(a, l0, k) = 150 k + 2^(a-k) (2^k + 4) + 2^(a-k) (2*2^k + 3 k 2^(k-1) + 5) = 150 k + 2^(a-k) (3*2^k + 3 k 2^(k-1) + 9)`:
`150` per pass and layer for the step and chain constants, `2^k + 4` per block for its `2^k - 1` twiddles and 5 of control, `2*2^k + 3 k 2^(k-1) + 5` per block for its `2^k` loads, `2^k` stores, `k 2^(k-1)` butterflies at 3 and 5 of control (4.4). Since the blocks of a position share the twiddles in the schedule, the per-block charge is at least the schedule's count. The forward and the inverse transform are the same passes: `F(a) = I(a) = sum over the passes of P(a, l0, k)`. At `a = 25` (the `j = 26` node) the passes are

| level `l0` | width `k` | positions `2^(a-l0-k)` | blocks `2^(a-k)` | `2^k + 4` | `2*2^k + 3k2^(k-1)+5` | `P(a,l0,k)` |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 4 | 2,097,152 | 2,097,152 | 20 | 133 | 320,864,856 |
| 4 | 4 | 131,072 | 2,097,152 | 20 | 133 | 320,864,856 |
| 8 | 4 | 8,192 | 2,097,152 | 20 | 133 | 320,864,856 |
| 12 | 4 | 512 | 2,097,152 | 20 | 133 | 320,864,856 |
| 16 | 4 | 32 | 2,097,152 | 20 | 133 | 320,864,856 |
| 20 | 4 | 2 | 2,097,152 | 20 | 133 | 320,864,856 |
| 24 | 1 | 1 | 16,777,216 | 6 | 12 | 301,990,038 |
| | | | | | **`F(25)`** | **2,227,179,174** |

and at every `a` of the trial:

| `a` | passes `(l0, k)` | `F(a)` |
|---:|---|---:|
| 6 | (0, 4), (4, 2) | 2,040 |
| 7 | (0, 4), (4, 3) | 3,378 |
| 8 | (0, 4), (4, 4) | 6,096 |
| 9 | (0, 4), (4, 4), (8, 1) | 15,750 |
| 10 | (0, 4), (4, 4), (8, 2) | 29,532 |
| 11 | (0, 4), (4, 4), (8, 3) | 58,482 |
| 12 | (0, 4), (4, 4), (8, 4) | 119,304 |
| 13 | (0, 4), (4, 4), (8, 4), (12, 1) | 310,686 |
| 14 | (0, 4), (4, 4), (8, 4), (12, 2) | 607,284 |
| 15 | (0, 4), (4, 4), (8, 4), (12, 3) | 1,224,906 |
| 16 | (0, 4), (4, 4), (8, 4), (12, 4) | 2,509,152 |
| 17 | (0, 4), (4, 4), (8, 4), (12, 4), (16, 1) | 6,195,702 |
| 18 | (0, 4), (4, 4), (8, 4), (12, 4), (16, 2) | 12,192,396 |
| 19 | (0, 4), (4, 4), (8, 4), (12, 4), (16, 3) | 24,578,850 |
| 20 | (0, 4), (4, 4), (8, 4), (12, 4), (16, 4) | 50,138,040 |
| 21 | (0, 4), (4, 4), (8, 4), (12, 4), (16, 4), (20, 1) | 119,147,598 |
| 22 | (0, 4), (4, 4), (8, 4), (12, 4), (16, 4), (20, 2) | 235,146,468 |
| 23 | (0, 4), (4, 4), (8, 4), (12, 4), (16, 4), (20, 3) | 473,435,514 |
| 24 | (0, 4), (4, 4), (8, 4), (12, 4), (16, 4), (20, 4) | 962,596,368 |
| 25 | (0, 4), (4, 4), (8, 4), (12, 4), (16, 4), (20, 4), (24, 1) | 2,227,179,174 |

*The recursion.* With `lc(l) = 3 l + 2` (loop control), `cp(l) = 4 l + lc(l)` (copy), `zf(l) = 2 l + lc(l)` (zero fill), `ac(l, u) = (7 + u) l + lc(l)` (a window of `l` coefficients, `u = 1` subtracting), `crt(n) = 22 n + lc(n)` (three-row CRT), `for8(n) = 3 (n/8) + 3`, `pw(n, 0) = for8(n) + 7 n`, `pw(n, 1) = pw(n, 2) = for8(n) + 10 n` (pointwise passes), `row(L, r) = cp(min(L, n)) + zf(max(0, n - L)) + ac(max(0, L - n), [r = 2]) + 2 n [r > 0] + F(a)`, `inv(r) = F(a) + (1 + [r > 0]) n` and `S = {1, 2}` (all three rows at `j = 7`), the node of budget `2^j - 1` is charged

`pd(j) = 184 + 2 pd(j-1) + sum_(r=0)^2 (row(2^(j+1), r) + row(2^(j+1) - 1, r)) + 8 sum_(r in S) row(n, r) + 6 (pw(n, 0) + pw(n, 2)) + 12 (pw(n, 0) + pw(n, 1)) + 6 sum_(r=0)^2 inv(r) + 6 crt(n) + 30 + 13 (2^j - 1) + lc(2^j - 1) + 3 (25 n + lc(n))`, `node_bf(j) = ceil(101 (pd(j) + 10) / 100)`,

where the terms charge, in this order: the node's own entry and exit (184); the two child calls of budget `2^(j-1) - 1` (`2 pd(j-1)`); the six row transforms of the two top windows (the `3 n` and `3 n - 1` coefficients of `c` and `d` beyond the row: `cp(n)` for the row, `ac(3 n)` or `ac(3 n - 1)` for the window, `2 n` for the rows `Y + 1` and `Y - i`); the eight row products of the returned matrix rows (the rows of `M1` kept from the apply, those of `M2` returned by the child); the six pointwise passes of the apply and the twelve of the matrix product; the six inverse transforms of the apply; the 3-row CRT that joins the three rows; the pseudo-division over the `2^j - 1` coefficients of the window (13 operations per coefficient, loop control) with its fixed part; the three coefficient arrays of `n` words; and `+ 10` for the bump-arena allocation (an allocation or release is 10 operations, 4.4). The sum before the allowance is `pd(j)`; the charge `pd(j) + 10` carries the one per cent allowance, rounded up, so every integer below is an upper bound. The base case is budget 63, `pd(6) = 105,140`: `90` plus, for each pair of steps `s = 0, 2, ..., 60` with `L = 2 (62 - s) + 1`, `76 + 13 L + 9 (L - 2) + lc(L) + 2 (13 (s + 2) + 9 (s + 3) + lc(s + 3)) + 8`, and for the last step `s = 62`, `25 + 13 L + lc(L) + 2 (13 (s + 2) + lc(s + 2)) + 4` (4.4). Evaluated at each `j` the ten terms are

| `j` | `2 pd(j-1)` | 6 top rows | 8 return rows | apply passes | matrix passes | 6 inverses | CRT | pseudo-division | arrays | per-block | charged |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 7 | 210,280 | 27,349 | 61,904 | 6,852 | 13,704 | 38,640 | 9,612 | 2,064 | 5,382 | 375,981 | **379,741** |
| 8 | 751,942 | 50,481 | 72,576 | 13,668 | 27,336 | 64,644 | 19,212 | 4,112 | 10,758 | 1,014,923 | **1,025,073** |
| 9 | 2,029,826 | 96,997 | 134,496 | 27,300 | 54,600 | 117,408 | 38,412 | 8,208 | 21,510 | 2,528,951 | **2,554,241** |
| 10 | 5,057,882 | 215,337 | 325,824 | 54,564 | 109,128 | 298,860 | 76,812 | 16,400 | 43,014 | 6,198,015 | **6,259,996** |
| 11 | 12,396,010 | 418,861 | 620,064 | 109,092 | 218,184 | 562,296 | 153,612 | 32,784 | 86,022 | 14,597,119 | **14,743,091** |
| 12 | 29,194,218 | 834,225 | 1,230,720 | 218,148 | 436,296 | 1,114,116 | 307,212 | 65,552 | 172,038 | 33,572,719 | **33,908,447** |
| 13 | 67,145,418 | 1,682,485 | 2,498,784 | 436,260 | 872,520 | 2,270,352 | 614,412 | 131,088 | 344,070 | 75,995,583 | **76,755,539** |
| 14 | 151,991,146 | 3,797,433 | 6,150,720 | 872,484 | 1,744,968 | 5,838,108 | 1,228,812 | 262,160 | 688,134 | 172,574,159 | **174,299,901** |
| 15 | 345,148,298 | 7,510,333 | 12,075,936 | 1,744,932 | 3,489,864 | 11,422,632 | 2,457,612 | 524,304 | 1,376,262 | 385,750,367 | **389,607,871** |
| 16 | 771,500,714 | 15,082,689 | 24,317,184 | 3,489,828 | 6,979,656 | 23,031,348 | 4,915,212 | 1,048,592 | 2,752,518 | 853,117,935 | **861,649,115** |
| 17 | 1,706,235,850 | 30,521,413 | 49,583,712 | 6,979,620 | 13,959,240 | 47,130,816 | 9,830,412 | 2,097,168 | 5,505,030 | 1,871,843,455 | **1,890,561,890** |
| 18 | 3,743,686,890 | 68,107,209 | 118,005,696 | 13,959,204 | 27,918,408 | 115,454,796 | 19,660,812 | 4,194,320 | 11,010,054 | 4,121,997,583 | **4,163,217,559** |
| 19 | 8,243,995,146 | 135,020,365 | 232,827,168 | 27,918,372 | 55,836,744 | 227,327,448 | 39,321,612 | 8,388,624 | 22,020,102 | 8,992,655,775 | **9,082,582,333** |
| 20 | 17,985,311,530 | 271,205,073 | 468,759,168 | 55,836,708 | 111,673,416 | 458,147,940 | 78,643,212 | 16,777,232 | 44,040,198 | 19,490,394,671 | **19,685,298,618** |
| 21 | 38,980,789,322 | 548,292,181 | 953,203,680 | 111,673,380 | 223,346,760 | 933,942,000 | 157,286,412 | 33,554,448 | 88,080,390 | 42,030,168,767 | **42,450,470,455** |
| 22 | 84,060,337,514 | 1,209,813,465 | 2,208,351,552 | 223,346,724 | 446,693,448 | 2,207,571,324 | 314,572,812 | 67,108,880 | 176,160,774 | 90,913,956,687 | **91,823,096,254** |
| 23 | 181,827,913,354 | 2,400,734,557 | 4,366,323,360 | 446,693,412 | 893,386,824 | 4,358,465,544 | 629,145,612 | 134,217,744 | 352,321,542 | 195,409,202,143 | **197,363,294,165** |
| 24 | 390,818,404,266 | 4,820,324,577 | 8,782,927,872 | 893,386,788 | 1,786,773,576 | 8,773,497,492 | 1,258,291,212 | 268,435,472 | 704,643,078 | 418,106,684,527 | **422,287,751,373** |
| 25 | 836,213,369,034 | 9,735,001,189 | 17,817,461,088 | 1,786,773,540 | 3,573,547,080 | 17,830,051,104 | 2,516,582,412 | 536,870,928 | 1,409,286,150 | 891,418,942,719 | **900,333,132,147** |
| 26 | 1,782,837,885,418 | 21,281,921,001 | 40,466,705,088 | 3,573,547,044 | 7,147,094,088 | 41,095,858,092 | 5,033,164,812 | 1,073,741,840 | 2,818,572,294 | 1,905,328,489,871 | **1,924,381,774,770** |

The script below evaluates the recursion exactly (integers only), asserts the twenty charged integers, the base case `105,140`, the totals of E.2 and the top-window bound of the next paragraph, and prints row D, `N_max` and `log2(N_max/363)`; it is the evidence for every integer of this subsection.

```
from math import log2

def lc(l): return 3*l+2
def cp(l): return 4*l+lc(l)
def zf(l): return 2*l+lc(l)
def ac(l,u): return (7+u)*l+lc(l)
def crt(n): return 22*n+lc(n)
def pw(n,r): return 3*(n//8)+3+(7 if r == 0 else 10)*n

def passes(a):
    out, l0 = [], 0
    while a-l0 >= 4: out.append((l0,4)); l0 += 4
    if a-l0: out.append((l0,a-l0))
    return out

def P(a,l0,k):
    b = 1 << (a-k)
    return 150*k + b*((1 << k)+4) + b*(2*(1 << k)+3*k*(1 << (k-1))+5)

def F(a): return sum(P(a,l0,k) for l0,k in passes(a))

def base():
    t = 90
    for s in range(0,62,2):
        L = 2*(62-s)+1
        t += 76+13*L+9*(L-2)+lc(L)+2*(13*(s+2)+9*(s+3)+lc(s+3))+8
    return t+25+13+lc(1)+2*(13*64+lc(64))+4

memo = {6: base()}
def pd(j):
    if j in memo: return memo[j]
    n, a = 1 << (j-1), j-1
    def row(L,r):
        return cp(min(L,n))+zf(max(0,n-L))+ac(max(0,L-n),r == 2)+2*n*(r > 0)+F(a)
    S = (0,1,2) if j == 7 else (1,2)
    memo[j] = (184+2*pd(j-1)
        + sum(row(1 << (j+1),r)+row((1 << (j+1))-1,r) for r in range(3))
        + 8*sum(row(n,r) for r in S) + 6*(pw(n,0)+pw(n,2))
        + 12*(pw(n,0)+pw(n,1))
        + 6*sum(F(a)+(1+(r > 0))*n for r in range(3)) + 6*crt(n)
        + 30+13*((1 << j)-1)+lc((1 << j)-1)+3*(25*n+lc(n)))
    return memo[j]

node = {j: -(-101*(pd(j)+10)//100) for j in range(7,27)}
assert memo[6] == 105140
assert [node[j] for j in range(7,27)] == [
    379741, 1025073, 2554241, 6259996, 14743091, 33908447, 76755539,
    174299901, 389607871, 861649115, 1890561890, 4163217559, 9082582333,
    19685298618, 42450470455, 91823096254, 197363294165, 422287751373,
    900333132147, 1924381774770]
assert F(25) == 2227179174 and F(6) == 2040
sched = {26:8,25:1,24:1,23:1,22:2,21:2,20:1,19:1,18:1,17:1,16:2,15:1,14:1,
         13:2,12:2,11:2,10:1,9:1,8:2,7:2}
assert sum(sched.values()) == 35
reps = 3198523405724+sum(c*node[j] for j, c in sched.items())
D = reps+135271588
assert reps == 20419480219408 and D == 20419615490996
T = 63076198571935
N = 3548884+T+1000000
assert N == 63076203120819
shortest = {7:330, 8:714, 9:1482, 10:2506, 11:4554, 12:10698, 13:22986,
            14:47562, 15:80330, 16:145866, 17:342474, 18:604618, 19:1128906,
            20:2177482, 21:4274634, 22:10566090, 23:23149002, 24:39926218,
            25:73480650, 26:140589514}
assert all((1 << (j+1))-1 <= shortest[j] for j in range(7, 27))
print([node[j] for j in range(7,27)])
print('row D', D, ' N_max', N, ' log2(N_max/363) = %.14f' % log2(N/363))
```

*The top window.* The node is called on the top window of the pair, `L(j) = 2 h1 + 1 = 2^(j+1) - 1` coefficients (`h1 = 2^j - 1`; the top-coefficient lemma of 4.4), and `L(j)` is at most the shorter operand of the call at every `j` the trial uses:

| `j` | `L(j) = 2^(j+1) - 1` | shorter operand | margin |
|---:|---:|---:|---:|
| 7 | 255 | 330 | 75 |
| 8 | 511 | 714 | 203 |
| 9 | 1,023 | 1,482 | 459 |
| 10 | 2,047 | 2,506 | 459 |
| 11 | 4,095 | 4,554 | 459 |
| 12 | 8,191 | 10,698 | 2,507 |
| 13 | 16,383 | 22,986 | 6,603 |
| 14 | 32,767 | 47,562 | 14,795 |
| 15 | 65,535 | 80,330 | 14,795 |
| 16 | 131,071 | 145,866 | 14,795 |
| 17 | 262,143 | 342,474 | 80,331 |
| 18 | 524,287 | 604,618 | 80,331 |
| 19 | 1,048,575 | 1,128,906 | 80,331 |
| 20 | 2,097,151 | 2,177,482 | 80,331 |
| 21 | 4,194,303 | 4,274,634 | 80,331 |
| 22 | 8,388,607 | 10,566,090 | 2,177,483 |
| 23 | 16,777,215 | 23,149,002 | 6,371,787 |
| 24 | 33,554,431 | 39,926,218 | 6,371,787 |
| 25 | 67,108,863 | 73,480,650 | 6,371,787 |
| 26 | 134,217,727 | 140,589,514 | 6,371,787 |

so the window of every call is inside its pair, the indices of the row transforms are those of the pair, and the charge `row(2^(j+1), r)` is the transform of a window the call holds (the margin at `j = 7` is 75 coefficients, the smallest).

*Conservatism.* The per-block reading gives up the sharing of the twiddle factors: each of the `2^l0` blocks that share a position's twiddles is charged for forming them itself, so the pass charge is at least the schedule's and the node charge is an upper bound on the operations the schedule executes. The one per cent allowance covers control not modelled block by block. Against the previous version of this entry, row D rises from `19,398,840,003,317` to `20,419,615,490,996` (`+1,020,775,487,679`), `N_max` from `62,055,427,633,140` to `63,076,203,120,819`, and the normalized cost from `53.58080` to `53.60434` (`+0.02354`); this entry's cost is `0.06157` below the frontier's `53.66591`.

### E.3 Totals and the allocation walk of one trial

```
m = 610,351,562 | truncated point sets: n1 = 610,795,520 of N = 1,073,741,824 (TRC = 1165 of 2048 nodes) | squaring steps 199 of which with S: 45
S_C = 41,812,848,268,920
S_D normal local charges of the tree = 20,419,615,490,996
S_D of the lean stage D on the normal remainder sequence, with the quotient and return tests = 20,419,615,490,996
S_D = 20,419,615,490,996
peak of the live set, stage A = 19,545,456,704 bytes
peak of the live set, stage B = 49,610,227,904 bytes
peak of the live set, stage C = 82,287,666,560 bytes
peak of the live set, stage D = 82,577,450,688 bytes
two-ended pool: blocks of more than 2^19 bytes; largest sum of the two ends after each stage (bytes): init 0, A 19,545,456,704, B 49,610,227,904, C 82,287,666,560, D 82,577,449,728; at most 21 blocks; 2,076 blocks examined in all
slab classes (class: peak number of live blocks): 7: 2, 8: 2, 9: 2, 10: 3, 11: 4, 12: 2, 13: 10, 14: 10, 15: 10, 16: 10, 17: 10, 18: 10, 19: 10; slab area = 10,425,088 bytes
arena = 82,587,891,840 bytes (two-ended pool 82,577,449,728 + 128, slab classes 10,425,088, stages E and later 16,896), memory = 82,593,207,820 bytes, log2 = 36.266
stage D on the two-ended pool (blocks of more than 2^19 bytes): after init, A, B, C: low end 19,545,456,704, high end 19,545,456,704, live 39,090,913,408, largest sum so far 82,287,666,560
  stage D: 562 pool events (280 allocations, 282 frees) on 282 distinct blocks; the first 24:
  alloc #3              536,870,976 bytes pool L | live     39,627,784,384 | pool low     20,082,327,680 high     19,545,456,704 sum     39,627,784,384
  alloc #4            2,147,483,776 bytes pool L | live     41,775,268,160 | pool low     22,229,811,456 high     19,545,456,704 sum     41,775,268,160
  alloc #5            2,147,483,776 bytes pool L | live     43,922,751,936 | pool low     24,377,295,232 high     19,545,456,704 sum     43,922,751,936
  alloc #6            2,147,483,776 bytes pool L | live     46,070,235,712 | pool low     26,524,779,008 high     19,545,456,704 sum     46,070,235,712
  alloc #7            2,147,483,776 bytes pool L | live     48,217,719,488 | pool low     28,672,262,784 high     19,545,456,704 sum     48,217,719,488
  alloc #8           34,359,730,240 bytes pool L | live     82,577,449,728 | pool low     63,031,993,024 high     19,545,456,704 sum     82,577,449,728
  free  #8           34,359,730,240 bytes pool   | live     48,217,719,488 | pool low     28,672,262,784 high     19,545,456,704 sum     48,217,719,488
  alloc #9            6,442,451,008 bytes pool L | live     54,660,170,496 | pool low     35,114,713,792 high     19,545,456,704 sum     54,660,170,496
  alloc #10           4,831,838,272 bytes pool L | live     59,492,008,768 | pool low     39,946,552,064 high     19,545,456,704 sum     59,492,008,768
  alloc #11           4,831,838,272 bytes pool L | live     64,323,847,040 | pool low     44,778,390,336 high     19,545,456,704 sum     64,323,847,040
  alloc #12           6,442,451,008 bytes pool L | live     70,766,298,048 | pool low     51,220,841,344 high     19,545,456,704 sum     70,766,298,048
  alloc #13           4,831,838,272 bytes pool L | live     75,598,136,320 | pool low     56,052,679,616 high     19,545,456,704 sum     75,598,136,320
  alloc #14           4,831,838,272 bytes pool L | live     80,429,974,592 | pool low     60,884,517,888 high     19,545,456,704 sum     80,429,974,592
  alloc #15           1,610,612,800 bytes pool L | live     82,040,587,392 | pool low     62,495,130,688 high     19,545,456,704 sum     82,040,587,392
  free  #9            6,442,451,008 bytes pool   | live     75,598,136,384 | pool low     62,495,130,688 high     19,545,456,704 sum     82,040,587,392
  free  #10           4,831,838,272 bytes pool   | live     70,766,298,112 | pool low     62,495,130,688 high     19,545,456,704 sum     82,040,587,392
  free  #11           4,831,838,272 bytes pool   | live     65,934,459,840 | pool low     62,495,130,688 high     19,545,456,704 sum     82,040,587,392
  free  #12           6,442,451,008 bytes pool   | live     59,492,008,832 | pool low     62,495,130,688 high     19,545,456,704 sum     82,040,587,392
  free  #13           4,831,838,272 bytes pool   | live     54,660,170,560 | pool low     62,495,130,688 high     19,545,456,704 sum     82,040,587,392
  free  #14           4,831,838,272 bytes pool   | live     49,828,332,288 | pool low     62,495,130,688 high     19,545,456,704 sum     82,040,587,392
  free  #15           1,610,612,800 bytes pool   | live     48,217,719,488 | pool low     28,672,262,784 high     19,545,456,704 sum     48,217,719,488
  free  #4            2,147,483,776 bytes pool   | live     46,070,235,712 | pool low     28,672,262,784 high     19,545,456,704 sum     48,217,719,488
  free  #5            2,147,483,776 bytes pool   | live     43,922,751,936 | pool low     28,672,262,784 high     19,545,456,704 sum     48,217,719,488
  free  #6            2,147,483,776 bytes pool   | live     41,775,268,160 | pool low     28,672,262,784 high     19,545,456,704 sum     48,217,719,488
  the 1 events that raise the high-water mark (the last 1 shown; event number first):
  [6]   alloc #8           34,359,730,240 bytes pool L | live     82,577,449,728 | pool low     63,031,993,024 high     19,545,456,704 sum     82,577,449,728
  the pool at the high-water mark (event 6): 82,577,449,728 bytes = low end 63,031,993,024 + high end 19,545,456,704
    low end, 7 blocks from its own end of the pool (bytes, block, site; free = unallocated):
          19,545,456,704 #1 carried in to stage D (twiddle table / g / R)
             536,870,976 #3 
           2,147,483,776 #4 
           2,147,483,776 #5 
           2,147,483,776 #6 
           2,147,483,776 #7 
          34,359,730,240 #8 
    high end, 1 blocks from its own end of the pool (bytes, block, site; free = unallocated):
          19,545,456,704 #2 carried in to stage D (twiddle table / g / R)
  after stage D: low end 0, high end 0; high-water mark of the pool over the trial 82,577,449,728 bytes
```
