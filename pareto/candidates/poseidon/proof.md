# Orchard Poseidon, r = 7: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, value-domain powering on truncated point sets with radix-16/32 passes, a Graeffe prefix, inversion-free half-gcd on three rows, running twiddle factors, one centre

## 1. Claim

Target: `poseidon-orchard-r7-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, seven partial rounds 4, 5, 6, 7, 8, 9 and 10, full rounds 60-63, state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

The current r7-v2 package is the line/Graeffe/value-domain algorithm with an absolute current-machine ledger (sections 2-4) with an operation count that bounds every run (sections 6-7) and a success probability derived from two score-critical premises: `H-ONE` (section 9.1), a statement about the fraction of centres at which the fixed digest polynomial has between 1 and 16 usable roots, and `H-NORMAL` (section 9.5), a statement about the normality of the remainder sequence that enters only the success probability. Section 9.2 derives the success probability from them.

* The current package derives stage C from its absolute event table, every outer apply from six forwards and two inverses, and every node from exact seven-layer formulas with ten itemized arena operations. Row C is `41,654,856,180,514`, row D is `14,898,452,597,146`, `N_max` `57,397,147,138,563`, memory `78,353,465,376` bytes and normalized cost `53.39150`. H-ONE, H-NORMAL, success and the experiments are unchanged.
* The algorithm: draw a centre `c` from two fresh random words, `c = (w1 2^256 + w2) mod p` (within statistical distance `p/2^512` of uniform on `F_p`, 4.1.1), build the odd part `g_c` of the line polynomial by evaluation and one inverse transform, replace `g_c` by its 27-fold Graeffe transform `g = g_c^(27)` (monic, degree `m`, its roots the `2^27`-th powers of those of `g_c`; section 4.3G), compute `R = S^((p-1)/2^28) mod g` in the value domain by Montgomery powering on two truncated point sets `O1`, `O2` of `n' = 1165 * 2^19 = 610,795,520` points (1165 of the 2048 depth-11 nodes of the subgroup of order `2^30` and of its coset; the method of bradcush `b30de9bf`/`a41aecdd`, there 15 of 16 nodes, section 4.3T; radix-16 and radix-32 passes under the declared 387-word register file, 4.2), every product transform of stages C and D with running twiddle factors in the block form of 4.2 (no twiddle table in either stage), take `G = gcd(g, R - 1)` by the inversion-free half-gcd of bradcush `4bcabff8`, with its apply on three rows and its matrix product on two (outer step `k = 2^j - 1 <= 2^25 - 1`, complete in-place eight-transform apply, section 4.4), charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case, and if `G` has degree between 1 and `DMAX = 16` isolate a root `y` of `G` in at most `Z = 64` rounds, find `s` with `s^(2^28) = y` and `F(c + s) = F(c - s)` among at most `2^27` candidates (4.1.3), map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39209`: a lower bound for the probability, over the algorithm's fresh random words, that the centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1), `delta = 0.001` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `eps_iso <= 2.371e-15`, `eps_coin <= 65 p / 2^512 <= 1.404e-76`, `eps_g <= 2^27 n' (D - 1) / p < 2^-167` (the centre makes `g` vanish at a point of `O1`, 4.3G) (sections 4.1.1, 4.3T, 9.2). The value the formula gives is `0.392099999999997628` (at or above the organizer floor 0.39); the claim is that value floored at five decimals.
* `time_log2 = 37.20222` in target-compression units (`C(7)=363`). `N_max=57,397,147,138,563` and `log2(N_max/363)=37.202218526668594241737310723202327383351842666536889025475632806011199533429049`, rounded up at five decimals. Offline work is `100,000,000` operations, `preprocessing_log2=18.07160` in target-compression units.
* `memory_log2_bytes = 36.18928` (`78,353,465,376` bytes, section 7). The normalized cost is `37.20222+36.18928-20=53.39150`.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; every random field element is drawn from two fresh words, at most `65` field elements (`130` words) per run (section 4.1.1), and a draw costs 63 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^13`, then the roots of its odd part about a centre, found, after a Graeffe prefix (Dandelin-Graeffe root squaring), with a gcd against `S^((p-1)/2^28) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1), a statement about the fraction of good centres, and `H-NORMAL` (score-critical for the success probability only, section 9.5), bradcush's premise on the normality of the remainder sequence stated with the allowance `delta = 0.001` and supported by organizer-run tests. Both are statements about probability. The machine (387 charged registers, 256 field registers of 256 bits plus 131 integer address registers, counted in memory; constants as immediates; every load, store and spill counted) is stated as a restriction in claim.json, as the accepted entries `89b451ff` and `fb176310` state theirs, not as a heuristic (4.2). The costs are the declared cost model of this entry: the charging rules of section 4.2 with that register file, the inversion-free half-gcd of stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the named LIFO allocation walk of section 4.2, checked by the embedded program (Appendix E). Everything else is proved or counted here.

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
init:   constants (once; no twiddle table: stage B builds the table of its transform; the product passes of stages C and D use running twiddle factors, 4.2)
setup:  the line (line_setup) (once)
for t = 1, ..., K (K = 1):            [the test t <= K is made at the start of the trial; no exit except success]
  A  c := (w1 * 2^256 + w2) mod p from two fresh random words w1, w2 (4.1.1)
  B  g := monic g_c, by section 3 (1,610,612,736 evaluations + one inverse NTT of size 805,306,368 + the nonzero-leading-coefficient test + normalisation)
  C  g := g^(27): 27 Graeffe steps on O1 (section 4.3G); R := S^((p-1)/2^28) mod g, in the value domain on the truncated point sets O1, O2 of n' = 610,795,520 points (section 4.3T): 199 squaring steps, 45 of them also multiplying by S
  D  G := gcd(g, R - 1) (monic): the inversion-free half-gcd on three rows with the in-place applies of the memory cap (section 4.4), charged for the normal remainder sequence with the quotient and return tests; on any other case ABORT (6.3)
  E  if deg G = 0 or deg G > DMAX: trial ends. Otherwise isolate a root y of G (4.1.2); if none within Z = 64 rounds: trial ends.
  F  u := a 2^28-th root of y (28 Tonelli-Shanks square roots, 2-adicity 32); for j = 0, ..., 2^27 - 1: s := u mu^j, W1 = c + s, W2 = c - s, until F(W1) = F(W2) (4.1.3); tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (363 operations each) are equal and the pairs differ -> output; otherwise the trial ends
```

4.1.1 Coins (ruling `04c0dd43`, finding F-EVAL-001). The only randomness is the cost-model random-word primitive. Every random field element of the algorithm (the centre `c` of stage A and each shift of stage E) is drawn from two fresh 256-bit words `w1, w2`: each is reduced mod `p` by three conditional subtractions (exact, `2^256 < 4p`), and `x = (w1 mod p) * (2^256 mod p) + (w2 mod p)` in `F_p`, i.e. `x = (w1 2^256 + w2) mod p` with `w1 2^256 + w2` uniform on `[0, 2^512)`. There is no rejection and no retry. A draw is 63 operations: per word 1 random-word operation, 1 load, 1 store, 3 control, the reduction 9 and its loop control 11 (26 per word, 52), two Montgomery conversions 2, the load of the constant `2^256 mod p` 1, one multiplication 1, one addition 1, entry 2, the two addresses 4. At most `1 + Z = 65` draws (`130` words) per run. With `2^512 = Q p + r`, each residue has `Q` or `Q + 1` preimages, so one draw is within statistical distance `r (p - r) / (p 2^512) <= p / 2^512 = 2^-258.0` of uniform on `F_p`; the 65 draws are independent, so the joint distribution of all the coins of a run is within `eps_coin = 65 p / 2^512 <= 1.404e-76` of the distribution with every draw exactly uniform (total variation is subadditive over independent components).

4.1.2 Stage E: isolating a root of `G`. With `1 <= deg G <= DMAX = 16`, a Cantor-Zassenhaus split with random shifts isolates one linear factor in at most `Z = 64` rounds at degree `<= 16`; `eps_iso <= 2.371e-15` bounds the probability that 64 rounds fail to isolate a root when `deg G >= 1` (section 9.4).

4.1.3 Stage F: the root of `g_c` above `y`. By 4.3G, `y = S^(2^27)` for a usable root `S` of `g_c`, and the solutions of `S'^(2^27) = y` are `u^2 mu^(2j)`, `j < 2^27`, where `u^(2^28) = y` and `mu` is a fixed primitive `2^28`-th root of unity (`2^28 | p - 1`; a constant of the offline derivation, 6.2). `u` comes from 28 successive Tonelli-Shanks square roots: `y` is a `2^28`-th power, and if `x` is a `2^k`-th power with `1 <= k <= 28`, both square roots of `x` are `2^(k-1)`-th powers (`-1` is a `2^(k-1)`-th power, `2^k | p - 1`). The scan takes `s = u mu^j` for `j = 0, 1, ..., 2^27 - 1` and stops at the first `j` with `F(c + s) = F(c - s)` (two line evaluations of section 3). For `S' = s^2` a root of `g_c` this holds, because `F(c + s) - F(c - s) = 2 s g_c(s^2)`, so the scan stops at the latest at the `j` of `S`; any stop has `s != 0` (`y != 0`) and `F(c + s) = F(c - s)`, a collision by 2.4. Charge per candidate: `s <- s mu` 1, `c + s` and `c - s` 2, two line evaluations `2 * 302`, their calls 4, the comparison and branch 2, the loop control 3: `616`; at most `2^27` candidates, `82,678,120,448`, and the loop exit 2. The 28 square roots are charged `47,012` each (the whole row F of the algorithm without the prefix, a square root and the back-map), `1,316,336`, and the back-map `47,012`: row F = `82,679,483,798`.

### 4.2 Machine model and charging rules (387 registers)

Every field operation, load, store, control operation and random word is one primitive operation; `C(7)=363` primitive operations is one target-compression unit. The machine has one 387-word file: 256 field registers and 131 integer address registers, charged in section 7. It holds an `ob128` call: 128 values, 127 twiddles, one field temporary, 128 row bases, a twiddle address, a position offset and a loop bound. Stage C uses the explicit radix-16/32 event schedule of E.1 inside this file. A block-pass data load or store with base-plus-index addressing costs one operation; every other spill is charged explicitly.

Stage C uses the absolute radix-16/32 event schedule of E.1 inside this file; no predecessor stage total enters the ledger. Column kernels are available through `ob128`; their position control is `F(cnt)=1+3 floor(cnt/8)+2+3(cnt mod 8)+2`. Node products and outer applies use current running-twiddle passes through seven layers.

Four consecutive blocks use one straight-line body and charge three controls per block. For a width-`k` product pass, each block loads and stores `2^k` words and makes `k 2^(k-1)` three-operation butterflies. Per group the running root, `k-1` squarings and `2^k-1-k` register multiplications form the twiddles. Group zero omits the `2^k-1` twiddle-one multiplications and adds three controls. E.2.1 gives the full forward and inverse formulas.

Each outer apply transforms four matrix entries and two operands forward and two outputs inverse. For entry degree `d` and budget `k`, their exact lengths are `(k+1,k,k,k-1,d+1,d)` and output lengths `(d-k+1,d-k)`. E.2.3 charges addressed copies `2L+F(L)`, zero fill `(N-L)+F(N-L)`, eight twists/scales per point, the 14-operation addressed bilinear map, addressed output placement, and—on a `3*2^a` domain—eight explicit radix-3 passes. The 500 fixed operations are itemized in 4.4.

Allocation uses one preallocated LIFO arena. A block is a 64-byte header plus payload rounded to 64 bytes. The implementation reserves each long-lived output before the temporary regions that produce it, so every release rewinds the current top to the preceding mark. Stage B reserves `g` before its interpolation and twiddle regions; stage C reserves `R` and its table before `W0`, inversion and batch scratch; each stage-D repetition releases its node, apply and four matrix regions in reverse order. The exact script asserts the name at every pop, rejects a nonpositive allocation and finishes with an empty stack. Stage-event frames, the outer-apply fixed 500 and each node's ten arena operations charge the executed allocator work. Sections 7 and E.3 give the complete normal-case walk; the ABORT prefix property bounds every other run.

The construction is credited to Jbenisek `c7ef0551-4f55-4e24-b1f2-9e18b0f3909d`; the larger register-file precedent is cryptogakusei `1533f8f0-b39a-4cca-a0b2-c9d6c9d31eb0`.

### 4.3G The Graeffe prefix

Definition. For `h` monic of even degree `m` write `h(X) = E(X^2) + X O(X^2)`; its Graeffe transform is `h~(Y) = E(Y)^2 - Y O(Y)^2`, so `h~(X^2) = h(X) h(-X)` and `h~` is monic of degree `m` with roots the squares of the roots of `h` (with multiplicity). Stage C first replaces `g = g_c` by `g^(27)`, 27 Graeffe steps, then computes `R = S^e mod g^(27)`, `e = (p-1)/2^28` (2-adicity 32), and stage D takes `G = gcd(g^(27), R - 1)`.

Lemma. `G` is the product of `(Y - y)` over the distinct values `y = S^(2^27)`, `S` a usable root of `g_c` (a nonzero square in `F_p` with `g_c(S) = 0`, section 3). Proof: `g^(27)(Y) = prod_i (Y - S_i^(2^27))` over the roots `S_i` of `g_c` in an algebraic closure; `Y^e - 1` is squarefree and its roots are the `2^28`-th powers of `F_p^*`. If `S_i^(2^27) = u^(2^28)` with `u` in `F_p^*`, then `S_i = u^2 zeta` with `zeta^(2^27) = 1`, so `zeta` is in `F_p` and `zeta = xi^2` with `xi^(2^28) = 1` (`2^28 | p - 1`), and `S_i = (u xi)^2` is a nonzero square of `F_p`; conversely `S = v^2` gives `S^(2^27) = v^(2^28)`. So `deg G` is the number of distinct `2^27`-th powers of the usable roots: `1 <= deg G <= k(c)` when `k(c) >= 1`, and `deg G = 0` when `k(c) = 0`; the event `E_c` of 9.2 gives `1 <= deg G <= DMAX`.

Execution (on the point set `O1` of 4.3T). One step: `E` (`m/2 + 1` coefficients) and `O` (`m/2`) are read from `g` at stride 2 by the top passes of two truncated forwards, which load only the input blocks below the length (3 or 2 of the 8 per offset, two offset ranges per batch; butterflies only on nonzero inputs; no zero-fill); the fused bottom pass forms `G = (E^2 - y O^2)/N` at each point `y` of `O1` between the forward and the inverse bottom layers (`y` is the last-layer twiddle of its butterfly, in a register: two squarings, two multiplications, one subtraction, 5 per point); one truncated inverse stores the new coefficients into the array of `g` (those above `m` come out zero). `E` and `O` on `O1` use the arrays of `A` on `O2` and of `A` on `O1` before stage C fills them, with a batch buffer of `5,177,344` words of their own, used by one transform at a time and freed after the prefix; no array is added and the high-water mark of section 7 is unchanged. One step is `133,475,049,158` operations (Appendix E.1), 27 steps; stage C then runs 199 squaring steps in place of 226 (the exponent loses 27 low zero bits). A bit-zero powering step is `186,436,381,172`. Depth 27 is fixed by the declared H-NORMAL probability space and retained experiment design; Appendix E.2.2 optimizes the outer cap at that depth.

Every map is exact; no premise is added to the time or the memory. The zero test of `k1` (4.3T) now concerns `g^(27)`: `g^(27)(y) = 0` for `y` in `O1` only if `g_c(x) = 0` for one of the `2^27` values `x` with `x^(2^27) = y` (in `F_p` or an extension); for each such `x`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g^(27) vanishes on O1) <= 2^27 n' (D - 1) / p = eps_g < 2^-167`.

### 4.3T Stage C in the value domain on truncated point sets (the method of bradcush `b30de9bf`/`a41aecdd`, 1165 of 2048 nodes)

Point sets. `N = 2^30` divides `p - 1` (2-adicity 32). Let `psi` have order `2^31`, `H_N = <psi^2>` and `Y = X^(2^19)`. `H_N` is the union of the 2048 depth-11 nodes `{x : x^(2^19) = r_j}`, `r_j` the 2048-th roots of unity in transform (bit-reversed) order; `O1` is the union of the first 1165 nodes, `n' = 1165 * 2^19 = 610,795,520 >= m + 1 = 610,351,563` points, and `O2` the same 1165 nodes of the coset `psi H_N` (`x^(2^19) = r'_j`, `r'_j^2048 = -1`), disjoint from `O1`. `P1 = prod_{j<1165} (Y - r_j)` has degree `n'`, vanishes on `O1` and is the nonzero constant `P1(r'_j)` on node `j` of `O2`; `delta_j = 1/P1(r'_j)` (1165 table constants).

Truncated transforms (bradcush `b30de9bf` 4.3, generalized as the truncated Fourier transform of van der Hoeven, ISSAC 2004). A polynomial of degree `< n'` is `sum_{k<2048} P_k Y^k` with `deg P_k < 2^19` and `P_k = 0` for `k >= 1165`; its values on the 1165 nodes determine it and are determined by it (the CRT for the 1165 coprime moduli `Y - r_j`, whose product `P1` has degree `n'`). The forward transform runs the top 3 layers on all `N/8` offsets (no truncation saving is charged), the middle layers only on the blocks above present nodes, and the bottom 3 layers on the `n'` points. The inverse runs the same layers in reverse, scales each 8-point block of its bottom pass by `diag(1, c^-1 J)` (`c = y^8` of the block, `V^T V = 8 diag(1, cJ)`; 7 multiplications and the load of `c^-1`, 9 operations per block), and recovers the residues of the dropped part `[1165, 2048)`, the maximal subtrees `{1165}`, `{1166..1167}`, `{1168..1183}`, `{1184..1215}`, `{1216..1279}`, `{1280..1535}`, `{1536..2047}` (depths 11, 10, 7, 6, 5, 3, 2), from the known zero chunks `P_k = 0` along their paths to the root, as bradcush recovers the one dropped leaf; with the value of the path held in a register this is charged 8 operations (3 multiplications, 3 additions, the load of the known value) per point of a dropped subtree per layer of its path and one store (2) per point. The positions above `n'` that a transform touches are held in two buffers (one transform runs at a time). Layers 1-7 (the top pass, the first middle pass and the recoveries of the dropped subtrees of depths 7, 6, 5, 3, 2) act on each class of the `128` positions with equal low 23 bits separately (`73` below `73 * 2^23`, `55` above: the depth-7 nodes 73-127), so they run class-batch by class-batch, `128` batches of `65,536` classes, the `55` positions above of each class of the batch held in a batch buffer of `3,604,480` words and discarded after the batch; the `3 * 2^19 = 1,572,864` positions in `[n', 73 * 2^23)` that the passes below layer 7 touch (the dropped depth-11 nodes 1165-1167, the subtrees of depths 11 and 10) are a tail buffer held whole. Charged once per batch: the 8 groups, the pass overhead and the batch loop of the first middle pass (`8 * 20 + 20 + 3`), the top-pass overhead with its 16 inner loops, one per range of `65,536` consecutive offsets (`60 + 20 + 16 * 5`), and the path constants of the five in-batch recoveries reloaded (`163`: 23 levels, 3 constants each loaded at 2, and 5 loops at 5); before the top of each truncated forward the zero-fill of lane 4 above `n'` (the `7` positions of each class of the batch, per batch, and the tail once; a store, 2, each and the loop). The passes are fused as in `b30de9bf` 4.5 under a 64-field-register subfile of the 256 field registers of 4.2, the 30 layers split 3 | 4, 4, 5, 5, 5 | 4: a bottom pass (16-point blocks: forward layers, the pointwise map, inverse layers; one set of 15 twiddles for both directions, 19 operations per block: two loads from the two-level table, one multiplication, three squarings, eleven multiplications by register constants; `V^T V = 16 diag(1, cJ)` with `c = y^16` of the block, so every inverse bottom pass scales each block by `diag(1, c^-1 J)`: 15 multiplications and the load of `c^-1`, 17 operations per block), two middle passes of radix 16 (per block 16 loads and 16 stores at one operation each, 32 butterflies and 3 control (the block loop unrolled by four, 4.2), 131; the 15 twiddles of a group in registers, formed from the running group root by one multiplication, 3 squarings and 11 multiplications by register constants, 20 per group with its control), three middle passes of radix 32 (per block 32 loads and 32 stores at one operation each, 80 butterflies, the loads of the 3 twiddles that do not fit beside the 32 values (6) and 3 control (the block loop unrolled by four, 4.2), 313; per group the 31 twiddles from the running group root, 1 + 4 + 22 operations, the stores of the 3 spilled ones and control, 38), and a pruned top pass that fuses the inverse top of one set with the forward top of the other: only the `b = 5` depth-3 subtrees that hold points of the 1165 nodes are formed or read (the butterflies of the 8-point top block counted on the needed and nonzero lanes, `_top_counts`), and the coset twiddle is applied on those `b` blocks.

Montgomery powering (`b30de9bf` 4.5). For residues of degree `< n'`, `Mont(A, B) = (A B + u g)/P1` with `u = -A B / g mod P1` (`deg u < n'`); the division by `P1` is exact, `Mont(A, B) = A B / P1 mod g`, and `deg Mont(A, A) <= n' - 2`, so `X Mont(A, A)` has degree `< n'`. A residue `A` (representing `S^e P1`) is held by its values on `O1` and on `O2`, each up to a tracked scalar. One step: `U = A^2 k1` on `O1` (`k1 = -1/(N^3 g)` there; `u` is determined by its values on `O1`); `U` to `O2` (truncated inverse on `O1`, truncated forward on `O2`); `B2 = (A2^2 + U g) delta_j` on node `j` of `O2`, which is `Mont(A, A)` up to the tracked scalar because `P1 = 1/delta_j` there, times the point `x` when the exponent bit is 1; `B2` to `O1` (truncated inverse on `O2`, truncated forward on `O1`). No `1/N` is executed inside the steps (the scalars are tracked, 2 operations per step). Per point and step: on `O1` `sqr, LD k1, mul` (4); on `O2` `LD A2, sqr, LD g, mul, add`, the multiplication by `delta_j`, `ST` (10) and per block the load of `delta_j` (2) and 2 address updates beyond the block control (4.2); 3 more per point for a 1-bit (the load of the point and a multiplication) and 1 more address update per block.

Entry and exit. `g` (coefficients after the Graeffe prefix of 4.3G, its slots above `m` zero) goes to `O1` and `O2` (a truncated forward each; every scaling of this section, `1/N` and the coset twist, is a running product fused into the adjacent pass, 2 operations per point). The start residue is `A0 = X^v P1 mod g`, `v = 2^27 = 134,217,728` (VSHIFT = 2): `q = floor(X^v P1 / g)` has `ell = v + n' - m + 1 = 134,661,687` coefficients and is formed from the Newton reciprocal of the reversed `g` and one product (transforms of up to `3*2^27` points with running twiddle factors in the block form of 4.2); on node `j` of `O2`, `x^v P1(x) = r'_j^256 P1(r'_j)` is a constant, so `A0 = x^v P1 - q g` there is one truncated forward of `q` and one pointwise pass (8 per point); then `A0` goes to `O1`. `k1` is formed by chunked batch inversion on `O1` (chunks of `2^16` points: prefix products, one inversion, two multiplications per point; the `2^16` prefixes are kept in the tail and batch buffer, which no transform uses at that time); each chunk product is tested for zero before its inversion (2 per chunk), and a zero ends the trial: for fixed `x != 0`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g vanishes on O1) <= eps_g < 2^-167` for the transformed `g` (4.3G, 9.2). The exit is one step with multiplier 1 (`Mont(A, 1)`) and two truncated inverses with their scaling, which return `kappa R` (`kappa` the tracked scalar) and `g` in coefficient form; the gcd is scale-invariant, so stage D receives `kappa R - kappa`. There are `199` squaring steps (the exponent `(p-1)/2^28`, 4.3G), `45` of them also multiplying by `S`.

Exactness and memory. Every map above is exact (Montgomery products of polynomials of degree `< n'`, held bijectively by their values on 1165 nodes); no premise is added to stage C. The live set of the stage is four arrays of `n'` words (`g` on `O2`, `A` on `O2`, `A` on `O1`, `k1` on `O1`), the tail and batch buffer of `5,177,344` words, the tables (`1,195 + 16,384` words: 30 constants, the 1165 `delta_j`, the two-level root tables) and, while `q` is formed, the Newton arrays. The step-by-step count is expanded in Appendix E.1 and totals **row C = 41,654,856,180,514** (section 6).

### 4.4 Stage D: inversion-free half-gcd, three-row apply and two-row product

`G=gcd(g,R-1)` uses pseudo-division and the normal-sequence quotient and return tests. A node of budget `2^j-1` calls two children of budget `2^(j-1)-1`; its first-matrix apply uses `Y-1,Y+1,Y-i`, while `M=M1[[Q,1],[b^2,0]]M2` uses `Y-1,Y+1`. On the normal sequence the product entries have degree at most `2n-1`, so the two rows determine them exactly.

The driver starts at degree `610,351,562`, repeatedly takes the largest fitting budget, applies the returned matrix with the complete implementation of 4.2 and performs the quotient-tested division. The apply's fixed 500 is `28+24+56+144+48+72+12+24+32+20+40`: entry/exit, tests, plan lookup, six forward frames, two inverse frames, six source descriptors, bilinear setup, two output setups, row/scale constants, arena mark/rewind, pointer/result updates. The division costs `15*(degree-budget)+4,454`, itemized as coefficient work plus tests, addresses and exit. The current planner selects cap 25. The remaining degree is finished by the explicit classical formula of E.2. Row D is `14,898,452,597,146`. On an abnormal quotient, short return or zero remainder, ABORT executes only a prefix of this work and allocation sequence.

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G = gcd(g, R - 1)`, whose roots are the values `y = S^(2^27)` of the usable roots `S` of `g_c` (4.3G); stage F stops only at an `s != 0` with `F(c + s) = F(c - s)` (4.1.3), so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Ledger: operation count (primitive operations; `C(7) = 363`)

| row | what is charged | operations |
| --- | --- | --- |
| init | constants and bookkeeping (once; no twiddle table, 4.2) | 17,978 |
| setup | the line (`line_setup`, once) | 4,910 |
| A (per trial) | stage bookkeeping, loop test and update, the coin draw (63, two words), one allocation | 1,228 |
| B (per trial) | `1,610,612,736` evaluations of `F` on the line at their executed `155 + 21 r = 302` operations each (section 3), the loop work, the twiddle table and the inverse transform of size `805,306,368`, the normalisation | 760,889,235,868 |
| C (per trial) | absolute current event schedule; Appendix E.1 | 41,654,856,180,514 |
| D (per trial) | exact nodes, complete applies, driver and tail; Appendix E.2 | 14,898,452,597,146 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16`, each with one draw of 63 (two words) | 166,081,821 |
| F (per trial) | the `2^28`-th root of `y` (28 square roots at 47,012), the scan of at most `2^27` candidates at 616 and its exit, the back-map 47,012 (4.1.3) | 82,679,483,798 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 363 + 32` | 8,292 |
| trial-loop (per trial) | trial-loop bookkeeping (12) and the allocator reset after an ABORT (1,000), charged in every trial | 1,012 |
| plan_invN misses | one per distinct plan size (and the block size `3 * 2^24` of 4.4) | 135,916 |
| output rows | the fixed output rows (stages H and I) | 3,390,080 |
| offline | absolute cap planner and constant derivation | 100,000,000 |
| **N_max** | `T_fixed + T_trial + T_off` | **57,397,147,138,563** |

`T_off=100,000,000`; `T_trial=57,397,043,589,679`; `T_fixed=3,548,884`; `N_max=57,397,147,138,563`. `log2(N_max/363)=37.202218526668594241737310723202327383351842666536889025475632806011199533429049`, rounded up to `37.20222`. Rows C and D are `41,654,856,180,514` and `14,898,452,597,146`.

### 6.1 Validation
The earlier `56272e37` package reports comparisons with instrumented totals at `r = 3, 4, 5`. This package does not use those totals: the truncated-set stage C count is the formula of Appendix E.1, and the LIFO arena is the named push/pop walk of section 7 and Appendix E.3. Rows C and D are the finite recurrences of Appendix E (E.1, E.2), summed term by term; no coefficient is fitted or extrapolated.

### 6.2 Offline derivation
The literals of the sources are computed once, offline, from `p` and the organizer's 192 round constants and 9 MDS entries, one literal at a time (working set: at most 16 words of 32 bytes and a 64-byte digit buffer); each is the value of one closed formula, with no search and no choice. Count in the primitives of 4.2 (orchard-field-ram-v2: every field operation, load, store and control operation is 1): a field operation is charged 4 (the operation, two operand loads, one store), a 64-bit word operation 3 (the operation, one load, one store), a hexadecimal digit 5 (its load, the table load, a shift, an or, the loop control). (a) Input: 202 values of 64 hexadecimal digits (`p`, the 192 round constants, the 9 MDS entries), 324 each with the 4 word stores: `65,448`. (b) Field literals, 494 field operations: `2 = 1 + 1` (1); `R = 2^256 mod p`, `2` squared 8 times (8); `R^2 mod p` (1); the Montgomery forms `x R mod p` of the 201 organizer constants (201); `2^65 R mod p` (`2` squared 6 times, times `2`, times `R`: 8); `5 = 2 + 2 + 1` (2); `5^t R mod p` with `t = (p-1)/2^32`, the odd exponent of the Tonelli-Shanks of stage F (223 bits, 46 of them 1: 222 squarings, 45 multiplications, times `R`: 268); `mu R mod p`, `mu = (5^t)^(2^4)` of order `2^28` (4 squarings, times `R`: 5); charged `4 * 494 + 3 * 222` (the bit steps of the square-and-multiply) `= 2,642`. (c) Word literals, 90 word operations: `p - 1` (4), `t` (a shift by 32 over 4 words, 12), `(t+1)/2` (16), `(p-1)/2` (12), `p - 2` (4), `e = (4(p-1)+1)/5` (a shift by 2 into 5 words 15, plus 1, a division by 5 word by word 10: 26), `-p^-1 mod 2^64` (5 Newton steps `x <- x (2 - p_0 x)` from `x = p_0`, 3 each, and a negation: 16); charged `3 * 90 = 270`. (d) Output: 212 literals of 64 hexadecimal digits (the 201 Montgomery forms, `R`, `R^2`, `2^65 R`, `5^t R`, `mu R`, `t`, `(t+1)/2`, `(p-1)/2`, `p - 2`, `e`, `p`), 324 each, and `-p^-1 mod 2^64` (16 digits, 81): `68,769`. The source-literal component is `65,448 + 2,642 + 270 + 68,769 = 137,129` operations. Appendix E.2.2 derives a 79,532,313-operation bound for the cap planner, low-cap screen and constant checks. The ledger charges `100,000,000` operations, declared `preprocessing_log2 = 18.07160` in target-compression units and included once in `N_max`.

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry `e6dcb600`)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g, R - 1)`, `g = g_c^(27)` (4.3G): every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the re-centring division of a node, the division of each repetition of the outer loop, each step of the base case) tests, before it does any work beyond reading the two leading coefficients, that its quotient has degree 1 (2 operations); (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); a zero remainder inside `hgcd` or in the outer-loop division also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state at the start of the trial (`1,000` operations, charged in every trial). Lemma (prefix; `e6dcb600`, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each node of budget `2^j - 1` splits into two calls of budget `2^(j-1) - 1` (each lean call at `k1 = ceil(k/2)`) and, with every quotient of degree 1, every degree in the tree is fixed by `m` and the number of quotients so far, and the budgets of the outer loop (`k = 2^j - 1 <= min(2^25 - 1, (n - 1)/2)`, then `ceil((n+1)/2)`, section 4.4) are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's `hgcd` calls and divisions produce has degree at least the base-case bound, so every gcd of degree at most `DMAX = 16` first appears in the classical Euclid below the base-case degree, after a prefix of the degree-0 work; a zero remainder earlier ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2). The node follows `4bcabff8`, the lean call `1aa56884` proof 4.4 and the in-place applies `a78f526e` proof 4.4, all read as text only (no entry script was run, compiled or imported). Appendix E.2 expands, for `r = 7`, the charge of stage D for the normal sequence with the tests, `14,898,452,597,146`, repetition by repetition.

The `r = 7` trial (`78,353,465,376` bytes, `57,397,147,138,563` operations) exceeds the organizer sandbox (128 MiB, 20 s), so the costs are the exact formula counts of sections 6 and 7; zero-fill clearing is charged (ruling `3476cad8`) and the register file of 387 words (256 field, 131 integer address registers) is the machine restriction of claim.json.

## 7. Memory: absolute event walk

Every arena block has `blk(w)=64+64 ceil(32w/64)` bytes. Stage C allocates four `n'` arrays, the `30+1165+4*4096`-word table and the `55*65536+3*2^19`-word batch/tail scratch. Newton fits in the arrays because `3*ell<=n'`; the quotient fits because `ell+3*2^27<=n'`. Stage D allocates the pair, four `2^25+2`-word matrix blocks and the `(16*2^25-256)`-word bump. An apply allocates an output extension only when its transform domain exceeds `n'`. The script replays strict pushes and named pops:

| event | arena live bytes |
|---|---:|
| alloc A g | 19,545,456,704 |
| free A g | 0 |
| alloc B g result | 19,545,456,704 |
| alloc B interpolation | 45,315,260,544 |
| alloc B twiddle | 49,610,227,904 |
| free B twiddle | 45,315,260,544 |
| free B interpolation | 19,545,456,704 |
| alloc C W1/R | 39,090,913,408 |
| alloc C table | 39,091,476,032 |
| alloc C W0 | 58,636,932,736 |
| alloc C batch and tail scratch | 58,802,607,808 |
| free C batch and tail scratch | 58,636,932,736 |
| alloc C k1 | 78,182,389,440 |
| alloc C inversion scratch | 78,348,064,512 |
| free C inversion scratch | 78,182,389,440 |
| free C k1 | 58,636,932,736 |
| free C W0 | 39,091,476,032 |
| alloc D1 matrix 1 | 40,165,217,984 |
| alloc D1 matrix 2 | 41,238,959,936 |
| alloc D1 matrix 3 | 42,312,701,888 |
| alloc D1 matrix 4 | 43,386,443,840 |
| alloc D1 node bump | 60,566,304,896 |
| free D1 node bump | 43,386,443,840 |
| alloc D1 apply output extension | 49,610,791,040 |
| alloc D1 apply work | 75,380,594,880 |
| free D1 apply work | 49,610,791,040 |
| free D1 apply output extension | 43,386,443,840 |
| free D1 matrix 4 | 42,312,701,888 |
| free D1 matrix 3 | 41,238,959,936 |
| free D1 matrix 2 | 40,165,217,984 |
| free D1 matrix 1 | 39,091,476,032 |
| alloc D2 matrix 1 | 40,165,217,984 |
| alloc D2 matrix 2 | 41,238,959,936 |
| alloc D2 matrix 3 | 42,312,701,888 |
| alloc D2 matrix 4 | 43,386,443,840 |
| alloc D2 node bump | 60,566,304,896 |
| free D2 node bump | 43,386,443,840 |
| alloc D2 apply output extension | 49,610,791,040 |
| alloc D2 apply work | 75,380,594,880 |
| free D2 apply work | 49,610,791,040 |
| free D2 apply output extension | 43,386,443,840 |
| free D2 matrix 4 | 42,312,701,888 |
| free D2 matrix 3 | 41,238,959,936 |
| free D2 matrix 2 | 40,165,217,984 |
| free D2 matrix 1 | 39,091,476,032 |
| alloc D3 matrix 1 | 40,165,217,984 |
| alloc D3 matrix 2 | 41,238,959,936 |
| alloc D3 matrix 3 | 42,312,701,888 |
| alloc D3 matrix 4 | 43,386,443,840 |
| alloc D3 node bump | 60,566,304,896 |
| free D3 node bump | 43,386,443,840 |
| alloc D3 apply output extension | 49,610,791,040 |
| alloc D3 apply work | 75,380,594,880 |
| free D3 apply work | 49,610,791,040 |
| free D3 apply output extension | 43,386,443,840 |
| free D3 matrix 4 | 42,312,701,888 |
| free D3 matrix 3 | 41,238,959,936 |
| free D3 matrix 2 | 40,165,217,984 |
| free D3 matrix 1 | 39,091,476,032 |
| alloc D4 matrix 1 | 40,165,217,984 |
| alloc D4 matrix 2 | 41,238,959,936 |
| alloc D4 matrix 3 | 42,312,701,888 |
| alloc D4 matrix 4 | 43,386,443,840 |
| alloc D4 node bump | 60,566,304,896 |
| free D4 node bump | 43,386,443,840 |
| alloc D4 apply work | 60,566,313,088 |
| free D4 apply work | 43,386,443,840 |
| free D4 matrix 4 | 42,312,701,888 |
| free D4 matrix 3 | 41,238,959,936 |
| free D4 matrix 2 | 40,165,217,984 |
| free D4 matrix 1 | 39,091,476,032 |
| alloc D5 matrix 1 | 40,165,217,984 |
| alloc D5 matrix 2 | 41,238,959,936 |
| alloc D5 matrix 3 | 42,312,701,888 |
| alloc D5 matrix 4 | 43,386,443,840 |
| alloc D5 node bump | 60,566,304,896 |
| free D5 node bump | 43,386,443,840 |
| alloc D5 apply work | 60,566,313,088 |
| free D5 apply work | 43,386,443,840 |
| free D5 matrix 4 | 42,312,701,888 |
| free D5 matrix 3 | 41,238,959,936 |
| free D5 matrix 2 | 40,165,217,984 |
| free D5 matrix 1 | 39,091,476,032 |
| alloc D6 matrix 1 | 40,165,217,984 |
| alloc D6 matrix 2 | 41,238,959,936 |
| alloc D6 matrix 3 | 42,312,701,888 |
| alloc D6 matrix 4 | 43,386,443,840 |
| alloc D6 node bump | 60,566,304,896 |
| free D6 node bump | 43,386,443,840 |
| alloc D6 apply work | 60,566,313,088 |
| free D6 apply work | 43,386,443,840 |
| free D6 matrix 4 | 42,312,701,888 |
| free D6 matrix 3 | 41,238,959,936 |
| free D6 matrix 2 | 40,165,217,984 |
| free D6 matrix 1 | 39,091,476,032 |
| alloc D7 matrix 1 | 40,165,217,984 |
| alloc D7 matrix 2 | 41,238,959,936 |
| alloc D7 matrix 3 | 42,312,701,888 |
| alloc D7 matrix 4 | 43,386,443,840 |
| alloc D7 node bump | 60,566,304,896 |
| free D7 node bump | 43,386,443,840 |
| alloc D7 apply work | 60,566,313,088 |
| free D7 apply work | 43,386,443,840 |
| free D7 matrix 4 | 42,312,701,888 |
| free D7 matrix 3 | 41,238,959,936 |
| free D7 matrix 2 | 40,165,217,984 |
| free D7 matrix 1 | 39,091,476,032 |
| alloc D8 matrix 1 | 40,165,217,984 |
| alloc D8 matrix 2 | 41,238,959,936 |
| alloc D8 matrix 3 | 42,312,701,888 |
| alloc D8 matrix 4 | 43,386,443,840 |
| alloc D8 node bump | 60,566,304,896 |
| free D8 node bump | 43,386,443,840 |
| alloc D8 apply work | 56,271,345,792 |
| free D8 apply work | 43,386,443,840 |
| free D8 matrix 4 | 42,312,701,888 |
| free D8 matrix 3 | 41,238,959,936 |
| free D8 matrix 2 | 40,165,217,984 |
| free D8 matrix 1 | 39,091,476,032 |
| alloc D9 matrix 1 | 40,165,217,984 |
| alloc D9 matrix 2 | 41,238,959,936 |
| alloc D9 matrix 3 | 42,312,701,888 |
| alloc D9 matrix 4 | 43,386,443,840 |
| alloc D9 node bump | 60,566,304,896 |
| free D9 node bump | 43,386,443,840 |
| alloc D9 apply work | 56,271,345,792 |
| free D9 apply work | 43,386,443,840 |
| free D9 matrix 4 | 42,312,701,888 |
| free D9 matrix 3 | 41,238,959,936 |
| free D9 matrix 2 | 40,165,217,984 |
| free D9 matrix 1 | 39,091,476,032 |
| alloc D10 matrix 1 | 40,165,217,984 |
| alloc D10 matrix 2 | 41,238,959,936 |
| alloc D10 matrix 3 | 42,312,701,888 |
| alloc D10 matrix 4 | 43,386,443,840 |
| alloc D10 node bump | 60,566,304,896 |
| free D10 node bump | 43,386,443,840 |
| alloc D10 apply work | 56,271,345,792 |
| free D10 apply work | 43,386,443,840 |
| free D10 matrix 4 | 42,312,701,888 |
| free D10 matrix 3 | 41,238,959,936 |
| free D10 matrix 2 | 40,165,217,984 |
| free D10 matrix 1 | 39,091,476,032 |
| alloc D11 matrix 1 | 40,165,217,984 |
| alloc D11 matrix 2 | 41,238,959,936 |
| alloc D11 matrix 3 | 42,312,701,888 |
| alloc D11 matrix 4 | 43,386,443,840 |
| alloc D11 node bump | 60,566,304,896 |
| free D11 node bump | 43,386,443,840 |
| alloc D11 apply work | 56,271,345,792 |
| free D11 apply work | 43,386,443,840 |
| free D11 matrix 4 | 42,312,701,888 |
| free D11 matrix 3 | 41,238,959,936 |
| free D11 matrix 2 | 40,165,217,984 |
| free D11 matrix 1 | 39,091,476,032 |
| alloc D12 matrix 1 | 40,165,217,984 |
| alloc D12 matrix 2 | 41,238,959,936 |
| alloc D12 matrix 3 | 42,312,701,888 |
| alloc D12 matrix 4 | 43,386,443,840 |
| alloc D12 node bump | 60,566,304,896 |
| free D12 node bump | 43,386,443,840 |
| alloc D12 apply work | 51,976,378,496 |
| free D12 apply work | 43,386,443,840 |
| free D12 matrix 4 | 42,312,701,888 |
| free D12 matrix 3 | 41,238,959,936 |
| free D12 matrix 2 | 40,165,217,984 |
| free D12 matrix 1 | 39,091,476,032 |
| alloc D13 matrix 1 | 40,165,217,984 |
| alloc D13 matrix 2 | 41,238,959,936 |
| alloc D13 matrix 3 | 42,312,701,888 |
| alloc D13 matrix 4 | 43,386,443,840 |
| alloc D13 node bump | 60,566,304,896 |
| free D13 node bump | 43,386,443,840 |
| alloc D13 apply work | 51,976,378,496 |
| free D13 apply work | 43,386,443,840 |
| free D13 matrix 4 | 42,312,701,888 |
| free D13 matrix 3 | 41,238,959,936 |
| free D13 matrix 2 | 40,165,217,984 |
| free D13 matrix 1 | 39,091,476,032 |
| alloc D14 matrix 1 | 40,165,217,984 |
| alloc D14 matrix 2 | 41,238,959,936 |
| alloc D14 matrix 3 | 42,312,701,888 |
| alloc D14 matrix 4 | 43,386,443,840 |
| alloc D14 node bump | 60,566,304,896 |
| free D14 node bump | 43,386,443,840 |
| alloc D14 apply work | 49,828,894,848 |
| free D14 apply work | 43,386,443,840 |
| free D14 matrix 4 | 42,312,701,888 |
| free D14 matrix 3 | 41,238,959,936 |
| free D14 matrix 2 | 40,165,217,984 |
| free D14 matrix 1 | 39,091,476,032 |
| alloc D15 matrix 1 | 40,165,217,984 |
| alloc D15 matrix 2 | 41,238,959,936 |
| alloc D15 matrix 3 | 42,312,701,888 |
| alloc D15 matrix 4 | 43,386,443,840 |
| alloc D15 node bump | 60,566,304,896 |
| free D15 node bump | 43,386,443,840 |
| alloc D15 apply work | 49,828,894,848 |
| free D15 apply work | 43,386,443,840 |
| free D15 matrix 4 | 42,312,701,888 |
| free D15 matrix 3 | 41,238,959,936 |
| free D15 matrix 2 | 40,165,217,984 |
| free D15 matrix 1 | 39,091,476,032 |
| alloc D16 matrix 1 | 40,165,217,984 |
| alloc D16 matrix 2 | 41,238,959,936 |
| alloc D16 matrix 3 | 42,312,701,888 |
| alloc D16 matrix 4 | 43,386,443,840 |
| alloc D16 node bump | 60,566,304,896 |
| free D16 node bump | 43,386,443,840 |
| alloc D16 apply work | 47,681,411,200 |
| free D16 apply work | 43,386,443,840 |
| free D16 matrix 4 | 42,312,701,888 |
| free D16 matrix 3 | 41,238,959,936 |
| free D16 matrix 2 | 40,165,217,984 |
| free D16 matrix 1 | 39,091,476,032 |
| alloc D17 matrix 1 | 40,165,217,984 |
| alloc D17 matrix 2 | 41,238,959,936 |
| alloc D17 matrix 3 | 42,312,701,888 |
| alloc D17 matrix 4 | 43,386,443,840 |
| alloc D17 node bump | 60,566,304,896 |
| free D17 node bump | 43,386,443,840 |
| alloc D17 apply work | 46,607,669,376 |
| free D17 apply work | 43,386,443,840 |
| free D17 matrix 4 | 42,312,701,888 |
| free D17 matrix 3 | 41,238,959,936 |
| free D17 matrix 2 | 40,165,217,984 |
| free D17 matrix 1 | 39,091,476,032 |
| alloc D18 matrix 1 | 39,628,347,072 |
| alloc D18 matrix 2 | 40,165,218,112 |
| alloc D18 matrix 3 | 40,702,089,152 |
| alloc D18 matrix 4 | 41,238,960,192 |
| alloc D18 node bump | 49,828,886,656 |
| free D18 node bump | 41,238,960,192 |
| alloc D18 apply work | 42,849,572,992 |
| free D18 apply work | 41,238,960,192 |
| free D18 matrix 4 | 40,702,089,152 |
| free D18 matrix 3 | 40,165,218,112 |
| free D18 matrix 2 | 39,628,347,072 |
| free D18 matrix 1 | 39,091,476,032 |
| alloc D19 matrix 1 | 39,359,911,616 |
| alloc D19 matrix 2 | 39,628,347,200 |
| alloc D19 matrix 3 | 39,896,782,784 |
| alloc D19 matrix 4 | 40,165,218,368 |
| alloc D19 node bump | 44,460,177,536 |
| free D19 node bump | 40,165,218,368 |
| alloc D19 apply work | 40,970,524,800 |
| free D19 apply work | 40,165,218,368 |
| free D19 matrix 4 | 39,896,782,784 |
| free D19 matrix 3 | 39,628,347,200 |
| free D19 matrix 2 | 39,359,911,616 |
| free D19 matrix 1 | 39,091,476,032 |
| alloc D20 matrix 1 | 39,225,693,888 |
| alloc D20 matrix 2 | 39,359,911,744 |
| alloc D20 matrix 3 | 39,494,129,600 |
| alloc D20 matrix 4 | 39,628,347,456 |
| alloc D20 node bump | 41,775,822,976 |
| free D20 node bump | 39,628,347,456 |
| alloc D20 apply work | 40,165,218,432 |
| free D20 apply work | 39,628,347,456 |
| free D20 matrix 4 | 39,494,129,600 |
| free D20 matrix 3 | 39,359,911,744 |
| free D20 matrix 2 | 39,225,693,888 |
| free D20 matrix 1 | 39,091,476,032 |
| alloc D21 matrix 1 | 39,225,693,888 |
| alloc D21 matrix 2 | 39,359,911,744 |
| alloc D21 matrix 3 | 39,494,129,600 |
| alloc D21 matrix 4 | 39,628,347,456 |
| alloc D21 node bump | 41,775,822,976 |
| free D21 node bump | 39,628,347,456 |
| alloc D21 apply work | 40,031,000,704 |
| free D21 apply work | 39,628,347,456 |
| free D21 matrix 4 | 39,494,129,600 |
| free D21 matrix 3 | 39,359,911,744 |
| free D21 matrix 2 | 39,225,693,888 |
| free D21 matrix 1 | 39,091,476,032 |
| alloc D22 matrix 1 | 39,158,585,024 |
| alloc D22 matrix 2 | 39,225,694,016 |
| alloc D22 matrix 3 | 39,292,803,008 |
| alloc D22 matrix 4 | 39,359,912,000 |
| alloc D22 node bump | 40,433,645,696 |
| free D22 node bump | 39,359,912,000 |
| alloc D22 apply work | 39,628,347,520 |
| free D22 apply work | 39,359,912,000 |
| free D22 matrix 4 | 39,292,803,008 |
| free D22 matrix 3 | 39,225,694,016 |
| free D22 matrix 2 | 39,158,585,024 |
| free D22 matrix 1 | 39,091,476,032 |
| alloc D23 matrix 1 | 39,158,585,024 |
| alloc D23 matrix 2 | 39,225,694,016 |
| alloc D23 matrix 3 | 39,292,803,008 |
| alloc D23 matrix 4 | 39,359,912,000 |
| alloc D23 node bump | 40,433,645,696 |
| free D23 node bump | 39,359,912,000 |
| alloc D23 apply work | 39,561,238,656 |
| free D23 apply work | 39,359,912,000 |
| free D23 matrix 4 | 39,292,803,008 |
| free D23 matrix 3 | 39,225,694,016 |
| free D23 matrix 2 | 39,158,585,024 |
| free D23 matrix 1 | 39,091,476,032 |
| alloc D24 matrix 1 | 39,125,030,592 |
| alloc D24 matrix 2 | 39,158,585,152 |
| alloc D24 matrix 3 | 39,192,139,712 |
| alloc D24 matrix 4 | 39,225,694,272 |
| alloc D24 node bump | 39,762,557,056 |
| free D24 node bump | 39,225,694,272 |
| alloc D24 apply work | 39,326,357,632 |
| free D24 apply work | 39,225,694,272 |
| free D24 matrix 4 | 39,192,139,712 |
| free D24 matrix 3 | 39,158,585,152 |
| free D24 matrix 2 | 39,125,030,592 |
| free D24 matrix 1 | 39,091,476,032 |
| alloc D25 matrix 1 | 39,108,253,376 |
| alloc D25 matrix 2 | 39,125,030,720 |
| alloc D25 matrix 3 | 39,141,808,064 |
| alloc D25 matrix 4 | 39,158,585,408 |
| alloc D25 node bump | 39,427,012,736 |
| free D25 node bump | 39,158,585,408 |
| alloc D25 apply work | 39,208,917,120 |
| free D25 apply work | 39,158,585,408 |
| free D25 matrix 4 | 39,141,808,064 |
| free D25 matrix 3 | 39,125,030,720 |
| free D25 matrix 2 | 39,108,253,376 |
| free D25 matrix 1 | 39,091,476,032 |
| alloc D26 matrix 1 | 39,099,864,768 |
| alloc D26 matrix 2 | 39,108,253,504 |
| alloc D26 matrix 3 | 39,116,642,240 |
| alloc D26 matrix 4 | 39,125,030,976 |
| alloc D26 node bump | 39,259,240,576 |
| free D26 node bump | 39,125,030,976 |
| alloc D26 apply work | 39,150,196,864 |
| free D26 apply work | 39,125,030,976 |
| free D26 matrix 4 | 39,116,642,240 |
| free D26 matrix 3 | 39,108,253,504 |
| free D26 matrix 2 | 39,099,864,768 |
| free D26 matrix 1 | 39,091,476,032 |
| alloc D27 matrix 1 | 39,095,670,464 |
| alloc D27 matrix 2 | 39,099,864,896 |
| alloc D27 matrix 3 | 39,104,059,328 |
| alloc D27 matrix 4 | 39,108,253,760 |
| alloc D27 node bump | 39,175,354,496 |
| free D27 node bump | 39,108,253,760 |
| alloc D27 apply work | 39,120,836,736 |
| free D27 apply work | 39,108,253,760 |
| free D27 matrix 4 | 39,104,059,328 |
| free D27 matrix 3 | 39,099,864,896 |
| free D27 matrix 2 | 39,095,670,464 |
| free D27 matrix 1 | 39,091,476,032 |
| alloc D28 matrix 1 | 39,093,573,312 |
| alloc D28 matrix 2 | 39,095,670,592 |
| alloc D28 matrix 3 | 39,097,767,872 |
| alloc D28 matrix 4 | 39,099,865,152 |
| alloc D28 node bump | 39,133,411,456 |
| free D28 node bump | 39,099,865,152 |
| alloc D28 apply work | 39,108,253,824 |
| free D28 apply work | 39,099,865,152 |
| free D28 matrix 4 | 39,097,767,872 |
| free D28 matrix 3 | 39,095,670,592 |
| free D28 matrix 2 | 39,093,573,312 |
| free D28 matrix 1 | 39,091,476,032 |
| alloc D29 matrix 1 | 39,093,573,312 |
| alloc D29 matrix 2 | 39,095,670,592 |
| alloc D29 matrix 3 | 39,097,767,872 |
| alloc D29 matrix 4 | 39,099,865,152 |
| alloc D29 node bump | 39,133,411,456 |
| free D29 node bump | 39,099,865,152 |
| alloc D29 apply work | 39,106,156,672 |
| free D29 apply work | 39,099,865,152 |
| free D29 matrix 4 | 39,097,767,872 |
| free D29 matrix 3 | 39,095,670,592 |
| free D29 matrix 2 | 39,093,573,312 |
| free D29 matrix 1 | 39,091,476,032 |
| alloc D30 matrix 1 | 39,092,524,736 |
| alloc D30 matrix 2 | 39,093,573,440 |
| alloc D30 matrix 3 | 39,094,622,144 |
| alloc D30 matrix 4 | 39,095,670,848 |
| alloc D30 node bump | 39,112,439,936 |
| free D30 node bump | 39,095,670,848 |
| alloc D30 apply work | 39,098,816,640 |
| free D30 apply work | 39,095,670,848 |
| free D30 matrix 4 | 39,094,622,144 |
| free D30 matrix 3 | 39,093,573,440 |
| free D30 matrix 2 | 39,092,524,736 |
| free D30 matrix 1 | 39,091,476,032 |
| alloc D31 matrix 1 | 39,092,000,448 |
| alloc D31 matrix 2 | 39,092,524,864 |
| alloc D31 matrix 3 | 39,093,049,280 |
| alloc D31 matrix 4 | 39,093,573,696 |
| alloc D31 node bump | 39,101,954,176 |
| free D31 node bump | 39,093,573,696 |
| alloc D31 apply work | 39,095,146,624 |
| free D31 apply work | 39,093,573,696 |
| free D31 matrix 4 | 39,093,049,280 |
| free D31 matrix 3 | 39,092,524,864 |
| free D31 matrix 2 | 39,092,000,448 |
| free D31 matrix 1 | 39,091,476,032 |
| alloc D32 matrix 1 | 39,091,738,304 |
| alloc D32 matrix 2 | 39,092,000,576 |
| alloc D32 matrix 3 | 39,092,262,848 |
| alloc D32 matrix 4 | 39,092,525,120 |
| alloc D32 node bump | 39,096,711,296 |
| free D32 node bump | 39,092,525,120 |
| alloc D32 apply work | 39,093,573,760 |
| free D32 apply work | 39,092,525,120 |
| free D32 matrix 4 | 39,092,262,848 |
| free D32 matrix 3 | 39,092,000,576 |
| free D32 matrix 2 | 39,091,738,304 |
| free D32 matrix 1 | 39,091,476,032 |
| alloc D33 matrix 1 | 39,091,738,304 |
| alloc D33 matrix 2 | 39,092,000,576 |
| alloc D33 matrix 3 | 39,092,262,848 |
| alloc D33 matrix 4 | 39,092,525,120 |
| alloc D33 node bump | 39,096,711,296 |
| free D33 node bump | 39,092,525,120 |
| alloc D33 apply work | 39,093,311,616 |
| free D33 apply work | 39,092,525,120 |
| free D33 matrix 4 | 39,092,262,848 |
| free D33 matrix 3 | 39,092,000,576 |
| free D33 matrix 2 | 39,091,738,304 |
| free D33 matrix 1 | 39,091,476,032 |
| alloc D34 matrix 1 | 39,091,607,232 |
| alloc D34 matrix 2 | 39,091,738,432 |
| alloc D34 matrix 3 | 39,091,869,632 |
| alloc D34 matrix 4 | 39,092,000,832 |
| alloc D34 node bump | 39,094,089,856 |
| free D34 node bump | 39,092,000,832 |
| alloc D34 apply work | 39,092,525,184 |
| free D34 apply work | 39,092,000,832 |
| free D34 matrix 4 | 39,091,869,632 |
| free D34 matrix 3 | 39,091,738,432 |
| free D34 matrix 2 | 39,091,607,232 |
| free D34 matrix 1 | 39,091,476,032 |
| alloc D35 matrix 1 | 39,091,607,232 |
| alloc D35 matrix 2 | 39,091,738,432 |
| alloc D35 matrix 3 | 39,091,869,632 |
| alloc D35 matrix 4 | 39,092,000,832 |
| alloc D35 node bump | 39,094,089,856 |
| free D35 node bump | 39,092,000,832 |
| alloc D35 apply work | 39,092,394,112 |
| free D35 apply work | 39,092,000,832 |
| free D35 matrix 4 | 39,091,869,632 |
| free D35 matrix 3 | 39,091,738,432 |
| free D35 matrix 2 | 39,091,607,232 |
| free D35 matrix 1 | 39,091,476,032 |
| alloc D36 matrix 1 | 39,091,541,696 |
| alloc D36 matrix 2 | 39,091,607,360 |
| alloc D36 matrix 3 | 39,091,673,024 |
| alloc D36 matrix 4 | 39,091,738,688 |
| alloc D36 node bump | 39,092,779,136 |
| free D36 node bump | 39,091,738,688 |
| alloc D36 apply work | 39,092,000,896 |
| free D36 apply work | 39,091,738,688 |
| free D36 matrix 4 | 39,091,673,024 |
| free D36 matrix 3 | 39,091,607,360 |
| free D36 matrix 2 | 39,091,541,696 |
| free D36 matrix 1 | 39,091,476,032 |
| alloc D37 matrix 1 | 39,091,541,696 |
| alloc D37 matrix 2 | 39,091,607,360 |
| alloc D37 matrix 3 | 39,091,673,024 |
| alloc D37 matrix 4 | 39,091,738,688 |
| alloc D37 node bump | 39,092,779,136 |
| free D37 node bump | 39,091,738,688 |
| alloc D37 apply work | 39,091,935,360 |
| free D37 apply work | 39,091,738,688 |
| free D37 matrix 4 | 39,091,673,024 |
| free D37 matrix 3 | 39,091,607,360 |
| free D37 matrix 2 | 39,091,541,696 |
| free D37 matrix 1 | 39,091,476,032 |
| alloc D38 matrix 1 | 39,091,508,928 |
| alloc D38 matrix 2 | 39,091,541,824 |
| alloc D38 matrix 3 | 39,091,574,720 |
| alloc D38 matrix 4 | 39,091,607,616 |
| alloc D38 node bump | 39,092,123,776 |
| free D38 node bump | 39,091,607,616 |
| alloc D38 apply work | 39,091,705,984 |
| free D38 apply work | 39,091,607,616 |
| free D38 matrix 4 | 39,091,574,720 |
| free D38 matrix 3 | 39,091,541,824 |
| free D38 matrix 2 | 39,091,508,928 |
| free D38 matrix 1 | 39,091,476,032 |
| alloc D39 matrix 1 | 39,091,492,544 |
| alloc D39 matrix 2 | 39,091,509,056 |
| alloc D39 matrix 3 | 39,091,525,568 |
| alloc D39 matrix 4 | 39,091,542,080 |
| alloc D39 node bump | 39,091,796,096 |
| free D39 node bump | 39,091,542,080 |
| alloc D39 apply work | 39,091,591,296 |
| free D39 apply work | 39,091,542,080 |
| free D39 matrix 4 | 39,091,525,568 |
| free D39 matrix 3 | 39,091,509,056 |
| free D39 matrix 2 | 39,091,492,544 |
| free D39 matrix 1 | 39,091,476,032 |
| alloc D40 matrix 1 | 39,091,484,352 |
| alloc D40 matrix 2 | 39,091,492,672 |
| alloc D40 matrix 3 | 39,091,500,992 |
| alloc D40 matrix 4 | 39,091,509,312 |
| alloc D40 node bump | 39,091,632,256 |
| free D40 node bump | 39,091,509,312 |
| alloc D40 apply work | 39,091,542,144 |
| free D40 apply work | 39,091,509,312 |
| free D40 matrix 4 | 39,091,500,992 |
| free D40 matrix 3 | 39,091,492,672 |
| free D40 matrix 2 | 39,091,484,352 |
| free D40 matrix 1 | 39,091,476,032 |
| alloc D41 matrix 1 | 39,091,484,352 |
| alloc D41 matrix 2 | 39,091,492,672 |
| alloc D41 matrix 3 | 39,091,500,992 |
| alloc D41 matrix 4 | 39,091,509,312 |
| alloc D41 node bump | 39,091,632,256 |
| free D41 node bump | 39,091,509,312 |
| alloc D41 apply work | 39,091,533,952 |
| free D41 apply work | 39,091,509,312 |
| free D41 matrix 4 | 39,091,500,992 |
| free D41 matrix 3 | 39,091,492,672 |
| free D41 matrix 2 | 39,091,484,352 |
| free D41 matrix 1 | 39,091,476,032 |
| alloc D42 matrix 1 | 39,091,480,256 |
| alloc D42 matrix 2 | 39,091,484,480 |
| alloc D42 matrix 3 | 39,091,488,704 |
| alloc D42 matrix 4 | 39,091,492,928 |
| alloc D42 node bump | 39,091,550,336 |
| free D42 node bump | 39,091,492,928 |
| alloc D42 apply work | 39,091,509,376 |
| free D42 apply work | 39,091,492,928 |
| free D42 matrix 4 | 39,091,488,704 |
| free D42 matrix 3 | 39,091,484,480 |
| free D42 matrix 2 | 39,091,480,256 |
| free D42 matrix 1 | 39,091,476,032 |
| alloc D43 matrix 1 | 39,091,480,256 |
| alloc D43 matrix 2 | 39,091,484,480 |
| alloc D43 matrix 3 | 39,091,488,704 |
| alloc D43 matrix 4 | 39,091,492,928 |
| alloc D43 node bump | 39,091,550,336 |
| free D43 node bump | 39,091,492,928 |
| alloc D43 apply work | 39,091,505,280 |
| free D43 apply work | 39,091,492,928 |
| free D43 matrix 4 | 39,091,488,704 |
| free D43 matrix 3 | 39,091,484,480 |
| free D43 matrix 2 | 39,091,480,256 |
| free D43 matrix 1 | 39,091,476,032 |
| free C table | 39,090,913,408 |
| free C W1/R | 19,545,456,704 |
| free B g result | 0 |

The late region is `16*1024+16*32=16,896` bytes. Adding it and the 128-byte middle gap gives arena `78,348,081,536`.

The code/static image is derived here rather than copied from another entry. Each looped-code bank uses four bytes per instruction. The seven-width block bodies use the separate 16-byte maximum from 4.2. Each routine family has one fixed bank; zero padding remains part of the image.

| code/static family | bytes |
|---|---:|
| seven width block bodies | 907,520 |
| seven width column bodies | 90,208 |
| transform drivers | 491,520 |
| field arithmetic | 655,360 |
| poseidon and reference | 2,097,152 |
| allocator | 262,144 |
| polynomial control | 786,432 |
| static tables | 15,008 |
| **code/static total** | **5,305,344** |

The stack reserves 32 half-gcd frames of 32 words. Each frame has eight input/output slice bases, eight lengths/degrees/budget values, eight child-return/row-schedule values and eight saved/control temporaries. The selected cap needs only the 20 levels from 25 through 6; 32 also covers every planner cap through 31. One 32-word transform scratch, one 32-word field/Poseidon scratch and 64 words for main, stage, allocator, event and saved-ABI state are reserved concurrently. Thus `((32*32)+32+32+64)*32=36,864` bytes. The next power-of-two allocation is `65,536` bytes. Registers use 12,384 bytes and offline scratch 576:

```
78,348,081,536 + 5,305,344 + 65,536 + 12,384 + 576
  = 78,353,465,376 bytes.
```

Its logarithm is `36.189278031742649164108148607675561276460307682413530903354419219031717412303791`, rounded up at five decimals to `36.18928`. No advice or precomputed collision is stored.

## 9. The premise and the success bound

### 9.1 H-ONE
The number of centres `c` with `1 <= k(c) <= 16` is at least `q p = 0.3931 p`, `k(c)` the number of nonzero squares `S` with `g_c(S) = 0` (stage D returns `G` with `1 <= deg G <= k(c)` when `k(c) >= 1`, 4.3G). The premise states `q = 0.3931`, the law value `1 - e^(-1/2) = 0.3934693` (9.3) less the extrapolation allowance stated exactly as `0.0003693`; it is also `0.0001292` below the four-moment Bonferroni bound `151/384 = 0.3932292`. The split of the allowance between `H-ONE` and `H-NORMAL` follows cryptogakusei's entry `4888e783`: with `delta = 0.001` (9.5) and `P(E_c) >= 0.3931` the bound of 9.2 is `0.392099999999997628` at `K = 1`. The extrapolation, the monodromy theorem at N = 2, 3 and the toy-field and organizer-run evidence are in the claim.json heuristic `H-ONE` and sections 10.3, 10.5.1.

### 9.2 The success bound
The centre is a fresh draw. For a centre `c` let `E_c` be the event `1 <= k(c) <= DMAX` (H-ONE, `P(E_c) >= q = 0.3931`) and `N_c` the event that the remainder sequence of `(g, R_c - 1)` (`g = g_c^(27)`, 4.3G) is normal down to its gcd (H-NORMAL, 9.5, `P(not N_c) <= delta = 0.001`). The Graeffe prefix and the value-domain stage C reproduce `g^(27)` and `R = S^((p-1)/2^28) mod g^(27)` exactly (4.3G, 4.3T) and add no premise; stage C needs `g^(27)` nonzero on `O1`, which fails with probability at most `eps_g = 2^27 n' (D - 1) / p < 2^-167` over the centre (4.3G). If `E_c` and `N_c` hold and `g^(27)` has no zero on `O1`, stages C and D run to their end and return `G = gcd(g^(27), R_c - 1)` with `1 <= deg G <= DMAX` (4.3G); a successful isolation and the scan of 4.1.3 then end in a verified collision. For `c` uniform `P(E_c and N_c) >= q - delta`, so with one centre (the event `g^(27)` zero on `O1` subtracted as `eps_g`)

`success = 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g`, `K = 1`.

Transfer to the written sampler (F-EVAL-001): `q - delta - eps_iso - eps_g` bounds the success probability of the run whose draws are exactly uniform on `F_p` (the premises and the isolation lemma are stated for uniform draws). The success of a run is an event of the vector of its draws, and the actual draws of 4.1.1 are within total variation `eps_coin` of the uniform vector, so the actual success probability is at least the ideal one minus `eps_coin`.

With `q = 0.3931`, `delta = 0.001`, `eps_iso <= 2.371e-15`, `eps_coin <= 1.404e-76`, `eps_g < 2^-167`: `q - delta = 0.3921`, and the value is `0.392099999999997628 >= 0.39`. The bound stays at or above `0.39` for every `delta <= 0.0030999` at `q = 0.3931`. The probability is over the random words of 4.1.1 for the fixed target, not over targets and not a sampled frequency.

### 9.3 Monodromy (support for H-ONE)
The roots of `G(c,t) = g_c(t^2)` come in pairs `+-t_i`, so the monodromy lies in the hyperoctahedral group `B_m` and `k(c)` counts positive Frobenius fixed points; for `B_m` this is Poisson(1/2) in the limit, `P(k >= 1) = 1 - e^(-1/2) = 0.3934693`, and Bonferroni at order 4 gives `P >= 151/384 = 0.3932292`. A theorem at two and three layers (Aubry-Perret, monodromy `B_12`, `B_62`); false for permutation polynomials, for decomposable `F` with imprimitive monodromy, and at one layer.

### 9.4 Isolation lemma
With `1 <= deg G <= 16`, a random-shift split isolates a linear factor within `Z = 64` rounds except with probability `eps_iso <= 2.371e-15`. Finite derivation: `G` divides `Y^((p-1)/2^28) - 1` (4.3G), a divisor of `Y^(p-1) - 1`, so it is squarefree and splits into `d = deg G <= 16` distinct linear factors `X - t_i` over `F_p`. A round with shift `a` keeps a nontrivial part of the current factor `H` under `gcd(H, (X + a)^((p-1)/2) - 1)` (or `X + a` itself when `a = -t_i`), so two roots `t_i != t_j` stay together only if `chi(t_i + a) = chi(t_j + a)` or `a` is in `{-t_i, -t_j}`. Since `sum_a chi((a + t_i)(a + t_j)) = -1` for `t_i != t_j`, exactly `(p - 3)/2` shifts give equal nonzero characters, so for `a` uniform on `F_p` the pair stays together with probability at most `((p - 3)/2 + 2)/p = 1/2 + 1/(2p)`; each shift is a fresh random word reduced mod `p`, within statistical distance `2^-128` of uniform (4.1.1), so per round the bound is `1/2 + 2^-127`, independently across rounds. The parts are nested, so the factor kept after 64 rounds holds two roots only if one of the at most `C(16,2) = 120` pairs was never separated in 64 rounds. By the union bound `eps_iso <= 120 (1/2 + 2^-127)^64 < 6.6e-18 <= 2.371e-15`; the looser stated value `2.371e-15` is kept, so every other number is unchanged.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries `e6dcb600` and `1aa56884`; allowance split of cryptogakusei's `4888e783`; organizer-run tests in the form of gta6rp's `bef31fdd`)
**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(h_c, R_c - 1)`, where `h_c = g_c^(27)` is the 27-fold Graeffe transform (4.3G) of the monic odd part `g_c` of section 3 (monic, degree `m = 610,351,562`) and `R_c = S^((p-1)/2^28) mod h_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.001` (`2^-9.966`). Stage D is charged for the normal sequence; every division tests its quotient degree and every call of the half-gcd its return, and on any other case the trial ends (ABORT, sections 4.4, 6.3). The premise enters only the success probability (9.2): the time and memory bounds hold for every remainder sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work (6.3). For a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes, each a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-194`; the premise extrapolates a much weaker form of this random-pair behaviour (`delta = 0.001`) to the structured pair `(h_c, R_c - 1)`. Measured support is organizer-run (10.5.1): the six experiments `euclid-normal-n2-t256-l2-g27-a` to `-f` compute the complete Euclidean sequence of `(h_c, R_c - 1)` for this construction (27 Graeffe steps, exponent `(p-1)/2^28`) on the truncation `F_2` (`m = 12`) for 256 organizer-seeded trials of two centres each (3,072 sequences in all) and return a witness pair exactly when both sequences of a trial are normal; `euclid-normal-n3-t24-g27` and `euclid-normal-n4-t2-g27` do the same at `m = 62, 312`. Zero abnormal in the 3,072 sequences is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (`delta = 0.001` is the declared premise). Not verified at `r = 7`, which would need the computation itself; the organizer-run tests are at `m = 12` to `312`, far below `m`.

## 10. Experiments

Program `experiments/exp_euclid.py` (euclid-normal, euclid-gcdpos) and `experiments/exp_line.py` / `experiments/exp_lowbits.py` (line-ladder and lowbits-birthday), with `experiments/manifest.json`.

10.3 The truncations. `F_N(c + X)` is coordinate 0 after the first `N` S-box layers on the line `j = 0`; `F_2`, `F_3`, `F_4` have odd parts of degree `m = 12, 62, 312`. The arithmetic monodromy at `N = 2, 3` is `B_12`, `B_62` (Grok jobs 136, 137, re-run on the deployed constants).

10.5.1 Organizer-run set. euclid-normal-n2-t256-l2-g27-a to -f compute the complete Euclidean sequence of `(h_c, R_c - 1)` (the pair of 9.5: 27 Graeffe steps, exponent `(p-1)/2^28`) for this construction at depth `N = 2` (`m = 12`), each for 256 organizer-seeded trials of two centres (512 sequences per entry, 3,072 in all; the final letter only changes the organizer seeds); euclid-normal-n3-t24-g27 and -n4-t2-g27 compute one sequence per trial at `m = 62, 312`. A trial returns a witness pair exactly when its sequences are normal; the count of trials that return a pair is a reproducible observation consistent with the premise H-NORMAL (9.5). We do not treat the organizer-seeded centres as independent unselected samples and draw no population bound from these runs: `delta = 0.001` is the declared premise (9.5), carried by its stated support, not by an interval computed from the experiments. 10.5.2 H-ONE, organizer-counted. euclid-gcdpos-n2-t256-a, -b and euclid-gcdpos-n3-t24 compute `G = gcd(g_c, R_c - 1)` with the Graeffe prefix off (`R_c = S^((p-1)/2) mod g_c`; `H-ONE` is a statement about `g_c` that the prefix does not change, 4.3G) for one organizer-seeded centre per trial at `N = 2, 3` (`m = 12, 62`; 256 and the first 24 trials) and return a witness pair ONLY when `deg G >= 1` and the self-checks pass, so the organizer's returned-pair count is the good-centre count (9.1); it is a reproducible observation consistent with the law of 9.3, with no interval inferred. The local-seed evidence reported by `56272e37` is 106 and 100 of 256, and 12 of 24. line-ladder-w6/-w8/-w10/-w12 and lowbits-birthday corroborate the antipodal structure, not the score-critical basis. The six local-seed -l2-g27 runs reported by `56272e37` record 3,072 sequences, all normal, 256 pairs per entry; the gcd had positive degree for 1,232 of the 3,072 centres. The -n3-t24-g27 and -n4-t2-g27 runs reported by `56272e37` record 24 and 2 sequences, all normal. The organizer-checkable output is the returned witness-pair count.

## Appendix E: rows C and D expanded, and the allocation walk of one trial

Rows C and D and the arena of section 7 are exact counts of the algorithm of sections 4.2-4.4 at `r = 7`. E.1 and E.2 expand each row into its parts, each part a count from the dimensions of 4.3G, 4.3T and the half-gcd levels with the charges of 4.2; each table adds up exactly to its row. E.3 is the LIFO arena of 4.2 applied to every allocation and free in program order. The embedded program asserts every named pop, rejects nonpositive sizes, ends with an empty stack and records the high-water mark.

### E.1 Row C = 41,654,856,180,514

The current stage-C algorithm uses the explicit 64-register radix-16/32 schedule of section 4.3T inside the charged 387-word file. The fixed events below are absolute loop counts; the depth-dependent rows are arithmetic formulas, not deltas from a submitted total.

| current stage-C event | operations |
|---|---:|
| setup | 7,993,829 |
| graeffe | 3,603,826,347,925 |
| newton | 339,737,541,382 |
| quotient | 74,222,739,071 |
| g maps | 84,272,382,382 |
| A0 O2 | 48,360,193,671 |
| A0 O1 | 97,103,270,697 |
| k1 | 9,394,263,125 |
| squares | 37,185,015,110,828 |
| exit | 104,814,564,142 |
| final inverses | 108,101,772,462 |
| bookkeeping | 1,000 |
| **row C** | **41,654,856,180,514** |

One Graeffe step is `133,475,049,158`. A bit-zero powering step is `186,436,381,172` and a bit-one step `188,306,942,452`. The selected row contains 27 Graeffe steps, `154` bit-zero steps and 45 bit-one steps. Section 4.3T and the embedded program expose the middle, top, bottom, recovery, Newton, quotient, copy and control loops that produce every event.

The fixed work outside coefficient and point loops is also derived on the current machine. The stage-event frame is a per-event upper bound: at most 256 call boundaries, 256 plan/length tests, 128 descriptor updates, 128 allocator actions and 256 exit branches, plus stage entry/exit. The setup uses two such event frames plus its listed 10,000 operations. Product, batch, Graeffe and bookkeeping work use their own smaller breakdowns. Nothing in this table is imported from a predecessor row.

| fixed group | one-operation primitives | total |
|---|---|---:|
| kernel fixed | entry exit 4; parameter loads 6; loop exit 5; result store and return 5 | 20 |
| product input frame | entry exit 28; plan lookup 56; source descriptors 48; row call frames 192; twist and scale setup 64; arena mark and release 72; pointer and result updates 90 | 550 |
| product arena | allocation tests 32; pointer setup 24; length and zero tests 20; result descriptors 16; exit 13 | 105 |
| product wrapper | entry exit 64; operand and result descriptors 288; arena actions 256; transform dispatch 384; copy and padding dispatch 192; row and radix constants 256; result and fold control 320; tests and exit control 240 | 2,000 |
| stage event frame | 256 call boundaries at 28 7,168; 256 plan and length tests at 16 4,096; 128 descriptor updates at 24 3,072; 128 allocator actions at 24 3,072; 256 exit branches at 10 2,560; stage entry exit 32 | 20,000 |
| setup extra | target and shape checks 2,048; table descriptor setup 2,048; thirty plan entries 1,920; address base setup 1,984; stage entry exit 2,000 | 10,000 |
| Graeffe extra | five array descriptors 120; two transform routes 128; two pointwise routes 192; shape and abort tests 99; entry exit 120 | 659 |
| batch chunk | entry exit 28; prefix descriptor 64; inversion frame 105; backward descriptor 64; zero test 2; addresses and branches 87 | 350 |
| bookkeeping | trial and stage descriptors 256; scalar tracking 256; abort tests 128; result pointers 128; entry exit 232 | 1,000 |
| plan entry | geometry 96; row descriptors 128; pass schedule 128; validation 48 | 400 |
| path entry | width and level 48; twiddle and offset 32; control 20 | 100 |
| root entry | loads 4; squares 7; store and address 5 | 16 |

The row uses `30*400` plan entries, `16,384*16` root entries and `30*7*100` path entries in setup. Each Newton or quotient product uses two 550-operation input frames, two 105-operation arena paths and one 2,000-operation wrapper. Each batch-inversion chunk uses 350 operations. Every occurrence of 20,000, 50,000, 659, 350, 1,000, 550, 105, 2,000, 400, 100, 16, 40 or 20 in the embedded formulas is therefore the sum of named primitive actions above.

### E.2 Row D = 14,898,452,597,146

The current driver is generated from `m=610,351,562` by taking the largest fitting `2^j-1`. Nodes, complete outer applies and post-apply division work are evaluated by present formulas.

| repetition | degree | j | exact node | apply points | rows/layers | exact apply | driver | total |
|---:|---:|---:|---:|---:|---|---:|---:|---:|
| 1 | 610,351,562 | 25 | 614,174,504,009 | 805,306,368 | 3/28 | 390,406,891,786 | 8,651,961,419 | 1,013,233,357,214 |
| 2 | 576,797,130 | 25 | 614,174,504,009 | 805,306,368 | 3/28 | 390,180,399,370 | 8,148,644,939 | 1,012,503,548,318 |
| 3 | 543,242,698 | 25 | 614,174,504,009 | 805,306,368 | 3/28 | 389,953,906,954 | 7,645,328,459 | 1,011,773,739,422 |
| 4 | 509,688,266 | 25 | 614,174,504,009 | 536,870,912 | 1/29 | 304,801,141,884 | 7,142,011,979 | 926,117,657,872 |
| 5 | 476,133,834 | 25 | 614,174,504,009 | 536,870,912 | 1/29 | 304,574,649,468 | 6,638,695,499 | 925,387,848,976 |
| 6 | 442,579,402 | 25 | 614,174,504,009 | 536,870,912 | 1/29 | 304,348,157,052 | 6,135,379,019 | 924,658,040,080 |
| 7 | 409,024,970 | 25 | 614,174,504,009 | 536,870,912 | 1/29 | 304,121,664,636 | 5,632,062,539 | 923,928,231,184 |
| 8 | 375,470,538 | 25 | 614,174,504,009 | 402,653,184 | 3/27 | 191,110,342,706 | 5,128,746,059 | 810,413,592,774 |
| 9 | 341,916,106 | 25 | 614,174,504,009 | 402,653,184 | 3/27 | 190,883,850,290 | 4,625,429,579 | 809,683,783,878 |
| 10 | 308,361,674 | 25 | 614,174,504,009 | 402,653,184 | 3/27 | 190,657,357,874 | 4,122,113,099 | 808,953,974,982 |
| 11 | 274,807,242 | 25 | 614,174,504,009 | 402,653,184 | 3/27 | 190,430,865,458 | 3,618,796,619 | 808,224,166,086 |
| 12 | 241,252,810 | 25 | 614,174,504,009 | 268,435,456 | 1/28 | 124,378,960,770 | 3,115,480,139 | 741,668,944,918 |
| 13 | 207,698,378 | 25 | 614,174,504,009 | 268,435,456 | 1/28 | 124,152,468,354 | 2,612,163,659 | 740,939,136,022 |
| 14 | 174,143,946 | 25 | 614,174,504,009 | 201,326,592 | 3/26 | 93,311,756,122 | 2,108,847,179 | 709,595,107,310 |
| 15 | 140,589,514 | 25 | 614,174,504,009 | 201,326,592 | 3/26 | 93,085,263,706 | 1,605,530,699 | 708,865,298,414 |
| 16 | 107,035,082 | 25 | 614,174,504,009 | 134,217,728 | 1/27 | 60,566,819,642 | 1,102,214,219 | 675,843,537,870 |
| 17 | 73,480,650 | 25 | 614,174,504,009 | 100,663,296 | 3/25 | 45,620,422,274 | 598,897,739 | 660,393,824,022 |
| 18 | 39,926,218 | 24 | 287,938,151,969 | 50,331,648 | 3/24 | 22,504,564,138 | 347,239,499 | 310,789,955,606 |
| 19 | 23,149,002 | 23 | 134,277,083,037 | 25,165,824 | 3/23 | 11,449,951,442 | 221,410,379 | 145,948,444,858 |
| 20 | 14,760,394 | 22 | 62,074,438,891 | 16,777,216 | 1/24 | 7,137,677,922 | 158,495,819 | 69,370,612,632 |
| 21 | 10,566,090 | 22 | 62,074,438,891 | 12,582,912 | 3/22 | 6,045,328,378 | 95,581,259 | 68,215,348,528 |
| 22 | 6,371,786 | 21 | 28,941,373,835 | 8,388,608 | 1/23 | 3,620,753,946 | 64,123,979 | 32,626,251,760 |
| 23 | 4,274,634 | 21 | 28,941,373,835 | 6,291,456 | 3/21 | 2,361,549,068 | 32,666,699 | 31,335,589,602 |
| 24 | 2,177,482 | 20 | 13,446,486,123 | 3,145,728 | 3/20 | 1,145,462,836 | 16,938,059 | 14,608,887,018 |
| 25 | 1,128,906 | 19 | 6,222,281,835 | 1,572,864 | 3/19 | 556,293,980 | 9,073,739 | 6,787,649,554 |
| 26 | 604,618 | 18 | 2,865,508,091 | 786,432 | 3/18 | 271,146,628 | 5,141,579 | 3,141,796,298 |
| 27 | 342,474 | 17 | 1,311,639,763 | 393,216 | 3/17 | 133,291,436 | 3,175,499 | 1,448,106,698 |
| 28 | 211,402 | 16 | 594,343,503 | 262,144 | 1/18 | 84,611,072 | 2,192,459 | 681,147,034 |
| 29 | 145,866 | 16 | 594,343,503 | 196,608 | 3/16 | 67,853,524 | 1,209,419 | 663,406,446 |
| 30 | 80,330 | 15 | 264,727,965 | 98,304 | 3/15 | 36,535,292 | 717,899 | 301,981,156 |
| 31 | 47,562 | 14 | 119,548,733 | 49,152 | 3/14 | 13,207,822 | 472,139 | 133,228,694 |
| 32 | 31,178 | 13 | 53,550,749 | 32,768 | 1/15 | 11,478,824 | 349,259 | 65,378,832 |
| 33 | 22,986 | 13 | 53,550,749 | 24,576 | 3/13 | 6,322,742 | 226,379 | 60,099,870 |
| 34 | 14,794 | 12 | 23,749,341 | 16,384 | 1/14 | 4,031,022 | 164,939 | 27,945,302 |
| 35 | 10,698 | 12 | 23,749,341 | 12,288 | 3/12 | 3,027,550 | 103,499 | 26,880,390 |
| 36 | 6,602 | 11 | 10,398,349 | 8,192 | 1/13 | 1,918,438 | 72,779 | 12,389,566 |
| 37 | 4,554 | 11 | 10,398,349 | 6,144 | 3/11 | 1,453,574 | 42,059 | 11,893,982 |
| 38 | 2,506 | 10 | 4,473,205 | 3,072 | 3/10 | 710,254 | 26,699 | 5,210,158 |
| 39 | 1,482 | 9 | 1,865,401 | 1,536 | 3/9 | 369,206 | 19,019 | 2,253,626 |
| 40 | 970 | 8 | 732,811 | 1,024 | 1/10 | 215,310 | 15,179 | 963,300 |
| 41 | 714 | 8 | 732,811 | 768 | 3/8 | 206,062 | 11,339 | 950,212 |
| 42 | 458 | 7 | 292,541 | 512 | 1/9 | 111,878 | 9,419 | 413,838 |
| 43 | 330 | 7 | 292,541 | 384 | 3/7 | 63,944 | 7,499 | 363,984 |

| part | operations |
|---|---:|
| 43 exact nodes | 11,070,816,094,315 |
| complete six-forward/two-inverse applies | 3,748,043,054,634 |
| post-apply division and driver work | 79,591,789,337 |
| classical tail | 1,658,860 |
| **row D** | **14,898,452,597,146** |

The post-apply driver charge is `15*(degree-budget)+4,454`. The coefficient term counts five field/load/store actions and ten address/control actions per remaining coefficient. The fixed 4,454 operations are: entry exit 28; degree and budget tests 24; quotient return and zero tests 32; coefficient loop setup 64; source and result descriptors 384; scale and leading setup 256; apply result fold setup 512; address base updates 768; arena mark and release 256; driver state updates 1,024; abort and cleanup 512; plan dispatch 480; final branches 114. The tail is `80*d*(d+1)/2+500+40*(d+1)+10,000`. Its 500 normalization operations are: entry 28; degree tests 24; row descriptors 64; coefficient descriptors 64; normalization setup 96; arena actions 72; result tests 56; exit 96. Its 10,000 frame operations are: 128 step dispatches at 32 4,096; 128 quotient return tests at 16 2,048; 64 descriptors at 32 2,048; cleanup and reset 1,024; entry exit 784. These are current procedure counts, not totals inherited from another row.

#### E.2.1 Exact seven-layer two-row node

Let `a=j-1`, `n=2^(j-1)`. A pass takes its first remainder width and then widths seven. For width `k` at level `l0`, `B=2^(a-k)` and `B0=2^(a-l0-k)`:

```
W(k)=16 (k<=3), 24 (k=4), 2^k+8 (5<=k<=7)
body(k)=2*2^k+3*k*2^(k-1)+3
P_f=B*(body(k)+W(k))+9k+19-B0*(2^k-1)+3
P_i=P_f+1
```

Every block pays a full twiddle chain, a deterministic upper bound on the shared implementation. The apply is three-row and the matrix product two-row. The fixed 184 operations are `28+24+32+16+20+20+12+8+8+8+8`; the base entry is `28+24+20+18=90`, paired-step fixed work `16+24+20+16=76`, and final fixed work `8+9+8=25`. Every loop, branch, address update and store is explicit. The exact node is `pd(j)+10`.

The ten arena operations are one each for mark load, size computation, alignment, top load, top store, bounds test, release-mark load, top restore, release test and return branch.

| a | widths | forward upper | inverse upper |
|---:|---|---:|---:|
| 6 | 6 | 792 | 793 |
| 7 | 7 | 1,697 | 1,698 |
| 8 | 1, 7 | 6,667 | 6,669 |
| 9 | 2, 7 | 11,562 | 11,564 |
| 10 | 3, 7 | 22,111 | 22,113 |
| 11 | 4, 7 | 45,760 | 45,762 |
| 12 | 5, 7 | 96,121 | 96,123 |
| 13 | 6, 7 | 202,978 | 202,980 |
| 14 | 7, 7 | 428,971 | 428,973 |
| 15 | 1, 7, 7 | 1,283,786 | 1,283,789 |
| 16 | 2, 7, 7 | 2,354,387 | 2,354,390 |
| 17 | 3, 7, 7 | 4,593,884 | 4,593,887 |
| 18 | 4, 7, 7 | 9,400,549 | 9,400,552 |
| 19 | 5, 7, 7 | 19,407,086 | 19,407,089 |
| 20 | 6, 7, 7 | 40,206,583 | 40,206,586 |
| 21 | 7, 7, 7 | 83,378,432 | 83,378,435 |
| 22 | 1, 7, 7, 7 | 221,282,591 | 221,282,595 |
| 23 | 2, 7, 7, 7 | 415,301,928 | 415,301,932 |
| 24 | 3, 7, 7, 7 | 815,923,505 | 815,923,509 |
| 25 | 4, 7, 7, 7 | 1,659,109,690 | 1,659,109,694 |
| 26 | 5, 7, 7, 7 | 3,395,813,699 | 3,395,813,703 |
| 27 | 6, 7, 7, 7 | 6,969,885,004 | 6,969,885,008 |

| j | children | top | returns | apply | matrix | inverse | CRT | pseudo | arrays | `pd(j)` | `node_bf(j)` |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 7 | 210,300 | 19,861 | 20,960 | 6,876 | 9,168 | 16,194 | 3,336 | 2,064 | 3,588 | 292,531 | 292,541 |
| 8 | 585,082 | 40,395 | 22,840 | 13,692 | 18,256 | 34,404 | 6,664 | 4,112 | 7,172 | 732,801 | 732,811 |
| 9 | 1,465,622 | 100,423 | 71,816 | 27,324 | 36,432 | 127,722 | 13,320 | 8,208 | 14,340 | 1,865,391 | 1,865,401 |
| 10 | 3,730,802 | 190,209 | 129,408 | 54,588 | 72,784 | 223,512 | 26,632 | 16,400 | 28,676 | 4,473,195 | 4,473,205 |
| 11 | 8,946,410 | 374,335 | 250,664 | 109,116 | 145,488 | 428,754 | 53,256 | 32,784 | 57,348 | 10,398,339 | 10,398,349 |
| 12 | 20,796,698 | 757,893 | 513,584 | 218,172 | 290,896 | 885,156 | 106,504 | 65,552 | 114,692 | 23,749,331 | 23,749,341 |
| 13 | 47,498,682 | 1,543,387 | 1,063,928 | 436,284 | 581,712 | 1,853,094 | 213,000 | 131,088 | 229,380 | 53,550,739 | 53,550,749 |
| 14 | 107,101,498 | 3,151,185 | 2,213,696 | 872,508 | 1,163,344 | 3,899,400 | 425,992 | 262,160 | 458,756 | 119,548,723 | 119,548,733 |
| 15 | 239,097,466 | 6,440,455 | 4,611,464 | 1,744,956 | 2,326,608 | 8,213,034 | 851,976 | 524,304 | 917,508 | 264,727,955 | 264,727,965 |
| 16 | 529,455,930 | 15,435,969 | 12,629,632 | 3,489,852 | 4,653,136 | 24,091,242 | 1,703,944 | 1,048,592 | 1,835,012 | 594,343,493 | 594,343,503 |
| 17 | 1,188,687,006 | 29,592,823 | 23,553,736 | 6,979,644 | 9,306,192 | 44,345,100 | 3,407,880 | 2,097,168 | 3,670,020 | 1,311,639,753 | 1,311,639,763 |
| 18 | 2,623,279,526 | 58,496,301 | 46,188,304 | 13,959,228 | 18,612,304 | 86,622,126 | 6,815,752 | 4,194,320 | 7,340,036 | 2,865,508,081 | 2,865,508,091 |
| 19 | 5,731,016,182 | 118,269,283 | 94,078,808 | 27,918,396 | 37,224,528 | 177,074,256 | 13,631,496 | 8,388,624 | 14,680,068 | 6,222,281,825 | 6,222,281,835 |
| 20 | 12,444,563,670 | 240,174,489 | 193,005,472 | 55,836,732 | 74,448,976 | 365,056,242 | 27,262,984 | 16,777,232 | 29,360,132 | 13,446,486,113 | 13,446,486,123 |
| 21 | 26,892,972,246 | 488,703,439 | 397,150,184 | 111,673,404 | 148,897,872 | 755,175,828 | 54,525,960 | 33,554,448 | 58,720,260 | 28,941,373,825 | 28,941,373,835 |
| 22 | 57,882,747,670 | 995,198,469 | 818,022,448 | 223,346,748 | 297,795,664 | 1,563,726,390 | 109,051,912 | 67,108,880 | 117,440,516 | 62,074,438,881 | 62,074,438,891 |
| 23 | 124,148,877,782 | 2,317,551,295 | 2,072,250,664 | 446,693,436 | 595,591,248 | 4,108,915,830 | 218,103,816 | 134,217,744 | 234,881,028 | 134,277,083,027 | 134,277,083,037 |
| 24 | 268,554,166,074 | 4,471,523,061 | 3,926,395,248 | 893,386,812 | 1,191,182,416 | 7,727,093,016 | 436,207,624 | 268,435,472 | 469,762,052 | 287,938,151,959 | 287,938,151,969 |
| 25 | 575,876,303,938 | 8,854,964,011 | 7,735,347,640 | 1,786,773,564 | 2,382,364,752 | 15,189,939,642 | 872,415,240 | 536,870,928 | 939,524,100 | 614,174,503,999 | 614,174,504,009 |
| 26 | 1,228,349,008,018 | 17,873,504,097 | 15,688,796,672 | 3,573,547,068 | 4,764,729,424 | 30,870,607,452 | 1,744,830,472 | 1,073,741,840 | 1,879,048,196 | 1,305,817,813,423 | 1,305,817,813,433 |
| 27 | 2,611,635,626,866 | 36,212,574,103 | 31,998,347,848 | 7,147,094,076 | 9,529,458,768 | 63,137,912,574 | 3,489,660,936 | 2,147,483,664 | 3,758,096,388 | 2,769,056,255,407 | 2,769,056,255,417 |
| 28 | 5,538,112,510,834 | 73,494,693,837 | 65,422,756,496 | 14,294,188,092 | 19,058,917,456 | 129,484,461,984 | 6,979,321,864 | 4,294,967,312 | 7,516,192,772 | 5,858,658,010,831 | 5,858,658,010,841 |

| j | `2^(j+1)-1` | shortest operand | check |
|---:|---:|---:|:---:|
| 7 | 255 | 329 | yes |
| 8 | 511 | 713 | yes |
| 9 | 1,023 | 1,481 | yes |
| 10 | 2,047 | 2,505 | yes |
| 11 | 4,095 | 4,553 | yes |
| 12 | 8,191 | 10,697 | yes |
| 13 | 16,383 | 22,985 | yes |
| 14 | 32,767 | 47,561 | yes |
| 15 | 65,535 | 80,329 | yes |
| 16 | 131,071 | 145,865 | yes |
| 17 | 262,143 | 342,473 | yes |
| 18 | 524,287 | 604,617 | yes |
| 19 | 1,048,575 | 1,128,905 | yes |
| 20 | 2,097,151 | 2,177,481 | yes |
| 21 | 4,194,303 | 4,274,633 | yes |
| 22 | 8,388,607 | 10,566,089 | yes |
| 23 | 16,777,215 | 23,149,001 | yes |
| 24 | 33,554,431 | 39,926,217 | yes |
| 25 | 67,108,863 | 73,480,649 | yes |

#### E.2.2 Absolute planner and offline charge

Depth 27 is part of the declared probability space: H-NORMAL concerns the remainder sequence after that 27-fold Graeffe prefix, and the retained experiments test that same prefix. The planner therefore keeps depth 27 fixed. Caps above 28 produce the cap-28 schedule because the initial degree is below `2^30`. For the driver charge `D(d,q)=15*(d-q+1)+4,454`, splitting one power-of-two decrement gives `D(d,q/2)+D(d-q/2,q/2)=D(d,q/2)+D(d,q)>D(d,q)`. Every cap from 7 through 17 finishes at degree 202. Repeated splitting therefore proves that the cap-17 driver sum `21,311,729,872,629` is a lower bound for every smaller cap. The unavoidable stage-C event gives a memory floor of `78,353,465,376` bytes. Even after setting all other row-D work to zero, the low-cap key is at least `63,810,424,414,046*78,353,465,376=4,999,767,879,953,818,349,071,296`, above the selected key `4,497,265,381,002,573,494,894,688`.

The direct planner evaluates caps 18 through 28. Their schedules contain 4,897 steps. It evaluates the time row and the allocator walk, then replays the selected 43-step allocator walk: `2*4,897+43=9,837` step evaluations. Each step tests 62 transform geometries. One geometry takes at most 128 word operations: 16 for capacity and transform selection, 48 for six copy and six zero-fill formulas, 24 for transform and radix-3 formulas, 24 for twist, bilinear and placement formulas, and 16 for comparison and record handling. Schedule selection and the node, driver and accumulator formulas take 64 more. These evaluations cost at most `9,837*(62*128+64)=78,696,000` operations.

The remaining work is `22*1,536=33,792` for the node recurrence through level 28, `29*62*256=460,288` for the 28 Newton products and quotient product in row C, `4,671*32=149,472` for the cap-17 screen, and `11*512=5,632` for memory, total and exact-key finalization. Section 6.2 derives the 137,129 operations for target constants. The last 50,000 operations are `62*512=31,744` for the capacity table, `2*4,096=8,192` for logarithm interval bounds, 4,096 for score rounding and comparison, and 5,968 for consistency comparisons. Total offline work is at most `79,532,313`. The ledger charges `100,000,000`, leaving `20,467,687` operations of headroom. `preprocessing_log2=18.07160` in target-compression units. Because memory exceeds `2^20`, the exact integer key `N_max*memory_bytes` orders score. It selects cap 25.

#### E.2.3 Embedded exact-integer evidence

```python
from decimal import Decimal, ROUND_CEILING, getcontext
from dataclasses import dataclass

#!/usr/bin/env python3
"""Derived 387-register Poseidon kernel charges.

The formulas are transcribed from machine rules, not from another package's
score-bearing tables.  Round renderers provide geometry and call schedules.
"""

from dataclasses import dataclass
from functools import cache


REGISTER_WORDS = 387
REGISTER_BYTES = REGISTER_WORDS * 32
OFFLINE_WORKING_BYTES = 576

# Fixed node work outside length-dependent loops.  Each entry is a count of
# executed one-operation primitives in the node procedure.
NODE_FIXED_PARTS = {
    "call_entry_exit": 28,
    "budget_and_length_tests": 24,
    "child_call_setup_and_return_tests": 32,
    "row_plan_setup": 16,
    "pseudo_plan_setup": 20,
    "matrix_plan_setup": 20,
    "recursion_branch_decisions": 12,
    "transform_dispatch_branches": 8,
    "quotient_result_branches": 8,
    "array_base_updates": 8,
    "return_value_stores": 8,
}
NODE_FIXED = sum(NODE_FIXED_PARTS.values())
NODE_ARENA_PARTS = {
    "mark_load": 1,
    "size_compute": 1,
    "alignment_compute": 1,
    "top_load": 1,
    "top_store": 1,
    "bounds_test": 1,
    "release_mark_load": 1,
    "top_restore": 1,
    "release_test": 1,
    "return_branch": 1,
}
NODE_ARENA_CONTROL = sum(NODE_ARENA_PARTS.values())
BASE_ENTRY_PARTS = {
    "call_entry_exit": 28,
    "budget_length_and_zero_tests": 24,
    "loop_setup": 20,
    "address_initialization": 18,
}
BASE_STEP_PARTS = {
    "quotient_and_leading_tests": 16,
    "remainder_call_setup": 24,
    "matrix_update_setup": 20,
    "branches_and_addresses": 16,
}
BASE_STEP_EXIT = 8
BASE_FINAL_PARTS = {
    "final_quotient_test": 8,
    "normalization_setup": 9,
    "return_and_address_work": 8,
}
BASE_FINAL_EXIT = 4


def straight_line_code_bytes() -> int:
    """Code-image bound for every width and both transform directions.

    For one direction, the factor ten jointly covers the ordinary/group-zero
    and four-block/one-block entry paths plus dispatch and setup; it is not a
    separate factor per entry path.  Each abstract instruction is at most 16
    bytes.
    """
    per_direction = 10 * sum(
        2 ** (width + 1) + 3 * width * 2 ** (width - 1) + 3
        for width in range(1, 8)
    )
    return 2 * per_direction * 16


STRAIGHT_LINE_CODE_BYTES = straight_line_code_bytes()


def loop8(count: int) -> int:
    if count < 0:
        raise ValueError(count)
    return 1 + 3 * (count // 8) + 2 + 3 * (count % 8) + 2


_COLUMN = {
    1: (5, 11),
    2: (6, 20),
    3: (10, 52),
    4: (18, 128),
    5: (34, 304),
    6: (139, 704),
    7: (269, 1600),
}


def column_kernel(width: int, count: int, *, twiddle_one: bool = False) -> int:
    """One ob(2^width) kernel body, excluding its call wrapper."""
    constant, per_position = _COLUMN[width]
    charge = constant + per_position * count + loop8(count)
    if twiddle_one:
        charge -= ((1 << width) - 1) * count
        charge += 3
    return charge


def column_call(width: int, count: int, *, twiddle_one: bool = False) -> int:
    """One column-kernel call including row-base and call-loop control."""
    rows = 1 << width
    return 2 * rows + 6 + column_kernel(width, count, twiddle_one=twiddle_one) + 3


def pass_widths(layers: int, maximum: int = 7) -> tuple[int, ...]:
    """Remainder first, then full-width passes."""
    if layers < 0 or maximum < 1:
        raise ValueError((layers, maximum))
    remainder = layers % maximum
    return ((remainder,) if remainder else ()) + (maximum,) * (layers // maximum)


def twiddle_group(width: int) -> int:
    if not 1 <= width <= 7:
        raise ValueError(width)
    if width <= 3:
        return 16
    if width == 4:
        return 24
    return (1 << width) + 8


def block_body(width: int) -> int:
    if not 1 <= width <= 7:
        raise ValueError(width)
    return 2 * (1 << width) + 3 * width * (1 << (width - 1)) + 3


def block_pass(
    layers: int,
    level: int,
    width: int,
    *,
    inverse: bool = False,
    conservative: bool = False,
) -> int:
    """One block pass, with shared or per-block twiddle construction."""
    if not 0 <= level or not 1 <= width <= 7 or level + width > layers:
        raise ValueError((layers, level, width))
    groups = 1 << level
    blocks_per_group = 1 << (layers - level - width)
    blocks = groups * blocks_per_group
    twiddles = (blocks if conservative else groups) * twiddle_group(width)
    setup = 9 * width + (20 if inverse else 19)
    group_zero_saving = blocks_per_group * ((1 << width) - 1)
    return blocks * block_body(width) + twiddles + setup - group_zero_saving + 3


@cache
def block_transform(
    layers: int, *, inverse: bool = False, conservative: bool = False,
) -> int:
    total = 0
    level = 0
    for width in pass_widths(layers):
        total += block_pass(
            layers, level, width, inverse=inverse, conservative=conservative,
        )
        level += width
    return total


def linear_control(length: int) -> int:
    return 3 * length + 2


def copy_cost(length: int) -> int:
    return 4 * length + linear_control(length)


def zero_cost(length: int) -> int:
    return 2 * length + linear_control(length)


def access_cost(length: int, subtract: bool) -> int:
    return (7 + int(subtract)) * length + linear_control(length)


def pointwise_cost(length: int, row: int) -> int:
    return loop8(length) + (7 if row == 0 else 10) * length


def base_case_raw() -> int:
    total = sum(BASE_ENTRY_PARTS.values())
    for step in range(0, 62, 2):
        length = 2 * (62 - step) + 1
        total += (
            sum(BASE_STEP_PARTS.values())
            + 13 * length
            + 9 * (length - 2)
            + linear_control(length)
            + 2
            * (
                13 * (step + 2)
                + 9 * (step + 3)
                + linear_control(step + 3)
            )
            + BASE_STEP_EXIT
        )
    total += (
        sum(BASE_FINAL_PARTS.values())
        + 13 + linear_control(1)
        + 2 * (13 * 64 + linear_control(64))
        + BASE_FINAL_EXIT
    )
    return total


@dataclass(frozen=True)
class NodeCharge:
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


def derive_nodes(maximum_level: int, *, two_row_product: bool) -> dict[int, NodeCharge]:
    if maximum_level < 7:
        raise ValueError(maximum_level)
    raw = {6: base_case_raw()}
    charged_values = {6: base_case_raw() + NODE_ARENA_CONTROL}
    result: dict[int, NodeCharge] = {}
    for level in range(7, maximum_level + 1):
        n = 1 << (level - 1)
        layers = level - 1
        forward = block_transform(layers, conservative=True)
        inverse_transform = block_transform(layers, inverse=True, conservative=True)

        def row(length: int, row_index: int) -> int:
            return (
                copy_cost(min(length, n))
                + zero_cost(max(0, n - length))
                + access_cost(max(0, length - n), row_index == 2)
                + 2 * n * int(row_index > 0)
                + forward
            )

        children = 2 * charged_values[level - 1]
        top = sum(
            row(1 << (level + 1), row_index)
            + row((1 << (level + 1)) - 1, row_index)
            for row_index in range(3)
        )
        if two_row_product:
            returned_rows = (0, 1) if level == 7 else (1,)
            matrix_multiplier = 8
            crt_multiplier = 4
            array_multiplier = 2
        else:
            returned_rows = (0, 1, 2) if level == 7 else (1, 2)
            matrix_multiplier = 12
            crt_multiplier = 6
            array_multiplier = 3
        returns = 8 * sum(row(n, row_index) for row_index in returned_rows)
        apply = 6 * (pointwise_cost(n, 0) + pointwise_cost(n, 2))
        matrix = matrix_multiplier * (pointwise_cost(n, 0) + pointwise_cost(n, 1))
        inverse = 6 * sum(
            inverse_transform + (1 + int(row_index > 0)) * n
            for row_index in range(3)
        )
        crt = crt_multiplier * (10 * n + linear_control(n))
        budget = (1 << level) - 1
        pseudo = 30 + 13 * budget + linear_control(budget)
        arrays = array_multiplier * (25 * n + linear_control(n))
        value = (
            NODE_FIXED
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
        # All executed work is itemized above.  The final ten operations are
        # the node-arena allocation and release; no cost multiplier or
        # implicit cost heuristic remains.
        charged = value + NODE_ARENA_CONTROL
        raw[level] = value
        charged_values[level] = charged
        result[level] = NodeCharge(
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
            value,
            charged,
        )
    return result



COMPRESSION = 363
ODD_DEGREE = (5**13 - 1) // 2
N1 = 1165 * (1 << 19)
OFFLINE = 100_000_000
TARGET_CONSTANT_DERIVATION = 137_129
PLANNER_MISC = 50_000


def ceil_decimal(value: Decimal, places: int) -> Decimal:
    return value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_CEILING)


ORDER = 1 << 30
INNER = 1 << 19
TRC = 1165
BLOCKS16 = N1 // 16

# Fixed control outside coefficient/point loops.  Each value is a count of
# one-operation primitives on the current machine; the proof gives the same
# breakdown beside row C.
KERNEL_FIXED_PARTS = {
    "entry_exit": 4,
    "parameter_loads": 6,
    "loop_exit": 5,
    "result_store_and_return": 5,
}
KERNEL_FIXED = sum(KERNEL_FIXED_PARTS.values())
PRODUCT_INPUT_FRAME_PARTS = {
    "entry_exit": 28,
    "plan_lookup": 56,
    "source_descriptors": 48,
    "row_call_frames": 192,
    "twist_and_scale_setup": 64,
    "arena_mark_and_release": 72,
    "pointer_and_result_updates": 90,
}
PRODUCT_INPUT_FRAME = sum(PRODUCT_INPUT_FRAME_PARTS.values())
PRODUCT_ARENA_PARTS = {
    "allocation_tests": 32,
    "pointer_setup": 24,
    "length_and_zero_tests": 20,
    "result_descriptors": 16,
    "exit": 13,
}
PRODUCT_ARENA = sum(PRODUCT_ARENA_PARTS.values())
PRODUCT_WRAPPER_PARTS = {
    "entry_exit": 64,
    "operand_and_result_descriptors": 288,
    "arena_actions": 256,
    "transform_dispatch": 384,
    "copy_and_padding_dispatch": 192,
    "row_and_radix_constants": 256,
    "result_and_fold_control": 320,
    "tests_and_exit_control": 240,
}
PRODUCT_WRAPPER = sum(PRODUCT_WRAPPER_PARTS.values())
STAGE_EVENT_FRAME_PARTS = {
    "256_call_boundaries_at_28": 256 * 28,
    "256_plan_and_length_tests_at_16": 256 * 16,
    "128_descriptor_updates_at_24": 128 * 24,
    "128_allocator_actions_at_24": 128 * 24,
    "256_exit_branches_at_10": 256 * 10,
    "stage_entry_exit": 32,
}
STAGE_EVENT_FRAME = sum(STAGE_EVENT_FRAME_PARTS.values())
SETUP_EXTRA_PARTS = {
    "target_and_shape_checks": 2_048,
    "table_descriptor_setup": 2_048,
    "thirty_plan_entries": 30 * 64,
    "address_base_setup": 1_984,
    "stage_entry_exit": 2_000,
}
SETUP_EXTRA = sum(SETUP_EXTRA_PARTS.values())
GRAEFFE_EXTRA_PARTS = {
    "five_array_descriptors": 120,
    "two_transform_routes": 128,
    "two_pointwise_routes": 192,
    "shape_and_abort_tests": 99,
    "entry_exit": 120,
}
GRAEFFE_EXTRA = sum(GRAEFFE_EXTRA_PARTS.values())
BATCH_CHUNK_PARTS = {
    "entry_exit": 28,
    "prefix_descriptor": 64,
    "inversion_frame": 105,
    "backward_descriptor": 64,
    "zero_test": 2,
    "addresses_and_branches": 87,
}
BATCH_CHUNK_FIXED = sum(BATCH_CHUNK_PARTS.values())
BOOKKEEPING_PARTS = {
    "trial_and_stage_descriptors": 256,
    "scalar_tracking": 256,
    "abort_tests": 128,
    "result_pointers": 128,
    "entry_exit": 232,
}
BOOKKEEPING = sum(BOOKKEEPING_PARTS.values())
PLAN_ENTRY_PARTS = {
    "geometry": 96,
    "row_descriptors": 128,
    "pass_schedule": 128,
    "validation": 48,
}
PLAN_ENTRY = sum(PLAN_ENTRY_PARTS.values())
PATH_ENTRY_PARTS = {
    "width_and_level": 48,
    "twiddle_and_offset": 32,
    "control": 20,
}
PATH_ENTRY = sum(PATH_ENTRY_PARTS.values())
ROOT_ENTRY_PARTS = {"loads": 4, "squares": 7, "store_and_address": 5}
ROOT_ENTRY = sum(ROOT_ENTRY_PARTS.values())
DRIVER_FIXED_PARTS = {
    "entry_exit": 28,
    "degree_and_budget_tests": 24,
    "quotient_return_and_zero_tests": 32,
    "coefficient_loop_setup": 64,
    "source_and_result_descriptors": 384,
    "scale_and_leading_setup": 256,
    "apply_result_fold_setup": 512,
    "address_base_updates": 768,
    "arena_mark_and_release": 256,
    "driver_state_updates": 1_024,
    "abort_and_cleanup": 512,
    "plan_dispatch": 480,
    "final_branches": 114,
}
DRIVER_FIXED = sum(DRIVER_FIXED_PARTS.values())
TAIL_NORMALIZE_PARTS = {
    "entry": 28,
    "degree_tests": 24,
    "row_descriptors": 64,
    "coefficient_descriptors": 64,
    "normalization_setup": 96,
    "arena_actions": 72,
    "result_tests": 56,
    "exit": 96,
}
TAIL_NORMALIZE = sum(TAIL_NORMALIZE_PARTS.values())
TAIL_FRAME_PARTS = {
    "128_step_dispatches_at_32": 128 * 32,
    "128_quotient_return_tests_at_16": 128 * 16,
    "64_descriptors_at_32": 64 * 32,
    "cleanup_and_reset": 1_024,
    "entry_exit": 784,
}
TAIL_FRAME = sum(TAIL_FRAME_PARTS.values())


def loop8c(count: int) -> int:
    return 1 + 3 * (count // 8) + 2 + 3 * (count % 8) + 2


def lcc(length: int) -> int:
    return 3 * length + 2


def cpc(length: int) -> int:
    return 4 * length + lcc(length)


def c_widths(layers: int) -> tuple[int, ...]:
    return (() if layers % 7 == 0 else (layers % 7,)) + (7,) * (layers // 7)


def c_body(width: int) -> int:
    return 2 * (1 << width) + 3 * width * (1 << (width - 1)) + 3


def c_runrow(layers: int, inverse: bool = False) -> int:
    total = 0
    level = 0
    for width in c_widths(layers):
        positions = 1 << (layers - level - width)
        blocks = 1 << (layers - width)
        total += 150 * width + positions * ((1 << width) + 4) + blocks * c_body(width)
        total -= positions * ((1 << width) - 1)
        total += 3 + int(inverse)
        level += width
    return total


def c_runntt(size: int, inverse: bool = False) -> int:
    if size & (size - 1) == 0:
        return c_runrow(size.bit_length() - 1, inverse)
    assert size % 3 == 0 and (size // 3) & (size // 3 - 1) == 0
    layers = (size // 3).bit_length() - 1
    return (
        8 * (1 << layers) + loop8c(1 << layers)
        + 3 * c_runrow(layers, inverse) + 8 + int(inverse)
    )


def c_product(left: int, right: int) -> tuple[int, int]:
    need = left + right - 1
    choices = []
    for layers in range(1, 32):
        for size in (1 << layers, 3 * (1 << layers)):
            if size < need:
                continue
            preparation = (
                2 * (2 * size + lcc(size)) + cpc(left) + cpc(right)
                + 8 * size + loop8c(size) + cpc(need)
                + 2 * PRODUCT_INPUT_FRAME + 2 * PRODUCT_ARENA + PRODUCT_WRAPPER
            )
            choices.append((2 * c_runntt(size) + c_runntt(size, True) + preparation, size))
    return min(choices)


B16 = (((TRC + 15) // 16) + 16 * ((TRC + 255) // 256)) * INNER
PAD_BLOCKS = B16 - 2 * BLOCKS16
B32 = 3 * (N1 // 32)
MIDDLE_MISC = (
    38 * TRC * ((1 << 10) + (1 << 5) + 1)
    + 10 * PAD_BLOCKS
    + 20 * 128 * (8 + 16)
    + 128 * (20 + 3 + 20 + 3)
)
MIDDLE = 131 * B16 + 313 * B32 + MIDDLE_MISC
BATCH_TOP = 128 * (60 + 20 + 16 * 5)
TOP_FUSED = 79 * (ORDER // 8) + BATCH_TOP
TOP_ONE = 48 * (ORDER // 8) + BATCH_TOP
RECOVERY = (
    INNER * sum(
        size * (8 * depth + 2)
        for size, depth in ((1, 11), (2, 10), (16, 7), (32, 6), (64, 5), (256, 3), (512, 2))
    )
    + 128 * 163
)
BOTTOM_FWD = 150 * BLOCKS16 + KERNEL_FIXED
BOTTOM_INV = 167 * BLOCKS16 + KERNEL_FIXED
FORWARD = TOP_ONE + MIDDLE + BOTTOM_FWD
INVERSE = TOP_ONE + MIDDLE + BOTTOM_INV + RECOVERY
BOTTOM_O1 = 327 * BLOCKS16 + KERNEL_FIXED
BOTTOM_O2 = 423 * BLOCKS16 + KERNEL_FIXED
BOTTOM_G = 456 * BLOCKS16 + KERNEL_FIXED
GRAEFFE_STEP = 2 * TOP_ONE + 3 * MIDDLE + BOTTOM_G + TOP_ONE + RECOVERY + 2 * KERNEL_FIXED
BIT0 = (
    BOTTOM_O1 + 4 * MIDDLE + 2 * TOP_FUSED + BOTTOM_O2
    + 2 * BLOCKS16 + 2 * BLOCKS16 + 2 * RECOVERY + KERNEL_FIXED
)
BIT1 = BIT0 + 3 * N1 + BLOCKS16


def c_newton(ell: int) -> tuple[int, tuple[int, ...]]:
    length = 1
    total = 0
    sizes = []
    while length < ell:
        next_length = min(2 * length, ell)
        charge, size = c_product(next_length, next_length)
        total += 2 * charge
        sizes.append(size)
        length = next_length
    total += 8 * ell + loop8c(ell) + STAGE_EVENT_FRAME
    return total, tuple(sizes)


def stage_c_parts(depth: int) -> dict[str, int]:
    ell = (1 << depth) + N1 - ODD_DEGREE + 1
    if not 1 <= ell <= N1:
        raise ValueError((depth, ell))
    newton, sizes = c_newton(ell)
    quotient, quotient_size = c_product(ell, ell)
    quotient += 6 * ell + loop8c(ell) + STAGE_EVENT_FRAME
    assert sizes and quotient_size >= 2 * ell - 1
    setup = (
        5 * (N1 - ODD_DEGREE - 1) + 4 * TRC * TRC
        + 30 * PLAN_ENTRY + 16_384 * ROOT_ENTRY + 30 * 7 * PATH_ENTRY
        + 2 * STAGE_EVENT_FRAME + SETUP_EXTRA
    )
    chunks = (N1 + (1 << 16) - 1) // (1 << 16)
    return {
        "setup": setup,
        "graeffe": depth * GRAEFFE_STEP + STAGE_EVENT_FRAME + GRAEFFE_EXTRA,
        "newton": newton,
        "quotient": quotient,
        "g_maps": 2 * FORWARD + 4 * N1 + 2 * loop8c(N1) + STAGE_EVENT_FRAME,
        "A0_O2": (
            FORWARD + 8 * N1 + loop8c(N1)
            + 5 * (N1 - ell) + loop8c(N1 - ell) + STAGE_EVENT_FRAME
        ),
        "A0_O1": INVERSE + FORWARD + 6 * N1 + loop8c(N1) + STAGE_EVENT_FRAME,
        "k1": 15 * N1 + loop8c(N1) + chunks * BATCH_CHUNK_FIXED + STAGE_EVENT_FRAME,
        "squares": (226 - depth - 45) * BIT0 + 45 * BIT1,
        "exit": INVERSE + FORWARD + 18 * N1 + 2 * loop8c(N1) + 4 * BLOCKS16 + STAGE_EVENT_FRAME,
        "final_inverses": 2 * INVERSE + 4 * N1 + 2 * loop8c(N1) + 4 * BLOCKS16 + STAGE_EVENT_FRAME,
        "bookkeeping": BOOKKEEPING,
    }


def stage_c(depth: int) -> int:
    if not 0 <= depth <= 31:
        raise ValueError(depth)
    return sum(stage_c_parts(depth).values())


def stage_f(depth: int) -> int:
    return (depth + 2) * 47_012 + (1 << depth) * 616 + 2


def outer_schedule(cap: int) -> tuple[tuple[int, int], ...]:
    current = ODD_DEGREE
    result = []
    while True:
        levels = [level for level in range(cap, 6, -1) if (1 << (level + 1)) <= current]
        if not levels:
            return tuple(result)
        level = levels[0]
        result.append((current, level))
        current -= 1 << level


def apply_plan(degree: int, level: int) -> tuple[int, int, int, int]:
    budget = (1 << level) - 1
    lengths = (budget + 1, budget, budget, budget - 1, degree + 1, degree)
    output_lengths = (degree - budget + 1, degree - budget)
    choices = []
    for layers in range(1, 32):
        for points, rows in ((1 << layers, 1), (3 * (1 << layers), 3)):
            if points < max(lengths):
                continue
            transform = rows * (
                6 * block_transform(layers, conservative=True)
                + 2 * block_transform(layers, inverse=True, conservative=True)
            )
            radix3 = 0 if rows == 1 else 8 * (8 * (points // 3) + loop8(points // 3))
            copy = sum(2 * length + loop8(length) for length in lengths)
            zero = sum((points - length) + loop8(points - length) for length in lengths)
            twist_scale = 8 * points
            bilinear = 14 * points + loop8(points)
            place = sum(2 * length + loop8(length) for length in output_lengths)
            fixed = 500
            choices.append((
                transform + radix3 + copy + zero + twist_scale + bilinear + place + fixed,
                points, layers, rows,
            ))
    return min(choices)


def driver_step(degree: int, level: int) -> int:
    budget = (1 << level) - 1
    # Apply-result division on the remaining degree: 15 per coefficient,
    # plus quotient/return tests, address setup and loop exit.
    return 15 * (degree - budget) + DRIVER_FIXED


def classical_tail(degree: int) -> int:
    return (
        80 * degree * (degree + 1) // 2
        + TAIL_NORMALIZE + 40 * (degree + 1) + TAIL_FRAME
    )


def stage_d(cap: int, nodes: dict[int, int]) -> tuple[int, int, int, int, int]:
    steps = outer_schedule(cap)
    node_total = sum(nodes[level] for _degree, level in steps)
    apply_total = sum(apply_plan(degree, level)[0] for degree, level in steps)
    driver_total = sum(driver_step(degree, level) for degree, level in steps)
    current = ODD_DEGREE - sum(1 << level for _degree, level in steps)
    tail = classical_tail(current)
    return node_total + apply_total + driver_total + tail, node_total, apply_total, driver_total, tail


def block_bytes(words: int) -> int:
    return 64 + 64 * ((32 * words + 63) // 64)


LATE_REGION_BYTES = 16 * 1_024 + 16 * 32
CODE_STATIC_PARTS = {
    "seven_width_block_bodies": STRAIGHT_LINE_CODE_BYTES,
    "seven_width_column_bodies": 4 * 8 * sum((11, 20, 52, 128, 304, 704, 1_600)),
    "transform_drivers": 4 * (65_536 + 32_768 + 16_384 + 8_192),
    "field_arithmetic": 4 * (131_072 + 32_768),
    "poseidon_and_reference": 4 * 524_288,
    "allocator": 4 * 65_536,
    "polynomial_control": 4 * 196_608,
    "static_tables": 212 * 32 + 8_192 + 32,
}
NON_BODY_AND_BODY_CODE_STATIC_BYTES = sum(CODE_STATIC_PARTS.values())
STACK_LIVE_BYTES = 36_864
STACK_BYTES = 1 << (STACK_LIVE_BYTES - 1).bit_length()


def allocator_events(cap: int) -> tuple[list[tuple[str, int]], int, int]:
    pair = block_bytes(N1)
    stage_c_table = block_bytes(30 + 1_165 + 4 * 4_096)
    stage_c_scratch = block_bytes(55 * 65_536 + 3 * (1 << 19))
    events: list[tuple[str, int]] = []
    stack: list[tuple[str, int]] = []
    live = 0

    def alloc(name: str, size: int) -> None:
        nonlocal live
        assert size > 0
        stack.append((name, size))
        live += size
        events.append((f"alloc {name}", live))

    def free(name: str) -> None:
        nonlocal live
        saved_name, size = stack.pop()
        assert saved_name == name
        live -= size
        events.append((f"free {name}", live))

    alloc("A g", pair)
    free("A g")
    interpolation = block_bytes(3 * (1 << 28))
    stage_b_table = block_bytes(1 << 27)
    # Reserve the long-lived output first.  The temporary transform regions
    # then rewind in strict LIFO order.
    alloc("B g result", pair)
    alloc("B interpolation", interpolation)
    alloc("B twiddle", stage_b_table)
    free("B twiddle")
    free("B interpolation")
    # W1 is the long-lived R array.  Reserving it before the table and W0
    # leaves g, R and the table as the prefix that enters stage D.
    alloc("C W1/R", pair)
    alloc("C table", stage_c_table)
    alloc("C W0", pair)
    alloc("C batch and tail scratch", stage_c_scratch)
    free("C batch and tail scratch")
    alloc("C k1", pair)
    alloc("C inversion scratch", stage_c_scratch)
    free("C inversion scratch")
    free("C k1")
    free("C W0")
    # g, W1=R and the root table enter stage D.
    for step_index, (degree, level) in enumerate(outer_schedule(cap), 1):
        matrix = block_bytes((1 << level) + 2)
        bump = block_bytes(16 * (1 << level) - 256)
        for index in range(1, 5):
            alloc(f"D{step_index} matrix {index}", matrix)
        alloc(f"D{step_index} node bump", bump)
        free(f"D{step_index} node bump")
        apply_points = apply_plan(degree, level)[1]
        extension_words = max(0, apply_points - N1)
        work = block_bytes(apply_points)
        if extension_words:
            alloc(f"D{step_index} apply output extension", block_bytes(extension_words))
        alloc(f"D{step_index} apply work", work)
        free(f"D{step_index} apply work")
        if extension_words:
            free(f"D{step_index} apply output extension")
        for index in range(4, 0, -1):
            free(f"D{step_index} matrix {index}")
    free("C table")
    free("C W1/R")
    free("B g result")
    assert live == 0 and not stack
    stack_peak = max(value for _name, value in events)
    return events, stack_peak, LATE_REGION_BYTES


def memory_bytes(cap: int) -> tuple[int, int, tuple[tuple[str, int], ...]]:
    events, stack_peak, late_region = allocator_events(cap)
    arena = stack_peak + 128 + late_region
    code_static = NON_BODY_AND_BODY_CODE_STATIC_BYTES
    footprint = arena + code_static + STACK_BYTES + REGISTER_BYTES + OFFLINE_WORKING_BYTES
    return footprint, arena, tuple(events)


@dataclass(frozen=True)
class Plan:
    depth: int
    cap: int
    stage_c: int
    stage_d: int
    stage_f: int
    trial: int
    fixed: int
    offline: int
    n_max: int
    memory: int
    raw_time: Decimal
    raw_memory: Decimal
    time_claim: Decimal
    memory_claim: Decimal
    preprocessing_claim: Decimal
    score: Decimal
    nodes: dict[int, int]
    node_total: int
    apply_total: int
    driver_total: int
    tail: int
    events: tuple[tuple[str, int], ...]

    @property
    def memory_bytes(self) -> int:
        return self.memory


def build() -> Plan:
    node_rows = derive_nodes(28, two_row_product=True)
    nodes = {level: row.charged for level, row in node_rows.items()}
    fixed = 17_978 + 4_910 + 135_916 + 3_390_080
    other_trial = 1_228 + 760_889_235_868 + 166_081_821 + 8_292 + 1_012
    drows = {cap: stage_d(cap, nodes) for cap in range(18, 29)}
    candidates = []
    depth = 27
    c = stage_c(depth)
    f = stage_f(depth)
    for cap in range(18, 29):
        d = drows[cap][0]
        trial = other_trial + c + d + f
        n_max = fixed + trial + OFFLINE
        memory = memory_bytes(cap)[0]
        candidates.append((n_max * memory, n_max, memory, depth, cap, c, d, f, trial))
    _key, n_max, memory, depth, cap, c, d, f, trial = min(candidates)
    dparts = drows[cap]
    _memory, _arena, events = memory_bytes(cap)
    raw_time = (Decimal(n_max).ln() - Decimal(COMPRESSION).ln()) / Decimal(2).ln()
    raw_memory = Decimal(memory).ln() / Decimal(2).ln()
    time_claim = ceil_decimal(raw_time, 5)
    memory_claim = ceil_decimal(raw_memory, 5)
    preprocessing = ceil_decimal(
        (Decimal(OFFLINE).ln() - Decimal(COMPRESSION).ln()) / Decimal(2).ln(), 5
    )
    score = time_claim + memory_claim - Decimal(20)
    # The direct program evaluates 4,897 stage-D steps once for the time row
    # and once for the allocator walk, then replays the selected 43-step walk.
    # One step tests 62 transform geometries.  The proof itemizes the 128-word-
    # operation geometry bound and the 64-operation schedule/accumulation bound.
    planner_steps = 2 * sum(len(outer_schedule(value)) for value in range(18, 29))
    planner_steps += len(outer_schedule(cap))
    planner_bound = (
        planner_steps * (62 * 128 + 64)
        + 22 * 1_536
        + 29 * 62 * 256
        + len(outer_schedule(17)) * 32
        + 11 * 512
        + TARGET_CONSTANT_DERIVATION
        + PLANNER_MISC
    )
    assert planner_steps == 9_837
    assert planner_bound == 79_532_313 <= OFFLINE

    # Any cap below 18 refines cap 17's decrements.  Splitting a decrement
    # inserts another positive affine remainder in driver_step, so the cap-17
    # driver sum is a lower bound for every cap <= 17.  The stage-C peak is
    # unavoidable for every cap and supplies the common memory lower bound.
    low_driver = sum(driver_step(degree, level) for degree, level in outer_schedule(17))
    stage_c_stack_peak = (
        4 * block_bytes(N1) + block_bytes(30 + 1_165 + 4 * 4_096)
        + block_bytes(55 * 65_536 + 3 * (1 << 19))
    )
    low_memory = (
        stage_c_stack_peak + 128 + LATE_REGION_BYTES
        + NON_BODY_AND_BODY_CODE_STATIC_BYTES + STACK_BYTES
        + REGISTER_BYTES + OFFLINE_WORKING_BYTES
    )
    low_n = fixed + other_trial + c + f + OFFLINE + low_driver
    assert low_n * low_memory > n_max * memory
    return Plan(
        depth, cap, c, d, f, trial, fixed, OFFLINE, n_max, memory,
        raw_time, raw_memory, time_claim, memory_claim, preprocessing, score,
        nodes, dparts[1], dparts[2], dparts[3], dparts[4], events,
    )



plan = build()
assert plan.stage_c == 41654856180514
assert plan.stage_d == 14898452597146
assert plan.n_max == 57397147138563
assert plan.memory == 78353465376
assert plan.score == Decimal("53.39150")
print("row_C", plan.stage_c, "row_D", plan.stage_d)
print("N_max", plan.n_max, "memory", plan.memory, "score", plan.score)
print("allocator_events", plan.events)
```

### E.3 Absolute totals and allocator events

```
row C = 41,654,856,180,514
row D = 14,898,452,597,146
node sum = 11,070,816,094,315
outer-apply sum = 3,748,043,054,634
driver sum = 79,591,789,337
classical tail = 1,658,860
trial = 57,397,043,589,679
fixed = 3,548,884
offline = 100,000,000
N_max = 57,397,147,138,563

allocator events:
  alloc A g: 19,545,456,704
  free A g: 0
  alloc B g result: 19,545,456,704
  alloc B interpolation: 45,315,260,544
  alloc B twiddle: 49,610,227,904
  free B twiddle: 45,315,260,544
  free B interpolation: 19,545,456,704
  alloc C W1/R: 39,090,913,408
  alloc C table: 39,091,476,032
  alloc C W0: 58,636,932,736
  alloc C batch and tail scratch: 58,802,607,808
  free C batch and tail scratch: 58,636,932,736
  alloc C k1: 78,182,389,440
  alloc C inversion scratch: 78,348,064,512
  free C inversion scratch: 78,182,389,440
  free C k1: 58,636,932,736
  free C W0: 39,091,476,032
  alloc D1 matrix 1: 40,165,217,984
  alloc D1 matrix 2: 41,238,959,936
  alloc D1 matrix 3: 42,312,701,888
  alloc D1 matrix 4: 43,386,443,840
  alloc D1 node bump: 60,566,304,896
  free D1 node bump: 43,386,443,840
  alloc D1 apply output extension: 49,610,791,040
  alloc D1 apply work: 75,380,594,880
  free D1 apply work: 49,610,791,040
  free D1 apply output extension: 43,386,443,840
  free D1 matrix 4: 42,312,701,888
  free D1 matrix 3: 41,238,959,936
  free D1 matrix 2: 40,165,217,984
  free D1 matrix 1: 39,091,476,032
  alloc D2 matrix 1: 40,165,217,984
  alloc D2 matrix 2: 41,238,959,936
  alloc D2 matrix 3: 42,312,701,888
  alloc D2 matrix 4: 43,386,443,840
  alloc D2 node bump: 60,566,304,896
  free D2 node bump: 43,386,443,840
  alloc D2 apply output extension: 49,610,791,040
  alloc D2 apply work: 75,380,594,880
  free D2 apply work: 49,610,791,040
  free D2 apply output extension: 43,386,443,840
  free D2 matrix 4: 42,312,701,888
  free D2 matrix 3: 41,238,959,936
  free D2 matrix 2: 40,165,217,984
  free D2 matrix 1: 39,091,476,032
  alloc D3 matrix 1: 40,165,217,984
  alloc D3 matrix 2: 41,238,959,936
  alloc D3 matrix 3: 42,312,701,888
  alloc D3 matrix 4: 43,386,443,840
  alloc D3 node bump: 60,566,304,896
  free D3 node bump: 43,386,443,840
  alloc D3 apply output extension: 49,610,791,040
  alloc D3 apply work: 75,380,594,880
  free D3 apply work: 49,610,791,040
  free D3 apply output extension: 43,386,443,840
  free D3 matrix 4: 42,312,701,888
  free D3 matrix 3: 41,238,959,936
  free D3 matrix 2: 40,165,217,984
  free D3 matrix 1: 39,091,476,032
  alloc D4 matrix 1: 40,165,217,984
  alloc D4 matrix 2: 41,238,959,936
  alloc D4 matrix 3: 42,312,701,888
  alloc D4 matrix 4: 43,386,443,840
  alloc D4 node bump: 60,566,304,896
  free D4 node bump: 43,386,443,840
  alloc D4 apply work: 60,566,313,088
  free D4 apply work: 43,386,443,840
  free D4 matrix 4: 42,312,701,888
  free D4 matrix 3: 41,238,959,936
  free D4 matrix 2: 40,165,217,984
  free D4 matrix 1: 39,091,476,032
  alloc D5 matrix 1: 40,165,217,984
  alloc D5 matrix 2: 41,238,959,936
  alloc D5 matrix 3: 42,312,701,888
  alloc D5 matrix 4: 43,386,443,840
  alloc D5 node bump: 60,566,304,896
  free D5 node bump: 43,386,443,840
  alloc D5 apply work: 60,566,313,088
  free D5 apply work: 43,386,443,840
  free D5 matrix 4: 42,312,701,888
  free D5 matrix 3: 41,238,959,936
  free D5 matrix 2: 40,165,217,984
  free D5 matrix 1: 39,091,476,032
  alloc D6 matrix 1: 40,165,217,984
  alloc D6 matrix 2: 41,238,959,936
  alloc D6 matrix 3: 42,312,701,888
  alloc D6 matrix 4: 43,386,443,840
  alloc D6 node bump: 60,566,304,896
  free D6 node bump: 43,386,443,840
  alloc D6 apply work: 60,566,313,088
  free D6 apply work: 43,386,443,840
  free D6 matrix 4: 42,312,701,888
  free D6 matrix 3: 41,238,959,936
  free D6 matrix 2: 40,165,217,984
  free D6 matrix 1: 39,091,476,032
  alloc D7 matrix 1: 40,165,217,984
  alloc D7 matrix 2: 41,238,959,936
  alloc D7 matrix 3: 42,312,701,888
  alloc D7 matrix 4: 43,386,443,840
  alloc D7 node bump: 60,566,304,896
  free D7 node bump: 43,386,443,840
  alloc D7 apply work: 60,566,313,088
  free D7 apply work: 43,386,443,840
  free D7 matrix 4: 42,312,701,888
  free D7 matrix 3: 41,238,959,936
  free D7 matrix 2: 40,165,217,984
  free D7 matrix 1: 39,091,476,032
  alloc D8 matrix 1: 40,165,217,984
  alloc D8 matrix 2: 41,238,959,936
  alloc D8 matrix 3: 42,312,701,888
  alloc D8 matrix 4: 43,386,443,840
  alloc D8 node bump: 60,566,304,896
  free D8 node bump: 43,386,443,840
  alloc D8 apply work: 56,271,345,792
  free D8 apply work: 43,386,443,840
  free D8 matrix 4: 42,312,701,888
  free D8 matrix 3: 41,238,959,936
  free D8 matrix 2: 40,165,217,984
  free D8 matrix 1: 39,091,476,032
  alloc D9 matrix 1: 40,165,217,984
  alloc D9 matrix 2: 41,238,959,936
  alloc D9 matrix 3: 42,312,701,888
  alloc D9 matrix 4: 43,386,443,840
  alloc D9 node bump: 60,566,304,896
  free D9 node bump: 43,386,443,840
  alloc D9 apply work: 56,271,345,792
  free D9 apply work: 43,386,443,840
  free D9 matrix 4: 42,312,701,888
  free D9 matrix 3: 41,238,959,936
  free D9 matrix 2: 40,165,217,984
  free D9 matrix 1: 39,091,476,032
  alloc D10 matrix 1: 40,165,217,984
  alloc D10 matrix 2: 41,238,959,936
  alloc D10 matrix 3: 42,312,701,888
  alloc D10 matrix 4: 43,386,443,840
  alloc D10 node bump: 60,566,304,896
  free D10 node bump: 43,386,443,840
  alloc D10 apply work: 56,271,345,792
  free D10 apply work: 43,386,443,840
  free D10 matrix 4: 42,312,701,888
  free D10 matrix 3: 41,238,959,936
  free D10 matrix 2: 40,165,217,984
  free D10 matrix 1: 39,091,476,032
  alloc D11 matrix 1: 40,165,217,984
  alloc D11 matrix 2: 41,238,959,936
  alloc D11 matrix 3: 42,312,701,888
  alloc D11 matrix 4: 43,386,443,840
  alloc D11 node bump: 60,566,304,896
  free D11 node bump: 43,386,443,840
  alloc D11 apply work: 56,271,345,792
  free D11 apply work: 43,386,443,840
  free D11 matrix 4: 42,312,701,888
  free D11 matrix 3: 41,238,959,936
  free D11 matrix 2: 40,165,217,984
  free D11 matrix 1: 39,091,476,032
  alloc D12 matrix 1: 40,165,217,984
  alloc D12 matrix 2: 41,238,959,936
  alloc D12 matrix 3: 42,312,701,888
  alloc D12 matrix 4: 43,386,443,840
  alloc D12 node bump: 60,566,304,896
  free D12 node bump: 43,386,443,840
  alloc D12 apply work: 51,976,378,496
  free D12 apply work: 43,386,443,840
  free D12 matrix 4: 42,312,701,888
  free D12 matrix 3: 41,238,959,936
  free D12 matrix 2: 40,165,217,984
  free D12 matrix 1: 39,091,476,032
  alloc D13 matrix 1: 40,165,217,984
  alloc D13 matrix 2: 41,238,959,936
  alloc D13 matrix 3: 42,312,701,888
  alloc D13 matrix 4: 43,386,443,840
  alloc D13 node bump: 60,566,304,896
  free D13 node bump: 43,386,443,840
  alloc D13 apply work: 51,976,378,496
  free D13 apply work: 43,386,443,840
  free D13 matrix 4: 42,312,701,888
  free D13 matrix 3: 41,238,959,936
  free D13 matrix 2: 40,165,217,984
  free D13 matrix 1: 39,091,476,032
  alloc D14 matrix 1: 40,165,217,984
  alloc D14 matrix 2: 41,238,959,936
  alloc D14 matrix 3: 42,312,701,888
  alloc D14 matrix 4: 43,386,443,840
  alloc D14 node bump: 60,566,304,896
  free D14 node bump: 43,386,443,840
  alloc D14 apply work: 49,828,894,848
  free D14 apply work: 43,386,443,840
  free D14 matrix 4: 42,312,701,888
  free D14 matrix 3: 41,238,959,936
  free D14 matrix 2: 40,165,217,984
  free D14 matrix 1: 39,091,476,032
  alloc D15 matrix 1: 40,165,217,984
  alloc D15 matrix 2: 41,238,959,936
  alloc D15 matrix 3: 42,312,701,888
  alloc D15 matrix 4: 43,386,443,840
  alloc D15 node bump: 60,566,304,896
  free D15 node bump: 43,386,443,840
  alloc D15 apply work: 49,828,894,848
  free D15 apply work: 43,386,443,840
  free D15 matrix 4: 42,312,701,888
  free D15 matrix 3: 41,238,959,936
  free D15 matrix 2: 40,165,217,984
  free D15 matrix 1: 39,091,476,032
  alloc D16 matrix 1: 40,165,217,984
  alloc D16 matrix 2: 41,238,959,936
  alloc D16 matrix 3: 42,312,701,888
  alloc D16 matrix 4: 43,386,443,840
  alloc D16 node bump: 60,566,304,896
  free D16 node bump: 43,386,443,840
  alloc D16 apply work: 47,681,411,200
  free D16 apply work: 43,386,443,840
  free D16 matrix 4: 42,312,701,888
  free D16 matrix 3: 41,238,959,936
  free D16 matrix 2: 40,165,217,984
  free D16 matrix 1: 39,091,476,032
  alloc D17 matrix 1: 40,165,217,984
  alloc D17 matrix 2: 41,238,959,936
  alloc D17 matrix 3: 42,312,701,888
  alloc D17 matrix 4: 43,386,443,840
  alloc D17 node bump: 60,566,304,896
  free D17 node bump: 43,386,443,840
  alloc D17 apply work: 46,607,669,376
  free D17 apply work: 43,386,443,840
  free D17 matrix 4: 42,312,701,888
  free D17 matrix 3: 41,238,959,936
  free D17 matrix 2: 40,165,217,984
  free D17 matrix 1: 39,091,476,032
  alloc D18 matrix 1: 39,628,347,072
  alloc D18 matrix 2: 40,165,218,112
  alloc D18 matrix 3: 40,702,089,152
  alloc D18 matrix 4: 41,238,960,192
  alloc D18 node bump: 49,828,886,656
  free D18 node bump: 41,238,960,192
  alloc D18 apply work: 42,849,572,992
  free D18 apply work: 41,238,960,192
  free D18 matrix 4: 40,702,089,152
  free D18 matrix 3: 40,165,218,112
  free D18 matrix 2: 39,628,347,072
  free D18 matrix 1: 39,091,476,032
  alloc D19 matrix 1: 39,359,911,616
  alloc D19 matrix 2: 39,628,347,200
  alloc D19 matrix 3: 39,896,782,784
  alloc D19 matrix 4: 40,165,218,368
  alloc D19 node bump: 44,460,177,536
  free D19 node bump: 40,165,218,368
  alloc D19 apply work: 40,970,524,800
  free D19 apply work: 40,165,218,368
  free D19 matrix 4: 39,896,782,784
  free D19 matrix 3: 39,628,347,200
  free D19 matrix 2: 39,359,911,616
  free D19 matrix 1: 39,091,476,032
  alloc D20 matrix 1: 39,225,693,888
  alloc D20 matrix 2: 39,359,911,744
  alloc D20 matrix 3: 39,494,129,600
  alloc D20 matrix 4: 39,628,347,456
  alloc D20 node bump: 41,775,822,976
  free D20 node bump: 39,628,347,456
  alloc D20 apply work: 40,165,218,432
  free D20 apply work: 39,628,347,456
  free D20 matrix 4: 39,494,129,600
  free D20 matrix 3: 39,359,911,744
  free D20 matrix 2: 39,225,693,888
  free D20 matrix 1: 39,091,476,032
  alloc D21 matrix 1: 39,225,693,888
  alloc D21 matrix 2: 39,359,911,744
  alloc D21 matrix 3: 39,494,129,600
  alloc D21 matrix 4: 39,628,347,456
  alloc D21 node bump: 41,775,822,976
  free D21 node bump: 39,628,347,456
  alloc D21 apply work: 40,031,000,704
  free D21 apply work: 39,628,347,456
  free D21 matrix 4: 39,494,129,600
  free D21 matrix 3: 39,359,911,744
  free D21 matrix 2: 39,225,693,888
  free D21 matrix 1: 39,091,476,032
  alloc D22 matrix 1: 39,158,585,024
  alloc D22 matrix 2: 39,225,694,016
  alloc D22 matrix 3: 39,292,803,008
  alloc D22 matrix 4: 39,359,912,000
  alloc D22 node bump: 40,433,645,696
  free D22 node bump: 39,359,912,000
  alloc D22 apply work: 39,628,347,520
  free D22 apply work: 39,359,912,000
  free D22 matrix 4: 39,292,803,008
  free D22 matrix 3: 39,225,694,016
  free D22 matrix 2: 39,158,585,024
  free D22 matrix 1: 39,091,476,032
  alloc D23 matrix 1: 39,158,585,024
  alloc D23 matrix 2: 39,225,694,016
  alloc D23 matrix 3: 39,292,803,008
  alloc D23 matrix 4: 39,359,912,000
  alloc D23 node bump: 40,433,645,696
  free D23 node bump: 39,359,912,000
  alloc D23 apply work: 39,561,238,656
  free D23 apply work: 39,359,912,000
  free D23 matrix 4: 39,292,803,008
  free D23 matrix 3: 39,225,694,016
  free D23 matrix 2: 39,158,585,024
  free D23 matrix 1: 39,091,476,032
  alloc D24 matrix 1: 39,125,030,592
  alloc D24 matrix 2: 39,158,585,152
  alloc D24 matrix 3: 39,192,139,712
  alloc D24 matrix 4: 39,225,694,272
  alloc D24 node bump: 39,762,557,056
  free D24 node bump: 39,225,694,272
  alloc D24 apply work: 39,326,357,632
  free D24 apply work: 39,225,694,272
  free D24 matrix 4: 39,192,139,712
  free D24 matrix 3: 39,158,585,152
  free D24 matrix 2: 39,125,030,592
  free D24 matrix 1: 39,091,476,032
  alloc D25 matrix 1: 39,108,253,376
  alloc D25 matrix 2: 39,125,030,720
  alloc D25 matrix 3: 39,141,808,064
  alloc D25 matrix 4: 39,158,585,408
  alloc D25 node bump: 39,427,012,736
  free D25 node bump: 39,158,585,408
  alloc D25 apply work: 39,208,917,120
  free D25 apply work: 39,158,585,408
  free D25 matrix 4: 39,141,808,064
  free D25 matrix 3: 39,125,030,720
  free D25 matrix 2: 39,108,253,376
  free D25 matrix 1: 39,091,476,032
  alloc D26 matrix 1: 39,099,864,768
  alloc D26 matrix 2: 39,108,253,504
  alloc D26 matrix 3: 39,116,642,240
  alloc D26 matrix 4: 39,125,030,976
  alloc D26 node bump: 39,259,240,576
  free D26 node bump: 39,125,030,976
  alloc D26 apply work: 39,150,196,864
  free D26 apply work: 39,125,030,976
  free D26 matrix 4: 39,116,642,240
  free D26 matrix 3: 39,108,253,504
  free D26 matrix 2: 39,099,864,768
  free D26 matrix 1: 39,091,476,032
  alloc D27 matrix 1: 39,095,670,464
  alloc D27 matrix 2: 39,099,864,896
  alloc D27 matrix 3: 39,104,059,328
  alloc D27 matrix 4: 39,108,253,760
  alloc D27 node bump: 39,175,354,496
  free D27 node bump: 39,108,253,760
  alloc D27 apply work: 39,120,836,736
  free D27 apply work: 39,108,253,760
  free D27 matrix 4: 39,104,059,328
  free D27 matrix 3: 39,099,864,896
  free D27 matrix 2: 39,095,670,464
  free D27 matrix 1: 39,091,476,032
  alloc D28 matrix 1: 39,093,573,312
  alloc D28 matrix 2: 39,095,670,592
  alloc D28 matrix 3: 39,097,767,872
  alloc D28 matrix 4: 39,099,865,152
  alloc D28 node bump: 39,133,411,456
  free D28 node bump: 39,099,865,152
  alloc D28 apply work: 39,108,253,824
  free D28 apply work: 39,099,865,152
  free D28 matrix 4: 39,097,767,872
  free D28 matrix 3: 39,095,670,592
  free D28 matrix 2: 39,093,573,312
  free D28 matrix 1: 39,091,476,032
  alloc D29 matrix 1: 39,093,573,312
  alloc D29 matrix 2: 39,095,670,592
  alloc D29 matrix 3: 39,097,767,872
  alloc D29 matrix 4: 39,099,865,152
  alloc D29 node bump: 39,133,411,456
  free D29 node bump: 39,099,865,152
  alloc D29 apply work: 39,106,156,672
  free D29 apply work: 39,099,865,152
  free D29 matrix 4: 39,097,767,872
  free D29 matrix 3: 39,095,670,592
  free D29 matrix 2: 39,093,573,312
  free D29 matrix 1: 39,091,476,032
  alloc D30 matrix 1: 39,092,524,736
  alloc D30 matrix 2: 39,093,573,440
  alloc D30 matrix 3: 39,094,622,144
  alloc D30 matrix 4: 39,095,670,848
  alloc D30 node bump: 39,112,439,936
  free D30 node bump: 39,095,670,848
  alloc D30 apply work: 39,098,816,640
  free D30 apply work: 39,095,670,848
  free D30 matrix 4: 39,094,622,144
  free D30 matrix 3: 39,093,573,440
  free D30 matrix 2: 39,092,524,736
  free D30 matrix 1: 39,091,476,032
  alloc D31 matrix 1: 39,092,000,448
  alloc D31 matrix 2: 39,092,524,864
  alloc D31 matrix 3: 39,093,049,280
  alloc D31 matrix 4: 39,093,573,696
  alloc D31 node bump: 39,101,954,176
  free D31 node bump: 39,093,573,696
  alloc D31 apply work: 39,095,146,624
  free D31 apply work: 39,093,573,696
  free D31 matrix 4: 39,093,049,280
  free D31 matrix 3: 39,092,524,864
  free D31 matrix 2: 39,092,000,448
  free D31 matrix 1: 39,091,476,032
  alloc D32 matrix 1: 39,091,738,304
  alloc D32 matrix 2: 39,092,000,576
  alloc D32 matrix 3: 39,092,262,848
  alloc D32 matrix 4: 39,092,525,120
  alloc D32 node bump: 39,096,711,296
  free D32 node bump: 39,092,525,120
  alloc D32 apply work: 39,093,573,760
  free D32 apply work: 39,092,525,120
  free D32 matrix 4: 39,092,262,848
  free D32 matrix 3: 39,092,000,576
  free D32 matrix 2: 39,091,738,304
  free D32 matrix 1: 39,091,476,032
  alloc D33 matrix 1: 39,091,738,304
  alloc D33 matrix 2: 39,092,000,576
  alloc D33 matrix 3: 39,092,262,848
  alloc D33 matrix 4: 39,092,525,120
  alloc D33 node bump: 39,096,711,296
  free D33 node bump: 39,092,525,120
  alloc D33 apply work: 39,093,311,616
  free D33 apply work: 39,092,525,120
  free D33 matrix 4: 39,092,262,848
  free D33 matrix 3: 39,092,000,576
  free D33 matrix 2: 39,091,738,304
  free D33 matrix 1: 39,091,476,032
  alloc D34 matrix 1: 39,091,607,232
  alloc D34 matrix 2: 39,091,738,432
  alloc D34 matrix 3: 39,091,869,632
  alloc D34 matrix 4: 39,092,000,832
  alloc D34 node bump: 39,094,089,856
  free D34 node bump: 39,092,000,832
  alloc D34 apply work: 39,092,525,184
  free D34 apply work: 39,092,000,832
  free D34 matrix 4: 39,091,869,632
  free D34 matrix 3: 39,091,738,432
  free D34 matrix 2: 39,091,607,232
  free D34 matrix 1: 39,091,476,032
  alloc D35 matrix 1: 39,091,607,232
  alloc D35 matrix 2: 39,091,738,432
  alloc D35 matrix 3: 39,091,869,632
  alloc D35 matrix 4: 39,092,000,832
  alloc D35 node bump: 39,094,089,856
  free D35 node bump: 39,092,000,832
  alloc D35 apply work: 39,092,394,112
  free D35 apply work: 39,092,000,832
  free D35 matrix 4: 39,091,869,632
  free D35 matrix 3: 39,091,738,432
  free D35 matrix 2: 39,091,607,232
  free D35 matrix 1: 39,091,476,032
  alloc D36 matrix 1: 39,091,541,696
  alloc D36 matrix 2: 39,091,607,360
  alloc D36 matrix 3: 39,091,673,024
  alloc D36 matrix 4: 39,091,738,688
  alloc D36 node bump: 39,092,779,136
  free D36 node bump: 39,091,738,688
  alloc D36 apply work: 39,092,000,896
  free D36 apply work: 39,091,738,688
  free D36 matrix 4: 39,091,673,024
  free D36 matrix 3: 39,091,607,360
  free D36 matrix 2: 39,091,541,696
  free D36 matrix 1: 39,091,476,032
  alloc D37 matrix 1: 39,091,541,696
  alloc D37 matrix 2: 39,091,607,360
  alloc D37 matrix 3: 39,091,673,024
  alloc D37 matrix 4: 39,091,738,688
  alloc D37 node bump: 39,092,779,136
  free D37 node bump: 39,091,738,688
  alloc D37 apply work: 39,091,935,360
  free D37 apply work: 39,091,738,688
  free D37 matrix 4: 39,091,673,024
  free D37 matrix 3: 39,091,607,360
  free D37 matrix 2: 39,091,541,696
  free D37 matrix 1: 39,091,476,032
  alloc D38 matrix 1: 39,091,508,928
  alloc D38 matrix 2: 39,091,541,824
  alloc D38 matrix 3: 39,091,574,720
  alloc D38 matrix 4: 39,091,607,616
  alloc D38 node bump: 39,092,123,776
  free D38 node bump: 39,091,607,616
  alloc D38 apply work: 39,091,705,984
  free D38 apply work: 39,091,607,616
  free D38 matrix 4: 39,091,574,720
  free D38 matrix 3: 39,091,541,824
  free D38 matrix 2: 39,091,508,928
  free D38 matrix 1: 39,091,476,032
  alloc D39 matrix 1: 39,091,492,544
  alloc D39 matrix 2: 39,091,509,056
  alloc D39 matrix 3: 39,091,525,568
  alloc D39 matrix 4: 39,091,542,080
  alloc D39 node bump: 39,091,796,096
  free D39 node bump: 39,091,542,080
  alloc D39 apply work: 39,091,591,296
  free D39 apply work: 39,091,542,080
  free D39 matrix 4: 39,091,525,568
  free D39 matrix 3: 39,091,509,056
  free D39 matrix 2: 39,091,492,544
  free D39 matrix 1: 39,091,476,032
  alloc D40 matrix 1: 39,091,484,352
  alloc D40 matrix 2: 39,091,492,672
  alloc D40 matrix 3: 39,091,500,992
  alloc D40 matrix 4: 39,091,509,312
  alloc D40 node bump: 39,091,632,256
  free D40 node bump: 39,091,509,312
  alloc D40 apply work: 39,091,542,144
  free D40 apply work: 39,091,509,312
  free D40 matrix 4: 39,091,500,992
  free D40 matrix 3: 39,091,492,672
  free D40 matrix 2: 39,091,484,352
  free D40 matrix 1: 39,091,476,032
  alloc D41 matrix 1: 39,091,484,352
  alloc D41 matrix 2: 39,091,492,672
  alloc D41 matrix 3: 39,091,500,992
  alloc D41 matrix 4: 39,091,509,312
  alloc D41 node bump: 39,091,632,256
  free D41 node bump: 39,091,509,312
  alloc D41 apply work: 39,091,533,952
  free D41 apply work: 39,091,509,312
  free D41 matrix 4: 39,091,500,992
  free D41 matrix 3: 39,091,492,672
  free D41 matrix 2: 39,091,484,352
  free D41 matrix 1: 39,091,476,032
  alloc D42 matrix 1: 39,091,480,256
  alloc D42 matrix 2: 39,091,484,480
  alloc D42 matrix 3: 39,091,488,704
  alloc D42 matrix 4: 39,091,492,928
  alloc D42 node bump: 39,091,550,336
  free D42 node bump: 39,091,492,928
  alloc D42 apply work: 39,091,509,376
  free D42 apply work: 39,091,492,928
  free D42 matrix 4: 39,091,488,704
  free D42 matrix 3: 39,091,484,480
  free D42 matrix 2: 39,091,480,256
  free D42 matrix 1: 39,091,476,032
  alloc D43 matrix 1: 39,091,480,256
  alloc D43 matrix 2: 39,091,484,480
  alloc D43 matrix 3: 39,091,488,704
  alloc D43 matrix 4: 39,091,492,928
  alloc D43 node bump: 39,091,550,336
  free D43 node bump: 39,091,492,928
  alloc D43 apply work: 39,091,505,280
  free D43 apply work: 39,091,492,928
  free D43 matrix 4: 39,091,488,704
  free D43 matrix 3: 39,091,484,480
  free D43 matrix 2: 39,091,480,256
  free D43 matrix 1: 39,091,476,032
  free C table: 39,090,913,408
  free C W1/R: 19,545,456,704
  free B g result: 0
memory = 78,353,465,376
```

The embedded script generates every value above from current formulas and evaluates the 11 distinct caps from 18 through 28 at the evidence-backed depth 27.

Code/static is the sum in section 7: seven-width block bodies `2*10*16*2,836=907,520`; eight-position column bodies `4*8*(11+20+52+128+304+704+1,600)=90,208`; padded driver banks `4*16*(4,096+2,048+1,024+512)=491,520`; field/Montgomery and word/random/exponent banks `4*(32*4,096+32*1,024)=655,360`; reference/line/verification `4*16*32,768=2,097,152`; allocator `4*16*4,096=262,144`; polynomial control `4*48*4,096=786,432`; and static data `212*32+8,192+32=15,008`. Total `5,305,344`. The derived live stack is 36,864 bytes and its power-of-two allocation is 65,536.
