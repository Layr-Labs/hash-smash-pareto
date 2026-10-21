# Orchard Poseidon, r = 5: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, a Graeffe prefix, value-domain powering on truncated point sets, inversion-free half-gcd, one centre

## 1. Claim

Target: `poseidon-orchard-r5-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, five partial rounds 4, 5, 6, 7 and 8, full rounds 60-63, state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is an algorithm (sections 2-4) with an operation count that bounds every run (sections 6-7) and a success probability derived from two score-critical premises: `H-ONE` (section 9.1), a statement about the fraction of centres at which the fixed digest polynomial has between 1 and 16 usable roots, and `H-NORMAL` (section 9.5), a statement about the normality of the remainder sequence that enters only the success probability. Section 9.2 derives the success probability from them.

* The algorithm: draw a centre `c` from two fresh random words, `c = (w1 2^256 + w2) mod p` (within statistical distance `p/2^512` of uniform on `F_p`, 4.1.1), build the odd part `g_c` of the line polynomial by evaluation and one inverse transform, replace `g_c` by its 22-fold Graeffe transform `g = g_c^(22)` (monic, degree `m`, its roots the `2^22`-th powers of those of `g_c`; section 4.3G), compute `R = S^((p-1)/2^23) mod g` in the value domain by Montgomery powering on two truncated point sets `O1`, `O2` of `n' = 1491 * 2^14 = 24,428,544` points (1491 of the 2048 depth-11 nodes of the subgroup of order `2^25` and of its coset; the method of bradcush `b30de9bf`/`a41aecdd`, there 15 of 16 nodes, section 4.3T), take `G = gcd(g, R - 1)` by the inversion-free half-gcd of bradcush `b30de9bf`/`4bcabff8` (matrices in coefficient form, node products on three rows, outer step `k <= 2^21 - 1` as in weijiekoh `a78f526e`, section 4.4), charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, and if `G` has degree between 1 and `DMAX = 16` isolate a root `y` of `G` in at most `Z = 64` rounds, find `s` with `s^(2^23) = y` and `F(c + s) = F(c - s)` among at most `2^22` candidates (4.1.3), map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39009`: a lower bound for the probability, over the algorithm's fresh random words, that the centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1), `delta = 0.003` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `eps_iso <= 2.371e-15`, `eps_coin <= 65 p / 2^512 <= 1.404e-76`, `eps_g <= 2^22 n' (D - 1) / p < 2^-181` (the centre makes `g` vanish at a point of `O1`, 4.3G) (sections 4.1.1, 4.3T, 9.2). The value the formula gives is `0.390099999999997628` (at or above the organizer floor 0.39); the claim is that value floored at five decimals.
* `time_log2 = 32.67097` in target-compression units (`C(5) = 321` primitive operations per unit): the operation count that bounds every run, derived in section 6 as `T_fixed + K * T_trial + T_off` with `K = 1`, stage C a Graeffe prefix of 22 steps (4.3G) and value-domain powering on truncated point sets (4.3T), stage D the inversion-free half-gcd charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (4.4, 6.3; the time bound holds for every sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work), stage E at its cap of `Z` rounds at degree `DMAX`, and the scan of stage F at its cap of `2^22` candidates (4.1.3). `N_max = 2,195,048,645,175` operations, `log2(N_max / 321) = 32.67096056366712843...`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is counted exactly, `T_off = 137,149` operations, and charged at its declared cap of 1,000,000 operations; that cap is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 31.54627` (`3,135,961,964` bytes, section 7). Under the pareto convention `time_log2 + max(0, memory_log2_bytes - 20)` this gives `32.67097 + 11.54627 = 44.21724`; the time-only scalar is `32.67097`, and the memory is reviewed separately.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; every random field element is drawn from two fresh words, at most `65` field elements (`130` words) per run (section 4.1.1), and a draw costs 63 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^11`, then the roots of its odd part about a centre, found, after a Graeffe prefix (Dandelin-Graeffe root squaring), with a gcd against `S^((p-1)/2^23) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Against our current entry `3237ea8c` at `44.25102`, this package ports the union of the running-twiddle construction of `56272e37` and the 387-register, seven-layer, unrolled-loop, twiddle-one construction of `c7ef0551`. Rows C and D become `1,337,973,395,390` and `834,209,997,260`. `N_max` is `2,195,048,645,175` and the normalized cost is `44.21724`, a gain of `0.03378`. H-ONE, H-NORMAL, the success bound, and the experiments are unchanged.
* This package is the base entry `98f2ba70` with one change to its charge: the half-gcd node keeps the base's two-row product, and each row transform of the node is evaluated in the block form of `27fbfbe7` 4.2; the node charge `node_bf(j)` is derived in Appendix E.2.1 as a per-block upper bound with a declared one per cent allowance, and no integer is taken from another entry's node column. Row D `877,652,806,744` (was `940,293,795,311`); every other row, the memory and the success bound are unchanged. The top-window bound against the shortest operands of this round is in E.2.1. Normalized cost `44.25102` (was `44.29068`).
* Against our r = 5 entry `e0ef7608` (time + memory penalty 44.35138), one change to its algorithm: the product step `M = M1 [[Q, 1], [b^2, 0]] M2` of each half-gcd node runs on the two rows `Y - 1`, `Y + 1` (`2n` points) in place of three; its entries have degree at most `2n - 1` on the normal sequence (4.4). Row D `940,293,795,311` (was `1,039,563,293,257`); every other row, the memory and the success bound are unchanged. Our entry `e0ef7608` against our r = 5 entry `ebbb87b0` (time + memory penalty 44.37412), one change to its algorithm: a Graeffe prefix (4.3G). Stage C first applies 22 Graeffe steps `g(Y) <- E(Y)^2 - Y O(Y)^2` on `O1` (`4,031,113,422` operations each) and then raises `S` to `(p-1)/2^23` (209 squaring steps in place of 231); the gcd keeps exactly the `2^22`-th powers of the usable roots (`1 <= deg G <= k(c)`), and stage F finds the root of `g_c` above the isolated one by a scan of at most `2^22` candidates on the line map (4.1.3). Row C `1,346,966,135,742` (was `1,387,466,466,885`), row F `2,232,498,018` (was `47,012`); memory unchanged. `H-NORMAL` is stated for the pair of the transformed polynomial and its organizer-run tests compute that pair (9.5, 10.5.1); `H-ONE`, every other charge and the other experiments are unchanged.
* Prior entries: `ebbb87b0` (44.37412) improved our r = 5 entry `d2edbd3d` (44.64067) by charging the loads and stores of the pass-block data words one operation each and running layers 1-12 of the truncated transforms class-batch by class-batch in a `71,296`-word buffer; `d2edbd3d` improved our r = 5 entry `647649ab` (time + memory penalty 44.83898: the one-centre algorithm of our r = 6 entry `c318f442` with bradcush's truncated-point-set stage C, entries `b30de9bf`, `a41aecdd`, and the memory schedule of 0xshikhar's entries `52120fad` and `716c3818`) by three changes: (i) stage D is the inversion-free half-gcd of bradcush (`b30de9bf`, whose source revises `4bcabff8`; read as text only), charged in this cost model with the outer-step cap `KMAX = 2^21 - 1` (4.4); (ii) the kernel charges of stage C (4.3T): the passes split top 3 | middle 5, 4, 4, 5 | bottom 4 on the 64-register machine stated as a restriction in claim.json (4.2), the form of our r = 3 entry `ef123c2b`; the bottom twiddles from the two-level table with register constants, running supergroup twiddles in the middle passes, the pruned top pass, the recovery with the path value in a register, the scaling fused into the adjacent pass, and the batch-inversion chunk in the batch buffer; (iii) each line evaluation of stage B charged at the operations it executes, `155 + 21 r = 260`, in place of `C(5) = 321` (section 3). The premises, the coins, stages A and E-G and the organizer-run tests are those of `647649ab` (`H-ONE` at `q = 0.3931`, `H-NORMAL` at `delta = 0.003` with the split of cryptogakusei's entry `4888e783`, the ABORT discipline of bradcush's `e6dcb600` and the test form of gta6rp's entry `bef31fdd`). The memory is the allocator high-water mark of the one trial (section 7).
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1), a statement about the fraction of good centres, and `H-NORMAL` (score-critical for the success probability only, section 9.5), bradcush's premise on the normality of the remainder sequence stated with the allowance `delta = 0.003` and supported by organizer-run tests. Both are statements about probability. The costs are the declared cost model of this entry, not heuristics: the charging rules of section 4.2, the machine (64 registers of 256 bits and constants as immediates; every load, store and spill counted), stated as a restriction in claim.json as the accepted entries `89b451ff` and `fb176310` state theirs, not as a heuristic, the inversion-free half-gcd of stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (Appendix E). Everything else is proved or counted here.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`. `(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`. The algorithm uses the line `j = 0`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant `M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS, nonzero on the deployed constants, checked). Let `(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, `d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i` (the supports are disjoint). After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8 (partial), 60, 61, 62, 63 (full) put eleven S-box layers on top of an affine map, and the digest is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^11 = D = 48,828,125`. The leading coefficient is obtained by propagating leading coefficients through the eleven layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used: `f_D(0) = 0x3d8a63413498ea10d01ec5a3bc7106382d152c057486fdb7dfe795da6ea4e687` (computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau` against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`), hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 24,414,062`, `g_c` has degree exactly `m` and leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`, `W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The useful roots are the roots in `F_p` with `S^((p-1)/2) = 1`: they are the roots of `gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p`; `S = 0` is not a root of `S^((p-1)/2) - 1`). This gcd divides the squarefree `S^((p-1)/2) - 1`, so it is a product of `k(c)` distinct linear factors over `F_p` (9.1); stage D computes instead the gcd of 4.3G, whose roots are their `2^22`-th powers.

Construction of `g_c` by evaluation. `H = 25,165,824 = 3 * 2^23` divides `p - 1` (`p - 1 = 2^32 * 3 * q`) and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`; one inverse transform of size `H` returns the coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). Each of the `2H = 50,331,648` evaluations of `F` is charged at the operations it executes (the line evaluation `tail_eval`): the affine start `alpha + beta W` (3 multiplications, 3 additions: 6), round 2 (three S-boxes `x^5` of 3 operations each and the MDS, 9 multiplications and 6 additions: 24; its constants are in `alpha`), round 3 (3 constant additions, 9, 15: 27), the five partial rounds (3 + 3 + 15 = 21 each), rounds 60-62 (27 each) and round 63 (3 + 9 and row 0 of the MDS, 3 multiplications and 2 additions: 17), `155 + 21 r = 260` operations at `r = 5`; rounds 0 and 1 are not executed (section 2). The loop work (two point additions, one subtraction, one multiplication by `1/(2 zeta^i)`, the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, the store with its address, the loop control and the bit-reversed index) is charged on top (stage B, section 6), with the twiddle table of the transform, built by stage B (4.2).

## 4. The algorithm (one centre, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   constants (once; no twiddle table: each stage builds the table of its own transforms, 4.2)
setup:  the line (line_setup) (once)
for t = 1, ..., K (K = 1):            [the test t <= K is made at the start of the trial; no exit except success]
  A  c := (w1 * 2^256 + w2) mod p from two fresh random words w1, w2 (4.1.1)
  B  g := monic g_c, by section 3 (50,331,648 evaluations + one inverse NTT of size 25,165,824 + the nonzero-leading-coefficient test + normalisation)
  C  g := g^(22): 22 Graeffe steps on O1 (section 4.3G); R := S^((p-1)/2^23) mod g, in the value domain on the truncated point sets O1, O2 of n' = 24,428,544 points (section 4.3T): 209 squaring steps, 45 of them also multiplying by S
  D  G := gcd(g, R - 1) (monic): the inversion-free half-gcd (section 4.4), charged for the normal remainder sequence with the quotient and return tests; on any other case ABORT (6.3)
  E  if deg G = 0 or deg G > DMAX: trial ends. Otherwise isolate a root y of G (4.1.2); if none within Z = 64 rounds: trial ends.
  F  u := a 2^23-th root of y (23 Tonelli-Shanks square roots, 2-adicity 32); for j = 0, ..., 2^22 - 1: s := u mu^j, W1 = c + s, W2 = c - s, until F(W1) = F(W2) (4.1.3); tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (300 operations each) are equal and the pairs differ -> output; otherwise the trial ends
```

4.1.1 Coins (ruling `04c0dd43`, finding F-EVAL-001). The only randomness is the cost-model random-word primitive. Every random field element of the algorithm (the centre `c` of stage A and each shift of stage E) is drawn from two fresh 256-bit words `w1, w2`: each is reduced mod `p` by three conditional subtractions (exact, `2^256 < 4p`), and `x = (w1 mod p) * (2^256 mod p) + (w2 mod p)` in `F_p`, i.e. `x = (w1 2^256 + w2) mod p` with `w1 2^256 + w2` uniform on `[0, 2^512)`. There is no rejection and no retry. A draw is 63 operations: per word 1 random-word operation, 1 load, 1 store, 3 control, the reduction 9 and its loop control 11 (26 per word, 52), two Montgomery conversions 2, the load of the constant `2^256 mod p` 1, one multiplication 1, one addition 1, entry 2, the two addresses 4. At most `1 + Z = 65` draws (`130` words) per run. With `2^512 = Q p + r`, each residue has `Q` or `Q + 1` preimages, so one draw is within statistical distance `r (p - r) / (p 2^512) <= p / 2^512 = 2^-258.0` of uniform on `F_p`; the 65 draws are independent, so the joint distribution of all the coins of a run is within `eps_coin = 65 p / 2^512 <= 1.404e-76` of the distribution with every draw exactly uniform (total variation is subadditive over independent components).

4.1.2 Stage E: isolating a root of `G`. With `1 <= deg G <= DMAX = 16`, a Cantor-Zassenhaus split with random shifts isolates one linear factor in at most `Z = 64` rounds at degree `<= 16`; `eps_iso <= 2.371e-15` bounds the probability that 64 rounds fail to isolate a root when `deg G >= 1` (section 9.4).

4.1.3 Stage F: the root of `g_c` above `y`. By 4.3G, `y = S^(2^22)` for a usable root `S` of `g_c`, and the solutions of `S'^(2^22) = y` are `u^2 mu^(2j)`, `j < 2^22`, where `u^(2^23) = y` and `mu` is a fixed primitive `2^23`-th root of unity (`2^23 | p - 1`; a constant of the offline derivation, 6.2). `u` comes from 23 successive Tonelli-Shanks square roots: `y` is a `2^23`-th power, and if `x` is a `2^k`-th power with `1 <= k <= 23`, both square roots of `x` are `2^(k-1)`-th powers (`-1` is a `2^(k-1)`-th power, `2^k | p - 1`). The scan takes `s = u mu^j` for `j = 0, 1, ..., 2^22 - 1` and stops at the first `j` with `F(c + s) = F(c - s)` (two line evaluations of section 3). For `S' = s^2` a root of `g_c` this holds, because `F(c + s) - F(c - s) = 2 s g_c(s^2)`, so the scan stops at the latest at the `j` of `S`; any stop has `s != 0` (`y != 0`) and `F(c + s) = F(c - s)`, a collision by 2.4. Charge per candidate: `s <- s mu` 1, `c + s` and `c - s` 2, two line evaluations `2 * 260`, their calls 4, the comparison and branch 2, the loop control 3: `532`; at most `2^22` candidates, `2,231,369,728`, and the loop exit 2. The 23 square roots are charged `47,012` each (the whole row F of the algorithm without the prefix, a square root and the back-map), `1,081,276`, and the back-map `47,012`: row F = `2,232,498,018`.

### 4.2 Machine model and charging rules (`C(5) = 321`)

Every field operation, load, store, control operation, and random word costs one primitive operation. One target-compression unit is `C(r) = 216 + 21r = 321` operations.

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

The truncated transforms of stage C keep their proved split `3 | 5,4,4,5 | 4`. Four blocks run per straight-line loop body. Appendix E.1 derives the middle and bottom deltas, including every extra array-pointer update. The Newton and quotient products also use running twiddles. Their predecessor component totals remain charged as conservative caps, so the package does not rely on another entry's product total or undercharge those paths. Stage D treats its outer applies the same way: every pass executes with running twiddles, while E.2 retains the predecessor's larger apply charge. The node recurrence itself is re-derived.

The allocator remains one preallocated arena. The pool, slab, allocation, free, and walk rules are unchanged. Stage B keeps its transform table. The two-level root tables of the truncated transforms remain. Stages C and D build no product twiddle table. The algorithm uses one thread and no dispatch.

### 4.3G The Graeffe prefix

Definition. For `h` monic of even degree `m` write `h(X) = E(X^2) + X O(X^2)`; its Graeffe transform is `h~(Y) = E(Y)^2 - Y O(Y)^2`, so `h~(X^2) = h(X) h(-X)` and `h~` is monic of degree `m` with roots the squares of the roots of `h` (with multiplicity). Stage C first replaces `g = g_c` by `g^(22)`, 22 Graeffe steps, then computes `R = S^e mod g^(22)`, `e = (p-1)/2^23` (2-adicity 32), and stage D takes `G = gcd(g^(22), R - 1)`.

Lemma. `G` is the product of `(Y - y)` over the distinct values `y = S^(2^22)`, `S` a usable root of `g_c` (a nonzero square in `F_p` with `g_c(S) = 0`, section 3). Proof: `g^(22)(Y) = prod_i (Y - S_i^(2^22))` over the roots `S_i` of `g_c` in an algebraic closure; `Y^e - 1` is squarefree and its roots are the `2^23`-th powers of `F_p^*`. If `S_i^(2^22) = u^(2^23)` with `u` in `F_p^*`, then `S_i = u^2 zeta` with `zeta^(2^22) = 1`, so `zeta` is in `F_p` and `zeta = xi^2` with `xi^(2^23) = 1` (`2^23 | p - 1`), and `S_i = (u xi)^2` is a nonzero square of `F_p`; conversely `S = v^2` gives `S^(2^22) = v^(2^23)`. So `deg G` is the number of distinct `2^22`-th powers of the usable roots: `1 <= deg G <= k(c)` when `k(c) >= 1`, and `deg G = 0` when `k(c) = 0`; the event `E_c` of 9.2 gives `1 <= deg G <= DMAX`.

Execution (on the point set `O1` of 4.3T). One step: `E` (`m/2 + 1` coefficients) and `O` (`m/2`) are read from `g` at stride 2 by the top passes of two truncated forwards, which load only the input blocks below the length (3 or 2 of the 8 per offset, two offset ranges per batch; no zero-fill); the fused bottom pass forms `G = (E^2 - y O^2)/N` at each point `y` of `O1` between the forward and the inverse bottom layers (`y` is the last-layer twiddle of its butterfly, in a register: two squarings, two multiplications, one subtraction, 5 per point); one truncated inverse stores the new coefficients into the array of `g` (those above `m` come out zero). `E` and `O` on `O1` use the arrays of `A` on `O2` and of `A` on `O1` before stage C fills them, with a batch buffer of `71,296` words of their own; no array is added and the high-water mark of section 7 is unchanged. One step is `4,002,104,526` operations (Appendix E.1), 22 steps; stage C then runs 209 squaring steps in place of 231 (the exponent loses 22 low zero bits). A step saves one squaring step (`5,872,037,596`) for `4,031,113,422` and doubles the scan of 4.1.3 (`2^s * 532`); `s = 22` minimises the total.

Every map is exact; no premise is added to the time or the memory. The zero test of `k1` (4.3T) now concerns `g^(22)`: `g^(22)(y) = 0` for `y` in `O1` only if `g_c(x) = 0` for one of the `2^22` values `x` with `x^(2^22) = y` (in `F_p` or an extension); for each such `x`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g^(22) vanishes on O1) <= 2^22 n' (D - 1) / p = eps_g < 2^-181`.

### 4.3T Stage C in the value domain on truncated point sets (the method of bradcush `b30de9bf`/`a41aecdd`, 1491 of 2048 nodes)

Point sets. `N = 2^25` divides `p - 1` (2-adicity 32). Let `psi` have order `2^26`, `H_N = <psi^2>` and `Y = X^(2^14)`. `H_N` is the union of the 2048 depth-11 nodes `{x : x^(2^14) = r_j}`, `r_j` the 2048-th roots of unity in transform (bit-reversed) order; `O1` is the union of the first 1491 nodes, `n' = 1491 * 2^14 = 24,428,544 >= m + 1 = 24,414,063` points, and `O2` the same 1491 nodes of the coset `psi H_N` (`x^(2^14) = r'_j`, `r'_j^2048 = -1`), disjoint from `O1`. `P1 = prod_{j<1491} (Y - r_j)` has degree `n'`, vanishes on `O1` and is the nonzero constant `P1(r'_j)` on node `j` of `O2`; `delta_j = 1/P1(r'_j)` (1491 table constants).

Truncated transforms (bradcush `b30de9bf` 4.3, generalized as the truncated Fourier transform of van der Hoeven, ISSAC 2004). A polynomial of degree `< n'` is `sum_{k<2048} P_k Y^k` with `deg P_k < 2^14` and `P_k = 0` for `k >= 1491`; its values on the 1491 nodes determine it and are determined by it (the CRT for the 1491 coprime moduli `Y - r_j`, whose product `P1` has degree `n'`). The forward transform runs the top 3 layers on all `N/8` offsets (no truncation saving is charged), the middle layers only on the blocks above present nodes, and the bottom 4 layers on the `n'` points. The inverse runs the same layers in reverse, scales each 16-point block of its bottom pass by `diag(1, c^-1 J)` (`c = y^16` of the block, `V^T V = 16 diag(1, cJ)`; 15 multiplications and the load of `c^-1`, 17 operations per block), and recovers the residues of the dropped part `[1491, 2048)`, the maximal subtrees `{1491}`, `{1492..1495}`, `{1496..1503}`, `{1504..1535}`, `{1536..2047}` (depths 11, 9, 8, 6, 2), from the known zero chunks `P_k = 0` along their paths to the root, as bradcush recovers the one dropped leaf; with the value of the path held in a register this is charged 8 operations (3 multiplications, 3 additions, the load of the known value) per point of a dropped subtree per layer of its path and one store (2) per point. Layers 1-12 (the top pass, the first two middle passes and the recoveries) act on each class of the `4096` positions with equal low 13 bits separately (`2982` in `O1`, `1114` above `n'`: the dropped nodes and the lane-5 tail), so they run class-batch by class-batch, `128` batches of `64` classes, the `1114` positions above `n'` of each class of the batch held in one batch buffer of `71,296` words (one transform runs at a time) and discarded after the batch; the passes below layer 12 touch only the `n'` positions. Charged once per batch: the groups, the pass overhead and the batch loop of the two batched middle passes (radix 32: `8` groups, each with `16` inner loops of 5, one per contiguous range of the batch offsets; radix 16: `256` groups), the top-pass overhead with its `512` inner loops (`60 + 20 + 512 * 5`), the path constants of each recovery (`256`), and before the top of each truncated forward the zero-fill of the `5,760` coefficient positions of lane 5 above `n'` (a store, 2, each and the loop). The passes are fused as in `b30de9bf` 4.5 under the predecessor's 64-word layout, whose larger spill charge this package retains as a conservative cap; the 387-word machine executes the same 25-layer split 3 | 5, 4, 4, 5 | 4 (`TR_CFG`, the cheapest split under that register file): a bottom pass (16-point blocks: forward layers, the pointwise map, inverse layers; one set of 15 twiddles for both directions, 19 operations per block: two loads from the two-level table, one multiplication, three squarings, eleven multiplications by register constants), four middle passes of radix 32, 16, 16, 32 (a running supergroup factor, 1 multiplication per group, and the group twiddles formed from it and held in registers: radix 16, 16 loads and 16 stores at one operation each, 32 butterflies and 5 control, 133 per block, 15 twiddles and control, 20 per group; radix 32, 32 loads and 32 stores at one operation each, 80 butterflies, the loads of the 3 spilled twiddles and 5 control, 315 per block, 31 twiddles, the stores of the 3 spilled ones and control, 42 per group), and a pruned top pass that fuses the inverse top of one set with the forward top of the other: only the `b = 6` depth-3 subtrees that hold points of the 1491 nodes are formed or read (the butterflies of the 8-point top block counted on the needed and nonzero lanes, `_top_counts`), and the coset twiddle is applied on those `b` blocks. The applies of stage D on `n'` points use the same transforms.

Montgomery powering (`b30de9bf` 4.5). For residues of degree `< n'`, `Mont(A, B) = (A B + u g)/P1` with `u = -A B / g mod P1` (`deg u < n'`); the division by `P1` is exact, `Mont(A, B) = A B / P1 mod g`, and `deg Mont(A, A) <= n' - 2`, so `X Mont(A, A)` has degree `< n'`. A residue `A` (representing `S^e P1`) is held by its values on `O1` and on `O2`, each up to a tracked scalar. One step: `U = A^2 k1` on `O1` (`k1 = -1/(N^3 g)` there; `u` is determined by its values on `O1`); `U` to `O2` (truncated inverse on `O1`, truncated forward on `O2`); `B2 = (A2^2 + U g) delta_j` on node `j` of `O2`, which is `Mont(A, A)` up to the tracked scalar because `P1 = 1/delta_j` there, times the point `x` when the exponent bit is 1; `B2` to `O1` (truncated inverse on `O2`, truncated forward on `O1`). No `1/N` is executed inside the steps (the scalars are tracked, 2 operations per step). Per point and step: on `O1` `sqr, LD k1, mul` (4); on `O2` `LD A2, sqr, LD g, mul, add`, the multiplication by `delta_j`, `ST` (10) and the load of `delta_j` per block (2); 3 more for a 1-bit (the load of the point and a multiplication).

Entry and exit. `g` (coefficients after the Graeffe prefix of 4.3G, its slots above `m` zero) goes to `O1` and `O2` (a truncated forward each; every scaling of this section, `1/N` and the coset twist, is a running product fused into the adjacent pass, 2 operations per point). The start residue is `A0 = X^v P1 mod g`, `v = 2^22 = 4,194,304` (VSHIFT = 2): `q = floor(X^v P1 / g)` has `ell = v + n' - m + 1 = 4,208,787` coefficients and is formed from the Newton reciprocal of the reversed `g` and one product (transforms of up to `3*2^22` points, with running twiddle factors and no stage product table); on node `j` of `O2`, `x^v P1(x) = r'_j^256 P1(r'_j)` is a constant, so `A0 = x^v P1 - q g` there is one truncated forward of `q` and one pointwise pass (8 per point); then `A0` goes to `O1`. `k1` is formed by chunked batch inversion on `O1` (chunks of `2^16` points: prefix products, one inversion, two multiplications per point; the `2^16` prefixes are kept in the batch buffer, which no transform uses at that time); each chunk product is tested for zero before its inversion (2 per chunk), and a zero ends the trial: for fixed `x != 0`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g vanishes on O1) <= eps_g < 2^-181` for the transformed `g` (4.3G, 9.2). The exit is one step with multiplier 1 (`Mont(A, 1)`) and two truncated inverses with their scaling, which return `kappa R` (`kappa` the tracked scalar) and `g` in coefficient form; the gcd is scale-invariant, so stage D receives `kappa R - kappa`. There are `209` squaring steps (the exponent `(p-1)/2^23`, 4.3G), `45` of them also multiplying by `S`.

Exactness and memory. Every map above is exact (Montgomery products of polynomials of degree `< n'`, held bijectively by their values on 1491 nodes); no premise is added to stage C. The live set of the stage is four arrays of `n'` words (`g` on `O2`, `A` on `O2`, `A` on `O1`, `k1` on `O1`), the batch buffer of `71,296` words, the tables (`1,521 + 16,384` words: 30 constants, the 1491 `delta_j`, the two-level root tables) and, while `q` is formed, the Newton arrays. The step-by-step count is expanded in Appendix E.1 and totals **row C = 1,337,973,395,390** (section 6).

### 4.4 Stage D: the inversion-free half-gcd (the method of bradcush `b30de9bf`/`4bcabff8`)

`G = gcd(g, R - 1)` is computed by a recursive half-gcd on the normal remainder sequence that keeps every matrix in coefficient form and never inverts a leading coefficient (pseudo-division). A node `hgcd(a, b, k)` of budget `k = 2^j - 1` runs its first child (budget `2^(j-1) - 1`) on the top window, applies the child's matrix `M1`, `(c, d) = adj(M1)(a, b)`, makes one pseudo-division with a quotient of degree 1 (its remainder `e` only on the `2^j - 1` positions the second child reads), runs the second child (`M2`) and forms `M = M1 [[Q, 1], [b^2, 0]] M2`. The apply of a node is formed on the three rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), one transform of `n` points per row in the block form of `27fbfbe7` 4.2 (the twist of the rows `Y + 1`, `Y - i` as a running product fused into the pass; E.2.1), and recombined by a 3-row CRT (22 operations per position); the product `M` on the two rows `Y - 1`, `Y + 1` only, recombined by the 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` (10 operations per position, the `1/2` folded into the `1/n` of the inverse). The product needs no third row: on the normal sequence every quotient has degree 1 and `b^2` is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; the values of each child's matrix on the row `Y - 1` are reused by its parent, the values of `M1` from the apply are reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). The base case is budget `2^6 - 1`, two remainder steps per pass.

The driver: while the degree `n` of `g` admits it, `k = 2^j - 1` is the largest with `2k + 1 <= n` and `k <= KMAX = 2^21 - 1` (the outer-step cap of weijiekoh `a78f526e`), `hgcd(k)` runs on the top window and its matrix is applied to `(g, R)` in place (`plan_apply`: the cheapest of the truncated transform of 4.3T on `n'` points, a `2^a`-point or a `3*2^a`-point transform; the entries of `M` row by row of `2^16` points when the transform has at least `2^17` points; `1/N` fused into the pointwise loop, 1 operation per point); from degree 254 down the schoolbook pseudo-division Euclid, then the normalisation of `G`. Every node works in one bump arena (allocation and release 10 operations each), `node_mem(j)` words at its peak (`33,554,176` at `j = 21`). On the normal sequence every length, parameter and allocation is a function of `m` alone: 31 outer steps (eleven on the truncated transform of `n'` points, then `2^a`- and `3*2^a`-point plans from `3*2^19` down to `3*2^6` points) and the Euclid from degree 141.

The row is charged for the normal remainder sequence (every quotient of degree 1), the case of the premise `H-NORMAL` (9.5): every division tests that its quotient has degree 1 (inside the fixed charge of each division: 30 per node division, 10 per base step) and every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter (2 operations, twice per node), and a zero remainder also ends the trial; on any other case the trial ABORTs (section 6.3). By the prefix lemma of 6.3 every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, so the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The charges are those of 4.2 (expanded in Appendix E.2); the total is **row D = 877,652,806,744** (sections 6.3, 6).

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G = gcd(g, R - 1)`, whose roots are the values `y = S^(2^22)` of the usable roots `S` of `g_c` (4.3G); stage F stops only at an `s != 0` with `F(c + s) = F(c - s)` (4.1.3), so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Ledger: operation count (`C(5) = 321`)

| row | what is charged | operations |
| --- | --- | ---: |
| init | constants and bookkeeping | 17,983 |
| setup | line setup | 4,910 |
| A | trial bookkeeping, centre draw, allocation | 1,228 |
| B | line evaluations, loop work, transform, normalization | 20,462,141,906 |
| C | 22 Graeffe steps and exact value-domain powering; Appendix E.1 | 1,337,973,395,390 |
| D | inversion-free half-gcd, normal-sequence walk with ABORT; Appendix E.2 | 834,209,997,260 |
| E | 64 isolation rounds at degree at most 16 | 166,081,821 |
| F | square roots and at most `2^22` line candidates | 2,232,498,018 |
| G | two reference hashes | 7,452 |
| trial loop | loop bookkeeping and allocator reset | 1,012 |
| plan misses | one per distinct plan size | 108,115 |
| output | fixed output rows | 3,390,080 |
| offline | declared cap over the 137,141-operation derivation | 1,000,000 |
| **N_max** | `T_fixed + T_trial + T_off` | **2,195,048,645,175** |

`T_fixed = 3,521,088`, `T_trial = 2,195,044,124,087`, and `T_off = 1,000,000`. Thus `N_max = 2,195,048,645,175`. The raw time is `log2(N_max/321) = 32.670960563667128431916933804096890992467177896637871509417249465135995376035535`. The claim rounds it upward at five decimals to `32.67097`.

Appendix E derives each changed charge. All searches stay charged. Stage F remains at its `2^22` cap, stage E remains at 64 rounds, and the offline search space contains no search or choice.

### 6.1 Validation

Run `python3 -B ledger_v2.py` from this candidate tree. The script derives the six- and seven-layer kernels, the running-twiddle node recurrence, both table removals, rows C and D, `N_max`, both logarithms, and the score.

### 6.2 Offline derivation

The literal derivation is unchanged. It executes 137,149 operations and is charged at its declared cap of 1,000,000 operations inside `N_max`. Its working set is 16 words plus a 64-byte digit buffer, 576 bytes, counted in section 7.

### 6.3 The normal-sequence charge and ABORT

The quotient test and return test are unchanged. On the first abnormal quotient, short return, or zero remainder, the trial resets the allocator and stops. Until that event, every length, budget, and allocation equals the normal walk. Thus every abnormal trial executes a prefix of the charged work and allocation sequence. `H-NORMAL` affects only success probability.

## 7. Memory counted by event

The arena capacity remains `3,129,725,504` bytes. Stage C set the predecessor's high-water mark at `3,129,708,480` bytes. The running-twiddle implementation removes the product-table allocation from stage C and the stage-D table allocation, so neither removal can raise that mark. We retain the whole predecessor arena as a conservative reservation. This also covers every unchanged allocation event of the normal walk and every prefix that an ABORT can execute.

| event or fixed region | bytes | effect on high-water mark |
| --- | ---: | --- |
| stage A live peak | 781,713,472 | below the retained arena |
| stage B live peak | 1,721,237,696 | below the retained arena |
| stage C predecessor peak | 3,129,708,480 | sets the retained pool mark |
| stage-C product table | removed | running twiddles; cannot raise the mark |
| stage D predecessor peak | 2,654,511,040 | below the stage-C mark |
| stage-D product table | removed | running twiddles; cannot raise the mark |
| two-ended pool reserve and middle gap | 3,129,708,608 | predecessor mark plus 128 bytes |
| slab classes | 0 | unchanged |
| stages E and later | 16,896 | unchanged |
| **arena** | **3,129,725,504** | conservative capacity |
| base code and static data | 5,250,444 | unchanged base image |
| seven-layer and group-zero straight-line bodies | 907,520 | section 4.2 bound |
| register file, `387 * 32` | 12,384 | charged machine state |
| offline working set | 576 | 16 words and digit buffer |
| stack | 65,536 | unchanged |
| **footprint** | **3,135,961,964** | sum of all rows |

The raw memory logarithm is `31.546260915135377623889046800038886674435495865278027842602921898719722552710192`. The claim rounds it upward at five decimals to `31.54627`. The arena contains no stored advice. Stage B and the truncated transforms build only their declared tables. Every product pass in stages C and D forms twiddles as running factors.

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
The centre is a fresh draw. For a centre `c` let `E_c` be the event `1 <= k(c) <= DMAX` (H-ONE, `P(E_c) >= q = 0.3931`) and `N_c` the event that the remainder sequence of `(g, R_c - 1)` (`g = g_c^(22)`, 4.3G) is normal down to its gcd (H-NORMAL, 9.5, `P(not N_c) <= delta = 0.003`). The Graeffe prefix and the value-domain stage C reproduce `g^(22)` and `R = S^((p-1)/2^23) mod g^(22)` exactly (4.3G, 4.3T) and add no premise; stage C needs `g^(22)` nonzero on `O1`, which fails with probability at most `eps_g = 2^22 n' (D - 1) / p < 2^-181` over the centre (4.3G). If `E_c` and `N_c` hold and `g^(22)` has no zero on `O1`, stages C and D run to their end and return `G = gcd(g^(22), R_c - 1)` with `1 <= deg G <= DMAX` (4.3G); a successful isolation and the scan of 4.1.3 then end in a verified collision. For `c` uniform `P(E_c and N_c) >= q - delta`, so with one centre (the event `g^(22)` zero on `O1` subtracted as `eps_g`)

`success = 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g`, `K = 1`.

Transfer to the written sampler (F-EVAL-001): `q - delta - eps_iso - eps_g` bounds the success probability of the run whose draws are exactly uniform on `F_p` (the premises and the isolation lemma are stated for uniform draws). The success of a run is an event of the vector of its draws, and the actual draws of 4.1.1 are within total variation `eps_coin` of the uniform vector, so the actual success probability is at least the ideal one minus `eps_coin`.

With `q = 0.3931`, `delta = 0.003`, `eps_iso <= 2.371e-15`, `eps_coin <= 1.404e-76`, `eps_g < 2^-181`: `q - delta = 0.3901`, and the value is `0.390099999999997628 >= 0.39`. The bound stays at or above `0.39` for every `delta <= 0.0030999` at `q = 0.3931`. The probability is over the random words of 4.1.1 for the fixed target, not over targets and not a sampled frequency.

### 9.3 Monodromy (support for H-ONE)
The roots of `G(c,t) = g_c(t^2)` come in pairs `+-t_i`, so the monodromy lies in the hyperoctahedral group `B_m` and `k(c)` counts positive Frobenius fixed points; for `B_m` this is Poisson(1/2) in the limit, `P(k >= 1) = 1 - e^(-1/2) = 0.3934693`, and Bonferroni at order 4 gives `P >= 151/384 = 0.3932292`. A theorem at two and three layers (Aubry-Perret, monodromy `B_12`, `B_62`); false for permutation polynomials, for decomposable `F` with imprimitive monodromy, and at one layer.

### 9.4 Isolation lemma
With `1 <= deg G <= 16`, a random-shift split isolates a linear factor within `Z = 64` rounds except with probability `eps_iso <= 2.371e-15`. Finite derivation: `G` divides `Y^((p-1)/2^23) - 1` (4.3G), a divisor of `Y^(p-1) - 1`, so it is squarefree and splits into `d = deg G <= 16` distinct linear factors `X - t_i` over `F_p`. A round with shift `a` keeps a nontrivial part of the current factor `H` under `gcd(H, (X + a)^((p-1)/2) - 1)` (or `X + a` itself when `a = -t_i`), so two roots `t_i != t_j` stay together only if `chi(t_i + a) = chi(t_j + a)` or `a` is in `{-t_i, -t_j}`. Since `sum_a chi((a + t_i)(a + t_j)) = -1` for `t_i != t_j`, exactly `(p - 3)/2` shifts give equal nonzero characters, so for `a` uniform on `F_p` the pair stays together with probability at most `((p - 3)/2 + 2)/p = 1/2 + 1/(2p)`; each shift is a fresh random word reduced mod `p`, within statistical distance `2^-128` of uniform (4.1.1), so per round the bound is `1/2 + 2^-127`, independently across rounds. The parts are nested, so the factor kept after 64 rounds holds two roots only if one of the at most `C(16,2) = 120` pairs was never separated in 64 rounds. By the union bound `eps_iso <= 120 (1/2 + 2^-127)^64 < 6.6e-18 <= 2.371e-15`; the looser stated value `2.371e-15` is kept, so every other number is unchanged.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries `e6dcb600` and `1aa56884`; allowance split of cryptogakusei's `4888e783`; organizer-run tests in the form of gta6rp's `bef31fdd`)
**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(h_c, R_c - 1)`, where `h_c = g_c^(22)` is the 22-fold Graeffe transform (4.3G) of the monic odd part `g_c` of section 3 (monic, degree `m = 24,414,062`) and `R_c = S^((p-1)/2^23) mod h_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.003` (`2^-8.38`). Stage D is charged for the normal sequence; every division tests its quotient degree and every call of the half-gcd its return, and on any other case the trial ends (ABORT, sections 4.4, 6.3). The premise enters only the success probability (9.2): the time and memory bounds hold for every remainder sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work (6.3). For a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes, each a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-203`; the premise extrapolates a much weaker form of this random-pair behaviour (`delta = 0.003`) to the structured pair `(h_c, R_c - 1)`. Measured support is organizer-run (10.5.1): the six experiments `euclid-normal-n2-t256-l2-g22-a` to `-f` compute the complete Euclidean sequence of `(h_c, R_c - 1)` for this construction (22 Graeffe steps, exponent `(p-1)/2^23`) on the truncation `F_2` (`m = 12`) for 256 organizer-seeded trials of two centres each (3,072 sequences in all) and return a witness pair exactly when both sequences of a trial are normal; `euclid-normal-n3-t24-g22` and `euclid-normal-n4-t2-g22` do the same at `m = 62, 312`. Zero abnormal in the 3,072 sequences is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (`delta = 0.003` is the declared premise). Not verified at `r = 5`, which would need the computation itself; the organizer-run tests are at `m = 12` to `312`, far below `m`.

## 10. Experiments

Program `experiments/exp_euclid.py` (euclid-normal, one-centre) and `experiments/exp_line.py` / `experiments/exp_lowbits.py` (line-ladder and lowbits-birthday), with `experiments/manifest.json`.

10.3 The truncations. `F_N(c + X)` is coordinate 0 after the first `N` S-box layers on the line `j = 0`; `F_2`, `F_3`, `F_4` have odd parts of degree `m = 12, 62, 312`. The arithmetic monodromy at `N = 2, 3` is `B_12`, `B_62` (Grok jobs 136, 137, re-run on the deployed constants).

10.5.1 Organizer-run set. euclid-normal-n2-t256-l2-g22-a to -f compute the complete Euclidean sequence of `(h_c, R_c - 1)` (the pair of 9.5: 22 Graeffe steps, exponent `(p-1)/2^23`) for this construction at depth `N = 2` (`m = 12`), each for 256 organizer-seeded trials of two centres (512 sequences per entry, 3,072 in all; the final letter only changes the organizer seeds); euclid-normal-n2-t256-g22, -n3-t24-g22 and -n4-t2-g22 compute one sequence per trial at `m = 12, 62, 312`. A trial returns a witness pair exactly when its sequences are normal; the count of trials that return a pair is a reproducible observation consistent with the premise H-NORMAL (9.5). We do not treat the organizer-seeded centres as independent unselected samples and draw no population bound from these runs: `delta = 0.003` is the declared premise (9.5), carried by its stated support, not by an interval computed from the experiments. one-centre-n2-t256 and one-centre-n3-t24 run one trial of the algorithm with the Graeffe prefix off (`s = 0`: the gcd against `S^((p-1)/2) - 1` and a square root in place of the scan; they test `H-ONE`, a statement about `g_c` that the prefix does not change, 4.3G) at depth `N = 2, 3` per organizer seed and return a witness pair exactly when the sequence is normal, `1 <= k(c) <= 16` and the isolated root gives a verified collision of `F_N`; the returned count is a reproducible observation (9.1), reported as an observation with no interval inferred. line-ladder-w6/-w8/-w10/-w12 and lowbits-birthday corroborate the antipodal structure, not the score-critical basis. Our runs of the six -l2-g22 entries with local seeds (one CPU; 9.99 to 11.79 s each on our workstation, where an -l2 entry without the prefix takes 11.44 s): 3,072 sequences, all normal, 256 pairs per entry; the gcd had positive degree for 1,248 of the 3,072 centres (0.406). Our runs of -n2-t256-g22, -n3-t24-g22 and -n4-t2-g22: 256, 24 and 2 sequences, all normal. The organizer-checkable output is the returned witness-pair count; the premises H-ONE and H-NORMAL hold under trusted execution of the submitted program.

## Appendix E: exact changed rows and memory events

### E.1 Row C = 1,337,973,395,390

| part | operations |
| --- | ---: |
| plans, constants, root tables, zero fill, first allocations; product table removed | 8,322,562 |
| allocation of `A`; 22 Graeffe steps and prefix buffer | 88,046,300,283 |
| Newton reciprocal; predecessor total retained as a conservative running-pass cap | 10,381,373,048 |
| quotient product and copy; predecessor total retained as a conservative running-pass cap | 3,110,092,300 |
| `g` to `O1` and `O2` | 2,691,170,006 |
| start residue `A0` on `O2` | 1,598,195,721 |
| `A0` to `O1` | 2,896,481,784 |
| `k1` by chunked inversion | 361,560,465 |
| 209 squaring steps | 1,222,325,872,028 |
| exit Montgomery step | 3,354,517,347 |
| two truncated inverses | 3,199,508,846 |
| stage bookkeeping | 1,000 |
| **row C** | **1,337,973,395,390** |

The four-block savings come from the live geometry. One middle-pass set saves `9,160,704`. A bottom pass has `1,526,784` blocks. A Graeffe step saves `3*9,160,704 + 1,526,784 = 29,008,896`. A bit-zero powering step saves `39,696,384` and costs `5,832,341,212`. A bit-one step saves `38,169,600` and costs `5,907,153,628`. A normal truncated transform saves `12,214,272`. The 22 Graeffe steps, 164 bit-zero steps, 45 bit-one steps, nine other transforms, and the removed `16,777,216`-operation table sum to `8,992,740,352`. One Graeffe step costs `4,002,104,526`.

The Newton and quotient rows execute the union machine's running-twiddle passes. Their predecessor totals are retained as conservative caps. This choice gives away savings but cannot undercount the work.

### E.2 Row D = 834,209,997,260

| outer step | degree `n` | k | `node_bf(j)` | apply charge | step total |
|---:|---:|---:|---:|---:|---:|
| 1 | 24,414,062 | 2,097,151 | 29,795,972,627 | 45,907,820,462 (truncated, `n'`, 24,428,544) | 75,703,794,669 |
| 2 | 22,316,911 | 2,097,151 | 29,795,972,627 | 45,928,791,972 (truncated, `n'`, 24,428,544) | 75,724,766,179 |
| 3 | 20,219,760 | 2,097,151 | 29,795,972,627 | 45,949,763,482 (truncated, `n'`, 24,428,544) | 75,745,737,689 |
| 4 | 18,122,609 | 2,097,151 | 29,795,972,627 | 45,970,734,992 (truncated, `n'`, 24,428,544) | 75,766,709,199 |
| 5 | 16,025,458 | 2,097,151 | 29,795,972,627 | 45,991,706,502 (truncated, `n'`, 24,428,544) | 75,787,680,709 |
| 6 | 13,928,307 | 2,097,151 | 29,795,972,627 | 46,012,678,012 (truncated, `n'`, 24,428,544) | 75,808,652,219 |
| 7 | 11,831,156 | 2,097,151 | 29,795,972,627 | 46,033,649,522 (truncated, `n'`, 24,428,544) | 75,829,623,729 |
| 8 | 9,734,005 | 2,097,151 | 29,795,972,627 | 46,054,621,032 (truncated, `n'`, 24,428,544) | 75,850,595,239 |
| 9 | 7,636,854 | 2,097,151 | 29,795,972,627 | 46,075,592,542 (truncated, `n'`, 24,428,544) | 75,871,566,749 |
| 10 | 5,539,703 | 2,097,151 | 29,795,972,627 | 46,096,564,052 (truncated, `n'`, 24,428,544) | 75,892,538,259 |
| 11 | 3,442,552 | 1,048,575 | 13,865,617,022 | 28,908,306,250 (truncated, `n'`, 24,428,544) | 42,773,924,852 |
| 12 | 2,393,977 | 1,048,575 | 13,865,617,022 | 1,952,017,076 (`3*2^a`, 1,572,864) | 15,817,635,257 |
| 13 | 1,345,402 | 524,287 | 6,428,383,931 | 1,378,031,092 (`3*2^a`, 1,572,864) | 7,806,416,182 |
| 14 | 821,115 | 262,143 | 2,967,386,583 | 549,264,204 (`3*2^a`, 786,432) | 3,516,651,946 |
| 15 | 558,972 | 262,143 | 2,967,386,583 | 275,706,784 (`3*2^a`, 393,216) | 3,243,094,526 |
| 16 | 296,829 | 131,071 | 1,362,521,534 | 113,106,548 (`3*2^a`, 196,608) | 1,475,629,241 |
| 17 | 165,758 | 65,535 | 621,318,441 | 69,889,690 (`2^a`, 131,072) | 691,209,290 |
| 18 | 100,223 | 32,767 | 280,538,527 | 52,234,606 (`3*2^a`, 98,304) | 332,774,292 |
| 19 | 67,456 | 32,767 | 280,538,527 | 26,136,794 (`3*2^a`, 49,152) | 306,676,480 |
| 20 | 34,689 | 16,383 | 127,311,152 | 12,850,186 (`3*2^a`, 24,576) | 140,162,497 |
| 21 | 18,306 | 8,191 | 57,353,155 | 5,493,542 (`3*2^a`, 12,288) | 62,847,856 |
| 22 | 10,115 | 4,095 | 25,603,926 | 2,712,094 (`3*2^a`, 6,144) | 28,317,179 |
| 23 | 6,020 | 2,047 | 11,295,765 | 1,549,028 (`2^a`, 4,096) | 12,845,952 |
| 24 | 3,973 | 1,023 | 4,901,301 | 1,300,366 (`3*2^a`, 3,072) | 6,202,826 |
| 25 | 2,950 | 1,023 | 4,901,301 | 753,526 (`2^a`, 2,048) | 5,655,986 |
| 26 | 1,927 | 511 | 2,072,679 | 636,852 (`3*2^a`, 1,536) | 2,710,690 |
| 27 | 1,416 | 511 | 2,072,679 | 366,528 (`2^a`, 1,024) | 2,440,366 |
| 28 | 905 | 255 | 837,679 | 259,912 (`3*2^a`, 768) | 1,098,750 |
| 29 | 650 | 255 | 837,679 | 177,638 (`2^a`, 512) | 1,016,476 |
| 30 | 395 | 127 | 328,678 | 127,290 (`3*2^a`, 384) | 457,127 |
| 31 | 268 | 127 | 328,678 | 66,330 (`3*2^a`, 192) | 396,167 |

| tail | operations |
| --- | ---: |
| 31 outer steps above | 834,209,828,578 |
| schoolbook Euclid from degree 141 | 163,983 |
| normalization of `G` | 2,653 |
| stage entry after removing the product table | 1,624 |
| stage exit | 422 |
| **row D** | **834,209,997,260** |

The outer applies execute running-twiddle passes and retain the predecessor's larger charges. The stage removes `8*2^19 = 4,194,304` operations for the table that no longer exists. Every other tail event is unchanged.

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

The per-block twiddle reading is no smaller than the executed shared running chain. The one-percent allowance covers control not modeled block by block. The top-window checks remain those of the predecessor and hold for every row in the repetition table.

#### E.2.2 Embedded exact-integer script

```python
#!/usr/bin/env python3
"""Exact-integer evidence for the r5 387-register machine reprice.

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
    7: 2,
    8: 2,
    9: 2,
    10: 2,
    11: 1,
    12: 1,
    13: 1,
    14: 1,
    15: 2,
    16: 1,
    17: 1,
    18: 2,
    19: 1,
    20: 2,
    21: 10,
}

CURRENT_STAGE_C = 1_346_966_135_742
CURRENT_STAGE_D = 877_652_806_744
CURRENT_N_MAX = 2_247_484_195_011
CURRENT_MEMORY_BYTES = 3_135_041_484
CURRENT_SCORE = Decimal("44.25102")

# The truncated transforms retain their proven split 4 | 4,5,5,5 | 4.  The
# four-block body saves two controls in every middle and bottom block.  O2 uses
# the two saved controls for its two extra array pointers; a one-bit step has
# one additional point-pointer update.  A fused Graeffe bottom block has one
# extra pointer and therefore saves one.  These are the event counts of 4.3T,
# not a fitted delta.
TRUNCATED_POINTS = 24_428_544
TRUNCATED_WIDTHS = (5, 4, 4, 5)
MIDDLE_SAVING = 2 * sum(TRUNCATED_POINTS // (1 << width) for width in TRUNCATED_WIDTHS)
BOTTOM_BLOCKS = TRUNCATED_POINTS // 16
GRAEFFE_STEP_SAVING = 3 * MIDDLE_SAVING + BOTTOM_BLOCKS
BIT0_STEP_SAVING = 4 * MIDDLE_SAVING + 2 * BOTTOM_BLOCKS
BIT1_STEP_SAVING = 4 * MIDDLE_SAVING + BOTTOM_BLOCKS
TRUNCATED_TRANSFORM_SAVING = MIDDLE_SAVING + 2 * BOTTOM_BLOCKS
STAGE_C_TWIDDLE_TABLE = 8 * (1 << 21)
STAGE_C_SAVING = (
    STAGE_C_TWIDDLE_TABLE
    + 22 * GRAEFFE_STEP_SAVING
    + 164 * BIT0_STEP_SAVING
    + 45 * BIT1_STEP_SAVING
    + 9 * TRUNCATED_TRANSFORM_SAVING
)
STAGE_C = CURRENT_STAGE_C - STAGE_C_SAVING

OLD_NODE_SUM = sum(old_node_bf(j) * count for j, count in NODE_COUNTS.items())
NEW_NODE_SUM = sum(node_bf(j) * count for j, count in NODE_COUNTS.items())
STAGE_D_TWIDDLE_TABLE = 8 * (1 << 19)
STAGE_D = (
    CURRENT_STAGE_D
    - OLD_NODE_SUM
    + NEW_NODE_SUM
    - STAGE_D_TWIDDLE_TABLE
)

N_MAX = CURRENT_N_MAX + (STAGE_C - CURRENT_STAGE_C) + (STAGE_D - CURRENT_STAGE_D)

CODE_DELTA = 907_520
REGISTER_BYTES = 387 * 32
OFFLINE_WORKING_BYTES = 16 * 32 + 64
MEMORY_BYTES = CURRENT_MEMORY_BYTES + CODE_DELTA + REGISTER_BYTES + OFFLINE_WORKING_BYTES

RAW_TIME = (Decimal(N_MAX).ln() - Decimal(321).ln()) / Decimal(2).ln()
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
assert sum(NODE_COUNTS.values()) == 31

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

Section 7 lists every event that can set the retained high-water mark. The old stage-C product table and stage-D product table events are deleted. All remaining allocator events keep the same order and size. Since both edits remove blocks, no event can exceed the retained `3,129,708,480`-byte pool mark. The fixed regions then produce the exact footprint `3,135,961,964` bytes.
