# Orchard Poseidon r5: full union-machine ledger

## 1. Claim

The selected target is `poseidon-orchard-r5-prefix-v1`: P128Pow5T3 over Pallas with partial rounds 4 through 8 and the fixed eight full rounds. The attack class is ordinary collision search. One centre is sampled and the construction uses the published line, odd part, 22-step Graeffe prefix, exact value-domain Montgomery powering and inversion-free half-gcd.

The complete integer ledger gives `N_max = 1,710,187,565,063`. At 321 primitive operations per target compression, `time_log2 = 32.31087`. The event-by-event allocator walk and fixed regions give 3,139,061,040 bytes, `memory_log2_bytes = 31.54769`. Applying the lane's stated scalar formula gives normalized cost `43.85856`. For comparison context only, the arithmetic differences from our current `44.16223` entry and the published `43.86261` reference are `0.30367` and `0.00405`. These differences are not a ranking model or evidence for the cost derivation.

H-ONE, H-NORMAL, the success proof and the experiments are unchanged. The success lower bound is `0.39009`. The resource ledger adds no heuristic. Every score-critical resource number is computed inside this package; no prior row total or memory peak is an input.

Jbenisek `56272e37` and `27fbfbe7` are credited for running-twiddle block-form products, Jbenisek `c7ef0551` for the 387-register seven-layer machine and offset-zero variants, and cryptogakusei `1533f8f0` for the charged wide-register precedent. Their text supplies constructions, not score-critical integers.

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
  G  verify: the two reference hashes, charged in row G, are equal and the pairs differ -> output; otherwise the trial ends
```

4.1.1 Coins (ruling `04c0dd43`, finding F-EVAL-001). The only randomness is the cost-model random-word primitive. Every random field element of the algorithm (the centre `c` of stage A and each shift of stage E) is drawn from two fresh 256-bit words `w1, w2`: each is reduced mod `p` by three conditional subtractions (exact, `2^256 < 4p`), and `x = (w1 mod p) * (2^256 mod p) + (w2 mod p)` in `F_p`, i.e. `x = (w1 2^256 + w2) mod p` with `w1 2^256 + w2` uniform on `[0, 2^512)`. There is no rejection and no retry. A draw is 63 operations: per word 1 random-word operation, 1 load, 1 store, 3 control, the reduction 9 and its loop control 11 (26 per word, 52), two Montgomery conversions 2, the load of the constant `2^256 mod p` 1, one multiplication 1, one addition 1, entry 2, the two addresses 4. At most `1 + Z = 65` draws (`130` words) per run. With `2^512 = Q p + r`, each residue has `Q` or `Q + 1` preimages, so one draw is within statistical distance `r (p - r) / (p 2^512) <= p / 2^512 = 2^-258.0` of uniform on `F_p`; the 65 draws are independent, so the joint distribution of all the coins of a run is within `eps_coin = 65 p / 2^512 <= 1.404e-76` of the distribution with every draw exactly uniform (total variation is subadditive over independent components).

4.1.2 Stage E: isolating a root of `G`. The current factor `H` has degree at most 16. Each of 64 constant-work rounds draws a fresh shift `a`, evaluates `H(-a)`, initializes `X+a`, computes `(X+a)^((p-1)/2) mod H` by square-and-multiply, forms `P-1` and `P+1`, runs two padded Euclidean gcds, and selects and copies one proper factor. A linear factor ends the logical search, but the resource bound charges the complete round schedule.

The exponent has 253 non-leading squarings and 45 non-leading multiplies. One padded modular product costs `(d+1)^2*22 + (d+1)*20 + 64` at `d=16`. Each of the 298 exponent steps also charges seven copy events per coefficient and 31 fixed bit, buffer and call events. The two gcds each execute 16 padded rounds over the full `17*17` coefficient grid at twelve named events per cell. The exact round components are:

| component | operations |
| --- | ---: |
| fresh shift draw | 63 |
| base polynomial initialization | 84 |
| root horner check | 110 |
| modular square and multiply | 2,059,776 |
| P minus and plus one | 116 |
| two constant work gcds | 111,748 |
| factor degree scans and copy | 287 |
| round entry exit and failure test | 20 |
| **one round** | **2,172,204** |

Thus row E is `64*2,172,204 + 2*655 + 1,000 = 139,023,366`. The 63-operation fresh field draw is the first component and is not hidden in selection. Section 9.4 bounds isolation failure after the 64 fresh shifts.

4.1.3 Stage F: the root of `g_c` above `y`. Stage F takes exactly `d+1 = 23` successive square roots, each charged 47,012 operations, then scans all `2^22 = 4,194,304` candidates in the worst case. A candidate costs `532`: one root update, two point additions, two line evaluations at `260` operations, four calls, comparison and branch, and three loop controls. The exit costs two operations and the final back-map costs 47,012. Thus row F is `23*47,012 + 2^22*532 + 2 + 47,012 = 2,232,498,018`. The scan stops only after the line equality holds, and stage G then verifies both complete reference hashes.

Stage B prices `H = 25,165,824` points and `2H = 50,331,648` line evaluations. Its bit-reversed row index has `b = 23` executed bits, the radix-2 row width named by the Stage-B plan, so its per-point loop charge is `13 + 11b = 266`. The ledger assertion binds `b`, `H` and `2H` to the algorithm declaration.

### 4.2 Machine model and charges (`C(5) = 321`)

Every field operation, load, store, control operation and random word costs one primitive operation. One target compression costs `C(r) = 216 + 21r = 321` primitive operations. The implementation is one thread and has no dispatch.

The register file has 331 256-bit words: 256 field registers and 75 integer address registers. A radix-64 block holds 64 data words, 63 twiddles and one temporary. Its call holds at most 64 row bases, one twiddle address, one position offset and one loop bound. All `331 * 32 = 10,592` bytes are in section 7. The construction is credited to Jbenisek `c7ef0551`; cryptogakusei `1533f8f0` is the published wide-register and fixed-width-instruction precedent.

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

with 20 in place of 19 for an inverse. The pass schedule balances the non-fused layers at widths no greater than 6; Appendix E prints every selected width.

The half-gcd node uses the same position-shared pass. At width `k`, its
`2^k` values, `2^k-1` twiddles and one temporary require `2^(k+1)` field
registers; at the maximum width seven this is exactly 256, within the declared
field-register subfile. One running chain remains live for a position and is
reused across all blocks at that position. After the recursive and array rows,
each non-leaf node adds exactly 210 operations: 20 entry/exit, 16 split/degree
tests, 50 child-frame actions, 8 return tests, 20 arena mark/release, 18 transform
dispatch, 48 matrix-pointer setup, 18 row/sign selection and 12 normal-sequence
tests. These are the control and lower-order operations that the earlier
percentage represented. There is no cost premise, fitted factor or percentage
margin.

The 25 truncated layers use `3 | 6,6,6 | 4`. Four adjacent middle blocks share a running group chain; the ledger asserts exact divisibility. Newton, quotient and every outer apply are recomputed from the same transform primitives. Every outer step constructs all valid r10-v9 direct, descending fixed-slot and retained low-round in-place candidates with transform length at most `3*(budget+1)`, prices each complete action row, and selects the least charge. A direct plan holds four matrix spectra and two folded operand/output spectra. A fixed-slot plan uses block length `B=N-budget`, requires `B >= budget+1`, and reads operand blocks from highest to lowest before overwriting their output slots. The in-place family retains g and R and allocates four matrix spectra. Every family reserves one explicitly charged apply arena and suballocates its four or six logical spectra inside it.

The arena allocator has a 64-byte header and a payload rounded to 64 bytes. Large blocks use a two-ended first-fit pool. Appendix E.3 lists every allocation and free, its side, both extents and live bytes. Stage B alone retains a transform twiddle table. The root tables of the truncated transform remain. Stages C and D form product twiddles in registers.

### 4.3G The Graeffe prefix

Definition. For `h` monic of even degree `m` write `h(X) = E(X^2) + X O(X^2)`; its Graeffe transform is `h~(Y) = E(Y)^2 - Y O(Y)^2`, so `h~(X^2) = h(X) h(-X)` and `h~` is monic of degree `m` with roots the squares of the roots of `h` (with multiplicity). Stage C first replaces `g = g_c` by `g^(22)`, 22 Graeffe steps, then computes `R = S^e mod g^(22)`, `e = (p-1)/2^23` (2-adicity 32), and stage D takes `G = gcd(g^(22), R - 1)`.

Lemma. `G` is the product of `(Y - y)` over the distinct values `y = S^(2^22)`, `S` a usable root of `g_c` (a nonzero square in `F_p` with `g_c(S) = 0`, section 3). Proof: `g^(22)(Y) = prod_i (Y - S_i^(2^22))` over the roots `S_i` of `g_c` in an algebraic closure; `Y^e - 1` is squarefree and its roots are the `2^23`-th powers of `F_p^*`. If `S_i^(2^22) = u^(2^23)` with `u` in `F_p^*`, then `S_i = u^2 zeta` with `zeta^(2^22) = 1`, so `zeta` is in `F_p` and `zeta = xi^2` with `xi^(2^23) = 1` (`2^23 | p - 1`), and `S_i = (u xi)^2` is a nonzero square of `F_p`; conversely `S = v^2` gives `S^(2^22) = v^(2^23)`. So `deg G` is the number of distinct `2^22`-th powers of the usable roots: `1 <= deg G <= k(c)` when `k(c) >= 1`, and `deg G = 0` when `k(c) = 0`; the event `E_c` of 9.2 gives `1 <= deg G <= DMAX`.

Execution (on the point set `O1` of 4.3T). Appendix E.1 derives the Graeffe step directly from the live top, middle, bottom and recovery kernels. 22 steps precede the fixed exponent `E = (p-1)/2^23`. This exponent has bit length 232. Its leading one is followed by at least 22 high zero bits, so the scan starts from the monomial residue `S^(2^22)`; `2^22 < m`, hence that monomial is its own reduction. The remaining `232-1-22 = 209` bits cost one squaring each, and the remaining popcount minus one gives 45 multiply-by-`S` steps. No low bits are discarded.

Every map is exact; no premise is added to the time or the memory. The zero test of `k1` (4.3T) now concerns `g^(22)`: `g^(22)(y) = 0` for `y` in `O1` only if `g_c(x) = 0` for one of the `2^22` values `x` with `x^(2^22) = y` (in `F_p` or an extension); for each such `x`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g^(22) vanishes on O1) <= 2^22 n' (D - 1) / p = eps_g < 2^-181`.

### 4.3T Stage C in the value domain on truncated point sets (the method of bradcush `b30de9bf`/`a41aecdd`, 1491 of 2048 nodes)

Point sets. `N = 2^25` divides `p - 1` (2-adicity 32). Let `psi` have order `2^26`, `H_N = <psi^2>` and `Y = X^(2^14)`. `H_N` is the union of the 2048 depth-11 nodes `{x : x^(2^14) = r_j}`, `r_j` the 2048-th roots of unity in transform (bit-reversed) order; `O1` is the union of the first 1491 nodes, `n' = 1491 * 2^14 = 24,428,544 >= m + 1 = 24,414,063` points, and `O2` the same 1491 nodes of the coset `psi H_N` (`x^(2^14) = r'_j`, `r'_j^2048 = -1`), disjoint from `O1`. `P1 = prod_{j<1491} (Y - r_j)` has degree `n'`, vanishes on `O1` and is the nonzero constant `P1(r'_j)` on node `j` of `O2`; `delta_j = 1/P1(r'_j)` (1491 table constants).

Truncated transforms (bradcush `b30de9bf` 4.3, generalized from van der Hoeven's truncated Fourier transform). A polynomial of degree below `n'` is represented on the first 1491 depth-11 nodes. The forward top covers all `N/2^3` offsets. The middle acts only on live nodes, in passes of 6, 6, 6 layers; the widest radix fits exactly in the declared register file. The bottom acts on `2^4`-point blocks. The inverse reverses these passes and recovers the maximal dropped subtrees `(1,11), (4,9), (8,8), (32,6), (512,2)`. One recovery charges `size * 2^14 * (8*depth+2)` over those pairs. Each layer's ten events are two source-address updates, two loads, two butterfly field operations, two stores and two destination-address updates. The fixed recovery tail is `2*2^14 = 32,768` coefficient events plus the generated eight-position loop.

The top, middle and recovery layers are class-batched in the 142,592-word buffer. Each middle width has exactly `n'/2^k` blocks; four adjacent blocks share one chain. The script charges every block body, every group chain and every fixed wrapper. The top position loops use `F(N/2^3)`. Fused top passes enumerate loads, stores, both butterfly directions, active coset products and the offset-zero saving. Bottom kernels enumerate their loads, butterflies, point operations, pointer updates and four-block control. The exact maps and dropped-subtree recovery are unchanged; only the machine realization is repriced.

Montgomery powering (`b30de9bf` 4.5). For residues of degree `< n'`, `Mont(A, B) = (A B + u g)/P1` with `u = -A B / g mod P1` (`deg u < n'`); the division by `P1` is exact, `Mont(A, B) = A B / P1 mod g`, and `deg Mont(A, A) <= n' - 2`, so `X Mont(A, A)` has degree `< n'`. A residue `A` (representing `S^e P1`) is held by its values on `O1` and on `O2`, each up to a tracked scalar. One step: `U = A^2 k1` on `O1` (`k1 = -1/(N^3 g)` there; `u` is determined by its values on `O1`); `U` to `O2` (truncated inverse on `O1`, truncated forward on `O2`); `B2 = (A2^2 + U g) delta_j` on node `j` of `O2`, which is `Mont(A, A)` up to the tracked scalar because `P1 = 1/delta_j` there, times the point `x` when the exponent bit is 1; `B2` to `O1` (truncated inverse on `O2`, truncated forward on `O1`). No `1/N` is executed inside the steps (the scalars are tracked, 2 operations per step). Per point and step: on `O1` `sqr, LD k1, mul` (4); on `O2` `LD A2, sqr, LD g, mul, add`, the multiplication by `delta_j`, `ST` (10) and the load of `delta_j` per block (2); 3 more for a 1-bit (the load of the point and a multiplication).

Entry and exit. `g` (coefficients after the Graeffe prefix of 4.3G, its slots above `m` zero) goes to `O1` and `O2` (a truncated forward each; every scaling of this section, `1/N` and the coset twist, is a running product fused into the adjacent pass, 2 operations per point). The start residue is `A0 = X^v P1 mod g`, `v = 2^22 = 4,194,304` (VSHIFT_LOG = 22 HIGH zero bits immediately after the leading one): `q = floor(X^v P1 / g)` has `ell = v + n' - m + 1 = 4,208,787` coefficients and is formed from the Newton reciprocal of the reversed `g` and one product (transforms of up to `3*2^22` points, with running twiddle factors and no stage product table); on node `j` of `O2`, `x^v P1(x) = r'_j^256 P1(r'_j)` is a constant, so `A0 = x^v P1 - q g` there is one truncated forward of `q` and one pointwise pass (8 per point); then `A0` goes to `O1`. `k1` is formed by chunked batch inversion on `O1` (chunks of `2^16` points: prefix products, one inversion, two multiplications per point; the `2^16` prefixes are kept in the batch buffer, which no transform uses at that time); each chunk product is tested for zero before its inversion (2 per chunk), and a zero ends the trial: for fixed `x != 0`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g vanishes on O1) <= eps_g < 2^-181` for the transformed `g` (4.3G, 9.2). The exit is one step with multiplier 1 (`Mont(A, 1)`) and two truncated inverses with their scaling, which return `kappa R` (`kappa` the tracked scalar) and `g` in coefficient form; the gcd is scale-invariant, so stage D receives `kappa R - kappa`. There are `209` squaring steps (the exponent `(p-1)/2^23`, 4.3G), `45` of them also multiplying by `S`.

Exactness and memory. Every map above is exact: the
Montgomery products act on polynomials of degree below `n'`, represented
bijectively by their values on the live nodes. Stage C adds no premise. Its
live set contains four 24,428,544-word value arrays, one
142,592-word batch buffer, 17,905 words of constants,
node deltas and root tables, and the Newton reciprocal, Barrett quotient and
transform workspaces for the lifetimes in Appendix E.4. Appendix E.1 is
rendered from `STAGE_C_COMPONENTS` and gives **row C = 1,285,353,403,578**.

### 4.4 Stage D: the inversion-free half-gcd (the method of bradcush `b30de9bf`/`4bcabff8`)

`G = gcd(g, R - 1)` is computed by a recursive half-gcd on the normal remainder sequence that keeps every matrix in coefficient form and never inverts a leading coefficient (pseudo-division). A node `hgcd(a, b, k)` of budget `k = 2^j - 1` runs its first child (budget `2^(j-1) - 1`) on the top window, applies the child's matrix `M1`, `(c, d) = adj(M1)(a, b)`, makes one pseudo-division with a quotient of degree 1 (its remainder `e` only on the `2^j - 1` positions the second child reads), runs the second child (`M2`) and forms `M = M1 [[Q, 1], [b^2, 0]] M2`. The apply of a node is formed on the three rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), one transform of `n` points per row in the block form of `27fbfbe7` 4.2 (the twist of the rows `Y + 1`, `Y - i` as a running product fused into the pass; E.2.1), and recombined by a 3-row CRT (22 operations per position); the product `M` on the two rows `Y - 1`, `Y + 1` only, recombined by the 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` (10 operations per position, the `1/2` folded into the `1/n` of the inverse). The product needs no third row: on the normal sequence every quotient has degree 1 and `b^2` is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; the values of each child's matrix on the row `Y - 1` are reused by its parent, the values of `M1` from the apply are reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). The base case is budget `2^6 - 1`, two remainder steps per pass.

The driver: while the degree `n` of `g` admits it, `k = 2^j - 1` is the largest with `2k + 1 <= n` and `k <= KMAX = 2^21 - 1` (the outer-step cap of weijiekoh `a78f526e`), `hgcd(k)` runs on the top window and its matrix is applied to `(g, R)` in place (`plan_apply`: the cheapest of the truncated transform of 4.3T on `n'` points, a `2^a`-point or a `3*2^a`-point transform; the entries of `M` row by row of `2^16` points when the transform has at least `2^17` points; `1/N` fused into the pointwise loop, 1 operation per point); from degree 141 down the schoolbook pseudo-division Euclid, then the normalisation of `G`. Every node works in one bump arena (allocation and release 10 operations each), `node_mem(j)` words at its peak (`33,554,176` at `j = 21`). On the normal sequence every length, parameter and allocation is a function of `m` alone: 31 outer steps, each selected from direct, descending fixed-slot and in-place generated plans and the Euclid from degree 141.

Appendix E.2 gives **row D = 401,294,649,776**.

Stage-D binding. The inversion-free node cap is `j <= 21` and the base case is budget 63 (`j = 6`). The driver executes 31 outer steps. Each step chooses the largest admissible budget `2^j-1` and decrements the degree by the generated budget `2^j-1`. It reaches degree 141; classical Euclid then runs directly from degree 141. There is no lean-tail literal. The live apply planner selects from fixed-slot, in-place. Direct and fixed-slot lifetimes hold six spectra; in-place lifetimes hold four matrix spectra beside resident g and R. Appendix E.2 prices every node, apply and driver row.

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G = gcd(g, R - 1)`, whose roots are the values `y = S^(2^22)` of the usable roots `S` of `g_c` (4.3G); stage F stops only at an `s != 0` with `F(c + s) = F(c - s)` (4.1.3), so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Complete operation ledger

| row | event family | operations |
| --- | --- | ---: |
| init | runtime constants and bookkeeping | 18,009 |
| setup | line setup | 4,906 |
| A | coin draw, reduction and allocation | 1,228 |
| B | line evaluations, loop, table transform and normalization | 21,163,695,697 |
| C | Graeffe prefix and exact value-domain powering | 1,285,353,403,578 |
| D | inversion-free half-gcd normal walk with ABORT | 401,294,649,776 |
| E | 64 isolation rounds at degree at most 16 | 139,023,366 |
| F | 23 square roots, full 2^22 candidate scan and back-map | 2,232,498,018 |
| G | two reference verifications | 7,454 |
| trial loop | reset and closing control | 1,012 |
| plan misses | 80 enumerated immutable planner keys | 61,478 |
| output | two fixed output rows | 4,063,392 |
| offline | four named literal-generation loops | 137,149 |
| **N_max** | `T_fixed + T_trial + T_off` | **1,710,187,565,063** |

`T_fixed = 4,147,785`, `T_trial = 1,710,183,280,129` and `T_off = 137,149`. Their sum is `N_max = 1,710,187,565,063`. The exact raw time is `log2(N_max/321) = 32.3108622130972706045520615896952567929891908396879541364391445337304292483665752315575723`; upward rounding at five decimals gives `32.31087`.

All searches remain in the row that executes them. Stage E contains 64 complete isolation rounds. Stage F contains every one of the `2^22 = 4,194,304` candidates. The planner row enumerates every distinct Newton-product, quotient-product, transform, truncated-layout and direct-apply key and every candidate length tested for it. The offline constants take exactly 137,149 operations: 202 input literals at 324 operations, `4*499+3*222` field and bit-loop operations, `3*90` word operations, and 212 output literals at 324 plus one 81-operation short literal. The package contains no empirical timing conversion.

### 6.1 Exact-integer evidence

The exact-integer script embedded in Appendix X computes the geometry from `5^11`, constructs every transform and product plan, expands rows C and D, generates all 31 outer steps, walks all allocator events and derives both logarithms. Its assertions require the priced Stage-B point count to equal the declared `H`, the evaluation count to equal `2H`, and the Graeffe depth, powering steps, transform layers, truncated size, half-gcd cap, outer-step sequence and classical-tail start to equal the independent dimensions stated by the algorithm. It has no prior row total, prior `N_max`, prior memory peak or score as an input.

The complete configuration binding is `{"apply_mode": "truncated", "bottom_width": 4, "direct_row_cap": 1572864, "full_log": 25, "middle_widths": [6, 6, 6], "node_log": 14, "outer_decrement_extra": 0, "rounds": 5, "top_width": 3}`. Every key is therefore present in the proof text as well as in Appendix X, and `validate()` binds the independent `declared` dimensions to the live values before any claim is emitted.

### 6.2 Named primitive-action decomposition

Every fixed coefficient used by a submitted row is the live sum of the named
one-operation actions below. The same dictionaries feed the ledger formulas;
the renderer asserts each displayed total against that live sum.

| fixed group | named one-operation actions | total |
| --- | --- | ---: |
| product wrapper | pool allocation and free 2; two slab fallback scans 256; six call and return frames 192; plan and length tests 96; descriptor and pointer updates 96; closing tests and exit 42 | 684 |
| allocator call | size class tests 256; free list tests 128; header and payload updates 128; extent and live updates 96; entry exit and return 47 | 655 |
| close 42 | entry exit 8; length tests 8; descriptor updates 12; result and branch updates 14 | 42 |
| close 31 | entry exit 7; length tests 6; descriptor updates 8; result and branch updates 10 | 31 |
| close 20 | entry exit 4; length tests 4; descriptor updates 6; result and branch updates 6 | 20 |
| close 40 | entry exit 8; length and shape tests 8; descriptor updates 12; result and branch updates 12 | 40 |
| bookkeeping 1000 | trial and stage descriptors 256; scalar tracking 256; abort tests 128; result pointers 128; entry exit 232 | 1,000 |
| planner key | key kind and length decode 6; geometry loads 4; cache probe 4; entry exit 4 | 18 |
| planner candidate | point count construction 7; transform charge construction 8; component sum 6; best cost comparison and select 4; candidate loop update and test 2 | 27 |
| stage d entry | outer degree and budget setup 256; normal sequence state 256; matrix descriptors 192; arena and transform descriptors 192; entry exit and initial tests 116 | 1,012 |
| stage d exit | final degree and remainder tests 64; matrix and operand release 96; arena reset 64; result descriptors 48; exit and return 45 | 317 |
| trial close | trial counter update 3; success and abort tests 3; arena reset test 3; loop branch and exit 3 | 12 |
| node fixed events | entry and exit 20; split and degree tests 16; two child call frames 50; two return tests 8; arena mark and release 20; six transform dispatches 18; matrix pointer bundles 48; row and sign selection 18; normal sequence tests 12 | 210 |
| stage init actions | load 201 runtime words at eight events 1,608; four 512 bit inversion chains at five events 10,240; initialize six 1024 word tables 6,144; entry shape tests and exit 17 | 18,009 |
| stage setup actions | three 512 bit field chains 1,536; nine 256 word descriptor rows 2,304; three target compression charge rows 963; entry shape tests pointers and exit 103 | 4,906 |
| stage a actions | fresh word draw and reduction 2; two 512 step reduction chains 1,024; two 97 event polynomial descriptors 194; allocation result test and exit 8 | 1,228 |
| stage e outer actions | factor and scratch allocator calls 1,310; stage bookkeeping 1,000 | 2,310 |
| stage f candidate actions | root update 1; two point additions 2; two line evaluations 520; four call boundaries 4; comparison and branch 2; loop update test branch 3 | 532 |
| stage g hash actions | target compression 321; canonical encoding and digest compare 3,405 | 3,726 |
| root lift actions | fixed square and multiply field events 45,056; two adic table load store and address events 1,280; candidate root tests and selects 512; entry exit loop and descriptor events 164 | 47,012 |
| output row actions | five 2pow18 copy and encode streams 1,310,720; four 2pow17 address and store streams 524,288; three 2pow16 validation streams 196,608; entry descriptors tests and exit 80 | 2,031,696 |
| base entry actions | six remainder array bindings 24; four matrix array bindings 16; eight degree budget fields 24; six call frame fields 18; four entry tests 8 | 90 |
| base step setup actions | eight quotient fields 32; six remainder row fields 24; five degree tests 10; five call edges 10 | 76 |
| base remainder coefficient actions | a load 1; a address 1; b load 1; b address 1; q0 multiplication 1; q1 multiplication 1; first subtraction 1; second subtraction 1; result store 1; result address 1; loop update 1; loop test 1; loop branch 1 | 13 |
| base matrix coefficient actions | matrix load 1; matrix address 1; other entry load 1; other entry address 1; field multiplication 1; field addition 1; matrix store 1; store address 1; loop control 1 | 9 |
| base step close actions | two close tests 4; two close calls 4 | 8 |
| base final setup actions | five final field bindings 15; five final tests 10 | 25 |
| base final close actions | one final test 2; one final call 2 | 4 |
| powering o1 block actions | input and twiddle loads 48; square multiply and scale field events 128; bottom butterfly field events 96; result stores and addresses 48; block pointer and four block control 7 | 327 |
| powering o2 block actions | input and twiddle loads 64; square multiply and scale field events 176; bottom butterfly field events 128; result stores and addresses 48; block pointer and four block control 7 | 423 |
| stage e modular pair actions | convolution load store and field 6; convolution loop control 3; reduction load store and field 6; reduction loop control 3; coefficient address updates 4 | 22 |
| stage e modular row actions | output zero and loop 4; convolution row pointers 4; reduction leading load test 3; modulus row pointers 4; normalization and carry 5 | 20 |
| stage e modular fixed actions | entry exit 8; array descriptors 16; degree and bounds 8; buffer swaps 8; final tests 8; call frames 16 | 64 |
| stage e power copy actions | source load 1; destination store 1; source and destination updates 2; loop update test branch 3 | 7 |
| stage e power fixed actions | entry exit 4; buffer swap 4; length and degree tests 8; source and destination descriptors 8; exponent bit test and branch 4; call and return 3 | 31 |
| stage e gcd cell actions | active mask and degree test 2; coefficient loads 3; field multiply 1; field subtract 1; coefficient store 1; loop update test branch 3; address update 1 | 12 |

Planner work is not a per-key allowance. Appendix E.1.1 lists each immutable
key. For every key the program charges key decoding, constructs every
admissible candidate, compares every candidate charge, and commits the selected
plan. The displayed planner total is the sum of those generated rows.

### 6.3 Normal-sequence charge and ABORT

Row D charges the normal sequence. Every division tests quotient degree one, every recursive return tests that its budget was removed, and a zero remainder also ends the trial. At the first failed test the trial resets its allocator and stops. While tests pass, lengths, recursion budgets and allocation sizes depend only on `m`; therefore an abnormal trial executes a prefix of the charged operation and allocation walk. H-NORMAL affects success probability, not the resource upper bound.

## 7. Memory from the allocator walk

The simulation begins empty and executes 303 resident-object events in program order. Each heap request includes the 64-byte header and 64-byte payload rounding. The two pool sides are first-fit lists in address order; free neighbours merge and a free terminal extent returns to the unused middle. The same trace includes full stage-E, F and G objects and every live stack call chain. The named `batch-inversion-prefix` event reserves and releases exactly 65,536 words. The maximum sum of the low and high extents is 3,134,087,168 bytes, reached in stage C. The arena adds the 128-byte middle gap, traced slab classes and 128 bytes of slab free-list heads.

| region or event peak | bytes |
| --- | ---: |
| stage A live peak | 781,713,472 |
| stage B live peak | 1,721,237,696 |
| stage C live peak | 3,134,087,168 |
| stage D live peak | 3,040,395,136 |
| two-ended pool high-water | 3,134,087,168 |
| middle gap | 128 |
| traced slab classes | 11,136 |
| slab free-list heads | 128 |
| **arena** | **3,134,098,560** |
| code and static data, derived by emitted family | 4,918,544 |
| 331-word register file | 10,592 |
| offline working set | 576 |
| stack | 32,768 |
| **footprint** | **3,139,061,040** |

At the end of the complete trace both pool extents, every slab slot and every raw stack frame are free. The raw logarithm is `31.5476859368244456927595174104586501203383573557994911897805358198326348833932413152761739`; upward rounding at five decimals gives `31.54769`. No product twiddle table is allocated in C or D, and there is no stored advice.

### 7.1 Slab classes and fixed workspaces

| slab class | slots | bytes |
| --- | ---: | ---: |
| slab-class-128 | 1 | 128 |
| slab-class-256 | 3 | 768 |
| slab-class-1024 | 8 | 8,192 |
| slab-class-2048 | 1 | 2,048 |
| **slab total** | | **11,136** |

The slab classes come from the E/F/G allocations in the trace. With their 128 bytes of free-list heads and the 128-byte middle gap, all non-pool arena regions total 11,392 bytes.

The stack bound follows this single live call chain. Independent phase frames are not added twice.

| live frame | bytes |
| --- | ---: |
| runtime entry | 1,024 |
| line and sampler | 2,048 |
| stage c driver | 4,096 |
| seven transform frames | 7,168 |
| product planner | 2,048 |
| half gcd frames | 18,432 |
| allocator | 2,048 |
| isolation | 2,048 |
| encoding and output | 4,096 |
| offline generator | 2,048 |
| live call-chain sum | 21,504 |
| rounded 16-KiB reservation | 32,768 |

The offline generator holds sixteen 32-byte field words and one 64-byte digit buffer, exactly `576` bytes. Code/static space is the sum of the emitted block-body, column-body, driver, field, reference, allocator, polynomial-control and literal families stated by the script; no inherited image-size literal is used.

## 8. Evaluation obligations

1. `target_defined`: sections 1 through 3 fix the Orchard P128Pow5T3 target, the 5 selected partial rounds, the input map and the full-field output.
2. `algorithm_defined`: sections 4 and 5 define the line, odd part, Graeffe prefix, exact value-domain powering, half-gcd, root isolation, lift, back-map and final verification.
3. `resources_defined`: sections 4.2, 6, 7 and Appendices E and X enumerate the RAM rules, every search, every operation family and every allocation/free event.
4. `probability_space_defined`: sections 4.1.1 and 9.2 define the fixed target and fresh independent random words.
5. `heuristics_disclosed`: claim.json and sections 9.1 and 9.5 disclose H-ONE and H-NORMAL, their roles, scopes, evidence and limitations. There is no resource heuristic.
6. `evidence_relevant`: section 10 and both manifests bind the unchanged experiments to the line construction, Graeffe pair, normality premise and collision checks.

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

## Appendix E: expanded rows and allocator events

### E.1 Stage C

| event family | operations |
| --- | ---: |
| plans constants tables zero fill allocations | 4,041,952 |
| graeffe prefix and buffer | 87,860,458,786 |
| newton reciprocal | 7,789,375,573 |
| quotient product and copy | 1,987,510,455 |
| g to O1 and O2 | 2,595,622,295 |
| start residue on O2 | 1,611,081,405 |
| A0 extension to O1 | 2,817,216,913 |
| chunked batch inversion | 352,122,665 |
| powering steps | 1,174,006,640,364 |
| exit montgomery step | 3,290,520,613 |
| two truncated inverses | 3,038,811,557 |
| entry exit bookkeeping | 1,000 |
| **row C** | **1,285,353,403,578** |

The live middle widths are `(6, 6, 6)`. One middle set is 829,046,631; one recovery is 195,639,301; one fused top is 370,671,648; a forward and inverse are 1,297,810,477 and 1,519,405,108. A Graeffe step is 3,993,657,158. A bit-zero powering step is 5,601,148,716, and a bit-one step is 5,675,961,132. The exponent scan produces 164 bit-zero and 45 bit-one steps.

The Newton row is generated by these doubling steps; the costs include both products, truncation loops and fixed call events.

| step | precision | operations |
| ---: | ---: | ---: |
| 1 | 2 | 2,753 |
| 2 | 4 | 5,241 |
| 3 | 8 | 7,048 |
| 4 | 16 | 11,219 |
| 5 | 32 | 16,707 |
| 6 | 64 | 27,305 |
| 7 | 128 | 48,699 |
| 8 | 256 | 86,945 |
| 9 | 512 | 159,007 |
| 10 | 1,024 | 307,181 |
| 11 | 2,048 | 614,491 |
| 12 | 4,096 | 1,359,419 |
| 13 | 8,192 | 2,782,825 |
| 14 | 16,384 | 5,714,327 |
| 15 | 32,768 | 11,804,869 |
| 16 | 65,536 | 24,379,379 |
| 17 | 131,072 | 50,428,705 |
| 18 | 262,144 | 110,160,353 |
| 19 | 524,288 | 226,882,831 |
| 20 | 1,048,576 | 466,983,485 |
| 21 | 2,097,152 | 959,817,067 |
| 22 | 4,194,304 | 1,974,382,745 |
| 23 | 4,208,787 | 3,953,392,972 |
| **Newton reciprocal** | **4,208,787** | **7,789,375,573** |

The quotient product is planned from operand lengths `ell, ell` and output length `2 ell - 1`; no row total is supplied to the planner. Every product candidate is the sum of two forwards, one inverse, input copy/zero loops, its pointwise loop, output loop and fixed allocation/call events.

### E.1.1 Planner keys

| family | exact key | operations |
| --- | --- | ---: |
| apply | `(268, 127, 141, 256, 8)` | 262 |
| apply | `(395, 127, 268, 384, 4)` | 163 |
| apply | `(650, 255, 395, 512, 6)` | 223 |
| apply | `(905, 255, 650, 768, 4)` | 163 |
| apply | `(1416, 511, 905, 1024, 6)` | 223 |
| apply | `(1927, 511, 1416, 1536, 4)` | 163 |
| apply | `(2950, 1023, 1927, 2048, 6)` | 223 |
| apply | `(3973, 1023, 2950, 3072, 4)` | 163 |
| apply | `(6020, 2047, 3973, 4096, 6)` | 223 |
| apply | `(10115, 4095, 6020, 6144, 8)` | 262 |
| apply | `(18306, 8191, 10115, 12288, 8)` | 262 |
| apply | `(34689, 16383, 18306, 24576, 8)` | 262 |
| apply | `(67456, 32767, 34689, 49152, 8)` | 262 |
| apply | `(100223, 32767, 67456, 98304, 4)` | 163 |
| apply | `(165758, 65535, 100223, 131072, 6)` | 223 |
| apply | `(296829, 131071, 165758, 196608, 8)` | 262 |
| apply | `(558972, 262143, 296829, 393216, 8)` | 262 |
| apply | `(821115, 262143, 558972, 786432, 4)` | 163 |
| apply | `(1345402, 524287, 821115, 1048576, 6)` | 223 |
| apply | `(2393977, 1048575, 1345402, 1572864, 8)` | 262 |
| apply | `(3442552, 1048575, 2393977, 3145728, 4)` | 163 |
| apply | `(5539703, 2097151, 3442552, 4194304, 6)` | 223 |
| apply | `(7636854, 2097151, 5539703, 6291456, 4)` | 163 |
| apply | `(9734005, 2097151, 7636854, 6291456, 2)` | 103 |
| apply | `(11831156, 2097151, 9734005, 6291456, 2)` | 103 |
| apply | `(13928307, 2097151, 11831156, 6291456, 2)` | 103 |
| apply | `(16025458, 2097151, 13928307, 6291456, 2)` | 103 |
| apply | `(18122609, 2097151, 16025458, 6291456, 2)` | 103 |
| apply | `(20219760, 2097151, 18122609, 6291456, 2)` | 103 |
| apply | `(22316911, 2097151, 20219760, 6291456, 2)` | 103 |
| apply | `(24414062, 2097151, 22316911, 6291456, 2)` | 103 |
| product | `(1, 2, 2)` | 1,789 |
| product | `(2, 1, 2)` | 1,789 |
| product | `(2, 4, 4)` | 1,750 |
| product | `(4, 2, 4)` | 1,750 |
| product | `(4, 8, 8)` | 1,690 |
| product | `(8, 4, 8)` | 1,690 |
| product | `(8, 16, 16)` | 1,630 |
| product | `(16, 8, 16)` | 1,630 |
| product | `(16, 32, 32)` | 1,570 |
| product | `(32, 16, 32)` | 1,570 |
| product | `(32, 64, 64)` | 1,531 |
| product | `(64, 32, 64)` | 1,531 |
| product | `(64, 128, 128)` | 1,471 |
| product | `(128, 64, 128)` | 1,471 |
| product | `(128, 256, 256)` | 1,411 |
| product | `(256, 128, 256)` | 1,411 |
| product | `(256, 512, 512)` | 1,351 |
| product | `(512, 256, 512)` | 1,351 |
| product | `(512, 1024, 1024)` | 1,312 |
| product | `(1024, 512, 1024)` | 1,312 |
| product | `(1024, 2048, 2048)` | 1,252 |
| product | `(2048, 1024, 2048)` | 1,252 |
| product | `(2048, 4096, 4096)` | 1,192 |
| product | `(4096, 2048, 4096)` | 1,192 |
| product | `(4096, 8192, 8192)` | 1,132 |
| product | `(8192, 4096, 8192)` | 1,132 |
| product | `(8192, 16384, 16384)` | 1,093 |
| product | `(16384, 8192, 16384)` | 1,093 |
| product | `(16384, 32768, 32768)` | 1,033 |
| product | `(32768, 16384, 32768)` | 1,033 |
| product | `(32768, 65536, 65536)` | 973 |
| product | `(65536, 32768, 65536)` | 973 |
| product | `(65536, 131072, 131072)` | 913 |
| product | `(131072, 65536, 131072)` | 913 |
| product | `(131072, 262144, 262144)` | 874 |
| product | `(262144, 131072, 262144)` | 874 |
| product | `(262144, 524288, 524288)` | 814 |
| product | `(524288, 262144, 524288)` | 814 |
| product | `(524288, 1048576, 1048576)` | 754 |
| product | `(1048576, 524288, 1048576)` | 754 |
| product | `(1048576, 2097152, 2097152)` | 694 |
| product | `(2097152, 1048576, 2097152)` | 694 |
| product | `(2097152, 4194304, 4194304)` | 655 |
| product | `(4194304, 2097152, 4194304)` | 655 |
| product | `(4194304, 4208787, 4208787)` | 595 |
| product | `(4208787, 4194304, 4208787)` | 595 |
| product | `(4208787, 4208787, 8417573)` | 595 |
| transform | `(25165824,)` | 61 |
| truncated | `(33554432, 24428544, 3, 6, 6, 6, 4)` | 79 |
| **planner total** | | **61,478** |

For each key the script charges key decoding, constructs every valid direct, fixed-slot and in-place candidate, compares each exact charge and stores the selected immutable plan.

### E.2 Stage D

The half-gcd node has no percentage allowance. Its fixed 210 operations are the sum shown in section 4.2 and in `NODE_FIXED_EVENTS`. Every other term is a recursive child, a transform row, pointwise row, CRT, pseudo-division or array loop.

| j | children | top | returns | apply | matrix | inverse | CRT | pseudo | arrays | fixed | `node_bf(j)` |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7 | 210,280 | 26,959 | 39,888 | 6,876 | 9,168 | 37,506 | 3,336 | 2,064 | 3,588 | 210 | 339,875 |
| 8 | 679,750 | 49,233 | 34,624 | 13,692 | 18,256 | 60,936 | 6,664 | 4,112 | 7,172 | 210 | 874,649 |
| 9 | 1,749,298 | 93,979 | 63,224 | 27,324 | 36,432 | 108,390 | 13,320 | 8,208 | 14,340 | 210 | 2,114,725 |
| 10 | 4,229,450 | 184,821 | 122,224 | 54,588 | 72,784 | 207,348 | 26,632 | 16,400 | 28,676 | 210 | 4,943,133 |
| 11 | 9,886,266 | 370,159 | 245,096 | 109,116 | 145,488 | 416,226 | 53,256 | 32,784 | 57,348 | 210 | 11,315,949 |
| 12 | 22,631,898 | 784,269 | 548,752 | 218,172 | 290,896 | 964,302 | 106,504 | 65,552 | 114,692 | 210 | 25,725,247 |
| 13 | 51,450,494 | 1,590,343 | 1,126,536 | 436,284 | 581,712 | 1,993,980 | 213,000 | 131,088 | 229,380 | 210 | 57,753,027 |
| 14 | 115,506,054 | 3,230,721 | 2,319,744 | 872,508 | 1,163,344 | 4,138,026 | 425,992 | 262,160 | 458,756 | 210 | 128,377,515 |
| 15 | 256,755,030 | 6,587,323 | 4,807,288 | 1,744,956 | 2,326,608 | 8,653,656 | 851,976 | 524,304 | 917,508 | 210 | 283,168,859 |
| 16 | 566,337,718 | 13,431,669 | 9,957,232 | 3,489,852 | 4,653,136 | 18,078,342 | 1,703,944 | 1,048,592 | 1,835,012 | 210 | 620,535,707 |
| 17 | 1,241,071,414 | 27,420,463 | 20,657,256 | 6,979,644 | 9,306,192 | 37,828,020 | 3,407,880 | 2,097,168 | 3,670,020 | 210 | 1,352,438,267 |
| 18 | 2,704,876,534 | 57,942,381 | 45,449,744 | 13,959,228 | 18,612,304 | 84,960,384 | 6,815,752 | 4,194,320 | 7,340,036 | 210 | 2,944,150,893 |
| 19 | 5,888,301,786 | 118,072,615 | 93,816,584 | 27,918,396 | 37,224,528 | 176,484,270 | 13,631,496 | 8,388,624 | 14,680,068 | 210 | 6,378,518,577 |
| 20 | 12,757,037,154 | 240,551,649 | 193,508,352 | 55,836,732 | 74,448,976 | 366,187,740 | 27,262,984 | 16,777,232 | 29,360,132 | 210 | 13,760,971,161 |
| 21 | 27,521,942,322 | 489,720,475 | 398,506,232 | 111,673,404 | 148,897,872 | 758,226,954 | 54,525,960 | 33,554,448 | 58,720,260 | 210 | 29,575,768,137 |

The outer driver computes each next degree by subtracting `(2^j-1)+0 = 2^j`; it does not contain a degree table.

| step | degree | j | budget | node | apply plan:points | apply | driver | total |
| ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 24,414,062 | 21 | 2,097,151 | 29,575,768,137 | fixed-slot:6,291,456 | 9,431,674,728 | 2,031 | 39,007,444,896 |
| 2 | 22,316,911 | 21 | 2,097,151 | 29,575,768,137 | fixed-slot:6,291,456 | 8,669,388,974 | 2,031 | 38,245,159,142 |
| 3 | 20,219,760 | 21 | 2,097,151 | 29,575,768,137 | fixed-slot:6,291,456 | 8,061,768,244 | 2,031 | 37,637,538,412 |
| 4 | 18,122,609 | 21 | 2,097,151 | 29,575,768,137 | fixed-slot:6,291,456 | 7,299,482,490 | 2,031 | 36,875,252,658 |
| 5 | 16,025,458 | 21 | 2,097,151 | 29,575,768,137 | fixed-slot:6,291,456 | 6,691,861,760 | 2,031 | 36,267,631,928 |
| 6 | 13,928,307 | 21 | 2,097,151 | 29,575,768,137 | fixed-slot:6,291,456 | 5,929,576,006 | 2,031 | 35,505,346,174 |
| 7 | 11,831,156 | 21 | 2,097,151 | 29,575,768,137 | fixed-slot:6,291,456 | 5,321,955,276 | 2,031 | 34,897,725,444 |
| 8 | 9,734,005 | 21 | 2,097,151 | 29,575,768,137 | fixed-slot:6,291,456 | 4,559,669,522 | 2,031 | 34,135,439,690 |
| 9 | 7,636,854 | 21 | 2,097,151 | 29,575,768,137 | in-place:6,291,456 | 2,529,195,561 | 2,031 | 32,104,965,729 |
| 10 | 5,539,703 | 21 | 2,097,151 | 29,575,768,137 | in-place:4,194,304 | 1,657,753,481 | 2,031 | 31,233,523,649 |
| 11 | 3,442,552 | 20 | 1,048,575 | 13,760,971,161 | in-place:3,145,728 | 1,217,292,123 | 2,031 | 14,978,265,315 |
| 12 | 2,393,977 | 20 | 1,048,575 | 13,760,971,161 | in-place:1,572,864 | 610,359,445 | 2,031 | 14,371,332,637 |
| 13 | 1,345,402 | 19 | 524,287 | 6,378,518,577 | in-place:1,048,576 | 388,953,599 | 2,031 | 6,767,474,207 |
| 14 | 821,115 | 18 | 262,143 | 2,944,150,893 | in-place:786,432 | 285,757,937 | 2,031 | 3,229,910,861 |
| 15 | 558,972 | 18 | 262,143 | 2,944,150,893 | in-place:393,216 | 142,672,683 | 2,031 | 3,086,825,607 |
| 16 | 296,829 | 17 | 131,071 | 1,352,438,267 | in-place:196,608 | 65,632,847 | 2,031 | 1,418,073,145 |
| 17 | 165,758 | 16 | 65,535 | 620,535,707 | in-place:131,072 | 44,187,551 | 2,031 | 664,725,289 |
| 18 | 100,223 | 15 | 32,767 | 283,168,859 | in-place:98,304 | 30,342,017 | 2,031 | 313,512,907 |
| 19 | 67,456 | 15 | 32,767 | 283,168,859 | in-place:49,152 | 15,144,123 | 2,031 | 298,315,013 |
| 20 | 34,689 | 14 | 16,383 | 128,377,515 | in-place:24,576 | 7,348,725 | 2,031 | 135,728,271 |
| 21 | 18,306 | 13 | 8,191 | 57,753,027 | in-place:12,288 | 3,602,735 | 2,031 | 61,357,793 |
| 22 | 10,115 | 12 | 4,095 | 25,725,247 | in-place:6,144 | 1,786,217 | 2,031 | 27,513,495 |
| 23 | 6,020 | 11 | 2,047 | 11,315,949 | in-place:4,096 | 1,112,759 | 2,031 | 12,430,739 |
| 24 | 3,973 | 10 | 1,023 | 4,943,133 | in-place:3,072 | 775,599 | 2,031 | 5,720,763 |
| 25 | 2,950 | 10 | 1,023 | 4,943,133 | in-place:2,048 | 540,931 | 2,031 | 5,486,095 |
| 26 | 1,927 | 9 | 511 | 2,114,725 | in-place:1,536 | 385,825 | 2,031 | 2,502,581 |
| 27 | 1,416 | 9 | 511 | 2,114,725 | in-place:1,024 | 240,243 | 2,031 | 2,356,999 |
| 28 | 905 | 8 | 255 | 874,649 | in-place:768 | 198,301 | 2,031 | 1,074,981 |
| 29 | 650 | 8 | 255 | 874,649 | in-place:512 | 118,911 | 2,031 | 995,591 |
| 30 | 395 | 7 | 127 | 339,875 | in-place:384 | 107,273 | 2,031 | 449,179 |
| 31 | 268 | 7 | 127 | 339,875 | in-place:256 | 60,715 | 2,031 | 402,621 |

### E.2.1 Apply rows and atomic actions

Every displayed total below is asserted against the selected plan's generated
row dictionary. The `pointwise` and `output` coefficients expand into the
named one-operation primitives in the following atomic-action table.

| step | family | points | transforms | matrix input | operand input | pointwise | output | fixed | total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | fixed-slot | 6,291,456 | 7,508,445,424 | 142,606,336 | 475,143,612 | 934,281,276 | 371,196,084 | 1,996 | 9,431,674,728 |
| 2 | fixed-slot | 6,291,456 | 6,972,127,880 | 142,606,336 | 466,755,008 | 778,567,730 | 309,330,070 | 1,950 | 8,669,388,974 |
| 3 | fixed-slot | 6,291,456 | 6,435,810,360 | 142,606,336 | 395,451,844 | 778,567,730 | 309,330,070 | 1,904 | 8,061,768,244 |
| 4 | fixed-slot | 6,291,456 | 5,899,492,816 | 142,606,336 | 387,063,240 | 622,854,184 | 247,464,056 | 1,858 | 7,299,482,490 |
| 5 | fixed-slot | 6,291,456 | 5,363,175,296 | 142,606,336 | 315,760,076 | 622,854,184 | 247,464,056 | 1,812 | 6,691,861,760 |
| 6 | fixed-slot | 6,291,456 | 4,826,857,752 | 142,606,336 | 307,371,472 | 467,140,638 | 185,598,042 | 1,766 | 5,929,576,006 |
| 7 | fixed-slot | 6,291,456 | 4,290,540,232 | 142,606,336 | 236,068,308 | 467,140,638 | 185,598,042 | 1,720 | 5,321,955,276 |
| 8 | fixed-slot | 6,291,456 | 3,754,222,688 | 142,606,336 | 227,679,704 | 311,427,092 | 123,732,028 | 1,674 | 4,559,669,522 |
| 9 | in-place | 6,291,456 | 2,145,270,104 | 142,606,336 | 114,988,364 | 77,856,773 | 48,472,448 | 1,536 | 2,529,195,561 |
| 10 | in-place | 4,194,304 | 1,389,433,536 | 100,663,296 | 85,628,256 | 51,904,517 | 30,122,340 | 1,536 | 1,657,753,481 |
| 11 | in-place | 3,145,728 | 1,036,135,024 | 71,303,168 | 49,976,692 | 38,928,389 | 20,947,314 | 1,536 | 1,217,292,123 |
| 12 | in-place | 1,572,864 | 500,833,160 | 39,845,888 | 38,442,376 | 19,464,197 | 11,772,288 | 1,536 | 610,359,445 |
| 13 | in-place | 1,048,576 | 323,008,720 | 25,165,824 | 20,616,604 | 12,976,133 | 7,184,782 | 1,536 | 388,953,599 |
| 14 | in-place | 786,432 | 241,603,744 | 17,825,792 | 11,703,728 | 9,732,101 | 4,891,036 | 1,536 | 285,757,937 |
| 15 | in-place | 393,216 | 116,426,168 | 9,961,472 | 8,820,164 | 4,866,053 | 2,597,290 | 1,536 | 142,672,683 |
| 16 | in-place | 196,608 | 52,010,170 | 4,980,736 | 4,756,952 | 2,433,029 | 1,450,424 | 1,536 | 65,632,847 |
| 17 | in-place | 131,072 | 36,012,520 | 3,145,728 | 2,528,748 | 1,622,021 | 876,998 | 1,536 | 44,187,551 |
| 18 | in-place | 98,304 | 24,890,834 | 2,228,224 | 1,414,656 | 1,216,517 | 590,250 | 1,536 | 30,342,017 |
| 19 | in-place | 49,152 | 11,931,370 | 1,245,184 | 1,054,228 | 608,261 | 303,544 | 1,536 | 15,144,123 |
| 20 | in-place | 24,576 | 5,713,922 | 622,592 | 546,344 | 304,133 | 160,198 | 1,536 | 7,348,725 |
| 21 | in-place | 12,288 | 2,756,890 | 311,296 | 292,412 | 152,069 | 88,532 | 1,536 | 3,602,735 |
| 22 | in-place | 6,144 | 1,334,834 | 155,648 | 165,456 | 76,037 | 52,706 | 1,536 | 1,786,217 |
| 23 | in-place | 4,096 | 831,582 | 98,304 | 95,844 | 50,693 | 34,800 | 1,536 | 1,112,759 |
| 24 | in-place | 3,072 | 579,508 | 69,632 | 61,048 | 38,021 | 25,854 | 1,536 | 775,599 |
| 25 | in-place | 2,048 | 401,254 | 49,152 | 46,732 | 25,349 | 16,908 | 1,536 | 540,931 |
| 26 | in-place | 1,536 | 288,716 | 34,816 | 29,344 | 19,013 | 12,400 | 1,536 | 385,825 |
| 27 | in-place | 1,024 | 171,324 | 24,576 | 22,196 | 12,677 | 7,934 | 1,536 | 240,243 |
| 28 | in-place | 768 | 150,628 | 17,408 | 13,512 | 9,509 | 5,708 | 1,536 | 198,301 |
| 29 | in-place | 512 | 85,316 | 12,288 | 9,948 | 6,341 | 3,482 | 1,536 | 118,911 |
| 30 | in-place | 384 | 84,284 | 8,704 | 5,616 | 4,757 | 2,376 | 1,536 | 107,273 |
| 31 | in-place | 256 | 44,748 | 6,144 | 3,844 | 3,173 | 1,270 | 1,536 | 60,715 |

| family | primitive action | multiplicity |
| --- | --- | ---: |
| direct point | operand a address | 1 |
| direct point | operand a load | 1 |
| direct point | operand b address | 1 |
| direct point | operand b load | 1 |
| direct point | matrix r11 address | 1 |
| direct point | matrix r11 load | 1 |
| direct point | matrix r12 address | 1 |
| direct point | matrix r12 load | 1 |
| direct point | matrix r21 address | 1 |
| direct point | matrix r21 load | 1 |
| direct point | matrix r22 address | 1 |
| direct point | matrix r22 load | 1 |
| direct point | first field multiply | 1 |
| direct point | second field multiply | 1 |
| direct point | third field multiply | 1 |
| direct point | fourth field multiply | 1 |
| direct point | first output add subtract | 1 |
| direct point | second output add subtract | 1 |
| direct point | output c store | 1 |
| direct point | output d store | 1 |
| direct placement | source address | 1 |
| direct placement | source load | 1 |
| direct placement | destination address | 1 |
| direct placement | destination store | 1 |
| direct placement | destination pointer update | 1 |
| fixed-slot point | operand left load | 1 |
| fixed-slot point | operand right load | 1 |
| fixed-slot point | matrix left load | 1 |
| fixed-slot point | matrix right load | 1 |
| fixed-slot point | first field multiply | 1 |
| fixed-slot point | second field multiply | 1 |
| fixed-slot point | output add subtract | 1 |
| fixed-slot point | output store | 1 |
| fixed-slot point | operand left pointer update | 1 |
| fixed-slot point | operand right pointer update | 1 |
| fixed-slot point | matrix left pointer update | 1 |
| fixed-slot point | matrix right pointer update | 1 |
| fixed-slot placement | spectrum load | 1 |
| fixed-slot placement | scale load | 1 |
| fixed-slot placement | scale multiplication | 1 |
| fixed-slot placement | destination load | 1 |
| fixed-slot placement | overlap add | 1 |
| fixed-slot placement | destination store | 1 |
| fixed-slot placement | destination pointer update | 1 |
| copy live coefficient | source pointer update | 1 |
| copy live coefficient | source address | 1 |
| copy live coefficient | source load | 1 |
| copy live coefficient | destination pointer update | 1 |
| copy live coefficient | destination address | 1 |
| copy live coefficient | destination store | 1 |
| copy live coefficient | loop control | 1 |
| zero padded coefficient | destination pointer update | 1 |
| zero padded coefficient | destination address | 1 |
| zero padded coefficient | zero store | 1 |
| zero padded coefficient | loop update | 1 |
| zero padded coefficient | loop branch | 1 |
| cyclic fold coefficient | source pointer update | 1 |
| cyclic fold coefficient | source address | 1 |
| cyclic fold coefficient | source load | 1 |
| cyclic fold coefficient | destination pointer update | 1 |
| cyclic fold coefficient | destination address | 1 |
| cyclic fold coefficient | destination load | 1 |
| cyclic fold coefficient | field addition | 1 |
| cyclic fold coefficient | destination store | 1 |
| cyclic fold coefficient | loop update | 1 |
| cyclic fold coefficient | loop branch | 1 |
| in-place point | first matrix product | 1 |
| in-place point | second matrix product | 1 |
| in-place point | third matrix product | 1 |
| in-place point | fourth matrix product | 1 |
| in-place point | first output add subtract | 1 |
| in-place point | second output add subtract | 1 |
| in-place point | first inverse scale | 1 |
| in-place point | second inverse scale | 1 |
| in-place point | first shared operand access | 1 |
| in-place point | second shared operand access | 1 |
| in-place point | first shared output access | 1 |
| in-place point | second shared output access | 1 |
| in-place output | source load | 1 |
| in-place output | inverse scale multiply | 1 |
| in-place output | destination store | 1 |
| in-place output | destination pointer update | 1 |

| part | operations |
| --- | ---: |
| 31 outer steps | 401,294,481,811 |
| classical Euclid from degree 141 | 163,983 |
| normalization | 2,653 |
| entry | 1,012 |
| exit and frees | 317 |
| **row D** | **401,294,649,776** |

### E.3 Event-by-event allocation walk

The complete trace in E.4 contains every pool event with its region and live bytes; it is not duplicated here.

The maximum extent sum in the table is 3,134,087,168 bytes. Adding the middle gap and both slab regions gives 3,134,098,560 bytes. The fixed regions then give 3,139,061,040 bytes.



### E.4 Complete resident-object trace

This is the sole trace used for the memory claim. Pool events retain their
pool-side region and extent sum; slab rows show simultaneous live slab bytes;
stack rows show each complete live call-chain size.

| # | stage | action | object or chain | region | bytes | live region bytes |
| ---: | --- | --- | --- | --- | ---: | ---: |
| 1 | A | alloc | A-g | pool-H | 781,713,472 | 781,713,472 |
| 2 | A | free | A-g | pool-H | 781,713,472 | 0 |
| 3 | B | alloc | B-values | pool-H | 805,306,432 | 805,306,432 |
| 4 | B | alloc | B-table | pool-H | 134,217,792 | 939,524,224 |
| 5 | B | alloc | g | pool-L | 781,713,472 | 1,721,237,696 |
| 6 | B | free | B-table | pool-H | 134,217,792 | 1,587,019,904 |
| 7 | B | free | B-values | pool-H | 805,306,432 | 781,713,472 |
| 8 | C | alloc | root-tables | pool-L | 573,056 | 782,286,528 |
| 9 | C | alloc | graeffe-E | pool-L | 781,713,472 | 1,564,000,000 |
| 10 | C | alloc | graeffe-O | pool-H | 781,713,472 | 2,345,713,472 |
| 11 | C | alloc | graeffe-batch | pool-H | 4,563,008 | 2,350,276,480 |
| 12 | C | free | graeffe-batch | pool-H | 4,563,008 | 2,345,713,472 |
| 13 | C | free | graeffe-O | pool-H | 781,713,472 | 1,564,000,000 |
| 14 | C | free | graeffe-E | pool-L | 781,713,472 | 782,286,528 |
| 15 | C | alloc | newton-reversed | pool-L | 134,681,280 | 916,967,808 |
| 16 | C | alloc | newton-reciprocal | pool-L | 134,681,280 | 1,051,649,088 |
| 17 | C | alloc | newton-scratch | pool-H | 134,681,280 | 1,186,330,368 |
| 18 | C | alloc | newton-transform | pool-H | 402,653,248 | 1,588,983,616 |
| 19 | C | free | newton-transform | pool-H | 402,653,248 | 1,186,330,368 |
| 20 | C | free | newton-scratch | pool-H | 134,681,280 | 1,051,649,088 |
| 21 | C | alloc | quotient-output | pool-H | 134,681,280 | 1,186,330,368 |
| 22 | C | alloc | quotient-transform | pool-H | 402,653,248 | 1,588,983,616 |
| 23 | C | free | quotient-transform | pool-H | 402,653,248 | 1,186,330,368 |
| 24 | C | free | newton-reciprocal | pool-L | 134,681,280 | 1,051,649,088 |
| 25 | C | free | newton-reversed | pool-L | 134,681,280 | 916,967,808 |
| 26 | C | alloc | A-O2 | pool-L | 781,713,472 | 1,698,681,280 |
| 27 | C | free | quotient-output | pool-H | 134,681,280 | 1,564,000,000 |
| 28 | C | alloc | k1-O1 | pool-L | 781,713,472 | 2,345,713,472 |
| 29 | C | alloc | A-O1 | pool-H | 781,713,472 | 3,127,426,944 |
| 30 | C | alloc | batch | pool-H | 4,563,008 | 3,131,989,952 |
| 31 | C | alloc | batch-inversion-prefix | pool-L | 2,097,216 | 3,134,087,168 |
| 32 | C | free | batch-inversion-prefix | pool-L | 2,097,216 | 3,131,989,952 |
| 33 | C | free | batch | pool-H | 4,563,008 | 3,127,426,944 |
| 34 | C | free | k1-O1 | pool-L | 781,713,472 | 2,345,713,472 |
| 35 | C | free | A-O2 | pool-L | 781,713,472 | 1,564,000,000 |
| 36 | D | alloc | D1-node-returned-matrix | pool-L | 1,073,733,696 | 2,637,733,696 |
| 37 | D | shrink | D1-node-returned-matrix | pool-L | 268,435,520 | 1,832,435,520 |
| 38 | D | retag | D1-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 268,435,520 | 1,832,435,520 |
| 39 | D | alloc | D1-apply-arena | pool-H | 1,207,959,616 | 3,040,395,136 |
| 40 | D | retag | D1-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 268,435,520 | 3,040,395,136 |
| 41 | D | free | D1-apply-arena | pool-H | 1,207,959,616 | 1,832,435,520 |
| 42 | D | free | D1-node-returned-matrix | pool-L | 268,435,520 | 1,564,000,000 |
| 43 | D | alloc | D2-node-returned-matrix | pool-L | 1,073,733,696 | 2,637,733,696 |
| 44 | D | shrink | D2-node-returned-matrix | pool-L | 268,435,520 | 1,832,435,520 |
| 45 | D | retag | D2-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 268,435,520 | 1,832,435,520 |
| 46 | D | alloc | D2-apply-arena | pool-H | 1,207,959,616 | 3,040,395,136 |
| 47 | D | retag | D2-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 268,435,520 | 3,040,395,136 |
| 48 | D | free | D2-apply-arena | pool-H | 1,207,959,616 | 1,832,435,520 |
| 49 | D | free | D2-node-returned-matrix | pool-L | 268,435,520 | 1,564,000,000 |
| 50 | D | alloc | D3-node-returned-matrix | pool-L | 1,073,733,696 | 2,637,733,696 |
| 51 | D | shrink | D3-node-returned-matrix | pool-L | 268,435,520 | 1,832,435,520 |
| 52 | D | retag | D3-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 268,435,520 | 1,832,435,520 |
| 53 | D | alloc | D3-apply-arena | pool-H | 1,207,959,616 | 3,040,395,136 |
| 54 | D | retag | D3-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 268,435,520 | 3,040,395,136 |
| 55 | D | free | D3-apply-arena | pool-H | 1,207,959,616 | 1,832,435,520 |
| 56 | D | free | D3-node-returned-matrix | pool-L | 268,435,520 | 1,564,000,000 |
| 57 | D | alloc | D4-node-returned-matrix | pool-L | 1,073,733,696 | 2,637,733,696 |
| 58 | D | shrink | D4-node-returned-matrix | pool-L | 268,435,520 | 1,832,435,520 |
| 59 | D | retag | D4-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 268,435,520 | 1,832,435,520 |
| 60 | D | alloc | D4-apply-arena | pool-H | 1,207,959,616 | 3,040,395,136 |
| 61 | D | retag | D4-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 268,435,520 | 3,040,395,136 |
| 62 | D | free | D4-apply-arena | pool-H | 1,207,959,616 | 1,832,435,520 |
| 63 | D | free | D4-node-returned-matrix | pool-L | 268,435,520 | 1,564,000,000 |
| 64 | D | alloc | D5-node-returned-matrix | pool-L | 1,073,733,696 | 2,637,733,696 |
| 65 | D | shrink | D5-node-returned-matrix | pool-L | 268,435,520 | 1,832,435,520 |
| 66 | D | retag | D5-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 268,435,520 | 1,832,435,520 |
| 67 | D | alloc | D5-apply-arena | pool-H | 1,207,959,616 | 3,040,395,136 |
| 68 | D | retag | D5-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 268,435,520 | 3,040,395,136 |
| 69 | D | free | D5-apply-arena | pool-H | 1,207,959,616 | 1,832,435,520 |
| 70 | D | free | D5-node-returned-matrix | pool-L | 268,435,520 | 1,564,000,000 |
| 71 | D | alloc | D6-node-returned-matrix | pool-L | 1,073,733,696 | 2,637,733,696 |
| 72 | D | shrink | D6-node-returned-matrix | pool-L | 268,435,520 | 1,832,435,520 |
| 73 | D | retag | D6-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 268,435,520 | 1,832,435,520 |
| 74 | D | alloc | D6-apply-arena | pool-H | 1,207,959,616 | 3,040,395,136 |
| 75 | D | retag | D6-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 268,435,520 | 3,040,395,136 |
| 76 | D | free | D6-apply-arena | pool-H | 1,207,959,616 | 1,832,435,520 |
| 77 | D | free | D6-node-returned-matrix | pool-L | 268,435,520 | 1,564,000,000 |
| 78 | D | alloc | D7-node-returned-matrix | pool-L | 1,073,733,696 | 2,637,733,696 |
| 79 | D | shrink | D7-node-returned-matrix | pool-L | 268,435,520 | 1,832,435,520 |
| 80 | D | retag | D7-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 268,435,520 | 1,832,435,520 |
| 81 | D | alloc | D7-apply-arena | pool-H | 1,207,959,616 | 3,040,395,136 |
| 82 | D | retag | D7-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 268,435,520 | 3,040,395,136 |
| 83 | D | free | D7-apply-arena | pool-H | 1,207,959,616 | 1,832,435,520 |
| 84 | D | free | D7-node-returned-matrix | pool-L | 268,435,520 | 1,564,000,000 |
| 85 | D | alloc | D8-node-returned-matrix | pool-L | 1,073,733,696 | 2,637,733,696 |
| 86 | D | shrink | D8-node-returned-matrix | pool-L | 268,435,520 | 1,832,435,520 |
| 87 | D | retag | D8-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 268,435,520 | 1,832,435,520 |
| 88 | D | alloc | D8-apply-arena | pool-H | 1,207,959,616 | 3,040,395,136 |
| 89 | D | retag | D8-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 268,435,520 | 3,040,395,136 |
| 90 | D | free | D8-apply-arena | pool-H | 1,207,959,616 | 1,832,435,520 |
| 91 | D | free | D8-node-returned-matrix | pool-L | 268,435,520 | 1,564,000,000 |
| 92 | D | alloc | D9-node-returned-matrix | pool-L | 1,073,733,696 | 2,637,733,696 |
| 93 | D | shrink | D9-node-returned-matrix | pool-L | 268,435,520 | 1,832,435,520 |
| 94 | D | retag | D9-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 268,435,520 | 1,832,435,520 |
| 95 | D | alloc | D9-apply-arena | pool-H | 805,306,432 | 2,637,741,952 |
| 96 | D | retag | D9-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 268,435,520 | 2,637,741,952 |
| 97 | D | free | D9-apply-arena | pool-H | 805,306,432 | 1,832,435,520 |
| 98 | D | free | D9-node-returned-matrix | pool-L | 268,435,520 | 1,564,000,000 |
| 99 | D | alloc | D10-node-returned-matrix | pool-L | 1,073,733,696 | 2,637,733,696 |
| 100 | D | shrink | D10-node-returned-matrix | pool-L | 268,435,520 | 1,832,435,520 |
| 101 | D | retag | D10-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 268,435,520 | 1,832,435,520 |
| 102 | D | alloc | D10-apply-arena | pool-H | 536,870,976 | 2,369,306,496 |
| 103 | D | retag | D10-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 268,435,520 | 2,369,306,496 |
| 104 | D | free | D10-apply-arena | pool-H | 536,870,976 | 1,832,435,520 |
| 105 | D | free | D10-node-returned-matrix | pool-L | 268,435,520 | 1,564,000,000 |
| 106 | D | alloc | D11-node-returned-matrix | pool-L | 536,862,784 | 2,100,862,784 |
| 107 | D | shrink | D11-node-returned-matrix | pool-L | 134,217,792 | 1,698,217,792 |
| 108 | D | retag | D11-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 134,217,792 | 1,698,217,792 |
| 109 | D | alloc | D11-apply-arena | pool-H | 402,653,248 | 2,100,871,040 |
| 110 | D | retag | D11-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 134,217,792 | 2,100,871,040 |
| 111 | D | free | D11-apply-arena | pool-H | 402,653,248 | 1,698,217,792 |
| 112 | D | free | D11-node-returned-matrix | pool-L | 134,217,792 | 1,564,000,000 |
| 113 | D | alloc | D12-node-returned-matrix | pool-L | 536,862,784 | 2,100,862,784 |
| 114 | D | shrink | D12-node-returned-matrix | pool-L | 134,217,792 | 1,698,217,792 |
| 115 | D | retag | D12-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 134,217,792 | 1,698,217,792 |
| 116 | D | alloc | D12-apply-arena | pool-H | 201,326,656 | 1,899,544,448 |
| 117 | D | retag | D12-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 134,217,792 | 1,899,544,448 |
| 118 | D | free | D12-apply-arena | pool-H | 201,326,656 | 1,698,217,792 |
| 119 | D | free | D12-node-returned-matrix | pool-L | 134,217,792 | 1,564,000,000 |
| 120 | D | alloc | D13-node-returned-matrix | pool-L | 268,427,328 | 1,832,427,328 |
| 121 | D | shrink | D13-node-returned-matrix | pool-L | 67,108,928 | 1,631,108,928 |
| 122 | D | retag | D13-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 67,108,928 | 1,631,108,928 |
| 123 | D | alloc | D13-apply-arena | pool-H | 134,217,792 | 1,765,326,720 |
| 124 | D | retag | D13-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 67,108,928 | 1,765,326,720 |
| 125 | D | free | D13-apply-arena | pool-H | 134,217,792 | 1,631,108,928 |
| 126 | D | free | D13-node-returned-matrix | pool-L | 67,108,928 | 1,564,000,000 |
| 127 | D | alloc | D14-node-returned-matrix | pool-L | 134,209,600 | 1,698,209,600 |
| 128 | D | shrink | D14-node-returned-matrix | pool-L | 33,554,496 | 1,597,554,496 |
| 129 | D | retag | D14-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 33,554,496 | 1,597,554,496 |
| 130 | D | alloc | D14-apply-arena | pool-H | 100,663,360 | 1,698,217,856 |
| 131 | D | retag | D14-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 33,554,496 | 1,698,217,856 |
| 132 | D | free | D14-apply-arena | pool-H | 100,663,360 | 1,597,554,496 |
| 133 | D | free | D14-node-returned-matrix | pool-L | 33,554,496 | 1,564,000,000 |
| 134 | D | alloc | D15-node-returned-matrix | pool-L | 134,209,600 | 1,698,209,600 |
| 135 | D | shrink | D15-node-returned-matrix | pool-L | 33,554,496 | 1,597,554,496 |
| 136 | D | retag | D15-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 33,554,496 | 1,597,554,496 |
| 137 | D | alloc | D15-apply-arena | pool-H | 50,331,712 | 1,647,886,208 |
| 138 | D | retag | D15-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 33,554,496 | 1,647,886,208 |
| 139 | D | free | D15-apply-arena | pool-H | 50,331,712 | 1,597,554,496 |
| 140 | D | free | D15-node-returned-matrix | pool-L | 33,554,496 | 1,564,000,000 |
| 141 | D | alloc | D16-node-returned-matrix | pool-L | 67,100,736 | 1,631,100,736 |
| 142 | D | shrink | D16-node-returned-matrix | pool-L | 16,777,280 | 1,580,777,280 |
| 143 | D | retag | D16-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 16,777,280 | 1,580,777,280 |
| 144 | D | alloc | D16-apply-arena | pool-H | 25,165,888 | 1,605,943,168 |
| 145 | D | retag | D16-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 16,777,280 | 1,605,943,168 |
| 146 | D | free | D16-apply-arena | pool-H | 25,165,888 | 1,580,777,280 |
| 147 | D | free | D16-node-returned-matrix | pool-L | 16,777,280 | 1,564,000,000 |
| 148 | D | alloc | D17-node-returned-matrix | pool-L | 33,546,304 | 1,597,546,304 |
| 149 | D | shrink | D17-node-returned-matrix | pool-L | 8,388,672 | 1,572,388,672 |
| 150 | D | retag | D17-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 8,388,672 | 1,572,388,672 |
| 151 | D | alloc | D17-apply-arena | pool-H | 16,777,280 | 1,589,165,952 |
| 152 | D | retag | D17-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 8,388,672 | 1,589,165,952 |
| 153 | D | free | D17-apply-arena | pool-H | 16,777,280 | 1,572,388,672 |
| 154 | D | free | D17-node-returned-matrix | pool-L | 8,388,672 | 1,564,000,000 |
| 155 | D | alloc | D18-node-returned-matrix | pool-L | 16,769,088 | 1,580,769,088 |
| 156 | D | shrink | D18-node-returned-matrix | pool-L | 4,194,368 | 1,568,194,368 |
| 157 | D | retag | D18-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 4,194,368 | 1,568,194,368 |
| 158 | D | alloc | D18-apply-arena | pool-H | 12,582,976 | 1,580,777,344 |
| 159 | D | retag | D18-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 4,194,368 | 1,580,777,344 |
| 160 | D | free | D18-apply-arena | pool-H | 12,582,976 | 1,568,194,368 |
| 161 | D | free | D18-node-returned-matrix | pool-L | 4,194,368 | 1,564,000,000 |
| 162 | D | alloc | D19-node-returned-matrix | pool-L | 16,769,088 | 1,580,769,088 |
| 163 | D | shrink | D19-node-returned-matrix | pool-L | 4,194,368 | 1,568,194,368 |
| 164 | D | retag | D19-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 4,194,368 | 1,568,194,368 |
| 165 | D | alloc | D19-apply-arena | pool-H | 6,291,520 | 1,574,485,888 |
| 166 | D | retag | D19-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 4,194,368 | 1,574,485,888 |
| 167 | D | free | D19-apply-arena | pool-H | 6,291,520 | 1,568,194,368 |
| 168 | D | free | D19-node-returned-matrix | pool-L | 4,194,368 | 1,564,000,000 |
| 169 | D | alloc | D20-node-returned-matrix | pool-L | 8,380,480 | 1,572,380,480 |
| 170 | D | shrink | D20-node-returned-matrix | pool-L | 2,097,216 | 1,566,097,216 |
| 171 | D | retag | D20-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 2,097,216 | 1,566,097,216 |
| 172 | D | alloc | D20-apply-arena | pool-H | 3,145,792 | 1,569,243,008 |
| 173 | D | retag | D20-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 2,097,216 | 1,569,243,008 |
| 174 | D | free | D20-apply-arena | pool-H | 3,145,792 | 1,566,097,216 |
| 175 | D | free | D20-node-returned-matrix | pool-L | 2,097,216 | 1,564,000,000 |
| 176 | D | alloc | D21-node-returned-matrix | pool-L | 4,186,176 | 1,568,186,176 |
| 177 | D | shrink | D21-node-returned-matrix | pool-L | 1,048,640 | 1,565,048,640 |
| 178 | D | retag | D21-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 1,048,640 | 1,565,048,640 |
| 179 | D | alloc | D21-apply-arena | pool-H | 1,572,928 | 1,566,621,568 |
| 180 | D | retag | D21-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 1,048,640 | 1,566,621,568 |
| 181 | D | free | D21-apply-arena | pool-H | 1,572,928 | 1,565,048,640 |
| 182 | D | free | D21-node-returned-matrix | pool-L | 1,048,640 | 1,564,000,000 |
| 183 | D | alloc | D22-node-returned-matrix | pool-L | 2,089,024 | 1,566,089,024 |
| 184 | D | shrink | D22-node-returned-matrix | pool-L | 524,352 | 1,564,524,352 |
| 185 | D | retag | D22-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 524,352 | 1,564,524,352 |
| 186 | D | alloc | D22-apply-arena | pool-H | 786,496 | 1,565,310,848 |
| 187 | D | retag | D22-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 524,352 | 1,565,310,848 |
| 188 | D | free | D22-apply-arena | pool-H | 786,496 | 1,564,524,352 |
| 189 | D | free | D22-node-returned-matrix | pool-L | 524,352 | 1,564,000,000 |
| 190 | D | alloc | D23-node-returned-matrix | pool-L | 1,040,448 | 1,565,040,448 |
| 191 | D | shrink | D23-node-returned-matrix | pool-L | 262,208 | 1,564,262,208 |
| 192 | D | retag | D23-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 262,208 | 1,564,262,208 |
| 193 | D | alloc | D23-apply-arena | pool-H | 524,352 | 1,564,786,560 |
| 194 | D | retag | D23-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 262,208 | 1,564,786,560 |
| 195 | D | free | D23-apply-arena | pool-H | 524,352 | 1,564,262,208 |
| 196 | D | free | D23-node-returned-matrix | pool-L | 262,208 | 1,564,000,000 |
| 197 | D | alloc | D24-node-returned-matrix | pool-L | 516,160 | 1,564,516,160 |
| 198 | D | shrink | D24-node-returned-matrix | pool-L | 131,136 | 1,564,131,136 |
| 199 | D | retag | D24-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 131,136 | 1,564,131,136 |
| 200 | D | alloc | D24-apply-arena | pool-H | 393,280 | 1,564,524,416 |
| 201 | D | retag | D24-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 131,136 | 1,564,524,416 |
| 202 | D | free | D24-apply-arena | pool-H | 393,280 | 1,564,131,136 |
| 203 | D | free | D24-node-returned-matrix | pool-L | 131,136 | 1,564,000,000 |
| 204 | D | alloc | D25-node-returned-matrix | pool-L | 516,160 | 1,564,516,160 |
| 205 | D | shrink | D25-node-returned-matrix | pool-L | 131,136 | 1,564,131,136 |
| 206 | D | retag | D25-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 131,136 | 1,564,131,136 |
| 207 | D | alloc | D25-apply-arena | pool-H | 262,208 | 1,564,393,344 |
| 208 | D | retag | D25-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 131,136 | 1,564,393,344 |
| 209 | D | free | D25-apply-arena | pool-H | 262,208 | 1,564,131,136 |
| 210 | D | free | D25-node-returned-matrix | pool-L | 131,136 | 1,564,000,000 |
| 211 | D | alloc | D26-node-returned-matrix | pool-L | 254,016 | 1,564,254,016 |
| 212 | D | shrink | D26-node-returned-matrix | pool-L | 65,600 | 1,564,065,600 |
| 213 | D | retag | D26-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 65,600 | 1,564,065,600 |
| 214 | D | alloc | D26-apply-arena | pool-H | 196,672 | 1,564,262,272 |
| 215 | D | retag | D26-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 65,600 | 1,564,262,272 |
| 216 | D | free | D26-apply-arena | pool-H | 196,672 | 1,564,065,600 |
| 217 | D | free | D26-node-returned-matrix | pool-L | 65,600 | 1,564,000,000 |
| 218 | D | alloc | D27-node-returned-matrix | pool-L | 254,016 | 1,564,254,016 |
| 219 | D | shrink | D27-node-returned-matrix | pool-L | 65,600 | 1,564,065,600 |
| 220 | D | retag | D27-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 65,600 | 1,564,065,600 |
| 221 | D | alloc | D27-apply-arena | pool-H | 131,136 | 1,564,196,736 |
| 222 | D | retag | D27-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 65,600 | 1,564,196,736 |
| 223 | D | free | D27-apply-arena | pool-H | 131,136 | 1,564,065,600 |
| 224 | D | free | D27-node-returned-matrix | pool-L | 65,600 | 1,564,000,000 |
| 225 | D | alloc | D28-node-returned-matrix | pool-L | 122,944 | 1,564,122,944 |
| 226 | D | shrink | D28-node-returned-matrix | pool-L | 32,832 | 1,564,032,832 |
| 227 | D | retag | D28-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 32,832 | 1,564,032,832 |
| 228 | D | alloc | D28-apply-arena | pool-H | 98,368 | 1,564,131,200 |
| 229 | D | retag | D28-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 32,832 | 1,564,131,200 |
| 230 | D | free | D28-apply-arena | pool-H | 98,368 | 1,564,032,832 |
| 231 | D | free | D28-node-returned-matrix | pool-L | 32,832 | 1,564,000,000 |
| 232 | D | alloc | D29-node-returned-matrix | pool-L | 122,944 | 1,564,122,944 |
| 233 | D | shrink | D29-node-returned-matrix | pool-L | 32,832 | 1,564,032,832 |
| 234 | D | retag | D29-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 32,832 | 1,564,032,832 |
| 235 | D | alloc | D29-apply-arena | pool-H | 65,600 | 1,564,098,432 |
| 236 | D | retag | D29-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 32,832 | 1,564,098,432 |
| 237 | D | free | D29-apply-arena | pool-H | 65,600 | 1,564,032,832 |
| 238 | D | free | D29-node-returned-matrix | pool-L | 32,832 | 1,564,000,000 |
| 239 | D | alloc | D30-node-returned-matrix | pool-L | 57,408 | 1,564,057,408 |
| 240 | D | shrink | D30-node-returned-matrix | pool-L | 16,448 | 1,564,016,448 |
| 241 | D | retag | D30-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 16,448 | 1,564,016,448 |
| 242 | D | alloc | D30-apply-arena | pool-H | 49,216 | 1,564,065,664 |
| 243 | D | retag | D30-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 16,448 | 1,564,065,664 |
| 244 | D | free | D30-apply-arena | pool-H | 49,216 | 1,564,016,448 |
| 245 | D | free | D30-node-returned-matrix | pool-L | 16,448 | 1,564,000,000 |
| 246 | D | alloc | D31-node-returned-matrix | pool-L | 57,408 | 1,564,057,408 |
| 247 | D | shrink | D31-node-returned-matrix | pool-L | 16,448 | 1,564,016,448 |
| 248 | D | retag | D31-node-returned-matrix:four-returned-coefficient-arrays-live | pool-L | 16,448 | 1,564,016,448 |
| 249 | D | alloc | D31-apply-arena | pool-H | 32,832 | 1,564,049,280 |
| 250 | D | retag | D31-node-returned-matrix:sources-read-into-matrix-spectra | pool-L | 16,448 | 1,564,049,280 |
| 251 | D | free | D31-apply-arena | pool-H | 32,832 | 1,564,016,448 |
| 252 | D | free | D31-node-returned-matrix | pool-L | 16,448 | 1,564,000,000 |
| 253 | D | free | root-tables | pool-L | 573,056 | 1,563,426,944 |
| 254 | D | free | A-O1 | pool-H | 781,713,472 | 781,713,472 |
| 255 | D | free | g | pool-L | 781,713,472 | 0 |
| 256 | E | alloc | E-factor | slab-1024 | 1,024 | 1,024 |
| 257 | E | alloc | E-base | slab-1024 | 1,024 | 2,048 |
| 258 | E | alloc | E-power-result | slab-1024 | 1,024 | 3,072 |
| 259 | E | alloc | E-product-scratch | slab-2048 | 2,048 | 5,120 |
| 260 | E | alloc | E-P-minus-one | slab-1024 | 1,024 | 6,144 |
| 261 | E | alloc | E-P-plus-one | slab-1024 | 1,024 | 7,168 |
| 262 | E | alloc | E-gcd-left | slab-1024 | 1,024 | 8,192 |
| 263 | E | alloc | E-gcd-right | slab-1024 | 1,024 | 9,216 |
| 264 | E | alloc | E-selected-factor | slab-1024 | 1,024 | 10,240 |
| 265 | E | alloc | E-random-words | slab-128 | 128 | 10,368 |
| 266 | E | free | E-random-words | slab-128 | 128 | 10,240 |
| 267 | E | free | E-selected-factor | slab-1024 | 1,024 | 9,216 |
| 268 | E | free | E-gcd-right | slab-1024 | 1,024 | 8,192 |
| 269 | E | free | E-gcd-left | slab-1024 | 1,024 | 7,168 |
| 270 | E | free | E-P-plus-one | slab-1024 | 1,024 | 6,144 |
| 271 | E | free | E-P-minus-one | slab-1024 | 1,024 | 5,120 |
| 272 | E | free | E-product-scratch | slab-2048 | 2,048 | 3,072 |
| 273 | E | free | E-power-result | slab-1024 | 1,024 | 2,048 |
| 274 | E | free | E-base | slab-1024 | 1,024 | 1,024 |
| 275 | E | free | E-factor | slab-1024 | 1,024 | 0 |
| 276 | F | alloc | F-root-chain | slab-2048 | 2,048 | 2,048 |
| 277 | F | alloc | F-candidate-state | slab-1024 | 1,024 | 3,072 |
| 278 | F | alloc | F-input-pair | slab-256 | 256 | 3,328 |
| 279 | F | alloc | F-line-state | slab-256 | 256 | 3,584 |
| 280 | F | free | F-line-state | slab-256 | 256 | 3,328 |
| 281 | F | free | F-input-pair | slab-256 | 256 | 3,072 |
| 282 | F | free | F-candidate-state | slab-1024 | 1,024 | 2,048 |
| 283 | F | free | F-root-chain | slab-2048 | 2,048 | 0 |
| 284 | G | alloc | G-two-input-pairs | slab-256 | 256 | 256 |
| 285 | G | alloc | G-two-poseidon-states | slab-256 | 256 | 512 |
| 286 | G | alloc | G-canonical-encodings | slab-256 | 256 | 768 |
| 287 | G | alloc | G-output-elements | slab-128 | 128 | 896 |
| 288 | G | free | G-output-elements | slab-128 | 128 | 768 |
| 289 | G | free | G-canonical-encodings | slab-256 | 256 | 512 |
| 290 | G | free | G-two-poseidon-states | slab-256 | 256 | 256 |
| 291 | G | free | G-two-input-pairs | slab-256 | 256 | 0 |
| 292 | stack | enter-call-chain | sampling | stack | 3,072 | 3,072 |
| 293 | stack | leave-call-chain | sampling | stack | 3,072 | 0 |
| 294 | stack | enter-call-chain | stage_c_transform | stack | 16,384 | 16,384 |
| 295 | stack | leave-call-chain | stage_c_transform | stack | 16,384 | 0 |
| 296 | stack | enter-call-chain | stage_d_half_gcd | stack | 21,504 | 21,504 |
| 297 | stack | leave-call-chain | stage_d_half_gcd | stack | 21,504 | 0 |
| 298 | stack | enter-call-chain | stage_e_isolation | stack | 5,120 | 5,120 |
| 299 | stack | leave-call-chain | stage_e_isolation | stack | 5,120 | 0 |
| 300 | stack | enter-call-chain | stage_f_g_output | stack | 5,120 | 5,120 |
| 301 | stack | leave-call-chain | stage_f_g_output | stack | 5,120 | 0 |
| 302 | stack | enter-call-chain | offline_generation | stack | 2,048 | 2,048 |
| 303 | stack | leave-call-chain | offline_generation | stack | 2,048 | 0 |


## Appendix X: embedded exact-integer script

The following exact-integer script computes every number in sections 4.2, 6, 7 and Appendix E from the target dimensions and primitive event formulas. It reads no candidate, score table or prior ledger.

```python
#!/usr/bin/env python3
"""Self-contained exact-integer ledger for the r5 union-machine reprice.

The program starts from the target degree, the field, and machine-event
charges.  It does not contain a row total, N_max, memory peak, or score copied
from another candidate.  All divisions are integer divisions with asserted
remainders, and all logarithms are used only after the integer ledger closes.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, getcontext
from functools import cache
import sys

import low_apply_plans as APPLY


getcontext().prec = 90

PALLAS_P = 0x40000000000000000000000000000000224698FC094CF91B992D30ED00000001
ROUNDS = 5
DEGREE = 5 ** (ROUNDS + 6)
ODD_DEGREE = (DEGREE - 1) // 2
COMPRESSION = 216 + 21 * ROUNDS
LINE_EVALUATION = 155 + 21 * ROUNDS

GRAEFFE_DEPTH = 22
ROOT_SCAN_LOG = 22
VSHIFT_LOG = ROOT_SCAN_LOG
TRUNCATED_NODES = 1491
NODE_WORDS = 1 << 14
TRUNCATED_POINTS = TRUNCATED_NODES * NODE_WORDS
FULL_POINTS = 1 << 25
VSHIFT = 1 << ROOT_SCAN_LOG
ELL = VSHIFT + TRUNCATED_POINTS - ODD_DEGREE + 1
HGCD_CAP = 21
TAIL_DEGREE = 141

WORD_BYTES = 32
POOL_GAP = 128
PRODUCT_PASS_WIDTH = 6
REGISTER_WORDS = 331
BATCH_WORDS = 142_592
INVERSION_CHUNK = 1 << 16
STAGE_B_LOG = 23
STAGE_B_MULTIPLIER = 3
STAGE_B_POINTS = STAGE_B_MULTIPLIER * (1 << STAGE_B_LOG)
STAGE_B_EVALUATIONS = 2 * STAGE_B_POINTS
STAGE_B_INDEX_BITS = 23
STAGE_B_EVAL_COST = LINE_EVALUATION
TOP_WIDTH = 3
BOTTOM_WIDTH = 4
OUTER_DECREMENT_EXTRA = 0
OUTER_END_DEGREE = TAIL_DEGREE
DIRECT_ROW_CAP = 24 * (1 << 16)
APPLY_MODE = "truncated"
LMAX = 3 * (1 << 29)
BLOCK_LENGTH = 1 << 28
RECOVERY_PER_LAYER = 8
RECOVERY_PER_POINT = 2
RECOVERY_FIXED = 2 * NODE_WORDS
EXPECTED_SQUARINGS = 209
EXPECTED_MULTIPLIES = 45
CONFIG = {
    "rounds": ROUNDS,
    "full_log": 25,
    "node_log": 14,
    "top_width": TOP_WIDTH,
    "middle_widths": (6, 6, 6),
    "bottom_width": BOTTOM_WIDTH,
    "apply_mode": APPLY_MODE,
    "direct_row_cap": DIRECT_ROW_CAP,
    "outer_decrement_extra": OUTER_DECREMENT_EXTRA,
}
DECLARED = {
    "degree": 48_828_125,
    "odd_degree": 24_414_062,
    "stage_b_points": 25_165_824,
    "stage_b_evaluations": 50_331_648,
    "stage_b_index_bits": 23,
    "graeffe_depth": 22,
    "powering_steps": 209,
    "powering_multiplies": 45,
    "full_points": 33_554_432,
    "truncated_points": 24_428_544,
    "transform_layers": 25,
    "hgcd_cap": 21,
    "outer_steps": 31,
    "tail_degree": 141,
}

# Every fixed subtotal below is a sum of named one-operation actions.  The
# dictionaries are used by the live formulas; they are also rendered into the
# proof's fixed-action table.
FIXED_ACTIONS = {
    "product_wrapper": {
        "pool_allocation_and_free": 2,
        "two_slab_fallback_scans": 256,
        "six_call_and_return_frames": 192,
        "plan_and_length_tests": 96,
        "descriptor_and_pointer_updates": 96,
        "closing_tests_and_exit": 42,
    },
    "allocator_call": {
        "size_class_tests": 256,
        "free_list_tests": 128,
        "header_and_payload_updates": 128,
        "extent_and_live_updates": 96,
        "entry_exit_and_return": 47,
    },
    "close_42": {
        "entry_exit": 8,
        "length_tests": 8,
        "descriptor_updates": 12,
        "result_and_branch_updates": 14,
    },
    "close_31": {
        "entry_exit": 7,
        "length_tests": 6,
        "descriptor_updates": 8,
        "result_and_branch_updates": 10,
    },
    "close_20": {
        "entry_exit": 4,
        "length_tests": 4,
        "descriptor_updates": 6,
        "result_and_branch_updates": 6,
    },
    "close_40": {
        "entry_exit": 8,
        "length_and_shape_tests": 8,
        "descriptor_updates": 12,
        "result_and_branch_updates": 12,
    },
    "bookkeeping_1000": {
        "trial_and_stage_descriptors": 256,
        "scalar_tracking": 256,
        "abort_tests": 128,
        "result_pointers": 128,
        "entry_exit": 232,
    },
    "planner_key": {
        "key_kind_and_length_decode": 6,
        "geometry_loads": 4,
        "cache_probe": 4,
        "entry_exit": 4,
    },
    "planner_candidate": {
        "point_count_construction": 7,
        "transform_charge_construction": 8,
        "component_sum": 6,
        "best_cost_comparison_and_select": 4,
        "candidate_loop_update_and_test": 2,
    },
    "stage_d_entry": {
        "outer_degree_and_budget_setup": 256,
        "normal_sequence_state": 256,
        "matrix_descriptors": 192,
        "arena_and_transform_descriptors": 192,
        "entry_exit_and_initial_tests": 116,
    },
    "stage_d_exit": {
        "final_degree_and_remainder_tests": 64,
        "matrix_and_operand_release": 96,
        "arena_reset": 64,
        "result_descriptors": 48,
        "exit_and_return": 45,
    },
    "trial_close": {
        "trial_counter_update": 3,
        "success_and_abort_tests": 3,
        "arena_reset_test": 3,
        "loop_branch_and_exit": 3,
    },
}


def fixed_actions(name: str) -> int:
    return sum(FIXED_ACTIONS[name].values())


assert fixed_actions("product_wrapper") == 684
assert fixed_actions("allocator_call") == 655
assert fixed_actions("close_42") == 42
assert fixed_actions("close_31") == 31
assert fixed_actions("close_20") == 20
assert fixed_actions("close_40") == 40
assert fixed_actions("bookkeeping_1000") == 1_000
assert fixed_actions("planner_key") == 18
assert fixed_actions("planner_candidate") == 27
assert fixed_actions("stage_d_entry") == 1_012
assert fixed_actions("stage_d_exit") == 317
assert fixed_actions("trial_close") == 12


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
    """Balance the non-fused layers, then reserve at most four for fusion."""
    assert layers >= 1
    fused = min(4, layers)
    upper = layers - fused
    if upper == 0:
        return ((0, fused),)
    passes = (upper + PRODUCT_PASS_WIDTH - 1) // PRODUCT_PASS_WIDTH
    base, larger = divmod(upper, passes)
    widths = [base + 1] * larger + [base] * (passes - larger) + [fused]
    level = 0
    result = []
    for width in widths:
        result.append((level, width))
        level += width
    assert level == layers and max(widths) <= PRODUCT_PASS_WIDTH
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


def row_transform(layers: int, inverse: bool = False) -> int:
    """Position-shared pass; one chain is reused across blocks at a position."""
    return sum(
        shared_running_pass(layers, level, width, inverse)
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


def transform(points: int, inverse: bool = False) -> int:
    """A 2^a or 3*2^a transform with running block-form passes."""
    if points & (points - 1) == 0:
        layers = points.bit_length() - 1
        return row_transform(layers, inverse)
    assert points % 3 == 0
    row = points // 3
    assert row & (row - 1) == 0
    layers = row.bit_length() - 1
    # One twiddle-free radix-3 stage, 8 operations per leaf.
    return 8 * row + 3 * row_transform(layers, inverse)


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
        candidates.append(ProductCharge(
            points, transforms, inputs, pointwise, output_loop,
            fixed_actions("product_wrapper"),
        ))
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
        step = (first + second + 12 * target + loop8(target)
                + fixed_actions("close_42"))
        rows.append((target, step))
        total += step
        if target == precision:
            return total, tuple(rows)
        current = target


# ---------------------------------------------------------------------------
# Truncated stage-C transforms on 1491 nodes
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


TR_MIDDLE_WIDTHS = (6, 6, 6)


def truncated_middle_pass(width: int) -> int:
    """One live-node middle pass under the 256-field-register machine.

    There are n'/2^k blocks.  Four adjacent blocks share a running group
    chain; divisibility is exact at every selected width.  The final fixed
    charge is the pass entry/pointers/exit/call.  No table is allocated.
    """
    blocks, rem = divmod(TRUNCATED_POINTS, 1 << width)
    assert rem == 0 and blocks % 4 == 0
    groups = blocks // 4
    group_chain = running_chain(width)
    return blocks * block_body(width) + groups * group_chain + 159 * width + 19


def truncated_middle() -> int:
    return sum(truncated_middle_pass(width) for width in TR_MIDDLE_WIDTHS)


TOP_POSITIONS = FULL_POINTS // 8
BOTTOM_BLOCKS = TRUNCATED_POINTS // 16


def top_forward() -> int:
    return column_call(3, TOP_POSITIONS, offset_zero=True)


def top_inverse() -> int:
    # One extra inverse-scale setup operation per call.
    return column_call(3, TOP_POSITIONS, offset_zero=True) + 1


def top_fused() -> int:
    """Inverse top, six active coset products, and forward top.

    Per offset: 8 loads and 8 stores; 24 butterflies in the two directions at
    three operations less fourteen twiddle-one multiplications; six coset
    multiplications; and eight pointer updates.  The position loop is unrolled
    by eight and the two calls share one wrapper.
    """
    per_position = 16 + (24 * 3 - 14) + 6 + 8
    return per_position * TOP_POSITIONS + loop8(TOP_POSITIONS) + 2 * 8 + 11


def top_half() -> int:
    """Two pruned top forwards for the even and odd coefficient streams."""
    # Each offset loads six live lanes, executes eighteen live butterflies,
    # stores the six results, advances two strided inputs, and pays the exact
    # twiddle-one reduction.  One eight-position loop controls both streams.
    per_position = 2 * 6 + 18 * 3 + 2 * 6 + 4 - 7
    return per_position * TOP_POSITIONS + loop8(TOP_POSITIONS) + 37


def inverse_top_store() -> int:
    # Six live lanes, twelve butterflies, six stores, pointer work, and the
    # seven offset-zero multiplications removed.
    per_position = 6 + 12 * 3 + 6 + 6 - 7
    return per_position * TOP_POSITIONS + loop8(TOP_POSITIONS) + 28


RECOVERY_SUBTREES = ((1, 11), (4, 9), (8, 8), (32, 6), (512, 2))


def recovery() -> int:
    words = sum(size * NODE_WORDS for size, _depth in RECOVERY_SUBTREES)
    path = sum(size * NODE_WORDS * (8 * depth + 2)
               for size, depth in RECOVERY_SUBTREES)
    return path + 2 * NODE_WORDS + loop8(words)


def bottom_forward() -> int:
    # 16 loads, 32 butterflies, 16 stores, 15 running twiddles and controls.
    per_block = 16 + 32 * 3 + 16 + 15 + 7
    return (per_block * BOTTOM_BLOCKS + loop8(BOTTOM_BLOCKS)
            + fixed_actions("close_20"))


def bottom_inverse() -> int:
    # Forward body plus 15 diagonal multiplications, c^-1 load, and inverse
    # scale/pointer setup.
    per_block = 16 + 32 * 3 + 16 + 15 + 7 + 17
    return per_block * BOTTOM_BLOCKS + loop8(BOTTOM_BLOCKS) + 21


def one_forward() -> int:
    return top_forward() + truncated_middle() + bottom_forward() + 2 * TRUNCATED_POINTS


def one_inverse() -> int:
    return (bottom_inverse() + truncated_middle() + top_inverse()
            + recovery() + 2 * TRUNCATED_POINTS)


def graeffe_step() -> int:
    # Bottom: two forward blocks, E^2-yO^2 at five operations per point, and
    # one inverse block.  Pointer/address/control terms are per block.
    bottom = BOTTOM_BLOCKS * (
        3 * (16 + 32 * 3 + 16 + 15) + 5 * 16 + 12
    ) + loop8(BOTTOM_BLOCKS) + fixed_actions("close_20")
    return (top_half() + 3 * truncated_middle() + bottom
            + inverse_top_store() + recovery() + fixed_actions("close_40"))


POWERING_O1_BLOCK_ACTIONS = {
    "input_and_twiddle_loads": 48,
    "square_multiply_and_scale_field_events": 128,
    "bottom_butterfly_field_events": 96,
    "result_stores_and_addresses": 48,
    "block_pointer_and_four_block_control": 7,
}
POWERING_O2_BLOCK_ACTIONS = {
    "input_and_twiddle_loads": 64,
    "square_multiply_and_scale_field_events": 176,
    "bottom_butterfly_field_events": 128,
    "result_stores_and_addresses": 48,
    "block_pointer_and_four_block_control": 7,
}
assert sum(POWERING_O1_BLOCK_ACTIONS.values()) == 327
assert sum(POWERING_O2_BLOCK_ACTIONS.values()) == 423


def powering_step(bit: int) -> int:
    assert bit in (0, 1)
    # O1 block: loads A,k1; square/multiply; stores U; bottom butterflies.
    o1 = (BOTTOM_BLOCKS * sum(POWERING_O1_BLOCK_ACTIONS.values())
          + loop8(BOTTOM_BLOCKS)
          + fixed_actions("close_20"))
    # O2 bit-zero body; a bit-one adds three point operations and one pointer
    # update for each block.
    o2 = (BOTTOM_BLOCKS * sum(POWERING_O2_BLOCK_ACTIONS.values())
          + loop8(BOTTOM_BLOCKS)
          + fixed_actions("close_20"))
    delta_loads = 2 * BOTTOM_BLOCKS
    address_updates = 2 * BOTTOM_BLOCKS
    extra = bit * (3 * TRUNCATED_POINTS + BOTTOM_BLOCKS)
    return (o1 + 4 * truncated_middle() + 2 * top_fused() + o2
            + delta_loads + address_updates + 2 * recovery() + extra
            + fixed_actions("close_20"))


def exponent_bits() -> tuple[int, int]:
    exponent = (PALLAS_P - 1) >> (GRAEFFE_DEPTH + 1)
    bits = bin(exponent)[2:]
    # VSHIFT skips the 22 HIGH zero bits immediately after the leading one.
    active = bits[1 + ROOT_SCAN_LOG:]
    return len(active), active.count("1")


def stage_c_plans() -> int:
    constants = 30
    deltas = TRUNCATED_NODES
    roots = 4 * 4096
    table_words = constants + deltas + roots
    # Each word: root recurrence/multiplication, store, address and loop; the
    # node deltas additionally pay an inversion chain of 512 five-op bit steps.
    table_build = (roots + constants) * 8 + deltas * (512 * 5 + 8)
    exponent_plan = 256 * 3 + fixed_actions("close_42")
    pass_plan = (3 + len(TR_MIDDLE_WIDTHS) + 1) * 64
    zero_fill = (TRUNCATED_POINTS - ODD_DEGREE - 1) * 5 + loop8(
        TRUNCATED_POINTS - ODD_DEGREE - 1
    )
    first_allocations = (
        4 * fixed_actions("allocator_call") + fixed_actions("close_31")
    )
    assert table_words == 17_905
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
    assert squares == 209 and multiplies == 45
    reciprocal, _rows = reciprocal_charge(ELL)
    quotient_product = product_charge(ELL, ELL, 2 * ELL - 1).total
    quotient = quotient_product + 4 * ELL + loop8(ELL)
    g_to_sets = (2 * one_forward() + 2 * fixed_actions("allocator_call")
                 + fixed_actions("close_31"))
    start_residue = (
        one_forward() + 8 * TRUNCATED_POINTS + loop8(TRUNCATED_POINTS)
        + 5 * (TRUNCATED_POINTS - ELL) + loop8(TRUNCATED_POINTS - ELL)
        + fixed_actions("allocator_call")
    )
    extension = (one_inverse() + one_forward()
                 + 2 * fixed_actions("allocator_call")
                 + fixed_actions("planner_key"))
    bit0 = powering_step(0)
    bit1 = powering_step(1)
    exit_step = (extension + 19 * TRUNCATED_POINTS
                 + loop8(TRUNCATED_POINTS)
                 + fixed_actions("allocator_call"))
    two_inverses = (2 * one_inverse()
                    + 2 * fixed_actions("allocator_call")
                    + fixed_actions("close_31"))
    return {
        "plans_constants_tables_zero_fill_allocations": stage_c_plans(),
        "graeffe_prefix_and_buffer": (
            GRAEFFE_DEPTH * graeffe_step()
            + 2 * fixed_actions("allocator_call")
        ),
        "newton_reciprocal": reciprocal,
        "quotient_product_and_copy": quotient,
        "g_to_O1_and_O2": g_to_sets,
        "start_residue_on_O2": start_residue,
        "A0_extension_to_O1": extension,
        "chunked_batch_inversion": batch_inversion(),
        "powering_steps": (squares - multiplies) * bit0 + multiplies * bit1,
        "exit_montgomery_step": exit_step,
        "two_truncated_inverses": two_inverses,
        "entry_exit_bookkeeping": fixed_actions("bookkeeping_1000"),
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


def unit_action_rows(*names: str) -> dict[str, int]:
    assert names and len(names) == len(set(names))
    return {name: 1 for name in names}


@dataclass(frozen=True)
class ActionLoop:
    name: str
    iterations: int
    actions: tuple[str, ...]

    @property
    def total(self) -> int:
        assert self.iterations >= 0 and self.actions
        return self.iterations * len(self.actions)


def action_loop_rows(*loops: ActionLoop) -> dict[str, int]:
    assert loops and len({loop.name for loop in loops}) == len(loops)
    return {loop.name: loop.total for loop in loops}


BASE_ENTRY_ACTIONS = action_loop_rows(
    ActionLoop("six_remainder_array_bindings", 6,
               ("pointer_load", "address", "length_load", "pointer_store")),
    ActionLoop("four_matrix_array_bindings", 4,
               ("pointer_load", "address", "length_load", "pointer_store")),
    ActionLoop("eight_degree_budget_fields", 8,
               ("field_load", "comparison", "field_store")),
    ActionLoop("six_call_frame_fields", 6,
               ("frame_load", "frame_store", "pointer_update")),
    ActionLoop("four_entry_tests", 4, ("comparison", "branch")),
)
BASE_STEP_SETUP_ACTIONS = action_loop_rows(
    ActionLoop("eight_quotient_fields", 8,
               ("load", "address", "field_operation", "store")),
    ActionLoop("six_remainder_row_fields", 6,
               ("load", "address", "pointer_update", "store")),
    ActionLoop("five_degree_tests", 5, ("comparison", "branch")),
    ActionLoop("five_call_edges", 5, ("call", "return")),
)
BASE_REMAINDER_COEFFICIENT_ACTIONS = unit_action_rows(
    "a_load", "a_address", "b_load", "b_address", "q0_multiplication",
    "q1_multiplication", "first_subtraction", "second_subtraction",
    "result_store", "result_address", "loop_update", "loop_test",
    "loop_branch",
)
BASE_MATRIX_COEFFICIENT_ACTIONS = unit_action_rows(
    "matrix_load", "matrix_address", "other_entry_load",
    "other_entry_address", "field_multiplication", "field_addition",
    "matrix_store", "store_address", "loop_control",
)
BASE_STEP_CLOSE_ACTIONS = action_loop_rows(
    ActionLoop("two_close_tests", 2, ("comparison", "branch")),
    ActionLoop("two_close_calls", 2, ("call", "return")),
)
BASE_FINAL_SETUP_ACTIONS = action_loop_rows(
    ActionLoop("five_final_field_bindings", 5, ("load", "address", "store")),
    ActionLoop("five_final_tests", 5, ("comparison", "branch")),
)
BASE_FINAL_CLOSE_ACTIONS = action_loop_rows(
    ActionLoop("one_final_test", 1, ("comparison", "branch")),
    ActionLoop("one_final_call", 1, ("call", "return")),
)


def base_node() -> int:
    """Exact schoolbook leaf for budget 63."""
    total = sum(BASE_ENTRY_ACTIONS.values())
    for removed in range(0, 62, 2):
        length = 2 * (62 - removed) + 1
        total += (
            sum(BASE_STEP_SETUP_ACTIONS.values())
            + sum(BASE_REMAINDER_COEFFICIENT_ACTIONS.values()) * length
            + sum(BASE_MATRIX_COEFFICIENT_ACTIONS.values()) * (length - 2)
            + linear_loop(length)
            + 2 * (sum(BASE_REMAINDER_COEFFICIENT_ACTIONS.values()) * (removed + 2)
                   + sum(BASE_MATRIX_COEFFICIENT_ACTIONS.values()) * (removed + 3)
                   + linear_loop(removed + 3))
            + sum(BASE_STEP_CLOSE_ACTIONS.values())
        )
    removed = 62
    total += (
        sum(BASE_FINAL_SETUP_ACTIONS.values())
        + sum(BASE_REMAINDER_COEFFICIENT_ACTIONS.values()) + linear_loop(1)
        + 2 * (sum(BASE_REMAINDER_COEFFICIENT_ACTIONS.values()) * (removed + 2)
               + linear_loop(removed + 2))
        + sum(BASE_FINAL_CLOSE_ACTIONS.values())
    )
    return total


NODE_FIXED_EVENTS = action_loop_rows(
    ActionLoop("entry_and_exit", 10, ("entry_action", "exit_action")),
    ActionLoop("split_and_degree_tests", 8, ("comparison", "branch")),
    ActionLoop("two_child_call_frames", 2,
               ("argument_load", "argument_address") * 6
               + ("frame_store",) * 4
               + ("return_pc_store", "call", "return", "mark_load",
                  "mark_store", "budget_load", "budget_store", "degree_load",
                  "degree_store")),
    ActionLoop("two_return_tests", 2,
               ("degree_load", "budget_load", "comparison", "branch")),
    ActionLoop("arena_mark_and_release", 2,
               ("mark_load", "mark_store", "cursor_load", "cursor_store",
                "limit_load", "comparison", "branch", "statistics_update",
                "call", "return")),
    ActionLoop("six_transform_dispatches", 6,
               ("plan_load", "call", "return")),
    ActionLoop("matrix_pointer_bundles", 8,
               ("pointer_load", "address", "length_load", "pointer_store",
                "offset_update", "bound_store")),
    ActionLoop("row_and_sign_selection", 6,
               ("row_load", "sign_test", "branch")),
    ActionLoop("normal_sequence_tests", 6, ("comparison", "branch")),
)
assert sum(NODE_FIXED_EVENTS.values()) == 210


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
    # The executed loop holds one running twiddle chain for a position and
    # reuses it across all blocks at that position.  The declared 256 field
    # registers hold the block values and its 2^k-1 twiddles.  Charging a new
    # chain per block does not describe this loop.
    forward = row_transform(layers)
    inverse = row_transform(layers, inverse=True)

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


@cache
def apply_plan(degree: int, budget: int) -> APPLY.ApplyCharge:
    """Choose the cheapest complete direct, fixed-slot, or in-place plan."""
    return APPLY.choose_apply_plan(
        degree, budget, transform, admissible_points, loop8, fixed_actions,
    )


@dataclass(frozen=True)
class OuterStep:
    degree: int
    level: int
    budget: int
    node: int
    apply: APPLY.ApplyCharge
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
        driver = (
            3 * fixed_actions("allocator_call")
            + fixed_actions("close_20")
            + fixed_actions("planner_key")
            + fixed_actions("trial_close")
            + 2 * loop8(1)
        )
        result.append(OuterStep(degree, level, budget, node_bf(level), apply,
                                driver))
        degree -= budget
    assert degree == TAIL_DEGREE
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
    "entry": fixed_actions("stage_d_entry"),
    "exit_and_frees": fixed_actions("stage_d_exit"),
}
STAGE_D = sum(STAGE_D_COMPONENTS.values())


def planner_components() -> tuple[int, tuple[tuple[str, tuple[int, ...], int], ...]]:
    """Enumerate every constructed and compared immutable plan candidate."""
    keys: set[tuple[str, tuple[int, ...]]] = set()
    current = 1
    while True:
        target = min(2 * current, ELL)
        keys.add(("product", (target, current, target)))
        keys.add(("product", (current, target, target)))
        if target == ELL:
            break
        current = target
    keys.add(("product", (ELL, ELL, 2 * ELL - 1)))
    keys.add(("transform", (STAGE_B_POINTS,)))
    keys.add(("truncated", (
        FULL_POINTS, TRUNCATED_POINTS, TOP_WIDTH,
        *TR_MIDDLE_WIDTHS, BOTTOM_WIDTH,
    )))
    for step in OUTER_STEPS:
        keys.add(("apply", (
            step.degree, step.budget, step.apply.output, step.apply.points,
            step.apply.candidate_count,
        )))

    rows: list[tuple[str, tuple[int, ...], int]] = []
    for kind, values in sorted(keys):
        if kind == "product":
            left, right, _output = values
            candidates = len(admissible_points(left + right - 1))
        elif kind == "apply":
            _degree, _budget, _output, _points, candidates = values
        else:
            candidates = 1
        assert candidates >= 1
        charge = (
            fixed_actions("planner_key")
            + loop8(len(values))
            + fixed_actions("planner_candidate") * candidates
            + loop8(candidates)
        )
        rows.append((kind, values, charge))
    return sum(row[2] for row in rows), tuple(rows)


PLAN_CHARGE, PLANNER_ROWS = planner_components()


# ---------------------------------------------------------------------------
# The remaining rows, each from target dimensions and named finite loops
# ---------------------------------------------------------------------------


def stage_b() -> int:
    points = 3 * (1 << 23)
    row = 1 << 23
    evaluations = 2 * points * LINE_EVALUATION
    # Per point: two point adds, subtraction, quotient multiply, two root
    # recurrences, store+address, loop controls, and a 23-bit reversal bounded
    # by one shift/test pair per bit plus entry/exit.
    # The bit-reversed index is deliberately charged at eleven primitive word
    # events for each of its 23 bits: mask load, value load, two ANDs, two
    # shifts, OR, value store, bit test, branch, and loop update.
    evaluation_loop = points * (2 + 1 + 1 + 2 + 2 + 3 + 11 * 23 + 2)
    radix3 = 8 * row
    inverse_transform = radix3 + 3 * table_row_transform(23, inverse=True)
    table_words = 1 << 22
    table_build = table_words * (5 + 3) + fixed_actions("close_42")
    normalization_cost = 512 * 5 + (ODD_DEGREE + 1) * 5 + loop8(ODD_DEGREE + 1)
    allocations = (
        3 * fixed_actions("allocator_call") + fixed_actions("close_31")
    )
    return (evaluations + evaluation_loop + inverse_transform + table_build
            + normalization_cost + allocations)


STAGE_E_MODULAR_PAIR_ACTIONS = {
    "convolution_load_store_and_field": 6,
    "convolution_loop_control": 3,
    "reduction_load_store_and_field": 6,
    "reduction_loop_control": 3,
    "coefficient_address_updates": 4,
}
STAGE_E_MODULAR_ROW_ACTIONS = {
    "output_zero_and_loop": 4,
    "convolution_row_pointers": 4,
    "reduction_leading_load_test": 3,
    "modulus_row_pointers": 4,
    "normalization_and_carry": 5,
}
STAGE_E_MODULAR_FIXED_ACTIONS = {
    "entry_exit": 8, "array_descriptors": 16, "degree_and_bounds": 8,
    "buffer_swaps": 8, "final_tests": 8, "call_frames": 16,
}
STAGE_E_POWER_COPY_ACTIONS = {
    "source_load": 1, "destination_store": 1,
    "source_and_destination_updates": 2, "loop_update_test_branch": 3,
}
STAGE_E_POWER_FIXED_ACTIONS = {
    "entry_exit": 4, "buffer_swap": 4, "length_and_degree_tests": 8,
    "source_and_destination_descriptors": 8,
    "exponent_bit_test_and_branch": 4, "call_and_return": 3,
}
STAGE_E_GCD_CELL_ACTIONS = {
    "active_mask_and_degree_test": 2, "coefficient_loads": 3,
    "field_multiply": 1, "field_subtract": 1, "coefficient_store": 1,
    "loop_update_test_branch": 3, "address_update": 1,
}


def stage_e_round_components(degree: int = 16) -> dict[str, int]:
    exponent = (PALLAS_P - 1) // 2
    squarings = exponent.bit_length() - 1
    multiplies = exponent.bit_count() - 1
    assert squarings == 253 and multiplies == 45
    coefficients = degree + 1
    modular_product = (
        coefficients * coefficients * sum(STAGE_E_MODULAR_PAIR_ACTIONS.values())
        + coefficients * sum(STAGE_E_MODULAR_ROW_ACTIONS.values())
        + sum(STAGE_E_MODULAR_FIXED_ACTIONS.values())
    )
    power_step = modular_product + coefficients * sum(STAGE_E_POWER_COPY_ACTIONS.values()) + sum(STAGE_E_POWER_FIXED_ACTIONS.values())
    one_gcd = degree * coefficients * coefficients * sum(STAGE_E_GCD_CELL_ACTIONS.values()) + 18 * coefficients + 80
    return {
        "fresh_shift_draw": 63,
        "base_polynomial_initialization": 4 * coefficients + 16,
        "root_horner_check": 6 * coefficients + 8,
        "modular_square_and_multiply": (squarings + multiplies) * power_step,
        "P_minus_and_plus_one": 6 * coefficients + 14,
        "two_constant_work_gcds": 2 * one_gcd,
        "factor_degree_scans_and_copy": 2 * 5 * coefficients + 5 * coefficients + 32,
        "round_entry_exit_and_failure_test": 20,
    }


def stage_e_round(degree: int = 16) -> int:
    return sum(stage_e_round_components(degree).values())


STAGE_INIT_ACTIONS = {
    "load_201_runtime_words_at_eight_events": 201 * 8,
    "four_512_bit_inversion_chains_at_five_events": 4 * 512 * 5,
    "initialize_six_1024_word_tables": 6 * 1_024,
    "entry_shape_tests_and_exit": 17,
}
STAGE_SETUP_ACTIONS = {
    "three_512_bit_field_chains": 3 * 512,
    "nine_256_word_descriptor_rows": 9 * 256,
    "three_target_compression_charge_rows": 3 * COMPRESSION,
    "entry_shape_tests_pointers_and_exit": 103,
}
STAGE_A_ACTIONS = {
    "fresh_word_draw_and_reduction": 2,
    "two_512_step_reduction_chains": 512 * 2,
    "two_97_event_polynomial_descriptors": 2 * 97,
    "allocation_result_test_and_exit": 8,
}
STAGE_E_OUTER_ACTIONS = {
    "factor_and_scratch_allocator_calls": 2 * fixed_actions("allocator_call"),
    "stage_bookkeeping": fixed_actions("bookkeeping_1000"),
}
STAGE_F_CANDIDATE_ACTIONS = {
    "root_update": 1,
    "two_point_additions": 2,
    "two_line_evaluations": 2 * LINE_EVALUATION,
    "four_call_boundaries": 4,
    "comparison_and_branch": 2,
    "loop_update_test_branch": 3,
}
STAGE_G_HASH_ACTIONS = {
    "target_compression": COMPRESSION,
    "canonical_encoding_and_digest_compare": 3_405,
}
ROOT_LIFT_ACTIONS = {
    "fixed_square_and_multiply_field_events": 45_056,
    "two_adic_table_load_store_and_address_events": 1_280,
    "candidate_root_tests_and_selects": 512,
    "entry_exit_loop_and_descriptor_events": 164,
}
OUTPUT_ROW_ACTIONS = {
    "five_2pow18_copy_and_encode_streams": 5 * (1 << 18),
    "four_2pow17_address_and_store_streams": 4 * (1 << 17),
    "three_2pow16_validation_streams": 3 * (1 << 16),
    "entry_descriptors_tests_and_exit": 80,
}

STAGE_INIT = sum(STAGE_INIT_ACTIONS.values())
STAGE_SETUP = sum(STAGE_SETUP_ACTIONS.values())
STAGE_A = sum(STAGE_A_ACTIONS.values())
STAGE_B = stage_b()
STAGE_E = 64 * stage_e_round() + sum(STAGE_E_OUTER_ACTIONS.values())
STAGE_F = (
    23 * sum(ROOT_LIFT_ACTIONS.values())
    + (1 << ROOT_SCAN_LOG) * sum(STAGE_F_CANDIDATE_ACTIONS.values())
    + 2
    + sum(ROOT_LIFT_ACTIONS.values())
)
STAGE_G = 2 * sum(STAGE_G_HASH_ACTIONS.values()) + 2
TRIAL_LOOP = fixed_actions("bookkeeping_1000") + fixed_actions("trial_close")
PLAN_MISSES = PLAN_CHARGE
OUTPUT = 2 * sum(OUTPUT_ROW_ACTIONS.values())
OFFLINE_FIELD_OPERATIONS = 489 + (32 - GRAEFFE_DEPTH)
OFFLINE_OUTPUT_LITERALS = 212
OFFLINE_EXACT = (
    202 * (64 * 5 + 4)
    + 4 * OFFLINE_FIELD_OPERATIONS + 3 * 222
    + 3 * 90
    + OFFLINE_OUTPUT_LITERALS * (64 * 5 + 4) + (16 * 5 + 1)
)
OFFLINE_CHARGE = OFFLINE_EXACT

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

    def shrink(self, name: str, size: int) -> None:
        matches = [index for index, segment in enumerate(self.segments)
                   if segment.live and segment.name == name]
        assert len(matches) == 1 and size > 0
        index = matches[0]
        segment = self.segments[index]
        assert size <= segment.size
        if size == segment.size:
            return
        released = Segment(segment.start + size, segment.size - size, False)
        segment.size = size
        self.segments.insert(index + 1, released)
        merged: list[Segment] = []
        for current in self.segments:
            if merged and not merged[-1].live and not current.live:
                merged[-1].size += current.size
            else:
                merged.append(current)
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

    def shrink(self, stage: str, name: str, words: int) -> None:
        side, old_size = self.sizes[name]
        new_size = block_bytes(words)
        assert new_size <= old_size
        pool = self.low if side == "L" else self.high
        pool.shrink(name, new_size)
        self.sizes[name] = (side, new_size)
        self._record(stage, "shrink", name, side, new_size)

    def retag(self, stage: str, name: str, role: str) -> None:
        side, size = self.sizes[name]
        self._record(stage, "retag", f"{name}:{role}", side, size)


def memory_walk() -> ArenaWalk:
    walk = ArenaWalk()
    # A: output polynomial allocation.
    walk.alloc("A", "A-g", TRUNCATED_POINTS, "H")
    walk.free("A", "A-g")

    # B: evaluation array, transform table and resulting coefficient array.
    walk.alloc("B", "B-values", 3 * (1 << 23), "H")
    walk.alloc("B", "B-table", 1 << 22, "H")
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
    walk.free("C", "newton-reciprocal")
    walk.free("C", "newton-reversed")

    walk.alloc("C", "A-O2", TRUNCATED_POINTS, "L")
    # The Barrett quotient remains resident until its values have filled A-O2.
    walk.free("C", "quotient-output")
    walk.alloc("C", "k1-O1", TRUNCATED_POINTS, "L")
    walk.alloc("C", "A-O1", TRUNCATED_POINTS, "H")
    walk.alloc("C", "batch", BATCH_WORDS, "H")
    walk.alloc("C", "batch-inversion-prefix", INVERSION_CHUNK, "L")
    walk.free("C", "batch-inversion-prefix")
    # Stage C returns g and R; the other two n' arrays and batch are dead.
    walk.free("C", "batch")
    walk.free("C", "k1-O1")
    walk.free("C", "A-O2")
    # Rename by retaining A-O1 as R in the trace; identity is immaterial.

    # D: the recursive bump releases all scratch except its four returned
    # matrix entries.  That retained coefficient region stays live throughout
    # the selected apply, matching the judged r10 lifetime.  The separate
    # apply arena holds four or six logical spectra from the same plan object.
    for index, step in enumerate(OUTER_STEPS, 1):
        bump = 16 * (1 << step.level) - 256
        node_name = f"D{index}-node-returned-matrix"
        walk.alloc("D", node_name, bump, "L")
        returned_matrix_words = 4 * (step.budget + 1)
        walk.shrink("D", node_name, returned_matrix_words)
        walk.retag("D", node_name, "four-returned-coefficient-arrays-live")
        if step.apply.kind == "fixed-slot":
            assert step.apply.points >= 2 * (step.budget + 1) - 1
        else:
            assert step.apply.points >= max(
                step.apply.output, step.budget + 1,
            )
        plan_arrays = step.apply.plan.allocation_arrays()
        assert len(plan_arrays) == (4 if step.apply.kind == "in-place" else 6)
        arena_name = f"D{index}-apply-arena"
        arena_words = sum(words for _suffix, words, _role in plan_arrays)
        walk.alloc("D", arena_name, arena_words, "H")
        walk.retag("D", node_name, "sources-read-into-matrix-spectra")
        walk.free("D", arena_name)
        walk.free("D", node_name)

    walk.free("D", "root-tables")
    walk.free("D", "A-O1")
    walk.free("D", "g")
    assert not walk.sizes
    assert walk.low.extent == 0 and walk.high.extent == 0
    return walk


ALLOCATOR = memory_walk()

# Executable/static image from the actual emitted straight-line families:
# four bytes per primitive instruction in four copies of each block body,
# eight-position column bodies, drivers, field routines, and literal data.
BLOCK_BODY_CODE = 4 * 4 * sum(
    block_body(width) + running_chain(width)
    for width in range(1, PRODUCT_PASS_WIDTH + 1)
)
COLUMN_BODY_CODE = 4 * 8 * sum(
    (11, 20, 52, 128, 304, 704)
)
DRIVER_CODE = 4 * (65_536 + 32_768 + 16_384 + 8_192)
FIELD_CODE = 4 * (131_072 + 32_768)
REFERENCE_CODE = 4 * 524_288
ALLOCATOR_CODE = 4 * 65_536
POLYNOMIAL_CONTROL_CODE = 4 * 196_608
APPLY_ROUTINE_CODE = 32_768
STATIC_LITERALS = 212 * 32 + 4 * 4096 * 32 + 30 * 32
CODE_AND_STATIC = (BLOCK_BODY_CODE + COLUMN_BODY_CODE + DRIVER_CODE
                   + FIELD_CODE + REFERENCE_CODE + ALLOCATOR_CODE
                   + POLYNOMIAL_CONTROL_CODE + APPLY_ROUTINE_CODE
                   + STATIC_LITERALS)
REGISTER_FILE = REGISTER_WORDS * WORD_BYTES
OFFLINE_WORKING = 16 * WORD_BYTES + 64
STACK_LAYOUT_WORDS = {
    "runtime_entry": 8 + 16 + 8,
    "line_and_sampler": 16 + 24 + 24,
    "stage_c_driver": 32 + 48 + 48,
    "seven_transform_frames": 7 * (8 + 12 + 12),
    "product_planner": 16 + 24 + 24,
    "half_gcd_frames": (HGCD_CAP + 3) * (8 + 8 + 8),
    "allocator": 16 + 24 + 24,
    "isolation": 16 + 24 + 24,
    "encoding_and_output": 32 + 48 + 48,
    "offline_generator": 16 + 24 + 24,
}
STACK_FRAMES = {name: words * WORD_BYTES
                for name, words in STACK_LAYOUT_WORDS.items()}
STACK_LAYOUT_CHECK = max((
    STACK_FRAMES["runtime_entry"] + STACK_FRAMES["line_and_sampler"],
    STACK_FRAMES["runtime_entry"] + STACK_FRAMES["stage_c_driver"]
    + STACK_FRAMES["seven_transform_frames"] + STACK_FRAMES["product_planner"]
    + STACK_FRAMES["allocator"],
    STACK_FRAMES["runtime_entry"] + STACK_FRAMES["half_gcd_frames"]
    + STACK_FRAMES["allocator"],
    STACK_FRAMES["runtime_entry"] + STACK_FRAMES["isolation"]
    + STACK_FRAMES["allocator"],
    STACK_FRAMES["runtime_entry"] + STACK_FRAMES["encoding_and_output"],
    STACK_FRAMES["offline_generator"],
))
STACK_RESERVATION_CHECK = (
    (STACK_LAYOUT_CHECK + 16_383) // 16_384
) * 16_384

# The complete trace extends the A-D pool walk with the E/F/G slab objects and
# each real stack call chain.  It is the sole source of the memory claim.
from complete_memory import build as build_complete_memory
COMPLETE_MEMORY = build_complete_memory(sys.modules[__name__])
SLAB_EVENTS = tuple(
    (f"slab-class-{size}", slots, total)
    for size, slots, total in COMPLETE_MEMORY.slab_classes
)
SLAB_CLASSES = {size: slots for size, slots, _total in COMPLETE_MEMORY.slab_classes}
SLAB_AREA = COMPLETE_MEMORY.slab_area
SLAB_HEADS = COMPLETE_MEMORY.slab_heads
ARENA = COMPLETE_MEMORY.arena
STACK_LIVE = COMPLETE_MEMORY.stack_live
STACK = COMPLETE_MEMORY.stack_reserved
MEMORY_BYTES = COMPLETE_MEMORY.footprint

RAW_TIME = (Decimal(N_MAX).ln() - Decimal(COMPRESSION).ln()) / Decimal(2).ln()
TIME_CLAIM = ceil_decimal(RAW_TIME, 5)
RAW_MEMORY = Decimal(MEMORY_BYTES).ln() / Decimal(2).ln()
MEMORY_CLAIM = ceil_decimal(RAW_MEMORY, 5)
SCORE = TIME_CLAIM + max(Decimal(0), MEMORY_CLAIM - Decimal(20))


def validate() -> None:
    assert DEGREE == 5 ** (ROUNDS + 6) == DECLARED["degree"]
    assert ODD_DEGREE == (DEGREE - 1) // 2 == DECLARED["odd_degree"]
    assert STAGE_B_POINTS == DECLARED["stage_b_points"]
    assert STAGE_B_EVALUATIONS == 2 * STAGE_B_POINTS
    assert STAGE_B_EVALUATIONS == DECLARED["stage_b_evaluations"]
    assert STAGE_B_INDEX_BITS == DECLARED["stage_b_index_bits"]
    assert GRAEFFE_DEPTH == DECLARED["graeffe_depth"]
    assert FULL_POINTS == DECLARED["full_points"]
    assert TRUNCATED_POINTS == DECLARED["truncated_points"]
    assert TOP_WIDTH + sum(TR_MIDDLE_WIDTHS) + BOTTOM_WIDTH == DECLARED["transform_layers"]
    assert ELL == 4_208_787
    assert COMPRESSION == 321
    assert base_node() == 105_140
    assert len(OUTER_STEPS) == DECLARED["outer_steps"]
    assert sum(1 for step in OUTER_STEPS if step.level == 21) == 10
    assert RECOVERY_SUBTREES[-1] == (512, 2)
    assert exponent_bits() == (DECLARED["powering_steps"],
                               DECLARED["powering_multiplies"])
    assert PLAN_MISSES == sum(row[2] for row in PLANNER_ROWS)
    assert OFFLINE_EXACT == OFFLINE_CHARGE
    assert SLAB_AREA == sum(row[2] for row in SLAB_EVENTS)
    assert COMPLETE_MEMORY.pool_peak == ALLOCATOR.peak
    assert STACK_LAYOUT_CHECK == STACK_LIVE
    assert STACK_RESERVATION_CHECK == STACK
    assert max(event.live_region_bytes for event in COMPLETE_MEMORY.events
               if event.stage == "stack") == STACK_LIVE
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
        "register_words": REGISTER_WORDS,
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

### Appendix X.1: resident-memory helper in the ledger call graph

```python
#!/usr/bin/env python3
"""One complete resident-object trace for low-round Poseidon ledgers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResidentEvent:
    number: int
    stage: str
    action: str
    name: str
    region: str
    bytes: int
    live_region_bytes: int


@dataclass(frozen=True)
class CompleteMemory:
    events: tuple[ResidentEvent, ...]
    pool_peak: int
    slab_classes: tuple[tuple[int, int, int], ...]
    slab_area: int
    slab_heads: int
    gap: int
    arena: int
    stack_live: int
    stack_reserved: int
    code_static: int
    register_file: int
    offline_working: int
    footprint: int


class SlabTrace:
    def __init__(self, events: list[ResidentEvent]) -> None:
        self.events = events
        self.live: dict[str, tuple[int, int]] = {}
        self.class_live: dict[int, int] = {}
        self.class_peak: dict[int, int] = {}

    @staticmethod
    def size_class(need: int) -> int:
        power = 7
        while (1 << power) < need:
            power += 1
        assert power <= 14, (need, power)
        return 1 << power

    def alloc_words(self, stage: str, name: str, words: int) -> None:
        assert name not in self.live
        need = 64 + 64 * ((32 * words + 63) // 64)
        size = self.size_class(need)
        self.live[name] = (size, words)
        self.class_live[size] = self.class_live.get(size, 0) + 1
        self.class_peak[size] = max(self.class_peak.get(size, 0), self.class_live[size])
        self.events.append(ResidentEvent(
            len(self.events) + 1, stage, "alloc", name, f"slab-{size}", size,
            sum(item[0] for item in self.live.values()),
        ))

    def free(self, stage: str, name: str) -> None:
        size, _words = self.live.pop(name)
        self.class_live[size] -= 1
        self.events.append(ResidentEvent(
            len(self.events) + 1, stage, "free", name, f"slab-{size}", size,
            sum(item[0] for item in self.live.values()),
        ))


def stack_chains(module) -> tuple[dict[str, int], int]:
    frames = module.STACK_FRAMES
    entry = frames["runtime_entry"]
    chains = {
        "sampling": entry + frames["line_and_sampler"],
        "stage_c_transform": entry + frames["stage_c_driver"]
        + frames["seven_transform_frames"] + frames["product_planner"]
        + frames["allocator"],
        "stage_d_half_gcd": entry + frames["half_gcd_frames"] + frames["allocator"],
        "stage_e_isolation": entry + frames["isolation"] + frames["allocator"],
        "stage_f_g_output": entry + frames["encoding_and_output"],
        "offline_generation": frames["offline_generator"],
    }
    return chains, max(chains.values())


def build(module) -> CompleteMemory:
    events: list[ResidentEvent] = []
    for event in module.ALLOCATOR.events:
        events.append(ResidentEvent(
            len(events) + 1, event.stage, event.action, event.name,
            f"pool-{event.side}", event.size, event.live,
        ))

    slabs = SlabTrace(events)
    # Stage E constant-work round.  All arrays below are simultaneously live
    # at the maximum-degree path; later rounds reuse the same slots.
    for name, words in (
        ("E-factor", 17), ("E-base", 17), ("E-power-result", 17),
        ("E-product-scratch", 33), ("E-P-minus-one", 17),
        ("E-P-plus-one", 17), ("E-gcd-left", 17), ("E-gcd-right", 17),
        ("E-selected-factor", 17), ("E-random-words", 2),
    ):
        slabs.alloc_words("E", name, words)
    for name in reversed(tuple(slabs.live)):
        slabs.free("E", name)

    for name, words in (
        ("F-root-chain", 32), ("F-candidate-state", 16),
        ("F-input-pair", 4), ("F-line-state", 6),
    ):
        slabs.alloc_words("F", name, words)
    for name in reversed(tuple(slabs.live)):
        slabs.free("F", name)

    for name, words in (
        ("G-two-input-pairs", 4), ("G-two-poseidon-states", 6),
        ("G-canonical-encodings", 4), ("G-output-elements", 2),
    ):
        slabs.alloc_words("G", name, words)
    for name in reversed(tuple(slabs.live)):
        slabs.free("G", name)
    assert not slabs.live

    chains, stack_live = stack_chains(module)
    for name, size in chains.items():
        events.append(ResidentEvent(
            len(events) + 1, "stack", "enter-call-chain", name, "stack", size, size,
        ))
        events.append(ResidentEvent(
            len(events) + 1, "stack", "leave-call-chain", name, "stack", size, 0,
        ))
    stack_reserved = ((stack_live + 16_383) // 16_384) * 16_384

    classes = tuple(
        (size, slots, size * slots)
        for size, slots in sorted(slabs.class_peak.items())
    )
    slab_area = sum(total for _size, _slots, total in classes)
    slab_heads = len(classes) * 32
    gap = module.POOL_GAP
    pool_peak = module.ALLOCATOR.peak
    arena = pool_peak + gap + slab_area + slab_heads
    footprint = (
        arena + module.CODE_AND_STATIC + module.REGISTER_FILE
        + module.OFFLINE_WORKING + stack_reserved
    )
    return CompleteMemory(
        tuple(events), pool_peak, classes, slab_area, slab_heads, gap, arena,
        stack_live, stack_reserved, module.CODE_AND_STATIC,
        module.REGISTER_FILE, module.OFFLINE_WORKING, footprint,
    )
```

### Appendix X.2: apply-plan helper in the ledger call graph

```python
#!/usr/bin/env python3
"""Generated low-round ports of the judged r10-v9 apply schedules.

The direct and fixed-slot plans below preserve the r10-v9 atomic action
multisets, descending overwrite order, and six-spectrum allocation contract.
The in-place candidate is the already charged low-round folded-operand plan;
it remains a separate family because it retains g and R as its two operand
arrays instead of allocating two operand/output spectra.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import Callable


Transform = Callable[[int, bool], int]
AdmissiblePoints = Callable[[int], tuple[int, ...]]
LoopCharge = Callable[[int], int]
FixedCharge = Callable[[str], int]


def unit_action_rows(*names: str) -> dict[str, int]:
    assert len(names) == len(set(names))
    return {name: 1 for name in names}


COPY_LIVE_COEFFICIENT_ACTIONS = unit_action_rows(
    "source_pointer_update", "source_address", "source_load",
    "destination_pointer_update", "destination_address", "destination_store",
    "loop_control",
)
ZERO_PAD_COEFFICIENT_ACTIONS = unit_action_rows(
    "destination_pointer_update", "destination_address", "zero_store",
    "loop_update", "loop_branch",
)
CYCLIC_FOLD_COEFFICIENT_ACTIONS = unit_action_rows(
    "source_pointer_update", "source_address", "source_load",
    "destination_pointer_update", "destination_address", "destination_load",
    "field_addition", "destination_store", "loop_update", "loop_branch",
)
FIXED_SLOT_POINT_ACTIONS = unit_action_rows(
    "operand_left_load", "operand_right_load", "matrix_left_load",
    "matrix_right_load", "first_field_multiply", "second_field_multiply",
    "output_add_subtract", "output_store", "operand_left_pointer_update",
    "operand_right_pointer_update", "matrix_left_pointer_update",
    "matrix_right_pointer_update",
)
FIXED_SLOT_PLACEMENT_ACTIONS = unit_action_rows(
    "spectrum_load", "scale_load", "scale_multiplication", "destination_load",
    "overlap_add", "destination_store", "destination_pointer_update",
)
DIRECT_POINT_ACTIONS = unit_action_rows(
    "operand_a_address", "operand_a_load", "operand_b_address", "operand_b_load",
    "matrix_r11_address", "matrix_r11_load", "matrix_r12_address",
    "matrix_r12_load", "matrix_r21_address", "matrix_r21_load",
    "matrix_r22_address", "matrix_r22_load", "first_field_multiply",
    "second_field_multiply", "third_field_multiply", "fourth_field_multiply",
    "first_output_add_subtract", "second_output_add_subtract",
    "output_c_store", "output_d_store",
)
DIRECT_PLACEMENT_ACTIONS = unit_action_rows(
    "source_address", "source_load", "destination_address", "destination_store",
    "destination_pointer_update",
)
DIRECT_OUTPUT_ADDRESS_REUSE = {
    "output_c_store": "operand_a_address",
    "output_d_store": "operand_b_address",
}
IN_PLACE_POINT_ACTIONS = unit_action_rows(
    "first_matrix_product", "second_matrix_product", "third_matrix_product",
    "fourth_matrix_product", "first_output_add_subtract",
    "second_output_add_subtract", "first_inverse_scale",
    "second_inverse_scale", "first_shared_operand_access",
    "second_shared_operand_access", "first_shared_output_access",
    "second_shared_output_access",
)
IN_PLACE_OUTPUT_ACTIONS = unit_action_rows(
    "source_load", "inverse_scale_multiply", "destination_store",
    "destination_pointer_update",
)

assert sum(COPY_LIVE_COEFFICIENT_ACTIONS.values()) == 7
assert sum(ZERO_PAD_COEFFICIENT_ACTIONS.values()) == 5
assert sum(CYCLIC_FOLD_COEFFICIENT_ACTIONS.values()) == 10
assert sum(FIXED_SLOT_POINT_ACTIONS.values()) == 12
assert sum(FIXED_SLOT_PLACEMENT_ACTIONS.values()) == 7
assert sum(DIRECT_POINT_ACTIONS.values()) == 20
assert sum(DIRECT_PLACEMENT_ACTIONS.values()) == 5
assert sum(IN_PLACE_POINT_ACTIONS.values()) == 12
assert sum(IN_PLACE_OUTPUT_ACTIONS.values()) == 4
assert set(DIRECT_OUTPUT_ADDRESS_REUSE) == {
    "output_c_store", "output_d_store",
}
assert set(DIRECT_OUTPUT_ADDRESS_REUSE.values()) <= set(DIRECT_POINT_ACTIONS)


PLAN_DISPATCH = 23
CALL_CLOSE = 42


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
    kind: str
    candidate_count: int
    plan: object

    @property
    def total(self) -> int:
        return sum((self.transforms, self.matrix_inputs, self.operand_inputs,
                    self.pointwise, self.output_loops, self.fixed))

    def operation_rows(self) -> dict[str, int]:
        rows = {
            "transforms": self.transforms,
            "matrix_inputs": self.matrix_inputs,
            "operand_inputs": self.operand_inputs,
            "pointwise": self.pointwise,
            "output_loops": self.output_loops,
            "fixed": self.fixed,
        }
        assert sum(rows.values()) == self.total
        return rows


@dataclass(frozen=True)
class FixedSlotBlockStep:
    block_index: int
    produces_output: bool
    lower_destination_block: int
    upper_destination_block: int


def build_matrix_alias_schedule(
        matrix_length: int, transform_points: int,
) -> tuple[tuple[str, str, int, int], ...]:
    rows = []
    for entry in ("r11", "r12", "r21", "r22"):
        rows.extend((
            (entry, "node_writes_source_coefficients", 0, matrix_length),
            (entry, "node_scratch_uses_unused_arena", matrix_length,
             transform_points),
            (entry, "node_scratch_released", matrix_length,
             transform_points),
            (entry, "zero_padding_written", matrix_length, transform_points),
            (entry, "forward_butterflies_load_before_store", 0,
             transform_points),
        ))
    assert matrix_length <= transform_points
    assert all(start <= end for _entry, _phase, start, end in rows)
    return tuple(rows)


@dataclass(frozen=True)
class FixedSlotApplyPlan:
    degree: int
    budget: int
    block_length: int
    transform_points: int
    matrix_blocks: int
    operand_blocks: int
    output_slots: int
    matrix_alias: bool = False

    @property
    def output_length(self) -> int:
        return self.degree - self.budget

    @property
    def matrix_length(self) -> int:
        return self.budget + 1

    @property
    def operand_length(self) -> int:
        return self.degree + 1

    @cache
    def block_schedule(self) -> tuple[FixedSlotBlockStep, ...]:
        schedule = tuple(
            FixedSlotBlockStep(index, index < self.output_slots, index, index + 1)
            for index in range(self.operand_blocks - 1, -1, -1)
        )
        assert tuple(row.block_index for row in schedule) == tuple(
            range(self.operand_blocks - 1, -1, -1)
        )
        assert all(
            not row.produces_output
            or row.upper_destination_block >= self.operand_blocks
            or row.upper_destination_block > row.block_index
            for row in schedule
        )
        return schedule

    def allocation_arrays(self) -> tuple[tuple[str, int, str], ...]:
        matrix_words = self.matrix_blocks * self.transform_points
        return tuple(
            (f"matrix-{entry}-spectrum", matrix_words, "persistent matrix spectrum")
            for entry in ("r11", "r12", "r21", "r22")
        ) + (
            ("operand-a-spectrum-output-c", self.transform_points,
             "reusable descending operand/output spectrum"),
            ("operand-b-spectrum-output-d", self.transform_points,
             "reusable descending operand/output spectrum"),
        )

    def matrix_alias_schedule(self) -> tuple[tuple[str, str, int, int], ...]:
        if not self.matrix_alias:
            return ()
        return build_matrix_alias_schedule(
            self.matrix_length, self.transform_points,
        )

    def role_changes(self) -> tuple[tuple[str, str, str, int], ...]:
        rows: list[tuple[str, str, str, int]] = []
        for block in self.block_schedule():
            for operand, output in (("a", "c"), ("b", "d")):
                suffix = f"operand-{operand}-spectrum-output-{output}"
                rows.append((suffix, "coefficient block", "forward spectrum",
                             block.block_index))
                if block.produces_output:
                    rows.extend((
                        (suffix, "forward spectrum", f"pointwise output {output}",
                         block.block_index),
                        (suffix, f"pointwise output {output}",
                         f"inverse output {output}", block.block_index),
                        (suffix, f"inverse output {output}",
                         "placed lower and upper halves", block.block_index),
                    ))
                else:
                    rows.append((suffix, "forward spectrum",
                                 "discarded out-of-window input",
                                 block.block_index))
        return tuple(rows)

    def operation_rows(self, transform: Transform, loop8: LoopCharge,
                       fixed_actions: FixedCharge) -> dict[str, int]:
        copy = sum(COPY_LIVE_COEFFICIENT_ACTIONS.values())
        zero = sum(ZERO_PAD_COEFFICIENT_ACTIONS.values())
        point = sum(FIXED_SLOT_POINT_ACTIONS.values())
        placement = sum(FIXED_SLOT_PLACEMENT_ACTIONS.values())
        forward_matrix = 4 * self.matrix_blocks
        assert self.output_slots <= self.operand_blocks
        forward_operand = 2 * self.operand_blocks
        inverse_output = 2 * self.output_slots
        rows = {
            "forward_matrix_transforms": (
                forward_matrix * transform(self.transform_points, False)
            ),
            "forward_operand_transforms": (
                forward_operand * transform(self.transform_points, False)
            ),
            "inverse_output_transforms": (
                inverse_output * transform(self.transform_points, True)
            ),
            "matrix_input_copy_and_zero": 4 * (
                copy * self.matrix_length * int(not self.matrix_alias)
                + zero * (self.matrix_blocks * self.transform_points
                          - self.matrix_length)
            ),
            "operand_input_copy_and_zero": 2 * (
                copy * self.operand_length
                + zero * (self.operand_blocks * self.transform_points
                          - self.operand_length)
            ),
            "two_output_pointwise": self.output_slots * 2 * (
                point * self.transform_points + loop8(self.transform_points)
            ),
            "overlap_add_placement": self.output_slots * 2 * (
                placement * self.block_length + loop8(self.block_length)
            ),
            "dispatch_and_close": (
                (forward_matrix + forward_operand + inverse_output)
                * PLAN_DISPATCH + CALL_CLOSE
            ),
            "apply_arena_allocation_and_release": (
                2 * fixed_actions("allocator_call")
            ),
        }
        return rows


@dataclass(frozen=True)
class DirectApplyPlan:
    degree: int
    budget: int
    transform_points: int
    matrix_alias: bool = False

    @property
    def output_length(self) -> int:
        return self.degree - self.budget

    @property
    def matrix_length(self) -> int:
        return self.budget + 1

    @property
    def operand_length(self) -> int:
        return self.degree + 1

    def allocation_arrays(self) -> tuple[tuple[str, int, str], ...]:
        return tuple(
            (f"matrix-{entry}-spectrum", self.transform_points,
             "persistent matrix spectrum")
            for entry in ("r11", "r12", "r21", "r22")
        ) + (
            ("operand-a-spectrum-output-c", self.transform_points,
             "folded operand then output c"),
            ("operand-b-spectrum-output-d", self.transform_points,
             "folded operand then output d"),
        )

    def matrix_alias_schedule(self) -> tuple[tuple[str, str, int, int], ...]:
        if not self.matrix_alias:
            return ()
        return build_matrix_alias_schedule(
            self.matrix_length, self.transform_points,
        )

    def operation_rows(self, transform: Transform, loop8: LoopCharge,
                       fixed_actions: FixedCharge) -> dict[str, int]:
        copy = sum(COPY_LIVE_COEFFICIENT_ACTIONS.values())
        zero = sum(ZERO_PAD_COEFFICIENT_ACTIONS.values())
        fold = sum(CYCLIC_FOLD_COEFFICIENT_ACTIONS.values())
        matrix_inputs = 4 * (
            copy * self.matrix_length * int(not self.matrix_alias)
            + zero * (self.transform_points - self.matrix_length)
        )
        if self.operand_length <= self.transform_points:
            one_operand = (
                copy * self.operand_length
                + zero * (self.transform_points - self.operand_length)
            )
        else:
            one_operand = (
                copy * self.transform_points
                + fold * (self.operand_length - self.transform_points)
            )
        return {
            "six_forward_transforms": 6 * transform(self.transform_points, False),
            "two_inverse_transforms": 2 * transform(self.transform_points, True),
            "four_matrix_copy_and_zero_forms": matrix_inputs,
            "two_operand_copy_zero_or_fold_forms": 2 * one_operand,
            "fused_two_output_pointwise": (
                sum(DIRECT_POINT_ACTIONS.values()) * self.transform_points
                + loop8(self.transform_points)
            ),
            "two_output_placements": 2 * (
                sum(DIRECT_PLACEMENT_ACTIONS.values()) * self.output_length
                + loop8(self.output_length)
            ),
            "eight_transform_dispatches_and_close": 8 * PLAN_DISPATCH + CALL_CLOSE,
            "apply_arena_allocation_and_release": (
                2 * fixed_actions("allocator_call")
            ),
        }


@dataclass(frozen=True)
class InPlaceApplyPlan:
    degree: int
    budget: int
    transform_points: int
    matrix_alias: bool = False

    @property
    def output_length(self) -> int:
        return self.degree - self.budget

    @property
    def matrix_length(self) -> int:
        return self.budget + 1

    @property
    def operand_length(self) -> int:
        return self.degree + 1

    def allocation_arrays(self) -> tuple[tuple[str, int, str], ...]:
        return tuple(
            (f"matrix-{entry}-spectrum", self.transform_points,
             "matrix spectrum beside in-place g and R")
            for entry in ("r11", "r12", "r21", "r22")
        )

    def matrix_alias_schedule(self) -> tuple[tuple[str, str, int, int], ...]:
        """Node-output and scratch phases inside four aliased spectra."""
        if not self.matrix_alias:
            return ()
        return build_matrix_alias_schedule(
            self.matrix_length, self.transform_points,
        )

    def operation_rows(self, transform: Transform, loop8: LoopCharge,
                       fixed_actions: FixedCharge) -> dict[str, int]:
        copy = sum(COPY_LIVE_COEFFICIENT_ACTIONS.values())
        zero = sum(ZERO_PAD_COEFFICIENT_ACTIONS.values())
        fold = sum(CYCLIC_FOLD_COEFFICIENT_ACTIONS.values())
        matrix_inputs = 4 * (
            copy * self.matrix_length * int(not self.matrix_alias)
            + zero * (self.transform_points - self.matrix_length)
        )
        if self.operand_length <= self.transform_points:
            one_operand = (
                copy * self.operand_length
                + zero * (self.transform_points - self.operand_length)
            )
        else:
            one_operand = (
                copy * self.transform_points
                + fold * (self.operand_length - self.transform_points)
            )
        return {
            "six_forward_transforms": 6 * transform(self.transform_points, False),
            "two_inverse_transforms": 2 * transform(self.transform_points, True),
            "four_matrix_copy_and_zero_forms": matrix_inputs,
            "two_in_place_operand_copy_zero_or_fold_forms": 2 * one_operand,
            "fused_scaled_two_output_pointwise": (
                sum(IN_PLACE_POINT_ACTIONS.values()) * self.transform_points
                + loop8(self.transform_points)
            ),
            "two_in_place_output_loops": 2 * (
                sum(IN_PLACE_OUTPUT_ACTIONS.values()) * self.output_length
                + loop8(self.output_length)
            ),
            "allocator_dispatch_and_close": (
                2 * fixed_actions("allocator_call")
                + 8 * PLAN_DISPATCH + fixed_actions("close_42")
            ),
        }


@dataclass(frozen=True)
class Candidate:
    kind: str
    points: int
    charge: ApplyCharge


def _charge(kind: str, plan: object, rows: dict[str, int], budget: int,
            output: int, candidate_count: int) -> ApplyCharge:
    if kind == "fixed-slot":
        transforms = sum(value for name, value in rows.items()
                         if "transform" in name)
        matrix = rows["matrix_input_copy_and_zero"]
        operand = rows["operand_input_copy_and_zero"]
        pointwise = rows["two_output_pointwise"]
        output_loops = rows["overlap_add_placement"]
        fixed = (rows["dispatch_and_close"]
                 + rows["apply_arena_allocation_and_release"])
    elif kind == "direct":
        transforms = (rows["six_forward_transforms"]
                      + rows["two_inverse_transforms"])
        matrix = rows["four_matrix_copy_and_zero_forms"]
        operand = rows["two_operand_copy_zero_or_fold_forms"]
        pointwise = rows["fused_two_output_pointwise"]
        output_loops = rows["two_output_placements"]
        fixed = (rows["eight_transform_dispatches_and_close"]
                 + rows["apply_arena_allocation_and_release"])
    else:
        transforms = (rows["six_forward_transforms"]
                      + rows["two_inverse_transforms"])
        matrix = rows["four_matrix_copy_and_zero_forms"]
        operand = rows["two_in_place_operand_copy_zero_or_fold_forms"]
        pointwise = rows["fused_scaled_two_output_pointwise"]
        output_loops = rows["two_in_place_output_loops"]
        fixed = rows["allocator_dispatch_and_close"]
    points = getattr(plan, "transform_points")
    charge = ApplyCharge(points, budget, output, transforms, matrix, operand,
                         pointwise, output_loops, fixed, kind, candidate_count,
                         plan)
    assert charge.total == sum(rows.values())
    return charge


def apply_candidates(degree: int, budget: int, transform: Transform,
                     admissible_points: AdmissiblePoints, loop8: LoopCharge,
                     fixed_actions: FixedCharge,
                     matrix_alias: bool = False) -> tuple[Candidate, ...]:
    """Construct every valid candidate under the low-round 3*2^j cap."""
    output = degree - budget
    matrix_length = budget + 1
    maximum_points = 3 * matrix_length
    candidates: list[tuple[str, object, dict[str, int]]] = []

    for points in admissible_points(output):
        if points > maximum_points:
            continue
        direct = DirectApplyPlan(degree, budget, points, matrix_alias)
        candidates.append(("direct", direct,
                           direct.operation_rows(transform, loop8,
                                                 fixed_actions)))
        in_place = InPlaceApplyPlan(degree, budget, points, matrix_alias)
        candidates.append(("in-place", in_place,
                           in_place.operation_rows(transform, loop8,
                                                   fixed_actions)))

    for points in admissible_points(2 * matrix_length - 1):
        if points > maximum_points:
            continue
        block_length = points - budget
        if block_length < matrix_length:
            continue
        operand_blocks = (degree + 1 + block_length - 1) // block_length
        output_slots = (output + block_length - 1) // block_length
        fixed = FixedSlotApplyPlan(
            degree, budget, block_length, points, 1, operand_blocks,
            output_slots, matrix_alias,
        )
        candidates.append(("fixed-slot", fixed,
                           fixed.operation_rows(transform, loop8,
                                                fixed_actions)))

    assert candidates, (degree, budget, output, maximum_points)
    count = len(candidates)
    result = tuple(
        Candidate(kind, getattr(plan, "transform_points"),
                  _charge(kind, plan, rows, budget, output, count))
        for kind, plan, rows in candidates
    )
    return result


def choose_apply_plan(degree: int, budget: int, transform: Transform,
                      admissible_points: AdmissiblePoints, loop8: LoopCharge,
                      fixed_actions: FixedCharge,
                      matrix_alias: bool = False) -> ApplyCharge:
    candidates = apply_candidates(
        degree, budget, transform, admissible_points, loop8, fixed_actions,
        matrix_alias,
    )
    kind_order = {"fixed-slot": 0, "direct": 1, "in-place": 2}
    return min(
        (candidate.charge for candidate in candidates),
        key=lambda charge: (charge.total, charge.points,
                            kind_order[charge.kind]),
    )
```
