# Orchard Poseidon, r = 6: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, value-domain powering on truncated point sets with radix-16/32 passes, a Graeffe prefix, inversion-free half-gcd on three rows, one centre

## 1. Claim

Target: `poseidon-orchard-r6-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, six partial rounds 4, 5, 6, 7, 8 and 9, full rounds 60-63, state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is an algorithm (sections 2-4) with an operation count that bounds every run (sections 6-7) and a success probability derived from two score-critical premises: `H-ONE` (section 9.1), a statement about the fraction of centres at which the fixed digest polynomial has between 1 and 16 usable roots, and `H-NORMAL` (section 9.5), a statement about the normality of the remainder sequence that enters only the success probability. Section 9.2 derives the success probability from them.

* The algorithm: draw a centre `c` from two fresh random words, `c = (w1 2^256 + w2) mod p` (within statistical distance `p/2^512` of uniform on `F_p`, 4.1.1), build the odd part `g_c` of the line polynomial by evaluation and one inverse transform, replace `g_c` by its 24-fold Graeffe transform `g = g_c^(24)` (monic, degree `m`, its roots the `2^24`-th powers of those of `g_c`; section 4.3G), compute `R = S^((p-1)/2^25) mod g` in the value domain by Montgomery powering on two truncated point sets `O1`, `O2` of `n' = 233 * 2^19 = 122,159,104` points (233 of the 256 depth-8 nodes of the subgroup of order `2^27` and of its coset; the method of bradcush `b30de9bf`/`a41aecdd`, there 15 of 16 nodes, section 4.3T), take `G = gcd(g, R - 1)` by the inversion-free half-gcd on three rows of bradcush `4bcabff8` (outer step `k = 2^j - 1 <= 2^22 - 1`, each matrix applied to the whole pair in place by the block products of the memory cap of weijiekoh `a78f526e`, applies longer than `2^26` in blocks of length `2^22`, section 4.4), charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, and if `G` has degree between 1 and `DMAX = 16` isolate a root `y` of `G` in at most `Z = 64` rounds, find `s` with `s^(2^25) = y` and `F(c + s) = F(c - s)` among at most `2^24` candidates (4.1.3), map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39009`: a lower bound for the probability, over the algorithm's fresh random words, that the centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1), `delta = 0.003` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `eps_iso <= 2.371e-15`, `eps_coin <= 65 p / 2^512 <= 1.404e-76`, `eps_g <= 2^24 n' (D - 1) / p < 2^-175` (the centre makes `g` vanish at a point of `O1`, 4.3G) (sections 4.1.1, 4.3T, 9.2). The value the formula gives is `0.390099999999997628` (at or above the organizer floor 0.39); the claim is that value floored at five decimals.
* `time_log2 = 34.73194` in target-compression units (`C(6) = 342` primitive operations per unit): the operation count that bounds every run, derived in section 6 as `T_fixed + K * T_trial + T_off` with `K = 1`, stage C a Graeffe prefix of 24 steps (4.3G) and value-domain powering on truncated point sets (4.3T), stage D the inversion-free half-gcd on three rows charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (4.4, 6.3; the time bound holds for every sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work), stage E at its cap of `Z` rounds at degree `DMAX`, and the scan of stage F at its cap of `2^24` candidates (4.1.3). `N_max = 9,758,447,943,414` operations, `log2(N_max / 342) = 34.73193633278058139...`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is counted exactly, `T_off = 137,141` operations, and charged at its declared cap of 1,000,000 operations; that cap is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 33.86508` (`15,646,021,292` bytes, section 7). Under the pareto convention `time_log2 + max(0, memory_log2_bytes - 20)` this gives `34.73194 + 13.86508 = 48.59702`; the time-only scalar is `34.73194`, and the memory is reviewed separately.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; every random field element is drawn from two fresh words, at most `65` field elements (`130` words) per run (section 4.1.1), and a draw costs 63 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^12`, then the roots of its odd part about a centre, found, after a Graeffe prefix (Dandelin-Graeffe root squaring), with a gcd against `S^((p-1)/2^25) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Against the newest r6 entry `36aefd2a` at `48.62529`, this package keeps its all-product running-twiddle implementation and applies the residual c7 node levers: a 387-word file, passes through seven layers, and the group-zero twiddle-one body. Row C stays `6,680,271,984,462` and row D becomes `2,890,219,242,247`. `N_max` is `9,758,447,943,414` and the normalized cost is `48.59702`, a gain of `0.02827`. H-ONE, H-NORMAL, the `0.39009` success bound, and our experiments are unchanged.
* This package is the base entry `d7d51e67` with one change to its charge: the half-gcd node keeps the base's two-row product, and each row transform of the node is evaluated in the block form of `27fbfbe7` 4.2; the node charge `node_bf(j)` is derived in Appendix E.2.1 as a per-block upper bound with a declared one per cent allowance, and no integer is taken from another entry's node column. Row D `3,599,481,127,579` (was `3,958,780,450,536`); every other row, the memory and the success bound are unchanged. The top-window bound against the shortest operands of this round is in E.2.1. Normalized cost `48.70728` (was `48.75567`).
* Against our r = 6 entry `6c709970` (time + memory penalty 48.82700), one change to its algorithm: the product step `M = M1 [[Q, 1], [b^2, 0]] M2` of each half-gcd node runs on the two rows `Y - 1`, `Y + 1` (`2n` points) in place of three; its entries have degree at most `2n - 1` on the normal sequence (4.4). Row D `3,958,780,450,536` (was `4,510,919,995,962`); every other row, the memory and the success bound are unchanged. Our entry `6c709970` against our r = 6 entry `134dbc84` (time + memory penalty 48.85304), one change to its algorithm: a Graeffe prefix (4.3G). Stage C first applies 24 Graeffe steps `g(Y) <- E(Y)^2 - Y O(Y)^2` on `O1` (`20,692,982,543` operations each) and then raises `S` to `(p-1)/2^25` (205 squaring steps in place of 229); the gcd keeps exactly the `2^24`-th powers of the usable roots (`1 <= deg G <= k(c)`), and stage F finds the root of `g_c` above the isolated one by a scan of at most `2^24` candidates on the line map (4.1.3). Row C `6,746,634,456,293` (was `6,964,700,241,112`), row F `9,631,344,298` (was `47,012`); memory unchanged. `H-NORMAL` is stated for the pair of the transformed polynomial and its organizer-run tests compute that pair (9.5, 10.5.1); `H-ONE`, every other charge and the other experiments are unchanged.
* Prior entries: `134dbc84` (48.85304) is our r = 6 entry `a5e93fd0` (time + memory penalty 49.24619, the same algorithm and package) with three changes: (i) the loads and stores of the data words of the transform-pass blocks of 4.3T are charged one operation each, base plus index (4.2; the wording of the accepted `89b451ff` and `070a02b2`); (ii) the outer steps of stage D run bradcush's inversion-free half-gcd on three rows (entry `4bcabff8`; the transform reuse of `b30de9bf`), as in our r = 3 entry `bcf8e01c`, ported to `r = 6` and charged in this cost model (section 4.4), in place of the lean cofactor-free half-gcd of bradcush `e6dcb600`/`1aa56884`; (iii) layers 1-8 of the truncated transforms run class-batch by class-batch with the positions above `n'` of the batch in a `11,776`-word buffer, in place of the scratch of `N - n' = 12,058,624` words (4.3T, 7). Row C `6,964,700,241,112` (was `8,114,361,178,793`), row D `4,510,919,995,962` (was `6,634,762,459,061`); memory `2^33.865` (was `2^33.901`), the allocator high-water mark of one trial, reached in stage C (section 7). Every other charge, the premises and the experiments are unchanged. this entry improves our r = 6 entry `cf66371a` (the one-centre algorithm of our r = 6 entry `c318f442`: the two-word coins, the lean cofactor-free half-gcd charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, the memory cap of weijiekoh's entry `a78f526e`, the premises `H-ONE` at `q = 0.3931` and `H-NORMAL` at `delta = 0.003` with the split of cryptogakusei's entry `4888e783` and organizer-run tests in the form of gta6rp's entry `bef31fdd`; bradcush's value-domain stage C on truncated point sets, entries `b30de9bf`, `a41aecdd`; the memory schedule of 0xshikhar's entries `52120fad` and `716c3818`) by three changes: (i) the kernel charges of stage C (4.3T): the bottom twiddles from the two-level table with register constants, running group factors in the middle passes, the recovery with the path value in a register, the scaling fused into the adjacent pass, and the batch-inversion chunk in the scratch above `n'`; (ii) each line evaluation of stage B charged at the operations it executes, `155 + 21 r = 281`, in place of `C(6) = 342` (section 3); (iii) the passes of stage C at radix 16 and 32 on the 64-word register file, stated as a machine restriction in claim.json in the form our r = 3 entry `ef123c2b` states it (4.2, 4.3T). The premises, the coins, stages A and E-G and the organizer-run tests are those of `cf66371a`. The memory is the allocator high-water mark of the one trial (section 7).
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1), a statement about the fraction of good centres, and `H-NORMAL` (score-critical for the success probability only, section 9.5), bradcush's premise on the normality of the remainder sequence stated with the allowance `delta = 0.003`; the organizer-run tests are reproducible observations consistent with it (9.5, 10.5.1). Both are statements about probability. The machine (256 field and 131 integer address registers, all counted in memory; constants as immediates; every load, store and spill counted) is stated as a restriction in claim.json, as the accepted entries `89b451ff` and `fb176310` state theirs, not as a heuristic (4.2). The costs are the declared cost model of this entry, not heuristics: the charging rules of section 4.2 with that register file, the inversion-free half-gcd of stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (Appendix E). Everything else is proved or counted here.

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

### 4.2 Machine model and charging rules (`C(6) = 342`)

Every field operation, load, store, control operation, and random word costs one primitive operation. One target-compression unit is `C(r) = 216 + 21r = 342` operations.

The machine has one file of 387 256-bit registers. It has 256 field registers and 131 integer address registers. A radix-128 block uses 128 values, 127 twiddles, and one temporary. Its call uses at most 128 row bases, one twiddle address, one position offset, and one loop bound. Section 7 counts all `387 * 32 = 12,384` bytes. This construction follows Jbenisek `c7ef0551` and the register-file precedent of cryptogakusei `1533f8f0`.

Loads and stores in transform blocks use base-plus-index addressing and cost one operation each. The predecessor already used this rule. A loop over `cnt` positions, eight positions per straight-line body, costs

    F(cnt) = 1 + 3 floor(cnt/8) + 2 + 3 (cnt mod 8) + 2.

The terms are the initial bound, three controls per full body, two controls at the main-loop exit, three controls per remainder position, and two controls at the remainder-loop exit.

A column pass of `k` layers has `2^k` rows. Before the offset-zero specialization, its kernel costs `c0(k) + c1(k) cnt + F(cnt)`. The pairs `(c0,c1)` for `k = 1,...,7` are `(5,11)`, `(6,20)`, `(10,52)`, `(18,128)`, `(34,304)`, `(139,704)`, and `(269,1600)`. For six layers, `139 = 2*63 + 3 + 2*(6-1)` and `704 = 2*64 + 3*6*32`. For seven layers, `269 = 2*127 + 3 + 2*(7-1)` and `1600 = 2*128 + 3*7*64`. The call wrapper adds `2*2^k + 6` for the row bases and twiddle address, then 3 for the call loop. At offset zero, `2^k - 1` butterflies per position have twiddle one. The straight-line variant subtracts `(2^k - 1) cnt` multiplications and adds 3 controls. A run uses a first remainder pass and then seven-layer passes.

Every polynomial-product pass in stages C and D uses running twiddle factors and no shared stage table, the construction of Jbenisek `56272e37` and `27fbfbe7`. For a row of `2^a` points, a pass at level `l0` with width `k <= 7` has `2^l0` groups, `2^(a-l0-k)` blocks per group, and `2^(a-k)` blocks. A block costs

    B(k) = 2*2^k + 3k*2^(k-1) + 3.

The terms are the loads and stores, the butterflies, two block-base updates, and one share of the four-block loop. The running twiddle chain costs `2^k + 4`: one root advance, `k-1` squarings, `2^k-1-k` multiplications by register constants, and five controls. The per-layer step and chain constants cost `150k` per pass. Group zero replaces each twiddle-one multiplication by addition and subtraction. Its straight-line body removes `2^k - 1` operations in every block of that group and adds 3 controls.

The half-gcd node uses a deliberately larger per-block reading. Every block pays for a full running twiddle chain even though the implementation shares the chain. Its forward or inverse pass charge is

    150k + blocks (B(k) + 2^k + 4)
         - blocks_per_group (2^k - 1) + 3.

Appendix E.2.1 adds the declared one-percent allowance after summing the node. No integer in that recurrence comes from another submission.

The truncated transforms of stage C keep their proved split `4 | 4,5,5,5 | 4`. Four blocks run per straight-line loop body. Appendix E.1 derives the middle and bottom deltas, including every extra array-pointer update. The Newton and quotient products also use running twiddles. Their predecessor component totals remain charged as conservative caps, so the package does not rely on another entry's product total or undercharge those paths. Stage D treats its outer applies the same way: every pass executes with running twiddles, while E.2 retains the predecessor's larger apply charge. The node recurrence itself is re-derived.

The allocator remains one preallocated arena. The pool, slab, allocation, free, and walk rules are unchanged. Stage B keeps its transform table. The two-level root tables of the truncated transforms remain. Stages C and D build no product twiddle table. The algorithm uses one thread and no dispatch.

### 4.3G The Graeffe prefix

Definition. For `h` monic of even degree `m` write `h(X) = E(X^2) + X O(X^2)`; its Graeffe transform is `h~(Y) = E(Y)^2 - Y O(Y)^2`, so `h~(X^2) = h(X) h(-X)` and `h~` is monic of degree `m` with roots the squares of the roots of `h` (with multiplicity). Stage C first replaces `g = g_c` by `g^(24)`, 24 Graeffe steps, then computes `R = S^e mod g^(24)`, `e = (p-1)/2^25` (2-adicity 32), and stage D takes `G = gcd(g^(24), R - 1)`.

Lemma. `G` is the product of `(Y - y)` over the distinct values `y = S^(2^24)`, `S` a usable root of `g_c` (a nonzero square in `F_p` with `g_c(S) = 0`, section 3). Proof: `g^(24)(Y) = prod_i (Y - S_i^(2^24))` over the roots `S_i` of `g_c` in an algebraic closure; `Y^e - 1` is squarefree and its roots are the `2^25`-th powers of `F_p^*`. If `S_i^(2^24) = u^(2^25)` with `u` in `F_p^*`, then `S_i = u^2 zeta` with `zeta^(2^24) = 1`, so `zeta` is in `F_p` and `zeta = xi^2` with `xi^(2^25) = 1` (`2^25 | p - 1`), and `S_i = (u xi)^2` is a nonzero square of `F_p`; conversely `S = v^2` gives `S^(2^24) = v^(2^25)`. So `deg G` is the number of distinct `2^24`-th powers of the usable roots: `1 <= deg G <= k(c)` when `k(c) >= 1`, and `deg G = 0` when `k(c) = 0`; the event `E_c` of 9.2 gives `1 <= deg G <= DMAX`.

Execution (on the point set `O1` of 4.3T). One step: `E` (`m/2 + 1` coefficients) and `O` (`m/2`) are read from `g` at stride 2 by the top passes of two truncated forwards, which load only the input blocks below the length (8 or 7 of the 16 per offset, two offset ranges per batch; butterflies only on nonzero inputs; no zero-fill); the fused bottom pass forms `G = (E^2 - y O^2)/N` at each point `y` of `O1` between the forward and the inverse bottom layers (`y` is the last-layer twiddle of its butterfly, in a register: two squarings, two multiplications, one subtraction, 5 per point); one truncated inverse stores the new coefficients into the array of `g` (those above `m` come out zero). `E` and `O` on `O1` use the arrays of `A` on `O2` and of `A` on `O1` before stage C fills them, with a batch buffer of `11,776` words of their own, used by one transform at a time and freed after the prefix; no array is added and the high-water mark of section 7 is unchanged. One step is `20,545,035,023` operations (Appendix E.1), 24 steps; stage C then runs 205 squaring steps in place of 229 (the exponent loses 24 low zero bits). A step saves one squaring step (`29,779,056,940`) for `20,692,982,543` and doubles the scan of 4.1.3 (`2^s * 574`); `s = 24` minimises the total.

Every map is exact; no premise is added to the time or the memory. The zero test of `k1` (4.3T) now concerns `g^(24)`: `g^(24)(y) = 0` for `y` in `O1` only if `g_c(x) = 0` for one of the `2^24` values `x` with `x^(2^24) = y` (in `F_p` or an extension); for each such `x`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g^(24) vanishes on O1) <= 2^24 n' (D - 1) / p = eps_g < 2^-175`.

### 4.3T Stage C in the value domain on truncated point sets (the method of bradcush `b30de9bf`/`a41aecdd`, 233 of 256 nodes)

Point sets. `N = 2^27` divides `p - 1` (2-adicity 32). Let `psi` have order `2^28`, `H_N = <psi^2>` and `Y = X^(2^19)`. `H_N` is the union of the 256 depth-8 nodes `{x : x^(2^19) = r_j}`, `r_j` the 256-th roots of unity in transform (bit-reversed) order; `O1` is the union of the first 233 nodes, `n' = 233 * 2^19 = 122,159,104 >= m + 1 = 122,070,313` points, and `O2` the same 233 nodes of the coset `psi H_N` (`x^(2^19) = r'_j`, `r'_j^256 = -1`), disjoint from `O1`. `P1 = prod_{j<233} (Y - r_j)` has degree `n'`, vanishes on `O1` and is the nonzero constant `P1(r'_j)` on node `j` of `O2`; `delta_j = 1/P1(r'_j)` (233 table constants).

Truncated transforms (bradcush `b30de9bf` 4.3, generalized as the truncated Fourier transform of van der Hoeven, ISSAC 2004). A polynomial of degree `< n'` is `sum_{k<256} P_k Y^k` with `deg P_k < 2^19` and `P_k = 0` for `k >= 233`; its values on the 233 nodes determine it and are determined by it (the CRT for the 233 coprime moduli `Y - r_j`, whose product `P1` has degree `n'`). The forward transform runs the top 4 layers on all `N/16` offsets (no truncation saving is charged), the middle layers only on the blocks above present nodes, and the bottom 4 layers on the `n'` points. The inverse runs the same layers in reverse, scales each 16-point block of its bottom pass by `diag(1, c^-1 J)` (`c = y^16` of the block, `V^T V = 16 diag(1, cJ)`; 15 multiplications and the load of `c^-1`, 17 operations per block), and recovers the residues of the dropped part `[233, 256)`, the maximal subtrees `{233}`, `{234..235}`, `{236..239}`, `{240..255}` (depths 8, 7, 6, 4), from the known zero chunks `P_k = 0` along their paths to the root, as bradcush recovers the one dropped leaf; with the value of the path held in a register this is charged 8 operations (3 multiplications, 3 additions, the load of the known value) per point of a dropped subtree per layer of its path and one store (2) per point. Layers 1-8 (the top pass, the first middle pass and the recoveries) act on each class of the `256` positions with equal low 19 bits separately (`233` in `O1`, `23` above `n'`: the dropped nodes `[233, 256)`), so they run class-batch by class-batch, `1,024` batches of `512` classes, the `23` positions above `n'` of each class of the batch held in one batch buffer of `11,776` words and discarded after the batch (one transform runs at a time); the passes below layer 8 touch only the `n'` positions. Charged once per batch: the 16 groups, the pass overhead and the batch loop of the first middle pass (`16 * 20 + 20 + 3`), the top-pass overhead with its 31 register constants and 16 inner loops, one per depth-8 node within a lane (`4 * 31 + 20 + 16 * 5`), the path constants of each recovery (the 25 levels of the paths of the four dropped subtrees, 3 constants each at 2, and their 4 loops at 5: `170`), and before the top of each truncated forward the zero-fill of the `7 * 512 = 3,584` positions of the batch above `n'` in lane 14 (a store, 2, each and the loop). The passes are fused as in `b30de9bf` 4.5 under the predecessor's 64-word layout, whose larger spill charge this package retains as a conservative cap; the 387-word machine executes the same 27-layer split 4 | 4, 5, 5, 5 | 4 (`TR_CFG`, the cheapest split under that register file): a bottom pass (16-point blocks: forward layers, the pointwise map, inverse layers; one set of 15 twiddles for both directions, 19 operations per block: two loads from the two-level table, one multiplication, three squarings, eleven multiplications by register constants), a middle pass of radix 16 (per block 16 loads and 16 stores at one operation each, 32 butterflies and 5 control, 133; per group a running group factor, 1 multiplication, and its 15 twiddles formed by 3 squarings and 11 multiplications and held in registers, 20 per group with its overhead), three middle passes of radix 32 (per block 32 loads and 32 stores at one operation each, 80 butterflies, the loads of the 3 twiddles that do not fit (6) and 5 control, 315; per group the running factor and its 31 twiddles by 4 squarings and 22 multiplications, 28 of them in registers with the 32 data words, the factor and a temporary, 62 of the 64 words, and 3 stored, 38 per group with its overhead), and a top pass over all `N/16` offsets that fuses the inverse top of one set with the forward top of the other (31 coset constants in registers).

Montgomery powering (`b30de9bf` 4.5). For residues of degree `< n'`, `Mont(A, B) = (A B + u g)/P1` with `u = -A B / g mod P1` (`deg u < n'`); the division by `P1` is exact, `Mont(A, B) = A B / P1 mod g`, and `deg Mont(A, A) <= n' - 2`, so `X Mont(A, A)` has degree `< n'`. A residue `A` (representing `S^e P1`) is held by its values on `O1` and on `O2`, each up to a tracked scalar. One step: `U = A^2 k1` on `O1` (`k1 = -1/(N^3 g)` there; `u` is determined by its values on `O1`); `U` to `O2` (truncated inverse on `O1`, truncated forward on `O2`); `B2 = (A2^2 + U g) delta_j` on node `j` of `O2`, which is `Mont(A, A)` up to the tracked scalar because `P1 = 1/delta_j` there, times the point `x` when the exponent bit is 1; `B2` to `O1` (truncated inverse on `O2`, truncated forward on `O1`). No `1/N` is executed inside the steps (the scalars are tracked, 2 operations per step). Per point and step: on `O1` `sqr, LD k1, mul` (4); on `O2` `LD A2, sqr, LD g, mul, add`, the multiplication by `delta_j`, `ST` (10) and the load of `delta_j` per block (2); 3 more for a 1-bit (the load of the point and a multiplication).

Entry and exit. `g` (coefficients after the Graeffe prefix of 4.3G, its slots above `m` zero) goes to `O1` and `O2` (a truncated forward each; every scaling of this section, `1/N` and the coset twist, is a running product fused into the adjacent pass, 2 operations per point). The start residue is `A0 = X^v P1 mod g`, `v = 2^24 = 16,777,216` (VSHIFT = 2): `q = floor(X^v P1 / g)` has `ell = v + n' - m + 1 = 16,866,009` coefficients and is formed from the Newton reciprocal of the reversed `g` and one product (transforms of up to `3*2^24` points, with running twiddle factors and no stage product table); on node `j` of `O2`, `x^v P1(x) = r'_j^32 P1(r'_j)` is a constant, so `A0 = x^v P1 - q g` there is one truncated forward of `q` and one pointwise pass (8 per point); then `A0` goes to `O1`. `k1` is formed by chunked batch inversion on `O1` (chunks of `2^13` points: prefix products, one inversion, two multiplications per point; the `2^13` prefixes are kept in the batch buffer, which no transform uses at that time); each chunk product is tested for zero before its inversion (2 per chunk), and a zero ends the trial: for fixed `x != 0`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g vanishes on O1) <= eps_g < 2^-175` for the transformed `g` (4.3G, 9.2). The exit is one step with multiplier 1 (`Mont(A, 1)`) and two truncated inverses with their scaling, which return `kappa R` (`kappa` the tracked scalar) and `g` in coefficient form; the gcd is scale-invariant, so stage D receives `kappa R - kappa`. There are `205` squaring steps (the exponent `(p-1)/2^25`, 4.3G), `45` of them also multiplying by `S`.

Exactness and memory. Every map above is exact (Montgomery products of polynomials of degree `< n'`, held bijectively by their values on 233 nodes); no premise is added to stage C. The live set of the stage is four arrays of `n'` words (`g` on `O2`, `A` on `O2`, `A` on `O1`, `k1` on `O1`), the batch buffer of `11,776` words, the tables (`263 + 16,384` words: 30 constants, the 233 `delta_j`, the two-level root tables) and, while `q` is formed, the Newton arrays. The step-by-step count is expanded in Appendix E.1 and totals **row C = 6,680,271,984,462** (section 6).

### 4.4 Stage D: the inversion-free half-gcd on three rows (bradcush `4bcabff8`), with the in-place applies of the memory cap

`G = gcd(g, R - 1)` is computed by bradcush's inversion-free half-gcd (entry `4bcabff8`, with the transform reuse of `b30de9bf`; read as text only, ported and charged in this cost model as in our r = 3 entry `bcf8e01c`). Matrices and remainders are kept up to nonzero scalars with pseudo-division (`b^2 a = Q b + e`, `Q` of degree 1 on the normal sequence), so no field inversion runs inside the recursion; the gcd is the same up to a scalar and is made monic at the end. A node of budget `k = 2^j - 1` makes two child calls of budget `2^(j-1) - 1`; its products run on `3 * 2^(j-1)` points, the rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), each a power-of-two transform of `n` points in the block form of `27fbfbe7` 4.2 after a twist (E.2.1), joined by a 3-row CRT for `(c, d) = adj(M1)(a, b)` on the top window; then the pseudo-division and the product `M = M1 [[Q, 1], [b^2, 0]] M2` on the two rows `Y - 1`, `Y + 1` only (`2n` points; 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` with the `1/2` folded into the `1/n` of the inverse, 10 operations per point). The product needs no third row: on the normal sequence every quotient has degree 1 and `b^2` is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; the row `Y - 1` values of each child's matrix are returned by the child, the row values of `M1` are kept from the apply and reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). The twist roots of order `2n` and `4n` come from the squaring chain of the running twiddle factors of the row transform (4.2); the scales `1/2^a` (`a <= 21`) are a table of 21 words built at the entry of stage D (`1/2 = (p + 1)/2` an immediate, 20 multiplications). The base case (budget 63) runs two remainder steps per pass over its window. Driver: while `(n - 1)/2 >= 127`, one outer step calls the node on the top window of the pair with `k = 2^j - 1` the largest with `k <= min(2^22 - 1, (n - 1)/2)`, applies `adj(M)` to the whole pair in place, and makes one division with the quotient test; the apply is that of the memory cap (the method of weijiekoh `a78f526e`, its `mat_apply` LMAX, as in `a5e93fd0`): an apply to a pair longer than `LMAX = 2^26` coefficients is done by the block products of scheme (a) at the block length `2^22` (transforms of `2^23` points), each block of the operands transformed once, the transforms of a slot multiplied pointwise and summed, and each output slot inverse transformed and overlap-added in place into the output array. At `r = 6` the pair is below degree `192` after the last outer step, and classical division steps finish. The working arrays of a node live in one bump arena (an allocation or release is 10 operations) of `67,108,608` words at `j = 22`, the peak of its recursion; the cap `j <= 22` keeps the arena and the pair below the stage-C peak (section 7). On the normal sequence every length, budget and allocation is a function of `m` alone. The row is charged for the normal remainder sequence (every quotient of degree 1), the case of the premise `H-NORMAL` (9.5): every division and pseudo-division tests that its quotient has degree 1 and every call tests on return that it removed exactly its budget (2 operations each), and a zero remainder also ends the trial; on any other case the trial ABORTs (the allocator is reset and the run ends without output, section 6.3). By the prefix lemma of 6.3 every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, so the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The total is **row D = 2,890,219,242,247** (section 6.3, 6; Appendix E.2).

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G = gcd(g, R - 1)`, whose roots are the values `y = S^(2^24)` of the usable roots `S` of `g_c` (4.3G); stage F stops only at an `s != 0` with `F(c + s) = F(c - s)` (4.1.3), so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Ledger: operation count (`C(6) = 342`)

| row | what is charged | operations |
| --- | --- | ---: |
| init | constants and bookkeeping | 17,980 |
| setup | line setup | 4,910 |
| A | trial bookkeeping, centre draw, allocation | 1,228 |
| B | line evaluations, loop work, transform, normalization | 178,154,740,855 |
| C | 24 Graeffe steps and exact value-domain powering from the running-twiddle base; Appendix E.1 | 6,680,271,984,462 |
| D | inversion-free half-gcd, normal-sequence walk with ABORT; Appendix E.2 | 2,890,219,242,247 |
| E | 64 isolation rounds at degree at most 16 | 166,081,821 |
| F | square roots and at most `2^24` line candidates | 9,631,344,298 |
| G | two reference hashes | 7,872 |
| trial loop | loop bookkeeping and allocator reset | 1,012 |
| plan misses | one per distinct plan size | 126,649 |
| output | fixed output rows | 3,390,080 |
| offline | declared cap over the 137,141-operation derivation | 1,000,000 |
| **N_max** | `T_fixed + T_trial + T_off` | **9,758,447,943,414** |

`T_fixed = 3,539,619`, `T_trial = 9,758,443,403,795`, and `T_off = 1,000,000`. Thus `N_max = 9,758,447,943,414`. The raw time is `log2(N_max/342) = 34.731936332780581396997840559028158597638967018783662040208507249085677673194249`. The claim rounds it upward at five decimals to `34.73194`.

Appendix E derives each changed charge. All searches stay charged. Stage F remains at its `2^24` cap, stage E remains at 64 rounds, and the offline search space contains no search or choice.

### 6.1 Validation

Run `python3 -B ledger_v2.py` from this candidate tree. The script derives the six- and seven-layer kernels, the running-twiddle node recurrence, both table removals, rows C and D, `N_max`, both logarithms, and the score.

### 6.2 Offline derivation

The literal derivation is unchanged. It executes 137,141 operations and is charged at its declared cap of 1,000,000 operations inside `N_max`. Its working set is 16 words plus a 64-byte digit buffer, 576 bytes, counted in section 7.

### 6.3 The normal-sequence charge and ABORT

The quotient test and return test are unchanged. On the first abnormal quotient, short return, or zero remainder, the trial resets the allocator and stops. Until that event, every length, budget, and allocation equals the normal walk. Thus every abnormal trial executes a prefix of the charged work and allocation sequence. `H-NORMAL` affects only success probability.

## 7. Memory counted by event

The arena capacity remains `15,639,784,832` bytes. Stage C sets the running-twiddle predecessor's high-water mark at `15,637,275,264` bytes. The residual wider node changes no allocation size, so we retain that arena exactly. This covers every unchanged allocation event of the normal walk and every prefix that an ABORT can execute.

| event or fixed region | bytes | effect on high-water mark |
| --- | ---: | --- |
| stage A live peak | 3,909,091,392 | below the retained arena |
| stage B live peak | 11,425,284,288 | below the retained arena |
| stage C predecessor peak | 15,637,275,264 | sets the retained pool mark |
| stage-C product table | removed | running twiddles; cannot raise the mark |
| stage D predecessor peak | 12,650,022,528 | below the stage-C mark |
| stage-D product table | absent in 36aefd2a | running twiddles |
| two-ended pool reserve and middle gap | 15,637,275,392 | predecessor mark plus 128 bytes |
| slab classes | 2,492,544 | unchanged |
| stages E and later | 16,896 | unchanged |
| **arena** | **15,639,784,832** | exact retained capacity |
| base code and static data | 5,250,444 | unchanged base image |
| seven-layer and group-zero straight-line bodies | 907,520 | replaces 39,228 bytes of four-layer bodies |
| register file, `387 * 32` | 12,384 | charged machine state |
| offline working set | 576 | 16 words and digit buffer |
| stack | 65,536 | unchanged |
| **footprint** | **15,646,021,292** | sum of all rows |

The raw memory logarithm is `33.865076782256819792451885686275423095363588526600509277497096322187375327633672`. The claim rounds it upward at five decimals to `33.86508`. The arena contains no stored advice. Stage B and the truncated transforms build only their declared tables. Every product pass in stages C and D forms twiddles as running factors.

## 8. Evaluation obligations

1. `target_defined`: sections 1 through 3 name the exact Orchard P128Pow5T3 target, round selection, input domain, and full field output.
2. `algorithm_defined`: sections 4 and 5 define the line, Graeffe prefix, exact value-domain powering, half-gcd, isolation, root lift, back-map, and final verification.
3. `resources_defined`: sections 4.2, 6, 7, and Appendix E define the word RAM, every changed pass, all searches, preprocessing, total operations, and memory events.
4. `probability_space_defined`: sections 4.1.1 and 9.2 define the fixed target and the fresh random words. The sampler bias is subtracted once.
5. `heuristics_disclosed`: claim.json and sections 9.1 and 9.5 state H-ONE and H-NORMAL with their scope, evidence, extrapolation, and limits.
6. `evidence_relevant`: section 10 and the experiment manifest bind the unchanged experiments to this line construction, Graeffe pair, normality premise, and collision checks.

The machine change adds no heuristic. It changes only the implementation and its operation bound. The success calculation and experiment files remain unchanged.

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

## Appendix E: exact changed rows and memory events

### E.1 Row C = 6,680,271,984,462

| part | operations |
| --- | ---: |
| plans, constants, root tables, zero fill, first allocations | 1,780,782 |
| allocation of `A`; 24 Graeffe steps and prefix buffer | 493,080,841,211 |
| Newton reciprocal with running twiddles | 30,501,953,933 |
| quotient product and copy with running twiddles | 8,858,369,870 |
| `g` to `O1` and `O2` | 14,245,768,958 |
| start residue `A0` on `O2` | 8,396,037,820 |
| `A0` to `O1` | 14,608,187,552 |
| `k1` by chunked inversion | 1,841,736,386 |
| 205 squaring steps | 6,076,379,392,060 |
| exit Montgomery step | 16,898,671,115 |
| two truncated inverses | 15,459,243,775 |
| stage bookkeeping | 1,000 |
| **row C** | **6,680,271,984,462** |

Row C is the exact locally checked running-twiddle row of the direct r6 construction. The residual c7 change affects only the node recurrence in this package, so every row-C event remains unchanged.

### E.2 Row D = 2,890,219,242,247

| repetition | operand lengths | j | k | node | apply | repetition total |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 122,070,313, 122,070,312 | 22 | 4,194,303 | 63,819,292,800 | 65,457,938,573 | 131,045,375,977 |
| 2 | 117,876,009, 117,876,008 | 22 | 4,194,303 | 63,819,292,800 | 63,283,875,875 | 128,808,398,719 |
| 3 | 113,681,705, 113,681,704 | 22 | 4,194,303 | 63,819,292,800 | 61,109,813,177 | 126,571,421,461 |
| 4 | 109,487,401, 109,487,400 | 22 | 4,194,303 | 63,819,292,800 | 58,935,750,479 | 124,334,444,203 |
| 5 | 105,293,097, 105,293,096 | 22 | 4,194,303 | 63,819,292,800 | 56,761,687,781 | 122,097,466,945 |
| 6 | 101,098,793, 101,098,792 | 22 | 4,194,303 | 63,819,292,800 | 54,587,625,083 | 119,860,489,687 |
| 7 | 96,904,489, 96,904,488 | 22 | 4,194,303 | 63,819,292,800 | 52,413,562,377 | 117,623,512,421 |
| 8 | 92,710,185, 92,710,184 | 22 | 4,194,303 | 63,819,292,800 | 50,239,499,679 | 115,386,535,163 |
| 9 | 88,515,881, 88,515,880 | 22 | 4,194,303 | 63,819,292,800 | 48,065,436,981 | 113,149,557,905 |
| 10 | 84,321,577, 84,321,576 | 22 | 4,194,303 | 63,819,292,800 | 45,891,374,283 | 110,912,580,647 |
| 11 | 80,127,273, 80,127,272 | 22 | 4,194,303 | 63,819,292,800 | 43,717,311,585 | 108,675,603,389 |
| 12 | 75,932,969, 75,932,968 | 22 | 4,194,303 | 63,819,292,800 | 41,543,248,887 | 106,438,626,131 |
| 13 | 71,738,665, 71,738,664 | 22 | 4,194,303 | 63,819,292,800 | 39,369,186,189 | 104,201,648,873 |
| 14 | 67,544,361, 67,544,360 | 22 | 4,194,303 | 63,819,292,800 | 37,195,123,491 | 101,964,671,615 |
| 15 | 63,350,057, 63,350,056 | 22 | 4,194,303 | 63,819,292,800 | 35,021,060,793 | 99,727,694,357 |
| 16 | 59,155,753, 59,155,752 | 22 | 4,194,303 | 63,819,292,800 | 32,846,998,095 | 97,490,717,099 |
| 17 | 54,961,449, 54,961,448 | 22 | 4,194,303 | 63,819,292,800 | 30,672,935,397 | 95,253,739,841 |
| 18 | 50,767,145, 50,767,144 | 22 | 4,194,303 | 63,819,292,800 | 28,498,872,699 | 93,016,762,583 |
| 19 | 46,572,841, 46,572,840 | 22 | 4,194,303 | 63,819,292,800 | 26,061,193,288 | 90,516,168,612 |
| 20 | 42,378,537, 42,378,536 | 22 | 4,194,303 | 63,819,292,800 | 24,150,747,288 | 88,542,808,052 |
| 21 | 38,184,233, 38,184,232 | 22 | 4,194,303 | 63,819,292,800 | 21,976,684,590 | 86,305,830,794 |
| 22 | 33,989,929, 33,989,928 | 22 | 4,194,303 | 63,819,292,800 | 19,802,621,892 | 84,068,853,536 |
| 23 | 29,795,625, 29,795,624 | 22 | 4,194,303 | 63,819,292,800 | 17,628,559,194 | 81,831,876,278 |
| 24 | 25,601,321, 25,601,320 | 22 | 4,194,303 | 63,819,292,800 | 15,454,496,496 | 79,594,899,020 |
| 25 | 21,407,017, 21,407,016 | 22 | 4,194,303 | 63,819,292,800 | 12,877,093,540 | 76,954,581,504 |
| 26 | 17,212,713, 17,212,712 | 22 | 4,194,303 | 63,819,292,800 | 11,499,595,145 | 75,514,168,549 |
| 27 | 13,018,409, 13,018,408 | 22 | 4,194,303 | 63,819,292,800 | 8,805,438,375 | 72,757,097,219 |
| 28 | 8,824,105, 8,824,104 | 22 | 4,194,303 | 63,819,292,800 | 6,436,030,588 | 70,324,774,872 |
| 29 | 4,629,801, 4,629,800 | 21 | 2,097,151 | 29,795,972,627 | 3,257,442,829 | 33,091,409,660 |
| 30 | 2,532,649, 2,532,648 | 20 | 1,048,575 | 13,865,617,022 | 1,454,237,025 | 15,342,119,611 |
| 31 | 1,484,073, 1,484,072 | 19 | 524,287 | 6,428,383,931 | 724,860,434 | 7,167,645,609 |
| 32 | 959,785, 959,784 | 18 | 262,143 | 2,967,386,583 | 486,681,226 | 3,464,536,893 |
| 33 | 697,641, 697,640 | 18 | 262,143 | 2,967,386,583 | 357,548,724 | 3,331,472,231 |
| 34 | 435,497, 435,496 | 17 | 131,071 | 1,362,521,534 | 239,935,634 | 1,607,028,012 |
| 35 | 304,425, 304,424 | 17 | 131,071 | 1,362,521,534 | 178,608,892 | 1,543,735,190 |
| 36 | 173,353, 173,352 | 16 | 65,535 | 621,318,441 | 78,781,904 | 701,722,069 |
| 37 | 107,817, 107,816 | 15 | 32,767 | 280,538,527 | 52,906,853 | 334,575,584 |
| 38 | 75,049, 75,048 | 15 | 32,767 | 280,538,527 | 38,122,937 | 319,300,148 |
| 39 | 42,281, 42,280 | 14 | 16,383 | 127,311,152 | 19,135,070 | 146,839,146 |
| 40 | 25,897, 25,896 | 13 | 8,191 | 57,353,155 | 12,846,965 | 70,470,164 |
| 41 | 17,705, 17,704 | 13 | 8,191 | 57,353,155 | 8,974,509 | 66,474,828 |
| 42 | 9,513, 9,512 | 12 | 4,095 | 25,603,926 | 4,117,800 | 29,807,450 |
| 43 | 5,417, 5,416 | 11 | 2,047 | 11,295,765 | 2,069,041 | 13,419,810 |
| 44 | 3,369, 3,368 | 10 | 1,023 | 4,901,301 | 1,389,136 | 6,330,081 |
| 45 | 2,345, 2,344 | 10 | 1,023 | 4,901,301 | 1,032,157 | 5,957,742 |
| 46 | 1,321, 1,320 | 9 | 511 | 2,072,679 | 510,024 | 2,599,307 |
| 47 | 809, 808 | 8 | 255 | 837,679 | 370,400 | 1,220,843 |
| 48 | 553, 552 | 8 | 255 | 837,679 | 247,198 | 1,093,801 |
| 49 | 297, 296 | 7 | 127 | 328,678 | 122,849 | 458,531 |

| tail | operations |
| --- | ---: |
| 49 repetitions above | 2,890,218,522,162 |
| classical Euclid | 715,784 |
| scale table and driver entry | 319 |
| driver exit and normalization | 2,863 |
| stage bookkeeping | 1,119 |
| **row D** | **2,890,219,242,247** |

The outer applies already execute running-twiddle passes and retain their exact 36aefd2a charges. Only the four-layer node charge is replaced. Every tail event is unchanged.

#### E.2.1 Running-twiddle node recurrence

The node keeps the three-row apply and the two-row matrix product. Let `n = 2^(j-1)` and `a = j-1`. Split `a` into a first remainder and full seven-layer passes. For a pass `(l0,k)`, charge every block its own `2^k+4` running-twiddle chain, the body `B(k)`, and `150k` setup. Subtract the group-zero twiddle-one multiplications and add three controls. The inverse uses the same conservative pass charge.

The row primitives are `lc(l)=3l+2`, `cp(l)=4l+lc(l)`, `zf(l)=2l+lc(l)`, and `ac(l,u)=(7+u)l+lc(l)`. Pointwise loops use `F(n)`, not three controls per position. The base is re-derived as `pd(6)=105,140`. The recurrence then charges both children, six top row transforms, returned matrix rows, the pointwise apply, the two-row matrix product, six inverse transforms, four CRT calls, pseudo-division, arrays, and control. Finally, `node_bf(j)=ceil(101*(pd(j)+10)/100)`.

| j | `2 pd(j-1)` | top | returns | apply | matrix | inverse | CRT | pseudo | arrays | `pd(j)` | `node_bf(j)` |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 7 | 210,280 | 24,799 | 34,128 | 6,876 | 9,168 | 30,990 | 3,336 | 2,064 | 3,588 | 325,413 | 328,678 |
| 8 | 650,826 | 46,179 | 30,552 | 13,692 | 18,256 | 51,738 | 6,664 | 4,112 | 7,172 | 829,375 | 837,679 |
| 9 | 1,658,750 | 99,235 | 70,232 | 27,324 | 36,432 | 124,122 | 13,320 | 8,208 | 14,340 | 2,052,147 | 2,072,679 |
| 10 | 4,104,294 | 191,355 | 130,936 | 54,588 | 72,784 | 226,914 | 26,632 | 16,400 | 28,676 | 4,852,763 | 4,901,301 |
| 11 | 9,705,526 | 379,303 | 257,288 | 109,116 | 145,488 | 443,622 | 53,256 | 32,784 | 57,348 | 11,183,915 | 11,295,765 |
| 12 | 22,367,830 | 763,515 | 521,080 | 218,172 | 290,896 | 901,986 | 106,504 | 65,552 | 114,692 | 25,350,411 | 25,603,926 |
| 13 | 50,700,822 | 1,549,471 | 1,072,040 | 436,284 | 581,712 | 1,871,310 | 213,000 | 131,088 | 229,380 | 56,785,291 | 57,353,155 |
| 14 | 113,570,582 | 3,157,347 | 2,221,912 | 872,508 | 1,163,344 | 3,917,850 | 425,992 | 262,160 | 458,756 | 126,050,635 | 127,311,152 |
| 15 | 252,101,270 | 6,445,927 | 4,618,760 | 1,744,956 | 2,326,608 | 8,229,414 | 851,976 | 524,304 | 917,508 | 277,760,907 | 280,538,527 |
| 16 | 555,521,814 | 14,452,989 | 11,318,992 | 3,489,852 | 4,653,136 | 21,142,248 | 1,703,944 | 1,048,592 | 1,835,012 | 615,166,763 | 621,318,441 |
| 17 | 1,230,333,526 | 28,795,009 | 22,489,984 | 6,979,644 | 9,306,192 | 41,951,604 | 3,407,880 | 2,097,168 | 3,670,020 | 1,349,031,211 | 1,362,521,534 |
| 18 | 2,698,062,422 | 58,067,973 | 45,617,200 | 13,959,228 | 18,612,304 | 85,337,088 | 6,815,752 | 4,194,320 | 7,340,036 | 2,938,006,507 | 2,967,386,583 |
| 19 | 5,876,013,014 | 117,792,649 | 93,443,296 | 27,918,396 | 37,224,528 | 175,644,300 | 13,631,496 | 8,388,624 | 14,680,068 | 6,364,736,555 | 6,428,383,931 |
| 20 | 12,729,473,110 | 239,600,397 | 192,240,016 | 55,836,732 | 74,448,976 | 363,333,912 | 27,262,984 | 16,777,232 | 29,360,132 | 13,728,333,675 | 13,865,617,022 |
| 21 | 27,456,667,350 | 487,933,585 | 396,123,712 | 111,673,404 | 148,897,872 | 752,866,212 | 54,525,960 | 33,554,448 | 58,720,260 | 29,500,962,987 | 29,795,972,627 |
| 22 | 59,001,925,974 | 994,036,245 | 816,472,816 | 223,346,748 | 297,795,664 | 1,560,239,664 | 109,051,912 | 67,108,880 | 117,440,516 | 63,187,418,603 | 63,819,292,800 |

The per-block twiddle reading is no smaller than the executed shared running chain. The one-percent allowance covers control not modeled block by block. The top-window checks remain those of the predecessor and hold for every row in the repetition table.

#### E.2.2 Embedded exact-integer script

```python
#!/usr/bin/env python3
"""Exact-integer evidence for the r6 387-register machine reprice.

This file is deliberately self-contained.  It does not import another candidate
or read a submitted integer.  The final assertions bind the printed ledger to
claim.json and proof.md.
"""
from decimal import Decimal, ROUND_CEILING, getcontext
from math import ceil


getcontext().prec = 80


def loop8(cnt: int) -> int:
    """Control for a straight-line body that handles eight positions."""
    return 1 + 3 * (cnt // 8) + 2 + 3 * (cnt % 8) + 2


def column_kernel(k: int, cnt: int, offset_zero: bool = False) -> int:
    """Kernel only; the caller adds 2*2^k+6 and the call-loop control."""
    assert 1 <= k <= 7 and cnt >= 0
    constants = {1: 5, 2: 6, 3: 10, 4: 18, 5: 34, 6: 139, 7: 269}
    slopes = {1: 11, 2: 20, 3: 52, 4: 128, 5: 304, 6: 704, 7: 1600}
    ans = constants[k] + slopes[k] * cnt + loop8(cnt)
    if offset_zero:
        ans -= ((1 << k) - 1) * cnt
        ans += 3
    return ans


def block_twiddles(k: int) -> int:
    assert 1 <= k <= 7
    if k <= 3:
        return 16
    if k == 4:
        return 24
    return (1 << k) + 8


def block_body(k: int) -> int:
    assert 1 <= k <= 7
    return 2 * (1 << k) + 3 * k * (1 << (k - 1)) + 3


def upper_pass(a: int, l0: int, k: int, inverse: bool = False) -> int:
    """Per-block upper charge used by the half-gcd proof.

    Every block is charged its own twiddle formation even though the executed
    pass shares one set per group.  Group zero still receives the exact
    twiddle-one saving, and the one-percent allowance is added at node level.
    """
    assert 1 <= k <= 7 and 0 <= l0 and l0 + k <= a
    blocks = 1 << (a - k)
    blocks_per_group = 1 << (a - l0 - k)
    # The union machine uses 56272e37's running-twiddle construction instead
    # of c7ef0551's table loads.  Per layer, 150 operations form the step and
    # chain constants.  Charging every block its own running twiddle chain is
    # the conservative reading used by the node proof.
    setup = 150 * k
    return (
        blocks * (block_body(k) + (1 << k) + 4)
        + setup
        - blocks_per_group * ((1 << k) - 1)
        + 3
    )


def pass_schedule(a: int) -> list[tuple[int, int]]:
    """First the remainder, then full seven-layer passes."""
    assert a >= 1
    first = a % 7 or 7
    out = [(0, first)]
    l0 = first
    while l0 < a:
        out.append((l0, 7))
        l0 += 7
    return out


def row_passes(a: int, inverse: bool = False) -> int:
    return sum(upper_pass(a, l0, k, inverse) for l0, k in pass_schedule(a))


def lc(length: int) -> int:
    return 3 * length + 2


def cp(length: int) -> int:
    return 4 * length + lc(length)


def zf(length: int) -> int:
    return 2 * length + lc(length)


def ac(length: int, extra: int) -> int:
    return (7 + extra) * length + lc(length)


def pw(n: int, row: int) -> int:
    return loop8(n) + (7 if row == 0 else 10) * n


def base_case() -> int:
    total = 90
    for s in range(0, 62, 2):
        length = 2 * (62 - s) + 1
        total += (
            76
            + 13 * length
            + 9 * (length - 2)
            + lc(length)
            + 2 * (13 * (s + 2) + 9 * (s + 3) + lc(s + 3))
            + 8
        )
    s = 62
    length = 1
    total += 25 + 13 * length + lc(length) + 2 * (13 * (s + 2) + lc(s + 2)) + 4
    return total


PD: dict[int, int] = {6: base_case()}
COMPONENTS: dict[int, dict[str, int]] = {}


def pd(j: int) -> int:
    if j in PD:
        return PD[j]
    n = 1 << (j - 1)
    a = j - 1
    fwd = row_passes(a)
    inv = row_passes(a, inverse=True)

    def row(length: int, row_index: int) -> int:
        return (
            cp(min(length, n))
            + zf(max(0, n - length))
            + ac(max(0, length - n), 1 if row_index == 2 else 0)
            + 2 * n * (1 if row_index > 0 else 0)
            + fwd
        )

    top = sum(row(1 << (j + 1), r) + row((1 << (j + 1)) - 1, r) for r in range(3))
    returned_rows = (0, 1) if j == 7 else (1,)
    returns = 8 * sum(row(n, r) for r in returned_rows)
    apply = 6 * (pw(n, 0) + pw(n, 2))
    matrix = 8 * (pw(n, 0) + pw(n, 1))
    inverse = 6 * sum(inv + (1 + (r > 0)) * n for r in range(3))
    crt = 4 * (10 * n + lc(n))
    pseudo = 30 + 13 * ((1 << j) - 1) + lc((1 << j) - 1)
    arrays = 2 * (25 * n + lc(n))
    children = 2 * pd(j - 1)
    total = 184 + children + top + returns + apply + matrix + inverse + crt + pseudo + arrays
    COMPONENTS[j] = {
        "children": children,
        "top": top,
        "returns": returns,
        "apply": apply,
        "matrix": matrix,
        "inverse": inverse,
        "crt": crt,
        "pseudo": pseudo,
        "arrays": arrays,
        "pd": total,
    }
    PD[j] = total
    return total


def node_bf(j: int) -> int:
    return ceil(101 * (pd(j) + 10) / 100)


# The predecessor's four-layer conservative node is reproduced here so the
# stage-D delta is computed rather than imported as a node-column literal.
def old_pass_schedule(a: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    level = 0
    while a - level >= 4:
        out.append((level, 4))
        level += 4
    if a - level:
        out.append((level, a - level))
    return out


def old_pass(a: int, _level: int, width: int) -> int:
    blocks = 1 << (a - width)
    return (
        150 * width
        + blocks * ((1 << width) + 4)
        + blocks * (2 * (1 << width) + 3 * width * (1 << (width - 1)) + 5)
    )


def old_row_passes(a: int) -> int:
    return sum(old_pass(a, level, width) for level, width in old_pass_schedule(a))


OLD_PD: dict[int, int] = {6: base_case()}


def old_pd(j: int) -> int:
    if j in OLD_PD:
        return OLD_PD[j]
    n = 1 << (j - 1)
    a = j - 1
    passes = old_row_passes(a)

    def row(length: int, row_index: int) -> int:
        return (
            cp(min(length, n))
            + zf(max(0, n - length))
            + ac(max(0, length - n), 1 if row_index == 2 else 0)
            + 2 * n * (1 if row_index > 0 else 0)
            + passes
        )

    top = sum(row(1 << (j + 1), r) + row((1 << (j + 1)) - 1, r) for r in range(3))
    returned_rows = (0, 1) if j == 7 else (1,)
    returns = 8 * sum(row(n, r) for r in returned_rows)
    apply = 6 * ((3 * (n // 8) + 3 + 7 * n) + (3 * (n // 8) + 3 + 10 * n))
    matrix = 8 * ((3 * (n // 8) + 3 + 7 * n) + (3 * (n // 8) + 3 + 10 * n))
    inverse = 6 * sum(passes + (1 + (r > 0)) * n for r in range(3))
    crt = 4 * (10 * n + lc(n))
    pseudo = 30 + 13 * ((1 << j) - 1) + lc((1 << j) - 1)
    arrays = 2 * (25 * n + lc(n))
    OLD_PD[j] = (
        184
        + 2 * old_pd(j - 1)
        + top
        + returns
        + apply
        + matrix
        + inverse
        + crt
        + pseudo
        + arrays
    )
    return OLD_PD[j]


def old_node_bf(j: int) -> int:
    return ceil(101 * (old_pd(j) + 10) / 100)


def ceil_decimal(value: Decimal, places: int) -> Decimal:
    return value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_CEILING)


# Round-local geometry.  The predecessor's E.2 walk contains these counts; the
# map is also recoverable from m by the outer-driver rule in proof section 4.4.
NODE_COUNTS = {
    7: 1,
    8: 2,
    9: 1,
    10: 2,
    11: 1,
    12: 1,
    13: 2,
    14: 1,
    15: 2,
    16: 1,
    17: 2,
    18: 2,
    19: 1,
    20: 1,
    21: 1,
    22: 28,
}

CURRENT_STAGE_C = 6_680_271_984_462
CURRENT_STAGE_D = 3_083_866_028_821
CURRENT_N_MAX = 9_952_094_729_988
CURRENT_MEMORY_BYTES = 15_645_143_976
CURRENT_SCORE = Decimal("48.62529")

# The truncated transforms retain their proven split 4 | 4,5,5,5 | 4.  The
# four-block body saves two controls in every middle and bottom block.  O2 uses
# the two saved controls for its two extra array pointers; a one-bit step has
# one additional point-pointer update.  A fused Graeffe bottom block has one
# extra pointer and therefore saves one.  These are the event counts of 4.3T,
# not a fitted delta.
TRUNCATED_POINTS = 122_159_104
TRUNCATED_WIDTHS = (4, 5, 5, 5)
MIDDLE_SAVING = 2 * sum(TRUNCATED_POINTS // (1 << width) for width in TRUNCATED_WIDTHS)
BOTTOM_BLOCKS = TRUNCATED_POINTS // 16
GRAEFFE_STEP_SAVING = 3 * MIDDLE_SAVING + BOTTOM_BLOCKS
BIT0_STEP_SAVING = 4 * MIDDLE_SAVING + 2 * BOTTOM_BLOCKS
BIT1_STEP_SAVING = 4 * MIDDLE_SAVING + BOTTOM_BLOCKS
TRUNCATED_TRANSFORM_SAVING = MIDDLE_SAVING + 2 * BOTTOM_BLOCKS
STAGE_C_TWIDDLE_TABLE = 8 * (1 << 23)
STAGE_C_SAVING = (
    STAGE_C_TWIDDLE_TABLE
    + 24 * GRAEFFE_STEP_SAVING
    + 160 * BIT0_STEP_SAVING
    + 45 * BIT1_STEP_SAVING
    + 9 * TRUNCATED_TRANSFORM_SAVING
)
STAGE_C = CURRENT_STAGE_C

SOURCE_NODES = {
    7: 347_459,
    8: 903_917,
    9: 2_201_441,
    10: 5_273_367,
    11: 12_225_379,
    12: 27_789_787,
    13: 62_332_587,
    14: 140_035_737,
    15: 310_442_581,
    16: 682_038_701,
    17: 1_488_363_581,
    18: 3_255_978_923,
    19: 7_065_482_855,
    20: 15_245_615_039,
    21: 32_753_288_783,
    22: 70_522_726_845,
}
OLD_NODE_SUM = sum(SOURCE_NODES[j] * count for j, count in NODE_COUNTS.items())
NEW_NODE_SUM = sum(node_bf(j) * count for j, count in NODE_COUNTS.items())
STAGE_D_TWIDDLE_TABLE = 0
STAGE_D = CURRENT_STAGE_D - OLD_NODE_SUM + NEW_NODE_SUM

N_MAX = CURRENT_N_MAX + (STAGE_C - CURRENT_STAGE_C) + (STAGE_D - CURRENT_STAGE_D)

CODE_DELTA = 907_520 - 39_228
REGISTER_BYTES = 387 * 32 - 105 * 32
OFFLINE_WORKING_BYTES = 0
MEMORY_BYTES = CURRENT_MEMORY_BYTES + CODE_DELTA + REGISTER_BYTES + OFFLINE_WORKING_BYTES

RAW_TIME = (Decimal(N_MAX).ln() - Decimal(342).ln()) / Decimal(2).ln()
TIME_CLAIM = ceil_decimal(RAW_TIME, 5)
RAW_MEMORY = Decimal(MEMORY_BYTES).ln() / Decimal(2).ln()
MEMORY_CLAIM = ceil_decimal(RAW_MEMORY, 5)
SCORE = TIME_CLAIM + MEMORY_CLAIM - Decimal(20)
GAIN = CURRENT_SCORE - SCORE


assert loop8(0) == 5
assert loop8(8) == 8
assert base_case() == 105_140
assert column_kernel(6, 1) == 139 + 704 + loop8(1)
assert column_kernel(7, 1) == 269 + 1600 + loop8(1)
assert sum(NODE_COUNTS.values()) == 49

for level in range(7, 23):
    pd(level)

def main() -> None:
    print("schedule", {a: pass_schedule(a) for a in range(6, 22)})
    print("node_bf", {j: node_bf(j) for j in range(7, 23)})
    print("old_node_bf", {j: old_node_bf(j) for j in range(7, 23)})
    print("truncated_savings", {
        "middle": MIDDLE_SAVING,
        "bottom_blocks": BOTTOM_BLOCKS,
        "graeffe": GRAEFFE_STEP_SAVING,
        "bit0": BIT0_STEP_SAVING,
        "bit1": BIT1_STEP_SAVING,
        "transform": TRUNCATED_TRANSFORM_SAVING,
        "table": STAGE_C_TWIDDLE_TABLE,
        "total": STAGE_C_SAVING,
    })
    print("stage_c", STAGE_C)
    print("node_sums", OLD_NODE_SUM, NEW_NODE_SUM)
    print("stage_d", STAGE_D, "table_removed", STAGE_D_TWIDDLE_TABLE)
    print("n_max", N_MAX)
    print("memory_bytes", MEMORY_BYTES)
    print("raw_time", RAW_TIME, "time_claim", TIME_CLAIM)
    print("raw_memory", RAW_MEMORY, "memory_claim", MEMORY_CLAIM)
    print("score", SCORE, "gain", GAIN)


if __name__ == "__main__":
    main()
```

Run the script only as `python3 -B ledger_v2.py` from this candidate tree.

### E.3 Memory events

Section 7 lists every event that can set the retained high-water mark. The seven-layer node uses the same arrays and bump arena as the four-layer node. All allocator events therefore keep the same order and size, and the pool mark remains `15,637,275,264` bytes. The fixed regions then produce the exact footprint `15,646,021,292` bytes.
