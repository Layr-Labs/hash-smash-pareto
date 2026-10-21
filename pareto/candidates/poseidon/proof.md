# Orchard Poseidon r4: full union-machine ledger

## 1. Claim

The selected target is `poseidon-orchard-r4-prefix-v1`: P128Pow5T3 over Pallas with partial rounds 4 through 7 and the fixed eight full rounds. The attack class is ordinary collision search. One centre is sampled and the construction uses the published line, odd part, 20-step Graeffe prefix, exact value-domain Montgomery powering and inversion-free half-gcd.

The complete integer ledger gives `N_max = 349,370,330,527`. At 300 primitive operations per target compression, `time_log2 = 30.11715`. The event-by-event allocator walk and fixed regions give 630,718,112 bytes, `memory_log2_bytes = 29.23243`. Applying the lane's stated scalar formula gives normalized cost `39.34958`. For comparison context only, the arithmetic differences from our current `39.39329` entry and the published `39.39329` reference are `0.04371` and `0.04371`. These differences are not a ranking model or evidence for the cost derivation.

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

4.1.3 Stage F: the root of `g_c` above `y`. Stage F takes exactly `d+1 = 21` successive square roots, each charged 47,012 operations, then scans all `2^20 = 1,048,576` candidates in the worst case. A candidate costs `490`: one root update, two point additions, two line evaluations at `239` operations, four calls, comparison and branch, and three loop controls. The exit costs two operations and the final back-map costs 47,012. Thus row F is `21*47,012 + 2^20*490 + 2 + 47,012 = 514,836,506`. The scan stops only after the line equality holds, and stage G then verifies both complete reference hashes.

Stage B prices `H = 6,291,456` points and `2H = 12,582,912` line evaluations. Its bit-reversed row index has `b = 21` executed bits, the radix-2 row width named by the Stage-B plan, so its per-point loop charge is `13 + 11b = 244`. The ledger assertion binds `b`, `H` and `2H` to the algorithm declaration.

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

The 23 truncated layers use `3 | 7,4,4 | 5`. Four adjacent middle blocks share a running group chain; the ledger asserts exact divisibility. Newton, quotient and every outer apply are recomputed from the same transform primitives. A direct outer apply is limited to 24 rows of `2^16` coefficients; larger outputs use the truncated path. The matrix-row group count is derived from the live budget. A direct candidate must cover the output, every matrix entry and both operands before its one six-forward/two-inverse execution.

The arena allocator has a 64-byte header and a payload rounded to 64 bytes. Large blocks use a two-ended first-fit pool. Appendix E.3 lists every allocation and free, its side, both extents and live bytes. Stage B alone retains a transform twiddle table. The root tables of the truncated transform remain. Stages C and D form product twiddles in registers.

### 4.3G The Graeffe prefix

Definition. For `h` monic of even degree `m` write `h(X) = E(X^2) + X O(X^2)`; its Graeffe transform is `h~(Y) = E(Y)^2 - Y O(Y)^2`, so `h~(X^2) = h(X) h(-X)` and `h~` is monic of degree `m` with roots the squares of the roots of `h` (with multiplicity). Stage C first replaces `g = g_c` by `g^(20)`, 20 Graeffe steps, then computes `R = S^e mod g^(20)`, `e = (p-1)/2^21` (2-adicity 32), and stage D takes `G = gcd(g^(20), R - 1)`.

Lemma. `G` is the product of `(Y - y)` over the distinct values `y = S^(2^20)`, `S` a usable root of `g_c` (a nonzero square in `F_p` with `g_c(S) = 0`, section 3). Proof: `g^(20)(Y) = prod_i (Y - S_i^(2^20))` over the roots `S_i` of `g_c` in an algebraic closure; `Y^e - 1` is squarefree and its roots are the `2^21`-th powers of `F_p^*`. If `S_i^(2^20) = u^(2^21)` with `u` in `F_p^*`, then `S_i = u^2 zeta` with `zeta^(2^20) = 1`, so `zeta` is in `F_p` and `zeta = xi^2` with `xi^(2^21) = 1` (`2^21 | p - 1`), and `S_i = (u xi)^2` is a nonzero square of `F_p`; conversely `S = v^2` gives `S^(2^20) = v^(2^21)`. So `deg G` is the number of distinct `2^20`-th powers of the usable roots: `1 <= deg G <= k(c)` when `k(c) >= 1`, and `deg G = 0` when `k(c) = 0`; the event `E_c` of 9.2 gives `1 <= deg G <= DMAX`.

Execution (on the point set `O1` of 4.3T). Appendix E.1 derives the Graeffe step directly from the live top, middle, bottom and recovery kernels. 20 steps precede the fixed exponent `E = (p-1)/2^21`. This exponent has bit length 234. Its leading one is followed by at least 19 high zero bits, so the scan starts from the monomial residue `S^(2^19)`; `2^19 < m`, hence that monomial is its own reduction. The remaining `234-1-19 = 214` bits cost one squaring each, and the remaining popcount minus one gives 45 multiply-by-`S` steps. No low bits are discarded.

Every map is exact; no premise is added to the time or the memory. The zero test of `k1` (4.3T) now concerns `g^(20)`: `g^(20)(y) = 0` for `y` in `O1` only if `g_c(x) = 0` for one of the `2^20` values `x` with `x^(2^20) = y` (in `F_p` or an extension); for each such `x`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g^(20) vanishes on O1) <= 2^20 n' (D - 1) / p = eps_g < 2^-188`.

### 4.3T Stage C in the value domain on truncated point sets (the method of bradcush `b30de9bf`/`a41aecdd`, 75 of 128 nodes)

Point sets. `N = 2^23` divides `p - 1` (2-adicity 32). Let `psi` have order `2^24`, `H_N = <psi^2>` and `Y = X^(2^16)`. `H_N` is the union of the 128 depth-7 nodes `{x : x^(2^16) = r_j}`, `r_j` the 128-th roots of unity in transform (bit-reversed) order; `O1` is the union of the first 75 nodes, `n' = 75 * 2^16 = 4,915,200 >= m + 1 = 4,882,813` points, and `O2` the same 75 nodes of the coset `psi H_N` (`x^(2^16) = r'_j`, `r'_j^128 = -1`), disjoint from `O1`. `P1 = prod_{j<75} (Y - r_j)` has degree `n'`, vanishes on `O1` and is the nonzero constant `P1(r'_j)` on node `j` of `O2`; `delta_j = 1/P1(r'_j)` (75 table constants).

Truncated transforms (bradcush `b30de9bf` 4.3, generalized from van der Hoeven's truncated Fourier transform). A polynomial of degree below `n'` is represented on the first 75 depth-7 nodes. The forward top covers all `N/2^3` offsets. The middle acts only on live nodes, in passes of 7, 4, 4 layers; the widest radix fits exactly in the declared register file. The bottom acts on `2^5`-point blocks. The inverse reverses these passes and recovers the maximal dropped subtrees `(1,7), (4,5), (16,3), (32,2)`. One recovery charges `size * 2^16 * (8*depth+2)` over those pairs. Each layer's ten events are two source-address updates, two loads, two butterfly field operations, two stores and two destination-address updates. The fixed close is `4*(2^16/2^10) = 131,072` operations: one close operation for each of four streams in every `2^10`-word chunk.

The top, middle and recovery layers are class-batched in the 8,192-word buffer. Each middle width has exactly `n'/2^k` blocks; four adjacent blocks share one chain. The script charges every block body, every group chain and every fixed wrapper. The top position loops use `F(N/2^3)`. Fused top passes enumerate loads, stores, both butterfly directions, active coset products and the offset-zero saving. Bottom kernels enumerate their loads, butterflies, point operations, pointer updates and four-block control. The exact maps and dropped-subtree recovery are unchanged; only the machine realization is repriced.

Montgomery powering (`b30de9bf` 4.5). For residues of degree `< n'`, `Mont(A, B) = (A B + u g)/P1` with `u = -A B / g mod P1` (`deg u < n'`); the division by `P1` is exact, `Mont(A, B) = A B / P1 mod g`, and `deg Mont(A, A) <= n' - 2`, so `X Mont(A, A)` has degree `< n'`. A residue `A` (representing `S^e P1`) is held by its values on `O1` and on `O2`, each up to a tracked scalar. One step: `U = A^2 k1` on `O1` (`k1 = -1/(N^3 g)` there; `u` is determined by its values on `O1`); `U` to `O2` (truncated inverse on `O1`, truncated forward on `O2`); `B2 = (A2^2 + U g) delta_j` on node `j` of `O2`, which is `Mont(A, A)` up to the tracked scalar because `P1 = 1/delta_j` there, times the point `x` when the exponent bit is 1; `B2` to `O1` (truncated inverse on `O2`, truncated forward on `O1`). No `1/N` is executed inside the steps (the scalars are tracked, 2 operations per step). Per point and step: on `O1` `sqr, LD k1, mul` (4); on `O2` `LD A2, sqr, LD g, mul, add`, the multiplication by `delta_j`, `ST` (10) and the load of `delta_j` per block (2); 3 more for a 1-bit (the load of the point and a multiplication).

Entry and exit. `g` (coefficients after the Graeffe prefix of 4.3G, its slots above `m` zero) goes to `O1` and `O2` (a truncated forward each; every scaling of this section, `1/N` and the coset twist, is a running product fused into the adjacent pass, 2 operations per point). The start residue is `A0 = X^v P1 mod g`, `v = 2^19 = 524,288` (VSHIFT_LOG = 19 HIGH zero bits immediately after the leading one): `q = floor(X^v P1 / g)` has `ell = v + n' - m + 1 = 556,677` coefficients and is formed from the Newton reciprocal of the reversed `g` and one product (transforms of up to `3*2^19` points, with running twiddle factors and no stage product table); on node `j` of `O2`, `x^v P1(x) = r'_j^8 P1(r'_j)` is a constant, so `A0 = x^v P1 - q g` there is one truncated forward of `q` and one pointwise pass (8 per point); then `A0` goes to `O1`. `k1` is formed by chunked batch inversion on `O1` (chunks of `2^13` points: prefix products, one inversion, two multiplications per point; the `2^13` prefixes are kept in the batch buffer, which no transform uses at that time); each chunk product is tested for zero before its inversion (2 per chunk), and a zero ends the trial: for fixed `x != 0`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g vanishes on O1) <= eps_g < 2^-188` for the transformed `g` (4.3G, 9.2). The exit is one step with multiplier 1 (`Mont(A, 1)`) and two truncated inverses with their scaling, which return `kappa R` (`kappa` the tracked scalar) and `g` in coefficient form; the gcd is scale-invariant, so stage D receives `kappa R - kappa`. There are `214` squaring steps (the exponent `(p-1)/2^21`, 4.3G), `45` of them also multiplying by `S`.

Exactness and memory. Every map above is exact: the
Montgomery products act on polynomials of degree below `n'`, represented
bijectively by their values on the live nodes. Stage C adds no premise. Its
live set contains four 4,915,200-word value arrays, one
8,192-word batch buffer, 16,489 words of constants,
node deltas and root tables, and the Newton reciprocal, Barrett quotient and
transform workspaces for the lifetimes in Appendix E.4. Appendix E.1 is
rendered from `STAGE_C_COMPONENTS` and gives **row C = 270,631,678,025**.

### 4.4 Stage D: the inversion-free half-gcd (the method of bradcush `b30de9bf`/`4bcabff8`)

`G = gcd(g, R - 1)` is computed by a recursive half-gcd on the normal remainder sequence that keeps every matrix in coefficient form and never inverts a leading coefficient (pseudo-division). A node `hgcd(a, b, k)` of budget `k = 2^j - 1` runs its first child (budget `2^(j-1) - 1`) on the top window, applies the child's matrix `M1`, `(c, d) = adj(M1)(a, b)`, makes one pseudo-division with a quotient of degree 1 (its remainder `e` only on the `2^j - 1` positions the second child reads), runs the second child (`M2`) and forms `M = M1 [[Q, 1], [b^2, 0]] M2`. The apply of a node is formed on the three rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), one transform of `n` points per row in the block form of `27fbfbe7` 4.2 (the twist of the rows `Y + 1`, `Y - i` as a running product fused into the pass; E.2.1), and recombined by a 3-row CRT (22 operations per position); the product `M` on the two rows `Y - 1`, `Y + 1` only, recombined by the 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` (10 operations per position, the `1/2` folded into the `1/n` of the inverse). The product needs no third row: on the normal sequence every quotient has degree 1 and `b^2` is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; the values of each child's matrix on the row `Y - 1` are reused by its parent, the values of `M1` from the apply are reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). The base case is budget `2^6 - 1`, two remainder steps per pass.

The driver: while the degree `n` of `g` admits it, `k = 2^j - 1` is the largest with `2k + 1 <= n` and `k <= KMAX = 2^19 - 1` (the outer-step cap of weijiekoh `a78f526e`), `hgcd(k)` runs on the top window and its matrix is applied to `(g, R)` in place (`plan_apply`: the cheapest of the truncated transform of 4.3T on `n'` points, a `2^a`-point or a `3*2^a`-point transform; the entries of `M` row by row of `2^16` points when the transform has at least `2^17` points; `1/N` fused into the pointwise loop, 1 operation per point); from degree 148 down the schoolbook pseudo-division Euclid, then the normalisation of `G`. Every node works in one bump arena (allocation and release 10 operations each), `node_mem(j)` words at its peak (`8,388,352` at `j = 19`). On the normal sequence every length, parameter and allocation is a function of `m` alone: 24 outer steps (six on the truncated transform of `n'` points, then `3*2^19`- down to `3*2^6`-point plans) and the Euclid from degree 148.

Appendix E.2 gives **row D = 73,233,041,372**.

Stage-D binding. The inversion-free node cap is `j <= 19` and the base case is budget 63 (`j = 6`). The driver executes 24 outer steps. Each step chooses the largest admissible budget `2^j-1` and decrements the degree by the generated budget `2^j-1`. It reaches degree 148; classical Euclid then runs directly from degree 148. There is no lean-tail literal. The apply mode is `truncated`: outputs above 24 rows of `2^16` coefficients use the generated truncated path, and smaller outputs use the finite direct-plan search at a length covering every input and output. Appendix E.2 prices every node, apply and driver row.

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to two distinct canonical pairs with equal digests. Stage D returns `G = gcd(g, R - 1)`, whose roots are the values `y = S^(2^20)` of the usable roots `S` of `g_c` (4.3G); stage F stops only at an `s != 0` with `F(c + s) = F(c - s)` (4.1.3), so `W1 = c + s != c - s = W2`. Stage G verifies both inputs with the reference hash before the algorithm outputs, so a returned pair is a verified collision.

## 6. Complete operation ledger

| row | event family | operations |
| --- | --- | ---: |
| init | runtime constants and bookkeeping | 18,009 |
| setup | line setup | 4,843 |
| A | coin draw, reduction and allocation | 1,228 |
| B | line evaluations, loop, table transform and normalization | 4,847,442,763 |
| C | Graeffe prefix and exact value-domain powering | 270,631,678,025 |
| D | inversion-free half-gcd normal walk with ABORT | 73,233,041,372 |
| E | 64 isolation rounds at degree at most 16 | 139,023,366 |
| F | 21 square roots, full 2^20 candidate scan and back-map | 514,836,506 |
| G | two reference verifications | 7,412 |
| trial loop | reset and closing control | 1,012 |
| plan misses | 67 enumerated immutable planner keys | 75,442 |
| output | two fixed output rows | 4,063,392 |
| offline | four named literal-generation loops | 137,157 |
| **N_max** | `T_fixed + T_trial + T_off` | **349,370,330,527** |

`T_fixed = 4,161,686`, `T_trial = 349,366,031,684` and `T_off = 137,157`. Their sum is `N_max = 349,370,330,527`. The exact raw time is `log2(N_max/300) = 30.1171474491585089437157262361870496765003932346294474455736896294807991570385142427900369`; upward rounding at five decimals gives `30.11715`.

All searches remain in the row that executes them. Stage E contains 64 complete isolation rounds. Stage F contains every one of the `2^20 = 1,048,576` candidates. The planner row enumerates every distinct Newton-product, quotient-product, transform, truncated-layout and direct-apply key and every candidate length tested for it. The offline constants take exactly 137,157 operations: 202 input literals at 324 operations, `4*501+3*222` field and bit-loop operations, `3*90` word operations, and 212 output literals at 324 plus one 81-operation short literal. The package contains no empirical timing conversion.

### 6.1 Exact-integer evidence

The exact-integer script embedded in Appendix X computes the geometry from `5^10`, constructs every transform and product plan, expands rows C and D, generates all 24 outer steps, walks all allocator events and derives both logarithms. Its assertions require the priced Stage-B point count to equal the declared `H`, the evaluation count to equal `2H`, and the Graeffe depth, powering steps, transform layers, truncated size, half-gcd cap, outer-step sequence and classical-tail start to equal the independent dimensions stated by the algorithm. It has no prior row total, prior `N_max`, prior memory peak or score as an input.

The complete configuration binding is `{"active_top_cosets": 5, "apply_mode": "truncated", "batch_words": 8192, "bit_extra_block_ops": 1, "bit_extra_point_ops": 3, "bottom_width": 5, "declared": {"degree": 9765625, "full_points": 8388608, "graeffe_depth": 20, "hgcd_cap": 19, "odd_degree": 4882812, "outer_steps": 24, "powering_multiplies": 45, "powering_steps": 214, "stage_b_evaluations": 12582912, "stage_b_index_bits": 21, "stage_b_points": 6291456, "tail_degree": 148, "transform_layers": 23, "truncated_points": 4915200}, "delta_copies": 1, "direct_row_cap": 1572864, "direct_transform_mode": "single", "expected_multiplies": 45, "expected_outer_steps": 24, "expected_squarings": 214, "full_log": 23, "graeffe_depth": 20, "hgcd_cap": 19, "inverse_top_core": 48, "inversion_chunk": 8192, "middle_widths": [7, 4, 4], "node_log": 16, "o2_extra_point_ops": 6, "outer_decrement_extra": 0, "recovery_fixed": 131072, "recovery_per_layer": 8, "recovery_per_point": 2, "recovery_subtrees": [[1, 7], [4, 5], [16, 3], [32, 2]], "root_table_words": 16384, "rounds": 4, "slab_class_log": 7, "slab_slots": 0, "stage_b_eval_cost": 239, "stage_b_index_bits": 21, "stage_b_log": 21, "stage_b_multiplier": 3, "tail_degree": 148, "top_fused_core": 79, "top_half_core": 44, "top_width": 3, "truncated_nodes": 75, "vshift_log": 19}`. Every key is therefore present in the proof text as well as in Appendix X, and `validate()` binds the independent `declared` dimensions to the live values before any claim is emitted.

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
| stage setup actions | three 512 bit field chains 1,536; nine 256 word descriptor rows 2,304; three target compression charge rows 900; entry shape tests pointers and exit 103 | 4,843 |
| stage a actions | fresh word draw and reduction 2; two 512 step reduction chains 1,024; two 97 event polynomial descriptors 194; allocation result test and exit 8 | 1,228 |
| stage e outer actions | factor and scratch allocator calls 1,310; stage bookkeeping 1,000 | 2,310 |
| stage f candidate actions | root update 1; two point additions 2; two line evaluations 478; four call boundaries 4; comparison and branch 2; loop update test branch 3 | 490 |
| stage g hash actions | target compression 300; canonical encoding and digest compare 3,405 | 3,705 |
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

The simulation begins empty and executes 437 resident-object events in program order. Each heap request includes the 64-byte header and 64-byte payload rounding. The two pool sides are first-fit lists in address order; free neighbours merge and a free terminal extent returns to the unused middle. The same trace includes full stage-E, F and G objects and every live stack call chain. The named `batch-inversion-prefix` event reserves and releases exactly 8,192 words. The maximum sum of the low and high extents is 630,198,016 bytes, reached in stage C. The arena adds the 128-byte middle gap, traced slab classes and 128 bytes of slab free-list heads.

| region or event peak | bytes |
| --- | ---: |
| stage A live peak | 157,286,464 |
| stage B live peak | 459,276,480 |
| stage C live peak | 630,198,016 |
| stage D live peak | 583,528,000 |
| two-ended pool high-water | 630,198,016 |
| middle gap | 128 |
| traced slab classes | 11,136 |
| slab free-list heads | 128 |
| **arena** | **630,209,408** |
| code and static data, derived by emitted family | 462,976 |
| 387-word register file | 12,384 |
| offline working set | 576 |
| stack | 32,768 |
| **footprint** | **630,718,112** |

At the end of the complete trace both pool extents, every slab slot and every raw stack frame are free. The raw logarithm is `29.2324201220168412789906446596923551889676593397963335676178901100490213830861741247637246`; upward rounding at five decimals gives `29.23243`. No product twiddle table is allocated in C or D, and there is no stored advice.

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
| half gcd frames | 16,896 |
| allocator | 2,048 |
| isolation | 2,048 |
| encoding and output | 4,096 |
| offline generator | 2,048 |
| live call-chain sum | 19,968 |
| rounded 16-KiB reservation | 32,768 |

The offline generator holds sixteen 32-byte field words and one 64-byte digit buffer, exactly `576` bytes. Code/static space is the sum of the emitted block-body, column-body, driver, field, reference, allocator, polynomial-control and literal families stated by the script; no inherited image-size literal is used.

## 8. Evaluation obligations

1. `target_defined`: sections 1 through 3 fix the Orchard P128Pow5T3 target, the 4 selected partial rounds, the input map and the full-field output.
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
| graeffe prefix and buffer | 15,547,793,510 |
| newton reciprocal | 855,782,152 |
| quotient product and copy | 217,799,844 |
| g to O1 and O2 | 512,764,637 |
| start residue on O2 | 320,974,182 |
| A0 extension to O1 | 597,787,346 |
| chunked batch inversion | 72,204,005 |
| powering steps | 251,130,239,348 |
| exit montgomery step | 693,020,006 |
| two truncated inverses | 682,810,081 |
| entry exit bookkeeping | 1,000 |
| **row C** | **270,631,678,025** |

The live middle widths are `(7, 4, 4)`. One middle set is 146,383,242; one recovery is 79,953,920; one fused top is 83,230,752; a forward and inverse are 256,381,648 and 341,404,370. A Graeffe step is 777,389,610. A bit-zero powering step is 1,170,372,782, and a bit-one step is 1,185,271,982. The exponent scan produces 169 bit-zero and 45 bit-one steps.

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

### E.1.1 Planner keys

| family | exact key | operations |
| --- | --- | ---: |
| apply | `(275, 127, 148, 384)` | 1,414 |
| apply | `(402, 127, 275, 512)` | 1,384 |
| apply | `(657, 255, 402, 768)` | 1,354 |
| apply | `(912, 255, 657, 1024)` | 1,345 |
| apply | `(1423, 511, 912, 1536)` | 1,315 |
| apply | `(2446, 1023, 1423, 3072)` | 1,255 |
| apply | `(4493, 2047, 2446, 6144)` | 1,195 |
| apply | `(8588, 4095, 4493, 12288)` | 1,135 |
| apply | `(16779, 8191, 8588, 24576)` | 1,096 |
| apply | `(33162, 16383, 16779, 49152)` | 1,036 |
| apply | `(65929, 32767, 33162, 98304)` | 976 |
| apply | `(98696, 32767, 65929, 131072)` | 946 |
| apply | `(164231, 65535, 98696, 196608)` | 916 |
| apply | `(295302, 131071, 164231, 393216)` | 877 |
| apply | `(426373, 131071, 295302, 524288)` | 847 |
| apply | `(688516, 262143, 426373, 786432)` | 817 |
| apply | `(1212803, 524287, 688516, 1572864)` | 757 |
| apply | `(1737090, 524287, 1212803, 2097152)` | 727 |
| apply | `(2261377, 524287, 1737090, 4915200)` | 697 |
| apply | `(2785664, 524287, 2261377, 4915200)` | 697 |
| apply | `(3309951, 524287, 2785664, 4915200)` | 688 |
| apply | `(3834238, 524287, 3309951, 4915200)` | 688 |
| apply | `(4358525, 524287, 3834238, 4915200)` | 658 |
| apply | `(4882812, 524287, 4358525, 4915200)` | 658 |
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
| product | `(524288, 556677, 556677)` | 754 |
| product | `(556677, 524288, 556677)` | 754 |
| product | `(556677, 556677, 1113353)` | 754 |
| transform | `(6291456,)` | 61 |
| truncated | `(8388608, 4915200, 3, 7, 4, 4, 5)` | 79 |
| **planner total** | | **75,442** |

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

The outer driver computes each next degree by subtracting `(2^j-1)+0 = 2^j`; it does not contain a degree table.

| step | degree | j | budget | node | apply plan:points | apply | driver | total |
| ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 4,882,812 | 19 | 524,287 | 6,277,051,637 | truncated:4,915,200 | 2,334,742,963 | 2,031 | 8,611,796,631 |
| 2 | 4,358,525 | 19 | 524,287 | 6,277,051,637 | truncated:4,915,200 | 2,335,398,327 | 2,031 | 8,612,451,995 |
| 3 | 3,834,238 | 19 | 524,287 | 6,277,051,637 | truncated:4,915,200 | 2,336,053,691 | 2,031 | 8,613,107,359 |
| 4 | 3,309,951 | 19 | 524,287 | 6,277,051,637 | truncated:4,915,200 | 2,336,709,013 | 2,031 | 8,613,762,681 |
| 5 | 2,785,664 | 19 | 524,287 | 6,277,051,637 | truncated:4,915,200 | 2,337,364,377 | 2,031 | 8,614,418,045 |
| 6 | 2,261,377 | 19 | 524,287 | 6,277,051,637 | truncated:4,915,200 | 2,338,019,741 | 2,031 | 8,615,073,409 |
| 7 | 1,737,090 | 19 | 524,287 | 6,277,051,637 | direct:2,097,152 | 741,636,091 | 2,031 | 7,018,689,759 |
| 8 | 1,212,803 | 19 | 524,287 | 6,277,051,637 | direct:1,572,864 | 553,211,753 | 2,031 | 6,830,265,421 |
| 9 | 688,516 | 18 | 262,143 | 2,902,538,821 | direct:786,432 | 269,830,291 | 2,031 | 3,172,371,143 |
| 10 | 426,373 | 17 | 131,071 | 1,335,346,909 | direct:524,288 | 173,534,785 | 2,031 | 1,508,883,725 |
| 11 | 295,302 | 17 | 131,071 | 1,335,346,909 | direct:393,216 | 131,185,103 | 2,031 | 1,466,534,043 |
| 12 | 164,231 | 16 | 65,535 | 610,211,609 | direct:196,608 | 65,055,439 | 2,031 | 675,269,079 |
| 13 | 98,696 | 15 | 32,767 | 276,089,127 | direct:131,072 | 40,944,733 | 2,031 | 317,035,891 |
| 14 | 65,929 | 15 | 32,767 | 276,089,127 | direct:98,304 | 32,750,603 | 2,031 | 308,841,761 |
| 15 | 33,162 | 14 | 16,383 | 125,480,327 | direct:49,152 | 13,462,303 | 2,031 | 138,944,661 |
| 16 | 16,779 | 13 | 8,191 | 56,630,695 | direct:24,576 | 6,475,337 | 2,031 | 63,108,063 |
| 17 | 8,588 | 12 | 4,095 | 25,336,231 | direct:12,288 | 3,127,411 | 2,031 | 28,465,673 |
| 18 | 4,493 | 11 | 2,047 | 11,206,295 | direct:6,144 | 1,525,277 | 2,031 | 12,733,603 |
| 19 | 2,446 | 10 | 1,023 | 4,876,671 | direct:3,072 | 759,175 | 2,031 | 5,637,877 |
| 20 | 1,423 | 9 | 511 | 2,068,515 | direct:1,536 | 392,615 | 2,031 | 2,463,161 |
| 21 | 912 | 8 | 255 | 837,893 | direct:1,024 | 233,545 | 2,031 | 1,073,469 |
| 22 | 657 | 8 | 255 | 837,893 | direct:768 | 213,427 | 2,031 | 1,053,351 |
| 23 | 402 | 7 | 127 | 328,351 | direct:512 | 120,117 | 2,031 | 450,499 |
| 24 | 275 | 7 | 127 | 328,351 | direct:384 | 95,297 | 2,031 | 425,679 |

| part | operations |
| --- | ---: |
| 24 outer steps | 73,232,856,978 |
| classical Euclid from degree 148 | 180,412 |
| normalization | 2,653 |
| entry | 1,012 |
| exit and frees | 317 |
| **row D** | **73,233,041,372** |

### E.3 Event-by-event allocation walk

The complete trace in E.4 contains every pool, slab, stack and fixed-reservation event; it is not duplicated here.

The maximum extent sum in the table is 630,198,016 bytes. Adding the middle gap and both slab regions gives 630,209,408 bytes. The fixed regions then give 630,718,112 bytes.



### E.4 Complete resident-object trace

This is the sole trace used for the memory endpoint. Fixed reservations occur
first; every later pool, slab and stack-lifetime event reports the total
resident bytes including those fixed regions.

| # | stage | action | object or chain | region | bytes | total resident bytes |
| ---: | --- | --- | --- | --- | ---: | ---: |
| 1 | fixed | reserve | code-and-static | fixed | 462,976 | 462,976 |
| 2 | fixed | reserve | register-file | fixed | 12,384 | 475,360 |
| 3 | fixed | reserve | offline-workspace | fixed | 576 | 475,936 |
| 4 | fixed | reserve | stack-reservation | fixed | 32,768 | 508,704 |
| 5 | fixed | reserve | arena-middle-gap | fixed | 128 | 508,832 |
| 6 | fixed | reserve | slab-class-reservations | fixed | 11,136 | 519,968 |
| 7 | fixed | reserve | slab-free-list-heads | fixed | 128 | 520,096 |
| 8 | A | alloc | A-g | H | 157,286,464 | 157,806,560 |
| 9 | A | free | A-g | H | 157,286,464 | 520,096 |
| 10 | B | alloc | B-values | H | 201,326,656 | 201,846,752 |
| 11 | B | alloc | B-table | H | 100,663,360 | 302,510,112 |
| 12 | B | alloc | g | L | 157,286,464 | 459,796,576 |
| 13 | B | free | B-table | H | 100,663,360 | 359,133,216 |
| 14 | B | free | B-values | H | 201,326,656 | 157,806,560 |
| 15 | C | alloc | root-tables | L | 527,744 | 158,334,304 |
| 16 | C | alloc | graeffe-E | L | 157,286,464 | 315,620,768 |
| 17 | C | alloc | graeffe-O | H | 157,286,464 | 472,907,232 |
| 18 | C | alloc | graeffe-batch | H | 262,208 | 473,169,440 |
| 19 | C | free | graeffe-batch | H | 262,208 | 472,907,232 |
| 20 | C | free | graeffe-O | H | 157,286,464 | 315,620,768 |
| 21 | C | free | graeffe-E | L | 157,286,464 | 158,334,304 |
| 22 | C | alloc | newton-reversed | L | 17,813,760 | 176,148,064 |
| 23 | C | alloc | newton-reciprocal | L | 17,813,760 | 193,961,824 |
| 24 | C | alloc | newton-scratch | H | 17,813,760 | 211,775,584 |
| 25 | C | alloc | newton-transform | H | 50,331,712 | 262,107,296 |
| 26 | C | free | newton-transform | H | 50,331,712 | 211,775,584 |
| 27 | C | free | newton-scratch | H | 17,813,760 | 193,961,824 |
| 28 | C | alloc | quotient-output | H | 17,813,760 | 211,775,584 |
| 29 | C | alloc | quotient-transform | H | 50,331,712 | 262,107,296 |
| 30 | C | free | quotient-transform | H | 50,331,712 | 211,775,584 |
| 31 | C | free | newton-reciprocal | L | 17,813,760 | 193,961,824 |
| 32 | C | free | newton-reversed | L | 17,813,760 | 176,148,064 |
| 33 | C | alloc | A-O2 | L | 157,286,464 | 333,434,528 |
| 34 | C | free | quotient-output | H | 17,813,760 | 315,620,768 |
| 35 | C | alloc | k1-O1 | L | 157,286,464 | 472,907,232 |
| 36 | C | alloc | A-O1 | H | 157,286,464 | 630,193,696 |
| 37 | C | alloc | batch | H | 262,208 | 630,455,904 |
| 38 | C | alloc | batch-inversion-prefix | L | 262,208 | 630,718,112 |
| 39 | C | free | batch-inversion-prefix | L | 262,208 | 630,455,904 |
| 40 | C | free | batch | H | 262,208 | 630,193,696 |
| 41 | C | free | k1-O1 | L | 157,286,464 | 472,907,232 |
| 42 | C | free | A-O2 | L | 157,286,464 | 315,620,768 |
| 43 | D | alloc | D1-node | L | 268,427,328 | 584,048,096 |
| 44 | D | free | D1-node | L | 268,427,328 | 315,620,768 |
| 45 | D | alloc | D1-matrix | L | 67,108,928 | 382,729,696 |
| 46 | D | alloc | D1-transform | L | 157,286,464 | 540,016,160 |
| 47 | D | free | D1-transform | L | 157,286,464 | 382,729,696 |
| 48 | D | free | D1-matrix | L | 67,108,928 | 315,620,768 |
| 49 | D | alloc | D2-node | L | 268,427,328 | 584,048,096 |
| 50 | D | free | D2-node | L | 268,427,328 | 315,620,768 |
| 51 | D | alloc | D2-matrix | L | 67,108,928 | 382,729,696 |
| 52 | D | alloc | D2-transform | L | 157,286,464 | 540,016,160 |
| 53 | D | free | D2-transform | L | 157,286,464 | 382,729,696 |
| 54 | D | free | D2-matrix | L | 67,108,928 | 315,620,768 |
| 55 | D | alloc | D3-node | L | 268,427,328 | 584,048,096 |
| 56 | D | free | D3-node | L | 268,427,328 | 315,620,768 |
| 57 | D | alloc | D3-matrix | L | 67,108,928 | 382,729,696 |
| 58 | D | alloc | D3-transform | L | 157,286,464 | 540,016,160 |
| 59 | D | free | D3-transform | L | 157,286,464 | 382,729,696 |
| 60 | D | free | D3-matrix | L | 67,108,928 | 315,620,768 |
| 61 | D | alloc | D4-node | L | 268,427,328 | 584,048,096 |
| 62 | D | free | D4-node | L | 268,427,328 | 315,620,768 |
| 63 | D | alloc | D4-matrix | L | 67,108,928 | 382,729,696 |
| 64 | D | alloc | D4-transform | L | 157,286,464 | 540,016,160 |
| 65 | D | free | D4-transform | L | 157,286,464 | 382,729,696 |
| 66 | D | free | D4-matrix | L | 67,108,928 | 315,620,768 |
| 67 | D | alloc | D5-node | L | 268,427,328 | 584,048,096 |
| 68 | D | free | D5-node | L | 268,427,328 | 315,620,768 |
| 69 | D | alloc | D5-matrix | L | 67,108,928 | 382,729,696 |
| 70 | D | alloc | D5-transform | L | 157,286,464 | 540,016,160 |
| 71 | D | free | D5-transform | L | 157,286,464 | 382,729,696 |
| 72 | D | free | D5-matrix | L | 67,108,928 | 315,620,768 |
| 73 | D | alloc | D6-node | L | 268,427,328 | 584,048,096 |
| 74 | D | free | D6-node | L | 268,427,328 | 315,620,768 |
| 75 | D | alloc | D6-matrix | L | 67,108,928 | 382,729,696 |
| 76 | D | alloc | D6-transform | L | 157,286,464 | 540,016,160 |
| 77 | D | free | D6-transform | L | 157,286,464 | 382,729,696 |
| 78 | D | free | D6-matrix | L | 67,108,928 | 315,620,768 |
| 79 | D | alloc | D7-node | L | 268,427,328 | 584,048,096 |
| 80 | D | free | D7-node | L | 268,427,328 | 315,620,768 |
| 81 | D | shrink | g | L | 67,108,928 | 315,620,768 |
| 82 | D | shrink | A-O1 | H | 67,108,928 | 225,443,232 |
| 83 | D | alloc | D7-forward-1 | L | 67,108,928 | 225,443,232 |
| 84 | D | alloc | D7-forward-2 | H | 67,108,928 | 292,552,160 |
| 85 | D | alloc | D7-forward-3 | L | 67,108,928 | 359,661,088 |
| 86 | D | alloc | D7-forward-4 | H | 67,108,928 | 426,770,016 |
| 87 | D | retain | D7-forward-5 | L | 67,108,928 | 426,770,016 |
| 88 | D | retain | D7-forward-6 | H | 67,108,928 | 426,770,016 |
| 89 | D | release-retained | D7-forward-6 | H | 67,108,928 | 426,770,016 |
| 90 | D | release-retained | D7-forward-5 | L | 67,108,928 | 426,770,016 |
| 91 | D | free | D7-forward-4 | H | 67,108,928 | 359,661,088 |
| 92 | D | free | D7-forward-3 | L | 67,108,928 | 292,552,160 |
| 93 | D | free | D7-forward-2 | H | 67,108,928 | 225,443,232 |
| 94 | D | free | D7-forward-1 | L | 67,108,928 | 225,443,232 |
| 95 | D | alloc | D8-node | L | 268,427,328 | 493,870,560 |
| 96 | D | free | D8-node | L | 268,427,328 | 225,443,232 |
| 97 | D | shrink | g | L | 50,331,712 | 225,443,232 |
| 98 | D | shrink | A-O1 | H | 50,331,712 | 208,666,016 |
| 99 | D | alloc | D8-forward-1 | L | 50,331,712 | 208,666,016 |
| 100 | D | alloc | D8-forward-2 | H | 50,331,712 | 258,997,728 |
| 101 | D | alloc | D8-forward-3 | L | 50,331,712 | 258,997,728 |
| 102 | D | alloc | D8-forward-4 | H | 50,331,712 | 309,329,440 |
| 103 | D | retain | D8-forward-5 | L | 50,331,712 | 309,329,440 |
| 104 | D | retain | D8-forward-6 | H | 50,331,712 | 309,329,440 |
| 105 | D | release-retained | D8-forward-6 | H | 50,331,712 | 309,329,440 |
| 106 | D | release-retained | D8-forward-5 | L | 50,331,712 | 309,329,440 |
| 107 | D | free | D8-forward-4 | H | 50,331,712 | 258,997,728 |
| 108 | D | free | D8-forward-3 | L | 50,331,712 | 258,997,728 |
| 109 | D | free | D8-forward-2 | H | 50,331,712 | 208,666,016 |
| 110 | D | free | D8-forward-1 | L | 50,331,712 | 208,666,016 |
| 111 | D | alloc | D9-node | L | 134,209,600 | 342,875,616 |
| 112 | D | free | D9-node | L | 134,209,600 | 208,666,016 |
| 113 | D | shrink | g | L | 25,165,888 | 208,666,016 |
| 114 | D | shrink | A-O1 | H | 25,165,888 | 183,500,192 |
| 115 | D | alloc | D9-forward-1 | L | 25,165,888 | 183,500,192 |
| 116 | D | alloc | D9-forward-2 | H | 25,165,888 | 208,666,080 |
| 117 | D | alloc | D9-forward-3 | L | 25,165,888 | 208,666,080 |
| 118 | D | alloc | D9-forward-4 | H | 25,165,888 | 233,831,968 |
| 119 | D | retain | D9-forward-5 | L | 25,165,888 | 233,831,968 |
| 120 | D | retain | D9-forward-6 | H | 25,165,888 | 233,831,968 |
| 121 | D | release-retained | D9-forward-6 | H | 25,165,888 | 233,831,968 |
| 122 | D | release-retained | D9-forward-5 | L | 25,165,888 | 233,831,968 |
| 123 | D | free | D9-forward-4 | H | 25,165,888 | 208,666,080 |
| 124 | D | free | D9-forward-3 | L | 25,165,888 | 208,666,080 |
| 125 | D | free | D9-forward-2 | H | 25,165,888 | 183,500,192 |
| 126 | D | free | D9-forward-1 | L | 25,165,888 | 183,500,192 |
| 127 | D | alloc | D10-node | L | 67,100,736 | 183,500,192 |
| 128 | D | free | D10-node | L | 67,100,736 | 183,500,192 |
| 129 | D | shrink | g | L | 16,777,280 | 183,500,192 |
| 130 | D | shrink | A-O1 | H | 16,777,280 | 175,111,584 |
| 131 | D | alloc | D10-forward-1 | L | 16,777,280 | 175,111,584 |
| 132 | D | alloc | D10-forward-2 | H | 16,777,280 | 191,888,864 |
| 133 | D | alloc | D10-forward-3 | L | 16,777,280 | 191,888,864 |
| 134 | D | alloc | D10-forward-4 | H | 16,777,280 | 208,666,144 |
| 135 | D | retain | D10-forward-5 | L | 16,777,280 | 208,666,144 |
| 136 | D | retain | D10-forward-6 | H | 16,777,280 | 208,666,144 |
| 137 | D | release-retained | D10-forward-6 | H | 16,777,280 | 208,666,144 |
| 138 | D | release-retained | D10-forward-5 | L | 16,777,280 | 208,666,144 |
| 139 | D | free | D10-forward-4 | H | 16,777,280 | 191,888,864 |
| 140 | D | free | D10-forward-3 | L | 16,777,280 | 191,888,864 |
| 141 | D | free | D10-forward-2 | H | 16,777,280 | 175,111,584 |
| 142 | D | free | D10-forward-1 | L | 16,777,280 | 175,111,584 |
| 143 | D | alloc | D11-node | L | 67,100,736 | 175,111,584 |
| 144 | D | free | D11-node | L | 67,100,736 | 175,111,584 |
| 145 | D | shrink | g | L | 12,582,976 | 175,111,584 |
| 146 | D | shrink | A-O1 | H | 12,582,976 | 170,917,280 |
| 147 | D | alloc | D11-forward-1 | L | 12,582,976 | 170,917,280 |
| 148 | D | alloc | D11-forward-2 | H | 12,582,976 | 183,500,256 |
| 149 | D | alloc | D11-forward-3 | L | 12,582,976 | 183,500,256 |
| 150 | D | alloc | D11-forward-4 | H | 12,582,976 | 196,083,232 |
| 151 | D | retain | D11-forward-5 | L | 12,582,976 | 196,083,232 |
| 152 | D | retain | D11-forward-6 | H | 12,582,976 | 196,083,232 |
| 153 | D | release-retained | D11-forward-6 | H | 12,582,976 | 196,083,232 |
| 154 | D | release-retained | D11-forward-5 | L | 12,582,976 | 196,083,232 |
| 155 | D | free | D11-forward-4 | H | 12,582,976 | 183,500,256 |
| 156 | D | free | D11-forward-3 | L | 12,582,976 | 183,500,256 |
| 157 | D | free | D11-forward-2 | H | 12,582,976 | 170,917,280 |
| 158 | D | free | D11-forward-1 | L | 12,582,976 | 170,917,280 |
| 159 | D | alloc | D12-node | L | 33,546,304 | 170,917,280 |
| 160 | D | free | D12-node | L | 33,546,304 | 170,917,280 |
| 161 | D | shrink | g | L | 6,291,520 | 170,917,280 |
| 162 | D | shrink | A-O1 | H | 6,291,520 | 164,625,824 |
| 163 | D | alloc | D12-forward-1 | L | 6,291,520 | 164,625,824 |
| 164 | D | alloc | D12-forward-2 | H | 6,291,520 | 170,917,344 |
| 165 | D | alloc | D12-forward-3 | L | 6,291,520 | 170,917,344 |
| 166 | D | alloc | D12-forward-4 | H | 6,291,520 | 177,208,864 |
| 167 | D | retain | D12-forward-5 | L | 6,291,520 | 177,208,864 |
| 168 | D | retain | D12-forward-6 | H | 6,291,520 | 177,208,864 |
| 169 | D | release-retained | D12-forward-6 | H | 6,291,520 | 177,208,864 |
| 170 | D | release-retained | D12-forward-5 | L | 6,291,520 | 177,208,864 |
| 171 | D | free | D12-forward-4 | H | 6,291,520 | 170,917,344 |
| 172 | D | free | D12-forward-3 | L | 6,291,520 | 170,917,344 |
| 173 | D | free | D12-forward-2 | H | 6,291,520 | 164,625,824 |
| 174 | D | free | D12-forward-1 | L | 6,291,520 | 164,625,824 |
| 175 | D | alloc | D13-node | L | 16,769,088 | 164,625,824 |
| 176 | D | free | D13-node | L | 16,769,088 | 164,625,824 |
| 177 | D | shrink | g | L | 4,194,368 | 164,625,824 |
| 178 | D | shrink | A-O1 | H | 4,194,368 | 162,528,672 |
| 179 | D | alloc | D13-forward-1 | L | 4,194,368 | 162,528,672 |
| 180 | D | alloc | D13-forward-2 | H | 4,194,368 | 166,723,040 |
| 181 | D | alloc | D13-forward-3 | L | 4,194,368 | 166,723,040 |
| 182 | D | alloc | D13-forward-4 | H | 4,194,368 | 170,917,408 |
| 183 | D | retain | D13-forward-5 | L | 4,194,368 | 170,917,408 |
| 184 | D | retain | D13-forward-6 | H | 4,194,368 | 170,917,408 |
| 185 | D | release-retained | D13-forward-6 | H | 4,194,368 | 170,917,408 |
| 186 | D | release-retained | D13-forward-5 | L | 4,194,368 | 170,917,408 |
| 187 | D | free | D13-forward-4 | H | 4,194,368 | 166,723,040 |
| 188 | D | free | D13-forward-3 | L | 4,194,368 | 166,723,040 |
| 189 | D | free | D13-forward-2 | H | 4,194,368 | 162,528,672 |
| 190 | D | free | D13-forward-1 | L | 4,194,368 | 162,528,672 |
| 191 | D | alloc | D14-node | L | 16,769,088 | 162,528,672 |
| 192 | D | free | D14-node | L | 16,769,088 | 162,528,672 |
| 193 | D | shrink | g | L | 3,145,792 | 162,528,672 |
| 194 | D | shrink | A-O1 | H | 3,145,792 | 161,480,096 |
| 195 | D | alloc | D14-forward-1 | L | 3,145,792 | 161,480,096 |
| 196 | D | alloc | D14-forward-2 | H | 3,145,792 | 164,625,888 |
| 197 | D | alloc | D14-forward-3 | L | 3,145,792 | 164,625,888 |
| 198 | D | alloc | D14-forward-4 | H | 3,145,792 | 167,771,680 |
| 199 | D | retain | D14-forward-5 | L | 3,145,792 | 167,771,680 |
| 200 | D | retain | D14-forward-6 | H | 3,145,792 | 167,771,680 |
| 201 | D | release-retained | D14-forward-6 | H | 3,145,792 | 167,771,680 |
| 202 | D | release-retained | D14-forward-5 | L | 3,145,792 | 167,771,680 |
| 203 | D | free | D14-forward-4 | H | 3,145,792 | 164,625,888 |
| 204 | D | free | D14-forward-3 | L | 3,145,792 | 164,625,888 |
| 205 | D | free | D14-forward-2 | H | 3,145,792 | 161,480,096 |
| 206 | D | free | D14-forward-1 | L | 3,145,792 | 161,480,096 |
| 207 | D | alloc | D15-node | L | 8,380,480 | 161,480,096 |
| 208 | D | free | D15-node | L | 8,380,480 | 161,480,096 |
| 209 | D | shrink | g | L | 1,572,928 | 161,480,096 |
| 210 | D | shrink | A-O1 | H | 1,572,928 | 159,907,232 |
| 211 | D | alloc | D15-forward-1 | L | 1,572,928 | 159,907,232 |
| 212 | D | alloc | D15-forward-2 | H | 1,572,928 | 161,480,160 |
| 213 | D | alloc | D15-forward-3 | L | 1,572,928 | 161,480,160 |
| 214 | D | alloc | D15-forward-4 | H | 1,572,928 | 163,053,088 |
| 215 | D | retain | D15-forward-5 | L | 1,572,928 | 163,053,088 |
| 216 | D | retain | D15-forward-6 | H | 1,572,928 | 163,053,088 |
| 217 | D | release-retained | D15-forward-6 | H | 1,572,928 | 163,053,088 |
| 218 | D | release-retained | D15-forward-5 | L | 1,572,928 | 163,053,088 |
| 219 | D | free | D15-forward-4 | H | 1,572,928 | 161,480,160 |
| 220 | D | free | D15-forward-3 | L | 1,572,928 | 161,480,160 |
| 221 | D | free | D15-forward-2 | H | 1,572,928 | 159,907,232 |
| 222 | D | free | D15-forward-1 | L | 1,572,928 | 159,907,232 |
| 223 | D | alloc | D16-node | L | 4,186,176 | 159,907,232 |
| 224 | D | free | D16-node | L | 4,186,176 | 159,907,232 |
| 225 | D | shrink | g | L | 786,496 | 159,907,232 |
| 226 | D | shrink | A-O1 | H | 786,496 | 159,120,800 |
| 227 | D | alloc | D16-forward-1 | L | 786,496 | 159,120,800 |
| 228 | D | alloc | D16-forward-2 | H | 786,496 | 159,907,296 |
| 229 | D | alloc | D16-forward-3 | L | 786,496 | 159,907,296 |
| 230 | D | alloc | D16-forward-4 | H | 786,496 | 160,693,792 |
| 231 | D | retain | D16-forward-5 | L | 786,496 | 160,693,792 |
| 232 | D | retain | D16-forward-6 | H | 786,496 | 160,693,792 |
| 233 | D | release-retained | D16-forward-6 | H | 786,496 | 160,693,792 |
| 234 | D | release-retained | D16-forward-5 | L | 786,496 | 160,693,792 |
| 235 | D | free | D16-forward-4 | H | 786,496 | 159,907,296 |
| 236 | D | free | D16-forward-3 | L | 786,496 | 159,907,296 |
| 237 | D | free | D16-forward-2 | H | 786,496 | 159,120,800 |
| 238 | D | free | D16-forward-1 | L | 786,496 | 159,120,800 |
| 239 | D | alloc | D17-node | L | 2,089,024 | 159,120,800 |
| 240 | D | free | D17-node | L | 2,089,024 | 159,120,800 |
| 241 | D | shrink | g | L | 393,280 | 159,120,800 |
| 242 | D | shrink | A-O1 | H | 393,280 | 158,727,584 |
| 243 | D | alloc | D17-forward-1 | L | 393,280 | 158,727,584 |
| 244 | D | alloc | D17-forward-2 | H | 393,280 | 159,120,864 |
| 245 | D | alloc | D17-forward-3 | L | 393,280 | 159,120,864 |
| 246 | D | alloc | D17-forward-4 | H | 393,280 | 159,514,144 |
| 247 | D | retain | D17-forward-5 | L | 393,280 | 159,514,144 |
| 248 | D | retain | D17-forward-6 | H | 393,280 | 159,514,144 |
| 249 | D | release-retained | D17-forward-6 | H | 393,280 | 159,514,144 |
| 250 | D | release-retained | D17-forward-5 | L | 393,280 | 159,514,144 |
| 251 | D | free | D17-forward-4 | H | 393,280 | 159,120,864 |
| 252 | D | free | D17-forward-3 | L | 393,280 | 159,120,864 |
| 253 | D | free | D17-forward-2 | H | 393,280 | 158,727,584 |
| 254 | D | free | D17-forward-1 | L | 393,280 | 158,727,584 |
| 255 | D | alloc | D18-node | L | 1,040,448 | 158,727,584 |
| 256 | D | free | D18-node | L | 1,040,448 | 158,727,584 |
| 257 | D | shrink | g | L | 196,672 | 158,727,584 |
| 258 | D | shrink | A-O1 | H | 196,672 | 158,530,976 |
| 259 | D | alloc | D18-forward-1 | L | 196,672 | 158,530,976 |
| 260 | D | alloc | D18-forward-2 | H | 196,672 | 158,727,648 |
| 261 | D | alloc | D18-forward-3 | L | 196,672 | 158,727,648 |
| 262 | D | alloc | D18-forward-4 | H | 196,672 | 158,924,320 |
| 263 | D | retain | D18-forward-5 | L | 196,672 | 158,924,320 |
| 264 | D | retain | D18-forward-6 | H | 196,672 | 158,924,320 |
| 265 | D | release-retained | D18-forward-6 | H | 196,672 | 158,924,320 |
| 266 | D | release-retained | D18-forward-5 | L | 196,672 | 158,924,320 |
| 267 | D | free | D18-forward-4 | H | 196,672 | 158,727,648 |
| 268 | D | free | D18-forward-3 | L | 196,672 | 158,727,648 |
| 269 | D | free | D18-forward-2 | H | 196,672 | 158,530,976 |
| 270 | D | free | D18-forward-1 | L | 196,672 | 158,530,976 |
| 271 | D | alloc | D19-node | L | 516,160 | 158,530,976 |
| 272 | D | free | D19-node | L | 516,160 | 158,530,976 |
| 273 | D | shrink | g | L | 98,368 | 158,530,976 |
| 274 | D | shrink | A-O1 | H | 98,368 | 158,432,672 |
| 275 | D | alloc | D19-forward-1 | L | 98,368 | 158,432,672 |
| 276 | D | alloc | D19-forward-2 | H | 98,368 | 158,531,040 |
| 277 | D | alloc | D19-forward-3 | L | 98,368 | 158,531,040 |
| 278 | D | alloc | D19-forward-4 | H | 98,368 | 158,629,408 |
| 279 | D | retain | D19-forward-5 | L | 98,368 | 158,629,408 |
| 280 | D | retain | D19-forward-6 | H | 98,368 | 158,629,408 |
| 281 | D | release-retained | D19-forward-6 | H | 98,368 | 158,629,408 |
| 282 | D | release-retained | D19-forward-5 | L | 98,368 | 158,629,408 |
| 283 | D | free | D19-forward-4 | H | 98,368 | 158,531,040 |
| 284 | D | free | D19-forward-3 | L | 98,368 | 158,531,040 |
| 285 | D | free | D19-forward-2 | H | 98,368 | 158,432,672 |
| 286 | D | free | D19-forward-1 | L | 98,368 | 158,432,672 |
| 287 | D | alloc | D20-node | L | 254,016 | 158,432,672 |
| 288 | D | free | D20-node | L | 254,016 | 158,432,672 |
| 289 | D | shrink | g | L | 49,216 | 158,432,672 |
| 290 | D | shrink | A-O1 | H | 49,216 | 158,383,520 |
| 291 | D | alloc | D20-forward-1 | L | 49,216 | 158,383,520 |
| 292 | D | alloc | D20-forward-2 | H | 49,216 | 158,432,736 |
| 293 | D | alloc | D20-forward-3 | L | 49,216 | 158,432,736 |
| 294 | D | alloc | D20-forward-4 | H | 49,216 | 158,481,952 |
| 295 | D | retain | D20-forward-5 | L | 49,216 | 158,481,952 |
| 296 | D | retain | D20-forward-6 | H | 49,216 | 158,481,952 |
| 297 | D | release-retained | D20-forward-6 | H | 49,216 | 158,481,952 |
| 298 | D | release-retained | D20-forward-5 | L | 49,216 | 158,481,952 |
| 299 | D | free | D20-forward-4 | H | 49,216 | 158,432,736 |
| 300 | D | free | D20-forward-3 | L | 49,216 | 158,432,736 |
| 301 | D | free | D20-forward-2 | H | 49,216 | 158,383,520 |
| 302 | D | free | D20-forward-1 | L | 49,216 | 158,383,520 |
| 303 | D | alloc | D21-node | L | 122,944 | 158,383,520 |
| 304 | D | free | D21-node | L | 122,944 | 158,383,520 |
| 305 | D | shrink | g | L | 32,832 | 158,383,520 |
| 306 | D | shrink | A-O1 | H | 32,832 | 158,367,136 |
| 307 | D | alloc | D21-forward-1 | L | 32,832 | 158,367,136 |
| 308 | D | alloc | D21-forward-2 | H | 32,832 | 158,399,968 |
| 309 | D | alloc | D21-forward-3 | L | 32,832 | 158,399,968 |
| 310 | D | alloc | D21-forward-4 | H | 32,832 | 158,432,800 |
| 311 | D | retain | D21-forward-5 | L | 32,832 | 158,432,800 |
| 312 | D | retain | D21-forward-6 | H | 32,832 | 158,432,800 |
| 313 | D | release-retained | D21-forward-6 | H | 32,832 | 158,432,800 |
| 314 | D | release-retained | D21-forward-5 | L | 32,832 | 158,432,800 |
| 315 | D | free | D21-forward-4 | H | 32,832 | 158,399,968 |
| 316 | D | free | D21-forward-3 | L | 32,832 | 158,399,968 |
| 317 | D | free | D21-forward-2 | H | 32,832 | 158,367,136 |
| 318 | D | free | D21-forward-1 | L | 32,832 | 158,367,136 |
| 319 | D | alloc | D22-node | L | 122,944 | 158,367,136 |
| 320 | D | free | D22-node | L | 122,944 | 158,367,136 |
| 321 | D | shrink | g | L | 24,640 | 158,367,136 |
| 322 | D | shrink | A-O1 | H | 24,640 | 158,358,944 |
| 323 | D | alloc | D22-forward-1 | L | 24,640 | 158,358,944 |
| 324 | D | alloc | D22-forward-2 | H | 24,640 | 158,383,584 |
| 325 | D | alloc | D22-forward-3 | L | 24,640 | 158,383,584 |
| 326 | D | alloc | D22-forward-4 | H | 24,640 | 158,408,224 |
| 327 | D | retain | D22-forward-5 | L | 24,640 | 158,408,224 |
| 328 | D | retain | D22-forward-6 | H | 24,640 | 158,408,224 |
| 329 | D | release-retained | D22-forward-6 | H | 24,640 | 158,408,224 |
| 330 | D | release-retained | D22-forward-5 | L | 24,640 | 158,408,224 |
| 331 | D | free | D22-forward-4 | H | 24,640 | 158,383,584 |
| 332 | D | free | D22-forward-3 | L | 24,640 | 158,383,584 |
| 333 | D | free | D22-forward-2 | H | 24,640 | 158,358,944 |
| 334 | D | free | D22-forward-1 | L | 24,640 | 158,358,944 |
| 335 | D | alloc | D23-node | L | 57,408 | 158,358,944 |
| 336 | D | free | D23-node | L | 57,408 | 158,358,944 |
| 337 | D | shrink | g | L | 16,448 | 158,358,944 |
| 338 | D | shrink | A-O1 | H | 16,448 | 158,350,752 |
| 339 | D | alloc | D23-forward-1 | L | 16,448 | 158,350,752 |
| 340 | D | alloc | D23-forward-2 | H | 16,448 | 158,367,200 |
| 341 | D | alloc | D23-forward-3 | L | 16,448 | 158,367,200 |
| 342 | D | alloc | D23-forward-4 | H | 16,448 | 158,383,648 |
| 343 | D | retain | D23-forward-5 | L | 16,448 | 158,383,648 |
| 344 | D | retain | D23-forward-6 | H | 16,448 | 158,383,648 |
| 345 | D | release-retained | D23-forward-6 | H | 16,448 | 158,383,648 |
| 346 | D | release-retained | D23-forward-5 | L | 16,448 | 158,383,648 |
| 347 | D | free | D23-forward-4 | H | 16,448 | 158,367,200 |
| 348 | D | free | D23-forward-3 | L | 16,448 | 158,367,200 |
| 349 | D | free | D23-forward-2 | H | 16,448 | 158,350,752 |
| 350 | D | free | D23-forward-1 | L | 16,448 | 158,350,752 |
| 351 | D | alloc | D24-node | L | 57,408 | 158,350,752 |
| 352 | D | free | D24-node | L | 57,408 | 158,350,752 |
| 353 | D | shrink | g | L | 12,352 | 158,350,752 |
| 354 | D | shrink | A-O1 | H | 12,352 | 158,346,656 |
| 355 | D | alloc | D24-forward-1 | L | 12,352 | 158,346,656 |
| 356 | D | alloc | D24-forward-2 | H | 12,352 | 158,359,008 |
| 357 | D | alloc | D24-forward-3 | L | 12,352 | 158,359,008 |
| 358 | D | alloc | D24-forward-4 | H | 12,352 | 158,371,360 |
| 359 | D | retain | D24-forward-5 | L | 12,352 | 158,371,360 |
| 360 | D | retain | D24-forward-6 | H | 12,352 | 158,371,360 |
| 361 | D | release-retained | D24-forward-6 | H | 12,352 | 158,371,360 |
| 362 | D | release-retained | D24-forward-5 | L | 12,352 | 158,371,360 |
| 363 | D | free | D24-forward-4 | H | 12,352 | 158,359,008 |
| 364 | D | free | D24-forward-3 | L | 12,352 | 158,359,008 |
| 365 | D | free | D24-forward-2 | H | 12,352 | 158,346,656 |
| 366 | D | free | D24-forward-1 | L | 12,352 | 158,346,656 |
| 367 | D | free | root-tables | L | 527,744 | 544,800 |
| 368 | D | free | A-O1 | H | 12,352 | 532,448 |
| 369 | D | free | g | L | 12,352 | 520,096 |
| 370 | E | alloc | E-factor | S1024 | 1,024 | 520,096 |
| 371 | E | alloc | E-base | S1024 | 1,024 | 520,096 |
| 372 | E | alloc | E-power-result | S1024 | 1,024 | 520,096 |
| 373 | E | alloc | E-product-scratch | S2048 | 2,048 | 520,096 |
| 374 | E | alloc | E-P-minus-one | S1024 | 1,024 | 520,096 |
| 375 | E | alloc | E-P-plus-one | S1024 | 1,024 | 520,096 |
| 376 | E | alloc | E-gcd-left | S1024 | 1,024 | 520,096 |
| 377 | E | alloc | E-gcd-right | S1024 | 1,024 | 520,096 |
| 378 | E | alloc | E-selected-factor | S1024 | 1,024 | 520,096 |
| 379 | E | alloc | E-random-words | S128 | 128 | 520,096 |
| 380 | E | free | E-random-words | S128 | 128 | 520,096 |
| 381 | E | free | E-selected-factor | S1024 | 1,024 | 520,096 |
| 382 | E | free | E-gcd-right | S1024 | 1,024 | 520,096 |
| 383 | E | free | E-gcd-left | S1024 | 1,024 | 520,096 |
| 384 | E | free | E-P-plus-one | S1024 | 1,024 | 520,096 |
| 385 | E | free | E-P-minus-one | S1024 | 1,024 | 520,096 |
| 386 | E | free | E-product-scratch | S2048 | 2,048 | 520,096 |
| 387 | E | free | E-power-result | S1024 | 1,024 | 520,096 |
| 388 | E | free | E-base | S1024 | 1,024 | 520,096 |
| 389 | E | free | E-factor | S1024 | 1,024 | 520,096 |
| 390 | F | alloc | F-root-chain | S2048 | 2,048 | 520,096 |
| 391 | F | alloc | F-candidate-state | S1024 | 1,024 | 520,096 |
| 392 | F | alloc | F-input-pair | S256 | 256 | 520,096 |
| 393 | F | alloc | F-line-state | S256 | 256 | 520,096 |
| 394 | F | free | F-line-state | S256 | 256 | 520,096 |
| 395 | F | free | F-input-pair | S256 | 256 | 520,096 |
| 396 | F | free | F-candidate-state | S1024 | 1,024 | 520,096 |
| 397 | F | free | F-root-chain | S2048 | 2,048 | 520,096 |
| 398 | G | alloc | G-two-input-pairs | S256 | 256 | 520,096 |
| 399 | G | alloc | G-two-poseidon-states | S256 | 256 | 520,096 |
| 400 | G | alloc | G-canonical-encodings | S256 | 256 | 520,096 |
| 401 | G | alloc | G-output-elements | S128 | 128 | 520,096 |
| 402 | G | free | G-output-elements | S128 | 128 | 520,096 |
| 403 | G | free | G-canonical-encodings | S256 | 256 | 520,096 |
| 404 | G | free | G-two-poseidon-states | S256 | 256 | 520,096 |
| 405 | G | free | G-two-input-pairs | S256 | 256 | 520,096 |
| 406 | stack | alloc | sampling:runtime_entry | R | 1,024 | 520,096 |
| 407 | stack | alloc | sampling:line_and_sampler | R | 2,048 | 520,096 |
| 408 | stack | free | sampling:line_and_sampler | R | 2,048 | 520,096 |
| 409 | stack | free | sampling:runtime_entry | R | 1,024 | 520,096 |
| 410 | stack | alloc | stage_c_transform:runtime_entry | R | 1,024 | 520,096 |
| 411 | stack | alloc | stage_c_transform:stage_c_driver | R | 4,096 | 520,096 |
| 412 | stack | alloc | stage_c_transform:seven_transform_frames | R | 7,168 | 520,096 |
| 413 | stack | alloc | stage_c_transform:product_planner | R | 2,048 | 520,096 |
| 414 | stack | alloc | stage_c_transform:allocator | R | 2,048 | 520,096 |
| 415 | stack | free | stage_c_transform:allocator | R | 2,048 | 520,096 |
| 416 | stack | free | stage_c_transform:product_planner | R | 2,048 | 520,096 |
| 417 | stack | free | stage_c_transform:seven_transform_frames | R | 7,168 | 520,096 |
| 418 | stack | free | stage_c_transform:stage_c_driver | R | 4,096 | 520,096 |
| 419 | stack | free | stage_c_transform:runtime_entry | R | 1,024 | 520,096 |
| 420 | stack | alloc | stage_d_half_gcd:runtime_entry | R | 1,024 | 520,096 |
| 421 | stack | alloc | stage_d_half_gcd:half_gcd_frames | R | 16,896 | 520,096 |
| 422 | stack | alloc | stage_d_half_gcd:allocator | R | 2,048 | 520,096 |
| 423 | stack | free | stage_d_half_gcd:allocator | R | 2,048 | 520,096 |
| 424 | stack | free | stage_d_half_gcd:half_gcd_frames | R | 16,896 | 520,096 |
| 425 | stack | free | stage_d_half_gcd:runtime_entry | R | 1,024 | 520,096 |
| 426 | stack | alloc | stage_e_isolation:runtime_entry | R | 1,024 | 520,096 |
| 427 | stack | alloc | stage_e_isolation:isolation | R | 2,048 | 520,096 |
| 428 | stack | alloc | stage_e_isolation:allocator | R | 2,048 | 520,096 |
| 429 | stack | free | stage_e_isolation:allocator | R | 2,048 | 520,096 |
| 430 | stack | free | stage_e_isolation:isolation | R | 2,048 | 520,096 |
| 431 | stack | free | stage_e_isolation:runtime_entry | R | 1,024 | 520,096 |
| 432 | stack | alloc | stage_f_g_output:runtime_entry | R | 1,024 | 520,096 |
| 433 | stack | alloc | stage_f_g_output:encoding_and_output | R | 4,096 | 520,096 |
| 434 | stack | free | stage_f_g_output:encoding_and_output | R | 4,096 | 520,096 |
| 435 | stack | free | stage_f_g_output:runtime_entry | R | 1,024 | 520,096 |
| 436 | stack | alloc | offline_generation:offline_generator | R | 2,048 | 520,096 |
| 437 | stack | free | offline_generation:offline_generator | R | 2,048 | 520,096 |


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
CONFIG = {'rounds': 4, 'graeffe_depth': 20, 'vshift_log': 19, 'truncated_nodes': 75, 'node_log': 16, 'full_log': 23, 'hgcd_cap': 19, 'tail_degree': 148, 'top_width': 3, 'bottom_width': 5, 'middle_widths': [7, 4, 4], 'active_top_cosets': 5, 'top_fused_core': 79, 'top_half_core': 44, 'inverse_top_core': 48, 'recovery_fixed': 131072, 'recovery_per_layer': 8, 'recovery_per_point': 2, 'recovery_subtrees': [[1, 7], [4, 5], [16, 3], [32, 2]], 'batch_words': 8192, 'inversion_chunk': 8192, 'stage_b_log': 21, 'stage_b_multiplier': 3, 'stage_b_index_bits': 21, 'stage_b_eval_cost': 239, 'root_table_words': 16384, 'delta_copies': 1, 'o2_extra_point_ops': 6, 'bit_extra_point_ops': 3, 'bit_extra_block_ops': 1, 'outer_decrement_extra': 0, 'direct_row_cap': 1572864, 'apply_mode': 'truncated', 'direct_transform_mode': 'single', 'slab_slots': 0, 'slab_class_log': 7, 'expected_outer_steps': 24, 'expected_squarings': 214, 'expected_multiplies': 45, 'declared': {'degree': 9765625, 'odd_degree': 4882812, 'stage_b_points': 6291456, 'stage_b_evaluations': 12582912, 'stage_b_index_bits': 21, 'graeffe_depth': 20, 'powering_steps': 214, 'powering_multiplies': 45, 'full_points': 8388608, 'truncated_points': 4915200, 'transform_layers': 23, 'hgcd_cap': 19, 'outer_steps': 24, 'tail_degree': 148}}
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
