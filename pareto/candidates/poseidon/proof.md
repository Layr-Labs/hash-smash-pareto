## 1. Claim

Target: `poseidon-orchard-r6-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, six partial rounds 4, 5, 6, 7, 8 and 9, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

**What this entry is, and credit.** This entry is Jbenisek's algorithm at r = 6 (entry 18369013, the best-scoring entry at this round count (in review, not human-accepted), normalized cost 53.85281) with the lean stages C and D of bradcush's r = 21 entry e6dcb600, ported to r = 6 and recomputed here. Jbenisek (entry 18369013 and the family of entries it belongs to) designed the algorithm and the construction, wrote the premise `H-GEOM-w2` with its reduction, the proof text reproduced here, the rows of the ledger other than C and D, the evidence and the experiments. bradcush (e6dcb600) contributed the changes of stages C and D used here: (1) the truncated second recursive call of the half-gcd (lemma 4.4); (2) stage D charged for the normal remainder sequence, with the quotient and return tests, the ABORT and the premise `H-NORMAL`; (3) the allocator's flat statistics charge on every allocation and free (at this r every product fits one transform of at most `3 * 2^32` points, so e6dcb600's block products and squaring step do not apply, and stage C is Jbenisek's, plus that charge). Passages from those entries are reproduced with attribution; "we" and "our" in reproduced passages refer to their authors, and neither author has reviewed this package. This package adds: (a) a re-implementation of the ledger of stages C and D (Appendix E), written for this package from the printed text of e6dcb600's ledger (read, not run), which reproduces the totals asserted by e6dcb600 at r = 21 exactly and evaluates them at r = 6; (b) the evaluation at this r; (e) the placement of every array in the two-ended pool and slab classes of 4.2 (Jbenisek's allocator), with the remainder of a division written over its dead dividend, and the arena found by simulating that allocator on the complete allocation sequence of a trial (section 7); (f) the coset-solve workspace of stage B in the allocation walk; (g) an explicit charge for the reset of the allocator after an ABORT; (h) small-size checks of the half-gcd of 4.4 (Appendix G.2; the appendix also checks two procedures of e6dcb600's block mode that this r does not use); (i) the return test strengthened to fire on a zero last remainder as well (4.4, 6.3(b)), so that the prefix argument of 6.3 holds for every input; (j) the three organizer-executed normality experiments of 10.5.1 (`experiments/exp_normal.py`), evidence for `H-NORMAL` at degrees 12 to 312. Papers: Bariant, Bouvier, Leurent and Perrin (ToSC 2022(3), the two-round bypass); Thome (2003) and Stehle and Zimmermann (2004), the padded half-gcd with both recursive calls truncated. Grok (xAI) jobs 133-140, reproduced from entry 18369013: the moment reduction and its constants, the Markov cap, the toy theorems, the certificate program, the monodromy lemma and the block-NTT schemes.

* The algorithm: draw a centre `c` uniformly from `F_p` from fresh random words, build the odd part `g_c` of the line polynomial by evaluation and one inverse transform, compute `G = gcd(g_c, S^((p-1)/2) - 1)` by a power-mod and a half-gcd (which ABORTs the trial on an abnormal remainder sequence), and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` in at most `Z = 64` rounds, take its square root, map back and verify the two inputs with the reference hash. At most `K = 2` centres are tried, one after the other, on a single thread; the first verified collision ends the algorithm.
* `success_probability = 0.41959`: from `H-GEOM-w2` (section 9.2) as in Jbenisek's entry, with `q = 0.24816`, `K = 2`, `eps_iso < 2^-48`, `eps_coin < 2^-128`; with the ABORT of stage D the bound is `P >= 1 - (1 - q + delta)^K - K (eps_iso + eps_coin)`, `delta = 0.01` from `H-NORMAL` (9.5). Its exact value is `0.419599814` (9.2(g); `0.434736614` with `delta = 0`, the bound that Jbenisek's entry claims as `0.43473`).
* `time_log2 = 38.53110` in target-compression units (`C(6) = 342` primitive operations per unit): the operation count of section 6, `T_fixed + K * T_trial + T_off` with every trial charged in full (stage D for the normal remainder sequence, which bounds every trial since an abnormal one aborts after a prefix of that work, 6.3; stage E at its cap of `Z` rounds at degree `DMAX`), `N_max = 135,731,132,850,836` operations, `log2(N_max / 342) = 38.52989249`, claimed as `38.53110`: rounded up at five decimals after adding 0.0012, a margin of `113,652,529,489` operations for any charge this count may have missed. The offline derivation of the constants (section 6.2) is bounded by 1,000,000 operations; that bound is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 34.857` (`31,056,744,908` bytes = `2^34.85419`, section 7): the arena found by simulating the allocator of 4.2 on the allocation sequence of a trial, plus code, static data and stack. The claimed bound is above the arena and above the live-set peak of section 7 taken by itself, so it does not depend on accepting the allocator model. Normalized cost `38.53110 + (34.857 - 20) = 53.38810`, against 53.85281 for entry 18369013 (time 38.93581, memory 34.917). This is the Pareto track's scoring policy `hashsmash-orchard-tm-v1` (`normalizedTimeMemoryLog2 = time_log2 + max(0, memory_log2_bytes - 20)`); the cost model's own time-only score is `time_log2`.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; `130` words at most (section 4.1.1), and a draw (one word) costs 31 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^12`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Declared heuristics (claim.json): `H-GEOM-w2` (score-critical, section 9.1, Jbenisek's premise, unchanged) and `H-NORMAL` (score-critical for the success probability only, section 9.5, e6dcb600's premise restated at this r). The costs are the declared cost model, not heuristics: the charging rules of section 4.2 (the register file of 18 words of 256 bits whose operands are not charged as loads, Jbenisek's disclosed interpretation of the model; every array access is charged), and the arena of section 7, the capacity of the allocator of 4.2 on the allocation sequence of one trial, found by simulation. Everything else is proved or counted: the line construction, the degree of `F`, the odd-part reduction, the collision criterion (sections 2, 3, 5), the truncation lemma 4.4, the Cauchy-Schwarz reduction (section 9.2), the isolation lemma (section 9.4), the independence of the centres, the cap rules and every operation count (sections 4, 6, 7).

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a
bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the
deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`.
`(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`.
The algorithm uses the line `j = 0`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant
`M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS, nonzero on the deployed constants, checked). Let
`(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, where
`d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i`
(the supports are disjoint). After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8, 9 (partial), 60, 61, 62, 63 (full) put twelve S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^12 = D = 244,140,625`. The leading coefficient is obtained by
propagating leading coefficients through the twelve layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used:
`f_D(0) = 0x34bd5acc9093858597cb29a9ca5405d90d50343d4924ce1be148b06792258969`
(computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 122,070,312`, `g_c` has degree exactly `m` and
leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives `s = 0` and is not a root of `S^((p-1)/2) - 1`).
`G` divides `S^((p-1)/2) - 1`, which is squarefree, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. `H = 201,326,592 = 3 * 2^26` divides `p - 1` (`p - 1 = 2^32 * 3 * q`), and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity
and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`. One inverse transform of size `H` returns the
coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). The `2H = 402,653,184` evaluations of `F` are each charged as
one target-compression unit (`C(6) = 342` operations), although a line evaluation (affine start, the remaining rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation.
The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 zeta^i)`, two multiplications for the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, one store with its address operation,
the loop control, the update of the row counter `row = k mod 3` (increment, comparison, branch, assignment; no modulo instruction), and the executed shifts, masks, ors and loop control of the bit-reversed index `layout_index_r`, which are counted inside that function) is charged on top.


## 4. The algorithm (at most K centres, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   twiddle table (once)
setup:  the line (line_setup) (once)
for t = 1, 2, ..., K:                                  [the test t <= K is made at the start of every trial; no other exit except success]
  A  c := a uniform element of F_p from one fresh random word (section 4.1.1)
  B  g := monic g_c, by section 3 (402,653,184 evaluations + one inverse NTT of size 201,326,592 + the test that the leading coefficient is nonzero + normalisation by the leading coefficient)
  C  R := S^((p-1)/2) mod g           (left-to-right square-and-multiply on the exponent, base S; 227 modular squarings, 45 of the steps also multiply by S by a streaming shift)
  D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4; every division tests that its quotient has degree 1, and on any other quotient the trial ABORTs: it ends, the allocator is reset, next t)
  E  if deg G = 0 or deg G > DMAX: the trial ends, next t.   Otherwise isolate a root S of G (section 4.1.2).  If none is isolated within Z rounds: the trial ends, next t.
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (342 operations each) are equal and the pairs differ -> go to H; otherwise the trial ends, next t
H  output: the two pairs (and the digest and the centre) are converted to canonical form and encoded as 64 hexadecimal digits each.
   If t > K was reached the algorithm fails (the failure event, probability bounded in section 9).
```
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. Binary powering therefore performs 253 modular squarings and 45 multiplications by `S`; the 26 bits after the leading one are zero, so the algorithm starts from the monomial `S^v` with `v = 2^26 < m` (this absorbs 26 of the 253 squarings, 26 + 227 = 253), and the squaring loop of stage C has 227 steps, of which 45 also multiply by `S` (a streaming shift).

Stopping rule over the `K` centres. The loop bound `K = 2` is a constant of the algorithm. A trial is run to its end, or to an ABORT in stage D, whatever its outcome; the claim charges every trial at its maximum (stage D for the normal remainder sequence, stages E to G at their worst case, section 6), so a trial that fails early or aborts is paid for at the full-trial price, never less. Stage E is entered only when `1 <= deg G <= DMAX`, and at most `Z` rounds are made in it. The algorithm has no other loop whose length depends on data: the loops of stages B and C have lengths fixed by `m` and the exponent (section 4.3), the powering has a fixed number of steps, and on a normal remainder sequence the half-gcd has a fixed recursion: 21 levels of recursion in `hgcd` (the parameter `k` starts at `floor((n+1)/2) = 61,035,156` and is halved, rounded up, until it is at most 96) and at most 21 repetitions of the outer loop of the Euclid driver (each repetition removes more than half of the degree, from 122,070,312 to at most 192). A remainder sequence that is not normal is detected at its first quotient of degree other than 1, before any work that the normal sequence would not do, and the trial ends there (section 6.3). Hence the number of executed operations is at most `N_max` for every coin sequence and every target value, the algorithm cannot stop early except by success or by failure after `K` trials, and nothing in the claim depends on a run being lucky.

#### 4.1.1 Coins

The only randomness of the algorithm is the cost model's random-word primitive (fresh independent algorithmic coins): an independent uniform 256-bit word, each use returning a fresh word, uniform on `0..2^256-1` and independent of everything else, and costing one operation. **Probability space:** every probability of section 9 is over these words. A draw is one fresh word `y`; the draw is `x = y mod p`, computed by at most three steps `if y >= p then y := y - p` (`y < 2^256 < 4p`, so three steps bring `y` below `p`). Write `2^256 = 3p + s0` with `0 < s0 < p`: the residues below `s0` have exactly four preimages below `2^256` and the other `S3 = p - s0 = 4p - 2^256` residues have exactly three, so `P[x = z] = 4/2^256` or `3/2^256` for every residue `z`, every residue has probability at least `3/2^256`, and all but `S3` residues have probability `4/2^256`. The draw is within statistical distance `S3 (1/p - 3/2^256) = 1.574e-39 (2^-128.90) < 2^-128` of uniform on `F_p`. A draw costs 31 operations: for the word one random-word operation, one load, one store into the cell `y` and three control operations (two addresses, the increment of the word index), 6 in all; for the reduction three steps each of a comparison, a conditional branch and a field subtraction (9 operations), with the loop control of 3 per iteration and 2 on exit (11); one Montgomery conversion of `x` (1); the entry of the call (2) and the address of `y` (2). Draws are made once per trial for the centre and once per isolation round for the shift: at most `K (1 + Z) = 130` draws, `130` words. No word is used twice, and the number of words used before a draw depends only on earlier words, so each draw is independent of the earlier course of the algorithm.

#### 4.1.2 Stage E: isolating a root of G

`G` is monic, squarefree, and a product of `d = deg G` distinct linear factors over `F_p` with `1 <= d <= DMAX` (it divides `S^((p-1)/2) - 1`, which is squarefree). The roots `r` of `G` are the usable `S`. While `deg G >= 2`, and for at most `Z` rounds (`ZCAP`): draw `a` (a draw as in 4.1.1; if it is 0, `a := 1`, since the Taylor shift uses `1/a`; the zero test is 5 operations and the replacement 2, charged in every round), replace `G` by `G(Z - a)` (a Taylor shift; its roots are `r + a`) and add `a` to a running shift, compute `X_a = Z^((p-1)/2) mod G` by schoolbook square-and-multiply, `G_+ = gcd(G, X_a - 1)` and `G_- = gcd(G, X_a + 1)` by classical Euclid. Then `G = G_+ G_- Z^e0` with `e0` = 1 if `G(0) = 0` and 0 otherwise. Keep, as the new `G`, the one of `G_+`, `G_-` of smaller nonzero degree (ties: `G_+`) if at least one is nonconstant; if both are constant then `G = Z` (the root is 0). When `deg G = 1` the loop ends and the root of the original `G` is `-G_0` minus the running shift. If `deg G >= 2` remains after `Z` rounds the trial fails (it ends, next `t`). Each round is charged at the cost of its operations at degree `deg G <= DMAX` (section 6). The lemma of section 9.4 bounds the probability that `deg G >= 2` remains after `Z` rounds.

### 4.2 Machine model and charging rules

Every operation of the algorithm is counted where it executes; none is estimated.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications, 330 operations; `x^e`; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each, and each such access is charged together with one address-formation operation (one control operation).
* every loop: `3n + 2` control operations for `n` iterations (the index update, the bound comparison and the conditional branch of each iteration, and one comparison and branch when the loop is left). Loops over the elements of an array written eight elements per pass (the pointwise, copy, fold and subtraction loops of the powering and of the products) are charged 3 per pass of eight, 1 for the bound, 2 when the main loop is left, and 3 per iteration for the remaining 0 to 7 elements.
* every other executed index or control operation, one each: shift, mask, or, addition, subtraction, comparison, conditional branch, assignment of a register, and the selection of an element of the register block (16 data words) by a computed index. Data-dependent tests are charged per executed test.
* index arithmetic uses only shifts, additions, subtractions, comparisons and branches (the benchmark's primitive list has no integer multiplication, division or modulo): a multiplication by a power of two is a shift, by 3 or 5 a shift and an addition, and a product of an index and a stride is a running sum; each is charged as a control operation where it occurs.
* transforms: a transform of size `3 * 2^a` is a twiddle-free radix-3 stage (8 operations per leaf) followed by three rows of radix-2 passes of at most four layers. A pass works on blocks of `2^k <= 16` points held in registers; each butterfly is three field operations (none for the multiplication when the twiddle is 1), each twiddle is one load with its address operation (the first twiddle of a layer also 2 operations of address formation), and the group and block loops around a block are charged 3 per iteration and 2 on exit. The working registers are a disclosed assumption: the 16 data words, the twiddle operand and the butterfly temporary, a register file of 18 words of 256 bits. The 256-bit constants of the radix-3 stage are loaded at every use.
* random words: the cost model's random-word primitive (an independent uniform 256-bit word) is one operation per word. The word of a draw is also loaded, stored into the cell `y` of the draw and addressed (one load, one store and three control operations), 6. A draw is that word (6), the reduction modulo `p` (three steps each of a comparison, a conditional branch and a field subtraction, 9, with the loop control of three iterations, 11), the conversion of the result to the internal representation (1), the entry (2) and the address of `y` (2): 31 operations. The shift of an isolation round is also tested for zero (5 operations) and, if zero, replaced by 1 (2 operations).
* the bit loops of inversion and exponentiation executed outside stages with a per-operation rule: 2,310 control operations per inversion.
* small-degree work in the line setup, the schoolbook `Z^((p-1)/2)` for `d <= 40` and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 6 control operations.
* the reduced permutation evaluations of stage B: 342 each (section 3), instead of their (smaller) expanded arithmetic. Nothing else is charged as a unit.
* Montgomery conversions: every conversion of an integer to or from the internal representation (for example the word converted in a draw, the exponent in the Taylor shift, the constants of the twiddle setup, the inputs of the two reference hashes and the six conversions of the output in stage H) is one Montgomery multiplication and is charged as one field multiplication. The constants of the permutation are stored in Montgomery form and need no conversion.
* output (stages H and I): in stage H the answer (two pairs, the digest and the centre) is converted out of the Montgomery representation (6 multiplications) and encoded as 64 hexadecimal digits each at 12 operations per digit and 5 per call. Stage I charges everything after the last step of the algorithm: the formatting of the report, 400 operations per byte of a buffer of 8,192 bytes (a decimal digit costs at most 44 operations, a copied byte at most 10, a conversion at most 150), 20,000 operations of report loops, 100 for the entry and the length check, one write system call at `10000 + 8 * 8,192` and one exit system call at 10,000 (a system call is 10,000 operations plus 8 per byte copied), and the bookkeeping of the stage (2 * 1,000).
* allocation (the two-ended pool and slab classes of Jbenisek's entries at r = 8 to 20; the end of every statement is this package's, 4.3 and 4.4): every array is taken from one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes (`need` bytes), and `need` decides the allocator. A block of more than `2^18 = 262,144` bytes comes from the pool, one region with two ends (low and high): its blocks follow each other in address order, each with a header (size, size of the previous block, in-use flag), no two free blocks are adjacent, and the unused middle between the two ends is one free block. Each allocation statement uses one end, fixed in advance by the rule of 4.4 (stage D: an end derived from the result end `ys` passed to the call of `hgcd` that executes the statement) and 4.3 (stage C: a constant of the statement); the statements of stages A and B and every statement not named there use the low end. A request walks the blocks of its end from that end inward, takes the first free block with at least `need` bytes (the unused middle is the last block of either walk), cuts it on the side nearest its end and leaves the rest free when the rest is at least 128 bytes (else it belongs to the block); a free merges the block with a free neighbour on either side, the unused middle included. Since no two free blocks are adjacent and a walk ends at the middle, a walk examines at most `2 P + 1` blocks, `P` the live blocks of its end. A block of at most `2^18` bytes comes from the slab classes: its class `j` is the least `j >= 7` with `2^j >= need`; a request takes the first slot of the free list of its class, else a new slot of `2^j` bytes from the end of the slab area, and writes the class and the in-use flag into the header; a free puts the slot on the free list of its class. Charges, inside the stage rows: every allocation `1 + 120 + 13 (2 L + 1) + 64` operations, `L` the live blocks at that point (this covers a pool request, 97 operations besides the walk and 13 per block examined with `P <= L`, and a slab request, at most 126, as in Jbenisek's entries), and every free `105 + 64`; the second 64 is the flat statistics charge that e6dcb600 adds on every allocation and free. An allocation and a free that the program replaces by writing in place (the remainder of a division written over its dividend, 4.4) stay charged. The memory of both allocators is the arena of section 7.
* allocator statistics (e6dcb600's reading of the rule above): the flat 64 of the allocator's statistics is charged on every allocation and on every free in Appendix E (rows C and D), and as an allowance of 64 for each of at most `10^10` allocator calls per trial in the rows A, B, E, F and G, which this package takes from Jbenisek's entry unexpanded (section 6).
* trial loop: the test of the trial counter, its increment and the bookkeeping of the trial, at most 12 operations per trial, are `TRIAL_EXTRA` = 12 in the ledger; the loop test and update of stage A are 5.
* the offline derivation of the constants is charged in section 6.2.


### 4.3 Stage C: the powering schedule (in place, no stored spectra)

At r = 6 every product of stage C fits one transform of at most `3 * 2^32` points, and stage C is Jbenisek's cyclic form below, unchanged (its charge is Jbenisek's row C plus the allocator's flat statistics charge on its three allocations and three frees, `6 * 64 = 384` operations). Placement (this package, 4.2): every array of stage C (`Y`, the row buffer `tmp` and `MU`) takes the low end of the pool. (The text below is Jbenisek's.)

For the exponent `E` (here `(p-1)/2`), `m` the degree of the modulus, `N = 3 * 2^a >= 2m - 1` and `N' = 3 * 2^b >= m + 1`. A transform of size `3 * 2^a` is a twiddle-free radix-3 stage (Good-Thomas; each radix-3 leaf costs 8 operations) followed by three independent
rows of radix-2 transforms of length `2^a`, run as passes of at most four layers (blocks of at most 16 data words in registers; with the two working words the register file is 18 words of 256 bits, see section 4.2). The state is `s = a / N` so no scaling is needed in the loop.
One step maps the residue `a` (`m` coefficients, stored in the buffer `Y` of `N` elements) to `a^2 mod g`:
```
Y := conv_sq(Y)                       square: forward transform, pointwise square fused with the first inverse pass, inverse transform
F[i] := Y[i] + Y[i+N'] (i < m)       fold of the low part modulo x^N' - 1 (saved in the buffer F of m elements)
Y[0..m-2] := Y[m..2m-2]               high part T1 of the square
Y := conv(Y, MU)                      quotient q (Barrett): MU = x^(N-m+2) * floor(x^(2m-2)/g) / (N N') stored compactly (m-1 elements)
Y := conv_N'(Y, g)                    (q * g) mod (x^N' - 1)
Y[i] := F[i] - Y[i] (i < m)           new residue; if the exponent bit is 1: shift by x and subtract lead * g (streaming)
```
The spectra of `MU` and of `g` are not stored: for each multiplication the second operand is transformed one row of the Good-Thomas layout at a time into a buffer `tmp`, immediately multiplied into the corresponding row of `Y`, and discarded.
`MU` is computed once from `g` by Newton iteration with the same row-wise products. The leading exponent bits are absorbed by starting from the monomial `S^v` with `v < m`.
All charges of this stage depend only on `m` and the exponent, not on the coefficients.
### 4.4 Stage D: the half-gcd (e6dcb600's procedure: truncated second call, normal sequence with the quotient and return tests)

Notation: a polynomial is stored as its coefficient array with the top coefficient nonzero (length = degree + 1). Euclid sequence of `(a, b)`, `deg a > deg b`: `r_0 = a`, `r_1 = b`, `r_{i-1} = q_i r_i + r_{i+1}`; `d_j = deg q_1 + ... + deg q_j`, so `deg r_j = deg a - d_j`;
`R_j = Q_1 ... Q_j` with `Q_i = [[q_i, 1], [1, 0]]` (entries of degree at most `d_j`; the first-row entries of degree exactly `d_j` for `r11`), and `(r_0, r_1)^T = R_j (r_j, r_{j+1})^T`.

The text of this section up to the paragraph *Placement* is e6dcb600's (bradcush), whose procedure this package uses; it replaces the half-gcd of Jbenisek's entry, whose second recursive call received the whole reduced pair. The return test of steps (1) and (5) is strengthened by this package (it fires on a zero last remainder too, 6.3(b)); the rest is e6dcb600's text.

`hgcd(a, b, k)` (`deg a = n`) returns, for `h = max{ j : d_j <= k }`, the matrix `R_h` (when asked) and the pair `(r_h, r_{h+1})` (when asked). The procedure: if `b = 0` or `n - deg b > k` return the identity. If `k <= 96`, plain Euclid (`poly_divrem_naive`) while the next quotient degree fits the remaining parameter; a division step whose quotient has two coefficients (the normal case) is one pass over the remainder, `r_k = a_k - q0 b_k - q1 b_(k-1)`, with `b_(k-1)` kept from the previous iteration and no copy of `a` (per element 2 loads, 2 multiplications, 2 subtractions, 1 store, each load and store with its address operation, the loop control of 3 and the test `if (k)` of 2 operations), and `R := R Q` for a two-coefficient quotient is likewise one pass per entry pair (`mul_add_q2`).
Otherwise, `k1 = ceil(k/2)` (`k1 = floor(n/2)` if `2 k1 > n`), `s = n - 2 k1`: (1) `R1 = hgcd(a quo x^s, b quo x^s, k1)` (the top parts, matrix wanted, no pair wanted); if it returns `d_1 != k1`, the trial ABORTs (the return test), whether or not its last remainder is zero (a normal sequence whose gcd has degree at most 96 always reaches `d_1 = k1` here, 6.3(b); a call that stops short has met either a zero remainder of the whole pair, which means a gcd of degree at least 96 > `DMAX`, or, by lemma 4.4, a quotient of the whole pair of degree other than 1; in both cases the trial cannot succeed, so no successful trial is lost); (2) `(c, d) = R1^{-1} (a, b)` by NTT products (`apply_inv`): `c = s (r22 a - r12 b)`, `d = s (r11 b - r21 a)`, `s = (-1)^h`, evaluated cyclically on `3 * 2^j` points (the high coefficients of `c` and `d` cancel, so the cyclic result is exact); the Good-Thomas rows are processed one at a time, and in each row `a` and `b` and each of the four matrix entries are transformed once (six forward transforms of a row) and the two output rows are inverse transformed (`conv_bilin_otf`), the sign of each output being absorbed in the scale factor `1/N`; (at this r every product of stage D fits one transform); (3) if `d = 0` or the next quotient degree `deg c - deg d` exceeds `k - d_1` (`d_1 = deg R1`) return `R1` and `(c, d)`; (4) if `deg c - deg d != 1` the trial ABORTs (a comparison and a branch, charged at every division); otherwise divide `c = q d + e` (`q` of two coefficients: one pass, as in the base case); (5) put `k3 = k - d_1 - 1` and `s3 = deg d - 2 k3`. If `s3 > 0`: `R2 = hgcd(d quo x^s3, e quo x^s3, k3)` (the top parts, matrix wanted, no pair wanted), with the return test, and only when the caller wants the reduced pair, `(c', d') = R2^{-1} (d, e)` by `apply_inv`; if `s3 <= 0`: `R2, (c', d') = hgcd(d, e, k3)`, with the return test. Return `R1 Q R2` (matrix products by NTT, only if the matrix is wanted; the product of the two 2 x 2 matrices transforms each of the eight entries once per row, with the right-factor entries of one column pair held and the left-factor entries streamed, and inverse transforms the four outputs, `conv_bilin_otf` again;) and `(c', d')` when asked.
The outer function `poly_gcd_own` repeats, while `deg b > 0` and `n = deg a > 192`: `(c, d) = hgcd(a, b, floor((n+1)/2))` (pair wanted, matrix not wanted), the return test, the ABORT test of the quotient degree and one division `c = q d + e` by a quotient of two coefficients, and `(a, b) := (d, e)`; at or below 192 it runs classical Euclid with the same test; at the end it scales the last nonzero remainder to be monic (one inversion, `deg + 1` multiplications). The only calls that want the reduced pair are those of `poly_gcd_own` and, recursively, the second calls with `s3 <= 0` inside them; every call inside a first call, and every truncated second call, wants the matrix only.

**Lemma 4.4 (truncation; e6dcb600).** Let `deg a = n > deg b`, let `a*`, `b*` agree with `a`, `b` on every coefficient of degree at least `t`, where `t <= n - 2k`, and let `q_1, q_2, ...` be the quotients and `d_j` their degree sums for `(a, b)`. Then every quotient `q_j` with `d_j <= k` is also the `j`-th quotient of `(a*, b*)`, and the stopping test of `hgcd(., ., k)` (the next quotient degree exceeds `k - d_h`, or the next remainder is zero) has the same outcome for both pairs. *Proof.* Induction on `j`. Let `q_1, ..., q_(j-1)` be common and `R = R_(j-1)`; the entries of `R^(-1)` (the adjugate of `R` up to sign) have degree at most `d_(j-1)`. So `r_(j-1) - r*_(j-1)` and `r_j - r*_j` are `R^(-1)` applied to `(a - a*, b - b*)`, of degree `< t + d_(j-1)`. Now `deg r_j = n - d_j` and the quotient of `r_(j-1)` by `r_j` depends only on their coefficients of degree at least `deg r_j - deg q_j = n - 2 d_j + d_(j-1)`. If `d_j <= k` this bound is at least `n - 2k + d_(j-1) >= t + d_(j-1)`, above the degree of the differences, so `deg r*_j = deg r_j` and `q*_j = q_j`. For the stopping test after `h` quotients: `d_(h+1) > k` holds iff `deg r_(h+1) < n - k` (or `r_(h+1) = 0`), and the coefficients of `r_(h+1)` and `r*_(h+1)` of degree at least `n - k >= t + d_h` agree, so the test has the same outcome. QED. Applied with `a* = x^s (a quo x^s)` (`t = s = n - 2 k1`), the first call's quotients are those of `(a, b)`; dividing by `x^s` changes no quotient. Applied to the second call with `t = s3 = deg d - 2 k3`, likewise; the returned `R2` is the product of the quotient matrices of `(d, e)`, so `R2^{-1} (d, e)` is the reduced pair of `(d, e)` and `R1 Q R2 = R_h` for `(a, b)`. Appendix G.2 (this package's check) runs this half-gcd against the plain Euclidean algorithm over the Pallas field and confirms that every recursive call runs on at most `2k + 1` coefficients.

**Division and the two tests (e6dcb600; the return test strengthened by this package).** On the normal remainder sequence every division of stage D (in `hgcd`, in the base case and in `poly_gcd_own`) has a quotient of two coefficients and is the one-pass division above. Two tests, 2 operations each and charged wherever they execute, detect any other sequence: the *quotient test* at every division (a quotient used by the algorithm has degree 1), and the *return test* after every recursive call and every call of `poly_gcd_own` (the call returned exactly its parameter `k` as degree count; a zero last remainder does not exempt it: this package's strengthening of e6dcb600's test, see 6.3(b)). On a normal sequence whose gcd has degree at most 96 neither test fails: by lemma 4.4 every quotient a call uses is a quotient of the whole pair, hence of degree 1, no call of `hgcd` meets a zero remainder (6.3(b)), and a call with parameter `k` stops exactly after `k` of them (with `d_j = j` the stopping test fails first at `j = k + 1`). If either test fails the trial ABORTs, so the Newton division (`divrem_fast`) of Jbenisek's entry is never run.

**Placement (this package).** These rules fix the end of the pool (4.2) of every array of stage D; they change no operation count (the allocations and frees are the same statements, in the same number, at the same live counts; Appendix E checks the totals against the untraced ledger). `poly_gcd_own` passes to `hgcd` the result end `ys` = the end of `g` and `F` (the low end). (i) A call that returns the reduced pair and no matrix owns its operands, which lie on `ys`: its first call is passed `ys` (so `R1` lies inside the operands), its `apply_inv` writes `c`, `d` and its working arrays on the other end, the division and the second call use that end (the truncated second call is passed the other end), and its final `apply_inv` writes `(c', d')` on `ys`. (ii) A call that returns a matrix keeps its own arrays (`c`, `d`, the division, the outputs of `mat_mul` and its working arrays) on `ys`; its two calls are passed the other end, where `mat_mulQ` also writes its two new entries, and `mat_mul` frees all of these after writing `R` on `ys`. (iii) `apply_inv` allocates `d` before `c` (so `c`, which is freed first, is the innermost); in a product that fits one transform, the output arrays are allocated before the row buffers, and the work arrays of `mat_mul` are taken from the end of its factors, before its row buffers. (iv) The remainder `e` of a division `c = q d + e` by a two-coefficient quotient is written over `c` when the array of `c` has exactly the length of `e`'s array (block mode: `c` is an output of `apply_inv` of its exact length): each `e_i = c_i - q_0 d_i - q_1 d_(i-1)` is formed after `c_i` is read and `c` is not used after the division. The allocation of `e` and the free of `c` that this saves stay charged. Section 7 shows the effect: the pool's high-water mark is the peak of the live set at this r to within the figure stated there.

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes and compares them; the algorithm outputs only if they are equal and the pairs differ; it never outputs a non-collision. This section is a statement about the output of a successful run, and holds for every coin sequence. It contains no probability.

## 6. Ledger: operation count, every trial at its maximum (primitive operations; `C(6) = 342`)

Notation: `T_fixed` = init (twiddle table) + setup (the line) + the plan_invN misses + stage H + stage I; `T_trial` = stages A to D of one trial, stage E at its cap, stages F and G, the trial loop, the allocator statistics of the unexpanded rows and the reset after an ABORT; `T_off` = the offline bound of section 6.2. The claim is `N_max = T_fixed + K * T_trial + T_off` with `K = 2`, and `time_log2 = ceil_5(log2(N_max / 342) + 0.0012)`.

Every stage is charged by the rules of section 4.2 where it executes. Every trial is charged as if its gcd had degree 0 in stages A to D (the larger case), and in addition with stage E at its cap, stage F at its worst case and stage G. The rows other than C and D are Jbenisek's rows at this r (entry 18369013, section 6 there), unchanged except for the four rows marked as added.

| row | what is charged | operations |
|---|---|---:|
| init | twiddle table of `2^(27-1)` elements (`ntt_init(27)`: 5 operations per element, loop control, the roots of unity, the inversions of the setup) | 536,889,025 |
| setup | the line (`line_setup`) | 4,910 |
| A (per trial) | stage bookkeeping 1,000, loop test and update 5, the coin draw 31, one allocation | 1,196 |
| B (per trial) | `201,326,592` points, each with two evaluations of `F` (at `c + zeta^i` and `c - zeta^i`) at `C(6) = 342` operations each, the loop work around them, the inverse transform of size `201,326,592`, the normalisation | 202,448,149,150 |
| B, coset-solve workspace (per trial, added) | the allocation and free of the workspace of the geometric solve, now in the allocation walk of stage B (an allowance) | 10,000 |
| C (per trial) | `S^((p-1)/2) mod g`: Newton reciprocal, `227` squaring steps, 45 multiplications by `S` (section 4.3); expanded in Appendix E | 57,870,590,362,676 |
| D (per trial) | half-gcd of `(g, R - 1)` (section 4.4, truncated second call) on the normal remainder sequence, with the test of every quotient degree and of every return (section 6.3); expanded in Appendix E | 9,152,091,036,683 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16` (below) | 166,079,773 |
| F (per trial) | square root, back-map (below) | 47,012 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 342 + 32` | 7,872 |
| trial loop | the test and increment of the trial counter and the bookkeeping of the trial: at most 12 | 12 |
| allocator statistics, rows A, B, E, F, G (per trial, added, e6dcb600) | the flat 64 of the allocator's statistics (4.2) for at most `10^10` allocator calls in the rows that Appendix E does not expand (rows C and D charge it on every allocation and free) | 640,000,000,000 |
| reset after an ABORT (per trial, added) | an aborted trial resets the allocator to its state after init (the two ends of the pool, the 35 free-list heads) | 1,000 |
| plan_invN misses | one per distinct plan size (26 sizes) | 80,314 |
| plan_invN misses, second allowance (added, e6dcb600) | the plans of the lean products differ from Jbenisek's; a second allowance of the row above | 95,759 |
| H | canonical encoding of the output (6 conversions, 384 digits) | 5,644 |
| I | output of the answer: formatting (`400 * 8,192`), loops, entry, one `write`, one `exit_group` | 3,384,436 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + 2 * T_trial + T_off` | **135,731,132,850,836** |

The rows C and D are not asserted by hand: Appendix E expands them from the transform sizes, the Newton levels, the squaring steps and the half-gcd levels with the truncated second call, with the kernel charges of section 4.2, and prints the two values 57,870,590,362,676 and 9,152,091,036,683 (Jbenisek's entry: 57,870,590,362,292 and 31,843,288,956,710).

`N_max = 135,731,132,850,836` operations `= 396,874,657,458.5` units, `log2(N_max / 342) = 38.5298924853`, claimed as `time_log2 = 38.53110` (0.0012 added, then rounded up at five decimals: a margin of `113,652,529,489` operations).

Stage B charges each of the `402,653,184` evaluations of `F` as one reduced permutation, `C(6) = 216 + 21 * 6 = 342` operations, although a line evaluation is a strict subset of the work of a reference permutation; the loop work around the evaluations is charged on top (section 3).

Stage E at its cap. The trial enters stage E only when `1 <= deg G <= DMAX`; stage E opens with 1,000 (stage bookkeeping) and runs a round for each pass of the isolation loop until `deg G = 1` or `Z` rounds have been made. A round at current degree `d` costs `R(d)`: the coin draw 31, the zero test of the shift (5, and at most 2 for the replacement of a zero draw by 1) and one negation; the Taylor shift (`taylor_shift`: two allocations, three loops of `d + 1` steps with their loads, stores and loop control, the schoolbook product of two polynomials of `d + 1` coefficients, two inversions and one exponentiation by `d`); `Z^((p-1)/2) mod G` by schoolbook square-and-multiply (`pow_half`: 253 modular squarings, each `2d + 3 d (d-1)/2 + 2 d^2` field operations and an allocation and a free, and 45 multiplications by `Z`, each `2d` field operations; because the memory-access charge adds 9 operations per field operation, every field operation of `pow_half` is charged 10); two classical gcds (`gcd_cl`: at most `d` outer iterations, each with one inversion charged `2,640` operations (the 330 field operations of `x^(p-2)` and the 2,310 control operations of its bit loop), at most `2d + 1` division steps, each charged at the largest row length); the copies, the tests and the frees. The cap charges every one of the `Z` rounds at `d = DMAX`, because `R(d)` is non-decreasing in `d`: `R(16) = 2,594,979`, of which `pow_half` is 2,471,032, the Taylor shift 11,700 and the two gcds 54,395 each. All allocations are charged at `L <= 16` live blocks (550 per allocation, 105 per free): in stage E the live blocks are the twiddle table, `G`, `S`, `S - 1`, `S + 1` and the two gcd arrays (at most 8), and at most four more inside the Taylor shift or the modular squaring. `E_cap = 1,000 + 3 + 64 * R(16) + 114 = 166,079,773`.

Stage F. After the stage bookkeeping (1,000), 12,000 control operations for the Tonelli-Shanks control and 2 more, the field operations of stage F are charged 10 each (the memory-access charge): the powers by `q` and by `(q+1)/2`, Tonelli-Shanks with parameter `m` falling strictly from 32 (an outer step with parameter `m` costs `m` squarings and 2 multiplications: at most `sum_(m=1)^(32) (m + 2) = 592`), and two back-maps (three fifth-root powers `x^e`, `e = (4(p-1)+1)/5`, two multiplications, two additions, two subtractions each), plus one addition and one subtraction: at most 3,401 field operations, so `F = 13,002 + 10 * 3,401 = 47,012`.

Every figure above is an upper bound that the algorithm meets or exceeds for every coin sequence and every target value (stage D by section 6.3): each loop bound is a constant or a function of `m` only, the trial loop is capped at `K` and tested at the start of each trial, the isolation loop is capped at `Z` rounds of degree at most `DMAX`, and the operations of each stage are counted under the rules of section 4.2.

### 6.1 Ledger recomputation and validation

The sum of section 6 is recomputed by the following script (standard library only).

```python
from math import log2, ceil
K, C = 2, 342
fixed = [536889025, 4910, 80314, 95759, 5644, 3384436]   # init, setup, plan_invN misses (two allowances), stage H, stage I
trial = [1196, 202448159150, 57870590362676, 9152091036683, 166079773, 47012, 7872, 12, 640000000000, 1000]   # stages A, B (with the workspace allowance), C, D, E (cap), F, G, trial loop, allocator statistics, ABORT reset
offline = 1000000
N = sum(fixed) + K * sum(trial) + offline
print('N =', format(N, ','))
print('log2(N/C) =', log2(N / C))
print('time_log2 =', '%.5f' % (ceil((log2(N / C) + 0.0012) * 100000 - 1e-6) / 100000))
```

It prints `N = 135,731,132,850,836`, `log2(N/C) = 38.5298924853` and `time_log2 = 38.53110`. Appendix E prints the same `N_max` from the ledger.

Jbenisek's entry compares the same counting rules with the instrumented totals of its executed entries (algorithmic totals; those runs used the earlier programs, not the stages C and D of this package); the table is reproduced as Jbenisek's validation of the charging rules of 4.2:

| run | counted total | measured total | counted - measured | slack (bits) | counted heap peak | measured heap peak |
|---|---:|---:|---:|---:|---:|---:|
| r = 3, earlier program (fixed centre) | 410,937,818,567 | 409,369,056,359 | 1,568,762,208 | 0.00552 | 244,745,792 | 244,745,792 |
| r = 4, earlier program (fixed centre) | 3,993,660,556,174 | 3,977,289,295,772 | 16,371,260,402 | 0.00593 | 1,072,730,560 | 1,072,730,624 |
| r = 5, earlier program (fixed centre) | 9,217,469,769,975 | 9,171,678,989,504 | 45,790,780,471 | 0.00718 | 4,759,669,952 | 4,759,669,952 |

### 6.2 Offline derivation of the literals (preprocessing)

The algorithm uses constants that are derived from the organizer's constants and from `p` offline: the 192 round constants and 9 MDS entries in Montgomery form, `R^2 mod p`, `R mod p`, `2^65` and `5^q` in Montgomery form, the exponents `q`, `(q+1)/2`, `(p-1)/2`, `p - 2` and the integer `e = (4(p-1)+1)/5`. There is no search and no choice: each literal is the value of one closed formula in the organizer's constants. The Montgomery form of a constant `x` is `x * 2^256 mod p`, one modular multiplication plus parsing 64 hexadecimal digits; `5^q` is a square-and-multiply of 221 squarings and at most 221 multiplications; the exponents are shifts and subtractions of `p`. Each literal costs at most 4,000 word operations, there are at most 250 literals: 1,000,000 operations in all. This bound is inside `N_max` and is the declared `preprocessing_log2 = 20` (`2^20 = 1,048,576 >= 1,000,000`). The algorithm uses no other offline result: the line, its minors and the twiddle table are computed at run time and charged in `setup` and `init`. The leading coefficient `f_D(0)` of section 2.3 is a fact used in the proof; the algorithm re-derives it (stage B tests that the leading coefficient of `g_c` is nonzero and normalises by it).

### 6.3 Stage D: the normal remainder sequence, and the abort (e6dcb600)

The text of this section is e6dcb600's (bradcush), restated for r = 6; it replaces Jbenisek's worst-case charge of stage D for every remainder sequence.

The row D is the charge of the half-gcd of section 4.4 on a normal remainder sequence: every quotient of the Euclidean sequence of `(g, R - 1)` has degree 1, from `deg g = m` down to the gcd. (a) *Lengths.* On such a sequence `d_j = j`, every call `hgcd(a, b, k)` of the recursion has the parameter fixed by the recursion (`k1 = ceil(k/2)`, `k3 = k - k1 - 1`), its first call has `2 k1 + 1` coefficients and its second call at most `2 k3 + 1` (lemma 4.4), the reduced pairs have the lengths `deg a - h` and `deg a - h - 1`, and every matrix of a call with parameter `k` has entries of at most `k + 1` coefficients. Every length of the program is therefore a function of `m` alone, and Appendix E evaluates the charge on these shapes exactly (`gcd_cost(m, 0)`, with the gcd of degree 0). (b) *A gcd of positive degree.* When the gcd has degree `d >= 1` the normal sequence ends at a zero remainder after `m - d` divisions. If `d <= 96` that zero remainder occurs in the classical Euclid of `poly_gcd_own` (every `hgcd` call of the top loop stops at a degree of at least 96, its parameter being at most `(n+1)/2` with `n > 192`), so the program executes a prefix of the calls of the degree-0 case, with the same lengths at every executed call (a call whose second operand is zero, or whose remaining parameter is exhausted, returns at its first test). If `d > 96` the zero remainder may instead be met inside an `hgcd` call of the top loop, which then returns a degree count below its parameter, and the trial ABORTs at the return test of its caller (4.4, step (1): the test fires whether or not the remainder is zero) before any `apply_inv` on operands of other than the normal shapes; such a trial could not have succeeded (`d > DMAX`). In both cases the charge is at most row D. (c) *The tests and the abort.* The quotient test and the return test of 4.4 (2 operations each, charged wherever they execute in Appendix E) are passed by every normal sequence. Consider any other sequence and the first point, in execution order, at which a call whose degree count `h` is still below its parameter `k` finds that the next quotient of its own pair has degree other than 1 (a call with `h = k` stops whatever its next quotient is, as on a normal sequence). If that quotient fits the remaining parameter, the call uses it and the quotient test fails at that division. If it does not fit, the call stops early: the base case breaks out of its loop, a node returns at step (3) after its first call and `apply_inv`, which were executed with normal shapes because every quotient before this point had degree 1; the call returns a degree count below its parameter, and the return test of its caller fails (zero remainder or not, 4.4 step (1)) before the caller does anything with the result; in particular no `apply_inv` is ever executed on operands of other than the normal shapes. In both cases the trial ends having executed only operations that the normal sequence also executes, with the same lengths (lemma 4.4: until that point the truncated calls see the quotients of the whole pair). Hence row D bounds stage D for every input, and the abort affects only the success probability, through the premise `H-NORMAL` (9.2(g), 9.5). (d) *Memory.* The same argument applies to the allocations: an aborted trial executes a prefix of the allocation sequence of the normal one (and then frees its live arrays before the next trial, at most the charge of the frees of the normal sequence), so the arena of section 7, found on the normal sequence, serves every trial. Jbenisek's entry instead charged stage D for every remainder sequence (31,843,288,956,710 operations at this r); this package does not need that bound.

## 7. Memory

Three terms make up the memory.

(a) The code and static data of an implementation of the algorithm: 399,216 bytes of code, 32 of initialised data and 4,851,196 of static tables and buffers (the 8,192-byte output buffer and the tables of the stages), Jbenisek's figure, plus an allowance of 65,536 bytes for the code of the lean stages (at this r the truncated half-gcd with its tests and the abort; e6dcb600's block-mode kernels are not used): 5,315,980 bytes.

(b) The arena, which serves every array of the largest trial (the heap is inside the memory of the implementation; nothing is requested from the system at run time). Each block has a 64-byte header and a payload rounded up to a multiple of 64 bytes (section 4.2). The arena is the capacity of the allocator of 4.2 on the allocation sequence of one trial, found by simulation, not the peak of the live set. Appendix E records every allocation and free of a trial in the order of the program (the twiddle table; stage A: `g`; stage B: the array of the inverse transform and `F`; stage C; stage D) and runs the allocator on it: the two-ended pool takes the blocks of more than `2^18` bytes and is simulated address by address, block by block (two lists in address order, from the two ends; the first free block that fits on the request's side, cut on the side nearest its end; a free merges with its free neighbours and with the unused middle); the slab classes take the other blocks, and their area is the sum over the classes of the peak number of live blocks of the class times the slot. The calls of the half-gcd on fewer than `2^12` coefficients are evaluated once per shape and summarised by their slab-class counts (net and peak), after Appendix E checks that they allocate no pool block; every larger call, and every array of stages A to C, is placed individually. The simulation checks that a trial returns the allocator to its state after init, so the second trial repeats the first; after an ABORT the program resets the allocator to that state (section 6).

Results at r = 6: the high-water mark of the pool (the largest sum of the extents of its two ends) is `31,046,103,616` bytes (after stage A `6,053,733,824`, after stage B `12,496,184,832`, after stage C `31,046,103,232`, after stage D `31,046,103,616`); the peak of the live set is `31,046,103,616` bytes (stage A `6,053,733,824`, B `12,496,184,832`, C `31,046,103,232`, D `31,046,103,616`; in units of `32 m` bytes, one copy of a polynomial of `m` coefficients: 1.5498, 3.1990, 7.9478, 7.9478), so the pool is `1.000000` times the live-set peak. The slab area is `5,242,752` bytes; stages E to I hold at most 16 live arrays of at most 17 elements and the allocator keeps 36 words, `16,896` bytes. The arena is the pool plus 128 bytes (so that the unused middle is always at least 128 bytes), the slab area and those `16,896` bytes, rounded up to 64: `31,051,363,392` bytes.

With the end rules of 4.4 and 4.3 the pool has no hole at the moment of its largest demand. An aborted trial executes a prefix of the allocation sequence of the normal one, so the arena serves it too (6.3 (d)).

(c) A stack bound of 65,536 bytes.

Total: (a) + (b) + (c) = `31,056,744,908` bytes `= 2^34.85419`, which rounds up at three decimals to 34.855; claimed as `memory_log2_bytes = 34.857` (0.002 added: `2^34.857 = 31,117,346,713` bytes, `60,601,805` bytes above the total); Jbenisek's entry 18369013 claims 34.917. The memory penalty is `max(0, 34.857 - 20) = 14.857`. The offline derivation of section 6.2 is a closed formula per constant; its memory is bounded by 1,024 bytes, inside the figure above. The algorithm has no stored advice and no precomputed data beyond the constants of section 6.2; the twiddle table is built at run time and charged in stage "init".

## 8. What is provided

* The algebraic derivation (sections 2-3), the algorithm and its charges (4, 6, 7), the truncation lemma 4.4 with proofs, the premises with the reduction to explicit constants (section 9), the isolation lemma with proof (9.4), and the evidence, labelled as evidence (section 10).
* The claim is the operation count of the algorithm (every trial at its maximum), `memory_log2_bytes` its footprint (the allocator's arena, section 7), and a success probability that follows from the two premises. The cost claim is in the model of section 4.2.
* The ledger of stages C and D with the allocator simulation (Appendix E, this package's program) and the small-size checks of Appendix G.2, standard library only. No certificates (the certificate manifest is empty); the experiments are Jbenisek's five organizer experiments for this target (10.2), unchanged, plus this package's three normality tests (10.5.1, `experiments/exp_normal.py`).

## 9. Success probability and the premise `H-GEOM-w2` and `H-NORMAL`

### 9.1 The premise

Notation. `p` is the Pallas prime, `D = 5^12`, and `F` is the fixed polynomial of section 2.3 at r = 6 (degree `D`, leading coefficient `f_D(0) != 0`). Put
`G(c, t) = (F(c + t) - F(c - t)) / (2 t)` in `F_p[c, t]`, a polynomial of total degree `D - 1` (section 3: `G(c, t) = g_c(t^2)`). For `c` in `F_p` let `k(c)` be the number of nonzero squares `S = t^2` with `G(c, t) = 0`; this is `deg G_c` of section 3. Let `V` be the Zariski closure of `{ (c, s_1, s_2) : G(c, s_1) = G(c, s_2) = 0, s_1^2 != s_2^2 }`.

**Premise `H-GEOM-w2`.** The plane curve `G = 0` has at least one absolutely irreducible component defined over `F_p`, and `V` is a curve (pure dimension 1) with at most `w = 2` absolutely irreducible components defined over `F_p`.

Four fields (as in claim.json). **Statement:** the premise above. **Role:** score-critical. **Scope:** the fixed target `poseidon-orchard-r6-prefix-v1`, this line construction (the line `j = 0` of the first two rounds, section 2), the polynomial `F` of section 2.3; centres uniform on `F_p`. Nothing is claimed for other round counts. **Limitations:** it concerns this `F`, not every polynomial of degree `D`: it is false for permutation polynomials, in particular for every pure composition of maps `x -> a x^5 + b` (`p = 2 mod 5`, so those maps are bijective), and it is not implied by a statement about components over the algebraic closure alone (`F(X) = X^3` over `F_101`: `(F(X) - F(Y)) / (X - Y)` splits into two conjugate lines over `F_(101^2)`, the curve has no off-diagonal rational point, and `k` is zero for every `c`). The explicit constants of 9.2 apply for r <= 7.

What the premise does not contain: no random-polynomial model, no independence of different centres (they are independent because each draw uses distinct fresh random words), no statement about the number of roots beyond the two moments of 9.2.

### 9.2 The reduction to explicit constants, and the success bound

For `c` uniform in `F_p` write `E[.]` for the mean over `c`.

(a) *Squares.* For `t != 0` the values `t` and `-t` give the same `S = t^2` and different points `(c, t)`, so `E[k] = N* / (2p)` with `N* = #{ (c, t) : t != 0, G(c, t) = 0 }`.

(b) *First moment.* Put `d = D - 1`. By the first part of the premise, `G = 0` has an absolutely irreducible component `C_1` defined over `F_p`, of degree at most `d`. Weil's bound for the normalisation of `C_1` (genus at most `(d-1)(d-2)/2`), the count of the singular points of the plane model (at most `(d-1)(d-2)/2`, each with at most `d` branches) and the at most `d` points at infinity give `|#C_1(F_p) - p| <= (d-1)(d-2) sqrt(p) + d (d-1)(d-2)/2 + 2 d + 1`. The points with `t = 0` (at most `d`, since `G(c, 0) = F'(c)` has degree `d`) are inside the term `2d`; further rational components of `G = 0` only add points. Hence `E[k] >= 1/2 - e_1` with `e_1 = ((d-1)(d-2) (2^127 + 1) + d (d-1)(d-2)/2 + 2d + 1) / (2p)` (`sqrt(p) < 2^127 + 1`); `e_1 < 1.752e-22` at r = 6.

(c) *Second moment.* `k(k-1)` counts ordered pairs of distinct usable squares; each pair lifts to 4 points `(s_1, s_2)` by independent signs, and `s_1^2 != s_2^2` is the open condition that defines `V`. So `E[k(k-1)] <= #V(F_p) / (4p)` (the closure only adds points). By the second part of the premise `V` is a curve; it lies in the intersection of the surfaces `G(c, s_1) = 0` and `G(c, s_2) = 0` of degree `d` each. The two surfaces have no common component (a common component would be a factor `h(c)` of `G(c, t)`, but as a polynomial in `c` the leading coefficient of `G` is `D f_D(0)`, independent of `t` and nonzero), so the intersection is a curve of degree `d^2` and `V`, a part of it, has degree at most `delta = d^2` (the two diagonal curves `s_2 = +-s_1` of the intersection are not in `V`, and removing them only lowers the degree). A curve of degree `delta` has geometric genus at most `(delta-1)(delta-2)/2` (project to a plane). For a union of components of total degree `delta`, an absolutely irreducible component defined over `F_p` has at most `p + 1 + (delta_i-1)(delta_i-2) sqrt(p) + (delta_i-1)(delta_i-2)/2` rational points (Weil's bound for its normalisation, plus at most one point per singular point of the plane model), and these terms sum to at most the same expression with `delta` in place of `delta_i`; an `F_p`-component that is not absolutely irreducible has all its rational points on two conjugate components, at most `delta^2` points in all. With at most `w` absolutely irreducible components over `F_p`, `#V(F_p) <= w (p + 1) + (delta-1)(delta-2) sqrt(p) + (delta-1)(delta-2)/2 + delta^2`. Hence `E[k(k-1)] <= w/4 + e_2` with `e_2 = (w + (delta-1)(delta-2) (2^127 + 1) + (delta-1)(delta-2)/2 + delta^2) / (4p)`; `e_2 < 0.00000522` at r = 6.

(d) *Cauchy-Schwarz.* `(E[k])^2 = (E[k 1_(k >= 1)])^2 <= E[k^2] P(k >= 1)` and `E[k^2] = E[k] + E[k(k-1)]`, so `P(k >= 1) >= a^2 / (a + b)` with `a = E[k]` and `b = E[k(k-1)]`. The right side increases in `a` and decreases in `b`, so its minimum over `a >= 1/2 - e_1`, `b <= w/4 + e_2` is at the corner: `P(k >= 1) >= (1/2 - e_1)^2 / (1/2 - e_1 + w/4 + e_2) = 0.2499986949`.

(e) *The cap `DMAX`.* `k >= DMAX + 1` implies `k(k-1) >= (DMAX+1) DMAX = 272`, so by Markov `P(k > DMAX) <= (w/4 + e_2) / 272 = 0.0018382545`. Therefore, for `c` uniform, the event `E_c : 1 <= k(c) <= DMAX` has probability at least `q = 0.2499986949 - 0.0018382545 = 0.2481604405`; the entry uses `q = 0.24816`.

(f) *Centres and isolation.* The algorithm draws its centres `c_1, ..., c_K` from fresh random words by the rule of 4.1.1; each is within statistical distance `eps_coin < 2^-128` of uniform (the exact value is 1.574e-39 (2^-128.90)), and the draws are independent. If `E_(c_t)` holds, the isolation of stage E fails with probability at most `eps_iso = 2.371e-15 (2^-48.58) < 2^-48` over words that are fresh for that stage (lemma 9.4). A trial with `E_(c_t)` and a successful isolation ends in a verified collision (sections 2-5). Therefore

`P[no collision in K trials] <= (1 - q)^K + K (eps_coin + eps_iso)`,

and, given the premise,

`P[success] >= 1 - (1 - q)^K - K (eps_coin + eps_iso) = 0.434736614`, with `q = 0.24816`, `K = 2`, `w = 2` (before the `H-NORMAL` allowance `delta` of (g), which gives the claimed 0.41959).

The probability is over the random words of 4.1.1 for the fixed target. It is not a probability over targets and not a sampled frequency, and no run of this algorithm at r = 6 enters it. The arithmetic of (b)-(f) is recomputed with exact rationals by the script of Appendix D, which prints every number used here. If only `k >= 1` were required (no cap `DMAX`), the same arithmetic would give 0.437498042 for two centres.

(g) *The ABORT of stage D and `H-NORMAL` (e6dcb600's addition).* For a centre `c` let `N_c` be the event that the remainder sequence of `(g_c, R_c - 1)` is normal down to its gcd (every quotient of degree 1, section 6.3); by the premise `H-NORMAL` (9.5), `P(not N_c) <= delta = 0.01` for `c` uniform. If `N_(c_t)` holds, stage D runs without ABORT and returns `G = gcd(g_c, R - 1)`; a trial with `E_(c_t)`, `N_(c_t)` and a successful isolation ends in a verified collision. For `c` uniform `P(E_c and N_c) >= q - delta`, so the bound of (f) becomes `P[success] >= 1 - (1 - q + delta)^K - K (eps_coin + eps_iso) = 0.419599814 >= 0.41959` (`q = 0.24816`, `delta = 0.01`, `K = 2`, computed with exact rationals by this package, Appendix D; with `delta = 0` the bound is 0.434736614, the value of (f)). It stays at least 0.39 for every `delta <= 0.02918`, above the stated `delta = 0.01`.

### 9.3 The parameter w

With the same constants: `w = 1`: `P(k >= 1) >= 0.33333101`, success 0.55432610; `w = 2` (this entry): 0.24999869 and 0.43473728 (the unfloored `q` with `delta = 0`, as Appendix D prints them; the claim uses `q` floored at 5 decimals and `delta = 0.01`, 9.2(g)). The smallest good fraction `q'` (the probability of `E_c`) for which `K` centres give 0.39 is 0.39000 for K=1, 0.21898 for K=2, 0.15191 for K=3 and 0.11625 for K=4 (the terms `K (eps_coin + eps_iso)` are below `10^-14`); with the submitted `K = 2` the good fraction can be smaller than `q` by the factor `0.882` (down to `q' = 0.21898`) before the bound falls below 0.39. The time bound is `T_fixed + K T_trial` with `T_fixed` much smaller than `T_trial`, so `K'` centres instead of `K` cost about `log2(K'/K)` more in `time_log2`.

### 9.4 Lemma (isolation), proved

**Lemma.** Let `G` be monic of degree `d` with `2 <= d <= DMAX`, a product of `d` distinct linear factors over `F_p`. In one round of 4.1.2 (`a` is a coin draw, with 0 replaced by 1), with probability at least `w = (4 (p-3)/2 - S3)/2^256 = 1/2 - 7.869e-40` (`S3` of 4.1.1) both `G_+` and `G_-` are nonconstant, and then the kept part has degree at most `floor(d/2)`. The degree never increases. Hence after `Z` rounds the probability that `deg G >= 2` remains is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1]`, which for `DMAX = 16`, `Z = 64` equals at most 2.371e-15 (2^-48.58) (the exact sum below).

*Proof.* Let `u != v` be two roots of `G`, `chi` the quadratic character on `F_p`. In a round the roots of the shifted `G` are `r + a`. If `a` is not `-u`, not `-v`, and `chi(u+a) != chi(v+a)`, then exactly one of `u+a`, `v+a` is a nonzero square and the other a nonsquare; so `(u+a)^((p-1)/2) = 1` for one and `-1` for the other, one root lies in `G_+` and the other in `G_-` (a root of the shifted `G` is a root of `Z^((p-1)/2) - 1` iff its character is `+1`, of `Z^((p-1)/2) + 1` iff it is `-1`). Both parts are then nonconstant, their degrees sum to at most `d`, and the smaller has degree at most `floor(d/2)`. The number of `a` with `chi(u+a) chi(v+a) = -1`: `sum_(a != -u,-v) chi((a+u)(a+v)) = -1`, because the quadratic `a^2 + (u+v) a + uv` has nonzero discriminant `(u-v)^2` (the standard evaluation of a quadratic character sum), so the count of `a` outside `{-u,-v}` with product `-1` is `((p-2) + 1)/2 = (p-1)/2`, at least `(p-3)/2` of them nonzero. Every residue is taken by the draw with probability `3/2^256` or `4/2^256`, and `4/2^256` for all but `S3` of them (4.1.1), so the `(p-3)/2` nonzero values of `a` listed have together probability at least `(4 (p-3)/2 - S3)/2^256 = w` (a zero draw is replaced by 1, which only adds probability). A part is always a divisor of `G`, so the degree is nonincreasing whatever happens in a round that is not of this kind. Conditional on any history of earlier rounds, the next `a` is made of fresh random words, so every round is of this kind with probability at least `w`, and at most `ceil(log2 DMAX)` such rounds bring `d <= DMAX` to 1 (16 -> 8 -> 4 -> 2 -> 1). The failure probability is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = 2.371e-15 (2^-48.58)`, computed exactly in Appendix D. This is a proved bound under the random words, not a premise and not a sample.

### 9.5 The premise `H-NORMAL` (e6dcb600's premise, restated at r = 6)

**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(g_c, R_c - 1)`, where `g_c` is the monic odd part of section 3 (degree `m = 122,070,312`) and `R_c = S^((p-1)/2) mod g_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.01` (`2^-6.64`).

Four fields (as in claim.json). **Role:** score-critical for the success probability only: the time and memory bounds hold for every sequence, because an abnormal sequence ends the trial at its first abnormal quotient after a prefix of the charged work (6.3). **Scope:** the pairs `(g_c, R_c - 1)` of this target at r = 6, `c` uniform; nothing is claimed for other round counts. **Extrapolation and evidence:** for a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes; each is a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-199`. That bound does not transfer directly, because the coefficients of `R_c` are polynomials of degree about `p` in those of `g_c`; the premise asserts much less than random-pair behaviour: an abnormality probability of at most `delta = 0.01`, which is all the success bound uses (9.2(g): every `delta <= 0.02918` keeps it above 0.39). Measured support, organizer-executed (this package, section 10.5.1): the experiments `euclid-normal-d25-n256`, `euclid-normal-d125-n32` and `euclid-normal-d625-n2` compute in the organizer's sandbox the complete Euclidean remainder sequence of `(g_c, R_c - 1)` for the same construction on the first 4, 5 and 6 rounds of the permutation (degrees 25, 125 and 625; `m = 12`, `62` and `312`) at 256, 32 and 2 fresh centres from the organizer's seeds, and return a witness pair for a trial exactly when its sequence is normal; the prediction is that every computed sequence is normal (our local runs of the same program: 256, 40 and 3 sequences, no quotient of degree other than 1). Reported by Jbenisek's entry (not organizer-executed, section 10.5): the complete sequences on the sibling targets with `r' = 0` and `r' = 1` partial rounds, every quotient of degree 1 in all 10 runs (8 runs of 7,811 steps and 2 of 39,061 steps, 140,610 quotients in all). **Limitations:** not verified at r = 6, which would need the computation itself; a structural reason for a quotient of degree above 1 (an algebraic relation between `g_c` and `R_c` that forces a principal subresultant coefficient to vanish for many centres) would invalidate it, and none is known. The success bound of 9.2 stays at least 0.39 for every `delta <= 0.02918`, above the stated `delta = 0.01`. The organizer-executed tests are at degrees up to 625, far below `m`: they test the construction, not its scale, and the premise at this `r` remains a premise.

## 10. Evidence

This section is the evidence for the premise `H-GEOM-w2` and for the digest of the target. The executions of 10.1, the computations of 10.3 and the runs of 10.5 are reported by Jbenisek's entry 18369013; neither this package nor the organizer executed them, so they motivate the premises without being verified execution evidence. The experiments of 10.2 and 10.5.1 are run by the organizer's runner. None of it enters `success_probability` or the bound of section 9, and none is a lower bound on the probability of `E_c`.

### 10.1 Executed full-scale outcomes at r = 3, 4, 5

| run | degree of F | m | centres tried (in order) | outcome per centre (`deg G`) | successes | operations N (executed) | time_log2 | memory (bytes) | threads, wall |
|---|---:|---:|---|---|---:|---:|---:|---:|---|
| r = 3, earlier program | 5^9 | 976,562 | 1 (fixed) | c=1: 1 | 1 | 317,054,280,703 | 30.08182 | 250,386,180 | 1 thread, 3,202.9 s |
| r = 4, earlier program | 5^10 | 4,882,812 | 1, 2 (fixed) | c=1: 0 (no usable root); c=2: 1 | 1 | 3,992,419,235,666 | 33.63159 | 1,231,371,140 | 6 threads, 13,030.2 s |
| r = 5, earlier program | 5^11 | 24,414,062 | 1 (fixed) | c=1: 1 | 1 | 9,205,778,231,873 | 34.73925 | 5,604,188,884 | 13 threads, 22,048.3 s |

These are the executed entries of the same construction with the centres 1, 2, ... in place of coin draws (their operation counts are the instrumented totals of those runs, thread charges included). Usable roots appeared at three of the four centres tried; each run stops at its first success.

The collisions found (each is a pair of distinct canonical `(nk, rho)` with equal digests at its own round count, accepted by the organizer's digest function when the entry was filed):
* r = 3 (centre 1):
  * nk1  = 0x0499f5c4354bafa11ca451e656d380d078444ed6561d6355487453741e1a6815
  * rho1 = 0x21625d728b86cf0865d7ad7cd99a0c20464939e5253940d95b3a639d7a909af7
  * nk2  = 0x1009050c8c1414cf5975db612457a2e49b06db64fce28c7dd5ad52ed8fc2c567
  * rho2 = 0x31611cd777dc6c418e048d96a497f46fa51523b47dbadcd97d0ad171160fcdb8
  * digest (field element) = 0x325165c946fe20c28af82e940ec89fca03e6fb74afa1a3fa28a54e552a1f12ec, as the organizer's 32 little-endian bytes `ec121f2a554ea528faa3a1af74fbe603ca9fc80e942ef88ac220fe46c9655132`
* r = 4 (centre 2):
  * nk1  = 0x25c10b7d8d36b332b4a4ddb92f1f1a3ffa40259b7b77b0ba458ad0be367ab979
  * rho1 = 0x2e568f6667ceaedd4195dbd24a55c365075306af4a5d0931b1707ba0bf7616ea
  * nk2  = 0x2acbf624301319ca0830c5fda78ae08e00d75798f24adf1320401f1a3bc4c580
  * rho2 = 0x162fa98e63ff13622228cd9e3b4d9039124a918f1f11d12718a2a782ed69fb17
  * digest (field element) = 0x3deca6a0b865e914ebcc74484b3cedb56b9f6293338881693e00cbee0c161fa1, as the organizer's 32 little-endian bytes `a11f160ceecb003e6981883393629f6bb5ed3c4b4874cceb14e965b8a0a6ec3d`
* r = 5 (centre 1):
  * nk1  = 0x35aefd661e07cec063071e6f92f2bbcfd6bbc794bc99be91c008fed0a2a5ebb5
  * rho1 = 0x3dd4caae629bb08efa85dd470f72f2fc183cf026de9cd1aa356e147f058a0090
  * nk2  = 0x242b99e697375e309d54e5db54c215cb6526b420e7ff760eec690a5fb189c764
  * rho2 = 0x2e9a4cf95fce4bbf8ebe8eb72485446ceca86268a6c2305f70d4460179334e37
  * digest (field element) = 0x2425532a0c6af3e7c0864ce59d3b1ddbd62ea79ba594c3305f8fbacf7c184249, as the organizer's 32 little-endian bytes `4942187ccfba8f5f30c394a59ba72ed6db1d3b9de54c86c0e7f36a0c2a532524`

### 10.2 The organizer experiments declared in `experiments/manifest.json`

Five experiments of kind `python-message-pairs-v1`, run by the organizer's own experiment runner (the Orchard digest of the target is called by the runner). The two Python sources are 32,902 bytes together (the limit for experiment sources is 65,536).

(a) `lowbits-birthday` (`experiments/exp_lowbits.py`, kind `python-message-pairs-v1`, event `digest-xor-mask` with mask `fffc` followed by 30 zero bytes and expected value zero). For each organizer trial the program searches at most 1200 fresh inputs derived from the trial seed for two distinct canonical messages whose digests of the selected target `poseidon-orchard-r6-prefix-v1` agree in the first 14 bits of the big-endian reading, and returns the pair (or two nulls). Its source is 15,748 bytes (the limit for experiment sources is 65,536). Its event is a reduced one on the digest of the selected target: the program computes its candidates with its own copy of the permutation (constants embedded), and a returned pair counts only if the organizer's callback gives digests that agree in those 14 bits, so a pair is accepted only when that copy agrees with the target. The digest map so checked is the map whose line polynomial `F` the premise concerns.

The experiment is run by the organizer's own experiment runner (python-message-pairs-v1, the Orchard digest called by the runner), and the intake report of that run, when the organizer executes it, records the observed count; the prediction is 256 of 256 trials (every trial returns a pair). Jbenisek's entry 18369013 reports 256 of 256 trials, from the organizer's run of that entry's package and from a local run of the same events; this package executed nothing.

(b) `line-ladder-w6`, `line-ladder-w8`, `line-ladder-w10`, `line-ladder-w12` (`experiments/exp_line.py`, event `digest-xor-mask` on the first 6, 8, 10 and 12 bits of the digest, expected value zero). The program is the line construction of section 2 for the target at r = 6: it builds the line `j = 0` of the first two rounds (the point `Q`, the direction `(a, b)`, the vectors `alpha` and `beta`), evaluates `F(W)` as the remaining twelve rounds applied to `alpha + beta W` (`deg F = 5^12`), and maps a point `W` back to the canonical pair `(nk, rho)` with the inverse S-box `x -> x^e` of 2.1 and 2.2. For each organizer trial it takes a centre `c` from the trial seed, scans the antipodal pairs `W = c + s`, `W = c - s` for `s = 1, ..., 150`, and at the first pair whose digests agree on the masked bits it maps both points back, checks both messages against the full permutation inside the program and returns them (else two nulls). A returned pair counts only when the runner's own digest of the two canonical messages agrees on those bits, so each counted trial is a pair of antipodal points of the line construction whose digests `F(c+s)` and `F(c-s)` agree at width `w`: the reduced-width form of the event `F(c+s) = F(c-s)` that the premise `H-GEOM-w2` is about (a root of `g_c`). In the picture of the premise, `F(c+s) - F(c-s) = 2 s g_c(s^2)` takes random-function values in `s` at these widths, so a trial returns a pair with probability `1-(1-2^-w)^150`: 0.9058, 0.4441, 0.1363 and 0.0360, that is about 232, 114, 35 and 9 of the 256 trials for `w` = 6, 8, 10, 12. A clustering of the roots of `g_c`, or a bias of the odd structure, would move these counts.

For these four experiments the intake report of the organizer's run of this package, when executed, records the observed counts; the predictions are 232, 114, 35 and 9 of 256. Jbenisek's entry 18369013 reports 235, 120, 27 and 8 of the 256 trials with a verified pair for `w` = 6, 8, 10, 12 respectively, from the organizer's run of that entry's package, with byte-identical output on repetition; those counts fall with the width as the predictions do. This package executed nothing.

### 10.3 Computed theorems and computations for the generic line (Grok, jobs 135 and 136)

Grok (xAI), our research partner, computed the hypothesis of `H-GEOM-w` exactly over the Pallas field for a toy permutation, by exact computation (the cycle types, factorisations and leading coefficients below are the printed results): width 3, S-box `x -> x^5`, `M = [[2,1,1],[1,2,1],[1,1,2]]` (every minor nonzero mod `p`), round `i` adds the constants `(3i+1, 3i+2, 3i+3)`, every round full, output coordinate 0, on the generic line `(L, 2L+1, 3L+5)`. Notation as in 9.1: `D = deg F`, `G(c,t) = (F(c+t) - F(c-t))/(2t) = H(c, t^2)`, `m = (D-1)/2`; the cycle types below are those of `H(c, u)` (or of `F(x) - a`) at the stated values over `F_p`, which by Dedekind give elements of the arithmetic monodromy.

* **Theorem A (one full round).** `D = 5`. The curve `G = 0` is absolutely irreducible (`F'` has 4 simple roots, so `u` is not a square in the function field); the cycle types of `F(x) - a` at `a = 8, 1, 5` are `(5)`, `(4,1)`, `(2,1,1,1)`, so the arithmetic monodromy is `S_5`. The pair scheme `G(c,s1) = G(c,s2) = 0` is geometrically reduced and of pure dimension 1, and its part off `s1^2 = s2^2` has exactly one absolutely irreducible component defined over `F_p`: the resultant in `c` of `G(c,s1)` and `G(c,s2)` is a constant times `(s1-s2)^4 (s1+s2)^4 Phi(s1,s2)` with `Phi` of degree 8, and `Phi` is irreducible at specialisations of `s1` over `F_(p^k)` for `k = 2, 4, 8`, hence absolutely irreducible. So the hypothesis holds with `w = 1`, with no further assumption.
* **Theorem B (two full rounds).** `D = 25`, `deg H = 12`. The cycle types of `H(c,u)` at `c = 1, 9, 103` are `(12)`, `(11,1)`, `(7,1,1,1,1,1)`; a 12-cycle, an 11-cycle and a 7-cycle (7 is prime and at most 12 - 3) give, by Jordan's theorem, `A_12` inside the arithmetic monodromy, and the 12-cycle is odd, so it is `S_12`; the geometric monodromy is `A_12` or `S_12`, both 2-transitive. Hence `G = 0` is absolutely irreducible, the pair scheme is geometrically reduced of pure dimension 1, and the off-diagonal scheme `{H(c,u1) = H(c,u2) = 0, u1 != u2}` in the coordinates `(c, u1, u2)` is absolutely irreducible.
* **Theorem D (degrees).** For every `N <= 17` rounds and every listed line and schedule, the output coordinate has degree exactly `5^N` over `F_p` (the leading coefficient is an integer, nonzero mod `p`). This is the fact of section 2.3 (`deg F = D`) for the toy.
* The axis line `(L, 0, 0)` is a different case (Theorem C): there `F = R(X + c0)^5` is decomposable, its geometric monodromy is imprimitive, and the hypothesis fails (`w = 0`). The theorems above are for the generic line.

Our line is generic in this sense. The polynomial that the construction of section 2 produces is dense: in our miniature runs (`p` of 20 and of 24 bits, `r` up to 4, run twice with identical digests of the coefficient vectors) every coefficient of the digest polynomial in `W` is nonzero up to the 0 to 2 zeros expected of a random polynomial, each residue of the exponent modulo 5 and modulo 25 carries its fair share, and the polynomial `g` that the algorithm builds is dense likewise. This is evidence for `H-GEOM-w2` at one and two rounds on a generic line, with the group-theoretic certificate (an `m`-cycle, an `(m-1)`-cycle and a prime cycle of length at most `m - 3`) that proves it for any further explicit `F` it is computed for.


**Grok job 136 (first N full rounds, Orchard parameter tuple, generic line) and its re-run on the deployed constants.** Grok (xAI) computed the hypothesis of `H-GEOM-w` exactly over the Pallas field for the Orchard tuple (width 3, S-box `x -> x^5`, `R_F = 8`, `R_P = 56`) and the generic line `(L, 2L+1, 3L+5)`, for the first `N = 1, 2, 3, 4` full rounds, with the round constants and MDS produced by the Hadeshash Grain generator and the same group-theoretic certificate as in Theorems A and B (program `certify.py` of job 136, printed in Appendix F). Results: degree exactly `5^N` with a nonzero leading coefficient; `F'` has `5^N - 1` simple roots; (a) `G = 0` is absolutely irreducible and (b) the pair scheme is geometrically reduced of pure dimension 1 at `N = 1, 2, 3, 4`; `w = 1` at `N = 1` (the cofactor `Phi` of degree 8 of the eliminant is absolutely irreducible); at `N = 2` and `N = 3` the arithmetic monodromy of `H` is `S_12` and `S_62` (cycle types `(12)`, `(11,1)`, `(7,1^5)` at `c = 11, 10, 457` and `(62)`, `(61,1)`, `(59,1^3)` at `c = 57, 60, 152`), so the off-diagonal `u`-scheme is absolutely irreducible; at `N = 4` the cycle types `(312)` at `c = 349` and `(311,1)` at `c = 56` give a transitive, 2-transitive monodromy, which gives (a) and (b).

The Grain output differs from the deployed table (the organizer constants that `experiments/exp_line.py` embeds and that the runner's digest uses), so we ran the same program, unchanged, on the deployed constants and on the attack's own line: `F_N` is coordinate 0 after the first `N` S-box layers of the digest polynomial of section 2.3 (start state `alpha + beta W`; layers = rounds 2 and 3, full, then the partial rounds 4 and 5), so `F_N` has degree `5^N` and is the truncation of the polynomial `F` of the premise (`N = 12`; the line and the first layers do not depend on r). The results (`certify_dep.py`, Appendix F):

| N | layers of `F_N` | `deg F_N` | `m` | cycle types of `H(c,u)` found (value of `c`) | (a), (b) | `w` / off-diagonal scheme | monodromy of `H` |
|--:|---|--:|--:|---|:-:|---|---|
| 1 | round 2 | 5 | 2 | (2) at 3, (1,1) at 1 | yes | `w = 1` (`Phi` of degree 8 absolutely irreducible: irreducible of full degree over `F_(p^k)`, `k` = 2, 4, 8) | `S_2` |
| 2 | rounds 2, 3 | 25 | 12 | (12) at 8, (11,1) at 18, (7,1^5) at 1644 | yes | off-diagonal scheme absolutely irreducible | `S_12` |
| 3 | rounds 2, 3, 4 | 125 | 62 | (62) at 82, (61,1) at 24, (59,1^3) at 622 | yes | off-diagonal scheme absolutely irreducible | `S_62` |
| 4 | rounds 2, 3, 4, 5 | 625 | 312 | (312) at 121, (311,1) at 357 | yes | not computed | transitive and 2-transitive |

For every row the spot check of `F_N` against direct iteration of the rounds passed, the leading coefficient of `F_N` equals the one propagated through the layers (section 2.3), `F_N'` has `5^N - 1` simple roots, and `H(c,0) = F_N'(c)` at `c` = 1, 2, 5, 17. The cycle types are those of the square-free specialisations of `H(c,u)` at the stated `c`; for `N = 1` the discriminant of `H` is not a square (odd-exponent factors of degrees 2 and 2), and for `N = 4` the Jordan prime cycle `(307,1^5)` was not met in 929 specialisations (expected count 0.025), so the single-component statement is not made at `N = 4`.

So (a) and (b) hold for `F_N` at `N = 1, 2, 3, 4` on the deployed constants and the attack line, `w = 1` at `N = 1`, and the monodromy of `H` is `S_m` at `N = 2` and `N = 3`. The premise `H-GEOM-w2` states `w <= 2` at `N = 12`; this is the measured trend of the premise, and it is our theory that the trend continues to `N = 12`.
Under (a) and 2-transitivity of the monodromy of H, w is 1 or 2 (Grok job 137, lemma: with the arithmetic monodromy Gamma inside the hyperoctahedral group B_m, K = Gamma meet F_2^m is one of 0, <1>, E, F_2^m once pi(Gamma) contains A_m, and w = 1 exactly when K contains the even-weight subspace E, w = 2 otherwise; the witnesses of Grok job 136 establish the hypotheses). Measured on the deployed Orchard constants and the attack's own line (the F_N of proof.md 10.3, using the Frobenius cycle types of H(c, u) and their lifts to G(c, t) = H(c, t^2) over F_p): N = 1 gives K = F_2^2 and w = 1; N = 2 (m = 12) gives K = F_2^12 and w = 1, witnessed by the 12-cycle specialisations c = 8 (two 12-cycles on G, omega = 0) and c = 24 (one 24-cycle, omega = 1) and the even permutation c = 6; N = 3 (m = 62) gives K = F_2^62 and w = 1, witnessed by the 62-cycle specialisations c = 82 (omega = 0) and c = 102 (omega = 1) and the even permutation c = 1. So w = 1 at N = 1, 2, 3 on the deployed constants, a measured trend, and the premise states w <= 2 at N = 12, which the lemma bounds by 2 given (a) and 2-transitivity.

### 10.4 Scope

One trial at r = 6 needs about 31 GB of memory (section 7) and about 6.8e+13 operations (section 6). The claim is the premise `H-GEOM-w2` with the reduction of section 9.2; the executed centres at r = 3, 4, 5, the experiments of 10.2, the theorems and computations of 10.3 and the measurements of 10.5 are the evidence for it.
### 10.5 Euclidean sequences on the sibling targets

The algorithm of section 4 at `r = 6` applies the Euclidean algorithm to `g_c` (degree `m = 122,070,312`) and `R - 1`, `R = S^((p-1)/2) mod g_c`. This section is the measured support of the premise `H-NORMAL` (9.5): stage D is charged for the normal remainder sequence, and a trial ABORTs at the first quotient of degree other than 1 (6.3). The digest polynomial of the same family at `r' = 0` and `r' = 1` partial rounds (same constants, same line `j = 0`, `F` of degree `5^6 = 15,625` and `5^7 = 78,125`, `m = 7,812` and `39,062`) is small enough to run the stage in full with `python-flint`: for each centre `c` we built `F(c + x)`, its odd part `g_c`, `R` by powering and the complete Euclidean sequence of `(g_c, R - 1)`. Results (`sib_euclid.py`, centres `c` = 1, ..., 8 at `r' = 0` and `c` = 1, 2 at `r' = 1`): every quotient had degree 1 in all 10 runs, the sequences ended at degree 0 after `m - 1` steps (7,811 and 39,061 steps; no run had a quotient of degree other than 1), and at `r' = 0` the gcd had degree 1 (a usable root, a collision of the sibling target) at the centres 2, 4 and 7. Each `r' = 0` run takes about 20 s and each `r' = 1` run about 6 minutes on one core. The program `sib_euclid.py` is printed in Appendix F.

At `r = 6` the stages need about 31 GB and 1.4e+14 operations, which the organizer sandbox (128 MiB, 20 s) does not host; the counts at this `r` are the formula counts of sections 6 and 7, and `H-NORMAL` at this `r` is a premise.

### 10.5.1 Organizer-executed normality tests (this package)

Three experiments of kind `python-message-pairs-v1`, declared in `experiments/manifest.json` and run by the organizer's runner (program `experiments/exp_normal.py`, 22,310 bytes; the three sources together are 55,212 bytes, under the 65,536 limit). For each organizer trial the program takes a centre `c` from the trial seed, builds symbolically the digest polynomial `F_k(W)` of the first `4 + k` rounds of the selected permutation on the attack's line (full rounds 0-3 and partial rounds `4..3+k`, coordinate 0; the same constants, MDS and line `j = 0` as section 2, with no final full rounds so that the degree `5^(2+k)` stays small), its monic odd part `g_c` about `c` (degree `m = (5^(2+k) - 1)/2`), `R_c = x^((p-1)/2) mod g_c` and the complete Euclidean remainder sequence of `(g_c, R_c - 1)`, all exactly over `F_p` with the standard library (products by Kronecker substitution, a Newton inverse and Barrett reduction). The sequence is normal when every quotient has degree 1 down to the gcd (4.4, 6.3). When it is normal the program returns two distinct canonical messages of the selected target whose digests agree on the declared 6-bit mask, found by a short search of the points `c + s` on the line (the witness that the trial was computed and found normal); when a quotient of degree other than 1 occurs it returns two nulls. The mask event is the witness channel; the measurement is the normality check, whose counts (`steps`, `abnormal_quotients`, `gcd_degree`) the program reports as observations, which the runner labels untrusted. The experiment id fixes the degree and the number of leading trials computed (the sandbox allows 20 s for the 256 trials of an experiment): `euclid-normal-d25-n256` (`k = 0`, degree 25, `m = 12`, all 256 trials), `euclid-normal-d125-n32` (`k = 1`, degree 125, `m = 62`, trials 0-31) and `euclid-normal-d625-n2` (`k = 2`, degree 625, `m = 312`, trials 0-1); the remaining trials return two nulls, so the predicted counts of returned pairs are 256, 32 and 2 of 256. Prediction: every computed sequence is normal. Our local runs of the same program (a Python 3.12 container with one CPU and 128 MiB, seeds of our own): 256, 40 and 3 sequences at `m = 12`, `62` and `312`, no quotient of degree other than 1, in 6.0, 9.1 and 7.3 seconds; the gcd had positive degree in 91, 20 and 2 of them (a usable root of `g_c`, as `E[k]` about `1/2` in 9.2 predicts), and every returned pair was checked against the organizer's reference digest. What these tests show: under trusted execution, the construction's pairs `(g_c, R_c - 1)` have normal remainder sequences at degrees 12 to 312. What they do not show: anything at degree `m = 122,070,312`, where `H-NORMAL` (9.5) remains a premise, now asserting only `delta = 0.01`. The sibling-target runs of 10.5 at `m = 7,812` and `39,062` are Jbenisek's reported computations (entry 18369013), not executed here or by the organizer.

## 11. Appendix D: the premise arithmetic (`premise_numbers.py`)

`python3 premise_numbers.py` recomputes with exact rationals every number of section 9.2 and 9.3.

#### premise_numbers.py

```python
#!/usr/bin/env python3
"""Exact-rational recomputation of the success bound of proof.md section 9 for r = 6 (standard library only; prints every number used).
Premise H-GEOM-w gives E[k] >= 1/2 - e1 and E[k(k-1)] <= w/4 + e2 (Weil's bound with the plane genus bound; section 9.2).
Cauchy-Schwarz: P(k >= 1) >= E[k]^2 / (E[k] + E[k(k-1)]).  Markov on k(k-1): P(k >= DMAX+1) <= E[k(k-1)] / ((DMAX+1) DMAX).
q = P(1 <= k <= DMAX) >= the difference; K independent centres: 1 - (1-q)^K - K (eps_coin + eps_iso).
The entry uses q floored at 5 decimals (9.2(e)); with the ABORT of stage D and the H-NORMAL allowance delta = 0.01 (9.2(g), 9.5)
the claimed bound is 1 - (1-q+delta)^K - K (eps_coin + eps_iso)."""
import math
from fractions import Fraction as Fr
from math import comb
P = (1 << 254) + 0x224698FC094CF91B992D30ED00000001
SP = 1 << 127                                   # floor(sqrt(P)) = 2^127, (2^127 + 1)^2 > P
R, DMAX, ZCAP = 6, 16, 64
DELTA = Fr(1, 100)   # the H-NORMAL abnormality allowance (section 9.5); the Bezout degree below is the lower-case delta of 9.2(c)
D = 5 ** (6 + R); d = D - 1
# first moment: |N - P| <= (d-1)(d-2) sqrt(P) + d (d-1)(d-2)/2 + 2d + 1 for the plane curve G = 0 (degree d); E[k] = N*/(2P)
e1 = Fr((d - 1) * (d - 2) * (SP + 1) + d * (d - 1) * (d - 2) // 2 + 2 * d + 1, 2 * P)
# pair curve V: Bezout degree delta = d^2; N_V <= w (P+1) + (delta-1)(delta-2) sqrt(P) + (delta-1)(delta-2)/2 + delta^2; E[k(k-1)] = N_V / (4P)
delta = d * d
# pair curve V: Bezout degree delta = d^2; N_V <= w (P+1) + (delta-1)(delta-2) sqrt(P) + (delta-1)(delta-2)/2 + delta^2; E[k(k-1)] = N_V / (4P)
delta = d * d
def e2_of(w): return Fr(w + (delta - 1) * (delta - 2) * (SP + 1) + (delta - 1) * (delta - 2) // 2 + delta * delta, 4 * P)
# coins: a draw is x = w mod P for one uniform 256-bit word w. 2^256 = 3 P + RES with 0 < RES < P: the residues below RES have 4 preimages, the other S3 = P - RES = 4 P - 2^256 have 3.
# statistical distance of x from uniform: eps_coin = S3 (1/P - 3/2^256).
# isolation lemma: a round is good (both parts nonconstant) when the shift a lies in a set of (P-1)/2 residues, at least (P-3)/2 of them nonzero; a is the draw x with 0 replaced by 1,
# every residue has at least 3 preimages and all but S3 residues have 4, so P[a in good] >= (4 (P-3)/2 - S3) / 2^256
RES = (1 << 256) - 3 * P
S3 = P - RES
assert 0 < RES < P and S3 == 4 * P - (1 << 256)
wq = Fr(4 * ((P - 3) // 2) - S3, 1 << 256)
eps_iso = sum(comb(ZCAP, j) * wq ** j * (1 - wq) ** (ZCAP - j) for j in range(0, 4))
eps_coin = S3 * (Fr(1, P) - Fr(3, 1 << 256))
def bound(w, K):
    e2 = e2_of(w)
    a = Fr(1, 2) - e1
    b = Fr(w, 4) + e2
    q_cs = a * a / (a + b)
    tail = b / ((DMAX + 1) * DMAX)
    q = q_cs - tail
    q5 = Fr(int(q * 100000), 100000)                             # the value the entry uses in the success formula: q floored at 5 decimals (9.2(e))
    succ_exact = 1 - (1 - q) ** K - K * (eps_coin + eps_iso)     # unfloored q, delta = 0 (the figures of 9.3)
    succ0 = 1 - (1 - q5) ** K - K * (eps_coin + eps_iso)         # floored q, delta = 0 (9.2(f))
    succ = 1 - (1 - q5 + DELTA) ** K - K * (eps_coin + eps_iso)  # with the H-NORMAL abnormality allowance delta (9.2(g), 9.5): the claimed bound
    return dict(e2=e2, b=b, q_cs=q_cs, tail=tail, q=q, q5=q5, succ=succ, succ0=succ0, succ_exact=succ_exact, succ_notail=1 - (1 - q_cs) ** K)
def f(x, n=12): return '%.*f' % (n, float(x))
if __name__ == '__main__':
    W, K = 2, 2
    B = bound(W, K)
    print('D = 5^%d = %d, d = D - 1' % (6 + R, D))
    print('e1 < %.3e' % float(e1)); print('e2 < %s' % f(B['e2'], 10))
    print('E[k] >= 1/2 - e1; E[k(k-1)] <= w/4 + e2 = %s  (w = %d)' % (f(B['b'], 10), W))
    print('Cauchy-Schwarz: P(k >= 1) >= %s' % f(B['q_cs'], 10))
    print('Markov tail:    P(k > %d)  <= %s' % (DMAX, f(B['tail'], 10)))
    print('q = P(1 <= k <= %d) >= %s' % (DMAX, f(B['q'], 10)))
    print('K = %d without the tail (P(k >= 1) only): %s' % (K, f(B['succ_notail'], 10)))
    print('per-round good probability w >= %s = 1/2 - %.3e' % (f(wq, 20), float(Fr(1, 2) - wq)))
    print('eps_iso < %.3e (2^%.2f)   eps_coin < %.3e (2^%.2f)' % (float(eps_iso), math.log2(float(eps_iso)), float(eps_coin), math.log2(float(eps_coin))))
    print('q used in the success formula (q floored at 5 decimals, 9.2(e)): %s' % f(B['q5'], 5))
    print('success with delta = 0 >= 1 - (1-q)^%d - %d (eps_coin + eps_iso) = %s   (%s with the unfloored q)' % (K, K, f(B['succ0'], 12), f(B['succ_exact'], 12)))
    print('success >= 1 - (1-q+delta)^%d - %d (eps_coin + eps_iso) = %s   (delta = %s, H-NORMAL)' % (K, K, f(B['succ'], 12), f(DELTA, 4)))
    print('claimed success_probability: %s (floor at 5 decimals)' % ('%.5f' % (int(B['succ'] * 100000) / 100000)))
    for w in (1, 2, 3):
        Bw = bound(w, 2)
        print('w = %d: P(k>=1) >= %s, q >= %s, K=2 success %s, K=3 success %s   (unfloored q, delta = 0)' % (w, f(Bw['q_cs'], 8), f(Bw['q'], 8), f(Bw['succ_exact'], 8), f(bound(w, 3)['succ_exact'], 8)))
```

## 12. Appendix E: the stage C and stage D ledger and the allocator (`cd_ledger.py`, this package)

`cd_ledger.py` is this package's program (standard library only). It is a re-implementation, written from the printed text of e6dcb600's ledger (read, not run), of the charging rules of e6dcb600 (bradcush; proof.md 4.2-4.5 and Appendix E there), which extend Jbenisek's ledger: the transform kernels and pass charges, the cyclic products, the block products (schemes (a) and (c)), the outer-transform charges (`ontt`, with the kernel charges counted from e6dcb600's kernel text), stage C (`powx_lean`) and the half-gcd on the normal sequence (`hgcd`, `gcd_cost`). Its additions are the workspace rule (`ACAP`), the scheme (a) case of the squaring step, the end rules of 4.4 and 4.5, the recording of every allocation and free in program order and the allocator simulation (`simulate`). Validation: `python3 cd_ledger.py check21` reproduces the totals that e6dcb600 asserts at r = 21 with its chunk bounds: `S_C = 4,062,062,219,504,740,890,363,177`, `S_D = 1,360,756,098,766,545,569,709,103` and the four stage peaks (`119,209,289,619,500,726,912`, `238,418,579,240,595,258,048`, `632,939,936,390,951,625,792`, `577,946,978,315,814,447,872` bytes); at r = 6, 7 and 8, where stage C is unchanged, it gives Jbenisek's row C plus 384 (the statistics charge on three allocations and three frees) and Jbenisek's stage C peaks.

The run for this r (the call below, which traces the allocation sequence, and the untraced ledger, which must give the same `S_C` and `S_D`) uses no block-product parameters (chunk bounds `{}`, workspace caps `{}`: at this r every product fits one cyclic transform, 4.3) and the pool threshold `2^18` bytes. It gives `S_C = 57,870,590,362,676`, `S_D = 9,152,091,036,683` and the allocator figures of section 7, in about 30 s.

The call that produces the figures of sections 6 and 7 at this r (in the folder of `cd_ledger.py`):

```python
import cd_ledger as L
res = L.run(6, cf={}, acap={}, trace=True, big_exp=18, lcut_shift=1)
plain = L.run(6, cf={}, acap={})            # the untraced ledger: the same S_C and S_D
assert (res['S_C'], res['S_D']) == (plain['S_C'], plain['S_D']) == (57870590362676, 9152091036683)
```

#### cd_ledger.py

```python
#!/usr/bin/env python3
"""Ledger of stages C and D for the Orchard Poseidon algebraic collision algorithm (Jbenisek's algorithm), with the lean stage C/D
of bradcush's r = 21 entry e6dcb600 (truncated second half-gcd call, chunked outer-transform products with blocks of HB = 2^31 and a
one-row 2^32-point block transform, the lean squaring step, the normal remainder sequence with the abort test), evaluated at any r.

This is a re-implementation, written for this package from the printed text of e6dcb600's ledger (read, not run), of the charging rules stated in e6dcb600 (proof.md 4.2-4.5, 6.3,
Appendix E there), which in turn extend the ledger of Jbenisek's f62fb39.  It is validated by reproducing every total that e6dcb600
asserts at r = 21 (S_C, S_D, the four stage peaks), see check_r21().  New here: every allocation and free is recorded in program order
and the allocator of section 7 (a two-ended first-fit pool for large blocks, slab classes for the others, the design of Jbenisek's
r = 8..20 entries) is simulated on that sequence, so the arena is an allocator capacity, not the peak of the live set.

Placement (this package; no operation count depends on it): every allocation statement has an end of the pool (stage C: a constant; stage D: derived
from the result end `ys` passed to hgcd, proof.md 4.4), and the remainder of a division is written over its dividend when the dividend's array has
exactly its length (the allocation and free this saves stay charged).  The workspace rule ACAP excludes scheme (a) for a product kind when its
workspace exceeds the cap; when q g of the squaring step is in scheme (a) the wrap of the square is not added (lemma 4.5 without reduction).

Exact integer arithmetic throughout; standard library only.
Usage: python3 cd_ledger.py check21      (reproduce e6dcb600's r = 21 totals)
       or call run(r, cf, acap, trace=True, big_exp=..., lcut_shift=1) as in proof.md Appendix E.
"""
import math
import sys

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
PM2, PM1H = P - 2, (P - 1) >> 1
INV_CTL, STAGE_BK, CACHE = 2310, 1000, 64


def powcost(e):
    """square-and-multiply cost of x^e on one element: squarings + multiplications"""
    return (e.bit_length() - 1) + (bin(e).count('1') - 1) if e > 0 else 0


# radix-2 pass kernels of a transform (section 4.2): for k = 1..4 layers, (c0, a, b): charge c0 + a G + b G S
PASS = {
    'f': ((4, 17, 19), (4, 35, 43), (4, 80, 96), (4, 185, 213)),
    'i': ((4, 17, 21), (4, 36, 47), (4, 82, 102), (4, 188, 221)),
    'usq': ((3, 18, 0), (3, 49, 0), (3, 128, 0), (3, 315, 0)),
    'umul': ((4, 23, 0), (4, 58, 0), (4, 145, 0), (4, 348, 0)),
}
# radix-3 position kernels: K3[type][pattern of nonzero rows][rotation]
K3 = {
    'f': [(6, 6, 6), (8, 14, 14), (14, 8, 14), (19, 19, 25), (14, 14, 8), (19, 25, 19), (25, 19, 19), (24, 24, 24)],
    'i': [None, (10, 16, 16), (16, 10, 16), (20, 20, 26), (16, 16, 10), (20, 26, 20), (26, 20, 20), (24, 24, 24)],
    'r0': [(2, 2, 2), (4, 4, 4), (4, 4, 4), (7, 7, 7), (4, 4, 4), (7, 7, 7), (7, 7, 7), (10, 10, 10)],
    'r1': [(2, 2, 2), (4, 7, 7), (7, 4, 7), (10, 10, 13), (7, 7, 4), (10, 13, 10), (13, 10, 10), (16, 16, 16)],
    'r2': [(2, 2, 2), (4, 7, 7), (7, 4, 7), (10, 10, 13), (7, 7, 4), (10, 13, 10), (13, 10, 10), (16, 16, 16)],
}
ROT = ((0, 0, 0), (0, 1, 2), (0, 2, 1))


def pass_fwd(a, l0, k):
    c0, p, q = PASS['f'][k - 1]
    g = 1 << l0
    return 5 + (9 * k + 2) + 4 + c0 + p * g + q * g * ((1 << (a - l0 - k)) - 1)


def pass_inv(a, l0, k):
    c0, p, q = PASS['i'][k - 1]
    g = 1 << l0
    return 6 + (9 * k + 2) + 4 + c0 + p * g + q * g * ((1 << (a - l0 - k)) - 1)


def pass_fused(a, k, mode):
    c0, p, q = PASS['usq' if mode == 'sq' else 'umul'][k - 1]
    return 6 + (9 * k + 2) + 6 + c0 + p * (1 << (a - k))


FREE_OPS = 105
ALLOC_STAT = 64                    # the allocator's flat statistics charge, on every allocation and every free


def blk(slots):
    """bytes of a block of `slots` field elements: 64-byte header + payload rounded up to 64"""
    return 64 + ((slots * 32 + 63) & ~63)


# ---------------------------------------------------------------- the walk: operation count, live set, and (when tracing) the event log
class Slot(int):
    """an array, represented by its number of slots; `sid` identifies a large block in the event log"""
    pass


TAGS = {}
POLICY = {}            # allocation statement (tag) -> end of the pool: 0 low, 1 high, 'p0'/'p1' alternate with the depth of the half-gcd recursion
DEPTH = [0]


def side_of(tag, default):
    v = POLICY.get(tag, default)
    if v == 'p0': return DEPTH[0] & 1
    if v == 'p1': return 1 - (DEPTH[0] & 1)
    return v
TRACE = {'log': None, 'depth': 0, 'big': None, 'sid': 0}   # log: events in program order; depth > 0 inside a summarised (cached) call;
                                                           # big: blocks of more than `big` bytes are pool blocks (identity kept)


def slab_class(nbytes):
    return max(7, (nbytes - 1).bit_length())


class Tr:
    __slots__ = ('ops', 'cur', 'peak', 'cnt', 'pcnt', 'base', 'live', 'ccur', 'cpk')

    def __init__(self, base=0):
        self.ops = 0; self.cur = 0; self.peak = 0; self.cnt = 0; self.pcnt = 0; self.base = base
        self.live = TRACE['log'] is not None and TRACE['depth'] == 0
        self.ccur = {}; self.cpk = {}

    def here(self):
        return self.base + self.cnt

    def ctl(self, n): self.ops += n
    def ld(self, n): self.ops += 2 * n
    def st(self, n): self.ops += 2 * n
    def loopc(self, n): self.ops += 3 * n + 2

    def _cls_add(self, c, d):
        v = self.ccur.get(c, 0) + d
        self.ccur[c] = v
        if v > self.cpk.get(c, 0): self.cpk[c] = v

    def add(self, o):
        self.ops += o.ops
        self.peak = max(self.peak, self.cur + o.peak); self.pcnt = max(self.pcnt, self.cnt + o.pcnt)
        self.cur += o.cur; self.cnt += o.cnt
        if TRACE['log'] is not None and not o.live:
            if self.live:
                TRACE['log'].append(('S', dict(o.ccur), dict(o.cpk)))
            else:
                for c in set(o.ccur) | set(o.cpk):
                    pk = self.ccur.get(c, 0) + o.cpk.get(c, 0)
                    if pk > self.cpk.get(c, 0): self.cpk[c] = pk
                    self.ccur[c] = self.ccur.get(c, 0) + o.ccur.get(c, 0)

    def new_fp(self, slots, side=0, tag=None):
        slots = max(slots, 1) if slots else 1
        if tag is not None: side = side_of(tag, side)
        self.ops += 1 + 120 + 13 * (2 * (self.base + self.cnt) + 1) + ALLOC_STAT
        b = blk(slots); self.cur += b; self.cnt += 1
        self.peak = max(self.peak, self.cur); self.pcnt = max(self.pcnt, self.cnt)
        s = Slot(slots)
        if TRACE['log'] is not None:
            if b > TRACE['big']:
                assert self.live, 'a pool block inside a summarised call'
                TRACE['sid'] += 1; s.sid = TRACE['sid']
                TRACE['log'].append(('A', s.sid, b, side)); TAGS[s.sid] = tag
            elif self.live:
                TRACE['log'].append(('a', slab_class(b)))
            else:
                self._cls_add(slab_class(b), 1)
        return s

    def charge_alloc_free(self):
        """the charge of an allocation and a free that the program replaces by writing in place (kept, so the count is an upper bound)"""
        self.ops += 1 + 120 + 13 * (2 * (self.base + self.cnt) + 1) + ALLOC_STAT + FREE_OPS + ALLOC_STAT

    def free(self, slots):
        self.ops += FREE_OPS + ALLOC_STAT
        b = blk(slots); self.cur -= b; self.cnt -= 1
        if TRACE['log'] is not None:
            if b > TRACE['big']:
                assert self.live and hasattr(slots, 'sid'), 'a pool block freed without identity'
                TRACE['log'].append(('F', slots.sid))
            elif self.live:
                TRACE['log'].append(('f', slab_class(b)))
            else:
                self._cls_add(slab_class(b), -1)


# ---------------------------------------------------------------- transform plans and the cyclic products (below the block length)
class Plan:
    def __init__(self, rows, a):
        self.rows = rows; self.a = a; self.n = 1 << a; self.N = 3 * self.n if rows == 3 else self.n
        self.c0 = (1 if a & 1 else 2) if rows == 3 else 0
        self.np = (a + 3) >> 2
        kk = [0] * self.np; rem = a
        for i in range(self.np - 1, -1, -1):
            k = min(4, rem); kk[i] = k; rem -= k
        self.kk = kk


def plan_invN_ops(Pl):
    return 7 * CACHE


def udivmod_cost(a, b):
    nb = a.bit_length(); q = a // b
    return 4 * nb + 2 + 10 * nb + 2 * bin(q).count('1') + 4


def for8(n):
    return 1 + 3 * (n // 8) + 2 + 3 * (n % 8) + 2


def make_plan(rows, a):
    p = Plan(rows, a)
    return p, 18 + 4 + (3 * p.np + 2) + 4 * p.np + 2 + (4 if rows == 3 else 0)


BIGA = 32                               # transforms of 3 * 2^a points exist in F_p for a <= 32 only
P32 = make_plan(1, BIGA)[0]             # the block transform: one row of 2^32 points
NB = P32.N; HB = NB // 2


def plan3_for_len(ln):
    c = 0
    for a in range(2, 64):
        c += 8
        if 3 * (1 << a) >= ln:
            p, cc = make_plan(3, a)
            return p, c + cc
    raise ValueError(ln)


def split_regions(n, N, boff, lenB):
    c = 3; bp = [0]; nt0 = 0
    for t in range(3):
        st = nt0 + N - boff
        if st >= N: st -= N
        nt0 += n; c += 9
        c += 3
        if st < lenB:
            x = lenB - st; c += 4
            if 0 < x < n: bp.append(x); c += 1
        c += 3
        if st > 0:
            x = N - st; c += 4
            if 0 < x < n: bp.append(x); c += 1
            x = N + lenB - st; c += 5
            if 0 < x < n: bp.append(x); c += 1
    c += 2
    bp.append(n); c += 1
    cnt = len(bp)
    for a in range(1, cnt):                      # insertion sort, charged per step
        key = bp[a]; b = a - 1; c += 5
        while b >= 0 and bp[b] > key:
            bp[b + 1] = bp[b]; b -= 1; c += 6
        c += 3
        bp[b + 1] = key
    c += 2
    out = []; pats = []
    for a in range(cnt - 1):
        c += 6
        if bp[a + 1] > bp[a]:
            lo = bp[a]; p = 0; nt1 = 0
            for t in range(3):
                idx = lo + nt1 + N - boff
                if idx >= N: idx -= N
                p |= (1 if idx < lenB else 0) << t; nt1 += n; c += 13
            c += 5
            out.append(lo); pats.append(p); c += 2
    c += 2
    out.append(n); c += 1
    return out, pats, c


def driver(typ, pat, c0, lo, hi):
    K = [K3[typ][pat][r] for r in ROT[c0]]
    i = lo
    c = udivmod_cost(lo, 3); ph = lo % 3; c += 1
    c += 2
    if ph == 1:
        c += 2
        if i < hi:
            c += K[1]; i += 1; c += 1
            c += 2
            if i < hi:
                c += K[2]; i += 1; c += 1
    else:
        c += 2
        if ph == 2:
            c += 2
            if i < hi:
                c += K[2]; i += 1; c += 1
    nt = 0; c += 2
    if hi > i:
        nt = (hi - i) // 3; c += udivmod_cost(hi - i, 3); c += 2
    c += nt * (K[0] + K[1] + K[2] + 4)
    i += 3 * nt
    c += 4
    if hi > i:
        rem = hi - i; c += 1
        c += K[0]; i += 1; c += 1
        c += 2
        if rem == 2:
            c += K[1]
    return c


def stageA_fwd(Pl, ln):
    c = 4; n = Pl.n
    if Pl.rows == 1:                      # the one-row block transform: copy ln coefficients (load + store each), zero the rest (a store each)
        assert Pl.a > BIGA - 1 and ln <= n
        return c + for8(ln) + 4 * ln + for8(n - ln) + 2 * (n - ln) + 2
    bp, pat, cc = split_regions(n, Pl.N, 0, ln); c += cc + 2
    for q in range(len(pat)):
        c += 4 + driver('f', pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def stageA_inv(Pl, outlen):
    if Pl.rows == 1:
        return 0
    c = 2
    bp, pat, cc = split_regions(Pl.n, Pl.N, 0, outlen); c += cc + 2
    for q in range(len(pat)):
        c += 2
        if pat[q] == 0:
            c += 3; continue
        c += 4 + driver('i', pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def stageA_row(Pl, r, lenB, boff):
    bp, pat, c = split_regions(Pl.n, Pl.N, boff, lenB)
    c += 2
    for q in range(len(pat)):
        c += 3 * 11 + 2 + 4 + driver('r%d' % r, pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def fwd_passes(Pl, cnt):
    l0 = 0; c = 0
    for p in range(cnt):
        c += pass_fwd(Pl.a, l0, Pl.kk[p]) + 4; l0 += Pl.kk[p]
    return c


def inv_passes(Pl, first):
    l0 = sum(Pl.kk[:first + 1]); c = 0
    for p in range(first, -1, -1):
        l0 -= Pl.kk[p]
        c += pass_inv(Pl.a, l0, Pl.kk[p]) + 4
    return c


def fused(Pl, mode):
    return pass_fused(Pl.a, Pl.kk[-1], mode)


def conv_core_row(Pl, mode):
    return 9 + fwd_passes(Pl, Pl.np - 1) + 4 + fused(Pl, mode) + inv_passes(Pl, Pl.np - 2) + 4


def conv_sq(Pl, ln, outlen):
    assert Pl.a <= BIGA
    c = stageA_fwd(Pl, ln) + Pl.rows * conv_core_row(Pl, 'sq') + 2
    return c + stageA_inv(Pl, outlen)


def mulc_otf_row(Pl, r, lenB, boff):
    c = 12 + stageA_row(Pl, r, lenB, boff)
    c += fwd_passes(Pl, Pl.np) + 2
    c += fwd_passes(Pl, Pl.np - 1) + fused(Pl, 'mul') + inv_passes(Pl, Pl.np - 2) + 4
    return c


def conv_mulc_otf(Pl, ln, lenB, boff, outlen, sub=False):
    if Pl.a > BIGA:
        return conv_mulc_big(ln, lenB, (Pl.N - boff) % Pl.N, outlen, sub)
    c = 2 + stageA_fwd(Pl, ln) + 4
    for r in range(3):
        c += mulc_otf_row(Pl, r, lenB, boff)
    return c + 2 + stageA_inv(Pl, outlen)


def pw_loop(n, mode):
    return for8(n) + n * (7 if mode == 0 else 10)


def _eps(nout, groups):
    eps = [0] * nout
    for g in groups:
        for s in range(len(g['S'])):
            for h in range(len(g['H'])):
                o, sg = g['prod'].get((s, h), (-1, 0))
                if o >= 0 and not eps[o]:
                    eps[o] = sg
    return eps


def conv_bilin_cost(Pl, nout, outlen, groups):
    """a bilinear form (several products summed into nout outputs) on one cyclic transform, rows processed one at a time"""
    if Pl.a > BIGA:
        return conv_bilin_big(nout, outlen, groups)
    c = 2 + 2 + 3 * nout
    eps = _eps(nout, groups)
    for g in groups:
        c += 6 * len(g['S']) * len(g['H'])
    for r in range(3):
        c += 2 + 2 + nout + 1
        done = [0] * nout
        for g in groups:
            c += 7
            for lh in g['H']:
                c += 6 + stageA_row(Pl, r, lh, 0) + fwd_passes(Pl, Pl.np)
            for s, ls in enumerate(g['S']):
                c += 6 + stageA_row(Pl, r, ls, 0) + fwd_passes(Pl, Pl.np)
                for h in range(len(g['H'])):
                    c += 8
                    o, sg = g['prod'].get((s, h), (-1, 0))
                    if o < 0: continue
                    if not done[o]:
                        done[o] = 1; c += pw_loop(Pl.n, 0)
                    elif sg == eps[o]:
                        c += pw_loop(Pl.n, 1)
                    else:
                        c += pw_loop(Pl.n, 2)
        for k in range(nout):
            c += 3
            if eps[k]:
                c += inv_passes(Pl, Pl.np - 1)
    for k in range(nout):
        c += 3
        if eps[k]:
            c += stageA_inv(Pl, outlen[k])
    return c, eps


# ---------------------------------------------------------------- block products (section 4.5): blocks of HB = 2^31, block transform of NB = 2^32 points
_BF = {}


def big_fwd(bl):                        # forward block transform of a block of bl coefficients, zero-padded to NB
    if bl not in _BF:
        _BF[bl] = stageA_fwd(P32, bl) + P32.rows * fwd_passes(P32, P32.np)
    return _BF[bl]


def big_inv(outn):                      # inverse block transform (the factor NB is removed by the placement)
    return P32.rows * inv_passes(P32, P32.np - 1) + stageA_inv(P32, outn)


def big_pw(mode):                       # one pointwise pass over NB points: 0 write, 1 add, 2 subtract
    return P32.rows * pw_loop(P32.n, mode)


def nblk(l): return -(-l // HB)


def big_fwd_all(l):
    k = nblk(l)
    return (k - 1) * big_fwd(HB) + big_fwd(l - (k - 1) * HB)


def big_place(cnt, ov, sub):
    c = 3 * cnt + 2 + 2 * cnt + cnt + 2 * cnt
    return c + (cnt if sub else ov) * 3


# outer-transform kernels (e6dcb600, Appendix E: ob3, ob2f/ob4f/ob8f, ob2i/ob4i/ob8i), charge c0 + c1 * cnt counted from their text:
# ob3: call 10, two constant loads 4, loop exit 2; per position 3 loads (6), 8 field operations, 3 stores (6), loop step 3.
# ob(2^k): call 10, (2^k - 1) twiddle loads, loop exit 2; per position 2^k loads, k 2^(k-1) butterflies of 3 operations, 2^k stores, loop step 3.
def _kch(k):
    if k == 0:
        return 10 + 4 + 2, 6 + 8 + 6 + 3
    w = 1 << k
    return 10 + 2 * (w - 1) + 2, 2 * w + 3 * k * (w // 2) + 2 * w + 3


KCH = {'ob3': _kch(0)}
for _k in (1, 2, 3):
    KCH['ob%df' % (1 << _k)] = KCH['ob%di' % (1 << _k)] = _kch(_k)
assert KCH['ob3'] == (16, 23) and KCH['ob2f'] == (14, 14) and KCH['ob4f'] == (18, 31) and KCH['ob8f'] == (26, 71)
ADR_CTL, TWI_CTL = 4, 3


def outer_plan(n):
    r3 = n % 3 == 0; M = n // 3 if r3 else n
    a = M.bit_length() - 1
    assert (1 << a) == M, n
    return r3, M, ([a % 3] if a % 3 else []) + [3] * (a // 3)


def ontt(n, cnt, inv=False):
    """charge of the outer transform of n points at cnt positions (twiddle table 6n + 2, Good-Thomas radix-3 stage, passes of <= 3 layers)"""
    r3, M, ks = outer_plan(n)
    c = 6 * n + 2
    nrows = 3 if r3 else 1
    if r3:
        k0, k1 = KCH['ob3']
        c += 10 + 3 * M + 2 + M * (3 * ADR_CTL + k0 + k1 * cnt)
    c += 3 * nrows + 2
    per_row = 3 * len(ks) + 2; Ns = M
    for k in ks:
        h = Ns >> k; nb = M // Ns
        k0, k1 = KCH[('ob%d' % (1 << k)) + ('i' if inv else 'f')]
        per_row += 3 * nb + 2 + nb * (3 * h + 2) + nb * h * ((1 << k) * ADR_CTL + ((1 << k) - 1) * TWI_CTL + k0 + k1 * cnt)
        Ns >>= k
    return c + nrows * per_row


def pad23(n):
    best = None
    for a in range(0, 33):
        for c in (1, 3):
            v = c << a
            if v >= n and (best is None or v < best): best = v
    assert best is not None, n
    return best


CTX = {'cf': None, 'ltrue': None, 'cyc': None, 'acap': None}
ACAP = {}
PL = {}
CF = {}


def nc_for(n2, cf):
    nc = 1
    while cf is not None and (n2 // nc) * HB > cf and (n2 // nc) % 2 == 0: nc *= 2
    return nc


def segs(ws, ln):
    e = ws + ln
    if ln <= 0: return []
    q = min(e, (ws // HB + 1) * HB)
    if q == e: return [(ln, 1)]
    out = [(q - ws, 1)]
    full = (e - q) // HB; rest = e - q - full * HB
    if full: out.append((HB, full))
    if rest: out.append((rest, 1))
    return out


def fold_ops(l, n3, tw):
    """twist and fold an operand of l coefficients into its chunk array of n3 rows of HB"""
    kx = nblk(l); last = l - (kx - 1) * HB
    wr = 4 + tw; ac = 7 + tw
    first = min(kx, n3); acc = kx - first; zero_rows = max(0, n3 - kx)
    c = 0
    if kx <= n3:
        c += (first - 1) * (10 + for8(HB) + wr * HB) + 10 + for8(last) + wr * last + for8(HB - last) + 2 * (HB - last)
    else:
        c += first * (10 + for8(HB) + wr * HB) + (acc - 1) * (10 + for8(HB) + ac * HB) + 10 + for8(last) + ac * last
    c += zero_rows * (10 + for8(HB) + 2 * HB)
    return c + 3 * (kx + zero_rows) + 2


def acc_ops(ws, ln, first, sub):
    per = 5 if (first and not sub) else 8
    return sum(c * (10 + for8(x) + per * x + 3) for x, c in segs(ws, ln)) + 2


FOLD_ROW = 8 * HB + for8(HB) + 4


def _gp(n, kb):
    if n <= 0: return 0
    return n * (n + 1) // 2 if n <= kb else kb * (kb + 1) // 2 + (n - kb) * kb


def pairs_upto(ka, kb, s):
    if s < 0: return 0
    return _gp(s + 1, kb) - _gp(s + 1 - ka, kb)


def pairs_range(ka, kb, A, B):
    return pairs_upto(ka, kb, B) - pairs_upto(ka, kb, A - 1)


def window_slots(ws, outlen):
    we = ws + outlen
    s0 = max(0, (ws + 1) // HB - 3)
    while (s0 + 2) * HB - 1 <= ws: s0 += 1
    s1 = -(-we // HB) + 2
    while s1 * HB >= we: s1 -= 1
    return s0, s1, we


def slot_cost(s, s0, ws, we, sub):
    lo, hi = s * HB, (s + 2) * HB - 1
    outn = min(NB - 1, we - lo); cnt = min(hi, we) - max(lo, ws)
    ov = 0
    if s > s0: ov = max(0, min((s + 1) * HB - 1, we) - max(s * HB, ws))
    return big_inv(outn) + big_place(cnt, ov, sub)


ROOTS = 6 * (330 + INV_CTL)
MODE_LOG = {}


def conv_bilin_big(nout, outlen, groups, ws=0, sub=False, shared=False):
    """a block product (bilinear form): scheme (a) (slots) or scheme (c) (chunked outer product modulo Y^n2 - 1), whichever is cheaper"""
    eps = _eps(nout, groups)
    prods = [[] for _ in range(nout)]
    for g in groups:
        for (si, hi_), (o, sg) in g['prod'].items():
            if o >= 0: prods[o].append((g['S'][si], g['H'][hi_]))
    ops_ = []
    for g in groups:
        ops_ += list(g['H'])
        if not shared: ops_ += list(g['S'])
    pw0, pw1 = big_pw(0), big_pw(1)
    # scheme (a)
    ca = 2 + sum(big_fwd_all(l) for l in ops_)
    live = []
    for k in range(nout):
        if not eps[k] or not prods[k]: continue
        live.append(k)
        s0, s1, we = window_slots(ws, outlen[k])
        stot = max(nblk(ls) + nblk(lh) - 1 for ls, lh in prods[k])
        A, B = s0, min(s1, stot - 1)
        if B < A: continue
        npr = sum(pairs_range(nblk(ls), nblk(lh), A, B) for ls, lh in prods[k])
        cnt_s = B - A + 1
        ca += cnt_s * (pw0 - pw1) + pw1 * npr
        edges = sorted(set(range(A, min(A + 3, B + 1))) | set(range(max(B - 2, A), B + 1)))
        for s in edges: ca += slot_cost(s, s0, ws, we, sub)
        mid = cnt_s - len(edges)
        if mid > 0:
            ca += mid * slot_cost(edges[2] + 1, s0, ws, we, sub)
    temps_a = [nblk(l) * NB for l in ops_] + [NB]
    # scheme (c)
    need = 0
    lt = CTX['ltrue']
    for k in live:
        if CTX['cyc']:
            need = max(need, CTX['cyc'])
        else:
            L = lt[k] if lt else max(ls + lh - 1 for ls, lh in prods[k])
            need = max(need, ws + outlen[k], L - ws)
    n2 = pad23(-(-need // HB)); nc = nc_for(n2, CTX['cf']); n3 = n2 // nc
    mops = [l for l in ops_ if nblk(l) > 1]; singles = [l for l in ops_ if nblk(l) == 1]
    co = 2 + ROOTS + sum(big_fwd(l) for l in singles) + 3 * nc + 2
    for j_first, mult in ((True, 1), (False, nc - 1)):
        if not mult: continue
        cj = 6 + sum(fold_ops(l, n3, 0 if j_first else 1) for l in mops) + len(mops) * ontt(n3, HB) + n3 * (8 + len(mops) * big_fwd(HB))
        for k in live:
            cj += n3 * (pw0 + (len(prods[k]) - 1) * pw1 + big_inv(NB - 1) + FOLD_ROW) + ontt(n3, HB, True) + acc_ops(ws, outlen[k], j_first, sub)
        co += mult * cj
    temps_c = [n3 * HB] * max(len(mops), len(live)) + [NB] * (len(ops_) + len(live)) + [n3]
    use_c = co <= ca
    if CTX.get('acap') is not None and sum(temps_a) > CTX['acap']:
        use_c = True                       # the workspace rule (this package): scheme (a) only when its workspace fits under the cap
    PL.clear()
    PL.update(mode='c' if use_c else 'a', n2=n2 if use_c else 0, nc=nc if use_c else 0, temps=temps_c if use_c else temps_a, ca=ca, co=co)
    MODE_LOG[PL['mode']] = MODE_LOG.get(PL['mode'], 0) + 1
    return (co if use_c else ca), eps


def conv_mulc_big(ln, lenB, ws, outlen, sub=False):
    return conv_bilin_big(1, [outlen], [dict(H=[lenB], S=[ln], prod={(0, 0): (0, 1)})], ws, sub, False)[0] + 6


def product_peak(T, Pl):
    """the temporary arrays of the product just evaluated, allocated at its start and freed at its end"""
    arr = PL['temps'] if Pl.a > BIGA else [Pl.n]
    ids = [T.new_fp(x, 1, 'tmpN') for x in arr]
    for x in ids: T.free(x)


# ---------------------------------------------------------------- stage C: S^((p-1)/2) mod g (section 4.5 of e6dcb600: the lean step)
def ebit(E, i): return (E >> i) & 1


def step_walk(base, m, Psq, Pq, Pg, Fcur):
    """the arrays of one squaring step: Fn and T1 receive S^bit R^2, R (the array F) is freed, q gets its own array, T1 is freed, q g is
    subtracted from Fn, q is freed; Fn is the new F.  Returns the trace and the new F."""
    S = Tr(base)
    sT1 = S.new_fp(m, 1, 'T1'); sFn = S.new_fp(m + 1, 0, 'Fn')               # T1 and the temporaries from the high end of the pool, F, Fn and q from the low end
    for x in [S.new_fp(y, 1, 'tmpC') for y in Psq['temps']]: S.free(x)
    S.free(Fcur)
    sq = S.new_fp(m, 0, 'qC')
    for x in [S.new_fp(y, 1, 'tmpC') for y in Pq['temps']]: S.free(x)
    S.free(sT1)
    for x in [S.new_fp(y, 1, 'tmpC') for y in Pg['temps']]: S.free(x)
    S.free(sq)
    assert S.cur == 0 and S.cnt == 0
    return S, sFn


def powx_lean(m, b, Fslot, E=PM1H):
    T = Tr(b)
    PN, c1 = plan3_for_len(2 * m - 1); PNp, c2 = plan3_for_len(m + 1)
    T.ctl(c1 + c2)
    N, Np = PN.N, PNp.N
    BIG = PN.a > BIGA
    if BIG:
        assert PNp.a > BIGA
        sM = T.new_fp(m, 1, 'MU'); sY = T.new_fp(m, 0, 'Y')          # MU from the high end for the whole of stage C
        L = m
        CTX['cf'] = CF.get('newton'); CTX['acap'] = ACAP.get('newton')
    else:
        sY = T.new_fp(N, 0, 'Yc'); sT = T.new_fp(PN.n, 0, 'Tc'); sM = T.new_fp(m - 1, 0, 'MUc')
        L = m - 1
    # Newton iteration for the reciprocal
    T.ld(L); T.st(L); T.loopc(L); T.ctl(L)
    T.ctl(4 + 8); T.st(1)
    l = 1
    while l < L:
        l2 = min(2 * l, L)
        T.ctl(8)
        P1, c = plan3_for_len(l2 + l - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P1, l, l2, 0, l2))
        if BIG:
            assert P1.a > BIGA or P1.N <= m - 1
            product_peak(T, P1)
        T.ctl(plan_invN_ops(P1))
        T.ops += l2 - l
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        P2, c = plan3_for_len(l2 - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P2, l2 - l, l, 0, l2 - l))
        if BIG:
            assert P2.a > BIGA or P2.N <= m - 1
            product_peak(T, P2)
        T.ctl(plan_invN_ops(P2))
        T.ops += 2 * (l2 - l)
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        l = l2
    CTX['cf'] = None; CTX['acap'] = None
    T.ld(L); T.st(L); T.loopc(L // 2); T.ctl(2 * (L // 2))
    T.ctl(plan_invN_ops(PN)); T.ctl(plan_invN_ops(PNp)); T.ops += 1
    T.ops += L; T.ld(L); T.st(L); T.loopc(L)
    gamma = N - (m - 2)
    info = {}
    if BIG:
        CTX['cf'] = CF.get('sq'); CTX['acap'] = ACAP.get('sq')
        sq_ops = conv_bilin_big(1, [2 * m - 1], [dict(H=[m], S=[m], prod={(0, 0): (0, 1)})], 0, False, True)[0] + 4; Psq = dict(PL)
        CTX['cf'] = CF.get('q'); CTX['acap'] = ACAP.get('q')
        q_ops = conv_bilin_big(1, [m], [dict(H=[m], S=[m], prod={(0, 0): (0, 1)})], m - 1)[0] + 6; Pq = dict(PL)
        CTX['cf'] = CF.get('qg'); CTX['acap'] = ACAP.get('qg'); CTX['cyc'] = m + 1
        qg_ops = conv_bilin_big(1, [m], [dict(H=[m + 1], S=[m], prod={(0, 0): (0, 1)})], 0, True)[0] + 6; Pg = dict(PL)
        CTX['cf'] = None; CTX['cyc'] = None; CTX['acap'] = None
        # e6dcb600 has every step product in scheme (c) at r = 21.  At smaller r scheme (a) can be cheaper; the square and the quotient are
        # exact windows in either scheme, and q g in scheme (a) is the exact linear product: then A - q g has degree < m (lemma 4.5 with no
        # cyclic reduction), Fn = A[0..m) - (q g)[0..m) and no wrap of A is added (nf = 0).
        T.free(sY)
        Nq = Pg['n2'] * HB if Pg['mode'] == 'c' else None
        nf = max(0, 2 * m - Nq) if Nq is not None else 0
        fold_F = for8(nf) + 7 * nf + 10
        info['prods'] = {'sq': (Psq['mode'], Psq['n2'], Psq['nc'], sq_ops), 'q': (Pq['mode'], Pq['n2'], Pq['nc'], q_ops), 'qg': (Pg['mode'], Pg['n2'], Pg['nc'], qg_ops)}
    info['peakN'] = T.peak
    top = 255
    while top > 0 and not ebit(E, top):
        top -= 1; T.ctl(12)
    v = 1; bit = top
    while bit >= 1 and ((v << 1) | ebit(E, bit - 1)) < m:
        v = (v << 1) | ebit(E, bit - 1); bit -= 1; T.ctl(25)
    T.st(m); T.loopc(m)
    T.ctl(plan_invN_ops(PN)); T.st(1)
    steps = bit
    lim = (2 * m - 2 - Np + 1) if 2 * m - 2 >= Np else 0
    lim = min(lim, m)
    Fnow = Fslot
    if BIG:
        S, Fnow = step_walk(T.here(), m, Psq, Pq, Pg, Fnow)
        step = sq_ops + 8 + 4 + fold_F + q_ops + qg_ops + S.ops
        if TRACE['log'] is not None:          # the event log: every step allocates and frees its arrays (identical charges)
            for _ in range(steps - 1):
                _, Fnow = step_walk(T.here(), m, Psq, Pq, Pg, Fnow)
    else:
        step = conv_sq(PN, m, 2 * m - 1) + 8
        step += for8(lim) + 7 * lim + for8(m - lim) + 4 * (m - lim) + for8(m - 1) + 4 * (m - 1)
        step += conv_mulc_otf(PN, m - 1, m - 1, gamma, m - 1) + conv_mulc_otf(PNp, m - 1, m + 1, 0, m)
        step += for8(m) + 7 * m
    step += 14 + 6
    nset = sum(ebit(E, i) for i in range(bit))
    mulx = 0 if BIG else 2 + for8(m - 1) + 8 * (m - 1) + 2 + 4
    T.ops += steps * step + nset * mulx
    if BIG:
        T.peak = max(T.peak, T.cur + S.peak); T.pcnt = max(T.pcnt, T.cnt + S.pcnt)
        info['peakS'] = T.cur + S.peak
    T.ops += 1 + m; T.ld(m); T.st(m); T.loopc(m)
    T.ctl(2 + 500)
    if BIG:
        T.free(sM)
    else:
        T.free(sY); T.free(sT); T.free(sM)
    info.update(steps=steps, nset=nset, step=step, mulx=mulx, BIG=BIG, F=Fnow)
    return T, info


# ---------------------------------------------------------------- stage D: the half-gcd (section 4.4 of e6dcb600), the normal remainder sequence
ABORT_TEST = 2


def dupv(ln, b):
    T = Tr(b); s = T.new_fp(ln if ln else 1, 0, 'dup')
    T.ld(ln); T.st(ln); T.loopc(ln)
    return T, s


def trim(it): return 11 * it


def divrem_naive(lx, ly, term_zero=0):
    c = 3
    la, lb = lx, ly
    assert la == lb + 1
    if lb >= 2:
        c += powcost(PM2) + INV_CTL + 3 + 1
        c += 2 * 3 + 2 * 2 + 6
        c += 2 * (lb - 1) + 2 * max(lb - 2, 0)
        c += 4 * (lb - 1) + 2 * (lb - 1) + 3 * (lb - 1) + 2 + 4 + 2 * (lb - 1)
        it = 1 + term_zero * (lb - 1)
        c += trim(it)
        return c, 2, lb - 1 - term_zero * (lb - 1), it
    c += 2 * la + 2 * la + 3 * la + 2
    c += powcost(PM2) + INV_CTL
    c += (la - lb + 1) * (1 + 2 + 2 + 2 + 7)
    c += trim(1)
    return c, la - lb + 1, 0, 1


def mat_identity(b):
    T = Tr(b); sl = [T.new_fp(1, 0, 'id') for _ in range(4)]
    T.st(2)
    return T, [1, 0, 0, 1], sl


def mat_free(T, sl):
    for s in sl:
        if s: T.free(s)


def mul_add_q2(T, le, lf, side=0):
    lt = le + 1 if le else 0
    lo = max(lt, lf)
    s = T.new_fp(lo if lo else 1, side, 'maq')
    muls = le + max(le - 1, 0) + (1 if le > 0 else 0)
    adds = max(le - 1, 0) + (min(lf, le + 1) if le > 0 else 0)
    T.ops += muls + adds
    T.ld(le + lf); T.st(lo); T.loopc(lo); T.ctl(8 + 8 * lo)
    T.ctl(trim(1))
    return lo, s


def mat_mulQ(T, lens, sl, side=0):
    l0, s0 = mul_add_q2(T, lens[0], lens[1], side)
    l2, s2 = mul_add_q2(T, lens[2], lens[3], side)
    T.free(sl[1]); T.free(sl[3])
    return [l0, lens[0], l2, lens[2]], [s0, sl[0], s2, sl[2]]


def poly_mul_naive_cost(la, lb):
    return la * lb * 11 + (la * lb - (la + lb - 1)) + (la + lb - 1) * 11 + 2


def mat_mul(A, B, b, side=0):
    T = Tr(b); T.ctl(80)
    Al, Bl = A[0], B[0]
    Ls = [0] * 4
    for i in range(2):
        for j in range(2):
            l = 0
            for t in range(2):
                la, lb = Al[2 * i + t], Bl[2 * t + j]
                if la and lb and la + lb - 1 > l: l = la + lb - 1
            Ls[2 * i + j] = l
    Lmax = max(1, max(Ls))
    outl = [0] * 4; outs = [0] * 4
    if Lmax <= 48:
        for i in range(2):
            for j in range(2):
                l = Ls[2 * i + j]
                o = T.new_fp(l if l else 1)
                T.st(l); T.loopc(l)
                for t in range(2):
                    la, lb = Al[2 * i + t], Bl[2 * t + j]
                    if not la or not lb: continue
                    tmp = T.new_fp(la + lb - 1)
                    T.ops += poly_mul_naive_cost(la, lb)
                    T.ops += la + lb - 1
                    T.ld(2 * (la + lb - 1)); T.st(la + lb - 1); T.loopc(la + lb - 1)
                    T.free(tmp); T.ctl(6)
                T.ctl(trim(1))
                outl[2 * i + j] = l; outs[2 * i + j] = o
        return T, outl, outs, False
    Pl, c = plan3_for_len(Lmax); T.ctl(c)
    BIG = Pl.a > BIGA
    N = Pl.N
    if not BIG:
        ob = [T.new_fp(N, 1 - side, 'mm_ob') for _ in range(4)]               # work buffers on the end of the factors, then the row buffers (freed first)
        tH0 = T.new_fp(Pl.n, 1 - side, 'mm_tmp'); tH1 = T.new_fp(Pl.n, 1 - side, 'mm_tmp'); tS = T.new_fp(Pl.n, 1 - side, 'mm_tmp')
    groups = []
    for t in range(2):
        g = dict(H=[], S=[], prod={}); hj = [-1, -1]
        for j in range(2):
            if Bl[2 * t + j]:
                hj[j] = len(g['H']); g['H'].append(Bl[2 * t + j])
        for i in range(2):
            if Al[2 * i + t]:
                s = len(g['S']); g['S'].append(Al[2 * i + t])
                for j in range(2):
                    if hj[j] >= 0: g['prod'][(s, hj[j])] = (2 * i + j, 1)
        if g['H'] and g['S']: groups.append(g)
        T.ctl(20)
    CTX['cf'] = CF.get('D') if BIG else None
    CTX['acap'] = ACAP.get('D') if BIG else None
    cc, eps = conv_bilin_cost(Pl, 4, Ls, groups); T.ctl(cc)
    CTX['cf'] = None; CTX['acap'] = None
    if BIG:
        Pd = dict(PL)
        ob = [T.new_fp(Ls[k] if Ls[k] else 1, side, 'mm_out') for k in range(4)]
        for x in [T.new_fp(y, side, 'mm_tmp') for y in Pd['temps']]: T.free(x)
        for M_ in (A, B):
            for s_ in M_[1]:
                if s_: T.free(s_)
    else:
        T.free(tH0); T.free(tH1); T.free(tS)
    T.ctl(plan_invN_ops(Pl))
    for k in range(4):
        l = Ls[k]
        if BIG:
            T.ctl(3)
            if not eps[k]: T.st(l); T.loopc(l)
            outs[k] = ob[k]
            if l: T.ctl(trim(1))
            outl[k] = l
            continue
        o = T.new_fp(l if l else 1, side, 'mm_out'); T.ctl(3)
        if eps[k]:
            T.ops += l; T.ld(l); T.st(l); T.loopc(l)
        T.free(ob[k])
        outs[k] = o
        if l: T.ctl(trim(1))
        outl[k] = l
    return T, outl, outs, BIG


def fslots(m):
    return m + 1 if plan3_for_len(2 * m - 1)[0].a > BIGA else m


def apply_inv(Rl, Rs, h, la, lb, consume, b, side=0):
    T = Tr(b)
    nres = la
    Pl, c = plan3_for_len(nres); T.ctl(c)
    N = Pl.N
    BIG = Pl.a > BIGA
    if BIG:
        lc0 = la - h; ld0 = lc0 - 1
        sd_ = T.new_fp(ld0, side, 'ai_out'); sc_ = T.new_fp(lc0, side, 'ai_out')     # d first: c is freed first
    else:
        sd_ = T.new_fp(N, side, 'ai_out'); sc_ = T.new_fp(N, side, 'ai_out')       # outputs first, then the two row buffers (freed first)
        tH = T.new_fp(Pl.n, side, 'ai_tmp'); tS = T.new_fp(Pl.n, side, 'ai_tmp')
    sgn = -1 if (h & 1) else 1
    T.ctl(60)
    ec = [3, 1]; ed = [2, 0]; sc = [sgn, -sgn]; sd = [-sgn, sgn]
    lV = [la, lb]
    groups = []
    for v in range(2):
        g = dict(H=[lV[v]], S=[], prod={})
        if not lV[v]: continue
        if Rl[ec[v]]:
            g['prod'][(len(g['S']), 0)] = (0, sc[v]); g['S'].append(Rl[ec[v]])
        if Rl[ed[v]]:
            g['prod'][(len(g['S']), 0)] = (1, sd[v]); g['S'].append(Rl[ed[v]])
        if g['S']: groups.append(g)
        T.ctl(10)
    if BIG:
        CTX['ltrue'] = [lc0, ld0]; CTX['cf'] = CF.get('D')
        CTX['acap'] = ACAP.get('D')
    cc, eps = conv_bilin_cost(Pl, 2, [lc0, ld0] if BIG else [nres, nres], groups); T.ctl(cc)
    CTX['ltrue'] = None; CTX['cf'] = None; CTX['acap'] = None
    if BIG:
        Pa = dict(PL)
        for x in [T.new_fp(y, side, 'ai_tmp') for y in Pa['temps']]: T.free(x)
        if consume: mat_free(T, Rs)
    else:
        T.free(tH); T.free(tS)
        if consume: mat_free(T, Rs)
    T.ctl(plan_invN_ops(Pl))
    for k in range(2):
        T.ctl(3)
        if not eps[k]:
            T.st(nres); T.loopc(nres); continue
        if BIG: continue
        if eps[k] < 0: T.ops += 1
        T.ops += nres; T.ld(nres); T.st(nres); T.loopc(nres)
    lc = la - h; ld = lc - 1
    T.ctl(trim(1) + trim(1) if BIG else trim(1 + (nres - lc)) + trim(1 + (nres - ld)))
    return T, lc, sc_, ld, sd_


HCACHE = {}
GSIDE = [0]
INPLACE_NB = [False, False]     # also write the remainder over a longer (transform-length) dividend array: [in the half-gcd, in the outer driver]
LCUT = [None]          # when tracing: calls with la > LCUT run live (their events go to the log), the others are cached and summarised


def hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b, ys=0):
    if TRACE['log'] is not None and TRACE['depth'] == 0 and la > LCUT[0]:
        return _hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b, ys)
    key = (la, int(sa), lb, int(sb), k, want_mat, own, wc, wd, b)
    r = HCACHE.get(key)
    if r is None:
        TRACE['depth'] += 1
        try:
            r = _hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b, ys)
        finally:
            TRACE['depth'] -= 1
        HCACHE[key] = r
    return r


def _hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b, ys=0):
    DEPTH[0] += 1
    try:
        return _hgcd_body(la, sa, lb, sb, k, want_mat, own, wc, wd, b, ys)
    finally:
        DEPTH[0] -= 1


def _hgcd_body(la, sa, lb, sb, k, want_mat, own, wc, wd, b, ys):
    """returns (Tr, (lc, sc, ld, sd, Rl, Rs, h)).  ys: the end of the pool for the results.  A call that returns a pair (and no matrix) owns its
    inputs, which lie on ys: its first call returns R1 on ys, its own arrays go to the other end, the final pair to ys.  A call that returns a
    matrix keeps its arrays and its matrix on ys and has its two calls return their matrices on the other end."""
    pairnode = (wc or wd) and not want_mat
    own_side = 1 - ys if pairnode else ys
    T = Tr(b); T.ctl(40)
    n = la - 1
    Rl = Rs = None
    if lb == 0 or n - (lb - 1) > k:
        if want_mat:
            t, Rl, Rs = mat_identity(T.here()); T.add(t)
        T.ctl(4)
        lc = sc = ld = sd = None
        if wc:
            if own & 1: sc = sa
            else:
                t, sc = dupv(la, T.here()); T.add(t)
            lc = la
        elif own & 1: T.free(sa)
        if wd:
            if own & 2: sd = sb
            else:
                t, sd = dupv(lb, T.here()); T.add(t)
            ld = lb
        elif own & 2: T.free(sb)
        return T, (lc, sc, ld, sd, Rl, Rs, 0)
    if k <= 96:
        return hgcd_base(la, sa, lb, sb, k, want_mat, own, wc, wd, T)
    k1 = (k + 1) >> 1
    if k1 + k1 > n: k1 = n >> 1
    s = n - 2 * k1
    las = la - s; lbs = lb - s if lb > s else 0
    t1, o1 = hgcd(las, 0, lbs, 0, k1, 1, 0, False, False, T.here(), ys if pairnode else 1 - ys)
    T.add(t1)
    R1l, R1s, h1 = o1[4], o1[5], o1[6]
    T.ctl(ABORT_TEST)
    assert h1 >= 1, 'non-generic shape'
    t2, lcc, scc, ldd, sdd = apply_inv(R1l, R1s, h1, la, lb, not want_mat, T.here(), own_side)
    T.add(t2); T.ctl(4)
    if own & 1: T.free(sa)
    if own & 2: T.free(sb)
    sumdeg = n - (lcc - 1); k2 = k - sumdeg
    if ldd == 0 or (lcc - ldd) > k2:
        if want_mat: Rl, Rs = R1l, R1s
        lc = sc = ld = sd = None
        if wc: lc, sc = lcc, scc
        else: T.free(scc)
        if wd: ld, sd = ldd, sdd
        else: T.free(sdd)
        return T, (lc, sc, ld, sd, Rl, Rs, h1)
    dq = lcc - ldd
    sq = T.new_fp(dq + 1, own_side, 'div_q')
    inplace = int(scc) == lcc or (INPLACE_NB[0] and int(scc) > lcc)
    if inplace:
        srm = scc; T.charge_alloc_free()  # the remainder c - q d is written over c (dead after the division); the allocation and free it replaces stay charged
    else:
        srm = T.new_fp(lcc, own_side, 'div_r')
    T.ctl(3)
    dc, lq, lrem, _ = divrem_naive(lcc, ldd)
    T.ctl(dc + ABORT_TEST)
    if not inplace: T.free(scc)
    k3 = k2 - dq
    s3 = (ldd - 1) - 2 * k3
    if s3 > 0:
        # the truncated second call: the top 2 k3 + 1 coefficients of (d, r), matrix only; R2^-1 applied to the whole pair only if the caller wants it
        t3, o3 = hgcd(ldd - s3, 0, lrem - s3, 0, k3, 1, 0, False, False, T.here(), 1 - own_side if not pairnode else 1 - ys)
        T.add(t3)
        R2l, R2s, h3 = o3[4], o3[5], o3[6]
        T.ctl(ABORT_TEST)
        lc3 = sc3 = ld3 = sd3 = None
        if wc or wd:
            t4, lc4, sc4, ld4, sd4 = apply_inv(R2l, R2s, h3, ldd, lrem, not want_mat, T.here(), ys)
            T.add(t4); T.ctl(4)
            T.free(sdd); T.free(srm)
            if wc: lc3, sc3 = lc4, sc4
            else: T.free(sc4)
            if wd: ld3, sd3 = ld4, sd4
            else: T.free(sd4)
        else:
            T.free(sdd); T.free(srm)
            if not want_mat: mat_free(T, R2s)
        o3 = (lc3, sc3, ld3, sd3, R2l, R2s, h3)
    else:
        t3, o3 = hgcd(ldd, sdd, lrem, srm, k3, want_mat, 3, wc, wd, T.here(), own_side)
        T.add(t3); T.ctl(ABORT_TEST)
    h = h1 + dq + o3[6]
    if want_mat:
        R1l2, R1s2 = mat_mulQ(T, R1l, R1s, 1 - ys)
        tm, Ml, Ms, cons = mat_mul((R1l2, R1s2), (o3[4], o3[5]), T.here(), ys); T.add(tm)
        if not cons:
            mat_free(T, o3[5]); mat_free(T, R1s2)
        Rl, Rs = Ml, Ms
    T.free(sq)
    return T, (o3[0], o3[1], o3[2], o3[3], Rl, Rs, h)


def hgcd_base(la, sa, lb, sb, k, want_mat, own, wc, wd, T):
    if own & 1: sx = sa
    else:
        t, sx = dupv(la, T.here()); T.add(t)
    if own & 2: sy = sb
    else:
        t, sy = dupv(lb, T.here()); T.add(t)
    lx, ly, ssum = la, lb, 0
    Rl = Rs = None
    if want_mat:
        t, Rl, Rs = mat_identity(T.here()); T.add(t)
    while ly > 0:
        dq = lx - ly
        T.ctl(6)
        if dq > k - ssum: break
        sq = T.new_fp(dq + 1, 0, 'base_q'); sr = T.new_fp(lx, 0, 'base_r')
        dc, lq, lr, _ = divrem_naive(lx, ly)
        T.ctl(dc + ABORT_TEST)
        if want_mat:
            Rl, Rs = mat_mulQ(T, Rl, Rs)
        ssum += dq
        T.free(sx); sx = sy; lx = ly; sy = sr; ly = lr
        T.free(sq)
    lc = sc = ld = sd = None
    if wc: lc, sc = lx, sx
    else: T.free(sx)
    if wd: ld, sd = ly, sy
    else: T.free(sy)
    return T, (lc, sc, ld, sd, Rl, Rs, ssum)


def gcd_cost(m, dG, b, gS, FS):
    """poly_gcd_own(g, R - 1) on the normal remainder sequence, gcd of degree dG; gS, FS: the arrays g (m + 1) and F"""
    T = Tr(b)
    lx, ly = m + 1, m
    sx = gS; sy = FS
    T.ctl(3); T.ctl(3)
    while ly > 0:
        T.ctl(2)
        n = lx - 1
        T.ctl(4)
        if n <= 2 * 96:
            sq = T.new_fp(lx - ly + 1, 0, 'gcd_q'); sr = T.new_fp(lx, 0, 'gcd_r')
            last = (ly == dG + 1)
            dc, lq, lr, _ = divrem_naive(lx, ly, term_zero=1 if (last and dG >= 1) else 0)
            if last and dG == 0:
                lr = 0
            T.ctl(dc + ABORT_TEST)
            T.free(sx); sx = sy; lx = ly; sy = sr; ly = lr
            T.free(sq); T.ctl(5)
            continue
        k = (n + 1) // 2
        t, o = hgcd(lx, sx, ly, sy, k, False, 3, True, True, T.here(), GSIDE[0])
        T.add(t)
        lc, sc, ld, sd = o[0], o[1], o[2], o[3]
        T.ctl(ABORT_TEST)
        T.ctl(2)
        sq = T.new_fp(lc - ld + 1, 0, 'gcd_q')
        inplace = int(sc) == lc or (INPLACE_NB[1] and int(sc) > lc)
        if inplace:
            sr = sc; T.charge_alloc_free()   # the remainder is written over c (dead after the division); the allocation and free stay charged
        else:
            sr = T.new_fp(lc, GSIDE[0], 'gcd_r')
        T.ctl(3)
        dc, lq, lr, _ = divrem_naive(lc, ld)
        T.ctl(dc + ABORT_TEST)
        if not inplace: T.free(sc)
        T.free(sq)
        sx = sd; lx = ld; sy = sr; ly = lr; T.ctl(5)
    T.free(sy)
    T.ctl(2)
    T.ops += powcost(PM2); T.ctl(INV_CTL); T.ld(1)
    T.ops += lx - 1
    T.ld(lx); T.st(lx); T.loopc(lx)
    return T, (lx, sx)


# ---------------------------------------------------------------- the allocator (section 7): a two-ended first-fit pool for blocks of more than 2^BIG_EXP bytes,
# slab classes (slots of 2^j bytes, j >= 7, a free list per class, new slots from the end of the slab area) for the others
class FirstFit:
    """one end of the pool: blocks [size, sid] (sid None = free) in address order from this end; no two free blocks adjacent; the unused middle
    lies beyond the last block.  An allocation takes the first free block (from this end) with at least `need` bytes, cuts it on the side nearest
    this end and leaves the rest free if it is at least 128 bytes; otherwise it extends this end into the middle.  A free merges with free
    neighbours and, if it is the outermost block, with the middle."""
    def __init__(self):
        self.L = []; self.end = 0; self.scans = 0; self.maxblocks = 0

    def alloc(self, sid, need):
        L = self.L
        for k in range(len(L)):
            b = L[k]
            if b[1] is None and b[0] >= need:
                rem = b[0] - need; b[1] = sid
                if rem >= 128:
                    b[0] = need; L.insert(k + 1, [rem, None])
                self.scans += k + 1
                return
        self.scans += len(L) + 1
        L.append([need, sid]); self.end += need
        self.maxblocks = max(self.maxblocks, len(L))

    def free(self, sid):
        L = self.L
        k = next(i for i in range(len(L)) if L[i][1] == sid)
        L[k][1] = None
        if k + 1 < len(L) and L[k + 1][1] is None:
            L[k][0] += L[k + 1][0]; del L[k + 1]
        if k > 0 and L[k - 1][1] is None:
            L[k - 1][0] += L[k][0]; del L[k]; k -= 1
        if k == len(L) - 1:
            self.end -= L[k][0]; del L[k]


DEBUG_SNAP = [False, None]


def simulate(stages):
    """stages: [(name, events)] in program order.  Returns the pool high-water (largest sum of the two ends), per stage, the slab area and class peaks."""
    ends = (FirstFit(), FirstFit()); where = {}
    high = 0; per = {}
    ccur = {}; cpk = {}
    snap_init = None
    for name, ev in stages:
        for e in ev:
            t = e[0]
            if t == 'A':
                where[e[1]] = e[3]; ends[e[3]].alloc(e[1], e[2])
                if ends[0].end + ends[1].end > high:
                    high = ends[0].end + ends[1].end
                    if DEBUG_SNAP[0]: DEBUG_SNAP[1] = (name, [list(b) for b in ends[0].L], [list(b) for b in ends[1].L])
            elif t == 'F':
                ends[where.pop(e[1])].free(e[1])
            elif t == 'a':
                v = ccur.get(e[1], 0) + 1; ccur[e[1]] = v; cpk[e[1]] = max(cpk.get(e[1], 0), v)
            elif t == 'f':
                ccur[e[1]] = ccur.get(e[1], 0) - 1
            else:
                _, sc, sp = e
                for c in set(sc) | set(sp):
                    cpk[c] = max(cpk.get(c, 0), ccur.get(c, 0) + sp.get(c, 0)); ccur[c] = ccur.get(c, 0) + sc.get(c, 0)
        per[name] = high
        if name == 'init':
            snap_init = (tuple(tuple(b) for b in ends[0].L), tuple(tuple(b) for b in ends[1].L), {c: v for c, v in ccur.items() if v})
    snap_end = (tuple(tuple(b) for b in ends[0].L), tuple(tuple(b) for b in ends[1].L), {c: v for c, v in ccur.items() if v})
    assert snap_end == snap_init, 'a trial does not return the allocator to its state after init'
    slab = sum(v << c for c, v in cpk.items())
    return dict(high=high, per=per, slab=slab, cpk=dict(sorted(cpk.items())), scans=ends[0].scans + ends[1].scans,
                maxblocks=ends[0].maxblocks + ends[1].maxblocks)


QE_BYTES = 16 * 1024 + 512        # stages E and later: at most 16 live arrays of at most 17 elements (1,024-byte slots) and the allocator's 36 words
IMAGE_EXTRA = 399216 + 32 + 4851196
CODE_EXTRA = 65536                # code of the lean stages (an allowance; at r = 6 the truncated half-gcd with its tests and the abort: e6dcb600's block-mode kernels are not used)
STACK = 65536


def ceil3(x): return math.ceil(x * 1000) / 1000
def ceil5(x): return math.ceil(x * 100000 - 1e-6) / 100000


def twiddle_slots(m):
    a = 2
    while 3 * (1 << a) < 2 * m - 1: a += 1
    return (1 << min(a, BIGA)) // 2


def corr_len(kappa):
    return min(v for a in range(1, 64) for v in (1 << a, 3 << a) if v >= 2 * kappa - 1)


F_FIRST = [True]


def n_steps(m, E=PM1H):
    top = E.bit_length() - 1; v = 1; bit = top
    while bit >= 1 and ((v << 1) | ebit(E, bit - 1)) < m:
        v = (v << 1) | ebit(E, bit - 1); bit -= 1
    return bit


def stage_AB(m, solve_ws=True):
    """the arrays before stage C: the twiddle table (init), g (stage A), the coset array of stage B with the workspace of the geometric solve
    (block mode) or the inverse-transform array (one transform), then F"""
    I = Tr(0); I.new_fp(twiddle_slots(m), 0, 'tw')
    A = Tr(1); sg = A.new_fp(m + 1, 0, 'g')
    B = Tr(2)
    if m + 1 > (1 << BIGA):
        Pl = make_plan(3, BIGA - 1)[0]; ncos = -(-(m + 1) // Pl.N); H = ncos * Pl.N
        sb = B.new_fp(H, 0, 'H')
        if solve_ws:
            S = corr_len(ncos)
            sw = B.new_fp(4 * S + 3 * ncos, 1, 'ws')      # chirp and mu transforms, correlation buffer, transform scratch, three arrays of kappa constants
            B.free(sw)
        if F_FIRST[0] and n_steps(m) % 2 == 1 and plan3_for_len(2 * m - 1)[0].a > BIGA:
            # an odd number of squaring steps: F is taken before the coset array is freed, so that F alternates back into the slot next to g
            sF = B.new_fp(fslots(m), 0, 'F'); B.free(sb)
            return I, A, B, sg, sF
        B.free(sb)
    else:
        H = min(3 << a for a in range(2, 64) if 3 << a >= m + 1)   # the inverse transform of stage B has 3 * 2^a points (section 4, 'Construction of g_c by evaluation')
        sb = B.new_fp(H, 0, 'H'); B.free(sb)
    sF = B.new_fp(fslots(m), 0, 'F')
    return I, A, B, sg, sF


# ---------------------------------------------------------------- the rows that this ledger does not expand: Jbenisek's entries at each r (section 6 there)
ROWS = {   # r: (C(r), fixed = [init, setup, plan_invN misses, H, I], A, B, E, F, G, trial loop, source entry)
    6: (342, [536889025, 4910, 80314, 5644, 3384436], 1196, 202448149150, '18369013'),
    7: (363, [2147501759, 4910, 86492, 5644, 3384436], 1196, 858062870469, 'df42fe1f'),
    8: (384, [8589952701, 4910, 92670, 5644, 3384436], 1196, 3656592954235, '7d53191b'),
    9: (405, None, 1196, 23115473037075, 'e76bdab0'),
    10: (426, None, 1196, 97164545020652, '418d61f1'),
    11: (447, None, 1196, 539088909426379, '9562cddb'),
    12: (468, None, 1196, 3655884838496434, '048f4110'),
    13: (489, None, 1196, 19262428006970633, 'd57ebc31'),
    14: (510, None, 1196, 107946671426269314, '299f77ac'),
    15: (531, None, 1196, 626993782321806337, 'c5aaccf4'),
    16: (552, None, 1196, 3036821731738006734, 'e8a3b9fa'),
    17: (573, None, 1196, 16824333175932967786, '84a6b973'),
    18: (594, None, 1196, 97722233724525086187, '088b401d'),
    19: (615, None, 1196, 461146671982189275752, 'b1f16047'),
    20: (636, None, 1196, 2534607690146512986240, '5d6dda61'),
    21: (657, None, 1196, 14724903587095649952616, 'f62fb396'),
}
FIXED_BIG = [17179887292, 4910, 95759, 5644, 3384436]
E_CAP, F_ROW, TRIAL_EXTRA, OFFLINE = 166079773, 47012, 12, 1000000
PLAN_EXTRA = 95759                 # e6dcb600: a second allowance for the plan_invN misses (the plans of the lean products differ)
STAT_EXTRA = 64 * 10 ** 10         # e6dcb600: per trial, the flat 64 of the allocator statistics for at most 10^10 calls in rows A, B, E, F, G
B_ALLOC_EXTRA = 10000              # this package: the allocation and free of the coset-solve workspace added to the walk of stage B (an allowance)
RESET_EXTRA = 1000                 # this package: the reset of the allocator after an ABORT (section 6, row 'ABORT reset')
CF_E6 = dict(sq=0.375, q=0.18, qg=0.70, newton=0.25, D=0.06)


def g_row(Cr): return 1000 + 10 * 2 * Cr + 32


def run(r, cf=None, trace=False, big_exp=None, lcut_shift=3, quiet=False, solve_ws=True, acap=None):
    m = (5 ** (6 + r) - 1) // 2
    cf = dict(CF_E6 if cf is None else cf)
    CF.clear(); CF.update({k: (v if isinstance(v, int) else int(v * m)) for k, v in cf.items()})
    ACAP.clear(); ACAP.update({k: (v if isinstance(v, int) else int(v * m)) for k, v in (acap or {}).items()})
    HCACHE.clear(); MODE_LOG.clear()
    res = {}
    if trace:
        TRACE['log'] = []; TRACE['depth'] = 0; TRACE['sid'] = 0
        TRACE['big'] = 1 << big_exp
        LCUT[0] = (1 << big_exp) >> (5 + lcut_shift)
    try:
        I, A, B, sg, sF = stage_AB(m, solve_ws)
        evAB = None
        if trace:
            evAB = list(TRACE['log']); TRACE['log'].clear()
            # split the A/B log by stage: init = first event, A = second, B = the rest
            stages = [('init', evAB[:1]), ('A', evAB[1:2]), ('B', evAB[2:])]
        C, cinfo = powx_lean(m, 3, sF); C.ctl(STAGE_BK)
        if trace:
            stages.append(('C', list(TRACE['log']))); TRACE['log'].clear()
        D = Tr(3); D.ctl(STAGE_BK); D.ops += 1; D.ctl(11)
        t, (lg, sgg) = gcd_cost(m, 0, 3, sg, cinfo['F'])
        D.add(t); D.ctl(2); D.free(sgg)
        if trace:
            stages.append(('D', list(TRACE['log'])))
    finally:
        TRACE['log'] = None; TRACE['depth'] = 0
    tws = twiddle_slots(m); twb = blk(tws); g_b = blk(m + 1); F_b = blk(fslots(m))
    peaks = dict(A=twb + A.peak, B=twb + g_b + B.peak, C=twb + g_b + F_b + C.peak, D=twb + g_b + F_b + D.peak)
    res.update(r=r, m=m, cf=cf, acap=dict(acap or {}), S_C=C.ops, S_D=D.ops, peaks=peaks, cinfo=cinfo, modes=dict(MODE_LOG))
    if trace:
        sim = simulate(stages)
        arena = (sim['high'] + 128 + sim['slab'] + QE_BYTES + 63) & ~63
        res.update(sim=sim, arena=arena, big_exp=big_exp, nevents=sum(len(e) for _, e in stages))
        mem = arena + IMAGE_EXTRA + CODE_EXTRA + STACK
    else:
        arena = (max(peaks.values()) + 63) & ~63
        mem = arena + IMAGE_EXTRA + CODE_EXTRA + STACK
    res['mem'] = mem; res['mem_log2'] = math.log2(mem); res['mem_claim'] = ceil3(math.log2(mem) + 0.002)  # the claim adds 0.002 before rounding (section 7)
    Cr, fixed, rowA, rowB, src = ROWS[r]
    fixed = FIXED_BIG if fixed is None else fixed
    trial = [rowA, rowB + B_ALLOC_EXTRA, C.ops, D.ops, E_CAP, F_ROW, g_row(Cr), TRIAL_EXTRA, STAT_EXTRA, RESET_EXTRA]
    N = sum(fixed) + PLAN_EXTRA + 2 * sum(trial) + OFFLINE
    res.update(Cr=Cr, fixed=fixed, trial=trial, N=N, time_log2=math.log2(N / Cr), time_claim=ceil5(math.log2(N / Cr) + 0.0012))  # the claim adds 0.0012 before rounding (section 6.1)
    res['score'] = res['time_claim'] + max(0, res['mem_claim'] - 20)
    if not quiet:
        report(res)
    return res


def report(res):
    f = lambda x: format(x, ',')
    print('r = %d, m = %s, chunk fractions %s' % (res['r'], f(res['m']), res['cf']))
    ci = res['cinfo']
    print('  stage C: %d squaring steps (%d with S), one step = %s ops%s' % (ci['steps'], ci['nset'], f(ci['step']), '' if not ci.get('prods') else
          '; ' + ', '.join('%s (%s) n2=%d nc=%d %s' % (k, v[0], v[1], v[2], f(v[3])) for k, v in ci['prods'].items())))
    print('  S_C = %s   S_D = %s   block-product schemes used: %s' % (f(res['S_C']), f(res['S_D']), res['modes']))
    m32 = 32 * res['m']
    print('  live-set peaks: ' + ', '.join('%s %s (%.4f m)' % (k, f(v), v / m32) for k, v in res['peaks'].items()))
    if 'sim' in res:
        s = res['sim']
        print('  allocator: pool high-water %s (%.6f x live peak), per stage %s; slab area %s; arena %s; %d events' %
              (f(s['high']), s['high'] / max(res['peaks'].values()), {k: f(v) for k, v in s['per'].items()}, f(s['slab']), f(res['arena']), res['nevents']))
    print('  memory = %s bytes, log2 = %.5f, claimed %.3f' % (f(res['mem']), res['mem_log2'], res['mem_claim']))
    print('  N_max = %s, log2(N/%d) = %.8f, time_log2 claimed %.5f, score %.5f' % (f(res['N']), res['Cr'], res['time_log2'], res['time_claim'], res['score']))


def check_r21():
    """reproduce the totals asserted by e6dcb600 at r = 21 with its chunk fractions"""
    res = run(21, CF_E6, quiet=True, solve_ws=False)
    assert res['S_C'] == 4062062219504740890363177, res['S_C']
    assert res['S_D'] == 1360756098766545569709103, res['S_D']
    assert res['peaks'] == dict(A=119209289619500726912, B=238418579240595258048, C=632939936390951625792, D=577946978315814447872), res['peaks']
    return res


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == 'check21':
        res = check_r21(); report(res)
        print('peaks match e6dcb600:', res['peaks'] == dict(A=119209289619500726912, B=238418579240595258048, C=632939936390951625792, D=577946978315814447872))
    else:
        r = int(args[0]); tr = '--trace' in args
        be = int(args[args.index('--big') + 1]) if '--big' in args else None
        cfa = None
        if '--cf' in args:
            v = [float(x) for x in args[args.index('--cf') + 1].split(',')]
            cfa = dict(zip(('sq', 'q', 'qg', 'newton', 'D'), v))
        run(r, cfa, tr, be)
```

## 13. Appendix F: the programs of 10.3 and 10.5

The three programs, as run. `certify.py` is the certificate program of Grok job 136 (python-flint); `certify_dep.py` runs it unchanged on the deployed constants and on the attack line, reading the constants and `line()` from `experiments/exp_line.py` (same folder); `sib_euclid.py` is the measurement of 10.5 (same folder).

### F.1 certify.py (Grok job 136)

```python
"""
Certify H_ci pieces for the first N full rounds of the Orchard Poseidon
permutation (Pallas base field, t=3, x^5, Grain MDS and round constants
from grain.py / params.txt).

Line: state(lambda) = (lambda, 2*lambda+1, 3*lambda+5).
Points compared by the attack are lambda = c±s.
Output word F is coordinate 0 after N full rounds
    state <- MDS * (state + RC[r])**5.

Run:
    python certify.py 1
    python certify.py 2
    python certify.py 3
    python certify.py 4 --start 1 --stride 1 --limit 4000
"""

from __future__ import annotations

import argparse
import os
import time
from math import gcd as int_gcd

from flint import fmpz_mod_poly, fmpz_mod_poly_ctx

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
HERE = os.path.dirname(os.path.abspath(__file__))
CTX = fmpz_mod_poly_ctx(P)
X = fmpz_mod_poly([0, 1], CTX)


def load_params():
    path = os.path.join(HERE, "params.txt")
    if not os.path.exists(path):
        raise SystemExit("params.txt missing; run python grain.py")
    mds = []
    rc = []
    mode = None
    with open(path, encoding="ascii") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line == "mds":
                mode = "mds"
                continue
            if line == "rc":
                mode = "rc"
                continue
            if line.startswith("cauchy") or line.startswith("p ") or line.startswith("t ") or line.startswith("RF") or line.startswith("RP") or line.startswith("alpha"):
                mode = None
                continue
            if mode == "mds":
                mds.append([int(x) for x in line.split()])
            elif mode == "rc":
                rc.append([int(x) for x in line.split()])
    if len(mds) != 3 or any(len(r) != 3 for r in mds):
        raise SystemExit("bad mds")
    if len(rc) < 4:
        raise SystemExit("need at least 4 round-constant rows")
    return mds, rc


def low(poly):
    if poly.is_zero():
        return [0]
    return [int(c) % P for c in poly.coeffs()]


def C(n):
    return fmpz_mod_poly([n % P], CTX)


def add_const(poly, c):
    cs = low(poly)
    cs[0] = (cs[0] + c) % P
    return fmpz_mod_poly(cs, CTX)


def pow5(poly):
    s2 = poly.square()
    s4 = s2.square()
    return s4 * poly


def matvec(mds, vec):
    out = []
    for i in range(3):
        acc = fmpz_mod_poly([0], CTX)
        for j in range(3):
            acc += vec[j] * (mds[i][j] % P)
        out.append(acc)
    return out


def build_F(N, mds, rc):
    state = [
        fmpz_mod_poly([0, 1], CTX),       # lambda
        fmpz_mod_poly([1, 2], CTX),       # 2*lambda + 1
        fmpz_mod_poly([5, 3], CTX),       # 3*lambda + 5
    ]
    for r in range(N):
        state = [pow5(add_const(state[i], rc[r][i])) for i in range(3)]
        state = matvec(mds, state)
    return state[0]


def leading_by_slopes(N, mds):
    L = [1, 2, 3]
    for _ in range(N):
        powered = [pow(v, 5, P) for v in L]
        L = [
            sum(mds[i][j] * powered[j] for j in range(3)) % P
            for i in range(3)
        ]
    return L[0]


def H_at(F, c):
    """H(c, u) where G(c, t) = H(c, t^2) = (F(c+t)-F(c-t))/(2t)."""
    c %= P
    Fp = F.compose(X + c)
    Fm = F.compose(C(c) - X)
    diff = Fp - Fm
    cs = low(diff)
    if cs[0] % P != 0:
        raise RuntimeError("F(c+t)-F(c-t) has a constant term")
    # divide by t, then by 2; keep even powers (poly in u=t^2)
    halved = cs[1:]
    inv2 = pow(2, -1, P)
    halved = [(v * inv2) % P for v in halved]
    hcoeffs = halved[0::2]
    # odd positions must vanish
    if any(halved[i] % P != 0 for i in range(1, len(halved), 2)):
        raise RuntimeError("G is not even in t")
    return fmpz_mod_poly(hcoeffs, CTX)


def G_in_c(F, t):
    """G(c, t) as a polynomial in c, t a nonzero field element."""
    if t % P == 0:
        raise ValueError("t=0")
    diff = F.compose(X + (t % P)) - F.compose(X - (t % P))
    inv = pow((2 * t) % P, -1, P)
    return diff * inv


def eval_poly(poly, a):
    return int(poly.evaluate(a % P)) % P


def factor_degrees(poly):
    fac = poly.factor()
    degs = []
    squarefree = True
    for g, e in fac[1]:
        e = int(e)
        if e != 1:
            squarefree = False
        degs.extend([int(g.degree())] * e)
    degs.sort()
    return degs, squarefree, fac


def is_prime_small(q):
    if q < 2:
        return False
    if q % 2 == 0:
        return q == 2
    d = 3
    while d * d <= q:
        if q % d == 0:
            return False
        d += 2
    return True


def largest_prime_leq(n):
    q = n
    while q >= 2 and not is_prime_small(q):
        q -= 1
    return q


def pow_x(poly):
    return X.pow_mod(P, poly)


def linear_gcd(poly):
    xp = pow_x(poly)
    g = poly.gcd(xp - X)
    return g


def squarefree_poly(g):
    if g.degree() <= 0:
        return True
    d = g.gcd(g.derivative())
    return d.degree() <= 0


def simple_root_stats(F):
    d1 = F.derivative()
    d2 = d1.derivative()
    g = d1.gcd(d2)
    deg = int(d1.degree())
    gdeg = int(g.degree()) if not g.is_zero() else -1
    # number of distinct roots in the algebraic closure that are simple
    # equals deg(d1 / rad_multiple). If g = gcd(d1, d1'), then d1/g is the
    # squarefree product of the simple-root factors only when every multiple
    # root's multiplicity is exactly the amount removed... standard fact:
    # d1 / gcd(d1, d1') is squarefree and its roots are exactly the distinct
    # roots of d1. That counts DISTINCT roots, not simple roots.
    # Simple roots: let s = d1 / gcd(d1, d1'). The multiple-root factors are
    # those of g. A root is simple iff it divides s and not g.
    # product of (x-r) over simple r  =  s / gcd(s, g) but g divides a power
    # of the multiple part and is coprime to the simple part, so gcd(s, g)
    # is 1 if s was computed as d1/g in a UFD... actually d1/g is coprime to
    # the radical of the multiple part only after removing all shared roots.
    # In char 0 or p > deg, gcd(d1, d1') is exactly the product (x-r)^{m_r-1}.
    # Then d1/gcd has each distinct root once, INCLUDING multiple roots.
    # The simple ones are the roots of d1/gcd that are not roots of gcd.
    quot = d1.exact_division(g) if g.degree() >= 0 and not g.is_zero() else d1
    # remove roots that are still multiple, i.e. divide out gcd(quot, g)
    shared = quot.gcd(g)
    if shared.degree() > 0:
        simple = quot.exact_division(shared)
    else:
        simple = quot
    n_simple_factors_deg = int(simple.degree()) if simple.degree() >= 0 else 0
    return {
        "deg_Fprime": deg,
        "deg_gcd_Fp_Fpp": int(g.degree()) if g.degree() >= 0 else -1,
        "deg_simple_part": n_simple_factors_deg,
    }


def interpolate(xs, ys):
    n = len(xs)
    xs = [int(x) % P for x in xs]
    dd = [int(y) % P for y in ys]
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            dd[i] = ((dd[i] - dd[i - 1]) * pow((xs[i] - xs[i - j]) % P, -1, P)) % P
    out = fmpz_mod_poly([dd[0]], CTX)
    basis = fmpz_mod_poly([1], CTX)
    for j in range(1, n):
        basis *= X - xs[j - 1]
        out += basis * (dd[j] % P)
    return out


def eliminant_in_s2(F, s1, bound):
    """Res_c(G(c,s1), G(c,s2)) as a polynomial in s2, degree <= bound."""
    gs1 = G_in_c(F, s1)
    # sample s2 = 1..bound+1, skipping 0 and collisions are fine (zeros)
    xs = []
    ys = []
    s2 = 1
    while len(xs) < bound + 1:
        if s2 % P == 0:
            s2 += 1
            continue
        gs2 = G_in_c(F, s2)
        val = gs1.resultant(gs2)
        xs.append(s2)
        ys.append(int(val) % P)
        s2 += 1
    return interpolate(xs, ys)


def divide_out_linear(poly, root, max_mult=64):
    mult = 0
    root %= P
    factor = X - root
    while poly.degree() >= 1:
        q, r = poly.divmod(factor)
        if r.degree() > 0 or (not r.is_zero() and low(r)[0] % P != 0):
            break
        # r should be 0
        if not r.is_zero():
            break
        poly = q
        mult += 1
        if mult > max_mult:
            break
    return poly, mult


def sign_of_cycle_type(degs):
    # sign of a permutation is (-1)^{sum (len-1)}
    s = sum(d - 1 for d in degs)
    return -1 if s % 2 else 1


def log(msg):
    print(msg, flush=True)
    try:
        with open(os.path.join(HERE, "runlog.txt"), "a", encoding="utf-8") as fh:
            fh.write(msg + "\n")
    except OSError:
        pass


def certify_derivative_and_degree(N, F, mds):
    D = 5 ** N
    deg = int(F.degree())
    lead = int(F.leading_coefficient()) % P
    pred = leading_by_slopes(N, mds)
    stats = simple_root_stats(F)
    # identity H(c,0) == F'(c) at a few points
    dF = F.derivative()
    ident_ok = True
    for c in (1, 2, 5, 17):
        h0 = eval_poly(H_at(F, c), 0)
        fp = eval_poly(dF, c)
        if h0 != fp:
            ident_ok = False
            log(f"IDENTITY FAIL c={c} H(c,0)={h0} F'(c)={fp}")
    # random point agreement: poly vs not needed, build is symbolic
    log(
        f"N={N} degF={deg} expect={D} lead={lead} slope_lead={pred} "
        f"lead_match={lead == pred} H0_is_Fprime={ident_ok} simple={stats}"
    )
    return {
        "deg": deg,
        "lead": lead,
        "lead_match": lead == pred and lead != 0 and deg == D,
        "ident_ok": ident_ok,
        "simple": stats,
    }


def search_cycle_types(N, F, start, stride, limit, time_cap):
    """Search specialisations c = start, start+stride, ... 

    Stops early once an m-cycle, an (m-1)-cycle and a Jordan q-cycle
    have all been seen, or after `limit` values, or after time_cap seconds.
    """
    D = 5 ** N
    m = (D - 1) // 2
    q = largest_prime_leq(m - 3) if m >= 6 else None
    fixed_for_q = (m - q) if q is not None else None
    log(f"search N={N} m={m} jordan_q={q} fixed_points={fixed_for_q} start={start} stride={stride} limit={limit}")
    found = {"m_cycle": None, "m1_cycle": None, "jordan": None}
    t0 = time.perf_counter()
    checked = 0
    c = start
    samples = []
    use_full = N <= 3
    while checked < limit:
        if time.perf_counter() - t0 > time_cap:
            log(f"time cap {time_cap}s hit after {checked} values, last c={c - stride}")
            break
        H = H_at(F, c)
        if int(H.degree()) != m:
            log(f"degree drop c={c} deg={H.degree()}")
            c += stride
            checked += 1
            continue
        if use_full:
            degs, sqf, _fac = factor_degrees(H)
            if len(samples) < 12:
                samples.append((c, degs, sqf))
                log(f"sample c={c} squarefree={sqf} degs={degs}")
            if sqf and found["m_cycle"] is None and degs == [m]:
                found["m_cycle"] = c
                log(f"FOUND m-cycle c={c} time={time.perf_counter()-t0:.2f}s")
            if sqf and found["m1_cycle"] is None and degs == [1, m - 1]:
                found["m1_cycle"] = c
                log(f"FOUND (m-1,1) c={c} time={time.perf_counter()-t0:.2f}s")
            if (
                sqf
                and q is not None
                and found["jordan"] is None
                and degs == [1] * fixed_for_q + [q]
            ):
                found["jordan"] = (c, q, fixed_for_q)
                log(
                    f"FOUND jordan {q}-cycle + {fixed_for_q} fixed "
                    f"c={c} time={time.perf_counter()-t0:.2f}s"
                )
        else:
            g = linear_gcd(H)
            gd = int(g.degree()) if g.degree() > 0 else 0
            sf = squarefree_poly(g) if gd > 0 else True
            if found["m_cycle"] is None and gd == 0 and H.is_irreducible():
                found["m_cycle"] = c
                log(f"FOUND m-cycle c={c} time={time.perf_counter()-t0:.2f}s")
            if found["m1_cycle"] is None and gd == 1 and sf:
                quot = H.exact_division(g.monic())
                if quot.is_irreducible():
                    found["m1_cycle"] = c
                    log(f"FOUND (m-1,1) c={c} time={time.perf_counter()-t0:.2f}s")
            if q is not None and found["jordan"] is None and gd == fixed_for_q and sf:
                quot = H.exact_division(g.monic())
                if int(quot.degree()) == q and quot.is_irreducible():
                    found["jordan"] = (c, q, fixed_for_q)
                    log(
                        f"FOUND jordan {q}-cycle + {fixed_for_q} fixed "
                        f"c={c} time={time.perf_counter()-t0:.2f}s"
                    )
        checked += 1
        if checked % 25 == 0:
            log(
                f"progress checked={checked} c={c} elapsed={time.perf_counter()-t0:.1f}s "
                f"found={found}"
            )
        if found["m_cycle"] and found["m1_cycle"] and (q is None or found["jordan"]):
            log("all targets found")
            break
        c += stride
    elapsed = time.perf_counter() - t0
    log(f"search done checked={checked} elapsed={elapsed:.2f}s found={found}")
    return {
        "m": m,
        "q": q,
        "found": found,
        "samples": samples,
        "checked": checked,
        "elapsed": elapsed,
    }


def multiplicity_of_root(poly, root):
    poly, mult = divide_out_linear(poly, root, max_mult=10000)
    return poly, mult


def n1_eliminant(F):
    """For N=1, compute Res_c(G(c,s1), G(c,s2)) at several s1 and factor."""
    # degree bound: (5-1)^2 = 16, take 24 to see the true degree
    bound = 24
    results = []
    for s1 in (3, 5, 8, 13):
        t0 = time.perf_counter()
        poly = eliminant_in_s2(F, s1, bound)
        # trim leading zeros already handled by degree
        deg = int(poly.degree())
        log(f"eliminant s1={s1} deg={deg} time={time.perf_counter()-t0:.3f}s")
        # divide out (s2-s1) and (s2+s1)
        poly, m_plus = multiplicity_of_root(poly, s1)       # s2 = s1
        poly, m_minus = multiplicity_of_root(poly, (-s1) % P)  # s2 = -s1
        degs, sqf, fac = factor_degrees(poly)
        log(
            f"  after removing (s2-s1)^{m_plus} (s2+s1)^{m_minus}: "
            f"deg={poly.degree()} squarefree={sqf} factor_degs={degs}"
        )
        results.append(
            {
                "s1": s1,
                "raw_deg": deg,
                "mult_s2_eq_s1": m_plus,
                "mult_s2_eq_minus_s1": m_minus,
                "cofactor_degs": degs,
                "cofactor_squarefree": sqf,
                "cofactor": poly,
            }
        )
    return results


def abs_irreducible_univariate_specialization(bivariate_builder, degree, divisors):
    """Not used for large degree. Placeholder kept out; N=1 uses direct test."""
    raise NotImplementedError


def test_abs_irred_phi(cofactor_poly_at_s1_builder, s1_values_in_ext, degree):
    pass


def n1_absolute(F):
    """Absolute irreducibility of the N=1 cofactor via extension specialisations.

    Build the bivariate-in-practice eliminant cofactor as a univariate in s2
    over an extension of the s1-line, by specialising s1 in F_{p^k}.
    """
    from flint import fq_default_ctx, fq_default_poly_ctx

    # First get Phi over F_p at s1=3, as produced by n1, and its degree.
    # We recompute a monic cofactor in F_p[s2] and then, for each prime-power
    # divisor, specialise s1 inside F_{p^k}.
    #
    # Concrete method: G_in_c needs F over the prime field, resultant too.
    # For s1 in F_{p^k}, do the resultant inside that extension.
    D = 5
    # Rebuild F over prime field is already `F`. For extension arithmetic,
    # convert F's coefficients into the extension and repeat eliminant
    # interpolation there only for k in the divisor set of the cofactor degree.
    base = eliminant_in_s2(F, 3, 24)
    base, m1 = multiplicity_of_root(base, 3)
    base, m2 = multiplicity_of_root(base, (-3) % P)
    degs, sqf, fac = factor_degrees(base)
    log(f"base cofactor at s1=3 degs={degs} sqf={sqf} mults {m1},{m2}")
    # If several F_p factors, test each factor's absolute irreducibility
    # by the specialization method on that factor's degree.
    factors = []
    for g, e in fac[1]:
        factors.append((g.monic(), int(g.degree()), int(e)))
    reports = []
    for g, deg, e in factors:
        divs = [d for d in range(2, deg + 1) if deg % d == 0]
        # only need to forbid a split into d conjugate pieces; the extension
        # degree to test is d (number of conjugates). For deg<=16 this is fine.
        log(f"absolute test factor deg={deg} exp={e} divisors={divs}")
        verdicts = []
        for k in divs:
            Fld = fq_default_ctx(P, k)
            PC = fq_default_poly_ctx(Fld)
            Y = PC.gen()
            # lift prime-field F into extension polys in c
            fcoeffs = low(F)

            def lift_poly(coeffs):
                # coeffs low to high as field elements
                return sum(
                    (PC.gen() ** 0) * 0,
                    (),
                )  # placeholder replaced below

            # Build extension polynomial from prime-field coefficient list.
            def ext_poly(coeffs, PC=PC):
                # Use the prime-field embedding: fq elements from ints.
                cs = []
                for a in coeffs:
                    cs.append(Fld(int(a) % P))
                # fq_default_poly from list?
                return PC([Fld(int(a) % P) for a in coeffs]) if False else None

            # Construct via the context call pattern that worked for fmpz:
            # try PC.zero and accumulation.
            acc = None
            # We'll build using evaluate-and-interpolate over the extension,
            # calling resultant in the extension.
            verdicts.append((k, "deferred"))
        reports.append({"deg": deg, "exp": e, "divs": divs, "verdicts": verdicts})
    return {"factors": [(d, e) for _, d, e in factors], "reports": reports, "sqf": sqf}


def build_ext_poly(PC, Fld, coeffs):
    """coeffs low-to-high integers -> fq poly."""
    # Try constructor
    try:
        return PC([Fld(int(a) % P) for a in coeffs])
    except Exception:
        pass
    x = PC.gen()
    acc = PC.zero()
    powx = PC.one()
    for a in coeffs:
        acc += powx * Fld(int(a) % P)
        powx *= x
    return acc


def g_in_c_ext(F_coeffs, t_ext, PC, Fld):
    """G(c, t) in the extension, t_ext an fq element, as a poly in c."""
    # F(c+t) = sum f_k (c+t)^k. Use horner in the polynomial ring.
    x = PC.gen()
    # shift variable to x+t
    # Horner
    acc_p = PC.zero()
    acc_m = PC.zero()
    # evaluate horner with the polynomial (x+t) substituted: just horner the
    # coefficient list into the element (x + t) of the polynomial ring.
    xp = x + t_ext
    xm = x - t_ext
    for a in reversed(F_coeffs):
        acc_p = acc_p * xp + Fld(int(a) % P)
        acc_m = acc_m * xm + Fld(int(a) % P)
    diff = acc_p - acc_m
    inv = (Fld(2) * t_ext) ** -1
    return diff * inv


def eliminant_ext(F_coeffs, s1_ext, bound, PC, Fld):
    gs1 = g_in_c_ext(F_coeffs, s1_ext, PC, Fld)
    # interpolate in s2 at field elements 1,2,... 
    xs = []
    ys = []
    s2 = 1
    x = PC.gen()
    while len(xs) < bound + 1:
        s2_e = Fld(s2)
        if s2_e.is_zero():
            s2 += 1
            continue
        gs2 = g_in_c_ext(F_coeffs, s2_e, PC, Fld)
        val = gs1.resultant(gs2)
        xs.append(s2_e)
        ys.append(val)
        s2 += 1
    # Newton interpolation over Fq
    n = len(xs)
    dd = list(ys)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            dd[i] = (dd[i] - dd[i - 1]) / (xs[i] - xs[i - j])
    out = PC.zero() + dd[0]
    # PC.zero()+dd[0] might fail if types differ; use accumulation
    basis = PC.one()
    out = basis * dd[0]
    for j in range(1, n):
        basis *= x - xs[j - 1]
        out += basis * dd[j]
    return out


def divide_linear_ext(poly, root, PC):
    x = PC.gen()
    mult = 0
    factor = x - root
    while poly.degree() >= 1:
        q, r = poly.divmod(factor)
        if not r.is_zero():
            break
        poly = q
        mult += 1
        if mult > 64:
            break
    return poly, mult


def horner_ext(coeffs, point, Fld):
    acc = Fld(0)
    for a in reversed(coeffs):
        acc = acc * point + Fld(int(a) % P)
    return acc


def n1_absolute_run(F):
    """Interpolate Phi(s1, s2), the degree-8 cofactor of the eliminant, and
    test absolute irreducibility by irreducible specialisations over F_{p^k}.
    """
    from flint import fq_default_ctx, fq_default_poly_ctx

    samples = []
    for s1 in range(1, 25):
        poly = eliminant_in_s2(F, s1, 20)
        raw = int(poly.degree())
        poly, m1 = multiplicity_of_root(poly, s1)
        poly, m2 = multiplicity_of_root(poly, (-s1) % P)
        if m1 != 4 or m2 != 4:
            log(f"unexpected multiplicity s1={s1} ({m1},{m2})")
        cs = low(poly)
        samples.append((s1, cs, raw, int(poly.degree())))
    deg_s2 = max(d for _, _, _, d in samples)
    log(f"Phi samples deg_s2={deg_s2} raw_degs={sorted(set(r for _,_,r,_ in samples))}")
    # coefficient of s2^j as a polynomial in s1
    coeff_polys = []
    for j in range(deg_s2 + 1):
        xs = [s1 for s1, _, _, _ in samples]
        ys = []
        for _, cs, _, _ in samples:
            ys.append(cs[j] if j < len(cs) else 0)
        coeff_polys.append(interpolate(xs, ys))
        log(f"  coeff s2^{j} deg_s1={int(coeff_polys[-1].degree())}")
    # consistency: a second interpolation on a subset must agree on a fresh s1
    check_s1 = 30
    poly = eliminant_in_s2(F, check_s1, 20)
    poly, _, = multiplicity_of_root(poly, check_s1)
    # recompute properly
    poly = eliminant_in_s2(F, check_s1, 20)
    poly, _m1 = multiplicity_of_root(poly, check_s1)
    poly, _m2 = multiplicity_of_root(poly, (-check_s1) % P)
    got = low(poly)
    pred = [eval_poly(coeff_polys[j], check_s1) for j in range(deg_s2 + 1)]
    while got and got[-1] == 0:
        got.pop()
    while pred and pred[-1] == 0:
        pred.pop()
    if got != pred:
        log(f"INTERPOLATION MISMATCH s1={check_s1} got_deg={len(got)-1} pred_deg={len(pred)-1}")
        # show first difference
        for i, (a, b) in enumerate(zip(got, pred)):
            if a != b:
                log(f"  first diff at s2^{i}")
                break
        else:
            log(f"  length mismatch {len(got)} vs {len(pred)}")
        raise SystemExit(1)
    log(f"interpolation agrees at s1={check_s1}")
    # content
    content = coeff_polys[0]
    for cp in coeff_polys[1:]:
        content = content.gcd(cp)
    log(f"content degree {int(content.degree())} (0 means constant)")
    # F_p factorisation of one specialisation already logged; repeat at s1=13
    spec = [eval_poly(coeff_polys[j], 13) for j in range(deg_s2 + 1)]
    spec_poly = fmpz_mod_poly(spec, CTX)
    degs, sqf, _ = factor_degrees(spec_poly)
    log(f"Phi(13,s2) squarefree={sqf} degs={degs}")
    divs = [d for d in range(2, deg_s2 + 1) if deg_s2 % d == 0]
    tests = []
    for k in divs:
        t0 = time.perf_counter()
        Fld = fq_default_ctx(P, k)
        PC = fq_default_poly_ctx(Fld)
        # several s1 in the extension, stop at the first full-degree irreducible
        z = Fld.gen()
        hit = None
        for tadd in range(0, 40):
            s1 = z + Fld(tadd + 1)
            ev = [horner_ext(low(coeff_polys[j]), s1, Fld) for j in range(deg_s2 + 1)]
            # drop leading zeros
            while ev and ev[-1].is_zero():
                ev.pop()
            if len(ev) - 1 != deg_s2:
                continue
            fp = PC.zero()
            # build by horner in PC
            x = PC.gen()
            acc = PC.zero()
            for a in reversed(ev):
                acc = acc * x + a
            fp = acc
            if int(fp.degree()) == deg_s2 and fp.is_irreducible():
                hit = tadd + 1
                break
        dt = time.perf_counter() - t0
        log(f"  ext k={k} irreducible full-degree hit_t={hit} time={dt:.2f}s")
        tests.append({"k": k, "hit": hit, "time": dt})
    return {"deg_s2": deg_s2, "tests": tests, "content_deg": int(content.degree())}


def disc_quadratic(F):
    """For degree-5 F, H is quadratic in u. Return disc(u) as poly in c, factored."""
    # Sample H at many c and interpolate the discriminant polynomial.
    # H = A u^2 + B(c) u + C(c), A = leading = const.
    # disc = B^2 - 4 A C.
    # Degree of disc: B has deg <= 3? Let's just interpolate high enough.
    # deg F=5, H degree 2 in u, coeffs of u^1 and u^0 have degree <= 4.
    # disc degree <= 8. Sample 12 points.
    xs = []
    ys = []
    A = None
    for c in range(1, 14):
        H = H_at(F, c)
        cs = low(H)
        while len(cs) < 3:
            cs.append(0)
        if A is None:
            A = cs[2]
        disc = (cs[1] * cs[1] - 4 * cs[2] * cs[0]) % P
        xs.append(c)
        ys.append(disc)
    poly = interpolate(xs, ys)
    degs, sqf, fac = factor_degrees(poly)
    log(f"disc poly deg={poly.degree()} squarefree={sqf} factor_degs={degs} lead={int(poly.leading_coefficient())%P}")
    # Is disc a square in F_p-bar(c)? Squarefree part degree > 0 => no.
    sqfree_degs = []
    for g, e in fac[1]:
        if int(e) % 2 == 1:
            sqfree_degs.append(int(g.degree()))
    log(f"odd-exponent factor degrees {sqfree_degs}")
    return {
        "deg": int(poly.degree()),
        "factor_degs": degs,
        "squarefree": sqf,
        "odd_factor_degs": sqfree_degs,
        "lead": int(poly.leading_coefficient()) % P,
    }


def spot_check_F(N, F, mds, rc):
    """Compare F(lambda) with direct round iteration at a few lambdas."""
    ok = True
    for lam in (0, 1, 2, 7, 19):
        state = [lam % P, (2 * lam + 1) % P, (3 * lam + 5) % P]
        for r in range(N):
            state = [pow((state[i] + rc[r][i]) % P, 5, P) for i in range(3)]
            state = [
                sum(mds[i][j] * state[j] for j in range(3)) % P
                for i in range(3)
            ]
        pred = eval_poly(F, lam)
        if pred != state[0]:
            ok = False
            log(f"SPOT FAIL N={N} lam={lam} poly={pred} direct={state[0]}")
    log(f"spot check N={N} ok={ok}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("N", type=int)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--limit", type=int, default=5000)
    ap.add_argument("--time-cap", type=float, default=600.0)
    ap.add_argument("--skip-search", action="store_true")
    args = ap.parse_args()
    mds, rc = load_params()
    log(f"loaded rc rows {len(rc)} mds00 {mds[0][0]}")
    t0 = time.perf_counter()
    F = build_F(args.N, mds, rc)
    log(f"built F N={args.N} in {time.perf_counter()-t0:.3f}s deg={F.degree()}")
    spot_check_F(args.N, F, mds, rc)
    info = certify_derivative_and_degree(args.N, F, mds)
    if args.N == 1:
        disc_quadratic(F)
        n1_eliminant(F)
        n1_absolute_run(F)
    if not args.skip_search and args.N >= 2:
        search_cycle_types(args.N, F, args.start, args.stride, args.limit, args.time_cap)
    elif args.N == 1 and not args.skip_search:
        # small cycle types of H for the record
        search_cycle_types(1, F, 1, 1, 30, 60)


if __name__ == "__main__":
    main()
```

### F.2 certify_dep.py

```python
# Grok 136 certificate code (certify.py, unchanged) run on the DEPLOYED constants and the attack's own line.
# F_N = coordinate 0 of the first N S-box layers of the digest polynomial of proof.md section 2.3, in the variable W:
# start state alpha + beta W (the line j = 0 after the first two rounds), layers = rounds 2, 3 (full), 4, 5, ... (partial, coordinate 0 only).
# usage: python certify_dep.py N [--limit L --time-cap T --skip-search]   (certify.py and exp_line.py in this folder)
import sys, os
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exp_line.py')).read()
exec(src[:src.index('NPAIR = 150')], globals())          # P, MDS, RC, line(), rounds_from()
import certify as Z
from flint import fmpz_mod_poly
Z.HERE = os.path.dirname(os.path.abspath(__file__))
FULL = [True, True] + [False] * 20
_qu, _qv, _a, _b, AL, BE = line(7)
def load_params(): return MDS, [RC[2 + r] for r in range(20)]
def build_F(N, mds, rc):
    st = [Z.add_const(Z.C(0), 0) * 0 + Z.X * BE[i] + AL[i] for i in range(3)]
    for r in range(N):
        st = [Z.add_const(st[i], rc[r][i]) for i in range(3)]
        st = [Z.pow5(st[i]) if (FULL[r] or i == 0) else st[i] for i in range(3)]
        st = Z.matvec(mds, st)
    return st[0]
def leading_by_slopes(N, mds):
    L = [(v, 1) for v in BE]                      # (leading coefficient, degree) of each coordinate
    for r in range(N):
        pw = [(pow(v, 5, P), 5 * d) if (FULL[r] or i == 0) else (v, d) for i, (v, d) in enumerate(L)]
        top = max(d for _, d in pw)
        L = [(sum(mds[i][j] * pw[j][0] for j in range(3) if pw[j][1] == top) % P, top) for i in range(3)]
    return L[0][0]
def spot_check_F(N, F, mds, rc):
    ok = True
    for w in (0, 1, 2, 7, 19):
        s = [(AL[i] + BE[i] * w) % P for i in range(3)]
        for r in range(N):
            s = [(s[i] + rc[r][i]) % P for i in range(3)]
            s = [pow(s[i], 5, P) if (FULL[r] or i == 0) else s[i] for i in range(3)]
            s = [sum(mds[i][j] * s[j] for j in range(3)) % P for i in range(3)]
        if Z.eval_poly(F, w) != s[0]: ok = False; Z.log(f"SPOT FAIL N={N} w={w}")
    Z.log(f"spot check N={N} ok={ok} (deployed constants, attack line)")
    return ok
Z.load_params, Z.build_F, Z.leading_by_slopes, Z.spot_check_F = load_params, build_F, leading_by_slopes, spot_check_F
Z.log = lambda msg: print(msg, flush=True)
if __name__ == "__main__": Z.main()
```

### F.3 sib_euclid.py

```python
# Euclid-normality measurement (A1 of H1-charging-rules) on the real Orchard digest polynomial of the sibling targets
# r' = 0,1,2 partial rounds (same constants, same line j=0 of rounds 0-1, degree 5^(6+r')). Uses python-flint. usage: sib_euclid.py R NCENTRES [START]
import sys, time, json, hashlib, re
from flint import fmpz_mod_poly_ctx, fmpz_mod_ctx
src = open('exp_line.py').read()
exec(src[:src.index('req = json.loads')].replace('NPAIR = 150', 'NPAIR = 150'), globals())   # P, MDS, RC, line()
R = int(sys.argv[1]); NC = int(sys.argv[2]); START = int(sys.argv[3]) if len(sys.argv) > 3 else 1
ctx = fmpz_mod_poly_ctx(fmpz_mod_ctx(P)); X = ctx.gen()
qu, qv, a, bb, al, be = line(R)
s = [al[i] + be[i] * X for i in range(3)]
for i in (*range(2, 4), *range(4, 4 + R), *range(60, 64)):
    s = [x + c for x, c in zip(s, RC[i])]
    for j in (range(3) if i < 4 or i >= 60 else range(1)): s[j] = s[j] ** 5
    s = [sum((MDS[r][k] * s[k] for k in range(3)), ctx.zero() if hasattr(ctx, 'zero') else 0 * X) for r in range(3)]
F = s[0]; D = F.degree(); assert D == 5 ** (6 + R), D
m = (D - 1) // 2
out = []
for c in range(START, START + NC):
    t0 = time.time()
    Fc = F.compose(X + c); co = Fc.coeffs()
    g = ctx([co[2 * k + 1] for k in range(m + 1)]).monic()
    Rr = X.pow_mod((P - 1) // 2, g) - 1
    t1 = time.time()
    a_, b_ = g, Rr; steps = 0; bad = []; 
    while b_.degree() > 0:
        q, r = a_.divmod(b_); steps += 1
        if q.degree() != 1: bad.append((steps, q.degree()))
        a_, b_ = b_, r
    rec = dict(r=R, centre=c, D=D, m=m, deg_R1=Rr.degree(), euclid_steps=steps, nonnormal=bad[:5], n_nonnormal=len(bad), final_deg=a_.degree() if b_.is_zero() else b_.degree(), sec_pow=round(t1 - t0, 1), sec_euclid=round(time.time() - t1, 1))
    print(json.dumps(rec), flush=True)
```


## 14. Appendix G: small-size checks

(Jbenisek's entry at this r has no Appendix G; G.1 is not used. G.2 is this package's.)

### G.2 small_checks.py (this package)

Small-size checks over the Pallas field, written for this package (standard library only, about 1 s; checks (2) and (3) concern e6dcb600's block-mode procedures, which this r does not use, and are kept as checks of the shared code of Appendix E): the half-gcd of 4.4 with the truncated second call against the plain Euclidean algorithm (matrix, degree count, reduced pair; the quotient and return tests never fail on random pairs; every recursive call runs on at most `2k + 1` coefficients), scheme (c) of e6dcb600's block mode (its section 4.5) against schoolbook products modulo `X^(n2 HB) - 1` (windows, a signed bilinear form, `nc = 1, 2, 4`), and the squaring step of e6dcb600's lean stage C (its lemma 4.5) with the cyclic and with the exact `q g` against the remainder of the square. Output of `python3 small_checks.py`:

```
(1) truncated half-gcd: ok (1344 calls; largest operand length / (2k + 1) over the recursive calls = 1.000; quotient and return tests passed)
(2) scheme (c), chunked outer product: ok
(3) squaring step, cyclic and exact q g: ok
```

```python
#!/usr/bin/env python3
"""Small-size checks over the Pallas field of the half-gcd of proof.md 4.4 and of two block-mode procedures of e6dcb600 (its 4.5; not used at r = 6) (standard library only).
  (1) the half-gcd of 4.4 with the truncated second call, against the plain Euclidean algorithm stopped at the same degree sum:
      matrix, degree count and reduced pair; on normal pairs the quotient test and the return test of 4.4 never fail;
      every call runs on at most 2k + 1 coefficients;
  (2) scheme (c) of e6dcb600's block mode (its 4.5; twist and fold, outer transform of n2/nc points, inner transform, fold modulo X^HB - w^o, inverse,
      untwist and accumulate over the chunks) against the schoolbook product reduced modulo X^(n2 HB) - 1, for windows,
      a bilinear form of two signed products, and nc = 1, 2, 4;
  (3) the squaring step of e6dcb600's lean stage C (its lemma 4.5): q = window [m - 1, 2m - 1) of T1 * MU equals floor(A / g), and
      (A mod (X^N' - 1)) - ((q g) mod (X^N' - 1)) agrees with A mod g on [0, m), for N' >= m + 1 (the cyclic q g of scheme (c))
      and for the exact linear q g (scheme (a): no wrap of A is added), for the exponent bit b = 0 and 1.
Run: python3 small_checks.py   (prints ok for each part)."""
import random

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
GEN = 5                                  # 5 generates a subgroup containing the 2^32 * 3 part used here (checked below)


def trim(a):
    while a and a[-1] == 0: a.pop()
    return a


def add(a, b):
    n = max(len(a), len(b)); return trim([((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % P for i in range(n)])


def sub(a, b):
    n = max(len(a), len(b)); return trim([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % P for i in range(n)])


def mul(a, b):
    if not a or not b: return []
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b): out[i + j] = (out[i + j] + x * y) % P
    return trim(out)


def scal(a, c): return trim([x * c % P for x in a])


def divmod_(a, b):
    a = list(a); q = [0] * max(0, len(a) - len(b) + 1); inv = pow(b[-1], P - 2, P)
    for i in range(len(a) - len(b), -1, -1):
        c = a[i + len(b) - 1] * inv % P; q[i] = c
        if c:
            for j, y in enumerate(b): a[i + j] = (a[i + j] - c * y) % P
    return trim(q), trim(a)


def deg(a): return len(a) - 1


def quo_x(a, s): return trim(list(a[s:])) if s > 0 else list(a)


# ---------------------------------------------------------------- (1) the half-gcd with the truncated second call
I2 = ([1], [], [], [1])                  # 2x2 matrices as (r11, r12, r21, r22)


def mmul(A, B):
    return (add(mul(A[0], B[0]), mul(A[1], B[2])), add(mul(A[0], B[1]), mul(A[1], B[3])),
            add(mul(A[2], B[0]), mul(A[3], B[2])), add(mul(A[2], B[1]), mul(A[3], B[3])))


def apply_inv(R, h, a, b):
    s = 1 if h % 2 == 0 else P - 1
    return scal(sub(mul(R[3], a), mul(R[1], b)), s), scal(sub(mul(R[0], b), mul(R[2], a)), s)


STATS = {'maxlen_ratio': 0.0, 'calls': 0, 'abnormal': 0}


def hgcd(a, b, k, want_pair, depth=0):
    """returns (R, h, pair or None); the quotient test and the return test of 4.4 are counted in STATS['abnormal'] if they fail"""
    n = deg(a)
    STATS['calls'] += 1
    if depth > 0: STATS['maxlen_ratio'] = max(STATS['maxlen_ratio'], len(a) / (2 * k + 1))   # every recursive call
    if not b or n - deg(b) > k:
        return I2, 0, ((a, b) if want_pair else None)
    if k <= 4:                                   # base case: plain Euclid while the next quotient fits
        R, h, x, y = I2, 0, a, b
        while y and deg(x) - deg(y) <= k - h:
            q, r = divmod_(x, y)
            if deg(q) != 1: STATS['abnormal'] += 1
            R = mmul(R, (q, [1], [1], [])); h += deg(q); x, y = y, r
        return R, h, ((x, y) if want_pair else None)
    k1 = (k + 1) >> 1
    if 2 * k1 > n: k1 = n >> 1
    s = n - 2 * k1
    R1, h1, _ = hgcd(quo_x(a, s), quo_x(b, s), k1, False, depth + 1)
    c, d = apply_inv(R1, h1, a, b)
    if d and h1 != k1: STATS['abnormal'] += 1          # return test
    if not d or deg(c) - deg(d) > k - h1:
        return R1, h1, ((c, d) if want_pair else None)
    q, e = divmod_(c, d)
    if deg(q) != 1: STATS['abnormal'] += 1              # quotient test
    k3 = k - h1 - deg(q); s3 = deg(d) - 2 * k3
    if s3 > 0:
        R2, h3, _ = hgcd(quo_x(d, s3), quo_x(e, s3), k3, False, depth + 1)
        pair = apply_inv(R2, h3, d, e) if want_pair else None
    else:
        R2, h3, pair = hgcd(d, e, k3, want_pair, depth + 1)
    if (pair[1] if pair else apply_inv(R2, h3, d, e)[1]) and h3 != k3: STATS['abnormal'] += 1
    return mmul(mmul(R1, (q, [1], [1], [])), R2), h1 + deg(q) + h3, pair


def euclid_to(a, b, k):
    R, h, x, y = I2, 0, a, b
    while y and deg(x) - deg(y) <= k - h:
        q, r = divmod_(x, y)
        R = mmul(R, (q, [1], [1], [])); h += deg(q); x, y = y, r
    return R, h, (x, y)


def check_hgcd(rnd):
    for trial in range(40):
        n = rnd.randrange(8, 130)
        a = [rnd.randrange(P) for _ in range(n)] + [1]
        b = [rnd.randrange(P) for _ in range(n - 1)] + [rnd.randrange(1, P)]
        for k in ((n + 1) // 2, rnd.randrange(5, n)):
            R, h, pair = hgcd(a, b, k, True)
            R0, h0, pair0 = euclid_to(a, b, k)
            assert (R, h, pair) == (R0, h0, pair0), (n, k)
            assert h == k, 'a random pair is normal: the degree count equals the parameter'
    assert STATS['abnormal'] == 0
    assert STATS['maxlen_ratio'] <= 1.0 + 1e-12, STATS['maxlen_ratio']
    return STATS


# ---------------------------------------------------------------- (2) scheme (c), chunked outer product modulo Y^n2 - 1, Y = X^HB
def root(n):
    assert (P - 1) % n == 0
    w = pow(GEN, (P - 1) // n, P)
    assert pow(w, n, P) == 1 and all(pow(w, n // f, P) != 1 for f in (2, 3) if n % f == 0)
    return w


def dft(x, w):
    n = len(x); return [sum(x[i] * pow(w, i * k, P) for i in range(n)) % P for k in range(n)]


def blocks(A, HB, n):
    return [[(A[i * HB + t] if i * HB + t < len(A) else 0) for t in range(HB)] for i in range(n)]


def chunked(prods, HB, n2, nc, nout):
    """prods: list of (out, sign, A, B); returns the outputs modulo X^(n2 HB) - 1 (coefficient lists of n2 HB)"""
    NB = 2 * HB; w = root(n2); wNB = root(NB); n3 = n2 // nc; wc = pow(w, nc, P)
    kmax = max(max(-(-len(A) // HB), -(-len(B) // HB)) for _, _, A, B in prods)
    out = [[0] * (n2 * HB) for _ in range(nout)]
    for j in range(nc):
        def chunk(A):
            Ab = blocks(A, HB, -(-len(A) // HB))
            z = [[0] * HB for _ in range(n3)]
            for i, blk_ in enumerate(Ab):                 # twist by w^(j i) and fold i modulo n3
                f = pow(w, j * i, P)
                for t in range(HB): z[i % n3][t] = (z[i % n3][t] + f * blk_[t]) % P
            cols = [dft([z[u][t] for u in range(n3)], wc) for t in range(HB)]   # outer transform across the rows
            return [[cols[t][u] for t in range(HB)] for u in range(n3)]
        CA = [(o, sg, chunk(A), chunk(B)) for o, sg, A, B in prods]
        res = [[[0] * HB for _ in range(n3)] for _ in range(nout)]
        for u in range(n3):
            wo = pow(w, j + nc * u, P)
            acc = [[0] * NB for _ in range(nout)]
            for o, sg, ca, cb in CA:                     # inner transform, pointwise product (signed), summed
                fa = dft(ca[u] + [0] * HB, wNB); fb = dft(cb[u] + [0] * HB, wNB)
                for t in range(NB): acc[o][t] = (acc[o][t] + sg * fa[t] * fb[t]) % P
            for o in range(nout):
                c = dft(acc[o], pow(wNB, P - 2, P)); invNB = pow(NB, P - 2, P)
                c = [x * invNB % P for x in c]
                res[o][u] = [(c[t] + wo * c[t + HB]) % P for t in range(HB)]   # fold modulo X^HB - w^o
        for o in range(nout):
            cols = [dft([res[o][u][t] for u in range(n3)], pow(wc, P - 2, P)) for t in range(HB)]  # inverse outer transform (times n3)
            for s in range(n2):                          # untwist and accumulate: piece s += w^(-j s) z_(s mod n3)
                f = pow(w, (n2 - (j * s) % n2) % n2, P) * pow(n2, P - 2, P) % P
                for t in range(HB): out[o][s * HB + t] = (out[o][s * HB + t] + f * cols[t][s % n3]) % P
    return out


def cyc(a, L):
    out = [0] * L
    for i, x in enumerate(a): out[i % L] = (out[i % L] + x) % P
    return out


def check_chunked(rnd):
    HB = 4
    for n2 in (4, 6, 8, 12):
        for nc in (1, 2, 4):
            if n2 % nc or (n2 // nc) % 1: continue
            if not ((n2 // nc) & (n2 // nc - 1) == 0 or ((n2 // nc) % 3 == 0 and ((n2 // nc // 3) & (n2 // nc // 3 - 1)) == 0)): continue
            L = n2 * HB
            A = [rnd.randrange(P) for _ in range(rnd.randrange(HB + 1, L))]; B = [rnd.randrange(P) for _ in range(rnd.randrange(HB + 1, L))]
            C = [rnd.randrange(P) for _ in range(rnd.randrange(1, L))]; D = [rnd.randrange(P) for _ in range(rnd.randrange(HB + 1, L))]
            got = chunked([(0, 1, A, B), (0, P - 1, C, D), (1, 1, A, D)], HB, n2, nc, 2)
            want0 = cyc(sub(mul(A, B), mul(C, D)), L); want1 = cyc(mul(A, D), L)
            assert got[0] == want0 and got[1] == want1, (n2, nc)
            ws = rnd.randrange(0, L // 2); ln = rnd.randrange(1, L - ws)        # a window of the cyclic result
            assert got[0][ws:ws + ln] == want0[ws:ws + ln]
    return True


# ---------------------------------------------------------------- (3) the squaring step (lemma 4.5)
def check_step(rnd):
    HB = 4
    for m in (9, 13, 22, 30):
        g = [rnd.randrange(P) for _ in range(m)] + [1]
        MU, _ = divmod_([0] * (2 * m - 1) + [1], g)               # floor(X^(2m-1) / g)
        for b in (0, 1):
            R = [rnd.randrange(P) for _ in range(m)]
            A = mul(R, R)
            if b: A = [0] + A                                       # S^b R^2: the offset of the square by one coefficient
            A = A + [0] * (2 * m - len(A))
            T1 = trim(list(A[m:2 * m])); A0 = trim(list(A[:m]))
            q = trim(list(mul(T1, MU)[m - 1:2 * m - 1]))           # window [m - 1, 2m - 1)
            qq, rem = divmod_(trim(list(A)), g)
            assert q == qq, (m, b)
            # exact linear q g (scheme (a)): A[0..m) - (q g)[0..m) is the remainder
            qg = mul(q, g) + [0] * (2 * m)
            r_exact = trim([(A[i] - qg[i]) % P for i in range(m)])
            assert r_exact == rem
            # cyclic q g modulo X^N' - 1 (scheme (c)), N' = n2' HB >= m + 1, with the wrap of A added to Fn
            n2p = 1
            while n2p * HB < m + 1: n2p *= 2
            Np = n2p * HB
            Fn = list(A[:m]) + [0] * (Np - m)
            for i in range(2 * m - Np):                              # Fn[i] += T1[i + N' - m]
                if i < m: Fn[i] = (Fn[i] + A[i + Np]) % P
            qgc = chunked([(0, 1, q, g)], HB, n2p, 1, 1)[0] if len(q) > HB and len(g) > HB else cyc(mul(q, g), Np)
            r_cyc = trim([(Fn[i] - qgc[i]) % P for i in range(m)])
            assert r_cyc == rem, (m, b)
    return True


if __name__ == '__main__':
    rnd = random.Random(20261017)
    st = check_hgcd(rnd)
    print('(1) truncated half-gcd: ok (%d calls; largest operand length / (2k + 1) over the recursive calls = %.3f; quotient and return tests passed)' % (st['calls'], st['maxlen_ratio']))
    print('(2) scheme (c), chunked outer product: ok' if check_chunked(rnd) else 'FAIL')
    print('(3) squaring step, cyclic and exact q g: ok' if check_step(rnd) else 'FAIL')
```
