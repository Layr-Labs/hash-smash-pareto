# Orchard Poseidon, r = 3: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, value-domain powering on truncated point sets, inversion-free half-gcd on three rows, one centre

## 1. Claim

Target: `poseidon-orchard-r3-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, three partial rounds 4, 5 and 6, full rounds 60-63, state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is an algorithm (sections 2-4) with an operation count that bounds every run (sections 6-7) and a success probability derived from two score-critical premises: `H-ONE` (section 9.1), a statement about the fraction of centres at which the fixed digest polynomial has between 1 and 16 usable roots, and `H-NORMAL` (section 9.5), a statement about the normality of the remainder sequence that enters only the success probability. Section 9.2 derives the success probability from them.

* The algorithm: draw a centre `c` from two fresh random words, `c = (w1 2^256 + w2) mod p` (within statistical distance `p/2^512` of uniform on `F_p`, 4.1.1), build the odd part `g_c` of the line polynomial by evaluation and one inverse transform, compute `R = S^((p-1)/2) mod g_c` in the value domain by Montgomery powering on two truncated point sets `O1`, `O2` of `n' = 477 * 2^11 = 976,896` points (477 of the 512 depth-9 nodes of the subgroup of order `2^20` and of its coset; the method of bradcush `b30de9bf`/`a41aecdd`, there 15 of 16 nodes, section 4.3T), take `G = gcd(g_c, R - 1)` by the inversion-free half-gcd on three rows of bradcush `4bcabff8` (outer step `k <= 2^16 - 1`, section 4.4), charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` in at most `Z = 64` rounds, take its square root, map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39009`: a lower bound for the probability, over the algorithm's fresh random words, that the centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1), `delta = 0.003` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `eps_iso <= 2.371e-15`, `eps_coin <= 65 p / 2^512 <= 1.404e-76`, `eps_g <= n' (D - 1) / p < 2^-213` (the centre makes `g_c` vanish at a point of `O1`, 4.3T) (sections 4.1.1, 4.3T, 9.2). The value the formula gives is `0.390099999999997628` (at or above the organizer floor 0.39); the claim is that value floored at five decimals.
* `time_log2 = 28.10590` in target-compression units (`C(3) = 279` primitive operations per unit): the operation count that bounds every run, derived in section 6 as `T_fixed + K * T_trial + T_off` with `K = 1`, stage C in the value domain on truncated point sets (4.3T), stage D the inversion-free half-gcd on three rows charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (4.4, 6.3; the time bound holds for every sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work), and stage E at its cap of `Z` rounds at degree `DMAX`. `N_max = 80,597,497,306` operations, `log2(N_max / 279) = 28.10589...`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is bounded by 1,000,000 operations; that bound is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 26.990` (`133,210,380` bytes, section 7). The normalized cost is `28.10590 + max(0, 26.990 - 20) = 28.10590 + 6.990 = 35.09590`.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; every random field element is drawn from two fresh words, at most `65` field elements (`130` words) per run (section 4.1.1), and a draw costs 63 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^9`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Prior entries: this entry replaces our filed r = 3 entry `95d8b186` (normalized cost 35.59204) by the same algorithm with three changes: (i) stage D is bradcush's inversion-free half-gcd on the rows `Y - 1`, `Y + 1`, `Y - i` (entry `4bcabff8`), ported and charged in this cost model (4.4), with the normal-sequence charging and the ABORT of bradcush `e6dcb600` as before, in place of the lean cofactor-free half-gcd with a memory cap; (ii) in stage C (4.2, 4.3T; the 18-word register file and the pass split of `95d8b186`) the twiddles of an 8-point block or radix-8 group are formed from the two-level root table in 11 operations, the twist and `1/N` scalings are running products fused into the adjacent pass, the batch inversion of `k1` works in the scratch buffer of the stage, and the table of the Newton and quotient products is sized to their transforms (`3*2^17` points); (iii) a line evaluation of stage B is charged at its counted field operations, `155 + 21 r = 218` (section 3), in place of one target-compression unit. `95d8b186` is the one-centre algorithm of our r = 6 entry `c318f442` with the stage C of bradcush `b30de9bf`/`a41aecdd`, the memory schedule of 0xshikhar `52120fad` (each stage builds and frees the twiddle table of its own transforms) and the premises `H-ONE` at `q = 0.3931` and `H-NORMAL` at `delta = 0.003` (the split of cryptogakusei's entry `4888e783`, organizer-run tests in the form of gta6rp's entry `bef31fdd`); it replaced our executed r = 3 entry `bb9cca58`. Ruling `867c60fd` refused the register-file premise `R-REG64` of our previous filing of this stack; it is withdrawn, and every transform here is charged on the 18-word register file. The memory is the allocator high-water mark of the one trial (section 7).
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1), a statement about the fraction of good centres; `H-NORMAL` (score-critical for the success probability only, section 9.5), bradcush's premise on the normality of the remainder sequence stated with the allowance `delta = 0.003` and supported by organizer-run tests. The costs are the declared cost model of this entry: the charging rules of section 4.2 with the register file of 18 words, the half-gcd of stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (Appendix E). Everything else is proved or counted here.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`. `(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`. The algorithm uses the line `j = 0`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant `M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS, nonzero on the deployed constants, checked). Let `(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, `d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i` (the supports are disjoint). After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6 (partial), 60, 61, 62, 63 (full) put nine S-box layers on top of an affine map, and the digest is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^9 = D = 1,953,125`. The leading coefficient is obtained by propagating leading coefficients through the nine layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used: `f_D(0) = 0x11f9cfdeecb8c5965318cbdc58480d2e6db510f12862658af639ce81578c3e23` (computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau` against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`), hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 976,562`, `g_c` has degree exactly `m` and leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`, `W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The useful roots are the roots in `F_p` with `S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p`; `S = 0` is not a root of `S^((p-1)/2) - 1`). `G` divides the squarefree `S^((p-1)/2) - 1`, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. `H = 1,572,864 = 3 * 2^19` divides `p - 1` (`p - 1 = 2^32 * 3 * q`) and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`; one inverse transform of size `H` returns the coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). The `2H = 3,145,728` evaluations of `F` are each charged at the field operations of a line evaluation, counted as the unit `C(r) = 216 + 21 r` is counted (a round: 3 additions of its constants, S-boxes at 3 operations, the MDS at 9 multiplications and 6 additions): the affine start `alpha + beta W` (6; the round-2 constants are inside `alpha`), round 2 (24), round 3 (27), the `r` partial rounds (21 each), rounds 60-62 (27 each) and round 63 with row 0 of the last MDS only (3 + 9 + 5 = 17), `155 + 21 r = 218` operations at `r = 3` against `C(3) = 279` for a full permutation. The loop work (two point additions, one subtraction, one multiplication by `1/(2 zeta^i)`, the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, the store with its address, the loop control and the bit-reversed index) is charged on top (stage B, section 6), with the twiddle table of the transform, built by stage B (4.2).

## 4. The algorithm (one centre, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   constants (once; no twiddle table: each stage builds the table of its own transforms, 4.2)
setup:  the line (line_setup) (once)
for t = 1, ..., K (K = 1):            [the test t <= K is made at the start of the trial; no exit except success]
  A  c := (w1 * 2^256 + w2) mod p from two fresh random words w1, w2 (4.1.1)
  B  g := monic g_c, by section 3 (3,145,728 evaluations + one inverse NTT of size 1,572,864 + the nonzero-leading-coefficient test + normalisation)
  C  R := S^((p-1)/2) mod g, in the value domain on the truncated point sets O1, O2 of n' = 976,896 points (section 4.3T): 236 squaring steps, 45 of them also multiplying by S
  D  G := gcd(g, R - 1) (monic): the inversion-free half-gcd on three rows (section 4.4), charged for the normal remainder sequence with the quotient and return tests; on any other case ABORT (6.3)
  E  if deg G = 0 or deg G > DMAX: trial ends. Otherwise isolate a root S of G (4.1.2); if none within Z = 64 rounds: trial ends.
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (279 operations each) are equal and the pairs differ -> output; otherwise the trial ends
```

4.1.1 Coins (ruling `04c0dd43`, finding F-EVAL-001). The only randomness is the cost-model random-word primitive. Every random field element of the algorithm (the centre `c` of stage A and each shift of stage E) is drawn from two fresh 256-bit words `w1, w2`: each is reduced mod `p` by three conditional subtractions (exact, `2^256 < 4p`), and `x = (w1 mod p) * (2^256 mod p) + (w2 mod p)` in `F_p`, i.e. `x = (w1 2^256 + w2) mod p` with `w1 2^256 + w2` uniform on `[0, 2^512)`. There is no rejection and no retry. A draw is 63 operations: per word 1 random-word operation, 1 load, 1 store, 3 control, the reduction 9 and its loop control 11 (26 per word, 52), two Montgomery conversions 2, the load of the constant `2^256 mod p` 1, one multiplication 1, one addition 1, entry 2, the two addresses 4. At most `1 + Z = 65` draws (`130` words) per run. With `2^512 = Q p + r`, each residue has `Q` or `Q + 1` preimages, so one draw is within statistical distance `r (p - r) / (p 2^512) <= p / 2^512 = 2^-258.0` of uniform on `F_p`; the 65 draws are independent, so the joint distribution of all the coins of a run is within `eps_coin = 65 p / 2^512 <= 1.404e-76` of the distribution with every draw exactly uniform (total variation is subadditive over independent components).

4.1.2 Stage E: isolating a root of `G`. With `1 <= deg G <= DMAX = 16`, a Cantor-Zassenhaus split with random shifts isolates one linear factor in at most `Z = 64` rounds at degree `<= 16`; `eps_iso <= 2.371e-15` bounds the probability that 64 rounds fail to isolate a root when `deg G >= 1` (section 9.4).

### 4.2 Machine model and charging rules (summary; `C(3) = 279`)

Every field operation, load, store, control operation and random word is one primitive operation; `C(r) = 216 + 21 r = 279` primitive operations is one target-compression unit. The register file is 18 words of 256 bits per transform block, the only register assumption; the algorithm runs on one thread, no dispatch. Allocation: one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes. A block of more than `2^10` bytes is served by the two-ended pool (one region, two ends, first-fit in address order, the statements marked `# pool:H` using the high end and, with the depth-parity placement of section 7, the end `(j + bit8) mod 2` of a half-gcd node at depth `j`); every smaller block by its slab class (the least `j >= 7` with `2^j >= need`, a slot of `2^j` bytes). The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows (a pool request `97` operations besides the walk and `13` per block examined, a slab request at most `126`, a free `81` for a slab block and at most `105` for a pool block). The memory of both allocators is the arena of section 7. Twiddle tables: none is built in init; stage B, the Newton and quotient products of stage C and stage D each build the table of their own largest transform (`2^(a-1)` entries for `3*2^a` points: its root, 5 operations per entry and the loop) and free it at the end of that work, charged in the stage's row; the passes of 4.3T use two-level root tables of `4 x 4,096` words, built in stage C and kept for the applies of stage D on `O1`, which frees them; the table of stage D serves its transforms of `2^19` and `3*2^18` points.

### 4.3T Stage C in the value domain on truncated point sets (the method of bradcush `b30de9bf`/`a41aecdd`, 477 of 512 nodes)

Point sets. `N = 2^20` divides `p - 1` (2-adicity 32). Let `psi` have order `2^21`, `H_N = <psi^2>` and `Y = X^(2^11)`. `H_N` is the union of the 512 depth-9 nodes `{x : x^(2^11) = r_j}`, `r_j` the 512-th roots of unity in transform (bit-reversed) order; `O1` is the union of the first 477 nodes, `n' = 477 * 2^11 = 976,896 >= m + 1 = 976,563` points, and `O2` the same 477 nodes of the coset `psi H_N` (`x^(2^11) = r'_j`, `r'_j^512 = -1`), disjoint from `O1`. `P1 = prod_{j<477} (Y - r_j)` has degree `n'`, vanishes on `O1` and is the nonzero constant `P1(r'_j)` on node `j` of `O2`; `delta_j = 1/P1(r'_j)` (477 table constants).

Truncated transforms (bradcush `b30de9bf` 4.3, generalized as the truncated Fourier transform of van der Hoeven, ISSAC 2004). A polynomial of degree `< n'` is `sum_{k<512} P_k Y^k` with `deg P_k < 2^11` and `P_k = 0` for `k >= 477`; its values on the 477 nodes determine it and are determined by it (the CRT for the 477 coprime moduli `Y - r_j`, whose product `P1` has degree `n'`). The forward transform runs the top 3 layers on all `N/8` offsets (no truncation saving is charged), the middle layers only on the blocks above present nodes, and the bottom 3 layers on the `n'` points. The inverse runs the same layers in reverse and recovers the residues of the dropped part `[477, 512)`, the maximal subtrees `{477}`, `{478..479}`, `{480..511}` (depths 9, 8, 4), from the known zero chunks `P_k = 0` along their paths to the root, as bradcush recovers the one dropped leaf; this is charged 10 operations (3 multiplications, 3 additions, a load and a store) per point of a dropped subtree per layer of its path. The passes are fused as in `b30de9bf` 4.5 under the 18-word register file, the 20 layers split 3 | 4, 4, 3, 3 | 3: a bottom pass (8-point blocks: forward layers, the pointwise map, inverse layers; one twiddle set for both directions, its 7 twiddles from the two-level root table: two loads, 1 multiplication, 2 squarings and 4 multiplications by the register constants `i`, `zeta_8`, 11 per block; `V^T V = 8 diag(1, cJ)` with `c = y^8` of the block, so every inverse bottom pass scales each 8-point block by `diag(1, c^-1 J)`: 7 multiplications and the load of `c^-1`, 9 operations per block), middle passes of radix 16 then 8 (radix 16, 16 data words: its 15 twiddles loaded per block, 195 per block and 5 per group; radix 8: 73 per block, the 7 group twiddles formed as in the bottom pass and held in registers, 16 per group), and a top pass that fuses the inverse top of one set with the forward top of the other.

Montgomery powering (`b30de9bf` 4.5). For residues of degree `< n'`, `Mont(A, B) = (A B + u g)/P1` with `u = -A B / g mod P1` (`deg u < n'`); the division by `P1` is exact, `Mont(A, B) = A B / P1 mod g`, and `deg Mont(A, A) <= n' - 2`, so `X Mont(A, A)` has degree `< n'`. A residue `A` (representing `S^e P1`) is held by its values on `O1` and on `O2`, each up to a tracked scalar. One step: `U = A^2 k1` on `O1` (`k1 = -1/(N^3 g)` there; `u` is determined by its values on `O1`); `U` to `O2` (truncated inverse on `O1`, truncated forward on `O2`); `B2 = (A2^2 + U g) delta_j` on node `j` of `O2`, which is `Mont(A, A)` up to the tracked scalar because `P1 = 1/delta_j` there, times the point `x` when the exponent bit is 1; `B2` to `O1` (truncated inverse on `O2`, truncated forward on `O1`). No `1/N` is executed inside the steps (the scalars are tracked, 2 operations per step). Per point and step: on `O1` `sqr, LD k1, mul` (4); on `O2` `LD A2, sqr, LD g, mul, add`, the multiplication by `delta_j`, `ST` (10) and the load of `delta_j` per block (2); 3 more for a 1-bit (the load of the point and a multiplication).

Entry and exit. `g` (coefficients from stage B, its slots above `m` zeroed) goes to `O1` and `O2` (a truncated forward each, the scaling a running product fused into its first pass, 2 operations per point). The start residue is `A0 = X^v P1 mod g`, `v = 2^17 = 131,072` (VSHIFT = 2): `q = floor(X^v P1 / g)` has `ell = v + n' - m + 1 = 131,407` coefficients and is formed from the Newton reciprocal of the reversed `g` and one product (transforms of up to `3*2^17` points, with their own twiddle table, freed after the quotient); on node `j` of `O2`, `x^v P1(x) = r'_j^64 P1(r'_j)` is a constant, so `A0 = x^v P1 - q g` there is one truncated forward of `q` and one pointwise pass (8 per point); then `A0` goes to `O1`. `k1` is formed by chunked batch inversion on `O1` (chunks of `2^16` points: prefix products, held in the scratch buffer of the stage, one inversion, two multiplications per point); each chunk product is tested for zero before its inversion (2 per chunk), and a zero ends the trial: for fixed `x != 0`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g_c vanishes on O1) <= n' (D - 1) / p = eps_g < 2^-213` (9.2). The exit is one step with multiplier 1 (`Mont(A, 1)`) and two truncated inverses with their scaling, which return `kappa R` (`kappa` the tracked scalar) and `g` in coefficient form; the gcd is scale-invariant, so stage D receives `kappa R - kappa`. There are `236` squaring steps, `45` of them also multiplying by `S`.

Exactness and memory. Every map above is exact (Montgomery products of polynomials of degree `< n'`, held bijectively by their values on 477 nodes); no premise is added to stage C. The live set of the stage is four arrays of `n'` words (`g` on `O2`, `A` on `O2`, `A` on `O1`, `k1` on `O1`), the tables (`507 + 16,384` words: 30 constants, the 477 `delta_j`, the two-level root tables), one scratch buffer of `N - n' = 71,680` words (zero-filled once) that extends the array being transformed to all `N` positions, which the top pass (all `N/8` offsets), the middle passes (`2^20` positions in the first) and the stores of the recovered dropped subtrees use (one transform runs at a time, so the in-place schedule needs no other storage), and which holds the prefix products of one batch-inversion chunk (`2^16 <= 71,680` words) and, while `q` is formed, the Newton arrays. The step-by-step count is expanded in Appendix E (`powx_tr`, `tr_step`) and totals **row C = 61,516,769,663** (section 6).

### 4.4 Stage D: the inversion-free half-gcd on three rows (bradcush `4bcabff8`)

`G = gcd(g, R - 1)` is computed by bradcush's inversion-free half-gcd (entry `4bcabff8`, read as text only; ported and charged in this cost model). Matrices and remainders are kept up to scalars with pseudo-division (`b^2 a = Q b + e`, `Q` of degree 1 on the normal sequence), so no field inversion runs inside the recursion. A node of budget `k = 2^j - 1` makes two child calls of budget `2^(j-1) - 1`; its products run on `3 * 2^(j-1)` points, the rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), each a power-of-two transform of `n` points after a twist, joined by a 3-row CRT: `(c, d) = adj(M1)(a, b)` on the top window, the pseudo-division, and `M = M1 [[Q, 1], [b^2, 0]] M2`; the row `Y - 1` values of each child's matrix are returned by the child, and the row values of `M1` are kept from the apply and reused in the product. The base case (budget 63) runs two remainder steps per pass over its window (the second reads the first remainder from registers). The driver calls `hgcd(a, b, k)` on the top window with `k = 2^j - 1 <= 2^16 - 1` the largest with `2k + 1 <= deg a`, applies the returned matrix to the whole pair in place by the cheapest of three transforms (the truncated set `O1` of 4.3T with its root tables, `2^a` or `3 * 2^a` points; the matrix entries row-wise in rows of `2^16` when the transform has at least `2^17` points), and repeats; below degree `2 * 63 + 1` classical division steps finish and `G` is normalised. Every working array of the half-gcd lives in one bump arena (an allocation or release is 10 operations) of `1,048,320` words, the peak of the recursion and of the applies.

Charges (Appendix E, `pd_*`): field operation 1, load or store 2, loop control `3 n + 2`, the passes of section 4.2 for the row transforms, the truncated transforms of 4.3T for an apply on `O1`; the twist of a row and the `1/n` of an inverse are running products fused into the adjacent loop (2 operations per point, 1 for `1/n` alone). Appendix E prints the outer steps with their budgets, charges and apply plans: 28 outer steps (13 at `k = 65,535`) and the classical tail from degree 206. On the normal sequence every length, budget and allocation is a function of `m` alone.

The row is charged for the normal remainder sequence (every quotient of degree 1), the case of the premise `H-NORMAL` (9.5): every division tests that its quotient has degree 1 and every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter (2 operations each), and a zero remainder met inside `hgcd` or in the classical tail also ends the trial; on any other case the trial ABORTs (section 6.3). By the prefix lemma of 6.3 every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, so the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The total is **row D = 17,835,006,021** (section 6.3, 6).

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G | g_c`, whose roots `S` are nonzero squares with `g_c(S) = 0` and `S^((p-1)/2) = 1` (section 3); `s = sqrt(S) != 0`, so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Ledger: operation count (primitive operations; `C(3) = 279`)

| row | what is charged | operations |
| --- | --- | --- |
| init | constants and bookkeeping (once; no twiddle table, 4.2) | 17,987 |
| setup | the line (`line_setup`, once) | 4,910 |
| A (per trial) | stage bookkeeping, loop test and update, the coin draw (63, two words), one allocation | 1,228 |
| B (per trial) | `3,145,728` evaluations of `F` at `155 + 21 r = 218` counted operations each (section 3), the loop work, the twiddle table and the inverse transform of size `1,572,864`, the normalisation | 1,075,093,735 |
| C (per trial) | `S^((p-1)/2) mod g` in the value domain on the truncated point sets `O1`, `O2` (477 of 512 nodes, `n' = 976,896`), VSHIFT = 2, 236 squaring steps, passes 3 | 4, 4, 3, 3 | 3 (section 4.3T); expanded in Appendix E | 61,516,769,663 |
| D (per trial) | inversion-free half-gcd of `(g, R - 1)` on three rows, charged for the normal remainder sequence with the quotient and return tests (sections 4.4, 6.3); expanded in Appendix E | 17,835,006,021 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16`, each with one draw of 63 (two words) | 166,081,821 |
| F (per trial) | square root, back-map | 47,012 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 279 + 32` | 6,612 |
| trial-loop (per trial) | trial-loop bookkeeping (12) and the allocator reset after an ABORT (1,000), charged in every trial | 1,012 |
| plan_invN misses | one per distinct plan size | 77,225 |
| output rows | the fixed output rows (stages H and I) | 3,390,080 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + 1 * T_trial + T_off` | **80,597,497,306** |

`T_off = 1,000,000`; `T_trial = A + B + C + D + E + F + G + trial-loop = 80,593,007,104`; `T_fixed = init + setup + plan_invN misses + output rows = 3,490,202`; `K = 1`, so `N_max = 3,490,202 + 80,593,007,104 + 1,000,000 = 80,597,497,306`. `log2(N_max / 279) = 28.10589...`, rounded up at five decimals to `28.10590`. Rows C and D are not asserted by hand: Appendix E (`stage_cd_r3.py`) expands them from the dimensions of 4.3T and the half-gcd levels with the kernel charges of 4.2 and prints and asserts the two values `61,516,769,663` and `17,835,006,021`.

### 6.1 Validation
The kernel charges and the allocator rules are those compared with the instrumented totals of our executed runs at `r = 3, 4, 5` (the arena rule within 64 bytes of the measured heap peaks there); the truncated-set stage C (4.3T) and the stage D of 4.4 have no executed counterpart, and their counts are the formulas of Appendix E.

### 6.2 Offline derivation
The literals of the sources (Montgomery forms of the organizer constants, `5^q`, `2^65`, the exponent `(4(p-1)+1)/5`) are derived offline in at most `1,000,000` operations, declared `preprocessing_log2 = 20` and inside `N_max`.

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry `e6dcb600`)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g_c, R_c - 1)`: every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the pseudo-division of a node, each step of the base case and of the classical tail) tests, before it does any work beyond reading the two leading coefficients, that its quotient has degree 1 (2 operations); (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); a zero remainder inside `hgcd` or in the classical tail also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state at the start of the trial (`1,000` operations, charged in every trial). Lemma (prefix; `e6dcb600`, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each node calls its children with budget `2^(j-1) - 1` and, with every quotient of degree 1, every degree in the tree is fixed by `m` and the number of quotients so far, and the budgets of the outer loop (`k` the largest `2^j - 1 <= 2^16 - 1` with `2k + 1 <= n`, section 4.4) are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's `hgcd` calls produce has degree above the classical tail, so every gcd of degree at most `DMAX = 16` first appears in the classical tail (from degree 206); a zero remainder earlier ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The charging follows `e6dcb600` and the half-gcd follows `4bcabff8`, both read as text only (no entry script was run, compiled or imported). Appendix E (`stage_cd_r3.py`) prints, for `r = 3`, the charge of stage D for the normal sequence with the tests, `17,835,006,021`, and asserts it.

The `r = 3` trial (`~133 MB`, `~8.1e10` operations) exceeds the organizer sandbox (128 MiB, 20 s), so the costs are the exact formula counts of sections 6 and 7; zero-fill clearing is charged (ruling `3476cad8`) and the register file is 18 words (4.2).

## 7. Memory: the arena of one trial

The arena is the capacity of the allocator of 4.2 on the allocation/free sequence of the trial. Appendix E runs the allocator on every allocation and free of the trial in the order of the program and reports the two-ended-pool high-water mark (the largest sum of the extents of the two ends over the trial), the slab area and the peaks of the live set per stage. The two-ended pool takes the blocks of more than `2^10` bytes. Its high-water mark is reached in stage C: `127,877,376` bytes (the four arrays of `n'` words of 4.3T, the scratch of `N - n' = 71,680` words, which also holds the prefix products of one batch-inversion chunk, and the tables), plus 128 bytes so the unused middle is always at least 128 bytes. Stage D holds `g`, `R`, the root tables of stage C, its twiddle table (`2^18` words) and the bump arena of the half-gcd (`1,048,320` words, 4.4); under the H-NORMAL ABORT these are the normal-case arrays, and a trial with any other sequence ends after a prefix of these allocations (6.3), so the normal-case walk bounds every trial. The stage-D live peak is `104,997,056` bytes, below the stage-C peak. No block of `2^10` bytes or less is live in stages A to D (slab area 0). Stages E and later hold at most 16 small arrays and the free-list heads: `16,896` bytes. The arena is `127,894,400` bytes (two-ended pool `127,877,376 + 128`, stages E and later `16,896`). Peaks of the live set per stage (bytes): A `31,260,736`; B `89,981,120`; C `127,877,376`; D `104,997,056`. With `5,250,444` bytes of code and static data and a `65,536`-byte stack, the footprint is `133,210,380` bytes `= 2^26.990`, rounded up at three decimals. No stored advice; each twiddle table is built at run time by the stage that uses it and charged in that stage's row (4.2).

## 8. Review points, answered by location

1. Row D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (6.3): by the prefix lemma every trial executes a prefix of the normal-case work, so the time and memory bounds hold for every sequence; `H-NORMAL` (9.5) enters only the success probability.
2. Stage D (4.4) is printed outer step by outer step by Appendix E (budget, half-gcd charge, apply charge and plan); its bump arena (`1,048,320` words) is a block of the allocation walk, and its live peak (`104,997,056` bytes) is below the stage-C peak, the high-water mark of the trial.
3. Row B reproducible from sections 3 and 6 (evaluations * 218 counted operations + the loop work, the twiddle table and the inverse transform + normalisation). The 18-word register file (4.2) is the only register assumption; every value beyond it is charged as a load or store.
4. The 1,000,000-op offline figure is a declared bound (`preprocessing_log2 = 20`), score effect < 4e-7 bit.
5. The mem penalty uses the rounded-up `mem_log2`, a self-penalizing over-charge.
6. `success = q - delta - eps_coin - eps_iso - eps_g >= 0.39` from the premises `H-ONE` and `H-NORMAL` (9.2, 9.5) with `K = 1`, `q = 0.3931`, `delta = 0.003`; the value is `0.390099999999997628`. The `H-ONE` allowance below the law value is stated exactly (`0.3934693 - 0.3931 = 0.0003693`; `q <= 151/384 = 0.3932292`, the four-moment Bonferroni bound, 9.1), and `delta = 0.003` is the declared premise; the 3,072 organizer-seeded sequences are reproducible observations consistent with it (10.5.1).
7. The organizer-checkable output is the returned witness-pair count; the premises hold under trusted execution of the submitted program, disclosed, not claimed as an organizer-verified proof.

## 9. The premise and the success bound

### 9.1 H-ONE
The number of centres `c` with `1 <= k(c) <= 16` is at least `q p = 0.3931 p`, `k(c)` the number of nonzero squares `S` with `g_c(S) = 0` (`= deg G`). The premise states `q = 0.3931`, the law value `1 - e^(-1/2) = 0.3934693` (9.3) less the extrapolation allowance stated exactly as `0.0003693`; it is also `0.0001292` below the four-moment Bonferroni bound `151/384 = 0.3932292`. The split of the allowance between `H-ONE` and `H-NORMAL` follows cryptogakusei's entry `4888e783`: with `delta = 0.003` (9.5) the bound of 9.2 needs `P(E_c) >= 0.3931` at `K = 1`. The extrapolation, the monodromy theorem at N = 2, 3 and the toy-field and organizer-run evidence are in the claim.json heuristic `H-ONE` and sections 10.3, 10.5.1.

### 9.2 The success bound
The centre is a fresh draw. For a centre `c` let `E_c` be the event `1 <= k(c) <= DMAX` (H-ONE, `P(E_c) >= q = 0.3931`) and `N_c` the event that the remainder sequence of `(g_c, R_c - 1)` is normal down to its gcd (H-NORMAL, 9.5, `P(not N_c) <= delta = 0.003`). The value-domain stage C reproduces `R = S^((p-1)/2) mod g` exactly (Montgomery products on the truncated point sets, 4.3T) and adds no premise; it needs `g_c` nonzero on `O1`, which fails with probability at most `eps_g = n' (D - 1) / p < 2^-213` over the centre (4.3T). If `E_c` and `N_c` hold and `g_c` has no zero on `O1`, stages C and D run to their end and return `G = gcd(g_c, R_c - 1)`; a successful isolation then ends in a verified collision. For `c` uniform `P(E_c and N_c) >= q - delta`, so with one centre (the event `g_c` zero on `O1` subtracted as `eps_g`)

`success = 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g`, `K = 1`.

Transfer to the written sampler (F-EVAL-001): `q - delta - eps_iso - eps_g` bounds the success probability of the run whose draws are exactly uniform on `F_p` (the premises and the isolation lemma are stated for uniform draws). The success of a run is an event of the vector of its draws, and the actual draws of 4.1.1 are within total variation `eps_coin` of the uniform vector, so the actual success probability is at least the ideal one minus `eps_coin`.

With `q = 0.3931`, `delta = 0.003`, `eps_iso <= 2.371e-15`, `eps_coin <= 1.404e-76`, `eps_g < 2^-213`: `q - delta = 0.3901`, and the value is `0.390099999999997628 >= 0.39`. The bound stays at or above `0.39` for every `delta <= 0.0030999` at `q = 0.3931`. The probability is over the random words of 4.1.1 for the fixed target, not over targets and not a sampled frequency.

### 9.3 Monodromy (support for H-ONE)
The roots of `G(c,t) = g_c(t^2)` come in pairs `+-t_i`, so the monodromy lies in the hyperoctahedral group `B_m` and `k(c)` counts positive Frobenius fixed points; for `B_m` this is Poisson(1/2) in the limit, `P(k >= 1) = 1 - e^(-1/2) = 0.3934693`, and Bonferroni at order 4 gives `P >= 151/384 = 0.3932292`. A theorem at two and three layers (Aubry-Perret, monodromy `B_12`, `B_62`); false for permutation polynomials, for decomposable `F` with imprimitive monodromy, and at one layer.

### 9.4 Isolation lemma
With `1 <= deg G <= 16`, a random-shift split isolates a linear factor within `Z = 64` rounds except with probability `eps_iso <= 2.371e-15`. Finite derivation: `G` divides both `g_c` and `S^((p-1)/2) - 1`, so it is squarefree and splits into `d = deg G <= 16` distinct linear factors `X - t_i` over `F_p`. A round with shift `a` keeps a nontrivial part of the current factor `H` under `gcd(H, (X + a)^((p-1)/2) - 1)` (or `X + a` itself when `a = -t_i`), so two roots `t_i != t_j` stay together only if `chi(t_i + a) = chi(t_j + a)` or `a` is in `{-t_i, -t_j}`. Since `sum_a chi((a + t_i)(a + t_j)) = -1` for `t_i != t_j`, exactly `(p - 3)/2` shifts give equal nonzero characters, so for `a` uniform on `F_p` the pair stays together with probability at most `((p - 3)/2 + 2)/p = 1/2 + 1/(2p)`; each shift is a fresh random word reduced mod `p`, within statistical distance `2^-128` of uniform (4.1.1), so per round the bound is `1/2 + 2^-127`, independently across rounds. The parts are nested, so the factor kept after 64 rounds holds two roots only if one of the at most `C(16,2) = 120` pairs was never separated in 64 rounds. By the union bound `eps_iso <= 120 (1/2 + 2^-127)^64 < 6.6e-18 <= 2.371e-15`; the looser stated value `2.371e-15` is kept, so every other number is unchanged.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries `e6dcb600` and `1aa56884`; allowance split of cryptogakusei's `4888e783`; organizer-run tests in the form of gta6rp's `bef31fdd`)
**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(g_c, R_c - 1)`, where `g_c` is the monic odd part of section 3 (degree `m = 976,562`) and `R_c = S^((p-1)/2) mod g_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.003` (`2^-8.38`). Stage D is charged for the normal sequence; every division tests its quotient degree and every call of the half-gcd its return, and on any other case the trial ends (ABORT, sections 4.4, 6.3). The premise enters only the success probability (9.2): the time and memory bounds hold for every remainder sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work (6.3). For a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes, each a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-213`; the premise extrapolates a much weaker form of this random-pair behaviour (`delta = 0.003`) to the structured pair `(g_c, R_c - 1)`. Measured support is organizer-run (10.5.1): the six experiments `euclid-normal-n2-t256-l2-a` to `-f` compute the complete Euclidean sequence of `(g_c, R_c - 1)` for this construction on the truncation `F_2` (`m = 12`) for 256 organizer-seeded trials of two centres each (3,072 sequences in all) and return a witness pair exactly when both sequences of a trial are normal; `euclid-normal-n3-t24` and `euclid-normal-n4-t2` do the same at `m = 62, 312`. The prediction is that every computed sequence is normal. Zero abnormal in the 3,072 sequences is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (`delta = 0.003` is the declared premise). Not verified at `r = 3`, which would need the computation itself; the organizer-run tests are at `m = 12` to `312`, far below `m`.

## 10. Experiments

Program `experiments/exp_euclid.py` (euclid-normal, one-centre) and `experiments/exp_line.py` / `experiments/exp_lowbits.py` (line-ladder and lowbits-birthday), with `experiments/manifest.json`.

10.3 The truncations. `F_N(c + X)` is coordinate 0 after the first `N` S-box layers on the line `j = 0`; `F_2`, `F_3`, `F_4` have odd parts of degree `m = 12, 62, 312`. The arithmetic monodromy at `N = 2, 3` is `B_12`, `B_62` (Grok jobs 136, 137, re-run on the deployed constants).

10.5.1 Organizer-run set. euclid-normal-n2-t256-l2-a to -f compute the complete Euclidean sequence of `(g_c, R_c - 1)` for this construction at depth `N = 2` (`m = 12`), each for 256 organizer-seeded trials of two centres (512 sequences per entry, 3,072 in all; the final letter only changes the organizer seeds); euclid-normal-n2-t256, -n3-t24 and -n4-t2 compute one sequence per trial at `m = 12, 62, 312`. A trial returns a witness pair exactly when its sequences are normal; the prediction (H-NORMAL, 9.5) is that every trial returns a pair, so the abnormal count is zero, a reproducible observation consistent with the premise. We do not treat the organizer-seeded centres as independent unselected samples and draw no population bound from these runs: `delta = 0.003` is the declared premise (9.5), carried by its stated support, not by an interval computed from the experiments. one-centre-n2-t256 and one-centre-n3-t24 run one trial of the algorithm at depth `N = 2, 3` per organizer seed and return a witness pair exactly when the sequence is normal, `1 <= k(c) <= 16` and the isolated root gives a verified collision of `F_N`, with expected count about 0.393469 T under H-ONE (9.1), reported as an observation with no interval inferred. line-ladder-w6/-w8/-w10/-w12 and lowbits-birthday corroborate the antipodal structure (random-function model), not the score-critical basis. Our runs of the six -l2 entries with local seeds in the organizer's container settings (1 CPU, 128 MiB, no network; 6.96 to 8.35 s each, every replay byte-identical): 3,072 sequences, all normal, every returned pair checked; the gcd had positive degree for 1,229 of the 3,072 centres (0.400). The organizer-checkable output is the returned witness-pair count; the premises H-ONE and H-NORMAL hold under trusted execution of the submitted program.

## Appendix E: the stage C and stage D totals and the arena of one trial (`stage_cd_r3.py`)

The standalone program `stage_cd_r3.py` below expands stages C and D of one trial at `r = 3` from the dimensions of 4.3T and the half-gcd levels with the kernel charges of 4.2, runs the allocator of 4.2 on the allocation/free walk of the trial, and recomputes and asserts the stage totals, the live-set peaks and the two-ended-pool high-water mark. Stage C is `powx_tr` (the truncated point sets of 4.3T, `TRC = (477, 9)`, `VD_H = 2^20`, `VSHIFT = 2`; one step is `tr_step`, passes 3 | 4, 4, 3, 3 | 3, `tr_mid`). Stage D is `stage_d` (the inversion-free half-gcd on three rows of section 4.4, `pd_*`), charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (6.3); H-NORMAL (section 9.5) enters only the success bound, not the time or the memory. The twiddle tables are built and freed by the stages that use them (`TWMOVE = 1`, 4.2). The program is self-contained and runs standalone (ruling `ea6f3fc9` requires the recompute script and its output in the package); its asserts fix `S_C = 61,516,769,663`, `S_D = 17,835,006,021`, the pool high-water `127,877,376` (reached in stage C) and the arena `127,894,400`. The full source follows, then its exit-0 output (every number of sections 6 and 7 is read from it).

```python
#!/usr/bin/env python3
"""Appendix E: stage C and stage D of one trial at r = 3, expanded into their totals (standard library only).
Run:  python3 stage_cd_r3.py      prints S_C = 61,516,769,663 and S_D = 17,835,006,021 and asserts them.

The inputs are the dimensions m = (5^9 - 1)/2 = 976,562 (degree of the modulus), the exponent (p-1)/2, and the charging rules of section 4.2,
which fix the per-kernel charges in the tables PASS and K3 below (butterfly 3 field operations or 2 when the twiddle is 1, twiddle load with
address, 8 operations per radix-3 leaf, loop control 3 per iteration and 2 on exit). Everything else is a finite recurrence:
  stage C: in the value domain on the truncated point sets O1, O2 of n' = 477 * 2^11 = 976,896 points (proof 4.3T; TRC = (477, 9), h = 2^20); the exponent: 236 squaring
           steps, 45 of them with the multiplication by S; each step = the passes of tr_step (bottom, middle, fused top, recoveries of the dropped subtrees) + the pointwise loops;
  stage D: the normal-sequence half-gcd of proof 4.4 (pd_*): the driver takes hgcd(k), k = 2^j - 1 <= 65535, on the top window, then applies the matrix to the
           whole pair in place; a node of budget 2^j - 1 = two child calls, the apply of the first matrix on the rows Y - 1, Y + 1, Y - i (3 * 2^(j-1) points, 3-row CRT),
           one pseudo-division, the matrix product on the same rows; base case 2^6 - 1 (two remainder steps per pass); the tail below degree 2 * 63 + 1 by classical steps.
`Tr` accumulates the operations and walks every allocation and free (an allocation is charged 121 + 13 (2 live + 1), a free 105; a block is 64 + 32 * slots rounded up to 64 bytes,
header included), with the live bytes and their peak, and the peak of the temporary arrays inside one call (the quotient and working arrays of every division, the workspaces of the
outer-transform scheme of the block products); it also records the events of the walk: every allocation and free with the identity of its block (the arrays given to a call by name).
The charge of stage D is the normal remainder sequence of proof.md 4.4 and 6.3: every division tests that its quotient has degree 1 and every call of hgcd that
it returns its parameter (or a zero remainder), and any other case ends the trial (ABORT). Its working arrays live in one bump arena: the peak words of the recursion (pd_node_mem) and of the applies (pd_run).
Twiddle tables (TWMOVE = 1): no table is built in init; stage B, stage C and stage D each build the table of their own transforms and free it (tw_new, charged by tw_ops);
the two-level root tables of stage C (sTab) stay live into stage D, whose apply on the truncated set O1 uses them.
Register file: 18 words (proof 4.2): the transforms of stage C run the passes top 3 | middle 4, 4, 3, 3 | bottom 3 (tr_mid; radix 16 loads its 15 twiddles per block: 195 per block, 5 per group).
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


BIG_EXP = 10                           # a block (header included) of more than 2^BIG_EXP bytes is served by the two-ended pool, every other block by its slab class (proof 4.2); a constant of the algorithm for each r
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
        self.ops += 1 + 120 + 13 * (2 * (self.base + self.cnt) + 1)
        b = blk(slots); self.cur += b; self.cnt += 1
        self.peak = max(self.peak, self.cur); self.pcnt = max(self.pcnt, self.cnt)
        i = new_id(); self.ev.append(('A', i, int(slots), _site(2), _who()) if LD_WHO else ('A', i, int(slots), _site(2)))
        return Slot(slots, i)

    def free(self, slots):
        self.ops += FREE_OPS
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
    try: return powx_vd(m, b, E, sg)
    finally: CTX['stage'] = None


VDC = 1              # stage C in the value domain (1) or the coefficient-domain squaring of 4.5 (0); a constant of the algorithm
VD_H = 1 << 20       # h: the order of the subgroup H; the inner transform of h points is one row of passes (plan rows = 1, a = 32), in place on a coset
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
TWC_A = 17; TWL_A = 14; TWD_A = 19; TWD_HI = 0     # TWC_A: the Newton and quotient products of stage C (3*2^17 points); TWD_A: stage D (2^19 and 3*2^18 points)
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
TRC = (477, 9)       # (c, d): O1 = the first c = 477 of the 2^d = 512 depth-9 nodes of H_N, N = 2^20 (None: off)
TR_MID = None        # radices of the middle passes, top-down (None: radix 16 first while the remainder is not a multiple of 3, then radix 8)
TR_TWB = 11          # 8-point block twiddles: 7 constants from a two-level root table: LD 2 + 2, 1 mul, 2 sqr, 4 mul by register constants (i, zeta8)
TR_TWG = 11          # radix-8 group twiddles, as TR_TWB
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


def tr_scale(n): return 2 * n         # the twist / 1/N as a running product fused into the adjacent pass: mul of the running factor, mul of the value
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
    T.ctl(tr_batch_inv())                                                # (5) k1 = -1/(n^3 g) on O1 (chunked batch inversion; the prefix products of a chunk of 2^16 in sScr)
    steps, nset = d['steps'], d['nset']
    step0, step1 = tr_step(0), tr_step(1)
    T.ctl((steps - nset) * step0 + nset * step1)                         # (6)
    T.ctl(tr_pw(7) + ext + tr_pw(11))                                     # (7)
    T.free(sR1); T.free(sG1)
    if sScr is not None: T.free(sScr)
    interp = tr_inv() + tr_scale(n1)
    T.ctl(2 * interp)                                                     # (8)
    T.ctl(2 + 500)                                                        # sTab stays live: stage D's apply on O1 uses the root tables, and frees it
    VD.clear(); VD.update(d, ext=ext, step0=step0, step1=step1, interp=interp, NTAB=NTAB)
    info = dict(steps=steps, nset=nset, PN=None, PNp=None, step=step0, mulx=step1 - step0, sg2=sg, sR2=sR2, sTab=sTab, vd=dict(VD))
    return T, info


# ================================================================ stage D: the normal-sequence half-gcd after bradcush e6dcb600 / 4bcabff8 (credited derivative, read as text only; proof 4.4)
# Inversion-free half-gcd on the normal remainder sequence: a node of budget 2^j - 1 makes two child calls of budget 2^(j-1) - 1; its products run on 3 * 2^(j-1) points, the rows
# Y - 1, Y + 1, Y - i (Y = X^n, n = 2^(j-1)) with a 3-row CRT; the row Y - 1 values of each child's matrix are its rows 0, 1 (reused), and the M1 row values kept from the apply are reused
# in M = M1 [[Q, 1], [b^2, 0]] M2; pseudo-division over the positions the next call reads. Driver: hgcd(k <= PD_KMAX) on the top window, then the apply of its matrix to the whole pair in place.
# Charges: field op 1, LD/ST 2, loop 3 n + 2, the passes of this program (fwd_passes, inv_passes, stageA_*), the truncated transform of stage C (tr_*) for an apply on O1.
PD_ARENA_OP = 10     # bump arena: an allocation or release = LD 1, add, ST 1, compare + branch (2), 3 spare
PD_CALL = 40         # one call of hgcd
PD_BASEJ = 6         # base case: budget 2^6 - 1 = 63
PD_KMAX = 65535      # the largest budget of one outer step


def pd_loopc(n): return 3 * n + 2
def pd_copy(l): return 4 * l + pd_loopc(l) if l > 0 else 0
def pd_zfill(l): return 2 * l + pd_loopc(l) if l > 0 else 0
def pd_acc(l, mul): return (7 + mul) * l + pd_loopc(l) if l > 0 else 0
def pd_crt(n): return 22 * n + pd_loopc(n)                 # per t: 10 field ops, LD 3, ST 3


@functools.lru_cache(None)
def pd_P1(a): return make_plan(1, a)[0]
@functools.lru_cache(None)
def pd_FROW(a): return fwd_passes(pd_P1(a), pd_P1(a).np) + 10
@functools.lru_cache(None)
def pd_IROW(a): return inv_passes(pd_P1(a), pd_P1(a).np - 1) + 10


def pd_rowfwd(L, r, a):
    """one row of a product: the window of L coefficients folded onto 2^a points (copy, zero-fill, fold-add; row Y - i folds with a multiplication), the row twist (rows 1, 2: running
    factor, 2 per point) and the forward transform"""
    n = 1 << a
    return pd_copy(min(L, n)) + pd_zfill(max(0, n - L)) + pd_acc(max(0, L - n), 1 if r == 2 else 0) + (2 * n if r else 0) + pd_FROW(a)


def pd_rowinv(r, a): return pd_IROW(a) + (1 if r == 0 else 2) * (1 << a)     # 1/n (row 0) or the untwist times 1/n (running factor) fused into the CRT loop


@functools.lru_cache(None)
def pd_base(j=PD_BASEJ):
    """the base case of budget 2^j - 1: two remainder steps per pass (r1 and r2 in one loop: LD a, b; ST r1, r2), the same for the two matrix columns"""
    k = (1 << j) - 1; c = PD_CALL + 4 * PD_ARENA_OP + 10; s = 0
    while s < k:
        Lr = 2 * (k - s - 1) + 1
        if s + 1 < k:
            c += 2 * (10 + 15) + 26                            # control; q1, q0, b, b^2 of both steps; r1's two leading coefficients ahead
            c += 13 * Lr + 9 * (Lr - 2) + pd_loopc(Lr)         # one pass: r1 (13 per position) and r2 on Lr - 2 positions (9: r1 stays in registers)
            c += 2 * (13 * (s + 2) + 9 * (s + 3) + pd_loopc(s + 3)) + 8
            s += 2
        else:
            c += 10 + 15 + 13 * Lr + pd_loopc(Lr) + 2 * (13 * (s + 2) + pd_loopc(s + 2)) + 4; s += 1
    return c


@functools.lru_cache(None)
def pd_node(j):
    """operations of one node of budget 2^j - 1, returning its matrix in coefficient form and its values on the parent's row Y - 1"""
    if j <= PD_BASEJ: return pd_base(j)
    a = j - 1; n = 1 << a
    c = PD_CALL + 14 * PD_ARENA_OP + 2 * 2                    # call, arena buffers, the return tests
    c += 2 * pd_node(j - 1)
    LA = 1 << (j + 1); LB = LA - 1
    rowsM = [0, 1, 2] if j - 1 == PD_BASEJ else [1, 2]
    for r in range(3): c += pd_rowfwd(LA, r, a) + pd_rowfwd(LB, r, a)        # apply1: (c, d) = adj(M1)(a, b) on 3n points
    for r in rowsM: c += 4 * pd_rowfwd(n, r, a)
    c += 3 * 2 * (pw_loop(n, 0) + pw_loop(n, 2))
    c += 2 * sum(pd_rowinv(r, a) for r in range(3)) + 2 * pd_crt(n)
    Le = (1 << j) - 1
    c += 30 + 13 * Le + pd_loopc(Le)                           # pseudo-division (quotient of degree 1), e on the 2^j - 1 positions child 2 reads
    c += 3 * (25 * n + pd_loopc(n))                            # M = M1 [[Q, 1], [b^2, 0]] M2 on 3n points: Q values and M1 Q (col 1 reused)
    for r in rowsM: c += 4 * pd_rowfwd(n, r, a)
    c += 3 * 4 * (pw_loop(n, 0) + pw_loop(n, 1))
    c += 4 * sum(pd_rowinv(r, a) for r in range(3)) + 4 * pd_crt(n)
    return c


@functools.lru_cache(None)
def pd_node_mem(j):
    """peak words of a node in the bump arena (its inputs, the caller's windows, excluded); returned: M coefficients 4 * 2n and M values on the parent's row Y - 1 (8n)"""
    if j <= PD_BASEJ: return 4 * (1 << j) + 2 * (1 << (j + 1))
    n = 1 << (j - 1)
    m1 = pd_node_mem(j - 1)
    apply1 = 4 * n + 12 * n + 6 * n                            # M1 coefficients + row-0 values (returned), M1 rows 1, 2 values, the a, b row buffers (c, d over them)
    child2 = 12 * n + 4 * n + m1                               # M1 values kept, the d and e windows (2n each), child 2
    prod = 12 * n + 4 * n + 4 * n + 8 * n                      # M1 Q values, M2 coefficients + row-0 values (returned), M2 rows 1, 2 (outputs over the M2 values)
    out = 8 * n + 8 * n
    return max(m1, apply1, child2, prod, out)


def pd_plan_apply(lc, la, k):
    """the apply of the driver: (c, d) = adj(M)(a, b) cyclic on Nd >= lc points, a, b in place; the cheapest of the truncated set O1 (stage C's transforms), 2^a or 3 * 2^a points;
    the matrix entries row-wise (rows of 2^16) when Nd >= 2^17"""
    n1 = tr_dims()[3]; best = None; cands = []
    if lc <= n1 and la <= n1: cands.append(('tr', n1))
    for aa in range(5, 20):
        if (1 << aa) >= lc: cands.append(('p1', aa))
        if 3 * (1 << aa) >= lc and 3 * (1 << aa) <= n1: cands.append(('p3', aa))
    for kind, x in cands:
        if kind == 'tr':
            Nd = n1; f = tr_fwd(); iv = tr_inv() + n1
        elif kind == 'p1':
            Nd = 1 << x; Pl = pd_P1(x); f = fwd_passes(Pl, Pl.np) + 10; iv = inv_passes(Pl, Pl.np - 1) + Nd + 10
        else:
            Pl, pc = make_plan(3, x); Nd = Pl.N
            f = stageA_fwd(Pl, min(la, Nd)) + 3 * fwd_passes(Pl, Pl.np) + pc; iv = 3 * inv_passes(Pl, Pl.np - 1) + stageA_inv(Pl, lc) + Nd + pc
        if Nd > n1: continue
        c = 2 * (pd_acc(max(0, la - Nd), 0) + pd_zfill(max(0, Nd - la)) + f)
        L = k + 1
        if Nd >= (1 << 17):
            R = -(-Nd // (1 << 16))
            c += 4 * R * (pd_copy(1 << 16) + pd_acc(max(0, L - (1 << 16)), 1) + 2 * (1 << 16) + pd_FROW(16))
        else:
            c += 4 * (pd_copy(L) + pd_zfill(Nd - L) + f)
        c += 2 * (pw_loop(Nd, 0) + pw_loop(Nd, 2))
        c += 2 * iv + 8 * PD_ARENA_OP + 20
        if best is None or c < best[0]: best = (c, kind, x, Nd)
    return best


def pd_run(m):
    """stage D on (g, R - 1) of degree m: the operations besides the stage frame and the table, the peak words of the bump arena, the outer steps"""
    lx = m + 1; ops = 0; steps = []; peak = 0
    while True:
        n = lx - 1; j = 0
        while ((1 << (j + 1)) - 1) <= min(PD_KMAX, (n - 1) // 2): j += 1
        if j <= PD_BASEJ: break
        k = (1 << j) - 1
        t = pd_node(j) + 10
        ap = pd_plan_apply(n - k + 1, lx, k)
        ops += t + ap[0]
        peak = max(peak, pd_node_mem(j), 4 * (k + 1) + 4 * (1 << 16) + (tr_scratch() if ap[1] == 'tr' else 0))
        steps.append((n, k, t, ap)); lx -= k
    n = lx - 1; tail = 0
    for d in range(n, 0, -1): tail += 10 + 15 + 13 * d + pd_loopc(d)     # classical steps below the base-case degree, then the normalisation of G
    ops += tail + powcost(PM2) + INV_CTL + 2 + 2 * 1 + 2 + 2 + pd_loopc(1)
    return ops, peak, steps, n


def stage_d(m, db, cinfo):
    """stage D of one trial on the arrays g, R and the root tables carried from stage C: the frame, its twiddle table, the bump arena, the half-gcd"""
    D = Tr(db); D.ctl(STAGE_BK); D.ops += 1; D.ctl(11)
    twD = tw_new(D, TWD_A, TWD_HI)                              # the table of its transforms (2^19 and 3*2^18 points)
    ops, peak, steps, tdeg = pd_run(m)
    sA = D.new_fp(peak)                                         # the bump arena of the half-gcd
    D.ctl(ops)
    D.free(sA); D.free(twD); D.free(cinfo['sTab']); D.free(cinfo['sR2']); D.free(cinfo['sg2'])
    D.ctl(2)
    return D, dict(peak=peak, steps=steps, tail=tdeg, core=ops)


def stage_AB(m):
    """the arrays of the stages before C: the twiddle table (init), g (stage A), the array of stage B (freed after the inverse transforms) and F.
    Stage B transforms on the plan of plan_for_len(m + 1): the least a with 2^a >= m + 1 or 3*2^a >= m + 1 (2^a taken first at that a); block mode (that a > BIGA): the ncos cosets
    of 3*2^(BIGA-1); sub-block: the single inverse transform of that plan, SMALL_BLOCK = 1 running the two-ended pool."""
    H = next(v for a in range(2, 96) for v in (1 << a, 3 << a) if v >= m + 1)     # plan_for_len(m + 1): at each a from 2 up, 2^a first, then 3*2^a
    if H > (3 << BIGA):                                      # block mode of stage B (the plan has a > BIGA): no transform of that size exists
        Pl = make_plan(3, BIGA - 1)[0]; ncos = -(-(m + 1) // Pl.N); H = ncos * Pl.N
    I = Tr(0)
    if not TWMOVE: I.new_fp(twiddle_slots(m))
    A = Tr(1)
    sg = A.new_fp(vd_gslots(m))  # pool:H
    B = Tr(2)
    twB = tw_new(B, next(a for a in range(2, 96) if H in (1 << a, 3 << a)), False) if TWMOVE else None     # stage B: the table of its transform (3*2^a points)
    sb = B.new_fp(H)  # pool:H
    B.free(sb)
    if twB is not None: B.free(twB)
    return I, A, B, sg


def main():
    m = (5 ** 9 - 1) // 2
    set_outer_limit(m)
    I, A, B, sg = stage_AB(m)
    C, cinfo = powx_lean(m, 3, PM1H, sg); C.ctl(STAGE_BK)
    D, dinfo = stage_d(m, 3, cinfo)                            # live blocks at the entry of stage D: g, R and the root tables
    print('m =', format(m, ','), '| truncated point sets: n1 =', format(VD['n1'], ','), 'of N =', format(VD_H, ','), '(TRC = %d of %d nodes) | squaring steps' % (TRC[0], 1 << TRC[1]), cinfo['steps'], 'of which with S:', cinfo['nset'])
    print('stage C: one squaring step %s operations (with S: %s), middle radices %s' % (format(cinfo['step'], ','), format(cinfo['step'] + cinfo['mulx'], ','), tr_mid()))
    print('S_C =', format(C.ops, ','))
    print('stage D outer steps (degree n, budget k, hgcd ops, apply ops, apply plan):')
    for n, k, tt, ap in dinfo['steps']: print('  n = %d k = %d hgcd %s apply %s %s' % (n, k, format(tt, ','), format(ap[0], ','), ap[1:]))
    print('stage D: classical tail from degree %d; half-gcd operations %s; bump arena %s words' % (dinfo['tail'], format(dinfo['core'], ','), format(dinfo['peak'], ',')))
    print('S_D =', format(D.ops, ','))
    pA = A.peak; pB = A.cur + B.peak; pC = A.cur + B.cur + C.peak; pD = A.cur + B.cur + C.cur + D.peak
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
    assert C.ops == 61516769663 and D.ops == 17835006021
    assert peaks == dict(A=31260736, B=89981120, C=127877376, D=104997056) and pool['big_high'] == 127877376 and arena == 127894400 and mem == 133210380


if __name__ == '__main__':
    main()
```

Exit status 0. Output:

```
m = 976,562 | truncated point sets: n1 = 976,896 of N = 1,048,576 (TRC = 477 of 512 nodes) | squaring steps 236 of which with S: 45
stage C: one squaring step 255,998,140 operations (with S: 258,928,828), middle radices [4, 4, 3, 3]
S_C = 61,516,769,663
stage D outer steps (degree n, budget k, hgcd ops, apply ops, apply plan):
  n = 976562 k = 65535 hgcd 929,595,151 apply 533,393,342 ('tr', 976896, 976896)
  n = 911027 k = 65535 hgcd 929,595,151 apply 534,048,692 ('tr', 976896, 976896)
  n = 845492 k = 65535 hgcd 929,595,151 apply 446,826,566 ('p3', 18, 786432)
  n = 779957 k = 65535 hgcd 929,595,151 apply 445,410,324 ('p3', 18, 786432)
  n = 714422 k = 65535 hgcd 929,595,151 apply 445,410,404 ('p3', 18, 786432)
  n = 648887 k = 65535 hgcd 929,595,151 apply 445,410,288 ('p3', 18, 786432)
  n = 583352 k = 65535 hgcd 929,595,151 apply 282,942,386 ('p1', 19, 524288)
  n = 517817 k = 65535 hgcd 929,595,151 apply 281,825,786 ('p1', 19, 524288)
  n = 452282 k = 65535 hgcd 929,595,151 apply 222,028,058 ('p3', 17, 393216)
  n = 386747 k = 65535 hgcd 929,595,151 apply 220,611,570 ('p3', 17, 393216)
  n = 321212 k = 65535 hgcd 929,595,151 apply 140,882,856 ('p1', 18, 262144)
  n = 255677 k = 65535 hgcd 929,595,151 apply 103,730,220 ('p3', 16, 196608)
  n = 190142 k = 65535 hgcd 929,595,151 apply 70,377,370 ('p1', 17, 131072)
  n = 124607 k = 32767 hgcd 415,103,005 apply 52,819,998 ('p3', 15, 98304)
  n = 91840 k = 32767 hgcd 415,103,005 apply 31,716,686 ('p1', 16, 65536)
  n = 59073 k = 16383 hgcd 183,074,811 apply 25,870,250 ('p3', 14, 49152)
  n = 42690 k = 16383 hgcd 183,074,811 apply 15,466,976 ('p1', 15, 32768)
  n = 26307 k = 8191 hgcd 79,501,763 apply 12,616,264 ('p3', 13, 24576)
  n = 18116 k = 8191 hgcd 79,501,763 apply 5,488,966 ('p3', 12, 12288)
  n = 9925 k = 4095 hgcd 34,546,553 apply 2,707,600 ('p3', 11, 6144)
  n = 5830 k = 2047 hgcd 14,718,631 apply 1,545,228 ('p1', 12, 4096)
  n = 3783 k = 1023 hgcd 6,103,701 apply 1,295,884 ('p3', 10, 3072)
  n = 2760 k = 1023 hgcd 6,103,701 apply 749,726 ('p1', 11, 2048)
  n = 1737 k = 511 hgcd 2,435,301 apply 632,306 ('p3', 9, 1536)
  n = 1226 k = 511 hgcd 2,435,301 apply 268,580 ('p3', 8, 768)
  n = 715 k = 255 hgcd 959,263 apply 178,938 ('p1', 9, 512)
  n = 460 k = 127 hgcd 352,431 apply 128,986 ('p3', 7, 384)
  n = 333 k = 127 hgcd 352,431 apply 69,470 ('p1', 8, 256)
stage D: classical tail from degree 206; half-gcd operations 17,832,906,505; bump arena 1,048,320 words
S_D = 17,835,006,021
peak of the live set, stage A = 31,260,736 bytes
peak of the live set, stage B = 89,981,120 bytes
peak of the live set, stage C = 127,877,376 bytes
peak of the live set, stage D = 104,997,056 bytes
two-ended pool: blocks of more than 2^10 bytes; largest sum of the two ends after each stage (bytes): init 0, A 31,260,736, B 89,981,120, C 127,877,376, D 127,877,376; at most 10 blocks; 45 blocks examined in all
slab classes (class: peak number of live blocks): ; slab area = 0 bytes
arena = 127,894,400 bytes (two-ended pool 127,877,376 + 128, slab classes 0, stages E and later 16,896), memory = 133,210,380 bytes, log2 = 26.990
```
