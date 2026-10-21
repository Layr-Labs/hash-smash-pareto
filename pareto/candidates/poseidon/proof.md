# Orchard Poseidon r6: full union-machine ledger

## 1. Claim

The selected target is `poseidon-orchard-r6-prefix-v1`: P128Pow5T3 over Pallas with partial rounds 4 through 9 and the fixed eight full rounds. The attack class is ordinary collision search. One centre is sampled and the construction uses the published line, odd part, 24-step Graeffe prefix, exact value-domain Montgomery powering and inversion-free half-gcd.

The complete integer ledger gives `N_max = 9,304,019,784,146`. At 342 primitive operations per target compression, `time_log2 = 34.66314`. The event-by-event allocator walk and fixed regions give 15,638,058,240 bytes, `memory_log2_bytes = 33.86435`. Applying the lane's stated scalar formula gives normalized cost `48.52749`. For comparison context only, the arithmetic differences from our current `48.52996` entry and the published `48.52996` reference are `0.00247` and `0.00247`. These differences are not a ranking model or evidence for the cost derivation.

H-ONE, H-NORMAL, the success proof and the experiments are unchanged. The success lower bound is `0.39009`. The resource ledger adds no heuristic. Every score-critical resource number is computed inside this package; no prior row total or memory peak is an input.

Jbenisek `56272e37` and `27fbfbe7` are credited for running-twiddle block-form products, Jbenisek `c7ef0551` for the 387-register seven-layer machine and offset-zero variants, and cryptogakusei `1533f8f0` for the charged wide-register precedent. Their text supplies constructions, not score-critical integers.

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

4.1.3 Stage F: the root of `g_c` above `y`. Stage F takes exactly `d+1 = 25` successive square roots, each charged 47,012 operations, then scans all `2^24 = 16,777,216` candidates in the worst case. A candidate costs `574`: one root update, two point additions, two line evaluations at `281` operations, four calls, comparison and branch, and three loop controls. The exit costs two operations and the final back-map costs 47,012. Thus row F is `25*47,012 + 2^24*574 + 2 + 47,012 = 9,631,344,298`. The scan stops only after the line equality holds, and stage G then verifies both complete reference hashes.

Stage B prices `H = 201,326,592` points and `2H = 402,653,184` line evaluations. Its bit-reversed row index has `b = 26` executed bits, the radix-2 row width named by the Stage-B plan, so its per-point loop charge is `13 + 11b = 299`. The ledger assertion binds `b`, `H` and `2H` to the algorithm declaration.

### 4.2 Machine model and charges (`C(6) = 342`)

Every field operation, load, store, control operation and random word costs one primitive operation. One target compression costs `C(r) = 216 + 21r = 342` primitive operations. The implementation is one thread and has no dispatch.

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

with 20 in place of 19 for an inverse. The pass schedule balances the non-fused layers at widths no greater than 7; Appendix E prints every selected width.

The half-gcd node uses the same position-shared pass. At width `k`, its
`2^k` values, `2^k-1` twiddles and one temporary require `2^(k+1)` field
registers; at the maximum width seven this is exactly 256, within the declared
field-register subfile. One running chain remains live for a position and is
reused across all blocks at that position. After the recursive and array rows,
each non-leaf node adds exactly 184 operations: 20 entry/exit, 16 split/degree
tests, 24 child frames, 8 return tests, 20 arena mark/release, 18 transform
dispatch, 48 matrix-pointer setup, 18 row/sign selection and 12 normal-sequence
tests. These are the control and lower-order operations that the earlier
percentage represented. There is no cost premise, fitted factor or percentage
margin.

The 27 truncated layers use `4 | 7,6,6 | 4`. Four adjacent middle blocks share a running group chain; the ledger asserts exact divisibility. Newton, quotient and every outer apply are recomputed from the same transform primitives. An outer apply above the single threshold `LMAX = 67,108,864 = 3*2^29` coefficients uses block length `2^22` and transforms of `2^23` points. Smaller applies use six forward and two inverse direct transforms at a length covering all six forward operands and both outputs.

The arena allocator has a 64-byte header and a payload rounded to 64 bytes. Large blocks use a two-ended first-fit pool. Appendix E.3 lists every allocation and free, its side, both extents and live bytes. Stage B alone retains a transform twiddle table. The root tables of the truncated transform remain. Stages C and D form product twiddles in registers.

### 4.3G The Graeffe prefix

Definition. For `h` monic of even degree `m` write `h(X) = E(X^2) + X O(X^2)`; its Graeffe transform is `h~(Y) = E(Y)^2 - Y O(Y)^2`, so `h~(X^2) = h(X) h(-X)` and `h~` is monic of degree `m` with roots the squares of the roots of `h` (with multiplicity). Stage C first replaces `g = g_c` by `g^(24)`, 24 Graeffe steps, then computes `R = S^e mod g^(24)`, `e = (p-1)/2^25` (2-adicity 32), and stage D takes `G = gcd(g^(24), R - 1)`.

Lemma. `G` is the product of `(Y - y)` over the distinct values `y = S^(2^24)`, `S` a usable root of `g_c` (a nonzero square in `F_p` with `g_c(S) = 0`, section 3). Proof: `g^(24)(Y) = prod_i (Y - S_i^(2^24))` over the roots `S_i` of `g_c` in an algebraic closure; `Y^e - 1` is squarefree and its roots are the `2^25`-th powers of `F_p^*`. If `S_i^(2^24) = u^(2^25)` with `u` in `F_p^*`, then `S_i = u^2 zeta` with `zeta^(2^24) = 1`, so `zeta` is in `F_p` and `zeta = xi^2` with `xi^(2^25) = 1` (`2^25 | p - 1`), and `S_i = (u xi)^2` is a nonzero square of `F_p`; conversely `S = v^2` gives `S^(2^24) = v^(2^25)`. So `deg G` is the number of distinct `2^24`-th powers of the usable roots: `1 <= deg G <= k(c)` when `k(c) >= 1`, and `deg G = 0` when `k(c) = 0`; the event `E_c` of 9.2 gives `1 <= deg G <= DMAX`.

Execution (on the point set `O1` of 4.3T). Appendix E.1 derives the Graeffe step directly from the live top, middle, bottom and recovery kernels. 24 steps precede the fixed exponent `E = (p-1)/2^25`. This exponent has bit length 230. Its leading one is followed by at least 24 high zero bits, so the scan starts from the monomial residue `S^(2^24)`; `2^24 < m`, hence that monomial is its own reduction. The remaining `230-1-24 = 205` bits cost one squaring each, and the remaining popcount minus one gives 45 multiply-by-`S` steps. No low bits are discarded.

Every map is exact; no premise is added to the time or the memory. The zero test of `k1` (4.3T) now concerns `g^(24)`: `g^(24)(y) = 0` for `y` in `O1` only if `g_c(x) = 0` for one of the `2^24` values `x` with `x^(2^24) = y` (in `F_p` or an extension); for each such `x`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g^(24) vanishes on O1) <= 2^24 n' (D - 1) / p = eps_g < 2^-175`.

### 4.3T Stage C in the value domain on truncated point sets (the method of bradcush `b30de9bf`/`a41aecdd`, 233 of 256 nodes)

Point sets. `N = 2^27` divides `p - 1` (2-adicity 32). Let `psi` have order `2^28`, `H_N = <psi^2>` and `Y = X^(2^19)`. `H_N` is the union of the 256 depth-8 nodes `{x : x^(2^19) = r_j}`, `r_j` the 256-th roots of unity in transform (bit-reversed) order; `O1` is the union of the first 233 nodes, `n' = 233 * 2^19 = 122,159,104 >= m + 1 = 122,070,313` points, and `O2` the same 233 nodes of the coset `psi H_N` (`x^(2^19) = r'_j`, `r'_j^256 = -1`), disjoint from `O1`. `P1 = prod_{j<233} (Y - r_j)` has degree `n'`, vanishes on `O1` and is the nonzero constant `P1(r'_j)` on node `j` of `O2`; `delta_j = 1/P1(r'_j)` (233 table constants).

Truncated transforms (bradcush `b30de9bf` 4.3, generalized from van der Hoeven's truncated Fourier transform). A polynomial of degree below `n'` is represented on the first 233 depth-8 nodes. The forward top covers all `N/2^4` offsets. The middle acts only on live nodes, in passes of 7, 6, 6 layers; the widest radix fits exactly in the declared register file. The bottom acts on `2^4`-point blocks. The inverse reverses these passes and recovers the maximal dropped subtrees `(1,8), (2,7), (4,6), (16,4)`. One recovery charges `size * 2^19 * (8*depth+2)` over those pairs. Each layer's ten events are two source-address updates, two loads, two butterfly field operations, two stores and two destination-address updates. The fixed close is `4*(2^19/2^10) = 1,048,576` operations: one close operation for each of four streams in every `2^10`-word chunk.

The top, middle and recovery layers are class-batched in the 11,776-word buffer. Each middle width has exactly `n'/2^k` blocks; four adjacent blocks share one chain. The script charges every block body, every group chain and every fixed wrapper. The top position loops use `F(N/2^4)`. Fused top passes enumerate loads, stores, both butterfly directions, active coset products and the offset-zero saving. Bottom kernels enumerate their loads, butterflies, point operations, pointer updates and four-block control. The exact maps and dropped-subtree recovery are unchanged; only the machine realization is repriced.

Montgomery powering (`b30de9bf` 4.5). For residues of degree `< n'`, `Mont(A, B) = (A B + u g)/P1` with `u = -A B / g mod P1` (`deg u < n'`); the division by `P1` is exact, `Mont(A, B) = A B / P1 mod g`, and `deg Mont(A, A) <= n' - 2`, so `X Mont(A, A)` has degree `< n'`. A residue `A` (representing `S^e P1`) is held by its values on `O1` and on `O2`, each up to a tracked scalar. One step: `U = A^2 k1` on `O1` (`k1 = -1/(N^3 g)` there; `u` is determined by its values on `O1`); `U` to `O2` (truncated inverse on `O1`, truncated forward on `O2`); `B2 = (A2^2 + U g) delta_j` on node `j` of `O2`, which is `Mont(A, A)` up to the tracked scalar because `P1 = 1/delta_j` there, times the point `x` when the exponent bit is 1; `B2` to `O1` (truncated inverse on `O2`, truncated forward on `O1`). No `1/N` is executed inside the steps (the scalars are tracked, 2 operations per step). Per point and step: on `O1` `sqr, LD k1, mul` (4); on `O2` `LD A2, sqr, LD g, mul, add`, the multiplication by `delta_j`, `ST` (10) and the load of `delta_j` per block (2); 3 more for a 1-bit (the load of the point and a multiplication).

Entry and exit. `g` (coefficients after the Graeffe prefix of 4.3G, its slots above `m` zero) goes to `O1` and `O2` (a truncated forward each; every scaling of this section, `1/N` and the coset twist, is a running product fused into the adjacent pass, 2 operations per point). The start residue is `A0 = X^v P1 mod g`, `v = 2^24 = 16,777,216` (VSHIFT_LOG = 24 HIGH zero bits immediately after the leading one): `q = floor(X^v P1 / g)` has `ell = v + n' - m + 1 = 16,866,009` coefficients and is formed from the Newton reciprocal of the reversed `g` and one product (transforms of up to `3*2^24` points, with running twiddle factors and no stage product table); on node `j` of `O2`, `x^v P1(x) = r'_j^32 P1(r'_j)` is a constant, so `A0 = x^v P1 - q g` there is one truncated forward of `q` and one pointwise pass (8 per point); then `A0` goes to `O1`. `k1` is formed by chunked batch inversion on `O1` (chunks of `2^13` points: prefix products, one inversion, two multiplications per point; the `2^13` prefixes are kept in the batch buffer, which no transform uses at that time); each chunk product is tested for zero before its inversion (2 per chunk), and a zero ends the trial: for fixed `x != 0`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g vanishes on O1) <= eps_g < 2^-175` for the transformed `g` (4.3G, 9.2). The exit is one step with multiplier 1 (`Mont(A, 1)`) and two truncated inverses with their scaling, which return `kappa R` (`kappa` the tracked scalar) and `g` in coefficient form; the gcd is scale-invariant, so stage D receives `kappa R - kappa`. There are `205` squaring steps (the exponent `(p-1)/2^25`, 4.3G), `45` of them also multiplying by `S`.

Exactness and memory. Every map above is exact: the
Montgomery products act on polynomials of degree below `n'`, represented
bijectively by their values on the live nodes. Stage C adds no premise. Its
live set contains four 122,159,104-word value arrays, one
11,776-word batch buffer, 16,647 words of constants,
node deltas and root tables, and the Newton reciprocal, Barrett quotient and
transform workspaces for the lifetimes in Appendix E.4. Appendix E.1 is
rendered from `STAGE_C_COMPONENTS` and gives **row C = 6,418,521,942,506**.

### 4.4 Stage D: the inversion-free half-gcd on three rows (bradcush `4bcabff8`), with the in-place applies of the memory cap

Appendix E.2 gives **row D = 2,690,873,000,425**.

Stage-D binding. The inversion-free node cap is `j <= 22` and the base case is budget 63 (`j = 6`). The driver executes 49 outer steps. Each step chooses the largest admissible budget `2^j-1` and decrements the degree by `(2^j-1)+1 = 2^j`. It reaches degree 168; classical Euclid then runs directly from degree 168. There is no lean-tail literal. The apply mode is `block` with the single threshold `LMAX = 67,108,864 = 3*2^29`, block length 4,194,304, and 8,388,608-point long transforms. Appendix E.2 prices every node, apply and driver row.

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G = gcd(g, R - 1)`, whose roots are the values `y = S^(2^24)` of the usable roots `S` of `g_c` (4.3G); stage F stops only at an `s != 0` with `F(c + s) = F(c - s)` (4.1.3), so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Complete operation ledger

| row | event family | operations |
| --- | --- | ---: |
| init | runtime constants and bookkeeping | 18,009 |
| setup | line setup | 4,969 |
| A | coin draw, reduction and allocation | 1,228 |
| B | line evaluations, loop, table transform and normalization | 184,850,153,951 |
| C | Graeffe prefix and exact value-domain powering | 6,418,521,942,506 |
| D | inversion-free half-gcd normal walk with ABORT | 2,690,873,000,425 |
| E | 64 isolation rounds at degree at most 16 | 139,023,366 |
| F | 25 square roots, full 2^24 candidate scan and back-map | 9,631,344,298 |
| G | two reference verifications | 7,496 |
| trial loop | reset and closing control | 1,012 |
| plan misses | 88 enumerated immutable planner keys | 86,353 |
| output | two fixed output rows | 4,063,392 |
| offline | four named literal-generation loops | 137,141 |
| **N_max** | `T_fixed + T_trial + T_off` | **9,304,019,784,146** |

`T_fixed = 4,172,723`, `T_trial = 9,304,015,474,282` and `T_off = 137,141`. Their sum is `N_max = 9,304,019,784,146`. The exact raw time is `log2(N_max/342) = 34.6631387883357243705074715392590180244939630326344030726862008873319432610243567445043781`; upward rounding at five decimals gives `34.66314`.

All searches remain in the row that executes them. Stage E contains 64 complete isolation rounds. Stage F contains every one of the `2^24 = 16,777,216` candidates. The planner row enumerates every distinct Newton-product, quotient-product, transform, truncated-layout and direct-apply key and every candidate length tested for it. The offline constants take exactly 137,141 operations: 202 input literals at 324 operations, `4*497+3*222` field and bit-loop operations, `3*90` word operations, and 212 output literals at 324 plus one 81-operation short literal. The package contains no empirical timing conversion.

### 6.1 Exact-integer evidence

The exact-integer script embedded in Appendix X computes the geometry from `5^12`, constructs every transform and product plan, expands rows C and D, generates all 49 outer steps, walks all allocator events and derives both logarithms. Its assertions require the priced Stage-B point count to equal the declared `H`, the evaluation count to equal `2H`, and the Graeffe depth, powering steps, transform layers, truncated size, half-gcd cap, outer-step sequence and classical-tail start to equal the independent dimensions stated by the algorithm. It has no prior row total, prior `N_max`, prior memory peak or score as an input.

The complete configuration binding is `{"active_top_cosets": 16, "apply_mode": "block", "batch_words": 11776, "bit_extra_block_ops": 1, "bit_extra_point_ops": 3, "block_length": 4194304, "bottom_width": 4, "declared": {"degree": 244140625, "full_points": 134217728, "graeffe_depth": 24, "hgcd_cap": 22, "odd_degree": 122070312, "outer_steps": 49, "powering_multiplies": 45, "powering_steps": 205, "stage_b_evaluations": 402653184, "stage_b_index_bits": 26, "stage_b_points": 201326592, "tail_degree": 168, "transform_layers": 27, "truncated_points": 122159104}, "delta_copies": 1, "direct_row_cap": 0, "direct_transform_mode": "single", "expected_multiplies": 45, "expected_outer_steps": 49, "expected_squarings": 205, "full_log": 27, "graeffe_depth": 24, "hgcd_cap": 22, "inverse_top_core": 131, "inversion_chunk": 8192, "lmax": 67108864, "middle_widths": [7, 6, 6], "node_log": 19, "o2_extra_point_ops": 6, "outer_decrement_extra": 1, "recovery_fixed": 1048576, "recovery_per_layer": 8, "recovery_per_point": 2, "recovery_subtrees": [[1, 8], [2, 7], [4, 6], [16, 4]], "root_table_words": 16384, "rounds": 6, "slab_class_log": 18, "slab_slots": 16, "stage_b_eval_cost": 281, "stage_b_index_bits": 26, "stage_b_log": 26, "stage_b_multiplier": 3, "tail_degree": 168, "top_fused_core": 259, "top_half_core": 192, "top_width": 4, "truncated_nodes": 233, "vshift_log": 24}`. Every key is therefore present in the proof text as well as in Appendix X, and `validate()` binds the independent `declared` dimensions to the live values before any claim is emitted.

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
| bookkeeping 1000 | trial and stage descriptors 256; scalar tracking 256; abort tests 128; result pointers 128; entry exit 232 | 1,000 |
| planner key | key kind and length decode 6; geometry loads 4; cache probe 4; entry exit 4 | 18 |
| planner candidate | point count construction 7; transform charge construction 8; component sum 6; best cost comparison and select 4; candidate loop update and test 2 | 27 |
| stage d entry | outer degree and budget setup 256; normal sequence state 256; matrix descriptors 192; arena and transform descriptors 192; entry exit and initial tests 116 | 1,012 |
| stage d exit | final degree and remainder tests 64; matrix and operand release 96; arena reset 64; result descriptors 48; exit and return 45 | 317 |
| trial close | trial counter update 3; success and abort tests 3; arena reset test 3; loop branch and exit 3 | 12 |
| node fixed events | entry and exit 20; split and degree tests 16; two child call frames 24; two return tests 8; arena mark and release 20; six transform dispatches 18; matrix pointer bundles 48; row and sign selection 18; normal sequence tests 12 | 184 |
| stage init actions | load 201 runtime words at eight events 1,608; four 512 bit inversion chains at five events 10,240; initialize six 1024 word tables 6,144; entry shape tests and exit 17 | 18,009 |
| stage setup actions | three 512 bit field chains 1,536; nine 256 word descriptor rows 2,304; three target compression charge rows 1,026; entry shape tests pointers and exit 103 | 4,969 |
| stage a actions | fresh word draw and reduction 2; two 512 step reduction chains 1,024; two 97 event polynomial descriptors 194; allocation result test and exit 8 | 1,228 |
| stage e outer actions | factor and scratch allocator calls 1,310; stage bookkeeping 1,000 | 2,310 |
| stage f candidate actions | root update 1; two point additions 2; two line evaluations 562; four call boundaries 4; comparison and branch 2; loop update test branch 3 | 574 |
| stage g hash actions | target compression 342; canonical encoding and digest compare 3,405 | 3,747 |
| root lift actions | fixed square and multiply field events 45,056; two adic table load store and address events 1,280; candidate root tests and selects 512; entry exit loop and descriptor events 164 | 47,012 |
| output row actions | five 2pow18 copy and encode streams 1,310,720; four 2pow17 address and store streams 524,288; three 2pow16 validation streams 196,608; entry descriptors tests and exit 80 | 2,031,696 |
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

The simulation begins empty and executes 841 resident-object events in program order. Each heap request includes the 64-byte header and 64-byte payload rounding. The two pool sides are first-fit lists in address order; free neighbours merge and a free terminal extent returns to the unused middle. The same trace includes full stage-E, F and G objects and every live stack call chain. The named `batch-inversion-prefix` event reserves and releases exactly 8,192 words. The maximum sum of the low and high extents is 15,637,537,472 bytes, reached in stage C. The arena adds the 128-byte middle gap, traced slab classes and 128 bytes of slab free-list heads.

| region or event peak | bytes |
| --- | ---: |
| stage A live peak | 3,909,091,392 |
| stage B live peak | 13,572,767,936 |
| stage C live peak | 15,637,537,472 |
| stage D live peak | 12,885,435,072 |
| two-ended pool high-water | 15,637,537,472 |
| middle gap | 128 |
| traced slab classes | 11,136 |
| slab free-list heads | 128 |
| **arena** | **15,637,548,864** |
| code and static data, derived by emitted family | 463,648 |
| 387-word register file | 12,384 |
| offline working set | 576 |
| stack | 32,768 |
| **footprint** | **15,638,058,240** |

At the end of the complete trace both pool extents, every slab slot and every raw stack frame are free. The raw logarithm is `33.8643423348285615749488945331316314313221157186049554972648021821458530859274653723954483`; upward rounding at five decimals gives `33.86435`. No product twiddle table is allocated in C or D, and there is no stored advice.

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
| half gcd frames | 19,200 |
| allocator | 2,048 |
| isolation | 2,048 |
| encoding and output | 4,096 |
| offline generator | 2,048 |
| live call-chain sum | 22,272 |
| rounded 16-KiB reservation | 32,768 |

The offline generator holds sixteen 32-byte field words and one 64-byte digit buffer, exactly `576` bytes. Code/static space is the sum of the emitted block-body, column-body, driver, field, reference, allocator, polynomial-control and literal families stated by the script; no inherited image-size literal is used.

## 8. Evaluation obligations

1. `target_defined`: sections 1 through 3 fix the Orchard P128Pow5T3 target, the 6 selected partial rounds, the input map and the full-field output.
2. `algorithm_defined`: sections 4 and 5 define the line, odd part, Graeffe prefix, exact value-domain powering, half-gcd, root isolation, lift, back-map and final verification.
3. `resources_defined`: sections 4.2, 6, 7 and Appendices E and X enumerate the RAM rules, every search, every operation family and every allocation/free event.
4. `probability_space_defined`: sections 4.1.1 and 9.2 define the fixed target and fresh independent random words.
5. `heuristics_disclosed`: claim.json and sections 9.1 and 9.5 disclose H-ONE and H-NORMAL, their roles, scopes, evidence and limitations. There is no resource heuristic.
6. `evidence_relevant`: section 10 and both manifests bind the unchanged experiments to the line construction, Graeffe pair, normality premise and collision checks.

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

## Appendix E: expanded rows and allocator events

### E.1 Stage C

| event family | operations |
| --- | ---: |
| plans constants tables zero fill allocations | 1,210,840 |
| graeffe prefix and buffer | 471,896,290,286 |
| newton reciprocal | 33,523,874,630 |
| quotient product and copy | 8,504,284,788 |
| g to O1 and O2 | 13,337,361,925 |
| start residue on O2 | 8,257,713,857 |
| A0 extension to O1 | 13,953,695,226 |
| chunked batch inversion | 1,794,510,085 |
| powering steps | 5,836,362,442,790 |
| exit montgomery step | 16,320,528,526 |
| two truncated inverses | 14,570,028,553 |
| entry exit bookkeeping | 1,000 |
| **row C** | **6,418,521,942,506** |

The live middle widths are `(7, 6, 6)`. One middle set is 4,325,198,854; one recovery is 486,539,264; one fused top is 2,175,795,248; a forward and inverse are 6,668,680,292 and 7,285,013,606. A Graeffe step is 19,662,345,374. A bit-zero powering step is 28,387,938,494, and a bit-one step is 28,762,050,750. The exponent scan produces 160 bit-zero and 45 bit-one steps.

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
| 20 | 1,048,576 | 444,976,139 |
| 21 | 2,097,152 | 915,838,777 |
| 22 | 4,194,304 | 1,885,872,743 |
| 23 | 8,388,608 | 4,336,430,887 |
| 24 | 16,777,216 | 8,595,814,997 |
| 25 | 16,866,009 | 16,921,776,151 |
| **Newton reciprocal** | **16,866,009** | **33,523,874,630** |

The quotient product is planned from operand lengths `ell, ell` and output length `2 ell - 1`; no row total is supplied to the planner. Every product candidate is the sum of two forwards, one inverse, input copy/zero loops, its pointwise loop, output loop and fixed allocation/call events.

### E.1.1 Planner keys

| family | exact key | operations |
| --- | --- | ---: |
| apply | `(296, 127, 169, 384)` | 1,414 |
| apply | `(552, 255, 297, 768)` | 1,354 |
| apply | `(808, 255, 553, 1024)` | 1,345 |
| apply | `(1320, 511, 809, 1536)` | 1,315 |
| apply | `(2344, 1023, 1321, 3072)` | 1,255 |
| apply | `(3368, 1023, 2345, 4096)` | 1,225 |
| apply | `(5416, 2047, 3369, 6144)` | 1,195 |
| apply | `(9512, 4095, 5417, 12288)` | 1,135 |
| apply | `(17704, 8191, 9513, 24576)` | 1,096 |
| apply | `(25896, 8191, 17705, 32768)` | 1,066 |
| apply | `(42280, 16383, 25897, 49152)` | 1,036 |
| apply | `(75048, 32767, 42281, 98304)` | 976 |
| apply | `(107816, 32767, 75049, 131072)` | 946 |
| apply | `(173352, 65535, 107817, 196608)` | 916 |
| apply | `(304424, 131071, 173353, 393216)` | 877 |
| apply | `(435496, 131071, 304425, 524288)` | 847 |
| apply | `(697640, 262143, 435497, 786432)` | 817 |
| apply | `(959784, 262143, 697641, 1048576)` | 787 |
| apply | `(1484072, 524287, 959785, 1572864)` | 757 |
| apply | `(2532648, 1048575, 1484073, 3145728)` | 697 |
| apply | `(4629800, 2097151, 2532649, 6291456)` | 658 |
| apply | `(8824104, 4194303, 4629801, 12582912)` | 598 |
| apply | `(13018408, 4194303, 8824105, 16777216)` | 568 |
| apply | `(17212712, 4194303, 13018409, 25165824)` | 538 |
| apply | `(21407016, 4194303, 17212713, 25165824)` | 538 |
| apply | `(25601320, 4194303, 21407017, 33554432)` | 508 |
| apply | `(29795624, 4194303, 25601321, 33554432)` | 508 |
| apply | `(33989928, 4194303, 29795625, 50331648)` | 478 |
| apply | `(38184232, 4194303, 33989929, 50331648)` | 478 |
| apply | `(42378536, 4194303, 38184233, 50331648)` | 478 |
| apply | `(46572840, 4194303, 42378537, 50331648)` | 478 |
| apply | `(50767144, 4194303, 46572841, 67108864)` | 469 |
| apply | `(54961448, 4194303, 50767145, 67108864)` | 469 |
| apply | `(59155752, 4194303, 54961449, 67108864)` | 469 |
| apply | `(63350056, 4194303, 59155753, 67108864)` | 469 |
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
| product | `(4194304, 8388608, 8388608)` | 595 |
| product | `(8388608, 4194304, 8388608)` | 595 |
| product | `(8388608, 16777216, 16777216)` | 535 |
| product | `(16777216, 8388608, 16777216)` | 535 |
| product | `(16777216, 16866009, 16866009)` | 475 |
| product | `(16866009, 16777216, 16866009)` | 475 |
| product | `(16866009, 16866009, 33732017)` | 475 |
| transform | `(201326592,)` | 61 |
| truncated | `(134217728, 122159104, 4, 7, 6, 6, 4)` | 79 |
| **planner total** | | **86,353** |

For each key the script charges key decoding, constructs every admissible transform length, compares each exact charge and stores the selected immutable plan. Block-mode applies have no choice and therefore no planner key.

### E.2 Stage D

The half-gcd node has no percentage allowance. Its fixed 184 operations are the sum shown in section 4.2 and in `NODE_FIXED_EVENTS`. Every other term is a recursive child, a transform row, pointwise row, CRT, pseudo-division or array loop.

| j | children | top | returns | apply | matrix | inverse | CRT | pseudo | arrays | fixed | `node_bf(j)` |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 7 | 210,280 | 25,237 | 35,296 | 6,876 | 9,168 | 32,322 | 3,336 | 2,064 | 3,588 | 184 | 328,351 |
| 8 | 656,702 | 46,671 | 31,208 | 13,692 | 18,256 | 53,232 | 6,664 | 4,112 | 7,172 | 184 | 837,893 |
| 9 | 1,675,786 | 99,103 | 70,056 | 27,324 | 36,432 | 123,762 | 13,320 | 8,208 | 14,340 | 184 | 2,068,515 |
| 10 | 4,137,030 | 189,693 | 128,720 | 54,588 | 72,784 | 221,964 | 26,632 | 16,400 | 28,676 | 184 | 4,876,671 |
| 11 | 9,753,342 | 374,527 | 250,920 | 109,116 | 145,488 | 429,330 | 53,256 | 32,784 | 57,348 | 184 | 11,206,295 |
| 12 | 22,412,590 | 752,457 | 506,336 | 218,172 | 290,896 | 868,848 | 106,504 | 65,552 | 114,692 | 184 | 25,336,231 |
| 13 | 50,672,462 | 1,525,795 | 1,040,472 | 436,284 | 581,712 | 1,800,318 | 213,000 | 131,088 | 229,380 | 184 | 56,630,695 |
| 14 | 113,261,390 | 3,108,381 | 2,156,624 | 872,508 | 1,163,344 | 3,770,988 | 425,992 | 262,160 | 458,756 | 184 | 125,480,327 |
| 15 | 250,960,654 | 6,346,327 | 4,485,960 | 1,744,956 | 2,326,608 | 7,930,650 | 851,976 | 524,304 | 917,508 | 184 | 276,089,127 |
| 16 | 552,178,254 | 14,150,805 | 10,916,080 | 3,489,852 | 4,653,136 | 20,235,750 | 1,703,944 | 1,048,592 | 1,835,012 | 184 | 610,211,609 |
| 17 | 1,220,423,218 | 28,087,375 | 21,546,472 | 6,979,644 | 9,306,192 | 39,828,756 | 3,407,880 | 2,097,168 | 3,670,020 | 184 | 1,335,346,909 |
| 18 | 2,670,693,818 | 56,549,385 | 43,592,416 | 13,959,228 | 18,612,304 | 80,781,378 | 6,815,752 | 4,194,320 | 7,340,036 | 184 | 2,902,538,821 |
| 19 | 5,805,077,642 | 114,652,099 | 89,255,896 | 27,918,396 | 37,224,528 | 166,222,704 | 13,631,496 | 8,388,624 | 14,680,068 | 184 | 6,277,051,637 |
| 20 | 12,554,103,274 | 233,215,869 | 183,727,312 | 55,836,732 | 74,448,976 | 344,180,382 | 27,262,984 | 16,777,232 | 29,360,132 | 184 | 13,518,913,077 |
| 21 | 27,037,826,154 | 475,061,047 | 378,960,328 | 111,673,404 | 148,897,872 | 714,248,652 | 54,525,960 | 33,554,448 | 58,720,260 | 184 | 29,013,468,309 |
| 22 | 58,026,936,618 | 968,187,633 | 782,008,000 | 223,346,748 | 297,795,664 | 1,482,693,882 | 109,051,912 | 67,108,880 | 117,440,516 | 184 | 62,074,570,037 |

The outer driver computes each next degree by subtracting `(2^j-1)+1 = 2^j`; it does not contain a degree table.

| step | degree | j | budget | node | apply plan:points | apply | driver | total |
| ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 122,070,312 | 22 | 4,194,303 | 62,074,570,037 | block:8,388,608 | 56,645,475,942 | 2,031 | 118,720,048,010 |
| 2 | 117,876,008 | 22 | 4,194,303 | 62,074,570,037 | block:8,388,608 | 54,779,451,734 | 2,031 | 116,854,023,802 |
| 3 | 113,681,704 | 22 | 4,194,303 | 62,074,570,037 | block:8,388,608 | 52,913,427,526 | 2,031 | 114,987,999,594 |
| 4 | 109,487,400 | 22 | 4,194,303 | 62,074,570,037 | block:8,388,608 | 51,047,403,318 | 2,031 | 113,121,975,386 |
| 5 | 105,293,096 | 22 | 4,194,303 | 62,074,570,037 | block:8,388,608 | 49,181,379,110 | 2,031 | 111,255,951,178 |
| 6 | 101,098,792 | 22 | 4,194,303 | 62,074,570,037 | block:8,388,608 | 47,315,354,902 | 2,031 | 109,389,926,970 |
| 7 | 96,904,488 | 22 | 4,194,303 | 62,074,570,037 | block:8,388,608 | 45,449,330,694 | 2,031 | 107,523,902,762 |
| 8 | 92,710,184 | 22 | 4,194,303 | 62,074,570,037 | block:8,388,608 | 43,583,306,486 | 2,031 | 105,657,878,554 |
| 9 | 88,515,880 | 22 | 4,194,303 | 62,074,570,037 | block:8,388,608 | 41,717,282,278 | 2,031 | 103,791,854,346 |
| 10 | 84,321,576 | 22 | 4,194,303 | 62,074,570,037 | block:8,388,608 | 39,851,258,070 | 2,031 | 101,925,830,138 |
| 11 | 80,127,272 | 22 | 4,194,303 | 62,074,570,037 | block:8,388,608 | 37,985,233,862 | 2,031 | 100,059,805,930 |
| 12 | 75,932,968 | 22 | 4,194,303 | 62,074,570,037 | block:8,388,608 | 36,119,209,654 | 2,031 | 98,193,781,722 |
| 13 | 71,738,664 | 22 | 4,194,303 | 62,074,570,037 | block:8,388,608 | 34,253,185,446 | 2,031 | 96,327,757,514 |
| 14 | 67,544,360 | 22 | 4,194,303 | 62,074,570,037 | block:8,388,608 | 32,387,161,238 | 2,031 | 94,461,733,306 |
| 15 | 63,350,056 | 22 | 4,194,303 | 62,074,570,037 | direct:67,108,864 | 29,053,900,799 | 2,031 | 91,128,472,867 |
| 16 | 59,155,752 | 22 | 4,194,303 | 62,074,570,037 | direct:67,108,864 | 29,000,423,423 | 2,031 | 91,074,995,491 |
| 17 | 54,961,448 | 22 | 4,194,303 | 62,074,570,037 | direct:67,108,864 | 28,946,946,047 | 2,031 | 91,021,518,115 |
| 18 | 50,767,144 | 22 | 4,194,303 | 62,074,570,037 | direct:67,108,864 | 28,893,468,671 | 2,031 | 90,968,040,739 |
| 19 | 46,572,840 | 22 | 4,194,303 | 62,074,570,037 | direct:50,331,648 | 21,946,985,071 | 2,031 | 84,021,557,139 |
| 20 | 42,378,536 | 22 | 4,194,303 | 62,074,570,037 | direct:50,331,648 | 21,893,507,695 | 2,031 | 83,968,079,763 |
| 21 | 38,184,232 | 22 | 4,194,303 | 62,074,570,037 | direct:50,331,648 | 21,840,030,319 | 2,031 | 83,914,602,387 |
| 22 | 33,989,928 | 22 | 4,194,303 | 62,074,570,037 | direct:50,331,648 | 21,786,552,943 | 2,031 | 83,861,125,011 |
| 23 | 29,795,624 | 22 | 4,194,303 | 62,074,570,037 | direct:33,554,432 | 14,166,217,479 | 2,031 | 76,240,789,547 |
| 24 | 25,601,320 | 22 | 4,194,303 | 62,074,570,037 | direct:33,554,432 | 14,112,740,103 | 2,031 | 76,187,312,171 |
| 25 | 21,407,016 | 22 | 4,194,303 | 62,074,570,037 | direct:25,165,824 | 10,848,328,583 | 2,031 | 72,922,900,651 |
| 26 | 17,212,712 | 22 | 4,194,303 | 62,074,570,037 | direct:25,165,824 | 10,794,851,207 | 2,031 | 72,869,423,275 |
| 27 | 13,018,408 | 22 | 4,194,303 | 62,074,570,037 | direct:16,777,216 | 6,923,701,775 | 2,031 | 68,998,273,843 |
| 28 | 8,824,104 | 22 | 4,194,303 | 62,074,570,037 | direct:12,582,912 | 5,449,993,375 | 2,031 | 67,524,565,443 |
| 29 | 4,629,800 | 21 | 2,097,151 | 29,013,468,309 | direct:6,291,456 | 2,351,315,873 | 2,031 | 31,364,786,213 |
| 30 | 2,532,648 | 20 | 1,048,575 | 13,518,913,077 | direct:3,145,728 | 1,142,303,929 | 2,031 | 14,661,219,037 |
| 31 | 1,484,072 | 19 | 524,287 | 6,277,051,637 | direct:1,572,864 | 556,670,417 | 2,031 | 6,833,724,085 |
| 32 | 959,784 | 18 | 262,143 | 2,902,538,821 | direct:1,048,576 | 359,938,429 | 2,031 | 3,262,479,281 |
| 33 | 697,640 | 18 | 262,143 | 2,902,538,821 | direct:786,432 | 269,946,601 | 2,031 | 3,172,487,453 |
| 34 | 435,496 | 17 | 131,071 | 1,335,346,909 | direct:524,288 | 173,651,077 | 2,031 | 1,509,000,017 |
| 35 | 304,424 | 17 | 131,071 | 1,335,346,909 | direct:393,216 | 131,301,377 | 2,031 | 1,466,650,317 |
| 36 | 173,352 | 16 | 65,535 | 610,211,609 | direct:196,608 | 65,171,737 | 2,031 | 675,385,377 |
| 37 | 107,816 | 15 | 32,767 | 276,089,127 | direct:131,072 | 41,061,013 | 2,031 | 317,152,171 |
| 38 | 75,048 | 15 | 32,767 | 276,089,127 | direct:98,304 | 32,866,865 | 2,031 | 308,958,023 |
| 39 | 42,280 | 14 | 16,383 | 125,480,327 | direct:49,152 | 13,578,547 | 2,031 | 139,060,905 |
| 40 | 25,896 | 13 | 8,191 | 56,630,695 | direct:32,768 | 10,270,885 | 2,031 | 66,903,611 |
| 41 | 17,704 | 13 | 8,191 | 56,630,695 | direct:24,576 | 6,487,115 | 2,031 | 63,119,841 |
| 42 | 9,512 | 12 | 4,095 | 25,336,231 | direct:12,288 | 3,139,171 | 2,031 | 28,477,433 |
| 43 | 5,416 | 11 | 2,047 | 11,206,295 | direct:6,144 | 1,537,019 | 2,031 | 12,745,345 |
| 44 | 3,368 | 10 | 1,023 | 4,876,671 | direct:4,096 | 962,827 | 2,031 | 5,841,529 |
| 45 | 2,344 | 10 | 1,023 | 4,876,671 | direct:3,072 | 757,843 | 2,031 | 5,636,545 |
| 46 | 1,320 | 9 | 511 | 2,068,515 | direct:1,536 | 391,307 | 2,031 | 2,461,853 |
| 47 | 808 | 8 | 255 | 837,893 | direct:1,024 | 232,219 | 2,031 | 1,072,143 |
| 48 | 552 | 8 | 255 | 837,893 | direct:768 | 212,083 | 2,031 | 1,052,007 |
| 49 | 296 | 7 | 127 | 328,351 | direct:384 | 95,549 | 2,031 | 425,931 |

| part | operations |
| --- | ---: |
| 49 outer steps | 2,690,872,764,771 |
| classical Euclid from degree 168 | 231,672 |
| normalization | 2,653 |
| entry | 1,012 |
| exit and frees | 317 |
| **row D** | **2,690,873,000,425** |

### E.3 Event-by-event allocation walk

The complete trace in E.4 contains every pool, slab, stack and fixed-reservation event; it is not duplicated here.

The maximum extent sum in the table is 15,637,537,472 bytes. Adding the middle gap and both slab regions gives 15,637,548,864 bytes. The fixed regions then give 15,638,058,240 bytes.



### E.4 Complete resident-object trace

This is the sole trace used for the memory endpoint. Fixed reservations occur
first; every later pool, slab and stack-lifetime event reports the total
resident bytes including those fixed regions.

| # | stage | action | object or chain | region | bytes | total resident bytes |
| ---: | --- | --- | --- | --- | ---: | ---: |
| 1 | fixed | reserve | code-and-static | fixed | 463,648 | 463,648 |
| 2 | fixed | reserve | register-file | fixed | 12,384 | 476,032 |
| 3 | fixed | reserve | offline-workspace | fixed | 576 | 476,608 |
| 4 | fixed | reserve | stack-reservation | fixed | 32,768 | 509,376 |
| 5 | fixed | reserve | arena-middle-gap | fixed | 128 | 509,504 |
| 6 | fixed | reserve | slab-class-reservations | fixed | 11,136 | 520,640 |
| 7 | fixed | reserve | slab-free-list-heads | fixed | 128 | 520,768 |
| 8 | A | alloc | A-g | H | 3,909,091,392 | 3,909,612,160 |
| 9 | A | free | A-g | H | 3,909,091,392 | 520,768 |
| 10 | B | alloc | B-values | H | 6,442,451,008 | 6,442,971,776 |
| 11 | B | alloc | B-table | H | 3,221,225,536 | 9,664,197,312 |
| 12 | B | alloc | g | L | 3,909,091,392 | 13,573,288,704 |
| 13 | B | free | B-table | H | 3,221,225,536 | 10,352,063,168 |
| 14 | B | free | B-values | H | 6,442,451,008 | 3,909,612,160 |
| 15 | C | alloc | root-tables | L | 532,800 | 3,910,144,960 |
| 16 | C | alloc | graeffe-E | L | 3,909,091,392 | 7,819,236,352 |
| 17 | C | alloc | graeffe-O | H | 3,909,091,392 | 11,728,327,744 |
| 18 | C | alloc | graeffe-batch | H | 376,896 | 11,728,704,640 |
| 19 | C | free | graeffe-batch | H | 376,896 | 11,728,327,744 |
| 20 | C | free | graeffe-O | H | 3,909,091,392 | 7,819,236,352 |
| 21 | C | free | graeffe-E | L | 3,909,091,392 | 3,910,144,960 |
| 22 | C | alloc | newton-reversed | L | 539,712,384 | 4,449,857,344 |
| 23 | C | alloc | newton-reciprocal | L | 539,712,384 | 4,989,569,728 |
| 24 | C | alloc | newton-scratch | H | 539,712,384 | 5,529,282,112 |
| 25 | C | alloc | newton-transform | H | 1,610,612,800 | 7,139,894,912 |
| 26 | C | free | newton-transform | H | 1,610,612,800 | 5,529,282,112 |
| 27 | C | free | newton-scratch | H | 539,712,384 | 4,989,569,728 |
| 28 | C | alloc | quotient-output | H | 539,712,384 | 5,529,282,112 |
| 29 | C | alloc | quotient-transform | H | 1,610,612,800 | 7,139,894,912 |
| 30 | C | free | quotient-transform | H | 1,610,612,800 | 5,529,282,112 |
| 31 | C | free | newton-reciprocal | L | 539,712,384 | 4,989,569,728 |
| 32 | C | free | newton-reversed | L | 539,712,384 | 4,449,857,344 |
| 33 | C | alloc | A-O2 | L | 3,909,091,392 | 8,358,948,736 |
| 34 | C | free | quotient-output | H | 539,712,384 | 7,819,236,352 |
| 35 | C | alloc | k1-O1 | L | 3,909,091,392 | 11,728,327,744 |
| 36 | C | alloc | A-O1 | H | 3,909,091,392 | 15,637,419,136 |
| 37 | C | alloc | batch | H | 376,896 | 15,637,796,032 |
| 38 | C | alloc | batch-inversion-prefix | L | 262,208 | 15,638,058,240 |
| 39 | C | free | batch-inversion-prefix | L | 262,208 | 15,637,796,032 |
| 40 | C | free | batch | H | 376,896 | 15,637,419,136 |
| 41 | C | free | k1-O1 | L | 3,909,091,392 | 11,728,327,744 |
| 42 | C | free | A-O2 | L | 3,909,091,392 | 7,819,236,352 |
| 43 | D | alloc | D1-node | L | 2,147,475,520 | 9,966,711,872 |
| 44 | D | free | D1-node | L | 2,147,475,520 | 7,819,236,352 |
| 45 | D | alloc | D1-matrix | L | 536,870,976 | 8,356,107,328 |
| 46 | D | alloc | D1-row-a | H | 536,870,976 | 8,892,978,304 |
| 47 | D | alloc | D1-row-b | H | 536,870,976 | 9,429,849,280 |
| 48 | D | alloc | D1-accumulator | L | 1,610,612,800 | 11,040,462,080 |
| 49 | D | alloc | D1-overlap | L | 536,870,976 | 11,577,333,056 |
| 50 | D | free | D1-overlap | L | 536,870,976 | 11,040,462,080 |
| 51 | D | free | D1-accumulator | L | 1,610,612,800 | 9,429,849,280 |
| 52 | D | free | D1-row-b | H | 536,870,976 | 8,892,978,304 |
| 53 | D | free | D1-row-a | H | 536,870,976 | 8,356,107,328 |
| 54 | D | free | D1-matrix | L | 536,870,976 | 7,819,236,352 |
| 55 | D | alloc | D2-node | L | 2,147,475,520 | 9,966,711,872 |
| 56 | D | free | D2-node | L | 2,147,475,520 | 7,819,236,352 |
| 57 | D | alloc | D2-matrix | L | 536,870,976 | 8,356,107,328 |
| 58 | D | alloc | D2-row-a | H | 536,870,976 | 8,892,978,304 |
| 59 | D | alloc | D2-row-b | H | 536,870,976 | 9,429,849,280 |
| 60 | D | alloc | D2-accumulator | L | 1,610,612,800 | 11,040,462,080 |
| 61 | D | alloc | D2-overlap | L | 536,870,976 | 11,577,333,056 |
| 62 | D | free | D2-overlap | L | 536,870,976 | 11,040,462,080 |
| 63 | D | free | D2-accumulator | L | 1,610,612,800 | 9,429,849,280 |
| 64 | D | free | D2-row-b | H | 536,870,976 | 8,892,978,304 |
| 65 | D | free | D2-row-a | H | 536,870,976 | 8,356,107,328 |
| 66 | D | free | D2-matrix | L | 536,870,976 | 7,819,236,352 |
| 67 | D | alloc | D3-node | L | 2,147,475,520 | 9,966,711,872 |
| 68 | D | free | D3-node | L | 2,147,475,520 | 7,819,236,352 |
| 69 | D | alloc | D3-matrix | L | 536,870,976 | 8,356,107,328 |
| 70 | D | alloc | D3-row-a | H | 536,870,976 | 8,892,978,304 |
| 71 | D | alloc | D3-row-b | H | 536,870,976 | 9,429,849,280 |
| 72 | D | alloc | D3-accumulator | L | 1,610,612,800 | 11,040,462,080 |
| 73 | D | alloc | D3-overlap | L | 536,870,976 | 11,577,333,056 |
| 74 | D | free | D3-overlap | L | 536,870,976 | 11,040,462,080 |
| 75 | D | free | D3-accumulator | L | 1,610,612,800 | 9,429,849,280 |
| 76 | D | free | D3-row-b | H | 536,870,976 | 8,892,978,304 |
| 77 | D | free | D3-row-a | H | 536,870,976 | 8,356,107,328 |
| 78 | D | free | D3-matrix | L | 536,870,976 | 7,819,236,352 |
| 79 | D | alloc | D4-node | L | 2,147,475,520 | 9,966,711,872 |
| 80 | D | free | D4-node | L | 2,147,475,520 | 7,819,236,352 |
| 81 | D | alloc | D4-matrix | L | 536,870,976 | 8,356,107,328 |
| 82 | D | alloc | D4-row-a | H | 536,870,976 | 8,892,978,304 |
| 83 | D | alloc | D4-row-b | H | 536,870,976 | 9,429,849,280 |
| 84 | D | alloc | D4-accumulator | L | 1,610,612,800 | 11,040,462,080 |
| 85 | D | alloc | D4-overlap | L | 536,870,976 | 11,577,333,056 |
| 86 | D | free | D4-overlap | L | 536,870,976 | 11,040,462,080 |
| 87 | D | free | D4-accumulator | L | 1,610,612,800 | 9,429,849,280 |
| 88 | D | free | D4-row-b | H | 536,870,976 | 8,892,978,304 |
| 89 | D | free | D4-row-a | H | 536,870,976 | 8,356,107,328 |
| 90 | D | free | D4-matrix | L | 536,870,976 | 7,819,236,352 |
| 91 | D | alloc | D5-node | L | 2,147,475,520 | 9,966,711,872 |
| 92 | D | free | D5-node | L | 2,147,475,520 | 7,819,236,352 |
| 93 | D | alloc | D5-matrix | L | 536,870,976 | 8,356,107,328 |
| 94 | D | alloc | D5-row-a | H | 536,870,976 | 8,892,978,304 |
| 95 | D | alloc | D5-row-b | H | 536,870,976 | 9,429,849,280 |
| 96 | D | alloc | D5-accumulator | L | 1,610,612,800 | 11,040,462,080 |
| 97 | D | alloc | D5-overlap | L | 536,870,976 | 11,577,333,056 |
| 98 | D | free | D5-overlap | L | 536,870,976 | 11,040,462,080 |
| 99 | D | free | D5-accumulator | L | 1,610,612,800 | 9,429,849,280 |
| 100 | D | free | D5-row-b | H | 536,870,976 | 8,892,978,304 |
| 101 | D | free | D5-row-a | H | 536,870,976 | 8,356,107,328 |
| 102 | D | free | D5-matrix | L | 536,870,976 | 7,819,236,352 |
| 103 | D | alloc | D6-node | L | 2,147,475,520 | 9,966,711,872 |
| 104 | D | free | D6-node | L | 2,147,475,520 | 7,819,236,352 |
| 105 | D | alloc | D6-matrix | L | 536,870,976 | 8,356,107,328 |
| 106 | D | alloc | D6-row-a | H | 536,870,976 | 8,892,978,304 |
| 107 | D | alloc | D6-row-b | H | 536,870,976 | 9,429,849,280 |
| 108 | D | alloc | D6-accumulator | L | 1,610,612,800 | 11,040,462,080 |
| 109 | D | alloc | D6-overlap | L | 536,870,976 | 11,577,333,056 |
| 110 | D | free | D6-overlap | L | 536,870,976 | 11,040,462,080 |
| 111 | D | free | D6-accumulator | L | 1,610,612,800 | 9,429,849,280 |
| 112 | D | free | D6-row-b | H | 536,870,976 | 8,892,978,304 |
| 113 | D | free | D6-row-a | H | 536,870,976 | 8,356,107,328 |
| 114 | D | free | D6-matrix | L | 536,870,976 | 7,819,236,352 |
| 115 | D | alloc | D7-node | L | 2,147,475,520 | 9,966,711,872 |
| 116 | D | free | D7-node | L | 2,147,475,520 | 7,819,236,352 |
| 117 | D | alloc | D7-matrix | L | 536,870,976 | 8,356,107,328 |
| 118 | D | alloc | D7-row-a | H | 536,870,976 | 8,892,978,304 |
| 119 | D | alloc | D7-row-b | H | 536,870,976 | 9,429,849,280 |
| 120 | D | alloc | D7-accumulator | L | 1,610,612,800 | 11,040,462,080 |
| 121 | D | alloc | D7-overlap | L | 536,870,976 | 11,577,333,056 |
| 122 | D | free | D7-overlap | L | 536,870,976 | 11,040,462,080 |
| 123 | D | free | D7-accumulator | L | 1,610,612,800 | 9,429,849,280 |
| 124 | D | free | D7-row-b | H | 536,870,976 | 8,892,978,304 |
| 125 | D | free | D7-row-a | H | 536,870,976 | 8,356,107,328 |
| 126 | D | free | D7-matrix | L | 536,870,976 | 7,819,236,352 |
| 127 | D | alloc | D8-node | L | 2,147,475,520 | 9,966,711,872 |
| 128 | D | free | D8-node | L | 2,147,475,520 | 7,819,236,352 |
| 129 | D | alloc | D8-matrix | L | 536,870,976 | 8,356,107,328 |
| 130 | D | alloc | D8-row-a | H | 536,870,976 | 8,892,978,304 |
| 131 | D | alloc | D8-row-b | H | 536,870,976 | 9,429,849,280 |
| 132 | D | alloc | D8-accumulator | L | 1,610,612,800 | 11,040,462,080 |
| 133 | D | alloc | D8-overlap | L | 536,870,976 | 11,577,333,056 |
| 134 | D | free | D8-overlap | L | 536,870,976 | 11,040,462,080 |
| 135 | D | free | D8-accumulator | L | 1,610,612,800 | 9,429,849,280 |
| 136 | D | free | D8-row-b | H | 536,870,976 | 8,892,978,304 |
| 137 | D | free | D8-row-a | H | 536,870,976 | 8,356,107,328 |
| 138 | D | free | D8-matrix | L | 536,870,976 | 7,819,236,352 |
| 139 | D | alloc | D9-node | L | 2,147,475,520 | 9,966,711,872 |
| 140 | D | free | D9-node | L | 2,147,475,520 | 7,819,236,352 |
| 141 | D | alloc | D9-matrix | L | 536,870,976 | 8,356,107,328 |
| 142 | D | alloc | D9-row-a | H | 536,870,976 | 8,892,978,304 |
| 143 | D | alloc | D9-row-b | H | 536,870,976 | 9,429,849,280 |
| 144 | D | alloc | D9-accumulator | L | 1,610,612,800 | 11,040,462,080 |
| 145 | D | alloc | D9-overlap | L | 536,870,976 | 11,577,333,056 |
| 146 | D | free | D9-overlap | L | 536,870,976 | 11,040,462,080 |
| 147 | D | free | D9-accumulator | L | 1,610,612,800 | 9,429,849,280 |
| 148 | D | free | D9-row-b | H | 536,870,976 | 8,892,978,304 |
| 149 | D | free | D9-row-a | H | 536,870,976 | 8,356,107,328 |
| 150 | D | free | D9-matrix | L | 536,870,976 | 7,819,236,352 |
| 151 | D | alloc | D10-node | L | 2,147,475,520 | 9,966,711,872 |
| 152 | D | free | D10-node | L | 2,147,475,520 | 7,819,236,352 |
| 153 | D | alloc | D10-matrix | L | 536,870,976 | 8,356,107,328 |
| 154 | D | alloc | D10-row-a | H | 536,870,976 | 8,892,978,304 |
| 155 | D | alloc | D10-row-b | H | 536,870,976 | 9,429,849,280 |
| 156 | D | alloc | D10-accumulator | L | 1,610,612,800 | 11,040,462,080 |
| 157 | D | alloc | D10-overlap | L | 536,870,976 | 11,577,333,056 |
| 158 | D | free | D10-overlap | L | 536,870,976 | 11,040,462,080 |
| 159 | D | free | D10-accumulator | L | 1,610,612,800 | 9,429,849,280 |
| 160 | D | free | D10-row-b | H | 536,870,976 | 8,892,978,304 |
| 161 | D | free | D10-row-a | H | 536,870,976 | 8,356,107,328 |
| 162 | D | free | D10-matrix | L | 536,870,976 | 7,819,236,352 |
| 163 | D | alloc | D11-node | L | 2,147,475,520 | 9,966,711,872 |
| 164 | D | free | D11-node | L | 2,147,475,520 | 7,819,236,352 |
| 165 | D | alloc | D11-matrix | L | 536,870,976 | 8,356,107,328 |
| 166 | D | alloc | D11-row-a | H | 536,870,976 | 8,892,978,304 |
| 167 | D | alloc | D11-row-b | H | 536,870,976 | 9,429,849,280 |
| 168 | D | alloc | D11-accumulator | L | 1,610,612,800 | 11,040,462,080 |
| 169 | D | alloc | D11-overlap | L | 536,870,976 | 11,577,333,056 |
| 170 | D | free | D11-overlap | L | 536,870,976 | 11,040,462,080 |
| 171 | D | free | D11-accumulator | L | 1,610,612,800 | 9,429,849,280 |
| 172 | D | free | D11-row-b | H | 536,870,976 | 8,892,978,304 |
| 173 | D | free | D11-row-a | H | 536,870,976 | 8,356,107,328 |
| 174 | D | free | D11-matrix | L | 536,870,976 | 7,819,236,352 |
| 175 | D | alloc | D12-node | L | 2,147,475,520 | 9,966,711,872 |
| 176 | D | free | D12-node | L | 2,147,475,520 | 7,819,236,352 |
| 177 | D | alloc | D12-matrix | L | 536,870,976 | 8,356,107,328 |
| 178 | D | alloc | D12-row-a | H | 536,870,976 | 8,892,978,304 |
| 179 | D | alloc | D12-row-b | H | 536,870,976 | 9,429,849,280 |
| 180 | D | alloc | D12-accumulator | L | 1,610,612,800 | 11,040,462,080 |
| 181 | D | alloc | D12-overlap | L | 536,870,976 | 11,577,333,056 |
| 182 | D | free | D12-overlap | L | 536,870,976 | 11,040,462,080 |
| 183 | D | free | D12-accumulator | L | 1,610,612,800 | 9,429,849,280 |
| 184 | D | free | D12-row-b | H | 536,870,976 | 8,892,978,304 |
| 185 | D | free | D12-row-a | H | 536,870,976 | 8,356,107,328 |
| 186 | D | free | D12-matrix | L | 536,870,976 | 7,819,236,352 |
| 187 | D | alloc | D13-node | L | 2,147,475,520 | 9,966,711,872 |
| 188 | D | free | D13-node | L | 2,147,475,520 | 7,819,236,352 |
| 189 | D | alloc | D13-matrix | L | 536,870,976 | 8,356,107,328 |
| 190 | D | alloc | D13-row-a | H | 536,870,976 | 8,892,978,304 |
| 191 | D | alloc | D13-row-b | H | 536,870,976 | 9,429,849,280 |
| 192 | D | alloc | D13-accumulator | L | 1,610,612,800 | 11,040,462,080 |
| 193 | D | alloc | D13-overlap | L | 536,870,976 | 11,577,333,056 |
| 194 | D | free | D13-overlap | L | 536,870,976 | 11,040,462,080 |
| 195 | D | free | D13-accumulator | L | 1,610,612,800 | 9,429,849,280 |
| 196 | D | free | D13-row-b | H | 536,870,976 | 8,892,978,304 |
| 197 | D | free | D13-row-a | H | 536,870,976 | 8,356,107,328 |
| 198 | D | free | D13-matrix | L | 536,870,976 | 7,819,236,352 |
| 199 | D | alloc | D14-node | L | 2,147,475,520 | 9,966,711,872 |
| 200 | D | free | D14-node | L | 2,147,475,520 | 7,819,236,352 |
| 201 | D | alloc | D14-matrix | L | 536,870,976 | 8,356,107,328 |
| 202 | D | alloc | D14-row-a | H | 536,870,976 | 8,892,978,304 |
| 203 | D | alloc | D14-row-b | H | 536,870,976 | 9,429,849,280 |
| 204 | D | alloc | D14-accumulator | L | 1,610,612,800 | 11,040,462,080 |
| 205 | D | alloc | D14-overlap | L | 536,870,976 | 11,577,333,056 |
| 206 | D | free | D14-overlap | L | 536,870,976 | 11,040,462,080 |
| 207 | D | free | D14-accumulator | L | 1,610,612,800 | 9,429,849,280 |
| 208 | D | free | D14-row-b | H | 536,870,976 | 8,892,978,304 |
| 209 | D | free | D14-row-a | H | 536,870,976 | 8,356,107,328 |
| 210 | D | free | D14-matrix | L | 536,870,976 | 7,819,236,352 |
| 211 | D | alloc | D15-node | L | 2,147,475,520 | 9,966,711,872 |
| 212 | D | free | D15-node | L | 2,147,475,520 | 7,819,236,352 |
| 213 | D | shrink | g | L | 2,147,483,712 | 7,819,236,352 |
| 214 | D | shrink | A-O1 | H | 2,147,483,712 | 6,057,628,672 |
| 215 | D | alloc | D15-forward-1 | L | 2,147,483,712 | 8,205,112,384 |
| 216 | D | alloc | D15-forward-2 | H | 2,147,483,712 | 10,352,596,096 |
| 217 | D | alloc | D15-forward-3 | L | 2,147,483,712 | 12,500,079,808 |
| 218 | D | alloc | D15-forward-4 | H | 2,147,483,712 | 14,647,563,520 |
| 219 | D | retain | D15-forward-5 | L | 2,147,483,712 | 14,647,563,520 |
| 220 | D | retain | D15-forward-6 | H | 2,147,483,712 | 14,647,563,520 |
| 221 | D | release-retained | D15-forward-6 | H | 2,147,483,712 | 14,647,563,520 |
| 222 | D | release-retained | D15-forward-5 | L | 2,147,483,712 | 14,647,563,520 |
| 223 | D | free | D15-forward-4 | H | 2,147,483,712 | 12,500,079,808 |
| 224 | D | free | D15-forward-3 | L | 2,147,483,712 | 10,352,596,096 |
| 225 | D | free | D15-forward-2 | H | 2,147,483,712 | 8,205,112,384 |
| 226 | D | free | D15-forward-1 | L | 2,147,483,712 | 6,057,628,672 |
| 227 | D | alloc | D16-node | L | 2,147,475,520 | 8,205,104,192 |
| 228 | D | free | D16-node | L | 2,147,475,520 | 6,057,628,672 |
| 229 | D | shrink | g | L | 2,147,483,712 | 6,057,628,672 |
| 230 | D | shrink | A-O1 | H | 2,147,483,712 | 6,057,628,672 |
| 231 | D | alloc | D16-forward-1 | L | 2,147,483,712 | 8,205,112,384 |
| 232 | D | alloc | D16-forward-2 | H | 2,147,483,712 | 10,352,596,096 |
| 233 | D | alloc | D16-forward-3 | L | 2,147,483,712 | 12,500,079,808 |
| 234 | D | alloc | D16-forward-4 | H | 2,147,483,712 | 14,647,563,520 |
| 235 | D | retain | D16-forward-5 | L | 2,147,483,712 | 14,647,563,520 |
| 236 | D | retain | D16-forward-6 | H | 2,147,483,712 | 14,647,563,520 |
| 237 | D | release-retained | D16-forward-6 | H | 2,147,483,712 | 14,647,563,520 |
| 238 | D | release-retained | D16-forward-5 | L | 2,147,483,712 | 14,647,563,520 |
| 239 | D | free | D16-forward-4 | H | 2,147,483,712 | 12,500,079,808 |
| 240 | D | free | D16-forward-3 | L | 2,147,483,712 | 10,352,596,096 |
| 241 | D | free | D16-forward-2 | H | 2,147,483,712 | 8,205,112,384 |
| 242 | D | free | D16-forward-1 | L | 2,147,483,712 | 6,057,628,672 |
| 243 | D | alloc | D17-node | L | 2,147,475,520 | 8,205,104,192 |
| 244 | D | free | D17-node | L | 2,147,475,520 | 6,057,628,672 |
| 245 | D | shrink | g | L | 2,147,483,712 | 6,057,628,672 |
| 246 | D | shrink | A-O1 | H | 2,147,483,712 | 6,057,628,672 |
| 247 | D | alloc | D17-forward-1 | L | 2,147,483,712 | 8,205,112,384 |
| 248 | D | alloc | D17-forward-2 | H | 2,147,483,712 | 10,352,596,096 |
| 249 | D | alloc | D17-forward-3 | L | 2,147,483,712 | 12,500,079,808 |
| 250 | D | alloc | D17-forward-4 | H | 2,147,483,712 | 14,647,563,520 |
| 251 | D | retain | D17-forward-5 | L | 2,147,483,712 | 14,647,563,520 |
| 252 | D | retain | D17-forward-6 | H | 2,147,483,712 | 14,647,563,520 |
| 253 | D | release-retained | D17-forward-6 | H | 2,147,483,712 | 14,647,563,520 |
| 254 | D | release-retained | D17-forward-5 | L | 2,147,483,712 | 14,647,563,520 |
| 255 | D | free | D17-forward-4 | H | 2,147,483,712 | 12,500,079,808 |
| 256 | D | free | D17-forward-3 | L | 2,147,483,712 | 10,352,596,096 |
| 257 | D | free | D17-forward-2 | H | 2,147,483,712 | 8,205,112,384 |
| 258 | D | free | D17-forward-1 | L | 2,147,483,712 | 6,057,628,672 |
| 259 | D | alloc | D18-node | L | 2,147,475,520 | 8,205,104,192 |
| 260 | D | free | D18-node | L | 2,147,475,520 | 6,057,628,672 |
| 261 | D | shrink | g | L | 2,147,483,712 | 6,057,628,672 |
| 262 | D | shrink | A-O1 | H | 2,147,483,712 | 6,057,628,672 |
| 263 | D | alloc | D18-forward-1 | L | 2,147,483,712 | 8,205,112,384 |
| 264 | D | alloc | D18-forward-2 | H | 2,147,483,712 | 10,352,596,096 |
| 265 | D | alloc | D18-forward-3 | L | 2,147,483,712 | 12,500,079,808 |
| 266 | D | alloc | D18-forward-4 | H | 2,147,483,712 | 14,647,563,520 |
| 267 | D | retain | D18-forward-5 | L | 2,147,483,712 | 14,647,563,520 |
| 268 | D | retain | D18-forward-6 | H | 2,147,483,712 | 14,647,563,520 |
| 269 | D | release-retained | D18-forward-6 | H | 2,147,483,712 | 14,647,563,520 |
| 270 | D | release-retained | D18-forward-5 | L | 2,147,483,712 | 14,647,563,520 |
| 271 | D | free | D18-forward-4 | H | 2,147,483,712 | 12,500,079,808 |
| 272 | D | free | D18-forward-3 | L | 2,147,483,712 | 10,352,596,096 |
| 273 | D | free | D18-forward-2 | H | 2,147,483,712 | 8,205,112,384 |
| 274 | D | free | D18-forward-1 | L | 2,147,483,712 | 6,057,628,672 |
| 275 | D | alloc | D19-node | L | 2,147,475,520 | 8,205,104,192 |
| 276 | D | free | D19-node | L | 2,147,475,520 | 6,057,628,672 |
| 277 | D | shrink | g | L | 1,610,612,800 | 6,057,628,672 |
| 278 | D | shrink | A-O1 | H | 1,610,612,800 | 5,520,757,760 |
| 279 | D | alloc | D19-forward-1 | L | 1,610,612,800 | 5,520,757,760 |
| 280 | D | alloc | D19-forward-2 | H | 1,610,612,800 | 7,131,370,560 |
| 281 | D | alloc | D19-forward-3 | L | 1,610,612,800 | 8,741,983,360 |
| 282 | D | alloc | D19-forward-4 | H | 1,610,612,800 | 10,352,596,160 |
| 283 | D | retain | D19-forward-5 | L | 1,610,612,800 | 10,352,596,160 |
| 284 | D | retain | D19-forward-6 | H | 1,610,612,800 | 10,352,596,160 |
| 285 | D | release-retained | D19-forward-6 | H | 1,610,612,800 | 10,352,596,160 |
| 286 | D | release-retained | D19-forward-5 | L | 1,610,612,800 | 10,352,596,160 |
| 287 | D | free | D19-forward-4 | H | 1,610,612,800 | 8,741,983,360 |
| 288 | D | free | D19-forward-3 | L | 1,610,612,800 | 7,131,370,560 |
| 289 | D | free | D19-forward-2 | H | 1,610,612,800 | 5,520,757,760 |
| 290 | D | free | D19-forward-1 | L | 1,610,612,800 | 5,520,757,760 |
| 291 | D | alloc | D20-node | L | 2,147,475,520 | 5,520,757,760 |
| 292 | D | free | D20-node | L | 2,147,475,520 | 5,520,757,760 |
| 293 | D | shrink | g | L | 1,610,612,800 | 5,520,757,760 |
| 294 | D | shrink | A-O1 | H | 1,610,612,800 | 5,520,757,760 |
| 295 | D | alloc | D20-forward-1 | L | 1,610,612,800 | 5,520,757,760 |
| 296 | D | alloc | D20-forward-2 | H | 1,610,612,800 | 7,131,370,560 |
| 297 | D | alloc | D20-forward-3 | L | 1,610,612,800 | 8,741,983,360 |
| 298 | D | alloc | D20-forward-4 | H | 1,610,612,800 | 10,352,596,160 |
| 299 | D | retain | D20-forward-5 | L | 1,610,612,800 | 10,352,596,160 |
| 300 | D | retain | D20-forward-6 | H | 1,610,612,800 | 10,352,596,160 |
| 301 | D | release-retained | D20-forward-6 | H | 1,610,612,800 | 10,352,596,160 |
| 302 | D | release-retained | D20-forward-5 | L | 1,610,612,800 | 10,352,596,160 |
| 303 | D | free | D20-forward-4 | H | 1,610,612,800 | 8,741,983,360 |
| 304 | D | free | D20-forward-3 | L | 1,610,612,800 | 7,131,370,560 |
| 305 | D | free | D20-forward-2 | H | 1,610,612,800 | 5,520,757,760 |
| 306 | D | free | D20-forward-1 | L | 1,610,612,800 | 5,520,757,760 |
| 307 | D | alloc | D21-node | L | 2,147,475,520 | 5,520,757,760 |
| 308 | D | free | D21-node | L | 2,147,475,520 | 5,520,757,760 |
| 309 | D | shrink | g | L | 1,610,612,800 | 5,520,757,760 |
| 310 | D | shrink | A-O1 | H | 1,610,612,800 | 5,520,757,760 |
| 311 | D | alloc | D21-forward-1 | L | 1,610,612,800 | 5,520,757,760 |
| 312 | D | alloc | D21-forward-2 | H | 1,610,612,800 | 7,131,370,560 |
| 313 | D | alloc | D21-forward-3 | L | 1,610,612,800 | 8,741,983,360 |
| 314 | D | alloc | D21-forward-4 | H | 1,610,612,800 | 10,352,596,160 |
| 315 | D | retain | D21-forward-5 | L | 1,610,612,800 | 10,352,596,160 |
| 316 | D | retain | D21-forward-6 | H | 1,610,612,800 | 10,352,596,160 |
| 317 | D | release-retained | D21-forward-6 | H | 1,610,612,800 | 10,352,596,160 |
| 318 | D | release-retained | D21-forward-5 | L | 1,610,612,800 | 10,352,596,160 |
| 319 | D | free | D21-forward-4 | H | 1,610,612,800 | 8,741,983,360 |
| 320 | D | free | D21-forward-3 | L | 1,610,612,800 | 7,131,370,560 |
| 321 | D | free | D21-forward-2 | H | 1,610,612,800 | 5,520,757,760 |
| 322 | D | free | D21-forward-1 | L | 1,610,612,800 | 5,520,757,760 |
| 323 | D | alloc | D22-node | L | 2,147,475,520 | 5,520,757,760 |
| 324 | D | free | D22-node | L | 2,147,475,520 | 5,520,757,760 |
| 325 | D | shrink | g | L | 1,610,612,800 | 5,520,757,760 |
| 326 | D | shrink | A-O1 | H | 1,610,612,800 | 5,520,757,760 |
| 327 | D | alloc | D22-forward-1 | L | 1,610,612,800 | 5,520,757,760 |
| 328 | D | alloc | D22-forward-2 | H | 1,610,612,800 | 7,131,370,560 |
| 329 | D | alloc | D22-forward-3 | L | 1,610,612,800 | 8,741,983,360 |
| 330 | D | alloc | D22-forward-4 | H | 1,610,612,800 | 10,352,596,160 |
| 331 | D | retain | D22-forward-5 | L | 1,610,612,800 | 10,352,596,160 |
| 332 | D | retain | D22-forward-6 | H | 1,610,612,800 | 10,352,596,160 |
| 333 | D | release-retained | D22-forward-6 | H | 1,610,612,800 | 10,352,596,160 |
| 334 | D | release-retained | D22-forward-5 | L | 1,610,612,800 | 10,352,596,160 |
| 335 | D | free | D22-forward-4 | H | 1,610,612,800 | 8,741,983,360 |
| 336 | D | free | D22-forward-3 | L | 1,610,612,800 | 7,131,370,560 |
| 337 | D | free | D22-forward-2 | H | 1,610,612,800 | 5,520,757,760 |
| 338 | D | free | D22-forward-1 | L | 1,610,612,800 | 5,520,757,760 |
| 339 | D | alloc | D23-node | L | 2,147,475,520 | 5,520,757,760 |
| 340 | D | free | D23-node | L | 2,147,475,520 | 5,520,757,760 |
| 341 | D | shrink | g | L | 1,073,741,888 | 5,520,757,760 |
| 342 | D | shrink | A-O1 | H | 1,073,741,888 | 4,983,886,848 |
| 343 | D | alloc | D23-forward-1 | L | 1,073,741,888 | 4,983,886,848 |
| 344 | D | alloc | D23-forward-2 | H | 1,073,741,888 | 6,057,628,736 |
| 345 | D | alloc | D23-forward-3 | L | 1,073,741,888 | 6,057,628,736 |
| 346 | D | alloc | D23-forward-4 | H | 1,073,741,888 | 7,131,370,624 |
| 347 | D | retain | D23-forward-5 | L | 1,073,741,888 | 7,131,370,624 |
| 348 | D | retain | D23-forward-6 | H | 1,073,741,888 | 7,131,370,624 |
| 349 | D | release-retained | D23-forward-6 | H | 1,073,741,888 | 7,131,370,624 |
| 350 | D | release-retained | D23-forward-5 | L | 1,073,741,888 | 7,131,370,624 |
| 351 | D | free | D23-forward-4 | H | 1,073,741,888 | 6,057,628,736 |
| 352 | D | free | D23-forward-3 | L | 1,073,741,888 | 6,057,628,736 |
| 353 | D | free | D23-forward-2 | H | 1,073,741,888 | 4,983,886,848 |
| 354 | D | free | D23-forward-1 | L | 1,073,741,888 | 4,983,886,848 |
| 355 | D | alloc | D24-node | L | 2,147,475,520 | 4,983,886,848 |
| 356 | D | free | D24-node | L | 2,147,475,520 | 4,983,886,848 |
| 357 | D | shrink | g | L | 1,073,741,888 | 4,983,886,848 |
| 358 | D | shrink | A-O1 | H | 1,073,741,888 | 4,983,886,848 |
| 359 | D | alloc | D24-forward-1 | L | 1,073,741,888 | 4,983,886,848 |
| 360 | D | alloc | D24-forward-2 | H | 1,073,741,888 | 6,057,628,736 |
| 361 | D | alloc | D24-forward-3 | L | 1,073,741,888 | 6,057,628,736 |
| 362 | D | alloc | D24-forward-4 | H | 1,073,741,888 | 7,131,370,624 |
| 363 | D | retain | D24-forward-5 | L | 1,073,741,888 | 7,131,370,624 |
| 364 | D | retain | D24-forward-6 | H | 1,073,741,888 | 7,131,370,624 |
| 365 | D | release-retained | D24-forward-6 | H | 1,073,741,888 | 7,131,370,624 |
| 366 | D | release-retained | D24-forward-5 | L | 1,073,741,888 | 7,131,370,624 |
| 367 | D | free | D24-forward-4 | H | 1,073,741,888 | 6,057,628,736 |
| 368 | D | free | D24-forward-3 | L | 1,073,741,888 | 6,057,628,736 |
| 369 | D | free | D24-forward-2 | H | 1,073,741,888 | 4,983,886,848 |
| 370 | D | free | D24-forward-1 | L | 1,073,741,888 | 4,983,886,848 |
| 371 | D | alloc | D25-node | L | 2,147,475,520 | 4,983,886,848 |
| 372 | D | free | D25-node | L | 2,147,475,520 | 4,983,886,848 |
| 373 | D | shrink | g | L | 805,306,432 | 4,983,886,848 |
| 374 | D | shrink | A-O1 | H | 805,306,432 | 4,715,451,392 |
| 375 | D | alloc | D25-forward-1 | L | 805,306,432 | 4,715,451,392 |
| 376 | D | alloc | D25-forward-2 | H | 805,306,432 | 5,520,757,824 |
| 377 | D | alloc | D25-forward-3 | L | 805,306,432 | 5,520,757,824 |
| 378 | D | alloc | D25-forward-4 | H | 805,306,432 | 6,326,064,256 |
| 379 | D | retain | D25-forward-5 | L | 805,306,432 | 6,326,064,256 |
| 380 | D | retain | D25-forward-6 | H | 805,306,432 | 6,326,064,256 |
| 381 | D | release-retained | D25-forward-6 | H | 805,306,432 | 6,326,064,256 |
| 382 | D | release-retained | D25-forward-5 | L | 805,306,432 | 6,326,064,256 |
| 383 | D | free | D25-forward-4 | H | 805,306,432 | 5,520,757,824 |
| 384 | D | free | D25-forward-3 | L | 805,306,432 | 5,520,757,824 |
| 385 | D | free | D25-forward-2 | H | 805,306,432 | 4,715,451,392 |
| 386 | D | free | D25-forward-1 | L | 805,306,432 | 4,715,451,392 |
| 387 | D | alloc | D26-node | L | 2,147,475,520 | 4,715,451,392 |
| 388 | D | free | D26-node | L | 2,147,475,520 | 4,715,451,392 |
| 389 | D | shrink | g | L | 805,306,432 | 4,715,451,392 |
| 390 | D | shrink | A-O1 | H | 805,306,432 | 4,715,451,392 |
| 391 | D | alloc | D26-forward-1 | L | 805,306,432 | 4,715,451,392 |
| 392 | D | alloc | D26-forward-2 | H | 805,306,432 | 5,520,757,824 |
| 393 | D | alloc | D26-forward-3 | L | 805,306,432 | 5,520,757,824 |
| 394 | D | alloc | D26-forward-4 | H | 805,306,432 | 6,326,064,256 |
| 395 | D | retain | D26-forward-5 | L | 805,306,432 | 6,326,064,256 |
| 396 | D | retain | D26-forward-6 | H | 805,306,432 | 6,326,064,256 |
| 397 | D | release-retained | D26-forward-6 | H | 805,306,432 | 6,326,064,256 |
| 398 | D | release-retained | D26-forward-5 | L | 805,306,432 | 6,326,064,256 |
| 399 | D | free | D26-forward-4 | H | 805,306,432 | 5,520,757,824 |
| 400 | D | free | D26-forward-3 | L | 805,306,432 | 5,520,757,824 |
| 401 | D | free | D26-forward-2 | H | 805,306,432 | 4,715,451,392 |
| 402 | D | free | D26-forward-1 | L | 805,306,432 | 4,715,451,392 |
| 403 | D | alloc | D27-node | L | 2,147,475,520 | 4,715,451,392 |
| 404 | D | free | D27-node | L | 2,147,475,520 | 4,715,451,392 |
| 405 | D | shrink | g | L | 536,870,976 | 4,715,451,392 |
| 406 | D | shrink | A-O1 | H | 536,870,976 | 4,447,015,936 |
| 407 | D | alloc | D27-forward-1 | L | 536,870,976 | 4,447,015,936 |
| 408 | D | alloc | D27-forward-2 | H | 536,870,976 | 4,983,886,912 |
| 409 | D | alloc | D27-forward-3 | L | 536,870,976 | 4,983,886,912 |
| 410 | D | alloc | D27-forward-4 | H | 536,870,976 | 5,520,757,888 |
| 411 | D | retain | D27-forward-5 | L | 536,870,976 | 5,520,757,888 |
| 412 | D | retain | D27-forward-6 | H | 536,870,976 | 5,520,757,888 |
| 413 | D | release-retained | D27-forward-6 | H | 536,870,976 | 5,520,757,888 |
| 414 | D | release-retained | D27-forward-5 | L | 536,870,976 | 5,520,757,888 |
| 415 | D | free | D27-forward-4 | H | 536,870,976 | 4,983,886,912 |
| 416 | D | free | D27-forward-3 | L | 536,870,976 | 4,983,886,912 |
| 417 | D | free | D27-forward-2 | H | 536,870,976 | 4,447,015,936 |
| 418 | D | free | D27-forward-1 | L | 536,870,976 | 4,447,015,936 |
| 419 | D | alloc | D28-node | L | 2,147,475,520 | 4,447,015,936 |
| 420 | D | free | D28-node | L | 2,147,475,520 | 4,447,015,936 |
| 421 | D | shrink | g | L | 402,653,248 | 4,447,015,936 |
| 422 | D | shrink | A-O1 | H | 402,653,248 | 4,312,798,208 |
| 423 | D | alloc | D28-forward-1 | L | 402,653,248 | 4,312,798,208 |
| 424 | D | alloc | D28-forward-2 | H | 402,653,248 | 4,715,451,456 |
| 425 | D | alloc | D28-forward-3 | L | 402,653,248 | 4,715,451,456 |
| 426 | D | alloc | D28-forward-4 | H | 402,653,248 | 5,118,104,704 |
| 427 | D | retain | D28-forward-5 | L | 402,653,248 | 5,118,104,704 |
| 428 | D | retain | D28-forward-6 | H | 402,653,248 | 5,118,104,704 |
| 429 | D | release-retained | D28-forward-6 | H | 402,653,248 | 5,118,104,704 |
| 430 | D | release-retained | D28-forward-5 | L | 402,653,248 | 5,118,104,704 |
| 431 | D | free | D28-forward-4 | H | 402,653,248 | 4,715,451,456 |
| 432 | D | free | D28-forward-3 | L | 402,653,248 | 4,715,451,456 |
| 433 | D | free | D28-forward-2 | H | 402,653,248 | 4,312,798,208 |
| 434 | D | free | D28-forward-1 | L | 402,653,248 | 4,312,798,208 |
| 435 | D | alloc | D29-node | L | 1,073,733,696 | 4,312,798,208 |
| 436 | D | free | D29-node | L | 1,073,733,696 | 4,312,798,208 |
| 437 | D | shrink | g | L | 201,326,656 | 4,312,798,208 |
| 438 | D | shrink | A-O1 | H | 201,326,656 | 4,111,471,616 |
| 439 | D | alloc | D29-forward-1 | L | 201,326,656 | 4,111,471,616 |
| 440 | D | alloc | D29-forward-2 | H | 201,326,656 | 4,312,798,272 |
| 441 | D | alloc | D29-forward-3 | L | 201,326,656 | 4,312,798,272 |
| 442 | D | alloc | D29-forward-4 | H | 201,326,656 | 4,514,124,928 |
| 443 | D | retain | D29-forward-5 | L | 201,326,656 | 4,514,124,928 |
| 444 | D | retain | D29-forward-6 | H | 201,326,656 | 4,514,124,928 |
| 445 | D | release-retained | D29-forward-6 | H | 201,326,656 | 4,514,124,928 |
| 446 | D | release-retained | D29-forward-5 | L | 201,326,656 | 4,514,124,928 |
| 447 | D | free | D29-forward-4 | H | 201,326,656 | 4,312,798,272 |
| 448 | D | free | D29-forward-3 | L | 201,326,656 | 4,312,798,272 |
| 449 | D | free | D29-forward-2 | H | 201,326,656 | 4,111,471,616 |
| 450 | D | free | D29-forward-1 | L | 201,326,656 | 4,111,471,616 |
| 451 | D | alloc | D30-node | L | 536,862,784 | 4,111,471,616 |
| 452 | D | free | D30-node | L | 536,862,784 | 4,111,471,616 |
| 453 | D | shrink | g | L | 100,663,360 | 4,111,471,616 |
| 454 | D | shrink | A-O1 | H | 100,663,360 | 4,010,808,320 |
| 455 | D | alloc | D30-forward-1 | L | 100,663,360 | 4,010,808,320 |
| 456 | D | alloc | D30-forward-2 | H | 100,663,360 | 4,111,471,680 |
| 457 | D | alloc | D30-forward-3 | L | 100,663,360 | 4,111,471,680 |
| 458 | D | alloc | D30-forward-4 | H | 100,663,360 | 4,212,135,040 |
| 459 | D | retain | D30-forward-5 | L | 100,663,360 | 4,212,135,040 |
| 460 | D | retain | D30-forward-6 | H | 100,663,360 | 4,212,135,040 |
| 461 | D | release-retained | D30-forward-6 | H | 100,663,360 | 4,212,135,040 |
| 462 | D | release-retained | D30-forward-5 | L | 100,663,360 | 4,212,135,040 |
| 463 | D | free | D30-forward-4 | H | 100,663,360 | 4,111,471,680 |
| 464 | D | free | D30-forward-3 | L | 100,663,360 | 4,111,471,680 |
| 465 | D | free | D30-forward-2 | H | 100,663,360 | 4,010,808,320 |
| 466 | D | free | D30-forward-1 | L | 100,663,360 | 4,010,808,320 |
| 467 | D | alloc | D31-node | L | 268,427,328 | 4,010,808,320 |
| 468 | D | free | D31-node | L | 268,427,328 | 4,010,808,320 |
| 469 | D | shrink | g | L | 50,331,712 | 4,010,808,320 |
| 470 | D | shrink | A-O1 | H | 50,331,712 | 3,960,476,672 |
| 471 | D | alloc | D31-forward-1 | L | 50,331,712 | 3,960,476,672 |
| 472 | D | alloc | D31-forward-2 | H | 50,331,712 | 4,010,808,384 |
| 473 | D | alloc | D31-forward-3 | L | 50,331,712 | 4,010,808,384 |
| 474 | D | alloc | D31-forward-4 | H | 50,331,712 | 4,061,140,096 |
| 475 | D | retain | D31-forward-5 | L | 50,331,712 | 4,061,140,096 |
| 476 | D | retain | D31-forward-6 | H | 50,331,712 | 4,061,140,096 |
| 477 | D | release-retained | D31-forward-6 | H | 50,331,712 | 4,061,140,096 |
| 478 | D | release-retained | D31-forward-5 | L | 50,331,712 | 4,061,140,096 |
| 479 | D | free | D31-forward-4 | H | 50,331,712 | 4,010,808,384 |
| 480 | D | free | D31-forward-3 | L | 50,331,712 | 4,010,808,384 |
| 481 | D | free | D31-forward-2 | H | 50,331,712 | 3,960,476,672 |
| 482 | D | free | D31-forward-1 | L | 50,331,712 | 3,960,476,672 |
| 483 | D | alloc | D32-node | L | 134,209,600 | 3,960,476,672 |
| 484 | D | free | D32-node | L | 134,209,600 | 3,960,476,672 |
| 485 | D | shrink | g | L | 33,554,496 | 3,960,476,672 |
| 486 | D | shrink | A-O1 | H | 33,554,496 | 3,943,699,456 |
| 487 | D | alloc | D32-forward-1 | L | 33,554,496 | 3,943,699,456 |
| 488 | D | alloc | D32-forward-2 | H | 33,554,496 | 3,977,253,952 |
| 489 | D | alloc | D32-forward-3 | L | 33,554,496 | 3,977,253,952 |
| 490 | D | alloc | D32-forward-4 | H | 33,554,496 | 4,010,808,448 |
| 491 | D | retain | D32-forward-5 | L | 33,554,496 | 4,010,808,448 |
| 492 | D | retain | D32-forward-6 | H | 33,554,496 | 4,010,808,448 |
| 493 | D | release-retained | D32-forward-6 | H | 33,554,496 | 4,010,808,448 |
| 494 | D | release-retained | D32-forward-5 | L | 33,554,496 | 4,010,808,448 |
| 495 | D | free | D32-forward-4 | H | 33,554,496 | 3,977,253,952 |
| 496 | D | free | D32-forward-3 | L | 33,554,496 | 3,977,253,952 |
| 497 | D | free | D32-forward-2 | H | 33,554,496 | 3,943,699,456 |
| 498 | D | free | D32-forward-1 | L | 33,554,496 | 3,943,699,456 |
| 499 | D | alloc | D33-node | L | 134,209,600 | 3,943,699,456 |
| 500 | D | free | D33-node | L | 134,209,600 | 3,943,699,456 |
| 501 | D | shrink | g | L | 25,165,888 | 3,943,699,456 |
| 502 | D | shrink | A-O1 | H | 25,165,888 | 3,935,310,848 |
| 503 | D | alloc | D33-forward-1 | L | 25,165,888 | 3,935,310,848 |
| 504 | D | alloc | D33-forward-2 | H | 25,165,888 | 3,960,476,736 |
| 505 | D | alloc | D33-forward-3 | L | 25,165,888 | 3,960,476,736 |
| 506 | D | alloc | D33-forward-4 | H | 25,165,888 | 3,985,642,624 |
| 507 | D | retain | D33-forward-5 | L | 25,165,888 | 3,985,642,624 |
| 508 | D | retain | D33-forward-6 | H | 25,165,888 | 3,985,642,624 |
| 509 | D | release-retained | D33-forward-6 | H | 25,165,888 | 3,985,642,624 |
| 510 | D | release-retained | D33-forward-5 | L | 25,165,888 | 3,985,642,624 |
| 511 | D | free | D33-forward-4 | H | 25,165,888 | 3,960,476,736 |
| 512 | D | free | D33-forward-3 | L | 25,165,888 | 3,960,476,736 |
| 513 | D | free | D33-forward-2 | H | 25,165,888 | 3,935,310,848 |
| 514 | D | free | D33-forward-1 | L | 25,165,888 | 3,935,310,848 |
| 515 | D | alloc | D34-node | L | 67,100,736 | 3,935,310,848 |
| 516 | D | free | D34-node | L | 67,100,736 | 3,935,310,848 |
| 517 | D | shrink | g | L | 16,777,280 | 3,935,310,848 |
| 518 | D | shrink | A-O1 | H | 16,777,280 | 3,926,922,240 |
| 519 | D | alloc | D34-forward-1 | L | 16,777,280 | 3,926,922,240 |
| 520 | D | alloc | D34-forward-2 | H | 16,777,280 | 3,943,699,520 |
| 521 | D | alloc | D34-forward-3 | L | 16,777,280 | 3,943,699,520 |
| 522 | D | alloc | D34-forward-4 | H | 16,777,280 | 3,960,476,800 |
| 523 | D | retain | D34-forward-5 | L | 16,777,280 | 3,960,476,800 |
| 524 | D | retain | D34-forward-6 | H | 16,777,280 | 3,960,476,800 |
| 525 | D | release-retained | D34-forward-6 | H | 16,777,280 | 3,960,476,800 |
| 526 | D | release-retained | D34-forward-5 | L | 16,777,280 | 3,960,476,800 |
| 527 | D | free | D34-forward-4 | H | 16,777,280 | 3,943,699,520 |
| 528 | D | free | D34-forward-3 | L | 16,777,280 | 3,943,699,520 |
| 529 | D | free | D34-forward-2 | H | 16,777,280 | 3,926,922,240 |
| 530 | D | free | D34-forward-1 | L | 16,777,280 | 3,926,922,240 |
| 531 | D | alloc | D35-node | L | 67,100,736 | 3,926,922,240 |
| 532 | D | free | D35-node | L | 67,100,736 | 3,926,922,240 |
| 533 | D | shrink | g | L | 12,582,976 | 3,926,922,240 |
| 534 | D | shrink | A-O1 | H | 12,582,976 | 3,922,727,936 |
| 535 | D | alloc | D35-forward-1 | L | 12,582,976 | 3,922,727,936 |
| 536 | D | alloc | D35-forward-2 | H | 12,582,976 | 3,935,310,912 |
| 537 | D | alloc | D35-forward-3 | L | 12,582,976 | 3,935,310,912 |
| 538 | D | alloc | D35-forward-4 | H | 12,582,976 | 3,947,893,888 |
| 539 | D | retain | D35-forward-5 | L | 12,582,976 | 3,947,893,888 |
| 540 | D | retain | D35-forward-6 | H | 12,582,976 | 3,947,893,888 |
| 541 | D | release-retained | D35-forward-6 | H | 12,582,976 | 3,947,893,888 |
| 542 | D | release-retained | D35-forward-5 | L | 12,582,976 | 3,947,893,888 |
| 543 | D | free | D35-forward-4 | H | 12,582,976 | 3,935,310,912 |
| 544 | D | free | D35-forward-3 | L | 12,582,976 | 3,935,310,912 |
| 545 | D | free | D35-forward-2 | H | 12,582,976 | 3,922,727,936 |
| 546 | D | free | D35-forward-1 | L | 12,582,976 | 3,922,727,936 |
| 547 | D | alloc | D36-node | L | 33,546,304 | 3,922,727,936 |
| 548 | D | free | D36-node | L | 33,546,304 | 3,922,727,936 |
| 549 | D | shrink | g | L | 6,291,520 | 3,922,727,936 |
| 550 | D | shrink | A-O1 | H | 6,291,520 | 3,916,436,480 |
| 551 | D | alloc | D36-forward-1 | L | 6,291,520 | 3,916,436,480 |
| 552 | D | alloc | D36-forward-2 | H | 6,291,520 | 3,922,728,000 |
| 553 | D | alloc | D36-forward-3 | L | 6,291,520 | 3,922,728,000 |
| 554 | D | alloc | D36-forward-4 | H | 6,291,520 | 3,929,019,520 |
| 555 | D | retain | D36-forward-5 | L | 6,291,520 | 3,929,019,520 |
| 556 | D | retain | D36-forward-6 | H | 6,291,520 | 3,929,019,520 |
| 557 | D | release-retained | D36-forward-6 | H | 6,291,520 | 3,929,019,520 |
| 558 | D | release-retained | D36-forward-5 | L | 6,291,520 | 3,929,019,520 |
| 559 | D | free | D36-forward-4 | H | 6,291,520 | 3,922,728,000 |
| 560 | D | free | D36-forward-3 | L | 6,291,520 | 3,922,728,000 |
| 561 | D | free | D36-forward-2 | H | 6,291,520 | 3,916,436,480 |
| 562 | D | free | D36-forward-1 | L | 6,291,520 | 3,916,436,480 |
| 563 | D | alloc | D37-node | L | 16,769,088 | 3,916,436,480 |
| 564 | D | free | D37-node | L | 16,769,088 | 3,916,436,480 |
| 565 | D | shrink | g | L | 4,194,368 | 3,916,436,480 |
| 566 | D | shrink | A-O1 | H | 4,194,368 | 3,914,339,328 |
| 567 | D | alloc | D37-forward-1 | L | 4,194,368 | 3,914,339,328 |
| 568 | D | alloc | D37-forward-2 | H | 4,194,368 | 3,918,533,696 |
| 569 | D | alloc | D37-forward-3 | L | 4,194,368 | 3,918,533,696 |
| 570 | D | alloc | D37-forward-4 | H | 4,194,368 | 3,922,728,064 |
| 571 | D | retain | D37-forward-5 | L | 4,194,368 | 3,922,728,064 |
| 572 | D | retain | D37-forward-6 | H | 4,194,368 | 3,922,728,064 |
| 573 | D | release-retained | D37-forward-6 | H | 4,194,368 | 3,922,728,064 |
| 574 | D | release-retained | D37-forward-5 | L | 4,194,368 | 3,922,728,064 |
| 575 | D | free | D37-forward-4 | H | 4,194,368 | 3,918,533,696 |
| 576 | D | free | D37-forward-3 | L | 4,194,368 | 3,918,533,696 |
| 577 | D | free | D37-forward-2 | H | 4,194,368 | 3,914,339,328 |
| 578 | D | free | D37-forward-1 | L | 4,194,368 | 3,914,339,328 |
| 579 | D | alloc | D38-node | L | 16,769,088 | 3,914,339,328 |
| 580 | D | free | D38-node | L | 16,769,088 | 3,914,339,328 |
| 581 | D | shrink | g | L | 3,145,792 | 3,914,339,328 |
| 582 | D | shrink | A-O1 | H | 3,145,792 | 3,913,290,752 |
| 583 | D | alloc | D38-forward-1 | L | 3,145,792 | 3,913,290,752 |
| 584 | D | alloc | D38-forward-2 | H | 3,145,792 | 3,916,436,544 |
| 585 | D | alloc | D38-forward-3 | L | 3,145,792 | 3,916,436,544 |
| 586 | D | alloc | D38-forward-4 | H | 3,145,792 | 3,919,582,336 |
| 587 | D | retain | D38-forward-5 | L | 3,145,792 | 3,919,582,336 |
| 588 | D | retain | D38-forward-6 | H | 3,145,792 | 3,919,582,336 |
| 589 | D | release-retained | D38-forward-6 | H | 3,145,792 | 3,919,582,336 |
| 590 | D | release-retained | D38-forward-5 | L | 3,145,792 | 3,919,582,336 |
| 591 | D | free | D38-forward-4 | H | 3,145,792 | 3,916,436,544 |
| 592 | D | free | D38-forward-3 | L | 3,145,792 | 3,916,436,544 |
| 593 | D | free | D38-forward-2 | H | 3,145,792 | 3,913,290,752 |
| 594 | D | free | D38-forward-1 | L | 3,145,792 | 3,913,290,752 |
| 595 | D | alloc | D39-node | L | 8,380,480 | 3,913,290,752 |
| 596 | D | free | D39-node | L | 8,380,480 | 3,913,290,752 |
| 597 | D | shrink | g | L | 1,572,928 | 3,913,290,752 |
| 598 | D | shrink | A-O1 | H | 1,572,928 | 3,911,717,888 |
| 599 | D | alloc | D39-forward-1 | L | 1,572,928 | 3,911,717,888 |
| 600 | D | alloc | D39-forward-2 | H | 1,572,928 | 3,913,290,816 |
| 601 | D | alloc | D39-forward-3 | L | 1,572,928 | 3,913,290,816 |
| 602 | D | alloc | D39-forward-4 | H | 1,572,928 | 3,914,863,744 |
| 603 | D | retain | D39-forward-5 | L | 1,572,928 | 3,914,863,744 |
| 604 | D | retain | D39-forward-6 | H | 1,572,928 | 3,914,863,744 |
| 605 | D | release-retained | D39-forward-6 | H | 1,572,928 | 3,914,863,744 |
| 606 | D | release-retained | D39-forward-5 | L | 1,572,928 | 3,914,863,744 |
| 607 | D | free | D39-forward-4 | H | 1,572,928 | 3,913,290,816 |
| 608 | D | free | D39-forward-3 | L | 1,572,928 | 3,913,290,816 |
| 609 | D | free | D39-forward-2 | H | 1,572,928 | 3,911,717,888 |
| 610 | D | free | D39-forward-1 | L | 1,572,928 | 3,911,717,888 |
| 611 | D | alloc | D40-node | L | 4,186,176 | 3,911,717,888 |
| 612 | D | free | D40-node | L | 4,186,176 | 3,911,717,888 |
| 613 | D | shrink | g | L | 1,048,640 | 3,911,717,888 |
| 614 | D | shrink | A-O1 | H | 1,048,640 | 3,911,193,600 |
| 615 | D | alloc | D40-forward-1 | L | 1,048,640 | 3,911,193,600 |
| 616 | D | alloc | D40-forward-2 | H | 1,048,640 | 3,912,242,240 |
| 617 | D | alloc | D40-forward-3 | L | 1,048,640 | 3,912,242,240 |
| 618 | D | alloc | D40-forward-4 | H | 1,048,640 | 3,913,290,880 |
| 619 | D | retain | D40-forward-5 | L | 1,048,640 | 3,913,290,880 |
| 620 | D | retain | D40-forward-6 | H | 1,048,640 | 3,913,290,880 |
| 621 | D | release-retained | D40-forward-6 | H | 1,048,640 | 3,913,290,880 |
| 622 | D | release-retained | D40-forward-5 | L | 1,048,640 | 3,913,290,880 |
| 623 | D | free | D40-forward-4 | H | 1,048,640 | 3,912,242,240 |
| 624 | D | free | D40-forward-3 | L | 1,048,640 | 3,912,242,240 |
| 625 | D | free | D40-forward-2 | H | 1,048,640 | 3,911,193,600 |
| 626 | D | free | D40-forward-1 | L | 1,048,640 | 3,911,193,600 |
| 627 | D | alloc | D41-node | L | 4,186,176 | 3,911,193,600 |
| 628 | D | free | D41-node | L | 4,186,176 | 3,911,193,600 |
| 629 | D | shrink | g | L | 786,496 | 3,911,193,600 |
| 630 | D | shrink | A-O1 | H | 786,496 | 3,910,931,456 |
| 631 | D | alloc | D41-forward-1 | L | 786,496 | 3,910,931,456 |
| 632 | D | alloc | D41-forward-2 | H | 786,496 | 3,911,717,952 |
| 633 | D | alloc | D41-forward-3 | L | 786,496 | 3,911,717,952 |
| 634 | D | alloc | D41-forward-4 | H | 786,496 | 3,912,504,448 |
| 635 | D | retain | D41-forward-5 | L | 786,496 | 3,912,504,448 |
| 636 | D | retain | D41-forward-6 | H | 786,496 | 3,912,504,448 |
| 637 | D | release-retained | D41-forward-6 | H | 786,496 | 3,912,504,448 |
| 638 | D | release-retained | D41-forward-5 | L | 786,496 | 3,912,504,448 |
| 639 | D | free | D41-forward-4 | H | 786,496 | 3,911,717,952 |
| 640 | D | free | D41-forward-3 | L | 786,496 | 3,911,717,952 |
| 641 | D | free | D41-forward-2 | H | 786,496 | 3,910,931,456 |
| 642 | D | free | D41-forward-1 | L | 786,496 | 3,910,931,456 |
| 643 | D | alloc | D42-node | L | 2,089,024 | 3,910,931,456 |
| 644 | D | free | D42-node | L | 2,089,024 | 3,910,931,456 |
| 645 | D | shrink | g | L | 393,280 | 3,910,931,456 |
| 646 | D | shrink | A-O1 | H | 393,280 | 3,910,538,240 |
| 647 | D | alloc | D42-forward-1 | L | 393,280 | 3,910,538,240 |
| 648 | D | alloc | D42-forward-2 | H | 393,280 | 3,910,931,520 |
| 649 | D | alloc | D42-forward-3 | L | 393,280 | 3,910,931,520 |
| 650 | D | alloc | D42-forward-4 | H | 393,280 | 3,911,324,800 |
| 651 | D | retain | D42-forward-5 | L | 393,280 | 3,911,324,800 |
| 652 | D | retain | D42-forward-6 | H | 393,280 | 3,911,324,800 |
| 653 | D | release-retained | D42-forward-6 | H | 393,280 | 3,911,324,800 |
| 654 | D | release-retained | D42-forward-5 | L | 393,280 | 3,911,324,800 |
| 655 | D | free | D42-forward-4 | H | 393,280 | 3,910,931,520 |
| 656 | D | free | D42-forward-3 | L | 393,280 | 3,910,931,520 |
| 657 | D | free | D42-forward-2 | H | 393,280 | 3,910,538,240 |
| 658 | D | free | D42-forward-1 | L | 393,280 | 3,910,538,240 |
| 659 | D | alloc | D43-node | L | 1,040,448 | 3,910,538,240 |
| 660 | D | free | D43-node | L | 1,040,448 | 3,910,538,240 |
| 661 | D | shrink | g | L | 196,672 | 3,910,538,240 |
| 662 | D | shrink | A-O1 | H | 196,672 | 3,910,341,632 |
| 663 | D | alloc | D43-forward-1 | L | 196,672 | 3,910,341,632 |
| 664 | D | alloc | D43-forward-2 | H | 196,672 | 3,910,538,304 |
| 665 | D | alloc | D43-forward-3 | L | 196,672 | 3,910,538,304 |
| 666 | D | alloc | D43-forward-4 | H | 196,672 | 3,910,734,976 |
| 667 | D | retain | D43-forward-5 | L | 196,672 | 3,910,734,976 |
| 668 | D | retain | D43-forward-6 | H | 196,672 | 3,910,734,976 |
| 669 | D | release-retained | D43-forward-6 | H | 196,672 | 3,910,734,976 |
| 670 | D | release-retained | D43-forward-5 | L | 196,672 | 3,910,734,976 |
| 671 | D | free | D43-forward-4 | H | 196,672 | 3,910,538,304 |
| 672 | D | free | D43-forward-3 | L | 196,672 | 3,910,538,304 |
| 673 | D | free | D43-forward-2 | H | 196,672 | 3,910,341,632 |
| 674 | D | free | D43-forward-1 | L | 196,672 | 3,910,341,632 |
| 675 | D | alloc | D44-node | L | 516,160 | 3,910,341,632 |
| 676 | D | free | D44-node | L | 516,160 | 3,910,341,632 |
| 677 | D | shrink | g | L | 131,136 | 3,910,341,632 |
| 678 | D | shrink | A-O1 | H | 131,136 | 3,910,276,096 |
| 679 | D | alloc | D44-forward-1 | L | 131,136 | 3,910,276,096 |
| 680 | D | alloc | D44-forward-2 | H | 131,136 | 3,910,407,232 |
| 681 | D | alloc | D44-forward-3 | L | 131,136 | 3,910,407,232 |
| 682 | D | alloc | D44-forward-4 | H | 131,136 | 3,910,538,368 |
| 683 | D | retain | D44-forward-5 | L | 131,136 | 3,910,538,368 |
| 684 | D | retain | D44-forward-6 | H | 131,136 | 3,910,538,368 |
| 685 | D | release-retained | D44-forward-6 | H | 131,136 | 3,910,538,368 |
| 686 | D | release-retained | D44-forward-5 | L | 131,136 | 3,910,538,368 |
| 687 | D | free | D44-forward-4 | H | 131,136 | 3,910,407,232 |
| 688 | D | free | D44-forward-3 | L | 131,136 | 3,910,407,232 |
| 689 | D | free | D44-forward-2 | H | 131,136 | 3,910,276,096 |
| 690 | D | free | D44-forward-1 | L | 131,136 | 3,910,276,096 |
| 691 | D | alloc | D45-node | L | 516,160 | 3,910,276,096 |
| 692 | D | free | D45-node | L | 516,160 | 3,910,276,096 |
| 693 | D | shrink | g | L | 98,368 | 3,910,276,096 |
| 694 | D | shrink | A-O1 | H | 98,368 | 3,910,243,328 |
| 695 | D | alloc | D45-forward-1 | L | 98,368 | 3,910,243,328 |
| 696 | D | alloc | D45-forward-2 | H | 98,368 | 3,910,341,696 |
| 697 | D | alloc | D45-forward-3 | L | 98,368 | 3,910,341,696 |
| 698 | D | alloc | D45-forward-4 | H | 98,368 | 3,910,440,064 |
| 699 | D | retain | D45-forward-5 | L | 98,368 | 3,910,440,064 |
| 700 | D | retain | D45-forward-6 | H | 98,368 | 3,910,440,064 |
| 701 | D | release-retained | D45-forward-6 | H | 98,368 | 3,910,440,064 |
| 702 | D | release-retained | D45-forward-5 | L | 98,368 | 3,910,440,064 |
| 703 | D | free | D45-forward-4 | H | 98,368 | 3,910,341,696 |
| 704 | D | free | D45-forward-3 | L | 98,368 | 3,910,341,696 |
| 705 | D | free | D45-forward-2 | H | 98,368 | 3,910,243,328 |
| 706 | D | free | D45-forward-1 | L | 98,368 | 3,910,243,328 |
| 707 | D | alloc | D46-node | L | 254,016 | 3,910,243,328 |
| 708 | D | free | D46-node | L | 254,016 | 3,910,243,328 |
| 709 | D | shrink | g | L | 49,216 | 3,910,243,328 |
| 710 | D | shrink | A-O1 | H | 49,216 | 3,910,194,176 |
| 711 | D | alloc | D46-forward-1 | L | 49,216 | 3,910,194,176 |
| 712 | D | alloc | D46-forward-2 | H | 49,216 | 3,910,243,392 |
| 713 | D | alloc | D46-forward-3 | L | 49,216 | 3,910,243,392 |
| 714 | D | alloc | D46-forward-4 | H | 49,216 | 3,910,292,608 |
| 715 | D | retain | D46-forward-5 | L | 49,216 | 3,910,292,608 |
| 716 | D | retain | D46-forward-6 | H | 49,216 | 3,910,292,608 |
| 717 | D | release-retained | D46-forward-6 | H | 49,216 | 3,910,292,608 |
| 718 | D | release-retained | D46-forward-5 | L | 49,216 | 3,910,292,608 |
| 719 | D | free | D46-forward-4 | H | 49,216 | 3,910,243,392 |
| 720 | D | free | D46-forward-3 | L | 49,216 | 3,910,243,392 |
| 721 | D | free | D46-forward-2 | H | 49,216 | 3,910,194,176 |
| 722 | D | free | D46-forward-1 | L | 49,216 | 3,910,194,176 |
| 723 | D | alloc | D47-node | L | 122,944 | 3,910,194,176 |
| 724 | D | free | D47-node | L | 122,944 | 3,910,194,176 |
| 725 | D | shrink | g | L | 32,832 | 3,910,194,176 |
| 726 | D | shrink | A-O1 | H | 32,832 | 3,910,177,792 |
| 727 | D | alloc | D47-forward-1 | L | 32,832 | 3,910,177,792 |
| 728 | D | alloc | D47-forward-2 | H | 32,832 | 3,910,210,624 |
| 729 | D | alloc | D47-forward-3 | L | 32,832 | 3,910,210,624 |
| 730 | D | alloc | D47-forward-4 | H | 32,832 | 3,910,243,456 |
| 731 | D | retain | D47-forward-5 | L | 32,832 | 3,910,243,456 |
| 732 | D | retain | D47-forward-6 | H | 32,832 | 3,910,243,456 |
| 733 | D | release-retained | D47-forward-6 | H | 32,832 | 3,910,243,456 |
| 734 | D | release-retained | D47-forward-5 | L | 32,832 | 3,910,243,456 |
| 735 | D | free | D47-forward-4 | H | 32,832 | 3,910,210,624 |
| 736 | D | free | D47-forward-3 | L | 32,832 | 3,910,210,624 |
| 737 | D | free | D47-forward-2 | H | 32,832 | 3,910,177,792 |
| 738 | D | free | D47-forward-1 | L | 32,832 | 3,910,177,792 |
| 739 | D | alloc | D48-node | L | 122,944 | 3,910,177,792 |
| 740 | D | free | D48-node | L | 122,944 | 3,910,177,792 |
| 741 | D | shrink | g | L | 24,640 | 3,910,177,792 |
| 742 | D | shrink | A-O1 | H | 24,640 | 3,910,169,600 |
| 743 | D | alloc | D48-forward-1 | L | 24,640 | 3,910,169,600 |
| 744 | D | alloc | D48-forward-2 | H | 24,640 | 3,910,194,240 |
| 745 | D | alloc | D48-forward-3 | L | 24,640 | 3,910,194,240 |
| 746 | D | alloc | D48-forward-4 | H | 24,640 | 3,910,218,880 |
| 747 | D | retain | D48-forward-5 | L | 24,640 | 3,910,218,880 |
| 748 | D | retain | D48-forward-6 | H | 24,640 | 3,910,218,880 |
| 749 | D | release-retained | D48-forward-6 | H | 24,640 | 3,910,218,880 |
| 750 | D | release-retained | D48-forward-5 | L | 24,640 | 3,910,218,880 |
| 751 | D | free | D48-forward-4 | H | 24,640 | 3,910,194,240 |
| 752 | D | free | D48-forward-3 | L | 24,640 | 3,910,194,240 |
| 753 | D | free | D48-forward-2 | H | 24,640 | 3,910,169,600 |
| 754 | D | free | D48-forward-1 | L | 24,640 | 3,910,169,600 |
| 755 | D | alloc | D49-node | L | 57,408 | 3,910,169,600 |
| 756 | D | free | D49-node | L | 57,408 | 3,910,169,600 |
| 757 | D | shrink | g | L | 12,352 | 3,910,169,600 |
| 758 | D | shrink | A-O1 | H | 12,352 | 3,910,157,312 |
| 759 | D | alloc | D49-forward-1 | L | 12,352 | 3,910,157,312 |
| 760 | D | alloc | D49-forward-2 | H | 12,352 | 3,910,169,664 |
| 761 | D | alloc | D49-forward-3 | L | 12,352 | 3,910,169,664 |
| 762 | D | alloc | D49-forward-4 | H | 12,352 | 3,910,182,016 |
| 763 | D | retain | D49-forward-5 | L | 12,352 | 3,910,182,016 |
| 764 | D | retain | D49-forward-6 | H | 12,352 | 3,910,182,016 |
| 765 | D | release-retained | D49-forward-6 | H | 12,352 | 3,910,182,016 |
| 766 | D | release-retained | D49-forward-5 | L | 12,352 | 3,910,182,016 |
| 767 | D | free | D49-forward-4 | H | 12,352 | 3,910,169,664 |
| 768 | D | free | D49-forward-3 | L | 12,352 | 3,910,169,664 |
| 769 | D | free | D49-forward-2 | H | 12,352 | 3,910,157,312 |
| 770 | D | free | D49-forward-1 | L | 12,352 | 3,910,157,312 |
| 771 | D | free | root-tables | L | 532,800 | 545,472 |
| 772 | D | free | A-O1 | H | 12,352 | 533,120 |
| 773 | D | free | g | L | 12,352 | 520,768 |
| 774 | E | alloc | E-factor | S1024 | 1,024 | 520,768 |
| 775 | E | alloc | E-base | S1024 | 1,024 | 520,768 |
| 776 | E | alloc | E-power-result | S1024 | 1,024 | 520,768 |
| 777 | E | alloc | E-product-scratch | S2048 | 2,048 | 520,768 |
| 778 | E | alloc | E-P-minus-one | S1024 | 1,024 | 520,768 |
| 779 | E | alloc | E-P-plus-one | S1024 | 1,024 | 520,768 |
| 780 | E | alloc | E-gcd-left | S1024 | 1,024 | 520,768 |
| 781 | E | alloc | E-gcd-right | S1024 | 1,024 | 520,768 |
| 782 | E | alloc | E-selected-factor | S1024 | 1,024 | 520,768 |
| 783 | E | alloc | E-random-words | S128 | 128 | 520,768 |
| 784 | E | free | E-random-words | S128 | 128 | 520,768 |
| 785 | E | free | E-selected-factor | S1024 | 1,024 | 520,768 |
| 786 | E | free | E-gcd-right | S1024 | 1,024 | 520,768 |
| 787 | E | free | E-gcd-left | S1024 | 1,024 | 520,768 |
| 788 | E | free | E-P-plus-one | S1024 | 1,024 | 520,768 |
| 789 | E | free | E-P-minus-one | S1024 | 1,024 | 520,768 |
| 790 | E | free | E-product-scratch | S2048 | 2,048 | 520,768 |
| 791 | E | free | E-power-result | S1024 | 1,024 | 520,768 |
| 792 | E | free | E-base | S1024 | 1,024 | 520,768 |
| 793 | E | free | E-factor | S1024 | 1,024 | 520,768 |
| 794 | F | alloc | F-root-chain | S2048 | 2,048 | 520,768 |
| 795 | F | alloc | F-candidate-state | S1024 | 1,024 | 520,768 |
| 796 | F | alloc | F-input-pair | S256 | 256 | 520,768 |
| 797 | F | alloc | F-line-state | S256 | 256 | 520,768 |
| 798 | F | free | F-line-state | S256 | 256 | 520,768 |
| 799 | F | free | F-input-pair | S256 | 256 | 520,768 |
| 800 | F | free | F-candidate-state | S1024 | 1,024 | 520,768 |
| 801 | F | free | F-root-chain | S2048 | 2,048 | 520,768 |
| 802 | G | alloc | G-two-input-pairs | S256 | 256 | 520,768 |
| 803 | G | alloc | G-two-poseidon-states | S256 | 256 | 520,768 |
| 804 | G | alloc | G-canonical-encodings | S256 | 256 | 520,768 |
| 805 | G | alloc | G-output-elements | S128 | 128 | 520,768 |
| 806 | G | free | G-output-elements | S128 | 128 | 520,768 |
| 807 | G | free | G-canonical-encodings | S256 | 256 | 520,768 |
| 808 | G | free | G-two-poseidon-states | S256 | 256 | 520,768 |
| 809 | G | free | G-two-input-pairs | S256 | 256 | 520,768 |
| 810 | stack | alloc | sampling:runtime_entry | R | 1,024 | 520,768 |
| 811 | stack | alloc | sampling:line_and_sampler | R | 2,048 | 520,768 |
| 812 | stack | free | sampling:line_and_sampler | R | 2,048 | 520,768 |
| 813 | stack | free | sampling:runtime_entry | R | 1,024 | 520,768 |
| 814 | stack | alloc | stage_c_transform:runtime_entry | R | 1,024 | 520,768 |
| 815 | stack | alloc | stage_c_transform:stage_c_driver | R | 4,096 | 520,768 |
| 816 | stack | alloc | stage_c_transform:seven_transform_frames | R | 7,168 | 520,768 |
| 817 | stack | alloc | stage_c_transform:product_planner | R | 2,048 | 520,768 |
| 818 | stack | alloc | stage_c_transform:allocator | R | 2,048 | 520,768 |
| 819 | stack | free | stage_c_transform:allocator | R | 2,048 | 520,768 |
| 820 | stack | free | stage_c_transform:product_planner | R | 2,048 | 520,768 |
| 821 | stack | free | stage_c_transform:seven_transform_frames | R | 7,168 | 520,768 |
| 822 | stack | free | stage_c_transform:stage_c_driver | R | 4,096 | 520,768 |
| 823 | stack | free | stage_c_transform:runtime_entry | R | 1,024 | 520,768 |
| 824 | stack | alloc | stage_d_half_gcd:runtime_entry | R | 1,024 | 520,768 |
| 825 | stack | alloc | stage_d_half_gcd:half_gcd_frames | R | 19,200 | 520,768 |
| 826 | stack | alloc | stage_d_half_gcd:allocator | R | 2,048 | 520,768 |
| 827 | stack | free | stage_d_half_gcd:allocator | R | 2,048 | 520,768 |
| 828 | stack | free | stage_d_half_gcd:half_gcd_frames | R | 19,200 | 520,768 |
| 829 | stack | free | stage_d_half_gcd:runtime_entry | R | 1,024 | 520,768 |
| 830 | stack | alloc | stage_e_isolation:runtime_entry | R | 1,024 | 520,768 |
| 831 | stack | alloc | stage_e_isolation:isolation | R | 2,048 | 520,768 |
| 832 | stack | alloc | stage_e_isolation:allocator | R | 2,048 | 520,768 |
| 833 | stack | free | stage_e_isolation:allocator | R | 2,048 | 520,768 |
| 834 | stack | free | stage_e_isolation:isolation | R | 2,048 | 520,768 |
| 835 | stack | free | stage_e_isolation:runtime_entry | R | 1,024 | 520,768 |
| 836 | stack | alloc | stage_f_g_output:runtime_entry | R | 1,024 | 520,768 |
| 837 | stack | alloc | stage_f_g_output:encoding_and_output | R | 4,096 | 520,768 |
| 838 | stack | free | stage_f_g_output:encoding_and_output | R | 4,096 | 520,768 |
| 839 | stack | free | stage_f_g_output:runtime_entry | R | 1,024 | 520,768 |
| 840 | stack | alloc | offline_generation:offline_generator | R | 2,048 | 520,768 |
| 841 | stack | free | offline_generation:offline_generator | R | 2,048 | 520,768 |


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
CONFIG = {'rounds': 6, 'graeffe_depth': 24, 'vshift_log': 24, 'truncated_nodes': 233, 'node_log': 19, 'full_log': 27, 'hgcd_cap': 22, 'tail_degree': 168, 'top_width': 4, 'bottom_width': 4, 'middle_widths': [7, 6, 6], 'active_top_cosets': 16, 'top_fused_core': 259, 'top_half_core': 192, 'inverse_top_core': 131, 'recovery_fixed': 1048576, 'recovery_per_layer': 8, 'recovery_per_point': 2, 'recovery_subtrees': [[1, 8], [2, 7], [4, 6], [16, 4]], 'batch_words': 11776, 'inversion_chunk': 8192, 'stage_b_log': 26, 'stage_b_multiplier': 3, 'stage_b_index_bits': 26, 'stage_b_eval_cost': 281, 'root_table_words': 16384, 'delta_copies': 1, 'o2_extra_point_ops': 6, 'bit_extra_point_ops': 3, 'bit_extra_block_ops': 1, 'outer_decrement_extra': 1, 'direct_row_cap': 0, 'apply_mode': 'block', 'direct_transform_mode': 'single', 'lmax': 67108864, 'block_length': 4194304, 'slab_slots': 16, 'slab_class_log': 18, 'expected_outer_steps': 49, 'expected_squarings': 205, 'expected_multiplies': 45, 'declared': {'degree': 244140625, 'odd_degree': 122070312, 'stage_b_points': 201326592, 'stage_b_evaluations': 402653184, 'stage_b_index_bits': 26, 'graeffe_depth': 24, 'powering_steps': 205, 'powering_multiplies': 45, 'full_points': 134217728, 'truncated_points': 122159104, 'transform_layers': 27, 'hgcd_cap': 22, 'outer_steps': 49, 'tail_degree': 168}}
DECLARED = CONFIG["declared"]
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
RECOVERY_PER_LAYER = CONFIG["recovery_per_layer"]
RECOVERY_PER_POINT = CONFIG["recovery_per_point"]
RECOVERY_FIXED = CONFIG["recovery_fixed"]
BATCH_WORDS = CONFIG["batch_words"]
INVERSION_CHUNK = CONFIG["inversion_chunk"]
STAGE_B_LOG = CONFIG["stage_b_log"]
STAGE_B_MULTIPLIER = CONFIG["stage_b_multiplier"]
STAGE_B_INDEX_BITS = CONFIG["stage_b_index_bits"]
STAGE_B_EVAL_COST = CONFIG["stage_b_eval_cost"]
STAGE_B_POINTS = STAGE_B_MULTIPLIER * (1 << STAGE_B_LOG)
STAGE_B_EVALUATIONS = 2 * STAGE_B_POINTS
ROOT_TABLE_WORDS = CONFIG["root_table_words"]
DELTA_COPIES = CONFIG["delta_copies"]
O2_EXTRA_POINT_OPS = CONFIG["o2_extra_point_ops"]
BIT_EXTRA_POINT_OPS = CONFIG["bit_extra_point_ops"]
BIT_EXTRA_BLOCK_OPS = CONFIG["bit_extra_block_ops"]
OUTER_DECREMENT_EXTRA = CONFIG["outer_decrement_extra"]
DIRECT_ROW_CAP = CONFIG["direct_row_cap"]
APPLY_MODE = CONFIG["apply_mode"]
DIRECT_TRANSFORM_MODE = CONFIG["direct_transform_mode"]
LMAX = CONFIG.get("lmax", 0)
BLOCK_LENGTH = CONFIG.get("block_length", 0)
SLAB_AREA = CONFIG["slab_slots"] * (1 << CONFIG["slab_class_log"])
EXPECTED_OUTER_STEPS = CONFIG["expected_outer_steps"]
EXPECTED_SQUARINGS = CONFIG["expected_squarings"]
EXPECTED_MULTIPLIES = CONFIG["expected_multiplies"]
OUTER_END_DEGREE = CONFIG.get("outer_end_degree", TAIL_DEGREE)

WORD_BYTES = 32
POOL_GAP = 128
PRODUCT_PASS_WIDTH = 7

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
        "entry_exit": 8, "length_tests": 8,
        "descriptor_updates": 12, "result_and_branch_updates": 14,
    },
    "close_31": {
        "entry_exit": 7, "length_tests": 6,
        "descriptor_updates": 8, "result_and_branch_updates": 10,
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
    # The running root, width-1 squarings, remaining constant multiplies and
    # five controls form exactly 2^width+4 events.  Values and all twiddles fit
    # in the declared 256-field-register file for width <= 7.
    group_chain = running_chain(width)
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
    # Each dropped-subtree layer performs the configured charged coefficient
    # events.  RECOVERY_FIXED is the round-specific count of class-batch closes
    # and path reloads; the renderer expands it beside the recovery geometry.
    path = sum(size * NODE_WORDS * (
        RECOVERY_PER_LAYER * depth + RECOVERY_PER_POINT
    )
               for size, depth in RECOVERY_SUBTREES)
    return path + RECOVERY_FIXED


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
    o2 = BOTTOM_BLOCKS * (
        o1_per_block + O2_EXTRA_POINT_OPS * radix
    ) + loop8(BOTTOM_BLOCKS) + 20
    delta_loads = 2 * BOTTOM_BLOCKS
    address_updates = 2 * BOTTOM_BLOCKS
    extra = bit * (
        BIT_EXTRA_POINT_OPS * TRUNCATED_POINTS
        + BIT_EXTRA_BLOCK_OPS * BOTTOM_BLOCKS
    )
    return (o1 + 4 * truncated_middle() + 2 * top_fused() + o2
            + delta_loads + address_updates + 2 * recovery() + extra + 20)


def exponent_bits() -> tuple[int, int]:
    exponent = (PALLAS_P - 1) >> (GRAEFFE_DEPTH + 1)
    bits = bin(exponent)[2:]
    # The scan starts at the monomial residue S^(2^VSHIFT_LOG).  It drops the
    # leading one and the following VSHIFT_LOG high zero bits, not low bits.
    assert set(bits[1:1 + VSHIFT_LOG]) <= {"0"}
    assert (1 << VSHIFT_LOG) < ODD_DEGREE
    active = bits[1 + VSHIFT_LOG:]
    return len(active), active.count("1")


def stage_c_plans() -> int:
    constants = 30
    deltas = TRUNCATED_NODES
    roots = ROOT_TABLE_WORDS
    table_words = constants + DELTA_COPIES * deltas + roots
    # Each word: root recurrence/multiplication, store, address and loop; the
    # node deltas additionally pay an inversion chain of 512 five-op bit steps.
    table_build = ((roots + constants) * 8
                   + DELTA_COPIES * deltas * (512 * 5 + 8))
    exponent_plan = 256 * 3 + fixed_actions("close_42")
    pass_plan = (3 + len(TR_MIDDLE_WIDTHS) + 1) * 64
    zero_fill = (TRUNCATED_POINTS - ODD_DEGREE - 1) * 5 + loop8(
        TRUNCATED_POINTS - ODD_DEGREE - 1
    )
    first_allocations = (
        4 * fixed_actions("allocator_call") + fixed_actions("close_31")
    )
    assert table_words == 30 + DELTA_COPIES * TRUNCATED_NODES + ROOT_TABLE_WORDS
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
    # A running chain is held for one position and reused across every block
    # at that position.  The block's values and 2^k-1 twiddles fit in the
    # declared register file.  Charging the chain per block would describe a
    # different implementation from the executed loop.
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
            + 6 * fixed_actions("allocator_call")
            + fixed_actions("close_42")
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
        row_groups = (matrix_rows + 3) // 4
        assert row_groups >= 1
        transforms = row_groups * (3 * one_forward() + one_inverse())
        matrix_inputs = 4 * 7 * matrix_length
        operand_inputs = 10 * (ODD_DEGREE - degree)
        pointwise = 12 * TRUNCATED_POINTS + loop8(TRUNCATED_POINTS)
        output_loops = 2 * (4 * output + loop8(output))
        fixed = (2 * fixed_actions("allocator_call") + 8 * 23
                 + fixed_actions("close_42"))
        return ApplyCharge(TRUNCATED_POINTS, budget, output, transforms,
                           matrix_inputs, operand_inputs, pointwise,
                           output_loops, fixed)

    candidates: list[ApplyCharge] = []
    required_points = max(output, matrix_length, operand_length)
    for points in admissible_points(required_points):
        assert DIRECT_TRANSFORM_MODE == "single"
        transforms = 6 * transform(points) + 2 * transform(points, inverse=True)
        matrix_inputs = 4 * (
            7 * matrix_length + 5 * (points - matrix_length)
        )
        assert operand_length <= points
        one_operand = 7 * operand_length + 5 * (points - operand_length)
        operand_inputs = 2 * one_operand
        # Per point: four products, two additions/subtractions, two fused
        # inverse scales, and four loads/stores/address shares.
        pointwise = 12 * points + loop8(points)
        output_loops = 2 * (4 * output + loop8(output))
        fixed = (2 * fixed_actions("allocator_call") + 8 * 23
                 + fixed_actions("close_42"))
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
        driver = (3 * fixed_actions("allocator_call") + 20
                  + fixed_actions("planner_key") + 12 + 2 * loop8(1))
        result.append(OuterStep(degree, level, budget, node_bf(level), apply,
                                driver))
        degree -= budget + OUTER_DECREMENT_EXTRA
    assert degree == OUTER_END_DEGREE, (degree, OUTER_END_DEGREE)
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
    "classical_euclid": classical_tail(OUTER_END_DEGREE),
    "normalization": normalization(),
    "entry": fixed_actions("stage_d_entry"),
    "exit_and_frees": fixed_actions("stage_d_exit"),
}
STAGE_D = sum(STAGE_D_COMPONENTS.values())


def planner_components() -> tuple[int, tuple[tuple[str, tuple[int, ...], int], ...]]:
    """Enumerate every run-time planner cache key and finite candidate scan."""
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
    keys.add(("truncated", (FULL_POINTS, TRUNCATED_POINTS,
                              TOP_WIDTH, *TR_MIDDLE_WIDTHS, BOTTOM_WIDTH)))
    for step in OUTER_STEPS:
        if not (APPLY_MODE == "block" and step.degree > LMAX):
            keys.add(("apply", (step.degree, step.budget,
                                  step.apply.output, step.apply.points)))

    rows: list[tuple[str, tuple[int, ...], int]] = []
    for kind, values in sorted(keys):
        if kind == "product":
            left, right, _output = values
            candidates = len(admissible_points(left + right - 1))
        elif kind == "apply":
            degree, budget, output, _points = values
            candidates = len(admissible_points(max(
                output, budget + 1, degree + 1,
            )))
        else:
            candidates = 1
        assert candidates >= 1
        # Decode the immutable key, construct and compare every candidate,
        # then insert the selected plan in the cache.
        charge = (
            fixed_actions("planner_key") + loop8(len(values))
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
    points = STAGE_B_POINTS
    row = 1 << STAGE_B_LOG
    evaluations = 2 * points * STAGE_B_EVAL_COST
    # Per point: two point adds, subtraction, quotient multiply, two root
    # recurrences, store+address, loop controls, and the configured reversal
    # by one shift/test pair per bit plus entry/exit.
    # The bit-reversed index is deliberately charged at eleven primitive word
    # events for each index bit: mask load, value load, two ANDs, two
    # shifts, OR, value store, bit test, branch, and loop update.
    evaluation_loop = points * (
        2 + 1 + 1 + 2 + 2 + 3 + 11 * STAGE_B_INDEX_BITS + 2
    )
    if STAGE_B_MULTIPLIER == 3:
        inverse_transform = 8 * row + 3 * table_row_transform(
            STAGE_B_LOG, inverse=True
        )
    else:
        assert STAGE_B_MULTIPLIER == 1
        inverse_transform = table_row_transform(STAGE_B_LOG, inverse=True)
    table_words = points // 2
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
    "entry_exit": 8,
    "array_descriptors": 16,
    "degree_and_bounds": 8,
    "buffer_swaps": 8,
    "final_tests": 8,
    "call_frames": 16,
}
STAGE_E_POWER_COPY_ACTIONS = {
    "source_load": 1,
    "destination_store": 1,
    "source_and_destination_updates": 2,
    "loop_update_test_branch": 3,
}
STAGE_E_POWER_FIXED_ACTIONS = {
    "entry_exit": 4,
    "buffer_swap": 4,
    "length_and_degree_tests": 8,
    "source_and_destination_descriptors": 8,
    "exponent_bit_test_and_branch": 4,
    "call_and_return": 3,
}
STAGE_E_GCD_CELL_ACTIONS = {
    "active_mask_and_degree_test": 2,
    "coefficient_loads": 3,
    "field_multiply": 1,
    "field_subtract": 1,
    "coefficient_store": 1,
    "loop_update_test_branch": 3,
    "address_update": 1,
}


def stage_e_round_components(degree: int = 16) -> dict[str, int]:
    """One constant-work isolation round for a factor of degree <= 16.

    Pseudocode: draw a fresh shift; evaluate H(-a); initialize X+a;
    square-and-multiply (X+a)^((p-1)/2) mod H; form P-1 and P+1;
    execute two padded Euclidean gcds; select and copy one proper factor.
    Every padded loop runs to its declared maximum even if a linear factor is
    found early, so this is the exact charged upper for one round.
    """
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
    power_step = (
        modular_product
        + coefficients * sum(STAGE_E_POWER_COPY_ACTIONS.values())
        + sum(STAGE_E_POWER_FIXED_ACTIONS.values())
    )
    one_gcd = (
        degree * coefficients * coefficients * sum(STAGE_E_GCD_CELL_ACTIONS.values())
        + 18 * coefficients
        + 80
    )
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
ROOT_LIFT_ACTIONS = {
    "fixed_square_and_multiply_field_events": 45_056,
    "two_adic_table_load_store_and_address_events": 1_280,
    "candidate_root_tests_and_selects": 512,
    "entry_exit_loop_and_descriptor_events": 164,
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
    (GRAEFFE_DEPTH + 1) * sum(ROOT_LIFT_ACTIONS.values())
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
        self.slab_live: dict[str, tuple[int, int]] = {}
        self.slab_counts: dict[int, int] = {}
        self.slab_peaks: dict[int, int] = {}
        self.raw_live: dict[str, int] = {}
        self.raw_peak = 0
        self.peak = 0
        self.stage_peaks: dict[str, int] = {}

    def _record(self, stage: str, action: str, name: str,
                side: str, size: int) -> None:
        live = (
            sum(segment.size for pool in (self.low, self.high)
                for segment in pool.segments if segment.live)
            + sum(size for _size_class, size in self.slab_live.values())
            + sum(self.raw_live.values())
        )
        extent_sum = self.low.extent + self.high.extent
        event = MemoryEvent(len(self.events) + 1, stage, action, name, side,
                            size, self.low.extent, self.high.extent,
                            extent_sum, live)
        self.events.append(event)
        self.peak = max(self.peak, extent_sum)
        self.stage_peaks[stage] = max(self.stage_peaks.get(stage, 0), live)

    def alloc(self, stage: str, name: str, words: int,
              side: str = "L", force_pool: bool = False) -> None:
        assert name not in self.sizes
        size = block_bytes(words)
        if size <= (1 << 14) and not force_pool:
            size_class = 1 << max(7, (size - 1).bit_length())
            self.sizes[name] = (f"S{size_class}", size_class)
            self.slab_live[name] = (size_class, size_class)
            self.slab_counts[size_class] = self.slab_counts.get(size_class, 0) + 1
            self.slab_peaks[size_class] = max(
                self.slab_peaks.get(size_class, 0), self.slab_counts[size_class]
            )
            self._record(stage, "alloc", name, f"S{size_class}", size_class)
            return
        pool = self.low if side == "L" else self.high
        pool.allocate(name, size)
        self.sizes[name] = (side, size)
        self._record(stage, "alloc", name, side, size)

    def free(self, stage: str, name: str) -> None:
        side, size = self.sizes.pop(name)
        if side.startswith("S"):
            size_class, _allocated = self.slab_live.pop(name)
            self.slab_counts[size_class] -= 1
            self._record(stage, "free", name, side, size)
            return
        pool = self.low if side == "L" else self.high
        pool.free(name)
        self._record(stage, "free", name, side, size)

    def alloc_raw(self, stage: str, name: str, size: int) -> None:
        assert name not in self.sizes and name not in self.raw_live and size >= 0
        self.sizes[name] = ("R", size)
        self.raw_live[name] = size
        self.raw_peak = max(self.raw_peak, sum(self.raw_live.values()))
        self._record(stage, "alloc", name, "R", size)

    def free_raw(self, stage: str, name: str) -> None:
        side, size = self.sizes.pop(name)
        assert side == "R" and self.raw_live.pop(name) == size
        self._record(stage, "free", name, "R", size)

    def shrink(self, stage: str, name: str, words: int) -> None:
        side, old_size = self.sizes[name]
        assert side in ("L", "H")
        new_size = block_bytes(words)
        assert new_size <= old_size
        pool = self.low if side == "L" else self.high
        pool.shrink(name, new_size)
        self.sizes[name] = (side, new_size)
        self._record(stage, "shrink", name, side, new_size)

    def retain(self, stage: str, name: str, source: str,
               minimum_words: int) -> None:
        """Record an existing live block as an in-place padded operand."""
        side, size = self.sizes[source]
        assert side in ("L", "H")
        assert size >= block_bytes(minimum_words)
        self._record(stage, "retain", name, side, size)

    def release_retained(self, stage: str, name: str, source: str) -> None:
        side, size = self.sizes[source]
        assert side in ("L", "H")
        self._record(stage, "release-retained", name, side, size)


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


def memory_walk() -> ArenaWalk:
    walk = ArenaWalk()
    # A: output polynomial allocation.
    walk.alloc("A", "A-g", TRUNCATED_POINTS, "H")
    walk.free("A", "A-g")

    # B: evaluation array, transform table and resulting coefficient array.
    walk.alloc("B", "B-values", STAGE_B_POINTS, "H")
    walk.alloc("B", "B-table", STAGE_B_POINTS // 2, "H")
    walk.alloc("B", "g", TRUNCATED_POINTS, "L")
    walk.free("B", "B-table")
    walk.free("B", "B-values")

    # C: table construction, Graeffe scratch, Newton/quotient work, then the
    # four long-lived value arrays.  Temporary phases do not overlap unless the
    # algorithm consumes both objects at once.
    walk.alloc("C", "root-tables",
               30 + DELTA_COPIES * TRUNCATED_NODES + ROOT_TABLE_WORDS, "L")
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
    # q stays in coefficient form until this n'-word destination has been
    # filled by its truncated evaluation.  Only then is q released.
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

    # D: node bump arena is not live with apply storage.  Block and truncated
    # applies retain their declared workspaces.  A direct apply holds all four
    # matrix entries and both operands, each padded to the selected covering
    # transform length, through the six forward transforms.
    for index, step in enumerate(OUTER_STEPS, 1):
        bump = 16 * (1 << step.level) - 256
        walk.alloc("D", f"D{index}-node", bump, "L")
        walk.free("D", f"D{index}-node")
        if APPLY_MODE == "block" and step.degree > LMAX:
            walk.alloc("D", f"D{index}-matrix", 4 * (step.budget + 1), "L")
            walk.alloc("D", f"D{index}-row-a", 4 * BLOCK_LENGTH, "H")
            walk.alloc("D", f"D{index}-row-b", 4 * BLOCK_LENGTH, "H")
            walk.alloc("D", f"D{index}-accumulator", 12 * BLOCK_LENGTH, "L")
            walk.alloc("D", f"D{index}-overlap", 4 * BLOCK_LENGTH, "L")
            walk.free("D", f"D{index}-overlap")
            walk.free("D", f"D{index}-accumulator")
            walk.free("D", f"D{index}-row-b")
            walk.free("D", f"D{index}-row-a")
            walk.free("D", f"D{index}-matrix")
        elif (APPLY_MODE == "truncated"
              and step.apply.points == TRUNCATED_POINTS
              and step.apply.output > DIRECT_ROW_CAP):
            walk.alloc("D", f"D{index}-matrix", 4 * (step.budget + 1), "L")
            walk.alloc("D", f"D{index}-transform", step.apply.points, "L")
            walk.free("D", f"D{index}-transform")
            walk.free("D", f"D{index}-matrix")
        else:
            required = max(
                step.apply.output, step.budget + 1, step.degree + 1,
            )
            assert step.apply.points >= required
            padded_bytes = block_bytes(step.apply.points)
            reuse_operands = all(
                walk.sizes[name][1] >= padded_bytes
                for name in ("g", "A-O1")
            )
            matrix_operands = 4 if reuse_operands else 6
            if reuse_operands:
                walk.shrink("D", "g", step.apply.points)
                walk.shrink("D", "A-O1", step.apply.points)
            for operand in range(1, matrix_operands + 1):
                walk.alloc(
                    "D", f"D{index}-forward-{operand}", step.apply.points,
                    "L" if operand % 2 else "H", force_pool=True,
                )
            if reuse_operands:
                walk.retain("D", f"D{index}-forward-5", "g", step.apply.points)
                walk.retain("D", f"D{index}-forward-6", "A-O1", step.apply.points)
                walk.release_retained(
                    "D", f"D{index}-forward-6", "A-O1",
                )
                walk.release_retained("D", f"D{index}-forward-5", "g")
            for operand in range(matrix_operands, 0, -1):
                walk.free("D", f"D{index}-forward-{operand}")

    walk.free("D", "root-tables")
    walk.free("D", "A-O1")
    walk.free("D", "g")

    # E: one maximum-degree constant-work isolation round.  Later rounds reuse
    # the same slab slots.
    for name, words in (
        ("E-factor", 17), ("E-base", 17), ("E-power-result", 17),
        ("E-product-scratch", 33), ("E-P-minus-one", 17),
        ("E-P-plus-one", 17), ("E-gcd-left", 17), ("E-gcd-right", 17),
        ("E-selected-factor", 17), ("E-random-words", 2),
    ):
        walk.alloc("E", name, words)
    for name in (
        "E-random-words", "E-selected-factor", "E-gcd-right", "E-gcd-left",
        "E-P-plus-one", "E-P-minus-one", "E-product-scratch",
        "E-power-result", "E-base", "E-factor",
    ):
        walk.free("E", name)

    for name, words in (
        ("F-root-chain", 32), ("F-candidate-state", 16),
        ("F-input-pair", 4), ("F-line-state", 6),
    ):
        walk.alloc("F", name, words)
    for name in ("F-line-state", "F-input-pair", "F-candidate-state", "F-root-chain"):
        walk.free("F", name)

    for name, words in (
        ("G-two-input-pairs", 4), ("G-two-poseidon-states", 6),
        ("G-canonical-encodings", 4), ("G-output-elements", 2),
    ):
        walk.alloc("G", name, words)
    for name in ("G-output-elements", "G-canonical-encodings",
                 "G-two-poseidon-states", "G-two-input-pairs"):
        walk.free("G", name)

    # Stack frames are traced as separate live call chains.  Independent phase
    # frames are never added together.
    chains = {
        "sampling": ("runtime_entry", "line_and_sampler"),
        "stage_c_transform": ("runtime_entry", "stage_c_driver",
                              "seven_transform_frames", "product_planner", "allocator"),
        "stage_d_half_gcd": ("runtime_entry", "half_gcd_frames", "allocator"),
        "stage_e_isolation": ("runtime_entry", "isolation", "allocator"),
        "stage_f_g_output": ("runtime_entry", "encoding_and_output"),
        "offline_generation": ("offline_generator",),
    }
    for chain, frames in chains.items():
        for frame in frames:
            walk.alloc_raw("stack", f"{chain}:{frame}", STACK_FRAMES[frame])
        for frame in reversed(frames):
            walk.free_raw("stack", f"{chain}:{frame}")

    assert not walk.sizes
    assert not walk.slab_live and not walk.raw_live
    assert walk.low.extent == 0 and walk.high.extent == 0
    return walk


ALLOCATOR = memory_walk()
SLAB_CLASSES = dict(ALLOCATOR.slab_peaks)
SLAB_EVENTS = tuple(
    (f"slab-class-{size}", slots, slots * size)
    for size, slots in sorted(SLAB_CLASSES.items()) if slots
)
SLAB_AREA = sum(size for _name, _slots, size in SLAB_EVENTS)
SLAB_HEADS = len(SLAB_EVENTS) * WORD_BYTES
ARENA = ALLOCATOR.peak + POOL_GAP + SLAB_AREA + SLAB_HEADS

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
OFFLINE_FRAMES = {
    "sixteen_field_words": 16 * WORD_BYTES,
    "hex_digit_buffer": 64,
}
OFFLINE_WORKING = sum(OFFLINE_FRAMES.values())
STACK_LIVE = ALLOCATOR.raw_peak
STACK = ((STACK_LIVE + 16_383) // 16_384) * 16_384


@dataclass(frozen=True)
class CompleteResidentEvent:
    number: int
    stage: str
    action: str
    name: str
    region: str
    bytes: int
    live_bytes: int


def complete_memory_events() -> tuple[CompleteResidentEvent, ...]:
    events: list[CompleteResidentEvent] = []
    fixed_live = 0
    for name, size in (
        ("code-and-static", CODE_AND_STATIC),
        ("register-file", REGISTER_FILE),
        ("offline-workspace", OFFLINE_WORKING),
        ("stack-reservation", STACK),
        ("arena-middle-gap", POOL_GAP),
        ("slab-class-reservations", SLAB_AREA),
        ("slab-free-list-heads", SLAB_HEADS),
    ):
        fixed_live += size
        events.append(CompleteResidentEvent(
            len(events) + 1, "fixed", "reserve", name, "fixed", size,
            fixed_live,
        ))
    for event in ALLOCATOR.events:
        events.append(CompleteResidentEvent(
            len(events) + 1, event.stage, event.action, event.name, event.side,
            event.size, fixed_live + event.extent_sum,
        ))
    return tuple(events)


COMPLETE_MEMORY_EVENTS = complete_memory_events()
MEMORY_BYTES = max(event.live_bytes for event in COMPLETE_MEMORY_EVENTS)

RAW_TIME = (Decimal(N_MAX).ln() - Decimal(COMPRESSION).ln()) / Decimal(2).ln()
TIME_CLAIM = ceil_decimal(RAW_TIME, 5)
RAW_MEMORY = Decimal(MEMORY_BYTES).ln() / Decimal(2).ln()
MEMORY_CLAIM = ceil_decimal(RAW_MEMORY, 5)
SCORE = TIME_CLAIM + max(Decimal(0), MEMORY_CLAIM - Decimal(20))


def validate() -> None:
    # These assertions bind each priced geometry to the independent dimensions
    # stated in the algorithm section.  A renderer substitution that changes a
    # transform size without changing the declaration fails here.
    assert DEGREE == 5 ** (ROUNDS + 6) == DECLARED["degree"]
    assert ODD_DEGREE == (DEGREE - 1) // 2 == DECLARED["odd_degree"]
    assert STAGE_B_POINTS == DECLARED["stage_b_points"]
    assert STAGE_B_EVALUATIONS == 2 * STAGE_B_POINTS
    assert STAGE_B_EVALUATIONS == DECLARED["stage_b_evaluations"]
    assert STAGE_B_INDEX_BITS == DECLARED["stage_b_index_bits"]
    assert GRAEFFE_DEPTH == DECLARED["graeffe_depth"]
    assert exponent_bits() == (
        DECLARED["powering_steps"], DECLARED["powering_multiplies"]
    )
    assert FULL_POINTS == DECLARED["full_points"]
    assert TRUNCATED_POINTS == TRUNCATED_NODES * NODE_WORDS
    assert TRUNCATED_POINTS == DECLARED["truncated_points"]
    assert TOP_WIDTH + sum(TR_MIDDLE_WIDTHS) + BOTTOM_WIDTH == CONFIG["full_log"]
    assert CONFIG["full_log"] == DECLARED["transform_layers"]
    assert ELL == VSHIFT + TRUNCATED_POINTS - ODD_DEGREE + 1
    assert HGCD_CAP == DECLARED["hgcd_cap"]
    assert TAIL_DEGREE == DECLARED["tail_degree"]
    assert OUTER_END_DEGREE == DECLARED.get("outer_end_degree", TAIL_DEGREE)
    assert COMPRESSION == 216 + 21 * ROUNDS
    assert base_node() == 105_140
    assert len(OUTER_STEPS) == EXPECTED_OUTER_STEPS == DECLARED["outer_steps"]
    assert exponent_bits() == (EXPECTED_SQUARINGS, EXPECTED_MULTIPLIES)
    assert OUTER_STEPS[0].degree == ODD_DEGREE
    for current, following in zip(OUTER_STEPS, OUTER_STEPS[1:]):
        assert current.level <= HGCD_CAP
        assert current.budget == (1 << current.level) - 1
        assert following.degree == (
            current.degree - current.budget - OUTER_DECREMENT_EXTRA
        )
    last = OUTER_STEPS[-1]
    assert last.degree - last.budget - OUTER_DECREMENT_EXTRA == OUTER_END_DEGREE
    for step in OUTER_STEPS:
        points = step.apply.points
        if points != TRUNCATED_POINTS:
            row = points if points & (points - 1) == 0 else points // 3
            assert row & (row - 1) == 0
        assert step.apply.output == step.degree - step.budget
    assert classical_tail(OUTER_END_DEGREE) == sum(
        16 * degree + 27 for degree in range(1, DECLARED["tail_degree"] + 1)
    )
    assert PLAN_MISSES == sum(row[2] for row in PLANNER_ROWS)
    assert OFFLINE_EXACT == OFFLINE_CHARGE
    assert SLAB_AREA == sum(row[2] for row in SLAB_EVENTS)
    assert OFFLINE_WORKING == sum(OFFLINE_FRAMES.values()) == 576
    assert STACK >= STACK_LIVE and STACK - STACK_LIVE < 16_384
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
    print("planner_rows", PLANNER_ROWS)
    print("ledger", LEDGER)
    print("n_max", N_MAX)
    print("allocator_events", len(ALLOCATOR.events))
    print("stage_peaks", ALLOCATOR.stage_peaks)
    print("pool_high_water", ALLOCATOR.peak)
    print("arena", ARENA)
    print("memory_components", {
        "arena": ARENA, "code_static": CODE_AND_STATIC,
        "register_file": REGISTER_FILE, "offline_working": OFFLINE_WORKING,
        "stack": STACK, "stack_live": STACK_LIVE,
        "slab_events": SLAB_EVENTS,
    })
    print("memory_bytes", MEMORY_BYTES)
    print("raw_time", RAW_TIME, "time_claim", TIME_CLAIM)
    print("raw_memory", RAW_MEMORY, "memory_claim", MEMORY_CLAIM)
    print("score", SCORE)


if __name__ == "__main__":
    main()
```
