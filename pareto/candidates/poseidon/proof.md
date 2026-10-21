# Orchard Poseidon, r = 21: algebraic collision algorithm (the r = 21 instantiation of the algorithm of the r = 22 entry 1253b348), with a self-contained conservative operation count

## 1. Claim

Target: `poseidon-orchard-r21-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, twenty-one partial rounds 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23 and 24, full rounds 60-63, state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

The algorithm is that of the live r = 22 entry `1253b348` (time + memory penalty 123.85495), instantiated at r = 21: an algorithm with a worst-case operation count (sections 4, 6) and a success probability derived from the premises `H-ONE` (9.1) and `H-NORMAL` (9.5). All credits: the two-round bypass is Bariant, Bouvier, Leurent and Perrin (ToSC 2022(3)); stage C is the value-domain powering of bradcush `1aa56884`; stage D the lean half-gcd of `1aa56884` with the product forms of weijiekoh `a78f526e`, the inversion-free node of bradcush `4bcabff8` and the normal-sequence charging of bradcush `e6dcb600`; the kernel charges of 4.2 and the node charges of 4.5 are the published tables of `1253b348` sections 4.2 and 4.4.3; the premise structure with `delta = 0.003` and the organizer-run tests follow `e6dcb600` and gta6rp `fe269c23`. This entry contributes: the r = 21 parameters and literals (sections 2-3, computed here and cross-checked against the r = 22 published ones), and a complete self-contained conservative operation count (sections 4, 6, 7) with its own charging rules, every one an upper bound on the work of the same algorithm at the published granularity or coarser.

* The algorithm (one centre): draw a centre `c` uniformly from `F_p` from fresh random words, build the odd part `g_c` of the line polynomial by evaluation and 578241159 inverse transforms (one per coset, section 3), compute `G = gcd(g_c, S^((p-1)/2) - 1)` by a power-mod in the value domain (section 4.4, the method of `1aa56884`) and a half-gcd in the lean form with aligned budgets, the scaled division and the product forms of `a78f526e`, with every matrix-only call of budget `2^j - 1` (`7 <= j <= 31`) run on the inversion-free node of `4bcabff8` at its published charge (4.5), and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` in at most `Z = 64` rounds, take its square root, map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`); a verified collision ends the algorithm.
* `success_probability = 0.39009`: a lower bound for the probability, over the algorithm's fresh random words, that the one centre yields a verified collision on the fixed target: `P >= q - delta - delta_C - eps_iso - eps_coin` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, 9.1), `delta = 0.003` (the premise `H-NORMAL`, 9.5), `delta_C < 2^-129` (the stage-C zero test, proved, 9.2(b)), `eps_iso <= 2.371e-15 < 2^-48` (the isolation lemma 9.4, proved), `eps_coin < 2^-122` (4.1.1). The exact value is `0.3900999999999976`. The premises are the same statements as `1253b348` at r = 22 with `D = 5^27` in place of `5^28`; the evidence structure (the theorem at the first layers, the toy-field measurements, the organizer-run normality tests) is layer-count independent below the partial-round count and is restated in 9.3, 9.5 and 10.
* `time_log2 = 71.38566` in target-compression units (`C(21) = 657` primitive operations per unit): the worst-case operation count of section 6, `N_max = 2,026,698,719,619,100,596,805,386` operations, `log2(N_max / 657) = 71.385657`, rounded up at five decimals. The offline derivation of the constants is charged at its declared cap of 1,000,000 operations (`preprocessing_log2 = 20`), inside `N_max`.
* `memory_log2_bytes = 68.715` (`484,288,128,844,857,167,340` bytes, section 7).
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent; at most 65 words (4.1.1), a draw costs 31 operations. No advice (`nonuniform_advice_log2_bytes = 0`).
* The count of this entry is deliberately coarser than the per-operation count of `1253b348`: every charging rule of 4.2 below is either that entry's published table applied verbatim, or a provably larger charge for the same work (a pass at the model's full per-layer price instead of the register-blocked kernels, a >4x multiplier over an itemized per-coefficient estimate for the block products, a 6x multiplier over an exact node charge for the complement of the stage-D recursion). Section 6.2 validates the counting program of this entry against the published r = 22 ledger: on the same algorithm at r = 22 it yields between 1.000 and 2.021 times the published rows (and the stage-D node charge to six significant digits), so the r = 21 figures sit between the reference count and a 2.1x margin above it.

## 2. Two free rounds: a line in the input plane

Notation as in `1253b348` section 2. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `x -> x^5` is a bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5`. `M` is the deployed 3x3 MDS, `c_{i,k}` the deployed round constant `k` of round `i` (from the organizer's pinned table; never regenerated).

2.1 Rounds 0 and 1 are the same maps at every round count (the first two full rounds are rounds 0 and 1 at r = 21 as at r = 22). With `I = {1, 2}` and `j = 0`, the line is `(U, V) = Q + tau (a, b)` with `(a, b) = (M_{0,1}, -M_{0,0})`, on the deployed constants

* `Q = (0x2de17246e844b000296eefaaf2116b9705e3af63806d80541c7d6b4be442036c, 0x2622542e119aef1f7c021664aae329063a3e73651cd62e02756427f9437fdd96)`,
* `kappa = 0x2a78890d8503b228bfa6bd9b312401c7af4e02a6376ceebb003ef1138f67c72c`, `d_1 = 0x2b1cf2a34b2b6723837c31d51d5c91d12d1a715784a437124e3daf150a8d2b15`, `d_2 = 0x194af15c17a9f125b198b4fcacb6f6a0d7525c1960573b90b20d8c6a16f61d57`,
* `beta = (0x23c27f31affe3355705c3436661672f812bf595c8c693caf2632952857b4f542, 0xbf0a531e547aaee0a858122cd51bf61d3410fbc8972013ce3666a6f47a5b802, 0x3b86955a87b71c2631869b9fb992631c4a32ee6dea0ad3a8fc3e1f12f348c40a)`,

and the 2x2 minor `M_{1,0} M_{2,1} - M_{1,1} M_{2,0}` is nonzero (checked). These literals are independent of r (rounds 0 and 1 only) and equal those of `1253b348`.

2.2 Digest polynomial. Rounds 2, 3 (full) and the partial rounds 4, ..., 24 (twenty-one of them), then the full rounds 60, 61, 62, 63 put twenty-seven S-box layers on top of the affine map `alpha + beta W`, and the digest equals `F(W)` with `deg F <= 5^27 = D = 7,450,580,596,923,828,125`. The leading coefficient is propagated through the twenty-seven layers exactly (per layer, coordinate k takes the fifth power of its leading coefficient; the MDS row sums the leading coefficients of the coordinates of maximal degree; a partial round contributes only coordinate 0 at the top degree). The propagator is the same computation that reproduces the published r = 22 literal `f_D(0) = 0x01ebb04ce1fc6ef55e5bbc0c99a8fde1b23ccd0d8be2a3b2f068630c0a4f3f71` of `1253b348` section 2.3 exactly; at r = 21 it gives

`f_D(0) = 0x36b153bb044072edf9f26b65249c0916ff2a474ed84a710a60ff678516cb3a3`,

nonzero, so `deg F = D` exactly. (The stage-B program tests the leading coefficient of the built `g_c` at run time and normalises by it; nothing rests on this offline value.)

2.3 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then the canonical pairs `(nk, rho)` differ (2.4 of `1253b348`: `x -> x^5` injective, the line direction nonzero) and the digests are equal.

## 3. Odd part with a centre

For a centre `c in F_p`, `F(c + s) - F(c - s) = 2 s g_c(s^2)` with `g_c` of degree exactly `m = (D - 1) / 2 = 3,725,290,298,461,914,062` and leading coefficient `f_D(0)`. A collision pair with midpoint `c` is `W1 = c + s`, `W2 = c - s` with `S = s^2` a nonzero square root of `g_c`; the useful roots are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)`, a product of distinct linear factors.

Construction of `g_c` by evaluation (`1253b348` section 3 at r = 21). No transform of `H >= m + 1` points exists (`p - 1 = 2^32 * 3 * q`). Let `B = 3 * 2^31 = 6,442,450,944`, `kappa = ceil((m + 1) / B) = 578,241,159`, `z = 4^B`, evaluation points on the `kappa` cosets. The inverse transforms are `kappa` transforms of size `B`; the geometric solve runs, per position `j < B`, two correlations of length `S_len = 3 * 2^29 = 1,610,612,736` (the smallest `2^a` or `3 * 2^a` that is at least `2 kappa - 1 = 1,156,482,317`). The `2 kappa B = 7,450,580,601,318,408,192` evaluations of `F` are each charged as one target-compression unit (`C(21) = 657`), although a line evaluation is a strict subset of the work of a reference permutation (the same generous rule as `1253b348`). The loop work, the transforms, the solve, its once-per-trial constants and the normalisation are charged on top (4.3).

## 4. The algorithm (one centre, one thread)

### 4.1 Stages, coins and the stopping rule

The stage structure, coins, stopping rule and isolation stage are those of `1253b348` 4.1, 4.1.1 and 4.1.2 verbatim at `K = 1`, `DMAX = 16`, `Z = 64`:

```
init:   twiddle table (once)
setup:  the line (once)
for t = 1 (one centre):
  A  c := a uniform element of F_p from one fresh random word
  B  g := monic g_c (section 3)
  C  R := S^((p-1)/2) mod g   (value domain, section 4.4: 192 squaring steps, 45 of them also multiply by S)
  D  G := gcd(g, R - 1)       (half-gcd, section 4.5)
  E  if deg G in [1, DMAX]: isolate a root S of G (at most Z rounds, lemma 9.4)
  F  s := sqrt(S); W1 = c + s, W2 = c - s; map back to (nk, rho)
  G  verify with two reference hashes (657 operations each)
H  output the two pairs
```

The exponent `E = (p-1)/2` has bit length 254 and Hamming weight 46, its leading bit at position 253, and the 64 bits after the leading one (positions 189 to 252) are zero (computed; 10.3(d)). Write `E = 2^253 + E_low` with `E_low = E mod 2^189 < 2^189` of Hamming weight 45. The Barrett start of stage C forms `R~_0 = X^v P1 mod g` with `v = 2^61` (a multiple of `2^32` below `m` also at r = 21, since `2^61 = 2,305,843,009,213,693,952 < m`; on a coset, `x^v = u_k^v zeta^i` with `zeta = omega^v` of order 3, constant on each Good-Thomas row), and the loop runs the recurrence `e' = 2 e + b` from `e_0 = 2^61` over the 192 bits of the word `E_low` read from the top: 192 steps (the first three with `b = 0`, the `VSHIFT = 3` of the lineage), of which 45 with a multiply, ending at `e = 2^253 + E_low = E` exactly (verified by running the recurrence on the actual exponent; 10.3(d)). Stage D's recursion parameters are fixed by `m` on the normal remainder sequence: the outer loop of the Euclid driver repeats 55 times at r = 21 (from `m` down to at most 192, each repetition removing more than half of the degree), and the recursion is simulated exactly in the count (4.5). The ABORT rules (quotient, return and window tests, the stage-C zero test) and the prefix argument are `1253b348` 6.3 verbatim: a trial with any other remainder sequence ends after a prefix of the charged work.

#### 4.1.1 Coins

Identical to `1253b348` 4.1.1: at most 65 fresh words, a draw 31 operations, the reduction within statistical distance `2^-128.9` of uniform per word, `eps_coin < 2^-122` over the run.

#### 4.1.2 Stage E: isolating a root of G

Identical to `1253b348` 4.1.2 (Taylor shift by a drawn shift, `X_a = Z^((p-1)/2) mod G`, the split by `gcd`, the smaller part kept); the failure probability is bounded by lemma 9.4 (`2.371e-15`), proved, no premise.

### 4.2 Machine model and charging rules of this entry

Every operation is counted where it executes; none is estimated; every rule below is either the published table of `1253b348` 4.2 (rule R1) or a charge at least as large for the same work (R2-R6). The machine is the machine of `1253b348`: a word RAM with 256-bit words, one field element per word, a register file of 387 words (256 field registers of 256 bits and 131 integer address registers), one load per word fetched, one store per word written, each address formation charged.

* **R1 (kernel table).** The column-kernel charges of `1253b348` 4.2, applied verbatim: a call over `nb` blocks at `cnt` positions costs `constant + per-position * cnt + F(cnt)` with `F(cnt) = 1 + 3 floor(cnt/8) + 2 + 3 (cnt mod 8) + 2`, and the constants `ob128: 269 + 1600 cnt`, `ob64: 139 + 704 cnt`, `ob32: 34 + 304 cnt`, `ob16: 18 + 128 cnt`, `ob8: 10 + 52 cnt`, `ob4: 6 + 20 cnt`, `ob3: 7 + 22 cnt`, `ob2: 5 + 11 cnt`, plus 3 of driver loop per call. A transform of `3 * 2^a` points is the radix-3 stage (`ob3` calls at the `n/3` triple positions) and three rows of radix-2 passes, at most seven layers per pass (`ob128`), the remainder of `a mod 7` layers as one pass of the matching size; a transform of `2^a` points is the radix-2 part alone. A batched transform over `cnt` cosets runs every call at `cnt` positions (the published column form); a single-coset transform runs the same calls at `cnt = 1` (no batch amortization of the call charges, a larger charge than the batched form). Batching is used only where the published entry batches (the inner transforms of stage C over its coset arrays).
* **R2 (plain pass pricing).** The solve correlations of stage B and the inverse transforms of stage B are charged, per `1253b348` section 3's own rule ("each two transforms of length `S` with `S/2 log2` butterflies at the charge of the model's own pass cost"), at the model's full per-layer pass price: per layer and row-point 8 operations (a load and a store with their address formations 4, half a butterfly 1.5, half a twiddle load with its address 0.5, loop control and index arithmetic 2), and the radix-3 stage 13 per triple. This is strictly above the register-blocked charge for the same work.
* **R3 (block products).** Every product whose operands exceed the `3 * 2^32` transform cap (the Newton reciprocal and the `q` product of the Barrett start, and the products of the stage-D top region) is computed by the chunked block transform of `1253b348` 4.5 (blocks of `B = 3 * 2^31` coefficients, inner transforms of `3 * 2^32` points, an outer transform across the blocks, chunk assembly, pointwise products, the fold and the untwist). The charge is `STREAM = 1200` operations per streamed input coefficient and `WIN = 4400` operations per output-window coefficient. Itemization per streamed coefficient at the concrete sizes (block count `nb <= 4 * 10^8`, `log2 nb <= 29`): forward and inverse inner-transform passages `3 x 66.4` (the R1 per-point charge; each coefficient transformed once forward per operand use and the outputs inverse once), outer-transform butterflies `2 x 29 x 1.5 <= 87`, pointwise 3, assembly, weights, fold, untwist and placement about 40 field operations, their loads, stores and addressing about 4 per field operation about 320, loop control and index arithmetic about 50: at most about 660. Per output-window coefficient the same itemization with one forward and one inverse inner passage, the full assembly and placement chain, and the accumulator traffic: at most about 560. The declared rates 1200 and 4400 are at least 1.8 and 7.9 times these itemizations.
* **R4 (stage-D complement).** The inversion-free nodes of stage D (parameter `2^j - 1`, `7 <= j <= 31`, matrix-only) are charged at the published `node(j) + 10` constants of `1253b348` 4.4.3 (its table, transcribed in 4.5 below). The complement - the products, divisions, windows and tests of the top region (parameters at least `2^54`, split at `ceil(k/2)`) and of the non-aligned nodes below it, the apply_inv and matrix products, the classical tail below degree 192 and the monic scaling - is charged at `6 *` the node charge. The multiplier is generous, and the ratio is scale-invariant: both the node tiling and the complement are sums of products over the same recursion tree, a function of `m` that scales with it (the walk of 4.5 gives `node(r=22) / node(r=21) = 5.000`, the degree ratio), and at r = 22 the published per-operation ledger of the same algorithm prices this complement at `4.81 *` its node charge (`2,311,690,734,967,390,642,254,210` over `480,515,005,842,733,334,842,189`). The declared `6 *` covers the ratio with 25% headroom at both rounds.
* **R5 (stage-B loop).** The evaluation loop of stage B is charged 56 operations per evaluation point on top of the `C(21)` unit per evaluation: the itemized field operations of `1253b348` section 3 (two additions for the points, one subtraction, one multiplication by `1/(2 s)`, two multiplications for the recurrences of `s` and `1/s`, one store) each with its operand loads and addressing, the loop control, the row counter and the bit-reversed index arithmetic.
* **R6 (stage overheads).** Rows B and C carry a flat 15% and 10% respectively over their itemized terms (set-up, staging, allocator traffic, loop control and the small steps beyond the itemized terms).
* All other charges (the random words, the Montgomery conversions, the small-degree work of stages E, F and G at their caps, the output, the allocation charges, the ABORT reset, the offline derivation at its cap) are the published r-independent constants of `1253b348` section 6, restated in the ledger; row G uses `C(21) = 657`.

### 4.3 Stage B at r = 21

`578,241,159` cosets of `6,442,450,944` points, two evaluations of `F` per point at `657` operations each; the loop work at 56 per point; the inverse transforms of the cosets at R2; the geometric solve per position `j < B` at two correlations of length `1,610,612,736` (each two R2 transforms, `10 S` pointwise and scalings, `30 kappa` staging), its once-per-trial constants, and the normalisation; +15% (R6).

### 4.4 Stage C at r = 21: the powering in the value domain

The method of `1aa56884` (as `1253b348` 4.6). `h = 3 * 2^32`, `K = ceil((m + 1)/h) = 289,120,580` cosets per point set, `n1 = K h = 3,725,290,307,101,655,040 = m + 1 + 8,639,740,977`. The Barrett start computes the reciprocal of the reversed `g` modulo `X^ell`, `ell = v + (n1 - m) + 1 = 2,305,843,017,853,434,931` (the same formula that reproduces the published r = 22 literal `2,305,843,013,757,693,177` exactly), then `q = floor(X^v P1 / g)`; both products are charged at R3. Step 2 evaluates `g` on `O1` and `O2` (one chirp correlation of length `Le = 2^30` per position - the smallest length at least `3 K - 1 = 867,361,739` - plus `2K` forward inner transforms of `h` points at R1, batched). Step 3 evaluates `q` at the nodes of `O2` (correlations of length `Lq = 3 * 2^27 = 402,653,184`) and forms `R~_0` on `O2` pointwise; step 4 is one extension `O2 -> O1`; step 5 the batch inversion; step 6 the loop of 192 steps (45 with `b = 1`), each two pointwise passes and two extensions; step 7 leaves the Montgomery form; step 8 interpolates `R2` and `g` into coefficient form. An extension is, per position `j < h`, a correlation of length `Lx = 3 * 2^28 = 805,306,368` (the smallest length at least `2 K - 1`), charged two R1 single-coset transforms of `Lx` points plus pointwise and scalings, plus the `2K` inner transforms of the cosets at R1 (batched); the Winograd radix-3 replacement and the fused boundary passes of `1253b348` 4.6 are NOT taken (every butterfly is charged in full at R1); +10% (R6).

### 4.5 Stage D at r = 21

The half-gcd of `1253b348` 4.4/4.4.1/4.4.2/4.4.3 on `(g, R - 1)`, `deg g = m`: the aligned split below `2^54` (a parameter `2^j - 1` splits into `2^(j-1) - 1`, one division, `2^(j-1) - 1`), the matrix-only calls of parameter `2^j - 1` (`7 <= j <= 31`) on the inversion-free node of `4bcabff8`, the scaled division and product forms of `a78f526e`, charged for the normal remainder sequence (every quotient of degree 1) with the quotient, return and window tests and the ABORT of `1253b348` 6.3. The count simulates the recursion exactly on the normal sequence (the parameter tree is a function of `m` alone): the outer loop of the Euclid driver repeats 55 times, and the inversion-free node calls tile the degree range below the top region; their total charge is

`node_charge = 96,103,002,060,067,857,432,887`

(the walk over the tree with the `node(j) + 10` constants, transcribed from `1253b348` 4.4.3 - the charge of one inversion-free node of parameter `2^j - 1` on the machine of 4.2, covering its 3-row products, pseudo-divisions, CRTs, transforms, twiddles, allocations and tests):

| j | parameter `2^j - 1` | `node(j) + 10` |
|---:|---:|---:|
| 7 | 127 | 300,325 |
| 8 | 255 | 762,659 |
| 9 | 511 | 1,896,589 |
| 10 | 1,023 | 4,535,361 |
| 11 | 2,047 | 10,579,017 |
| 12 | 4,095 | 24,247,673 |
| 13 | 8,191 | 54,845,689 |
| 14 | 16,383 | 122,759,449 |
| 15 | 32,767 | 272,415,353 |
| 16 | 65,535 | 604,910,535 |
| 17 | 131,071 | 1,330,497,923 |
| 18 | 262,143 | 2,906,012,187 |
| 19 | 524,287 | 6,312,011,115 |
| 20 | 1,048,575 | 13,646,532,395 |
| 21 | 2,097,151 | 29,385,787,339 |
| 22 | 4,194,303 | 63,055,053,355 |
| 23 | 8,388,607 | 135,482,363,257 |
| 24 | 16,777,215 | 289,776,338,741 |
| 25 | 33,554,431 | 617,645,653,965 |
| 26 | 67,108,863 | 1,312,752,319,261 |
| 27 | 134,217,727 | 2,783,312,331,997 |
| 28 | 268,435,455 | 5,888,346,946,941 |
| 29 | 536,870,911 | 12,432,687,806,429 |
| 30 | 1,073,741,823 | 26,280,442,643,243 |
| 31 | 2,147,483,647 | 55,399,609,269,479 |

Row D = `6 * node_charge = 576,618,012,360,407,144,597,322` by R4.

## 5. Why the output is a collision

`1253b348` section 5 verbatim: a root `S` of `G` is a nonzero square with `g_c(S) = 0`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, the canonical pairs differ and collide; stage G recomputes both reference hashes and compares; the algorithm outputs only verified collisions. No probability enters this section.

## 6. Ledger: worst-case operation count (`C(21) = 657`)

`N_max = T_fixed + T_trial + T_off` with `K = 1`, every trial charged in full (stage D for the normal sequence, which bounds every trial by the prefix argument of `1253b348` 6.3; stage E at its cap).

| row | what is charged | operations |
|---|---|---:|
| init | twiddle table of `2^31` elements (6.1) | 17,179,887,666 |
| setup | the line (`1253b348` 6, r-independent) | 4,910 |
| A (per trial) | stage bookkeeping, loop test, the coin draw, one allocation | 1,382 |
| B (per trial) | stage 3 at r = 21 under R2/R5/R6 | 18,991,939,593,846,380,843,154 |
| C (per trial) | stage 4.4 at r = 21 under R1/R3/R6 | 1,431,088,767,664,829,718,738,382 |
| D (per trial) | stage 4.5 under R4 | 576,618,012,360,407,144,597,322 |
| E (per trial, cap) | isolation at its cap, `Z = 64` rounds at `DMAX = 16` (6.1) | 168,104,221 |
| F (per trial) | `1253b348` 6 (r-independent) | 47,012 |
| G (per trial) | two reference hashes at `C(21)` with the memory-access charge (`1000 + 10 * 2 * 657 + 32`) | 14,172 |
| trial loop / ABORT reset / plan misses / H / I | `1253b348` 6 (r-independent) | 12 / 1,000 / 176,073 / 5,644 / 3,384,436 |
| offline | declared cap (`preprocessing_log2 = 20`) | 1,000,000 |
| **N_max** | | **2,026,698,719,619,100,596,805,386** |

`log2(N_max / 657) = 71.385657`, claimed as `time_log2 = 71.38566` (rounded up at five decimals). The main components: row B = `7,450,580,601,318,408,192` evaluations at 657 (`4,895,031,455,066,194,182,144`) + loop (`417,232,513,673,830,858,752`) + inverse transforms (`940,014,919,204,298,429,496`) + solve (`10,240,099,450,308,651,909,120`) + 15%; row C = the loop of 192 steps (`1,098,993,757,702,251,243,110,400`, embedding its 384 extensions at `2,804,337,326,244,967,219,200` each plus the pointwise passes and the `b = 1` extras), the Barrett start (Newton `154,952,650,412,690,431,459,200`, `q` product `31,999,126,905,210,632,233,600`), the evaluations and steps 2-8 (one further extension at the same unit charge in step 4, two in step 8), +10%; row D as in 4.5.

### 6.1 The fixed rows, derived

The r-independent rows are charged at this entry's own derivations; each meets or exceeds the corresponding published constant of `1253b348` section 6 (so the r = 22 validation of 6.2 compares like with like).

* init: the twiddle table of the `3 * 2^32`-point transform has `2^31` elements at 5 operations (the multiplication by the running root, its load and store with addressing, the loop step), the build loop `3 * 2^31 + 2` of control, and seven inversions (the root-chain seeds and the normalisation constants) at 2,640 each (`a^(p-2)`: 254 squarings and 76 multiplications = 330 field operations, plus 2,310 control of the bit loop): `5 * 2^31 + (3 * 2^31 + 2) + 7 * 2640 = 17,179,887,666`.
* A: the stage bookkeeping 1,000, the loop test and update 5, the coin draw 31 (4.1.1: the word load, store and addressing 6, the three-step reduction 9 with its loop control 11, the conversion 1, the entry and its address 4) and one allocation 346 (`1 + 120 + 13 (2 L + 1)` at `L = 8` live blocks): 1,382.
* E at its cap: a round at degree `d = DMAX = 16` costs the draw 31, the zero test 7, one negation and the round bracket (copies, tests, frees) at most 3,543 in all, a Taylor shift at most 12,000, the schoolbook `Z^((p-1)/2) mod G` = 253 modular squarings each `10 (2d + 3 d (d-1)/2 + 2 d^2) + 670 = 9,710` field operations with allocation and free (every field operation carries its memory-access charge of 9) and 45 multiplications by `Z` at 320 each, plus 2, and two classical gcds at most 70,000 each (at most 16 outer iterations, each an inversion at 2,640 and at most 33 division steps at about 50): `R(16) = 2,626,611`, `E_cap = 1,000 + 3 + 64 R(16) + 114 = 168,104,221`.
* F: the stage bookkeeping 1,000, 12,002 of Tonelli-Shanks control, and at most 3,401 field operations at 10 each (the powers by `q` and `(q+1)/2`, the parameter loop from 32, two back-maps of three fifth-root powers `x^e`, two multiplications and four additions each, one addition and one subtraction): 47,012.
* G: `1,000 + 10 * 2 * 657 + 32 = 14,172` (two reference hashes at `C(21) = 657` operations, every field operation carrying its memory-access charge, the stage bookkeeping and the comparison).
* H: six Montgomery exits (6 multiplications), six numbers at 64 hexadecimal digits (12 operations per digit) and six calls at 5, with the stage bookkeeping 1,000: `6 + 6 * 64 * 12 + 6 * 5 + 1,000 = 5,644`.
* I: the report formatting `400 * 8,192`, the loops 20,000, the entry and length check 100, one write system call `10,000 + 8 * 8,192`, one exit 10,000 and the bookkeeping 2,000: 3,384,436.
* plan misses: one per distinct transform plan size (57 sizes), 3,089 each: 176,073. The setup of the line (4,910), the trial-loop row (12) and the ABORT reset (1,000, 4.1) are the published r-independent constants of `1253b348` section 6, quoted; together with the offline cap (1,000,000, section 6.2 there, one literal at a time) they sum to 1,011,416 operations, half a part per million of `N_max`, and no claim depends on their further decomposition.

### 6.2 Validation of the counting program at r = 22

The same program, the same rules, at r = 22 (the reference instantiation whose per-operation ledger is published as `1253b348` sections 6-7) yields:

| quantity | this program at r = 22 | published `1253b348` | ratio |
|---|---:|---:|---:|
| row B | 87,395,067,043,007,858,612,911 | 70,687,663,583,435,236,818,093 | 1.236 |
| row C | 5,789,989,538,739,699,779,625,312 | 2,864,231,396,344,716,890,684,788 | 2.021 |
| row D | 2,883,090,035,056,920,427,627,554 | 2,792,205,740,810,123,977,096,399 | 1.033 |
| stage-D node charge | 480,515,005,842,820,071,271,259 | 480,515,005,842,733,334,842,189 | 1.0000000000002 |
| arena | 2,421,439,619,699,002,310,656 | 2,386,356,551,700,258,436,352 | 1.015 |

Every row is at or above the published count (the rules are upper bounds for the same work), the node charge - the one part counted at exactly the published granularity - agrees to six significant digits (the walk's j-mix differs negligibly from theirs; both tilings sum to the same degree range), and the r-independent literals of this entry's sections 2-4 (`f_D(0)` at r = 22, `ell`, the parameter formulas) reproduce the published r = 22 values exactly. As a score, the same rules at r = 22 give `124.48915`, `0.634` above the published `123.85495`: the declared r = 21 figures carry at most this margin over the reference-grained count of the same algorithm.

## 7. Memory

(a) Code and static data: 5,250,444 bytes (`1253b348` 7(a), unchanged). (c) Stack: 65,536 bytes. (d) The register file: 387 words of 256 bits, 12,384 bytes.

(b) The arena: the live peak is stage C's, which holds `R1`, `R2`, `G1` and the array of `g` (four arrays of `n1 = 3,725,290,307,101,655,040` elements at 32 bytes), the twiddle table of the `3 * 2^32`-point transform (`3 * 2^31` elements), the group buffer of `3 * 2^10` rows of `Le = 2^30` elements and one transform row of `Le` elements; stage B holds the evaluation array of `kappa * B` elements and its working arrays (smaller at r = 21); stage D's live set at r = 21 (the two `m`-coefficient operands, the four matrix arrays and the block-product chunk forms) is below the stage-C peak (at r = 22 the same statement is the published one, `2,252,183,265,158,336,140,544` against `2,384,186,428,193,518,891,648`, and both sides scale together in `m`). The arena adds an allowance of one sixty-fourth for block headers and allocator rounding and a `2^48`-byte margin for the slab classes and the small arrays of stages D to I:

`arena = 484,288,128,844,851,838,976` bytes, `total = 484,288,128,844,857,167,340 = 2^68.7144`, claimed as `memory_log2_bytes = 68.715` (rounded up at three decimals). The memory penalty is `68.715 - 20 = 48.715`. At r = 22 the same rule gives `2^71.037`, above the published `2^71.016` (table in 6.2).

## 9. Success probability and the premises

### 9.1 The premise `H-ONE`

Notation of `1253b348` 9.1 at r = 21: `D = 5^27`, `F` the digest polynomial of 2.2, `g_c` the monic odd part of degree `m = 3,725,290,298,461,914,062`, `k(c)` the number of nonzero squares with `g_c(S) = 0`, `E_c` the event `1 <= k(c) <= 16`.

**Premise.** The number of centres `c` with `1 <= k(c) <= 16` is at least `0.3931 p`; for `c` uniform, `P(E_c) >= q = 0.3931`.

Scope: the fixed target `poseidon-orchard-r21-prefix-v1`, this line construction, this `F`; nothing for other round counts. Limitations: false for permutation polynomials and for a decomposable `F` with imprimitive monodromy (the axis line of 10.3, Theorem C); false at one layer; the value `0.3931` is `0.0003693` below `1 - e^(-1/2) = 0.3934693` and `0.0001292` below the four-moment Bonferroni bound `151/384`. With `delta = 0.003` the bound of 9.2 needs `P(E_c) >= 0.393000000000002345`.

### 9.2 The success bound with one centre

(a) The centre is one draw, within `2^-128.9` of uniform; `eps_coin < 2^-122` over the run. (b) `P(not N_c) <= delta = 0.003` (H-NORMAL, 9.5). The stage-C zero test: for each of the `n1` points `x` of `O1`, `g_c(x)` is a polynomial of degree `D - 1` in `c` with `D f_D(0)` leading coefficient, nonzero (2.2), so `P(Z_c) <= delta_C = n1 (D - 1) 4 / 2^256 = 9.587e-40 < 2^-129`, proved, no premise. (c) The isolation lemma 9.4 (proved): `eps_iso <= 2.371e-15`. (d) With `K = 1`,

`P[success] >= q - delta - delta_C - eps_coin - eps_iso = 0.3900999999999976 >= 0.39009`.

The bound stays at least 0.39 for every `delta <= 0.0030999` at `q = 0.3931`. The probability is over the algorithm's random words for the fixed target; no run at r = 21 enters it.

### 9.3 Where the number comes from (support of `H-ONE`; not used in the bound)

The law, the moments, the Bonferroni bounds and the theorem at two and three layers are those of `1253b348` 9.3, and every one of them is computed below the partial-round count: the roots of `G(c, t)` are signed (the cover lies in the hyperoctahedral group `B_m`), and the monodromy computations on the deployed constants and the algorithm's line (the computations of `1253b348` 10.3, credited there to Grok jobs 136 and 137 and re-run by that entry on the deployed constants) give, for `F_N` the truncation of `F` to its first `N` S-box layers (the same polynomial at every `r >= 2`):

| N | deg `F_N` | m | cycle types of `H(c,u)` found (value of c) | monodromy of `H` | w |
|--:|---:|---:|---|---|---:|
| 1 | 5 | 2 | (2) at 3, (1,1) at 1 | `S_2` | 1 |
| 2 | 25 | 12 | (12) at 8, (11,1) at 18, (7,1^5) at 1644 | `S_12` | 1 |
| 3 | 125 | 62 | (62) at 82, (61,1) at 24, (59,1^3) at 622 | `S_62` | 1 |
| 4 | 625 | 312 | (312) at 121, (311,1) at 357 | transitive, 2-transitive | not computed |

with, for every row, the spot check of `F_N` against direct iteration of the rounds, the leading coefficient equal to the propagated one, `F_N'` squarefree with `5^N - 1` simple roots, and `H(c,0) = F_N'(c)` at `c = 1, 2, 5, 17`. At `N = 2` and `N = 3` the arithmetic monodromy `B_m = F_2^m x S_m` makes the j-fold fibre powers absolutely irreducible and the Aubry-Perret bound with Bonferroni gives `0.39346933 <= P(1 <= k <= 16) <= 0.39346944`: the premise is a theorem there ("for `N <= 4` the polynomial `F_N` is the same at every round count `r >= 2`", `1253b348` 10.5.1). The toy-field measurements (27 cases, 3 to 8 layers, deviations `1.36/sqrt(p)`) and the counts of Grok job 139 (`eps ~ 3.1/sqrt(p)`, degrees 5 to 1,953,125, no dependence on the degree) are likewise below r. The extrapolation is from the law at the computed depths to `N = 27` in place of `N = 28`: no structure appears between the third layer and the twenty-seventh that changes the law of the positive fixed points by 0.09%.

### 9.4 Lemma (isolation), proved

`1253b348` 9.4 verbatim (the statement and proof are in `d = deg G <= 16` and the coin draws; nothing depends on r): each round halves the degree with probability at least `w = 1/2 - 7.869e-40`, and the failure probability is at most `P[Bin(64, w) <= 3] = 2.371e-15`.

### 9.5 The premise `H-NORMAL`

**Premise.** For `c` uniform on `F_p`, the Euclidean remainder sequence of `(g_c, R_c - 1)` at r = 21 (`deg g_c = m = 3,725,290,298,461,914,062`) is normal down to its gcd (`deg(R_c - 1) = m - 1`, every quotient of degree 1) except with probability at most `delta = 0.003`.

This is bradcush's premise (entries `e6dcb600`, `1aa56884`) with the allowance of gta6rp's `fe269c23`, stated at r = 21. Role: score-critical for the success probability only - the time and memory bounds hold for every sequence (the ABORT and prefix rules of 4.1/6). Extrapolation and evidence: the random-pair Schwartz-Zippel remark (`2 m^2 / p < 2^-121`, not transferred), and the organizer-run tests of 10.5: the normality experiments run the complete sequence of `(g_c, R_c - 1)` on the truncations `F_2`, `F_3` (m = 12, 62 - the same polynomials at every r) and the sibling targets (m = 7,812 and 39,062); a run with no abnormal sequence is a reproducible observation consistent with the premise, `delta = 0.003` is the declared allowance. Limitations: the tests reach `m = 62` organizer-run (`39,062` on the siblings), far below `m`; nothing about the organiser-seeded trials is assumed.

## 10. Evidence

### 10.2 The organizer experiments (declared in `experiments/manifest.json`)

Nine experiments of kind `python-message-pairs-v1`, the same programs and events as `1253b348` 10.2 and 10.5.1 (the sources are r-parameterized: each reads the round count of the selected target from the runner's `target_profile`, so the same programs run at r = 21 against the r = 21 digest):

(a) `lowbits-birthday` (`experiments/exp_lowbits.py`): per organizer trial, a birthday search over at most 1200 fresh inputs for two distinct canonical messages whose r = 21 digests agree on the first 14 bits; a returned pair counts only when the organizer's callback confirms it.

(b) `line-ladder-w6/-w8/-w10/-w12` (`experiments/exp_line.py`): the line construction of section 2 at r = 21 (the program builds the line `j = 0`, evaluates `F(W)` as the remaining twenty-seven rounds on `alpha + beta W`, maps points back with the inverse S-box); per trial, a centre from the seed and a scan of the antipodal pairs `s = 1, ..., 150` for agreement on the first 6, 8, 10, 12 bits - the reduced-width form of the event `F(c+s) = F(c-s)` that `H-ONE` is about. The intake report of the organizer's run (256 trials per experiment) records 256 of 256 returned pairs for `lowbits-birthday`, 231, 118, 33 and 14 for the ladder at widths 6, 8, 10 and 12, and 256, 256, 103 and 9 for `euclid-normal-n2-t256-l2-a/-b`, `one-centre-n2-t256` and `one-centre-n3-t24`: every computed normality sequence normal (no abnormal sequence in 512), and the one-centre counts at the depths where the law is a theorem (103/256 = 0.402 at m = 12; 9 pairs in the 24-trial budget at m = 62, the law's 0.393 x 24 = 9.4). The counts of returned pairs are reproducible observations consistent with the r = 22 run of the same programs (256; 232/128/47/8; 256/256; and the one-centre counts there); no probability, rate or population bound is drawn from them and none enters section 9.

### 10.5 Organizer-run tests: normality and one centre (`experiments/exp_euclid.py`)

The four experiments `euclid-normal-n2-t256-l2-a/-b` (two centres per trial, `m = 12`, 512 sequences each) and `one-centre-n2-t256` / `one-centre-n3-t24` (one trial of the algorithm at depth `N = 2, 3`), the program printed in full in `experiments/exp_euclid.py` (Python standard library only): the design follows gta6rp's `fe269c23`; for each computed trial the program builds `F_N(c + X)` exactly over `F_p` on the deployed constants and the algorithm's line, takes the monic odd part, computes `R = X^((p-1)/2) mod g` and runs the complete Euclidean sequence of `(g, R - 1)`, recording every quotient degree; a trial returns a pair of canonical messages exactly when its sequence(s) are normal (and, for the one-centre tests, `1 <= k(c) <= 16` and the isolated root verifies). For `N <= 4` the polynomial `F_N` is the same at every round count `r >= 2`, so the tests measure the same family of pairs as the premise; only the returned witness is checked against the r = 21 digest by the runner. The intake report of the organizer's run is the evidence; the per-trial counts are untrusted observations; nothing enters section 9.

### 10.3 Computed facts of this entry

(a) The leading-coefficient propagator of 2.2 (exact integer arithmetic over `F_p` on the organizer's pinned constants) reproduces the published r = 22 literal exactly and gives the r = 21 literal above; the run also checks the nonzero minor and the nonzero `beta`. (b) The parameter formulas (`kappa`, `K`, `n1`, `S_len`, `Lx`, `Le`, `ell`) reproduce the published r = 22 literals exactly (`1253b348` sections 3 and 4.6) and are evaluated at r = 21 in sections 3-4. (c) The stage-D recursion walk of 4.5, run at r = 22, reproduces the published node total `480,515,005,842,733,334,842,189` to six significant digits (section 6.2). (d) The exponent decomposition of 4.1 is verified by direct computation on `E = (p-1)/2`: bit length 254, Hamming weight 46, leading bit at 253, bits 189 to 252 all zero, `E_low = E mod 2^189` of Hamming weight 45 (15 set bits below position 62, the lowest at 31), and the recurrence `e' = 2 e + b` run from `e_0 = 2^61` over the 192-bit word `E_low` (three leading zero bits, then its 189 bits) ends at `e = E` with exactly 45 multiplies. The counting program of sections 4-7 is exact integer arithmetic; its outputs are the figures of sections 6-7 and the validation table of 6.2.
