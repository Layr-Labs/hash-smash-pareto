# Orchard Poseidon, r = 3: one deterministic executed run (two free rounds on a line, odd part about a centre, value-domain powering, half-gcd)

## 1. Claim

Target: `poseidon-orchard-r3-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, partial rounds 4, 5 and 6, full rounds
60-63, state `[nk, rho, 2^65]`, digest = coordinate 0 of the output state). Output: two distinct canonical pairs `(nk, rho)` with equal
digests.

* `success_probability = 1`: the procedure is deterministic (centres `c_i = i`, tried in the fixed order `i = 1, 2, 3, ...`, at most
  `MAXTR = 64` trials). It was executed once, from the start, on the fixed target and stopped with a verified collision after
  1 trial(s). Every executed trial is charged, and so is the work outside the trials. This is not a probability over centres.
  The centre order starts at the canonical first centre `c = 1`. It was already public (edd943c, see below) that this centre gives a
  collision on this line; the program does not use that knowledge (nothing is stored), and the line and the centres are the
  canonical choices of the construction. Section 5.1 shows from the certificate itself that the pair lies on the line with
  midpoint 1.
* `time_log2 = 28.22797` in target-compression units (`C(3) = 216 + 21*3 = 279` primitive operations per unit). This is the executed
  operation count of that one run, `N = 87,714,039,092` operations (section 6), and `log2(N / 279) = 28.227967`, rounded up at five
  decimals. The twiddle tables and the constants are built inside the run (or charged in it) and are part of `N`; there is no
  separate preprocessing and no advice, which claim.json records as `preprocessing_log2 = 0` and
  `nonuniform_advice_log2_bytes = 0` (meaning none).
* `memory_log2_bytes = 27.0028`. This is `134,473,813` bytes (section 7): the whole statically linked executable image (code, data
  and bss; the bss holds every buffer of the run) plus a 65,536-byte stack bound, rounded up at four decimals. The measured peak
  resident set of the run, 134,217,728 bytes, is below it. The memory penalty is `27.0028 - 20 = 7.0028`, so the normalized
  cost is `28.22797 + 7.0028 = 35.23077`.
* Dimensions: the line polynomial `g_c` has degree `m = 976562`. All transforms are radix-2 transforms of size at most `n = 2^20`
  on the 2-power roots of unity (the 2-adicity of `p - 1` is 32). Stage C uses `n = 2^20` points on each of two cosets. Stage D uses
  products on `2^j` or `3 * 2^(j-2)` points.
* Method: two free rounds on a special line make the digest a univariate polynomial `F` of degree `5^9`. Its odd part about a
  centre `c` gives `g_c`, and the roots of `g_c` that are squares give collisions. They are the roots of
  `gcd(g_c, S^((p-1)/2) - 1)`. This is the known approach of the current r = 3 frontier entry (edd943c). It was reimplemented
  from the mathematics, in our own source (section 9), with a lower executed count (edd943c's proof states `N = 317,054,280,703`
  operations, time 30.08182, memory 138,396,180 bytes = 2^27.0443, normalized 37.12612):
  (i) `g_c` is interpolated on `2^20` points (`2^21` line evaluations) and is never transformed to more than `2^20` points;
  (ii) the powering is a Montgomery squaring in the value domain of two cosets of `H_20`, four transforms of size `2^20` per
  step, and no product is ever formed in coefficient form;
  (iii) the gcd is an inversion-free half-gcd whose products are evaluated row by row on `3 * 2^(j-2)` or `2^j` points.
  **Disclosure:** the collision found is the same pair as the certificate of edd943c. Both programs use the line `j = 0` and the
  centre `c = 1`, and the root of `g_1` that they find is determined by the target. The claim is the cost of this program's
  execution, not the novelty of the pair.
* No cryptanalytic heuristic is used. The score rests on two disclosed premises: the charging model of section 4.2 (the same model
  as edd943c: field operations, loads/stores with address formation, loop and control operations, and an 18-word register file;
  declared as heuristic H1 in claim.json), and the faithful execution of the shipped deterministic source (sections 6, 8). The
  organizer did not execute it; the run takes about 15 minutes on one core.

## 2. Two free rounds: a line in the input plane

Notation: `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`. Since `p mod 5 = 2`, `gcd(5, p - 1) = 1`, and
`x -> x^5` is a bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5`. `M` is the deployed 3x3 MDS matrix and `c_{i,k}` the
deployed round constant `k` of round `i`. Both are read from the organizer file `orchard-pallas-constants.json` (section 9,
`gen_consts.py`).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5` and `K = (2^65 + c_{0,2})^5`, the state after round 0 is
`M (U, V, K)^T`. The map `(nk, rho) -> (U, V)` is a bijection of `[0,p)^2`, with inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`.

2.2 Round 1. The S-box inputs are `x_k = M_{k,0} U + M_{k,1} V + b_k` with `b_k = M_{k,2} K + c_{1,k}`. For an index
`j in {0, 1, 2}`, "the line `j`" is the line in the `(U, V)` plane on which `x_j` is constant and the other two inputs vanish at a
common point; this program (like edd943c) uses `j = 0`. Let `Q = (U_Q, V_Q)` solve
`x_1 = x_2 = 0`; the 2x2 determinant `M_{1,0} M_{2,1} - M_{1,1} M_{2,0}` is a minor of the MDS matrix and is nonzero. Put
`(a, b) = (M_{0,1}, -M_{0,0})` and `(U, V) = Q + tau (a, b)`. Then `x_0 = kappa = M_{0,0} U_Q + M_{0,1} V_Q + b_0` is constant (the
`tau` term is `M_{0,0} M_{0,1} - M_{0,1} M_{0,0} = 0`), and `x_i = tau d_i` for `i = 1, 2` with `d_i = M_{i,0} a + M_{i,1} b`.
With `W = tau^5`, the S-box output of round 1 is `(kappa^5, W d_1^5, W d_2^5) = v0 + W v1`. After the MDS of round 1 the state is
`alpha + W beta` with `alpha = M v0` and `beta = M v1`, affine in `W` (`line_setup` in `line.c`).

2.3 The digest polynomial. Rounds 2 and 3 (full), 4, 5 and 6 (partial) and 60-63 (full) apply nine S-box layers to coordinate 0,
starting from an affine function of `W`. Hence the digest is `F(W)` with `deg F <= D = 5^9 = 1953125`. The program checks that
`deg F = D`: the interpolated `g_c` of section 3 has degree exactly `m = (D - 1)/2` (`stage_prep` tests coefficient `m`, nonzero,
and the coefficients above it, all zero). The leading coefficient of `g_c` is that of `F`. For every `W` in `F_p`, `F(W)` is the
reference digest of the canonical pair built from `tau = W^e` (sections 2.1-2.2). Stage G of the run recomputes both digests with the
full reference permutation, and the organizer's hash checks the certificate.

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)`, then `tau1 != tau2` (`x -> x^5` is injective), so the points `(U, V)`
differ (`(a, b) != 0`) and the canonical pairs `(nk, rho)` differ, with equal digests.

## 3. Odd part with a centre, and interpolation on 2^20 points

For a centre `c` in `F_p`, write `F(c + s) - F(c - s) = 2 s g_c(s^2)`: the even powers of `s` cancel, and
`g_c(S) = sum_j f_{2j+1} S^j`, where `f_i` are the coefficients of `F(c + X)`. Since `D = 2m + 1`, `g_c` has degree exactly `m` and
leading coefficient `f_D`. A collision pair with midpoint `c` is `W1 = c + s`, `W2 = c - s` with `s != 0`, i.e. `S = s^2` a
nonzero square in `F_p` with `g_c(S) = 0`. These roots are exactly the roots of `G = gcd(g_c, S^((p-1)/2) - 1)`: a root `S` of
`g_c` in `F_p` is a nonzero square iff `S^((p-1)/2) = 1`. `G` divides `S^((p-1)/2) - 1`, which is squarefree and splits over `F_p`,
so `G` is a product of `deg G` distinct linear factors.

Stage B (interpolation). Let `n = 2^20 >= m + 1`, `zeta` a primitive `2^21`-th root of unity (`psi = 5^((p-1)/2^21)`; 5 is a
nonresidue) and `S_i = zeta^(2i)`, which runs over the subgroup `H_20` of order `2^20`. Then
`(F(c + zeta^i) - F(c - zeta^i)) zeta^-i = 2 g_c(S_i)` for `i = 0 .. n-1`. These are `2n = 2^21` line evaluations, each charged as one
target compression (279 operations), although a line evaluation (affine start, rounds 2-63 of section 2.3, one row of the last MDS)
is a strict subset of the work of a reference permutation. The value for `S_i` is stored at position `brv_20(i)`, the output order
of the forward transforms (`stage_b` in `stageb.c`). Since `deg g_c < n`, these `n` values determine `g_c`. Its coefficients are
one inverse transform away and are checked as in 2.3.

## 4. The program (one deterministic run)

### 4.1 Stages

```
init:  twiddle tables (two-level table TA x TB of psi^e), the transform constants of stage C
setup: the line (Q, a, b, alpha, beta), section 2
for i = 1, 2, ..., 64 (stop at the first verified collision):
  A     c := i
  B     the 2^20 values 2 g_c(S) on H_20 (2^21 line evaluations), section 3
  prep  coefficients of g_c and the checks of 2.3; q = floor(X^n / g) by Newton inversion of the reversed top part
        (series inverse to X^(n-m+1)); the start residue A0 = X^(2^16) (X^n mod g - 1); Gi = -1/(n^3 g') on H_20 by one batch
        inversion; G2 = g' on the coset psi H_20 (g' = 2 n g_c; section 4.4); trial ends if g_c vanishes on H_20 (not reached)
  C     kappa R := kappa S^((p-1)/2) mod g by 237 value-domain Montgomery squarings, 45 with a multiplication by S (4.5)
  D     G := gcd(g, kappa (R - 1)), monic, by the half-gcd (4.6); trial ends if deg G = 0
  E     a root S of G (deg G = 1: S = -G_0; deg G >= 2: equal-degree splitting with shifts 1, 2, ...)
  F     s := sqrt(S) (Tonelli-Shanks, 2-adicity 32, nonresidue 5); W1 = c + s, W2 = c - s; tau = W^e;
        (U, V) = Q + tau (a, b); nk = U^e - c_{0,0}, rho = V^e - c_{0,1}
  G     both reference hashes (279 operations each); success iff equal digests and distinct pairs
H     the six output values (centre, two pairs, digest) as 64 hexadecimal digits each
I     the report: formatted into one 8192-byte buffer, written by one write system call; exit_group
```

The exponent `E = (p-1)/2` has 254 bits and Hamming weight 46. Its top bit (bit 253) is followed by 128 zeros. The start residue
represents `S^v` with `v = 2^16`, the largest power of two with `m + v <= n` (section 4.4). This absorbs the top bit and the first
16 of those zeros, so stage C runs the remaining 237 bits, most significant first: 237 squarings, 45 of them followed by a
multiplication by `S`.

Determinism: the program reads no input and no file; its only argument is the round count (3). The order of centres, all
parameters (`n`, `v`, `kmax = 131071`, thresholds) and the trial cap are fixed in the source. There are no random choices. For
`deg G >= 2` stage E tries the shifts `delta = 1, 2, ..., 256` and ends the trial if none splits (each shift separates a given pair of
roots with probability about 1/2 over the shift); this branch was not reached in the run.

### 4.2 Machine model and charging rules

Every item below is counted by the executing code at the statement that executes it, with the counters of `fp.h`.

* Canonical `F_p` addition, subtraction (negation is one subtraction), multiplication and squaring: 1 each. Montgomery conversions
  (`fp_from_u64`, `fp_from_limbs`, `fp_to_limbs`) are one multiplication each. Inversion (`a^(p-2)`) and every exponentiation are
  expanded by left-to-right square-and-multiply: one squaring per bit below the top, one multiplication per further set bit, and 6
  control operations per bit (loop update, comparison, branch, word selection, shift, bit test), plus 6 per bit of the top-bit
  search.
* A load or store of a 256-bit array element: 1 each, plus 1 address operation each (`LD(n)`, `ST(n)`).
* Every loop: 3 operations per iteration (index update, comparison, branch) and 2 on exit (`LOOPC(n) = 3n + 2`), unless a
  different count is written next to it. The fixed 8- and 4-word operations of a transform block (the butterflies, and the
  pointwise maps of the stage C bottom pass, macros `R8`/`R4` in `stagec.c`) are written out straight-line with constant indices:
  no loop is executed there, and their words stay in registers.
* Every other executed integer or control operation (index and address arithmetic, shifts, masks, comparisons, branches,
  selections): 1 each, added by `CTL(k)` next to the statement. Where a statement's count is a bound, the comment says so.
* Procedure calls are treated as inlined: call, return and argument passing are not charged (every called function is a fixed
  block of counted statements and could be written in place without changing any counted operation; the transform kernels are
  `static inline`).
* Registers (the structural assumption, the same register file of 18 words of 256 bits as edd943c). A transform block of 8 data
  words keeps its 7 twiddles and one temporary in registers (16 words). The top passes of stage C keep 8 data words and 7 constants.
  Values held in registers are not charged as loads. Integer indices, pointers and loop bounds are held in integer registers.
* A line evaluation `F(W)` and a reference hash are charged one target compression (279 operations) each (`C_UNIT` in `line.h`),
  not their expanded arithmetic.
* Fixed bounds (`main.c`): 100 operations per stage switch (`STAGE_BK`), 20 per snapshot of the counters for a trial row
  (`TRIAL_BK`), 5,000 for the prologue of `main` (`PROLOGUE`), 20,000 for the constants of `consts.h` computed by `gen_consts.py`
  (`CONSTS_GEN`: `psi` and its inverse by exponentiation, about 650 field operations, `2^512 mod p`, `-p^-1 mod 2^64` and 201
  conversions; charged in stage init so that all preprocessing is inside the run), and in stage I: 400 per byte of the 8,192-byte output buffer
  (formatting, charged in full whatever it holds), 20,000 for the report loops, `10,000 + 8,192 * 8` for the write system call and
  10,000 for `exit_group`.
* Instrumentation is not an algorithm step and is not charged: the counter updates themselves, the reporting-only profile
  snapshots of stage D (`PROF_BEGIN/PROF_END`) and the arena-peak statistic.
* Memory allocation: stage D allocates from a stack arena inside the static buffer (`aalloc`, 5 operations; `arel`, 1). Stages B,
  prep and C use four fixed buffers of `n` words. There is no other allocator and no system call besides the two of stage I.

### 4.3 Transforms

The transforms run on the binary tree of the `2^21`-th roots of unity. Node `(d, j)` is the modulus `X^(2^(21-d)) - psi_d^brv_d(j)`
(`psi_d` of order `2^d`). It splits into `(d+1, 2j)` and `(d+1, 2j+1)` with the twiddle `psi_(d+1)^brv_d(j)`. The size-`2^L` transform
of a node maps a residue modulo that node to its values at the node's roots: natural-order coefficients in, bit-reversed values
out (Cooley-Tukey butterflies). The inverse is the transpose (Gentleman-Sande) and returns `2^L` times the coefficients
(`ntt.c`; `ntt_fwd_b` / `ntt_inv_b` take any node, given by its offset `B`). Passes cover 3 layers (radix-8 kernels, 8 data words
plus 7 twiddles in registers), or 2 or 1 at the end. Every element is loaded and stored once per pass. The 7 twiddles of a
supergroup come from one table twiddle (two loads and a multiplication, `TA[e mod 2^11] * TB[e >> 11]`) plus 2 squarings and 4
multiplications by constants. A block with all node twiddles equal to 1 uses kernels without those multiplications.

### 4.4 Stage prep

All four buffers have `n = 2^20` words. With `gt = 2 g_c`, the values of `gt` on `H_20` are the output of stage B.

1. One inverse transform gives `G* = n gt` in coefficient form. The program checks coefficient `m` (nonzero) and the coefficients
   above it (all zero).
2. With `k = n - m = 72014`, the reversed top part `f = rev_m(G*) mod X^(k+1)` is inverted as a power series by Newton iteration:
   `h_(2t) = h_t - h_t (f h_t - 1) mod X^(2t)`, with cyclic products of size `2t` up to `2^17`. Then
   `q* = rev_k(h) = floor(X^n / G*)`.
3. `T = q* G* mod (X^n - 1)` uses one forward transform of `q*`, a pointwise product with the stored values (`G*` on `H_20` is `n`
   times them) and one inverse transform. Since `X^n = q* G* + r` with `deg r < m <= n`, `T = 1 - r`, where `r = X^n mod g`.
4. The start residue is `A0 = -X^v T = X^v (r - 1)`, `v = 2^16`. It has degree `<= m - 1 + v < n` and satisfies
   `A0 = S^v P1 (mod g)` for `P1 = X^n - 1`, i.e. the Montgomery form of `S^v`.
5. `G2 = g'(O2)` with `g' = G*` on the coset `O2 = psi H_20` (roots of `X^n + 1`), by one forward transform.
6. `Gi = -1/(n^3 g'(O1)) = -1/(n^4 gt(O1))` on `O1 = H_20`, by one batch inversion (prefix products, one inversion, two
   multiplications per element). The trial would end if a value were zero (`g_c` vanishing on `H_20`); this did not occur.

### 4.5 Stage C: value-domain Montgomery powering

Let `P1 = X^n - 1`, `O1 = H_20` (where `P1 = 0`) and `O2 = psi H_20` (where `X^n = -1`, so `P1 = -2`). For residues of degree `< n`,
define `Mont(A, B) = (A B + u g') / P1` with `u = -A B / g' mod P1` (`deg u < n`). The numerator is divisible by `P1`, so the
quotient is exact. `Mont(A, B) = A B / P1 (mod g')`, and `g'` is a nonzero multiple of `g`. For `deg A, deg B <= n - 1`, the
numerator has degree `<= 2n - 2`, so `deg Mont(A, A) <= n - 2`. One step maps the residue `A` to `Mont(A, A)`, or to
`X Mont(A, A)` when the exponent bit is 1. The latter still has degree `<= n - 1`, so no reduction is needed. Starting from
`A0 = S^v P1`, the residue after the steps represents `S^e P1` with `e` the exponent prefix processed so far.

Representation. A residue `A` is held as `mu A` on `O1` and `lambda A` on `O2`, with `mu = n lambda`. The `O1` values are never
stored: the work buffer `W` holds the `O1` transform up to its last pass. One step:

```
U  = (mu A)^2 Gi  on O1                     (= -(mu A)^2 / (n^3 g'): the values of u, scaled)
U  -> O2: inverse transform on O1, forward transform on O2
B2 = (lambda A)^2 + U G2  on O2             (= lambda^2 (A^2 + u g') = -2 lambda^2 Mont(A, A) there)
     times X (the point) when the bit is 1; stored as the new O2 values (lambda' = -2 lambda^2)
B2 -> O1: inverse transform on O2, forward transform on O1 (mu' = n lambda')
```

The transforms are fused into passes:
* a bottom pass (depths 17-19): forward layers, the pointwise map, inverse layers, with the twiddles of the block computed once
  per block for both directions;
* a top pass (depths 0-2): the inverse top layers of one coset and the forward top layers of the other, with the 7 constants
  `psi_2, psi_3, psi_3^3, psi_4, psi_4^3, psi_4^5, psi_4^7` (every top twiddle of both cosets up to sign) in registers;
* the middle depths 3-16 in radix-8 passes.

Each step is 4 transforms of size `2^20` and the pointwise work. No normalization by `1/n` is executed: the scalars `lambda`, `mu`
are tracked (two field operations per step). At the end, an exit step with the multiplier 1 (`Mont(A, 1)`, degree `< m`) gives the
coefficients of `kappa R`, with `R = S^((p-1)/2) mod g` reduced and `kappa = -2 lambda_final`. The gcd of stage D is
scale-invariant, so `kappa` is never divided out: stage D receives `kappa R - kappa`.

### 4.6 Stage D: the half-gcd

Notation: for `(a, b)` with `deg a > deg b`, Euclid's sequence is `r_0 = a`, `r_1 = b`, `r_(i-1) = q_i r_i + r_(i+1)`, and
`d_j = deg q_1 + ... + deg q_j`. Every polynomial and 2x2 matrix below is held **up to a nonzero scalar**. This suffices because
only `adj(M) (a, b)` and products of matrices are formed (both homogeneous), and the final gcd is made monic.

`hgcd(a, b, k)` returns a matrix `M` with `(a, b)` proportional to `M (r_h, r_(h+1))` and `deg M = d_h`, `h = max{j : d_j <= k}`.
* Truncation lemma (von zur Gathen and Gerhard, *Modern Computer Algebra*, chapter 11, the fast Euclidean algorithm; the basis of
  every half-gcd): let
  `deg a = n > deg b`, `0 <= k <= n`, and let `a*`, `b*` satisfy `deg(a - a*) < n - 2k` and `deg(b - b*) < n - 2k`. Then the Euclid
  sequences of `(a, b)` and `(a*, b*)` have the same quotients `q_1 .. q_h` for `h = max{j : d_j <= k}`. (Thull and Yap give the same statement for their HGCD.)
  Each call therefore reads only the top `2k+1` coefficients
  (a pointer offset, no copy). The lemma is only needed for the run to succeed: a defect in stage D could make the computed
  `G` wrong and the trial fail, never produce a false collision, because stage G checks the pair with the reference permutation
  (and section 5.1 checks the certificate independently).
* `k <= 48`: Euclid's algorithm on copies of the top parts, while the next quotient fits the budget.
* Otherwise, with `k1 = floor(k/2)`:
  1. `M1 = hgcd(a, b, k1)`.
  2. `(c, d) = adj(M1) (a, b)`, i.e. `c = r22 a - r12 b`, `d = r11 b - r21 a`, by cyclic products. The true `c` has degree
     `deg a - d1`. In the normal case (`d1 = k1`, all quotients linear) and `k = 2^j - 1`, this is `3 * 2^(j-1) - 1`, so its residues on the three rows `Y - 1`, `Y + 1`, `Y - i`
     (`Y = X^(2^(j-1))`, three of the four quarter-rows of the size-`2^(j+1)` tree) determine it exactly. The inputs are split into
     the three rows by two butterfly layers (the fourth quarter-row, `Y + i`, is dropped). The code tests the degree at run time
     and otherwise uses the full size-`2^l` tree. Each row is transformed, the four matrix entries are
     transformed one row at a time and multiplied in, and each row is inverse transformed. The CRT is then
     `4 C0 = (R0 + R1) + 2 R2 - i (R0 - R1)`, `4 C1 = 2 (R0 - R1)`, `4 C2 = (R0 + R1) - 2 R2 + i (R0 - R1)`
     (`apply_adj3`). When the degree does not fit `3 * 2^(l-2)`, the same is done on the full size-`2^l` tree (`apply_adj`).
  3. If `d = 0` or the next quotient degree exceeds `k - d1`, return `M1`.
  4. One pseudo-division `beta^(t+1) c = Q d + e` (`t = deg c - deg d`, `beta = lc(d)`). It is inversion-free, and for `t = 1` it
     is one pass: `Q = beta c_n X + (beta c_(n-1) - c_n d_(n-2))`, `e_i = beta^2 c_i - q1 d_(i-1) - q0 d_i`. Then
     `(c, d)` is proportional to `[[Q, 1], [beta^(t+1), 0]] (d, e)`.
  5. `M2 = hgcd(d, e, k - d1 - t)` on the compacted top parts of `d` and `e`. It writes its output over its own inputs, which it
     no longer reads by then.
  6. Return `M1 [[Q, 1], [beta^(t+1), 0]] M2`. The product is formed on two rows of `2^(j-1)` points (entries of degree `<= k`).
     Below the top level the transforms of `M1`'s entries on these two rows are kept from step 2 (they are rows `Y - 1`, `Y + 1`
     there too), and the product is `M1 ([[Q, 1], [beta^(t+1), 0]] M2)`. This saves the four transforms of the left factor.
* Driver (`hg_gcd`): while `deg b >= 0`, take `k = 2^j - 1 <= min(131071, deg a / 2)` and set `M = hgcd(a, b, k)`. Apply
  `adj(M)` to the full `(a, b)` in place (rows as in step 2, on `3 * 2^(l-2)` or `2^l` points), then make one pseudo-division and
  shift `(a, b) := (b, e)`. Below degree 96, Euclid's algorithm runs to the end. Finally the last nonzero remainder is made monic
  (one inversion). The bound 131071 keeps the arena of stage D within the two buffers freed after stage C (`2n` words, with
  `g` and `kappa (R - 1)` in the other two): the measured peak of the arena was 1,835,076 words (section 7).
* Abnormal quotients (degree `> 1`, or degree gaps) are handled by the general pseudo-division and wider matrix slots. They do not
  occur in this run.

### 4.7 Stages E to I

For `deg G = 1` (this run), `S = -G_0`. Stage F computes `s` by Tonelli-Shanks. It forms the two line points and maps them back
with three exponentiations each (`tau = W^e`, `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), all charged per operation. Stage G calls
the reference permutation (rounds 0-3, 4-6, 60-63 on `[nk, rho, 2^65]`) for both pairs and compares. Stage H encodes six values in
hexadecimal (one conversion and 12 operations per digit). Stage I charges the fixed bounds of 4.2, then formats the report, writes
it once and exits.

## 5. Why the output is a collision

By sections 2-3, a root `S` of `G` is a nonzero square root of `g_c`, so `s = sqrt(S) != 0` satisfies `F(c + s) = F(c - s)` with
`c + s != c - s`. The two canonical pairs differ and have the same digest. Stage G recomputes both digests with the full reference
permutation, and the program reports success only if they are equal and the pairs differ. Independently of the program, the pair in
`certificates/` matches the organizer's hash (`verifier/poseidon.py`, r = 3): digest `ec121f2a554ea528faa3a1af74fbe603ca9fc80e942ef88ac220fe46c9655132` (as 32 little-endian bytes;
the field element `0x325165c946fe20c28af82e940ec89fca03e6fb74afa1a3fa28a54e552a1f12ec`).

### 5.1 The certificate lies on the line, with midpoint 1

The certificate inputs are `nk1 = 0x0499f5c4354bafa11ca451e656d380d078444ed6561d6355487453741e1a6815`, `rho1 = 0x21625d728b86cf0865d7ad7cd99a0c20464939e5253940d95b3a639d7a909af7`,
`nk2 = 0x1009050c8c1414cf5975db612457a2e49b06db64fce28c7dd5ad52ed8fc2c567`, `rho2 = 0x31611cd777dc6c418e048d96a497f46fa51523b47dbadcd97d0ad171160fcdb8` (canonical, encoded little-endian in the .bin files). From the certificate alone (no run needed): with `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, the point `(U, V)` must equal
`Q + tau (a, b)`, and `W = tau^5`. With the constants of section 2 (computed by `line_setup`):

```
U_Q = 0x2de17246e844b000296eefaaf2116b9705e3af63806d80541c7d6b4be442036c
V_Q = 0x2622542e119aef1f7c021664aae329063a3e73651cd62e02756427f9437fdd96
a   = 0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e
b   = 0x354a1a478b5972184c2a60423736152b8a6ef850e5c7edc566ee0c66281ee49e
pair 1: tau1 = (U1 - U_Q)/a = (V1 - V_Q)/b = 0x39c88e1ed227ad8dcafe20885fb4be613a0069d62f625555fa63ab5982b6177a
        W1 = tau1^5 = 0x0febb7461f9c538f59555ab53d844978c2bd79eab44dab4671542236627b497e
pair 2: tau2 = 0x227346ab9e35c250e4d8f690c6d52e98d5ab3c79620151b886a51afaa9be825b
        W2 = tau2^5 = 0x301448b9e063ac70a6aaa54ac27bb6875f891f1154ff4dd527d90eb69d84b685
W1 + W2 = 2,  s = (W1 - W2)/2 = 0x0febb7461f9c538f59555ab53d844978c2bd79eab44dab4671542236627b497d,  S = s^2 = 0x38b28f42d94fae9ec4fdb974c8927999bdf6ef6f3befec643f97d804676d1235
```

So both pairs lie on the line (the two expressions for `tau` agree) and their midpoint is `c = (W1 + W2)/2 = 1`; hence `S` is a
nonzero square root of `g_1`, `deg G >= 1` at `c = 1`, and the deterministic procedure succeeds in trial 1. That `deg G = 1`
exactly (so that stage E needs no splitting) is an outcome of the run, not something the certificate shows. A judge can recompute these with a few lines of big-integer arithmetic from the organizer
constants.

## 6. Ledger: the executed run (primitive operations; `C(3) = 279`)

The counts below are the counters of one execution of the source of section 9, built with
`gcc -Os -march=native -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -fno-tree-loop-distribute-patterns -o single main.c hgcd.c stageb.c stagec.c line.c ntt.c fp.c nolibc.c` and run as `single 3` under a 64 KiB stack limit. Nothing is extrapolated or taken from another run. The program prints
the total of the stage rows, the counters of the whole run and the sum of the trial rows, plus `RECONCILE ok=1` (stage rows equal
the counters). `arith` = additions, subtractions, multiplications and squarings; `control` includes the address operation of every
load and store; `units` counts the line evaluations and reference hashes, each charged 279 in `total`.

| stage | arith | loads | stores | control | units (x279) | total |
|---|---:|---:|---:|---:|---:|---:|
| init: twiddle tables, stage C constants (once) | 3,144 | 3,070 | 3,085 | 40,713 | 0 | 50,012 |
| setup: the line (once) | 410 | 44 | 10 | 1,716 | 0 | 2,180 |
| A: centre | 1 | 0 | 0 | 126 | 0 | 127 |
| B: 2^21 line evaluations, values of g_c on H_20 | 6,291,456 | 0 | 1,048,576 | 15,728,742 | 2,097,152 | 608,174,182 |
| prep: coefficients and checks, Newton series inverse, start residue, Gi, G2 | 164,429,643 | 51,473,135 | 44,917,353 | 211,760,799 | 0 | 472,580,930 |
| C: S^((p-1)/2) mod g, 237 steps | 31,797,536,829 | 7,488,328,500 | 6,247,415,808 | 21,228,202,918 | 0 | 66,761,484,055 |
| D: half-gcd of (g, kappa (R - 1)) | 5,740,319,601 | 2,347,096,087 | 1,670,619,757 | 10,110,307,542 | 0 | 19,868,342,987 |
| E: root of G | 1 | 3 | 2 | 119 | 0 | 125 |
| F: square root, back-map | 3,071 | 12 | 0 | 13,430 | 0 | 16,513 |
| G: two reference hashes | 0 | 0 | 0 | 135 | 2 | 693 |
| H: encoding of the output | 6 | 0 | 0 | 4,846 | 0 | 4,852 |
| I: report (bounds), write, exit | 0 | 0 | 0 | 3,382,436 | 0 | 3,382,436 |
| **total N** | | | | | | **87,714,039,092** |

| trial | centre | deg G | stage-D arena peak (words) | charge of the trial |
|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 1,835,076 | 87,710,599,507 |
| outside the trials (init, setup, H, I, and the closing bookkeeping of the trial loop) | | | | 3,439,585 |

The trial charge is read from the counters at the end of the trial, before the trial loop's exit test and the stage switch to H
(105 operations: `STAGE_BK` + `LOOPC(1)`), which are attributed to stage G's row in the stage table and to "outside" here; both
tables sum to `N`.

`N = 87,714,039,092` operations `= 314,387,236.9` units, `log2(N / 279) = 28.227967`, claimed as `28.22797` (rounded up).

Stage C in detail: 237 steps of the loop. Each step is two bottom passes, two top passes and 20 radix-8/4 passes of `2^20`
elements, and stage C as a whole averages 2.817e+08 operations per step (1.342e+08 field operations and 5.796e+07 loads and stores per step). Stage D breakdown (reporting-only profile of the same
run): base cases 1,252,823,840, applies inside hgcd 8,593,136,413, applies of the driver 2,732,853,883, matrix products 6,272,813,818 (the rest: divisions, compaction, degree scans, allocation).

### 6.1 Ledger recomputation

```python
from math import log2, ceil
stages = [50012, 2180, 127, 608174182, 472580930, 66761484055, 19868342987, 125, 16513, 693, 4852, 3382436]   # init, setup, A, B, prep, C, D, E, F, G, H, I
N = sum(stages)
assert N == 87714039092
t = log2(N / 279)
print(N, round(N / 279, 1), t, ceil(t * 1e5) / 1e5)
mem = 134473813
print(mem, log2(mem), ceil(log2(mem) * 1e4) / 1e4)
```

## 7. Memory

The executable is linked statically without any C library (`nolibc.c` supplies the process entry, the two system calls and
`memcpy`/`memset`/`memmove`/`memcmp`). Its whole loadable image, from `size`: text 82,257 + data 4 + bss 134,326,016 = 134,408,277
bytes. The bss contains every buffer of the run:
* the static region `REG` of `4n = 4,194,304` words (134,217,728 bytes). Stages B, prep and C use its four quarters as the
  buffers of 4.4-4.5. Stage D keeps `g` and `kappa (R - 1)` in two quarters and uses the other two (2,097,152 words) as its stack
  arena; the measured arena peak was 1,835,076 words;
* the twiddle tables `TA` (2,048 words) and `TB` (1,024 words);
* the 8,192-byte output buffer and the small static state.

Nothing is mapped from the kernel at run time (no `mmap`, no `brk`). The stack bound is 65,536 bytes: the run was executed under a
64 KiB stack limit (`RLIMIT_STACK`). Total: 134,408,277 + 65,536 = 134,473,813 bytes `= 2^27.002750`, claimed as `27.0028`
(rounded up). The measured peak resident set of the run (`ru_maxrss` of the child) was 134,217,728 bytes, below the counted
figure (the kernel's resident-set counters are batched, so this is a sanity check, not a tight measurement; the figure claimed
is the image plus the stack bound). The memory penalty is `7.0028`; normalized cost `28.22797 + 7.0028 = 35.23077`.

## 8. Testing, what is and is not provided, reproduction

* Provided: the derivation (sections 2-3), the algorithm and its charging (4), the ledger of the executed run (6), the memory (7),
  the complete source (9) and the collision certificate (`certificates/`, checked by the organizer's hash).
* Supporting tests (not part of the claim; run during development with the same source): the transforms were checked against
  naive evaluation for all sizes up to `2^10` and random node offsets. Stage B + prep + C were checked against FLINT
  (`S^((p-1)/2) mod g_c` with `pow_mod`) at r = 0 (`m = 7812`) and r = 1 (`m = 39062`). Stage D was checked against FLINT's gcd on
  random pairs, pairs with common factors of degree 3 and `n/4`, low-degree second inputs, forced degree gaps and sparse inputs
  (abnormal quotients), at degrees 50-9000, under AddressSanitizer and UBSan. The whole program found collisions at r = 0, 1 and 2
  as well.
* No Python experiment is declared. The run's counts come from the instrumentation written into the source. The organizer did not
  run the program, so the counts rest on the shipped source.
* The cost claim assumes the model of 4.2. Costs outside it (cache, bandwidth) are not part of it.
* Reproduction on one core: build with the command of section 6 (the counted run used gcc (GCC) 16.2.1 20260810 on Linux 7.2.8-arch1-2 x86_64, CPU 11th Gen Intel(R) Core(TM) i7-1185G7 @ 3.00GHz) and run
  `single 3` under a 64 KiB stack limit. It reproduces every count of section 6 and prints the collision (about 907 s on that machine). `consts.h` is
  generated by `python3 -I gen_consts.py <pareto/orchard-pallas-constants.json> > consts.h`.

## 9. Complete source of the instrumented program

Files: `fp.h`, `fp.c` (field and counters), `consts.h` (generated by `gen_consts.py`), `ntt.h`, `ntt.c` (transforms), `line.h`,
`line.c` (the line, line evaluation, back-map, reference hash), `stageb.h`, `stageb.c` (stage B and prep), `stagec.h`, `stagec.c`
(stage C), `hgcd.h`, `hgcd.c` (stage D), `main.c` (trial loop, stages E-I, report), `nolibc.c` (entry, system calls), `gen_consts.py`.
SHA-256 of each file is listed with it.

### fp.h

SHA-256 `a973f9ee2f7c29cd0b16a39e2b6677e8934ad5255f1b6ae8aeed3d7da32d83a0`, 4361 bytes.

```c
/* Pallas field arithmetic in Montgomery form, and the operation counters of the cost model.
 *
 * Every field addition, subtraction, multiplication and squaring increments its counter.  Loads and stores of 256-bit array
 * elements are charged by LD/ST at the statement that executes them, each with one address operation (control).  Loops are
 * charged LOOPC(n) = 3n + 2 control operations (index update, comparison, branch per iteration, and the exit test) unless a
 * different count is written next to them.  CTL(k) charges k other executed integer operations. */
#ifndef FP_H
#define FP_H
#include <stdint.h>
#include <stddef.h>

typedef unsigned __int128 u128;
typedef struct { uint64_t v[4]; } fp;

struct ctr { uint64_t add, sub, mul, sqr, ld, st, ctl, unit; };
extern struct ctr X;

#define LD(n)    (X.ld += (uint64_t)(n), X.ctl += (uint64_t)(n))
#define ST(n)    (X.st += (uint64_t)(n), X.ctl += (uint64_t)(n))
#define CTL(n)   (X.ctl += (uint64_t)(n))
#define LOOPC(n) (X.ctl += 3 * (uint64_t)(n) + 2)

static inline uint64_t ctr_total(const struct ctr *c)
{
    return c->add + c->sub + c->mul + c->sqr + c->ld + c->st + c->ctl + c->unit;
}

#include "consts.h"

static const fp FP_P = {P_LIMBS};
static const fp FP_ONE = {ONE_LIMBS};
static const fp FP_ZERO = {{0, 0, 0, 0}};

/** Return 1 if a >= b as 256-bit integers. */
static inline int ge256(const fp *a, const fp *b)
{
    for (int i = 3; i >= 0; i--) {
        if (a->v[i] != b->v[i]) return a->v[i] > b->v[i];
    }
    return 1;
}

/** Return a - b mod 2^256 and set *borrow. */
static inline fp sub256(fp a, fp b, uint64_t *borrow)
{
    fp r;
    uint64_t br = 0;
    for (int i = 0; i < 4; i++) {
        u128 t = (u128)a.v[i] - b.v[i] - br;
        r.v[i] = (uint64_t)t;
        br = (uint64_t)(t >> 64) & 1;
    }
    *borrow = br;
    return r;
}

/** Return a + b mod 2^256 (no overflow occurs for canonical inputs since p < 2^255). */
static inline fp add256(fp a, fp b)
{
    fp r;
    uint64_t c = 0;
    for (int i = 0; i < 4; i++) {
        u128 t = (u128)a.v[i] + b.v[i] + c;
        r.v[i] = (uint64_t)t;
        c = (uint64_t)(t >> 64);
    }
    return r;
}

/** Montgomery product a*b/2^256 mod p of canonical inputs, canonical output; not counted. */
static inline fp mont_raw(fp a, fp b)
{
    static const uint64_t q[4] = P_LIMBS;
    uint64_t t[4] = {0, 0, 0, 0};
    for (int i = 0; i < 4; i++) {
        u128 A = (u128)a.v[0] * b.v[i] + t[0];
        t[0] = (uint64_t)A;
        A >>= 64;
        uint64_t m = t[0] * P_INV;
        u128 C = ((u128)m * q[0] + t[0]) >> 64;
        for (int j = 1; j < 4; j++) {
            A = (u128)a.v[j] * b.v[i] + t[j] + (uint64_t)A;
            t[j] = (uint64_t)A;
            A >>= 64;
            C = (u128)m * q[j] + t[j] + (uint64_t)C;
            t[j - 1] = (uint64_t)C;
            C >>= 64;
        }
        t[3] = (uint64_t)C + (uint64_t)A;
    }
    fp r = {{t[0], t[1], t[2], t[3]}};
    if (ge256(&r, &FP_P)) {
        uint64_t br;
        r = sub256(r, FP_P, &br);
    }
    return r;
}

/** Return a + b mod p (one field addition). */
static inline fp fp_add(fp a, fp b)
{
    X.add++;
    fp r = add256(a, b);
    if (ge256(&r, &FP_P)) {
        uint64_t br;
        r = sub256(r, FP_P, &br);
    }
    return r;
}

/** Return a - b mod p (one field subtraction). */
static inline fp fp_sub(fp a, fp b)
{
    X.sub++;
    uint64_t br;
    fp r = sub256(a, b, &br);
    if (br) r = add256(r, FP_P);
    return r;
}

/** Return -a mod p (charged as one subtraction 0 - a). */
static inline fp fp_neg(fp a) { return fp_sub(FP_ZERO, a); }

/** Return a * b mod p in Montgomery form (one field multiplication). */
static inline fp fp_mul(fp a, fp b)
{
    X.mul++;
    return mont_raw(a, b);
}

/** Return a^2 mod p (one field squaring). */
static inline fp fp_sqr(fp a)
{
    X.sqr++;
    return mont_raw(a, a);
}

/** Return 1 if a == b (one comparison and branch: 2 control operations). */
static inline int fp_eq(fp a, fp b)
{
    CTL(2);
    return a.v[0] == b.v[0] && a.v[1] == b.v[1] && a.v[2] == b.v[2] && a.v[3] == b.v[3];
}

/** Return 1 if a == 0 (2 control operations). */
static inline int fp_is0(fp a) { return fp_eq(a, FP_ZERO); }

fp fp_pow(fp a, const uint64_t e[4]);
fp fp_inv(fp a);
fp fp_from_u64(uint64_t x);
fp fp_from_limbs(const uint64_t l[4]);
void fp_to_limbs(fp a, uint64_t l[4]);
#endif
```

### fp.c

SHA-256 `c2437ab3d1cb80e9d792e3c372fa704f23efd85a560efc027db14ff8a19a0aeb`, 1701 bytes.

```c
/* Exponentiation, inversion and conversions (all charged by their constituent operations). */
#include "fp.h"

struct ctr X;

static const fp FP_R2 = {R2_LIMBS};

/** Return a^e for a 256-bit exponent e (little-endian limbs), left-to-right binary method.
 *  Charged: one squaring per bit below the top bit, one multiplication per further set bit, and per bit 6 control
 *  operations (loop update/compare/branch, word select, shift, bit test). */
fp fp_pow(fp a, const uint64_t e[4])
{
    int top = 255;
    while (top >= 0 && !((e[top >> 6] >> (top & 63)) & 1)) {
        top--;
        CTL(6);
    }
    CTL(8);
    if (top < 0) return FP_ONE;
    fp r = a;
    for (int i = top - 1; i >= 0; i--) {
        r = fp_sqr(r);
        CTL(6);
        if ((e[i >> 6] >> (i & 63)) & 1) r = fp_mul(r, a);
    }
    CTL(2);
    return r;
}

/** Return a^(p-2) = 1/a for a != 0 (0 for a = 0). */
fp fp_inv(fp a)
{
    static const uint64_t pm2[4] = {0x992d30ecffffffffULL, 0x224698fc094cf91bULL, 0, 0x4000000000000000ULL};
    return fp_pow(a, pm2);
}

/** Return the field element with canonical integer value given by limbs (< p); one multiplication by 2^512 mod p. */
fp fp_from_limbs(const uint64_t l[4])
{
    fp a = {{l[0], l[1], l[2], l[3]}};
    return fp_mul(a, FP_R2);
}

/** Return the field element with integer value x. */
fp fp_from_u64(uint64_t x)
{
    uint64_t l[4] = {x, 0, 0, 0};
    return fp_from_limbs(l);
}

/** Write the canonical integer value of a into l (one multiplication by 1, four word stores and their loop: 18). */
void fp_to_limbs(fp a, uint64_t l[4])
{
    fp one = {{1, 0, 0, 0}};
    fp r = fp_mul(a, one);
    for (int i = 0; i < 4; i++) l[i] = r.v[i];
    CTL(18);
}
```

### consts.h

SHA-256 `f8ac2e0dc8a97e255a690fa0f400369a27459aed4e6e30e38c6ad7114d505d64`, 20557 bytes.

```c
/* generated by gen_consts.py from zcash/halo2 halo2_poseidon-0.2.0 halo2_poseidon/src/fp.rs (sha of the source json is checked by the caller) */
#ifndef CONSTS_H
#define CONSTS_H
#define P_LIMBS {0x992d30ed00000001ULL, 0x224698fc094cf91bULL, 0x0000000000000000ULL, 0x4000000000000000ULL}
#define P_INV 0x992d30ecffffffffULL /* -p^-1 mod 2^64 */
#define R2_LIMBS {0x8c78ecb30000000fULL, 0xd7d30dbd8b0de0e7ULL, 0x7797a99bc3c95d18ULL, 0x096d41af7b9cb714ULL} /* 2^512 mod p */
#define ONE_LIMBS {0x34786d38fffffffdULL, 0x992c350be41914adULL, 0xffffffffffffffffULL, 0x3fffffffffffffffULL} /* Montgomery form of 1 */
#define TREE_K 21
#define TA_BITS 11
#define PSI_LIMBS {0x9de6f8ca42c3897fULL, 0x542570ce4b202debULL, 0x084cdceadcc46158ULL, 0x287055b2299467f6ULL} /* Montgomery form of psi = 5^((p-1)/2^K) */
#define PSI_INV_LIMBS {0x502d922a860e0248ULL, 0x9aede8c2164e94aeULL, 0xc5413491910138a4ULL, 0x05cfd8e66c406bcfULL}
static const fp RC[64][3] = {
  {{{0x2d6110568f8fb1cdULL, 0xe436f09787ae5fc6ULL, 0x51ea32d50f7be93fULL, 0x3ee3b205efa6ab5dULL}}, {{0x5564975171925a88ULL, 0x4ccc244f2b4cee87ULL, 0xa473a9e22140ab94ULL, 0x293983c6cd66b132ULL}}, {{0x1650a1e8d6eb3b9dULL, 0xe1d084ae973c80a4ULL, 0xc6b0e48a821b7324ULL, 0x26f40bdecf47ed19ULL}}},
  {{{0xc6687b9c41161a23ULL, 0x7132cacb8362ca7aULL, 0xd85a41c272c6bbb5ULL, 0x201e196e95c1d5a7ULL}}, {{0xfac81e29844529d7ULL, 0x55cd21dd6e3519aaULL, 0xdac6e75068b2d6e6ULL, 0x1db160cfe68f1791ULL}}, {{0xd0380768fd7d233eULL, 0x1e9be9783f636613ULL, 0x072a39e85b32c9c0ULL, 0x12451bc216857272ULL}}},
  {{{0x28238cb2f9610a03ULL, 0xa5bf3dbbb71c1a95ULL, 0xcfa2634c3dcdc1cfULL, 0x30d475d91c9d2660ULL}}, {{0xe54edcbe9506d50dULL, 0x6336d456820cd730ULL, 0x62f946f09a61cd4cULL, 0x3dbf6a7660d1c1f2ULL}}, {{0xa1f0f09ab6b52ec7ULL, 0xa0256009a9a655c0ULL, 0x02d87cd8131e6863ULL, 0x1d82928e0581f03dULL}}},
  {{{0xd40988e46aa0d84aULL, 0xcb83b98a6c3311b6ULL, 0x1faecd3d4f5ba6feULL, 0x21816a2ace1e6ceeULL}}, {{0x12966345b9eb55e6ULL, 0xe7207d68cede2273ULL, 0xc5e2cfe134e17a59ULL, 0x3b77812fa31cbea0ULL}}, {{0x7c6cf91aa5ec91b8ULL, 0x788439799fc5e819ULL, 0x420b62303e699297ULL, 0x03cf4743b88562d7ULL}}},
  {{{0x62a23ec7246945beULL, 0xf0ce22ea72865fbdULL, 0x656887c5d7179774ULL, 0x0387c6accf862ddbULL}}, {{0x3a8498acade3e889ULL, 0x11837e2c04524a39ULL, 0x1d734b9714471abcULL, 0x123cb78b6fa1e7f0ULL}}, {{0xd9e655459801f98aULL, 0xfc579cc290c7c6f9ULL, 0x2027d70ac2d2c545ULL, 0x347d84f327297c50ULL}}},
  {{{0x0c514cbe25cd5dceULL, 0xecce789089b36388ULL, 0xe8ae18e6cf5c2d28ULL, 0x09508b80b79c153cULL}}, {{0xf1c79b4f210c1577ULL, 0x39d1fa61fe64ebd8ULL, 0xb8d92fd604863955ULL, 0x16356b23d117fcf8ULL}}, {{0x075b151491dd1191ULL, 0x61dc8c496394e6dbULL, 0x3db07ac8572c1d58ULL, 0x0cd7d3fd2c41152eULL}}},
  {{{0xf2f6633139c4b05eULL, 0x01dbcb2916c3253dULL, 0xf1172b5fa58201e9ULL, 0x16ce288f5de472a7ULL}}, {{0x74b411041f0f061bULL, 0x119ca91c82f60867ULL, 0x88a45446cea98b5fULL, 0x3f947ecf9f672579ULL}}, {{0x9bc2a35b9de62d46ULL, 0x040c50a583d292a1ULL, 0x1f62387715c339a0ULL, 0x2b0e1ed4a55c9b51ULL}}},
  {{{0x0988c91b9e85fef9ULL, 0xe8ad133faa5d1bcdULL, 0xd8df562e7b09d6efULL, 0x0ce401a7279eeb38ULL}}, {{0xc4dfd87b16cb67c7ULL, 0x63d16458323b64bcULL, 0xc8c653cf8e63bcccULL, 0x11242b4450a3daa4ULL}}, {{0x6768a64cd32ee7f7ULL, 0xc2e49f96bbd21fb0ULL, 0x97aae974ebac14cbULL, 0x01d1a1069ea732f8ULL}}},
  {{{0xd11a4d50cdf5c831ULL, 0xf0141a1730a04151ULL, 0x4839556e137af540ULL, 0x337fc238de198aacULL}}, {{0x65126e84b58b3ba7ULL, 0xc8d56c47b3b29eeeULL, 0x8f7755c67ad08f38ULL, 0x032b374daf0f5daeULL}}, {{0x03c37d36570461bdULL, 0xf7af83659d08e8f8ULL, 0x5ab5a972d3ed3a2cULL, 0x3ea0dc7d347f4499ULL}}},
  {{{0x6c9388c1bf9426b6ULL, 0x6ef2023f27f48878ULL, 0x4858081b3f9d5fc7ULL, 0x022a53a4a03a61b2ULL}}, {{0x8d8bbf6d29f2c488ULL, 0xf1fb6efb14f6c308ULL, 0x12566c68cdf47685ULL, 0x2874c6e0c2f51250ULL}}, {{0x0cbd4d8959832848ULL, 0x0be4c3aaeae1eec8ULL, 0x8ff6a34de0e0041bULL, 0x35a497e0ae1c0c6fULL}}},
  {{{0xf265123421944696ULL, 0x58c83e93fd718498ULL, 0xf5d679bbfa9b691dULL, 0x16394bccd2d2fddaULL}}, {{0x6b0b7673c8d01fe1ULL, 0x43d92fddf33b2e84ULL, 0xc2c2fb35e711d5baULL, 0x3310e80bcf0c079cULL}}, {{0xba2001a87d410461ULL, 0x92db1732f98ac5bfULL, 0x46b53d2f258b21a0ULL, 0x2431dc11acaf9487ULL}}},
  {{{0x4e5eac0c7809dac9ULL, 0x88d278a88757b06dULL, 0xb1caa105e8cfd525ULL, 0x38c5e465b0998789ULL}}, {{0x8d582cd16028d0b6ULL, 0x02f5f6f2049341fbULL, 0x14da884cd65b6d4cULL, 0x175b5e71ccbd92ccULL}}, {{0x7a4f279b84faae3fULL, 0xdc9cf712aa7020eaULL, 0xd282adb6f153c7ceULL, 0x3dc87f51bee14157ULL}}},
  {{{0x54cf83685b98d9ecULL, 0xf982055b2e3f539fULL, 0xa9150eebebecca51ULL, 0x101de276dcdc3feaULL}}, {{0x07ff3281e556dffaULL, 0x8e411f5f9f08c47aULL, 0x901151014e2336c7ULL, 0x051670efbebe0450ULL}}, {{0x9e49643f069395b7ULL, 0x28bf9db3e38928cdULL, 0x8c02c832008df673ULL, 0x079d4a1265f1f9b8ULL}}},
  {{{0x174d2c5549935069ULL, 0xf449d64ba7afd980ULL, 0x17489be3cbeb8217ULL, 0x3dde70f1a49ecc6cULL}}, {{0x7dfd80ab7fad4deeULL, 0x8f7d70f1057b7365ULL, 0x432c8e8ae0ea2f2dULL, 0x21a4f21cbad39e96ULL}}, {{0x97383a22729d1abaULL, 0x4120a9e5df48c0aeULL, 0x0ac4c5efc2eedad4ULL, 0x1b96fd1670bdf887ULL}}},
  {{{0x663798be9e2ca816ULL, 0x74a1d330e5c2746dULL, 0xaf106b2043e0b1cdULL, 0x1d3b129ea32c0690ULL}}, {{0x623d1657253b3822ULL, 0xde6cd3acc6c1e3daULL, 0x1bbcb5725404e77dULL, 0x1555343383b9e912ULL}}, {{0x5e942b15b6542262ULL, 0x99c8b631c5e985c4ULL, 0x22cd0b12f24838eaULL, 0x342e25680ac0f457ULL}}},
  {{{0xacee1be8258f1974ULL, 0x330f1daa7a0a82d3ULL, 0x30cf05803e57f42fULL, 0x05af97ff16360de2ULL}}, {{0xf60d13bc70fb7261ULL, 0x89323aa335da65e0ULL, 0xa230cf39306ada27ULL, 0x37ec8d60f94c0e00ULL}}, {{0x77cb61b22f0fef36ULL, 0x97b9c176aa4f29dcULL, 0x753951ba534b64ccULL, 0x39d864f4db0d66e5ULL}}},
  {{{0x1c93a280de7e6390ULL, 0x89bbe99192d5942bULL, 0xd298630838ac97b4ULL, 0x1fdee9515ec23733ULL}}, {{0x1b1500ea3ea52e7cULL, 0xab66b5200e504be8ULL, 0xf2ca2fc2dd1238ceULL, 0x2e99ac0058887a8eULL}}, {{0x797a75c017355c08ULL, 0x95753d5fbfe4b639ULL, 0x99d90146a1022ee1ULL, 0x18c6c282437c0106ULL}}},
  {{{0x28c41cb0f6a427aaULL, 0x7a6274209547e747ULL, 0x409958bab0ce8004ULL, 0x0f5c9a21669c3561ULL}}, {{0x4f458041d5a49e9aULL, 0x70bf9be212724995ULL, 0x16bb868a425b1357ULL, 0x11bbfdbd72e6c273ULL}}, {{0x840d988bb266eb39ULL, 0x32ee4645ac430194ULL, 0xdf94525d6b695073ULL, 0x26f7032e169d741eULL}}},
  {{{0xed032a7242155f1cULL, 0xd3bf87a6d0fc1c34ULL, 0x6e6b7f2bba883e7aULL, 0x03bee947acf8d869ULL}}, {{0x54124791da75f84cULL, 0xdea3fdd86d09154cULL, 0xa8b1b78ee689124bULL, 0x08cc569a704f8ae7ULL}}, {{0x16e420feed279927ULL, 0xd4e9f90a2430cadeULL, 0xbda76f8c724ed3c4ULL, 0x26f0c2eb7941a2edULL}}},
  {{{0xfa8bcd50c49a6dc1ULL, 0x1b75bef3f3b40443ULL, 0x16306d7f83e6e86fULL, 0x2cb265185a682f74ULL}}, {{0x816198532054502fULL, 0xa53e572f12c3401fULL, 0xe9a8f617740903c3ULL, 0x2c9ba61ca6f41275ULL}}, {{0xf5b6a307021d72c4ULL, 0xf9b09e3b204957faULL, 0x1ef85c62ca5473eeULL, 0x0efc66dcec9a30aeULL}}},
  {{{0x005b369d1ddec201ULL, 0x1a842b0d7196bbe6ULL, 0x737adf896a50cea4ULL, 0x236df79cb9f4188bULL}}, {{0xea5b61d7bd606ab0ULL, 0xccb039d4615a540eULL, 0x1408af70b00d1a59ULL, 0x225863cd3b10bb9dULL}}, {{0x6cb2f4bcc26de564ULL, 0xbb358e5aee7406abULL, 0xf08ffcbb81863becULL, 0x00f144f53402205fULL}}},
  {{{0x47dac6922bd0e686ULL, 0x7d618f7ba9d32c8eULL, 0x6118919ff121628cULL, 0x074faa94927b7786ULL}}, {{0x3af193a3ff7b9d4dULL, 0x5b4be86fcf9052b0ULL, 0xa9433b495aa64416ULL, 0x041c30de6dcc571eULL}}, {{0x3d90f898029f92e2ULL, 0xfcbb9e4743c48e1dULL, 0x20bc4ddedcf505afULL, 0x0ce8a49fa10949e7ULL}}},
  {{{0x6bb524c3db961189ULL, 0xe93f7a4d2c5cd069ULL, 0xc7c572085a58c1f2ULL, 0x157be04d9af4f4b7ULL}}, {{0xcce74e4ac292398dULL, 0xaed371d912fb1d56ULL, 0x356e0c2dbf7bc066ULL, 0x3514dcf22466a19fULL}}, {{0xfd1e5928b50de13cULL, 0x00f1d7fb3cb6d5ffULL, 0xfe3bd8a8f595d931ULL, 0x2aef30e01461acebULL}}},
  {{{0xa86cd7f133554ebbULL, 0x094a97d9d8908309ULL, 0x3de9cf716c0e5531ULL, 0x2a215295d3b86a1cULL}}, {{0xd53c009bb1e61c5cULL, 0xfb9b2a40c066fa76ULL, 0xfc69157a958ea7d9ULL, 0x2a396665f94e134fULL}}, {{0xf86e48d38ebb1402ULL, 0x06e4f55e6bfb3e89ULL, 0x16bf492bbf874eb3ULL, 0x335d71a30027eccdULL}}},
  {{{0x1e4bb73ffb93a6d1ULL, 0x9ef465a03f553915ULL, 0xa986466f8cb39340ULL, 0x344b522709d83fd6ULL}}, {{0x54d1385a73cedc14ULL, 0x554f9d50f1aa4237ULL, 0x6c40c2c46e70eb08ULL, 0x08d14481b53d311cULL}}, {{0x1424438d34dfc1daULL, 0x2409171b46a1ca37ULL, 0x1a1c4cfb701efcc3ULL, 0x3238d087fe0f487bULL}}},
  {{{0xe4e41151ef95cfa8ULL, 0x5ac9a18bf328f9a7ULL, 0xa74bc957b4f0312fULL, 0x2a7229e81bd17e27ULL}}, {{0x128b64e508a63bd9ULL, 0xbc72e63f546c4584ULL, 0x88cf7accb6e0e0eeULL, 0x113c3d59a596d700ULL}}, {{0xf4d7b2de93df79c1ULL, 0xd48511fd9b630fa2ULL, 0x66d2195a8ed94ca5ULL, 0x1c0c0ca45eee2c44ULL}}},
  {{{0x466d86d03c2466caULL, 0x8227a59ab7462664ULL, 0xd2fd28964ffc5f0eULL, 0x047b0867cd0bb8bcULL}}, {{0xd789d21c1d4ea83cULL, 0x7401f29ebae79841ULL, 0xe0abd0eb46b46cb8ULL, 0x28e0786cd4de5a8fULL}}, {{0x7402eeab3141e20fULL, 0xd768b71e6068c79bULL, 0x3db2195fe3a15590ULL, 0x2ae0bdb635468021ULL}}},
  {{{0xc16e17aec4c8c257ULL, 0xcbe2e0daf07542ffULL, 0xbfe62521350c02fbULL, 0x1228614aa1224324ULL}}, {{0x75e7f93077ae107aULL, 0x4393dd80790be351ULL, 0xdff377ea2fa44416ULL, 0x1e8508e864d3a7c5ULL}}, {{0xb1ec20078a1957fdULL, 0x763ab46a70baa519ULL, 0x7738685a419fd1cbULL, 0x2a5e0a5a9db64745ULL}}},
  {{{0xc22212c67483d82eULL, 0xa75cc24295d6ff8dULL, 0x7992eb54a6a2ed5dULL, 0x07404560d0b2cbd5ULL}}, {{0x2a285911ee339ba5ULL, 0x8893e0badb13c939ULL, 0xd83525d7431b9b62ULL, 0x25f63b980e96e6dbULL}}, {{0xa15a39ed0b3d0589ULL, 0xd368b459a4b900e0ULL, 0x4efa56d549364219ULL, 0x0b5ca2beedd7dd3eULL}}},
  {{{0xeb7ba4127d2e6354ULL, 0x6986145a2941fb14ULL, 0x0e3e7c6c97a14312ULL, 0x1ed53f1aa1bf808fULL}}, {{0xaf8ab4c0d2b2669dULL, 0x7e7a7326eb971e3fULL, 0xa2d3848e9ce2fc69ULL, 0x29ea52e7093a43d4ULL}}, {{0x1e72622bdb4569a9ULL, 0x874356996d93fcdeULL, 0x5c7c464758b32bc2ULL, 0x105fe2acbcc84897ULL}}},
  {{{0x0653a67e86f62c0fULL, 0xda058f0b6767498aULL, 0xa49ef164a0280442ULL, 0x348a3f44e29a1db3ULL}}, {{0x4ebc09df098dddf4ULL, 0x7953e2582fc1806cULL, 0x4c7c4749054887c8ULL, 0x0ea7f29878781fb8ULL}}, {{0x9e9e28ff373a00a1ULL, 0x59d68a2c32f0aeaeULL, 0x030aa50eb0d116f4ULL, 0x265063100e234ee0ULL}}},
  {{{0xc65436d24cba466aULL, 0x461c6791d1c4df7bULL, 0x44a880f485ffa101ULL, 0x3fbc3cf75118c62eULL}}, {{0xd77ac655ca67b1c2ULL, 0x76d88fda6b1d115cULL, 0x089c758c1ba6ef20ULL, 0x0964db39bd4b200bULL}}, {{0xbd5667e04c034a11ULL, 0x5d4c63fffa29c3a1ULL, 0xf6831d76df36eaa1ULL, 0x255644c108880d6dULL}}},
  {{{0xafa80ea9d8392946ULL, 0xb374fe3c3d852b90ULL, 0x6ac7be0421200289ULL, 0x20e4c096c4dd72e6ULL}}, {{0x7896f449e943831eULL, 0x1ce40ea3c4383e92ULL, 0xb49ab8f65a18dfb3ULL, 0x022f6ae3e0d1f236ULL}}, {{0x3befcfdbe8dd042cULL, 0x1f23c41b8459e28cULL, 0x9d3df3e0c372ff8aULL, 0x18dc26fa862b191eULL}}},
  {{{0x56dd436505fd7a95ULL, 0xde6df28980a2b7d9ULL, 0x0363df341e40f38bULL, 0x07e2bca200e16abaULL}}, {{0xd411d472d8dc23daULL, 0xf50cfab4071be3cfULL, 0x3c259a5e3e76eb62ULL, 0x0ac0b7df209f51acULL}}, {{0x5ed3556cb6eccdaaULL, 0x5a77f234139d70b3ULL, 0xfcb189da416e3bcaULL, 0x0cafd03316e3da67ULL}}},
  {{{0x3ded6d76360a45beULL, 0x6c429cb169faa590ULL, 0x2fb017c34a83a077ULL, 0x31f542859f15f500ULL}}, {{0x3429130c2c719a28ULL, 0x2c9ef140b71e34edULL, 0x483fc18d0a310a87ULL, 0x1495571d0705997cULL}}, {{0x3af7365d394648aeULL, 0x5cf1b21e24262136ULL, 0xc0fc62acf9bb6f72ULL, 0x1115c26a2fa746d9ULL}}},
  {{{0x8099beda71efd72fULL, 0xd36c358a6cb42b28ULL, 0xeec3d42dc5d22579ULL, 0x22193d634f4398d4ULL}}, {{0x69fa4c8431c72241ULL, 0x3d493a2870de9ecaULL, 0xfa85379fa7f96e96ULL, 0x06ed1793aac4bac5ULL}}, {{0x469e500151fe112eULL, 0xf15b462bf229e21fULL, 0xf700e5a684cc210eULL, 0x208c794ee061495bULL}}},
  {{{0x42e1de787c5ac045ULL, 0xdaf7f483c5ac2542ULL, 0x3a179e90ac57dc06ULL, 0x3ccede2a70073e55ULL}}, {{0x9907bebdd515efcdULL, 0x5c5759cc9d41d88aULL, 0x3674aac584e9815eULL, 0x256eccb4ae6815a8ULL}}, {{0xfbecb087cd94ed86ULL, 0xe2c856bd76367ef6ULL, 0x4eb80ed90b2de128ULL, 0x259f3b2f4d72a341ULL}}},
  {{{0x8aee7138a3e493efULL, 0xc097e3916e39d301ULL, 0x3f4edaab5fade903ULL, 0x26341785bebb55d1ULL}}, {{0x81743dbd685bfc78ULL, 0x51e1df5405018bb4ULL, 0x5e7f09f43fab73dcULL, 0x300dc575584e1165ULL}}, {{0xcf5e72012088079fULL, 0x5ee47f6039ea45b0ULL, 0x1376a4ad287da55cULL, 0x15c592ab8709a775ULL}}},
  {{{0xd1ba83ae61ab349cULL, 0x54c4ebfa46c6c5ddULL, 0x6811f417646c4a9bULL, 0x0304e5f3b22fd1e6ULL}}, {{0x96b0a28615104eebULL, 0xddc28384fa498de1ULL, 0x2e588de186363997ULL, 0x35279da4cf2bc018ULL}}, {{0xd0533b7b914aa30eULL, 0xf91091f7f642e389ULL, 0xe768cc728d9ffd9fULL, 0x3512143a077d0fa6ULL}}},
  {{{0xa64b6584aa7777b6ULL, 0xa9ecd008c97413bdULL, 0x42db693e89469246ULL, 0x000f9bd1021c5922ULL}}, {{0x0208b8d66e15fe3bULL, 0xeb7cb55bbc327ae8ULL, 0x63a2418e20a3ba6cULL, 0x38a5ea6f82db3d5dULL}}, {{0x9a649745f40e953eULL, 0x9d6406d52cb622f5ULL, 0x200a4cbd0f1f267cULL, 0x3db51a34b6e9fe06ULL}}},
  {{{0x17c83056e2c382a1ULL, 0x2f4c8b882d658eb4ULL, 0x96acd13fcc26bf82ULL, 0x000c6a1b1bf90012ULL}}, {{0xf616d545a5d3e939ULL, 0x2af7464619d365cbULL, 0xf097308d468c947dULL, 0x291ffc707a48e2ccULL}}, {{0xd3b637e65a834971ULL, 0x8fa7365afde54fe7ULL, 0x118cc5ff60f24404ULL, 0x1430b62cbd021f4aULL}}},
  {{{0xab3d6c0df3ce0ca0ULL, 0x08144b4c79d86499ULL, 0xf91d2462d75a2286ULL, 0x2bf52870c017cf4eULL}}, {{0xe5e5488d5162898eULL, 0xe83c6c0ca21e9962ULL, 0x66f17a5cce9bd5eeULL, 0x0faa86932fc9ec52ULL}}, {{0x6a601060296db14dULL, 0xecf3cf47c1dc4442ULL, 0x6a950536b5584542ULL, 0x313de4b333fc8118ULL}}},
  {{{0xc2bb2bdb161c0d43ULL, 0xe42240232ae44172ULL, 0x305435bec7528b04ULL, 0x2da4e7173aee4d48ULL}}, {{0x923370757c286129ULL, 0xbf9fcef7fa21e1f3ULL, 0x0e1971e6add36a32ULL, 0x05f07747dffb6336ULL}}, {{0xb63765a7f3c491d9ULL, 0xc6da1f9e3e9828c7ULL, 0xde242a4e2279090dULL, 0x2cca495816249692ULL}}},
  {{{0x1ff64be92cab7091ULL, 0x3d79404b46d72eb9ULL, 0x1710f1c5af14541aULL, 0x0ebaf248a381fe31ULL}}, {{0xa40aa7f2f4be8e45ULL, 0x135a66ac8749ce1cULL, 0xd8d76ea87865c570ULL, 0x044ec20c80c90b04ULL}}, {{0x4a9da72cba665450ULL, 0xd5295d8e27bb7bfbULL, 0x3626ca8c336dd990ULL, 0x022408a1fb0b3800ULL}}},
  {{{0x8446ea40f76089b3ULL, 0xdbfa50f0a581e128ULL, 0xd7685cd42f8f7c21ULL, 0x398f3c2662df6e9aULL}}, {{0x37d44d6ed12e5836ULL, 0xdd62ee99a8b6cc55ULL, 0xaf6d348d1857a659ULL, 0x1f9c9041980969afULL}}, {{0xf749702efd480758ULL, 0x323710fe973ef206ULL, 0xddb2efafff6e26bfULL, 0x3281013f35baa4d1ULL}}},
  {{{0x36f8bf09755e3fd1ULL, 0x5d77e2be7cd25b26ULL, 0xb3f18051ec66d481ULL, 0x228b840f19b7f6edULL}}, {{0x1e20bd7e9007dc99ULL, 0x7f9c083ce884876dULL, 0xb113ce50640f20f6ULL, 0x2bf716d6b3cd9a18ULL}}, {{0xe0f986df949e09f8ULL, 0x32d8dd9249948d2eULL, 0x9ae905c32961e96fULL, 0x30553eb90e4d277aULL}}},
  {{{0x2acddfb558ce6fd8ULL, 0xc70f8fcddfdb34a1ULL, 0xfa66e72c6937e86fULL, 0x385df4d2ddcdcaa5ULL}}, {{0x3e7465e402206318ULL, 0xf6ead3f9d9e048b3ULL, 0x619112a188adb41eULL, 0x2c34febcf9def460ULL}}, {{0xe8a7c82fa2625b3fULL, 0xaebb23cc8147e2bdULL, 0xf587afa348f34bf0ULL, 0x07ccc87a97eee0b3ULL}}},
  {{{0xd679b84eef1994b9ULL, 0x7def28d56667062cULL, 0xac3068742ec64b40ULL, 0x14479d04a6999fefULL}}, {{0x1bf627000bfe0e4aULL, 0x1c54cb5d1844ccffULL, 0x76ba72dfe568a18aULL, 0x1eb61f5d4af67fbdULL}}, {{0x48f5e53e337b002aULL, 0xa2cd1072d615602fULL, 0x6bb93f9dad34bed7ULL, 0x320e9200e22d4464ULL}}},
  {{{0x5aa93dae91a2e4b9ULL, 0xfaacb53728337d8aULL, 0x1081dbb00247523bULL, 0x397bf21666510308ULL}}, {{0x8f7f76f47d9ff019ULL, 0x24de8ffa0fad4008ULL, 0x2018e79b576a6bc7ULL, 0x158acea556828e27ULL}}, {{0xe905f10b227bbf42ULL, 0xc2edbfc5a426c09fULL, 0xd95d18ff73154263ULL, 0x040333330a351778ULL}}},
  {{{0x91a0adc20b096a81ULL, 0x8ed3f92a943f4990ULL, 0x09dca1eb774a58aaULL, 0x3190de39a08e30d0ULL}}, {{0xa186477461610158ULL, 0x49dcf00c9a3f4cdcULL, 0xc24bd4292b6300a8ULL, 0x2353ebbae73e6b0bULL}}, {{0xd86fe6c3fd5d72d6ULL, 0xcb092c676b2faf59ULL, 0x41de6a751b2ab6b8ULL, 0x36d1c42ec123b236ULL}}},
  {{{0x6eeb8c14a580493fULL, 0xa63fafe1762d0433ULL, 0x2535874ab3d5feb7ULL, 0x3f9fd0c9caf16f44ULL}}, {{0x097b1331d5d5fdcdULL, 0xb69a099bd2707e4bULL, 0xa00d654aab61139bULL, 0x04a51f72fbc8f91eULL}}, {{0xec1ba969b57bc21aULL, 0x757b333a7ffa3b3dULL, 0x0e597273fe4ac666ULL, 0x114d73316180d61bULL}}},
  {{{0x042ec88c94422adfULL, 0x84669dfab8f97048ULL, 0xdcc347c19ad69842ULL, 0x293316fbfcb11e39ULL}}, {{0x63d9ab3880316efeULL, 0xd06d752adf2b43fcULL, 0xa236c0995704aa60ULL, 0x286ce110716c2974ULL}}, {{0x25fd65694898efb4ULL, 0x99cb620dfc63fbcdULL, 0xf3a0a1e1aedec074ULL, 0x097462528778299bULL}}},
  {{{0x418c3f6d880e3244ULL, 0x20a933100425e4d5ULL, 0x5366e37bd79dd77dULL, 0x1c5640c60b10f088ULL}}, {{0x062556e677ce1aeeULL, 0x551bb969a99a27d8ULL, 0xbd64e65f6d50ce56ULL, 0x3670f79b1ebd37eaULL}}, {{0x6340a6e40b2cb449ULL, 0x75a66980082192d0ULL, 0xf26997d2e59968b8ULL, 0x1ba8ef4ddba030a2ULL}}},
  {{{0x9e81ed6bcca99ca8ULL, 0xe283e6741c1c8c1aULL, 0x4dcbab4c903e7d6cULL, 0x144287df706d7d35ULL}}, {{0xf307d19656785140ULL, 0xf2359f3af40af740ULL, 0x073120eaab4c104dULL, 0x372a560cedb19147ULL}}, {{0x0917ef782f366a32ULL, 0x118e0d62997e0761ULL, 0x85a794632bd1186eULL, 0x3fd8af8f75a55735ULL}}},
  {{{0x45f1327d29d5bb47ULL, 0x1d267c203c076406ULL, 0x54568d3ebb89dbacULL, 0x050c1e7fd4e0840aULL}}, {{0x8918a0f53d47ef87ULL, 0xd801c477ffe38754ULL, 0x6f614c3c03eab522ULL, 0x3e22c9f862e9d961ULL}}, {{0x0a6c3b558ff7fb9dULL, 0x916c06f103a297bfULL, 0xfe331bfa4f477e45ULL, 0x02fda085e0882d39ULL}}},
  {{{0xe00d560c1922bd80ULL, 0xbe5fb99f7823e7ceULL, 0x9b8ab20ee58d07d2ULL, 0x3cf282a530973229ULL}}, {{0x61f5e4a62789d305ULL, 0xe79e5db989d235c2ULL, 0x779fd5723b0e4c8cULL, 0x1fb84c68e272aacdULL}}, {{0x9f8bc8af370f0e1fULL, 0x628b777da9608e7aULL, 0x56f3fce27af86d3dULL, 0x3ed0ea844bce3f7cULL}}},
  {{{0xa81ca9ad3596718eULL, 0xa2e243ebc26d8786ULL, 0xbdd0c75e49311133ULL, 0x0491f56bad943b95ULL}}, {{0x662a89747f07eb48ULL, 0xbfd2949f2198be29ULL, 0x61faee803ba6ad21ULL, 0x0d92b19df57965e5ULL}}, {{0x74c0170dcb26b9a3ULL, 0x6e043841ae89ad9cULL, 0x9c21986513bb6c95ULL, 0x32c850785ef8c550ULL}}},
  {{{0xed4d002f16bc787fULL, 0x06ebf8cb07196aa9ULL, 0x14eb45e365573e2bULL, 0x25032cef4a7000efULL}}, {{0x3b118891deafe0c1ULL, 0x13f9c32f82aa94f5ULL, 0xa02a82d122209fb7ULL, 0x1ce89d10d60cb6f5ULL}}, {{0xf371d6ce33fea695ULL, 0x5505eca4ffdb4f3aULL, 0x2c1c430f4a00cc14ULL, 0x18679130f2053d1bULL}}},
  {{{0x8f93a25b2e5c3ac9ULL, 0xf65309c16f7c2122ULL, 0x448ec71a1bb9c43fULL, 0x1c9901bfdaead7bbULL}}, {{0xce3903ea34b01eb4ULL, 0x3743ef7a61a75b0dULL, 0xc4b3b804343ab52cULL, 0x21525c6921c10348ULL}}, {{0x3e58ceccf33d9fd6ULL, 0x0a4405f0f3f9ecddULL, 0x5e439182f7d467e3ULL, 0x2fdbb7666a8d4e93ULL}}},
  {{{0xd95c47374d92d769ULL, 0x6e7a4d28152762eeULL, 0x70aca0ccc8b1e64cULL, 0x00224355557620cdULL}}, {{0xd546a4caccd86c58ULL, 0x94e61f808ca9e38fULL, 0xd4dcc0ca96cc3b32ULL, 0x19e80175f12ee906ULL}}, {{0xdd1c43055a2df184ULL, 0x21ea7e74be932b7bULL, 0xeb9bd9f6301efde3ULL, 0x204f1be7c3153361ULL}}},
  {{{0x669a1bfa4452e5b9ULL, 0xb50119f9ba5913e4ULL, 0x376e862381f50e26ULL, 0x2fb4218313d636abULL}}, {{0x79c6708a2d8292c2ULL, 0x2684a5342d6e29c4ULL, 0x77efae4ea0f85e94ULL, 0x26a86c00b42234b5ULL}}, {{0xacb8a62ec21f1790ULL, 0xa532d1c96fd777b0ULL, 0xbce6beb99cd715c5ULL, 0x2205f95b96860426ULL}}},
  {{{0xeea18d332c6ba201ULL, 0x7e49750fe17b0c48ULL, 0x84b958e355658851ULL, 0x1af476c6c11beb7cULL}}, {{0xac7444171b9ed2a4ULL, 0xb13b491258203302ULL, 0x7bbd82c67d980d63ULL, 0x288fef4833b6612bULL}}, {{0xdb2f5426a3ce3a28ULL, 0xe35f66b7b35fd095ULL, 0xc2911efe8acaa8d3ULL, 0x20adef5e2b2bc83fULL}}},
  {{{0x668c5c60dc165271ULL, 0xa20833455f8c9082ULL, 0x7ea98ee735477650ULL, 0x3742df583c401d58ULL}}, {{0x76bb56ba0777dd32ULL, 0x57ae5691adfd5bb6ULL, 0xc25cd5eaaad89961ULL, 0x0ba64c73d78f268aULL}}, {{0x77f195a810966117ULL, 0x5a4fa67cbe740274ULL, 0xc195daea12525beaULL, 0x116979774227425cULL}}},
  {{{0x5d58cfd09c2210bbULL, 0x4ba345d05d37c73aULL, 0x6e8d9dd33f2a5189ULL, 0x1a0e98c3ef88d4cfULL}}, {{0x561643bef1c2f375ULL, 0xd28ed380885331acULL, 0xba76d3ad613a46f5ULL, 0x3ef76bf14ed05706ULL}}, {{0x0fe0d46abf50f962ULL, 0xb8c8c797af9d04b6ULL, 0xd19d4f33430a128fULL, 0x11ffb1bc451c07d1ULL}}},
};
static const fp MDS[3][3] = {
  {{{0x7c1a669d208e8b4dULL, 0x5f51868647bdf2a3ULL, 0x00fcf9354819f613ULL, 0x3103a7de3b678ebdULL}}, {{0xd02c6b7336d40cfaULL, 0x3a1a0851864fb4a7ULL, 0x2282de236a32af60ULL, 0x0e799762bd549615ULL}}, {{0xb3624a21289b4249ULL, 0xca6c5877b9c3c7c5ULL, 0xb02a2a0100ebb202ULL, 0x117cb780c908530aULL}}},
  {{{0xe3ff3f5c313a6a34ULL, 0x51c6f61bd721544dULL, 0x8ed31b47cae66704ULL, 0x02087f41039c75bbULL}}, {{0xd2f9d522444ac1a0ULL, 0xe69ac4d3b9d1c5a0ULL, 0x6edec07987aaee83ULL, 0x1e43c65722df71bdULL}}, {{0x10a0d86e38d77e7bULL, 0xf0b93da384af65e0ULL, 0x62ed3679f9a91794ULL, 0x2345494383dd3fb8ULL}}},
  {{{0x1ff15b66b7bbe66dULL, 0x75ecdd64110a734fULL, 0x78f0280d37007108ULL, 0x376408280c7418bcULL}}, {{0x934d00845da6461dULL, 0x930aa4624cdae4b4ULL, 0xdcd1ebac0098612dULL, 0x2de64334636be38dULL}}, {{0x0f957fede68e9322ULL, 0x14ac4b874d7324dbULL, 0x4007b97b032e6d5dULL, 0x22011675ded37456ULL}}},
};
#endif
```

### ntt.h

SHA-256 `d7541a91903cc9232747032fee3233024962aad2735010b4736915c92d7d45c1`, 1294 bytes.

```c
/* Number-theoretic transforms over Pallas on the subgroup tree of 2^K-th roots of unity.
 *
 * Node (d, j) of the tree (depth d, index j < 2^d) is the modulus X^(2^(K-d)) - psi_d^brv_d(j); it splits into
 * (d+1, 2j) and (d+1, 2j+1) with the twiddle t(d, j) = psi_(d+1)^brv_d(j).  A transform of size 2^L is the subtree of
 * node (K-L, J0): J0 = 0 is the subgroup H_L of order 2^L (modulus X^n - 1), J0 = 1 its coset (modulus X^n + 1).
 * Forward: natural-order coefficients in, values in bit-reversed order out (position j holds the value at the root of
 * leaf j).  Inverse: the transpose, returning 2^L times the coefficients. */
#ifndef NTT_H
#define NTT_H
#include "fp.h"

#define LMAX (TREE_K - 1)

void tw_init(void);
fp twiddle(uint32_t e);
uint32_t tw_exp(int L, int J0, int d, uint32_t u);
void fwd_pass(fp *x, int L, int J0, int d0, int r);
void inv_pass(fp *x, int L, int J0, int d0, int r);
void ntt_fwd(fp *x, int L, int J0);
void ntt_inv(fp *x, int L, int J0);
void ntt_fwd_range(fp *x, int L, int J0, int dlo, int dhi);
void ntt_inv_range(fp *x, int L, int J0, int dlo, int dhi);
uint32_t brv_next(uint32_t u, int bits);
void ntt_fwd_b(fp *x, int L, uint32_t B);
void ntt_inv_b(fp *x, int L, uint32_t B);

extern fp C_PSI2, C_PSI3, C_PSI33, C_IPSI2, C_IPSI3, C_IPSI33;
#endif
```

### ntt.c

SHA-256 `6461d9ed1a4a47dbdf0a938231b03e62c94e4e1778ccf3374aaf1a7eea4d5686`, 10675 bytes.

```c
/* Radix-8/4/2 passes of the tree transforms (see ntt.h).  Register model: a block of 8 data words and its 7 twiddles
 * stay in registers (with one temporary, 16 of the 18 assumed 256-bit registers); every array element is loaded and
 * stored once per pass. */
#include "ntt.h"

#define TB_N (1u << (TREE_K - TA_BITS))
static fp TA[1u << TA_BITS], TB[TB_N];
fp C_PSI2, C_PSI3, C_PSI33, C_IPSI2, C_IPSI3, C_IPSI33;

/** Build the two-level twiddle tables psi^e = TA[e mod 2^TA_BITS] * TB[e >> TA_BITS] and the pass constants. */
void tw_init(void)
{
    const fp psi = {PSI_LIMBS}, ipsi = {PSI_INV_LIMBS};
    TA[0] = FP_ONE;
    ST(1);
    for (uint32_t i = 1; i < (1u << TA_BITS); i++) {
        TA[i] = fp_mul(TA[i - 1], psi);
        LD(1);
        ST(1);
    }
    LOOPC((1u << TA_BITS) - 1);
    fp step = psi;
    for (int i = 0; i < TA_BITS; i++) step = fp_sqr(step);
    LOOPC(TA_BITS);
    TB[0] = FP_ONE;
    ST(1);
    for (uint32_t i = 1; i < TB_N; i++) {
        TB[i] = fp_mul(TB[i - 1], step);
        LD(1);
        ST(1);
    }
    LOOPC(TB_N - 1);
    fp c3 = psi, ic3 = ipsi;
    for (int i = 0; i < TREE_K - 3; i++) {
        c3 = fp_sqr(c3);
        ic3 = fp_sqr(ic3);
    }
    LOOPC(TREE_K - 3);
    C_PSI3 = c3;
    C_PSI2 = fp_sqr(c3);
    C_PSI33 = fp_mul(C_PSI2, c3);
    C_IPSI3 = ic3;
    C_IPSI2 = fp_sqr(ic3);
    C_IPSI33 = fp_mul(C_IPSI2, ic3);
    ST(6);
}

/** Return psi^e for 0 <= e < 2^K: two table loads, one multiplication, mask and shift. */
fp twiddle(uint32_t e)
{
    CTL(2);
    LD(2);
    return fp_mul(TA[e & ((1u << TA_BITS) - 1)], TB[e >> TA_BITS]);
}

/** Return the exponent (in powers of psi) of the twiddle of node (d, G) of the size-2^L subtree J0, where u = brv_d(G):
 *  (2u + J0) * 2^(K-d-2) (6 operations: doubling, addition, two subtractions for the shift count, shift, and one spare). */
uint32_t tw_exp(int L, int J0, int d, uint32_t u)
{
    (void)L;
    CTL(6);
    return (2 * u + (uint32_t)J0) << (TREE_K - d - 2);
}

/** The same for the size-2^L subtree with offset B (its root is the node of depth K-L whose root of unity is psi^(B 2^L)):
 *  (u 2^(K-L) + B) * 2^(L-d-1) (7 operations: three subtractions for the shift counts, two shifts, addition, one
 *  spare).  J0 = 0, 1 are B = 0, 2^(K-L-1). */
static uint32_t tw_exp_b(int L, uint32_t B, int d, uint32_t u)
{
    CTL(7);
    return ((u << (TREE_K - L)) + B) << (L - d - 1);
}

/** Return brv_bits(brv_bits(u) + 1), i.e. the bit-reversed successor (charged per executed carry step). */
uint32_t brv_next(uint32_t u, int bits)
{
    CTL(2);
    if (bits == 0) return 0;
    uint32_t bit = 1u << (bits - 1);
    CTL(2);
    while (u & bit) {
        u ^= bit;
        bit >>= 1;
        CTL(4);
    }
    CTL(3);
    return u | bit;
}

#define CT(a, b, w) do { fp t_ = fp_mul(b, w); b = fp_sub(a, t_); a = fp_add(a, t_); } while (0)
#define CT1(a, b)   do { fp t_ = b; b = fp_sub(a, t_); a = fp_add(a, t_); } while (0)
#define GS(a, b, w) do { fp t_ = fp_sub(a, b); a = fp_add(a, b); b = fp_mul(t_, w); } while (0)
#define GS1(a, b)   do { fp t_ = fp_sub(a, b); a = fp_add(a, b); b = t_; } while (0)

/** Compute the 7 twiddles of a radix-8 supergroup from the exponent e of its top node (forward if inv = 0, else inverse).
 *  w[0] depth d0; w[1], w[2] depth d0+1; w[3..6] depth d0+2. */
static void tw8(uint32_t e, int inv, fp w[7])
{
    uint32_t e2 = e >> 2;
    CTL(1);
    if (inv) {
        e2 = ((1u << TREE_K) - e2) & ((1u << TREE_K) - 1);
        CTL(2);
    }
    fp b2 = twiddle(e2), b1 = fp_sqr(b2);
    w[0] = fp_sqr(b1);
    LD(3);
    w[1] = b1;
    w[2] = fp_mul(b1, inv ? C_IPSI2 : C_PSI2);
    w[3] = b2;
    w[4] = fp_mul(b2, inv ? C_IPSI2 : C_PSI2);
    w[5] = fp_mul(b2, inv ? C_IPSI3 : C_PSI3);
    w[6] = fp_mul(b2, inv ? C_IPSI33 : C_PSI33);
}

/** Twiddles of a radix-4 supergroup: w[0] depth d0; w[1], w[2] depth d0+1. */
static void tw4(uint32_t e, int inv, fp w[3])
{
    uint32_t e1 = e >> 1;
    CTL(1);
    if (inv) {
        e1 = ((1u << TREE_K) - e1) & ((1u << TREE_K) - 1);
        CTL(2);
    }
    fp b1 = twiddle(e1);
    w[0] = fp_sqr(b1);
    LD(1);
    w[1] = b1;
    w[2] = fp_mul(b1, inv ? C_IPSI2 : C_PSI2);
}

static fp tw2(uint32_t e, int inv)
{
    if (inv) {
        e = ((1u << TREE_K) - e) & ((1u << TREE_K) - 1);
        CTL(2);
    }
    return twiddle(e);
}

/** Forward radix-8 kernel on x[0], x[st], ..., x[7 st]; triv = 1 when the node twiddles w[0], w[1], w[3] are 1. */
static inline void k8f(fp *x, size_t st, const fp w[7], int triv)
{
    fp a0 = x[0], a1 = x[st], a2 = x[2 * st], a3 = x[3 * st], a4 = x[4 * st], a5 = x[5 * st], a6 = x[6 * st], a7 = x[7 * st];
    LD(8);
    if (triv) {
        CT1(a0, a4); CT1(a1, a5); CT1(a2, a6); CT1(a3, a7);
        CT1(a0, a2); CT1(a1, a3); CT(a4, a6, w[2]); CT(a5, a7, w[2]);
        CT1(a0, a1); CT(a2, a3, w[4]); CT(a4, a5, w[5]); CT(a6, a7, w[6]);
    } else {
        CT(a0, a4, w[0]); CT(a1, a5, w[0]); CT(a2, a6, w[0]); CT(a3, a7, w[0]);
        CT(a0, a2, w[1]); CT(a1, a3, w[1]); CT(a4, a6, w[2]); CT(a5, a7, w[2]);
        CT(a0, a1, w[3]); CT(a2, a3, w[4]); CT(a4, a5, w[5]); CT(a6, a7, w[6]);
    }
    x[0] = a0; x[st] = a1; x[2 * st] = a2; x[3 * st] = a3; x[4 * st] = a4; x[5 * st] = a5; x[6 * st] = a6; x[7 * st] = a7;
    ST(8);
}

/** Inverse radix-8 kernel (transpose of k8f with inverse twiddles, times 8). */
static inline void k8i(fp *x, size_t st, const fp w[7], int triv)
{
    fp a0 = x[0], a1 = x[st], a2 = x[2 * st], a3 = x[3 * st], a4 = x[4 * st], a5 = x[5 * st], a6 = x[6 * st], a7 = x[7 * st];
    LD(8);
    if (triv) {
        GS1(a0, a1); GS(a2, a3, w[4]); GS(a4, a5, w[5]); GS(a6, a7, w[6]);
        GS1(a0, a2); GS1(a1, a3); GS(a4, a6, w[2]); GS(a5, a7, w[2]);
        GS1(a0, a4); GS1(a1, a5); GS1(a2, a6); GS1(a3, a7);
    } else {
        GS(a0, a1, w[3]); GS(a2, a3, w[4]); GS(a4, a5, w[5]); GS(a6, a7, w[6]);
        GS(a0, a2, w[1]); GS(a1, a3, w[1]); GS(a4, a6, w[2]); GS(a5, a7, w[2]);
        GS(a0, a4, w[0]); GS(a1, a5, w[0]); GS(a2, a6, w[0]); GS(a3, a7, w[0]);
    }
    x[0] = a0; x[st] = a1; x[2 * st] = a2; x[3 * st] = a3; x[4 * st] = a4; x[5 * st] = a5; x[6 * st] = a6; x[7 * st] = a7;
    ST(8);
}

static inline void k4f(fp *x, size_t st, const fp w[3], int triv)
{
    fp a0 = x[0], a1 = x[st], a2 = x[2 * st], a3 = x[3 * st];
    LD(4);
    if (triv) {
        CT1(a0, a2); CT1(a1, a3);
        CT1(a0, a1); CT(a2, a3, w[2]);
    } else {
        CT(a0, a2, w[0]); CT(a1, a3, w[0]);
        CT(a0, a1, w[1]); CT(a2, a3, w[2]);
    }
    x[0] = a0; x[st] = a1; x[2 * st] = a2; x[3 * st] = a3;
    ST(4);
}

static inline void k4i(fp *x, size_t st, const fp w[3], int triv)
{
    fp a0 = x[0], a1 = x[st], a2 = x[2 * st], a3 = x[3 * st];
    LD(4);
    if (triv) {
        GS1(a0, a1); GS(a2, a3, w[2]);
        GS1(a0, a2); GS1(a1, a3);
    } else {
        GS(a0, a1, w[1]); GS(a2, a3, w[2]);
        GS(a0, a2, w[0]); GS(a1, a3, w[0]);
    }
    x[0] = a0; x[st] = a1; x[2 * st] = a2; x[3 * st] = a3;
    ST(4);
}

static inline void k2f(fp *x, size_t st, fp w, int triv)
{
    fp a0 = x[0], a1 = x[st];
    LD(2);
    if (triv) CT1(a0, a1); else CT(a0, a1, w);
    x[0] = a0; x[st] = a1;
    ST(2);
}

static inline void k2i(fp *x, size_t st, fp w, int triv)
{
    fp a0 = x[0], a1 = x[st];
    LD(2);
    if (triv) GS1(a0, a1); else GS(a0, a1, w);
    x[0] = a0; x[st] = a1;
    ST(2);
}

#define INNER(KERN, W, T) do { for (size_t o = 0; o < st; o++) { CTL(1); KERN(base + o, st, W, T); } LOOPC(st); } while (0)

/** One pass of r = 1, 2 or 3 layers at depths d0 .. d0+r-1 of the size-2^L transform J0 (dir 0 forward, 1 inverse).
 *  Per supergroup: base address (2), trivial-twiddle test (4), kernel selection by r, dir and triv (6). */
static void pass_b(fp *x, int L, uint32_t B, int d0, int r, int dir)
{
    size_t S = (size_t)1 << (L - d0), st = S >> r, ng = (size_t)1 << d0;
    uint32_t u = 0;
    CTL(4);
    for (size_t G = 0; G < ng; G++) {
        fp *base = x + G * S;
        int triv = (B == 0 && G == 0);
        uint32_t e = tw_exp_b(L, B, d0, u);
        fp w[7];
        CTL(12);
        if (r == 3) {
            tw8(e, dir, w);
            if (dir) { if (triv) INNER(k8i, w, 1); else INNER(k8i, w, 0); }
            else { if (triv) INNER(k8f, w, 1); else INNER(k8f, w, 0); }
        } else if (r == 2) {
            tw4(e, dir, w);
            if (dir) { if (triv) INNER(k4i, w, 1); else INNER(k4i, w, 0); }
            else { if (triv) INNER(k4f, w, 1); else INNER(k4f, w, 0); }
        } else {
            w[0] = tw2(e, dir);
            if (dir) { if (triv) INNER(k2i, w[0], 1); else INNER(k2i, w[0], 0); }
            else { if (triv) INNER(k2f, w[0], 1); else INNER(k2f, w[0], 0); }
        }
        u = brv_next(u, d0);
    }
    LOOPC(ng);
}

/** The pass of the subtree J0 (B = J0 2^(K-L-1), one shift). */
static void pass(fp *x, int L, int J0, int d0, int r, int dir)
{
    CTL(1);
    pass_b(x, L, (uint32_t)J0 << (TREE_K - L - 1), d0, r, dir);
}

void fwd_pass(fp *x, int L, int J0, int d0, int r) { pass(x, L, J0, d0, r, 0); }
void inv_pass(fp *x, int L, int J0, int d0, int r) { pass(x, L, J0, d0, r, 1); }

/** Forward passes covering depths [dlo, dhi) in radix-8 steps (the last pass takes the remainder). */
void ntt_fwd_range(fp *x, int L, int J0, int dlo, int dhi)
{
    for (int d = dlo; d < dhi; d += 3) {
        int r = dhi - d < 3 ? dhi - d : 3;
        pass(x, L, J0, d, r, 0);
        CTL(5);
    }
    CTL(2);
}

/** Inverse passes covering depths [dlo, dhi), deepest first, grouped exactly as ntt_fwd_range groups them. */
void ntt_inv_range(fp *x, int L, int J0, int dlo, int dhi)
{
    if (dlo >= dhi) return;
    int d = dlo;
    while (d + 3 < dhi) d += 3;
    CTL(2 * ((dhi - dlo + 2) / 3) + 2);
    for (; d >= dlo; d -= 3) {
        int r = dhi - d < 3 ? dhi - d : 3;
        pass(x, L, J0, d, r, 1);
        CTL(5);
    }
    CTL(2);
}

void ntt_fwd(fp *x, int L, int J0) { ntt_fwd_range(x, L, J0, 0, L); }
void ntt_inv(fp *x, int L, int J0) { ntt_inv_range(x, L, J0, 0, L); }

/** Forward transform of the size-2^L subtree with offset B (see tw_exp_b). */
void ntt_fwd_b(fp *x, int L, uint32_t B)
{
    for (int d = 0; d < L; d += 3) {
        int r = L - d < 3 ? L - d : 3;
        pass_b(x, L, B, d, r, 0);
        CTL(5);
    }
    CTL(2);
}

/** Inverse transform of the size-2^L subtree with offset B (returns 2^L times the coefficients). */
void ntt_inv_b(fp *x, int L, uint32_t B)
{
    if (L == 0) return;
    int d = 0;
    while (d + 3 < L) d += 3;
    CTL(2 * ((L + 2) / 3) + 2);
    for (; d >= 0; d -= 3) {
        int r = L - d < 3 ? L - d : 3;
        pass_b(x, L, B, d, r, 1);
        CTL(5);
    }
    CTL(2);
}
```

### line.h

SHA-256 `0d536d1e735e5ec606b6267b349492564fd9b57be4e2cd518ffacd0126e262aa`, 186 bytes.

```c
#ifndef LINE_H
#define LINE_H
#include "fp.h"

#define C_UNIT 279

void line_setup(int nr);
fp line_eval(fp W);
fp ref_hash(fp nk, fp rho);
void line_back(fp W, fp *nk, fp *rho);
#endif
```

### line.c

SHA-256 `1120719872cbc89ad63890f7ed6eb8b5d0954490e7ae232c3d40a74a8dd50130`, 3820 bytes.

```c
/* The line j = 0 of the two free rounds (proof section 2): (U, V) = Q + tau (a, b), W = tau^5, and the digest F(W).
 *
 * Setup is counted per operation.  A line evaluation F(W) and a reference hash are charged one target compression
 * (C_UNIT operations) each, not their expanded arithmetic, which is smaller. */
#include "line.h"

static fp AL[3], BE[3], QU, QV, LA, LB;
static int NR;

static const uint64_t E5[4] = {0xe0f0f3f0cccccccdULL, 0x4e9ee0c9a10a60e2ULL, 0x3333333333333333ULL, 0x3333333333333333ULL};

static fp r_add(fp a, fp b)
{
    fp r = add256(a, b);
    if (ge256(&r, &FP_P)) {
        uint64_t br;
        r = sub256(r, FP_P, &br);
    }
    return r;
}

static fp r_pow5(fp x)
{
    fp x2 = mont_raw(x, x);
    return mont_raw(mont_raw(x2, x2), x);
}

static fp pow5(fp x)
{
    fp x2 = fp_sqr(x);
    return fp_mul(fp_sqr(x2), x);
}

/** Return row i of M v with counted operations. */
static fp mds_row(int i, const fp v[3])
{
    LD(3);
    return fp_add(fp_add(fp_mul(MDS[i][0], v[0]), fp_mul(MDS[i][1], v[1])), fp_mul(MDS[i][2], v[2]));
}

/** Compute Q, (a, b), alpha and beta of the line for nr partial rounds (counted). */
void line_setup(int nr)
{
    NR = nr;
    const uint64_t two65[4] = {0, 2, 0, 0};
    LD(1);
    fp K = pow5(fp_add(fp_from_limbs(two65), RC[0][2]));
    fp b[3];
    for (int k = 0; k < 3; k++) {
        LD(2);
        b[k] = fp_add(fp_mul(MDS[k][2], K), RC[1][k]);
    }
    LOOPC(3);
    LD(4);
    fp det = fp_sub(fp_mul(MDS[1][0], MDS[2][1]), fp_mul(MDS[1][1], MDS[2][0]));
    fp idet = fp_inv(det);
    LD(4);
    QU = fp_mul(fp_add(fp_neg(fp_mul(b[1], MDS[2][1])), fp_mul(b[2], MDS[1][1])), idet);
    QV = fp_mul(fp_add(fp_neg(fp_mul(b[2], MDS[1][0])), fp_mul(b[1], MDS[2][0])), idet);
    LD(2);
    LA = MDS[0][1];
    LB = fp_neg(MDS[0][0]);
    fp q[3] = {QU, QV, FP_ZERO};
    fp kap = fp_add(mds_row(0, q), b[0]);
    fp ab[3] = {LA, LB, FP_ZERO};
    fp d1 = mds_row(1, ab), d2 = mds_row(2, ab);
    fp v0[3] = {pow5(kap), FP_ZERO, FP_ZERO}, v1[3] = {FP_ZERO, pow5(d1), pow5(d2)};
    for (int i = 0; i < 3; i++) {
        AL[i] = mds_row(i, v0);
        BE[i] = mds_row(i, v1);
    }
    LOOPC(3);
    ST(10);
}

/** Apply rounds first..3, the nr partial rounds 4.., and the full rounds 60..63 to s (uncounted). */
static void rounds_raw(fp s[3], int first)
{
    for (int i = first; i < 64; i++) {
        if (i == 4 + NR) i = 60;
        int full = i < 4 || i >= 60;
        for (int k = 0; k < 3; k++) s[k] = r_add(s[k], RC[i][k]);
        s[0] = r_pow5(s[0]);
        if (full) {
            s[1] = r_pow5(s[1]);
            s[2] = r_pow5(s[2]);
        }
        fp t[3];
        for (int r = 0; r < 3; r++)
            t[r] = r_add(r_add(mont_raw(MDS[r][0], s[0]), mont_raw(MDS[r][1], s[1])), mont_raw(MDS[r][2], s[2]));
        s[0] = t[0];
        s[1] = t[1];
        s[2] = t[2];
    }
}

/** Return the digest F(W) of the line point W (one unit charge). */
fp line_eval(fp W)
{
    X.unit += C_UNIT;
    fp s[3];
    for (int k = 0; k < 3; k++) s[k] = r_add(AL[k], mont_raw(BE[k], W));
    rounds_raw(s, 2);
    return s[0];
}

/** Return the digest of the canonical input (nk, rho) by the full reference permutation (one unit charge). */
fp ref_hash(fp nk, fp rho)
{
    X.unit += C_UNIT;
    const uint64_t two65[4] = {0, 2, 0, 0};
    fp t = {{two65[0], two65[1], two65[2], two65[3]}};
    fp s[3] = {nk, rho, mont_raw(t, (fp){R2_LIMBS})};
    rounds_raw(s, 0);
    return s[0];
}

/** Map the line point W to its canonical input: tau = W^e, (U, V) = Q + tau (a, b), nk = U^e - c00, rho = V^e - c01. */
void line_back(fp W, fp *nk, fp *rho)
{
    fp tau = fp_pow(W, E5);
    LD(2);
    *nk = fp_sub(fp_pow(fp_add(QU, fp_mul(tau, LA)), E5), RC[0][0]);
    *rho = fp_sub(fp_pow(fp_add(QV, fp_mul(tau, LB)), E5), RC[0][1]);
    LD(4);
}
```

### stageb.h

SHA-256 `1f74a435b810e2d41243723a0a12954d42d7bd14942fcb44739b3507e1923d8c`, 163 bytes.

```c
#ifndef STAGEB_H
#define STAGEB_H
#include "fp.h"
void stage_b(fp c, int L, fp *V);
int stage_prep(int L, size_t m, int t, fp *B0, fp *B1, fp *B2, fp *B3);
#endif
```

### stageb.c

SHA-256 `832b4f9882d5c75531034b8d068a2682cfbcd76c07d3b96dccdbbcd91a06e4f2`, 5511 bytes.

```c
/* Stage B (the line polynomial g_c by evaluation) and the preparation of stage C (start residue, Gi, G2).
 *
 * n = 2^L >= m + 1.  zeta is a primitive 2^(L+1)-th root of unity, so S_i = zeta^(2i) runs over O1 = H_L, and
 * F(c + s) - F(c - s) = 2 s g_c(s^2) gives the values gt(S_i) = (F(c + zeta^i) - F(c - zeta^i)) zeta^-i of gt = 2 g_c.
 * The value at S_i is stored at position brv_L(i), the output order of the forward transforms. */
#include "stageb.h"
#include "line.h"
#include "ntt.h"

/** Return psi^(2^j) (j squarings). */
static fp psi_pow2(fp psi, int j)
{
    for (int i = 0; i < j; i++) psi = fp_sqr(psi);
    LOOPC(j);
    return psi;
}

/** Fill V (n words) with the values of gt = 2 g_c on O1 in transform order. */
void stage_b(fp c, int L, fp *V)
{
    size_t n = (size_t)1 << L;
    const fp psi = {PSI_LIMBS}, ipsi = {PSI_INV_LIMBS};
    fp z = psi_pow2(psi, TREE_K - 1 - L), iz = psi_pow2(ipsi, TREE_K - 1 - L);
    fp s = FP_ONE, is = FP_ONE;
    uint32_t j = 0;
    for (size_t i = 0; i < n; i++) {
        fp d = fp_sub(line_eval(fp_add(c, s)), line_eval(fp_sub(c, s)));
        V[j] = fp_mul(d, is);
        ST(1);
        s = fp_mul(s, z);
        is = fp_mul(is, iz);
        j = brv_next(j, L);
    }
    LOOPC(n);
}

/** out = a * b mod (X^N - 1), N = 2^l, for a of length la and b of length lb (la, lb <= N); ta, tb scratch of N
 *  words.  If tb_ready, tb already holds the transform of b scaled by 1/N and b is ignored. */
static void cyc_mul(fp *out, const fp *a, size_t la, const fp *b, size_t lb, int l, fp *ta, fp *tb, int tb_ready)
{
    size_t N = (size_t)1 << l;
    for (size_t i = 0; i < N; i++) ta[i] = i < la ? a[i] : FP_ZERO;
    LD(la);
    ST(N);
    LOOPC(N);
    CTL(N);
    ntt_fwd(ta, l, 0);
    if (!tb_ready) {
        fp iN = fp_inv(fp_from_u64(N));
        for (size_t i = 0; i < N; i++) tb[i] = i < lb ? b[i] : FP_ZERO;
        LD(lb);
        ST(N);
        LOOPC(N);
        CTL(N);
        ntt_fwd(tb, l, 0);
        for (size_t i = 0; i < N; i++) tb[i] = fp_mul(tb[i], iN);
        LD(N);
        ST(N);
        LOOPC(N);
    }
    for (size_t i = 0; i < N; i++) ta[i] = fp_mul(ta[i], tb[i]);
    LD(2 * N);
    ST(N);
    LOOPC(N);
    ntt_inv(ta, l, 0);
    CTL(2);
    if (out != ta) {
        for (size_t i = 0; i < N; i++) out[i] = ta[i];
        LD(N);
        ST(N);
        LOOPC(N);
    }
}

/** h = 1/f mod X^prec by Newton iteration (h_2t = h_t - h_t (f h_t - 1) mod X^2t); f has at least prec coefficients.
 *  h needs P2 = 2^ceil(log2 prec) words and the scratch s 2 P2 words. */
static void series_inv(fp *h, const fp *f, size_t prec, fp *s)
{
    size_t t = 1;
    int l = 1;
    LD(1);
    h[0] = fp_inv(f[0]);
    ST(1);
    while (t < prec) {
        size_t N = 2 * t;
        fp *ta = s, *tb = s + N;
        size_t lf = N < prec ? N : prec;
        cyc_mul(ta, f, lf, h, t, l, ta, tb, 0);
        cyc_mul(ta, ta + t, t, NULL, 0, l, ta, tb, 1);
        for (size_t i = 0; i < t; i++) h[t + i] = fp_neg(ta[i]);
        LD(t);
        ST(t);
        LOOPC(t);
        t = N;
        l++;
        CTL(6);
    }
    CTL(2);
}

/** Prepare stage C from V = gt(O1) (transform order).  Uses four n-word buffers: on entry B0 = V; on success
 *  B0 = Gi = -1/(n^3 g'(O1)), B1 = G2 = g'(O2) for g' = 2n g_c, B2 = W = coefficients of A0 = S^v P1 mod g (degree
 *  < n), B3 scratch.  Requires 2m >= n and 2^t <= n - m (v = 2^t).  Returns 0, or -1 if deg gt != m or gt vanishes
 *  on O1. */
int stage_prep(int L, size_t m, int t, fp *B0, fp *B1, fp *B2, fp *B3)
{
    size_t n = (size_t)1 << L, k = n - m, v = (size_t)1 << t;
    for (size_t i = 0; i < n; i++) B1[i] = B0[i];
    LD(n);
    ST(n);
    LOOPC(n);
    ntt_inv(B1, L, 0);
    for (size_t i = m + 1; i < n; i++)
        if (!fp_is0(B1[i])) return -1;
    LD(n - m - 1);
    LOOPC(n - m - 1);
    LD(1);
    if (fp_is0(B1[m])) return -1;

    /* f = rev_m(G*) to k + 1 terms, G* = B1 = n gt; q = floor(X^n / G*) = rev_k(1/f mod X^(k+1)).
     * f = B2[0..k], h = B2[n/2..], Newton scratch B3 (k + 1 <= n/2). */
    fp *f = B2, *h = B2 + n / 2;
    for (size_t i = 0; i <= k; i++) f[i] = B1[m - i];
    CTL(k + 1);
    LD(k + 1);
    ST(k + 1);
    LOOPC(k + 1);
    series_inv(h, f, k + 1, B3);
    for (size_t i = 0; i < n; i++) B3[i] = i <= k ? h[k - i] : FP_ZERO;
    CTL(k + 1);
    LD(k + 1);
    ST(n);
    LOOPC(n);
    CTL(n);

    /* T = q* G* mod (X^n - 1) = 1 - r, r = X^n mod g; A0 = X^v (r - 1) = -X^v T. */
    ntt_fwd(B3, L, 0);
    for (size_t i = 0; i < n; i++) B3[i] = fp_mul(B3[i], B0[i]);
    LD(2 * n);
    ST(n);
    LOOPC(n);
    ntt_inv(B3, L, 0);
    for (size_t i = 0; i < v; i++) B2[i] = FP_ZERO;
    ST(v);
    LOOPC(v);
    for (size_t i = 0; i < m; i++) B2[i + v] = fp_neg(B3[i]);
    LD(m);
    ST(m);
    LOOPC(m);
    for (size_t i = m + v; i < n; i++) B2[i] = FP_ZERO;
    ST(n - m - v);
    LOOPC(n - m - v);

    ntt_fwd(B1, L, 1);

    /* Gi = -1/(n^4 gt(O1)) by batch inversion with prefix products in B3. */
    fp acc = FP_ONE;
    for (size_t i = 0; i < n; i++) {
        LD(1);
        if (fp_is0(B0[i])) return -1;
        acc = fp_mul(acc, B0[i]);
        B3[i] = acc;
        ST(1);
    }
    LOOPC(n);
    fp n4 = fp_sqr(fp_sqr(fp_from_u64(n)));
    fp inv = fp_neg(fp_inv(fp_mul(acc, n4)));
    for (size_t i = n; i-- > 1;) {
        fp vi = B0[i];
        LD(2);
        B0[i] = fp_mul(inv, B3[i - 1]);
        ST(1);
        inv = fp_mul(inv, vi);
        CTL(1);
    }
    LOOPC(n - 1);
    B0[0] = inv;
    ST(1);
    return 0;
}
```

### stagec.h

SHA-256 `bdba35e25f6be187ceeb30e15bfd8bb69fb39d59dd6ded12eea4b410e0d61b43`, 237 bytes.

```c
#ifndef STAGEC_H
#define STAGEC_H
#include "fp.h"
void stagec_init(void);
void stage_c(fp *W, fp *A2, const fp *Gi, const fp *G2, int L, const uint8_t *bits, int nbits, fp *kappa, int verbose,
             void (*progress)(int));
#endif
```

### stagec.c

SHA-256 `807924e14c57ed0c6888e2bb88339eb48668ac4c9803d336f64c5113a5e62a1c`, 10109 bytes.

```c
/* Stage C: R = S^E mod g by Montgomery squarings in the value domain of two cosets.
 *
 * n = 2^L, O1 = H_L (roots of P1 = X^n - 1), O2 = its coset (roots of X^n + 1, where P1 = -2).  A residue A (deg < n) is
 * held as mu*A on O1 and lambda*A on O2 (mu = n*lambda); the O1 values are never stored: the work buffer W holds the O1
 * transform up to its last pass.  One step maps A to Mont(A, A) = A^2 / P1 mod g (degree < n):
 *   U  = (mu A)^2 * Gi on O1                  Gi = -1 / (n^3 g)      (u = -A^2/g mod P1, scaled)
 *   U  -> O2: inverse transform on O1, forward transform on O2
 *   B2 = (lambda A)^2 + U * G2 on O2          G2 = g;  B2 = lambda^2 (A^2 + u g) = -2 lambda^2 Mont(A, A)
 *   (times x on O2 when the exponent bit is 1), stored as the new O2 values (lambda' = -2 lambda^2)
 *   B2 -> O1: inverse transform on O2, forward transform on O1 (mu' = n lambda').
 * Passes: bottom (depths L-3..L-1) fused forward + pointwise + inverse; top (depths 0..2) fused inverse + forward. */
#include "ntt.h"
#include "stagec.h"

#define CTN(a, b, w) do { fp t_ = fp_mul(b, w); b = fp_add(a, t_); a = fp_sub(a, t_); } while (0)
#define GSN(a, b, w) do { fp t_ = fp_sub(b, a); a = fp_add(a, b); b = fp_mul(t_, w); } while (0)
#define CT(a, b, w)  do { fp t_ = fp_mul(b, w); b = fp_sub(a, t_); a = fp_add(a, t_); } while (0)
#define CT1(a, b)    do { fp t_ = b; b = fp_sub(a, t_); a = fp_add(a, t_); } while (0)
#define GS(a, b, w)  do { fp t_ = fp_sub(a, b); a = fp_add(a, b); b = fp_mul(t_, w); } while (0)
#define GS1(a, b)    do { fp t_ = fp_sub(a, b); a = fp_add(a, b); b = t_; } while (0)
/* Straight-line repetition with constant indices (no loop, no loop control): the 8 words of a block stay in registers. */
#define R4(S) do { S(0); S(1); S(2); S(3); } while (0)
#define R8(S) do { S(0); S(1); S(2); S(3); S(4); S(5); S(6); S(7); } while (0)

/* The seven constants psi_2, psi_3, psi_3^3, psi_4, psi_4^3, psi_4^5, psi_4^7 (psi_d of order 2^d); every twiddle of the
 * top passes of both cosets is one of them up to sign, so they stay in registers. */
static fp Q2, Q3, Q33, Q4, Q43, Q45, Q47;

/** Compute the top-pass constants (5 multiplications/squarings, 7 stores). */
void stagec_init(void)
{
    const fp psi = {PSI_LIMBS};
    fp q4 = psi;
    for (int i = 0; i < TREE_K - 4; i++) q4 = fp_sqr(q4);
    LOOPC(TREE_K - 4);
    Q4 = q4;
    Q3 = fp_sqr(Q4);
    Q2 = fp_sqr(Q3);
    Q33 = fp_mul(Q3, Q2);
    Q43 = fp_mul(Q4, Q3);
    Q45 = fp_mul(Q4, Q2);
    Q47 = fp_mul(Q43, Q2);
    ST(7);
}

/** Top pass O1 -> O2: inverse depths 2, 1, 0 of the O1 transform, then forward depths 0, 1, 2 of the O2 transform. */
static void top_12(fp *W, int L)
{
    size_t st = (size_t)1 << (L - 3);
    LD(7);
    for (size_t o = 0; o < st; o++) {
        fp *x = W + o;
        fp a0 = x[0], a1 = x[st], a2 = x[2 * st], a3 = x[3 * st], a4 = x[4 * st], a5 = x[5 * st], a6 = x[6 * st], a7 = x[7 * st];
        LD(8);
        CTL(1);
        GS1(a0, a1); GSN(a2, a3, Q2); GSN(a4, a5, Q33); GSN(a6, a7, Q3);
        GS1(a0, a2); GS1(a1, a3); GSN(a4, a6, Q2); GSN(a5, a7, Q2);
        GS1(a0, a4); GS1(a1, a5); GS1(a2, a6); GS1(a3, a7);
        CT(a0, a4, Q2); CT(a1, a5, Q2); CT(a2, a6, Q2); CT(a3, a7, Q2);
        CT(a0, a2, Q3); CT(a1, a3, Q3); CT(a4, a6, Q33); CT(a5, a7, Q33);
        CT(a0, a1, Q4); CT(a2, a3, Q45); CT(a4, a5, Q43); CT(a6, a7, Q47);
        x[0] = a0; x[st] = a1; x[2 * st] = a2; x[3 * st] = a3; x[4 * st] = a4; x[5 * st] = a5; x[6 * st] = a6; x[7 * st] = a7;
        ST(8);
    }
    LOOPC(st);
}

/** Top pass O2 -> O1: inverse depths 2, 1, 0 of the O2 transform, then forward depths 0, 1, 2 of the O1 transform. */
static void top_21(fp *W, int L)
{
    size_t st = (size_t)1 << (L - 3);
    LD(7);
    for (size_t o = 0; o < st; o++) {
        fp *x = W + o;
        fp a0 = x[0], a1 = x[st], a2 = x[2 * st], a3 = x[3 * st], a4 = x[4 * st], a5 = x[5 * st], a6 = x[6 * st], a7 = x[7 * st];
        LD(8);
        CTL(1);
        GSN(a0, a1, Q47); GSN(a2, a3, Q43); GSN(a4, a5, Q45); GSN(a6, a7, Q4);
        GSN(a0, a2, Q33); GSN(a1, a3, Q33); GSN(a4, a6, Q3); GSN(a5, a7, Q3);
        GSN(a0, a4, Q2); GSN(a1, a5, Q2); GSN(a2, a6, Q2); GSN(a3, a7, Q2);
        CT1(a0, a4); CT1(a1, a5); CT1(a2, a6); CT1(a3, a7);
        CT1(a0, a2); CT1(a1, a3); CT(a4, a6, Q2); CT(a5, a7, Q2);
        CT1(a0, a1); CT(a2, a3, Q2); CT(a4, a5, Q3); CT(a6, a7, Q33);
        x[0] = a0; x[st] = a1; x[2 * st] = a2; x[3 * st] = a3; x[4 * st] = a4; x[5 * st] = a5; x[6 * st] = a6; x[7 * st] = a7;
        ST(8);
    }
    LOOPC(st);
}

/** Seven forward (inv = 0) or inverse twiddles of bottom block G of the subtree J0, from u = brv_(L-3)(G). */
static void bot_tw(int L, int J0, uint32_t u, int inv, fp w[7])
{
    uint32_t e = tw_exp(L, J0, L - 3, u) >> 2;
    CTL(1);
    if (inv) {
        e = ((1u << TREE_K) - e) & ((1u << TREE_K) - 1);
        CTL(2);
    }
    fp b2 = twiddle(e), b1 = fp_sqr(b2);
    w[0] = fp_sqr(b1);
    w[1] = b1;
    w[3] = b2;
    LD(3);
    w[2] = fp_mul(b1, inv ? C_IPSI2 : C_PSI2);
    w[4] = fp_mul(b2, inv ? C_IPSI2 : C_PSI2);
    w[5] = fp_mul(b2, inv ? C_IPSI3 : C_PSI3);
    w[6] = fp_mul(b2, inv ? C_IPSI33 : C_PSI33);
}

enum { M_SQ1, M_EXIT1, M_B2, M_B2X, M_EXIT2 };

/** Bottom pass of the subtree J0 (0 for O1, 1 for O2): forward depths L-3..L-1, the pointwise map of the mode, inverse
 *  depths L-1..L-3.  Modes: M_SQ1 U = v^2 Gi; M_EXIT1 U = v Gi; M_B2 v = A2^2 + v G2 (stored to A2); M_B2X the same times
 *  x; M_EXIT2 v = A2 / n + v G2 (inn = 1/n). */
static void bottom(fp *W, fp *A2, const fp *Y, int L, int J0, int mode, fp inn)
{
    size_t nb = (size_t)1 << (L - 3);
    uint32_t u = 0;
    CTL(3);
    for (size_t G = 0; G < nb; G++) {
        fp *x = W + 8 * G;
        fp w[7], iw[7], v[8];
        CTL(2);
        bot_tw(L, J0, u, 0, w);
        fp a0 = x[0], a1 = x[1], a2 = x[2], a3 = x[3], a4 = x[4], a5 = x[5], a6 = x[6], a7 = x[7];
        LD(8);
        if (J0 == 0 && G == 0) {
            CT1(a0, a4); CT1(a1, a5); CT1(a2, a6); CT1(a3, a7);
            CT1(a0, a2); CT1(a1, a3); CT(a4, a6, w[2]); CT(a5, a7, w[2]);
            CT1(a0, a1); CT(a2, a3, w[4]); CT(a4, a5, w[5]); CT(a6, a7, w[6]);
        } else {
            CT(a0, a4, w[0]); CT(a1, a5, w[0]); CT(a2, a6, w[0]); CT(a3, a7, w[0]);
            CT(a0, a2, w[1]); CT(a1, a3, w[1]); CT(a4, a6, w[2]); CT(a5, a7, w[2]);
            CT(a0, a1, w[3]); CT(a2, a3, w[4]); CT(a4, a5, w[5]); CT(a6, a7, w[6]);
        }
        CTL(2);
        v[0] = a0; v[1] = a1; v[2] = a2; v[3] = a3; v[4] = a4; v[5] = a5; v[6] = a6; v[7] = a7;
        const fp *y = Y + 8 * G;
        CTL(4);
        if (mode == M_SQ1) {
#define P_SQ1(q) v[q] = fp_mul(fp_sqr(v[q]), y[q])
            R8(P_SQ1);
            LD(8);
        } else if (mode == M_EXIT1) {
#define P_EX1(q) v[q] = fp_mul(v[q], y[q])
            R8(P_EX1);
            LD(8);
        } else {
            fp *z = A2 + 8 * G;
            CTL(1);
            if (mode == M_EXIT2) {
#define P_EX2(q) v[q] = fp_add(fp_mul(z[q], inn), fp_mul(v[q], y[q]))
                R8(P_EX2);
                LD(16);
            } else {
#define P_B2(q) v[q] = fp_add(fp_sqr(z[q]), fp_mul(v[q], y[q]))
                R8(P_B2);
                LD(16);
                if (mode == M_B2X) {
#define P_X(r) v[2 * (r)] = fp_mul(v[2 * (r)], w[3 + (r)]); v[2 * (r) + 1] = fp_neg(fp_mul(v[2 * (r) + 1], w[3 + (r)]))
                    R4(P_X);
                }
                CTL(2);
#define P_ST(q) z[q] = v[q]
                R8(P_ST);
                ST(8);
            }
        }
        bot_tw(L, J0, u, 1, iw);
        a0 = v[0]; a1 = v[1]; a2 = v[2]; a3 = v[3]; a4 = v[4]; a5 = v[5]; a6 = v[6]; a7 = v[7];
        if (J0 == 0 && G == 0) {
            GS1(a0, a1); GS(a2, a3, iw[4]); GS(a4, a5, iw[5]); GS(a6, a7, iw[6]);
            GS1(a0, a2); GS1(a1, a3); GS(a4, a6, iw[2]); GS(a5, a7, iw[2]);
            GS1(a0, a4); GS1(a1, a5); GS1(a2, a6); GS1(a3, a7);
        } else {
            GS(a0, a1, iw[3]); GS(a2, a3, iw[4]); GS(a4, a5, iw[5]); GS(a6, a7, iw[6]);
            GS(a0, a2, iw[1]); GS(a1, a3, iw[1]); GS(a4, a6, iw[2]); GS(a5, a7, iw[2]);
            GS(a0, a4, iw[0]); GS(a1, a5, iw[0]); GS(a2, a6, iw[0]); GS(a3, a7, iw[0]);
        }
        CTL(2);
        x[0] = a0; x[1] = a1; x[2] = a2; x[3] = a3; x[4] = a4; x[5] = a5; x[6] = a6; x[7] = a7;
        ST(8);
        u = brv_next(u, L - 3);
    }
    LOOPC(nb);
}

/** Run stage C.  On entry W holds the coefficients (natural order, degree < n) of the start residue A0 in Montgomery
 *  form (A0 = S^v P1 mod g up to a multiple of g), A2 is scratch, Gi[j] = -1/(n^3 g(o1_j)) and G2[j] = g(o2_j) in the
 *  transform output order.  Squarings follow bits[0..nbits-1] (most significant first; bit 1 multiplies by x after the
 *  squaring).  On exit W holds the coefficients of kappa * R, R = S^(v 2^nbits + bits) mod g of degree < deg g, and
 *  *kappa is returned. */
void stage_c(fp *W, fp *A2, const fp *Gi, const fp *G2, int L, const uint8_t *bits, int nbits, fp *kappa, int verbose,
             void (*progress)(int))
{
    size_t n = (size_t)1 << L;
    fp inn = fp_inv(fp_from_u64(n));
    for (size_t i = 0; i < n; i++) A2[i] = fp_mul(W[i], inn);
    LD(n);
    ST(n);
    LOOPC(n);
    ntt_fwd(A2, L, 1);
    ntt_fwd_range(W, L, 0, 0, L - 3);
    fp lam = inn;
    for (int s = 0; s < nbits; s++) {
        bottom(W, NULL, Gi, L, 0, M_SQ1, inn);
        ntt_inv_range(W, L, 0, 3, L - 3);
        top_12(W, L);
        ntt_fwd_range(W, L, 1, 3, L - 3);
        CTL(2);
        bottom(W, A2, G2, L, 1, bits[s] ? M_B2X : M_B2, inn);
        ntt_inv_range(W, L, 1, 3, L - 3);
        top_21(W, L);
        ntt_fwd_range(W, L, 0, 3, L - 3);
        lam = fp_sqr(lam);
        lam = fp_neg(fp_add(lam, lam));
        LOOPC(1);
        CTL(2);
        if (progress) progress(s);
    }
    (void)verbose;
    bottom(W, NULL, Gi, L, 0, M_EXIT1, inn);
    ntt_inv_range(W, L, 0, 3, L - 3);
    top_12(W, L);
    ntt_fwd_range(W, L, 1, 3, L - 3);
    bottom(W, A2, G2, L, 1, M_EXIT2, inn);
    ntt_inv_range(W, L, 1, 0, L - 3);
    *kappa = fp_neg(fp_add(lam, lam));
}
```

### hgcd.h

SHA-256 `e41904760f54a1aeaa6b2db5b965196baa15580e835296d0598bc59ae224adcc`, 250 bytes.

```c
#ifndef HGCD_H
#define HGCD_H
#include "fp.h"
typedef struct { fp *e[4]; long d[4]; } mat;
extern size_t hg_peak;
extern uint64_t hg_prof[4];
void hg_arena(fp *base, size_t cap);
long hg_gcd(fp *a, long da, fp *b, long db, long kmax, fp **g);
#endif
```

### hgcd.c

SHA-256 `78fb6e07a3d7da53060d16c4aeaf04f62119b7fcb5d638d6d3bff0ff88b34153`, 26703 bytes.

```c
/* Stage D: G = gcd(a, b) by the half-gcd, with every polynomial and matrix held up to a nonzero scalar.
 *
 * Euclid sequence r_0 = a, r_1 = b, quotient degrees summing to d_j after j steps.  hgcd(a, b, k) returns a matrix M with
 * (a, b) proportional to M (r_h, r_(h+1)), h = max{j : d_j <= k}, deg M = d_h.  It reads only the coefficients of degree
 * >= deg a - 2k (top-part truncation), recurses on k/2 for the first half, forms (c, d) = adj(M1) (a, b) by cyclic
 * products, makes one pseudo-division c = (Q d + e) / beta^(t+1), recurses on (d, e) and returns M1 [[Q, 1], [beta^(t+1),
 * 0]] M2.  Division is inversion-free (pseudo-division), so the matrices are exact up to a scalar, which suffices: only
 * adj(M) (a, b) and products of matrices are formed, and both are homogeneous.
 *
 * Products are cyclic of size N = 2^l (mod X^N - 1), exact because the true result has degree < N.  The second factors
 * (matrix entries) are transformed one row at a time: row rho is the subtree of relative depth e and index rho of the
 * size-N transform, offset B = brv_e(rho) 2^(K-l), modulus X^(N/2^e) - w_rho. */
#include "hgcd.h"
#include "ntt.h"

void die(int code);

static fp *AR;
static size_t AR_CAP, AR_TOP;
size_t hg_peak;
uint64_t hg_prof[4]; /* base, node apply, driver apply, matrix products (reporting only, not charged) */
#define PROF_BEGIN uint64_t prof0_ = ctr_total(&X)
#define PROF_END(i) (hg_prof[i] += ctr_total(&X) - prof0_)

/** Use cap words at base as the stage D arena. */
void hg_arena(fp *base, size_t cap)
{
    AR = base;
    AR_CAP = cap;
    AR_TOP = 0;
    hg_peak = 0;
}

/** Allocate n words on the arena stack (5 operations: address, top update, capacity comparison and branch; the peak
 *  statistic is reporting only). */
static fp *aalloc(size_t n)
{
    fp *p = AR + AR_TOP;
    AR_TOP += n;
    CTL(5);
    if (AR_TOP > hg_peak) hg_peak = AR_TOP;
    if (AR_TOP > AR_CAP) die(4);
    return p;
}

static size_t amark(void) { return AR_TOP; }
static void arel(size_t m) { AR_TOP = m; CTL(1); }

static uint32_t brv(uint32_t x, int bits)
{
    uint32_t r = 0;
    for (int i = 0; i < bits; i++) r = (r << 1) | ((x >> i) & 1);
    CTL(4 * bits);
    LOOPC(bits);
    return r;
}

/** Return the degree of a[0..len) (-1 if zero), scanning from the top. */
static long pdeg(const fp *a, long len)
{
    long i = len - 1;
    while (i >= 0) {
        LD(1);
        if (!fp_is0(a[i])) break;
        i--;
        CTL(3);
    }
    CTL(2);
    return i;
}

static long pow2l(long x, int *l)
{
    long n = 1;
    int e = 0;
    while (n < x) {
        n <<= 1;
        e++;
        CTL(4);
    }
    CTL(2);
    *l = e;
    return n;
}

/** Return the matrix entry capacity for budget k: N'(k) + 2 with N'(k) = 2^ceil(log2(k + 1)). */
static long mcap(long k)
{
    int l;
    return pow2l(k + 1, &l) + 2;
}

/** Point the four entries of M at consecutive slots of cap words in reg. */
static void mat_at(mat *M, fp *reg, long cap)
{
    for (int i = 0; i < 4; i++) M->e[i] = reg + i * cap;
    CTL(8);
    LOOPC(4);
}

static void mat_id(mat *M)
{
    M->e[0][0] = FP_ONE;
    M->e[3][0] = FP_ONE;
    ST(2);
    M->d[0] = 0;
    M->d[1] = -1;
    M->d[2] = -1;
    M->d[3] = 0;
    CTL(4);
}

static void copy(fp *dst, const fp *src, long n)
{
    for (long i = 0; i < n; i++) dst[i] = src[i];
    LD(n);
    ST(n);
    LOOPC(n);
}

/** dst[0..rs) = src[0..len) mod (X^rs - w): Horner over the blocks of rs words (w_is1: w = 1, additions only). */
static void fold(fp *dst, const fp *src, long len, long rs, fp w, int w_is1)
{
    long nb = (len + rs - 1) / rs;
    CTL(3);
    if (nb <= 1) {
        copy(dst, src, len);
        for (long i = len < 0 ? 0 : len; i < rs; i++) dst[i] = FP_ZERO;
        ST(rs - (len < 0 ? 0 : len));
        LOOPC(rs - (len < 0 ? 0 : len));
        return;
    }
    long top = (nb - 1) * rs, tl = len - top;
    copy(dst, src + top, tl);
    for (long i = tl; i < rs; i++) dst[i] = FP_ZERO;
    ST(rs - tl);
    LOOPC(rs - tl);
    for (long b = nb - 2; b >= 0; b--) {
        const fp *s = src + b * rs;
        if (w_is1) {
            for (long i = 0; i < rs; i++) dst[i] = fp_add(dst[i], s[i]);
        } else {
            for (long i = 0; i < rs; i++) dst[i] = fp_add(fp_mul(dst[i], w), s[i]);
        }
        LD(2 * rs);
        ST(rs);
        LOOPC(rs);
        CTL(3);
    }
    LOOPC(nb - 1);
}

/** a[0..N) = a[0..len) mod (X^N - 1) in place. */
static void fold1_inplace(fp *a, long len, long N)
{
    for (long b = N; b < len; b += N) {
        long m = len - b < N ? len - b : N;
        for (long i = 0; i < m; i++) a[i] = fp_add(a[i], a[b + i]);
        LD(2 * m);
        ST(m);
        LOOPC(m);
        CTL(4);
    }
    LOOPC((len - 1) / N);
    for (long i = len; i < N; i++) a[i] = FP_ZERO;
    ST(len < N ? N - len : 0);
    LOOPC(len < N ? N - len : 0);
}

/** Root w_rho of row rho (of 2^e) of the size-2^l transform, and its offset B. */
static fp row_root(int l, int e, uint32_t rho, uint32_t *B)
{
    uint32_t br = brv(rho, e);
    *B = br << (TREE_K - l);
    CTL(2);
    return twiddle((br << (TREE_K - e)) & ((1u << TREE_K) - 1));
}

/** T = transform of entry (x, dx) on row (lr, B, w). */
static void row_entry(fp *T, const fp *x, long dx, long rs, int lr, uint32_t B, fp w, int w_is1)
{
    fold(T, x, dx + 1, rs, w, w_is1);
    ntt_fwd_b(T, lr, B);
}

/** Rows for a transform of size 2^l: at most 2^emax rows, each of at least 16 points. */
static int row_split(int l, int emax)
{
    int e = emax;
    if (e > l - 4) e = l - 4 > 0 ? l - 4 : 0;
    CTL(4);
    return e;
}

/** (c, d) = adj(M) (a, b) mod X^N - 1 (N = 2^l), times N: c = r22 a - r12 b, d = r11 b - r21 a.  a, b of lengths la, lb
 *  (folded mod X^N - 1); c, d are N-word buffers (c may equal a and d equal b when la, lb <= N, in place).  The entries are
 *  transformed per row of 2^(l-e) points; scratch 2 * 2^(l-e) words. */
static void apply_adj(const mat *M, const fp *a, long la, const fp *b, long lb, fp *c, fp *d, int l, int e)
{
    long N = 1L << l;
    if (c != a) fold(c, a, la, N, FP_ONE, 1);
    else fold1_inplace(c, la, N);
    if (d != b) fold(d, b, lb, N, FP_ONE, 1);
    else fold1_inplace(d, lb, N);
    CTL(4);
    ntt_fwd(c, l, 0);
    ntt_fwd(d, l, 0);
    int lr = l - e;
    long rs = 1L << lr;
    size_t mk = amark();
    fp *T = aalloc(rs), *U = aalloc(rs);
    for (uint32_t rho = 0; rho < (1u << e); rho++) {
        uint32_t B;
        fp w = row_root(l, e, rho, &B);
        int w1 = rho == 0;
        fp *cr = c + rho * rs, *dr = d + rho * rs;
        CTL(4);
        row_entry(T, M->e[3], M->d[3], rs, lr, B, w, w1);
        for (long i = 0; i < rs; i++) U[i] = fp_mul(T[i], cr[i]);
        LD(2 * rs);
        ST(rs);
        LOOPC(rs);
        if (M->d[1] >= 0) {
            row_entry(T, M->e[1], M->d[1], rs, lr, B, w, w1);
            for (long i = 0; i < rs; i++) U[i] = fp_sub(U[i], fp_mul(T[i], dr[i]));
            LD(3 * rs);
            ST(rs);
            LOOPC(rs);
        }
        row_entry(T, M->e[0], M->d[0], rs, lr, B, w, w1);
        for (long i = 0; i < rs; i++) dr[i] = fp_mul(T[i], dr[i]);
        LD(2 * rs);
        ST(rs);
        LOOPC(rs);
        if (M->d[2] >= 0) {
            row_entry(T, M->e[2], M->d[2], rs, lr, B, w, w1);
            for (long i = 0; i < rs; i++) dr[i] = fp_sub(dr[i], fp_mul(T[i], cr[i]));
            LD(3 * rs);
            ST(rs);
            LOOPC(rs);
        }
        copy(cr, U, rs);
        CTL(4);
    }
    LOOPC(1u << e);
    arel(mk);
    ntt_inv(c, l, 0);
    ntt_inv(d, l, 0);
}

/** dst blocks 0, 1, 2 (rs words each) = src mod (Y - 1), (Y + 1), (Y - i) for Y = X^rs, src of length len <= 4 rs:
 *  with src = A0 + A1 Y + A2 Y^2 + A3 Y^3, R0 = (A0 + A2) + (A1 + A3), R1 = (A0 + A2) - (A1 + A3),
 *  R2 = (A0 - A2) + i (A1 - A3).  Works in place (dst == src). */
static void split3(fp *dst, const fp *src, long len, long rs, fp ii)
{
    for (long i = 0; i < rs; i++) {
        fp a0 = i < len ? src[i] : FP_ZERO, a1 = rs + i < len ? src[rs + i] : FP_ZERO;
        fp a2 = 2 * rs + i < len ? src[2 * rs + i] : FP_ZERO, a3 = 3 * rs + i < len ? src[3 * rs + i] : FP_ZERO;
        fp s0 = fp_add(a0, a2), s1 = fp_add(a1, a3), d0 = fp_sub(a0, a2), d1 = fp_sub(a1, a3);
        dst[i] = fp_add(s0, s1);
        dst[rs + i] = fp_sub(s0, s1);
        dst[2 * rs + i] = fp_add(d0, fp_mul(ii, d1));
        CTL(8);
    }
    LD(len < 4 * rs ? len : 4 * rs);
    ST(3 * rs);
    LOOPC(rs);
}

/** The same as apply_adj with N = 3 2^(l-2): rows 0, 1, 2 of the 4-row split of the size-2^l transform (moduli Y - 1,
 *  Y + 1, Y - i, Y = X^(2^(l-2))), then combined: for c = C0 + C1 Y + C2 Y^2 the row residues R0, R1, R2 give
 *  4 C0 = (R0 + R1) + 2 R2 - i (R0 - R1), 4 C1 = 2 (R0 - R1), 4 C2 = (R0 + R1) - 2 R2 + i (R0 - R1).  c, d hold
 *  3 2^(l-2) words (in place allowed if the buffers hold 2^l words); scratch 2 rows. */
static void apply_adj3(const mat *M, const fp *a, long la, const fp *b, long lb, fp *c, fp *d, int l, fp *sav)
{
    int lr = l - 2;
    long rs = 1L << lr, N4 = 4 * rs;
    uint32_t B2;
    fp ii = row_root(l, 2, 2, &B2);
    CTL(4);
    if (c == a && la > N4) {
        fold1_inplace(c, la, N4);
        la = N4;
    }
    if (d == b && lb > N4) {
        fold1_inplace(d, lb, N4);
        lb = N4;
    }
    if (c != a && la > N4) {
        fp *t = aalloc(N4);
        fold(t, a, la, N4, FP_ONE, 1);
        split3(c, t, N4, rs, ii);
        arel(amark() - N4);
    } else split3(c, a, la, rs, ii);
    if (d != b && lb > N4) {
        fp *t = aalloc(N4);
        fold(t, b, lb, N4, FP_ONE, 1);
        split3(d, t, N4, rs, ii);
        arel(amark() - N4);
    } else split3(d, b, lb, rs, ii);
    size_t mk = amark();
    fp *T = aalloc(rs), *U = aalloc(rs);
    for (uint32_t rho = 0; rho < 3; rho++) {
        uint32_t B;
        fp w = row_root(l, 2, rho, &B);
        int w1 = rho == 0;
        fp *cr = c + rho * rs, *dr = d + rho * rs;
        CTL(5);
        ntt_fwd_b(cr, lr, B);
        ntt_fwd_b(dr, lr, B);
        fp *Te[4];
        for (int i = 0; i < 4; i++) Te[i] = sav && rho < 2 ? sav + i * 2 * rs + rho * rs : T;
        CTL(24);
        LOOPC(4);
        fp *T3 = Te[3];
        row_entry(T3, M->e[3], M->d[3], rs, lr, B, w, w1);
        for (long i = 0; i < rs; i++) U[i] = fp_mul(T3[i], cr[i]);
        LD(2 * rs);
        ST(rs);
        LOOPC(rs);
        if (M->d[1] >= 0) {
            fp *T1 = Te[1];
            row_entry(T1, M->e[1], M->d[1], rs, lr, B, w, w1);
            for (long i = 0; i < rs; i++) U[i] = fp_sub(U[i], fp_mul(T1[i], dr[i]));
            LD(3 * rs);
            ST(rs);
            LOOPC(rs);
        }
        fp *T0 = Te[0];
        row_entry(T0, M->e[0], M->d[0], rs, lr, B, w, w1);
        for (long i = 0; i < rs; i++) dr[i] = fp_mul(T0[i], dr[i]);
        LD(2 * rs);
        ST(rs);
        LOOPC(rs);
        if (M->d[2] >= 0) {
            fp *T2 = Te[2];
            row_entry(T2, M->e[2], M->d[2], rs, lr, B, w, w1);
            for (long i = 0; i < rs; i++) dr[i] = fp_sub(dr[i], fp_mul(T2[i], cr[i]));
            LD(3 * rs);
            ST(rs);
            LOOPC(rs);
        }
        copy(cr, U, rs);
        ntt_inv_b(cr, lr, B);
        ntt_inv_b(dr, lr, B);
        CTL(4);
    }
    LOOPC(3);
    arel(mk);
    for (int z = 0; z < 2; z++) {
        fp *x = z ? d : c;
        for (long i = 0; i < rs; i++) {
            fp r0 = x[i], r1 = x[rs + i], r2 = x[2 * rs + i];
            fp u = fp_add(r0, r1), v = fp_sub(r0, r1), iv = fp_mul(ii, v), t2 = fp_add(r2, r2);
            x[i] = fp_sub(fp_add(u, t2), iv);
            x[rs + i] = fp_add(v, v);
            x[2 * rs + i] = fp_add(fp_sub(u, t2), iv);
        }
        LD(3 * rs);
        ST(3 * rs);
        LOOPC(rs);
    }
    LOOPC(2);
}

/** O = A B for 2x2 matrices, entries of degree <= k < N = 2^l (O's entries are N-word arrays, disjoint from A and B).
 *  B's entries are transformed per row (4 rows of scratch), A's streamed through one more row; if Asav is given (e = 1
 *  only), A's entry i is taken already transformed from Asav + i N. */
static void mat_mul(mat *O, const mat *A, const mat *Bm, long k, int e, const fp *Asav)
{
    int l;
    long N = pow2l(k + 1, &l);
    if (e > l) e = l;
    int lr = l - e;
    long rs = 1L << lr;
    size_t mk = amark();
    fp *TB[4], *T = aalloc(rs);
    for (int i = 0; i < 4; i++) TB[i] = aalloc(rs);
    LOOPC(4);
    for (uint32_t rho = 0; rho < (1u << e); rho++) {
        uint32_t B;
        fp w = row_root(l, e, rho, &B);
        int w1 = rho == 0;
        long off = rho * rs;
        CTL(3);
        for (int i = 0; i < 4; i++) {
            if (Bm->d[i] >= 0) row_entry(TB[i], Bm->e[i], Bm->d[i], rs, lr, B, w, w1);
            CTL(2);
        }
        LOOPC(4);
        /* O[2r + s] = A[2r] B[s] + A[2r + 1] B[2 + s] */
        for (int r = 0; r < 2; r++) {
            fp *o0 = O->e[2 * r] + off, *o1 = O->e[2 * r + 1] + off;
            int first = 1;
            for (int t = 0; t < 2; t++) {
                int ai = 2 * r + t;
                CTL(4);
                if (A->d[ai] < 0) continue;
                const fp *TA_ = T;
                if (Asav) TA_ = Asav + ai * N + off;
                else row_entry(T, A->e[ai], A->d[ai], rs, lr, B, w, w1);
                CTL(2);
                for (int s = 0; s < 2; s++) {
                    fp *o = s ? o1 : o0;
                    const fp *tb = TB[2 * t + s];
                    CTL(4);
                    if (Bm->d[2 * t + s] < 0) {
                        if (first) {
                            for (long i = 0; i < rs; i++) o[i] = FP_ZERO;
                            ST(rs);
                            LOOPC(rs);
                        }
                        continue;
                    }
                    if (first) {
                        for (long i = 0; i < rs; i++) o[i] = fp_mul(TA_[i], tb[i]);
                        LD(2 * rs);
                    } else {
                        for (long i = 0; i < rs; i++) o[i] = fp_add(o[i], fp_mul(TA_[i], tb[i]));
                        LD(3 * rs);
                    }
                    ST(rs);
                    LOOPC(rs);
                }
                LOOPC(2);
                first = 0;
            }
            LOOPC(2);
            if (first) {
                for (long i = 0; i < rs; i++) o0[i] = o1[i] = FP_ZERO;
                ST(2 * rs);
                LOOPC(rs);
            }
        }
        LOOPC(2);
    }
    LOOPC(1u << e);
    arel(mk);
    for (int i = 0; i < 4; i++) {
        ntt_inv(O->e[i], l, 0);
        O->d[i] = pdeg(O->e[i], N);
    }
    LOOPC(4);
}

/** Pseudo-division in place: beta^(t+1) A = Q B + E, t = da - db >= 0, beta = lc(B); A[0..db) becomes E (degree < db),
 *  Q (t + 1 words) and beta^(t+1) are returned. */
static void pdiv(fp *A, long da, const fp *B, long db, fp *Q, fp *bt)
{
    long t = da - db;
    LD(1);
    fp beta = B[db], bp = FP_ONE;
    if (t == 1) {
        /* Q = beta a_n X + (beta a_(n-1) - a_n b_(n-2)); E_i = beta^2 a_i - q1 b_(i-1) - q0 b_i */
        LD(3);
        fp an = A[da], an1 = A[da - 1], bn2 = db >= 1 ? B[db - 1] : FP_ZERO;
        fp q1 = fp_mul(beta, an), q0 = fp_sub(fp_mul(beta, an1), fp_mul(an, bn2)), b2 = fp_sqr(beta);
        CTL(2);
        fp prev = FP_ZERO;
        for (long i = 0; i < db; i++) {
            fp bi = B[i];
            A[i] = fp_sub(fp_sub(fp_mul(b2, A[i]), fp_mul(q1, prev)), fp_mul(q0, bi));
            prev = bi;
        }
        LD(2 * db);
        ST(db);
        LOOPC(db);
        Q[0] = q0;
        Q[1] = q1;
        ST(2);
        *bt = b2;
        return;
    }
    for (long j = t; j >= 0; j--) {
        LD(1);
        fp cj = A[db + j];
        for (long i = 0; i < db + j; i++) A[i] = fp_mul(beta, A[i]);
        LD(db + j);
        ST(db + j);
        LOOPC(db + j);
        for (long i = 0; i < db; i++) A[j + i] = fp_sub(A[j + i], fp_mul(cj, B[i]));
        LD(2 * db);
        ST(db);
        LOOPC(db);
        for (long i = j + 1; i <= t; i++) Q[i] = fp_mul(beta, Q[i]);
        LD(t - j);
        ST(t - j);
        LOOPC(t - j);
        Q[j] = cj;
        ST(1);
        bp = fp_mul(bp, beta);
        CTL(2);
    }
    LOOPC(t + 1);
    *bt = bp;
}

/** M <- M [[Q, 1], [bt, 0]] in place (entry capacity >= deg M + t + 1): new r11 = r11 Q + bt r12 (into r12's slot),
 *  new r12 = r11; likewise for the second row. */
static void mat_q(mat *M, const fp *Q, long t, fp bt)
{
    for (int r = 0; r < 2; r++) {
        fp *x = M->e[2 * r], *y = M->e[2 * r + 1];
        long dx = M->d[2 * r], dy = M->d[2 * r + 1];
        long dn = dx < 0 ? dy : dx + t;
        CTL(6);
        if (t == 1 && dx >= 0) {
            /* y_i <- bt y_i + Q0 x_i + Q1 x_(i-1), keeping x_(i-1) of the previous iteration (ascending) */
            fp q0 = Q[0], q1 = Q[1], xp = FP_ZERO;
            LD(2);
            for (long i = 0; i <= dn; i++) {
                fp xi = i <= dx ? x[i] : FP_ZERO, s = fp_add(fp_mul(q0, xi), fp_mul(q1, xp));
                if (i <= dy) s = fp_add(s, fp_mul(bt, y[i]));
                y[i] = s;
                xp = xi;
                CTL(4);
            }
            LD(dx + 1 + dy + 1);
            ST(dn + 1);
            LOOPC(dn + 1);
            M->e[2 * r] = y;
            M->e[2 * r + 1] = x;
            M->d[2 * r] = dn;
            M->d[2 * r + 1] = dx;
            CTL(4);
            continue;
        }
        for (long i = dn; i >= 0; i--) {
            fp s = FP_ZERO;
            if (i <= dy) {
                LD(1);
                s = fp_mul(bt, y[i]);
            }
            long j0 = i - dx > 0 ? i - dx : 0, j1 = i < t ? i : t;
            CTL(6);
            for (long j = j0; j <= j1; j++) s = fp_add(s, fp_mul(Q[j], x[i - j]));
            LD(2 * (j1 - j0 + 1 > 0 ? j1 - j0 + 1 : 0));
            LOOPC(j1 - j0 + 1 > 0 ? j1 - j0 + 1 : 0);
            y[i] = s;
            ST(1);
        }
        LOOPC(dn + 1);
        M->e[2 * r] = y;
        M->e[2 * r + 1] = x;
        M->d[2 * r] = dn;
        M->d[2 * r + 1] = dx;
        CTL(4);
    }
    LOOPC(2);
}

static long QCAP;
static fp *QBUF;
static long KSAVE; /* nodes with k <= KSAVE keep M1's transforms (set by hg_gcd: below the top level only) */

/** Euclid with budget k on copies of a (degree n <= 2k after truncation) and b: M accumulates the steps. */
static void hgcd_base(const fp *a, long n, const fp *b, long db, long k, mat *M)
{
    size_t mk = amark();
    fp *A = aalloc(n + 1), *Bv = aalloc(n + 1), *Q = aalloc(n + 2);
    copy(A, a, n + 1);
    copy(Bv, b, db + 1);
    mat_id(M);
    long da = n, d = 0;
    while (db >= 0 && d + da - db <= k) {
        long t = da - db;
        fp bt;
        pdiv(A, da, Bv, db, Q, &bt);
        mat_q(M, Q, t, bt);
        fp *tmp = A;
        A = Bv;
        Bv = tmp;
        long de = pdeg(Bv, db);
        da = db;
        db = de;
        d += t;
        CTL(10);
    }
    CTL(4);
    arel(mk);
}

#ifndef HG_BASE
#define HG_BASE 48
#endif
#ifndef ROWS_MM
#define ROWS_MM 1
#endif
static int ROWS_A = 3, ROWS_M = ROWS_MM;

/** hgcd(a, b, k) into M (entries with capacity mcap(k) each, at a region that may overlap a and b: they are read only
 *  before M is written). */
static void hgcd(const fp *a, long n, const fp *b, long db, long k, mat *M)
{
    CTL(4);
    if (db < 0 || n - db > k) {
        mat_id(M);
        return;
    }
    long s = n - 2 * k;
    CTL(2);
    if (s > 0) {
        a += s;
        b += s;
        n -= s;
        db -= s;
        CTL(4);
    }
    CTL(2);
    if (k <= HG_BASE) {
        PROF_BEGIN;
        hgcd_base(a, n, b, db, k, M);
        PROF_END(0);
        return;
    }
    size_t mk = amark();
    long k1 = k / 2, cap1 = mcap(k1);
    int lm;
    long Nm = pow2l(k + 1, &lm);
    /* save: keep the transforms of M1 on the two rows of the final product (from the apply) and form M = M1 (Q M2) */
    int save = k <= KSAVE && ROWS_M == 1 && lm >= 6;
    CTL(6);
    fp *SAV = save ? aalloc(4 * Nm) : NULL;
    mat M1;
    mat_at(&M1, aalloc(4 * cap1), cap1);
    fp *base1 = M1.e[0];
    hgcd(a, n, b, db, k1, &M1);
    long d1 = M1.d[0], dc = n - d1;
    int l;
    long N = pow2l(dc + 1, &l);
    int three = l >= 6 && 3 * (N >> 2) >= dc + 1;
    CTL(4);
    if (three) N = 3 * (N >> 2);
    save = save && three && (1L << (l - 2)) == Nm / 2;
    CTL(4);
    fp *c = aalloc(2 * N), *d = c + N;
    {
        PROF_BEGIN;
        if (three) apply_adj3(&M1, a, n + 1, b, db + 1, c, d, l, save ? SAV : NULL);
        else apply_adj(&M1, a, n + 1, b, db + 1, c, d, l, row_split(l, ROWS_A));
        PROF_END(1);
    }
    long dd = pdeg(d, N);
    CTL(4);
    if (dd < 0 || dc - dd > k - d1) {
        for (int i = 0; i < 4; i++) {
            copy(M->e[i], M1.e[i], M1.d[i] + 1);
            M->d[i] = M1.d[i];
        }
        LOOPC(4);
        arel(mk);
        return;
    }
    long t = dc - dd;
    fp bt, *Q = t + 2 > QCAP ? aalloc(t + 2) : QBUF;
    pdiv(c, dc, d, dd, Q, &bt);
    long de = pdeg(c, dd);
    long k2 = k - d1 - t, s2 = dd - 2 * k2;
    if (s2 < 0) s2 = 0;
    long len = dd - s2 + 1;
    CTL(8);
    if (save) {
        /* M1's coefficients are no longer needed: the (e, d) tops go to M1's region, then M2 (Q M2 needs t more) */
        fp *ev = base1, *dv = base1 + len;
        for (long i = 0; i < len; i++) ev[i] = s2 + i <= de ? c[s2 + i] : FP_ZERO;
        LD(len);
        ST(len);
        LOOPC(len);
        CTL(2 * len);
        copy(dv, d + s2, len);
        long cap2 = mcap(k2);
        if (cap2 < k2 + t + 2) cap2 = k2 + t + 2;
        long r2 = 4 * cap2 > 2 * len ? 4 * cap2 : 2 * len;
        CTL(6);
        arel((size_t)(base1 - AR) + (size_t)r2);
        fp *Qs = aalloc(t + 1);
        copy(Qs, Q, t + 1);
        mat M2;
        mat_at(&M2, base1, cap2);
        hgcd(dv, dd - s2, ev, de - s2, k2, &M2);
        /* Q M2 = [[Q, 1], [bt, 0]] M2: row 1 <- Q row1 + row2 (into row 2's slots), row 2 <- bt row1 (in place) */
        for (int col = 0; col < 2; col++) {
            fp *x = M2.e[col], *y = M2.e[2 + col];
            long dx = M2.d[col], dy = M2.d[2 + col];
            long dn = dx < 0 ? dy : dx + t;
            CTL(6);
            for (long i = dn; i >= 0; i--) {
                fp acc = i <= dy ? y[i] : FP_ZERO;
                long j0 = i - dx > 0 ? i - dx : 0, j1 = i < t ? i : t;
                for (long j = j0; j <= j1; j++) acc = fp_add(acc, fp_mul(Qs[j], x[i - j]));
                LD(1 + 2 * (j1 - j0 + 1 > 0 ? j1 - j0 + 1 : 0));
                LOOPC(j1 - j0 + 1 > 0 ? j1 - j0 + 1 : 0);
                y[i] = acc;
                ST(1);
                CTL(8);
            }
            LOOPC(dn + 1);
            for (long i = 0; i <= dx; i++) x[i] = fp_mul(bt, x[i]);
            LD(dx + 1);
            ST(dx + 1);
            LOOPC(dx + 1);
            M2.e[col] = y;
            M2.e[2 + col] = x;
            M2.d[col] = dn;
            M2.d[2 + col] = dx;
            CTL(4);
        }
        LOOPC(2);
        {
            PROF_BEGIN;
            mat_mul(M, &M1, &M2, k, ROWS_M, SAV);
            PROF_END(3);
        }
        arel(mk);
        return;
    }
    int wide = d1 + t + 1 > cap1;
    long capw = d1 + t + 2;
    CTL(4);
    if (wide) {
        /* abnormal quotient too large for the slots of M1: widen them (on top, moved down below) */
        mat W;
        mat_at(&W, aalloc(4 * capw), capw);
        for (int i = 0; i < 4; i++) {
            copy(W.e[i], M1.e[i], M1.d[i] + 1);
            W.d[i] = M1.d[i];
        }
        LOOPC(4);
        M1 = W;
    }
    mat_q(&M1, Q, t, bt);
    /* compact the top parts of e and d used by the second call to the start of the (d, e) region: e then d */
    fp *ev = c, *dv = c + len;
    for (long i = 0; i < len; i++) ev[i] = s2 + i <= de ? c[s2 + i] : FP_ZERO;
    LD(len);
    ST(len);
    LOOPC(len);
    CTL(2 * len);
    copy(dv, d + s2, len);
    /* the second call writes M2 over its inputs: region of 4 mcap(k2) words from c */
    long cap2 = mcap(k2), r2 = 4 * cap2 > 2 * len ? 4 * cap2 : 2 * len;
    CTL(4);
    if (wide) {
        fp *dst = c + r2, *src = M1.e[0] < M1.e[1] ? M1.e[0] : M1.e[1];
        for (int i = 0; i < 4; i++) src = M1.e[i] < src ? M1.e[i] : src;
        CTL(12);
        LOOPC(4);
        copy(dst, src, 4 * capw);
        for (int i = 0; i < 4; i++) M1.e[i] = dst + (M1.e[i] - src);
        LOOPC(4);
        CTL(12);
        arel((size_t)(c - AR) + (size_t)(r2 + 4 * capw));
    } else {
        arel((size_t)(c - AR) + (size_t)r2);
    }
    mat M2;
    mat_at(&M2, c, cap2);
    hgcd(dv, dd - s2, ev, de - s2, k2, &M2);
    {
        PROF_BEGIN;
        mat_mul(M, &M1, &M2, k, ROWS_M, NULL);
        PROF_END(3);
    }
    arel(mk);
}

/** gcd of a (degree da) and b (degree db < da) in place in buffers of n words each (with da < n); returns the degree of
 *  the gcd and sets *g to the buffer holding it (monic). */
long hg_gcd(fp *a, long da, fp *b, long db, long kmax, fp **g)
{
    QCAP = 64;
    QBUF = aalloc(QCAP);
    while (db >= 0) {
        CTL(2);
        if (da <= 2 * HG_BASE) {
            fp *Q = aalloc(da + 2);
            while (db >= 0) {
                fp bt;
                pdiv(a, da, b, db, Q, &bt);
                long de = pdeg(a, db);
                fp *t = a;
                a = b;
                b = t;
                da = db;
                db = de;
                CTL(6);
            }
            break;
        }
        long k = 1;
        while (2 * k + 1 <= kmax && 2 * k + 1 <= da / 2) {
            k = 2 * k + 1;
            CTL(7);
        }
        CTL(6);
        size_t mk = amark();
        long cap = mcap(k);
        KSAVE = k / 2;
        CTL(1);
        mat M;
        mat_at(&M, aalloc(4 * cap), cap);
        hgcd(a, da, b, db, k, &M);
        int l;
        long dm = M.d[0], dc = da - dm, N = pow2l(dc + 1, &l);
        int three = l >= 6 && 3 * (N >> 2) >= dc + 1;
        CTL(4);
        {
            PROF_BEGIN;
            if (three) apply_adj3(&M, a, da + 1, b, db + 1, a, b, l, NULL);
            else apply_adj(&M, a, da + 1, b, db + 1, a, b, l, row_split(l, ROWS_A));
            PROF_END(2);
        }
        arel(mk);
        da = dc;
        db = pdeg(b, da);
        CTL(4);
        if (db < 0) break;
        long t = da - db;
        fp bt;
        fp *Q = t + 2 > QCAP ? aalloc(t + 2) : QBUF;
        pdiv(a, da, b, db, Q, &bt);
        arel(mk);
        long de = pdeg(a, db);
        fp *tp = a;
        a = b;
        b = tp;
        da = db;
        db = de;
        CTL(8);
    }
    LD(1);
    fp il = fp_inv(a[da]);
    for (long i = 0; i <= da; i++) a[i] = fp_mul(a[i], il);
    LD(da + 1);
    ST(da + 1);
    LOOPC(da + 1);
    *g = a;
    return da;
}
```

### main.c

SHA-256 `26d0992a407cc9e096d6b6bb4f08dbeeb3d0387ef210eb4c44c00a0d1a644b8b`, 13665 bytes.

```c
/* Orchard Poseidon r = NR collision by the odd part of the line digest about centres c = 1, 2, ...: one deterministic run.
 *
 * Per trial: A centre; B g_c by evaluation; prep (start residue, 1/g on O1, g on O2); C R = S^((p-1)/2) mod g;
 * D G = gcd(g, R - 1); E a root S of G; F s = sqrt(S), the two line points c +- s and their canonical inputs;
 * G both reference hashes.  H output encoding.  I the report (formatting bound, one write, exit).  Usage: main [nr]
 * (default 3).  Built without a C library (nolibc.c). */
#include "ntt.h"
#include "stagec.h"
#include "stageb.h"
#include "line.h"
#include "hgcd.h"

long sys_write(int fd, const void *buf, size_t n);

#ifndef LMAXRUN
#define LMAXRUN 20
#endif
#define MAXTR 64
#define SPLIT_CAP 256
#define KMAX 131071

static fp REG[4 * ((size_t)1 << LMAXRUN)];

enum { S_INIT, S_SETUP, S_A, S_B, S_PREP, S_C, S_D, S_E, S_F, S_G, S_H, S_I, S_N };
static const char *SNAME[S_N] = {"init", "setup", "A", "B", "prep", "C", "D", "E", "F", "G", "H", "I"};

/* Charged constants (bounds on fixed work outside the per-operation counting):
 * STAGE_BK per stage switch (8 counter subtractions and additions with their loads and stores, about 50 operations);
 * TRIAL_BK per snapshot of the counters for the trial rows (8 loads and additions, about 16 operations);
 * PROLOGUE for the argument parse and the dimension and exponent-bit setup of main before the first stage;
 * CONSTS_GEN for the constants of consts.h computed by gen_consts.py (psi = 5^((p-1)/2^21) and its inverse: about 650
 * squarings and multiplications; 2^512 mod p; -p^-1 mod 2^64; 201 conversions to Montgomery form), charged here so that the
 * run includes all preprocessing;
 * stage I: FMT_PER_BYTE for every byte of the output buffer (formatting and copying, the buffer charged in full),
 * REPORT_LOOPS for the loops over the stage and trial rows, SYS_WRITE and SYS_EXIT for the two system calls. */
#define STAGE_BK 100
#define TRIAL_BK 20
#define PROLOGUE 5000
#define CONSTS_GEN 20000
#define OUTCAP 8192
#define FMT_PER_BYTE 400
#define REPORT_LOOPS 20000
#define SYS_WRITE (10000 + (OUTCAP << 3))
#define SYS_EXIT 10000
static struct ctr ST_ACC[S_N];
static struct ctr LAST;
static int CUR = -1;

/** Close the current stage (add the counters since it opened, the bookkeeping charge included) and open stage s
 *  (s < 0: close only). */
static void stage(int s)
{
    if (CUR >= 0) {
        CTL(STAGE_BK);
        uint64_t *acc = (uint64_t *)&ST_ACC[CUR], *now = (uint64_t *)&X, *last = (uint64_t *)&LAST;
        for (int i = 0; i < 8; i++) acc[i] += now[i] - last[i];
        LAST = X;
    } else {
        LAST = X;
        CTL(STAGE_BK);
    }
    CUR = s;
}

static const uint64_t EH[4] = {0xcc96987680000000ULL, 0x11234c7e04a67c8dULL, 0, 0x2000000000000000ULL}; /* (p-1)/2 */

/** Square root of a nonzero square a by Tonelli-Shanks (p - 1 = 2^32 q, nonresidue 5). */
static fp fp_sqrt(fp a)
{
    static const uint64_t Q[4] = {0x094cf91b992d30edULL, 0x00000000224698fcULL, 0x0000000000000000ULL, 0x40000000ULL};
    static const uint64_t Q1[4] = {0x04a67c8dcc969876ULL, 0x0000000011234c7eULL, 0x0000000000000000ULL, 0x20000000ULL}; /* (q-1)/2 */
    fp z = fp_pow(fp_from_u64(5), Q), x = fp_pow(a, Q1), b = fp_mul(fp_sqr(x), a);
    x = fp_mul(x, a);
    int m = 32;
    while (!fp_eq(b, FP_ONE)) {
        int i = 0;
        fp t = b;
        while (!fp_eq(t, FP_ONE)) {
            t = fp_sqr(t);
            i++;
            CTL(2);
        }
        fp y = z;
        for (int j = 0; j < m - i - 1; j++) y = fp_sqr(y);
        LOOPC(m - i - 1);
        z = fp_sqr(y);
        x = fp_mul(x, y);
        b = fp_mul(b, z);
        m = i;
        CTL(4);
    }
    return x;
}

/** r = x^E mod G (G monic of degree dg >= 2, x = X + delta), schoolbook; r has dg words.  Scratch t of 2 dg words. */
static void powmod_small(const fp *G, int dg, fp delta, fp *r, fp *t)
{
    for (int i = 0; i < dg; i++) r[i] = FP_ZERO;
    r[0] = FP_ONE;
    ST(dg);
    for (int bit = 253; bit >= 0; bit--) {
        for (int i = 0; i < 2 * dg; i++) t[i] = FP_ZERO;
        for (int i = 0; i < dg; i++)
            for (int j = 0; j < dg; j++) t[i + j] = fp_add(t[i + j], fp_mul(r[i], r[j]));
        if ((EH[bit >> 6] >> (bit & 63)) & 1) {
            for (int i = 2 * dg - 1; i > 0; i--) t[i] = fp_add(t[i - 1], fp_mul(t[i], delta));
            t[0] = fp_mul(t[0], delta);
        }
        for (int i = 2 * dg - 1; i >= dg; i--)
            for (int j = 0; j < dg; j++) t[i - dg + j] = fp_sub(t[i - dg + j], fp_mul(t[i], G[j]));
        for (int i = 0; i < dg; i++) r[i] = t[i];
        /* generous per-operation charge for this small schoolbook work */
        CTL(9 * (uint64_t)dg * dg * 3);
        LD(4 * (uint64_t)dg * dg);
        ST(2 * (uint64_t)dg * dg);
    }
}

/** Monic gcd of small polynomials u (deg du) and v (deg dv) by Euclid, in place; returns its degree, result in *out. */
static int gcd_small(fp *u, int du, fp *v, int dv, fp **out)
{
    while (dv >= 0) {
        fp il = fp_inv(v[dv]);
        for (int i = du - dv; i >= 0; i--) {
            fp q = fp_mul(u[i + dv], il);
            for (int j = 0; j <= dv; j++) u[i + j] = fp_sub(u[i + j], fp_mul(q, v[j]));
            CTL(9 * (uint64_t)(dv + 1));
            LD(2 * (uint64_t)(dv + 1));
            ST(dv + 1);
        }
        int de = dv - 1;
        while (de >= 0 && fp_is0(u[de])) de--;
        fp *t = u;
        u = v;
        v = t;
        du = dv;
        dv = de;
        CTL(8);
    }
    fp il = fp_inv(u[du]);
    for (int i = 0; i <= du; i++) u[i] = fp_mul(u[i], il);
    CTL(9 * (uint64_t)(du + 1));
    *out = u;
    return du;
}

/** A root of the squarefree split polynomial G (monic, degree dg >= 1) by equal-degree splitting with shifts 1, 2, ...,
 *  SPLIT_CAP (each shift splits a given pair of roots with probability about 1/2 over the shift; *ok = 0 ends the trial
 *  if the cap is reached). */
static fp find_root(fp *G, int dg, fp *scr, int *ok)
{
    *ok = 1;
    uint64_t delta = 1;
    CTL(2);
    while (dg > 1) {
        if (delta > SPLIT_CAP) {
            *ok = 0;
            return FP_ZERO;
        }
        CTL(4);
        fp *r = scr, *t = scr + dg, *u = scr + 3 * dg, *v = scr + 4 * dg + 1;
        fp dl = fp_from_u64(delta);
        powmod_small(G, dg, dl, r, t);
        r[0] = fp_sub(r[0], FP_ONE);
        for (int i = 0; i <= dg; i++) u[i] = G[i];
        int dr = dg - 1;
        while (dr >= 0 && fp_is0(r[dr])) dr--;
        for (int i = 0; i <= dr; i++) v[i] = r[i];
        CTL(9 * (uint64_t)(2 * dg + 2));
        fp *h;
        int dh = dr < 0 ? -1 : gcd_small(u, dg, v, dr, &h);
        CTL(12);
        if (dh >= 1 && dh < dg) {
            /* the roots of h are the roots of G with S + delta a square; continue in h (shifted back) */
            for (int i = 0; i <= dh; i++) G[i] = h[i];
            CTL(9 * (uint64_t)(dh + 1));
            dg = dh;
        }
        delta++;
        CTL(3);
    }
    LD(1);
    return fp_neg(G[0]);
}

static char OUT[OUTCAP];
static size_t ON;

static void out_c(char c)
{
    if (ON < OUTCAP) OUT[ON] = c;
    ON++;
}

static void out_s(const char *t)
{
    while (*t) out_c(*t++);
}

static void out_u(uint64_t v)
{
    char d[24];
    int k = 0;
    do {
        d[k++] = (char)('0' + v % 10);
        v /= 10;
    } while (v);
    while (k) out_c(d[--k]);
}

/** Stage H encoding: the canonical value of a as 64 hexadecimal digits (one conversion, 12 operations per digit). */
static void enc_hex(char *dst, fp a)
{
    uint64_t l[4];
    fp_to_limbs(a, l);
    for (int i = 0; i < 64; i++) {
        int pos = 63 - i;
        dst[i] = "0123456789abcdef"[(l[pos >> 4] >> (4 * (pos & 15))) & 15];
    }
    CTL(12 * 64 + 5);
}

static void copy_fp(fp *d, const fp *src, long n)
{
    for (long i = 0; i < n; i++) d[i] = src[i];
    LD(n);
    ST(n);
    LOOPC(n);
}

static int parse_int(const char *t)
{
    int v = 0;
    while (*t >= '0' && *t <= '9') v = 10 * v + (*t++ - '0');
    return v;
}

int main(int argc, char **argv)
{
    int nr = argc > 1 ? parse_int(argv[1]) : 3;
    size_t m = 15625;
    for (int i = 0; i < nr; i++) m *= 5;
    m = (m - 1) / 2;
    int L = 1;
    while (((size_t)1 << L) < m + 1) L++;
    if (L > LMAXRUN) return 1;
    size_t n = (size_t)1 << L;
    int t = 0;
    while (((size_t)2 << t) <= n - m && t < 128) t++;
    int nb = 253 - t;
    uint8_t bits[253];
    for (int i = 0; i < nb; i++) {
        int b = 252 - t - i;
        bits[i] = (EH[b >> 6] >> (b & 63)) & 1;
    }
    fp *R0 = REG, *R1 = REG + n, *R2 = REG + 2 * n, *R3 = REG + 3 * n;
    long kmax = (long)n / 6 < KMAX ? (long)n / 6 : KMAX;

    stage(S_INIT);
    CTL(PROLOGUE + CONSTS_GEN);
    tw_init();
    stagec_init();
    stage(S_SETUP);
    line_setup(nr);
    int found = 0, tr, ntr = 0;
    long tdeg[MAXTR + 1];
    size_t tpeak[MAXTR + 1];
    uint64_t tcost[MAXTR + 1];
    fp c = FP_ZERO, nk1 = FP_ZERO, rho1 = FP_ZERO, nk2 = FP_ZERO, rho2 = FP_ZERO, dig = FP_ZERO;
    for (tr = 1; tr <= MAXTR && !found; tr++) {
        stage(S_A);
        uint64_t t0 = ctr_total(&X);
        ntr = tr;
        tdeg[tr] = -2;
        tpeak[tr] = 0;
        CTL(6 + TRIAL_BK);
        c = fp_from_u64((uint64_t)tr);
        stage(S_B);
        stage_b(c, L, R1);
        stage(S_PREP);
        int bad = stage_prep(L, m, t, R1, R0, R3, R2);
        CTL(2);
        if (bad) {
            CTL(TRIAL_BK);
            tcost[tr] = ctr_total(&X) - t0;
            continue;
        }
        stage(S_C);
        fp kap;
        stage_c(R3, R2, R1, R0, L, bits, nb, &kap, 0, NULL);
        stage(S_D);
        ntt_inv(R0, L, 1);
        LD(1);
        R3[0] = fp_sub(R3[0], kap);
        ST(1);
        long db = (long)m - 1;
        while (db >= 0) {
            LD(1);
            if (!fp_is0(R3[db])) break;
            db--;
            CTL(3);
        }
        CTL(2);
        hg_arena(R1, 2 * n);
        fp *G;
        long dg = hg_gcd(R0, (long)m, R3, db, kmax, &G);
        tdeg[tr] = dg;
        tpeak[tr] = hg_peak;
        CTL(4);
        if (dg < 1) {
            CTL(TRIAL_BK);
            tcost[tr] = ctr_total(&X) - t0;
            continue;
        }
        stage(S_E);
        fp *Gs = R1, *scr = R1 + dg + 1;
        CTL(2);
        copy_fp(Gs, G, dg + 1);
        int okr;
        fp S = find_root(Gs, (int)dg, scr, &okr);
        CTL(2);
        if (!okr) {
            CTL(TRIAL_BK);
            tcost[tr] = ctr_total(&X) - t0;
            continue;
        }
        stage(S_F);
        fp s = fp_sqrt(S), w1 = fp_add(c, s), w2 = fp_sub(c, s);
        line_back(w1, &nk1, &rho1);
        line_back(w2, &nk2, &rho2);
        stage(S_G);
        fp h1 = ref_hash(nk1, rho1), h2 = ref_hash(nk2, rho2);
        CTL(6);
        if (fp_eq(h1, h2) && !(fp_eq(nk1, nk2) && fp_eq(rho1, rho2))) {
            found = 1;
            dig = h1;
        }
        CTL(TRIAL_BK);
            tcost[tr] = ctr_total(&X) - t0;
    }
    LOOPC(ntr);
    stage(S_H);
    char hx[6][64];
    if (found) {
        enc_hex(hx[0], c);
        enc_hex(hx[1], nk1);
        enc_hex(hx[2], rho1);
        enc_hex(hx[3], nk2);
        enc_hex(hx[4], rho2);
        enc_hex(hx[5], dig);
    }
    stage(S_I);
    CTL((uint64_t)FMT_PER_BYTE * OUTCAP + REPORT_LOOPS + SYS_WRITE + SYS_EXIT);
    stage(-1);

    uint64_t tot = 0, ttot = 0;
    out_s("Orchard Poseidon r=");
    out_u((uint64_t)nr);
    out_s(" m=");
    out_u(m);
    out_s(" n=");
    out_u(n);
    out_s(" steps=");
    out_u((uint64_t)nb);
    out_s(" kmax=");
    out_u((uint64_t)kmax);
    out_s("\n");
    for (int i = 1; i <= ntr; i++) {
        out_s("trial ");
        out_u((uint64_t)i);
        out_s(" centre ");
        out_u((uint64_t)i);
        out_s(" degG ");
        if (tdeg[i] < 0) out_s(tdeg[i] == -2 ? "prep-failed" : "-1");
        else out_u((uint64_t)tdeg[i]);
        out_s(" arena_peak_words ");
        out_u(tpeak[i]);
        out_s(" ops ");
        out_u(tcost[i]);
        out_s("\n");
        ttot += tcost[i];
    }
    if (found) {
        static const char *lab[6] = {"centre ", "nk1 ", "rho1 ", "nk2 ", "rho2 ", "digest "};
        out_s("collision found after ");
        out_u((uint64_t)ntr);
        out_s(" trials\n");
        for (int i = 0; i < 6; i++) {
            out_s(lab[i]);
            for (int j = 0; j < 64; j++) out_c(hx[i][j]);
            out_s("\n");
        }
    } else {
        out_s("no collision\n");
    }
    for (int k = 0; k < S_N; k++) {
        uint64_t st = ctr_total(&ST_ACC[k]);
        tot += st;
        out_s("stage ");
        out_s(SNAME[k]);
        out_s(" ");
        out_u(st);
        out_s(" add ");
        out_u(ST_ACC[k].add);
        out_s(" sub ");
        out_u(ST_ACC[k].sub);
        out_s(" mul ");
        out_u(ST_ACC[k].mul);
        out_s(" sqr ");
        out_u(ST_ACC[k].sqr);
        out_s(" ld ");
        out_u(ST_ACC[k].ld);
        out_s(" st ");
        out_u(ST_ACC[k].st);
        out_s(" ctl ");
        out_u(ST_ACC[k].ctl);
        out_s(" unit ");
        out_u(ST_ACC[k].unit);
        out_s("\n");
    }
    out_s("stageD_profile base ");
    out_u(hg_prof[0]);
    out_s(" node_apply ");
    out_u(hg_prof[1]);
    out_s(" driver_apply ");
    out_u(hg_prof[2]);
    out_s(" products ");
    out_u(hg_prof[3]);
    out_s("\n");
    uint64_t all = ctr_total(&X);
    out_s("total ");
    out_u(tot);
    out_s(" counters ");
    out_u(all);
    out_s(" trials ");
    out_u(ttot);
    out_s(" outside_trials ");
    out_u(all - ttot);
    out_s(" RECONCILE ok=");
    out_u(tot == all);
    out_s("\n");
    if (ON > OUTCAP) return 3;
    sys_write(1, OUT, ON);
    return found ? 0 : 2;
}
```

### nolibc.c

SHA-256 `6e4edec4ee9e080bffe99132151a4aeddd41028d77a40da38ba31157d972836e`, 1830 bytes.

```c
/* Process entry, the two system calls of the run (write once, exit_group once) and the memory primitives the compiler may
 * emit, for a static executable without any C library (x86-64 Linux). */
#include <stddef.h>
#include <stdint.h>

int main(int argc, char **argv);

/** write(2). */
long sys_write(int fd, const void *buf, size_t n)
{
    long r;
    __asm__ volatile("syscall" : "=a"(r) : "a"(1L), "D"((long)fd), "S"(buf), "d"(n) : "rcx", "r11", "memory");
    return r;
}

/** exit_group(2). */
__attribute__((noreturn)) void sys_exit(int code)
{
    __asm__ volatile("syscall" : : "a"(231L), "D"((long)code) : "rcx", "r11", "memory");
    __builtin_unreachable();
}

/** Abort the run with the given exit status (used only on an internal capacity error). */
__attribute__((noreturn)) void die(int code) { sys_exit(code); }

void *memcpy(void *d, const void *s, size_t n)
{
    unsigned char *dp = d;
    const unsigned char *sp = s;
    while (n--) *dp++ = *sp++;
    return d;
}

void *memmove(void *d, const void *s, size_t n)
{
    unsigned char *dp = d;
    const unsigned char *sp = s;
    if (dp < sp) {
        while (n--) *dp++ = *sp++;
    } else {
        while (n--) dp[n] = sp[n];
    }
    return d;
}

void *memset(void *d, int c, size_t n)
{
    unsigned char *dp = d;
    while (n--) *dp++ = (unsigned char)c;
    return d;
}

int memcmp(const void *a, const void *b, size_t n)
{
    const unsigned char *x = a, *y = b;
    for (size_t i = 0; i < n; i++)
        if (x[i] != y[i]) return x[i] < y[i] ? -1 : 1;
    return 0;
}

__attribute__((used, noreturn)) void c_start(long *sp)
{
    int argc = (int)sp[0];
    char **argv = (char **)(sp + 1);
    sys_exit(main(argc, argv));
}

__asm__(".text\n.global _start\n_start:\n  xor %rbp, %rbp\n  mov %rsp, %rdi\n  and $-16, %rsp\n  call c_start\n  hlt\n");
```

### gen_consts.py

SHA-256 `201a84e5c44fd5f15cbb6da7bcf6b34b2e8b79553c0216dcc7716541abfc7fee`, 2494 bytes.

```python
#!/usr/bin/env python3
"""Write consts.h: the Pallas modulus, Montgomery constants, the deployed Orchard round constants and MDS (read from
pareto/orchard-pallas-constants.json, never regenerated), and the roots of unity used by the transforms, all in Montgomery form.

Usage: python3 -I gen_consts.py <orchard-pallas-constants.json> > consts.h
"""
import json
import sys

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
R = 1 << 256
K = 21                      # largest transform tree: 2^K points; psi_K is a primitive 2^K-th root of unity
TA_BITS = 11                # twiddle exponent split: psi^e = TA[e & 2047] * TB[e >> 11]


def limbs(x):
    """Return the four little-endian 64-bit limbs of x as a C initializer."""
    return '{0x%016xULL, 0x%016xULL, 0x%016xULL, 0x%016xULL}' % tuple((x >> (64 * i)) & (2**64 - 1) for i in range(4))


def mont(x):
    """Return the Montgomery form x * 2^256 mod p."""
    return x * R % P


def main():
    data = json.load(open(sys.argv[1]))
    rc = [[int(x, 16) for x in row] for row in data['round_constants']]
    mds = [[int(x, 16) for x in row] for row in data['mds']]
    gen = 5
    assert pow(gen, (P - 1) // 2, P) == P - 1 and pow(gen, (P - 1) // 3, P) != 1
    assert (P - 1) % (1 << 32) == 0
    psi = pow(gen, (P - 1) >> K, P)
    assert pow(psi, 1 << (K - 1), P) == P - 1
    inv = (-pow(P, -1, 1 << 64)) % (1 << 64)
    out = ['/* generated by gen_consts.py from %s (sha of the source json is checked by the caller) */' % data['source'],
           '#ifndef CONSTS_H', '#define CONSTS_H',
           '#define P_LIMBS %s' % limbs(P),
           '#define P_INV 0x%016xULL /* -p^-1 mod 2^64 */' % inv,
           '#define R2_LIMBS %s /* 2^512 mod p */' % limbs(R * R % P),
           '#define ONE_LIMBS %s /* Montgomery form of 1 */' % limbs(mont(1)),
           '#define TREE_K %d' % K,
           '#define TA_BITS %d' % TA_BITS,
           '#define PSI_LIMBS %s /* Montgomery form of psi = 5^((p-1)/2^K) */' % limbs(mont(psi)),
           '#define PSI_INV_LIMBS %s' % limbs(mont(pow(psi, P - 2, P)))]
    out.append('static const fp RC[64][3] = {')
    out += ['  {%s},' % ', '.join('{' + limbs(mont(x)) + '}' for x in row) for row in rc]
    out.append('};')
    out.append('static const fp MDS[3][3] = {')
    out += ['  {%s},' % ', '.join('{' + limbs(mont(x)) + '}' for x in row) for row in mds]
    out.append('};')
    out.append('#endif')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
```

