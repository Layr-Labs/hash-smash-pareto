# Orchard Poseidon, r = 9: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, lean half-gcd with a memory cap, one centre, 64-register passes

## 1. Claim

Target: `poseidon-orchard-r9-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, nine partial rounds 4, 5, 6, 7, 8, 9, 10, 11 and 12, full rounds 60-63, state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is an algorithm (sections 2-4) with an operation count that bounds every run (sections 6-7) and a success probability derived from two score-critical premises, `H-ONE` (section 9.1, a statement about the fraction of centres at which the fixed digest polynomial has between 1 and 16 usable roots) and `H-NORMAL` (section 9.5, the normality of the remainder sequence, allowance `delta = 0.001`); section 9.2 derives the success probability from them. Stage D is charged for the normal remainder sequence with the ABORT on any other case (section 6.3), so the time and memory bounds use no premise on the sequences.

* The algorithm: draw a centre `c` uniformly from `F_p` from fresh random words, build the odd part `g_c` of the line polynomial by evaluation and one inverse transform, compute `R = S^((p-1)/2) mod g_c` in the value domain on `K_cos = 114` cosets of size `h = 2^27` (bradcush `4bcabff8`; every transform pass in the block form of the declared 64-word register file, 4.2), take `G = gcd(g_c, R - 1)` by the lean cofactor-free half-gcd (bradcush `e6dcb600`/`1aa56884`) with the memory cap of weijiekoh `a78f526e` (outer step `k <= 3 * 2^29`, applies longer than `3 * 2^31` coefficients by in-place block products of block length `3 * 2^28`, section 4.4), charged for every remainder sequence, and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` in at most `Z = 64` rounds, take its square root, map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; the trial runs to its end or ABORTs stage D on an abnormal remainder sequence (6.3), when the allocator is reset and the run ends without output; a verified collision ends the algorithm.
* `success_probability = 0.392099999999996447`: a lower bound for the probability, over the algorithm's fresh random words, that the centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta)^K - K (eps_coin + eps_iso) = q - delta - eps_coin - eps_iso` with `q = 0.3931` (the premise `H-ONE`, section 9.1), `delta = 0.001` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `K = 1`, `eps_iso < 2^-48`, `eps_coin < 2^-122` (sections 4.1.1, 9.2). The value the formula gives with those eps bounds is `0.392099999999996447` (at or above the organizer floor 0.39).
* `time_log2 = 42.67345` in target-compression units (`C(9) = 405` primitive operations per unit): the operation count that bounds every run, derived in section 6 as `T_fixed + K * T_trial + T_off` with `K = 1`, stage C in the value domain (4.3V), stage D the lean cofactor-free half-gcd with the memory cap charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (4.4, 6.3; the time bound holds for every sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work), and stage E at its cap of `Z` rounds at degree `DMAX`. `N_max = 2,840,816,925,173,729` operations, `log2(N_max / 405) = 42.67344...`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is bounded by 1,000,000 operations; that bound is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 40.890` (`2,036,428,264,780` bytes, section 7). The normalized cost is `42.67345 + max(0, 40.890 - 20) = 42.67345 + 20.890 = 63.56345`.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; `65` words at most (section 4.1.1), and a draw (one word) costs 31 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^15`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Prior entry: this entry is our filed r = 9 entry `b0ee9e30` (normalized cost 63.83088) with one change: the transforms run on the 64-register machine stated as a restriction in claim.json, as in our r = 3 entries `ef123c2b`/`253629b9`: every transform pass (the inner transforms of stage C, the products of stages C and D) runs blocks of `2^k` points with the `2^k - 1` twiddles of its group in registers, and the inner transforms of `2^27` points run the passes `4, 4, 4, 5, 5, 5` (4.2, 4.3V). Stage C falls from `2,233,950,532,573,330` to `1,809,844,608,973,170` operations and stage D from `1,162,288,107,277,055` to `1,007,839,492,582,635`; the memory is unchanged at `2^40.890`. `b0ee9e30` is our entry `e76bdab0` with four changes under the same cost model: (i) stage C computed in the value domain on cosets (section 4.3V, the method of bradcush `4bcabff8`); (ii) stage D the lean cofactor-free half-gcd charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, the premise `H-NORMAL` of bradcush (entries `e6dcb600`, `1aa56884`) in the organizer-run form of gta6rp (entry `bef31fdd`) (sections 4.4, 6.3, 9.5, 10.5.1); (iii) the success allowance split between the two premises as in cryptogakusei's entry `4888e783`: `H-ONE` at `q = 0.3931` (9.1) and `H-NORMAL` at `delta = 0.001` (9.5), so one centre (`K = 1`) clears the floor (9.2); (iv) the stage-D memory cap of weijiekoh's entry `a78f526e` (outer half-gcd step `k <= DMAX`, long applies by in-place block products), ported into this program and charged in this cost model (4.4, 7). The per-trial rows A, B, E, F, G and the evidence are the same family; the memory is the actual allocator high-water mark of one trial (section 7).
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1), a statement about the fraction of good centres, and `H-NORMAL` (score-critical for the success probability only, section 9.5), bradcush's premise on the normality of the remainder sequence stated with the allowance `delta = 0.001` and supported by organizer-run tests (gta6rp's recipe, entry `bef31fdd`). Both are statements about probability. The machine (64 registers of 256 bits and constants as immediates; every load, store and spill counted) is stated as a restriction in claim.json, as the accepted entries `89b451ff` and `fb176310` state theirs, not as a heuristic (4.2). The costs are the declared cost model of this entry, not heuristics: the charging rules of section 4.2 with that register file, the lean cofactor-free half-gcd of stage D with the memory cap charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (Appendix E). Everything else is proved or counted here.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`. `(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`. The algorithm uses the line `j = 0`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant `M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS, nonzero on the deployed constants, checked). Let `(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, `d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i` (the supports are disjoint). After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8, 9, 10, 11, 12 (partial), 60, 61, 62, 63 (full) put fifteen S-box layers on top of an affine map, and the digest is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^15 = D = 30,517,578,125`. The leading coefficient is obtained by propagating leading coefficients through the fifteen layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used: `f_D(0) = 0x38489183ee8ea6531b0262aa997881736e2e11b4da7afe2fb7083021c88caae2` (computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau` against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`), hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 15,258,789,062`, `g_c` has degree exactly `m` and leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`, `W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The useful roots are the roots in `F_p` with `S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p`; `S = 0` is not a root of `S^((p-1)/2) - 1`). `G` divides the squarefree `S^((p-1)/2) - 1`, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. At this r no transform of `H >= m + 1` points exists: `p - 1 = 2^32 * 3 * q` has roots of unity of order `3 * 2^a` for `a <= 32` only, and `m + 1 = 15,258,789,063 > 3 * 2^32`. Let `B = 3 * 2^31 = 6,442,450,944`, `zeta` a primitive `2B`-th root of unity (`2B = 3 * 2^32` divides `p - 1`) and `omega = zeta^2`, a primitive `B`-th root. Let `kappa = ceil((m + 1) / B) = 3` and `v_k = k + 1` for `k = 0..kappa-1`, `u_k = v_k^2`; the `kappa` numbers `n_k = u_k^B` are pairwise distinct (checked). The evaluation points are `s_{k,i} = v_k zeta^i` for `k < kappa`, `i < B`, so that `S_{k,i} = s_{k,i}^2 = u_k omega^i`, and `g_c(S_{k,i}) = (F(c + s_{k,i}) - F(c - s_{k,i})) / (2 s_{k,i})`. Write `g_c(x) = sum_{t < kappa} x^{tB} h_t(x)` with `deg h_t < B`. For `y = omega^i` we have `y^B = 1`, hence `g_c(u_k y) = w_k(y)` with `w_k(y) = sum_t n_k^t h_t(u_k y)`, a polynomial of degree `< B`. One inverse transform of size `B` of the values `(g_c(S_{k,i}))_i` returns the coefficients `w_k[j] = u_k^j sum_t n_k^t h_t[j]`. After multiplication by `u_k^{-j}`, for every `j < B` the numbers `W_k[j] = sum_t n_k^t h_t[j]` (`k < kappa`) are the values of the polynomial `sum_t h_t[j] X^t` at the distinct nodes `n_k`: a `kappa x kappa` Vandermonde system, whose inverse (`kappa^2` constants, fixed in the source) returns `h_0[j], ..., h_{kappa-1}[j]`, that is the coefficients `g_c[j + tB]`. The `2 kappa B = 38,654,705,664` evaluations of `F` are each charged as one target-compression unit (`C(9) = 405` operations), although a line evaluation (affine start, the remaining rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation. The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 s_{k,i})`, two multiplications for the recurrences of `s_{k,i}` and `1/s_{k,i}`, one store with its address operation, the loop control, the update of the row counter, and the executed shifts, masks, ors and loop control of the bit-reversed index, which are counted inside that function) and the recombination (per `j`: `kappa` multiplications for the running powers `u_k^{-j}`, `kappa` for the scaling, `kappa^2` multiplications and `kappa (kappa - 1)` additions for the Vandermonde system, `kappa` loads and `kappa` stores) are charged on top.

## 4. The algorithm (at most K centres, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   twiddle table (once)
setup:  the line (line_setup) (once)
for t = 1, 2, ..., K:                 [the test t <= K is made at the start of every trial; no exit except success]
  A  c := a uniform element of F_p from one fresh random word (4.1.1)
  B  g := monic g_c, by section 3 (38,654,705,664 evaluations + 3 inverse NTTs of size 6,442,450,944 + the recombination of the 3 cosets + the nonzero-leading-coefficient test + normalisation)
  C  R := S^((p-1)/2) mod g, in the value domain on K_cos = 114 cosets of size h = 2^27 (section 4.3V): 222 squaring steps, 45 of them also multiplying by S
  D  G := gcd(g, R - 1) (monic): the lean cofactor-free half-gcd with the memory cap, charged for every remainder sequence (section 4.4), by the normal-sequence trace with the quotient and return tests (6.3)
  E  if deg G = 0 or deg G > DMAX: trial ends. Otherwise isolate a root S of G (4.1.2); if none within Z = 64 rounds: trial ends.
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (405 operations each) are equal and the pairs differ -> output; otherwise the trial ends
```

4.1.1 Coins. The only randomness is the cost-model random-word primitive. The words are fresh, independent and uniform on `[0, 2^256)`. A centre is `c = w mod p` for one word `w` (at most three conditional subtractions); the isolation of stage E draws at most 64 further words, reduced the same way. At most 65 words per run; a draw is 31 operations. There is no rejection and no retry. The reduction is not exactly uniform on `F_p`: `2^256 = 3p + r` with `0 < p - r = 4(p - 2^254) < 2^127.1`, so every residue has 3 or 4 preimages and `w mod p` is within statistical distance `r (p - r) / (p 2^256) < 2^-128.9` of uniform on `F_p`. Over the 65 words the distance is `eps_coin <= 65 * 2^-128.9 < 2^-122`, and the success bound (9.2) subtracts it.

4.1.2 Stage E: isolating a root of `G`. With `1 <= deg G <= DMAX = 16`, a Cantor-Zassenhaus split with random shifts isolates one linear factor in at most `Z = 64` rounds at degree `<= 16`; `eps_iso < 2^-48` bounds the probability that 64 rounds fail to isolate a root when `deg G >= 1` (section 9.4).

### 4.2 Machine model and charging rules (summary; `C(9) = 405`)

Every field operation, load, store, control operation and random word is one primitive operation; `C(r) = 216 + 21 r = 405` primitive operations is one target-compression unit. The register file is 64 words of 256 bits (the machine restriction of claim.json: it holds the 16 values and 15 twiddles of a radix-16 block, or the 32 values and 28 of the 31 twiddles of a radix-32 block; every other value, the 3 spilled twiddles of a radix-32 group included, is charged as a load or store), the only register assumption. Every transform pass of `k` layers at level `l0` of a `2^a`-point transform runs `2^(a-k)` blocks of `2^k` points, each `2^k` loads, `k 2^(k-1)` butterflies at 3, `2^k` stores and 5 control (`4 * 2^k + 3 k 2^(k-1) + 5`; radix 32 adds 6 for the loads of its 3 spilled twiddles), and `2^l0` groups, each forming its `2^k - 1` twiddles once in registers from the twiddle table (radix 16: two loads of two words, one multiplication, three squarings, eleven multiplications by register constants and 5 control, 24; radix 32: 42 with the stores of the 3 spilled twiddles; `k <= 3`: 16), plus `9 k + 19` per forward pass and `9 k + 20` per inverse pass; the algorithm runs on one thread, no dispatch. Allocation: one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes. A block of more than `2^24` bytes is served by the two-ended pool (one region, two ends, first-fit in address order, the statements marked `# pool:H` using the high end and, with the depth-parity placement of section 7, the end `(j + bit8) mod 2` of a half-gcd node at depth `j`); every smaller block by its slab class (the least `j >= 7` with `2^j >= need`, a slot of `2^j` bytes). The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows (a pool request `97` operations besides the walk and `13` per block examined, a slab request at most `126`, a free `81` for a slab block and at most `105` for a pool block). The memory of both allocators is the arena of section 7.

### 4.3V Stage C in the value domain, on cosets of a subgroup of order `h = 2^27` (the method of bradcush `4bcabff8`)

The residue `R = S^((p-1)/2) mod g` is carried by its values on `K_cos = 114` cosets `5^k H`, `k = 0..K_cos-1`, of the subgroup `H` of order `h = 2^27` (the extension uses the `2 K_cos = 228` cosets `5^0 H, ..., 5^(2 K_cos - 1) H`). The cosets are distinct because `5^(d h) != 1` for `1 <= d <= 2 K_cos - 1` and `ord(5^h) = (p-1)/h >= 2 K_cos`; `h | p - 1`; and `n1 = K_cos h = 15,300,820,992 >= m + 1`. A squaring step is a pointwise square on the current point set plus one change of point set (an extension) built from `2 K_cos` inner transforms of `h` points and a between-coset Lagrange convolution of length `Lx = 256` (the smallest `2^a` or `3*2^a` that is at least `2 K_cos`); the start monomial is `S^v`, `v = 2^31 = 2,147,483,648` a multiple of `h` (VSHIFT = 2). There are `222` squaring steps, `45` of them also multiplying by `S` (a streaming shift). The evaluation of `q` uses `Kq = 17` rows and a convolution of length `Lq = 192`; the chirp evaluation of `g` at the `2 K_cos` nodes uses a convolution of length `Le = 384`. The equality of the value-domain and coefficient-domain residue is exact (it composes exact inner transforms with the exact Lagrange interpolation of polynomials of degree `< K_cos` from `K_cos` distinct nodes); no premise is added. `g` and `R` are held whole (one array each; the top-node pieces of bradcush's lemma 4.8(b) are not used). The inner transforms of `h = 2^27` points run the passes `4, 4, 4, 5, 5, 5` (top-down; the cheapest order under the 64-word register file, 4.2). The step-by-step operation count is expanded in Appendix E.1 (where `K_cos` is `K`) and totals **row C = 1,809,844,608,973,170** (section 6).

### 4.4 Stage D: the lean cofactor-free half-gcd with the memory cap, charged for every remainder sequence

`G = gcd(g, R - 1)` is computed by a recursive half-gcd whose products use the transform of section 4.2. The lean variant (bradcush `e6dcb600`/`1aa56884`) returns the remainder of a node, not its transforming matrix, and every consuming `apply` overwrites the arrays it reads (remainder over dividend, the quotient of two coefficients and the remainder only); it computes the same remainder sequence and the same gcd as the matrix form.

Memory cap (the method of weijiekoh `a78f526e`, its `gcd_lean` DMAX and `mat_apply` LMAX, ported into this program and charged in this cost model): (a) the outer loop of the Euclid driver calls `hgcd(a, b, k)` with `k = min(ceil((n + 1)/2), DMAX)`, `DMAX = 3 * 2^29 = 1,610,612,736`, so one outer step reduces the degree by at most `DMAX + 1` and the matrix and the working arrays of one call stay short; (b) every apply of a matrix to a pair longer than `LMAX = 3 * 2^31 = 6,442,450,944` coefficients is done by the block products of section 4.5 at the block length `3 * 2^28 = 805,306,368` (transforms of `3 * 2^29` points): each block of the operands is transformed once, the transforms of a slot are multiplied pointwise and summed, and each output slot is inverse transformed and overlap-added in place into the output array, so the working set of one apply is a few blocks, not the full-length transforms. Both are constants of the algorithm; on the normal sequence every length, parameter and allocation is a function of `m` alone, as without the cap. The cap changes only the shapes of the calls; the remainder sequence and the gcd are the same.

The row is charged for the normal remainder sequence (every quotient of degree 1), the case of the premise `H-NORMAL` (9.5): every division tests that its quotient has degree 1 and every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter (2 operations each), and a zero remainder met inside `hgcd` or in the outer-loop division also ends the trial; on any other case the trial ABORTs (the allocator is reset and the run ends without output, section 6.3). By the prefix lemma of 6.3 every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, so the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The total is **row D = 1,007,839,492,582,635** (section 6.3, 6).

### 4.5 Products longer than `3 * 2^32` points (block mode)

The field has no transform of more than `3 * 2^32` points (`p - 1 = 2^32 * 3 * q`, `q` odd). A product in stage D whose transform would be longer, and every apply longer than `LMAX` (4.4), is computed by block products (scheme (a), Grok job 140): each operand is cut into blocks of `A_HB = 3 * 2^28` coefficients, each block is zero-padded to `A_NB = 3 * 2^29` points and transformed once, the block spectra of a slot (the block pairs `i + j = s`) are multiplied pointwise and summed in the transform domain, and each slot that meets the wanted output window is inverse transformed once and overlap-added, scaled by `1/A_NB`, into the output; a product of two blocks has fewer than `A_NB` coefficients, so a block product does not wrap. A product at or below `LMAX` uses whichever of the single transform and the block products is charged less. Every transform, pointwise product, placement and allocation is charged by the rules of 4.2; Appendix E expands them.

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G | g_c`, whose roots `S` are nonzero squares with `g_c(S) = 0` and `S^((p-1)/2) = 1` (section 3); `s = sqrt(S) != 0`, so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Ledger: operation count (primitive operations; `C(9) = 405`)

| row | what is charged | operations |
| --- | --- | --- |
| init | twiddle table (`ntt_init`, once) | 17,179,887,292 |
| setup | the line (`line_setup`, once) | 4,910 |
| A (per trial) | stage bookkeeping, loop test and update, the coin draw (31), one allocation | 1,196 |
| B (per trial) | `3` cosets of `6,442,450,944` points, each point with two evaluations of `F` (at `c + s` and `c - s`) at `C(9) = 405` operations each, the loop work around them, `3` inverse transforms of size `6,442,450,944`, the recombination of the cosets, the normalisation | 23,115,473,036,889 |
| C (per trial) | `S^((p-1)/2) mod g` in the value domain, `K_cos = 114` cosets of size `h = 2^27`, VSHIFT = 2, passes in block form (sections 4.2, 4.3V); expanded in Appendix E | 1,809,844,608,973,170 |
| D (per trial) | lean cofactor-free half-gcd of `(g, R - 1)` with the memory cap, charged for every remainder sequence (section 4.4): the normal-sequence trace with the quotient and return tests (6.3), passes in block form (4.2); expanded in Appendix E | 1,007,839,492,582,635 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16` | 166,079,773 |
| F (per trial) | square root, back-map | 47,012 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 405 + 32` | 9,132 |
| trial-loop (per trial) | trial-loop bookkeeping and the allocator reset after an ABORT, charged in every trial | 1,012 |
| plan_invN misses | one per distinct plan size | 160,628 |
| output rows | the fixed output rows | 3,390,080 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + T_trial + T_off` | **2,840,816,925,173,729** |

`T_off = 1,000,000`; `T_trial = A + B + C + D + E + F + G + trial-loop = 2,840,799,740,730,819` (the trial-loop row is the trial-loop bookkeeping and the allocator reset after an ABORT, charged in every trial); `T_fixed = init + setup + plan_invN misses + output rows = 17,183,442,910`; `K = 1`, so `N_max = 17,183,442,910 + 2,840,799,740,730,819 + 1,000,000 = 2,840,816,925,173,729`. `log2(N_max / 405) = 42.67344...`, rounded up at five decimals to `42.67345`. Rows C and D are expanded part by part in Appendix E (E.1, E.2) from the dimensions of 4.3V and the half-gcd levels with the kernel charges of 4.2; the parts add up exactly to `1,809,844,608,973,170` and `1,007,839,492,582,635`.

### 6.1 Validation
The worst-case counts are derived by formula and compared with the instrumented totals of our executed runs at `r = 3, 4, 5`; the arena rule (the heap peak of the allocation walk) is within 64 bytes of the measured heap peaks there.

### 6.2 Offline derivation
The literals of the sources (Montgomery forms of the organizer constants, `5^q`, `2^65`, the exponent `(4(p-1)+1)/5`) are derived offline in at most `1,000,000` operations, declared `preprocessing_log2 = 20` and inside `N_max`.

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry `e6dcb600`)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g_c, R_c - 1)`: every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the re-centring division of a node, the division of each repetition of the outer loop, each step of the base case) tests that its quotient has degree 1 (2 operations), before the division runs; (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); a zero remainder inside `hgcd` or in the outer-loop division also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state after the twiddle table (`1,000` operations, charged in the trial) and the run ends without output (`K = 1`). Lemma (prefix; `e6dcb600`, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each call splits at `k1 = ceil(k/2)` and, with every quotient of degree 1, every degree in the tree is fixed by `m` and the number of quotients so far, and the parameters of the second call and of the outer loop (`k = min(ceil((n+1)/2), DMAX)`, section 4.4) are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's `hgcd` calls and divisions produce has degree at least the base-case bound, so every gcd of degree at most `DMAX = 16` first appears in the classical Euclid below the base-case degree, after a prefix of the degree-0 work; a zero remainder earlier ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The quotient test runs before each division, so the Newton (fast) division is never reached on the charged path and row D carries no fast-division or zero-scan term. The charges follow `1aa56884` proof 4.4 and the cap follows `a78f526e` proof 4.4, both read as text only (no entry script was run, compiled or imported). Appendix E.2 expands, for `r = 9`, the charge of stage D for the normal sequence with the tests, `1,007,839,492,582,635`, repetition by repetition.

The `r = 9` trial (`~2.04 TB`, `~2.84e15` operations) exceeds the organizer sandbox (128 MiB, 20 s), so the costs are the exact formula counts of sections 6 and 7; zero-fill clearing is charged (ruling `3476cad8`) and the 64-word register file is the machine restriction of claim.json.

## 7. Memory: the arena of one trial

The arena is the capacity of the allocator of 4.2 on the allocation/free sequence of one trial (`K = 1`: the run is one trial). Appendix E.3 runs the allocator on every allocation and free of the trial in the order of the program and reports the two-ended-pool high-water mark (the largest sum of the extents of the two ends over the trial), the slab area and the peaks of the live set per stage. The two-ended pool takes the blocks of more than `2^24` bytes and is placed with depth-parity ends and in-place `R*Q` with two spare slots charged (the `POOL_PLACE = 20` discipline). Under the H-NORMAL ABORT stage D the stage-D live set holds the **normal-case division arrays**: on the normal sequence every quotient has degree 1, so each division forms only the quotient of two coefficients and the remainder, and a trial with any other sequence ends (ABORT) after a prefix of these allocations (6.3), so the normal-case walk bounds every trial. With the memory cap of 4.4 the stage-D live peak is `1,769,526,527,168` bytes, below the stage-C peak; the stage-D trace of Appendix E has no event that raises the pool's high-water mark. The high-water mark is `2,035,814,651,200` bytes, reached in stage C, plus 128 bytes so the unused middle is always at least 128 bytes. The slab classes take the smaller blocks: `608,280,576` bytes. Stages E and later hold at most 16 small arrays and the free-list heads: `16,896` bytes. The arena is `2,036,422,948,800` bytes (two-ended pool `2,035,814,651,200 + 128`, slab `608,280,576`, stages E and later `16,896`). Peaks of the live set per stage (bytes): A `558,345,748,608`; B `1,176,821,039,296`; C `2,035,827,246,528`; D `1,769,526,527,168`. With `5,250,444` bytes of code and static data and a `65,536`-byte stack, the footprint is `2,036,428,264,780` bytes `= 2^40.890`, rounded up at three decimals. No stored advice; the twiddle table is built at run time and charged in stage init.

## 8. Review points, answered by location

1. Row D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (6.3): by the prefix lemma every trial executes a prefix of the normal-case work, so the time and memory bounds hold for every sequence; `H-NORMAL` (9.5) enters only the success probability.
2. The memory cap (4.4) is a constant of the algorithm (`DMAX = 3 * 2^29`, `LMAX = 3 * 2^31`, block length `3 * 2^28`); its extra transform work is charged in row D, and its effect on the memory is read from the allocation walk of Appendix E (stage-D peak `1,769,526,527,168` below the stage-C peak; no stage-D event raises the high-water mark).
3. Row B reproducible from sections 3 and 6 (evaluations * ops/unit + the 3 inverse transforms + the recombination + normalisation). The 64-word register file (the machine restriction of claim.json, 4.2) is the only register assumption; every value beyond it is charged as a load or store.
4. The 1,000,000-op offline figure is a declared bound (`preprocessing_log2 = 20`), score effect < 4e-7 bit.
5. The mem penalty uses the rounded-up `mem_log2` - a self-penalizing over-charge, deliberate.
6. Row D is the normal-sequence trace with the tests and nothing else: the quotient test runs before each division, so the Newton (fast) division is never reached on the charged path and no fast-division or zero-scan term is added (6.3; Appendix E.2 expands the row).
7. `success = 1 - (1 - q + delta)^K - K (eps_coin + eps_iso) >= 0.39` from the premises `H-ONE` and `H-NORMAL` (9.2, 9.5) with `K = 1`, `q = 0.3931`, `delta = 0.001`, i.e. `q - delta - eps_coin - eps_iso`; the value the formula gives with the stated eps bounds is `0.392099999999996447`, margin above 0.39 is `0.002099999999996447`. The delta stated in H-NORMAL (9.5) is the delta used here.
8. The stage-D memory peak holds the normal-case division arrays (section 7, 6.3); an abnormal trial ABORTs after a prefix of these allocations.
9. The organizer-checkable output is the returned witness-pair count. For euclid-gcdpos (10.5.2) a pair is returned only when `deg G >= 1`, so that count is the organizer-counted good-centre fraction at `N = 2, 3`; the step from there to `N = 15` is the premise H-ONE (9.1), not an organizer-verified proof.

## 9. The premise and the success bound

### 9.1 H-ONE
The number of centres `c` with `1 <= k(c) <= 16` is at least `q p = 0.3931 p`, `k(c)` the number of nonzero squares `S` with `g_c(S) = 0` (`= deg G`). The premise states `q = 0.3931`, the Poisson(1/2) law value `0.39346933` less the extrapolation allowance stated exactly as `0.0003693` (`0.39346933 - 0.0003693 = 0.39310003`, rounded to `q = 0.3931`), also below the four-moment Bonferroni bound `151/384 = 0.3932292` (9.3); the same value as cryptogakusei's `4888e783`. The toy-field range at `p = 1,048,627` (down to `0.39214`) lies within the deviation scale `1.36/sqrt(p) = 0.00133` of the law; at the Pallas prime that scale is below `2^-126`, far inside the allowance `0.0003693`. The extrapolation, the monodromy theorem at N = 2, 3 and the toy-field and organizer-run evidence are in the claim.json heuristic `H-ONE` and sections 10.3, 10.5.1.

### 9.2 The success bound
The `K = 1` centre is a fresh draw. For a centre `c` let `E_c` be the event `1 <= k(c) <= DMAX` (H-ONE, `P(E_c) >= q = 0.3931`) and `N_c` the event that the remainder sequence of `(g_c, R_c - 1)` is normal down to its gcd (H-NORMAL, 9.5, `P(not N_c) <= delta = 0.001`). The value-domain stage C reproduces `R = S^((p-1)/2) mod g` exactly, in closed form from coset distinctness with no premise (4.3V), so it adds no allowance (`delta_C = 0`). If `E_c` and `N_c` hold, stages C and D run to their end and return `G = gcd(g_c, R_c - 1)`; a successful isolation then ends in a verified collision. For `c` uniform `P(E_c and N_c) >= q - delta`, so with the one centre

`success = 1 - (1 - q + delta)^K - K (eps_coin + eps_iso) = q - delta - eps_coin - eps_iso`, `K = 1`.

With `q = 0.3931`, `delta = 0.001`, `eps_iso < 2^-48`, `eps_coin < 2^-122` (4.1.1): `q - delta = 0.3921`, and the value the formula gives with the stated eps bounds is `0.392099999999996447 >= 0.39` (`0.3921` with `eps = 0`). The bound stays at or above `0.39` for every `delta <= 0.0030999` (`q - 0.39 - eps_coin - eps_iso`), above the stated `delta = 0.001`; the delta stated in H-NORMAL (9.5) is the delta used here.

### 9.3 Monodromy (support for H-ONE)
The roots of `G(c,t) = g_c(t^2)` come in pairs `+-t_i`, so the monodromy lies in the hyperoctahedral group `B_m` and `k(c)` counts positive Frobenius fixed points; for `B_m` this is Poisson(1/2) in the limit, `P(k >= 1) = 1 - e^(-1/2) = 0.3934693`, and Bonferroni at order 4 gives `P >= 151/384 = 0.3932292`. A theorem at two and three layers (Aubry-Perret, monodromy `B_12`, `B_62`); false for permutation polynomials, for decomposable `F` with imprimitive monodromy, and at one layer.

### 9.4 Isolation lemma
With `1 <= deg G <= 16`, a random-shift split isolates a linear factor within `Z = 64` rounds except with probability `eps_iso < 2^-48`. Finite derivation (ruling `d2f0cc3d`, F-ISOLATION-BOUND; the derivation accepted on our r = 4 entry after ruling `044e6b33`): `G` divides both `g_c` and `S^((p-1)/2) - 1`, so it is squarefree and splits into `d = deg G <= 16` distinct linear factors `X - t_i` over `F_p`. A round with shift `a` keeps a nontrivial part of the current factor `H` under `gcd(H, (X + a)^((p-1)/2) - 1)` (or `X + a` itself when `a = -t_i`), so two roots `t_i != t_j` stay together only if `chi(t_i + a) = chi(t_j + a)` or `a` is in `{-t_i, -t_j}`. Since `sum_a chi((a + t_i)(a + t_j)) = -1` for `t_i != t_j`, exactly `(p - 3)/2` shifts give equal nonzero characters, so for `a` uniform on `F_p` the pair stays together with probability at most `((p - 3)/2 + 2)/p = 1/2 + 1/(2p)`; each shift is a fresh random word reduced mod `p`, within statistical distance `2^-128.9` of uniform (4.1.1), so per round the bound is `1/2 + 1/(2p) + 2^-128.9 < 1/2 + 2^-127`, independently across rounds. The parts are nested, so the factor kept after 64 rounds holds two roots only if one of the at most `C(16,2) = 120` pairs was never separated in 64 rounds. By the union bound `eps_iso <= 120 (1/2 + 2^-127)^64 < 6.6e-18 < 2^-48 = 3.55e-15`; the looser stated value `2^-48` is kept, so every other number is unchanged.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries `e6dcb600` and `1aa56884`, with the allowance and the organizer-run tests of gta6rp's entry `bef31fdd`)
**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(g_c, R_c - 1)`, where `g_c` is the monic odd part of section 3 (degree `m = 15,258,789,062`) and `R_c = S^((p-1)/2) mod g_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.001` (`2^-9.966`). Stage D is charged for the normal sequence; every division tests its quotient degree and every call of the half-gcd its return, and on any other case the trial ends (ABORT, sections 4.4, 6.3). The premise enters only the success probability (9.2): the time and memory bounds hold for every remainder sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work (6.3). For a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes, each a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-185`; the premise extrapolates a much weaker form of this random-pair behaviour (`delta = 0.001`) to the structured pair `(g_c, R_c - 1)`. Measured support is organizer-run (10.5.1): the experiments `euclid-normal-n2-t256-l2-a` to `-l2-f`, `euclid-normal-n3-t24` and `euclid-normal-n4-t2` compute the complete Euclidean sequence of `(g_c, R_c - 1)` for this construction on the truncations `F_2`, `F_3`, `F_4` (`m = 12, 62, 312`), the first six for 256 organizer-seeded trials of two centres each (3,072 sequences at `m = 12`), the others for 24 and 2 organizer-seeded centres, and return a witness pair exactly when the sequences are normal; the prediction is that every computed sequence is normal. Zero abnormal in the 3,072 sequences is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (`delta = 0.001` is the declared premise). Not verified at `r = 9`, which would need the computation itself; the organizer-run tests are at `m = 12` to `312`, far below `m`.

## 10. Experiments

Program `experiments/exp_euclid.py` (euclid-normal) and `experiments/exp_line.py` / `experiments/exp_lowbits.py` (line-ladder and lowbits-birthday), with `experiments/manifest.json`.

10.3 The truncations. `F_N(c + X)` is coordinate 0 after the first `N` S-box layers on the line `j = 0`; `F_2`, `F_3`, `F_4` have odd parts of degree `m = 12, 62, 312`. The arithmetic monodromy at `N = 2, 3` is `B_12`, `B_62` (Grok jobs 136, 137, re-run on the deployed constants).

10.5.1 Organizer-run set. euclid-normal-n2-t256-l2-a to -l2-f / -n3-t24 / -n4-t2 compute the complete Euclidean sequence of `(g_c, R_c - 1)` for this construction at depth `N = 2, 3, 4` (`m = 12, 62, 312`); the first six run 256 organizer-seeded trials of two centres each (3,072 sequences at `m = 12`), the others 24 and 2 organizer-seeded centres, and return a witness pair exactly when the sequences are normal; the prediction (H-NORMAL, 9.5) is that every computed sequence is normal, so all 6 x 256, 24 and 2 trials return a pair and the abnormal count is zero in the 3,072 sequences, a reproducible observation consistent with the premise. We do not treat the organizer-seeded centres as independent unselected samples and draw no population bound from these runs: `delta = 0.001` is the declared premise (9.5), carried by its stated support, not by an interval computed from the experiments. line-ladder-w6/-w8/-w10/-w12 and lowbits-birthday corroborate the antipodal structure (random-function model), not the score-critical basis. The organizer-checkable output is the returned witness-pair count (here the number of trials whose sequences are all normal). Our runs of the same program: 1,066 sequences at `m = 12, 62, 312`, every quotient of degree 1.

10.5.2 Organizer-counted good centres (H-ONE; ruling `710de924`, lane_experiments H-ONE). euclid-gcdpos-n2-t256-a, -b and euclid-gcdpos-n3-t24 take one organizer-seeded centre per trial at `N = 2, 3` (`m = 12, 62`), compute `G = gcd(g_c, R_c - 1)` (`deg G = k(c)`) and return a witness pair ONLY when `deg G >= 1`, so the organizer's returned-pair count is the good-centre count. Prediction: the expected count under H-ONE is `0.393469 T` for `T` trials (the law of 9.3, about `1 - e^(-1/2)`, a theorem at these depths): about 101 of 256 for each `N = 2` entry, about 9.4 of 24 for `N = 3`; the count is a reproducible observation consistent with the premise, with no interval inferred. Our runs of these three entries in the organizer container settings (1 CPU) on local seeds: 99 and 107 of 256 (12.5 s, 14.8 s) and 9 of 24 (15.5 s).

## Appendix E: rows C and D expanded, and the allocation walk of one trial

Rows C and D and the arena of section 7 are exact counts of the algorithm of sections 4.2-4.5 at `r = 9`. E.1 and E.2 expand each row into its parts, each part a count from the dimensions of 4.3V and the half-gcd levels with the charges of 4.2; each table adds up exactly to its row. E.3 is the allocator of 4.2 run on every allocation and free of the trial in program order: the totals, the live-set peaks per stage, the two-ended-pool high-water mark, the slab classes, and the stage-D allocation/free trace against the high-water mark.

### E.1 Row C = 1,809,844,608,973,170

Row C is the sum of the steps of section 4.3V in the order the stage runs them:

| part of stage C | operations |
| --- | ---: |
| plans of the passes, the exponent, the tables (`30 K` constants, the `h` powers of omega, the kernel spectra), the group buffer, the zero-fill of `g` above `m`, the allocations of `R` | 1,463,073,409 |
| the Newton reciprocal of the reversed `g` to `ell` coefficients (doubling steps, transform products) | 5,890,961,253,121 |
| the product `q` (one product of `2 ell - 1` points), the zero fill of `rev(X^v P1)`, the reversal of `q` | 1,715,603,384,088 |
| `g` on `O1` and `O2` (chirp evaluation of the coefficient rows at the `2K` nodes, `2K` forward inner transforms) | 5,333,091,392,640 |
| the start residue on `O2` (`q` evaluated at the `K` nodes, `K` forward inner transforms, pointwise pass at 8) | 2,756,218,330,828 |
| the start residue to `O1` (one extension) | 3,837,506,395,610 |
| `-1/g` on `O1` by batch inversion (auxiliary array of `h`, zero tests) | 225,687,415,057 |
| the squaring steps (step 6; below) | 1,777,090,220,447,928 |
| leaving the Montgomery form (pointwise passes at 7 and 11, one extension), the frees | 4,124,396,794,440 |
| two interpolations (inverse inner transforms, interpolation at the `K` nodes): `R` and `g` in coefficient form, the frees, the closing control | 8,869,460,485,049 |
| stage bookkeeping (entry, exit) | 1,000 |
| **row C** | **1,809,844,608,973,170** |

The squaring steps: `177` steps with exponent bit 0 and `45` with bit 1, `177 * 7,992,504,831,844 + 45 * 8,053,708,115,812 = 1,777,090,220,447,928`. One step is (i) the pointwise pass at 8 on `O1`, (ii) one extension, (iii) the pointwise pass at 12 on `O2` (16 for bit 1), (iv) one extension, and 20 for the step:

| part of one step | operations |
| --- | ---: |
| pointwise pass at 8 (`K h` points) | 128,144,378,318 |
| two extensions, 3,837,506,395,610 each | 7,675,012,791,220 |
| pointwise pass at 12 (bit 0) / 16 (bit 1) | 189,347,662,286 / 250,550,946,254 |
| step control | 20 |
| **one step, bit 0 / bit 1** | **7,992,504,831,844 / 8,053,708,115,812** |

One extension (`K = 114` cosets of `h = 2^27` points): `K` inverse inner transforms `1,037,756,747,042`, the between-coset Lagrange convolutions of length `256` over the `h` positions `1,761,992,902,210`, `K` forward inner transforms `1,037,756,746,358`; the inner transforms of `2^27` points run the passes `4, 4, 4, 5, 5, 5` (top-down) in the block form of 4.2.

### E.2 Row D = 1,007,839,492,582,635

The Euclid driver of 4.4 makes 32 repetitions, each one half-gcd call on the current pair with `k = min(ceil((n+1)/2), 3*2^29)`, then one division with the quotient and return tests; below degree `192` the classical Euclid runs 139 steps.

| repetition | operand lengths | k | half-gcd charge (whole subtree) | repetition total (with the division and tests) |
|---:|---:|---:|---:|---:|
| 1 | 15,258,789,063, 15,258,789,062 | 1,610,612,736 | 113,480,684,074,041 | 113,685,406,721,931 |
| 2 | 13,648,176,326, 13,648,176,325 | 1,610,612,736 | 111,629,311,570,325 | 111,809,875,027,160 |
| 3 | 12,037,563,589, 12,037,563,588 | 1,610,612,736 | 109,777,939,066,609 | 109,934,343,332,389 |
| 4 | 10,426,950,852, 10,426,950,851 | 1,610,612,736 | 107,926,566,562,908 | 108,058,811,637,633 |
| 5 | 8,816,338,115, 8,816,338,114 | 1,610,612,736 | 106,075,194,059,207 | 106,183,279,942,877 |
| 6 | 7,205,725,378, 7,205,725,377 | 1,610,612,736 | 104,223,821,555,477 | 104,307,748,248,092 |
| 7 | 5,595,112,641, 5,595,112,640 | 1,610,612,736 | 102,372,449,051,747 | 102,432,216,553,307 |
| 8 | 3,984,499,904, 3,984,499,903 | 1,610,612,736 | 100,521,076,548,059 | 100,556,684,858,564 |
| 9 | 2,373,887,167, 2,373,887,166 | 1,186,943,583 | 78,858,257,128,287 | 78,876,061,285,032 |
| 10 | 1,186,943,583, 1,186,943,582 | 593,471,791 | 37,967,500,649,111 | 37,976,402,728,976 |
| 11 | 593,471,791, 593,471,790 | 296,735,895 | 18,000,821,920,159 | 18,005,272,961,584 |
| 12 | 296,735,895, 296,735,894 | 148,367,947 | 8,493,091,949,488 | 8,495,317,471,693 |
| 13 | 148,367,947, 148,367,946 | 74,183,973 | 3,995,604,173,365 | 3,996,716,935,960 |
| 14 | 74,183,973, 74,183,972 | 37,091,986 | 1,876,589,524,611 | 1,877,145,907,401 |
| 15 | 37,091,986, 37,091,985 | 18,545,993 | 876,808,302,009 | 877,086,494,889 |
| 16 | 18,545,992, 18,545,991 | 9,272,996 | 410,329,714,778 | 410,468,812,703 |
| 17 | 9,272,995, 9,272,994 | 4,636,497 | 191,297,362,494 | 191,366,912,949 |
| 18 | 4,636,497, 4,636,496 | 2,318,248 | 88,980,962,893 | 89,015,739,613 |
| 19 | 2,318,248, 2,318,247 | 1,159,124 | 41,101,522,700 | 41,118,912,545 |
| 20 | 1,159,123, 1,159,122 | 579,561 | 19,022,982,516 | 19,031,678,931 |
| 21 | 579,561, 579,560 | 289,780 | 8,758,135,038 | 8,762,484,738 |
| 22 | 289,780, 289,779 | 144,890 | 4,018,950,609 | 4,021,126,944 |
| 23 | 144,889, 144,888 | 72,444 | 1,825,912,931 | 1,827,002,591 |
| 24 | 72,444, 72,443 | 36,222 | 831,555,061 | 832,101,376 |
| 25 | 36,221, 36,220 | 18,110 | 375,688,977 | 375,963,627 |
| 26 | 18,110, 18,109 | 9,055 | 168,810,342 | 168,949,152 |
| 27 | 9,054, 9,053 | 4,527 | 74,655,469 | 74,726,359 |
| 28 | 4,526, 4,525 | 2,263 | 33,084,858 | 33,121,788 |
| 29 | 2,262, 2,261 | 1,131 | 14,443,602 | 14,463,552 |
| 30 | 1,130, 1,129 | 565 | 6,235,933 | 6,247,393 |
| 31 | 564, 563 | 282 | 2,593,714 | 2,600,929 |
| 32 | 281, 280 | 140 | 1,058,977 | 1,064,077 |

| part of row D | operations |
| --- | ---: |
| the 32 repetitions above | 1,007,839,492,016,755 |
| the classical Euclid below degree 192 (139 steps, quotient test each) | 561,997 |
| driver entry | 6 |
| driver exit (free, inversion of the leading coefficient, normalisation) | 2,758 |
| stage bookkeeping (entry, exit, the free of `g`) | 1,119 |
| **row D** | **1,007,839,492,582,635** |

### E.3 Totals and the allocation walk of one trial

```
m = 15,258,789,062 | transform sizes 256 134217728 | squaring steps 222 of which with S: 45
S_C = 1,809,844,608,973,170
S_D normal local charges of the tree = 1,007,839,492,582,635
S_D of the lean stage D on the normal remainder sequence, with the quotient and return tests = 1,007,839,492,582,635
S_D = 1,007,839,492,582,635
peak of the live set, stage A = 558,345,748,608 bytes
peak of the live set, stage B = 1,176,821,039,296 bytes
peak of the live set, stage C = 2,035,827,246,528 bytes
peak of the live set, stage D = 1,769,526,527,168 bytes
two-ended pool: blocks of more than 2^24 bytes; largest sum of the two ends after each stage (bytes): init 68,719,476,800, A 558,345,748,608, B 1,176,821,039,296, C 2,035,814,651,200, D 2,035,814,651,200; at most 91 blocks; 21,931,392 blocks examined in all
slab classes (class: peak number of live blocks): 7: 24, 8: 2, 9: 1, 12: 11, 13: 11, 14: 20, 15: 13, 16: 20, 17: 20, 18: 20, 19: 13, 20: 20, 21: 20, 22: 20, 23: 13, 24: 20; slab area = 608,280,576 bytes
arena = 2,036,422,948,800 bytes (two-ended pool 2,035,814,651,200 + 128, slab classes 608,280,576, stages E and later 16,896), memory = 2,036,428,264,780 bytes, log2 = 40.890
stage D on the two-ended pool (blocks of more than 2^24 bytes): after init, A, B, C: low end 558,345,748,608, high end 489,626,271,808, live 1,047,972,020,416, largest sum so far 2,035,814,651,200
  stage D: 2,102,726 pool events (1,051,362 allocations, 1,051,364 frees) on 1,051,365 distinct blocks; the first 24:
  alloc #4               25,165,888 bytes pool L | live  1,047,997,186,304 | pool low    558,370,914,496 high    489,626,271,808 sum  1,047,997,186,304
  alloc #5               25,165,888 bytes pool L | live  1,048,022,352,192 | pool low    558,396,080,384 high    489,626,271,808 sum  1,048,022,352,192
  alloc #6               16,777,280 bytes pool L | live  1,048,039,129,472 | pool low    558,412,857,664 high    489,626,271,808 sum  1,048,039,129,472
  alloc #7               16,777,280 bytes pool L | live  1,048,055,906,752 | pool low    558,429,634,944 high    489,626,271,808 sum  1,048,055,906,752
  alloc #8               16,777,280 bytes pool L | live  1,048,072,684,032 | pool low    558,446,412,224 high    489,626,271,808 sum  1,048,072,684,032
  alloc #9               16,777,280 bytes pool L | live  1,048,089,461,312 | pool low    558,463,189,504 high    489,626,271,808 sum  1,048,089,461,312
  alloc #10              16,777,280 bytes pool L | live  1,048,106,238,592 | pool low    558,479,966,784 high    489,626,271,808 sum  1,048,106,238,592
  alloc #11              16,777,280 bytes pool L | live  1,048,123,015,872 | pool low    558,496,744,064 high    489,626,271,808 sum  1,048,123,015,872
  alloc #12              16,777,280 bytes pool L | live  1,048,139,793,152 | pool low    558,513,521,344 high    489,626,271,808 sum  1,048,139,793,152
  free  #4               25,165,888 bytes pool   | live  1,048,114,627,264 | pool low    558,513,521,344 high    489,626,271,808 sum  1,048,139,793,152
  free  #5               25,165,888 bytes pool   | live  1,048,089,461,376 | pool low    558,513,521,344 high    489,626,271,808 sum  1,048,139,793,152
  free  #6               16,777,280 bytes pool   | live  1,048,072,684,096 | pool low    558,513,521,344 high    489,626,271,808 sum  1,048,139,793,152
  free  #7               16,777,280 bytes pool   | live  1,048,055,906,816 | pool low    558,513,521,344 high    489,626,271,808 sum  1,048,139,793,152
  free  #8               16,777,280 bytes pool   | live  1,048,039,129,536 | pool low    558,513,521,344 high    489,626,271,808 sum  1,048,139,793,152
  free  #9               16,777,280 bytes pool   | live  1,048,022,352,256 | pool low    558,513,521,344 high    489,626,271,808 sum  1,048,139,793,152
  free  #10              16,777,280 bytes pool   | live  1,048,005,574,976 | pool low    558,513,521,344 high    489,626,271,808 sum  1,048,139,793,152
  free  #11              16,777,280 bytes pool   | live  1,047,988,797,696 | pool low    558,513,521,344 high    489,626,271,808 sum  1,048,139,793,152
  free  #12              16,777,280 bytes pool   | live  1,047,972,020,416 | pool low    558,345,748,608 high    489,626,271,808 sum  1,047,972,020,416
  alloc #13              16,777,280 bytes pool L | live  1,047,988,797,696 | pool low    558,362,525,888 high    489,626,271,808 sum  1,047,988,797,696
  alloc #14              16,777,280 bytes pool L | live  1,048,005,574,976 | pool low    558,379,303,168 high    489,626,271,808 sum  1,048,005,574,976
  alloc #15              16,777,280 bytes pool L | live  1,048,022,352,256 | pool low    558,396,080,448 high    489,626,271,808 sum  1,048,022,352,256
  alloc #16              16,777,280 bytes pool L | live  1,048,039,129,536 | pool low    558,412,857,728 high    489,626,271,808 sum  1,048,039,129,536
  alloc #17              16,777,280 bytes pool L | live  1,048,055,906,816 | pool low    558,429,635,008 high    489,626,271,808 sum  1,048,055,906,816
  alloc #18              16,777,280 bytes pool L | live  1,048,072,684,096 | pool low    558,446,412,288 high    489,626,271,808 sum  1,048,072,684,096
  the 0 events that raise the high-water mark (the last 0 shown; event number first):
  after stage D: low end 68,719,476,800, high end 0; high-water mark of the pool over the trial 2,035,814,651,200 bytes
```
