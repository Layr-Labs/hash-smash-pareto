# Orchard Poseidon, r = 9: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, inversion-free half-gcd on three rows, one centre, 64-register passes

## 1. Claim

Target: `poseidon-orchard-r9-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, nine partial rounds 4, 5, 6, 7, 8, 9, 10, 11 and 12, full rounds 60-63, state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is an algorithm (sections 2-4) with an operation count that bounds every run (sections 6-7) and a success probability derived from two score-critical premises, `H-ONE` (section 9.1, a statement about the fraction of centres at which the fixed digest polynomial has between 1 and 16 usable roots) and `H-NORMAL` (section 9.5, the normality of the remainder sequence, allowance `delta = 0.001`); section 9.2 derives the success probability from them. Stage D is charged for the normal remainder sequence with the ABORT on any other case (section 6.3), so the time and memory bounds use no premise on the sequences.

* The algorithm: draw a centre `c` uniformly from `F_p` from fresh random words, build the odd part `g_c` of the line polynomial by evaluation and one inverse transform, compute `R = S^((p-1)/2) mod g_c` in the value domain on `K_cos = 114` cosets of size `h = 2^27` (bradcush `4bcabff8`; every transform pass in the block form of the declared 64-word register file, 4.2), take `G = gcd(g_c, R - 1)` by the inversion-free half-gcd on three rows of bradcush `4bcabff8` (outer step `k = 2^j - 1 <= 2^30 - 1`, each matrix applied to the whole pair in place by the block products of the memory cap of weijiekoh `a78f526e`, applies longer than `3 * 2^31` coefficients in blocks of length `3 * 2^28`, section 4.4), charged for every remainder sequence, and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` in at most `Z = 64` rounds, take its square root, map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; the trial runs to its end or ABORTs stage D on an abnormal remainder sequence (6.3), when the allocator is reset and the run ends without output; a verified collision ends the algorithm.
* `success_probability = 0.392099999999996447`: a lower bound for the probability, over the algorithm's fresh random words, that the centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta)^K - K (eps_coin + eps_iso) = q - delta - eps_coin - eps_iso` with `q = 0.3931` (the premise `H-ONE`, section 9.1), `delta = 0.001` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `K = 1`, `eps_iso < 2^-48`, `eps_coin < 2^-122` (sections 4.1.1, 9.2). The value the formula gives with those eps bounds is `0.392099999999996447` (at or above the organizer floor 0.39).
* `time_log2 = 42.28584` in target-compression units (`C(9) = 405` primitive operations per unit): the operation count that bounds every run, derived in section 6 as `T_fixed + K * T_trial + T_off` with `K = 1`, stage C in the value domain (4.3V), stage D the inversion-free half-gcd on three rows charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (4.4, 6.3; the time bound holds for every sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work), and stage E at its cap of `Z` rounds at degree `DMAX`. `N_max = 2,171,492,330,994,183` operations, `log2(N_max / 405) = 42.28583...`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is bounded by 1,000,000 operations; that bound is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 40.889` (`2,036,146,290,252` bytes, section 7). The normalized cost is `42.28584 + max(0, 40.889 - 20) = 42.28584 + 20.889 = 63.17484`.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; `65` words at most (section 4.1.1), and a draw (one word) costs 31 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^15`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Against our filed r = 9 entry `43f8d8b8` (normalized cost 63.56345, the same algorithm and package), two changes: (i) the loads and stores of the data words of the transform-pass blocks are charged one operation each, base plus index (4.2; the wording of the accepted `89b451ff` and `070a02b2`); (ii) the outer steps of stage D run bradcush's inversion-free half-gcd on three rows (entry `4bcabff8`; the transform reuse of `b30de9bf`), as in our r = 3 entry `bcf8e01c`, ported to `r = 9` and charged in this cost model (section 4.4), in place of the lean cofactor-free node of bradcush `e6dcb600`/`1aa56884`. Row C `1,581,734,815,658,178` (was `1,809,844,608,973,170`), row D `566,624,691,718,081` (was `1,007,839,492,582,635`); arena `2,036,140,974,272` bytes (was `2,036,422,948,800`), the high-water mark of one trial still reached in stage C (section 7). Every other charge, the premises and the experiments are unchanged.
* Prior entry: this entry is our filed r = 9 entry `b0ee9e30` (normalized cost 63.83088) with one change: the transforms run on the 64-register machine stated as a restriction in claim.json, as in our r = 3 entries `ef123c2b`/`253629b9`: every transform pass (the inner transforms of stage C, the products of stages C and D) runs blocks of `2^k` points with the `2^k - 1` twiddles of its group in registers, and the inner transforms of `2^27` points run the passes `4, 4, 4, 5, 5, 5` (4.2, 4.3V). Stage C falls from `2,233,950,532,573,330` to `1,809,844,608,973,170` operations and stage D from `1,162,288,107,277,055` to `1,007,839,492,582,635`; the memory is unchanged. `b0ee9e30` is our entry `e76bdab0` with four changes under the same cost model: (i) stage C computed in the value domain on cosets (section 4.3V, the method of bradcush `4bcabff8`); (ii) stage D the lean cofactor-free half-gcd charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, the premise `H-NORMAL` of bradcush (entries `e6dcb600`, `1aa56884`) in the organizer-run form of gta6rp (entry `bef31fdd`) (sections 4.4, 6.3, 9.5, 10.5.1); (iii) the success allowance split between the two premises as in cryptogakusei's entry `4888e783`: `H-ONE` at `q = 0.3931` (9.1) and `H-NORMAL` at `delta = 0.001` (9.5), so one centre (`K = 1`) clears the floor (9.2); (iv) the stage-D memory cap of weijiekoh's entry `a78f526e` (outer half-gcd step `k <= DMAX`, long applies by in-place block products), ported into this program and charged in this cost model (4.4, 7). The per-trial rows A, B, E, F, G and the evidence are the same family; the memory is the actual allocator high-water mark of one trial (section 7).
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1), a statement about the fraction of good centres, and `H-NORMAL` (score-critical for the success probability only, section 9.5), bradcush's premise on the normality of the remainder sequence stated with the allowance `delta = 0.001` and supported by organizer-run tests (gta6rp's recipe, entry `bef31fdd`). Both are statements about probability. The machine (64 registers of 256 bits and constants as immediates; every load, store and spill counted) is stated as a restriction in claim.json, as the accepted entries `89b451ff` and `fb176310` state theirs, not as a heuristic (4.2). The costs are the declared cost model of this entry, not heuristics: the charging rules of section 4.2 with that register file, the inversion-free half-gcd of stage D with the in-place applies of the memory cap charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (Appendix E). Everything else is proved or counted here.

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
  D  G := gcd(g, R - 1) (monic): the inversion-free half-gcd on three rows with the in-place applies of the memory cap, charged for every remainder sequence (section 4.4), by the normal-sequence trace with the quotient and return tests (6.3)
  E  if deg G = 0 or deg G > DMAX: trial ends. Otherwise isolate a root S of G (4.1.2); if none within Z = 64 rounds: trial ends.
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (405 operations each) are equal and the pairs differ -> output; otherwise the trial ends
```

4.1.1 Coins. The only randomness is the cost-model random-word primitive. The words are fresh, independent and uniform on `[0, 2^256)`. A centre is `c = w mod p` for one word `w` (at most three conditional subtractions); the isolation of stage E draws at most 64 further words, reduced the same way. At most 65 words per run; a draw is 31 operations. There is no rejection and no retry. The reduction is not exactly uniform on `F_p`: `2^256 = 3p + r` with `0 < p - r = 4(p - 2^254) < 2^127.1`, so every residue has 3 or 4 preimages and `w mod p` is within statistical distance `r (p - r) / (p 2^256) < 2^-128.9` of uniform on `F_p`. Over the 65 words the distance is `eps_coin <= 65 * 2^-128.9 < 2^-122`, and the success bound (9.2) subtracts it.

4.1.2 Stage E: isolating a root of `G`. With `1 <= deg G <= DMAX = 16`, a Cantor-Zassenhaus split with random shifts isolates one linear factor in at most `Z = 64` rounds at degree `<= 16`; `eps_iso < 2^-48` bounds the probability that 64 rounds fail to isolate a root when `deg G >= 1` (section 9.4).

### 4.2 Machine model and charging rules (summary; `C(9) = 405`)

Every field operation, load, store, control operation and random word is one primitive operation; `C(r) = 216 + 21 r = 405` primitive operations is one target-compression unit. The register file is 64 words of 256 bits (the machine restriction of claim.json: it holds the 16 values and 15 twiddles of a radix-16 block, or the 32 values and 28 of the 31 twiddles of a radix-32 block; every other value, the 3 spilled twiddles of a radix-32 group included, is charged as a load or store; a load or store of a data word of a block of a transform pass is one operation, its address the base plus index of the load or store itself: one load per word fetched from memory and one store per word written, the wording of the accepted entries `89b451ff` and `070a02b2`), the only register assumption. Every transform pass of `k` layers at level `l0` of a `2^a`-point transform runs `2^(a-k)` blocks of `2^k` points, each `2^k` loads and `2^k` stores at one operation each (base plus index), `k 2^(k-1)` butterflies at 3 and 5 control (`2 * 2^k + 3 k 2^(k-1) + 5`; radix 32 adds 6 for the loads of its 3 spilled twiddles), and `2^l0` groups, each forming its `2^k - 1` twiddles once in registers from the twiddle table (radix 16: two loads of two words, one multiplication, three squarings, eleven multiplications by register constants and 5 control, 24; radix 32: 42 with the stores of the 3 spilled twiddles; `k <= 3`: 16), plus `9 k + 19` per forward pass and `9 k + 20` per inverse pass; the algorithm runs on one thread, no dispatch. Allocation: one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes. A block of more than `2^24` bytes is served by the two-ended pool (one region, two ends, first-fit in address order, the statements marked `# pool:H` using the high end and, with the depth-parity placement of section 7, the end `(j + bit8) mod 2` of a half-gcd node at depth `j`); every smaller block by its slab class (the least `j >= 7` with `2^j >= need`, a slot of `2^j` bytes). The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows (a pool request `97` operations besides the walk and `13` per block examined, a slab request at most `126`, a free `81` for a slab block and at most `105` for a pool block). The memory of both allocators is the arena of section 7.

### 4.3V Stage C in the value domain, on cosets of a subgroup of order `h = 2^27` (the method of bradcush `4bcabff8`)

The residue `R = S^((p-1)/2) mod g` is carried by its values on `K_cos = 114` cosets `5^k H`, `k = 0..K_cos-1`, of the subgroup `H` of order `h = 2^27` (the extension uses the `2 K_cos = 228` cosets `5^0 H, ..., 5^(2 K_cos - 1) H`). The cosets are distinct because `5^(d h) != 1` for `1 <= d <= 2 K_cos - 1` and `ord(5^h) = (p-1)/h >= 2 K_cos`; `h | p - 1`; and `n1 = K_cos h = 15,300,820,992 >= m + 1`. A squaring step is a pointwise square on the current point set plus one change of point set (an extension) built from `2 K_cos` inner transforms of `h` points and a between-coset Lagrange convolution of length `Lx = 256` (the smallest `2^a` or `3*2^a` that is at least `2 K_cos`); the start monomial is `S^v`, `v = 2^31 = 2,147,483,648` a multiple of `h` (VSHIFT = 2). There are `222` squaring steps, `45` of them also multiplying by `S` (a streaming shift). The evaluation of `q` uses `Kq = 17` rows and a convolution of length `Lq = 192`; the chirp evaluation of `g` at the `2 K_cos` nodes uses a convolution of length `Le = 384`. The equality of the value-domain and coefficient-domain residue is exact (it composes exact inner transforms with the exact Lagrange interpolation of polynomials of degree `< K_cos` from `K_cos` distinct nodes); no premise is added. `g` and `R` are held whole (one array each; the top-node pieces of bradcush's lemma 4.8(b) are not used). The inner transforms of `h = 2^27` points run the passes `4, 4, 4, 5, 5, 5` (top-down; the cheapest order under the 64-word register file, 4.2). The step-by-step operation count is expanded in Appendix E.1 (where `K_cos` is `K`) and totals **row C = 1,581,734,815,658,178** (section 6).

### 4.4 Stage D: the inversion-free half-gcd on three rows (bradcush `4bcabff8`), with the in-place applies of the memory cap, charged for every remainder sequence

`G = gcd(g, R - 1)` is computed by bradcush's inversion-free half-gcd (entry `4bcabff8`, with the transform reuse of `b30de9bf`; read as text only, ported and charged in this cost model as in our r = 3 entry `bcf8e01c`). Matrices and remainders are kept up to nonzero scalars with pseudo-division (`b^2 a = Q b + e`, `Q` of degree 1 on the normal sequence), so no field inversion runs inside the recursion; the gcd is the same up to a scalar and is made monic at the end. A node of budget `k = 2^j - 1` makes two child calls of budget `2^(j-1) - 1`; its products run on `3 * 2^(j-1)` points, the rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), each a power-of-two transform of `n` points in the block form of 4.2 after a twist, joined by a 3-row CRT: `(c, d) = adj(M1)(a, b)` on the top window, the pseudo-division, and `M = M1 [[Q, 1], [b^2, 0]] M2`; the row `Y - 1` values of each child's matrix are returned by the child, and the row values of `M1` are kept from the apply and reused in the product. The twist roots of order `2n` and `4n` (`4n <= 2^31`, so they exist in `F_p`) come from the squaring chain of the running twiddle factors of the row transform (4.2); the scales `1/2^a` (`a <= 29`) are a table of 29 words built at the entry of stage D (`1/2 = (p + 1)/2` an immediate, 28 multiplications). The base case (budget 63) runs two remainder steps per pass over its window.

Driver: while `(n - 1)/2 >= 127`, one outer step calls the node on the top window of the pair with `k = 2^j - 1` the largest with `k <= min(2^30 - 1, (n - 1)/2)` (below the outer cap `DMAX = 3 * 2^29` of weijiekoh `a78f526e`), applies `adj(M)` to the whole pair in place, and makes one division with the quotient test; the apply is that of the memory cap (the method of weijiekoh `a78f526e`, its `mat_apply` LMAX, as in `43f8d8b8`): an apply to a pair longer than `LMAX = 3 * 2^31 = 6,442,450,944` coefficients is done by the block products of section 4.5 at the block length `3 * 2^28 = 805,306,368` (transforms of `3 * 2^29` points), each block of the operands transformed once, the transforms of a slot multiplied pointwise and summed, and each output slot inverse transformed and overlap-added in place into the output array. The last outer step (degree below `255`) is the lean cofactor-free half-gcd of bradcush `e6dcb600`/`1aa56884` as in `43f8d8b8`, and below degree `192` classical division steps finish. The working arrays of a node live in one bump arena (an allocation or release is 10 operations) of `17,179,868,928` words at `j = 30`, the peak of its recursion; the cap `j <= 30` keeps the arena and the pair below the stage-C peak (section 7). The caps are constants of the algorithm; on the normal sequence every length, budget and allocation is a function of `m` alone.

The row is charged for the normal remainder sequence (every quotient of degree 1), the case of the premise `H-NORMAL` (9.5): every division and pseudo-division tests that its quotient has degree 1 and every call tests on return that it removed exactly its budget (2 operations each), and a zero remainder also ends the trial; on any other case the trial ABORTs (the allocator is reset and the run ends without output, section 6.3). By the prefix lemma of 6.3 every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, so the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The total is **row D = 566,624,691,718,081** (section 6.3, 6; Appendix E.2).

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
| C (per trial) | `S^((p-1)/2) mod g` in the value domain, `K_cos = 114` cosets of size `h = 2^27`, VSHIFT = 2, passes in block form (sections 4.2, 4.3V); expanded in Appendix E | 1,581,734,815,658,178 |
| D (per trial) | inversion-free half-gcd of `(g, R - 1)` on three rows with the in-place applies of the memory cap, charged for every remainder sequence (section 4.4): the normal-sequence trace with the quotient and return tests (6.3), passes in block form (4.2); expanded in Appendix E | 566,624,691,718,081 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16` | 166,079,773 |
| F (per trial) | square root, back-map | 47,012 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 405 + 32` | 9,132 |
| trial-loop (per trial) | trial-loop bookkeeping and the allocator reset after an ABORT, charged in every trial | 1,012 |
| plan_invN misses | one per distinct plan size | 160,628 |
| output rows | the fixed output rows | 3,390,080 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + T_trial + T_off` | **2,171,492,330,994,183** |

`T_off = 1,000,000`; `T_trial = A + B + C + D + E + F + G + trial-loop = 2,171,475,146,551,273` (the trial-loop row is the trial-loop bookkeeping and the allocator reset after an ABORT, charged in every trial); `T_fixed = init + setup + plan_invN misses + output rows = 17,183,442,910`; `K = 1`, so `N_max = 17,183,442,910 + 2,171,475,146,551,273 + 1,000,000 = 2,171,492,330,994,183`. `log2(N_max / 405) = 42.28583...`, rounded up at five decimals to `42.28584`. Rows C and D are expanded part by part in Appendix E (E.1, E.2) from the dimensions of 4.3V and the half-gcd levels with the kernel charges of 4.2; the parts add up exactly to `1,581,734,815,658,178` and `566,624,691,718,081`.

### 6.1 Validation
The worst-case counts are derived by formula and compared with the instrumented totals of our executed runs at `r = 3, 4, 5`; the arena rule (the heap peak of the allocation walk) is within 64 bytes of the measured heap peaks there.

### 6.2 Offline derivation
The literals of the sources (Montgomery forms of the organizer constants, `5^q`, `2^65`, the exponent `(4(p-1)+1)/5`) are derived offline in at most `1,000,000` operations, declared `preprocessing_log2 = 20` and inside `N_max`.

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry `e6dcb600`)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g_c, R_c - 1)`: every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the re-centring division of a node, the division of each repetition of the outer loop, each step of the base case) tests that its quotient has degree 1 (2 operations), before the division runs; (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); a zero remainder inside `hgcd` or in the outer-loop division also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state after the twiddle table (`1,000` operations, charged in the trial) and the run ends without output (`K = 1`). Lemma (prefix; `e6dcb600`, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each node of budget `2^j - 1` splits into two calls of budget `2^(j-1) - 1` (each lean call at `k1 = ceil(k/2)`) and, with every quotient of degree 1, every degree in the tree is fixed by `m` and the number of quotients so far, and the budgets of the outer loop (`k = 2^j - 1 <= min(2^30 - 1, (n - 1)/2)`, then `ceil((n+1)/2)`, section 4.4) are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's `hgcd` calls and divisions produce has degree at least the base-case bound, so every gcd of degree at most `DMAX = 16` first appears in the classical Euclid below the base-case degree, after a prefix of the degree-0 work; a zero remainder earlier ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The quotient test runs before each division, so the Newton (fast) division is never reached on the charged path and row D carries no fast-division or zero-scan term. The node follows `4bcabff8`, the lean call `1aa56884` proof 4.4 and the in-place applies `a78f526e` proof 4.4, all read as text only (no entry script was run, compiled or imported). Appendix E.2 expands, for `r = 9`, the charge of stage D for the normal sequence with the tests, `566,624,691,718,081`, repetition by repetition.

The `r = 9` trial (`~2.04 TB`, `~2.17e15` operations) exceeds the organizer sandbox (128 MiB, 20 s), so the costs are the exact formula counts of sections 6 and 7; zero-fill clearing is charged (ruling `3476cad8`) and the 64-word register file is the machine restriction of claim.json.

## 7. Memory: the arena of one trial

The arena is the capacity of the allocator of 4.2 on the allocation/free sequence of one trial (`K = 1`: the run is one trial). Appendix E.3 runs the allocator on every allocation and free of the trial in the order of the program and reports the two-ended-pool high-water mark (the largest sum of the extents of the two ends over the trial), the slab area and the peaks of the live set per stage. The two-ended pool takes the blocks of more than `2^24` bytes and is placed with depth-parity ends and in-place `R*Q` with two spare slots charged (the `POOL_PLACE = 20` discipline). Under the H-NORMAL ABORT stage D the stage-D live set holds the **normal-case division arrays**: on the normal sequence every quotient has degree 1, so each division forms only the quotient of two coefficients and the remainder, and a trial with any other sequence ends (ABORT) after a prefix of these allocations (6.3), so the normal-case walk bounds every trial. With the node arena of 4.4 (`j <= 30`) and the in-place applies of the memory cap the stage-D live peak is `1,958,505,089,152` bytes (the pair and the arena of the `j = 30` node), below the stage-C peak; the stage-D trace of Appendix E has no event that raises the pool's high-water mark. The high-water mark is `2,035,814,651,200` bytes, reached in stage C, plus 128 bytes so the unused middle is always at least 128 bytes. The slab classes take the smaller blocks: `326,306,048` bytes. Stages E and later hold at most 16 small arrays and the free-list heads: `16,896` bytes. The arena is `2,036,140,974,272` bytes (two-ended pool `2,035,814,651,200 + 128`, slab `326,306,048`, stages E and later `16,896`). Peaks of the live set per stage (bytes): A `558,345,748,608`; B `1,176,821,039,296`; C `2,035,827,246,528`; D `1,958,505,089,152`. With `5,250,444` bytes of code and static data and a `65,536`-byte stack, the footprint is `2,036,146,290,252` bytes `= 2^40.889`, rounded up at three decimals. No stored advice; the twiddle table is built at run time and charged in stage init.

## 8. Review points, answered by location

1. Row D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (6.3): by the prefix lemma every trial executes a prefix of the normal-case work, so the time and memory bounds hold for every sequence; `H-NORMAL` (9.5) enters only the success probability.
2. The node budget cap and the memory cap (4.4) are constants of the algorithm (`k = 2^j - 1 <= 2^30 - 1`, `LMAX = 3 * 2^31`, block length `3 * 2^28`); its extra transform work is charged in row D, and its effect on the memory is read from the allocation walk of Appendix E (stage-D peak `1,958,505,089,152` below the stage-C peak; no stage-D event raises the high-water mark).
3. Row B reproducible from sections 3 and 6 (evaluations * ops/unit + the 3 inverse transforms + the recombination + normalisation). The 64-word register file (the machine restriction of claim.json, 4.2) is the only register assumption; every value beyond it is charged as a load or store.
4. The 1,000,000-op offline figure is a declared bound (`preprocessing_log2 = 20`), score effect < 4e-7 bit.
5. The mem penalty uses the rounded-up `mem_log2` - a self-penalizing over-charge, deliberate.
6. Row D is the normal-sequence trace with the tests and nothing else: the quotient test runs before each division, so the Newton (fast) division is never reached on the charged path and no fast-division or zero-scan term is added (6.3; Appendix E.2 expands the row).
7. `success = 1 - (1 - q + delta)^K - K (eps_coin + eps_iso) >= 0.39` from the premises `H-ONE` and `H-NORMAL` (9.2, 9.5) with `K = 1`, `q = 0.3931`, `delta = 0.001`, i.e. `q - delta - eps_coin - eps_iso`; the value the formula gives with the stated eps bounds is `0.392099999999996447`, margin above 0.39 is `0.002099999999996447`. The delta stated in H-NORMAL (9.5) is the delta used here.
8. The stage-D memory peak holds the pair, the node arena and the normal-case division arrays (section 7, 6.3); an abnormal trial ABORTs after a prefix of these allocations.
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

### E.1 Row C = 1,581,734,815,658,178

Row C is the sum of the steps of section 4.3V in the order the stage runs them:

| part of stage C | operations |
| --- | ---: |
| plans of the passes, the exponent, the tables (`30 K` constants, the `h` powers of omega, the kernel spectra), the group buffer, the zero-fill of `g` above `m`, the allocations of `R` | 1,463,068,033 |
| the Newton reciprocal of the reversed `g` to `ell` coefficients (doubling steps, transform products) | 4,919,439,650,641 |
| the product `q` (one product of `2 ell - 1` points), the zero fill of `rev(X^v P1)`, the reversal of `q` | 1,432,135,542,552 |
| `g` on `O1` and `O2` (chirp evaluation of the coefficient rows at the `2K` nodes, `2K` forward inner transforms) | 4,759,713,258,624 |
| the start residue on `O2` (`q` evaluated at the `K` nodes, `K` forward inner transforms, pointwise pass at 8) | 2,469,529,263,820 |
| the start residue to `O1` (one extension) | 3,332,847,738,330 |
| `-1/g` on `O1` by batch inversion (auxiliary array of `h`, zero tests) | 225,687,415,057 |
| the squaring steps (step 6; below) | 1,553,021,776,615,608 |
| leaving the Montgomery form (pointwise passes at 7 and 11, one extension), the frees | 3,619,738,137,160 |
| two interpolations (inverse inner transforms, interpolation at the `K` nodes): `R` and `g` in coefficient form, the frees, the closing control | 7,952,484,967,353 |
| stage bookkeeping (entry, exit) | 1,000 |
| **row C** | **1,581,734,815,658,178** |

The squaring steps: `177` steps with exponent bit 0 and `45` with bit 1, `177 * 6,983,187,517,284 + 45 * 7,044,390,801,252 = 1,553,021,776,615,608`. One step is (i) the pointwise pass at 8 on `O1`, (ii) one extension, (iii) the pointwise pass at 12 on `O2` (16 for bit 1), (iv) one extension, and 20 for the step:

| part of one step | operations |
| --- | ---: |
| pointwise pass at 8 (`K h` points) | 128,144,378,318 |
| two extensions, 3,332,847,738,330 each | 6,665,695,476,660 |
| pointwise pass at 12 (bit 0) / 16 (bit 1) | 189,347,662,286 / 250,550,946,254 |
| step control | 20 |
| **one step, bit 0 / bit 1** | **6,983,187,517,284 / 7,044,390,801,252** |

One extension (`K = 114` cosets of `h = 2^27` points): `K` inverse inner transforms `854,146,895,138`, the between-coset Lagrange convolutions of length `256` over the `h` positions `1,624,553,948,738`, `K` forward inner transforms `854,146,894,454`; the inner transforms of `2^27` points run the passes `4, 4, 4, 5, 5, 5` (top-down) in the block form of 4.2.

### E.2 Row D = 566,624,691,718,081

The Euclid driver of 4.4 makes 50 repetitions. Repetitions 1-49: the inversion-free node of budget `k = 2^j - 1` (the largest with `k <= min(2^30 - 1, (n - 1)/2)`) on the top window, the apply of `adj(M)` to the whole pair in place, then one division with the quotient and return tests; `node` is the charge of the node (`pd_node(j) + 10`), `apply` that of the apply, the last column the repetition with the call, the matrix allocations, the arena, the division and the tests. Repetition 50 (`(n - 1)/2 < 127`) is the lean half-gcd of `43f8d8b8`; below degree `192` the classical Euclid runs 98 steps.

| repetition | operand lengths | j | k | node | apply | repetition total |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 15,258,789,063, 15,258,789,062 | 30 | 1,073,741,823 | 35,244,355,091,391 | 8,688,107,813,202 | 44,145,238,617,803 |
| 2 | 14,185,047,239, 14,185,047,238 | 30 | 1,073,741,823 | 35,244,355,091,391 | 8,230,264,297,652 | 43,671,288,974,893 |
| 3 | 13,111,305,415, 13,111,305,414 | 30 | 1,073,741,823 | 35,244,355,091,391 | 7,506,589,149,124 | 42,931,507,699,005 |
| 4 | 12,037,563,591, 12,037,563,590 | 30 | 1,073,741,823 | 35,244,355,091,391 | 6,901,830,907,595 | 42,310,643,330,116 |
| 5 | 10,963,821,767, 10,963,821,766 | 30 | 1,073,741,823 | 35,244,355,091,391 | 6,443,987,392,045 | 41,836,693,687,206 |
| 6 | 9,890,079,943, 9,890,079,942 | 30 | 1,073,741,823 | 35,244,355,091,391 | 5,720,312,243,517 | 41,096,912,411,318 |
| 7 | 8,816,338,119, 8,816,338,118 | 30 | 1,073,741,823 | 35,244,355,091,391 | 5,115,554,002,003 | 40,476,048,042,444 |
| 8 | 7,742,596,295, 7,742,596,294 | 30 | 1,073,741,823 | 35,244,355,091,391 | 4,657,710,486,453 | 40,002,098,399,534 |
| 9 | 6,668,854,471, 6,668,854,470 | 30 | 1,073,741,823 | 35,244,355,091,391 | 3,934,035,337,925 | 39,262,317,123,646 |
| 10 | 5,595,112,647, 5,595,112,646 | 30 | 1,073,741,823 | 35,244,355,091,391 | 3,329,277,096,403 | 38,641,452,754,764 |
| 11 | 4,521,370,823, 4,521,370,822 | 30 | 1,073,741,823 | 35,244,355,091,391 | 2,871,433,580,853 | 38,167,503,111,854 |
| 12 | 3,447,628,999, 3,447,628,998 | 30 | 1,073,741,823 | 35,244,355,091,391 | 2,147,758,432,325 | 37,427,721,835,966 |
| 13 | 2,373,887,175, 2,373,887,174 | 30 | 1,073,741,823 | 35,244,355,091,391 | 1,543,000,190,803 | 36,806,857,467,084 |
| 14 | 1,300,145,351, 1,300,145,350 | 29 | 536,870,911 | 16,648,562,137,789 | 808,358,053,082 | 17,468,369,312,081 |
| 15 | 763,274,439, 763,274,438 | 28 | 268,435,455 | 7,869,685,616,021 | 490,395,091,176 | 8,367,503,296,567 |
| 16 | 494,838,983, 494,838,982 | 27 | 134,217,727 | 3,710,732,748,629 | 328,706,275,504 | 4,044,848,347,583 |
| 17 | 360,621,255, 360,621,254 | 27 | 134,217,727 | 3,710,732,748,629 | 240,405,624,192 | 3,954,534,430,351 |
| 18 | 226,403,527, 226,403,526 | 26 | 67,108,863 | 1,744,485,745,769 | 161,088,465,816 | 1,907,963,636,155 |
| 19 | 159,294,663, 159,294,662 | 26 | 67,108,863 | 1,744,485,745,769 | 117,826,809,394 | 1,863,695,346,773 |
| 20 | 92,185,799, 92,185,798 | 25 | 33,554,431 | 816,970,326,887 | 58,546,119,800 | 876,395,921,817 |
| 21 | 58,631,367, 58,631,366 | 24 | 16,777,215 | 382,862,153,279 | 39,737,184,616 | 423,227,154,785 |
| 22 | 41,854,151, 41,854,150 | 24 | 16,777,215 | 382,862,153,279 | 27,033,547,074 | 410,271,859,003 |
| 23 | 25,076,935, 25,076,934 | 23 | 8,388,607 | 178,818,797,567 | 13,468,607,367 | 192,537,734,464 |
| 24 | 16,688,327, 16,688,326 | 22 | 4,194,303 | 83,176,656,147 | 9,038,653,435 | 92,402,724,552 |
| 25 | 12,494,023, 12,494,022 | 22 | 4,194,303 | 83,176,656,147 | 6,644,194,616 | 89,945,351,173 |
| 26 | 8,299,719, 8,299,718 | 21 | 2,097,151 | 38,482,439,185 | 4,459,102,563 | 43,034,584,878 |
| 27 | 6,202,567, 6,202,566 | 21 | 2,097,151 | 38,482,439,185 | 3,255,755,193 | 41,799,780,228 |
| 28 | 4,105,415, 4,105,414 | 20 | 1,048,575 | 17,814,101,737 | 2,219,658,699 | 20,079,617,646 |
| 29 | 3,056,839, 3,056,838 | 20 | 1,048,575 | 17,814,101,737 | 1,500,717,325 | 19,344,947,632 |
| 30 | 2,008,263, 2,008,262 | 19 | 524,287 | 8,205,940,905 | 1,007,661,430 | 9,235,866,585 |
| 31 | 1,483,975, 1,483,974 | 19 | 524,287 | 8,205,940,905 | 733,386,118 | 8,953,726,953 |
| 32 | 959,687, 959,686 | 18 | 262,143 | 3,757,000,125 | 492,364,894 | 4,259,832,789 |
| 33 | 697,543, 697,542 | 18 | 262,143 | 3,757,000,125 | 359,157,559 | 4,122,693,294 |
| 34 | 435,399, 435,398 | 17 | 131,071 | 1,706,167,483 | 241,008,070 | 1,951,745,083 |
| 35 | 304,327, 304,326 | 17 | 131,071 | 1,706,167,483 | 170,759,080 | 1,879,530,013 |
| 36 | 173,255, 173,254 | 16 | 65,535 | 774,779,795 | 79,925,776 | 856,325,981 |
| 37 | 107,719, 107,718 | 15 | 32,767 | 349,013,843 | 53,669,337 | 403,812,070 |
| 38 | 74,951, 74,950 | 15 | 32,767 | 349,013,843 | 38,503,698 | 388,154,911 |
| 39 | 42,183, 42,182 | 14 | 16,383 | 155,603,303 | 19,136,175 | 175,131,088 |
| 40 | 25,799, 25,798 | 13 | 8,191 | 68,388,581 | 12,847,657 | 81,504,968 |
| 41 | 17,607, 17,606 | 13 | 8,191 | 68,388,581 | 9,011,337 | 77,545,768 |
| 42 | 9,415, 9,414 | 12 | 4,095 | 29,977,853 | 4,133,323 | 34,195,586 |
| 43 | 5,319, 5,318 | 11 | 2,047 | 12,927,581 | 2,046,460 | 15,027,731 |
| 44 | 3,271, 3,270 | 10 | 1,023 | 5,449,281 | 1,373,988 | 6,861,599 |
| 45 | 2,247, 2,246 | 10 | 1,023 | 5,449,281 | 992,142 | 6,464,393 |
| 46 | 1,223, 1,222 | 9 | 511 | 2,218,279 | 484,130 | 2,717,699 |
| 47 | 711, 710 | 8 | 255 | 885,811 | 229,107 | 1,126,368 |
| 48 | 455, 454 | 7 | 127 | 333,069 | 153,567 | 496,166 |
| 49 | 327, 326 | 7 | 127 | 333,069 | 111,365 | 452,044 |

| part of row D | operations |
| --- | ---: |
| the 49 repetitions above (outer step: node, apply, call; then the division with the quotient and return tests) | 566,624,690,712,410 |
| repetition 50: operands 199, 198, the lean half-gcd of `1aa56884` with `k = 99` (charge 628,138), the division and tests | 632,649 |
| the classical Euclid below degree 192 (98 steps, quotient test each) | 368,647 |
| driver entry (the table of the 29 scales `1/2^a`: one allocation, 28 multiplications, 29 stores, the loop) | 393 |
| driver exit (the frees, inversion of the leading coefficient, normalisation) | 2,863 |
| stage bookkeeping (entry, exit, the free of `g`) | 1,119 |
| **row D** | **566,624,691,718,081** |

### E.3 Totals and the allocation walk of one trial

```
m = 15,258,789,062 | transform sizes 256 134217728 | squaring steps 222 of which with S: 45
S_C = 1,581,734,815,658,178
S_D normal local charges of the tree = 566,624,691,718,081
S_D of the lean stage D on the normal remainder sequence, with the quotient and return tests = 566,624,691,718,081
S_D = 566,624,691,718,081
peak of the live set, stage A = 558,345,748,608 bytes
peak of the live set, stage B = 1,176,821,039,296 bytes
peak of the live set, stage C = 2,035,827,246,528 bytes
peak of the live set, stage D = 1,958,505,089,152 bytes
two-ended pool: blocks of more than 2^24 bytes; largest sum of the two ends after each stage (bytes): init 68,719,476,800, A 558,345,748,608, B 1,176,821,039,296, C 2,035,814,651,200, D 2,035,814,651,200; at most 20 blocks; 3,085 blocks examined in all
slab classes (class: peak number of live blocks): 7: 2, 8: 2, 9: 1, 10: 1, 11: 4, 12: 2, 13: 10, 14: 10, 15: 10, 16: 6, 17: 10, 18: 8, 19: 10, 20: 10, 21: 6, 22: 10, 23: 10, 24: 10; slab area = 326,306,048 bytes
arena = 2,036,140,974,272 bytes (two-ended pool 2,035,814,651,200 + 128, slab classes 326,306,048, stages E and later 16,896), memory = 2,036,146,290,252 bytes, log2 = 40.889
stage D on the two-ended pool (blocks of more than 2^24 bytes): after init, A, B, C: low end 558,345,748,608, high end 489,626,271,808, live 1,047,972,020,416, largest sum so far 2,035,814,651,200
  stage D: 786 pool events (392 allocations, 394 frees) on 395 distinct blocks; the first 24:
  alloc #4           34,359,738,496 bytes pool L | live  1,082,331,758,912 | pool low    592,705,487,104 high    489,626,271,808 sum  1,082,331,758,912
  alloc #5           34,359,738,496 bytes pool L | live  1,116,691,497,408 | pool low    627,065,225,600 high    489,626,271,808 sum  1,116,691,497,408
  alloc #6           34,359,738,496 bytes pool L | live  1,151,051,235,904 | pool low    661,424,964,096 high    489,626,271,808 sum  1,151,051,235,904
  alloc #7           34,359,738,496 bytes pool L | live  1,185,410,974,400 | pool low    695,784,702,592 high    489,626,271,808 sum  1,185,410,974,400
  alloc #8          549,755,805,760 bytes pool L | live  1,735,166,780,160 | pool low  1,245,540,508,352 high    489,626,271,808 sum  1,735,166,780,160
  free  #8          549,755,805,760 bytes pool   | live  1,185,410,974,400 | pool low    695,784,702,592 high    489,626,271,808 sum  1,185,410,974,400
  alloc #9          154,618,822,720 bytes pool L | live  1,340,029,797,120 | pool low    850,403,525,312 high    489,626,271,808 sum  1,340,029,797,120
  alloc #10         103,079,215,168 bytes pool L | live  1,443,109,012,288 | pool low    953,482,740,480 high    489,626,271,808 sum  1,443,109,012,288
  alloc #11         103,079,215,168 bytes pool L | live  1,546,188,227,456 | pool low  1,056,561,955,648 high    489,626,271,808 sum  1,546,188,227,456
  alloc #12         154,618,822,720 bytes pool L | live  1,700,807,050,176 | pool low  1,211,180,778,368 high    489,626,271,808 sum  1,700,807,050,176
  alloc #13         103,079,215,168 bytes pool L | live  1,803,886,265,344 | pool low  1,314,259,993,536 high    489,626,271,808 sum  1,803,886,265,344
  alloc #14         103,079,215,168 bytes pool L | live  1,906,965,480,512 | pool low  1,417,339,208,704 high    489,626,271,808 sum  1,906,965,480,512
  alloc #15          51,539,607,616 bytes pool L | live  1,958,505,088,128 | pool low  1,468,878,816,320 high    489,626,271,808 sum  1,958,505,088,128
  free  #9          154,618,822,720 bytes pool   | live  1,803,886,265,408 | pool low  1,468,878,816,320 high    489,626,271,808 sum  1,958,505,088,128
  free  #10         103,079,215,168 bytes pool   | live  1,700,807,050,240 | pool low  1,468,878,816,320 high    489,626,271,808 sum  1,958,505,088,128
  free  #11         103,079,215,168 bytes pool   | live  1,597,727,835,072 | pool low  1,468,878,816,320 high    489,626,271,808 sum  1,958,505,088,128
  free  #12         154,618,822,720 bytes pool   | live  1,443,109,012,352 | pool low  1,468,878,816,320 high    489,626,271,808 sum  1,958,505,088,128
  free  #13         103,079,215,168 bytes pool   | live  1,340,029,797,184 | pool low  1,468,878,816,320 high    489,626,271,808 sum  1,958,505,088,128
  free  #14         103,079,215,168 bytes pool   | live  1,236,950,582,016 | pool low  1,468,878,816,320 high    489,626,271,808 sum  1,958,505,088,128
  free  #15          51,539,607,616 bytes pool   | live  1,185,410,974,400 | pool low    695,784,702,592 high    489,626,271,808 sum  1,185,410,974,400
  free  #4           34,359,738,496 bytes pool   | live  1,151,051,235,904 | pool low    695,784,702,592 high    489,626,271,808 sum  1,185,410,974,400
  free  #5           34,359,738,496 bytes pool   | live  1,116,691,497,408 | pool low    695,784,702,592 high    489,626,271,808 sum  1,185,410,974,400
  free  #6           34,359,738,496 bytes pool   | live  1,082,331,758,912 | pool low    695,784,702,592 high    489,626,271,808 sum  1,185,410,974,400
  free  #7           34,359,738,496 bytes pool   | live  1,047,972,020,416 | pool low    558,345,748,608 high    489,626,271,808 sum  1,047,972,020,416
  the 0 events that raise the high-water mark (the last 0 shown; event number first):
  after stage D: low end 68,719,476,800, high end 0; high-water mark of the pool over the trial 2,035,814,651,200 bytes
```
