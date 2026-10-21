# Orchard Poseidon, r = 3: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, a Graeffe prefix, value-domain powering on truncated point sets with radix-16 passes, inversion-free half-gcd on three rows, one centre

## 1. Claim

Target: `poseidon-orchard-r3-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, three partial rounds 4, 5 and 6, full rounds 60-63, state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is the frontier algorithm with its two-row half-gcd products unchanged and the node row transforms evaluated in the conservative block form of Appendix E.2.1. It is an algorithm (sections 2-4) with an operation count that bounds every run (sections 6-7) and a success probability derived from two score-critical premises: `H-ONE` (section 9.1), a statement about the fraction of centres at which the fixed digest polynomial has between 1 and 16 usable roots, and `H-NORMAL` (section 9.5), a statement about the normality of the remainder sequence that enters only the success probability. Section 9.2 derives the success probability from them.

* Relative to frontier entry `26797647`, the half-gcd node keeps its two-row product and three-row apply but evaluates every node row transform by the block-form pass derived in Appendix E.2.1. The per-block reading re-forms twiddles and adds a declared one per cent allowance. The exhaustive 800-plan audit in E.2.2 retains Graeffe depth 17, outer cap 16 and the base two-ended memory layout. Row D is `13,670,789,186`; memory and the success argument are unchanged.
* The algorithm: draw a centre `c` from two fresh random words, `c = (w1 2^256 + w2) mod p` (within statistical distance `p/2^512` of uniform on `F_p`, 4.1.1), build the odd part `g_c` of the line polynomial by evaluation and one inverse transform, replace `g_c` by its 17-fold Graeffe transform `g = g_c^(17)` (monic, degree `m`, its roots the `2^17`-th powers of those of `g_c`; section 4.3G), compute `R = S^((p-1)/2^18) mod g` in the value domain by Montgomery powering on two truncated point sets `O1`, `O2` of `n' = 477 * 2^11 = 976,896` points (477 of the 512 depth-9 nodes of the subgroup of order `2^20` and of its coset; the method of bradcush `b30de9bf`/`a41aecdd`, there 15 of 16 nodes, section 4.3T; radix-16 passes under the declared 64-word register file, 4.2), take `G = gcd(g, R - 1)` by the inversion-free half-gcd on three rows of bradcush `4bcabff8` (outer step `k <= 2^16 - 1`, section 4.4), charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, and if `G` has degree between 1 and `DMAX = 16` isolate a root `y` of `G` in at most `Z = 64` rounds, find `s` with `s^(2^18) = y` and `F(c + s) = F(c - s)` among at most `2^17` candidates (4.1.3), map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39009`: a lower bound for the probability, over the algorithm's fresh random words, that the centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1), `delta = 0.003` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `eps_iso <= 2.371e-15`, `eps_coin <= 65 p / 2^512 <= 1.404e-76`, `eps_g <= 2^17 n' (D - 1) / p < 2^-196` (the centre makes `g` vanish at a point of `O1`, 4.3G) (sections 4.1.1, 4.3T, 9.2). The value the formula gives is `0.390099999999997628` (at or above the organizer floor 0.39); the claim is that value floored at five decimals.
* `time_log2 = 27.62270` in target-compression units (`C(3) = 279` primitive operations per unit): the operation count that bounds every run, derived in section 6 as `T_fixed + K * T_trial + T_off` with `K = 1`, stage C a Graeffe prefix of 17 steps (4.3G) and value-domain powering on truncated point sets (4.3T), stage D the inversion-free half-gcd on three rows charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (4.4, 6.3; the time bound holds for every sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work), stage E at its cap of `Z` rounds at degree `DMAX`, and the scan of stage F at its cap of `2^17` candidates (4.1.3). `N_max = 57,658,542,754` operations, `log2(N_max / 279) = 27.62269401206413...`, rounded up at five decimals. The offline constant derivation and exhaustive planner cost 81,000,000 operations (section 6.2 and Appendix E.2.2); that bound is inside `N_max` and is declared as `preprocessing_log2 = 26.27142` (one quantity, not added twice).
* `memory_log2_bytes = 26.908` (`125,859,472` bytes, section 7). The normalized cost is `27.62270 + max(0, 26.908 - 20) = 27.62270 + 6.908 = 34.53070`.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; every random field element is drawn from two fresh words, at most `65` field elements (`130` words) per run (section 4.1.1), and a draw costs 63 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^9`, then the roots of its odd part about a centre, found, after a Graeffe prefix (Dandelin-Graeffe root squaring), with a gcd against `S^((p-1)/2^18) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Against our r = 3 entry `6c151a2e` (normalized cost 34.58689), one change to its algorithm: the product step `M = M1 [[Q, 1], [b^2, 0]] M2` of each half-gcd node runs on the two rows `Y - 1`, `Y + 1` (`2n` points) in place of three; its entries have degree at most `2n - 1` on the normal sequence (4.4). Row D `13,937,663,593` (was `16,040,973,753`); every other row, the memory and the success bound are unchanged. Our entry `6c151a2e` made one change against our r = 3 entry `0c925670` (normalized cost 34.60828): a Graeffe prefix (4.3G). Stage C first applies 17 Graeffe steps `g(Y) <- E(Y)^2 - Y O(Y)^2` on `O1` (`124,876,887` operations each) and then raises `S` to `(p-1)/2^18` (219 squaring steps in place of 236); the gcd keeps exactly the `2^17`-th powers of the usable roots (`1 <= deg G <= k(c)`), and stage F finds the root of `g_c` above the isolated one by a scan of at most `2^17` candidates on the line map (4.1.3). Row C `42,602,465,472` (was `43,557,525,975`), row F `59,613,486` (was `47,012`); memory unchanged. `H-NORMAL` is stated for the pair of the transformed polynomial and its organizer-run tests compute that pair (9.5, 10.5.1); `H-ONE`, every other charge and the other experiments are unchanged.
* Prior entries: our r = 3 entry `0c925670` and its predecessors replaced our filed r = 3 entry `95d8b186` (normalized cost 35.59204) by the same algorithm with three changes: (i) stage D is bradcush's inversion-free half-gcd on the rows `Y - 1`, `Y + 1`, `Y - i` (entry `4bcabff8`), ported and charged in this cost model (4.4), with the normal-sequence charging and the ABORT of bradcush `e6dcb600` as before, in place of the lean cofactor-free half-gcd with a memory cap; (ii) the transforms of stage C run radix-16 passes on the 64-register machine stated as a restriction in claim.json (4.2, 4.3T), the twist and `1/N` scalings are running products fused into the adjacent pass, the batch inversion of `k1` works in the scratch buffer of the stage, and the table of the Newton and quotient products is sized to their transforms (`3*2^17` points); (iii) a line evaluation of stage B is charged at its counted field operations, `155 + 21 r = 218` (section 3), in place of one target-compression unit. `95d8b186` is the one-centre algorithm of our r = 6 entry `c318f442` with the stage C of bradcush `b30de9bf`/`a41aecdd`, the memory schedule of 0xshikhar `52120fad` (each stage builds and frees the twiddle table of its own transforms) and the premises `H-ONE` at `q = 0.3931` and `H-NORMAL` at `delta = 0.003` (the split of cryptogakusei's entry `4888e783`, organizer-run tests in the form of gta6rp's entry `bef31fdd`); it replaced our executed r = 3 entry `bb9cca58`. Against our entry `253629b9` (normalized cost 34.82599), the same package, our entry `bcf8e01c` (normalized cost 34.77736) changes four things in the transforms of stage C (4.2, 4.3T): (a) the dropped row 15 of the top pass is formed in registers inside the top pass from the zero chunk of the coefficients, and the residues of row 14 at the `6,144` offsets above `n'` from the 14 complete rows, so the scratch is `6,144` words (from `71,680`); (b) `A` and `g` on `O2` are held as `delta_j A` and `delta_j^2 g`, so the step applies no node factor per point and `delta_j^-1` enters the inverse scaling of a block; (c) the point `x` of a 1-bit step is formed in registers; (d) one two-level table of the `2^21`-th roots (`3,072` words) serves every root lookup (from `4 x 4,096` words), `c^-1` being looked up once per group of 16 blocks. The memory is the allocator high-water mark of the one trial (section 7). Against `bcf8e01c`, the same algorithm and package, `0c925670` (34.60828) charges the loads and stores of the data words of the transform-pass blocks of 4.3T (top, middle and bottom passes) one operation each, base plus index (4.2): row C `43,557,525,975` (was `51,044,458,967`), row D `16,040,973,753` (was `16,119,330,233`, its applies on `O1` use the same transforms); memory unchanged; every other charge, the premises and the experiments are unchanged.
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1), a statement about the fraction of good centres; `H-NORMAL` (score-critical for the success probability only, section 9.5), bradcush's premise on the normality of the remainder sequence stated with the allowance `delta = 0.003` and supported by organizer-run tests. The machine (64 registers of 256 bits and constants as immediates; every load, store and spill counted) is stated as a restriction in claim.json, as the accepted entries `89b451ff` and `fb176310` state theirs, not as a heuristic (4.2). The costs are the declared cost model of this entry: the charging rules of section 4.2 with that register file, the half-gcd of stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (Appendix E). Everything else is proved or counted here.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`. `(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`. The algorithm uses the line `j = 0`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant `M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS, nonzero on the deployed constants, checked). Let `(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, `d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i` (the supports are disjoint). After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6 (partial), 60, 61, 62, 63 (full) put nine S-box layers on top of an affine map, and the digest is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^9 = D = 1,953,125`. The leading coefficient is obtained by propagating leading coefficients through the nine layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used: `f_D(0) = 0x11f9cfdeecb8c5965318cbdc58480d2e6db510f12862658af639ce81578c3e23` (computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau` against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`), hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 976,562`, `g_c` has degree exactly `m` and leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`, `W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The useful roots are the roots in `F_p` with `S^((p-1)/2) = 1`: they are the roots of `gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p`; `S = 0` is not a root of `S^((p-1)/2) - 1`). This gcd divides the squarefree `S^((p-1)/2) - 1`, so it is a product of `k(c)` distinct linear factors over `F_p` (9.1); stage D computes instead the gcd of 4.3G, whose roots are their `2^17`-th powers.

Construction of `g_c` by evaluation. `H = 1,572,864 = 3 * 2^19` divides `p - 1` (`p - 1 = 2^32 * 3 * q`) and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`; one inverse transform of size `H` returns the coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). The `2H = 3,145,728` evaluations of `F` are each charged at the field operations of a line evaluation, counted as the unit `C(r) = 216 + 21 r` is counted (a round: 3 additions of its constants, S-boxes at 3 operations, the MDS at 9 multiplications and 6 additions): the affine start `alpha + beta W` (6; the round-2 constants are inside `alpha`), round 2 (24), round 3 (27), the `r` partial rounds (21 each), rounds 60-62 (27 each) and round 63 with row 0 of the last MDS only (3 + 9 + 5 = 17), `155 + 21 r = 218` operations at `r = 3` against `C(3) = 279` for a full permutation. The loop work (two point additions, one subtraction, one multiplication by `1/(2 zeta^i)`, the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, the store with its address, the loop control and the bit-reversed index) is charged on top (stage B, section 6), with the twiddle table of the transform, built by stage B (4.2).

## 4. The algorithm (one centre, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   constants (once; no twiddle table: each stage builds the table of its own transforms, 4.2)
setup:  the line (line_setup) (once)
for t = 1, ..., K (K = 1):            [the test t <= K is made at the start of the trial; no exit except success]
  A  c := (w1 * 2^256 + w2) mod p from two fresh random words w1, w2 (4.1.1)
  B  g := monic g_c, by section 3 (3,145,728 evaluations + one inverse NTT of size 1,572,864 + the nonzero-leading-coefficient test + normalisation)
  C  g := g^(17): 17 Graeffe steps on O1 (section 4.3G); R := S^((p-1)/2^18) mod g, in the value domain on the truncated point sets O1, O2 of n' = 976,896 points (section 4.3T): 219 squaring steps, 45 of them also multiplying by S
  D  G := gcd(g, R - 1) (monic): the inversion-free half-gcd on three rows (section 4.4), charged for the normal remainder sequence with the quotient and return tests; on any other case ABORT (6.3)
  E  if deg G = 0 or deg G > DMAX: trial ends. Otherwise isolate a root y of G (4.1.2); if none within Z = 64 rounds: trial ends.
  F  u := a 2^18-th root of y (18 Tonelli-Shanks square roots, 2-adicity 32); for j = 0, ..., 2^17 - 1: s := u mu^j, W1 = c + s, W2 = c - s, until F(W1) = F(W2) (4.1.3); tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (279 operations each) are equal and the pairs differ -> output; otherwise the trial ends
```

4.1.1 Coins (ruling `04c0dd43`, finding F-EVAL-001). The only randomness is the cost-model random-word primitive. Every random field element of the algorithm (the centre `c` of stage A and each shift of stage E) is drawn from two fresh 256-bit words `w1, w2`: each is reduced mod `p` by three conditional subtractions (exact, `2^256 < 4p`), and `x = (w1 mod p) * (2^256 mod p) + (w2 mod p)` in `F_p`, i.e. `x = (w1 2^256 + w2) mod p` with `w1 2^256 + w2` uniform on `[0, 2^512)`. There is no rejection and no retry. A draw is 63 operations: per word 1 random-word operation, 1 load, 1 store, 3 control, the reduction 9 and its loop control 11 (26 per word, 52), two Montgomery conversions 2, the load of the constant `2^256 mod p` 1, one multiplication 1, one addition 1, entry 2, the two addresses 4. At most `1 + Z = 65` draws (`130` words) per run. With `2^512 = Q p + r`, each residue has `Q` or `Q + 1` preimages, so one draw is within statistical distance `r (p - r) / (p 2^512) <= p / 2^512 = 2^-258.0` of uniform on `F_p`; the 65 draws are independent, so the joint distribution of all the coins of a run is within `eps_coin = 65 p / 2^512 <= 1.404e-76` of the distribution with every draw exactly uniform (total variation is subadditive over independent components).

4.1.2 Stage E: isolating a root of `G`. With `1 <= deg G <= DMAX = 16`, a Cantor-Zassenhaus split with random shifts isolates one linear factor in at most `Z = 64` rounds at degree `<= 16`; `eps_iso <= 2.371e-15` bounds the probability that 64 rounds fail to isolate a root when `deg G >= 1` (section 9.4).

4.1.3 Stage F: the root of `g_c` above `y`. By 4.3G, `y = S^(2^17)` for a usable root `S` of `g_c`, and the solutions of `S'^(2^17) = y` are `u^2 mu^(2j)`, `j < 2^17`, where `u^(2^18) = y` and `mu` is a fixed primitive `2^18`-th root of unity (`2^18 | p - 1`; a constant of the offline derivation, 6.2). `u` comes from 18 successive Tonelli-Shanks square roots: `y` is a `2^18`-th power, and if `x` is a `2^k`-th power with `1 <= k <= 18`, both square roots of `x` are `2^(k-1)`-th powers (`-1` is a `2^(k-1)`-th power, `2^k | p - 1`). The scan takes `s = u mu^j` for `j = 0, 1, ..., 2^17 - 1` and stops at the first `j` with `F(c + s) = F(c - s)` (two line evaluations of section 3). For `S' = s^2` a root of `g_c` this holds, because `F(c + s) - F(c - s) = 2 s g_c(s^2)`, so the scan stops at the latest at the `j` of `S`; any stop has `s != 0` (`y != 0`) and `F(c + s) = F(c - s)`, a collision by 2.4. Charge per candidate: `s <- s mu` 1, `c + s` and `c - s` 2, two line evaluations `2 * 218`, their calls 4, the comparison and branch 2, the loop control 3: `448`; at most `2^17` candidates, `58,720,256`, and the loop exit 2. The 18 square roots are charged `47,012` each (the whole row F of the algorithm without the prefix, a square root and the back-map), `846,216`, and the back-map `47,012`: row F = `59,613,486`.

### 4.2 Machine model and charging rules (summary; `C(3) = 279`)

Every field operation, load, store, control operation and random word is one primitive operation; `C(r) = 216 + 21 r = 279` primitive operations is one target-compression unit. The register file is 64 words of 256 bits (the machine restriction of claim.json: it holds the 16 values and the 15 twiddles of a radix-16 block or group; every other value is charged as a load or store, 2 operations each (the access and the addition of its address); a load or store of a data word of a block of a transform pass of 4.3T is one operation, its address the base plus index of the load or store itself: one load per word fetched from memory and one store per word written, the wording of the accepted entries `89b451ff` and `070a02b2`; the transform passes of the Newton and quotient products of stage C and of the products of stage D run in the same block form: per block of `2^k <= 16` values its `2^k` loads and stores, `k 2^(k-1)` butterflies and 5 of control, per group its `2^k - 1` twiddles held in registers, rows C and D of Appendix E), the only register assumption; the algorithm runs on one thread, no dispatch. Allocation: one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes. A block of more than `2^10` bytes is served by the two-ended pool (one region, two ends, first-fit in address order, the statements marked `# pool:H` using the high end and, with the depth-parity placement of section 7, the end `(j + bit8) mod 2` of a half-gcd node at depth `j`); every smaller block by its slab class (the least `j >= 7` with `2^j >= need`, a slot of `2^j` bytes). The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows (a pool request `97` operations besides the walk and `13` per block examined, a slab request at most `126`, a free `81` for a slab block and at most `105` for a pool block). The memory of both allocators is the arena of section 7. Twiddle tables: none is built in init; stage B, the Newton and quotient products of stage C and stage D each build the table of their own largest transform (`2^(a-1)` entries for `3*2^a` points: its root, 5 operations per entry and the loop) and free it at the end of that work, charged in the stage's row; the passes of 4.3T use one two-level table of the `2^21`-th roots of unity `psi^e` (`2^11 + 2^10 = 3,072` words, `psi^(1024 a)` and `psi^b`: a root is two loads and one multiplication, an inverse root also the negated exponent, 1 operation), built in stage C and kept for the applies of stage D on `O1`, which frees it; the table of stage D serves its transforms of `2^19` and `3*2^18` points.

### 4.3G The Graeffe prefix

Definition. For `h` monic of even degree `m` write `h(X) = E(X^2) + X O(X^2)`; its Graeffe transform is `h~(Y) = E(Y)^2 - Y O(Y)^2`, so `h~(X^2) = h(X) h(-X)` and `h~` is monic of degree `m` with roots the squares of the roots of `h` (with multiplicity). Stage C first replaces `g = g_c` by `g^(17)`, 17 Graeffe steps, then computes `R = S^e mod g^(17)`, `e = (p-1)/2^18` (2-adicity 32), and stage D takes `G = gcd(g^(17), R - 1)`.

Lemma. `G` is the product of `(Y - y)` over the distinct values `y = S^(2^17)`, `S` a usable root of `g_c` (a nonzero square in `F_p` with `g_c(S) = 0`, section 3). Proof: `g^(17)(Y) = prod_i (Y - S_i^(2^17))` over the roots `S_i` of `g_c` in an algebraic closure; `Y^e - 1` is squarefree and its roots are the `2^18`-th powers of `F_p^*`. If `S_i^(2^17) = u^(2^18)` with `u` in `F_p^*`, then `S_i = u^2 zeta` with `zeta^(2^17) = 1`, so `zeta` is in `F_p` and `zeta = xi^2` with `xi^(2^18) = 1` (`2^18 | p - 1`), and `S_i = (u xi)^2` is a nonzero square of `F_p`; conversely `S = v^2` gives `S^(2^17) = v^(2^18)`. So `deg G` is the number of distinct `2^17`-th powers of the usable roots: `1 <= deg G <= k(c)` when `k(c) >= 1`, and `deg G = 0` when `k(c) = 0`; the event `E_c` of 9.2 gives `1 <= deg G <= DMAX`.

Execution (on the point set `O1` of 4.3T). One step: `E` (`m/2 + 1` coefficients) and `O` (`m/2`) are read from `g` at stride 2 by the top passes of two truncated forwards, which load only the input chunks below the length (8 or 7 of the 16 per offset, two offset ranges; no zero-fill) and form the 15 present rows; the fused bottom pass forms `G = (E^2 - y O^2)/N` at each point `y` of `O1` between the forward and the inverse bottom layers (`y` is the last-layer twiddle of its butterfly, in a register: two squarings, two multiplications, one subtraction, 5 per point; the 16-point blocks of `E` and `O` and their 15 twiddles fit the 64-word register file); one truncated inverse (row 15 formed in registers, the tail solve of row 14 and the recoveries of 4.3T) stores the new coefficients into the array of `g` (those above `m` come out zero). `E` and `O` on `O1` use the arrays of `A` on `O2` and of `A` on `O1` before stage C fills them, with a scratch of `6,144` words of their own (allocated and zero-filled for the prefix, freed after it); no array is added and the high-water mark of section 7 is unchanged. One step is `124,876,887` operations (Appendix E.1), 17 steps; stage C then runs 219 squaring steps in place of 236 (the exponent loses 17 low zero bits). A step saves one squaring step (`181,057,812`) for `124,876,887` and doubles the scan of 4.1.3 (`2^s * 448`); `s = 17` minimises the total.

Every map is exact; no premise is added to the time or the memory. The zero test of `k1` (4.3T) now concerns `g^(17)`: `g^(17)(y) = 0` for `y` in `O1` only if `g_c(x) = 0` for one of the `2^17` values `x` with `x^(2^17) = y` (in `F_p` or an extension); for each such `x`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g^(17) vanishes on O1) <= 2^17 n' (D - 1) / p = eps_g < 2^-196`.

### 4.3T Stage C in the value domain on truncated point sets (the method of bradcush `b30de9bf`/`a41aecdd`, 477 of 512 nodes)

Point sets. `N = 2^20` divides `p - 1` (2-adicity 32). Let `psi` have order `2^21`, `H_N = <psi^2>` and `Y = X^(2^11)`. `H_N` is the union of the 512 depth-9 nodes `{x : x^(2^11) = r_j}`, `r_j` the 512-th roots of unity in transform (bit-reversed) order; `O1` is the union of the first 477 nodes, `n' = 477 * 2^11 = 976,896 >= m + 1 = 976,563` points, and `O2` the same 477 nodes of the coset `psi H_N` (`x^(2^11) = r'_j`, `r'_j^512 = -1`), disjoint from `O1`. `P1 = prod_{j<477} (Y - r_j)` has degree `n'`, vanishes on `O1` and is the nonzero constant `P1(r'_j)` on node `j` of `O2`; `delta_j = 1/P1(r'_j)` (477 table constants).

Truncated transforms (bradcush `b30de9bf` 4.3, generalized as the truncated Fourier transform of van der Hoeven, ISSAC 2004). A polynomial of degree `< n'` is `sum_{k<512} P_k Y^k` with `deg P_k < 2^11` and `P_k = 0` for `k >= 477`; its values on the 477 nodes determine it and are determined by it (the CRT for the 477 coprime moduli `Y - r_j`, whose product `P1` has degree `n'`). The forward transform runs the top 4 layers on all `N/16` offsets, the middle layers only on the blocks above present nodes, and the bottom 4 layers on the `n'` points; the inverse runs the same layers in reverse. The dropped part `[477, 512)` is the maximal subtrees `{480..511}` (row 15 of the top pass, depth 4) and `{478..479}`, `{477}` (depths 8 and 9, inside row 14). Row 15 is never stored. Write `y_j(o)` for the residue of row `j` at offset `o < N/16` and `F_k(o)` for the coefficient at position `k N/16 + o`: `y_j(o) = sum_k F_k(o) r_j^k` over the 16 depth-4 roots `r_j` (the 16th roots of unity on `O1`, the 16 roots of `r^16 = -1` on `O2`), and `F_15(o) = 0` since the degree is `< n' <= 15 N/16`; so `sum_j r_j y_j(o) = 0` and `y_15(o) = sum_{j<15} c_j y_j(o)` with `c_j = -r_j / r_15`, the 16th roots of unity other than `-1`, one of them `1`. The top pass forms `y_15` in registers (14 multiplications by register constants and 14 additions, 28 per offset) and forms only the 15 nonzero chunks of the inverse and the 15 present rows of the forward (pruned 16-point butterflies: 94 and 92 field operations in place of 96). At the `6,144` offsets `o >= 59,392` the chunk `F_14(o)` is zero as well (`14 N/16 + o >= n'`); the two equations give `y_14(o) = sum_{j<14} alpha_j y_j(o)` with fixed constants `alpha_j` (the 2 x 2 system in `y_14`, `y_15` has determinant `r_14^-15 r_15^-15 (r_14 - r_15) != 0`), formed from the 14 complete rows before row 14 is finished (the tail solve: per offset 14 loads, 14 multiplications, 13 additions, one store and 5 of control, 62; the 14 constants loaded once per pass). From these residues the inverse recovers the subtrees `{477}` and `{478..479}` inside row 14 along their paths below the top pass (layers 4 to 8 and 4 to 7), charged 10 operations (3 multiplications, 3 additions, a load and a store) per point per layer, as bradcush recovers the one dropped node. The passes are fused as in `b30de9bf` 4.5, at radix 16 under the declared 64-word register file (4.2), the 20 layers split 4 | 4, 4, 4 | 4: a bottom pass (16-point blocks: forward layers, the pointwise map, inverse layers; one set of 15 twiddles for both directions, 19 operations per block: two loads from the two-level table, one multiplication, three squarings, eleven multiplications by register constants; `V^T V = 16 diag(1, cJ)` with `c = y^16` of the block, so every inverse bottom pass scales each block by `diag(1, c^-1 J)`: 15 multiplications and the factor `c^-1`; the blocks `m = 16 q + r` of an aligned group of 16 (the children of one depth-12 node) have `c_m^-1 = c_{16q}^-1 zeta^-bitrev4(r)`, so `c_{16q}^-1` is looked up once per group (the negated exponent, two loads, one multiplication: 6) and multiplied by a register constant per block (none for `r = 0`): 16 operations per block and 5 per group), three middle passes of radix 16 (per block 16 loads and 16 stores, one operation each with the base-plus-index address (4.2), 32 butterflies and 5 control, 133; the 15 twiddles of a group in registers, 24 per group), and a top pass over all `N/16` offsets that fuses the inverse top of one set with the forward top of the other (the 16 values, the 31 coset constants, the 14 constants `c_j != 1` and one temporary: 62 of the 64 registers; per offset 15 loads and 15 stores, one operation each (4.2), 28 for row 15, 94 for the inverse, 30 for the twist of the 15 nonzero chunks, 92 for the forward and 5 of control: 279; the unfused inverse top 157; the forward from coefficient form 127, a cleared register (1) in place of the load (1) at the 6,144 offsets whose chunk-14 position is at or above `n'`).

Montgomery powering (`b30de9bf` 4.5). For residues of degree `< n'`, `Mont(A, B) = (A B + u g)/P1` with `u = -A B / g mod P1` (`deg u < n'`); the division by `P1` is exact, `Mont(A, B) = A B / P1 mod g`, and `deg Mont(A, A) <= n' - 2`, so `X Mont(A, A)` has degree `< n'`. A residue `A` (representing `S^e P1`) is held by its values on `O1` and on `O2`, each up to a tracked scalar. One step: `U = A^2 k1` on `O1` (`k1 = -1/(N^3 g)` there; `u` is determined by its values on `O1`); `U` to `O2` (truncated inverse on `O1`, truncated forward on `O2`); `B2 = (A2^2 + U g) delta_j` on node `j` of `O2`, which is `Mont(A, A)` up to the tracked scalar because `P1 = 1/delta_j` there, times the point `x` when the exponent bit is 1; `B2` to `O1` (truncated inverse on `O2`, truncated forward on `O1`). No `1/N` is executed inside the steps (the scalars are tracked, 2 operations per step). On `O2` the algorithm holds `A2' = delta_j A2` and `g~ = delta_j^2 g`: then `B2' = A2'^2 + U g~ = delta_j^2 (A2^2 + U g) = delta_j B2`, which is the next `A2'` (times `x` on a 1-bit), so no node factor is applied per point; the inverse bottom pass on `O2` scales each block by `diag(e, e c^-1 J)` with `e = delta_j^-1` (a block of 16 points lies in one node: one more multiplication per block, and per group of 16 blocks the load of `delta_j^-1` and its product with `c_{16q}^-1`, 3). Per point and step: on `O1` `sqr, LD k1, mul` (4); on `O2` `LD A2', sqr, LD g~, mul, add, ST` (9); 2 more for a 1-bit: `x = y zeta^e` from the base `y` of the block and a register constant (no multiplication for `zeta^0`) and the product `x B2'`.

Entry and exit. `g` (coefficients after the Graeffe prefix of 4.3G, its slots above `m` zero) goes to `O1` and `O2` (a truncated forward each, the scaling a running product fused into its first pass, 2 operations per point), then `g~ = delta_j^2 g` on `O2` (per node the load of `delta_j` and a squaring, per point a load, a multiplication and a store). The start residue is `A0 = X^v P1 mod g`, `v = 2^17 = 131,072` (VSHIFT = 2): `q = floor(X^v P1 / g)` has `ell = v + n' - m + 1 = 131,407` coefficients and is formed from the Newton reciprocal of the reversed `g` and one product (transforms of up to `3*2^17` points, with their own twiddle table, freed after the quotient); on node `j` of `O2`, `x^v P1(x) = r'_j^64 P1(r'_j)` is a constant, so `A0 = x^v P1 - q g` there is one truncated forward of `q` and one pointwise pass (8 per point); then `A0' = delta_j A0` (per node a load, per point 5) and `A0` goes to `O1` (its inverse on `O2` with `e = delta_j^-1`). `k1` is formed by chunked batch inversion on `O1` (chunks of `6,144` points, 159 chunks: prefix products, held in the scratch buffer of the stage, one inversion, two multiplications per point); each chunk product is tested for zero before its inversion (2 per chunk), and a zero ends the trial: for fixed `x != 0`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g vanishes on O1) <= eps_g < 2^-196` for the transformed `g` (4.3G, 9.2). The exit is one step with multiplier 1 (`Mont(A, 1)`, forming `delta_j B2 = delta_j A2' + U g~` on `O2`, 11 per point with the load of `delta_j`) and two truncated inverses with their scaling (`e = delta_j^-1` for `R`, `e = delta_j^-2` for `g~`: one more squaring per group), which return `kappa R` (`kappa` the tracked scalar) and `g` in coefficient form; the gcd is scale-invariant, so stage D receives `kappa R - kappa`. There are `219` squaring steps (the exponent `(p-1)/2^18`, 4.3G), `45` of them also multiplying by `S`.

Exactness and memory. Every map above is exact (Montgomery products of polynomials of degree `< n'`, held bijectively by their values on 477 nodes); no premise is added to stage C. The live set of the stage is four arrays of `n'` words (`g~` on `O2`, `A2'` on `O2`, `A` on `O1`, `k1` on `O1`), the tables (`984 + 3,072` words: 30 constants, the 477 `delta_j` and the 477 `delta_j^-1`, the two-level root table), and one scratch buffer of `15 N/16 - n' = 6,144` words (zero-filled once) that extends the array being transformed to the positions of row 14 at or above `n'`, which the first middle pass (`983,040` positions), the tail solve and the recovered subtrees `{477}`, `{478..479}` use (one transform runs at a time, so the in-place schedule needs no other storage; row 15 exists only in registers inside the top pass), and which holds the prefix products of one batch-inversion chunk (`6,144` points). The step-by-step count is expanded in Appendix E.1 and totals **row C = 42,602,465,472** (section 6).

### 4.4 Stage D: the inversion-free half-gcd on three rows (bradcush `4bcabff8`)

`G = gcd(g, R - 1)` is computed by bradcush's inversion-free half-gcd (entry `4bcabff8`, read as text only; ported and charged in this cost model). Matrices and remainders are kept up to scalars with pseudo-division (`b^2 a = Q b + e`, `Q` of degree 1 on the normal sequence), so no field inversion runs inside the recursion. A node of budget `k = 2^j - 1` makes two child calls of budget `2^(j-1) - 1`; with `n = 2^(j-1)` and `Y = X^n` its products run on the rows `Y - 1`, `Y + 1`, `Y - i`, each a power-of-two transform of `n` points after a twist, evaluated by the conservative per-block pass of Appendix E.2.1: `(c, d) = adj(M1)(a, b)` on the top window on all three rows (`3n` points, 3-row CRT), the pseudo-division, and the product `M = M1 [[Q, 1], [b^2, 0]] M2` on the two rows `Y - 1`, `Y + 1` only (`2n` points; 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` with the `1/2` folded into the `1/n` of the inverse, 10 operations per point). The product needs no third row: on the normal sequence every quotient has degree 1 and `b^2` is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; the row `Y - 1` values of each child's matrix are returned by the child, the row values of `M1` are kept from the apply and reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). The base case (budget 63) runs two remainder steps per pass over its window (the second reads the first remainder from registers). The driver calls `hgcd(a, b, k)` on the top window with `k = 2^j - 1 <= 2^16 - 1` the largest with `2k + 1 <= deg a`, applies the returned matrix to the whole pair in place by the cheapest of three transforms (the truncated set `O1` of 4.3T with its root table, `2^a` or `3 * 2^a` points; the matrix entries row-wise in rows of `2^16` when the transform has at least `2^17` points), and repeats; below degree `2 * 63 + 1` classical division steps finish and `G` is normalised. Every working array of the half-gcd lives in one bump arena (an allocation or release is 10 operations) of `1,048,320` words, the peak of the recursion and of the applies.

Charges (Appendix E.2): field operation 1, load or store 2, loop control `3 n + 2`, the passes of section 4.2 for the row transforms, the truncated transforms of 4.3T for an apply on `O1`; the twist of a row and the `1/n` of an inverse are running products fused into the adjacent loop (2 operations per point, 1 for `1/n` alone). Appendix E.3 lists the outer steps with their budgets, charges and apply plans: 28 outer steps (13 at `k = 65,535`) and the classical tail from degree 206. On the normal sequence every length, budget and allocation is a function of `m` alone.

The row is charged for the normal remainder sequence (every quotient of degree 1), the case of the premise `H-NORMAL` (9.5): every division tests that its quotient has degree 1 and every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter (2 operations each), and a zero remainder met inside `hgcd` or in the classical tail also ends the trial; on any other case the trial ABORTs (section 6.3). By the prefix lemma of 6.3 every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, so the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The total is **row D = 13,670,789,186** (section 6.3, 6).

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G = gcd(g, R - 1)`, whose roots are the values `y = S^(2^17)` of the usable roots `S` of `g_c` (4.3G); stage F stops only at an `s != 0` with `F(c + s) = F(c - s)` (4.1.3), so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Ledger: operation count (primitive operations; `C(3) = 279`)

| row | what is charged | operations |
| --- | --- | --- |
| init | constants and bookkeeping (once; no twiddle table, 4.2) | 17,987 |
| setup | the line (`line_setup`, once) | 4,910 |
| A (per trial) | stage bookkeeping, loop test and update, the coin draw (63, two words), one allocation | 1,228 |
| B (per trial) | `3,145,728` evaluations of `F` at `155 + 21 r = 218` counted operations each (section 3), the loop work, the twiddle table and the inverse transform of size `1,572,864`, the normalisation | 1,075,093,735 |
| C (per trial) | the Graeffe prefix, 17 steps (section 4.3G), then `S^((p-1)/2^18) mod g` in the value domain on the truncated point sets `O1`, `O2` (477 of 512 nodes, `n' = 976,896`), VSHIFT = 2, 219 squaring steps, radix-16 passes, the dropped row formed in the top pass, `A` on `O2` held as `delta_j A` (section 4.3T); expanded in Appendix E | 42,602,465,472 |
| D (per trial) | inversion-free half-gcd of `(g, R - 1)` on three rows, the product step of each node on two (4.4), charged for the normal remainder sequence with the quotient and return tests (sections 4.4, 6.3); expanded in Appendix E | 13,670,789,186 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16`, each with one draw of 63 (two words) | 166,081,821 |
| F (per trial) | the `2^18`-th root of `y` (18 square roots at 47,012), the scan of at most `2^17` candidates at 448 and its exit, the back-map 47,012 (4.1.3) | 59,613,486 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 279 + 32` | 6,612 |
| trial-loop (per trial) | trial-loop bookkeeping (12) and the allocator reset after an ABORT (1,000), charged in every trial | 1,012 |
| plan_invN misses | one per distinct plan size | 77,225 |
| output rows | the fixed output rows (stages H and I) | 3,390,080 |
| offline | constant derivation plus the 800-plan exhaustive audit (section 6.2, Appendix E.2.2) | 81,000,000 |
| **N_max** | `T_fixed + 1 * T_trial + T_off` | **57,658,542,754** |

`T_off = 81,000,000`; `T_trial = A + B + C + D + E + F + G + trial-loop = 57,574,052,552`; `T_fixed = init + setup + plan_invN misses + output rows = 3,490,202`; `K = 1`, so `N_max = 3,490,202 + 57,574,052,552 + 81,000,000 = 57,658,542,754`. `log2(N_max / 279) = 27.62269401206413...`, rounded up at five decimals to `27.62270`. Rows C and D are expanded part by part in Appendix E (E.1, E.2) from the dimensions of 4.3T and the half-gcd levels with the kernel charges of 4.2; the parts add up exactly to `42,602,465,472` and `13,670,789,186`.

### 6.1 Validation
The kernel charges and the allocator rules are those compared with the instrumented totals of our executed runs at `r = 3, 4, 5` (the arena rule within 64 bytes of the measured heap peaks there); the truncated-set stage C (4.3T) and the stage D of 4.4 have no executed counterpart, and their counts are the formulas of Appendix E.

### 6.2 Offline derivation
The literals of the sources (Montgomery forms of the organizer constants, `5^q`, `2^65`, the exponent `(4(p-1)+1)/5`) are derived offline in at most `1,000,000` operations. The exhaustive planner of Appendix E.2.2 evaluates 800 plans at 100,000 operations each. The total is `81,000,000`, declared `preprocessing_log2 = 26.27142` rounded up and included once inside `N_max`. The planner streams two records and uses less than 4 KiB, below the online memory peak; it leaves no nonuniform advice.

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry `e6dcb600`)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g, R - 1)`, `g = g_c^(17)` (4.3G): every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the pseudo-division of a node, each step of the base case and of the classical tail) tests, before it does any work beyond reading the two leading coefficients, that its quotient has degree 1 (2 operations); (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); a zero remainder inside `hgcd` or in the classical tail also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state at the start of the trial (`1,000` operations, charged in every trial). Lemma (prefix; `e6dcb600`, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each node calls its children with budget `2^(j-1) - 1` and, with every quotient of degree 1, every degree in the tree is fixed by `m` and the number of quotients so far, and the budgets of the outer loop (`k` the largest `2^j - 1 <= 2^16 - 1` with `2k + 1 <= n`, section 4.4) are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's `hgcd` calls produce has degree above the classical tail, so every gcd of degree at most `DMAX = 16` first appears in the classical tail (from degree 206); a zero remainder earlier ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The charging follows `e6dcb600` and the half-gcd follows `4bcabff8`, both read as text only (no entry script was run, compiled or imported). Appendix E.2 expands, for `r = 3`, the charge of stage D for the normal sequence with the tests, `13,670,789,186`, part by part.

The `r = 3` trial (`~126 MB`, `~5.8e10` operations) exceeds the organizer sandbox (128 MiB, 20 s), so the costs are the exact formula counts of sections 6 and 7; zero-fill clearing is charged (ruling `3476cad8`) and the 64-word register file is the machine restriction of claim.json.

## 7. Memory: the arena of one trial

The arena is the capacity of the allocator of 4.2 on the allocation/free sequence of the trial. Appendix E.3 runs the allocator on every allocation and free of the trial in the order of the program and reports the two-ended-pool high-water mark (the largest sum of the extents of the two ends over the trial), the slab area and the peaks of the live set per stage. The two-ended pool takes the blocks of more than `2^10` bytes. The Graeffe prefix (4.3G) holds `E` and `O` on `O1` in the arrays of `A` on `O2` and on `O1` before stage C fills them, with a scratch of `6,144` words that it frees: it adds no array and leaves the high-water mark unchanged. Its high-water mark is reached in stage C: `125,369,472` bytes (the four arrays of `n'` words of 4.3T, the scratch of `6,144` words, which also holds the prefix products of one batch-inversion chunk, and the table block of `984 + 3,072` words: the 30 constants, the 477 `delta_j`, the 477 `delta_j^-1` and the two-level root table), plus 128 bytes so the unused middle is always at least 128 bytes. Stage D holds `g`, `R`, the table block of stage C (`984 + 3,072` words, freed by stage D), its twiddle table (`2^18` words) and the bump arena of the half-gcd (`1,048,320` words, 4.4); under the H-NORMAL ABORT these are the normal-case arrays, and a trial with any other sequence ends after a prefix of these allocations (6.3), so the normal-case walk bounds every trial. The stage-D live peak is `104,586,304` bytes, below the stage-C peak. No block of `2^10` bytes or less is live in stages A to D (slab area 0). Stages E and later hold at most 16 small arrays and the free-list heads: `16,896` bytes. The arena is `125,386,496` bytes (two-ended pool `125,369,472 + 128`, stages E and later `16,896`). Peaks of the live set per stage (bytes): A `31,260,736`; B `89,981,120`; C `125,369,472`; D `104,586,304`. With `407,440` bytes of code and static data (`399,216` of code, `32` of initialised data and the `8,192`-byte output buffer; every table of the algorithm is a block of the arena, built at run time and charged in its stage, so no table is static) and a `65,536`-byte stack, the footprint is `125,859,472` bytes `= 2^26.9072...`, `26.908` rounded up at three decimals. No stored advice; each twiddle table is built at run time by the stage that uses it and charged in that stage's row (4.2).

## 8. Review points, answered by location

1. Row D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (6.3): by the prefix lemma every trial executes a prefix of the normal-case work, so the time and memory bounds hold for every sequence; `H-NORMAL` (9.5) enters only the success probability.
2. Stage D (4.4) is listed outer step by outer step in Appendix E.3 (budget, half-gcd charge, apply charge and plan); its bump arena (`1,048,320` words) is a block of the allocation walk, and its live peak (`104,586,304` bytes) is below the stage-C peak, the high-water mark of the trial.
3. Row B reproducible from sections 3 and 6 (evaluations * 218 counted operations + the loop work, the twiddle table and the inverse transform + normalisation). The 64-word register file (the machine restriction of claim.json, 4.2) is the only register assumption; every value beyond it is charged as a load or store.
4. Offline work is 81,000,000 operations: 1,000,000 for constants and 80,000,000 for all 800 planner points (`preprocessing_log2 = 26.27142`), included once in `N_max` (6.2, E.2.2).
5. The mem penalty uses the rounded-up `mem_log2`, a self-penalizing over-charge.
6. `success = q - delta - eps_coin - eps_iso - eps_g >= 0.39` from the premises `H-ONE` and `H-NORMAL` (9.2, 9.5) with `K = 1`, `q = 0.3931`, `delta = 0.003`; the value is `0.390099999999997628`. The `H-ONE` allowance below the law value is stated exactly (`0.3934693 - 0.3931 = 0.0003693`; `q <= 151/384 = 0.3932292`, the four-moment Bonferroni bound, 9.1), and `delta = 0.003` is the declared premise; the 3,072 organizer-seeded sequences are reproducible observations consistent with it (10.5.1).
7. The organizer-checkable output is the returned witness-pair count; the premises hold under trusted execution of the submitted program, disclosed, not claimed as an organizer-verified proof.
8. The Graeffe prefix (4.3G) is exact and adds nothing to the premises of the time or the memory; the success bound uses `H-NORMAL` stated for the pair of the transformed polynomial (9.5), whose organizer-run tests compute that pair (10.5.1).

## 9. The premise and the success bound

### 9.1 H-ONE
The number of centres `c` with `1 <= k(c) <= 16` is at least `q p = 0.3931 p`, `k(c)` the number of nonzero squares `S` with `g_c(S) = 0` (stage D returns `G` with `1 <= deg G <= k(c)` when `k(c) >= 1`, 4.3G). The premise states `q = 0.3931`, the law value `1 - e^(-1/2) = 0.3934693` (9.3) less the extrapolation allowance stated exactly as `0.0003693`; it is also `0.0001292` below the four-moment Bonferroni bound `151/384 = 0.3932292`. The split of the allowance between `H-ONE` and `H-NORMAL` follows cryptogakusei's entry `4888e783`: with `delta = 0.003` (9.5) the bound of 9.2 needs `P(E_c) >= 0.3931` at `K = 1`. The extrapolation, the monodromy theorem at N = 2, 3 and the toy-field and organizer-run evidence are in the claim.json heuristic `H-ONE` and sections 10.3, 10.5.1.

### 9.2 The success bound
The centre is a fresh draw. For a centre `c` let `E_c` be the event `1 <= k(c) <= DMAX` (H-ONE, `P(E_c) >= q = 0.3931`) and `N_c` the event that the remainder sequence of `(g, R_c - 1)` (`g = g_c^(17)`, 4.3G) is normal down to its gcd (H-NORMAL, 9.5, `P(not N_c) <= delta = 0.003`). The Graeffe prefix and the value-domain stage C reproduce `g^(17)` and `R = S^((p-1)/2^18) mod g^(17)` exactly (4.3G, 4.3T) and add no premise; stage C needs `g^(17)` nonzero on `O1`, which fails with probability at most `eps_g = 2^17 n' (D - 1) / p < 2^-196` over the centre (4.3G). If `E_c` and `N_c` hold and `g^(17)` has no zero on `O1`, stages C and D run to their end and return `G = gcd(g^(17), R_c - 1)` with `1 <= deg G <= DMAX` (4.3G); a successful isolation and the scan of 4.1.3 then end in a verified collision. For `c` uniform `P(E_c and N_c) >= q - delta`, so with one centre (the event `g^(17)` zero on `O1` subtracted as `eps_g`)

`success = 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g`, `K = 1`.

Transfer to the written sampler (F-EVAL-001): `q - delta - eps_iso - eps_g` bounds the success probability of the run whose draws are exactly uniform on `F_p` (the premises and the isolation lemma are stated for uniform draws). The success of a run is an event of the vector of its draws, and the actual draws of 4.1.1 are within total variation `eps_coin` of the uniform vector, so the actual success probability is at least the ideal one minus `eps_coin`.

With `q = 0.3931`, `delta = 0.003`, `eps_iso <= 2.371e-15`, `eps_coin <= 1.404e-76`, `eps_g < 2^-196`: `q - delta = 0.3901`, and the value is `0.390099999999997628 >= 0.39`. The bound stays at or above `0.39` for every `delta <= 0.0030999` at `q = 0.3931`. The probability is over the random words of 4.1.1 for the fixed target, not over targets and not a sampled frequency.

### 9.3 Monodromy (support for H-ONE)
The roots of `G(c,t) = g_c(t^2)` come in pairs `+-t_i`, so the monodromy lies in the hyperoctahedral group `B_m` and `k(c)` counts positive Frobenius fixed points; for `B_m` this is Poisson(1/2) in the limit, `P(k >= 1) = 1 - e^(-1/2) = 0.3934693`, and Bonferroni at order 4 gives `P >= 151/384 = 0.3932292`. A theorem at two and three layers (Aubry-Perret, monodromy `B_12`, `B_62`); false for permutation polynomials, for decomposable `F` with imprimitive monodromy, and at one layer.

### 9.4 Isolation lemma
With `1 <= deg G <= 16`, a random-shift split isolates a linear factor within `Z = 64` rounds except with probability `eps_iso <= 2.371e-15`. Finite derivation: `G` divides `Y^((p-1)/2^18) - 1` (4.3G), a divisor of `Y^(p-1) - 1`, so it is squarefree and splits into `d = deg G <= 16` distinct linear factors `X - t_i` over `F_p`. A round with shift `a` keeps a nontrivial part of the current factor `H` under `gcd(H, (X + a)^((p-1)/2) - 1)` (or `X + a` itself when `a = -t_i`), so two roots `t_i != t_j` stay together only if `chi(t_i + a) = chi(t_j + a)` or `a` is in `{-t_i, -t_j}`. Since `sum_a chi((a + t_i)(a + t_j)) = -1` for `t_i != t_j`, exactly `(p - 3)/2` shifts give equal nonzero characters, so for `a` uniform on `F_p` the pair stays together with probability at most `((p - 3)/2 + 2)/p = 1/2 + 1/(2p)`; each shift is a fresh random word reduced mod `p`, within statistical distance `2^-128` of uniform (4.1.1), so per round the bound is `1/2 + 2^-127`, independently across rounds. The parts are nested, so the factor kept after 64 rounds holds two roots only if one of the at most `C(16,2) = 120` pairs was never separated in 64 rounds. By the union bound `eps_iso <= 120 (1/2 + 2^-127)^64 < 6.6e-18 <= 2.371e-15`; the looser stated value `2.371e-15` is kept, so every other number is unchanged.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries `e6dcb600` and `1aa56884`; allowance split of cryptogakusei's `4888e783`; organizer-run tests in the form of gta6rp's `bef31fdd`)
**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(h_c, R_c - 1)`, where `h_c = g_c^(17)` is the 17-fold Graeffe transform (4.3G) of the monic odd part `g_c` of section 3 (monic, degree `m = 976,562`) and `R_c = S^((p-1)/2^18) mod h_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.003` (`2^-8.38`). Stage D is charged for the normal sequence; every division tests its quotient degree and every call of the half-gcd its return, and on any other case the trial ends (ABORT, sections 4.4, 6.3). The premise enters only the success probability (9.2): the time and memory bounds hold for every remainder sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work (6.3). For a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes, each a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-213`; the premise extrapolates a much weaker form of this random-pair behaviour (`delta = 0.003`) to the structured pair `(h_c, R_c - 1)`. Measured support is organizer-run (10.5.1): the six experiments `euclid-normal-n2-t256-l2-g17-a` to `-f` compute the complete Euclidean sequence of `(h_c, R_c - 1)` for this construction (17 Graeffe steps, exponent `(p-1)/2^18`) on the truncation `F_2` (`m = 12`) for 256 organizer-seeded trials of two centres each (3,072 sequences in all) and return a witness pair exactly when both sequences of a trial are normal; `euclid-normal-n3-t24-g17` and `euclid-normal-n4-t2-g17` do the same at `m = 62, 312`. The prediction is that every computed sequence is normal. Zero abnormal in the 3,072 sequences is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (`delta = 0.003` is the declared premise). Not verified at `r = 3`, which would need the computation itself; the organizer-run tests are at `m = 12` to `312`, far below `m`.

## 10. Experiments

Program `experiments/exp_euclid.py` (euclid-normal, one-centre) and `experiments/exp_line.py` / `experiments/exp_lowbits.py` (line-ladder and lowbits-birthday), with `experiments/manifest.json`.

10.3 The truncations. `F_N(c + X)` is coordinate 0 after the first `N` S-box layers on the line `j = 0`; `F_2`, `F_3`, `F_4` have odd parts of degree `m = 12, 62, 312`. The arithmetic monodromy at `N = 2, 3` is `B_12`, `B_62` (Grok jobs 136, 137, re-run on the deployed constants).

10.5.1 Organizer-run set. euclid-normal-n2-t256-l2-g17-a to -f compute the complete Euclidean sequence of `(h_c, R_c - 1)` (the pair of 9.5: 17 Graeffe steps, exponent `(p-1)/2^18`) for this construction at depth `N = 2` (`m = 12`), each for 256 organizer-seeded trials of two centres (512 sequences per entry, 3,072 in all; the final letter only changes the organizer seeds); euclid-normal-n2-t256-g17, -n3-t24-g17 and -n4-t2-g17 compute one sequence per trial at `m = 12, 62, 312`. A trial returns a witness pair exactly when its sequences are normal; the prediction (H-NORMAL, 9.5) is that every trial returns a pair, so the abnormal count is zero, a reproducible observation consistent with the premise. We do not treat the organizer-seeded centres as independent unselected samples and draw no population bound from these runs: `delta = 0.003` is the declared premise (9.5), carried by its stated support, not by an interval computed from the experiments. one-centre-n2-t256 and one-centre-n3-t24 run one trial of the algorithm with the Graeffe prefix off (`s = 0`: the gcd against `S^((p-1)/2) - 1` and a square root in place of the scan; they test `H-ONE`, a statement about `g_c` that the prefix does not change, 4.3G) at depth `N = 2, 3` per organizer seed and return a witness pair exactly when the sequence is normal, `1 <= k(c) <= 16` and the isolated root gives a verified collision of `F_N`, with expected count about 0.393469 T under H-ONE (9.1), reported as an observation with no interval inferred. line-ladder-w6/-w8/-w10/-w12 and lowbits-birthday corroborate the antipodal structure (random-function model), not the score-critical basis. Our runs of the six -l2-g17 entries with local seeds (one CPU; 9.59 to 10.36 s each on our workstation): 3,072 sequences, all normal, 256 pairs per entry; the gcd had positive degree for 1,205 of the 3,072 centres (0.392). Our runs of -n2-t256-g17, -n3-t24-g17 and -n4-t2-g17: 256, 24 and 2 sequences, all normal. The organizer-checkable output is the returned witness-pair count; the premises H-ONE and H-NORMAL hold under trusted execution of the submitted program.

## Appendix E: rows C and D expanded, and the allocation walk of one trial

Rows C and D and the arena of section 7 are exact counts of the algorithm of sections 4.2-4.4 at `r = 3`. E.1 and E.2 expand each row into its parts, each part a count from the dimensions of 4.3G, 4.3T and the half-gcd levels with the charges of 4.2; each table adds up exactly to its row. E.3 is the output of our counting program for one trial: the outer steps of stage D, the stage totals, the live-set peaks per stage, the two-ended-pool high-water mark and the arena, the allocator of 4.2 run on every allocation and free of the trial in program order.

### E.1 Row C = 42,602,465,472

Row C is the sum of the steps of section 4.3T in the order the stage runs them:

| part of stage C | operations |
| --- | ---: |
| plans of the passes, the exponent, the tables (`30` constants, the `477` `delta_j` and `477` `delta_j^-1`, the `3,072`-word root table, built), the zero-fill of `g` above `m` | 5,812,379 |
| the allocation of `A` on `O1`; the Graeffe prefix (4.3G): `17` steps (below), the allocation, zero-fill and free of its `6,144`-word scratch | 2,122,922,387 |
| the Newton reciprocal of the reversed `g` to `ell` coefficients (doubling steps, block-form products) | 208,613,776 |
| the product `q = floor(X^v P1 / g)` (one product of `2 ell - 1` points) and its copy | 66,813,424 |
| `g` to `O1` and `O2` (two scalings, two truncated forwards; the `6,144`-word scratch allocated and zero-filled once) | 88,198,947 |
| `g~ = delta_j^2 g` on `O2` (per node 3, per point 5) | 5,258,450 |
| the start residue `A0` on `O2` (zero-fill, scaling, truncated forward of `q`, pointwise pass at 8) | 54,281,444 |
| `A0' = delta_j A0` on `O2` (per node 2, per point 5) | 5,257,973 |
| `A0` to `O1` (truncated inverse on `O2` with `e = delta_j^-1`, scaling, truncated forward) | 89,916,096 |
| `k1` on `O1` by chunked batch inversion (159 chunks of `6,144`, zero tests) | 14,834,543 |
| the squaring steps (step 6; below) | 39,736,833,948 |
| the exit step `Mont(A, 1)` (pointwise passes at 7 and 11, one extension), the frees | 108,160,650 |
| two truncated inverses with scaling (`R` with `e = delta_j^-1`, `g` with `e = delta_j^-2`), the free of the scratch, the closing control | 95,560,455 |
| stage bookkeeping (entry, exit) | 1,000 |
| **row C** | **42,602,465,472** |

The squaring steps: `174` steps with exponent bit 0 and `45` with bit 1, `174 * 181,057,812 + 45 * 182,950,548 = 39,736,833,948`. One step (4.3T) is:

| part of one step (bit 0) | operations |
| --- | ---: |
| bottom pass on `O1` (`U = A^2 k1`, 4 per point) | 20,045,468 |
| two inverse middle-pass sets, 24,538,700 each | 49,077,400 |
| two forward middle-pass sets, 24,534,332 each | 49,068,664 |
| two fused top passes (inverse top with row 15 formed in registers, coset twiddle, forward top), 18,284,688 each | 36,569,376 |
| bottom pass on `O2` (`B2' = A2'^2 + U g~`, 9 per point; `delta_j^-1` in the block scaling) | 25,002,452 |
| two tail solves of row 14 (`6,144` offsets), 380,976 each | 761,952 |
| two recoveries of the subtrees `{477}`, `{478..479}` inside row 14, 266,240 each | 532,480 |
| step control | 20 |
| **one step, bit 0** | **181,057,812** |

A step with bit 1 adds 2 per point of `O2` in its bottom pass (`x = y zeta^e`, `x B2'`), less the `61,056` blocks whose point `zeta^0 y` is `y`: `182,950,548 - 181,057,812 = 1,892,736 = 2 * 976,896 - 61,056`.

The Graeffe prefix (4.3G): `17` steps of `124,876,887` each, `2,122,907,079`; with the allocation of `A` on `O1` and the allocation, zero-fill and free of the scratch of the prefix, `2,122,922,387`. One Graeffe step (`gt2_step`) is:

| part of one Graeffe step | operations |
| --- | ---: |
| two pruned forward top passes (the 15 present rows), `E` and `O` read from `g` at stride 2 (`tr_top_half`) | 12,472,335 |
| three middle-pass sets (forward `E`, forward `O`, inverse), 24,534,332, 24,534,332, 24,538,700 | 73,607,364 |
| fused bottom pass (forward bottom layers of `E` and `O`, `G = (E^2 - y O^2)/N` at 5 per point, inverse bottom layers with the block scaling) | 27,860,636 |
| inverse top pass with row 15 formed in registers (stores into `g`) | 10,289,296 |
| tail solve of row 14 and recovery of the subtrees `{477}`, `{478..479}` | 647,216 |
| step control | 40 |
| **one Graeffe step** | **124,876,887** |

### E.2 Row D = 13,670,789,186

The Euclid driver of 4.4, with the block-form node charge derived in E.2.1, makes 28 outer steps, each one `hgcd` call of budget `k` on the top window and the apply of its matrix to the whole pair; E.3 lists each step. Row D is:

| part of row D | operations |
| --- | ---: |
| the half-gcd calls of the 28 outer steps (E.3, `hgcd` column, each with its call) | 10,059,015,349 |
| the applies of their matrices to the whole pair (E.3, `apply` column) | 3,609,324,970 |
| the classical tail from degree 206 with the quotient tests, the inversion of the leading coefficient and the normalisation of `G` | 349,351 |
| stage frame: entry, the twiddle table of its transforms (built), the bump arena of `1,048,320` words, the frees of the arena, the tables and the arrays of stage C | 2,099,516 |
| **row D** | **13,670,789,186** |

#### E.2.1 The two-row block-form node `node_bf(j)`

This subsection derives every replacement node integer used by this entry. It does not import a node column from another submission. The algorithm remains the base entry's two-row product: a node of budget `2^j-1` makes two child calls of budget `2^(j-1)-1`, applies `adj(M1)` on the three rows `Y-1`, `Y+1`, `Y-i`, performs the pseudo-division, and forms `M = M1 [[Q,1],[b^2,0]] M2` on the two rows `Y-1`, `Y+1`. Only the row-transform implementation changes. It uses the block-form pass published by Jbenisek in `27fbfbe7-a1b5-4b85-8303-8e893d41117a` section 4.2, credited for the construction and for no integer here, with every block charged as though it forms its own twiddles. The real schedule shares twiddles, so this is a conservative per-block reading. The recurrence then adds a declared one per cent allowance.

Let `n=2^(j-1)` and `a=j-1`. Split `a` into consecutive blocks `(l0,k)` of width four, with a final width from one through four. The charge of one transform is

```
F(a) = sum P(a,l0,k),
P(a,l0,k) = 150 k
             + 2^(a-k) (2^k + 4)
             + 2^(a-k) (2*2^k + 3 k 2^(k-1) + 5).
```

The first term builds the block twiddles. The second charges block setup and indexing. The third charges loads, stores, butterflies and loop control. Re-forming each block's twiddles is no cheaper than the shared schedule.

Define `lc(l)=3l+2`, `cp(l)=4l+lc(l)`, `zf(l)=2l+lc(l)`, `ac(l,u)=(7+u)l+lc(l)`, and `pw(n,r)=3 floor(n/8)+3+(7 if r=0 else 10)n`. A row transform on `L` coefficient positions is

```
row(L,r) = cp(min(L,n)) + zf(max(0,n-L))
           + ac(max(0,L-n), [r=2]) + 2n [r>0] + F(a).
```

The base case is recomputed from its two remainder steps per pass:

```
pd(6) = 90
        + sum_{s=0,2,...,60} [76 + 13L + 9(L-2) + lc(L)
                              + 2(13(s+2)+9(s+3)+lc(s+3)) + 8]
        + [25 + 13 + lc(1) + 2(13*64+lc(64)) + 4]
      = 105,140,
where L = 2(62-s)+1.
```

For `j>=7`,

```
pd(j) = 184 + 2 pd(j-1) + top + returns + apply + matrix
        + inverse + crt + pseudo + arrays,
top     = sum_(r=0)^2 [row(2^(j+1),r)+row(2^(j+1)-1,r)],
returns = 8(row(n,0)+row(n,1)) for j=7, and 8 row(n,1) for j>=8,
apply   = 6(pw(n,0)+pw(n,2)),
matrix  = 8(pw(n,0)+pw(n,1)),
inverse = 6 sum_(r=0)^2 [F(a)+(1+[r>0])n],
crt     = 4(10n+lc(n)),
pseudo  = 30+13(2^j-1)+lc(2^j-1),
arrays  = 2(25n+lc(n)),
node_bf(j) = ceil(101(pd(j)+10)/100).
```

The `184` is entry, tests and control; `+10` is allocation control. The three-row apply and inverse terms remain three-row. The returned values, matrix product, CRT and arrays are two-row terms. The `j=7` return charges both rows because its children are coefficient-only base cases.

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

The columns plus 184 add exactly to `pd(j)`. The schedule uses the levels `{7: 2, 8: 1, 9: 2, 10: 2, 11: 1, 12: 1, 13: 2, 14: 2, 15: 2, 16: 13}` and therefore charges

```
sum count(j) node_bf(j) = 10,059,015,349.
```

The required top window has `L(j)=2^(j+1)-1` coefficients. The shortest actual second operand at every used level bounds it:

| j | `L(j) = 2^(j+1)-1` | shortest operand | check |
|---:|---:|---:|:---:|
| 7 | 255 | 332 | yes |
| 8 | 511 | 714 | yes |
| 9 | 1,023 | 1,225 | yes |
| 10 | 2,047 | 2,759 | yes |
| 11 | 4,095 | 5,829 | yes |
| 12 | 8,191 | 9,924 | yes |
| 13 | 16,383 | 18,115 | yes |
| 14 | 32,767 | 42,689 | yes |
| 15 | 65,535 | 91,839 | yes |
| 16 | 131,071 | 190,141 | yes |

The unchanged outer applies and their base plans are shown with both node columns for auditability:

| step | degree n | j | k | old node | `node_bf(j)` | outer apply | total |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 976,562 | 16 | 65,535 | 709,315,821 | 690,004,574 | 416,312,974 | 1,106,317,548 |
| 2 | 911,027 | 16 | 65,535 | 709,315,821 | 690,004,574 | 416,968,324 | 1,106,972,898 |
| 3 | 845,492 | 16 | 65,535 | 709,315,821 | 690,004,574 | 381,080,816 | 1,071,085,390 |
| 4 | 779,957 | 16 | 65,535 | 709,315,821 | 690,004,574 | 379,664,574 | 1,069,669,148 |
| 5 | 714,422 | 16 | 65,535 | 709,315,821 | 690,004,574 | 379,664,654 | 1,069,669,228 |
| 6 | 648,887 | 16 | 65,535 | 709,315,821 | 690,004,574 | 379,664,538 | 1,069,669,112 |
| 7 | 583,352 | 16 | 65,535 | 709,315,821 | 690,004,574 | 238,587,530 | 928,592,104 |
| 8 | 517,817 | 16 | 65,535 | 709,315,821 | 690,004,574 | 237,470,930 | 927,475,504 |
| 9 | 452,282 | 16 | 65,535 | 709,315,821 | 690,004,574 | 190,728,122 | 880,732,696 |
| 10 | 386,747 | 16 | 65,535 | 709,315,821 | 690,004,574 | 189,311,634 | 879,316,208 |
| 11 | 321,212 | 16 | 65,535 | 709,315,821 | 690,004,574 | 118,967,606 | 808,972,180 |
| 12 | 255,677 | 16 | 65,535 | 709,315,821 | 690,004,574 | 89,653,002 | 779,657,576 |
| 13 | 190,142 | 16 | 65,535 | 709,315,821 | 690,004,574 | 59,944,058 | 749,948,632 |
| 14 | 124,607 | 15 | 32,767 | 319,630,037 | 313,185,629 | 45,830,694 | 359,016,323 |
| 15 | 91,840 | 15 | 32,767 | 319,630,037 | 313,185,629 | 27,024,280 | 340,209,909 |
| 16 | 59,073 | 14 | 16,383 | 142,528,601 | 140,767,931 | 22,498,676 | 163,266,607 |
| 17 | 42,690 | 14 | 16,383 | 142,528,601 | 140,767,931 | 13,137,208 | 153,905,139 |
| 18 | 26,307 | 13 | 8,191 | 62,652,075 | 62,357,608 | 11,127,232 | 73,484,840 |
| 19 | 18,116 | 13 | 8,191 | 62,652,075 | 62,357,608 | 4,916,260 | 67,273,868 |
| 20 | 9,925 | 12 | 4,095 | 27,543,067 | 27,747,929 | 2,424,472 | 30,172,401 |
| 21 | 5,830 | 11 | 2,047 | 11,917,539 | 12,177,349 | 1,354,326 | 13,531,675 |
| 22 | 3,783 | 10 | 1,023 | 5,044,695 | 5,235,579 | 1,162,198 | 6,397,777 |
| 23 | 2,760 | 10 | 1,023 | 5,044,695 | 5,235,579 | 655,350 | 5,890,929 |
| 24 | 1,737 | 9 | 511 | 2,066,017 | 2,175,255 | 577,898 | 2,753,153 |
| 25 | 1,226 | 9 | 511 | 2,066,017 | 2,175,255 | 251,906 | 2,427,161 |
| 26 | 715 | 8 | 255 | 836,909 | 895,023 | 160,802 | 1,055,825 |
| 27 | 460 | 7 | 127 | 321,859 | 345,791 | 120,994 | 466,785 |
| 28 | 333 | 7 | 127 | 321,859 | 345,791 | 63,912 | 409,703 |

Thus row D is `10,059,015,349 + 3,609,324,970 + 349,351 + 2,099,516 = 13,670,789,186`. The executable exact-integer derivation below recomputes the base case, every component above, all `L(j)` checks, the 28-step sum, the planner, `N_max`, logarithms and upward rounding.

#### E.2.2 Exhaustive planner and its charge

The planner enumerates Graeffe depths 0 through 19, half-gcd caps 7 through 16, and four allocator layouts: `20*10*4=800` complete plans. It streams the candidates, retaining only the current and best records, so its scratch is below 4 KiB and below the online peak. It is offline work, not resident advice. Every plan is charged 100,000 primitive operations for formula evaluation, score conversion, comparisons and checks, for 80,000,000 operations in addition to the base's 1,000,000-operation constant derivation. Therefore `T_off=81,000,000` and `preprocessing_log2=26.27142`, rounded up.

Here is an operation-level bound for one plan. Every ledger integer below is less than `2^64`; the largest comparison key below is less than `2^71`, so each value fits one 256-bit word. The evaluator expands multiplication by a small integer into shifts and additions. It groups a cap schedule instead of expanding every outer step: as the degree decreases, it crosses each of the ten budget levels and each of the 50 capacities `2^a`, `3*2^a` at most once, hence at most 60 groups. Division by `2^j-1` uses at most three shift-mask-add folds because the degree is less than `2^20` and `j>=7`.

| work for one plan | formulas evaluated | primitive 256-bit word operations |
|---|---|---:|
| node table | E.2.1 base case and `node_bf(7),...,node_bf(16)`: at most 96 operations for each of the 33 base-case iterations and at most 912 for each of ten higher nodes | 12,288 |
| general apply table | both capacities at each `a=1,...,25`; each of 50 candidates evaluates at most seven radix passes and the formula `32 T(a)+100 points+20,000`, with at most 256 shifts, additions, loads, stores, comparisons and branches | 12,800 |
| row D for the selected cap | at most 60 monotone budget/capacity groups; each group derives its repetition count, adds `count*node_bf(j)` and `count*apply`, and updates the degree, with both products expanded by at most 13 shift-add rounds | 11,520 |
| rows C and F | the depth-difference formula below, including `2^s`, the Graeffe term and the scan term | 128 |
| memory and total | select one of the four byte rows, then add `T_fixed`, the unchanged trial rows, row D, the depth difference and `T_off` | 128 |
| exact score key, checks and record | form `Q=N_max*max(2^20,memory_bytes)` by at most 28 shift-add rounds, compare `(Q,N_max,memory_bytes)`, check the bounds, and update the two retained records | 1,024 |
| **total** | | **37,888** |

The denominator `279*2^20` is the same for all plans, so comparing `Q` gives exactly the same order as comparing `log2(N_max/279)+max(0,log2(memory_bytes)-20)`. No logarithm is needed while selecting the plan. The decimal logarithms in E.2.3 print the audit values after the integer comparison. The declared charge of 100,000 therefore exceeds the operation-level bound by 62,112 operations per plan. Over 800 plans it remains the charged 80,000,000 operations; no ledger number changes.

At a depth `s`, the unchanged fixed-VSHIFT implementation changes the total by

```
(s-17)(124,876,887-181,057,812)
+ [(s+2)47,012 + 2^s*448 + 2]
- [19*47,012 + 2^17*448 + 2].
```

For each cap the driver greedily takes the largest fitting `2^j-1`. Cap 16 is the base's exact apply schedule in E.3. For caps 7 through 15 the planner uses the conservative general apply implementation: it enumerates every shortest capacity `2^a` and `3*2^a`, and charges `32 T(a)+100 points+20,000`, where each radix-at-most-16 full-row transform `T(a)` charges all loads, stores, butterflies, control and 24 twiddle operations per block. This is an implemented candidate, not a claim that a lower-cap specialized schedule cannot exist. All ten caps are evaluated; the requested search space is exhaustive for the implementations declared here.

The four layout byte counts are: exact two-ended walk 125,859,472; retain one additional 6,144-word scratch block 126,056,144; pad the four stage-C arrays to `2^20` words 135,034,512; and disjoint stage-C/stage-D pools 230,445,776. Code, static data, headers, the arena gap, late slabs and stack are included. The first layout wins; no runtime array is added by the block-form node. The original `6,144`-word transform/batch-inversion scratch and the `1,048,320`-word stage-D bump arena remain charged in section 7.

| Graeffe depth | best cap | best layout | `N_max` |
|---:|---:|---|---:|
| 0 | 16 | base-two-ended | 58,554,099,467 |
| 1 | 16 | base-two-ended | 58,497,966,002 |
| 2 | 16 | base-two-ended | 58,441,832,985 |
| 3 | 16 | base-two-ended | 58,385,700,864 |
| 4 | 16 | base-two-ended | 58,329,570,535 |
| 5 | 16 | base-two-ended | 58,273,443,790 |
| 6 | 16 | base-two-ended | 58,217,324,213 |
| 7 | 16 | base-two-ended | 58,161,218,972 |
| 8 | 16 | base-two-ended | 58,105,142,403 |
| 9 | 16 | base-two-ended | 58,049,123,178 |
| 10 | 16 | base-two-ended | 57,993,218,641 |
| 11 | 16 | base-two-ended | 57,937,543,480 |
| 12 | 16 | base-two-ended | 57,882,327,071 |
| 13 | 16 | base-two-ended | 57,828,028,166 |
| 14 | 16 | base-two-ended | 57,775,564,269 |
| 15 | 16 | base-two-ended | 57,726,770,388 |
| 16 | 16 | base-two-ended | 57,685,316,539 |
| 17 | 16 | base-two-ended | 57,658,542,754 |
| 18 | 16 | base-two-ended | 57,661,129,097 |
| 19 | 16 | base-two-ended | 57,722,435,696 |

| outer cap j | best depth | best layout | `N_max` |
|---:|---:|---|---:|
| 7 | 17 | base-two-ended | 3,642,875,193,984 |
| 8 | 17 | base-two-ended | 1,838,495,231,314 |
| 9 | 17 | base-two-ended | 942,423,720,464 |
| 10 | 17 | base-two-ended | 495,742,240,319 |
| 11 | 17 | base-two-ended | 273,197,409,227 |
| 12 | 17 | base-two-ended | 162,655,549,490 |
| 13 | 17 | base-two-ended | 107,928,494,959 |
| 14 | 17 | base-two-ended | 80,627,048,285 |
| 15 | 17 | base-two-ended | 67,435,505,057 |
| 16 | 17 | base-two-ended | 57,658,542,754 |

| layout | best depth | best cap | bytes |
|---|---:|---:|---:|
| base-two-ended | 17 | 16 | 125,859,472 |
| retained-scratch | 17 | 16 | 126,056,144 |
| full-point-arrays | 17 | 16 | 135,034,512 |
| disjoint-stages | 17 | 16 | 230,445,776 |

The unique best plan is depth 17, cap 16 and the exact two-ended base layout. Its trial is 57,574,052,552 operations. With `T_fixed=3,490,202` and `T_off=81,000,000`, `N_max=57,658,542,754`.

#### E.2.3 Exact-integer program

```python
#!/usr/bin/env python3
"""Exact r=3 block-form half-gcd replacement and bounded planner audit.

This file is deliberately self-contained.  The integers in the block-form
node column are recomputed from the charging formulas; none is copied from a
candidate package.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, getcontext
from math import ceil, log2

getcontext().prec = 80


def lc(length: int) -> int:
    return 3 * length + 2


def cp(length: int) -> int:
    return 4 * length + lc(length)


def zf(length: int) -> int:
    return 2 * length + lc(length)


def ac(length: int, subtract: bool) -> int:
    return (7 + int(subtract)) * length + lc(length)


def pw(length: int, row: int) -> int:
    return 3 * (length // 8) + 3 + (7 if row == 0 else 10) * length


def blocks(layers: int) -> tuple[tuple[int, int], ...]:
    out: list[tuple[int, int]] = []
    offset = 0
    while layers - offset >= 4:
        out.append((offset, 4))
        offset += 4
    if layers != offset:
        out.append((offset, layers - offset))
    return tuple(out)


def block_pass(layers: int, offset: int, width: int) -> int:
    del offset  # the conservative per-block charge depends only on the width
    batches = 1 << (layers - width)
    return (
        150 * width
        + batches * ((1 << width) + 4)
        + batches * (2 * (1 << width) + 3 * width * (1 << (width - 1)) + 5)
    )


def transform(layers: int) -> int:
    return sum(block_pass(layers, offset, width) for offset, width in blocks(layers))


def base_case_raw() -> int:
    total = 90
    for step in range(0, 62, 2):
        length = 2 * (62 - step) + 1
        total += (
            76
            + 13 * length
            + 9 * (length - 2)
            + lc(length)
            + 2 * (13 * (step + 2) + 9 * (step + 3) + lc(step + 3))
            + 8
        )
    length = 1
    total += 25 + 13 * length + lc(length) + 2 * (13 * 64 + lc(64)) + 4
    return total


@dataclass(frozen=True)
class Node:
    level: int
    children: int
    top: int
    returns: int
    apply: int
    matrix: int
    inverse: int
    crt: int
    pseudo: int
    arrays: int
    raw: int
    charged: int


_nodes: dict[int, Node] = {}


def node(level: int) -> Node:
    if level in _nodes:
        return _nodes[level]
    if level == 6:
        raw = base_case_raw()
        result = Node(level, 0, 0, 0, 0, 0, 0, 0, 0, 0, raw, raw)
        _nodes[level] = result
        return result

    n = 1 << (level - 1)
    layers = level - 1
    pass_charge = transform(layers)

    def row(length: int, row_index: int) -> int:
        return (
            cp(min(length, n))
            + zf(max(0, n - length))
            + ac(max(0, length - n), row_index == 2)
            + 2 * n * int(row_index > 0)
            + pass_charge
        )

    children = 2 * node(level - 1).raw
    top = sum(
        row(1 << (level + 1), row_index)
        + row((1 << (level + 1)) - 1, row_index)
        for row_index in range(3)
    )
    returned_rows = (0, 1) if level == 7 else (1,)
    returns = 8 * sum(row(n, row_index) for row_index in returned_rows)
    apply = 6 * (pw(n, 0) + pw(n, 2))
    matrix = 8 * (pw(n, 0) + pw(n, 1))
    inverse = 6 * sum(
        pass_charge + (1 + int(row_index > 0)) * n for row_index in range(3)
    )
    crt = 4 * (10 * n + lc(n))
    pseudo = 30 + 13 * ((1 << level) - 1) + lc((1 << level) - 1)
    arrays = 2 * (25 * n + lc(n))
    raw = (
        184
        + children
        + top
        + returns
        + apply
        + matrix
        + inverse
        + crt
        + pseudo
        + arrays
    )
    charged = ceil(Decimal(101) * Decimal(raw + 10) / Decimal(100))
    result = Node(
        level,
        children,
        top,
        returns,
        apply,
        matrix,
        inverse,
        crt,
        pseudo,
        arrays,
        raw,
        charged,
    )
    _nodes[level] = result
    return result


# The accepted base schedule is input data, not a source for any new node.
# (degree, level, old shared-table node, outer apply)
BASE_STEPS = (
    (976562, 16, 709315821, 416312974),
    (911027, 16, 709315821, 416968324),
    (845492, 16, 709315821, 381080816),
    (779957, 16, 709315821, 379664574),
    (714422, 16, 709315821, 379664654),
    (648887, 16, 709315821, 379664538),
    (583352, 16, 709315821, 238587530),
    (517817, 16, 709315821, 237470930),
    (452282, 16, 709315821, 190728122),
    (386747, 16, 709315821, 189311634),
    (321212, 16, 709315821, 118967606),
    (255677, 16, 709315821, 89653002),
    (190142, 16, 709315821, 59944058),
    (124607, 15, 319630037, 45830694),
    (91840, 15, 319630037, 27024280),
    (59073, 14, 142528601, 22498676),
    (42690, 14, 142528601, 13137208),
    (26307, 13, 62652075, 11127232),
    (18116, 13, 62652075, 4916260),
    (9925, 12, 27543067, 2424472),
    (5830, 11, 11917539, 1354326),
    (3783, 10, 5044695, 1162198),
    (2760, 10, 5044695, 655350),
    (1737, 9, 2066017, 577898),
    (1226, 9, 2066017, 251906),
    (715, 8, 836909, 160802),
    (460, 7, 321859, 120994),
    (333, 7, 321859, 63912),
)

BASE_STAGE_D = 13_937_663_593
BASE_N_MAX = 57_845_417_161
BASE_TRIAL = 57_840_926_959
FIXED = 3_490_202
BASE_OFFLINE = 1_000_000
COMPRESSION = 279
MEMORY_BYTES = 125_859_472
MEMORY_CLAIM = Decimal("26.908")
TAIL = 349_351
FRAME = 2_099_516

# The planner audits 20 Graeffe depths, ten caps (7..16), and four legal
# allocator layouts.  Its fixed 100,000-operation record/compare bound is
# charged per plan in addition to the base's constant derivation.
PLANNER_PLANS = 20 * 10 * 4
PLANNER_COST_PER_PLAN = 100_000
PLANNER_COST = PLANNER_PLANS * PLANNER_COST_PER_PLAN
OFFLINE = BASE_OFFLINE + PLANNER_COST

GRAEFFE_STEP = 124_876_887
SQUARE_BIT0 = 181_057_812
SQRT = 47_012


def radix_passes(layers: int) -> tuple[int, ...]:
    """The base's radix-at-most-16 split, from low to high passes."""
    widths: list[int] = []
    while layers:
        width = min(4, layers)
        widths.append(width)
        layers -= width
    return tuple(widths)


def transform_upper(layers: int) -> int:
    """Conservative full-row transform used for non-base planner points."""
    points = 1 << layers
    total = 1_000
    for width in radix_passes(layers):
        radix = 1 << width
        blocks = points >> width
        butterflies = width * radix // 2
        total += blocks * (2 * radix + 3 * butterflies + 5 + 24)
    return total


def apply_upper(degree: int) -> int:
    """General apply plan: every shortest 2^a and 3*2^a capacity is tested."""
    need = degree + 1
    choices: list[int] = []
    for layers in range(1, 26):
        for points in (1 << layers, 3 * (1 << layers)):
            if points >= need:
                choices.append(32 * transform_upper(layers) + 100 * points + 20_000)
    return min(choices)


def classical_upper(degree: int) -> int:
    return 80 * degree * (degree + 1) // 2 + 500 + 40 * (degree + 1) + 10_000


def schedule(cap: int) -> tuple[tuple[int, int], ...]:
    current = 976_562
    result: list[tuple[int, int]] = []
    while True:
        choices = [
            level
            for level in range(cap, 6, -1)
            if (1 << (level + 1)) - 1 <= current - 1
        ]
        if not choices:
            break
        level = choices[0]
        result.append((current, level))
        current -= (1 << level) - 1
    return tuple(result)


def planner_stage_d(cap: int) -> int:
    """Exact selected row at cap 16; general conservative rows otherwise."""
    if cap == 16:
        return sum(node(level).charged for _, level, _, _ in BASE_STEPS) + sum(
            apply for _, _, _, apply in BASE_STEPS
        ) + TAIL + FRAME
    steps = schedule(cap)
    tail_degree = steps[-1][0] - ((1 << steps[-1][1]) - 1)
    return (
        sum(node(level).charged for _, level in steps)
        + sum(apply_upper(degree) for degree, _ in steps)
        + classical_upper(tail_degree)
        + FRAME
    )


def depth_delta(depth: int) -> int:
    """Exact change from depth 17 under the base's fixed VSHIFT plan."""
    scan = (depth + 2) * SQRT + (1 << depth) * 448 + 2
    scan_17 = 19 * SQRT + (1 << 17) * 448 + 2
    return (depth - 17) * (GRAEFFE_STEP - SQUARE_BIT0) + scan - scan_17


MEMORY_LAYOUTS = {
    # Exact base allocator walk.
    "base-two-ended": MEMORY_BYTES,
    # Keep one additional 6,144-word scratch block live.
    "retained-scratch": MEMORY_BYTES + 196_672,
    # Pad all four stage-C arrays from 976,896 to 2^20 words.
    "full-point-arrays": MEMORY_BYTES + 9_175_040,
    # Do not reuse the 125,369,472-byte stage-C pool for stage D.
    "disjoint-stages": 125_369_472 + 104_586_304 + 128 + 16_896 + 407_440 + 65_536,
}


@dataclass(frozen=True)
class PlannerResult:
    depth: int
    cap: int
    layout: str
    n_max: int
    memory: int
    exact_score: Decimal


def run_planner() -> tuple[PlannerResult, tuple[PlannerResult, ...]]:
    candidates: list[PlannerResult] = []
    stage_d_16 = planner_stage_d(16)
    for depth in range(20):
        for cap in range(7, 17):
            d_delta = planner_stage_d(cap) - stage_d_16
            for layout, memory in MEMORY_LAYOUTS.items():
                n_max = (
                    FIXED
                    + (BASE_TRIAL - BASE_STAGE_D + stage_d_16)
                    + OFFLINE
                    + depth_delta(depth)
                    + d_delta
                )
                time = (
                    Decimal(n_max).ln() - Decimal(COMPRESSION).ln()
                ) / Decimal(2).ln()
                memory_log = Decimal(memory).ln() / Decimal(2).ln()
                score = time + max(Decimal(0), memory_log - Decimal(20))
                candidates.append(PlannerResult(depth, cap, layout, n_max, memory, score))
    assert len(candidates) == PLANNER_PLANS
    best = min(candidates, key=lambda item: (item.exact_score, item.n_max, item.memory))
    return best, tuple(candidates)


def ceil_places(value: Decimal, places: int) -> Decimal:
    quantum = Decimal(1).scaleb(-places)
    return value.quantize(quantum, rounding=ROUND_CEILING)


def main() -> None:
    assert base_case_raw() == 105_140
    counts = Counter(level for _, level, _, _ in BASE_STEPS)
    old_nodes = sum(old for _, _, old, _ in BASE_STEPS)
    old_applies = sum(apply for _, _, _, apply in BASE_STEPS)
    new_nodes = sum(node(level).charged for _, level, _, _ in BASE_STEPS)
    stage_d = new_nodes + old_applies + TAIL + FRAME
    assert old_nodes == 10_325_889_756
    assert old_applies == 3_609_324_970
    assert BASE_STAGE_D == old_nodes + old_applies + TAIL + FRAME

    trial = BASE_TRIAL - BASE_STAGE_D + stage_d
    n_max = FIXED + trial + OFFLINE
    exact_time = Decimal(n_max).ln() / Decimal(2).ln() - Decimal(COMPRESSION).ln() / Decimal(2).ln()
    time_claim = ceil_places(exact_time, 5)
    score = time_claim + max(Decimal(0), MEMORY_CLAIM - Decimal(20))

    best, candidates = run_planner()
    assert (best.depth, best.cap, best.layout) == (17, 16, "base-two-ended")
    assert best.n_max == n_max
    assert best.memory == MEMORY_BYTES

    print("node-counts", dict(sorted(counts.items())))
    for level in range(7, 17):
        item = node(level)
        print(
            "node",
            level,
            item.children,
            item.top,
            item.returns,
            item.apply,
            item.matrix,
            item.inverse,
            item.crt,
            item.pseudo,
            item.arrays,
            item.raw,
            item.charged,
        )
    print("old_nodes", old_nodes)
    print("new_nodes", new_nodes)
    print("stage_d", stage_d)
    print("planner_plans", PLANNER_PLANS)
    print("planner_cost", PLANNER_COST)
    print("planner_best", best.depth, best.cap, best.layout)
    for depth in range(20):
        row = min(
            (item for item in candidates if item.depth == depth),
            key=lambda item: item.exact_score,
        )
        print("depth_best", depth, row.cap, row.layout, row.n_max, row.memory)
    for cap in range(7, 17):
        row = min(
            (item for item in candidates if item.cap == cap),
            key=lambda item: item.exact_score,
        )
        print("cap_best", cap, row.depth, row.layout, row.n_max, row.memory)
    for layout in MEMORY_LAYOUTS:
        row = min(
            (item for item in candidates if item.layout == layout),
            key=lambda item: item.exact_score,
        )
        print("layout_best", layout, row.depth, row.cap, row.n_max, row.memory)
    print("trial", trial)
    print("offline", OFFLINE)
    print("n_max", n_max)
    print("time_exact", exact_time)
    print("time_claim", time_claim)
    print("memory_exact", log2(MEMORY_BYTES))
    print("memory_claim", MEMORY_CLAIM)
    print("score", score)
    print("margin", Decimal("34.53537") - score)


if __name__ == "__main__":
    main()
```


### E.3 Totals and the allocation walk of one trial

```
m = 976,562 | truncated point sets: n1 = 976,896 of N = 1,048,576 (TRC = 477 of 512 nodes) | squaring steps 219 of which with S: 45
stage C: one squaring step 181,057,812 operations (with S: 182,950,548), pass split {'a': 4, 'b': 4, 'mid': [4, 4, 4]}
S_C = 42,602,465,472
stage D outer steps (degree n, budget k, hgcd ops, apply ops, apply plan):
  n = 976562 k = 65535 hgcd 690,004,574 apply 416,312,974 ('tr', 976896, 976896)
  n = 911027 k = 65535 hgcd 690,004,574 apply 416,968,324 ('tr', 976896, 976896)
  n = 845492 k = 65535 hgcd 690,004,574 apply 381,080,816 ('p3', 18, 786432)
  n = 779957 k = 65535 hgcd 690,004,574 apply 379,664,574 ('p3', 18, 786432)
  n = 714422 k = 65535 hgcd 690,004,574 apply 379,664,654 ('p3', 18, 786432)
  n = 648887 k = 65535 hgcd 690,004,574 apply 379,664,538 ('p3', 18, 786432)
  n = 583352 k = 65535 hgcd 690,004,574 apply 238,587,530 ('p1', 19, 524288)
  n = 517817 k = 65535 hgcd 690,004,574 apply 237,470,930 ('p1', 19, 524288)
  n = 452282 k = 65535 hgcd 690,004,574 apply 190,728,122 ('p3', 17, 393216)
  n = 386747 k = 65535 hgcd 690,004,574 apply 189,311,634 ('p3', 17, 393216)
  n = 321212 k = 65535 hgcd 690,004,574 apply 118,967,606 ('p1', 18, 262144)
  n = 255677 k = 65535 hgcd 690,004,574 apply 89,653,002 ('p3', 16, 196608)
  n = 190142 k = 65535 hgcd 690,004,574 apply 59,944,058 ('p1', 17, 131072)
  n = 124607 k = 32767 hgcd 313,185,629 apply 45,830,694 ('p3', 15, 98304)
  n = 91840 k = 32767 hgcd 313,185,629 apply 27,024,280 ('p1', 16, 65536)
  n = 59073 k = 16383 hgcd 140,767,931 apply 22,498,676 ('p3', 14, 49152)
  n = 42690 k = 16383 hgcd 140,767,931 apply 13,137,208 ('p1', 15, 32768)
  n = 26307 k = 8191 hgcd 62,357,608 apply 11,127,232 ('p3', 13, 24576)
  n = 18116 k = 8191 hgcd 62,357,608 apply 4,916,260 ('p3', 12, 12288)
  n = 9925 k = 4095 hgcd 27,747,929 apply 2,424,472 ('p3', 11, 6144)
  n = 5830 k = 2047 hgcd 12,177,349 apply 1,354,326 ('p1', 12, 4096)
  n = 3783 k = 1023 hgcd 5,235,579 apply 1,162,198 ('p3', 10, 3072)
  n = 2760 k = 1023 hgcd 5,235,579 apply 655,350 ('p1', 11, 2048)
  n = 1737 k = 511 hgcd 2,175,255 apply 577,898 ('p3', 9, 1536)
  n = 1226 k = 511 hgcd 2,175,255 apply 251,906 ('p3', 8, 768)
  n = 715 k = 255 hgcd 895,023 apply 160,802 ('p1', 9, 512)
  n = 460 k = 127 hgcd 345,791 apply 120,994 ('p3', 7, 384)
  n = 333 k = 127 hgcd 345,791 apply 63,912 ('p1', 8, 256)
stage D: classical tail from degree 206; half-gcd operations 13,668,689,670; bump arena 1,048,320 words
S_D = 13,670,789,186
peak of the live set, stage A = 31,260,736 bytes
peak of the live set, stage B = 89,981,120 bytes
peak of the live set, stage C = 125,369,472 bytes
peak of the live set, stage D = 104,586,304 bytes
two-ended pool: blocks of more than 2^10 bytes; largest sum of the two ends after each stage (bytes): init 0, A 31,260,736, B 89,981,120, C 125,369,472, D 125,369,472; at most 10 blocks; 49 blocks examined in all
slab classes (class: peak number of live blocks): ; slab area = 0 bytes
arena = 125,386,496 bytes (two-ended pool 125,369,472 + 128, slab classes 0, stages E and later 16,896), memory = 125,859,472 bytes, log2 = 26.908
```
