# Orchard Poseidon, r = 8: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, half-gcd, one centre

## 1. Claim

Target: `poseidon-orchard-r8-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, eight partial rounds 4, 5, 6, 7, 8, 9, 10 and 11, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is an algorithm (sections 2-4) with a worst-case operation count (sections 6-7) and a success probability derived from the score-critical premise `H-ONE` (section 9.1), a statement about the fraction of centres at which the fixed digest polynomial has between 1 and 16 usable roots; section 9.2 derives the success probability from it.

* The algorithm: draw a centre `c` uniformly from `F_p` from fresh random words, build the odd part `g_c` of the line polynomial by evaluation and one inverse transform, compute `G = gcd(g_c, S^((p-1)/2) - 1)` by a power-mod and a half-gcd, and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` in at most `Z = 64` rounds, take its square root, map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39009`: a lower bound for the probability, over the algorithm's fresh random words, that the centre yields a verified collision on the fixed target: `P >= q - eps_coin - eps_iso - eps_O1` with `q = 0.3901` (the premise `H-ONE`, section 9.1), `K = 1`, `eps_iso < 2^-48`, `eps_coin < 2^-128`, `eps_O1 < 2^-189` (section 9.2; `eps_O1` bounds the probability that `g_c` has a root on the evaluation set of stage C, 4.3V(d)). The exact value is `0.390099999999997628` (`eps_O1` is below its 18th decimal).
* `time_log2 = 41.85470` in target-compression units (`C(8) = 384` primitive operations per unit): the worst-case operation count, derived in section 6 as `T_fixed + K * T_trial` with `K = 1` and the trial charged in full (including stage E at its cap of `Z` rounds at degree `DMAX`), `N_max = 1,527,039,469,464,147` operations, `log2(N_max / 384) = 41.85469627461552`, rounded up at five decimals. Stage C runs in the value domain on cosets (section 4.3V: the recurrence, its exactness proof, the finite operation count expanded step by step in Appendix E, and its allocation sequence). The offline derivation of the constants (section 6.2) is bounded by 1,000,000 operations; that bound is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 39.132` (`602,370,547,468` bytes, section 7).
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; `65` words at most (section 4.1.1), and a draw (one word) costs 31 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^14`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Prior entries: this entry is the same attack as our r = 8 entry c7a238b5 (the same algorithm, line and experiments), with the exact accounting of sections 4.2, 4.4, 6.3, 7 and Appendix E; it is the r = 8 version of our r = 7 algebraic entry 05a41d88 (the same algorithm, ledger method, premise structure and evidence design). The ruling on 05a41d88 (not_evaluable on the experiments lane) is answered here in the same way: the organizer experiments `line-ladder-w6`, `-w8`, `-w10` and `-w12` on the antipodal line pairs of this construction at r = 8 (10.2), the computations of Grok job 136 and their re-run on the deployed constants and the attack line (10.3), and the measurement of the Euclidean sequences on the sibling targets (10.5). Our filed r = 8 one-centre entry c69ae3de is our r = 8 entry 7d53191b with one centre in place of two (`K = 1`) and the premise `H-ONE` of our r = 13 entry 17a75731 in place of `H-GEOM-w2`. This entry is c69ae3de with stage C computed in the value domain on cosets (section 4.3V, the method of bradcush 4bcabff8); the rows C, B and plan_invN misses of the ledger and the sizes of the arrays `g` and `R` change, nothing else.
* Declared heuristic (claim.json): `H-ONE` only (score-critical, section 9.1), a statement about probability. The costs are the declared cost model of this entry, not heuristics: the charging rules of section 4.2, the register file of 18 words, the half-gcd of stage D charged for every remainder sequence (section 6.3), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation. Everything else is proved or counted here: the line construction, the degree of `F`, the odd-part reduction, the collision criterion (sections 2, 3, 5), the success bound from the premise (section 9.2), the isolation lemma (section 9.4), the cap rules and every operation count (sections 4, 6, 7).
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

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8, 9, 10, 11 (partial), 60, 61, 62, 63 (full) put fourteen S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^14 = D = 6,103,515,625`. The leading coefficient is obtained by
propagating leading coefficients through the fourteen layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used:
`f_D(0) = 0x183f2fcd6b7f01c5336d69339c25f14df8d1fa36a4d8cc1d63c4824f83feea20`
(computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 3,051,757,812`, `g_c` has degree exactly `m` and
leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives `s = 0` and is not a root of `S^((p-1)/2) - 1`).
`G` divides `S^((p-1)/2) - 1`, which is squarefree, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. `H = 3,221,225,472 = 3 * 2^30` divides `p - 1` (`p - 1 = 2^32 * 3 * q`), and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity
and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`. One inverse transform of size `H` returns the
coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). The `2H = 6,442,450,944` evaluations of `F` are each charged as
one target-compression unit (`C(8) = 384` operations), although a line evaluation (affine start, the remaining rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation.
The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 zeta^i)`, two multiplications for the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, one store with its address operation,
the loop control, the update of the row counter `row = k mod 3` (increment, comparison, branch, assignment; no modulo instruction), and the executed shifts, masks, ors and loop control of the bit-reversed index `layout_index_r`, which are counted inside that function) is charged on top.



## 4. The algorithm (at most K centres, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   twiddle table (once)
setup:  the line (line_setup) (once)
for t = 1, 2, ..., K:                                  [the test t <= K is made at the start of every trial; no other exit except success]
  A  c := a uniform element of F_p from one fresh random word (section 4.1.1)
  B  g := monic g_c, by section 3 (6,442,450,944 evaluations + one inverse NTT of size 3,221,225,472 + the test that the leading coefficient is nonzero + normalisation by the leading coefficient)
  C  R := S^((p-1)/2) mod g           (left-to-right square-and-multiply on the exponent, base S, in the value domain on cosets, section 4.3V; 224 modular squarings, 45 of the steps also multiply by S)
  D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4)
  E  if deg G = 0 or deg G > DMAX: the trial ends, next t.   Otherwise isolate a root S of G (section 4.1.2).  If none is isolated within Z rounds: the trial ends, next t.
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (384 operations each) are equal and the pairs differ -> go to H; otherwise the trial ends, next t
H  output: the two pairs (and the digest and the centre) are converted to canonical form and encoded as 64 hexadecimal digits each.
   If t > K was reached the algorithm fails (the failure event, probability bounded in section 9).
```
The exponent `E = (p-1)/2` has bit length 254 and Hamming weight 46: `E = 2^29 * 2^224 + E'` with `E' < 2^224` of Hamming weight 45 (the 31 bits after the leading one are zero). The algorithm starts from the monomial `S^v` with `v = 2^29` (a multiple of `h = 2^24`, section 4.3V; this absorbs the top 30 bits of `E`), and the squaring loop of stage C has 224 steps (one per bit of `E'`), of which 45 also multiply by `S`.

Stopping rule over the `K` centres. The loop bound `K = 1` is a constant of the algorithm. A trial is run to its end whatever its outcome; the claim charges every trial at its maximum (stages E to G at their worst case, section 6), so a trial that fails early is paid for at the full-trial price, never less. Stage E is entered only when `1 <= deg G <= DMAX`, and at most `Z` rounds are made in it. The algorithm has no other loop whose length depends on data: the loops of stages B to D have lengths fixed by `m` and the exponent (sections 4.3V, 4.4), the powering has a fixed number of steps, and the half-gcd has a fixed recursion: 25 levels of recursion in `hgcd` (the parameter `k` starts at `floor((n+1)/2) = 1,525,878,906` and is halved, rounded up, until it is at most 96) and at most 25 repetitions of the outer loop of the Euclid driver (each repetition removes more than half of the degree, from 3,051,757,812 to at most 192). Hence, with stage D charged for every remainder sequence (section 6.3), the number of executed operations is at most `N_max` for every coin sequence and every target value, the algorithm cannot stop early except by success or by failure after `K` trials, and nothing in the claim depends on a run being lucky.

#### 4.1.1 Coins

The only randomness of the algorithm is the cost model's random-word primitive (fresh independent algorithmic coins): an independent uniform 256-bit word, each use returning a fresh word, uniform on `0..2^256-1` and independent of everything else, and costing one operation. **Probability space:** every probability of section 9 is over these words. A draw is one fresh word `y`; the draw is `x = y mod p`, computed by at most three steps `if y >= p then y := y - p` (`y < 2^256 < 4p`, so three steps bring `y` below `p`). Write `2^256 = 3p + s0` with `0 < s0 < p`: the residues below `s0` have exactly four preimages below `2^256` and the other `S3 = p - s0 = 4p - 2^256` residues have exactly three, so `P[x = z] = 4/2^256` or `3/2^256` for every residue `z`, every residue has probability at least `3/2^256`, and all but `S3` residues have probability `4/2^256`. The draw is within statistical distance `S3 (1/p - 3/2^256) = 1.574e-39 (2^-128.90) < 2^-128` of uniform on `F_p`. A draw costs 31 operations: for the word one random-word operation, one load, one store into the cell `y` and three control operations (two addresses, the increment of the word index), 6 in all; for the reduction three steps each of a comparison, a conditional branch and a field subtraction (9 operations), with the loop control of 3 per iteration and 2 on exit (11); one Montgomery conversion of `x` (1); the entry of the call (2) and the address of `y` (2). Draws are made once per trial for the centre and once per isolation round for the shift: at most `K (1 + Z) = 65` draws, `65` words. No word is used twice, and the number of words used before a draw depends only on earlier words, so each draw is independent of the earlier course of the algorithm.

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
* the reduced permutation evaluations of stage B: 384 each (section 3), instead of their (smaller) expanded arithmetic. Nothing else is charged as a unit.
* Montgomery conversions: every conversion of an integer to or from the internal representation (for example the word converted in a draw, the exponent in the Taylor shift, the constants of the twiddle setup, the inputs of the two reference hashes and the six conversions of the output in stage H) is one Montgomery multiplication and is charged as one field multiplication. The constants of the permutation are stored in Montgomery form and need no conversion.
* output (stages H and I): in stage H the answer (two pairs, the digest and the centre) is converted out of the Montgomery representation (6 multiplications) and encoded as 64 hexadecimal digits each at 12 operations per digit and 5 per call. Stage I charges everything after the last step of the algorithm: the formatting of the report, 400 operations per byte of a buffer of 8,192 bytes (a decimal digit costs at most 44 operations, a copied byte at most 10, a conversion at most 150), 20,000 operations of report loops, 100 for the entry and the length check, one write system call at `10000 + 8 * 8,192` and one exit system call at 10,000 (a system call is 10,000 operations plus 8 per byte copied), and the bookkeeping of the stage (2 * 1,000).
* allocation: every array is taken from one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes (`need` bytes), and `need` decides the allocator. A block of more than 2^21 = 2,097,152 bytes comes from the pool, one region with two ends: its blocks follow each other in address order, each with a header (size, size of the previous block, in-use flag), no two free blocks are adjacent, and the unused middle between the two ends is one free block. Each allocation statement of the program uses one end of the pool, a constant of the statement and of the parity of the depth of the recursion of `hgcd` in which it is executed (the depth is 0 outside `hgcd`, 1 in the first call from the Euclid driver, and one more in each nested call): the statements marked `# pool:H` in the listing of Appendix E (the block array of stage B, the output `c` of `apply_inv`) use the high end at every depth; the statements marked `# pool:H0` (the padded divisor `bp` of a division, the entries of the matrix products) use it at even depth only; the statements marked `# pool:H1` (the row scratch of the products of a division, its array `ar`, the outputs of `mul_add_q2`, the second row scratch and the output `d` of `apply_inv`, the quotient and remainder arrays of a node of the half-gcd) use it at odd depth only; every other statement, and each marked statement at the other parity, uses the low end. A low request walks the blocks upward from the bottom of the pool, a high request downward from the top (the two sizes in the header give both neighbours, so the two walks are the same code mirrored); it takes the first free block with at least `need` bytes (the unused middle is the last block of either walk) and cuts the block from the side nearest its own end, and the rest stays a free block when it is at least 128 bytes (else it belongs to the block); a free merges the block with a free neighbour on either side, the unused middle included, the same code for both ends. Since no two free blocks are adjacent and a walk ends at the middle, a walk examines at most 2 P + 1 blocks, P the live blocks on its side of the pool, and one block examined is 13 operations (two comparisons with branches, two loads, the advance). A block of at most 2^21 bytes comes from the slab classes: the class `j` is the least `j >= 7` with `2^j >= need`, a slot is `2^j` bytes; a request takes the first slot of the free list of its class, else a new slot from the end of the slab area, and writes the class and the in-use flag into the header; a free puts the slot on the free list of its class. The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows: a request of the pool 97 operations besides the walk (the statement that calls the allocator, which chooses the end from the marker of the statement and the parity of the depth, at most 6 operations of the 97, the set-up, the split, the header stores, and a flat 64 for the statistics) and 13 per block examined, a request of a slab class at most `126` (the statement that calls the allocator, the class `j` by a binary search over 7..63 in 6 steps of 6 operations, the pop or the bump, the two header stores, and a flat 64 for the statistics), a free 81 for a slab block and at most 105 for a pool block (a free tests the size of the block to choose the allocator, in place of the test for a null pointer, which the program never needs). Every allocation of the walk is charged `1 + 120 + 13 (2 L + 1)` with L the live blocks at that point, which covers the pool (P <= L, the 97 operations and 13 per block examined) and the slab path (at most `126 <= 1 + 120 + 13` operations), and every free 105 (550 per allocation and 105 per free at 16 live blocks in stage E). The memory of both allocators is the arena of section 7.
* trial loop: the test of the trial counter, its increment and the bookkeeping of the trial, at most 12 operations per trial, are `TRIAL_EXTRA` = 12 in the ledger; the loop test and update of stage A are 5.
* the offline derivation of the constants is charged in section 6.2.



### 4.3V Stage C in the value domain, on cosets of a subgroup of order 2^24 (the method of bradcush 4bcabff8)

This entry is our filed r = 8 one-centre entry c69ae3de with one change of program: stage C, the powering `R = S^E mod g` with `E = (p-1)/2` and `m = deg g = 3,051,757,812`, is computed in the value domain on cosets (the low-h coset powering of bradcush 4bcabff8) instead of by coefficient-domain squarings. Stages A, B, D, E, F, G, H, I, the line, the premise and the evidence are those of c69ae3de. `R` enters stage D in coefficient form, equal to the coefficient-domain `S^E mod g` (part (d) below proves this; no premise is involved). Three ledger rows change (section 6): row C (`446,444,428,530,905` in place of the `1,056,612,093,561,642` of c69ae3de), row B (`-186`: stage B no longer allocates an array `F`, because `R` leaves stage C in an array of its own), and the plan_invN misses (`-3,089`: 29 distinct plan sizes in place of 30). The array of `g` and the array of `R` have `n1 = 3,053,453,312` slots in place of `m + 1` and `m`, so the live set of stages A to D grows by `108,511,936` bytes; `memory_log2_bytes = 39.132` is unchanged (section 7, part (f) below).

#### (a) Dimensions, point sets and the certificate (closed form; no premise)

`h = 2^24 = 16,777,216`; `H` is the subgroup of order `h` of `F_p^*` and `omega` a primitive `h`-th root of unity. `K = ceil((m + 1) / h) = 182`, `n1 = K h = 3,053,453,312` (`n1 - (m + 1) = 1,695,499`). `u_k = 5^k` and `C_k = u_k H` for `k = 0, ..., 2K - 1 = 363`; `O1 = C_0 u ... u C_(K-1)`, `O2 = C_K u ... u C_(2K-1)`. `z = 5^h`; on `C_k` every point satisfies `X^h = u_k^h = z^k` (the node of the coset). `M1(X) = prod_(k < K) (X^h - z^k)` is the monic polynomial of degree `n1` whose roots are exactly the points of `O1`; on `C_j` it is the constant `mu_j = prod_(k < K) (z^j - z^k)`, nonzero for `j >= K`.

Three facts are used, each verified directly:
1. `h | p - 1`: `v2(p - 1) = 32 >= 24`. So `H` and `omega` exist and the size-`h` cyclic transform (one row of the radix passes of section 4.2 at `a = 24`) is exact.
2. `z^d != 1` for `1 <= d <= 2K - 1 = 363`, checked by 363 modular exponentiations (the program computes them in its table setup; part (e)). Hence the `2K` nodes `z^0, ..., z^(2K-1)` are distinct (`z^j = z^k` iff `z^(j-k) = 1`), the `2K` cosets are disjoint, `|O1| = |O2| = n1`, every `mu_j` (`j >= K`) is nonzero, and the Lagrange interpolation of part (c) is invertible. (The direct check is the certificate; no statement about the order of 5 is used.)
3. `n1 >= m + 1`, so `2 n1 >= 2m + 1`: a polynomial of degree at most `m` is determined by its values on `O1` (or on `O2`), and the degree bounds of part (d) hold.

#### (b) The representation: coefficient rows and the inner transform

For a polynomial `P` of degree `< n1` write its coefficient index as `j = j0 + h j1` (`0 <= j0 < h`, `0 <= j1 < K`) and let `P_j0(y) = sum_(j1 < K) p_(j0 + h j1) y^j1` be its `h` coefficient rows (polynomials of degree `< K`). At the point `u_k omega^i` of `C_k`,

`P(u_k omega^i) = sum_(j0 < h) omega^(i j0) [u_k^j0 P_j0(z^k)]`,

so the `h` values of `P` on `C_k` are the size-`h` cyclic transform of the vector `(u_k^j0 P_j0(z^k))_j0`, and the inverse transform of the values on `C_k`, divided entrywise by `u_k^j0`, returns the `h` numbers `P_j0(z^k)`. The values of `P` on `O1` are therefore in exact linear correspondence with the `K` values `P_j0(z^k)`, `k < K`, of each of the `h` row polynomials at `K` distinct nodes, hence (Lagrange) with the rows themselves, hence with the coefficients of `P`. Every map in this chain is an exact linear bijection; nothing is approximated.

#### (c) The extension (change of point set): `O1 -> O2` and `O2 -> O1`

Input: the values of a polynomial `P` of degree `< n1` on `O1`. (1) `K` inverse inner transforms (one per coset, in place) and the scaling by `u_k^(-j0)` give `a_(j0,k) = P_j0(z^k)`, `k < K`. (2) For each inner position `j0`, `P_j0` has degree `< K`, so its values at the nodes of `O2` are its Lagrange interpolant from the `K` nodes of `O1`: with `w(y) = prod_(k < K) (y - z^k)`,

`P_j0(z^(K+t)) = sum_(k < K) a_(j0,k) w(z^(K+t)) / ((z^(K+t) - z^k) w'(z^k)) = mu_(K+t) sum_(k < K) [a_(j0,k) z^(-k) / w'(z^k)] c_(K+t-k)`, `c_d = 1 / (z^d - 1)` (`1 <= d <= 2K - 1`),

a linear convolution over the coset index `k` with the fixed kernel `c`, whose `2K - 1` entries are nonzero by fact 2. It is computed as one cyclic convolution of length `Lx = 384` (the smallest `2^a` or `3 2^a` that is at least `2K = 364`, so no wrap reaches the `K` used outputs) with the spectrum of the kernel stored once per trial, by the row kernels of section 4.2 (the forward passes, the fused pass with the pointwise product by the stored spectrum, the inverse passes). The `h` positions are processed in `h / 1024 = 16,384` groups of `VCNT = 1,024` positions: a group buffer holds one row per position (of `Lmax = 768` elements, the longest convolution of the stage); the `K` input rows of a group are copied in with their running factors `z^(-k) / w'(z^k)` (per element a load, the multiplication by the factor, the multiplication of the factor by its step, a store and the strided address: 7 operations), the `1,024` convolutions run in the buffer, and the `K` output rows are copied out with the factors `mu_(K+t)` (7 per element). (3) The scaling by `u_(K+t)^j0` and `K` forward inner transforms give the values of `P` on `O2`. The map `O2 -> O1` is the same procedure with the roles of the two node sets exchanged (the kernel `1 / (z^(k-K-t) - 1)` is the same vector `c` read backwards). The extension is exact: it composes exact inner transforms with the exact Lagrange interpolation of polynomials of degree `< K` from `K` distinct nodes. One extension, its `2K` inner transforms included, is `944,967,161,528` operations (Appendix E prints it).

#### (d) The recurrence (Montgomery form on cosets) and its exactness

The Montgomery form of a residue `A` (`deg A < m`) is `A~ = A M1 mod g` (degree `< m`). The stage keeps two arrays of `n1` values: `R1` = the values on `O1` and `R2` = the values on `O2` of the current `A~`, or of `X A~` (degree `<= m`) after a multiplication by `X`; both are determined by either array (fact 3). Two fixed arrays hold `G1 = -1/g` on `O1` and `G2 = g` on `O2`.

*One squaring step* (one bit of the exponent), from `T = A~^2` (`deg T <= 2m`):
(i) `R1 := R1^2 G1` pointwise: the values on `O1` of the polynomial `U` of degree `< n1` with `U = -T/g` on `O1` (`U` exists and is unique by fact 3: it is the interpolant of these `n1` values).
(ii) the extension `O1 -> O2` of `U` (part (c)), in place in `R1`.
(iii) `R2 := (R2^2 + R1 G2) / mu_k` pointwise (`mu_k` is a constant per coset): the values on `O2` of `S' = (T + U g) / M1`. `S'` is a polynomial: `T + U g` vanishes at every point of `O1`, that is at the `n1` distinct roots of `M1`, so `M1 | T + U g`. `deg S' <= max(2m, n1 - 1 + m) - n1 <= m - 1` by fact 3. And `S' M1 = T + U g`, so `S' = T M1^(-1) mod g = (A^2)~`: the Montgomery form of `A^2 mod g`, of degree `< m`. If the exponent bit is 1, `R2` is also multiplied pointwise by the coordinate of the point (`u_k omega^i`): the values of `X S'`, degree `<= m`.
(iv) the extension `O2 -> O1` from `R2` into `R1` (the polynomial has degree `<= m < n1`, so its values on `O2` determine it and the extension is exact).

*Start.* `A~_0 = X^v M1 mod g` with `v = 2^29` (a multiple of `h`), the Montgomery form of `X^v`. Since `deg (X^v M1) = v + n1`, `A~_0 = X^v M1 - q g` with `q = floor(X^v M1 / g)` of `ell = v + n1 - m + 1 = 538,566,413` coefficients. `q` is computed in the coefficient domain by the reversed Newton identity (as in the division of 4.4: the reciprocal of `rev(g)` modulo `X^ell` by 30 Newton levels `l -> min(2 l, ell)`, products by the transforms of 4.2, then one product with `rev(X^v M1) mod X^ell`, whose only nonzero coefficients are the `Kq = 33` coefficients of `M1` at the multiples of `h` that fall below `ell`). On `O2`, `X^v = u_k^v` (`omega^(i v) = 1` because `h | v`) and `M1 = mu_k`, so `R2 := u_k^v mu_k - q G2` with `q` evaluated on `O2` through its `Kq` coefficient rows (the chirp evaluation of part (e), `K` inner transforms), and `R1` is the extension `O2 -> O1` of `R2`.

*Steps.* `E = 2^29 2^224 + E'` with `E' < 2^224` of Hamming weight 45 (section 4.1), so `X^E = (X^v)^(2^224) X^E'` and the loop makes 224 squaring steps, 45 of them with the multiplication by `X`. By induction on the steps the invariant holds after every step, and after the last one `A~ = X^E M1 mod g`.

*End.* `R1 := R1 G1`, the extension `O1 -> O2`, `R2 := (R2 + R1 G2) / mu_k`: with `U = -A~/g` on `O1` this is `(A~ + U g) / M1`, a polynomial of degree `<= max(m, n1 + m - 1) - n1 <= m - 1`, equal to `A~ M1^(-1) mod g = X^E mod g = R`. So `R2` holds the values of `R` on `O2`. Finally `R` and `g` (whose array holds its values on `O2` during the loop) are returned to coefficient form in place: `K` inverse inner transforms and the scalings `u_k^(-j0)` give `R_j0(z^k)` for `k = K, ..., 2K - 1`, and each row `R_j0` (degree `< K`) is recovered from its `K` values at these distinct nodes by the Lagrange formula in two cyclic convolutions of length `Lx` per inner position (the partial-fraction weights `a_(j0,k) z^(-k) / w2'(z^k)` convolved with the kernel `c`, then the product with the coefficient vector of `w2(y) = prod_(K <= k < 2K) (y - z^k)`, the spectra of both stored once per trial).

*The one data-dependent exit.* `G1 = -1/g` on `O1` is formed by Montgomery's batch inversion per coset; if a prefix product is zero, `g` has a root in `O1` and the trial ends (it is charged in full as every trial is). For a fixed point `S0 != 0`, the number of centres `c` with `g_c(S0) = 0` is at most `D - 1 = 5^14 - 1`: `2 t g_c(t^2) = F(c + t) - F(c - t)` for `t^2 = S0` (over `F_(p^2)` if `S0` is not a square), and `c -> F(c + t) - F(c - t)` is a nonzero polynomial of degree `D - 1` in `c` (its `c^(D-1)` coefficient is `2 D t f_D(0) != 0`, since `p` does not divide `D` and `t != 0`). So for a uniform centre `P[g_c has a root in O1] <= n1 (D - 1) / p = eps_O1 < 2^-189` (exactly `6.438e-58`); section 9.2 subtracts it.

*Exactness.* Every step above is an identity between polynomials evaluated at points of `O1 u O2`, an exact size-`h` transform at a primitive `h`-th root of unity, or an exact Lagrange interpolation from `K` distinct nodes; the only hypotheses used are facts 1 to 3 of part (a), certified for `h = 2^24`, `K = 182`. Hence the coefficient array that enters stage D is the coefficient-domain `S^E mod g` of c69ae3de, and stage D, the gcd degree `k(c)`, the premise `H-ONE` and the success bound are unchanged. This is a proof for the full dimensions, not an extrapolation. Our implementation of the same recurrence was also checked against an independent coefficient-domain `X^E mod g` (schoolbook products and monic division over the Pallas field) at two small regimes, `K = 3, h = 32` and `K = 12, h = 16`, with equal results; that check tests the code of the recurrence, which does not depend on `h` or `K` beyond facts 1 to 3, and is not part of the argument.

#### (e) The operation count: a finite recurrence, expanded in Appendix E

Appendix E (`stage_cd.py`, function `powx_vd`) expands row C from the dimensions of part (a) with the kernel charges of section 4.2 and prints the operations of each step; the values are:

| step of stage C (one trial) | operations |
|---|---:|
| (0) the plans of the transforms (`h = 2^24`; `Lx = 384`, `Le = 768`, `Lq = 256`), the `30 K = 5,460` per-trial constants (`u_k`, `1/u_k`, the copy factors, `1/mu_k`, `u_k^v mu_k`, `1/w'(z^k)`, `mu_(K+t)`, the chirp scales, the coefficients of `w2`; each two inversions and 60 operations), the table of `omega^i`, the five kernel spectra (the extension kernel at `Lx`, the chirp of the evaluation of `q` at `Lq`, the chirp of the interpolation at `Lx`, the coefficients of `w2` at `Lx`, the chirp of the evaluation of `g` at the `2K` nodes at `Le`; each entry one inversion and 20 operations, then one forward transform), the first five allocations of the stage and the zero fill of the `n1 - (m + 1)` slots of `g` above its coefficients | 205,467,725 |
| (1) the Barrett start: the reciprocal of `rev(g)` modulo `X^ell` (30 Newton levels, two products per level by `conv_mulc_otf` of 4.2), the product giving `q` (`ell = 538,566,413` coefficients), its reversal; the allocations and frees of `G`, `M`, `Y` and `Tt` | 2,221,035,380,510 |
| (2) `g` on `O1` and on `O2`: the chirp evaluation of its `K` coefficient rows at the `2K` nodes (one convolution of length `Le = 768` per inner position, `16,384` groups of `1,024`), `2K` forward inner transforms | 1,348,265,786,932 |
| (3) `A~_0` on `O2`: `q` at the `K` nodes of `O2` through its `Kq = 33` rows (one convolution of length `Lq = 256` per position), `K` forward inner transforms, the pointwise pass `u_k^v mu_k - q G2` (8 operations per element with its loads, stores and addresses) | 511,243,164,774 |
| (4) `A~_0` on `O1`: one extension `O2 -> O1` | 944,967,161,528 |
| (5) `-1/g` on `O1`: `K` batch inversions (per coset the prefix products, one inversion with its zero test, the backward pass) | 45,038,923,677 |
| (6) the 224 squaring steps: 179 steps of `1,953,293,487,312` (the pointwise pass (i) at 8 per element, one extension, the pointwise pass (iii) at 12 per element, one extension, 20 for the step) and 45 steps of `1,965,507,300,560` (the pass (iii) at 16 per element: `omega^i` loaded and multiplied by `u_k`, the product by the coordinate) | 438,087,362,754,048 |
| (7) leaving the Montgomery form: one pointwise pass (7 per element), one extension `O1 -> O2`, one pointwise pass (11 per element); the frees of `R1` and `G1` | 1,002,219,419,350 |
| (8) `R` and `g` back to coefficient form: for each, `K` inverse inner transforms and one interpolation (`1,142,045,235,272` each); the frees of the transform row, the group buffer and the tables | 2,284,090,471,361 |
| stage bookkeeping | 1,000 |
| **row C** | **446,444,428,530,905** |

A pointwise pass over `O1` or `O2` is `K` cosets of `h` elements, charged per element as stated, with 14 operations per coset (its constants and addresses) and the loop control of section 4.2 (eight elements per pass). An inner transform is one row of the radix passes of 4.2 at `a = 24` (forward: all passes; inverse: all passes but the first, which is fused with the copy that precedes it), plus 10 for the call (the coset address, the plan and twiddle arguments, call and return). The group copies and the convolutions of a group are charged as in part (c); each group adds 20 (its position offset, the buffer and table addresses, the calls). Every allocation is charged `1 + 120 + 13 (2 L + 1)` with `L` the live blocks and every free 105, as in 4.2. The same generator, run from the package's source on a second machine of ours (the Luna server, order S034, 2026-10-19 01:08 MDT), printed the same row C, `446,444,428,530,905`, at `r = 8`, `h = 2^24`, `K = 182`.

#### (f) Memory: the allocation sequence of stage C on the two-ended pool

The arena of section 7 is the capacity of the allocator of 4.2 on the allocation sequence of one trial, so the sequence of stage C is given here in the order of the program (Appendix E prints this trace, `stage_c_trace`). After init, A and B the low end of the pool holds the twiddle table and `g` (`132,070,244,480` bytes) and the high end is empty. The arrays of stage C (a block is 64 + 32 slots rounded up to 64 bytes; L = the low end, H = the high end, the statements marked `# pool:H`):

| event | array | slots | bytes | end | live bytes after | low end | high end |
|---|---|---:|---:|---|---:|---:|---:|
| alloc | `R` (the values on `O2`, then `R` in coefficient form for stage D; the first allocation of the stage) | 3,053,453,312 | 97,710,506,048 | L | 229,780,750,528 | 229,780,750,528 | 0 |
| alloc | the tables (constants, `omega^i`, the kernel spectra) | 16,784,852 | 537,115,328 | L | 230,317,865,856 | 230,317,865,856 | 0 |
| alloc | the group buffer (`1,024` rows of `768`) | 786,432 | 25,165,888 | L | 230,343,031,744 | 230,343,031,744 | 0 |
| alloc | the transform row of the length-768 convolutions (slab class) | 768 | 24,640 | slab | 230,343,056,384 | 230,343,031,744 | 0 |
| alloc | `R1` (`q`, then the values on `O1`) | 3,053,453,312 | 97,710,506,048 | L | 328,053,562,432 | 328,053,537,792 | 0 |
| alloc | `G` (the reciprocal) | 538,566,413 | 17,234,125,312 | H | 345,287,687,744 | 328,053,537,792 | 17,234,125,312 |
| alloc | `M` (the Newton scratch) | 538,566,413 | 17,234,125,312 | H | 362,521,813,056 | 328,053,537,792 | 34,468,250,624 |
| alloc | `Y` (the transform array of the Newton products) | 1,610,612,736 | 51,539,607,616 | H | 414,061,420,672 | 328,053,537,792 | 86,007,858,240 |
| free | `Y` | 1,610,612,736 | 51,539,607,616 | | 362,521,813,056 | 328,053,537,792 | 34,468,250,624 |
| free | `G` | 538,566,413 | 17,234,125,312 | | 345,287,687,744 | 328,053,537,792 | 34,468,250,624 |
| alloc | `Tt` (the transform array of the product giving `q`) | 1,610,612,736 | 51,539,607,616 | H | 396,827,295,360 | 328,053,537,792 | 86,007,858,240 |
| free | `Tt` | 1,610,612,736 | 51,539,607,616 | | 345,287,687,744 | 328,053,537,792 | 34,468,250,624 |
| free | `M` | 538,566,413 | 17,234,125,312 | | 328,053,562,432 | 328,053,537,792 | 0 |
| alloc | `G1` (`g`, then `-1/g`, on `O1`) | 3,053,453,312 | 97,710,506,048 | L | 425,764,068,480 | 425,764,043,840 | 0 |
| alloc | the auxiliary array of the batch inversion | 16,777,216 | 536,870,976 | L | 426,300,939,456 | 426,300,914,816 | 0 |
| free | the auxiliary array | 16,777,216 | 536,870,976 | | 425,764,068,480 | 425,764,043,840 | 0 |
| free | `R1` | 3,053,453,312 | 97,710,506,048 | | 328,053,562,432 | 425,764,043,840 | 0 |
| free | `G1` | 3,053,453,312 | 97,710,506,048 | | 230,343,056,384 | 230,343,031,744 | 0 |
| free | the transform row | 768 | 24,640 | | 230,343,031,744 | 230,343,031,744 | 0 |
| free | the group buffer | 786,432 | 25,165,888 | | 230,317,865,856 | 230,317,865,856 | 0 |
| free | the tables | 16,784,852 | 537,115,328 | | 229,780,750,528 | 229,780,750,528 | 0 |

(`Tt` is allocated at the high end after the frees of `Y` and `G`, into the free block they left, so the high end does not grow beyond `86,007,858,240`.) The peak of the live set of stage C is `426,300,939,456` bytes and the largest sum of the two ends of the pool in stage C is `426,300,914,816` bytes (the slab block is not in the pool). After stage C the low end holds the twiddle table, `g` and `R` with no free block between them (`229,780,750,528` bytes) and the high end is empty: stage D starts from a packed pool, as in c69ae3de, with `R` of `n1` slots in place of `F` of `m` slots and `g` of `n1` slots in place of `m + 1`. The largest sum of the two ends over the trial is reached in stage D, `602,314,908,032` bytes, equal to the peak of the live set of stage D (section 7): the stage-C sequence leaves no hole that stage D pays for.

### 4.4 Stage D: the half-gcd

Notation: a polynomial is stored as its coefficient array with the top coefficient nonzero (length = degree + 1). Euclid sequence of `(a, b)`, `deg a > deg b`: `r_0 = a`, `r_1 = b`, `r_{i-1} = q_i r_i + r_{i+1}`; `d_j = deg q_1 + ... + deg q_j`, so `deg r_j = deg a - d_j`;
`R_j = Q_1 ... Q_j` with `Q_i = [[q_i, 1], [1, 0]]` (entries of degree at most `d_j`; the first-row entries of degree exactly `d_j` for `r11`), and `(r_0, r_1)^T = R_j (r_j, r_{j+1})^T`.

`hgcd(a, b, k)` (`deg a = n`) returns, for `h = max{ j : d_j <= k }`, the matrix `R_h` (when asked) and the pair `(r_h, r_{h+1})`. The procedure: if `b = 0` or `n - deg b > k` return the identity. If `k <= 96`, plain Euclid (`poly_divrem_naive`) while the next quotient degree fits the remaining parameter; a division step whose quotient has two coefficients (the normal case) is one pass over the remainder, `r_k = a_k - q0 b_k - q1 b_(k-1)`, with `b_(k-1)` kept from the previous iteration and no copy of `a` (per element 2 loads, 2 multiplications, 2 subtractions, 1 store, each load and store with its address operation, the loop control of 3 and the test `if (k)` of 2 operations), and `R := R Q` for a two-coefficient quotient is likewise one pass per entry pair (`mul_add_q2`).
Otherwise, `k1 = ceil(k/2)` (`k1 = floor(n/2)` if `2 k1 > n`), `s = n - 2 k1`: (1) `R1 = hgcd(a quo x^s, b quo x^s, k1)` (the top parts, matrix wanted); (2) `(c, d) = R1^{-1} (a, b)` by NTT products (`apply_inv`): `c = s (r22 a - r12 b)`, `d = s (r11 b - r21 a)`, `s = (-1)^h`, evaluated cyclically on `3 * 2^j` points (the high coefficients of `c` and `d` cancel, so the cyclic result is exact); the Good-Thomas rows are processed one at a time, and in each row `a` and `b` and each of the four matrix entries are transformed once (six forward transforms of a row) and the two output rows are inverse transformed (`conv_bilin_otf`), the sign of each output being absorbed in the scale factor `1/N`; (3) if `d = 0` or the next quotient degree `deg c - deg d` exceeds `k - d_1`
(`d_1 = deg R1`) return `R1` and `(c, d)`; (4) divide `c = q d + e` (`divrem_any`); (5) `R2, (c', d') = hgcd(d, e, k - d_1 - deg q)`; return `R1 Q R2` (matrix products by NTT, only if the matrix is wanted; the product of the two 2 x 2 matrices transforms each of the eight entries once per row, with the right-factor entries of one column pair held and the left-factor entries streamed, and inverse transforms the four outputs, `conv_bilin_otf` again).
The outer function `poly_gcd_own` repeats, while `deg b > 0` and `n = deg a > 192`: `(c, d) = hgcd(a, b, floor((n+1)/2))`, one division `c = q d + e` and `(a, b) := (d, e)`; at or below 192 it runs classical Euclid; at the end it scales the last nonzero remainder to be monic (one inversion, `deg + 1` multiplications).

**Division.** `divrem_any(a, b)`, `la - lb + 1` quotient coefficients `kq`: if `kq <= 64` or `lb <= 64` schoolbook (`poly_divrem_naive`); otherwise (`divrem_fast`) the reversed Newton identity: `q_rev = (a_rev * inv(b_rev mod x^kq)) mod x^kq`, `q = reverse(q_rev)`, `r = a - q b` (low `lb - 1` coefficients), with
the reciprocal by Newton iteration `g_{2t} = g_t - x^t (g_t * mid(f g_t))` and all products by `poly_mul`.

**Products and arrays of the padded division.** The padded division of section 6.3 (b) (the Newton range `64 <= dq <= dmax = min(k2, la - 65)` of a dividend `a` of `la` coefficients; `kN = dmax + 1`, `lbp = la - 64`, `lbr = min(lbp, kN)`) runs in the order below. Besides the arrays of its caller (the dividend, the divisor, and the quotient array `q` and the remainder array `r` of the node, which are allocated before the division, `q` at its largest length of `k2 + 1` elements and `r` with `la` elements) it holds only the arrays named here, each from its allocation to its free.

Every product of the division is one product of two polynomials computed by the transform of 4.2 and left in its transform array. For a product of `o` coefficients of which a window is wanted: the array `out` of `N = 3 * 2^a >= need` elements (the smallest transform size of 4.2 that is at least `need`; `need = o`, except for the middle product below) and one row scratch of `2^a` elements are allocated; for each of the three rows of the Good-Thomas layout the first operand is transformed into the row of `out` itself and the second operand into the row scratch, the two are multiplied pointwise into the row of `out` (the pointwise loop of 4.2, with the first factor read from the row of `out`), and the row of `out` is inverse transformed in place; the wanted entries of `out` are multiplied by `1/N` in place; the row scratch is freed. The caller reads the product from `out` and frees it. The operations are those of the bilinear form with one product and the scaling of the wanted coefficients, as charged in 6.3 (b) (`prod_cost` of Appendix E, with the windows below); only the arrays they work on differ from a product into a separate array of `o` elements.

Windows. Only part of each product of the division is used, and the program forms only that part. In the series inverse only the coefficients `t .. t2 - 1` of `e = br_(lft) * g_t` are used (they are `mid`): `e` is a middle product (Hanrot, Quercia and Zimmermann, 2004), formed cyclically modulo `x^N - 1` with `N = 3 * 2^a >= need = max(t2, lft - 1)`; the coefficients of positions `>= N` wrap onto positions `< lft + t - 1 - N <= t`, below the window, so the window is exact; the second operand `br_(lft)` is read shifted by `N - t`, so that the window starts at position 0; only the `m2` coefficients of the window are inverse transformed and scaled. Of `h = g_t * mid` only the first `m2` coefficients are used, of `qp = ar * g` the first `kN`, of `pp = qb * bp` the first `lbp - 1` (the remainder has fewer than `lbp` coefficients): these products are formed with the transform of the full product (`need = o`) and only those coefficients are inverse transformed and scaled.

1. `bp` (`lbp` elements): the divisor with zeros above its top coefficient; `br` (`lbr` elements): the reversal of `bp`; `g` (`kN` elements).
2. The series inverse `g = 1/br mod x^kN` by the levels `t -> t2 = min(2 t, kN)`, `t = 1, 2, 4, ...`, with `lft = min(lbr, t2)` and `m2 = t2 - t`: the product `e = br_(lft) * g_t` (the window `t .. t2 - 1` of its `lft + t - 1` coefficients wanted); `mid` (`m2` elements): the coefficients `t .. t2 - 1` of `e` (zero beyond its last coefficient), after which `e` is freed; the product `h = g_t * mid` (the first `m2` of its `2 m2 - 1` coefficients wanted); `g[t .. t2) := -h[0 .. m2)`; `h` and `mid` are freed.
3. `br` is freed. `ar` (`kN` elements): the reversal of the top `kN` coefficients of the dividend.
4. The product `qp = ar * g` (the first `kN` of its `2 kN - 1` coefficients wanted); `qb` (`kN` elements): the reversal of the first `kN` coefficients of `qp`, truncated to the `dq + 1` coefficients of the quotient with zeros above; then `qp`, `ar` and `g` are freed.
5. The product `pp = qb * bp` (the first `lbp - 1` of its `la` coefficients wanted); the remainder `r := a - pp` (low `lb - 1` coefficients); then `pp`, `qb` and `bp` are freed.

Appendix E (`div_walk`) allocates and frees exactly these arrays in this order, with the sizes of the plan of each product, and adds the peak of the walk to the live set of the node.

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes and compares them; the algorithm outputs only if they are equal and the pairs differ; it never outputs a non-collision. This section is a statement about the output of a successful run, and holds for every coin sequence. It contains no probability.

## 6. Ledger: worst-case operation count (primitive operations; `C(8) = 384`)

Notation: `T_fixed` = init (twiddle table) + setup (the line) + the plan_invN misses + stage H + stage I; `T_trial` = stages A to D of one trial, stage E at its cap, stages F and G, and the trial loop; `T_off` = the offline bound of section 6.2. The claim is `N_max = T_fixed + K * T_trial + T_off` with `K = 1`, and `time_log2 = ceil_5(log2(N_max / 384))`.

Every stage is charged by the rules of section 4.2 where it executes. Section 6.1 compares the same counting with the instrumented totals of our executed entries at r = 3, 4, 5. Every trial is charged as if its gcd had degree 0 in stages A to D (the larger case), and in addition with stage E at its cap, stage F at its worst case and stage G.

| row | what is charged | operations |
|---|---|---:|
| init | twiddle table of `2^(31-1)` elements (`ntt_init(31)`: 5 operations per element, loop control, the roots of unity, the inversions of the setup) | 8,589,952,701 |
| setup | the line (`line_setup`) | 4,910 |
| A (per trial) | stage bookkeeping 1,000, loop test and update 5, the coin draw 31, one allocation | 1,196 |
| B (per trial) | `3,221,225,472` points, each with two evaluations of `F` (at `c + zeta^i` and `c - zeta^i`) at `C(8) = 384` operations each, the loop work around them, the inverse transform of size `3,221,225,472`, the normalisation | 3,656,592,954,049 |
| C (per trial) | `S^((p-1)/2) mod g` in the value domain on `K = 182` cosets of size `h = 2^24` (section 4.3V): the Barrett start, `g` and the start value on the two point sets, `224` squaring steps (45 with the multiplication by `S`), the return to coefficient form; expanded step by step in Appendix E (the table of 4.3V(e)) | 446,444,428,530,905 |
| D (per trial) | half-gcd of `(g, R - 1)` (section 4.4), charged for every remainder sequence (section 6.3: the normal local charge plus one full division at every node); expanded in Appendix E | 1,076,929,687,405,216 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16` (below) | 166,079,773 |
| F (per trial) | square root, back-map (below) | 47,012 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 384 + 32` | 8,712 |
| trial loop | the test and increment of the trial counter and the bookkeeping of the trial: at most 12 | 12 |
| plan_invN misses | one per distinct plan size (29 sizes) | 89,581 |
| H | canonical encoding of the output (6 conversions, 384 digits) | 5,644 |
| I | output of the answer: formatting (`400 * 8,192`), loops, entry, one `write`, one `exit_group` | 3,384,436 |
| offline | section 6.2 | 1,000,000 |
| **N_max** | `T_fixed + 1 * T_trial + T_off` | **1,527,039,469,464,147** |

The rows C and D are not asserted: Appendix E (`stage_cd.py`) expands them from the dimensions of 4.3V(a) (row C: the Barrett start, the evaluations, the 224 squaring steps and the interpolations, each step printed) and the half-gcd levels (row D), with the kernel charges of section 4.2, and prints and asserts the two values 446,444,428,530,905 and 1,076,929,687,405,216. Row B is 186 less and the plan_invN row 3,089 less than in c69ae3de: stage B allocates no array `F` (R leaves stage C in an array of its own), and 29 distinct plan sizes are used in place of 30.

`N_max = 1,527,039,469,464,147` operations `= 3,976,665,285,062.9` units, `log2(N_max / 384) = 41.85469627461552`, claimed as `41.85470` (rounded up at five decimals).

Stage B charges each of the `6,442,450,944` evaluations of `F` as one reduced permutation, `C(8) = 216 + 21 * 8 = 384` operations, although a line evaluation is a strict subset of the work of a reference permutation; the loop work around the evaluations is charged on top (section 3).

Stage E at its cap. The trial enters stage E only when `1 <= deg G <= DMAX`; stage E opens with 1,000 (stage bookkeeping) and runs a round for each pass of the isolation loop until `deg G = 1` or `Z` rounds have been made. A round at current degree `d` costs `R(d)`: the coin draw 31, the zero test of the shift (5, and at most 2 for the replacement of a zero draw by 1) and one negation; the Taylor shift (`taylor_shift`: two allocations, three loops of `d + 1` steps with their loads, stores and loop control, the schoolbook product of two polynomials of `d + 1` coefficients, two inversions and one exponentiation by `d`); `Z^((p-1)/2) mod G` by schoolbook square-and-multiply (`pow_half`: 253 modular squarings, each `2d + 3 d (d-1)/2 + 2 d^2` field operations and an allocation and a free, and 45 multiplications by `Z`, each `2d` field operations; because the memory-access charge adds 9 operations per field operation, every field operation of `pow_half` is charged 10); two classical gcds (`gcd_cl`: at most `d` outer iterations, each with one inversion charged `2,640` operations (the 330 field operations of `x^(p-2)` and the 2,310 control operations of its bit loop), at most `2d + 1` division steps, each charged at the largest row length); the copies, the tests and the frees. The cap charges every one of the `Z` rounds at `d = DMAX`, because `R(d)` is non-decreasing in `d`: `R(16) = 2,594,979`, of which `pow_half` is 2,471,032, the Taylor shift 11,700 and the two gcds 54,395 each. All allocations are charged at `L <= 16` live blocks (550 per allocation, 105 per free): in stage E the live blocks are the twiddle table, `G`, `S`, `S - 1`, `S + 1` and the two gcd arrays (at most 8), and at most four more inside the Taylor shift or the modular squaring. `E_cap = 1,000 + 3 + 64 * R(16) + 114 = 166,079,773`.

Stage F. After the stage bookkeeping (1,000), 12,000 control operations for the Tonelli-Shanks control and 2 more, the field operations of stage F are charged 10 each (the memory-access charge): the powers by `q` and by `(q+1)/2`, Tonelli-Shanks with parameter `m` falling strictly from 32 (an outer step with parameter `m` costs `m` squarings and 2 multiplications: at most `sum_(m=1)^(32) (m + 2) = 592`), and two back-maps (three fifth-root powers `x^e`, `e = (4(p-1)+1)/5`, two multiplications, two additions, two subtractions each), plus one addition and one subtraction: at most 3,401 field operations, so `F = 13,002 + 10 * 3,401 = 47,012`.

Every figure above is an upper bound that the algorithm meets or exceeds for every coin sequence and every target value (stage D by section 6.3): each loop bound is a constant or a function of `m` only, the trial loop is capped at `K` and tested at the start of each trial, the isolation loop is capped at `Z` rounds of degree at most `DMAX`, and the operations of each stage are counted under the rules of section 4.2.

### 6.1 Ledger recomputation and validation

The sum of section 6 is recomputed by the following script (standard library only).

```python
from math import log2, ceil
K, C = 1, 384
fixed = [8589952701, 4910, 89581, 5644, 3384436]   # init, setup, plan_invN misses, stage H, stage I
trial = [1196, 3656592954049, 446444428530905, 1076929687405216, 166079773, 47012, 8712, 12]   # stages A, B, C (4.3V, Appendix E), D, E (cap), F, G, main
offline = 1000000
N = sum(fixed) + K * sum(trial) + offline
print('N =', format(N, ','))
print('units =', round(N / C, 1))
print('time_log2 =', '%.5f' % (ceil(log2(N / C) * 100000 - 1e-6) / 100000))
```

Comparison of the counting with the instrumented totals of our executed entries (algorithmic totals; the executed runs at r = 3, 4, 5 had fixed centres and a different stage A, and their thread charges are excluded): the count is above the measured total in every row, and its heap peak equals the measured heap peak at r = 3 and r = 5 and is 64 bytes below it at r = 4.

| run | counted total | measured total | counted - measured | slack (bits) | counted heap peak | measured heap peak |
|---|---:|---:|---:|---:|---:|---:|
| r = 3, earlier program (fixed centre) | 410,937,818,567 | 409,369,056,359 | 1,568,762,208 | 0.00552 | 244,745,792 | 244,745,792 |
| r = 4, earlier program (fixed centre) | 3,993,660,556,174 | 3,977,289,295,772 | 16,371,260,402 | 0.00593 | 1,072,730,560 | 1,072,730,624 |
| r = 5, earlier program (fixed centre) | 9,217,469,769,975 | 9,171,678,989,504 | 45,790,780,471 | 0.00718 | 4,759,669,952 | 4,759,669,952 |

### 6.2 Offline derivation of the literals (preprocessing)

The algorithm uses constants that are derived from the organizer's constants and from `p` offline: the 192 round constants and 9 MDS entries in Montgomery form, `R^2 mod p`, `R mod p`, `2^65` and `5^q` in Montgomery form, the exponents `q`, `(q+1)/2`, `(p-1)/2`, `p - 2` and the integer `e = (4(p-1)+1)/5`. There is no search and no choice: each literal is the value of one closed formula in the organizer's constants. The Montgomery form of a constant `x` is `x * 2^256 mod p`, one modular multiplication plus parsing 64 hexadecimal digits; `5^q` is a square-and-multiply of 221 squarings and at most 221 multiplications; the exponents are shifts and subtractions of `p`. Each literal costs at most 4,000 word operations, there are at most 250 literals: 1,000,000 operations in all. This bound is inside `N_max` and is the declared `preprocessing_log2 = 20` (`2^20 = 1,048,576 >= 1,000,000`). The algorithm uses no other offline result: the line, its minors and the twiddle table are computed at run time and charged in `setup` and `init`. The leading coefficient `f_D(0)` of section 2.3 is a fact used in the proof; the algorithm re-derives it (stage B tests that the leading coefficient of `g_c` is nonzero and normalises by it).

### 6.3 Stage D charged for every remainder sequence (declared cost model)

The row D of the ledger bounds the half-gcd for every pair of inputs. It is evaluated node by node, with no multiplier: the recurrence below is the function `hgcd` of Appendix E with `WORST_D = True`, summed over the actual recursion tree. (a) The padded half-gcd. The program is the padded half-gcd of Thome (2003) and Stehle and Zimmermann (2004). A call `hgcd(a, b, k)` of length `n` pads the operands to the length `2 k1` with `k1 = ceil(k/2)` (it drops the low `s = n - 2 k1` coefficients), so its first recursive call has operands of length exactly `2 k1` and parameter `k1`, the same for every input, and the call splits at exactly half. That call returns the degree `h1` and the matrix `R1`, and it stops only when the next quotient has degree `dq > k1 - h1` (or the remainder is zero or the target is reached), so `h1 + dq >= k1 + 1`: the quotient that overshoots the midpoint is not part of the first call. The node removes the overshoot by one division of the reduced pair (the re-centering division), after which the second call has parameter `k3 = k - h1 - dq <= k - k1 - 1` and operands of length at most `n - k1`. Hence for every input the recursion tree is a subtree of the tree of the normal case (every quotient of degree 1, `h1 = k1`, `dq = 1`), with the same `k` at every node, operands no longer, matrices of at most `k + 1` coefficients; `apply_inv` and the matrix products of a node cost no more than at the same node of the normal case (their charge does not decrease with the lengths of the operands), and each repetition of the outer loop of the Euclid driver removes at least `k + 1` degrees, as in the normal case. Every length of the program is therefore a function of `m` alone. (b) The recurrence. For a node of the normal-case tree with operand length `la` and parameter `k`, `W(node) = local(node) + div(lcc, k2) + W(first call) + W(second call)`, where `local(node)` is the normal charge of the node without its two calls (the padding, `apply_inv`, the division of two coefficients, the matrix products, the allocations and frees) and `div(lcc, k2)` is the charge of the re-centering division at that node for every quotient degree `dq` from 1 to `k2 = k - h1` that can occur there, computed exactly (`worst_div` of Appendix E): when the quotient has at most 64 coefficients or the divisor at most 64 (the schoolbook range, at most 127 values of `dq`), the division is schoolbook (`3 + 7 lcc` plus the inverse of the leading coefficient plus `(dq + 1)` rows of `12 (lcc - dq - 1) + 15`) and every such `dq` is evaluated; otherwise (the Newton range `64 <= dq <= dmax = min(k2, lcc - 65)`) the program runs the division padded: the quotient precision is `kN = dmax + 1`, the divisor is copied into a buffer of `lcc - 64` coefficients with zeros above its top coefficient (the same polynomial), its reversal into a buffer of `min(lcc - 64, kN)`, and the quotient, truncated to its `dq + 1` coefficients, into a buffer of `kN` with zeros above; every size is then the same for every `dq` in the range, so the charge is one number: the Newton division at these sizes (one series inverse of precision `kN` and the two products, by the model's bilinear-form charge with the windows of section 4.4: only the used coefficients are inverse transformed, and the middle products of the series inverse use the smaller cyclic transform) plus the three buffer loops (a load, a store, a loop step and a select per element, with their allocation and free). The arrays that this division holds, and the order in which it allocates and frees them, are given in section 4.4 and walked in Appendix E (`div_walk`); they do not change the charge. `div` is the larger of the schoolbook maximum and this number; no maximisation over unchecked degrees is involved. All nodes are charged at their worst `dq` at the same time. The tree is that of the normal case, and `W` is summed over all of its nodes. (c) The base case `k <= 96`: each step of `hgcd_base` is charged on the general division path (`naive_general`), at least what the same step costs in the normal case; a step of quotient degree `d` costs at most `d` times a step of degree 1 on that path, and the degrees removed by a base call sum to at most `k`, so a base call of any input costs no more than the base call of the normal case with every step so charged. (d) The outer loop of `poly_gcd_own` (`n > 192`) adds, per repetition, the full division of `lc` coefficients at its worst quotient degree `div(lc, lc - 1)`, and the closing classical Euclid at length at most 192 adds `12 * 193^2 + 20 * 193 + 400,000` operations once. Appendix E (`stage_cd.py`) prints, for `r = 8`, the normal local charges of the tree (614,595,109,235,139), and the total of the recurrence with (b), (c) and (d) (1,076,929,687,405,216), and asserts the latter.

## 7. Memory

Three terms make up the memory.

(a) The code and static data of an implementation of the algorithm: 399,216 bytes of code, 32 of initialised data and 4,851,196 of static tables and buffers (the 8,192-byte output buffer and the tables of the stages): 5,250,444 bytes.

(b) The arena, which serves every array of the largest trial (the heap is inside the memory of the implementation; nothing is requested from the system at run time). Each block has a 64-byte header and a payload rounded up to a multiple of 64 bytes (section 4.2). The arena is the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (one trial, `K = 1`: a trial frees every array but the twiddle table, and the simulation checks that the pool is back to that state). `python3 stage_cd.py` of Appendix E records every allocation and free of the trial in the order of the program (the twiddle table, stage A, stage B, stage C, stage D; the arrays of a division are allocated and freed in the order of section 4.4), checks that these events reproduce the live-set walk of every stage (bytes in use, peak, live blocks), and runs the allocator on them. With the padding of section 6.3 every size in the sequence is a function of `m` and of the shape of the recursion only (the lengths of the half-gcd tree, section 6.3 part (a), and the arrays of the division of section 4.4), so the sequence is the same for every input. The two-ended pool takes the blocks of more than 2^21 bytes and is simulated address by address (two lists in address order, the low one from the bottom and the high one, for the statements and parities marked `# pool:H`, `# pool:H0`, `# pool:H1`, from the top; the first free block that fits on the request's side is cut from the side nearest its end; a free merges with its free neighbours and with the unused middle); its capacity is the largest sum of the extents of the two ends over the trial, `602,314,908,032` bytes (after stage C `426,300,914,816`, after stage D `602,314,908,032`), plus 128 bytes so that the unused middle is always at least 128 bytes. The stage-C part of the sequence is listed array by array, with the two ends after every event, in 4.3V(f): stage C leaves the low end packed (the twiddle table, `g`, `R`) and the high end empty. The live-set peak of the same sequence is `602,314,908,032` bytes, the live set of the top-level `apply_inv` of the half-gcd, and the pool reaches exactly that peak: the two ends are packed with no hole at the moment of the largest demand. The slab classes take the blocks of at most 2^21 bytes (a block of at most `2^j` bytes gets a slot of `2^j` bytes; the free list of the class first, else a new slot from the end of the slab area), so the slab area is the sum over the classes of the peak number of live blocks of the class times `2^j`: `50,306,432` bytes (Appendix E prints the peaks per class). Stages E to I hold at most 16 live arrays of at most 17 elements (16 slots of 1,024 bytes), and the allocator keeps 35 free-list heads and the end of the slab area (36 words, 288 bytes): `16,896` bytes with a margin of 224. The arena is `602,365,231,488` bytes (the three terms, rounded up to 64 bytes), in the stage with the highest pool address, D. The peaks of the live set per stage (twiddle table, `g`, `R` after stage C, and the live set of the stage; each array counted as 64 + 32 * slots rounded up to 64 bytes, headers included): A 132,070,244,480; B 235,149,459,648; C 426,300,939,456; D 602,314,908,032; stage E and the later stages hold the twiddle table and a few arrays of at most 17 elements. The walk of stage D is the worst-case one: besides the arrays of the normal case it holds, at every division, the quotient array at its largest length (`k2 + 1` elements at a node of the half-gcd, the whole length in the outer loop), the remainder array of `lcc` elements (`lc` in the outer loop), and the arrays of the padded Newton division in the order of section 4.4 (`bp`, `br`, `g`, the products and arrays of the levels of the series inverse, `ar`, `qb` and the two final products, each product with its transform array and its row scratch), walked by `div_walk` of Appendix E; the lengths of all other arrays are at most those of the normal case (section 6.3, part (a)). The arrays of the divisions do not raise the peak of stage D: the script of Appendix E prints the peak of stage D without them, `602,314,908,032` bytes, and with them, `602,314,908,032` bytes. The peak of stage D is the live set of the top-level `apply_inv` of the half-gcd: the twiddle table, `g` and `R` (`n1 = 3,053,453,312` slots each), the four entries of the matrix of the first recursive call, the two row scratches of `1,073,741,824` elements and the two output arrays of `3,221,225,472` elements. The largest transform has `3 * 2^31` points and uses roots of unity of order 3 and `2^31`; `p - 1` is divisible by 3 and by `2^32`, so the transform sizes of this r are available in the field. The largest buffers of stage C (4.3V(f)) are `g`, `R`, `R1` and `G1` (`n1` elements each), the twiddle table (`2^30` elements) and the transform arrays `Y` and `Tt` of the Barrett start (`3 * 2^29` elements each).

(c) A stack bound of 65,536 bytes.

Total: (a) + (b) + (c) = `602,370,547,468` bytes `= 2^39.13186`, claimed as `memory_log2_bytes = 39.132` (rounded up at three decimals). The memory penalty is `max(0, 39.132 - 20) = 19.132`. The offline derivation of section 6.2 is a closed formula per constant; its memory is bounded by 1,024 bytes, inside the figure above. The algorithm has no stored advice and no precomputed data beyond the constants of section 6.2; the twiddle table is built at run time and charged in stage "init".

## 8. What is provided

* The algebraic derivation (sections 2-3), the algorithm and its worst-case charges (4, 6, 7), the premise `H-ONE` with the success bound (section 9), the isolation lemma with proof (9.4), and the evidence, labelled as evidence (section 10).
* The claim is the worst-case count of the algorithm, `memory_log2_bytes` its footprint, and a success probability that follows from `H-ONE`. The cost claim is in the model of section 4.2.
* No certificates (the certificate manifest is empty); the experiments are those of 10.2.
## 9. Success probability and the premise `H-ONE`

### 9.1 The premise `H-ONE`

Notation. `p` is the Pallas prime, `D = 5^14`, and `F` is the fixed polynomial of section 2.3 at r = 8 (degree `D`, leading coefficient `f_D(0) != 0`). `g_c` is the monic odd part about the centre `c` (section 3, degree `m = 3,051,757,812`), and `G(c, t) = (F(c + t) - F(c - t)) / (2 t) = g_c(t^2)`. For `c` in `F_p`, let `k(c)` be the number of nonzero squares `S` with `g_c(S) = 0`; this is `deg G_c` of section 3, the degree of `gcd(g_c, S^((p-1)/2) - 1)`. `E_c` is the event `1 <= k(c) <= DMAX` (`DMAX = 16`) under which stage E runs.

**Premise `H-ONE`.** The number of centres `c` in `F_p` with `1 <= k(c) <= 16` is at least `0.3901 p`. Equivalently, for `c` uniform on `F_p`, `P(E_c) >= q = 0.3901`.

Four fields (as in claim.json). **Statement:** the premise above. **Role:** score-critical. **Scope:** the fixed target `poseidon-orchard-r8-prefix-v1`, this line construction (the line `j = 0` of the first two rounds, section 2) and the polynomial `F` of section 2.3, with centres uniform on `F_p`. Nothing is claimed for other round counts. **Limitations:**
- The premise concerns this `F`, not every polynomial of degree `D`. It is false for permutation polynomials: every pure composition of maps `x -> a x^5 + b` is bijective and has `k = 0` at every centre. It is also false for a decomposable `F` with imprimitive monodromy (the axis line of 10.3, Theorem C).
- It is false at one layer (`F_1`, `m = 2`: the law of 9.3(a) gives exactly 0.375) and true at two and three layers (9.3(c)).
- The value `0.3901` is `0.0033693` below the value `1 - e^(-1/2) = 0.3934693` of the law of 9.3(a). The bound of 9.2 needs `P(E_c) >= 0.390000000000002372`.

What the premise does not contain: no random-polynomial model; no independence of centres (one centre is drawn); no statement about the remainder sequences (stage D is charged for every remainder sequence, 6.3); and nothing about the cost.

### 9.2 The success bound with one centre

(a) *Centre.* The centre is one draw (4.1.1) and lies within statistical distance `eps_coin < 2^-128` of uniform on `F_p`; the exact value is 1.574e-39 (2^-128.90). So `P(E_c) >= q - eps_coin` for the drawn centre.

(b) *Stages C and D.* Stage C (4.3V, which computes `R` exactly: the proof there is unconditional) and stage D (4.4, charged for every remainder sequence, 6.3) run to their end for every centre and return `G = gcd(g_c, R_c - 1)`, of degree `k(c)`, with one exception: if `g_c` has a root on the evaluation set `O1` of stage C the trial ends there (4.3V(d)). For a uniform centre this has probability at most `eps_O1 = n1 (5^14 - 1) / p = 6.438e-58 (2^-189.99) < 2^-189`, a proved bound (4.3V(d)); for the drawn centre the event `E_c` without a root on `O1` therefore has probability at least `q - eps_coin - eps_O1`. No premise on the remainder sequence is used.

(c) *Isolation.* If `E_c` holds, stage E fails with probability at most `eps_iso = 2.371e-15 (2^-48.58) < 2^-48`, over words that are fresh for that stage (lemma 9.4).

(d) *The bound.* A trial with `E_c` and a successful isolation ends in a verified collision (sections 2-5). So, with `K = 1`,

`P[success] >= 1 - (1 - q)^K - K (eps_coin + eps_iso + eps_O1) = q - eps_coin - eps_iso - eps_O1 = 0.390099999999997628 >= 0.39009`

with `q = 0.3901` and `K = 1`. The bound stays at least 0.39 for every `q >= 0.390000000000002372`. The probability is over the random words of 4.1.1 for the fixed target. It is not a probability over targets and not a sampled frequency, and no run of this algorithm at r = 8 enters it. Appendix D recomputes these numbers with exact rationals.

*Sensitivity of the bound to `H-ONE`.* The success bound moves one for one with `q`: if the true fraction is `q - eps`, the one-centre success is at least `0.3900`, `0.3891`, `0.3867` and `0.3801` for `eps = 0.0001`, `0.001`, `0.0033693` (the whole allowance below the law of 9.3(a)) and `0.01`. The same algorithm with two centres (`K = 2`, one more bit of time, `time_log2 = 42.85470`) has success at least `1 - (1 - q)^2 - 2 (eps_coin + eps_iso + eps_O1)`, which is `0.6279`, `0.6268`, `0.6239` and `0.6157` at those `eps` and stays at least 0.39 for every `q >= 0.21898`; the premise can fail by `0.17` before the two-centre variant falls below 0.39. The evidence for `H-ONE` (9.3, 10.3, 10.5.1) is labelled by who ran it and by its depth; the organizer-run tests at `N = 2, 3` and the computed theorems at those depths establish nothing at `N = 14`, where `H-ONE` is a premise and is declared as such.

(e) *Why one centre needs `H-ONE`.* Two moments of `k` cannot give 0.39 with one centre. The law of 9.3(a) has the exact values `E[k] = 1/2` and `E[k(k-1)] = 1/4`, and the sharp lower bound on `P(k >= 1)` over all laws with these moments is `3/8 = 0.375`: the law `P(0) = 5/8`, `P(1) = 1/4`, `P(2) = 1/8` attains it. With three moments the bound is still 0.375. This is why our entry 7d53191b (premise `H-GEOM-w2`, two moments from Weil's bound) used two centres. One centre needs a statement about the event itself, or four moments (9.3(b)).

### 9.3 Where the number comes from (support of `H-ONE`; not used in the bound)

(a) *The law.* The roots of `G(c, t)` in `t` are `+-t_1, ..., +-t_m`, where `u_i = t_i^2` are the roots of `g_c`. So the Galois group `Gamma` of the cover `G(c, t) = 0` of the `c`-line acts by signed permutations: `Gamma` is a subgroup of the hyperoctahedral group `B_m` (10.3, Grok job 137). For a centre off the branch locus, `k(c)` is the number of positive fixed points of the Frobenius element: the indices `i` with `t_i` in `F_p`.

For a uniform element of `B_m`, the binomial moments of this number are `E[C(k, j)] = 2^-j / j!` for `j <= m`, so `P(k >= 1) = 1 - sum_(j <= m) (-1/2)^j / j!`. This is 0.375 at `m = 2`, 0.3958 at `m = 3`, 0.3932 at `m = 4`, and 0.3934693403 for every `m >= 12`: the Poisson(1/2) value `1 - e^(-1/2)`. The tail is negligible: `P(k > 16) < 2.3e-20`. With Chebotarev's theorem (Frobenius elements equidistributed in `Gamma`), this law is the frequency over the centres.

(b) *Moments and counts.* `E[C(k, j)] = N_j / (2^j j! p)`, where `N_j` is the number of points `(c, t_1, ..., t_j)` over `F_p` with `G(c, t_i) = 0`, `t_i != 0` and `t_a^2 != t_b^2` (for `j = 1, 2` these are the counts of the two-moment premise `H-GEOM-w2` of our entry 7d53191b).

For every integer `k >= 1`, `sum_(j=1..4) (-1)^(j+1) C(k, j) = 1 - C(k-1, 4)`. This is 1 for `k <= 5` and at most 0 for `k >= 6`, and the sum is 0 at `k = 0`. So `1_(1 <= k <= DMAX) >= k - C(k, 2) + C(k, 3) - C(k, 4)` for every integer `k >= 0`, and `P(E_c) >= S_1 - S_2 + S_3 - S_4` (Bonferroni at order 4). With the moments of (a) this is `151/384 = 0.3932292`.

Hence `H-ONE` follows from four count statements, `N_1 >= (1 - eps) p`, `N_2 <= (1 + eps) p`, `N_3 >= (1 - eps) p` and `N_4 <= (1 + eps) p`, with `eps <= 0.0048257` (`151/384 - (249/384) eps >= 0.3901`). The premise is stated as the weaker statement `H-ONE` itself.

(c) *A theorem at two and three layers.* Let `F_N` be the truncation of 10.3: the first `N` S-box layers, degree `5^N`. On the deployed constants and the attack line, 10.3 gives the arithmetic monodromy `Gamma = B_12` at `N = 2` and `Gamma = B_62` at `N = 3` (`pi(Gamma) = S_m`, `K = F_2^m`).

The geometric monodromy is normal in `Gamma` with a cyclic quotient. It therefore contains the commutator subgroup `{(eps, pi) : pi in A_m, prod eps = 1}` of `B_m`. That subgroup acts transitively on ordered `j`-tuples of signed distinct indices for `j <= m - 2`: `A_m` is `(m-2)`-transitive, and a free sign fixes the parity.

So for `j <= 8` the curve counted by `N_j` is absolutely irreducible, a complete intersection of degree at most `(5^N - 1)^j`. The Aubry-Perret bound gives `N_j = p (1 + rho_j)` with `|rho_j| <= (5^N - 1)^(2j) p^(-1/2)`: below `2^-53` at `N = 2` and below `2^-15` at `N = 3` (`j <= 8`).

The Bonferroni bounds of orders 7 and 8 then give `0.39346933 <= P(E_c) <= 0.39346944` for `F_2` and for `F_3`. At these depths `H-ONE` is a theorem, with margin 0.00337.

At `N = 4`, the cycle types `(312)` and `(311,1)` of 10.3 make `pi(Gamma)` 2-transitive of degree 312. The only such groups are `A_312`, `S_312`, and the groups between `PSL(2,311)` and `PGL(2,311)`, whose non-identity elements fix at most two points. Centres with `k(c) = 3` and `k(c) = 4` occur (our runs, 10.5.1), and the 312-cycle is odd, so `pi(Gamma) = S_312`. The sign kernel at `N = 4` is not computed.

(d) *Measured.*
- Toy fields, exact over all centres: deployed constants reduced modulo `p = 1,048,627` and six random-constant seeds, 3 to 8 S-box layers, partial rounds included, 27 cases. `P(k >= 1)` lies between 0.39214 and 0.39436; the largest deviation from 0.3934693 is 0.00133, that is `1.36 / sqrt(p)`.
- The real field, on uniform centres: see 10.5.1 for the organizer-run tests and our runs.

(e) *The extrapolation.* At `N = 14` the monodromy is not computed, and the counts `N_3`, `N_4` are out of reach of Weil's bound (the relative error bound `(5^14 - 1)^(2j) p^(-1/2)` is about `2^68.0` at `j = 3`).

The premise states that this `F` stays within `0.0034` of the law of (a): no structure appears between the third layer and the fourteenth that changes the law of the positive fixed points by 0.9%.

The measured deviations shrink like `p^(-1/2)` and do not grow with the degree. On the toy fields the deviation is `1.36 / sqrt(p)`. The counts of Grok job 139 give `eps ~ 3.1 / sqrt(p)` over degrees 5 to 1,953,125 (Grok job 139: exact counts of `N_1`, `N_2` on width-3 toy permutations over prime fields below `2^22`, 1,316 generic seeds, no dependence on the degree).

### 9.4 Lemma (isolation), proved

**Lemma.** Let `G` be monic of degree `d` with `2 <= d <= DMAX`, a product of `d` distinct linear factors over `F_p`. In one round of 4.1.2 (`a` is a coin draw, with 0 replaced by 1), with probability at least `w = (4 (p-3)/2 - S3)/2^256 = 1/2 - 7.869e-40` (`S3` of 4.1.1) both `G_+` and `G_-` are nonconstant, and then the kept part has degree at most `floor(d/2)`. The degree never increases. Hence after `Z` rounds the probability that `deg G >= 2` remains is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1]`, which for `DMAX = 16`, `Z = 64` equals at most 2.371e-15 (2^-48.58) (the exact sum below).

*Proof.* Let `u != v` be two roots of `G`, `chi` the quadratic character on `F_p`. In a round the roots of the shifted `G` are `r + a`. If `a` is not `-u`, not `-v`, and `chi(u+a) != chi(v+a)`, then exactly one of `u+a`, `v+a` is a nonzero square and the other a nonsquare; so `(u+a)^((p-1)/2) = 1` for one and `-1` for the other, one root lies in `G_+` and the other in `G_-` (a root of the shifted `G` is a root of `Z^((p-1)/2) - 1` iff its character is `+1`, of `Z^((p-1)/2) + 1` iff it is `-1`). Both parts are then nonconstant, their degrees sum to at most `d`, and the smaller has degree at most `floor(d/2)`. The number of `a` with `chi(u+a) chi(v+a) = -1`: `sum_(a != -u,-v) chi((a+u)(a+v)) = -1`, because the quadratic `a^2 + (u+v) a + uv` has nonzero discriminant `(u-v)^2` (the standard evaluation of a quadratic character sum), so the count of `a` outside `{-u,-v}` with product `-1` is `((p-2) + 1)/2 = (p-1)/2`, at least `(p-3)/2` of them nonzero. Every residue is taken by the draw with probability `3/2^256` or `4/2^256`, and `4/2^256` for all but `S3` of them (4.1.1), so the `(p-3)/2` nonzero values of `a` listed have together probability at least `(4 (p-3)/2 - S3)/2^256 = w` (a zero draw is replaced by 1, which only adds probability). A part is always a divisor of `G`, so the degree is nonincreasing whatever happens in a round that is not of this kind. Conditional on any history of earlier rounds, the next `a` is made of fresh random words, so every round is of this kind with probability at least `w`, and at most `ceil(log2 DMAX)` such rounds bring `d <= DMAX` to 1 (16 -> 8 -> 4 -> 2 -> 1). The failure probability is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = 2.371e-15 (2^-48.58)`, computed exactly in Appendix D. This is a proved bound under the random words, not a premise and not a sample.

## 10. Evidence

This section is the evidence for the premise `H-ONE` and for the digest of the target. The executions of 10.1 and the computations of 10.3 are ours; the experiments of 10.2 are run by the organizer's runner. None of it enters `success_probability` or the bound of section 9, and none is a lower bound on the probability of `E_c`.

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

Seven experiments of kind `python-message-pairs-v1` (five here, two in 10.5.1), run by the organizer's own experiment runner (the Orchard digest of the target is called by the runner). The three Python sources are 60,921 bytes together (the limit for experiment sources is 65,536).

(a) `lowbits-birthday` (`experiments/exp_lowbits.py`, kind `python-message-pairs-v1`, event `digest-xor-mask` with mask `fffc` followed by 30 zero bytes and expected value zero). For each organizer trial the program searches at most 1200 fresh inputs derived from the trial seed for two distinct canonical messages whose digests of the selected target `poseidon-orchard-r8-prefix-v1` agree in the first 14 bits of the big-endian reading, and returns the pair (or two nulls). Its source is 15,748 bytes (the limit for experiment sources is 65,536). Its event is a reduced one on the digest of the selected target: the program computes its candidates with its own copy of the permutation (constants embedded), and a returned pair counts only if the organizer's callback gives digests that agree in those 14 bits, so a pair is accepted only when that copy agrees with the target. The digest map so checked is the map whose line polynomial `F` the premise concerns.

The experiment is run by the organizer's own experiment runner (python-message-pairs-v1, the Orchard digest called by the runner), and the intake report of that run is the evidence: 256 of 256 trials returned a verified pair at r = 8, and the output was byte-identical on repetition. Our own earlier local run of the same events (plain Python on our machine) agreed: 256 of 256 trials in 3.8 s.

(b) `line-ladder-w6`, `line-ladder-w8`, `line-ladder-w10`, `line-ladder-w12` (`experiments/exp_line.py`, event `digest-xor-mask` on the first 6, 8, 10 and 12 bits of the digest, expected value zero). The program is the line construction of section 2 for the target at r = 8: it builds the line `j = 0` of the first two rounds (the point `Q`, the direction `(a, b)`, the vectors `alpha` and `beta`), evaluates `F(W)` as the remaining fourteen rounds applied to `alpha + beta W` (`deg F = 5^14`), and maps a point `W` back to the canonical pair `(nk, rho)` with the inverse S-box `x -> x^e` of 2.1 and 2.2. For each organizer trial it takes a centre `c` from the trial seed, scans the antipodal pairs `W = c + s`, `W = c - s` for `s = 1, ..., 150`, and at the first pair whose digests agree on the masked bits it maps both points back, checks both messages against the full permutation inside the program and returns them (else two nulls). A returned pair counts only when the runner's own digest of the two canonical messages agrees on those bits, so each counted trial is a pair of antipodal points of the line construction whose digests `F(c+s)` and `F(c-s)` agree at width `w`: the reduced-width form of the event `F(c+s) = F(c-s)` that the premise `H-ONE` is about (a root of `g_c`). In the picture of the premise, `F(c+s) - F(c-s) = 2 s g_c(s^2)` takes random-function values in `s` at these widths, so a trial returns a pair with probability `1-(1-2^-w)^150`: 0.9058, 0.4441, 0.1363 and 0.0360, that is about 232, 114, 35 and 9 of the 256 trials for `w` = 6, 8, 10, 12. A clustering of the roots of `g_c`, or a bias of the odd structure, would move these counts.

The intake report of the organizer's run records 231, 117, 39 and 8 of the 256 trials with a verified pair for `w` = 6, 8, 10, 12 respectively, and byte-identical output on repetition. The counts fall with the width as the predictions do.

### 10.3 Computed theorems and computations for the generic line (Grok, jobs 135 and 136)

Grok (xAI), our research partner, computed the hypothesis of `H-GEOM-w` exactly over the Pallas field for a toy permutation, by exact computation (the cycle types, factorisations and leading coefficients below are the printed results): width 3, S-box `x -> x^5`, `M = [[2,1,1],[1,2,1],[1,1,2]]` (every minor nonzero mod `p`), round `i` adds the constants `(3i+1, 3i+2, 3i+3)`, every round full, output coordinate 0, on the generic line `(L, 2L+1, 3L+5)`. Notation as in 9.1: `D = deg F`, `G(c,t) = (F(c+t) - F(c-t))/(2t) = H(c, t^2)`, `m = (D-1)/2`; the cycle types below are those of `H(c, u)` (or of `F(x) - a`) at the stated values over `F_p`, which by Dedekind give elements of the arithmetic monodromy.

* **Theorem A (one full round).** `D = 5`. The curve `G = 0` is absolutely irreducible (`F'` has 4 simple roots, so `u` is not a square in the function field); the cycle types of `F(x) - a` at `a = 8, 1, 5` are `(5)`, `(4,1)`, `(2,1,1,1)`, so the arithmetic monodromy is `S_5`. The pair scheme `G(c,s1) = G(c,s2) = 0` is geometrically reduced and of pure dimension 1, and its part off `s1^2 = s2^2` has exactly one absolutely irreducible component defined over `F_p`: the resultant in `c` of `G(c,s1)` and `G(c,s2)` is a constant times `(s1-s2)^4 (s1+s2)^4 Phi(s1,s2)` with `Phi` of degree 8, and `Phi` is irreducible at specialisations of `s1` over `F_(p^k)` for `k = 2, 4, 8`, hence absolutely irreducible. So the hypothesis holds with `w = 1`, with no further assumption.
* **Theorem B (two full rounds).** `D = 25`, `deg H = 12`. The cycle types of `H(c,u)` at `c = 1, 9, 103` are `(12)`, `(11,1)`, `(7,1,1,1,1,1)`; a 12-cycle, an 11-cycle and a 7-cycle (7 is prime and at most 12 - 3) give, by Jordan's theorem, `A_12` inside the arithmetic monodromy, and the 12-cycle is odd, so it is `S_12`; the geometric monodromy is `A_12` or `S_12`, both 2-transitive. Hence `G = 0` is absolutely irreducible, the pair scheme is geometrically reduced of pure dimension 1, and the off-diagonal scheme `{H(c,u1) = H(c,u2) = 0, u1 != u2}` in the coordinates `(c, u1, u2)` is absolutely irreducible.
* **Theorem D (degrees).** For every `N <= 17` rounds and every listed line and schedule, the output coordinate has degree exactly `5^N` over `F_p` (the leading coefficient is an integer, nonzero mod `p`). This is the fact of section 2.3 (`deg F = D`) for the toy.
* The axis line `(L, 0, 0)` is a different case (Theorem C): there `F = R(X + c0)^5` is decomposable, its geometric monodromy is imprimitive, and the hypothesis fails (`w = 0`). The theorems above are for the generic line.

Our line is generic in this sense. The polynomial that the construction of section 2 produces is dense: in our miniature runs (`p` of 20 and of 24 bits, `r` up to 4, run twice with identical digests of the coefficient vectors) every coefficient of the digest polynomial in `W` is nonzero up to the 0 to 2 zeros expected of a random polynomial, each residue of the exponent modulo 5 and modulo 25 carries its fair share, and the polynomial `g` that the algorithm builds is dense likewise. This is evidence for `H-ONE` at one and two rounds on a generic line, with the group-theoretic certificate (an `m`-cycle, an `(m-1)`-cycle and a prime cycle of length at most `m - 3`) that proves it for any further explicit `F` it is computed for.


**Grok job 136 (first N full rounds, Orchard parameter tuple, generic line) and its re-run on the deployed constants.** Grok (xAI) computed the hypothesis of `H-GEOM-w` exactly over the Pallas field for the Orchard tuple (width 3, S-box `x -> x^5`, `R_F = 8`, `R_P = 56`) and the generic line `(L, 2L+1, 3L+5)`, for the first `N = 1, 2, 3, 4` full rounds, with the round constants and MDS produced by the Hadeshash Grain generator and the same group-theoretic certificate as in Theorems A and B (program `certify.py` of job 136, printed in Appendix F). Results: degree exactly `5^N` with a nonzero leading coefficient; `F'` has `5^N - 1` simple roots; (a) `G = 0` is absolutely irreducible and (b) the pair scheme is geometrically reduced of pure dimension 1 at `N = 1, 2, 3, 4`; `w = 1` at `N = 1` (the cofactor `Phi` of degree 8 of the eliminant is absolutely irreducible); at `N = 2` and `N = 3` the arithmetic monodromy of `H` is `S_12` and `S_62` (cycle types `(12)`, `(11,1)`, `(7,1^5)` at `c = 11, 10, 457` and `(62)`, `(61,1)`, `(59,1^3)` at `c = 57, 60, 152`), so the off-diagonal `u`-scheme is absolutely irreducible; at `N = 4` the cycle types `(312)` at `c = 349` and `(311,1)` at `c = 56` give a transitive, 2-transitive monodromy, which gives (a) and (b).

The Grain output differs from the deployed table (the organizer constants that `experiments/exp_line.py` embeds and that the runner's digest uses), so we ran the same program, unchanged, on the deployed constants and on the attack's own line: `F_N` is coordinate 0 after the first `N` S-box layers of the digest polynomial of section 2.3 (start state `alpha + beta W`; layers = rounds 2 and 3, full, then the partial rounds 4 and 5), so `F_N` has degree `5^N` and is the truncation of the polynomial `F` of the premise (`N = 14`; the line and the first layers do not depend on r). The results (`certify_dep.py`, Appendix F):

| N | layers of `F_N` | `deg F_N` | `m` | cycle types of `H(c,u)` found (value of `c`) | (a), (b) | `w` / off-diagonal scheme | monodromy of `H` |
|--:|---|--:|--:|---|:-:|---|---|
| 1 | round 2 | 5 | 2 | (2) at 3, (1,1) at 1 | yes | `w = 1` (`Phi` of degree 8 absolutely irreducible: irreducible of full degree over `F_(p^k)`, `k` = 2, 4, 8) | `S_2` |
| 2 | rounds 2, 3 | 25 | 12 | (12) at 8, (11,1) at 18, (7,1^5) at 1644 | yes | off-diagonal scheme absolutely irreducible | `S_12` |
| 3 | rounds 2, 3, 4 | 125 | 62 | (62) at 82, (61,1) at 24, (59,1^3) at 622 | yes | off-diagonal scheme absolutely irreducible | `S_62` |
| 4 | rounds 2, 3, 4, 5 | 625 | 312 | (312) at 121, (311,1) at 357 | yes | not computed | transitive and 2-transitive |

For every row the spot check of `F_N` against direct iteration of the rounds passed, the leading coefficient of `F_N` equals the one propagated through the layers (section 2.3), `F_N'` has `5^N - 1` simple roots, and `H(c,0) = F_N'(c)` at `c` = 1, 2, 5, 17. The cycle types are those of the square-free specialisations of `H(c,u)` at the stated `c`; for `N = 1` the discriminant of `H` is not a square (odd-exponent factors of degrees 2 and 2), and for `N = 4` the Jordan prime cycle `(307,1^5)` was not met in 929 specialisations (expected count 0.025), so the single-component statement is not made at `N = 4`.

So (a) and (b) hold for `F_N` at `N = 1, 2, 3, 4` on the deployed constants and the attack line, `w = 1` at `N = 1`, and the monodromy of `H` is `S_m` at `N = 2` and `N = 3`. The premise `H-ONE` (9.1) extrapolates the law of 9.3(a), a theorem at `N = 2, 3` (9.3(c)), to `N = 14`.
Under (a) and 2-transitivity of the monodromy of H, w is 1 or 2 (Grok job 137, lemma: with the arithmetic monodromy Gamma inside the hyperoctahedral group B_m, K = Gamma meet F_2^m is one of 0, <1>, E, F_2^m once pi(Gamma) contains A_m, and w = 1 exactly when K contains the even-weight subspace E, w = 2 otherwise; the witnesses of Grok job 136 establish the hypotheses). Measured on the deployed Orchard constants and the attack's own line (the F_N of proof.md 10.3, using the Frobenius cycle types of H(c, u) and their lifts to G(c, t) = H(c, t^2) over F_p): N = 1 gives K = F_2^2 and w = 1; N = 2 (m = 12) gives K = F_2^12 and w = 1, witnessed by the 12-cycle specialisations c = 8 (two 12-cycles on G, omega = 0) and c = 24 (one 24-cycle, omega = 1) and the even permutation c = 6; N = 3 (m = 62) gives K = F_2^62 and w = 1, witnessed by the 62-cycle specialisations c = 82 (omega = 0) and c = 102 (omega = 1) and the even permutation c = 1. So w = 1 at N = 1, 2, 3 on the deployed constants, a measured trend; with pi(Gamma) = S_m this gives Gamma = B_12 at N = 2 and Gamma = B_62 at N = 3, the groups used in 9.3(c).

### 10.4 Scope

One trial at r = 8 needs about 602 GB of live memory and about 23.7 times the work of an r = 6 trial. The claim is the premise `H-ONE` with the bound of section 9.2; the executed centres at r = 3, 4, 5, the experiments of 10.2 and 10.5.1, the theorems and computations of 10.3 and the measurements of 10.5 are the evidence for it.
### 10.5 Euclidean sequences on the sibling targets

The algorithm of section 4 at `r = 8` applies the Euclidean algorithm to `g_c` (degree `m = 3,051,757,812`) and `R - 1`, `R = S^((p-1)/2) mod g_c`. Stage D is charged for every remainder sequence by the proof of section 6.3, which does not use this section; this section records the sibling runs. The digest polynomial of the same family at `r' = 0` and `r' = 1` partial rounds (same constants, same line `j = 0`, `F` of degree `5^6 = 15,625` and `5^7 = 78,125`, `m = 7,812` and `39,062`) is small enough to run the stage in full with `python-flint`: for each centre `c` we built `F(c + x)`, its odd part `g_c`, `R` by powering and the complete Euclidean sequence of `(g_c, R - 1)`. Results (`sib_euclid.py`, centres `c` = 1, ..., 8 at `r' = 0` and `c` = 1, 2 at `r' = 1`): every quotient had degree 1 in all 10 runs, the sequences ended at degree 0 after `m - 1` steps (7,811 and 39,061 steps; no run had a quotient of degree other than 1), and at `r' = 0` the gcd had degree 1 (a usable root, a collision of the sibling target) at the centres 2, 4 and 7. Each `r' = 0` run takes about 20 s and each `r' = 1` run about 6 minutes on one core. The program `sib_euclid.py` is printed in Appendix F.

At `r = 8` the stages need about 602 GB and 2.1e15 operations, which the organizer sandbox (128 MiB, 20 s) does not host; the counts at this `r` are the formula counts of sections 6 and 7.

### 10.5.1 Organizer-run tests: one centre (`experiments/exp_euclid.py`)

Two experiments of kind `python-message-pairs-v1`, declared in `experiments/manifest.json` and run by the organizer's runner (program `experiments/exp_euclid.py`, 28,019 bytes, Python standard library only; the program of our entry 17a75731, unchanged): the one-centre tests `one-centre-n2-t256` and `one-centre-n3-t24` (one trial of the algorithm at depth `N = 2` and `3`, `m = 12` and `62`). For each computed trial the program takes a centre `c` from the trial seed (the rule of `exp_line.py`) and builds, exactly over `F_p`, the polynomial `F_N(c + X)`: the `F_N` of 10.3 (start state `alpha + beta W` of the line `j = 0`, the S-box layers of rounds 2 and 3 (full), then 4 (partial, coordinate 0), the MDS after each; degree `5^N`). It checks `F_N` against direct iteration of those layers at `c + 1`, `c - 1`, `c + 2`, `c - 2` and the odd-part identity `2 x g(x^2) = F_N(c + x) - F_N(c - x)` at `x = 1, 2`; takes the monic odd part `g` (degree `m = (5^N - 1)/2`); computes `R = X^((p-1)/2) mod g` (253 squarings and 45 multiplications by `X`); and runs the complete Euclidean sequence of `(g, R - 1)` down to the zero remainder; the gcd `G` has degree `k(c)`. A trial whose sequence is normal (`deg(R - 1) = m - 1` and every quotient of degree 1), with `1 <= k(c) <= 16` and an isolated root (stage E, shifts from the seed) that passes the check `F_N(c + s) = F_N(c - s)`, returns two distinct canonical messages: the points `c + s` of the line, `s = 1, 2, ...`, are mapped back to `(nk, rho)` as in 10.2(b), and the first two whose digests of the selected target agree on the first 6 bits of the big-endian reading are returned. Among 65 points such a pair always exists. Every other trial, and every trial past the first `T` (`T` = 256 and 24, the sandbox budget of 20 s), returns two nulls. The organizer-checked count of returned pairs therefore equals the number of computed trials that pass. The per-trial counts listed in the manifest are reported as observations, which the runner labels untrusted. Prediction: `Binomial(256, 0.393469)` (mean 100.7) and `Binomial(24, 0.393469)` (mean 9.4) (9.3). The test also asks for a normal sequence, which at r = 8 is not a premise (stage D is charged for every sequence, 6.3); an abnormal sequence only lowers the count. For `N <= 4` the polynomial `F_N` is the same at every round count `r >= 2` (its layers come before the final full rounds), so the tests measure the same family of polynomials as the premise; only the witness uses the digest at r = 8.

Our runs of the program's Euclidean computation (2026-10-18, seeds of our own): 1,066 sequences at `m = 12`, `62`, `312` (768, 280 and 18), every quotient of degree 1, and the gcd had positive degree in 301, 117 and 7 of them (fractions 0.392, 0.418 and 0.389, against 0.3935 of 9.3(a)). What these tests show: under trusted execution, the frequency of `E_c` on the construction's own polynomial at `m = 12` to `312`. What they do not show: anything at `m = 3,051,757,812`, where `H-ONE` remains a premise.

## 11. Appendix D: the premise arithmetic (`premise_numbers.py`)

`python3 premise_numbers.py` recomputes with exact rationals every number of sections 9.1 to 9.3 and 9.4.

#### premise_numbers.py

```python
#!/usr/bin/env python3
"""Exact-rational recomputation of the numbers of proof.md section 9 for r = 8 (standard library only).
One centre (K = 1): success >= 1 - (1 - q)^K - K (eps_coin + eps_iso + eps_O1) = q - eps_coin - eps_iso - eps_O1, q = 0.3901 (premise H-ONE)."""
import math
from fractions import Fraction as Fr
from math import comb, factorial
P = (1 << 254) + 0x224698FC094CF91B992D30ED00000001
DMAX, ZCAP, K = 16, 64, 1
Q = Fr(3901, 10000)
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
# stage C (4.3V(d)): the trial ends if g_c has a root on the evaluation set O1 (n1 = 182 * 2^24 points); for a fixed point at most 5^14 - 1 centres have it as a root
eps_O1 = Fr((182 << 24) * (5 ** 14 - 1), P)
succ = 1 - (1 - Q) ** K - K * (eps_coin + eps_iso + eps_O1)
need = Fr(39, 100) + K * (eps_coin + eps_iso + eps_O1)   # smallest q with success >= 0.39
def law(m): return 1 - sum(Fr((-1) ** j, 2 ** j * factorial(j)) for j in range(0, m + 1))   # P(k >= 1) for a uniform element of B_m
bonf4 = sum(Fr((-1) ** (j + 1), 2 ** j * factorial(j)) for j in range(1, 5))                # S1 - S2 + S3 - S4 = 151/384
wsum = sum(Fr(1, 2 ** j * factorial(j)) for j in range(1, 5))                                # 249/384
def dec(x, n): v = (Fr(x).numerator * 10 ** n) // Fr(x).denominator; t = str(v).rjust(n + 1, '0'); return t[:-n] + '.' + t[-n:]   # floor at n decimals
if __name__ == '__main__':
    print('per-round good probability w >= 1/2 - %.3e' % float(Fr(1, 2) - wq))
    print('eps_iso < %.3e (2^%.2f)   eps_coin < %.3e (2^%.2f)   eps_O1 < %.3e (2^%.2f)' % (float(eps_iso), math.log2(float(eps_iso)), float(eps_coin), math.log2(float(eps_coin)), float(eps_O1), math.log2(float(eps_O1))))
    print('q = %s, K = %d: success >= %s (floor at 18 decimals)' % (dec(Q, 4), K, dec(succ, 18)))
    print('claimed success_probability: %s (floor at 5 decimals)' % ('%.5f' % (int(succ * 100000) / 100000)))
    print('success >= 0.39 needs q >= %s (floor at 18 decimals; the next 18-decimal value is the bound of 9.1)' % dec(need, 18))
    print('law of 9.3(a): m=2 %s, m=3 %s, m=4 %s, m=12 %.10f; 1 - e^(-1/2) = %.10f' % (dec(law(2), 4), dec(law(3), 4), dec(law(4), 4), float(law(12)), 1 - math.exp(-0.5)))
    print('q below the law by %.7f' % (1 - math.exp(-0.5) - float(Q)))
    print('Bonferroni order 4: %s = %.7f; weights %s; eps <= %.7f' % (bonf4, float(bonf4), wsum, float((bonf4 - Q) / wsum)))
```

## 12. Appendix E: the stage C and stage D totals (`stage_cd.py`)

`python3 stage_cd.py` expands the two rows of section 6 that carry almost all of the cost, 446,444,428,530,905 (stage C, in the value domain, section 4.3V) and 1,076,929,687,405,216 (stage D), from the dimensions: `h = 2^24`, `K = 182`, `n1 = 3,053,453,312`, the convolution lengths 384, 768 and 256, the 30 Newton levels of the Barrett start, the 224 squaring steps, the half-gcd levels, and the kernel charges of section 4.2. It prints the operations of each step of stage C (the table of 4.3V(e)), both totals, walks every allocation and free of stages A to D (the arrays of section 4.4 included) and prints the peak of the live set of each stage and the stage-C trace of the two-ended pool (the table of 4.3V(f)), then runs the allocator of section 4.2 on the allocations and frees of one trial (the two-ended pool address by address, the slab classes by their peak counts) and prints the largest sum of the two ends of the pool after each stage, the slab area, the arena and the memory figure of section 7, and asserts all of them. The function `powx_lean` (the coefficient-domain stage C of c69ae3de) is kept in the script for comparison and is not run.

#### stage_cd.py

```python
#!/usr/bin/env python3
"""Appendix E: stage C and stage D of one trial at r = 8, expanded into their totals (standard library only).
Run:  python3 stage_cd.py      prints S_C = 446,444,428,530,905 and S_D = 1,076,929,687,405,216, the operations of each step of stage C, the peaks, the stage-C trace of the pool, the arena and the memory, and asserts them.

The inputs are the dimensions m = (5^14 - 1)/2 = 3,051,757,812 (degree of the modulus), the exponent (p-1)/2, and the charging rules of section 4.2,
which fix the per-kernel charges in the tables PASS and K3 below (butterfly 3 field operations or 2 when the twiddle is 1, twiddle load with
address, 8 operations per radix-3 leaf, loop control 3 per iteration and 2 on exit). Everything else is a finite recurrence:
  stage C (value domain, proof 4.3V; powx_vd): h = 2^24, K = 182 cosets per point set, n1 = K h; the Barrett start (Newton levels l -> min(2l, ell)); the exponent: 224 squaring steps,
           45 of them with the multiplication by X; each step = two pointwise passes + two extensions (K inner transforms of h points in place, the between-coset convolutions of length Lx = 384
           per inner position, K inner transforms); the per-step and per-extension charges are printed.  powx_lean (the coefficient-domain stage C of the filed entry c69ae3de) is kept for comparison and is not run;
  stage D: the outer loop of the Euclid driver, hgcd(k) with k halved (rounded up) until k <= 96, in each level the two recursive calls,
           apply_inv (one bilinear convolution), the division by a quotient of degree one, the 2x2 matrix product (conv_bilin_cost);
  below k <= 96 and n <= 192: classical division steps with quotient of two coefficients (divrem_naive).
`Tr` accumulates the operations and walks every allocation and free (an allocation is charged 121 + 13 (2 live + 1), a free 105; a block is 64 + 32 * slots rounded up to 64 bytes,
header included), with the live bytes and their peak, and the peak of the temporary arrays inside one call (the arrays of every division: div_walk); it also records the events of the walk: every
allocation and free with the identity of its block (the arrays given to a call by name) and, for an allocation, the list of the pool that serves its statement.
The charge of stage D is the recurrence of proof.md 6.3, evaluated node by node on the actual recursion tree (WORST_D = True): at every node of the half-gcd the normal local charge plus the charge
of one full division at that node's size (worst_div, from the divisions naive_general or the padded Newton division padded_division); the script prints the normal local total, the recurrence total and the
peak of the live set of each stage.
The arena is not the peak of the live set: the script runs the allocator of proof.md 4.2 on the events of one trial (init, A, B, C, D in the order of the program; sizes are functions of m and
the recursion shape only, the same for every input): the blocks of more than 2^BIG_EXP bytes are placed address by address by the two-ended pool (TwoEnd: two first-fit lists, the low one from the
bottom, the high one from the top; the list of an allocation statement is fixed by the marker `# pool:H` (both parities of the recursion depth of hgcd), `# pool:H0` or `# pool:H1` (depth parity
0 or 1) on the statement, and is the low list without a marker; split, coalescing; the largest sum of the two ends is the capacity of the pool), the other blocks by the slab classes (slot of 2^class
bytes, a new slot from the end of the slab area when the free list of the class is empty: the area is the sum over the classes of the peak number of live blocks times the slot), and it checks that
the events reproduce the walk (walk_check); it prints the arena and the memory figure with the code image and the stack."""
import functools, math, collections, re, sys

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
PM2, PM1H = P - 2, (P - 1) >> 1
INV_CTL, STAGE_BK, CACHE = 2310, 1000, 64


def powcost(e):
    return (e.bit_length() - 1) + (bin(e).count('1') - 1) if e > 0 else 0


PASS = {   # kernel -> for k = 1..4 layers: (c0, a, b), charge c0 + a*G + b*G*S  (G groups, S = 2^(layers below) - 1)
    'f': ((4, 17, 19), (4, 35, 43), (4, 80, 96), (4, 185, 213)),
    'i': ((4, 17, 21), (4, 36, 47), (4, 82, 102), (4, 188, 221)),
    'usq': ((3, 18, 0), (3, 49, 0), (3, 128, 0), (3, 315, 0)),
    'umul': ((4, 23, 0), (4, 58, 0), (4, 145, 0), (4, 348, 0)),
}

K3 = {   # radix-3 position kernels: K3[type][pattern of nonzero rows 0..7][rotation 0..2]
    'f': [(6,6,6),(8,14,14),(14,8,14),(19,19,25),(14,14,8),(19,25,19),(25,19,19),(24,24,24)],
    'i': [None,(10,16,16),(16,10,16),(20,20,26),(16,16,10),(20,26,20),(26,20,20),(24,24,24)],
    'r0': [(2,2,2),(4,4,4),(4,4,4),(7,7,7),(4,4,4),(7,7,7),(7,7,7),(10,10,10)],
    'r1': [(2,2,2),(4,7,7),(7,4,7),(10,10,13),(7,7,4),(10,13,10),(13,10,10),(16,16,16)],
    'r2': [(2,2,2),(4,7,7),(7,4,7),(10,10,13),(7,7,4),(10,13,10),(13,10,10),(16,16,16)],
}
ROT = ((0, 0, 0), (0, 1, 2), (0, 2, 1))      # rotation of the three kernels of a position triple, by the phase c0


def pass_fwd(a, l0, k):
    c0, p, q = PASS['f'][k - 1]; g = 1 << l0
    return 5 + (9 * k + 2) + 4 + c0 + p * g + q * g * ((1 << (a - l0 - k)) - 1)


def pass_inv(a, l0, k):
    c0, p, q = PASS['i'][k - 1]; g = 1 << l0
    return 6 + (9 * k + 2) + 4 + c0 + p * g + q * g * ((1 << (a - l0 - k)) - 1)


def pass_fused(a, k, mode):
    c0, p, q = PASS['usq' if mode == 'sq' else 'umul'][k - 1]
    return 6 + (9 * k + 2) + 6 + c0 + p * (1 << (a - k))


FREE_OPS = 105


def blk(slots):
    return 64 + ((slots * 32 + 63) & ~63)


BIG_EXP = 21                           # a block (header included) of more than 2^BIG_EXP bytes is served by the two-ended pool, every other block by its slab class (proof 4.2); a constant of the algorithm for each r
MIDPROD = 7                             # windows of the Newton division (proof 4.4): bit 2, the products e of the series inverse are middle products; bit 4, the other products of the divisions are inverse transformed only for the coefficients used; bit 1 (the cyclic form of the product (q g) of a squaring step) belongs to block mode and is not used at this r
QMIN = 7                               # smallest slab class: slots of 2^7 = 128 bytes
SLAB_ALLOC_OPS = 126                   # operations of an allocation from a slab class (proof 4.2): 125 plus the NEW_FP statement; below the charge 1 + 120 + 13 (2 L + 1) of every allocation
SLAB_FREE_OPS = 81                     # operations of a free of a slab block (proof 4.2); the charge of a free is FREE_OPS = 105
assert SLAB_ALLOC_OPS <= 1 + 120 + 13 and SLAB_FREE_OPS <= 105


class Slot(int):
    """an array of v slots together with the identity of its block, so that the walk is also the sequence of allocations and frees of the program (proof 4.2, 7)"""
    def __new__(cls, v, ident):
        o = int.__new__(cls, v); o.id = ident; return o


class Ctx:
    """identities of the blocks of one walk: the root walk, or one memoised call of hgcd (ids >= 0 local to the call, ids < 0 the arrays given to it)"""
    def __init__(self): self.n = 0


CTX_STACK = [Ctx()]


def new_id():
    c = CTX_STACK[-1]; i = c.n; c.n += 1; return i


class Rec:
    """the events of one memoised call of hgcd, recorded once: ('A', id, slots) allocation, ('F', id, slots) free, ('T', slots...) temporary arrays of one call (allocated in the
    order listed, freed in the reverse order), ('R', n, events) a self-contained group repeated n times, ('C', rec, base, args) a call of a recorded call"""
    def __init__(self, ev, nloc): self.ev = ev; self.nloc = nloc


POOL_MARK = {k + 1: re.search(r'# pool:(H[01]?)$', ln.rstrip()).group(1) for k, ln in enumerate(open(__file__, encoding='utf-8').read().split(chr(10))) if re.search(r'# pool:(H[01]?)$', ln.rstrip())}
PAR = [0]              # parity of the depth of the recursion of hgcd in which the statement being evaluated runs (0 outside hgcd)


def _site(depth):
    """the list of the pool that serves the allocation statement that called: 1 (high list) for the statements marked `# pool:H` in this file, and for the statements marked `# pool:H0` or `# pool:H1` when the parity
    of the depth of the recursion of hgcd (PAR) is 0 or 1 respectively; else 0 (low list); a constant of the statement and of the parity"""
    f = sys._getframe(depth); mk = POOL_MARK.get(f.f_lineno) if f.f_code.co_filename == __file__ else None
    return 1 if (mk == 'H' or mk == 'H%d' % PAR[0]) else 0


class Tr:
    """sequential trace: ops, current live bytes/blocks relative to entry, peaks, and the events (allocations and frees) of the walk"""
    __slots__ = ('ops', 'cur', 'peak', 'cnt', 'pcnt', 'base', 'ev')

    def __init__(self, base=0):
        self.ops = 0; self.cur = 0; self.peak = 0; self.cnt = 0; self.pcnt = 0; self.base = base; self.ev = []

    def here(self): return self.base + self.cnt            # live blocks now (for sub-traces)

    def bump(self, slots):                                  # peak of a temporary array of `slots` elements that is live only inside one call (no operation charged)
        if slots > 0:
            self.peak = max(self.peak, self.cur + blk(slots)); self.pcnt = max(self.pcnt, self.cnt + 1)
            self.ev.append(('T', (int(slots),), _site(2)))

    def bump_blocks(self, slot_list):                       # peak of several temporary arrays live together inside one call (no operation charged)
        self.peak = max(self.peak, self.cur + sum(blk(x) for x in slot_list)); self.pcnt = max(self.pcnt, self.cnt + len(slot_list))
        if slot_list: self.ev.append(('T', tuple(int(x) for x in slot_list), _site(2)))

    def bump_walk(self, W):                                 # the walk W of the temporary arrays of one call, started at the current live set (no operation charged): its allocations and frees are events of this walk
        if W is not None:
            self.peak = max(self.peak, self.cur + W.peak); self.pcnt = max(self.pcnt, self.cnt + W.pcnt)
            self.ev.extend(W.ev)

    def ctl(self, n): self.ops += n
    def ld(self, n): self.ops += 2 * n
    def st(self, n): self.ops += 2 * n
    def loopc(self, n): self.ops += 3 * n + 2

    def add(self, o):
        self.ops += o.ops
        self.peak = max(self.peak, self.cur + o.peak); self.pcnt = max(self.pcnt, self.cnt + o.pcnt)
        self.cur += o.cur; self.cnt += o.cnt
        self.ev.extend(o.ev)

    def new_fp(self, slots):
        slots = max(slots, 1) if slots else 1
        self.ops += 1 + 120 + 13 * (2 * (self.base + self.cnt) + 1)
        b = blk(slots); self.cur += b; self.cnt += 1
        self.peak = max(self.peak, self.cur); self.pcnt = max(self.pcnt, self.cnt)
        i = new_id(); self.ev.append(('A', i, int(slots), _site(2)))
        return Slot(slots, i)

    def free(self, slots):
        self.ops += FREE_OPS
        self.cur -= blk(slots); self.cnt -= 1
        self.ev.append(('F', slots.id, int(slots)))


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


def for8(n):                           # FOR8 / for8_ctl charge of the loop control
    return 1 + 3 * (n // 8) + 2 + 3 * (n % 8) + 2


def make_plan(rows, a):
    p = Plan(rows, a)
    c = 18 + 4 + (3 * p.np + 2) + 4 * p.np + 2 + (4 if rows == 3 else 0)
    return p, c


def plan3_for_len(ln):
    c = 0
    for a in range(2, 64):
        c += 3 + 1 + 2 + 2
        if 3 * (1 << a) >= ln:
            p, cc = make_plan(3, a); return p, c + cc
    raise ValueError


def split_regions(n, N, boff, lenB):
    c = 3; bp = [0]
    nt0 = 0
    for t in range(3):
        st = nt0 + N - boff
        if st >= N: st -= N
        nt0 += n; c += 9
        c += 3
        if st < lenB:
            x = lenB - st; c += 1; c += 3
            if 0 < x < n: bp.append(x); c += 1
        c += 3
        if st > 0:
            x = N - st; c += 1; c += 3
            if 0 < x < n: bp.append(x); c += 1
            x = N + lenB - st; c += 2; c += 3
            if 0 < x < n: bp.append(x); c += 1
    c += 2
    bp.append(n); c += 1
    cnt = len(bp)
    for a in range(1, cnt):
        key = bp[a]; b = a - 1; c += 3 + 2
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
    c += 2
    c += 2
    if hi > i:
        rem = hi - i; c += 1
        c += K[0]; i += 1; c += 1
        c += 2
        if rem == 2:
            c += K[1]
    return c


def stageA_fwd(Pl, ln):
    c = 4
    n = Pl.n
    if Pl.rows == 1:
        raise NotImplementedError('plain rows==1 forward copy is not used on the charged path')
    bp, pat, cc = split_regions(n, Pl.N, 0, ln); c += cc
    c += 2
    for q in range(len(pat)):
        c += 4 + driver('f', pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def stageA_inv(Pl, outlen):
    if Pl.rows == 1:
        return 0
    c = 2
    bp, pat, cc = split_regions(Pl.n, Pl.N, 0, outlen); c += cc
    c += 2
    for q in range(len(pat)):
        c += 2
        if pat[q] == 0:
            c += 3; continue
        c += 4 + driver('i', pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def stageA_row(Pl, r, lenB, boff):
    n = Pl.n
    bp, pat, c = split_regions(n, Pl.N, boff, lenB)
    c += 2
    for q in range(len(pat)):
        c += 3 * 11 + 2 + 4 + driver('r%d' % r, pat[q], Pl.c0, bp[q], bp[q + 1]) + 3
    return c + 2


def fwd_passes(Pl, cnt):
    l0 = 0; c = 0
    for p in range(cnt):
        c += pass_fwd(Pl.a, l0, Pl.kk[p]) + 4; l0 += Pl.kk[p]
    return c


def inv_passes(Pl, first):            # inverse passes p = first down to 0
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
    c = stageA_fwd(Pl, ln)
    c += Pl.rows * conv_core_row(Pl, 'sq') + 2
    return c + stageA_inv(Pl, outlen)


def mulc_otf_row(Pl, r, lenB, boff):
    c = 12 + stageA_row(Pl, r, lenB, boff)
    c += fwd_passes(Pl, Pl.np) + 2
    c += fwd_passes(Pl, Pl.np - 1) + fused(Pl, 'mul') + inv_passes(Pl, Pl.np - 2) + 4
    return c


def conv_mulc_otf(Pl, ln, lenB, boff, outlen):
    c = 2 + stageA_fwd(Pl, ln) + 4
    for r in range(3):
        c += mulc_otf_row(Pl, r, lenB, boff)
    return c + 2 + stageA_inv(Pl, outlen)


def pw_loop(n, mode):
    return for8(n) + n * (7 if mode == 0 else 10)


def conv_bilin_cost(Pl, nout, outlen, groups, hboff=0):
    c = 2
    eps = [0] * nout
    c += 2 + 3 * nout
    for g in groups:
        for s in range(len(g['S'])):
            for h in range(len(g['H'])):
                c += 6
                o, sg = g['prod'].get((s, h), (-1, 0))
                if o >= 0 and not eps[o]:
                    eps[o] = sg
    for r in range(3):
        c += 2 + 2 + nout + 1
        done = [0] * nout
        for g in groups:
            c += 7
            for lh in g['H']:
                c += 6 + stageA_row(Pl, r, lh, hboff) + fwd_passes(Pl, Pl.np)
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
        c += 0
    for k in range(nout):
        c += 3
        if eps[k]:
            c += stageA_inv(Pl, outlen[k])
    return c, eps


def ebit(E, i): return (E >> i) & 1


def powx_lean(m, b, E=PM1H):
    T = Tr(b)
    PN, c1 = plan3_for_len(2 * m - 1); PNp, c2 = plan3_for_len(m + 1)
    T.ctl(c1 + c2)
    N, Np = PN.N, PNp.N
    sY = T.new_fp(N)
    sT = T.new_fp(PN.n)
    sM = T.new_fp(m - 1)
    # newton_lean
    L = m - 1
    T.ld(L); T.st(L); T.loopc(L); T.ctl(L)
    T.ctl(4 + 8); T.st(1)
    l = 1
    while l < L:
        l2 = min(2 * l, L)
        T.ctl(8)
        P1, c = plan3_for_len(l2 + l - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P1, l, l2, 0, l2))
        T.ctl(plan_invN_ops(P1))
        T.ops += l2 - l                                       # pl_run MULC
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        P2, c = plan3_for_len(l2 - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P2, l2 - l, l, 0, l2 - l))
        T.ctl(plan_invN_ops(P2))
        T.ops += 2 * (l2 - l)                                 # pl_run NEGMULC: mul + sub per element
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        l = l2
    T.ld(L); T.st(L); T.loopc(L // 2); T.ctl(2 * (L // 2))
    # prefix + scale
    T.ctl(plan_invN_ops(PN)); T.ctl(plan_invN_ops(PNp)); T.ops += 1
    T.ops += m - 1; T.ld(m - 1); T.st(m - 1); T.loopc(m - 1)
    gamma = N - (m - 2)
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
    step = conv_sq(PN, m, 2 * m - 1) + 8
    step += for8(lim) + 7 * lim + for8(m - lim) + 4 * (m - lim) + for8(m - 1) + 4 * (m - 1)
    step += conv_mulc_otf(PN, m - 1, m - 1, gamma, m - 1) + conv_mulc_otf(PNp, m - 1, m + 1, 0, m)
    step += for8(m) + 7 * m
    step += 14 + 6
    mulx = 2 + for8(m - 1) + 8 * (m - 1) + 2 + 4
    nset = sum(ebit(E, b) for b in range(bit))
    T.ops += steps * step + nset * mulx
    T.ops += 1 + m; T.ld(m); T.st(m); T.loopc(m)
    T.ctl(2 + 500)
    T.free(sY); T.free(sT); T.free(sM)
    info = dict(steps=steps, nset=nset, PN=PN, PNp=PNp, step=step, mulx=mulx)
    return T, info



BIGA = 32                              # v2(p-1) = 32: transform sizes 3*2^a exist in F_p for a <= 32 only


def pad23(n):
    """the smallest 2^a or 3 * 2^a (a <= 32) that is at least n"""
    best = None
    for a in range(0, 33):
        for c in (1, 3):
            v = c << a
            if v >= n and (best is None or v < best): best = v
    assert best is not None, n
    return best


# ---------------------------------------------------------------- stage C in the value domain (VDC = 1): pos_vdc pricing, the method of bradcush 1aa56884 (its proof 4.6), charged in this model's primitives
# The residue is held by its values on O1 = C_0 u ... u C_(K-1) and O2 = C_K u ... u C_(2K-1), C_k = 5^k H, H the subgroup of order h = 2^32, K = ceil((m+1)/h), n1 = K h >= m + 1
# (each of O1, O2 is the union of K cosets, n1 points).  A squaring step is two pointwise passes and two extensions (change of point set); an extension is an inner transform of h
# points per coset (one row of the passes of 4.2, in place) and, per inner position, one cyclic convolution over the coset index with a fixed kernel (Lagrange interpolation at the
# geometric nodes z^k, z = 5^h).  The convolutions of a group of VCNT positions run in a group buffer with one row of L elements per position (position-major: the copies into and out
# of it are strided, one address operation per element charged); each row is one cyclic convolution of L points with the stored spectrum of the kernel, charged by the row kernels of
# this model (conv_core_row: forward passes, the fused pass with the pointwise product by the stored spectrum, inverse passes; for L = 3 * 2^a with the radix-3 input and output
# stages stageA_fwd / stageA_inv, as conv_sq does).
VDC = 1              # stage C in the value domain (this entry, proof 4.3V); 0 = the coefficient-domain squaring of the filed r = 8 entry (powx_lean above)
VD_H = 1 << 24       # h = 2^24: the order of the subgroup H (proof 4.3V); the inner transform of h points is one row of passes (plan rows = 1, a = 24), in place on a coset
VCNT = 1 << 10       # inner positions per group of the geometric phase
VSHIFT = 2           # the start monomial is S^v, v = (the largest power of two below m) >> VSHIFT, a multiple of h: VSHIFT more squaring steps, a shorter Newton reciprocal
VD_CALL = 10         # one call of an inner transform: the coset address (a multiplication and an addition), the plan and twiddle arguments, call and return
VD_ROW = 16          # one row of a group copy with a running factor: the factor and its step loaded (LD 2 = 4), the factor stored back (ST 1 = 2), two addresses (4), call, entry, exit (6)
VD_ROWC = 12         # one row of a group copy with a per-row constant: the constant loaded (2), two addresses (4), call, entry, exit (6)
VD_PWC = 14          # one coset of a pointwise pass: its constants loaded (1/M(n_k), u_k, the factor of the coset) and the addresses
VD_GROUP = 20        # one group of the geometric phase: its position offset, the buffer and table addresses, the calls
VD_SPLIT = 0         # pos_leand: g and R in two pieces: the base of a coset is selected (a comparison and a branch) at every coset access of a pass (2), else 0


def vd_active(m):
    """the value-domain stage C is used (VDC = 1) where it is defined: either the start monomial v (the largest power of two below m, shifted by VSHIFT) is a multiple of h,
    or h covers the whole residue in one coset (K = 1, h >= m + 1, bradcush 4bcabff8): the start monomial x^v is replaced by X^(v)(X^h mod g - 1) and v need not divide h"""
    return bool(VDC) and 1 <= VD_H.bit_length() - 1 <= BIGA and (m.bit_length() - 1 - VSHIFT >= VD_H.bit_length() - 1 or VD_H >= m + 1)


def vd_plan(L):
    """the plan of a cyclic convolution of L = 2^a or 3 * 2^a points (a <= 32: the roots of unity exist in F_p)"""
    rows = 3 if L % 3 == 0 else 1
    a = (L // rows).bit_length() - 1
    Pl, c = make_plan(rows, a)
    assert Pl.N == L and a <= BIGA, L
    return Pl, c


def vd_inv1():
    """one field inversion (fp_inv): the power p - 2 and its control"""
    return powcost(PM2) + INV_CTL


def vd_dims(m, E=PM1H):
    """the dimensions of the value-domain stage C for the modulus degree m: K, n1, the convolution lengths, the start exponent v, the steps, the Barrett length ell"""
    h = VD_H; K = -(-(m + 1) // h); n1 = K * h
    assert n1 >= m + 1                                                     # O1 and O2 each hold n1 >= m + 1 points: a polynomial of degree <= m is determined by its values
    Lx = pad23(2 * K)                                                      # extensions and interpolations (indices <= 2K - 1 < Lx, no wrap into the outputs)
    Le = None if K == 1 else (pad23(3 * K - 1) if 3 * K - 1 <= 3 << BIGA else None)   # K=1: no geometric phase; one chirp evaluation of g at the 2K nodes; None: two evaluations of K nodes at Lx
    top = 255; zc = 0
    while top > 0 and not ebit(E, top): top -= 1; zc += 1
    v = 1; bit = top; vb = 0
    while bit >= 1 and ((v << 1) | ebit(E, bit - 1)) < m:
        v = (v << 1) | ebit(E, bit - 1); bit -= 1; vb += 1
    for _ in range(VSHIFT):
        assert ebit(E, bit) == 0
        v >>= 1; bit += 1
    assert v & (v - 1) == 0 and (v % h == 0 or h >= m + 1)                 # x^v = u_k^v on the coset C_k (K>1); K=1 (h >= m+1): the start X^(v)(X^h mod g - 1), v need not divide h
    ell = v + n1 - m + 1                                                   # q = floor(X^v P1 / g) has ell = deg + 1 coefficients
    Kq = -(-ell // h); Lq = pad23(Kq + K - 1)
    return dict(h=h, K=K, n1=n1, Lx=Lx, Le=Le, v=v, steps=bit, top=top, zc=zc, vb=vb, ell=ell, Kq=Kq, Lq=Lq,
                nset=sum(ebit(E, i) for i in range(bit)))


def vd_gslots(m):
    """the array of g (stages A to D): n1 slots; the values of g on O2 are written into it in place (stage C, step 2) and it goes to stage D as g in coefficient form"""
    return vd_dims(m)['n1']


def vd_conv(Pl, kin, outlen):
    """one cyclic convolution of one position's row (kin live inputs) with a stored kernel spectrum: rows = 1: the zero fill of the other L - kin entries and the row kernels in place;
    rows = 3: the radix-3 input stage from the row into the transform buffer, the three row convolutions, the output stage back into the row (outlen outputs); 5: the position loop and address"""
    if Pl.rows == 1:
        z = Pl.N - kin
        return 5 + 2 * z + for8(z) + conv_core_row(Pl, 'mul')
    return 5 + stageA_fwd(Pl, kin) + 3 * conv_core_row(Pl, 'mul') + 2 + stageA_inv(Pl, outlen)


def vd_rows(cnt, rows, per, row_over):
    """rows of cnt elements copied between a coset array and the group buffer: per element `per` (running factor: a load, the multiplication by the factor, the multiplication of
    the factor by its step, a store, the strided address = 7; per-row constant: a load, a multiplication, a store, the strided address = 6), per row row_over, loops by the eight-element rule"""
    return rows * (row_over + VD_SPLIT + for8(cnt) + per * cnt) + 3 * rows + 2


def vd_phase(per_group):
    ng = VD_H // VCNT
    return ng * (VD_GROUP + per_group) + 3 * ng + 2


def vd_reset(rows):
    """the running factors of a phase set from their base table: per row a load and a store, the loop"""
    return 7 * rows + 2


def vd_scale(n):
    """one running-factor pass over n elements (per element: a load, the multiplication by the factor, the multiplication of the factor by its step, a store, the strided address = 7),
    the loop by the eight-element rule, the entry and exit: the coset-change twiddle of the single-coset (K = 1) extension and the u_k^j scalings of its evaluation / interpolation"""
    return 5 + for8(n) + 7 * n


def vd_ext(K, Px):
    """the geometric phase of one extension (O1 -> O2 or O2 -> O1): K rows in with their factors, one convolution per position, K rows out with their factors.
    K = 1 (bradcush 4bcabff8, a single coset holds the whole residue): no between-coset convolution; the change of point set is the coset-change twiddle folded between the inverse and
    forward inner transforms of `ext`, one running-factor pass over the h coefficients."""
    if K == 1:
        return vd_scale(VD_H)
    return 2 * vd_reset(K) + vd_phase(vd_rows(VCNT, K, 7, VD_ROW) + VCNT * vd_conv(Px, K, 2 * K) + vd_rows(VCNT, K, 7, VD_ROW))


def vd_eval(kin, kout, Pl):
    """chirp evaluation of kin coefficient rows at kout geometric nodes: rows in with a per-row constant, one convolution with the chirp per position, kout rows out with their factors.
    kin = kout = 1 (K = 1): one geometric node, the chirp correlation is the identity; only the per-coefficient u_0^j scaling remains (one running-factor pass over h)."""
    if kin == 1 and kout == 1:
        return vd_scale(VD_H)
    return vd_reset(kout) + vd_phase(vd_rows(VCNT, kin, 6, VD_ROWC) + VCNT * vd_conv(Pl, kin, kin + kout - 1) + vd_rows(VCNT, kout, 7, VD_ROW))


def vd_interp(K, Px):
    """interpolation at K geometric nodes back to coefficient form: rows in with their factors, the chirp correlation, the K results moved with a per-index constant (two loads, a
    multiplication, a store), the correlation with the coefficients of M, rows out with a per-row constant.
    K = 1: one node, both correlations are the identity; the inverse inner transform returns the coefficients directly, only the u_0^{-j} scaling remains (one running-factor pass over h)."""
    if K == 1:
        return vd_scale(VD_H)
    mid = vd_conv(Px, K, 2 * K - 1) + 7 * K + for8(K) + 4 + vd_conv(Px, K, 2 * K)
    return vd_reset(K) + vd_phase(vd_rows(VCNT, K, 7, VD_ROW) + VCNT * mid + vd_rows(VCNT, K, 6, VD_ROWC))


def vd_inner(ncos, inv, PH):
    """ncos inner transforms of h points, one per coset, in place (the first pass may read another array: the same charges)"""
    one = inv_passes(PH, PH.np - 1) if inv else fwd_passes(PH, PH.np)
    return ncos * (one + VD_CALL + VD_SPLIT) + 3 * ncos + 2


def vd_pw(ncos, per):
    """a pointwise pass over ncos cosets of h values: per element `per`, per coset VD_PWC, loops by the eight-element rule"""
    return ncos * (VD_PWC + VD_SPLIT + for8(VD_H) + per * VD_H) + 3 * ncos + 2


def vd_batch_inv(ncos):
    """-1/g in place on ncos cosets (Montgomery's batch inversion): per coset the prefix products into the auxiliary array (a load, a multiplication, a store), one inversion and its
    zero test (a zero prefix ends the trial: g vanishes on O1), the backward pass (two loads, two multiplications, the negation, a store), 20 for the coset"""
    h = VD_H
    return ncos * (20 + VD_SPLIT + for8(h) + 5 * h + vd_inv1() + 2 + for8(h) + 9 * h) + 3 * ncos + 2


def vd_spectrum(Pl, nent):
    """a fixed kernel of L points: nent entries computed (each charged as one inversion and 20 operations), the rest zero (rows = 1: zero fill; rows = 3: the radix-3 input stage reads
    the nent entries only), the forward transform (all passes: the fused pass of vd_conv multiplies by it)"""
    c = nent * (vd_inv1() + 20) + 4
    if Pl.rows == 1:
        z = Pl.N - nent
        return c + 2 * z + for8(z) + fwd_passes(Pl, Pl.np)
    return c + stageA_fwd(Pl, nent) + 3 * fwd_passes(Pl, Pl.np)


VD = {}              # description of the last value-domain stage C (filled by powx_vd)
VD_STEPS = []        # (step, operations so far) at the end of each step of powx_vd


def _mark(T, name): VD_STEPS.append((name, T.ops))


def powx_vd(m, b, E=PM1H, sg=None):
    """stage C in the value domain.  Entry: g in coefficient form in the caller's array sg of n1 slots (stage A; its slots above m are zeroed here).  Exit: R = S^E mod g in an array of
    n1 slots (the first allocation of the stage, at the low end) and g in coefficient form in sg; both go to stage D.  Returns (Tr, info)."""
    T = Tr(b); VD_STEPS.clear()
    d = vd_dims(m, E)
    h, K, n1, ell, Kq = d['h'], d['K'], d['n1'], d['ell'], d['Kq']
    assert sg is not None and (sum(int(x) for x in sg) if isinstance(sg, tuple) else int(sg)) == n1
    PH, c0 = make_plan(1, h.bit_length() - 1); assert PH.N == h
    Px, c1 = vd_plan(d['Lx']); Pq, c2 = vd_plan(d['Lq'])
    Pe, c3 = vd_plan(d['Le']) if d['Le'] else (None, 0)
    T.ctl(c0 + c1 + c2 + c3)
    T.ctl(12 * d['zc'] + 25 * d['vb'] + 4 * VSHIFT)                        # the exponent: its leading bit, the start monomial, the shift
    # tables (per trial): 30 K constants (u_k, 1/u_k, the base factors of the copies, 1/M(n_k), u_k^v M(n_k), M'(z^k)^-1, M(z^(K+t)), M2'^-1, M2(z^t) z^-t, the chirp scales, the
    # coefficients mu_i of M), each charged as two inversions and 60 operations; the table of omega^i in transform order (h entries); the kernel spectra
    if K == 1:
        spec = []                                                          # K = 1: a single coset holds the whole residue; there is no geometric-phase convolution, so no kernel spectra
    else:
        spec = [(Px, 2 * K), (Pq, Kq + K - 1), (Px, 2 * K - 1), (Px, K + 1)]   # extension kernel; chirp of the evaluation of q; chirp of the interpolation; the coefficients of M
        if Pe: spec.append((Pe, 3 * K - 1))                               # chirp of the evaluation of g at the 2K nodes (one convolution of length Le)
    NTAB = 30 * K
    sR2 = T.new_fp(n1)                                                    # R on O2, then R in coefficient form for stage D: the first allocation of the stage, at the bottom of the low end
    sTab = T.new_fp(NTAB + h + sum(P_.N for P_, _ in spec))
    T.ctl(NTAB * (2 * vd_inv1() + 60) + 10 * h + sum(vd_spectrum(P_, n_) for P_, n_ in spec))
    Lmax = max([P_.N for P_, _ in spec] or [1])
    sB1 = T.new_fp(VCNT * Lmax)                                           # the group buffer: one row of Lmax elements per position
    sBT = T.new_fp(Lmax) if any(P_.rows == 3 for P_, _ in spec) else None # the transform row of a convolution of 3 * 2^a points
    zg = n1 - (m + 1); T.st(zg); T.ctl(for8(zg))                          # the slots of g above its m + 1 coefficients are zeroed (the rows of g are read whole in step 2)
    sR1 = T.new_fp(n1)                                                    # q (its first ell elements) from step 1 to step 3, then R~ on O1 (or u0 on O1 / O2)
    _mark(T, '(0) plans, tables and kernel spectra, the arrays of the stage')
    # (1) Barrett start: the reciprocal of the reversed g modulo X^ell (Newton, the products of 4.5), then q = rev(rev(X^v P1) mod X^ell * reciprocal mod X^ell)
    sG = T.new_fp(ell)  # pool:H
    sM = T.new_fp(ell)  # pool:H
    L = ell
    # For VD_H < 2^32 the final Newton products can be padded above ell.
    # Keep the paper-account work buffer large enough for every one-transform product.
    Ymax = L
    _yl = 1
    while _yl < L:
        _yl2 = min(2 * _yl, L)
        _yp1, _ = plan3_for_len(_yl2 + _yl - 1)
        _yp2, _ = plan3_for_len(_yl2 - 1)
        Ymax = max(Ymax, _yp1.N, _yp2.N)
        _yl = _yl2
    sY = T.new_fp(Ymax)  # pool:H
    T.ld(L); T.st(L); T.loopc(L); T.ctl(L)                                # the reversed top ell coefficients of g
    T.ctl(4 + 8); T.st(1)
    l = 1
    while l < L:
        l2 = min(2 * l, L)
        T.ctl(8)
        P1, c = plan3_for_len(l2 + l - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P1, l, l2, 0, l2))
        assert P1.a > BIGA or P1.N <= Ymax                              # a product that fits one transform uses Y as its transform buffer
        assert P1.a <= BIGA                                              # every product of the Barrett start fits one transform at r = 8
        T.ctl(plan_invN_ops(P1))
        T.ops += l2 - l
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        P2, c = plan3_for_len(l2 - 1); T.ctl(c)
        T.ctl(conv_mulc_otf(P2, l2 - l, l, 0, l2 - l))
        assert P2.a > BIGA or P2.N <= Ymax
        assert P2.a <= BIGA
        T.ctl(plan_invN_ops(P2))
        T.ops += 2 * (l2 - l)
        T.ld(l2 - l); T.st(l2 - l); T.loopc(l2 - l); T.ctl(l2 - l)
        l = l2
    T.free(sY); T.free(sG)
    PQ, c = plan3_for_len(2 * ell - 1)
    sTt = T.new_fp(max(ell, PQ.N))  # pool:H; include the padded final product transform
    T.st(ell); T.ctl(for8(ell)); T.ctl(Kq * (vd_inv1() + 30))              # rev(X^v P1) mod X^ell: zero fill, the Kq coefficients mu_i at the multiples of h
    T.ctl(c)
    T.ctl(conv_mulc_otf(PQ, ell, ell, 0, ell))                            # q (reversed) into the first ell elements of R1, window [0, ell)
    assert PQ.a <= BIGA
    T.ctl(plan_invN_ops(PQ))
    T.free(sTt); T.free(sM)
    T.ld(ell); T.st(ell); T.loopc(ell // 2); T.ctl(2 * (ell // 2))          # reversal of q in place
    _mark(T, '(1) Barrett start: the reciprocal of rev(g) mod X^ell (Newton) and q = floor(X^v M1 / g)')
    # (2) g on O1 (array G1) and on O2 (in place in the array of g): chirp evaluation of the K coefficient rows, the 2K forward inner transforms
    sG1 = T.new_fp(n1)
    if Pe: T.ctl(vd_eval(K, 2 * K, Pe))
    else: T.ctl(2 * vd_eval(K, K, Px))                                    # no length >= 3K - 1: the nodes of O1 and of O2 in two evaluations
    T.ctl(vd_inner(2 * K, False, PH))
    _mark(T, '(2) g on O1 and O2: chirp evaluation of its K coefficient rows at the 2K nodes, 2K inner transforms')
    # (3) R~_0 = X^v P1 mod g on O2: q evaluated at the K nodes of O2 into R2, the forward inner transforms, R2 := u_k^v M(n_k) - R2 * G2 (8 per element)
    zq = Kq * h - ell; T.st(zq); T.ctl(for8(zq))                          # the tail of the last row of q in R1
    T.ctl(vd_eval(Kq, K, Pq) + vd_inner(K, False, PH) + vd_pw(K, 8))
    _mark(T, '(3) R~_0 = X^v M1 - q g on O2: q at the K nodes of O2, K inner transforms, one pointwise pass')
    # (4) R~_0 on O1: inverse inner transforms of O2 reading R2 and writing R1, the extension O2 -> O1 in place on R1, the forward inner transforms
    ext = vd_inner(K, True, PH) + vd_ext(K, Px) + vd_inner(K, False, PH)
    T.ctl(ext)
    _mark(T, '(4) R~_0 on O1: one extension O2 -> O1')
    # (5) -1/g on O1, in place in G1 (auxiliary array of h elements); a zero prefix product ends the trial
    sAux = T.new_fp(h); T.ctl(vd_batch_inv(K)); T.free(sAux)
    _mark(T, '(5) -1/g on O1: K batch inversions')
    # (6) the squaring loop, one step per bit b of E below the start: (i) R1 := R1^2 G1 (8); (ii) extension O1 -> O2 in place on R1; (iii) R2 := x^b (R2^2 + R1 G2) / M(n_k)
    # (12, 16 when b = 1: omega^i loaded, multiplied by u_k, the product by x); (iv) extension O2 -> O1 from R2 into R1; 20 for the step
    step0 = vd_pw(K, 8) + ext + vd_pw(K, 12) + ext + 20
    step1 = vd_pw(K, 8) + ext + vd_pw(K, 16) + ext + 20
    steps, nset = d['steps'], d['nset']
    T.ctl((steps - nset) * step0 + nset * step1)
    _mark(T, '(6) the 224 squaring steps (45 with the multiplication by X)')
    # (7) leaving the Montgomery form: R1 := R1 G1 (7), the extension O1 -> O2, R2 := (R2 + R1 G2) / M(n_k) (11): R2 holds R = S^E mod g on O2
    T.ctl(vd_pw(K, 7) + ext + vd_pw(K, 11))
    T.free(sR1); T.free(sG1)
    _mark(T, '(7) leaving the Montgomery form: one pointwise pass, one extension O1 -> O2, one pointwise pass')
    # (8) R (in R2) and g (in the array of g) back to coefficient form, in place: inverse inner transforms, interpolation at the K nodes of O2
    interp = vd_inner(K, True, PH) + vd_interp(K, Px)
    T.ctl(2 * interp)
    if sBT is not None: T.free(sBT)
    T.free(sB1); T.free(sTab)
    T.ctl(2 + 500)
    _mark(T, '(8) R and g back to coefficient form: K inverse inner transforms and one interpolation each; the frees of the stage')
    VD.clear(); VD.update(d, ext=ext, step0=step0, step1=step1, interp=interp, Lmax=Lmax, NTAB=NTAB)
    info = dict(steps=steps, nset=nset, PN=Px, PNp=PH, step=step0, mulx=step1 - step0, sg2=sg, sR2=sR2, vd=dict(VD))
    return T, info


# ---------------------------------------------------------------- hgcd.c on shapes (normal Euclid; with WORST_D the worst-case recurrence of proof.md 6.3)
WC_MEM = False       # worst-case live set of stage D: the quotient array of every division at its largest length and the working arrays of the Newton division
WORST_D = False      # worst-case recurrence of stage D: at every node of the half-gcd tree the normal local charge plus the charge of one full division at that node (proof.md 6.3)

# full division at a node: the charge of divrem_any by the model's own routines (schoolbook division, or the Newton division = one series inverse + two products)
CMUL_INNER = 12      # one inner step of the schoolbook division: mul, sub, LD(2) = 4, ST(1) = 2, loop 3, index 1 -> 1 + 1 + 4 + 2 + 3 + 1
CMUL_OUTER = 15
SMALL_EUCLID = 12 * (2 * 96 + 1) ** 2 + 20 * (2 * 96 + 1) + 400000      # closing loop of poly_gcd_own with n <= 192: Euclid with arbitrary quotients, quadratic bound


def naive_general(lx, ly):
    """poly_divrem_naive on the general path: lx coefficients by ly, quotient of lx - ly + 1 coefficients"""
    dq1 = lx - ly + 1
    return 3 + 7 * lx + powcost(PM2) + INV_CTL + dq1 * ((ly - 1) * CMUL_INNER + CMUL_OUTER)


def prod_cost(la, lb, outlen, ws=0, out=None):
    """product of la by lb coefficients whose support has outlen coefficients (outlen = la + lb - 1, or the length of the true product when high zeros are padded).
    Default: all outlen coefficients are placed.  Window (MIDPROD): only the out coefficients from position ws are placed (out = None: all of them).
    ws = 0: the transform has at least outlen points (no wrap-around) and only the first out coefficients are inverse transformed and placed.
    ws > 0 (middle product, Hanrot-Quercia-Zimmermann 2004): the product is formed cyclically with N >= max(ws + out, outlen - ws) points; the coefficients of positions >= N wrap onto
    positions < outlen - N <= ws, below the window, so the window is exact; the operand H is read shifted by N - ws so that the window starts at position 0"""
    if out is None: out = outlen - ws
    if ws == 0 and out == outlen: need = outlen
    else:
        need = outlen if ws == 0 else max(ws + out, outlen - ws)
        assert ws + out <= need and outlen - ws <= need or ws == 0
    Pl, c = plan3_for_len(max(need, 2))
    g = dict(H=[lb], S=[la], prod={(0, 0): (0, 1)})
    cc, eps = conv_bilin_cost(Pl, 1, [out], [g], (Pl.N - ws) % Pl.N if ws else 0)
    return c + cc + plan_invN_ops(Pl) + 3 * out + 20          # product + scaling/placement + control


def series_inverse_cost(lf, k):
    c = 0; t = 1
    while t < k:
        t2 = min(2 * t, k); lft = min(lf, t2); m2 = t2 - t
        if MIDPROD & 2: p1 = prod_cost(lft, t, lft + t - 1, t, m2)                      # middle product: only the coefficients t .. t2 - 1 of g_(t2) phi_t are used
        else: p1 = prod_cost(lft, t, lft + t - 1)
        p2 = prod_cost(m2, m2, 2 * m2 - 1, 0, m2) if MIDPROD & 4 else prod_cost(m2, m2, 2 * m2 - 1)     # only the first m2 coefficients of phi e are used
        c += p1 + p2 + 12 * m2 + 12 * m2 + 40
        t = t2
    return c


def fast_division(la, lb):
    k = la - lb + 1
    return (powcost(PM2) + INV_CTL + 8 * k + 8 * lb + series_inverse_cost(min(lb, k), k)
            + (prod_cost(k, k, 2 * k - 1, 0, k) + prod_cost(k, lb, la, 0, lb - 1) if MIDPROD & 4 else prod_cost(k, k, 2 * k - 1) + prod_cost(k, lb, la)) + 8 * la + 400)


def div_cost(la, lb):
    """divrem_any: schoolbook if the quotient has at most 64 coefficients or the divisor at most 64, else the Newton division"""
    k = la - lb + 1
    if k <= 64 or lb <= 64: return naive_general(la, lb)
    return fast_division(la, lb)


@functools.lru_cache(maxsize=None)
def padded_division(la, kmax):
    """the charge of the re-centering division in its padded form (10-17, ruling 643de050 H-COST-DIV-MAX), for the Newton range 64 <= dq <= dmax = min(kmax, la - 65):
    the program runs it with the quotient precision kN = dmax + 1 and the divisor in a buffer of lbp = la - 64 coefficients (zeros above its top
    coefficient, so the polynomial is unchanged), the reversed divisor in a buffer of min(lbp, kN) and the quotient truncated to dq + 1 coefficients in
    a buffer of kN (zeros above); the sizes are the same for every dq, so the charge is one number: the three buffer loops (load, store, loop step,
    one select per element, allocation and free) and the Newton division at the padded sizes"""
    dmax = min(kmax, la - 65)
    kN = dmax + 1; lbp = la - 64
    loops = sum(dupv(n, 0)[0].ops + n + 105 for n in (lbp, min(lbp, kN), kN))
    return loops + (powcost(PM2) + INV_CTL + 8 * kN + 8 * lbp + series_inverse_cost(min(lbp, kN), kN)
                    + (prod_cost(kN, kN, 2 * kN - 1, 0, kN) + prod_cost(kN, lbp, la, 0, lbp - 1) if MIDPROD & 4 else prod_cost(kN, kN, 2 * kN - 1) + prod_cost(kN, lbp, la)) + 8 * la + 400)


@functools.lru_cache(maxsize=None)
def worst_div(la, kmax):
    """the charge of one re-centering division of a polynomial of la coefficients by one of la - dq, for every 1 <= dq <= kmax: in the schoolbook
    range (quotient or divisor of at most 64 coefficients) every dq is evaluated (at most 127 values); in the Newton range the division runs padded
    (padded_division), one charge for every dq; the result is the larger of the two"""
    hi = min(kmax, la - 1); best = 0
    for d in set(range(1, min(hi, 63) + 1)) | set(range(max(1, la - 64), hi + 1)):
        best = max(best, naive_general(la, la - d))
    if hi >= 64 and la - 65 >= 64:
        best = max(best, padded_division(la, kmax))
    return best


DIV_WALK = True      # WC_MEM only: add the allocation walk of the arrays of the padded Newton division (div_walk) to the live set of the node


def product_array(W, outlen, ws=0, out=None):
    """poly_mul with the product left in its transform array: the array `out` of the plan (3 * 2^a >= need points) is allocated, the first operand is transformed row by row in place in the
    row of `out` it belongs to, the second one into the single row scratch (n slots, allocated for the product and freed at its end), the pointwise product is formed in place in the row, the
    inverse transform runs in place and the scaling by 1/N is applied in place to the wanted entries; the caller reads the product from `out` and frees it.  need = outlen, or for the window of
    prod_cost (ws > 0, the middle product: the coefficients ws .. ws + out - 1 of a product of outlen coefficients) max(ws + out, outlen - ws), as in prod_cost.  Returns the slot count of `out`."""
    if out is None: out = outlen - ws
    Pl, _ = plan3_for_len(max(outlen if ws == 0 else max(ws + out, outlen - ws), 2))
    assert Pl.a <= 32                                           # transform sizes 3 * 2^a exist in F_p for a <= 32
    out = W.new_fp(Pl.N)
    row = W.new_fp(Pl.n); W.free(row)  # pool:H1
    return out


def div_walk(la, kmax):
    """the allocation walk of the padded Newton division (6.3 (b)) of a dividend of la coefficients, in the order of the program (proof 4.4): the arrays bp, br, g, the levels of the series
    inverse, ar, qb and the two products; the arrays of the caller (the quotient array q, the remainder array r, the dividend and the divisor) are not in this walk.  Returns the trace (its peak,
    block count and events are used: the operations of the division are charged by padded_division) or None when the division is schoolbook."""
    dmax = min(kmax, la - 65)
    if dmax < 64 or la - 65 < 64: return None
    kN = dmax + 1; lbp = la - 64; lbr = min(lbp, kN)
    W = Tr(0)
    sbp = W.new_fp(lbp)  # pool:H0
    sbr = W.new_fp(lbr)
    sg = W.new_fp(kN)
    t = 1
    while t < kN:
        t2 = min(2 * t, kN); lft = min(lbr, t2); m2 = t2 - t
        se = product_array(W, lft + t - 1, t if MIDPROD & 2 else 0, m2)   # e = f * g_t, of which the coefficients t .. t2 - 1 are used (middle product)
        smid = W.new_fp(m2); W.free(se)                         # mid = e[t..t2), then e is dead
        sh = product_array(W, 2 * m2 - 1)                       # h = g_t * mid
        W.free(sh); W.free(smid)                                # g[t..t2) = -h[0..m2), then h and mid are dead
        t = t2
    W.free(sbr)                                                 # the reversed divisor is dead once the inverse is complete
    sar = W.new_fp(kN)  # pool:H1
    sqp = product_array(W, 2 * kN - 1)                          # qp = ar * g
    sqb = W.new_fp(kN)                                          # the quotient buffer, read from qp
    W.free(sqp); W.free(sar); W.free(sg)
    spp = product_array(W, la)                                  # pp = qb * bp, only the low la positions
    W.free(spp); W.free(sqb); W.free(sbp)
    assert W.cur == 0 and W.cnt == 0
    return W

def dupv(ln, b):
    T = Tr(b); s = T.new_fp(ln if ln else 1)
    T.ld(ln); T.st(ln); T.loopc(ln)
    return T, s


def trim(it): return 11 * it           # trimlen: CTL(9 it) + LD(it)


def divrem_naive(lx, ly, term_zero=0):
    """cost of poly_divrem_naive for consecutive lengths (lx = ly + 1); returns (ops, lq, lr, iterations of the final trim)"""
    c = 3
    la, lb = lx, ly
    assert la == lb + 1
    if lb >= 2:
        c += powcost(PM2) + INV_CTL + 3 + 1
        c += 2 * 3 + 2 * 2 + 6
        c += (2 * (lb - 1) + 2 * max(lb - 2, 0))
        c += 4 * (lb - 1) + 2 * (lb - 1) + 3 * (lb - 1) + 2 + 4 + 2 * (lb - 1)
        it = 1 + term_zero * (lb - 1)
        c += trim(it)
        return c, 2, lb - 1 - term_zero * (lb - 1), it
    # general path, lb == 1 (la == 2)
    c += 2 * la + 2 * la + 3 * la + 2
    c += powcost(PM2) + INV_CTL
    c += (la - lb + 1) * (1 + 2 + 2 + 2 + 7) + (la - lb + 1) * 0
    c += trim(1)
    return c, la - lb + 1, 0, 1


def mat_identity(b):
    T = Tr(b); sl = [T.new_fp(1) for _ in range(4)]
    T.st(2)
    return T, [1, 0, 0, 1], sl


def mat_free(T, sl):
    for s in sl:
        if s: T.free(s)


def mul_add_q2(T, le, lf):
    lt = le + 1 if le else 0
    lo = max(lt, lf)
    s = T.new_fp(lo if lo else 1)  # pool:H1
    muls = (le + max(le - 1, 0) + (1 if le > 0 else 0))
    adds = max(le - 1, 0) + (min(lf, le + 1) if le > 0 else 0)
    T.ops += muls + adds
    T.ld(le + lf); T.st(lo); T.loopc(lo); T.ctl(8 + 8 * lo)
    T.ctl(trim(1))
    return lo, s


def mat_mulQ(T, lens, sl):
    l0, s0 = mul_add_q2(T, lens[0], lens[1])
    l2, s2 = mul_add_q2(T, lens[2], lens[3])
    T.free(sl[1]); T.free(sl[3])
    return [l0, lens[0], l2, lens[2]], [s0, sl[0], s2, sl[2]]


def poly_mul_naive_cost(la, lb):
    return la * lb * 11 + (la * lb - (la + lb - 1)) + (la + lb - 1) * 11 + 2


def mat_mul(A, B, b):
    """A, B = (lens, slots); returns (Tr, lens, slots)"""
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
        return T, outl, outs
    Pl, c = plan3_for_len(Lmax); T.ctl(c)
    N = Pl.N
    tH0 = T.new_fp(Pl.n)
    tH1 = T.new_fp(Pl.n)
    tS = T.new_fp(Pl.n)
    ob = [T.new_fp(N) for _ in range(4)]
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
    cc, eps = conv_bilin_cost(Pl, 4, Ls, groups); T.ctl(cc)
    T.free(tH0); T.free(tH1); T.free(tS)
    T.ctl(plan_invN_ops(Pl))
    for k in range(4):
        l = Ls[k]
        o = T.new_fp(l if l else 1); T.ctl(3)  # pool:H0
        if eps[k]:
            T.ops += l; T.ld(l); T.st(l); T.loopc(l)
        T.free(ob[k])
        outs[k] = o
        if l: T.ctl(trim(1))
        outl[k] = l
    return T, outl, outs


def apply_inv(Rl, Rs, h, la, lb, consume, b):
    """returns (Tr, lc, sc, ld, sd)"""
    T = Tr(b)
    nres = la
    Pl, c = plan3_for_len(nres); T.ctl(c)
    N = Pl.N
    tH = T.new_fp(Pl.n)
    tS = T.new_fp(Pl.n)  # pool:H1
    sc_ = T.new_fp(N)  # pool:H
    sd_ = T.new_fp(N)  # pool:H1
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
    cc, eps = conv_bilin_cost(Pl, 2, [nres, nres], groups); T.ctl(cc)
    T.free(tH); T.free(tS)
    if consume:
        mat_free(T, Rs)
    T.ctl(plan_invN_ops(Pl))
    for k in range(2):
        T.ctl(3)
        if not eps[k]:
            T.st(nres); T.loopc(nres); continue
        if eps[k] < 0: T.ops += 1
        T.ops += nres; T.ld(nres); T.st(nres); T.loopc(nres)
    lc = la - h; ld = lc - 1
    T.ctl(trim(1 + (nres - lc)) + trim(1 + (nres - ld)))
    return T, lc, sc_, ld, sd_


HGCD_CACHE = {}


def _relink(x, base, ext):
    """the arrays in the result of a recorded call, named in the ids of the caller (ids < 0 are the arrays given to the call)"""
    if isinstance(x, Slot): return Slot(int(x), ext[-x.id - 1] if x.id < 0 else base + x.id)
    if isinstance(x, list): return [_relink(y, base, ext) for y in x]
    if isinstance(x, tuple): return tuple(_relink(y, base, ext) for y in x)
    return x


def hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b):
    """hgcd memoised by shape: the body _hgcd runs once for each shape and records its events with ids relative to the call; every use links them to the arrays of the caller.
    returns (Tr, out) ; out = (lc, sc, ld, sd, Rl, Rs, h)"""
    key = (la, int(sa), lb, int(sb), k, want_mat, own, wc, wd, b, PAR[0])
    ent = HGCD_CACHE.get(key)
    if ent is None:
        ctx = Ctx(); CTX_STACK.append(ctx); PAR[0] ^= 1
        try:
            T, out = _hgcd(la, Slot(int(sa), -1) if sa else 0, lb, Slot(int(sb), -2) if sb else 0, k, want_mat, own, wc, wd, b)
        finally:
            CTX_STACK.pop(); PAR[0] ^= 1
        ent = (T, out, Rec(T.ev, ctx.n)); HGCD_CACHE[key] = ent
    T, out, rec = ent
    ctx = CTX_STACK[-1]; base = ctx.n; ctx.n += rec.nloc
    ext = (sa.id if sa else None, sb.id if sb else None)
    Tc = Tr(T.base); Tc.ops, Tc.cur, Tc.peak, Tc.cnt, Tc.pcnt = T.ops, T.cur, T.peak, T.cnt, T.pcnt
    Tc.ev = [('C', rec, base, ext)]
    return Tc, _relink(out, base, ext)


hgcd.cache_clear = HGCD_CACHE.clear


def _hgcd(la, sa, lb, sb, k, want_mat, own, wc, wd, b):
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
    t1, o1 = hgcd(las, 0, lbs, 0, k1, 1, 0, False, False, T.here())
    T.add(t1)
    R1l, R1s, h1 = o1[4], o1[5], o1[6]
    assert h1 >= 1, 'non-generic shape'
    t2, lcc, scc, ldd, sdd = apply_inv(R1l, R1s, h1, la, lb, not want_mat, T.here())
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
    dqm = max(dq, k2) if WC_MEM else dq
    sq = T.new_fp(dqm + 1)  # pool:H1
    srm = T.new_fp(lcc)  # pool:H1
    if WC_MEM and DIV_WALK: T.bump_walk(div_walk(lcc, dqm))
    T.ctl(3)                                                  # divrem_any
    dc, lq, lrem, _ = divrem_naive(lcc, ldd)
    T.ctl(dc)
    if WORST_D: T.ops += worst_div(lcc, k2)                   # recurrence of 6.3: plus one full division of this node at its worst quotient degree
    T.free(scc)
    k3 = k2 - dq
    t3, o3 = hgcd(ldd, sdd, lrem, srm, k3, want_mat, 3, wc, wd, T.here())
    T.add(t3)
    h = h1 + dq + o3[6]
    if want_mat:
        R1l2, R1s2 = mat_mulQ(T, R1l, R1s)
        tm, Ml, Ms = mat_mul((R1l2, R1s2), (o3[4], o3[5]), T.here()); T.add(tm)
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
        sq = T.new_fp(dq + 1)
        sr = T.new_fp(lx)
        dc, lq, lr, _ = divrem_naive(lx, ly)
        T.ctl(dc)
        if WORST_D: T.ops += max(0, naive_general(lx, ly) - dc)   # recurrence of 6.3: a step of the base case charged on the general path (a step of quotient degree d is at most d steps of degree 1)
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


def gcd_cost(m, dG, b, sx, sy):
    """poly_gcd_own(g (m+1 coefficients), R-1 (m coefficients)), normal Euclid, gcd degree dG.  sx, sy: the arrays of g (m+1 slots) and of F (m slots) of the caller.
    Returns (Tr, (lg, sg))."""
    T = Tr(b)
    lx, ly = m + 1, m
    T.ctl(3); T.ctl(3)
    while ly > 0:
        T.ctl(2)
        n = lx - 1
        T.ctl(4)
        if n <= 2 * 96:
            sq = T.new_fp(lx - ly + 1); sr = T.new_fp(lx)
            last = (ly == dG + 1)
            dc, lq, lr, _ = divrem_naive(lx, ly, term_zero=1 if (last and dG >= 1) else 0)
            if last and dG == 0:
                lr = 0
            T.ctl(dc)
            T.free(sx); sx = sy; lx = ly; sy = sr; ly = lr
            T.free(sq); T.ctl(5)
            continue
        k = (n + 1) // 2
        t, o = hgcd(lx, sx, ly, sy, k, False, 3, True, True, T.here())
        T.add(t)
        lc, sc, ld, sd = o[0], o[1], o[2], o[3]
        T.ctl(2)
        dqm = (lc if WC_MEM else lc - ld)
        sq = T.new_fp(dqm + 1)
        sr = T.new_fp(lc)
        if WC_MEM and DIV_WALK: T.bump_walk(div_walk(lc, dqm))
        T.ctl(3)
        dc, lq, lr, _ = divrem_naive(lc, ld)
        T.ctl(dc)
        if WORST_D: T.ops += worst_div(lc, lc - 1)            # recurrence of 6.3: the division of the outer loop at its worst quotient degree
        T.free(sc); T.free(sq)
        sx = sd; lx = ld; sy = sr; ly = lr; T.ctl(5)
    T.free(sy)
    T.ctl(2)
    if WORST_D: T.ops += SMALL_EUCLID                         # recurrence of 6.3: the closing loop (n <= 192) with arbitrary quotients
    T.ops += powcost(PM2); T.ctl(INV_CTL); T.ld(1)
    T.ops += lx - 1
    T.ld(lx); T.st(lx); T.loopc(lx)
    return T, (lx, sx)


# ---------------------------------------------------------------- the allocator of proof 4.2 on the walk: two-ended pool for the big blocks, slab classes for the others
def _big_events(ev, T, memo):
    """the events of the two-ended pool (blocks of more than T bytes, header included) in ev, sizes in bytes; None if there is none"""
    out = []
    for e in ev:
        t = e[0]
        if t == 'A':
            if blk(e[2]) > T: out.append(('A', e[1], blk(e[2]), e[3]))
        elif t == 'F':
            if blk(e[2]) > T: out.append(('F', e[1]))
        elif t == 'T':
            sz = tuple(blk(x) for x in e[1] if blk(x) > T)
            if sz: out.append(('T', sz, e[2]))
        elif t == 'R':
            sub = _big_events(e[2], T, memo)
            if sub: out.append(('R', sub))
        else:
            if id(e[1]) not in memo: memo[id(e[1])] = _big_events(e[1].ev, T, memo)
            if memo[id(e[1])]: out.append(('C', memo[id(e[1])], e[2], e[3]))
    return out or None


class FirstFit:
    """one list of the pool: its blocks [size, id] (id None = free) in address order counted from the list's own end of the pool, no two free blocks adjacent, the unused middle of the
    pool beyond the last block.  An allocation takes the free block nearest its own end with at least `need` bytes, else the unused middle; it takes the side of the block nearest its own
    end, and the rest stays a free block if it is at least 128 bytes (else it is part of the allocated block).  A free merges the block with a free neighbour on either side, and with the
    unused middle.  end = the extent of the list (the far side of its outermost block)."""
    def __init__(self): self.L = []; self.end = 0; self.scans = 0; self.nblk = 0

    def alloc(self, i, need):
        L = self.L
        for k in range(len(L)):
            b = L[k]
            if b[1] is None and b[0] >= need:
                rem = b[0] - need; b[1] = i
                if rem >= 128:
                    b[0] = need; L.insert(k + 1, [rem, None])
                self.scans += k + 1
                return
        self.scans += len(L) + 1
        L.append([need, i]); self.end += need
        self.nblk = max(self.nblk, len(L))

    def free(self, i):
        L = self.L
        k = next(k for k in range(len(L)) if L[k][1] == i and L[k][1] is not None)
        b = L[k]; b[1] = None
        if k + 1 < len(L) and L[k + 1][1] is None:
            b[0] += L[k + 1][0]; del L[k + 1]
        if k > 0 and L[k - 1][1] is None:
            L[k - 1][0] += b[0]; del L[k]; k -= 1; b = L[k]
        if k == len(L) - 1:
            self.end -= b[0]; del L[k]


class TwoEnd:
    """the pool of proof 4.2: one region, list 0 grows from the bottom, list 1 (the statements marked `# pool:H`) from the top, the unused middle between them.  An allocation uses the
    list of its statement only; a free goes back to the list of its block.  high = the largest sum of the two ends; the pool has high + 128 bytes, so the middle is never shorter than 128 bytes."""
    def __init__(self): self.P = (FirstFit(), FirstFit()); self.where = {}; self.high = 0

    def alloc(self, i, need, c):
        self.where[i] = c; self.P[c].alloc(i, need)
        self.high = max(self.high, self.P[0].end + self.P[1].end)

    def free(self, i): self.P[self.where.pop(i)].free(i)

    def snap(self): return tuple(tuple(tuple(b) for b in Q.L) for Q in self.P)


def _ff_run(P, ev, base, ext):
    for e in ev:
        t = e[0]
        if t == 'A': P.alloc(ext[-e[1] - 1] if e[1] < 0 else base + e[1], e[2], e[3])
        elif t == 'F': P.free(ext[-e[1] - 1] if e[1] < 0 else base + e[1])
        elif t == 'T':
            for k, s in enumerate(e[1]): P.alloc(('t', k), s, e[2])
            for k in reversed(range(len(e[1]))): P.free(('t', k))
        elif t == 'R':
            before = P.snap()
            _ff_run(P, e[1], base, ext)
            assert P.snap() == before, 'a repeated group does not restore the pool'
        else:
            _ff_run(P, e[1], base + e[2], tuple(None if x is None else (ext[-x - 1] if x < 0 else base + x) for x in e[3]))


def slab_class(need): return max(QMIN, (need - 1).bit_length())            # the slot of a block of `need` bytes is 2^class bytes


def _slab_walk(ev, T, memo):
    """for each slab class (blocks of at most T bytes): (net, peak) number of live blocks of the events, relative to the entry"""
    cur = collections.defaultdict(int); pk = collections.defaultdict(int)
    for e in ev:
        t = e[0]
        if t == 'A':
            if blk(e[2]) <= T:
                c = slab_class(blk(e[2])); cur[c] += 1; pk[c] = max(pk[c], cur[c])
        elif t == 'F':
            if blk(e[2]) <= T: cur[slab_class(blk(e[2]))] -= 1
        elif t == 'T':
            for c, n in collections.Counter(slab_class(blk(x)) for x in e[1] if blk(x) <= T).items(): pk[c] = max(pk[c], cur[c] + n)
        else:
            if t == 'R': net, pe = _slab_walk(e[2], T, memo)
            else:
                if id(e[1]) not in memo: memo[id(e[1])] = _slab_walk(e[1].ev, T, memo)
                net, pe = memo[id(e[1])]
            for c in set(net) | set(pe):
                pk[c] = max(pk[c], cur[c] + pe.get(c, 0)); cur[c] += net.get(c, 0)
    return dict(cur), dict(pk)


def _walk_sum(ev, memo):
    """(net bytes, peak bytes, net blocks, peak blocks) of the events, relative to the entry: the live-set walk, recomputed from the events"""
    cur = pk = cnt = pc = 0
    for e in ev:
        t = e[0]
        if t == 'A':
            cur += blk(e[2]); cnt += 1; pk = max(pk, cur); pc = max(pc, cnt)
        elif t == 'F':
            cur -= blk(e[2]); cnt -= 1
        elif t == 'T':
            pk = max(pk, cur + sum(blk(x) for x in e[1])); pc = max(pc, cnt + len(e[1]))
        else:
            if t == 'R': r = _walk_sum(e[2], memo)
            else:
                if id(e[1]) not in memo: memo[id(e[1])] = _walk_sum(e[1].ev, memo)
                r = memo[id(e[1])]
            pk = max(pk, cur + r[1]); pc = max(pc, cnt + r[3]); cur += r[0]; cnt += r[2]
    return cur, pk, cnt, pc


QE_BYTES = 16 * 1024 + 512              # stage E and the later stages: at most 16 live arrays of at most 17 elements (a slot of 1,024 bytes each), taken from the slab classes; and the 36 words of the allocator (35 free-list heads, the end of the slab area)


def pool_account(stage_ev, big_exp):
    """the arena of one trial for the allocator of proof 4.2: stage_ev = [(name, events)] in the order of the program (init, A, B, C, D).  Blocks of more than 2^big_exp bytes come from the
    two-ended pool (TwoEnd, simulated address by address on the events), the others from the slab classes (a slot of 2^class bytes; a class takes a new slot from the end of the slab area when
    its free list is empty, so that the area is the sum over the classes of the peak number of live blocks times the slot).  The pool has `high + 128` bytes (high = the largest sum of the two ends; the unused middle
    is then always at least 128 bytes)."""
    T = 1 << big_exp
    P = TwoEnd(); bm = {}; sm = {}; wm = {}
    cur = collections.defaultdict(int); pk = collections.defaultdict(int); per = {}
    wcur = wpk = wcnt = wpc = 0
    for name, ev in stage_ev:
        f = _big_events(ev, T, bm) or []
        _ff_run(P, f, 0, ())
        per[name] = P.high
        net, pe = _slab_walk(ev, T, sm)
        for c in set(net) | set(pe):
            pk[c] = max(pk[c], cur[c] + pe.get(c, 0)); cur[c] += net.get(c, 0)
        if name == 'init': post = (P.snap(), {c: n for c, n in cur.items() if n})
    assert P.snap() == post[0] and {c: n for c, n in cur.items() if n} == post[1], 'a trial does not return the allocator to its state after init (the second trial would differ)'
    slab = sum(pk[c] << c for c in pk)
    arena = (P.high + 128 + slab + QE_BYTES + 63) & ~63
    return dict(T=T, big_exp=big_exp, big_high=P.high, big_stage=per, slab=slab, slab_peaks={c: pk[c] for c in sorted(pk)}, arena=arena, scans=P.P[0].scans + P.P[1].scans, big_blocks=P.P[0].nblk + P.P[1].nblk,
                big_final=P.snap())


def stage_c_trace(stage_ev, big_exp):
    """the allocation / free trace of stage C on the two-ended pool (proof 4.3V): the pool after init, A and B, then every event of stage C with the live bytes of the trial and the extents of the two ends"""
    T = 1 << big_exp; P = TwoEnd(); bm = {}
    live = 0
    for name, ev in stage_ev:
        if name == 'C': break
        _ff_run(P, _big_events(ev, T, bm) or [], 0, ())
        live += _walk_sum(ev, {})[0]
    print('stage C on the two-ended pool (blocks of more than 2^%d bytes): after init, A, B: low end %s, high end %s, live %s' % (big_exp, format(P.P[0].end, ','), format(P.P[1].end, ','), format(live, ',')))
    names = {}
    for e in stage_ev[3][1]:
        if e[0] == 'A':
            names[e[1]] = len(names) + 1; live += blk(e[2])
            big = blk(e[2]) > T
            if big: _ff_run(P, _big_events([e], T, bm), 0, ())
            print('  alloc #%-2d %14s slots %16s bytes %s | live %16s | pool low %16s high %16s sum %16s' % (names[e[1]], format(e[2], ','), format(blk(e[2]), ','), ('pool ' + ('H' if e[3] else 'L')) if big else 'slab  ', format(live, ','), format(P.P[0].end, ','), format(P.P[1].end, ','), format(P.P[0].end + P.P[1].end, ',')))
        elif e[0] == 'F':
            live -= blk(e[2])
            big = blk(e[2]) > T
            if big: _ff_run(P, _big_events([e], T, bm), 0, ())
            print('  free  #%-2d %14s slots %16s bytes %s | live %16s | pool low %16s high %16s sum %16s' % (names[e[1]], format(e[2], ','), format(blk(e[2]), ','), 'pool  ' if big else 'slab  ', format(live, ','), format(P.P[0].end, ','), format(P.P[1].end, ','), format(P.P[0].end + P.P[1].end, ',')))
        else:
            assert False, e[0]
    print('  after stage C: low end %s, high end %s, largest sum of the two ends so far %s' % (format(P.P[0].end, ','), format(P.P[1].end, ','), format(P.high, ',')))


def walk_check(stage_ev):
    """the live-set walk recomputed from the events: (bytes in use, peak bytes, blocks, peak blocks) of each stage"""
    memo = {}
    return {name: _walk_sum(ev, memo) for name, ev in stage_ev}


IMAGE_EXTRA = 399216 + 32 + 4851196        # text + data + static bss besides the arena (proof section 7)
STACK = 65536


def ceil3(x): return math.ceil(x * 1000) / 1000


def twiddle_slots(m):
    a = 2
    while 3 * (1 << a) < 2 * m - 1: a += 1
    return (1 << min(a, 32)) // 2                             # init_stage: the table of nmax/2 elements, nmax = 2^min(a, 32)


def stage_AB(m):
    """the arrays of the stages before C: the twiddle table (init), g (stage A), the array of the inverse transform of stage B (H elements, the smallest 2^a or 3 * 2^a that is at least m + 1; freed
    after the transform) and F"""
    H = min(v for a in range(2, 64) for v in (1 << a, 3 << a) if v >= m + 1)
    I = Tr(0); I.new_fp(twiddle_slots(m))
    A = Tr(1); sg = A.new_fp(vd_gslots(m))
    B = Tr(2); sb = B.new_fp(H); B.free(sb)  # pool:H
    return I, A, B, sg


def main():
    global WORST_D, WC_MEM, DIV_WALK
    m = (5 ** 14 - 1) // 2
    def stages():
        hgcd.cache_clear()
        I, A, B, sg = stage_AB(m)
        C, cinfo = powx_vd(m, 3, PM1H, sg); C.ctl(STAGE_BK)              # stage C in the value domain (4.3V); R is left in cinfo['sR2'] (n1 slots), g in sg
        D = Tr(3); D.ctl(STAGE_BK); D.ops += 1; D.ctl(11)
        t, (lg, sgg) = gcd_cost(m, 0, 3, sg, cinfo['sR2'])
        D.add(t); D.ctl(2); D.free(sgg)
        return C, cinfo, D, (I, A, B)
    WORST_D = False; WC_MEM = False
    Cn, cinfo, Dn, _ = stages()                                # the normal local charge of the half-gcd tree, no division beyond the quotient of two coefficients
    WORST_D = True; WC_MEM = True; DIV_WALK = False
    Cw, cinfo, Dw, _ = stages()                                # the recurrence of 6.3 with the quotient and remainder arrays of every division at their largest length, without the arrays of the Newton division
    DIV_WALK = True
    C, cinfo, D, (I, A, B) = stages()                          # the recurrence of 6.3: normal local charge + one full division at every node, summed over the tree; every allocation walked
    vd = cinfo['vd']
    print('m =', format(m, ','), '| h =', format(vd['h'], ','), 'K =', vd['K'], 'n1 =', format(vd['n1'], ','), '| Lx =', vd['Lx'], 'Le =', vd['Le'], 'Lq =', vd['Lq'], '| v =', format(vd['v'], ','), 'ell =', format(vd['ell'], ','), 'Kq =', vd['Kq'],
          '| squaring steps', vd['steps'], 'of which with x:', vd['nset'])
    print('one extension (O1 -> O2 or O2 -> O1, inner transforms included) =', format(vd['ext'], ','), '| one squaring step =', format(vd['step0'], ','), '(with the multiplication by x:', format(vd['step1'], ',') + ')',
          '| one interpolation back to coefficients =', format(vd['interp'], ','))
    prev = 0
    for name, ops in VD_STEPS:
        print('  stage C %-110s %22s' % (name, format(ops - prev, ','))); prev = ops
    print('  stage C %-110s %22s' % ('stage bookkeeping (STAGE_BK)', format(C.ops - prev, ',')))
    print('S_C =', format(C.ops, ','))
    print('S_D normal local charges of the tree =', format(Dn.ops, ','))
    print('S_D with one full division at every node (and the outer loop, and the closing loop) =', format(D.ops, ','))
    print('S_D =', format(D.ops, ','))
    tws = twiddle_slots(m); twb = blk(tws)
    A_, B_, C_ = A.cur, B.cur, C.cur                           # what each stage leaves live: g (n1 slots) after A, nothing after B, R (n1 slots) after C
    pA = twb + A.peak; pB = twb + A_ + B.peak
    pC = twb + A_ + B_ + C.peak; pD = twb + A_ + B_ + C_ + D.peak; pD0 = twb + A_ + B_ + C_ + Dw.peak
    peaks = dict(A=pA, B=pB, C=pC, D=pD)
    for x in 'ABCD': print('peak of the live set, stage %s = %s bytes' % (x, format(peaks[x], ',')))
    print('peak of the live set, stage D, without the arrays of the Newton divisions = %s bytes (with them: %s)' % (format(pD0, ','), format(pD, ',')))
    # the allocator of section 4.2 on the sequence of allocations and frees of one trial (the second trial repeats it from the same state)
    stage_ev = [('init', I.ev), ('A', A.ev), ('B', B.ev), ('C', C.ev), ('D', D.ev)]
    walk = walk_check(stage_ev)                                # the events reproduce the walk: bytes in use, peak and live blocks of every stage
    for x, T_ in zip('ABCD', (A, B, C, D)): assert walk[x] == (T_.cur, T_.peak, T_.cnt, T_.pcnt), x
    pool = pool_account(stage_ev, BIG_EXP)
    stage_c_trace(stage_ev, BIG_EXP)
    print('two-ended pool: blocks of more than 2^%d bytes; largest sum of the two ends after each stage (bytes): %s; at most %d blocks; %s blocks examined in all'
          % (BIG_EXP, ', '.join('%s %s' % (k, format(v, ',')) for k, v in pool['big_stage'].items()), pool['big_blocks'], format(pool['scans'], ',')))
    print('slab classes (class: peak number of live blocks): %s; slab area = %s bytes' % (', '.join('%d: %d' % kv for kv in pool['slab_peaks'].items()), format(pool['slab'], ',')))
    arena = pool['arena']                                      # pool high-water + 128 + slab area + QE_BYTES, rounded up to 64
    mem = arena + IMAGE_EXTRA + STACK
    print('arena = %s bytes (two-ended pool %s + 128, slab classes %s, stages E and later %s), memory = %s bytes, log2 = %.3f'
          % (format(arena, ','), format(pool['big_high'], ','), format(pool['slab'], ','), format(QE_BYTES, ','), format(mem, ','), ceil3(math.log2(mem))))
    assert C.ops == 446444428530905 and D.ops == 1076929687405216
    assert peaks == dict(A=132070244480, B=235149459648, C=426300939456, D=602314908032) and arena == 602365231488 and mem == 602370547468


if __name__ == '__main__':
    main()
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

