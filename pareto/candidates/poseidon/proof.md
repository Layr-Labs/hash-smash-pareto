# Orchard Poseidon, r = 6: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, value-domain powering on truncated point sets with radix-16/32 passes, a Graeffe prefix, inversion-free half-gcd on three rows, one centre

## 1. Claim

Target: `poseidon-orchard-r6-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, six partial rounds 4, 5, 6, 7, 8 and 9, full rounds 60-63, state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is an algorithm (sections 2-4) with an operation count that bounds every run (sections 6-7) and a success probability derived from two score-critical premises: `H-ONE` (section 9.1), a statement about the fraction of centres at which the fixed digest polynomial has between 1 and 16 usable roots, and `H-NORMAL` (section 9.5), a statement about the normality of the remainder sequence that enters only the success probability. Section 9.2 derives the success probability from them.

* The algorithm: draw a centre `c` from two fresh random words, `c = (w1 2^256 + w2) mod p` (within statistical distance `p/2^512` of uniform on `F_p`, 4.1.1), build the odd part `g_c` of the line polynomial by evaluation and one inverse transform, replace `g_c` by its 24-fold Graeffe transform `g = g_c^(24)` (monic, degree `m`, its roots the `2^24`-th powers of those of `g_c`; section 4.3G), compute `R = S^((p-1)/2^25) mod g` in the value domain by Montgomery powering on two truncated point sets `O1`, `O2` of `n' = 233 * 2^19 = 122,159,104` points (233 of the 256 depth-8 nodes of the subgroup of order `2^27` and of its coset; the method of bradcush `b30de9bf`/`a41aecdd`, there 15 of 16 nodes, section 4.3T), take `G = gcd(g, R - 1)` by the inversion-free half-gcd on three rows of bradcush `4bcabff8` (outer step `k = 2^j - 1 <= 2^22 - 1`, each matrix applied to the whole pair in place by the block products of the memory cap of weijiekoh `a78f526e`, applies longer than `2^26` in blocks of length `2^22`, section 4.4), charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, and if `G` has degree between 1 and `DMAX = 16` isolate a root `y` of `G` in at most `Z = 64` rounds, find `s` with `s^(2^25) = y` and `F(c + s) = F(c - s)` among at most `2^24` candidates (4.1.3), map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39009`: a lower bound for the probability, over the algorithm's fresh random words, that the centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1), `delta = 0.003` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `eps_iso <= 2.371e-15`, `eps_coin <= 65 p / 2^512 <= 1.404e-76`, `eps_g <= 2^24 n' (D - 1) / p < 2^-175` (the centre makes `g` vanish at a point of `O1`, 4.3G) (sections 4.1.1, 4.3T, 9.2). The value the formula gives is `0.390099999999997628` (at or above the organizer floor 0.39); the claim is that value floored at five decimals.
* `time_log2 = 34.84228` in target-compression units (`C(6) = 342` primitive operations per unit): the operation count that bounds every run, derived in section 6 as `T_fixed + K * T_trial + T_off` with `K = 1`, stage C a Graeffe prefix of 24 steps (4.3G) and value-domain powering on truncated point sets (4.3T), stage D the inversion-free half-gcd on three rows charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (4.4, 6.3; the time bound holds for every sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work), stage E at its cap of `Z` rounds at degree `DMAX`, and the scan of stage F at its cap of `2^24` candidates (4.1.3). `N_max = 10,534,072,300,577` operations, `log2(N_max / 342) = 34.84227598522185...`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is counted exactly, `T_off = 137,141` operations, and charged at its declared cap of 1,000,000 operations; that cap is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 33.865` (`15,645,111,564` bytes, section 7). Under the pareto convention `time_log2 + max(0, memory_log2_bytes - 20)` this gives `34.84228 + 13.865 = 48.70728`; the time-only scalar is `34.84228`, and the memory is reviewed separately.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; every random field element is drawn from two fresh words, at most `65` field elements (`130` words) per run (section 4.1.1), and a draw costs 63 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^12`, then the roots of its odd part about a centre, found, after a Graeffe prefix (Dandelin-Graeffe root squaring), with a gcd against `S^((p-1)/2^25) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* This package is the base entry `d7d51e67` with one change to its charge: the half-gcd node keeps the base's two-row product, and each row transform of the node is evaluated in the block form of `27fbfbe7` 4.2; the node charge `node_bf(j)` is derived in Appendix E.2.1 as a per-block upper bound with a declared one per cent allowance, and no integer is taken from another entry's node column. Row D `3,599,481,127,579` (was `3,958,780,450,536`); every other row, the memory and the success bound are unchanged. The top-window bound against the shortest operands of this round is in E.2.1. Normalized cost `48.70728` (was `48.75567`).
* Against our r = 6 entry `6c709970` (time + memory penalty 48.82700), one change to its algorithm: the product step `M = M1 [[Q, 1], [b^2, 0]] M2` of each half-gcd node runs on the two rows `Y - 1`, `Y + 1` (`2n` points) in place of three; its entries have degree at most `2n - 1` on the normal sequence (4.4). Row D `3,958,780,450,536` (was `4,510,919,995,962`); every other row, the memory and the success bound are unchanged. Our entry `6c709970` against our r = 6 entry `134dbc84` (time + memory penalty 48.85304), one change to its algorithm: a Graeffe prefix (4.3G). Stage C first applies 24 Graeffe steps `g(Y) <- E(Y)^2 - Y O(Y)^2` on `O1` (`20,692,982,543` operations each) and then raises `S` to `(p-1)/2^25` (205 squaring steps in place of 229); the gcd keeps exactly the `2^24`-th powers of the usable roots (`1 <= deg G <= k(c)`), and stage F finds the root of `g_c` above the isolated one by a scan of at most `2^24` candidates on the line map (4.1.3). Row C `6,746,634,456,293` (was `6,964,700,241,112`), row F `9,631,344,298` (was `47,012`); memory unchanged. `H-NORMAL` is stated for the pair of the transformed polynomial and its organizer-run tests compute that pair (9.5, 10.5.1); `H-ONE`, every other charge and the other experiments are unchanged.
* Prior entries: `134dbc84` (48.85304) is our r = 6 entry `a5e93fd0` (time + memory penalty 49.24619, the same algorithm and package) with three changes: (i) the loads and stores of the data words of the transform-pass blocks of 4.3T are charged one operation each, base plus index (4.2; the wording of the accepted `89b451ff` and `070a02b2`); (ii) the outer steps of stage D run bradcush's inversion-free half-gcd on three rows (entry `4bcabff8`; the transform reuse of `b30de9bf`), as in our r = 3 entry `bcf8e01c`, ported to `r = 6` and charged in this cost model (section 4.4), in place of the lean cofactor-free half-gcd of bradcush `e6dcb600`/`1aa56884`; (iii) layers 1-8 of the truncated transforms run class-batch by class-batch with the positions above `n'` of the batch in a `11,776`-word buffer, in place of the scratch of `N - n' = 12,058,624` words (4.3T, 7). Row C `6,964,700,241,112` (was `8,114,361,178,793`), row D `4,510,919,995,962` (was `6,634,762,459,061`); memory `2^33.865` (was `2^33.901`), the allocator high-water mark of one trial, reached in stage C (section 7). Every other charge, the premises and the experiments are unchanged. this entry improves our r = 6 entry `cf66371a` (the one-centre algorithm of our r = 6 entry `c318f442`: the two-word coins, the lean cofactor-free half-gcd charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, the memory cap of weijiekoh's entry `a78f526e`, the premises `H-ONE` at `q = 0.3931` and `H-NORMAL` at `delta = 0.003` with the split of cryptogakusei's entry `4888e783` and organizer-run tests in the form of gta6rp's entry `bef31fdd`; bradcush's value-domain stage C on truncated point sets, entries `b30de9bf`, `a41aecdd`; the memory schedule of 0xshikhar's entries `52120fad` and `716c3818`) by three changes: (i) the kernel charges of stage C (4.3T): the bottom twiddles from the two-level table with register constants, running group factors in the middle passes, the recovery with the path value in a register, the scaling fused into the adjacent pass, and the batch-inversion chunk in the scratch above `n'`; (ii) each line evaluation of stage B charged at the operations it executes, `155 + 21 r = 281`, in place of `C(6) = 342` (section 3); (iii) the passes of stage C at radix 16 and 32 on the 64-word register file, stated as a machine restriction in claim.json in the form our r = 3 entry `ef123c2b` states it (4.2, 4.3T). The premises, the coins, stages A and E-G and the organizer-run tests are those of `cf66371a`. The memory is the allocator high-water mark of the one trial (section 7).
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1), a statement about the fraction of good centres, and `H-NORMAL` (score-critical for the success probability only, section 9.5), bradcush's premise on the normality of the remainder sequence stated with the allowance `delta = 0.003`; the organizer-run tests are reproducible observations consistent with it (9.5, 10.5.1). Both are statements about probability. The machine (64 registers of 256 bits and constants as immediates; every load, store and spill counted) is stated as a restriction in claim.json, as the accepted entries `89b451ff` and `fb176310` state theirs, not as a heuristic (4.2). The costs are the declared cost model of this entry, not heuristics: the charging rules of section 4.2 with that register file, the inversion-free half-gcd of stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (Appendix E). Everything else is proved or counted here.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`. `(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`. The algorithm uses the line `j = 0`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant `M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS, nonzero on the deployed constants, checked). Let `(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, `d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i` (the supports are disjoint). After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8, 9 (partial), 60, 61, 62, 63 (full) put twelve S-box layers on top of an affine map, and the digest is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^12 = D = 244,140,625`. The leading coefficient is obtained by propagating leading coefficients through the twelve layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used: `f_D(0) = 0x34bd5acc9093858597cb29a9ca5405d90d50343d4924ce1be148b06792258969` (computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau` against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`), hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 122,070,312`, `g_c` has degree exactly `m` and leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`, `W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The useful roots are the roots in `F_p` with `S^((p-1)/2) = 1`: they are the roots of `gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p`; `S = 0` is not a root of `S^((p-1)/2) - 1`). This gcd divides the squarefree `S^((p-1)/2) - 1`, so it is a product of `k(c)` distinct linear factors over `F_p` (9.1); stage D computes instead the gcd of 4.3G, whose roots are their `2^24`-th powers.

Construction of `g_c` by evaluation. `H = 201,326,592 = 3 * 2^26` divides `p - 1` (`p - 1 = 2^32 * 3 * q`) and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`; one inverse transform of size `H` returns the coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). Each of the `2H = 402,653,184` evaluations of `F` is charged at the operations it executes (the line evaluation `tail_eval`): the affine start `alpha + beta W` (3 multiplications, 3 additions: 6), round 2 (three S-boxes `x^5` of 3 operations each and the MDS, 9 multiplications and 6 additions: 24; its constants are in `alpha`), round 3 (3 constant additions, 9, 15: 27), the six partial rounds (3 + 3 + 15 = 21 each), rounds 60-62 (27 each) and round 63 (3 + 9 and row 0 of the MDS, 3 multiplications and 2 additions: 17), `155 + 21 r = 281` operations at `r = 6`; rounds 0 and 1 are not executed (section 2). The loop work (two point additions, one subtraction, one multiplication by `1/(2 zeta^i)`, the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, the store with its address, the loop control and the bit-reversed index) is charged on top (stage B, section 6), with the twiddle table of the transform, built by stage B (4.2).

## 4. The algorithm (one centre, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   constants (once; no twiddle table: each stage builds the table of its own transforms, 4.2)
setup:  the line (line_setup) (once)
for t = 1, ..., K (K = 1):            [the test t <= K is made at the start of the trial; no exit except success]
  A  c := (w1 * 2^256 + w2) mod p from two fresh random words w1, w2 (4.1.1)
  B  g := monic g_c, by section 3 (402,653,184 evaluations + one inverse NTT of size 201,326,592 + the nonzero-leading-coefficient test + normalisation)
  C  g := g^(24): 24 Graeffe steps on O1 (section 4.3G); R := S^((p-1)/2^25) mod g, in the value domain on the truncated point sets O1, O2 of n' = 122,159,104 points (section 4.3T): 205 squaring steps, 45 of them also multiplying by S
  D  G := gcd(g, R - 1) (monic): the inversion-free half-gcd on three rows with the in-place applies of the memory cap (section 4.4), charged for the normal remainder sequence with the quotient and return tests; on any other case ABORT (6.3)
  E  if deg G = 0 or deg G > DMAX: trial ends. Otherwise isolate a root y of G (4.1.2); if none within Z = 64 rounds: trial ends.
  F  u := a 2^25-th root of y (25 Tonelli-Shanks square roots, 2-adicity 32); for j = 0, ..., 2^24 - 1: s := u mu^j, W1 = c + s, W2 = c - s, until F(W1) = F(W2) (4.1.3); tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (300 operations each) are equal and the pairs differ -> output; otherwise the trial ends
```

4.1.1 Coins (ruling `04c0dd43`, finding F-EVAL-001). The only randomness is the cost-model random-word primitive. Every random field element of the algorithm (the centre `c` of stage A and each shift of stage E) is drawn from two fresh 256-bit words `w1, w2`: each is reduced mod `p` by three conditional subtractions (exact, `2^256 < 4p`), and `x = (w1 mod p) * (2^256 mod p) + (w2 mod p)` in `F_p`, i.e. `x = (w1 2^256 + w2) mod p` with `w1 2^256 + w2` uniform on `[0, 2^512)`. There is no rejection and no retry. A draw is 63 operations: per word 1 random-word operation, 1 load, 1 store, 3 control, the reduction 9 and its loop control 11 (26 per word, 52), two Montgomery conversions 2, the load of the constant `2^256 mod p` 1, one multiplication 1, one addition 1, entry 2, the two addresses 4. At most `1 + Z = 65` draws (`130` words) per run. With `2^512 = Q p + r`, each residue has `Q` or `Q + 1` preimages, so one draw is within statistical distance `r (p - r) / (p 2^512) <= p / 2^512 = 2^-258.0` of uniform on `F_p`; the 65 draws are independent, so the joint distribution of all the coins of a run is within `eps_coin = 65 p / 2^512 <= 1.404e-76` of the distribution with every draw exactly uniform (total variation is subadditive over independent components).

4.1.2 Stage E: isolating a root of `G`. With `1 <= deg G <= DMAX = 16`, a Cantor-Zassenhaus split with random shifts isolates one linear factor in at most `Z = 64` rounds at degree `<= 16`; `eps_iso <= 2.371e-15` bounds the probability that 64 rounds fail to isolate a root when `deg G >= 1` (section 9.4).

4.1.3 Stage F: the root of `g_c` above `y`. By 4.3G, `y = S^(2^24)` for a usable root `S` of `g_c`, and the solutions of `S'^(2^24) = y` are `u^2 mu^(2j)`, `j < 2^24`, where `u^(2^25) = y` and `mu` is a fixed primitive `2^25`-th root of unity (`2^25 | p - 1`; a constant of the offline derivation, 6.2). `u` comes from 25 successive Tonelli-Shanks square roots: `y` is a `2^25`-th power, and if `x` is a `2^k`-th power with `1 <= k <= 25`, both square roots of `x` are `2^(k-1)`-th powers (`-1` is a `2^(k-1)`-th power, `2^k | p - 1`). The scan takes `s = u mu^j` for `j = 0, 1, ..., 2^24 - 1` and stops at the first `j` with `F(c + s) = F(c - s)` (two line evaluations of section 3). For `S' = s^2` a root of `g_c` this holds, because `F(c + s) - F(c - s) = 2 s g_c(s^2)`, so the scan stops at the latest at the `j` of `S`; any stop has `s != 0` (`y != 0`) and `F(c + s) = F(c - s)`, a collision by 2.4. Charge per candidate: `s <- s mu` 1, `c + s` and `c - s` 2, two line evaluations `2 * 281`, their calls 4, the comparison and branch 2, the loop control 3: `574`; at most `2^24` candidates, `9,630,121,984`, and the loop exit 2. The 25 square roots are charged `47,012` each (the whole row F of the algorithm without the prefix, a square root and the back-map), `1,175,300`, and the back-map `47,012`: row F = `9,631,344,298`.

### 4.2 Machine model and charging rules (summary; `C(6) = 342`)

Every field operation, load, store, control operation and random word is one primitive operation; `C(r) = 216 + 21 r = 342` primitive operations is one target-compression unit. The register file is 64 words of 256 bits (the machine restriction of claim.json: it holds the 32 values of a radix-32 block with 28 of its 31 group twiddles, the running group factor and one temporary; every other value, the 3 other twiddles included, is charged as a load or store; a load or store of a data word of a block of a transform pass of 4.3T is one operation, its address the base plus index of the load or store itself: one load per word fetched from memory and one store per word written, the wording of the accepted entries `89b451ff` and `070a02b2`), the only register assumption; the algorithm runs on one thread, no dispatch. Allocation: one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes. A block of more than `2^17` bytes is served by the two-ended pool (one region, two ends, first-fit in address order, the statements marked `# pool:H` using the high end and, with the depth-parity placement of section 7, the end `(j + bit8) mod 2` of a half-gcd node at depth `j`); every smaller block by its slab class (the least `j >= 7` with `2^j >= need`, a slot of `2^j` bytes). The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows (a pool request `97` operations besides the walk and `13` per block examined, a slab request at most `126`, a free `81` for a slab block and at most `105` for a pool block). The memory of both allocators is the arena of section 7. Twiddle tables: none is built in init; stage B, the Newton and quotient products of stage C and stage D each build the table of their own largest transform (`2^(a-1)` entries for `3*2^a` points: its root, 5 operations per entry and the loop) and free it at the end of that work, charged in the stage's row; the passes of 4.3T use two-level root tables of `4 x 4,096` words (stage C).

### 4.3G The Graeffe prefix

Definition. For `h` monic of even degree `m` write `h(X) = E(X^2) + X O(X^2)`; its Graeffe transform is `h~(Y) = E(Y)^2 - Y O(Y)^2`, so `h~(X^2) = h(X) h(-X)` and `h~` is monic of degree `m` with roots the squares of the roots of `h` (with multiplicity). Stage C first replaces `g = g_c` by `g^(24)`, 24 Graeffe steps, then computes `R = S^e mod g^(24)`, `e = (p-1)/2^25` (2-adicity 32), and stage D takes `G = gcd(g^(24), R - 1)`.

Lemma. `G` is the product of `(Y - y)` over the distinct values `y = S^(2^24)`, `S` a usable root of `g_c` (a nonzero square in `F_p` with `g_c(S) = 0`, section 3). Proof: `g^(24)(Y) = prod_i (Y - S_i^(2^24))` over the roots `S_i` of `g_c` in an algebraic closure; `Y^e - 1` is squarefree and its roots are the `2^25`-th powers of `F_p^*`. If `S_i^(2^24) = u^(2^25)` with `u` in `F_p^*`, then `S_i = u^2 zeta` with `zeta^(2^24) = 1`, so `zeta` is in `F_p` and `zeta = xi^2` with `xi^(2^25) = 1` (`2^25 | p - 1`), and `S_i = (u xi)^2` is a nonzero square of `F_p`; conversely `S = v^2` gives `S^(2^24) = v^(2^25)`. So `deg G` is the number of distinct `2^24`-th powers of the usable roots: `1 <= deg G <= k(c)` when `k(c) >= 1`, and `deg G = 0` when `k(c) = 0`; the event `E_c` of 9.2 gives `1 <= deg G <= DMAX`.

Execution (on the point set `O1` of 4.3T). One step: `E` (`m/2 + 1` coefficients) and `O` (`m/2`) are read from `g` at stride 2 by the top passes of two truncated forwards, which load only the input blocks below the length (8 or 7 of the 16 per offset, two offset ranges per batch; butterflies only on nonzero inputs; no zero-fill); the fused bottom pass forms `G = (E^2 - y O^2)/N` at each point `y` of `O1` between the forward and the inverse bottom layers (`y` is the last-layer twiddle of its butterfly, in a register: two squarings, two multiplications, one subtraction, 5 per point); one truncated inverse stores the new coefficients into the array of `g` (those above `m` come out zero). `E` and `O` on `O1` use the arrays of `A` on `O2` and of `A` on `O1` before stage C fills them, with a batch buffer of `11,776` words of their own, used by one transform at a time and freed after the prefix; no array is added and the high-water mark of section 7 is unchanged. One step is `20,692,982,543` operations (Appendix E.1), 24 steps; stage C then runs 205 squaring steps in place of 229 (the exponent loses 24 low zero bits). A step saves one squaring step (`29,779,056,940`) for `20,692,982,543` and doubles the scan of 4.1.3 (`2^s * 574`); `s = 24` minimises the total.

Every map is exact; no premise is added to the time or the memory. The zero test of `k1` (4.3T) now concerns `g^(24)`: `g^(24)(y) = 0` for `y` in `O1` only if `g_c(x) = 0` for one of the `2^24` values `x` with `x^(2^24) = y` (in `F_p` or an extension); for each such `x`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g^(24) vanishes on O1) <= 2^24 n' (D - 1) / p = eps_g < 2^-175`.

### 4.3T Stage C in the value domain on truncated point sets (the method of bradcush `b30de9bf`/`a41aecdd`, 233 of 256 nodes)

Point sets. `N = 2^27` divides `p - 1` (2-adicity 32). Let `psi` have order `2^28`, `H_N = <psi^2>` and `Y = X^(2^19)`. `H_N` is the union of the 256 depth-8 nodes `{x : x^(2^19) = r_j}`, `r_j` the 256-th roots of unity in transform (bit-reversed) order; `O1` is the union of the first 233 nodes, `n' = 233 * 2^19 = 122,159,104 >= m + 1 = 122,070,313` points, and `O2` the same 233 nodes of the coset `psi H_N` (`x^(2^19) = r'_j`, `r'_j^256 = -1`), disjoint from `O1`. `P1 = prod_{j<233} (Y - r_j)` has degree `n'`, vanishes on `O1` and is the nonzero constant `P1(r'_j)` on node `j` of `O2`; `delta_j = 1/P1(r'_j)` (233 table constants).

Truncated transforms (bradcush `b30de9bf` 4.3, generalized as the truncated Fourier transform of van der Hoeven, ISSAC 2004). A polynomial of degree `< n'` is `sum_{k<256} P_k Y^k` with `deg P_k < 2^19` and `P_k = 0` for `k >= 233`; its values on the 233 nodes determine it and are determined by it (the CRT for the 233 coprime moduli `Y - r_j`, whose product `P1` has degree `n'`). The forward transform runs the top 4 layers on all `N/16` offsets (no truncation saving is charged), the middle layers only on the blocks above present nodes, and the bottom 4 layers on the `n'` points. The inverse runs the same layers in reverse, scales each 16-point block of its bottom pass by `diag(1, c^-1 J)` (`c = y^16` of the block, `V^T V = 16 diag(1, cJ)`; 15 multiplications and the load of `c^-1`, 17 operations per block), and recovers the residues of the dropped part `[233, 256)`, the maximal subtrees `{233}`, `{234..235}`, `{236..239}`, `{240..255}` (depths 8, 7, 6, 4), from the known zero chunks `P_k = 0` along their paths to the root, as bradcush recovers the one dropped leaf; with the value of the path held in a register this is charged 8 operations (3 multiplications, 3 additions, the load of the known value) per point of a dropped subtree per layer of its path and one store (2) per point. Layers 1-8 (the top pass, the first middle pass and the recoveries) act on each class of the `256` positions with equal low 19 bits separately (`233` in `O1`, `23` above `n'`: the dropped nodes `[233, 256)`), so they run class-batch by class-batch, `1,024` batches of `512` classes, the `23` positions above `n'` of each class of the batch held in one batch buffer of `11,776` words and discarded after the batch (one transform runs at a time); the passes below layer 8 touch only the `n'` positions. Charged once per batch: the 16 groups, the pass overhead and the batch loop of the first middle pass (`16 * 20 + 20 + 3`), the top-pass overhead with its 31 register constants and 16 inner loops, one per depth-8 node within a lane (`4 * 31 + 20 + 16 * 5`), the path constants of each recovery (the 25 levels of the paths of the four dropped subtrees, 3 constants each at 2, and their 4 loops at 5: `170`), and before the top of each truncated forward the zero-fill of the `7 * 512 = 3,584` positions of the batch above `n'` in lane 14 (a store, 2, each and the loop). The passes are fused as in `b30de9bf` 4.5 under the declared 64-word register file (4.2), the 27 layers split 4 | 4, 5, 5, 5 | 4 (`TR_CFG`, the cheapest split under that register file): a bottom pass (16-point blocks: forward layers, the pointwise map, inverse layers; one set of 15 twiddles for both directions, 19 operations per block: two loads from the two-level table, one multiplication, three squarings, eleven multiplications by register constants), a middle pass of radix 16 (per block 16 loads and 16 stores at one operation each, 32 butterflies and 5 control, 133; per group a running group factor, 1 multiplication, and its 15 twiddles formed by 3 squarings and 11 multiplications and held in registers, 20 per group with its overhead), three middle passes of radix 32 (per block 32 loads and 32 stores at one operation each, 80 butterflies, the loads of the 3 twiddles that do not fit (6) and 5 control, 315; per group the running factor and its 31 twiddles by 4 squarings and 22 multiplications, 28 of them in registers with the 32 data words, the factor and a temporary, 62 of the 64 words, and 3 stored, 38 per group with its overhead), and a top pass over all `N/16` offsets that fuses the inverse top of one set with the forward top of the other (31 coset constants in registers).

Montgomery powering (`b30de9bf` 4.5). For residues of degree `< n'`, `Mont(A, B) = (A B + u g)/P1` with `u = -A B / g mod P1` (`deg u < n'`); the division by `P1` is exact, `Mont(A, B) = A B / P1 mod g`, and `deg Mont(A, A) <= n' - 2`, so `X Mont(A, A)` has degree `< n'`. A residue `A` (representing `S^e P1`) is held by its values on `O1` and on `O2`, each up to a tracked scalar. One step: `U = A^2 k1` on `O1` (`k1 = -1/(N^3 g)` there; `u` is determined by its values on `O1`); `U` to `O2` (truncated inverse on `O1`, truncated forward on `O2`); `B2 = (A2^2 + U g) delta_j` on node `j` of `O2`, which is `Mont(A, A)` up to the tracked scalar because `P1 = 1/delta_j` there, times the point `x` when the exponent bit is 1; `B2` to `O1` (truncated inverse on `O2`, truncated forward on `O1`). No `1/N` is executed inside the steps (the scalars are tracked, 2 operations per step). Per point and step: on `O1` `sqr, LD k1, mul` (4); on `O2` `LD A2, sqr, LD g, mul, add`, the multiplication by `delta_j`, `ST` (10) and the load of `delta_j` per block (2); 3 more for a 1-bit (the load of the point and a multiplication).

Entry and exit. `g` (coefficients after the Graeffe prefix of 4.3G, its slots above `m` zero) goes to `O1` and `O2` (a truncated forward each; every scaling of this section, `1/N` and the coset twist, is a running product fused into the adjacent pass, 2 operations per point). The start residue is `A0 = X^v P1 mod g`, `v = 2^24 = 16,777,216` (VSHIFT = 2): `q = floor(X^v P1 / g)` has `ell = v + n' - m + 1 = 16,866,009` coefficients and is formed from the Newton reciprocal of the reversed `g` and one product (transforms of up to `3*2^24` points, with their own twiddle table, freed after the quotient); on node `j` of `O2`, `x^v P1(x) = r'_j^32 P1(r'_j)` is a constant, so `A0 = x^v P1 - q g` there is one truncated forward of `q` and one pointwise pass (8 per point); then `A0` goes to `O1`. `k1` is formed by chunked batch inversion on `O1` (chunks of `2^13` points: prefix products, one inversion, two multiplications per point; the `2^13` prefixes are kept in the batch buffer, which no transform uses at that time); each chunk product is tested for zero before its inversion (2 per chunk), and a zero ends the trial: for fixed `x != 0`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g vanishes on O1) <= eps_g < 2^-175` for the transformed `g` (4.3G, 9.2). The exit is one step with multiplier 1 (`Mont(A, 1)`) and two truncated inverses with their scaling, which return `kappa R` (`kappa` the tracked scalar) and `g` in coefficient form; the gcd is scale-invariant, so stage D receives `kappa R - kappa`. There are `205` squaring steps (the exponent `(p-1)/2^25`, 4.3G), `45` of them also multiplying by `S`.

Exactness and memory. Every map above is exact (Montgomery products of polynomials of degree `< n'`, held bijectively by their values on 233 nodes); no premise is added to stage C. The live set of the stage is four arrays of `n'` words (`g` on `O2`, `A` on `O2`, `A` on `O1`, `k1` on `O1`), the batch buffer of `11,776` words, the tables (`263 + 16,384` words: 30 constants, the 233 `delta_j`, the two-level root tables) and, while `q` is formed, the Newton arrays. The step-by-step count is expanded in Appendix E.1 and totals **row C = 6,746,634,456,293** (section 6).

### 4.4 Stage D: the inversion-free half-gcd on three rows (bradcush `4bcabff8`), with the in-place applies of the memory cap

`G = gcd(g, R - 1)` is computed by bradcush's inversion-free half-gcd (entry `4bcabff8`, with the transform reuse of `b30de9bf`; read as text only, ported and charged in this cost model as in our r = 3 entry `bcf8e01c`). Matrices and remainders are kept up to nonzero scalars with pseudo-division (`b^2 a = Q b + e`, `Q` of degree 1 on the normal sequence), so no field inversion runs inside the recursion; the gcd is the same up to a scalar and is made monic at the end. A node of budget `k = 2^j - 1` makes two child calls of budget `2^(j-1) - 1`; its products run on `3 * 2^(j-1)` points, the rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), each a power-of-two transform of `n` points in the block form of `27fbfbe7` 4.2 after a twist (E.2.1), joined by a 3-row CRT for `(c, d) = adj(M1)(a, b)` on the top window; then the pseudo-division and the product `M = M1 [[Q, 1], [b^2, 0]] M2` on the two rows `Y - 1`, `Y + 1` only (`2n` points; 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` with the `1/2` folded into the `1/n` of the inverse, 10 operations per point). The product needs no third row: on the normal sequence every quotient has degree 1 and `b^2` is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; the row `Y - 1` values of each child's matrix are returned by the child, the row values of `M1` are kept from the apply and reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). The twist roots of order `2n` and `4n` come from the squaring chain of the running twiddle factors of the row transform (4.2); the scales `1/2^a` (`a <= 21`) are a table of 21 words built at the entry of stage D (`1/2 = (p + 1)/2` an immediate, 20 multiplications). The base case (budget 63) runs two remainder steps per pass over its window. Driver: while `(n - 1)/2 >= 127`, one outer step calls the node on the top window of the pair with `k = 2^j - 1` the largest with `k <= min(2^22 - 1, (n - 1)/2)`, applies `adj(M)` to the whole pair in place, and makes one division with the quotient test; the apply is that of the memory cap (the method of weijiekoh `a78f526e`, its `mat_apply` LMAX, as in `a5e93fd0`): an apply to a pair longer than `LMAX = 2^26` coefficients is done by the block products of scheme (a) at the block length `2^22` (transforms of `2^23` points), each block of the operands transformed once, the transforms of a slot multiplied pointwise and summed, and each output slot inverse transformed and overlap-added in place into the output array. At `r = 6` the pair is below degree `192` after the last outer step, and classical division steps finish. The working arrays of a node live in one bump arena (an allocation or release is 10 operations) of `67,108,608` words at `j = 22`, the peak of its recursion; the cap `j <= 22` keeps the arena and the pair below the stage-C peak (section 7). On the normal sequence every length, budget and allocation is a function of `m` alone. The row is charged for the normal remainder sequence (every quotient of degree 1), the case of the premise `H-NORMAL` (9.5): every division and pseudo-division tests that its quotient has degree 1 and every call tests on return that it removed exactly its budget (2 operations each), and a zero remainder also ends the trial; on any other case the trial ABORTs (the allocator is reset and the run ends without output, section 6.3). By the prefix lemma of 6.3 every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, so the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The total is **row D = 3,599,481,127,579** (section 6.3, 6; Appendix E.2).

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G = gcd(g, R - 1)`, whose roots are the values `y = S^(2^24)` of the usable roots `S` of `g_c` (4.3G); stage F stops only at an `s != 0` with `F(c + s) = F(c - s)` (4.1.3), so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Ledger: operation count (primitive operations; `C(6) = 342`)

| row | what is charged | operations |
| --- | --- | --- |
| init | constants and bookkeeping (once; no twiddle table, 4.2) | 17,980 |
| setup | the line (`line_setup`, once) | 4,910 |
| A (per trial) | stage bookkeeping, loop test and update, the coin draw (63, two words), one allocation | 1,228 |
| B (per trial) | `402,653,184` evaluations of `F` on the line at their executed `155 + 21 r = 281` operations each (section 3), the loop work, the twiddle table and the inverse transform of size `201,326,592`, the normalisation | 178,154,740,855 |
| C (per trial) | the Graeffe prefix, 24 steps (section 4.3G), then `S^((p-1)/2^25) mod g` in the value domain on the truncated point sets `O1`, `O2` (233 of 256 nodes, `n' = 122,159,104`), VSHIFT = 2, 205 squaring steps (section 4.3T); expanded in Appendix E | 6,746,634,456,293 |
| D (per trial) | inversion-free half-gcd of `(g, R - 1)` (node products on two rows, 4.4) on three rows with the in-place applies of the memory cap, charged for the normal remainder sequence with the quotient and return tests (sections 4.4, 6.3); expanded in Appendix E | 3,599,481,127,579 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16`, each with one draw of 63 (two words) | 166,081,821 |
| F (per trial) | the `2^25`-th root of `y` (25 square roots at 47,012), the scan of at most `2^24` candidates at 574 and its exit, the back-map 47,012 (4.1.3) | 9,631,344,298 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 342 + 32` | 7,872 |
| trial-loop (per trial) | trial-loop bookkeeping (12) and the allocator reset after an ABORT (1,000), charged in every trial | 1,012 |
| plan_invN misses | one per distinct plan size | 126,649 |
| output rows | the fixed output rows (stages H and I) | 3,390,080 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + 1 * T_trial + T_off` | **10,534,072,300,577** |

`T_off = 1,000,000` (the declared cap; the exact count is `137,141`, 6.2); `T_trial = A + B + C + D + E + F + G + trial-loop = 10,534,067,760,958`; `T_fixed = init + setup + plan_invN misses + output rows = 3,539,619`; `K = 1`, so `N_max = 3,539,619 + 10,534,067,760,958 + 1,000,000 = 10,534,072,300,577`. `log2(N_max / 342) = 34.84227598522185...`, rounded up at five decimals to `34.84228`. Rows C and D are expanded part by part in Appendix E (E.1, E.2) from the dimensions of 4.3T and the half-gcd levels with the kernel charges of 4.2; the parts add up exactly to `6,746,634,456,293` and `3,599,481,127,579`.

### 6.1 Validation
The kernel charges and the allocator rules are those compared with the instrumented totals of our executed runs at `r = 3, 4, 5` (the arena rule within 64 bytes of the measured heap peaks there); the truncated-set stage C (4.3T) has no executed counterpart, and its count is the formula of Appendix E. Rows C and D are the finite recurrences of Appendix E (E.1, E.2), summed term by term; no coefficient is fitted or extrapolated.

### 6.2 Offline derivation
The literals of the sources are computed once, offline, from `p` and the organizer's 192 round constants and 9 MDS entries, one literal at a time (working set: at most 16 words of 32 bytes and a 64-byte digit buffer); each is the value of one closed formula, with no search and no choice. Count in the primitives of 4.2 (orchard-field-ram-v2: every field operation, load, store and control operation is 1): a field operation is charged 4 (the operation, two operand loads, one store), a 64-bit word operation 3 (the operation, one load, one store), a hexadecimal digit 5 (its load, the table load, a shift, an or, the loop control). (a) Input: 202 values of 64 hexadecimal digits (`p`, the 192 round constants, the 9 MDS entries), 324 each with the 4 word stores: `65,448`. (b) Field literals, 497 field operations: `2 = 1 + 1` (1); `R = 2^256 mod p`, `2` squared 8 times (8); `R^2 mod p` (1); the Montgomery forms `x R mod p` of the 201 organizer constants (201); `2^65 R mod p` (`2` squared 6 times, times `2`, times `R`: 8); `5 = 2 + 2 + 1` (2); `5^t R mod p` with `t = (p-1)/2^32`, the odd exponent of the Tonelli-Shanks of stage F (223 bits, 46 of them 1: 222 squarings, 45 multiplications, times `R`: 268); `mu R mod p`, `mu = (5^t)^(2^7)` of order `2^25` (7 squarings, times `R`: 8); charged `4 * 497 + 3 * 222` (the bit steps of the square-and-multiply) `= 2,654`. (c) Word literals, 90 word operations: `p - 1` (4), `t` (a shift by 32 over 4 words, 12), `(t+1)/2` (16), `(p-1)/2` (12), `p - 2` (4), `e = (4(p-1)+1)/5` (a shift by 2 into 5 words 15, plus 1, a division by 5 word by word 10: 26), `-p^-1 mod 2^64` (5 Newton steps `x <- x (2 - p_0 x)` from `x = p_0`, 3 each, and a negation: 16); charged `3 * 90 = 270`. (d) Output: 212 literals of 64 hexadecimal digits (the 201 Montgomery forms, `R`, `R^2`, `2^65 R`, `5^t R`, `mu R`, `t`, `(t+1)/2`, `(p-1)/2`, `p - 2`, `e`, `p`), 324 each, and `-p^-1 mod 2^64` (16 digits, 81): `68,769`. `T_off = 65,448 + 2,654 + 270 + 68,769 = 137,141` operations. The ledger charges the declared cap `1,000,000 >= T_off` (`preprocessing_log2 = 20`, `2^20 = 1,048,576`), inside `N_max`: a counted bound, not a premise.

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry `e6dcb600`)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g, R - 1)`, `g = g_c^(24)` (4.3G): every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the re-centring division of a node, the division of each repetition of the outer loop, each step of the base case) tests, before it does any work beyond reading the two leading coefficients, that its quotient has degree 1 (2 operations); (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); a zero remainder inside `hgcd` or in the outer-loop division also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state at the start of the trial (`1,000` operations, charged in every trial). Lemma (prefix; `e6dcb600`, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each node of budget `2^j - 1` splits into two calls of budget `2^(j-1) - 1` and, with every quotient of degree 1, every degree in the tree is fixed by `m` and the number of quotients so far, and the budgets of the outer loop (`k = 2^j - 1 <= min(2^22 - 1, (n - 1)/2)`, section 4.4) are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's `hgcd` calls and divisions produce has degree at least the base-case bound, so every gcd of degree at most `DMAX = 16` first appears in the classical Euclid below the base-case degree, after a prefix of the degree-0 work; a zero remainder earlier ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The node follows `4bcabff8`, the charging `e6dcb600`/`1aa56884` proof 4.4 and the in-place applies `a78f526e` proof 4.4, all read as text only (no entry script was run, compiled or imported). Appendix E.2 expands, for `r = 6`, the charge of stage D for the normal sequence with the tests, `3,599,481,127,579`, repetition by repetition.

The `r = 6` trial (`~15.6 GB`, `~1.1e13` operations) exceeds the organizer sandbox (128 MiB, 20 s), so the costs are the exact formula counts of sections 6 and 7; zero-fill clearing is charged (ruling `3476cad8`) and the 64-word register file is the machine restriction of claim.json.

## 7. Memory: the arena of one trial

The arena is the capacity of the allocator of 4.2 on the allocation/free sequence of the trial. Appendix E.3 runs the allocator on every allocation and free of the trial in the order of the program and reports the two-ended-pool high-water mark (the largest sum of the extents of the two ends over the trial), the slab area and the peaks of the live set per stage. The two-ended pool takes the blocks of more than `2^17` bytes and is placed with depth-parity ends and in-place `R*Q` with two spare slots charged (the `POOL_PLACE = 20` discipline). Under the H-NORMAL ABORT stage D the stage-D live set holds the **normal-case division arrays**: on the normal sequence every quotient has degree 1, so each division forms only the quotient of two coefficients and the remainder, and a trial with any other sequence ends (ABORT) after a prefix of these allocations (6.3), so the normal-case walk bounds every trial. With the node arena of 4.4 (`j <= 22`) and the in-place applies of the memory cap the stage-D live peak is `13,723,764,416` bytes, at an outer-step apply by one transform of `3 * 2^24` points (in the two-ended pool `13,723,763,648` bytes: the pair, the stage-D twiddle table, the four entries of the outer-step matrix, two arrays of `2^24` words at the high end and two of `3 * 2^24` words; in the slab classes `768` bytes of small blocks), below the stage-C peak; the stage-D trace of Appendix E.3 has no event that raises the pool's high-water mark. The high-water mark is `15,637,275,264` bytes, reached in stage C (the four arrays of `n'` words of 4.3T, the batch buffer of `11,776` words and the tables, all in the two-ended pool), plus 128 bytes so the unused middle is always at least 128 bytes. The Graeffe prefix (4.3G) holds `E` and `O` on `O1` in the arrays of `A` on `O2` and on `O1` before stage C fills them, with a batch buffer of `11,776` words that it frees: it adds no array and leaves the high-water mark unchanged (Appendix E.3). The slab classes take the smaller blocks: `2,503,296` bytes. Stages E and later hold at most 16 small arrays and the free-list heads: `16,896` bytes. The arena is `15,639,795,584` bytes (two-ended pool `15,637,275,264 + 128`, slab `2,503,296`, stages E and later `16,896`). Peaks of the live set per stage (bytes): A `3,909,091,392`; B `11,425,284,288`; C `15,637,275,264`; D `13,723,764,416`. With `5,250,444` bytes of code and static data and a `65,536`-byte stack, the footprint is `15,645,111,564` bytes `= 2^33.865` (`2^33.86499...`), rounded up at three decimals. No stored advice; each twiddle table is built at run time by the stage that uses it and charged in that stage's row (4.2).

## 8. Review points, answered by location

1. Row D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (6.3): by the prefix lemma every trial executes a prefix of the normal-case work, so the time and memory bounds hold for every sequence; `H-NORMAL` (9.5) enters only the success probability.
2. The node budget cap and the memory cap (4.4) are constants of the algorithm (`k = 2^j - 1 <= 2^22 - 1`, `LMAX = 2^26`, block length `2^22`); its extra transform work is charged in row D, and its effect on the memory is read from the allocation walk of Appendix E (the stage-D live peak `13,723,764,416`, `13,723,763,648` in the pool and `768` in the slab, is below the high-water mark `15,637,275,264` set in stage C; no stage-D event raises it). All 1,082 stage-D pool events of Appendix E.3 (the first 24 are listed) follow one rule: the allocator of 4.2 (first fit in address order) on the allocations and frees of the stage-D arrays of 4.4 in program order, their sizes fixed by `m` on the normal sequence; the largest sum of the two ends over all 1,082 events is `13,723,763,648` bytes (event 443).
3. Row B reproducible from sections 3 and 6 (evaluations * 281, the operations of one line evaluation, + the loop work, the twiddle table and the inverse transform + normalisation). The 64-word register file (the machine restriction of claim.json, 4.2) is the only register assumption; every value beyond it is charged as a load or store.
4. The offline derivation is counted literal class by literal class in 6.2 (`T_off = 137,141` operations) and charged at the declared cap `1,000,000` (`preprocessing_log2 = 20`); the cap over the count moves `time_log2` by less than `10^-6`.
5. The mem penalty uses the rounded-up `mem_log2`, a self-penalizing over-charge.
6. `success = q - delta - eps_coin - eps_iso - eps_g >= 0.39` from the premises `H-ONE` and `H-NORMAL` (9.2, 9.5) with `K = 1`, `q = 0.3931`, `delta = 0.003`; the value is `0.390099999999997628`. The `H-ONE` allowance below the law value is stated exactly (`0.3934693 - 0.3931 = 0.0003693`; `q <= 151/384 = 0.3932292`, the four-moment Bonferroni bound, 9.1), and `delta = 0.003` is the declared premise (9.5); the 3,072 organizer-seeded sequences (10.5.1) are reproducible observations consistent with it, and no population bound is drawn from them.
7. The organizer-checkable output is the returned witness-pair count; the premises hold under trusted execution of the submitted program, disclosed, not claimed as an organizer-verified proof.
8. The Graeffe prefix (4.3G) is exact and adds nothing to the premises of the time or the memory; the success bound uses `H-NORMAL` stated for the pair of the transformed polynomial (9.5), whose organizer-run tests compute that pair (10.5.1).

## 9. The premise and the success bound

### 9.1 H-ONE
The number of centres `c` with `1 <= k(c) <= 16` is at least `q p = 0.3931 p`, `k(c)` the number of nonzero squares `S` with `g_c(S) = 0` (stage D returns `G` with `1 <= deg G <= k(c)` when `k(c) >= 1`, 4.3G). The premise states `q = 0.3931`, the law value `1 - e^(-1/2) = 0.3934693` (9.3) less the extrapolation allowance stated exactly as `0.0003693`; it is also `0.0001292` below the four-moment Bonferroni bound `151/384 = 0.3932292`. The split of the allowance between `H-ONE` and `H-NORMAL` follows cryptogakusei's entry `4888e783`: with `delta = 0.003` (9.5) the bound of 9.2 needs `P(E_c) >= 0.3931` at `K = 1`. The extrapolation, the monodromy theorem at N = 2, 3 and the toy-field and organizer-run evidence are in the claim.json heuristic `H-ONE` and sections 10.3, 10.5.1.

### 9.2 The success bound
The centre is a fresh draw. For a centre `c` let `E_c` be the event `1 <= k(c) <= DMAX` (H-ONE, `P(E_c) >= q = 0.3931`) and `N_c` the event that the remainder sequence of `(g, R_c - 1)` (`g = g_c^(24)`, 4.3G) is normal down to its gcd (H-NORMAL, 9.5, `P(not N_c) <= delta = 0.003`). The Graeffe prefix and the value-domain stage C reproduce `g^(24)` and `R = S^((p-1)/2^25) mod g^(24)` exactly (4.3G, 4.3T) and add no premise; stage C needs `g^(24)` nonzero on `O1`, which fails with probability at most `eps_g = 2^24 n' (D - 1) / p < 2^-175` over the centre (4.3G). If `E_c` and `N_c` hold and `g^(24)` has no zero on `O1`, stages C and D run to their end and return `G = gcd(g^(24), R_c - 1)` with `1 <= deg G <= DMAX` (4.3G); a successful isolation and the scan of 4.1.3 then end in a verified collision. For `c` uniform `P(E_c and N_c) >= q - delta`, so with one centre (the event `g^(24)` zero on `O1` subtracted as `eps_g`)

`success = 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g`, `K = 1`.

Transfer to the written sampler (F-EVAL-001): `q - delta - eps_iso - eps_g` bounds the success probability of the run whose draws are exactly uniform on `F_p` (the premises and the isolation lemma are stated for uniform draws). The success of a run is an event of the vector of its draws, and the actual draws of 4.1.1 are within total variation `eps_coin` of the uniform vector, so the actual success probability is at least the ideal one minus `eps_coin`.

With `q = 0.3931`, `delta = 0.003`, `eps_iso <= 2.371e-15`, `eps_coin <= 1.404e-76`, `eps_g < 2^-175`: `q - delta = 0.3901`, and the value is `0.390099999999997628 >= 0.39`. The bound stays at or above `0.39` for every `delta <= 0.0030999` at `q = 0.3931`. The probability is over the random words of 4.1.1 for the fixed target, not over targets and not a sampled frequency.

### 9.3 Monodromy (support for H-ONE)
The roots of `G(c,t) = g_c(t^2)` come in pairs `+-t_i`, so the monodromy lies in the hyperoctahedral group `B_m` and `k(c)` counts positive Frobenius fixed points; for `B_m` this is Poisson(1/2) in the limit, `P(k >= 1) = 1 - e^(-1/2) = 0.3934693`, and Bonferroni at order 4 gives `P >= 151/384 = 0.3932292`. A theorem at two and three layers (Aubry-Perret, monodromy `B_12`, `B_62`); false for permutation polynomials, for decomposable `F` with imprimitive monodromy, and at one layer.

### 9.4 Isolation lemma
With `1 <= deg G <= 16`, a random-shift split isolates a linear factor within `Z = 64` rounds except with probability `eps_iso <= 2.371e-15`. Finite derivation: `G` divides `Y^((p-1)/2^25) - 1` (4.3G), a divisor of `Y^(p-1) - 1`, so it is squarefree and splits into `d = deg G <= 16` distinct linear factors `X - t_i` over `F_p`. A round with shift `a` keeps a nontrivial part of the current factor `H` under `gcd(H, (X + a)^((p-1)/2) - 1)` (or `X + a` itself when `a = -t_i`), so two roots `t_i != t_j` stay together only if `chi(t_i + a) = chi(t_j + a)` or `a` is in `{-t_i, -t_j}`. Since `sum_a chi((a + t_i)(a + t_j)) = -1` for `t_i != t_j`, exactly `(p - 3)/2` shifts give equal nonzero characters, so for `a` uniform on `F_p` the pair stays together with probability at most `((p - 3)/2 + 2)/p = 1/2 + 1/(2p)`; each shift is a fresh random word reduced mod `p`, within statistical distance `2^-128` of uniform (4.1.1), so per round the bound is `1/2 + 2^-127`, independently across rounds. The parts are nested, so the factor kept after 64 rounds holds two roots only if one of the at most `C(16,2) = 120` pairs was never separated in 64 rounds. By the union bound `eps_iso <= 120 (1/2 + 2^-127)^64 < 6.6e-18 <= 2.371e-15`; the looser stated value `2.371e-15` is kept, so every other number is unchanged.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries `e6dcb600` and `1aa56884`; allowance split of cryptogakusei's `4888e783`; organizer-run tests in the form of gta6rp's `bef31fdd`)
**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(h_c, R_c - 1)`, where `h_c = g_c^(24)` is the 24-fold Graeffe transform (4.3G) of the monic odd part `g_c` of section 3 (monic, degree `m = 122,070,312`) and `R_c = S^((p-1)/2^25) mod h_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.003` (`2^-8.38`). Stage D is charged for the normal sequence; every division tests its quotient degree and every call of the half-gcd its return, and on any other case the trial ends (ABORT, sections 4.4, 6.3). The premise enters only the success probability (9.2): the time and memory bounds hold for every remainder sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work (6.3). For a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes, each a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-199`; the premise extrapolates a much weaker form of this random-pair behaviour (`delta = 0.003`) to the structured pair `(h_c, R_c - 1)`. Measured support is organizer-run (10.5.1): the six experiments `euclid-normal-n2-t256-l2-g24-a` to `-f` compute the complete Euclidean sequence of `(h_c, R_c - 1)` for this construction (24 Graeffe steps, exponent `(p-1)/2^25`) on the truncation `F_2` (`m = 12`) for 256 organizer-seeded trials of two centres each (3,072 sequences in all) and return a witness pair exactly when both sequences of a trial are normal; `euclid-normal-n3-t24-g24` and `euclid-normal-n4-t2-g24` do the same at `m = 62, 312`. Zero abnormal in the 3,072 sequences is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (`delta = 0.003` is the declared premise). Not verified at `r = 6`, which would need the computation itself; the organizer-run tests are at `m = 12` to `312`, far below `m`.

## 10. Experiments

Program `experiments/exp_euclid.py` (euclid-normal, one-centre) and `experiments/exp_line.py` / `experiments/exp_lowbits.py` (line-ladder and lowbits-birthday), with `experiments/manifest.json`.

10.3 The truncations. `F_N(c + X)` is coordinate 0 after the first `N` S-box layers on the line `j = 0`; `F_2`, `F_3`, `F_4` have odd parts of degree `m = 12, 62, 312`. The arithmetic monodromy at `N = 2, 3` is `B_12`, `B_62` (Grok jobs 136, 137, re-run on the deployed constants).

10.5.1 Organizer-run set. euclid-normal-n2-t256-l2-g24-a to -f compute the complete Euclidean sequence of `(h_c, R_c - 1)` (the pair of 9.5: 24 Graeffe steps, exponent `(p-1)/2^25`) for this construction at depth `N = 2` (`m = 12`), each for 256 organizer-seeded trials of two centres (512 sequences per entry, 3,072 in all; the final letter only changes the organizer seeds); euclid-normal-n2-t256-g24, -n3-t24-g24 and -n4-t2-g24 compute one sequence per trial at `m = 12, 62, 312`. A trial returns a witness pair exactly when its sequences are normal; the count of trials that return a pair is a reproducible observation consistent with the premise H-NORMAL (9.5). We do not treat the organizer-seeded centres as independent unselected samples and draw no population bound from these runs: `delta = 0.003` is the declared premise (9.5), carried by its stated support, not by an interval computed from the experiments. one-centre-n2-t256 and one-centre-n3-t24 run one trial of the algorithm with the Graeffe prefix off (`s = 0`: the gcd against `S^((p-1)/2) - 1` and a square root in place of the scan; they test `H-ONE`, a statement about `g_c` that the prefix does not change, 4.3G) at depth `N = 2, 3` per organizer seed and return a witness pair exactly when the sequence is normal, `1 <= k(c) <= 16` and the isolated root gives a verified collision of `F_N`; the returned count is a reproducible observation (9.1), reported as an observation with no interval inferred. line-ladder-w6/-w8/-w10/-w12 and lowbits-birthday corroborate the antipodal structure, not the score-critical basis. Our runs of the six -l2-g24 entries with local seeds (one CPU; 9.34 to 10.47 s each on our workstation): 3,072 sequences, all normal, 256 pairs per entry; the gcd had positive degree for 1,181 of the 3,072 centres. Our runs of -n2-t256-g24, -n3-t24-g24 and -n4-t2-g24: 256, 24 and 2 sequences, all normal. The organizer-checkable output is the returned witness-pair count; the premises H-ONE and H-NORMAL hold under trusted execution of the submitted program.

## Appendix E: rows C and D expanded, and the allocation walk of one trial

Rows C and D and the arena of section 7 are exact counts of the algorithm of sections 4.2-4.4 at `r = 6`. E.1 and E.2 expand each row into its parts, each part a count from the dimensions of 4.3G, 4.3T and the half-gcd levels with the charges of 4.2; each table adds up exactly to its row. E.3 is the allocator of 4.2 run on every allocation and free of the trial in program order: the totals, the live-set peaks per stage, the two-ended-pool high-water mark, the slab classes, and the stage-D allocation/free trace against the high-water mark.

### E.1 Row C = 6,746,634,456,293

Row C is the sum of the steps of section 4.3T in the order the stage runs them:

| part of stage C | operations |
| --- | ---: |
| plans of the passes, the exponent, the node constants and the two-level root tables (built), the zero-fill of `g` above `m`, the first allocations | 68,890,280 |
| the allocation of `A` on `O1`; the Graeffe prefix (4.3G): `24` steps (below) and the allocation and free of its batch buffer | 496,631,581,743 |
| the Newton reciprocal of the reversed `g` to `ell` coefficients (doubling steps, products with running twiddle factors) | 43,846,768,562 |
| the product `q = floor(X^v P1 / g)` (one product of `2 ell - 1` points) and its copy | 12,803,292,178 |
| `g` to `O1` and `O2` (two scaling passes, two truncated forwards; the batch buffer allocated) | 14,387,130,110 |
| the start residue `A0` on `O2` (zero-fill, scaling, truncated forward of `q`, pointwise pass at 8) | 8,466,718,396 |
| `A0` to `O1` (one extension: truncated inverse, scaling, truncated forward) | 14,749,548,704 |
| `k1` on `O1` by chunked batch inversion (chunks of `2^13`, zero tests) | 1,841,736,386 |
| the squaring steps (step 6; below) | 6,121,198,151,740 |
| the exit step `Mont(A, 1)` (pointwise passes and one extension), the frees | 17,040,032,267 |
| two truncated inverses with scaling (`kappa R` and `g` in coefficient form), the frees, the closing control | 15,600,604,927 |
| stage bookkeeping (entry, exit) | 1,000 |
| **row C** | **6,746,634,456,293** |

The squaring steps: `160` steps with exponent bit 0 and `45` with bit 1, `160 * 29,779,056,940 + 45 * 30,145,534,252 = 6,121,198,151,740`. One step (`tr_step`, 4.3T) is:

| part of one step (bit 0) | operations |
| --- | ---: |
| bottom pass on `O1` (`U = A^2 k1`, 4 per point) | 2,511,896,596 |
| four middle-pass sets (inverse and forward, both sides), 4,664,099,388 each | 18,656,397,552 |
| two fused top passes (inverse top, coset twiddle, forward top), 2,189,656,064 each | 4,379,312,128 |
| bottom pass on `O2` (`B2 = (A2^2 + U g) delta_j`, 10 per point for bit 0) | 3,244,851,220 |
| loads of `delta_j` (2 per block of 16 points) | 15,269,888 |
| two recoveries of the dropped subtrees, 485,664,768 each | 971,329,536 |
| step control | 20 |
| **one step, bit 0** | **29,779,056,940** |

A step with bit 1 adds 3 per point of `O2` in its bottom pass: `30,145,534,252 - 29,779,056,940 = 366,477,312 = 3 * 122,159,104`.

The Graeffe prefix (4.3G): `24` steps of `20,692,982,543` each, `496,631,581,032`; with the allocation of `A` on `O1` and the allocation and free of the batch buffer of the prefix, `496,631,581,743`. One Graeffe step (`gt2_step`) is:

| part of one Graeffe step | operations |
| --- | ---: |
| two forward top passes, `E` and `O` read from `g` at stride 2 (`tr_top_half`) | 1,609,935,903 |
| three middle-pass sets (forward `E`, forward `O`, inverse), 4,664,099,388 each | 13,992,298,164 |
| fused bottom pass (forward bottom layers of `E` and `O`, `G = (E^2 - y O^2)/N` at 5 per point, inverse bottom layers) | 3,489,169,428 |
| inverse top pass (stores into `g`) | 1,115,914,240 |
| recovery of the dropped subtrees | 485,664,768 |
| step control | 40 |
| **one Graeffe step** | **20,692,982,543** |

Pass charges (4.3T, `TR_CFG`: top `4` | middle 4, 5, 5, 5 | bottom `4` of the 27 layers, `n' = 122,159,104`): bottom block of `2^4` points with its twiddles, middle blocks and groups of radix 16/32, top blocks of `2^4` points over all `N / 2^4` offsets; the positions above `n'` that layers 1-8 touch are those of the batch buffer, one batch of classes at a time (4.3T). Middle-pass sets `tr_middle = 4,664,099,388`; top pass, fused, `2,189,656,064`; one recovery `485,664,768`.

### E.2 Row D = 3,599,481,127,579

The Euclid driver of 4.4 makes 49 repetitions, each the inversion-free node of budget `k = 2^j - 1` (the largest with `k <= min(2^22 - 1, (n - 1)/2)`) on the top window, the apply of `adj(M)` to the whole pair in place, then one division with the quotient and return tests; `node` is the charge of the node (`pd_node(j) + 10`), `apply` that of the apply, the last column the repetition with the call, the matrix allocations, the arena, the division and the tests. After repetition 49 the pair is below degree `192`, where the classical Euclid runs 168 steps.

| repetition | operand lengths | j | k | node | apply | repetition total |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 122,070,313, 122,070,312 | 22 | 4,194,303 | 72,613,994,389 | 94,730,404,287 | 169,112,543,436 |
| 2 | 117,876,009, 117,876,008 | 22 | 4,194,303 | 72,613,994,389 | 91,594,182,053 | 165,913,406,642 |
| 3 | 113,681,705, 113,681,704 | 22 | 4,194,303 | 72,613,994,389 | 88,457,959,819 | 162,714,269,848 |
| 4 | 109,487,401, 109,487,400 | 22 | 4,194,303 | 72,613,994,389 | 85,321,737,585 | 159,515,133,054 |
| 5 | 105,293,097, 105,293,096 | 22 | 4,194,303 | 72,613,994,389 | 82,185,515,351 | 156,315,996,260 |
| 6 | 101,098,793, 101,098,792 | 22 | 4,194,303 | 72,613,994,389 | 79,049,293,117 | 153,116,859,466 |
| 7 | 96,904,489, 96,904,488 | 22 | 4,194,303 | 72,613,994,389 | 75,913,070,875 | 149,917,722,664 |
| 8 | 92,710,185, 92,710,184 | 22 | 4,194,303 | 72,613,994,389 | 72,776,848,641 | 146,718,585,870 |
| 9 | 88,515,881, 88,515,880 | 22 | 4,194,303 | 72,613,994,389 | 69,640,626,407 | 143,519,449,076 |
| 10 | 84,321,577, 84,321,576 | 22 | 4,194,303 | 72,613,994,389 | 66,504,404,173 | 140,320,312,282 |
| 11 | 80,127,273, 80,127,272 | 22 | 4,194,303 | 72,613,994,389 | 63,368,181,939 | 137,121,175,488 |
| 12 | 75,932,969, 75,932,968 | 22 | 4,194,303 | 72,613,994,389 | 60,231,959,705 | 133,922,038,694 |
| 13 | 71,738,665, 71,738,664 | 22 | 4,194,303 | 72,613,994,389 | 57,095,737,471 | 130,722,901,900 |
| 14 | 67,544,361, 67,544,360 | 22 | 4,194,303 | 72,613,994,389 | 53,959,515,237 | 127,523,765,106 |
| 15 | 63,350,057, 63,350,056 | 22 | 4,194,303 | 72,613,994,389 | 50,823,293,003 | 124,324,628,312 |
| 16 | 59,155,753, 59,155,752 | 22 | 4,194,303 | 72,613,994,389 | 47,687,070,769 | 121,125,491,518 |
| 17 | 54,961,449, 54,961,448 | 22 | 4,194,303 | 72,613,994,389 | 44,550,848,535 | 117,926,354,724 |
| 18 | 50,767,145, 50,767,144 | 22 | 4,194,303 | 72,613,994,389 | 41,414,626,301 | 114,727,217,930 |
| 19 | 46,572,841, 46,572,840 | 22 | 4,194,303 | 72,613,994,389 | 37,422,637,746 | 110,672,314,815 |
| 20 | 42,378,537, 42,378,536 | 22 | 4,194,303 | 72,613,994,389 | 35,142,181,818 | 108,328,944,327 |
| 21 | 38,184,233, 38,184,232 | 22 | 4,194,303 | 72,613,994,389 | 32,005,959,584 | 105,129,807,533 |
| 22 | 33,989,929, 33,989,928 | 22 | 4,194,303 | 72,613,994,389 | 28,869,737,350 | 101,930,670,739 |
| 23 | 29,795,625, 29,795,624 | 22 | 4,194,303 | 72,613,994,389 | 25,733,515,116 | 98,731,533,945 |
| 24 | 25,601,321, 25,601,320 | 22 | 4,194,303 | 72,613,994,389 | 22,597,292,882 | 95,532,397,151 |
| 25 | 21,407,017, 21,407,016 | 22 | 4,194,303 | 72,613,994,389 | 18,503,250,228 | 91,375,439,937 |
| 26 | 17,212,713, 17,212,712 | 22 | 4,194,303 | 72,613,994,389 | 16,261,459,593 | 89,070,734,742 |
| 27 | 13,018,409, 13,018,408 | 22 | 4,194,303 | 72,613,994,389 | 12,605,143,287 | 85,351,503,876 |
| 28 | 8,824,105, 8,824,104 | 22 | 4,194,303 | 72,613,994,389 | 8,737,879,699 | 81,421,325,728 |
| 29 | 4,629,801, 4,629,800 | 21 | 2,097,151 | 33,612,163,471 | 4,212,695,691 | 37,862,853,522 |
| 30 | 2,532,649, 2,532,648 | 20 | 1,048,575 | 15,611,146,654 | 2,032,140,299 | 17,665,552,673 |
| 31 | 1,484,073, 1,484,072 | 19 | 524,287 | 7,216,026,848 | 1,010,371,810 | 8,240,800,058 |
| 32 | 959,785, 959,784 | 18 | 262,143 | 3,314,808,088 | 679,556,442 | 4,004,833,770 |
| 33 | 697,641, 697,640 | 18 | 262,143 | 3,314,808,088 | 495,686,354 | 3,817,031,522 |
| 34 | 435,497, 435,496 | 17 | 131,071 | 1,509,193,305 | 333,425,728 | 1,847,190,033 |
| 35 | 304,425, 304,424 | 17 | 131,071 | 1,509,193,305 | 222,900,132 | 1,734,698,357 |
| 36 | 173,353, 173,352 | 16 | 65,535 | 690,004,574 | 106,590,394 | 798,216,848 |
| 37 | 107,817, 107,816 | 15 | 32,767 | 313,185,629 | 71,664,543 | 385,980,532 |
| 38 | 75,049, 75,048 | 15 | 32,767 | 313,185,629 | 50,583,005 | 364,407,474 |
| 39 | 42,281, 42,280 | 14 | 16,383 | 140,767,931 | 25,658,044 | 166,819,055 |
| 40 | 25,897, 25,896 | 13 | 8,191 | 62,357,608 | 17,266,851 | 79,894,659 |
| 41 | 17,705, 17,704 | 13 | 8,191 | 62,357,608 | 11,339,729 | 73,844,657 |
| 42 | 9,513, 9,512 | 12 | 4,095 | 27,747,929 | 5,300,306 | 33,134,115 |
| 43 | 5,417, 5,416 | 11 | 2,047 | 12,177,349 | 2,628,993 | 14,861,502 |
| 44 | 3,369, 3,368 | 10 | 1,023 | 5,235,579 | 1,768,480 | 7,043,859 |
| 45 | 2,345, 2,344 | 10 | 1,023 | 5,235,579 | 1,198,790 | 6,458,809 |
| 46 | 1,321, 1,320 | 9 | 511 | 2,175,255 | 639,602 | 2,831,617 |
| 47 | 809, 808 | 8 | 255 | 895,023 | 429,776 | 1,337,719 |
| 48 | 553, 552 | 8 | 255 | 895,023 | 262,920 | 1,167,023 |
| 49 | 297, 296 | 7 | 127 | 345,791 | 131,141 | 484,092 |

| part of row D | operations |
| --- | ---: |
| the 49 repetitions above (outer step: node, apply, call; then the division with the quotient and return tests) | 3,599,211,966,959 |
| the classical Euclid below degree 192 (168 steps, quotient test each) | 720,152 |
| driver entry (the table of the 21 scales `1/2^a`: one allocation, 20 multiplications, 21 stores, the loop) | 345 |
| driver exit (the frees, inversion of the leading coefficient, normalisation) | 2,863 |
| stage bookkeeping (entry, exit, the free of `g`, the stage-D twiddle table) | 268,437,260 |
| **row D** | **3,599,481,127,579** |

#### E.2.1 The node charge `node_bf(j)`, a per-block upper bound

The half-gcd node of 4.4 is unchanged: a node of budget `2^j - 1` makes two child calls of budget `2^(j-1) - 1`, applies `adj(M1)` on the three rows `Y - 1`, `Y + 1`, `Y - i`, makes the pseudo-division, and forms the product `M = M1 [[Q, 1], [b^2, 0]] M2` on the two rows `Y - 1`, `Y + 1`. The one change is the transform: each row transform of the node is the block-form pass of `27fbfbe7` 4.2, not the shared-table pass. The pass forms the twiddles of its own block from the running factors; the schedule shares twiddles between blocks, so charging every block its own twiddles is an upper bound. The charge below is computed from the charging rules of 4.2 and 4.4; no integer is taken from another entry's node column. A one per cent allowance, declared in the recursion, covers the control not modelled block by block.

Let `n = 2^(j-1)`, `a = j-1`, and let `F(a)` be the per-block charge of the pass of 4.2:

    F(a) = sum P(a, l0, k)  over the blocks a = l0 + k, k <= 4, l0 a multiple of 4,
                            the last block with 1 <= k <= 4;
    P(a, l0, k) = 150k + 2^(a-k) (2^k + 4)
                  + 2^(a-k) (2*2^k + 3k 2^(k-1) + 5).

The row primitives are `lc(l) = 3l + 2`, `cp(l) = 4l + lc(l)`, `zf(l) = 2l + lc(l)`, `ac(l, u) = (7 + u) l + lc(l)`, and `pw(n, r) = 3 floor(n/8) + 3 + (7 if r = 0 else 10) n`; the row of a transform of `n` points on `L` positions, row index `r`, is

    row(L, r) = cp(min(L, n)) + zf(max(0, n - L))
                  + ac(max(0, L - n), 1 if r = 2 else 0)
                  + 2n [r > 0] + F(a).

The base case of budget `2^6 - 1` is the base entry's two remainder steps per pass, charged `pd(6) = 105,140`; the two-row base case is no larger, so this is an upper bound. For `j >= 7`:

    pd(j) = 184 + 2 pd(j-1) + top(j) + returns(j) + apply(j) + matrix(j)
            + inverse(j) + crt(j) + pseudo(j) + arrays(j),

    top(j)      = sum_{r=0}^2 [row(2^(j+1), r) + row(2^(j+1) - 1, r)],
    returns(j)  = 8 (row(n, 0) + row(n, 1))   if j = 7,
                = 8 row(n, 1)                  if j >= 8,
    apply(j)    = 6 (pw(n, 0) + pw(n, 2)),
    matrix(j)   = 8 (pw(n, 0) + pw(n, 1)),
    inverse(j)  = 6 sum_{r=0}^2 [F(a) + (1 + [r > 0]) n],
    crt(j)      = 4 (10n + lc(n)),
    pseudo(j)   = 30 + 13(2^j - 1) + lc(2^j - 1),
    arrays(j)   = 2 (25n + lc(n)),

and `node_bf(j) = ceil(101 (pd(j) + 10) / 100)`.

The terms are charged as follows. The top apply is charged six row transforms, the two windows `c`, `d` on the three rows. The product is on the two rows `Y - 1`, `Y + 1`; the returned row `Y + 1` is charged eight row products, one row transform each. At `j = 7` the children are base cases and both rows `Y - 1`, `Y + 1` are transformed (4.4), so both are charged. The matrix product is charged eight pointwise passes on the two rows; the 2-row CRT (10 operations per point) is charged four times; the values of `Q` and `M1Q` are charged 25 per point on each of the two rows. The apply's six inverse transforms are charged with the apply, and the pseudo-division is the base entry's. The entry, the return tests and the bump-arena control are 184; the `+10` is the bump-arena allocation. The per-block reading re-forms the twiddles of every block, which is at least the work of the shared schedule.

The charged integers are: `j = 7`: `345,791`; `j = 8`: `895,023`; `j = 9`: `2,175,255`; `j = 10`: `5,235,579`; `j = 11`: `12,177,349`; `j = 12`: `27,747,929`; `j = 13`: `62,357,608`; `j = 14`: `140,767,931`; `j = 15`: `313,185,629`; `j = 16`: `690,004,574`; `j = 17`: `1,509,193,305`; `j = 18`: `3,314,808,088`; `j = 19`: `7,216,026,848`; `j = 20`: `15,611,146,654`; `j = 21`: `33,612,163,471`; `j = 22`: `72,613,994,389`.

| j | `2 pd(j-1)` | top (6 rows) | returns | apply | matrix | inverse | CRT | pseudo-division | arrays | `pd(j)` | `node_bf(j)` |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 7 | 210,280 | 27,349 | 40,928 | 6,852 | 9,136 | 38,640 | 3,336 | 2,064 | 3,588 | 342,357 | 345,791 |
| 8 | 684,714 | 50,481 | 36,288 | 13,668 | 18,224 | 64,644 | 6,664 | 4,112 | 7,172 | 886,151 | 895,023 |
| 9 | 1,772,302 | 96,997 | 67,248 | 27,300 | 36,400 | 117,408 | 13,320 | 8,208 | 14,340 | 2,153,707 | 2,175,255 |
| 10 | 4,307,414 | 215,337 | 162,912 | 54,564 | 72,752 | 298,860 | 26,632 | 16,400 | 28,676 | 5,183,731 | 5,235,579 |
| 11 | 10,367,462 | 418,861 | 310,032 | 109,092 | 145,456 | 562,296 | 53,256 | 32,784 | 57,348 | 12,056,771 | 12,177,349 |
| 12 | 24,113,542 | 834,225 | 615,360 | 218,148 | 290,864 | 1,114,116 | 106,504 | 65,552 | 114,692 | 27,473,187 | 27,747,929 |
| 13 | 54,946,374 | 1,682,485 | 1,249,392 | 436,260 | 581,680 | 2,270,352 | 213,000 | 131,088 | 229,380 | 61,740,195 | 62,357,608 |
| 14 | 123,480,390 | 3,797,433 | 3,075,360 | 872,484 | 1,163,312 | 5,838,108 | 425,992 | 262,160 | 458,756 | 139,374,179 | 140,767,931 |
| 15 | 278,748,358 | 7,510,333 | 6,037,968 | 1,744,932 | 2,326,576 | 11,422,632 | 851,976 | 524,304 | 917,508 | 310,084,771 | 313,185,629 |
| 16 | 620,169,542 | 15,082,689 | 12,158,592 | 3,489,828 | 4,653,104 | 23,031,348 | 1,703,944 | 1,048,592 | 1,835,012 | 683,172,835 | 690,004,574 |
| 17 | 1,366,345,670 | 30,521,413 | 24,791,856 | 6,979,620 | 9,306,160 | 47,130,816 | 3,407,880 | 2,097,168 | 3,670,020 | 1,494,250,787 | 1,509,193,305 |
| 18 | 2,988,501,574 | 68,107,209 | 59,002,848 | 13,959,204 | 18,612,272 | 115,454,796 | 6,815,752 | 4,194,320 | 7,340,036 | 3,281,988,195 | 3,314,808,088 |
| 19 | 6,563,976,390 | 135,020,365 | 116,413,584 | 27,918,372 | 37,224,496 | 227,327,448 | 13,631,496 | 8,388,624 | 14,680,068 | 7,144,581,027 | 7,216,026,848 |
| 20 | 14,289,162,054 | 271,205,073 | 234,379,584 | 55,836,708 | 74,448,944 | 458,147,940 | 27,262,984 | 16,777,232 | 29,360,132 | 15,456,580,835 | 15,611,146,654 |
| 21 | 30,913,161,670 | 548,292,181 | 476,601,840 | 111,673,380 | 148,897,840 | 933,942,000 | 54,525,960 | 33,554,448 | 58,720,260 | 33,279,369,763 | 33,612,163,471 |
| 22 | 66,558,739,526 | 1,209,813,465 | 1,104,175,776 | 223,346,724 | 297,795,632 | 2,207,571,324 | 109,051,912 | 67,108,880 | 117,440,516 | 71,895,043,939 | 72,613,994,389 |

The table's `pd(j)` includes the entry 184 and the children; the listed columns plus 184 add to it. The `node_bf(j)` column is the charged integer.

```python
from math import log2, ceil

def lc(l): return 3*l + 2
def cp(l): return 4*l + lc(l)
def zf(l): return 2*l + lc(l)
def ac(l, u): return (7+u)*l + lc(l)
def pw(n, r): return 3*(n//8) + 3 + (7 if r == 0 else 10)*n

def passes(a):
    out, l0 = [], 0
    while a - l0 >= 4:
        out.append((l0, 4)); l0 += 4
    if a - l0:
        out.append((l0, a-l0))
    return out

def P(a, l0, k):
    b = 1 << (a-k)
    return 150*k + b*((1 << k) + 4) + b*(2*(1 << k) + 3*k*(1 << (k-1)) + 5)

def F(a): return sum(P(a, l0, k) for l0, k in passes(a))

def base_case():
    t = 90
    for s in range(0, 62, 2):
        L = 2*(62-s) + 1
        t += 76 + 13*L + 9*(L-2) + lc(L) + 2*(13*(s+2) + 9*(s+3) + lc(s+3)) + 8
    s = 62; L = 2*(62-s) + 1
    t += 25 + 13*L + lc(L) + 2*(13*(s+2) + lc(s+2)) + 4
    return t

memo = {6: base_case()}
def pd(j):
    if j in memo: return memo[j]
    n, a = 1 << (j-1), j-1; Fa = F(a)
    def row(L, r):
        return (cp(min(L, n)) + zf(max(0, n-L))
                + ac(max(0, L-n), 1 if r == 2 else 0)
                + 2*n*(1 if r > 0 else 0) + Fa)
    top = sum(row(1 << (j+1), r) + row((1 << (j+1))-1, r) for r in range(3))
    S = (0, 1) if j == 7 else (1,)
    returns = 8*sum(row(n, r) for r in S)
    apply = 6*(pw(n, 0) + pw(n, 2))
    matrix = 8*(pw(n, 0) + pw(n, 1))
    inverse = 6*sum(Fa + (1 + (r > 0))*n for r in range(3))
    crt = 4*(10*n + lc(n))
    pseudo = 30 + 13*((1 << j) - 1) + lc((1 << j) - 1)
    arrays = 2*(25*n + lc(n))
    memo[j] = (184 + 2*pd(j-1) + top + returns + apply + matrix + inverse
               + crt + pseudo + arrays)
    return memo[j]

CHARGED = {j: ceil(101*(pd(j)+10)/100) for j in range(7, 23)}
assert pd(6) == 105140
EXPECT = [345791, 895023, 2175255, 5235579, 12177349, 27747929, 62357608, 140767931, 313185629, 690004574, 1509193305, 3314808088, 7216026848, 15611146654, 33612163471, 72613994389]
assert [CHARGED[j] for j in range(7, 23)] == EXPECT

COUNTS = {22: 28, 21: 1, 20: 1, 19: 1, 18: 2, 17: 2, 16: 1, 15: 2, 14: 1, 13: 2, 12: 1, 11: 1, 10: 2, 9: 1, 8: 2, 7: 1}
OLD_NODE = 2460215072115
OLD_REPS = 3958511289916
OLD_D = 3958780450536
TAIL = [720152, 345, 2863, 268437260]
N_OLD = 10893371623534
C = 342
MEM = 33.865
NODE_NEW = sum(CHARGED[j]*c for j, c in COUNTS.items())
REPS_NEW = OLD_REPS - OLD_NODE + NODE_NEW
D = REPS_NEW + sum(TAIL)
assert D == OLD_D - OLD_NODE + NODE_NEW
N = N_OLD + (D - OLD_D)
LOG = log2(N/C)
SCORE = LOG + max(0, MEM - 20)
L = {7: 255, 8: 511, 9: 1023, 10: 2047, 11: 4095, 12: 8191, 13: 16383, 14: 32767, 15: 65535, 16: 131071, 17: 262143, 18: 524287, 19: 1048575, 20: 2097151, 21: 4194303, 22: 8388607}
SHORT = {22: 8824104, 21: 4629800, 20: 2532648, 19: 1484072, 18: 697640, 17: 304424, 16: 173352, 15: 75048, 14: 42280, 13: 17704, 12: 9512, 11: 5416, 10: 2344, 9: 1320, 8: 552, 7: 296}
assert all(L[j] <= SHORT[j] for j in L)
print("node_bf", CHARGED)
print("node sum", NODE_NEW, "row D", D, "N_max", N)
print("log2", repr(LOG), "score", repr(SCORE))
```

The exact-integer script computes every `node_bf(j)`, the node sum of this round's schedule, row D, `N_max`, `log2(N_max/C)` and the normalized score, and checks the top-window bound. It is the evidence for every integer in this subsection.

The tail of row D is unchanged from the base entry and is charged by the base's rules: the classical Euclid below degree 192 `720,152`; the driver entry `345`; the driver exit `2,863`; the stage bookkeeping `268,437,260`. These parts add to the step totals above; the script includes them and checks `row D = 3,599,481,127,579`.

The top window of a node of budget `2^j - 1` has `L(j) = 2^(j+1) - 1` coefficients. The shortest operand at each `j` of the E.2 schedule is the shorter of the pair (for `r = 4, 5` the second operand, of degree `n - 1`; for `r = 6` the exact shorter length in the two-length column of E.2); the bound holds at every call:

| j | `L(j) = 2^(j+1) - 1` | shortest operand at `j` | `L(j) <= shortest` |
|---:|---:|---:|:---:|
| 7 | 255 | 296 | yes |
| 8 | 511 | 552 | yes |
| 9 | 1,023 | 1,320 | yes |
| 10 | 2,047 | 2,344 | yes |
| 11 | 4,095 | 5,416 | yes |
| 12 | 8,191 | 9,512 | yes |
| 13 | 16,383 | 17,704 | yes |
| 14 | 32,767 | 42,280 | yes |
| 15 | 65,535 | 75,048 | yes |
| 16 | 131,071 | 173,352 | yes |
| 17 | 262,143 | 304,424 | yes |
| 18 | 524,287 | 697,640 | yes |
| 19 | 1,048,575 | 1,484,072 | yes |
| 20 | 2,097,151 | 2,532,648 | yes |
| 21 | 4,194,303 | 4,629,800 | yes |
| 22 | 8,388,607 | 8,824,104 | yes |

### E.3 Totals and the allocation walk of one trial

```
m = 122,070,312 | truncated point sets: n1 = 122,159,104 of N = 134,217,728 (TRC = 233 of 256 nodes) | squaring steps 205 of which with S: 45
S_C = 6,746,634,456,293
S_D normal local charges of the tree = 3,599,481,127,579
S_D of the lean stage D on the normal remainder sequence, with the quotient and return tests = 3,599,481,127,579
S_D = 3,599,481,127,579
peak of the live set, stage A = 3,909,091,392 bytes
peak of the live set, stage B = 11,425,284,288 bytes
peak of the live set, stage C = 15,637,275,264 bytes
peak of the live set, stage D = 13,723,764,416 bytes
two-ended pool: blocks of more than 2^17 bytes; largest sum of the two ends after each stage (bytes): init 0, A 3,909,091,392, B 11,425,284,288, C 15,637,275,264, D 15,637,275,264; at most 25 blocks; 4,518 blocks examined in all
slab classes (class: peak number of live blocks): 7: 1, 8: 2, 9: 2, 10: 3, 12: 2, 13: 4, 14: 10, 15: 10, 16: 10, 17: 10; slab area = 2,503,296 bytes
arena = 15,639,795,584 bytes (two-ended pool 15,637,275,264 + 128, slab classes 2,503,296, stages E and later 16,896), memory = 15,645,111,564 bytes, log2 = 33.865
stage D on the two-ended pool (blocks of more than 2^17 bytes): after init, A, B, C: low end 3,909,091,392, high end 3,909,091,392, live 7,818,182,784, largest sum so far 15,637,275,264
  stage D: 1,082 pool events (540 allocations, 542 frees) on 542 distinct blocks; the first 24:
  alloc #3            1,073,741,888 bytes pool L | live      8,891,924,672 | pool low      4,982,833,280 high      3,909,091,392 sum      8,891,924,672
  alloc #4              134,217,856 bytes pool L | live      9,026,142,528 | pool low      5,117,051,136 high      3,909,091,392 sum      9,026,142,528
  alloc #5              134,217,856 bytes pool L | live      9,160,360,384 | pool low      5,251,268,992 high      3,909,091,392 sum      9,160,360,384
  alloc #6              134,217,856 bytes pool L | live      9,294,578,240 | pool low      5,385,486,848 high      3,909,091,392 sum      9,294,578,240
  alloc #7              134,217,856 bytes pool L | live      9,428,796,096 | pool low      5,519,704,704 high      3,909,091,392 sum      9,428,796,096
  alloc #8            2,147,475,520 bytes pool L | live     11,576,271,616 | pool low      7,667,180,224 high      3,909,091,392 sum     11,576,271,616
  free  #8            2,147,475,520 bytes pool   | live      9,428,796,096 | pool low      5,519,704,704 high      3,909,091,392 sum      9,428,796,096
  alloc #9              536,870,976 bytes pool L | live      9,965,667,072 | pool low      6,056,575,680 high      3,909,091,392 sum      9,965,667,072
  alloc #10             268,435,520 bytes pool L | live     10,234,102,592 | pool low      6,325,011,200 high      3,909,091,392 sum     10,234,102,592
  alloc #11             268,435,520 bytes pool L | live     10,502,538,112 | pool low      6,593,446,720 high      3,909,091,392 sum     10,502,538,112
  alloc #12             536,870,976 bytes pool L | live     11,039,409,088 | pool low      7,130,317,696 high      3,909,091,392 sum     11,039,409,088
  alloc #13             268,435,520 bytes pool L | live     11,307,844,608 | pool low      7,398,753,216 high      3,909,091,392 sum     11,307,844,608
  alloc #14             268,435,520 bytes pool L | live     11,576,280,128 | pool low      7,667,188,736 high      3,909,091,392 sum     11,576,280,128
  alloc #15             268,435,520 bytes pool L | live     11,844,715,648 | pool low      7,935,624,256 high      3,909,091,392 sum     11,844,715,648
  free  #9              536,870,976 bytes pool   | live     11,307,844,672 | pool low      7,935,624,256 high      3,909,091,392 sum     11,844,715,648
  free  #10             268,435,520 bytes pool   | live     11,039,409,152 | pool low      7,935,624,256 high      3,909,091,392 sum     11,844,715,648
  free  #11             268,435,520 bytes pool   | live     10,770,973,632 | pool low      7,935,624,256 high      3,909,091,392 sum     11,844,715,648
  free  #12             536,870,976 bytes pool   | live     10,234,102,656 | pool low      7,935,624,256 high      3,909,091,392 sum     11,844,715,648
  free  #13             268,435,520 bytes pool   | live      9,965,667,136 | pool low      7,935,624,256 high      3,909,091,392 sum     11,844,715,648
  free  #14             268,435,520 bytes pool   | live      9,697,231,616 | pool low      7,935,624,256 high      3,909,091,392 sum     11,844,715,648
  free  #15             268,435,520 bytes pool   | live      9,428,796,096 | pool low      5,519,704,704 high      3,909,091,392 sum      9,428,796,096
  free  #4              134,217,856 bytes pool   | live      9,294,578,240 | pool low      5,519,704,704 high      3,909,091,392 sum      9,428,796,096
  free  #5              134,217,856 bytes pool   | live      9,160,360,384 | pool low      5,519,704,704 high      3,909,091,392 sum      9,428,796,096
  free  #6              134,217,856 bytes pool   | live      9,026,142,528 | pool low      5,519,704,704 high      3,909,091,392 sum      9,428,796,096
  the 0 events that raise the high-water mark (the last 0 shown; event number first):
  after stage D: low end 0, high end 0; high-water mark of the pool over the trial 15,637,275,264 bytes
```
