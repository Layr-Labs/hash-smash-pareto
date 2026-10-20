# Orchard Poseidon, r = 5: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, value-domain powering on truncated point sets, lean half-gcd with a memory cap, one centre

## 1. Claim

Target: `poseidon-orchard-r5-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, five partial rounds 4, 5, 6, 7 and 8, full rounds 60-63, state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is an algorithm (sections 2-4) with an operation count that bounds every run (sections 6-7) and a success probability derived from two score-critical premises: `H-ONE` (section 9.1), a statement about the fraction of centres at which the fixed digest polynomial has between 1 and 16 usable roots, and `H-NORMAL` (section 9.5), a statement about the normality of the remainder sequence that enters only the success probability. Section 9.2 derives the success probability from them.

* The algorithm: draw a centre `c` from two fresh random words, `c = (w1 2^256 + w2) mod p` (within statistical distance `p/2^512` of uniform on `F_p`, 4.1.1), build the odd part `g_c` of the line polynomial by evaluation and one inverse transform, compute `R = S^((p-1)/2) mod g_c` in the value domain by Montgomery powering on two truncated point sets `O1`, `O2` of `n' = 1491 * 2^14 = 24,428,544` points (1491 of the 2048 depth-11 nodes of the subgroup of order `2^25` and of its coset; the method of bradcush `b30de9bf`/`a41aecdd`, there 15 of 16 nodes, section 4.3T), take `G = gcd(g_c, R - 1)` by the lean cofactor-free half-gcd (bradcush `e6dcb600`/`1aa56884`) with the memory cap of weijiekoh `a78f526e` (outer step `k <= 2,080,768 = 2^21 - 2^14`, applies longer than `2^23` by in-place block products of block length `2^19`, section 4.4), charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` in at most `Z = 64` rounds, take its square root, map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39009`: a lower bound for the probability, over the algorithm's fresh random words, that the centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1), `delta = 0.003` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `eps_iso <= 2.371e-15`, `eps_coin <= 65 p / 2^512 <= 1.404e-76`, `eps_g <= n' (D - 1) / p < 2^-203` (the centre makes `g_c` vanish at a point of `O1`, 4.3T) (sections 4.1.1, 4.3T, 9.2). The value the formula gives is `0.390099999999997628` (at or above the organizer floor 0.39); the claim is that value floored at five decimals.
* `time_log2 = 33.16398` in target-compression units (`C(5) = 321` primitive operations per unit): the operation count that bounds every run, derived in section 6 as `T_fixed + K * T_trial + T_off` with `K = 1`, stage C in the value domain on truncated point sets (4.3T), stage D the lean cofactor-free half-gcd with the memory cap charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (4.4, 6.3; the time bound holds for every sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work), and stage E at its cap of `Z` rounds at degree `DMAX`. `N_max = 3,089,280,065,735` operations, `log2(N_max / 321) = 33.16397...`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is bounded by 1,000,000 operations; that bound is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 31.675` (`3,427,584,396` bytes, section 7). The normalized cost is `33.16398 + max(0, 31.675 - 20) = 33.16398 + 11.675 = 44.83898`.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; every random field element is drawn from two fresh words, at most `65` field elements (`130` words) per run (section 4.1.1), and a draw costs 63 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^11`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Prior entries: this entry replaces our filed r = 5 entry `2f2c30dd` (one executed trial, claimed normalized cost 46.88814) by the one-centre algorithm of our r = 6 entry `c318f442` (the two-word coins, the lean cofactor-free half-gcd charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, the memory cap of weijiekoh's entry `a78f526e`, the premises `H-ONE` at `q = 0.3931` and `H-NORMAL` at `delta = 0.003` with the split of cryptogakusei's entry `4888e783` and organizer-run tests in the form of gta6rp's entry `bef31fdd`), with two changes: (i) stage C is bradcush's value-domain Montgomery powering on truncated point sets (entries `b30de9bf`, `a41aecdd`), ported with 1491 of 2048 nodes and charged in this cost model (4.3T); (ii) the memory schedule of 0xshikhar's entries `52120fad` (r = 4) and `716c3818` (r = 5) (each buffer built and freed by the stage that uses it): no twiddle table is held from init; stage B, the Newton and quotient products of stage C and stage D each build the table of their own transforms and free it, and the padded quotient transform of stage C is placed at the high end over the freed Newton buffers (4.2, 7). The memory is the allocator high-water mark of the one trial (section 7).
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1), a statement about the fraction of good centres, and `H-NORMAL` (score-critical for the success probability only, section 9.5), bradcush's premise on the normality of the remainder sequence stated with the allowance `delta = 0.003` and supported by organizer-run tests. Both are statements about probability. The costs are the declared cost model of this entry, not heuristics: the charging rules of section 4.2, the register file of 18 words, the lean cofactor-free half-gcd of stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (Appendix E). Everything else is proved or counted here.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`. `(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`. The algorithm uses the line `j = 0`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant `M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS, nonzero on the deployed constants, checked). Let `(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, `d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i` (the supports are disjoint). After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8 (partial), 60, 61, 62, 63 (full) put eleven S-box layers on top of an affine map, and the digest is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^11 = D = 48,828,125`. The leading coefficient is obtained by propagating leading coefficients through the eleven layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used: `f_D(0) = 0x3d8a63413498ea10d01ec5a3bc7106382d152c057486fdb7dfe795da6ea4e687` (computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau` against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`), hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 24,414,062`, `g_c` has degree exactly `m` and leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`, `W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The useful roots are the roots in `F_p` with `S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p`; `S = 0` is not a root of `S^((p-1)/2) - 1`). `G` divides the squarefree `S^((p-1)/2) - 1`, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. `H = 25,165,824 = 3 * 2^23` divides `p - 1` (`p - 1 = 2^32 * 3 * q`) and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`; one inverse transform of size `H` returns the coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). The `2H = 50,331,648` evaluations of `F` are each charged as one target-compression unit (`C(5) = 321` operations), although a line evaluation (affine start, the remaining rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation. The loop work (two point additions, one subtraction, one multiplication by `1/(2 zeta^i)`, the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, the store with its address, the loop control and the bit-reversed index) is charged on top (stage B, section 6), with the twiddle table of the transform, built by stage B (4.2).

## 4. The algorithm (one centre, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   constants (once; no twiddle table: each stage builds the table of its own transforms, 4.2)
setup:  the line (line_setup) (once)
for t = 1, ..., K (K = 1):            [the test t <= K is made at the start of the trial; no exit except success]
  A  c := (w1 * 2^256 + w2) mod p from two fresh random words w1, w2 (4.1.1)
  B  g := monic g_c, by section 3 (50,331,648 evaluations + one inverse NTT of size 25,165,824 + the nonzero-leading-coefficient test + normalisation)
  C  R := S^((p-1)/2) mod g, in the value domain on the truncated point sets O1, O2 of n' = 24,428,544 points (section 4.3T): 231 squaring steps, 45 of them also multiplying by S
  D  G := gcd(g, R - 1) (monic): the lean cofactor-free half-gcd with the memory cap (section 4.4), charged for the normal remainder sequence with the quotient and return tests; on any other case ABORT (6.3)
  E  if deg G = 0 or deg G > DMAX: trial ends. Otherwise isolate a root S of G (4.1.2); if none within Z = 64 rounds: trial ends.
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (300 operations each) are equal and the pairs differ -> output; otherwise the trial ends
```

4.1.1 Coins (ruling `04c0dd43`, finding F-EVAL-001). The only randomness is the cost-model random-word primitive. Every random field element of the algorithm (the centre `c` of stage A and each shift of stage E) is drawn from two fresh 256-bit words `w1, w2`: each is reduced mod `p` by three conditional subtractions (exact, `2^256 < 4p`), and `x = (w1 mod p) * (2^256 mod p) + (w2 mod p)` in `F_p`, i.e. `x = (w1 2^256 + w2) mod p` with `w1 2^256 + w2` uniform on `[0, 2^512)`. There is no rejection and no retry. A draw is 63 operations: per word 1 random-word operation, 1 load, 1 store, 3 control, the reduction 9 and its loop control 11 (26 per word, 52), two Montgomery conversions 2, the load of the constant `2^256 mod p` 1, one multiplication 1, one addition 1, entry 2, the two addresses 4. At most `1 + Z = 65` draws (`130` words) per run. With `2^512 = Q p + r`, each residue has `Q` or `Q + 1` preimages, so one draw is within statistical distance `r (p - r) / (p 2^512) <= p / 2^512 = 2^-258.0` of uniform on `F_p`; the 65 draws are independent, so the joint distribution of all the coins of a run is within `eps_coin = 65 p / 2^512 <= 1.404e-76` of the distribution with every draw exactly uniform (total variation is subadditive over independent components).

4.1.2 Stage E: isolating a root of `G`. With `1 <= deg G <= DMAX = 16`, a Cantor-Zassenhaus split with random shifts isolates one linear factor in at most `Z = 64` rounds at degree `<= 16`; `eps_iso <= 2.371e-15` bounds the probability that 64 rounds fail to isolate a root when `deg G >= 1` (section 9.4).

### 4.2 Machine model and charging rules (summary; `C(5) = 321`)

Every field operation, load, store, control operation and random word is one primitive operation; `C(r) = 216 + 21 r = 321` primitive operations is one target-compression unit. The register file is 18 words of 256 bits per transform block, the only register assumption; the algorithm runs on one thread, no dispatch. Allocation: one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes. A block of more than `2^14` bytes is served by the two-ended pool (one region, two ends, first-fit in address order, the statements marked `# pool:H` using the high end and, with the depth-parity placement of section 7, the end `(j + bit8) mod 2` of a half-gcd node at depth `j`); every smaller block by its slab class (the least `j >= 7` with `2^j >= need`, a slot of `2^j` bytes). The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows (a pool request `97` operations besides the walk and `13` per block examined, a slab request at most `126`, a free `81` for a slab block and at most `105` for a pool block). The memory of both allocators is the arena of section 7. Twiddle tables: none is built in init; stage B, the Newton and quotient products of stage C and stage D each build the table of their own largest transform (`2^(a-1)` entries for `3*2^a` points: its root, 5 operations per entry and the loop) and free it at the end of that work, charged in the stage's row; the passes of 4.3T use two-level root tables of `4 x 4,096` words (stage C).

### 4.3T Stage C in the value domain on truncated point sets (the method of bradcush `b30de9bf`/`a41aecdd`, 1491 of 2048 nodes)

Point sets. `N = 2^25` divides `p - 1` (2-adicity 32). Let `psi` have order `2^26`, `H_N = <psi^2>` and `Y = X^(2^14)`. `H_N` is the union of the 2048 depth-11 nodes `{x : x^(2^14) = r_j}`, `r_j` the 2048-th roots of unity in transform (bit-reversed) order; `O1` is the union of the first 1491 nodes, `n' = 1491 * 2^14 = 24,428,544 >= m + 1 = 24,414,063` points, and `O2` the same 1491 nodes of the coset `psi H_N` (`x^(2^14) = r'_j`, `r'_j^2048 = -1`), disjoint from `O1`. `P1 = prod_{j<1491} (Y - r_j)` has degree `n'`, vanishes on `O1` and is the nonzero constant `P1(r'_j)` on node `j` of `O2`; `delta_j = 1/P1(r'_j)` (1491 table constants).

Truncated transforms (bradcush `b30de9bf` 4.3, generalized as the truncated Fourier transform of van der Hoeven, ISSAC 2004). A polynomial of degree `< n'` is `sum_{k<2048} P_k Y^k` with `deg P_k < 2^14` and `P_k = 0` for `k >= 1491`; its values on the 1491 nodes determine it and are determined by it (the CRT for the 1491 coprime moduli `Y - r_j`, whose product `P1` has degree `n'`). The forward transform runs the top 3 layers on all `N/8` offsets (no truncation saving is charged), the middle layers only on the blocks above present nodes, and the bottom 3 layers on the `n'` points. The inverse runs the same layers in reverse, scales each 8-point block of its bottom pass by `diag(1, c^-1 J)` (`c = y^8` of the block, `V^T V = 8 diag(1, cJ)`; 7 multiplications and the load of `c^-1`, 9 operations per block), and recovers the residues of the dropped part `[1491, 2048)`, the maximal subtrees `{1491}`, `{1492..1495}`, `{1496..1503}`, `{1504..1535}`, `{1536..2047}` (depths 11, 9, 8, 6, 2), from the known zero chunks `P_k = 0` along their paths to the root, as bradcush recovers the one dropped leaf; this is charged 10 operations (3 multiplications, 3 additions, a load and a store) per point of a dropped subtree per layer of its path. The positions above `n'` that a transform touches (the top pass over all `N` points, the middle passes, the recovered subtrees) are one scratch buffer of `N - n' = 9,125,888` words that extends the array being transformed (one transform runs at a time), zero-filled once and charged in row C. The passes are fused as in `b30de9bf` 4.5 under the 18-word register file: a bottom pass (8-point blocks: forward layers, the pointwise map, inverse layers; one twiddle set for both directions, `V^T V = 8 diag(1, cJ)`), middle passes of radix 16 then 8, and a top pass that fuses the inverse top of one set with the forward top of the other.

Montgomery powering (`b30de9bf` 4.5). For residues of degree `< n'`, `Mont(A, B) = (A B + u g)/P1` with `u = -A B / g mod P1` (`deg u < n'`); the division by `P1` is exact, `Mont(A, B) = A B / P1 mod g`, and `deg Mont(A, A) <= n' - 2`, so `X Mont(A, A)` has degree `< n'`. A residue `A` (representing `S^e P1`) is held by its values on `O1` and on `O2`, each up to a tracked scalar. One step: `U = A^2 k1` on `O1` (`k1 = -1/(N^3 g)` there; `u` is determined by its values on `O1`); `U` to `O2` (truncated inverse on `O1`, truncated forward on `O2`); `B2 = (A2^2 + U g) delta_j` on node `j` of `O2`, which is `Mont(A, A)` up to the tracked scalar because `P1 = 1/delta_j` there, times the point `x` when the exponent bit is 1; `B2` to `O1` (truncated inverse on `O2`, truncated forward on `O1`). No `1/N` is executed inside the steps (the scalars are tracked, 2 operations per step). Per point and step: on `O1` `sqr, LD k1, mul` (4); on `O2` `LD A2, sqr, LD g, mul, add`, the multiplication by `delta_j`, `ST` (10) and the load of `delta_j` per block (2); 3 more for a 1-bit (the load of the point and a multiplication).

Entry and exit. `g` (coefficients from stage B, its slots above `m` zeroed) goes to `O1` and `O2` (a scaling pass and a truncated forward each). The start residue is `A0 = X^v P1 mod g`, `v = 2^22 = 4,194,304` (VSHIFT = 2): `q = floor(X^v P1 / g)` has `ell = v + n' - m + 1 = 4,208,787` coefficients and is formed from the Newton reciprocal of the reversed `g` and one product (transforms of up to `3*2^22` points, with their own twiddle table, freed after the quotient); on node `j` of `O2`, `x^v P1(x) = r'_j^256 P1(r'_j)` is a constant, so `A0 = x^v P1 - q g` there is one truncated forward of `q` and one pointwise pass (8 per point); then `A0` goes to `O1`. `k1` is formed by chunked batch inversion on `O1` (chunks of `2^16` points: prefix products, one inversion, two multiplications per point); each chunk product is tested for zero before its inversion (2 per chunk), and a zero ends the trial: for fixed `x != 0`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g_c vanishes on O1) <= n' (D - 1) / p = eps_g < 2^-203` (9.2). The exit is one step with multiplier 1 (`Mont(A, 1)`) and two truncated inverses with their scaling, which return `kappa R` (`kappa` the tracked scalar) and `g` in coefficient form; the gcd is scale-invariant, so stage D receives `kappa R - kappa`. There are `231` squaring steps, `45` of them also multiplying by `S`.

Exactness and memory. Every map above is exact (Montgomery products of polynomials of degree `< n'`, held bijectively by their values on 1491 nodes); no premise is added to stage C. The live set of the stage is four arrays of `n'` words (`g` on `O2`, `A` on `O2`, `A` on `O1`, `k1` on `O1`), the scratch of `N - n'` words, the tables (`1,521 + 16,384` words: 30 constants, the 1491 `delta_j`, the two-level root tables) and, while `q` is formed, the Newton arrays. The step-by-step count is expanded in Appendix E (`powx_tr`, `tr_step`) and totals **row C = 1,975,202,223,424** (section 6).

### 4.4 Stage D: the lean cofactor-free half-gcd with the memory cap

`G = gcd(g, R - 1)` is computed by a recursive half-gcd whose products use the transform of section 4.2. The lean variant (bradcush `e6dcb600`/`1aa56884`) returns the remainder of a node, not its transforming matrix, and every consuming `apply` overwrites the arrays it reads (remainder over dividend, the quotient of two coefficients and the remainder only); it computes the same remainder sequence and the same gcd as the matrix form.

Memory cap (the method of weijiekoh `a78f526e`, its `gcd_lean` DMAX and `mat_apply` LMAX, ported into this program and charged in this cost model): (a) the outer loop of the Euclid driver calls `hgcd(a, b, k)` with `k = min(ceil((n + 1)/2), DMAX)`, `DMAX = 2,080,768 = 2^21 - 2^14`, so one outer step reduces the degree by at most `DMAX + 1` and the matrix and the working arrays of one call stay short; (b) every apply of a matrix to a pair longer than `LMAX = 2^23` coefficients is done by the block products of scheme (a) at the block length `2^19` (transforms of `2^20` points): each block of the operands is transformed once, the transforms of a slot are multiplied pointwise and summed, and each output slot is inverse transformed and overlap-added in place into the output array, so the working set of one apply is a few blocks, not the full-length transforms. Both are constants of the algorithm; on the normal sequence every length, parameter and allocation is a function of `m` alone, as without the cap. The cap changes only the shapes of the calls; the remainder sequence and the gcd are the same.

The row is charged for the normal remainder sequence (every quotient of degree 1), the case of the premise `H-NORMAL` (9.5): every division tests that its quotient has degree 1 and every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter (2 operations each), and a zero remainder met inside `hgcd` or in the outer-loop division also ends the trial; on any other case the trial ABORTs (section 6.3). By the prefix lemma of 6.3 every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, so the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The total is **row D = 1,090,374,810,264** (section 6.3, 6).

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G | g_c`, whose roots `S` are nonzero squares with `g_c(S) = 0` and `S^((p-1)/2) = 1` (section 3); `s = sqrt(S) != 0`, so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Ledger: operation count (primitive operations; `C(5) = 321`)

| row | what is charged | operations |
| --- | --- | --- |
| init | constants and bookkeeping (once; no twiddle table, 4.2) | 17,983 |
| setup | the line (`line_setup`, once) | 4,910 |
| A (per trial) | stage bookkeeping, loop test and update, the coin draw (63, two words), one allocation | 1,228 |
| B (per trial) | `50,331,648` evaluations of `F` at `C(5) = 321` each, the loop work, the twiddle table and the inverse transform of size `25,165,824`, the normalisation | 23,532,372,434 |
| C (per trial) | `S^((p-1)/2) mod g` in the value domain on the truncated point sets `O1`, `O2` (1491 of 2048 nodes, `n' = 24,428,544`), VSHIFT = 2, 231 squaring steps (section 4.3T); expanded in Appendix E | 1,975,202,223,424 |
| D (per trial) | lean cofactor-free half-gcd of `(g, R - 1)` with the memory cap, charged for the normal remainder sequence with the quotient and return tests (sections 4.4, 6.3); expanded in Appendix E | 1,090,374,810,264 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16`, each with one draw of 63 (two words) | 166,081,821 |
| F (per trial) | square root, back-map | 47,012 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 321 + 32` | 7,452 |
| trial-loop (per trial) | trial-loop bookkeeping (12) and the allocator reset after an ABORT (1,000), charged in every trial | 1,012 |
| plan_invN misses | one per distinct plan size | 108,115 |
| output rows | the fixed output rows (stages H and I) | 3,390,080 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + 1 * T_trial + T_off` | **3,089,280,065,735** |

`T_off = 1,000,000`; `T_trial = A + B + C + D + E + F + G + trial-loop = 3,089,275,544,647`; `T_fixed = init + setup + plan_invN misses + output rows = 3,521,088`; `K = 1`, so `N_max = 3,521,088 + 3,089,275,544,647 + 1,000,000 = 3,089,280,065,735`. `log2(N_max / 321) = 33.16397...`, rounded up at five decimals to `33.16398`. Rows C and D are not asserted by hand: Appendix E (`stage_cd_r5.py`) expands them from the dimensions of 4.3T and the half-gcd levels with the kernel charges of 4.2 and prints and asserts the two values `1,975,202,223,424` and `1,090,374,810,264`.

### 6.1 Validation
The kernel charges and the allocator rules are those compared with the instrumented totals of our executed runs at `r = 3, 4, 5` (the arena rule within 64 bytes of the measured heap peaks there); the truncated-set stage C (4.3T) has no executed counterpart, and its count is the formula of Appendix E.

### 6.2 Offline derivation
The literals of the sources (Montgomery forms of the organizer constants, `5^q`, `2^65`, the exponent `(4(p-1)+1)/5`) are derived offline in at most `1,000,000` operations, declared `preprocessing_log2 = 20` and inside `N_max`.

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry `e6dcb600`)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g_c, R_c - 1)`: every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the re-centring division of a node, the division of each repetition of the outer loop, each step of the base case) tests, before it does any work beyond reading the two leading coefficients, that its quotient has degree 1 (2 operations); (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); a zero remainder inside `hgcd` or in the outer-loop division also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state at the start of the trial (`1,000` operations, charged in every trial). Lemma (prefix; `e6dcb600`, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each call splits at `k1 = ceil(k/2)` and, with every quotient of degree 1, every degree in the tree is fixed by `m` and the number of quotients so far, and the parameters of the second call and of the outer loop (`k = min(ceil((n+1)/2), DMAX)`, section 4.4) are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's `hgcd` calls and divisions produce has degree at least the base-case bound, so every gcd of degree at most `DMAX = 16` first appears in the classical Euclid below the base-case degree, after a prefix of the degree-0 work; a zero remainder earlier ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The charges follow `1aa56884` proof 4.4 and the cap follows `a78f526e` proof 4.4, both read as text only (no entry script was run, compiled or imported). Appendix E (`stage_cd_r5.py`) prints, for `r = 5`, the charge of stage D for the normal sequence with the tests, `1,090,374,810,264`, and asserts it.

The `r = 5` trial (`~3.43 GB`, `~3.1e12` operations) exceeds the organizer sandbox (128 MiB, 20 s), so the costs are the exact formula counts of sections 6 and 7; zero-fill clearing is charged (ruling `3476cad8`) and the 18-word register-file assumption is declared.

## 7. Memory: the arena of one trial

The arena is the capacity of the allocator of 4.2 on the allocation/free sequence of the trial. Appendix E runs the allocator on every allocation and free of the trial in the order of the program and reports the two-ended-pool high-water mark (the largest sum of the extents of the two ends over the trial), the slab area and the peaks of the live set per stage. The two-ended pool takes the blocks of more than `2^14` bytes and is placed with depth-parity ends and in-place `R*Q` with two spare slots charged (the `POOL_PLACE = 20` discipline). Under the H-NORMAL ABORT stage D the stage-D live set holds the **normal-case division arrays**: on the normal sequence every quotient has degree 1, so each division forms only the quotient of two coefficients and the remainder, and a trial with any other sequence ends (ABORT) after a prefix of these allocations (6.3), so the normal-case walk bounds every trial. With the memory cap of 4.4 the stage-D live peak is `2,334,131,392` bytes (with the stage-D twiddle table), below the stage-C peak; the stage-D trace of Appendix E has no event that raises the pool's high-water mark. The high-water mark is `3,421,552,640` bytes, reached in stage C (the four arrays of `n'` words of 4.3T, the scratch of `N - n'` words and the tables), plus 128 bytes so the unused middle is always at least 128 bytes. The slab classes take the smaller blocks: `698,752` bytes. Stages E and later hold at most 16 small arrays and the free-list heads: `16,896` bytes. The arena is `3,422,268,416` bytes (two-ended pool `3,421,552,640 + 128`, slab `698,752`, stages E and later `16,896`). Peaks of the live set per stage (bytes): A `781,713,472`; B `1,721,237,696`; C `3,421,552,640`; D `2,334,131,392`. With `5,250,444` bytes of code and static data and a `65,536`-byte stack, the footprint is `3,427,584,396` bytes `= 2^31.675`, rounded up at three decimals. No stored advice; each twiddle table is built at run time by the stage that uses it and charged in that stage's row (4.2).

## 8. Review points, answered by location

1. Row D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (6.3): by the prefix lemma every trial executes a prefix of the normal-case work, so the time and memory bounds hold for every sequence; `H-NORMAL` (9.5) enters only the success probability.
2. The memory cap (4.4) is a constant of the algorithm (`DMAX = 2^21 - 2^14`, `LMAX = 2^23`, block length `2^19`); its extra transform work is charged in row D, and its effect on the memory is read from the allocation walk of Appendix E (stage-D peak `2,334,131,392` below the stage-C peak; no stage-D event raises the high-water mark).
3. Row B reproducible from sections 3 and 6 (evaluations * ops/unit + the twiddle table and the inverse transform + normalisation).
4. The 1,000,000-op offline figure is a declared bound (`preprocessing_log2 = 20`), score effect < 4e-7 bit.
5. The mem penalty uses the rounded-up `mem_log2`, a self-penalizing over-charge.
6. `success = q - delta - eps_coin - eps_iso - eps_g >= 0.39` from the premises `H-ONE` and `H-NORMAL` (9.2, 9.5) with `K = 1`, `q = 0.3931`, `delta = 0.003`; the value is `0.390099999999997628`. The `H-ONE` allowance below the law value is stated exactly (`0.3934693 - 0.3931 = 0.0003693`; `q <= 151/384 = 0.3932292`, the four-moment Bonferroni bound, 9.1), and `delta = 0.003` is supported by 3,072 organizer-seeded sequences (10.5.1).
7. The organizer-checkable output is the returned witness-pair count; the premises hold under trusted execution of the submitted program, disclosed, not claimed as an organizer-verified proof.

## 9. The premise and the success bound

### 9.1 H-ONE
The number of centres `c` with `1 <= k(c) <= 16` is at least `q p = 0.3931 p`, `k(c)` the number of nonzero squares `S` with `g_c(S) = 0` (`= deg G`). The premise states `q = 0.3931`, the law value `1 - e^(-1/2) = 0.3934693` (9.3) less the extrapolation allowance stated exactly as `0.0003693`; it is also `0.0001292` below the four-moment Bonferroni bound `151/384 = 0.3932292`. The split of the allowance between `H-ONE` and `H-NORMAL` follows cryptogakusei's entry `4888e783`: with `delta = 0.003` (9.5) the bound of 9.2 needs `P(E_c) >= 0.3931` at `K = 1`. The extrapolation, the monodromy theorem at N = 2, 3 and the toy-field and organizer-run evidence are in the claim.json heuristic `H-ONE` and sections 10.3, 10.5.1.

### 9.2 The success bound
The centre is a fresh draw. For a centre `c` let `E_c` be the event `1 <= k(c) <= DMAX` (H-ONE, `P(E_c) >= q = 0.3931`) and `N_c` the event that the remainder sequence of `(g_c, R_c - 1)` is normal down to its gcd (H-NORMAL, 9.5, `P(not N_c) <= delta = 0.003`). The value-domain stage C reproduces `R = S^((p-1)/2) mod g` exactly (Montgomery products on the truncated point sets, 4.3T) and adds no premise; it needs `g_c` nonzero on `O1`, which fails with probability at most `eps_g = n' (D - 1) / p < 2^-203` over the centre (4.3T). If `E_c` and `N_c` hold and `g_c` has no zero on `O1`, stages C and D run to their end and return `G = gcd(g_c, R_c - 1)`; a successful isolation then ends in a verified collision. For `c` uniform `P(E_c and N_c) >= q - delta`, so with one centre (the event `g_c` zero on `O1` subtracted as `eps_g`)

`success = 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g`, `K = 1`.

Transfer to the written sampler (F-EVAL-001): `q - delta - eps_iso - eps_g` bounds the success probability of the run whose draws are exactly uniform on `F_p` (the premises and the isolation lemma are stated for uniform draws). The success of a run is an event of the vector of its draws, and the actual draws of 4.1.1 are within total variation `eps_coin` of the uniform vector, so the actual success probability is at least the ideal one minus `eps_coin`.

With `q = 0.3931`, `delta = 0.003`, `eps_iso <= 2.371e-15`, `eps_coin <= 1.404e-76`, `eps_g < 2^-203`: `q - delta = 0.3901`, and the value is `0.390099999999997628 >= 0.39`. The bound stays at or above `0.39` for every `delta <= 0.0030999` at `q = 0.3931`. The probability is over the random words of 4.1.1 for the fixed target, not over targets and not a sampled frequency.

### 9.3 Monodromy (support for H-ONE)
The roots of `G(c,t) = g_c(t^2)` come in pairs `+-t_i`, so the monodromy lies in the hyperoctahedral group `B_m` and `k(c)` counts positive Frobenius fixed points; for `B_m` this is Poisson(1/2) in the limit, `P(k >= 1) = 1 - e^(-1/2) = 0.3934693`, and Bonferroni at order 4 gives `P >= 151/384 = 0.3932292`. A theorem at two and three layers (Aubry-Perret, monodromy `B_12`, `B_62`); false for permutation polynomials, for decomposable `F` with imprimitive monodromy, and at one layer.

### 9.4 Isolation lemma
With `1 <= deg G <= 16`, a random-shift split isolates a linear factor within `Z = 64` rounds except with probability `eps_iso <= 2.371e-15`. Finite derivation: `G` divides both `g_c` and `S^((p-1)/2) - 1`, so it is squarefree and splits into `d = deg G <= 16` distinct linear factors `X - t_i` over `F_p`. A round with shift `a` keeps a nontrivial part of the current factor `H` under `gcd(H, (X + a)^((p-1)/2) - 1)` (or `X + a` itself when `a = -t_i`), so two roots `t_i != t_j` stay together only if `chi(t_i + a) = chi(t_j + a)` or `a` is in `{-t_i, -t_j}`. Since `sum_a chi((a + t_i)(a + t_j)) = -1` for `t_i != t_j`, exactly `(p - 3)/2` shifts give equal nonzero characters, so for `a` uniform on `F_p` the pair stays together with probability at most `((p - 3)/2 + 2)/p = 1/2 + 1/(2p)`; each shift is a fresh random word reduced mod `p`, within statistical distance `2^-128` of uniform (4.1.1), so per round the bound is `1/2 + 2^-127`, independently across rounds. The parts are nested, so the factor kept after 64 rounds holds two roots only if one of the at most `C(16,2) = 120` pairs was never separated in 64 rounds. By the union bound `eps_iso <= 120 (1/2 + 2^-127)^64 < 6.6e-18 <= 2.371e-15`; the looser stated value `2.371e-15` is kept, so every other number is unchanged.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries `e6dcb600` and `1aa56884`; allowance split of cryptogakusei's `4888e783`; organizer-run tests in the form of gta6rp's `bef31fdd`)
**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(g_c, R_c - 1)`, where `g_c` is the monic odd part of section 3 (degree `m = 24,414,062`) and `R_c = S^((p-1)/2) mod g_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.003` (`2^-8.38`). Stage D is charged for the normal sequence; every division tests its quotient degree and every call of the half-gcd its return, and on any other case the trial ends (ABORT, sections 4.4, 6.3). The premise enters only the success probability (9.2): the time and memory bounds hold for every remainder sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work (6.3). For a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes, each a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-203`; the premise extrapolates a much weaker form of this random-pair behaviour (`delta = 0.003`) to the structured pair `(g_c, R_c - 1)`. Measured support is organizer-run (10.5.1): the six experiments `euclid-normal-n2-t256-l2-a` to `-f` compute the complete Euclidean sequence of `(g_c, R_c - 1)` for this construction on the truncation `F_2` (`m = 12`) for 256 organizer-seeded trials of two centres each (3,072 sequences in all) and return a witness pair exactly when both sequences of a trial are normal; `euclid-normal-n3-t24` and `euclid-normal-n4-t2` do the same at `m = 62, 312`. The prediction is that every computed sequence is normal. Zero abnormal in the 3,072 sequences bounds the abnormality at `m = 12` by `3/3072 = 0.00098 < delta = 0.003` (rule of three, one-sided 95%). Not verified at `r = 5`, which would need the computation itself; the organizer-run tests are at `m = 12` to `312`, far below `m`.

## 10. Experiments

Program `experiments/exp_euclid.py` (euclid-normal, one-centre) and `experiments/exp_line.py` / `experiments/exp_lowbits.py` (line-ladder and lowbits-birthday), with `experiments/manifest.json`.

10.3 The truncations. `F_N(c + X)` is coordinate 0 after the first `N` S-box layers on the line `j = 0`; `F_2`, `F_3`, `F_4` have odd parts of degree `m = 12, 62, 312`. The arithmetic monodromy at `N = 2, 3` is `B_12`, `B_62` (Grok jobs 136, 137, re-run on the deployed constants).

10.5.1 Organizer-run set. euclid-normal-n2-t256-l2-a to -f compute the complete Euclidean sequence of `(g_c, R_c - 1)` for this construction at depth `N = 2` (`m = 12`), each for 256 organizer-seeded trials of two centres (512 sequences per entry, 3,072 in all; the final letter only changes the organizer seeds); euclid-normal-n2-t256, -n3-t24 and -n4-t2 compute one sequence per trial at `m = 12, 62, 312`. A trial returns a witness pair exactly when its sequences are normal; the prediction (H-NORMAL, 9.5) is that every trial returns a pair, so the abnormal count is zero, which bounds the abnormality at `m = 12` by `3/3072 < delta = 0.003`. one-centre-n2-t256 and one-centre-n3-t24 run one trial of the algorithm at depth `N = 2, 3` per organizer seed and return a witness pair exactly when the sequence is normal, `1 <= k(c) <= 16` and the isolated root gives a verified collision of `F_N`, with predicted counts Binomial(T, 0.393469) (H-ONE, 9.1). line-ladder-w6/-w8/-w10/-w12 and lowbits-birthday corroborate the antipodal structure (random-function model), not the score-critical basis. Our runs of the six -l2 entries with local seeds in the organizer's container settings (1 CPU, 128 MiB, no network; 6.96 to 8.35 s each, every replay byte-identical): 3,072 sequences, all normal, every returned pair checked; the gcd had positive degree for 1,229 of the 3,072 centres (0.400). The organizer-checkable output is the returned witness-pair count; the premises H-ONE and H-NORMAL hold under trusted execution of the submitted program.

## Appendix E: the stage C and stage D totals and the arena of one trial (`stage_cd_r5.py`)

The standalone program `stage_cd_r5.py` below expands stages C and D of one trial at `r = 5` from the dimensions of 4.3T and the half-gcd levels with the kernel charges of 4.2, runs the allocator of 4.2 on the allocation/free walk of the trial, and recomputes and asserts the stage totals, the live-set peaks and the two-ended-pool high-water mark. Stage C is `powx_tr` (the truncated point sets of 4.3T, `TRC = (1491, 11)`, `VD_H = 2^25`, `VSHIFT = 2`; one step is `tr_step`). Stage D is the lean cofactor-free half-gcd on the normal remainder sequence with the memory cap of section 4.4 (`GCD_DMAX = 2^21 - 2^14`, `LD_LMAX = 2^23`, `A_HB = 2^19`, `LD_PIECES = 0`): before each division the program tests that the quotient has degree 1 (`deg a - deg b = 1` with a nonzero leading coefficient) and every half-gcd call tests that it returns its parameter or a zero remainder, two operations each charged ahead of the division, and any other case ends the trial at once (ABORT); H-NORMAL (section 9.5) enters only the success bound, not the time or the memory. The twiddle tables are built and freed by the stages that use them (`TWMOVE = 1`, 4.2) and the live sets follow the `POOL_PLACE = 20` placement discipline (section 7). The program is self-contained and runs standalone (ruling `ea6f3fc9` requires the recompute script and its output in the package); its asserts fix `S_C = 1,975,202,223,424`, `S_D = 1,090,374,810,264`, the pool high-water `3,421,552,640` (reached in stage C; the stage-D trace raises it at no event) and the arena `3,422,268,416`. The full source follows, then its exit-0 output (every number of sections 6 and 7 is read from it).

```python
#!/usr/bin/env python3
"""Appendix E: stage C and stage D of one trial at r = 5, expanded into their totals (standard library only).
Run:  python3 stage_cd_r5.py      prints S_C = 1,975,202,223,424 and S_D = 1,090,374,810,264 and asserts them.

The inputs are the dimensions m = (5^11 - 1)/2 = 24,414,062 (degree of the modulus), the exponent (p-1)/2, and the charging rules of section 4.2,
which fix the per-kernel charges in the tables PASS and K3 below (butterfly 3 field operations or 2 when the twiddle is 1, twiddle load with
address, 8 operations per radix-3 leaf, loop control 3 per iteration and 2 on exit). Everything else is a finite recurrence:
  stage C: in the value domain on the truncated point sets O1, O2 of n' = 1491 * 2^14 = 24,428,544 points (proof 4.3T; TRC = (1491, 11), h = 2^25); the exponent: 231 squaring
           steps, 45 of them with the multiplication by S; each step = the passes of tr_step (bottom, middle, fused top, recoveries of the dropped subtrees) + the pointwise loops;
  stage D: the outer loop of the Euclid driver, hgcd(k) with k halved (rounded up) until k <= 96, in each level the two recursive calls,
           apply_inv (one bilinear convolution), the division by a quotient of degree one, the 2x2 matrix product (conv_bilin_cost);
  below k <= 96 and n <= 192: classical division steps with quotient of two coefficients (divrem_naive).
`Tr` accumulates the operations and walks every allocation and free (an allocation is charged 121 + 13 (2 live + 1), a free 105; a block is 64 + 32 * slots rounded up to 64 bytes,
header included), with the live bytes and their peak, and the peak of the temporary arrays inside one call (the quotient and working arrays of every division, the workspaces of the
outer-transform scheme of the block products); it also records the events of the walk: every allocation and free with the identity of its block (the arrays given to a call by name).
The charge of stage D is the lean cofactor-free half-gcd with the memory cap on the normal remainder sequence of proof.md 4.4 and 6.3 (NORMALD = 1, WORST_D = False):
every division tests that its quotient has degree 1 and every call of hgcd that it returns its parameter (or a zero remainder), 2 operations each, and any other case ends
the trial (ABORT); the script prints the normal local total, the stage-D total and the peak of the live set of each stage.
Twiddle tables (TWMOVE = 1): no table is built in init; stage B, stage C and stage D each build the table of their own transforms and free it (tw_new, charged by tw_ops).
The arena is not the peak of the live set: the script runs the allocator of proof.md 4.2 on the events of one trial (init, A, B, C, D in the order of the program; sizes are functions of m and
the recursion shape only, the same for every input): the blocks of more than 2^BIG_EXP bytes are placed address by address by the two-ended pool (TwoEnd: two first-fit lists, the low one from
the bottom, the high one, for the statements marked `# pool:H`, from the top; split, coalescing, the largest sum of the two ends is its capacity), the other blocks by the slab classes (slot of 2^class bytes, one new slot from the end of the slab area when the free list of the class is empty: the area is the
sum over the classes of the peak number of live blocks times the slot), and it checks that the events reproduce the walk (walk_check)."""
import functools, math, collections, sys, os

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
PM2, PM1H = P - 2, (P - 1) >> 1
INV_CTL, STAGE_BK, CACHE = 2310, 1000, 64


def powcost(e):
    return (e.bit_length() - 1) + (bin(e).count('1') - 1) if e > 0 else 0


PASS = {   # kernel -> for k = 1..4 layers: (c0, a, b), charge c0 + a*G + b*G*S  (G groups, S = 2^(layers below) - 1)
    'f': ((4, 17, 19), (4, 35, 43), (4, 80, 96), (4, 185, 213)),
    'i': ((4, 17, 21), (4, 36, 47), (4, 82, 102), (4, 188, 221)),
    'usq': ((3, 18, 0), (3, 49, 0), (3, 128, 0), (3, 315, 0)),
    'umul': ((4, 23, 0), (4, 58, 0), (4, 145, 0), (4, 348, 0)),
}

K3 = {   # radix-3 position kernels: K3[type][pattern of nonzero rows 0..7][rotation 0..2]
    'f': [(6,6,6),(8,14,14),(14,8,14),(19,19,25),(14,14,8),(19,25,19),(25,19,19),(24,24,24)],
    'i': [None,(10,16,16),(16,10,16),(20,20,26),(16,16,10),(20,26,20),(26,20,20),(24,24,24)],
    'r0': [(2,2,2),(4,4,4),(4,4,4),(7,7,7),(4,4,4),(7,7,7),(7,7,7),(10,10,10)],
    'r1': [(2,2,2),(4,7,7),(7,4,7),(10,10,13),(7,7,4),(10,13,10),(13,10,10),(16,16,16)],
    'r2': [(2,2,2),(4,7,7),(7,4,7),(10,10,13),(7,7,4),(10,13,10),(13,10,10),(16,16,16)],
}
ROT = ((0, 0, 0), (0, 1, 2), (0, 2, 1))      # rotation of the three kernels of a position triple, by the phase c0


def pass_fwd(a, l0, k):
    c0, p, q = PASS['f'][k - 1]; g = 1 << l0
    return 5 + (9 * k + 2) + 4 + c0 + p * g + q * g * ((1 << (a - l0 - k)) - 1)


def pass_inv(a, l0, k):
    c0, p, q = PASS['i'][k - 1]; g = 1 << l0
    return 6 + (9 * k + 2) + 4 + c0 + p * g + q * g * ((1 << (a - l0 - k)) - 1)


def pass_fused(a, k, mode):
    c0, p, q = PASS['usq' if mode == 'sq' else 'umul'][k - 1]
    return 6 + (9 * k + 2) + 6 + c0 + p * (1 << (a - k))


FREE_OPS = 105


def blk(slots):
    return 64 + ((slots * 32 + 63) & ~63)


BIG_EXP = 14                           # a block (header included) of more than 2^BIG_EXP bytes is served by the two-ended pool, every other block by its slab class (proof 4.2); a constant of the algorithm for each r
MIDPROD = 7                             # bit 1: the product (q g)[0..m-1] of the squaring step of stage C is formed cyclically (outer length for the window only) with the known high coefficients subtracted; bit 2: windows of the Newton products
QMIN = 7                               # smallest slab class: slots of 2^7 = 128 bytes
SLAB_ALLOC_OPS = 126                   # operations of an allocation from a slab class (proof 4.2): 125 plus the NEW_FP statement; below the charge 1 + 120 + 13 (2 L + 1) of every allocation
SLAB_FREE_OPS = 81                     # operations of a free of a slab block (proof 4.2); the charge of a free is FREE_OPS = 105
assert SLAB_ALLOC_OPS <= 1 + 120 + 13 and SLAB_FREE_OPS <= 105
STREAMC = 0          # rival 716c3818 stage-C memory schedule, off
STREAMD = 0          # rival 716c3818 stage-D memory schedule, off
LIVESET = 0          # rival 716c3818 live-set aliasing, off


class Slot(int):
    """an array of v slots together with the identity of its block, so that the walk is also the sequence of allocations and frees of the program (proof 4.2, 7)"""
    def __new__(cls, v, ident):
        o = int.__new__(cls, v); o.id = ident; return o


class Ctx:
    """identities of the blocks of one walk: the root walk, or one memoised call of hgcd (ids >= 0 local to the call, ids < 0 the arrays given to it)"""
    def __init__(self): self.n = 0


CTX_STACK = [Ctx()]


def new_id():
    c = CTX_STACK[-1]; i = c.n; c.n += 1; return i


class Rec:
    """the events of one memoised call of hgcd, recorded once: ('A', id, slots) allocation, ('F', id, slots) free, ('T', slots...) temporary arrays of one call (allocated in the
    order listed, freed in the reverse order), ('R', n, events) a self-contained group repeated n times, ('C', rec, base, args) a call of a recorded call"""
    def __init__(self, ev, nloc): self.ev = ev; self.nloc = nloc


POOL_H_LINES = frozenset(k + 1 for k, ln in enumerate(open(__file__, encoding='utf-8').read().split(chr(10))) if ln.rstrip().endswith('# pool:' + 'H'))


def _site(depth):
    """the list of the pool that serves the allocation statement that called: 1 (high list) for the statements marked `# pool:H` in this file, else 0 (low list); a constant of the statement"""
    f = sys._getframe(depth); return 1 if (f.f_code.co_filename == __file__ and f.f_lineno in POOL_H_LINES) else 0


LD_WHO = 0           # gcdonly (10-19): 1 records the names of the calling functions on every allocation event (a fifth element; for the peak analysis only, no charge)


def _who():
    """the names of the calling functions above new_fp, for the peak analysis only (no charge)"""
    out = []
    f = sys._getframe(2)
    for _ in range(4):
        if f is None: break
        out.append(f.f_code.co_name + ':' + str(f.f_lineno)); f = f.f_back
    return '<'.join(out)


class Tr:
    """sequential trace: ops, current live bytes/blocks relative to entry, peaks, and the events (allocations and frees) of the walk"""
    __slots__ = ('ops', 'cur', 'peak', 'cnt', 'pcnt', 'base', 'ev')

    def __init__(self, base=0):
        self.ops = 0; self.cur = 0; self.peak = 0; self.cnt = 0; self.pcnt = 0; self.base = base; self.ev = []

    def here(self): return self.base + self.cnt            # live blocks now (for sub-traces)

    def bump(self, slots):                                  # peak of a temporary array of `slots` elements that is live only inside one call (no operation charged)
        if slots > 0:
            self.peak = max(self.peak, self.cur + blk(slots)); self.pcnt = max(self.pcnt, self.cnt + 1)
            self.ev.append(('T', (int(slots),), _site(2)))

    def bump_blocks(self, slot_list):                       # peak of several temporary arrays live together inside one call (no operation charged)
        self.peak = max(self.peak, self.cur + sum(blk(x) for x in slot_list)); self.pcnt = max(self.pcnt, self.cnt + len(slot_list))
        if slot_list: self.ev.append(('T', tuple(int(x) for x in slot_list), _site(2)))

    def ctl(self, n): self.ops += n
    def ld(self, n): self.ops += 2 * n
    def st(self, n): self.ops += 2 * n
    def loopc(self, n): self.ops += 3 * n + 2

    def add(self, o):
        self.ops += o.ops
        self.peak = max(self.peak, self.cur + o.peak); self.pcnt = max(self.pcnt, self.cnt + o.pcnt)
        self.cur += o.cur; self.cnt += o.cnt
        self.ev.extend(o.ev)

    def new_fp(self, slots):
        slots = max(slots, 1) if slots else 1
        self.ops += 1 + 120 + 13 * (2 * (self.base + self.cnt) + 1) + ASTAT        # pos_leand: ASTAT = 0 except in the gate (1aa56884 allocator statistics)
        b = blk(slots); self.cur += b; self.cnt += 1
        self.peak = max(self.peak, self.cur); self.pcnt = max(self.pcnt, self.cnt)
        i = new_id(); self.ev.append(('A', i, int(slots), _site(2), _who()) if LD_WHO else ('A', i, int(slots), _site(2)))
        return Slot(slots, i)

    def free(self, slots):
        self.ops += FREE_OPS + ASTAT
        self.cur -= blk(slots); self.cnt -= 1
        self.ev.append(('F', slots.id, int(slots)))


class Plan:
    def __init__(self, rows, a):
        self.rows = rows; self.a = a; self.n = 1 << a; self.N = 3 * self.n if rows == 3 else self.n
        self.c0 = (1 if a & 1 else 2) if rows == 3 else 0
        self.np = (a + 3) >> 2
        kk = [0] * self.np; rem = a
        for i in range(self.np - 1, -1, -1):
            k = min(4, rem); kk[i] = k; rem -= k
        self.kk = kk


def plan_invN_ops(Pl):
    return 7 * CACHE


def udivmod_cost(a, b):
    nb = a.bit_length(); q = a // b
    return 4 * nb + 2 + 10 * nb + 2 * bin(q).count('1') + 4


def for8(n):                           # FOR8 / for8_ctl charge of the loop control
    return 1 + 3 * (n // 8) + 2 + 3 * (n % 8) + 2


def make_plan(rows, a):
    p = Plan(rows, a)
    c = 18 + 4 + (3 * p.np + 2) + 4 * p.np + 2 + (4 if rows == 3 else 0)
    return p, c


BIGA = 32                              # v2(p-1) = 32: transform sizes 3*2^a exist in F_p for a <= 32 only; longer products use blocks (Grok job 140, scheme (a))
P32, _c32 = make_plan(3, BIGA)         # the block transform plan 3*2^32
NB = P32.N; HB = NB // 2               # block transform size NB = 3*2^32, block length HB = NB/2


def plan3_for_len(ln):
    c = 0
    for a in range(2, 96):                 # pos_vdc: 96 (r = 22 needs a = 64, 65)
        c += 3 + 1 + 2 + 2
        if 3 * (1 << a) >= ln:
            p, cc = make_plan(3, a); return p, c + cc
    raise ValueError


def split_regions(n, N, boff, lenB):
    c = 3; bp = [0]
    nt0 = 0
    for t in range(3):
        st = nt0 + N - boff
        if st >= N: st -= N
        nt0 += n; c += 9
        c += 3
        if st < lenB:
            x = lenB - st; c += 1; c += 3
            if 0 < x < n: bp.append(x); c += 1
        c += 3
        if st > 0:
            x = N - st; c += 1; c += 3
            if 0 < x < n: bp.append(x); c += 1
            x = N + lenB - st; c += 2; c += 3
            if 0 < x < n: bp.append(x); c += 1
    c += 2
    bp.append(n); c += 1
    cnt = len(bp)
    for a in range(1, cnt):
        key = bp[a]; b = a - 1; c += 3 + 2
        while b >= 0 and bp[b] > key:
            bp[b + 1] = bp[b]; b -= 1; c += 6
        c += 3
        bp[b + 1] = key
    c += 2
    out = []; pats = []
    for a in range(cnt - 1):
        c += 6
        if bp[a + 1] > bp[a]:
            lo = bp[a]; p = 0; nt1 = 0
            for t in range(3):
                idx = lo + nt1 + N - boff
                if idx >= N: idx -= N
                p |= (1 if idx < lenB else 0) << t; nt1 += n; c += 13
            c += 5
            out.append(lo); pats.append(p); c += 2
    c += 2
    out.append(n); c += 1
    return out, pats, c


def driver(typ, pat, c0, lo, hi):
    K = [K3[typ][pat][r] for r in ROT[c0]]
    i = lo
    c = udivmod_cost(lo, 3); ph = lo % 3; c += 1
    c += 2
    if ph == 1:
        c += 2
        if i < hi:
            c += K[1]; i += 1; c += 1
            c += 2
            if i < hi:
                c += K[2]; i += 1; c += 1
    else:
        c += 2
        if ph == 2:
            c += 2
            if i < hi:
                c += K[2]; i += 1; c += 1
    nt = 0; c += 2
    if hi > i:
        nt = (hi - i) // 3; c += udivmod_cost(hi - i, 3); c += 2
    c += nt * (K[0] + K[1] + K[2] + 4)
    i += 3 * nt
    c += 2
    c += 2
    if hi > i:
        rem = hi - i; c += 1
        c += K[0]; i += 1; c += 1
        c += 2
        if rem == 2:
            c += K[1]
    return c


def stageA_fwd(Pl, ln):
    c = 4
    n = Pl.n
    if Pl.rows == 1:
        raise NotImplementedError('plain rows==1 forward copy is not used on the charged path')
    bp, pat, cc = split_regions(n, Pl.N, 0, ln); c += cc
    c += 2
    for q in range(len(pat)):
        c += 4 + driver('f', pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def stageA_inv(Pl, outlen):
    if Pl.rows == 1:
        return 0
    c = 2
    bp, pat, cc = split_regions(Pl.n, Pl.N, 0, outlen); c += cc
    c += 2
    for q in range(len(pat)):
        c += 2
        if pat[q] == 0:
            c += 3; continue
        c += 4 + driver('i', pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def stageA_row(Pl, r, lenB, boff):
    n = Pl.n
    bp, pat, c = split_regions(n, Pl.N, boff, lenB)
    c += 2
    for q in range(len(pat)):
        c += 3 * 11 + 2 + 4 + driver('r%d' % r, pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def fwd_passes(Pl, cnt):
    l0 = 0; c = 0
    for p in range(cnt):
        c += pass_fwd(Pl.a, l0, Pl.kk[p]) + 4; l0 += Pl.kk[p]
    return c


def inv_passes(Pl, first):            # inverse passes p = first down to 0
    l0 = sum(Pl.kk[:first + 1]); c = 0
    for p in range(first, -1, -1):
        l0 -= Pl.kk[p]
        c += pass_inv(Pl.a, l0, Pl.kk[p]) + 4
    return c


def fused(Pl, mode):
    return pass_fused(Pl.a, Pl.kk[-1], mode)


def conv_core_row(Pl, mode):
    return 9 + fwd_passes(Pl, Pl.np - 1) + 4 + fused(Pl, mode) + inv_passes(Pl, Pl.np - 2) + 4


def conv_sq(Pl, ln, outlen):
    if Pl.a > BIGA: return conv_sq_big(ln, outlen)
    c = stageA_fwd(Pl, ln)
    c += Pl.rows * conv_core_row(Pl, 'sq') + 2
    return c + stageA_inv(Pl, outlen)


def mulc_otf_row(Pl, r, lenB, boff):
    c = 12 + stageA_row(Pl, r, lenB, boff)
    c += fwd_passes(Pl, Pl.np) + 2
    c += fwd_passes(Pl, Pl.np - 1) + fused(Pl, 'mul') + inv_passes(Pl, Pl.np - 2) + 4
    return c


def conv_mulc_otf(Pl, ln, lenB, boff, outlen, sub=False, cached=False, wrap=False):
    if Pl.a > BIGA: return conv_mulc_big(ln, lenB, (Pl.N - boff) % Pl.N, outlen, sub, cached, wrap)
    c = 2 + stageA_fwd(Pl, ln) + 4
    for r in range(3):
        c += mulc_otf_row(Pl, r, lenB, boff)
    return c + 2 + stageA_inv(Pl, outlen)


def pw_loop(n, mode):
    return for8(n) + n * (7 if mode == 0 else 10)


def conv_bilin_cost(Pl, nout, outlen, groups, hboff=0):
    if Pl.a > BIGA: return conv_bilin_big(nout, outlen, groups, (Pl.N - hboff) % Pl.N if hboff else 0)
    c = 2
    eps = [0] * nout
    c += 2 + 3 * nout
    for g in groups:
        for s in range(len(g['S'])):
            for h in range(len(g['H'])):
                c += 6
                o, sg = g['prod'].get((s, h), (-1, 0))
                if o >= 0 and not eps[o]:
                    eps[o] = sg
    for r in range(3):
        c += 2 + 2 + nout + 1
        done = [0] * nout
        for g in groups:
            c += 7
            for lh in g['H']:
                c += 6 + stageA_row(Pl, r, lh, hboff) + fwd_passes(Pl, Pl.np)
            for s, ls in enumerate(g['S']):
                c += 6 + stageA_row(Pl, r, ls, 0) + fwd_passes(Pl, Pl.np)
                for h in range(len(g['H'])):
                    c += 8
                    o, sg = g['prod'].get((s, h), (-1, 0))
                    if o < 0: continue
                    if not done[o]:
                        done[o] = 1; c += pw_loop(Pl.n, 0)
                    elif sg == eps[o]:
                        c += pw_loop(Pl.n, 1)
                    else:
                        c += pw_loop(Pl.n, 2)
        for k in range(nout):
            c += 3
            if eps[k]:
                c += inv_passes(Pl, Pl.np - 1)
        c += 0
    for k in range(nout):
        c += 3
        if eps[k]:
            c += stageA_inv(Pl, outlen[k])
    return c, eps


# ---------------------------------------------------------------- products longer than 3*2^32: block products (Grok job 140, scheme (a))
# A product of two polynomials is split into blocks of HB = 3*2^31 coefficients.  Every block is transformed once with the transform of size NB = 3*2^32
# (plan P32, the same kernels), the transforms of a slot s (the block pairs i + j = s) are multiplied pointwise and summed in the transform domain,
# every slot that meets the wanted output window is inverse transformed once and placed (overlap-added, scaled by 1/NB, or subtracted) into the output.
@functools.lru_cache(maxsize=None)
def big_fwd(bl):                       # forward transform of a block of bl coefficients (zero-padded to NB), all three rows
    return stageA_fwd(P32, bl) + 3 * fwd_passes(P32, P32.np)


@functools.lru_cache(maxsize=None)
def big_inv(outn):                     # inverse transform of one slot, the first outn coefficients are needed
    return 3 * inv_passes(P32, P32.np - 1) + stageA_inv(P32, outn)


def big_pw(mode):                      # one pointwise product over NB points: mode 0 write, 1 add, 2 subtract (as pw_loop)
    return 3 * pw_loop(P32.n, mode)


def nblk(l): return -(-l // HB)


def big_fwd_all(l):                    # all blocks of an operand of l coefficients (closed form)
    k = nblk(l)
    return (k - 1) * big_fwd(HB) + big_fwd(l - (k - 1) * HB)


def big_place(cnt, ov, sub):           # place a slot: cnt coefficients read from the accumulator, scaled by 1/NB, stored; ov of them added to, or all subtracted from, the output
    c = 3 * cnt + 2 + 2 * cnt + cnt + 2 * cnt            # loop control, load, scale multiplication, store
    return c + (cnt if sub else ov) * 3                   # load of the output value and the add or subtract


# ---------------------------------------------------------------- extension for r >= 12 (pricing model, 2026-10-17): closed-form slot sums and the outer-NTT block product (Grok job 140, j = 3)
OB2 = (5, 13)                            # kernel ob2 of ntt_kern.h, one radix-2 butterfly of two blocks over cnt positions: charge 5 + 13 cnt (parsed and asserted in Leaf)
OB3 = (7, 24)                            # kernel ob3, one twiddle-free radix-3 butterfly of three blocks over cnt positions: charge 7 + 24 cnt
OCALL = 10                               # one call of ob2 or ob3: the two or three block addresses (a multiplication and an addition each), the twiddle address, call and return
OCP = (5, 7)                             # kernel ocp of ntt_kern.h (chunked outer transform): z = w x over cnt positions, charge 5 + 7 cnt (parsed and asserted in Leaf)
OAX = (5, 10)                            # kernel oax: z += w x, charge 5 + 10 cnt
OZF = (3, 4)                             # kernel ozf: z = 0, charge 3 + 4 cnt
OCALL_C = 30                             # one call of ocp, oax or ozf in the assembly of a chunk: the two block addresses (a multiplication and an addition each), the exponent i * j1 mod n2 (a multiplication and a reduction of 20), the table address (a multiplication and an addition), call and return
OCALL_I = 31                             # one call of ocp or oax in the accumulation of a chunk: as OCALL_C and one subtraction (the weight w^(-e) is the table entry n2 - e)


def ontt_at(n, cnt):
    """one outer transform of n = 2^a or 3*2^a points at each of cnt positions: the twiddle table (n entries: a multiplication, a store
    and a control each), the radix-3 stage (n/3 calls of ob3) and a radix-2 layers (n/2 calls of ob2 each), every call charged in full"""
    c = 3 * n; q = n
    if n % 3 == 0:
        q = n // 3; c += q * (OCALL + OB3[0] + OB3[1] * cnt)
    lg = q.bit_length() - 1
    assert (1 << lg) == q, n
    return c + lg * (n // 2) * (OCALL + OB2[0] + OB2[1] * cnt)


def pad23(n):
    best = None
    for a in range(0, 33):
        for c in (1, 3):
            v = c << a
            if v >= n and (best is None or v < best): best = v
    assert best is not None, n
    return best


MODE_LOG = {}
OUTER_LIMIT = None                      # elements: outside the squaring loop of stage C a block product uses scheme (b) only if its workspace is at most this (None: no limit)
LIMIT_MULT = 8                       # OUTER_LIMIT = LIMIT_MULT * m (None: no limit); a constant of the algorithm for each r (proof 4.5)
DIRECT_DIV = False                      # scheme (c) in a division: the chunks of a product are accumulated into the output array of the division itself (no separate accumulator); a constant of the algorithm
CHUNK_C = 4                          # scheme (c): number of chunks of the outer points of the block products of stage C (None: no scheme (c) in stage C); a constant of the algorithm for each r (proof 4.5)
CHUNK_D = 4                          # the same for the block products of stage D
SEQ_OUT = False                         # scheme (b) of apply_inv: the two outputs are formed one after the other, so that fewer operand forms are live together; a constant of the algorithm for each r (proof 4.5)


def set_outer_limit(m):
    global OUTER_LIMIT
    OUTER_LIMIT = None if LIMIT_MULT is None else LIMIT_MULT * m
    hgcd.cache_clear(); worst_div.cache_clear(); padded_division_full.cache_clear()
    if 'ld_ontt' in globals(): ld_ontt.cache_clear()        # pos_leand: the outer charge depends on LD_CONV


def chunk_req():
    """the number of chunks asked for the block products of the stage being evaluated (None: scheme (c) is not available there)"""
    return CHUNK_C if CTX['stage'] == 'C' else CHUNK_D if CTX['stage'] == 'D' else None


def ok23(q):
    while q % 2 == 0: q //= 2
    return q in (1, 3)
CTX = {'loop': False, 'seq': False, 'stage': None, 'direct': False}     # loop: True while the products of the squaring loop of stage C are evaluated (no limit applies to them); seq: the outputs of the bilinear form being evaluated (apply_inv) are formed one after the other in scheme (b)
PL = {}                                 # description of the last block product evaluated by conv_bilin_big: scheme, outer length, operand forms, working arrays


def copy_ops(l):                        # copy of l coefficients into the outer-domain array of an operand: a load, a store and the loop step per coefficient
    return 7 * l + 2


def fill_ops(l, n2):                    # the outer-domain form of an operand of l coefficients (n2 arrays of HB points): the copy of the l coefficients, then the zero fill of the n2 HB - l positions
    return copy_ops(l) + 5 * (n2 * HB - l) + 2   # beyond them (a store and the loop step per position): the form comes from the pool, which holds stale data (ruling 3476cad8)


def form_slots(l, mode, n2, pc=1):
    """slots of the transform-domain form of an operand of l coefficients: nblk(l) spectra of NB points (scheme (a), and an operand of one block in every scheme),
    or the n2 outer-domain arrays of HB points of scheme (b), or the n2 / pc arrays of HB points of the chunk of scheme (c)"""
    if mode == 'a' or nblk(l) == 1: return nblk(l) * NB
    return (n2 // pc) * HB


def prod_work(P, nout):
    """slots of the arrays that the block product described by P (a copy of PL) holds besides the forms of its operands and its outputs in coefficient form: the working
    arrays (scheme (a): one accumulator of NB points; scheme (b): one array of NB points per operand form at the current outer point and per output, and the table of the n2
    outer twiddles) and, in scheme (b), further outer-domain arrays for the outputs that have no dead operand form to overwrite (the output of an outer point overwrites a dead operand array of that point)"""
    if P['mode'] == 'a': return [NB]
    if P['mode'] == 'c':      # one chunk: Q arrays of HB points per output that has no dead operand form to overwrite, one array of NB points per operand form and output, the tables, the accumulators
        return [(P['n2'] // P['pc']) * HB] * max(0, nout - P['nf']) + [NB] * P['nwork'] + [P['n2'] + 1, P['n2'] // P['pc']] + list(P['acc'])
    return [P['n2'] * HB] * max(0, nout - P['nf']) + [NB] * P['nwork'] + [P['n2']]            # the last: the table of the n2 outer twiddles


def prod_arrays(P, ops, nout):
    """every transform-domain array live during the block product P: the form of each operand in ops (the operands that are not persistent) and prod_work"""
    if P['mode'] == 'c': ops = list(ops) + list(P['hc'])           # the cached operands have no persistent form in scheme (c): their chunk forms are made at each use
    return [form_slots(l, P['mode'], P['n2'], P.get('pc', 1)) for l in ops] + prod_work(P, nout)


def _gp(n, kb):
    if n <= 0: return 0
    return n * (n + 1) // 2 if n <= kb else kb * (kb + 1) // 2 + (n - kb) * kb


def pairs_upto(ka, kb, s):
    """number of block pairs (i, j) with i + j <= s"""
    if s < 0: return 0
    return _gp(s + 1, kb) - _gp(s + 1 - ka, kb)


def pairs_range(ka, kb, A, B):
    return pairs_upto(ka, kb, B) - pairs_upto(ka, kb, A - 1)


def window_slots(ws, outlen):
    we = ws + outlen
    s0 = max(0, (ws + 1) // HB - 3)
    while (s0 + 2) * HB - 1 <= ws: s0 += 1
    s1 = -(-we // HB) + 2
    while s1 * HB >= we: s1 -= 1
    return s0, s1, we


def slot_cost(s, s0, ws, we, sub):
    lo, hi = s * HB, (s + 2) * HB - 1
    outn = min(NB - 1, we - lo); cnt = min(hi, we) - max(lo, ws)
    ov = 0
    if s > s0: ov = max(0, min((s + 1) * HB - 1, we) - max(s * HB, ws))
    return big_inv(outn) + big_place(cnt, ov, sub)


def chunk_fill_ops(l, Q, pc):
    """assembly of the pc chunks of the outer-domain form of an operand of l coefficients (k = nblk(l) blocks): in every chunk each block is read once with the weight w^(i j1)
    (ocp for the blocks i < Q, which start the arrays, oax for the others; the last block has l - (k - 1) HB positions) and the Q - k arrays that no block reaches are zeroed (ozf)"""
    k = nblk(l); last = l - (k - 1) * HB
    nocp = min(k, Q); noax = k - nocp
    full = lambda ch_, n_: n_ * (OCALL_C + ch_[0] + ch_[1] * HB)
    c = full(OCP, nocp) + full(OAX, noax)
    if nocp == k:                                                 # the last block starts an array: its other HB - last positions are zeroed (ozf; the array comes from the pool, ruling 3476cad8)
        c -= OCP[1] * (HB - last)
        if last < HB: c += OCALL_C + OZF[0] + OZF[1] * (HB - last)
    else: c -= OAX[1] * (HB - last)
    if k < Q: c += (Q - k) * (OCALL_C + OZF[0] + OZF[1] * HB)
    return pc * c


def conv_bilin_big(nout, outlen, groups, ws=0, sub=False, shared=False, cached=False, wrap=False):
    """block version of conv_bilin_cost.  Returns (ops, eps) and describes the scheme used in PL.  Scheme (a) (all block pairs, closed form) or, when it is cheaper and, outside the
    squaring loop, its workspace is within OUTER_LIMIT, the outer-NTT scheme of Grok job 140 (j = 3).  cached: the H operands are persistent (stage C keeps the spectra, or the
    outer-domain arrays, of MU and g from one step to the next); scheme (a) does not transform them again, scheme (b) repeats the inner transform of every outer point of such
    an operand at each use (the persistent outer-domain array has HB elements per point, not NB)."""
    eps = [0] * nout
    for g in groups:
        for s in range(len(g['S'])):
            for h in range(len(g['H'])):
                o, sg = g['prod'].get((s, h), (-1, 0))
                if o >= 0 and not eps[o]: eps[o] = sg
    prods = [[] for _ in range(nout)]
    for g in groups:
        for (si, hi_), (o, sg) in g['prod'].items():
            if o >= 0: prods[o].append((g['S'][si], g['H'][hi_]))
    ops_ = []; hc_ = []
    for g in groups:
        if cached: hc_ += list(g['H'])
        else: ops_ += list(g['H'])
        if not shared: ops_ += list(g['S'])
    pw0, pw1 = big_pw(0), big_pw(1)
    # ---- scheme (a)
    ca = 2 + sum(big_fwd_all(l) for l in ops_)
    ninfo = []
    for k in range(nout):
        if not eps[k] or not prods[k]: continue
        s0, s1, we = window_slots(ws, outlen[k])
        stot = max(nblk(ls) + nblk(lh) - 1 for ls, lh in prods[k])
        A, B = s0, min(s1, stot - 1)
        ninfo.append((k, s0, s1, stot, we))
        if B < A: continue
        npr = sum(pairs_range(nblk(ls), nblk(lh), A, B) for ls, lh in prods[k])
        cnt_s = B - A + 1
        ca += cnt_s * (pw0 - pw1) + pw1 * npr
        edges = sorted(set(range(A, min(A + 3, B + 1))) | set(range(max(B - 2, A), B + 1)))
        for s in edges: ca += slot_cost(s, s0, ws, we, sub)
        mid = cnt_s - len(edges)
        if mid > 0:
            rep = edges[2] + 1
            ca += mid * slot_cost(rep, s0, ws, we, sub)
    # ---- outer scheme
    co = None; n2 = 0; wrapinfo = None
    nf = sum(1 for l in ops_ if nblk(l) > 1); nwork = len(ops_) + len(hc_) + nout
    extra_seq = 0                                                  # scheme (b), outputs one after the other (apply_inv): the operands of several outputs are transformed again for each further output
    if CTX['seq']:
        hm = sum(1 for g in groups for l in g['H'] if nblk(l) > 1)
        sk = [0] * nout
        for g in groups:
            for kind in ('H', 'S'):
                for i_, l in enumerate(g[kind]):
                    outs_ = {o for (si, hi_), (o, sg) in g['prod'].items() if o >= 0 and (hi_ if kind == 'H' else si) == i_}
                    if nblk(l) > 1 and len(outs_) > 1: extra_seq += len(outs_) - 1
                    if kind == 'S' and nblk(l) > 1:
                        for o in outs_: sk[o] += 1
        nf = hm + max(sk)                                          # operand forms live together: those of the H operands and those of the S operands of one output
    if ninfo and max(nblk(l) for l in ops_ + hc_) > 1:
        n2 = 1
        for (k, s0, s1, stot, we) in ninfo: n2 = max(n2, pad23(s1 + 2 if wrap else max(s1 + 2, stot + 1 - s0)))
        co = 2
        for l in ops_:
            if nblk(l) == 1: co += big_fwd(l)
            else: co += n2 * big_fwd(HB) + ontt_at(n2, HB) + fill_ops(l, n2)
        for l in hc_:
            if nblk(l) > 1: co += n2 * big_fwd(HB)             # the inner transform of every outer point of a persistent operand, at each use (a one-block operand is kept as its spectrum)
        co += extra_seq * n2 * big_fwd(HB)
        for (k, s0, s1, stot, we) in ninfo:
            npk = len(prods[k])
            co += n2 * (pw0 + (npk - 1) * pw1) + n2 * big_inv(NB - 1) + n2 * big_place(HB, HB, False) + ontt_at(n2, HB) + big_place(outlen[k], outlen[k], sub)
            if wrap:                                                   # cyclic mod x^(n2 HB) - 1: the upper half of the last slot is added to the first slot, and the known coefficients at positions >= n2 HB (the high half of R^2) are added back
                full = max(ls + lh - 1 for ls, lh in prods[k])
                wc = max(0, full - n2 * HB)
                co += big_place(HB, HB, False) + 10 * wc + 2
                wrapinfo = (n2 * HB, wc)
    # ---- chunked outer scheme (c): the outer points are processed in pc chunks (four-step split n2 = pc * Q); the operands stay in coefficient form, a chunk holds Q outer points
    cc_ = None; pcs = 1; accs = []; acck = []
    pc_req = chunk_req()
    if pc_req is not None and ninfo and max(nblk(l) for l in ops_ + hc_) > 1:
        pcs = pc_req if (n2 % pc_req == 0 and ok23(n2 // pc_req)) else 1
        Q = n2 // pcs
        cc_ = 2 + 3 * (n2 + 1)                                    # the table of the n2 + 1 outer twiddles
        for l in ops_ + hc_:
            if nblk(l) > 1: cc_ += n2 * big_fwd(HB) + chunk_fill_ops(l, Q, pcs) + pcs * ontt_at(Q, HB)
        for l in ops_:
            if nblk(l) == 1: cc_ += big_fwd(l)                    # an operand of one block: its spectrum, once
        for (k, s0, s1, stot, we) in ninfo:
            npk = len(prods[k])
            A_, B_ = s0, min(s1, stot - 1)
            tc = max(0, min(n2, B_ - A_ + 2))                     # the output blocks A..B + 1 (the high half of slot B goes to block B + 1)
            if not CTX['direct']: accs.append(tc * HB); acck.append(k)
            cc_ += n2 * (pw0 + (npk - 1) * pw1) + n2 * big_inv(NB - 1) + n2 * big_place(HB, HB, False) + pcs * ontt_at(Q, HB) + big_place(outlen[k], outlen[k], sub)
            if CTX['direct']:      # the pieces are accumulated into the destination array itself: only the positions of the window, the first chunk assigns (ocp), the others add (oax)
                cwin = lambda sp_: min((sp_ + 1) * HB, ws + outlen[k]) - max(sp_ * HB, ws)
                edges_ = sorted(set(range(A_, min(A_ + 5, A_ + tc))) | set(range(max(A_, A_ + tc - 5), A_ + tc)))
                for sp_ in edges_:
                    cw = cwin(sp_)
                    if cw > 0: cc_ += (OCALL_I + OCP[0] + OCP[1] * cw) + (pcs - 1) * (OCALL_I + OAX[0] + OAX[1] * cw)
                if tc > len(edges_):                                  # the pieces between the first five and the last five lie inside the window (asserted): HB positions each
                    assert cwin(A_ + 5) == HB and cwin(A_ + tc - 6) == HB, (A_, tc, ws, outlen[k])
                    cc_ += (tc - len(edges_)) * ((OCALL_I + OCP[0] + OCP[1] * HB) + (pcs - 1) * (OCALL_I + OAX[0] + OAX[1] * HB))
            else:
                cc_ += tc * (OCALL_I + OCP[0] + OCP[1] * HB) + (pcs - 1) * tc * (OCALL_I + OAX[0] + OAX[1] * HB)
    # 10-17 (ruling fb911c77 H-COST-OUTER): the outer transform is charged by its own kernels ob3 and ob2 (ontt_at), every call in full, integer charges only;
    # the scheme with the smaller charge is used, provided (outside the squaring loop) the workspace of scheme (b), max(operand forms live together, outputs) * n2 * HB + nwork * NB, is within OUTER_LIMIT.
    lim = None if CTX['loop'] else OUTER_LIMIT
    if pc_req is not None:
        use_c = cc_ is not None and cc_ < ca                      # a stage with chunks: scheme (a) or scheme (c), the smaller charge (no scheme (b))
        use_b = False
    else:
        use_c = False
        use_b = co is not None and co < ca and (lim is None or max(nf, 1 if CTX['seq'] else nout) * n2 * HB + nwork * NB <= lim)
    if use_c:
        nfc = sum(1 for l in ops_ + hc_ if nblk(l) > 1)
        PL.clear(); PL.update(seq=False, mode='c', n2=n2, pc=pcs, nf=nfc, nwork=len(ops_) + len(hc_) + nout, nout=nout, ops=tuple(ops_), hc=tuple(hc_), ca=ca, co=co, cc=cc_, acc=tuple(accs), acck=tuple(acck))
        MODE_LOG['chunk'] = MODE_LOG.get('chunk', 0) + 1
        return cc_, eps
    PL.clear(); PL.update(wrap=bool(wrap) and use_b, wrapinfo=wrapinfo if use_b else None, seq=bool(CTX['seq']) and use_b, mode='b' if use_b else 'a', n2=n2 if use_b else 0, nf=nf, nwork=nwork, nout=nout, ops=tuple(ops_), hc=tuple(hc_), ca=ca, co=co)
    if use_b:
        MODE_LOG['outer'] = MODE_LOG.get('outer', 0) + 1
        return co, eps
    MODE_LOG['a'] = MODE_LOG.get('a', 0) + 1
    return ca, eps


def conv_sq_big(ln, outlen):
    return conv_bilin_big(1, [outlen], [dict(H=[ln], S=[ln], prod={(0, 0): (0, 1)})], shared=True)[0] + 4


def conv_mulc_big(ln, lenB, ws, outlen, sub=False, cached=False, wrap=False):
    return conv_bilin_big(1, [outlen], [dict(H=[lenB], S=[ln], prod={(0, 0): (0, 1)})], ws, sub, False, cached, wrap)[0] + 6


def product_peak(T, Pl, nout=1):
    """the transform-domain arrays of the product just evaluated (Newton phase of stage C), allocated at its start and freed at its end"""
    arr = prod_arrays(PL, PL['ops'], nout) if Pl.a > BIGA else [Pl.n]       # a product that fits one transform: its transform row
    ids = [T.new_fp(x) for x in arr]  # pool:H
    for x in ids: T.free(x)


def persist_ops(l, P):
    """creation of the persistent form of a cached operand of l coefficients: its spectra (scheme (a), or one block), or the copy into the outer-domain array and the outer transform"""
    if nblk(l) == 1: return big_fwd(l)
    if P['mode'] == 'c': return 0                                 # scheme (c): the coefficient array itself is kept; its chunk forms are made at each use
    if P['mode'] == 'a': return big_fwd_all(l)
    return fill_ops(l, P['n2']) + ontt_at(P['n2'], HB)


def persist(T, l, P):
    """the persistent form of a cached operand of l coefficients: allocated, made from the coefficient array (with the table of the outer twiddles in scheme (b)); returns its slot"""
    sl = T.new_fp(form_slots(l, P['mode'], P['n2']))
    if P['mode'] == 'b' and nblk(l) > 1:
        tw = T.new_fp(P['n2']); T.free(tw)
    T.ops += persist_ops(l, P)
    return sl


def regen_ops(l, P, place):
    """regeneration of the l coefficients of g from its persistent form P.  Scheme (a) (and one block): the inverse transform of each block spectrum into one work array of NB points,
    block by block; for the shift by x (place = False) the factor 1/NB is folded into the multiplier (one multiplication), at the end of stage C (place = True) the block is placed with
    its scaling into the array of g.  Scheme (b): the inverse outer transform of the persistent array in place and its scaling by 1/n2 (a load, a multiplication, a store and the loop
    step per coefficient); for the shift the forward outer transform that restores the form follows; at the end of stage C the blocks are copied into the array of g"""
    k = nblk(l)
    if P['mode'] == 'a' or k == 1:
        last = l - (k - 1) * HB
        if place: return (k - 1) * (big_inv(HB) + big_place(HB, 0, False)) + big_inv(last) + big_place(last, 0, False) + 6 * k
        return (k - 1) * big_inv(HB) + big_inv(last) + 6 * k + 1
    return (1 if place else 2) * ontt_at(P['n2'], HB) + 8 * l + 2 + (copy_ops(l) if place else 0)


def regen_work(T, P, l):
    """allocation and free of the work array of a regeneration of g (one array of NB points, or the table of the n2 outer twiddles)"""
    x = T.new_fp(NB if (P['mode'] == 'a' or nblk(l) == 1) else P['n2']); T.free(x)  # pool:H


def chunk_phase(S, P, nout=1, hi=False, ha=None):
    """the arrays of a product of scheme (c) while its chunks are processed: the chunk forms of all operands, the working arrays, the tables and the accumulators; returns (the ids of
    the accumulators, a function that frees everything else).  The coefficient arrays of the operands are the caller's and stay live.  hi: the list (high = True) of the arrays other than
    the accumulators; ha: the list of the accumulators (None = hi)"""
    arr = prod_arrays(P, P['ops'], nout); na = len(P['acc']); nr = len(arr) - na
    ha = hi if ha is None else ha
    if hi: rest = [S.new_fp(x) for x in arr[:nr]]  # pool:H
    else: rest = [S.new_fp(x) for x in arr[:nr]]
    if ha: acc = [S.new_fp(x) for x in arr[nr:]]  # pool:H
    else: acc = [S.new_fp(x) for x in arr[nr:]]
    def done():
        for x in rest: S.free(x)
    return acc, done


def step_walk(base, m, Psq, Pq, Pg):
    """the arrays of one squaring step of the streamed schedule (proof 4.5), with every allocation and free charged: F holds R and receives the low half of R^2 and then the
    result; the persistent forms of MU and g are the caller's.  Psq, Pq, Pg describe the three products (copies of PL).  Returns the trace of one step (all arrays freed).
    A product of scheme (c) keeps its operand (R, T1, q) in coefficient form until its last chunk is processed, accumulates its output in the accumulators and places it afterwards."""
    S = Tr(base)
    if Psq['mode'] == 'c':
        acc, done = chunk_phase(S, Psq, hi=True, ha=False)           # the accumulators of the square R^2 (two operand-lengths, the largest arrays of the step) go to the low list, above F
        done()                                                        # R is dead after the last chunk: the low half of R^2 is placed into F
        sT1 = S.new_fp(m - 1)                                         # the high half of R^2  # pool:H
        for x in acc: S.free(x)
    else:
        fR = S.new_fp(form_slots(m, Psq['mode'], Psq['n2']))              # the form of R; F is free to receive the low half of R^2  # pool:H
        wk = [S.new_fp(x) for x in prod_work(Psq, 1)]  # pool:H
        sT1 = S.new_fp(m - 1)                                             # the high half of R^2  # pool:H
        for x in wk: S.free(x)
        S.free(fR)
    if Pq['mode'] == 'c':
        acc, done = chunk_phase(S, Pq, hi=True)
        done(); S.free(sT1)                                           # T1 is dead after the last chunk
        sq = S.new_fp(m - 1)                                          # the quotient estimate q  # pool:H
        for x in acc: S.free(x)
    else:
        fT = S.new_fp(form_slots(m - 1, Pq['mode'], Pq['n2']))            # the form of T1; T1 is free once it is transformed (kept until the end of the step when (q g) is formed cyclically)  # pool:H
        if not Pg.get('wrap'): S.free(sT1)
        wk = [S.new_fp(x) for x in prod_work(Pq, 1)]  # pool:H
        sq = S.new_fp(m - 1)                                              # the quotient estimate q  # pool:H
        for x in wk: S.free(x)
        S.free(fT)
    if Pg['mode'] == 'c':
        acc, done = chunk_phase(S, Pg, hi=True)
        done(); S.free(sq)                                            # q is dead after the last chunk; (q g)[0..m-1] is subtracted from F by the placement
        for x in acc: S.free(x)
    else:
        fq = S.new_fp(form_slots(m - 1, Pg['mode'], Pg['n2']))            # the form of q; q is free once it is transformed  # pool:H
        S.free(sq)
        wk = [S.new_fp(x) for x in prod_work(Pg, 1)]                      # (q g)[0..m-1] is subtracted from F by the placement  # pool:H
        for x in wk: S.free(x)
        S.free(fq)
        if Pg.get('wrap'): S.free(sT1)
    assert S.cur == 0 and S.cnt == 0
    return S




def ebit(E, i): return (E >> i) & 1


def powx_lean(m, b, E=PM1H, sg=None):
    """sg: the array g of the caller (stage C frees it after its form is made)"""
    CTX['stage'] = 'C'
    try: return powx_vd(m, b, E, sg) if vd_active(m) else powx_lean_(m, b, E, sg)
    finally: CTX['stage'] = None


def powx_lean_(m, b, E=PM1H, sg=None):
    T = Tr(b)
    PN, c1 = plan3_for_len(2 * m - 1); PNp, c2 = plan3_for_len(m + 1)
    T.ctl(c1 + c2)
    N, Np = PN.N, PNp.N
    BIG = PN.a > BIGA
    if BIG:
        assert PNp.a > BIGA
        # block mode, streamed (proof 4.5): g and F are the arrays of the caller (F holds the reversed g in the Newton phase and the state R in the loop); the Newton phase holds
        # MU (m-1) and the product buffer Y (m-1) besides them; the loop holds the persistent forms of MU and g and, per step, the arrays of step_walk
        sM = T.new_fp(m - 1); sY = T.new_fp(m - 1)  # pool:H
    else:
        sY = T.new_fp(N); sT = T.new_fp(PN.n); sM = T.new_fp(m - 1)
    # newton_lean
    L = m - 1
    T.ld(L); T.st(L); T.loopc(L); T.ctl(L)
    T.ctl(4 + 8); T.st(1)
    l = 1
    while l < L:
        l2 = min(2 * l, L)
        T.ctl(8)
        P1, c = plan3_for_len(l2 + l - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P1, l, l2, 0, l2))
        if BIG:
            assert P1.a > BIGA or P1.N <= m - 1                      # a product that fits one transform uses Y (m-1 slots) as its transform buffer
            product_peak(T, P1)
        T.ctl(plan_invN_ops(P1))
        T.ops += l2 - l                                       # pl_run MULC
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        P2, c = plan3_for_len(l2 - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P2, l2 - l, l, 0, l2 - l))
        if BIG:
            assert P2.a > BIGA or P2.N <= m - 1                      # a product that fits one transform uses Y (m-1 slots) as its transform buffer
            product_peak(T, P2)
        T.ctl(plan_invN_ops(P2))
        T.ops += 2 * (l2 - l)                                 # pl_run NEGMULC: mul + sub per element
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        l = l2
    T.ld(L); T.st(L); T.loopc(L // 2); T.ctl(2 * (L // 2))
    # prefix + scale
    T.ctl(plan_invN_ops(PN)); T.ctl(plan_invN_ops(PNp)); T.ops += 1
    T.ops += m - 1; T.ld(m - 1); T.st(m - 1); T.loopc(m - 1)
    gamma = N - (m - 2)
    if BIG:
        # the three products of a step, in the order of the step; the two cached operands (MU, g) are persistent
        CTX['loop'] = True
        try:
            sq_ops = conv_sq(PN, m, 2 * m - 1); Psq = dict(PL)
            q_ops = conv_mulc_otf(PN, m - 1, m - 1, gamma, m - 1, False, True); Pq = dict(PL)
            qg_ops = conv_mulc_otf(PNp, m - 1, m + 1, 0, m, True, True, bool(MIDPROD & 1)); Pg = dict(PL)
        finally:
            CTX['loop'] = False
        T.free(sY)                                            # the Newton phase is over: the persistent forms replace MU and the workspace
        keepM = Pq['mode'] == 'c' and nblk(m - 1) > 1         # scheme (c): MU and g stay in coefficient form (their chunk forms are made at each use, charged in the products)
        keepG = Pg['mode'] == 'c' and nblk(m + 1) > 1
        sPM = None if keepM else persist(T, m - 1, Pq)
        if not keepM: T.free(sM)
        sPG = None if keepG else persist(T, m + 1, Pg)
        if not keepG: T.free(sg)                              # g is freed: it is regenerated from its form for each shift by x and, at the end of stage C, for stage D
    top = 255
    while top > 0 and not ebit(E, top):
        top -= 1; T.ctl(12)
    v = 1; bit = top
    while bit >= 1 and ((v << 1) | ebit(E, bit - 1)) < m:
        v = (v << 1) | ebit(E, bit - 1); bit -= 1; T.ctl(25)
    T.st(m); T.loopc(m)
    T.ctl(plan_invN_ops(PN)); T.st(1)
    steps = bit
    lim = (2 * m - 2 - Np + 1) if 2 * m - 2 >= Np else 0
    lim = min(lim, m)
    if BIG:      # F holds R and receives the low half of R^2; T1 is read from its own array; q is placed into its array; (q g)[0..m-1] is subtracted from F by the placement
        S = step_walk(T.here(), m, Psq, Pq, Pg)
        step = sq_ops + 8 + q_ops + qg_ops + S.ops
    else:
        step = conv_sq(PN, m, 2 * m - 1) + 8
        step += for8(lim) + 7 * lim + for8(m - lim) + 4 * (m - lim) + for8(m - 1) + 4 * (m - 1)
        step += conv_mulc_otf(PN, m - 1, m - 1, gamma, m - 1) + conv_mulc_otf(PNp, m - 1, m + 1, 0, m)
        step += for8(m) + 7 * m
    step += 14 + 6
    mulx = 2 + for8(m - 1) + 8 * (m - 1) + 2 + 4
    nset = sum(ebit(E, b) for b in range(bit))
    if BIG and not keepG:      # each shift by x regenerates the coefficients of g from the persistent form (the work array of the regeneration is allocated and freed in the shift)
        Mw = Tr(T.here()); regen_work(Mw, Pg, m + 1); assert Mw.cur == 0
        mulx += Mw.ops + regen_ops(m + 1, Pg, False)
    T.ops += steps * step + nset * mulx
    if BIG:
        T.peak = max(T.peak, T.cur + S.peak); T.pcnt = max(T.pcnt, T.cnt + S.pcnt)
        if not keepG: T.peak = max(T.peak, T.cur + Mw.peak)
        T.ev.append(('R', steps, tuple(S.ev)))
        if not keepG: T.ev.append(('R', nset, tuple(Mw.ev)))      # every step and every shift allocates and frees its arrays: the group restores the allocator
    T.ops += 1 + m; T.ld(m); T.st(m); T.loopc(m)
    T.ctl(2 + 500)
    if BIG:      # the loop is over: MU's form is freed, g is regenerated into an array of its own for stage D, then its form is freed (scheme (c): MU is freed, g is the array it always was)
        if keepM: T.free(sM)
        else: T.free(sPM)
        if not keepG:
            sg2 = T.new_fp(m + 1); regen_work(T, Pg, m + 1); T.ops += regen_ops(m + 1, Pg, True)
            T.free(sPG)
        else: sg2 = sg                                          # scheme (c): g stayed the caller's array; it goes to stage D as it is
    else:
        T.free(sY); T.free(sT); T.free(sM)
    info = dict(steps=steps, nset=nset, PN=PN, PNp=PNp, step=step, mulx=mulx)
    if BIG: info.update(modes=(Psq['mode'], Pq['mode'], Pg['mode']), n2=(Psq['n2'], Pq['n2'], Pg['n2']), sg2=sg2)
    return T, info


# ---------------------------------------------------------------- stage C in the value domain (VDC = 1): pos_vdc pricing, the method of bradcush 1aa56884 (its proof 4.6), charged in this model's primitives
# The residue is held by its values on O1 = C_0 u ... u C_(K-1) and O2 = C_K u ... u C_(2K-1), C_k = 5^k H, H the subgroup of order h = 2^32, K = ceil((m+1)/h), n1 = K h >= m + 1
# (each of O1, O2 is the union of K cosets, n1 points).  A squaring step is two pointwise passes and two extensions (change of point set); an extension is an inner transform of h
# points per coset (one row of the passes of 4.2, in place) and, per inner position, one cyclic convolution over the coset index with a fixed kernel (Lagrange interpolation at the
# geometric nodes z^k, z = 5^h).  The convolutions of a group of VCNT positions run in a group buffer with one row of L elements per position (position-major: the copies into and out
# of it are strided, one address operation per element charged); each row is one cyclic convolution of L points with the stored spectrum of the kernel, charged by the row kernels of
# this model (conv_core_row: forward passes, the fused pass with the pointwise product by the stored spectrum, inverse passes; for L = 3 * 2^a with the radix-3 input and output
# stages stageA_fwd / stageA_inv, as conv_sq does).
VDC = 1              # stage C in the value domain (1) or the coefficient-domain squaring of 4.5 (0); a constant of the algorithm
VD_H = 1 << 25       # h: the order of the subgroup H; the inner transform of h points is one row of passes (plan rows = 1, a = 32), in place on a coset
VCNT = 1 << 5        # inner positions per group of the geometric phase
VSHIFT = 2           # the start monomial is S^v, v = (the largest power of two below m) >> VSHIFT, a multiple of h: VSHIFT more squaring steps, a shorter Newton reciprocal
VD_CALL = 10         # one call of an inner transform: the coset address (a multiplication and an addition), the plan and twiddle arguments, call and return
VD_ROW = 16          # one row of a group copy with a running factor: the factor and its step loaded (LD 2 = 4), the factor stored back (ST 1 = 2), two addresses (4), call, entry, exit (6)
VD_ROWC = 12         # one row of a group copy with a per-row constant: the constant loaded (2), two addresses (4), call, entry, exit (6)
VD_PWC = 14          # one coset of a pointwise pass: its constants loaded (1/M(n_k), u_k, the factor of the coset) and the addresses
VD_GROUP = 20        # one group of the geometric phase: its position offset, the buffer and table addresses, the calls
VD_SPLIT = 0         # pos_leand: g and R in two pieces: the base of a coset is selected (a comparison and a branch) at every coset access of a pass (2), else 0


def vd_active(m):
    """the value-domain stage C is used (VDC = 1) where it is defined: either the start monomial v (the largest power of two below m, shifted by VSHIFT) is a multiple of h,
    or h covers the whole residue in one coset (K = 1, h >= m + 1, bradcush 4bcabff8): the start monomial x^v is replaced by X^(v)(X^h mod g - 1) and v need not divide h"""
    return bool(VDC) and 1 <= VD_H.bit_length() - 1 <= BIGA and (m.bit_length() - 1 - VSHIFT >= VD_H.bit_length() - 1 or VD_H >= m + 1)


def vd_plan(L):
    """the plan of a cyclic convolution of L = 2^a or 3 * 2^a points (a <= 32: the roots of unity exist in F_p)"""
    rows = 3 if L % 3 == 0 else 1
    a = (L // rows).bit_length() - 1
    Pl, c = make_plan(rows, a)
    assert Pl.N == L and a <= BIGA, L
    return Pl, c


def vd_inv1():
    """one field inversion (fp_inv): the power p - 2 and its control"""
    return powcost(PM2) + INV_CTL


def vd_dims(m, E=PM1H):
    """the dimensions of the value-domain stage C for the modulus degree m: K, n1, the convolution lengths, the start exponent v, the steps, the Barrett length ell"""
    h = VD_H; K = -(-(m + 1) // h); n1 = K * h
    if TRC: n1 = tr_dims()[3]; assert K == 1 and n1 >= m + 1
    assert n1 >= m + 1                                                     # O1 and O2 each hold n1 >= m + 1 points: a polynomial of degree <= m is determined by its values
    Lx = pad23(2 * K)                                                      # extensions and interpolations (indices <= 2K - 1 < Lx, no wrap into the outputs)
    Le = None if K == 1 else (pad23(3 * K - 1) if 3 * K - 1 <= 3 << BIGA else None)   # K=1: no geometric phase; one chirp evaluation of g at the 2K nodes; None: two evaluations of K nodes at Lx
    top = 255; zc = 0
    while top > 0 and not ebit(E, top): top -= 1; zc += 1
    v = 1; bit = top; vb = 0
    while bit >= 1 and ((v << 1) | ebit(E, bit - 1)) < m:
        v = (v << 1) | ebit(E, bit - 1); bit -= 1; vb += 1
    for _ in range(VSHIFT):
        assert ebit(E, bit) == 0
        v >>= 1; bit += 1
    assert v & (v - 1) == 0 and (v % h == 0 or h >= m + 1)                 # x^v = u_k^v on the coset C_k (K>1); K=1 (h >= m+1): the start X^(v)(X^h mod g - 1), v need not divide h
    ell = v + n1 - m + 1                                                   # q = floor(X^v P1 / g) has ell = deg + 1 coefficients
    Kq = -(-ell // h); Lq = pad23(Kq + K - 1)
    return dict(h=h, K=K, n1=n1, Lx=Lx, Le=Le, v=v, steps=bit, top=top, zc=zc, vb=vb, ell=ell, Kq=Kq, Lq=Lq,
                nset=sum(ebit(E, i) for i in range(bit)))


def vd_gslots(m):
    """the array of g (stages A to D): n1 slots; the values of g on O2 are written into it in place (stage C, step 2) and it goes to stage D as g in coefficient form"""
    return vd_dims(m)['n1']


def vd_conv(Pl, kin, outlen):
    """one cyclic convolution of one position's row (kin live inputs) with a stored kernel spectrum: rows = 1: the zero fill of the other L - kin entries and the row kernels in place;
    rows = 3: the radix-3 input stage from the row into the transform buffer, the three row convolutions, the output stage back into the row (outlen outputs); 5: the position loop and address"""
    if Pl.rows == 1:
        z = Pl.N - kin
        return 5 + 2 * z + for8(z) + conv_core_row(Pl, 'mul')
    return 5 + stageA_fwd(Pl, kin) + 3 * conv_core_row(Pl, 'mul') + 2 + stageA_inv(Pl, outlen)


def vd_rows(cnt, rows, per, row_over):
    """rows of cnt elements copied between a coset array and the group buffer: per element `per` (running factor: a load, the multiplication by the factor, the multiplication of
    the factor by its step, a store, the strided address = 7; per-row constant: a load, a multiplication, a store, the strided address = 6), per row row_over, loops by the eight-element rule"""
    return rows * (row_over + VD_SPLIT + for8(cnt) + per * cnt) + 3 * rows + 2


def vd_phase(per_group):
    ng = VD_H // VCNT
    return ng * (VD_GROUP + per_group) + 3 * ng + 2


def vd_reset(rows):
    """the running factors of a phase set from their base table: per row a load and a store, the loop"""
    return 7 * rows + 2


def vd_scale(n):
    """one running-factor pass over n elements (per element: a load, the multiplication by the factor, the multiplication of the factor by its step, a store, the strided address = 7),
    the loop by the eight-element rule, the entry and exit: the coset-change twiddle of the single-coset (K = 1) extension and the u_k^j scalings of its evaluation / interpolation"""
    return 5 + for8(n) + 7 * n


def vd_ext(K, Px):
    """the geometric phase of one extension (O1 -> O2 or O2 -> O1): K rows in with their factors, one convolution per position, K rows out with their factors.
    K = 1 (bradcush 4bcabff8, a single coset holds the whole residue): no between-coset convolution; the change of point set is the coset-change twiddle folded between the inverse and
    forward inner transforms of `ext`, one running-factor pass over the h coefficients."""
    if K == 1:
        return vd_scale(VD_H)
    return 2 * vd_reset(K) + vd_phase(vd_rows(VCNT, K, 7, VD_ROW) + VCNT * vd_conv(Px, K, 2 * K) + vd_rows(VCNT, K, 7, VD_ROW))


def vd_eval(kin, kout, Pl):
    """chirp evaluation of kin coefficient rows at kout geometric nodes: rows in with a per-row constant, one convolution with the chirp per position, kout rows out with their factors.
    kin = kout = 1 (K = 1): one geometric node, the chirp correlation is the identity; only the per-coefficient u_0^j scaling remains (one running-factor pass over h)."""
    if kin == 1 and kout == 1:
        return vd_scale(VD_H)
    return vd_reset(kout) + vd_phase(vd_rows(VCNT, kin, 6, VD_ROWC) + VCNT * vd_conv(Pl, kin, kin + kout - 1) + vd_rows(VCNT, kout, 7, VD_ROW))


def vd_interp(K, Px):
    """interpolation at K geometric nodes back to coefficient form: rows in with their factors, the chirp correlation, the K results moved with a per-index constant (two loads, a
    multiplication, a store), the correlation with the coefficients of M, rows out with a per-row constant.
    K = 1: one node, both correlations are the identity; the inverse inner transform returns the coefficients directly, only the u_0^{-j} scaling remains (one running-factor pass over h)."""
    if K == 1:
        return vd_scale(VD_H)
    mid = vd_conv(Px, K, 2 * K - 1) + 7 * K + for8(K) + 4 + vd_conv(Px, K, 2 * K)
    return vd_reset(K) + vd_phase(vd_rows(VCNT, K, 7, VD_ROW) + VCNT * mid + vd_rows(VCNT, K, 6, VD_ROWC))


def vd_inner(ncos, inv, PH):
    """ncos inner transforms of h points, one per coset, in place (the first pass may read another array: the same charges)"""
    one = inv_passes(PH, PH.np - 1) if inv else fwd_passes(PH, PH.np)
    return ncos * (one + VD_CALL + VD_SPLIT) + 3 * ncos + 2


def vd_pw(ncos, per):
    """a pointwise pass over ncos cosets of h values: per element `per`, per coset VD_PWC, loops by the eight-element rule"""
    return ncos * (VD_PWC + VD_SPLIT + for8(VD_H) + per * VD_H) + 3 * ncos + 2


def vd_batch_inv(ncos):
    """-1/g in place on ncos cosets (Montgomery's batch inversion): per coset the prefix products into the auxiliary array (a load, a multiplication, a store), one inversion and its
    zero test (a zero prefix ends the trial: g vanishes on O1), the backward pass (two loads, two multiplications, the negation, a store), 20 for the coset"""
    h = VD_H
    return ncos * (20 + VD_SPLIT + for8(h) + 5 * h + vd_inv1() + 2 + for8(h) + 9 * h) + 3 * ncos + 2


def vd_spectrum(Pl, nent):
    """a fixed kernel of L points: nent entries computed (each charged as one inversion and 20 operations), the rest zero (rows = 1: zero fill; rows = 3: the radix-3 input stage reads
    the nent entries only), the forward transform (all passes: the fused pass of vd_conv multiplies by it)"""
    c = nent * (vd_inv1() + 20) + 4
    if Pl.rows == 1:
        z = Pl.N - nent
        return c + 2 * z + for8(z) + fwd_passes(Pl, Pl.np)
    return c + stageA_fwd(Pl, nent) + 3 * fwd_passes(Pl, Pl.np)


VD = {}              # description of the last value-domain stage C (filled by powx_vd)


def powx_vd(m, b, E=PM1H, sg=None):
    """stage C in the value domain.  Entry: g in coefficient form in the caller's array sg of n1 slots (stage A; its slots above m are zeroed here).  Exit: R = S^E mod g in an array of
    n1 slots (the first allocation of the stage, at the low end) and g in coefficient form in sg; both go to stage D.  Returns (Tr, info)."""
    if TRC: return powx_tr(m, b, E, sg)
    T = Tr(b)
    d = vd_dims(m, E)
    h, K, n1, ell, Kq = d['h'], d['K'], d['n1'], d['ell'], d['Kq']
    assert sg is not None and (sum(int(x) for x in sg) if isinstance(sg, tuple) else int(sg)) == n1
    PH, c0 = make_plan(1, h.bit_length() - 1); assert PH.N == h
    Px, c1 = vd_plan(d['Lx']); Pq, c2 = vd_plan(d['Lq'])
    Pe, c3 = vd_plan(d['Le']) if d['Le'] else (None, 0)
    T.ctl(c0 + c1 + c2 + c3)
    T.ctl(12 * d['zc'] + 25 * d['vb'] + 4 * VSHIFT)                        # the exponent: its leading bit, the start monomial, the shift
    # tables (per trial): 30 K constants (u_k, 1/u_k, the base factors of the copies, 1/M(n_k), u_k^v M(n_k), M'(z^k)^-1, M(z^(K+t)), M2'^-1, M2(z^t) z^-t, the chirp scales, the
    # coefficients mu_i of M), each charged as two inversions and 60 operations; the table of omega^i in transform order (h entries); the kernel spectra
    if K == 1:
        spec = []                                                          # K = 1: a single coset holds the whole residue; there is no geometric-phase convolution, so no kernel spectra
    else:
        spec = [(Px, 2 * K), (Pq, Kq + K - 1), (Px, 2 * K - 1), (Px, K + 1)]   # extension kernel; chirp of the evaluation of q; chirp of the interpolation; the coefficients of M
        if Pe: spec.append((Pe, 3 * K - 1))                               # chirp of the evaluation of g at the 2K nodes (one convolution of length Le)
    NTAB = 30 * K
    sR2 = None
    if ALLOC_FIX: sR2 = tuple([T.new_fp(x) for x in sg]) if isinstance(sg, tuple) else T.new_fp(n1)   # alloc-order fix (10-19, default off): R in coefficient form allocated before the tables of the stage, so that it is the bottom of the low end
    sTab = T.new_fp(NTAB + h + sum(P_.N for P_, _ in spec))
    T.ctl(NTAB * (2 * vd_inv1() + 60) + 10 * h + sum(vd_spectrum(P_, n_) for P_, n_ in spec))
    Lmax = max([P_.N for P_, _ in spec] or [1])
    sB1 = T.new_fp(VCNT * Lmax)                                           # the group buffer: one row of Lmax elements per position
    sBT = T.new_fp(Lmax) if any(P_.rows == 3 for P_, _ in spec) else None # the transform row of a convolution of 3 * 2^a points
    zg = n1 - (m + 1); T.st(zg); T.ctl(for8(zg))                          # the slots of g above its m + 1 coefficients are zeroed (the rows of g are read whole in step 2)
    if sR2 is None: sR2 = tuple([T.new_fp(x) for x in sg]) if isinstance(sg, tuple) else T.new_fp(n1)       # R on O2 (pos_leand: the pieces of g), then R in coefficient form for stage D (allocated first: the bottom of the low end)
    sR1 = T.new_fp(n1)                                                    # q (its first ell elements) from step 1 to step 3, then R~ on O1 (or u0 on O1 / O2)
    # (1) Barrett start: the reciprocal of the reversed g modulo X^ell (Newton, the products of 4.5), then q = rev(rev(X^v P1) mod X^ell * reciprocal mod X^ell)
    if STREAMC:
        sG = sM = None                                                   # rival 716c3818 schedule: the reversed g and the reciprocal are not kept in arrays of their own; they are streamed through the one folded transform buffer sF (allocated below)
    else:
        sG = T.new_fp(ell)  # pool:H
        sM = T.new_fp(ell)  # pool:H
    L = ell
    # For VD_H < 2^32 the final Newton products can be padded above ell.
    # Keep the paper-account work buffer large enough for every one-transform product.
    Ymax = L
    _yl = 1
    while _yl < L:
        _yl2 = min(2 * _yl, L)
        _yp1, _ = plan3_for_len(_yl2 + _yl - 1)
        _yp2, _ = plan3_for_len(_yl2 - 1)
        Ymax = max(Ymax, _yp1.N, _yp2.N)
        _yl = _yl2
    if STREAMC:
        sF = T.new_fp(Ymax)  # pool:H
        sY = sF                                                          # the single folded N'=N/2 transform buffer: in-place squaring (no product buffer), the Barrett reciprocal streamed into it (no stored MU), half-length folds
    else:
        sY = T.new_fp(Ymax)  # pool:H
    T.ld(L); T.st(L); T.loopc(L); T.ctl(L)                                # the reversed top ell coefficients of g
    T.ctl(4 + 8); T.st(1)
    l = 1
    while l < L:
        l2 = min(2 * l, L)
        T.ctl(8)
        P1, c = plan3_for_len(l2 + l - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P1, l, l2, 0, l2))
        assert P1.a > BIGA or P1.N <= Ymax                              # a product that fits one transform uses Y as its transform buffer
        if P1.a > BIGA: product_peak(T, P1)
        T.ctl(plan_invN_ops(P1))
        if STREAMC: T.ctl(for8(P1.N) + 5 * P1.N)                        # lever 1 (in-place squaring, no product buffer): the product is folded back in place in sF (F[i]:=Y[i]+Y[i+N'], Y:=F-Y) - one extra add/sub pass over the transform, charged
        T.ops += l2 - l
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        P2, c = plan3_for_len(l2 - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P2, l2 - l, l, 0, l2 - l))
        assert P2.a > BIGA or P2.N <= Ymax
        if P2.a > BIGA: product_peak(T, P2)
        T.ctl(plan_invN_ops(P2))
        if STREAMC: T.ctl(for8(P2.N) + 5 * P2.N)                        # lever 1: in-place fold of the second Newton product, one extra pass charged
        T.ops += 2 * (l2 - l)
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        l = l2
    if STREAMC: T.free(sF)                                               # the single folded buffer is freed; g and the reciprocal were never kept in arrays of their own
    else: T.free(sY); T.free(sG)
    PQ, c = plan3_for_len(2 * ell - 1)
    sTt = T.new_fp(max(ell, PQ.N))  # pool:H; include the padded final product transform
    T.st(ell); T.ctl(for8(ell)); T.ctl(Kq * (vd_inv1() + 30))              # rev(X^v P1) mod X^ell: zero fill, the Kq coefficients mu_i at the multiples of h
    T.ctl(c)
    if STREAMC: T.ctl(fwd_passes(PQ, PQ.np) + (stageA_fwd(PQ, ell) if PQ.rows == 3 else 0))   # lever 2 (reciprocal streamed, not stored): the reciprocal is re-formed into the transform buffer for the quotient product - one extra forward transform charged
    T.ctl(conv_mulc_otf(PQ, ell, ell, 0, ell))                            # q (reversed) into the first ell elements of R1, window [0, ell)
    if PQ.a > BIGA: product_peak(T, PQ)
    T.ctl(plan_invN_ops(PQ))
    if STREAMC: T.free(sTt)                                               # sM was never allocated under STREAMC
    else: T.free(sTt); T.free(sM)
    T.ld(ell); T.st(ell); T.loopc(ell // 2); T.ctl(2 * (ell // 2))          # reversal of q in place
    # (2) g on O1 (array G1) and on O2 (in place in the array of g): chirp evaluation of the K coefficient rows, the 2K forward inner transforms
    sG1 = T.new_fp(n1)
    if Pe: T.ctl(vd_eval(K, 2 * K, Pe))
    else: T.ctl(2 * vd_eval(K, K, Px))                                    # no length >= 3K - 1: the nodes of O1 and of O2 in two evaluations
    T.ctl(vd_inner(2 * K, False, PH))
    # (3) R~_0 = X^v P1 mod g on O2: q evaluated at the K nodes of O2 into R2, the forward inner transforms, R2 := u_k^v M(n_k) - R2 * G2 (8 per element)
    zq = Kq * h - ell; T.st(zq); T.ctl(for8(zq))                          # the tail of the last row of q in R1
    T.ctl(vd_eval(Kq, K, Pq) + vd_inner(K, False, PH) + vd_pw(K, 8))
    # (4) R~_0 on O1: inverse inner transforms of O2 reading R2 and writing R1, the extension O2 -> O1 in place on R1, the forward inner transforms
    ext = vd_inner(K, True, PH) + vd_ext(K, Px) + vd_inner(K, False, PH)
    T.ctl(ext)
    # (5) -1/g on O1, in place in G1 (auxiliary array of h elements); a zero prefix product ends the trial
    sAux = T.new_fp(h); T.ctl(vd_batch_inv(K)); T.free(sAux)
    # (6) the squaring loop, one step per bit b of E below the start: (i) R1 := R1^2 G1 (8); (ii) extension O1 -> O2 in place on R1; (iii) R2 := x^b (R2^2 + R1 G2) / M(n_k)
    # (12, 16 when b = 1: omega^i loaded, multiplied by u_k, the product by x); (iv) extension O2 -> O1 from R2 into R1; 20 for the step
    step0 = vd_pw(K, 8) + ext + vd_pw(K, 12) + ext + 20
    step1 = vd_pw(K, 8) + ext + vd_pw(K, 16) + ext + 20
    steps, nset = d['steps'], d['nset']
    T.ctl((steps - nset) * step0 + nset * step1)
    # (7) leaving the Montgomery form: R1 := R1 G1 (7), the extension O1 -> O2, R2 := (R2 + R1 G2) / M(n_k) (11): R2 holds R = S^E mod g on O2
    T.ctl(vd_pw(K, 7) + ext + vd_pw(K, 11))
    T.free(sR1); T.free(sG1)
    # (8) R (in R2) and g (in the array of g) back to coefficient form, in place: inverse inner transforms, interpolation at the K nodes of O2
    interp = vd_inner(K, True, PH) + vd_interp(K, Px)
    T.ctl(2 * interp)
    if sBT is not None: T.free(sBT)
    T.free(sB1); T.free(sTab)
    T.ctl(2 + 500)
    VD.clear(); VD.update(d, ext=ext, step0=step0, step1=step1, interp=interp, Lmax=Lmax, NTAB=NTAB)
    info = dict(steps=steps, nset=nset, PN=Px, PNp=PH, step=step0, mulx=step1 - step0, sg2=sg, sR2=sR2, vd=dict(VD))
    return T, info


# ---------------------------------------------------------------- hgcd.c on shapes (normal Euclid; with WORST_D the worst-case recurrence of proof.md 6.3)
WC_MEM = False       # worst-case live set of stage D: the quotient array of every division at its largest length and the working arrays of the Newton division
WORST_D = False      # worst-case recurrence of stage D: at every node of the half-gcd tree the normal local charge plus the charge of one full division at that node (proof.md 6.3)
TRUNC2 = 1           # the second recursive call of a node runs on the top 2 k3 + 1 coefficients of the reduced pair (Thome 2003, Stehle-Zimmermann 2004; proof 4.4) and its matrix is applied to the whole pair only where the node returns the remainders
TRUNC2_SHRINK = 7    # with TRUNC2: the remainders returned by a node that applies the second matrix are moved into arrays of their own length (one copy each; bit 1: c, bit 2: d, bit 4: from the low end of the pool)
NORMALD = 1          # stage D for the normal remainder sequence only: every division tests that its quotient has degree 1 and every call of hgcd that it returns its parameter (or a zero remainder), 2 operations each; any other case ends the trial (premise H-NORMAL; WORST_D and WC_MEM are then off)

# full division at a node: the charge of divrem_any by the model's own routines (schoolbook division, or the Newton division = one series inverse + two products)
CMUL_INNER = 12      # one inner step of the schoolbook division: mul, sub, LD(2) = 4, ST(1) = 2, loop 3, index 1 -> 1 + 1 + 4 + 2 + 3 + 1
CMUL_OUTER = 15
SMALL_EUCLID = 12 * (2 * 96 + 1) ** 2 + 20 * (2 * 96 + 1) + 400000      # closing loop of poly_gcd_own with n <= 192: Euclid with arbitrary quotients, quadratic bound


def naive_general(lx, ly):
    """poly_divrem_naive on the general path: lx coefficients by ly, quotient of lx - ly + 1 coefficients"""
    dq1 = lx - ly + 1
    return 3 + 7 * lx + powcost(PM2) + INV_CTL + dq1 * ((ly - 1) * CMUL_INNER + CMUL_OUTER)


DIVLOG = None        # when a list, prod_cost appends the transform-domain arrays of every block product it evaluates (the memory walk of the division)


def prod_cost(la, lb, outlen, ws=0, out=None):
    """product of la by lb coefficients whose support has outlen coefficients (outlen = la + lb - 1, or the length of the true product when high zeros are padded).
    Default: all outlen coefficients are placed.  Window (MIDPROD): only the out coefficients from position ws are placed (out = None: all of them).
    ws = 0: the transform has at least outlen points (no wrap-around) and only the first out coefficients are inverse transformed and placed.
    ws > 0 (middle product, Hanrot-Quercia-Zimmermann 2004): the product is formed cyclically with N >= max(ws + out, outlen - ws) points; the coefficients of positions >= N wrap onto
    positions < outlen - N <= ws, below the window, so the window is exact; the operand H is read shifted by N - ws so that the window starts at position 0"""
    if out is None: out = outlen - ws
    if ws == 0 and out == outlen: need = outlen
    else:
        need = outlen if ws == 0 else max(ws + out, outlen - ws)
        assert ws + out <= need and outlen - ws <= need or ws == 0
    Pl, c = plan3_for_len(max(need, 2))
    g = dict(H=[lb], S=[la], prod={(0, 0): (0, 1)})
    CTX['direct'] = DIRECT_DIV                                # a division accumulates the chunks of a product into the output array of the division (listed in wc_div_arrays)
    try: cc, eps = conv_bilin_cost(Pl, 1, [out], [g], (Pl.N - ws) % Pl.N if ws else 0)
    finally: CTX['direct'] = False
    if Pl.a > BIGA and DIVLOG is not None: DIVLOG.append(prod_arrays(PL, PL['ops'], 1))
    return c + cc + plan_invN_ops(Pl) + 3 * out + 20          # product + scaling/placement + control


def series_inverse_cost(lf, k):
    c = 0; t = 1
    while t < k:
        t2 = min(2 * t, k); lft = min(lf, t2); m2 = t2 - t
        if MIDPROD & 2: p1 = prod_cost(lft, t, lft + t - 1, t, m2)                      # middle product: only the coefficients t .. t2 - 1 of g_(t2) phi_t are used
        else: p1 = prod_cost(lft, t, lft + t - 1)
        p2 = prod_cost(m2, m2, 2 * m2 - 1, 0, m2) if MIDPROD & 4 else prod_cost(m2, m2, 2 * m2 - 1)     # only the first m2 coefficients of phi e are used
        c += p1 + p2 + 12 * m2 + 12 * m2 + 40
        t = t2
    return c


def fast_division(la, lb):
    k = la - lb + 1
    return (powcost(PM2) + INV_CTL + 8 * k + 8 * lb + series_inverse_cost(min(lb, k), k)
            + (prod_cost(k, k, 2 * k - 1, 0, k) + prod_cost(k, lb, la, 0, lb - 1) if MIDPROD & 4 else prod_cost(k, k, 2 * k - 1) + prod_cost(k, lb, la)) + 8 * la + 400)


def div_cost(la, lb):
    """divrem_any: schoolbook if the quotient has at most 64 coefficients or the divisor at most 64, else the Newton division"""
    k = la - lb + 1
    if k <= 64 or lb <= 64: return naive_general(la, lb)
    return fast_division(la, lb)


@functools.lru_cache(maxsize=None)
def padded_division_full(la, kmax):
    """(charge, transform-domain arrays of the block product of largest live size) of the re-centering division in its padded form (10-17, ruling 643de050 H-COST-DIV-MAX), for the Newton range 64 <= dq <= dmax = min(kmax, la - 65):
    the program runs it with the quotient precision kN = dmax + 1 and the divisor in a buffer of lbp = la - 64 coefficients (zeros above its top
    coefficient, so the polynomial is unchanged), the reversed divisor in a buffer of min(lbp, kN) and the quotient truncated to dq + 1 coefficients in
    a buffer of kN (zeros above); the sizes are the same for every dq, so the charge is one number: the three buffer loops (load, store, loop step,
    one select per element, allocation and free) and the Newton division at the padded sizes"""
    global DIVLOG
    old = DIVLOG; DIVLOG = []
    try:
        dmax = min(kmax, la - 65)
        kN = dmax + 1; lbp = la - 64
        loops = sum(dupv(n, 0)[0].ops + n + 105 for n in (lbp, min(lbp, kN), kN))
        ops = loops + (powcost(PM2) + INV_CTL + 8 * kN + 8 * lbp + series_inverse_cost(min(lbp, kN), kN)
                       + (prod_cost(kN, kN, 2 * kN - 1, 0, kN) + prod_cost(kN, lbp, la, 0, lbp - 1) if MIDPROD & 4 else prod_cost(kN, kN, 2 * kN - 1) + prod_cost(kN, lbp, la)) + 8 * la + 400)
        arrays = max(DIVLOG, key=lambda x: sum(blk(y) for y in x), default=[])
    finally:
        DIVLOG = old
    return ops, tuple(arrays)


def padded_division(la, kmax):
    return padded_division_full(la, kmax)[0]


@functools.lru_cache(maxsize=None)
def worst_div(la, kmax):
    """the charge of one re-centering division of a polynomial of la coefficients by one of la - dq, for every 1 <= dq <= kmax: in the schoolbook
    range (quotient or divisor of at most 64 coefficients) every dq is evaluated (at most 127 values); in the Newton range the division runs padded
    (padded_division), one charge for every dq; the result is the larger of the two"""
    hi = min(kmax, la - 1); best = 0
    for d in set(range(1, min(hi, 63) + 1)) | set(range(max(1, la - 64), hi + 1)):
        best = max(best, naive_general(la, la - d))
    if hi >= 64 and la - 65 >= 64:
        best = max(best, padded_division(la, kmax))
    return best


def wc_div_arrays(lcc, dq):
    """slots of the arrays live together inside divrem_fast (dq + 1 quotient coefficients, dividend of lcc coefficients), besides the caller's arrays"""
    k = dq + 1
    if k <= 64: return []
    pl, _ = plan3_for_len(max(lcc, 2 * k - 1))                  # the largest product of divrem_fast: q_rev = a_rev * g (2k - 1 coefficients) or q * b (lcc)
    if pl.a > BIGA: ws = list(padded_division_full(lcc, dq)[1])        # the transform-domain arrays of the largest block product of the padded division (its scheme as priced)
    else: ws = [pl.n, pl.n, pl.N]
    return [k, k, k, 2 * k - 1, lcc, lcc - 64, min(lcc - 64, k)] + ws              # the last two: the padded divisor and the reversed divisor (padded_division)

def dupv(ln, b):
    T = Tr(b); s = T.new_fp(ln if ln else 1)
    T.ld(ln); T.st(ln); T.loopc(ln)
    return T, s


def trim(it): return 11 * it           # trimlen: CTL(9 it) + LD(it)


def divrem_naive(lx, ly, term_zero=0):
    """cost of poly_divrem_naive for consecutive lengths (lx = ly + 1); returns (ops, lq, lr, iterations of the final trim)"""
    c = 3
    la, lb = lx, ly
    assert la == lb + 1
    if lb >= 2:
        c += powcost(PM2) + INV_CTL + 3 + 1
        c += 2 * 3 + 2 * 2 + 6
        c += (2 * (lb - 1) + 2 * max(lb - 2, 0))
        c += 4 * (lb - 1) + 2 * (lb - 1) + 3 * (lb - 1) + 2 + 4 + 2 * (lb - 1)
        it = 1 + term_zero * (lb - 1)
        c += trim(it)
        return c, 2, lb - 1 - term_zero * (lb - 1), it
    # general path, lb == 1 (la == 2)
    c += 2 * la + 2 * la + 3 * la + 2
    c += powcost(PM2) + INV_CTL
    c += (la - lb + 1) * (1 + 2 + 2 + 2 + 7) + (la - lb + 1) * 0
    c += trim(1)
    return c, la - lb + 1, 0, 1


def mat_identity(b):
    T = Tr(b); sl = [T.new_fp(1) for _ in range(4)]
    T.st(2)
    return T, [1, 0, 0, 1], sl


def mat_free(T, sl):
    for s in sl:
        if s: T.free(s)


def mul_add_q2(T, le, lf, into=None):
    lt = le + 1 if le else 0
    lo = max(lt, lf)
    if into is not None: s = into                                      # pool_place bit 16: r_e q + r_f written over the array of r_f (as the base case)
    elif POOL_PLACE & 4: s = pp_new(T, lo if lo else 1, pp_end(1))      # pool_place bit 4: R Q of a node at the end of the matrices of its children
    else: s = T.new_fp(lo if lo else 1)  # pool:H
    muls = (le + max(le - 1, 0) + (1 if le > 0 else 0))
    adds = max(le - 1, 0) + (min(lf, le + 1) if le > 0 else 0)
    T.ops += muls + adds
    T.ld(le + lf); T.st(lo); T.loopc(lo); T.ctl(8 + 8 * lo)
    T.ctl(trim(1))
    return lo, s


def mat_mulQ(T, lens, sl):
    if POOL_PLACE & 16:                                                # pool_place bit 16: R Q in place over r12 and r22 when their arrays hold the new entries
        ip = [bool(sl[f]) and max(lens[e] + 1 if lens[e] else 0, lens[f]) <= int(sl[f]) for e, f in ((0, 1), (2, 3))]
        PP_LOG['ip' if ip[0] else 'new'] += 1; PP_LOG['ip' if ip[1] else 'new'] += 1
        l0, s0 = mul_add_q2(T, lens[0], lens[1], sl[1] if ip[0] else None)
        l2, s2 = mul_add_q2(T, lens[2], lens[3], sl[3] if ip[1] else None)
        if not ip[0]: T.free(sl[1])
        if not ip[1]: T.free(sl[3])
        return [l0, lens[0], l2, lens[2]], [s0, sl[0], s2, sl[2]]
    l0, s0 = mul_add_q2(T, lens[0], lens[1])
    l2, s2 = mul_add_q2(T, lens[2], lens[3])
    T.free(sl[1]); T.free(sl[3])
    return [l0, lens[0], l2, lens[2]], [s0, sl[0], s2, sl[2]]


def poly_mul_naive_cost(la, lb):
    return la * lb * 11 + (la * lb - (la + lb - 1)) + (la + lb - 1) * 11 + 2


def mat_mul(A, B, b):
    """A, B = (lens, slots); returns (Tr, lens, slots, consumed); consumed: the product has itself freed the arrays of A and B (block mode: each is freed as soon as it is transformed)"""
    T = Tr(b); T.ctl(80)
    Al, Bl = A[0], B[0]
    Ls = [0] * 4
    for i in range(2):
        for j in range(2):
            l = 0
            for t in range(2):
                la, lb = Al[2 * i + t], Bl[2 * t + j]
                if la and lb and la + lb - 1 > l: l = la + lb - 1
            Ls[2 * i + j] = l
    Lmax = max(1, max(Ls))
    outl = [0] * 4; outs = [0] * 4
    if Lmax <= 48:
        for i in range(2):
            for j in range(2):
                l = Ls[2 * i + j]
                o = T.new_fp(l if l else 1)
                T.st(l); T.loopc(l)
                for t in range(2):
                    la, lb = Al[2 * i + t], Bl[2 * t + j]
                    if not la or not lb: continue
                    tmp = T.new_fp(la + lb - 1)
                    T.ops += poly_mul_naive_cost(la, lb)
                    T.ops += la + lb - 1
                    T.ld(2 * (la + lb - 1)); T.st(la + lb - 1); T.loopc(la + lb - 1)
                    T.free(tmp); T.ctl(6)
                T.ctl(trim(1))
                outl[2 * i + j] = l; outs[2 * i + j] = o
        return T, outl, outs, False
    Pl, c = plan3_for_len(Lmax); T.ctl(c)
    BIG = Pl.a > BIGA
    N = Pl.N
    if not BIG:
        tH0 = T.new_fp(Pl.n); tH1 = T.new_fp(Pl.n); tS = T.new_fp(Pl.n)
        ob = [T.new_fp(N) for _ in range(4)]  # pool:H
    groups = []
    for t in range(2):
        g = dict(H=[], S=[], prod={}); hj = [-1, -1]
        for j in range(2):
            if Bl[2 * t + j]:
                hj[j] = len(g['H']); g['H'].append(Bl[2 * t + j])
        for i in range(2):
            if Al[2 * i + t]:
                s = len(g['S']); g['S'].append(Al[2 * i + t])
                for j in range(2):
                    if hj[j] >= 0: g['prod'][(s, hj[j])] = (2 * i + j, 1)
        if g['H'] and g['S']: groups.append(g)
        T.ctl(20)
    cc, eps = conv_bilin_cost(Pl, 4, Ls, groups); T.ctl(cc)
    if BIG:
        # block mode, streamed (proof 4.5): the arrays of A and B are dead after the product and are freed as soon as they are transformed; the four outputs have their own length
        P = dict(PL)
        ob = [None] * 4
        for M_ in (A, B):
            for x, s_ in zip(M_[0], M_[1]):
                if not x and s_: T.free(s_)                          # an empty entry keeps only its one-slot array
        if P['mode'] == 'a':
            # scheme (a): the spectra of one matrix are held whole and those of the other one row (or column) at a time, the smaller of the two orders; each row (column) forms its two outputs
            nA = [nblk(x) if x else 0 for x in Al]; nBm = [nblk(x) if x else 0 for x in Bl]
            wsA = sum(nBm) + max(nA[0] + nA[1], nA[2] + nA[3])           # B whole, a row of A at a time
            wsB = sum(nA) + max(nBm[0] + nBm[2], nBm[1] + nBm[3])        # A whole, a column of B at a time
            if wsA <= wsB: whole, stream, rows = B, A, ((0, 1), (2, 3))
            else: whole, stream, rows = A, B, ((0, 2), (1, 3))
            held = []
            for x, s_ in zip(whole[0], whole[1]):
                if x:
                    held.append(T.new_fp(nblk(x) * NB)); T.free(s_)
            for r_ in rows:                                           # the entries of a row (column) of the streamed matrix are the entries of the two outputs of that row (column)
                cur = []
                for e in r_:
                    if stream[0][e]:
                        cur.append(T.new_fp(nblk(stream[0][e]) * NB)); T.free(stream[1][e])
                acc = T.new_fp(NB)
                for k in r_: ob[k] = T.new_fp(Ls[k] if Ls[k] else 1)  # pool:H
                T.free(acc)
                for x in cur: T.free(x)
            for x in held: T.free(x)
        elif P['mode'] == 'c':
            # scheme (c): the entries of A and B stay in coefficient form until the last chunk, the four outputs are accumulated and then placed into arrays of their own
            acc, done = chunk_phase(T, P, 4)
            done()
            for M_ in (A, B):
                for x, s_ in zip(M_[0], M_[1]):
                    if x: T.free(s_)
            accd = dict(zip(P['acck'], acc))
            for k in range(4):
                ob[k] = T.new_fp(Ls[k] if Ls[k] else 1)
                if k in accd: T.free(accd[k])
        else:
            # scheme (b): the outer-domain arrays of all operands; the output of an outer point overwrites a dead operand array of that point; the outputs in coefficient form
            # are allocated when the products are placed, after the operand arrays that are dead have been freed
            n2 = P['n2']
            fB = []; fA = []
            for x, s_ in zip(Bl, B[1]):
                if x:
                    fB.append(T.new_fp(form_slots(x, 'b', n2))); T.free(s_)
            for x, s_ in zip(Al, A[1]):
                if x:
                    fA.append(T.new_fp(form_slots(x, 'b', n2))); T.free(s_)
            wk = [T.new_fp(y) for y in prod_work(P, 4)]
            for x in wk + fB: T.free(x)
            for k in range(4): ob[k] = T.new_fp(Ls[k] if Ls[k] else 1)  # pool:H
            for x in fA: T.free(x)
    else:
        T.free(tH0); T.free(tH1); T.free(tS)
    T.ctl(plan_invN_ops(Pl))
    for k in range(4):
        l = Ls[k]
        if BIG:                                               # the placement of the slots already wrote the scaled output
            T.ctl(3)
            if not eps[k]: T.st(l); T.loopc(l)
            outs[k] = ob[k]
            if l: T.ctl(trim(1))
            outl[k] = l
            continue
        o = T.new_fp(l if l else 1); T.ctl(3)  # pool:H
        if eps[k]:
            T.ops += l; T.ld(l); T.st(l); T.loopc(l)
        T.free(ob[k])
        outs[k] = o
        if l: T.ctl(trim(1))
        outl[k] = l
    return T, outl, outs, BIG


def fslots(m):
    """slots of the array F (the state R of stage C and the second operand of stage D): in block mode m + 1, so that the output d of the apply_inv of the top node
    (nres = m + 1 coefficients) can be written over it"""
    return m + 1 if plan3_for_len(2 * m - 1)[0].a > BIGA else m


def apply_inv(Rl, Rs, h, la, lb, consume, b, own_in=(0, 0), sa=0, sb=0):
    """returns (Tr, lc, sc, ld, sd, reuse); reuse = (c was written over the owned a, d over the owned b), block mode only"""
    T = Tr(b)
    nres = la
    Pl, c = plan3_for_len(nres); T.ctl(c)
    N = Pl.N
    BIG = Pl.a > BIGA
    reuse = (False, False)
    if BIG:
        # block mode, streamed (proof 4.5): the outputs c and d are written over the owned inputs a and b when those arrays have nres slots (the placement of slot s writes the
        # blocks s and s + 1, which are already transformed), else into arrays of their own
        reuse = (bool(own_in[0]) and sa >= nres, bool(own_in[1]) and sb >= nres)
    else:
        tH = T.new_fp(Pl.n); tS = T.new_fp(Pl.n)
        sc_ = T.new_fp(N); sd_ = T.new_fp(N)  # pool:H
    sgn = -1 if (h & 1) else 1
    T.ctl(60)
    ec = [3, 1]; ed = [2, 0]; sc = [sgn, -sgn]; sd = [-sgn, sgn]
    lV = [la, lb]
    groups = []
    for v in range(2):
        g = dict(H=[lV[v]], S=[], prod={})
        if not lV[v]: continue
        if Rl[ec[v]]:
            g['prod'][(len(g['S']), 0)] = (0, sc[v]); g['S'].append(Rl[ec[v]])
        if Rl[ed[v]]:
            g['prod'][(len(g['S']), 0)] = (1, sd[v]); g['S'].append(Rl[ed[v]])
        if g['S']: groups.append(g)
        T.ctl(10)
    CTX['seq'] = BIG and SEQ_OUT
    try:
        cc, eps = conv_bilin_cost(Pl, 2, [nres, nres], groups); T.ctl(cc)
    finally:
        CTX['seq'] = False
    if BIG:
        P = dict(PL)
        if P['mode'] != 'c':
            sc_ = sa if reuse[0] else T.new_fp(nres)  # pool:H
            sd_ = sb if reuse[1] else T.new_fp(nres)  # pool:H
        if consume:
            for x, s_ in zip(Rl, Rs):
                if not x and s_: T.free(s_)                          # an empty entry keeps only its one-slot array
        if P['mode'] == 'c':
            # scheme (c): a, b and the entries stay in coefficient form until the last chunk; the outputs c and d are accumulated in two accumulators and placed afterwards,
            # over a and b when those are owned and long enough, else into arrays of their own
            acc, done = chunk_phase(T, P, 2)
            done()
            if consume:
                for x, s_ in zip(Rl, Rs):
                    if x: T.free(s_)
            sc_ = sa if reuse[0] else T.new_fp(nres)  # pool:H
            sd_ = sb if reuse[1] else T.new_fp(nres)  # pool:H
            for x in acc: T.free(x)
        elif P['mode'] == 'a':
            # scheme (a): the spectra of the four entries (each entry is freed as soon as it is transformed when R is consumed); a and b pass through a sliding window of
            # kR + 1 blocks each (an entry of kR blocks meets kR blocks of an operand at a slot, and the block after the slot is transformed before the slot is placed), one accumulator
            kR = max([nblk(x) for x in Rl if x] or [1])
            sp = []
            for x, s_ in zip(Rl, Rs):
                if x:
                    sp.append(T.new_fp(nblk(x) * NB))
                    if consume: T.free(s_)
            win = [T.new_fp(min(nblk(x), kR + 1) * NB) for x in (la, lb) if x]
            acc = T.new_fp(NB)
            for x in [acc] + win + sp: T.free(x)
        else:
            # scheme (b): the outer-domain arrays of the four entries and of a and b (the output of an outer point overwrites a dead operand array of that point), the working arrays
            n2 = P['n2']
            if P['seq']:
                # the outputs one after the other: the forms of a and b are made once and kept; c = r22 a - r12 b needs the forms of r22 and r12, which are freed after c is placed,
                # then d = r11 b - r21 a those of r11 and r21 (the inner transforms of a and b at each outer point are made again for d, charged); the output of an outer point overwrites a dead entry form
                fab = [T.new_fp(form_slots(x, 'b', n2)) for x in (la, lb) if x]
                for ph in ((3, 1), (2, 0)):
                    fo = []
                    for e in ph:
                        if Rl[e]:
                            fo.append(T.new_fp(form_slots(Rl[e], 'b', n2)))
                            if consume: T.free(Rs[e])
                    wk = [T.new_fp(y) for y in prod_work(P, 1)]
                    for x in wk + fo: T.free(x)
                for x in fab: T.free(x)
            else:
                # the outer-domain arrays of the four entries and of a and b (the output of an outer point overwrites a dead operand array of that point), the working arrays
                fo = []
                for x, s_ in zip(Rl, Rs):
                    if x:
                        fo.append(T.new_fp(form_slots(x, 'b', n2)))
                        if consume: T.free(s_)
                for x in (la, lb):
                    if x: fo.append(T.new_fp(form_slots(x, 'b', n2)))
                wk = [T.new_fp(y) for y in prod_work(P, 2)]
                for x in wk + fo: T.free(x)
    else:
        T.free(tH); T.free(tS)
        if consume:
            mat_free(T, Rs)
    T.ctl(plan_invN_ops(Pl))
    for k in range(2):
        T.ctl(3)
        if not eps[k]:
            T.st(nres); T.loopc(nres); continue
        if BIG: continue                                      # the scale 1/NB and the sign are applied by the placement of the slots
        if eps[k] < 0: T.ops += 1
        T.ops += nres; T.ld(nres); T.st(nres); T.loopc(nres)
    lc = la - h; ld = lc - 1
    T.ctl(trim(1 + (nres - lc)) + trim(1 + (nres - ld)))
    return T, lc, sc_, ld, sd_, reuse


HGCD_CACHE = {}


def _relink(x, base, ext):
    """the arrays in the result of a recorded call, named in the ids of the caller (ids < 0 are the arrays given to the call)"""
    if isinstance(x, Slot): return Slot(int(x), ext[-x.id - 1] if x.id < 0 else base + x.id)
    if isinstance(x, list): return [_relink(y, base, ext) for y in x]
    if isinstance(x, tuple): return tuple(_relink(y, base, ext) for y in x)
    return x


def hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b):
    """hgcd memoised by shape: the body _hgcd runs once for each shape and records its events with ids relative to the call; every use links them to the arrays of the caller.
    returns (Tr, out) ; out = (lc, sc, ld, sd, Rl, Rs, h)"""
    key = (la, int(sa), lb, int(sb), k, want_mat, own, wc, wd, b) + ((LD_PAR,) if POOL_PLACE & 4 else ())      # pool_place bit 4: the ends depend on the depth parity
    ent = HGCD_CACHE.get(key)
    if ent is None:
        ctx = Ctx(); CTX_STACK.append(ctx)
        try:
            T, out = _hgcd(la, Slot(int(sa), -1) if sa else 0, lb, Slot(int(sb), -2) if sb else 0, k, want_mat, own, wc, wd, b)
        finally:
            CTX_STACK.pop()
        ent = (T, out, Rec(T.ev, ctx.n)); HGCD_CACHE[key] = ent
    T, out, rec = ent
    ctx = CTX_STACK[-1]; base = ctx.n; ctx.n += rec.nloc
    ext = (sa.id if sa else None, sb.id if sb else None)
    Tc = Tr(T.base); Tc.ops, Tc.cur, Tc.peak, Tc.cnt, Tc.pcnt = T.ops, T.cur, T.peak, T.cnt, T.pcnt
    Tc.ev = [('C', rec, base, ext)]
    return Tc, _relink(out, base, ext)


hgcd.cache_clear = HGCD_CACHE.clear


def _hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b):
    if LEAND: return _hgcd_ld(la, sa, lb, sb, k, want_mat, own, wc, wd, b)      # pos_leand
    T = Tr(b); T.ctl(40)
    n = la - 1
    Rl = Rs = None
    if lb == 0 or n - (lb - 1) > k:
        if want_mat:
            t, Rl, Rs = mat_identity(T.here()); T.add(t)
        T.ctl(4)
        lc = sc = ld = sd = None
        if wc:
            if own & 1: sc = sa
            else:
                t, sc = dupv(la, T.here()); T.add(t)
            lc = la
        elif own & 1: T.free(sa)
        if wd:
            if own & 2: sd = sb
            else:
                t, sd = dupv(lb, T.here()); T.add(t)
            ld = lb
        elif own & 2: T.free(sb)
        return T, (lc, sc, ld, sd, Rl, Rs, 0)
    if k <= 96:
        return hgcd_base(la, sa, lb, sb, k, want_mat, own, wc, wd, T)
    k1 = (k + 1) >> 1
    if k1 + k1 > n: k1 = n >> 1
    s = n - 2 * k1
    las = la - s; lbs = lb - s if lb > s else 0
    t1, o1 = hgcd(las, 0, lbs, 0, k1, 1, 0, False, False, T.here())
    T.add(t1)
    if NORMALD: T.ctl(2)                                      # the return test: h1 == k1 (or a zero remainder), else the trial ends
    R1l, R1s, h1 = o1[4], o1[5], o1[6]
    assert h1 >= 1, 'non-generic shape'
    t2, lcc, scc, ldd, sdd, reuse = apply_inv(R1l, R1s, h1, la, lb, not want_mat, T.here(), (own & 1, (own >> 1) & 1), sa, sb)
    T.add(t2); T.ctl(4)
    if (own & 1) and not reuse[0]: T.free(sa)
    if (own & 2) and not reuse[1]: T.free(sb)
    sumdeg = n - (lcc - 1); k2 = k - sumdeg
    if ldd == 0 or (lcc - ldd) > k2:
        if want_mat: Rl, Rs = R1l, R1s
        lc = sc = ld = sd = None
        if wc: lc, sc = lcc, scc
        else: T.free(scc)
        if wd: ld, sd = ldd, sdd
        else: T.free(sdd)
        return T, (lc, sc, ld, sd, Rl, Rs, h1)
    dq = lcc - ldd
    if NORMALD: T.ctl(2)                                      # the quotient test: dq == 1, else the trial ends
    dqm = max(dq, k2) if WC_MEM else dq
    sq = T.new_fp(dqm + 1); srm = T.new_fp(lcc)  # pool:H
    if WC_MEM: T.bump_blocks(wc_div_arrays(lcc, dqm))
    T.ctl(3)                                                  # divrem_any
    dc, lq, lrem, _ = divrem_naive(lcc, ldd)
    T.ctl(dc)
    if WORST_D: T.ops += worst_div(lcc, k2)                   # recurrence of 6.3: plus one full division of this node at its worst quotient degree
    T.free(scc)
    k3 = k2 - dq
    s3 = ldd - 1 - 2 * k3
    if TRUNC2: T.ctl(3 + 7)                                   # s3 (a shift, two subtractions) and the test s3 > 0, lrem != 0, ldd - lrem <= k3 (comparisons, a subtraction, branches)
    if TRUNC2 and s3 > 0 and lrem and ldd - lrem <= k3:
        # the truncated second call (proof 4.4): its operands are the top 2 k3 + 1 coefficients of d and the top lrem - s3 of the remainder, read in place (shifted by s3, like the
        # first call); it returns its matrix only, and the matrix is applied to the whole pair (d, remainder) where this node returns the remainders
        T.ctl(4 + 2)                                          # the two shifted addresses (a shift and an addition each) and the two lengths
        t3, o3 = hgcd(ldd - s3, 0, lrem - s3, 0, k3, 1, 0, False, False, T.here())
        T.add(t3)
        if NORMALD: T.ctl(2)                                  # the return test: h3 == k3 (or a zero remainder), else the trial ends
        R3l, R3s, h3 = o3[4], o3[5], o3[6]
        T.ctl(4)                                              # the tests of wc and wd
        if wc or wd:
            t4, lc3, sc3, ld3, sd3, reuse3 = apply_inv(R3l, R3s, h3, ldd, lrem, not want_mat, T.here(), (1, 1), sdd, srm)
            T.add(t4); T.ctl(4 + 4)                           # the two reuse tests and the tests of wc and wd
            if not reuse3[0]: T.free(sdd)
            if not reuse3[1]: T.free(srm)
            if not wc:
                T.free(sc3); lc3 = sc3 = None
            if not wd:
                T.free(sd3); ld3 = sd3 = None
            if TRUNC2_SHRINK:
                # the remainders are written over d and the remainder of the node (arrays of up to the caller's length); each is moved into an array of its own length
                # (one copy: a load, a store and the loop step per coefficient), and the long array is freed.  bit 1: c, bit 2: d, bit 4: the copies from the low end of the pool
                T.ctl(2 * (3 + 1))                            # per remainder: the length test (a load of the block size, a comparison, a branch) and the pointer assignment
                if (TRUNC2_SHRINK & 1) and sc3 is not None and int(sc3) > lc3:
                    if TRUNC2_SHRINK & 4: s_ = T.new_fp(lc3)
                    else: s_ = T.new_fp(lc3)  # pool:H
                    T.ld(lc3); T.st(lc3); T.loopc(lc3); T.free(sc3); sc3 = s_
                if (TRUNC2_SHRINK & 2) and sd3 is not None and int(sd3) > ld3:
                    if TRUNC2_SHRINK & 4: s_ = T.new_fp(ld3)
                    else: s_ = T.new_fp(ld3)  # pool:H
                    T.ld(ld3); T.st(ld3); T.loopc(ld3); T.free(sd3); sd3 = s_
        else:
            T.free(sdd); T.free(srm)
            lc3 = sc3 = ld3 = sd3 = None
            T.ctl(2)                                          # the test of want_mat
            if not want_mat: mat_free(T, R3s)
        o3 = (lc3, sc3, ld3, sd3, R3l, R3s, h3)
    else:
        t3, o3 = hgcd(ldd, sdd, lrem, srm, k3, want_mat, 3, wc, wd, T.here())
        T.add(t3)
        if NORMALD: T.ctl(2)                                  # the return test: h3 == k3 (or a zero remainder), else the trial ends
    h = h1 + dq + o3[6]
    if want_mat:
        R1l2, R1s2 = mat_mulQ(T, R1l, R1s)
        tm, Ml, Ms, cons = mat_mul((R1l2, R1s2), (o3[4], o3[5]), T.here()); T.add(tm)
        if not cons:
            mat_free(T, o3[5]); mat_free(T, R1s2)
        Rl, Rs = Ml, Ms
    T.free(sq)
    return T, (o3[0], o3[1], o3[2], o3[3], Rl, Rs, h)


def hgcd_base(la, sa, lb, sb, k, want_mat, own, wc, wd, T):
    if own & 1: sx = sa
    else:
        t, sx = dupv(la, T.here()); T.add(t)
    if own & 2: sy = sb
    else:
        t, sy = dupv(lb, T.here()); T.add(t)
    lx, ly, ssum = la, lb, 0
    Rl = Rs = None
    if want_mat:
        t, Rl, Rs = mat_identity(T.here()); T.add(t)
    while ly > 0:
        dq = lx - ly
        T.ctl(6)
        if dq > k - ssum: break
        if NORMALD: T.ctl(2)                                  # the quotient test: dq == 1, else the trial ends
        sq = T.new_fp(dq + 1); sr = T.new_fp(lx)
        dc, lq, lr, _ = divrem_naive(lx, ly)
        T.ctl(dc)
        if WORST_D: T.ops += max(0, naive_general(lx, ly) - dc)   # recurrence of 6.3: a step of the base case charged on the general path (a step of quotient degree d is at most d steps of degree 1)
        if want_mat:
            Rl, Rs = mat_mulQ(T, Rl, Rs)
        ssum += dq
        T.free(sx); sx = sy; lx = ly; sy = sr; ly = lr
        T.free(sq)
    lc = sc = ld = sd = None
    if wc: lc, sc = lx, sx
    else: T.free(sx)
    if wd: ld, sd = ly, sy
    else: T.free(sy)
    return T, (lc, sc, ld, sd, Rl, Rs, ssum)


def gcd_cost(m, dG, b, sx, sy):
    CTX['stage'] = 'D'
    try: return gcd_cost_ld(m, dG, b, sx, sy) if LEAND else gcd_cost_(m, dG, b, sx, sy)      # pos_leand
    finally: CTX['stage'] = None


def gcd_cost_(m, dG, b, sx, sy):
    """poly_gcd_own(g (m+1 coefficients), R-1 (m coefficients)), normal Euclid, gcd degree dG.  sx, sy: the arrays of g (m+1 slots) and of F (fslots(m) slots) of the caller.
    Returns (Tr, (lg, sg))."""
    T = Tr(b)
    lx, ly = m + 1, m
    T.ctl(3); T.ctl(3)
    while ly > 0:
        T.ctl(2)
        n = lx - 1
        T.ctl(4)
        if n <= 2 * 96:
            if NORMALD: T.ctl(2)                              # the quotient test: lx - ly == 1, else the trial ends
            sq = T.new_fp(lx - ly + 1); sr = T.new_fp(lx)
            last = (ly == dG + 1)
            dc, lq, lr, _ = divrem_naive(lx, ly, term_zero=1 if (last and dG >= 1) else 0)
            if last and dG == 0:
                lr = 0
            T.ctl(dc)
            T.free(sx); sx = sy; lx = ly; sy = sr; ly = lr
            T.free(sq); T.ctl(5)
            continue
        k = (n + 1) // 2
        t, o = hgcd(lx, sx, ly, sy, k, False, 3, True, True, T.here())
        T.add(t)
        if NORMALD: T.ctl(2 + 2)                              # the return test (h == k or a zero remainder) and the quotient test (lc - ld == 1), else the trial ends
        lc, sc, ld, sd = o[0], o[1], o[2], o[3]
        T.ctl(2)
        dqm = (lc if WC_MEM else lc - ld)
        sq = T.new_fp(dqm + 1); sr = T.new_fp(lc)  # pool:H
        if WC_MEM: T.bump_blocks(wc_div_arrays(lc, dqm))
        T.ctl(3)
        dc, lq, lr, _ = divrem_naive(lc, ld)
        T.ctl(dc)
        if WORST_D: T.ops += worst_div(lc, lc - 1)            # recurrence of 6.3: the division of the outer loop at its worst quotient degree
        T.free(sc); T.free(sq)
        sx = sd; lx = ld; sy = sr; ly = lr; T.ctl(5)
    T.free(sy)
    T.ctl(2)
    if WORST_D: T.ops += SMALL_EUCLID                         # recurrence of 6.3: the closing loop (n <= 192) with arbitrary quotients
    T.ops += powcost(PM2); T.ctl(INV_CTL); T.ld(1)
    T.ops += lx - 1
    T.ld(lx); T.st(lx); T.loopc(lx)
    return T, (lx, sx)


# ---------------------------------------------------------------- LEAND: stage D charged the way of bradcush 1aa56884 (its proof 4.4, lemma 4.8, 4.5; e6dcb600 4.4), in this model's primitives
# Read as text only (no code of the entry was run, compiled or imported); the shapes follow Grok job 163 stage_d.py / products.py (our research tool, which reproduces the entry's row D to the unit).
# What LEAND changes in stage D: (1) the base case (k <= 96) runs in place: the matrix entries are four arrays of k + 2 elements allocated once, no array is allocated inside the loop;
# (2) apply_inv forms c, d cyclically on their true lengths la - h, la - h - 1 (their high coefficients cancel), by whichever of the single transform and the block products is cheaper;
# (3) a node that wants its matrix only forms the top window of c and d (degrees >= s3 - 1, lemma 4.8(a)); (4) the top node works on the two pieces [0, cut), [cut, n1) of g and R
# (lemma 4.8(b)): its first call frees the high pieces after its own apply_inv and c, d are formed one after the other from the low pieces; (5) mat_mul by the cheaper of the single
# transform and the block products; (6) the block products: scheme (a) at the block length 2^31 (one-row block transform of 2^32 points) or scheme (c) (chunked outer product) at the
# block length 2^b of smallest charge, b = 6 .. 31, chunk bound LD_CF elements.  The charges of every primitive are this model's (proof 4.2): passes, Good-Thomas stages, pointwise
# loops, allocations, the outer transform ontt_at (kernels ob2, ob3), the chunk assembly (ocp, oax, ozf), the placement; LD_CONV switches each primitive to the 1aa56884 convention
# (gate only).
LEAND = 1            # 1: stage D as above (requires NORMALD = 1 or AMORT = 1)
AMORT = 0            # with LEAND: premise-free stage D = the normal-sequence trace (tests charged, no abort) + one fast division of length m + the zero-scan allowance; top-node pieces off
LD_WIN = 1           # windows of lemma 4.8(a)
LD_PIECES = 0     # top-node pieces of lemma 4.8(b); None: on with NORMALD, off with AMORT (the pieces need h1 = k1 and h3 = k3, a normal sequence)
LD_CF = None         # chunk bound (elements) of the scheme (c) products of stage D; None: m // CHUNK_D
LD_CONV = dict(astat=0, outer=0, fold=0, acc=0, frow=0, pctl=0, scratch=0, compact=0, base3=0)   # 1: the convention of 1aa56884 for that primitive (gate), 0: this model's
LD_ABORT = 2         # one quotient or return test (a comparison and a branch)
LD_CFV = None        # the chunk bound in use (set by run_stages: LD_CF, or m // CHUNK_D)
LD_KSCR = 1 << 44    # 1aa56884 scratch region (gate convention only)
LD_COMPACT_ELEMS = 22924228636997165691      # 1aa56884 G.7 compaction count at r = 21 (CLAIMED; gate convention only)
LD_ROOTS = 6 * (330 + INV_CTL)                # 1aa56884 scheme (c) roots and constants per product (gate convention only)
LD_KCH = {'ob3': (16, 23), 'ob2f': (14, 14), 'ob2i': (14, 14), 'ob4f': (18, 31), 'ob4i': (18, 31), 'ob8f': (26, 71), 'ob8i': (26, 71)}   # 1aa56884 register-blocked outer kernels (gate only)
ASTAT = 0            # allocator statistics per allocation and free (1aa56884: 64; this model: 0); set only inside stage D by run_stages
HB31 = 1 << 31; NB32 = 1 << 32
A_HB = 1 << 19; A_NB = 1 << 20      # block length of scheme (a) of stage D (2^19 here: the in-place streamed block apply of the memory cap, proof.md 4.4, 7)
LD_LOG = collections.Counter()
VLOG = collections.Counter()        # the charge of the scale and loops below on the distinct block products evaluated (a record, not a charge)
LD_SITE = dict(inv=1, div=0, mat=1, tmp=1, top=1, outer=1, topdiv=1)   # the end of the pool of each LEAND allocation statement (1: high, `# pool:H`; 0: low), a constant of the statement
VFIX_PP = 15         # per scheme (c) product: the root w and the scale sign/(NB n2) of its outputs, from an offline table of 2^-i and 1/3 (VERIFY_undercharge U1)
VFIX_PC = 7          # per untwist call of scheme (c): the scaled weight w^(-e) sign/(NB n2) (load the table entry, load the scale, multiply, store) (U1)
VFIX_LOOP = 1        # 1: the chunk loop (3 per chunk + 2, set-up 6 per chunk) and the outer-point loop (3 per point and 2 per chunk) of scheme (c), and the fetch of w^o per output per point (4) (U2)
VFREEZE = 0          # 1 (comparison only): every choice (block length, scheme, single vs block) made on the charge without the three lines above
VCHOICE = 1          # 1: the single-vs-block choice of mat_mul and apply_inv also counts the allocations and frees the block path adds (len(temps) - 7 in mat_mul, len(temps) - 2 in apply_inv)
GCDONLY = 1          # gcdonly (10-19, default off): cofactor-free in-place stage D: (1) every consuming apply (a node that does not return its matrix, and the top node) writes c over the owned array of a and d over that of b
                     # (both outputs formed slot by slot after the block of the operand is transformed; the entries freed as they are transformed); (2) scheme (a) holds a window of kR + 1 block spectra per
                     # vector operand (proof 4.5) and one accumulator; (3) the remainder of every division is written over the dividend; (4) g and R in three pieces [0, cut2'), [cut2', cut), [cut, n1)
ALLOC_FIX = 1        # (10-19, default off): R in coefficient form (sR2 of powx_vd) allocated before the tables of stage C, so that it is the bottom of the low end (no charge changes: the live counts of the moved allocations balance)
POOL_PLACE = 20       # (10-19, default off): placement of the matrix product of a node (mat_mul_ld, single transform): bit 1 the four outputs allocated first, low end; bit 2 first, high end (charges from the walk);
                     # bit 4 depth-parity ends in stage D (pp_end: a node's own arrays at its end, R Q, transforms and work arrays at the end of its children's matrices); bit 8 flips the parity of depth 0; bit 16 R Q in place over r12, r22 (mat_mulQ) when they are long enough, the entries made by mat_mul_ld with two spare slots (r11 q + r12 is two longer than r12)


def ld_new(T, slots, site):
    if POOL_PLACE & 4 and site in PP_SITE: return pp_new(T, slots, pp_end(PP_SITE[site]))
    if LD_SITE[site]: return T.new_fp(slots)  # pool:H
    return T.new_fp(slots)


PP_LOG = collections.Counter()   # pool_place bit 16: R Q entries written in place / into new arrays (for the report only)
PP_SITE = dict(mat=0, inv=0, div=0, tmp=0)   # pool_place bit 4: 0 = the end of the node (its outputs: the matrix, c and d, q, the work arrays of its products), 1 = the other end (the end of the matrices of its children)
LD_PAR = 0           # pool_place bit 4: depth parity of the running node of stage D (flipped around each child call)


def pp_end(o):
    """pool_place bit 4: the end of the pool (1 high) for an allocation of the running node: its own end (o = 0) or the end of its children's matrices (o = 1); the node at depth j has end (j + bit 8) mod 2"""
    return (LD_PAR ^ ((POOL_PLACE >> 3) & 1) ^ o) & 1


def pp_new(T, slots, end):
    if end: return T.new_fp(slots)  # pool:H
    return T.new_fp(slots)


def pp_call(f, *a):
    """pool_place bit 4: a child call of a node runs at the other depth parity"""
    global LD_PAR
    if not POOL_PLACE & 4: return f(*a)
    LD_PAR ^= 1
    try: return f(*a)
    finally: LD_PAR ^= 1


def ld_pieces_on():
    return bool(LEAND) and (LD_PIECES if LD_PIECES is not None else not AMORT)


def ld_pieces(m):
    """the two pieces of g and R for the top node (1aa56884 4.6 step 8): [0, cut) and [cut, n1), cut = Kc 2^32 >= m + 1 - k1, k1 the first parameter of the top node"""
    h = VD_H; K = -(-(m + 1) // h)
    k1 = (((m + 1) // 2) + 1) >> 1
    Kc = -(-(m + 1 - k1) // h)
    if GCDONLY:                                                 # the third boundary cut2' = ceil(cut2 / h) h, cut2 = ldd - k3 of the top node (the low piece the second apply reads)
        k = (m + 1) // 2; k1_ = (k + 1) >> 1
        if k1_ + k1_ > m: k1_ = m >> 1
        lcc = m + 1 - k1_; ldd = lcc - 1; k3 = k - k1_ - 1; cut2 = ldd - k3
        K2 = -(-cut2 // h); assert 0 < K2 < Kc, (K2, Kc)
        return K2 * h, (Kc - K2) * h, (K - Kc) * h
    return Kc * h, (K - Kc) * h


def ld_rowfill(Pl, ln):
    """copy of ln coefficients into a transform row of Pl.n points and the zero fill of the rest: a load and a store per coefficient, a store per zero, eight-element loops"""
    return 4 + for8(ln) + 4 * ln + for8(Pl.n - ln) + 2 * (Pl.n - ln) + 2


@functools.lru_cache(maxsize=None)
def ld_bplan(hb): return make_plan(1, (2 * hb).bit_length() - 1)[0]


@functools.lru_cache(maxsize=None)
def ld_bfwd(bl, hb):
    """block transform of NB = 2 hb points (one row of passes) of a block of bl coefficients"""
    P = ld_bplan(hb); return ld_rowfill(P, bl) + fwd_passes(P, P.np)


@functools.lru_cache(maxsize=None)
def ld_binv(hb):
    P = ld_bplan(hb); return inv_passes(P, P.np - 1)


def ld_invN(size):
    """plan_invN of a transform of `size` points (the scale 1/N): a scan of the cache"""
    return 7 * CACHE


@functools.lru_cache(maxsize=None)
def ld_ontt(n, cnt, inv):
    """one outer transform of n = 2^a or 3 * 2^a points at cnt positions with its twiddle table: this model's kernels ob3, ob2 (ontt_at), or (gate) the ob8/ob4/ob2 kernels of 1aa56884"""
    if not LD_CONV['outer']: return ontt_at(n, cnt)
    r3 = n % 3 == 0; M = n // 3 if r3 else n; a = M.bit_length() - 1
    assert (1 << a) == M, n
    ks = ([a % 3] if a % 3 else []) + [3] * (a // 3)
    c = 6 * n + 2; nrows = 3 if r3 else 1
    if r3:
        k0, k1 = LD_KCH['ob3']; c += 10 + 3 * M + 2 + M * (3 * 4 + k0 + k1 * cnt)
    c += 3 * nrows + 2
    per_row = 3 * len(ks) + 2; Ns = M
    for k in ks:
        h = Ns >> k; nb = M // Ns; k0, k1 = LD_KCH['ob%d%s' % (1 << k, 'i' if inv else 'f')]
        per_row += (3 * nb + 2) + nb * (3 * h + 2) + nb * h * ((1 << k) * 4 + ((1 << k) - 1) * 3 + k0 + k1 * cnt)
        Ns >>= k
    return c + nrows * per_row


def ld_nblk(l, hb): return -(-l // hb)


def ld_segs(ws, ln, hb):
    """the pieces of the window [ws, ws + ln) cut at the multiples of hb: (length, count)"""
    e = ws + ln
    if ln <= 0: return []
    q = min(e, (ws // hb + 1) * hb)
    if q == e: return [(ln, 1)]
    out = [(q - ws, 1)]; full = (e - q) // hb; rest = e - q - full * hb
    if full: out.append((hb, full))
    if rest: out.append((rest, 1))
    return out


def ld_fold(l, n3, tw, hb):
    """twist and fold of an operand of l coefficients into the n3 rows of hb elements of one chunk (tw: not the first chunk)"""
    kx = ld_nblk(l, hb); last = l - (kx - 1) * hb
    if not LD_CONV['fold']:          # this model's chunk assembly: ocp for a block that starts a row, oax for a block added to a row, ozf for a row (or the tail of a row) no block reaches
        nocp = min(kx, n3); noax = kx - nocp
        c = nocp * (OCALL_C + OCP[0] + OCP[1] * hb) + noax * (OCALL_C + OAX[0] + OAX[1] * hb)
        if nocp == kx:
            c -= OCP[1] * (hb - last)
            if last < hb: c += OCALL_C + OZF[0] + OZF[1] * (hb - last)
        else: c -= OAX[1] * (hb - last)
        if kx < n3: c += (n3 - kx) * (OCALL_C + OZF[0] + OZF[1] * hb)
        return c
    wr = 4 + tw; ac = 7 + tw; first = min(kx, n3); acc = kx - first; zero_rows = max(0, n3 - kx); c = 0
    if kx <= n3:
        c += (first - 1) * (10 + for8(hb) + wr * hb) + 10 + for8(last) + wr * last + for8(hb - last) + 2 * (hb - last)
    else:
        c += first * (10 + for8(hb) + wr * hb) + (acc - 1) * (10 + for8(hb) + ac * hb) + 10 + for8(last) + ac * last
    c += zero_rows * (10 + for8(hb) + 2 * hb)
    return c + 3 * (kx + zero_rows) + 2


def ld_acc(ws, ln, first, sub, hb):
    """untwist of one chunk of an output into its window [ws, ws + ln) (the first chunk stores, the others add)"""
    if not LD_CONV['acc']:           # this model's kernels: ocp (first chunk) or oax (the others) per piece of the window, OCALL_I per call
        assert not sub
        ch = OCP if first else OAX
        return sum(cnt * (OCALL_I + ch[0] + ch[1] * x) for x, cnt in ld_segs(ws, ln, hb))
    per = 5 if (first and not sub) else 8
    return sum(cnt * (10 + for8(x) + per * x + 3) for x, cnt in ld_segs(ws, ln, hb)) + 2


def ld_frow(hb):
    """the inverse block transform of an outer point folded modulo X^hb - w^o into the row of the output chunk array"""
    if not LD_CONV['frow']: return big_place(hb, hb, False)
    return 8 * hb + for8(hb) + 4


def ld_nc(n2, cf, hb):
    nc = 1
    while cf is not None and (n2 // nc) * hb > cf and (n2 // nc) % 2 == 0: nc *= 2
    return nc


def ld_scheme_c(hb, need, ops, prods, live, outlen, ws, sub, cf):
    q = -(-need // hb)
    if q > 3 << BIGA: return None
    n2 = pad23(q); nc = ld_nc(n2, cf, hb); n3 = n2 // nc; nb2 = 2 * hb
    pw0, pw1 = pw_loop(nb2, 0), pw_loop(nb2, 1)
    mops = [l for l in ops if ld_nblk(l, hb) > 1]; singles = [l for l in ops if ld_nblk(l, hb) == 1]
    pc = LD_CONV['pctl']
    co = (2 + LD_ROOTS + 3 * nc + 2 if pc else 2 + 3 * (n2 + 1)) + sum(ld_bfwd(l, hb) for l in singles)
    for j_first, mult in ((True, 1), (False, nc - 1)):
        if not mult: continue
        cj = (6 if pc else 0) + sum(ld_fold(l, n3, 0 if j_first else 1, hb) for l in mops) + len(mops) * ld_ontt(n3, hb, False)
        cj += n3 * ((8 if pc else 0) + len(mops) * ld_bfwd(hb, hb))
        for k in live:
            cj += n3 * (pw0 + (len(prods[k]) - 1) * pw1 + ld_binv(hb) + ld_frow(hb))
            cj += ld_ontt(n3, hb, True) + ld_acc(ws, outlen[k], j_first, sub, hb)
        co += mult * cj
    temps = [n3 * hb] * max(len(mops), len(live)) + [nb2] * (len(ops) + len(live)) + ([n3] if pc else [n2 + 1, n3])
    if LD_DISC and LD_INVCTX is not None and (LD_DISC_ALL or not LD_INVCTX[0]):
        hs = LD_INVCTX[1]; Hm = any(ld_nblk(l, hb) > 1 for i, l in enumerate(ops) if i in hs); Sm = any(ld_nblk(l, hb) > 1 for i, l in enumerate(ops) if i not in hs)
        Hs = any(ld_nblk(l, hb) == 1 for i, l in enumerate(ops) if i in hs); Ss = any(ld_nblk(l, hb) == 1 for i, l in enumerate(ops) if i not in hs)
        if LD_DISC == 1: nsp = len(singles) + (1 if Hm else 0) + (1 if Sm else 0) + len(live)
        else: nsp = (1 if (Hm or Hs) else 0) + (1 if (Sm or Ss) else 0) + len(live)
        if nsp < len(ops) + len(live):
            temps = [n3 * hb] * max(len(mops), len(live)) + [nb2] * nsp + ([n3] if pc else [n2 + 1, n3])
            if LD_DISC == 2: co += (n2 - 1) * sum(ld_bfwd(l, hb) for l in singles)
    ex = VFIX_PP + VFIX_PC * nc * sum(sum(cnt for x, cnt in ld_segs(ws, outlen[k], hb)) for k in live)
    if VFIX_LOOP: ex += 2 + nc * (3 + 2 + 6) + n2 * (3 + 4 * len(live))
    return co + ex, temps, n2, nc, ex


def ld_window_slots(ws, outlen):
    we = ws + outlen
    s0 = max(0, (ws + 1) // A_HB - 3)
    while (s0 + 2) * A_HB - 1 <= ws: s0 += 1
    s1 = -(-we // A_HB) + 2
    while s1 * A_HB >= we: s1 -= 1
    return s0, s1, we


def ld_slot_cost(s, s0, ws, we, sub):
    lo, hi = s * A_HB, (s + 2) * A_HB - 1
    cnt = min(hi, we) - max(lo, ws); ov = 0
    if s > s0: ov = max(0, min((s + 1) * A_HB - 1, we) - max(s * A_HB, ws))
    return ld_binv(A_HB) + big_place(cnt, ov, sub)


LD_TMAX = None       # gcdonly: bound (elements) on the working arrays of one block product of stage D: the cheapest scheme (a at 2^31, c at 2^b) within the bound, else the one of smallest working set; a constant of the algorithm
LD_SEQ = 0           # gcdonly: a non-consuming two-output apply forms its outputs one after the other (the operand forms of the second output are made again, charged), so that the working arrays of one output only are live
LD_DISC = 1          # gcdonly2 item (1): scheme (c) of apply_inv, per outer point the groups one at a time (one spectrum of the vector, one of the entry being multiplied, the accumulators);
                     # 1: the single-block entries keep their spectra (no charge change); 2: no spectrum kept, the single-block operands transformed at every outer point (charged)
LD_DISC_ALL = 0      # 0: only the non-consuming applies; 1: every apply_inv
LD_TMAX_NC = None    # gcdonly2: LD_TMAX applied only inside the non-consuming applies
LD_INVCTX = None     # set by apply_inv_ld: (consume, hset) while its block product is chosen
LD_LAST_NC = 1       # gcdonly: the chunk count of the scheme chosen by the last ld_choose (1 for scheme (a))


def _tmax():
    if LD_TMAX_NC is not None and LD_INVCTX is not None and not LD_INVCTX[0]: return LD_TMAX_NC
    return LD_TMAX


def ld_choose(need, ops, prods, live, outlen, ws, sub, cf, win=None, force_a=False):
    """the cheapest of scheme (a) at the block length 2^31 and scheme (c) at the block length 2^b of smallest charge (b = 6 .. 31). Returns (ops, temps, mode, hb)"""
    global LD_LAST_NC
    ca = 2 + sum((ld_nblk(l, A_HB) - 1) * ld_bfwd(A_HB, A_HB) + ld_bfwd(l - (ld_nblk(l, A_HB) - 1) * A_HB, A_HB) for l in ops)
    pw0, pw1 = pw_loop(A_NB, 0), pw_loop(A_NB, 1)
    for k in live:
        s0, s1, we = ld_window_slots(ws, outlen[k])
        stot = max(ld_nblk(ls, A_HB) + ld_nblk(lh, A_HB) - 1 for ls, lh in prods[k])
        A, B = s0, min(s1, stot - 1)
        if B < A: continue
        npr = sum(pairs_range(ld_nblk(ls, A_HB), ld_nblk(lh, A_HB), A, B) for ls, lh in prods[k])
        cnt_s = B - A + 1
        ca += cnt_s * (pw0 - pw1) + pw1 * npr
        edges = sorted(set(range(A, min(A + 3, B + 1))) | set(range(max(B - 2, A), B + 1)))
        for s in edges: ca += ld_slot_cost(s, s0, ws, we, sub)
        mid = cnt_s - len(edges)
        if mid > 0: ca += mid * ld_slot_cost(edges[2] + 1, s0, ws, we, sub)
    if win is not None:                                       # gcdonly: the vector operands pass through a window of kR + 1 block spectra (proof 4.5), the entries are held whole, one accumulator
        hset, kR = win
        temps_a = [(min(ld_nblk(l, A_HB), kR + 1) if i in hset else ld_nblk(l, A_HB)) * A_NB for i, l in enumerate(ops)] + [A_NB]
    else: temps_a = [ld_nblk(l, A_HB) * A_NB for l in ops] + [A_NB]
    best = None; small = None
    for bb in range(6, BIGA):
        r = ld_scheme_c(1 << bb, need, ops, prods, live, outlen, ws, sub, cf)
        if r is not None:
            key = r[0] - (r[4] if VFREEZE else 0); tsum = sum(r[1])
            if small is None or tsum < small[0] or (tsum == small[0] and key < small[1]): small = (tsum, key) + r + (1 << bb,)
            if _tmax() is not None and tsum > _tmax(): continue
            if best is None or key < best[0]: best = (key,) + r + (1 << bb,)
    if _tmax() is not None and sum(temps_a) > _tmax() and not force_a:         # scheme (a) is over the bound: scheme (c) within it, else the smaller working set of the two
        if best is None and small[0] >= sum(temps_a): best = None
        elif best is None: best = small[1:]
        if best is not None:
            key, co, temps_c, n2, nc, ex, hbc = best
            LD_LAST_NC = nc; return co, temps_c, 'c', hbc, ex
    if best is None and small is not None: best = small[1:]
    assert best is not None, need
    key, co, temps_c, n2, nc, ex, hbc = best
    if key <= ca and not force_a and (_tmax() is None or sum(temps_c) <= _tmax()): LD_LAST_NC = nc; return co, temps_c, 'c', hbc, ex
    LD_LAST_NC = 1
    return ca, temps_a, 'a', A_HB, 0


def ld_bilin_big(nout, outlen, groups, ws=0, ltrue=None, stream=False, force_a=False):
    """the block form of a bilinear product (apply_inv, mat_mul): need from the true lengths (cancellation) or the product lengths; returns (ops, eps, temps, mode, hb)
    gcdonly: stream = the vector operands pass through a window of kR + 1 block spectra (the in-place apply); force_a = scheme (a) only"""
    eps = [0] * nout
    for g in groups:
        for s in range(len(g['S'])):
            for h in range(len(g['H'])):
                o, sg = g['prod'].get((s, h), (-1, 0))
                if o >= 0 and not eps[o]: eps[o] = sg
    prods = [[] for _ in range(nout)]
    for g in groups:
        for (si, hi_), (o, sg) in g['prod'].items():
            if o >= 0: prods[o].append((g['S'][si], g['H'][hi_]))
    if LD_SEQ and nout == 2 and not stream and not force_a:   # gcdonly: the two outputs one after the other, the operand forms of the second made again (charged); the larger working set of the two
        tot = 0; best = None; eps2 = [0] * nout
        for k in range(nout):
            gk = []
            for g in groups:
                pr = {sh: osg for sh, osg in g['prod'].items() if osg[0] == k}
                if pr: gk.append(dict(H=list(g['H']), S=list(g['S']), prod=pr))
            if not gk: continue
            c1, e1, t1, m1, h1, x1 = ld_bilin_big(1, [outlen[k]], [dict(H=g['H'], S=g['S'], prod={sh: (0, osg[1]) for sh, osg in g['prod'].items()}) for g in gk], ws, [ltrue[k]] if ltrue else None)
            tot += c1; eps2[k] = e1[0]
            if best is None or sum(t1) > sum(best[0]): best = (t1, m1, h1)
        VLOG['seq'] += 1
        return tot, eps2, best[0], best[1], best[2], 0
    ops_ = []; hset = set(); kR = 1
    for g in groups:
        hset.update(range(len(ops_), len(ops_) + len(g['H'])))
        ops_ += list(g['H']) + list(g['S'])
        for l in g['S']: kR = max(kR, ld_nblk(l, A_HB))
    live = [k for k in range(nout) if eps[k] and prods[k]]
    need = 0
    for k in live:
        L = ltrue[k] if ltrue else max(ls + lh - 1 for ls, lh in prods[k])
        need = max(need, ws + outlen[k], L - ws)
    co, temps, mode, hb, ex = ld_choose(need, ops_, prods, live, list(outlen), ws, False, LD_CFV, (hset, kR) if stream else None, force_a)
    VLOG['ex'] += ex
    return co, eps, temps, mode, hb, ex


def ld_scratch_return(T, kc, k, Rl):
    """1aa56884 scratch region (gate convention): the matrix of a call with k < 2^44 made from a call with k >= 2^44 is copied into the arena"""
    if LD_CONV['scratch'] and Rl is not None and kc < LD_KSCR <= k:
        T.ctl(4 * sum(Rl) + 20 + 4 * (121 + 13 * 2001 + 64))


def mat_mul_ld(A, B, b):
    """R1 Q R2 of a node (1aa56884 4.4): the four outputs by the single transform or the block products, whichever is cheaper; returns (Tr, lens, slots, consumed)"""
    T = Tr(b); T.ctl(80)
    Al, Bl = A[0], B[0]
    Ls = [0] * 4
    for i in range(2):
        for j in range(2):
            l = 0
            for t in range(2):
                la, lb = Al[2 * i + t], Bl[2 * t + j]
                if la and lb and la + lb - 1 > l: l = la + lb - 1
            Ls[2 * i + j] = l
    Lmax = max(1, max(Ls))
    outl = [0] * 4; outs = [0] * 4
    if Lmax <= 48:
        for i in range(2):
            for j in range(2):
                l = Ls[2 * i + j]
                o = T.new_fp(l if l else 1)
                T.st(l); T.loopc(l)
                for t in range(2):
                    la, lb = Al[2 * i + t], Bl[2 * t + j]
                    if not la or not lb: continue
                    tmp = T.new_fp(la + lb - 1)
                    T.ops += poly_mul_naive_cost(la, lb)
                    T.ops += la + lb - 1
                    T.ld(2 * (la + lb - 1)); T.st(la + lb - 1); T.loopc(la + lb - 1)
                    T.free(tmp); T.ctl(6)
                T.ctl(trim(1))
                outl[2 * i + j] = l; outs[2 * i + j] = o
        return T, outl, outs, False
    Pl, c = plan3_for_len(Lmax); T.ctl(c)
    N = Pl.N
    groups = []
    for t in range(2):
        g = dict(H=[], S=[], prod={}); hj = [-1, -1]
        for j in range(2):
            if Bl[2 * t + j]:
                hj[j] = len(g['H']); g['H'].append(Bl[2 * t + j])
        for i in range(2):
            if Al[2 * i + t]:
                s = len(g['S']); g['S'].append(Al[2 * i + t])
                for j in range(2):
                    if hj[j] >= 0: g['prod'][(s, hj[j])] = (2 * i + j, 1)
        if g['H'] and g['S']: groups.append(g)
        T.ctl(20)
    cb, eb, temps, mode, hb, exb = ld_bilin_big(4, Ls, groups)
    BIG = Pl.a > BIGA
    if not BIG:
        cs, es = conv_bilin_cost(Pl, 4, Ls, groups)
        BIG = cb - (exb if VFREEZE else 0) + VCHOICE * (len(temps) - 7) * (122 + 13 * (2 * (T.base + T.cnt) + 1) + FREE_OPS) < cs + sum(Ls[k] * 8 + 2 for k in range(4) if es[k])
    if not BIG and POOL_PLACE & 4:                            # pool_place bit 4: the transforms and products at the end of the children's matrices
        tH0, tH1, tS = [pp_new(T, Pl.n, pp_end(1)) for _ in range(3)]
        ob = [pp_new(T, N, pp_end(1)) for _ in range(4)]
        cc, eps = cs, es
    elif not BIG:
        if POOL_PLACE & 1: opre = [T.new_fp(Ls[k] if Ls[k] else 1) for k in range(4)]                  # pool_place bit 1: the four outputs first, low end
        elif POOL_PLACE & 2: opre = [T.new_fp(Ls[k] if Ls[k] else 1) for k in range(4)]  # pool_place bit 2: the four outputs first, high end  # pool:H
        tH0 = T.new_fp(Pl.n); tH1 = T.new_fp(Pl.n); tS = T.new_fp(Pl.n)
        ob = [T.new_fp(N) for _ in range(4)]  # pool:H
        cc, eps = cs, es
    else:
        cc, eps = cb, eb
    T.ctl(cc)
    if BIG:
        LD_LOG['mat_' + mode] += 1
        ob = [ld_new(T, (Ls[k] + (2 if POOL_PLACE & 16 else 0)) if Ls[k] else 1, 'mat') for k in range(4)]      # pool_place bit 16: two spare slots (R Q in place)
        held = [ld_new(T, y, 'tmp') for y in temps]
        for x in held: T.free(x)
        for M_ in (A, B):
            for s_ in M_[1]:
                if s_: T.free(s_)
    else:
        LD_LOG['mat_single'] += 1
        T.free(tH0); T.free(tH1); T.free(tS)
    T.ctl(ld_invN(2 * hb if BIG else Pl.N))
    for k in range(4):
        l = Ls[k]
        if BIG:
            T.ctl(3)
            if not eps[k]: T.st(l); T.loopc(l)
            outs[k] = ob[k]
            if l: T.ctl(trim(1))
            outl[k] = l
            continue
        if POOL_PLACE & 4: o = pp_new(T, (l + (2 if POOL_PLACE & 16 else 0)) if l else 1, pp_end(0))                # pool_place bit 4: the output matrix at the end of the node (bit 16: two spare slots)
        elif POOL_PLACE & 16: o = T.new_fp(l + 2 if l else 1)  # pool:H
        else: o = opre[k] if POOL_PLACE & 3 else T.new_fp(l if l else 1)  # pool:H
        T.ctl(3)
        if eps[k]:
            T.ops += l; T.ld(l); T.st(l); T.loopc(l)
        T.free(ob[k])
        outs[k] = o
        if l: T.ctl(trim(1))
        outl[k] = l
    return T, outl, outs, BIG


def apply_inv_ld(Rl, Rs, h, la, lb, consume, b, own_in=(0, 0), sa=0, sb=0, win=0):
    """(c, d) = R^-1 (a, b) on the true lengths la - h, la - h - 1 (the high coefficients cancel: cyclic exactness for need >= the true length), the top window [win, .) when win > 0
    (block products only); the single transform or the block products, whichever is cheaper.  Returns (Tr, lc, sc, ld, sd, (False, False, win))"""
    T = Tr(b)
    nres = la
    Pl, c = plan3_for_len(nres); T.ctl(c)
    sgn = -1 if (h & 1) else 1
    T.ctl(60)
    ec = [3, 1]; ed = [2, 0]; scv = [sgn, -sgn]; sdv = [-sgn, sgn]
    lV = [la, lb]
    groups = []
    for v in range(2):
        g = dict(H=[lV[v]], S=[], prod={})
        if not lV[v]: continue
        if Rl[ec[v]]:
            g['prod'][(len(g['S']), 0)] = (0, scv[v]); g['S'].append(Rl[ec[v]])
        if Rl[ed[v]]:
            g['prod'][(len(g['S']), 0)] = (1, sdv[v]); g['S'].append(Rl[ed[v]])
        if g['S']: groups.append(g)
        T.ctl(10)
    lc0 = la - h; ld0 = lc0 - 1
    inpl = bool(GCDONLY) and bool(consume) and bool(own_in[0]) and bool(own_in[1]) and not win and int(sa) >= lc0 and int(sb) >= ld0   # gcdonly: c over a, d over b
    global LD_INVCTX
    hs_ = set(); n_ = 0
    for g in groups: hs_.update(range(n_, n_ + len(g['H']))); n_ += len(g['H']) + len(g['S'])
    LD_INVCTX = (bool(consume), hs_)
    try: cb, eb, temps, mode, hb, exb = ld_bilin_big(2, [lc0 - win, ld0 - win], groups, win, [lc0, ld0], inpl)
    finally: LD_INVCTX = None
    if inpl and mode == 'c' and LD_LAST_NC > 1: inpl = False         # a chunked scheme (c) re-reads the operands per chunk: not in place (outputs allocated, the caller frees a and b)
    BIG = Pl.a > BIGA
    if not BIG:
        cs, es = conv_bilin_cost(Pl, 2, [nres, nres], groups)
        BIG = cb - (exb if VFREEZE else 0) + VCHOICE * (len(temps) - 2) * (122 + 13 * (2 * (T.base + T.cnt) + 1) + FREE_OPS) + 6 < cs + sum(8 * nres + 2 + (1 if es[k] < 0 else 0) for k in range(2) if es[k])
    if LD_LMAX and nres > LD_LMAX: BIG = True                # memory cap (the mat_apply LMAX of weijiekoh a78f526e, proof.md 4.4): an apply longer than LD_LMAX is done by block products
    if not BIG: win = 0
    if BIG:
        LD_LOG['inv_' + mode + ('_ip' if inpl else '')] += 1
        if inpl:
            sc_, sd_ = sa, sb                                  # gcdonly: scheme (c) in place only with one chunk (the operands are folded before any output is written)
        else:
            sc_ = ld_new(T, lc0 - win, 'inv')
            sd_ = ld_new(T, ld0 - win, 'inv')
        cc, eps = cb, eb
        T.ctl(cc)
        held = [ld_new(T, y, 'tmp') for y in temps]
        for x in held: T.free(x)
        if consume: mat_free(T, Rs)
    else:
        LD_LOG['inv_single' + ('_ip' if inpl else '')] += 1
        N = Pl.N
        if POOL_PLACE & 4: tH = pp_new(T, Pl.n, pp_end(1)); tS = pp_new(T, Pl.n, pp_end(1))      # pool_place bit 4: the transforms at the other end
        else: tH = T.new_fp(Pl.n); tS = T.new_fp(Pl.n)
        sc_ = ld_new(T, N, 'inv')
        sd_ = ld_new(T, N, 'inv')
        cc, eps = cs, es
        T.ctl(cc)
        T.free(tH); T.free(tS)
        if consume: mat_free(T, Rs)
    T.ctl(ld_invN(2 * hb if BIG else Pl.N))
    for k in range(2):
        T.ctl(3)
        if not eps[k]:
            T.st(nres); T.loopc(nres); continue
        if BIG: continue
        if eps[k] < 0: T.ops += 1
        T.ops += nres; T.ld(nres); T.st(nres); T.loopc(nres)
    lc = la - h; ld = lc - 1
    if BIG: T.ctl(trim(1) + trim(1))
    else: T.ctl(trim(1 + (nres - lc)) + trim(1 + (nres - ld)))
    if inpl and not BIG:                                      # gcdonly: the scaled outputs were stored into the arrays of a and b (the same loads and stores as the in-row scaling); the rows are freed
        T.free(sc_); T.free(sd_); sc_, sd_ = sa, sb
    return T, lc, sc_, ld, sd_, (inpl, inpl, win)


def hgcd_base_ld(la, sa, lb, sb, k, want_mat, own, wc, wd, T):
    """the base case in place (1aa56884 4.4): the division r = a - q0 b - q1 b' written over the array of a, the roles swapped; R := R Q by mul_add_q2 written over r12 / r22"""
    if own & 1: sx = sa
    else:
        t, sx = dupv(la, T.here()); T.add(t)
    if own & 2: sy = sb
    else:
        t, sy = dupv(lb, T.here()); T.add(t)
    lx, ly = la, lb
    Rl = Rs = None
    if want_mat:
        Rs = [T.new_fp(k + 2) for _ in range(4)]
        T.st(2); T.ctl(8)
        Rl = [1, 0, 0, 1]
    ssum = 0
    while ly > 0:
        dq = lx - ly
        T.ctl(6)
        if dq > k - ssum: break
        dc, lq, lr, _ = divrem_naive(lx, ly)
        T.ctl(dc + LD_ABORT + 4)
        if want_mat:
            for e, f in ((0, 1), (2, 3)):
                le, lf = Rl[e], Rl[f]
                lt = le + 1 if le else 0; lo = max(lt, lf)
                T.ops += (le + max(le - 1, 0) + (1 if le > 0 else 0)) + (max(le - 1, 0) + (min(lf, le + 1) if le > 0 else 0))
                T.ld(le + lf); T.st(lo); T.loopc(lo); T.ctl(8 + 8 * lo); T.ctl(trim(1))
                Rl[e], Rl[f] = lo, le; Rs[e], Rs[f] = Rs[f], Rs[e]
            T.ctl(4)
        ssum += dq
        lx, ly = ly, lr; sx, sy = sy, sx
    lc = sc = ld = sd = None
    if wc: lc, sc = lx, sx
    else: T.free(sx)
    if wd: ld, sd = ly, sy
    else: T.free(sy)
    return T, (lc, sc, ld, sd, Rl, Rs, ssum)


def _hgcd_ld(la, sa, lb, sb, k, want_mat, own, wc, wd, b, fr=()):
    """hgcd of 1aa56884 4.4 (memoised through hgcd(); fr: arrays of the caller freed after the first apply_inv, the top node only)"""
    T = Tr(b); T.ctl(40)
    n = la - 1
    if lb == 0 or n - (lb - 1) > k:
        Rl = Rs = None
        if want_mat:
            t, Rl, Rs = mat_identity(T.here()); T.add(t)
        T.ctl(4)
        lc = sc = ld = sd = None
        if wc:
            if own & 1: sc = sa
            else:
                t, sc = dupv(la, T.here()); T.add(t)
            lc = la
        elif own & 1: T.free(sa)
        if wd:
            if own & 2: sd = sb
            else:
                t, sd = dupv(lb, T.here()); T.add(t)
            ld = lb
        elif own & 2: T.free(sb)
        return T, (lc, sc, ld, sd, Rl, Rs, 0)
    if k <= 96:
        return hgcd_base_ld(la, sa, lb, sb, k, want_mat, own, wc, wd, T)
    k1 = (k + 1) >> 1
    if k1 + k1 > n: k1 = n >> 1
    s = n - 2 * k1
    las = la - s; lbs = lb - s if lb > s else 0
    t1, o1 = pp_call(hgcd, las, 0, lbs, 0, k1, 1, 0, False, False, T.here())
    T.add(t1)
    R1l, R1s, h1 = o1[4], o1[5], o1[6]
    ld_scratch_return(T, k1, k, R1l)
    T.ctl(LD_ABORT)                                           # the return test
    assert h1 >= 1, 'non-generic shape'
    w = 0
    if LD_WIN and want_mat and not wc and not wd:             # lemma 4.8(a): the top window of c and d, degrees >= s3 - 1
        lc_ = la - h1; ld_ = la - h1 - 1; k3_ = k - h1 - 1; s3_ = (ld_ - 1) - 2 * k3_
        if s3_ > 0 and not (ld_ == 0 or (lc_ - ld_) > k - h1): w = s3_ - 1
    t2, lcc, scc, ldd, sdd, reuse = apply_inv_ld(R1l, R1s, h1, la, lb, not want_mat, T.here(), (own & 1, (own >> 1) & 1), sa, sb, w)
    T.add(t2); T.ctl(4)
    w = reuse[2]
    if w: T.ctl(2 * LD_ABORT)                                 # the windowed node tests the coefficients at the leading degrees
    for x in fr: T.free(x)
    if own & 1 and not reuse[0]: T.free(sa)                   # gcdonly: an in-place apply returned c in the array of a (d in that of b)
    if own & 2 and not reuse[1]: T.free(sb)
    sumdeg = n - (lcc - 1); k2 = k - sumdeg
    if ldd == 0 or (lcc - ldd) > k2:
        Rl = Rs = None
        if want_mat: Rl, Rs = R1l, R1s
        lc = sc = ld = sd = None
        if wc: lc, sc = lcc, scc
        else: T.free(scc)
        if wd: ld, sd = ldd, sdd
        else: T.free(sdd)
        return T, (lc, sc, ld, sd, Rl, Rs, h1)
    dq = lcc - ldd
    dqm = max(dq, k2) if WC_MEM else dq
    sq = ld_new(T, dqm + 1, 'div')
    srm = scc if GCDONLY else ld_new(T, lcc - w, 'div')       # gcdonly: the remainder over the dividend
    if WC_MEM: T.bump_blocks(wc_div_arrays(lcc - w, dqm))
    T.ctl(3)
    dc, lq, lrem, _ = divrem_naive(lcc - w, ldd - w)
    lrem += w
    T.ctl(dc + LD_ABORT)                                      # the quotient test
    if not GCDONLY: T.free(scc)
    k3 = k2 - dq
    s3 = (ldd - 1) - 2 * k3
    if s3 > 0:
        t3, o3 = pp_call(hgcd, ldd - s3, 0, lrem - s3, 0, k3, 1, 0, False, False, T.here())
        T.add(t3)
        R2l, R2s, h3 = o3[4], o3[5], o3[6]
        ld_scratch_return(T, k3, k, R2l)
        T.ctl(LD_ABORT)
        lc3 = sc3 = ld3 = sd3 = None
        if wc or wd:
            t4, lc4, sc4, ld4, sd4, reuse4 = apply_inv_ld(R2l, R2s, h3, ldd, lrem, not want_mat, T.here(), (1, 1), sdd, srm, 0)
            T.add(t4); T.ctl(4)
            if not reuse4[0]: T.free(sdd)
            if not reuse4[1]: T.free(srm)
            if wc: lc3, sc3 = lc4, sc4
            else: T.free(sc4)
            if wd: ld3, sd3 = ld4, sd4
            else: T.free(sd4)
        else:
            T.free(sdd); T.free(srm)
            if not want_mat: mat_free(T, R2s)
        o3 = (lc3, sc3, ld3, sd3, R2l, R2s, h3)
    else:
        t3, o3 = pp_call(hgcd, ldd, sdd, lrem, srm, k3, want_mat, 3, wc, wd, T.here())
        T.add(t3)
        T.ctl(LD_ABORT)
    h = h1 + dq + o3[6]
    Rl = Rs = None
    if want_mat:
        R1l2, R1s2 = mat_mulQ(T, R1l, R1s)
        tm, Ml, Ms, cons = mat_mul_ld((R1l2, R1s2), (o3[4], o3[5]), T.here()); T.add(tm)
        if not cons:
            mat_free(T, o3[5]); mat_free(T, R1s2)
        Rl, Rs = Ml, Ms
    T.free(sq)
    return T, (o3[0], o3[1], o3[2], o3[3], Rl, Rs, h)


def apply_inv_split_ld(Rl, Rs, h, cut, outl, b, dcut=None, lowp=()):
    """the top node (1aa56884 4.4 (ii), (iii)): c, then d, from the low pieces (window [0, l) of products of true length cut + len(r) - 1, not cancelled); the entries that a finished
    output no longer needs are freed before the next output; d in two pieces at dcut when asked; the low pieces freed at the end"""
    T = Tr(b); T.ctl(60)
    out = []
    sgn = -1 if (h & 1) else 1
    for o, (e1, e2, sg) in enumerate(((3, 1, sgn), (0, 2, sgn))):
        lo = outl[o]
        if o == 1 and dcut:
            hnd = (ld_new(T, dcut, 'top'), ld_new(T, lo - dcut, 'top'))
        else:
            hnd = ld_new(T, lo, 'top')
        groups = [dict(H=[cut], S=[Rl[e1]], prod={(0, 0): (0, sg)}), dict(H=[cut], S=[Rl[e2]], prod={(0, 0): (0, -sg)})]
        cc, eps, temps, mode, hb, _ex = ld_bilin_big(1, [lo], groups, 0)
        LD_LOG['top_' + mode] += 1
        T.ctl(cc + 10)
        held = [ld_new(T, y, 'tmp') for y in temps]
        for x in held: T.free(x)
        T.free(Rs[e1]); T.free(Rs[e2])
        out.append(hnd)
    for x in lowp: T.free(x)
    T.ctl(7 * 64 + 2 * 3 + trim(1) + trim(1))                # plan_invN of the block plan, two trims, two scales
    return T, out


def hgcd_top_ld(la, lb, k, cut, b, high, low):
    """the top node of stage D with the pieces of g and R (1aa56884 4.4, lemma 4.8(b)); the normal shape is asserted (h1 = k1, h3 = k3, cut >= lc)"""
    T = Tr(b); T.ctl(40)
    n = la - 1
    k1 = (k + 1) >> 1
    if k1 + k1 > n: k1 = n >> 1
    s = n - 2 * k1
    t1, o1 = pp_call(_hgcd_ld, la - s, 0, lb - s, 0, k1, 1, 0, False, False, T.here(), tuple(high))
    T.add(t1)
    R1l, R1s, h1 = o1[4], o1[5], o1[6]
    T.ctl(LD_ABORT)
    lcc = la - h1; ldd = lcc - 1
    assert cut >= lcc and h1 == k1, (cut, lcc, h1, k1)
    k3 = k - h1 - 1
    cut2 = ldd - k3
    t2, (scc, sdd) = apply_inv_split_ld(R1l, R1s, h1, cut, (lcc, ldd), T.here(), cut2, tuple(low))
    T.add(t2); T.ctl(4)
    sumdeg = n - (lcc - 1); k2 = k - sumdeg
    assert not (ldd == 0 or (lcc - ldd) > k2), 'top shape'
    dq = lcc - ldd
    sq = ld_new(T, dq + 1, 'topdiv')
    srm = (ld_new(T, cut2, 'topdiv'), ld_new(T, lcc - cut2, 'topdiv'))
    T.ctl(3)
    dc, lq, lrem, _ = divrem_naive(lcc, ldd)
    T.ctl(dc + LD_ABORT)
    T.free(scc)
    assert k3 == k2 - dq
    s3 = (ldd - 1) - 2 * k3
    assert s3 > 0, s3
    t3, o3 = pp_call(_hgcd_ld, ldd - s3, 0, lrem - s3, 0, k3, 1, 0, False, False, T.here(), (sdd[1], srm[1]))
    T.add(t3)
    R2l, R2s, h3 = o3[4], o3[5], o3[6]
    T.ctl(LD_ABORT)
    assert h3 == k3, (h3, k3)
    lc4 = ldd - h3; ld4 = lc4 - 1
    t4, (sc4, sd4) = apply_inv_split_ld(R2l, R2s, h3, cut2, (lc4, ld4), T.here(), None, (sdd[0], srm[0]))
    T.add(t4); T.ctl(4)
    T.free(sq)
    return T, (lc4, sc4, ld4, sd4, None, None, h1 + dq + h3)


def go_apply(T, Rl, Rs, h, lV, outl, tag):
    """gcdonly: the simultaneous in-place apply of the top node, (c, d) = R^-1 (a, b) from the low pieces of a and b (lV coefficients each; products of true length lV + len(r) - 1, not
    cancelled; the windows [0, outl)); both outputs are formed slot by slot over the owned arrays of a and b (streamed scheme (a): windows of kR + 1 block spectra, the four entry spectra,
    one accumulator; or scheme (c) in one chunk), the entries freed; the charges of apply_inv_split_ld for one product of two outputs"""
    sgn = -1 if (h & 1) else 1
    ec = [3, 1]; ed = [2, 0]; scv = [sgn, -sgn]; sdv = [-sgn, sgn]
    groups = []; hidx = []; sidx = []; idx = 0
    T.ctl(60)
    for v in range(2):
        g = dict(H=[lV[v]], S=[], prod={}); es = []
        if Rl[ec[v]]:
            g['prod'][(len(g['S']), 0)] = (0, scv[v]); g['S'].append(Rl[ec[v]]); es.append(ec[v])
        if Rl[ed[v]]:
            g['prod'][(len(g['S']), 0)] = (1, sdv[v]); g['S'].append(Rl[ed[v]]); es.append(ed[v])
        if g['S']:
            groups.append(g); hidx.append(idx); idx += 1
            for e in es: sidx.append((idx, e)); idx += 1
        T.ctl(10)
    cc, eps, temps, mode, hb, _ex = ld_bilin_big(2, list(outl), groups, 0, None, True)
    if mode == 'c' and LD_LAST_NC > 1: cc, eps, temps, mode, hb, _ex = ld_bilin_big(2, list(outl), groups, 0, None, True, True)   # chunked (c) cannot be in place: streamed scheme (a)
    need = max(lV[v] + max([Rl[ec[v]], Rl[ed[v]]]) - 1 for v in range(2))
    Pl, cpl = plan3_for_len(need); T.ctl(cpl)
    BIG = Pl.a > BIGA
    if not BIG:                                               # the single transform (as apply_inv_ld, cyclic length >= the true product length, no cancellation): the cheaper by charge
        cs, es = conv_bilin_cost(Pl, 2, list(outl), groups)
        BIG = cc + VCHOICE * (len(temps) - 2) * (122 + 13 * (2 * (T.base + T.cnt) + 1) + FREE_OPS) + 6 < cs + sum(8 * outl[k] + 2 + (1 if es[k] < 0 else 0) for k in range(2) if es[k])
    if not BIG:
        LD_LOG[tag + '_single_ip'] += 1
        N = Pl.N
        if STREAMD and tag in ('top', 'top2'):                                    # rival 716c3818 stage-D schedule: the truncated half-gcd apply processes the Good-Thomas rows one at a time through a
            sFd = ld_new(T, N // 2, 'inv')                                        # SINGLE folded N'=N/2 transform buffer (lever 3), reused in place - no separate operand transforms sH/sS and no second output buffer sD
            T.ctl(cs)                                                            # the six forward transforms and two inverse transforms of the row (same conv charge; the entries stream in, not stored whole)
            T.ctl(2 * (for8(N) + 5 * N))                                         # lever 1/3: each output c,d is folded out of the one half-length spectrum in place (F[i]:=Y[i]+Y[i+N'], Y:=F-Y), one pass each, charged
            mat_free(T, Rs)
            T.ctl(ld_invN(Pl.N))
            for k in range(2):
                T.ctl(3)
                if not es[k]: T.st(outl[k]); T.loopc(outl[k]); continue
                if es[k] < 0: T.ops += 1
                T.ops += outl[k]; T.ld(outl[k]); T.st(outl[k]); T.loopc(outl[k])
            T.ctl(trim(1) + trim(1))
            T.free(sFd)
            return
        tH = T.new_fp(Pl.n); tS = T.new_fp(Pl.n)
        oc = ld_new(T, N, 'inv'); od = ld_new(T, N, 'inv')
        T.ctl(cs)
        T.free(tH); T.free(tS)
        mat_free(T, Rs)
        T.ctl(ld_invN(Pl.N))
        for k in range(2):
            T.ctl(3)
            if not es[k]: T.st(outl[k]); T.loopc(outl[k]); continue
            if es[k] < 0: T.ops += 1
            T.ops += outl[k]; T.ld(outl[k]); T.st(outl[k]); T.loopc(outl[k])      # the scaled output stored into the array of a (b)
        T.ctl(trim(1) + trim(1))
        T.free(oc); T.free(od)
        return
    LD_LOG[tag + '_' + mode + '_ip'] += 1
    T.ctl(cc + 10)
    if mode == 'a':                                           # the spectrum of each entry is made first and its coefficient array freed at once; then the two windows and the accumulator
        assert len(temps) == idx + 1
        held = []; done = set()
        for i, e in sidx:
            held.append(ld_new(T, temps[i], 'tmp')); T.free(Rs[e]); done.add(e)
        for i in hidx: held.append(ld_new(T, temps[i], 'tmp'))
        held.append(ld_new(T, temps[-1], 'tmp'))
        for x in reversed(held): T.free(x)
        for e in range(4):
            if e not in done and Rs[e]: T.free(Rs[e])
    else:
        held = [ld_new(T, y, 'tmp') for y in temps]
        for x in held: T.free(x)
        mat_free(T, Rs)
    T.ctl(ld_invN(2 * hb))
    for k in range(2):
        T.ctl(3)
        if not eps[k]: T.st(outl[k]); T.loopc(outl[k])
    T.ctl(trim(1) + trim(1))


def hgcd_top_go(la, lb, k, b, sx, sy):
    """gcdonly top node: g (sx) and R (sy) in three pieces [0, cut2'), [cut2', cut), [cut, n1).  The first call frees the high pieces after its first apply; c is written over g[0, cut) and
    d over R[0, cut) by one simultaneous apply; the division writes the remainder over c; the second call frees the middle pieces after its first apply; the second apply writes c4 over
    R[0, cut2') and d4 over g[0, cut2').  The normal shape is asserted (h1 = k1, h3 = k3, cut >= lcc, cut2' >= lc4)"""
    T = Tr(b); T.ctl(40)
    n = la - 1
    k1 = (k + 1) >> 1
    if k1 + k1 > n: k1 = n >> 1
    s = n - 2 * k1
    cut2p = int(sx[0]); cut = cut2p + int(sx[1])
    assert int(sy[0]) == cut2p and int(sy[1]) == int(sx[1])
    t1, o1 = pp_call(_hgcd_ld, la - s, 0, lb - s, 0, k1, 1, 0, False, False, T.here(), (sx[2], sy[2]))
    T.add(t1)
    R1l, R1s, h1 = o1[4], o1[5], o1[6]
    T.ctl(LD_ABORT)
    lcc = la - h1; ldd = lcc - 1
    assert cut >= lcc and h1 == k1, (cut, lcc, h1, k1)
    k3 = k - h1 - 1
    cut2 = ldd - k3
    assert cut2 <= cut2p < cut, (cut2, cut2p, cut)
    go_apply(T, R1l, R1s, h1, (cut, cut), (lcc, ldd), 'top')
    T.ctl(4)
    sumdeg = n - (lcc - 1); k2 = k - sumdeg
    assert not (ldd == 0 or (lcc - ldd) > k2), 'top shape'
    dq = lcc - ldd
    sq = ld_new(T, dq + 1, 'topdiv')
    T.ctl(3)
    dc, lq, lrem, _ = divrem_naive(lcc, ldd)                  # the remainder over c (g[0, cut))
    T.ctl(dc + LD_ABORT)
    assert k3 == k2 - dq
    s3 = (ldd - 1) - 2 * k3
    assert s3 > 0, s3
    t3, o3 = pp_call(_hgcd_ld, ldd - s3, 0, lrem - s3, 0, k3, 1, 0, False, False, T.here(), (sy[1], sx[1]))
    T.add(t3)
    R2l, R2s, h3 = o3[4], o3[5], o3[6]
    T.ctl(LD_ABORT)
    assert h3 == k3, (h3, k3)
    lc4 = ldd - h3; ld4 = lc4 - 1
    assert cut2p >= lc4, (cut2p, lc4)
    go_apply(T, R2l, R2s, h3, (cut2p, cut2p), (lc4, ld4), 'top2')
    T.ctl(4)
    T.free(sq)
    return T, (lc4, sy[0], ld4, sx[0], None, None, h1 + dq + h3)


def ld_fastdiv(m):
    """AMORT (Grok job 163): one fast division of length m, the Newton reciprocal of m + 1 coefficients and two products of m + 1 by m + 1 coefficients (this model's fast_division,
    the block products of stage D)"""
    return fast_division(2 * m + 1, m + 1)


def ld_zscan(m):
    """AMORT: the scans past zero leading coefficients of abnormal remainders (trim, 11 per coefficient): a remainder of index j is formed at most twice per level of the recursion
    and has deg q_j - 1 such zeros, sum_j (deg q_j - 1) <= m; levels <= bit length of m"""
    return 2 * 11 * m * m.bit_length()


LD_LMAX = 8388608        # an apply_inv_ld of more than LD_LMAX = 2^23 coefficients uses the block products (None: the cheaper by charge)
GCD_DMAX = 2080768       # cap on the parameter k of one outer half-gcd step, 2^21 - 2^14 (the gcd_lean DMAX of weijiekoh a78f526e; None: no cap)


def gcd_cost_ld(m, dG, b, sx, sy):
    """poly_gcd_own of 1aa56884 4.4 on the normal remainder sequence, with the top node on pieces when sx, sy are (low, high) pairs; AMORT: + ld_fastdiv(m) + ld_zscan(m)"""
    T = Tr(b)
    lx, ly = m + 1, m
    pieces = isinstance(sx, tuple)
    topcut = sum(int(x) for x in sx[:-1]) if pieces else 0
    T.ctl(3); T.ctl(3)
    tail = False
    while ly > 0:
        T.ctl(2)
        n = lx - 1
        T.ctl(4)
        if n <= 2 * 96:
            sq = T.new_fp(lx - ly + 1); sr = sx if GCDONLY else T.new_fp(lx)       # gcdonly: the remainder over the dividend
            last = (ly == dG + 1)
            dc, lq, lr, _ = divrem_naive(lx, ly, term_zero=1 if (last and dG >= 1) else 0)
            if last and dG == 0: lr = 0
            T.ctl(dc + LD_ABORT)
            if not GCDONLY: T.free(sx)
            sx = sy; lx = ly; sy = sr; ly = lr
            T.free(sq); T.ctl(5)
            continue
        k = (n + 1) // 2
        if GCD_DMAX: k = min(k, GCD_DMAX)                     # memory cap (gcd_lean DMAX of weijiekoh a78f526e, proof.md 4.4): one outer step reduces the degree by at most GCD_DMAX
        if k < LD_KSCR: tail = True
        if pieces and lx == m + 1 and GCDONLY:
            t, o = hgcd_top_go(lx, ly, k, T.here(), sx, sy)
        elif pieces and lx == m + 1:
            t, o = hgcd_top_ld(lx, ly, k, topcut, T.here(), (sx[1], sy[1]), (sx[0], sy[0]))
        else:
            t, o = hgcd(lx, sx, ly, sy, k, False, 3, True, True, T.here())
        T.add(t)
        lc, sc, ld, sd = o[0], o[1], o[2], o[3]
        T.ctl(LD_ABORT)                                       # the return test
        T.ctl(2)
        dqm = lc if WC_MEM else lc - ld
        sq = ld_new(T, dqm + 1, 'outer')
        sr = sc if GCDONLY else ld_new(T, lc, 'outer')        # gcdonly: the remainder over the dividend
        if WC_MEM: T.bump_blocks(wc_div_arrays(lc, dqm))
        T.ctl(3)
        dc, lq, lr, _ = divrem_naive(lc, ld)
        T.ctl(dc + LD_ABORT)                                  # the quotient test
        if not GCDONLY: T.free(sc)
        T.free(sq)
        sx = sd; lx = ld; sy = sr; ly = lr; T.ctl(5)
    T.free(sy)
    if tail and LD_CONV['scratch']: T.ctl(40)
    T.ctl(2)
    T.ops += powcost(PM2); T.ctl(INV_CTL); T.ld(1)
    T.ops += lx - 1
    T.ld(lx); T.st(lx); T.loopc(lx)
    if AMORT:
        LD_LOG['fastdiv'] = ld_fastdiv(m); LD_LOG['zscan'] = ld_zscan(m)
        T.ops += LD_LOG['fastdiv'] + LD_LOG['zscan']
    return T, (lx, sx)


# ---------------------------------------------------------------- the allocator of proof 4.2 on the walk: two-ended pool for the big blocks, slab classes for the others
def _big_events(ev, T, memo):
    """the events of the two-ended pool (blocks of more than T bytes, header included) in ev, sizes in bytes; None if there is none"""
    out = []
    for e in ev:
        t = e[0]
        if t == 'A':
            if blk(e[2]) > T: out.append(('A', e[1], blk(e[2]), e[3]))
        elif t == 'F':
            if blk(e[2]) > T: out.append(('F', e[1]))
        elif t == 'T':
            sz = tuple(blk(x) for x in e[1] if blk(x) > T)
            if sz: out.append(('T', sz, e[2]))
        elif t == 'R':
            sub = _big_events(e[2], T, memo)
            if sub: out.append(('R', sub))
        else:
            if id(e[1]) not in memo: memo[id(e[1])] = _big_events(e[1].ev, T, memo)
            if memo[id(e[1])]: out.append(('C', memo[id(e[1])], e[2], e[3]))
    return out or None


class FirstFit:
    """one list of the pool: its blocks [size, id] (id None = free) in address order counted from the list's own end of the pool, no two free blocks adjacent, the unused middle of the
    pool beyond the last block.  An allocation takes the free block nearest its own end with at least `need` bytes, else the unused middle; it takes the side of the block nearest its own
    end, and the rest stays a free block if it is at least 128 bytes (else it is part of the allocated block).  A free merges the block with a free neighbour on either side, and with the
    unused middle.  end = the extent of the list (the far side of its outermost block)."""
    def __init__(self): self.L = []; self.end = 0; self.scans = 0; self.nblk = 0

    def alloc(self, i, need):
        L = self.L
        for k in range(len(L)):
            b = L[k]
            if b[1] is None and b[0] >= need:
                rem = b[0] - need; b[1] = i
                if rem >= 128:
                    b[0] = need; L.insert(k + 1, [rem, None])
                self.scans += k + 1
                return
        self.scans += len(L) + 1
        L.append([need, i]); self.end += need
        self.nblk = max(self.nblk, len(L))

    def free(self, i):
        L = self.L
        k = next(k for k in range(len(L)) if L[k][1] == i and L[k][1] is not None)
        b = L[k]; b[1] = None
        if k + 1 < len(L) and L[k + 1][1] is None:
            b[0] += L[k + 1][0]; del L[k + 1]
        if k > 0 and L[k - 1][1] is None:
            L[k - 1][0] += b[0]; del L[k]; k -= 1; b = L[k]
        if k == len(L) - 1:
            self.end -= b[0]; del L[k]


class TwoEnd:
    """the pool of proof 4.2: one region, list 0 grows from the bottom, list 1 (the statements marked `# pool:H`) from the top, the unused middle between them.  An allocation uses the
    list of its statement only; a free goes back to the list of its block.  high = the largest sum of the two ends; the pool has high + 128 bytes, so the middle is never shorter than 128 bytes."""
    def __init__(self): self.P = (FirstFit(), FirstFit()); self.where = {}; self.high = 0

    def alloc(self, i, need, c):
        self.where[i] = c; self.P[c].alloc(i, need)
        self.high = max(self.high, self.P[0].end + self.P[1].end)

    def free(self, i): self.P[self.where.pop(i)].free(i)

    def snap(self): return tuple(tuple(tuple(b) for b in Q.L) for Q in self.P)


def _ff_run(P, ev, base, ext):
    for e in ev:
        t = e[0]
        if t == 'A': P.alloc(ext[-e[1] - 1] if e[1] < 0 else base + e[1], e[2], e[3])
        elif t == 'F': P.free(ext[-e[1] - 1] if e[1] < 0 else base + e[1])
        elif t == 'T':
            for k, s in enumerate(e[1]): P.alloc(('t', k), s, e[2])
            for k in reversed(range(len(e[1]))): P.free(('t', k))
        elif t == 'R':
            before = P.snap()
            _ff_run(P, e[1], base, ext)
            assert P.snap() == before, 'a repeated group does not restore the pool'
        else:
            _ff_run(P, e[1], base + e[2], tuple(None if x is None else (ext[-x - 1] if x < 0 else base + x) for x in e[3]))


def slab_class(need): return max(QMIN, (need - 1).bit_length())            # the slot of a block of `need` bytes is 2^class bytes


def _slab_walk(ev, T, memo):
    """for each slab class (blocks of at most T bytes): (net, peak) number of live blocks of the events, relative to the entry"""
    cur = collections.defaultdict(int); pk = collections.defaultdict(int)
    for e in ev:
        t = e[0]
        if t == 'A':
            if blk(e[2]) <= T:
                c = slab_class(blk(e[2])); cur[c] += 1; pk[c] = max(pk[c], cur[c])
        elif t == 'F':
            if blk(e[2]) <= T: cur[slab_class(blk(e[2]))] -= 1
        elif t == 'T':
            for c, n in collections.Counter(slab_class(blk(x)) for x in e[1] if blk(x) <= T).items(): pk[c] = max(pk[c], cur[c] + n)
        else:
            if t == 'R': net, pe = _slab_walk(e[2], T, memo)
            else:
                if id(e[1]) not in memo: memo[id(e[1])] = _slab_walk(e[1].ev, T, memo)
                net, pe = memo[id(e[1])]
            for c in set(net) | set(pe):
                pk[c] = max(pk[c], cur[c] + pe.get(c, 0)); cur[c] += net.get(c, 0)
    return dict(cur), dict(pk)


def _walk_sum(ev, memo):
    """(net bytes, peak bytes, net blocks, peak blocks) of the events, relative to the entry: the live-set walk, recomputed from the events"""
    cur = pk = cnt = pc = 0
    for e in ev:
        t = e[0]
        if t == 'A':
            cur += blk(e[2]); cnt += 1; pk = max(pk, cur); pc = max(pc, cnt)
        elif t == 'F':
            cur -= blk(e[2]); cnt -= 1
        elif t == 'T':
            pk = max(pk, cur + sum(blk(x) for x in e[1])); pc = max(pc, cnt + len(e[1]))
        else:
            if t == 'R': r = _walk_sum(e[2], memo)
            else:
                if id(e[1]) not in memo: memo[id(e[1])] = _walk_sum(e[1].ev, memo)
                r = memo[id(e[1])]
            pk = max(pk, cur + r[1]); pc = max(pc, cnt + r[3]); cur += r[0]; cnt += r[2]
    return cur, pk, cnt, pc


QE_BYTES = 16 * 1024 + 512              # stage E and the later stages: at most 16 live arrays of at most 17 elements (a slot of 1,024 bytes each), taken from the slab classes; and the 36 words of the allocator (35 free-list heads, the end of the slab area)


def pool_account(stage_ev, big_exp):
    """the arena of one trial for the allocator of proof 4.2: stage_ev = [(name, events)] in the order of the program (init, A, B, C, D).  Blocks of more than 2^big_exp bytes come from the
    two-ended pool (TwoEnd, simulated address by address on the events), the others from the slab classes (a slot of 2^class bytes; a class takes a new slot from the end of the slab area when
    its free list is empty, so that the area is the sum over the classes of the peak number of live blocks times the slot).  The pool has `high + 128` bytes (high = the largest sum of the two ends; the unused middle
    is then always at least 128 bytes)."""
    T = 1 << big_exp
    P = TwoEnd(); bm = {}; sm = {}; wm = {}
    cur = collections.defaultdict(int); pk = collections.defaultdict(int); per = {}
    wcur = wpk = wcnt = wpc = 0
    for name, ev in stage_ev:
        f = _big_events(ev, T, bm) or []
        _ff_run(P, f, 0, ())
        per[name] = P.high
        net, pe = _slab_walk(ev, T, sm)
        for c in set(net) | set(pe):
            pk[c] = max(pk[c], cur[c] + pe.get(c, 0)); cur[c] += net.get(c, 0)
        if name == 'init': post = (P.snap(), {c: n for c, n in cur.items() if n})
    assert P.snap() == post[0] and {c: n for c, n in cur.items() if n} == post[1], 'a trial does not return the allocator to its state after init (the second trial would differ)'
    slab = sum(pk[c] << c for c in pk)
    arena = (P.high + 128 + slab + QE_BYTES + 63) & ~63
    return dict(T=T, big_exp=big_exp, big_high=P.high, big_stage=per, slab=slab, slab_peaks={c: pk[c] for c in sorted(pk)}, arena=arena, scans=P.P[0].scans + P.P[1].scans, big_blocks=P.P[0].nblk + P.P[1].nblk,
                big_final=P.snap())


def walk_check(stage_ev):
    """the live-set walk recomputed from the events: (bytes in use, peak bytes, blocks, peak blocks) of each stage"""
    memo = {}
    return {name: _walk_sum(ev, memo) for name, ev in stage_ev}


IMAGE_EXTRA = 399216 + 32 + 4851196        # text + data + static bss besides the arena (proof section 7)
STACK = 65536


def ceil3(x): return math.ceil(x * 1000) / 1000


def twiddle_slots(m):
    a = 2
    while 3 * (1 << a) < 2 * m - 1: a += 1
    return (1 << min(a, BIGA)) // 2                           # init_stage: the table of nmax/2 elements, nmax = 2^min(a, 32)


PM1 = P - 1
TWC_A = 22; TWL_A = 14; TWD_A = 23; TWD_HI = 0
TWMOVE = 1           # the memory schedule of 0xshikhar 52120fad: no twiddle table in init; each stage builds the table of its own largest transform and frees it (charged in that stage)
STHI = 1             # the padded quotient transform sTt of stage C at the high end (over the freed Newton buffers)


def tw_ops(a):
    """the charge of a twiddle table of 2^(a-1) entries for transforms of 3*2^a points, as init_stage: its root and the build loop"""
    n = 1 << (a - 1)
    return 2 + 84 + powcost(PM1 >> a) + 10 + 2 + (n - 1) * 5 + (3 * n + 2)


def tw_new(T, a, hi):
    s = T.new_fp(1 << (a - 1)) if not hi else tw_new_h(T, a)
    T.ctl(tw_ops(a)); return s


def tw_new_h(T, a):
    return T.new_fp(1 << (a - 1))  # pool:H


def sTt_h(T, n):
    return T.new_fp(n)  # pool:H


# ================================================================ stage C on truncated point sets, after bradcush b30de9bf / a41aecdd (credited derivative; proof 4.3T)
# Truncated point sets: O1 = the first c of the 2^d depth-d nodes (bit-reversed prefix) of H_N, N = VD_H = 2^L; O2 the same inside psi H_N; n' = c 2^(L-d) >= m + 1.
# Passes (charges by the rules of this model: LD/ST 2, field op 1, BF/IB 3, loop 3 per iteration, addresses 2 per block):
#   bottom pass  (levels L-3..L-1, 8-point blocks over n' points): 7 twiddles per block (TR_TWB), shared by forward and inverse (V^T V = 8 diag(1, cJ));
#   middle passes (radix-8 with the 7 group twiddles in registers, TR_TWG per group; radix-16 loads its 15 twiddles per block), positions = TR_A(top level of the pass);
#   top pass     (levels 0..2, 8-point blocks over all N/8 offsets, no truncation saving): inverse top + coset twiddle (16 per block) + forward top fused;
#   inverse recovery of every dropped maximal subtree (depth s, size S): TR_RCV per offset per level of its path (3 mul + 3 add + LD + ST = 10).
TRC = (1491, 11)     # (c, d): O1 = the first c = 1491 of the 2^d = 2048 depth-11 nodes of H_N, N = 2^25 (None: off)
TR_MID = None        # radices of the middle passes, top-down (None: radix 16 first while the remainder is not a multiple of 3, then radix 8)
TR_TWB = 15          # bottom block twiddles: 7 constants from a two-level root table (LD 2 = 4, 1 mul, 2 sqr, 4 mul by register constants) charged 7 LD + 1
TR_TWG = 15          # middle radix-8 group twiddles, as TR_TWB
TR_RCV = 10
TR_PASS = 20         # one pass: entry, exit, pointers
TR_TABW = 4 * 4096   # two-level root tables (forward/inverse x O1/O2) in words
TR_DELTA = 1         # the multiplication of B2 by the node factor delta_j = 1/P1 on node j of O2 (P1 is constant on each node of O2, not on O2), and its load per block
TR_INVS = 9          # inverse bottom pass: V^T V = 8 diag(1, cJ), c = y^8 of the block, so each 8-point block is scaled by diag(1, c^-1 J): 7 mul + LD c^-1 (2) = 9
TR_NODEC = 1         # the c node factors delta_j kept in the constant table sTab (NTAB + c entries), each charged as one table constant (two inversions and 60)


def tr_dims():
    L = VD_H.bit_length() - 1; c, d = TRC
    return L, c, d, c << (L - d)


def tr_A(t):
    L, c, d, n1 = tr_dims()
    if t >= d: return n1
    return (-(-c // (1 << (d - t)))) << (L - t)


def tr_dropped():
    L, c, d, n1 = tr_dims(); out = []; s = c; top = 1 << d
    while s < top:
        j = 0
        while s % (1 << (j + 1)) == 0 and s + (1 << (j + 1)) <= top: j += 1
        out.append((d - j, (1 << j) << (L - d))); s += 1 << j
    return out


def tr_mid():
    L = VD_H.bit_length() - 1; k = L - 6
    if TR_MID: assert sum(TR_MID) == k; return list(TR_MID)
    r = []
    while k % 3: r.append(4); k -= 4
    return r + [3] * (k // 3)


def tr_middle():
    L = VD_H.bit_length() - 1; t = 3; c = 0
    for k in tr_mid():
        pos = tr_A(t); ngrp = 1 << t; blk_ = pos >> k
        if k == 3: c += blk_ * 73 + ngrp * (TR_TWG + 5)
        elif k == 4: c += blk_ * 195 + ngrp * 5
        else: raise ValueError(k)
        c += TR_PASS; t += k
    return c


def tr_scratch():
    """the positions above n' that a transform touches: the top pass over all N points (tr_A(0) = N), the middle passes (tr_A(t)) and the stores of the recovered
    dropped subtrees (N - n' points); one scratch buffer of N - n' points extends the array being transformed (one transform runs at a time), so the in-place schedule needs no other storage"""
    return max(tr_A(t) for t in range(0, tr_dims()[2] + 1)) - tr_dims()[3]


def tr_recover():
    return sum(TR_RCV * S * s for s, S in tr_dropped())


def tr_top(fused):
    L = VD_H.bit_length() - 1; nb = (1 << L) >> 3
    return nb * ((16 + 36 + 16 + 36 + 16 + 5) if fused else (16 + 36 + 16 + 5)) + 4 * 15 + TR_PASS


def tr_bottom(pw, inv=False):
    n1 = tr_dims()[3]; nb = n1 >> 3
    return nb * (16 + TR_TWB + 36 + (8 * pw + 36 + TR_INVS if pw is not None else 0) + (TR_INVS if inv else 0) + 16 + 5) + TR_PASS


def tr_fwd(): return tr_top(False) + tr_middle() + tr_bottom(None)
def tr_inv(): return tr_top(False) + tr_middle() + tr_bottom(None, True) + tr_recover()


def tr_step(bit):
    """one squaring step: bottom O1 (U = A^2 k1: sqr, LD, mul = 4), inverse middle, top (inv + coset twiddle + fwd), forward middle, bottom O2 (B2 = A2^2 + U g:
    LD A2, sqr, LD g, mul, add, the node factor delta_j = 1/P1(node j) of O2: mul, ST B2 = 10 per slot and the load of delta_j, 2 per block (TR_DELTA);
    +3 for a 1-bit: LD of the point, mul), inverse middle, top, forward middle, two recoveries, 20 for the step"""
    return (tr_bottom(4) + tr_middle() + tr_top(True) + tr_middle() + tr_bottom(9 + TR_DELTA + 3 * bit) + TR_DELTA * 2 * (tr_dims()[3] >> 3) + tr_middle() + tr_top(True) + tr_middle()
            + 2 * tr_recover() + 20)


def tr_scale(n): return 5 + for8(n) + 7 * n
def tr_pw(per): n1 = tr_dims()[3]; return 14 + for8(n1) + per * n1 + 5


def tr_batch_inv():
    n1 = tr_dims()[3]; h = 1 << 16; nch = -(-n1 // h)
    return nch * (20 + for8(h) + 5 * h + vd_inv1() + 2 + for8(h) + 9 * h) + 3 * nch + 2


def powx_tr(m, b, E=PM1H, sg=None):
    T = Tr(b)
    d = vd_dims(m, E)
    h, K, n1, ell = d['h'], d['K'], d['n1'], d['ell']
    assert K == 1 and n1 == tr_dims()[3] and n1 >= m + 1
    assert sg is not None and int(sg) == n1
    T.ctl(200)                                                            # plans of the passes
    T.ctl(12 * d['zc'] + 25 * d['vb'] + 4 * VSHIFT)
    NTAB = 30 + (tr_dims()[1] if TR_NODEC else 0)
    twN = tw_new(T, TWC_A, 1) if TWMOVE else None
    sR2 = T.new_fp(n1)
    sTab = T.new_fp(NTAB + TR_TABW)
    T.ctl(NTAB * (2 * vd_inv1() + 60) + 10 * TR_TABW)
    zg = n1 - (m + 1); T.st(zg); T.ctl(for8(zg))
    sR1 = T.new_fp(n1)
    sG = T.new_fp(ell)  # pool:H
    sM = T.new_fp(ell)  # pool:H
    L = ell; Ymax = L; _yl = 1
    while _yl < L:
        _yl2 = min(2 * _yl, L)
        Ymax = max(Ymax, plan3_for_len(_yl2 + _yl - 1)[0].N, plan3_for_len(_yl2 - 1)[0].N); _yl = _yl2
    sY = T.new_fp(Ymax)  # pool:H
    T.ld(L); T.st(L); T.loopc(L); T.ctl(L)
    T.ctl(4 + 8); T.st(1)
    l = 1
    while l < L:
        l2 = min(2 * l, L)
        T.ctl(8)
        P1, c = plan3_for_len(l2 + l - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P1, l, l2, 0, l2)); T.ctl(plan_invN_ops(P1))
        T.ops += l2 - l
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        P2, c = plan3_for_len(l2 - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P2, l2 - l, l, 0, l2 - l)); T.ctl(plan_invN_ops(P2))
        T.ops += 2 * (l2 - l)
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        l = l2
    T.free(sY); T.free(sG)
    PQ, c = plan3_for_len(2 * ell - 1)
    sTt = (sTt_h(T, max(ell, PQ.N)) if STHI else T.new_fp(max(ell, PQ.N)))
    T.st(ell); T.ctl(for8(ell)); T.ctl(1 * (vd_inv1() + 30))
    T.ctl(c); T.ctl(conv_mulc_otf(PQ, ell, ell, 0, ell)); T.ctl(plan_invN_ops(PQ))
    T.free(sTt); T.free(sM)
    if TWMOVE: T.free(twN)
    T.ld(ell); T.st(ell); T.loopc(ell // 2); T.ctl(2 * (ell // 2))
    # (2) g on O1 (G1) and O2 (in place)
    sG1 = T.new_fp(n1)
    nsc = tr_scratch(); sScr = T.new_fp(nsc) if nsc else None; T.st(nsc); T.ctl(for8(nsc))   # the scratch above n' (top pass, middle passes, recovered subtrees), zero-filled once
    T.ctl(2 * tr_scale(n1) + 2 * tr_fwd())
    # (3) start residue on O2
    zq = n1 - ell; T.st(zq); T.ctl(for8(zq))
    T.ctl(tr_scale(n1) + tr_fwd() + tr_pw(8))
    ext = tr_inv() + tr_scale(n1) + tr_fwd()
    T.ctl(ext)                                                            # (4) to O1
    sAux = T.new_fp(1 << 16); T.ctl(tr_batch_inv()); T.free(sAux)        # (5) k1 = -1/(n^3 g) on O1 (chunked batch inversion)
    steps, nset = d['steps'], d['nset']
    step0, step1 = tr_step(0), tr_step(1)
    T.ctl((steps - nset) * step0 + nset * step1)                         # (6)
    T.ctl(tr_pw(7) + ext + tr_pw(11))                                     # (7)
    T.free(sR1); T.free(sG1)
    if sScr is not None: T.free(sScr)
    interp = tr_inv() + tr_scale(n1)
    T.ctl(2 * interp)                                                     # (8)
    T.free(sTab)
    T.ctl(2 + 500)
    VD.clear(); VD.update(d, ext=ext, step0=step0, step1=step1, interp=interp, NTAB=NTAB)
    info = dict(steps=steps, nset=nset, PN=None, PNp=None, step=step0, mulx=step1 - step0, sg2=sg, sR2=sR2, vd=dict(VD))
    return T, info


def stage_AB(m):
    """the arrays of the stages before C: the twiddle table (init), g (stage A), the array of stage B (freed after the inverse transforms) and F.
    Stage B transforms on the plan of plan_for_len(m + 1): the least a with 2^a >= m + 1 or 3*2^a >= m + 1 (2^a taken first at that a); block mode (that a > BIGA): the ncos cosets
    of 3*2^(BIGA-1); sub-block: the single inverse transform of that plan, SMALL_BLOCK = 1 running the two-ended pool."""
    H = next(v for a in range(2, 96) for v in (1 << a, 3 << a) if v >= m + 1)     # plan_for_len(m + 1): at each a from 2 up, 2^a first, then 3*2^a
    if H > (3 << BIGA):                                      # block mode of stage B (the plan has a > BIGA): no transform of that size exists
        Pl = make_plan(3, BIGA - 1)[0]; ncos = -(-(m + 1) // Pl.N); H = ncos * Pl.N
    I = Tr(0)
    if not TWMOVE: I.new_fp(twiddle_slots(m))
    pcs = ld_pieces(m) if (vd_active(m) and ld_pieces_on()) else None     # LEAND: g (and R) in two pieces [0, cut), [cut, n1) for the top node of stage D (lemma 4.8(b))
    A = Tr(1)
    if pcs: sg = tuple([A.new_fp(p) for p in pcs])  # pool:H
    else: sg = A.new_fp(vd_gslots(m) if vd_active(m) else m + 1)  # pool:H
    B = Tr(2)
    twB = tw_new(B, next(a for a in range(2, 96) if H in (1 << a, 3 << a)), False) if TWMOVE else None     # stage B: the table of its transform (3*2^a points)
    sb = B.new_fp(H)  # pool:H
    B.free(sb)
    if twB is not None: B.free(twB)
    sF = None if vd_active(m) else B.new_fp(fslots(m))                 # VDC: no array F (R leaves stage C in an array of its own)
    return I, A, B, sg, sF


def _pool_walk(P, T, ev, base, ext, cb):
    """the events of one stage flattened onto the two-ended pool (the recorded calls of the half-gcd expanded, their ids linked to the arrays of the caller as in _ff_run, a repeated group once:
    it restores the pool), the blocks of more than T bytes only; cb(kind, id, bytes, list, site) after every allocation and free"""
    for e in ev:
        t = e[0]
        if t == 'A':
            if blk(e[2]) > T:
                i = ext[-e[1] - 1] if e[1] < 0 else base + e[1]
                P.alloc(i, blk(e[2]), e[3]); cb('A', i, blk(e[2]), e[3], e[4] if len(e) > 4 else '')
        elif t == 'F':
            if blk(e[2]) > T:
                i = ext[-e[1] - 1] if e[1] < 0 else base + e[1]
                P.free(i); cb('F', i, blk(e[2]), None, '')
        elif t == 'T':
            sz = [(k, blk(x)) for k, x in enumerate(e[1]) if blk(x) > T]
            for k, s in sz: P.alloc(('t', k), s, e[2]); cb('A', ('t', k), s, e[2], 'temporary arrays of one call')
            for k, s in reversed(sz): P.free(('t', k)); cb('F', ('t', k), s, None, '')
        elif t == 'R':
            before = P.snap()
            _pool_walk(P, T, e[2], base, ext, cb)
            assert P.snap() == before, 'a repeated group does not restore the pool'
        else:
            _pool_walk(P, T, e[1].ev, base + e[2], tuple(None if x is None else (ext[-x - 1] if x < 0 else base + x) for x in e[3]), cb)


def stage_d_trace(stage_ev, big_exp, trace_path=None, show=24):
    """the allocation / free trace of stage D on the two-ended pool: the pool after init, A, B and C, then every allocation and free of a big block of stage D in the order of the program
    (the recursion of the half-gcd expanded), with the live bytes of the trial, the extents of the two ends and their sum; the high-water mark of the pool is the largest sum.  Printed: the
    first `show` events, every event that raises the high-water mark (the last `show` of them), the live blocks of both ends at the high-water mark, the final state; the whole trace is
    written to trace_path when given.  Returns the high-water mark of the pool over the trial (init .. D)"""
    T = 1 << big_exp; P = TwoEnd(); bm = {}
    live = 0
    for name, ev in stage_ev:
        if name == 'D': break
        _ff_run(P, _big_events(ev, T, bm) or [], 0, ())
        live += _walk_sum(ev, {})[0]
    high0 = P.high
    print('stage D on the two-ended pool (blocks of more than 2^%d bytes): after init, A, B, C: low end %s, high end %s, live %s, largest sum so far %s'
          % (big_exp, format(P.P[0].end, ','), format(P.P[1].end, ','), format(live, ','), format(high0, ',')))
    st = dict(n=0, na=0, nf=0, live=live, high=high0, rises=[], at_high=None, names={}, fh=open(trace_path, 'w', encoding='utf-8') if trace_path else None)
    for Q in P.P:                                             # the big blocks carried into stage D (twiddle table, g, R): live in the pool before D; named here so an in-place free of one (GCDONLY writes c over a, d over b) is traced instead of raising
        for b in Q.L:
            if b[1] is not None and b[1] not in st['names']: st['names'][b[1]] = (len(st['names']) + 1, 'carried in to stage D (twiddle table / g / R)')
    head = []

    def cb(kind, i, nbytes, lst, site):
        st['n'] += 1
        if kind == 'A':
            st['na'] += 1; st['live'] += nbytes
            if i not in st['names']: st['names'][i] = (len(st['names']) + 1, site)
        else:
            st['nf'] += 1; st['live'] -= nbytes
        num = st['names'][i][0]
        line = '  %-5s #%-7d %18s bytes %s | live %18s | pool low %18s high %18s sum %18s' % ('alloc' if kind == 'A' else 'free', num, format(nbytes, ','), ('pool ' + ('H' if lst else 'L')) if kind == 'A' else 'pool  ',
                                                                                             format(st['live'], ','), format(P.P[0].end, ','), format(P.P[1].end, ','), format(P.P[0].end + P.P[1].end, ','))
        if site and kind == 'A': line += ' | ' + site
        if st['fh']: st['fh'].write(line + chr(10))
        if len(head) < show: head.append(line)
        if P.high > st['high']:
            st['high'] = P.high; st['rises'].append((st['n'], line))
            st['at_high'] = (st['n'], tuple(tuple((b[0], b[1], st['names'].get(b[1], (0, ''))) for b in Q.L) for Q in P.P))
    _pool_walk(P, T, stage_ev[-1][1], 0, (), cb)
    if st['fh']: st['fh'].close()
    print('  stage D: %s pool events (%s allocations, %s frees) on %s distinct blocks; the first %d:' % (format(st['n'], ','), format(st['na'], ','), format(st['nf'], ','), format(len(st['names']), ','), len(head)))
    for line in head: print(line)
    rises = st['rises']
    print('  the %d events that raise the high-water mark (the last %d shown; event number first):' % (len(rises), min(show, len(rises))))
    for n, line in rises[-show:]: print('  [%s]' % format(n, ','), line)
    if st['at_high']:
        n, ends = st['at_high']
        print('  the pool at the high-water mark (event %s): %s bytes = low end %s + high end %s' % (format(n, ','), format(st['high'], ','), format(sum(b[0] for b in ends[0]), ','), format(sum(b[0] for b in ends[1]), ',')))
        for c, Q in enumerate(ends):
            print('    %s end, %d blocks from its own end of the pool (bytes, block, site; free = unallocated):' % ('low' if c == 0 else 'high', len(Q)))
            for b in Q[:show]: print('      %18s %s' % (format(b[0], ','), ('#%d %s' % (b[2][0], b[2][1])) if b[1] is not None else 'free'))
            if len(Q) > show: print('      ... %d more' % (len(Q) - show))
    print('  after stage D: low end %s, high end %s; high-water mark of the pool over the trial %s bytes' % (format(P.P[0].end, ','), format(P.P[1].end, ','), format(P.high, ',')))
    return P.high


def main():
    global WORST_D, WC_MEM, LD_CFV
    m = (5 ** 11 - 1) // 2
    set_outer_limit(m)
    assert not any(LD_CONV.values())                           # this model's charges for every primitive (the other conventions are a comparison tool only)
    if LEAND: assert vd_active(m) and bool(NORMALD) != bool(AMORT), 'LEAND needs VDC and exactly one of NORMALD, AMORT'
    LD_CFV = LD_CF if LD_CF is not None else (m // CHUNK_D if CHUNK_D else None)     # the chunk bound of the scheme (c) products of the lean stage D
    def stages():
        global VD_SPLIT
        hgcd.cache_clear()
        I, A, B, sg, sF = stage_AB(m)
        pcs = isinstance(sg, tuple)
        VD_SPLIT = (2 if len(sg) == 2 else 4) if pcs else 0    # g and R in two pieces: the base of a coset is selected (a comparison and a branch) at every coset access of stage C (three pieces: two)
        C, cinfo = powx_lean(m, 3, PM1H, sg); C.ctl(STAGE_BK)
        VD_SPLIT = 0
        db = 3 + (len(sg) if pcs else 0)                       # live blocks at the entry of stage D: the twiddle table, g and R (two pieces each with the pieces; three with GCDONLY)
        D = Tr(db); D.ctl(STAGE_BK); D.ops += 1; D.ctl(11)
        twD = tw_new(D, TWD_A, TWD_HI) if TWMOVE else None      # stage D: the table of its transforms (3*2^23 points)
        t, (lg, sgg) = gcd_cost(m, 0, db, cinfo['sg2'], cinfo['sR2'] if vd_active(m) else sF)
        D.add(t); D.ctl(2)
        if twD is not None: D.free(twD)
        D.free(sgg)
        return C, cinfo, D, (I, A, B)
    WORST_D = False; WC_MEM = False
    Cn, cinfo, Dn, _ = stages()                                # the normal local charge of the half-gcd tree, no division beyond the quotient of two coefficients
    WORST_D = not NORMALD; WC_MEM = not NORMALD
    if LEAND: WORST_D = False; WC_MEM = bool(AMORT)            # the lean stage D: no per-node recurrence (NORMALD: the normal sequence with the quotient and return tests; AMORT: one fast division of length m, its arrays held)
    C, cinfo, D, (I, A, B) = stages()                          # the recurrence of 6.3: normal local charge + one full division at every node, summed over the tree (NORMALD: the normal sequence with the abort tests); every allocation walked
    print('m =', format(m, ','), '| truncated point sets: n1 =', format(VD['n1'], ','), 'of N =', format(VD_H, ','), '(TRC = %d of %d nodes) | squaring steps' % (TRC[0], 1 << TRC[1]), cinfo['steps'], 'of which with S:', cinfo['nset'])
    print('S_C =', format(C.ops, ','))
    print('S_D normal local charges of the tree =', format(Dn.ops, ','))
    if LEAND and NORMALD: print('S_D of the lean stage D on the normal remainder sequence, with the quotient and return tests =', format(D.ops, ','))
    elif LEAND: print('S_D of the lean stage D: the normal-sequence trace with the tests, one fast division of length m and the zero-scan allowance =', format(D.ops, ','))
    else: print('S_D with one full division at every node (and the outer loop, and the closing loop) =', format(D.ops, ','))
    print('S_D =', format(D.ops, ','))
    tws = twiddle_slots(m); twb = 0 if TWMOVE else blk(tws); g_b = blk(m + 1); F_b = blk(fslots(m))
    pA = twb + A.peak; pB = twb + g_b + B.peak
    pC = twb + g_b + F_b + C.peak; pD = twb + g_b + F_b + D.peak
    if vd_active(m):      # the live set at the entry of each stage is what the earlier stages left
        pB = twb + A.cur + B.peak; pC = twb + A.cur + B.cur + C.peak; pD = twb + A.cur + B.cur + C.cur + D.peak
    peaks = dict(A=pA, B=pB, C=pC, D=pD)
    for x in 'ABCD': print('peak of the live set, stage %s = %s bytes' % (x, format(peaks[x], ',')))
    # the allocator of section 4.2 on the sequence of allocations and frees of one trial (the second trial repeats it from the same state)
    stage_ev = [('init', I.ev), ('A', A.ev), ('B', B.ev), ('C', C.ev), ('D', D.ev)]
    walk = walk_check(stage_ev)                                # the events reproduce the walk: bytes in use, peak and live blocks of every stage
    for x, T_ in zip('ABCD', (A, B, C, D)): assert walk[x] == (T_.cur, T_.peak, T_.cnt, T_.pcnt), x
    pool = pool_account(stage_ev, BIG_EXP)
    print('two-ended pool: blocks of more than 2^%d bytes; largest sum of the two ends after each stage (bytes): %s; at most %d blocks; %s blocks examined in all'
          % (BIG_EXP, ', '.join('%s %s' % (k, format(v, ',')) for k, v in pool['big_stage'].items()), pool['big_blocks'], format(pool['scans'], ',')))
    print('slab classes (class: peak number of live blocks): %s; slab area = %s bytes' % (', '.join('%d: %d' % kv for kv in pool['slab_peaks'].items()), format(pool['slab'], ',')))
    arena = pool['arena']                                      # pool high-water + 128 + slab area + QE_BYTES, rounded up to 64
    mem = arena + IMAGE_EXTRA + STACK
    print('arena = %s bytes (two-ended pool %s + 128, slab classes %s, stages E and later %s), memory = %s bytes, log2 = %.3f'
          % (format(arena, ','), format(pool['big_high'], ','), format(pool['slab'], ','), format(QE_BYTES, ','), format(mem, ','), ceil3(math.log2(mem))))
    if GCDONLY:                                                # the cofactor-free in-place stage D: its exact count is S_D above; its allocation / free trace on the pool, event by event
        dhigh = stage_d_trace(stage_ev, BIG_EXP, os.environ.get('STAGE_D_TRACE'))
        assert dhigh == pool['big_stage']['D'] == pool['big_high'], (dhigh, pool['big_stage']['D'], pool['big_high'])
        assert D.ops == 1090374810264 and dhigh == 3421552640   # row: the stage-D count and the high-water mark of the pool
    assert C.ops == 1975202223424 and D.ops == 1090374810264
    assert peaks == dict(A=781713472, B=1721237696, C=3421552640, D=2334131392) and arena == 3422268416 and mem == 3427584396


if __name__ == '__main__':
    main()
```

Exit status 0. Output:

```
m = 24,414,062 | truncated point sets: n1 = 24,428,544 of N = 33,554,432 (TRC = 1491 of 2048 nodes) | squaring steps 231 of which with S: 45
S_C = 1,975,202,223,424
S_D normal local charges of the tree = 1,090,374,810,264
S_D of the lean stage D on the normal remainder sequence, with the quotient and return tests = 1,090,374,810,264
S_D = 1,090,374,810,264
peak of the live set, stage A = 781,713,472 bytes
peak of the live set, stage B = 1,721,237,696 bytes
peak of the live set, stage C = 3,421,552,640 bytes
peak of the live set, stage D = 2,334,131,392 bytes
two-ended pool: blocks of more than 2^14 bytes; largest sum of the two ends after each stage (bytes): init 0, A 781,713,472, B 1,721,237,696, C 3,421,552,640, D 3,421,552,640; at most 101 blocks; 49,025,801 blocks examined in all
slab classes (class: peak number of live blocks): 7: 15, 8: 2, 11: 8, 12: 12, 13: 25, 14: 26; slab area = 698,752 bytes
arena = 3,422,268,416 bytes (two-ended pool 3,421,552,640 + 128, slab classes 698,752, stages E and later 16,896), memory = 3,427,584,396 bytes, log2 = 31.675
stage D on the two-ended pool (blocks of more than 2^14 bytes): after init, A, B, C: low end 781,713,472, high end 781,713,472, live 1,563,426,944, largest sum so far 3,421,552,640
  stage D: 4,291,442 pool events (2,145,720 allocations, 2,145,722 frees) on 2,145,722 distinct blocks; the first 24:
  alloc #3              134,217,792 bytes pool L | live      1,697,644,736 | pool low        915,931,264 high        781,713,472 sum      1,697,644,736
  alloc #4                   24,640 bytes pool L | live      1,697,669,376 | pool low        915,955,904 high        781,713,472 sum      1,697,669,376
  alloc #5                   24,640 bytes pool L | live      1,697,694,016 | pool low        915,980,544 high        781,713,472 sum      1,697,694,016
  alloc #6                   16,448 bytes pool L | live      1,697,710,464 | pool low        915,996,992 high        781,713,472 sum      1,697,710,464
  alloc #7                   16,448 bytes pool L | live      1,697,726,912 | pool low        916,013,440 high        781,713,472 sum      1,697,726,912
  alloc #8                   16,448 bytes pool L | live      1,697,743,360 | pool low        916,029,888 high        781,713,472 sum      1,697,743,360
  alloc #9                   16,448 bytes pool L | live      1,697,759,808 | pool low        916,046,336 high        781,713,472 sum      1,697,759,808
  alloc #10                  16,448 bytes pool L | live      1,697,776,256 | pool low        916,062,784 high        781,713,472 sum      1,697,776,256
  alloc #11                  16,448 bytes pool L | live      1,697,792,704 | pool low        916,079,232 high        781,713,472 sum      1,697,792,704
  alloc #12                  16,448 bytes pool L | live      1,697,809,152 | pool low        916,095,680 high        781,713,472 sum      1,697,809,152
  free  #4                   24,640 bytes pool   | live      1,697,784,512 | pool low        916,095,680 high        781,713,472 sum      1,697,809,152
  free  #5                   24,640 bytes pool   | live      1,697,759,872 | pool low        916,095,680 high        781,713,472 sum      1,697,809,152
  free  #6                   16,448 bytes pool   | live      1,697,743,424 | pool low        916,095,680 high        781,713,472 sum      1,697,809,152
  free  #7                   16,448 bytes pool   | live      1,697,726,976 | pool low        916,095,680 high        781,713,472 sum      1,697,809,152
  free  #8                   16,448 bytes pool   | live      1,697,710,528 | pool low        916,095,680 high        781,713,472 sum      1,697,809,152
  free  #9                   16,448 bytes pool   | live      1,697,694,080 | pool low        916,095,680 high        781,713,472 sum      1,697,809,152
  free  #10                  16,448 bytes pool   | live      1,697,677,632 | pool low        916,095,680 high        781,713,472 sum      1,697,809,152
  free  #11                  16,448 bytes pool   | live      1,697,661,184 | pool low        916,095,680 high        781,713,472 sum      1,697,809,152
  free  #12                  16,448 bytes pool   | live      1,697,644,736 | pool low        915,931,264 high        781,713,472 sum      1,697,644,736
  alloc #13                  24,640 bytes pool H | live      1,697,669,376 | pool low        915,931,264 high        781,738,112 sum      1,697,669,376
  alloc #14                  24,640 bytes pool H | live      1,697,694,016 | pool low        915,931,264 high        781,762,752 sum      1,697,694,016
  alloc #15                  24,640 bytes pool H | live      1,697,718,656 | pool low        915,931,264 high        781,787,392 sum      1,697,718,656
  alloc #16                  24,640 bytes pool H | live      1,697,743,296 | pool low        915,931,264 high        781,812,032 sum      1,697,743,296
  alloc #17                  16,448 bytes pool L | live      1,697,759,744 | pool low        915,947,712 high        781,812,032 sum      1,697,759,744
  the 0 events that raise the high-water mark (the last 0 shown; event number first):
  after stage D: low end 0, high end 0; high-water mark of the pool over the trial 3,421,552,640 bytes
```
