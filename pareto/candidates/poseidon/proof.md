# Orchard Poseidon, r = 6: two free rounds on a line, odd part about a random centre, power-mod and half-gcd; one centre, the operation count of the executed program, success probability from the premises H-ONE and H-NORMAL

## 1. Claim

Target: `poseidon-orchard-r6-prefix-v1` (Orchard P128Pow5T3 over Pallas; full rounds 0–3, the six partial rounds 4–9, full rounds 60–63; state `[nk, rho, 2^65]`; digest = coordinate 0 in canonical 32-byte little-endian encoding). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is an algorithm (sections 2–4) with an operation count that bounds every run (section 6), a memory footprint (section 7) and a success probability derived from two score-critical premises, `H-ONE` (section 8.1, the fraction of centres at which the fixed digest polynomial has between 1 and 16 usable roots) and `H-NORMAL` (section 8.5, the normality of the Euclidean remainder sequence, which enters only the success probability). Section 8.2 derives the success probability from them. Every count of section 6 is read from the report of one execution of the shipped program at the target dimensions (three centres were executed, the third gave the collision of `certificates/`); the one-centre bound is assembled from that report by the rule stated in section 6.

* The algorithm (section 4): draw one centre `c` from two fresh random words, `c = (w1·2^256 + w2) mod p`; build the monic odd part `g_c` of the line polynomial (section 3) by `2^28` evaluations and one inverse transform; compute `R = S^((p−1)/2) mod g_c` by square-and-multiply on a spectral state (section 4.3); compute `G = gcd(g_c, R − 1)` by the half-gcd charged for the normal remainder sequence, with the quotient and return tests and the ABORT on any other case (section 4.4); if `1 ≤ deg G ≤ DMAX = 16`, isolate a root `S` of `G` in at most `Z = 64` rounds (section 4.5), take `s = sqrt(S)`, map `W = c ± s` back to two canonical pairs and verify both with the reference hash. One centre is tried (`K = 1`), on 20 threads whose work is summed; a verified collision ends the algorithm.
* `success_probability = 0.39009`: a lower bound on the probability, over the fresh random words of the algorithm and for the fixed target, that the one centre ends in a verified collision: `P ≥ 1 − (1 − q + δ)^K − K·(ε_coin + ε_iso) = q − δ − ε_coin − ε_iso` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 8.1), `δ = 0.003` (the allowance of the premise `H-NORMAL`, section 8.5), `ε_iso ≤ 2.371·10^−15` (the isolation lemma, section 8.4) and `ε_coin ≤ 65·p/2^512 ≤ 1.404·10^−76` (section 4.1). The value is `0.390099999999997628`, claimed floored at five decimals; it is at or above the organizer floor 0.39.
* `time_log2 = 35.45405` in target-compression units (`C(6) = 216 + 21·6 = 342` primitive operations per unit): `N_max = 16,097,398,375,981` operations bounds every run of the algorithm (section 6): `N_max = T_fixed + T_trial + E_cap + T_draw + T_abort`, where `T_fixed` (the twiddle tables, the line, the output and the report) and `T_trial` (stages A to G of one centre, with stage E at its executed value) are the counts of the executed run, `E_cap` replaces the executed stage E by its cap at `Z = 64` rounds and degree 16 (section 4.5), `T_draw = 63` is the centre draw and `T_abort = 1,000` a bookkeeping bound for a trial that ends in an ABORT. `log2(N_max / 342) = 35.454040`, rounded up at five decimals. The time bound holds for every remainder sequence (the prefix lemma of section 4.4); only the success probability depends on the premises. Thread control is charged inside the counts (section 4.2). The twiddle tables are built inside the run, so `preprocessing_log2 = 0`. No advice: `nonuniform_advice_log2_bytes = 0`.
* `memory_log2_bytes = 34.013` (`17,326,533,776` bytes, section 7): the whole statically linked executable image (text + data + bss; the bss holds the one static arena that serves every buffer of a trial) plus the main stack bound and the fixed stacks of the worker threads; the arena peak is reached in stage C and an aborted trial allocates a prefix of a normal trial's allocations. Normalized cost `35.45405 + (34.013 − 20) = 49.46705`.
* Executed evidence at the scale of the claim (section 9.1): the program was run once from `c = 1` on the fixed target; the centres `c = 1` and `c = 2` passed every normal-sequence test and ended with `deg G = 0` (no usable root), `c = 3` passed every test and gave the collision of `certificates/` with `deg G = 1`. The three remainder sequences of degree `m = 122,070,312` were normal (every one of the `129,934,595` tests of each trial passed; every quotient of degree 1). The per-centre charges agree to the operation up to the stages E, F and G of the successful centre, which is how `T_trial` is read (section 6).
* Prior entry. Our entry `a78f526e` is the same program (centres `c = 1, 2, 3` executed in order, a deterministic claim with every centre charged, normalized `51.22163`). This entry changes three things: the twiddle table is sparse (`L/32 + 1` entries, section 4.2; memory −0.16 bit), stage D carries the normal-sequence tests and stage E the degree test (sections 4.4, 4.5; `+2` operations per division and per half-gcd call), and the claim is the one-centre form with the premises `H-ONE` and `H-NORMAL`, which charges one centre. The run was executed again from the start with the new program and every count is of the new run.
* Credit. The construction (two free rounds on a line, the odd part about a centre, the gcd against `S^((p−1)/2) − 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022(3)) in the form of Jbenisek's entries (r = 1 … 22 on this track), whose charging rules (section 4.2 follows their section 4.2) and stage structure this package adopts. The one-centre form of the claim with the premise `H-ONE` is Jbenisek's (his r = 6 entry `c318f442` and his r = 13 … 22 entries); the premise `H-NORMAL` with the quotient and return tests and the ABORT is bradcush's (entries `e6dcb600`, `1aa56884`); the split of the allowance (`q = 0.3931`, `δ = 0.003`) is cryptogakusei's (entry `4888e783`); the organizer-run normality and one-centre tests follow the form of gta6rp's entry `bef31fdd` and Jbenisek's `c318f442`. The monodromy computations that support `H-ONE` at two and three layers (section 8.3) are reported by those entries; this package cites them as text and does not reproduce them. All of these were read as text; no source of another entry was compiled, run or copied. The program, its transform plan (one length `L = 2^27` throughout; the state of the powering kept as its values at the even and at the odd `2L`-th roots of unity), its squaring step (section 4.3: a Montgomery reduction modulo `g` with the auxiliary modulus `R = x^L − 1`, four length-`L` transforms per step, no precomputed reciprocal), its half-gcd with the memory cap, its sparse twiddle table, its thread partition, its instrumentation and every count are this package's own, as are the experiment program of section 9.4 and the survey runs of section 9.3.
* The collision in `certificates/` is the output of the executed run (centre `c = 3`), checked at the selected target with the organizer's digest.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p ≡ 2 (mod 5)`, so `gcd(5, p−1) = 1` and `x ↦ x^5` is a bijection of `F_p` with inverse `x ↦ x^e`, `e = (4(p−1)+1)/5`. `M` is the deployed 3×3 MDS and `c_{i,k}` the deployed round constant `k` of round `i` (read from the organizer's constants file; never regenerated). `p − 1 = 2^32 · 3 · q′`.

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5`, the state after round 0 is `M (U, V, K)^T`. `(nk, rho) ↦ (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e − c_{0,0}`, `rho = V^e − c_{0,1}`); `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`. The program uses the line `j = 0`, `I = {1, 2}`: let `Q = (U_Q, V_Q)` solve `x_1 = x_2 = 0` (the 2×2 minor `M_{10} M_{21} − M_{11} M_{20}` is nonzero on the deployed constants; checked by the program, which stops otherwise), `(a, b) = (M_{01}, −M_{00})`, `(U, V) = Q + τ (a, b)`. Then `x_0 = κ` is constant and `x_i = d_i τ` for `i ∈ I`, `d_i = M_{i0} a + M_{i1} b`. With `W = τ^5` the round-1 S-box output is `v0 + W v1`, `v0 = κ^5 e_0`, `v1 = d_1^5 e_1 + d_2^5 e_2`; after the round-1 MDS and the round-2 constants the state is `α + β W`, `α = M v0 + c_2`, `β = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), 4–9 (partial) and 60–63 (full) put twelve S-box layers on top of an affine map; the digest is row 0 of the last MDS applied to the result. So the digest equals `F(W)` with `deg F ≤ 5^12 = D = 244,140,625`. Propagating leading coefficients through the twelve layers (a partial round raises only coordinate 0 to the top degree; the MDS mixes the top-degree coordinates with nonzero coefficients on the deployed constants) gives the leading coefficient `f_D = 0x34bd5acc9093858597cb29a9ca5405d90d50343d4924ce1be148b06792258969` ≠ 0, so `deg F = D` exactly. (The program re-derives this: stage B tests that the leading coefficient of `g_c` is nonzero and normalises by it.) For random `τ`, `F(τ^5)` equals the organizer's digest of the canonical inputs built from `τ` (checked by the development runs of section 9.2 at r = 1 … 4, and by the verification of stage G at r = 6).

2.4 Collision criterion. If `W_1 ≠ W_2` and `F(W_1) = F(W_2)` then `τ_1 ≠ τ_2`, hence `(U, V)_1 ≠ (U, V)_2` (`(a, b) ≠ 0`), hence the canonical pairs differ, and the digests are equal. Every `W ∈ F_p` is `τ^5` for exactly one `τ`.

## 3. Odd part about a centre

For a centre `c ∈ F_p` write `F(c + s) − F(c − s) = 2 s g_c(s^2)`. Since `D = 2m + 1` with `m = 122,070,312`, `g_c` has degree exactly `m` and leading coefficient `f_D` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is `W_1 = c + s`, `W_2 = c − s` with `s ≠ 0`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The usable roots are the roots of `G = gcd(g_c, S^((p−1)/2) − 1)`: `S^((p−1)/2) − 1` is squarefree with the nonzero squares as its roots, so `G` is a product of `deg G` distinct linear factors over `F_p` whose roots are exactly the nonzero square roots of `g_c`.

Construction of `g_c` by evaluation. `H = 2^27 = 134,217,728 ≥ m + 1` divides `p − 1`. With `ω` a primitive `H`-th root of unity and `ζ^2 = ω`: `g_c(ω^i) = (F(c + ζ^i) − F(c − ζ^i)) / (2 ζ^i)`, `i < H`. One inverse transform of size `H` returns the coefficients of `g_c` exactly (the `H − m − 1` top coefficients are zero). The `2H = 268,435,456` evaluations of `F` are each charged as one target-compression unit (`342` operations), although a line evaluation (affine start, twelve layers, one MDS row) is a strict subset of a reference permutation; the loop work around them is charged on top.

## 4. The algorithm (one centre) and the executed program

### 4.1 Stages, coins and the stopping rule

```
init:   twiddle tables (built at run time, charged)
setup:  the line (Q, (a, b), d_1, d_2, κ, α, β)
one trial (K = 1):
  A  c := (w1·2^256 + w2) mod p from two fresh random words (63 operations; the executed run: c := i, one conversion)
  B  g := g_c by section 3 (2H evaluations, one inverse transform of size H = L, leading-coefficient test), and the
     two spectra of stage C: 1/g at the even points (batch inversion), g at the odd points (twist, one transform)
  C  R := S^((p−1)/2) mod g (left-to-right square-and-multiply on the spectral state, section 4.3); g made monic
  D  G := gcd(g, R − 1), monic: the half-gcd with transform products (section 4.4), charged for the normal remainder
     sequence; every division tests its quotient degree, every call its return, and on any other case the trial ends (ABORT)
  E  if deg G = 0 or deg G > DMAX = 16: the trial ends. Otherwise isolate a root S of G (section 4.5), at most Z = 64
     rounds, each with one shift drawn from two fresh random words; if none within Z rounds: the trial ends
  F  s := sqrt(S) (Tonelli–Shanks, 2-adicity 32); W_1 = c + s, W_2 = c − s; τ_i = W_i^e; (U, V)_i = Q + τ_i (a, b);
     nk_i = U_i^e − c_{0,0}, rho_i = V_i^e − c_{0,1}
  G  verify: the two reference hashes (342 each) are equal and the pairs differ → output; otherwise the trial ends
H  output: the two pairs, the digest and the centre in canonical hexadecimal
I  report: the ledger, one write, exit
```

Coins. The only randomness of the algorithm is the cost model's random-word primitive (one operation per 256-bit word), fresh and independent. Every random field element (the centre of stage A and each shift of stage E) is drawn from two fresh words `w1, w2`: each is reduced modulo `p` by three conditional subtractions (`2^256 < 4p`), and `x = (w1 mod p)·(2^256 mod p) + (w2 mod p)` in `F_p`, that is `x = (w1·2^256 + w2) mod p` with `w1·2^256 + w2` uniform on `[0, 2^512)`. There is no rejection and no retry. A draw is charged `63` operations: per word 1 random-word operation, 1 load, 1 store, 3 control, the reduction 9 and its loop control 11 (26 per word, 52 for two), two Montgomery conversions 2, the load of the constant `2^256 mod p` 1, one multiplication 1, one addition 1, the entry 2, the two addresses 4. At most `1 + Z = 65` draws (130 words) per run. With `2^512 = Q·p + ρ`, each residue has `Q` or `Q + 1` preimages, so one draw is within statistical distance `ρ(p − ρ)/(p·2^512) ≤ p/2^512 = 2^−258.0` of uniform on `F_p`; the 65 draws are independent, so the joint distribution of all the coins of a run is within `ε_coin = 65·p/2^512 ≤ 1.404·10^−76` of the distribution with every draw exactly uniform (total variation is subadditive over independent components). The success bound of section 8.2 is stated for exactly uniform draws and transferred to the written sampler by `ε_coin`.

The executed instantiation. The shipped program (section 11) is the algorithm above with its coins fixed, so that the run is reproducible: stage A sets `c := i` for the trials `i = 1, 2, 3, …` (one Montgomery conversion instead of the draw; the draw's 63 operations are added to the bound in section 6), the loop continues to the next centre when a trial ends without a collision (a `MAXTR = 64` guard), and the shifts of stage E come from a fixed generator (xorshift64 seeded with the constant 1; no shift was drawn in the executed run, since `deg G = 1` at the successful centre). Everything else, the stages B to I, the tests of stage D, the degree test of stage E, the charges and the memory, is the algorithm as claimed. The charge of the stages A to D does not depend on the value of `c` (section 6: the three executed centres agree to the operation), and the charges of E, F and G are bounded in sections 4.5 and 6; so one execution from `c = 1` measures the per-centre cost, and the one-centre bound of section 6 is read from it. The executed centres are also the full-scale evidence of section 9.1 for the premises.

Determinism and threads. The program takes no input and reads no file. Every trial is executed to its end (or to its ABORT) and counted by the same counters; every charged operation belongs to exactly one stage and one trial (the stage bookkeeping closes the previous stage as it opens the next). The work of every parallel loop is partitioned into fixed chunks decided by the loop length and the thread count alone, never by timing, so the executed operations, their count and the result are the same for every thread count; section 6 reports the thread count used.

### 4.2 Machine model and charging rules

Every item below is counted by the executing code at the statement that executes it (`orch.h`: the counters `X`, one set per thread; the macros `LD`, `ST`, `CTL`, `LOOPC`, `FOR8`); nothing in sections 6 and 7 is estimated from another run. The complete source is in section 11.

* Canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each (`fp_add`, `fp_sub`, `fp_neg`, `fp_dbl`, `fp_mul`, `fp_sqr` in `orch.h` increment the counter themselves). Inversion and exponentiation are expanded (`fp_pow` in `fp.c`: left-to-right, every squaring and multiplication counted, 9 control operations per exponent bit and 7 per bit of the top-bit search; `fp_inv` is `fp_pow` with `p − 2`; `fp_sqrt` is Tonelli–Shanks with the tests of its loops charged next to them). Every Montgomery conversion (`fp_from_u64`, `fp_from_limbs`, `fp_to_limbs`: the centre, the random words, the output) is one counted multiplication. The constants of `consts.h` are stored in Montgomery form.
* Load or store of a 256-bit element of an array: 1 each, together with one address-formation operation: `LD(n)` adds `n` to the load counter and `n` to the control counter, `ST(n)` likewise.
* Every loop that is not unrolled: `3n + 2` control operations for `n` iterations (index update, bound test, branch; one test and branch on exit): `LOOPC(n)` after the loop, or `CTL(3)` inside the body and `CTL(2)` after it. The macro `FOR8` (`orch.h`) writes its body eight times per pass in the source (genuinely unrolled): 1 for the bound `n & ~7`, 3 per pass of eight, 2 on exit, then the 0 to 7 remaining elements in a plain loop (3 each, 2 on exit). Its sites are the pointwise loops, the twist, untwist and `x`-value loops of `ntt.c` and the matrix loop `mat2_chunk` of `hgcd.c`. Every other `for` or `while` loop of the source is a real loop charged `3n + 2`.
* Every other executed index or control operation: 1 each (shift, mask, or, add, subtract, compare, conditional branch, select, pointer formation), added with `CTL(k)` next to the statement, as the comments show; data-dependent tests are charged per executed test. The index code contains no multiplication or division except by powers of two.
* Transform kernels are generated straight-line code (`gen_kern.py` is part of the source; its output `kern.h` is listed). A block kernel for `k` layers (`k = 1 … 4`; `2^k ≤ 16` data words `x[]`) has no loop and no branch: each butterfly is the literal statements `fp_sub`, `fp_add`, `fp_mul` (`BF`/`IB`; two operations and no multiplication for `BFN`/`IBN`, the twiddle 1 of the block `j = 0`), every twiddle load is a literal statement with its own charge (the first twiddle of a layer: its address, `CTL(2)` forward (shift, add) or `CTL(3)` inverse (shift, subtract, add), `CTL(1)` / `CTL(2)` in the block `j = 0` whose twiddle addresses are pass constants, and `LD(1)`; every further twiddle of the layer: `LD(1)`, a running-pointer step), and the `2^k` words of the block are loaded and stored with `LD(2^k)` / `ST(2^k)`. The twiddle table is sparse: it holds `w_T^(16k)` for `k = 0 … T/32` (`T = L = 2^27`, the largest transform length; `L/32 + 1` elements), which serves every pass whose twiddle step `2^(l0 + sh)` (`l0` the first layer of the pass, `sh = 27 − n` for a transform of length `2^n`) is at least 16. The one pass below that step, the first pass (`l0 = 0`) of a transform of length `≥ 2^24`, uses the chained kernels (`dif4c`, `dit4c`, `ff4c`, the same 16-word blocks): the twiddles of its block `j > 0` are `(A·c_u)^(2^i)` (`i` the layer, `u` the twiddle number) with `A = w_T^(j·2^sh)` and `c_u = w_16^u`, and the kernel computes them instead of loading them: the block indices `q = (j·2^sh) div 16` and `l = (j·2^sh) mod 16` (`CTL(3)`); forward, `A = TW[q]·LOW[l]` (`LD(2)`, one multiplication), each further twiddle of a layer is one load of the chain constant (`LD(1)`) and one multiplication, one squaring turns the last twiddle of a layer into the first of the next (up to sign; the layers alternate direction), and a negative twiddle is used by the butterfly `BFM` (three operations, like `BF`); inverse, the first twiddle of layer `i` is `TW[T/32 − (q << i)]·LOWI[i][l]` (`CTL(2)`, `LD(2)`, one multiplication) and the further twiddles of the layer are chained in the same way. The tables `LOW` (`w_T^l`, 16 entries), `LOWI` (`w_T^(−2^i·l)`, 64 entries) and the five chain constants are built in `init`. The chained kernels use the same 18 words: the chain constant is loaded into the temporary `t_`. The block `j = 0` of every pass uses the kernel `*z` (its twiddles are pass constants in the sparse table). A pass (`PASS_FN` in `ntt.c`) is the group loop and the block loop around the kernel, with the charges written in the macro (per pass 6 + 2, per group 3 + 2 + 8 + 2 + 2 (+ 1 when the block `j = 0` is peeled), per block 3 + 1); `run_pass` charges the pass constants (`8 + 6k`), the selection of the pass function (4) and the chunking (4). A transform of length `2^n` is the plan `4, 4, …, n mod 4` layers per pass (`plan`, charged). The fused kernels of the Montgomery step (`fl*`, `ff*` in `kern.h`) contain the layers of the last forward pass, the pointwise operation of the step on each of the `2^k` words (its field operations, and `LD(1)` per operand loaded and `ST(1)` per word stored, written in the macros `FL_*` of `ntt.c`) and the layers of the first inverse pass, with the same per-word and per-twiddle charges; `ff*` fuses the last inverse pass, the two-level twist or untwist factor (2 multiplications and `LD(1)` per word, `LD(1)` per block for the block factor) and the first forward pass.
* Working registers (declared assumption): a kernel keeps its block of at most 16 data words, the twiddle operand `w` and one temporary `t_` in registers: 18 words of 256 bits. The bodies of the pointwise loops keep at most three working words. Strides, shift counts, base pointers and loop indices are integer registers (their updates are charged as control operations; they carry no memory-access charge). Everything else is loaded and stored with its charge. A machine with fewer registers would cost more; this is the one structural assumption of the model.
* Threads (`par.c`). A parallel loop of `n` elements is cut into `nch` fixed chunks, `nch` the largest power of two `≤ n / 256` and at most 256 (0, that is serial, below 4,096 elements); `nch` depends on `n` only. The active threads are `min(T, nch)` for the thread count `T`; thread `t` runs the contiguous chunk range `[t·nch/T, (t+1)·nch/T)`. Each thread counts into its own thread-local counters, which the main thread adds after the region: the count is the work summed over all processors, as the cost model requires, never a latency. Declared charges per region: `TH_START + TH_JOIN = 200` per active thread and `TH_CHUNK = 10` per chunk (the dispatch arithmetic of the chunk bounds). The workers are a persistent pool woken per region (a generation counter; a worker that has spun 4,000 times sleeps on a condition variable); the 200 per thread and region is the declared stand-in for that wake and completion signal, and for the one-time creation of the 19 workers in the first region. The kernel's scheduling work for a sleeping worker is not in the model. Everything inside a chunk is charged by the rules above. Section 4.5 states how the count depends on `T`.
* Unit charges: every line evaluation `F(W)` of stage B (`tail_eval`: the affine start, twelve S-box layers, one MDS row) and each of the two reference hashes of stage G is charged `C(6) = 342` operations as one target-compression unit, instead of its (smaller) expanded arithmetic; the counters of the field operations inside are reset to the snapshot before the call (`line.c`). Nothing else is charged as a unit. The loop around the evaluations (the point, the two sums, the difference, the quotient, the store, the control) is charged on top.
* The allocator (`arena.c`): every buffer is a block of one static arena in the bss, LIFO (`xalloc` 15 control operations, `xfree` 9, charged where written; no header, the block offsets are a separate static array). Nothing is mapped from the kernel at run time except the stacks of the worker threads (section 7).
* Small fixed work (the line setup, the back-map, the square root, the verification glue): on top of every field operation, 2 loads, 1 store and 6 control operations plus the 3 address operations (`bound_since`, `line.c`), a bound.
* The random words of stage E (`root.c`, only executed when `deg G ≥ 2`): 47 control operations per 254-bit word (four xorshift64 steps, mask, limb assignments) plus one conversion.
* Stage bookkeeping: `STAGE_BK = 1,000` control operations per stage opened (a bound on reading the ten counters, the row search by name, the subtractions, the peak reset; under 400). `PROLOGUE = 500`: argument parsing, the environment test, the thread count, the degree computation. `CLOCK_READS = 400`: the two clock reads (start and end) through the vDSO.
* Progress lines (`progress` in `main.c`, written to the standard error stream as the run proceeds: one after init, and per trial one after stage B, one every 32 steps of stage C, one after stage C, one after stage D and one after stage G): each is charged a fixed `PROG_CHARGE = 400 · 256 + 10,000 + 8 · 256 = 114,448` operations in the stage in which it is executed (formatting of at most 256 bytes at 400 per byte, the clock read inside it, and one `write` system call at 10,000 plus 8 per byte). These lines carry no result; they let the run be watched.
* Output (stages H and I): stage H converts `nk1`, `rho1`, `nk2`, `rho2`, the digest, the centre and the root `S` out of the Montgomery representation (7 multiplications) and encodes each as 64 hexadecimal digits (`enc_hex`: 12 operations per digit and 5 per call). Stage I charges, before the report is formatted, everything the program executes after the last algorithm step, inside `N`: the formatting of the whole report buffer of `OUTCAP = 8,192` bytes at `FMT_PER_BYTE = 400` per byte, charged in full whatever it holds (`3,276,800`; the C library `vsnprintf` costs well under 400 operations per output byte); the loops of the report over the stage and trial rows and the `log2` (`REPORT_LOOPS = 20,000`, a bound); the single `write` of the buffer to the standard output (`SYS_WRITE = 10,000 + 8 · 8,192 = 75,536`); the exit (`SYS_EXIT = 10,000`); `CLOCK_READS`; and the bookkeeping of the closing of stage I (`STAGE_BK`). The program ends with exit status 3 and no collision line if the buffer overflowed, which the report shows did not happen. Stage I of every run is therefore the constant `3,384,736`.
* The meter itself (the increments of the counters, the per-component meter of stage D, the stage rows) is how the rules are applied, not a step of the program, and is not charged. The C library is statically linked (section 7); the only system calls of the run are the `write` calls above, the clock reads, the creation of the 19 worker threads at the first parallel region (`clone`; covered by the declared start charges, see the thread item; a real thread creation costs on the order of `10^4` instructions, so the 19 creations are below `10^6` operations, that is below `2^-23` of `N`), the futex waits and wakes of idle workers, and the exit.

### 4.3 Stage C: the powering on a spectral state (Montgomery reduction with `R = x^L − 1`)

Notation. `L = 2^27` (`m + 1 ≤ L`, here `L − m − 1 = 12,147,415`), `N = 2L`, `ω` a primitive `L`-th root of unity, `ζ` a primitive `N`-th root with `ζ^2 = ω`. The even points are `ω^k = ζ^(2k)`, the odd points `ζ^(2k+1)`, `k < L`. For a polynomial `f` of degree `< L`, `DIF(f)` is the vector of its values at the even points (bit-reversed order) and `DIF(twist(f))` the vector of its values at the odd points, where `twist(f)(x) = f(ζx)`; both are one length-`L` transform (`ntt.c`), and the inverse maps are the inverse transform followed, for the odd points, by the untwist (`ζ^(−j)`, with the `1/L` of the inverse transform folded in). `R = x^L − 1` is `0` at the even points and `−2` at the odd points.

Exponent. `(p − 1)/2` has its top bit at position 253. The program starts from the monomial `x^v` with `v = 2^j`, `j` the largest value with `2^j < m` and the bits `252 … 254 − j` of the exponent zero such that the Newton precision `P = v + L − m + 1` fits in `L/4` (at `r = 6`: `j = 24`, `P = 28,924,633`), and then runs one step per remaining bit, `253 − j = 229` steps, 45 of them with the multiplication by `x` (bit 1).

State. The residue `a` (`deg a < m`) is kept as `b = a · R mod g` (`deg b < m`), and `b` is kept as its two spectra `E = DIF(b)` and `O = DIF(twist(b))` (`2L` values; in the program both carry the fixed scale `μ = −1/2` and `E` is kept without the last pass of its transform, which the first fused pass of the next step completes). One step maps `b` to `Mont(b^2) = b^2 R^(−1) mod g` (or `Mont(x b^2)`):

1. `ŝ := E^2`, `O^2` pointwise, and times the values of `x` at those points when the exponent bit is 1. Since `deg s = deg(x b^2) ≤ 2m − 1 < N`, the `2L` values determine `s` exactly.
2. `t := −s · g^(−1) mod R`: at the even points `R = 0`, so `t̂_e = −ŝ_e / ĝ_e` pointwise with the stored `1/ĝ_e` (stage B; `g` has no root among the even points, tested there). One inverse transform gives the coefficients of `t` (`deg t < L`).
3. One twisted forward transform gives `t̂_o`, the values of `t` at the odd points.
4. `u := s + g · t` is divisible by `R` by construction, `deg u ≤ m + L − 1`, so `r := u / R` has `deg r ≤ m − 1` and `r ≡ s · R^(−1) (mod g)`, i.e. `r = Mont(s)`. At the odd points `R = −2`, so `r̂_o = (ŝ_o + ĝ_o · t̂_o) / (−2)` pointwise with the stored `ĝ_o` (stage B); the `−1/2` is the scale `μ` of the state. This is the new `O`.
5. One inverse twisted transform gives the coefficients of `r` (`deg r < m ≤ L`, so the `L` odd values determine `r`; the slots `m … L − 1` are zero), and one forward transform gives the new `E`.

Four length-`L` transforms per step, two of them with the twist or untwist folded into their outer passes, and the pointwise work of steps 1, 2 and 4 fused into the adjacent passes (`mont_step_f` in `powmod.c`, `ntt_fused_last`, `ntt_fused_first` in `ntt.c`): `4(np − 1)` sweeps over the `L` words per step with `np = 7` passes per transform. Nothing is precomputed beyond the two spectra of `g` (stage B) and the twiddle tables (init); no reciprocal of `g` is stored. Correctness of one step was checked against NTL's `SqrMod` on random moduli and on the real `g_c` of `r = 1`, and the whole stage against NTL's `PowerXMod` at `r = 1` (development runs, section 9.2).

Start value. `b_0 = x^v · R mod g` is obtained from `Q = floor(x^(v+L) / g)` by one Newton reciprocal of precision `P` (`series_inv` in `poly.c`, products by cyclic transforms): `Q g = x^(v+L) − ρ`, so `b_0 = ρ − x^v` up to the sign conventions of the code, built directly in the spectral form (`powmod.c`, the comment at the top). At `r = 6` this runs inside the buffer `E` (no extra memory). End: one reduction without the square gives `a = Mont(b) = S^((p−1)/2) mod g` as coefficients; the program checks that the slots `m … L − 1` are zero and stops with an error otherwise; `g` (monic) is recovered from its odd spectrum for stage D (one inverse transform, one scaling, and a check that the leading coefficient is 1).

All charges of this stage depend on `m`, `L` and the exponent only, not on the coefficients.

### 4.4 Stage D: the half-gcd, charged for the normal remainder sequence, with the tests and the ABORT

Input: `U = g` (monic, degree `m`) and `V = R − 1` (`R = S^((p−1)/2) mod g`, degree `< m`), both in buffers of `L` slots. Output: `G = gcd(U, V)`, monic, and its degree, or the ABORT.

`hgcd(U, V, d)` (`hgcd.c`, the degree-reduction form of the recursive half-gcd as in Thomé and in NTL's `HalfGCD`): it returns a `2 × 2` polynomial matrix `M`, a product of factors `[[0, 1], [1, −q]]`, such that `M (U, V)^T = (U', V')^T` are consecutive remainders of the Euclidean sequence with `deg U' > deg U − d ≥ deg V'` (the identity if `deg V ≤ deg U − d` already); only the top `2d − 1` coefficients of `U` and `V` are read (`s = deg U − 2d + 2` low coefficients are dropped). For `d ≤ HG_THR = 32` the base case is iterative Euclid on the truncated pair, building `M` as it goes; a division step with a quotient of degree 1 is the scaled step `divstep1`: with `v` the leading coefficient of `V`, `s U − (A x + B) V` with `s = v^2`, `A = v·lc(U)`, `B = v·U_(n−1) − lc(U)·V_(d−1)`, which is `v^2` times the true remainder (a unit multiple: the degree sequence, hence the gcd, is unchanged; the matrix rows are updated with the same scalars `mat_qstep1`), so the base case performs no field inversion. For `d > 32`: `M_1 = hgcd` on the top parts with `d_1 = ceil(d/2)`; `(U_1, V_1) := M_1 (U_1, V_1)` by cyclic transform products (`mat_apply`; the high coefficients cancel, so the cyclic result is exact); one division `U_1 = Q V_1 + r` (the scaled step when `deg V_1 ≤ 2,048`, else `poly_divrem_ip`); `M_2 = hgcd(V_1, r, d_2)` with `d_2 = deg V_1 − deg U_1 + d`; `M = M_2 · [[0, 1], [1, −Q]] · M_1` (`mat_mul`: schoolbook when an entry degree is below 16, else transform products of length `2^ceil(log2(d_a + d_b + 1))`).

The outer loop (`gcd_lean`) repeats, while `deg U > GCD_THR = 128`: `d = min(ceil((deg U + 1)/2), DMAX)` with `DMAX = L/16` (a memory bound: the matrix and the scratch of one call stay below the stage-C peak), `M = hgcd(U, V, d)`, `(U, V) := M (U, V)` in place on the full polynomials (`mat_apply`: one cyclic product of length `2^ceil(log2(deg U' + 1))` when that is at most `LMAX = L/4`, otherwise blocked overlap-add from the top block down, in place, with a small overflow array), then one division and the shift `(U, V) := (V, U mod V)`; at or below degree 128, classical Euclid; finally the last nonzero remainder is made monic (one inversion, `deg + 1` multiplications).

Division (`poly_divrem_ip`): schoolbook when the quotient or the divisor has degree below 64; otherwise the reversed Newton identity `rev(q) = rev(a) · rev(b)^(−1) mod x^(deg q + 1)` with the reciprocal by Newton iteration (`series_inv`) and the remainder by one cyclic product. Products by transforms (`poly_mul_cyc`) are two forward and one inverse transform of the stated length with the `1/length` folded into one input.

The normal-sequence tests (`NTEST` in `hgcd.c`, 2 control operations each, charged where they stand). The stage is charged for the normal remainder sequence of `(g, R − 1)`: `deg(R − 1) = m − 1` and every quotient of degree 1, down to the gcd (the premise `H-NORMAL`, section 8.5). Four kinds of test make every other sequence end the trial: (a) the entry test `deg V = deg U − 1` (`gcd_lean`); (b) the quotient test: every division (each step of the base case, the division of a call, the division of each repetition of the outer loop, each step of the classical tail) tests that its quotient has degree 1 before it does any work beyond reading the two degrees; (c) the return test: every call `hgcd(U, V, d)` is tested on return by its caller for having removed exactly its parameter, `deg m_11 = d − 1` (the identity passes exactly when `d = 1`); (d) a zero remainder met inside a call or in the outer loop (the gcd reached above the classical tail) fails the test that follows it. On a failed test the trial ends (ABORT): `G_info.aborted` is set, the buffers of the call chain are released by the same `xfree`/`mat_free` statements the normal path executes, `gcd_lean` returns `−2` and the trial is over (status 20 in the trial table); no later stage runs.

Prefix lemma. While every test so far has passed, every quotient so far had degree 1, and then every length, recursion parameter and allocation of the stage equals that of the normal sequence: each call splits at `d_1 = ceil(d/2)` and drops `s = deg U − 2d + 2` coefficients, after a passed return test the degrees after `M_1` are `deg U_1 − d_1 + 1` and `deg U_1 − d_1`, the division has a degree-1 quotient, `d_2 = d − d_1`, and the outer parameter `d = min(ceil((deg U + 1)/2), DMAX)` is a function of `deg U`, which on the normal sequence is a function of `m` and the number of divisions so far. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops short of its parameter and the return test of its caller fails before the result is used; a zero remainder fails the test that follows it. So an aborted trial executes a prefix of the operation sequence and of the allocation sequence of the normal case and then releases its buffers; its charge and its arena peak are at most those of a normal trial, which is what section 6 charges (`T_abort = 1,000` is added for the bookkeeping of the early return). A normal sequence whose gcd has degree above `GCD_THR = 128` meets its zero remainder above the classical tail and is also ended by test (d); such a trial fails the degree test of stage E anyway (`deg G > 16`), so the success bound of section 8.2 is unaffected: a trial with `1 ≤ deg G ≤ 16` and a normal sequence passes every test (its zero remainder appears in the classical tail, after the last division, whose quotient has degree 1).

Every executed operation of the stage is charged where it is written (section 4.2); the per-component meter (`G_info`) only groups the same counters. In the executed run every test passed at every centre: the report line `STAGED` shows `quot_deg_ge2 = 0`, `max_qdeg = 1`, `tests = 129,934,595`, `aborted = 0` (section 6), and the per-trial table shows `deg G ≥ 0` at every centre (an ABORT would read `−2`).

### 4.5 Stage E (root isolation, the cap) and the thread count

Stage E runs only when `1 ≤ deg G ≤ DMAX = 16` (`DMAX_E` in `main.c`; a trial with `deg G = 0` or `deg G > 16` ends there, 2 control operations for the test). When `deg G = 1` the stage reads `S = −G_0` (one negation). When `deg G ≥ 2` (`root.c`): equal-degree splitting, `F = gcd(G, (x + δ)^((p−1)/2) − 1)` for a shift `δ` drawn from two fresh random words, keeping the smaller of `F` and `G/F` when `0 < deg F < deg G`, with schoolbook arithmetic; at most `Z = 64` rounds; the degree never increases, and `G` is squarefree and splits over `F_p` (section 3). The lemma of section 8.4 bounds the probability that 64 rounds fail to isolate a root by `ε_iso ≤ 2.371·10^−15`.

The cap. In the ledger of section 6 the executed stage E is replaced by `E_cap = Z × E_round = 64 × 3,000,000 = 192,000,000` operations. `E_round = 3,000,000` is above the charge of any one round at degree 16: a round at degree `d` is one draw, the setup of `x + δ`, the powering `(x + δ)^((p−1)/2) mod G` (252 squarings and the multiplications of the exponent bits, each a schoolbook product of two polynomials of degree `d − 1` and one schoolbook division by `G`, whose charges are functions of the degrees alone: `poly_mul_school` and `poly_divrem_ip` never skip a coefficient), the gcd of `G` and `h − 1` (at most `d` schoolbook divisions, each charged at most as the division of degree `d` by degree `d − 1`) and the division `G/F` or the copy of `F`; every one of these charges grows with `d`, so the round at degree 16 is the most expensive, and its charge is bounded by the sum of the stated maxima. Measured: over 200 random degree-16 inputs (`tests/t_root.c`, line `ROOTCAP` of `tests/final/unit.txt`, the same code), the largest charge of one round was `2,682,993` and the largest whole isolation `12,380,222` (12 rounds); `E_round = 3,000,000` is the stated bound with a 12 % margin above the largest round observed, which included a split and the division `G/F`. `E_cap` is `1.2e-05` of `N_max`.

Thread count. The chunking of every parallel loop depends on the loop length only (section 4.2), so the set of executed operations and the result are the same for every thread count `T`; the only counter that depends on `T` is the declared thread charge, `200 · Σ_regions min(T, nch) + 10 · Σ_regions nch`. The development runs of section 9.2 verify this: at `r = 1` and `r = 3` the runs with `T = 1`, `8` and `20` have identical counters of every type except the thread charge, which equals that formula in each case (`tests/cmp_ledgers.py`). The report line `NOTHREAD` gives the total without the thread charges and the two sums. The claimed bound uses the counts with the thread charges of the executed `T = 20` run (the cost model charges total work; one thread would charge less).

## 5. Why the output is a collision

By sections 2–3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) ≠ 0`, `F(c+s) = F(c−s)`, `c+s ≠ c−s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes with an independent implementation of the full reduced permutation and compares them; the program reports success only if they are equal and the pairs differ. Independently of the program, the pair in `certificates/` is checked by the organizer's digest function; the digest `0x28aefdb3c3584417414dc9761b8059e53ce78d0df90a8e9df17e4832fd416eb7` is printed by the run.

## 6. Ledger: the one-centre bound, read from the executed run (primitive operations; `C(6) = 342`)

The counts are the instrumented totals of one execution of the shipped source (section 11), built in its directory with
```
gcc -O3 -march=native -static -pthread -mcmodel=medium -Wall -Wextra -Wno-unused-function -DR=6 -DARENA=17319594752ULL -o orch_r6 main.c fp.c arena.c par.c ntt.c poly.c powmod.c hgcd.c line.c root.c -lm
```
and run as `ulimit -s 256; ./orch_r6 20` (the argument is the thread count; section 4.5), started 2026-10-19T21:16:01Z. The run executed the centres `c = 1, 2, 3` in order and stopped at the collision of `c = 3`. `arith` = additions, subtractions, multiplications, squarings; `other` = loads, stores, control (the address operations of the loads and stores and the normal-sequence tests included), unit charges and the declared thread charges; `arena peak` = the highest number of arena bytes in use during the stage (section 7). Every figure is a counter of the same execution or a stated constant charged in the stage that executes the thing it covers (section 4.2); nothing is taken from another run. The program prints one total: the sum of the stage rows, the sum of the trial rows and the counters of the whole run are computed separately and printed in the line `RECONCILE`, which reads `ok=1` only if the three are equal (stages 48,291,542,585,674 = trials 48,291,542,585,674 = counters 48,291,542,585,674). The stage rows sum over the three centres; the trial rows give each centre.

| stage | arith | other | total (three centres) | arena peak (bytes) |
|---|---:|---:|---:|---:|
| init: transform tables | 4,375,372 | 30,308,970 | 34,684,342 | 139,201,280 |
| setup: the line | 391 | 8,013 | 8,404 | 138,676,992 |
| A: centre c = i | 3 | 3,180 | 3,183 | 17,318,546,176 |
| B: g_c (2H evaluations, interpolation) | 36,921,172,554 | 331,810,378,242 | 368,731,550,796 | 17,318,546,176 |
| C: S^((p-1)/2) mod g (Montgomery) | 15,996,870,150,867 | 17,047,601,991,018 | 33,044,472,141,885 | 17,318,546,176 |
| D: gcd(g, R - 1) (half-gcd) | 5,315,855,779,865 | 9,562,444,839,929 | 14,878,300,619,794 | 16,244,804,544 |
| E: root of G | 1 | 1,223 | 1,224 | 8,728,612,160 |
| F: sqrt, W1, W2, back-map | 3,433 | 65,297 | 68,730 | 138,676,992 |
| G: verification (2 reference hashes) | 0 | 116,162 | 116,162 | 138,676,992 |
| H: canonical encoding of the output | 7 | 6,411 | 6,418 | 138,676,992 |
| I: report formatting, single write, exit | 0 | 3,384,736 | 3,384,736 | 138,676,992 |
| total of the run | | | 48,291,542,585,674 | |

| trial | centre `c_i` | outcome | `deg G` | tests of stage D | charge of the trial (stages A to G) | of which E + F + G |
|---:|---:|---|---:|---|---:|---:|
| 1 | 1 | no usable root (the trial ends after stage D) | 0 | all passed | 16,097,168,106,126 | 0 |
| 2 | 2 | no usable root (the trial ends after stage D) | 0 | all passed | 16,097,168,106,126 | 0 |
| 3 | 3 | collision (stages E, F, G executed) | 1 | all passed | 16,097,168,289,522 | 186,116 |
| outside the trials: init, line setup, stages H and I | | | | | 38,083,900 | |

Stages A to D of a trial cost the same at every centre: `16,097,168,106,126` at `c = 1` and `c = 2`, `16,097,168,103,406` at `c = 3` (the gcd of degree 1 ends the classical tail one division earlier). The one-centre bound takes the largest:

| term | value | source |
|---|---:|---|
| `T_fixed` (init, setup, H, I) | 38,083,900 | the row `TRIAL 0` of the report (outside the trials) |
| stages A to D of one centre | 16,097,168,106,126 | the largest of the three centres |
| `E_cap` (stage E at its cap, section 4.5) | 192,000,000 | `64 × 3,000,000`; the executed stage E was 1,224 (`deg G = 1`) |
| stage F (square root, back-map) | 68,730 | executed at `c = 3` |
| stage G (two reference hashes) | 116,162 | executed at `c = 3` |
| `T_draw` (the centre, two random words) | 63 | section 4.1; the executed run set `c := i` with one conversion, which is inside the stage-A row |
| `T_abort` (bookkeeping of an ABORT) | 1,000 | a bound; never executed |
| **`N_max`** | **16,097,398,375,981** | sum |

A trial that ends after stage D (`deg G = 0` or `deg G > 16`, or an ABORT, which executes a prefix of the normal stage-D work, section 4.4) costs less than the sum above; a trial that runs stage E costs at most the sum. So `N_max` bounds every run of the algorithm. `log2(N_max / 342) = 35.454040`, claimed as `35.45405` (rounded up at five decimals). For reference, the executed run as a whole (three centres) counted `N = 48,291,542,585,674` operations, `log2(N / 342) = 37.03898`; that was the form of the claim of our entry `a78f526e`.
Composition of the run by type (the control counter includes the address operations of the loads and stores and the `129,934,595` tests of each stage D): add `6,903,529,970,537`, sub `6,823,962,642,279`, mul `7,398,950,114,736`, sqr `223,208,754,941`, loads `7,367,013,472,917`, stores `3,700,100,104,441`, control `15,498,137,469,843`, unit charges `275,414,778,540` (`805,306,370` units of 342), declared thread charges `101,225,277,440` (`24,241,954` regions, `441,886,820` active-thread starts, `1,284,791,344` chunks: `200 · 441,886,820 + 10 · 1,284,791,344`). Total without the thread charges: `48,190,317,308,234`.

Stage C of trial 1 in detail (`m = 122,070,312`, `L = 2^27`): start exponent `v = 2^24`, Newton precision `P = 28,924,633`, start value 85,928,959,769 operations; 229 steps (45 with the multiplication by `x`), 10,876,695,495,957 operations in the loop, 47,496,486,881 per step on average; final reduction and recovery of `g`: 52,199,476,101.
Stage D of trial 1: `trial1 outer=30 hgcd_calls=7864282 divisions=122070312 quot_deg_ge2=0 max_qdeg=1 blocked_applies=10 tests=129934595 aborted=0` (every quotient of the Euclidean sequence had degree 1; every one of the 129,934,595 tests passed; no ABORT).

Wall time: `46078` s (12 h 47 min) on 20 threads of the machine of section 9.2; the progress lines of the run (`r6.err`) are kept with the package material but carry no count.

### 6.1 Ledger recomputation

```python
from math import log2, ceil
C = 342
stages = [34684342, 8404, 3183, 368731550796, 33044472141885, 14878300619794, 1224, 68730, 116162, 6418, 3384736]   # init, setup, A, B, C, D, E, F, G, H, I (three centres)
trials = [16097168106126, 16097168106126, 16097168289522]   # stages A to G of each centre
outside = 38083900     # init, line setup, stages H and I
E, F, G = 1224, 68730, 116162   # the stage rows E, F, G (executed at the third centre only)
N = sum(stages)
assert N == sum(trials) + outside == 48291542585674
abcd = [t - (E + F + G if i == len(trials) - 1 else 0) for i, t in enumerate(trials)]
N_max = outside + max(abcd) + 64 * 3000000 + F + G + 63 + 1000
assert N_max == 16097398375981
print('N_max =', format(N_max, ','), ' time_log2 =', '%.5f' % (ceil(log2(N_max / C) * 100000 - 1e-9) / 100000))
```

## 7. Memory

The algorithm runs one trial in the memory the program allocates for a trial; the program is linked statically (`-static`, the build line of section 6): the C library (glibc, with its thread support) is inside the image; there is no loader and no shared library. Three terms make up the memory.
(a) The whole executable image: every loadable segment, text + data + bss as printed by `size orch_r6` for the linked program: text 1,590,708 + data 25,028 + bss 17,319,675,160 = `17,321,290,896` bytes. The bss holds the one static arena (`ARENA = 17,319,594,752` bytes, `arena.c`; a multiple of 64), the 8,192-byte report buffer, the pass tables and the static state of the C library. The text is the code of the shipped source and of the C library.
(b) The heap is inside term (a): every buffer of the program (the sparse twiddle table of `L/32 + 1` elements, the two-level tables, the buffers `E`, `O`, `GI`, `GO` of `L` elements each, the matrices and scratch of stage D) is a block of the static arena served by the LIFO allocator `xalloc` (section 4.2); nothing is mapped from the kernel at run time except the thread stacks of term (c). The arena size was fixed from the exact stage-C requirement at `r = 6` (`4L` state elements, `L/32 + 1` twiddle entries, the small tables: 17,318,546,176 bytes, the stage-C peak of the table of section 6) plus a margin of 1 MiB; the run stops with status 5 if a request does not fit. The highest number of arena bytes in use over the whole run was `17,318,546,176` (`ARENA size=... high_water=...` in the report); the per-stage peaks are in the table of section 6 (stage D stays below stage C; an aborted trial allocates a prefix of a normal trial's allocations, section 4.4; stage E at its cap allocates seven arrays of at most 34 elements).
(c) Stacks: the main stack bound of `262,144` bytes (the run was executed under `ulimit -s 256`), and the 19 worker threads with a fixed stack of `262,144` bytes each (`pthread_attr_setstacksize` in `par.c`; glibc maps exactly that size for the stack and the thread's static thread-local block, plus a guard page that is not accessible memory): `20 × 262,144 = 5,242,880` bytes.
Total: `17,326,533,776` bytes `= 2^34.013` (rounded up at three decimals). The memory penalty is `max(0, 34.013 − 20) = 14.013`; the normalized cost is `35.45405 + 14.013 = 49.46705`.
The pages the kernel maps for a process outside its image (vdso, vvar, page tables) and its buffers for the `write` calls are the kernel's memory and lie outside the program's memory figure. As a cross-check, the run's peak resident set was sampled every minute from `/proc/<pid>/status` (`VmHWM`): the highest sample was `16,914,552` kB = `17,320,501,248` bytes, below the total counted here (the arena pages are touched only as they are used).
The program has no stored advice and no precomputed data beyond what it computes itself (the twiddle tables are built at run time and charged in stage `init`).

## 8. The premises and the success bound

Notation. `p` is the Pallas prime, `D = 5^12 = 244,140,625`, `F` the fixed digest polynomial of section 2.3 (degree `D`, leading coefficient `f_D ≠ 0`), `g_c` the monic odd part about the centre `c` (section 3, degree `m = 122,070,312`), `G(c, t) = (F(c + t) − F(c − t))/(2t) = g_c(t^2)`. For `c ∈ F_p` let `k(c)` be the number of nonzero squares `S ∈ F_p` with `g_c(S) = 0`; this is `deg G` of section 3, the degree of `gcd(g_c, S^((p−1)/2) − 1)`. `E_c` is the event `1 ≤ k(c) ≤ DMAX = 16`, under which stage E runs; `N_c` is the event that the Euclidean remainder sequence of `(g_c, R_c − 1)`, `R_c = S^((p−1)/2) mod g_c`, is normal down to its gcd (`deg(R_c − 1) = m − 1` and every quotient of degree 1).

### 8.1 The premise `H-ONE`

**Premise `H-ONE`.** The number of centres `c ∈ F_p` with `1 ≤ k(c) ≤ 16` is at least `q·p` with `q = 0.3931`. Equivalently, for `c` uniform on `F_p`, `P(E_c) ≥ 0.3931`.

Role: score-critical. Scope: the fixed target `poseidon-orchard-r6-prefix-v1`, this line construction (the line `j = 0` of the first two rounds, section 2), the polynomial `F` of section 2.3, centres uniform on `F_p`. Nothing is claimed for other round counts, other lines or other polynomials. The value `0.3931` is `0.0003693` below `1 − e^(−1/2) = 0.3934693`, the law value of section 8.3, and `0.0001292` below the four-moment Bonferroni bound `151/384 = 0.3932292` (section 8.3); the split of the allowance between `H-ONE` and `H-NORMAL` (`δ = 0.003`) follows cryptogakusei's entry `4888e783`, as Jbenisek's `c318f442` does at this round count. What the premise does not contain: no random-polynomial model, no independence between centres (one centre is drawn), nothing about the remainder sequence (that is `H-NORMAL`) and nothing about the cost (the time bound holds for every sequence, section 4.4).

Limitations. The premise concerns this `F`, not every polynomial of degree `D`: it is false for permutation polynomials (`k = 0` at every centre) and for a decomposable `F` with imprimitive monodromy; it is false at one S-box layer (`m = 2`: the law of 8.3 gives exactly `0.375`). At twelve layers the monodromy of the cover is not computed and the point counts of section 8.3(b) are out of reach of Weil's bound; the premise is the extrapolation of a law that is a theorem at two and three layers (reported by Jbenisek's and cryptogakusei's entries, section 8.3(c)) and that is measured on this target at depths 2 and 3 by the organizer-run tests of section 9.4, at `r = 1, 2` on the sibling targets (`m = 39,062` and `195,312`, section 9.3) and at `r = 3, 4, 6` by the executed runs (sections 9.1, 9.2). The allowance `0.0003693` is thin.

### 8.2 The success bound with one centre

(a) The centre is one draw (section 4.1) within statistical distance `p/2^512` of uniform; the shifts of stage E are further draws of the same kind. The bound below is stated for exactly uniform draws and transferred to the written sampler at the end.

(b) By `H-ONE`, `P(E_c) ≥ q = 0.3931`; by `H-NORMAL` (8.5), `P(not N_c) ≤ δ = 0.003`; so `P(E_c and N_c) ≥ q − δ = 0.3901`.

(c) If `E_c` and `N_c` hold, stage C computes `R_c` exactly (section 4.3: the step is an exact identity in `F_p[x]`; the program checks the two degree conditions that certify it and stops with an error, never a false result, if they fail; no error occurred), stage D passes every test and returns `G = gcd(g_c, R_c − 1)` with `1 ≤ deg G ≤ 16` (section 4.4: on a normal sequence with `deg G ≤ 16` the zero remainder appears in the classical tail), and stage E fails to isolate a root with probability at most `ε_iso` (8.4), over shifts that are fresh for that stage. A root `S` of `G` is a nonzero square root of `g_c`, and stages F and G end in a verified collision (section 5).

(d) Hence, for uniform draws and `K = 1`, `P[success] ≥ P(E_c and N_c) − ε_iso ≥ q − δ − ε_iso`. The success of a run is an event of the vector of its draws, and the actual draws of section 4.1 are within total variation `ε_coin` of the uniform vector, so the actual success probability is at least `q − δ − ε_iso − ε_coin = 0.3931 − 0.003 − 2.371·10^−15 − 1.404·10^−76 = 0.390099999999997628 ≥ 0.39009`. This is the form `1 − (1 − q + δ)^K − K(ε_coin + ε_iso)` of bradcush's entry `1aa56884` at `K = 1`. The bound stays at or above `0.39` for every `δ ≤ 0.0030999` at `q = 0.3931`. The probability is over the random words of the algorithm for the fixed target: not a probability over targets, not a sampled frequency, and no run of the program enters it.

(e) Why one centre needs a statement about the event. The law of 8.3 has `E[k] = 1/2` and `E[k(k−1)] = 1/4`; over all laws with these two moments the sharp lower bound on `P(k ≥ 1)` is `3/8 = 0.375` (attained by `P(0) = 5/8`, `P(1) = 1/4`, `P(2) = 1/8`), below the floor. One centre therefore needs the premise about the event `E_c` itself (or four moments, 8.3(b)); two-moment premises need two centres.

### 8.3 Where the number comes from (support of `H-ONE`; not used in the bound)

(a) The law. The roots of `G(c, t)` in `t` come in pairs `±t_i`, `u_i = t_i^2` the roots of `g_c`, so the Galois group of the cover `G(c, t) = 0` of the `c`-line acts by signed permutations of the `m` pairs: it is a subgroup of the hyperoctahedral group `B_m`. For a centre off the branch locus, `k(c)` is the number of indices `i` with `t_i ∈ F_p`, the positive fixed points of the Frobenius element. For a uniform element of `B_m` the binomial moments of this number are `E[C(k, j)] = 2^−j / j!` (`j ≤ m`), so `P(k ≥ 1) = 1 − Σ_(j ≤ m) (−1/2)^j / j!`: `0.375` at `m = 2`, `0.3958` at `m = 3`, `0.3932` at `m = 4` and `0.3934693403` for every `m ≥ 12`, the Poisson(1/2) value `1 − e^(−1/2)`; `P(k > 16) < 2.3·10^−20`. By Chebotarev's theorem the Frobenius elements are equidistributed in the monodromy group, so when the group is all of `B_m` (or contains its commutator subgroup) this law is the frequency of `k(c)` over the centres, up to the error terms of (c).

(b) Moments and counts. `E[C(k, j)] = N_j / (2^j j! p)`, where `N_j` counts the points `(c, t_1, …, t_j)` over `F_p` with `G(c, t_i) = 0`, `t_i ≠ 0`, `t_a^2 ≠ t_b^2`. For every integer `k ≥ 0`, `1_(1 ≤ k ≤ 16) ≥ k − C(k, 2) + C(k, 3) − C(k, 4)` (the right side is `1 − C(k − 1, 4)` for `k ≥ 1`, which is `1` for `k ≤ 5` and `≤ 0` for `k ≥ 6`, and `0` at `k = 0`), so `P(E_c) ≥ S_1 − S_2 + S_3 − S_4` (Bonferroni at order 4), which with the moments of (a) is `151/384 = 0.3932292`. So `H-ONE` follows from four count statements `N_1 ≥ (1 − ε) p`, `N_2 ≤ (1 + ε) p`, `N_3 ≥ (1 − ε) p`, `N_4 ≤ (1 + ε) p` with `ε ≤ 0.0032835`; the premise is stated as the weaker statement `H-ONE` itself.

(c) A theorem at two and three layers (reported, not reproduced here). Let `F_N` be the truncation of `F` to its first `N` S-box layers (coordinate 0 after rounds 2, 3 and then 4, 5, …, on the same line; degree `5^N`, `m = (5^N − 1)/2`: `12`, `62`, `312` at `N = 2, 3, 4`). Jbenisek's entries (`18369013` and `c318f442` at this round count, with his research partner's computations) and cryptogakusei's `4888e783` report that on the deployed constants and this line the arithmetic monodromy of `g_c` is `S_12` at `N = 2` and `S_62` at `N = 3` (witnessed by Frobenius cycle types `(12)`, `(11, 1)`, `(7, 1^5)` and `(62)`, `(61, 1)`, `(59, 1^3)`), that the sign kernel is full (`B_12`, `B_62`), and that at `N = 4` the monodromy is 2-transitive of degree 312. With the geometric monodromy containing the commutator subgroup of `B_m`, the curves counted by `N_j` (`j ≤ 8`) are absolutely irreducible complete intersections, and the Aubry–Perret bound gives `N_j = p(1 + ρ_j)` with `|ρ_j| ≤ (5^N − 1)^(2j) p^(−1/2)`, below `2^−53` at `N = 2` and `2^−15` at `N = 3`; Bonferroni at orders 7 and 8 then gives `0.39346933 ≤ P(1 ≤ k ≤ 16) ≤ 0.39346944` at those depths: the premise is a theorem there, with margin `0.00237`. This package cites those computations as text (its section 9.4 tests the same depths on the same target with its own program, and the executed runs of 9.1–9.3 reach `m = 122,070,312`); it does not reproduce the monodromy certificates.

(d) The extrapolation. At `N = 12` neither the monodromy nor the counts can be computed (Weil's bound exceeds `p` for `j ≥ 2`). The premise states that this `F` stays within `0.0003693` of the law of (a): no structure appears between the third layer and the twelfth that changes the law of the positive fixed points by `0.1 %`. Measured on this target (section 9): at depths 2 and 3 the organizer-run one-centre tests predict `Binomial(T, 0.3935)` successes; the sibling targets at `r = 1` (`m = 39,062`, 1,024 centres) and `r = 2` (`m = 195,312`, 256 centres) and the executed runs at `r = 3`, `4` and `6` give the counts of section 9: at `r = 2`, `3`, `4` and `6` and in the organizer-run tests the counts are within sampling range of the law; at `r = 1` (depth 7) the sampled frequency is above the law (section 9.3, `z = +2.69`), a deviation at the smallest depth of the family in the direction of more usable centres, whose cause is not known. The premise is stated for `F` at depth 12 and is not a claim about `r = 1`.

### 8.4 The isolation lemma (proved)

**Lemma.** Let `G` be monic of degree `d`, `2 ≤ d ≤ 16`, a product of `d` distinct linear factors over `F_p`. In one round of stage E (the shift `δ` exactly uniform on `F_p`), with probability at least `w = (p − 3)/(2p)` the polynomials `F = gcd(G, (x + δ)^((p−1)/2) − 1)` and `G/F` are both nonconstant, and then the kept part has degree at most `floor(d/2)`. The degree never increases. Hence after `Z = 64` rounds the probability that `deg G ≥ 2` remains is at most `P[Bin(64, w) ≤ 3] ≤ 2.371·10^−15`.

*Proof.* Let `u ≠ v` be two roots of `G` and `χ` the quadratic character of `F_p`. The roots of `G` are mapped by `x ↦ x + δ` to `u + δ, v + δ, …`; a root `r + δ` lies in `F` exactly when `(r + δ)^((p−1)/2) = 1`, that is `χ(r + δ) = 1`. If `δ ∉ {−u, −v}` and `χ(u + δ) ≠ χ(v + δ)`, exactly one of the two lies in `F` and the other in `G/F`, so both are nonconstant, their degrees sum to `d`, and the smaller has degree at most `floor(d/2)`. The number of `δ` with `χ((u + δ)(v + δ)) = −1`: since the quadratic `(δ + u)(δ + v)` has the nonzero discriminant `(u − v)^2`, `Σ_(δ ≠ −u, −v) χ((δ + u)(δ + v)) = −1` (the standard quadratic character sum), so among the `p − 2` values of `δ` outside `{−u, −v}` the count with character `−1` is `(p − 2 + 1)/2 = (p − 1)/2`, of which at least `(p − 3)/2` are nonzero. So a uniform `δ` gives a splitting round with probability at least `w = (p − 3)/(2p)`. A part is always a divisor of `G`, so the degree is nonincreasing in every round. Conditional on any history, the next `δ` is fresh, so every round splits with probability at least `w` independently of the past, and at most `ceil(log2 16) = 4` splitting rounds bring `d ≤ 16` to `1` (`16 → 8 → 4 → 2 → 1`). The failure probability after `Z = 64` rounds is at most `P[Bin(64, w) ≤ 3] = Σ_(j ≤ 3) C(64, j) w^j (1 − w)^(64 − j)`, which at `w = 1/2 − 3/(2p)` is `2.371·10^−15` (`2^−48.58`). ∎ (The program replaces a zero draw by itself without change: `x + 0` is a valid shift that splits with the same bound; the actual draws are within `ε_coin` of uniform, accounted in 8.2(d).)

### 8.5 The premise `H-NORMAL`

**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(g_c, R_c − 1)`, `g_c` the monic odd part of section 3 (degree `m = 122,070,312`) and `R_c = S^((p−1)/2) mod g_c`, is normal down to its gcd (`deg(R_c − 1) = m − 1` and every quotient of degree 1) except with probability at most `δ = 0.003` (`2^−8.38`).

Role: score-critical for the success probability only. The time and memory bounds hold for every sequence: stage D is charged for the normal sequence, every division tests its quotient and every call its return, and on any other case the trial ends after a prefix of the charged work (the prefix lemma, section 4.4). Scope: the pairs `(g_c, R_c − 1)` of the target `poseidon-orchard-r6-prefix-v1`, `c` uniform on `F_p`; nothing for other round counts. The premise is bradcush's (entries `e6dcb600`, `1aa56884`), the allowance `δ = 0.003` cryptogakusei's split (`4888e783`).

Extrapolation and evidence. For a uniformly random pair of polynomials of degrees `m` and `m − 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes; each is a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz–Zippel the probability is at most `2m^2/p < 2^−199`. That bound does not transfer, because the coefficients of `R_c` are polynomials of degree about `p` in those of `g_c`; the premise asserts far less than random-pair behaviour, an abnormality probability of at most `0.003`, which is all that 8.2 uses. Measured on this target: (i) at the scale of the claim, the three executed centres of section 9.1 (`m = 122,070,312`): every one of the `129,934,595` tests of each trial passed, `max_qdeg = 1`; (ii) the executed runs at `r = 3` and `r = 4` (section 9.2, `m = 976,562` and `4,882,812`): every quotient of degree 1 at every centre; (iii) the survey runs of section 9.3 on the sibling targets `r = 1` (`m = 39,062`, 1,024 centres) and `r = 2` (`m = 195,312`, 256 centres), the same program, every centre run to the end of stage D: 1024 of 1024 sequences normal at `r = 1` and 256 of 256 sequences normal at `r = 2`; (iv) organizer-run (section 9.4): the experiments `euclid-normal-n2-t128-l2-a`, `-b` and `euclid-normal-n3-t20` compute the complete sequence for this construction at depths 2 and 3 (`m = 12`, `62`) at 532 organizer-seeded centres and return a pair exactly when every sequence of a trial is normal; the prediction is that every trial returns a pair. Limitations: the organizer-run tests are at `m = 12` and `62` and the surveys at `m ≤ 195,312`, below the scale of the claim; at the scale of the claim the evidence is three centres. An algebraic relation between `g_c` and `R_c` that forces a principal subresultant coefficient to vanish for many centres would invalidate the premise; none is known, and none appeared in `1,820` sequences at `m ≥ 12` on this target. Normality in the organizer-run tests is computed inside the submitted program (printed in full in `experiments/exp_centre.py`); the runner checks only the returned pairs.

## 9. Evidence

None of this section enters the success bound of section 8.2, and none of it is a lower bound on `P(E_c)`. 9.1 to 9.3 are runs of the shipped program on this machine (reported, not organizer-run); 9.4 is run by the organizer's runner.

### 9.1 The executed centres at `r = 6` (the scale of the claim)

The executed run of section 6 (`m = 122,070,312`, the actual target) ran three centres to the end of stage D or beyond:

| centre `c` | `deg(R − 1) = m − 1` | tests of stage D | quotient degrees | `k(c) = deg G` | outcome |
|---:|---|---:|---|---:|---|
| 1 | yes (entry test passed) | 129,934,595 passed, no ABORT | all 1 | 0 | no usable root |
| 2 | yes (entry test passed) | 129,934,595 passed, no ABORT | all 1 | 0 | no usable root |
| 3 | yes (entry test passed) | 129,934,595 passed, no ABORT | all 1 | 1 | collision, verified by stage G and by the organizer's digest (`certificates/`) |

Three normal sequences of degree `m` (the premise `H-NORMAL` held at all three), and `k(c) = 0, 0, 1`: one centre of three in `E_c` (the law of 8.3 gives `P(E_c) = 0.3935`; three draws say nothing precise, and the centres `1, 2, 3` are not random draws). The per-trial charges of stages A to D agree to the operation (section 6).

### 9.2 Development runs at `r = 1, 2, 3, 4` (the same program, smaller round counts of the same family)

at `r = 1` (`m = 39,062`, `L = 2^16`): `N = 3,915,364,169` on 1 thread (`log2(N/237) = 23.97776`; 8 threads 3,922,305,369, 20 threads 3,933,358,169, identical except the thread charges), collision at `c = 1`, `deg G = 1`, the same pair and digest as Jbenisek's `r = 1` entry; at `r = 2` (`m = 195,312`): `N = 19,175,814,543` (20 threads), collision at `c = 1`; at `r = 3` (`m = 976,562`, `L = 2^20`): `N = 87,121,990,330` on 1 thread (`28.21820`; 8 and 20 threads 87,214,549,930 and 87,350,893,130), collision at `c = 1`, `1,037,971` tests of stage D passed; at `r = 4` (`m = 4,882,812`, `L = 2^23`): trial 1 (`c = 1`) ended with `deg G = 0` (no usable root; every test passed), trial 2 (`c = 2`) gave the collision, `N = 1,496,028,918,174` (20 threads, `32.21546`). Every collision of these runs passes the organizer verifier, and at `r = 1 … 4` the pair and the root `S` equal those of an independent NTL computation of the same procedure (the resultant-free oracle `trial_w0.py`, not part of the package). Every remainder sequence of these runs was normal (`max_qdeg = 1`, `aborted = 0` in each report). Unit tests of the components (field vectors, transforms, the Montgomery step against NTL `SqrMod`, stage C against NTL `PowerXMod`, `g_c` against its definition at four random points, the half-gcd against NTL `GCD` on normal inputs with gcds up to degree 2,000 and the ABORT on abnormal inputs, the chained transform kernels against a naive DFT, the root isolation on synthetic split polynomials of degree up to 40) all passed before the run. Machine: one 24-core x86-64 host, 78 GB of memory, no other load of consequence during the `r = 6` run.

### 9.3 Survey runs on the sibling targets `r = 1` and `r = 2` (the same program, every centre run to its end)

The same program in its survey mode (`ORCH_SURVEY=K ORCH_START=c0`: `K` consecutive centres from `c0`, each run to the end of stage D or beyond, no stop at a success; `main.c`) on the targets `r = 1` (`m = 39,062`) and `r = 2` (`m = 195,312`) of the same family (same constants, same line): the complete Euclidean sequence of `(g_c, R_c − 1)` with the tests of section 4.4 at every centre, and the collision search when `1 ≤ k(c) ≤ 16`. The centres are `c = 1, 2, …` in order (not random draws).

| `r` | `m` | centres | normal sequences | `k(c)` = 0 / 1 / 2 / 3 / ≥ 4 | `k ≥ 1` | `1 ≤ k ≤ 16` (fraction; Clopper–Pearson, reference only) | verified collisions |
|---:|---:|---:|---|---|---:|---|---:|
| 1 | 39,062 | 1024 | 1024 (every test passed; `max_qdeg = 1`) | 579 / 340 / 86 / 17 / 2 | 445 | 445 (0.4346; 95 % interval 0.4039–0.4656) | 445 |
| 2 | 195,312 | 256 | 256 (every test passed; `max_qdeg = 1`) | 156 / 79 / 18 / 2 / 1 | 100 | 100 (0.3906; 95 % interval 0.3305–0.4533) | 100 |

The law of 8.3 gives `P(1 ≤ k ≤ 16) = 0.3935`. At `r = 2` the frequency agrees with the law (`z = -0.09`). At `r = 1` it is above the law: 445 of 1024 where the law expects 402.9 (`z = +2.69`; one-sided binomial tail 0.0040; the 95 % interval excludes 0.3935), with mean `k(c)` 0.5576 against `1/2`, the excess at `k = 1, 2, 3`. The polynomial at `r = 1` has depth 7 (`D = 5^7`), the smallest of the family; the deviation is in the direction of more usable centres, so at `r = 1` the value `q = 0.3931` of `H-ONE` is below the sampled frequency. It is reported as a fact about the sibling target: it neither supports nor refutes the premise at depth 12, which the premise states for `F` only. Every one of the 1,280 sequences was normal. These runs are reported by this package, not organizer-run.

### 9.4 Organizer-run tests at reduced depth (`experiments/manifest.json`, `experiments/exp_centre.py`)

Five experiments of kind `python-message-pairs-v1`, run by the organizer's runner (standard library only; the program is this package's own, written for it). For each computed trial the program takes a centre `c` from the trial seed and builds, exactly over `F_p`, the polynomial `F_N(c + X)` (the truncation of 8.3(c): coordinate 0 after the first `N` S-box layers of the digest polynomial on the line `j = 0`, the same constants, MDS and line as the program; checked against direct iteration of the layers at `c ± 1`, `c ± 2`), its monic odd part `g` (`m = 12` at `N = 2`, `62` at `N = 3`), `R = X^((p−1)/2) mod g` and the complete Euclidean remainder sequence of `(g, R − 1)` down to the zero remainder; `deg G = k(c)`. `one-centre-n2-t256` and `one-centre-n3-t20` run one trial of the algorithm of section 4 at depth 2 and 3 (256 and 20 organizer seeds): a trial is flagged when the sequence is normal, `1 ≤ k(c) ≤ 16`, the isolation (shifts from the seed, at most 64 rounds) returns a root `S` of `G`, and `F_N(c + s) = F_N(c − s)` for `s = sqrt(S) ≠ 0` by direct iteration; the predicted number of flagged trials is `Binomial(T, 0.3935)` (8.3: at these depths the premise is a theorem). `euclid-normal-n2-t128-l2-a`, `-b` (two centres per trial, 256 sequences each) and `euclid-normal-n3-t20` flag a trial when every sequence is normal; the prediction is that every trial is flagged. A flagged trial returns a witness: two distinct canonical messages of the selected target on the line, `W = c + s_1` and `W = c + s_2`, whose digests agree on the first 6 bits (found among the first 65 line points, so it always exists); every other trial returns two nulls. The organizer-checked pair count is therefore the number of flagged trials; the premises are tested under trusted execution of the submitted program, which the runner checks only through the returned pairs. Our local runs of the same program with local seeds (the organizer's container settings: one CPU, standard library, under 10 s each; the organizer's seeds differ):

| experiment | trials | flagged (local seeds) | predicted | `k ≥ 1` among the centres | abnormal sequences |
|---|---:|---:|---|---:|---:|
| `one-centre-n2-t256` | 256 | 106 | Binomial(256, 0.3935): 100.7 | 106 of 256 | 0 |
| `one-centre-n3-t20` | 20 | 6 | Binomial(20, 0.3935): 7.9 | 6 of 20 | 0 |
| `euclid-normal-n2-t128-l2-a` | 128 | 128 | every trial flagged (128) | 101 of 256 | 0 |
| `euclid-normal-n2-t128-l2-b` | 128 | 128 | every trial flagged (128) | 86 of 256 | 0 |
| `euclid-normal-n3-t20` | 20 | 20 | every trial flagged (20) | 6 of 20 | 0 |

The checks and the layer polynomials are independent of the C program (the experiment program is 31 KB of Python); the target digest inside it reproduces the organizer verifier on the certificate pair.

## 10. What is and is not provided

* Provided: the algebraic derivation (sections 2–3), the algorithm with its charges and its tests (4), the operation bound assembled from the executed run and the memory footprint (6, 7), the premises with their scope, evidence, extrapolation and limitations (8), the executed evidence at `r = 6` and at `r = 1 … 4` and the survey runs (9.1–9.3), the organizer-run experiments (9.4, `experiments/`), the complete C source of the instrumented program (11), and one collision certificate (`certificates/`, the output of the executed run).
* The time bound is a count of the shipped program under the model of section 4.2 (Jbenisek's reading of the organizer's model: a declared register file whose operands are not charged as loads, every array access charged with its address operation); word-level costs beyond it (cache, bandwidth) are outside the model. The organizer did not run the program; the counts rest on the shipped source, which is the complete text of section 11.
* The success probability rests on the two premises of section 8; `plausible_not_refuted` for them is not a proof. The executed centres (three at `r = 6`) are consistent with the premises but are too few to bound anything; the organizer-run tests reach `m = 62`, the surveys `m = 195,312`.
* Reproduction: (a) the certificate against the organizer's digest, seconds; (b) the ledger recomputation of section 6.1, seconds; (c) the build line of section 6 and `ulimit -s 256; ./orch_r6 20`, which reproduces every count of section 6 and prints the collision (12 h 47 min wall on 20 threads of the machine of section 9.2; about 18 GB of memory); (d) the survey runs with `ORCH_SURVEY=64 ORCH_START=…` on the `r = 1` and `r = 2` builds (section 9.3); (e) the experiments with the organizer's runner.

## 11. Complete source of the instrumented program

Seventeen files, as built by the line of section 6 (`kern.h` and `consts.h` are generated by the two Python scripts, which are listed too). The transform engine, the allocator, the thread layer and the stages are written for this package; nothing is copied from another entry.

### Makefile

```makefile
# orch build.  make R=1 (or 2, 3, 6); the arena size is fixed per R (bytes, multiple of 64).
R ?= 1
# Arena sizes (bytes, multiples of 64): the measured high-water mark of the recorded runs (r = 1..4), for r = 6 the
# exact stage-C requirement 4 L + L/32 + small tables (L = 2^27 elements of 32 bytes) plus a 1 MiB margin.
ifeq ($(R),1)
ARENA ?= 12602752
endif
ifeq ($(R),2)
ARENA ?= 49504832
endif
ifeq ($(R),3)
ARENA ?= 151355392
endif
ifeq ($(R),4)
ARENA ?= 1606471872
endif
ifeq ($(R),5)
ARENA ?= 4900000000
endif
ifeq ($(R),6)
ARENA ?= 17319594752
endif
CC = gcc
CFLAGS0 = -O3 -march=native -static -pthread -mcmodel=medium -Wall -Wextra -Wno-unused-function -DR=$(R) $(EXTRA)
CFLAGS = $(CFLAGS0) -DARENA=$(ARENA)ULL
SRC = main.c fp.c arena.c par.c ntt.c poly.c powmod.c hgcd.c line.c root.c
HDR = orch.h stages.h consts.h kern.h Makefile

orch_r$(R): $(SRC) $(HDR)
	$(CC) $(CFLAGS) -o $@ $(SRC) -lm

kern.h: gen_kern.py
	python3 gen_kern.py > kern.h

clean:
	rm -f orch_r1 orch_r2 orch_r3 orch_r4 orch_r6
```

### orch.h

```c
/* orch: instrumented collision finder for reduced-round Orchard Poseidon (Pallas).
 * Common definitions: counters and charging macros (DESIGN.md section 5), the field F_p in Montgomery form
 * (every field operation counts itself), the arena allocator, the thread runner, the transform engine and
 * the polynomial tools.  All charges are made where the charged operation executes. */
#ifndef ORCH_H
#define ORCH_H
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "consts.h"

#ifndef R
#define R 1
#endif
#define CR (216 + 21 * R)               /* C(r): primitive operations per target compression */

/* ------------------------------------------------------------------ counters */
typedef struct { uint64_t add, sub, mul, sqr, ld, st, ctl, rnd, unit, thr; } cnt_t;
/* add/sub/mul/sqr: field operations; ld/st: 256-bit element loads/stores (each also adds 1 address operation to
 * ctl); ctl: index/control operations; rnd: random words; unit: operations charged as units (C(r) per line
 * evaluation or reference hash); thr: the declared thread charges (start/join, chunk dispatch). */
extern __thread cnt_t X;
#define LD(n)  do { X.ld += (uint64_t)(n); X.ctl += (uint64_t)(n); } while (0)
#define ST(n)  do { X.st += (uint64_t)(n); X.ctl += (uint64_t)(n); } while (0)
#define CTL(n) (X.ctl += (uint64_t)(n))
/* a plain (not unrolled) loop of n iterations: 3 per iteration + 2 on exit */
#define LOOPC(n) (X.ctl += 3 * (uint64_t)(n) + 2)
/* FOR8: the body is written 8 times per pass in the source (genuinely unrolled); 1 for the bound n & ~7, 3 per pass
 * of eight, 2 on exit of the main loop, then the 0..7 leftover elements in a plain loop (3 each, 2 on exit). */
#define FOR8(I, N, ...) do { size_t n_ = (size_t)(N), n8_ = n_ & ~(size_t)7, i_ = 0; CTL(1);                 \
    for (; i_ < n8_; i_ += 8) {                                                                               \
        { size_t I = i_;     __VA_ARGS__; } { size_t I = i_ + 1; __VA_ARGS__; }                               \
        { size_t I = i_ + 2; __VA_ARGS__; } { size_t I = i_ + 3; __VA_ARGS__; }                               \
        { size_t I = i_ + 4; __VA_ARGS__; } { size_t I = i_ + 5; __VA_ARGS__; }                               \
        { size_t I = i_ + 6; __VA_ARGS__; } { size_t I = i_ + 7; __VA_ARGS__; } CTL(3); }                    \
    CTL(2);                                                                                                   \
    for (; i_ < n_; i_++) { size_t I = i_; __VA_ARGS__; CTL(3); }                                             \
    CTL(2); } while (0)

static inline cnt_t cnt_sub(cnt_t a, cnt_t b) {
    cnt_t r = { a.add - b.add, a.sub - b.sub, a.mul - b.mul, a.sqr - b.sqr, a.ld - b.ld, a.st - b.st,
                a.ctl - b.ctl, a.rnd - b.rnd, a.unit - b.unit, a.thr - b.thr };
    return r;
}
static inline cnt_t cnt_add(cnt_t a, cnt_t b) {
    cnt_t r = { a.add + b.add, a.sub + b.sub, a.mul + b.mul, a.sqr + b.sqr, a.ld + b.ld, a.st + b.st,
                a.ctl + b.ctl, a.rnd + b.rnd, a.unit + b.unit, a.thr + b.thr };
    return r;
}
static inline uint64_t cnt_arith(cnt_t a) { return a.add + a.sub + a.mul + a.sqr; }
static inline uint64_t cnt_total(cnt_t a) { return cnt_arith(a) + a.ld + a.st + a.ctl + a.rnd + a.unit + a.thr; }

/* ------------------------------------------------------------------ field (Montgomery, 4 x 64-bit limbs) */
typedef struct { uint64_t l[4]; } fp;
typedef unsigned __int128 u128;
static const uint64_t FP_P[4] = P_LIMBS;

/* r = a + b - p if a + b >= p (inputs canonical, p < 2^255 so a + b < 2^256) */
static inline void fp_add_raw(fp *r, const fp *a, const fp *b) {
    unsigned long long s0, s1, s2, s3, t0, t1, t2, t3;
    unsigned char c = 0;
    c = __builtin_ia32_addcarryx_u64(c, a->l[0], b->l[0], &s0);
    c = __builtin_ia32_addcarryx_u64(c, a->l[1], b->l[1], &s1);
    c = __builtin_ia32_addcarryx_u64(c, a->l[2], b->l[2], &s2);
    (void)__builtin_ia32_addcarryx_u64(c, a->l[3], b->l[3], &s3);
    unsigned char br = 0;
    br = __builtin_ia32_sbb_u64(br, s0, FP_P[0], &t0);
    br = __builtin_ia32_sbb_u64(br, s1, FP_P[1], &t1);
    br = __builtin_ia32_sbb_u64(br, s2, FP_P[2], &t2);
    br = __builtin_ia32_sbb_u64(br, s3, FP_P[3], &t3);
    uint64_t mk = (uint64_t)0 - (uint64_t)br;          /* all ones: keep s (s < p) */
    r->l[0] = (s0 & mk) | (t0 & ~mk); r->l[1] = (s1 & mk) | (t1 & ~mk);
    r->l[2] = (s2 & mk) | (t2 & ~mk); r->l[3] = (s3 & mk) | (t3 & ~mk);
}
/* r = a - b (+ p if negative) */
static inline void fp_sub_raw(fp *r, const fp *a, const fp *b) {
    unsigned long long s0, s1, s2, s3;
    unsigned char br = 0;
    br = __builtin_ia32_sbb_u64(br, a->l[0], b->l[0], &s0);
    br = __builtin_ia32_sbb_u64(br, a->l[1], b->l[1], &s1);
    br = __builtin_ia32_sbb_u64(br, a->l[2], b->l[2], &s2);
    br = __builtin_ia32_sbb_u64(br, a->l[3], b->l[3], &s3);
    uint64_t mk = (uint64_t)0 - (uint64_t)br;
    unsigned char c = 0;
    c = __builtin_ia32_addcarryx_u64(c, s0, FP_P[0] & mk, &s0);
    c = __builtin_ia32_addcarryx_u64(c, s1, FP_P[1] & mk, &s1);
    c = __builtin_ia32_addcarryx_u64(c, s2, FP_P[2] & mk, &s2);
    (void)__builtin_ia32_addcarryx_u64(c, s3, FP_P[3] & mk, &s3);
    r->l[0] = s0; r->l[1] = s1; r->l[2] = s2; r->l[3] = s3;
}
/* Montgomery product a*b/2^256 mod p (CIOS; p[2] = 0 is used to skip one product per row) */
static inline void fp_mul_raw(fp *r, const fp *a, const fp *b) {
    uint64_t t0 = 0, t1 = 0, t2 = 0, t3 = 0, t4 = 0;
    for (int i = 0; i < 4; i++) {
        uint64_t bi = b->l[i];
        u128 z;
        z = (u128)a->l[0] * bi + t0;                 t0 = (uint64_t)z;
        z = (u128)a->l[1] * bi + t1 + (z >> 64);     t1 = (uint64_t)z;
        z = (u128)a->l[2] * bi + t2 + (z >> 64);     t2 = (uint64_t)z;
        z = (u128)a->l[3] * bi + t3 + (z >> 64);     t3 = (uint64_t)z;
        z = (u128)t4 + (z >> 64);                    t4 = (uint64_t)z;
        uint64_t t5 = (uint64_t)(z >> 64);
        uint64_t mm = t0 * P_NINV;
        z = (u128)mm * FP_P[0] + t0;
        z = (u128)mm * FP_P[1] + t1 + (z >> 64);     t0 = (uint64_t)z;
        z = (u128)t2 + (z >> 64);                    t1 = (uint64_t)z;     /* p[2] = 0 */
        z = (u128)mm * FP_P[3] + t3 + (z >> 64);     t2 = (uint64_t)z;
        z = (u128)t4 + (z >> 64);                    t3 = (uint64_t)z;
        t4 = t5 + (uint64_t)(z >> 64);
    }
    unsigned long long s0, s1, s2, s3;
    unsigned char br = 0;
    br = __builtin_ia32_sbb_u64(br, t0, FP_P[0], &s0);
    br = __builtin_ia32_sbb_u64(br, t1, FP_P[1], &s1);
    br = __builtin_ia32_sbb_u64(br, t2, FP_P[2], &s2);
    br = __builtin_ia32_sbb_u64(br, t3, FP_P[3], &s3);
    (void)t4;                                          /* t < 2p < 2^256, so t4 = 0 here */
    uint64_t mk = (uint64_t)0 - (uint64_t)br;         /* all ones: t < p, keep t */
    r->l[0] = (t0 & mk) | (s0 & ~mk); r->l[1] = (t1 & mk) | (s1 & ~mk);
    r->l[2] = (t2 & mk) | (s2 & ~mk); r->l[3] = (t3 & mk) | (s3 & ~mk);
}
/* counted operations (1 each) */
static inline void fp_add(fp *r, const fp *a, const fp *b) { X.add++; fp_add_raw(r, a, b); }
static inline void fp_dbl(fp *r, const fp *a) { X.add++; fp_add_raw(r, a, a); }
static inline void fp_sub(fp *r, const fp *a, const fp *b) { X.sub++; fp_sub_raw(r, a, b); }
static inline void fp_neg(fp *r, const fp *a) { static const fp z = { { 0, 0, 0, 0 } }; X.sub++; fp_sub_raw(r, &z, a); }
static inline void fp_mul(fp *r, const fp *a, const fp *b) { X.mul++; fp_mul_raw(r, a, b); }
static inline void fp_sqr(fp *r, const fp *a) { X.sqr++; fp_mul_raw(r, a, a); }
/* uncounted helpers (register moves and tests whose cost is charged by the caller with CTL) */
static inline void fp_zero(fp *r) { r->l[0] = r->l[1] = r->l[2] = r->l[3] = 0; }
static inline void fp_one(fp *r) { static const fp o = { MONT_ONE }; *r = o; }
static inline int fp_is_zero(const fp *a) { return (a->l[0] | a->l[1] | a->l[2] | a->l[3]) == 0; }
static inline int fp_eq(const fp *a, const fp *b) {
    return a->l[0] == b->l[0] && a->l[1] == b->l[1] && a->l[2] == b->l[2] && a->l[3] == b->l[3];
}
/* fp.c */
void fp_from_u64(fp *r, uint64_t v);                 /* 1 mul (Montgomery conversion) */
void fp_from_limbs(fp *r, const uint64_t v[4]);      /* 1 mul; v < p */
void fp_to_limbs(uint64_t v[4], const fp *a);        /* 1 mul */
void fp_pow(fp *r, const fp *a, const uint64_t e[4]);/* left-to-right; squarings, multiplications and control counted */
void fp_inv(fp *r, const fp *a);                     /* a^(p-2) */
void fp_pow5(fp *r, const fp *a);                    /* 2 sqr + 1 mul */
int  fp_sqrt(fp *r, const fp *a);                    /* Tonelli-Shanks; 0 if a is a non-residue */
void fp_root_of_unity(fp *r, int k);                 /* primitive 2^k-th root, = GEN^(2^(32-k)) (counted) */

/* ------------------------------------------------------------------ arena (arena.c) */
void *xalloc(size_t bytes);                          /* LIFO stack allocator from a static arena in bss */
void  xfree(void *p);                                /* must be the most recent live allocation */
#define NEWFP(n) ((fp *)xalloc((size_t)(n) * sizeof(fp)))
size_t arena_size(void);
size_t arena_hwm(void);                              /* high-water mark (bytes) over the run */
size_t arena_used(void);
size_t arena_stage_peak_reset(void);                 /* returns the peak since the last reset, resets to current */

/* ------------------------------------------------------------------ threads (par.c) */
#define TH_START 100      /* declared charge per thread start */
#define TH_JOIN  100      /* declared charge per thread join */
#define TH_CHUNK 10       /* declared charge per dispatched chunk */
#define NCHUNK 256        /* largest chunk count of a parallel loop (independent of the thread count) */
#define CHUNK_MIN 256     /* elements per chunk at least */
#ifndef PAR_MIN
#define PAR_MIN 4096      /* loops over at least this many elements run as parallel regions */
#endif
extern int g_threads;
extern uint64_t g_regions, g_active_sum, g_chunk_sum;   /* regions, sum of active threads, sum of chunks */
/* run fn(arg, lo, hi) over the nch fixed chunks of [0, n) (nch a power of two; 0: one serial call, no charges) */
void par_range(size_t n, size_t nch, void (*fn)(void *arg, size_t lo, size_t hi), void *arg);
size_t par_chunks(size_t nel);                       /* fixed chunk count for a loop of nel elements (0: serial) */

/* ------------------------------------------------------------------ transforms (ntt.c) */
extern int ntt_nmax, ntt_ntab;    /* L = 2^nmax: state length of the two-level tables; 2^ntab: largest transform */
void ntt_init(int nmax, int ntab);/* roots, twiddle table (2^ntab / 2 entries), small tables; counted */
void ntt_dif(fp *x, int n);       /* in place, natural -> bit-reversed order; values at w_L^k at position brev(k) */
void ntt_dit(fp *x, int n);       /* in place, bit-reversed -> natural; result = L * coefficients */
void ntt_root(fp *r, int n);      /* w_{2^n} (uncounted copy of a table value; n <= nmax+1) */
void ntt_invL(fp *r, int n);      /* 2^-n (one charged load) */
int  ntt_npass(int n);            /* passes of the plan of a length-2^n transform */
void ntt_dif_range(fp *x, int n, int p0, int p1);   /* DIF passes [p0, p1) */
void ntt_dit_range(fp *x, int n, int p0, int p1);   /* DIT passes [p0, p1) (run in reverse order) */
enum { FZ_SQ, FZ_SQX, FZ_OU, FZ_OUX, FZ_MG, FZ_FM };
/* fused passes of the Montgomery step (length 2^nmax): last DIF pass + op + first DIT pass;
 * last DIT pass + twist (untwist: with 1/L) + first DIF pass */
void ntt_fused_last(fp *x, int op, const fp *gi, fp *o, const fp *go);
void ntt_fused_first(fp *x, int untwist);
/* two-level tables (built by ntt_init for the length L = 2^nmax, N = 2L, zeta = w_N):
 *   twist:   x[j] *= zeta^j        (j < L)          tw_mul(x, len, mode)
 *   untwist: x[j] *= zeta^-j / L   (j < len)
 *   brev-x:  E[i] *= w_L^brev(i), O[i] *= zeta^(2 brev(i) + 1)   (values of x at the even / odd points) */
void tw_twist(fp *dst, const fp *src, size_t len, const fp *scale);   /* dst[j] = src[j] zeta^j (* scale), j < len */
void tw_untwist(fp *x, size_t len);                                   /* x[j] *= zeta^-j / L */
void tw_xmul(fp *x, int odd);                                         /* multiply values by x (length L) */
void tw_point(fp *s, fp *sinv2, size_t pos);                          /* s = zeta^brev(pos), sinv2 = 1/(2 s) */
/* pointwise loops (length n, parallel when large); all charged */
void pw_copy(fp *d, const fp *s, size_t n);
void pw_zero(fp *d, size_t n);
void pw_scale(fp *d, const fp *s, const fp *c, size_t n);            /* d = s * c */
void pw_mul(fp *d, const fp *a, const fp *b, size_t n);              /* d = a * b */
void pw_sqr(fp *d, size_t n);                                        /* d = d^2 */
void pw_sqr_mul(fp *d, const fp *b, size_t n);                       /* d = d^2 * b */
void pw_sqr_fma(fp *d, const fp *b, const fp *c, size_t n);          /* d = d^2 + b * c */
void pw_fma(fp *d, const fp *b, const fp *c, size_t n);              /* d = d + b * c */
void pw_add(fp *d, const fp *a, size_t n);                           /* d += a */
void pw_sum(fp *d, const fp *a, const fp *b, size_t n);              /* d = a + b */
void pw_addscale(fp *d, const fp *a, const fp *c, size_t n);         /* d += a * c (c scalar) */
void pw_sub(fp *d, const fp *a, size_t n);                           /* d -= a */
void pw_rsub(fp *d, const fp *a, size_t n);                          /* d = a - d */
void pw_negcopy(fp *d, const fp *a, size_t n);                       /* d = -a */

/* ------------------------------------------------------------------ polynomials (poly.c) */
/* a polynomial is (fp *c, long deg), deg = -1 for 0 */
int  ceil_log2(size_t n);
long poly_deg(const fp *a, long maxdeg);                             /* scan for the top nonzero (charged) */
void poly_mul_school(fp *r, const fp *a, long da, const fp *b, long db);   /* r: da+db+1 entries */
/* r[0..outlen) = (a*b mod x^(2^n) - 1)[lo .. lo+outlen), via 2 forward + 1 inverse transform of length 2^n; a, b
 * may be longer than 2^n (folded); bufA, bufB hold 2^n elements each */
void poly_mul_cyc(fp *r, size_t lo, size_t outlen, const fp *a, size_t la, const fp *b, size_t lb, int n, fp *bufA, fp *bufB, int neg);
void fold_in(fp *dst, const fp *src, size_t len, int n, const fp *scale);   /* dst[0..2^n) = src mod x^(2^n)-1 (* scale) */
void poly_mul(fp *r, const fp *a, long da, const fp *b, long db);    /* full product (allocates) */
/* h[0..P) = f^-1 mod x^P (f(0) = 1, f given by f[0..min(P, lf))); scratch: 2 * 2^ceil_log2(P) elements */
void series_inv(fp *h, const fp *f, size_t lf, size_t P, fp *scratch);
/* q = a div b (da-db+1 entries); a[0..db) := a mod b; returns deg(a mod b) (-1 for 0); schoolbook or Newton */
long poly_divrem_ip(fp *q, fp *a, long da, const fp *b, long db);
#endif
```

### stages.h

```c
/* Interfaces of the stages: line.c (line, F(W), stage B, back-map, reference hash), powmod.c (stage C),
 * hgcd.c (stage D), root.c (stage E), main.c (progress lines). */
#ifndef STAGES_H
#define STAGES_H
#include "orch.h"
typedef struct { fp UQ, VQ, a, b, d[3], kappa, alpha[3], beta[3]; int ok; } line_t;
void bound_since(cnt_t s0);
void line_setup(line_t *L);
void tail_eval(fp *out, const line_t *L, const fp *W);
void ref_hash(fp *dg, const fp *nk, const fp *rho);
void map_back(fp *nk, fp *rho, const line_t *L, const fp *W);
int  build_g(const line_t *L, const fp *c, size_t m, fp *O, fp *GI, fp *GO, fp *lam);
/* powmod.c: stage C.  In: O = L g_raw, GI, GO, lam from build_g.  Out: E[0..m) = S^((p-1)/2) mod g - 1 ... see powmod.c */
typedef struct { int j, steps, xsteps; size_t P; cnt_t newton, start, loop, fin; } powinfo_t;
int  powmod_mont(size_t m, fp *E, fp *O, fp *GI, fp *GO, const fp *lam, powinfo_t *pi);
void mont_step(fp *E, fp *O, const fp *GI, const fp *GO, size_t m, int bit);
void mont_final(fp *E, fp *O, const fp *GI, const fp *GO, size_t m);
void mont_step_f(fp *E, fp *O, const fp *GI, const fp *GO, int bit);
void mont_final_f(fp *E, fp *O, const fp *GI, const fp *GO, size_t m);

/* hgcd.c: stage D */
long gcd_lean(fp **res, fp *U, long du, size_t capU, fp *V, long dv, size_t capV);
typedef struct { uint64_t hgcd_calls, outer_steps, quot_deg_ge2, divisions, max_qdeg, apply_blocked, aborted, tests;
                 cnt_t c_base, c_apply_in, c_apply_out, c_div, c_qstep, c_matmul; } gcdinfo_t;
extern gcdinfo_t G_info;
/* root.c: stage E */
int  root_isolate(fp *S, const fp *G, long dG, uint64_t *tries);
extern uint64_t root_round_max;
/* progress line on stderr (fixed declared charge) */
void progress(const char *fmt, ...);
#endif
```

### consts.h

```c
/* Generated by gen_consts.py from orchard-pallas-constants.json; Montgomery form (R = 2^256). */
#ifndef CONSTS_H
#define CONSTS_H
#include <stdint.h>
#define P_LIMBS { 0x992d30ed00000001ULL, 0x224698fc094cf91bULL, 0x0000000000000000ULL, 0x4000000000000000ULL }
#define P_NINV 0x992d30ecffffffffULL /* -p^-1 mod 2^64 */
#define MONT_ONE { 0x34786d38fffffffdULL, 0x992c350be41914adULL, 0xffffffffffffffffULL, 0x3fffffffffffffffULL } /* R mod p */
#define MONT_R2 { 0x8c78ecb30000000fULL, 0xd7d30dbd8b0de0e7ULL, 0x7797a99bc3c95d18ULL, 0x096d41af7b9cb714ULL } /* R^2 mod p */
#define CAP_M { 0x992d30ed00000001ULL, 0x58dd1194094cf913ULL, 0xedcb381fb5983723ULL, 0x3ffffffffffffffeULL } /* 2^65, the capacity element */
#define GEN2_32_M { 0xa28db849bad6dbf0ULL, 0x9083cd03d3b539dfULL, 0xfba6b9ca9dc8448eULL, 0x3ec928747b89c6daULL } /* 5^((p-1)/2^32), primitive 2^32-th root */
#define E5INV_LIMBS { 0xe0f0f3f0cccccccdULL, 0x4e9ee0c9a10a60e2ULL, 0x3333333333333333ULL, 0x3333333333333333ULL } /* e = 5^-1 mod (p-1) */
#define PM1H_LIMBS { 0xcc96987680000000ULL, 0x11234c7e04a67c8dULL, 0x0000000000000000ULL, 0x2000000000000000ULL } /* (p-1)/2 */
#define PM2_LIMBS { 0x992d30ecffffffffULL, 0x224698fc094cf91bULL, 0x0000000000000000ULL, 0x4000000000000000ULL } /* p-2 */
#define TS_Q_LIMBS { 0x094cf91b992d30edULL, 0x00000000224698fcULL, 0x0000000000000000ULL, 0x0000000040000000ULL } /* (p-1)/2^32, odd */
#define TS_QP1H_LIMBS { 0x04a67c8dcc969877ULL, 0x0000000011234c7eULL, 0x0000000000000000ULL, 0x0000000020000000ULL } /* (q+1)/2 */
#define TS_Z_M { 0xa28db849bad6dbf0ULL, 0x9083cd03d3b539dfULL, 0xfba6b9ca9dc8448eULL, 0x3ec928747b89c6daULL } /* 5^q: a primitive 2^32-th root (5 is a non-residue) */
static const uint64_t RC_M[64][3][4] = {
  { { 0x2d6110568f8fb1cdULL, 0xe436f09787ae5fc6ULL, 0x51ea32d50f7be93fULL, 0x3ee3b205efa6ab5dULL }, { 0x5564975171925a88ULL, 0x4ccc244f2b4cee87ULL, 0xa473a9e22140ab94ULL, 0x293983c6cd66b132ULL }, { 0x1650a1e8d6eb3b9dULL, 0xe1d084ae973c80a4ULL, 0xc6b0e48a821b7324ULL, 0x26f40bdecf47ed19ULL } },
  { { 0xc6687b9c41161a23ULL, 0x7132cacb8362ca7aULL, 0xd85a41c272c6bbb5ULL, 0x201e196e95c1d5a7ULL }, { 0xfac81e29844529d7ULL, 0x55cd21dd6e3519aaULL, 0xdac6e75068b2d6e6ULL, 0x1db160cfe68f1791ULL }, { 0xd0380768fd7d233eULL, 0x1e9be9783f636613ULL, 0x072a39e85b32c9c0ULL, 0x12451bc216857272ULL } },
  { { 0x28238cb2f9610a03ULL, 0xa5bf3dbbb71c1a95ULL, 0xcfa2634c3dcdc1cfULL, 0x30d475d91c9d2660ULL }, { 0xe54edcbe9506d50dULL, 0x6336d456820cd730ULL, 0x62f946f09a61cd4cULL, 0x3dbf6a7660d1c1f2ULL }, { 0xa1f0f09ab6b52ec7ULL, 0xa0256009a9a655c0ULL, 0x02d87cd8131e6863ULL, 0x1d82928e0581f03dULL } },
  { { 0xd40988e46aa0d84aULL, 0xcb83b98a6c3311b6ULL, 0x1faecd3d4f5ba6feULL, 0x21816a2ace1e6ceeULL }, { 0x12966345b9eb55e6ULL, 0xe7207d68cede2273ULL, 0xc5e2cfe134e17a59ULL, 0x3b77812fa31cbea0ULL }, { 0x7c6cf91aa5ec91b8ULL, 0x788439799fc5e819ULL, 0x420b62303e699297ULL, 0x03cf4743b88562d7ULL } },
  { { 0x62a23ec7246945beULL, 0xf0ce22ea72865fbdULL, 0x656887c5d7179774ULL, 0x0387c6accf862ddbULL }, { 0x3a8498acade3e889ULL, 0x11837e2c04524a39ULL, 0x1d734b9714471abcULL, 0x123cb78b6fa1e7f0ULL }, { 0xd9e655459801f98aULL, 0xfc579cc290c7c6f9ULL, 0x2027d70ac2d2c545ULL, 0x347d84f327297c50ULL } },
  { { 0x0c514cbe25cd5dceULL, 0xecce789089b36388ULL, 0xe8ae18e6cf5c2d28ULL, 0x09508b80b79c153cULL }, { 0xf1c79b4f210c1577ULL, 0x39d1fa61fe64ebd8ULL, 0xb8d92fd604863955ULL, 0x16356b23d117fcf8ULL }, { 0x075b151491dd1191ULL, 0x61dc8c496394e6dbULL, 0x3db07ac8572c1d58ULL, 0x0cd7d3fd2c41152eULL } },
  { { 0xf2f6633139c4b05eULL, 0x01dbcb2916c3253dULL, 0xf1172b5fa58201e9ULL, 0x16ce288f5de472a7ULL }, { 0x74b411041f0f061bULL, 0x119ca91c82f60867ULL, 0x88a45446cea98b5fULL, 0x3f947ecf9f672579ULL }, { 0x9bc2a35b9de62d46ULL, 0x040c50a583d292a1ULL, 0x1f62387715c339a0ULL, 0x2b0e1ed4a55c9b51ULL } },
  { { 0x0988c91b9e85fef9ULL, 0xe8ad133faa5d1bcdULL, 0xd8df562e7b09d6efULL, 0x0ce401a7279eeb38ULL }, { 0xc4dfd87b16cb67c7ULL, 0x63d16458323b64bcULL, 0xc8c653cf8e63bcccULL, 0x11242b4450a3daa4ULL }, { 0x6768a64cd32ee7f7ULL, 0xc2e49f96bbd21fb0ULL, 0x97aae974ebac14cbULL, 0x01d1a1069ea732f8ULL } },
  { { 0xd11a4d50cdf5c831ULL, 0xf0141a1730a04151ULL, 0x4839556e137af540ULL, 0x337fc238de198aacULL }, { 0x65126e84b58b3ba7ULL, 0xc8d56c47b3b29eeeULL, 0x8f7755c67ad08f38ULL, 0x032b374daf0f5daeULL }, { 0x03c37d36570461bdULL, 0xf7af83659d08e8f8ULL, 0x5ab5a972d3ed3a2cULL, 0x3ea0dc7d347f4499ULL } },
  { { 0x6c9388c1bf9426b6ULL, 0x6ef2023f27f48878ULL, 0x4858081b3f9d5fc7ULL, 0x022a53a4a03a61b2ULL }, { 0x8d8bbf6d29f2c488ULL, 0xf1fb6efb14f6c308ULL, 0x12566c68cdf47685ULL, 0x2874c6e0c2f51250ULL }, { 0x0cbd4d8959832848ULL, 0x0be4c3aaeae1eec8ULL, 0x8ff6a34de0e0041bULL, 0x35a497e0ae1c0c6fULL } },
  { { 0xf265123421944696ULL, 0x58c83e93fd718498ULL, 0xf5d679bbfa9b691dULL, 0x16394bccd2d2fddaULL }, { 0x6b0b7673c8d01fe1ULL, 0x43d92fddf33b2e84ULL, 0xc2c2fb35e711d5baULL, 0x3310e80bcf0c079cULL }, { 0xba2001a87d410461ULL, 0x92db1732f98ac5bfULL, 0x46b53d2f258b21a0ULL, 0x2431dc11acaf9487ULL } },
  { { 0x4e5eac0c7809dac9ULL, 0x88d278a88757b06dULL, 0xb1caa105e8cfd525ULL, 0x38c5e465b0998789ULL }, { 0x8d582cd16028d0b6ULL, 0x02f5f6f2049341fbULL, 0x14da884cd65b6d4cULL, 0x175b5e71ccbd92ccULL }, { 0x7a4f279b84faae3fULL, 0xdc9cf712aa7020eaULL, 0xd282adb6f153c7ceULL, 0x3dc87f51bee14157ULL } },
  { { 0x54cf83685b98d9ecULL, 0xf982055b2e3f539fULL, 0xa9150eebebecca51ULL, 0x101de276dcdc3feaULL }, { 0x07ff3281e556dffaULL, 0x8e411f5f9f08c47aULL, 0x901151014e2336c7ULL, 0x051670efbebe0450ULL }, { 0x9e49643f069395b7ULL, 0x28bf9db3e38928cdULL, 0x8c02c832008df673ULL, 0x079d4a1265f1f9b8ULL } },
  { { 0x174d2c5549935069ULL, 0xf449d64ba7afd980ULL, 0x17489be3cbeb8217ULL, 0x3dde70f1a49ecc6cULL }, { 0x7dfd80ab7fad4deeULL, 0x8f7d70f1057b7365ULL, 0x432c8e8ae0ea2f2dULL, 0x21a4f21cbad39e96ULL }, { 0x97383a22729d1abaULL, 0x4120a9e5df48c0aeULL, 0x0ac4c5efc2eedad4ULL, 0x1b96fd1670bdf887ULL } },
  { { 0x663798be9e2ca816ULL, 0x74a1d330e5c2746dULL, 0xaf106b2043e0b1cdULL, 0x1d3b129ea32c0690ULL }, { 0x623d1657253b3822ULL, 0xde6cd3acc6c1e3daULL, 0x1bbcb5725404e77dULL, 0x1555343383b9e912ULL }, { 0x5e942b15b6542262ULL, 0x99c8b631c5e985c4ULL, 0x22cd0b12f24838eaULL, 0x342e25680ac0f457ULL } },
  { { 0xacee1be8258f1974ULL, 0x330f1daa7a0a82d3ULL, 0x30cf05803e57f42fULL, 0x05af97ff16360de2ULL }, { 0xf60d13bc70fb7261ULL, 0x89323aa335da65e0ULL, 0xa230cf39306ada27ULL, 0x37ec8d60f94c0e00ULL }, { 0x77cb61b22f0fef36ULL, 0x97b9c176aa4f29dcULL, 0x753951ba534b64ccULL, 0x39d864f4db0d66e5ULL } },
  { { 0x1c93a280de7e6390ULL, 0x89bbe99192d5942bULL, 0xd298630838ac97b4ULL, 0x1fdee9515ec23733ULL }, { 0x1b1500ea3ea52e7cULL, 0xab66b5200e504be8ULL, 0xf2ca2fc2dd1238ceULL, 0x2e99ac0058887a8eULL }, { 0x797a75c017355c08ULL, 0x95753d5fbfe4b639ULL, 0x99d90146a1022ee1ULL, 0x18c6c282437c0106ULL } },
  { { 0x28c41cb0f6a427aaULL, 0x7a6274209547e747ULL, 0x409958bab0ce8004ULL, 0x0f5c9a21669c3561ULL }, { 0x4f458041d5a49e9aULL, 0x70bf9be212724995ULL, 0x16bb868a425b1357ULL, 0x11bbfdbd72e6c273ULL }, { 0x840d988bb266eb39ULL, 0x32ee4645ac430194ULL, 0xdf94525d6b695073ULL, 0x26f7032e169d741eULL } },
  { { 0xed032a7242155f1cULL, 0xd3bf87a6d0fc1c34ULL, 0x6e6b7f2bba883e7aULL, 0x03bee947acf8d869ULL }, { 0x54124791da75f84cULL, 0xdea3fdd86d09154cULL, 0xa8b1b78ee689124bULL, 0x08cc569a704f8ae7ULL }, { 0x16e420feed279927ULL, 0xd4e9f90a2430cadeULL, 0xbda76f8c724ed3c4ULL, 0x26f0c2eb7941a2edULL } },
  { { 0xfa8bcd50c49a6dc1ULL, 0x1b75bef3f3b40443ULL, 0x16306d7f83e6e86fULL, 0x2cb265185a682f74ULL }, { 0x816198532054502fULL, 0xa53e572f12c3401fULL, 0xe9a8f617740903c3ULL, 0x2c9ba61ca6f41275ULL }, { 0xf5b6a307021d72c4ULL, 0xf9b09e3b204957faULL, 0x1ef85c62ca5473eeULL, 0x0efc66dcec9a30aeULL } },
  { { 0x005b369d1ddec201ULL, 0x1a842b0d7196bbe6ULL, 0x737adf896a50cea4ULL, 0x236df79cb9f4188bULL }, { 0xea5b61d7bd606ab0ULL, 0xccb039d4615a540eULL, 0x1408af70b00d1a59ULL, 0x225863cd3b10bb9dULL }, { 0x6cb2f4bcc26de564ULL, 0xbb358e5aee7406abULL, 0xf08ffcbb81863becULL, 0x00f144f53402205fULL } },
  { { 0x47dac6922bd0e686ULL, 0x7d618f7ba9d32c8eULL, 0x6118919ff121628cULL, 0x074faa94927b7786ULL }, { 0x3af193a3ff7b9d4dULL, 0x5b4be86fcf9052b0ULL, 0xa9433b495aa64416ULL, 0x041c30de6dcc571eULL }, { 0x3d90f898029f92e2ULL, 0xfcbb9e4743c48e1dULL, 0x20bc4ddedcf505afULL, 0x0ce8a49fa10949e7ULL } },
  { { 0x6bb524c3db961189ULL, 0xe93f7a4d2c5cd069ULL, 0xc7c572085a58c1f2ULL, 0x157be04d9af4f4b7ULL }, { 0xcce74e4ac292398dULL, 0xaed371d912fb1d56ULL, 0x356e0c2dbf7bc066ULL, 0x3514dcf22466a19fULL }, { 0xfd1e5928b50de13cULL, 0x00f1d7fb3cb6d5ffULL, 0xfe3bd8a8f595d931ULL, 0x2aef30e01461acebULL } },
  { { 0xa86cd7f133554ebbULL, 0x094a97d9d8908309ULL, 0x3de9cf716c0e5531ULL, 0x2a215295d3b86a1cULL }, { 0xd53c009bb1e61c5cULL, 0xfb9b2a40c066fa76ULL, 0xfc69157a958ea7d9ULL, 0x2a396665f94e134fULL }, { 0xf86e48d38ebb1402ULL, 0x06e4f55e6bfb3e89ULL, 0x16bf492bbf874eb3ULL, 0x335d71a30027eccdULL } },
  { { 0x1e4bb73ffb93a6d1ULL, 0x9ef465a03f553915ULL, 0xa986466f8cb39340ULL, 0x344b522709d83fd6ULL }, { 0x54d1385a73cedc14ULL, 0x554f9d50f1aa4237ULL, 0x6c40c2c46e70eb08ULL, 0x08d14481b53d311cULL }, { 0x1424438d34dfc1daULL, 0x2409171b46a1ca37ULL, 0x1a1c4cfb701efcc3ULL, 0x3238d087fe0f487bULL } },
  { { 0xe4e41151ef95cfa8ULL, 0x5ac9a18bf328f9a7ULL, 0xa74bc957b4f0312fULL, 0x2a7229e81bd17e27ULL }, { 0x128b64e508a63bd9ULL, 0xbc72e63f546c4584ULL, 0x88cf7accb6e0e0eeULL, 0x113c3d59a596d700ULL }, { 0xf4d7b2de93df79c1ULL, 0xd48511fd9b630fa2ULL, 0x66d2195a8ed94ca5ULL, 0x1c0c0ca45eee2c44ULL } },
  { { 0x466d86d03c2466caULL, 0x8227a59ab7462664ULL, 0xd2fd28964ffc5f0eULL, 0x047b0867cd0bb8bcULL }, { 0xd789d21c1d4ea83cULL, 0x7401f29ebae79841ULL, 0xe0abd0eb46b46cb8ULL, 0x28e0786cd4de5a8fULL }, { 0x7402eeab3141e20fULL, 0xd768b71e6068c79bULL, 0x3db2195fe3a15590ULL, 0x2ae0bdb635468021ULL } },
  { { 0xc16e17aec4c8c257ULL, 0xcbe2e0daf07542ffULL, 0xbfe62521350c02fbULL, 0x1228614aa1224324ULL }, { 0x75e7f93077ae107aULL, 0x4393dd80790be351ULL, 0xdff377ea2fa44416ULL, 0x1e8508e864d3a7c5ULL }, { 0xb1ec20078a1957fdULL, 0x763ab46a70baa519ULL, 0x7738685a419fd1cbULL, 0x2a5e0a5a9db64745ULL } },
  { { 0xc22212c67483d82eULL, 0xa75cc24295d6ff8dULL, 0x7992eb54a6a2ed5dULL, 0x07404560d0b2cbd5ULL }, { 0x2a285911ee339ba5ULL, 0x8893e0badb13c939ULL, 0xd83525d7431b9b62ULL, 0x25f63b980e96e6dbULL }, { 0xa15a39ed0b3d0589ULL, 0xd368b459a4b900e0ULL, 0x4efa56d549364219ULL, 0x0b5ca2beedd7dd3eULL } },
  { { 0xeb7ba4127d2e6354ULL, 0x6986145a2941fb14ULL, 0x0e3e7c6c97a14312ULL, 0x1ed53f1aa1bf808fULL }, { 0xaf8ab4c0d2b2669dULL, 0x7e7a7326eb971e3fULL, 0xa2d3848e9ce2fc69ULL, 0x29ea52e7093a43d4ULL }, { 0x1e72622bdb4569a9ULL, 0x874356996d93fcdeULL, 0x5c7c464758b32bc2ULL, 0x105fe2acbcc84897ULL } },
  { { 0x0653a67e86f62c0fULL, 0xda058f0b6767498aULL, 0xa49ef164a0280442ULL, 0x348a3f44e29a1db3ULL }, { 0x4ebc09df098dddf4ULL, 0x7953e2582fc1806cULL, 0x4c7c4749054887c8ULL, 0x0ea7f29878781fb8ULL }, { 0x9e9e28ff373a00a1ULL, 0x59d68a2c32f0aeaeULL, 0x030aa50eb0d116f4ULL, 0x265063100e234ee0ULL } },
  { { 0xc65436d24cba466aULL, 0x461c6791d1c4df7bULL, 0x44a880f485ffa101ULL, 0x3fbc3cf75118c62eULL }, { 0xd77ac655ca67b1c2ULL, 0x76d88fda6b1d115cULL, 0x089c758c1ba6ef20ULL, 0x0964db39bd4b200bULL }, { 0xbd5667e04c034a11ULL, 0x5d4c63fffa29c3a1ULL, 0xf6831d76df36eaa1ULL, 0x255644c108880d6dULL } },
  { { 0xafa80ea9d8392946ULL, 0xb374fe3c3d852b90ULL, 0x6ac7be0421200289ULL, 0x20e4c096c4dd72e6ULL }, { 0x7896f449e943831eULL, 0x1ce40ea3c4383e92ULL, 0xb49ab8f65a18dfb3ULL, 0x022f6ae3e0d1f236ULL }, { 0x3befcfdbe8dd042cULL, 0x1f23c41b8459e28cULL, 0x9d3df3e0c372ff8aULL, 0x18dc26fa862b191eULL } },
  { { 0x56dd436505fd7a95ULL, 0xde6df28980a2b7d9ULL, 0x0363df341e40f38bULL, 0x07e2bca200e16abaULL }, { 0xd411d472d8dc23daULL, 0xf50cfab4071be3cfULL, 0x3c259a5e3e76eb62ULL, 0x0ac0b7df209f51acULL }, { 0x5ed3556cb6eccdaaULL, 0x5a77f234139d70b3ULL, 0xfcb189da416e3bcaULL, 0x0cafd03316e3da67ULL } },
  { { 0x3ded6d76360a45beULL, 0x6c429cb169faa590ULL, 0x2fb017c34a83a077ULL, 0x31f542859f15f500ULL }, { 0x3429130c2c719a28ULL, 0x2c9ef140b71e34edULL, 0x483fc18d0a310a87ULL, 0x1495571d0705997cULL }, { 0x3af7365d394648aeULL, 0x5cf1b21e24262136ULL, 0xc0fc62acf9bb6f72ULL, 0x1115c26a2fa746d9ULL } },
  { { 0x8099beda71efd72fULL, 0xd36c358a6cb42b28ULL, 0xeec3d42dc5d22579ULL, 0x22193d634f4398d4ULL }, { 0x69fa4c8431c72241ULL, 0x3d493a2870de9ecaULL, 0xfa85379fa7f96e96ULL, 0x06ed1793aac4bac5ULL }, { 0x469e500151fe112eULL, 0xf15b462bf229e21fULL, 0xf700e5a684cc210eULL, 0x208c794ee061495bULL } },
  { { 0x42e1de787c5ac045ULL, 0xdaf7f483c5ac2542ULL, 0x3a179e90ac57dc06ULL, 0x3ccede2a70073e55ULL }, { 0x9907bebdd515efcdULL, 0x5c5759cc9d41d88aULL, 0x3674aac584e9815eULL, 0x256eccb4ae6815a8ULL }, { 0xfbecb087cd94ed86ULL, 0xe2c856bd76367ef6ULL, 0x4eb80ed90b2de128ULL, 0x259f3b2f4d72a341ULL } },
  { { 0x8aee7138a3e493efULL, 0xc097e3916e39d301ULL, 0x3f4edaab5fade903ULL, 0x26341785bebb55d1ULL }, { 0x81743dbd685bfc78ULL, 0x51e1df5405018bb4ULL, 0x5e7f09f43fab73dcULL, 0x300dc575584e1165ULL }, { 0xcf5e72012088079fULL, 0x5ee47f6039ea45b0ULL, 0x1376a4ad287da55cULL, 0x15c592ab8709a775ULL } },
  { { 0xd1ba83ae61ab349cULL, 0x54c4ebfa46c6c5ddULL, 0x6811f417646c4a9bULL, 0x0304e5f3b22fd1e6ULL }, { 0x96b0a28615104eebULL, 0xddc28384fa498de1ULL, 0x2e588de186363997ULL, 0x35279da4cf2bc018ULL }, { 0xd0533b7b914aa30eULL, 0xf91091f7f642e389ULL, 0xe768cc728d9ffd9fULL, 0x3512143a077d0fa6ULL } },
  { { 0xa64b6584aa7777b6ULL, 0xa9ecd008c97413bdULL, 0x42db693e89469246ULL, 0x000f9bd1021c5922ULL }, { 0x0208b8d66e15fe3bULL, 0xeb7cb55bbc327ae8ULL, 0x63a2418e20a3ba6cULL, 0x38a5ea6f82db3d5dULL }, { 0x9a649745f40e953eULL, 0x9d6406d52cb622f5ULL, 0x200a4cbd0f1f267cULL, 0x3db51a34b6e9fe06ULL } },
  { { 0x17c83056e2c382a1ULL, 0x2f4c8b882d658eb4ULL, 0x96acd13fcc26bf82ULL, 0x000c6a1b1bf90012ULL }, { 0xf616d545a5d3e939ULL, 0x2af7464619d365cbULL, 0xf097308d468c947dULL, 0x291ffc707a48e2ccULL }, { 0xd3b637e65a834971ULL, 0x8fa7365afde54fe7ULL, 0x118cc5ff60f24404ULL, 0x1430b62cbd021f4aULL } },
  { { 0xab3d6c0df3ce0ca0ULL, 0x08144b4c79d86499ULL, 0xf91d2462d75a2286ULL, 0x2bf52870c017cf4eULL }, { 0xe5e5488d5162898eULL, 0xe83c6c0ca21e9962ULL, 0x66f17a5cce9bd5eeULL, 0x0faa86932fc9ec52ULL }, { 0x6a601060296db14dULL, 0xecf3cf47c1dc4442ULL, 0x6a950536b5584542ULL, 0x313de4b333fc8118ULL } },
  { { 0xc2bb2bdb161c0d43ULL, 0xe42240232ae44172ULL, 0x305435bec7528b04ULL, 0x2da4e7173aee4d48ULL }, { 0x923370757c286129ULL, 0xbf9fcef7fa21e1f3ULL, 0x0e1971e6add36a32ULL, 0x05f07747dffb6336ULL }, { 0xb63765a7f3c491d9ULL, 0xc6da1f9e3e9828c7ULL, 0xde242a4e2279090dULL, 0x2cca495816249692ULL } },
  { { 0x1ff64be92cab7091ULL, 0x3d79404b46d72eb9ULL, 0x1710f1c5af14541aULL, 0x0ebaf248a381fe31ULL }, { 0xa40aa7f2f4be8e45ULL, 0x135a66ac8749ce1cULL, 0xd8d76ea87865c570ULL, 0x044ec20c80c90b04ULL }, { 0x4a9da72cba665450ULL, 0xd5295d8e27bb7bfbULL, 0x3626ca8c336dd990ULL, 0x022408a1fb0b3800ULL } },
  { { 0x8446ea40f76089b3ULL, 0xdbfa50f0a581e128ULL, 0xd7685cd42f8f7c21ULL, 0x398f3c2662df6e9aULL }, { 0x37d44d6ed12e5836ULL, 0xdd62ee99a8b6cc55ULL, 0xaf6d348d1857a659ULL, 0x1f9c9041980969afULL }, { 0xf749702efd480758ULL, 0x323710fe973ef206ULL, 0xddb2efafff6e26bfULL, 0x3281013f35baa4d1ULL } },
  { { 0x36f8bf09755e3fd1ULL, 0x5d77e2be7cd25b26ULL, 0xb3f18051ec66d481ULL, 0x228b840f19b7f6edULL }, { 0x1e20bd7e9007dc99ULL, 0x7f9c083ce884876dULL, 0xb113ce50640f20f6ULL, 0x2bf716d6b3cd9a18ULL }, { 0xe0f986df949e09f8ULL, 0x32d8dd9249948d2eULL, 0x9ae905c32961e96fULL, 0x30553eb90e4d277aULL } },
  { { 0x2acddfb558ce6fd8ULL, 0xc70f8fcddfdb34a1ULL, 0xfa66e72c6937e86fULL, 0x385df4d2ddcdcaa5ULL }, { 0x3e7465e402206318ULL, 0xf6ead3f9d9e048b3ULL, 0x619112a188adb41eULL, 0x2c34febcf9def460ULL }, { 0xe8a7c82fa2625b3fULL, 0xaebb23cc8147e2bdULL, 0xf587afa348f34bf0ULL, 0x07ccc87a97eee0b3ULL } },
  { { 0xd679b84eef1994b9ULL, 0x7def28d56667062cULL, 0xac3068742ec64b40ULL, 0x14479d04a6999fefULL }, { 0x1bf627000bfe0e4aULL, 0x1c54cb5d1844ccffULL, 0x76ba72dfe568a18aULL, 0x1eb61f5d4af67fbdULL }, { 0x48f5e53e337b002aULL, 0xa2cd1072d615602fULL, 0x6bb93f9dad34bed7ULL, 0x320e9200e22d4464ULL } },
  { { 0x5aa93dae91a2e4b9ULL, 0xfaacb53728337d8aULL, 0x1081dbb00247523bULL, 0x397bf21666510308ULL }, { 0x8f7f76f47d9ff019ULL, 0x24de8ffa0fad4008ULL, 0x2018e79b576a6bc7ULL, 0x158acea556828e27ULL }, { 0xe905f10b227bbf42ULL, 0xc2edbfc5a426c09fULL, 0xd95d18ff73154263ULL, 0x040333330a351778ULL } },
  { { 0x91a0adc20b096a81ULL, 0x8ed3f92a943f4990ULL, 0x09dca1eb774a58aaULL, 0x3190de39a08e30d0ULL }, { 0xa186477461610158ULL, 0x49dcf00c9a3f4cdcULL, 0xc24bd4292b6300a8ULL, 0x2353ebbae73e6b0bULL }, { 0xd86fe6c3fd5d72d6ULL, 0xcb092c676b2faf59ULL, 0x41de6a751b2ab6b8ULL, 0x36d1c42ec123b236ULL } },
  { { 0x6eeb8c14a580493fULL, 0xa63fafe1762d0433ULL, 0x2535874ab3d5feb7ULL, 0x3f9fd0c9caf16f44ULL }, { 0x097b1331d5d5fdcdULL, 0xb69a099bd2707e4bULL, 0xa00d654aab61139bULL, 0x04a51f72fbc8f91eULL }, { 0xec1ba969b57bc21aULL, 0x757b333a7ffa3b3dULL, 0x0e597273fe4ac666ULL, 0x114d73316180d61bULL } },
  { { 0x042ec88c94422adfULL, 0x84669dfab8f97048ULL, 0xdcc347c19ad69842ULL, 0x293316fbfcb11e39ULL }, { 0x63d9ab3880316efeULL, 0xd06d752adf2b43fcULL, 0xa236c0995704aa60ULL, 0x286ce110716c2974ULL }, { 0x25fd65694898efb4ULL, 0x99cb620dfc63fbcdULL, 0xf3a0a1e1aedec074ULL, 0x097462528778299bULL } },
  { { 0x418c3f6d880e3244ULL, 0x20a933100425e4d5ULL, 0x5366e37bd79dd77dULL, 0x1c5640c60b10f088ULL }, { 0x062556e677ce1aeeULL, 0x551bb969a99a27d8ULL, 0xbd64e65f6d50ce56ULL, 0x3670f79b1ebd37eaULL }, { 0x6340a6e40b2cb449ULL, 0x75a66980082192d0ULL, 0xf26997d2e59968b8ULL, 0x1ba8ef4ddba030a2ULL } },
  { { 0x9e81ed6bcca99ca8ULL, 0xe283e6741c1c8c1aULL, 0x4dcbab4c903e7d6cULL, 0x144287df706d7d35ULL }, { 0xf307d19656785140ULL, 0xf2359f3af40af740ULL, 0x073120eaab4c104dULL, 0x372a560cedb19147ULL }, { 0x0917ef782f366a32ULL, 0x118e0d62997e0761ULL, 0x85a794632bd1186eULL, 0x3fd8af8f75a55735ULL } },
  { { 0x45f1327d29d5bb47ULL, 0x1d267c203c076406ULL, 0x54568d3ebb89dbacULL, 0x050c1e7fd4e0840aULL }, { 0x8918a0f53d47ef87ULL, 0xd801c477ffe38754ULL, 0x6f614c3c03eab522ULL, 0x3e22c9f862e9d961ULL }, { 0x0a6c3b558ff7fb9dULL, 0x916c06f103a297bfULL, 0xfe331bfa4f477e45ULL, 0x02fda085e0882d39ULL } },
  { { 0xe00d560c1922bd80ULL, 0xbe5fb99f7823e7ceULL, 0x9b8ab20ee58d07d2ULL, 0x3cf282a530973229ULL }, { 0x61f5e4a62789d305ULL, 0xe79e5db989d235c2ULL, 0x779fd5723b0e4c8cULL, 0x1fb84c68e272aacdULL }, { 0x9f8bc8af370f0e1fULL, 0x628b777da9608e7aULL, 0x56f3fce27af86d3dULL, 0x3ed0ea844bce3f7cULL } },
  { { 0xa81ca9ad3596718eULL, 0xa2e243ebc26d8786ULL, 0xbdd0c75e49311133ULL, 0x0491f56bad943b95ULL }, { 0x662a89747f07eb48ULL, 0xbfd2949f2198be29ULL, 0x61faee803ba6ad21ULL, 0x0d92b19df57965e5ULL }, { 0x74c0170dcb26b9a3ULL, 0x6e043841ae89ad9cULL, 0x9c21986513bb6c95ULL, 0x32c850785ef8c550ULL } },
  { { 0xed4d002f16bc787fULL, 0x06ebf8cb07196aa9ULL, 0x14eb45e365573e2bULL, 0x25032cef4a7000efULL }, { 0x3b118891deafe0c1ULL, 0x13f9c32f82aa94f5ULL, 0xa02a82d122209fb7ULL, 0x1ce89d10d60cb6f5ULL }, { 0xf371d6ce33fea695ULL, 0x5505eca4ffdb4f3aULL, 0x2c1c430f4a00cc14ULL, 0x18679130f2053d1bULL } },
  { { 0x8f93a25b2e5c3ac9ULL, 0xf65309c16f7c2122ULL, 0x448ec71a1bb9c43fULL, 0x1c9901bfdaead7bbULL }, { 0xce3903ea34b01eb4ULL, 0x3743ef7a61a75b0dULL, 0xc4b3b804343ab52cULL, 0x21525c6921c10348ULL }, { 0x3e58ceccf33d9fd6ULL, 0x0a4405f0f3f9ecddULL, 0x5e439182f7d467e3ULL, 0x2fdbb7666a8d4e93ULL } },
  { { 0xd95c47374d92d769ULL, 0x6e7a4d28152762eeULL, 0x70aca0ccc8b1e64cULL, 0x00224355557620cdULL }, { 0xd546a4caccd86c58ULL, 0x94e61f808ca9e38fULL, 0xd4dcc0ca96cc3b32ULL, 0x19e80175f12ee906ULL }, { 0xdd1c43055a2df184ULL, 0x21ea7e74be932b7bULL, 0xeb9bd9f6301efde3ULL, 0x204f1be7c3153361ULL } },
  { { 0x669a1bfa4452e5b9ULL, 0xb50119f9ba5913e4ULL, 0x376e862381f50e26ULL, 0x2fb4218313d636abULL }, { 0x79c6708a2d8292c2ULL, 0x2684a5342d6e29c4ULL, 0x77efae4ea0f85e94ULL, 0x26a86c00b42234b5ULL }, { 0xacb8a62ec21f1790ULL, 0xa532d1c96fd777b0ULL, 0xbce6beb99cd715c5ULL, 0x2205f95b96860426ULL } },
  { { 0xeea18d332c6ba201ULL, 0x7e49750fe17b0c48ULL, 0x84b958e355658851ULL, 0x1af476c6c11beb7cULL }, { 0xac7444171b9ed2a4ULL, 0xb13b491258203302ULL, 0x7bbd82c67d980d63ULL, 0x288fef4833b6612bULL }, { 0xdb2f5426a3ce3a28ULL, 0xe35f66b7b35fd095ULL, 0xc2911efe8acaa8d3ULL, 0x20adef5e2b2bc83fULL } },
  { { 0x668c5c60dc165271ULL, 0xa20833455f8c9082ULL, 0x7ea98ee735477650ULL, 0x3742df583c401d58ULL }, { 0x76bb56ba0777dd32ULL, 0x57ae5691adfd5bb6ULL, 0xc25cd5eaaad89961ULL, 0x0ba64c73d78f268aULL }, { 0x77f195a810966117ULL, 0x5a4fa67cbe740274ULL, 0xc195daea12525beaULL, 0x116979774227425cULL } },
  { { 0x5d58cfd09c2210bbULL, 0x4ba345d05d37c73aULL, 0x6e8d9dd33f2a5189ULL, 0x1a0e98c3ef88d4cfULL }, { 0x561643bef1c2f375ULL, 0xd28ed380885331acULL, 0xba76d3ad613a46f5ULL, 0x3ef76bf14ed05706ULL }, { 0x0fe0d46abf50f962ULL, 0xb8c8c797af9d04b6ULL, 0xd19d4f33430a128fULL, 0x11ffb1bc451c07d1ULL } },
};
static const uint64_t MDS_M[3][3][4] = {
  { { 0x7c1a669d208e8b4dULL, 0x5f51868647bdf2a3ULL, 0x00fcf9354819f613ULL, 0x3103a7de3b678ebdULL }, { 0xd02c6b7336d40cfaULL, 0x3a1a0851864fb4a7ULL, 0x2282de236a32af60ULL, 0x0e799762bd549615ULL }, { 0xb3624a21289b4249ULL, 0xca6c5877b9c3c7c5ULL, 0xb02a2a0100ebb202ULL, 0x117cb780c908530aULL } },
  { { 0xe3ff3f5c313a6a34ULL, 0x51c6f61bd721544dULL, 0x8ed31b47cae66704ULL, 0x02087f41039c75bbULL }, { 0xd2f9d522444ac1a0ULL, 0xe69ac4d3b9d1c5a0ULL, 0x6edec07987aaee83ULL, 0x1e43c65722df71bdULL }, { 0x10a0d86e38d77e7bULL, 0xf0b93da384af65e0ULL, 0x62ed3679f9a91794ULL, 0x2345494383dd3fb8ULL } },
  { { 0x1ff15b66b7bbe66dULL, 0x75ecdd64110a734fULL, 0x78f0280d37007108ULL, 0x376408280c7418bcULL }, { 0x934d00845da6461dULL, 0x930aa4624cdae4b4ULL, 0xdcd1ebac0098612dULL, 0x2de64334636be38dULL }, { 0x0f957fede68e9322ULL, 0x14ac4b874d7324dbULL, 0x4007b97b032e6d5dULL, 0x22011675ded37456ULL } },
};
#endif
```

### gen_consts.py

```python
"""Generate consts.h: the deployed Orchard constants (round constants, MDS) and the Pallas field
constants, all in Montgomery form (R = 2^256), as 4 x 64-bit little-endian limbs.
Source: the organizer file pareto/orchard-pallas-constants.json (read only).
Usage: python3 gen_consts.py /path/to/orchard-pallas-constants.json > consts.h
"""
import json
import sys

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
R = 1 << 256


def limbs(x):
    return '{ 0x%016xULL, 0x%016xULL, 0x%016xULL, 0x%016xULL }' % tuple((x >> (64 * i)) & (2**64 - 1) for i in range(4))


def mont(x):
    return limbs(x * R % P)


def main():
    d = json.load(open(sys.argv[1]))
    rc = [[int(x, 16) for x in row] for row in d['round_constants']]
    mds = [[int(x, 16) for x in row] for row in d['mds']]
    assert len(rc) == 64 and all(len(r) == 3 for r in rc) and len(mds) == 3
    assert all(x < P for row in rc for x in row) and all(x < P for row in mds for x in row)
    out = []
    out.append('/* Generated by gen_consts.py from orchard-pallas-constants.json; Montgomery form (R = 2^256). */')
    out.append('#ifndef CONSTS_H\n#define CONSTS_H\n#include <stdint.h>')
    out.append('#define P_LIMBS ' + limbs(P))
    out.append('#define P_NINV 0x%016xULL /* -p^-1 mod 2^64 */' % ((-pow(P, -1, 2**64)) % 2**64))
    out.append('#define MONT_ONE ' + limbs(R % P) + ' /* R mod p */')
    out.append('#define MONT_R2 ' + limbs(R * R % P) + ' /* R^2 mod p */')
    out.append('#define CAP_M ' + mont(1 << 65) + ' /* 2^65, the capacity element */')
    out.append('#define GEN2_32_M ' + mont(pow(5, (P - 1) >> 32, P)) + ' /* 5^((p-1)/2^32), primitive 2^32-th root */')
    e5 = (4 * (P - 1) + 1) // 5
    assert 5 * e5 % (P - 1) == 1
    out.append('#define E5INV_LIMBS ' + limbs(e5) + ' /* e = 5^-1 mod (p-1) */')
    out.append('#define PM1H_LIMBS ' + limbs((P - 1) // 2) + ' /* (p-1)/2 */')
    out.append('#define PM2_LIMBS ' + limbs(P - 2) + ' /* p-2 */')
    q = (P - 1) >> 32
    out.append('#define TS_Q_LIMBS ' + limbs(q) + ' /* (p-1)/2^32, odd */')
    out.append('#define TS_QP1H_LIMBS ' + limbs((q + 1) // 2) + ' /* (q+1)/2 */')
    out.append('#define TS_Z_M ' + mont(pow(5, q, P)) + ' /* 5^q: a primitive 2^32-th root (5 is a non-residue) */')
    out.append('static const uint64_t RC_M[64][3][4] = {')
    for row in rc:
        out.append('  { ' + ', '.join(mont(x) for x in row) + ' },')
    out.append('};')
    out.append('static const uint64_t MDS_M[3][3][4] = {')
    for row in mds:
        out.append('  { ' + ', '.join(mont(x) for x in row) + ' },')
    out.append('};')
    out.append('#endif')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
```

### fp.c

```c
/* Field helpers that are not inline: conversions (1 multiplication each), exponentiation, inversion,
 * square root.  Every field operation counts itself; the control of the bit loops is charged next to it. */
#include "orch.h"

__thread cnt_t X;

static const fp R2 = { MONT_R2 };

void fp_from_limbs(fp *r, const uint64_t v[4]) {
    fp a = { { v[0], v[1], v[2], v[3] } };
    fp_mul(r, &a, &R2);                         /* a * R^2 / R = a R: one Montgomery multiplication */
}
void fp_from_u64(fp *r, uint64_t v) { uint64_t w[4] = { v, 0, 0, 0 }; fp_from_limbs(r, w); }
void fp_to_limbs(uint64_t v[4], const fp *a) {
    fp one = { { 1, 0, 0, 0 } }, t;
    fp_mul(&t, a, &one);                        /* a R / R = a */
    memcpy(v, t.l, 32);
}

/* left-to-right binary powering.  Control per exponent bit below the top: loop (3), word index (shift),
 * bit index (mask), shift and mask of the bit (2), test and branch (2) = 9; the search for the top bit:
 * 7 per tested bit (loop 3, word index, shift, mask, test). */
void fp_pow(fp *r, const fp *a, const uint64_t e[4]) {
    int top = 255;
    while (top >= 0 && !((e[top >> 6] >> (top & 63)) & 1)) { top--; CTL(7); }
    CTL(7 + 2);
    if (top < 0) { fp_one(r); return; }
    fp acc = *a;
    for (int i = top - 1; i >= 0; i--) {
        fp_sqr(&acc, &acc);
        CTL(9);
        if ((e[i >> 6] >> (i & 63)) & 1) fp_mul(&acc, &acc, a);
    }
    CTL(2);
    *r = acc;
}

void fp_inv(fp *r, const fp *a) { static const uint64_t E[4] = PM2_LIMBS; fp_pow(r, a, E); }

void fp_pow5(fp *r, const fp *a) { fp t; fp_sqr(&t, a); fp_sqr(&t, &t); fp_mul(r, &t, a); }

/* primitive 2^k-th root of unity: GEN^(2^(32-k)), GEN = 5^((p-1)/2^32) */
void fp_root_of_unity(fp *r, int k) {
    static const fp G = { GEN2_32_M };
    fp t = G;
    for (int i = k; i < 32; i++) { fp_sqr(&t, &t); CTL(3); }
    CTL(2);
    *r = t;
}

/* Tonelli-Shanks, p - 1 = 2^32 q.  Returns 1 and r with r^2 = a, or 0 if a is a non-residue.
 * Equality tests with the constant 1 or 0: 4 limb comparisons + branch = 5 control operations. */
int fp_sqrt(fp *r, const fp *a) {
    static const uint64_t PM1H[4] = PM1H_LIMBS, Q[4] = TS_Q_LIMBS, QP1H[4] = TS_QP1H_LIMBS;
    static const fp Z = { TS_Z_M };
    fp one; fp_one(&one);
    CTL(5);
    if (fp_is_zero(a)) { fp_zero(r); return 1; }
    fp leg; fp_pow(&leg, a, PM1H);
    CTL(5);
    if (!fp_eq(&leg, &one)) return 0;
    fp x, b, c = Z;
    fp_pow(&x, a, QP1H);
    fp_pow(&b, a, Q);
    int M = 32;
    for (;;) {
        CTL(5 + 3);                                 /* test b == 1, loop */
        if (fp_eq(&b, &one)) break;
        int i = 0; fp t = b;
        while (!fp_eq(&t, &one)) { fp_sqr(&t, &t); i++; CTL(5 + 3); }
        CTL(5 + 2);
        fp d = c;
        for (int j = 0; j < M - i - 1; j++) { fp_sqr(&d, &d); CTL(3); }
        CTL(2 + 2);                                 /* loop exit, M - i - 1 */
        fp_mul(&x, &x, &d);
        fp_sqr(&c, &d);
        fp_mul(&b, &b, &c);
        M = i; CTL(1);
    }
    *r = x;
    return 1;
}
```

### arena.c

```c
/* Static arena in the bss with a LIFO (stack) allocator.  Every buffer of the program comes from here;
 * nothing is mapped at run time.  Each executed operation of xalloc / xfree is charged where written. */
#include "orch.h"
#include <stdio.h>
#include <stdlib.h>

#ifndef ARENA
#define ARENA ((size_t)1 << 30)
#endif
#define MAXLIVE 4096

static unsigned char arena[ARENA] __attribute__((aligned(64)));
static size_t top_off;                 /* bytes in use */
static size_t stk[MAXLIVE];            /* start offsets of the live blocks */
static int nlive;
static size_t hwm, stage_peak;

size_t arena_size(void) { return (size_t)ARENA; }
size_t arena_hwm(void) { return hwm; }
size_t arena_used(void) { return top_off; }
size_t arena_stage_peak_reset(void) { size_t p = stage_peak; stage_peak = top_off; return p; }

void *xalloc(size_t bytes) {
    size_t sz = (bytes + 63) & ~(size_t)63;           CTL(2);   /* add, mask */
    CTL(2 + 2);                                                 /* the two capacity tests */
    if (nlive >= MAXLIVE || sz > (size_t)ARENA - top_off) {
        fprintf(stderr, "arena: request of %zu bytes does not fit (used %zu of %zu)\n", bytes, top_off, (size_t)ARENA);
        exit(5);
    }
    stk[nlive++] = top_off;                           CTL(3);   /* store, index, increment */
    void *p = arena + top_off;                        CTL(1);
    top_off += sz;                                    CTL(1);
    CTL(4);                                                     /* two peak comparisons and updates */
    if (top_off > hwm) hwm = top_off;
    if (top_off > stage_peak) stage_peak = top_off;
    return p;
}

void xfree(void *p) {
    CTL(2 + 4);                                                 /* test of nlive, index, load, compare, branch */
    if (nlive == 0 || (unsigned char *)p != arena + stk[nlive - 1]) {
        fprintf(stderr, "arena: non-LIFO free\n");
        exit(5);
    }
    top_off = stk[--nlive];                           CTL(3);
}
```

### par.c

```c
/* Deterministic parallel regions.  A loop of n elements (or blocks) is cut into nch fixed chunks (nch depends only
 * on the loop size, never on the thread count); chunk sizes q or q+1 with q = n >> log2(nch); thread t runs the
 * contiguous chunk range [t*nch/T, (t+1)*nch/T).  Each thread counts into its own thread-local counters; the main
 * thread (thread 0) adds the counters of the others after the region.  Declared charges (counter thr), per region:
 * TH_START + TH_JOIN per active thread (min(threads, chunks)) and TH_CHUNK per chunk (dispatch, including the
 * chunk bounds).
 * Implementation: a pool of T-1 persistent worker threads (stack THREAD_STACK each), woken per region by a
 * generation counter; the charges are those of a start and a join per thread and region. */
#include "orch.h"
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <sched.h>
#include <immintrin.h>

int g_threads = 1;
uint64_t g_regions, g_active_sum, g_chunk_sum;

#define MAXTH 64
#define THREAD_STACK (256 * 1024)
#define SPIN 4000

typedef struct {
    void (*fn)(void *, size_t, size_t);
    void *arg;
    size_t n, nch, c0, c1;
    cnt_t out;
} job_t;

static job_t J[MAXTH];
static pthread_t th[MAXTH];
static int pool_n;                                   /* workers started */
static volatile unsigned gen;                        /* region generation */
static volatile int pending;                         /* workers still busy in the current region */
static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t cv = PTHREAD_COND_INITIALIZER;

/* chunk count of a loop of nel elements: 0 (serial) below PAR_MIN, else the largest power of two <= nel / CHUNK_MIN,
 * at most NCHUNK; it depends only on nel */
size_t par_chunks(size_t nel) {
    if (nel < PAR_MIN) return 0;
    size_t c = nel / CHUNK_MIN, p = 1;
    while (p * 2 <= c && p < NCHUNK) p *= 2;
    return p;
}

static void run_chunks(job_t *Jb) {
    int lg = __builtin_ctzll(Jb->nch);
    size_t q = Jb->n >> lg, rem = Jb->n & (Jb->nch - 1);
    for (size_t c = Jb->c0; c < Jb->c1; c++) {
        size_t lo = c * q + (c < rem ? c : rem);      /* dispatch arithmetic: inside the TH_CHUNK charge */
        size_t hi = lo + q + (c < rem ? 1 : 0);
        if (hi > lo) Jb->fn(Jb->arg, lo, hi);
    }
}

static void *worker(void *p) {
    int id = (int)(intptr_t)p;
    unsigned g = 0;
    for (;;) {
        int s = 0;
        while (__atomic_load_n(&gen, __ATOMIC_ACQUIRE) == g) {
            if (++s < SPIN) { _mm_pause(); continue; }
            pthread_mutex_lock(&mu);
            while (__atomic_load_n(&gen, __ATOMIC_ACQUIRE) == g) pthread_cond_wait(&cv, &mu);
            pthread_mutex_unlock(&mu);
        }
        g = __atomic_load_n(&gen, __ATOMIC_ACQUIRE);
        memset(&X, 0, sizeof X);
        run_chunks(&J[id]);
        J[id].out = X;
        __atomic_fetch_sub(&pending, 1, __ATOMIC_ACQ_REL);
    }
    return NULL;
}

static void pool_start(int T) {
    pthread_attr_t at;
    pthread_attr_init(&at);
    pthread_attr_setstacksize(&at, THREAD_STACK);
    for (int t = pool_n + 1; t < T; t++)
        if (pthread_create(&th[t], &at, worker, (void *)(intptr_t)t)) { fprintf(stderr, "pthread_create failed\n"); exit(9); }
    pthread_attr_destroy(&at);
    pool_n = T - 1;
}

void par_range(size_t n, size_t nch, void (*fn)(void *, size_t, size_t), void *arg) {
    if (nch == 0 || n == 0) { fn(arg, 0, n); return; }
    if (nch & (nch - 1)) { fprintf(stderr, "par_range: chunk count must be a power of two\n"); exit(9); }
    int T = g_threads < (int)nch ? g_threads : (int)nch;     /* active threads: min(threads, chunks) */
    g_regions++; g_active_sum += (uint64_t)T; g_chunk_sum += nch;
    X.thr += (uint64_t)T * (TH_START + TH_JOIN) + (uint64_t)nch * TH_CHUNK;
    for (int t = 0; t < T; t++) {
        J[t].fn = fn; J[t].arg = arg; J[t].n = n; J[t].nch = nch;
        J[t].c0 = nch * (size_t)t / (size_t)T; J[t].c1 = nch * (size_t)(t + 1) / (size_t)T;
    }
    if (T > 1) {
        if (pool_n < T - 1) pool_start(T);
        for (int t = T; t <= pool_n; t++) { J[t].c0 = J[t].c1 = 0; }   /* idle workers of this region */
        __atomic_store_n(&pending, pool_n, __ATOMIC_RELEASE);
        pthread_mutex_lock(&mu);
        __atomic_add_fetch(&gen, 1, __ATOMIC_ACQ_REL);
        pthread_cond_broadcast(&cv);
        pthread_mutex_unlock(&mu);
    }
    run_chunks(&J[0]);
    if (T > 1) {
        int s = 0;
        while (__atomic_load_n(&pending, __ATOMIC_ACQUIRE) > 0) { if (++s < SPIN) _mm_pause(); else sched_yield(); }
        for (int t = 1; t <= pool_n; t++) X = cnt_add(X, J[t].out);
    }
}
```

### ntt.c

```c
/* Transform engine over F_p: length-2^n DIF (natural -> bit-reversed) and DIT (bit-reversed -> natural,
 * unnormalised), run as passes of at most 4 layers on blocks of at most 16 words (kern.h); the sparse twiddle
 * table holds w_T^(16k), k <= T/32, for the largest length T = 2^ntab (shorter transforms read it with a stride);
 * a pass whose twiddle step is below 16 (the first pass of a transform of length >= T/8) computes its twiddles
 * from the table, the 16-entry tables LOW / LOWI and the chain constants (gen_kern.py, variant "c"); the two-level
 * tables are for the state length L = 2^nmax (ntab = nmax).
 * Also: two-level tables for the twist zeta^j, the untwist zeta^-j / L, the values of x at the even / odd
 * points in bit-reversed order, and the stage-B points; and the pointwise loops.  Everything is charged. */
#include "orch.h"
typedef struct { const fp *gi, *go, *xl, *xh; fp *o; } fz_t;   /* operands of the fused pointwise operations */
#define FUSED_KERNELS
/* pointwise operations inside the fused passes (registers: x[t], the twiddle register w, the temporary t_) */
#define FL_SQ(t)  do { fp t_ = C->gi[i0 + (t)]; LD(1); fp_sqr(&x[t], &x[t]); fp_mul(&x[t], &x[t], &t_); } while (0)
#define FL_SQX(t) do { fp t_ = C->gi[i0 + (t)]; LD(1); fp_sqr(&x[t], &x[t]); fp_mul(&x[t], &x[t], &t_);                \
                       t_ = C->xl[il0 + (t)]; LD(1); fp_mul(&x[t], &x[t], &t_); t_ = C->xh[ih]; LD(1); fp_mul(&x[t], &x[t], &t_); } while (0)
#define FL_OU(t)  do { w = C->o[i0 + (t)]; LD(1); fp_sqr(&w, &w); fp t_ = C->go[i0 + (t)]; LD(1); fp_mul(&t_, &t_, &x[t]);    \
                       fp_add(&w, &w, &t_); C->o[i0 + (t)] = w; ST(1); x[t] = w; } while (0)
#define FL_OUX(t) do { w = C->o[i0 + (t)]; LD(1); fp_sqr(&w, &w); fp t_ = C->xl[il0 + (t)]; LD(1); fp_mul(&w, &w, &t_);      \
                       t_ = C->xh[ih]; LD(1); fp_mul(&w, &w, &t_); t_ = C->go[i0 + (t)]; LD(1); fp_mul(&t_, &t_, &x[t]);       \
                       fp_add(&w, &w, &t_); C->o[i0 + (t)] = w; ST(1); x[t] = w; } while (0)
#define FL_MG(t)  do { fp t_ = C->gi[i0 + (t)]; LD(1); fp_mul(&x[t], &x[t], &t_); } while (0)
#define FL_FM(t)  do { w = C->o[i0 + (t)]; LD(1); fp t_ = C->go[i0 + (t)]; LD(1); fp_mul(&t_, &t_, &x[t]);                   \
                       fp_add(&w, &w, &t_); C->o[i0 + (t)] = w; ST(1); x[t] = w; } while (0)
#include "kern.h"
#include <stdio.h>
#include <stdlib.h>

int ntt_nmax, ntt_ntab;
static fp *TW;                       /* w_T^(16k), k = 0 .. T/32 (TW[T/32] = -1) */
static fp *LOWT, *LOWIT, *CHT;       /* LOW[l] = w_T^l, LOWI[16 i + l] = w_T^(-2^i l) (l < 16, i < 4); chain constants */
static fp ZETA, WL;                  /* zeta = w_{2L}, w_L */
static int LO;                       /* low bits of the two-level split */
static fp *TL, *TH, *UL_, *UH_, *XL, *XH, *XHo, *PL, *PH, *PLi, *PHi;
static fp IP2[64];                   /* 2^-n */
void ntt_invL(fp *r, int n) { *r = IP2[n]; LD(1); }

void ntt_root(fp *r, int n) {
    if (n == 0) { fp_one(r); return; }
    if (n == 1) { fp_one(r); fp_neg(r, r); return; }
    if (n <= ntt_ntab - 4) { *r = TW[(size_t)1 << (ntt_ntab - 4 - n)]; return; }
    if (n <= ntt_ntab) { *r = LOWT[(size_t)1 << (ntt_ntab - n)]; return; }
    if (n == ntt_nmax + 1) { *r = ZETA; return; }
    fprintf(stderr, "ntt_root: n too large\n"); exit(8);
}

/* bit reverse of i over 'bits' bits: per bit a shift, a mask, an or, a shift and the loop (7) */
static size_t brev(size_t i, int bits) {
    size_t r = 0;
    for (int b = 0; b < bits; b++) { r = (r << 1) | ((i >> b) & 1); }
    CTL(7 * (uint64_t)bits + 2);
    return r;
}

/* powers base^0 .. base^(n-1) into d (sequential products) */
static void powers(fp *d, const fp *base, size_t n) {
    fp one; fp_one(&one);
    d[0] = one; ST(1);
    for (size_t i = 1; i < n; i++) { fp_mul(&d[i], &d[i - 1], base); LD(1); ST(1); }
    LOOPC(n - 1);
}

typedef struct { fp *d; fp w; } tab_t;
static void tw_chunk(void *a, size_t lo, size_t hi) {
    tab_t *T = a;
    fp v; uint64_t e[4] = { lo, 0, 0, 0 };
    fp_pow(&v, &T->w, e);                         /* chunk start w^lo */
    for (size_t i = lo; i < hi; i++) { T->d[i] = v; ST(1); fp_mul(&v, &v, &T->w); }
    LOOPC(hi - lo);
}

void ntt_init(int nmax, int ntab) {
    ntt_nmax = nmax; ntt_ntab = ntab < nmax ? nmax : ntab;
    size_t L = (size_t)1 << nmax;
    fp_root_of_unity(&WL, nmax);
    fp_root_of_unity(&ZETA, nmax + 1);
    if (ntt_ntab < 8) { fprintf(stderr, "ntt_init: ntab too small\n"); exit(8); }
    size_t nt = ((size_t)1 << ntt_ntab) / 32 + 1;
    TW = NEWFP(nt);
    { tab_t T = { TW, { { 0 } } }; fp_root_of_unity(&T.w, ntt_ntab - 4); par_range(nt, par_chunks(nt), tw_chunk, &T); }
    LOWT = NEWFP(16); LOWIT = NEWFP(64); CHT = NEWFP(5);
    {
        fp wT, wTi, bi;
        fp_root_of_unity(&wT, ntt_ntab);
        powers(LOWT, &wT, 16);
        fp_inv(&wTi, &wT);
        bi = wTi;
        for (int i = 0; i < 4; i++) { powers(LOWIT + 16 * i, &bi, 16); fp_sqr(&bi, &bi); CTL(3); }
        CTL(2);
        fp_root_of_unity(&CHT[0], 4);                               /* w_16 */
        fp_root_of_unity(&CHT[1], 3); fp_inv(&CHT[1], &CHT[1]);     /* w_8^-1 */
        fp_root_of_unity(&CHT[2], 2);                               /* w_4 */
        fp_inv(&CHT[3], &CHT[2]);                                   /* w_4^-1 */
        fp_inv(&CHT[4], &CHT[0]);                                   /* w_16^-1 */
        ST(5);
    }
    LO = nmax / 2;
    size_t nl = (size_t)1 << LO, nh = (size_t)1 << (nmax - LO);
    TL = NEWFP(nl); TH = NEWFP(nh); UL_ = NEWFP(nl); UH_ = NEWFP(nh);
    XL = NEWFP(nl); XH = NEWFP(nh); XHo = NEWFP(nh);
    PL = NEWFP(nl); PH = NEWFP(nh); PLi = NEWFP(nl); PHi = NEWFP(nh);
    fp zi, b, t, Linv, half, two;
    fp_inv(&zi, &ZETA);
    { fp Lf; fp_from_u64(&Lf, L); fp_inv(&Linv, &Lf); }
    fp_from_u64(&two, 2); fp_inv(&half, &two);
    fp_one(&IP2[0]); ST(1);
    for (int i = 1; i <= ntt_ntab + 1; i++) { fp_mul(&IP2[i], &IP2[i - 1], &half); LD(1); ST(1); }
    LOOPC(ntt_ntab + 1);
    /* twist: zeta^j = TH[j >> LO] * TL[j & mask];  untwist: zeta^-j / L = UH_[..] * UL_[..] */
    powers(TL, &ZETA, nl);
    b = ZETA; for (int i = 0; i < LO; i++) { fp_sqr(&b, &b); CTL(3); } CTL(2);
    powers(TH, &b, nh);
    powers(UL_, &zi, nl);
    b = zi; for (int i = 0; i < LO; i++) { fp_sqr(&b, &b); CTL(3); } CTL(2);
    powers(UH_, &b, nh);
    for (size_t i = 0; i < nh; i++) { fp_mul(&UH_[i], &UH_[i], &Linv); LD(1); ST(1); }
    LOOPC(nh);
    /* values of x in bit-reversed order: at the even points w_L^brev(i), i = ih * 2^LO + il:
     * brev(i) = brev_LO(il) 2^(nmax-LO) + brev_(nmax-LO)(ih)  ->  XL[il] * XH[ih];  odd points: * zeta */
    fp *tmp = NEWFP(nl > nh ? nl : nh);
    b = WL; for (int i = 0; i < nmax - LO; i++) { fp_sqr(&b, &b); CTL(3); } CTL(2);   /* w_L^(2^(nmax-LO)) */
    powers(tmp, &b, nl);
    for (size_t i = 0; i < nl; i++) { XL[i] = tmp[brev(i, LO)]; LD(1); ST(1); }
    LOOPC(nl);
    powers(tmp, &WL, nh);
    for (size_t i = 0; i < nh; i++) { XH[i] = tmp[brev(i, nmax - LO)]; LD(1); ST(1); fp_mul(&XHo[i], &XH[i], &ZETA); ST(1); }
    LOOPC(nh);
    /* stage-B points zeta^brev(pos) and 1/(2 zeta^brev(pos)) */
    b = ZETA; for (int i = 0; i < nmax - LO; i++) { fp_sqr(&b, &b); CTL(3); } CTL(2);
    powers(tmp, &b, nl);
    for (size_t i = 0; i < nl; i++) { PL[i] = tmp[brev(i, LO)]; LD(1); ST(1); }
    LOOPC(nl);
    fp_inv(&t, &b); powers(tmp, &t, nl);
    for (size_t i = 0; i < nl; i++) { PLi[i] = tmp[brev(i, LO)]; LD(1); ST(1); }
    LOOPC(nl);
    powers(tmp, &ZETA, nh);
    for (size_t i = 0; i < nh; i++) { PH[i] = tmp[brev(i, nmax - LO)]; LD(1); ST(1); }
    LOOPC(nh);
    powers(tmp, &zi, nh);
    for (size_t i = 0; i < nh; i++) { fp_mul(&PHi[i], &tmp[brev(i, nmax - LO)], &half); LD(1); ST(1); }
    LOOPC(nh);
    xfree(tmp);
}

/* ------------------------------------------------------------------ passes */
typedef struct { fp *x; int n, l0, k; kc_t K; } pass_t;

#define PASS_FN(NAME, KG, KZ)                                                                       \
static void NAME(void *a, size_t b_lo, size_t b_hi) {                                               \
    pass_t *P = a; const kc_t *K = &P->K;                                                           \
    int logs = P->n - P->l0 - P->k; size_t s = (size_t)1 << logs, sm = s - 1;                       \
    size_t g0 = b_lo >> logs, g1 = (b_hi - 1) >> logs; CTL(6);                                      \
    for (size_t g = g0; g <= g1; g++) {                                                             \
        fp *base = P->x + (g << (P->n - P->l0));                                                    \
        size_t jl = g == g0 ? (b_lo & sm) : 0, jh = g == g1 ? ((b_hi - 1) & sm) + 1 : s;           \
        CTL(3 + 2 + 8);                     /* loop; base (shift, add); bounds (2 tests, 2 masks/adds, selects) */ \
        size_t j = jl;                                                                              \
        CTL(2);                                                                                     \
        if (j == 0) { KZ(base, s, 0, K); j = 1; CTL(1); }                                          \
        for (; j < jh; j++) { KG(base + j, s, j, K); CTL(3 + 1); }    /* loop; block address */   \
        CTL(2);                                                                                     \
    }                                                                                               \
    CTL(2);                                                                                         \
}
PASS_FN(pf1, dif1g, dif1z) PASS_FN(pf2, dif2g, dif2z) PASS_FN(pf3, dif3g, dif3z) PASS_FN(pf4, dif4g, dif4z)
PASS_FN(pi1, dit1g, dit1z) PASS_FN(pi2, dit2g, dit2z) PASS_FN(pi3, dit3g, dit3z) PASS_FN(pi4, dit4g, dit4z)
PASS_FN(pf4c, dif4c, dif4z) PASS_FN(pi4c, dit4c, dit4z)      /* chained twiddles: first pass, sh < 4 */
static void (*const PF[5])(void *, size_t, size_t) = { 0, pf1, pf2, pf3, pf4 };
static void (*const PI[5])(void *, size_t, size_t) = { 0, pi1, pi2, pi3, pi4 };
/* a pass needs the chained kernel when its twiddle step 2^(l0 + sh) is below the table step 16 */
static int chained_pass(int n, int l0) { return l0 + (ntt_ntab - n) < 4; }

/* pass layer counts: 4, 4, ..., 4, then the remainder (n mod 4) */
static int plan(int n, int ks[8]) {
    int np = 0, left = n;
    while (left >= 4) { ks[np++] = 4; left -= 4; CTL(3 + 2); }
    if (left) ks[np++] = left;
    CTL(2 + 2);
    return np;
}

static void fill_kc(kc_t *K, int n, int l0, int k) {
    int sh = ntt_ntab - n;
    size_t s = (size_t)1 << (n - l0 - k);
    K->tw = TW; K->low = LOWT; K->lowi = LOWIT; K->ch = CHT; K->sh = sh;
    K->hLT = (size_t)1 << (ntt_ntab - 5);
    for (int i = 0; i < k; i++) {
        K->csd[i] = l0 + i + sh - 4;
        K->D[i] = (s << (l0 + i + sh)) >> 4;
    }
    CTL(8 + 6 * (uint64_t)k);                     /* pass constants */
}

static void run_pass(fp *x, int n, int l0, int k, int inverse) {
    pass_t P;
    P.x = x; P.n = n; P.l0 = l0; P.k = k;
    fill_kc(&P.K, n, l0, k);
    void (*fn)(void *, size_t, size_t) = inverse ? PI[k] : PF[k];
    if (chained_pass(n, l0)) {
        if (k != 4) { fprintf(stderr, "run_pass: chained pass needs k = 4\n"); exit(8); }
        fn = inverse ? pi4c : pf4c;
    }
    CTL(4);                                       /* selection of the pass function (test, table, call) */
    size_t NB = (size_t)1 << (n - k);
    size_t nch = par_chunks((size_t)1 << n);
    if (nch > NB) nch = NB;
    CTL(4);
    par_range(NB, nch, fn, &P);
}

/* passes [p0, p1) of the plan: forward in order, inverse in reverse order */
int ntt_npass(int n) { int ks[8]; return plan(n, ks); }
void ntt_dif_range(fp *x, int n, int p0, int p1) {
    int ks[8], np = plan(n, ks), l0 = 0;
    (void)np;
    for (int p = 0; p < p0; p++) { l0 += ks[p]; CTL(3 + 1); }
    for (int p = p0; p < p1; p++) { run_pass(x, n, l0, ks[p], 0); l0 += ks[p]; CTL(3 + 1); }
    CTL(4);
}
void ntt_dit_range(fp *x, int n, int p0, int p1) {
    int ks[8], np = plan(n, ks), l0 = n;
    for (int p = np - 1; p >= p1; p--) { l0 -= ks[p]; CTL(3 + 1); }
    for (int p = p1 - 1; p >= p0; p--) { l0 -= ks[p]; run_pass(x, n, l0, ks[p], 1); CTL(3 + 1); }
    CTL(4);
}

/* ---- fused passes of the Montgomery step (n = nmax) */
typedef struct { fp *x; int k; kc_t K; fz_t C; } fl_t;
#define FL_FN(K_, OP)                                                                               \
static void flc_##K_##_##OP(void *a, size_t g0, size_t g1) {                                        \
    fl_t *F = a; const fz_t *C = &F->C; size_t mask = ((size_t)1 << LO) - 1;                        \
    for (size_t g = g0; g < g1; g++) {                                                              \
        size_t i0 = g << K_, il0 = i0 & mask, ih = i0 >> LO;                                        \
        CTL(3 + 4);                       /* loop; block start (shift), row offset (mask), row (shift), base */ \
        fl##K_##_##OP(F->x + i0, &F->K, C, i0, il0, ih);                                            \
    }                                                                                               \
    CTL(2);                                                                                         \
}
#define FL_FNS(K_) FL_FN(K_, sq) FL_FN(K_, sqx) FL_FN(K_, ou) FL_FN(K_, oux) FL_FN(K_, mg) FL_FN(K_, fm)
FL_FNS(1) FL_FNS(2) FL_FNS(3) FL_FNS(4)
static void (*const FLC[5][6])(void *, size_t, size_t) = { { 0 },
    { flc_1_sq, flc_1_sqx, flc_1_ou, flc_1_oux, flc_1_mg, flc_1_fm },
    { flc_2_sq, flc_2_sqx, flc_2_ou, flc_2_oux, flc_2_mg, flc_2_fm },
    { flc_3_sq, flc_3_sqx, flc_3_ou, flc_3_oux, flc_3_mg, flc_3_fm },
    { flc_4_sq, flc_4_sqx, flc_4_ou, flc_4_oux, flc_4_mg, flc_4_fm } };

/* last DIF pass + pointwise op + first DIT pass, on x (length L = 2^nmax), blocks of 2^k contiguous words */
void ntt_fused_last(fp *x, int op, const fp *gi, fp *o, const fp *go) {
    int n = ntt_nmax, ks[8], np = plan(n, ks), k = ks[np - 1];
    fl_t F; F.x = x; F.k = k;
    fill_kc(&F.K, n, n - k, k);
    F.C.gi = gi; F.C.go = go; F.C.o = o; F.C.xl = XL; F.C.xh = op == FZ_OUX ? XHo : XH;
    CTL(10);
    size_t NB = (size_t)1 << (n - k), nch = par_chunks((size_t)1 << n);
    if (nch > NB) nch = NB;
    par_range(NB, nch, FLC[k][op], &F);
}

typedef struct { fp *x; int k; size_t s, dh; kc_t K; const fp *tl, *th; } ff_t;
#define FF_FN(K_)                                                                                   \
static void ffc_##K_(void *a, size_t j0, size_t j1) {                                               \
    ff_t *F = a; size_t mask = ((size_t)1 << LO) - 1;                                               \
    size_t j = j0;                                                                                  \
    CTL(2);                                                                                         \
    if (j == 0) { ff##K_##z(F->x, F->s, 0, &F->K, F->tl, F->th, F->dh); j = 1; CTL(3); }            \
    for (; j < j1; j++) {                                                                           \
        CTL(3 + 4);                       /* loop; table pointers (mask, add, shift, add) */         \
        ff##K_##g(F->x + j, F->s, j, &F->K, F->tl + (j & mask), F->th + (j >> LO), F->dh);          \
    }                                                                                               \
    CTL(2);                                                                                         \
}
FF_FN(1) FF_FN(2) FF_FN(3) FF_FN(4)
#define ff4cz ff4z
#define ff4cg ff4c
FF_FN(4c)
static void (*const FFC[5])(void *, size_t, size_t) = { 0, ffc_1, ffc_2, ffc_3, ffc_4 };

/* last DIT pass + (un)twist + first DIF pass (length L = 2^nmax; the untwist includes 1/L) */
void ntt_fused_first(fp *x, int untwist) {
    int n = ntt_nmax, ks[8]; plan(n, ks);
    int k = ks[0];
    ff_t F; F.x = x; F.k = k; F.s = (size_t)1 << (n - k); F.dh = F.s >> LO;
    fill_kc(&F.K, n, 0, k);
    F.tl = untwist ? UL_ : TL; F.th = untwist ? UH_ : TH;
    CTL(10);
    if (F.s < ((size_t)1 << LO)) { fprintf(stderr, "ntt_fused_first: n too small\n"); exit(8); }
    void (*fn)(void *, size_t, size_t) = FFC[k];
    if (chained_pass(n, 0)) {
        if (k != 4) { fprintf(stderr, "ntt_fused_first: chained pass needs k = 4\n"); exit(8); }
        fn = ffc_4c;
    }
    size_t nch = par_chunks((size_t)1 << n);
    if (nch > F.s) nch = F.s;
    par_range(F.s, nch, fn, &F);
}

void ntt_dif(fp *x, int n) {
    CTL(2);
    if (n <= 0) return;
    if (n > ntt_ntab) { fprintf(stderr, "ntt_dif: n=%d > ntab=%d\n", n, ntt_ntab); exit(8); }
    int ks[8], np = plan(n, ks), l0 = 0;
    for (int p = 0; p < np; p++) { run_pass(x, n, l0, ks[p], 0); l0 += ks[p]; CTL(3 + 1); }
    CTL(2);
}

void ntt_dit(fp *x, int n) {
    CTL(2);
    if (n <= 0) return;
    if (n > ntt_ntab) { fprintf(stderr, "ntt_dit: n=%d > ntab=%d\n", n, ntt_ntab); exit(8); }
    int ks[8], np = plan(n, ks), l0 = n;
    for (int p = np - 1; p >= 0; p--) { l0 -= ks[p]; run_pass(x, n, l0, ks[p], 1); CTL(3 + 1); }
    CTL(2);
}

/* ------------------------------------------------------------------ two-level twist / untwist / x values */
typedef struct { fp *d; const fp *s; size_t len; fp sc; int has_sc; int odd; } tw_t;

/* rows ih of 2^LO elements; chunks are ranges of rows */
static void twist_chunk(void *a, size_t r0, size_t r1) {
    tw_t *T = a; size_t nl = (size_t)1 << LO;
    for (size_t ih = r0; ih < r1; ih++) {
        fp h = TH[ih]; LD(1);
        if (T->has_sc) fp_mul(&h, &h, &T->sc);
        size_t j0 = ih << LO, cnt = T->len - j0 < nl ? T->len - j0 : nl;
        fp *d = T->d + j0; const fp *s = T->s + j0;
        CTL(3 + 2 + 2 + 3 + 2);              /* loop; scale test; j0; min (sub, compare, select); pointers */
        FOR8(i, cnt, { fp w; fp_mul(&w, &h, &TL[i]); fp_mul(&d[i], &s[i], &w); LD(2); ST(1); });
    }
    CTL(2);
}
void tw_twist(fp *dst, const fp *src, size_t len, const fp *scale) {
    tw_t T = { dst, src, len, { { 0 } }, scale != NULL, 0 };
    if (scale) T.sc = *scale;
    size_t rows = (len + ((size_t)1 << LO) - 1) >> LO;
    CTL(6);
    par_range(rows, par_chunks(len) > rows ? 0 : par_chunks(len), twist_chunk, &T);
}

static void untwist_chunk(void *a, size_t r0, size_t r1) {
    tw_t *T = a; size_t nl = (size_t)1 << LO;
    for (size_t ih = r0; ih < r1; ih++) {
        fp h = UH_[ih]; LD(1);
        size_t j0 = ih << LO, cnt = T->len - j0 < nl ? T->len - j0 : nl;
        fp *d = T->d + j0;
        CTL(3 + 1 + 3 + 1);
        FOR8(i, cnt, { fp w; fp_mul(&w, &h, &UL_[i]); fp_mul(&d[i], &d[i], &w); LD(2); ST(1); });
    }
    CTL(2);
}
void tw_untwist(fp *x, size_t len) {
    tw_t T = { x, x, len, { { 0 } }, 0, 0 };
    size_t rows = (len + ((size_t)1 << LO) - 1) >> LO;
    CTL(5);
    par_range(rows, par_chunks(len) > rows ? 0 : par_chunks(len), untwist_chunk, &T);
}

static void xmul_chunk(void *a, size_t r0, size_t r1) {
    tw_t *T = a; size_t nl = (size_t)1 << LO;
    const fp *H = T->odd ? XHo : XH;
    for (size_t ih = r0; ih < r1; ih++) {
        fp h = H[ih]; LD(1);
        fp *d = T->d + (ih << LO);
        CTL(3 + 2);
        FOR8(i, nl, { fp w; fp_mul(&w, &h, &XL[i]); fp_mul(&d[i], &d[i], &w); LD(2); ST(1); });
    }
    CTL(2);
}
void tw_xmul(fp *x, int odd) {
    tw_t T = { x, x, 0, { { 0 } }, 0, odd };
    size_t rows = (size_t)1 << (ntt_nmax - LO), L = (size_t)1 << ntt_nmax;
    CTL(5);
    par_range(rows, par_chunks(L) > rows ? 0 : par_chunks(L), xmul_chunk, &T);
}

void tw_point(fp *s, fp *sinv2, size_t pos) {
    size_t il = pos & (((size_t)1 << LO) - 1), ih = pos >> LO;
    CTL(3);
    fp_mul(s, &PL[il], &PH[ih]);
    fp_mul(sinv2, &PLi[il], &PHi[ih]);
    LD(4);
}

/* ------------------------------------------------------------------ pointwise loops */
typedef struct { fp *d; const fp *a, *b; fp c; } pw_t;
#define PW_FN(NAME, ...)                                                                 \
static void NAME##_chunk(void *arg, size_t lo, size_t hi) {                              \
    pw_t *W = arg; fp *d = W->d + lo; const fp *a = W->a ? W->a + lo : NULL;             \
    const fp *b = W->b ? W->b + lo : NULL; (void)a; (void)b; CTL(4);                     \
    FOR8(i, hi - lo, __VA_ARGS__);                                                            \
}
PW_FN(copy, { d[i] = a[i]; LD(1); ST(1); })
PW_FN(zero, { fp_zero(&d[i]); ST(1); })
PW_FN(scale, { fp_mul(&d[i], &a[i], &W->c); LD(1); ST(1); })
PW_FN(mul, { fp_mul(&d[i], &a[i], &b[i]); LD(2); ST(1); })
PW_FN(sqr, { fp_sqr(&d[i], &d[i]); LD(1); ST(1); })
PW_FN(sqrmul, { fp t; fp_sqr(&t, &d[i]); fp_mul(&d[i], &t, &a[i]); LD(2); ST(1); })
PW_FN(sqrfma, { fp t, u; fp_sqr(&t, &d[i]); fp_mul(&u, &a[i], &b[i]); fp_add(&d[i], &t, &u); LD(3); ST(1); })
PW_FN(fma, { fp u; fp_mul(&u, &a[i], &b[i]); fp_add(&d[i], &d[i], &u); LD(3); ST(1); })
PW_FN(sum, { fp_add(&d[i], &a[i], &b[i]); LD(2); ST(1); })
PW_FN(add, { fp_add(&d[i], &d[i], &a[i]); LD(2); ST(1); })
PW_FN(addsc, { fp u; fp_mul(&u, &a[i], &W->c); fp_add(&d[i], &d[i], &u); LD(2); ST(1); })
PW_FN(sub, { fp_sub(&d[i], &d[i], &a[i]); LD(2); ST(1); })
PW_FN(rsub, { fp_sub(&d[i], &a[i], &d[i]); LD(2); ST(1); })
PW_FN(negc, { fp_neg(&d[i], &a[i]); LD(1); ST(1); })

#define PW_RUN(NAME, D, A, B, C, N) do { pw_t W_ = { (D), (A), (B), { { 0 } } };            \
    if ((C) != NULL) W_.c = *(const fp *)(C);                                                \
    CTL(4); par_range((N), par_chunks(N), NAME##_chunk, &W_); } while (0)

void pw_copy(fp *d, const fp *s, size_t n) { PW_RUN(copy, d, s, NULL, NULL, n); }
void pw_zero(fp *d, size_t n) { PW_RUN(zero, d, NULL, NULL, NULL, n); }
void pw_scale(fp *d, const fp *s, const fp *c, size_t n) { PW_RUN(scale, d, s, NULL, c, n); }
void pw_mul(fp *d, const fp *a, const fp *b, size_t n) { PW_RUN(mul, d, a, b, NULL, n); }
void pw_sqr(fp *d, size_t n) { PW_RUN(sqr, d, NULL, NULL, NULL, n); }
void pw_sqr_mul(fp *d, const fp *b, size_t n) { PW_RUN(sqrmul, d, b, NULL, NULL, n); }
void pw_sqr_fma(fp *d, const fp *b, const fp *c, size_t n) { PW_RUN(sqrfma, d, b, c, NULL, n); }
void pw_fma(fp *d, const fp *b, const fp *c, size_t n) { PW_RUN(fma, d, b, c, NULL, n); }
void pw_add(fp *d, const fp *a, size_t n) { PW_RUN(add, d, a, NULL, NULL, n); }
void pw_addscale(fp *d, const fp *a, const fp *c, size_t n) { PW_RUN(addsc, d, a, NULL, c, n); }
void pw_sub(fp *d, const fp *a, size_t n) { PW_RUN(sub, d, a, NULL, NULL, n); }
void pw_rsub(fp *d, const fp *a, size_t n) { PW_RUN(rsub, d, a, NULL, NULL, n); }
void pw_negcopy(fp *d, const fp *a, size_t n) { PW_RUN(negc, d, a, NULL, NULL, n); }
void pw_sum(fp *d, const fp *a, const fp *b, size_t n) { PW_RUN(sum, d, a, b, NULL, n); }
```

### gen_kern.py

```python
"""Generate kern.h: straight-line block kernels of the radix-2 transform passes (no loop, no branch inside).

A block is 2^k words (k = 1..4) at stride s, held in the register file x[0..15] (+ the twiddle operand w and the
butterfly temporary t_: 18 words).  Forward (DIF) layer i of the pass (i = 0..k-1, half = 2^(k-1-i)) pairs x[q*2h + u]
with x[q*2h + u + h] using the twiddle number u (u < h) of the layer; inverse (DIT) runs the layers in the reverse
order with the inverse butterfly.  Variant "g": general block (j0 > 0); variant "z": block j0 = 0, where twiddle u = 0
is 1 (no load, 2-operation butterfly).

Twiddle table: w_T^(16 k) for k = 0 .. T/32 (the sparse table; T = 2^ntab the largest transform length), so a layer
with table step 2^(l0 + i + sh) >= 16 (l0 the first layer of the pass, sh = ntab - n) reads its twiddles directly.
Charges written in the generated text (direct kernels):
  LD(1)/ST(1) per word of the block; the first twiddle of a layer: its address (CTL(2) forward: shift, add;
  CTL(3) inverse: shift, subtract, add) and LD(1); every further twiddle: LD(1) (the load and its address
  operation, a running-pointer step).  Butterflies count their own field operations (3, or 2 without twiddle).
Chained kernels (variant "c": the first pass, l0 = 0, of a transform with sh < 4, k = 4, j0 > 0): the twiddles of
the block are (A c_u)^(2^i) with A = w_T^(j0 2^sh) and c_u = w_16^u, and they are computed:
  the block indices q = (j0 2^sh) div 16, l = (j0 2^sh) mod 16 (CTL(3): shift, shift, mask);
  forward: A = TW[q] * LOW[l] (LD(2), 1 multiplication); layer 0 ascending in u, each further twiddle one load of
  the chain constant (LD(1)) and one multiplication; then one squaring gives (up to sign) a twiddle of the next
  layer, the layers alternate direction, and a negative twiddle is used by the butterfly BFM (3 operations, like BF);
  inverse: the first twiddle of layer i is TW[T/32 - (q << i)] * LOWI[i][l] (CTL(2), LD(2), 1 multiplication), the
  further twiddles of the layer one chain load (LD(1)) and one multiplication each.
Usage: python3 gen_kern.py > kern.h
"""

# chain constants (index in K->ch): w_16, w_8^-1, w_4, w_4^-1, w_16^-1
CH16, CH8I, CH4, CH4I, CH16I = 0, 1, 2, 3, 4


def pairs(k, i, u, op):
    n = 1 << k
    h = 1 << (k - 1 - i)
    return ' '.join(f'{op}(x[{q * 2 * h + u}], x[{q * 2 * h + u + h}]);' for q in range(n // (2 * h)))


def layer_code(k, inverse, zero, i, L):
    """butterflies of layer i of a k-layer block with direct twiddle loads"""
    h = 1 << (k - 1 - i)
    for u in range(h):
        if zero and u == 0:
            op = 'IBN' if inverse else 'BFN'
        else:
            op = 'IB' if inverse else 'BF'
            first = (u == 1) if zero else (u == 0)
            if first:
                if inverse:
                    if zero:
                        L.append(f'    wp = K->tw + (K->hLT - K->D[{i}]); CTL(2); w = *wp; LD(1);')
                    else:
                        L.append(f'    wp = K->tw + (K->hLT - (j0 << K->csd[{i}])); CTL(3); w = *wp; LD(1);')
                else:
                    if zero:
                        L.append(f'    wp = K->tw + K->D[{i}]; CTL(1); w = *wp; LD(1);')
                    else:
                        L.append(f'    wp = K->tw + (j0 << K->csd[{i}]); CTL(2); w = *wp; LD(1);')
            else:
                L.append(f'    wp {"-" if inverse else "+"}= K->D[{i}]; w = *wp; LD(1);')
        L.append('    ' + pairs(k, i, u, op))


def chain(c):
    return f'    t_ = K->ch[{c}]; LD(1); fp_mul(&w, &w, &t_);'


def chained_dif_layers(L):
    """k = 4, forward: A = TW[q] LOW[l]; layer 0 ascending (chain w_16), square (-> -A^2 w_8^3), layer 1 descending
    (chain w_8^-1, negative twiddles), square (-> A^4), layer 2 ascending (chain w_4), square (-> -A^8), layer 3."""
    L.append('    w = K->tw[q]; LD(1); t_ = K->low[l]; LD(1); fp_mul(&w, &w, &t_);')
    for u in range(8):
        if u:
            L.append(chain(CH16))
        L.append('    ' + pairs(4, 0, u, 'BF'))
    L.append('    fp_sqr(&w, &w);')
    for u in (3, 2, 1, 0):
        if u != 3:
            L.append(chain(CH8I))
        L.append('    ' + pairs(4, 1, u, 'BFM'))
    L.append('    fp_sqr(&w, &w);')
    for u in (0, 1):
        if u:
            L.append(chain(CH4))
        L.append('    ' + pairs(4, 2, u, 'BF'))
    L.append('    fp_sqr(&w, &w);')
    L.append('    ' + pairs(4, 3, 0, 'BFM'))


def chained_dit_layers(L):
    """k = 4, inverse: layers 3, 2, 1, 0; the first twiddle of layer i is TW[T/32 - (q << i)] * LOWI[i][l], the
    further ones chained (w_4^-1, w_8^-1, w_16^-1)."""
    consts = {2: CH4I, 1: CH8I, 0: CH16I}
    for i in (3, 2, 1, 0):
        L.append(f'    wp = K->tw + (K->hLT - (q << {i})); CTL(2); w = *wp; LD(1); t_ = K->lowi[{16 * i} + l]; LD(1); fp_mul(&w, &w, &t_);')
        h = 1 << (3 - i)
        for u in range(h):
            if u:
                L.append(chain(consts[i]))
            L.append('    ' + pairs(4, i, u, 'IB'))


def loads(n, stride=True):
    return '    ' + ' '.join(f'x[{t}] = b[{t} * s];' if stride else f'x[{t}] = b[{t}];' for t in range(n)) + f' LD({n});'


def stores(n, stride=True):
    return '    ' + ' '.join(f'b[{t} * s] = x[{t}];' if stride else f'b[{t}] = x[{t}];' for t in range(n)) + f' ST({n});'


def kernel(k, inverse, zero):
    n = 1 << k
    name = ('dit' if inverse else 'dif') + f'{k}' + ('z' if zero else 'g')
    L = [f'static inline void {name}(fp *b, size_t s, size_t j0, const kc_t *K) {{',
         '    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;', loads(n)]
    layers = list(range(k))
    if inverse:
        layers = layers[::-1]
    for i in layers:
        layer_code(k, inverse, zero, i, L)
    L.append(stores(n))
    L.append('}')
    return '\n'.join(L)


def kernel_chained(inverse):
    name = 'dit4c' if inverse else 'dif4c'
    L = [f'static inline void {name}(fp *b, size_t s, size_t j0, const kc_t *K) {{',
         '    fp x[16], w, t_; const fp *wp; (void)wp;', loads(16),
         '    size_t jsh = j0 << K->sh, q = jsh >> 4, l = jsh & 15; CTL(3);']
    if inverse:
        chained_dit_layers(L)
    else:
        chained_dif_layers(L)
    L.append(stores(16))
    L.append('}')
    return '\n'.join(L)


def fused_last(k, op):
    """s = 1 block (j0 = 0): DIF layers of the last pass, the pointwise operation FL_<op>(t) per word, the DIT layers
    of the same pass (the first pass of the inverse transform)."""
    n = 1 << k
    L = [f'static inline void fl{k}_{op}(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {{',
         '    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;',
         loads(n, False)]
    for i in range(k):
        layer_code(k, False, True, i, L)
    L.append('    ' + ' '.join(f'FL_{op.upper()}({t});' for t in range(n)))
    for i in reversed(range(k)):
        layer_code(k, True, True, i, L)
    L.append(stores(n, False))
    L.append('}')
    return '\n'.join(L)


def twist_code(n):
    return ['    w = *tlv; LD(1);',
            '    ' + ' '.join(f'{{ fp t_ = thp[{t} * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[{t}], &x[{t}], &t_); LD(1); }}' for t in range(n))]


def fused_first(k, zero):
    """first-pass block (stride s): DIT layers (last pass of the inverse), multiplication of word t by
    tl * th[t * dh] (the two-level twist or untwist factor of position j0 + t s), DIF layers (first pass)."""
    n = 1 << k
    name = f'ff{k}{"z" if zero else "g"}'
    L = [f'static inline void {name}(fp *b, size_t s, size_t j0, const kc_t *K, const fp *tlv, const fp *thp, size_t dh) {{',
         '    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;', loads(n)]
    for i in reversed(range(k)):
        layer_code(k, True, zero, i, L)
    L += twist_code(n)
    for i in range(k):
        layer_code(k, False, zero, i, L)
    L.append(stores(n))
    L.append('}')
    return '\n'.join(L)


def fused_first_chained():
    L = ['static inline void ff4c(fp *b, size_t s, size_t j0, const kc_t *K, const fp *tlv, const fp *thp, size_t dh) {',
         '    fp x[16], w, t_; const fp *wp; (void)wp;', loads(16),
         '    size_t jsh = j0 << K->sh, q = jsh >> 4, l = jsh & 15; CTL(3);']
    chained_dit_layers(L)
    L += twist_code(16)
    chained_dif_layers(L)
    L.append(stores(16))
    L.append('}')
    return '\n'.join(L)


def main():
    out = ['/* Generated by gen_kern.py: straight-line block kernels (see the generator header for the charges). */',
           '#ifndef KERN_H', '#define KERN_H',
           '/* pass constants (integer registers): tw the sparse twiddle table (w_T^(16k)), sh = ntab - n, csd[i] = l0+i+sh-4',
           ' * (direct kernels), D[i] = s << (l0+i+sh) >> 4 (twiddle stride of layer i in table units), hLT = T/32;',
           ' * chained kernels: low = w_T^l (l < 16), lowi[16 i + l] = w_T^(-2^i l), ch = chain constants */',
           'typedef struct { const fp *tw, *low, *lowi, *ch; int sh; int csd[4]; size_t D[4]; size_t hLT; } kc_t;',
           '#define BF(u, v)  do { fp t_; fp_sub(&t_, &(u), &(v)); fp_add(&(u), &(u), &(v)); fp_mul(&(v), &t_, &w); } while (0)',
           '#define BFM(u, v) do { fp t_; fp_sub(&t_, &(v), &(u)); fp_add(&(u), &(u), &(v)); fp_mul(&(v), &t_, &w); } while (0)',
           '#define BFN(u, v) do { fp t_; fp_sub(&t_, &(u), &(v)); fp_add(&(u), &(u), &(v)); (v) = t_; } while (0)',
           '#define IB(u, v)  do { fp t_; fp_mul(&t_, &(v), &w); fp_add(&(v), &(u), &t_); fp_sub(&(u), &(u), &t_); } while (0)',
           '#define IBN(u, v) do { fp t_ = (v); fp_sub(&(v), &(u), &t_); fp_add(&(u), &(u), &t_); } while (0)']
    for k in range(1, 5):
        for inv in (False, True):
            for z in (False, True):
                out.append(kernel(k, inv, z))
    out.append(kernel_chained(False))
    out.append(kernel_chained(True))
    out.append('#ifdef FUSED_KERNELS')
    for k in range(1, 5):
        for op in ('sq', 'sqx', 'ou', 'oux', 'mg', 'fm'):
            out.append(fused_last(k, op))
        for z in (False, True):
            out.append(fused_first(k, z))
    out.append(fused_first_chained())
    out.append('#endif')
    out.append('#endif')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
```

### kern.h

```c
/* Generated by gen_kern.py: straight-line block kernels (see the generator header for the charges). */
#ifndef KERN_H
#define KERN_H
/* pass constants (integer registers): tw the sparse twiddle table (w_T^(16k)), sh = ntab - n, csd[i] = l0+i+sh-4
 * (direct kernels), D[i] = s << (l0+i+sh) >> 4 (twiddle stride of layer i in table units), hLT = T/32;
 * chained kernels: low = w_T^l (l < 16), lowi[16 i + l] = w_T^(-2^i l), ch = chain constants */
typedef struct { const fp *tw, *low, *lowi, *ch; int sh; int csd[4]; size_t D[4]; size_t hLT; } kc_t;
#define BF(u, v)  do { fp t_; fp_sub(&t_, &(u), &(v)); fp_add(&(u), &(u), &(v)); fp_mul(&(v), &t_, &w); } while (0)
#define BFM(u, v) do { fp t_; fp_sub(&t_, &(v), &(u)); fp_add(&(u), &(u), &(v)); fp_mul(&(v), &t_, &w); } while (0)
#define BFN(u, v) do { fp t_; fp_sub(&t_, &(u), &(v)); fp_add(&(u), &(u), &(v)); (v) = t_; } while (0)
#define IB(u, v)  do { fp t_; fp_mul(&t_, &(v), &w); fp_add(&(v), &(u), &t_); fp_sub(&(u), &(u), &t_); } while (0)
#define IBN(u, v) do { fp t_ = (v); fp_sub(&(v), &(u), &t_); fp_add(&(u), &(u), &t_); } while (0)
static inline void dif1g(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; LD(2);
    wp = K->tw + (j0 << K->csd[0]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[1]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; ST(2);
}
static inline void dif1z(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; LD(2);
    BFN(x[0], x[1]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; ST(2);
}
static inline void dit1g(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; LD(2);
    wp = K->tw + (K->hLT - (j0 << K->csd[0])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[1]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; ST(2);
}
static inline void dit1z(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; LD(2);
    IBN(x[0], x[1]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; ST(2);
}
static inline void dif2g(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; LD(4);
    wp = K->tw + (j0 << K->csd[0]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[2]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[1], x[3]);
    wp = K->tw + (j0 << K->csd[1]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[1]); BF(x[2], x[3]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; ST(4);
}
static inline void dif2z(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; LD(4);
    BFN(x[0], x[2]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]);
    BFN(x[0], x[1]); BFN(x[2], x[3]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; ST(4);
}
static inline void dit2g(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; LD(4);
    wp = K->tw + (K->hLT - (j0 << K->csd[1])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[1]); IB(x[2], x[3]);
    wp = K->tw + (K->hLT - (j0 << K->csd[0])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[2]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[1], x[3]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; ST(4);
}
static inline void dit2z(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; LD(4);
    IBN(x[0], x[1]); IBN(x[2], x[3]);
    IBN(x[0], x[2]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; ST(4);
}
static inline void dif3g(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; LD(8);
    wp = K->tw + (j0 << K->csd[0]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[4]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[1], x[5]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[6]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[7]);
    wp = K->tw + (j0 << K->csd[1]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[2]); BF(x[4], x[6]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]);
    wp = K->tw + (j0 << K->csd[2]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[1]); BF(x[2], x[3]); BF(x[4], x[5]); BF(x[6], x[7]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; ST(8);
}
static inline void dif3z(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; LD(8);
    BFN(x[0], x[4]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[6]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[7]);
    BFN(x[0], x[2]); BFN(x[4], x[6]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; ST(8);
}
static inline void dit3g(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; LD(8);
    wp = K->tw + (K->hLT - (j0 << K->csd[2])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[1]); IB(x[2], x[3]); IB(x[4], x[5]); IB(x[6], x[7]);
    wp = K->tw + (K->hLT - (j0 << K->csd[1])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[2]); IB(x[4], x[6]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]);
    wp = K->tw + (K->hLT - (j0 << K->csd[0])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[4]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[1], x[5]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[6]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[7]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; ST(8);
}
static inline void dit3z(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; LD(8);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]);
    IBN(x[0], x[2]); IBN(x[4], x[6]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]);
    IBN(x[0], x[4]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[6]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[7]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; ST(8);
}
static inline void dif4g(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; x[8] = b[8 * s]; x[9] = b[9 * s]; x[10] = b[10 * s]; x[11] = b[11 * s]; x[12] = b[12 * s]; x[13] = b[13 * s]; x[14] = b[14 * s]; x[15] = b[15 * s]; LD(16);
    wp = K->tw + (j0 << K->csd[0]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[8]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[1], x[9]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[10]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[11]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[4], x[12]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[5], x[13]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[6], x[14]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[7], x[15]);
    wp = K->tw + (j0 << K->csd[1]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[4]); BF(x[8], x[12]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[1], x[5]); BF(x[9], x[13]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[2], x[6]); BF(x[10], x[14]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[3], x[7]); BF(x[11], x[15]);
    wp = K->tw + (j0 << K->csd[2]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[2]); BF(x[4], x[6]); BF(x[8], x[10]); BF(x[12], x[14]);
    wp += K->D[2]; w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]); BF(x[9], x[11]); BF(x[13], x[15]);
    wp = K->tw + (j0 << K->csd[3]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[1]); BF(x[2], x[3]); BF(x[4], x[5]); BF(x[6], x[7]); BF(x[8], x[9]); BF(x[10], x[11]); BF(x[12], x[13]); BF(x[14], x[15]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; b[8 * s] = x[8]; b[9 * s] = x[9]; b[10 * s] = x[10]; b[11 * s] = x[11]; b[12 * s] = x[12]; b[13 * s] = x[13]; b[14 * s] = x[14]; b[15 * s] = x[15]; ST(16);
}
static inline void dif4z(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; x[8] = b[8 * s]; x[9] = b[9 * s]; x[10] = b[10 * s]; x[11] = b[11 * s]; x[12] = b[12 * s]; x[13] = b[13 * s]; x[14] = b[14 * s]; x[15] = b[15 * s]; LD(16);
    BFN(x[0], x[8]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[9]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[10]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[11]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[4], x[12]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[5], x[13]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[6], x[14]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[7], x[15]);
    BFN(x[0], x[4]); BFN(x[8], x[12]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]); BF(x[9], x[13]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[2], x[6]); BF(x[10], x[14]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[3], x[7]); BF(x[11], x[15]);
    BFN(x[0], x[2]); BFN(x[4], x[6]); BFN(x[8], x[10]); BFN(x[12], x[14]);
    wp = K->tw + K->D[2]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]); BF(x[9], x[11]); BF(x[13], x[15]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]); BFN(x[8], x[9]); BFN(x[10], x[11]); BFN(x[12], x[13]); BFN(x[14], x[15]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; b[8 * s] = x[8]; b[9 * s] = x[9]; b[10 * s] = x[10]; b[11 * s] = x[11]; b[12 * s] = x[12]; b[13 * s] = x[13]; b[14 * s] = x[14]; b[15 * s] = x[15]; ST(16);
}
static inline void dit4g(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; x[8] = b[8 * s]; x[9] = b[9 * s]; x[10] = b[10 * s]; x[11] = b[11 * s]; x[12] = b[12 * s]; x[13] = b[13 * s]; x[14] = b[14 * s]; x[15] = b[15 * s]; LD(16);
    wp = K->tw + (K->hLT - (j0 << K->csd[3])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[1]); IB(x[2], x[3]); IB(x[4], x[5]); IB(x[6], x[7]); IB(x[8], x[9]); IB(x[10], x[11]); IB(x[12], x[13]); IB(x[14], x[15]);
    wp = K->tw + (K->hLT - (j0 << K->csd[2])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[2]); IB(x[4], x[6]); IB(x[8], x[10]); IB(x[12], x[14]);
    wp -= K->D[2]; w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]); IB(x[9], x[11]); IB(x[13], x[15]);
    wp = K->tw + (K->hLT - (j0 << K->csd[1])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[4]); IB(x[8], x[12]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[1], x[5]); IB(x[9], x[13]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[2], x[6]); IB(x[10], x[14]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[3], x[7]); IB(x[11], x[15]);
    wp = K->tw + (K->hLT - (j0 << K->csd[0])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[8]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[1], x[9]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[10]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[11]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[4], x[12]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[5], x[13]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[6], x[14]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[7], x[15]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; b[8 * s] = x[8]; b[9 * s] = x[9]; b[10 * s] = x[10]; b[11 * s] = x[11]; b[12 * s] = x[12]; b[13 * s] = x[13]; b[14 * s] = x[14]; b[15 * s] = x[15]; ST(16);
}
static inline void dit4z(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; x[8] = b[8 * s]; x[9] = b[9 * s]; x[10] = b[10 * s]; x[11] = b[11 * s]; x[12] = b[12 * s]; x[13] = b[13 * s]; x[14] = b[14 * s]; x[15] = b[15 * s]; LD(16);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]); IBN(x[8], x[9]); IBN(x[10], x[11]); IBN(x[12], x[13]); IBN(x[14], x[15]);
    IBN(x[0], x[2]); IBN(x[4], x[6]); IBN(x[8], x[10]); IBN(x[12], x[14]);
    wp = K->tw + (K->hLT - K->D[2]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]); IB(x[9], x[11]); IB(x[13], x[15]);
    IBN(x[0], x[4]); IBN(x[8], x[12]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]); IB(x[9], x[13]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[2], x[6]); IB(x[10], x[14]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[3], x[7]); IB(x[11], x[15]);
    IBN(x[0], x[8]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[9]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[10]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[11]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[4], x[12]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[5], x[13]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[6], x[14]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[7], x[15]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; b[8 * s] = x[8]; b[9 * s] = x[9]; b[10 * s] = x[10]; b[11 * s] = x[11]; b[12 * s] = x[12]; b[13 * s] = x[13]; b[14 * s] = x[14]; b[15 * s] = x[15]; ST(16);
}
static inline void dif4c(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w, t_; const fp *wp; (void)wp;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; x[8] = b[8 * s]; x[9] = b[9 * s]; x[10] = b[10 * s]; x[11] = b[11 * s]; x[12] = b[12 * s]; x[13] = b[13 * s]; x[14] = b[14 * s]; x[15] = b[15 * s]; LD(16);
    size_t jsh = j0 << K->sh, q = jsh >> 4, l = jsh & 15; CTL(3);
    w = K->tw[q]; LD(1); t_ = K->low[l]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[0], x[8]);
    t_ = K->ch[0]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[1], x[9]);
    t_ = K->ch[0]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[2], x[10]);
    t_ = K->ch[0]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[3], x[11]);
    t_ = K->ch[0]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[4], x[12]);
    t_ = K->ch[0]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[5], x[13]);
    t_ = K->ch[0]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[6], x[14]);
    t_ = K->ch[0]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[7], x[15]);
    fp_sqr(&w, &w);
    BFM(x[3], x[7]); BFM(x[11], x[15]);
    t_ = K->ch[1]; LD(1); fp_mul(&w, &w, &t_);
    BFM(x[2], x[6]); BFM(x[10], x[14]);
    t_ = K->ch[1]; LD(1); fp_mul(&w, &w, &t_);
    BFM(x[1], x[5]); BFM(x[9], x[13]);
    t_ = K->ch[1]; LD(1); fp_mul(&w, &w, &t_);
    BFM(x[0], x[4]); BFM(x[8], x[12]);
    fp_sqr(&w, &w);
    BF(x[0], x[2]); BF(x[4], x[6]); BF(x[8], x[10]); BF(x[12], x[14]);
    t_ = K->ch[2]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[1], x[3]); BF(x[5], x[7]); BF(x[9], x[11]); BF(x[13], x[15]);
    fp_sqr(&w, &w);
    BFM(x[0], x[1]); BFM(x[2], x[3]); BFM(x[4], x[5]); BFM(x[6], x[7]); BFM(x[8], x[9]); BFM(x[10], x[11]); BFM(x[12], x[13]); BFM(x[14], x[15]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; b[8 * s] = x[8]; b[9 * s] = x[9]; b[10 * s] = x[10]; b[11 * s] = x[11]; b[12 * s] = x[12]; b[13 * s] = x[13]; b[14 * s] = x[14]; b[15 * s] = x[15]; ST(16);
}
static inline void dit4c(fp *b, size_t s, size_t j0, const kc_t *K) {
    fp x[16], w, t_; const fp *wp; (void)wp;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; x[8] = b[8 * s]; x[9] = b[9 * s]; x[10] = b[10 * s]; x[11] = b[11 * s]; x[12] = b[12 * s]; x[13] = b[13 * s]; x[14] = b[14 * s]; x[15] = b[15 * s]; LD(16);
    size_t jsh = j0 << K->sh, q = jsh >> 4, l = jsh & 15; CTL(3);
    wp = K->tw + (K->hLT - (q << 3)); CTL(2); w = *wp; LD(1); t_ = K->lowi[48 + l]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[0], x[1]); IB(x[2], x[3]); IB(x[4], x[5]); IB(x[6], x[7]); IB(x[8], x[9]); IB(x[10], x[11]); IB(x[12], x[13]); IB(x[14], x[15]);
    wp = K->tw + (K->hLT - (q << 2)); CTL(2); w = *wp; LD(1); t_ = K->lowi[32 + l]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[0], x[2]); IB(x[4], x[6]); IB(x[8], x[10]); IB(x[12], x[14]);
    t_ = K->ch[3]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[1], x[3]); IB(x[5], x[7]); IB(x[9], x[11]); IB(x[13], x[15]);
    wp = K->tw + (K->hLT - (q << 1)); CTL(2); w = *wp; LD(1); t_ = K->lowi[16 + l]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[0], x[4]); IB(x[8], x[12]);
    t_ = K->ch[1]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[1], x[5]); IB(x[9], x[13]);
    t_ = K->ch[1]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[2], x[6]); IB(x[10], x[14]);
    t_ = K->ch[1]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[3], x[7]); IB(x[11], x[15]);
    wp = K->tw + (K->hLT - (q << 0)); CTL(2); w = *wp; LD(1); t_ = K->lowi[0 + l]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[0], x[8]);
    t_ = K->ch[4]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[1], x[9]);
    t_ = K->ch[4]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[2], x[10]);
    t_ = K->ch[4]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[3], x[11]);
    t_ = K->ch[4]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[4], x[12]);
    t_ = K->ch[4]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[5], x[13]);
    t_ = K->ch[4]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[6], x[14]);
    t_ = K->ch[4]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[7], x[15]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; b[8 * s] = x[8]; b[9 * s] = x[9]; b[10 * s] = x[10]; b[11 * s] = x[11]; b[12 * s] = x[12]; b[13 * s] = x[13]; b[14 * s] = x[14]; b[15 * s] = x[15]; ST(16);
}
#ifdef FUSED_KERNELS
static inline void fl1_sq(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; LD(2);
    BFN(x[0], x[1]);
    FL_SQ(0); FL_SQ(1);
    IBN(x[0], x[1]);
    b[0] = x[0]; b[1] = x[1]; ST(2);
}
static inline void fl1_sqx(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; LD(2);
    BFN(x[0], x[1]);
    FL_SQX(0); FL_SQX(1);
    IBN(x[0], x[1]);
    b[0] = x[0]; b[1] = x[1]; ST(2);
}
static inline void fl1_ou(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; LD(2);
    BFN(x[0], x[1]);
    FL_OU(0); FL_OU(1);
    IBN(x[0], x[1]);
    b[0] = x[0]; b[1] = x[1]; ST(2);
}
static inline void fl1_oux(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; LD(2);
    BFN(x[0], x[1]);
    FL_OUX(0); FL_OUX(1);
    IBN(x[0], x[1]);
    b[0] = x[0]; b[1] = x[1]; ST(2);
}
static inline void fl1_mg(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; LD(2);
    BFN(x[0], x[1]);
    FL_MG(0); FL_MG(1);
    IBN(x[0], x[1]);
    b[0] = x[0]; b[1] = x[1]; ST(2);
}
static inline void fl1_fm(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; LD(2);
    BFN(x[0], x[1]);
    FL_FM(0); FL_FM(1);
    IBN(x[0], x[1]);
    b[0] = x[0]; b[1] = x[1]; ST(2);
}
static inline void ff1g(fp *b, size_t s, size_t j0, const kc_t *K, const fp *tlv, const fp *thp, size_t dh) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; LD(2);
    wp = K->tw + (K->hLT - (j0 << K->csd[0])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[1]);
    w = *tlv; LD(1);
    { fp t_ = thp[0 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[0], &x[0], &t_); LD(1); } { fp t_ = thp[1 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[1], &x[1], &t_); LD(1); }
    wp = K->tw + (j0 << K->csd[0]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[1]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; ST(2);
}
static inline void ff1z(fp *b, size_t s, size_t j0, const kc_t *K, const fp *tlv, const fp *thp, size_t dh) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; LD(2);
    IBN(x[0], x[1]);
    w = *tlv; LD(1);
    { fp t_ = thp[0 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[0], &x[0], &t_); LD(1); } { fp t_ = thp[1 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[1], &x[1], &t_); LD(1); }
    BFN(x[0], x[1]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; ST(2);
}
static inline void fl2_sq(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; LD(4);
    BFN(x[0], x[2]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]);
    BFN(x[0], x[1]); BFN(x[2], x[3]);
    FL_SQ(0); FL_SQ(1); FL_SQ(2); FL_SQ(3);
    IBN(x[0], x[1]); IBN(x[2], x[3]);
    IBN(x[0], x[2]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; ST(4);
}
static inline void fl2_sqx(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; LD(4);
    BFN(x[0], x[2]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]);
    BFN(x[0], x[1]); BFN(x[2], x[3]);
    FL_SQX(0); FL_SQX(1); FL_SQX(2); FL_SQX(3);
    IBN(x[0], x[1]); IBN(x[2], x[3]);
    IBN(x[0], x[2]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; ST(4);
}
static inline void fl2_ou(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; LD(4);
    BFN(x[0], x[2]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]);
    BFN(x[0], x[1]); BFN(x[2], x[3]);
    FL_OU(0); FL_OU(1); FL_OU(2); FL_OU(3);
    IBN(x[0], x[1]); IBN(x[2], x[3]);
    IBN(x[0], x[2]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; ST(4);
}
static inline void fl2_oux(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; LD(4);
    BFN(x[0], x[2]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]);
    BFN(x[0], x[1]); BFN(x[2], x[3]);
    FL_OUX(0); FL_OUX(1); FL_OUX(2); FL_OUX(3);
    IBN(x[0], x[1]); IBN(x[2], x[3]);
    IBN(x[0], x[2]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; ST(4);
}
static inline void fl2_mg(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; LD(4);
    BFN(x[0], x[2]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]);
    BFN(x[0], x[1]); BFN(x[2], x[3]);
    FL_MG(0); FL_MG(1); FL_MG(2); FL_MG(3);
    IBN(x[0], x[1]); IBN(x[2], x[3]);
    IBN(x[0], x[2]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; ST(4);
}
static inline void fl2_fm(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; LD(4);
    BFN(x[0], x[2]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]);
    BFN(x[0], x[1]); BFN(x[2], x[3]);
    FL_FM(0); FL_FM(1); FL_FM(2); FL_FM(3);
    IBN(x[0], x[1]); IBN(x[2], x[3]);
    IBN(x[0], x[2]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; ST(4);
}
static inline void ff2g(fp *b, size_t s, size_t j0, const kc_t *K, const fp *tlv, const fp *thp, size_t dh) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; LD(4);
    wp = K->tw + (K->hLT - (j0 << K->csd[1])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[1]); IB(x[2], x[3]);
    wp = K->tw + (K->hLT - (j0 << K->csd[0])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[2]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[1], x[3]);
    w = *tlv; LD(1);
    { fp t_ = thp[0 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[0], &x[0], &t_); LD(1); } { fp t_ = thp[1 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[1], &x[1], &t_); LD(1); } { fp t_ = thp[2 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[2], &x[2], &t_); LD(1); } { fp t_ = thp[3 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[3], &x[3], &t_); LD(1); }
    wp = K->tw + (j0 << K->csd[0]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[2]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[1], x[3]);
    wp = K->tw + (j0 << K->csd[1]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[1]); BF(x[2], x[3]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; ST(4);
}
static inline void ff2z(fp *b, size_t s, size_t j0, const kc_t *K, const fp *tlv, const fp *thp, size_t dh) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; LD(4);
    IBN(x[0], x[1]); IBN(x[2], x[3]);
    IBN(x[0], x[2]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]);
    w = *tlv; LD(1);
    { fp t_ = thp[0 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[0], &x[0], &t_); LD(1); } { fp t_ = thp[1 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[1], &x[1], &t_); LD(1); } { fp t_ = thp[2 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[2], &x[2], &t_); LD(1); } { fp t_ = thp[3 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[3], &x[3], &t_); LD(1); }
    BFN(x[0], x[2]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]);
    BFN(x[0], x[1]); BFN(x[2], x[3]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; ST(4);
}
static inline void fl3_sq(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; x[4] = b[4]; x[5] = b[5]; x[6] = b[6]; x[7] = b[7]; LD(8);
    BFN(x[0], x[4]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[6]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[7]);
    BFN(x[0], x[2]); BFN(x[4], x[6]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]);
    FL_SQ(0); FL_SQ(1); FL_SQ(2); FL_SQ(3); FL_SQ(4); FL_SQ(5); FL_SQ(6); FL_SQ(7);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]);
    IBN(x[0], x[2]); IBN(x[4], x[6]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]);
    IBN(x[0], x[4]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[6]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[7]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; b[4] = x[4]; b[5] = x[5]; b[6] = x[6]; b[7] = x[7]; ST(8);
}
static inline void fl3_sqx(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; x[4] = b[4]; x[5] = b[5]; x[6] = b[6]; x[7] = b[7]; LD(8);
    BFN(x[0], x[4]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[6]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[7]);
    BFN(x[0], x[2]); BFN(x[4], x[6]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]);
    FL_SQX(0); FL_SQX(1); FL_SQX(2); FL_SQX(3); FL_SQX(4); FL_SQX(5); FL_SQX(6); FL_SQX(7);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]);
    IBN(x[0], x[2]); IBN(x[4], x[6]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]);
    IBN(x[0], x[4]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[6]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[7]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; b[4] = x[4]; b[5] = x[5]; b[6] = x[6]; b[7] = x[7]; ST(8);
}
static inline void fl3_ou(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; x[4] = b[4]; x[5] = b[5]; x[6] = b[6]; x[7] = b[7]; LD(8);
    BFN(x[0], x[4]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[6]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[7]);
    BFN(x[0], x[2]); BFN(x[4], x[6]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]);
    FL_OU(0); FL_OU(1); FL_OU(2); FL_OU(3); FL_OU(4); FL_OU(5); FL_OU(6); FL_OU(7);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]);
    IBN(x[0], x[2]); IBN(x[4], x[6]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]);
    IBN(x[0], x[4]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[6]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[7]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; b[4] = x[4]; b[5] = x[5]; b[6] = x[6]; b[7] = x[7]; ST(8);
}
static inline void fl3_oux(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; x[4] = b[4]; x[5] = b[5]; x[6] = b[6]; x[7] = b[7]; LD(8);
    BFN(x[0], x[4]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[6]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[7]);
    BFN(x[0], x[2]); BFN(x[4], x[6]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]);
    FL_OUX(0); FL_OUX(1); FL_OUX(2); FL_OUX(3); FL_OUX(4); FL_OUX(5); FL_OUX(6); FL_OUX(7);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]);
    IBN(x[0], x[2]); IBN(x[4], x[6]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]);
    IBN(x[0], x[4]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[6]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[7]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; b[4] = x[4]; b[5] = x[5]; b[6] = x[6]; b[7] = x[7]; ST(8);
}
static inline void fl3_mg(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; x[4] = b[4]; x[5] = b[5]; x[6] = b[6]; x[7] = b[7]; LD(8);
    BFN(x[0], x[4]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[6]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[7]);
    BFN(x[0], x[2]); BFN(x[4], x[6]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]);
    FL_MG(0); FL_MG(1); FL_MG(2); FL_MG(3); FL_MG(4); FL_MG(5); FL_MG(6); FL_MG(7);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]);
    IBN(x[0], x[2]); IBN(x[4], x[6]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]);
    IBN(x[0], x[4]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[6]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[7]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; b[4] = x[4]; b[5] = x[5]; b[6] = x[6]; b[7] = x[7]; ST(8);
}
static inline void fl3_fm(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; x[4] = b[4]; x[5] = b[5]; x[6] = b[6]; x[7] = b[7]; LD(8);
    BFN(x[0], x[4]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[6]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[7]);
    BFN(x[0], x[2]); BFN(x[4], x[6]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]);
    FL_FM(0); FL_FM(1); FL_FM(2); FL_FM(3); FL_FM(4); FL_FM(5); FL_FM(6); FL_FM(7);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]);
    IBN(x[0], x[2]); IBN(x[4], x[6]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]);
    IBN(x[0], x[4]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[6]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[7]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; b[4] = x[4]; b[5] = x[5]; b[6] = x[6]; b[7] = x[7]; ST(8);
}
static inline void ff3g(fp *b, size_t s, size_t j0, const kc_t *K, const fp *tlv, const fp *thp, size_t dh) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; LD(8);
    wp = K->tw + (K->hLT - (j0 << K->csd[2])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[1]); IB(x[2], x[3]); IB(x[4], x[5]); IB(x[6], x[7]);
    wp = K->tw + (K->hLT - (j0 << K->csd[1])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[2]); IB(x[4], x[6]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]);
    wp = K->tw + (K->hLT - (j0 << K->csd[0])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[4]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[1], x[5]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[6]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[7]);
    w = *tlv; LD(1);
    { fp t_ = thp[0 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[0], &x[0], &t_); LD(1); } { fp t_ = thp[1 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[1], &x[1], &t_); LD(1); } { fp t_ = thp[2 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[2], &x[2], &t_); LD(1); } { fp t_ = thp[3 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[3], &x[3], &t_); LD(1); } { fp t_ = thp[4 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[4], &x[4], &t_); LD(1); } { fp t_ = thp[5 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[5], &x[5], &t_); LD(1); } { fp t_ = thp[6 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[6], &x[6], &t_); LD(1); } { fp t_ = thp[7 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[7], &x[7], &t_); LD(1); }
    wp = K->tw + (j0 << K->csd[0]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[4]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[1], x[5]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[6]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[7]);
    wp = K->tw + (j0 << K->csd[1]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[2]); BF(x[4], x[6]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]);
    wp = K->tw + (j0 << K->csd[2]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[1]); BF(x[2], x[3]); BF(x[4], x[5]); BF(x[6], x[7]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; ST(8);
}
static inline void ff3z(fp *b, size_t s, size_t j0, const kc_t *K, const fp *tlv, const fp *thp, size_t dh) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; LD(8);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]);
    IBN(x[0], x[2]); IBN(x[4], x[6]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]);
    IBN(x[0], x[4]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[6]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[7]);
    w = *tlv; LD(1);
    { fp t_ = thp[0 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[0], &x[0], &t_); LD(1); } { fp t_ = thp[1 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[1], &x[1], &t_); LD(1); } { fp t_ = thp[2 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[2], &x[2], &t_); LD(1); } { fp t_ = thp[3 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[3], &x[3], &t_); LD(1); } { fp t_ = thp[4 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[4], &x[4], &t_); LD(1); } { fp t_ = thp[5 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[5], &x[5], &t_); LD(1); } { fp t_ = thp[6 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[6], &x[6], &t_); LD(1); } { fp t_ = thp[7 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[7], &x[7], &t_); LD(1); }
    BFN(x[0], x[4]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[6]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[7]);
    BFN(x[0], x[2]); BFN(x[4], x[6]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; ST(8);
}
static inline void fl4_sq(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; x[4] = b[4]; x[5] = b[5]; x[6] = b[6]; x[7] = b[7]; x[8] = b[8]; x[9] = b[9]; x[10] = b[10]; x[11] = b[11]; x[12] = b[12]; x[13] = b[13]; x[14] = b[14]; x[15] = b[15]; LD(16);
    BFN(x[0], x[8]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[9]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[10]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[11]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[4], x[12]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[5], x[13]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[6], x[14]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[7], x[15]);
    BFN(x[0], x[4]); BFN(x[8], x[12]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]); BF(x[9], x[13]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[2], x[6]); BF(x[10], x[14]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[3], x[7]); BF(x[11], x[15]);
    BFN(x[0], x[2]); BFN(x[4], x[6]); BFN(x[8], x[10]); BFN(x[12], x[14]);
    wp = K->tw + K->D[2]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]); BF(x[9], x[11]); BF(x[13], x[15]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]); BFN(x[8], x[9]); BFN(x[10], x[11]); BFN(x[12], x[13]); BFN(x[14], x[15]);
    FL_SQ(0); FL_SQ(1); FL_SQ(2); FL_SQ(3); FL_SQ(4); FL_SQ(5); FL_SQ(6); FL_SQ(7); FL_SQ(8); FL_SQ(9); FL_SQ(10); FL_SQ(11); FL_SQ(12); FL_SQ(13); FL_SQ(14); FL_SQ(15);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]); IBN(x[8], x[9]); IBN(x[10], x[11]); IBN(x[12], x[13]); IBN(x[14], x[15]);
    IBN(x[0], x[2]); IBN(x[4], x[6]); IBN(x[8], x[10]); IBN(x[12], x[14]);
    wp = K->tw + (K->hLT - K->D[2]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]); IB(x[9], x[11]); IB(x[13], x[15]);
    IBN(x[0], x[4]); IBN(x[8], x[12]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]); IB(x[9], x[13]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[2], x[6]); IB(x[10], x[14]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[3], x[7]); IB(x[11], x[15]);
    IBN(x[0], x[8]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[9]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[10]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[11]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[4], x[12]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[5], x[13]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[6], x[14]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[7], x[15]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; b[4] = x[4]; b[5] = x[5]; b[6] = x[6]; b[7] = x[7]; b[8] = x[8]; b[9] = x[9]; b[10] = x[10]; b[11] = x[11]; b[12] = x[12]; b[13] = x[13]; b[14] = x[14]; b[15] = x[15]; ST(16);
}
static inline void fl4_sqx(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; x[4] = b[4]; x[5] = b[5]; x[6] = b[6]; x[7] = b[7]; x[8] = b[8]; x[9] = b[9]; x[10] = b[10]; x[11] = b[11]; x[12] = b[12]; x[13] = b[13]; x[14] = b[14]; x[15] = b[15]; LD(16);
    BFN(x[0], x[8]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[9]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[10]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[11]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[4], x[12]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[5], x[13]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[6], x[14]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[7], x[15]);
    BFN(x[0], x[4]); BFN(x[8], x[12]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]); BF(x[9], x[13]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[2], x[6]); BF(x[10], x[14]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[3], x[7]); BF(x[11], x[15]);
    BFN(x[0], x[2]); BFN(x[4], x[6]); BFN(x[8], x[10]); BFN(x[12], x[14]);
    wp = K->tw + K->D[2]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]); BF(x[9], x[11]); BF(x[13], x[15]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]); BFN(x[8], x[9]); BFN(x[10], x[11]); BFN(x[12], x[13]); BFN(x[14], x[15]);
    FL_SQX(0); FL_SQX(1); FL_SQX(2); FL_SQX(3); FL_SQX(4); FL_SQX(5); FL_SQX(6); FL_SQX(7); FL_SQX(8); FL_SQX(9); FL_SQX(10); FL_SQX(11); FL_SQX(12); FL_SQX(13); FL_SQX(14); FL_SQX(15);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]); IBN(x[8], x[9]); IBN(x[10], x[11]); IBN(x[12], x[13]); IBN(x[14], x[15]);
    IBN(x[0], x[2]); IBN(x[4], x[6]); IBN(x[8], x[10]); IBN(x[12], x[14]);
    wp = K->tw + (K->hLT - K->D[2]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]); IB(x[9], x[11]); IB(x[13], x[15]);
    IBN(x[0], x[4]); IBN(x[8], x[12]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]); IB(x[9], x[13]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[2], x[6]); IB(x[10], x[14]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[3], x[7]); IB(x[11], x[15]);
    IBN(x[0], x[8]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[9]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[10]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[11]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[4], x[12]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[5], x[13]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[6], x[14]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[7], x[15]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; b[4] = x[4]; b[5] = x[5]; b[6] = x[6]; b[7] = x[7]; b[8] = x[8]; b[9] = x[9]; b[10] = x[10]; b[11] = x[11]; b[12] = x[12]; b[13] = x[13]; b[14] = x[14]; b[15] = x[15]; ST(16);
}
static inline void fl4_ou(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; x[4] = b[4]; x[5] = b[5]; x[6] = b[6]; x[7] = b[7]; x[8] = b[8]; x[9] = b[9]; x[10] = b[10]; x[11] = b[11]; x[12] = b[12]; x[13] = b[13]; x[14] = b[14]; x[15] = b[15]; LD(16);
    BFN(x[0], x[8]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[9]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[10]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[11]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[4], x[12]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[5], x[13]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[6], x[14]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[7], x[15]);
    BFN(x[0], x[4]); BFN(x[8], x[12]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]); BF(x[9], x[13]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[2], x[6]); BF(x[10], x[14]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[3], x[7]); BF(x[11], x[15]);
    BFN(x[0], x[2]); BFN(x[4], x[6]); BFN(x[8], x[10]); BFN(x[12], x[14]);
    wp = K->tw + K->D[2]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]); BF(x[9], x[11]); BF(x[13], x[15]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]); BFN(x[8], x[9]); BFN(x[10], x[11]); BFN(x[12], x[13]); BFN(x[14], x[15]);
    FL_OU(0); FL_OU(1); FL_OU(2); FL_OU(3); FL_OU(4); FL_OU(5); FL_OU(6); FL_OU(7); FL_OU(8); FL_OU(9); FL_OU(10); FL_OU(11); FL_OU(12); FL_OU(13); FL_OU(14); FL_OU(15);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]); IBN(x[8], x[9]); IBN(x[10], x[11]); IBN(x[12], x[13]); IBN(x[14], x[15]);
    IBN(x[0], x[2]); IBN(x[4], x[6]); IBN(x[8], x[10]); IBN(x[12], x[14]);
    wp = K->tw + (K->hLT - K->D[2]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]); IB(x[9], x[11]); IB(x[13], x[15]);
    IBN(x[0], x[4]); IBN(x[8], x[12]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]); IB(x[9], x[13]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[2], x[6]); IB(x[10], x[14]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[3], x[7]); IB(x[11], x[15]);
    IBN(x[0], x[8]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[9]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[10]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[11]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[4], x[12]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[5], x[13]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[6], x[14]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[7], x[15]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; b[4] = x[4]; b[5] = x[5]; b[6] = x[6]; b[7] = x[7]; b[8] = x[8]; b[9] = x[9]; b[10] = x[10]; b[11] = x[11]; b[12] = x[12]; b[13] = x[13]; b[14] = x[14]; b[15] = x[15]; ST(16);
}
static inline void fl4_oux(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; x[4] = b[4]; x[5] = b[5]; x[6] = b[6]; x[7] = b[7]; x[8] = b[8]; x[9] = b[9]; x[10] = b[10]; x[11] = b[11]; x[12] = b[12]; x[13] = b[13]; x[14] = b[14]; x[15] = b[15]; LD(16);
    BFN(x[0], x[8]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[9]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[10]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[11]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[4], x[12]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[5], x[13]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[6], x[14]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[7], x[15]);
    BFN(x[0], x[4]); BFN(x[8], x[12]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]); BF(x[9], x[13]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[2], x[6]); BF(x[10], x[14]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[3], x[7]); BF(x[11], x[15]);
    BFN(x[0], x[2]); BFN(x[4], x[6]); BFN(x[8], x[10]); BFN(x[12], x[14]);
    wp = K->tw + K->D[2]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]); BF(x[9], x[11]); BF(x[13], x[15]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]); BFN(x[8], x[9]); BFN(x[10], x[11]); BFN(x[12], x[13]); BFN(x[14], x[15]);
    FL_OUX(0); FL_OUX(1); FL_OUX(2); FL_OUX(3); FL_OUX(4); FL_OUX(5); FL_OUX(6); FL_OUX(7); FL_OUX(8); FL_OUX(9); FL_OUX(10); FL_OUX(11); FL_OUX(12); FL_OUX(13); FL_OUX(14); FL_OUX(15);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]); IBN(x[8], x[9]); IBN(x[10], x[11]); IBN(x[12], x[13]); IBN(x[14], x[15]);
    IBN(x[0], x[2]); IBN(x[4], x[6]); IBN(x[8], x[10]); IBN(x[12], x[14]);
    wp = K->tw + (K->hLT - K->D[2]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]); IB(x[9], x[11]); IB(x[13], x[15]);
    IBN(x[0], x[4]); IBN(x[8], x[12]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]); IB(x[9], x[13]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[2], x[6]); IB(x[10], x[14]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[3], x[7]); IB(x[11], x[15]);
    IBN(x[0], x[8]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[9]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[10]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[11]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[4], x[12]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[5], x[13]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[6], x[14]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[7], x[15]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; b[4] = x[4]; b[5] = x[5]; b[6] = x[6]; b[7] = x[7]; b[8] = x[8]; b[9] = x[9]; b[10] = x[10]; b[11] = x[11]; b[12] = x[12]; b[13] = x[13]; b[14] = x[14]; b[15] = x[15]; ST(16);
}
static inline void fl4_mg(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; x[4] = b[4]; x[5] = b[5]; x[6] = b[6]; x[7] = b[7]; x[8] = b[8]; x[9] = b[9]; x[10] = b[10]; x[11] = b[11]; x[12] = b[12]; x[13] = b[13]; x[14] = b[14]; x[15] = b[15]; LD(16);
    BFN(x[0], x[8]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[9]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[10]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[11]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[4], x[12]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[5], x[13]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[6], x[14]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[7], x[15]);
    BFN(x[0], x[4]); BFN(x[8], x[12]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]); BF(x[9], x[13]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[2], x[6]); BF(x[10], x[14]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[3], x[7]); BF(x[11], x[15]);
    BFN(x[0], x[2]); BFN(x[4], x[6]); BFN(x[8], x[10]); BFN(x[12], x[14]);
    wp = K->tw + K->D[2]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]); BF(x[9], x[11]); BF(x[13], x[15]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]); BFN(x[8], x[9]); BFN(x[10], x[11]); BFN(x[12], x[13]); BFN(x[14], x[15]);
    FL_MG(0); FL_MG(1); FL_MG(2); FL_MG(3); FL_MG(4); FL_MG(5); FL_MG(6); FL_MG(7); FL_MG(8); FL_MG(9); FL_MG(10); FL_MG(11); FL_MG(12); FL_MG(13); FL_MG(14); FL_MG(15);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]); IBN(x[8], x[9]); IBN(x[10], x[11]); IBN(x[12], x[13]); IBN(x[14], x[15]);
    IBN(x[0], x[2]); IBN(x[4], x[6]); IBN(x[8], x[10]); IBN(x[12], x[14]);
    wp = K->tw + (K->hLT - K->D[2]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]); IB(x[9], x[11]); IB(x[13], x[15]);
    IBN(x[0], x[4]); IBN(x[8], x[12]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]); IB(x[9], x[13]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[2], x[6]); IB(x[10], x[14]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[3], x[7]); IB(x[11], x[15]);
    IBN(x[0], x[8]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[9]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[10]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[11]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[4], x[12]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[5], x[13]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[6], x[14]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[7], x[15]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; b[4] = x[4]; b[5] = x[5]; b[6] = x[6]; b[7] = x[7]; b[8] = x[8]; b[9] = x[9]; b[10] = x[10]; b[11] = x[11]; b[12] = x[12]; b[13] = x[13]; b[14] = x[14]; b[15] = x[15]; ST(16);
}
static inline void fl4_fm(fp *b, const kc_t *K, const fz_t *C, size_t i0, size_t il0, size_t ih) {
    fp x[16], w; const fp *wp; (void)wp; (void)w; (void)C; (void)i0; (void)il0; (void)ih; (void)K;
    x[0] = b[0]; x[1] = b[1]; x[2] = b[2]; x[3] = b[3]; x[4] = b[4]; x[5] = b[5]; x[6] = b[6]; x[7] = b[7]; x[8] = b[8]; x[9] = b[9]; x[10] = b[10]; x[11] = b[11]; x[12] = b[12]; x[13] = b[13]; x[14] = b[14]; x[15] = b[15]; LD(16);
    BFN(x[0], x[8]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[9]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[10]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[11]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[4], x[12]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[5], x[13]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[6], x[14]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[7], x[15]);
    BFN(x[0], x[4]); BFN(x[8], x[12]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]); BF(x[9], x[13]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[2], x[6]); BF(x[10], x[14]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[3], x[7]); BF(x[11], x[15]);
    BFN(x[0], x[2]); BFN(x[4], x[6]); BFN(x[8], x[10]); BFN(x[12], x[14]);
    wp = K->tw + K->D[2]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]); BF(x[9], x[11]); BF(x[13], x[15]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]); BFN(x[8], x[9]); BFN(x[10], x[11]); BFN(x[12], x[13]); BFN(x[14], x[15]);
    FL_FM(0); FL_FM(1); FL_FM(2); FL_FM(3); FL_FM(4); FL_FM(5); FL_FM(6); FL_FM(7); FL_FM(8); FL_FM(9); FL_FM(10); FL_FM(11); FL_FM(12); FL_FM(13); FL_FM(14); FL_FM(15);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]); IBN(x[8], x[9]); IBN(x[10], x[11]); IBN(x[12], x[13]); IBN(x[14], x[15]);
    IBN(x[0], x[2]); IBN(x[4], x[6]); IBN(x[8], x[10]); IBN(x[12], x[14]);
    wp = K->tw + (K->hLT - K->D[2]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]); IB(x[9], x[11]); IB(x[13], x[15]);
    IBN(x[0], x[4]); IBN(x[8], x[12]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]); IB(x[9], x[13]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[2], x[6]); IB(x[10], x[14]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[3], x[7]); IB(x[11], x[15]);
    IBN(x[0], x[8]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[9]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[10]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[11]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[4], x[12]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[5], x[13]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[6], x[14]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[7], x[15]);
    b[0] = x[0]; b[1] = x[1]; b[2] = x[2]; b[3] = x[3]; b[4] = x[4]; b[5] = x[5]; b[6] = x[6]; b[7] = x[7]; b[8] = x[8]; b[9] = x[9]; b[10] = x[10]; b[11] = x[11]; b[12] = x[12]; b[13] = x[13]; b[14] = x[14]; b[15] = x[15]; ST(16);
}
static inline void ff4g(fp *b, size_t s, size_t j0, const kc_t *K, const fp *tlv, const fp *thp, size_t dh) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; x[8] = b[8 * s]; x[9] = b[9 * s]; x[10] = b[10 * s]; x[11] = b[11 * s]; x[12] = b[12 * s]; x[13] = b[13 * s]; x[14] = b[14 * s]; x[15] = b[15 * s]; LD(16);
    wp = K->tw + (K->hLT - (j0 << K->csd[3])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[1]); IB(x[2], x[3]); IB(x[4], x[5]); IB(x[6], x[7]); IB(x[8], x[9]); IB(x[10], x[11]); IB(x[12], x[13]); IB(x[14], x[15]);
    wp = K->tw + (K->hLT - (j0 << K->csd[2])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[2]); IB(x[4], x[6]); IB(x[8], x[10]); IB(x[12], x[14]);
    wp -= K->D[2]; w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]); IB(x[9], x[11]); IB(x[13], x[15]);
    wp = K->tw + (K->hLT - (j0 << K->csd[1])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[4]); IB(x[8], x[12]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[1], x[5]); IB(x[9], x[13]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[2], x[6]); IB(x[10], x[14]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[3], x[7]); IB(x[11], x[15]);
    wp = K->tw + (K->hLT - (j0 << K->csd[0])); CTL(3); w = *wp; LD(1);
    IB(x[0], x[8]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[1], x[9]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[10]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[11]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[4], x[12]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[5], x[13]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[6], x[14]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[7], x[15]);
    w = *tlv; LD(1);
    { fp t_ = thp[0 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[0], &x[0], &t_); LD(1); } { fp t_ = thp[1 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[1], &x[1], &t_); LD(1); } { fp t_ = thp[2 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[2], &x[2], &t_); LD(1); } { fp t_ = thp[3 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[3], &x[3], &t_); LD(1); } { fp t_ = thp[4 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[4], &x[4], &t_); LD(1); } { fp t_ = thp[5 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[5], &x[5], &t_); LD(1); } { fp t_ = thp[6 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[6], &x[6], &t_); LD(1); } { fp t_ = thp[7 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[7], &x[7], &t_); LD(1); } { fp t_ = thp[8 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[8], &x[8], &t_); LD(1); } { fp t_ = thp[9 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[9], &x[9], &t_); LD(1); } { fp t_ = thp[10 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[10], &x[10], &t_); LD(1); } { fp t_ = thp[11 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[11], &x[11], &t_); LD(1); } { fp t_ = thp[12 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[12], &x[12], &t_); LD(1); } { fp t_ = thp[13 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[13], &x[13], &t_); LD(1); } { fp t_ = thp[14 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[14], &x[14], &t_); LD(1); } { fp t_ = thp[15 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[15], &x[15], &t_); LD(1); }
    wp = K->tw + (j0 << K->csd[0]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[8]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[1], x[9]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[10]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[11]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[4], x[12]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[5], x[13]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[6], x[14]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[7], x[15]);
    wp = K->tw + (j0 << K->csd[1]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[4]); BF(x[8], x[12]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[1], x[5]); BF(x[9], x[13]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[2], x[6]); BF(x[10], x[14]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[3], x[7]); BF(x[11], x[15]);
    wp = K->tw + (j0 << K->csd[2]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[2]); BF(x[4], x[6]); BF(x[8], x[10]); BF(x[12], x[14]);
    wp += K->D[2]; w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]); BF(x[9], x[11]); BF(x[13], x[15]);
    wp = K->tw + (j0 << K->csd[3]); CTL(2); w = *wp; LD(1);
    BF(x[0], x[1]); BF(x[2], x[3]); BF(x[4], x[5]); BF(x[6], x[7]); BF(x[8], x[9]); BF(x[10], x[11]); BF(x[12], x[13]); BF(x[14], x[15]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; b[8 * s] = x[8]; b[9 * s] = x[9]; b[10 * s] = x[10]; b[11 * s] = x[11]; b[12 * s] = x[12]; b[13 * s] = x[13]; b[14 * s] = x[14]; b[15 * s] = x[15]; ST(16);
}
static inline void ff4z(fp *b, size_t s, size_t j0, const kc_t *K, const fp *tlv, const fp *thp, size_t dh) {
    fp x[16], w; const fp *wp; (void)j0; (void)wp; (void)w; (void)K;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; x[8] = b[8 * s]; x[9] = b[9 * s]; x[10] = b[10 * s]; x[11] = b[11 * s]; x[12] = b[12 * s]; x[13] = b[13 * s]; x[14] = b[14 * s]; x[15] = b[15 * s]; LD(16);
    IBN(x[0], x[1]); IBN(x[2], x[3]); IBN(x[4], x[5]); IBN(x[6], x[7]); IBN(x[8], x[9]); IBN(x[10], x[11]); IBN(x[12], x[13]); IBN(x[14], x[15]);
    IBN(x[0], x[2]); IBN(x[4], x[6]); IBN(x[8], x[10]); IBN(x[12], x[14]);
    wp = K->tw + (K->hLT - K->D[2]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[3]); IB(x[5], x[7]); IB(x[9], x[11]); IB(x[13], x[15]);
    IBN(x[0], x[4]); IBN(x[8], x[12]);
    wp = K->tw + (K->hLT - K->D[1]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[5]); IB(x[9], x[13]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[2], x[6]); IB(x[10], x[14]);
    wp -= K->D[1]; w = *wp; LD(1);
    IB(x[3], x[7]); IB(x[11], x[15]);
    IBN(x[0], x[8]);
    wp = K->tw + (K->hLT - K->D[0]); CTL(2); w = *wp; LD(1);
    IB(x[1], x[9]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[2], x[10]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[3], x[11]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[4], x[12]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[5], x[13]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[6], x[14]);
    wp -= K->D[0]; w = *wp; LD(1);
    IB(x[7], x[15]);
    w = *tlv; LD(1);
    { fp t_ = thp[0 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[0], &x[0], &t_); LD(1); } { fp t_ = thp[1 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[1], &x[1], &t_); LD(1); } { fp t_ = thp[2 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[2], &x[2], &t_); LD(1); } { fp t_ = thp[3 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[3], &x[3], &t_); LD(1); } { fp t_ = thp[4 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[4], &x[4], &t_); LD(1); } { fp t_ = thp[5 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[5], &x[5], &t_); LD(1); } { fp t_ = thp[6 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[6], &x[6], &t_); LD(1); } { fp t_ = thp[7 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[7], &x[7], &t_); LD(1); } { fp t_ = thp[8 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[8], &x[8], &t_); LD(1); } { fp t_ = thp[9 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[9], &x[9], &t_); LD(1); } { fp t_ = thp[10 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[10], &x[10], &t_); LD(1); } { fp t_ = thp[11 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[11], &x[11], &t_); LD(1); } { fp t_ = thp[12 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[12], &x[12], &t_); LD(1); } { fp t_ = thp[13 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[13], &x[13], &t_); LD(1); } { fp t_ = thp[14 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[14], &x[14], &t_); LD(1); } { fp t_ = thp[15 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[15], &x[15], &t_); LD(1); }
    BFN(x[0], x[8]);
    wp = K->tw + K->D[0]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[9]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[2], x[10]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[3], x[11]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[4], x[12]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[5], x[13]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[6], x[14]);
    wp += K->D[0]; w = *wp; LD(1);
    BF(x[7], x[15]);
    BFN(x[0], x[4]); BFN(x[8], x[12]);
    wp = K->tw + K->D[1]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[5]); BF(x[9], x[13]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[2], x[6]); BF(x[10], x[14]);
    wp += K->D[1]; w = *wp; LD(1);
    BF(x[3], x[7]); BF(x[11], x[15]);
    BFN(x[0], x[2]); BFN(x[4], x[6]); BFN(x[8], x[10]); BFN(x[12], x[14]);
    wp = K->tw + K->D[2]; CTL(1); w = *wp; LD(1);
    BF(x[1], x[3]); BF(x[5], x[7]); BF(x[9], x[11]); BF(x[13], x[15]);
    BFN(x[0], x[1]); BFN(x[2], x[3]); BFN(x[4], x[5]); BFN(x[6], x[7]); BFN(x[8], x[9]); BFN(x[10], x[11]); BFN(x[12], x[13]); BFN(x[14], x[15]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; b[8 * s] = x[8]; b[9 * s] = x[9]; b[10 * s] = x[10]; b[11 * s] = x[11]; b[12 * s] = x[12]; b[13 * s] = x[13]; b[14 * s] = x[14]; b[15 * s] = x[15]; ST(16);
}
static inline void ff4c(fp *b, size_t s, size_t j0, const kc_t *K, const fp *tlv, const fp *thp, size_t dh) {
    fp x[16], w, t_; const fp *wp; (void)wp;
    x[0] = b[0 * s]; x[1] = b[1 * s]; x[2] = b[2 * s]; x[3] = b[3 * s]; x[4] = b[4 * s]; x[5] = b[5 * s]; x[6] = b[6 * s]; x[7] = b[7 * s]; x[8] = b[8 * s]; x[9] = b[9 * s]; x[10] = b[10 * s]; x[11] = b[11 * s]; x[12] = b[12 * s]; x[13] = b[13 * s]; x[14] = b[14 * s]; x[15] = b[15 * s]; LD(16);
    size_t jsh = j0 << K->sh, q = jsh >> 4, l = jsh & 15; CTL(3);
    wp = K->tw + (K->hLT - (q << 3)); CTL(2); w = *wp; LD(1); t_ = K->lowi[48 + l]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[0], x[1]); IB(x[2], x[3]); IB(x[4], x[5]); IB(x[6], x[7]); IB(x[8], x[9]); IB(x[10], x[11]); IB(x[12], x[13]); IB(x[14], x[15]);
    wp = K->tw + (K->hLT - (q << 2)); CTL(2); w = *wp; LD(1); t_ = K->lowi[32 + l]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[0], x[2]); IB(x[4], x[6]); IB(x[8], x[10]); IB(x[12], x[14]);
    t_ = K->ch[3]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[1], x[3]); IB(x[5], x[7]); IB(x[9], x[11]); IB(x[13], x[15]);
    wp = K->tw + (K->hLT - (q << 1)); CTL(2); w = *wp; LD(1); t_ = K->lowi[16 + l]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[0], x[4]); IB(x[8], x[12]);
    t_ = K->ch[1]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[1], x[5]); IB(x[9], x[13]);
    t_ = K->ch[1]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[2], x[6]); IB(x[10], x[14]);
    t_ = K->ch[1]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[3], x[7]); IB(x[11], x[15]);
    wp = K->tw + (K->hLT - (q << 0)); CTL(2); w = *wp; LD(1); t_ = K->lowi[0 + l]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[0], x[8]);
    t_ = K->ch[4]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[1], x[9]);
    t_ = K->ch[4]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[2], x[10]);
    t_ = K->ch[4]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[3], x[11]);
    t_ = K->ch[4]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[4], x[12]);
    t_ = K->ch[4]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[5], x[13]);
    t_ = K->ch[4]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[6], x[14]);
    t_ = K->ch[4]; LD(1); fp_mul(&w, &w, &t_);
    IB(x[7], x[15]);
    w = *tlv; LD(1);
    { fp t_ = thp[0 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[0], &x[0], &t_); LD(1); } { fp t_ = thp[1 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[1], &x[1], &t_); LD(1); } { fp t_ = thp[2 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[2], &x[2], &t_); LD(1); } { fp t_ = thp[3 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[3], &x[3], &t_); LD(1); } { fp t_ = thp[4 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[4], &x[4], &t_); LD(1); } { fp t_ = thp[5 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[5], &x[5], &t_); LD(1); } { fp t_ = thp[6 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[6], &x[6], &t_); LD(1); } { fp t_ = thp[7 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[7], &x[7], &t_); LD(1); } { fp t_ = thp[8 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[8], &x[8], &t_); LD(1); } { fp t_ = thp[9 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[9], &x[9], &t_); LD(1); } { fp t_ = thp[10 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[10], &x[10], &t_); LD(1); } { fp t_ = thp[11 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[11], &x[11], &t_); LD(1); } { fp t_ = thp[12 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[12], &x[12], &t_); LD(1); } { fp t_ = thp[13 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[13], &x[13], &t_); LD(1); } { fp t_ = thp[14 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[14], &x[14], &t_); LD(1); } { fp t_ = thp[15 * dh]; fp_mul(&t_, &t_, &w); fp_mul(&x[15], &x[15], &t_); LD(1); }
    w = K->tw[q]; LD(1); t_ = K->low[l]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[0], x[8]);
    t_ = K->ch[0]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[1], x[9]);
    t_ = K->ch[0]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[2], x[10]);
    t_ = K->ch[0]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[3], x[11]);
    t_ = K->ch[0]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[4], x[12]);
    t_ = K->ch[0]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[5], x[13]);
    t_ = K->ch[0]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[6], x[14]);
    t_ = K->ch[0]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[7], x[15]);
    fp_sqr(&w, &w);
    BFM(x[3], x[7]); BFM(x[11], x[15]);
    t_ = K->ch[1]; LD(1); fp_mul(&w, &w, &t_);
    BFM(x[2], x[6]); BFM(x[10], x[14]);
    t_ = K->ch[1]; LD(1); fp_mul(&w, &w, &t_);
    BFM(x[1], x[5]); BFM(x[9], x[13]);
    t_ = K->ch[1]; LD(1); fp_mul(&w, &w, &t_);
    BFM(x[0], x[4]); BFM(x[8], x[12]);
    fp_sqr(&w, &w);
    BF(x[0], x[2]); BF(x[4], x[6]); BF(x[8], x[10]); BF(x[12], x[14]);
    t_ = K->ch[2]; LD(1); fp_mul(&w, &w, &t_);
    BF(x[1], x[3]); BF(x[5], x[7]); BF(x[9], x[11]); BF(x[13], x[15]);
    fp_sqr(&w, &w);
    BFM(x[0], x[1]); BFM(x[2], x[3]); BFM(x[4], x[5]); BFM(x[6], x[7]); BFM(x[8], x[9]); BFM(x[10], x[11]); BFM(x[12], x[13]); BFM(x[14], x[15]);
    b[0 * s] = x[0]; b[1 * s] = x[1]; b[2 * s] = x[2]; b[3 * s] = x[3]; b[4 * s] = x[4]; b[5 * s] = x[5]; b[6 * s] = x[6]; b[7 * s] = x[7]; b[8 * s] = x[8]; b[9 * s] = x[9]; b[10 * s] = x[10]; b[11 * s] = x[11]; b[12 * s] = x[12]; b[13 * s] = x[13]; b[14 * s] = x[14]; b[15 * s] = x[15]; ST(16);
}
#endif
#endif
```

### poly.c

```c
/* Polynomial tools: degree scan, schoolbook product, cyclic product by transforms, power-series inverse
 * (Newton), division (schoolbook for short quotients or divisors, else by the reversed Newton identity).
 * All charged where executed. */
#include "orch.h"
#include <stdio.h>
#include <stdlib.h>

int ceil_log2(size_t n) { int k = 0; while (((size_t)1 << k) < n) { k++; CTL(4); } CTL(2); return k; }

/* top nonzero coefficient at or below maxdeg; per tested coefficient: load, 4-limb zero test and branch (5),
 * loop (3) */
long poly_deg(const fp *a, long maxdeg) {
    long d = maxdeg;
    while (d >= 0 && fp_is_zero(&a[d])) { d--; LD(1); CTL(5 + 3); }
    LD(1); CTL(5 + 2);
    return d;
}

void poly_mul_school(fp *r, const fp *a, long da, const fp *b, long db) {
    CTL(2);
    if (da < 0 || db < 0) return;
    for (long i = 0; i <= da + db; i++) { fp_zero(&r[i]); ST(1); }
    LOOPC(da + db + 1);
    for (long i = 0; i <= da; i++) {
        fp ai = a[i]; LD(1);
        for (long j = 0; j <= db; j++) { fp t; fp_mul(&t, &ai, &b[j]); fp_add(&r[i + j], &r[i + j], &t); LD(2); ST(1); CTL(1); }
        LOOPC(db + 1);
    }
    LOOPC(da + 1);
}

/* dst[0..2^n) = (src[0..len) mod x^(2^n) - 1), optionally times a scalar */
void fold_in(fp *dst, const fp *src, size_t len, int n, const fp *scale) {
    size_t L = (size_t)1 << n, c = len < L ? len : L;
    CTL(4);
    if (scale) pw_scale(dst, src, scale, c); else pw_copy(dst, src, c);
    pw_zero(dst + c, L - c);
    for (size_t j = L; j < len; j += L) {
        size_t cc = len - j < L ? len - j : L;
        if (scale) pw_addscale(dst, src + j, scale, cc); else pw_add(dst, src + j, cc);
        CTL(3 + 4);
    }
    CTL(2);
}

/* r[0..outlen) = +-(a*b mod x^L - 1)[lo .. lo+outlen), L = 2^n; 1/L folded into the input fold of b */
void poly_mul_cyc(fp *r, size_t lo, size_t outlen, const fp *a, size_t la, const fp *b, size_t lb, int n,
                  fp *A, fp *B, int neg) {
    fp il; ntt_invL(&il, n);
    fold_in(A, a, la, n, NULL);
    fold_in(B, b, lb, n, &il);
    ntt_dif(A, n); ntt_dif(B, n);
    pw_mul(A, A, B, (size_t)1 << n);
    ntt_dit(A, n);
    CTL(2);
    if (neg) pw_negcopy(r, A + lo, outlen); else pw_copy(r, A + lo, outlen);
}

/* h[0..P) = f^-1 mod x^P by Newton: h_{k2} = h_k - x^k (h_k * ((f h_k) div x^k)) mod x^(k2), k2 = min(2k, P).
 * Both products are cyclic of length 2^ceil_log2(k2) >= k2 (wrap-around: the wrapped coefficients of f h_k land
 * below x^k, outside the window [k, k2); the low k2-k coefficients of h_k e are clean for a length >= k2 - 1).
 * scratch: 2 * 2^ceil_log2(P) elements. */
void series_inv(fp *h, const fp *f, size_t lf, size_t P, fp *scratch) {
    CTL(2);
    if (P == 0) return;
    fp_inv(&h[0], &f[0]); LD(1); ST(1);
    size_t k = 1;
    while (k < P) {
        size_t k2 = 2 * k < P ? 2 * k : P;
        int n = ceil_log2(k2);
        fp *A = scratch, *B = scratch + ((size_t)1 << n);
        CTL(3 + 5);
        size_t lfk = lf < k2 ? lf : k2;
        poly_mul_cyc(h + k, k, k2 - k, f, lfk, h, k, n, A, B, 0);        /* e = (f h_k)[k .. k2) */
        poly_mul_cyc(h + k, 0, k2 - k, h, k, h + k, k2 - k, n, A, B, 1); /* -(h_k e) mod x^(k2-k) */
        k = k2;
    }
    CTL(2);
}

/* q = a div b, a[0..db) := a mod b.  Schoolbook when the quotient or the divisor is short. */
#define DIV_SCHOOL 64
long poly_divrem_ip(fp *q, fp *a, long da, const fp *b, long db) {
    CTL(2);
    if (da < db) return poly_deg(a, da);
    long dq = da - db;
    CTL(2 + 3);
    if (dq < DIV_SCHOOL || db < DIV_SCHOOL) {
        fp inv; fp_inv(&inv, &b[db]); LD(1);
        for (long i = da; i >= db; i--) {
            fp c; fp_mul(&c, &a[i], &inv); LD(1);
            q[i - db] = c; ST(1); CTL(1);
            fp *ai = a + (i - db); CTL(1);
            for (long j = 0; j < db; j++) { fp t; fp_mul(&t, &c, &b[j]); fp_sub(&ai[j], &ai[j], &t); LD(2); ST(1); }
            LOOPC(db);
        }
        LOOPC(dq + 1);
        return poly_deg(a, db - 1);
    }
    /* a quotient too long for the transform table: divide the top part in chunks of at most 2^(ntab-1) quotient
     * coefficients (each chunk: a division of degree db + c - 1 by b, in place) */
    if (ceil_log2(2 * ((size_t)dq + 1) - 1) > ntt_ntab) {
        size_t CH = (size_t)1 << (ntt_ntab - 1);
        long top = da;
        while (top >= db) {
            long c = top - db + 1; if (c > (long)CH) c = (long)CH;
            long off = top - db - c + 1;
            CTL(3 + 8);
            poly_divrem_ip(q + off, a + off, db + c - 1, b, db);
            top = off + db - 1;
        }
        CTL(2);
        return poly_deg(a, db - 1);
    }
    /* Newton: rev(q) = rev(a) * rev(b)^-1 mod x^(dq+1) */
    size_t P = (size_t)dq + 1;
    int np = ceil_log2(P);
    int nm = ceil_log2(2 * P - 1);
    int nr = ceil_log2((size_t)db);
    int ns = nm > np ? nm : np; if (nr > ns) ns = nr;
    CTL(4);
    size_t lf = (size_t)db + 1 < P ? (size_t)db + 1 : P;
    fp *f = NEWFP(P), *h = NEWFP(P), *ra = NEWFP(P);
    fp *sc = NEWFP((size_t)2 << ns);
    for (size_t i = 0; i < lf; i++) { f[i] = b[db - (long)i]; LD(1); ST(1); CTL(1); }
    LOOPC(lf);
    series_inv(h, f, lf, P, sc);
    for (size_t i = 0; i < P; i++) { ra[i] = a[da - (long)i]; LD(1); ST(1); CTL(1); }
    LOOPC(P);
    poly_mul_cyc(f, 0, P, ra, P, h, P, nm, sc, sc + ((size_t)1 << nm), 0);       /* rev(q) into f */
    for (size_t j = 0; j < P; j++) { q[j] = f[P - 1 - j]; LD(1); ST(1); CTL(2); }
    LOOPC(P);
    /* a mod b = fold(a) - (q b mod x^L - 1), L >= db (deg r < db <= L) */
    size_t L = (size_t)1 << nr;
    fp *A = sc, *B = sc + L;
    fp il; ntt_invL(&il, nr);
    fold_in(A, q, P, nr, NULL);
    fold_in(B, b, (size_t)db + 1, nr, &il);
    ntt_dif(A, nr); ntt_dif(B, nr);
    pw_mul(A, A, B, L);
    ntt_dit(A, nr);
    fold_in(B, a, (size_t)da + 1, nr, NULL);
    pw_sub(B, A, (size_t)db);
    pw_copy(a, B, (size_t)db);
    xfree(sc); xfree(ra); xfree(h); xfree(f);
    return poly_deg(a, db - 1);
}

/* full product r[0..da+db] by one cyclic product of length >= da+db+1 (schoolbook below 32 terms) */
void poly_mul(fp *r, const fp *a, long da, const fp *b, long db) {
    CTL(4);
    if (da < 0 || db < 0) return;
    if (da < 32 || db < 32) { poly_mul_school(r, a, da, b, db); return; }
    int n = ceil_log2((size_t)(da + db + 1));
    fp *A = NEWFP((size_t)2 << n);
    poly_mul_cyc(r, 0, (size_t)(da + db + 1), a, (size_t)da + 1, b, (size_t)db + 1, n, A, A + ((size_t)1 << n), 0);
    xfree(A);
}
```

### powmod.c

```c
/* Stage C: S^((p-1)/2) mod g by Montgomery reduction with R = x^L - 1 (L = 2^nmax >= m, N = 2L), on the two
 * spectral halves of the state (BUILD_LOG.md, finding 2).
 *
 * State: B = mu * b with mu = -1/2 and b = a * R mod g (a the current power, deg b < m), kept as
 *   E = DIF_L(B)            values at the even points w_N^(2k)    (= w_L^k), bit-reversed order
 *   O = DIF_L(twist(B))     values at the odd points w_N^(2k+1),  bit-reversed order.
 * One step (Mont(b^2) = b^2 R^-1 mod g, or Mont(x b^2) for an exponent bit 1):
 *   E := E^2 * GI [* x-values]      GI = 1/g_raw(w_L^k): t' = kappa' mu^2 t, t = -s g^-1 mod R, kappa' = -L/lead
 *   E := DIF(twist(DIT(E)))         the odd-point values of t'
 *   O := O^2 [* x-values] + GO * E  GO = -DIF(twist(g_raw))/L = ghat_o / kappa'; = mu^2 (s + g t)(odd) = mu^2 (-2) r = mu r
 *   E := DIF(untwist(DIT(O)))       coefficients of B_new (slots m..L-1 are zero), then its even-point values
 * Transforms per step: 4 of length L (= 2N in units of the length-N transform).
 * Start: b0 = x^v R mod g, v = 2^j (a prefix of the exponent), from Q = floor(x^(v+L) / g) (Newton, precision
 * P = v + L - m + 1): Q g = x^(v+L) - rho, b0 = rho - x^v = -(Q g mod x^L + 1) - 2 x^v, so
 * mu b0 = (Q g mod x^L + 1)/2 + x^v; its odd values are Qhat_o ghat_o / 2.
 * End: a = Mont(b) (one reduction without the square); g is recovered from GO. */
#include "orch.h"
#include "stages.h"
#include <stdio.h>
#include <stdlib.h>

static int ebit(const uint64_t e[4], int i) { CTL(4); return (int)((e[i >> 6] >> (i & 63)) & 1); }

/* one step on the state (E, O): b -> Mont(b^2), or Mont(x b^2) if bit */
void mont_step(fp *E, fp *O, const fp *GI, const fp *GO, size_t m, int bit) {
    int n = ntt_nmax;
    size_t L = (size_t)1 << n;
    CTL(4);
    pw_sqr_mul(E, GI, L);
    if (bit) tw_xmul(E, 0);
    ntt_dit(E, n);
    tw_twist(E, E, L, NULL);
    ntt_dif(E, n);
    if (bit) { pw_sqr(O, L); tw_xmul(O, 1); pw_fma(O, GO, E, L); }
    else pw_sqr_fma(O, GO, E, L);
    pw_copy(E, O, L);
    ntt_dit(E, n);
    tw_untwist(E, m);
#ifdef CHECK_TAIL
    { long d2 = poly_deg(E, (long)L - 1); if (d2 >= (long)m) { fprintf(stderr, "powmod: tail nonzero\n"); exit(6); } }
#endif
    ntt_dif(E, n);
}

/* The same step with the pointwise operations fused into the passes next to them.  State convention: E holds
 * DIF(B) without its last pass (the pass is completed inside the next fused pass); O is complete.
 * Passes per step (np passes per transform): 4 (np - 1) instead of 4 np passes plus 6 pointwise sweeps. */
void mont_step_f(fp *E, fp *O, const fp *GI, const fp *GO, int bit) {
    int n = ntt_nmax, np = ntt_npass(n);
    CTL(6);
    ntt_fused_last(E, bit ? FZ_SQX : FZ_SQ, GI, NULL, NULL);     /* E = DIT pass(E^2 GI [x]) */
    ntt_dit_range(E, n, 1, np - 1);
    ntt_fused_first(E, 0);                                       /* t: last DIT pass, twist, first DIF pass */
    ntt_dif_range(E, n, 1, np - 1);
    ntt_fused_last(E, bit ? FZ_OUX : FZ_OU, NULL, O, GO);        /* O = O^2 [x] + GO t_o; E = DIT pass(O) */
    ntt_dit_range(E, n, 1, np - 1);
    ntt_fused_first(E, 1);                                       /* last DIT pass, untwist (1/L), first DIF pass */
    ntt_dif_range(E, n, 1, np - 1);
}
void mont_final_f(fp *E, fp *O, const fp *GI, const fp *GO, size_t m) {
    int n = ntt_nmax, np = ntt_npass(n);
    CTL(6);
    ntt_fused_last(E, FZ_MG, GI, NULL, NULL);
    ntt_dit_range(E, n, 1, np - 1);
    ntt_fused_first(E, 0);
    ntt_dif_range(E, n, 1, np - 1);
    ntt_fused_last(E, FZ_FM, NULL, O, GO);
    ntt_dit_range(E, n, 0, np - 1);
    tw_untwist(E, m);
}

/* final reduction without the square: E[0..m) := coefficients of Mont(b) (rest 0) */
void mont_final(fp *E, fp *O, const fp *GI, const fp *GO, size_t m) {
    int n = ntt_nmax;
    size_t L = (size_t)1 << n;
    pw_mul(E, E, GI, L);
    ntt_dit(E, n);
    tw_twist(E, E, L, NULL);
    ntt_dif(E, n);
    pw_fma(O, GO, E, L);
    pw_copy(E, O, L);
    ntt_dit(E, n);
    tw_untwist(E, m);
}

int powmod_mont(size_t m, fp *E, fp *O, fp *GI, fp *GO, const fp *lam, powinfo_t *pi) {
    static const uint64_t EXP[4] = PM1H_LIMBS;
    int n = ntt_nmax;
    size_t L = (size_t)1 << n;
    cnt_t c0 = X;
    /* ---- choice of v = 2^j: the largest j (2^j < m, bits 252..253-j of the exponent zero) with P <= L/4 if
     * possible (Newton inside E), else P <= L/2 (one extra scratch buffer) */
    int top = 253, j = -1, big = 0;
    for (int jj = 0; jj < 128; jj++) {
        size_t v = (size_t)1 << jj, P = v + L - m + 1;
        CTL(3 + 6);
        if (v >= m || (jj > 0 && ebit(EXP, top - jj) != 0)) break;
        if (P <= L / 4) { j = jj; big = 0; }
        else if (P <= L / 2 && (j < 0 || big)) { j = jj; big = 1; }
    }
    CTL(2);
    if (j < 0) { fprintf(stderr, "powmod: no start exponent\n"); return 4; }
    size_t v = (size_t)1 << j, dq = v + L - m, P = dq + 1;
    pi->j = j; pi->P = P;
    int np = ceil_log2(P);
    fp *f = E, *h = E + P, *sc = E + 2 * P, *extra = NULL;
    CTL(4);
    if (2 * P + ((size_t)2 << np) > L) { extra = NEWFP(P + ((size_t)2 << np)); h = extra; sc = extra + P; }
    size_t lf = P < m + 1 ? P : m + 1;
    for (size_t i = 0; i < lf; i++) { f[i] = O[m - i]; LD(1); ST(1); CTL(1); }
    LOOPC(lf);
    series_inv(h, f, lf, P, sc);                       /* h = rev(g_raw L)^-1 mod x^P = rev(Q) * lead stuff */
    /* Q_raw[k] = h[dq - k]; with g_raw L = lam g_monic: h = rev(g_monic)^-1 / lam, Q_monic = lam Q_raw.
     * Odd values of mu b0 - x^v: Q_monic,o ghat_monic,o / 2, ghat_monic,o = -(L^2/lam) GO, so the factor on Q_raw
     * is lam * (-L^2/lam) / 2 = -L^2/2 (lam cancels). */
    for (size_t k = 0; k <= dq; k++) { O[k] = h[dq - k]; LD(1); ST(1); CTL(1); }
    LOOPC(dq + 1);
    if (extra) xfree(extra);
    fp c1, Lf, half;
    fp_from_u64(&Lf, L); fp_sqr(&c1, &Lf); fp_from_u64(&half, 2); fp_inv(&half, &half);
    fp_mul(&c1, &c1, &half); fp_neg(&c1, &c1);
    tw_twist(O, O, P, &c1);
    pw_zero(O + P, L - P);
    ntt_dif(O, n);
    pw_mul(O, O, GO, L);
    pw_copy(E, O, L);
    ntt_dit(E, n);
    tw_untwist(E, m);
    long tdeg = poly_deg(E, (long)L - 1);              /* the slots m..L-1 must be 0 */
    CTL(2);
    if (tdeg >= (long)m) { fprintf(stderr, "powmod: start value has degree %ld >= m\n", tdeg); return 5; }
    { fp one; fp_one(&one); fp_add(&E[v], &E[v], &one); LD(1); ST(1); }
    tw_twist(O, E, m, NULL);
    pw_zero(O + m, L - m);
    ntt_dif(O, n);
#ifdef NOFUSE
    ntt_dif(E, n);
#else
    ntt_dif_range(E, n, 0, ntt_npass(n) - 1);                   /* the last pass is done in the first step */
#endif
    cnt_t c1s = X;
    pi->newton = cnt_sub(c1s, c0);
    /* ---- the squaring loop over the exponent bits below the prefix */
    int steps = 0, xs = 0;
    for (int b = top - j - 1; b >= 0; b--) {
        int bit = ebit(EXP, b);
        CTL(3 + 2);                                    /* loop; argument */
#ifdef NOFUSE
        mont_step(E, O, GI, GO, m, bit);
#else
        mont_step_f(E, O, GI, GO, bit);
#endif
        steps++; xs += bit; CTL(2);
        CTL(4);
        if ((steps & 31) == 0) progress("  C step %d/%d", steps, top - j);
    }
    CTL(2);
    cnt_t c2 = X;
    pi->loop = cnt_sub(c2, c1s);
    pi->steps = steps; pi->xsteps = xs;
    /* ---- a = Mont(b): one reduction without the square (mu (-2) = 1) */
#ifdef NOFUSE
    mont_final(E, O, GI, GO, m);
#else
    mont_final_f(E, O, GI, GO, m);
#endif
    tdeg = poly_deg(E, (long)L - 1);
    CTL(2);
    if (tdeg >= (long)m) { fprintf(stderr, "powmod: result has degree %ld >= m\n", tdeg); return 7; }
    /* ---- g (monic) from GO: DIT gives -twist(g_raw), untwist gives -g_raw/L, times -L^2/lam = g_monic */
    pw_copy(O, GO, L);
    ntt_dit(O, n);
    tw_untwist(O, m + 1);
    fp s2, il;
    fp_inv(&il, lam); fp_mul(&s2, &c1, &il); fp_dbl(&s2, &s2);          /* -L^2 / lam */
    pw_scale(O, O, &s2, m + 1);
    { fp one; fp_one(&one); LD(1); CTL(5); if (!fp_eq(&O[m], &one)) { fprintf(stderr, "powmod: g not monic\n"); return 8; } }
    pi->fin = cnt_sub(X, c2);
    return 0;
}
```

### hgcd.c

```c
/* Stage D: G = gcd(U, V) by the recursive half-gcd (degree-reduction form, as in Thome / NTL HalfGCD), with
 * products by transforms.  Matrix convention: M (U, V) = (U', V'), M = product of [[0, 1], [1, -q]] factors,
 * so deg U' = deg U - deg m11.
 *
 * hgcd(U, V, d): returns M such that U' = M row 0, V' = M row 1 are consecutive remainders with
 *   deg U' > deg U - d >= deg V'   (or the identity if deg V <= deg U - d already);
 * only the top 2d - 1 coefficients of U, V are read.  Structure (d > HG_THR):
 *   M1 = hgcd(U1, V1, ceil(d/2)) on the top parts; (U1, V1) = M1 (U1, V1); one division U1 = Q V1 + r;
 *   M2 = hgcd(V1, r, d2), d2 = deg V1 - deg U1 + d; M = M2 [[0,1],[1,-Q]] M1.
 * The outer loop reduces (U, V) by at most DMAX per call (memory bound) and applies M to the full polynomials
 * in place, by blocks (overlap-add) when the cyclic length would exceed LMAX.
 * Every executed operation is charged; the bookkeeping of a call (degree tests, parameters, allocations)
 * is charged with the bound written next to it.
 *
 * Normal-sequence tests (the trial is charged for the normal remainder sequence, every quotient of degree 1):
 * every division tests that its quotient has degree 1 before it does any work beyond reading the degrees, every
 * hgcd call tests on return that it removed exactly its parameter (deg m11 = d - 1), a zero remainder inside
 * hgcd or in the outer loop fails the test, and the entry tests deg V = deg U - 1.  Each test is 2 control
 * operations (NTEST).  On a failed test the trial ends (ABORT): G_info.aborted = 1, every buffer of the call
 * chain is released and gcd_lean returns -2.  While every test so far has passed, every length, parameter and
 * allocation equals that of the normal sequence, so an aborted trial has executed a prefix of the normal-case
 * work (the prefix lemma of the proof). */
#define NTEST() CTL(2)
#include "orch.h"
#include "stages.h"
#include <stdio.h>
#include <stdlib.h>

#ifndef HG_THR
#define HG_THR 32          /* base case: iterative Euclid on the truncated pair */
#endif
#ifndef GCD_THR
#define GCD_THR 128        /* outer loop: classical Euclid below this degree */
#endif
#ifndef SCHOOL
#define SCHOOL 16          /* matrix products with entries below this degree: schoolbook */
#endif
#ifndef SCALED_MAX
#define SCALED_MAX 2048    /* inner divisions with a degree-1 quotient and a divisor up to this degree: scaled step */
#endif
#ifndef DMAX_DIV
#define DMAX_DIV 16        /* outer reduction per hgcd call at most L / DMAX_DIV (memory bound) */
#endif
#ifndef LMAX_DIV
#define LMAX_DIV 4         /* cyclic products longer than L / LMAX_DIV are blocked (memory bound) */
#endif

gcdinfo_t G_info;
static size_t DMAX, LMAX;

typedef struct { fp *e[4]; long d[4]; size_t cap; fp *blk; } mat_t;

static void mat_alloc(mat_t *M, size_t cap) {
    M->cap = cap; M->blk = NEWFP(4 * cap);
    for (int i = 0; i < 4; i++) { M->e[i] = M->blk + i * cap; M->d[i] = -1; }
    CTL(12);
}
static void mat_free(mat_t *M) { xfree(M->blk); }
static void mat_identity(mat_t *M) {
    fp_one(&M->e[0][0]); fp_one(&M->e[3][0]); ST(2);
    M->d[0] = 0; M->d[1] = -1; M->d[2] = -1; M->d[3] = 0; CTL(4);
}
static long mat_maxdeg(const mat_t *M) {
    long d = M->d[0];
    for (int i = 1; i < 4; i++) if (M->d[i] > d) d = M->d[i];
    CTL(12);
    return d;
}
static void mat_copy(mat_t *D, const mat_t *S) {
    for (int i = 0; i < 4; i++) {
        if (S->d[i] >= 0) pw_copy(D->e[i], S->e[i], (size_t)S->d[i] + 1);
        D->d[i] = S->d[i]; CTL(5);
    }
}

/* X' = X h0 + Y h1, Y' = X h2 + Y h3 (pointwise) */
typedef struct { fp *x, *y; const fp *h[4]; } m2_t;
static void mat2_chunk(void *a, size_t lo, size_t hi) {
    m2_t *W = a;
    fp *x = W->x + lo, *y = W->y + lo;
    const fp *h0 = W->h[0] + lo, *h1 = W->h[1] + lo, *h2 = W->h[2] + lo, *h3 = W->h[3] + lo;
    CTL(6);
    FOR8(i, hi - lo, {
        fp a0, a1, b0, b1;
        fp_mul(&a0, &x[i], &h0[i]); fp_mul(&a1, &y[i], &h1[i]);
        fp_mul(&b0, &x[i], &h2[i]); fp_mul(&b1, &y[i], &h3[i]);
        fp_add(&x[i], &a0, &a1); fp_add(&y[i], &b0, &b1);
        LD(6); ST(2); });
}
static void pw_mat2(fp *x, fp *y, const fp *h0, const fp *h1, const fp *h2, const fp *h3, size_t n) {
    m2_t W = { x, y, { h0, h1, h2, h3 } };
    CTL(4);
    par_range(n, par_chunks(n), mat2_chunk, &W);
}

/* hat of a polynomial (degree d < 2^n) times 2^-n, into buf (2^n slots) */
static void hat_scaled(fp *buf, const fp *a, long d, int n) {
    size_t Ln = (size_t)1 << n;
    CTL(2);
    if (d < 0) { pw_zero(buf, Ln); return; }
    fp il; ntt_invL(&il, n);
    fold_in(buf, a, (size_t)d + 1, n, &il);
    ntt_dif(buf, n);
}

/* r = a b (schoolbook), r zeroed for empty products; returns degree bound da+db (or -1) */
static long mul_small(fp *r, const fp *a, long da, const fp *b, long db) {
    CTL(3);
    if (da < 0 || db < 0) return -1;
    poly_mul_school(r, a, da, b, db);
    return da + db;
}

/* Out = A B (2x2 polynomial matrices); Out has capacity for the product */
static void mat_mul(mat_t *O, const mat_t *A, const mat_t *B) {
    long da = mat_maxdeg(A), db = mat_maxdeg(B);
    CTL(4);
    if (da < SCHOOL || db < SCHOOL) {
        size_t cap = (size_t)(da + db + 2);
        fp *t1 = NEWFP(cap), *t2 = NEWFP(cap);
        for (int i = 0; i < 2; i++)
            for (int jj = 0; jj < 2; jj++) {
                long d1 = mul_small(t1, A->e[2 * i], A->d[2 * i], B->e[jj], B->d[jj]);
                long d2 = mul_small(t2, A->e[2 * i + 1], A->d[2 * i + 1], B->e[2 + jj], B->d[2 + jj]);
                long dd = d1 > d2 ? d1 : d2;
                fp *o = O->e[2 * i + jj];
                for (long k = 0; k <= dd; k++) {
                    fp s; fp_zero(&s);
                    if (k <= d1) { s = t1[k]; LD(1); }
                    if (k <= d2) { fp_add(&s, &s, &t2[k]); LD(1); }
                    o[k] = s; ST(1); CTL(4);
                }
                LOOPC(dd + 1);
                O->d[2 * i + jj] = poly_deg(o, dd);
                CTL(3 + 6);
            }
        xfree(t2); xfree(t1);
        return;
    }
    int n = ceil_log2((size_t)(da + db + 1));
    size_t Ln = (size_t)1 << n;
    fp *H = NEWFP(6 * Ln);
    fp *H00 = H, *H01 = H + Ln, *H10 = H + 2 * Ln, *H11 = H + 3 * Ln, *Xb = H + 4 * Ln, *Yb = H + 5 * Ln;
    hat_scaled(H00, B->e[0], B->d[0], n); hat_scaled(H01, B->e[1], B->d[1], n);
    hat_scaled(H10, B->e[2], B->d[2], n); hat_scaled(H11, B->e[3], B->d[3], n);
    for (int i = 0; i < 2; i++) {
        /* row i: (X, Y) = (hat a_i0, hat a_i1) -> (X H00 + Y H10, X H01 + Y H11) */
        CTL(3);
        if (A->d[2 * i] >= 0) { pw_copy(Xb, A->e[2 * i], (size_t)A->d[2 * i] + 1); pw_zero(Xb + A->d[2 * i] + 1, Ln - (size_t)A->d[2 * i] - 1); }
        else pw_zero(Xb, Ln);
        if (A->d[2 * i + 1] >= 0) { pw_copy(Yb, A->e[2 * i + 1], (size_t)A->d[2 * i + 1] + 1); pw_zero(Yb + A->d[2 * i + 1] + 1, Ln - (size_t)A->d[2 * i + 1] - 1); }
        else pw_zero(Yb, Ln);
        CTL(4);
        ntt_dif(Xb, n); ntt_dif(Yb, n);
        pw_mat2(Xb, Yb, H00, H10, H01, H11, Ln);
        ntt_dit(Xb, n); ntt_dit(Yb, n);
        long d0 = da + db < (long)Ln - 1 ? da + db : (long)Ln - 1;
        long e0 = poly_deg(Xb, d0), e1 = poly_deg(Yb, d0);
        CTL(4);
        if (e0 >= 0) pw_copy(O->e[2 * i], Xb, (size_t)e0 + 1);
        if (e1 >= 0) pw_copy(O->e[2 * i + 1], Yb, (size_t)e1 + 1);
        O->d[2 * i] = e0; O->d[2 * i + 1] = e1;
    }
    xfree(H);
}

/* M := [[0,1],[1,-Q]] M  (row 0 := row 1; row 1 := row 0 - Q row 1); capacity M->cap suffices */
static void mat_qstep(mat_t *M, const fp *Q, long dq) {
    for (int c = 0; c < 2; c++) {
        long d0 = M->d[c], d1 = M->d[2 + c];
        long dp = d1 >= 0 ? d1 + dq : -1, dd = dp > d0 ? dp : d0;
        fp *t = NEWFP((size_t)(dd + 1 > 0 ? dd + 1 : 1));
        CTL(8);
        if (dp >= 0) {
            if (dq < SCHOOL || d1 < SCHOOL) poly_mul_school(t, Q, dq, M->e[2 + c], d1);
            else poly_mul(t, Q, dq, M->e[2 + c], d1);
            if (d0 >= 0) pw_rsub(t, M->e[c], (size_t)(d0 < dp ? d0 : dp) + 1);     /* t = row0 - Q row1 on the overlap */
            else pw_negcopy(t, t, (size_t)dp + 1);
            CTL(4);
            if (d0 >= 0 && d0 > dp) {
                pw_copy(t + dp + 1, M->e[c] + dp + 1, (size_t)(d0 - dp));
            } else if (d0 >= 0 && d0 < dp) {
                pw_negcopy(t + d0 + 1, t + d0 + 1, (size_t)(dp - d0));
            }
        } else if (d0 >= 0) pw_copy(t, M->e[c], (size_t)d0 + 1);
        /* row 0 := row 1, row 1 := t */
        if (d1 >= 0) pw_copy(M->e[c], M->e[2 + c], (size_t)d1 + 1);
        M->d[c] = d1;
        long dt = dd >= 0 ? poly_deg(t, dd) : -1;
        if (dt >= 0) pw_copy(M->e[2 + c], t, (size_t)dt + 1);
        M->d[2 + c] = dt;
        CTL(10);
        xfree(t);
    }
}

/* write helper for the blocked apply: dst[pos .. pos+len) (+)= src, positions >= cap go to ovf[pos - cap] */
static void put_range(fp *dst, size_t cap, fp *ovf, size_t pos, const fp *src, size_t len, int add) {
    size_t in = pos < cap ? (cap - pos < len ? cap - pos : len) : 0;
    CTL(8);
    if (in) { if (add) pw_add(dst + pos, src, in); else pw_copy(dst + pos, src, in); }
    if (len > in) {
        size_t o = pos + in - cap;
        if (add) pw_add(ovf + o, src + in, len - in); else pw_copy(ovf + o, src + in, len - in);
    }
}

/* (U, V) := M (U, V) in place; *du, *dv updated.  capU, capV: slots of the buffers. */
static void mat_apply(const mat_t *M, fp *U, long *du, size_t capU, fp *V, long *dv, size_t capV) {
    long n0 = *du, v0 = *dv, dm = mat_maxdeg(M);
    long dout = n0 - M->d[3];                     /* deg U' */
    CTL(6);
    if (dm < SCHOOL && n0 < 4 * SCHOOL) {
        size_t cap = (size_t)(n0 + dm + 2);
        fp *t1 = NEWFP(cap), *t2 = NEWFP(cap), *t3 = NEWFP(cap), *t4 = NEWFP(cap);
        long a1 = mul_small(t1, M->e[0], M->d[0], U, n0), a2 = mul_small(t2, M->e[1], M->d[1], V, v0);
        long b1 = mul_small(t3, M->e[2], M->d[2], U, n0), b2 = mul_small(t4, M->e[3], M->d[3], V, v0);
        long au = a1 > a2 ? a1 : a2, bu = b1 > b2 ? b1 : b2;
        for (long k = 0; k <= au; k++) { fp s; fp_zero(&s); if (k <= a1) s = t1[k]; if (k <= a2) fp_add(&s, &s, &t2[k]); t1[k] = s; LD(2); ST(1); CTL(6); }
        LOOPC(au + 1);
        for (long k = 0; k <= bu; k++) { fp s; fp_zero(&s); if (k <= b1) s = t3[k]; if (k <= b2) fp_add(&s, &s, &t4[k]); t3[k] = s; LD(2); ST(1); CTL(6); }
        LOOPC(bu + 1);
        long eu = au >= 0 ? poly_deg(t1, au) : -1, ev = bu >= 0 ? poly_deg(t3, bu) : -1;
        if (eu > dout || ev >= (eu < 0 ? 0 : eu + 1)) { fprintf(stderr, "hgcd: apply degree check failed\n"); exit(10); }
        if (eu >= 0) pw_copy(U, t1, (size_t)eu + 1);
        if (ev >= 0) pw_copy(V, t3, (size_t)ev + 1);
        *du = eu; *dv = ev;
        CTL(10);
        xfree(t4); xfree(t3); xfree(t2); xfree(t1);
        return;
    }
    size_t need = (size_t)dout + 1;
    int n1 = ceil_log2(need);
    CTL(3);
    if (((size_t)1 << n1) <= LMAX) {
        /* one cyclic product of length 2^n1 >= deg U' + 1: the high coefficients cancel in the sums */
        size_t Ln = (size_t)1 << n1;
        fp *HU = NEWFP(4 * Ln), *HV = HU + Ln, *T = HU + 2 * Ln, *T2 = HU + 3 * Ln;
        fold_in(HU, U, (size_t)n0 + 1, n1, NULL);
        if (v0 >= 0) fold_in(HV, V, (size_t)v0 + 1, n1, NULL); else pw_zero(HV, Ln);
        ntt_dif(HU, n1); ntt_dif(HV, n1);
        hat_scaled(T, M->e[0], M->d[0], n1);
        pw_mul(T, T, HU, Ln);
        hat_scaled(T2, M->e[1], M->d[1], n1);
        pw_fma(T, T2, HV, Ln);
        hat_scaled(T2, M->e[2], M->d[2], n1);
        pw_mul(HU, HU, T2, Ln);
        hat_scaled(T2, M->e[3], M->d[3], n1);
        pw_fma(HU, T2, HV, Ln);
        ntt_dit(T, n1); ntt_dit(HU, n1);
        long eu = poly_deg(T, (long)Ln - 1), ev = poly_deg(HU, (long)Ln - 1);
        CTL(4);
        if (eu != dout || ev >= eu) { fprintf(stderr, "hgcd: apply degrees %ld %ld (expected %ld)\n", eu, ev, dout); exit(10); }
        pw_copy(U, T, (size_t)eu + 1);
        if (ev >= 0) pw_copy(V, HU, (size_t)ev + 1);
        *du = eu; *dv = ev;
        xfree(HU);
        return;
    }
    /* blocked overlap-add, top block first, in place */
    G_info.apply_blocked++;
    int nb = ceil_log2(4 * ((size_t)dm + 1));
    while (((size_t)1 << nb) > LMAX && ((size_t)1 << (nb - 1)) >= 2 * ((size_t)dm + 1)) { nb--; CTL(6); }
    size_t Lb = (size_t)1 << nb, B = Lb - (size_t)dm;
    size_t tot = (size_t)n0 + 1;
    size_t capmin = capU < capV ? capU : capV, wtop = tot + (size_t)dm;          /* highest write position + 1 */
    size_t ovn = (wtop > capmin ? wtop - capmin : 0) + 1;
    CTL(16);
    fp *H = NEWFP(6 * Lb + 2 * ovn);
    fp *H00 = H, *H01 = H + Lb, *H10 = H + 2 * Lb, *H11 = H + 3 * Lb, *HU = H + 4 * Lb, *HV = H + 5 * Lb;
    fp *ovU = H + 6 * Lb, *ovV = ovU + ovn;
    hat_scaled(H00, M->e[0], M->d[0], nb); hat_scaled(H01, M->e[1], M->d[1], nb);
    hat_scaled(H10, M->e[2], M->d[2], nb); hat_scaled(H11, M->e[3], M->d[3], nb);
    pw_zero(ovU, 2 * ovn);
    /* V above its degree and both buffers above deg U, up to their capacity, are zeroed (they receive sums) */
    {
        size_t endU = wtop < capU ? wtop : capU, endV = wtop < capV ? wtop : capV;
        CTL(8);
        if (endU > tot) pw_zero(U + tot, endU - tot);
        if (endV > (size_t)(v0 + 1)) pw_zero(V + v0 + 1, endV - (size_t)(v0 + 1));
    }
    /* blocks from the top: [s - len, s) with len = min(B, s); no multiplication or division in the index code */
    size_t s = tot;
    do {
        size_t len = s < B ? s : B;
        s -= len;
        CTL(3 + 4);
        pw_copy(HU, U + s, len); pw_zero(HU + len, Lb - len);
        pw_copy(HV, V + s, len); pw_zero(HV + len, Lb - len);
        ntt_dif(HU, nb); ntt_dif(HV, nb);
        pw_mat2(HU, HV, H00, H01, H10, H11, Lb);
        ntt_dit(HU, nb); ntt_dit(HV, nb);
        size_t outlen = len + (size_t)dm;          /* overwrite the consumed input block, add the rest */
        put_range(U, capU, ovU, s, HU, len, 0);
        put_range(U, capU, ovU, s + len, HU + len, outlen - len, 1);
        put_range(V, capV, ovV, s, HV, len, 0);
        put_range(V, capV, ovV, s + len, HV + len, outlen - len, 1);
    } while (s > 0);
    CTL(2);
    long ou = poly_deg(ovU, (long)ovn - 1), ov = poly_deg(ovV, (long)ovn - 1);
    size_t topU = capU < wtop ? capU : wtop, topV = capV < wtop ? capV : wtop;
    long eu = poly_deg(U, (long)topU - 1), ev = poly_deg(V, (long)topV - 1);
    CTL(4);
    if (ou >= 0 || ov >= 0 || eu != dout || ev >= eu) { fprintf(stderr, "hgcd: blocked apply degrees %ld %ld (%ld)\n", eu, ev, dout); exit(10); }
    *du = eu; *dv = ev;
    xfree(H);
}

/* scaled division step for a quotient of degree 1 (no inversion): with v = V[dv], s = v^2, A = v U[du],
 * B = v U[du-1] - U[du] V[dv-1]:  s U - (A x + B) V has degree < dv; it overwrites U[0..dv).  The remainder is
 * v^2 times the true remainder (a unit multiple: degrees, and so the half-gcd, are unchanged).  Per coefficient
 * 3 multiplications, 2 subtractions. */
static long divstep1(fp *U, long du, const fp *V, long dv, fp *s, fp *A, fp *B) {
    fp v = V[dv], t; LD(4);
    fp_sqr(s, &v);
    fp_mul(A, &v, &U[du]);
    fp_mul(B, &v, &U[du - 1]); fp_mul(&t, &U[du], &V[dv - 1]); fp_sub(B, B, &t);
    { fp a, b; fp_mul(&a, s, &U[0]); fp_mul(&b, B, &V[0]); fp_sub(&U[0], &a, &b); LD(2); ST(1); }
    for (long i = 1; i < dv; i++) {
        fp a, b, c; fp_mul(&a, s, &U[i]); fp_mul(&b, A, &V[i - 1]); fp_mul(&c, B, &V[i]);
        fp_sub(&a, &a, &b); fp_sub(&U[i], &a, &c); LD(3); ST(1);
    }
    LOOPC(dv > 1 ? dv - 1 : 0);
    CTL(4);
    return poly_deg(U, dv - 1);
}
/* M := [[0,1],[1,0]] applied with the scaled quotient: row 0 := row 1, row 1 := s row 0 - (A x + B) row 1 */
static void mat_qstep1(mat_t *M, const fp *s, const fp *A, const fp *B) {
    for (int c = 0; c < 2; c++) {
        long d0 = M->d[c], d1 = M->d[2 + c];
        long dn = d1 >= 0 ? d1 + 1 : -1; if (d0 > dn) dn = d0;
        fp *r0 = M->e[c], *r1 = M->e[2 + c];
        fp *t = NEWFP((size_t)(dn + 1 > 0 ? dn + 1 : 1));
        CTL(8);
        for (long k = 0; k <= dn; k++) {
            fp acc; fp_zero(&acc);
            if (k <= d0) { fp_mul(&acc, s, &r0[k]); LD(1); }
            if (k <= d1) { fp b; fp_mul(&b, B, &r1[k]); fp_sub(&acc, &acc, &b); LD(1); }
            if (k >= 1 && k - 1 <= d1) { fp a; fp_mul(&a, A, &r1[k - 1]); fp_sub(&acc, &acc, &a); LD(1); }
            t[k] = acc; ST(1); CTL(6);
        }
        LOOPC(dn + 1);
        if (d1 >= 0) pw_copy(r0, r1, (size_t)d1 + 1);
        M->d[c] = d1;
        long dt = dn >= 0 ? poly_deg(t, dn) : -1;
        if (dt >= 0) pw_copy(r1, t, (size_t)dt + 1);
        M->d[2 + c] = dt;
        CTL(6);
        xfree(t);
    }
}

/* base case: iterative Euclid on (U, V) (local copies, modified), building M; degree-1 quotients by the scaled
 * step (no inversion), other quotients by exact division */
static void euclid_base(fp *U, long du, fp *V, long dv, long d, mat_t *M) {
    long goal = du - d;
    mat_identity(M);
    fp *q = NEWFP((size_t)d + 2);
    CTL(3);
    while (dv >= 0 && dv > goal) {
        long dq = du - dv, dr;
        G_info.divisions++; if (dq >= 2) G_info.quot_deg_ge2++; if ((uint64_t)dq > G_info.max_qdeg) G_info.max_qdeg = (uint64_t)dq;
        CTL(4);
        NTEST(); G_info.tests++;
        if (dq != 1) { G_info.aborted = 1; break; }
        if (dv >= 1) {
            fp s, A, B;
            dr = divstep1(U, du, V, dv, &s, &A, &B);
            mat_qstep1(M, &s, &A, &B);
        } else {
            dr = poly_divrem_ip(q, U, du, V, dv);
            mat_qstep(M, q, dq);
        }
        fp *t = U; U = V; V = t;
        du = dv; dv = dr;
        CTL(3 + 6);
    }
    CTL(2);
    xfree(q);
}

#define ACC(field, call) do { cnt_t a0_ = X; call; G_info.field = cnt_add(G_info.field, cnt_sub(X, a0_)); } while (0)
static void hgcd(const fp *u, long du, const fp *v, long dv, long d, mat_t *M) {
    G_info.hgcd_calls++;
    CTL(4);
    if (dv < 0 || dv <= du - d) { mat_identity(M); return; }
    long s = du - 2 * d + 2; if (s < 0) s = 0;
    long du1 = du - s, dv1 = dv - s;
    CTL(8);
    fp *U1 = NEWFP((size_t)du1 + 1), *V1 = NEWFP((size_t)du1 + 1);
    pw_copy(U1, u + s, (size_t)du1 + 1);
    pw_copy(V1, v + s, (size_t)dv1 + 1);
    CTL(2);
    if (d <= HG_THR) { ACC(c_base, euclid_base(U1, du1, V1, dv1, d, M)); xfree(V1); xfree(U1); return; }
    long d1 = (d + 1) / 2; if (d1 < 1) d1 = 1; if (d1 >= d) d1 = d - 1;
    CTL(8);
    mat_t M1; mat_alloc(&M1, (size_t)d1 + 2);        /* degree <= d1 - 1, + 1 after a degree-1 quotient */
    hgcd(U1, du1, V1, dv1, d1, &M1);
    NTEST(); G_info.tests++;                          /* return test: the call removed exactly d1 */
    if (G_info.aborted || M1.d[3] != d1 - 1) { G_info.aborted = 1; mat_free(&M1); xfree(V1); xfree(U1); return; }
    long a = du1, b = dv1;
    ACC(c_apply_in, mat_apply(&M1, U1, &a, (size_t)du1 + 1, V1, &b, (size_t)du1 + 1));
    long d2 = b - du1 + d;
    CTL(6);
    if (b < 0 || d2 <= 0) { G_info.aborted = 1; mat_free(&M1); xfree(V1); xfree(U1); return; }   /* zero remainder */
    long dq = a - b;
    NTEST(); G_info.tests++;                          /* quotient test */
    if (dq != 1) { G_info.aborted = 1; mat_free(&M1); xfree(V1); xfree(U1); return; }
    fp *Q = NEWFP((size_t)dq + 1);
    mat_t M1b, *P1 = &M1;
    CTL(4);
    if (mat_maxdeg(&M1) + dq + 1 > (long)M1.cap) {      /* a quotient of degree >= 2: a larger copy of M1 */
        mat_alloc(&M1b, (size_t)d + 1); mat_copy(&M1b, &M1); P1 = &M1b;
    }
    long r;
    G_info.divisions++; if (dq >= 2) G_info.quot_deg_ge2++; if ((uint64_t)dq > G_info.max_qdeg) G_info.max_qdeg = (uint64_t)dq;
    CTL(4);
    if (b >= 1 && b <= SCALED_MAX) {
        fp s1, A1, B1;
        ACC(c_div, r = divstep1(U1, a, V1, b, &s1, &A1, &B1));
        ACC(c_qstep, mat_qstep1(P1, &s1, &A1, &B1));
    } else {
        ACC(c_div, r = poly_divrem_ip(Q, U1, a, V1, b));
        ACC(c_qstep, mat_qstep(P1, Q, dq));
    }
    mat_t M2; mat_alloc(&M2, (size_t)d2 + 1);
    hgcd(V1, b, U1, r, d2, &M2);                     /* (U1, V1) := (V1, r) */
    NTEST(); G_info.tests++;                          /* return test of the second call; r < 0: zero remainder */
    if (G_info.aborted || r < 0 || M2.d[3] != d2 - 1) {
        G_info.aborted = 1;
        mat_free(&M2); if (P1 != &M1) mat_free(&M1b); xfree(Q); mat_free(&M1); xfree(V1); xfree(U1);
        return;
    }
    ACC(c_matmul, mat_mul(M, &M2, P1));
    CTL(10);
    mat_free(&M2);
    if (P1 != &M1) mat_free(&M1b);
    xfree(Q); mat_free(&M1); xfree(V1); xfree(U1);
}

/* gcd of U (deg du) and V (deg dv < du); buffers of capU / capV slots, overwritten.  *res: the monic gcd (in one
 * of the two buffers); returns its degree, or -2 when a normal-sequence test failed (ABORT, *res unset). */
long gcd_lean(fp **res, fp *U, long du, size_t capU, fp *V, long dv, size_t capV) {
    size_t L = (size_t)1 << ntt_nmax;
    DMAX = L / DMAX_DIV; if (DMAX < 2 * HG_THR) DMAX = 2 * HG_THR;
    LMAX = L / LMAX_DIV; if (LMAX < 1024) LMAX = 1024;
    memset(&G_info, 0, sizeof G_info);
    CTL(10);
    NTEST(); G_info.tests++;                          /* entry test: deg V = deg U - 1 */
    if (dv != du - 1) { G_info.aborted = 1; return -2; }
    while (dv >= 0 && du > GCD_THR) {
        long d = (du + 1) / 2; if (d > (long)DMAX) d = (long)DMAX;
        G_info.outer_steps++;
        CTL(3 + 6);
        if (dv > du - d) {
            mat_t M; mat_alloc(&M, (size_t)d + 1);
            hgcd(U, du, V, dv, d, &M);
            NTEST(); G_info.tests++;                  /* return test */
            if (G_info.aborted || M.d[3] != d - 1) { G_info.aborted = 1; mat_free(&M); return -2; }
            ACC(c_apply_out, mat_apply(&M, U, &du, capU, V, &dv, capV));
            mat_free(&M);
        }
        CTL(2);
        if (dv >= 0) {
            long dq = du - dv;
            NTEST(); G_info.tests++;                  /* quotient test */
            if (dq != 1) { G_info.aborted = 1; return -2; }
            fp *Q = NEWFP((size_t)dq + 1);
            long r; ACC(c_div, r = poly_divrem_ip(Q, U, du, V, dv));
            G_info.divisions++; if (dq >= 2) G_info.quot_deg_ge2++; if ((uint64_t)dq > G_info.max_qdeg) G_info.max_qdeg = (uint64_t)dq;
            xfree(Q);
            fp *t = U; U = V; V = t; size_t tc = capU; capU = capV; capV = tc;
            du = dv; dv = r;
            CTL(8);
        } else { G_info.aborted = 1; return -2; }      /* zero remainder above the classical tail */
    }
    CTL(2);
    while (dv >= 0) {
        long dq = du - dv;
        NTEST(); G_info.tests++;                      /* quotient test */
        if (dq != 1) { G_info.aborted = 1; return -2; }
        fp *Q = NEWFP((size_t)dq + 1);
        long r = poly_divrem_ip(Q, U, du, V, dv);
        G_info.divisions++; if (dq >= 2) G_info.quot_deg_ge2++; if ((uint64_t)dq > G_info.max_qdeg) G_info.max_qdeg = (uint64_t)dq;
        xfree(Q);
        fp *t = U; U = V; V = t; du = dv; dv = r;
        CTL(3 + 8);
    }
    CTL(2);
    if (du >= 0) {
        fp il; fp_inv(&il, &U[du]); LD(1);
        pw_scale(U, U, &il, (size_t)du + 1);
    }
    *res = U;
    return du;
}
```

### line.c

```c
/* The line in the input plane (DESIGN.md section 2), the digest polynomial F(W) evaluated pointwise, stage B
 * (values of g_c at the 2^n-th roots of unity, interpolation, the stored spectra of stage C), the map back from W to
 * canonical inputs, and the reference hash.  Constants come from consts.h (Montgomery form). */
#include "orch.h"
#include "stages.h"
#include <stdio.h>
#include <stdlib.h>

#define RCF(i, k) ((const fp *)RC_M[i][k])
#define MDSF(i, k) ((const fp *)MDS_M[i][k])

/* small fixed work (setup, back-map, Tonelli-Shanks, verification glue): charged as a bound of 2 loads,
 * 1 store and 6 control operations on top of every field operation executed since the snapshot */
void bound_since(cnt_t s0) {
    uint64_t ops = cnt_arith(cnt_sub(X, s0));
    X.ld += 2 * ops; X.st += ops; X.ctl += 6 * ops + 2 * ops + ops;   /* the address operations of the loads and the store */
}

static void mds_full(fp x[3]) {
    fp o[3], t;
    for (int i = 0; i < 3; i++) {
        fp_mul(&o[i], MDSF(i, 0), &x[0]);
        fp_mul(&t, MDSF(i, 1), &x[1]); fp_add(&o[i], &o[i], &t);
        fp_mul(&t, MDSF(i, 2), &x[2]); fp_add(&o[i], &o[i], &t);
    }
    x[0] = o[0]; x[1] = o[1]; x[2] = o[2];
}

void line_setup(line_t *L) {
    cnt_t s0 = X;
    fp cap = { CAP_M }, t, u, K, base[3];
    fp_add(&t, &cap, RCF(0, 2));
    fp_pow5(&K, &t);                                           /* K = (2^65 + c_{0,2})^5 */
    for (int k = 0; k < 3; k++) { fp_mul(&t, MDSF(k, 2), &K); fp_add(&base[k], &t, RCF(1, k)); }
    /* j = 0: Q solves x_1 = x_2 = 0, i.e. M10 U + M11 V = -base1, M20 U + M21 V = -base2 */
    fp det, idet, e, f, n1, n2;
    fp_mul(&t, MDSF(1, 0), MDSF(2, 1)); fp_mul(&u, MDSF(1, 1), MDSF(2, 0)); fp_sub(&det, &t, &u);
    L->ok = !fp_is_zero(&det);
    fp_inv(&idet, &det);
    fp_neg(&n1, &base[1]); fp_neg(&n2, &base[2]);
    fp_mul(&t, &n1, MDSF(2, 1)); fp_mul(&u, MDSF(1, 1), &n2); fp_sub(&e, &t, &u); fp_mul(&L->UQ, &e, &idet);
    fp_mul(&t, MDSF(1, 0), &n2); fp_mul(&u, &n1, MDSF(2, 0)); fp_sub(&f, &t, &u); fp_mul(&L->VQ, &f, &idet);
    L->a = *MDSF(0, 1); fp_neg(&L->b, MDSF(0, 0));            /* direction (a, b) = (M01, -M00): x_0 constant */
    for (int k = 0; k < 3; k++) { fp_mul(&t, MDSF(k, 0), &L->a); fp_mul(&u, MDSF(k, 1), &L->b); fp_add(&L->d[k], &t, &u); }
    fp_mul(&t, MDSF(0, 0), &L->UQ); fp_mul(&u, MDSF(0, 1), &L->VQ); fp_add(&t, &t, &u); fp_add(&L->kappa, &t, &base[0]);
    fp k5, d5[3];
    fp_pow5(&k5, &L->kappa); fp_pow5(&d5[1], &L->d[1]); fp_pow5(&d5[2], &L->d[2]);
    for (int k = 0; k < 3; k++) {
        fp_mul(&t, MDSF(k, 0), &k5); fp_add(&L->alpha[k], &t, RCF(2, k));
        fp_mul(&t, MDSF(k, 1), &d5[1]); fp_mul(&u, MDSF(k, 2), &d5[2]); fp_add(&L->beta[k], &t, &u);
    }
    L->ok = L->ok && fp_is_zero(&L->d[0]);
    CTL(10);
    bound_since(s0);
}

/* F(W): round 2 on alpha + beta W, round 3, the R partial rounds 4..3+R, rounds 60..63; digest = row 0 */
void tail_eval(fp *out, const line_t *L, const fp *W) {
    fp x[3], t;
    for (int k = 0; k < 3; k++) { fp_mul(&t, &L->beta[k], W); fp_add(&x[k], &L->alpha[k], &t); }
    for (int k = 0; k < 3; k++) fp_pow5(&x[k], &x[k]);
    mds_full(x);
    for (int k = 0; k < 3; k++) fp_add(&x[k], &x[k], RCF(3, k));
    for (int k = 0; k < 3; k++) fp_pow5(&x[k], &x[k]);
    mds_full(x);
    for (int i = 4; i < 4 + R; i++) {
        for (int k = 0; k < 3; k++) fp_add(&x[k], &x[k], RCF(i, k));
        fp_pow5(&x[0], &x[0]);
        mds_full(x);
    }
    for (int i = 60; i < 64; i++) {
        for (int k = 0; k < 3; k++) fp_add(&x[k], &x[k], RCF(i, k));
        for (int k = 0; k < 3; k++) fp_pow5(&x[k], &x[k]);
        if (i < 63) mds_full(x);
    }
    fp o;
    fp_mul(&o, MDSF(0, 0), &x[0]);
    fp_mul(&t, MDSF(0, 1), &x[1]); fp_add(&o, &o, &t);
    fp_mul(&t, MDSF(0, 2), &x[2]); fp_add(&o, &o, &t);
    *out = o;
}

/* reference hash: the reduced permutation of (nk, rho, 2^65), digest = coordinate 0 */
void ref_hash(fp *dg, const fp *nk, const fp *rho) {
    fp x[3] = { *nk, *rho, { CAP_M } };
    for (int i = 0; i < 64; i++) {
        int full = i < 4 || i >= 60, part = i >= 4 && i < 4 + R;
        if (!full && !part) continue;
        for (int k = 0; k < 3; k++) fp_add(&x[k], &x[k], RCF(i, k));
        if (full) { for (int k = 0; k < 3; k++) fp_pow5(&x[k], &x[k]); }
        else fp_pow5(&x[0], &x[0]);
        mds_full(x);
    }
    *dg = x[0];
}

void map_back(fp *nk, fp *rho, const line_t *L, const fp *W) {
    static const uint64_t E5[4] = E5INV_LIMBS;
    fp tau, U, V, t;
    fp_pow(&tau, W, E5);
    fp_mul(&t, &tau, &L->a); fp_add(&U, &L->UQ, &t);
    fp_mul(&t, &tau, &L->b); fp_add(&V, &L->VQ, &t);
    fp_pow(&t, &U, E5); fp_sub(nk, &t, RCF(0, 0));
    fp_pow(&t, &V, E5); fp_sub(rho, &t, RCF(0, 1));
}

/* ------------------------------------------------------------------ stage B */
typedef struct { const line_t *L; fp c; fp *V; } evb_t;
/* V[pos] = g_c(w^k), k = brev(pos): (F(c + zeta^k) - F(c - zeta^k)) / (2 zeta^k); each F charged C(r) */
static void eval_chunk(void *a, size_t lo, size_t hi) {
    evb_t *E = a;
    for (size_t pos = lo; pos < hi; pos++) {
        fp s, si, W1, W2, F1, F2, d;
        tw_point(&s, &si, pos);
        fp_add(&W1, &E->c, &s); fp_sub(&W2, &E->c, &s);
        cnt_t e0 = X;
        tail_eval(&F1, E->L, &W1);
        tail_eval(&F2, E->L, &W2);
        X = e0;
        X.unit += 2 * (uint64_t)CR;
        fp_sub(&d, &F1, &F2);
        fp_mul(&E->V[pos], &d, &si); ST(1);
        CTL(3 + 4);                                   /* loop; the two evaluation calls and their arguments */
    }
    CTL(2);
}

/* batch inversion by chunks: GI[i] = 1/V[i]; zf[chunk] set if a value is 0 */
typedef struct { const fp *V; fp *GI; int zero; } binv_t;
static void binv_chunk(void *a, size_t lo, size_t hi) {
    binv_t *B = a;
    fp acc = B->V[lo]; LD(1);
    B->GI[lo] = acc; ST(1);
    for (size_t i = lo + 1; i < hi; i++) { fp_mul(&acc, &acc, &B->V[i]); B->GI[i] = acc; LD(1); ST(1); }
    LOOPC(hi - lo - 1);
    CTL(5);
    if (fp_is_zero(&acc)) { B->zero = 1; return; }  /* only written, never cleared: no race on the value 1 */
    fp inv; fp_inv(&inv, &acc);
    for (size_t i = hi - 1; i > lo; i--) {
        fp t; fp_mul(&t, &inv, &B->GI[i - 1]); fp_mul(&inv, &inv, &B->V[i]);
        B->GI[i] = t; LD(2); ST(1); CTL(1);
    }
    LOOPC(hi - lo - 1);
    B->GI[lo] = inv; ST(1);
}

/* Stage B.  On return (status 0):
 *   O  = L * g_raw (coefficients, natural order; L slots; g_raw = the odd part, lead lam / L at index m)
 *   GI = 1 / g_raw(w^brev(i))          (the even-point values, inverted)
 *   GO = DIF(twist(g_raw)) * (-1/L)    (odd-point values, scaled for the Montgomery step, see powmod.c)
 *   *lam = O[m] = L * lead(g_raw)
 * Status 1: a value g(w^k) is 0 (the Montgomery reduction needs gcd(g, x^L - 1) = 1); status 2: deg g < m;
 * status 3: an interpolated coefficient above m is nonzero (impossible unless the evaluation is wrong). */
int build_g(const line_t *L, const fp *c, size_t m, fp *O, fp *GI, fp *GO, fp *lam) {
    int n = ntt_nmax;
    size_t Ln = (size_t)1 << n;
    evb_t E = { L, *c, O };
    par_range(Ln, par_chunks(Ln), eval_chunk, &E);
    binv_t B = { O, GI, 0 };
    par_range(Ln, par_chunks(Ln), binv_chunk, &B);
    CTL(2);
    if (B.zero) return 1;
    ntt_dit(O, n);
    *lam = O[m]; LD(1);
    CTL(5);
    if (fp_is_zero(lam)) return 2;
    long top = poly_deg(O, (long)Ln - 1);
    CTL(2);
    if (top != (long)m) return 3;
    fp il, sc; ntt_invL(&il, n); fp_mul(&sc, &il, &il); fp_neg(&sc, &sc);     /* -1/L^2 */
    tw_twist(GO, O, m + 1, &sc);
    pw_zero(GO + m + 1, Ln - m - 1);
    ntt_dif(GO, n);
    return 0;
}
```

### root.c

```c
/* Stage E: one root of a monic, squarefree, split polynomial G (deg G >= 1) by equal-degree splitting:
 * for a random delta, gcd(G, (x + delta)^((p-1)/2) - 1) is a proper factor with good probability; keep the smaller
 * factor until the degree is 1.  Schoolbook arithmetic (deg G is small).  The generator (xorshift64, seed 1) is
 * used only here.  A random 254-bit word: 4 xorshift steps (3 shifts, 3 xors, 1 assignment each), the mask, the
 * limb assignments and the bookkeeping: 47 control operations, plus the Montgomery conversion (1 multiplication). */
#include "orch.h"
#include "stages.h"
#include <stdio.h>
#include <stdlib.h>

#define RND_CTL 47
#define ZMAX 64

uint64_t root_round_max;      /* largest charge of one isolation round (reported; the stage-E cap uses it) */
static uint64_t rs = 1;
static uint64_t xs64(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static void rnd_fp(fp *a) {
    uint64_t v[4] = { xs64(), xs64(), xs64(), xs64() & 0x3fffffffffffffffULL };
    fp_from_limbs(a, v);
    CTL(RND_CTL);
}

/* r = a b mod G (deg a, b < dG); r has dG slots; t: 2 dG scratch */
static void mulmod(fp *r, const fp *a, const fp *b, const fp *G, long dG, fp *t, fp *q) {
    poly_mul_school(t, a, dG - 1, b, dG - 1);
    poly_divrem_ip(q, t, 2 * dG - 2, G, dG);
    pw_copy(r, t, (size_t)dG);
}

/* gcd of A (deg da) and B (deg db < da), schoolbook Euclid, in place; returns degree, *res points to it (monic) */
static long gcd_small(fp **res, fp *A, long da, fp *B, long db, fp *q) {
    while (db >= 0) {
        long r = poly_divrem_ip(q, A, da, B, db);
        fp *t = A; A = B; B = t; da = db; db = r;
        CTL(3 + 6);
    }
    CTL(2);
    fp il; fp_inv(&il, &A[da]); LD(1);
    pw_scale(A, A, &il, (size_t)da + 1);
    *res = A;
    return da;
}

int root_isolate(fp *S, const fp *G0, long dG0, uint64_t *tries) {
    static const uint64_t EXP[4] = PM1H_LIMBS;
    long d = dG0;
    fp *G = NEWFP((size_t)d + 1), *h = NEWFP((size_t)d), *base = NEWFP((size_t)d), *t = NEWFP(2 * (size_t)d + 2),
       *q = NEWFP((size_t)d + 2), *A = NEWFP((size_t)d + 1), *B = NEWFP((size_t)d + 1);
    pw_copy(G, G0, (size_t)d + 1);
    *tries = 0;
    int ok = 0;
    CTL(4);
    while (d >= 2 && *tries < ZMAX) {
        (*tries)++;
        uint64_t r0 = cnt_total(X);
        fp delta; rnd_fp(&delta);
        /* base = x + delta mod G (d >= 2: no reduction), h = base^((p-1)/2) mod G */
        pw_zero(base, (size_t)d);
        base[0] = delta; fp_one(&base[1]); ST(2);
        pw_copy(h, base, (size_t)d);
        int top = 253;
        for (int i = top - 1; i >= 0; i--) {
            mulmod(h, h, h, G, d, t, q);
            CTL(3 + 4 + 2);
            if ((EXP[i >> 6] >> (i & 63)) & 1) mulmod(h, h, base, G, d, t, q);
        }
        CTL(2);
        /* h - 1, then gcd(G, h - 1) */
        fp one; fp_one(&one); fp_sub(&h[0], &h[0], &one); LD(1); ST(1);
        long dh = poly_deg(h, d - 1);
        CTL(2);
        if (dh >= 0) {
            pw_copy(A, G, (size_t)d + 1); pw_copy(B, h, (size_t)dh + 1);
            fp *F; long df = gcd_small(&F, A, d, B, dh, q);
            CTL(4);
            if (df > 0 && df < d) {
                /* keep the smaller of F and G / F */
                CTL(2);
                if (2 * df <= d) { pw_copy(G, F, (size_t)df + 1); d = df; }
                else {
                    long dc = d - df;
                    pw_copy(t, G, (size_t)d + 1);
                    poly_divrem_ip(q, t, d, F, df);           /* exact: q = G / F, monic */
                    pw_copy(G, q, (size_t)dc + 1);
                    d = dc;
                }
            }
        }
        { uint64_t rc = cnt_total(X) - r0; if (rc > root_round_max) root_round_max = rc; }
    }
    CTL(2);
    if (d == 1) { fp_neg(S, &G[0]); LD(1); ok = 1; }
    xfree(B); xfree(A); xfree(q); xfree(t); xfree(base); xfree(h); xfree(G);
    return ok;
}
```

### main.c

```c
/* orch: one deterministic run of the collision search on Orchard Poseidon with R partial rounds.
 * usage: orch [threads]
 * Trials i = 1, 2, ... (MAXTR = 64) use the centre c = i on the line j = 0.  Stages (DESIGN.md section 3):
 *   init  transform tables          setup  the line
 *   A centre   B g_c (stage-B evaluations, interpolation, stored spectra)   C S^((p-1)/2) mod g (Montgomery)
 *   D gcd(g, R - 1) (half-gcd)      E root of G      F sqrt, W1, W2, back-map      G two reference hashes
 *   H canonical hexadecimal output  I report: one buffer, one write, exit
 * Every charged operation belongs to exactly one stage (stage_open closes the previous stage).  The stage rows,
 * the trial rows and the counters are reconciled in the report. */
#include "orch.h"
#include "stages.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <math.h>
#include <time.h>
#include <unistd.h>

#define MAXTR 64
#define DMAX_E 16                     /* stage E runs only for 1 <= deg G <= DMAX_E */
#define FREE_EO() do { xfree(O); xfree(E); } while (0)
#define STAGEC_NAME "C: S^((p-1)/2) mod g (Montgomery)"
#define STAGE_BK 1000                 /* per stage opened (bookkeeping bound) */
#define OUTCAP 8192
#define FMT_PER_BYTE 400
#define REPORT_LOOPS 20000
#define SYS_WRITE (10000 + 8 * OUTCAP)
#define SYS_EXIT 10000
#define PROLOGUE 500                  /* argument parsing, thread count, degree computation (bound) */
#define CLOCK_READS 400               /* two clock reads through the vDSO (bound) */
#define PROG_LEN 256                  /* a progress line: formatting of 256 bytes, one write of 256 bytes */
#define PROG_CHARGE ((uint64_t)FMT_PER_BYTE * PROG_LEN + 10000 + 8 * PROG_LEN)

typedef struct { const char *name; cnt_t d; size_t peak; int visits; } row_t;
static row_t rows[32]; static int nrows;
static cnt_t cur; static const char *cur_name; static int cur_trial;
static uint64_t trial_tot[MAXTR + 1];
static int verbose = 1;

static void stage_close(void) {
    if (!cur_name) return;
    cnt_t d = cnt_sub(X, cur);
    int k = 0; while (k < nrows && strcmp(rows[k].name, cur_name)) k++;
    if (k == nrows) { rows[k].name = cur_name; memset(&rows[k].d, 0, sizeof rows[k].d); rows[k].peak = 0; rows[k].visits = 0; nrows++; }
    rows[k].d = cnt_add(rows[k].d, d); rows[k].visits++;
    size_t pk = arena_stage_peak_reset();
    if (pk > rows[k].peak) rows[k].peak = pk;
    trial_tot[cur_trial] += cnt_total(d);
    cur_name = NULL;
}
static void stage_open(const char *name, int trial) {
    stage_close(); cur = X; cur_name = name; cur_trial = trial; CTL(STAGE_BK);
}

static double t_start;
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }

void progress(const char *fmt, ...) {
    char buf[PROG_LEN + 64];
    va_list ap; va_start(ap, fmt);
    int k = vsnprintf(buf, PROG_LEN - 40, fmt, ap);
    va_end(ap);
    if (k < 0) k = 0;
    if (k > PROG_LEN - 41) k = PROG_LEN - 41;
    k += snprintf(buf + k, 40, " [t=%.1fs N=%llu]\n", now() - t_start, (unsigned long long)cnt_total(X));
    X.ctl += PROG_CHARGE;
    if (verbose) { ssize_t w = write(2, buf, (size_t)k); (void)w; }
}

static char out[OUTCAP]; static size_t out_len; static int out_over;
static void outf(const char *fmt, ...) {
    va_list ap; va_start(ap, fmt);
    int k = vsnprintf(out + out_len, out_len < OUTCAP ? OUTCAP - out_len : 0, fmt, ap);
    va_end(ap);
    if (k < 0 || out_len + (size_t)k >= OUTCAP) { out_over = 1; out_len = OUTCAP; return; }
    out_len += (size_t)k;
}

/* canonical 64-digit hexadecimal: 1 conversion (1 mul) + 12 operations per digit + 5 */
static void enc_hex(char o[65], const fp *a) {
    static const char HX[] = "0123456789abcdef";
    uint64_t v[4]; fp_to_limbs(v, a);
    for (int i = 0; i < 64; i++) { int pos = 63 - i; o[i] = HX[(v[pos >> 4] >> (4 * (pos & 15))) & 15]; }
    o[64] = 0;
    CTL(64 * 12 + 5);
}

static size_t degree_m(void) { size_t D = 1; for (int i = 0; i < 6 + R; i++) D *= 5; return (D - 1) / 2; }

int main(int argc, char **argv) {
    g_threads = argc > 1 ? atoi(argv[1]) : 1;
    if (g_threads < 1) g_threads = 1;
    if (g_threads > 64) g_threads = 64;
    if (getenv("ORCH_QUIET")) verbose = 0;
    /* survey mode (evidence runs only, never the claimed run): ORCH_SURVEY=K runs exactly K centres from
     * ORCH_START (default 1) without stopping at a success; the report lists k(c), normality and status per centre */
    long survey = getenv("ORCH_SURVEY") ? atol(getenv("ORCH_SURVEY")) : 0;
    uint64_t c_start = getenv("ORCH_START") ? strtoull(getenv("ORCH_START"), NULL, 10) : 1;
    if (survey > MAXTR) survey = MAXTR;
    t_start = now();
    size_t m = degree_m();
    int nmax = 0; while (((size_t)1 << nmax) < m + 1) nmax++;
    size_t L = (size_t)1 << nmax;
    memset(&X, 0, sizeof X);
    arena_stage_peak_reset();

    stage_open("init: transform tables", 0);
    CTL(PROLOGUE);
    ntt_init(nmax, nmax);
    progress("r=%d m=%zu L=2^%d threads=%d: init done", R, m, nmax, g_threads);
    stage_open("setup: the line", 0);
    line_t Ln; line_setup(&Ln);
    CTL(2);
    if (!Ln.ok) { fprintf(stderr, "line setup failed\n"); return 4; }

    fp c, S = { { 0 } }, nk1, rho1, nk2, rho2, dg1, dg2;
    int success = 0, trials = 0;
    long t_degG[MAXTR + 1]; int t_status[MAXTR + 1]; uint64_t t_centre[MAXTR + 1], t_tries[MAXTR + 1];
    powinfo_t PI1; memset(&PI1, 0, sizeof PI1);
    gcdinfo_t GI1; memset(&GI1, 0, sizeof GI1);
    for (uint64_t i = c_start; survey ? trials < survey : !success; i++) {
        trials++;
        CTL(3 + 2);
        if (trials > MAXTR) { fprintf(stderr, "MAXTR reached\n"); return 2; }
        if (survey && success) { success = 0; }      /* survey: keep going after a collision */
        stage_open("A: centre c = i", trials);
        fp_from_u64(&c, i);
        t_centre[trials] = i; t_degG[trials] = -2; t_status[trials] = 0; t_tries[trials] = 0;
        fp *E = NEWFP(L), *O = NEWFP(L), *GIv = NEWFP(L), *GO = NEWFP(L);
        fp lam;
        stage_open("B: g_c (2H evaluations, interpolation)", trials);
        int st = build_g(&Ln, &c, m, O, GIv, GO, &lam);
        progress("trial %d centre %llu: B status %d", trials, (unsigned long long)i, st);
        CTL(2);
        if (st == 3) { fprintf(stderr, "stage B internal error\n"); return 6; }
        if (st) { t_status[trials] = 10 + st; xfree(GO); xfree(GIv); xfree(O); xfree(E); continue; }
        stage_open(STAGEC_NAME, trials);
        powinfo_t pi;
        st = powmod_mont(m, E, O, GIv, GO, &lam, &pi);
        xfree(GO); xfree(GIv);
        if (trials == 1) PI1 = pi;
        progress("trial %d: C status %d (j=%d, %d steps, %d x-steps)", trials, st, pi.j, pi.steps, pi.xsteps);
        CTL(2);
        if (st) { fprintf(stderr, "stage C internal error %d\n", st); return 6; }
        stage_open("D: gcd(g, R - 1) (half-gcd)", trials);
        { fp one; fp_one(&one); fp_sub(&E[0], &E[0], &one); LD(1); ST(1); }
        long dR = poly_deg(E, (long)m - 1);
        fp *G; long dG = gcd_lean(&G, O, (long)m, L, E, dR, L);
        if (trials == 1) GI1 = G_info;
        t_degG[trials] = dG;
        progress("trial %d: D deg G = %ld (hgcd calls %llu, divisions %llu, quotients of degree >= 2: %llu, tests %llu, aborted %llu)",
                 trials, dG, (unsigned long long)G_info.hgcd_calls, (unsigned long long)G_info.divisions,
                 (unsigned long long)G_info.quot_deg_ge2, (unsigned long long)G_info.tests, (unsigned long long)G_info.aborted);
        CTL(2);
        if (dG == -2) { t_status[trials] = 20; FREE_EO(); continue; }      /* ABORT: abnormal remainder sequence */
        CTL(2);
        if (dG < 1 || dG > DMAX_E) { t_status[trials] = dG < 1 ? 0 : 21; FREE_EO(); continue; }
        stage_open("E: root of G", trials);
        uint64_t tries = 0;
        int found = root_isolate(&S, G, dG, &tries);
        t_tries[trials] = tries;
        CTL(2);
        if (!found) { t_status[trials] = 30; FREE_EO(); continue; }
        FREE_EO();
        stage_open("F: sqrt, W1, W2, back-map", trials);
        cnt_t s0 = X;
        fp s, W1, W2;
        int sq = fp_sqrt(&s, &S);
        CTL(2);
        if (!sq) { t_status[trials] = 40; continue; }
        fp_add(&W1, &c, &s); fp_sub(&W2, &c, &s);
        map_back(&nk1, &rho1, &Ln, &W1);
        map_back(&nk2, &rho2, &Ln, &W2);
        bound_since(s0);
        stage_open("G: verification (2 reference hashes)", trials);
        {
            cnt_t e0 = X;
            ref_hash(&dg1, &nk1, &rho1);
            ref_hash(&dg2, &nk2, &rho2);
            X = e0; X.unit += 2 * (uint64_t)CR;
        }
        int same_in = fp_eq(&nk1, &nk2) && fp_eq(&rho1, &rho2), same_dg = fp_eq(&dg1, &dg2);
        CTL(3 * 8 + 6);
        success = same_dg && !same_in;
        t_status[trials] = success ? 1 : 50;
        progress("trial %d: verification %s", trials, success ? "COLLISION" : "failed");
    }
    char hx[7][65];
    stage_open("H: canonical encoding of the output", 0);
    enc_hex(hx[0], &nk1); enc_hex(hx[1], &rho1); enc_hex(hx[2], &nk2); enc_hex(hx[3], &rho2); enc_hex(hx[4], &dg1); enc_hex(hx[5], &c); enc_hex(hx[6], &S);
    stage_open("I: report formatting, single write, exit", 0);
    CTL(STAGE_BK + (uint64_t)FMT_PER_BYTE * OUTCAP + REPORT_LOOPS + SYS_WRITE + SYS_EXIT + CLOCK_READS);
    stage_close();
    double el = now() - t_start;
    /* ---------------- report (everything below is already charged in stage I) */
    outf("ORCH r=%d C(r)=%d m=%zu L=2^%d (N=2^%d) threads=%d stageC=%s\n", R, CR, m, nmax, nmax + 1, g_threads, STAGEC_NAME);
    uint64_t all = 0, trs = 0;
    for (int k = 0; k < nrows; k++) all += cnt_total(rows[k].d);
    for (int t = 0; t <= trials; t++) trs += trial_tot[t];
    uint64_t counters = cnt_total(X);
    outf("%-58s %16s %16s %16s %12s\n", "stage", "arith", "other", "total", "arena_peak");
    for (int k = 0; k < nrows; k++)
        outf("%-58s %16llu %16llu %16llu %12zu\n", rows[k].name, (unsigned long long)cnt_arith(rows[k].d),
             (unsigned long long)(cnt_total(rows[k].d) - cnt_arith(rows[k].d)), (unsigned long long)cnt_total(rows[k].d), rows[k].peak);
    for (int t = 1; t <= trials; t++)
        outf("TRIAL %d centre %llu status %d degG %ld root_tries %llu total %llu\n", t, (unsigned long long)t_centre[t], t_status[t],
             t_degG[t], (unsigned long long)t_tries[t], (unsigned long long)trial_tot[t]);
    outf("TRIAL 0 outside the trials (init, setup, H, I) total %llu\n", (unsigned long long)trial_tot[0]);
    outf("RECONCILE stages=%llu trials=%llu counters=%llu ok=%d\n", (unsigned long long)all, (unsigned long long)trs,
         (unsigned long long)counters, all == trs && trs == counters);
    outf("TYPES add=%llu sub=%llu mul=%llu sqr=%llu ld=%llu st=%llu ctl=%llu unit=%llu thread=%llu\n",
         (unsigned long long)X.add, (unsigned long long)X.sub, (unsigned long long)X.mul, (unsigned long long)X.sqr, (unsigned long long)X.ld,
         (unsigned long long)X.st, (unsigned long long)X.ctl, (unsigned long long)X.unit, (unsigned long long)X.thr);
    outf("NOTHREAD total_without_thread_charges=%llu regions=%llu active_threads_sum=%llu chunks_sum=%llu\n", (unsigned long long)(counters - X.thr),
         (unsigned long long)g_regions, (unsigned long long)g_active_sum, (unsigned long long)g_chunk_sum);
    outf("STAGEC trial1 j=%d v=2^%d P=%zu steps=%d xsteps=%d start=%llu loop=%llu per_step=%llu final=%llu\n", PI1.j, PI1.j, PI1.P,
         PI1.steps, PI1.xsteps, (unsigned long long)cnt_total(PI1.newton), (unsigned long long)cnt_total(PI1.loop),
         (unsigned long long)(PI1.steps ? cnt_total(PI1.loop) / (uint64_t)PI1.steps : 0), (unsigned long long)cnt_total(PI1.fin));
    outf("STAGED trial1 outer=%llu hgcd_calls=%llu divisions=%llu quot_deg_ge2=%llu max_qdeg=%llu blocked_applies=%llu tests=%llu aborted=%llu\n",
         (unsigned long long)GI1.outer_steps, (unsigned long long)GI1.hgcd_calls, (unsigned long long)GI1.divisions,
         (unsigned long long)GI1.quot_deg_ge2, (unsigned long long)GI1.max_qdeg, (unsigned long long)GI1.apply_blocked,
         (unsigned long long)GI1.tests, (unsigned long long)GI1.aborted);
    outf("SUMMARY N=%llu units=%.1f log2(N/C(r))=%.5f\n", (unsigned long long)counters, (double)counters / CR, log2((double)counters / CR));
    outf("ARENA size=%zu high_water=%zu\n", arena_size(), arena_hwm());
    outf("TIME elapsed=%.2fs\n", el);
    if (success) {
        outf("COLLISION root_S 0x%s\n", hx[6]);
        outf("COLLISION centre 0x%s\nCOLLISION nk1 0x%s\nCOLLISION rho1 0x%s\nCOLLISION nk2 0x%s\nCOLLISION rho2 0x%s\nCOLLISION digest 0x%s\n",
             hx[5], hx[0], hx[1], hx[2], hx[3], hx[4]);
    }
    if (out_over) return 3;
    ssize_t w = write(1, out, out_len); (void)w;
    return success ? 0 : 1;
}
```

