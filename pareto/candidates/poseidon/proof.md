# Orchard Poseidon r4: full union-machine ledger

## 1. Claim

The selected target is `poseidon-orchard-r4-prefix-v1`: P128Pow5T3 over Pallas with partial rounds 4 through 7 and the fixed eight full rounds. The attack class is ordinary collision search. One centre is sampled and the construction uses the published line, odd part, 20-step Graeffe prefix, exact value-domain Montgomery powering and inversion-free half-gcd.

The complete integer ledger gives `N_max = 360,246,182,268`. At 300 primitive operations per target compression, `time_log2 = 30.16138`. The event-by-event allocator walk and fixed regions give 630,494,304 bytes, `memory_log2_bytes = 29.23191`. The normalized score is `39.39329`. It improves our current `39.41712` point by `0.02383` and the frontier `39.42571` bar by `0.03242`.

H-ONE, H-NORMAL, the success proof and the experiments are unchanged. The success lower bound is `0.39009`. The resource ledger adds no heuristic. Every score-critical resource number is computed inside this package; no prior row total or memory peak is an input.

Jbenisek `56272e37` and `27fbfbe7` are credited for running-twiddle block-form products, Jbenisek `c7ef0551` for the 387-register seven-layer machine and offset-zero variants, and cryptogakusei `1533f8f0` for the charged wide-register precedent. Their text supplies constructions, not score-critical integers.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`. `(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`. The algorithm uses the line `j = 0`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant `M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS, nonzero on the deployed constants, checked). Let `(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, `d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i` (the supports are disjoint). After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7 (partial), 60, 61, 62, 63 (full) put ten S-box layers on top of an affine map, and the digest is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^10 = D = 9,765,625`. The leading coefficient is obtained by propagating leading coefficients through the ten layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used: `f_D(0) = 0x0eae601a80e5d207e772f8ff7333c0b8f442a251f419e3ee3506ef0b5e3612a9` (computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau` against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`), hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 4,882,812`, `g_c` has degree exactly `m` and leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`, `W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The useful roots are the roots in `F_p` with `S^((p-1)/2) = 1`: they are the roots of `gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p`; `S = 0` is not a root of `S^((p-1)/2) - 1`). This gcd divides the squarefree `S^((p-1)/2) - 1`, so it is a product of `k(c)` distinct linear factors over `F_p` (9.1); stage D computes instead the gcd of 4.3G, whose roots are their `2^20`-th powers.

Construction of `g_c` by evaluation. `H = 6,291,456 = 3 * 2^21` divides `p - 1` (`p - 1 = 2^32 * 3 * q`) and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`; one inverse transform of size `H` returns the coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). Each of the `2H = 12,582,912` evaluations of `F` is charged at the operations it executes (the line evaluation `tail_eval`): the affine start `alpha + beta W` (3 multiplications, 3 additions: 6), round 2 (three S-boxes `x^5` of 3 operations each and the MDS, 9 multiplications and 6 additions: 24; its constants are in `alpha`), round 3 (3 constant additions, 9, 15: 27), the four partial rounds (3 + 3 + 15 = 21 each), rounds 60-62 (27 each) and round 63 (3 + 9 and row 0 of the MDS, 3 multiplications and 2 additions: 17), `155 + 21 r = 239` operations at `r = 4`; rounds 0 and 1 are not executed (section 2). The loop work (two point additions, one subtraction, one multiplication by `1/(2 zeta^i)`, the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, the store with its address, the loop control and the bit-reversed index) is charged on top (stage B, section 6), with the twiddle table of the transform, built by stage B (4.2).

## 4. The algorithm (one centre, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   constants (once; no twiddle table: each stage builds the table of its own transforms, 4.2)
setup:  the line (line_setup) (once)
for t = 1, ..., K (K = 1):            [the test t <= K is made at the start of the trial; no exit except success]
  A  c := (w1 * 2^256 + w2) mod p from two fresh random words w1, w2 (4.1.1)
  B  g := monic g_c, by section 3 (12,582,912 evaluations + one inverse NTT of size 6,291,456 + the nonzero-leading-coefficient test + normalisation)
  C  g := g^(20): 20 Graeffe steps on O1 (section 4.3G); R := S^((p-1)/2^21) mod g, in the value domain on the truncated point sets O1, O2 of n' = 4,915,200 points (section 4.3T): 214 squaring steps, 45 of them also multiplying by S
  D  G := gcd(g, R - 1) (monic): the inversion-free half-gcd (section 4.4), charged for the normal remainder sequence with the quotient and return tests; on any other case ABORT (6.3)
  E  if deg G = 0 or deg G > DMAX: trial ends. Otherwise isolate a root y of G (4.1.2); if none within Z = 64 rounds: trial ends.
  F  u := a 2^21-th root of y (21 Tonelli-Shanks square roots, 2-adicity 32); for j = 0, ..., 2^20 - 1: s := u mu^j, W1 = c + s, W2 = c - s, until F(W1) = F(W2) (4.1.3); tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes, charged in row G, are equal and the pairs differ -> output; otherwise the trial ends
```

4.1.1 Coins (ruling `04c0dd43`, finding F-EVAL-001). The only randomness is the cost-model random-word primitive. Every random field element of the algorithm (the centre `c` of stage A and each shift of stage E) is drawn from two fresh 256-bit words `w1, w2`: each is reduced mod `p` by three conditional subtractions (exact, `2^256 < 4p`), and `x = (w1 mod p) * (2^256 mod p) + (w2 mod p)` in `F_p`, i.e. `x = (w1 2^256 + w2) mod p` with `w1 2^256 + w2` uniform on `[0, 2^512)`. There is no rejection and no retry. A draw is 63 operations: per word 1 random-word operation, 1 load, 1 store, 3 control, the reduction 9 and its loop control 11 (26 per word, 52), two Montgomery conversions 2, the load of the constant `2^256 mod p` 1, one multiplication 1, one addition 1, entry 2, the two addresses 4. At most `1 + Z = 65` draws (`130` words) per run. With `2^512 = Q p + r`, each residue has `Q` or `Q + 1` preimages, so one draw is within statistical distance `r (p - r) / (p 2^512) <= p / 2^512 = 2^-258.0` of uniform on `F_p`; the 65 draws are independent, so the joint distribution of all the coins of a run is within `eps_coin = 65 p / 2^512 <= 1.404e-76` of the distribution with every draw exactly uniform (total variation is subadditive over independent components).

4.1.2 Stage E: isolating a root of `G`. With `1 <= deg G <= DMAX = 16`, a Cantor-Zassenhaus split with random shifts isolates one linear factor in at most `Z = 64` rounds at degree `<= 16`; `eps_iso <= 2.371e-15` bounds the probability that 64 rounds fail to isolate a root when `deg G >= 1` (section 9.4).

4.1.3 Stage F: the root of `g_c` above `y`. By 4.3G, `y = S^(2^20)` for a usable root `S` of `g_c`, and the solutions of `S'^(2^20) = y` are `u^2 mu^(2j)`, `j < 2^20`, where `u^(2^21) = y` and `mu` is a fixed primitive `2^21`-th root of unity (`2^21 | p - 1`; a constant of the offline derivation, 6.2). `u` comes from 21 successive Tonelli-Shanks square roots: `y` is a `2^21`-th power, and if `x` is a `2^k`-th power with `1 <= k <= 21`, both square roots of `x` are `2^(k-1)`-th powers (`-1` is a `2^(k-1)`-th power, `2^k | p - 1`). The scan takes `s = u mu^j` for `j = 0, 1, ..., 2^20 - 1` and stops at the first `j` with `F(c + s) = F(c - s)` (two line evaluations of section 3). For `S' = s^2` a root of `g_c` this holds, because `F(c + s) - F(c - s) = 2 s g_c(s^2)`, so the scan stops at the latest at the `j` of `S`; any stop has `s != 0` (`y != 0`) and `F(c + s) = F(c - s)`, a collision by 2.4. Charge per candidate: `s <- s mu` 1, `c + s` and `c - s` 2, two line evaluations `2 * 239`, their calls 4, the comparison and branch 2, the loop control 3: `490`; at most `2^20` candidates, `513,802,240`, and the loop exit 2. The 21 square roots are charged `47,012` each (the whole row F of the algorithm without the prefix, a square root and the back-map), `987,252`, and the back-map `47,012`: row F = `514,836,506`.

### 4.2 Machine model and charges (`C(4) = 300`)

Every field operation, load, store, control operation and random word costs one primitive operation. One target compression costs `C(r) = 216 + 21r = 300` primitive operations. The implementation is one thread and has no dispatch.

The register file has 387 256-bit words: 256 field registers and 131 integer address registers. A radix-128 block holds 128 data words, 127 twiddles and one temporary. Its call holds at most 128 row bases, one twiddle address, one position offset and one loop bound. All `387 * 32 = 12,384` bytes are in section 7. The construction is credited to Jbenisek `c7ef0551`; cryptogakusei `1533f8f0` is the published wide-register and fixed-width-instruction precedent.

Loads and stores in transform blocks use base-plus-index addressing and cost one operation each. A position loop with eight positions in its straight-line body costs

    F(cnt) = 1 + 3 floor(cnt/8) + 2 + 3 (cnt mod 8) + 2.

The five terms are the initial bound, three controls per full body, the main-loop exit, three controls per remaining position and the remainder-loop exit. A column kernel of `k` layers has `2^k` rows. Before the offset-zero specialization, its charge is `c0(k) + c1(k) cnt + F(cnt)`, where for `k = 1,...,7`

    c0 = (5, 6, 10, 18, 34, 139, 269)
    c1 = (11, 20, 52, 128, 304, 704, 1600).

For six layers, `139 = 2*63 + 3 + 2*(6-1)` and `704 = 2*64 + 3*6*32`. For seven, `269 = 2*127 + 3 + 2*(7-1)` and `1600 = 2*128 + 3*7*64`. The wrapper is `2*2^k + 6`, and the call loop is five operations including exit. At offset zero, `2^k-1` butterflies per position have twiddle one: their multiplication is absent, while three controls select the straight-line variant.

Every product pass in stages C and D uses Jbenisek's running-twiddle construction of `56272e37` and `27fbfbe7`. Neither stage has a product twiddle table. On a `2^a`-point row, a width-`k` pass beginning at level `l0` has `2^(a-k)` blocks and `2^(a-l0-k)` running positions. A block costs

    B(k) = 2*2^k + 3k*2^(k-1) + 3.

The terms are `2^k` loads, `2^k` stores, `k*2^(k-1)` three-operation butterflies, two base updates and one share of the four-block loop. A running chain costs `2^k+4`: one root advance, `k-1` squarings, `2^k-1-k` constant multiplications and five controls. The constants and pass wrapper cost `159k+19` forward or `159k+20` inverse. Group zero removes `2^k-1` multiplications in each of its blocks and pays three controls. Thus the executed forward pass is

    2^(a-k) B(k) + 2^(a-l0-k) (2^k+4)
      + 159k + 19 - 2^(a-l0-k)(2^k-1) + 3,

with 20 in place of 19 for an inverse. The first pass takes the remainder modulo seven layers and every later pass takes seven layers.

The half-gcd recurrence deliberately charges a larger finite pass: every block, rather than every running position, pays `2^k+4`. Its forward charge is

    2^(a-k) (B(k)+2^k+4) + 159k + 19
      - 2^(a-l0-k)(2^k-1) + 3,

again with 20 for inverse. After the recursive and array rows, each non-leaf node adds exactly 184 operations: 20 entry/exit, 16 split/degree tests, 24 child frames, 8 return tests, 20 arena mark/release, 18 transform dispatch, 48 matrix-pointer setup, 18 row/sign selection and 12 normal-sequence tests. These are the control and lower-order operations that the earlier percentage represented. There is no cost premise, fitted factor or percentage margin.

The 23 truncated layers use `3 | 7,4,4 | 5`. Four adjacent middle blocks share a running group chain; the ledger asserts exact divisibility. Newton, quotient and every outer apply are recomputed from the same transform primitives. A direct outer apply is limited to 24 rows of `2^16` coefficients; larger outputs use the truncated path. The matrix-row group count is derived from the live budget.

The arena allocator has a 64-byte header and a payload rounded to 64 bytes. Large blocks use a two-ended first-fit pool. Appendix E.3 lists every allocation and free, its side, both extents and live bytes. Stage B alone retains a transform twiddle table. The root tables of the truncated transform remain. Stages C and D form product twiddles in registers.

### 4.3G The Graeffe prefix

Definition. For `h` monic of even degree `m` write `h(X) = E(X^2) + X O(X^2)`; its Graeffe transform is `h~(Y) = E(Y)^2 - Y O(Y)^2`, so `h~(X^2) = h(X) h(-X)` and `h~` is monic of degree `m` with roots the squares of the roots of `h` (with multiplicity). Stage C first replaces `g = g_c` by `g^(20)`, 20 Graeffe steps, then computes `R = S^e mod g^(20)`, `e = (p-1)/2^21` (2-adicity 32), and stage D takes `G = gcd(g^(20), R - 1)`.

Lemma. `G` is the product of `(Y - y)` over the distinct values `y = S^(2^20)`, `S` a usable root of `g_c` (a nonzero square in `F_p` with `g_c(S) = 0`, section 3). Proof: `g^(20)(Y) = prod_i (Y - S_i^(2^20))` over the roots `S_i` of `g_c` in an algebraic closure; `Y^e - 1` is squarefree and its roots are the `2^21`-th powers of `F_p^*`. If `S_i^(2^20) = u^(2^21)` with `u` in `F_p^*`, then `S_i = u^2 zeta` with `zeta^(2^20) = 1`, so `zeta` is in `F_p` and `zeta = xi^2` with `xi^(2^21) = 1` (`2^21 | p - 1`), and `S_i = (u xi)^2` is a nonzero square of `F_p`; conversely `S = v^2` gives `S^(2^20) = v^(2^21)`. So `deg G` is the number of distinct `2^20`-th powers of the usable roots: `1 <= deg G <= k(c)` when `k(c) >= 1`, and `deg G = 0` when `k(c) = 0`; the event `E_c` of 9.2 gives `1 <= deg G <= DMAX`.

Execution (on the point set `O1` of 4.3T). One step: `E` (`m/2 + 1` coefficients) and `O` (`m/2`) are read from `g` at stride 2 by the top passes of two truncated forwards, which load only the input blocks below the length (3 or 2 of the 8 per offset, two offset ranges per batch; no zero-fill); the fused bottom pass forms `G = (E^2 - y O^2)/N` at each point `y` of `O1` between the forward and the inverse bottom layers (`y` is the last-layer twiddle of its butterfly, in a register: two squarings, two multiplications, one subtraction, 5 per point); its 32-point blocks of `E` and `O` do not fit the 64-word register file together, so the block of `E` is transformed and squared first and `E^2` is stored to its slot and loaded back (2 per point), and 5 twiddles are spilled as in the pointwise bottom pass of 4.3T (30 per block); one truncated inverse stores the new coefficients into the array of `g` (those above `m` come out zero). `E` and `O` on `O1` use the arrays of `A` on `O2` and of `A` on `O1` before stage C fills them, with a batch buffer of `8,192` words of their own; no array is added and the high-water mark of section 7 is unchanged. Appendix E.1 derives the Graeffe step directly from the live top, middle, bottom and recovery kernels. 20 steps precede the 214 fixed exponent steps; the exponent loses its 20 low zero bits.

Every map is exact; no premise is added to the time or the memory. The zero test of `k1` (4.3T) now concerns `g^(20)`: `g^(20)(y) = 0` for `y` in `O1` only if `g_c(x) = 0` for one of the `2^20` values `x` with `x^(2^20) = y` (in `F_p` or an extension); for each such `x`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g^(20) vanishes on O1) <= 2^20 n' (D - 1) / p = eps_g < 2^-188`.

### 4.3T Stage C in the value domain on truncated point sets (the method of bradcush `b30de9bf`/`a41aecdd`, 75 of 128 nodes)

Point sets. `N = 2^23` divides `p - 1` (2-adicity 32). Let `psi` have order `2^24`, `H_N = <psi^2>` and `Y = X^(2^16)`. `H_N` is the union of the 128 depth-7 nodes `{x : x^(2^16) = r_j}`, `r_j` the 128-th roots of unity in transform (bit-reversed) order; `O1` is the union of the first 75 nodes, `n' = 75 * 2^16 = 4,915,200 >= m + 1 = 4,882,813` points, and `O2` the same 75 nodes of the coset `psi H_N` (`x^(2^16) = r'_j`, `r'_j^128 = -1`), disjoint from `O1`. `P1 = prod_{j<75} (Y - r_j)` has degree `n'`, vanishes on `O1` and is the nonzero constant `P1(r'_j)` on node `j` of `O2`; `delta_j = 1/P1(r'_j)` (75 table constants).

Truncated transforms (bradcush `b30de9bf` 4.3, generalized from van der Hoeven's truncated Fourier transform). A polynomial of degree below `n'` is represented on the first 75 depth-7 nodes. The forward top covers all `N/2^3` offsets. The middle acts only on live nodes, in passes of 7, 4, 4 layers; the widest radix fits exactly in the declared register file. The bottom acts on `2^5`-point blocks. The inverse reverses these passes and recovers the maximal dropped subtrees `(1,7), (4,5), (16,3), (32,2)`. One recovery charges `size * 2^16 * (8*depth+2)` for every pair and its configured closing stores.

The top, middle and recovery layers are class-batched in the 8,192-word buffer. Each middle width has exactly `n'/2^k` blocks; four adjacent blocks share one chain. The script charges every block body, every group chain and every fixed wrapper. The top position loops use `F(N/2^3)`. Fused top passes enumerate loads, stores, both butterfly directions, active coset products and the offset-zero saving. Bottom kernels enumerate their loads, butterflies, point operations, pointer updates and four-block control. The exact maps and dropped-subtree recovery are unchanged; only the machine realization is repriced.

Montgomery powering (`b30de9bf` 4.5). For residues of degree `< n'`, `Mont(A, B) = (A B + u g)/P1` with `u = -A B / g mod P1` (`deg u < n'`); the division by `P1` is exact, `Mont(A, B) = A B / P1 mod g`, and `deg Mont(A, A) <= n' - 2`, so `X Mont(A, A)` has degree `< n'`. A residue `A` (representing `S^e P1`) is held by its values on `O1` and on `O2`, each up to a tracked scalar. One step: `U = A^2 k1` on `O1` (`k1 = -1/(N^3 g)` there; `u` is determined by its values on `O1`); `U` to `O2` (truncated inverse on `O1`, truncated forward on `O2`); `B2 = (A2^2 + U g) delta_j` on node `j` of `O2`, which is `Mont(A, A)` up to the tracked scalar because `P1 = 1/delta_j` there, times the point `x` when the exponent bit is 1; `B2` to `O1` (truncated inverse on `O2`, truncated forward on `O1`). No `1/N` is executed inside the steps (the scalars are tracked, 2 operations per step). Per point and step: on `O1` `sqr, LD k1, mul` (4); on `O2` `LD A2, sqr, LD g, mul, add`, the multiplication by `delta_j`, `ST` (10) and the load of `delta_j` per block (2); 3 more for a 1-bit (the load of the point and a multiplication).

Entry and exit. `g` (coefficients after the Graeffe prefix of 4.3G, its slots above `m` zero) goes to `O1` and `O2` (a truncated forward each; every scaling of this section, `1/N` and the coset twist, is a running product fused into the adjacent pass, 2 operations per point). The start residue is `A0 = X^v P1 mod g`, `v = 2^19 = 524,288` (VSHIFT = 3): `q = floor(X^v P1 / g)` has `ell = v + n' - m + 1 = 556,677` coefficients and is formed from the Newton reciprocal of the reversed `g` and one product (transforms of up to `3*2^19` points, with running twiddle factors and no stage product table); on node `j` of `O2`, `x^v P1(x) = r'_j^8 P1(r'_j)` is a constant, so `A0 = x^v P1 - q g` there is one truncated forward of `q` and one pointwise pass (8 per point); then `A0` goes to `O1`. `k1` is formed by chunked batch inversion on `O1` (chunks of `2^13` points: prefix products, one inversion, two multiplications per point; the `2^13` prefixes are kept in the batch buffer, which no transform uses at that time); each chunk product is tested for zero before its inversion (2 per chunk), and a zero ends the trial: for fixed `x != 0`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g vanishes on O1) <= eps_g < 2^-188` for the transformed `g` (4.3G, 9.2). The exit is one step with multiplier 1 (`Mont(A, 1)`) and two truncated inverses with their scaling, which return `kappa R` (`kappa` the tracked scalar) and `g` in coefficient form; the gcd is scale-invariant, so stage D receives `kappa R - kappa`. There are `214` squaring steps (the exponent `(p-1)/2^21`, 4.3G), `45` of them also multiplying by `S`.

Exactness and memory. Every map above is exact (Montgomery products of polynomials of degree `< n'`, held bijectively by their values on 75 nodes); no premise is added to stage C. The live set of the stage is four arrays of `n'` words (`g` on `O2`, `A` on `O2`, `A` on `O1`, `k1` on `O1`), the tables (`105 + 16,384` words: 30 constants, the 75 `delta_j`, the two-level root tables), one batch buffer of `8,192` words (the `106 * 64 = 6,784` positions above `n'` of one batch of classes, or the `2^13` prefixes of one batch-inversion chunk; one transform runs at a time, so the schedule needs no other storage) and, while `q` is formed, the Newton arrays. Appendix E.1 expands every event and gives **row C = 271,235,518,025**.

### 4.4 Stage D: the inversion-free half-gcd (the method of bradcush `b30de9bf`/`4bcabff8`)

`G = gcd(g, R - 1)` is computed by a recursive half-gcd on the normal remainder sequence that keeps every matrix in coefficient form and never inverts a leading coefficient (pseudo-division). A node `hgcd(a, b, k)` of budget `k = 2^j - 1` runs its first child (budget `2^(j-1) - 1`) on the top window, applies the child's matrix `M1`, `(c, d) = adj(M1)(a, b)`, makes one pseudo-division with a quotient of degree 1 (its remainder `e` only on the `2^j - 1` positions the second child reads), runs the second child (`M2`) and forms `M = M1 [[Q, 1], [b^2, 0]] M2`. The apply of a node is formed on the three rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), one transform of `n` points per row in the block form of `27fbfbe7` 4.2 (the twist of the rows `Y + 1`, `Y - i` as a running product fused into the pass; E.2.1), and recombined by a 3-row CRT (22 operations per position); the product `M` on the two rows `Y - 1`, `Y + 1` only, recombined by the 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` (10 operations per position, the `1/2` folded into the `1/n` of the inverse). The product needs no third row: on the normal sequence every quotient has degree 1 and `b^2` is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; the values of each child's matrix on the row `Y - 1` are reused by its parent, the values of `M1` from the apply are reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). The base case is budget `2^6 - 1`, two remainder steps per pass.

The driver: while the degree `n` of `g` admits it, `k = 2^j - 1` is the largest with `2k + 1 <= n` and `k <= KMAX = 2^19 - 1` (the outer-step cap of weijiekoh `a78f526e`), `hgcd(k)` runs on the top window and its matrix is applied to `(g, R)` in place (`plan_apply`: the cheapest of the truncated transform of 4.3T on `n'` points, a `2^a`-point or a `3*2^a`-point transform; the entries of `M` row by row of `2^16` points when the transform has at least `2^17` points; `1/N` fused into the pointwise loop, 1 operation per point); from degree 148 down the schoolbook pseudo-division Euclid, then the normalisation of `G`. Every node works in one bump arena (allocation and release 10 operations each), `node_mem(j)` words at its peak (`8,388,352` at `j = 19`). On the normal sequence every length, parameter and allocation is a function of `m` alone: 24 outer steps (six on the truncated transform of `n'` points, then `3*2^19`- down to `3*2^6`-point plans) and the Euclid from degree 148.

Appendix E.2 gives **row D = 83,530,418,490**.

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G = gcd(g, R - 1)`, whose roots are the values `y = S^(2^20)` of the usable roots `S` of `g_c` (4.3G); stage F stops only at an `s != 0` with `F(c + s) = F(c - s)` (4.1.3), so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Complete operation ledger

| row | event family | operations |
| --- | --- | ---: |
| init | runtime constants and bookkeeping | 18,009 |
| setup | line setup | 4,906 |
| A | coin draw, reduction and allocation | 1,228 |
| B | line evaluations, loop, table transform and normalization | 4,830,665,547 |
| C | Graeffe prefix and exact value-domain powering | 271,235,518,025 |
| D | inversion-free half-gcd normal walk with ABORT | 83,530,418,490 |
| E | 64 isolation rounds at degree at most 16 | 129,547,526 |
| F | 23 roots, full candidate scan and back-map | 514,836,506 |
| G | two reference verifications | 7,412 |
| trial loop | reset and closing control | 1,012 |
| plan misses | 17 deterministic plan constructions | 100,215 |
| output | two fixed output rows | 4,063,392 |
| offline | declared cap over the closed literal derivation | 1,000,000 |
| **N_max** | `T_fixed + T_trial + T_off` | **360,246,182,268** |

`T_fixed = 4,186,522`, `T_trial = 360,240,995,746` and `T_off = 1,000,000`. Their sum is `N_max = 360,246,182,268`. The exact raw time is `log2(N_max/300) = 30.1613734946930015051130690004497047999427829577857177744631345311717772511003488235369269`; upward rounding at five decimals gives `30.16138`.

All searches remain in the row that executes them. Stage E contains 64 complete isolation rounds. Stage F contains every one of the `2^22` candidates. The offline constants take 136,785 operations by the closed literal formula and are charged at 1,000,000. The package contains no empirical timing conversion.

### 6.1 Exact-integer evidence

The exact-integer script embedded in Appendix X computes the geometry from `5^10`, constructs every transform and product plan, expands rows C and D, generates all 24 outer steps, walks all allocator events and derives both logarithms. Its assertions bind the dimensions, recurrence depth, event maximum and final sums. It has no prior row total, prior `N_max`, prior memory peak or score as an input.

### 6.2 Normal-sequence charge and ABORT

Row D charges the normal sequence. Every division tests quotient degree one, every recursive return tests that its budget was removed, and a zero remainder also ends the trial. At the first failed test the trial resets its allocator and stops. While tests pass, lengths, recursion budgets and allocation sizes depend only on `m`; therefore an abnormal trial executes a prefix of the charged operation and allocation walk. H-NORMAL affects success probability, not the resource upper bound.

## 7. Memory from the allocator walk

The allocator simulation begins empty. It executes 180 allocation/free events in program order. Each request includes the 64-byte header and 64-byte payload rounding. The two pool sides are first-fit lists in address order; free neighbours merge and a free terminal extent returns to the unused middle. The maximum sum of the low and high extents is 629,935,808 bytes, reached in stage C. A 128-byte middle gap, 0 bytes for configured small-block classes and 16,896 bytes for the later classes give an arena of 629,952,832 bytes.

| region or event peak | bytes |
| --- | ---: |
| stage A live peak | 157,286,464 |
| stage B live peak | 392,167,616 |
| stage C live peak | 629,935,808 |
| stage D live peak | 583,528,000 |
| two-ended pool high-water | 629,935,808 |
| middle gap | 128 |
| recursion slab classes | 0 |
| later slab classes and heads | 16,896 |
| **arena** | **629,952,832** |
| code and static data, derived by emitted family | 462,976 |
| 387-word register file | 12,384 |
| offline working set | 576 |
| stack | 65,536 |
| **footprint** | **630,494,304** |

At the end of stage D both pool extents are zero and no allocation remains live. The raw logarithm is `29.2319080961423663366685551520510685575870557418819747323054718801552100004761843923755032`; upward rounding at five decimals gives `29.23191`. No product twiddle table is allocated in C or D, and there is no stored advice.

## 8. Evaluation obligations

1. `target_defined`: sections 1 through 3 fix the Orchard P128Pow5T3 target, the five selected partial rounds, the input map and the full-field output.
2. `algorithm_defined`: sections 4 and 5 define the line, odd part, Graeffe prefix, exact value-domain powering, half-gcd, root isolation, lift, back-map and final verification.
3. `resources_defined`: sections 4.2, 6, 7 and Appendices E and X enumerate the RAM rules, every search, every operation family and every allocation/free event.
4. `probability_space_defined`: sections 4.1.1 and 9.2 define the fixed target and fresh independent random words.
5. `heuristics_disclosed`: claim.json and sections 9.1 and 9.5 disclose H-ONE and H-NORMAL, their roles, scopes, evidence and limitations. There is no resource heuristic.
6. `evidence_relevant`: section 10 and both manifests bind the unchanged experiments to the line construction, Graeffe pair, normality premise and collision checks.

## 9. The premise and the success bound

### 9.1 H-ONE
The number of centres `c` with `1 <= k(c) <= 16` is at least `q p = 0.3931 p`, `k(c)` the number of nonzero squares `S` with `g_c(S) = 0` (stage D returns `G` with `1 <= deg G <= k(c)` when `k(c) >= 1`, 4.3G). The premise states `q = 0.3931`, the law value `1 - e^(-1/2) = 0.3934693` (9.3) less the extrapolation allowance stated exactly as `0.0003693`; it is also `0.0001292` below the four-moment Bonferroni bound `151/384 = 0.3932292`. The split of the allowance between `H-ONE` and `H-NORMAL` follows cryptogakusei's entry `4888e783`: with `delta = 0.003` (9.5) the bound of 9.2 needs `P(E_c) >= 0.3931` at `K = 1`. The extrapolation, the monodromy theorem at N = 2, 3 and the toy-field and organizer-run evidence are in the claim.json heuristic `H-ONE` and sections 10.3, 10.5.1.

### 9.2 The success bound
The centre is a fresh draw. For a centre `c` let `E_c` be the event `1 <= k(c) <= DMAX` (H-ONE, `P(E_c) >= q = 0.3931`) and `N_c` the event that the remainder sequence of `(g, R_c - 1)` (`g = g_c^(20)`, 4.3G) is normal down to its gcd (H-NORMAL, 9.5, `P(not N_c) <= delta = 0.003`). The Graeffe prefix and the value-domain stage C reproduce `g^(20)` and `R = S^((p-1)/2^21) mod g^(20)` exactly (4.3G, 4.3T) and add no premise; stage C needs `g^(20)` nonzero on `O1`, which fails with probability at most `eps_g = 2^20 n' (D - 1) / p < 2^-188` over the centre (4.3G). If `E_c` and `N_c` hold and `g^(20)` has no zero on `O1`, stages C and D run to their end and return `G = gcd(g^(20), R_c - 1)` with `1 <= deg G <= DMAX` (4.3G); a successful isolation and the scan of 4.1.3 then end in a verified collision. For `c` uniform `P(E_c and N_c) >= q - delta`, so with one centre (the event `g^(20)` zero on `O1` subtracted as `eps_g`)

`success = 1 - (1 - q + delta)^K - K (eps_coin + eps_iso + eps_g) = q - delta - eps_coin - eps_iso - eps_g`, `K = 1`.

Transfer to the written sampler (F-EVAL-001): `q - delta - eps_iso - eps_g` bounds the success probability of the run whose draws are exactly uniform on `F_p` (the premises and the isolation lemma are stated for uniform draws). The success of a run is an event of the vector of its draws, and the actual draws of 4.1.1 are within total variation `eps_coin` of the uniform vector, so the actual success probability is at least the ideal one minus `eps_coin`.

With `q = 0.3931`, `delta = 0.003`, `eps_iso <= 2.371e-15`, `eps_coin <= 1.404e-76`, `eps_g < 2^-188`: `q - delta = 0.3901`, and the value is `0.390099999999997628 >= 0.39`. The bound stays at or above `0.39` for every `delta <= 0.0030999` at `q = 0.3931`. The probability is over the random words of 4.1.1 for the fixed target, not over targets and not a sampled frequency.

### 9.3 Monodromy (support for H-ONE)
The roots of `G(c,t) = g_c(t^2)` come in pairs `+-t_i`, so the monodromy lies in the hyperoctahedral group `B_m` and `k(c)` counts positive Frobenius fixed points; for `B_m` this is Poisson(1/2) in the limit, `P(k >= 1) = 1 - e^(-1/2) = 0.3934693`, and Bonferroni at order 4 gives `P >= 151/384 = 0.3932292`. A theorem at two and three layers (Aubry-Perret, monodromy `B_12`, `B_62`); false for permutation polynomials, for decomposable `F` with imprimitive monodromy, and at one layer.

### 9.4 Isolation lemma
With `1 <= deg G <= 16`, a random-shift split isolates a linear factor within `Z = 64` rounds except with probability `eps_iso <= 2.371e-15`. Finite derivation: `G` divides `Y^((p-1)/2^21) - 1` (4.3G), a divisor of `Y^(p-1) - 1`, so it is squarefree and splits into `d = deg G <= 16` distinct linear factors `X - t_i` over `F_p`. A round with shift `a` keeps a nontrivial part of the current factor `H` under `gcd(H, (X + a)^((p-1)/2) - 1)` (or `X + a` itself when `a = -t_i`), so two roots `t_i != t_j` stay together only if `chi(t_i + a) = chi(t_j + a)` or `a` is in `{-t_i, -t_j}`. Since `sum_a chi((a + t_i)(a + t_j)) = -1` for `t_i != t_j`, exactly `(p - 3)/2` shifts give equal nonzero characters, so for `a` uniform on `F_p` the pair stays together with probability at most `((p - 3)/2 + 2)/p = 1/2 + 1/(2p)`; each shift is a fresh random word reduced mod `p`, within statistical distance `2^-128` of uniform (4.1.1), so per round the bound is `1/2 + 2^-127`, independently across rounds. The parts are nested, so the factor kept after 64 rounds holds two roots only if one of the at most `C(16,2) = 120` pairs was never separated in 64 rounds. By the union bound `eps_iso <= 120 (1/2 + 2^-127)^64 < 6.6e-18 <= 2.371e-15`; the looser stated value `2.371e-15` is kept, so every other number is unchanged.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries `e6dcb600` and `1aa56884`; allowance split of cryptogakusei's `4888e783`; organizer-run tests in the form of gta6rp's `bef31fdd`)
**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(h_c, R_c - 1)`, where `h_c = g_c^(20)` is the 20-fold Graeffe transform (4.3G) of the monic odd part `g_c` of section 3 (monic, degree `m = 4,882,812`) and `R_c = S^((p-1)/2^21) mod h_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.003` (`2^-8.38`). Stage D is charged for the normal sequence; every division tests its quotient degree and every call of the half-gcd its return, and on any other case the trial ends (ABORT, sections 4.4, 6.3). The premise enters only the success probability (9.2): the time and memory bounds hold for every remainder sequence, because an abnormal trial ends at its first failed test after executing a prefix of the charged work (6.3). For a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes, each a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-208`; the premise extrapolates a much weaker form of this random-pair behaviour (`delta = 0.003`) to the structured pair `(h_c, R_c - 1)`. Measured support is organizer-run (10.5.1): the six experiments `euclid-normal-n2-t256-l2-g20-a` to `-f` compute the complete Euclidean sequence of `(h_c, R_c - 1)` for this construction (20 Graeffe steps, exponent `(p-1)/2^21`) on the truncation `F_2` (`m = 12`) for 256 organizer-seeded trials of two centres each (3,072 sequences in all) and return a witness pair exactly when both sequences of a trial are normal; `euclid-normal-n3-t24-g20` and `euclid-normal-n4-t2-g20` do the same at `m = 62, 312`. The prediction is that every computed sequence is normal. Zero abnormal in the 3,072 sequences is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (`delta = 0.003` is the declared premise). Not verified at `r = 4`, which would need the computation itself; the organizer-run tests are at `m = 12` to `312`, far below `m`.

## 10. Experiments

Program `experiments/exp_euclid.py` (euclid-normal, one-centre) and `experiments/exp_line.py` / `experiments/exp_lowbits.py` (line-ladder and lowbits-birthday), with `experiments/manifest.json`.

10.3 The truncations. `F_N(c + X)` is coordinate 0 after the first `N` S-box layers on the line `j = 0`; `F_2`, `F_3`, `F_4` have odd parts of degree `m = 12, 62, 312`. The arithmetic monodromy at `N = 2, 3` is `B_12`, `B_62` (Grok jobs 136, 137, re-run on the deployed constants).

10.5.1 Organizer-run set. euclid-normal-n2-t256-l2-g20-a to -f compute the complete Euclidean sequence of `(h_c, R_c - 1)` (the pair of 9.5: 20 Graeffe steps, exponent `(p-1)/2^21`) for this construction at depth `N = 2` (`m = 12`), each for 256 organizer-seeded trials of two centres (512 sequences per entry, 3,072 in all; the final letter only changes the organizer seeds); euclid-normal-n2-t256-g20, -n3-t24-g20 and -n4-t2-g20 compute one sequence per trial at `m = 12, 62, 312`. A trial returns a witness pair exactly when its sequences are normal; the prediction (H-NORMAL, 9.5) is that every trial returns a pair, so the abnormal count is zero, a reproducible observation consistent with the premise. We do not treat the organizer-seeded centres as independent unselected samples and draw no population bound from these runs: `delta = 0.003` is the declared premise (9.5), carried by its stated support, not by an interval computed from the experiments. one-centre-n2-t256 and one-centre-n3-t24 run one trial of the algorithm with the Graeffe prefix off (`s = 0`: the gcd against `S^((p-1)/2) - 1` and a square root in place of the scan; they test `H-ONE`, a statement about `g_c` that the prefix does not change, 4.3G) at depth `N = 2, 3` per organizer seed and return a witness pair exactly when the sequence is normal, `1 <= k(c) <= 16` and the isolated root gives a verified collision of `F_N`, with expected count about 0.393469 T under H-ONE (9.1), reported as an observation with no interval inferred. line-ladder-w6/-w8/-w10/-w12 and lowbits-birthday corroborate the antipodal structure (random-function model), not the score-critical basis. Our runs of the six -l2-g20 entries with local seeds (one CPU; 9.23 to 9.63 s each on our workstation): 3,072 sequences, all normal, 256 pairs per entry; the gcd had positive degree for 1,195 of the 3,072 centres (0.389). Our runs of -n2-t256-g20, -n3-t24-g20 and -n4-t2-g20: 256, 24 and 2 sequences, all normal. The organizer-checkable output is the returned witness-pair count; the premises H-ONE and H-NORMAL hold under trusted execution of the submitted program.

## Appendix E: expanded rows and allocator events

### E.1 Stage C

| event family | operations |
| --- | ---: |
| plans constants tables zero fill allocations | 501,914 |
| graeffe prefix and buffer | 15,586,961,510 |
| newton reciprocal | 855,782,152 |
| quotient product and copy | 217,799,844 |
| g to O1 and O2 | 514,070,237 |
| start residue on O2 | 321,626,982 |
| A0 extension to O1 | 599,092,946 |
| chunked batch inversion | 72,204,005 |
| powering steps | 251,689,036,148 |
| exit montgomery step | 694,325,606 |
| two truncated inverses | 684,115,681 |
| entry exit bookkeeping | 1,000 |
| **row C** | **271,235,518,025** |

The live middle widths are `(7, 4, 4)`. One middle set is 147,036,042; one recovery is 79,953,920; one fused top is 83,230,752; a forward and inverse are 257,034,448 and 342,057,170. A Graeffe step is 779,348,010. A bit-zero powering step is 1,172,983,982, and a bit-one step is 1,187,883,182. The exponent scan produces 169 bit-zero and 45 bit-one steps.

The Newton row is generated by these doubling steps; the costs include both products, truncation loops and fixed call events.

| step | precision | operations |
| ---: | ---: | ---: |
| 1 | 2 | 2,753 |
| 2 | 4 | 5,241 |
| 3 | 8 | 7,048 |
| 4 | 16 | 9,915 |
| 5 | 32 | 14,983 |
| 6 | 64 | 24,741 |
| 7 | 128 | 46,039 |
| 8 | 256 | 79,253 |
| 9 | 512 | 174,379 |
| 10 | 1,024 | 321,797 |
| 11 | 2,048 | 627,595 |
| 12 | 4,096 | 1,263,977 |
| 13 | 8,192 | 2,589,175 |
| 14 | 16,384 | 5,347,301 |
| 15 | 32,768 | 11,081,875 |
| 16 | 65,536 | 26,536,787 |
| 17 | 131,072 | 52,429,441 |
| 18 | 262,144 | 105,981,359 |
| 19 | 524,288 | 216,621,277 |
| 20 | 556,677 | 432,617,216 |
| **Newton reciprocal** | **556,677** | **855,782,152** |

The quotient product is planned from operand lengths `ell, ell` and output length `2 ell - 1`; no row total is supplied to the planner. Every product candidate is the sum of two forwards, one inverse, input copy/zero loops, its pointwise loop, output loop and fixed allocation/call events.

### E.2 Stage D

The half-gcd node has no percentage allowance. Its fixed 184 operations are the sum shown in section 4.2 and in `NODE_FIXED_EVENTS`. Every other term is a recursive child, a transform row, pointwise row, CRT, pseudo-division or array loop.

| j | children | top | returns | apply | matrix | inverse | CRT | pseudo | arrays | fixed | `node_bf(j)` |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7 | 210,280 | 25,237 | 35,296 | 6,876 | 9,168 | 32,322 | 3,336 | 2,064 | 3,588 | 184 | 328,351 |
| 8 | 656,702 | 46,671 | 31,208 | 13,692 | 18,256 | 53,232 | 6,664 | 4,112 | 7,172 | 184 | 837,893 |
| 9 | 1,675,786 | 99,895 | 71,112 | 27,324 | 36,432 | 126,138 | 13,320 | 8,208 | 14,340 | 184 | 2,072,739 |
| 10 | 4,145,478 | 192,069 | 131,888 | 54,588 | 72,784 | 229,092 | 26,632 | 16,400 | 28,676 | 184 | 4,897,791 |
| 11 | 9,795,582 | 380,071 | 258,312 | 109,116 | 145,488 | 445,962 | 53,256 | 32,784 | 57,348 | 184 | 11,278,103 |
| 12 | 22,556,206 | 764,337 | 522,176 | 218,172 | 290,896 | 904,488 | 106,504 | 65,552 | 114,692 | 184 | 25,543,207 |
| 13 | 51,086,414 | 1,550,347 | 1,073,208 | 436,284 | 581,712 | 1,873,974 | 213,000 | 131,088 | 229,380 | 184 | 57,175,591 |
| 14 | 114,351,182 | 3,158,277 | 2,223,152 | 872,508 | 1,163,344 | 3,920,676 | 425,992 | 262,160 | 458,756 | 184 | 126,836,231 |
| 15 | 253,672,462 | 6,446,911 | 4,620,072 | 1,744,956 | 2,326,608 | 8,232,402 | 851,976 | 524,304 | 917,508 | 184 | 279,337,383 |
| 16 | 558,674,766 | 14,454,141 | 11,320,528 | 3,489,852 | 4,653,136 | 21,145,758 | 1,703,944 | 1,048,592 | 1,835,012 | 184 | 618,325,913 |
| 17 | 1,236,651,826 | 28,796,215 | 22,491,592 | 6,979,644 | 9,306,192 | 41,955,276 | 3,407,880 | 2,097,168 | 3,670,020 | 184 | 1,355,355,997 |
| 18 | 2,710,711,994 | 58,069,233 | 45,618,880 | 13,959,228 | 18,612,304 | 85,340,922 | 6,815,752 | 4,194,320 | 7,340,036 | 184 | 2,950,662,853 |
| 19 | 5,901,325,706 | 117,793,963 | 93,445,048 | 27,918,396 | 37,224,528 | 175,648,296 | 13,631,496 | 8,388,624 | 14,680,068 | 184 | 6,390,056,309 |

The outer driver computes each next degree by subtracting `2^j-1`; it does not contain a degree table.

| step | degree | j | budget | node | apply plan:points | apply | driver | total |
| ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 4,882,812 | 19 | 524,287 | 6,390,056,309 | truncated:4,915,200 | 3,453,125,877 | 2,031 | 9,843,184,217 |
| 2 | 4,358,525 | 19 | 524,287 | 6,390,056,309 | truncated:4,915,200 | 3,453,781,241 | 2,031 | 9,843,839,581 |
| 3 | 3,834,238 | 19 | 524,287 | 6,390,056,309 | truncated:4,915,200 | 3,454,436,605 | 2,031 | 9,844,494,945 |
| 4 | 3,309,951 | 19 | 524,287 | 6,390,056,309 | truncated:4,915,200 | 3,455,091,927 | 2,031 | 9,845,150,267 |
| 5 | 2,785,664 | 19 | 524,287 | 6,390,056,309 | truncated:4,915,200 | 3,455,747,291 | 2,031 | 9,845,805,631 |
| 6 | 2,261,377 | 19 | 524,287 | 6,390,056,309 | truncated:4,915,200 | 3,456,402,655 | 2,031 | 9,846,460,995 |
| 7 | 1,737,090 | 19 | 524,287 | 6,390,056,309 | direct:1,572,864 | 1,976,994,141 | 2,031 | 8,367,052,481 |
| 8 | 1,212,803 | 19 | 524,287 | 6,390,056,309 | direct:786,432 | 966,905,311 | 2,031 | 7,356,963,651 |
| 9 | 688,516 | 18 | 262,143 | 2,950,662,853 | direct:524,288 | 617,342,065 | 2,031 | 3,568,006,949 |
| 10 | 426,373 | 17 | 131,071 | 1,355,355,997 | direct:393,216 | 465,949,315 | 2,031 | 1,821,307,343 |
| 11 | 295,302 | 17 | 131,071 | 1,355,355,997 | direct:196,608 | 232,290,053 | 2,031 | 1,587,648,081 |
| 12 | 164,231 | 16 | 65,535 | 618,325,913 | direct:131,072 | 144,751,853 | 2,031 | 763,079,797 |
| 13 | 98,696 | 15 | 32,767 | 279,337,383 | direct:98,304 | 116,476,799 | 2,031 | 395,816,213 |
| 14 | 65,929 | 15 | 32,767 | 279,337,383 | direct:49,152 | 47,038,377 | 2,031 | 326,377,791 |
| 15 | 33,162 | 14 | 16,383 | 126,836,231 | direct:24,576 | 22,489,131 | 2,031 | 149,327,393 |
| 16 | 16,779 | 13 | 8,191 | 57,175,591 | direct:12,288 | 10,796,717 | 2,031 | 67,974,339 |
| 17 | 8,588 | 12 | 4,095 | 25,543,207 | direct:6,144 | 5,237,807 | 2,031 | 30,783,045 |
| 18 | 4,493 | 11 | 2,047 | 11,278,103 | direct:3,072 | 2,598,193 | 2,031 | 13,878,327 |
| 19 | 2,446 | 10 | 1,023 | 4,897,791 | direct:1,536 | 1,344,499 | 2,031 | 6,244,321 |
| 20 | 1,423 | 9 | 511 | 2,072,739 | direct:1,024 | 777,707 | 2,031 | 2,852,477 |
| 21 | 912 | 8 | 255 | 837,893 | direct:768 | 732,365 | 2,031 | 1,572,289 |
| 22 | 657 | 8 | 255 | 837,893 | direct:512 | 401,039 | 2,031 | 1,240,963 |
| 23 | 402 | 7 | 127 | 328,351 | direct:384 | 319,305 | 2,031 | 649,687 |
| 24 | 275 | 7 | 127 | 328,351 | direct:192 | 192,931 | 2,031 | 523,313 |

| part | operations |
| --- | ---: |
| 24 outer steps | 83,530,234,096 |
| classical Euclid | 180,412 |
| normalization | 2,653 |
| entry | 1,012 |
| exit and frees | 317 |
| **row D** | **83,530,418,490** |

### E.3 Event-by-event allocation walk

| # | stage | action | block | side | bytes | low extent | high extent | extent sum | live bytes |
| ---: | --- | --- | --- | :---: | ---: | ---: | ---: | ---: | ---: |
| 1 | A | alloc | A-g | H | 157,286,464 | 0 | 157,286,464 | 157,286,464 | 157,286,464 |
| 2 | A | free | A-g | H | 157,286,464 | 0 | 0 | 0 | 0 |
| 3 | B | alloc | B-values | H | 201,326,656 | 0 | 201,326,656 | 201,326,656 | 201,326,656 |
| 4 | B | alloc | B-table | H | 33,554,496 | 0 | 234,881,152 | 234,881,152 | 234,881,152 |
| 5 | B | alloc | g | L | 157,286,464 | 157,286,464 | 234,881,152 | 392,167,616 | 392,167,616 |
| 6 | B | free | B-table | H | 33,554,496 | 157,286,464 | 201,326,656 | 358,613,120 | 358,613,120 |
| 7 | B | free | B-values | H | 201,326,656 | 157,286,464 | 0 | 157,286,464 | 157,286,464 |
| 8 | C | alloc | root-tables | L | 527,744 | 157,814,208 | 0 | 157,814,208 | 157,814,208 |
| 9 | C | alloc | graeffe-E | L | 157,286,464 | 315,100,672 | 0 | 315,100,672 | 315,100,672 |
| 10 | C | alloc | graeffe-O | H | 157,286,464 | 315,100,672 | 157,286,464 | 472,387,136 | 472,387,136 |
| 11 | C | alloc | graeffe-batch | H | 262,208 | 315,100,672 | 157,548,672 | 472,649,344 | 472,649,344 |
| 12 | C | free | graeffe-batch | H | 262,208 | 315,100,672 | 157,286,464 | 472,387,136 | 472,387,136 |
| 13 | C | free | graeffe-O | H | 157,286,464 | 315,100,672 | 0 | 315,100,672 | 315,100,672 |
| 14 | C | free | graeffe-E | L | 157,286,464 | 157,814,208 | 0 | 157,814,208 | 157,814,208 |
| 15 | C | alloc | newton-reversed | L | 17,813,760 | 175,627,968 | 0 | 175,627,968 | 175,627,968 |
| 16 | C | alloc | newton-reciprocal | L | 17,813,760 | 193,441,728 | 0 | 193,441,728 | 193,441,728 |
| 17 | C | alloc | newton-scratch | H | 17,813,760 | 193,441,728 | 17,813,760 | 211,255,488 | 211,255,488 |
| 18 | C | alloc | newton-transform | H | 50,331,712 | 193,441,728 | 68,145,472 | 261,587,200 | 261,587,200 |
| 19 | C | free | newton-transform | H | 50,331,712 | 193,441,728 | 17,813,760 | 211,255,488 | 211,255,488 |
| 20 | C | free | newton-scratch | H | 17,813,760 | 193,441,728 | 0 | 193,441,728 | 193,441,728 |
| 21 | C | alloc | quotient-output | H | 17,813,760 | 193,441,728 | 17,813,760 | 211,255,488 | 211,255,488 |
| 22 | C | alloc | quotient-transform | H | 50,331,712 | 193,441,728 | 68,145,472 | 261,587,200 | 261,587,200 |
| 23 | C | free | quotient-transform | H | 50,331,712 | 193,441,728 | 17,813,760 | 211,255,488 | 211,255,488 |
| 24 | C | free | quotient-output | H | 17,813,760 | 193,441,728 | 0 | 193,441,728 | 193,441,728 |
| 25 | C | free | newton-reciprocal | L | 17,813,760 | 175,627,968 | 0 | 175,627,968 | 175,627,968 |
| 26 | C | free | newton-reversed | L | 17,813,760 | 157,814,208 | 0 | 157,814,208 | 157,814,208 |
| 27 | C | alloc | A-O2 | L | 157,286,464 | 315,100,672 | 0 | 315,100,672 | 315,100,672 |
| 28 | C | alloc | k1-O1 | L | 157,286,464 | 472,387,136 | 0 | 472,387,136 | 472,387,136 |
| 29 | C | alloc | A-O1 | H | 157,286,464 | 472,387,136 | 157,286,464 | 629,673,600 | 629,673,600 |
| 30 | C | alloc | batch | H | 262,208 | 472,387,136 | 157,548,672 | 629,935,808 | 629,935,808 |
| 31 | C | free | batch | H | 262,208 | 472,387,136 | 157,286,464 | 629,673,600 | 629,673,600 |
| 32 | C | free | k1-O1 | L | 157,286,464 | 315,100,672 | 157,286,464 | 472,387,136 | 472,387,136 |
| 33 | C | free | A-O2 | L | 157,286,464 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 34 | D | alloc | D1-node | L | 268,427,328 | 426,241,536 | 157,286,464 | 583,528,000 | 583,528,000 |
| 35 | D | free | D1-node | L | 268,427,328 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 36 | D | alloc | D1-matrix | L | 67,108,928 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 37 | D | alloc | D1-transform | L | 157,286,464 | 382,209,600 | 157,286,464 | 539,496,064 | 539,496,064 |
| 38 | D | free | D1-transform | L | 157,286,464 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 39 | D | free | D1-matrix | L | 67,108,928 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 40 | D | alloc | D2-node | L | 268,427,328 | 426,241,536 | 157,286,464 | 583,528,000 | 583,528,000 |
| 41 | D | free | D2-node | L | 268,427,328 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 42 | D | alloc | D2-matrix | L | 67,108,928 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 43 | D | alloc | D2-transform | L | 157,286,464 | 382,209,600 | 157,286,464 | 539,496,064 | 539,496,064 |
| 44 | D | free | D2-transform | L | 157,286,464 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 45 | D | free | D2-matrix | L | 67,108,928 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 46 | D | alloc | D3-node | L | 268,427,328 | 426,241,536 | 157,286,464 | 583,528,000 | 583,528,000 |
| 47 | D | free | D3-node | L | 268,427,328 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 48 | D | alloc | D3-matrix | L | 67,108,928 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 49 | D | alloc | D3-transform | L | 157,286,464 | 382,209,600 | 157,286,464 | 539,496,064 | 539,496,064 |
| 50 | D | free | D3-transform | L | 157,286,464 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 51 | D | free | D3-matrix | L | 67,108,928 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 52 | D | alloc | D4-node | L | 268,427,328 | 426,241,536 | 157,286,464 | 583,528,000 | 583,528,000 |
| 53 | D | free | D4-node | L | 268,427,328 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 54 | D | alloc | D4-matrix | L | 67,108,928 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 55 | D | alloc | D4-transform | L | 157,286,464 | 382,209,600 | 157,286,464 | 539,496,064 | 539,496,064 |
| 56 | D | free | D4-transform | L | 157,286,464 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 57 | D | free | D4-matrix | L | 67,108,928 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 58 | D | alloc | D5-node | L | 268,427,328 | 426,241,536 | 157,286,464 | 583,528,000 | 583,528,000 |
| 59 | D | free | D5-node | L | 268,427,328 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 60 | D | alloc | D5-matrix | L | 67,108,928 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 61 | D | alloc | D5-transform | L | 157,286,464 | 382,209,600 | 157,286,464 | 539,496,064 | 539,496,064 |
| 62 | D | free | D5-transform | L | 157,286,464 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 63 | D | free | D5-matrix | L | 67,108,928 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 64 | D | alloc | D6-node | L | 268,427,328 | 426,241,536 | 157,286,464 | 583,528,000 | 583,528,000 |
| 65 | D | free | D6-node | L | 268,427,328 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 66 | D | alloc | D6-matrix | L | 67,108,928 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 67 | D | alloc | D6-transform | L | 157,286,464 | 382,209,600 | 157,286,464 | 539,496,064 | 539,496,064 |
| 68 | D | free | D6-transform | L | 157,286,464 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 69 | D | free | D6-matrix | L | 67,108,928 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 70 | D | alloc | D7-node | L | 268,427,328 | 426,241,536 | 157,286,464 | 583,528,000 | 583,528,000 |
| 71 | D | free | D7-node | L | 268,427,328 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 72 | D | alloc | D7-matrix | L | 67,108,928 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 73 | D | alloc | D7-transform | L | 50,331,712 | 275,254,848 | 157,286,464 | 432,541,312 | 432,541,312 |
| 74 | D | free | D7-transform | L | 50,331,712 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 75 | D | free | D7-matrix | L | 67,108,928 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 76 | D | alloc | D8-node | L | 268,427,328 | 426,241,536 | 157,286,464 | 583,528,000 | 583,528,000 |
| 77 | D | free | D8-node | L | 268,427,328 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 78 | D | alloc | D8-matrix | L | 67,108,928 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 79 | D | alloc | D8-transform | L | 25,165,888 | 250,089,024 | 157,286,464 | 407,375,488 | 407,375,488 |
| 80 | D | free | D8-transform | L | 25,165,888 | 224,923,136 | 157,286,464 | 382,209,600 | 382,209,600 |
| 81 | D | free | D8-matrix | L | 67,108,928 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 82 | D | alloc | D9-node | L | 134,209,600 | 292,023,808 | 157,286,464 | 449,310,272 | 449,310,272 |
| 83 | D | free | D9-node | L | 134,209,600 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 84 | D | alloc | D9-matrix | L | 33,554,496 | 191,368,704 | 157,286,464 | 348,655,168 | 348,655,168 |
| 85 | D | alloc | D9-transform | L | 16,777,280 | 208,145,984 | 157,286,464 | 365,432,448 | 365,432,448 |
| 86 | D | free | D9-transform | L | 16,777,280 | 191,368,704 | 157,286,464 | 348,655,168 | 348,655,168 |
| 87 | D | free | D9-matrix | L | 33,554,496 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 88 | D | alloc | D10-node | L | 67,100,736 | 224,914,944 | 157,286,464 | 382,201,408 | 382,201,408 |
| 89 | D | free | D10-node | L | 67,100,736 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 90 | D | alloc | D10-matrix | L | 16,777,280 | 174,591,488 | 157,286,464 | 331,877,952 | 331,877,952 |
| 91 | D | alloc | D10-transform | L | 12,582,976 | 187,174,464 | 157,286,464 | 344,460,928 | 344,460,928 |
| 92 | D | free | D10-transform | L | 12,582,976 | 174,591,488 | 157,286,464 | 331,877,952 | 331,877,952 |
| 93 | D | free | D10-matrix | L | 16,777,280 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 94 | D | alloc | D11-node | L | 67,100,736 | 224,914,944 | 157,286,464 | 382,201,408 | 382,201,408 |
| 95 | D | free | D11-node | L | 67,100,736 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 96 | D | alloc | D11-matrix | L | 16,777,280 | 174,591,488 | 157,286,464 | 331,877,952 | 331,877,952 |
| 97 | D | alloc | D11-transform | L | 6,291,520 | 180,883,008 | 157,286,464 | 338,169,472 | 338,169,472 |
| 98 | D | free | D11-transform | L | 6,291,520 | 174,591,488 | 157,286,464 | 331,877,952 | 331,877,952 |
| 99 | D | free | D11-matrix | L | 16,777,280 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 100 | D | alloc | D12-node | L | 33,546,304 | 191,360,512 | 157,286,464 | 348,646,976 | 348,646,976 |
| 101 | D | free | D12-node | L | 33,546,304 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 102 | D | alloc | D12-matrix | L | 8,388,672 | 166,202,880 | 157,286,464 | 323,489,344 | 323,489,344 |
| 103 | D | alloc | D12-transform | L | 4,194,368 | 170,397,248 | 157,286,464 | 327,683,712 | 327,683,712 |
| 104 | D | free | D12-transform | L | 4,194,368 | 166,202,880 | 157,286,464 | 323,489,344 | 323,489,344 |
| 105 | D | free | D12-matrix | L | 8,388,672 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 106 | D | alloc | D13-node | L | 16,769,088 | 174,583,296 | 157,286,464 | 331,869,760 | 331,869,760 |
| 107 | D | free | D13-node | L | 16,769,088 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 108 | D | alloc | D13-matrix | L | 4,194,368 | 162,008,576 | 157,286,464 | 319,295,040 | 319,295,040 |
| 109 | D | alloc | D13-transform | L | 3,145,792 | 165,154,368 | 157,286,464 | 322,440,832 | 322,440,832 |
| 110 | D | free | D13-transform | L | 3,145,792 | 162,008,576 | 157,286,464 | 319,295,040 | 319,295,040 |
| 111 | D | free | D13-matrix | L | 4,194,368 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 112 | D | alloc | D14-node | L | 16,769,088 | 174,583,296 | 157,286,464 | 331,869,760 | 331,869,760 |
| 113 | D | free | D14-node | L | 16,769,088 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 114 | D | alloc | D14-matrix | L | 4,194,368 | 162,008,576 | 157,286,464 | 319,295,040 | 319,295,040 |
| 115 | D | alloc | D14-transform | L | 1,572,928 | 163,581,504 | 157,286,464 | 320,867,968 | 320,867,968 |
| 116 | D | free | D14-transform | L | 1,572,928 | 162,008,576 | 157,286,464 | 319,295,040 | 319,295,040 |
| 117 | D | free | D14-matrix | L | 4,194,368 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 118 | D | alloc | D15-node | L | 8,380,480 | 166,194,688 | 157,286,464 | 323,481,152 | 323,481,152 |
| 119 | D | free | D15-node | L | 8,380,480 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 120 | D | alloc | D15-matrix | L | 2,097,216 | 159,911,424 | 157,286,464 | 317,197,888 | 317,197,888 |
| 121 | D | alloc | D15-transform | L | 786,496 | 160,697,920 | 157,286,464 | 317,984,384 | 317,984,384 |
| 122 | D | free | D15-transform | L | 786,496 | 159,911,424 | 157,286,464 | 317,197,888 | 317,197,888 |
| 123 | D | free | D15-matrix | L | 2,097,216 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 124 | D | alloc | D16-node | L | 4,186,176 | 162,000,384 | 157,286,464 | 319,286,848 | 319,286,848 |
| 125 | D | free | D16-node | L | 4,186,176 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 126 | D | alloc | D16-matrix | L | 1,048,640 | 158,862,848 | 157,286,464 | 316,149,312 | 316,149,312 |
| 127 | D | alloc | D16-transform | L | 393,280 | 159,256,128 | 157,286,464 | 316,542,592 | 316,542,592 |
| 128 | D | free | D16-transform | L | 393,280 | 158,862,848 | 157,286,464 | 316,149,312 | 316,149,312 |
| 129 | D | free | D16-matrix | L | 1,048,640 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 130 | D | alloc | D17-node | L | 2,089,024 | 159,903,232 | 157,286,464 | 317,189,696 | 317,189,696 |
| 131 | D | free | D17-node | L | 2,089,024 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 132 | D | alloc | D17-matrix | L | 524,352 | 158,338,560 | 157,286,464 | 315,625,024 | 315,625,024 |
| 133 | D | alloc | D17-transform | L | 196,672 | 158,535,232 | 157,286,464 | 315,821,696 | 315,821,696 |
| 134 | D | free | D17-transform | L | 196,672 | 158,338,560 | 157,286,464 | 315,625,024 | 315,625,024 |
| 135 | D | free | D17-matrix | L | 524,352 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 136 | D | alloc | D18-node | L | 1,040,448 | 158,854,656 | 157,286,464 | 316,141,120 | 316,141,120 |
| 137 | D | free | D18-node | L | 1,040,448 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 138 | D | alloc | D18-matrix | L | 262,208 | 158,076,416 | 157,286,464 | 315,362,880 | 315,362,880 |
| 139 | D | alloc | D18-transform | L | 98,368 | 158,174,784 | 157,286,464 | 315,461,248 | 315,461,248 |
| 140 | D | free | D18-transform | L | 98,368 | 158,076,416 | 157,286,464 | 315,362,880 | 315,362,880 |
| 141 | D | free | D18-matrix | L | 262,208 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 142 | D | alloc | D19-node | L | 516,160 | 158,330,368 | 157,286,464 | 315,616,832 | 315,616,832 |
| 143 | D | free | D19-node | L | 516,160 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 144 | D | alloc | D19-matrix | L | 131,136 | 157,945,344 | 157,286,464 | 315,231,808 | 315,231,808 |
| 145 | D | alloc | D19-transform | L | 49,216 | 157,994,560 | 157,286,464 | 315,281,024 | 315,281,024 |
| 146 | D | free | D19-transform | L | 49,216 | 157,945,344 | 157,286,464 | 315,231,808 | 315,231,808 |
| 147 | D | free | D19-matrix | L | 131,136 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 148 | D | alloc | D20-node | L | 254,016 | 158,068,224 | 157,286,464 | 315,354,688 | 315,354,688 |
| 149 | D | free | D20-node | L | 254,016 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 150 | D | alloc | D20-matrix | L | 65,600 | 157,879,808 | 157,286,464 | 315,166,272 | 315,166,272 |
| 151 | D | alloc | D20-transform | L | 32,832 | 157,912,640 | 157,286,464 | 315,199,104 | 315,199,104 |
| 152 | D | free | D20-transform | L | 32,832 | 157,879,808 | 157,286,464 | 315,166,272 | 315,166,272 |
| 153 | D | free | D20-matrix | L | 65,600 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 154 | D | alloc | D21-node | L | 122,944 | 157,937,152 | 157,286,464 | 315,223,616 | 315,223,616 |
| 155 | D | free | D21-node | L | 122,944 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 156 | D | alloc | D21-matrix | L | 32,832 | 157,847,040 | 157,286,464 | 315,133,504 | 315,133,504 |
| 157 | D | alloc | D21-transform | L | 24,640 | 157,871,680 | 157,286,464 | 315,158,144 | 315,158,144 |
| 158 | D | free | D21-transform | L | 24,640 | 157,847,040 | 157,286,464 | 315,133,504 | 315,133,504 |
| 159 | D | free | D21-matrix | L | 32,832 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 160 | D | alloc | D22-node | L | 122,944 | 157,937,152 | 157,286,464 | 315,223,616 | 315,223,616 |
| 161 | D | free | D22-node | L | 122,944 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 162 | D | alloc | D22-matrix | L | 32,832 | 157,847,040 | 157,286,464 | 315,133,504 | 315,133,504 |
| 163 | D | alloc | D22-transform | L | 16,448 | 157,863,488 | 157,286,464 | 315,149,952 | 315,149,952 |
| 164 | D | free | D22-transform | L | 16,448 | 157,847,040 | 157,286,464 | 315,133,504 | 315,133,504 |
| 165 | D | free | D22-matrix | L | 32,832 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 166 | D | alloc | D23-node | L | 57,408 | 157,871,616 | 157,286,464 | 315,158,080 | 315,158,080 |
| 167 | D | free | D23-node | L | 57,408 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 168 | D | alloc | D23-matrix | L | 16,448 | 157,830,656 | 157,286,464 | 315,117,120 | 315,117,120 |
| 169 | D | alloc | D23-transform | L | 12,352 | 157,843,008 | 157,286,464 | 315,129,472 | 315,129,472 |
| 170 | D | free | D23-transform | L | 12,352 | 157,830,656 | 157,286,464 | 315,117,120 | 315,117,120 |
| 171 | D | free | D23-matrix | L | 16,448 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 172 | D | alloc | D24-node | L | 57,408 | 157,871,616 | 157,286,464 | 315,158,080 | 315,158,080 |
| 173 | D | free | D24-node | L | 57,408 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 174 | D | alloc | D24-matrix | L | 16,448 | 157,830,656 | 157,286,464 | 315,117,120 | 315,117,120 |
| 175 | D | alloc | D24-transform | L | 6,208 | 157,836,864 | 157,286,464 | 315,123,328 | 315,123,328 |
| 176 | D | free | D24-transform | L | 6,208 | 157,830,656 | 157,286,464 | 315,117,120 | 315,117,120 |
| 177 | D | free | D24-matrix | L | 16,448 | 157,814,208 | 157,286,464 | 315,100,672 | 315,100,672 |
| 178 | D | free | root-tables | L | 527,744 | 157,286,464 | 157,286,464 | 314,572,928 | 314,572,928 |
| 179 | D | free | A-O1 | H | 157,286,464 | 157,286,464 | 0 | 157,286,464 | 157,286,464 |
| 180 | D | free | g | L | 157,286,464 | 0 | 0 | 0 | 0 |

The maximum extent sum in the table is 629,935,808 bytes. Adding the middle gap and both slab regions gives 629,952,832 bytes. The fixed regions then give 630,494,304 bytes.

## Appendix X: embedded exact-integer script

The following exact-integer script computes every number in sections 4.2, 6, 7 and Appendix E from the target dimensions and primitive event formulas. It reads no candidate, score table or prior ledger.

```python
#!/usr/bin/env python3
"""Self-contained exact-integer ledger for one union-machine reprice.

The program starts from the target degree, the field, and machine-event
charges.  It does not contain a row total, N_max, memory peak, or score copied
from another candidate.  All divisions are integer divisions with asserted
remainders, and all logarithms are used only after the integer ledger closes.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, getcontext
from functools import cache


getcontext().prec = 90

PALLAS_P = 0x40000000000000000000000000000000224698FC094CF91B992D30ED00000001
CONFIG = {'rounds': 4, 'graeffe_depth': 20, 'vshift_log': 19, 'truncated_nodes': 75, 'node_log': 16, 'full_log': 23, 'hgcd_cap': 19, 'tail_degree': 148, 'top_width': 3, 'bottom_width': 5, 'middle_widths': [7, 4, 4], 'active_top_cosets': 5, 'top_fused_core': 79, 'top_half_core': 44, 'inverse_top_core': 48, 'recovery_closing_words': 2, 'recovery_subtrees': [[1, 7], [4, 5], [16, 3], [32, 2]], 'batch_words': 8192, 'inversion_chunk_log': 13, 'stage_b_log': 21, 'outer_decrement_extra': 0, 'direct_row_cap': 1572864, 'apply_mode': 'truncated', 'slab_slots': 0, 'slab_class_log': 7, 'expected_outer_steps': 24, 'expected_squarings': 214, 'expected_multiplies': 45}
ROUNDS = CONFIG["rounds"]
DEGREE = 5 ** (ROUNDS + 6)
ODD_DEGREE = (DEGREE - 1) // 2
COMPRESSION = 216 + 21 * ROUNDS
LINE_EVALUATION = 155 + 21 * ROUNDS

GRAEFFE_DEPTH = CONFIG["graeffe_depth"]
ROOT_SCAN_LOG = GRAEFFE_DEPTH
VSHIFT_LOG = CONFIG["vshift_log"]
TRUNCATED_NODES = CONFIG["truncated_nodes"]
NODE_WORDS = 1 << CONFIG["node_log"]
TRUNCATED_POINTS = TRUNCATED_NODES * NODE_WORDS
FULL_POINTS = 1 << CONFIG["full_log"]
VSHIFT = 1 << VSHIFT_LOG
ELL = VSHIFT + TRUNCATED_POINTS - ODD_DEGREE + 1
HGCD_CAP = CONFIG["hgcd_cap"]
TAIL_DEGREE = CONFIG["tail_degree"]
TOP_WIDTH = CONFIG["top_width"]
BOTTOM_WIDTH = CONFIG["bottom_width"]
TR_MIDDLE_WIDTHS = tuple(CONFIG["middle_widths"])
RECOVERY_SUBTREES = tuple(tuple(row) for row in CONFIG["recovery_subtrees"])
BATCH_WORDS = CONFIG["batch_words"]
INVERSION_CHUNK = 1 << CONFIG["inversion_chunk_log"]
STAGE_B_LOG = CONFIG["stage_b_log"]
OUTER_DECREMENT_EXTRA = CONFIG["outer_decrement_extra"]
DIRECT_ROW_CAP = CONFIG["direct_row_cap"]
APPLY_MODE = CONFIG["apply_mode"]
LMAX = CONFIG.get("lmax", 0)
BLOCK_LENGTH = CONFIG.get("block_length", 0)
SLAB_AREA = CONFIG["slab_slots"] * (1 << CONFIG["slab_class_log"])
EXPECTED_OUTER_STEPS = CONFIG["expected_outer_steps"]
EXPECTED_SQUARINGS = CONFIG["expected_squarings"]
EXPECTED_MULTIPLIES = CONFIG["expected_multiplies"]

WORD_BYTES = 32
POOL_GAP = 128
LATE_SLAB = 16_896


def ceil_decimal(value: Decimal, places: int) -> Decimal:
    return value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_CEILING)


def loop8(count: int) -> int:
    """Control for an eight-position straight-line loop and its remainder."""
    assert count >= 0
    return 1 + 3 * (count // 8) + 2 + 3 * (count % 8) + 2


def linear_loop(count: int) -> int:
    assert count >= 0
    return 3 * count + 2


def block_bytes(words: int) -> int:
    assert words >= 0
    payload = ((words * WORD_BYTES + 63) // 64) * 64
    return payload + 64


# ---------------------------------------------------------------------------
# Union-machine transform primitives
# ---------------------------------------------------------------------------


def pass_schedule(layers: int) -> tuple[tuple[int, int], ...]:
    """First the remainder and then full seven-layer passes."""
    assert layers >= 1
    first = layers % 7 or 7
    result = [(0, first)]
    level = first
    while level < layers:
        result.append((level, 7))
        level += 7
    return tuple(result)


def block_body(width: int) -> int:
    """Loads/stores, butterflies, bases, and four-block loop share."""
    assert 1 <= width <= 7
    radix = 1 << width
    return 2 * radix + 3 * width * (radix // 2) + 3


def running_chain(width: int) -> int:
    """Root advance, squarings, constant multiplies, and five controls."""
    assert 1 <= width <= 7
    return (1 << width) + 4


def shared_running_pass(layers: int, level: int, width: int,
                        inverse: bool = False) -> int:
    """Executed running-twiddle block-form pass.

    One chain is shared by all groups at a position.  Group zero receives the
    exact twiddle-one saving.  The fixed 159*k+19/20 charge is 150*k constant
    construction, 9*k pointer setup, and 19/20 call/exit operations.
    """
    assert 0 <= level and 1 <= width <= 7 and level + width <= layers
    blocks = 1 << (layers - width)
    positions = 1 << (layers - level - width)
    group_zero_blocks = positions
    fixed = 159 * width + (20 if inverse else 19)
    twiddle_one = group_zero_blocks * ((1 << width) - 1)
    return (
        blocks * block_body(width)
        + positions * running_chain(width)
        + fixed
        - twiddle_one
        + 3
    )


def per_block_upper_pass(layers: int, level: int, width: int,
                         inverse: bool = False) -> int:
    """Finite per-block upper used only inside half-gcd nodes.

    Unlike the executed pass, every block pays a complete running chain.  This
    subsumes all sharing choices; there is no percentage allowance.
    """
    assert 0 <= level and 1 <= width <= 7 and level + width <= layers
    blocks = 1 << (layers - width)
    group_zero_blocks = 1 << (layers - level - width)
    fixed = 159 * width + (20 if inverse else 19)
    twiddle_one = group_zero_blocks * ((1 << width) - 1)
    return (
        blocks * (block_body(width) + running_chain(width))
        + fixed
        - twiddle_one
        + 3
    )


def row_transform(layers: int, inverse: bool = False,
                  per_block: bool = False) -> int:
    primitive = per_block_upper_pass if per_block else shared_running_pass
    return sum(
        primitive(layers, level, width, inverse)
        for level, width in pass_schedule(layers)
    )


def table_group_cost(width: int) -> int:
    """Stage-B table twiddles loaded once for a group."""
    assert 1 <= width <= 7
    if width <= 3:
        return 16
    if width == 4:
        return 24
    return (1 << width) + 8


def table_pass(layers: int, level: int, width: int,
               inverse: bool = False) -> int:
    """Stage-B radix-2 pass, whose twiddle table remains live."""
    blocks = 1 << (layers - width)
    groups = 1 << level
    group_zero_blocks = 1 << (layers - level - width)
    fixed = 9 * width + (38 if inverse else 37)
    return (
        blocks * block_body(width)
        + groups * table_group_cost(width)
        + fixed
        - group_zero_blocks * ((1 << width) - 1)
        + 3
    )


def table_row_transform(layers: int, inverse: bool = False) -> int:
    return sum(
        table_pass(layers, level, width, inverse)
        for level, width in pass_schedule(layers)
    )


def transform(points: int, inverse: bool = False,
              per_block: bool = False) -> int:
    """A 2^a or 3*2^a transform with running block-form passes."""
    if points & (points - 1) == 0:
        layers = points.bit_length() - 1
        return row_transform(layers, inverse, per_block)
    assert points % 3 == 0
    row = points // 3
    assert row & (row - 1) == 0
    layers = row.bit_length() - 1
    # One twiddle-free radix-3 stage, 8 operations per leaf.
    return 8 * row + 3 * row_transform(layers, inverse, per_block)


def admissible_points(required: int) -> tuple[int, ...]:
    assert required >= 2
    choices: list[int] = []
    for layers in range(1, 33):
        for points in (1 << layers, 3 * (1 << layers)):
            if points >= required:
                choices.append(points)
    return tuple(sorted(set(choices)))


@dataclass(frozen=True)
class ProductCharge:
    points: int
    transforms: int
    input_loops: int
    pointwise: int
    output_loop: int
    fixed: int

    @property
    def total(self) -> int:
        return (self.transforms + self.input_loops + self.pointwise
                + self.output_loop + self.fixed)


@cache
def product_charge(left: int, right: int, output: int) -> ProductCharge:
    """One ordinary polynomial product, fully charged.

    Inputs are copied at seven operations per coefficient, zero slots at five,
    the pointwise product at ten per point, and the output read at four per
    coefficient.  Allocation/free and dispatch contribute the named fixed 684
    operations (one pool allocation and free, two slab-free fallbacks, six
    calls, and closing tests).  Each candidate length is costed and the least
    is selected; this is a finite deterministic plan choice, not a search at
    run time.
    """
    assert left >= 1 and right >= 1 and output <= left + right - 1
    candidates: list[ProductCharge] = []
    for points in admissible_points(left + right - 1):
        transforms = 2 * transform(points) + transform(points, inverse=True)
        inputs = 7 * (left + right) + 5 * (2 * points - left - right)
        pointwise = 10 * points
        output_loop = 4 * output + loop8(output)
        candidates.append(ProductCharge(points, transforms, inputs,
                                        pointwise, output_loop, 684))
    return min(candidates, key=lambda item: (item.total, item.points))


def reciprocal_charge(precision: int) -> tuple[int, tuple[tuple[int, int], ...]]:
    """Newton reciprocal, including both products at every doubling."""
    assert precision >= 1
    current = 1
    rows: list[tuple[int, int]] = []
    total = 0
    while True:
        target = min(2 * current, precision)
        # u <- u*(2-fu) mod X^target: f*u and u*(2-fu).
        first = product_charge(target, current, target).total
        second = product_charge(current, target, target).total
        step = first + second + 12 * target + loop8(target) + 42
        rows.append((target, step))
        total += step
        if target == precision:
            return total, tuple(rows)
        current = target


# ---------------------------------------------------------------------------
# Truncated stage-C transforms on the configured live nodes
# ---------------------------------------------------------------------------


def column_kernel(width: int, positions: int, offset_zero: bool = False) -> int:
    constants = {1: 5, 2: 6, 3: 10, 4: 18, 5: 34, 6: 139, 7: 269}
    slopes = {1: 11, 2: 20, 3: 52, 4: 128, 5: 304, 6: 704, 7: 1600}
    assert width in constants and positions >= 0
    charge = constants[width] + slopes[width] * positions + loop8(positions)
    if offset_zero:
        charge -= ((1 << width) - 1) * positions
        charge += 3
    return charge


def column_call(width: int, positions: int, offset_zero: bool = False) -> int:
    rows = 1 << width
    return (2 * rows + 6) + column_kernel(width, positions, offset_zero) + 5


def truncated_middle_pass(width: int) -> int:
    """One live-node middle pass under the 256-field-register machine.

    There are n'/2^k blocks.  Four adjacent blocks share a running group
    chain; divisibility is exact at every selected width.  The final fixed
    charge is the pass entry/pointers/exit/call.  No table is allocated.
    """
    blocks, rem = divmod(TRUNCATED_POINTS, 1 << width)
    assert rem == 0 and blocks % 4 == 0
    groups = blocks // 4
    group_chain = 16 if width <= 3 else (24 if width == 4 else (1 << width) + 8)
    return blocks * block_body(width) + groups * group_chain + 159 * width + 19


def truncated_middle() -> int:
    return sum(truncated_middle_pass(width) for width in TR_MIDDLE_WIDTHS)


TOP_POSITIONS = FULL_POINTS // (1 << TOP_WIDTH)
BOTTOM_BLOCKS = TRUNCATED_POINTS // (1 << BOTTOM_WIDTH)


def top_forward() -> int:
    return column_call(TOP_WIDTH, TOP_POSITIONS, offset_zero=True)


def top_inverse() -> int:
    # One extra inverse-scale setup operation per call.
    return column_call(TOP_WIDTH, TOP_POSITIONS, offset_zero=True) + 1


def top_fused() -> int:
    """Inverse top, six active coset products, and forward top.

    Per offset: 8 loads and 8 stores; 24 butterflies in the two directions at
    three operations less fourteen twiddle-one multiplications; six coset
    multiplications; and eight pointer updates.  The position loop is unrolled
    by eight and the two calls share one wrapper.
    """
    radix = 1 << TOP_WIDTH
    per_position = CONFIG["top_fused_core"]
    return per_position * TOP_POSITIONS + loop8(TOP_POSITIONS) + 2 * radix + 11


def top_half() -> int:
    """Two pruned stride-two forwards, including their live-lane events."""
    return (CONFIG["top_half_core"] * TOP_POSITIONS
            + loop8(TOP_POSITIONS) + 37)


def inverse_top_store() -> int:
    return (CONFIG["inverse_top_core"] * TOP_POSITIONS
            + loop8(TOP_POSITIONS) + 28)


def recovery() -> int:
    path = sum(size * NODE_WORDS * (8 * depth + 2)
               for size, depth in RECOVERY_SUBTREES)
    return path + CONFIG["recovery_closing_words"] * NODE_WORDS


def bottom_forward() -> int:
    radix = 1 << BOTTOM_WIDTH
    per_block = 2 * radix + 3 * BOTTOM_WIDTH * (radix // 2) + (radix - 1) + 7
    return per_block * BOTTOM_BLOCKS + loop8(BOTTOM_BLOCKS) + 20


def bottom_inverse() -> int:
    radix = 1 << BOTTOM_WIDTH
    per_block = (
        2 * radix + 3 * BOTTOM_WIDTH * (radix // 2) + (radix - 1) + 7
        + (radix - 1) + 2
    )
    return per_block * BOTTOM_BLOCKS + loop8(BOTTOM_BLOCKS) + 21


def one_forward() -> int:
    return top_forward() + truncated_middle() + bottom_forward() + 2 * TRUNCATED_POINTS


def one_inverse() -> int:
    return (bottom_inverse() + truncated_middle() + top_inverse()
            + recovery() + 2 * TRUNCATED_POINTS)


def graeffe_step() -> int:
    # Bottom: two forward blocks, E^2-yO^2 at five operations per point, and
    # one inverse block.  Pointer/address/control terms are per block.
    radix = 1 << BOTTOM_WIDTH
    bottom_per_block = (
        3 * (2 * radix + 3 * BOTTOM_WIDTH * (radix // 2))
        + (radix - 1) + 5 * radix + 12 - (2 * radix + 3)
    )
    bottom = BOTTOM_BLOCKS * bottom_per_block + loop8(BOTTOM_BLOCKS) + 20
    return (top_half() + 3 * truncated_middle() + bottom
            + inverse_top_store() + recovery() + 40)


def powering_step(bit: int) -> int:
    assert bit in (0, 1)
    # O1 block: loads A,k1; square/multiply; stores U; bottom butterflies.
    radix = 1 << BOTTOM_WIDTH
    o1_per_block = 8 * radix + 3 * BOTTOM_WIDTH * radix + 7
    o1 = BOTTOM_BLOCKS * o1_per_block + loop8(BOTTOM_BLOCKS) + 20
    # O2 bit-zero body; a bit-one adds three point operations and one pointer
    # update for each block.
    o2 = BOTTOM_BLOCKS * (o1_per_block + 6 * radix) + loop8(BOTTOM_BLOCKS) + 20
    delta_loads = 2 * BOTTOM_BLOCKS
    address_updates = 2 * BOTTOM_BLOCKS
    extra = bit * (3 * TRUNCATED_POINTS + BOTTOM_BLOCKS)
    return (o1 + 4 * truncated_middle() + 2 * top_fused() + o2
            + delta_loads + address_updates + 2 * recovery() + extra + 20)


def exponent_bits() -> tuple[int, int]:
    exponent = (PALLAS_P - 1) >> (GRAEFFE_DEPTH + 1)
    bits = bin(exponent)[2:]
    # VSHIFT preloads the low 22 zero squarings.
    active = bits[1 + VSHIFT_LOG:]
    return len(active), active.count("1")


def stage_c_plans() -> int:
    constants = 30
    deltas = TRUNCATED_NODES
    roots = 4 * 4096
    table_words = constants + deltas + roots
    # Each word: root recurrence/multiplication, store, address and loop; the
    # node deltas additionally pay an inversion chain of 512 five-op bit steps.
    table_build = (roots + constants) * 8 + deltas * (512 * 5 + 8)
    exponent_plan = 256 * 3 + 42
    pass_plan = (3 + len(TR_MIDDLE_WIDTHS) + 1) * 64
    zero_fill = (TRUNCATED_POINTS - ODD_DEGREE - 1) * 5 + loop8(
        TRUNCATED_POINTS - ODD_DEGREE - 1
    )
    first_allocations = 4 * 655 + 31
    assert table_words == 30 + TRUNCATED_NODES + 4 * 4096
    return table_build + exponent_plan + pass_plan + zero_fill + first_allocations


def batch_inversion() -> int:
    chunk = INVERSION_CHUNK
    chunks = (TRUNCATED_POINTS + chunk - 1) // chunk
    # Prefix product 4, backward multiply 6, load/store/address 3, loop share 1
    # per point; per chunk one 512-step five-op inversion, zero test and setup.
    return (14 * TRUNCATED_POINTS + loop8(TRUNCATED_POINTS)
            + chunks * (512 * 5 + 2 + 18))


def stage_c_components() -> dict[str, int]:
    squares, multiplies = exponent_bits()
    assert squares == EXPECTED_SQUARINGS and multiplies == EXPECTED_MULTIPLIES
    reciprocal, _rows = reciprocal_charge(ELL)
    quotient_product = product_charge(ELL, ELL, 2 * ELL - 1).total
    quotient = quotient_product + 4 * ELL + loop8(ELL)
    g_to_sets = 2 * one_forward() + 2 * 655 + 31
    start_residue = (
        one_forward() + 8 * TRUNCATED_POINTS + loop8(TRUNCATED_POINTS)
        + 5 * (TRUNCATED_POINTS - ELL) + loop8(TRUNCATED_POINTS - ELL) + 655
    )
    extension = one_inverse() + one_forward() + 2 * 655 + 18
    bit0 = powering_step(0)
    bit1 = powering_step(1)
    exit_step = extension + 19 * TRUNCATED_POINTS + loop8(TRUNCATED_POINTS) + 655
    two_inverses = 2 * one_inverse() + 2 * 655 + 31
    return {
        "plans_constants_tables_zero_fill_allocations": stage_c_plans(),
        "graeffe_prefix_and_buffer": GRAEFFE_DEPTH * graeffe_step() + 2 * 655,
        "newton_reciprocal": reciprocal,
        "quotient_product_and_copy": quotient,
        "g_to_O1_and_O2": g_to_sets,
        "start_residue_on_O2": start_residue,
        "A0_extension_to_O1": extension,
        "chunked_batch_inversion": batch_inversion(),
        "powering_steps": (squares - multiplies) * bit0 + multiplies * bit1,
        "exit_montgomery_step": exit_step,
        "two_truncated_inverses": two_inverses,
        "entry_exit_bookkeeping": 1_000,
    }


STAGE_C_COMPONENTS = stage_c_components()
STAGE_C = sum(STAGE_C_COMPONENTS.values())


# ---------------------------------------------------------------------------
# Inversion-free half-gcd, with finite lower-order counts and no percentage
# ---------------------------------------------------------------------------


def copy_cost(length: int) -> int:
    return 4 * length + linear_loop(length)


def zero_cost(length: int) -> int:
    return 2 * length + linear_loop(length)


def access_cost(length: int, subtract: bool) -> int:
    return (7 + int(subtract)) * length + linear_loop(length)


def pointwise_cost(length: int, row: int) -> int:
    return (7 if row == 0 else 10) * length + loop8(length)


def base_node() -> int:
    """Exact schoolbook leaf for budget 63."""
    total = 90
    for removed in range(0, 62, 2):
        length = 2 * (62 - removed) + 1
        total += (
            76 + 13 * length + 9 * (length - 2) + linear_loop(length)
            + 2 * (13 * (removed + 2) + 9 * (removed + 3)
                   + linear_loop(removed + 3))
            + 8
        )
    removed = 62
    total += (25 + 13 + linear_loop(1)
              + 2 * (13 * (removed + 2) + linear_loop(removed + 2)) + 4)
    return total


NODE_FIXED_EVENTS = {
    "entry_and_exit": 20,
    "split_and_degree_tests": 16,
    "two_child_call_frames": 24,
    "two_return_tests": 8,
    "arena_mark_and_release": 20,
    "six_transform_dispatches": 18,
    "matrix_pointer_bundles": 48,
    "row_and_sign_selection": 18,
    "normal_sequence_tests": 12,
}


@dataclass(frozen=True)
class NodeRow:
    children: int
    top_rows: int
    returned_rows: int
    apply_pointwise: int
    matrix_pointwise: int
    inverses: int
    crt: int
    pseudo_division: int
    arrays: int
    fixed: int

    @property
    def total(self) -> int:
        return sum((self.children, self.top_rows, self.returned_rows,
                    self.apply_pointwise, self.matrix_pointwise, self.inverses,
                    self.crt, self.pseudo_division, self.arrays, self.fixed))


NODE_ROWS: dict[int, NodeRow] = {}


@cache
def node_bf(level: int) -> int:
    if level == 6:
        return base_node()
    assert level > 6
    n = 1 << (level - 1)
    layers = level - 1
    forward = row_transform(layers, per_block=True)
    inverse = row_transform(layers, inverse=True, per_block=True)

    def row(length: int, row_index: int) -> int:
        return (
            copy_cost(min(length, n))
            + zero_cost(max(0, n - length))
            + access_cost(max(0, length - n), row_index == 2)
            + 2 * n * int(row_index > 0)
            + forward
        )

    top = sum(row(1 << (level + 1), r)
              + row((1 << (level + 1)) - 1, r) for r in range(3))
    returned = (0, 1) if level == 7 else (1,)
    returns = 8 * sum(row(n, r) for r in returned)
    apply = 6 * (pointwise_cost(n, 0) + pointwise_cost(n, 2))
    matrix = 8 * (pointwise_cost(n, 0) + pointwise_cost(n, 1))
    inverses = 6 * sum(inverse + (1 + int(r > 0)) * n for r in range(3))
    crt = 4 * (10 * n + linear_loop(n))
    budget = (1 << level) - 1
    pseudo = 30 + 13 * budget + linear_loop(budget)
    arrays = 2 * (25 * n + linear_loop(n))
    fixed = sum(NODE_FIXED_EVENTS.values())
    row_value = NodeRow(2 * node_bf(level - 1), top, returns, apply,
                        matrix, inverses, crt, pseudo, arrays, fixed)
    NODE_ROWS[level] = row_value
    return row_value.total


@dataclass(frozen=True)
class ApplyCharge:
    points: int
    budget: int
    output: int
    transforms: int
    matrix_inputs: int
    operand_inputs: int
    pointwise: int
    output_loops: int
    fixed: int

    @property
    def total(self) -> int:
        return sum((self.transforms, self.matrix_inputs, self.operand_inputs,
                    self.pointwise, self.output_loops, self.fixed))


@cache
def apply_plan(degree: int, budget: int) -> ApplyCharge:
    """Four-entry matrix applied to two operands, selecting a finite plan.

    Six forwards transform four matrix entries and two operands; two inverses
    return the outputs.  Long operands are folded modulo X^P-1 at ten
    operations per excess coefficient.  P is at least the exact output length,
    so the normal-sequence high coefficients, which cancel, are recovered
    without wraparound.
    """
    output = degree - budget
    matrix_length = budget + 1
    operand_length = degree + 1
    direct_row_cap = DIRECT_ROW_CAP

    if APPLY_MODE == "block" and degree > LMAX:
        assert BLOCK_LENGTH > 0
        points = 2 * BLOCK_LENGTH
        operand_blocks = (degree + 1 + BLOCK_LENGTH - 1) // BLOCK_LENGTH
        matrix_blocks = (matrix_length + BLOCK_LENGTH - 1) // BLOCK_LENGTH
        output_blocks = (output + BLOCK_LENGTH - 1) // BLOCK_LENGTH
        transforms = (
            (4 * matrix_blocks + 2 * operand_blocks) * transform(points)
            + 2 * output_blocks * transform(points, inverse=True)
        )
        matrix_inputs = 4 * (
            7 * matrix_length
            + 5 * (matrix_blocks * points - matrix_length)
        )
        operand_inputs = 2 * (
            7 * (degree + 1)
            + 5 * (operand_blocks * points - degree - 1)
        )
        pointwise = 2 * output_blocks * (12 * points + loop8(points))
        output_loops = 2 * output_blocks * (
            7 * BLOCK_LENGTH + loop8(BLOCK_LENGTH)
        )
        fixed = (
            (4 * matrix_blocks + 2 * operand_blocks + 2 * output_blocks) * 23
            + 6 * 655 + 42
        )
        return ApplyCharge(points, budget, output, transforms, matrix_inputs,
                           operand_inputs, pointwise, output_loops, fixed)

    # The published implementation reserves at most 24 direct matrix rows of
    # 2^16 coefficients.  Above that output length it uses the same truncated
    # O1/O2 application as stage C.  Its four row batches each execute six
    # forwards and two inverses.  Matrix rows are streamed once; coefficients
    # removed by prior outer steps are folded at five operations in each of the
    # two operands.  This is an implementation restriction, not a planner
    # search or a claim about a faster output-sized product.
    if APPLY_MODE == "truncated" and output > direct_row_cap:
        matrix_rows = (matrix_length + (1 << 16) - 1) // (1 << 16)
        row_groups = max(3, (matrix_rows + 3) // 4)
        transforms = row_groups * (3 * one_forward() + one_inverse())
        matrix_inputs = 4 * 7 * matrix_length
        operand_inputs = 10 * (ODD_DEGREE - degree)
        pointwise = 12 * TRUNCATED_POINTS + loop8(TRUNCATED_POINTS)
        output_loops = 2 * (4 * output + loop8(output))
        fixed = 2 * 655 + 8 * 23 + 42
        return ApplyCharge(TRUNCATED_POINTS, budget, output, transforms,
                           matrix_inputs, operand_inputs, pointwise,
                           output_loops, fixed)

    candidates: list[ApplyCharge] = []
    for points in admissible_points(output):
        if APPLY_MODE == "block":
            transforms = 6 * transform(points) + 2 * transform(points, inverse=True)
        else:
            transforms = 24 * transform(points) + 8 * transform(points, inverse=True)
        matrix_inputs = 4 * (
            7 * matrix_length + 5 * (points - matrix_length)
        )
        if operand_length <= points:
            one_operand = 7 * operand_length + 5 * (points - operand_length)
        else:
            one_operand = 7 * points + 10 * (operand_length - points)
        operand_inputs = 2 * one_operand
        # Per point: four products, two additions/subtractions, two fused
        # inverse scales, and four loads/stores/address shares.
        pointwise = 12 * points + loop8(points)
        output_loops = 2 * (4 * output + loop8(output))
        fixed = 2 * 655 + 8 * 23 + 42
        candidates.append(ApplyCharge(points, budget, output, transforms,
                                      matrix_inputs, operand_inputs, pointwise,
                                      output_loops, fixed))
    return min(candidates, key=lambda item: (item.total, item.points))


@dataclass(frozen=True)
class OuterStep:
    degree: int
    level: int
    budget: int
    node: int
    apply: ApplyCharge
    driver: int

    @property
    def total(self) -> int:
        return self.node + self.apply.total + self.driver


def outer_steps() -> tuple[OuterStep, ...]:
    degree = ODD_DEGREE
    result: list[OuterStep] = []
    while degree > TAIL_DEGREE:
        chosen: tuple[int, int] | None = None
        for level in range(HGCD_CAP, 6, -1):
            budget = (1 << level) - 1
            if 2 * budget + 1 <= degree:
                chosen = (level, budget)
                break
        if chosen is None:
            break
        level, budget = chosen
        apply = apply_plan(degree, budget)
        # Node arena allocation/free, matrix and transform-buffer allocation/
        # frees, dispatch, degree update, quotient and return tests.
        driver = 3 * 655 + 20 + 18 + 12 + 2 * loop8(1)
        result.append(OuterStep(degree, level, budget, node_bf(level), apply,
                                driver))
        degree -= budget + OUTER_DECREMENT_EXTRA
    assert degree == TAIL_DEGREE, (degree, TAIL_DEGREE)
    return tuple(result)


OUTER_STEPS = outer_steps()


def classical_tail(degree: int) -> int:
    # For quotient degree one at live length d: 13 coefficient events, three
    # loop controls per coefficient, and 27 leading/test/update operations.
    return sum(16 * d + 27 for d in range(1, degree + 1))


def normalization() -> int:
    # One fixed 512-step inversion chain, coefficient scaling for degree <=16,
    # and call/exit control.
    return 512 * 5 + 5 * 17 + 8


STAGE_D_COMPONENTS = {
    "outer_steps": sum(step.total for step in OUTER_STEPS),
    "classical_euclid": classical_tail(TAIL_DEGREE),
    "normalization": normalization(),
    "entry": 1_012,
    "exit_and_frees": 317,
}
STAGE_D = sum(STAGE_D_COMPONENTS.values())


# ---------------------------------------------------------------------------
# The remaining rows, each from target dimensions and named finite loops
# ---------------------------------------------------------------------------


def stage_b() -> int:
    points = 3 * (1 << STAGE_B_LOG)
    row = 1 << STAGE_B_LOG
    evaluations = 2 * points * LINE_EVALUATION
    # Per point: two point adds, subtraction, quotient multiply, two root
    # recurrences, store+address, loop controls, and a 23-bit reversal bounded
    # by one shift/test pair per bit plus entry/exit.
    # The bit-reversed index is deliberately charged at eleven primitive word
    # events for each index bit: mask load, value load, two ANDs, two
    # shifts, OR, value store, bit test, branch, and loop update.
    evaluation_loop = points * (2 + 1 + 1 + 2 + 2 + 3 + 11 * STAGE_B_LOG + 2)
    radix3 = 8 * row
    inverse_transform = radix3 + 3 * table_row_transform(STAGE_B_LOG, inverse=True)
    table_words = 1 << (STAGE_B_LOG - 1)
    table_build = table_words * (5 + 3) + 42
    normalization_cost = 512 * 5 + (ODD_DEGREE + 1) * 5 + loop8(ODD_DEGREE + 1)
    allocations = 3 * 655 + 31
    return (evaluations + evaluation_loop + inverse_transform + table_build
            + normalization_cost + allocations)


def stage_e_round(degree: int = 16) -> int:
    exponent = (PALLAS_P - 1) // 2
    squarings = exponent.bit_length() - 1
    multiplies = bin(exponent).count("1") - 1
    # Per coefficient pair: ten multiply-accumulate load/store/address events,
    # six nested-loop controls, and six reduction/carry events.
    schoolbook_product = (
        (degree + 1) ** 2 * 22
        + 20 * (degree + 1) + 64
    )
    powering = (squarings + multiplies) * schoolbook_product
    taylor_shift = 8 * (degree + 1) ** 2 + linear_loop((degree + 1) ** 2) + 64
    two_gcds = 2 * sum(16 * d + 27 for d in range(1, degree + 1))
    selection = 32 * degree + 95
    return powering + taylor_shift + two_gcds + selection


STAGE_INIT = sum((201 * 8, 4 * 512 * 5, 6 * 1_024, 17))
STAGE_SETUP = sum((3 * 512, 9 * 256, 3 * 321, 103))
STAGE_A = sum((2, 512 * 2, 2 * 97, 8))
STAGE_B = stage_b()
STAGE_E = 64 * stage_e_round() + 2 * 655 + 1_000
STAGE_F = (
    (GRAEFFE_DEPTH + 1) * 47_012
    + (1 << ROOT_SCAN_LOG) * (
        1 + 2 + 2 * LINE_EVALUATION + 4 + 2 + 3
    )
    + 2
    + 47_012
)
STAGE_G = 2 * (COMPRESSION + 3_405) + 2
TRIAL_LOOP = 1_000 + 12
PLAN_MISSES = 17 * (5 * 1_024 + 3 * 256 + 7)
OUTPUT = 2 * (5 * (1 << 18) + 4 * (1 << 17) + 3 * (1 << 16) + 80)
OFFLINE_EXACT = (
    202 * (64 * 5 + 4)
    + 4 * 489 + 3 * 222
    + 3 * 90
    + 211 * (64 * 5 + 4) + (16 * 5 + 1)
)
OFFLINE_CHARGE = 1_000_000
assert OFFLINE_EXACT <= OFFLINE_CHARGE

LEDGER = {
    "init": STAGE_INIT,
    "setup": STAGE_SETUP,
    "A": STAGE_A,
    "B": STAGE_B,
    "C": STAGE_C,
    "D": STAGE_D,
    "E": STAGE_E,
    "F": STAGE_F,
    "G": STAGE_G,
    "trial_loop": TRIAL_LOOP,
    "plan_misses": PLAN_MISSES,
    "output": OUTPUT,
    "offline": OFFLINE_CHARGE,
}
N_MAX = sum(LEDGER.values())


# ---------------------------------------------------------------------------
# Event-by-event two-ended first-fit allocator walk
# ---------------------------------------------------------------------------


@dataclass
class Segment:
    start: int
    size: int
    live: bool
    name: str | None = None


class PoolSide:
    def __init__(self) -> None:
        self.segments: list[Segment] = []
        self.extent = 0

    def allocate(self, name: str, size: int) -> None:
        for index, segment in enumerate(self.segments):
            if not segment.live and segment.size >= size:
                replacement = [Segment(segment.start, size, True, name)]
                if segment.size > size:
                    replacement.append(Segment(segment.start + size,
                                               segment.size - size, False))
                self.segments[index:index + 1] = replacement
                return
        self.segments.append(Segment(self.extent, size, True, name))
        self.extent += size

    def free(self, name: str) -> None:
        matches = [segment for segment in self.segments
                   if segment.live and segment.name == name]
        assert len(matches) == 1, (name, matches)
        matches[0].live = False
        matches[0].name = None
        merged: list[Segment] = []
        for segment in self.segments:
            if merged and not merged[-1].live and not segment.live:
                merged[-1].size += segment.size
            else:
                merged.append(segment)
        while merged and not merged[-1].live:
            self.extent = merged[-1].start
            merged.pop()
        self.segments = merged


@dataclass(frozen=True)
class MemoryEvent:
    number: int
    stage: str
    action: str
    name: str
    side: str
    size: int
    low: int
    high: int
    extent_sum: int
    live: int


class ArenaWalk:
    def __init__(self) -> None:
        self.low = PoolSide()
        self.high = PoolSide()
        self.events: list[MemoryEvent] = []
        self.sizes: dict[str, tuple[str, int]] = {}
        self.peak = 0
        self.stage_peaks: dict[str, int] = {}

    def _record(self, stage: str, action: str, name: str,
                side: str, size: int) -> None:
        live = sum(segment.size for pool in (self.low, self.high)
                   for segment in pool.segments if segment.live)
        extent_sum = self.low.extent + self.high.extent
        event = MemoryEvent(len(self.events) + 1, stage, action, name, side,
                            size, self.low.extent, self.high.extent,
                            extent_sum, live)
        self.events.append(event)
        self.peak = max(self.peak, extent_sum)
        self.stage_peaks[stage] = max(self.stage_peaks.get(stage, 0), live)

    def alloc(self, stage: str, name: str, words: int,
              side: str = "L") -> None:
        assert name not in self.sizes
        size = block_bytes(words)
        pool = self.low if side == "L" else self.high
        pool.allocate(name, size)
        self.sizes[name] = (side, size)
        self._record(stage, "alloc", name, side, size)

    def free(self, stage: str, name: str) -> None:
        side, size = self.sizes.pop(name)
        pool = self.low if side == "L" else self.high
        pool.free(name)
        self._record(stage, "free", name, side, size)


def memory_walk() -> ArenaWalk:
    walk = ArenaWalk()
    # A: output polynomial allocation.
    walk.alloc("A", "A-g", TRUNCATED_POINTS, "H")
    walk.free("A", "A-g")

    # B: evaluation array, transform table and resulting coefficient array.
    walk.alloc("B", "B-values", 3 * (1 << STAGE_B_LOG), "H")
    walk.alloc("B", "B-table", 1 << (STAGE_B_LOG - 1), "H")
    walk.alloc("B", "g", TRUNCATED_POINTS, "L")
    walk.free("B", "B-table")
    walk.free("B", "B-values")

    # C: table construction, Graeffe scratch, Newton/quotient work, then the
    # four long-lived value arrays.  Temporary phases do not overlap unless the
    # algorithm consumes both objects at once.
    walk.alloc("C", "root-tables", 30 + TRUNCATED_NODES + 4 * 4096, "L")
    walk.alloc("C", "graeffe-E", TRUNCATED_POINTS, "L")
    walk.alloc("C", "graeffe-O", TRUNCATED_POINTS, "H")
    walk.alloc("C", "graeffe-batch", BATCH_WORDS, "H")
    walk.free("C", "graeffe-batch")
    walk.free("C", "graeffe-O")
    walk.free("C", "graeffe-E")

    product_workspace = product_charge(ELL, ELL, 2 * ELL - 1).points
    walk.alloc("C", "newton-reversed", ELL, "L")
    walk.alloc("C", "newton-reciprocal", ELL, "L")
    walk.alloc("C", "newton-scratch", ELL, "H")
    walk.alloc("C", "newton-transform", product_workspace, "H")
    walk.free("C", "newton-transform")
    walk.free("C", "newton-scratch")
    walk.alloc("C", "quotient-output", ELL, "H")
    walk.alloc("C", "quotient-transform", product_workspace, "H")
    walk.free("C", "quotient-transform")
    walk.free("C", "quotient-output")
    walk.free("C", "newton-reciprocal")
    walk.free("C", "newton-reversed")

    walk.alloc("C", "A-O2", TRUNCATED_POINTS, "L")
    walk.alloc("C", "k1-O1", TRUNCATED_POINTS, "L")
    walk.alloc("C", "A-O1", TRUNCATED_POINTS, "H")
    walk.alloc("C", "batch", BATCH_WORDS, "H")
    # Stage C returns g and R; the other two n' arrays and batch are dead.
    walk.free("C", "batch")
    walk.free("C", "k1-O1")
    walk.free("C", "A-O2")
    # Rename by retaining A-O1 as R in the trace; identity is immaterial.

    # D: node bump arena is not live with apply storage.  Each apply holds the
    # four matrix entries as one packed block and one reused transform buffer.
    for index, step in enumerate(OUTER_STEPS, 1):
        bump = 16 * (1 << step.level) - 256
        walk.alloc("D", f"D{index}-node", bump, "L")
        walk.free("D", f"D{index}-node")
        walk.alloc("D", f"D{index}-matrix", 4 * (step.budget + 1), "L")
        if APPLY_MODE == "block" and step.degree > LMAX:
            walk.alloc("D", f"D{index}-row-a", 4 * BLOCK_LENGTH, "H")
            walk.alloc("D", f"D{index}-row-b", 4 * BLOCK_LENGTH, "H")
            walk.alloc("D", f"D{index}-slot-c", 12 * BLOCK_LENGTH, "L")
            walk.alloc("D", f"D{index}-slot-d", 12 * BLOCK_LENGTH, "L")
            walk.free("D", f"D{index}-slot-d")
            walk.free("D", f"D{index}-slot-c")
            walk.free("D", f"D{index}-row-b")
            walk.free("D", f"D{index}-row-a")
        else:
            walk.alloc("D", f"D{index}-transform", step.apply.points, "L")
            walk.free("D", f"D{index}-transform")
        walk.free("D", f"D{index}-matrix")

    walk.free("D", "root-tables")
    walk.free("D", "A-O1")
    walk.free("D", "g")
    assert not walk.sizes
    assert walk.low.extent == 0 and walk.high.extent == 0
    return walk


ALLOCATOR = memory_walk()
ARENA = ALLOCATOR.peak + POOL_GAP + SLAB_AREA + LATE_SLAB

# Executable/static image from the actual emitted straight-line families:
# four bytes per primitive instruction in four copies of each block body,
# eight-position column bodies, drivers, field routines, and literal data.
BLOCK_BODY_CODE = 4 * 4 * sum(
    block_body(width) + running_chain(width) for width in range(1, 8)
)
COLUMN_BODY_CODE = 4 * 8 * sum(
    (11, 20, 52, 128, 304, 704, 1600)
)
DRIVER_CODE = 4 * (16_384 + 8_192 + 4_096 + 2_048)
FIELD_CODE = 4 * (16_384 + 4_096)
REFERENCE_CODE = 16 * COMPRESSION
ALLOCATOR_CODE = 4 * 4_096
POLYNOMIAL_CONTROL_CODE = 4 * 20_480
STATIC_LITERALS = 212 * 32 + 8_192
CODE_AND_STATIC = (BLOCK_BODY_CODE + COLUMN_BODY_CODE + DRIVER_CODE
                   + FIELD_CODE + REFERENCE_CODE + ALLOCATOR_CODE
                   + POLYNOMIAL_CONTROL_CODE + STATIC_LITERALS)
REGISTER_FILE = (256 + 131) * WORD_BYTES
OFFLINE_WORKING = 16 * WORD_BYTES + 64
STACK = 65_536
MEMORY_BYTES = (ARENA + CODE_AND_STATIC + REGISTER_FILE
                + OFFLINE_WORKING + STACK)

RAW_TIME = (Decimal(N_MAX).ln() - Decimal(COMPRESSION).ln()) / Decimal(2).ln()
TIME_CLAIM = ceil_decimal(RAW_TIME, 5)
RAW_MEMORY = Decimal(MEMORY_BYTES).ln() / Decimal(2).ln()
MEMORY_CLAIM = ceil_decimal(RAW_MEMORY, 5)
SCORE = TIME_CLAIM + max(Decimal(0), MEMORY_CLAIM - Decimal(20))


def validate() -> None:
    assert DEGREE == 5 ** (ROUNDS + 6)
    assert ODD_DEGREE == (DEGREE - 1) // 2
    assert TRUNCATED_POINTS == TRUNCATED_NODES * NODE_WORDS
    assert ELL == VSHIFT + TRUNCATED_POINTS - ODD_DEGREE + 1
    assert COMPRESSION == 216 + 21 * ROUNDS
    assert base_node() == 105_140
    assert len(OUTER_STEPS) == EXPECTED_OUTER_STEPS
    assert exponent_bits() == (EXPECTED_SQUARINGS, EXPECTED_MULTIPLIES)
    assert sum(LEDGER.values()) == N_MAX
    assert ALLOCATOR.peak == max(event.extent_sum for event in ALLOCATOR.events)
    assert MEMORY_BYTES == (ARENA + CODE_AND_STATIC + REGISTER_FILE
                            + OFFLINE_WORKING + STACK)
    assert TIME_CLAIM >= RAW_TIME
    assert MEMORY_CLAIM >= RAW_MEMORY


def comma(value: int) -> str:
    return f"{value:,}"


def main() -> None:
    validate()
    squares, multiplies = exponent_bits()
    print("geometry", {
        "D": DEGREE, "m": ODD_DEGREE, "N": FULL_POINTS,
        "n1": TRUNCATED_POINTS, "ell": ELL,
        "graeffe": GRAEFFE_DEPTH, "squarings": squares,
        "multiplies": multiplies,
    })
    print("machine", {
        "pass_schedule_21": pass_schedule(21),
        "middle_widths": TR_MIDDLE_WIDTHS,
        "register_words": 387,
        "loop8_n1": loop8(TRUNCATED_POINTS),
    })
    print("stage_c_components")
    for name, value in STAGE_C_COMPONENTS.items():
        print(" ", name, value)
    print("stage_c", STAGE_C)
    print("node_fixed_events", NODE_FIXED_EVENTS, sum(NODE_FIXED_EVENTS.values()))
    print("node_bf", {level: node_bf(level) for level in range(7, 22)})
    print("stage_d_outer_steps")
    for index, step in enumerate(OUTER_STEPS, 1):
        print(" ", index, step.degree, step.level, step.budget, step.node,
              step.apply.points, step.apply.total, step.driver, step.total)
    print("stage_d_components", STAGE_D_COMPONENTS)
    print("stage_d", STAGE_D)
    print("ledger", LEDGER)
    print("n_max", N_MAX)
    print("allocator_events", len(ALLOCATOR.events))
    print("stage_peaks", ALLOCATOR.stage_peaks)
    print("pool_high_water", ALLOCATOR.peak)
    print("arena", ARENA)
    print("memory_components", {
        "arena": ARENA, "code_static": CODE_AND_STATIC,
        "register_file": REGISTER_FILE, "offline_working": OFFLINE_WORKING,
        "stack": STACK,
    })
    print("memory_bytes", MEMORY_BYTES)
    print("raw_time", RAW_TIME, "time_claim", TIME_CLAIM)
    print("raw_memory", RAW_MEMORY, "memory_claim", MEMORY_CLAIM)
    print("score", SCORE)


if __name__ == "__main__":
    main()
```
