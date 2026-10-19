# Orchard Poseidon, r = 3: a deterministic program and its operation count derived from the source (two free rounds on a line, odd part about a centre, value-domain powering on truncated point sets, half-gcd)

## 1. Claim

Target: `poseidon-orchard-r3-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, partial rounds 4, 5 and 6, full rounds
60-63, state `[nk, rho, 2^65]`, digest = coordinate 0 of the output state). Output: two distinct canonical pairs `(nk, rho)` with equal
digests.

* `success_probability = 1`. The procedure is deterministic: it has no random choices and no input, and it tries the centres
  `c_i = i` in the fixed order `i = 1, 2, 3, ...` (at most `MAXTR = 64` trials). On this target it ends in trial 1 with a verified
  collision. This follows from the certificate and the algorithm, not from a run. The certificate pair lies on the line `j = 0`
  with midpoint `c = 1` (section 5.1, checkable from the certificate alone), so `g_1` has a nonzero square root `S` and
  `G = gcd(g_1, S^((p-1)/2) - 1)` has degree at least 1. Stages A to G compute what section 4 states, given the premises H2 (the
  data-dependent branches take their generic outcomes, 6.1) and, when `deg G >= 2`, H3 (shift splitting, 4.7). This is not a
  probability over centres. The centre order starts at the canonical first centre `c = 1`; that this centre succeeds on this line
  was public before (edd943c, 4bcabff8), and the program stores no instance-specific data.
* `time_log2 = 27.88161` in target-compression units (`C(3) = 216 + 21*3 = 279` primitive operations per unit). Under the
  premises H1-H3, on this target the procedure executes at most `N_claim = 68,992,558,203` operations (section 6), and
  `log2(N_claim / 279) = 27.881600`, rounded up at five decimals.
  - Section 6 derives this count from the source of section 9. Each executed statement carries its charge (rules of 4.2), and a
    stage's count is the sum over the statements it executes.
  - Under H2 every data-dependent branch of stages A to D has a fixed outcome, and every length is a function of the dimensions.
    So these stages have fixed counts: stage C in closed form (6.3), stages B and prep by their components (6.4), stage D by
    its recursion (6.5).
  - Stage E is bounded over `1 <= deg G <= 8` and every number of shifts up to the cap of 256. Stage F is bounded over every
    path of its square-root loop (6.6). The other stages are fixed.
  - For `deg G = 1` the count is exactly `68,808,527,086`. The claim adds `184,031,117` operations so that it holds for every
    `deg G <= 8`.
  - Appendix A transcribes the charge statements into a cost model that evaluates these counts.

  The twiddle tables and the constants are built inside the run (or charged in it). There is no separate preprocessing and no
  advice: claim.json records `preprocessing_log2 = 0` and `nonuniform_advice_log2_bytes = 0` (meaning none).
* `memory_log2_bytes = 26.9095`. This is `126,051,522` bytes (section 7): the whole statically linked executable image (code,
  data and bss; the bss holds every buffer) plus a 65,536-byte stack bound, rounded up at four decimals.
  - The stack bound is derived from GCC's per-function frame sizes for the same build. The deepest call chain is
    39,456 bytes, which leaves 26,064 bytes for the arguments, environment and auxiliary vector of the process
    (the program needs no environment).
  - The stage-D arena, inside the bss, peaks at 1,900,548 of its 1,966,080 words on the generic path (derived in 6.5).
  - The memory penalty is `26.9095 - 20 = 6.9095`, so the normalized cost is `27.88161 + 6.9095 = 34.79111`.
* Dimensions: the line polynomial `g_c` has degree `m = 976562`. All transforms are radix-2 transforms on the 2-power roots of unity
  (the 2-adicity of `p - 1` is 32), on the tree of the `2^21`-th roots. Let `n = 2^20` and `n' = 15 * 2^16 = 983040 > m`. The point
  sets of stages B and C are `O1` = `H_20` without one coset of `H_16` (`n'` points) and `O2`, the same 15 cosets inside the coset
  `psi H_20` (section 4.3). Stage D uses products on `2^l` or `3 * 2^(l-2)` points, and its first product on `O1` (15 rows of `2^16`).
* Method: two free rounds on a special line make the digest a univariate polynomial `F` of degree `5^9`. Its odd part about a
  centre `c` gives `g_c`, and the roots of `g_c` that are squares give collisions. They are the roots of
  `gcd(g_c, S^((p-1)/2) - 1)`. This is the known approach of edd943c (0xshikhar) and of our earlier entry 4bcabff8. The source
  (section 9) is our own and is the 4bcabff8 program with these changes:
  - `g_c` is interpolated from its values on `O1` (`2 n'` line evaluations) and is never transformed to more than `n'` points.
  - The powering is a Montgomery squaring in the value domain of `O1` and `O2`, four truncated transforms of `n'` points per
    step, with `P1 = (X^n - 1) / (X^(n/16) - c1)` (section 4.5), and a start residue that absorbs 17 zero bits of the exponent.
  - The gcd is an inversion-free half-gcd whose products are evaluated row by row. Below the top level the transforms and the
    values of the factors are reused across the levels of the recursion (section 4.6).

  Counts for comparison: edd943c `N = 317,054,280,703`, memory 138,396,180 bytes, normalized 37.12612; 4bcabff8
  `N = 87,714,039,092`, memory 134,473,813 bytes, normalized 35.23077.
* Premises, declared in claim.json, all score-critical:
  - H1: the charging model of 4.2 (the same model as edd943c and 4bcabff8: field operations, loads and stores with address
    formation, loop and control operations, and an 18-word register file).
  - H2: the generic path on this target (6.1).
  - H3: shift splitting, which matters only when `deg G >= 2` (4.7).
* Corroboration, not used by the claim: we executed the instrumented program once (about 14 minutes on one core). It took
  the generic path with `deg G = 1`, and every counter it printed equals the count derived in section 6 for that path (6.8). The
  organizer did not run it.
* **Disclosure:** the collision is the same pair as the certificates of edd943c, 4bcabff8 and a41aecdd. All of them use the line
  `j = 0` and the centre `c = 1`, and the root of `g_1` that they find is determined by the target. The claim is the cost of this
  program, not the novelty of the pair. This package revises a41aecdd (the same program and source): there the count was claimed
  as the output of the executed run; here it is derived from the source, with the run only as corroboration.

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
starting from an affine function of `W`. Hence the digest is `F(W)` with `deg F <= D = 5^9 = 1953125`. Equality holds: propagating the
leading coefficients (the state after round 1 has leading coefficient vector `beta` in `W`; a full round maps it to `M (lc_k^5)_k`,
a partial round to `M (lc_0^5, 0, 0)^T`; round constants do not reach the top degree) gives no cancellation and
`lc(F) = 0x11f9cfdeecb8c5965318cbdc58480d2e6db510f12862658af639ce81578c3e23`. So `g_c` (section 3) has degree exactly `m = (D - 1)/2` for every centre; the program's tests of coefficient
`m` (nonzero) and of the coefficients above it up to `n' - 1` (zero) in `stage_prep` therefore always pass. For every `W` in `F_p`,
`F(W)` is the reference digest of the canonical pair built from `tau = W^e` (sections 2.1-2.2). Stage G recomputes both digests
with the full reference permutation, and the organizer's hash checks the certificate.

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)`, then `tau1 != tau2` (`x -> x^5` is injective), so the points `(U, V)`
differ (`(a, b) != 0`) and the canonical pairs `(nk, rho)` differ, with equal digests.

## 3. Odd part with a centre, and interpolation on O1

For a centre `c` in `F_p`, write `F(c + s) - F(c - s) = 2 s g_c(s^2)`: the even powers of `s` cancel, and
`g_c(S) = sum_j f_{2j+1} S^j`, where `f_i` are the coefficients of `F(c + X)`. Since `D = 2m + 1`, `g_c` has degree exactly `m` and
leading coefficient `f_D`. A collision pair with midpoint `c` is `W1 = c + s`, `W2 = c - s` with `s != 0`, i.e. `S = s^2` a
nonzero square in `F_p` with `g_c(S) = 0`. These roots are exactly the roots of `G = gcd(g_c, S^((p-1)/2) - 1)`: a root `S` of
`g_c` in `F_p` is a nonzero square iff `S^((p-1)/2) = 1`. `G` divides `S^((p-1)/2) - 1`, which is squarefree and splits over `F_p`,
so `G` is a product of `deg G` distinct linear factors.

Stage B (interpolation). Let `zeta = psi = 5^((p-1)/2^21)`, a primitive `2^21`-th root of unity (5 is a nonresidue), and
`S_i = zeta^(2i)`, which runs over the subgroup `H_20` of order `n = 2^20`. Then `(F(c + zeta^i) - F(c - zeta^i)) zeta^-i =
2 g_c(S_i)`. The program evaluates this for the `n' = 983040` indices `i` with `i mod 16 != 15`: the points `S_i` with
`i mod 16 = 15` form one coset of `H_16` (those with `S^(2^16) = c1 = psi^(15 * 2^17)`), and the others form `O1` (section 4.3).
These are `2 n'` line evaluations, each charged as one target compression (279 operations, the organizer's unit `C(3)` for one
complete permutation), although a line evaluation does strictly less work than a reference permutation: it starts from the affine
state `alpha + W beta` and runs only rounds 2-3, 4-6 and 60-63 of section 2.3. The value for
`S_i` is stored at position `brv_20(i)`, the output order of the forward transforms (these positions are exactly `[0, n')`;
`stage_b` in `stageb.c`). Since `deg g_c = m < n'`, these `n'` values determine `g_c`; its coefficients are one truncated inverse
transform away (section 4.3).

## 4. The program (one deterministic run)

### 4.1 Stages

```
init:  twiddle tables (three-level table of psi^e), the transform constants, the tables of the truncated top
setup: the line (Q, a, b, alpha, beta), section 2
for i = 1, 2, ..., 64 (stop at the first verified collision):
  A     c := i
  B     the n' values 2 g_c(S) on O1 (2 n' line evaluations), section 3
  prep  coefficients of g_c and the tests of 2.3; the quotient q = floor(X^v P1 / g') by Newton inversion of the reversed top
        part (series inverse to X^(k+1), k = n' + v - m); the start residue A0 = X^v P1 mod g' from its values -q g' on O1;
        Gi = -1/(n^3 g') on O1 by one batch inversion; G2 = g' on O2 (g' = 2 n g_c); per-block factors; delta_j (section 4.4);
        the trial would end if deg g_c != m (impossible, 2.3) or if g_c vanished on O1 (excluded by H2)
  C     kappa R := kappa S^((p-1)/2) mod g by 236 value-domain Montgomery squarings, 45 with a multiplication by S (4.5)
  D     G := gcd(g, kappa (R - 1)), monic, by the half-gcd (4.6); the trial would end if deg G = 0 (impossible at c = 1, 5.1)
  E     a root S of G (deg G = 1: S = -G_0; deg G >= 2: equal-degree splitting with shifts 1, 2, ..., 256)
  F     s := sqrt(S) (Tonelli-Shanks, 2-adicity 32, nonresidue 5); W1 = c + s, W2 = c - s; tau = W^e;
        (U, V) = Q + tau (a, b); nk = U^e - c_{0,0}, rho = V^e - c_{0,1}
  G     both reference hashes (279 operations each); success iff equal digests and distinct pairs
H     the six output values (centre, two pairs, digest) as 64 hexadecimal digits each
I     the report: formatted into one 8192-byte buffer, written by one write system call; exit_group
```

The exponent `E = (p-1)/2` has 254 bits and Hamming weight 46. Its top bit (bit 253) is followed by 128 zeros. The start residue
represents `S^v` with `v = 2^17` (the largest power of two, up to `2^(L-3)`, whose Newton buffers fit in the buffers of prep;
`main.c`). This absorbs the top bit and the first 17 of those zeros, so stage C runs the remaining 236 bits, most significant
first: 236 squarings, 45 of them followed by a multiplication by `S`.

Determinism: the program reads no input and no file; its only argument is the round count (3). The order of centres, all
parameters (`n`, `n'`, `v`, `kmax = 131071`, thresholds) and the trial cap are fixed in the source. There are no random choices. For
`deg G >= 2` stage E tries the shifts `delta = 1, 2, ..., 256` and ends the trial if they do not split `G` down to degree 1 (H3);
section 6.6 bounds the cost of this branch for `deg G <= 8`.

### 4.2 Machine model and charging rules

Every item below is charged by a statement of the source, at the statement that executes it, with the counters of `fp.h`
(`LD`, `ST`, `CTL`, `LOOPC` and the counted field operations). Section 6 sums these statements over the executed path, and
Appendix A transcribes them.

* Canonical `F_p` addition, subtraction (negation is one subtraction), multiplication and squaring: 1 each. Montgomery conversions
  (`fp_from_u64`, `fp_from_limbs`, `fp_to_limbs`) are one multiplication each. Inversion (`a^(p-2)`) and every exponentiation are
  expanded by left-to-right square-and-multiply: one squaring per bit below the top, one multiplication per further set bit, and 6
  control operations per bit (loop update, comparison, branch, word selection, shift, bit test), plus 6 per bit of the top-bit
  search.
* A load or store of a 256-bit array element: 1 each, plus 1 address operation each (`LD(n)`, `ST(n)`).
* Every loop: 3 operations per iteration (index update, comparison, branch) and 2 on exit (`LOOPC(n) = 3n + 2`), unless a
  different count is written next to it. The inner loops of the transform passes are unrolled by 4 in the source (four kernel
  calls per iteration, one address update and one loop iteration per four kernels; `INNER` in `ntt.c`), and use one iteration per
  kernel when a supergroup has fewer than 4 offsets. The fixed operations of a block (the butterflies of the radix-2 to radix-16
  kernels, the 4 + 4 layers of the truncated top with its 15 loads and stores, and the pointwise maps of the stage C bottom passes;
  macros `R4C`/`R8C`/`R15`/`R16` in `ntt.c`, `R4`/`R8` in `stagec.c`) are written out straight-line with constant indices: no loop is
  executed there, and their words stay in registers.
* Per-pass constants: the variant of a pass (radix, direction and unrolling of a transform pass; the subtrees of a truncated top;
  the mode of a bottom pass) is selected once per pass by a charged test, and the per-block code is the loop specialized to those
  constants (an inline function called with constant arguments). Per-block tests that do depend on the block are charged where they
  execute (the zero extension of a top block); the first supergroup of `H_L`, whose node twiddles are 1, is peeled out of its loop.
* Every other executed integer or control operation (index and address arithmetic, shifts, masks, comparisons, branches,
  selections, table indices): 1 each, added by `CTL(k)` next to the statement. Where a statement's count is a bound, the comment
  says so.
* Procedure calls are treated as inlined: call, return and argument passing are not charged (every called function is a fixed
  block of counted statements and could be written in place without changing any counted operation; the transform kernels are
  `static inline`). The one recursive function, `hgcd`, cannot be inlined: each of its calls is charged `HG_CALL = 128`
  operations, a bound on call and return (2), the stack-pointer adjustment (2), the nine arguments (9) and saving and restoring up
  to 48 live values at 2 each (96: the caller's integer locals and its one live field value, `beta^(t+1)`, with its address
  operations; `hgcd.c`).
* Registers (the structural assumption, the same register file of 18 words of 256 bits as edd943c and 4bcabff8). Values held in
  registers are not charged as loads. Integer indices, pointers and loop bounds are held in integer registers; their own
  arithmetic is charged by `CTL` (including the base pointer of every block and supergroup), but they, and any spills of them,
  are not charged as loads or stores (except across the recursive calls of `hgcd`, below).
  - Radix-8 block: 8 data words, its 7 twiddles and one temporary; a pass that advances its supergroup twiddle by multiplication
    also holds the running twiddle and its step (18).
  - Radix-16 block: 16 data words, the current twiddle and one temporary (18). Its 15 twiddles are computed once per supergroup,
    stored to a 15-word array (charged) and each is loaded (charged) when its layer starts; the running twiddle and its step are
    stored and reloaded around the block (charged).
  - Truncated top pass (section 4.3): the 16 words of an offset (15 loaded, the 16th formed in a register), one twiddle and one
    temporary (18); each node twiddle different from 1 is loaded (charged) once per offset, and the three twiddles of the recovery
    are loaded (charged).
  - Stage C bottom passes: 8 data words, 7 twiddles, the running block twiddle and two temporaries; the step of the running
    twiddle and the table entries are loaded per block (charged).
  - Stage D's fused pointwise loops (`apply_adj3`, `mat_mul_f`) hold at most 17 words (the four entries of each operand at one
    point, `q0`, `q1`, `beta^(t+1)`, the point and the temporaries of the sums).
  - Sensitivity (estimate from the pass structure of 6.3, not a count): a pass costs about `4.2 n'` operations of memory
    traffic and overhead per element sweep. With about 8 registers (radix-4 blocks, fused tops and bottoms of 2 + 2 layers) a stage
    C step needs about 16 more passes (`+66e6` operations per step, `+28%` of stage C) and stage D's transforms about 30% more,
    about `+0.3` in `time_log2`; with radix-2 blocks only, about 60 more passes per step and separate pointwise passes, about
    `+1.0`.
* A line evaluation `F(W)` and a reference hash are charged one target compression (279 operations) each (`C_UNIT` in `line.h`),
  not their expanded arithmetic.
* Fixed bounds (`main.c`): 100 operations per stage switch (`STAGE_BK`), 20 per snapshot of the counters for a trial row
  (`TRIAL_BK`), 5,000 for the prologue of `main` (`PROLOGUE`), 100,000 for the constants of `consts.h` computed by
  `gen_consts.py` (`CONSTS_GEN`: parsing the 201 hexadecimal constants of the organizer file, about 13,000 digits at 6 operations
  each, `psi` and its inverse by exponentiation, about 650 field operations, `2^512 mod p`, `-p^-1 mod 2^64` and 201 conversions;
  charged in stage init so that all preprocessing is inside the count), and in stage I: 400 per byte of the 8,192-byte
  output buffer (formatting, charged in full whatever it holds), 20,000 for the report loops, `10,000 + 8,192 * 8` for the write
  system call and 10,000 for `exit_group`. Stage E's schoolbook polynomial work (`powmod_small`, `gcd_small`, `find_root`) is
  charged generously per coefficient operation as written there.
* Instrumentation is not an algorithm step and is not charged: the counter updates themselves, the reporting-only profile
  snapshots of stage D (`PROF_BEGIN/PROF_END`) and the arena-peak statistic.
* Memory allocation: stage D allocates from a stack arena inside the static buffer (`aalloc`, 5 operations; `arel`, 1). Stages B,
  prep and C use four fixed buffers of `n'` words. There is no other allocator and no system call besides the two of stage I.

### 4.3 Transforms

The transforms run on the binary tree of the `2^21`-th roots of unity. Node `(d, j)` is the modulus `X^(2^(21-d)) - psi_d^brv_d(j)`
(`psi_d` of order `2^d`). It splits into `(d+1, 2j)` and `(d+1, 2j+1)` with the twiddle `t(d, j) = psi_(d+1)^brv_d(j)`. The
size-`2^L` transform of a node maps a residue modulo that node to its values at the node's roots: natural-order coefficients in,
bit-reversed values out (Cooley-Tukey butterflies). The inverse is the transpose (Gentleman-Sande) and returns `2^L` times the
coefficients (`ntt.c`; `ntt_fwd_b` / `ntt_inv_b` take any node, given by its offset `B`; `ntt_fwd_bz` reads a shorter input and
treats the missing coefficients as zero registers, loading only the present ones). Passes cover 3 layers (radix-8 kernels), 4
layers (radix 16), or 1 or 2 at the top of a range. Every element is loaded and stored once per pass. Supergroups are visited in
the order of their bit-reversed index, so the twiddle of the next supergroup is one multiplication by a fixed step from the last;
the 7 (or 15) twiddles of a block follow from it by squarings and multiplications by the constants `psi_2, psi_3, psi_3^3`
(and `psi_4^(1,5,3,7)`). A block whose node twiddles are 1 uses kernels without those multiplications.

**Truncated sets.** For the size-`2^L` subtree `J0` (`J0 = 0`: `H_L`; `J0 = 1`: its coset), the depth-4 nodes `N_0 .. N_15` are the
16 cosets of `H_(L-4)` in it (residues modulo `Y - r_j`, `Y = X^(2^(L-4))`). `O(L, J0)` is the union of `N_0 .. N_14`, `n' = 15 *
2^(L-4)` points at the positions `[0, n')` of the transform order. A polynomial `P` of degree `< n'` is `sum_(k<16) P_k Y^k` with
`P_15 = 0`; its values on `O` are determined by, and determine, `P`.
* Forward (`tr_fwd`): the top 4 layers (`tr_top`, per offset: the 15 present coefficient words in registers, `P_15 = 0`) produce the
  residues modulo `N_0 .. N_14` (leaf 15 is not formed); the lower layers run on those 15 nodes only (`tr_range` skips the
  supergroups below `N_15`).
* Inverse (`tr_inv`): the lower layers are inverted on the 15 nodes; then, per offset, the top 4 layers are inverted with the residue
  modulo `N_15` unknown and `P_15 = 0` known. For a node `Y^(2h) - t^2` with children `Y^h - t` and `Y^h + t`, the children's
  residues are `A + t B` and `A - t B` (`A`, `B` the low and high halves of the parent's residue), so the top coefficient of the
  second is that of the first minus `2t` times the parent's top coefficient. Along the path to `N_15` the complete sibling
  subtrees `(1,0)`, `(2,2)`, `(3,6)` and leaf 14 are inverted first (giving `X1 = 8 (1,0)`, `X2 = 4 (2,2)`, `X3 = 2 (3,6)`, the
  residues times their scale); the root's top coefficient is `P_15 = 0`, so `T2 = X2[3] - t11 X1[7] = 4 * top((2,3))`,
  `T3 = X3[1] - t23 T2 = 2 * top((3,7))` and leaf 15 `= leaf 14 - t37 T3` (`t` = the forward twiddles of nodes `(1,1)`, `(2,3)`,
  `(3,7)`). Then the remaining inverse butterflies run as usual and output slot 15 (`16 P_15 = 0`) is not formed. The result is
  `2^L` times the coefficients, as for the full inverse.
* The point sets of the program: `O1 = O(20, 0)` (`H_20` without the coset `N_15 = {x : x^(2^16) = c1}`, `c1 = psi^(15 * 2^17)`)
  and `O2 = O(20, 1)` (nodes `x^(2^16) = r_j`, `r_j = psi^(brv_4(j) 2^17 + 2^16)`, `j < 15`, inside `psi H_20` where `x^n = -1`).

### 4.4 Stage prep

All four buffers have `n'` words. With `gt = 2 g_c`, the values of `gt` on `O1` are the output of stage B.

1. One truncated inverse transform gives `G* = n gt` in coefficient form. The program tests coefficient `m` (nonzero) and the
   coefficients `m+1 .. n'-1` (all zero); by 2.3 these tests always pass.
2. `P1 = (X^n - 1)/(X^w - c1) = sum_(s<16) c1^(15-s) X^(s w)` with `w = n/16` (degree `n'`); its roots are `O1`. With `v = 2^17`
   and `k = n' + v - m = 137550`, the quotient `q = floor(X^v P1 / G*)` has degree `k`. Reversal gives `rev_k(q) = rev(X^v P1) /
   rev_m(G*) mod X^(k+1)` with `rev(X^v P1) = sum_s c1^s X^(s w)`, i.e. `rev_k(q) = h / (1 - c1 X^w) mod X^(k+1)` where
   `h = 1/f mod X^(k+1)`, `f = rev_m(G*)`. `h` is computed by Newton iteration `h_(2t) = h_t - h_t (f h_t - 1) mod X^(2t)` with
   cyclic products of size `2t` up to `2^18`; the division by `1 - c1 X^w` is the recurrence `h_i += c1 h_(i-w)` (ascending).
3. The start residue `A0 = X^v P1 mod G*` (the Montgomery form of `S^v`) has degree `< m < n'`. On `O1`, `X^v P1 = 0`, so
   `A0 = X^v P1 - q G* = -q G*` there. The program forms the values of `q` on `O1` (one truncated forward transform), multiplies them by
   the stored values (`G* = n gt`, and `n` is absorbed by the inverse's factor `2^20`) and negates them, and one truncated inverse
   transform returns the coefficients of `A0` exactly.
4. `G2 = g'(O2)` with `g' = G*`, by one truncated forward transform on `O2`.
5. `Gi = -1/(n^3 g'(O1)) = -1/(n^4 gt(O1))` on `O1`, by one batch inversion (prefix products, one inversion, two multiplications
   per element). The trial would end if a value were zero (`g_c` vanishing on `O1`); H2(a) excludes this (6.1).
6. Block factors for stage C (4.5): each bottom block of `Gi` is divided by its node root `c` and each block of `G2` multiplied by its
   node root (`blk_scale`, blocks in the bottom-pass order with a running root); `delta_j = r_j - c1` for `j < 15`.

### 4.5 Stage C: value-domain Montgomery powering on O1 and O2

For residues of degree `< n'`, define `Mont(A, B) = (A B + u g') / P1` with `u = -A B / g' mod P1` (`deg u < n'`). The numerator is
divisible by `P1`, so the quotient is exact. `Mont(A, B) = A B / P1 (mod g')`, and `g'` is a nonzero multiple of `g`. For
`deg A, deg B <= n' - 1`, the numerator has degree `<= max(2n' - 2, n' - 1 + m) < 2n' - 1`, so `deg Mont(A, A) <= n' - 2`. One step
maps the residue `A` to `Mont(A, A)`, or to `X Mont(A, A)` when the exponent bit is 1. The latter still has degree `<= n' - 1`, so no
reduction is needed. Starting from `A0 = S^v P1`, the residue after the steps represents `S^e P1` with `e` the exponent prefix
processed so far.

`P1` vanishes on `O1`. On `O2`, `x^n = -1` and `x^w = r_j` on node `j`, so `P1(x) = (x^n - 1)/(x^w - c1) = -2 / delta_j`.

Representation. A residue `A` is held as `mu A` on `O1` and `lambda A` on `O2`, with `mu = n lambda`. The `O1` values are never
stored: the work buffer `W` holds the `O1` transform up to its last pass. One step:

```
U  = (mu A)^2 Gi  on O1                         (= -(mu A)^2 / (n^3 g'): the values of u, scaled)
U  -> O2: truncated inverse transform on O1, truncated forward transform on O2
B2 = ((lambda A)^2 + U G2) delta_j  on O2       (= lambda^2 (A^2 + u g') delta_j = -2 lambda^2 Mont(A, A) there)
     times X (the point) when the bit is 1; stored as the new O2 values (lambda' = -2 lambda^2)
B2 -> O1: truncated inverse transform on O2, truncated forward transform on O1 (mu' = n lambda')
```

`u` has degree `< n'`, so its values on `O1` determine it, and `Mont(A, A)` has degree `< n'`, so its values on `O2` determine it.

The transforms are fused into passes:
* a bottom pass (depths 17-19, blocks `X^8 - c` of 8 words): forward layers, the pointwise map, inverse layers. One twiddle set serves
  both directions: on `X^8 - c` with roots `x_k`, the matrix `V = (x_k^l)` satisfies `V^T V = 8 diag(1, c J)` (`J` the reversal
  `l -> 8 - l` on `l = 1..7`, since `sum_k x_k^(l+l') = 8c` if `l + l' = 8`, `8` if `l = l' = 0`, else 0), so
  `V^-1 = (1/8) diag(1, c^-1 J) V^T = (1/(8c)) diag(c, J) V^T`. So on `O1` the inverse is the forward network transposed (reversed
  layers, Gentleman-Sande butterflies with the forward twiddles), with slot 0 times `c`, the store in the order 0, 7, 6, ..., 1, and
  the factor `1/c` folded into `Gi` (prep step 6). On `O2` the forward is computed the same way from the inverse network, with slot 0
  times `1/c`, the load in that order, and `c` folded into `G2`;
* a top pass (depths 0-3, `tr_top`): the truncated inverse top of one set and the truncated forward top of the other, fused per offset;
* the middle depths 4-16: one radix-16 pass and three radix-8 passes per transform.

Each step is 4 truncated transforms of `n'` points and the pointwise work. No normalization by `1/n` is executed inside the
steps: `A0` is multiplied by `1/n` once on entry (before its forward transform on `O2`, so `lambda = 1/n`), the exit step uses
`A2 / n`, and the scalars `lambda`, `mu` are tracked (two field operations per step). At the end, an exit step with the multiplier 1 (`Mont(A, 1)`, degree
`< m`) gives the coefficients of `kappa R`, with `R = S^((p-1)/2) mod g` reduced and `kappa = -2 lambda_final`. The gcd of stage D
is scale-invariant, so `kappa` is never divided out: stage D receives `kappa R - kappa`.

### 4.6 Stage D: the half-gcd

Notation: for `(a, b)` with `deg a > deg b`, Euclid's sequence is `r_0 = a`, `r_1 = b`, `r_(i-1) = q_i r_i + r_(i+1)`, and
`d_j = deg q_1 + ... + deg q_j`. Every pair `(a, b)` and every 2x2 matrix below is held **up to one common nonzero scalar** (the
same scalar for both members of a pair, and for all four entries of a matrix). This suffices because only `adj(M) (a, b)` and
products of matrices are formed (both homogeneous of degree 1 in each argument), and the final gcd is made monic. The code keeps
the scalar common: pseudo-division gives `[[Q, 1], [beta^(t+1), 0]] (d, e) = beta^(t+1) (c, d)` exactly, and rows of a product formed
from values are rescaled to the scale of the rows formed from coefficients (below).

The input `g` is recovered from `G2` after stage C: the block factors are divided out (`blk_scale`) and one truncated inverse
transform on `O2` gives `n G*`.

`hgcd(a, b, k)` returns a matrix `M` with `(a, b)` proportional to `M (r_h, r_(h+1))` and `deg M = d_h`, `h = max{j : d_j <= k}`.
* Truncation lemma (von zur Gathen and Gerhard, *Modern Computer Algebra*, chapter 11, the fast Euclidean algorithm; the basis of
  every half-gcd): let `deg a = n > deg b`, `0 <= k <= n`, and let `a*`, `b*` satisfy `deg(a - a*) < n - 2k` and
  `deg(b - b*) < n - 2k`. Then the Euclid sequences of `(a, b)` and `(a*, b*)` have the same quotients `q_1 .. q_h` for
  `h = max{j : d_j <= k}`. (Thull and Yap give the same statement for their HGCD.) Each call therefore reads only the top `2k+1`
  coefficients (a pointer offset, no copy), the base case re-truncates after each step, and a pseudo-division computes only the
  positions of the remainder that the next call reads. A defect in stage D could make the computed `G` wrong and the trial fail,
  never produce a false collision, because stage G checks the pair with the reference permutation (and section 5.1 checks the
  certificate independently).
* `k <= 48`: Euclid's algorithm on copies of the top parts, while the next quotient fits the budget; two consecutive normal steps
  (both quotients linear) are fused into one pass over the coefficients.
* Otherwise, with `k1 = floor(k/2)`:
  1. `M1 = hgcd(a, b, k1)`.
  2. `(c, d) = adj(M1) (a, b)`, i.e. `c = r22 a - r12 b`, `d = r11 b - r21 a`, by cyclic products. The true `c` has degree
     `deg a - d1`. In the normal case and `k = 2^j - 1` (inputs of degree `2k + 1 = 2^(j+1) - 1`) this is `3 * 2^(j-1) - 1`, so
     with the product size `2^l`, `l = j + 1`, its residues on the three rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^(2^(l-2))`, three of
     the four quarter-rows of the size-`2^l` tree, `3 * 2^(l-2)` points) determine it exactly. The inputs are split
     into the three rows by two butterfly layers (the fourth quarter-row, `Y + i`, is dropped). Each row is transformed, the four
     matrix entries are transformed one row at a time and multiplied in (one fused pass per row), and each row is inverse
     transformed. The CRT is then `4 C0 = (R0 + R1) + 2 R2 - i (R0 - R1)`, `4 C1 = 2 (R0 - R1)`, `4 C2 = (R0 + R1) - 2 R2 + i (R0 -
     R1)` (`apply_adj3`). The code tests the degree at run time; when it does not fit `3 * 2^(l-2)`, the same is done on the full
     size-`2^l` tree (`apply_adj`).
  3. If `d = 0` or the next quotient degree exceeds `k - d1`, return `M1`.
  4. One pseudo-division `beta^(t+1) c = Q d + e` (`t = deg c - deg d`, `beta = lc(d)`). It is inversion-free, and for `t = 1` it
     is one pass: with `u = deg c`, `Q = beta c_u X + (beta c_(u-1) - c_u d_(u-2))` and `e_i = beta^2 c_i - q1 d_(i-1) - q0 d_i`. Then
     `[[Q, 1], [beta^(t+1), 0]] (d, e) = beta^(t+1) (c, d)`.
  5. `M2 = hgcd(d, e, k - d1 - t)` on the compacted top parts of `d` and `e`. It writes its output over its own inputs, which it
     no longer reads by then.
  6. Return `M1 [[Q, 1], [beta^(t+1), 0]] M2`. The product is formed on two rows of `2^(j-1)` points (entries of degree `<= k`), in
     one fused pass per row; for `t = 1` the factor `[[Q, 1], [beta^2, 0]]` is applied pointwise (`Q(x) = q0 + q1 x` from a table of the
     points `x`, held in the arena).
* Reuse of transforms and values (all exact, because the transform of a polynomial of degree `< N` at `N` points is its vector of
  values there): below the top level, `M1`'s transforms on the two rows of the final product are kept from step 2 (they are the rows
  `Y - 1`, `Y + 1` there too); a recursive call whose output size equals the subgroup row `Y - 1` also writes the values of its
  result on that row (formed pointwise in its own final product), and the parent uses them instead of transforming the
  coefficients; the driver's call returns `M` as values on the subgroup of size `2^17`, and the driver's product uses them on the
  rows inside that subgroup (the truncated first product converts them to coefficients first). Values and transforms of
  coefficients obtained from them by an inverse transform differ by the factor `2^17` of that inverse; the rows formed from values
  are multiplied by it.
* Driver (`hg_gcd`): while `deg b >= 0`, take `k = 2^j - 1 <= min(131071, deg a / 2)` and set `M = hgcd(a, b, k)`. Apply
  `adj(M)` to the full `(a, b)` in place (rows as in step 2), then make one pseudo-division and shift `(a, b) := (b, e)`. Below
  degree 96, Euclid's algorithm runs to the end. Finally the last nonzero remainder is made monic (one inversion). `a` and `b` live
  in two buffers of `n'` words. The first product of the driver (`deg c` about `845,000`) cannot use `3 * 2^18 = 786432` points
  (too few for that degree) nor `2^20` points (more than the `n'`-word buffers hold): it is taken modulo `P1` on `O1` instead, as 15
  rows of `2^16` points (`apply_adj_tr`: the split into the rows and the recombination are the truncated top layers of 4.3; it is
  exact because `deg c, deg d < n'`). The bound 131071 keeps the arena of stage D within the two buffers freed after stage C
  (`2 n' = 1,966,080` words, with `g` and `kappa (R - 1)` in the other two): on the generic path the arena peaks at 1,900,548
  words (6.5).
* Abnormal quotients (degree `> 1`, or degree gaps) are handled by the general pseudo-division and wider matrix slots; they do not
  occur under H2(b).

### 4.7 Stages E to I

For `deg G = 1`, `S = -G_0`. For `deg G >= 2`, stage E splits `G` with the shifts `delta = 1 .. 256`: it computes
`(X + delta)^((p-1)/2) mod G` by schoolbook square-and-multiply, takes `h = gcd(G, (X + delta)^((p-1)/2) - 1)`, whose roots are the
roots `s_i` of `G` with `s_i + delta` a nonzero square, and continues with `h` whenever `1 <= deg h < deg G`. This relies on the
standard equal-degree-splitting heuristic for the fixed shifts (H3: a shift separates a given pair of roots with probability about
1/2 over random shifts). Section 6.6 bounds the branch's cost for `deg G <= 8` and the full 256 shifts. Stage F computes `s` by
Tonelli-Shanks. It forms the two line points and maps them back with three exponentiations each (`tau = W^e`,
`nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), all charged per operation. Stage G calls the reference permutation (rounds 0-3, 4-6,
60-63 on `[nk, rho, 2^65]`) for both pairs and compares. Stage H encodes six values in hexadecimal (one conversion and 12
operations per digit). Stage I charges the fixed bounds of 4.2, then formats the report, writes it once and exits.

## 5. Why the output is a collision

By sections 2-3, a root `S` of `G` is a nonzero square root of `g_c`, so `s = sqrt(S) != 0` satisfies `F(c + s) = F(c - s)` with
`c + s != c - s`. The two canonical pairs differ and have the same digest. Stage G recomputes both digests with the full reference
permutation, and the program reports success only if they are equal and the pairs differ. Independently of the program, the pair in
`certificates/` matches the organizer's hash (`verifier/poseidon.py`, r = 3): digest `ec121f2a554ea528faa3a1af74fbe603ca9fc80e942ef88ac220fe46c9655132` (as 32 little-endian bytes;
the field element `0x325165c946fe20c28af82e940ec89fca03e6fb74afa1a3fa28a54e552a1f12ec`).

### 5.1 The certificate lies on the line, with midpoint 1

The certificate inputs are `nk1 = 0x0499f5c4354bafa11ca451e656d380d078444ed6561d6355487453741e1a6815`, `rho1 = 0x21625d728b86cf0865d7ad7cd99a0c20464939e5253940d95b3a639d7a909af7`,
`nk2 = 0x1009050c8c1414cf5975db612457a2e49b06db64fce28c7dd5ad52ed8fc2c567`, `rho2 = 0x31611cd777dc6c418e048d96a497f46fa51523b47dbadcd97d0ad171160fcdb8` (canonical, encoded little-endian in the .bin files). From the certificate alone (no run needed): with
`U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, the point `(U, V)` must equal `Q + tau (a, b)`, and `W = tau^5`. With the
constants of section 2 (computed by `line_setup`):

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
S^((p-1)/2) = 1 (S is a nonzero square);  S^(2^20) != 1 (S is not in H_20, so not in O1)
```

The organizer constants used above (from `orchard-pallas-constants.json`, SHA-256 `ab79bd05cbdcbe7c4c63ef7a4b95ffe8ec8938c1d71b49ceeebaf5b3f80aee62`; only the MDS matrix enters
`lc(F)` in 2.3, and round constants of rounds 0 and 1 enter the line):

```
M_{0,0} = 0x0ab5e5b874a68de7b3d59fbdc8c9ead497d7a0ab23850b56323f2486d7e11b63
M_{0,1} = 0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e
M_{0,2} = 0x07c045d5f5e9e5a6d803952bbb364fdfa0a3b71a5fb1573519d1cf25d8e8345d
M_{1,0} = 0x233162630ebf9ed7f8e24f66822c2d9f3a0a464048bd770ad049cdc8d085167c
M_{1,1} = 0x25cae2599892a8b0b36664548d60957d78f8365c85bbab07402270113e047a2e
M_{1,2} = 0x22f5b5e1e6081c9774938717989a19579aad3d8262efd83ff84d806f685f747a
M_{2,0} = 0x2e29dd59c64b1037f333aa91c383346421680eabc56bc15dfee7a9944f84dbe4
M_{2,1} = 0x1d1aab4ec1cd678892d15e7dceef1665cbeaf48b3a0624c3c771effa43263664
M_{2,2} = 0x3bf763086a18936451e0cbead65516b975872c39b59a31f615639415f6e85ef1
c_{0,0} = 0x360d7470611e473d353f628f76d110f34e71162f31003b7057538c2596426303
c_{0,1} = 0x2bab94d7ae222d135dc3c6c5febfaa314908ac2f12ebe06fbdb74213bf63188b
c_{0,2} = 0x150c93fef652fb1c2bf03e1a29aa871fef77e7d736766c5d0939d92753cc5dc8
c_{1,0} = 0x3270661e68928b3a955d55db56dc57c103cc0a60141e894e14259dce537782b2
c_{1,1} = 0x073f116f04122e25a0b7afe4e2057299b407c370f2b5a1ccce9fb9ffc345afb3
c_{1,2} = 0x2a32ec5c4ee5b1837affd09c1f53f5fd55c9cd2061ae93ca8ebad76fc71554d8
```

So both pairs lie on the line (the two expressions for `tau` agree) and their midpoint is `c = (W1 + W2)/2 = 1`. Hence `S` is a
nonzero square root of `g_1`, `deg G >= 1` at `c = 1`, and the deterministic procedure succeeds in trial 1 (given the premises of
6.1). The certificate does not show that `deg G = 1`; the claim covers every `deg G <= 8` (6.6). When `deg G = 1`, `S` is the
root that stage E returns, and it fixes stage F's path (6.6). A judge can recompute all of this with a few lines of big-integer
arithmetic from the organizer constants.

## 6. The operation count, derived from the source

### 6.1 What the count depends on, and the premise H2

Each statement of section 9 that does work carries its charge (rules of 4.2). The count of a stage is the sum of the charges of
the statements it executes. Which statements execute depends on the target only at the points below. Everything else depends only
on the fixed dimensions and parameters (`L = 20`, `n`, `n'`, `m`, `v = 2^17`, `kmax`, the thresholds, the bits of `(p-1)/2`): loop
bounds, transform sizes and passes, and buffer lengths.

1. prep: the tests of coefficients `m+1 .. n'-1` (zero) and `m` (nonzero), whose outcomes are fixed by 2.3; the zero test of every
   value in the batch inversion (H2(a)).
2. stage D: the test of `deg(kappa R - kappa) = m - 1` (one test when the coefficient of degree `m - 1` is nonzero), and inside the
   half-gcd every degree scan (`pdeg`), every test on quotient degrees and every early return (H2(b)).
3. `deg G`, which ends stage D's final Euclid loop, and stage E's shifts (H2(c), H3).
4. stage F: the path of the Tonelli-Shanks loop, a function of the root `S` (6.6).
5. stage G's comparison and the trial loop (one trial, 5.1).

**Premise H2 (the generic path).** For the fixed target at `c = 1`, with `R_1 = S^((p-1)/2) mod g_1` (stage D receives the nonzero
multiple `kappa (R_1 - 1)`):
* (a) `g_1` has no zero on `O1`;
* (b) `deg(R_1 - 1) = m - 1`, and the Euclidean remainder sequence of `(g_1, R_1 - 1)` is normal (every quotient has degree 1)
  down to `G`;
* (c) `deg G <= 8`.

Supporting evidence (random-polynomial model):
* (a): Every point of `O1` is a nonzero square (`H_20` consists of squares, since `2^21` divides `p - 1`), so a zero of `g_1` on
  `O1` would be a root of `G`. The certificate's root `S` is not in `H_20` (5.1). Under (c), `G` has at most 7 other roots. In the
  random model each lies in the `n'`-point set `O1` with probability `n' / p < 2^-234`.
* (b): Dividing out the common factor `G` (the remainder sequence of `(G u, G v)` is `G` times that of `(u, v)`), the sequence of
  the cofactors is abnormal only if one of their at most `m` principal subresultant coefficients vanishes. Each is a nonzero
  polynomial of degree at most `2m` in the coefficients, so for random cofactors the Schwartz-Zippel bound gives a probability
  at most `2 m^2 / p < 2^-212`. A zero leading coefficient of `R_1 - 1` has probability `1/p`.
* (c): The roots of `G` are the roots of `g_1` that are nonzero squares. Given the certificate's root, the number of others behaves
  like a Poisson variable of mean 1/2 in the random-polynomial model, so `P(deg G > 8)` is about `6 * 10^-8`.

Score sensitivity:
* If (a) failed, trial 1 would end in prep and later centres would run. Each further trial costs about as much as the first (about
  `+1` in `time_log2` for one more), and a fresh centre succeeds with probability only about 0.39 in the same model, so the time
  bound would not hold.
* If (b) failed, stage D would follow the general path for abnormal quotients. Its count, its arena peak and its recursion depth
  (hence the stack bound of section 7) are not derived here, and the arena could overflow, which ends the program (`die(4)`).
* If (c) failed with `deg G = d > 8`, stage E would cost at most `256 e(d)` (6.6), e.g. `+0.02` in `time_log2` at `d = 20`.

**Lemma (stage D's shapes).** Under (b), every call `hgcd(a, b, k)` of the recursion receives `deg b = deg a - 1` and returns a
matrix of `deg M = k` (`k` normal steps), whose entries have degrees `(k, k-1, k-1, k-2)`. Its two children have budgets
`floor(k/2)` and `k - floor(k/2) - 1`. Every product size, row split and reuse flag is a function of `k` and of the call's
position, and the driver's iterations are a function of `m`. Hence every length that the code tests, loops over or allocates is a
function of `m` and `deg G`. The cost model below computes these lengths by running the recursion on degrees.

**The cost model (Appendix A)** mirrors every function of section 9 that the run executes. For each statement it adds the counters
that the statement adds (`LD(n)`: `n` loads and `n` address operations; `LOOPC(n) = 3n + 2`; ...), tracking lengths and degrees
only and doing no field arithmetic. For stage D it also mirrors the arena (`aalloc`, `arel`). Section 6.2 lists what it evaluates
under H2; sections 6.3 to 6.6 give the stages in closed form or by components, and the tables are its output.

### 6.2 Ledger

Counts in primitive operations (`C(3) = 279`). Column "deg G = 1" is the count of the procedure on the generic path when
`deg G = 1` (then stage E needs no shift and stage F follows the path fixed by the certificate's `S`). Column "bound" is the count
used for the claim: the largest count over `1 <= deg G <= 8` (stage D's count is largest for `deg G = 1`, stage E at `deg G = 8`
with all 256 shifts, stage F over every path). `arith` = additions, subtractions, multiplications and squarings; `control`
includes the address operation of every load and store; `units` counts the line evaluations and reference hashes, each 279.

| stage | arith | loads | stores | control | units (x279) | deg G = 1 | bound |
|---|---:|---:|---:|---:|---:|---:|---:|
| init: twiddle tables, transform constants (once) | 572 | 561 | 458 | 108,249 | 0 | 109,840 | 109,840 |
| setup: the line (once) | 410 | 44 | 10 | 1,716 | 0 | 2,180 | 2,180 |
| A: centre | 1 | 0 | 0 | 126 | 0 | 127 | 127 |
| B: 2 n' = 1,966,080 line evaluations, values of g_c on O1 | 6,029,312 | 0 | 983,040 | 15,794,278 | 1,966,080 | 571,342,950 | 571,342,950 |
| prep: coefficients and tests, Newton series inverse, start residue, Gi, G2, block factors | 196,534,682 | 61,370,243 | 48,329,531 | 171,575,441 | 0 | 477,809,897 | 477,809,897 |
| C: S^((p-1)/2) mod g, 236 steps | 30,056,618,897 | 7,479,492,708 | 4,905,242,955 | 13,729,670,774 | 0 | 56,171,025,334 | 56,171,025,334 |
| D: g from G2, half-gcd of (g, kappa (R - 1)) | 4,938,006,303 | 1,493,607,643 | 1,114,715,130 | 4,038,503,063 | 0 | 11,584,832,139 | 11,584,832,139 |
| E: root of G | 1 | 3 | 2 | 119 | 0 | 125 | 184,029,614 |
| F: square root, back-map | 3,071 | 12 | 0 | 13,430 | 0 | 16,513 | 18,141 |
| G: two reference hashes, trial loop exit | 0 | 0 | 0 | 135 | 2 | 693 | 693 |
| H: encoding of the output | 6 | 0 | 0 | 4,846 | 0 | 4,852 | 4,852 |
| I: report (bounds), write, exit | 0 | 0 | 0 | 3,382,436 | 0 | 3,382,436 | 3,382,436 |
| **total** | | | | | | **68,808,527,086** | **68,992,558,203** |

`N_claim = 68,992,558,203` operations `= 247,285,154.8` units, `log2(N_claim / 279) = 27.881600`, claimed as `27.88161` (rounded up). For
`deg G = 1`, `log2(68808527086 / 279) = 27.877747`.

Recomputation of the claim from the rows:

```python
from math import log2, ceil
d1 = [109840, 2180, 127, 571342950, 477809897, 56171025334, 11584832139, 125, 16513, 693, 4852, 3382436]      # init, setup, A, B, prep, C, D, E, F, G, H, I (deg G = 1)
bound = [109840, 2180, 127, 571342950, 477809897, 56171025334, 11584832139, 184029614, 18141, 693, 4852, 3382436]
assert sum(d1) == 68808527086 and sum(bound) == 68992558203
t = log2(sum(bound) / 279)
print(t, ceil(t * 1e5) / 1e5)
mem = 126051522
print(mem, log2(mem), ceil(log2(mem) * 1e4) / 1e4)
```

### 6.3 Stage C in closed form

Stage C does not depend on the data: every count below follows from the code of section 9 and the rules of 4.2. Notation: `n' = 983040`
elements, 122,880 bottom blocks of 8 words, 65,536 offsets of the truncated top, `nh = 2^(d0-4)` rows of 15 supergroups for a pass
at depth `d0`, `st` kernels per supergroup. `brv_next` costs `7 + 4c` for `c` carry steps, and over a row loop of `nh` iterations
the carries total `nh - 1`.

* Radix-8 kernel (`k8f`/`k8i`): 8 loads and 8 stores with their address operations (32) and 12 butterflies of one multiplication,
  one addition, one subtraction (36): 68. With the unrolled loop (one control operation and one iteration, 3, per 4 kernels): 69
  per kernel. A supergroup: `69 st + 2` (loop exit) `+ 5` (index `G` and base `x + G S`) `+ 12` (twiddles: 2 squarings, 4
  multiplications, 3 constant loads) `+ 1` (running twiddle) `= 69 st + 20`; the trivial first supergroup of `H_L` (7 of the 12
  butterflies without multiplication, base `x`) costs `62 st + 15`. A pass at depth `d0` on the coset (`J0 = 1`, forward):
  `15 nh (69 st + 20) + 65 nh + 40` (per row: 3 control, `LOOPC(15) = 47`, 1 multiplication across the absent supergroup,
  `brv_next` 7 and the row loop 3, plus 4 per carry; per pass: dispatch 8, setup 10, two twiddles 24, loop exit 2, minus 4). On
  `H_L` (`J0 = 0`) subtract `7 st + 8`; an inverse pass adds 4 (two inverse twiddles). Depths 8, 11, 14 (`st` = 512, 64, 8):
  8,484,600, 8,525,480 and 8,852,520 on the coset; 8,481,008, 8,525,024 and 8,852,456 on `H_L`.
* Radix-16 pass at depth 4 (`nh = 1`, `st = 4096`): kernel 32 + 32 (loads, stores) + 96 (32 butterflies) + 30 (15 twiddle loads) =
  190, 191 with the loop; supergroup `191 st + 88` (the 15 twiddles computed and stored: 72; base and step stored and reloaded:
  8; index and base 5); pass `15 (191 st + 88) + 100` = 11,736,460 on the coset, 11,642,244 on `H_L` (trivial kernel 167:
  subtract `23 st + 8`).
* A middle range (depths 4-16: one radix-16 and three radix-8 passes) adds 69 operations of range bookkeeping (`tr_range`):
  37,599,129 forward on the coset, 37,500,801 forward on `H_L`; the inverse ranges add 16 (37,599,145 and 37,500,817).
* Truncated top (fused): per offset 1 + 30 (15 loads) + inverse top + forward top + 30 (15 stores) + 3 (loop). The inverse top of
  `H_L` costs 114 (31 butterflies, 14 of them without multiplication, 11 twiddle loads, the recovery 12, one addition) and that of the
  coset 136 (15 twiddle loads); the forward tops cost 122 (coset) and 100 (`H_L`); either fused pair is 236, so 300 per offset and
  `65536 * 300 + 10 = 19,660,810` per pass.
* `bottom1` (squaring mode): per block 159 (index and the two block pointers 6, twiddles 12, 8 + 8 loads 32, 24 butterflies 72,
  8 squarings and 8 multiplications 16, slot 0 times `c` 2, 8 stores 16, running twiddle with its step load 3); the trivial first
  block 138; per row 62 plus the carries; setup 24: `122879 * 159 + 138 + 8192 * 62 + 4 * 8191 - 3 + 24 = 20,078,588`.
* `bottom2`: per block 211 (index and the three block pointers 7, twiddles 12, slot 0 times `1/c` 2, 8 loads 16, 24 butterflies
  72, `A2^2 + v Y` 24 with 16 loads 32, `delta_j` load 2 and 8 multiplications, `iw0` recomputed 1, 8 stores to `A2` 16, 8 stores
  16, running twiddle 3); with a multiplication by `x` (bit 1) 239 (3 multiplications for the leaf roots, 4 loads, a spill and
  reload, 8 multiplications, 4 negations, the running forward twiddle 3); per row 60 (63 with bit 1) plus the carries; setup 41
  (65 with bit 1): 26,452,005 and 29,917,245.
* One step: `bottom1` + 4 middle ranges + 2 tops + `bottom2` + 2 (bit test) + 10 (the scalar update `lambda <- -2 lambda^2` and
  the step loop) = **236,052,117** (bit 0) and **239,517,357** (bit 1).
* Stage C = `306,789,822 + 191 * 236,052,117 + 45 * 239,517,357 = 56,171,025,234`, where 306,789,822 is the entry (1/n, the forward
  transform of `A0/n` on `O2`, the forward top and middle of `A0` on `O1`) plus the exit step (multiplier 1, then the truncated
  inverse on `O2`), counted the same way. With the 100 operations (`STAGE_BK`) of the switch to stage D, which the ledger
  attributes to the stage being closed, this is the stage C row of 6.2, 56,171,025,334.

### 6.4 Stages B and prep

Stage B: per evaluated point (`n'` of them) two line evaluations (2 units), the centre plus and minus the point (one addition,
one subtraction), the difference and its scaling (one subtraction, one multiplication), one store and the two running powers (two
multiplications); per skipped point (65,536) the two running powers; one bit-reversed successor per point (`2^20` calls of
`brv_next`, `7 + 4c` each); `LOOPC(15)` per row of 15 and the outer loop. Total, with the switch to prep: 571,342,950
(`2 n' = 1,966,080` units = 548,536,320 operations, plus 22,806,630 other operations).

Stage prep by component (Appendix A, `stage_prep`; the truncated transforms are the passes of 6.3 at the full depth range 4-20, and
the cyclic products of the Newton iteration are full transforms of `2^1 .. 2^18` points):

| component | count |
|---|---:|
| copy of the values, truncated inverse on O1 (coefficients of G* = n gt) | 67,884,999 |
| checks: coefficients m+1..n'-1 zero, coefficient m nonzero | 45,345 |
| f = rev_m(G*) to precision k+1 = 137551 | 1,100,410 |
| h = 1/f mod X^(k+1): Newton iteration, cyclic products of 2..2^18 points | 167,734,595 |
| division by 1 - c1 X^w (recurrence h_i += c1 h_(i-w)) | 864,194 |
| q reversed into B3, truncated forward on O1 | 66,397,088 |
| values -q G* on O1, truncated inverse (coefficients of A0) | 71,817,159 |
| G2: truncated forward of G* on O2 | 61,626,328 |
| Gi: batch inversion (prefix products, one inversion, back pass) | 21,628,749 |
| block factors (blk_scale of Gi and G2) | 18,710,596 |
| delta_j, j < 15 | 332 |
| trial bookkeeping after prep and the switch to stage C | 102 |
| **prep** | **477,809,897** |

### 6.5 Stage D on the generic path

Stage D's row is the recovery of `g` from `G2` (two `blk_scale` passes and the truncated inverse on `O2`), the subtraction of
`kappa`, the degree test, the half-gcd and the trial bookkeeping. The half-gcd is a fixed recursion by the lemma of 6.1. Its
driver makes 24 iterations, then Euclid's algorithm from degree 82 down to `G` (51,067 operations for `deg G = 1`).

Driver iterations (the product kind: `tr` = the truncated product on `O1`, `3` = `3 * 2^(l-2)` points, `full` = `2^l` points;
"rows from values" = rows of the product inside the subgroup where the driver's call returned values; "own" = the apply, the
division, the degree scans and the loop's control, without the hgcd call):

| iteration | deg a | k | deg c | l | product | rows from values | hgcd call | own |
|---:|---:|---:|---:|---:|---|---:|---:|---:|
| 1 | 976,562 | 131,071 | 845,491 | 20 | tr | 0 | 1,309,060,352 | 584,460,842 |
| 2 | 845,490 | 131,071 | 714,419 | 20 | 3 | 1 | 1,309,060,352 | 410,127,351 |
| 3 | 714,418 | 131,071 | 583,347 | 20 | 3 | 1 | 1,309,060,352 | 408,712,991 |
| 4 | 583,346 | 131,071 | 452,275 | 19 | full | 1 | 1,309,060,352 | 259,656,146 |
| 5 | 452,274 | 131,071 | 321,203 | 19 | 3 | 1 | 1,309,060,352 | 200,747,458 |
| 6 | 321,202 | 131,071 | 190,131 | 18 | 3 | 2 | 1,309,060,352 | 103,237,849 |
| 7 | 190,130 | 65,535 | 124,595 | 17 | full | 1 | 589,228,908 | 61,658,321 |
| 8 | 124,594 | 32,767 | 91,827 | 17 | 3 | 1 | 263,463,872 | 45,385,628 |
| 9 | 91,826 | 32,767 | 59,059 | 16 | full | 1 | 263,463,872 | 29,138,286 |
| 10 | 59,058 | 16,383 | 42,675 | 16 | 3 | 1 | 116,753,948 | 21,722,577 |
| 11 | 42,674 | 16,383 | 26,291 | 15 | full | 1 | 116,753,948 | 13,799,051 |
| 12 | 26,290 | 8,191 | 18,099 | 15 | 3 | 1 | 51,341,832 | 10,202,142 |
| 13 | 18,098 | 8,191 | 9,907 | 14 | 3 | 2 | 51,341,832 | 5,244,733 |
| 14 | 9,906 | 4,095 | 5,811 | 13 | 3 | 2 | 22,343,708 | 2,540,258 |
| 15 | 5,810 | 2,047 | 3,763 | 12 | full | 1 | 9,570,904 | 1,464,178 |
| 16 | 3,762 | 1,023 | 2,739 | 12 | 3 | 1 | 4,044,852 | 1,068,077 |
| 17 | 2,738 | 1,023 | 1,715 | 11 | full | 1 | 4,044,852 | 677,279 |
| 18 | 1,714 | 511 | 1,203 | 11 | 3 | 1 | 1,678,656 | 500,154 |
| 19 | 1,202 | 511 | 691 | 10 | 3 | 2 | 1,678,656 | 271,809 |
| 20 | 690 | 255 | 435 | 9 | full | 1 | 664,940 | 151,257 |
| 21 | 434 | 127 | 307 | 9 | 3 | 1 | 255,500 | 109,884 |
| 22 | 306 | 127 | 179 | 8 | 3 | 2 | 255,500 | 58,315 |
| 23 | 178 | 63 | 115 | 7 | full | 1 | 92,319 | 31,843 |
| 24 | 114 | 31 | 83 | 7 | 3 | 0 | 24,520 | 25,955 |

The hgcd calls by budget `k` and role, with the charge of one call excluding its children ("driver call" = the top call of an
iteration, which returns values on the subgroup of size `2^lm`; "saved M1" = the node keeps `M1`'s transforms from its apply;
"returns values" = the node also writes its result's values on the parent's subgroup row; "first child" = its output region is
free from the start). Base calls (`k = 31`) differ by the 4 operations of the truncation offset. The call counts follow from the
recursion: an iteration whose top budget is `2^j - 1` makes `2^(j-i)` calls of budget `2^i - 1` (`i = 5 .. j`), for example
30,515 base calls in all. Each charge per call is a sum of the components of the code (the transforms of 6.3's pass structure at
the call's sizes, the fused pointwise loops, the pseudo-division and the bookkeeping), which Appendix A lists function by function:

| k | role | calls | own charge per call | total |
|---:|---|---:|---:|---:|
| 131,071 | driver call | 6 | 130,407,154 | 782,442,924 |
| 65,535 | driver call | 1 | 62,192,054 | 62,192,054 |
| 65,535 | saved M1, returns values | 6 | 62,289,743 | 373,738,458 |
| 65,535 | saved M1, returns values, first child | 6 | 62,289,747 | 373,738,482 |
| 32,767 | driver call | 2 | 29,834,594 | 59,669,188 |
| 32,767 | saved M1, returns values | 13 | 29,889,147 | 388,558,911 |
| 32,767 | saved M1, returns values, first child | 13 | 29,889,151 | 388,558,963 |
| 16,383 | driver call | 2 | 14,046,662 | 28,093,324 |
| 16,383 | saved M1, returns values | 28 | 14,107,351 | 395,005,828 |
| 16,383 | saved M1, returns values, first child | 28 | 14,107,355 | 395,005,940 |
| 8,191 | driver call | 2 | 6,648,970 | 13,297,940 |
| 8,191 | saved M1, returns values | 58 | 6,660,779 | 386,325,182 |
| 8,191 | saved M1, returns values, first child | 58 | 6,660,783 | 386,325,414 |
| 4,095 | driver call | 1 | 3,184,182 | 3,184,182 |
| 4,095 | saved M1, returns values | 118 | 3,186,903 | 376,054,554 |
| 4,095 | saved M1, returns values, first child | 118 | 3,186,907 | 376,055,026 |
| 2,047 | driver call | 1 | 1,478,810 | 1,478,810 |
| 2,047 | saved M1, returns values | 237 | 1,487,667 | 352,577,079 |
| 2,047 | saved M1, returns values, first child | 237 | 1,487,671 | 352,578,027 |
| 1,023 | driver call | 2 | 694,110 | 1,388,220 |
| 1,023 | saved M1, returns values | 475 | 695,303 | 330,268,925 |
| 1,023 | saved M1, returns values, first child | 475 | 695,307 | 330,270,825 |
| 511 | driver call | 2 | 343,410 | 686,820 |
| 511 | saved M1, returns values | 952 | 340,123 | 323,797,096 |
| 511 | saved M1, returns values, first child | 952 | 340,127 | 323,800,904 |
| 255 | driver call | 1 | 153,966 | 153,966 |
| 255 | saved M1, returns values | 1,906 | 156,647 | 298,569,182 |
| 255 | saved M1, returns values, first child | 1,906 | 156,651 | 298,576,806 |
| 127 | driver call | 2 | 72,242 | 144,484 |
| 127 | saved M1, returns values | 3,813 | 72,227 | 275,401,551 |
| 127 | saved M1, returns values, first child | 3,813 | 72,231 | 275,416,803 |
| 63 | driver call | 1 | 43,283 | 43,283 |
| 63 | saved M1, returns values | 7,628 | 42,591 | 324,884,148 |
| 63 | saved M1, returns values, first child | 7,628 | 42,595 | 324,914,660 |
| 31 | base | 15,257 | 24,516 | 374,040,612 |
| 31 | base | 15,258 | 24,520 | 374,126,160 |

Sum: hgcd calls 9,351,364,731 + driver iterations 2,160,992,384 + the rest of stage D (the recovery of `g`, `XT`, the final Euclid
loop, the bookkeeping) 72,475,024 = 11,584,832,139. The arena (Appendix A mirrors `aalloc`/`arel` exactly) peaks at 1,900,548 of its
1,966,080 words.

### 6.6 Stages E to I and the fixed stages

* Stage E: for `deg G = 1`, 125 operations (copy of `G`, `S = -G_0`, bookkeeping). For `deg G = d >= 2`, one shift costs at
  most `e(d)` (the schoolbook powering of `(X + delta)^((p-1)/2) mod G` with its per-coefficient charges, the worst scan of `r - 1`,
  the worst `gcd_small` over every remainder sequence, and a split), and at most 256 shifts run, all at degree at most `d`:

| d | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `e(d)` | 49,853 | 106,660 | 185,345 | 285,908 | 408,349 | 552,668 | 718,865 |
| stage E bound (256 shifts) | 12,762,500 | 27,305,099 | 47,448,466 | 73,192,601 | 104,537,504 | 141,483,175 | 184,029,614 |

* Stage F: the fixed part (the two exponentiations of `fp_sqrt`, three per back-map, the line points and the switch) costs
  15,256. The Tonelli-Shanks loop finds the orders `2^i` of `b`, strictly decreasing. For the certificate's `S` the orders are
  `30, 28, 27, 25, 24, 18, 15, 14, 13, 11, 3`, a loop of 1,257, so stage F costs 16,513. Over every strictly decreasing sequence of orders below 32 the
  loop costs at most 2,885, so stage F costs at most 18,141.
* Fixed stages: init 109,840 (100 + 100 for the stage switches, `PROLOGUE` 5,000, `CONSTS_GEN` 100,000, the tables of
  `tw_init` 4,640); setup 2,180 (`line_setup`, one inversion of 1,870 operations, and the switch); A 127; G
  693 (two units, the comparison, the trial bookkeeping, the loop exit and the switch); H 4,852 (six encodings of 792 and
  the switch); I 3,382,436 (the bounds of 4.2 and the switch).

### 6.7 Total

`N_claim = 68,992,558,203` (6.2): the generic path for `deg G = 1`, 68,808,527,086, plus 184,031,117 = (stage E's bound at `deg G = 8` minus its
count at `deg G = 1`) + (stage F's worst case minus its count for the certificate's `S`). Stage D's count for `deg G = d` is that of
`deg G = 1` minus 32, 78, 138, 212, 300, 402, 518 for `d = 2 .. 8` (a shorter final Euclid loop), so the stage-wise maximum is an
upper bound for every `deg G <= 8`.

### 6.8 Corroboration: the executed run (not used by the claim)

The instrumented program of section 9 counts every charge at run time, so its printed counters are an independent check of the
derivation. It was built with `gcc -Os -march=native -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -fno-tree-loop-distribute-patterns -o single main.c hgcd.c stageb.c stagec.c line.c ntt.c fp.c nolibc.c` (gcc (GCC) 16.2.1 20260810; the binary's SHA-256 is `5a164a2540a0cfa904d93900cf7c6aa0e4619897ec213f37e5bfcc967b8a16d2`; with `-march=native` the binary, but not the
counts, depends on the compiler and CPU) and run once as `single 3` under a 64 KiB stack limit (about 858 s on that machine). It took the generic path
with `deg G = 1` (`degG 1` in its output), and every stage row it printed (each counter of each row) equals column "deg G = 1" of
6.2. Its total is 68,808,527,086, its stage-D profile is `base cases 743,955,700, applies inside hgcd 5,091,059,614, applies of the driver 2,084,069,714, matrix products 3,247,045,227`, and its arena peak is 1,900,548 words. The organizer did
not run it; the claim does not depend on it. Its complete output (the program's single write, then the launcher's line):

```
Orchard Poseidon r=3 m=976562 n=1048576 steps=236 kmax=131071
trial 1 centre 1 degG 1 arena_peak_words 1900548 ops 68805027673
collision found after 1 trials
centre 0000000000000000000000000000000000000000000000000000000000000001
nk1 0499f5c4354bafa11ca451e656d380d078444ed6561d6355487453741e1a6815
rho1 21625d728b86cf0865d7ad7cd99a0c20464939e5253940d95b3a639d7a909af7
nk2 1009050c8c1414cf5975db612457a2e49b06db64fce28c7dd5ad52ed8fc2c567
rho2 31611cd777dc6c418e048d96a497f46fa51523b47dbadcd97d0ad171160fcdb8
digest 325165c946fe20c28af82e940ec89fca03e6fb74afa1a3fa28a54e552a1f12ec
stage init 109840 add 0 sub 0 mul 513 sqr 59 ld 561 st 458 ctl 108249 unit 0
stage setup 2180 add 25 sub 4 mul 119 sqr 262 ld 44 st 10 ctl 1716 unit 0
stage A 127 add 0 sub 0 mul 1 sqr 0 ld 0 st 0 ctl 126 unit 0
stage B 571342950 add 983040 sub 1966080 mul 3080192 sqr 0 ld 0 st 983040 ctl 15794278 unit 548536320
stage prep 477809897 add 62069076 sub 63373332 mul 69215217 sqr 1877057 ld 61370243 st 48329531 ctl 171575441 unit 0
stage C 56171025334 add 9655288045 sub 9475424493 mul 10224511881 sqr 701394478 ld 7479492708 st 4905242955 ctl 13729670774 unit 0
stage D 11584832139 add 1525004161 sub 1473636530 mul 1876394860 sqr 62970752 ld 1493607643 st 1114715130 ctl 4038503063 unit 0
stage E 125 add 0 sub 1 mul 0 sqr 0 ld 3 st 2 ctl 119 unit 0
stage F 16513 add 5 sub 5 mul 862 sqr 2199 ld 12 st 0 ctl 13430 unit 0
stage G 693 add 0 sub 0 mul 0 sqr 0 ld 0 st 0 ctl 135 unit 558
stage H 4852 add 0 sub 0 mul 6 sqr 0 ld 0 st 0 ctl 4846 unit 0
stage I 3382436 add 0 sub 0 mul 0 sqr 0 ld 0 st 0 ctl 3382436 unit 0
stageD_profile base 743955700 node_apply 5091059614 driver_apply 2084069714 products 3247045227
total 68808527086 counters 68808527086 trials 68805027673 outside_trials 3499413 RECONCILE ok=1
# exit 0 wall 858.2s maxrss 122904 KiB
```

The cost model of stage D was also compared with the instrumented half-gcd (`test_d.c`, section 10, run as `test_d <degree> 131071`,
i.e. `kmax = 131071` as at full size) on random inputs of degrees 50, 97, 98, 120, 200, 513, 1,000, 1,500, 2,047, 2,048, 4,000, 6,000, 8,191, 9,000, 12,000, 16,385, 20,000, 30,000, 40,000, 70,000, 125,000, 250,000, 500,000, 976,562 (gcd of degree 0; buffers of `15 * 2^(L-4)` words as at full size, so that the truncated first product runs wherever
it is needed): the charge, the four profile parts and the arena peak agreed exactly in every case. These comparisons are development checks and were not run by the
organizer.

## 7. Memory

The executable is linked statically without any C library (`nolibc.c` supplies the process entry, the two system calls and
`memcpy`/`memset`/`memmove`/`memcmp`). Its whole loadable image, from `size`: text 129,938 + data 16 + bss 125,856,032 = 125,985,986
bytes. The bss contains every buffer of the run:
* the static region `REG` of `4 n' = 3,932,160` words (125,829,120 bytes). Stages B, prep and C use its four quarters as the
  buffers of 4.4-4.5. Stage D keeps `g` and `kappa (R - 1)` in two quarters and uses the other two (1,966,080 words) as its stack
  arena; on the generic path the arena peaks at 1,900,548 words (6.5);
* the twiddle tables `T0`, `T1`, `T2` (3 x 128 words), the tables of the truncated top (2 x 2 x 32 words), `DL` (15 words);
* the 8,192-byte output buffer and the small static state.

Nothing is mapped at run time (no `mmap`, no `brk`). The stack bound is 65,536 bytes:
* Frames: GCC's call graph with per-function stack usage for the same build (`-fcallgraph-info=su` added to the command of 6.8
  produces a byte-identical binary) gives, over every call chain from the entry `c_start`, at most 39,456 bytes. This
  counts 13 nested frames of the recursive `hgcd` (budgets `2^17 - 1` down to 31, the depth on the generic path of H2(b)), each frame at GCC's bound with its return
  address, and charges the deepest callee chain below the innermost frame. The deepest chain is c_start 16, main 3328, hg_gcd 784, hgcd 2384 x 13, mat_mul_f 1728, row_entry 80, ntt_fwd_b 8, ntt_fwd_bz 80, top_pass_k 1120, k16i 832, fp_mul 96, mont_raw 384, sub256 8.
* Process data: the kernel places the arguments, the environment, their pointers and the auxiliary vector at the top of the
  stack, and the entry stub aligns the stack by at most 15 bytes. The program reads only `argv[1]` and needs no environment. The
  bound leaves `65,536 - 39,456 - 16 = 26,064` bytes for this data (a typical shell environment is a few KiB).

The run of 6.8 was executed under `RLIMIT_STACK = 64 KiB`. Total: 125,985,986 + 65,536 = 126,051,522 bytes `= 2^26.909438`, claimed as
`26.9095` (rounded up). The memory penalty is `6.9095`; normalized cost `27.88161 + 6.9095 = 34.79111`.

## 8. What is provided, testing, reproduction

* Provided: the derivation (sections 2-3), the algorithm and its charging (4), the derived count (6) and memory (7), the complete
  source (9), the cost model (Appendix A) and the collision certificate (`certificates/`, checked by the organizer's hash).
* The claim rests on the source, the charging rules (H1), the generic-path premise (H2) and shift splitting (H3, for
  `deg G >= 2`), and on the source implementing the algorithms of sections 3-4 as stated (derived there; a defect would end trial
  1 without producing a false collision, since stage G checks the pair with the reference permutation). No Python experiment is
  declared, and nothing in the claim depends on an execution of the C program. The counts of section 6 are closed forms (stage C,
  stage B, the fixed stages) or values computed by the cost model of Appendix A from the charge statements (prep, stage D, the
  bounds of stages E and F). The organizer has not run the cost model; it is a deterministic calculation (standard library, about
  10 minutes) that a reader can re-run, or check piecewise against the tables of 6.4-6.6.
* Development tests (not part of the claim; run during development with the same source; their programs are not reproduced here,
  except `test_d.c`, section 10):
  - Transforms: `ntt_fwd_bz` (with zero extension) and `ntt_inv_b` against naive evaluation for every size up to `2^12` and node
    offsets 0, the coset and random; `tr_fwd` and `tr_inv` against naive evaluation for `L = 7 .. 12` and both subtrees.
  - Prep + stage C against FLINT (`pow_mod(X, v 2^nb + bits, g)` for random `g` of degree `m` with `0.75 n < m < n'`, random bits,
    several start exponents `v`), `L = 8 .. 13`.
  - Stage D against FLINT's gcd on random pairs, pairs with common factors of degree 3 and `n/4`, low-degree second inputs, forced
    degree gaps, sparse inputs and Euclid sequences built with abnormal quotients, at degrees 950-7629, with the buffers of `a`
    and `b` sized `15 * 2^(L-4)` (so that the driver's first product takes the truncated path, as at full size), under
    AddressSanitizer and UBSan.
  - The whole program at r = 2 (`single 2`) found a collision (verified by the reference permutation in stage G), with identical
    counts from `-Os` and `-O3` builds.
* The cost claim assumes the model of 4.2. Costs outside it (cache, bandwidth) are not part of it.
* Reproduction: `python3 -I gen_consts.py <pareto/orchard-pallas-constants.json> > consts.h` (its first line records the SHA-256 of
  that file, `ab79bd05cbdcbe7c4c63ef7a4b95ffe8ec8938c1d71b49ceeebaf5b3f80aee62`); build with the command of 6.8 (gcc (GCC) 16.2.1 20260810 on Linux 7.2.8-arch1-2 x86_64, CPU 11th Gen Intel(R) Core(TM) i7-1185G7 @ 3.00GHz; the same toolchain and CPU flags rebuild
  the identical binary); run `single 3` under a 64 KiB stack limit. The cost model: `python3 derive.py <S> derived.json` (Appendix
  A; about 10 minutes) prints `N(deg G = 1)` and `N_claim`.

## 9. Complete source of the instrumented program

Files: `fp.h`, `fp.c` (field and counters), `consts.h` (generated by `gen_consts.py`), `ntt.h`, `ntt.c` (transforms, including the
truncated sets), `line.h`, `line.c` (the line, line evaluation, back-map, reference hash), `stageb.h`, `stageb.c` (stage B and
prep), `stagec.h`, `stagec.c` (stage C), `hgcd.h`, `hgcd.c` (stage D), `main.c` (trial loop, stages E-I, report), `nolibc.c`
(entry, system calls), `gen_consts.py`. SHA-256 of each file is listed with it.

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

SHA-256 `05d0d95994dcdee22a9a975699cce4b8daf84d7ff36614032adac6332c8ac858`, 20562 bytes. Generated by `python3 -I gen_consts.py orchard-pallas-constants.json > consts.h` (below); not reproduced here. It defines `TREE_K = 21`, the limbs of `p`, `-p^-1 mod 2^64`, `2^256 mod p`, `2^512 mod p`, `psi` and its inverse, and the round constants and MDS matrix in Montgomery form. Its first line records the SHA-256 of the organizer file:

```c
/* generated by gen_consts.py from zcash/halo2 halo2_poseidon-0.2.0 halo2_poseidon/src/fp.rs, SHA-256 ab79bd05cbdcbe7c4c63ef7a4b95ffe8ec8938c1d71b49ceeebaf5b3f80aee62 */
```

### ntt.h

SHA-256 `523497b7f2e69da2ef8348096a3fa9c398ff77a756f5965f79f284b6bcb2147b`, 1773 bytes.

```c
/* Number-theoretic transforms over Pallas on the subgroup tree of 2^K-th roots of unity.
 *
 * Node (d, j) of the tree (depth d, index j < 2^d) is the modulus X^(2^(K-d)) - psi_d^brv_d(j); it splits into
 * (d+1, 2j) and (d+1, 2j+1) with the twiddle t(d, j) = psi_(d+1)^brv_d(j).  A transform of size 2^L is the subtree of a node of
 * depth K-L, given by its offset B (the node's root of unity is psi^(B 2^L)): B = 0 is the subgroup H_L (modulus X^n - 1),
 * B = 2^(K-L-1) = J0 2^(K-L-1) with J0 = 1 its coset (X^n + 1).  Forward: natural-order coefficients in, values in bit-reversed
 * order out (position j holds the value at the root of leaf j).  Inverse: the transpose, returning 2^L times the coefficients.
 *
 * Truncated sets: O(L, J0) is the union of the depth-4 nodes 0..14 of the size-2^L subtree J0 (all but the last), n' = 15 2^(L-4)
 * points at positions [0, n') of the transform order.  tr_fwd maps a polynomial of degree < n' to its values there; tr_inv maps
 * the values of such a polynomial back to 2^L times its coefficients (the coefficients of degree >= n' are known to be zero). */
#ifndef NTT_H
#define NTT_H
#include "fp.h"

void tw_init(void);
fp twiddle(uint32_t e);
fp twiddle_inv(uint32_t e);
uint32_t brv_next(uint32_t u, int bits);
void ntt_fwd_bz(fp *x, const fp *src, long len, int L, uint32_t B);
void ntt_fwd_b(fp *x, int L, uint32_t B);
void ntt_inv_b(fp *x, int L, uint32_t B);
void ntt_fwd(fp *x, int L, int J0);
void ntt_inv(fp *x, int L, int J0);

void tr_top(fp *x, int L, int jin, int jout);
void tr_range(fp *x, int L, int J0, int dlo, int dhi, int dir);
void tr_fwd(fp *x, int L, int J0);
void tr_inv(fp *x, int L, int J0);

extern const uint8_t BRV4[16];
extern fp C_PSI2, C_PSI3, C_PSI33, C_IPSI2, C_IPSI3, C_IPSI33;
#endif
```

### ntt.c

SHA-256 `3c3261045aee97e33488c8a61cbad0baa32d5060822e1eab7c99d79c56df4182`, 30379 bytes.

```c
/* Transforms (see ntt.h).  Register model (18 words of 256 bits): a radix-8 block keeps its 8 data words, its 7 twiddles and one
 * temporary in registers, plus the running supergroup twiddle and its step where a pass advances them; a radix-16 block keeps its
 * 16 data words, the current twiddle and one temporary, and loads each twiddle from a 15-word array when its layer starts.  Every
 * array element is loaded and stored once per pass. */
#include "ntt.h"

/* Twiddle tables, three levels of 7 bits (K = 21): psi^e = T0[e mod 2^7] * T1[(e >> 7) mod 2^7] * T2[e >> 14]. */
#define TW_BITS 7
#define TW_N (1u << TW_BITS)
static fp T0[TW_N], T1[TW_N], T2[TW_N];
fp C_PSI2, C_PSI3, C_PSI33, C_IPSI2, C_IPSI3, C_IPSI33;
static fp C16[4], C16I[4]; /* psi_4^(1,5,3,7) and their inverses (psi_d of order 2^d) */
/* Truncated top (tr_top): twiddle t(t, j) of local node (t, j) of subtree J0, i.e. psi^(brv_t(j) 2^(K-t-1) + J0 2^(K-t-2)), and its
 * inverse. */
static fp TW[2][4][8], ITW[2][4][8];
const uint8_t BRV4[16] = {0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15};

/** Return psi^e for 0 <= e < 2^K: three table loads, two multiplications, two masks and two shifts. */
fp twiddle(uint32_t e)
{
    CTL(4);
    LD(3);
    return fp_mul(fp_mul(T0[e & (TW_N - 1)], T1[(e >> TW_BITS) & (TW_N - 1)]), T2[e >> (2 * TW_BITS)]);
}

/** Return psi^(-e) = psi^(2^K - e) (negation and mask, then twiddle). */
fp twiddle_inv(uint32_t e)
{
    CTL(2);
    return twiddle(((1u << TREE_K) - e) & ((1u << TREE_K) - 1));
}

static fp tw2(uint32_t e, int inv) { return inv ? twiddle_inv(e) : twiddle(e); }

/** Build the three-level twiddle tables psi^e = T0[e mod 2^7] T1[(e >> 7) mod 2^7] T2[e >> 14], the pass constants and the tables of the
 *  truncated top. */
void tw_init(void)
{
    const fp psi = {PSI_LIMBS}, ipsi = {PSI_INV_LIMBS};
    fp *tab[3] = {T0, T1, T2};
    fp step = psi;
    for (int l = 0; l < 3; l++) {
        fp *T = tab[l];
        T[0] = FP_ONE;
        ST(1);
        for (uint32_t i = 1; i < TW_N; i++) {
            T[i] = fp_mul(T[i - 1], step);
            LD(1);
            ST(1);
        }
        LOOPC(TW_N - 1);
        for (int i = 0; i < TW_BITS; i++) step = fp_sqr(step);
        LOOPC(TW_BITS);
        CTL(2);
    }
    LOOPC(3);
    fp c4 = psi, ic4 = ipsi;
    for (int i = 0; i < TREE_K - 4; i++) {
        c4 = fp_sqr(c4);
        ic4 = fp_sqr(ic4);
    }
    LOOPC(TREE_K - 4);
    fp c3 = fp_sqr(c4), ic3 = fp_sqr(ic4);
    C_PSI3 = c3;
    C_PSI2 = fp_sqr(c3);
    C_PSI33 = fp_mul(C_PSI2, c3);
    C_IPSI3 = ic3;
    C_IPSI2 = fp_sqr(ic3);
    C_IPSI33 = fp_mul(C_IPSI2, ic3);
    ST(6);
    C16[0] = c4;
    C16[1] = fp_mul(fp_mul(c3, c3), c4);
    C16[2] = fp_mul(c3, c4);
    C16[3] = fp_mul(fp_mul(c3, c3), C16[2]);
    C16I[0] = ic4;
    C16I[1] = fp_mul(fp_mul(ic3, ic3), ic4);
    C16I[2] = fp_mul(ic3, ic4);
    C16I[3] = fp_mul(fp_mul(ic3, ic3), C16I[2]);
    ST(8);
    for (int J0 = 0; J0 < 2; J0++) {
        for (int t = 0; t < 4; t++) {
            for (int j = 0; j < (1 << t); j++) {
                uint32_t br = (uint32_t)BRV4[j] >> (4 - t);
                uint32_t e = (br << (TREE_K - t - 1)) + ((uint32_t)J0 << (TREE_K - t - 2));
                TW[J0][t][j] = twiddle(e);
                ITW[J0][t][j] = twiddle_inv(e);
                ST(2);
                CTL(10);
            }
            LOOPC(1 << t);
        }
        LOOPC(4);
    }
    LOOPC(2);
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

/* Kernels on in[0], in[is], ... (read) and x[0], x[st], ... (written); ldn is the number of memory loads of the call (the radix,
 * or fewer for a zero-extended block of ntt_fwd_bz whose missing inputs are zero registers); triv = 1 when the block's node
 * twiddles are 1. */
static inline void k2f(const fp *in, size_t is, fp *x, size_t st, const fp *w, int triv, int ldn)
{
    fp a0 = in[0], a1 = in[is];
    LD(ldn);
    if (triv) CT1(a0, a1); else CT(a0, a1, w[0]);
    x[0] = a0; x[st] = a1;
    ST(2);
}

static inline void k2i(const fp *in, size_t is, fp *x, size_t st, const fp *w, int triv, int ldn)
{
    fp a0 = in[0], a1 = in[is];
    LD(ldn);
    if (triv) GS1(a0, a1); else GS(a0, a1, w[0]);
    x[0] = a0; x[st] = a1;
    ST(2);
}

static inline void k4f(const fp *in, size_t is, fp *x, size_t st, const fp *w, int triv, int ldn)
{
    fp a0 = in[0], a1 = in[is], a2 = in[2 * is], a3 = in[3 * is];
    LD(ldn);
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

static inline void k4i(const fp *in, size_t is, fp *x, size_t st, const fp *w, int triv, int ldn)
{
    fp a0 = in[0], a1 = in[is], a2 = in[2 * is], a3 = in[3 * is];
    LD(ldn);
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

static inline void k8f(const fp *in, size_t is, fp *x, size_t st, const fp *w, int triv, int ldn)
{
    fp a0 = in[0], a1 = in[is], a2 = in[2 * is], a3 = in[3 * is], a4 = in[4 * is], a5 = in[5 * is], a6 = in[6 * is], a7 = in[7 * is];
    LD(ldn);
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

static inline void k8i(const fp *in, size_t is, fp *x, size_t st, const fp *w, int triv, int ldn)
{
    fp a0 = in[0], a1 = in[is], a2 = in[2 * is], a3 = in[3 * is], a4 = in[4 * is], a5 = in[5 * is], a6 = in[6 * is], a7 = in[7 * is];
    LD(ldn);
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

/* Radix-16 kernels (4 layers), written out straight-line with constant indices (macros R16, R8C, R4C): each of the 15 twiddles
 * is loaded from the array w when its layer starts (fewer if triv). */
#define R16(M) M(0) M(1) M(2) M(3) M(4) M(5) M(6) M(7) M(8) M(9) M(10) M(11) M(12) M(13) M(14) M(15)
#define R8C(M) M(0) M(1) M(2) M(3) M(4) M(5) M(6) M(7)
#define R4C(M) M(0) M(1) M(2) M(3)
#define TWL(i) (LD(1), w[i])
#define K16_LD(i) a[i] = in[(i) * is];
#define K16_ST(i) x[(i) * st] = a[i];
#define F_L1T(i) CT1(a[i], a[(i) + 8]);
#define F_L1(i) CT(a[i], a[(i) + 8], t);
#define F_L2T(i) CT1(a[i], a[(i) + 4]);
#define F_L2(i) CT(a[i], a[(i) + 4], t);
#define F_L2B(i) CT(a[8 + (i)], a[12 + (i)], t);
#define I_L1T(i) GS1(a[i], a[(i) + 8]);
#define I_L1(i) GS(a[i], a[(i) + 8], t);
#define I_L2T(i) GS1(a[i], a[(i) + 4]);
#define I_L2(i) GS(a[i], a[(i) + 4], t);
#define I_L2B(i) GS(a[8 + (i)], a[12 + (i)], t);
static inline void k16f(const fp *in, size_t is, fp *x, size_t st, const fp *w, int triv, int ldn)
{
    fp a[16], t;
    R16(K16_LD)
    LD(ldn);
    if (triv) {
        R8C(F_L1T)
        R4C(F_L2T)
    } else {
        t = TWL(0);
        R8C(F_L1)
        t = TWL(1);
        R4C(F_L2)
    }
    t = TWL(2);
    R4C(F_L2B)
    if (triv) { CT1(a[0], a[2]); CT1(a[1], a[3]); }
    else { t = TWL(3); CT(a[0], a[2], t); CT(a[1], a[3], t); }
    t = TWL(4); CT(a[4], a[6], t); CT(a[5], a[7], t);
    t = TWL(5); CT(a[8], a[10], t); CT(a[9], a[11], t);
    t = TWL(6); CT(a[12], a[14], t); CT(a[13], a[15], t);
    if (triv) CT1(a[0], a[1]);
    else { t = TWL(7); CT(a[0], a[1], t); }
    t = TWL(8); CT(a[2], a[3], t);
    t = TWL(9); CT(a[4], a[5], t);
    t = TWL(10); CT(a[6], a[7], t);
    t = TWL(11); CT(a[8], a[9], t);
    t = TWL(12); CT(a[10], a[11], t);
    t = TWL(13); CT(a[12], a[13], t);
    t = TWL(14); CT(a[14], a[15], t);
    R16(K16_ST)
    ST(16);
}

static inline void k16i(const fp *in, size_t is, fp *x, size_t st, const fp *w, int triv, int ldn)
{
    fp a[16], t;
    R16(K16_LD)
    LD(ldn);
    if (triv) GS1(a[0], a[1]);
    else { t = TWL(7); GS(a[0], a[1], t); }
    t = TWL(8); GS(a[2], a[3], t);
    t = TWL(9); GS(a[4], a[5], t);
    t = TWL(10); GS(a[6], a[7], t);
    t = TWL(11); GS(a[8], a[9], t);
    t = TWL(12); GS(a[10], a[11], t);
    t = TWL(13); GS(a[12], a[13], t);
    t = TWL(14); GS(a[14], a[15], t);
    if (triv) { GS1(a[0], a[2]); GS1(a[1], a[3]); }
    else { t = TWL(3); GS(a[0], a[2], t); GS(a[1], a[3], t); }
    t = TWL(4); GS(a[4], a[6], t); GS(a[5], a[7], t);
    t = TWL(5); GS(a[8], a[10], t); GS(a[9], a[11], t);
    t = TWL(6); GS(a[12], a[14], t); GS(a[13], a[15], t);
    if (triv) {
        R4C(I_L2T)
    } else {
        t = TWL(1);
        R4C(I_L2)
    }
    t = TWL(2);
    R4C(I_L2B)
    if (triv) {
        R8C(I_L1T)
    } else {
        t = TWL(0);
        R8C(I_L1)
    }
    R16(K16_ST)
    ST(16);
}

/** The twiddles of a block of r layers from the base twiddle b of its deepest layer (r = 4: b = w[7], stored to the 15-word array;
 *  r = 3: b = w[3]; r = 2: b = w[1]; r = 1: b = w[0]); forward constants if inv = 0. */
static void derive(fp b, int r, int inv, fp *w)
{
    fp p2 = inv ? C_IPSI2 : C_PSI2, p3 = inv ? C_IPSI3 : C_PSI3, p33 = inv ? C_IPSI33 : C_PSI33;
    if (r == 4) {
        const fp *c16 = inv ? C16I : C16;
        fp b2 = fp_sqr(b), b1 = fp_sqr(b2);
        LD(3);
        w[0] = fp_sqr(b1);
        w[1] = b1;
        w[2] = fp_mul(b1, p2);
        w[3] = b2;
        w[4] = fp_mul(b2, p2);
        w[5] = fp_mul(b2, p3);
        w[6] = fp_mul(b2, p33);
        w[7] = b;
        w[8] = fp_mul(b, p2);
        w[9] = fp_mul(b, p3);
        w[10] = fp_mul(b, p33);
        for (int i = 0; i < 4; i++) w[11 + i] = fp_mul(b, c16[i]);
        LD(4);
        LOOPC(4);
        ST(15);
    } else if (r == 3) {
        fp b1 = fp_sqr(b);
        LD(3);
        w[0] = fp_sqr(b1);
        w[1] = b1;
        w[2] = fp_mul(b1, p2);
        w[3] = b;
        w[4] = fp_mul(b, p2);
        w[5] = fp_mul(b, p3);
        w[6] = fp_mul(b, p33);
    } else if (r == 2) {
        LD(1);
        w[0] = fp_sqr(b);
        w[1] = b;
        w[2] = fp_mul(b, p2);
    } else {
        w[0] = b;
    }
}

/* The offsets o of a supergroup (st of them), the kernel at base + o: unrolled by 4 (one control operation and one loop iteration
 * per 4 kernels) when unr (st >= 4), else one loop iteration per kernel.  unr, like the radix, the direction and triv, is a
 * constant of the specialized pass (see pass_b). */
#define INNER(KERN, W, T) do {                                                                                             \
    if (unr) {                                                                                                             \
        for (size_t o = 0; o < st; o += 4) {                                                                               \
            CTL(1);                                                                                                        \
            KERN(base + o, st, base + o, st, W, T, R_);                                                                    \
            KERN(base + o + 1, st, base + o + 1, st, W, T, R_);                                                            \
            KERN(base + o + 2, st, base + o + 2, st, W, T, R_);                                                            \
            KERN(base + o + 3, st, base + o + 3, st, W, T, R_);                                                            \
        }                                                                                                                  \
        LOOPC(st / 4);                                                                                                     \
    } else {                                                                                                               \
        for (size_t o = 0; o < st; o++) {                                                                                  \
            CTL(1);                                                                                                        \
            KERN(base + o, st, base + o, st, W, T, R_);                                                                    \
        }                                                                                                                  \
        LOOPC(st);                                                                                                         \
    }                                                                                                                      \
} while (0)

/** One supergroup of r layers in place; r, dir, triv and unr are constants at every call (inlined). */
static inline void sgroup(fp *base, size_t st, int r, int dir, const fp *w, int triv, int unr)
{
    int R_ = 1 << r;
    if (r == 4) { if (dir) INNER(k16i, w, triv); else INNER(k16f, w, triv); }
    else if (r == 3) { if (dir) INNER(k8i, w, triv); else INNER(k8f, w, triv); }
    else if (r == 2) { if (dir) INNER(k4i, w, triv); else INNER(k4f, w, triv); }
    else { if (dir) INNER(k2i, w, triv); else INNER(k2f, w, triv); }
}

/* ---- full transforms of any node (prep, stage D) ---- */

/** Pass of r = 3 or 4 layers at depth d0 >= 1 of the size-2^L transform with offset B, in place (r, dir and unr constants).
 *  Supergroups are visited in the order of their bit-reversed index u, so that the base twiddle advances by one multiplication by
 *  step per supergroup (radix 8: the base and step stay in registers next to the block; radix 16: they are stored and reloaded
 *  around the block, 2 + 2 words).  G = brv(u) is advanced by brv_next.  The first supergroup (u = 0) is peeled: its node
 *  twiddles are 1 when B = 0. */
static inline void pass_b_k(fp *x, int L, uint32_t B, int d0, int r, int dir, int unr)
{
    size_t S = (size_t)1 << (L - d0), st = S >> r, ng = (size_t)1 << d0;
    uint32_t e = (B << (L - d0 - 1)) >> (r - 1), es = 1u << (TREE_K - d0 - r);
    CTL(10);
    fp b = tw2(e, dir), step = tw2(es, dir);
    fp w[15];
    derive(b, r, dir, w);
    if (r == 4) {
        ST(2);
        LD(2);
    }
    CTL(2);
    if (B == 0) sgroup(x, st, r, dir, w, 1, unr);
    else sgroup(x, st, r, dir, w, 0, unr);
    uint32_t G = brv_next(0, d0);
    for (size_t u = 1; u < ng; u++) {
        CTL(2);
        b = fp_mul(b, step);
        derive(b, r, dir, w);
        if (r == 4) {
            ST(2);
            LD(2);
        }
        sgroup(x + G * S, st, r, dir, w, 0, unr);
        G = brv_next(G, d0);
    }
    LOOPC(ng - 1);
}

/** The variant (radix r = 3 or 4, direction, unrolling) of a pass is selected once per pass; each branch is the same loop with
 *  constants. */
static void pass_b(fp *x, int L, uint32_t B, int d0, int r, int dir)
{
    int unr = L - d0 - r >= 2;
    CTL(6);
    if (r == 4) {
        if (dir) { if (unr) pass_b_k(x, L, B, d0, 4, 1, 1); else pass_b_k(x, L, B, d0, 4, 1, 0); }
        else { if (unr) pass_b_k(x, L, B, d0, 4, 0, 1); else pass_b_k(x, L, B, d0, 4, 0, 0); }
    } else {
        if (dir) { if (unr) pass_b_k(x, L, B, d0, 3, 1, 1); else pass_b_k(x, L, B, d0, 3, 1, 0); }
        else { if (unr) pass_b_k(x, L, B, d0, 3, 0, 1); else pass_b_k(x, L, B, d0, 3, 0, 0); }
    }
}

/** Number of layers of the top pass of a size-2^L transform: 4 (radix 16) if L = 1 mod 3 and L >= 4, else L mod 3, else 3; the
 *  remaining layers are radix-8 passes (for L = 2 mod 3 and L >= 11 the top is followed by one radix-16 pass at depth 4). */
static int top_layers(int L)
{
    CTL(3);
    if (L < 3) return L;
    if (L % 3 == 1) return 4;
    return L % 3 ? L % 3 : 3;
}

/** The top pass (depth 0, one supergroup, rt layers) of the size-2^L transform with offset B, reading src[0..len) zero-extended
 *  (forward only; len = 2^L otherwise) and writing x (rt and dir constants). */
static inline void top_pass_k(fp *x, const fp *src, long len, int L, uint32_t B, int rt, int dir)
{
    size_t st = (size_t)1 << (L - rt);
    int triv = B == 0, nr = 1 << rt;
    uint32_t e = (B << (L - 1)) >> (rt - 1);
    fp w[15];
    CTL(8);
    derive(tw2(e, dir), rt, dir, w);
    long full = len - (long)((size_t)(nr - 1) * st);
    CTL(4);
    for (size_t o = 0; o < st; o++) {
        const fp *in = src + o;
        size_t is = st;
        int ldn = nr;
        fp z[16];
        CTL(2);
        if ((long)o >= full) {
            /* some inputs of this block lie beyond len: zero registers, only the others are loaded */
            ldn = 0;
            for (int j = 0; j < nr; j++) {
                long idx = (long)(o + (size_t)j * st);
                z[j] = idx < len ? src[idx] : FP_ZERO;
                ldn += idx < len;
                CTL(3);
            }
            LOOPC(nr);
            in = z;
            is = 1;
        }
        CTL(1);
        if (rt == 4) { if (dir) k16i(in, is, x + o, st, w, triv, ldn); else k16f(in, is, x + o, st, w, triv, ldn); }
        else if (rt == 3) { if (dir) k8i(in, is, x + o, st, w, triv, ldn); else k8f(in, is, x + o, st, w, triv, ldn); }
        else if (rt == 2) { if (dir) k4i(in, is, x + o, st, w, triv, ldn); else k4f(in, is, x + o, st, w, triv, ldn); }
        else { if (dir) k2i(in, is, x + o, st, w, triv, ldn); else k2f(in, is, x + o, st, w, triv, ldn); }
    }
    LOOPC(st);
}

/** The variant (rt, dir) of the top pass is selected once per pass.  Inside the pass the test triv (B = 0) selects the trivial
 *  kernel; it is charged once per block (CTL(1) above). */
static void top_pass(fp *x, const fp *src, long len, int L, uint32_t B, int rt, int dir)
{
    CTL(4);
    if (rt == 4) { if (dir) top_pass_k(x, src, len, L, B, 4, 1); else top_pass_k(x, src, len, L, B, 4, 0); }
    else if (rt == 3) { if (dir) top_pass_k(x, src, len, L, B, 3, 1); else top_pass_k(x, src, len, L, B, 3, 0); }
    else if (rt == 2) { if (dir) top_pass_k(x, src, len, L, B, 2, 1); else top_pass_k(x, src, len, L, B, 2, 0); }
    else { if (dir) top_pass_k(x, src, len, L, B, 1, 1); else top_pass_k(x, src, len, L, B, 1, 0); }
}

/** Forward transform of the size-2^L subtree with offset B of src[0..len) zero-extended to 2^L words, into x (src may equal x when
 *  len = 2^L).  Top pass of top_layers(L) layers (two radix-16 passes for L = 2 mod 3, L >= 11), then radix-8 passes. */
void ntt_fwd_bz(fp *x, const fp *src, long len, int L, uint32_t B)
{
    if (L == 0) {
        x[0] = len > 0 ? src[0] : FP_ZERO;
        LD(len > 0);
        ST(1);
        CTL(1);
        return;
    }
    int rt = top_layers(L), two = L % 3 == 2 && L >= 11;
    CTL(4);
    if (two) rt = 4;
    top_pass(x, src, len, L, B, rt, 0);
    if (two) {
        pass_b(x, L, B, 4, 4, 0);
        rt = 8;
    }
    for (int d = rt; d < L; d += 3) {
        pass_b(x, L, B, d, 3, 0);
        CTL(4);
    }
    CTL(2); /* the loop's exit test */
    CTL(2);
}

void ntt_fwd_b(fp *x, int L, uint32_t B) { ntt_fwd_bz(x, x, 1L << L, L, B); }

/** Inverse transform of the size-2^L subtree with offset B, in place (returns 2^L times the coefficients), passes mirrored. */
void ntt_inv_b(fp *x, int L, uint32_t B)
{
    if (L == 0) return;
    int rt = top_layers(L), two = L % 3 == 2 && L >= 11;
    CTL(7);
    if (two) rt = 8;
    for (int d = L - 3; d >= rt; d -= 3) {
        pass_b(x, L, B, d, 3, 1);
        CTL(4);
    }
    CTL(2); /* the loop's exit test */
    if (two) {
        pass_b(x, L, B, 4, 4, 1);
        rt = 4;
    }
    top_pass(x, x, 1L << L, L, B, rt, 1);
    CTL(2);
}

void ntt_fwd(fp *x, int L, int J0) { CTL(1); ntt_fwd_bz(x, x, 1L << L, L, (uint32_t)J0 << (TREE_K - L - 1)); }
void ntt_inv(fp *x, int L, int J0) { CTL(1); ntt_inv_b(x, L, (uint32_t)J0 << (TREE_K - L - 1)); }

/* ---- truncated sets (stage C, prep, stage D's first product) ---- */

/** Pass of r = 1..4 layers at depth d0 >= 4 of the size-2^L transform J0 (dir 0 forward, 1 inverse; r, dir and unr constants),
 *  skipping the supergroups below the absent depth-4 node 15.  Supergroups are visited in the order of u = 16 uh + ul (their
 *  bit-reversed index), G = brv(u) = BRV4[ul] 2^(d0-4) + brv_(d0-4)(uh), so that the base twiddle advances by one multiplication
 *  per supergroup (two across the skipped one); the first supergroup of H_L (node twiddles 1) is peeled.  The base and its step
 *  are held as in pass_b. */
static inline void tr_pass_k(fp *x, int L, int J0, int d0, int r, int dir, int unr)
{
    size_t S = (size_t)1 << (L - d0), st = S >> r, nh = (size_t)1 << (d0 - 4);
    uint32_t es = 1u << (TREE_K - d0 - r), e0 = (uint32_t)J0 << (TREE_K - d0 - 1 - r);
    CTL(10);
    fp b = tw2(e0, dir), step = tw2(es, dir);
    fp w[15];
    uint32_t gh = 0;
    for (size_t uh = 0; uh < nh; uh++) {
        int ul0 = uh == 0 && J0 == 0;
        CTL(3);
        if (ul0) {
            derive(b, r, dir, w);
            if (r == 4) {
                ST(2);
                LD(2);
            }
            sgroup(x, st, r, dir, w, 1, unr);
            b = fp_mul(b, step);
        }
        for (int ul = ul0; ul < 15; ul++) {
            size_t G = (size_t)BRV4[ul] * nh + gh;
            CTL(5); /* G (table load, multiply, add) and the base x + G S (multiply, add) */
            derive(b, r, dir, w);
            if (r == 4) {
                ST(2);
                LD(2);
            }
            sgroup(x + G * S, st, r, dir, w, 0, unr);
            b = fp_mul(b, step);
        }
        LOOPC(15 - ul0);
        b = fp_mul(b, step);
        gh = brv_next(gh, d0 - 4);
    }
    LOOPC(nh);
}

/** The variant (r, dir, unrolling) of a truncated pass is selected once per pass. */
static void tr_pass(fp *x, int L, int J0, int d0, int r, int dir)
{
    int unr = L - d0 - r >= 2;
    CTL(8);
#define TRV(R) do { if (dir) { if (unr) tr_pass_k(x, L, J0, d0, R, 1, 1); else tr_pass_k(x, L, J0, d0, R, 1, 0); }               \
                    else { if (unr) tr_pass_k(x, L, J0, d0, R, 0, 1); else tr_pass_k(x, L, J0, d0, R, 0, 0); } } while (0)
    if (r == 4) TRV(4);
    else if (r == 3) TRV(3);
    else if (r == 2) TRV(2);
    else TRV(1);
}

/** The passes covering depths [dlo, dhi) (dlo >= 4) of the truncated transform J0, forward (dir 0) or inverse (dir 1, mirrored):
 *  from dlo one radix-16 pass if the number of layers is 1 mod 3 (two if 2 mod 3 and at least 8), else a radix-2 or radix-4
 *  pass if fewer than 4 layers remain unmatched, then radix-8 passes. */
void tr_range(fp *x, int L, int J0, int dlo, int dhi, int dir)
{
    int ds[8], rs[8], np = 0, nl = dhi - dlo, d = dlo;
    CTL(8);
    if (nl <= 0) return;
    int n16 = nl % 3 == 1 && nl >= 4 ? 1 : (nl % 3 == 2 && nl >= 8 ? 2 : 0);
    for (int i = 0; i < n16; i++) {
        ds[np] = d;
        rs[np++] = 4;
        d += 4;
        CTL(4);
    }
    LOOPC(n16);
    CTL(2);
    if ((dhi - d) % 3) {
        ds[np] = d;
        rs[np++] = (dhi - d) % 3;
        d += (dhi - d) % 3;
        CTL(6);
    }
    int n8 = 0;
    for (; d < dhi; d += 3) {
        ds[np] = d;
        rs[np++] = 3;
        n8++;
        CTL(3);
    }
    LOOPC(n8);
    for (int i = 0; i < np; i++) {
        int k = dir ? np - 1 - i : i;
        tr_pass(x, L, J0, ds[k], rs[k], dir);
        CTL(4);
    }
    LOOPC(np);
}

/* Truncated top, written out straight-line with constant indices: per offset the 15 present slot words in registers; the node
 * twiddle t(t, j) of subtree J is 1 exactly when J = 0 and j = 0 (its exponent brv_t(j) 2^(K-t-1) + J 2^(K-t-2) is 0), and every
 * other node twiddle is loaded once per offset (LD(1)); J is a constant of the specialized pass. */
#define TWF(J, t, j) (LD(1), TW[J][t][j])
#define TWI(J, t, j) (LD(1), ITW[J][t][j])

/** Inverse of the top 4 layers of subtree J with leaf 15 unknown and coefficient block 15 known to be zero (slot 15 of the output is
 *  not formed).  The complete subtrees (1,0), (2,2), (3,6) and leaf 14 are inverted first; with X1 = 8 (1,0), X2 = 4 (2,2),
 *  X3 = 2 (3,6) (residues times their scale), the top coefficients of the residues on the path to leaf 15 follow from block 15 = 0:
 *  T2 = X2[3] - t11 X1[7], T3 = X3[1] - t23 T2, leaf 15 = leaf 14 - t37 T3 (t = forward twiddles of nodes (1,1), (2,3), (3,7)). */
static inline void inv16t(fp a[16], int J)
{
    fp t;
    if (J) { t = TWI(J, 3, 0); GS(a[0], a[1], t); } else GS1(a[0], a[1]);
    t = TWI(J, 3, 1); GS(a[2], a[3], t);
    t = TWI(J, 3, 2); GS(a[4], a[5], t);
    t = TWI(J, 3, 3); GS(a[6], a[7], t);
    if (J) { t = TWI(J, 2, 0); GS(a[0], a[2], t); GS(a[1], a[3], t); } else { GS1(a[0], a[2]); GS1(a[1], a[3]); }
    t = TWI(J, 2, 1); GS(a[4], a[6], t); GS(a[5], a[7], t);
    if (J) { t = TWI(J, 1, 0); GS(a[0], a[4], t); GS(a[1], a[5], t); GS(a[2], a[6], t); GS(a[3], a[7], t); }
    else { GS1(a[0], a[4]); GS1(a[1], a[5]); GS1(a[2], a[6]); GS1(a[3], a[7]); }
    t = TWI(J, 3, 4); GS(a[8], a[9], t);
    t = TWI(J, 3, 5); GS(a[10], a[11], t);
    t = TWI(J, 2, 2); GS(a[8], a[10], t); GS(a[9], a[11], t);
    t = TWI(J, 3, 6); GS(a[12], a[13], t);
    LD(3);
    a[15] = fp_sub(a[11], fp_mul(TW[J][1][1], a[7]));
    a[15] = fp_sub(a[13], fp_mul(TW[J][2][3], a[15]));
    a[15] = fp_sub(a[14], fp_mul(TW[J][3][7], a[15]));
    t = TWI(J, 3, 7); GS(a[14], a[15], t);
    t = TWI(J, 2, 3); GS(a[12], a[14], t); GS(a[13], a[15], t);
    t = TWI(J, 1, 1); GS(a[8], a[12], t); GS(a[9], a[13], t); GS(a[10], a[14], t); GS(a[11], a[15], t);
    if (J) {
        t = TWI(J, 0, 0);
        GS(a[0], a[8], t); GS(a[1], a[9], t); GS(a[2], a[10], t); GS(a[3], a[11], t); GS(a[4], a[12], t); GS(a[5], a[13], t);
        GS(a[6], a[14], t);
    } else {
        GS1(a[0], a[8]); GS1(a[1], a[9]); GS1(a[2], a[10]); GS1(a[3], a[11]); GS1(a[4], a[12]); GS1(a[5], a[13]); GS1(a[6], a[14]);
    }
    a[7] = fp_add(a[7], a[15]);
}

/** Forward top 4 layers of subtree J with coefficient block 15 zero; leaf 15 is not formed. */
static inline void fwd16t(fp a[16], int J)
{
    fp t;
    if (J) {
        t = TWF(J, 0, 0);
        CT(a[0], a[8], t); CT(a[1], a[9], t); CT(a[2], a[10], t); CT(a[3], a[11], t); CT(a[4], a[12], t); CT(a[5], a[13], t);
        CT(a[6], a[14], t);
    } else {
        CT1(a[0], a[8]); CT1(a[1], a[9]); CT1(a[2], a[10]); CT1(a[3], a[11]); CT1(a[4], a[12]); CT1(a[5], a[13]); CT1(a[6], a[14]);
    }
    a[15] = a[7];
    if (J) { t = TWF(J, 1, 0); CT(a[0], a[4], t); CT(a[1], a[5], t); CT(a[2], a[6], t); CT(a[3], a[7], t); }
    else { CT1(a[0], a[4]); CT1(a[1], a[5]); CT1(a[2], a[6]); CT1(a[3], a[7]); }
    t = TWF(J, 1, 1); CT(a[8], a[12], t); CT(a[9], a[13], t); CT(a[10], a[14], t); CT(a[11], a[15], t);
    if (J) { t = TWF(J, 2, 0); CT(a[0], a[2], t); CT(a[1], a[3], t); } else { CT1(a[0], a[2]); CT1(a[1], a[3]); }
    t = TWF(J, 2, 1); CT(a[4], a[6], t); CT(a[5], a[7], t);
    t = TWF(J, 2, 2); CT(a[8], a[10], t); CT(a[9], a[11], t);
    t = TWF(J, 2, 3); CT(a[12], a[14], t); CT(a[13], a[15], t);
    if (J) { t = TWF(J, 3, 0); CT(a[0], a[1], t); } else CT1(a[0], a[1]);
    t = TWF(J, 3, 1); CT(a[2], a[3], t);
    t = TWF(J, 3, 2); CT(a[4], a[5], t);
    t = TWF(J, 3, 3); CT(a[6], a[7], t);
    t = TWF(J, 3, 4); CT(a[8], a[9], t);
    t = TWF(J, 3, 5); CT(a[10], a[11], t);
    t = TWF(J, 3, 6); CT(a[12], a[13], t);
    t = TWF(J, 3, 7); a[14] = fp_add(a[14], fp_mul(a[15], t));
}

#define TOP_LD(k) a[k] = x[o + (k) * q];
#define TOP_ST(k) x[o + (k) * q] = a[k];
#define R15(M) M(0) M(1) M(2) M(3) M(4) M(5) M(6) M(7) M(8) M(9) M(10) M(11) M(12) M(13) M(14)

/** Truncated top pass over the 15 slot blocks of 2^(L-4) words (jin, jout constants): the inverse top of subtree jin (if >= 0),
 *  then the forward top of subtree jout (if >= 0), fused per offset. */
static inline void tr_top_k(fp *x, int L, int jin, int jout)
{
    size_t q = (size_t)1 << (L - 4);
    CTL(2);
    for (size_t o = 0; o < q; o++) {
        fp a[16];
        CTL(1);
        R15(TOP_LD)
        LD(15);
        a[15] = FP_ZERO;
        if (jin >= 0) inv16t(a, jin);
        if (jout >= 0) fwd16t(a, jout);
        R15(TOP_ST)
        ST(15);
    }
    LOOPC(q);
}

/** The variant (jin, jout) of the truncated top is selected once per pass. */
void tr_top(fp *x, int L, int jin, int jout)
{
    CTL(6);
    if (jin == 0 && jout == 1) tr_top_k(x, L, 0, 1);
    else if (jin == 1 && jout == 0) tr_top_k(x, L, 1, 0);
    else if (jin < 0) { if (jout) tr_top_k(x, L, -1, 1); else tr_top_k(x, L, -1, 0); }
    else { if (jin) tr_top_k(x, L, 1, -1); else tr_top_k(x, L, 0, -1); }
}

/** Truncated forward transform: coefficients (degree < n') in natural order to the values on O(L, J0). */
void tr_fwd(fp *x, int L, int J0)
{
    tr_top(x, L, -1, J0);
    tr_range(x, L, J0, 4, L, 0);
}

/** Truncated inverse transform: the values on O(L, J0) of a polynomial of degree < n' to 2^L times its coefficients. */
void tr_inv(fp *x, int L, int J0)
{
    tr_range(x, L, J0, 4, L, 1);
    tr_top(x, L, J0, -1);
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

SHA-256 `bb3585527b0655ff368f9e3fd0f2dccc2e8ef29cecbfbeab37a57bafb881cb60`, 218 bytes.

```c
#ifndef STAGEB_H
#define STAGEB_H
#include "fp.h"
void stage_b(fp c, int L, fp *V);
int stage_prep(int L, size_t m, int t, fp *B0, fp *B1, fp *B2, fp *B3, fp *DL);
void blk_scale(fp *T, int L, int J0, int inv);
#endif
```

### stageb.c

SHA-256 `65641c437a7a19516f3c9a488afa5b7debd56b0b33dbfc0d0f35bbc51eb9dd4e`, 7720 bytes.

```c
/* Stage B (the line polynomial g_c by evaluation on the truncated set O1) and the preparation of stage C (start residue, Gi, G2,
 * the node factors delta_j).
 *
 * n = 2^L, n' = 15 n / 16 > m.  zeta is a primitive 2^(L+1)-th root of unity, so S_i = zeta^(2i) runs over H_L, and
 * F(c + s) - F(c - s) = 2 s g_c(s^2) gives the values gt(S_i) = (F(c + zeta^i) - F(c - zeta^i)) zeta^-i of gt = 2 g_c.  The value at
 * S_i is stored at position brv_L(i), the output order of the forward transforms; the points with i = 15 mod 16 form the absent
 * depth-4 node 15 (positions >= n') and are not evaluated. */
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

/** Fill V (n' words) with the values of gt = 2 g_c on O1 in transform order. */
void stage_b(fp c, int L, fp *V)
{
    size_t nh = (size_t)1 << (L - 4);
    const fp psi = {PSI_LIMBS}, ipsi = {PSI_INV_LIMBS};
    fp z = psi_pow2(psi, TREE_K - 1 - L), iz = psi_pow2(ipsi, TREE_K - 1 - L);
    fp s = FP_ONE, is = FP_ONE;
    uint32_t j = 0;
    for (size_t ih = 0; ih < nh; ih++) {
        for (int il = 0; il < 15; il++) {
            fp d = fp_sub(line_eval(fp_add(c, s)), line_eval(fp_sub(c, s)));
            V[j] = fp_mul(d, is);
            ST(1);
            s = fp_mul(s, z);
            is = fp_mul(is, iz);
            j = brv_next(j, L);
        }
        LOOPC(15);
        /* i = 16 ih + 15 lies in the absent node: only the running values advance */
        s = fp_mul(s, z);
        is = fp_mul(is, iz);
        j = brv_next(j, L);
    }
    LOOPC(nh);
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

/** Multiply every bottom block (8 words, a depth-(L-3) node X^8 - c) of the table T on O(L, J0) by c (inv = 0) or 1/c (inv = 1).
 *  Blocks in the order of u = 16 uh + ul with G = brv(u) as in the bottom passes; c = psi^((2u + J0) 2^(K-L+2)) advances by one
 *  multiplication per block (two across the absent node's block). */
void blk_scale(fp *T, int L, int J0, int inv)
{
    size_t nh = (size_t)1 << (L - 7);
    uint32_t e0 = (uint32_t)J0 << (TREE_K - L + 2), es = 1u << (TREE_K - L + 3);
    fp c = inv ? twiddle_inv(e0) : twiddle(e0), step = inv ? twiddle_inv(es) : twiddle(es);
    uint32_t gh = 0;
    CTL(10);
    for (size_t uh = 0; uh < nh; uh++) {
        for (int ul = 0; ul < 15; ul++) {
            fp *x = T + 8 * ((size_t)BRV4[ul] * nh + gh);
            CTL(5);
            for (int q = 0; q < 8; q++) x[q] = fp_mul(x[q], c);
            LD(8);
            ST(8);
            LOOPC(8);
            c = fp_mul(c, step);
        }
        LOOPC(15);
        c = fp_mul(c, step);
        gh = brv_next(gh, L - 7);
    }
    LOOPC(nh);
}

/** Prepare stage C from V = gt(O1) (transform order).  Four n'-word buffers: on entry B0 = V; on success B0 = Gi =
 *  -1/(n^3 g'(O1)) / c and B1 = G2 = c g'(O2) per block for g' = n gt, B3 = W = the coefficients of the start residue
 *  A0 = X^v P1 mod g' (v = 2^t, degree < m), B2 scratch, and DL[j] = delta_j (j < 15).  Requires m < n' and, with
 *  k = n' + v - m and P2 = 2^ceil(log2(k + 1)), n/2 + P2 <= n' and 2 P2 <= n' (the Newton buffers).  Returns 0, or -1 if
 *  deg gt != m or gt vanishes on O1. */
int stage_prep(int L, size_t m, int t, fp *B0, fp *B1, fp *B2, fp *B3, fp *DL)
{
    size_t n = (size_t)1 << L, w = n >> 4, nn = 15 * w, v = (size_t)1 << t, k = nn + v - m;
    for (size_t i = 0; i < nn; i++) B1[i] = B0[i];
    LD(nn);
    ST(nn);
    LOOPC(nn);
    tr_inv(B1, L, 0);
    for (size_t i = m + 1; i < nn; i++)
        if (!fp_is0(B1[i])) return -1;
    LD(nn - m - 1);
    LOOPC(nn - m - 1);
    LD(1);
    if (fp_is0(B1[m])) return -1;

    /* G* = B1 = n gt.  q = floor(X^v P1 / G*) has degree k; with f = rev_m(G*) and, for w = n/16, P1 = sum_(s < 16)
     * c1^(15-s) X^(s w), rev(X^v P1) = sum_(s < 16) c1^s X^(s w), so rev_k(q) = (1/f) / (1 - c1 X^w) mod X^(k+1) (k < 16 w).
     * f = B2[0..k], h = B2[n/2..], Newton scratch B3. */
    fp *f = B2, *h = B2 + n / 2;
    for (size_t i = 0; i <= k; i++) f[i] = B1[m - i];
    CTL(k + 1);
    LD(k + 1);
    ST(k + 1);
    LOOPC(k + 1);
    series_inv(h, f, k + 1, B3);
    fp c1 = twiddle(15u << (TREE_K - 4));
    for (size_t i = w; i <= k; i++) h[i] = fp_add(h[i], fp_mul(c1, h[i - w]));
    LD(2 * (k + 1 - w));
    ST(k + 1 - w);
    LOOPC(k + 1 - w);
    CTL(k + 1 - w);

    /* X^v P1 vanishes on O1, so A0 = X^v P1 - q G* takes the values -q G* = -n q V there; deg A0 < m < n', so the truncated
     * inverse of -q V returns A0 exactly. */
    for (size_t i = 0; i < nn; i++) B3[i] = i <= k ? h[k - i] : FP_ZERO;
    CTL(k + 1);
    LD(k + 1);
    ST(nn);
    LOOPC(nn);
    CTL(nn);
    tr_fwd(B3, L, 0);
    for (size_t i = 0; i < nn; i++) B3[i] = fp_neg(fp_mul(B3[i], B0[i]));
    LD(2 * nn);
    ST(nn);
    LOOPC(nn);
    tr_inv(B3, L, 0);

    tr_fwd(B1, L, 1);

    /* Gi = -1/(n^4 gt(O1)) by batch inversion with prefix products in B2. */
    fp acc = FP_ONE;
    for (size_t i = 0; i < nn; i++) {
        LD(1);
        if (fp_is0(B0[i])) return -1;
        acc = fp_mul(acc, B0[i]);
        B2[i] = acc;
        ST(1);
    }
    LOOPC(nn);
    fp n4 = fp_sqr(fp_sqr(fp_from_u64(n)));
    fp inv = fp_neg(fp_inv(fp_mul(acc, n4)));
    for (size_t i = nn; i-- > 1;) {
        fp vi = B0[i];
        LD(2);
        B0[i] = fp_mul(inv, B2[i - 1]);
        ST(1);
        inv = fp_mul(inv, vi);
        CTL(1);
    }
    LOOPC(nn - 1);
    B0[0] = inv;
    ST(1);
    blk_scale(B0, L, 0, 1);
    blk_scale(B1, L, 1, 0);

    /* delta_j = r_j - c1, r_j = psi^(brv_4(j) 2^(K-4) + 2^(K-5)) the root of node j of the coset */
    for (int j = 0; j < 15; j++) {
        DL[j] = fp_sub(twiddle(((uint32_t)BRV4[j] << (TREE_K - 4)) + (1u << (TREE_K - 5))), c1);
        ST(1);
        CTL(4);
    }
    LOOPC(15);
    return 0;
}
```

### stagec.h

SHA-256 `f77a5c5400fd3ff10d4dfcc7a00d6725e7cb0685d09329cdf199f5d608450a3c`, 178 bytes.

```c
#ifndef STAGEC_H
#define STAGEC_H
#include "fp.h"
void stage_c(fp *W, fp *A2, const fp *Gi, const fp *G2, const fp *DL, int L, const uint8_t *bits, int nbits, fp *kappa);
#endif
```

### stagec.c

SHA-256 `b17ef09c017727b19d5f1292586955e2c8a062b8a1ebcf0b5e1462004e299273`, 12176 bytes.

```c
/* Stage C: R = S^E mod g by Montgomery squarings in the value domain of two truncated point sets.
 *
 * n = 2^L, n' = 15 n / 16.  O1 = the depth-4 nodes 0..14 of H_L, the roots of P1 = (X^n - 1) / (X^(n/16) - c1) (c1 the root of the
 * absent node 15, deg P1 = n'); O2 = the same nodes of the coset of H_L, where X^n = -1 and P1 = -2 / delta_j on node j,
 * delta_j = r_j - c1 (r_j the node's root; the table DL).  A residue A (deg < n') is held as mu A on O1 and lambda A on O2
 * (mu = n lambda); the O1 values are never stored: the work buffer W holds the O1 transform up to its last pass.  One step maps A to
 * Mont(A, A) = A^2 / P1 mod g (degree < n'):
 *   U  = (mu A)^2 Gi on O1                    Gi = -1 / (n^3 g)        (u = -A^2/g mod P1, scaled)
 *   U  -> O2: inverse transform on O1, forward transform on O2
 *   B2 = ((lambda A)^2 + U G2) delta_j on O2  G2 = g;  B2 = -2 lambda^2 Mont(A, A)
 *   (times x on O2 when the exponent bit is 1), stored as the new O2 values (lambda' = -2 lambda^2)
 *   B2 -> O1: inverse transform on O2, forward transform on O1 (mu' = n lambda').
 * Passes: bottom (depths L-3..L-1) fused forward + pointwise + inverse; middle (depths 4..L-4, tr_range); top (depths 0..3, tr_top)
 * fused inverse of one set + forward of the other.
 *
 * Bottom blocks (depth L-3 nodes X^8 - c) are visited in bit-reversed order with a running block twiddle.  One twiddle set serves
 * both directions: with V = (x_k^l) for the roots x_k of X^8 - c, V^T V = 8 diag(1, c J) (J reverses l -> 8 - l on l = 1..7), so
 * V^-1 = (1/8) diag(1, c^-1 J) V^T = (1/(8c)) diag(c, J) V^T.  On O1 the inverse is therefore the forward network transposed
 * (reversed layers, GS butterflies with the forward twiddles), slot 0 times c, stored in the order 0, 7, 6, ..., 1, with the
 * factor 1/c folded into Gi; on O2 the forward is the inverse network transposed (load in that order, slot 0 times 1/c), with c
 * folded into G2.  Register file in the bottom passes: 8 data words, 7 twiddles, the running base and two temporaries;
 * the step constant is loaded per block. */
#include "ntt.h"
#include "stagec.h"

#define CT(a, b, w)  do { fp t_ = fp_mul(b, w); b = fp_sub(a, t_); a = fp_add(a, t_); } while (0)
#define CT1(a, b)    do { fp t_ = b; b = fp_sub(a, t_); a = fp_add(a, t_); } while (0)
#define GS(a, b, w)  do { fp t_ = fp_sub(a, b); a = fp_add(a, b); b = fp_mul(t_, w); } while (0)
#define GS1(a, b)    do { fp t_ = fp_sub(a, b); a = fp_add(a, b); b = t_; } while (0)
/* Straight-line repetition with constant indices (no loop, no loop control): the 8 words of a block stay in registers. */
#define R4(S) do { S(0); S(1); S(2); S(3); } while (0)
#define R8(S) do { S(0); S(1); S(2); S(3); S(4); S(5); S(6); S(7); } while (0)

enum { M_SQ1, M_EXIT1, M_B2, M_B2X, M_EXIT2 };

/** Seven block twiddles from the running depth-(L-1) base b (forward constants if inv = 0). */
static inline void blk_tw(fp b, int inv, fp w[7])
{
    fp b1 = fp_sqr(b);
    w[0] = fp_sqr(b1);
    w[1] = b1;
    w[2] = fp_mul(b1, inv ? C_IPSI2 : C_PSI2);
    w[3] = b;
    w[4] = fp_mul(b, inv ? C_IPSI2 : C_PSI2);
    w[5] = fp_mul(b, inv ? C_IPSI3 : C_PSI3);
    w[6] = fp_mul(b, inv ? C_IPSI33 : C_PSI33);
    LD(3);
}

/** One O1 block (8 words at x, table y): forward depths L-3..L-1, U = v^2 y (M_SQ1) or v y (M_EXIT1), the transposed forward
 *  network, slot 0 times c = w0^2, the permuted store.  triv: the first block of H_L (node twiddles 1, c = 1). */
static inline void blk1(fp *x, const fp *y, fp b, int triv, int mode)
{
    fp w[7];
    blk_tw(b, 0, w);
    fp a0 = x[0], a1 = x[1], a2 = x[2], a3 = x[3], a4 = x[4], a5 = x[5], a6 = x[6], a7 = x[7];
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
    if (mode == M_SQ1) {
        a0 = fp_mul(fp_sqr(a0), y[0]); a1 = fp_mul(fp_sqr(a1), y[1]); a2 = fp_mul(fp_sqr(a2), y[2]);
        a3 = fp_mul(fp_sqr(a3), y[3]); a4 = fp_mul(fp_sqr(a4), y[4]); a5 = fp_mul(fp_sqr(a5), y[5]);
        a6 = fp_mul(fp_sqr(a6), y[6]); a7 = fp_mul(fp_sqr(a7), y[7]);
    } else {
        a0 = fp_mul(a0, y[0]); a1 = fp_mul(a1, y[1]); a2 = fp_mul(a2, y[2]); a3 = fp_mul(a3, y[3]);
        a4 = fp_mul(a4, y[4]); a5 = fp_mul(a5, y[5]); a6 = fp_mul(a6, y[6]); a7 = fp_mul(a7, y[7]);
    }
    LD(8);
    if (triv) {
        GS1(a0, a1); GS(a2, a3, w[4]); GS(a4, a5, w[5]); GS(a6, a7, w[6]);
        GS1(a0, a2); GS1(a1, a3); GS(a4, a6, w[2]); GS(a5, a7, w[2]);
        GS1(a0, a4); GS1(a1, a5); GS1(a2, a6); GS1(a3, a7);
    } else {
        GS(a0, a1, w[3]); GS(a2, a3, w[4]); GS(a4, a5, w[5]); GS(a6, a7, w[6]);
        GS(a0, a2, w[1]); GS(a1, a3, w[1]); GS(a4, a6, w[2]); GS(a5, a7, w[2]);
        GS(a0, a4, w[0]); GS(a1, a5, w[0]); GS(a2, a6, w[0]); GS(a3, a7, w[0]);
        a0 = fp_mul(a0, fp_sqr(w[0]));
    }
    x[0] = a0; x[1] = a7; x[2] = a6; x[3] = a5; x[4] = a4; x[5] = a3; x[6] = a2; x[7] = a1;
    ST(8);
}

/** O1 bottom pass (Y = Gi / c per block, mode constant); blocks in the order of u = 16 uh + ul, G = brv(u), the absent node's
 *  blocks skipped. */
static inline void bottom1_k(fp *W, const fp *Y, int L, int mode)
{
    size_t nh = (size_t)1 << (L - 7);
    fp step = twiddle(1u << (TREE_K - L)), b = FP_ONE;
    uint32_t gh = 0;
    CTL(8);
    for (size_t uh = 0; uh < nh; uh++) {
        int ul0 = uh == 0;
        CTL(2);
        if (ul0) {
            CTL(1);
            blk1(W, Y, b, 1, mode);
            b = fp_mul(b, step);
            LD(1);
        }
        for (int ul = ul0; ul < 15; ul++) {
            size_t G = (size_t)BRV4[ul] * nh + gh;
            CTL(6); /* G (table load, multiply, add), 8 G, W + 8 G, Y + 8 G */
            blk1(W + 8 * G, Y + 8 * G, b, 0, mode);
            b = fp_mul(b, step);
            LD(1);
        }
        LOOPC(15 - ul0);
        b = fp_mul(b, step);
        LD(1);
        gh = brv_next(gh, L - 7);
    }
    LOOPC(nh);
}

/** The mode of a bottom pass is selected once per pass. */
static void bottom1(fp *W, const fp *Y, int L, int mode)
{
    CTL(2);
    if (mode == M_SQ1) bottom1_k(W, Y, L, M_SQ1);
    else bottom1_k(W, Y, L, M_EXIT1);
}

/** O2 bottom pass (Y = c G2 per block, mode constant): permuted load with slot 0 times 1/c, the forward-structure network with the
 *  inverse twiddles (gives v / c), the pointwise map times delta_j (M_B2: B2 = A2^2 + (v/c) Y; M_B2X: the same times x; both stored
 *  to A2; M_EXIT2: A2 inn + (v/c) Y), the inverse network, the natural store. */
static inline void bottom2_k(fp *W, fp *A2, const fp *Y, const fp *DL, int L, int mode, fp inn)
{
    size_t nh = (size_t)1 << (L - 7);
    fp step = twiddle_inv(1u << (TREE_K - L)), b = twiddle_inv(1u << (TREE_K - L - 1));
    fp fstep = FP_ONE, fb = FP_ONE;
    uint32_t gh = 0;
    CTL(8);
    if (mode == M_B2X) {
        fstep = twiddle(1u << (TREE_K - L));
        fb = twiddle(1u << (TREE_K - L - 1));
    }
    for (size_t uh = 0; uh < nh; uh++) {
        for (int ul = 0; ul < 15; ul++) {
            size_t G = (size_t)BRV4[ul] * nh + gh;
            fp *x = W + 8 * G, *z = A2 + 8 * G;
            const fp *y = Y + 8 * G;
            fp iw[7];
            CTL(7); /* G (table load, multiply, add), 8 G and the three block pointers */
            blk_tw(b, 1, iw);
            fp a0 = fp_mul(x[0], fp_sqr(iw[0])), a7 = x[1], a6 = x[2], a5 = x[3], a4 = x[4], a3 = x[5], a2 = x[6], a1 = x[7];
            LD(8);
            CT(a0, a4, iw[0]); CT(a1, a5, iw[0]); CT(a2, a6, iw[0]); CT(a3, a7, iw[0]);
            CT(a0, a2, iw[1]); CT(a1, a3, iw[1]); CT(a4, a6, iw[2]); CT(a5, a7, iw[2]);
            CT(a0, a1, iw[3]); CT(a2, a3, iw[4]); CT(a4, a5, iw[5]); CT(a6, a7, iw[6]);
            fp v[8] = {a0, a1, a2, a3, a4, a5, a6, a7};
            if (mode == M_EXIT2) {
#define P_E2(q) v[q] = fp_add(fp_mul(z[q], inn), fp_mul(v[q], y[q]))
                R8(P_E2);
            } else {
#define P_B2(q) v[q] = fp_add(fp_sqr(z[q]), fp_mul(v[q], y[q]))
                R8(P_B2);
            }
            LD(16);
            /* delta_j of the block's depth-4 node; iw[0] is dropped for it and recomputed (register file) */
            fp d = DL[BRV4[ul]];
            LD(1);
#define P_D(q) v[q] = fp_mul(v[q], d)
            R8(P_D);
            iw[0] = fp_sqr(iw[1]);
            if (mode == M_B2X) {
                /* leaf roots x_(2r) = w[3+r], x_(2r+1) = -w[3+r] (forward twiddles from the running forward base, formed one at
                 * a time, with one spill and reload of the running base) */
                fp xw[4];
                xw[0] = fb;
                xw[1] = fp_mul(fb, C_PSI2);
                xw[2] = fp_mul(fb, C_PSI3);
                xw[3] = fp_mul(fb, C_PSI33);
                LD(3);
                LD(1);
                ST(1);
#define P_X(r) v[2 * (r)] = fp_mul(v[2 * (r)], xw[r]); v[2 * (r) + 1] = fp_neg(fp_mul(v[2 * (r) + 1], xw[r]))
                R4(P_X);
                fb = fp_mul(fb, fstep);
                LD(1);
            }
            if (mode != M_EXIT2) {
#define P_ST(q) z[q] = v[q]
                R8(P_ST);
                ST(8);
            }
            a0 = v[0]; a1 = v[1]; a2 = v[2]; a3 = v[3]; a4 = v[4]; a5 = v[5]; a6 = v[6]; a7 = v[7];
            GS(a0, a1, iw[3]); GS(a2, a3, iw[4]); GS(a4, a5, iw[5]); GS(a6, a7, iw[6]);
            GS(a0, a2, iw[1]); GS(a1, a3, iw[1]); GS(a4, a6, iw[2]); GS(a5, a7, iw[2]);
            GS(a0, a4, iw[0]); GS(a1, a5, iw[0]); GS(a2, a6, iw[0]); GS(a3, a7, iw[0]);
            x[0] = a0; x[1] = a1; x[2] = a2; x[3] = a3; x[4] = a4; x[5] = a5; x[6] = a6; x[7] = a7;
            ST(8);
            b = fp_mul(b, step);
            LD(1);
        }
        LOOPC(15);
        b = fp_mul(b, step);
        LD(1);
        if (mode == M_B2X) {
            fb = fp_mul(fb, fstep);
            LD(1);
        }
        gh = brv_next(gh, L - 7);
    }
    LOOPC(nh);
}

static void bottom2(fp *W, fp *A2, const fp *Y, const fp *DL, int L, int mode, fp inn)
{
    CTL(3);
    if (mode == M_B2) bottom2_k(W, A2, Y, DL, L, M_B2, inn);
    else if (mode == M_B2X) bottom2_k(W, A2, Y, DL, L, M_B2X, inn);
    else bottom2_k(W, A2, Y, DL, L, M_EXIT2, inn);
}

/** Run stage C.  On entry W holds the coefficients (natural order, degree < n') of the start residue A0 in Montgomery form
 *  (A0 = S^v P1 mod g), A2 is scratch, Gi and G2 the tables (Gi = -1/(n^3 g(O1)) / c, G2 = c g(O2) per block, transform order) and
 *  DL[j] = delta_j.  Squarings follow bits[0..nbits-1] (most significant first; bit 1 multiplies by x after the squaring).  On exit
 *  W holds the coefficients of kappa R, R = S^(v 2^nbits + bits) mod g of degree < deg g, and *kappa is returned. */
void stage_c(fp *W, fp *A2, const fp *Gi, const fp *G2, const fp *DL, int L, const uint8_t *bits, int nbits, fp *kappa)
{
    size_t n = (size_t)1 << L, nn = 15 * (n >> 4);
    fp inn = fp_inv(fp_from_u64(n));
    for (size_t i = 0; i < nn; i++) A2[i] = fp_mul(W[i], inn);
    LD(nn);
    ST(nn);
    LOOPC(nn);
    tr_fwd(A2, L, 1);
    tr_top(W, L, -1, 0);
    tr_range(W, L, 0, 4, L - 3, 0);
    fp lam = inn;
    for (int s = 0; s < nbits; s++) {
        bottom1(W, Gi, L, M_SQ1);
        tr_range(W, L, 0, 4, L - 3, 1);
        tr_top(W, L, 0, 1);
        tr_range(W, L, 1, 4, L - 3, 0);
        CTL(2);
        bottom2(W, A2, G2, DL, L, bits[s] ? M_B2X : M_B2, inn);
        tr_range(W, L, 1, 4, L - 3, 1);
        tr_top(W, L, 1, 0);
        tr_range(W, L, 0, 4, L - 3, 0);
        lam = fp_sqr(lam);
        lam = fp_neg(fp_add(lam, lam));
        LOOPC(1);
        CTL(2);
    }
    bottom1(W, Gi, L, M_EXIT1);
    tr_range(W, L, 0, 4, L - 3, 1);
    tr_top(W, L, 0, 1);
    tr_range(W, L, 1, 4, L - 3, 0);
    bottom2(W, A2, G2, DL, L, M_EXIT2, inn);
    tr_range(W, L, 1, 4, L - 3, 1);
    tr_top(W, L, 1, -1);
    *kappa = fp_neg(fp_add(lam, lam));
}
```

### hgcd.h

SHA-256 `6e68d89bc766e566495e1db534f7a73ea9fe94384e28ff867e2d4853d2b4b31a`, 261 bytes.

```c
#ifndef HGCD_H
#define HGCD_H
#include "fp.h"
typedef struct { fp *e[4]; long d[4]; } mat;
extern size_t hg_peak;
extern uint64_t hg_prof[4];
void hg_arena(fp *base, size_t cap);
long hg_gcd(fp *a, long da, fp *b, long db, long kmax, long bcap, fp **g);
#endif
```

### hgcd.c

SHA-256 `d3d74a9aa9800feb57e149d13fb71ac445225eb882da6d125940e83c1a856d7c`, 48716 bytes.

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
    CTL(2);
    if (dx + 1 <= rs) {
        ntt_fwd_bz(T, x, dx + 1, lr, B);
        return;
    }
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

/** cr, dr (rs words each) times 2^lg. */
static void scale_rows(fp *cr, fp *dr, long rs, int lg)
{
    fp sc = fp_from_u64((uint64_t)1 << lg);
    for (long i = 0; i < rs; i++) {
        cr[i] = fp_mul(sc, cr[i]);
        dr[i] = fp_mul(sc, dr[i]);
    }
    LD(2 * rs);
    ST(2 * rs);
    LOOPC(rs);
}

/** M's entries hold values on H of size 2^lm (from mat_mul_f without the inverse): make them coefficients (times 2^lm). */
static void mat_vals_to_coeffs(mat *M, int lm)
{
    for (int i = 0; i < 4; i++) {
        ntt_inv(M->e[i], lm, 0);
        M->d[i] = pdeg(M->e[i], 1L << lm);
    }
    LOOPC(4);
}

/** (c, d) = adj(M) (a, b) mod X^N - 1 (N = 2^l), times N: c = r22 a - r12 b, d = r11 b - r21 a.  a, b of lengths la, lb
 *  (folded mod X^N - 1); c, d are N-word buffers (c may equal a and d equal b when la, lb <= N, in place).  The entries are
 *  transformed per row of 2^(l-e) points; scratch 2 * 2^(l-e) words. */
static void apply_adj(mat *M, const fp *a, long la, const fp *b, long lb, fp *c, fp *d, int l, int e, int mv, int lmv)
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
    fp *S4 = aalloc(4 * rs);
    for (uint32_t rho = 0; rho < (1u << e); rho++) {
        uint32_t B;
        fp w = row_root(l, e, rho, &B);
        int w1 = rho == 0;
        fp *cr = c + rho * rs, *dr = d + rho * rs;
        const fp *T0 = S4, *T1 = S4 + rs, *T2 = S4 + 2 * rs, *T3 = S4 + 3 * rs;
        CTL(7);
        if ((long)rho < mv) {
            /* rows rho < mv are the leaves of H of size 2^lmv: M holds exactly these values */
            T0 = M->e[0] + rho * rs;
            T1 = M->e[1] + rho * rs;
            T2 = M->e[2] + rho * rs;
            T3 = M->e[3] + rho * rs;
            CTL(5);
        } else {
            for (int i = 0; i < 4; i++) {
                fp *dst = S4 + i * rs;
                if (M->d[i] >= 0) row_entry(dst, M->e[i], M->d[i], rs, lr, B, w, w1);
                else {
                    for (long j = 0; j < rs; j++) dst[j] = FP_ZERO;
                    ST(rs);
                    LOOPC(rs);
                }
                CTL(4);
            }
            LOOPC(4);
        }
        for (long i = 0; i < rs; i++) {
            fp c0 = cr[i], d0 = dr[i];
            cr[i] = fp_sub(fp_mul(T3[i], c0), fp_mul(T1[i], d0));
            dr[i] = fp_sub(fp_mul(T0[i], d0), fp_mul(T2[i], c0));
        }
        LD(6 * rs);
        ST(2 * rs);
        LOOPC(rs);
        if ((long)rho < mv) {
            /* M's values v invert to coefficients whose values are 2^lmv v: scale these rows to match */
            scale_rows(cr, dr, rs, lmv);
            if ((long)rho == mv - 1) mat_vals_to_coeffs(M, lmv);
            CTL(2);
        }
        CTL(2);
    }
    LOOPC(1u << e);
    arel(mk);
    ntt_inv(c, l, 0);
    ntt_inv(d, l, 0);
}

/** One position i of split3: (R0, R1, R2)[i] from the four block coefficients. */
static inline void split3_at(fp *dst, long i, long rs, fp a0, fp a1, fp a2, fp a3, fp ii)
{
    fp s0 = fp_add(a0, a2), s1 = fp_add(a1, a3), d0 = fp_sub(a0, a2), d1 = fp_sub(a1, a3);
    dst[i] = fp_add(s0, s1);
    dst[rs + i] = fp_sub(s0, s1);
    dst[2 * rs + i] = fp_add(d0, fp_mul(ii, d1));
}

/** dst blocks 0, 1, 2 (rs words each) = src mod (Y - 1), (Y + 1), (Y - i) for Y = X^rs, src of length len <= 4 rs:
 *  with src = A0 + A1 Y + A2 Y^2 + A3 Y^3, R0 = (A0 + A2) + (A1 + A3), R1 = (A0 + A2) - (A1 + A3),
 *  R2 = (A0 - A2) + i (A1 - A3).  Works in place (dst == src).  Two loops: positions with all four blocks present, then the
 *  others (bound tests). */
static void split3(fp *dst, const fp *src, long len, long rs, fp ii)
{
    long ifull = len - 3 * rs;
    if (ifull < 0) ifull = 0;
    if (ifull > rs) ifull = rs;
    CTL(5);
    for (long i = 0; i < ifull; i++) split3_at(dst, i, rs, src[i], src[rs + i], src[2 * rs + i], src[3 * rs + i], ii);
    LOOPC(ifull);
    for (long i = ifull; i < rs; i++) {
        fp a0 = i < len ? src[i] : FP_ZERO, a1 = rs + i < len ? src[rs + i] : FP_ZERO;
        fp a2 = 2 * rs + i < len ? src[2 * rs + i] : FP_ZERO, a3 = 3 * rs + i < len ? src[3 * rs + i] : FP_ZERO;
        CTL(8);
        split3_at(dst, i, rs, a0, a1, a2, a3, ii);
    }
    LOOPC(rs - ifull);
    LD(len < 4 * rs ? len : 4 * rs);
    ST(3 * rs);
}

/** The same as apply_adj with N = 3 2^(l-2): rows 0, 1, 2 of the 4-row split of the size-2^l transform (moduli Y - 1,
 *  Y + 1, Y - i, Y = X^(2^(l-2))), then combined: for c = C0 + C1 Y + C2 Y^2 the row residues R0, R1, R2 give
 *  4 C0 = (R0 + R1) + 2 R2 - i (R0 - R1), 4 C1 = 2 (R0 - R1), 4 C2 = (R0 + R1) - 2 R2 + i (R0 - R1).  c, d hold
 *  3 2^(l-2) words (in place allowed if the buffers hold 2^l words); scratch 2 rows. */
static void apply_adj3(mat *M, const fp *a, long la, const fp *b, long lb, fp *c, fp *d, int l, fp *sav,
                       const fp *mval, long mvs, fp *scr, int mv, int lmv, int lsub)
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
    if (lsub <= 0 || lsub > lr || sav) lsub = lr;
    int f = lr - lsub;
    long rsub = 1L << lsub;
    CTL(5);
    /* entry transforms: rows 0 and 1 into SAV (row 2 first, through SAV's row-1 slots), else into scr (stride scs) */
    long scs = rsub;
    if (!sav && !scr) scr = aalloc(4 * rsub);
    else if (!sav) scs = mvs;
    CTL(4);
    for (uint32_t z = 0; z < 3; z++) {
        uint32_t rho = z == 0 ? 0 : (sav ? 3 - z : z);
        uint32_t B;
        fp w = row_root(l, 2, rho, &B);
        int w1 = rho == 0;
        fp *cr = c + rho * rs, *dr = d + rho * rs;
        CTL(7);
        ntt_fwd_b(cr, lr, B);
        ntt_fwd_b(dr, lr, B);
        /* the pointwise part runs over 2^f sub-rows of rsub points (f = 0 inside hgcd; the driver uses sub-rows of the
         *  size of H where M is known, so that the entries need no folding and the scratch is 4 rsub words) */
        for (long j = 0; j < (1L << f); j++) {
            long g = (long)rho * (1L << f) + j, off = j * rsub;
            uint32_t Bs = B;
            fp ws = w;
            int w1s = w1 && j == 0;
            CTL(6);
            if (f) ws = row_root(l, 2 + f, (uint32_t)g, &Bs);
            const fp *Te[4];
            int usev = rho == 0 && mval;
            const fp *mv0 = mval;
            long mvs0 = mvs;
            CTL(4);
            if (g < mv) {
                mv0 = M->e[0] + g * rsub;
                mvs0 = M->e[1] - M->e[0];
                usev = 1;
                CTL(4);
            }
            for (int i = 0; i < 4; i++) {
                fp *dst = sav ? sav + i * 2 * rs + (rho ? rs : 0) : scr + i * scs;
                CTL(6);
                if (usev) {
                    Te[i] = mv0 + i * mvs0;
                    CTL(2);
                } else {
                    Te[i] = dst;
                    if (M->d[i] >= 0) row_entry(dst, M->e[i], M->d[i], rsub, lsub, Bs, ws, w1s);
                    else {
                        for (long q = 0; q < rsub; q++) dst[q] = FP_ZERO;
                        ST(rsub);
                        LOOPC(rsub);
                    }
                }
            }
            LOOPC(4);
            fp *crs = cr + off, *drs = dr + off;
            /* (c, d) <- (r22 c - r12 d, r11 d - r21 c), one fused pass */
            for (long i = 0; i < rsub; i++) {
                fp c0 = crs[i], d0 = drs[i];
                crs[i] = fp_sub(fp_mul(Te[3][i], c0), fp_mul(Te[1][i], d0));
                drs[i] = fp_sub(fp_mul(Te[0][i], d0), fp_mul(Te[2][i], c0));
            }
            LD(6 * rsub);
            ST(2 * rsub);
            LOOPC(rsub);
            if (g < mv) {
                scale_rows(crs, drs, rsub, lmv);
                if (g == mv - 1) mat_vals_to_coeffs(M, lmv);
                CTL(2);
            }
        }
        LOOPC(1L << f);
        ntt_inv_b(cr, lr, B);
        ntt_inv_b(dr, lr, B);
        CTL(5);
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

/** The same as apply_adj when 2^l words exceed the buffers of a and b (l = L, the first product of the driver): the product is
 *  taken modulo P' = (X^(2^l) - 1) / (X^(2^(l-4)) - c1) of degree N' = 15 2^(l-4), i.e. on the depth-4 nodes 0..14 of H_l, as 15
 *  rows of 2^(l-4) points (row rho is node rho: offset brv_4(rho) 2^(K-l), modulus X^(2^(l-4)) - w_rho).  It is exact because the
 *  true c and d have degree < N'.  In place in a and b (N' words each, la, lb <= N'): the split into the rows and the recombination
 *  are the truncated top layers (tr_top of ntt.c, the forward with coefficient block 15 zero, the inverse recovering the absent
 *  row from it).  M holds coefficients.  Scratch 4 rows. */
static void apply_adj_tr(const mat *M, fp *a, long la, fp *b, long lb, int l)
{
    long rs = 1L << (l - 4), nn = 15 * rs;
    for (long i = la; i < nn; i++) a[i] = FP_ZERO;
    ST(nn - la);
    LOOPC(nn - la);
    for (long i = lb; i < nn; i++) b[i] = FP_ZERO;
    ST(nn - lb);
    LOOPC(nn - lb);
    tr_top(a, l, -1, 0);
    tr_top(b, l, -1, 0);
    size_t mk = amark();
    fp *S4 = aalloc(4 * rs);
    for (uint32_t rho = 0; rho < 15; rho++) {
        uint32_t B;
        fp w = row_root(l, 4, rho, &B);
        int w1 = rho == 0;
        fp *cr = a + rho * rs, *dr = b + rho * rs;
        CTL(4);
        ntt_fwd_b(cr, l - 4, B);
        ntt_fwd_b(dr, l - 4, B);
        for (int i = 0; i < 4; i++) {
            fp *dst = S4 + i * rs;
            if (M->d[i] >= 0) row_entry(dst, M->e[i], M->d[i], rs, l - 4, B, w, w1);
            else {
                for (long q = 0; q < rs; q++) dst[q] = FP_ZERO;
                ST(rs);
                LOOPC(rs);
            }
            CTL(4);
        }
        LOOPC(4);
        const fp *T0 = S4, *T1 = S4 + rs, *T2 = S4 + 2 * rs, *T3 = S4 + 3 * rs;
        for (long i = 0; i < rs; i++) {
            fp c0 = cr[i], d0 = dr[i];
            cr[i] = fp_sub(fp_mul(T3[i], c0), fp_mul(T1[i], d0));
            dr[i] = fp_sub(fp_mul(T0[i], d0), fp_mul(T2[i], c0));
        }
        LD(6 * rs);
        ST(2 * rs);
        LOOPC(rs);
        ntt_inv_b(cr, l - 4, B);
        ntt_inv_b(dr, l - 4, B);
    }
    LOOPC(15);
    arel(mk);
    tr_top(a, l, 0, -1);
    tr_top(b, l, 0, -1);
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

static fp *XT;   /* x at the points of H_s in transform output order (a prefix serves every s), XT_N words */
static long XT_N;

/** O = A B (see mat_mul_gen), e = 1, with every entry of A and Bm nonzero: one fused pass per row.  Asav: A's entries
 *  transformed (entry i at Asav + i N).  bval: if given, Bm = [[Q, 1], [bt, 0]] M2 and bval holds M2's values on row 0
 *  (entry i at bval + i rs), so B's row 0 is formed pointwise with Q = Qc[0] + Qc[1] x (t = 1).  oval: if given, the
 *  values of O on both rows (entry i at oval + i ovs) are also stored, scaled by N so that they are the values of the
 *  returned coefficients. */
static void mat_mul_f(mat *O, const mat *A, const mat *Bm, long k, const fp *Asav, const fp *bval, long bvs, const fp *Qc,
                      fp bt, fp *oval, long ovs, int noinv, int qraw)
{
    int l;
    long N = pow2l(k + 1, &l);
    int lr = l - 1;
    long rs = 1L << lr;
    size_t mk = amark();
    fp sc = FP_ONE;
    if (oval) sc = fp_from_u64((uint64_t)N);
    CTL(6);
    for (uint32_t rho = 0; rho < 2; rho++) {
        uint32_t B;
        fp w = row_root(l, 1, rho, &B);
        int w1 = rho == 0;
        long off = rho * rs;
        int bv = rho == 0 && bval;
        CTL(5);
        /* operand rows live in the output rows (each point is read before it is written) or in scratch */
        fp *TB[4];
        const fp *Ap[4];
        fp *scr = !Asav && rho == 1 ? aalloc(4 * rs) : NULL;
        CTL(2);
        for (int i = 0; i < 4; i++) {
            TB[i] = Asav ? O->e[i] + off : (rho == 0 ? O->e[i] + rs : scr + i * rs);
            if (Asav) Ap[i] = Asav + i * N + off;
            else {
                fp *ta = O->e[i] + off;
                row_entry(ta, A->e[i], A->d[i], rs, lr, B, w, w1);
                Ap[i] = ta;
            }
            if (!bv) row_entry(TB[i], Bm->e[i], Bm->d[i], rs, lr, B, w, w1);
            CTL(8);
        }
        LOOPC(4);
        fp *o[4];
        for (int i = 0; i < 4; i++) o[i] = O->e[i] + off;
        CTL(8);
        LOOPC(4);
        fp q0 = Qc ? Qc[0] : FP_ZERO, q1 = Qc ? Qc[1] : FP_ZERO;
        LD(2);
        /* B = [[Q, 1], [bt, 0]] M2 formed pointwise (x from XT: row 1 is the second half of H of size N) when bval
         *  holds M2's row-0 values, or on both rows when qraw (Bm = M2, not yet multiplied by Q) */
        int useq = Qc && (bv || qraw);
        if (useq && rho == 1) {
            /* row 1 (X^rs = -1) is zeta H_rs, zeta = w^1 of order 2 rs: x = zeta XT[p], folded into q1 */
            q1 = fp_mul(q1, twiddle(1u << (TREE_K - l)));
            CTL(2);
        }
        const fp *mb = bv ? bval : TB[0];
        long ms = bv ? bvs : TB[1] - TB[0]; /* uniform stride of the four B rows */
        CTL(6);
        for (long p = 0; p < rs; p++) {
            fp b0, b1, b2, b3;
            fp m0 = mb[p], m1 = mb[ms + p], m2 = mb[2 * ms + p], m3 = mb[3 * ms + p];
            LD(4);
            if (useq) {
                fp qx = fp_add(q0, fp_mul(q1, XT[p]));
                b0 = fp_add(fp_mul(qx, m0), m2);
                b1 = fp_add(fp_mul(qx, m1), m3);
                b2 = fp_mul(bt, m0);
                b3 = fp_mul(bt, m1);
                LD(1);
            } else {
                b0 = m0;
                b1 = m1;
                b2 = m2;
                b3 = m3;
            }
            fp a0 = Ap[0][p], a1 = Ap[1][p], a2 = Ap[2][p], a3 = Ap[3][p];
            fp r0 = fp_add(fp_mul(a0, b0), fp_mul(a1, b2)), r1 = fp_add(fp_mul(a0, b1), fp_mul(a1, b3));
            fp r2 = fp_add(fp_mul(a2, b0), fp_mul(a3, b2)), r3 = fp_add(fp_mul(a2, b1), fp_mul(a3, b3));
            o[0][p] = r0;
            o[1][p] = r1;
            o[2][p] = r2;
            o[3][p] = r3;
            LD(4);
            ST(4);
            if (oval) {
                fp s1 = sc;
                oval[off + p] = fp_mul(s1, r0);
                oval[ovs + off + p] = fp_mul(s1, r1);
                oval[2 * ovs + off + p] = fp_mul(s1, r2);
                oval[3 * ovs + off + p] = fp_mul(s1, r3);
                ST(4);
                CTL(1);
            }
        }
        LOOPC(rs);
        if (scr) arel(mk);
    }
    LOOPC(2);
    arel(mk);
    CTL(1);
    if (noinv) {
        /* values kept; deg r11 = deg A11 + deg B11 (the sum of the quotient degrees), the others bounded by N - 1 */
        O->d[0] = A->d[0] + Bm->d[0] + (qraw ? 1 : 0);
        O->d[1] = O->d[2] = O->d[3] = N - 1;
        CTL(5);
        return;
    }
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

/** pdiv restricted to the positions >= lo of the remainder (the lower ones are left untouched): beta^(t+1) A = Q B + E
 *  at positions >= lo, which only depend on positions >= lo - t of A and B. */
static void pdiv_lo(fp *A, long da, const fp *B, long db, fp *Q, fp *bt, long lo)
{
    long t = da - db;
    LD(1);
    fp beta = B[db], bp = FP_ONE;
    CTL(2);
    if (t == 1) {
        LD(3);
        fp an = A[da], an1 = A[da - 1], bn2 = db >= 1 ? B[db - 1] : FP_ZERO;
        fp q1 = fp_mul(beta, an), q0 = fp_sub(fp_mul(beta, an1), fp_mul(an, bn2)), b2 = fp_sqr(beta);
        CTL(3);
        fp prev = lo >= 1 ? B[lo - 1] : FP_ZERO;
        LD(lo >= 1);
        for (long i = lo; i < db; i++) {
            fp bi = B[i];
            A[i] = fp_sub(fp_sub(fp_mul(b2, A[i]), fp_mul(q1, prev)), fp_mul(q0, bi));
            prev = bi;
        }
        long nn = db - lo > 0 ? db - lo : 0;
        LD(2 * nn);
        ST(nn);
        LOOPC(nn);
        Q[0] = q0;
        Q[1] = q1;
        ST(2);
        *bt = b2;
        return;
    }
    for (long j = t; j >= 0; j--) {
        LD(1);
        fp cj = A[db + j];
        long i0 = lo, i1 = lo - j > 0 ? lo - j : 0;
        CTL(4);
        for (long i = i0; i < db + j; i++) A[i] = fp_mul(beta, A[i]);
        long n1 = db + j - i0 > 0 ? db + j - i0 : 0;
        LD(n1);
        ST(n1);
        LOOPC(n1);
        for (long i = i1; i < db; i++) A[j + i] = fp_sub(A[j + i], fp_mul(cj, B[i]));
        long n2 = db - i1 > 0 ? db - i1 : 0;
        LD(2 * n2);
        ST(n2);
        LOOPC(n2);
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

/** Normal pseudo-division step (deg A = deg B + 1) writing the remainder's positions [lo, db) to out[0 .. db - lo) and
 *  out[db - lo] = 0 (out may equal A, the writes trail the reads). */
static void pdiv1_to(const fp *A, long da, const fp *B, long db, fp *Q, fp *bt, long lo, fp *out)
{
    LD(4);
    fp beta = B[db], an = A[da], an1 = A[da - 1], bn2 = db >= 1 ? B[db - 1] : FP_ZERO;
    fp q1 = fp_mul(beta, an), q0 = fp_sub(fp_mul(beta, an1), fp_mul(an, bn2)), b2 = fp_sqr(beta);
    CTL(3);
    fp prev = lo >= 1 ? B[lo - 1] : FP_ZERO;
    LD(lo >= 1);
    for (long i = lo; i < db; i++) {
        fp bi = B[i];
        out[i - lo] = fp_sub(fp_sub(fp_mul(b2, A[i]), fp_mul(q1, prev)), fp_mul(q0, bi));
        prev = bi;
    }
    long nn = db - lo > 0 ? db - lo : 0;
    LD(2 * nn);
    ST(nn);
    LOOPC(nn);
    out[nn] = FP_ZERO;
    Q[0] = q0;
    Q[1] = q1;
    ST(3);
    *bt = b2;
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
            long im = dx < dy ? dx : dy;
            CTL(2);
            for (long i = 0; i <= im; i++) {
                fp xi = x[i], s = fp_add(fp_add(fp_mul(q0, xi), fp_mul(q1, xp)), fp_mul(bt, y[i]));
                y[i] = s;
                xp = xi;
            }
            for (long i = im + 1 > 0 ? im + 1 : 0; i <= dn; i++) {
                fp xi = i <= dx ? x[i] : FP_ZERO, s = fp_add(fp_mul(q0, xi), fp_mul(q1, xp));
                if (i <= dy) s = fp_add(s, fp_mul(bt, y[i]));
                y[i] = s;
                xp = xi;
                CTL(4);
            }
            LOOPC(1);
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
static long VONLY_K = -1; /* the node with this budget (the driver's call) returns M as values on H_Nm, not inverted */
static int hg_vonly_done;
static long VLIM; /* nodes with k <= VLIM may return M also as values (set by hg_gcd to the driver's budget) */

/** Two normal Euclid steps fused in one pass over the coefficients (t = 1 twice): (A, B) -> (E, F) with
 *  b2 A = Q1 B + E, c2 B = Q2 E + F, Q1 = q1 X + q0, Q2 = r1 X + r0 (b2 = beta^2, c2 = gamma^2, gamma = lc(E)).  A
 *  becomes E (degree db - 1), B becomes F.  Returns 0 (nothing done) unless deg E = db - 1. */
static int euclid2(fp *A, fp *Bv, long db, fp *Qs)
{
    LD(7);
    fp an = A[db + 1], an1 = A[db], beta = Bv[db], bn1 = Bv[db - 1], bn2 = Bv[db - 2], bn3 = Bv[db - 3];
    fp q1 = fp_mul(beta, an), q0 = fp_sub(fp_mul(beta, an1), fp_mul(an, bn1)), b2 = fp_sqr(beta);
    fp a1 = A[db - 1], a2 = A[db - 2];
    LD(2);
    fp eT = fp_sub(fp_sub(fp_mul(b2, a1), fp_mul(q1, bn2)), fp_mul(q0, bn1));
    CTL(2);
    if (fp_is0(eT)) return 0;
    fp eT2 = fp_sub(fp_sub(fp_mul(b2, a2), fp_mul(q1, bn3)), fp_mul(q0, bn2));
    fp r1 = fp_mul(eT, beta), r0 = fp_sub(fp_mul(eT, bn1), fp_mul(beta, eT2)), c2 = fp_sqr(eT);
    (void)bn3;
    fp bp = FP_ZERO, ep = FP_ZERO;
    /* i <= db - 2: E_i and F_i; i = db - 1: E_i only */
    for (long i = 0; i <= db - 2; i++) {
        fp bi = Bv[i];
        fp ei = fp_sub(fp_sub(fp_mul(b2, A[i]), fp_mul(q1, bp)), fp_mul(q0, bi));
        fp fi = fp_sub(fp_sub(fp_mul(c2, bi), fp_mul(r1, ep)), fp_mul(r0, ei));
        A[i] = ei;
        Bv[i] = fi;
        bp = bi;
        ep = ei;
    }
    LD(2 * (db - 1));
    ST(2 * (db - 1));
    LOOPC(db - 1);
    A[db - 1] = eT;
    ST(1);
    Qs[0] = q0; Qs[1] = q1; Qs[2] = b2; Qs[3] = r0; Qs[4] = r1; Qs[5] = c2;
    ST(6);
    return 1;
}

/** M <- M P1 P2 with Pj = [[Qj, 1], [cj, 0]] (both rows with nonzero first entries): per row, x' = Q1 x + b2 y,
 *  x'' = Q2 x' + c2 x, stored over x (x'') and y (x'). */
static void mat_q2(mat *M, const fp *Qs)
{
    fp q0 = Qs[0], q1 = Qs[1], b2 = Qs[2], r0 = Qs[3], r1 = Qs[4], c2 = Qs[5];
    LD(6);
    for (int r = 0; r < 2; r++) {
        fp *x = M->e[2 * r], *y = M->e[2 * r + 1];
        long dx = M->d[2 * r], dy = M->d[2 * r + 1], im = dx < dy ? dx : dy;
        fp xp = FP_ZERO, x1p = FP_ZERO;
        CTL(6);
        for (long i = 0; i <= im; i++) {
            fp xi = x[i];
            fp x1 = fp_add(fp_add(fp_mul(q0, xi), fp_mul(q1, xp)), fp_mul(b2, y[i]));
            fp x2 = fp_add(fp_add(fp_mul(r0, x1), fp_mul(r1, x1p)), fp_mul(c2, xi));
            y[i] = x1;
            x[i] = x2;
            xp = xi;
            x1p = x1;
        }
        LD(2 * (im + 1 > 0 ? im + 1 : 0));
        ST(2 * (im + 1 > 0 ? im + 1 : 0));
        LOOPC(im + 1 > 0 ? im + 1 : 0);
        for (long i = im + 1 > 0 ? im + 1 : 0; i <= dx + 2; i++) {
            fp xi = i <= dx ? x[i] : FP_ZERO, yi = i <= dy ? y[i] : FP_ZERO;
            LD((i <= dx) + (i <= dy));
            fp x1 = fp_add(fp_add(fp_mul(q0, xi), fp_mul(q1, xp)), fp_mul(b2, yi));
            fp x2 = i <= dx + 1 ? fp_add(fp_add(fp_mul(r0, x1), fp_mul(r1, x1p)), fp_mul(c2, xi)) : fp_mul(r1, x1p);
            if (i <= dx + 1) { y[i] = x1; ST(1); }
            x[i] = x2;
            ST(1);
            xp = xi;
            x1p = x1;
            CTL(6);
        }
        LOOPC(dx + 3 - (im + 1 > 0 ? im + 1 : 0));
        M->d[2 * r] = dx + 2;
        M->d[2 * r + 1] = dx + 1;
        CTL(2);
    }
    LOOPC(2);
}

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
        /* only the top 2 (k - d) + 1 coefficients matter for the remaining budget (truncation lemma) */
        long lo = da - 2 * (k - d);
        CTL(4);
        if (lo > 0) {
            A += lo;
            Bv += lo;
            da -= lo;
            db -= lo;
            CTL(4);
        }
        long t = da - db;
        int two = t == 1 && db >= 3 && d + 2 <= k && M->d[0] >= 0 && M->d[2] >= 0;
        CTL(8);
        if (two && euclid2(A, Bv, db, Q)) {
            mat_q2(M, Q);
            long df = pdeg(Bv, db - 1);
            da = db - 1;
            db = df;
            d += 2;
            CTL(6);
            continue;
        }
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

/* hgcd is recursive and its calls cannot be inlined: each call is charged HG_CALL = 128 operations, a bound on call and return (2),
 * the stack-pointer adjustment (2), the nine arguments (9), and saving and restoring up to 48 live values, 2 each (96: the integer
 * locals of the caller and its one live field value, beta^(t+1), with its address operations). */
#define HG_CALL 128

/** hgcd(a, b, k) into M (entries with capacity mcap(k) each, at a region that may overlap a and b: they are read only
 *  before M is written). */
static int hgcd(const fp *a, long n, const fp *b, long db, long k, mat *M, fp *mval, long mvs, int mfree)
{
    CTL(HG_CALL + 4);
    if (db < 0 || n - db > k) {
        mat_id(M);
        return 0;
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
        return 0;
    }
    size_t mk = amark();
    long mstr = M->e[1] - M->e[0]; /* M's slots are consecutive (mat_at) at entry; the region is free after the apply */
    CTL(2);
    long k1 = k / 2, cap1 = mcap(k1);
    int lm, l1_;
    long Nm = pow2l(k + 1, &lm);
    /* save: keep the transforms of M1 on the two rows of the final product (from the apply) and form M = M1 (Q M2) */
    int save = k <= KSAVE && ROWS_M == 1 && lm >= 6;
    CTL(6);
    fp *SAV = save ? aalloc(4 * Nm) : NULL;
    mat M1;
    mat_at(&M1, aalloc(4 * cap1), cap1);
    fp *base1 = M1.e[0];
    /* the values of M1 on H of size Nm/2 (row 0 of the apply and of the product): into SAV's row-0 slots, or V1 */
    long Nc1 = pow2l(k1 + 1, &l1_);
    int want1 = Nc1 == Nm / 2 && lm >= 7 && k <= VLIM;
    CTL(4);
    /* a non-save node keeps V1 in its own output region when that region is free from the start (driver, first child) */
    fp *V1 = want1 && !save ? (mfree ? M->e[0] : aalloc(4 * Nc1)) : NULL;
    fp *v1b = save ? SAV : V1;
    long v1s = save ? Nm : (mfree ? mstr : Nc1);
    CTL(4);
    int v1 = hgcd(a, n, b, db, k1, &M1, want1 ? v1b : NULL, v1s, 1);
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
        int usev = v1 && three && (1L << (l - 2)) == Nc1;
        CTL(3);
        if (three) apply_adj3(&M1, a, n + 1, b, db + 1, c, d, l, save ? SAV : NULL, usev ? v1b : NULL, v1s, save ? NULL : V1, 0, 0, 0);
        else apply_adj(&M1, a, n + 1, b, db + 1, c, d, l, row_split(l, ROWS_A), 0, 0);
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
        return 0;
    }
    long t = dc - dd;
    fp bt, *Q = t + 2 > QCAP ? aalloc(t + 2) : QBUF;
    long k2 = k - d1 - t, s2 = dd - 2 * k2;
    if (s2 < 0) s2 = 0;
    CTL(4);
    long len = dd - s2 + 1, de;
    int direct = t == 1;
    fp *evd = save ? base1 : c; /* where the second call's e goes (then d's top right after it) */
    CTL(10);
    if (direct) {
        pdiv1_to(c, dc, d, dd, Q, &bt, s2, evd);
        de = pdeg(evd, dd - s2) + s2;
    } else {
        pdiv_lo(c, dc, d, dd, Q, &bt, s2);
        de = pdeg(c + s2, dd - s2) + s2;
    }
    if (save) {
        /* M1's coefficients are no longer needed: the (e, d) tops go to M1's region, then M2 (Q M2 needs t more) */
        fp *ev = base1, *dv = base1 + len;
        if (!direct) {
            for (long i = 0; i < len; i++) ev[i] = s2 + i <= de ? c[s2 + i] : FP_ZERO;
            LD(len);
            ST(len);
            LOOPC(len);
            CTL(2 * len);
        }
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
        int l2_;
        long rsm = Nm / 2;
        int want2 = pow2l(k2 + 1, &l2_) == rsm && lm >= 7 && k <= VLIM;
        CTL(4);
        fp *V2 = want2 ? M->e[0] + rsm : NULL;
        int v2 = hgcd(dv, dd - s2, ev, de - s2, k2, &M2, V2, mstr, 0);
        {
            /* normal quotient and every entry nonzero: Q is applied pointwise in the product (no Q M2 coefficients) */
            int allp = t == 1;
            for (int i = 0; i < 4; i++) allp = allp && M1.d[i] >= 0 && M2.d[i] >= 0;
            CTL(12);
            if (allp) {
                int nv = k == VONLY_K;
                CTL(2);
                PROF_BEGIN;
                mat_mul_f(M, &M1, &M2, k, SAV, v2 ? V2 : NULL, mstr, Qs, bt, mval, mvs, nv, 1);
                PROF_END(3);
                hg_vonly_done = nv;
                arel(mk);
                return mval != NULL;
            }
        }
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
        int full = 1;
        for (int i = 0; i < 4; i++) full = full && M1.d[i] >= 0 && M2.d[i] >= 0;
        CTL(12);
        int res = 0;
        {
            PROF_BEGIN;
            if (full) {
                int bq = v2 && t == 1;
                CTL(2);
                int nv = k == VONLY_K;
                CTL(2);
                mat_mul_f(M, &M1, &M2, k, SAV, bq ? V2 : NULL, mstr, Qs, bt, mval, mvs, nv, 0);
                hg_vonly_done = nv;
                res = mval != NULL;
            } else mat_mul(M, &M1, &M2, k, ROWS_M, SAV);
            PROF_END(3);
        }
        arel(mk);
        return res;
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
    if (!direct) {
        for (long i = 0; i < len; i++) ev[i] = s2 + i <= de ? c[s2 + i] : FP_ZERO;
        LD(len);
        ST(len);
        LOOPC(len);
        CTL(2 * len);
    }
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
    int l2_;
    long rsm = Nm / 2;
    int want2 = pow2l(k2 + 1, &l2_) == rsm && lm >= 7 && k <= VLIM;
    CTL(4);
    fp *V2 = want2 ? M->e[0] + rsm : NULL;
    int v2 = hgcd(dv, dd - s2, ev, de - s2, k2, &M2, V2, mstr, 0);
    int full = 1;
    for (int i = 0; i < 4; i++) full = full && M1.d[i] >= 0 && M2.d[i] >= 0;
    CTL(12);
    int res = 0;
    {
        PROF_BEGIN;
        if (full) {
            int nv = k == VONLY_K;
            CTL(2);
            mat_mul_f(M, &M1, &M2, k, NULL, v2 ? V2 : NULL, mstr, NULL, FP_ZERO, mval, mvs, nv, 0);
            hg_vonly_done = nv;
            res = mval != NULL;
        } else mat_mul(M, &M1, &M2, k, ROWS_M, NULL);
        PROF_END(3);
    }
    arel(mk);
    return res;
}

/** gcd of a (degree da) and b (degree db < da) in place in buffers of bcap words each (da < bcap); returns the degree of the gcd
 *  and sets *g to the buffer holding it (monic).  A product of the driver on 2^l points that does not fit the buffers (l = L when
 *  bcap = 15 2^(L-4)) is taken on the truncated set instead (apply_adj_tr). */
long hg_gcd(fp *a, long da, fp *b, long db, long kmax, long bcap, fp **g)
{
    QCAP = 64;
    QBUF = aalloc(QCAP);
    {
        int lx;
        XT_N = pow2l((kmax < da / 2 ? kmax : da / 2) + 1, &lx) / 2;
        CTL(3);
        XT = aalloc(XT_N);
        XT[0] = FP_ONE;
        ST(1);
        for (int bb = 0; (1L << bb) < XT_N; bb++) {
            long h = 1L << bb;
            fp r = twiddle(1u << (TREE_K - 1 - bb));
            for (long j = 0; j < h; j++) XT[h + j] = fp_mul(XT[j], r);
            LD(h);
            ST(h);
            LOOPC(h);
            CTL(3);
        }
        LOOPC(lx);
    }
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
        VLIM = k;
        CTL(2);
        mat M;
        mat_at(&M, aalloc(4 * cap), cap);
        VONLY_K = k;
        hg_vonly_done = 0;
        CTL(2);
        hgcd(a, da, b, db, k, &M, NULL, 0, 1);
        int l, lmv;
        long dm = M.d[0], dc = da - dm, N = pow2l(dc + 1, &l), Nmv = pow2l(k + 1, &lmv);
        int three = l >= 6 && 3 * (N >> 2) >= dc + 1, trunc = !three && N > bcap;
        /* rows (sub-rows) of Nmv points: the entries (degree < Nmv) need no folding, the scratch is 4 Nmv words */
        int er = three ? 2 : (l - lmv > 0 ? l - lmv : 0);
        int lsub = lmv < l - er ? lmv : l - er;
        long rsub = 1L << lsub;
        int mv = 0; /* sub-rows of the apply that lie in H of size Nmv, where M is known by its values */
        if (hg_vonly_done && !trunc) mv = (int)(Nmv / rsub);
        CTL(14);
        if (hg_vonly_done && !mv) mat_vals_to_coeffs(&M, lmv);
        {
            PROF_BEGIN;
            if (three) apply_adj3(&M, a, da + 1, b, db + 1, a, b, l, NULL, NULL, 0, NULL, mv, lmv, lsub);
            else if (trunc) apply_adj_tr(&M, a, da + 1, b, db + 1, l);
            else apply_adj(&M, a, da + 1, b, db + 1, a, b, l, er, mv, lmv);
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

SHA-256 `f37e24d83527bb4b5a2b22d928c21b8f8a5f0e7538f1f17f0d57ed545a7d891d`, 14140 bytes.

```c
/* Orchard Poseidon r = NR collision by the odd part of the line digest about centres c = 1, 2, ...: one deterministic run.
 *
 * Per trial: A centre; B g_c by evaluation on O1; prep (start residue, 1/g on O1, g on O2); C R = S^((p-1)/2) mod g;
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
#define NNMAX (15 * ((size_t)1 << (LMAXRUN - 4)))

static fp REG[4 * NNMAX];
static fp DL[15];

enum { S_INIT, S_SETUP, S_A, S_B, S_PREP, S_C, S_D, S_E, S_F, S_G, S_H, S_I, S_N };
static const char *SNAME[S_N] = {"init", "setup", "A", "B", "prep", "C", "D", "E", "F", "G", "H", "I"};

/* Charged constants (bounds on fixed work outside the per-operation counting):
 * STAGE_BK per stage switch (8 counter subtractions and additions with their loads and stores, about 50 operations);
 * TRIAL_BK per snapshot of the counters for the trial rows (8 loads and additions, about 16 operations);
 * PROLOGUE for the argument parse and the dimension and exponent-bit setup of main before the first stage;
 * CONSTS_GEN for the constants of consts.h computed by gen_consts.py (parsing the 201 hexadecimal constants of the organizer
 * file, about 13,000 digits at 6 operations each; psi = 5^((p-1)/2^21) and its inverse: about 650 squarings and multiplications;
 * 2^512 mod p; -p^-1 mod 2^64; 201 conversions to Montgomery form), charged here so that the run includes all preprocessing;
 * stage I: FMT_PER_BYTE for every byte of the output buffer (formatting and copying, the buffer charged in full),
 * REPORT_LOOPS for the loops over the stage and trial rows, SYS_WRITE and SYS_EXIT for the two system calls. */
#define STAGE_BK 100
#define TRIAL_BK 20
#define PROLOGUE 5000
#define CONSTS_GEN 100000
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
    int L = 7;
    while (15 * ((size_t)1 << (L - 4)) < m + 1) L++;
    size_t n = (size_t)1 << L, nn = 15 * (n >> 4);
    /* the start residue X^v P1 mod g, v = 2^t: the largest t <= L - 3 whose Newton buffers fit (stage_prep) */
    int t = L - 3;
    for (;;) {
        size_t k = nn + ((size_t)1 << t) - m, p2 = 1;
        while (p2 < k + 1) p2 <<= 1;
        if (n / 2 + p2 <= nn && 2 * p2 <= nn) break;
        if (--t < 0) return 1;
    }
    if (L > LMAXRUN) return 1;
    int nb = 253 - t;
    uint8_t bits[253];
    for (int i = 0; i < nb; i++) {
        int b = 252 - t - i;
        bits[i] = (EH[b >> 6] >> (b & 63)) & 1;
    }
    fp *R0 = REG, *R1 = REG + nn, *R2 = REG + 2 * nn, *R3 = REG + 3 * nn;
    long kmax = (long)n / 6 < KMAX ? (long)n / 6 : KMAX;

    stage(S_INIT);
    CTL(PROLOGUE + CONSTS_GEN);
    tw_init();
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
        int bad = stage_prep(L, m, t, R1, R0, R2, R3, DL);
        CTL(2);
        if (bad) {
            CTL(TRIAL_BK);
            tcost[tr] = ctr_total(&X) - t0;
            continue;
        }
        stage(S_C);
        fp kap;
        stage_c(R3, R2, R1, R0, DL, L, bits, nb, &kap);
        stage(S_D);
        blk_scale(R0, L, 1, 1);
        tr_inv(R0, L, 1);
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
        hg_arena(R1, 2 * nn);
        fp *G;
        long dg = hg_gcd(R0, (long)m, R3, db, kmax, (long)nn, &G);
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

SHA-256 `6cdb88d5a2d61e96e1f61c2d5999a2b4e482919ec48db987cc5720ff419cd449`, 2402 bytes.

```python
#!/usr/bin/env python3
"""Write consts.h: the Pallas modulus, Montgomery constants, the deployed Orchard round constants and MDS (read from
pareto/orchard-pallas-constants.json, never regenerated), and the roots of unity used by the transforms, all in Montgomery form.

Usage: python3 -I gen_consts.py <orchard-pallas-constants.json> > consts.h
"""
import hashlib
import json
import sys

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
R = 1 << 256
K = 21                      # largest transform tree: 2^K points; psi_K is a primitive 2^K-th root of unity


def limbs(x):
    """Return the four little-endian 64-bit limbs of x as a C initializer."""
    return '{0x%016xULL, 0x%016xULL, 0x%016xULL, 0x%016xULL}' % tuple((x >> (64 * i)) & (2**64 - 1) for i in range(4))


def mont(x):
    """Return the Montgomery form x * 2^256 mod p."""
    return x * R % P


def main():
    raw = open(sys.argv[1], 'rb').read()
    data = json.loads(raw)
    rc = [[int(x, 16) for x in row] for row in data['round_constants']]
    mds = [[int(x, 16) for x in row] for row in data['mds']]
    gen = 5
    assert pow(gen, (P - 1) // 2, P) == P - 1 and pow(gen, (P - 1) // 3, P) != 1
    assert (P - 1) % (1 << 32) == 0
    psi = pow(gen, (P - 1) >> K, P)
    assert pow(psi, 1 << (K - 1), P) == P - 1
    inv = (-pow(P, -1, 1 << 64)) % (1 << 64)
    out = ['/* generated by gen_consts.py from %s, SHA-256 %s */' % (data['source'], hashlib.sha256(raw).hexdigest()),
           '#ifndef CONSTS_H', '#define CONSTS_H',
           '#define P_LIMBS %s' % limbs(P),
           '#define P_INV 0x%016xULL /* -p^-1 mod 2^64 */' % inv,
           '#define R2_LIMBS %s /* 2^512 mod p */' % limbs(R * R % P),
           '#define ONE_LIMBS %s /* Montgomery form of 1 */' % limbs(mont(1)),
           '#define TREE_K %d' % K,
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


## 10. The instrumented half-gcd test of 6.8 (not part of the claim)

`test_d.c` links against the source of section 9 and runs `hg_gcd` on random inputs of a given degree with the buffers sized as at
full size (`-DTRCAP`); `validate_d.py` (Appendix A) compares its printed charge, profile and arena peak with the cost model. It is
not a declared experiment, and nothing in the claim depends on it.

### test_d.c

SHA-256 `7b23320f331691a9a54f488b237910bb532e0b8f169a898d805d9ccc339ae081`, 2458 bytes.

```c
/* Stage D test: read kmax, da, a (da+1 hex), db, b (db+1 hex); print deg G and G's coefficients (monic).  The buffers of a and b
 * hold exactly cap words: with -DTRCAP cap = 15 2^(L-4) for the least such cap > da (the truncated first product of the driver is
 * exercised when it is needed), else the least power of two > da.  With argv[1] = da and argv[2] = kmax: random inputs, counts
 * only. */
#include "ntt.h"
#include "hgcd.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static fp rd(void){ char s[80]; if(scanf("%79s",s)!=1) exit(1); uint64_t l[4]={0,0,0,0}; size_t k=strlen(s);
  for(size_t i=0;i<k;i++){ int c=s[k-1-i]; int d = c<='9'? c-'0' : (c|32)-'a'+10; l[i/16] |= (uint64_t)d << (4*(i%16)); } return fp_from_limbs(l); }
static uint64_t rs = 88172645463325252ULL;
static uint64_t xr(void){ rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static fp rnd(void){ fp a={{xr(),xr(),xr(),xr()>>3}}; return a; }
void die(int c){ fprintf(stderr, "die %d\n", c); exit(c); }
int main(int argc, char **argv){
  long kmax, da, db;
  if (argc > 2) { da = atol(argv[1]); kmax = atol(argv[2]); db = da - 1; }
  else if (scanf("%ld %ld",&kmax,&da)!=2) return 1;
  long cap = 1;
#ifdef TRCAP
  int L = 4; while (15L << (L - 4) < da + 1) L++; cap = 15L << (L - 4);
#else
  while (cap < da + 1) cap <<= 1;
#endif
  fp *a = calloc(cap, sizeof(fp)), *b = calloc(cap, sizeof(fp));
  if (argc > 2) { for (long i = 0; i <= da; i++) a[i] = rnd(); for (long i = 0; i <= db; i++) b[i] = rnd(); }
  else { for (long i = 0; i <= da; i++) a[i] = rd(); if (scanf("%ld",&db)!=1) return 1; for (long i = 0; i <= db; i++) b[i] = rd(); }
  tw_init();
  size_t acap = argc > 3 ? (size_t)atol(argv[3]) : 4 * (size_t)cap + 4096; fp *ar = malloc(acap * sizeof(fp));
  hg_arena(ar, acap);
  struct ctr x0 = X; fp *g; long dg = hg_gcd(a, da, b, db, kmax, cap, &g); struct ctr x1 = X;
  printf("%ld\n", dg);
  if (argc <= 2) for (long i = 0; i <= dg; i++) { uint64_t l[4]; fp_to_limbs(g[i], l); printf("%016lx%016lx%016lx%016lx\n",(unsigned long)l[3],(unsigned long)l[2],(unsigned long)l[1],(unsigned long)l[0]); }
  fprintf(stderr, "cap %ld ops %lu peak %zu words (%.3f cap) prof base %lu napply %lu dapply %lu matmul %lu\n", cap,
          (unsigned long)(ctr_total(&x1) - ctr_total(&x0)), hg_peak, (double)hg_peak / cap, (unsigned long)hg_prof[0],
          (unsigned long)hg_prof[1], (unsigned long)hg_prof[2], (unsigned long)hg_prof[3]);
  return 0;
}
```


## Appendix A. The cost model

Python 3, standard library only. `model.py`: the field-operation and memory charges, the kernels, passes and transforms of `ntt.c`,
and stages B, prep and C; `stage_d.py`: stage D (`hgcd.c` and its part of `main.c`) on a normal remainder sequence, with the arena;
`run_model.py`: the other stages, stage E's and stage F's bounds, and the ledger; `derive.py`: evaluates everything and writes the
numbers of section 6; `stack_bound.py`: the stack bound of section 7 from GCC's call-graph files; `validate_d.py`: the comparison
of 6.8. Each function mirrors the C function of the same name. SHA-256 of each file is listed with it.

### model.py

SHA-256 `673dd3c5a70f9b781bc1871bc13483aca2674ae1c857cf7e3af1d66dd74c574c`, 13247 bytes.

```python
"""Charges of the program of proof.md section 9 (fp.h, fp.c, ntt.c, stageb.c, stagec.c): kernels, passes, transforms, stages B,
prep and C.

Each function mirrors the C function of the same name and returns the counters that its executed statements add (fp.h: a field
operation 1 in its counter; LD/ST(n) n loads or stores plus n address operations; LOOPC(n) = 3n + 2; CTL(k) = k).  No field
arithmetic is done.
"""
from functools import lru_cache
from collections import Counter

K = 21
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
KEYS = ('add', 'sub', 'mul', 'sqr', 'ld', 'st', 'ctl', 'unit')


class C(Counter):
    def __add__(self, o):
        r = C(self)
        for k, v in o.items():
            r[k] += v
        return r

    def __mul__(self, n):
        return C({k: v * n for k, v in self.items()})

    __rmul__ = __mul__

    def total(self):
        return sum(self[k] for k in KEYS)


def ctl(n): return C(ctl=n)
def ld(n): return C(ld=n, ctl=n)
def st(n): return C(st=n, ctl=n)
def loopc(n): return C(ctl=3 * n + 2)
MUL = C(mul=1); SQR = C(sqr=1); ADD = C(add=1); SUB = C(sub=1)
CT = MUL + SUB + ADD
CT1 = SUB + ADD
GS = SUB + ADD + MUL
GS1 = SUB + ADD


@lru_cache(None)
def fp_pow(e):
    r = C()
    top = 255
    while top >= 0 and not (e >> top) & 1:
        top -= 1
        r += ctl(6)
    r += ctl(8)
    if top < 0:
        return r
    for i in range(top - 1, -1, -1):
        r += SQR + ctl(6)
        if (e >> i) & 1:
            r += MUL
    return r + ctl(2)


def fp_inv(): return fp_pow(P - 2)
FROM_U64 = MUL


def twiddle(): return ctl(4) + ld(3) + 2 * MUL
def twiddle_inv(): return ctl(2) + twiddle()
def tw2(inv): return twiddle_inv() if inv else twiddle()


def t1(i):
    c = 0
    while i & 1:
        c += 1
        i >>= 1
    return c


def brv_next_cost(i, bits):
    """Cost of the i-th call (i = 0, 1, ...) of a bit-reversed counter of `bits` bits started at 0."""
    if bits == 0:
        return ctl(2)
    return ctl(2) + ctl(2) + ctl(4 * min(t1(i), bits)) + ctl(3)


@lru_cache(None)
def brv_seq(n_calls, bits, start=0):
    r = C()
    for i in range(start, start + n_calls):
        r += brv_next_cost(i, bits)
    return r


# ---------------- kernels ----------------
@lru_cache(None)
def kernel(r, dirn, triv, ldn):
    R = 1 << r
    c = ld(ldn)
    if r == 1:
        c += (CT1 if triv else CT) if dirn == 0 else (GS1 if triv else GS)
    elif r == 2:
        if dirn == 0:
            c += (3 * CT1 + CT) if triv else 4 * CT
        else:
            c += (GS1 + GS + 2 * GS1) if triv else 4 * GS
    elif r == 3:
        if dirn == 0:
            c += (7 * CT1 + 5 * CT) if triv else 12 * CT
        else:
            c += (7 * GS1 + 5 * GS) if triv else 12 * GS
    else:
        bf = CT if dirn == 0 else GS
        bf1 = CT1 if dirn == 0 else GS1
        if triv:
            c += 15 * bf1 + 17 * bf + ld(11)
        else:
            c += 32 * bf + ld(15)
    c += st(R)
    return c


@lru_cache(None)
def derive(r):
    if r == 4:
        return 3 * SQR + ld(3) + 11 * MUL + ld(4) + loopc(4) + st(15)
    if r == 3:
        return 2 * SQR + ld(3) + 4 * MUL
    if r == 2:
        return ld(1) + SQR + MUL
    return C()


@lru_cache(None)
def sgroup(st_, r, dirn, triv, unr):
    k = kernel(r, dirn, triv, 1 << r)
    if unr:
        n = len(range(0, st_, 4))
        return n * (ctl(1) + 4 * k) + loopc(st_ // 4)
    return st_ * (ctl(1) + k) + loopc(st_)


# ---------------- truncated transforms ----------------
@lru_cache(None)
def tr_pass_k(L, J0, d0, r, dirn, unr):
    S = 1 << (L - d0)
    st_ = S >> r
    nh = 1 << (d0 - 4)
    c = ctl(10) + tw2(dirn) + tw2(dirn)
    r4 = (st(2) + ld(2)) if r == 4 else C()
    for uh in range(nh):
        ul0 = 1 if (uh == 0 and J0 == 0) else 0
        c += ctl(3)
        if ul0:
            c += derive(r) + r4 + sgroup(st_, r, dirn, 1, unr) + MUL
        c += (15 - ul0) * (ctl(5) + derive(r) + r4 + sgroup(st_, r, dirn, 0, unr) + MUL)
        c += loopc(15 - ul0)
        c += MUL
        c += brv_next_cost(uh, d0 - 4)
    c += loopc(nh)
    return c


def tr_pass(L, J0, d0, r, dirn):
    unr = 1 if L - d0 - r >= 2 else 0
    return ctl(8) + tr_pass_k(L, J0, d0, r, dirn, unr)


@lru_cache(None)
def tr_range(L, J0, dlo, dhi, dirn):
    c = ctl(8)
    nl = dhi - dlo
    if nl <= 0:
        return c
    d = dlo
    ds, rs = [], []
    n16 = 1 if (nl % 3 == 1 and nl >= 4) else (2 if (nl % 3 == 2 and nl >= 8) else 0)
    for _ in range(n16):
        ds.append(d); rs.append(4); d += 4
        c += ctl(4)
    c += loopc(n16) + ctl(2)
    if (dhi - d) % 3:
        ds.append(d); rs.append((dhi - d) % 3); d += (dhi - d) % 3
        c += ctl(6)
    n8 = 0
    while d < dhi:
        ds.append(d); rs.append(3)
        c += ctl(3)
        d += 3
        n8 += 1
    np_ = len(ds)
    c += loopc(n8)
    for i in range(np_):
        k = np_ - 1 - i if dirn else i
        c += tr_pass(L, J0, ds[k], rs[k], dirn) + ctl(4)
    c += loopc(np_)
    return c


@lru_cache(None)
def inv16t(J):
    c = C()
    c += (ld(1) + GS) if J else GS1
    c += 3 * (ld(1) + GS)
    c += (ld(1) + 2 * GS) if J else 2 * GS1
    c += ld(1) + 2 * GS
    c += (ld(1) + 4 * GS) if J else 4 * GS1
    c += 2 * (ld(1) + GS)
    c += ld(1) + 2 * GS
    c += ld(1) + GS
    c += ld(3)
    c += 3 * (MUL + SUB)
    c += ld(1) + GS
    c += ld(1) + 2 * GS
    c += ld(1) + 4 * GS
    c += (ld(1) + 7 * GS) if J else 7 * GS1
    c += ADD
    return c


@lru_cache(None)
def fwd16t(J):
    c = C()
    c += (ld(1) + 7 * CT) if J else 7 * CT1
    c += (ld(1) + 4 * CT) if J else 4 * CT1
    c += ld(1) + 4 * CT
    c += (ld(1) + 2 * CT) if J else 2 * CT1
    c += 3 * (ld(1) + 2 * CT)
    c += (ld(1) + CT) if J else CT1
    c += 6 * (ld(1) + CT)
    c += ld(1) + MUL + ADD
    return c


@lru_cache(None)
def tr_top(L, jin, jout):
    q = 1 << (L - 4)
    per = ctl(1) + ld(15)
    if jin >= 0:
        per += inv16t(jin)
    if jout >= 0:
        per += fwd16t(jout)
    per += st(15)
    return ctl(6) + ctl(2) + q * per + loopc(q)


def tr_fwd(L, J0): return tr_top(L, -1, J0) + tr_range(L, J0, 4, L, 0)
def tr_inv(L, J0): return tr_range(L, J0, 4, L, 1) + tr_top(L, J0, -1)


# ---------------- full transforms ----------------
def top_layers(L):
    c = ctl(3)
    if L < 3:
        return L, c
    if L % 3 == 1:
        return 4, c
    return (L % 3 if L % 3 else 3), c


@lru_cache(None)
def pass_b_k(L, Bz, d0, r, dirn, unr):
    """Bz: 1 if B == 0 (first supergroup trivial)."""
    S = 1 << (L - d0)
    st_ = S >> r
    ng = 1 << d0
    r4 = (st(2) + ld(2)) if r == 4 else C()
    c = ctl(10) + tw2(dirn) + tw2(dirn) + derive(r) + r4 + ctl(2)
    c += sgroup(st_, r, dirn, 1 if Bz else 0, unr)
    c += brv_next_cost(0, d0)
    c += (ng - 1) * (ctl(2) + MUL + derive(r) + r4 + sgroup(st_, r, dirn, 0, unr))
    c += brv_seq(ng - 1, d0, 1)
    c += loopc(ng - 1)
    return c


def pass_b(L, Bz, d0, r, dirn):
    unr = 1 if L - d0 - r >= 2 else 0
    return ctl(6) + pass_b_k(L, Bz, d0, r, dirn, unr)


@lru_cache(None)
def top_pass_k(L, Bz, rt, dirn, length):
    st_ = 1 << (L - rt)
    nr = 1 << rt
    c = ctl(8) + tw2(dirn) + derive(rt)
    full = length - (nr - 1) * st_
    c += ctl(4)
    for o in range(st_):
        c += ctl(2)
        ldn = nr
        if o >= full:
            ldn = 0
            for j in range(nr):
                ldn += 1 if o + j * st_ < length else 0
                c += ctl(3)
            c += loopc(nr)
        c += ctl(1)
        c += kernel(rt, dirn, 1 if Bz else 0, ldn)
    c += loopc(st_)
    return c


def top_pass(L, Bz, rt, dirn, length):
    return ctl(4) + top_pass_k(L, Bz, rt, dirn, length)


@lru_cache(None)
def ntt_fwd_bz(L, Bz, length):
    if L == 0:
        return ld(1 if length > 0 else 0) + st(1) + ctl(1)
    rt, c = top_layers(L)
    two = L % 3 == 2 and L >= 11
    c += ctl(4)
    if two:
        rt = 4
    c += top_pass(L, Bz, rt, 0, length)
    if two:
        c += pass_b(L, Bz, 4, 4, 0)
        rt = 8
    d = rt
    while d < L:
        c += pass_b(L, Bz, d, 3, 0) + ctl(4)
        d += 3
    return c + ctl(2) + ctl(2)


@lru_cache(None)
def ntt_inv_b(L, Bz):
    if L == 0:
        return C()
    rt, c = top_layers(L)
    two = L % 3 == 2 and L >= 11
    c += ctl(7)
    if two:
        rt = 8
    d = L - 3
    while d >= rt:
        c += pass_b(L, Bz, d, 3, 1) + ctl(4)
        d -= 3
    c += ctl(2)
    if two:
        c += pass_b(L, Bz, 4, 4, 1)
        rt = 4
    c += top_pass(L, Bz, rt, 1, 1 << L)
    return c + ctl(2)


def ntt_fwd(L): return ctl(1) + ntt_fwd_bz(L, 1, 1 << L)
def ntt_inv(L): return ctl(1) + ntt_inv_b(L, 1)


# ---------------- stage B ----------------
def stage_b(L=20):
    nh = 1 << (L - 4)
    c = loopc(0) + loopc(0)
    per = C(unit=2 * 279) + ADD + SUB + SUB + MUL + st(1) + MUL + MUL
    c += 15 * nh * per
    c += nh * (loopc(15) + MUL + MUL)
    c += brv_seq(16 * nh, L)
    c += loopc(nh)
    return c


# ---------------- prep ----------------
def cyc_mul(la, lb, l, tb_ready):
    N = 1 << l
    c = ld(la) + st(N) + loopc(N) + ctl(N) + ntt_fwd(l)
    if not tb_ready:
        c += FROM_U64 + fp_inv()
        c += ld(lb) + st(N) + loopc(N) + ctl(N) + ntt_fwd(l)
        c += N * MUL + ld(N) + st(N) + loopc(N)
    c += N * MUL + ld(2 * N) + st(N) + loopc(N)
    c += ntt_inv(l) + ctl(2)
    return c


def series_inv(prec):
    t, l = 1, 1
    c = ld(1) + fp_inv() + st(1)
    while t < prec:
        N = 2 * t
        lf = N if N < prec else prec
        c += cyc_mul(lf, t, l, 0)
        c += cyc_mul(t, 0, l, 1)
        c += t * SUB + ld(t) + st(t) + loopc(t)
        t = N
        l += 1
        c += ctl(6)
    return c + ctl(2)


def blk_scale(L, inv):
    nh = 1 << (L - 7)
    c = (twiddle_inv() if inv else twiddle()) * 2 + ctl(10)
    c += 15 * nh * (ctl(5) + 8 * MUL + ld(8) + st(8) + loopc(8) + MUL)
    c += nh * (loopc(15) + MUL)
    c += brv_seq(nh, L - 7)
    c += loopc(nh)
    return c


def stage_prep(L=20, m=976562, t=17):
    n = 1 << L
    w = n >> 4
    nn = 15 * w
    v = 1 << t
    k = nn + v - m
    c = ld(nn) + st(nn) + loopc(nn)
    c += tr_inv(L, 0)
    c += (nn - m - 1) * ctl(2) + ld(nn - m - 1) + loopc(nn - m - 1)
    c += ld(1) + ctl(2)
    c += ctl(k + 1) + ld(k + 1) + st(k + 1) + loopc(k + 1)
    c += series_inv(k + 1)
    c += twiddle()
    c += (k + 1 - w) * (MUL + ADD) + ld(2 * (k + 1 - w)) + st(k + 1 - w) + loopc(k + 1 - w) + ctl(k + 1 - w)
    c += ctl(k + 1) + ld(k + 1) + st(nn) + loopc(nn) + ctl(nn)
    c += tr_fwd(L, 0)
    c += nn * (MUL + SUB) + ld(2 * nn) + st(nn) + loopc(nn)
    c += tr_inv(L, 0)
    c += tr_fwd(L, 1)
    c += nn * (ld(1) + ctl(2) + MUL + st(1)) + loopc(nn)
    c += FROM_U64 + 2 * SQR
    c += MUL + fp_inv() + SUB
    c += (nn - 1) * (ld(2) + MUL + st(1) + MUL + ctl(1)) + loopc(nn - 1)
    c += st(1)
    c += blk_scale(L, 1) + blk_scale(L, 0)
    c += 15 * (twiddle() + SUB + st(1) + ctl(4)) + loopc(15)
    return c


# ---------------- stage C ----------------
def blk_tw():
    return 2 * SQR + 4 * MUL + ld(3)


@lru_cache(None)
def blk1(triv, mode):
    c = blk_tw() + ld(8)
    c += (7 * CT1 + 5 * CT) if triv else 12 * CT
    c += 8 * (SQR + MUL) if mode == 'SQ1' else 8 * MUL
    c += ld(8)
    c += (7 * GS1 + 5 * GS) if triv else (12 * GS + SQR + MUL)
    c += st(8)
    return c


@lru_cache(None)
def bottom1(L, mode):
    nh = 1 << (L - 7)
    c = ctl(2) + twiddle() + ctl(8)
    for uh in range(nh):
        ul0 = 1 if uh == 0 else 0
        c += ctl(2)
        if ul0:
            c += ctl(1) + blk1(1, mode) + MUL + ld(1)
        c += (15 - ul0) * (ctl(6) + blk1(0, mode) + MUL + ld(1))
        c += loopc(15 - ul0) + MUL + ld(1) + brv_next_cost(uh, L - 7)
    return c + loopc(nh)


@lru_cache(None)
def bottom2(L, mode):
    nh = 1 << (L - 7)
    c = ctl(3) + twiddle_inv() + twiddle_inv() + ctl(8)
    if mode == 'B2X':
        c += twiddle() + twiddle()
    blk = ctl(7) + blk_tw() + SQR + MUL + ld(8) + 12 * CT
    blk += 8 * (MUL + MUL + ADD) if mode == 'EXIT2' else 8 * (SQR + MUL + ADD)
    blk += ld(16) + ld(1) + 8 * MUL + SQR
    if mode == 'B2X':
        blk += 3 * MUL + ld(3) + ld(1) + st(1) + 4 * (MUL + MUL + SUB) + MUL + ld(1)
    if mode != 'EXIT2':
        blk += st(8)
    blk += 12 * GS + st(8) + MUL + ld(1)
    for uh in range(nh):
        c += 15 * blk + loopc(15) + MUL + ld(1)
        if mode == 'B2X':
            c += MUL + ld(1)
        c += brv_next_cost(uh, L - 7)
    return c + loopc(nh)


def stage_c(L, bits):
    n = 1 << L
    nn = 15 * (n >> 4)
    c = FROM_U64 + fp_inv()
    c += nn * MUL + ld(nn) + st(nn) + loopc(nn)
    c += tr_fwd(L, 1)
    c += tr_top(L, -1, 0) + tr_range(L, 0, 4, L - 3, 0)
    for b in bits:
        c += bottom1(L, 'SQ1')
        c += tr_range(L, 0, 4, L - 3, 1) + tr_top(L, 0, 1) + tr_range(L, 1, 4, L - 3, 0)
        c += ctl(2)
        c += bottom2(L, 'B2X' if b else 'B2')
        c += tr_range(L, 1, 4, L - 3, 1) + tr_top(L, 1, 0) + tr_range(L, 0, 4, L - 3, 0)
        c += SQR + ADD + SUB + loopc(1) + ctl(2)
    c += bottom1(L, 'EXIT1')
    c += tr_range(L, 0, 4, L - 3, 1) + tr_top(L, 0, 1) + tr_range(L, 1, 4, L - 3, 0)
    c += bottom2(L, 'EXIT2')
    c += tr_range(L, 1, 4, L - 3, 1) + tr_top(L, 1, -1)
    c += ADD + SUB
    return c
```

### stage_d.py

SHA-256 `b6f632c31ad6d61de3fbc9f0aaa9ed1ce75d562b366f336ae8dd79e04795ecfe`, 20033 bytes.

```python
"""Stage D (hgcd.c and its part of main.c) on a normal remainder sequence: the charges and the arena, from the source.

Every quotient of the Euclidean sequence of the inputs has degree 1, down to the gcd of degree dgcd (whose successor is 0),
and deg b = deg a - 1.  Then every length and every test of the code is a function of the degrees alone, which this module
tracks; it does no field arithmetic.  Each function mirrors the C function of the same name and adds the counters that its
executed statements add (fp.h: LD/ST n loads or stores plus n address operations, LOOPC(n) = 3n + 2, CTL(k) = k).  The stack
arena of the C code (aalloc/amark/arel) is mirrored by AR, so that the peak of AR_TOP is derived too.
"""
from model import (C, ctl, ld, st, loopc, MUL, SQR, ADD, SUB, twiddle, fp_inv, FROM_U64,
                   ntt_fwd_bz, ntt_inv_b, tr_top, tr_inv, blk_scale)

HG_BASE = 48
HG_CALL = 128
QCAP = 64
ROWS_A = 3
PROF = [C(), C(), C(), C()]   # base, node apply, driver apply, products (the program's reporting-only profile)
G = {'KSAVE': 0, 'VLIM': 0, 'VONLY_K': -1, 'vonly_done': 0}
AR = {'top': 0, 'peak': 0}
STATS = {}   # (k, role) -> {own charge of one call (children excluded): calls}


def hg_arena():
    AR['top'] = 0
    AR['peak'] = 0


def aalloc(n):
    """Returns (offset, charge): 5 operations."""
    off = AR['top']
    AR['top'] += n
    AR['peak'] = max(AR['peak'], AR['top'])
    return off, ctl(5)


def amark(): return AR['top']


def arel(m):
    AR['top'] = m
    return ctl(1)


def pdeg(length, deg):
    """Scan of a[0..length) from the top down to its degree deg (-1: all zero)."""
    if deg >= 0:
        return (length - 1 - deg) * (ld(1) + ctl(5)) + ld(1) + ctl(2) + ctl(2)
    return length * (ld(1) + ctl(5)) + ctl(2)


def pow2l(x):
    n, e = 1, 0
    while n < x:
        n <<= 1
        e += 1
    return n, e, ctl(4 * e + 2)


def mcap(k):
    n, _, c = pow2l(k + 1)
    return n + 2, c


def mat_at(): return ctl(8) + loopc(4)
def mat_id(): return st(2) + ctl(4)
def copy(n): return ld(n) + st(n) + loopc(n)


def fold(length, rs, w_is1):
    nb = (length + rs - 1) // rs
    c = ctl(3)
    if nb <= 1:
        z = rs - (0 if length < 0 else length)
        return c + copy(length) + st(z) + loopc(z)
    top = (nb - 1) * rs
    tl = length - top
    c += copy(tl) + st(rs - tl) + loopc(rs - tl)
    blk = (rs * ADD) if w_is1 else rs * (MUL + ADD)
    c += (nb - 1) * (blk + ld(2 * rs) + st(rs) + loopc(rs) + ctl(3))
    c += loopc(nb - 1)
    return c


def fold1_inplace(length, N):
    c = C()
    b = N
    while b < length:
        m = min(length - b, N)
        c += m * ADD + ld(2 * m) + st(m) + loopc(m) + ctl(4)
        b += N
    c += loopc((length - 1) // N)
    z = N - length if length < N else 0
    c += st(z) + loopc(z)
    return c


def brv(bits): return ctl(4 * bits) + loopc(bits)
def row_root(e): return brv(e) + ctl(2) + twiddle()


def row_entry(dx, rs, lr, Bz, w_is1):
    c = ctl(2)
    if dx + 1 <= rs:
        return c + ntt_fwd_bz(lr, Bz, dx + 1)
    return c + fold(dx + 1, rs, w_is1) + ntt_fwd_bz(lr, Bz, 1 << lr)


def ntt_fwd(l): return ctl(1) + ntt_fwd_bz(l, 1, 1 << l)
def ntt_inv(l): return ctl(1) + ntt_inv_b(l, 1)


def scale_rows(rs): return FROM_U64 + rs * 2 * MUL + ld(2 * rs) + st(2 * rs) + loopc(rs)


def true_degs(h):
    """Degrees of the entries of a matrix of h normal steps: r11, r12, r21, r22."""
    return [h, h - 1, h - 1, h - 2]


def mat_vals_to_coeffs(M, lm):
    c = C()
    M['d'] = true_degs(M['h'])
    for i in range(4):
        c += ntt_inv(lm) + pdeg(1 << lm, M['d'][i])
    return c + loopc(4)


PW = 4 * MUL + 2 * SUB  # one point of the fused adj pass


def apply_adj(M, la, lb, c_is_a, l, e, mv, lmv):
    N = 1 << l
    c = fold1_inplace(la, N) if c_is_a else fold(la, N, 1)
    c += fold1_inplace(lb, N) if c_is_a else fold(lb, N, 1)
    c += ctl(4) + ntt_fwd(l) + ntt_fwd(l)
    lr = l - e
    rs = 1 << lr
    mk = amark()
    _, a = aalloc(4 * rs)
    c += a
    for rho in range(1 << e):
        c += row_root(e) + ctl(7)
        if rho < mv:
            c += ctl(5)
        else:
            for i in range(4):
                if M['d'][i] >= 0:
                    c += row_entry(M['d'][i], rs, lr, rho == 0, rho == 0)
                else:
                    c += st(rs) + loopc(rs)
                c += ctl(4)
            c += loopc(4)
        c += rs * PW + ld(6 * rs) + st(2 * rs) + loopc(rs)
        if rho < mv:
            c += scale_rows(rs)
            if rho == mv - 1:
                c += mat_vals_to_coeffs(M, lmv)
            c += ctl(2)
        c += ctl(2)
    c += loopc(1 << e) + arel(mk) + ntt_inv(l) + ntt_inv(l)
    return c


SPLIT_AT = 4 * ADD + 3 * SUB + MUL


def split3(length, rs):
    ifull = max(0, min(length - 3 * rs, rs))
    c = ctl(5) + ifull * SPLIT_AT + loopc(ifull)
    c += (rs - ifull) * (ctl(8) + SPLIT_AT) + loopc(rs - ifull)
    c += ld(min(length, 4 * rs)) + st(3 * rs)
    return c


CRT = 5 * ADD + 3 * SUB + MUL


def apply_adj3(M, la, lb, c_is_a, l, sav, mval, scr, mv, lmv, lsub):
    lr = l - 2
    rs = 1 << lr
    N4 = 4 * rs
    c = row_root(2) + ctl(4)
    if c_is_a and la > N4:
        c += fold1_inplace(la, N4)
        la = N4
    if c_is_a and lb > N4:
        c += fold1_inplace(lb, N4)
        lb = N4
    for ln in (la, lb):
        if (not c_is_a) and ln > N4:
            _, a = aalloc(N4)
            c += a + fold(ln, N4, 1) + split3(N4, rs) + arel(amark() - N4)
        else:
            c += split3(ln, rs)
    mk = amark()
    if lsub <= 0 or lsub > lr or sav:
        lsub = lr
    f = lr - lsub
    rsub = 1 << lsub
    c += ctl(5)
    if not sav and not scr:
        _, a = aalloc(4 * rsub)
        c += a
    c += ctl(4)
    for z in range(3):
        rho = 0 if z == 0 else ((3 - z) if sav else z)
        c += row_root(2) + ctl(7)
        c += ntt_fwd_bz(lr, rho == 0, 1 << lr) * 2
        for j in range(1 << f):
            g = rho * (1 << f) + j
            c += ctl(6)
            if f:
                c += row_root(2 + f)
            usev = (rho == 0 and mval)
            c += ctl(4)
            if g < mv:
                usev = True
                c += ctl(4)
            for i in range(4):
                c += ctl(6)
                if usev:
                    c += ctl(2)
                else:
                    if M['d'][i] >= 0:
                        c += row_entry(M['d'][i], rsub, lsub, g == 0, rho == 0 and j == 0)
                    else:
                        c += st(rsub) + loopc(rsub)
            c += loopc(4)
            c += rsub * PW + ld(6 * rsub) + st(2 * rsub) + loopc(rsub)
            if g < mv:
                c += scale_rows(rsub)
                if g == mv - 1:
                    c += mat_vals_to_coeffs(M, lmv)
                c += ctl(2)
        c += loopc(1 << f)
        c += ntt_inv_b(lr, rho == 0) * 2 + ctl(5)
    c += loopc(3) + arel(mk)
    c += 2 * (rs * CRT + ld(3 * rs) + st(3 * rs) + loopc(rs)) + loopc(2)
    return c


def apply_adj_tr(M, la, lb, l):
    rs = 1 << (l - 4)
    nn = 15 * rs
    c = st(nn - la) + loopc(nn - la) + st(nn - lb) + loopc(nn - lb)
    c += tr_top(l, -1, 0) * 2
    mk = amark()
    _, a = aalloc(4 * rs)
    c += a
    for rho in range(15):
        c += row_root(4) + ctl(4) + ntt_fwd_bz(l - 4, rho == 0, 1 << (l - 4)) * 2
        for i in range(4):
            if M['d'][i] >= 0:
                c += row_entry(M['d'][i], rs, l - 4, rho == 0, rho == 0)
            else:
                c += st(rs) + loopc(rs)
            c += ctl(4)
        c += loopc(4) + rs * PW + ld(6 * rs) + st(2 * rs) + loopc(rs)
        c += ntt_inv_b(l - 4, rho == 0) * 2
    c += loopc(15) + arel(mk) + tr_top(l, 0, -1) * 2
    return c


def mat_mul_f(O, A, Bm, k, Asav, bval, Qc, oval, noinv, qraw):
    N, l, c = pow2l(k + 1)
    lr = l - 1
    rs = 1 << lr
    mk = amark()
    if oval:
        c += FROM_U64
    c += ctl(6)
    for rho in range(2):
        c += row_root(1)
        bv = rho == 0 and bval
        c += ctl(5)
        scr = (not Asav) and rho == 1
        if scr:
            _, a = aalloc(4 * rs)
            c += a
        c += ctl(2)
        for i in range(4):
            if not Asav:
                c += row_entry(A['d'][i], rs, lr, rho == 0, rho == 0)
            if not bv:
                c += row_entry(Bm['d'][i], rs, lr, rho == 0, rho == 0)
            c += ctl(8)
        c += loopc(4) + ctl(8) + loopc(4) + ld(2)
        useq = Qc and (bv or qraw)
        if useq and rho == 1:
            c += MUL + twiddle() + ctl(2)
        c += ctl(6)
        per = ld(4)
        if useq:
            per += (MUL + ADD) + (MUL + ADD) + (MUL + ADD) + MUL + MUL + ld(1)
        per += 4 * (2 * MUL + ADD) + ld(4) + st(4)
        if oval:
            per += 4 * MUL + st(4) + ctl(1)
        c += rs * per + loopc(rs)
        if scr:
            c += arel(mk)
    c += loopc(2) + arel(mk) + ctl(1)
    h = A['h'] + Bm['h'] + (1 if qraw else 0)
    O['h'] = h
    if noinv:
        O['d'] = [h, N - 1, N - 1, N - 1]
        return c + ctl(5)
    O['d'] = true_degs(h)
    for i in range(4):
        c += ntt_inv(l) + pdeg(N, O['d'][i])
    return c + loopc(4)


def pdiv_t1(db):
    return ld(1) + ld(3) + MUL + (2 * MUL + SUB) + SQR + ctl(2) + db * (3 * MUL + 2 * SUB) + ld(2 * db) + st(db) + \
        loopc(db) + st(2)


def pdiv1_to(db, lo):
    nn = max(db - lo, 0)
    return ld(4) + MUL + (2 * MUL + SUB) + SQR + ctl(3) + ld(1 if lo >= 1 else 0) + nn * (3 * MUL + 2 * SUB) + \
        ld(2 * nn) + st(nn) + loopc(nn) + st(3)


def mat_q_t1(M):
    """M <- M [[Q, 1], [bt, 0]] with t = 1 (charges of mat_q)."""
    c = C()
    d = M['d']
    nd = list(d)
    for r in range(2):
        dx, dy = d[2 * r], d[2 * r + 1]
        dn = dy if dx < 0 else dx + 1
        c += ctl(6)
        if dx >= 0:
            c += ld(2)
            im = min(dx, dy)
            c += ctl(2)
            c += (im + 1 if im >= 0 else 0) * (3 * MUL + 2 * ADD)
            for i in range(max(im + 1, 0), dn + 1):
                c += 2 * MUL + ADD
                if i <= dy:
                    c += MUL + ADD
                c += ctl(4)
            c += loopc(1) + ld(dx + 1 + dy + 1) + st(dn + 1) + loopc(dn + 1) + ctl(4)
        else:
            for i in range(dn, -1, -1):
                if i <= dy:
                    c += ld(1) + MUL
                j0 = max(i - dx, 0)
                j1 = min(i, 1)
                cnt = max(j1 - j0 + 1, 0)
                c += ctl(6) + cnt * (MUL + ADD) + ld(2 * cnt) + loopc(cnt) + st(1)
            c += loopc(dn + 1) + ctl(4)
        nd[2 * r], nd[2 * r + 1] = dn, dx
    M['d'] = nd
    M['h'] += 1
    return c + loopc(2)


def euclid2(db):
    n = db - 1
    return ld(7) + MUL + (2 * MUL + SUB) + SQR + ld(2) + (3 * MUL + 2 * SUB) + ctl(2) + ctl(2) + (3 * MUL + 2 * SUB) + \
        MUL + (2 * MUL + SUB) + SQR + n * (6 * MUL + 4 * SUB) + ld(2 * n) + st(2 * n) + loopc(n) + st(1) + st(6)


def mat_q2(M):
    c = ld(6)
    d = M['d']
    nd = list(d)
    for r in range(2):
        dx, dy = d[2 * r], d[2 * r + 1]
        im = min(dx, dy)
        c += ctl(6)
        n1 = im + 1 if im + 1 > 0 else 0
        c += n1 * (6 * MUL + 4 * ADD) + ld(2 * n1) + st(2 * n1) + loopc(n1)
        for i in range(n1, dx + 3):
            c += ld((1 if i <= dx else 0) + (1 if i <= dy else 0))
            c += 3 * MUL + 2 * ADD
            c += (3 * MUL + 2 * ADD) if i <= dx + 1 else MUL
            if i <= dx + 1:
                c += st(1)
            c += st(1) + ctl(6)
        c += loopc(dx + 3 - n1)
        nd[2 * r], nd[2 * r + 1] = dx + 2, dx + 1
        c += ctl(2)
    M['d'] = nd
    M['h'] += 2
    return c + loopc(2)


def hgcd_base(n, db, k, M):
    mk = amark()
    c = C()
    for size in (n + 1, n + 1, n + 2):
        _, a = aalloc(size)
        c += a
    c += copy(n + 1) + copy(db + 1) + mat_id()
    M['d'] = [0, -1, -1, 0]
    M['h'] = 0
    da, d = n, 0
    while db >= 0 and d + da - db <= k:
        lo = da - 2 * (k - d)
        c += ctl(4)
        if lo > 0:
            da -= lo
            db -= lo
            c += ctl(4)
        t = da - db
        assert t == 1
        two = t == 1 and db >= 3 and d + 2 <= k and M['d'][0] >= 0 and M['d'][2] >= 0
        c += ctl(8)
        if two:
            c += euclid2(db) + mat_q2(M) + pdeg(db - 1, db - 2)
            da = db - 1
            db = db - 2
            d += 2
            c += ctl(6)
            continue
        c += pdiv_t1(db) + mat_q_t1(M) + pdeg(db, db - 1)
        da, db = db, db - 1
        d += 1
        c += ctl(10)
    c += ctl(4) + arel(mk)
    return c


def _role(save, mval, mfree, nv):
    return ('driver call' if nv else ('saved M1' if save else 'plain')) + (', returns values' if mval else '') + \
        (', first child' if mfree and not nv else '')


def _stat(k, role, own):
    e = STATS.setdefault((k, role), {})
    e[own] = e.get(own, 0) + 1


def hgcd(n, db, k, M, mval, mfree):
    """hgcd(a, b, k) on a normal pair of degrees (n, db): returns (charge, whether M's values were also returned)."""
    c = ctl(HG_CALL + 4)
    if db < 0 or n - db > k:
        M['d'] = [0, -1, -1, 0]
        M['h'] = 0
        return c + mat_id(), 0
    s = n - 2 * k
    c += ctl(2)
    if s > 0:
        n -= s
        db -= s
        c += ctl(4)
    c += ctl(2)
    if k <= HG_BASE:
        b = hgcd_base(n, db, k, M)
        PROF[0] += b
        _stat(k, 'base', (c + b).total())
        return c + b, 0
    mk = amark()
    c += ctl(2)
    k1 = k // 2
    cap1, pc = mcap(k1)
    c += pc
    Nm, lm, pc = pow2l(k + 1)
    c += pc
    save = k <= G['KSAVE'] and lm >= 6
    c += ctl(6)
    if save:
        _, a = aalloc(4 * Nm)
        c += a
    base1, a = aalloc(4 * cap1)
    c += a + mat_at()
    Nc1, _, pc = pow2l(k1 + 1)
    c += pc
    want1 = Nc1 == Nm // 2 and lm >= 7 and k <= G['VLIM']
    c += ctl(4)
    V1 = want1 and not save
    if V1 and not mfree:
        _, a = aalloc(4 * Nc1)
        c += a
    c += ctl(4)
    M1 = {}
    cc, v1 = hgcd(n, db, k1, M1, want1, 1)
    c += cc
    kids = cc.total()
    d1 = M1['d'][0]
    assert d1 == M1['h'] == k1
    dc = n - d1
    N, l, pc = pow2l(dc + 1)
    c += pc
    three = l >= 6 and 3 * (N >> 2) >= dc + 1
    c += ctl(4)
    if three:
        N = 3 * (N >> 2)
    save = save and three and (1 << (l - 2)) == Nm // 2
    c += ctl(4)
    c_off, a = aalloc(2 * N)
    c += a
    usev = v1 and three and (1 << (l - 2)) == Nc1
    p1 = ctl(3)
    if three:
        p1 += apply_adj3(M1, n + 1, db + 1, False, l, save, usev, (not save) and V1, 0, 0, 0)
    else:
        e = min(ROWS_A, l - 4 if l - 4 > 0 else 0)
        p1 += ctl(4) + apply_adj(M1, n + 1, db + 1, False, l, e, 0, 0)
    PROF[1] += p1
    c += p1
    dd = dc - 1
    c += pdeg(N, dd) + ctl(4)
    assert dd >= 0 and dc - dd <= k - d1
    t = dc - dd
    k2 = k - d1 - t
    s2 = max(dd - 2 * k2, 0)
    c += ctl(4)
    length = dd - s2 + 1
    c += ctl(10)
    c += pdiv1_to(dd, s2)
    de = dd - 1
    c += pdeg(dd - s2, de - s2)
    M2 = {}
    if save:
        c += copy(length)
        cap2, pc = mcap(k2)
        cap2 = max(cap2, k2 + t + 2)
        r2 = max(4 * cap2, 2 * length)
        c += pc + ctl(6) + arel(base1 + r2)
        _, a = aalloc(t + 1)
        c += a + copy(t + 1) + mat_at()
        n2, _, pc = pow2l(k2 + 1)
        c += pc
        want2 = n2 == Nm // 2 and lm >= 7 and k <= G['VLIM']
        c += ctl(4)
        cc, v2 = hgcd(dd - s2, de - s2, k2, M2, want2, 0)
        c += cc + ctl(12)
        kids += cc.total()
        nv = k == G['VONLY_K']
        c += ctl(2)
        p3 = mat_mul_f(M, M1, M2, k, True, v2, True, mval, nv, 1)
        PROF[3] += p3
        c += p3
        G['vonly_done'] = 1 if nv else 0
        c += arel(mk)
        _stat(k, _role(True, mval, mfree, nv), c.total() - kids)
        return c, 1 if mval else 0
    assert d1 + t + 1 <= cap1   # not wide
    c += ctl(4) + mat_q_t1(M1) + copy(length)
    cap2, pc = mcap(k2)
    r2 = max(4 * cap2, 2 * length)
    c += pc + ctl(4) + arel(c_off + r2) + mat_at()
    n2, _, pc = pow2l(k2 + 1)
    c += pc
    want2 = n2 == Nm // 2 and lm >= 7 and k <= G['VLIM']
    c += ctl(4)
    cc, v2 = hgcd(dd - s2, de - s2, k2, M2, want2, 0)
    c += cc + ctl(12)
    kids += cc.total()
    assert all(x >= 0 for x in M1['d'] + M2['d'])   # full: mat_mul_f, never mat_mul
    nv = k == G['VONLY_K']
    p3 = ctl(2) + mat_mul_f(M, M1, M2, k, False, v2, False, mval, nv, 0)
    PROF[3] += p3
    c += p3
    G['vonly_done'] = 1 if nv else 0
    c += arel(mk)
    _stat(k, _role(False, mval, mfree, nv), c.total() - kids)
    return c, 1 if mval else 0


def final_euclid(da, db, dgcd):
    """The driver's Euclid loop below degree 2 HG_BASE + 1, from (da, db = da - 1) down to the gcd, and the monic scaling."""
    c = ctl(2)
    _, a = aalloc(da + 2)
    c += a
    while db >= 0:
        assert da - db == 1
        de = db - 1 if db > dgcd else -1
        c += pdiv_t1(db) + pdeg(db, de)
        da, db = db, de
        c += ctl(6)
    return c + ld(1) + fp_inv() + (da + 1) * MUL + ld(da + 1) + st(da + 1) + loopc(da + 1)


def hg_gcd(da, db, kmax, bcap, dgcd=1):
    """hg_gcd on a normal pair of degrees (da, db = da - 1) with a gcd of degree dgcd; returns (charge, driver iterations)."""
    hg_arena()
    _, c = aalloc(QCAP)
    xtn, lx, pc = pow2l(min(kmax, da // 2) + 1)
    xtn //= 2
    _, a = aalloc(xtn)
    c += pc + ctl(3) + a + st(1)
    bb = 0
    while (1 << bb) < xtn:
        h = 1 << bb
        c += twiddle() + h * MUL + ld(h) + st(h) + loopc(h) + ctl(3)
        bb += 1
    c += loopc(lx)
    iters = []
    while db >= 0:
        if da <= 2 * HG_BASE:
            c += final_euclid(da, db, dgcd)
            return c, iters
        c0 = c.total()
        c += ctl(2)
        k = 1
        while 2 * k + 1 <= kmax and 2 * k + 1 <= da // 2:
            k = 2 * k + 1
            c += ctl(7)
        c += ctl(6)
        mk = amark()
        cap, pc = mcap(k)
        c += pc
        G['KSAVE'] = k // 2
        G['VLIM'] = k
        c += ctl(2)
        _, a = aalloc(4 * cap)
        c += a + mat_at()
        G['VONLY_K'] = k
        G['vonly_done'] = 0
        c += ctl(2)
        M = {}
        cc, _ = hgcd(da, db, k, M, False, 1)
        c += cc
        top_call = cc.total()
        dm = M['d'][0]
        dc = da - dm
        N, l, pc = pow2l(dc + 1)
        c += pc
        Nmv, lmv, pc = pow2l(k + 1)
        c += pc
        three = l >= 6 and 3 * (N >> 2) >= dc + 1
        trunc = (not three) and N > bcap
        er = 2 if three else max(l - lmv, 0)
        lsub = min(lmv, l - er)
        rsub = 1 << lsub
        mv = Nmv // rsub if (G['vonly_done'] and not trunc) else 0
        c += ctl(14)
        if G['vonly_done'] and not mv:
            c += mat_vals_to_coeffs(M, lmv)
        if three:
            p2 = apply_adj3(M, da + 1, db + 1, True, l, False, False, False, mv, lmv, lsub)
            kind = '3'
        elif trunc:
            p2 = apply_adj_tr(M, da + 1, db + 1, l)
            kind = 'tr'
        else:
            p2 = apply_adj(M, da + 1, db + 1, True, l, er, mv, lmv)
            kind = 'full'
        PROF[2] += p2
        c += p2 + arel(mk)
        it = [da, k, dc, l, kind, mv, p2.total()]
        da = dc
        db = dc - 1
        c += pdeg(da, db) + ctl(4)
        c += pdiv_t1(db) + arel(mk)
        de = db - 1
        c += pdeg(db, de)
        da, db = db, de
        c += ctl(8)
        iters.append(tuple(it + [top_call, c.total() - c0 - top_call]))
    raise AssertionError('the normal sequence ends in the final Euclid loop')


def stage_d(L=20, m=976562, dgcd=1):
    """Stage D's row of main.c: blk_scale and the truncated inverse on O2, kappa subtracted, deg(kappa R - kappa) found
    (m - 1: one test), hg_gcd, the trial bookkeeping and the switch to stage E."""
    nn = 15 * ((1 << L) >> 4)
    c = blk_scale(L, 1) + tr_inv(L, 1) + ld(1) + SUB + st(1)
    c += ld(1) + ctl(2) + ctl(2)
    kmax = min((1 << L) // 6, 131071)
    cc, iters = hg_gcd(m, m - 1, kmax, nn, dgcd)
    c += cc + ctl(4) + ctl(100)
    return c, iters
```

### run_model.py

SHA-256 `28ba5f370e2d9c2e41263de7a917757ee93acbd427a83eeb5af34cd76794b519`, 6927 bytes.

```python
"""Operation count of one run of the program of proof.md section 9 (stages init to I), from its charge statements.

The count depends on the target only through four data-dependent branches: (a) whether g_1 vanishes on O1 (prep), (b) the
degree sequence of the Euclidean remainders of (g_1, kappa (R - 1)) (stage D), (c) deg G and the number of shifts used by
find_root (stage E), and (d) the Tonelli-Shanks path of the square root (stage F).  This module evaluates the stages on the
generic path ((a) no zero, (b) normal) for a gcd of degree d, and bounds stages E and F over all their paths.
"""
from functools import lru_cache

from model import (C, ctl, ld, st, loopc, MUL, SQR, ADD, SUB, P, fp_pow, fp_inv, FROM_U64, twiddle, twiddle_inv,
                   stage_b, stage_prep, stage_c)
import stage_d

STAGE_BK, TRIAL_BK, PROLOGUE, CONSTS_GEN = 100, 20, 5000, 100000
OUTCAP, FMT_PER_BYTE, REPORT_LOOPS, SYS_EXIT = 8192, 400, 20000, 10000
SYS_WRITE = 10000 + (OUTCAP << 3)
SPLIT_CAP = 256
TREE_K, TW_BITS = 21, 7
EH = (P - 1) // 2
E5 = (4 * (P - 1) + 1) // 5
Q_TS = (P - 1) >> 32
Q1_TS = (Q_TS - 1) // 2


def tw_init():
    """ntt.c tw_init: the three 128-entry tables, the pass constants, the truncated-top tables."""
    tw_n = 1 << TW_BITS
    c = C()
    for _ in range(3):
        c += st(1) + (tw_n - 1) * (MUL + ld(1) + st(1)) + loopc(tw_n - 1) + TW_BITS * SQR + loopc(TW_BITS) + ctl(2)
    c += loopc(3)
    c += (TREE_K - 4) * 2 * SQR + loopc(TREE_K - 4)
    c += 2 * SQR + SQR + MUL + SQR + MUL + st(6)
    c += 2 * (MUL + MUL + MUL + MUL + MUL) + st(8)
    for _ in range(2):
        for t in range(4):
            c += (1 << t) * (twiddle() + twiddle_inv() + st(2) + ctl(10)) + loopc(1 << t)
        c += loopc(4)
    return c + loopc(2)


def mds_row(): return ld(3) + 3 * MUL + 2 * ADD
def pow5(): return 2 * SQR + MUL


def line_setup():
    """line.c line_setup."""
    c = ld(1) + MUL + ADD + pow5()
    c += 3 * (ld(2) + MUL + ADD) + loopc(3)
    c += ld(4) + 2 * MUL + SUB + fp_inv()
    c += ld(4) + 2 * (3 * MUL + SUB + ADD)
    c += ld(2) + SUB
    c += mds_row() + ADD + 2 * mds_row() + 3 * pow5()
    c += 3 * 2 * mds_row() + loopc(3) + st(10)
    return c


def line_back():
    """line.c line_back: tau = W^e, nk = (U_Q + tau a)^e - c00, rho = (V_Q + tau b)^e - c01."""
    return 3 * fp_pow(E5) + ld(2) + 2 * (MUL + ADD + SUB) + ld(4)


def ts_iter(m, i):
    """One iteration of the Tonelli-Shanks loop with current m and found order 2^i (0 < i < m)."""
    return ctl(2) + i * (ctl(2) + SQR + ctl(2)) + ctl(2) + (m - i - 1) * SQR + loopc(m - i - 1) + SQR + 2 * MUL + ctl(4)


@lru_cache(None)
def ts_worst(m):
    """Largest cost of the Tonelli-Shanks loop from m (strictly decreasing orders), the final successful test included."""
    best = ctl(2)
    for i in range(1, m):
        c = ts_iter(m, i) + ts_worst(i)
        if c.total() > best.total():
            best = c
    return best


def ts_path(path):
    """Cost of the loop for the order sequence path (e.g. (5, 2)), the final test included."""
    c, m = C(), 32
    for i in path:
        c += ts_iter(m, i)
        m = i
    return c + ctl(2)


def fp_sqrt_fixed():
    return FROM_U64 + fp_pow(Q_TS) + fp_pow(Q1_TS) + SQR + MUL + MUL


def stage_f(ts):
    """Stage F with Tonelli-Shanks loop cost ts, plus the switch to stage G."""
    return fp_sqrt_fixed() + ts + ADD + SUB + 2 * line_back() + ctl(STAGE_BK)


def powmod_small(dg):
    """main.c powmod_small: (X + delta)^E mod G for G of degree dg, schoolbook (charged per bit as written)."""
    c = st(dg)
    for bit in range(253, -1, -1):
        c += dg * dg * (MUL + ADD)
        if (EH >> bit) & 1:
            c += (2 * dg - 1) * (MUL + ADD) + MUL
        c += dg * dg * (MUL + SUB)
        c += ctl(27 * dg * dg) + ld(4 * dg * dg) + st(2 * dg * dg)
    return c


@lru_cache(None)
def gcd_small_worst(du, dv):
    """Largest charge of main.c gcd_small(u, du, v, dv) over all remainder-degree sequences (dv >= 0 on entry)."""
    if dv < 0:
        return fp_inv() + (du + 1) * MUL + ctl(9 * (du + 1))
    step = fp_inv() + (du - dv + 1) * (MUL + (dv + 1) * (MUL + SUB) + ctl(9 * (dv + 1)) + ld(2 * (dv + 1)) + st(dv + 1))
    best = None
    for de in range(-1, dv):
        scan = ctl(2) * ((dv - 1 - de) + (1 if de >= 0 else 0))
        c = step + scan + ctl(8) + gcd_small_worst(dv, de)
        if best is None or c.total() > best.total():
            best = c
    return best


@lru_cache(None)
def root_iter_worst(dg):
    """Largest charge of one shift of main.c find_root at degree dg >= 2 (any r, any gcd path, a split included)."""
    base = ctl(4) + FROM_U64 + powmod_small(dg) + SUB + ctl(9 * (2 * dg + 2)) + ctl(12) + ctl(3)
    best = None
    for dr in range(-1, dg):
        scan = ctl(2) * ((dg - 1 - dr) + (1 if dr >= 0 else 0))
        g = gcd_small_worst(dg, dr) if dr >= 0 else C()
        split = ctl(9 * dg) if dr >= 1 else C()   # a split to dh <= dg - 1 copies dh + 1 <= dg words: CTL(9 (dh + 1))
        c = base + scan + g + split
        if best is None or c.total() > best.total():
            best = c
    return best


def copy_fp(n): return ld(n) + st(n) + loopc(n)


def stage_e(d, shifts):
    """Stage E for deg G = d: shifts == 0 means d = 1 (no splitting); otherwise an upper bound with `shifts` shifts at degree d."""
    c = ctl(2) + copy_fp(d + 1) + ctl(2)
    for _ in range(shifts):
        c += root_iter_worst(d)
    c += ld(1) + SUB
    return c + ctl(2) + ctl(STAGE_BK)


def stage_g():
    """Two reference hashes, the comparison, the trial bookkeeping, the loop exit and the switch to stage H."""
    return C(unit=2 * 279) + ctl(6) + ctl(2) + ctl(2) + ctl(TRIAL_BK) + loopc(1) + ctl(STAGE_BK)


def stage_h():
    return 6 * (MUL + ctl(18) + ctl(12 * 64 + 5)) + ctl(STAGE_BK)


def stage_i():
    return ctl(FMT_PER_BYTE * OUTCAP + REPORT_LOOPS + SYS_WRITE + SYS_EXIT) + ctl(STAGE_BK)


def stage_init():
    return ctl(STAGE_BK) + ctl(PROLOGUE + CONSTS_GEN) + tw_init() + ctl(STAGE_BK)


def stage_a():
    return ctl(6 + TRIAL_BK) + FROM_U64 + ctl(STAGE_BK)


def ledger(d=1, e_shifts=0, ts=None, L=20, m=976562, t=17, d_row=None):
    """Stage rows of a run with one trial on the generic path, gcd degree d (stage E with e_shifts, stage F with ts;
    d_row: stage D's row if already evaluated)."""
    bits = [(EH >> (252 - t - i)) & 1 for i in range(253 - t)]
    rows = {}
    rows['init'] = stage_init()
    rows['setup'] = line_setup() + ctl(STAGE_BK)
    rows['A'] = stage_a()
    rows['B'] = stage_b(L) + ctl(STAGE_BK)
    rows['prep'] = stage_prep(L, m, t) + ctl(2) + ctl(STAGE_BK)
    rows['C'] = stage_c(L, bits) + ctl(STAGE_BK)
    rows['D'] = d_row if d_row is not None else stage_d.stage_d(L, m, d)[0]
    rows['E'] = stage_e(d, e_shifts)
    rows['F'] = stage_f(ts if ts is not None else ts_worst(32))
    rows['G'] = stage_g()
    rows['H'] = stage_h()
    rows['I'] = stage_i()
    return rows
```

### derive.py

SHA-256 `32f6f34a15d799f3607a87bcdde15e1247cfc21ebc072d2ffe3038f02e59f681`, 5551 bytes.

```python
"""Evaluate the operation count derived from the source (proof.md section 6) and write it to a JSON file.

Usage: python3 derive.py <S as hex> <out.json>
S is the root of g_1 given by the certificate (proof.md section 5.1); it fixes stage F's path when deg G = 1.  Prints the count of
the generic path with deg G = 1 and the claimed bound (every stage at its largest count over 1 <= deg G <= DMAX).
"""
import json
import sys

import model
import run_model as rm
import stage_d
from model import C, ctl, ld, st, loopc, MUL, SUB, ADD, SQR

KEYS = ('add', 'sub', 'mul', 'sqr', 'ld', 'st', 'ctl', 'unit')
DMAX = 8   # premise H2(c): deg G <= DMAX


def cnt(c):
    d = {k: c[k] for k in KEYS}
    d['total'] = c.total()
    return d


def ts_orders(a):
    """The orders 2^i found by fp_sqrt (main.c) for the square a: the path of its Tonelli-Shanks loop."""
    P = model.P
    z, x = pow(5, rm.Q_TS, P), pow(a, rm.Q1_TS, P)
    b, x = x * x % P * a % P, x * a % P
    m, seq = 32, []
    while b != 1:
        i, t = 0, b
        while t != 1:
            t = t * t % P
            i += 1
        y = z
        for _ in range(m - i - 1):
            y = y * y % P
        z = y * y % P
        x = x * y % P
        b = b * z % P
        m = i
        seq.append(i)
    assert x * x % P == a
    return seq


def prep_parts(L=20, m=976562, t=17):
    """stage_prep by component (model.stage_prep summed in the same order)."""
    n = 1 << L
    w = n >> 4
    nn = 15 * w
    k = nn + (1 << t) - m
    parts = [
        ("copy of the values, truncated inverse on O1 (coefficients of G* = n gt)", ld(nn) + st(nn) + loopc(nn) + model.tr_inv(L, 0)),
        ("checks: coefficients m+1..n'-1 zero, coefficient m nonzero", (nn - m - 1) * ctl(2) + ld(nn - m - 1) + loopc(nn - m - 1) + ld(1) + ctl(2)),
        ("f = rev_m(G*) to precision k+1 = %d" % (k + 1), ctl(k + 1) + ld(k + 1) + st(k + 1) + loopc(k + 1)),
        ("h = 1/f mod X^(k+1): Newton iteration, cyclic products of 2..2^18 points", model.series_inv(k + 1)),
        ("division by 1 - c1 X^w (recurrence h_i += c1 h_(i-w))", model.twiddle() + (k + 1 - w) * (MUL + ADD) + ld(2 * (k + 1 - w)) + st(k + 1 - w) + loopc(k + 1 - w) + ctl(k + 1 - w)),
        ("q reversed into B3, truncated forward on O1", ctl(k + 1) + ld(k + 1) + st(nn) + loopc(nn) + ctl(nn) + model.tr_fwd(L, 0)),
        ("values -q G* on O1, truncated inverse (coefficients of A0)", nn * (MUL + SUB) + ld(2 * nn) + st(nn) + loopc(nn) + model.tr_inv(L, 0)),
        ("G2: truncated forward of G* on O2", model.tr_fwd(L, 1)),
        ("Gi: batch inversion (prefix products, one inversion, back pass)", nn * (ld(1) + ctl(2) + MUL + st(1)) + loopc(nn) + model.FROM_U64 + 2 * SQR + MUL + model.fp_inv() + SUB + (nn - 1) * (ld(2) + MUL + st(1) + MUL + ctl(1)) + loopc(nn - 1) + st(1)),
        ("block factors (blk_scale of Gi and G2)", model.blk_scale(L, 1) + model.blk_scale(L, 0)),
        ("delta_j, j < 15", 15 * (model.twiddle() + SUB + st(1) + ctl(4)) + loopc(15)),
        ("trial bookkeeping after prep and the switch to stage C", ctl(2) + ctl(rm.STAGE_BK)),
    ]
    tot = sum((p[1] for p in parts), C())
    assert tot.total() == (model.stage_prep(L, m, t) + ctl(2) + ctl(rm.STAGE_BK)).total()
    return [(name, c.total()) for name, c in parts]


def main():
    sys.setrecursionlimit(10000)
    S, out = int(sys.argv[1], 16), sys.argv[2]
    seq = ts_orders(S)
    stage_d.STATS.clear()
    d_row, iters = stage_d.stage_d(20, 976562, 1)
    peak = stage_d.AR['peak']
    d_stats = {'%d|%s' % k: v for k, v in stage_d.STATS.items()}
    rows1 = rm.ledger(1, 0, rm.ts_path(seq), d_row=d_row)
    n1 = sum(v.total() for v in rows1.values())
    # D(d) differs from D(1) only in the driver's final Euclid loop (from degrees 82, 81)
    fe1 = stage_d.final_euclid(82, 81, 1).total()
    by_d = {}
    for d in range(1, DMAX + 1):
        dd = stage_d.final_euclid(82, 81, d).total() - fe1
        e = rm.stage_e(d, rm.SPLIT_CAP if d >= 2 else 0).total()
        by_d[d] = {'D_minus_D1': dd, 'E': e}
    f_cert = rows1['F'].total()
    f_worst = rm.stage_f(rm.ts_worst(32)).total()
    # the claim: every stage at its largest count over 1 <= deg G <= DMAX (stage D's is at deg G = 1, its longest final loop)
    assert all(by_d[d]['D_minus_D1'] <= 0 for d in by_d)
    e_max = max(by_d[d]['E'] for d in by_d)
    bound_rows = {k: v.total() for k, v in rows1.items()}
    bound_rows['E'] = e_max
    bound_rows['F'] = f_worst
    n_claim = sum(bound_rows.values())
    hgcd_sum = sum(own * n for byown in d_stats.values() for own, n in byown.items())
    drv_sum = sum(it[-1] for it in iters)
    res = {
        'S': '0x%064x' % S, 'ts_orders': seq,
        'rows_d1': {k: cnt(v) for k, v in rows1.items()}, 'N_d1': n1,
        'by_d': by_d, 'F_cert': f_cert, 'F_worst': f_worst, 'ts_worst_loop': rm.ts_worst(32).total(),
        'E_per_shift_worst': {d: rm.root_iter_worst(d).total() for d in range(2, DMAX + 1)},
        'bound_rows': bound_rows, 'N_claim': n_claim, 'arena_peak': peak,
        'd_hgcd_sum': hgcd_sum, 'd_drv_sum': drv_sum, 'd_rest': rows1['D'].total() - hgcd_sum - drv_sum,
        'final_euclid_d1': fe1, 'tw_init': rm.tw_init().total(), 'f_fixed': rm.stage_f(C()).total(),
        'd_iters': iters, 'd_stats': d_stats, 'prep_parts': prep_parts(),
        'b_parts': {'units': 2 * 983040 * 279},
        'fp_inv': model.fp_inv().total(),
    }
    json.dump(res, open(out, 'w'), indent=1)
    print('N(deg G = 1) =', n1, ' N_claim =', n_claim, ' arena peak', peak)


if __name__ == '__main__':
    main()
```

### stack_bound.py

SHA-256 `045938ea8a4cabb2715ee9508f4755ebcdd2a46c1eb9c765ee9c963d6bf1f44e`, 2523 bytes.

```python
"""Worst-case stack depth of the program from GCC's call graph with per-function stack usage (-fcallgraph-info=su).

Usage: python3 stack_bound.py <dir with the .ci files> <entry> <recursive function> <nested frames>
Every function's frame is GCC's bound (return address included).  The only recursion is hgcd calling itself; on the generic
path its nesting is at most <nested frames> frames (one per level of the recursion, k = 2^17 - 1 down to 31).
"""
import glob
import re
import sys
from functools import lru_cache


def load(d):
    size, edges = {}, {}
    for f in glob.glob(d + '/*.ci'):
        for line in open(f):
            m = re.match(r'node: \{ title: "([^"]+)" label: "[^\\]*\\n[^\\]*\\n(\d+) bytes \(([^)]*)\)"', line)
            if m:
                size[m.group(1)] = (int(m.group(2)), m.group(3))
                continue
            m = re.match(r'edge: \{ sourcename: "([^"]+)" targetname: "([^"]+)"', line)
            if m:
                edges.setdefault(m.group(1), set()).add(m.group(2))
    return size, edges


def bound(d, entry, rec, nested):
    """Returns (worst stack in bytes, [(function, frame bytes, repetitions, kind)] along the deepest chain, unknown callees)."""
    size, edges = load(d)
    unknown = sorted({t for s in edges.values() for t in s if t not in size})

    @lru_cache(None)
    def depth(f, left):
        """Deepest stack below and including f; left = remaining frames of rec (when f == rec)."""
        own = size.get(f, (0, ''))[0]
        best, path = 0, ()
        for g in edges.get(f, ()):
            if g == f:
                if g == rec and left > 1:
                    dg, pg = depth(g, left - 1)
                else:
                    continue
            elif g == rec:
                dg, pg = depth(g, nested)
            else:
                dg, pg = depth(g, 0)
            if dg > best:
                best, path = dg, pg
        return own + best, (f,) + path

    total, path = depth(entry, 0)
    run, prev = [], None
    for f in path:
        if f == prev:
            run[-1][2] += 1
        else:
            run.append([f, size.get(f, (0, '?'))[0], 1, size.get(f, (0, '?'))[1]])
        prev = f
    return total, run, unknown


def main():
    total, run, unknown = bound(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
    print('unknown callees', unknown)
    print('worst stack', total, 'bytes')
    for f, b, n, kind in run:
        print(f"  {f:28s} {b:>6} x {n}  ({kind})")


if __name__ == '__main__':
    main()
```

### validate_d.py

SHA-256 `80bbd59b18369799dbdc2ba112c7a3670bbec60595705a50b345ad997f0b5e54`, 1539 bytes.

```python
"""Compare the stage D model (stage_d.hg_gcd) with the instrumented C half-gcd on random inputs (gcd of degree 0).

Usage: python3 validate_d.py <tdt binary> <kmax> <da> [<da> ...]   (tdt = test_d.c built with -DTRCAP)
"""
import re
import subprocess
import sys

import stage_d


def model(da, kmax):
    L = 4
    while 15 << (L - 4) < da + 1:
        L += 1
    cap = 15 << (L - 4)
    for i in range(4):
        stage_d.PROF[i] = stage_d.C()
    c, _ = stage_d.hg_gcd(da, da - 1, kmax, cap, 0)
    return c.total(), [p.total() for p in stage_d.PROF], cap, stage_d.AR['peak']


def main():
    sys.setrecursionlimit(10000)
    binp, kmax = sys.argv[1], int(sys.argv[2])
    bad = 0
    for da in map(int, sys.argv[3:]):
        r = subprocess.run([binp, str(da), str(kmax)], capture_output=True, text=True)
        f = re.search(r'cap (\d+) ops (\d+) peak (\d+) words .* prof base (\d+) napply (\d+) dapply (\d+) matmul (\d+)',
                      r.stderr)
        cap, ops, peak, prof = int(f.group(1)), int(f.group(2)), int(f.group(3)), [int(f.group(i)) for i in range(4, 8)]
        mt, mp, mcap, mpeak = model(da, kmax)
        ok = mt == ops and mp == prof and mcap == cap and mpeak == peak and r.stdout.split()[0] == '0'
        bad += not ok
        print(f"da {da:>7} cap {cap:>7} C {ops:>14,} model {mt:>14,} diff {mt - ops:>6} prof {[a - b for a, b in zip(mp, prof)]}"
              f" peak {peak} model {mpeak} {'ok' if ok else 'MISMATCH'}", flush=True)
    print('mismatches', bad)


if __name__ == '__main__':
    main()
```

