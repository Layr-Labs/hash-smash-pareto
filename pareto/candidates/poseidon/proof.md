# Orchard Poseidon, r = 18: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, half-gcd on aligned budgets with the inversion-free node on three rows, one centre, the scaled straight-line program in stage B; stage B on column passes (this entry)

## 1. Claim

Target: `poseidon-orchard-r18-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, eighteen partial rounds 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 and 21, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

**This entry's change (stage B on column passes; Appendix B2).** This package is `ab6b989a` (mpjunior92, time + memory penalty 105.08552) taken from its evaluated commit and edited in place, so the line numbers before the appendices are preserved. One change, in row B only: the `4625930` inverse transforms of size `6,442,450,944` and the four transforms of length `S = 12,582,912` per position of the geometric solve are run as the column passes of section 4.2 (the kernels `ob2` to `ob128` and `ob3` of stage C, with their call, kernel and loop charges), the inverse transforms across the cosets (cnt = `4625930`) and the solve in groups of `1,024` positions; the point loop stores in natural order (no bit-reversed index). The interpolation itself (section 3) is unchanged. Row B `40,390,833,724,747,331,365` (was `86,684,755,546,378,974,541`), `N_max = 6,979,310,775,483,852,735,602` (was `7,025,604,697,305,484,378,778`), `time_log2 = 63.34926` (was `63.35880`), `memory_log2_bytes = 61.72672` (the solve buffers, 551,366,623,232 bytes, added as term (f) of section 7), time + memory penalty `105.07598` (was `105.08552`). Every other row, the premises, the success bound and the experiments are those of `ab6b989a`. This entry is an algorithm (sections 2-4) with a worst-case operation count (sections 6-7) and a success probability derived from the premises `H-ONE` (section 9.1) and `H-NORMAL` (section 9.5), statements about the usable roots of the fixed digest polynomial and its remainder sequences; section 9.2 derives the success probability from them with explicit constants.

* The algorithm: draw a centre `c` uniformly from `F_p` from fresh random words, build the odd part `g_c` of the line polynomial by evaluation and 4625930 inverse transforms (one per coset, section 3), compute `G = gcd(g_c, S^((p-1)/2) - 1)` by a power-mod in the value domain (section 4.6, the method of bradcush 1aa56884) and a half-gcd in the lean form of 1aa56884 (4.4.1) with the scaled division and the product forms of weijiekoh a78f526e (4.4.2), its budgets below `2^54` split at powers of two and every matrix-only call of budget `2^j - 1` (`7 <= j <= 31`) run on bradcush's inversion-free half-gcd on three rows (4bcabff8; 4.4.3), and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` in at most `Z = 64` rounds, take its square root, map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39209`: a lower bound for the probability, over the algorithm's fresh random words, that the one centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta + delta_C)^K - K (eps_iso + eps_coin) = q - delta - delta_C - eps_iso - eps_coin` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1: at least `0.3931 p` centres have between 1 and `DMAX = 16` usable roots), `delta = 0.001` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `delta_C < 2^-143.5` the stage-C zero test (proved, 9.2(b)), `eps_iso <= P[Bin(64, w) <= 3] = sum_(j <= 3) C(64, j) w^j (1 - w)^(64 - j) = 2.371e-15 < 2^-48` (each isolation round halves `deg G <= 16` with probability at least `w = 1/2 - 7.869e-40` whatever came before, and four halvings reach degree 1; lemma 9.4), `eps_coin < 2^-122` (4.1.1). The exact value is `0.392099999999997615`. The value of `q` is `0.3934693 - 0.3931 = 0.0003693` below `1 - e^(-1/2) = 0.3934693` (and below the four-moment Bonferroni bound `151/384 = 0.3932292`), the law of the usable roots in section 9.3, which is a theorem for the first two and three S-box layers on the deployed constants (9.3(c)).

* `time_log2 = 63.34926` in target-compression units (`C(18) = 594` primitive operations per unit): the worst-case operation count, derived in section 6 as `T_fixed + K * T_trial` with every trial charged in full (stage D for the normal remainder sequence, which bounds every trial because a trial with any other sequence ends after a prefix of that work, section 6.3; stage E at its cap of `Z` rounds at degree `DMAX`), `N_max = 6,979,310,775,483,852,735,602` operations, `log2(N_max / 594) = 63.3492554455`, rounded up at five decimals. The offline derivation of the constants (section 6.2) is counted exactly, `T_off = 136,785` operations, and charged at its declared cap of 1,000,000 operations; that cap is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 61.72672` (`3,815,855,379,080,802,572` bytes, section 7). This entry adds the stage-B solve buffers, `551,366,623,232` bytes (section 7, term (f)): footprint `3,815,855,930,447,425,804` bytes.
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; `65` words at most (section 4.1.1), and a draw (one word) costs 31 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^24`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* This entry's change against the r = 18 frontier entry `4fd1cd9` (Jbenisek, time + memory penalty 105.08849; the base restored with `yukon reset` and edited in place, so the line numbers before the appendices are preserved and the claim's evidence references stay valid): stage B charges each of its `59,604,654,190,755,840` line evaluations of `F` at the `135 + 12 r = 351` operations of the scaled straight-line program (section 3, Appendix L), not at the full reference permutation `C(18) = 594`. `4fd1cd9` itself notes that a line evaluation (affine start, the remaining rounds, one row of the last MDS) is a strict subset of the work of a reference permutation; this entry charges that subset exactly, the refinement of `mpjunior92`'s accepted r = 3 entry `1ac48175` and r = 20 entry `ac52b89`. The loop work around the evaluations, every other row of the ledger, the arena, the register file, the premises `H-ONE` / `H-NORMAL`, the success bound and the experiments are exactly `4fd1cd9`'s. Row B `86,684,755,546,378,974,541` (was `101,168,686,514,732,643,661`, down by `59,604,654,190,755,840 * (594 - 351) = 14,483,930,968,353,669,120`); `N_max = 7,025,604,697,305,484,378,778` (was `7,040,088,628,273,838,047,898`); `time_log2 = 63.35880` (was `63.36177`); `memory_log2_bytes = 61.72672` unchanged (the 351-operation program's code, about 5.6 KB, is within memory term (a) of section 7 and leaves the footprint unchanged at five decimals); time + memory penalty `105.08552` (was `105.08849`). The scaled program is the `135 + 12 r` straight-line form of the r = 56 entries `3a1b25b6` (newjordan), `9fb982e8` (pierce403) and `69e14209` (Jbenisek); it is rebuilt by our own code from the organizer constants and checked against the reference digest at 200 random points, with its 351-operation listing in Appendix L. The remaining bullets of this section are the development history of the base package `4fd1cd9` (Jbenisek), retained unchanged; "our" in them refers to that base.
* Against our r = 18 entry `e9ec7ef5` (time + memory penalty 105.27734, the same algorithm and package), five changes: (i) stage D splits its budgets below `2^54` at powers of two and runs every matrix-only call of budget `2^j - 1` (`7 <= j <= 31`) on the inversion-free half-gcd on three rows of bradcush's entry `4bcabff8`, ported as in our r = 3 entry `bcf8e01c` and our r = 22 entry `907f3c9e` (4.4.3); (ii) with the apply plans of 0xplemonade's entry `ff21bd28`, each apply of steps (2) and (6) of a half-gcd node runs the cheaper of its block products or single transform and a direct whole-pair or fixed-slot plan on one transform size (4.4.1 item 7); (iii) with the batch-inversion prefix of `ff21bd28`, stage C runs the batch inversion in chunks of `2^16` elements (its auxiliary array `2^16` elements, was `h`) and forms the `omega^e` of the `b = 1` boundary pass from two tables of `2^16` entries (was one table of `h` entries; 4.6); (iv) the layers of the block-form passes and of the column passes are split into passes of at most seven layers by the split of least charge, in place of seven at a time with the remainder in one pass (4.2; the exact pass split of 0xplemonade's entry `d4b13ccd`); (v) in the node of the inversion-free half-gcd (4.4.3), the four chunks of each of `a`, `b` are folded onto the three rows in one loop of 22 operations per position and each matrix-vector map of the node is one two-output pass of 20 operations per point (the fused two-output rows of 0xplemonade's entry `8b1eb62a`, read as text, priced by the direct apply row of `ff21bd28`). Row C `4,201,139,007,696,370,489,010` (was `4,203,019,494,667,203,600,990`), row D `2,737,780,934,045,384,314,781` (was `3,714,648,543,752,492,917,303`); `N_max` `7,040,088,628,273,838,047,898` (was `8,018,836,724,951,779,762,400`), time_log2 `63.36177` (was `63.54957`); the live peak of stage C `3,814,698,222,768,355,136` bytes (was `3,814,698,497,639,970,624`), the arena `3,815,855,379,074,495,104` bytes (was `3,818,637,556,614,930,688`); term (a) `71,008` bytes more code (7(a)); memory `3,815,855,379,080,802,572` bytes, memory_log2 `61.72672` (was `61.72777`). The premises, the success bound and the experiments are unchanged.
* Against our r = 18 entry `05b4c884` (time + memory penalty 105.29044, the same algorithm and package): (i) the register file of the machine is declared as one file of 387 words, 256 field registers of 256 bits plus the 131 integer address registers of an `ob128` call, counted in the memory (7(d), 12,384 bytes; was 256 words, 8,192 bytes), no operation added (ruling fdb6bc0e on our r = 17 entry, the same machine text); (ii) in group 0 of every block-form pass a butterfly whose twiddle is 1 is its addition and subtraction, 2 operations (a straight-line variant of the block body, 3 control operations more per pass), as in the column kernels (4.2); (iii) the block loop of a group runs four blocks per pass of a straight-line body (a group of one block has no block loop): 3 control operations per block, was 5 (4.2); (iv) the offline derivation of 6.2 is counted exactly, `T_off = 136,785`, and charged at its declared cap 1,000,000 (was the bound 1,000,000), its working set memory term 7(e) (ruling 4896c4ea on our r = 5 entry, the same 6.2 text); (v) `H-NORMAL` at `delta = 0.001` in place of `0.003` (9.2, 9.5), the form of our accepted r = 9 entry `5b96dbb5`: the success bound `q - delta - delta_C - eps_coin - eps_iso = 0.392099999999997615`, claimed `0.39209` (was `0.39009`), at or above 0.39 for every `delta <= 0.0030999`; the H-ONE good-centre tests `euclid-gcdpos-n2-t256-a`, `-b` and `euclid-gcdpos-n3-t24` (a pair returned ONLY when `deg gcd(g_c, R_c - 1) >= 1`) and the normality tests `euclid-normal-n2-t256-l2-c` to `-l2-f`, `euclid-normal-n3-t24` and `euclid-normal-n4-t2` replace the one-centre tests (3,072 sequences at `m = 12`, the set of `5b96dbb5`), with the program of `5b96dbb5` (10.5.1, 10.5.2); no interval is computed from them and no independence of the trials is assumed. Row C `4,203,019,494,667,203,600,990` (was `4,204,318,906,512,954,811,023`), row D `3,714,648,543,752,492,917,303` (was `3,786,477,931,652,787,906,833`), row B unchanged; `N_max = 8,018,836,724,951,779,762,400` (was `8,091,965,524,697,825,961,963`), `time_log2 = 63.54957` (was `63.56267`); arena `3,818,637,556,614,930,688` bytes (was `3,818,637,556,612,800,768`), code bound 7(a) +907,520 bytes; memory `3,818,637,556,621,167,148` bytes, `memory_log2_bytes = 61.72777` (unchanged); time + memory penalty 105.27734 (was 105.29044).
* History, in our r = 18 entry `05b4c884` (time + memory penalty 105.29044) against our entry `abf2152d` (105.39623, the same algorithm and package): the register file of that version was 256 words of 256 bits (was 64), counted in the memory (7(d), 8,192 bytes in that version; this entry: 387 words, 12,384 bytes, item (i) above), as the live entry cryptogakusei `1533f8f0` declares a file of 304 registers of 256 bits: the column passes of stage C and of the outer transforms of stage D take up to seven layers (`ob64`, `ob128`) and the block-form passes of the products up to seven layers (blocks of 128 points with their 127 twiddles in registers); 4.2; every column pass runs its position loop eight positions per pass, with the loop control `F(cnt) = 1 + 3 floor(cnt / 8) + 2 + 3 (cnt mod 8) + 2` per call in place of 3 per position (our r = 17 entry `8346be35`; 4.2, 4.6); the output of mul_add_q2 comes from the low end of the pool (4.2, 7); every operation count of an allocation is the same at either end; memory_log2 is rounded up at five decimals (7). Row C `4,204,318,906,512,954,811,023` (was `4,470,751,463,855,935,421,979`), row D `3,786,477,931,652,787,906,833` (was `4,020,457,812,115,086,721,409`); the pool takes the blocks of more than `2^47` bytes (was `2^46`; 4.2, 7); arena `3,818,637,556,612,800,768` bytes (was `3,869,170,580,510,262,016`), memory_log2 61.72777 (was 61.747). Every other charge, the premises and the experiments are unchanged.
* History, in our r = 18 entry `abf2152d` (time + memory penalty 105.39623) against our entry `8318fb53` (105.43494, the same algorithm and package): two kernel changes. (i) A column-kernel butterfly whose twiddle is 1 is charged 2 operations (its call at offset 0 a straight-line variant, 4.2). (ii) The block-form passes take up to five layers (blocks of 32 points; 32 data words, 31 twiddles and the temporary, the 64 words of the file declared in that version, as `ob32`; 4.2). Row C `4,470,751,463,855,935,421,979` (was `4,545,686,363,768,499,652,452`), row D `4,020,457,812,115,086,721,409` (was `4,179,173,535,136,607,425,997`); arena `3,869,170,580,510,262,016` bytes (was `3,869,170,580,496,409,344`), memory_log2 unchanged (61.747 in that version). Every other charge, the premises and the experiments are unchanged.
* History, in our r = 18 entry `8318fb53` (time + memory penalty 105.43494) against our entry `ad072c87` (105.51493, the same algorithm and package): the loads and stores of the block-form passes of 4.2 are charged one operation each (base plus index, as the column kernels `ob4` to `ob32`): row C `4,545,686,363,768,499,652,452` (was `4,559,341,001,017,025,493,780`), row D `4,179,173,535,136,607,425,997` (was `4,668,670,464,087,253,741,963`); memory unchanged. Every other charge, the premises and the experiments are unchanged.
* History, in our r = 18 entry `ad072c87` (time + memory penalty 105.51493) against the same algorithm with the leaf passes of 4.2 in every product (105.58447): the transform passes of the products of stages C and D (all but the fused pass of each product) run in the block form of our r = 3 entries `ef123c2b` / `253629b9` (per group the `2^k - 1` twiddles held in registers), on the register file of that version (64 words) stated as a restriction in claim.json: row C `4,559,341,001,017,025,493,780` (was `4,576,053,522,015,281,264,039`), row D `4,668,670,464,087,253,741,963` (was `5,112,666,027,465,481,101,935`); arena `3,869,170,580,496,409,344` bytes (was `3,869,170,580,657,464,064`). Every other charge, the premises and the experiments were unchanged.
* Prior entry: this entry is the r = 18 version of our r = 7 algebraic entry 05a41d88 (the same algorithm, ledger method, premise structure and evidence design). The ruling on 05a41d88 (not_evaluable on the experiments lane) is answered here in the same way: the organizer experiments `line-ladder-w6`, `-w8`, `-w10` and `-w12` on the antipodal line pairs of this construction at r = 18 (10.2), the computations of Grok job 136 and their re-run on the deployed constants and the algorithm's line (10.3), and the measurement of the Euclidean sequences on the sibling targets (10.5). Stage C is the value-domain powering of bradcush's entry 1aa56884 (section 4.6), stage D its lean half-gcd (4.4.1), and stage D is charged for the normal remainder sequence under the premise `H-NORMAL` of bradcush (entries e6dcb600, 1aa56884) with gta6rp's allowance and organizer-run tests (9.5); all credited in the dependencies and the note.
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1) and `H-NORMAL` (score-critical for the success probability only, section 9.5). Both are statements about probability. `H-NORMAL` is bradcush's premise (entries e6dcb600 and 1aa56884), stated here with the allowance `delta = 0.001` and supported by organizer-run normality tests, the recipe of gta6rp's entries (3876eb92 at this round count); the test program `experiments/exp_euclid.py` is our own (10.5.1). The costs are the declared cost model of this entry, not heuristics: the charging rules of section 4.2 on the machine stated as a restriction in claim.json (256 field registers of 256 bits plus 131 integer address registers; every load, store and spill counted), as the accepted entries `89b451ff` and `fb176310` state theirs and as our r = 3 entries `ef123c2b` and `253629b9` do, and the base-plus-index addressing of the stage-C column kernels (4.2), stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation. Everything else is proved or counted here: the line construction, the degree of `F`, the odd-part reduction, the collision criterion (sections 2, 3, 5), the success bound (section 9.2), the stage-C zero-test bound (9.2(b)), the isolation lemma (section 9.4), the uniformity of the centre, the cap rules and every operation count (sections 4, 6, 7).
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

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21 (partial), 60, 61, 62, 63 (full) put twenty-four S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^24 = D = 59,604,644,775,390,625`. The leading coefficient is obtained by
propagating leading coefficients through the twenty-four layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used:
`f_D(0) = 0x25c9aa58a3ad0038c573a084c0d6c6fb4fd57348bd1aeed83e5f0777ac1ffc80`
(computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 29,802,322,387,695,312`, `g_c` has degree exactly `m` and
leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives `s = 0` and is not a root of `S^((p-1)/2) - 1`).
`G` divides `S^((p-1)/2) - 1`, which is squarefree, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. At this r no transform of `H >= m + 1` points exists: `p - 1 = 2^32 * 3 * q'` has roots of unity of order `3 * 2^a` for `a <= 32` only, and `m + 1 = 29,802,322,387,695,313 > 3 * 2^32`. Let `B = 3 * 2^31 = 6,442,450,944`, `zeta` a primitive `2B`-th root of unity (`2B = 3 * 2^32` divides `p - 1`) and `omega = zeta^2`, a primitive `B`-th root. Let `kappa = ceil((m + 1) / B) = 4625930`, `v_k = 2^k` and `u_k = v_k^2 = 4^k` for `k < kappa`, and `z = 4^B`; the `kappa` numbers `n_k = u_k^B = z^k` form a geometric progression and are pairwise distinct, because the order of `z` exceeds `kappa` (`z^d != 1` for every divisor `d` of `p - 1` up to `2 * 10^8`, and `kappa < 2 * 10^8`). The evaluation points are `s_{k,i} = v_k zeta^i` for `k < kappa`, `i < B`, so that `S_{k,i} = s_{k,i}^2 = u_k omega^i`, and `g_c(S_{k,i}) = (F(c + s_{k,i}) - F(c - s_{k,i})) / (2 s_{k,i})`. Write `g_c(x) = sum_{t < kappa} x^{tB} h_t(x)` with `deg h_t < B`. For `y = omega^i` we have `y^B = 1`, hence `g_c(u_k y) = w_k(y)` with `w_k(y) = sum_t n_k^t h_t(u_k y)`, a polynomial of degree `< B`. One inverse transform of size `B` of the values `(g_c(S_{k,i}))_i` returns the coefficients `w_k[j] = u_k^j sum_t n_k^t h_t[j]`. After multiplication by `u_k^{-j}`, for every `j < B` the numbers `W_k[j] = sum_t n_k^t h_t[j]` (`k < kappa`) are the values of the polynomial `h^(j)(X) = sum_t h_t[j] X^t` at the nodes `z^k`, and its coefficients `h_t[j] = g_c[j + tB]` are recovered from them by two correlations of length `kappa` (Lagrange interpolation at geometric nodes, the chirp-z form). Let `M(X) = prod_k (X - z^k) = sum_i mu_i X^i`; the q-binomial theorem gives `mu_{kappa-j} = (-1)^j z^{j(j-1)/2} [kappa choose j]_z`, and `M'(z^k) = z^{k(k-1)/2 + k(kappa-1-k)} prod_{j <= k} (z^j - 1) prod_{j <= kappa-1-k} (1 - z^j)`. With `a_k = W_k[j] / M'(z^k)` and `A(i) = sum_k a_k z^{ki}` (`i < kappa`) we have `h_t[j] = sum_{i > t} mu_i A(i - t - 1)`. Since `z^{ki} = z^{C(k+i,2) - C(k,2) - C(i,2)}` with `C(n,2) = n(n-1)/2`, `A(i) z^{C(i,2)}` is the correlation of the sequence `a_k z^{-C(k,2)}` with the chirp `z^{C(n,2)}` (first correlation), and `h_t[j]` is the correlation of `A` with `(mu_1, ..., mu_kappa)` (second correlation). Each correlation is one cyclic convolution of length `S = 12,582,912` (the smallest `2^a` or `3 * 2^a` that is at least `2 kappa - 1`), done with the transform of length `S` (forward, pointwise product, inverse); the transforms of the fixed sequences (the chirp and `mu`) and the constants `mu_i`, `1/M'(z^k)`, `z^{-C(k,2)}` are computed once per trial and shared by the `B` positions `j`. The `2 kappa B = 59,604,654,190,755,840` evaluations of `F` are each charged at the `135 + 12 r = 351` operations of the scaled straight-line program of Appendix L (the `135 + 12 r` form of the r = 56 entries `3a1b25b6`, `9fb982e8`, `69e14209`, as in `mpjunior92`'s r = 3 entry `1ac48175`), not at the full reference permutation `C(18) = 594`: a line evaluation (affine start, the remaining rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation, and the program computes `F(W)` by scaled lanes (each dense layer 2 MUL + 3 ADD per lane after row normalisation, each partial round 12 operations, the hidden pair rotated so its matrix is diagonal at the exit), checked equal to the reference digest times a fixed nonzero constant at 200 random points (Appendix L); the interpolated polynomial is that constant times `g_c`, and the normalisation to monic removes it. The loop work, the inverse transforms and the solve are charged as in Appendix B2 (this entry): the point loop runs in natural order (per point the two additions for the points, the subtraction, the multiplication by `1/(2 s_{k,i})`, the two multiplications of the recurrences of `s_{k,i}` and `1/(2 s_{k,i})`, one store at `i * kappa + k` with its address operation and 3 of loop control: `2 * 351 + 11` with the two evaluations), the `kappa` inverse transforms of size `B` are made together as column passes across the cosets (decimation in frequency, natural order in, transform order out), and the solve is made in groups of `1,024` positions (slots) in a group buffer of `S` rows: gather with the factor `c_k (4^(-j))^k` (`c_k = z^(-C(k,2)) / M'(z^k)`; `W_k[j] = (4^(-j))^k w_k[j]` because `u_k^(-j) = (4^(-j))^k`), first correlation (forward transform of length `S`, product by the chirp spectrum, inverse transform), rows `i < kappa` times `z^(-C(i,2)) / S`, second correlation (forward transform, product by the spectrum of `(mu_1, ..., mu_kappa)`, inverse transform), scatter of `h_t[j]` to `g[j + tB]` with `1/S`; every transform on the column passes of section 4.2 (no pruning, no twiddle-1 saving); the once-per-trial constants and the normalisation are counted there as well.

## 4. The algorithm (at most K centres, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   twiddle table (once)
setup:  the line (line_setup) (once)
for t = 1, 2, ..., K:                                  [the test t <= K is made at the start of every trial; no other exit except success]
  A  c := a uniform element of F_p from one fresh random word (section 4.1.1)
  B  g := monic g_c, by section 3 (59,604,654,190,755,840 evaluations + 4625930 inverse NTTs of size 6,442,450,944 + the geometric solve of the 4625930 cosets (two correlations of length 12,582,912 per position) + the test that the leading coefficient is nonzero + normalisation by the leading coefficient)
  C  R := S^((p-1)/2) mod g           (left-to-right square-and-multiply on the exponent, base S; value domain, section 4.6: from S^v, v = 2^52; 201 squaring steps, 45 of them also multiply by S, pointwise)
  D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4)
  E  if deg G = 0 or deg G > DMAX: the trial ends, next t.   Otherwise isolate a root S of G (section 4.1.2).  If none is isolated within Z rounds: the trial ends, next t.
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (594 operations each) are equal and the pairs differ -> go to H; otherwise the trial ends, next t
H  output: the two pairs (and the digest and the centre) are converted to canonical form and encoded as 64 hexadecimal digits each.
   If t > K was reached the algorithm fails (the failure event, probability bounded in section 9).
```
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. Binary powering therefore performs 253 modular squarings and 45 multiplications by `S`; the 54 bits after the leading one are zero, so the algorithm starts from the monomial `S^v` with `v = 2^52` (a multiple of h below m, 4.6, `VSHIFT = 2`; 52 + 201 = 253), and the loop of stage C has 201 steps, of which 45 also multiply by `S` (pointwise).

Stopping rule. The loop bound `K = 1` is a constant of the algorithm: one centre is tried. A trial is run to its end, or to an ABORT of stage D on an abnormal remainder sequence (6.3) or of stage C on a zero of g on O1 (4.6 step 5), which then resets the allocator and draws the next centre; the claim charges every trial at its maximum (stages E to G at their worst case, section 6), so a trial that fails early is paid for at the full-trial price, never less. Stage E is entered only when `1 <= deg G <= DMAX`, and at most `Z` rounds are made in it. The algorithm has no other loop whose length depends on data: the loops of stages B to D have lengths fixed by `m` and the exponent (sections 4.3, 4.4), the powering has a fixed number of steps, and the half-gcd has a fixed recursion: 49 levels of recursion in `hgcd` (the parameter `k` starts at `floor((n+1)/2) = 14,901,161,193,847,656` and is halved, rounded up, until it is at most 96) and at most 49 repetitions of the outer loop of the Euclid driver (each repetition removes more than half of the degree, from 29,802,322,387,695,312 to at most 192). Hence, with stage D charged for the normal remainder sequence and every other sequence ending its trial after a prefix of that work (section 6.3), the number of executed operations is at most `N_max` for every coin sequence and every target value, the algorithm cannot stop early except by success, by an ABORT of a trial (the next centre is then drawn), or by failure after `K` trials, and nothing in the claim depends on a run being lucky.

#### 4.1.1 Coins

The only randomness of the algorithm is the cost model's random-word primitive (fresh independent algorithmic coins): an independent uniform 256-bit word, each use returning a fresh word, uniform on `0..2^256-1` and independent of everything else, and costing one operation. **Probability space:** every probability of section 9 is over these words. A draw is one fresh word `y`; the draw is `x = y mod p`, computed by at most three steps `if y >= p then y := y - p` (`y < 2^256 < 4p`, so three steps bring `y` below `p`). Write `2^256 = 3p + s0` with `0 < s0 < p`: the residues below `s0` have exactly four preimages below `2^256` and the other `S3 = p - s0 = 4p - 2^256` residues have exactly three, so `P[x = z] = 4/2^256` or `3/2^256` for every residue `z`, every residue has probability at least `3/2^256`, and all but `S3` residues have probability `4/2^256`. The draw is within statistical distance `S3 (1/p - 3/2^256) = 1.574e-39 (2^-128.90) < 2^-128` of uniform on `F_p`; over the at most 65 words of a run the distance is `eps_coin <= 65 * 2^-128.9 < 2^-122`, which the success bound (9.2) subtracts. A draw costs 31 operations: for the word one random-word operation, one load, one store into the cell `y` and three control operations (two addresses, the increment of the word index), 6 in all; for the reduction three steps each of a comparison, a conditional branch and a field subtraction (9 operations), with the loop control of 3 per iteration and 2 on exit (11); one Montgomery conversion of `x` (1); the entry of the call (2) and the address of `y` (2). Draws are made once per trial for the centre and once per isolation round for the shift: at most `K (1 + Z) = 65` draws, `65` words. No word is used twice, and the number of words used before a draw depends only on earlier words, so each draw is independent of the earlier course of the algorithm.

#### 4.1.2 Stage E: isolating a root of G

`G` is monic, squarefree, and a product of `d = deg G` distinct linear factors over `F_p` with `1 <= d <= DMAX` (it divides `S^((p-1)/2) - 1`, which is squarefree). The roots `r` of `G` are the usable `S`. While `deg G >= 2`, and for at most `Z` rounds (`ZCAP`): draw `a` (a draw as in 4.1.1; if it is 0, `a := 1`, since the Taylor shift uses `1/a`; the zero test is 5 operations and the replacement 2, charged in every round), replace `G` by `G(Z - a)` (a Taylor shift; its roots are `r + a`) and add `a` to a running shift, compute `X_a = Z^((p-1)/2) mod G` by schoolbook square-and-multiply, `G_+ = gcd(G, X_a - 1)` and `G_- = gcd(G, X_a + 1)` by classical Euclid. Then `G = G_+ G_- Z^e0` with `e0` = 1 if `G(0) = 0` and 0 otherwise. Keep, as the new `G`, the one of `G_+`, `G_-` of smaller nonzero degree (ties: `G_+`) if at least one is nonconstant; if both are constant then `G = Z` (the root is 0). When `deg G = 1` the loop ends and the root of the original `G` is `-G_0` minus the running shift. If `deg G >= 2` remains after `Z` rounds the trial fails (it ends, next `t`). Each round is charged at the cost of its operations at degree `deg G <= DMAX` (section 6). The lemma of section 9.4 bounds the probability that `deg G >= 2` remains after `Z` rounds: a round separates two given roots for at least `(p-3)/2` shifts, so it halves the degree with probability at least `w = 1/2 - 7.869e-40`, and four halvings take `16` to `1`; the failure probability is at most `P[Bin(64, w) <= 3] = 2.371e-15`, a finite sum, no premise.

### 4.2 Machine model and charging rules

Every operation of the algorithm is counted where it executes; none is estimated.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications, 330 operations; `x^e`; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each, and each such access is charged together with one address-formation operation (one control operation). Exception, the column kernels `ob4`, `ob8`, `ob16`, `ob32`, `ob64`, `ob128` (in stage C and in the outer transforms of stage D), `ob4m` and the two boundary passes of the loop (4.6): each load or store is 1 operation with no address operation. An element of the call's block at the position `j` is addressed as row base plus position offset, and a twiddle or spectrum word of the call as the table base plus the call's index scaled by a constant of the layer, the base-plus-index addressing of the load itself; the `2^k` row bases and the twiddle address are formed once per call (in the call charge `2 * 2^k + 6`, which is added to the kernel constant of the call, below) and held in integer registers, and the position offset advances with the index update of the loop step. Everywhere else (the rest of stage D, the `ob2` and `ob3` passes and the first and last passes of an extension of stage C included) the address operation is charged as above.
* every loop: `3n + 2` control operations for `n` iterations (the index update, the bound comparison and the conditional branch of each iteration, and one comparison and branch when the loop is left). Loops over the elements of an array written eight elements per pass (the pointwise, copy, fold and subtraction loops of the powering and of the products) are charged 3 per pass of eight, 1 for the bound, 2 when the main loop is left, and 3 per iteration for the remaining 0 to 7 elements.
* every other executed index or control operation, one each: shift, mask, or, addition, subtraction, comparison, conditional branch, assignment of a register, and the selection of an element of the register block (at most 32 data words) by a computed index. Data-dependent tests are charged per executed test.
* index arithmetic uses only shifts, additions, subtractions, comparisons and branches (the benchmark's primitive list has no integer multiplication, division or modulo): a multiplication by a power of two is a shift, by 3 or 5 a shift and an addition, and a product of an index and a stride is a running sum; each is charged as a control operation where it occurs.
* transforms: a transform of size `3 * 2^a` is a twiddle-free radix-3 stage (8 operations per leaf) followed by three rows of radix-2 passes of at most seven layers (the layers of each transform are split into passes by the exact minimum of the charges of this section: over every split of its layers into passes of `k <= 7` layers, the sum of the charges of a pass of `k` layers from layer `l0` of a row of `2^a` points, with the group-0 variant below, is least; the layers of the column passes of stage C and of the outer transforms of stage D are split the same way, by the least sum of the column-pass charges over passes of up to seven layers; the exact pass split of 0xplemonade's entry `d4b13ccd`). A pass works on blocks of `2^k <= 128` points held in registers, in the block form of our r = 3 entries `ef123c2b` and `253629b9` (their `pd_fwdp`, `pd_invp`): per block its `2^k` loads and `2^k` stores (1 each: a block element is addressed as the table base plus its index, the base-plus-index addressing of the load or store itself, as for `ob4` to `ob128` above; one load per word fetched from memory and one store per word written, the wording of the accepted entries `89b451ff` and `070a02b2`), `k 2^(k-1)` butterflies at three field operations each (two where the twiddle is 1 in group 0, below) and 3 of control (2 for the base of the block and 1 for its share of the block loop, below); per group its `2^k - 1` twiddles formed and held in registers for all its blocks (24 operations for `k = 4`: two loads with their addresses, one multiplication, three squarings, eleven multiplications by register constants and control; 16 for `k <= 3`; for `k = 5, 6, 7` its `2^k - 1` twiddles are loaded from the twiddle table, 1 each (base plus index, as for `ob32`), with 9 operations of address formation and control, `2^k + 8`: 40, 72, 136); per pass `5 + (9k + 2) + 12` (forward) or `6 + (9k + 2) + 12` (inverse) of pass set-up. Block loop: a pass of `k` layers at layer `l0` of a row of `2^a` points has `2^l0` groups of `n = 2^(a - l0 - k)` blocks; `n` is a constant of the pass, stored with the other parameters of the pass in the plan of the product, and the pass is entered at the body for its `n`. A group of `n >= 4` blocks runs them four per pass of a straight-line body (the four blocks addressed as the block base plus the constants 0 to 3 times the block stride in the loads and stores themselves), loop control `1 + 3 n / 4 + 2 <= n` for `n >= 12` (at r = 18 every group of more than one block has `n >= 16`); a group of one block has no block loop. So 1 per block covers the block loop. Twiddle 1 in the block-form passes: the twiddles of a group depend only on the group and the layer, and in group 0 the first twiddle of each layer is `w^0 = 1`; in every block of group 0 the butterflies of these twiddles, `2^(k-1-j)` in the layer `j = 0, ..., k-1` of the pass, `2^k - 1` per block, are their addition and subtraction, 2 operations. Group 0 of every block-form pass (forward and inverse) runs a straight-line variant of the block body without these multiplications: `2^k - 1` operations less per block of group 0 (`2^(a - l0 - k)` blocks) and 3 control operations more per pass. The one pass of a product that fuses its last forward layers, the pointwise product and its first inverse layers keeps the charge of a leaf pass: each butterfly is three field operations (none for the multiplication when the twiddle is 1), each twiddle is one load with its address operation. The first twiddle of each layer of a block is read through a running pointer of that layer, which is then advanced by the stride of the layer (one operation); the strides are formed once per pass (one shift per layer; in an inverse pass an addition and a shift per layer and 2 for the top of the table) and the pointers are set once per group (one operation per layer), and the at most five pointers and their strides are held in integer registers. The blocks of a group after its first run eight per pass of a straight-line body, the block base advanced by 1 per block; the block loop is charged as the loops of eight elements above (1 for the bound, 3 per pass of eight, 2 when the main loop is left, 3 per remaining block, 2 on exit), and the group loop 3 per iteration and 2 on exit. The register file is the machine restriction of claim.json: one register file of 387 words, 256 field registers of 256 bits plus 131 integer (address) registers (as the live entry cryptogakusei `1533f8f0` declares a file of 304 registers of 256 bits), counted in the memory (7(d)), every other value charged as a load or store (a block-form pass uses at most 256: the 128 data words, 127 twiddles and the butterfly temporary, as `ob128`; the fused leaf pass 18: the 16 data words, the twiddle operand and the butterfly temporary; the stage-C pass `ob128` uses 256: 128 data words, 127 twiddles and the butterfly temporary), and the 131 integer registers of the file for a call (the 128 row bases of an `ob128` call, the twiddle address, the position offset and the loop bound). Stage C (4.6) and the outer transforms of stage D (4.4.1, item 6) use column kernels: a column pass of `k <= 7` radix-2 layers runs over `2^k` rows at `cnt` positions and keeps its `2^k - 1` twiddles in registers for the whole position loop (`ob8`: 8 data words, 7 twiddles and the butterfly temporary, 16 of the 18 words; `ob4`: 4 + 3 + 1). Per position it loads `2^k` elements, makes `k 2^(k-1)` butterflies at 3 operations each (2 where the twiddle is 1, below) and stores `2^k` elements; its position loop is written eight positions per pass (the positions of a pass are addressed by the position offset plus the constants 0 to 7 in the loads and stores themselves, and the offset advances once per pass), so its loop control is `F(cnt) = 1 + 3 floor(cnt / 8) + 2 + 3 (cnt mod 8) + 2` per call, not 3 per position; each load or store is 1 (base-plus-index, above). Charges in stage C: a call over `nb` blocks (`nb = 2^k`; 3 for `ob3`) is charged the call charge `2 * nb + 6` (`sc_ocall` of the cost model) plus the kernel constant plus the per-position charge times `cnt`: `ob128` `269 + 1600 cnt + F(cnt)`, `ob64` `139 + 704 cnt + F(cnt)` (per call their 127 or 63 twiddles loaded at 2 each, a load with its address operation, 3 of control and 2 per layer after the first: `269 = 254 + 3 + 12`, `139 = 126 + 3 + 10`; per position `2^k` loads and `2^k` stores, `k 2^(k-1)` butterflies at 3 : `1600 = 256 + 1344`, `704 = 128 + 576`), `ob32` `34 + 304 cnt + F(cnt)`, `ob16` `18 + 128 cnt + F(cnt)`, `ob8` `10 + 52 cnt + F(cnt)`, `ob4` `6 + 20 cnt + F(cnt)`, and for the radix-3 stage and a one-layer remainder `ob3` `7 + 22 cnt + F(cnt)` and `ob2` `5 + 11 cnt + F(cnt)` (their loads and stores 2 each with the address operation), with the loop of the calls at 3 per call and 2 on exit (a run of `L` layers is cut into passes of at most seven layers by the split of least charge, a dynamic program over the layer boundaries on the charges above at the run's row count and positions, a constant of the algorithm for each run). An outer transform of stage D over `n` outer points (`n = 2^a` or `3 * 2^a`) at `cnt` positions is charged as in stage C: the twiddle table of the outer transform (`n` entries, 3 operations each, 4.5), for `3 | n` the `n/3` calls of `ob3`, and per row of `2^a` outer points its `a` layers as passes of `ob128` and one pass for the remaining layers, every call with the call charge and the loop of the calls. The four 256-bit constants of the radix-3 stage of a transform are held in four words of the register file for the whole stage, loaded once per driver call (4 loads with their address operations, 8 operations); a use costs no load. Twiddle 1 in the column kernels (the convention of the fused leaf pass above and of 1aa56884: a butterfly whose twiddle is 1 is its addition and subtraction, 2 operations): a column pass of `k` layers on a row of `2^a` points runs from the large-span end (forward) or towards it (inverse), and the butterflies with twiddle 1 of its layers are those at offset 0 of each block, `2^j` in its `j`-th layer, all in the call at offset 0 of each block (`2^k - 1` per position; `2^n - 1` per position over a run of `n` layers of a row); that call is a straight-line variant of the kernel without their multiplications, 1 operation less per such butterfly and position and 3 control operations more per such call. In the two-layer passes at the small-span end (the `ob4` pass of an inner transform, `ob4m` and the two boundary passes of 4.6) 3 of the 4 butterflies of each position and direction have twiddle 1 (both of the layer of span 2, one of the layer of span 4): 3 operations less per 4 points and direction.
* random words: the cost model's random-word primitive (an independent uniform 256-bit word) is one operation per word. The word of a draw is also loaded, stored into the cell `y` of the draw and addressed (one load, one store and three control operations), 6. A draw is that word (6), the reduction modulo `p` (three steps each of a comparison, a conditional branch and a field subtraction, 9, with the loop control of three iterations, 11), the conversion of the result to the internal representation (1), the entry (2) and the address of `y` (2): 31 operations. The shift of an isolation round is also tested for zero (5 operations) and, if zero, replaced by 1 (2 operations).
* the bit loops of inversion and exponentiation executed outside stages with a per-operation rule: 2,310 control operations per inversion.
* small-degree work in the line setup, the schoolbook `Z^((p-1)/2)` for `d <= 40` and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 6 control operations.
* the line evaluations of stage B: 351 each, the operations of the scaled straight-line program of section 3 and Appendix L (`135 + 12 r` at r = 18), not the full reference permutation `C(18) = 594`. The stage-G verification (below) runs the two full reference hashes and is charged `594` each. Nothing else is charged as a unit.
* Montgomery conversions: every conversion of an integer to or from the internal representation (for example the word converted in a draw, the exponent in the Taylor shift, the constants of the twiddle setup, the inputs of the two reference hashes and the six conversions of the output in stage H) is one Montgomery multiplication and is charged as one field multiplication. The constants of the permutation are stored in Montgomery form and need no conversion.
* output (stages H and I): in stage H the answer (two pairs, the digest and the centre) is converted out of the Montgomery representation (6 multiplications) and encoded as 64 hexadecimal digits each at 12 operations per digit and 5 per call. Stage I charges everything after the last step of the algorithm: the formatting of the report, 400 operations per byte of a buffer of 8,192 bytes (a decimal digit costs at most 44 operations, a copied byte at most 10, a conversion at most 150), 20,000 operations of report loops, 100 for the entry and the length check, one write system call at `10000 + 8 * 8,192` and one exit system call at 10,000 (a system call is 10,000 operations plus 8 per byte copied), and the bookkeeping of the stage (2 * 1,000).
* allocation: every array is taken from one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes (`need` bytes), and `need` decides the allocator. A block of more than 2^45 = 35,184,372,088,832 bytes comes from the pool, one region with two ends: its blocks follow each other in address order, each with a header (size, size of the previous block, in-use flag), no two free blocks are adjacent, and the unused middle between the two ends is one free block. Each allocation statement of the program uses one end of the pool, a constant of the statement: the statements (`g` of stage A, the block array of stage B, `MU` and `Y`, the work arrays of the Newton products, of a squaring step (in a chunked product of a squaring step, all its arrays except the accumulators of the square `R^2`, which use the low end) and of a shift, and the results inside the half-gcd: the quotient and remainder of a node and of the outer loop, the outputs of apply_inv and of the matrix products, every allocation of the lean stage D (`ld_new`, all sites `# pool:H`, including the working arrays of its block products), and the reversed `g` and the operand rev(X^v P1) of stage C step 1 (4.6)) use the high end, every other statement the low end, except that the copies of the remainders returned by a node that applies its second matrix (4.4, step (6)) are taken from the low end. A low request walks the blocks upward from the bottom of the pool, a high request downward from the top (the two sizes in the header give both neighbours, so the two walks are the same code mirrored); it takes the first free block with at least `need` bytes (the unused middle is the last block of either walk) and cuts the block from the side nearest its own end, and the rest stays a free block when it is at least 128 bytes (else it belongs to the block); a free merges the block with a free neighbour on either side, the unused middle included, the same code for both ends. Since no two free blocks are adjacent and a walk ends at the middle, a walk examines at most 2 P + 1 blocks, P the live blocks on its side of the pool, and one block examined is 13 operations (two comparisons with branches, two loads, the advance). A block of at most 2^45 bytes comes from the slab classes: the class `j` is the least `j >= 7` with `2^j >= need`, a slot is `2^j` bytes; a request takes the first slot of the free list of its class, else a new slot from the end of the slab area, and writes the class and the in-use flag into the header; a free puts the slot on the free list of its class. The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows: a request of the pool 97 operations besides the walk (the statement that calls the allocator, the set-up, the split, the header stores, and a flat 64 for the statistics) and 13 per block examined, a request of a slab class at most `126` (the statement that calls the allocator, the class `j` by a binary search over 7..63 in 6 steps of 6 operations, the pop or the bump, the two header stores, and a flat 64 for the statistics), a free 81 for a slab block and at most 105 for a pool block (a free tests the size of the block to choose the allocator, in place of the test for a null pointer, which the program never needs). Every allocation of the walk is charged `1 + 120 + 13 (2 L + 1)` with L the live blocks at that point, which covers the pool (P <= L, the 97 operations and 13 per block examined) and the slab path (at most `126 <= 1 + 120 + 13` operations), and every free 105 (550 per allocation and 105 per free at 16 live blocks in stage E). The memory of both allocators is the arena of section 7.
* trial loop: the test of the trial counter, its increment and the bookkeeping of the trial, at most 12 operations per trial, are `TRIAL_EXTRA` = 12 in the ledger; the loop test and update of stage A are 5.
* the offline derivation of the constants is charged in section 6.2.

### 4.3 Stage C: the powering schedule (cyclic form, below the block length; block mode in 4.5)

In this entry stage C runs in the value domain (section 4.6). This section and 4.5 define the transforms, the products and the Newton reciprocal that 4.6 uses for its set-up.

For the exponent `E` (here `(p-1)/2`), `m` the degree of the modulus, `N = 3 * 2^a >= 2m - 1` and `N' = 3 * 2^b >= m + 1`. A transform of size `3 * 2^a` is a twiddle-free radix-3 stage (Good-Thomas; each radix-3 leaf costs 8 operations) followed by three independent
rows of radix-2 transforms of length `2^a`, run as passes of at most seven layers (blocks of at most 128 data words in registers, the group twiddles held in registers: the block form of section 4.2). The state is `s = a / N` so no scaling is needed in the loop.
One step maps the residue `a` (`m` coefficients, stored in the buffer `Y` of `N` elements) to `a^2 mod g`:
```
Y := conv_sq(Y)                       square: forward transform, pointwise square fused with the first inverse pass, inverse transform
F[i] := Y[i] + Y[i+N'] (i < m)       fold of the low part modulo x^N' - 1 (saved in the buffer F of m elements)
Y[0..m-2] := Y[m..2m-2]               high part T1 of the square
Y := conv(Y, MU)                      quotient q (Barrett): MU = x^(N-m+2) * floor(x^(2m-2)/g) / (N N') stored compactly (m-1 elements)
Y := conv_N'(Y, g)                    (q * g) mod (x^N' - 1)
Y[i] := F[i] - Y[i] (i < m)           new residue; if the exponent bit is 1: shift by x and subtract lead * g (streaming)
```
In this cyclic form the spectra of `MU` and of `g` are not stored (block mode, section 4.5, keeps `MU` and `g` in coefficient form and makes their chunk forms at each use): for each multiplication the second operand is transformed one row of the Good-Thomas layout at a time into a buffer `tmp`, immediately multiplied into the corresponding row of `Y`, and discarded.
`MU` is computed once from `g` by Newton iteration with the same row-wise products. The leading exponent bits are absorbed by starting from the monomial `S^v` with `v < m`.
All charges of this stage depend only on `m` and the exponent, not on the coefficients.
### 4.4 Stage D: the half-gcd

Notation: a polynomial is stored as its coefficient array with the top coefficient nonzero (length = degree + 1). Euclid sequence of `(a, b)`, `deg a > deg b`: `r_0 = a`, `r_1 = b`, `r_{i-1} = q_i r_i + r_{i+1}`; `d_j = deg q_1 + ... + deg q_j`, so `deg r_j = deg a - d_j`;
`R_j = Q_1 ... Q_j` with `Q_i = [[q_i, 1], [1, 0]]` (entries of degree at most `d_j`; the first-row entries of degree exactly `d_j` for `r11`), and `(r_0, r_1)^T = R_j (r_j, r_{j+1})^T`.

`hgcd(a, b, k)` (`deg a = n`) returns, for `h = max{ j : d_j <= k }`, the matrix `R_h` and, only when asked (the calls of the Euclid driver, below), the pair `(r_h, r_{h+1})`; the inner calls return the matrix only. The procedure: if `b = 0` or `n - deg b > k` return the identity. If `k <= 96`, plain Euclid (`poly_divrem_naive`) while the next quotient degree fits the remaining parameter; a division step whose quotient has two coefficients (the normal case) is one pass over the remainder, `r_k = a_k - q0 b_k - q1 b_(k-1)`, with `b_(k-1)` kept from the previous iteration and no copy of `a` (per element 2 loads, 2 multiplications, 2 subtractions, 1 store, each load and store with its address operation, the loop control of 3 and the test `if (k)` of 2 operations), and `R := R Q` for a two-coefficient quotient is likewise one pass per entry pair (`mul_add_q2`).
Otherwise, `k1 = ceil(k/2)` (`k1 = floor(n/2)` if `2 k1 > n`), `s = n - 2 k1`: (1) `R1 = hgcd(a quo x^s, b quo x^s, k1)` (the top parts, matrix wanted); (2) `(c, d) = R1^{-1} (a, b)` by NTT products (`apply_inv`): `c = s (r22 a - r12 b)`, `d = s (r11 b - r21 a)`, `s = (-1)^h`, evaluated cyclically on `3 * 2^j` points (the high coefficients of `c` and `d` cancel, so the cyclic result is exact); the Good-Thomas rows are processed one at a time, and in each row `a` and `b` and each of the four matrix entries are transformed once (six forward transforms of a row) and the two output rows are inverse transformed (`conv_bilin_otf`), the sign of each output being absorbed in the scale factor `1/N`; (3) if `d = 0` or the next quotient degree `deg c - deg d` exceeds `k - d_1`
(`d_1 = deg R1`) return `R1` and `(c, d)`; (4) divide `c = q d + e` (`divrem_any`); (5) `k3 = k - d_1 - deg q`, `s3 = deg d - 2 k3`; if `s3 > 0`, `R2 = hgcd(d quo x^s3, e quo x^s3, k3)` (the top `2 k3 + 1` coefficients of `d` and the coefficients of `e` of the same degrees, read in place, matrix wanted), otherwise the call runs on `(d, e)`; this is the same top-coefficient lemma that step (1) uses (the quotients of a pair whose degrees sum to at most `k3`, and the stopping test, depend only on those coefficients; von zur Gathen and Gerhard, Modern Computer Algebra, chapter 11; the same truncation as bradcush 1aa56884, its lemma 4.4), and 1aa56884 (its Appendix G.3) runs the node with and without it against plain Euclid; (6) only if the caller wants the pair, `(c', d') = R2^{-1} (d, e)` by `apply_inv`, each moved into an array of its own length; return `R1 Q R2` (matrix products by NTT, only if the matrix is wanted; the product of the two 2 x 2 matrices transforms each of the eight entries once per row, with the right-factor entries of one column pair held and the left-factor entries streamed, and inverse transforms the four outputs, `conv_bilin_otf` again).
The outer function `poly_gcd_own` repeats, while `deg b > 0` and `n = deg a > 192`: `(c, d) = hgcd(a, b, floor((n+1)/2))`, one division `c = q d + e` and `(a, b) := (d, e)`; at or below 192 it runs classical Euclid; at the end it scales the last nonzero remainder to be monic (one inversion, `deg + 1` multiplications). With `H-NORMAL` (9.5) stage D runs the normal-sequence procedure of bradcush (entry e6dcb600): every division tests that its quotient has degree 1 and every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter ; a zero remainder met inside hgcd or in the division of the outer loop also ends the trial (ABORT); on any other case the trial ends (ABORT) and the next centre is drawn (section 6.3).

**Division.** `divrem_any(a, b)`, `la - lb + 1` quotient coefficients `kq`: if `kq <= 64` or `lb <= 64` schoolbook (`poly_divrem_naive`); otherwise (`divrem_fast`) the reversed Newton identity: `q_rev = (a_rev * inv(b_rev mod x^kq)) mod x^kq`, `q = reverse(q_rev)`, `r = a - q b` (low `lb - 1` coefficients), with
the reciprocal by Newton iteration `g_{2t} = g_t - x^t (g_t * mid(f g_t))` and all products by `poly_mul`.

#### 4.4.1 The lean stage D (this entry; the stage D of bradcush 1aa56884, its section 4.4 and lemmas 4.4 and 4.8, credited)

This entry runs the half-gcd above with six changes, all from 1aa56884 (credited in the dependencies and the note), and a seventh, the apply plans of 0xplemonade ff21bd28 (item 7; credited likewise), charged by this model's rules of 4.2 and 4.5. They change where arrays live and which coefficients are formed, never a quotient: every quotient used is a quotient of the whole pair (lemma 4.4 above, and lemma 4.8 below).

1. *The base case in place.* For `k <= 96` the two remainders are two arrays and a division step with a quotient of two coefficients is one pass `r_k = a_k - q0 b_k - q1 b_(k-1)` written over the array of `a`; the roles of the two arrays swap. The four matrix entries are four arrays of `k + 2` elements allocated once, and `R := R Q` writes `r11 q + r12` over `r12`. No array is allocated or freed inside the loop.
2. *Matrix-only calls.* A call returns the reduced pair only when its caller wants it: the calls of the Euclid driver `poly_gcd_own` and, inside them, the second calls with `s3 <= 0`. Every call inside a first call, and every truncated second call, returns its matrix only.
3. *Windows.* In a node that wants its matrix only and has `s3 > 0`, the block products of `apply_inv` (or the plan of item 7) form only the top window of `c` and `d`: the coefficients of degree at least `s3 - 1` (lemma 4.8 (a)). Such a node tests that the coefficients of `c` and `d` at their normal leading degrees `la - h - 1` and `la - h - 2` are nonzero (2 tests, charged) and ABORTs otherwise, so it never reports a shorter remainder from a window.
4. *The two tests and the ABORT.* At every division the quotient test (the quotient has degree 1) and after every recursive call and every call of `poly_gcd_own` the return test (the call returned exactly its parameter as degree count; a zero remainder inside hgcd or in the outer-loop division also ABORTs), 2 operations each, charged wherever they execute. If a test fails the trial ABORTs: the allocator is reset to its state after initialisation (`1,000` operations, charged in section 6) and the next centre is drawn. On the normal remainder sequence neither test fails (6.3), so every division of stage D is the one-pass division by a quotient of two coefficients and the Newton division is never run.
5. *The top node in pieces.* Stage C leaves `g` and `R` in two pieces each, the coefficients `[0, cut)` and `[cut, l)` with `cut = 22,351,744,247,791,616`. The first call of `poly_gcd_own` frees the high pieces of `g` and `R` right after its own `apply_inv`; the pair `(c, d)` is then formed from the low pieces only (`c` first, by the block products of 4.5 with the window `[0, lc)`, `lc = m + 1 - k1`; then `r22` and `r12` are freed; then `d`; then `r11`, `r21` and the low pieces are freed). The pair `(d, e)` of the second call is written as two pieces at `cut2 = deg d + 1 - k3` and handled the same way.
6. *Block products of stage D.* Each product of apply_inv (unless the apply runs a plan of item 7), of the top node and of mat_mul uses the cheapest of the single transform, scheme (a) at block length 2^31 (one row of passes of 2^32 points) and scheme (c) at the block length 2^b of least charge (b = 6..31, transforms of 2^(b+1) points). The number of chunks is the least power of two that brings a chunk form to at most `m // 16` elements. The outputs are allocated first at their true lengths, the chunks accumulate into them, the working arrays follow and are freed at the end, and the operands are freed after the last chunk. This replaces, for stage D, the Blocks, Choice, stage-D and Scaling bullets of 4.5. There is no placement pass in stage D: each output of a scheme (c) product is untwisted straight into its window with the scaled weight `sign / (NB n2) * w^(-e)` (the sign of the output, the factor `1/NB` of the unnormalised inverse transform and `1/n2` of the outer transform applied here), charged 15 operations per product (the scale and the weight base), 7 per untwist call (the table entry and the scale loaded and the result stored, each 2 with its address operation, and one multiplication) and the chunk and outer-point loops; at r = 18 this is 216,541,815,277,238,719 operations per trial (5,204,131 scheme (c) products, 16,765,014,117,587,808 untwist calls), included in row D. The outer transforms of scheme (c) use the column kernels of stage C (4.2: `ob128`, `ob64`, `ob32`, `ob16`, `ob8`, `ob4` and `ob2` across the outer points with base-plus-index loads and stores, `ob3` for the radix-3 stage) with the twiddle table of the outer transform, and the assembly of a chunk, the untwist into the window and the fold of an outer point into the row of its chunk are loops of eight elements per pass (4.2), with 1aa56884's conventions for these three primitives (credited). The kernels `ocp`, `oax` and `ozf` of 4.5 are not used in stage D. The choice between the single transform and the block products counts every charge of each path, including the allocations and frees the block path adds.
7. *Apply plans (the direct whole-pair and fixed-slot apply plans of 0xplemonade's entry `ff21bd28`, read as text, re-implemented and charged in this cost model).* An apply `(c, d) = adj(R1)(a, b)` of steps (2) and (6) of 4.4 (`c = s (r22 a - r12 b)`, `d = s (r11 b - r21 a)`, `h = d_1`, `lc = la - h` and `ld = lc - 1` coefficients; in a node of item 3 only the coefficients from `w = s3 - 1` on) runs either the apply of item 6 and 4.4.2 (single-transform forms) or one of the two plans below, whichever has the smaller charge. The live peak of stage D with the plans is 3,626,090,790,072,992,512 bytes, below that of stage C (3,814,698,222,768,355,136 bytes), so no plan raises the memory (7). The lengths, budgets and windows of every call are fixed on the normal sequence (6.3), so this choice is a constant of the algorithm for each call of the walk: at r = 18, of the 1,614 distinct apply calls of the walk, 688 run a plan (508 direct, 180 fixed-slot; 174 of them on a window). A plan uses one transform size `N = 3 * 2^e`; both forms are priced at every `e = 2, 3, ...` up to the first with `N >= lc - w + h` (8 control operations and the plan set-up per size), and the cheapest is run; 80 operations of entry, the plan scale `1/N` (plan_invN, as for every transform) and 22 for the two length checks. A transform of an array of `l <= N` coefficients is `6` plus the radix-3 input stage over the `l` coefficients plus three rows of block-form passes (4.2); an inverse is `3` plus three rows of inverse passes plus the radix-3 output stage over the coefficients formed; the scaling by `s/N` of `t` outputs into their array is `8t + 5` (a load, a multiplication, a store and the loop step per coefficient). Both forms first transform the nonzero entries of `R1` into spectra of `N` points; `R1` is freed then when the call consumes it.
(i) Direct whole-pair (no window, `N >= lc`): `a` and `b` are folded modulo `X^N - 1` (10 per coefficient beyond `N`: two loads, the addition, the store, the loop step) and transformed into the operand spectra `A` and `B`; one pass over the `N` points forms `C = r22 A - r12 B` over `A` and `D = r11 B - r21 A` over `B` (per point six loads with their address operations, four multiplications, a subtraction and an addition, and the two stores at the addresses of the loads of `A` and `B`: 20; the eight-element loop of 4.2, `2 + for8(N)`); the two inverses form the first `lc` and `ld` coefficients and the scaled outputs are written. Since `deg c, deg d < lc <= N` the cyclic results are exact.
(ii) Fixed-slot (`B = N - h > 0`): the outputs from `w` (`w = 0` without a window) are cut into `nb = ceil((lc - w) / B)` blocks of `B` coefficients, handled from the highest to the lowest (`3 nb + 6` of loop control). Block `i` covers the outputs `[s, e)`, `s = w + i B`, `e = min(s + B, lc)`: it transforms the windows `[max(0, s - h), e)` of `a` and of `b` (at most `N` coefficients) into `A` and `B`, forms `C` and `D` in one pass over the `N` points (charged 24 per point: six loads and two stores with their address operations, four multiplications, a subtraction and an addition, 22; `2 + for8(N)`), inverse transforms both (all `N` outputs; the first block of an apply without a window only its outputs) and writes the scaled outputs `[s, e)` of `c` and `[s, min(e, ld))` of `d`; 20 of control per block. A window of `v <= N` coefficients times an entry of at most `h + 1` coefficients has at most `v + h` coefficients, so the cyclic wrap of length `N` reaches only the positions below `v + h - N`; the outputs of block `i` sit at the positions from `min(s, h)` of its window on, and `v + h - N <= min(s, h)` since `e - s <= B`, so they are exact. The form is used when the first block that reads a full window of `N` coefficients has index at most 8 (the blocks from it to the last but one are charged alike).
The outputs are written over `a` and `b` when the caller owns both and there is no window (the direct form reads `a` and `b` before it writes; a fixed-slot block writes `[s, e)` and the blocks after it read only positions below `s`), else into two arrays of `lc - w` and `ld - w` elements. Memory of a plan: the four matrix spectra and the two operand/output spectra, six arrays of `N` elements (lean stage-D allocations, 4.2), besides the pair and the outputs; no chunk form or accumulator.

**Lemma 4.8 (windows and pieces; 1aa56884's lemma 4.8).** (a) In a node that wants its matrix only, with `s3 > 0`, the rest of the node reads `c` only at degrees at least `s3` and `d` only at degrees at least `s3 - 1`. (b) In the top node, after the first call's `apply_inv` no operation reads `a` or `b` at degrees at least `cut`, and the low `lc` and `lc - 1` coefficients of `c` and `d` computed from `a mod X^cut` and `b mod X^cut` are the `c` and `d` of step (2); the same holds for `(d, e)`, `cut2` and `(c', d')`.
*Proof.* (a) The stopping test and the quotient test use `deg c` and `deg d`; the quotient `q = q1 x + q0` uses the top two coefficients of `c` and of `d`; and `e_i = c_i - q0 d_i - q1 d_(i-1)`. The second call reads only `d quo x^s3` and `e quo x^s3`, that is `d_i` and `e_i` for `i >= s3`, hence `c_i` for `i >= s3` and `d_i` for `i >= s3 - 1`. After it the node needs only `R1`, `q` and `R2` (and `s3 - 1 <= deg d - 1`, so the top two coefficients are inside the window). (b) The first call reads `a quo x^s` and `b quo x^s` and, after its `apply_inv`, only its own arrays; the top node then reads `a` and `b` only in step (2). For `i < lc <= cut` the coefficient `i` of `r22 a` is `sum_j r22_j a_(i-j)` with `i - j < cut`, so it equals the coefficient `i` of `r22 (a mod X^cut)`; `c` has length `lc`, so it is the low `lc` coefficients of `s (r22 (a mod X^cut) - r12 (b mod X^cut))`, and likewise `d`. For the second call, `cut2 = deg d + 1 - k3 >= lc'` with `lc' = deg d + 1 - h3` and `h3 = k3` on the normal sequence. QED

The charges of these steps are this model's (4.2, 4.5), not 1aa56884's: with 1aa56884's own conventions the same walk gives its published row D to the unit (`1,062,106,645,154,198,605,714,641` at r = 21, recomputed in our model with their conventions switched on), and with this model's primitives, with the outer transforms of item 6 on the stage-C column kernels, 1aa56884's conventions for its other three primitives and the changes of 4.4.2, it gives row D of section 6.

#### 4.4.2 Scaled division and product forms (this entry; the stage D of weijiekoh a78f526e, its section 4.4, credited)

This entry runs the stage D of 4.4.1 with three changes from weijiekoh's entry a78f526e (credited in the dependencies and the note), charged by the rules of 4.2. They change how a division step and a single-transform product are computed; every quotient degree, every length of a polynomial and every branch of 4.4.1 is unchanged (lemma 4.9).

1. *Scaled division.* A division of `U` by `V` with a quotient of two coefficients and a divisor of at most 2,048 coefficients (every step of the base case and of the classical Euclid of `poly_gcd_own`, and the division of a node when its divisor is that short) is the scaled step `W = sigma U - (A x + B) V`, with `v = lc(V)`, `sigma = v^2`, `A = v lc(U)`, `B = v u' - lc(U) v'` (`u'`, `v'` the coefficients of `U` and `V` next below the leading ones). No inversion is executed: the inversion of `v` (the 330 field operations of `a^(p-2)` and the 2,310 control operations of its bit loop) is replaced by one more field operation of the set-up (5 against 4; 2 for a divisor of one coefficient), and each remainder coefficient costs one more multiplication, `sigma U_i` (per element 2 loads, 3 multiplications, 2 subtractions, 1 store, with the address operations and the loop control of 4.4). The matrix step is `R := R Q~` with `Q~ = [[A x + B, 1], [sigma, 0]]`: each row `(r_e, r_f)` becomes `(r_e (A x + B) + sigma r_f, r_e)`, one more multiplication per coefficient of `r_f`; at a node the product `R1 Q~` likewise. A division by a longer divisor is the exact division of 4.4. The quotient test and the ABORT are unchanged.
2. *Transform length from the output (apply_inv).* A single-transform `apply_inv` chooses its transform length `N` from the output length `lc = la - h`, not from `la`. `c` and `d` have lengths `lc` and `lc - 1`, at most `N`, so their reductions modulo `X^N - 1` determine them; the operands `a`, `b` and the four entries are read folded modulo `X^N - 1` as they are copied into a row (a coefficient of index `i >= N` is added into position `i mod N`: a load, an addition, a store and the loop step, charged 10 per folded coefficient per row read).
3. *Plain power-of-two length.* A single-transform product (of `apply_inv` or of the matrix products) may use a transform of `2^a` points (one row of the radix-2 passes of 4.2, no radix-3 stage; `2^a` divides `p - 1` for `a <= 32`), `2^a` the least power of two that holds the output, in place of the `3 * 2^b` points of the three-row form, whichever has the smaller charge. Its operands are copied into the row at 7 operations per coefficient and the rest of the row is zero-filled at 5 per position (a store with its address operation and the loop step) (folded as in item 2 when longer than the row); the pointwise products and the inverse passes are those of one row of the three-row form. The row of `2^a` points can be longer than the `3 * 2^b` points of the three-row form; the arrays of the chosen form are the ones allocated, and they are in the allocation sequence of section 7.

The choice between the single transform and the block products of 4.4.1 item 6 compares the charges of items 2 and 3; an apply may instead run a plan of 4.4.1 item 7 where that has the smaller charge. Lemma 4.8 is unchanged.

**Lemma 4.9 (scaled pairs).** With item 1, every remainder that stage D forms is a nonzero constant multiple of the remainder of the same index of the exact sequence of 4.4; every matrix entry has the degree of the exact one; and `apply_inv` returns nonzero constant multiples of the exact pair. *Proof.* If `U = alpha r_(j-1)` and `V = beta r_j` with nonzero constants, the exact quotient of `U` by `V` is `q = (A x + B) / sigma` (the quotient of degree 1 is fixed by the top two coefficients of `U` and `V`), so `W = sigma (U - q V) = sigma alpha r_(j+1)`, and `sigma = v^2 != 0`. Hence every degree, every quotient degree, every zero test and every branch (the quotient, return and window tests, the stopping tests) is that of the exact sequence, and so is every length and allocation. `A = v lc(U) != 0`, so the entries of `Q~` and of the products `R~` have the degrees of the exact ones. `adj(Q~) = [[0, -1], [-sigma, A x + B]]` maps `(U, V)` to `(-V, -W)`, so for `R~ = Q~_1 ... Q~_h` (and `R1 Q~ R2` at a node) `adj(R~) = adj(Q~_h) ... adj(Q~_1)` maps `(a, b)` to plus or minus the scaled pair at index `h`, which `apply_inv` forms (its sign `s = (-1)^h` of 4.4 multiplies both outputs by plus or minus 1). The top-coefficient lemma of 4.4 steps (1) and (5) holds for the scaled step as for the exact one: `A`, `B` and `sigma` are read from the top two coefficients, and the coefficient `i` of `W` reads `U_i`, `V_i` and `V_(i-1)` only. The last nonzero remainder is made monic at the end (4.4), so `G` is the monic gcd. QED

#### 4.4.3 Aligned budgets and the inversion-free node on three rows (this entry; the half-gcd of bradcush 4bcabff8, credited, as ported in our r = 3 entry bcf8e01c)

This entry runs the half-gcd of 4.4.1 and 4.4.2 with two changes. Neither changes a quotient, the stopping tests or the result: every call returns the matrix of the first `h` quotients of its pair, `h` equal to its parameter on the normal sequence.

1. *Aligned split.* A node of parameter `k < 2^54` gives its first call the parameter `k1 = 2^(b-1) - 1`, `b` the bit length of `k`, in place of `ceil(k/2)` (`k1 = floor(n/2)` if `2 k1 > n`, as before); the second call takes the parameter left over, `k3 = k - h1 - deg q`, as in 4.4 step (5). A node of parameter at least `2^54` splits as before. The top-coefficient lemma of 4.4 steps (1) and (5) holds for every `k1 < k`: the quotients of the first call are fixed by the top `2 k1 + 1` coefficients of the pair, and the second call continues the same sequence (von zur Gathen and Gerhard, Modern Computer Algebra, chapter 11; the split point is free). The point is that a parameter `2^j - 1` splits into `2^(j-1) - 1`, one division and `2^(j-1) - 1`, so below `2^54` most calls have a parameter of that form.
2. *The inversion-free node.* A call that wants its matrix only (the first calls and the truncated second calls of 4.4.1 item 2) with parameter `k = 2^j - 1`, `7 <= j <= 31`, reads the top `2k + 2` coefficients of its pair (its caller takes `s` and `s3` of 4.4 one smaller; by lemma 4.8(a) the windowed `c` and `d` of item 3 then start one degree lower) and runs bradcush's inversion-free half-gcd (entry 4bcabff8, with the transform reuse of b30de9bf; read as text only, ported and charged in this cost model as in our r = 3 entry bcf8e01c). Remainders are kept up to nonzero constants by pseudo-division, `lc(b)^2 a = Q b + e` with `Q` of degree 1 on the normal sequence: this is the scaled step of 4.4.2 item 1 (`sigma = lc(b)^2`, `Q = A x + B`), so the matrix the node returns is a product of the matrices `Q~` of 4.4.2 and lemma 4.9 applies to it and to every pair formed from it. A node of parameter `2^j - 1` makes two child calls of parameter `2^(j-1) - 1`; its products run on `3 * 2^(j-1)` points, the rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), each a transform of `n` points in the block form of 4.2 after a twist, joined by a 3-row CRT for `(c, d) = adj(M1)(a, b)` on the window; then the pseudo-division and the product `M = M1 [[Q, 1], [lc(b)^2, 0]] M2` on the two rows `Y - 1`, `Y + 1` only (`2n` points; 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` with the `1/2` folded into the `1/n` of the inverse, 10 operations per point). The product needs no third row: on the normal sequence every quotient has degree 1 and the scale of a step is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; each child returns the row `Y - 1` values of its matrix, the row values of `M1` are kept from the apply and reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). The twist of the row `Y - i` needs a root of unity of order `4n = 2^(j+1) <= 2^32`, the 2-part of `p - 1`, hence `j <= 31`. The base case (parameter 63) runs two remainder steps per pass over its window. Every pseudo-division tests that its quotient has degree 1 and every call tests on return that it removed exactly its parameter (2 operations each); on any other case the trial ends (ABORT, 6.3). The node returns its matrix in coefficient form in four arrays of `2^j + 1` words (entries of lengths `k + 1`, `k`, `k`, `k - 1`), which the caller uses as in 4.4.1.

**The two loops of the node (this entry).** *Fold.* The window of `a` (`4n'` coefficients, `n' = 2^(j-1)`) and the window of `b` (`4n' - 1`) are read once and the three rows `Y - 1`, `Y + 1`, `Y - i` are formed in one loop of eight positions per pass (4.2), position by position: `a_0 + a_2` and `a_1 + a_3` (2), their sum and difference for the rows `Y - 1` and `Y + 1` (2), and `(a_0 - a_2) + i (a_1 - a_3)` for the row `Y - i` (4, with the multiplication by `i`): eight field operations, four loads and three stores, each load and store with its address operation, 22 per position, and `2 + for8(n')` for the loop (`for8` as in 4.2), once for `a` and once for `b`; the twist of the rows `Y + 1` and `Y - i` by their running factors (2 per point and row) and the three forward transforms follow. This is charged in place of the row-by-row formation of the rows from the window, which per row copied the first chunk (4 per coefficient, and `3 n' + 2` of loop control) and folded the other three chunks into it in one accumulating loop (7 per coefficient, 8 on the row `Y - i`, and `3 (3 n') + 2` of loop control). *Two-output pass.* On each of the three rows of the apply one pass forms `C = r22 A - r12 B` and `D = r11 B - r21 A` from the row values of `a`, `b` and the four entries of `M1`; and in the product `M = P M2`, `P = M1 [[Q, 1], [b^2, 0]]`, on each of the two rows `Y - 1`, `Y + 1` one pass per column of `M2` forms the two entries of that column of `M` from the four entries of `P` and the column. Each is the two-output pass of 4.4.1 item 7 (i): six loads with their address operations, four multiplications, two additions or subtractions and two stores at the addresses of the loads of the two operands, 20 per point, and `2 + for8(n')` for the loop. This is charged in place of two pointwise passes per output. The bodies of the two loops, eight positions each, `8 * 22 + 3 = 179` and `8 * 20 + 3 = 163` instructions (3 of loop control), are counted as code in 7(a). Neither loop adds an array: the fold fills the six row arrays of the apply and a two-output pass writes over its operands, the arrays counted in the node arena. 0xplemonade's entry `8b1eb62a` (r = 7), whose note itemizes the node as fused two-output pointwise rows, was read as text and prompted charging the maps as two-output passes, priced here by the direct apply row of `ff21bd28`; no number or program is taken from it.

Charges (the rules of 4.2): for the rows that the two loops above do not form (the four entries of `M1` and of `M2` on their rows), a row of a product costs the copy of its window (4 per coefficient: a load and a store, each with its address operation), the zero fill of the rest of the row (2 per slot), the fold of a window longer than the row (7 per coefficient, 8 on the row `Y - i` with its multiplication), the twist (2 per point on the rows `Y + 1` and `Y - i`: the running factor and the multiplication), the forward transform of `n` points in the block form of 4.2 plus 10; the pointwise products are the two-output passes above; the inverse transform of a row plus 10, with `1/n` (row `Y - 1`) or the untwist times `1/n` (2 per point) fused into the CRT, which costs 22 per point (10 field operations, 3 loads, 3 stores, each load and store with its address operation); every loop carries the loop control of 4.2 (`3 n + 2`). The pseudo-division costs 30 and 13 per coefficient of the window the second child reads; the values of `Q` and of `M1 Q` cost 25 per point on each row of the product, which has the two rows `Y - 1`, `Y + 1` only (its 2-row CRT 10 per point, above); a node costs 40 for its call, 14 bump-arena operations (the allocations and releases of its working arrays) of 10 each, and its return tests 4. The scales `1/2^a` (`a <= 30`) are a table of 31 words built at the entry of stage D (one allocation; `1/2 = (p + 1)/2` an immediate, 29 multiplications, 30 stores, the loop), and the twist roots come from the twiddle table of 4.2. A matrix-only call on the node costs 40, the four allocations of its matrix and the allocation and release of its bump arena (the allocator of 4.2), and the node, `node(j) + 10`; the arena of the node holds at most `34,359,738,112` words (`j = 31`), far below the stage-C peak (section 7). Per trial on the normal sequence:

| j | parameter `2^j - 1` | `node(j) + 10` | calls per trial |
|---:|---:|---:|---:|
| 7 | 127 | 279,271 | 28 |
| 8 | 255 | 679,441 | 27 |
| 9 | 511 | 1,632,675 | 24 |
| 10 | 1,023 | 3,830,087 | 26 |
| 11 | 2,047 | 8,828,015 | 25 |
| 12 | 4,095 | 20,078,943 | 24 |
| 13 | 8,191 | 45,182,815 | 21 |
| 14 | 16,383 | 100,790,911 | 21 |
| 15 | 32,767 | 223,200,735 | 23 |
| 16 | 65,535 | 493,677,197 | 22 |
| 17 | 131,071 | 1,084,843,273 | 19 |
| 18 | 262,143 | 2,370,555,169 | 19 |
| 19 | 524,287 | 5,155,020,401 | 21 |
| 20 | 1,048,575 | 11,162,232,369 | 20 |
| 21 | 2,097,151 | 24,078,366,417 | 17 |
| 22 | 4,194,303 | 51,763,618,097 | 19 |
| 23 | 8,388,607 | 111,242,448,351 | 18 |
| 24 | 16,777,215 | 238,305,077,339 | 17 |
| 25 | 33,554,431 | 509,030,637,171 | 14 |
| 26 | 67,108,863 | 1,084,462,510,019 | 14 |
| 27 | 134,217,727 | 2,304,897,176,451 | 16 |
| 28 | 268,435,455 | 4,888,080,423,971 | 15 |
| 29 | 536,870,911 | 10,345,416,554,115 | 14 |
| 30 | 1,073,741,823 | 21,893,107,598,129 | 13 |
| 31 | 2,147,483,647 | 46,240,693,149,101 | 13,877,774 |

The nodes charge `641,718,458,944,739,251,563` operations of row D in all (13,878,251 calls; the sizes `j` with no call on the normal sequence have no row); the aligned split and the node give row D = `2,737,780,934,045,384,314,781`.

### 4.5 Products longer than `3 * 2^32` points (block mode)

The bullets of earlier entries on the coefficient-domain stage C are not repeated: stage C is 4.6, which uses this section only for the Newton reciprocal and the q product of its step 1. Stage D uses 4.4.1 item 6.

At this r the transforms of 4.3 and 4.4 would have up to `3 * 2^55` points (the square of stage C, `2m - 1 = 59,604,644,775,390,623` coefficients) and `3 * 2^54` points (`m + 1`, the products by `g`, and the products by the half-gcd matrices, whose entries have several blocks). The field has no root of unity of such an order (`p - 1 = 2^32 * 3 * q'`). Grok (xAI), job 140, determined the cost of multiplying polynomials of lengths `3 * 2^34`, `3 * 2^36` and `3 * 2^38` over this field and recommends the block NTT (its scheme (a)) for `3 * 2^34` and `3 * 2^36` and the same split with an outer transform across the blocks (its scheme (b), the outer FFT) for `3 * 2^38`: a product is cut into blocks, the blocks are transformed with the longest available transform, and the products of block spectra are summed in the transform domain. Grok job 140 checked both schemes against schoolbook on random products of length `2^14` with a transform cap of `2^10` (every coefficient equal, and the counted multiplications and additions equal to its formulas, `551,999` and `890,850` for scheme (a)). Both schemes are the same operations at every block count; at the lengths of this r we apply them by the charging rules of 4.2. The schemes, as used by the algorithm:

* Blocks. `B = 3 * 2^31` coefficients per block, transform size `NB = 2B = 3 * 2^32 = 12,884,901,888` (the plan of the largest transform of 4.3, with its kernels and charges). An operand of `l` coefficients has `ceil(l / B)` blocks; each block is zero-padded to `NB` points and transformed once (forward: the radix-3 stage and three rows of radix-2 passes). A product of two blocks has at most `2B - 1 < NB` coefficients, so a block product does not wrap.
* Scheme (a), slots. The slot `s` of a product `A C` is the sum of the block products `A_i C_j` with `i + j = s`; it is formed pointwise in the transform domain (`NB` multiplications per pair, additions or subtractions for the further pairs), inverse transformed once, and placed at offset `s B` of the output: a loop with a load, the multiplication by `1/NB` (and the sign), a store, and for the coefficients that overlap the previous slot a load of the output value and an addition (a subtraction when the placement subtracts into an array). Only the slots that meet the wanted window of the product are formed. The windows are those of 4.3: the Newton products use `[0, l2)`; the quotient `q` of a step is the window `[m - 2, 2m - 3)` of `T1 * MU`; the remainder uses the window `[0, m)` of `q g`.
* Scheme (b), outer transform (the scheme from which (c) below is derived; it is not used at this r). Let `ns` be the number of slots of the product, `[s0, s1]` the slots that meet the window, and `n2` the smallest `2^a` or `3 * 2^a` that is at least `max(s1 + 2, ns + 1 - s0)` (it divides `3 * 2^32`, so the roots exist). For every position `t < B` the `n2` values of the blocks of an operand at that position (zero beyond its last block) are transformed with the `n2`-point transform across the blocks (twiddles: powers of a primitive `n2`-th root of unity); this gives, for each of the `n2` outer points `o`, a polynomial of `B` coefficients, which is transformed with the block transform (`NB` points). For each outer point the spectra are multiplied pointwise (and summed over the products of the bilinear form), the result is inverse transformed, and its upper part (positions `B ..`) is multiplied by the `o`-th power of the outer root and added to the lower part (the fold). The inverse `n2`-point transform across the outer points returns, for each position `t`, the coefficients of the pieces of the product; the cyclic wrap of length `n2` does not reach the pieces of the window. The window is placed with the scaling `1/NB` and `1/n2`. Price of the outer transform (exact, from its kernels): a transform of `n2` points at each of the `B` positions of a block is a twiddle table of `n2` entries (3 operations each), `n2/3` calls of the radix-3 kernel `ob3` when `3` divides `n2`, and `n2/2` calls of the radix-2 kernel `ob2` in each of the `log2` radix-2 layers; a call of `ob3` is charged `7 + 25 B` and a call of `ob2` `5 + 14 B` (every load, store, field operation and loop step of the kernel text in `ntt_kern.h`, parsed like every other kernel), plus 10 for the call (block addresses, twiddle address, call and return). The charges are integers; nothing is averaged or truncated.
* Forms. The form of an operand of `l` coefficients is what a product multiplies pointwise. In scheme (a) it is the `ceil(l / B)` block spectra of `NB` points each (`ceil(l / B) * NB` elements). In scheme (b), when `l > B`, it is the `n2` outer-domain arrays of `B` elements each (`n2 * B` elements): the blocks are copied into one array of `n2` blocks, zero beyond the last block (the copy is charged, `7 l + 2` operations, and so is the zero fill of the other `n2 B - l` positions, `5 (n2 B - l) + 2` operations, because the form is taken from the pool, whose memory holds the data of earlier arrays), and transformed across the blocks; when `l <= B` the form is the one spectrum of `NB` points. A form is made from the coefficient array of the operand and charged as in 4.2 (each block transform, or the copy and the outer transform); the coefficient array is freed as soon as the form exists whenever the operand is not needed again. In scheme (b) the inner transform of an outer point is made when that point is multiplied, into a working array of `NB` points, and the output of an outer point overwrites a dead operand array of that point (a further outer-domain array is allocated only if the product has more outputs than operand forms of more than one block). The working arrays of a product are allocated at its start and freed at its end: in scheme (a) one accumulator of `NB` elements; in scheme (b) one array of `NB` elements for each operand and each output of the product.
* Stage D, products above one block. The entries of the half-gcd matrices and the operands `a`, `b` of `apply_inv` have several blocks at the top levels of the recursion. `apply_inv` forms `c = r22 a - r12 b` and `d = r11 b - r21 a`, a bilinear form with two outputs, each the sum of two products. The forms of the four entries are made first; when the matrix is not needed again, the coefficient array of an entry is freed as soon as it is transformed. The blocks of `a` and `b` are transformed one at a time as the slots advance and pass through a sliding window of `kR + 1` blocks for each of the two operands (`kR` is the largest number of blocks of an entry): a slot meets at most `kR` consecutive blocks of an operand, and the block after the slot is transformed before the slot is placed; a block that leaves the window is freed, and every block is transformed once, as the cost counts it. The slots are formed in order, each with the accumulator, inverse transformed and placed. The outputs `c` and `d` are written over `a` and `b` when those arrays belong to the node and have `nres` elements (the placement of slot `s` writes the blocks `s` and `s + 1` of the output, which are already transformed), otherwise into arrays of `nres` elements of their own. In scheme (b) the forms of the four entries and of `a` and `b` (outer-domain arrays; the outputs of the outer points overwrite the forms of `a` and `b`) and the working arrays are held together while the outer points are multiplied, and then freed; the outputs are written over `a` and `b` or into arrays of their own as above. The exact `c` and `d` have fewer than `nres` coefficients (the high coefficients cancel, 4.4), so slots that start at or beyond `nres` are not formed. The matrix product (`mat_mul`) of the half-gcd is the same bilinear form with four outputs, each the sum of two products. The forms of one factor are held whole and those of the other factor one row (or column) at a time, in whichever of the two orders holds fewer blocks, and each row forms its two outputs into arrays of their own length; the coefficient arrays of both factors are freed as soon as they are transformed. In scheme (b) the forms of all eight entries and the working arrays are held together while the outer points are multiplied; the four outputs are allocated when the operand arrays that are dead have been freed. The Newton division (`divrem_fast`) holds, besides the arrays of its caller, the arrays of the normal sequence (the Newton division is not run on it, 4.4.1 item 4) and the forms and working arrays of its largest block product, in the scheme in which that product is charged. All other products of stage D, and the Newton products below `3 * 2^32` points, are as in 4.3 and 4.4.
* Scheme (c), chunked outer transform (`P` chunks). The outer length `n2` is the one of scheme (b) (the smallest `2^a` or `3 * 2^a` that is at least `max(s1 + 2, ns + 1 - s0)`). If `P` divides `n2` and `Q = n2 / P` is of the form `2^a` or `3 * 2^a`, the outer points `o = j1 + P * j2` (`0 <= j1 < P`, `0 <= j2 < Q`) are handled in `P` chunks, chunk `j1` holding the `Q` points with that `j1`; otherwise the product uses one chunk (`P = 1`). The operands stay in coefficient form: nothing is copied into an outer-domain array. Let `w` be a primitive `n2`-th root of unity and `x_i` the blocks of an operand (`k` of them, `B` positions each; zero beyond `k`). Chunk `j1` is assembled from the blocks: for every `i2 < Q` the array `z_(i2) = sum over i = i2 + Q i1 < k of w^(i j1) x_i`, by one call of the kernel `ocp` (`z = c x`, charge `5 + 8 B`) for the first block of the sum and one call of `oax` (`z += c x`, `5 + 11 B`) for each further block (the last block over its own positions only), the weight `c` being the entry `(i j1) mod n2` of a table of the `n2 + 1` powers of `w` (3 operations per entry, built at the start of the product), and by one call of `ozf` (`z = 0`, `3 + 5 B`) for an `i2` that no block reaches, and for the positions of the last block's array beyond the last coefficient when that block starts its array (the chunk arrays are taken from the pool, whose memory holds the data of earlier arrays); each call is charged `30` more (the two block addresses, the exponent `i j1 mod n2` with the reduction, the table address, call and return). The `Q` arrays are then transformed with the `Q`-point transform across the arrays (root `w^P`; the twiddle table of `Q` entries at 3 operations each, `Q/3` calls of `ob3` when 3 divides `Q`, `Q/2` calls of `ob2` in each radix-2 layer; `ob3` is charged `7 + 25 B`, `ob2` `5 + 14 B`, plus 10 per call), after which array `j2` is `sum over i of w^(i (j1 + P j2)) x_i`, the outer-domain array of the point `o = j1 + P j2`. From there each point is treated as in the outer-transform scheme: the inner transform (`NB` points) of the arrays of its operands (made at every use, charged for every point of every operand of more than one block, including the persistent operands `MU` and `g` of stage C), the pointwise products, the inverse inner transform and the fold of the upper `B` positions with the `o`-th power of `w`. The `Q` folded arrays of the chunk are transformed back with the `Q`-point transform (root `w^(-P)`), and for every output piece `s` of the window (`s = s0 .. min(s1, ns - 1) + 1`, the `tc` pieces) the piece is accumulated, `acc_s += w^(-j1 s) U_(s mod Q)`, by one call of `ocp` in the first chunk and `oax` in the others (charged `1` more per call: the weight is the table entry `n2 - ((j1 s) mod n2)`). The sum over the chunks is the piece `s` multiplied by `n2`; the factor `1/n2` is applied by the placement. A product that is the quotient estimate, the remainder or a stage-C step computes its pieces into accumulators of `tc B` elements and places them into the destination afterwards; a product of a division (6.3) accumulates the pieces of the window directly into the output array of the division, so that it has no accumulator (the calls then run only over the positions of the window). Because the operands are in coefficient form for the whole product, every operand array and every chunk form is charged where it is used; no spectrum or outer-domain form is stored between products.
* Choice. At this r stage C uses `P = 4` chunks (stage D: 4.4.1, item 6): each block product uses scheme (a) or scheme (c), whichever has the smaller charge, as a function of the lengths and the window only; scheme (b) is not used. The number of chunks is a constant of the algorithm for each r, fixed before the run; it was chosen by comparing the scores of the ledger at these pairs (stage C, stage D): (4, 16). The pair used has the least score of them.
* Stage D in scheme (c). `apply_inv`: the coefficient arrays of the four entries, of `a` and of `b` stay live while the chunks are processed; the arrays of a chunk are the chunk forms of the six operands, the working arrays, the tables and two accumulators (`c` and `d`). After the last chunk the entries are freed when the matrix is not needed again; `c` and `d` are placed over `a` and `b` when those arrays belong to the node and have `nres` elements, otherwise into arrays of `nres` elements of their own; the accumulators are freed. `mat_mul`: the arrays of both factors stay live during the chunks (chunk forms of the eight entries, working arrays, tables, four accumulators); after the last chunk both factors are freed and the four outputs are placed into arrays of their own length, each accumulator being freed after its output is placed. Divisions: the arrays of 6.3, and the chunk forms, working arrays and tables of the largest block product of the division, the product accumulating its pieces directly into the output array of the division the arrays of the normal sequence (the Newton division is not run on it, 4.4.1 item 4), so that the division has no accumulator.
* Memory in scheme (c). A chunk form is `Q = n2 / P` arrays of `B` elements, so a product holds `Q B` elements for each operand of more than one block (and for each output beyond the number of such operands), where scheme (b) holds `n2 B`; the coefficient arrays of the operands and the accumulators are the other arrays of the product. The memory walk of section 7 allocates and frees every array named here.
* Scaling (coefficient-domain stage C and the products of 4.5; for stage D see 4.4.1 item 6, where the scale is applied at the untwist). The factor `NB` of the unnormalised inverse transform is removed in the placement (one multiplication per coefficient placed); the stored reciprocal `MU` and the polynomial `g` are not rescaled.
* Memory. The arena of section 7 is computed by running the allocator of 4.2 on the allocations and frees of every array named in this section, in the order of the program (a block is `64 + 32 * slots` bytes rounded up to a multiple of 64; the temporary arrays of one call are allocated in the order of the walk and freed in the reverse order). For the products in scheme (c) the arrays are those of the two bullets on scheme (c) above. Stage C, products in scheme (a): the twiddle table, `g` and `F`; in the Newton iteration also `MU`, `Y` and the forms and working arrays of the product in progress; in the loop `F` and the persistent forms of `MU` and `g` (`g` itself is freed) and, in a step, the form of `R` (then of `T1`, then of `q`), `T1` (then `q`) and the working arrays of the product in progress, in a shift by `x` the work array of the regeneration of `g`; at the end `g` is regenerated while the persistent form of `g` is still live. Stage D: the arrays of the nodes of the half-gcd, with in `apply_inv` and `mat_mul` the forms, the window and the working arrays described above, and in a division the quotient of two coefficients and the remainder only (6.3: on the normal sequence every quotient has degree 1, so the Newton division never runs). The truncated second call of a node reads the top coefficients of `d` and `e` in place (no array); the second `apply_inv` at the calls of the Euclid driver and the two copies of the returned remainders are counted with the node. In scheme (b) a form is `n2` outer-domain arrays of `B` elements, so the scheme holds `n2 * B` elements for each operand of more than one block. The twiddle table is the one of the transform of `3 * 2^32` points (`2^31` elements, `ntt_init(32)`).
* Cost. The charges are those of 4.2 applied to these operations: each block transform and each inverse transform with the kernels and pass structure of the transform of `3 * 2^32` points, each pointwise product `NB` times the per-point charge of the bilinear form of 4.4, each placement as stated above.

The three kernels of scheme (c), from `ntt_kern.h` (`LD(n)` and `ST(n)` are charged `2 n` operations, `CTL(n)` `n`, `fp_mul` and `fp_add` one each; the source counts `5 + 7 cnt`, `5 + 10 cnt` and `3 + 4 cnt`; this entry charges the loop step of each position 3, by the loop rule of 4.2, so the charges are `5 + 8 cnt`, `5 + 11 cnt` and `3 + 5 cnt`, as in the text above, and likewise `ob3` and `ob2` one more per position than their source):

```c
static void ocp(fp *z, const fp *x, const fp *w, size_t cnt) {
    fp u; fp wr = *w; LD(1); CTL(3);              /* weight into a register; entry, loop set-up and exit */
    for (size_t grp = 0; grp < cnt; grp++) {
        u = x[grp]; LD(1); fp_mul(&u, &u, &wr);
        z[grp] = u; ST(1); CTL(2);
    }
}
static void oax(fp *z, const fp *x, const fp *w, size_t cnt) {
    fp u, v; fp wr = *w; LD(1); CTL(3);
    for (size_t grp = 0; grp < cnt; grp++) {
        u = x[grp]; LD(1); v = z[grp]; LD(1); fp_mul(&u, &u, &wr); fp_add(&v, &v, &u);
        z[grp] = v; ST(1); CTL(2);
    }
}
static void ozf(fp *z, size_t cnt) {
    fp zr = {{0, 0, 0, 0}}; CTL(3);
    for (size_t grp = 0; grp < cnt; grp++) {
        z[grp] = zr; ST(1); CTL(2);
    }
}
```

### 4.6 Stage C in the value domain (this entry; the method of bradcush 1aa56884, its proof section 4.6)

In this entry stage C is not the coefficient-domain squaring of 4.3 and 4.5: it is the value-domain powering of bradcush's entry 1aa56884 (proof section 4.6 there, credited in the submission note), re-implemented and charged in this entry's cost model. The residue is held by its values on two sets of `n1` points. One modular squaring is a Montgomery reduction whose only non-pointwise work is two changes of point set (extensions). No product of polynomials, no `MU` and no quotient is formed in the loop. Sections 4.3 and 4.5 still define the transforms, the kernels and the Newton reciprocal that the set-up below uses.

**Points.** Here `h = 2^32` and `K` is the number of cosets of each point set (not the number of centres of 4.1). `H` is the subgroup of order `h` of `F_p^*`, with generator `omega = 5^((p-1)/h)`, which has order `h` because 5 is a non-square. Put `u_k = 5^k`, `C_k = u_k H` and `n_k = u_k^h = z^k` with `z = 5^h`. `p - 1 = 2^32 * 3 * 463 * q1 * q2` with `q1 = 539,204,044,132,271,846,773` prime, and `z^((p-1)/q1) != 1`, so the order of `z` is at least `q1 > 2K`. Hence the nodes `z^k` (`k < 2K`) are distinct and the cosets `C_k` are pairwise disjoint (`C_j = C_k` if and only if `z^(k-j) = 1`). Our script `zorder_check.py` (standard library) checks these three facts: `q1` is prime by a deterministic Miller-Rabin test with the bases up to 41 (valid for `n < 3.3 * 10^24`), `z^((p-1)/q1) != 1`, and `5^((p-1)/2) != 1`; all three hold. At r = 18: `m = 29,802,322,387,695,312`, `K = ceil((m + 1)/h) = 6,938,894`, `n1 = K h = 29,802,322,800,410,624 = m + 412,715,312`. Put `O1 = C_0 u ... u C_(K-1)` and `O2 = C_K u ... u C_(2K-1)`, `M(Y) = prod_(k<K) (Y - z^k)` and `P1(X) = M(X^h)`. `P1` has degree `n1`, is squarefree, has root set exactly `O1`, and on a coset `C_k` with `k >= K` it is the nonzero constant `M(n_k)`.

**Representation.** A polynomial `f` of degree `< n1` is determined by its values on `O1`, and also by its values on `O2`. Write `f = sum_(j<h) X^j F_j(X^h)` with `deg F_j < K`. Then `f mod (X^h - n_k) = sum_j F_j(n_k) X^j`, so the values of `f` on `C_k` are the transform of size `h` of `(u_k^j F_j(n_k))_j`. Each array holds the values coset by coset, in the output order of the inner transform. The inner transforms of the cosets of an array are made together, as column passes across the cosets (position = coset, stride `h`): column passes of at most seven layers for the 32 layers, split by least charge (4.2), in place on the array.

**Lemma 4.6 (the step).** Let `g` be monic of degree `m` with `g(x) != 0` on `O1`. Let `R~` have degree `<= m`, and let `u0` be the polynomial of degree `< n1` with `u0(x) = -R~(x)^2 / g(x)` on `O1`. Then `W = (R~^2 + u0 g) / P1` is a polynomial of degree `<= m - 1`, and `W = R~^2 P1^(-1) mod g`. On `C_k` with `k >= K`, its values are `(R~(x)^2 + u0(x) g(x)) / M(n_k)`. *Proof.* `R~^2 + u0 g` vanishes on the `n1` distinct roots of the squarefree `P1`, so `P1` divides it. Its degree is at most `max(2m, n1 - 1 + m) = n1 + m - 1` because `n1 >= m + 1`, so `deg W <= m - 1`. Modulo `g`, `W P1 = R~^2`, and `P1` is invertible modulo `g` because `g` has no root in `O1`. The values follow from `P1(x) = M(n_k)` on `C_k`. QED. So the invariant `R~_i = S^(e_i) P1 mod g` passes from step to step with `R~' = X^b W` (`e_(i+1) = 2 e_i + b`, `deg R~' <= m`). The same argument with `R~` in place of `R~^2` leaves the Montgomery form (step 7).

**Lemma 4.7 (extension).** Let `f` have degree `< n1`, with its values on `O1` given. The inverse inner transform of each coset gives `h u_k^j F_j(n_k)`. Fix a position `j`, write `F = F_j`, and put `s_i = F(z^i) z^(-i) / M'(z^i)` and `kappa(e) = 1/(z^e - 1)` for `1 <= e <= 2K - 1`. Then `F(z^(K+t)) = M(z^(K+t)) sum_(i<K) s_i kappa(K + t - i)` for `t < K`. *Proof.* `deg F < K`, so `F` is the Lagrange interpolant of its values at the `K` distinct nodes, and `z^(K+t) - z^i = z^i (z^(K+t-i) - 1)` with `1 <= K + t - i <= 2K - 1`. QED. The direction `O2 -> O1` is the same with the nodes `z^(K+i)`. The sum is a cyclic convolution of length `Lx = 2^24 >= 2K` with a fixed kernel, and no index wraps.

**The stage** (the eight steps of 1aa56884, with our parameters at r = 18). The exponent `E = (p-1)/2` starts from `S^v` with `v = 2^52`, a multiple of `h` below `m` (`VSHIFT = 2`: two more squaring steps and a shorter reciprocal), and runs `201` steps, `45` of them with `b = 1`.
1. *Barrett start:* the reciprocal of the reversed `g` modulo `X^ell`, `ell = 4,503,600,040,085,809`, by the Newton iteration of 4.3 with the products of 4.5. Then `q = floor(X^v P1 / g)` by one product (`Kq = 1,048,577` rows).
2. *`g` on `O1` and on `O2`* by the chirp evaluation of section 3 (one convolution of length `Le = 3 * 2^23 >= 3K - 1` per position) and `2K` forward inner transforms.
3. *`R~_0` on `O2`:* `q` evaluated at the nodes of `O2` (`Lq = 2^23`), then `R2 := u_k^v M(n_k) - R2 * G2` pointwise. This gives the values of `X^v P1 - q g = X^v P1 mod g`.
4. *`R~_0` on `O1`:* an extension `O2 -> O1` (lemma 4.7).
5. *`-1/g` on `O1`* by Montgomery's batch inversion per coset in chunks of `2^16` elements (the `2^16`-element batch-inversion prefix of 0xplemonade's entry `ff21bd28`): per chunk the prefix products into one auxiliary array of `2^16` elements (a load, a multiplication, a store), one inversion with its zero test and the backward pass (two loads, two multiplications, the negation, a store), 9 of chunk control; 20 per coset. A zero prefix product means `g` vanishes on `O1`, and the trial ABORTs as in 4.4.1 item 4 (allocator reset, ledger row 'ABORT reset') after a prefix of the charged work; the probability is below `2^-143.5` (9.2(b)).
6. *The loop*, for each bit `b`: `R1 := R1^2 G1` (`u0` on `O1`); the extension `O1 -> O2`; `R2 := x^b (R2^2 + R1 G2) / M(n_k)`; the extension `O2 -> O1`. By lemma 4.6 the invariant holds after every step.
7. *Leaving the Montgomery form:* `R1 := R1 G1`, the extension `O1 -> O2`, `R2 := (R2 + R1 G2) / M(n_k)`. `R2` now holds `R = S^E mod g` (degree `< m`).
8. *Coefficient form for stage D:* `R2` and `g` are interpolated in place (inverse inner transforms, then two chirp correlations of length `Lx` per position), each into two pieces, the coefficients `[0, cut)` and `[cut, l)` with `cut = 22,351,744,247,791,616`, which the top node of stage D frees early (4.4.1, step 5).

**Kernels.** Every column pass of this section, the pruned first and last passes included, runs its position loop eight positions per pass with the control `F(cnt)` per call (4.2), not 3 per position. The inner transforms are column passes across the cosets (4.2). In the loop the last two forward layers, the pointwise step and the first two inverse layers are one column pass per boundary (on the boundary pass of a step with `b = 1`, and per call the four `omega^e` of its rows, each the product of one entry of each of two tables of `2^16` entries, `omega^e = T1[y] T2[x]` for the position `p = x 2^16 + y` with exponent `e = 2^16 rev16(y) + rev16(x)` in the bit-reversed output order of the inner transform, `T1[y] = omega^(2^16 rev16(y))`, `T2[x] = omega^(rev16(x))`: two loads with their addresses and one multiplication per value, 12 more per call than one load per value from a table of `h` entries, the 12 being in the charge of one loop step with `b = 1` below; the two tables are built at `10` per entry), within the 18 words; the extension is computed in a coset-major group buffer with column passes, the first forward pass reading only the `K` input rows and the last inverse pass writing only the rows `K .. 2K - 1` (the register-blocked scheme of 1aa56884, credited).

**Charges** (the components sum to row C of section 6):

| component | operations |
|---|---:|
| inner transforms in the batches of stage C (column passes of 4.2 at `cnt` = the number of cosets; forward / inverse, per point of a coset, without the position-loop control `F(cnt)` of each call) | 60 / 60 |
| geometric phase of one extension (219.465 per element of `n1`) | 6,540,558,949,602,184,906 |
| one extension with its `2K` inner transforms | 10,064,567,511,436,727,308 |
| one loop step, `b = 0` / `b = 1` | 20,309,811,510,898,534,440 / 20,376,866,754,379,327,528 |
| tables: `30 K` constants, the two `omega` tables of `2^16` entries, the kernel spectra | 1,284,458,079,937 |
| Newton reciprocal (step 1, with its allocations) | 33,953,907,809,747,997,852 |
| product for `q` (step 1) | 8,614,488,042,618,583,489 |
| evaluation of `g` (step 2, geometric part) | 11,334,123,996,297,449,160 |
| `2K` forward inner transforms of `g` (step 2) | 3,524,008,401,438,016,431 |
| step 3 | 5,546,655,003,862,426,457 |
| step 4 | 9,935,113,620,501,271,562 |
| step 5 (batch inversion in chunks of `2^16`) | 440,794,344,196,995,680 |
| step 6, the loop: 201 steps (45 with `b = 1`) | 4,085,289,599,647,241,111,400 |
| step 7 | 10,775,166,697,313,257,138 |
| step 8 (two interpolations) | 31,725,148,838,494,704,654 |
| allocations, exponent scan, zero fills, end of stage | 10,200,594,250 |
| stage C of one trial, with the stage bookkeeping of 1,000 (ledger row C) | 4,201,139,007,696,370,489,010 |

The inner transforms are column passes and the geometric phase uses the register-blocked kernels above (the outer-kernel convention of 1aa56884). With the pieces of 4.4.1 every coset access of a row pass (the pointwise passes, the batch inversion, the rows read or written by an extension) also selects the base of its piece (a comparison and a branch, 2 operations), and every column pass splits its coset loop at the piece boundary (4 operations per call); both are included in the figures above. Every charge depends only on `m` and the exponent, not on the coefficients.

**Memory.** The loop holds `R1`, `R2`, `G1` and the array of `g` (which holds `g` on `O2` during the loop and `g` in coefficient form at the exit): four arrays of `n1` elements. It also holds the tables and the group buffer of `VCNT = 2^10` rows of `Lmax = Le = 3 * 2^23` elements (the longest kernel), and one transform row of `Lmax` elements; the tables are the `30 K` constants, the two `omega` tables of `2^16` entries and the kernel spectra, and step 5 adds one array of `2^16` elements. The live peak of stage C is `3.0000` arrays of `n1` above its entry , plus the array of `g` from stage A. Section 7 walks these allocations with the rest of the trial.

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes and compares them; the algorithm outputs only if they are equal and the pairs differ; it never outputs a non-collision. This section is a statement about the output of a successful run, and holds for every coin sequence. It contains no probability.

## 6. Ledger: worst-case operation count (primitive operations; `C(18) = 594`)

Notation: `T_fixed` = init (twiddle table) + setup (the line) + the plan_invN misses + stage H + stage I; `T_trial` = stages A to D of one trial, stage E at its cap, stages F and G, the trial loop and the allocator reset after an ABORT (charged in every trial); `T_off` = the offline derivation of section 6.2, counted exactly (136,785) and charged at its declared cap 1,000,000. The claim is `N_max = T_fixed + K * T_trial + T_off` with `K = 1` (one centre, section 9.2), and `time_log2 = ceil_5(log2(N_max / 594))`.

Every stage is charged by the rules of section 4.2 where it executes. Every trial is charged as if its gcd had degree 0 in stages A to D (the larger case), and in addition with stage E at its cap, stage F at its worst case and stage G.

| row | what is charged | operations |
|---|---|---:|
| init | twiddle table of `2^(32-1)` elements (`ntt_init(32)`: 5 operations per element, loop control, the roots of unity, the inversions of the setup) | 17,179,887,292 |
| setup | the line (`line_setup`) | 4,910 |
| A (per trial) | stage bookkeeping 1,000, loop test and update 5, the coin draw 31, one allocation | 1,382 |
| B (per trial) | (this entry: the inverse transforms and the geometric solve on the column passes of 4.2, the point loop in natural order; Appendix B2) `4625930` cosets of `6,442,450,944` points, each point with two evaluations of `F` (at `c + s` and `c - s`) at the `135 + 12 r = 351` operations of the scaled straight-line program (section 3, Appendix L), the loop work around them, `4625930` inverse transforms of size `6,442,450,944`, the geometric solve of the cosets (two correlations of length `12,582,912` per position), the normalisation | 40,390,833,724,747,331,365 |
| C (per trial) | `S^((p-1)/2) mod g` in the value domain (section 4.6): the Barrett start (Newton reciprocal and the product for `q`), the evaluations of `g` and `q`, the batch inversion, `201` steps (45 with `b = 1`), each two pointwise passes and two extensions, the exit and the two interpolations | 4,201,139,007,696,370,489,010 |
| D (per trial) | half-gcd of `(g, R - 1)` (sections 4.4, 4.4.1, 4.4.2, 4.4.3), charged for the normal remainder sequence with the quotient and return tests; any other sequence ends the trial after a prefix of this work (section 6.3) | 2,737,780,934,045,384,314,781 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16` (below) | 166,079,773 |
| F (per trial) | square root, back-map (below) | 47,012 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 594 + 32` | 12,912 |
| trial loop | the test and increment of the trial counter and the bookkeeping of the trial: at most 12 | 12 |
| ABORT reset (per trial) | the reset of the allocator when a test of stage D (quotient, return or window) or the zero test of stage C (4.6 step 5) fails and the trial ends (section 6.3): the 47 free-list heads (classes 7 to 53), the end of the slab area, the two ends of the pool and the header of its free middle block; at most 1,000, charged in every trial | 1,000 |
| plan_invN misses | one per distinct plan size (57 sizes, 3,089 each) | 176,073 |
| H | canonical encoding of the output (6 conversions, 384 digits) | 5,644 |
| I | output of the answer: formatting (`400 * 8,192`), loops, entry, one `write`, one `exit_group` | 3,384,436 |
| offline | section 6.2: `T_off = 136,785` counted exactly, charged at the declared cap | 1,000,000 |
| **N_max** | `T_fixed + T_trial + T_off` | **6,979,310,775,483,852,735,602** |

Row C is the sum of the charges of section 4.6; row D is the charge of the half-gcd of sections 4.4, 4.4.1, 4.4.2 and 4.4.3 with the products of 4.5, on the normal remainder sequence (6.3).

`N_max = 6,979,310,775,483,852,735,602` operations `= 11,749,681,440,208,506,288.89` units, `log2(N_max / 594) = 63.3492554455`, claimed as `63.34926` (rounded up at five decimals).

Stage B charges each of the `59,604,654,190,755,840` evaluations of `F` at the `135 + 12 * 18 = 351` operations of the scaled straight-line program (section 3, Appendix L), not at the full reference permutation `C(18) = 216 + 21 * 18 = 594`; the loop work around the evaluations is charged on top (section 3). The reduction against `4fd1cd9` is exactly `59,604,654,190,755,840 * (594 - 351) = 14,483,930,968,353,669,120`. This entry: the loop work, the `4625930` inverse transforms and the geometric solve are charged on the column passes of section 4.2 (Appendix B2, where row B is expanded part by part and the counting program is printed): row B `40,390,833,724,747,331,365` (was `86,684,755,546,378,974,541`).

Stage E at its cap. The trial enters stage E only when `1 <= deg G <= DMAX`; stage E opens with 1,000 (stage bookkeeping) and runs a round for each pass of the isolation loop until `deg G = 1` or `Z` rounds have been made. A round at current degree `d` costs `R(d)`: the coin draw 31, the zero test of the shift (5, and at most 2 for the replacement of a zero draw by 1) and one negation; the Taylor shift (`taylor_shift`: two allocations, three loops of `d + 1` steps with their loads, stores and loop control, the schoolbook product of two polynomials of `d + 1` coefficients, two inversions and one exponentiation by `d`); `Z^((p-1)/2) mod G` by schoolbook square-and-multiply (`pow_half`: 253 modular squarings, each `2d + 3 d (d-1)/2 + 2 d^2` field operations and an allocation and a free, and 45 multiplications by `Z`, each `2d` field operations; because the memory-access charge adds 9 operations per field operation, every field operation of `pow_half` is charged 10); two classical gcds (`gcd_cl`: at most `d` outer iterations, each with one inversion charged `2,640` operations (the 330 field operations of `x^(p-2)` and the 2,310 control operations of its bit loop), at most `2d + 1` division steps, each charged at the largest row length); the copies, the tests and the frees. The cap charges every one of the `Z` rounds at `d = DMAX`, because `R(d)` is non-decreasing in `d`: `R(16) = 2,594,979`, of which `pow_half` is 2,471,032, the Taylor shift 11,700 and the two gcds 54,395 each. All allocations are charged at `L <= 16` live blocks (550 per allocation, 105 per free): in stage E the live blocks are the twiddle table, `G`, `S`, `S - 1`, `S + 1` and the two gcd arrays (at most 8), and at most four more inside the Taylor shift or the modular squaring. `E_cap = 1,000 + 3 + 64 * R(16) + 114 = 166,079,773`.

Stage F. After the stage bookkeeping (1,000), 12,000 control operations for the Tonelli-Shanks control and 2 more, the field operations of stage F are charged 10 each (the memory-access charge): the powers by `q` and by `(q+1)/2`, Tonelli-Shanks with parameter `m` falling strictly from 32 (an outer step with parameter `m` costs `m` squarings and 2 multiplications: at most `sum_(m=1)^(32) (m + 2) = 592`), and two back-maps (three fifth-root powers `x^e`, `e = (4(p-1)+1)/5`, two multiplications, two additions, two subtractions each), plus one addition and one subtraction: at most 3,401 field operations, so `F = 13,002 + 10 * 3,401 = 47,012`.

Every figure above is an upper bound that the algorithm meets or exceeds for every coin sequence and every target value (stage D by section 6.3): each loop bound is a constant or a function of `m` only, the trial loop is capped at `K` and tested at the start of each trial, the isolation loop is capped at `Z` rounds of degree at most `DMAX`, and the operations of each stage are counted under the rules of section 4.2.

### 6.2 Offline derivation of the literals (preprocessing)

The literals of the sources are computed once, offline, from `p` and the organizer's 192 round constants and 9 MDS entries, one literal at a time (working set: at most 16 words of 32 bytes and a 64-byte digit buffer); each is the value of one closed formula, with no search and no choice. Count in the primitives of 4.2 (orchard-field-ram-v2: every field operation, load, store and control operation is 1): a field operation is charged 4 (the operation, two operand loads, one store), a 64-bit word operation 3 (the operation, one load, one store), a hexadecimal digit 5 (its load, the table load, a shift, an or, the loop control). (a) Input: 202 values of 64 hexadecimal digits (`p`, the 192 round constants, the 9 MDS entries), 324 each with the 4 word stores: `65,448`. (b) Field literals, 489 field operations: `2 = 1 + 1` (1); `R = 2^256 mod p`, `2` squared 8 times (8); `R^2 mod p` (1); the Montgomery forms `x R mod p` of the 201 organizer constants (201); `2^65 R mod p` (`2` squared 6 times, times `2`, times `R`: 8); `5 = 2 + 2 + 1` (2); `5^t R mod p` with `t = (p-1)/2^32`, the odd part of `p - 1` (the exponent written `q` in the Tonelli-Shanks of stage F; 223 bits, 46 of them 1: 222 squarings, 45 multiplications, times `R`: 268); charged `4 * 489 + 3 * 222` (the bit steps of the square-and-multiply) `= 2,622`. (c) Word literals, 90 word operations: `p - 1` (4), `t` (a shift by 32 over 4 words, 12), `(t+1)/2` (16), `(p-1)/2` (12), `p - 2` (4), `e = (4(p-1)+1)/5` (a shift by 2 into 5 words 15, plus 1, a division by 5 word by word 10: 26), `-p^-1 mod 2^64` (5 Newton steps `x <- x (2 - p_0 x)` from `x = p_0`, 3 each, and a negation: 16); charged `3 * 90 = 270`. (d) Output: 211 literals of 64 hexadecimal digits (the 201 Montgomery forms, `R`, `R^2`, `2^65 R`, `5^t R`, `t`, `(t+1)/2`, `(p-1)/2`, `p - 2`, `e`, `p`), 324 each, and `-p^-1 mod 2^64` (16 digits, 81): `68,445`. `T_off = 65,448 + 2,622 + 270 + 68,445 = 136,785` operations over the 212 literals. The ledger charges the declared cap `1,000,000 >= T_off` (`preprocessing_log2 = 20`, `2^20 = 1,048,576`), inside `N_max`: a counted bound, not a premise. The algorithm uses no other offline result: the line, its minors and the twiddle table are computed at run time and charged in `setup` and `init`. The leading coefficient `f_D(0)` of section 2.3 is a fact used in the proof; the algorithm re-derives it (stage B tests that the leading coefficient of `g_c` is nonzero and normalises by it).

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry e6dcb600)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g_c, R_c - 1)`: every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the re-centering division of a node, the division of each repetition of the outer loop, each step of the base case) tests that its quotient has degree 1 (2 operations); (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); (c) the window test of 4.4.1 item 3 (2 tests, 2 operations each); a zero remainder inside hgcd or in the outer-loop division also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state after the twiddle table (1,000 operations, charged in every trial) and the next centre is drawn. Lemma (prefix; e6dcb600, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each call splits at k1 = ceil(k/2) (at k1 = 2^(b-1) - 1, b the bit length of k, when k < 2^54, 4.4.3) and, with every quotient of degree 1, every degree in the tree is fixed by m and the number of quotients so far and the parameters of the second call and of the outer loop are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's hgcd calls and divisions produce has degree at least 94 (n >= 193), so a gcd of degree at most 94, and so every gcd of degree at most DMAX, first appears in the classical Euclid below degree 192, after a prefix of the degree-0 work. A zero remainder anywhere earlier (gcd degree above 94, a failed trial anyway) ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2(b)). Row D of section 6 is this charge, `2,737,780,934,045,384,314,781`.

## 7. Memory

Five terms make up the memory.

(a) The code and static data of an implementation of the algorithm: 399,216 bytes of code, 32 of initialised data and 4,851,196 of static tables and buffers (the 8,192-byte output buffer and the tables of the stages), and at most 907,520 bytes for the straight-line block bodies of 4.2 (for `k = 1, ..., 7`, forward and inverse: the four-block and one-block bodies and their group-0 variants, at most `10 (2^(k+1) + 3k 2^(k-1) + 3)` instructions of at most 16 bytes each): 6,157,964 bytes; and 32,768 bytes (at most 2,048 instructions of 16 bytes) for the routines of this entry, the apply plans of 4.4.1 item 7, the chunked batch inversion and the two `omega` tables of 4.6 and the pass splits of 4.2: 6,190,732 bytes; and 32,768 bytes (at most 2,048 instructions of 16 bytes) for the routines of the node of 4.4.3, the loop bodies at eight positions per pass of `8 c + 3` instructions for a charge of `c` per position (4.2): the row copy (4) 35, the zero fill (2) 19, the fold-accumulate (7, 8) 59 and 67, the twist (2) 19, the pseudo-division (13) 107, the values of `Q` and of `M1 Q` (25) 203, the 3-row CRT (22) 179, the 2-row CRT (10) 83, the base-case remainder loop (13 and 9 in one body, 22) 179 and its matrix-column loop (22) 179, and the table of the scales 100, 1,229 instructions in all, with its call, arena and test code inside the 2,048: 6,223,500 bytes; and 5,472 bytes for the two row bodies of the node of 4.4.3 (the fold row, `8 * 22 + 3 = 179` instructions, and the two-output row, `8 * 20 + 3 = 163`), 342 instructions of at most 16 bytes: 6,228,972 bytes.

(b) The arena, which serves every array of the largest trial (the heap is inside the memory of the implementation; nothing is requested from the system at run time). Each block has a 64-byte header and a payload rounded up to a multiple of 64 bytes (section 4.2). The arena is the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (the second trial repeats the first from the same state: a trial frees every array but the twiddle table, and the simulation checks that the pool is back to that state). The simulation records every allocation and free of the trial in the order of the program (the twiddle table, stage A, stage B, stage C, stage D; the temporary arrays of one call are allocated in the order of the walk and freed in the reverse order), checks that these events reproduce the live-set walk of every stage (bytes in use, peak, live blocks), and runs the allocator on them. By the prefix lemma of section 6.3 every size in the sequence is a function of `m` and of the shape of the recursion on the normal sequence (and the block counts of the products), so the sequence is the same for every input. The two-ended pool takes the blocks of more than 2^45 bytes and is simulated address by address (two lists in address order, the low one from the bottom and the high one, for the statements marked `# pool:H`, from the top; the first free block that fits on the request's side is cut from the side nearest its end; a free merges with its free neighbours and with the unused middle); its capacity is the largest sum of the extents of the two ends over the trial, `3,814,697,318,452,560,256` bytes (after stage C `3,814,697,318,452,560,256`, after stage D `3,814,697,318,452,560,256`), plus 128 bytes so that the unused middle is always at least 128 bytes. The live-set peak of the same sequence is `3,814,698,222,768,355,136` bytes and the arena is `1.00030` times it: the blocks that die first are taken from the top and the long-lived ones from the bottom, so the holes left by freed blocks are small. The slab classes take the blocks of at most 2^45 bytes (a block of at most `2^j` bytes gets a slot of `2^j` bytes; the free list of the class first, else a new slot from the end of the slab area), so the slab area is the sum over the classes of the peak number of live blocks of the class times `2^j`: `1,158,060,621,917,824` bytes. Stages E to I hold at most 16 live arrays of at most 17 elements (16 slots of 1,024 bytes), and the allocator keeps 47 free-list heads (classes 7 to 53) and the end of the slab area (48 words, 384 bytes): `16,896` bytes with a margin of 128. The arena is `3,815,855,379,074,495,104` bytes (the three terms, rounded up to 64 bytes), in the stage with the highest pool address, D. The peaks of the live set per stage (twiddle table, `g`, `F` and the live set of the stage; the arena above is larger): A 953,674,398,332,616,896; B 1,907,348,865,384,710,400; C 3,814,698,222,768,355,136; D 3,626,090,790,072,992,512; stage E and the later stages hold the twiddle table and a few arrays of at most 17 elements. The walk of stage D is the walk of the normal remainder sequence (6.3) with the pieces and windows of 4.4.1, its apply plans (item 7: six arrays of `N` elements and the outputs per plan) and 4.4.3: every array of stage D has the length the normal sequence gives it, and a trial with any other sequence ends (ABORT) after a prefix of these allocations, so the walk bounds every trial. The largest transform has `3 * 2^32` points and uses roots of unity of order 3 and `2^32` (`p - 1` is divisible by 3 and by `2^32`); products that would need a longer transform are computed by blocks (section 4.5). The largest buffers are those of stage C (section 4.6: `R1`, `R2`, `G1` and the array of `g`, `n1 = 29,802,322,800,410,624` elements each, the tables and the group buffer; the Newton phase of its set-up holds three arrays of `ell` elements and the forms of one product) and those of stage D (4.4, 4.4.1; the single-transform products of 4.4.2 allocate the rows of the form they use, and the sequence above contains them); the arrays of 4.4.3 (the table of 31 scales, the four matrix arrays of `2^j + 1` words and the node arena of at most `34,359,738,112` words of each matrix-only call) are blocks of at most `2^41` bytes, below the pool threshold `2^45`, and are inside the slab area above.

(c) A stack bound of 65,536 bytes.

(d) The register file of the machine of claim.json: one file of 387 words (256 field registers and 131 integer address registers), each counted as a 256-bit word, 12,384 bytes.

(e) The working set of the offline derivation of section 6.2: 16 words of 32 bytes and the 64-byte digit buffer, 576 bytes.

(f) This entry's stage-B solve buffers (Appendix B2), allocated in stage B and freed at its end: the group buffer of `1,024 * 12,582,912` elements, the two kernel spectra of `12,582,912` elements, the two tables of `4625930` constants and three arrays of `1,024` slot words, each counted as a slab slot of its own (64-byte header, payload rounded up to the power of two): `551,366,623,232` bytes, added on top of the footprint below (an upper bound: the stage-B live set of the base, at most two arrays of `n` elements, is unchanged). With it the footprint is `3,815,855,930,447,425,804` bytes `= 2^61.7267124`, claimed as `memory_log2_bytes = 61.72672`. The base package's total follows. Total: (a) + (b) + (c) + (d) + (e) = `3,815,855,379,080,802,572` bytes `= 2^61.72671`, claimed as `memory_log2_bytes = 61.72672` (rounded up at five decimals). The rows of section 6 and this arena are generated by our counting program: it adds the charges of 4.2 over every call of the algorithm of section 4 in program order and runs the allocator of 4.2 on the same allocation sequence; each term is the closed formula stated in sections 4 and 6, and the program is not attached. The memory penalty is `max(0, 61.72672 - 20) = 41.72672`. The offline derivation of section 6.2 is a closed formula per constant; its working set is term (e). The algorithm has no stored advice and no precomputed data beyond the constants of section 6.2; the twiddle table is built at run time and charged in stage "init".

## 9. Success probability and the premises `H-ONE` and `H-NORMAL`

### 9.1 The premise `H-ONE`

Notation. `p` is the Pallas prime, `D = 5^24`, and `F` is the fixed polynomial of section 2.3 at r = 18 (degree `D`, leading coefficient `f_D(0) != 0`). `g_c` is the monic odd part about the centre `c` (section 3, degree `m = 29,802,322,387,695,312`), and `G(c, t) = (F(c + t) - F(c - t)) / (2 t) = g_c(t^2)`. For `c` in `F_p`, let `k(c)` be the number of nonzero squares `S` with `g_c(S) = 0`; this is `deg G_c` of section 3, the degree of `gcd(g_c, S^((p-1)/2) - 1)`. `E_c` is the event `1 <= k(c) <= DMAX` (`DMAX = 16`) under which stage E runs.

**Premise `H-ONE`.** The number of centres `c` in `F_p` with `1 <= k(c) <= 16` is at least `0.3931 p`. Equivalently, for `c` uniform on `F_p`, `P(E_c) >= q = 0.3931`.

Four fields (as in claim.json). **Statement:** the premise above. **Role:** score-critical. **Scope:** the fixed target `poseidon-orchard-r18-prefix-v1`, this line construction (the line `j = 0` of the first two rounds, section 2) and the polynomial `F` of section 2.3, with centres uniform on `F_p`. Nothing is claimed for other round counts. **Limitations:**
- The premise concerns this `F`, not every polynomial of degree `D`. It is false for permutation polynomials: every pure composition of maps `x -> a x^5 + b` is bijective and has `k = 0` at every centre. It is also false for a decomposable `F` with imprimitive monodromy (the axis line of 10.3, Theorem C).
- It is false at one layer (`F_1`, `m = 2`: the law of 9.3(a) gives exactly 0.375) and true at two and three layers (9.3(c)).
- The value `0.3931` is `0.3934693 - 0.3931 = 0.0003693` below the value `1 - e^(-1/2) = 0.3934693` of the law of 9.3(a), and `0.0001292` below the four-moment Bonferroni bound `151/384 = 0.3932292` (9.3(b)). With `delta = 0.001` (9.5) and `P(E_c) >= 0.3931` the bound of 9.2 is `0.392099999999997615` at `K = 1`.

What the premise does not contain: no random-polynomial model; no independence of centres (one centre is drawn); no statement about the remainder sequences (that is `H-NORMAL`, 9.5); and nothing about the cost.

### 9.2 The success bound with one centre

(a) *Centre.* The centre is one draw (4.1.1) and lies within statistical distance `2^-128.9` of uniform on `F_p`; over the at most 65 words of the run the distance is `eps_coin < 2^-122` (4.1.1), which the bound subtracts. So `P(E_c) >= q - eps_coin` for the drawn centre.

(b) *The ABORT of stage D and the zero test of stage C.* Let `N_c` be the event that the remainder sequence of `(g_c, R_c - 1)` is normal down to its gcd: `deg(R_c - 1) = m - 1` and every quotient of degree 1 (section 6.3). By the premise `H-NORMAL` (9.5), `P(not N_c) <= delta = 0.001` for `c` uniform.

Let `Z_c` be the event that `g_c` vanishes at a point of the set `O1` of the value-domain stage C; its zero test (section 4.6) ends the trial. For each of the `n1` points `x` of `O1`, `g_c(x)` (before normalisation) is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so it has at most `D - 1` roots. Each residue is drawn with probability at most `4/2^256` (4.1.1). Hence `P(Z_c) <= delta_C = n1 (D - 1) 4 / 2^256 = 6.136e-44 (2^-143.5)`, proved, no premise.

If `E_c` and `N_c` hold and `Z_c` does not, stages C and D run to their end and return `G = gcd(g_c, R_c - 1)`.

(c) *Isolation.* If `E_c` holds, stage E fails with probability at most `eps_iso = 2.371e-15 (2^-48.58) < 2^-48`, over words that are fresh for that stage (lemma 9.4): each round, whatever came before, halves the degree with probability at least `w = 1/2 - 7.869e-40` (the `(p-3)/2` shifts that separate two roots, 4.1.1 weights), four halvings take `deg G <= 16` to 1, so the failure probability is at most `P[Bin(64, w) <= 3] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = 2.371e-15`. Proved, no premise.

(d) *The bound.* A trial with `E_c`, `N_c`, not `Z_c`, and a successful isolation ends in a verified collision (sections 2-5). For `c` uniform, `P(E_c and N_c and not Z_c) >= q - delta - delta_C`. So, with `K = 1`,

`P[success] >= 1 - (1 - q + delta + delta_C)^K - K (eps_coin + eps_iso) = q - delta - delta_C - eps_coin - eps_iso = 0.392099999999997615 >= 0.39209`

with `q = 0.3931`, `delta = 0.001` and `K = 1`. This is the form of bradcush's entry 1aa56884 (9.2(f) there) at `K = 1`. The bound stays at least 0.39 for every `delta <= 0.0030999` at `q = 0.3931`, and for every pair with `q - delta >= 0.390000000000002345`. The probability is over the random words of 4.1.1 for the fixed target. It is not a probability over targets and not a sampled frequency, and no run of this algorithm at r = 18 enters it.

(e) *Why one centre needs `H-ONE`.* Two moments of `k` cannot give 0.39 with one centre. The law of 9.3(a) has the exact values `E[k] = 1/2` and `E[k(k-1)] = 1/4`, and the sharp lower bound on `P(k >= 1)` over all laws with these moments is `3/8 = 0.375`: the law `P(0) = 5/8`, `P(1) = 1/4`, `P(2) = 1/8` attains it. With three moments the bound is still 0.375. This is why entries built on two moments (our earlier premise `H-GEOM-w1`, and gta6rp's linear two-moment bound) use two centres. One centre needs a statement about the event itself, or four moments (9.3(b)).

### 9.3 Where the number comes from (support of `H-ONE`; not used in the bound)

(a) *The law.* The roots of `G(c, t)` in `t` are `+-t_1, ..., +-t_m`, where `u_i = t_i^2` are the roots of `g_c`. So the Galois group `Gamma` of the cover `G(c, t) = 0` of the `c`-line acts by signed permutations: `Gamma` is a subgroup of the hyperoctahedral group `B_m` (10.3, Grok job 137). For a centre off the branch locus, `k(c)` is the number of positive fixed points of the Frobenius element: the indices `i` with `t_i` in `F_p`.

For a uniform element of `B_m`, the binomial moments of this number are `E[C(k, j)] = 2^-j / j!` for `j <= m`, so `P(k >= 1) = 1 - sum_(j <= m) (-1/2)^j / j!`. This is 0.375 at `m = 2`, 0.3958 at `m = 3`, 0.3932 at `m = 4`, and 0.3934693403 for every `m >= 12`: the Poisson(1/2) value `1 - e^(-1/2)`. The tail is negligible: `P(k > 16) < 2.3e-20`. With Chebotarev's theorem (Frobenius elements equidistributed in `Gamma`), this law is the frequency over the centres.

(b) *Moments and counts.* `E[C(k, j)] = N_j / (2^j j! p)`, where `N_j` is the number of points `(c, t_1, ..., t_j)` over `F_p` with `G(c, t_i) = 0`, `t_i != 0` and `t_a^2 != t_b^2` (for `j = 1, 2` these are the counts `N*` and `N_off` of our earlier premise `H-GEOM-w1`).

For every integer `k >= 1`, `sum_(j=1..4) (-1)^(j+1) C(k, j) = 1 - C(k-1, 4)`. This is 1 for `k <= 5` and at most 0 for `k >= 6`, and the sum is 0 at `k = 0`. So `1_(1 <= k <= DMAX) >= k - C(k, 2) + C(k, 3) - C(k, 4)` for every integer `k >= 0`, and `P(E_c) >= S_1 - S_2 + S_3 - S_4` (Bonferroni at order 4). With the moments of (a) this is `151/384 = 0.3932292`.

Hence `H-ONE` follows from four count statements, `N_1 >= (1 - eps) p`, `N_2 <= (1 + eps) p`, `N_3 >= (1 - eps) p` and `N_4 <= (1 + eps) p`, with `eps <= 0.0032835`. The premise is stated as the weaker statement `H-ONE` itself.

(c) *A theorem at two and three layers.* Let `F_N` be the truncation of 10.3: the first `N` S-box layers, degree `5^N`. On the deployed constants and the algorithm's line, 10.3 gives the arithmetic monodromy `Gamma = B_12` at `N = 2` and `Gamma = B_62` at `N = 3` (`pi(Gamma) = S_m`, `K = F_2^m`).

The geometric monodromy is normal in `Gamma` with a cyclic quotient. It therefore contains the commutator subgroup `{(eps, pi) : pi in A_m, prod eps = 1}` of `B_m`. That subgroup acts transitively on ordered `j`-tuples of signed distinct indices for `j <= m - 2`: `A_m` is `(m-2)`-transitive, and a free sign fixes the parity.

So for `j <= 8` the curve counted by `N_j` is absolutely irreducible, a complete intersection of degree at most `(5^N - 1)^j`. The Aubry-Perret bound gives `N_j = p (1 + rho_j)` with `|rho_j| <= (5^N - 1)^(2j) p^(-1/2)`: below `2^-53` at `N = 2` and below `2^-15` at `N = 3` (`j <= 8`).

The Bonferroni bounds of orders 7 and 8 then give `0.39346933 <= P(E_c) <= 0.39346944` for `F_2` and for `F_3`. At these depths `H-ONE` is a theorem, with margin 0.000369.

 At `N = 4`, the cycle types `(312)` and `(311,1)` of 10.3 make `pi(Gamma)` 2-transitive of degree 312. The only such groups are `A_312`, `S_312`, and the groups between `PSL(2,311)` and `PGL(2,311)`, whose non-identity elements fix at most two points. Centres with `k(c) = 3` and `k(c) = 4` occur (our runs, 10.5.1), and the 312-cycle is odd, so `pi(Gamma) = S_312`. The sign kernel at `N = 4` is not computed.

(d) *Measured.*
-  Toy fields, exact over all centres: deployed constants reduced modulo `p = 1,048,627` and six random-constant seeds, 3 to 8 S-box layers, partial rounds included, 27 cases. `P(k >= 1)` lies between 0.39214 and 0.39436; the largest deviation from 0.3934693 is 0.00133, that is `1.36 / sqrt(p)`.
- The real field: the organizer-run tests of 10.5.1 and 10.5.2 and our runs, reproducible observations at `m = 12` and `62`; no probability bound is drawn from them.

(e) *The extrapolation.* At `N = 24` neither the monodromy nor the counts can be computed. Weil's bound exceeds `p` for `j >= 2` (relative error `2^95.9` at `j = 2`).

The premise states that this `F` stays within `0.0003693` of the law of (a) (`q = 0.3931 <= 151/384 = 0.3932292`): no structure appears between the third layer and the 24-th that changes the law of the positive fixed points by 0.1%.

The measured deviations shrink like `p^(-1/2)` and do not grow with the degree. On the toy fields the deviation is `1.36 / sqrt(p)` . The counts of Grok job 139 give `eps ~ 3.1 / sqrt(p)` over degrees 5 to 1,953,125 (10.3).

### 9.4 Lemma (isolation), proved

**Lemma.** Let `G` be monic of degree `d` with `2 <= d <= DMAX`, a product of `d` distinct linear factors over `F_p`. In one round of 4.1.2 (`a` is a coin draw, with 0 replaced by 1), with probability at least `w = (4 (p-3)/2 - S3)/2^256 = 1/2 - 7.869e-40` (`S3` of 4.1.1) both `G_+` and `G_-` are nonconstant, and then the kept part has degree at most `floor(d/2)`. The degree never increases. Hence after `Z` rounds the probability that `deg G >= 2` remains is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1]`, which for `DMAX = 16`, `Z = 64` equals at most 2.371e-15 (2^-48.58) (the exact sum below).

*Proof.* Let `u != v` be two roots of `G`, `chi` the quadratic character on `F_p`. In a round the roots of the shifted `G` are `r + a`. If `a` is not `-u`, not `-v`, and `chi(u+a) != chi(v+a)`, then exactly one of `u+a`, `v+a` is a nonzero square and the other a nonsquare; so `(u+a)^((p-1)/2) = 1` for one and `-1` for the other, one root lies in `G_+` and the other in `G_-` (a root of the shifted `G` is a root of `Z^((p-1)/2) - 1` iff its character is `+1`, of `Z^((p-1)/2) + 1` iff it is `-1`). Both parts are then nonconstant, their degrees sum to at most `d`, and the smaller has degree at most `floor(d/2)`. The number of `a` with `chi(u+a) chi(v+a) = -1`: `sum_(a != -u,-v) chi((a+u)(a+v)) = -1`, because the quadratic `a^2 + (u+v) a + uv` has nonzero discriminant `(u-v)^2` (the standard evaluation of a quadratic character sum), so the count of `a` outside `{-u,-v}` with product `-1` is `((p-2) + 1)/2 = (p-1)/2`, at least `(p-3)/2` of them nonzero. Every residue is taken by the draw with probability `3/2^256` or `4/2^256`, and `4/2^256` for all but `S3` of them (4.1.1), so the `(p-3)/2` nonzero values of `a` listed have together probability at least `(4 (p-3)/2 - S3)/2^256 = w` (a zero draw is replaced by 1, which only adds probability). A part is always a divisor of `G`, so the degree is nonincreasing whatever happens in a round that is not of this kind. Conditional on any history of earlier rounds, the next `a` is made of fresh random words, so every round is of this kind with probability at least `w`, and at most `ceil(log2 DMAX)` such rounds bring `d <= DMAX` to 1 (16 -> 8 -> 4 -> 2 -> 1). The failure probability is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = 2.371e-15 (2^-48.58)`. This is a proved bound under the random words, not a premise and not a sample.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries e6dcb600 and 1aa56884, with the form of the allowance and the organizer-run tests of gta6rp's entry 3876eb92)

**Premise `H-NORMAL`.** For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(g_c, R_c - 1)`, where `g_c` is the monic odd part of section 3 (degree `m = 29,802,322,387,695,312`) and `R_c = S^((p-1)/2) mod g_c`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.001` (`2^-9.966`).

Four fields (as in claim.json). **Role:** score-critical for the success probability only. The time and memory bounds hold for every sequence: stage D is charged for the normal sequence, every division tests its quotient and every call its return, and on any other case the trial ends after a prefix of the charged work (6.3). **Scope:** the pairs `(g_c, R_c - 1)` of the target `poseidon-orchard-r18-prefix-v1`, `c` uniform on `F_p`; nothing is claimed for other round counts. **Extrapolation and evidence:** for a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes; each is a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-143.5`. That bound does not transfer directly, because the coefficients of `R_c` have degree about `p` in those of `g_c`; the premise asserts far less than random-pair behaviour, an abnormality probability of at most `delta = 0.001`, which is all the bound of 9.2(d) uses (every `delta <= 0.0030999` keeps it at least 0.39). Measured support, organizer-run (10.5.1): the experiments `euclid-normal-n2-t256-l2-a` to `-l2-f` compute the complete sequence of `(g_c, R_c - 1)` for this construction on the truncation `F_2` of the digest polynomial (10.3; `m = 12`) at 512 organizer-seeded centres each (3,072 sequences), and return a witness pair exactly when both sequences of a trial are normal; `euclid-normal-n3-t24` and `euclid-normal-n4-t2` compute it at `m = 62` and `m = 312` for the first 24 and the first 2 organizer-seeded centres. Zero abnormal in the computed sequences is a reproducible observation consistent with the premise; the organizer-seeded centres are not treated as independent unselected samples and no population bound is drawn from them (`delta = 0.001` is the declared premise, carried by the support stated here). Our runs of an earlier version of the program (its normality computation): 1,066 sequences at `m = 12`, `62` and `312`, every quotient of degree 1 (10.5.1). Reported by our earlier entries, not organizer-run (10.5): the complete sequences on the sibling targets with `r' = 0` and `r' = 1` partial rounds (`m = 7,812` and `39,062`), every quotient of degree 1 in all 10 runs. **Limitations:** the organizer-run tests reach `m = 312` (the sibling runs `m = 39,062`), far below `m = 29,802,322,387,695,312`. Normality is computed inside the submitted program; the runner checks only the returned witness pairs, so the tests are evidence under trusted execution of that program, which is printed in full in `experiments/exp_euclid.py`.

## 10. Evidence

This section is the evidence for the premise `H-ONE` and for the digest of the target. The computations of 10.3 are ours; the experiments of 10.2 are run by the organizer's runner. None of it enters `success_probability` or the bound of section 9, and none is a lower bound on the probability of `E_c`.

### 10.2 The organizer experiments declared in `experiments/manifest.json`

Sixteen experiments of kind `python-message-pairs-v1` (five here, eleven in 10.5.1 and 10.5.2), run by the organizer's own experiment runner (the Orchard digest of the target is called by the runner). The three Python sources are 58,143 bytes together (the limit for experiment sources is 65,536).

(a) `lowbits-birthday` (`experiments/exp_lowbits.py`, kind `python-message-pairs-v1`, event `digest-xor-mask` with mask `fffc` followed by 30 zero bytes and expected value zero). For each organizer trial the program searches at most 1200 fresh inputs derived from the trial seed for two distinct canonical messages whose digests of the selected target `poseidon-orchard-r18-prefix-v1` agree in the first 14 bits of the big-endian reading, and returns the pair (or two nulls). Its source is 15,748 bytes (the limit for experiment sources is 65,536). Its event is a reduced one on the digest of the selected target: the program computes its candidates with its own copy of the permutation (constants embedded), and a returned pair counts only if the organizer's callback gives digests that agree in those 14 bits, so a pair is accepted only when that copy agrees with the target. The digest map so checked is the map whose line polynomial `F` the premise concerns.

The experiment is run by the organizer's own experiment runner (python-message-pairs-v1, the Orchard digest called by the runner), and the intake report of that run is the evidence: 256 of 256 trials returned a verified pair at r = 18, and the output was byte-identical on repetition. Our own earlier local run of the same events (plain Python on our machine) agreed: 256 of 256 trials.

(b) `line-ladder-w6`, `line-ladder-w8`, `line-ladder-w10`, `line-ladder-w12` (`experiments/exp_line.py`, event `digest-xor-mask` on the first 6, 8, 10 and 12 bits of the digest, expected value zero). The program is the line construction of section 2 for the target at r = 18: it builds the line `j = 0` of the first two rounds (the point `Q`, the direction `(a, b)`, the vectors `alpha` and `beta`), evaluates `F(W)` as the remaining twenty-four rounds applied to `alpha + beta W` (`deg F = 5^24`), and maps a point `W` back to the canonical pair `(nk, rho)` with the inverse S-box `x -> x^e` of 2.1 and 2.2. For each organizer trial it takes a centre `c` from the trial seed, scans the antipodal pairs `W = c + s`, `W = c - s` for `s = 1, ..., 150`, and at the first pair whose digests agree on the masked bits it maps both points back, checks both messages against the full permutation inside the program and returns them (else two nulls). A returned pair counts only when the runner's own digest of the two canonical messages agrees on those bits, so each counted trial is a pair of antipodal points of the line construction whose digests `F(c+s)` and `F(c-s)` agree at width `w`: the reduced-width form of the event `F(c+s) = F(c-s)` that the premise `H-ONE` is about (a root of `g_c`). The count of returned pairs at each width is a reproducible observation of the construction's own antipodal pairs on the target; no probability, rate or population bound is drawn from it (public organizer seeds; nothing is assumed about the seeded trials being independent or identically distributed), and it does not enter section 9.

The intake report of the organizer's run records 238, 119, 32, 8 of the 256 trials with a verified pair for `w` = 6, 8, 10, 12 respectively, and byte-identical output on repetition. 

### 10.3 Computed theorems and computations for the generic line (Grok, jobs 135 and 136)

Grok (xAI), our research partner, computed the hypotheses (a) and (b) of this section exactly over the Pallas field for a toy permutation, by exact computation (the cycle types, factorisations and leading coefficients below are the printed results): width 3, S-box `x -> x^5`, `M = [[2,1,1],[1,2,1],[1,1,2]]` (every minor nonzero mod `p`), round `i` adds the constants `(3i+1, 3i+2, 3i+3)`, every round full, output coordinate 0, on the generic line `(L, 2L+1, 3L+5)`. Notation as in 9.1: `D = deg F`, `G(c,t) = (F(c+t) - F(c-t))/(2t) = H(c, t^2)`, `m = (D-1)/2`; the cycle types below are those of `H(c, u)` (or of `F(x) - a`) at the stated values over `F_p`, which by Dedekind give elements of the arithmetic monodromy.

* **Theorem A (one full round).** `D = 5`. The curve `G = 0` is absolutely irreducible (`F'` has 4 simple roots, so `u` is not a square in the function field); the cycle types of `F(x) - a` at `a = 8, 1, 5` are `(5)`, `(4,1)`, `(2,1,1,1)`, so the arithmetic monodromy is `S_5`. The pair scheme `G(c,s1) = G(c,s2) = 0` is geometrically reduced and of pure dimension 1, and its part off `s1^2 = s2^2` has exactly one absolutely irreducible component defined over `F_p`: the resultant in `c` of `G(c,s1)` and `G(c,s2)` is a constant times `(s1-s2)^4 (s1+s2)^4 Phi(s1,s2)` with `Phi` of degree 8, and `Phi` is irreducible at specialisations of `s1` over `F_(p^k)` for `k = 2, 4, 8`, hence absolutely irreducible. So the hypothesis holds with `w = 1`, with no further assumption.
* **Theorem B (two full rounds).** `D = 25`, `deg H = 12`. The cycle types of `H(c,u)` at `c = 1, 9, 103` are `(12)`, `(11,1)`, `(7,1,1,1,1,1)`; a 12-cycle, an 11-cycle and a 7-cycle (7 is prime and at most 12 - 3) give, by Jordan's theorem, `A_12` inside the arithmetic monodromy, and the 12-cycle is odd, so it is `S_12`; the geometric monodromy is `A_12` or `S_12`, both 2-transitive. Hence `G = 0` is absolutely irreducible, the pair scheme is geometrically reduced of pure dimension 1, and the off-diagonal scheme `{H(c,u1) = H(c,u2) = 0, u1 != u2}` in the coordinates `(c, u1, u2)` is absolutely irreducible.
* **Theorem D (degrees).** For every `N <= 17` rounds and every listed line and schedule, the output coordinate has degree exactly `5^N` over `F_p` (the leading coefficient is an integer, nonzero mod `p`). This is the fact of section 2.3 (`deg F = D`) for the toy.
* The axis line `(L, 0, 0)` is a different case (Theorem C): there `F = R(X + c0)^5` is decomposable, its geometric monodromy is imprimitive, and the hypothesis fails (`w = 0`). The theorems above are for the generic line.

Our line is generic in this sense. The polynomial that the construction of section 2 produces is dense: in our miniature runs (`p` of 20 and of 24 bits, `r` up to 4, run twice with identical digests of the coefficient vectors) every coefficient of the digest polynomial in `W` is nonzero up to the 0 to 2 zeros expected of a random polynomial, each residue of the exponent modulo 5 and modulo 25 carries its fair share, and the polynomial `g` that the algorithm builds is dense likewise. This is evidence for `H-ONE` at one and two rounds on a generic line, with the group-theoretic certificate (an `m`-cycle, an `(m-1)`-cycle and a prime cycle of length at most `m - 3`) that proves it for any further explicit `F` it is computed for.

**Grok job 136 (first N full rounds, Orchard parameter tuple, generic line) and its re-run on the deployed constants.** Grok (xAI) computed the hypotheses (a) and (b) of this section exactly over the Pallas field for the Orchard tuple (width 3, S-box `x -> x^5`, `R_F = 8`, `R_P = 56`) and the generic line `(L, 2L+1, 3L+5)`, for the first `N = 1, 2, 3, 4` full rounds, with the round constants and MDS produced by the Hadeshash Grain generator and the same group-theoretic certificate as in Theorems A and B. Results: degree exactly `5^N` with a nonzero leading coefficient; `F'` has `5^N - 1` simple roots; (a) `G = 0` is absolutely irreducible and (b) the pair scheme is geometrically reduced of pure dimension 1 at `N = 1, 2, 3, 4`; `w = 1` at `N = 1` (the cofactor `Phi` of degree 8 of the eliminant is absolutely irreducible); at `N = 2` and `N = 3` the arithmetic monodromy of `H` is `S_12` and `S_62` (cycle types `(12)`, `(11,1)`, `(7,1^5)` at `c = 11, 10, 457` and `(62)`, `(61,1)`, `(59,1^3)` at `c = 57, 60, 152`), so the off-diagonal `u`-scheme is absolutely irreducible; at `N = 4` the cycle types `(312)` at `c = 349` and `(311,1)` at `c = 56` give a transitive, 2-transitive monodromy, which gives (a) and (b).

The Grain output differs from the deployed table (the organizer constants that `experiments/exp_line.py` embeds and that the runner's digest uses), so we ran the same program, unchanged, on the deployed constants and on the algorithm's own line: `F_N` is coordinate 0 after the first `N` S-box layers of the digest polynomial of section 2.3 (start state `alpha + beta W`; layers = rounds 2 and 3, full, then the partial rounds 4 and 5), so `F_N` has degree `5^N` and is the truncation of the polynomial `F` of the premise (`N = 24`; the line and the first layers do not depend on r). The results:

| N | layers of `F_N` | `deg F_N` | `m` | cycle types of `H(c,u)` found (value of `c`) | (a), (b) | `w` / off-diagonal scheme | monodromy of `H` |
|--:|---|--:|--:|---|:-:|---|---|
| 1 | round 2 | 5 | 2 | (2) at 3, (1,1) at 1 | yes | `w = 1` (`Phi` of degree 8 absolutely irreducible: irreducible of full degree over `F_(p^k)`, `k` = 2, 4, 8) | `S_2` |
| 2 | rounds 2, 3 | 25 | 12 | (12) at 8, (11,1) at 18, (7,1^5) at 1644 | yes | off-diagonal scheme absolutely irreducible | `S_12` |
| 3 | rounds 2, 3, 4 | 125 | 62 | (62) at 82, (61,1) at 24, (59,1^3) at 622 | yes | off-diagonal scheme absolutely irreducible | `S_62` |
| 4 | rounds 2, 3, 4, 5 | 625 | 312 | (312) at 121, (311,1) at 357 | yes | not computed | transitive and 2-transitive |

For every row the spot check of `F_N` against direct iteration of the rounds passed, the leading coefficient of `F_N` equals the one propagated through the layers (section 2.3), `F_N'` has `5^N - 1` simple roots, and `H(c,0) = F_N'(c)` at `c` = 1, 2, 5, 17. The cycle types are those of the square-free specialisations of `H(c,u)` at the stated `c`; for `N = 1` the discriminant of `H` is not a square (odd-exponent factors of degrees 2 and 2), and for `N = 4` the Jordan prime cycle `(307,1^5)` was not met in 929 specialisations (expected count 0.025), so the single-component statement is not made at `N = 4`.

So (a) and (b) hold for `F_N` at `N = 1, 2, 3, 4` on the deployed constants and the algorithm's line, `w = 1` at `N = 1`, and the monodromy of `H` is `S_m` at `N = 2` and `N = 3`. The premise `H-ONE` (9.1) extrapolates the measured trend (`w = 1` at `N = 1, 2, 3` on the deployed constants, below) to `N = 24`.
Under (a) and 2-transitivity of the monodromy of H, w is 1 or 2 (Grok job 137, lemma: with the arithmetic monodromy Gamma inside the hyperoctahedral group B_m, K = Gamma meet F_2^m is one of 0, <1>, E, F_2^m once pi(Gamma) contains A_m, and w = 1 exactly when K contains the even-weight subspace E, w = 2 otherwise; the witnesses of Grok job 136 establish the hypotheses). Measured on the deployed Orchard constants and the algorithm's own line (the F_N of proof.md 10.3, using the Frobenius cycle types of H(c, u) and their lifts to G(c, t) = H(c, t^2) over F_p): N = 1 gives K = F_2^2 and w = 1; N = 2 (m = 12) gives K = F_2^12 and w = 1, witnessed by the 12-cycle specialisations c = 8 (two 12-cycles on G, omega = 0) and c = 24 (one 24-cycle, omega = 1) and the even permutation c = 6; N = 3 (m = 62) gives K = F_2^62 and w = 1, witnessed by the 62-cycle specialisations c = 82 (omega = 0) and c = 102 (omega = 1) and the even permutation c = 1. So w = 1 at N = 1, 2, 3 on the deployed constants, a measured trend, and the lemma gives w = 1 or w = 2 given (a) and 2-transitivity.

**Grok job 139 (the counts of the premise on toy copies).** Grok (xAI) computed `N*` and `N_off` exactly for width-3 Hades toy permutations over prime fields `p < 2^22` with `p mod 5 != 1` (S-box `x -> x^5`, uniformly random MDS matrix and round constants, the line `(L, 2L+1, 3L+5)`, `N` full rounds and `k` partial rounds, `deg F = 5^(N+k)` up to 1,953,125), by the fibre counts `N* = sum_y m_y (m_y - 1)` and `N_off = sum_c 4 r(c) (r(c) - 1)` (checked against brute force on the small cases), on 1,316 generic seeds with `p >= 1024` (the five degenerate seeds, where the degree drops, are excluded). The relative error `eps_obs = max(|N*/p - 1|, |N_off/p - w|/w)` with `w = 1` is `<= 0.2197` for every generic seed with `p >= 2053`, and the least-squares fit is `eps_obs = 3.10 / sqrt(p)` for a typical seed (`5.17 / sqrt(p)` for the maximum of four seeds), with no dependence on the degree (adding a term linear in `deg F` moves `R^2` from 0.5508 to 0.5509; the mean of `eps sqrt(p)` is 2.3 to 3.7 for every degree from 5 to 1,953,125); at `p = 2,097,169` the largest generic `eps_obs` is 0.0068. These counts support the premise of 9.1: the deviations shrink like `3 / sqrt(p)` and do not grow with the degree.

### 10.5 Euclidean sequences on the sibling targets

The algorithm of section 4 at `r = 18` applies the Euclidean algorithm to `g_c` (degree `m = 29,802,322,387,695,312`) and `R - 1`, `R = S^((p-1)/2) mod g_c`. This section and 10.5.1 are the measured support of the premise `H-NORMAL` (9.5): stage D is charged for the normal remainder sequence and a trial ends at the first quotient of degree other than 1 (6.3). The digest polynomial of the same family at `r' = 0` and `r' = 1` partial rounds (same constants, same line `j = 0`, `F` of degree `5^6 = 15,625` and `5^7 = 78,125`, `m = 7,812` and `39,062`) is small enough to run the stage in full with `python-flint`: for each centre `c` we built `F(c + x)`, its odd part `g_c`, `R` by powering and the complete Euclidean sequence of `(g_c, R - 1)`. Results (centres `c` = 1, ..., 8 at `r' = 0` and `c` = 1, 2 at `r' = 1`): every quotient had degree 1 in all 10 runs, the sequences ended at the gcd (degree 0, or degree 1 at the r' = 0 centres 2, 4, 7) after `m - deg gcd` divisions, and at `r' = 0` the gcd had degree 1 (a usable root, a collision of the sibling target) at the centres 2, 4 and 7. Each `r' = 0` run takes about 20 s and each `r' = 1` run about 6 minutes on one core.

At `r = 18` the stages need about 3815855379 GB and 7.0e+21 operations, which the organizer sandbox (128 MiB, 20 s) does not host; the counts at this `r` are the formula counts of sections 6 and 7.

### 10.5.1 Organizer-run tests: normality (`experiments/exp_euclid.py`)

Eleven experiments of kind `python-message-pairs-v1`, declared in `experiments/manifest.json` and run by the organizer's runner (program `experiments/exp_euclid.py`, 25,241 bytes, Python standard library only, the program of our accepted r = 9 entry `5b96dbb5`): the normality tests `euclid-normal-n2-t256-l2-a` to `-l2-f` (two centres per trial, `m = 12`, 512 sequences each, 3,072 in all) and `euclid-normal-n3-t24` and `euclid-normal-n4-t2` (one centre per trial, `m = 62` and `312`), and the good-centre tests `euclid-gcdpos-n2-t256-a`, `-b` and `euclid-gcdpos-n3-t24` of 10.5.2. The design follows gta6rp's organizer-run normality tests (entry 3876eb92, its 10.5.1); the program is our own. For each computed trial the program takes a centre `c` from the trial seed (the rule of `exp_line.py`) and builds, exactly over `F_p`, the polynomial `F_N(c + X)`: the `F_N` of 10.3 (start state `alpha + beta W` of the line `j = 0`, the S-box layers of rounds 2 and 3 (full), then 4 and 5 (partial, coordinate 0), the MDS after each; degree `5^N`). It checks `F_N` against direct iteration of those layers at `c + 1`, `c - 1`, `c + 2`, `c - 2` and the odd-part identity `2 x g(x^2) = F_N(c + x) - F_N(c - x)` at `x = 1, 2`; takes the monic odd part `g` (degree `m = (5^N - 1)/2`); computes `R = X^((p-1)/2) mod g` (253 squarings and 45 multiplications by `X`); and runs the complete Euclidean sequence of `(g, R - 1)` down to the zero remainder, recording the degree of every quotient. The sequence is normal when `deg(R - 1) = m - 1` and every quotient has degree 1, the condition of 6.3 and 9.5. A normality trial whose sequences are all normal and pass the self-checks, or a good-centre trial with `deg G >= 1` (10.5.2), returns two distinct canonical messages: the points `c + s` of the line, `s = 1, 2, ...`, are mapped back to `(nk, rho)` as in 10.2(b), and the first two whose digests of the selected target agree on the first 6 bits of the big-endian reading are returned. Among 65 points such a pair always exists, so a computed normal trial always returns a pair. Every other trial, and every trial past the first `T` (`T` = 256 in each `-l2` test, 24 and 2 in the other normality tests and 256, 256, 24 in the good-centre tests, the sandbox budget of 20 s), returns two nulls. The organizer-checked count of returned pairs therefore equals the number of computed trials that pass. The per-trial counts listed in the manifest are reported as observations, which the runner labels untrusted. Expected: every computed sequence is normal in the normality tests. No probability, rate or population bound is drawn from any of these organizer-seeded trials (public seeds; nothing is assumed about the trials being independent or identically distributed), and none enters section 9. We do not treat the organizer-seeded centres as independent unselected samples and draw no population bound from these runs: `delta = 0.001` and `q = 0.3931` are the declared premises (9.1, 9.5), carried by their stated support, not by an interval computed from the experiments. For `N <= 4` the polynomial `F_N` is the same at every round count `r >= 2` (its layers come before the final full rounds), so the tests measure the same family of pairs as the premise; only the witness uses the digest at r = 18.

Our runs of this program on seeds of our own (2026-10-21): 512 sequences at `m = 12` in each of the six `-l2` tests (3,072), 24 at `m = 62` and 2 at `m = 312` in the eight normality tests, all normal. What these tests show: under trusted execution, the construction's own pairs `(g_c, R_c - 1)` have normal remainder sequences at `m = 12` to `312`. What they do not show: anything at `m = 29,802,322,387,695,312`, where `H-NORMAL` remains a premise that asserts only `delta = 0.001`.

### 10.5.2 Organizer-counted good centres (premise `H-ONE`; `experiments/exp_euclid.py`)

`euclid-gcdpos-n2-t256-a`, `-b` and `euclid-gcdpos-n3-t24` take one organizer-seeded centre per trial at `N = 2, 3` (`m = 12, 62`; all 256 and the first 24 trials), compute `G = gcd(g_c, R_c - 1)` (`deg G = k(c)`, the number of usable roots) and return a witness pair ONLY when `deg G >= 1` and the self-checks pass, so the organizer's returned-pair count is the good-centre count. Expected: the fraction of good centres is the law of 9.3, a theorem at these depths; the returned counts are reproducible observations consistent with it, and no probability, rate or population bound is drawn from them (public organizer seeds; nothing is assumed about the seeded trials being independent or identically distributed). The step from `N = 2, 3` to the depth of the claim is the premise `H-ONE` (9.1), not an organizer-verified proof. Our runs of these three entries on seeds of our own (2026-10-21): 106 and 100 of 256, 12 of 24.


## Appendix L: the scaled straight-line program of stage B (`135 + 12 r = 351` operations at r = 18)

Stage B (section 3) evaluates the line digest `F(W)` by the scaled straight-line program below, not by the full
reference permutation `C(18) = 594`. It is the `135 + 12 r` form of the r = 56 entries `3a1b25b6` (newjordan),
`9fb982e8` (pierce403) and `69e14209` (Jbenisek), re-derived here from the organizer constants for r = 18; the
same refinement `mpjunior92` applied to stage B in the accepted r = 3 entry `1ac48175` and r = 20 entry `ac52b89`.

Structure and operation count (`ADD` = canonical field addition/subtraction, `MUL` = canonical field
multiplication, each one primitive operation, `1/C` of a unit):

* entry (lanes 1, 2 enter as one `ADD` each): 2 `ADD`;
* round 2 (full): S-boxes `9 MUL`, linear layer with the round-3 constants `6 MUL + 9 ADD`: 24;
* round 3 (full): S-boxes `9 MUL`, into the partial form `6 MUL + 6 ADD`: 21;
* 18 partial rounds (the sparse form of Grassi, Khovratovich, Rechberger, Roy, Schofnegger, USENIX Security 2021,
  with scaled lanes; the hidden pair rotated so its matrix is diagonal at the exit): 12 operations each: 216;
* exit: 3 `ADD`;
* rounds 60, 61, 62 (full): `9 MUL` S-boxes + `6 MUL` + `9 ADD` each: 72;
* round 63 (full): `9 MUL` S-boxes, output lane 0 only, `2 MUL + 2 ADD`: 13.

Sum `2 + 24 + 21 + 216 + 3 + 72 + 13 = 135 + 12 * 18 = 351` (139 `ADD`, 212 `MUL`). A lane may be held as its true
value divided by a known nonzero constant; a scaled S-box gives `(true)^5 = scale^5 (held)^5` and `scale^5` is folded
into the next linear layer, so `L(W) = F(W) / OUTSCALE` for a fixed nonzero `OUTSCALE`. The interpolated polynomial
of section 3 is then `g_c / OUTSCALE`, and the normalisation to monic removes the factor; the collision criterion of
section 2.4 is unchanged.

Verification. The program was built from the organizer constants by our own standard-library code and checked:
the first two rounds are affine in `W` on the line `j = 0` (checked at 8 random `W`), the message map is injective on
the samples, and `OUTSCALE * L(W) = digest(message(W))` of the reference Orchard Poseidon rounds (the deployed
constants and MDS, 8 full + 18 partial rounds) at 200 random `W`. The 351-operation listing
(`op dest, src1, src2`; `k<n>` are the step constants, `e1`, `e2` the entry registers of lanes 1, 2, `x` the line
variable `W`):

```
ADD y1, x, e1
ADD y2, x, e2
MUL s_z0, x, x
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, x
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k0
MUL t2, z2, k1
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k2
MUL t1, z1, k3
MUL t2, z2, k4
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k5
MUL t1, z1, k6
MUL t2, z2, k7
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k8
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k9
MUL t2, z2, k10
ADD h0, z0, t1
ADD h0, h0, t2
MUL t1, z1, k11
MUL t2, z2, k12
ADD h1, z0, t1
ADD h1, h1, t2
MUL t1, z1, k13
MUL t2, z2, k14
ADD h2, z0, t1
ADD h2, h2, t2
ADD u, h0, k15
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k16
MUL t2, h2, k17
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k18
ADD h1, h1, t1
MUL t2, x5, k19
ADD h2, h2, t2
ADD u, h0, k20
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k21
MUL t2, h2, k22
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k23
ADD h1, h1, t1
MUL t2, x5, k24
ADD h2, h2, t2
ADD u, h0, k25
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k26
MUL t2, h2, k27
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k28
ADD h1, h1, t1
MUL t2, x5, k29
ADD h2, h2, t2
ADD u, h0, k30
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k31
MUL t2, h2, k32
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k33
ADD h1, h1, t1
MUL t2, x5, k34
ADD h2, h2, t2
ADD u, h0, k35
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k36
MUL t2, h2, k37
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k38
ADD h1, h1, t1
MUL t2, x5, k39
ADD h2, h2, t2
ADD u, h0, k40
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k41
MUL t2, h2, k42
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k43
ADD h1, h1, t1
MUL t2, x5, k44
ADD h2, h2, t2
ADD u, h0, k45
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k46
MUL t2, h2, k47
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k48
ADD h1, h1, t1
MUL t2, x5, k49
ADD h2, h2, t2
ADD u, h0, k50
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k51
MUL t2, h2, k52
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k53
ADD h1, h1, t1
MUL t2, x5, k54
ADD h2, h2, t2
ADD u, h0, k55
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k56
MUL t2, h2, k57
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k58
ADD h1, h1, t1
MUL t2, x5, k59
ADD h2, h2, t2
ADD u, h0, k60
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k61
MUL t2, h2, k62
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k63
ADD h1, h1, t1
MUL t2, x5, k64
ADD h2, h2, t2
ADD u, h0, k65
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k66
MUL t2, h2, k67
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k68
ADD h1, h1, t1
MUL t2, x5, k69
ADD h2, h2, t2
ADD u, h0, k70
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k71
MUL t2, h2, k72
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k73
ADD h1, h1, t1
MUL t2, x5, k74
ADD h2, h2, t2
ADD u, h0, k75
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k76
MUL t2, h2, k77
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k78
ADD h1, h1, t1
MUL t2, x5, k79
ADD h2, h2, t2
ADD u, h0, k80
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k81
MUL t2, h2, k82
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k83
ADD h1, h1, t1
MUL t2, x5, k84
ADD h2, h2, t2
ADD u, h0, k85
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k86
MUL t2, h2, k87
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k88
ADD h1, h1, t1
MUL t2, x5, k89
ADD h2, h2, t2
ADD u, h0, k90
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k91
MUL t2, h2, k92
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k93
ADD h1, h1, t1
MUL t2, x5, k94
ADD h2, h2, t2
ADD u, h0, k95
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k96
MUL t2, h2, k97
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k98
ADD h1, h1, t1
MUL t2, x5, k99
ADD h2, h2, t2
ADD u, h0, k100
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k101
MUL t2, h2, k102
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k103
ADD h1, h1, t1
MUL t2, x5, k104
ADD h2, h2, t2
ADD y0, h0, k105
ADD y1, h1, k106
ADD y2, h2, k107
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k108
MUL t2, z2, k109
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k110
MUL t1, z1, k111
MUL t2, z2, k112
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k113
MUL t1, z1, k114
MUL t2, z2, k115
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k116
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k117
MUL t2, z2, k118
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k119
MUL t1, z1, k120
MUL t2, z2, k121
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k122
MUL t1, z1, k123
MUL t2, z2, k124
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k125
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k126
MUL t2, z2, k127
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k128
MUL t1, z1, k129
MUL t2, z2, k130
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k131
MUL t1, z1, k132
MUL t2, z2, k133
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k134
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k135
MUL t2, z2, k136
ADD x, z0, t1
ADD x, x, t2
```

## Appendix B2: stage B on column passes (this entry)

This appendix replaces the charge of row B of `ab6b989a`; it changes how stage B is executed and charged, not what it computes. The output of stage B (the monic `g_c` in coefficient form, section 3), every other row of section 6, the arena of stages C and D, the premises `H-ONE` and `H-NORMAL`, the success bound and the experiments are unchanged.

**B2.1 What changes.** In the base package the `kappa` inverse transforms of size `B` and the four transforms of length `S` per position `j` of the geometric solve were charged butterfly by butterfly at the model's generic pass cost, and the point loop formed a bit-reversed store index for every point. Here every one of these transforms runs on the column passes that section 4.2 defines for stage C (a pass of `k <= 7` radix-2 layers over `2^k` rows at `cnt` positions with its `2^k - 1` twiddles in registers, charged `2 nb + 6` for the call, the kernel constant, the per-position charge times `cnt`, `F(cnt)`, and 3 per call plus 2 per loop for the loop of the calls; `ob3` for the radix-3 stage; the layers of a run split by least charge). Nothing is pruned (zero rows are transformed) and no twiddle-1 saving is taken, so the figures are upper bounds for these passes.

**B2.2 The stage, step by step** (notation of section 3; `B = 6,442,450,944`, `S` the smallest `2^a` or `3 * 2^a` with `S >= 2 kappa - 1`).

1. *Point loop* (natural order). For each coset `k < kappa` and `i < B`: `s = v_k zeta^i` and `1/(2s) = (2 v_k)^(-1) zeta^(-i)` by two running products, `x = c' + s`, `x' = c' - s` (`c' = c + E0_0`, formed once), the two evaluations of the program `L` of Appendix L (351 operations each), `y = (L(x) - L(x')) * (1/(2s))`, and one store of `y` at address `i * kappa + k` of the value array (coset-minor layout) with its address operation; per point `2 * 351 + 11` (2 additions, 1 subtraction, 3 multiplications, the store and its address 2, loop control 3), per coset 20.
2. *Inverse transforms.* The `kappa` inverse transforms of size `B` are made together, in place, as column passes across the cosets: the positions of a pass are the `kappa` cosets (contiguous in the coset-minor layout), its rows the transform index. Decimation in frequency: the input is in natural order and the output in the transform's order, so slot `sigma` of a coset then holds `w_k[j]` for the coefficient position `j = pi(sigma)`, `pi` the fixed digit-reversal permutation of the Good-Thomas layout (radix-3 stage and three rows of 31 radix-2 layers). The factor `1/B` is folded into `c_k` below.
3. *Solve*, in `B / 1,024` groups of 1,024 consecutive slots, in a group buffer of `S` rows of 1,024 positions (row = index of the correlation, position = slot). Per slot the position `j = pi(sigma)` is formed (digit reversal, charged 300) and `rho_j = 4^(-j)` (square-and-multiply on at most 33 bits, charged 400). (a) Gather: row `(-k) mod S` (`k < kappa`) of the buffer receives `w_k[j] * c_k * rho_j^k` with `c_k = z^(-C(k,2)) / (B M'(z^k))` (a table) and the running power `rho_j^k` (an array of 1,024 words), 10 operations per element with the address operations; this is `a_k z^(-C(k,2))` of section 3, because `W_k[j] = u_k^(-j) w_k[j]` and `u_k^(-j) = 4^(-kj) = rho_j^k`. The other `S - kappa` rows are set to zero (1 store per element); with the rows reversed in this way each correlation is one cyclic convolution of length `S`. (b) First correlation: forward transform of length `S`, product by the precomputed spectrum of the chirp `z^(C(n,2))` (a row constant: per row one load with its address, per element a load, a multiplication and a store), inverse transform. (c) Rows `i < kappa` multiplied by `z^(-C(i,2)) / S` and moved to row `(-i) mod S` for the second correlation (4 per element), the other `S - kappa` rows zeroed (1 store per element). (d) Second correlation with `(mu_1, ..., mu_kappa)` the same way. (e) Scatter: `h_t[j]` (row `t < kappa`, `j + tB <= m`) times `1/S` stored at `g[j + tB]`, the address from the row base and the slot's offset (6 per element). Per group 700 per slot and 1,000 of set-up.
4. *Once per trial:* the tables `c_k` and `z^(-C(i,2))/S` (two inversions per index, 2,640 each, and 40 per index), the chirp and `mu` (40 per index), their two spectra (two transforms of length `S` at `cnt = 1`, and `10 S`), allocations and set-up 10,000.
5. *Normalisation:* the leading coefficient tested (5) and inverted (2,640); per coefficient a load, a multiplication and a store with the address operations (6).

The interpolation is exactly that of section 3 (Lagrange interpolation at the geometric nodes `z^k`, two correlations); only the slot order of the inverse transforms and the per-slot factor `rho_j^k` are made explicit. The standard-library program `stageb_toy.py` below runs this sequence (inverse transforms with the slots permuted, the factors `rho_j^k`, both correlations as cyclic convolutions of length `S`) on random polynomials over the Pallas field at toy sizes and recovers every coefficient:

```
Bt 6 kappa 3 ok
Bt 12 kappa 5 ok
Bt 24 kappa 4 ok
Bt 8 kappa 7 ok
Bt 48 kappa 2 ok
```

**B2.3 Charges at r = 18** (`python3 stageb_count.py 18`; `m = 29,802,322,387,695,312`, `kappa = 4625930`, `S = 12,582,912`, program `L` 351 operations):

| part | operations |
|---|---:|
| evaluations | 20,921,233,620,955,299,840 |
| point loop | 327,825,598,141,675,722 |
| inverse transforms | 1,906,893,185,930,494,984 |
| solve | 17,056,067,357,679,550,466 |
| constants | 27,714,135,828 |
| normalisation | 178,813,934,326,174,525 |
| **row B (this entry)** | **40,390,833,724,747,331,365** |

Row B of `ab6b989a`: `86,684,755,546,378,974,541`; the evaluations (`20,921,233,620,955,299,840`) are the same in both, so the whole difference, `46,293,921,821,631,643,176`, is in the loop work, the inverse transforms and the solve.

**B2.4 Ledger.** `N_max = 7,025,604,697,305,484,378,778 - 86,684,755,546,378,974,541 + 40,390,833,724,747,331,365 = 6,979,310,775,483,852,735,602`, `log2(N_max / 594) = 63.34925544553`, claimed `time_log2 = 63.34926` (rounded up at five decimals; was `63.35880`).

**B2.5 Memory.** The solve buffers (section 7, the added term): the group buffer (`1,024 * S` elements), the two spectra (`S` each), the two tables of `kappa` constants and three arrays of 1,024 words, each as its own slab slot: `551,366,623,232` bytes. Footprint `3,815,855,379,080,802,572 + 551,366,623,232 = 3,815,855,930,447,425,804` bytes, `log2 = 61.72671242`, claimed `memory_log2_bytes = 61.72672` (was `61.72672`). The value array and `g` are the two arrays of the base's stage B; the stage-B live set stays below the stage-C high-water mark that sets the pool.

**B2.6 The counting program** (`stageb_count.py`, standard library only) and its output at this r:

```python
"""Operation count of stage B (construction of g_c) with the geometric solve on column passes.
Standard library only.  Every charge is an integer; `python3 stageb_count.py R` prints the breakdown at R partial rounds."""
import sys

B = 3 * 2**31            # points per coset (transform size of the inverse transforms)
VCNT = 2**10            # positions per group of the solve (columns of the group buffer)

def F(cnt):              # loop control of a column pass, eight positions per pass (section 4.2)
    return 1 + 3 * (cnt // 8) + 2 + 3 * (cnt % 8) + 2

# column kernels of section 4.2: (rows, kernel constant, per-position charge)
COL = {7: (128, 269, 1600), 6: (64, 139, 704), 5: (32, 34, 304), 4: (16, 18, 128),
       3: (8, 10, 52), 2: (4, 6, 20), 1: (2, 5, 11)}
OB3 = (3, 7, 22)

def call(kern, cnt):     # one call: sc_ocall 2*nb + 6, kernel constant, per position, loop control, loop of calls 3
    nb, k0, kp = kern
    return 2 * nb + 6 + k0 + kp * cnt + F(cnt) + 3

def radix2_run(a, cnt):
    """least-charge split of a run of `a` radix-2 layers (rows of 2^a points) into passes of <= 7 layers;
    returns the charge of the run for ONE row (2^(a-k) calls per pass of k layers), loop exits included."""
    best = [0] + [None] * a
    for L in range(1, a + 1):
        for k in range(1, min(7, L) + 1):
            c = best[L - k] + (2**a // 2**k) * call(COL[k], cnt) + 2
            if best[L] is None or c < best[L]:
                best[L] = c
    return best[a]

def size_split(n):
    a, t = 0, n
    while t % 2 == 0:
        t //= 2; a += 1
    assert t in (1, 3), n
    return t, a

def col_transform(n, cnt):
    """one forward or inverse transform of length n (n = 2^a or 3 * 2^a) on `cnt` positions by column passes:
    the radix-3 stage (n/3 calls of ob3) and the radix-2 layers of each of the t rows; no pruning, no twiddle-1 saving."""
    t, a = size_split(n)
    c = 0
    if t == 3:
        c += (n // 3) * call(OB3, cnt) + 2
    c += t * radix2_run(a, cnt)
    return c

def row_pass_rowconst(n, cnt):
    """a pass over n rows of cnt positions that multiplies every element by a constant of its row:
    per row the constant loaded (load + address, 2), the call 2 + 6, the loop F(cnt) and 3 for the loop of rows;
    per element a load, a multiplication and a store (3)."""
    return n * (2 + 8 + F(cnt) + 3 + 3 * cnt) + 2

def S_of(kappa):
    best = None
    for a in range(0, 80):
        for v in (2**a, 3 * 2**a):
            if v >= 2 * kappa - 1 and (best is None or v < best):
                best = v
    return best

def count(r):
    D = 5**(6 + r); m = (D - 1) // 2
    kappa = -(-(m + 1) // B)
    S = S_of(kappa)
    ev = 135 + 12 * r
    out = {}
    # (1) point loop: per point 2 evaluations, 2 additions (c' + s, c' - s), 1 subtraction, 1 multiplication by 1/(2s),
    #     2 multiplications for the running s and 1/(2s), 1 store with its address (2), loop control 3: 2 ev + 11;
    #     per coset 20 (row set-up: v_k, 1/(2 v_k), the row base, loop control).
    out['evaluations'] = 2 * kappa * B * ev
    out['point loop'] = kappa * B * 11 + kappa * 20 + 2
    # (2) the kappa inverse transforms of size B, made together as column passes across the cosets (the value array
    #     is coset-minor: the value of point i of coset k is at i * kappa + k), cnt = kappa, in place, decimation in
    #     frequency (natural order in, transform order out), plus 1,000 for the driver.
    out['inverse transforms'] = col_transform(B, kappa) + 1000
    # (3) the solve, per group of VCNT slots (B / VCNT groups):
    G = B // VCNT
    per_group = 0
    # gather: rows k < kappa, per element load w, load and update the running power rho_j^k (load, mul, store),
    #   multiply by it and by the row constant c_k = z^(-C(k,2)) / M'(z^k), store: 10 per element (address included),
    #   per row 2 + 8 + F + 3; the rows kappa .. S-1 zero-filled: 1 store per element, per row 8 + F + 3.
    per_group += kappa * (13 + F(VCNT) + 10 * VCNT) + (S - kappa) * (11 + F(VCNT) + VCNT) + 4
    # first correlation: forward transform, pointwise by the chirp spectrum (row constant), inverse transform
    per_group += 2 * col_transform(S, VCNT) + row_pass_rowconst(S, VCNT)
    # between: rows i < kappa multiplied by z^(-C(i,2)) / S (row constant) and moved to the second correlation's layout
    #   (load, mul, store, 3 per element, plus 1 for the address of the moved row), rows kappa .. S-1 zero-filled
    per_group += kappa * (13 + F(VCNT) + 4 * VCNT) + (S - kappa) * (11 + F(VCNT) + VCNT) + 4
    # second correlation: forward transform, pointwise by the spectrum of (mu_1 .. mu_kappa) (row constant), inverse
    per_group += 2 * col_transform(S, VCNT) + row_pass_rowconst(S, VCNT)
    # scatter: rows t < kappa, per element load, multiplication by 1/S, store to g[j + tB] with its address formed
    #   from the row base and the slot's offset (load of the offset, addition): 6 per element; per row 13 + F
    per_group += kappa * (13 + F(VCNT) + 6 * VCNT) + 4
    # per group: the VCNT slot offsets j = pi(slot) (digit reversal, 300 each), rho_j = 4^(-j) and the running powers
    #   (exponentiation of 33 bits: 400 each), group set-up 1,000
    per_group += VCNT * 700 + 1000
    out['solve'] = G * per_group + 3 * G + 2
    # (4) once per trial: the constants c_k (two inversions at 2,640 each and 40 per index), the chirp z^(C(n,2)) for
    #     n < S and mu_i (40 per index), the two kernel spectra (two transforms of length S at cnt = 1, plus 10 S),
    #     the group buffer allocation and the stage set-up (10,000)
    out['constants'] = kappa * (2 * 2640 + 40) + 2 * S * 40 + 2 * (col_transform(S, 1) + 10 * S) + 10000
    # (5) normalisation: the leading coefficient tested (5) and inverted (2,640); per coefficient a load, a
    #     multiplication and a store with the address operations (6)
    out['normalisation'] = 6 * (m + 1) + 2645 + 2
    total = sum(out.values())
    return dict(r=r, m=m, kappa=kappa, S=S, ev=ev, parts=out, total=total)

if __name__ == '__main__':
    r = int(sys.argv[1])
    c = count(r)
    print('r', r, 'm', c['m'], 'kappa', c['kappa'], 'S', c['S'], 'program', c['ev'])
    for k, v in c['parts'].items():
        print('  %-20s %40s' % (k, format(v, ',')))
    print('  %-20s %40s' % ('row B', format(c['total'], ',')))
```

```
r 18 m 29802322387695312 kappa 4625930 S 12582912 program 351
  evaluations                        20,921,233,620,955,299,840
  point loop                            327,825,598,141,675,722
  inverse transforms                  1,906,893,185,930,494,984
  solve                              17,056,067,357,679,550,466
  constants                                      27,714,135,828
  normalisation                         178,813,934,326,174,525
  row B                              40,390,833,724,747,331,365
```

**B2.7 The toy check** (`stageb_toy.py`, standard library only):

```python
"""Toy-size check of the stage-B solve of proof.md section 3 (Appendix B2): values of a random polynomial g on the
kappa cosets u_k <omega> (u_k = 4^k, omega of order Bt) -> per-coset inverse transforms (output in digit-reversed
slot order) -> per-slot scaling rho_j^k -> first correlation (chirp) -> scaling z^(-C(i,2)) -> second correlation (mu)
-> coefficients of g.  Pallas field, standard library only."""
import random
p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
def inv(a): return pow(a, p - 2, p)
def root(order):                      # an element of exact multiplicative order `order` (order | 3 * 2^32)
    g = pow(5, (p - 1) // order, p)
    for q in (2, 3):
        if order % q == 0: assert pow(g, order // q, p) != 1
    return g
def dft(a, w):                         # direct transform: A[t] = sum_i a[i] w^(i t)
    n = len(a); return [sum(a[i] * pow(w, i * t, p) for i in range(n)) % p for t in range(n)]
def cyc_conv(x, y, w):                 # cyclic convolution through transforms of length n with root w
    n = len(x); X = dft(x, w); Y = dft(y, w); Z = [a * b % p for a, b in zip(X, Y)]
    ni = inv(n); return [v * ni % p for v in dft(Z, inv(w))]
def digit_reverse_perm(Bt):            # any fixed permutation of the slots (the transform order); here bit reversal of
    a = Bt.bit_length() - 1            # the radix-2 part with the radix-3 digit last, as an example of a transform order
    if Bt == 2**a:
        return [int(format(i, '0%db' % a)[::-1], 2) for i in range(Bt)]
    t = Bt // 3; a = t.bit_length() - 1
    return [3 * int(format(i % t, '0%db' % a)[::-1], 2) + i // t for i in range(Bt)]
def run(Bt, kappa, trials=3, seed=1):
    rnd = random.Random(seed)
    for _ in range(trials):
        m = kappa * Bt - 1 - rnd.randrange(Bt)               # deg g = m, kappa = ceil((m + 1) / Bt)
        g = [rnd.randrange(p) for _ in range(m + 1)]
        omega = root(Bt); z = pow(4, Bt, p)
        # values on the cosets
        vals = [[sum(g[e] * pow(pow(4, k, p) * pow(omega, i, p) % p, e, p) for e in range(m + 1)) % p
                 for i in range(Bt)] for k in range(kappa)]
        # per-coset inverse transform; slot sigma holds coefficient position j = pi[sigma]
        pi = digit_reverse_perm(Bt); assert sorted(pi) == list(range(Bt))
        w = [[0] * Bt for _ in range(kappa)]
        for k in range(kappa):
            co = [v * inv(Bt) % p for v in dft(vals[k], inv(omega))]   # co[j] = u_k^j W_k[j]
            for s in range(Bt): w[k][s] = co[pi[s]]
        # constants of the solve
        S = min(v for v in [2**a for a in range(40)] + [3 * 2**a for a in range(40)] if v >= 2 * kappa - 1)
        wS = root(S)
        nodes = [pow(z, k, p) for k in range(kappa)]
        mu = [1]                                               # M(X) = prod (X - z^k), coefficients mu_0 .. mu_kappa
        for x in nodes:
            mu = [((mu[i - 1] if i > 0 else 0) - x * (mu[i] if i < len(mu) else 0)) % p for i in range(len(mu) + 1)]
        Mp = []
        for k in range(kappa):
            t = 1
            for l in range(kappa):
                if l != k: t = t * (nodes[k] - nodes[l]) % p
            Mp.append(t)
        C2 = lambda n: n * (n - 1) // 2
        ck = [pow(inv(z), C2(k), p) * inv(Mp[k]) % p for k in range(kappa)]
        chirp = [pow(z, C2(n), p) for n in range(S)]
        out = [0] * (kappa * Bt)
        for s in range(Bt):
            j = pi[s]; rho = inv(pow(4, j, p)); P = 1
            a = []
            for k in range(kappa):                             # gather: w * rho_j^k * c_k
                a.append(w[k][s] * P % p * ck[k] % p); P = P * rho % p
            # first correlation A(i) z^(C(i,2)) = sum_k a_k z^(C(k+i,2)), i < kappa, as a cyclic convolution of length S
            x = [0] * S
            for k in range(kappa): x[(-k) % S] = a[k]
            y = cyc_conv(x, chirp, wS)
            A = [y[i] * pow(inv(z), C2(i), p) % p for i in range(kappa)]
            # second correlation h_t = sum_{i > t} mu_i A(i - t - 1), t < kappa
            x2 = [0] * S; y2 = [0] * S
            for i in range(kappa): x2[(-i) % S] = A[i]
            for i in range(1, kappa + 1): y2[i - 1] = mu[i]
            hcon = cyc_conv(x2, y2, wS)
            for t in range(kappa):
                if j + t * Bt <= m: out[j + t * Bt] = hcon[t]
        assert out[:m + 1] == g, 'mismatch'
    return True
if __name__ == '__main__':
    for Bt, kappa in ((6, 3), (12, 5), (24, 4), (8, 7), (48, 2)):
        print('Bt', Bt, 'kappa', kappa, 'ok' if run(Bt, kappa) else 'FAIL')
```

