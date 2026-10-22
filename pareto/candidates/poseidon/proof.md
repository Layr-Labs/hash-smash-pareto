# Orchard Poseidon r7-v8: shared-body Stage-C split defense

## 1. Claim

The target is `poseidon-orchard-r7-prefix-v1`. The complete generated ledger
gives `N_max = 53,896,855,695,902`, `time_log2 = 37.11145`, and
78,353,750,600 bytes with `memory_log2_bytes = 36.18929`. The
normalized score is `53.30074`, an improvement of
`0.03323` over the judged r7 bar.

H-ONE, H-NORMAL, their accepted wording and the experiments are preserved from
that judged package. The conservative success decimal remains `0.39209`.
The resource reprice adds no heuristic. Every submitted row is generated from
the live package code; no predecessor total or retained conservative cap is an
input.

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

4.1.2 Stage E: isolating a root of `G`. The current factor `H`
has degree at most 16. Each of 64 constant-work rounds draws a fresh shift
`a`, evaluates `H(-a)`, initializes `X+a`, computes
`(X+a)^((p-1)/2) mod H` by square-and-multiply, forms `P-1` and `P+1`, runs
two padded Euclidean gcds, and selects and copies one proper factor. A linear
factor ends the logical search, but the resource bound charges the complete
round schedule.

The exponent has 253 non-leading squarings and 45 non-leading multiplies. The
live pseudocode formula gives:

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

Thus row E is `64*2,172,204 + 2,310 = 139,023,366`. The 63-operation fresh field draw is the first component.
Section 9.4 bounds failure after the 64 fresh shifts.

4.1.3 Stage F: the root of `g_c` above `y`. By 4.3G, `y = S^(2^27)` for a usable root `S` of `g_c`, and the solutions of `S'^(2^27) = y` are `u^2 mu^(2j)`, `j < 2^27`, where `u^(2^28) = y` and `mu` is a fixed primitive `2^28`-th root of unity (`2^28 | p - 1`; a constant of the offline derivation, 6.2). `u` comes from 28 successive Tonelli-Shanks square roots: `y` is a `2^28`-th power, and if `x` is a `2^k`-th power with `1 <= k <= 28`, both square roots of `x` are `2^(k-1)`-th powers (`-1` is a `2^(k-1)`-th power, `2^k | p - 1`). The scan takes `s = u mu^j` for `j = 0, 1, ..., 2^27 - 1` and stops at the first `j` with `F(c + s) = F(c - s)` (two line evaluations of section 3). For `S' = s^2` a root of `g_c` this holds, because `F(c + s) - F(c - s) = 2 s g_c(s^2)`, so the scan stops at the latest at the `j` of `S`; any stop has `s != 0` (`y != 0`) and `F(c + s) = F(c - s)`, a collision by 2.4. Charge per candidate: `s <- s mu` 1, `c + s` and `c - s` 2, two line evaluations `2 * 302`, their calls 4, the comparison and branch 2, the loop control 3: `616`; at most `2^27` candidates, `82,678,120,448`, and the loop exit 2. The 28 square roots are charged `47,012` each (the whole row F of the algorithm without the prefix, a square root and the back-map), `1,316,336`, and the back-map `47,012`: row F = `82,679,483,798`.

### 4.2 Machine model and charging rules (392 registers)

Every field operation, load, store, control operation and random word costs one
primitive operation under `orchard-field-ram-v2`; `C(7) = 363` primitive
operations is one target-compression unit. The single 392-word file contains
256 field registers and 136 integer address registers and is charged in
section 7. A radix-128 block holds 128 values, 127 twiddles and one field
temporary; its call holds at most 128 row bases, a twiddle address, a position
offset and a loop bound.

Stage C uses the selected radix-16/32/64 truncated schedule. Its ordinary
polynomial products and all Stage-D node products use running
twiddles. For a width-`k` pass beginning at level `l`, let
`blocks = 2^(a-k)` and `positions = 2^(a-l-k)`. A block costs

    B(k) = 2*2^k + 3k*2^(k-1) + 3.

The terms are `2^k` loads, `2^k` stores, `k*2^(k-1)` three-operation
butterflies, two base updates and the four-block-loop share. One running chain
costs `2^k+4`: one root advance, `k-1` squarings,
`2^k-1-k` constant multiplications and five controls. The implementation
constructs one chain per position and reuses it across every block at that
position. It does not construct a chain per block. Group zero removes
`2^k-1` twiddle-one multiplications for each position and pays three controls.

The product-transform forward pass is therefore

    blocks*B(k) + positions*(2^k+4) + 9k+19
      - positions*(2^k-1) + 3,

with 20 in place of 19 for an inverse. The Stage-C product row uses its
declared constant-construction loop `150k`, the same position-shared chain,
block body and group-zero saving. Appendix E computes every selected pass from
these formulas. Neither stage allocates a product-twiddle table.

Each outer key constructs every valid direct, descending fixed-slot and
in-place candidate on `2^a` or `3*2^a` points up to `3*(budget+1)`. Direct
plans use four persistent matrix spectra and two folded operand/output
spectra. Their fused two-output point row contains six addressed loads, four
multiplications, two additions or subtractions, and both output stores.
Fixed-slot plans use `B=N-budget >= budget+1`; operand blocks run from highest
to lowest before their lower and upper output halves overwrite the pair. The
in-place family retains g and R and holds four matrix spectra. One immutable
plan supplies both the operation rows and the allocation lifetimes. Every
family reserves one explicitly charged apply arena and suballocates its four
or six logical spectra inside it. Appendix
E.2.1 expands every selected row and all atomic action dictionaries.

Allocation uses one preallocated LIFO pool. A block is a 64-byte header plus
payload rounded to 64 bytes. Long-lived outputs precede the temporary regions
that produce them, and named releases rewind in reverse order. The single
trace in Appendix E.3 begins with every fixed resident region, walks all A-D
pool objects, records each E/F/G slab occupancy and release, and enters and
leaves every component of the live stack chain. Its maximum is the submitted
footprint.

Jbenisek `68328ed9`, `56272e37`, `27fbfbe7` and `c7ef0551` are credited for
the split, running-twiddle, four-block and wide-register constructions. The
resource integers below are generated inside this package.

### 4.3G The Graeffe prefix

Definition. For `h` monic of even degree `m` write `h(X) = E(X^2) + X O(X^2)`; its Graeffe transform is `h~(Y) = E(Y)^2 - Y O(Y)^2`, so `h~(X^2) = h(X) h(-X)` and `h~` is monic of degree `m` with roots the squares of the roots of `h` (with multiplicity). Stage C first replaces `g = g_c` by `g^(27)`, 27 Graeffe steps, then computes `R = S^e mod g^(27)`, `e = (p-1)/2^28` (2-adicity 32), and stage D takes `G = gcd(g^(27), R - 1)`.

Lemma. `G` is the product of `(Y - y)` over the distinct values `y = S^(2^27)`, `S` a usable root of `g_c` (a nonzero square in `F_p` with `g_c(S) = 0`, section 3). Proof: `g^(27)(Y) = prod_i (Y - S_i^(2^27))` over the roots `S_i` of `g_c` in an algebraic closure; `Y^e - 1` is squarefree and its roots are the `2^28`-th powers of `F_p^*`. If `S_i^(2^27) = u^(2^28)` with `u` in `F_p^*`, then `S_i = u^2 zeta` with `zeta^(2^27) = 1`, so `zeta` is in `F_p` and `zeta = xi^2` with `xi^(2^28) = 1` (`2^28 | p - 1`), and `S_i = (u xi)^2` is a nonzero square of `F_p`; conversely `S = v^2` gives `S^(2^27) = v^(2^28)`. So `deg G` is the number of distinct `2^27`-th powers of the usable roots: `1 <= deg G <= k(c)` when `k(c) >= 1`, and `deg G = 0` when `k(c) = 0`; the event `E_c` of 9.2 gives `1 <= deg G <= DMAX`.

Execution (on the point set `O1` of 4.3T). One step: `E` (`m/2 + 1` coefficients) and `O` (`m/2`) are read from `g` at stride 2 by the top passes of two truncated forwards, which load only the input blocks below the length (3 or 2 of the 8 per offset, two offset ranges per batch; butterflies only on nonzero inputs; no zero-fill); the fused bottom pass forms `G = (E^2 - y O^2)/N` at each point `y` of `O1` between the forward and the inverse bottom layers (`y` is the last-layer twiddle of its butterfly, in a register: two squarings, two multiplications, one subtraction, 5 per point); one truncated inverse stores the new coefficients into the array of `g` (those above `m` come out zero). `E` and `O` on `O1` use the arrays of `A` on `O2` and of `A` on `O1` before stage C fills them, with a batch buffer of `5,177,344` words of their own, used by one transform at a time and freed after the prefix; no array is added and the high-water mark of section 7 is unchanged. One step is `120,764,295,858` operations (Appendix E.1), 27 steps; stage C then executes the 199 bits after the leading one and its 27 HIGH zero bits; no low exponent bit is discarded. A bit-zero powering step is `178,712,492,588`. Depth 27 is the fixed Graeffe-prefix choice of this algorithm; the split planner changes only its transform schedule.

Every map is exact; no premise is added to the time or the memory. The zero test of `k1` (4.3T) now concerns `g^(27)`: `g^(27)(y) = 0` for `y` in `O1` only if `g_c(x) = 0` for one of the `2^27` values `x` with `x^(2^27) = y` (in `F_p` or an extension); for each such `x`, `g_c(x)` is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so over the centre `P(g^(27) vanishes on O1) <= 2^27 n' (D - 1) / p = eps_g < 2^-167`.

### 4.3T Stage C in the value domain on truncated point sets

Let `N=2^30`, `Y=X^(2^19)`, and let O1 contain the first 1165 of the
2048 depth-11 nodes of the subgroup. O2 contains the corresponding nodes in
its disjoint coset. Thus `n'=1165*2^19=610,795,520`. The CRT on the live
moduli is bijective for every residue of degree below `n'`.

The selected 30-layer transform is `3 | 4, 5, 6, 6 | 6`. The top three layers
run on all `N/8` offsets. The table gives the exact block and chain counts at
each cumulative layer offset; the first pass includes its padded class-batch
blocks. A block charges
`2*2^k` loads and stores, `k*2^(k-1)` three-action butterflies, and three
pointer/control actions. A chain charges one root advance, `k-1` squarings,
the remaining constant multiplications and five controls, `2^k+4` actions.
The fixed wrapper is `159k+19`.

| width | layer offset | execution | blocks | chains | fallback | pass operations |
| ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 4 | 0 | class-batched-first-pass | 38,273,024 | 1,024 | 0 | 5,013,789,568 |
| 5 | 4 | live-node-position-shared | 19,087,360 | 4,771,840 | 337,032,448 | 6,368,639,022 |
| 6 | 9 | live-node-position-shared | 9,543,680 | 74,560 | 0 | 6,752,452,813 |
| 6 | 15 | live-node-position-shared | 9,543,680 | 1,165 | 0 | 6,747,461,953 |
| | | | | | **middle set** | **24,882,343,356** |

The 64-point bottom has 9,543,680 blocks. Its twiddle chain
is four addressed table loads, one multiplication, five squarings and 57
constant multiplications, 67 actions. A forward block costs 774 and inverse
scaling adds 65, giving 839. The fused O1 and O2 powering blocks cost 1,671
and 2,055. The fused Graeffe block holds both 64-value blocks and 63 shared
twiddles in 192 field registers and costs 2,376. The generated code asserts
each of these decompositions.

Layers 1 through 7 use 128 batches of 65,536 classes, a 3,604,480-word batch
region and a 1,572,864-word tail, 5,177,344 words in all.
Every non-calibration candidate uses the executable fallback
holding all `N-n'` omitted positions, charges its zero fill and every full
position-shared pass; its larger buffer enters its score key. The calibrated
width-five pass crosses the node/inner boundary and charges
337,032,448 generated fallback actions.

The offline planner enumerates all 987,568 ordered
compositions of 21 with widths 1 through 7, including `4,5,6,6`. Every plan
covers `3+21+6=30` layers, checks ordinary and fused register requirements,
emits operation rows and a memory schedule, and compares 11 cap rows with the
ordered five-field key `(N*bytes, N, bytes, split, cap)`. The search constructs
10,863,248 split-cap rows and costs
3,306,377,588 operations. It selects `4, 5, 6, 6`.

The selected code manifest comes from the same atomic bodies. It emits the
ordinary and group-zero paths, including the bit-one O2 body, in three
unrolled copies:

| family | ordinary operations | group-zero operations | copies | emitted operations | emitted bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| middle-width-4 | 131 | 116 | 3 | 741 | 2,964 |
| middle-width-5 | 307 | 276 | 3 | 1,749 | 6,996 |
| middle-width-6 | 707 | 644 | 3 | 4,053 | 16,212 |
| bottom-forward | 774 | 711 | 3 | 4,455 | 17,820 |
| bottom-inverse | 839 | 776 | 3 | 4,845 | 19,380 |
| bottom-o1 | 1,671 | 1,545 | 3 | 9,648 | 38,592 |
| bottom-o2-zero | 2,055 | 1,929 | 3 | 11,952 | 47,808 |
| bottom-o2-one | 2,248 | 2,122 | 3 | 13,110 | 52,440 |
| bottom-graeffe | 2,376 | 2,187 | 3 | 13,689 | 54,756 |
| **selected split routines** | | | | **64,242** | **256,968** |

At four bytes per instruction these families occupy
256,968 bytes in the traced image.

For residues below degree `n'`, `Mont(A,B)=(AB+ug)/P1`, with
`u=-AB/g mod P1`. Values on O1 determine `u`; inverse/forward extensions
carry it to O2, where node constants apply the exact division by P1. The
program executes 154 bit-zero and 45 bit-one steps after the leading bit.
`VSHIFT_LOG=27` means the 27 HIGH zero bits immediately after the leading bit
are skipped. No low exponent bit is discarded.

The 27 Graeffe maps use arrays that powering has not yet filled and the same
traced batch/tail scratch. One generated map costs
120,764,295,858 operations. Newton, quotient, coset maps, chunked
batch inversion, exits and final inverses remain generated from the judged
formulas. Appendix E.1 lists every component and sums to
**row C = 39,755,214,775,564**. Every map is exact; Stage C adds no premise.

### 4.4 Stage D: inversion-free half-gcd, three-row apply and two-row product

`G=gcd(g,R-1)` uses pseudo-division and the normal-sequence quotient and
return tests. A node of budget `2^j-1` calls two children of budget
`2^(j-1)-1`; its apply uses `Y-1,Y+1,Y-i`, while its matrix product uses
`Y-1,Y+1`. On the normal sequence the product entries have degree at most
`2n-1`, so those two rows determine them.

The driver starts at degree 610,351,562 and selects the largest fitting budget
under cap 25. Each outer key constructs all valid direct, descending
fixed-slot and in-place plans. The selected schedule has
15 fixed-slot, 0 direct and
28 in-place applies. The same immutable plan supplies its
operation rows and memory lifetimes.

The accepted r7-v5 allocation schedule is retained. Four separate coefficient
matrix blocks are allocated before the recursive bump. The bump is released
after node return, while all four coefficient blocks remain live through the
apply-arena allocation and use. The apply arena is then released, followed by
the four coefficient blocks in reverse order. No compaction or alias claim is
used.

The quotient-tested division costs `15*(degree-budget)+4,454`. The remainder
uses the explicit classical tail. Appendix E.2 prints every node, apply and
division row and sums to
**row D = 13,261,477,440,486**. An abnormal quotient, short return or zero
remainder ABORTs after a prefix of the same operation and allocation walk.

## 5. Why the output is a collision

By 2.4 any `W1 != W2` with `F(W1) = F(W2)` maps back to distinct canonical
inputs with equal digests. Stage D returns `G=gcd(g,R-1)`, whose roots are the
values `S^(2^27)` of usable roots of `g_c`. Stage F stops only at nonzero `s`
with `F(c+s)=F(c-s)`. Stage G checks both inputs with the reference hash before
returning them.

## 6. Complete operation ledger

| row | event family | operations |
| --- | --- | ---: |
| init | constants and bookkeeping | 17,978 |
| setup | line setup | 4,910 |
| A | coin draw and allocation | 1,228 |
| B | line evaluations, inverse transform and normalization | 793,955,629,857 |
| C | Graeffe prefix and value-domain powering | 39,755,214,775,564 |
| D | generated half-gcd nodes, applies, drivers and tail | 13,261,477,440,486 |
| E | 64 constant-work isolation rounds | 139,023,366 |
| F | root lifts and complete candidate scan | 82,679,483,798 |
| G | two reference verifications | 8,292 |
| trial_loop | reset and closing control | 1,012 |
| plan_cache | 73 immutable runtime plan lookups | 9,430 |
| output | two output rows | 3,390,080 |
| offline | every constructed and compared planner candidate plus constants | 3,385,909,901 |
| **N_max** | sum of the live rows | **53,896,855,695,902** |

The exact raw time is `log2(N_max/363) = 37.111440605173620160957167327842734433489503498793184103317386998256925220001139`; upward rounding gives
`37.11145`. No predecessor row, delta or retained cap is an input.

### 6.1 Exact-integer evidence

Appendix E is rendered from the same live dictionaries and objects used by
`LEDGER`. Assertions bind every displayed C component, D component, planner
row, memory event, total and logarithm to the ledger.

### 6.2 Named primitive-action decomposition and planner

| fixed group | named one-operation actions | total |
| --- | --- | ---: |
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
| driver fixed | entry exit 28; degree and budget tests 24; quotient return and zero tests 32; coefficient loop setup 64; source and result descriptors 384; scale and leading setup 256; apply result fold setup 512; address base updates 768; arena mark and release 256; driver state updates 1,024; abort and cleanup 512; plan dispatch 480; final branches 114 | 4,454 |
| tail normalize | entry 28; degree tests 24; row descriptors 64; coefficient descriptors 64; normalization setup 96; arena actions 72; result tests 56; exit 96 | 500 |
| tail frame | 128 step dispatches at 32 4,096; 128 quotient return tests at 16 2,048; 64 descriptors at 32 2,048; cleanup and reset 1,024; entry exit 784 | 10,000 |
| r7 apply allocator call | size and class tests 40; free list and extent tests 32; header and payload updates 32; live extent updates 20; entry exit and return 13 | 137 |
| direct point | operand a address 1; operand a load 1; operand b address 1; operand b load 1; matrix r11 address 1; matrix r11 load 1; matrix r12 address 1; matrix r12 load 1; matrix r21 address 1; matrix r21 load 1; matrix r22 address 1; matrix r22 load 1; first field multiply 1; second field multiply 1; third field multiply 1; fourth field multiply 1; first output add subtract 1; second output add subtract 1; output c store 1; output d store 1 | 20 |
| direct placement | source address 1; source load 1; destination address 1; destination store 1; destination pointer update 1 | 5 |
| fixed-slot point | operand left load 1; operand right load 1; matrix left load 1; matrix right load 1; first field multiply 1; second field multiply 1; output add subtract 1; output store 1; operand left pointer update 1; operand right pointer update 1; matrix left pointer update 1; matrix right pointer update 1 | 12 |
| fixed-slot placement | spectrum load 1; scale load 1; scale multiplication 1; destination load 1; overlap add 1; destination store 1; destination pointer update 1 | 7 |
| copy live coefficient | source pointer update 1; source address 1; source load 1; destination pointer update 1; destination address 1; destination store 1; loop control 1 | 7 |
| zero padded coefficient | destination pointer update 1; destination address 1; zero store 1; loop update 1; loop branch 1 | 5 |
| cyclic fold coefficient | source pointer update 1; source address 1; source load 1; destination pointer update 1; destination address 1; destination load 1; field addition 1; destination store 1; loop update 1; loop branch 1 | 10 |
| in-place point | first matrix product 1; second matrix product 1; third matrix product 1; fourth matrix product 1; first output add subtract 1; second output add subtract 1; first inverse scale 1; second inverse scale 1; first shared operand access 1; second shared operand access 1; first shared output access 1; second shared output access 1 | 12 |
| in-place output | source load 1; inverse scale multiply 1; destination store 1; destination pointer update 1 | 4 |
| split-plan construction | geometry and layer updates 96; row descriptor construction 128; pass schedule construction 128; register and memory validation 48 | 400 |
| split-cap row construction | cap geometry and schedule 48; stage row assembly 64; memory trace and key fields 40; score product and tuple store 40 | 192 |
| split-plan comparison | five key field load pairs 20; five ordered key comparisons 20; five comparison branches 20; selected record updates 16 | 76 |
| allocator call | size class tests 256; free list tests 128; header and payload updates 128; extent and live updates 96; entry exit and return 47 | 655 |
| close 42 | entry exit 8; length tests 8; descriptor updates 12; result and branch updates 14 | 42 |
| close 31 | entry exit 7; length tests 6; descriptor updates 8; result and branch updates 10 | 31 |
| init | 201 target constant descriptors at eight events 1,608; four 512 step field chains at five events 10,240; table address and storage setup 6,000; entry shape tests and exit 130 | 17,978 |
| setup | three 512 step field chains 1,536; nine 256 word descriptor rows 2,304; target specific line operations 966; entry exit and shape tests 104 | 4,910 |
| stage A | fresh field draw 63; allocator call 655; trial descriptor loop test and update 510 | 1,228 |
| stage G | verification bookkeeping 1,000; ten events for two reference hashes 7,260; distinctness encoding and exit 32 | 8,292 |
| trial loop | abort allocator reset 1,000; loop update test and branch 12 | 1,012 |
| output | first output map and encoding 1,572,864; second output map and encoding 1,572,864; canonical result rows and exit 244,352 | 3,390,080 |
| root lift | fixed square and multiply field events 45,056; two adic table load store and address events 1,280; candidate root tests and selects 512; entry exit loop and descriptor events 164 | 47,012 |
| Stage-F candidate | root update 1; two point additions 2; two line evaluations 604; four call boundaries 4; comparison and branch 2; loop update test branch 3 | 616 |
| node fixed | entry and exit 20; split and degree tests 16; two child call frames 50; two return tests 8; arena mark and release 20; six transform dispatches 18; matrix pointer bundles 48; row and sign selection 18; normal sequence tests 12 | 210 |
| base entry | six remainder array bindings 24; four matrix array bindings 16; eight degree budget fields 24; six call frame fields 18; four entry tests 8 | 90 |
| base step setup | eight quotient fields 32; six remainder row fields 24; five degree tests 10; five call edges 10 | 76 |
| base remainder coefficient | a load 1; a address 1; b load 1; b address 1; q0 multiplication 1; q1 multiplication 1; first subtraction 1; second subtraction 1; result store 1; result address 1; loop update 1; loop test 1; loop branch 1 | 13 |
| base matrix coefficient | matrix load 1; matrix address 1; other entry load 1; other entry address 1; field multiplication 1; field addition 1; matrix store 1; store address 1; loop control 1 | 9 |
| base step close | two close tests 4; two close calls 4 | 8 |
| base final setup | five final field bindings 15; five final tests 10 | 25 |
| base final close | one final test 2; one final call 2 | 4 |
| Stage-E modular pair | convolution load store and field 6; convolution loop control 3; reduction load store and field 6; reduction loop control 3; coefficient address updates 4 | 22 |
| Stage-E modular row | output zero and loop 4; convolution row pointers 4; reduction leading load test 3; modulus row pointers 4; normalization and carry 5 | 20 |
| Stage-E modular fixed | entry exit 8; array descriptors 16; degree and bounds 8; buffer swaps 8; final tests 8; call frames 16 | 64 |
| Stage-E power copy | source load 1; destination store 1; source and destination updates 2; loop update test branch 3 | 7 |
| Stage-E power fixed | entry exit 4; buffer swap 4; length and degree tests 8; source and destination descriptors 8; exponent bit test and branch 4; call and return 3 | 31 |
| Stage-E gcd cell | active mask and degree test 2; coefficient loads 3; field multiply 1; field subtract 1; coefficient store 1; loop update test branch 3; address update 1 | 12 |
| Stage-E allocator | size class tests 256; free list tests 128; header and payload updates 128; extent and live updates 96; entry exit and return 47 | 655 |
| planner miscellaneous | capacity table 62 rows at 512 31,744; two logarithm interval bounds 8,192; score rounding and comparison 4,096; consistency comparisons 5,968 | 50,000 |
| shared bottom-forward body | input loads 64; output stores 64; bottom butterflies 576; block pointer and four block control 3; shared twiddle chain 67 | 774 |
| shared bottom-inverse body | input loads 64; output stores 64; bottom butterflies 576; block pointer and four block control 3; shared twiddle chain 67; inverse diagonal 65 | 839 |
| shared bottom-o1 body | two bottom butterfly directions 1,152; input loads and result stores 128; four pointwise actions 256; shared twiddle chain 67; inverse diagonal 65; block pointer and four block control 3 | 1,671 |
| shared bottom-o2-zero body | two bottom butterfly directions 1,152; input loads and result stores 128; ten pointwise actions 640; shared twiddle chain 67; inverse diagonal 65; block pointer and four block control 3 | 2,055 |
| shared bottom-o2-one body | two bottom butterfly directions 1,152; input loads and result stores 128; ten pointwise actions 640; bit one point actions 192; shared twiddle chain 67; inverse diagonal 65; block pointer and four block control 3; bit one point pointer update 1 | 2,248 |
| shared bottom-graeffe body | three bottom butterfly directions 1,728; three input output streams 192; five pointwise actions 320; shared twiddle chain 67; inverse diagonal 65; block pointer and control 4 | 2,376 |

The offline planner charges all 987,568 Stage-C
splits at 400 construction
actions each, all 10,863,248 split-cap rows at
192 actions each, and
all but the first row at
76 five-field comparison
actions. It
also charges every generated cap-18-through-cap-28 geometry,
all 62 transform candidates per Stage-D step, all Stage-C product candidates,
the low-cap screen, memory and exact-key finalization, target constants and
score comparisons. The exact selected total is 3,385,909,901; it is
the generated sum rather than a retained cap. Runtime plan work is only the
9,430-operation lookup table listed in Appendix E.2.2.

### 6.3 Normal-sequence charge and ABORT

Row D charges the normal sequence. Every division tests quotient degree one,
every recursive return tests its removed budget, and a zero remainder ends the
trial. At the first failed test the trial stops and resets. While tests pass,
all lengths, budgets and allocations are functions of `m`; an abnormal trial
therefore executes a prefix of the charged operation and resident-object
walk. H-NORMAL affects success probability, not the resource upper bound.

## 7. Memory from one complete resident-object trace

The trace begins with code/static data, the 65,536-byte stack reservation, the
392-word register file, offline workspace, arena gap, all slab-class
reservations and their free-list heads. It then walks every A-D allocation and
named reverse-order release, every E/F/G slab occupancy and release, and each
component of the 36,864-byte live stack chain. Its maximum is exactly
78,353,750,600 bytes.

| resident region | bytes |
| --- | ---: |
| two-ended/LIFO pool high-water | 78,348,064,512 |
| arena middle gap | 128 |
| slab class reservations | 11,136 |
| slab free-list heads | 128 |
| **arena** | **78,348,075,904** |
| code and static families | 5,595,080 |
| rounded stack reservation | 65,536 |
| 392-word register file | 12,544 |
| offline workspace | 1,536 |
| **footprint** | **78,353,750,600** |

The raw logarithm is `36.189283283463162225724149797970592471079052390402451389704234611882363183684064` and the upward-rounded claim is
`36.18929`. The Barrett quotient and all full-size value arrays occur
for their complete lifetimes. No product-twiddle table or stored advice exists.

## 8. Evaluation obligations

1. Sections 1 through 3 fix the target, input map and full-field output.
2. Sections 4 and 5 define every algorithm stage and the collision check.
3. Sections 4.2, 6, 7 and Appendices E and X define every resource charge and resident object.
4. Sections 4.1.1 and 9.2 define the probability space over fresh random words.
5. Claim.json and sections 9.1 and 9.5 disclose H-ONE and H-NORMAL; no resource heuristic is added.
6. Section 10 and both manifests bind the unchanged experiments to the retained premises.

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

## Appendix E: generated rows and complete trace

### E.1 Stage C

| component | operations |
| --- | ---: |
| setup | 7,993,829 |
| graeffe | 3,260,636,008,825 |
| newton | 339,737,541,382 |
| quotient | 74,222,739,071 |
| g maps | 80,324,544,970 |
| A0 O2 | 46,386,274,965 |
| A0 O1 | 93,126,802,245 |
| k1 | 9,394,263,125 |
| squares | 35,646,672,885,812 |
| exit | 100,723,571,530 |
| final inverses | 103,982,148,810 |
| bookkeeping | 1,000 |
| **row C** | **39,755,214,775,564** |

### E.2 Stage D

| step | degree | level | node | apply family:points | apply | driver | total |
| ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | 610,351,562 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 252,712,863,428 | 8,651,961,419 | 847,389,761,214 |
| 2 | 576,797,130 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 241,734,299,672 | 8,148,644,939 | 835,907,880,978 |
| 3 | 543,242,698 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 228,281,096,492 | 7,645,328,459 | 821,951,361,318 |
| 4 | 509,688,266 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 217,302,532,736 | 7,142,011,979 | 810,469,481,082 |
| 5 | 476,133,834 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 203,849,329,556 | 6,638,695,499 | 796,512,961,422 |
| 6 | 442,579,402 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 192,870,765,800 | 6,135,379,019 | 785,031,081,186 |
| 7 | 409,024,970 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 179,417,562,620 | 5,632,062,539 | 771,074,561,526 |
| 8 | 375,470,538 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 168,438,998,864 | 5,128,746,059 | 759,592,681,290 |
| 9 | 341,916,106 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 154,985,795,684 | 4,625,429,579 | 745,636,161,630 |
| 10 | 308,361,674 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 144,007,231,928 | 4,122,113,099 | 734,154,281,394 |
| 11 | 274,807,242 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 130,554,028,748 | 3,618,796,619 | 720,197,761,734 |
| 12 | 241,252,810 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 119,575,464,992 | 3,115,480,139 | 708,715,881,498 |
| 13 | 207,698,378 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 106,122,261,812 | 2,612,163,659 | 694,759,361,838 |
| 14 | 174,143,946 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 95,143,698,056 | 2,108,847,179 | 683,277,481,602 |
| 15 | 140,589,514 | 25 | 586,024,936,367 | fixed-slot:100,663,296 | 81,690,494,876 | 1,605,530,699 | 669,320,961,942 |
| 16 | 107,035,082 | 25 | 586,024,936,367 | in-place:100,663,296 | 45,057,939,887 | 1,102,214,219 | 632,185,090,473 |
| 17 | 73,480,650 | 25 | 586,024,936,367 | in-place:50,331,648 | 22,688,667,863 | 598,897,739 | 609,312,501,969 |
| 18 | 39,926,218 | 24 | 274,818,348,423 | in-place:25,165,824 | 11,336,259,583 | 347,239,499 | 286,501,847,505 |
| 19 | 23,149,002 | 23 | 128,378,560,259 | in-place:16,777,216 | 7,151,639,887 | 221,410,379 | 135,751,610,525 |
| 20 | 14,760,394 | 22 | 59,639,755,857 | in-place:12,582,912 | 5,573,023,527 | 158,495,819 | 65,371,275,203 |
| 21 | 10,566,090 | 22 | 59,639,755,857 | in-place:8,388,608 | 3,513,605,383 | 95,581,259 | 63,248,942,499 |
| 22 | 6,371,786 | 21 | 27,796,111,601 | in-place:6,291,456 | 2,381,026,361 | 64,123,979 | 30,241,261,941 |
| 23 | 4,274,634 | 21 | 27,796,111,601 | in-place:3,145,728 | 1,184,863,073 | 32,666,699 | 29,013,641,373 |
| 24 | 2,177,482 | 20 | 12,910,282,705 | in-place:1,572,864 | 576,295,561 | 16,938,059 | 13,503,516,325 |
| 25 | 1,128,906 | 19 | 5,972,782,033 | in-place:786,432 | 281,448,881 | 9,073,739 | 6,263,304,653 |
| 26 | 604,618 | 18 | 2,750,447,201 | in-place:393,216 | 138,744,025 | 5,141,579 | 2,894,332,805 |
| 27 | 342,474 | 17 | 1,259,341,881 | in-place:262,144 | 87,022,317 | 3,175,499 | 1,349,539,697 |
| 28 | 211,402 | 16 | 572,247,477 | in-place:196,608 | 66,031,617 | 2,192,459 | 640,471,553 |
| 29 | 145,866 | 16 | 572,247,477 | in-place:98,304 | 34,549,545 | 1,209,419 | 608,006,441 |
| 30 | 80,330 | 15 | 257,143,043 | in-place:49,152 | 14,548,027 | 717,899 | 272,408,969 |
| 31 | 47,562 | 14 | 116,040,867 | in-place:32,768 | 10,758,677 | 472,139 | 127,271,683 |
| 32 | 31,178 | 13 | 51,942,147 | in-place:24,576 | 6,741,347 | 349,259 | 59,032,753 |
| 33 | 22,986 | 13 | 51,942,147 | in-place:16,384 | 4,376,859 | 226,379 | 56,545,385 |
| 34 | 14,794 | 12 | 23,020,739 | in-place:12,288 | 3,214,731 | 164,939 | 26,400,409 |
| 35 | 10,698 | 12 | 23,020,739 | in-place:8,192 | 2,072,275 | 103,499 | 25,196,513 |
| 36 | 6,602 | 11 | 10,074,931 | in-place:6,144 | 1,525,043 | 72,779 | 11,672,753 |
| 37 | 4,554 | 11 | 10,074,931 | in-place:3,072 | 775,067 | 42,059 | 10,892,057 |
| 38 | 2,506 | 10 | 4,334,971 | in-place:1,536 | 389,731 | 26,699 | 4,751,401 |
| 39 | 1,482 | 9 | 1,819,247 | in-place:1,024 | 234,939 | 19,019 | 2,073,205 |
| 40 | 970 | 8 | 732,441 | in-place:768 | 191,643 | 15,179 | 939,263 |
| 41 | 714 | 8 | 732,441 | in-place:512 | 115,411 | 11,339 | 859,191 |
| 42 | 458 | 7 | 292,407 | in-place:384 | 73,013 | 9,419 | 374,839 |
| 43 | 330 | 7 | 292,407 | in-place:256 | 58,683 | 7,499 | 358,589 |

| component | operations |
| --- | ---: |
| nodes | 10,565,081,374,069 |
| outer applies | 2,616,802,618,220 |
| drivers | 79,591,789,337 |
| classical tail | 1,658,860 |
| **row D** | **13,261,477,440,486** |

### E.2.1 Apply rows

| step | family | points | transforms | matrix input | operand input | pointwise | output | fixed | total |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | fixed-slot | 100,663,296 | 206,591,973,678 | 2,281,701,376 | 12,507,735,852 | 22,422,749,274 | 8,908,701,966 | 1,282 | 252,712,863,428 |
| 2 | fixed-slot | 100,663,296 | 196,754,260,656 | 2,281,701,376 | 11,366,885,164 | 22,422,749,274 | 8,908,701,966 | 1,236 | 241,734,299,672 |
| 3 | fixed-slot | 100,663,296 | 186,916,547,610 | 2,281,701,376 | 11,232,667,436 | 19,931,332,688 | 7,918,846,192 | 1,190 | 228,281,096,492 |
| 4 | fixed-slot | 100,663,296 | 177,078,834,588 | 2,281,701,376 | 10,091,816,748 | 19,931,332,688 | 7,918,846,192 | 1,144 | 217,302,532,736 |
| 5 | fixed-slot | 100,663,296 | 167,241,121,542 | 2,281,701,376 | 9,957,599,020 | 17,439,916,102 | 6,928,990,418 | 1,098 | 203,849,329,556 |
| 6 | fixed-slot | 100,663,296 | 157,403,408,520 | 2,281,701,376 | 8,816,748,332 | 17,439,916,102 | 6,928,990,418 | 1,052 | 192,870,765,800 |
| 7 | fixed-slot | 100,663,296 | 147,565,695,474 | 2,281,701,376 | 8,682,530,604 | 14,948,499,516 | 5,939,134,644 | 1,006 | 179,417,562,620 |
| 8 | fixed-slot | 100,663,296 | 137,727,982,452 | 2,281,701,376 | 7,541,679,916 | 14,948,499,516 | 5,939,134,644 | 960 | 168,438,998,864 |
| 9 | fixed-slot | 100,663,296 | 127,890,269,406 | 2,281,701,376 | 7,407,462,188 | 12,457,082,930 | 4,949,278,870 | 914 | 154,985,795,684 |
| 10 | fixed-slot | 100,663,296 | 118,052,556,384 | 2,281,701,376 | 6,266,611,500 | 12,457,082,930 | 4,949,278,870 | 868 | 144,007,231,928 |
| 11 | fixed-slot | 100,663,296 | 108,214,843,338 | 2,281,701,376 | 6,132,393,772 | 9,965,666,344 | 3,959,423,096 | 822 | 130,554,028,748 |
| 12 | fixed-slot | 100,663,296 | 98,377,130,316 | 2,281,701,376 | 4,991,543,084 | 9,965,666,344 | 3,959,423,096 | 776 | 119,575,464,992 |
| 13 | fixed-slot | 100,663,296 | 88,539,417,270 | 2,281,701,376 | 4,857,325,356 | 7,474,249,758 | 2,969,567,322 | 730 | 106,122,261,812 |
| 14 | fixed-slot | 100,663,296 | 78,701,704,248 | 2,281,701,376 | 3,716,474,668 | 7,474,249,758 | 2,969,567,322 | 684 | 95,143,698,056 |
| 15 | fixed-slot | 100,663,296 | 68,863,991,202 | 2,281,701,376 | 3,582,256,940 | 4,982,833,172 | 1,979,711,548 | 638 | 81,690,494,876 |
| 16 | in-place | 100,663,296 | 39,350,852,112 | 2,281,701,376 | 1,536,721,884 | 1,245,708,293 | 642,955,722 | 500 | 45,057,939,887 |
| 17 | in-place | 50,331,648 | 19,273,767,224 | 1,275,068,416 | 1,167,623,132 | 622,854,149 | 349,354,442 | 500 | 22,688,667,863 |
| 18 | in-place | 25,165,824 | 9,537,214,560 | 637,534,208 | 647,529,436 | 311,427,077 | 202,553,802 | 500 | 11,336,259,583 |
| 19 | in-place | 16,777,216 | 6,049,897,904 | 402,653,184 | 362,316,764 | 207,618,053 | 129,153,482 | 500 | 7,151,639,887 |
| 20 | in-place | 12,582,912 | 4,819,933,064 | 285,212,672 | 219,710,428 | 155,713,541 | 92,453,322 | 500 | 5,573,023,527 |
| 21 | in-place | 8,388,608 | 2,991,725,928 | 201,326,592 | 160,990,172 | 103,809,029 | 55,753,162 | 500 | 3,513,605,383 |
| 22 | in-place | 6,291,456 | 2,033,472,666 | 142,606,336 | 89,687,004 | 77,856,773 | 37,403,082 | 500 | 2,381,026,361 |
| 23 | in-place | 3,145,728 | 980,571,074 | 79,691,776 | 66,618,332 | 38,928,389 | 19,053,002 | 500 | 1,184,863,073 |
| 24 | in-place | 1,572,864 | 472,994,538 | 39,845,888 | 34,112,476 | 19,464,197 | 9,877,962 | 500 | 576,295,561 |
| 25 | in-place | 786,432 | 228,643,346 | 19,922,944 | 17,859,548 | 9,732,101 | 5,290,442 | 500 | 281,448,881 |
| 26 | in-place | 393,216 | 111,186,234 | 9,961,472 | 9,733,084 | 4,866,053 | 2,996,682 | 500 | 138,744,025 |
| 27 | in-place | 262,144 | 70,359,886 | 6,291,456 | 5,276,636 | 3,244,037 | 1,849,802 | 500 | 87,022,317 |
| 28 | in-place | 196,608 | 54,816,866 | 4,456,448 | 3,048,412 | 2,433,029 | 1,276,362 | 500 | 66,031,617 |
| 29 | in-place | 98,304 | 27,811,722 | 2,490,368 | 2,327,516 | 1,216,517 | 702,922 | 500 | 34,549,545 |
| 30 | in-place | 49,152 | 10,966,172 | 1,245,184 | 1,311,708 | 608,261 | 416,202 | 500 | 14,548,027 |
| 31 | in-place | 32,768 | 8,538,742 | 786,432 | 754,652 | 405,509 | 272,842 | 500 | 10,758,677 |
| 32 | in-place | 24,576 | 5,202,372 | 557,056 | 476,124 | 304,133 | 201,162 | 500 | 6,741,347 |
| 33 | in-place | 16,384 | 3,289,468 | 393,216 | 361,436 | 202,757 | 129,482 | 500 | 4,376,859 |
| 34 | in-place | 12,288 | 2,467,820 | 278,528 | 222,172 | 152,069 | 93,642 | 500 | 3,214,731 |
| 35 | in-place | 8,192 | 1,551,156 | 196,608 | 164,828 | 101,381 | 57,802 | 500 | 2,072,275 |
| 36 | in-place | 6,144 | 1,174,164 | 139,264 | 95,196 | 76,037 | 39,882 | 500 | 1,525,043 |
| 37 | in-place | 3,072 | 564,092 | 77,824 | 72,668 | 38,021 | 21,962 | 500 | 775,067 |
| 38 | in-place | 1,536 | 277,380 | 38,912 | 40,924 | 19,013 | 13,002 | 500 | 389,731 |
| 39 | in-place | 1,024 | 165,148 | 24,576 | 23,516 | 12,677 | 8,522 | 500 | 234,939 |
| 40 | in-place | 768 | 143,132 | 17,408 | 14,812 | 9,509 | 6,282 | 500 | 191,643 |
| 41 | in-place | 512 | 81,012 | 12,288 | 11,228 | 6,341 | 4,042 | 500 | 115,411 |
| 42 | in-place | 384 | 49,254 | 8,704 | 6,876 | 4,757 | 2,922 | 500 | 73,013 |
| 43 | in-place | 256 | 41,980 | 6,144 | 5,084 | 3,173 | 1,802 | 500 | 58,683 |

The named primitive-action dictionaries for every coefficient above appear in
section 6.2 and in the embedded `low_apply_plans.py`. Each selected total is
asserted against its generated operation rows.

### E.2.2 Runtime plan cache

| family | exact key | operations |
| --- | --- | ---: |
| stage_b_transform | `(805306368,)` | 61 |
| stage_c_layout | `(1073741824, 610795520, 524288, 1165, 3, 4, 5, 6, 6, 6)` | 67 |
| stage_c_product | `(2, 2)` | 64 |
| stage_c_product | `(4, 4)` | 64 |
| stage_c_product | `(8, 8)` | 64 |
| stage_c_product | `(16, 16)` | 64 |
| stage_c_product | `(32, 32)` | 64 |
| stage_c_product | `(64, 64)` | 64 |
| stage_c_product | `(128, 128)` | 64 |
| stage_c_product | `(256, 256)` | 64 |
| stage_c_product | `(512, 512)` | 64 |
| stage_c_product | `(1024, 1024)` | 64 |
| stage_c_product | `(2048, 2048)` | 64 |
| stage_c_product | `(4096, 4096)` | 64 |
| stage_c_product | `(8192, 8192)` | 64 |
| stage_c_product | `(16384, 16384)` | 64 |
| stage_c_product | `(32768, 32768)` | 64 |
| stage_c_product | `(65536, 65536)` | 64 |
| stage_c_product | `(131072, 131072)` | 64 |
| stage_c_product | `(262144, 262144)` | 64 |
| stage_c_product | `(524288, 524288)` | 64 |
| stage_c_product | `(1048576, 1048576)` | 64 |
| stage_c_product | `(2097152, 2097152)` | 64 |
| stage_c_product | `(4194304, 4194304)` | 64 |
| stage_c_product | `(8388608, 8388608)` | 64 |
| stage_c_product | `(16777216, 16777216)` | 64 |
| stage_c_product | `(33554432, 33554432)` | 64 |
| stage_c_product | `(67108864, 67108864)` | 64 |
| stage_c_product | `(134217728, 134217728)` | 64 |
| stage_c_product | `(134661687, 134661687)` | 64 |
| stage_d_apply | `(330, 7, 256, 6)` | 220 |
| stage_d_apply | `(458, 7, 384, 4)` | 160 |
| stage_d_apply | `(714, 8, 512, 6)` | 220 |
| stage_d_apply | `(970, 8, 768, 4)` | 160 |
| stage_d_apply | `(1482, 9, 1024, 6)` | 220 |
| stage_d_apply | `(2506, 10, 1536, 8)` | 259 |
| stage_d_apply | `(4554, 11, 3072, 8)` | 259 |
| stage_d_apply | `(6602, 11, 6144, 4)` | 160 |
| stage_d_apply | `(10698, 12, 8192, 6)` | 220 |
| stage_d_apply | `(14794, 12, 12288, 4)` | 160 |
| stage_d_apply | `(22986, 13, 16384, 6)` | 220 |
| stage_d_apply | `(31178, 13, 24576, 4)` | 160 |
| stage_d_apply | `(47562, 14, 32768, 6)` | 220 |
| stage_d_apply | `(80330, 15, 49152, 8)` | 259 |
| stage_d_apply | `(145866, 16, 98304, 8)` | 259 |
| stage_d_apply | `(211402, 16, 196608, 4)` | 160 |
| stage_d_apply | `(342474, 17, 262144, 6)` | 220 |
| stage_d_apply | `(604618, 18, 393216, 8)` | 259 |
| stage_d_apply | `(1128906, 19, 786432, 8)` | 259 |
| stage_d_apply | `(2177482, 20, 1572864, 8)` | 259 |
| stage_d_apply | `(4274634, 21, 3145728, 8)` | 259 |
| stage_d_apply | `(6371786, 21, 6291456, 4)` | 160 |
| stage_d_apply | `(10566090, 22, 8388608, 6)` | 220 |
| stage_d_apply | `(14760394, 22, 12582912, 4)` | 160 |
| stage_d_apply | `(23149002, 23, 16777216, 6)` | 220 |
| stage_d_apply | `(39926218, 24, 25165824, 8)` | 259 |
| stage_d_apply | `(73480650, 25, 50331648, 8)` | 259 |
| stage_d_apply | `(107035082, 25, 100663296, 4)` | 160 |
| stage_d_apply | `(140589514, 25, 100663296, 2)` | 100 |
| stage_d_apply | `(174143946, 25, 100663296, 2)` | 100 |
| stage_d_apply | `(207698378, 25, 100663296, 2)` | 100 |
| stage_d_apply | `(241252810, 25, 100663296, 2)` | 100 |
| stage_d_apply | `(274807242, 25, 100663296, 2)` | 100 |
| stage_d_apply | `(308361674, 25, 100663296, 2)` | 100 |
| stage_d_apply | `(341916106, 25, 100663296, 2)` | 100 |
| stage_d_apply | `(375470538, 25, 100663296, 2)` | 100 |
| stage_d_apply | `(409024970, 25, 100663296, 2)` | 100 |
| stage_d_apply | `(442579402, 25, 100663296, 2)` | 100 |
| stage_d_apply | `(476133834, 25, 100663296, 2)` | 100 |
| stage_d_apply | `(509688266, 25, 100663296, 2)` | 100 |
| stage_d_apply | `(543242698, 25, 100663296, 2)` | 100 |
| stage_d_apply | `(576797130, 25, 100663296, 2)` | 100 |
| stage_d_apply | `(610351562, 25, 100663296, 2)` | 100 |
| **runtime plan cache** | | **9,430** |

### E.2.3 Offline constructed-candidate planner

| component | operations |
| --- | ---: |
| stage c split candidates | 3,306,377,588 |
| stage d geometry candidates | 78,696,000 |
| node recurrence levels | 33,792 |
| stage c product candidates | 460,288 |
| low cap screen rows | 149,472 |
| memory total and exact key finalization | 5,632 |
| target constant derivation | 137,129 |
| planner miscellaneous | 50,000 |
| **offline** | **3,385,909,901** |

### E.3 Complete resident-object trace

| # | stage | action | object | region | object bytes | total resident bytes |
| ---: | --- | --- | --- | --- | ---: | ---: |
| 1 | fixed | reserve | code-and-static | fixed | 5,595,080 | 5,595,080 |
| 2 | fixed | reserve | stack-reservation | fixed | 65,536 | 5,660,616 |
| 3 | fixed | reserve | register-file | fixed | 12,544 | 5,673,160 |
| 4 | fixed | reserve | offline-workspace | fixed | 1,536 | 5,674,696 |
| 5 | fixed | reserve | arena-middle-gap | fixed | 128 | 5,674,824 |
| 6 | fixed | reserve | slab-class-reservations | fixed | 11,136 | 5,685,960 |
| 7 | fixed | reserve | slab-free-list-heads | fixed | 128 | 5,686,088 |
| 8 | A | alloc | A g | pool | 19,545,456,704 | 19,551,142,792 |
| 9 | A | free | A g | pool | 19,545,456,704 | 5,686,088 |
| 10 | B | alloc | B g result | pool | 19,545,456,704 | 19,551,142,792 |
| 11 | B | alloc | B interpolation | pool | 25,769,803,840 | 45,320,946,632 |
| 12 | B | alloc | B twiddle | pool | 4,294,967,360 | 49,615,913,992 |
| 13 | B | free | B twiddle | pool | 4,294,967,360 | 45,320,946,632 |
| 14 | B | free | B interpolation | pool | 25,769,803,840 | 19,551,142,792 |
| 15 | C | alloc | C W1/R | pool | 19,545,456,704 | 39,096,599,496 |
| 16 | C | alloc | C table | pool | 562,624 | 39,097,162,120 |
| 17 | C | alloc | C W0 | pool | 19,545,456,704 | 58,642,618,824 |
| 18 | C | alloc | C batch and tail scratch | pool | 165,675,072 | 58,808,293,896 |
| 19 | C | free | C batch and tail scratch | pool | 165,675,072 | 58,642,618,824 |
| 20 | C | alloc | C k1 | pool | 19,545,456,704 | 78,188,075,528 |
| 21 | C | alloc | C inversion scratch | pool | 165,675,072 | 78,353,750,600 |
| 22 | C | free | C inversion scratch | pool | 165,675,072 | 78,188,075,528 |
| 23 | C | free | C k1 | pool | 19,545,456,704 | 58,642,618,824 |
| 24 | C | free | C W0 | pool | 19,545,456,704 | 39,097,162,120 |
| 25 | D1 | alloc | D1 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 26 | D1 | alloc | D1 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 27 | D1 | alloc | D1 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 28 | D1 | alloc | D1 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 29 | D1 | alloc | D1 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 30 | D1 | free | D1 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 31 | D1 | alloc | D1 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 32 | D1 | free | D1 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 33 | D1 | free | D1 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 34 | D1 | free | D1 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 35 | D1 | free | D1 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 36 | D1 | free | D1 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 37 | D2 | alloc | D2 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 38 | D2 | alloc | D2 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 39 | D2 | alloc | D2 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 40 | D2 | alloc | D2 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 41 | D2 | alloc | D2 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 42 | D2 | free | D2 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 43 | D2 | alloc | D2 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 44 | D2 | free | D2 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 45 | D2 | free | D2 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 46 | D2 | free | D2 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 47 | D2 | free | D2 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 48 | D2 | free | D2 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 49 | D3 | alloc | D3 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 50 | D3 | alloc | D3 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 51 | D3 | alloc | D3 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 52 | D3 | alloc | D3 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 53 | D3 | alloc | D3 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 54 | D3 | free | D3 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 55 | D3 | alloc | D3 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 56 | D3 | free | D3 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 57 | D3 | free | D3 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 58 | D3 | free | D3 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 59 | D3 | free | D3 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 60 | D3 | free | D3 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 61 | D4 | alloc | D4 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 62 | D4 | alloc | D4 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 63 | D4 | alloc | D4 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 64 | D4 | alloc | D4 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 65 | D4 | alloc | D4 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 66 | D4 | free | D4 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 67 | D4 | alloc | D4 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 68 | D4 | free | D4 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 69 | D4 | free | D4 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 70 | D4 | free | D4 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 71 | D4 | free | D4 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 72 | D4 | free | D4 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 73 | D5 | alloc | D5 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 74 | D5 | alloc | D5 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 75 | D5 | alloc | D5 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 76 | D5 | alloc | D5 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 77 | D5 | alloc | D5 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 78 | D5 | free | D5 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 79 | D5 | alloc | D5 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 80 | D5 | free | D5 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 81 | D5 | free | D5 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 82 | D5 | free | D5 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 83 | D5 | free | D5 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 84 | D5 | free | D5 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 85 | D6 | alloc | D6 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 86 | D6 | alloc | D6 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 87 | D6 | alloc | D6 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 88 | D6 | alloc | D6 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 89 | D6 | alloc | D6 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 90 | D6 | free | D6 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 91 | D6 | alloc | D6 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 92 | D6 | free | D6 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 93 | D6 | free | D6 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 94 | D6 | free | D6 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 95 | D6 | free | D6 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 96 | D6 | free | D6 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 97 | D7 | alloc | D7 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 98 | D7 | alloc | D7 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 99 | D7 | alloc | D7 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 100 | D7 | alloc | D7 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 101 | D7 | alloc | D7 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 102 | D7 | free | D7 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 103 | D7 | alloc | D7 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 104 | D7 | free | D7 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 105 | D7 | free | D7 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 106 | D7 | free | D7 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 107 | D7 | free | D7 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 108 | D7 | free | D7 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 109 | D8 | alloc | D8 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 110 | D8 | alloc | D8 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 111 | D8 | alloc | D8 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 112 | D8 | alloc | D8 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 113 | D8 | alloc | D8 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 114 | D8 | free | D8 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 115 | D8 | alloc | D8 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 116 | D8 | free | D8 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 117 | D8 | free | D8 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 118 | D8 | free | D8 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 119 | D8 | free | D8 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 120 | D8 | free | D8 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 121 | D9 | alloc | D9 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 122 | D9 | alloc | D9 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 123 | D9 | alloc | D9 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 124 | D9 | alloc | D9 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 125 | D9 | alloc | D9 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 126 | D9 | free | D9 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 127 | D9 | alloc | D9 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 128 | D9 | free | D9 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 129 | D9 | free | D9 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 130 | D9 | free | D9 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 131 | D9 | free | D9 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 132 | D9 | free | D9 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 133 | D10 | alloc | D10 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 134 | D10 | alloc | D10 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 135 | D10 | alloc | D10 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 136 | D10 | alloc | D10 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 137 | D10 | alloc | D10 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 138 | D10 | free | D10 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 139 | D10 | alloc | D10 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 140 | D10 | free | D10 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 141 | D10 | free | D10 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 142 | D10 | free | D10 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 143 | D10 | free | D10 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 144 | D10 | free | D10 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 145 | D11 | alloc | D11 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 146 | D11 | alloc | D11 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 147 | D11 | alloc | D11 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 148 | D11 | alloc | D11 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 149 | D11 | alloc | D11 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 150 | D11 | free | D11 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 151 | D11 | alloc | D11 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 152 | D11 | free | D11 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 153 | D11 | free | D11 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 154 | D11 | free | D11 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 155 | D11 | free | D11 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 156 | D11 | free | D11 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 157 | D12 | alloc | D12 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 158 | D12 | alloc | D12 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 159 | D12 | alloc | D12 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 160 | D12 | alloc | D12 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 161 | D12 | alloc | D12 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 162 | D12 | free | D12 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 163 | D12 | alloc | D12 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 164 | D12 | free | D12 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 165 | D12 | free | D12 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 166 | D12 | free | D12 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 167 | D12 | free | D12 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 168 | D12 | free | D12 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 169 | D13 | alloc | D13 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 170 | D13 | alloc | D13 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 171 | D13 | alloc | D13 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 172 | D13 | alloc | D13 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 173 | D13 | alloc | D13 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 174 | D13 | free | D13 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 175 | D13 | alloc | D13 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 176 | D13 | free | D13 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 177 | D13 | free | D13 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 178 | D13 | free | D13 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 179 | D13 | free | D13 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 180 | D13 | free | D13 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 181 | D14 | alloc | D14 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 182 | D14 | alloc | D14 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 183 | D14 | alloc | D14 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 184 | D14 | alloc | D14 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 185 | D14 | alloc | D14 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 186 | D14 | free | D14 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 187 | D14 | alloc | D14 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 188 | D14 | free | D14 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 189 | D14 | free | D14 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 190 | D14 | free | D14 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 191 | D14 | free | D14 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 192 | D14 | free | D14 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 193 | D15 | alloc | D15 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 194 | D15 | alloc | D15 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 195 | D15 | alloc | D15 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 196 | D15 | alloc | D15 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 197 | D15 | alloc | D15 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 198 | D15 | free | D15 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 199 | D15 | alloc | D15 apply arena | pool | 19,327,352,896 | 62,719,482,824 |
| 200 | D15 | free | D15 apply arena | pool | 19,327,352,896 | 43,392,129,928 |
| 201 | D15 | free | D15 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 202 | D15 | free | D15 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 203 | D15 | free | D15 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 204 | D15 | free | D15 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 205 | D16 | alloc | D16 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 206 | D16 | alloc | D16 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 207 | D16 | alloc | D16 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 208 | D16 | alloc | D16 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 209 | D16 | alloc | D16 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 210 | D16 | free | D16 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 211 | D16 | alloc | D16 apply arena | pool | 12,884,901,952 | 56,277,031,880 |
| 212 | D16 | free | D16 apply arena | pool | 12,884,901,952 | 43,392,129,928 |
| 213 | D16 | free | D16 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 214 | D16 | free | D16 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 215 | D16 | free | D16 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 216 | D16 | free | D16 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 217 | D17 | alloc | D17 matrix 1 | pool | 1,073,741,952 | 40,170,904,072 |
| 218 | D17 | alloc | D17 matrix 2 | pool | 1,073,741,952 | 41,244,646,024 |
| 219 | D17 | alloc | D17 matrix 3 | pool | 1,073,741,952 | 42,318,387,976 |
| 220 | D17 | alloc | D17 matrix 4 | pool | 1,073,741,952 | 43,392,129,928 |
| 221 | D17 | alloc | D17 node bump | pool | 17,179,861,056 | 60,571,990,984 |
| 222 | D17 | free | D17 node bump | pool | 17,179,861,056 | 43,392,129,928 |
| 223 | D17 | alloc | D17 apply arena | pool | 6,442,451,008 | 49,834,580,936 |
| 224 | D17 | free | D17 apply arena | pool | 6,442,451,008 | 43,392,129,928 |
| 225 | D17 | free | D17 matrix 4 | pool | 1,073,741,952 | 42,318,387,976 |
| 226 | D17 | free | D17 matrix 3 | pool | 1,073,741,952 | 41,244,646,024 |
| 227 | D17 | free | D17 matrix 2 | pool | 1,073,741,952 | 40,170,904,072 |
| 228 | D17 | free | D17 matrix 1 | pool | 1,073,741,952 | 39,097,162,120 |
| 229 | D18 | alloc | D18 matrix 1 | pool | 536,871,040 | 39,634,033,160 |
| 230 | D18 | alloc | D18 matrix 2 | pool | 536,871,040 | 40,170,904,200 |
| 231 | D18 | alloc | D18 matrix 3 | pool | 536,871,040 | 40,707,775,240 |
| 232 | D18 | alloc | D18 matrix 4 | pool | 536,871,040 | 41,244,646,280 |
| 233 | D18 | alloc | D18 node bump | pool | 8,589,926,464 | 49,834,572,744 |
| 234 | D18 | free | D18 node bump | pool | 8,589,926,464 | 41,244,646,280 |
| 235 | D18 | alloc | D18 apply arena | pool | 3,221,225,536 | 44,465,871,816 |
| 236 | D18 | free | D18 apply arena | pool | 3,221,225,536 | 41,244,646,280 |
| 237 | D18 | free | D18 matrix 4 | pool | 536,871,040 | 40,707,775,240 |
| 238 | D18 | free | D18 matrix 3 | pool | 536,871,040 | 40,170,904,200 |
| 239 | D18 | free | D18 matrix 2 | pool | 536,871,040 | 39,634,033,160 |
| 240 | D18 | free | D18 matrix 1 | pool | 536,871,040 | 39,097,162,120 |
| 241 | D19 | alloc | D19 matrix 1 | pool | 268,435,584 | 39,365,597,704 |
| 242 | D19 | alloc | D19 matrix 2 | pool | 268,435,584 | 39,634,033,288 |
| 243 | D19 | alloc | D19 matrix 3 | pool | 268,435,584 | 39,902,468,872 |
| 244 | D19 | alloc | D19 matrix 4 | pool | 268,435,584 | 40,170,904,456 |
| 245 | D19 | alloc | D19 node bump | pool | 4,294,959,168 | 44,465,863,624 |
| 246 | D19 | free | D19 node bump | pool | 4,294,959,168 | 40,170,904,456 |
| 247 | D19 | alloc | D19 apply arena | pool | 2,147,483,712 | 42,318,388,168 |
| 248 | D19 | free | D19 apply arena | pool | 2,147,483,712 | 40,170,904,456 |
| 249 | D19 | free | D19 matrix 4 | pool | 268,435,584 | 39,902,468,872 |
| 250 | D19 | free | D19 matrix 3 | pool | 268,435,584 | 39,634,033,288 |
| 251 | D19 | free | D19 matrix 2 | pool | 268,435,584 | 39,365,597,704 |
| 252 | D19 | free | D19 matrix 1 | pool | 268,435,584 | 39,097,162,120 |
| 253 | D20 | alloc | D20 matrix 1 | pool | 134,217,856 | 39,231,379,976 |
| 254 | D20 | alloc | D20 matrix 2 | pool | 134,217,856 | 39,365,597,832 |
| 255 | D20 | alloc | D20 matrix 3 | pool | 134,217,856 | 39,499,815,688 |
| 256 | D20 | alloc | D20 matrix 4 | pool | 134,217,856 | 39,634,033,544 |
| 257 | D20 | alloc | D20 node bump | pool | 2,147,475,520 | 41,781,509,064 |
| 258 | D20 | free | D20 node bump | pool | 2,147,475,520 | 39,634,033,544 |
| 259 | D20 | alloc | D20 apply arena | pool | 1,610,612,800 | 41,244,646,344 |
| 260 | D20 | free | D20 apply arena | pool | 1,610,612,800 | 39,634,033,544 |
| 261 | D20 | free | D20 matrix 4 | pool | 134,217,856 | 39,499,815,688 |
| 262 | D20 | free | D20 matrix 3 | pool | 134,217,856 | 39,365,597,832 |
| 263 | D20 | free | D20 matrix 2 | pool | 134,217,856 | 39,231,379,976 |
| 264 | D20 | free | D20 matrix 1 | pool | 134,217,856 | 39,097,162,120 |
| 265 | D21 | alloc | D21 matrix 1 | pool | 134,217,856 | 39,231,379,976 |
| 266 | D21 | alloc | D21 matrix 2 | pool | 134,217,856 | 39,365,597,832 |
| 267 | D21 | alloc | D21 matrix 3 | pool | 134,217,856 | 39,499,815,688 |
| 268 | D21 | alloc | D21 matrix 4 | pool | 134,217,856 | 39,634,033,544 |
| 269 | D21 | alloc | D21 node bump | pool | 2,147,475,520 | 41,781,509,064 |
| 270 | D21 | free | D21 node bump | pool | 2,147,475,520 | 39,634,033,544 |
| 271 | D21 | alloc | D21 apply arena | pool | 1,073,741,888 | 40,707,775,432 |
| 272 | D21 | free | D21 apply arena | pool | 1,073,741,888 | 39,634,033,544 |
| 273 | D21 | free | D21 matrix 4 | pool | 134,217,856 | 39,499,815,688 |
| 274 | D21 | free | D21 matrix 3 | pool | 134,217,856 | 39,365,597,832 |
| 275 | D21 | free | D21 matrix 2 | pool | 134,217,856 | 39,231,379,976 |
| 276 | D21 | free | D21 matrix 1 | pool | 134,217,856 | 39,097,162,120 |
| 277 | D22 | alloc | D22 matrix 1 | pool | 67,108,992 | 39,164,271,112 |
| 278 | D22 | alloc | D22 matrix 2 | pool | 67,108,992 | 39,231,380,104 |
| 279 | D22 | alloc | D22 matrix 3 | pool | 67,108,992 | 39,298,489,096 |
| 280 | D22 | alloc | D22 matrix 4 | pool | 67,108,992 | 39,365,598,088 |
| 281 | D22 | alloc | D22 node bump | pool | 1,073,733,696 | 40,439,331,784 |
| 282 | D22 | free | D22 node bump | pool | 1,073,733,696 | 39,365,598,088 |
| 283 | D22 | alloc | D22 apply arena | pool | 805,306,432 | 40,170,904,520 |
| 284 | D22 | free | D22 apply arena | pool | 805,306,432 | 39,365,598,088 |
| 285 | D22 | free | D22 matrix 4 | pool | 67,108,992 | 39,298,489,096 |
| 286 | D22 | free | D22 matrix 3 | pool | 67,108,992 | 39,231,380,104 |
| 287 | D22 | free | D22 matrix 2 | pool | 67,108,992 | 39,164,271,112 |
| 288 | D22 | free | D22 matrix 1 | pool | 67,108,992 | 39,097,162,120 |
| 289 | D23 | alloc | D23 matrix 1 | pool | 67,108,992 | 39,164,271,112 |
| 290 | D23 | alloc | D23 matrix 2 | pool | 67,108,992 | 39,231,380,104 |
| 291 | D23 | alloc | D23 matrix 3 | pool | 67,108,992 | 39,298,489,096 |
| 292 | D23 | alloc | D23 matrix 4 | pool | 67,108,992 | 39,365,598,088 |
| 293 | D23 | alloc | D23 node bump | pool | 1,073,733,696 | 40,439,331,784 |
| 294 | D23 | free | D23 node bump | pool | 1,073,733,696 | 39,365,598,088 |
| 295 | D23 | alloc | D23 apply arena | pool | 402,653,248 | 39,768,251,336 |
| 296 | D23 | free | D23 apply arena | pool | 402,653,248 | 39,365,598,088 |
| 297 | D23 | free | D23 matrix 4 | pool | 67,108,992 | 39,298,489,096 |
| 298 | D23 | free | D23 matrix 3 | pool | 67,108,992 | 39,231,380,104 |
| 299 | D23 | free | D23 matrix 2 | pool | 67,108,992 | 39,164,271,112 |
| 300 | D23 | free | D23 matrix 1 | pool | 67,108,992 | 39,097,162,120 |
| 301 | D24 | alloc | D24 matrix 1 | pool | 33,554,560 | 39,130,716,680 |
| 302 | D24 | alloc | D24 matrix 2 | pool | 33,554,560 | 39,164,271,240 |
| 303 | D24 | alloc | D24 matrix 3 | pool | 33,554,560 | 39,197,825,800 |
| 304 | D24 | alloc | D24 matrix 4 | pool | 33,554,560 | 39,231,380,360 |
| 305 | D24 | alloc | D24 node bump | pool | 536,862,784 | 39,768,243,144 |
| 306 | D24 | free | D24 node bump | pool | 536,862,784 | 39,231,380,360 |
| 307 | D24 | alloc | D24 apply arena | pool | 201,326,656 | 39,432,707,016 |
| 308 | D24 | free | D24 apply arena | pool | 201,326,656 | 39,231,380,360 |
| 309 | D24 | free | D24 matrix 4 | pool | 33,554,560 | 39,197,825,800 |
| 310 | D24 | free | D24 matrix 3 | pool | 33,554,560 | 39,164,271,240 |
| 311 | D24 | free | D24 matrix 2 | pool | 33,554,560 | 39,130,716,680 |
| 312 | D24 | free | D24 matrix 1 | pool | 33,554,560 | 39,097,162,120 |
| 313 | D25 | alloc | D25 matrix 1 | pool | 16,777,344 | 39,113,939,464 |
| 314 | D25 | alloc | D25 matrix 2 | pool | 16,777,344 | 39,130,716,808 |
| 315 | D25 | alloc | D25 matrix 3 | pool | 16,777,344 | 39,147,494,152 |
| 316 | D25 | alloc | D25 matrix 4 | pool | 16,777,344 | 39,164,271,496 |
| 317 | D25 | alloc | D25 node bump | pool | 268,427,328 | 39,432,698,824 |
| 318 | D25 | free | D25 node bump | pool | 268,427,328 | 39,164,271,496 |
| 319 | D25 | alloc | D25 apply arena | pool | 100,663,360 | 39,264,934,856 |
| 320 | D25 | free | D25 apply arena | pool | 100,663,360 | 39,164,271,496 |
| 321 | D25 | free | D25 matrix 4 | pool | 16,777,344 | 39,147,494,152 |
| 322 | D25 | free | D25 matrix 3 | pool | 16,777,344 | 39,130,716,808 |
| 323 | D25 | free | D25 matrix 2 | pool | 16,777,344 | 39,113,939,464 |
| 324 | D25 | free | D25 matrix 1 | pool | 16,777,344 | 39,097,162,120 |
| 325 | D26 | alloc | D26 matrix 1 | pool | 8,388,736 | 39,105,550,856 |
| 326 | D26 | alloc | D26 matrix 2 | pool | 8,388,736 | 39,113,939,592 |
| 327 | D26 | alloc | D26 matrix 3 | pool | 8,388,736 | 39,122,328,328 |
| 328 | D26 | alloc | D26 matrix 4 | pool | 8,388,736 | 39,130,717,064 |
| 329 | D26 | alloc | D26 node bump | pool | 134,209,600 | 39,264,926,664 |
| 330 | D26 | free | D26 node bump | pool | 134,209,600 | 39,130,717,064 |
| 331 | D26 | alloc | D26 apply arena | pool | 50,331,712 | 39,181,048,776 |
| 332 | D26 | free | D26 apply arena | pool | 50,331,712 | 39,130,717,064 |
| 333 | D26 | free | D26 matrix 4 | pool | 8,388,736 | 39,122,328,328 |
| 334 | D26 | free | D26 matrix 3 | pool | 8,388,736 | 39,113,939,592 |
| 335 | D26 | free | D26 matrix 2 | pool | 8,388,736 | 39,105,550,856 |
| 336 | D26 | free | D26 matrix 1 | pool | 8,388,736 | 39,097,162,120 |
| 337 | D27 | alloc | D27 matrix 1 | pool | 4,194,432 | 39,101,356,552 |
| 338 | D27 | alloc | D27 matrix 2 | pool | 4,194,432 | 39,105,550,984 |
| 339 | D27 | alloc | D27 matrix 3 | pool | 4,194,432 | 39,109,745,416 |
| 340 | D27 | alloc | D27 matrix 4 | pool | 4,194,432 | 39,113,939,848 |
| 341 | D27 | alloc | D27 node bump | pool | 67,100,736 | 39,181,040,584 |
| 342 | D27 | free | D27 node bump | pool | 67,100,736 | 39,113,939,848 |
| 343 | D27 | alloc | D27 apply arena | pool | 33,554,496 | 39,147,494,344 |
| 344 | D27 | free | D27 apply arena | pool | 33,554,496 | 39,113,939,848 |
| 345 | D27 | free | D27 matrix 4 | pool | 4,194,432 | 39,109,745,416 |
| 346 | D27 | free | D27 matrix 3 | pool | 4,194,432 | 39,105,550,984 |
| 347 | D27 | free | D27 matrix 2 | pool | 4,194,432 | 39,101,356,552 |
| 348 | D27 | free | D27 matrix 1 | pool | 4,194,432 | 39,097,162,120 |
| 349 | D28 | alloc | D28 matrix 1 | pool | 2,097,280 | 39,099,259,400 |
| 350 | D28 | alloc | D28 matrix 2 | pool | 2,097,280 | 39,101,356,680 |
| 351 | D28 | alloc | D28 matrix 3 | pool | 2,097,280 | 39,103,453,960 |
| 352 | D28 | alloc | D28 matrix 4 | pool | 2,097,280 | 39,105,551,240 |
| 353 | D28 | alloc | D28 node bump | pool | 33,546,304 | 39,139,097,544 |
| 354 | D28 | free | D28 node bump | pool | 33,546,304 | 39,105,551,240 |
| 355 | D28 | alloc | D28 apply arena | pool | 25,165,888 | 39,130,717,128 |
| 356 | D28 | free | D28 apply arena | pool | 25,165,888 | 39,105,551,240 |
| 357 | D28 | free | D28 matrix 4 | pool | 2,097,280 | 39,103,453,960 |
| 358 | D28 | free | D28 matrix 3 | pool | 2,097,280 | 39,101,356,680 |
| 359 | D28 | free | D28 matrix 2 | pool | 2,097,280 | 39,099,259,400 |
| 360 | D28 | free | D28 matrix 1 | pool | 2,097,280 | 39,097,162,120 |
| 361 | D29 | alloc | D29 matrix 1 | pool | 2,097,280 | 39,099,259,400 |
| 362 | D29 | alloc | D29 matrix 2 | pool | 2,097,280 | 39,101,356,680 |
| 363 | D29 | alloc | D29 matrix 3 | pool | 2,097,280 | 39,103,453,960 |
| 364 | D29 | alloc | D29 matrix 4 | pool | 2,097,280 | 39,105,551,240 |
| 365 | D29 | alloc | D29 node bump | pool | 33,546,304 | 39,139,097,544 |
| 366 | D29 | free | D29 node bump | pool | 33,546,304 | 39,105,551,240 |
| 367 | D29 | alloc | D29 apply arena | pool | 12,582,976 | 39,118,134,216 |
| 368 | D29 | free | D29 apply arena | pool | 12,582,976 | 39,105,551,240 |
| 369 | D29 | free | D29 matrix 4 | pool | 2,097,280 | 39,103,453,960 |
| 370 | D29 | free | D29 matrix 3 | pool | 2,097,280 | 39,101,356,680 |
| 371 | D29 | free | D29 matrix 2 | pool | 2,097,280 | 39,099,259,400 |
| 372 | D29 | free | D29 matrix 1 | pool | 2,097,280 | 39,097,162,120 |
| 373 | D30 | alloc | D30 matrix 1 | pool | 1,048,704 | 39,098,210,824 |
| 374 | D30 | alloc | D30 matrix 2 | pool | 1,048,704 | 39,099,259,528 |
| 375 | D30 | alloc | D30 matrix 3 | pool | 1,048,704 | 39,100,308,232 |
| 376 | D30 | alloc | D30 matrix 4 | pool | 1,048,704 | 39,101,356,936 |
| 377 | D30 | alloc | D30 node bump | pool | 16,769,088 | 39,118,126,024 |
| 378 | D30 | free | D30 node bump | pool | 16,769,088 | 39,101,356,936 |
| 379 | D30 | alloc | D30 apply arena | pool | 6,291,520 | 39,107,648,456 |
| 380 | D30 | free | D30 apply arena | pool | 6,291,520 | 39,101,356,936 |
| 381 | D30 | free | D30 matrix 4 | pool | 1,048,704 | 39,100,308,232 |
| 382 | D30 | free | D30 matrix 3 | pool | 1,048,704 | 39,099,259,528 |
| 383 | D30 | free | D30 matrix 2 | pool | 1,048,704 | 39,098,210,824 |
| 384 | D30 | free | D30 matrix 1 | pool | 1,048,704 | 39,097,162,120 |
| 385 | D31 | alloc | D31 matrix 1 | pool | 524,416 | 39,097,686,536 |
| 386 | D31 | alloc | D31 matrix 2 | pool | 524,416 | 39,098,210,952 |
| 387 | D31 | alloc | D31 matrix 3 | pool | 524,416 | 39,098,735,368 |
| 388 | D31 | alloc | D31 matrix 4 | pool | 524,416 | 39,099,259,784 |
| 389 | D31 | alloc | D31 node bump | pool | 8,380,480 | 39,107,640,264 |
| 390 | D31 | free | D31 node bump | pool | 8,380,480 | 39,099,259,784 |
| 391 | D31 | alloc | D31 apply arena | pool | 4,194,368 | 39,103,454,152 |
| 392 | D31 | free | D31 apply arena | pool | 4,194,368 | 39,099,259,784 |
| 393 | D31 | free | D31 matrix 4 | pool | 524,416 | 39,098,735,368 |
| 394 | D31 | free | D31 matrix 3 | pool | 524,416 | 39,098,210,952 |
| 395 | D31 | free | D31 matrix 2 | pool | 524,416 | 39,097,686,536 |
| 396 | D31 | free | D31 matrix 1 | pool | 524,416 | 39,097,162,120 |
| 397 | D32 | alloc | D32 matrix 1 | pool | 262,272 | 39,097,424,392 |
| 398 | D32 | alloc | D32 matrix 2 | pool | 262,272 | 39,097,686,664 |
| 399 | D32 | alloc | D32 matrix 3 | pool | 262,272 | 39,097,948,936 |
| 400 | D32 | alloc | D32 matrix 4 | pool | 262,272 | 39,098,211,208 |
| 401 | D32 | alloc | D32 node bump | pool | 4,186,176 | 39,102,397,384 |
| 402 | D32 | free | D32 node bump | pool | 4,186,176 | 39,098,211,208 |
| 403 | D32 | alloc | D32 apply arena | pool | 3,145,792 | 39,101,357,000 |
| 404 | D32 | free | D32 apply arena | pool | 3,145,792 | 39,098,211,208 |
| 405 | D32 | free | D32 matrix 4 | pool | 262,272 | 39,097,948,936 |
| 406 | D32 | free | D32 matrix 3 | pool | 262,272 | 39,097,686,664 |
| 407 | D32 | free | D32 matrix 2 | pool | 262,272 | 39,097,424,392 |
| 408 | D32 | free | D32 matrix 1 | pool | 262,272 | 39,097,162,120 |
| 409 | D33 | alloc | D33 matrix 1 | pool | 262,272 | 39,097,424,392 |
| 410 | D33 | alloc | D33 matrix 2 | pool | 262,272 | 39,097,686,664 |
| 411 | D33 | alloc | D33 matrix 3 | pool | 262,272 | 39,097,948,936 |
| 412 | D33 | alloc | D33 matrix 4 | pool | 262,272 | 39,098,211,208 |
| 413 | D33 | alloc | D33 node bump | pool | 4,186,176 | 39,102,397,384 |
| 414 | D33 | free | D33 node bump | pool | 4,186,176 | 39,098,211,208 |
| 415 | D33 | alloc | D33 apply arena | pool | 2,097,216 | 39,100,308,424 |
| 416 | D33 | free | D33 apply arena | pool | 2,097,216 | 39,098,211,208 |
| 417 | D33 | free | D33 matrix 4 | pool | 262,272 | 39,097,948,936 |
| 418 | D33 | free | D33 matrix 3 | pool | 262,272 | 39,097,686,664 |
| 419 | D33 | free | D33 matrix 2 | pool | 262,272 | 39,097,424,392 |
| 420 | D33 | free | D33 matrix 1 | pool | 262,272 | 39,097,162,120 |
| 421 | D34 | alloc | D34 matrix 1 | pool | 131,200 | 39,097,293,320 |
| 422 | D34 | alloc | D34 matrix 2 | pool | 131,200 | 39,097,424,520 |
| 423 | D34 | alloc | D34 matrix 3 | pool | 131,200 | 39,097,555,720 |
| 424 | D34 | alloc | D34 matrix 4 | pool | 131,200 | 39,097,686,920 |
| 425 | D34 | alloc | D34 node bump | pool | 2,089,024 | 39,099,775,944 |
| 426 | D34 | free | D34 node bump | pool | 2,089,024 | 39,097,686,920 |
| 427 | D34 | alloc | D34 apply arena | pool | 1,572,928 | 39,099,259,848 |
| 428 | D34 | free | D34 apply arena | pool | 1,572,928 | 39,097,686,920 |
| 429 | D34 | free | D34 matrix 4 | pool | 131,200 | 39,097,555,720 |
| 430 | D34 | free | D34 matrix 3 | pool | 131,200 | 39,097,424,520 |
| 431 | D34 | free | D34 matrix 2 | pool | 131,200 | 39,097,293,320 |
| 432 | D34 | free | D34 matrix 1 | pool | 131,200 | 39,097,162,120 |
| 433 | D35 | alloc | D35 matrix 1 | pool | 131,200 | 39,097,293,320 |
| 434 | D35 | alloc | D35 matrix 2 | pool | 131,200 | 39,097,424,520 |
| 435 | D35 | alloc | D35 matrix 3 | pool | 131,200 | 39,097,555,720 |
| 436 | D35 | alloc | D35 matrix 4 | pool | 131,200 | 39,097,686,920 |
| 437 | D35 | alloc | D35 node bump | pool | 2,089,024 | 39,099,775,944 |
| 438 | D35 | free | D35 node bump | pool | 2,089,024 | 39,097,686,920 |
| 439 | D35 | alloc | D35 apply arena | pool | 1,048,640 | 39,098,735,560 |
| 440 | D35 | free | D35 apply arena | pool | 1,048,640 | 39,097,686,920 |
| 441 | D35 | free | D35 matrix 4 | pool | 131,200 | 39,097,555,720 |
| 442 | D35 | free | D35 matrix 3 | pool | 131,200 | 39,097,424,520 |
| 443 | D35 | free | D35 matrix 2 | pool | 131,200 | 39,097,293,320 |
| 444 | D35 | free | D35 matrix 1 | pool | 131,200 | 39,097,162,120 |
| 445 | D36 | alloc | D36 matrix 1 | pool | 65,664 | 39,097,227,784 |
| 446 | D36 | alloc | D36 matrix 2 | pool | 65,664 | 39,097,293,448 |
| 447 | D36 | alloc | D36 matrix 3 | pool | 65,664 | 39,097,359,112 |
| 448 | D36 | alloc | D36 matrix 4 | pool | 65,664 | 39,097,424,776 |
| 449 | D36 | alloc | D36 node bump | pool | 1,040,448 | 39,098,465,224 |
| 450 | D36 | free | D36 node bump | pool | 1,040,448 | 39,097,424,776 |
| 451 | D36 | alloc | D36 apply arena | pool | 786,496 | 39,098,211,272 |
| 452 | D36 | free | D36 apply arena | pool | 786,496 | 39,097,424,776 |
| 453 | D36 | free | D36 matrix 4 | pool | 65,664 | 39,097,359,112 |
| 454 | D36 | free | D36 matrix 3 | pool | 65,664 | 39,097,293,448 |
| 455 | D36 | free | D36 matrix 2 | pool | 65,664 | 39,097,227,784 |
| 456 | D36 | free | D36 matrix 1 | pool | 65,664 | 39,097,162,120 |
| 457 | D37 | alloc | D37 matrix 1 | pool | 65,664 | 39,097,227,784 |
| 458 | D37 | alloc | D37 matrix 2 | pool | 65,664 | 39,097,293,448 |
| 459 | D37 | alloc | D37 matrix 3 | pool | 65,664 | 39,097,359,112 |
| 460 | D37 | alloc | D37 matrix 4 | pool | 65,664 | 39,097,424,776 |
| 461 | D37 | alloc | D37 node bump | pool | 1,040,448 | 39,098,465,224 |
| 462 | D37 | free | D37 node bump | pool | 1,040,448 | 39,097,424,776 |
| 463 | D37 | alloc | D37 apply arena | pool | 393,280 | 39,097,818,056 |
| 464 | D37 | free | D37 apply arena | pool | 393,280 | 39,097,424,776 |
| 465 | D37 | free | D37 matrix 4 | pool | 65,664 | 39,097,359,112 |
| 466 | D37 | free | D37 matrix 3 | pool | 65,664 | 39,097,293,448 |
| 467 | D37 | free | D37 matrix 2 | pool | 65,664 | 39,097,227,784 |
| 468 | D37 | free | D37 matrix 1 | pool | 65,664 | 39,097,162,120 |
| 469 | D38 | alloc | D38 matrix 1 | pool | 32,896 | 39,097,195,016 |
| 470 | D38 | alloc | D38 matrix 2 | pool | 32,896 | 39,097,227,912 |
| 471 | D38 | alloc | D38 matrix 3 | pool | 32,896 | 39,097,260,808 |
| 472 | D38 | alloc | D38 matrix 4 | pool | 32,896 | 39,097,293,704 |
| 473 | D38 | alloc | D38 node bump | pool | 516,160 | 39,097,809,864 |
| 474 | D38 | free | D38 node bump | pool | 516,160 | 39,097,293,704 |
| 475 | D38 | alloc | D38 apply arena | pool | 196,672 | 39,097,490,376 |
| 476 | D38 | free | D38 apply arena | pool | 196,672 | 39,097,293,704 |
| 477 | D38 | free | D38 matrix 4 | pool | 32,896 | 39,097,260,808 |
| 478 | D38 | free | D38 matrix 3 | pool | 32,896 | 39,097,227,912 |
| 479 | D38 | free | D38 matrix 2 | pool | 32,896 | 39,097,195,016 |
| 480 | D38 | free | D38 matrix 1 | pool | 32,896 | 39,097,162,120 |
| 481 | D39 | alloc | D39 matrix 1 | pool | 16,512 | 39,097,178,632 |
| 482 | D39 | alloc | D39 matrix 2 | pool | 16,512 | 39,097,195,144 |
| 483 | D39 | alloc | D39 matrix 3 | pool | 16,512 | 39,097,211,656 |
| 484 | D39 | alloc | D39 matrix 4 | pool | 16,512 | 39,097,228,168 |
| 485 | D39 | alloc | D39 node bump | pool | 254,016 | 39,097,482,184 |
| 486 | D39 | free | D39 node bump | pool | 254,016 | 39,097,228,168 |
| 487 | D39 | alloc | D39 apply arena | pool | 131,136 | 39,097,359,304 |
| 488 | D39 | free | D39 apply arena | pool | 131,136 | 39,097,228,168 |
| 489 | D39 | free | D39 matrix 4 | pool | 16,512 | 39,097,211,656 |
| 490 | D39 | free | D39 matrix 3 | pool | 16,512 | 39,097,195,144 |
| 491 | D39 | free | D39 matrix 2 | pool | 16,512 | 39,097,178,632 |
| 492 | D39 | free | D39 matrix 1 | pool | 16,512 | 39,097,162,120 |
| 493 | D40 | alloc | D40 matrix 1 | pool | 8,320 | 39,097,170,440 |
| 494 | D40 | alloc | D40 matrix 2 | pool | 8,320 | 39,097,178,760 |
| 495 | D40 | alloc | D40 matrix 3 | pool | 8,320 | 39,097,187,080 |
| 496 | D40 | alloc | D40 matrix 4 | pool | 8,320 | 39,097,195,400 |
| 497 | D40 | alloc | D40 node bump | pool | 122,944 | 39,097,318,344 |
| 498 | D40 | free | D40 node bump | pool | 122,944 | 39,097,195,400 |
| 499 | D40 | alloc | D40 apply arena | pool | 98,368 | 39,097,293,768 |
| 500 | D40 | free | D40 apply arena | pool | 98,368 | 39,097,195,400 |
| 501 | D40 | free | D40 matrix 4 | pool | 8,320 | 39,097,187,080 |
| 502 | D40 | free | D40 matrix 3 | pool | 8,320 | 39,097,178,760 |
| 503 | D40 | free | D40 matrix 2 | pool | 8,320 | 39,097,170,440 |
| 504 | D40 | free | D40 matrix 1 | pool | 8,320 | 39,097,162,120 |
| 505 | D41 | alloc | D41 matrix 1 | pool | 8,320 | 39,097,170,440 |
| 506 | D41 | alloc | D41 matrix 2 | pool | 8,320 | 39,097,178,760 |
| 507 | D41 | alloc | D41 matrix 3 | pool | 8,320 | 39,097,187,080 |
| 508 | D41 | alloc | D41 matrix 4 | pool | 8,320 | 39,097,195,400 |
| 509 | D41 | alloc | D41 node bump | pool | 122,944 | 39,097,318,344 |
| 510 | D41 | free | D41 node bump | pool | 122,944 | 39,097,195,400 |
| 511 | D41 | alloc | D41 apply arena | pool | 65,600 | 39,097,261,000 |
| 512 | D41 | free | D41 apply arena | pool | 65,600 | 39,097,195,400 |
| 513 | D41 | free | D41 matrix 4 | pool | 8,320 | 39,097,187,080 |
| 514 | D41 | free | D41 matrix 3 | pool | 8,320 | 39,097,178,760 |
| 515 | D41 | free | D41 matrix 2 | pool | 8,320 | 39,097,170,440 |
| 516 | D41 | free | D41 matrix 1 | pool | 8,320 | 39,097,162,120 |
| 517 | D42 | alloc | D42 matrix 1 | pool | 4,224 | 39,097,166,344 |
| 518 | D42 | alloc | D42 matrix 2 | pool | 4,224 | 39,097,170,568 |
| 519 | D42 | alloc | D42 matrix 3 | pool | 4,224 | 39,097,174,792 |
| 520 | D42 | alloc | D42 matrix 4 | pool | 4,224 | 39,097,179,016 |
| 521 | D42 | alloc | D42 node bump | pool | 57,408 | 39,097,236,424 |
| 522 | D42 | free | D42 node bump | pool | 57,408 | 39,097,179,016 |
| 523 | D42 | alloc | D42 apply arena | pool | 49,216 | 39,097,228,232 |
| 524 | D42 | free | D42 apply arena | pool | 49,216 | 39,097,179,016 |
| 525 | D42 | free | D42 matrix 4 | pool | 4,224 | 39,097,174,792 |
| 526 | D42 | free | D42 matrix 3 | pool | 4,224 | 39,097,170,568 |
| 527 | D42 | free | D42 matrix 2 | pool | 4,224 | 39,097,166,344 |
| 528 | D42 | free | D42 matrix 1 | pool | 4,224 | 39,097,162,120 |
| 529 | D43 | alloc | D43 matrix 1 | pool | 4,224 | 39,097,166,344 |
| 530 | D43 | alloc | D43 matrix 2 | pool | 4,224 | 39,097,170,568 |
| 531 | D43 | alloc | D43 matrix 3 | pool | 4,224 | 39,097,174,792 |
| 532 | D43 | alloc | D43 matrix 4 | pool | 4,224 | 39,097,179,016 |
| 533 | D43 | alloc | D43 node bump | pool | 57,408 | 39,097,236,424 |
| 534 | D43 | free | D43 node bump | pool | 57,408 | 39,097,179,016 |
| 535 | D43 | alloc | D43 apply arena | pool | 32,832 | 39,097,211,848 |
| 536 | D43 | free | D43 apply arena | pool | 32,832 | 39,097,179,016 |
| 537 | D43 | free | D43 matrix 4 | pool | 4,224 | 39,097,174,792 |
| 538 | D43 | free | D43 matrix 3 | pool | 4,224 | 39,097,170,568 |
| 539 | D43 | free | D43 matrix 2 | pool | 4,224 | 39,097,166,344 |
| 540 | D43 | free | D43 matrix 1 | pool | 4,224 | 39,097,162,120 |
| 541 | C | free | C table | pool | 562,624 | 39,096,599,496 |
| 542 | C | free | C W1/R | pool | 19,545,456,704 | 19,551,142,792 |
| 543 | B | free | B g result | pool | 19,545,456,704 | 5,686,088 |
| 544 | E | occupy | factor | slab-1024 | 1,024 | 5,686,088 |
| 545 | E | occupy | base | slab-1024 | 1,024 | 5,686,088 |
| 546 | E | occupy | power-result | slab-1024 | 1,024 | 5,686,088 |
| 547 | E | occupy | product-scratch | slab-2048 | 2,048 | 5,686,088 |
| 548 | E | occupy | P-minus-one | slab-1024 | 1,024 | 5,686,088 |
| 549 | E | occupy | P-plus-one | slab-1024 | 1,024 | 5,686,088 |
| 550 | E | occupy | gcd-left | slab-1024 | 1,024 | 5,686,088 |
| 551 | E | occupy | gcd-right | slab-1024 | 1,024 | 5,686,088 |
| 552 | E | occupy | selected-factor | slab-1024 | 1,024 | 5,686,088 |
| 553 | E | occupy | random-words | slab-128 | 128 | 5,686,088 |
| 554 | E | release | random-words | slab-128 | 128 | 5,686,088 |
| 555 | E | release | selected-factor | slab-1024 | 1,024 | 5,686,088 |
| 556 | E | release | gcd-right | slab-1024 | 1,024 | 5,686,088 |
| 557 | E | release | gcd-left | slab-1024 | 1,024 | 5,686,088 |
| 558 | E | release | P-plus-one | slab-1024 | 1,024 | 5,686,088 |
| 559 | E | release | P-minus-one | slab-1024 | 1,024 | 5,686,088 |
| 560 | E | release | product-scratch | slab-2048 | 2,048 | 5,686,088 |
| 561 | E | release | power-result | slab-1024 | 1,024 | 5,686,088 |
| 562 | E | release | base | slab-1024 | 1,024 | 5,686,088 |
| 563 | E | release | factor | slab-1024 | 1,024 | 5,686,088 |
| 564 | F | occupy | root-chain | slab-2048 | 2,048 | 5,686,088 |
| 565 | F | occupy | candidate-state | slab-1024 | 1,024 | 5,686,088 |
| 566 | F | occupy | input-pair | slab-256 | 256 | 5,686,088 |
| 567 | F | occupy | line-state | slab-256 | 256 | 5,686,088 |
| 568 | F | release | line-state | slab-256 | 256 | 5,686,088 |
| 569 | F | release | input-pair | slab-256 | 256 | 5,686,088 |
| 570 | F | release | candidate-state | slab-1024 | 1,024 | 5,686,088 |
| 571 | F | release | root-chain | slab-2048 | 2,048 | 5,686,088 |
| 572 | G | occupy | two-input-pairs | slab-256 | 256 | 5,686,088 |
| 573 | G | occupy | two-poseidon-states | slab-256 | 256 | 5,686,088 |
| 574 | G | occupy | canonical-encodings | slab-256 | 256 | 5,686,088 |
| 575 | G | occupy | output-elements | slab-128 | 128 | 5,686,088 |
| 576 | G | release | output-elements | slab-128 | 128 | 5,686,088 |
| 577 | G | release | canonical-encodings | slab-256 | 256 | 5,686,088 |
| 578 | G | release | two-poseidon-states | slab-256 | 256 | 5,686,088 |
| 579 | G | release | two-input-pairs | slab-256 | 256 | 5,686,088 |
| 580 | stack | enter | thirty_two_half_gcd_frames | stack-live | 32,768 | 5,686,088 |
| 581 | stack | enter | transform_scratch | stack-live | 1,024 | 5,686,088 |
| 582 | stack | enter | field_and_poseidon_scratch | stack-live | 1,024 | 5,686,088 |
| 583 | stack | enter | main_stage_allocator_and_saved_abi | stack-live | 2,048 | 5,686,088 |
| 584 | stack | leave | main_stage_allocator_and_saved_abi | stack-live | 2,048 | 5,686,088 |
| 585 | stack | leave | field_and_poseidon_scratch | stack-live | 1,024 | 5,686,088 |
| 586 | stack | leave | transform_scratch | stack-live | 1,024 | 5,686,088 |
| 587 | stack | leave | thirty_two_half_gcd_frames | stack-live | 32,768 | 5,686,088 |

The maximum final column is 78,353,750,600 bytes and equals the claim.

## Appendix X: complete ledger call graph

### ledger_v8.py

```python
#!/usr/bin/env python3
"""Absolute r7 ledger under the generated 392-register split search."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, getcontext
from functools import cache

import low_apply_plans as APPLY
import r7_machine as M
import stage_c_split_search as SPLIT
import stage_e_core as E


getcontext().prec = 80
COMPRESSION = 363
ODD_DEGREE = (5**13 - 1) // 2
N1 = 1165 * (1 << 19)
STAGE_B_POINTS = 3 * (1 << 28)
STAGE_B_INDEX_BITS = 28
STAGE_B_EVALUATION = 155 + 21 * 7
OFFLINE_FIELD_OPERATIONS = 494
OFFLINE_OUTPUT_LITERALS = 212
TARGET_CONSTANT_DERIVATION = (
    202 * (64 * 5 + 4)
    + 4 * OFFLINE_FIELD_OPERATIONS + 3 * 222
    + 3 * 90
    + OFFLINE_OUTPUT_LITERALS * (64 * 5 + 4) + (16 * 5 + 1)
)
PLANNER_MISC_PARTS = {
    "capacity_table_62_rows_at_512": 62 * 512,
    "two_logarithm_interval_bounds": 2 * 4_096,
    "score_rounding_and_comparison": 4_096,
    "consistency_comparisons": 5_968,
}
PLANNER_MISC = sum(PLANNER_MISC_PARTS.values())


def ceil_decimal(value: Decimal, places: int) -> Decimal:
    return value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_CEILING)


ORDER = 1 << 30
INNER = 1 << 19
TRC = 1165
OPTIMIZED_STAGE_C_BUFFER_WORDS = 55 * (1 << 16) + 3 * (1 << 19)

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


def table_group(width: int) -> int:
    if width <= 3:
        return 16
    if width == 4:
        return 24
    return (1 << width) + 8


def table_row_transform(layers: int, inverse: bool = False) -> int:
    total = 0
    level = 0
    for width in M.pass_widths(layers):
        blocks = 1 << (layers - width)
        groups = 1 << level
        group_zero_blocks = 1 << (layers - level - width)
        total += (
            blocks * M.block_body(width)
            + groups * table_group(width)
            + 9 * width + (38 if inverse else 37)
            - group_zero_blocks * ((1 << width) - 1)
            + 3
        )
        level += width
    return total


ALLOCATOR_CALL_PARTS = {
    "size_class_tests": 256,
    "free_list_tests": 128,
    "header_and_payload_updates": 128,
    "extent_and_live_updates": 96,
    "entry_exit_and_return": 47,
}
CLOSE_42_PARTS = {
    "entry_exit": 8,
    "length_tests": 8,
    "descriptor_updates": 12,
    "result_and_branch_updates": 14,
}
CLOSE_31_PARTS = {
    "entry_exit": 7,
    "length_tests": 6,
    "descriptor_updates": 8,
    "result_and_branch_updates": 10,
}
assert sum(ALLOCATOR_CALL_PARTS.values()) == 655
assert sum(CLOSE_42_PARTS.values()) == 42
assert sum(CLOSE_31_PARTS.values()) == 31


def stage_b() -> int:
    row = 1 << 28
    evaluations = 2 * STAGE_B_POINTS * STAGE_B_EVALUATION
    evaluation_loop = STAGE_B_POINTS * (
        2 + 1 + 1 + 2 + 2 + 3 + 11 * STAGE_B_INDEX_BITS + 2
    )
    inverse_transform = 8 * row + 3 * table_row_transform(28, inverse=True)
    table_build = (STAGE_B_POINTS // 2) * (5 + 3) + sum(CLOSE_42_PARTS.values())
    normalization = 512 * 5 + (ODD_DEGREE + 1) * 5 + loop8c(ODD_DEGREE + 1)
    allocations = (
        3 * sum(ALLOCATOR_CALL_PARTS.values()) + sum(CLOSE_31_PARTS.values())
    )
    return sum((evaluations, evaluation_loop, inverse_transform,
                table_build, normalization, allocations))


STAGE_B = stage_b()


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


BATCH_TOP = 128 * (60 + 20 + 16 * 5)
TOP_FUSED = 79 * (ORDER // 8) + BATCH_TOP
TOP_ONE = 48 * (ORDER // 8) + BATCH_TOP
TOP_HALF_POINT_ACTIONS = {
    "five_live_lane_loads": 5,
    "ten_live_butterflies_at_three": 10 * 3,
    "four_output_stores": 4,
    "four_pointer_updates": 4,
}


def top_half() -> int:
    first_batched_blocks = ((TRC + 15) // 16) * INNER
    straight_blocks = first_batched_blocks - 62
    assert straight_blocks >= 0
    return (
        sum(TOP_HALF_POINT_ACTIONS.values()) * (ORDER // 8)
        + straight_blocks
    )
RECOVERY = (
    INNER * sum(
        size * (8 * depth + 2)
        for size, depth in ((1, 11), (2, 10), (16, 7), (32, 6), (64, 5), (256, 3), (512, 2))
    )
    + 128 * 163
)
@dataclass(frozen=True)
class StageCKernelRows:
    middle: int
    bottom_blocks: int
    bottom_forward: int
    bottom_inverse: int
    forward: int
    inverse: int
    bottom_o1: int
    bottom_o2: int
    bottom_graeffe: int
    graeffe_step: int
    bit0: int
    bit1: int


def stage_c_kernel_rows(plan: SPLIT.StageCSplitPlan) -> StageCKernelRows:
    width = plan.bottom_width
    radix = 1 << width
    blocks, remainder = divmod(N1, radix)
    assert remainder == 0
    bodies = SPLIT.BOTTOM_BODY_ROWS
    assert width == bodies.width
    bottom_forward_body = bodies.by_name("bottom-forward").ordinary_operations
    bottom_inverse_body = bodies.by_name("bottom-inverse").ordinary_operations
    bottom_o1_body = bodies.by_name("bottom-o1").ordinary_operations
    bottom_o2_body = bodies.by_name("bottom-o2-zero").ordinary_operations
    bottom_o2_one_body = bodies.by_name("bottom-o2-one").ordinary_operations
    bottom_graeffe_body = bodies.by_name("bottom-graeffe").ordinary_operations
    bottom_forward = bottom_forward_body * blocks + KERNEL_FIXED
    bottom_inverse = bottom_inverse_body * blocks + KERNEL_FIXED
    forward = TOP_ONE + plan.middle_charge + bottom_forward
    inverse = TOP_ONE + plan.middle_charge + bottom_inverse + RECOVERY
    bottom_o1 = bottom_o1_body * blocks + KERNEL_FIXED
    bottom_o2 = bottom_o2_body * blocks + KERNEL_FIXED
    bottom_graeffe = bottom_graeffe_body * blocks + KERNEL_FIXED
    graeffe_step = (
        top_half() + 3 * plan.middle_charge + bottom_graeffe
        + TOP_ONE + RECOVERY + 2 * KERNEL_FIXED
    )
    bit0 = (
        bottom_o1 + 4 * plan.middle_charge + 2 * TOP_FUSED + bottom_o2
        + 4 * blocks + 2 * RECOVERY + KERNEL_FIXED
    )
    bit1 = bit0 + (bottom_o2_one_body - bottom_o2_body) * blocks
    return StageCKernelRows(
        plan.middle_charge, blocks, bottom_forward, bottom_inverse,
        forward, inverse, bottom_o1, bottom_o2, bottom_graeffe,
        graeffe_step, bit0, bit1,
    )


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


def stage_c_parts(depth: int, split_plan: SPLIT.StageCSplitPlan) -> dict[str, int]:
    kernels = stage_c_kernel_rows(split_plan)
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
        "graeffe": depth * kernels.graeffe_step + STAGE_EVENT_FRAME + GRAEFFE_EXTRA,
        "newton": newton,
        "quotient": quotient,
        "g_maps": 2 * kernels.forward + 4 * N1 + 2 * loop8c(N1) + STAGE_EVENT_FRAME,
        "A0_O2": (
            kernels.forward + 8 * N1 + loop8c(N1)
            + 5 * (N1 - ell) + loop8c(N1 - ell) + STAGE_EVENT_FRAME
        ),
        "A0_O1": kernels.inverse + kernels.forward + 6 * N1 + loop8c(N1) + STAGE_EVENT_FRAME,
        "k1": 15 * N1 + loop8c(N1) + chunks * BATCH_CHUNK_FIXED + STAGE_EVENT_FRAME,
        "squares": (226 - depth - 45) * kernels.bit0 + 45 * kernels.bit1,
        "exit": kernels.inverse + kernels.forward + 18 * N1 + 2 * loop8c(N1) + 4 * kernels.bottom_blocks + STAGE_EVENT_FRAME,
        "final_inverses": 2 * kernels.inverse + 4 * N1 + 2 * loop8c(N1) + 4 * kernels.bottom_blocks + STAGE_EVENT_FRAME,
        "bookkeeping": BOOKKEEPING,
    }


def stage_c(depth: int, split_plan: SPLIT.StageCSplitPlan) -> int:
    if not 0 <= depth <= 31:
        raise ValueError(depth)
    return sum(stage_c_parts(depth, split_plan).values())


def stage_c_middle_multiplicity(depth: int) -> int:
    powering_steps = 226 - depth
    return depth * 3 + 2 + 1 + 2 + powering_steps * 4 + 2 + 2


ROOT_LIFT_PARTS = {
    "fixed_square_and_multiply_field_events": 45_056,
    "two_adic_table_load_store_and_address_events": 1_280,
    "candidate_root_tests_and_selects": 512,
    "entry_exit_loop_and_descriptor_events": 164,
}
STAGE_F_CANDIDATE_PARTS = {
    "root_update": 1,
    "two_point_additions": 2,
    "two_line_evaluations": 2 * STAGE_B_EVALUATION,
    "four_call_boundaries": 4,
    "comparison_and_branch": 2,
    "loop_update_test_branch": 3,
}
assert sum(ROOT_LIFT_PARTS.values()) == 47_012
assert sum(STAGE_F_CANDIDATE_PARTS.values()) == 616


def stage_f(depth: int) -> int:
    return (
        (depth + 2) * sum(ROOT_LIFT_PARTS.values())
        + (1 << depth) * sum(STAGE_F_CANDIDATE_PARTS.values()) + 2
    )


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


R7_ALLOCATOR_CALL_ACTIONS = {
    "size_and_class_tests": 40,
    "free_list_and_extent_tests": 32,
    "header_and_payload_updates": 32,
    "live_extent_updates": 20,
    "entry_exit_and_return": 13,
}
assert sum(R7_ALLOCATOR_CALL_ACTIONS.values()) == 137


def r7_fixed_actions(name: str) -> int:
    rows = {
        "allocator_call": R7_ALLOCATOR_CALL_ACTIONS,
        "close_42": {
            "entry_exit": 8,
            "length_tests": 8,
            "descriptor_updates": 12,
            "result_and_branch_updates": 14,
        },
    }
    return sum(rows[name].values())


@cache
def apply_admissible_points(required: int) -> tuple[int, ...]:
    points = sorted(
        {1 << exponent for exponent in range(33)}
        | {3 * (1 << exponent) for exponent in range(32)}
    )
    return tuple(value for value in points if value >= required)


@cache
def apply_transform(points: int, inverse: bool = False) -> int:
    if points & (points - 1) == 0:
        return M.block_transform(points.bit_length() - 1, inverse=inverse)
    assert points % 3 == 0
    row = points // 3
    assert row & (row - 1) == 0
    layers = row.bit_length() - 1
    radix3 = 8 * row + M.loop8(row)
    return 3 * M.block_transform(layers, inverse=inverse) + radix3


@cache
def apply_plan(degree: int, level: int) -> APPLY.ApplyCharge:
    budget = (1 << level) - 1
    return APPLY.choose_apply_plan(
        degree, budget, apply_transform, apply_admissible_points, M.loop8,
        r7_fixed_actions,
    )


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
    apply_total = sum(apply_plan(degree, level).total for degree, level in steps)
    driver_total = sum(driver_step(degree, level) for degree, level in steps)
    current = ODD_DEGREE - sum(1 << level for _degree, level in steps)
    tail = classical_tail(current)
    return node_total + apply_total + driver_total + tail, node_total, apply_total, driver_total, tail


def block_bytes(words: int) -> int:
    return 64 + 64 * ((32 * words + 63) // 64)


LATE_SLAB_CLASSES = {
    128: 1,
    256: 3,
    1_024: 8,
    2_048: 1,
}
LATE_SLAB_BYTES = sum(size * slots for size, slots in LATE_SLAB_CLASSES.items())
LATE_SLAB_HEADS = len(LATE_SLAB_CLASSES) * 32
LATE_REGION_BYTES = LATE_SLAB_BYTES + LATE_SLAB_HEADS
BASE_CODE_STATIC_PARTS = {
    "seven_width_block_bodies": M.STRAIGHT_LINE_CODE_BYTES,
    "seven_width_column_bodies": 4 * 8 * sum((11, 20, 52, 128, 304, 704, 1_600)),
    "transform_drivers": 4 * (65_536 + 32_768 + 16_384 + 8_192),
    "field_arithmetic": 4 * (131_072 + 32_768),
    "poseidon_and_reference": 4 * 524_288,
    "allocator": 4 * 65_536,
    "polynomial_control": 4 * 196_608,
    "r10_apply_routines": 32_768,
    "static_tables": 212 * 32 + 8_192 + 32,
}


def code_static_parts(split_plan: SPLIT.StageCSplitPlan) -> dict[str, int]:
    return {
        **BASE_CODE_STATIC_PARTS,
        "selected_stage_c_split_routines": split_plan.code_bytes,
    }


def code_static_bytes(split_plan: SPLIT.StageCSplitPlan) -> int:
    return sum(code_static_parts(split_plan).values())
STACK_LIVE_BYTES = 36_864
STACK_BYTES = 1 << (STACK_LIVE_BYTES - 1).bit_length()
STACK_CHAIN_PARTS = {
    "thirty_two_half_gcd_frames": 32 * 32 * 32,
    "transform_scratch": 32 * 32,
    "field_and_poseidon_scratch": 32 * 32,
    "main_stage_allocator_and_saved_abi": 64 * 32,
}
assert sum(STACK_CHAIN_PARTS.values()) == STACK_LIVE_BYTES


@dataclass(frozen=True)
class ResidentEvent:
    number: int
    stage: str
    action: str
    name: str
    region: str
    bytes: int
    live_bytes: int


def allocator_events(
    cap: int, split_plan: SPLIT.StageCSplitPlan,
) -> tuple[list[ResidentEvent], int, int]:
    pair = block_bytes(N1)
    stage_c_table = block_bytes(30 + 1_165 + 4 * 4_096)
    stage_c_scratch = block_bytes(split_plan.buffer_words)
    events: list[ResidentEvent] = []
    stack: list[tuple[str, int]] = []
    live = 0

    selected_code_static = code_static_bytes(split_plan)
    fixed_resident = (
        selected_code_static + STACK_BYTES
        + M.REGISTER_BYTES + M.OFFLINE_WORKING_BYTES
        + 128 + LATE_REGION_BYTES
    )

    def record(stage: str, action: str, name: str,
               region: str, size: int, live_bytes: int) -> None:
        events.append(ResidentEvent(
            len(events) + 1, stage, action, name, region, size, live_bytes,
        ))

    running_fixed = 0
    for name, size in (
        ("code-and-static", selected_code_static),
        ("stack-reservation", STACK_BYTES),
        ("register-file", M.REGISTER_BYTES),
        ("offline-workspace", M.OFFLINE_WORKING_BYTES),
        ("arena-middle-gap", 128),
        ("slab-class-reservations", LATE_SLAB_BYTES),
        ("slab-free-list-heads", LATE_SLAB_HEADS),
    ):
        running_fixed += size
        record("fixed", "reserve", name, "fixed", size, running_fixed)
    assert running_fixed == fixed_resident

    def alloc(name: str, size: int) -> None:
        nonlocal live
        assert size > 0
        stack.append((name, size))
        live += size
        record(name.split()[0], "alloc", name, "pool", size,
               fixed_resident + live)

    def free(name: str) -> None:
        nonlocal live
        saved_name, size = stack.pop()
        assert saved_name == name
        live -= size
        record(name.split()[0], "free", name, "pool", size,
               fixed_resident + live)

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
        selected = apply_plan(degree, level)
        plan_arrays = selected.plan.allocation_arrays()
        assert len(plan_arrays) == (4 if selected.kind == "in-place" else 6)
        arena_name = f"D{step_index} apply arena"
        arena_words = sum(words for _suffix, words, _role in plan_arrays)
        alloc(arena_name, block_bytes(arena_words))
        free(arena_name)
        for index in range(4, 0, -1):
            free(f"D{step_index} matrix {index}")
    free("C table")
    free("C W1/R")
    free("B g result")
    assert live == 0 and not stack

    slab_live = 0
    slab_objects: list[tuple[str, int]] = []

    def slab_phase(stage: str, objects: tuple[tuple[str, int], ...]) -> None:
        nonlocal slab_live
        for name, size in objects:
            slab_objects.append((name, size))
            slab_live += size
            record(stage, "occupy", name, f"slab-{size}", size,
                   fixed_resident)
        for name, size in reversed(objects):
            saved_name, saved_size = slab_objects.pop()
            assert (saved_name, saved_size) == (name, size)
            slab_live -= size
            record(stage, "release", name, f"slab-{size}", size,
                   fixed_resident)

    slab_phase("E", (
        ("factor", 1_024), ("base", 1_024), ("power-result", 1_024),
        ("product-scratch", 2_048), ("P-minus-one", 1_024),
        ("P-plus-one", 1_024), ("gcd-left", 1_024),
        ("gcd-right", 1_024), ("selected-factor", 1_024),
        ("random-words", 128),
    ))
    slab_phase("F", (
        ("root-chain", 2_048), ("candidate-state", 1_024),
        ("input-pair", 256), ("line-state", 256),
    ))
    slab_phase("G", (
        ("two-input-pairs", 256), ("two-poseidon-states", 256),
        ("canonical-encodings", 256), ("output-elements", 128),
    ))
    assert not slab_objects and slab_live == 0

    stack_live = 0
    for name, size in STACK_CHAIN_PARTS.items():
        stack_live += size
        record("stack", "enter", name, "stack-live", size, fixed_resident)
    assert stack_live == STACK_LIVE_BYTES
    for name, size in reversed(tuple(STACK_CHAIN_PARTS.items())):
        stack_live -= size
        record("stack", "leave", name, "stack-live", size, fixed_resident)
    assert stack_live == 0

    footprint_peak = max(event.live_bytes for event in events)
    pool_peak = footprint_peak - fixed_resident
    return events, pool_peak, LATE_REGION_BYTES


def memory_bytes(
    cap: int, split_plan: SPLIT.StageCSplitPlan,
) -> tuple[int, int, tuple[ResidentEvent, ...]]:
    events, pool_peak, late_region = allocator_events(cap, split_plan)
    arena = pool_peak + 128 + late_region
    code_static = code_static_bytes(split_plan)
    footprint = arena + code_static + STACK_BYTES + M.REGISTER_BYTES + M.OFFLINE_WORKING_BYTES
    assert max(event.live_bytes for event in events) == footprint
    return footprint, arena, tuple(events)


@dataclass(frozen=True)
class Plan:
    split_plan: SPLIT.StageCSplitPlan
    split_candidate_count: int
    split_cap_row_count: int
    split_search_charge: int
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
    events: tuple[ResidentEvent, ...]

    @property
    def memory_bytes(self) -> int:
        return self.memory


def offline_components(selected_cap: int) -> dict[str, int]:
    """Charge every constructed and compared planner candidate exactly."""
    planner_steps = 2 * sum(
        len(outer_schedule(value)) for value in range(18, 29)
    ) + len(outer_schedule(selected_cap))
    return {
        "stage_c_split_candidates": SPLIT.preprocessing_charge(
            SPLIT.composition_count(21, 7), 11,
        ),
        "stage_d_geometry_candidates": planner_steps * (62 * 128 + 64),
        "node_recurrence_levels": 22 * 1_536,
        "stage_c_product_candidates": 29 * 62 * 256,
        "low_cap_screen_rows": len(outer_schedule(17)) * 32,
        "memory_total_and_exact_key_finalization": 11 * 512,
        "target_constant_derivation": TARGET_CONSTANT_DERIVATION,
        "planner_miscellaneous": PLANNER_MISC,
    }


def offline_charge(selected_cap: int) -> int:
    return sum(offline_components(selected_cap).values())


INIT_ACTIONS = {
    "201_target_constant_descriptors_at_eight_events": 201 * 8,
    "four_512_step_field_chains_at_five_events": 4 * 512 * 5,
    "table_address_and_storage_setup": 6_000,
    "entry_shape_tests_and_exit": 130,
}
SETUP_ACTIONS = {
    "three_512_step_field_chains": 3 * 512,
    "nine_256_word_descriptor_rows": 9 * 256,
    "target_specific_line_operations": 966,
    "entry_exit_and_shape_tests": 104,
}
STAGE_A_ACTIONS = {
    "fresh_field_draw": 63,
    "allocator_call": 655,
    "trial_descriptor_loop_test_and_update": 510,
}
STAGE_G_ACTIONS = {
    "verification_bookkeeping": 1_000,
    "ten_events_for_two_reference_hashes": 10 * 2 * COMPRESSION,
    "distinctness_encoding_and_exit": 32,
}
TRIAL_LOOP_ACTIONS = {
    "abort_allocator_reset": 1_000,
    "loop_update_test_and_branch": 12,
}
OUTPUT_ACTIONS = {
    "first_output_map_and_encoding": 1_572_864,
    "second_output_map_and_encoding": 1_572_864,
    "canonical_result_rows_and_exit": 244_352,
}


def runtime_plan_keys(
    selected_cap: int, split_plan: SPLIT.StageCSplitPlan,
) -> tuple[tuple[str, tuple[int, ...]], ...]:
    keys: set[tuple[str, tuple[int, ...]]] = {
        ("stage_b_transform", (STAGE_B_POINTS,)),
        ("stage_c_layout", (
            ORDER, N1, INNER, TRC, split_plan.top_width,
            *split_plan.middle_widths, split_plan.bottom_width,
        )),
    }
    ell = (1 << 27) + N1 - ODD_DEGREE + 1
    length = 1
    while length < ell:
        next_length = min(2 * length, ell)
        keys.add(("stage_c_product", (next_length, next_length)))
        length = next_length
    keys.add(("stage_c_product", (ell, ell)))
    for degree, level in outer_schedule(selected_cap):
        selected = apply_plan(degree, level)
        keys.add(("stage_d_apply", (
            degree, level, selected.points, selected.candidate_count,
        )))
    return tuple(sorted(keys))


def runtime_plan_cache_components(
    selected_cap: int, split_plan: SPLIT.StageCSplitPlan,
) -> tuple[int, tuple[tuple[str, tuple[int, ...], int], ...]]:
    rows = []
    for kind, values in runtime_plan_keys(selected_cap, split_plan):
        candidates = values[-1] if kind == "stage_d_apply" else 1
        charge = (
            18 + loop8c(len(values))
            + 27 * candidates + loop8c(candidates)
        )
        rows.append((kind, values, charge))
    return sum(row[2] for row in rows), tuple(rows)


def fixed_charge(selected_cap: int, split_plan: SPLIT.StageCSplitPlan) -> int:
    plan_cache, _rows = runtime_plan_cache_components(selected_cap, split_plan)
    return (
        sum(INIT_ACTIONS.values()) + sum(SETUP_ACTIONS.values())
        + plan_cache + sum(OUTPUT_ACTIONS.values())
    )


def build() -> Plan:
    node_rows = M.derive_nodes(28, two_row_product=True)
    nodes = {level: row.charged for level, row in node_rows.items()}
    other_trial = (
        sum(STAGE_A_ACTIONS.values()) + STAGE_B + E.stage_charge()
        + sum(STAGE_G_ACTIONS.values()) + sum(TRIAL_LOOP_ACTIONS.values())
    )
    drows = {cap: stage_d(cap, nodes) for cap in range(18, 29)}
    depth = 27
    f = stage_f(depth)
    split_count = SPLIT.composition_count(21, 7)
    split_cap_row_count = split_count * 11
    split_search_charge = SPLIT.preprocessing_charge(split_count, 11)
    memory_cache: dict[tuple[int, int, int], int] = {}
    fixed_cache: dict[tuple[int, int], int] = {}
    offline_by_cap = {cap: offline_charge(cap) for cap in range(18, 29)}
    calibration_plan = SPLIT.build_r7_plan(
        (4, 5, 6, 6), full_points=ORDER, live_points=N1,
        optimized_buffer_words=OPTIMIZED_STAGE_C_BUFFER_WORDS,
    )
    calibration_c = stage_c(depth, calibration_plan)
    middle_multiplicity = stage_c_middle_multiplicity(depth)
    best = None
    observed = 0
    exact_competitor_seen = False
    for split_plan in SPLIT.r7_candidates(
        full_points=ORDER,
        live_points=N1,
        optimized_buffer_words=OPTIMIZED_STAGE_C_BUFFER_WORDS,
    ):
        observed += 1
        exact_competitor_seen |= split_plan.middle_widths == (4, 5, 6, 6)
        c = calibration_c + middle_multiplicity * (
            split_plan.middle_charge - calibration_plan.middle_charge
        )
        for cap in range(18, 29):
            fixed_key = (cap, len(split_plan.middle_widths))
            if fixed_key not in fixed_cache:
                fixed_cache[fixed_key] = fixed_charge(cap, split_plan)
            fixed = fixed_cache[fixed_key]
            d = drows[cap][0]
            trial = other_trial + c + d + f
            offline = offline_by_cap[cap]
            n_max = fixed + trial + offline
            memory_key = (cap, split_plan.buffer_words, split_plan.code_bytes)
            if memory_key not in memory_cache:
                memory_cache[memory_key] = memory_bytes(cap, split_plan)[0]
            memory = memory_cache[memory_key]
            key = (
                n_max * memory, n_max, memory, split_plan.split, cap,
            )
            row = (
                key, split_plan, n_max, memory, depth, cap, c, d, f,
                trial, offline,
            )
            if best is None or row[0] < best[0]:
                best = row
    assert observed == split_count and exact_competitor_seen and best is not None
    (
        _key, split_plan, n_max, memory, depth, cap, c, d, f, trial, offline,
    ) = best
    fixed = fixed_charge(cap, split_plan)
    dparts = drows[cap]
    _memory, _arena, events = memory_bytes(cap, split_plan)
    raw_time = (Decimal(n_max).ln() - Decimal(COMPRESSION).ln()) / Decimal(2).ln()
    raw_memory = Decimal(memory).ln() / Decimal(2).ln()
    time_claim = ceil_decimal(raw_time, 5)
    memory_claim = ceil_decimal(raw_memory, 5)
    preprocessing = ceil_decimal(
        (Decimal(offline).ln() - Decimal(COMPRESSION).ln()) / Decimal(2).ln(), 5
    )
    score = time_claim + memory_claim - Decimal(20)
    # The direct program evaluates 4,897 stage-D steps once for the time row
    # and once for the allocator walk, then replays the selected 43-step walk.
    # One step tests 62 transform geometries.  The proof itemizes the 128-word-
    # operation geometry bound and the 64-operation schedule/accumulation bound.
    planner_steps = 2 * sum(len(outer_schedule(value)) for value in range(18, 29))
    planner_steps += len(outer_schedule(cap))
    planner_bound = offline_charge(cap)
    assert planner_steps == 9_837
    assert planner_bound == offline

    # Any cap below 18 refines cap 17's decrements.  Splitting a decrement
    # inserts another positive affine remainder in driver_step, so the cap-17
    # driver sum is a lower bound for every cap <= 17.  The stage-C peak is
    # unavoidable for every cap and supplies the common memory lower bound.
    low_driver = sum(driver_step(degree, level) for degree, level in outer_schedule(17))
    stage_c_stack_peak = (
        4 * block_bytes(N1) + block_bytes(30 + 1_165 + 4 * 4_096)
        + block_bytes(split_plan.buffer_words)
    )
    low_memory = (
        stage_c_stack_peak + 128 + LATE_REGION_BYTES
        + code_static_bytes(split_plan) + STACK_BYTES
        + M.REGISTER_BYTES + M.OFFLINE_WORKING_BYTES
    )
    low_n = (
        fixed_charge(17, split_plan) + other_trial + c + f
        + offline_charge(17) + low_driver
    )
    assert low_n * low_memory > n_max * memory
    return Plan(
        split_plan, split_count, split_cap_row_count, split_search_charge,
        depth, cap, c, d, f, trial, fixed, offline, n_max, memory,
        raw_time, raw_memory, time_claim, memory_claim, preprocessing, score,
        nodes, dparts[1], dparts[2], dparts[3], dparts[4], events,
    )


PLAN = build()
CODE_STATIC_PARTS = code_static_parts(PLAN.split_plan)
NON_BODY_AND_BODY_CODE_STATIC_BYTES = sum(CODE_STATIC_PARTS.values())
STAGE_INIT = sum(INIT_ACTIONS.values())
STAGE_SETUP = sum(SETUP_ACTIONS.values())
STAGE_A = sum(STAGE_A_ACTIONS.values())
STAGE_C_COMPONENTS = stage_c_parts(PLAN.depth, PLAN.split_plan)
STAGE_C = PLAN.stage_c
STAGE_D_COMPONENTS = {
    "node_rows": PLAN.node_total,
    "outer_applies": PLAN.apply_total,
    "drivers": PLAN.driver_total,
    "classical_tail": PLAN.tail,
}
STAGE_D = PLAN.stage_d
STAGE_E = E.stage_charge()
STAGE_F = PLAN.stage_f
STAGE_G = sum(STAGE_G_ACTIONS.values())
TRIAL_LOOP = sum(TRIAL_LOOP_ACTIONS.values())
PLAN_CACHE, PLANNER_ROWS = runtime_plan_cache_components(PLAN.cap, PLAN.split_plan)
OUTPUT = sum(OUTPUT_ACTIONS.values())
OFFLINE_CHARGE = PLAN.offline
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
    "plan_cache": PLAN_CACHE,
    "output": OUTPUT,
    "offline": OFFLINE_CHARGE,
}
N_MAX = sum(LEDGER.values())
MEMORY_BYTES = PLAN.memory
ARENA = (
    MEMORY_BYTES - NON_BODY_AND_BODY_CODE_STATIC_BYTES - STACK_BYTES
    - M.REGISTER_BYTES - M.OFFLINE_WORKING_BYTES
)
RAW_TIME = PLAN.raw_time
RAW_MEMORY = PLAN.raw_memory
TIME_CLAIM = PLAN.time_claim
MEMORY_CLAIM = PLAN.memory_claim
PREPROCESSING_CLAIM = PLAN.preprocessing_claim
SCORE = PLAN.score


def validate() -> None:
    assert KERNEL_FIXED == 20
    assert PRODUCT_INPUT_FRAME == 550 and PRODUCT_ARENA == 105
    assert PRODUCT_WRAPPER == 2_000 and STAGE_EVENT_FRAME == 20_000
    assert SETUP_EXTRA == 10_000 and GRAEFFE_EXTRA == 659
    assert BATCH_CHUNK_FIXED == 350 and BOOKKEEPING == 1_000
    assert PLAN_ENTRY == 400 and PATH_ENTRY == 100 and ROOT_ENTRY == 16
    assert DRIVER_FIXED == 4_454 and TAIL_NORMALIZE == 500 and TAIL_FRAME == 10_000
    assert STAGE_B == stage_b()
    assert STAGE_C == sum(STAGE_C_COMPONENTS.values())
    assert STAGE_D == sum(STAGE_D_COMPONENTS.values())
    assert STAGE_E == E.stage_charge() == 139_023_366
    assert PLAN.cap == 25 and PLAN.depth == 27
    assert PLAN_CACHE == sum(row[2] for row in PLANNER_ROWS)
    assert OFFLINE_CHARGE == sum(offline_components(PLAN.cap).values())
    assert PLAN.split_candidate_count == SPLIT.composition_count(21, 7)
    assert PLAN.split_search_charge == SPLIT.preprocessing_charge(
        PLAN.split_candidate_count, 11,
    )
    assert PLAN.split_cap_row_count == PLAN.split_candidate_count * 11
    assert PLAN.split_plan.middle_widths == (4, 5, 6, 6)
    kernels = stage_c_kernel_rows(PLAN.split_plan)
    manifest = {row.name: row for row in PLAN.split_plan.code_manifest}
    for body in SPLIT.BOTTOM_BODY_ROWS.families:
        code = manifest[body.name]
        assert code.ordinary_operations == body.ordinary_operations
        assert code.group_zero_operations == body.group_zero_operations
        assert code.copies == body.copies
        assert code.total_operations == body.emitted_operations
        assert code.emitted_bytes == body.emitted_bytes
    assert PLAN.split_plan.middle_charge == 24_882_343_356
    assert top_half() == 5_809_635_266
    assert TOP_FUSED == 10_603_220_992
    assert RECOVERY == 11_189_375_360
    assert kernels.bottom_o1 == 15_947_489_300
    assert kernels.bottom_o2 == 19_612_262_420
    assert kernels.bottom_graeffe == 22_675_783_700
    assert kernels.graeffe_step == 120_764_295_858
    assert kernels.bit0 == 178_712_492_588
    assert kernels.bit1 == 180_554_422_828
    assert N_MAX == PLAN.n_max
    assert MEMORY_BYTES == max(event.live_bytes for event in PLAN.events)
    assert SCORE == TIME_CLAIM + MEMORY_CLAIM - Decimal(20)


def main() -> None:
    plan = PLAN
    assert KERNEL_FIXED == 20
    assert PRODUCT_INPUT_FRAME == 550 and PRODUCT_ARENA == 105
    assert PRODUCT_WRAPPER == 2_000 and STAGE_EVENT_FRAME == 20_000
    assert SETUP_EXTRA == 10_000 and GRAEFFE_EXTRA == 659
    assert BATCH_CHUNK_FIXED == 350 and BOOKKEEPING == 1_000
    assert PLAN_ENTRY == 400 and PATH_ENTRY == 100 and ROOT_ENTRY == 16
    assert DRIVER_FIXED == 4_454 and TAIL_NORMALIZE == 500 and TAIL_FRAME == 10_000
    assert stage_c(27, PLAN.split_plan) == PLAN.stage_c
    assert not any("handed-off" in event.name for event in PLAN.events)
    assert block_bytes(N1) == 19_545_456_704
    assert NON_BODY_AND_BODY_CODE_STATIC_BYTES == sum(CODE_STATIC_PARTS.values())
    assert CODE_STATIC_PARTS["r10_apply_routines"] == 32_768
    assert STACK_BYTES == 65_536
    validate()
    print(plan)


if __name__ == "__main__":
    main()
```
### low_apply_plans.py

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
### r7_machine.py

```python
#!/usr/bin/env python3
"""Derived 392-register Poseidon kernel charges.

The formulas are transcribed from machine rules, not from another package's
score-bearing tables.  Round renderers provide geometry and call schedules.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import cache


FIELD_REGISTER_WORDS = 256
INTEGER_REGISTER_WORDS = 136
REGISTER_WORDS = FIELD_REGISTER_WORDS + INTEGER_REGISTER_WORDS
REGISTER_BYTES = REGISTER_WORDS * 32
OFFLINE_DERIVATION_BYTES = 576
SPLIT_PLANNER_RECORD_BYTES = 2 * 24 * 32
OFFLINE_WORKING_BYTES = max(OFFLINE_DERIVATION_BYTES, SPLIT_PLANNER_RECORD_BYTES)


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
NODE_FIXED_PARTS = NODE_FIXED_EVENTS
NODE_FIXED = sum(NODE_FIXED_EVENTS.values())
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
BASE_ENTRY_PARTS = BASE_ENTRY_ACTIONS
BASE_STEP_PARTS = BASE_STEP_SETUP_ACTIONS
BASE_STEP_EXIT = sum(BASE_STEP_CLOSE_ACTIONS.values())
BASE_FINAL_PARTS = BASE_FINAL_SETUP_ACTIONS
BASE_FINAL_EXIT = sum(BASE_FINAL_CLOSE_ACTIONS.values())


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
    return (1 << width) + 4


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
    # In the declared DIT loop, one chain belongs to a position j and is
    # reused across the 2^level blocks at that position.  There are
    # blocks_per_group = 2^(layers-level-width) positions.
    twiddles = (blocks if conservative else blocks_per_group) * twiddle_group(width)
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
    total = sum(BASE_ENTRY_ACTIONS.values())
    for step in range(0, 62, 2):
        length = 2 * (62 - step) + 1
        total += (
            sum(BASE_STEP_SETUP_ACTIONS.values())
            + sum(BASE_REMAINDER_COEFFICIENT_ACTIONS.values()) * length
            + sum(BASE_MATRIX_COEFFICIENT_ACTIONS.values()) * (length - 2)
            + linear_control(length)
            + 2
            * (
                sum(BASE_REMAINDER_COEFFICIENT_ACTIONS.values()) * (step + 2)
                + sum(BASE_MATRIX_COEFFICIENT_ACTIONS.values()) * (step + 3)
                + linear_control(step + 3)
            )
            + sum(BASE_STEP_CLOSE_ACTIONS.values())
        )
    total += (
        sum(BASE_FINAL_SETUP_ACTIONS.values())
        + sum(BASE_REMAINDER_COEFFICIENT_ACTIONS.values()) + linear_control(1)
        + 2 * (sum(BASE_REMAINDER_COEFFICIENT_ACTIONS.values()) * 64
               + linear_control(64))
        + sum(BASE_FINAL_CLOSE_ACTIONS.values())
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
        forward = block_transform(layers)
        inverse_transform = block_transform(layers, inverse=True)

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


def main() -> None:
    assert REGISTER_BYTES == 12_544
    assert OFFLINE_WORKING_BYTES == 1_536
    assert STRAIGHT_LINE_CODE_BYTES == 907_520
    assert NODE_FIXED == 210 and NODE_ARENA_CONTROL == 10
    assert sum(BASE_ENTRY_PARTS.values()) == 90
    assert sum(BASE_STEP_PARTS.values()) == 76
    assert sum(BASE_FINAL_PARTS.values()) == 25
    assert base_case_raw() == 105_140
    assert loop8(0) == 5 and loop8(8) == 8 and loop8(15) == 29
    nodes = derive_nodes(26, two_row_product=True)
    print("register_bytes", REGISTER_BYTES)
    print("node_bf", {level: row.charged for level, row in nodes.items()})


if __name__ == "__main__":
    main()
```
### stage_e_core.py

```python
#!/usr/bin/env python3
"""Generated constant-work Stage-E isolation charge shared by round ledgers."""

from __future__ import annotations


PALLAS_P = 0x40000000000000000000000000000000224698FC094CF91B992D30ED00000001

MODULAR_PAIR_ACTIONS = {
    "convolution_load_store_and_field": 6,
    "convolution_loop_control": 3,
    "reduction_load_store_and_field": 6,
    "reduction_loop_control": 3,
    "coefficient_address_updates": 4,
}
MODULAR_ROW_ACTIONS = {
    "output_zero_and_loop": 4,
    "convolution_row_pointers": 4,
    "reduction_leading_load_test": 3,
    "modulus_row_pointers": 4,
    "normalization_and_carry": 5,
}
MODULAR_FIXED_ACTIONS = {
    "entry_exit": 8,
    "array_descriptors": 16,
    "degree_and_bounds": 8,
    "buffer_swaps": 8,
    "final_tests": 8,
    "call_frames": 16,
}
POWER_COPY_ACTIONS = {
    "source_load": 1,
    "destination_store": 1,
    "source_and_destination_updates": 2,
    "loop_update_test_branch": 3,
}
POWER_FIXED_ACTIONS = {
    "entry_exit": 4,
    "buffer_swap": 4,
    "length_and_degree_tests": 8,
    "source_and_destination_descriptors": 8,
    "exponent_bit_test_and_branch": 4,
    "call_and_return": 3,
}
GCD_CELL_ACTIONS = {
    "active_mask_and_degree_test": 2,
    "coefficient_loads": 3,
    "field_multiply": 1,
    "field_subtract": 1,
    "coefficient_store": 1,
    "loop_update_test_branch": 3,
    "address_update": 1,
}
ALLOCATOR_CALL_ACTIONS = {
    "size_class_tests": 256,
    "free_list_tests": 128,
    "header_and_payload_updates": 128,
    "extent_and_live_updates": 96,
    "entry_exit_and_return": 47,
}
assert sum(ALLOCATOR_CALL_ACTIONS.values()) == 655
OUTER_ACTIONS = {
    "two_allocator_calls": 2 * sum(ALLOCATOR_CALL_ACTIONS.values()),
    "trial_and_stage_descriptors": 256,
    "scalar_tracking": 256,
    "abort_tests": 128,
    "result_pointers": 128,
    "entry_exit": 232,
}


def round_components(degree: int = 16) -> dict[str, int]:
    """Charge the written constant-work split pseudocode.

    Draw a fresh shift; evaluate H(-a); initialize X+a; compute
    (X+a)^((p-1)/2) mod H by square-and-multiply; form P-1 and P+1;
    run two padded Euclidean gcds; select and copy one proper factor.
    """
    exponent = (PALLAS_P - 1) // 2
    squarings = exponent.bit_length() - 1
    multiplies = exponent.bit_count() - 1
    assert (squarings, multiplies) == (253, 45)
    coefficients = degree + 1
    modular_product = (
        coefficients * coefficients * sum(MODULAR_PAIR_ACTIONS.values())
        + coefficients * sum(MODULAR_ROW_ACTIONS.values())
        + sum(MODULAR_FIXED_ACTIONS.values())
    )
    power_step = (
        modular_product
        + coefficients * sum(POWER_COPY_ACTIONS.values())
        + sum(POWER_FIXED_ACTIONS.values())
    )
    one_gcd = (
        degree * coefficients * coefficients * sum(GCD_CELL_ACTIONS.values())
        + 18 * coefficients + 80
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


def round_charge(degree: int = 16) -> int:
    return sum(round_components(degree).values())


def stage_charge(rounds: int = 64, degree: int = 16) -> int:
    return rounds * round_charge(degree) + sum(OUTER_ACTIONS.values())


assert round_charge() == 2_172_204
assert stage_charge() == 139_023_366
```
### stage_c_split_search.py

```python
#!/usr/bin/env python3
"""Generated Stage-C split search for the low-round Poseidon ledgers.

This module contains no score-bearing totals.  It enumerates compositions,
derives every pass from primitive block and running-chain actions, derives the
buffer selected by the execution schedule, and emits the preprocessing charge
for every constructed and compared candidate.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator


FIELD_REGISTER_WORDS = 256
INTEGER_REGISTER_WORDS = 136
WORD_BYTES = 32
INSTRUCTION_BYTES = 4
UNROLLED_CODE_COPIES = 3

PLAN_CONSTRUCTION_ACTIONS = {
    "geometry_and_layer_updates": 96,
    "row_descriptor_construction": 128,
    "pass_schedule_construction": 128,
    "register_and_memory_validation": 48,
}
PLAN_COMPARISON_ACTIONS = {
    "five_key_field_load_pairs": 20,
    "five_ordered_key_comparisons": 20,
    "five_comparison_branches": 20,
    "selected_record_updates": 16,
}
CAP_ROW_CONSTRUCTION_ACTIONS = {
    "cap_geometry_and_schedule": 48,
    "stage_row_assembly": 64,
    "memory_trace_and_key_fields": 40,
    "score_product_and_tuple_store": 40,
}


def compositions(total: int, maximum: int) -> Iterator[tuple[int, ...]]:
    """Yield every ordered positive composition of total with bounded parts."""
    if total == 0:
        yield ()
        return
    for width in range(1, min(total, maximum) + 1):
        for suffix in compositions(total - width, maximum):
            yield (width,) + suffix


def composition_count(total: int, maximum: int) -> int:
    counts = [0] * (total + 1)
    counts[0] = 1
    for subtotal in range(1, total + 1):
        counts[subtotal] = sum(
            counts[subtotal - width]
            for width in range(1, min(subtotal, maximum) + 1)
        )
    return counts[total]


def block_body(width: int) -> int:
    """Loads, stores, butterflies, and four-block loop/pointer control."""
    radix = 1 << width
    return 2 * radix + 3 * width * (radix // 2) + 3


def running_chain(width: int) -> int:
    """Root advance, twiddle chain, and its five control actions."""
    return (1 << width) + 4


def middle_pass(points: int, width: int) -> tuple[int, int, int]:
    """Return charge, block count, and four-block shared-chain count."""
    radix = 1 << width
    blocks, remainder = divmod(points, radix)
    if remainder or blocks % 4:
        raise ValueError((points, width, blocks, remainder))
    chains = blocks // 4
    fixed = 159 * width + 19
    charge = blocks * block_body(width) + chains * running_chain(width) + fixed
    return charge, blocks, chains


def middle_set(points: int, widths: tuple[int, ...]) -> int:
    return sum(middle_pass(points, width)[0] for width in widths)


def field_register_requirement(width: int) -> int:
    """One radix block, all nontrivial twiddles, and one temporary."""
    return (1 << width) + ((1 << width) - 1) + 1


def integer_register_requirement(width: int) -> int:
    """Row bases plus the seven live addresses and loop fields."""
    return (1 << width) + 7


def fused_graeffe_field_register_requirement(bottom_width: int) -> int:
    """Both E/O blocks, their shared twiddles, and one temporary."""
    radix = 1 << bottom_width
    return 2 * radix + (radix - 1) + 1


@dataclass(frozen=True)
class MiddlePassRow:
    width: int
    cumulative_offset: int
    execution: str
    blocks: int
    chains: int
    block_operations: int
    chain_operations: int
    fixed_operations: int
    fallback_operations: int

    @property
    def total(self) -> int:
        return (
            self.blocks * self.block_operations
            + self.chains * self.chain_operations
            + self.fixed_operations
            + self.fallback_operations
        )


@dataclass(frozen=True)
class CodeFamily:
    name: str
    ordinary_operations: int
    group_zero_operations: int
    copies: int

    @property
    def total_operations(self) -> int:
        return self.copies * (
            self.ordinary_operations + self.group_zero_operations
        )

    @property
    def emitted_bytes(self) -> int:
        return self.total_operations * INSTRUCTION_BYTES


@dataclass(frozen=True)
class BottomBodyFamily:
    name: str
    actions: tuple[tuple[str, int], ...]
    twiddle_directions: int
    copies: int
    radix: int

    @property
    def ordinary_operations(self) -> int:
        assert self.actions and len({name for name, _value in self.actions}) == len(self.actions)
        assert all(value >= 0 for _name, value in self.actions)
        return sum(value for _name, value in self.actions)

    @property
    def group_zero_operations(self) -> int:
        return self.ordinary_operations - self.twiddle_directions * (
            self.radix - 1
        )

    @property
    def emitted_operations(self) -> int:
        return self.copies * (
            self.ordinary_operations + self.group_zero_operations
        )

    @property
    def emitted_bytes(self) -> int:
        return self.emitted_operations * INSTRUCTION_BYTES


@dataclass(frozen=True)
class BottomBodyRows:
    width: int
    families: tuple[BottomBodyFamily, ...]

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(row.name for row in self.families)

    def by_name(self, name: str) -> BottomBodyFamily:
        rows = tuple(row for row in self.families if row.name == name)
        if len(rows) != 1:
            raise KeyError(name)
        return rows[0]


def build_bottom_body_rows(width: int) -> BottomBodyRows:
    """Build the atomic bodies used by runtime charging and emitted code."""
    radix = 1 << width
    butterflies = 3 * width * (radix // 2)
    twiddle_chain = radix + 3
    inverse_diagonal = radix + 1
    block_control = 3

    def family(
        name: str, actions: tuple[tuple[str, int], ...], directions: int,
    ) -> BottomBodyFamily:
        return BottomBodyFamily(
            name=name,
            actions=actions,
            twiddle_directions=directions,
            copies=UNROLLED_CODE_COPIES,
            radix=radix,
        )

    rows = (
        family("bottom-forward", (
            ("input_loads", radix),
            ("output_stores", radix),
            ("bottom_butterflies", butterflies),
            ("block_pointer_and_four_block_control", block_control),
            ("shared_twiddle_chain", twiddle_chain),
        ), 1),
        family("bottom-inverse", (
            ("input_loads", radix),
            ("output_stores", radix),
            ("bottom_butterflies", butterflies),
            ("block_pointer_and_four_block_control", block_control),
            ("shared_twiddle_chain", twiddle_chain),
            ("inverse_diagonal", inverse_diagonal),
        ), 1),
        family("bottom-o1", (
            ("two_bottom_butterfly_directions", 2 * butterflies),
            ("input_loads_and_result_stores", 2 * radix),
            ("four_pointwise_actions", 4 * radix),
            ("shared_twiddle_chain", twiddle_chain),
            ("inverse_diagonal", inverse_diagonal),
            ("block_pointer_and_four_block_control", block_control),
        ), 2),
        family("bottom-o2-zero", (
            ("two_bottom_butterfly_directions", 2 * butterflies),
            ("input_loads_and_result_stores", 2 * radix),
            ("ten_pointwise_actions", 10 * radix),
            ("shared_twiddle_chain", twiddle_chain),
            ("inverse_diagonal", inverse_diagonal),
            ("block_pointer_and_four_block_control", block_control),
        ), 2),
        family("bottom-o2-one", (
            ("two_bottom_butterfly_directions", 2 * butterflies),
            ("input_loads_and_result_stores", 2 * radix),
            ("ten_pointwise_actions", 10 * radix),
            ("bit_one_point_actions", 3 * radix),
            ("shared_twiddle_chain", twiddle_chain),
            ("inverse_diagonal", inverse_diagonal),
            ("block_pointer_and_four_block_control", block_control),
            ("bit_one_point_pointer_update", 1),
        ), 2),
        family("bottom-graeffe", (
            ("three_bottom_butterfly_directions", 3 * butterflies),
            ("three_input_output_streams", 3 * radix),
            ("five_pointwise_actions", 5 * radix),
            ("shared_twiddle_chain", twiddle_chain),
            ("inverse_diagonal", inverse_diagonal),
            ("block_pointer_and_control", 4),
        ), 3),
    )
    result = BottomBodyRows(width=width, families=rows)
    assert len(set(result.names)) == len(result.families)
    return result


BOTTOM_BODY_ROWS = build_bottom_body_rows(6)


@dataclass(frozen=True)
class StageCSplitPlan:
    top_width: int
    middle_widths: tuple[int, ...]
    bottom_width: int
    middle_charge: int
    buffer_words: int
    pass_rows: tuple[MiddlePassRow, ...]
    fallback_operations: int
    code_manifest: tuple[CodeFamily, ...]
    field_registers: int
    integer_registers: int

    @property
    def split(self) -> tuple[int, ...]:
        return (self.top_width, *self.middle_widths, self.bottom_width)

    @property
    def code_operations(self) -> int:
        return sum(row.total_operations for row in self.code_manifest)

    @property
    def code_bytes(self) -> int:
        return sum(row.emitted_bytes for row in self.code_manifest)


def emitted_code_manifest(
    widths: tuple[int, ...], bottom_width: int,
) -> tuple[CodeFamily, ...]:
    """Named ordinary/group-zero straight-line families, three copies each."""
    rows = []
    for width in sorted(set(widths)):
        ordinary = block_body(width)
        rows.append(CodeFamily(
            f"middle-width-{width}", ordinary,
            ordinary - ((1 << width) - 1), UNROLLED_CODE_COPIES,
        ))
    if bottom_width != BOTTOM_BODY_ROWS.width:
        raise ValueError(bottom_width)
    for body in BOTTOM_BODY_ROWS.families:
        code = CodeFamily(
            body.name,
            body.ordinary_operations,
            body.group_zero_operations,
            body.copies,
        )
        assert code.total_operations == body.emitted_operations
        assert code.emitted_bytes == body.emitted_bytes
        rows.append(code)
    return tuple(rows)


def loop8(count: int) -> int:
    if count < 0:
        raise ValueError(count)
    return 1 + 3 * (count // 8) + 2 + 3 * (count % 8) + 2


def calibration_fallback_operations(
    *, batches: int, batch_classes: int, live_nodes: int, tail_nodes: int,
) -> int:
    """One-bit node/inner boundary fallback of the width-five pass.

    Each batch executes eight inner ranges with five controls for every class,
    ten boundary actions for each non-tail live node, and six entry/exit
    actions.  The three tail nodes use the resident tail path instead.
    """
    return batches * (
        8 * 5 * batch_classes + 10 * (live_nodes - tail_nodes) + 6
    )


def calibrated_r7_pass_rows(
    *, live_nodes: int, inner: int,
) -> tuple[MiddlePassRow, ...]:
    widths = (4, 5, 6, 6)
    batches = 128
    batch_classes = 1 << 16
    tail_nodes = 3
    rows = []
    first_blocks = ((live_nodes + 15) // 16) * inner
    rows.append(MiddlePassRow(
        4, 0, "class-batched-first-pass", first_blocks, batches * 8,
        block_body(4), running_chain(4), batches * (20 + 3), 0,
    ))
    cumulative = 4
    for index, width in enumerate(widths[1:], 1):
        blocks = live_nodes * inner // (1 << width)
        remaining_middle = sum(widths[index + 1:])
        chains = live_nodes * (1 << remaining_middle)
        fallback = (
            calibration_fallback_operations(
                batches=batches,
                batch_classes=batch_classes,
                live_nodes=live_nodes,
                tail_nodes=tail_nodes,
            )
            if index == 1 else 0
        )
        rows.append(MiddlePassRow(
            width, cumulative, "live-node-position-shared",
            blocks, chains, block_body(width), running_chain(width),
            159 * width + 19, fallback,
        ))
        cumulative += width
    assert cumulative == 21
    return tuple(rows)


def full_fallback_pass_rows(
    widths: tuple[int, ...], *, full_points: int, live_points: int,
    top_width: int, bottom_width: int,
) -> tuple[MiddlePassRow, ...]:
    """Executable full omitted-position fallback for every other split."""
    rows = []
    cumulative = 0
    zero_fill = 5 * (full_points - live_points) + loop8(full_points - live_points)
    total_layers = top_width + sum(widths) + bottom_width
    for index, width in enumerate(widths):
        global_level = top_width + cumulative
        blocks = full_points // (1 << width)
        chains = 1 << (total_layers - global_level - width)
        rows.append(MiddlePassRow(
            width, cumulative, "full-omitted-position-fallback",
            blocks, chains, block_body(width), running_chain(width),
            159 * width + 19,
            zero_fill if index == 0 else 0,
        ))
        cumulative += width
    return tuple(rows)


def r7_buffer_words(
    middle_widths: tuple[int, ...], *, full_points: int, live_points: int,
    optimized_words: int,
) -> int:
    """Buffer for the declared r7 execution schedule.

    The reviewed class-batched walk covers layers 1 through 7, hence exactly
    a first four-layer middle pass after the three-layer top.  Other first
    widths remain legal candidates but use the complete omitted-position
    scratch.  This conservative fallback is an actual schedule, not an
    estimate, and makes every enumerated candidate executable.
    """
    if middle_widths == (4, 5, 6, 6):
        return optimized_words
    return full_points - live_points


def build_r7_plan(
    middle_widths: tuple[int, ...], *, full_points: int, live_points: int,
    optimized_buffer_words: int,
) -> StageCSplitPlan:
    top_width = 3
    bottom_width = 6
    if sum(middle_widths) != 21 or not middle_widths:
        raise ValueError(middle_widths)
    if any(not 1 <= width <= 7 for width in middle_widths):
        raise ValueError(middle_widths)
    field_words = max(
        [field_register_requirement(width) for width in middle_widths]
        + [fused_graeffe_field_register_requirement(bottom_width)]
    )
    integer_words = max(
        [integer_register_requirement(width) for width in middle_widths]
        + [integer_register_requirement(bottom_width)]
    )
    if field_words > FIELD_REGISTER_WORDS or integer_words > INTEGER_REGISTER_WORDS:
        raise ValueError((middle_widths, field_words, integer_words))
    if middle_widths == (4, 5, 6, 6):
        inner = live_points // 1_165
        pass_rows = calibrated_r7_pass_rows(live_nodes=1_165, inner=inner)
    else:
        pass_rows = full_fallback_pass_rows(
            middle_widths, full_points=full_points, live_points=live_points,
            top_width=top_width, bottom_width=bottom_width,
        )
    middle_charge = sum(row.total for row in pass_rows)
    fallback_operations = sum(row.fallback_operations for row in pass_rows)
    code_manifest = emitted_code_manifest(middle_widths, bottom_width)
    return StageCSplitPlan(
        top_width=top_width,
        middle_widths=middle_widths,
        bottom_width=bottom_width,
        middle_charge=middle_charge,
        buffer_words=r7_buffer_words(
            middle_widths, full_points=full_points, live_points=live_points,
            optimized_words=optimized_buffer_words,
        ),
        pass_rows=pass_rows,
        fallback_operations=fallback_operations,
        code_manifest=code_manifest,
        field_registers=field_words,
        integer_registers=integer_words,
    )


def r7_candidates(
    *, full_points: int, live_points: int, optimized_buffer_words: int,
) -> Iterator[StageCSplitPlan]:
    calibration = build_r7_plan(
        (4, 5, 6, 6), full_points=full_points,
        live_points=live_points,
        optimized_buffer_words=optimized_buffer_words,
    )
    assert calibration.middle_charge == 24_882_343_356
    assert calibration.fallback_operations == 337_032_448
    assert tuple(row.width for row in calibration.pass_rows) == (4, 5, 6, 6)
    for widths in compositions(21, 7):
        plan = build_r7_plan(
            widths, full_points=full_points, live_points=live_points,
            optimized_buffer_words=optimized_buffer_words,
        )
        if widths == calibration.middle_widths:
            assert plan == calibration
        yield plan


def build_r5_plan(
    middle_widths: tuple[int, ...], *, live_points: int, buffer_words: int,
) -> StageCSplitPlan:
    top_width = 3
    bottom_width = 6
    if sum(middle_widths) != 16 or not middle_widths:
        raise ValueError(middle_widths)
    if any(not 1 <= width <= 6 for width in middle_widths):
        raise ValueError(middle_widths)
    field_words = max(
        [field_register_requirement(width) for width in middle_widths]
        + [fused_graeffe_field_register_requirement(bottom_width)]
    )
    integer_words = max(
        [integer_register_requirement(width) for width in middle_widths]
        + [integer_register_requirement(bottom_width)]
    )
    if field_words > FIELD_REGISTER_WORDS or integer_words > INTEGER_REGISTER_WORDS:
        raise ValueError((middle_widths, field_words, integer_words))
    pass_rows = tuple(
        MiddlePassRow(
            width, sum(middle_widths[:index]), "four-block-shared",
            live_points // (1 << width),
            (live_points // (1 << width)) // 4,
            block_body(width), running_chain(width), 159 * width + 19, 0,
        )
        for index, width in enumerate(middle_widths)
    )
    return StageCSplitPlan(
        top_width=top_width,
        middle_widths=middle_widths,
        bottom_width=bottom_width,
        middle_charge=sum(row.total for row in pass_rows),
        buffer_words=buffer_words,
        pass_rows=pass_rows,
        fallback_operations=0,
        code_manifest=emitted_code_manifest(middle_widths, bottom_width),
        field_registers=field_words,
        integer_registers=integer_words,
    )


def r5_candidates(
    *, live_points: int, buffer_words: int,
) -> Iterator[StageCSplitPlan]:
    for widths in compositions(16, 6):
        yield build_r5_plan(
            widths, live_points=live_points, buffer_words=buffer_words,
        )


def preprocessing_charge(candidate_count: int, cap_count: int = 1) -> int:
    if candidate_count < 1 or cap_count < 1:
        raise ValueError((candidate_count, cap_count))
    cap_rows = candidate_count * cap_count
    split_construction = (
        candidate_count * sum(PLAN_CONSTRUCTION_ACTIONS.values())
    )
    cap_row_construction = (
        cap_rows * sum(CAP_ROW_CONSTRUCTION_ACTIONS.values())
    )
    comparisons = (
        (cap_rows - 1) * sum(PLAN_COMPARISON_ACTIONS.values())
    )
    return split_construction + cap_row_construction + comparisons


def main() -> None:
    plans = list(r7_candidates(
        full_points=1 << 30,
        live_points=1165 * (1 << 19),
        optimized_buffer_words=55 * (1 << 16) + 3 * (1 << 19),
    ))
    exact = build_r7_plan(
        (4, 5, 6, 6), full_points=1 << 30,
        live_points=1165 * (1 << 19),
        optimized_buffer_words=55 * (1 << 16) + 3 * (1 << 19),
    )
    assert len(plans) == composition_count(21, 7)
    print("candidates", len(plans))
    print("competitor_split", exact)
    print("preprocessing", preprocessing_charge(len(plans), 11))


if __name__ == "__main__":
    main()
```
