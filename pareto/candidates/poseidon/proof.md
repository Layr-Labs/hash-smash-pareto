# Orchard Poseidon, r = 21: algebraic collision algorithm. Two free rounds on a line, odd part about a random centre, half-gcd with the inversion-free node on three rows, one centre, value-domain Graeffe prefix of 31 steps on the cosets of H^2, line program, aligned split

## 1. Claim

Target: `poseidon-orchard-r21-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, twenty-one partial rounds 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23 and 24, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

Authorship. This package is our r = 21 entry `30df2129` (time + memory penalty 119.16802), edited in place, with one change: in each of the 31 extensions of the Graeffe prefix (4.3G (iii)) the Toeplitz matrix `T` of order `2K` is applied as **one cyclic convolution of length `2 Lx = 2^32`** in the form of lemma 4.7 (bradcush `1aa56884`, as used in 4.6), in place of three products of order `K` and their schedule, charged by an exact pass-by-pass count (4.3G (iii)(b)). Row C `569,033,738,863,809,196,598,398`, `N_max = 1,060,183,533,768,181,510,310,184`, `time_log2 = 70.45084`, `memory_log2_bytes = 68.69383` (was `68.69384`; footprint `477,422,904,612,384,466,060` bytes, section 7), time + memory penalty `119.14467` (`30df2129`: `N_max = 1,077,472,428,245,490,240,123,723`, `70.47418`, `119.16802`); every other row unchanged. The rest of this paragraph describes `30df2129`: it is our r = 21 entry `213552fe` with three credited changes. (i) Stages C and F (akki-rock05, entry `eebae39d`, which is `213552fe` with this change; its text is taken over with credit): a **value-domain Graeffe prefix** (section 4.3G), the method of akki-rock05's r = 9 and r = 12 entries `479bd57c` and `bdc5ccfe` in the form this round needs. Here `H` has order `2^32`, the whole 2-part of `p - 1`, so no element of order `2h` exists; the prefix therefore works on the `2K = 1,734,723,476` cosets of `H' = H^2` (order `2^31`) that the `2K` cosets of `O1` and `O2` contain (the two halves of each coset of `H` in its transform order), with `omega` (the generator of `H`) in the role that `zeta` has at r = 9 and r = 12. Before the powering of 4.6, stage C replaces `g = g_c` by `g^(31)`, 31 Graeffe steps `g(Y) <- E(Y)^2 - Y O(Y)^2`, each computed in the value domain as `g^(t+1)(x^2) = g^(t)(x) g^(t)(-x)` at the cost of one Graeffe pass and one extension between cosets of `H'` (charged by an explicit bound from the extension of 4.6, 4.3G), where a loop step of 4.6 costs two pointwise passes and two extensions; the residue is `R = S^((p-1)/2^32) mod g^(31)`, so 163 loop steps remain in place of 194. Stage D takes `G = gcd(g^(31), R - 1)`, whose roots are the distinct `2^31`-th powers of the usable roots of `g_c`, and stage F recovers a collision by a scan over `2^31` candidates. (ii) Stage B and the scan of F (mpjunior92, entry `c667182d`, its Appendix L): each evaluation of `F` is one execution of the line program `L` (Appendix L, `387` operations at r = 21 in place of `657`) and stage E is that of `213552fe` (4.1.2, 9.4; row E of section 6 unchanged). (iii) Stage D (this entry): the **aligned split** of akki-rock05's entry `4cb15141` (its 4.4.3 item 1): every node of the half-gcd of parameter `2^46 < k < 2^53` gives its first call the budget `2^(b-1) - 1`, `b` the bit length of `k`, in place of `ceil(k/2)` (4.4.2 item 1); with the new walk the allocator takes the blocks of more than `2^54` bytes from the pool (was `2^53`; section 7). Rows (section 6): B `13,300,858,577,087,557,708,729` (was `15,312,515,339,265,429,643,596`), C `586,322,633,341,117,926,411,937` (was `606,998,556,432,298,400,337,481`), D `477,848,936,324,260,928,287,843` (was `499,583,924,451,688,166,545,205`), F `3,006,477,160,520` (was `47,012`), every other row unchanged. Totals: `N_max = 1,077,472,428,245,490,240,123,723` (was `1,121,894,996,223,269,347,127,988`; `eebae39d`: `1,101,219,073,135,095,350,315,644`), `time_log2 = 70.47418` (was `70.53247`; `eebae39d`: `70.50563`), `memory_log2_bytes = 68.69384` (was `68.69285`; footprint `477,423,045,899,628,635,276` bytes), time + memory penalty `119.16802` (was `119.22532`; `eebae39d`: `119.19848`). Appendix G itemises the prefix and the new rows; Appendix G2 records the toy-size checks of the prefix. In the text taken from `eebae39d` (4.3G, 6.2a, the restated premise `H-NORMAL` of 9.5 and its -g31 tests in 10.2 and 10.5.1) and from `c667182d` (Appendix L) the credits name their authors; text that says "our" or "this entry" elsewhere refers to the authors of `213552fe` and this package.

This entry is an algorithm (sections 2-4) with a worst-case operation count (sections 6-7) and a success probability derived from the premises `H-ONE` (section 9.1) and `H-NORMAL` (section 9.5), statements about the usable roots of the fixed digest polynomial and its remainder sequences; section 9.2 derives the success probability from them with explicit constants.

* The algorithm: draw a centre `c` uniformly from `F_p` from fresh random words, build the odd part `g_c` of the line polynomial by evaluation (the line program `L` of Appendix L) and 578241159 inverse transforms (one per coset, section 3), replace `g_c` by `g^(31)`, 31 Graeffe steps in the value domain on the cosets of `H^2` (4.3G), compute `G = gcd(g^(31), S^((p-1)/2^32) - 1)` by a power-mod in the value domain (section 4.6, the method of bradcush 1aa56884) and a half-gcd in the lean form of 1aa56884 (4.4.1) with the aligned split of akki-rock05 `4cb15141` (4.4.2 item 1), whose matrix-only calls of parameter `2^j - 1` (`7 <= j <= 31`) run on bradcush's inversion-free half-gcd on three rows (4bcabff8; 4.4.2), and if `G` has degree between 1 and `DMAX = 16` isolate a root `y` of `G` in at most `Z = 64` rounds, find `s` with `s^(2^32) = y` and `F(c + s) = F(c - s)` by a scan of `2^31` candidates (4.3G), map back and verify the two inputs with the reference hash. One centre is tried (`K = 1`), on a single thread; a verified collision ends the algorithm.
* `success_probability = 0.39209`: a lower bound for the probability, over the algorithm's fresh random words, that the one centre yields a verified collision on the fixed target: `P >= 1 - (1 - q + delta + delta_C)^K - K (eps_iso + eps_coin) = q - delta - delta_C - eps_iso - eps_coin` with `K = 1`, `q = 0.3931` (the premise `H-ONE`, section 9.1: at least `0.3931 p` centres have between 1 and `DMAX = 16` usable roots), `delta = 0.001` the allowance of the premise `H-NORMAL` for an abnormal remainder sequence (section 9.5), `delta_C < 2^-98.6` the stage-C zero test (proved, 9.2(b), with the Graeffe prefix), `eps_iso <= P[Bin(64, w) <= 3] = sum_(j <= 3) C(64, j) w^j (1 - w)^(64 - j) = 2.371e-15 < 2^-48` (each isolation round halves `deg G <= 16` with probability at least `w = 1/2 - 7.869e-40` whatever came before, and four halvings reach degree 1; lemma 9.4), `eps_coin < 2^-122` (4.1.1). The value the formula gives with the stated eps bounds is `0.39209999999999762857` (rounded down). The value of `q` is `0.3934693 - 0.3931 = 0.0003693` below `1 - e^(-1/2) = 0.3934693` (and `q <= 151/384 = 0.3932292`, the four-moment Bonferroni bound), the law of the usable roots in section 9.3, which is a theorem for the first two and three S-box layers on the deployed constants (9.3(c)).

* `time_log2 = 70.45084` in target-compression units (`C(21) = 657` primitive operations per unit): the worst-case operation count, derived in section 6 as `T_fixed + K * T_trial` with `K = 1`, the trial charged in full (stage D for the normal remainder sequence, which bounds every trial because a trial with any other sequence ends after a prefix of that work, section 6.3; stage E at its cap of `Z` rounds at degree `DMAX`), `N_max = 1,060,183,533,768,181,510,310,184` operations `= 1,613,673,567,379,271,705,190.53` units, `log2(N_max / 657) = 70.4508387557`, claimed as `70.45084` (rounded up at five decimals; with the Graeffe prefix of 4.3G, the line program `L` of Appendix L and the aligned split of 4.4.2; `213552fe` had `1,121,894,996,223,269,347,127,988` operations, `70.53247`; `eebae39d` `1,101,219,073,135,095,350,315,644`, `70.50563`). The offline derivation of the constants (section 6.2) is counted, `T_off = 136,785` operations (at most `138,785` with the literal `u` of the Graeffe prefix, 6.2a, and at most `836,651` with the `154` constants of `L`, Appendix L.1), and charged at its declared cap of 1,000,000 operations; that cap is inside `N_max` and is declared as `preprocessing_log2 = 20` (one quantity, not added twice).
* `memory_log2_bytes = 68.69383` (`477,422,904,612,384,466,060` bytes, section 7: the arena of the allocation walk with the aligned split, `477,422,622,862,523,491,840` bytes, the terms (a), (c), (d), (e) of `213552fe`, `6,291,084` bytes, `32,768` bytes of code and static data and `281,749,854,617,600` bytes of slab area for the Graeffe prefix (one group buffer and one kernel spectrum, 4.3G (iii)(c)), and `32,768` bytes for `L`, Appendix L.4). Time + memory penalty `70.45084 + 48.69383 = 119.14467` (`30df2129`: `119.16802`; `213552fe`: `119.22532`; `eebae39d`: `119.19848`).
* Coins: the only randomness is the cost model's random-word primitive, fresh and independent, one operation per word; `65` words at most (section 4.1.1), and a draw (one word) costs 31 operations. There is no other input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^27`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3) combined with a Cantor-Zassenhaus style root search; credits are in the submission note.
* Against our r = 21 entry `6f684cea` (time + memory penalty 119.36420, the same algorithm and package), five changes: (i) power-of-two budgets and the inversion-free half-gcd of bradcush's entry `4bcabff8` on three rows for every matrix-only call of parameter `2^j - 1`, `7 <= j <= 31` (4.4.2; ported as in our r = 3 entry `bcf8e01c`), with the table of its scales and the code of its routines charged (7(a)); (ii) with the apply plans of 0xplemonade's entry `ff21bd28`, each apply of steps (2) and (6) of a half-gcd node runs the cheaper of its block products or single transform and a direct whole-pair or fixed-slot plan on one transform size (4.4.1 item 8); (iii) with the batch-inversion prefix of `ff21bd28`, stage C runs the batch inversion in chunks of `2^16` elements (its auxiliary array `2^16` elements, was `h`) and forms the `omega^e` of the `b = 1` boundary pass from two tables of `2^16` entries (was one table of `h` entries; 4.6); (iv) the layers of the block-form passes and of the column passes are split into passes of at most seven layers by the split of least charge, in place of seven at a time with the remainder in one pass (4.2; the exact pass split of 0xplemonade's entry `d4b13ccd`); (v) in the node of the inversion-free half-gcd (4.4.2), the four chunks of each of `a`, `b` are folded onto the three rows in one loop of 22 operations per position and each matrix-vector map of the node is one two-output pass of 20 operations per point (the fused two-output rows of 0xplemonade's entry `8b1eb62a`, read as text, priced by the direct apply row of `ff21bd28`). Row C `606,998,556,432,298,400,337,481` (was `607,225,779,134,910,203,394,165`), row D `499,583,924,451,688,166,545,205` (was `612,741,468,908,096,532,029,872`); `N_max` `1,121,894,996,223,269,347,127,988` (was `1,235,279,763,382,289,515,669,339`), time_log2 `70.53247` (was `70.67137`); the live peak of stage C `476,837,265,213,765,335,104` bytes (was `476,837,265,488,636,950,592`), the arena `477,097,308,158,190,151,808` bytes (was `477,089,359,479,395,296,384`); term (a) `54,624` bytes more code (7(a)); memory `477,097,308,158,196,442,892` bytes, memory_log2 `68.69285` (was `68.69283`). The premises, the success bound and the experiments are unchanged.
* Against our r = 21 entry `741765b3` (time + memory penalty 119.37749, the same algorithm and package): (i) the register file of the machine is one file of 387 words, 256 field registers of 256 bits plus the 131 integer address registers of an `ob128` call, counted in the memory (7(d), 12,384 bytes), as ruled on our r = 17 entry `fdb6bc0e` (the same machine text); (ii) in group 0 of every block-form pass a butterfly whose twiddle is 1 is its addition and subtraction, 2 operations (a straight-line variant of the block body, 3 control operations more per pass), as in the column kernels (4.2); (iii) the block loop of a group runs four blocks per pass of a straight-line body (a group of one block has no block loop): 3 control operations per block (was 5) (4.2); (iv) the offline derivation of 6.2 is counted literal class by literal class, `T_off = 136,785`, charged at its declared cap 1,000,000, as ruled on our r = 5 entry `4896c4ea` (the same 6.2 text); (v) `H-NORMAL` at `delta = 0.001` in place of `0.003` (9.2, 9.5), the form of our accepted r = 9 entry `5b96dbb5`: the success bound is `0.39209999999999762857`, claimed `0.39209` (was `0.39009`); its tests are `euclid-normal-n2-t256-l2-a` to `-l2-f`, `-n3-t24` and `-n4-t2`, and the `H-ONE` tests `euclid-gcdpos-n2-t256-a`, `-b` and `-n3-t24` replace the one-centre tests (10.5.1). Row C `607,225,779,134,910,203,394,165` (was `607,393,835,440,886,834,460,801`), row D `612,741,468,908,096,532,029,872` (was `623,861,751,433,438,662,055,922`); arena `477,089,359,479,395,296,384` bytes (was `477,089,359,479,124,731,008`); code bound 7(a) +907,520 bytes for the straight-line bodies; memory `477,089,359,479,401,532,844` bytes, claimed at five decimals, `68.69283` (was `68.693`); time + memory penalty `119.36420` (was `119.37749`). Every other charge is unchanged.
* Against our r = 21 entry `2be501f4` (time + memory penalty 119.48148, the same algorithm and package): the register file of the machine is 256 words of 256 bits (was 64), counted in the memory (7(d), 8,192 bytes), as the live entry cryptogakusei `1533f8f0` declares a file of 304 registers of 256 bits: the column passes of stage C and of the outer transforms of stage D take up to seven layers (`ob64`, `ob128`) and the block-form passes of the products up to seven layers (blocks of 128 points with their 127 twiddles in registers); 4.2; every column pass runs its position loop eight positions per pass, with the loop control `F(cnt) = 1 + 3 floor(cnt / 8) + 2 + 3 (cnt mod 8) + 2` per call in place of 3 per position (our r = 17 entry `8346be35`; 4.2, 4.6). Row C `607,393,835,440,886,834,460,801` (was `661,024,929,398,749,279,061,636`), row D `623,861,751,433,438,662,055,922` (was `663,399,864,848,100,396,741,427`); arena `477,089,359,479,124,731,008` bytes (was `477,089,359,466,094,773,376`), memory_log2 unchanged. Every other charge, the premises and the experiments are unchanged.
* Against our r = 21 entry `8d17fd47` (time + memory penalty 119.51996, the same algorithm and package): two kernel changes. (i) A column-kernel butterfly whose twiddle is 1 is charged 2 operations (its call at offset 0 a straight-line variant, 4.2). (ii) The block-form passes take up to five layers (blocks of 32 points; 32 data words, 31 twiddles and the temporary, the 64 words of the declared file, as `ob32`; 4.2). Row C `661,024,929,398,749,279,061,636` (was `670,148,841,489,866,082,128,996`), row D `663,399,864,848,100,396,741,427` (was `690,486,674,943,952,789,921,455`); arena `477,089,359,466,094,773,376` bytes (was `477,089,359,472,523,371,648`), memory_log2 unchanged. Every other charge, the premises and the experiments are unchanged.
* Against our r = 21 entry `1255c53b` (time + memory penalty 119.60746, the same algorithm and package): the loads and stores of the block-form passes of 4.2 are charged one operation each (base plus index, as the column kernels `ob4` to `ob32`): row C `670,148,841,489,866,082,128,996` (was `672,339,392,072,036,941,416,468`), row D `690,486,674,943,952,789,921,455` (was `774,335,010,767,241,376,337,953`); memory unchanged. Every other charge, the premises and the experiments are unchanged.
* Against the same algorithm with the leaf passes of 4.2 in every product (time + memory penalty 119.6872): the transform passes of the products of stages C and D (all but the fused pass of each product) run in the block form of our r = 3 entries `ef123c2b` / `253629b9` (per group the `2^k - 1` twiddles held in registers), on the 64-word register file stated as a restriction in claim.json: row C `672,339,392,072,036,941,416,468` (was `675,011,474,978,489,941,202,668`), row D `774,335,010,767,241,376,337,953` (was `854,741,793,443,757,595,102,694`); arena `477,089,359,472,523,371,648` bytes (was `477,089,359,470,805,378,176`). Every other charge, the premises and the experiments are unchanged.
* Prior entry: this entry is the r = 21 version of our r = 7 algebraic entry 05a41d88 (the same algorithm, ledger method, premise structure and evidence design). The ruling on 05a41d88 (not_evaluable on the experiments lane) is answered here in the same way: the organizer experiments `line-ladder-w6`, `-w8`, `-w10` and `-w12` on the antipodal line pairs of this construction at r = 21 (10.2), the computations of Grok job 136 and their re-run on the deployed constants and the construction's line (10.3), and the measurement of the Euclidean sequences on the sibling targets (10.5). Stage C is the value-domain powering of bradcush's entry 1aa56884 (section 4.6), stage D its lean half-gcd (4.4.1), and stage D is charged for the normal remainder sequence under the premise `H-NORMAL` of bradcush (entries e6dcb600, 1aa56884) with gta6rp's allowance and organizer-run tests (9.5); all credited in the dependencies and the note.
* Declared heuristics (claim.json): `H-ONE` (score-critical, section 9.1) and `H-NORMAL` (score-critical for the success probability only, section 9.5). Both are statements about probability. `H-NORMAL` is bradcush's premise (entries e6dcb600 and 1aa56884), stated here with the allowance `delta = 0.001` (the value of our accepted r = 9 entry `5b96dbb5`) and supported by organizer-run normality tests, the recipe of gta6rp's entries (fe269c23 at r = 20; first in 6871afce at r = 14); the test program `experiments/exp_euclid.py` is our own (10.5.1). The costs are the declared cost model of this entry, not heuristics: the charging rules of section 4.2 on the machine stated as a restriction in claim.json (256 field registers of 256 bits plus 131 integer address registers; every load, store and spill counted), as the accepted entries `89b451ff` and `fb176310` state theirs and as our r = 3 entries `ef123c2b` and `253629b9` do, and the base-plus-index addressing of the stage-C column kernels (4.2), stage D charged for the normal remainder sequence with the quotient and return tests and the ABORT on any other case (section 6.3; the time and memory bounds hold for every sequence), and the arena of section 7, the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation. Everything else is proved or counted here: the line construction, the degree of `F`, the odd-part reduction, the collision criterion (sections 2, 3, 5), the success bound (section 9.2), the stage-C zero-test bound (9.2(b)), the isolation lemma (section 9.4), the uniformity of the centre, the cap rules and every operation count (sections 4, 6, 7).
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

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24 (partial), 60, 61, 62, 63 (full) put twenty-seven S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^27 = D = 7,450,580,596,923,828,125`. The leading coefficient is obtained by
propagating leading coefficients through the twenty-seven layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used:
`f_D(0) = 0x036b153bb044072edf9f26b65249c0916ff2a474ed84a710a60ff678516cb3a3`
(computed by the propagation just described, with the same code reproducing the constants of the executed entries at r = 3, 4, 5; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked at the executed round counts on random `tau`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 3,725,290,298,461,914,062`, `g_c` has degree exactly `m` and
leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives `s = 0` and is not a root of `S^((p-1)/2) - 1`).
`G` divides `S^((p-1)/2) - 1`, which is squarefree, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. At this r no transform of `H >= m + 1` points exists: `p - 1 = 2^32 * 3 * q'` has roots of unity of order `3 * 2^a` for `a <= 32` only, and `m + 1 = 3,725,290,298,461,914,063 > 3 * 2^32`. Let `B = 3 * 2^31 = 6,442,450,944`, `zeta` a primitive `2B`-th root of unity (`2B = 3 * 2^32` divides `p - 1`) and `omega = zeta^2`, a primitive `B`-th root. Let `kappa = ceil((m + 1) / B) = 578241159`, `v_k = 2^k` and `u_k = v_k^2 = 4^k` for `k < kappa`, and `z = 4^B`; the `kappa` numbers `n_k = u_k^B = z^k` form a geometric progression and are pairwise distinct, because the order of `z` exceeds `kappa` (`z^d != 1` for every divisor `d` of `p - 1` up to `6 * 10^8`, and `kappa < 6 * 10^8`). The evaluation points are `s_{k,i} = v_k zeta^i` for `k < kappa`, `i < B`, so that `S_{k,i} = s_{k,i}^2 = u_k omega^i`, and `g_c(S_{k,i}) = (F(c + s_{k,i}) - F(c - s_{k,i})) / (2 s_{k,i})`. Write `g_c(x) = sum_{t < kappa} x^{tB} h_t(x)` with `deg h_t < B`. For `y = omega^i` we have `y^B = 1`, hence `g_c(u_k y) = w_k(y)` with `w_k(y) = sum_t n_k^t h_t(u_k y)`, a polynomial of degree `< B`. One inverse transform of size `B` of the values `(g_c(S_{k,i}))_i` returns the coefficients `w_k[j] = u_k^j sum_t n_k^t h_t[j]`. After multiplication by `u_k^{-j}`, for every `j < B` the numbers `W_k[j] = sum_t n_k^t h_t[j]` (`k < kappa`) are the values of the polynomial `h^(j)(X) = sum_t h_t[j] X^t` at the nodes `z^k`, and its coefficients `h_t[j] = g_c[j + tB]` are recovered from them by two correlations of length `kappa` (Lagrange interpolation at geometric nodes, the chirp-z form). Let `M(X) = prod_k (X - z^k) = sum_i mu_i X^i`; the q-binomial theorem gives `mu_{kappa-j} = (-1)^j z^{j(j-1)/2} [kappa choose j]_z`, and `M'(z^k) = z^{k(k-1)/2 + k(kappa-1-k)} prod_{j <= k} (z^j - 1) prod_{j <= kappa-1-k} (1 - z^j)`. With `a_k = W_k[j] / M'(z^k)` and `A(i) = sum_k a_k z^{ki}` (`i < kappa`) we have `h_t[j] = sum_{i > t} mu_i A(i - t - 1)`. Since `z^{ki} = z^{C(k+i,2) - C(k,2) - C(i,2)}` with `C(n,2) = n(n-1)/2`, `A(i) z^{C(i,2)}` is the correlation of the sequence `a_k z^{-C(k,2)}` with the chirp `z^{C(n,2)}` (first correlation), and `h_t[j]` is the correlation of `A` with `(mu_1, ..., mu_kappa)` (second correlation). Each correlation is one cyclic convolution of length `S = 1,610,612,736` (the smallest `2^a` or `3 * 2^a` that is at least `2 kappa - 1`), done with the transform of length `S` (forward, pointwise product, inverse); the transforms of the fixed sequences (the chirp and `mu`) and the constants `mu_i`, `1/M'(z^k)`, `z^{-C(k,2)}` are computed once per trial and shared by the `B` positions `j`. The `2 kappa B = 7,450,580,601,318,408,192` evaluations of `F` are each one execution of the line program `L` of Appendix L (mpjunior92 `c667182d`), `135 + 12 * 21 = 387` operations, at `c' + s` and `c' - s` (`c' = c + E0_0`, one addition per trial; Appendix L.3). The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 s_{k,i})`, two multiplications for the recurrences of `s_{k,i}` and `1/s_{k,i}`, one store with its address operation, the loop control, the update of the row counter, and the executed shifts, masks, ors and loop control of the bit-reversed index, which are counted inside that function) and the solve (per `j`: two correlations, each two transforms of length `S` with `S/2 log2` butterflies at the charge of the model's own pass cost and `10 S` operations for the pointwise product and the scalings, and `14 kappa` operations for the chirp scalings, the division by `M'`, the loads and the stores) and its once-per-trial constants (`kappa` times two inversions, 40 operations per index, four transforms of length `S` and `10 S` operations) are charged on top.

## 4. The algorithm (at most K centres, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   twiddle table (once)
setup:  the line (line_setup) (once)
for t = 1, 2, ..., K:                                  [the test t <= K is made at the start of every trial; no other exit except success]
  A  c := a uniform element of F_p from one fresh random word (section 4.1.1)
  B  g := monic g_c, by section 3 (7,450,580,601,318,408,192 executions of L, Appendix L, + 578241159 inverse NTTs of size 6,442,450,944 + the geometric solve of the 578241159 cosets (two correlations of length 1,610,612,736 per position) + the test that the leading coefficient is nonzero + normalisation by the leading coefficient)
  C  g := g^(31), 31 Graeffe steps in the value domain (4.3G); R := S^((p-1)/2^32) mod g (left-to-right square-and-multiply, base S; value domain, section 4.6: from S^v, v = 2^59; 163 (4.3G; was 194) squaring steps, 45 of them also multiply by S, pointwise)
  D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4)
  E  if deg G = 0 or deg G > DMAX: the trial ends, next t.   Otherwise isolate a root y of G (section 4.1.2).  If none is isolated within Z rounds: the trial ends, next t.
  F  t := y^u (u = (2^32)^-1 mod (p-1)/2^32); for i < 2^31: s := t eta^i (eta of order 2^32), stop at F(c + s) = F(c - s) (4.3G); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (657 operations each) are equal and the pairs differ -> go to H; otherwise the trial ends, next t
H  output: the two pairs (and the digest and the centre) are converted to canonical form and encoded as 64 hexadecimal digits each.
   If t > K was reached the algorithm fails (the failure event, probability bounded in section 9).
```
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. Binary powering therefore performs 253 modular squarings and 45 multiplications by `S`; the 61 bits after the leading one are zero, so the algorithm starts from the monomial `S^v` with `v = 2^59` (a multiple of h below m, 4.6, `VSHIFT = 2`; 59 + 194 = 253), and the loop of stage C has 194 steps, of which 45 also multiply by `S` (pointwise). With the Graeffe prefix of 4.3G the exponent is `(p-1)/2^32`: its top bits are those of `(p-1)/2` (the same start monomial `S^v`, `v = 2^59`), and the 31 trailing zero bits of `(p-1)/2` are gone, so the loop has 163 steps, 45 of them with `b = 1`.

Stopping rule. The loop bound `K = 1` is a constant of the algorithm: one centre is tried. A trial is run to its end, or to an ABORT of stage D on an abnormal remainder sequence (6.3) or of stage C on a zero of g on O1 (4.6 step 5), which then resets the allocator and draws the next centre; the claim charges every trial at its maximum (stages E to G at their worst case, section 6), so a trial that fails early is paid for at the full-trial price, never less. Stage E is entered only when `1 <= deg G <= DMAX`, and at most `Z` rounds are made in it. The algorithm has no other loop whose length depends on data: the loops of stages B to D have lengths fixed by `m` and the exponent (sections 4.3, 4.4), the powering has a fixed number of steps, and the half-gcd has a fixed recursion: 56 levels of recursion in `hgcd` (the parameter `k` starts at `floor((n+1)/2) = 1,862,645,149,230,957,031` and is halved, rounded up, until it is at most 96) and at most 56 repetitions of the outer loop of the Euclid driver (each repetition removes more than half of the degree, from 3,725,290,298,461,914,062 to at most 192). Hence, with stage D charged for the normal remainder sequence and every other sequence ending its trial after a prefix of that work (section 6.3), the number of executed operations is at most `N_max` for every coin sequence and every target value, the algorithm cannot stop early except by success, by an ABORT of a trial (the next centre is then drawn), or by failure after `K` trials, and nothing in the claim depends on a run being lucky.

#### 4.1.1 Coins

The only randomness is the cost-model random-word primitive. The words are fresh, independent and uniform on `[0, 2^256)`. A centre is `c = w mod p` for one word `w` (at most three conditional subtractions); the isolation of stage E draws at most 64 further words, reduced the same way. At most 65 words per run; a draw is 31 operations. There is no rejection and no retry. The reduction is not exactly uniform on `F_p`: `2^256 = 3p + r` with `0 < p - r = 4(p - 2^254) < 2^127.1`, so every residue has 3 or 4 preimages and `w mod p` is within statistical distance `r (p - r) / (p 2^256) < 2^-128.9` of uniform on `F_p`. Over the 65 words the distance is `eps_coin <= 65 * 2^-128.9 < 2^-122`, and the success bound (9.2) subtracts it.

#### 4.1.2 Stage E: isolating a root of G

`G` is monic, squarefree, and a product of `d = deg G` distinct linear factors over `F_p` with `1 <= d <= DMAX` (it divides `Y^((p-1)/2^32) - 1`, which is squarefree; 4.3G). The roots `r` of `G` are the distinct `2^31`-th powers `y` of the usable `S` (4.3G). While `deg G >= 2`, and for at most `Z` rounds (`ZCAP`): draw `a` (a draw as in 4.1.1; if it is 0, `a := 1`, since the Taylor shift uses `1/a`; the zero test is 5 operations and the replacement 2, charged in every round), replace `G` by `G(Z - a)` (a Taylor shift; its roots are `r + a`) and add `a` to a running shift, compute `X_a = Z^((p-1)/2) mod G` by schoolbook square-and-multiply, `G_+ = gcd(G, X_a - 1)` and `G_- = gcd(G, X_a + 1)` by classical Euclid. Then `G = G_+ G_- Z^e0` with `e0` = 1 if `G(0) = 0` and 0 otherwise. Keep, as the new `G`, the one of `G_+`, `G_-` of smaller nonzero degree (ties: `G_+`) if at least one is nonconstant; if both are constant then `G = Z` (the root is 0). When `deg G = 1` the loop ends and the root of the original `G` is `-G_0` minus the running shift. If `deg G >= 2` remains after `Z` rounds the trial fails (it ends, next `t`). Each round is charged at the cost of its operations at degree `deg G <= DMAX` (section 6). The lemma of section 9.4 bounds the probability that `deg G >= 2` remains after `Z` rounds: a round separates two given roots for at least `(p-3)/2` shifts, so it halves the degree with probability at least `w = 1/2 - 7.869e-40`, and four halvings take `16` to `1`; the failure probability is at most `P[Bin(64, w) <= 3] = 2.371e-15`, a finite sum, no premise.

### 4.2 Machine model and charging rules

Every operation of the algorithm is counted where it executes; none is estimated.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications, 330 operations; `x^e`; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each, and each such access is charged together with one address-formation operation (one control operation). Exception, the stage-C column kernels `ob4`, `ob8`, `ob16`, `ob32`, `ob64`, `ob128`, `ob4m` and the two boundary passes of the loop (4.6), and the kernels `ob4` to `ob128` in the outer transforms of stage D (4.4.1 item 6): each load or store is 1 operation with no address operation. An element of the call's block at the position `j` is addressed as row base plus position offset, and a twiddle or spectrum word of the call as the table base plus the call's index scaled by a constant of the layer, the base-plus-index addressing of the load itself; the `2^k` row bases and the twiddle address are formed once per call (in the call charge `2 * 2^k + 6`, which is added to the kernel constant of the call, below) and held in integer registers, and the position offset advances with the index update of the loop step. Everywhere else (the rest of stage D, the `ob2` and `ob3` passes and the first and last passes of an extension of stage C included) the address operation is charged as above.
* every loop: `3n + 2` control operations for `n` iterations (the index update, the bound comparison and the conditional branch of each iteration, and one comparison and branch when the loop is left). Loops over the elements of an array written eight elements per pass (the pointwise, copy, fold and subtraction loops of the powering and of the products) are charged 3 per pass of eight, 1 for the bound, 2 when the main loop is left, and 3 per iteration for the remaining 0 to 7 elements.
* every other executed index or control operation, one each: shift, mask, or, addition, subtraction, comparison, conditional branch, assignment of a register, and the selection of an element of the register block (at most 32 data words) by a computed index. Data-dependent tests are charged per executed test.
* index arithmetic uses only shifts, additions, subtractions, comparisons and branches (the benchmark's primitive list has no integer multiplication, division or modulo): a multiplication by a power of two is a shift, by 3 or 5 a shift and an addition, and a product of an index and a stride is a running sum; each is charged as a control operation where it occurs.
* transforms: a transform of size `3 * 2^a` is a twiddle-free radix-3 stage (8 operations per leaf) followed by three rows of radix-2 passes of at most seven layers (the layers of each transform are split into passes by the exact minimum of the charges of this section: over every split of its layers into passes of `k <= 7` layers, the sum of the charges of a pass of `k` layers from layer `l0` of a row of `2^a` points, with the group-0 variant below, is least; the layers of the column passes of stage C and of the outer transforms of stage D are split the same way, by the least sum of the column-pass charges over passes of up to seven layers; the exact pass split of 0xplemonade's entry `d4b13ccd`). A pass works on blocks of `2^k <= 128` points held in registers, in the block form of our r = 3 entries `ef123c2b` and `253629b9` (their `pd_fwdp`, `pd_invp`): per block its `2^k` loads and `2^k` stores (1 each: a block element is addressed as the table base plus its index, the base-plus-index addressing of the load or store itself, as for `ob4` to `ob128` above; one load per word fetched from memory and one store per word written, the wording of the accepted entries `89b451ff` and `070a02b2`), `k 2^(k-1)` butterflies at three field operations each (two where the twiddle is 1 in group 0, below) and 3 of control (2 for the base of the block and 1 for its share of the block loop, below); per group its `2^k - 1` twiddles formed and held in registers for all its blocks (24 operations for `k = 4`: two loads with their addresses, one multiplication, three squarings, eleven multiplications by register constants and control; 16 for `k <= 3`; for `k = 5, 6, 7` its `2^k - 1` twiddles are loaded from the twiddle table, 1 each (base plus index, as for `ob32`), with 9 operations of address formation and control, `2^k + 8`: 40, 72, 136); per pass `5 + (9k + 2) + 12` (forward) or `6 + (9k + 2) + 12` (inverse) of pass set-up. Block loop: a pass of `k` layers at layer `l0` of a row of `2^a` points has `2^l0` groups of `n = 2^(a - l0 - k)` blocks; `n` is a constant of the pass, stored with the other parameters of the pass in the plan of the product, and the pass is entered at the body for its `n`. A group of `n >= 4` blocks runs them four per pass of a straight-line body (the four blocks addressed as the block base plus the constants 0 to 3 times the block stride in the loads and stores themselves), loop control `1 + 3 n / 4 + 2 <= n` for `n >= 12` (at r = 21 every group of more than one block has `n >= 16`); a group of one block has no block loop. So 1 per block covers the block loop. Twiddle 1 in the block-form passes: the twiddles of a group depend only on the group and the layer, and in group 0 the first twiddle of each layer is `w^0 = 1`; in every block of group 0 the butterflies of these twiddles, `2^(k-1-j)` in the layer `j = 0, ..., k-1` of the pass, `2^k - 1` per block, are their addition and subtraction, 2 operations. Group 0 of every block-form pass (forward and inverse) runs a straight-line variant of the block body without these multiplications: `2^k - 1` operations less per block of group 0 (`2^(a - l0 - k)` blocks) and 3 control operations more per pass. The one pass of a product that fuses its last forward layers, the pointwise product and its first inverse layers keeps the charge of a leaf pass: each butterfly is three field operations (none for the multiplication when the twiddle is 1), each twiddle is one load with its address operation. The first twiddle of a layer is read through a running pointer of that layer, held in an integer register with its stride: moving it to the next block of the group is 1 operation (a pass call forms the `k` strides, one shift per layer, and for an inverse pass also the shift counts (one addition per layer) and its base pointer (a shift and an addition); each group sets its `k` pointers for block 1 anew, 1 operation per layer, and a range of blocks that does not start at block 1 sets them by a shift and an addition per layer). The blocks of a group after the first are processed four at a time by a straight-line body, then one at a time for the 0 to 3 that remain, with 1 operation per block for the advance of the block base; for `n` such blocks the loop control is `1 + 3 * floor(n / 4) + 2 + 3 * (n mod 4) + 2` operations (the bound `n & ~3`, 3 per pass of four, 2 when the main loop is left, 3 per remaining block, 2 when the second loop is left), and the group loop is charged 3 per iteration. The register file is the machine restriction of claim.json: one register file of 387 words, 256 field registers of 256 bits plus 131 integer (address) registers (as the live entry cryptogakusei `1533f8f0` declares a file of 304 registers of 256 bits), counted in the memory (7(d)), every other value charged as a load or store (a block-form pass uses at most 256: the 128 data words, 127 twiddles and the butterfly temporary, as `ob128`; the fused leaf pass 18: the 16 data words, the twiddle operand and the butterfly temporary; the stage-C pass `ob128` uses 256: 128 data words, 127 twiddles and the butterfly temporary), and the 131 integer registers of the file in a call (the `2^k <= 128` row bases, the twiddle address, the position offset and the loop bound; the fused leaf pass holds its `k <= 4` twiddle pointers, strides and shift counts and its loop counters, fewer). Stage C (4.6) and the outer transforms of stage D (4.4.1, item 6) use the same column kernels: a column pass of `k <= 7` radix-2 layers runs over `2^k` rows at `cnt` positions and keeps its `2^k - 1` twiddles in registers for the whole position loop (`ob8`: 8 data words, 7 twiddles and the butterfly temporary, 16 words; `ob4`: 4 + 3 + 1). Per position it loads `2^k` elements, makes `k 2^(k-1)` butterflies at 3 operations each (2 where the twiddle is 1, below) and stores `2^k` elements; its position loop is written eight positions per pass (the positions of a pass are addressed by the position offset plus the constants 0 to 7 in the loads and stores themselves, and the offset advances once per pass), so its loop control is `F(cnt) = 1 + 3 floor(cnt / 8) + 2 + 3 (cnt mod 8) + 2` per call, not 3 per position; each load or store is 1 (base-plus-index, above). Charges per call, in stage C and in stage D: `ob128` `(2 * 2^k + 6) + 269 + 1600 cnt + F(cnt)` = `262 + 269 + 1600 cnt + F(cnt)`, `ob64` `134 + 139 + 704 cnt + F(cnt)` (the 127 or 63 twiddle loads of the call at 2 each with the address operation, 3 control operations and 2 per layer after the first: `269 = 254 + 3 + 12`, `139 = 126 + 3 + 10`; per position `2^k` loads and `2^k` stores and `k 2^(k-1)` butterflies at 3: `1600 = 256 + 1344`, `704 = 128 + 576`), `ob32` `70 + 34 + 304 cnt + F(cnt)`, `ob16` `38 + 18 + 128 cnt + F(cnt)`, `ob8` `22 + 10 + 52 cnt + F(cnt)`, `ob4` `14 + 6 + 20 cnt + F(cnt)`, where the first term is the call charge above, the second (`2^k + 2`) for `ob4` to `ob32` is the `2^k - 1` twiddle loads of the call at 1 each and 3 control operations, and for the radix-3 stage and a one-layer remainder `ob3` `12 + 7 + 22 cnt + F(cnt)` and `ob2` `10 + 5 + 11 cnt + F(cnt)` (their loads and stores 2 each with the address operation), and each call adds 3 for the call loop (a run of `L` layers is cut into passes of at most seven layers by the split of least charge, a dynamic program over the layer boundaries on the charges above at the run's row count and positions, a constant of the algorithm for each run). An outer transform of stage D of `n = 2^a` or `3 * 2^a` points at `cnt` positions is its twiddle table of `n` entries (3 operations each), for `3 | n` the radix-3 stage (`n / 3` calls of `ob3`), and on each of its 1 or 3 rows its `a` radix-2 layers cut into passes of at most seven layers by the split of least charge (4.2), each pass with its call charges and its call loop as above. The four 256-bit constants of the radix-3 stage (`W3[1]`, `W3[2]` and the two constants `CH`, `DL` of its position kernels) are loaded into four registers once per call of a region driver of the stage (4 loads with their address operations, 8 operations) and used from the registers; the position kernels of the stage use at most 10 words of the file for their own data, so with the 4 constants they use at most 14 of the 256 words. Twiddle 1 in the column kernels (the convention of the fused leaf pass above and of 1aa56884: a butterfly whose twiddle is 1 is its addition and subtraction, 2 operations): a column pass of `k` layers on a row of `2^a` points runs from the large-span end (forward) or towards it (inverse), and the butterflies with twiddle 1 of its layers are those at offset 0 of each block, `2^j` in its `j`-th layer, all in the call at offset 0 of each block (`2^k - 1` per position; `2^n - 1` per position over a run of `n` layers of a row); that call is a straight-line variant of the kernel without their multiplications, 1 operation less per such butterfly and position and 3 control operations more per such call. In the two-layer passes at the small-span end (the `ob4` pass of an inner transform, `ob4m` and the two boundary passes of 4.6) 3 of the 4 butterflies of each position and direction have twiddle 1 (both of the layer of span 2, one of the layer of span 4): 3 operations less per 4 points and direction.
* random words: the cost model's random-word primitive (an independent uniform 256-bit word) is one operation per word. The word of a draw is also loaded, stored into the cell `y` of the draw and addressed (one load, one store and three control operations), 6. A draw is that word (6), the reduction modulo `p` (three steps each of a comparison, a conditional branch and a field subtraction, 9, with the loop control of three iterations, 11), the conversion of the result to the internal representation (1), the entry (2) and the address of `y` (2): 31 operations. The shift of an isolation round is also tested for zero (5 operations) and, if zero, replaced by 1 (2 operations).
* the bit loops of inversion and exponentiation executed outside stages with a per-operation rule: 2,310 control operations per inversion.
* small-degree work in the line setup, the schoolbook `Z^((p-1)/2)` for `d <= 40` and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 6 control operations.
* the line evaluations of stage B and of the stage-F scan of 4.3G: each one execution of the program `L` of Appendix L, `387` operations on registers (Appendix L.3). The two reference hashes of stage G are charged as in row G. Nothing is charged as a unit.
* Montgomery conversions: every conversion of an integer to or from the internal representation (for example the word converted in a draw, the exponent in the Taylor shift, the constants of the twiddle setup, the inputs of the two reference hashes and the six conversions of the output in stage H) is one Montgomery multiplication and is charged as one field multiplication. The constants of the permutation are stored in Montgomery form and need no conversion.
* output (stages H and I): in stage H the answer (two pairs, the digest and the centre) is converted out of the Montgomery representation (6 multiplications) and encoded as 64 hexadecimal digits each at 12 operations per digit and 5 per call. Stage I charges everything after the last step of the algorithm: the formatting of the report, 400 operations per byte of a buffer of 8,192 bytes (a decimal digit costs at most 44 operations, a copied byte at most 10, a conversion at most 150), 20,000 operations of report loops, 100 for the entry and the length check, one write system call at `10000 + 8 * 8,192` and one exit system call at 10,000 (a system call is 10,000 operations plus 8 per byte copied), and the bookkeeping of the stage (2 * 1,000).
* allocation: every array is taken from one preallocated arena; a block is a 64-byte header plus the payload rounded up to a multiple of 64 bytes (`need` bytes), and `need` decides the allocator. A block of more than 2^54 = 18,014,398,509,481,984 bytes comes from the pool, one region with two ends: its blocks follow each other in address order, each with a header (size, size of the previous block, in-use flag), no two free blocks are adjacent, and the unused middle between the two ends is one free block. Each allocation statement of the program uses one end of the pool, a constant of the statement: the statements (`g` of stage A, the block array of stage B, `MU` and `Y`, the work arrays of the Newton products, of a squaring step (in a chunked product of a squaring step, all its arrays except the accumulators of the square `R^2`, which use the low end) and of a shift, and the results inside the half-gcd: the quotient and remainder of a node and of the outer loop, the outputs of apply_inv, of the matrix products and of mul_add_q2, every allocation of the lean stage D (`ld_new`, all sites `# pool:H`, including the working arrays of its block products), and the reversed `g` and the operand rev(X^v P1) of stage C step 1 (4.6)) use the high end, every other statement the low end, except that the copies of the remainders returned by a node that applies its second matrix (4.4, step (6)) are taken from the low end. A low request walks the blocks upward from the bottom of the pool, a high request downward from the top (the two sizes in the header give both neighbours, so the two walks are the same code mirrored); it takes the first free block with at least `need` bytes (the unused middle is the last block of either walk) and cuts the block from the side nearest its own end, and the rest stays a free block when it is at least 128 bytes (else it belongs to the block); a free merges the block with a free neighbour on either side, the unused middle included, the same code for both ends. Since no two free blocks are adjacent and a walk ends at the middle, a walk examines at most 2 P + 1 blocks, P the live blocks on its side of the pool, and one block examined is 13 operations (two comparisons with branches, two loads, the advance). A block of at most 2^54 bytes comes from the slab classes: the class `j` is the least `j >= 7` with `2^j >= need`, a slot is `2^j` bytes; a request takes the first slot of the free list of its class, else a new slot from the end of the slab area, and writes the class and the in-use flag into the header; a free puts the slot on the free list of its class. The allocators are charged per executed load, store, comparison, branch and address computation, inside the stage rows: a request of the pool 97 operations besides the walk (the statement that calls the allocator, the set-up, the split, the header stores, and a flat 64 for the statistics) and 13 per block examined, a request of a slab class at most `126` (the statement that calls the allocator, the class `j` by a binary search over 7..63 in 6 steps of 6 operations, the pop or the bump, the two header stores, and a flat 64 for the statistics), a free 81 for a slab block and at most 105 for a pool block (a free tests the size of the block to choose the allocator, in place of the test for a null pointer, which the program never needs). Every allocation of the walk is charged `1 + 120 + 13 (2 L + 1)` with L the live blocks at that point, which covers the pool (P <= L, the 97 operations and 13 per block examined) and the slab path (at most `126 <= 1 + 120 + 13` operations), and every free 105 (550 per allocation and 105 per free at 16 live blocks in stage E). The memory of both allocators is the arena of section 7.
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
Otherwise, `k1 = ceil(k/2)` (or the split of 4.4.2 item 1; `k1 = floor(n/2)` if `2 k1 > n`), `s = n - 2 k1`: (1) `R1 = hgcd(a quo x^s, b quo x^s, k1)` (the top parts, matrix wanted); (2) `(c, d) = R1^{-1} (a, b)` by NTT products (`apply_inv`): `c = s (r22 a - r12 b)`, `d = s (r11 b - r21 a)`, `s = (-1)^h`, evaluated cyclically on `3 * 2^j` or `2^j` points, at least the output length `la - h` (the high coefficients of `c` and `d` cancel, so the cyclic result is exact; 4.4.1 item 7); the Good-Thomas rows are processed one at a time, and in each row `a` and `b` and each of the four matrix entries are transformed once (six forward transforms of a row) and the two output rows are inverse transformed (`conv_bilin_otf`), the sign of each output being absorbed in the scale factor `1/N`; (3) if `d = 0` or the next quotient degree `deg c - deg d` exceeds `k - d_1`
(`d_1 = deg R1`) return `R1` and `(c, d)`; (4) divide `c = q d + e` (`divrem_any`); (5) `k3 = k - d_1 - deg q`, `s3 = deg d - 2 k3`; if `s3 > 0`, `R2 = hgcd(d quo x^s3, e quo x^s3, k3)` (the top `2 k3 + 1` coefficients of `d` and the coefficients of `e` of the same degrees, read in place, matrix wanted), otherwise the call runs on `(d, e)`; this is the same top-coefficient lemma that step (1) uses (the quotients of a pair whose degrees sum to at most `k3`, and the stopping test, depend only on those coefficients; von zur Gathen and Gerhard, Modern Computer Algebra, chapter 11; the same truncation as bradcush 1aa56884, its lemma 4.4), and 1aa56884 (its Appendix G.3) runs the node with and without it against plain Euclid; (6) only if the caller wants the pair, `(c', d') = R2^{-1} (d, e)` by `apply_inv`, each moved into an array of its own length; return `R1 Q R2` (matrix products by NTT, only if the matrix is wanted; the product of the two 2 x 2 matrices transforms each of the eight entries once per row, with the right-factor entries of one column pair held and the left-factor entries streamed, and inverse transforms the four outputs, `conv_bilin_otf` again).
The outer function `poly_gcd_own` repeats, while `deg b > 0` and `n = deg a > 192`: `(c, d) = hgcd(a, b, floor((n+1)/2))`, one division `c = q d + e` and `(a, b) := (d, e)`; at or below 192 it runs classical Euclid; at the end it scales the last nonzero remainder to be monic (one inversion, `deg + 1` multiplications). With `H-NORMAL` (9.5) stage D runs the normal-sequence procedure of bradcush (entry e6dcb600): every division tests that its quotient has degree 1 and every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter ; a zero remainder met inside hgcd or in the division of the outer loop also ends the trial (ABORT); on any other case the trial ends (ABORT) and the next centre is drawn (section 6.3).

**Division.** `divrem_any(a, b)`, `la - lb + 1` quotient coefficients `kq`: if `kq <= 64` or `lb <= 64` schoolbook (`poly_divrem_naive`); otherwise (`divrem_fast`) the reversed Newton identity: `q_rev = (a_rev * inv(b_rev mod x^kq)) mod x^kq`, `q = reverse(q_rev)`, `r = a - q b` (low `lb - 1` coefficients), with
the reciprocal by Newton iteration `g_{2t} = g_t - x^t (g_t * mid(f g_t))` and all products by `poly_mul`.

#### 4.4.1 The lean stage D (this entry; the stage D of bradcush 1aa56884, its section 4.4 and lemmas 4.4 and 4.8, credited)

This entry runs the half-gcd above with six changes from 1aa56884 (items 1-6) and the scaled steps and short transforms of weijiekoh a78f526e (item 7), all credited in the dependencies and the note, and an eighth, the apply plans of 0xplemonade ff21bd28 (item 8; credited likewise), charged by this model's rules of 4.2 and 4.5. Items 1-6 change where arrays live and which coefficients are formed, never a quotient: every quotient used is a quotient of the whole pair (lemma 4.4 above, and lemma 4.8 below). Item 7 multiplies remainders and matrices by nonzero constants only, which changes no quotient degree and no test.

1. *The base case in place.* For `k <= 96` the two remainders are two arrays and a division step with a quotient of two coefficients is one pass `r_k = a_k - q0 b_k - q1 b_(k-1)` written over the array of `a`; the roles of the two arrays swap. The four matrix entries are four arrays of `k + 2` elements allocated once, and `R := R Q` writes `r11 q + r12` over `r12`. No array is allocated or freed inside the loop.
2. *Matrix-only calls.* A call returns the reduced pair only when its caller wants it: the calls of the Euclid driver `poly_gcd_own` and, inside them, the second calls with `s3 <= 0`. Every call inside a first call, and every truncated second call, returns its matrix only.
3. *Windows.* In a node that wants its matrix only and has `s3 > 0`, the block products of `apply_inv` (or the plan of item 8) form only the top window of `c` and `d`: the coefficients of degree at least `s3 - 1` (lemma 4.8 (a)). Such a node tests that the coefficients of `c` and `d` at their normal leading degrees `la - h - 1` and `la - h - 2` are nonzero (2 tests, charged) and ABORTs otherwise, so it never reports a shorter remainder from a window.
4. *The two tests and the ABORT.* At every division the quotient test (the quotient has degree 1) and after every recursive call and every call of `poly_gcd_own` the return test (the call returned exactly its parameter as degree count; a zero remainder inside hgcd or in the outer-loop division also ABORTs), 2 operations each, charged wherever they execute. If a test fails the trial ABORTs: the allocator is reset to its state after initialisation (`1,000` operations, charged in section 6) and the next centre is drawn. On the normal remainder sequence neither test fails (6.3), so every division of stage D is the one-pass division by a quotient of two coefficients and the Newton division is never run.
5. *The top node in pieces.* Stage C leaves `g` and `R` in two pieces each, the coefficients `[0, cut)` and `[cut, l)` with `cut = 2,793,967,726,031,273,984`. The first call of `poly_gcd_own` frees the high pieces of `g` and `R` right after its own `apply_inv`; the pair `(c, d)` is then formed from the low pieces only (`c` first, by the block products of 4.5 with the window `[0, lc)`, `lc = m + 1 - k1`; then `r22` and `r12` are freed; then `d`; then `r11`, `r21` and the low pieces are freed). The pair `(d, e)` of the second call is written as two pieces at `cut2 = deg d + 1 - k3` and handled the same way.
6. *Block products of stage D.* Each product of apply_inv (unless the apply runs a plan of item 8), of the top node and of mat_mul uses the cheapest of the single transform, scheme (a) at block length 2^31 (one row of passes of 2^32 points) and scheme (c) at the block length 2^b of least charge (b = 6..31, transforms of 2^(b+1) points). The number of chunks is the least power of two that brings a chunk form to at most `m // 16` elements. The outputs are allocated first at their true lengths, the chunks accumulate into them, the working arrays follow and are freed at the end, and the operands are freed after the last chunk. This replaces, for stage D, the Blocks, Choice, stage-D and Scaling bullets of 4.5. There is no placement pass in stage D: each output of a scheme (c) product is untwisted straight into its window with the scaled weight `sign / (NB n2) * w^(-e)` (the sign of the output, the factor `1/NB` of the unnormalised inverse transform and `1/n2` of the outer transform applied here), charged 15 operations per product (the scale and the weight base), 7 per untwist call (the table entry and the scale loaded and the result stored, each 2 with its address operation, and one multiplication) and the chunk and outer-point loops; at r = 21 this is 27,066,888,835,362,197,752 operations per trial (650,521,035 scheme (c) products, 2,095,485,578,078,055,494 untwist calls), included in row D. The outer transforms of scheme (c) use the column kernels of stage C (4.2: `ob128`, `ob64`, `ob32`, `ob16`, `ob8`, `ob4`, `ob2` across the outer points, `ob3` for the radix-3 stage, with the stage-C charges and base-plus-index loads and stores), and the assembly of a chunk, the untwist into the window and the fold of an outer point into the row of its chunk are loops of eight elements per pass (4.2), with 1aa56884's conventions for these three primitives (credited). The kernels `ocp`, `oax` and `ozf` of 4.5 are not used in stage D. The choice between the single transform and the block products counts every charge of each path, including the allocations and frees the block path adds.

7. *Scaled steps and short transforms (the method of weijiekoh a78f526e, its section 4.4 `mat_mul` and `mat_apply`, credited).* (a) A division step whose quotient has degree 1 and whose divisor `V` has at most 2,048 coefficients is the scaled step `e = s U - (A x + B) V`, with `v = lc(V)`, `s = v^2`, `A = v lc(U)`, `B = v U_(n-1) - lc(U) V_(d-1)`: (`V_(d-1) = 0` when `d = 0`), and the coefficients of degrees `n` and `n - 1` cancel, so `e = s r` with `r` the exact remainder, and no field inversion is made. Per remainder coefficient the pass makes 3 multiplications (`s U_k`, `A V_(k-1)`, `B V_k`) in place of the 2 of the base case of 4.4, and the matrix update `R := R [[A x + B, 1], [s, 0]]` one more per matrix coefficient (`s r12`). Each step multiplies the new remainder by its own nonzero constant `s` (`v != 0`), so every remainder and every matrix entry is the exact one times a product of such constants, and `det R` is `(-1)^h` times a nonzero constant; with the sign `s = (-1)^h` of 4.4 step (2), `apply_inv` returns `(c, d)` each times a nonzero constant. So every quotient degree, every test of item 4 and every window of item 3 is unchanged, and the gcd, made monic at the end, is the same. A divisor of more than 2,048 coefficients takes the exact step. (b) A product of stage D made by a single transform (at most `3 * 2^32` points) uses the cheaper by charge of the transform of `3 * 2^a` points and the plain transform of `2^a` points (one row of radix-2 passes, no radix-3 stage; `2^32` divides `p - 1`). (c) In `apply_inv` the transform length is taken from the output length `la - h` of `c`, not from the operands: `r22 a - r12 b` is a nonzero multiple of `c` as a polynomial and `c`, `d` have degree below `la - h`, so the product modulo `x^N - 1` is exact for `N >= la - h`; an operand longer than `N` is folded modulo `x^N - 1` as it is read in. Copy-in is charged 7 operations per coefficient and row (a load and a store, each with its address operation, and the loop step), the zero fill of the rest of a row 5 per position (a store with its address operation and the loop step) and the fold 10 per folded coefficient and row read (a load, an addition, a store and the loop step).
8. *Apply plans (the direct whole-pair and fixed-slot apply plans of 0xplemonade's entry `ff21bd28`, read as text, re-implemented and charged in this cost model).* An apply `(c, d) = adj(R1)(a, b)` of steps (2) and (6) of 4.4 (`c = s (r22 a - r12 b)`, `d = s (r11 b - r21 a)`, `h = d_1`, `lc = la - h` and `ld = lc - 1` coefficients; in a node of item 3 only the coefficients from `w = s3 - 1` on) runs either the apply of items 6 and 7 (a)-(b) or one of the two plans below, whichever has the smaller charge. The live peak of stage D with the plans is 454,126,002,273,328,890,624 bytes, below that of stage C (476,837,265,213,765,335,104 bytes), so no plan raises the extent of the pool (7). The lengths, budgets and windows of every call are fixed on the normal sequence (6.3), so this choice is a constant of the algorithm for each call of the walk: at r = 21, of the 4,275 distinct apply calls of the walk, 1,775 run a plan (1,467 direct, 308 fixed-slot; 302 of them on a window). A plan uses one transform size `N = 3 * 2^e`; both forms are priced at every `e = 2, 3, ...` up to the first with `N >= lc - w + h` (8 control operations and the plan set-up per size), and the cheapest is run; 80 operations of entry, the plan scale `1/N` (plan_invN, as for every transform) and 22 for the two length checks. A transform of an array of `l <= N` coefficients is `6` plus the radix-3 input stage over the `l` coefficients plus three rows of block-form passes (4.2); an inverse is `3` plus three rows of inverse passes plus the radix-3 output stage over the coefficients formed; the scaling by `s/N` of `t` outputs into their array is `8t + 5` (a load, a multiplication, a store and the loop step per coefficient). Both forms first transform the nonzero entries of `R1` into spectra of `N` points; `R1` is freed then when the call consumes it.
(i) Direct whole-pair (no window, `N >= lc`): `a` and `b` are folded modulo `X^N - 1` (10 per coefficient beyond `N`: two loads, the addition, the store, the loop step) and transformed into the operand spectra `A` and `B`; one pass over the `N` points forms `C = r22 A - r12 B` over `A` and `D = r11 B - r21 A` over `B` (per point six loads with their address operations, four multiplications, a subtraction and an addition, and the two stores at the addresses of the loads of `A` and `B`: 20; the eight-element loop of 4.2, `2 + for8(N)`); the two inverses form the first `lc` and `ld` coefficients and the scaled outputs are written. Since `deg c, deg d < lc <= N` the cyclic results are exact.
(ii) Fixed-slot (`B = N - h > 0`): the outputs from `w` (`w = 0` without a window) are cut into `nb = ceil((lc - w) / B)` blocks of `B` coefficients, handled from the highest to the lowest (`3 nb + 6` of loop control). Block `i` covers the outputs `[s, e)`, `s = w + i B`, `e = min(s + B, lc)`: it transforms the windows `[max(0, s - h), e)` of `a` and of `b` (at most `N` coefficients) into `A` and `B`, forms `C` and `D` in one pass over the `N` points (charged 24 per point: six loads and two stores with their address operations, four multiplications, a subtraction and an addition, 22; `2 + for8(N)`), inverse transforms both (all `N` outputs; the first block of an apply without a window only its outputs) and writes the scaled outputs `[s, e)` of `c` and `[s, min(e, ld))` of `d`; 20 of control per block. A window of `v <= N` coefficients times an entry of at most `h + 1` coefficients has at most `v + h` coefficients, so the cyclic wrap of length `N` reaches only the positions below `v + h - N`; the outputs of block `i` sit at the positions from `min(s, h)` of its window on, and `v + h - N <= min(s, h)` since `e - s <= B`, so they are exact. The form is used when the first block that reads a full window of `N` coefficients has index at most 8 (the blocks from it to the last but one are charged alike).
The outputs are written over `a` and `b` when the caller owns both and there is no window (the direct form reads `a` and `b` before it writes; a fixed-slot block writes `[s, e)` and the blocks after it read only positions below `s`), else into two arrays of `lc - w` and `ld - w` elements. Memory of a plan: the four matrix spectra and the two operand/output spectra, six arrays of `N` elements (lean stage-D allocations, 4.2), besides the pair and the outputs; no chunk form or accumulator.

**Lemma 4.8 (windows and pieces; 1aa56884's lemma 4.8).** (a) In a node that wants its matrix only, with `s3 > 0`, the rest of the node reads `c` only at degrees at least `s3` and `d` only at degrees at least `s3 - 1`. (b) In the top node, after the first call's `apply_inv` no operation reads `a` or `b` at degrees at least `cut`, and the low `lc` and `lc - 1` coefficients of `c` and `d` computed from `a mod X^cut` and `b mod X^cut` are the `c` and `d` of step (2); the same holds for `(d, e)`, `cut2` and `(c', d')`.
*Proof.* (a) The stopping test and the quotient test use `deg c` and `deg d`; the quotient `q = q1 x + q0` uses the top two coefficients of `c` and of `d`; and `e_i = c_i - q0 d_i - q1 d_(i-1)`. The second call reads only `d quo x^s3` and `e quo x^s3`, that is `d_i` and `e_i` for `i >= s3`, hence `c_i` for `i >= s3` and `d_i` for `i >= s3 - 1`. After it the node needs only `R1`, `q` and `R2` (and `s3 - 1 <= deg d - 1`, so the top two coefficients are inside the window). (b) The first call reads `a quo x^s` and `b quo x^s` and, after its `apply_inv`, only its own arrays; the top node then reads `a` and `b` only in step (2). For `i < lc <= cut` the coefficient `i` of `r22 a` is `sum_j r22_j a_(i-j)` with `i - j < cut`, so it equals the coefficient `i` of `r22 (a mod X^cut)`; `c` has length `lc`, so it is the low `lc` coefficients of `s (r22 (a mod X^cut) - r12 (b mod X^cut))`, and likewise `d`. For the second call, `cut2 = deg d + 1 - k3 >= lc'` with `lc' = deg d + 1 - h3` and `h3 = k3` on the normal sequence. QED

The charges of these steps are this model's (4.2, 4.5), not 1aa56884's: with 1aa56884's own conventions the same walk gives its published row D to the unit (`1,062,106,645,154,198,605,714,641` at r = 21, recomputed in our model with their conventions switched on), and with this model's primitives, with 1aa56884's conventions for the four primitives of item 6, it gives `1,057,792,061,049,205,724,279,457` (the row D of our entry 3ecf886c); item 7 lowers it to row D of section 6.

#### 4.4.2 Budgets of the form `2^i - 1` and the inversion-free node on three rows (this entry; the half-gcd of bradcush 4bcabff8, credited, as ported in our r = 3 entry bcf8e01c)

This entry runs the half-gcd of 4.4.1 with two changes. Neither changes a quotient, the stopping tests or the result: every call returns the matrix of the first `h` quotients of its pair, `h` equal to its parameter on the normal sequence.

1. *Budgets `2^i - 1`.* A node of parameter `k = 2^j - 1` gives its first call the parameter `k1 = 2^(j-1) - 1`; a node of any other parameter `k < 2^53` gives it `k1 = 2^(b-1) - 1`, `b` the bit length of `k` (the aligned split of akki-rock05's entry `4cb15141`, its 4.4.3 item 1, read as text and charged in this cost model; for `k <= 2^46` this is the least `2^i - 1 >= ceil(k/2)` of `213552fe`, so the split changes only for `2^46 < k < 2^53`); a node of parameter `k >= 2^53` splits at `ceil(k/2)` as before (the top node of 4.4.1 item 5, its pieces and `cut` are unchanged); in every case `k1 = floor(n/2)` if `2 k1 > n`, as before, and the second call takes the parameter left over, `k3 = k - h1 - deg q`, as in 4.4 step (5). The top-coefficient lemma of 4.4 steps (1) and (5) holds for every `1 <= k1 <= k`: the quotients of the first call are fixed by the top `2 k1 + 1` coefficients of the pair, and the second call continues the same sequence (von zur Gathen and Gerhard, Modern Computer Algebra, chapter 11; the split point is free), and only the cost depends on it. On the normal sequence the second call of a node of parameter `2^j - 1` has parameter `2^(j-1) - 1` too, so the first call of every node of parameter below `2^53`, and every call under it, has a parameter `2^i - 1`.
2. *The inversion-free node.* A call that wants its matrix only (the first calls and the truncated second calls of 4.4.1 item 2) with parameter `k = 2^j - 1`, `7 <= j <= 31`, reads the top `2^(j+1)` coefficients of its pair in place (charged as a full window) and runs bradcush's inversion-free half-gcd (entry 4bcabff8, with the transform reuse of b30de9bf; read as text only, ported and charged in this cost model as in our r = 3 entry bcf8e01c). Remainders are kept up to nonzero constants by pseudo-division, `lc(b)^2 a = Q b + e` with `Q` of degree 1 on the normal sequence: this is the scaled step of 4.4.1 item 7 (a) (`sigma = lc(b)^2`, `Q = A x + B`), so every remainder and matrix entry of the node is the exact one times a nonzero constant, `det` of its matrix is `(-1)^h` times a nonzero constant, and the argument of 4.4.1 item 7 (a) applies to it and to every pair `apply_inv` forms from it. A node of parameter `2^j - 1` makes two child calls of parameter `2^(j-1) - 1`; its products run on `3 * 2^(j-1)` points, the rows `Y - 1`, `Y + 1`, `Y - i` (`Y = X^n`, `n = 2^(j-1)`), each a transform of `n` points in the block form of 4.2 after a twist, joined by a 3-row CRT for `(c, d) = adj(M1)(a, b)` on the window; then the pseudo-division and the product `M = M1 [[Q, 1], [lc(b)^2, 0]] M2` on the two rows `Y - 1`, `Y + 1` only (`2n` points; 2-row CRT `lo = (u + v)/2`, `hi = (u - v)/2` with the `1/2` folded into the `1/n` of the inverse, 10 operations per point). The product needs no third row: on the normal sequence every quotient has degree 1 and the scale of a step is a constant, so a matrix of `s` steps has entries of degree at most `s`; the entries of `M1`, `M2` (budget `n - 1`) have degree at most `n - 1` and those of `M` at most `2n - 1 < 2n`, and the values on the `2n` points with `X^(2n) = 1` determine `M` exactly (the 2n-point product of van der Hoeven, arXiv 2212.12389, Prop. 7, here without its leading-coefficient correction). A node reaches its product only after the quotient tests of its children and of its own pseudo-division have passed (6.3), so the degree bound holds whenever the product runs. These `2n` points are the row `Y' - 1` (`Y' = X^(2n)`) of the parent, so the values of `M` there are returned to the parent with no transform; each child returns the row `Y - 1` values of its matrix, the row values of `M1` are kept from the apply and reused in the product, and of `M2` only the row `Y + 1` is transformed (both rows when its children are base cases, which return coefficients only). The twist of the row `Y - i` needs a root of unity of order `4n = 2^(j+1) <= 2^32`, the 2-part of `p - 1`, hence `j <= 31`. The base case (parameter 63) runs two remainder steps per pass over its window. Every pseudo-division tests that its quotient has degree 1 and every call tests on return that it removed exactly its parameter (2 operations each); on any other case the trial ends (ABORT, 6.3). The node returns its matrix in coefficient form in four arrays of `2^j + 1` words (entries of lengths `k + 1`, `k`, `k`, `k - 1`), which the caller uses as in 4.4.1.

**The two loops of the node (this entry).** *Fold.* The window of `a` (`4n'` coefficients, `n' = 2^(j-1)`) and the window of `b` (`4n' - 1`) are read once and the three rows `Y - 1`, `Y + 1`, `Y - i` are formed in one loop of eight positions per pass (4.2), position by position: `a_0 + a_2` and `a_1 + a_3` (2), their sum and difference for the rows `Y - 1` and `Y + 1` (2), and `(a_0 - a_2) + i (a_1 - a_3)` for the row `Y - i` (4, with the multiplication by `i`): eight field operations, four loads and three stores, each load and store with its address operation, 22 per position, and `2 + for8(n')` for the loop (`for8` as in 4.2), once for `a` and once for `b`; the twist of the rows `Y + 1` and `Y - i` by their running factors (2 per point and row) and the three forward transforms follow. This is charged in place of the row-by-row formation of the rows from the window, which per row copied the first chunk (4 per coefficient, and `3 n' + 2` of loop control) and folded the other three chunks into it in one accumulating loop (7 per coefficient, 8 on the row `Y - i`, and `3 (3 n') + 2` of loop control). *Two-output pass.* On each of the three rows of the apply one pass forms `C = r22 A - r12 B` and `D = r11 B - r21 A` from the row values of `a`, `b` and the four entries of `M1`; and in the product `M = P M2`, `P = M1 [[Q, 1], [b^2, 0]]`, on each of the two rows `Y - 1`, `Y + 1` one pass per column of `M2` forms the two entries of that column of `M` from the four entries of `P` and the column. Each is the two-output pass of 4.4.1 item 8 (i): six loads with their address operations, four multiplications, two additions or subtractions and two stores at the addresses of the loads of the two operands, 20 per point, and `2 + for8(n')` for the loop. This is charged in place of two pointwise passes per output. The bodies of the two loops, eight positions each, `8 * 22 + 3 = 179` and `8 * 20 + 3 = 163` instructions (3 of loop control), are counted as code in 7(a). Neither loop adds an array: the fold fills the six row arrays of the apply and a two-output pass writes over its operands, the arrays counted in the node arena. 0xplemonade's entry `8b1eb62a` (r = 7), whose note itemizes the node as fused two-output pointwise rows, was read as text and prompted charging the maps as two-output passes, priced here by the direct apply row of `ff21bd28`; no number or program is taken from it.

Charges (the rules of 4.2): for the rows that the two loops above do not form (the four entries of `M1` and of `M2` on their rows), a row of a product costs the copy of its window (4 per coefficient: a load and a store, each with its address operation), the zero fill of the rest of the row (2 per slot), the fold of a window longer than the row (7 per coefficient, 8 on the row `Y - i` with its multiplication), the twist (2 per point on the rows `Y + 1` and `Y - i`: the running factor and the multiplication), the forward transform of `n` points in the block form of 4.2 plus 10; the pointwise products are the two-output passes above; the inverse transform of a row plus 10, with `1/n` (row `Y - 1`) or the untwist times `1/n` (2 per point) fused into the CRT, which costs 22 per point (10 field operations, 3 loads, 3 stores, each load and store with its address operation); every loop carries the loop control of 4.2 (`3 n + 2`). The pseudo-division costs 30 and 13 per coefficient of the window the second child reads; the values of `Q` and of `M1 Q` cost 25 per point on each row of the product, which has the two rows `Y - 1`, `Y + 1` only (its 2-row CRT 10 per point); a node costs 40 for its call, 14 bump-arena operations (the allocations and releases of its working arrays) of 10 each, and its return tests 4. The scales `1/2^a` (`a <= 30`) are a table of 31 words built at the entry of stage D (one allocation; `1/2 = (p + 1)/2` an immediate, 29 multiplications, 30 stores, the loop), and the twist roots come from the twiddle table of 4.2. A matrix-only call on the node costs 40, the four allocations of its matrix and the allocation and release of its bump arena (the allocator of 4.2), and the node, `node(j) + 10`; the arena of the node holds at most `34,359,738,112` words (`j = 31`), far below the live-set peak (section 7). Per trial on the normal sequence:

| j | parameter `2^j - 1` | `node(j) + 10` |
|---:|---:|---:|
| 7 | 127 | 279,271 |
| 8 | 255 | 679,441 |
| 9 | 511 | 1,632,675 |
| 10 | 1,023 | 3,830,087 |
| 11 | 2,047 | 8,828,015 |
| 12 | 4,095 | 20,078,943 |
| 13 | 8,191 | 45,182,815 |
| 14 | 16,383 | 100,790,911 |
| 15 | 32,767 | 223,200,735 |
| 16 | 65,535 | 493,677,197 |
| 17 | 131,071 | 1,084,843,273 |
| 18 | 262,143 | 2,370,555,169 |
| 19 | 524,287 | 5,155,020,401 |
| 20 | 1,048,575 | 11,162,232,369 |
| 21 | 2,097,151 | 24,078,366,417 |
| 22 | 4,194,303 | 51,763,618,097 |
| 23 | 8,388,607 | 111,242,448,351 |
| 24 | 16,777,215 | 238,305,077,339 |
| 25 | 33,554,431 | 509,030,637,171 |
| 26 | 67,108,863 | 1,084,462,510,019 |
| 27 | 134,217,727 | 2,304,897,176,451 |
| 28 | 268,435,455 | 4,888,080,423,971 |
| 29 | 536,870,911 | 10,345,416,554,115 |
| 30 | 1,073,741,823 | 21,893,107,598,129 |
| 31 | 2,147,483,647 | 46,240,693,149,101 |

Row D of section 6, `477,848,936,324,260,928,287,843` operations, is the walk of stage D (4.4, 4.4.1, 4.4.2 and this section) with these calls on the normal sequence.

### 4.5 Products longer than `3 * 2^32` points (block mode)

The bullets of earlier entries on the coefficient-domain stage C are not repeated: stage C is 4.6, which uses this section only for the Newton reciprocal and the q product of its step 1. Stage D uses 4.4.1 item 6.

At this r the transforms of 4.3 and 4.4 would have up to `3 * 2^62` points (the square of stage C, `2m - 1 = 7,450,580,596,923,828,123` coefficients) and `3 * 2^61` points (`m + 1`, the products by `g`, and the products by the half-gcd matrices, whose entries have several blocks). The field has no root of unity of such an order (`p - 1 = 2^32 * 3 * q'`). Grok (xAI), job 140, determined the cost of multiplying polynomials of lengths `3 * 2^34`, `3 * 2^36` and `3 * 2^38` over this field and recommends the block NTT (its scheme (a)) for `3 * 2^34` and `3 * 2^36` and the same split with an outer transform across the blocks (its scheme (b), the outer FFT) for `3 * 2^38`: a product is cut into blocks, the blocks are transformed with the longest available transform, and the products of block spectra are summed in the transform domain. Grok job 140 checked both schemes against schoolbook on random products of length `2^14` with a transform cap of `2^10` (every coefficient equal, and the counted multiplications and additions equal to its formulas, `551,999` and `890,850` for scheme (a)). Both schemes are the same operations at every block count; at the lengths of this r we apply them by the charging rules of 4.2. The schemes, as used by the algorithm:

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

**Points.** Here `h = 2^32` and `K` is the number of cosets of each point set (not the number of centres of 4.1). `H` is the subgroup of order `h` of `F_p^*`, with generator `omega = 5^((p-1)/h)`, which has order `h` because 5 is a non-square. Put `u_k = 5^k`, `C_k = u_k H` and `n_k = u_k^h = z^k` with `z = 5^h`. `p - 1 = 2^32 * 3 * 463 * q1 * q2` with `q1 = 539,204,044,132,271,846,773` prime, and `z^((p-1)/q1) != 1`, so the order of `z` is at least `q1 > 2K`. Hence the nodes `z^k` (`k < 2K`) are distinct and the cosets `C_k` are pairwise disjoint (`C_j = C_k` if and only if `z^(k-j) = 1`). These three facts are checked by direct computation (Python standard library): `q1` is prime by a deterministic Miller-Rabin test with the bases up to 41 (valid for `n < 3.3 * 10^24`), `z^((p-1)/q1) != 1`, and `5^((p-1)/2) != 1`; all three hold. At r = 21: `m = 3,725,290,298,461,914,062`, `K = ceil((m + 1)/h) = 867,361,738`, `n1 = K h = 3,725,290,298,511,720,448 = m + 49,806,386`. Put `O1 = C_0 u ... u C_(K-1)` and `O2 = C_K u ... u C_(2K-1)`, `M(Y) = prod_(k<K) (Y - z^k)` and `P1(X) = M(X^h)`. `P1` has degree `n1`, is squarefree, has root set exactly `O1`, and on a coset `C_k` with `k >= K` it is the nonzero constant `M(n_k)`.

**Representation.** A polynomial `f` of degree `< n1` is determined by its values on `O1`, and also by its values on `O2`. Write `f = sum_(j<h) X^j F_j(X^h)` with `deg F_j < K`. Then `f mod (X^h - n_k) = sum_j F_j(n_k) X^j`, so the values of `f` on `C_k` are the transform of size `h` of `(u_k^j F_j(n_k))_j`. Each array holds the values coset by coset, in the output order of the inner transform. The inner transforms of the cosets of an array are made together, as column passes across the cosets (position = coset, stride `h`): the 32 layers in column passes of at most seven layers, split by least charge (4.2), in place on the array.

**Lemma 4.6 (the step).** Let `g` be monic of degree `m` with `g(x) != 0` on `O1`. Let `R~` have degree `<= m`, and let `u0` be the polynomial of degree `< n1` with `u0(x) = -R~(x)^2 / g(x)` on `O1`. Then `W = (R~^2 + u0 g) / P1` is a polynomial of degree `<= m - 1`, and `W = R~^2 P1^(-1) mod g`. On `C_k` with `k >= K`, its values are `(R~(x)^2 + u0(x) g(x)) / M(n_k)`. *Proof.* `R~^2 + u0 g` vanishes on the `n1` distinct roots of the squarefree `P1`, so `P1` divides it. Its degree is at most `max(2m, n1 - 1 + m) = n1 + m - 1` because `n1 >= m + 1`, so `deg W <= m - 1`. Modulo `g`, `W P1 = R~^2`, and `P1` is invertible modulo `g` because `g` has no root in `O1`. The values follow from `P1(x) = M(n_k)` on `C_k`. QED. So the invariant `R~_i = S^(e_i) P1 mod g` passes from step to step with `R~' = X^b W` (`e_(i+1) = 2 e_i + b`, `deg R~' <= m`). The same argument with `R~` in place of `R~^2` leaves the Montgomery form (step 7).

**Lemma 4.7 (extension).** Let `f` have degree `< n1`, with its values on `O1` given. The inverse inner transform of each coset gives `h u_k^j F_j(n_k)`. Fix a position `j`, write `F = F_j`, and put `s_i = F(z^i) z^(-i) / M'(z^i)` and `kappa(e) = 1/(z^e - 1)` for `1 <= e <= 2K - 1`. Then `F(z^(K+t)) = M(z^(K+t)) sum_(i<K) s_i kappa(K + t - i)` for `t < K`. *Proof.* `deg F < K`, so `F` is the Lagrange interpolant of its values at the `K` distinct nodes, and `z^(K+t) - z^i = z^i (z^(K+t-i) - 1)` with `1 <= K + t - i <= 2K - 1`. QED. The direction `O2 -> O1` is the same with the nodes `z^(K+i)`. The sum is a cyclic convolution of length `Lx = 2^31 >= 2K` with a fixed kernel, and no index wraps.

**The stage** (the eight steps of 1aa56884, with our parameters at r = 21). The exponent `E = (p-1)/2` starts from `S^v` with `v = 2^59`, a multiple of `h` below `m` (`VSHIFT = 2`: two more squaring steps and a shorter reciprocal), and runs `194` steps, `45` of them with `b = 1` (with the Graeffe prefix of 4.3G: exponent `(p-1)/2^32`, `163` steps, `45` with `b = 1`).
1. *Barrett start:* the reciprocal of the reversed `g` modulo `X^ell`, `ell = 576,460,752,353,229,875`, by the Newton iteration of 4.3 with the products of 4.5. Then `q = floor(X^v P1 / g)` by one product (`Kq = 134,217,729` rows).
2. *`g` on `O1` and on `O2`* by the chirp evaluation of section 3 (one convolution of length `Le = 3 * 2^30 >= 3K - 1` per position) and `2K` forward inner transforms.
3. *`R~_0` on `O2`:* `q` evaluated at the nodes of `O2` (`Lq = 2^30`), then `R2 := u_k^v M(n_k) - R2 * G2` pointwise. This gives the values of `X^v P1 - q g = X^v P1 mod g`.
4. *`R~_0` on `O1`:* an extension `O2 -> O1` (lemma 4.7).
5. *`-1/g` on `O1`* by Montgomery's batch inversion per coset in chunks of `2^16` elements (the `2^16`-element batch-inversion prefix of 0xplemonade's entry `ff21bd28`): per chunk the prefix products into one auxiliary array of `2^16` elements (a load, a multiplication, a store), one inversion with its zero test and the backward pass (two loads, two multiplications, the negation, a store), 9 of chunk control; 20 per coset. A zero prefix product means `g` vanishes on `O1`, and the trial ABORTs as in 4.4.1 item 4 (allocator reset, ledger row 'ABORT reset') after a prefix of the charged work; the probability is below `2^-98.6` with the Graeffe prefix (9.2(b)).
6. *The loop*, for each bit `b`: `R1 := R1^2 G1` (`u0` on `O1`); the extension `O1 -> O2`; `R2 := x^b (R2^2 + R1 G2) / M(n_k)`; the extension `O2 -> O1`. By lemma 4.6 the invariant holds after every step.
7. *Leaving the Montgomery form:* `R1 := R1 G1`, the extension `O1 -> O2`, `R2 := (R2 + R1 G2) / M(n_k)`. `R2` now holds `R = S^E mod g` (degree `< m`).
8. *Coefficient form for stage D:* `R2` and `g` are interpolated in place (inverse inner transforms, then two chirp correlations of length `Lx` per position), each into two pieces, the coefficients `[0, cut)` and `[cut, l)` with `cut = 2,793,967,726,031,273,984`, which the top node of stage D frees early (4.4.1, step 5).

**Kernels.** Every column pass of this section, the pruned first and last passes included, runs its position loop eight positions per pass with the control `F(cnt)` per call (4.2), not 3 per position. In the loop, the last two forward layers of the inner transforms, the pointwise step and the first two inverse layers are one column pass per boundary: on `O1` (`9 + 44 cnt + F(cnt)`) per position 4 loads, 4 butterflies, for each of the 4 elements a load of `G1`, a squaring and a multiplication, 4 inverse butterflies and 4 stores; on `O2` (`11 + 61 cnt + F(cnt)`, `27 + 70 cnt + F(cnt)` for `b = 1`) the same with the load of `1/M(n_k)` and per element the loads of `R2` and `G2`, a squaring, two multiplications and an addition (`b = 1`: the factor `u_k` and two more multiplications per element, and per call the four `omega^e` of its rows, each the product of one entry of each of two tables of `2^16` entries, `omega^e = T1[y] T2[x]` for the position `p = x 2^16 + y` with exponent `e = 2^16 rev16(y) + rev16(x)` in the bit-reversed output order of the inner transform, `T1[y] = omega^(2^16 rev16(y))`, `T2[x] = omega^(rev16(x))`: two loads with their addresses and one multiplication per value, 12 more per call than one load per value from a table of `h` entries, the 12 being in the constant `27`; the two tables are built at `10` per entry), within the 18 words. The extension is computed in a coset-major group buffer (`L` rows of `VCNT` positions) with column passes (`ob128`, `ob64`, `ob32`, `ob16`, `ob8`, `ob4`, `ob2` as the layer count needs; `ob3` for the radix-3 stage): the first forward pass reads the `K` input rows from the coset array with their factors and skips the zero rows; the last two forward layers, the product by the kernel spectrum and the first two inverse layers are one pass (`ob4m`, `13 + 36 cnt + F(cnt)`: 4 data words, 3 + 3 twiddles and 4 spectrum words); the last inverse pass forms and writes only the rows `K .. 2K - 1`, with their factors, into the coset array. Every column call of this paragraph also carries the call charge `2 * 2^k + 6` of 4.2 (`k = 2` for the boundary passes and `ob4m`), and its constant term is its twiddle, spectrum and factor loads at 1 each and its control operations.

**Charges** (the components sum to row C of section 6):

| component | operations |
|---|---:|
| inner transforms of the `K` cosets of one array, one set of column passes with `cnt = K` (4.2; 267,630,149,769.60 per coset), forward / inverse | 220,250,513,080,958,821,725 / 220,250,513,080,958,821,725 |
| geometric phase of one extension (286.255 per element of `n1`) | 1,066,384,080,489,337,615,634 |
| one extension with its `2K` inner transforms | 1,506,885,106,651,255,259,084 |
| one loop step, `b = 0` / `b = 1` | 3,036,354,785,665,833,992,104 / 3,044,736,688,854,665,232,296 |
| tables: `30 K` constants, the two `omega` tables of `2^16` entries, the kernel spectra | 160,701,861,630,150 |
| Newton reciprocal (step 1, with its allocations) | 5,108,848,687,687,972,370,219 |
| product for `q` (step 1) | 1,293,318,812,978,101,148,604 |
| evaluation of `g` (step 2, geometric part) | 1,794,202,242,773,632,447,760 |
| `2K` forward inner transforms of `g` (step 2) | 440,501,026,031,116,126,503 |
| step 3 | 818,783,044,438,740,253,401 |
| step 4 (one extension) | 1,509,329,828,398,647,721,932 |
| step 5 (batch inversion in chunks of `2^16`) | 55,099,292,262,322,552,508 |
| (akki-rock05 `eebae39d`) the value-domain Graeffe prefix of 4.3G before step 1: own tables and allocations `160,721,725,918,484`, `g` on `O1` and `O2` (step 2) `2,234,703,268,804,748,574,263`, 31 steps at `1,579,229,064,072,492,328,740` (the Graeffe pass `29,802,322,457,482,702,644` and one extension between cosets of `H'` at `1,549,426,741,615,009,626,096`), the interpolation of `g^(31)` (step 8 whole) with its kernel `4,971,376,371,377,913,332,454` | 56,162,180,787,151,650,016,141 |
| step 6, the loop: 163 steps (45 with `b = 1`; 4.3G, was 194) | 495,303,015,707,028,346,521,592 |
| step 7 | 1,577,083,545,766,474,708,400 |
| step 8 (two interpolations) | 4,971,375,728,570,466,811,854 |
| allocations, exponent scan, zero fills, end of stage | 19,864,288,334 |
| stage C of one trial, with the stage bookkeeping of 1,000 (ledger row C) | 569,033,738,863,809,196,598,398 |

The inner transforms are column passes and the geometric phase uses the register-blocked kernels above (the outer-kernel convention of 1aa56884). With the pieces of 4.4.1 every coset access of a row pass (the pointwise passes, the batch inversion, the rows read or written by an extension) also selects the base of its piece (a comparison and a branch, 2 operations), and every column pass splits its coset loop at the piece boundary (4 operations per call); both are included in the figures above. Every charge depends only on `m` and the exponent, not on the coefficients.

**Memory.** The loop holds `R1`, `R2`, `G1` and the array of `g` (which holds `g` on `O2` during the loop and `g` in coefficient form at the exit): four arrays of `n1` elements. It also holds the tables and the group buffer of `VCNT = 2^10` rows of `Lmax = Le = 3 * 2^30` elements (the longest kernel), and one transform row of `Lmax` elements; the tables are the `30 K` constants, the two `omega` tables of `2^16` entries and the kernel spectra, and step 5 adds one array of `2^16` elements. The live peak of stage C is `3.0000` arrays of `n1` above its entry , plus the array of `g` from stage A. Section 7 walks these allocations with the rest of the trial.

### 4.3G The value-domain Graeffe prefix on the cosets of H^2 (akki-rock05, entry `eebae39d`, taken over with credit; the method of their entries `479bd57c` (r = 9), `bdc5ccfe` (r = 12) and `9a6e5a1a` (r = 10))

Notation: `H`, `h = 2^32`, `omega`, `C_k = 5^k H`, `z = 5^h`, `O1`, `O2`, `K = 867,361,738` and `n1 = K h` are those of 4.6. `H' = H^2 = <omega^2>` has order `h' = 2^31`, and `-1 = omega^(2^31)` lies in `H'`. In the transform order of 4.6 (position `p` of a coset `vH` holds the value at `v omega^rev32(p)`), the first half of `vH` (`p < 2^31`, even exponents) is the coset `vH'` in its own transform order (`rev32(p) = 2 rev31(p)`) and the second half is `v omega H'` (`rev32(p) = 2 rev31(p - 2^31) + 1`). So the `2K` cosets of `O1` and `O2` are the `4K` cosets `5^k H'` and `5^k omega H'`, `k < 2K`, and the two arrays of `g` on `O1` and `O2` (step 2 of 4.6) hold `g` on `U_0 u omega U_0`, `U_0 = 5^0 H' u ... u 5^(2K-1) H'`. In this section `omega` plays the role that `zeta` (of order `2h`) plays in the prefix of akki-rock05's r = 9 and r = 12 entries: no element of order `2h` exists here (`h = 2^32` is the whole 2-part of `p - 1`).

Definition and lemma. For `f` monic of even degree `m` write `f(X) = E(X^2) + X O(X^2)`; its Graeffe transform `f~(Y) = E(Y)^2 - Y O(Y)^2` satisfies `f~(X^2) = f(X) f(-X)` and is monic of degree `m` with roots the squares of the roots of `f`. `m = 3,725,290,298,461,914,062` is even. Stage C first replaces `g` by `g^(31)`, then runs the eight steps of 4.6 with the exponent `e' = (p-1)/2^32`, and stage D takes `G = gcd(g^(31), R - 1)`. Lemma (the r = 4 Graeffe entry `31cc7f83`, akki-rock05's `479bd57c`): `G` is the product of `(Y - y)` over the distinct `y = S^(2^31)`, `S` a usable root of `g_c`; for if `S_i^(2^31) = u^(2^32)` with `u` in `F_p^*` then `S_i = u^2 xi` with `xi^(2^31) = 1`, so `xi` is in `F_p`, `xi = w^2` with `w^(2^32) = 1` (`2^32 | p - 1`), and `S_i = (u w)^2` is a nonzero square of `F_p`; conversely `S = v^2` gives `S^(2^31) = v^(2^32)`. So `1 <= deg G <= k(c)` when `k(c) >= 1`, `deg G = 0` when `k(c) = 0`, and `G` divides `Y^e' - 1` (squarefree, split); the event `E_c` of 9.2 gives `1 <= deg G <= DMAX`.

Point sets. For a step `t = 0..30` the polynomial `f = g^(t)` (degree `m < n1`) is held by its values on `X_t = U_t u omega U_t`, `U_t = v_0^(t) H' u ... u v_(2K-1)^(t) H'`, `v_k^(0) = 5^k`, `v_k^(t+1) = (v_k^(t))^2`, in the two arrays of step 2 (the `2K` cosets `v_k^(t) H = v_k^(t) H' u v_k^(t) omega H'` of `H`, each in the transform order of 4.6: `U_t` in the first halves, `omega U_t` in the second halves). The node of a coset `vH'` of `H'` is `v^(h')`: the nodes of `U_t` are `n_k = z'^(k 2^t)` with `z' = 5^(2^31)` and those of `omega U_t` are `-n_k`. All `4K` nodes are distinct for every `t <= 31`: the order of `z' = 5^(2^31)` is divisible by the prime `q1 > 4K` of 4.6 (`q1` divides the order of `z = z'^2`, 4.6), and `(j - k) 2^t` with `0 < |j - k| < 2K` is not divisible by `q1`, so `n_j / n_k` has order divisible by `q1` and is neither `1` nor `-1`.

One Graeffe step `t -> t + 1`. (i) The Graeffe pass: in a coset `vH'` (its own transform order) `x` and `-x = x omega^(2^31)` sit at positions `2i`, `2i + 1`, and `f~(x^2) = f(x) f(-x)` is the value at `x^2` in `v^2 H'^2`, the first half of the coset `v^2 H'` of `H'`, at position `i`; the same over `v omega H'` gives the values at `x^2 omega^2`, its second half. The outputs, `n1` values of `f~` on `U_(t+1)` (the cosets `(v_k^(t))^2 H'`, `k < 2K`), are written in place into the first halves: each coset of `H` is processed whole, first its half `vH'` (outputs at positions `i < 2^30`, each written after its inputs at `2i`, `2i + 1`, all at least `i`), then its half `v omega H'` (outputs at positions `2^30 + i` of the first half, whose inputs there, the pairs of `vH'` at `2^30 + i` and above, have already been consumed). Charge, itemised under 4.2 (per output point two loads and one store, each with its address operation, 6, and one multiplication; per four outputs the two pointer updates and the loop control of the loop unrolled by four, 4: 8 per output point): 20 per half-coset and 20 per pass: `G_PASS = 8 n1 + 40 (2K) + 20 = 29,802,322,457,482,702,644`. (ii) The node set, at run time: the representatives squared, the `4K - 1` kernel values `-1/(r^e + 1)` (one batch inversion), the constants `M(-n_l) = r^(2K l) prod_(k<2K) (1 + r^(k-l))` and `M'(n_i) = r^(i (2K-1)) prod_(k != i) (1 - r^(k-i))` (the nodes are geometric, `n_k = r^k`, so these come from prefix products of the `1 +- r^e`, `|e| < 2K`, in `O(K)` operations, and one batch inversion), the kernel spectrum of the convolution below (one forward transform of length `2 Lx = 2^32`) and the factor tables: at most four times the table row of 4.6 (its `30 K` constants, the `omega` tables and its kernel spectra), charged `KERNEL = 4 * 160,701,861,630,150 = 642,807,446,520,600` per change of node set. (iii) One extension from `U_(t+1)` (the first halves) to `omega U_(t+1)` (the second halves), the extension of lemma 4.7 on the `2K` cosets of `H'`: with the nodes `n_k = z'^(k 2^(t+1)) = r^k` of `U_(t+1)` (`r = z'^(2^(t+1))`), per position `j < 2^31`, `F(-n_l) = M(-n_l) sum_(i<2K) s_i kappa'(l - i)` for `l < 2K`, with `M(Y) = prod_(k<2K) (Y - n_k)`, `s_i = F(n_i) n_i^(-1) / M'(n_i)` and `kappa'(e) = -1/(r^e + 1)` (`-n_l - n_i = -n_i (r^(l-i) + 1)`): a Toeplitz matrix `T` of order `2K` applied to the `2K` scaled inputs. Charge (Appendix G, `EXT2`): (a) the `2K` inverse inner transforms read the first halves and their first pass writes into the second halves (out of place, so the values of `U_(t+1)` stay for the next Graeffe pass; the later passes and the `2K` forward transforms work in the second halves); they are column passes of 4.2, run per array (the `2K` cosets of `H'` lie in the two arrays of `O1` and `O2`, `K` cosets of `H` each) at `cnt = K` positions per call as in 4.6, of 31 layers in each direction (a transform of a half of a coset of `H` is the transform of 4.6 without the layer that joins the two halves). Bound: per array, the `K` inverse 31-layer transforms (on the first halves, `2^31` points each) and the `K` forward 31-layer transforms (on the second halves) together touch the `K h` elements of the array once per layer, in column passes at `cnt = K` positions with the same number of calls per pass as the `K` forward 32-layer inner transforms of that array in step 2 of 4.6, and with one layer fewer (the least-charge split of 31 layers is at most a 32-layer split with one layer removed from one of its passes of at least 3 layers, and a pass of fewer layers is charged less, 4.2; forward and inverse column passes are charged alike in stage C, 4.2); over the two arrays the `2K + 2K` transforms are at most the `2K` forward 32-layer inner transforms of step 2 of 4.6, `440,501,026,031,116,126,503`, which is below the inner-transform part of an extension of 4.6, `1,506,885,106,651,255,259,084 - 1,066,384,080,489,337,615,634 = 440,501,026,161,917,643,450`, charged here. On top, `4 n1 = 14,901,161,194,046,881,792`: the output address of every store of the out-of-place first inverse pass (one operation per store, `n1`; the pass keeps only its `2^k` input row bases in the integer registers of 4.2, so its outputs do not use base-plus-index addressing), and the rest as margin (it also covers the reading of 4.6 in which the inner transforms of an extension have 30 layers per direction, the boundary passes of the loop holding the other two: one widened pass per direction, 1.5 per element and less than `0.04` per element of call charge); (b) (this change; `30df2129` ran three products of order `K` and a schedule here) `T` is applied as one cyclic convolution in the form of lemma 4.7: the `2K` scaled inputs `s_i` (the rows of `U_(t+1)` of both arrays) in rows `i < 2K`, the kernel value `kappa'(e - 2K)` at index `e`, `1 <= e <= 4K - 1`, and `F(-n_l) = M(-n_l) y_l` read from row `2K + l`, `l < 2K`, of a cyclic convolution of length `2 Lx = 2^32 >= 4K - 1`; the linear indices reach `6K - 2`, which wraps only to rows below `6K - 2 - 2 Lx = 909,203,130 < 2K`, so no output row is hit. It runs as the geometric phase of 4.6 (group buffer of `2 Lx` rows at `VCNT = 2^10` positions, the kernels and charges of 4.2 and 4.6) with `2K` input rows, over the `2^31` positions (`2^21` groups). Exact count per group, pass by pass: the pruned first two layers, which read the `2K` rows with their factors (`ob4` form; per input row its address, factor and step `8` and the piece base `2`), `23,047,231,413,194`; per direction the radix-2 run of the middle 28 layers in passes of 7, 7, 7, 7 layers (the least-charge split of 4.2; twiddle 1 counted only from the first layer of the run, fewer savings than 4.2 allows), `219,751,336,953,227`, two runs; the fused pass `ob4m` (`13 + 36 cnt + F(cnt)` per call, 6 less per position for twiddle 1), `33,435,246,657,538`; the pruned last two layers, which form and write only rows `2K .. 4K - 1` with their factors, `25,668,921,084,874`; per group `521,654,073,062,060`, plus `20 + 3` of group control and a margin of `2^34`; per extension the running factors reset, `2 (7 * 2K + 2)`, and the loop exit `2`. Total `X_CONV = 1,094,023,911,451,598,580,254` per extension. Check: the same count with `K` input rows at `Lx` gives `1,066,375,046,694,034,765,074` for the geometric phase of 4.6, `2,153,824,640` per group below its charged `GEO`; the margin is more than four times that difference. (c) No staging buffer and no addition pass remain: the inputs are read from and the outputs written to the coset arrays inside the convolution. The group buffer is one buffer of `2^10 * 2^32` words (`2^47` bytes, slab class 48) and the kernel spectrum one array of `2^32` words (class 38): `2^48 + 2^38` bytes of new slab area in section 7, freed before stage C proper. With `KERNEL`: `EXT2 = 1,549,426,741,615,009,626,096`. One step `1,579,229,064,072,492,328,740` (a loop step of 4.6 with `b = 0` is `3,036,354,785,665,833,992,104`); 31 steps `48,956,100,986,247,262,190,940`. After the 31st extension `g^(31)` is known on `X_31`, the `2K` cosets `v_k^(31) H` of `H`.

The prefix, before step 1 of 4.6: its own tables and allocations (the table and allocation rows of 4.6, `160,701,861,630,150 + 19,864,288,334`); `g` on `O1` and `O2` into the two arrays exactly as step 2 of 4.6 (`1,794,202,242,773,632,447,760 + 440,501,026,031,116,126,503`); the 31 steps; the interpolation of `g^(31)` from its values on the first `K` cosets `v_k^(31) H` of `X_31` (geometric nodes `(v_k^(31))^h`, distinct as above; `n1 >= m + 1` points; the inverse inner transforms and the two chirp correlations of step 8 with the kernel of these nodes, charged as the whole of step 8, `4,971,375,728,570,466,811,854`, and `KERNEL`) into the array of `g` in the form stage B leaves it; then the arrays and tables are freed. Prefix total `56,162,180,787,151,650,016,141`. Stage C then runs the eight steps of 4.6 on `g := g^(31)` with `e' = (p-1)/2^32`: 163 loop steps (118 with `b = 0`, 45 with `b = 1`), the base's 194 less its last 31, all with `b = 0` (`(p-1)/2 = 2^31 * 3 q'`, `3 q'` odd). Row C `= 606,998,556,432,298,400,337,481 - 31 * 3,036,354,785,665,833,992,104 + 56,162,180,787,151,650,016,141 = 569,033,738,863,809,196,598,398` (Appendix G).

Exactness. Every map is exact (the Graeffe identity, exact inner transforms, the exact Lagrange interpolation at distinct nodes); no premise is added to the time or the memory. The zero test of step 5 of 4.6 concerns `g^(31)`; its bound is 9.2(b) (`2^-98.6`). A toy-size run of the H^2 form itself (`h = 2^5`, `K = 3`, `m = 94`, 6 steps, Appendix G2) checks the half-coset layout, the pairing and output positions, the order-`2K` Toeplitz product (by its block split, against the direct product that this package computes as the convolution of (iii)(b)) and the extension to the negated nodes against direct evaluation; the zeta form of akki-rock05's earlier entries is checked there too.

Stage F (the scan). Stage E returns a root `y` of `G`, `y = S^(2^31)` for a usable root `S = s0^2`; then `s0^(2^32) = y`, the solutions of `s^(2^32) = y` are `t eta^i`, `i < 2^32`, for `t = y^u`, `u = (2^32)^-1 mod (p-1)/2^32` (because `y^((p-1)/2^32) = s0^(p-1) = 1`) and `eta` of order `2^32`; `eta^(2^31) = -1`, so `i < 2^31` covers every `s` up to sign, and `F(c + s) = F(c - s)` does not depend on the sign. The scan evaluates `F(c + s)` and `F(c - s)` on the line (each evaluation one execution of the line program `L` of Appendix L at `c' + s` and `c' - s`, as in stage B) for `s = t eta^i`, `i = 0, 1, ...`, and stops at the first equality; it reaches `+-s0` at the latest, and any `s != 0` with `F(c + s) = F(c - s)` gives a collision by 2.4 (stage G verifies it). Per candidate at most `1,400` operations (`s := s eta` 1, `c' + s` and `c' - s` 2, two executions of `L` at `387 + 2`, the comparison and its branch 2, the loop 3, a move 1: 787; charged 1,400), `2^31` candidates at most, and `6,000` for `t = y^u` (field operations at 10, the stage-F rule of section 6): row F `47,012 + 6,000 + 308 + 2^31 * 1,400 = 3,006,477,160,520` (`308`: the load of the constants of `L` before the scan, L.3). `eta` and `u` are offline literals (6.2a: `eta` is the literal `5^t R` of 6.2(b), `u` adds at most 2,000 operations, inside the declared cap).

Memory. The prefix runs at the entry of stage C, where the live set is the twiddle table and the array of `g`, and holds two arrays of `n1` words and its tables: `2.0000` arrays above the entry of stage C against the `3.0000` of the stage-C live peak of 4.6; the two arrays are taken from the low end of the pool and freed, last allocated first freed, before stage C proper, which restores the entry state of the pool; the prefix's tables are slab blocks of the classes of the stage table, freed before stage C proper builds its own. The pool is unchanged; the prefix and scan code add `32,768` bytes, and its group buffer and kernel spectrum are counted as `281,749,854,617,600` bytes of slab area (section 7).

## 5. Why the output is a collision

By sections 2-3 and 4.3G: a root `y` of `G = gcd(g^(31), R - 1)` is `S^(2^31)` for a usable root `S` of `g_c`, and the scan of stage F finds `s != 0` with `F(c+s) = F(c-s)` (it reaches `+-sqrt(S)` at the latest), `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes and compares them; the algorithm outputs only if they are equal and the pairs differ; it never outputs a non-collision. This section is a statement about the output of a successful run, and holds for every coin sequence. It contains no probability.

## 6. Ledger: worst-case operation count (primitive operations; `C(21) = 657`)

Notation: `T_fixed` = init (twiddle table) + setup (the line) + the plan_invN misses + stage H + stage I; `T_trial` = stages A to D of one trial, stage E at its cap, stages F and G, the trial loop and the allocator reset after an ABORT (charged in every trial); `T_off` = the offline derivation of section 6.2, counted exactly (136,785; at most 138,785 with the literal `u` of 6.2a) and charged at its declared cap 1,000,000. The claim is `N_max = T_fixed + K * T_trial + T_off` with `K = 1` (one centre, section 9.2), and `time_log2 = ceil_5(log2(N_max / 657))`.

Every stage is charged by the rules of section 4.2 where it executes. Every trial is charged as if its gcd had degree 0 in stages A to D (the larger case), and in addition with stage E at its cap, stage F at its worst case and stage G.

| row | what is charged | operations |
|---|---|---:|
| init | twiddle table of `2^(32-1)` elements (`ntt_init(32)`: 5 operations per element, loop control, the roots of unity, the inversions of the setup) | 17,179,887,292 |
| setup | the line (`line_setup`) | 4,910 |
| A (per trial) | stage bookkeeping 1,000, loop test and update 5, the coin draw 31, one allocation | 1,382 |
| B (per trial) | `578241159` cosets of `6,442,450,944` points, each point with two evaluations of `F` (at `c' + s` and `c' - s`), each one execution of the line program `L` (Appendix L, mpjunior92 `c667182d`) at `387` operations, the load of the `154` constants of `L` at the start of each coset (`178,098,276,972`) and `c' = c + E0_0` (1), the loop work around them, `578241159` inverse transforms of size `6,442,450,944`, the geometric solve of the cosets (two correlations of length `1,610,612,736` per position), the normalisation | 13,300,858,577,087,557,708,729 |
| C (per trial) | (4.3G, akki-rock05 `eebae39d`: after the Graeffe prefix) `S^((p-1)/2^32) mod g^(31)` in the value domain (section 4.6): the Barrett start (Newton reciprocal and the product for `q`), the evaluations of `g` and `q`, the batch inversion, `163` steps (45 with `b = 1`, after the Graeffe prefix of 4.3G), each two pointwise passes and two extensions, the exit and the two interpolations | 569,033,738,863,809,196,598,398 |
| D (per trial) | half-gcd of `(g^(31), R - 1)` (sections 4.4, 4.4.1, 4.4.2), charged for the normal remainder sequence with the quotient and return tests; any other sequence ends the trial after a prefix of this work (section 6.3); the aligned split of 4.4.2 item 1 | 477,848,936,324,260,928,287,843 |
| E (per trial, cap) | `Z = 64` rounds at degree `DMAX = 16` (below) | 166,079,773 |
| F (per trial) | (4.3G, akki-rock05 `eebae39d`) `t = y^u`, the load of the `154` constants of `L` once before the scan (`2 * 154 = 308`, L.3) and the scan of at most `2^31` candidates at 1,400 (4.3G); square root, back-map (below) | 3,006,477,160,520 |
| G (per trial) | two reference hashes: `1000 + 10 * 2 * 657 + 32` | 14,172 |
| trial loop | the test and increment of the trial counter and the bookkeeping of the trial: at most 12 | 12 |
| ABORT reset (per trial) | the reset of the allocator when a test of stage D (quotient, return or window) or the zero test of stage C (4.6 step 5) fails and the trial ends (section 6.3): the 48 free-list heads (classes 7 to 54), the end of the slab area, the two ends of the pool and the header of its free middle block; at most 1,000, charged in every trial | 1,000 |
| plan_invN misses | one per distinct plan size (57 sizes) | 176,073 |
| H | canonical encoding of the output (6 conversions, 384 digits) | 5,644 |
| I | output of the answer: formatting (`400 * 8,192`), loops, entry, one `write`, one `exit_group` | 3,384,436 |
| offline | section 6.2: `T_off = 136,785` counted exactly, charged at the declared cap | 1,000,000 |
| **N_max** | `T_fixed + T_trial + T_off` | **1,060,183,533,768,181,510,310,184** |

Row C is the sum of the charges of section 4.6; row D is the charge of the half-gcd of sections 4.4, 4.4.1 and 4.4.2 with the products of 4.5, on the normal remainder sequence (6.3).

`N_max = 1,060,183,533,768,181,510,310,184` operations `= 1,613,673,567,379,271,705,190.53` units, `log2(N_max / 657) = 70.4508387557`, claimed as `70.45084` (rounded up at five decimals; `30df2129`: `1,077,472,428,245,490,240,123,723`, `70.47418`); `T_trial = 1,060,183,533,768,164,325,851,829`. Appendix G itemises the prefix and the rows B, C and F, and the rows of the table above sum to `N_max`; row D is the count of our program with the aligned split (4.4.2 item 1). `213552fe` had `1,121,894,996,223,269,347,127,988` operations (`70.53247`), `eebae39d` `1,101,219,073,135,095,350,315,644` (`70.50563`).

Stage B charges each of the `7,450,580,601,318,408,192` evaluations of `F` as one execution of the line program `L`, `135 + 12 * 21 = 387` operations (Appendix L, checked against the reference rounds in L.2); the loop work around the evaluations is charged on top (section 3).

Stage E at its cap. The trial enters stage E only when `1 <= deg G <= DMAX`; stage E opens with 1,000 (stage bookkeeping) and runs a round for each pass of the isolation loop until `deg G = 1` or `Z` rounds have been made. A round at current degree `d` costs `R(d)`: the coin draw 31, the zero test of the shift (5, and at most 2 for the replacement of a zero draw by 1) and one negation; the Taylor shift (`taylor_shift`: two allocations, three loops of `d + 1` steps with their loads, stores and loop control, the schoolbook product of two polynomials of `d + 1` coefficients, two inversions and one exponentiation by `d`); `Z^((p-1)/2) mod G` by schoolbook square-and-multiply (`pow_half`: 253 modular squarings, each `2d + 3 d (d-1)/2 + 2 d^2` field operations and an allocation and a free, and 45 multiplications by `Z`, each `2d` field operations; because the memory-access charge adds 9 operations per field operation, every field operation of `pow_half` is charged 10); two classical gcds (`gcd_cl`: at most `d` outer iterations, each with one inversion charged `2,640` operations (the 330 field operations of `x^(p-2)` and the 2,310 control operations of its bit loop), at most `2d + 1` division steps, each charged at the largest row length); the copies, the tests and the frees. The cap charges every one of the `Z` rounds at `d = DMAX`, because `R(d)` is non-decreasing in `d`: `R(16) = 2,594,979`, of which `pow_half` is 2,471,032, the Taylor shift 11,700 and the two gcds 54,395 each. All allocations are charged at `L <= 16` live blocks (550 per allocation, 105 per free): in stage E the live blocks are the twiddle table, `G`, `S`, `S - 1`, `S + 1` and the two gcd arrays (at most 8), and at most four more inside the Taylor shift or the modular squaring. `E_cap = 1,000 + 3 + 64 * R(16) + 114 = 166,079,773`.

Stage F. After the stage bookkeeping (1,000), 12,000 control operations for the Tonelli-Shanks control and 2 more, the field operations of stage F are charged 10 each (the memory-access charge): the powers by `q` and by `(q+1)/2`, Tonelli-Shanks with parameter `m` falling strictly from 32 (an outer step with parameter `m` costs `m` squarings and 2 multiplications: at most `sum_(m=1)^(32) (m + 2) = 592`), and two back-maps (three fifth-root powers `x^e`, `e = (4(p-1)+1)/5`, two multiplications, two additions, two subtractions each), plus one addition and one subtraction: at most 3,401 field operations, so `F = 13,002 + 10 * 3,401 = 47,012`. (This entry: stage F first runs the scan of 4.3G, charged in row F; the Tonelli-Shanks charge above is kept as an overcharge.)

Every figure above is an upper bound that the algorithm meets or exceeds for every coin sequence and every target value (stage D by section 6.3): each loop bound is a constant or a function of `m` only, the trial loop is capped at `K` and tested at the start of each trial, the isolation loop is capped at `Z` rounds of degree at most `DMAX`, and the operations of each stage are counted under the rules of section 4.2.

### 6.2 Offline derivation of the literals (preprocessing)

The literals of the sources are computed once, offline, from `p` and the organizer's 192 round constants and 9 MDS entries, one literal at a time (working set: at most 16 words of 32 bytes and a 64-byte digit buffer); each is the value of one closed formula, with no search and no choice. Count in the primitives of 4.2 (orchard-field-ram-v2: every field operation, load, store and control operation is 1): a field operation is charged 4 (the operation, two operand loads, one store), a 64-bit word operation 3 (the operation, one load, one store), a hexadecimal digit 5 (its load, the table load, a shift, an or, the loop control). (a) Input: 202 values of 64 hexadecimal digits (`p`, the 192 round constants, the 9 MDS entries), 324 each with the 4 word stores: `65,448`. (b) Field literals, 489 field operations: `2 = 1 + 1` (1); `R = 2^256 mod p`, `2` squared 8 times (8); `R^2 mod p` (1); the Montgomery forms `x R mod p` of the 201 organizer constants (201); `2^65 R mod p` (`2` squared 6 times, times `2`, times `R`: 8); `5 = 2 + 2 + 1` (2); `5^t R mod p` with `t = (p-1)/2^32`, the odd part of `p - 1` (the exponent written `q` in the Tonelli-Shanks of stage F; 223 bits, 46 of them 1: 222 squarings, 45 multiplications, times `R`: 268); charged `4 * 489 + 3 * 222` (the bit steps of the square-and-multiply) `= 2,622`. (c) Word literals, 90 word operations: `p - 1` (4), `t` (a shift by 32 over 4 words, 12), `(t+1)/2` (16), `(p-1)/2` (12), `p - 2` (4), `e = (4(p-1)+1)/5` (a shift by 2 into 5 words 15, plus 1, a division by 5 word by word 10: 26), `-p^-1 mod 2^64` (5 Newton steps `x <- x (2 - p_0 x)` from `x = p_0`, 3 each, and a negation: 16); charged `3 * 90 = 270`. (d) Output: 211 literals of 64 hexadecimal digits (the 201 Montgomery forms, `R`, `R^2`, `2^65 R`, `5^t R`, `t`, `(t+1)/2`, `(p-1)/2`, `p - 2`, `e`, `p`), 324 each, and `-p^-1 mod 2^64` (16 digits, 81): `68,445`. `T_off = 65,448 + 2,622 + 270 + 68,445 = 136,785` operations over the 212 literals. The ledger charges the declared cap `1,000,000 >= T_off` (`preprocessing_log2 = 20`, `2^20 = 1,048,576`), inside `N_max`: a counted bound, not a premise. The algorithm uses no other offline result: the line, its minors and the twiddle table are computed at run time and charged in `setup` and `init`. The leading coefficient `f_D(0)` of section 2.3 is a fact used in the proof; the algorithm re-derives it (stage B tests that the leading coefficient of `g_c` is nonzero and normalises by it).

6.2a (4.3G, akki-rock05 `eebae39d`) The Graeffe prefix and the scan use `eta = 5^t` (order `2^32`, `t = (p-1)/2^32`), the literal `5^t R` of 6.2(b) already, and add one literal, `u = (2^32)^-1 mod t` (`t` odd): `k = -t^-1 mod 2^32` by 5 Newton steps `x <- x (2 - t_0 x)` on the low word (3 word operations each) and a negation, then `u = (1 + k t)/2^32` (a one-word by four-word product, 8 word operations with the carries, an addition and a shift by 32 over five words, 15): at most 50 word operations, 150 operations; its output, 64 hexadecimal digits, 324: at most 2,000 in all. `T_off <= 136,785 + 2,000 = 138,785`, inside the declared cap 1,000,000 that the ledger charges; with the `154` constants of `L` (Appendix L.1, at most `697,866`), `T_off <= 836,651`.

### 6.3 Stage D charged for the normal remainder sequence, with the ABORT (bradcush, entry e6dcb600)

Row D of the ledger charges the half-gcd of section 4.4 for the normal remainder sequence of `(g_c^(31), R_c - 1)` (4.3G): every quotient of degree 1, the case of the premise `H-NORMAL` (9.5). Two tests make every other sequence end the trial: (a) the quotient test: every division (the re-centering division of a node, the division of each repetition of the outer loop, each step of the base case) tests that its quotient has degree 1 (2 operations); (b) the return test: every call `hgcd(a, b, k)` tests on return that it removed exactly its parameter, `h = k` (2 operations); (c) the window test of 4.4.1 item 3 (2 tests, 2 operations each); a zero remainder inside hgcd or in the outer-loop division also ends the trial. On a failed test the trial ends (ABORT): the arrays of the trial are released by resetting the allocator to its state after the twiddle table (1,000 operations, charged in every trial) and the next centre is drawn. Lemma (prefix; e6dcb600, its 6.3(a)-(c)): while every quotient so far has degree 1, every length, recursion parameter and allocation of the program equals that of the normal case, because each call splits by the rule of 4.4.2 item 1 (a function of its parameter alone) and, with every quotient of degree 1, every degree in the tree is fixed by m and the number of quotients so far and the parameters of the second call and of the outer loop are fixed by `m` alone. At the first quotient of degree other than 1 either the quotient test of that division fails, or the call stops below its parameter with a nonzero remainder and the return test of its caller fails before the result is used. Every remainder that the outer loop's hgcd calls and divisions produce has degree at least 94 (n >= 193), so a gcd of degree at most 94, and so every gcd of degree at most DMAX, first appears in the classical Euclid below degree 192, after a prefix of the degree-0 work. A zero remainder anywhere earlier (gcd degree above 94, a failed trial anyway) ends the trial at that test. So every trial executes a prefix of the operations and of the allocation sequence charged for the normal case, and the time bound of section 6 and the memory bound of section 7 hold for every remainder sequence; only the success probability depends on the sequence (9.2(b)). Row D of section 6 is this charge, `477,848,936,324,260,928,287,843`.

## 7. Memory

Five terms make up the memory.

(a) The code and static data of an implementation of the algorithm: 399,216 bytes of code, 32 of initialised data and 4,851,196 of static tables and buffers (the 8,192-byte output buffer and the tables of the stages), and at most 907,520 bytes for the straight-line block bodies of 4.2 (for `k = 1, ..., 7`, forward and inverse: the four-block and one-block bodies and their group-0 variants, at most `10 (2^(k+1) + 3k 2^(k-1) + 3)` instructions of at most 16 bytes each): 6,157,964 bytes; and 32,768 bytes (at most 2,048 instructions of 16 bytes) for the routines of this entry, the apply plans of 4.4.1 item 8, the chunked batch inversion and the two `omega` tables of 4.6: 6,190,732 bytes; and 5,472 bytes for the two row bodies of the node of 4.4.2 (the fold row, `8 * 22 + 3 = 179` instructions, and the two-output row, `8 * 20 + 3 = 163`), 342 instructions of at most 16 bytes: 6,196,204 bytes; and 16,384 bytes (at most 1,024 instructions of 16 bytes) for the other routines of the node of 4.4.2 (its call, bump-arena and return operations, the copy, zero-fill, fold, twist and scale loops of its rows, the 3-row and 2-row CRT loops, the pseudo-division, the loop of the products by `Q`, the base case of budget 63 and the table of scales; the transforms and pointwise passes are the kernels of 4.2): 6,212,588 bytes.

(b) The arena, which serves every array of the largest trial (the heap is inside the memory of the implementation; nothing is requested from the system at run time). Each block has a 64-byte header and a payload rounded up to a multiple of 64 bytes (section 4.2). The arena is the capacity of the allocator of section 4.2 on the allocation sequence of one trial, found by simulation (a trial frees every array but the twiddle table, and the simulation checks that the pool is back to that state at the end of the trial). The simulation records every allocation and free of the trial in the order of the program (the twiddle table, stage A, stage B, stage C, stage D; the temporary arrays of one call are allocated in the order of the walk and freed in the reverse order), checks that these events reproduce the live-set walk of every stage (bytes in use, peak, live blocks), and runs the allocator on them. By the prefix lemma of section 6.3 every size in the sequence is a function of `m` and of the shape of the recursion on the normal sequence (and the block counts of the products), so the sequence is the same for every input. The two-ended pool takes the blocks of more than 2^54 bytes and is simulated address by address (two lists in address order, the low one from the bottom and the high one, for the statements marked `# pool:H`, from the top; the first free block that fits on the request's side is cut from the side nearest its end; a free merges with its free neighbours and with the unused middle); its capacity is the largest sum of the extents of the two ends over the trial, `476,837,158,209,500,217,728` bytes (after stage C `476,837,158,209,500,217,728`, after stage D `476,837,158,209,500,217,728`), plus 128 bytes so that the unused middle is always at least 128 bytes. The live-set peak of the same sequence is `476,837,265,213,765,335,104` bytes and the arena is `1.00123` times it: the blocks that die first are taken from the top and the long-lived ones from the bottom, so the holes left by freed blocks are small. The slab classes take the blocks of at most 2^54 bytes (a block of at most `2^j` bytes gets a slot of `2^j` bytes; the free list of the class first, else a new slot from the end of the slab area), so the slab area is the sum over the classes of the peak number of live blocks of the class times `2^j`: `585,464,653,023,257,088` bytes. Stages E to I hold at most 16 live arrays of at most 17 elements (16 slots of 1,024 bytes), and the allocator keeps 48 free-list heads (classes 7 to 54) and the end of the slab area (49 words, 392 bytes): `16,896` bytes with a margin of 120. The arena is `477,422,622,862,523,491,840` bytes (the three terms, rounded up to 64 bytes), in the stage with the highest pool address, C. The peaks of the live set per stage (twiddle table, `g`, `F` and the live set of the stage; the arena above is larger): A 119,209,289,621,094,531,264; B 238,418,579,242,189,062,400; C 476,837,265,213,765,335,104; D 454,126,002,273,328,890,624; stage E and the later stages hold the twiddle table and a few arrays of at most 17 elements. The walk of stage D is the walk of the normal remainder sequence (6.3) with the pieces and windows of 4.4.1, its apply plans (item 8: six arrays of `N` elements and the outputs per plan) and 4.4.2: every array of stage D has the length the normal sequence gives it, and a trial with any other sequence ends (ABORT) after a prefix of these allocations, so the walk bounds every trial. The largest transform has `3 * 2^32` points and uses roots of unity of order 3 and `2^32` (`p - 1` is divisible by 3 and by `2^32`); products that would need a longer transform are computed by blocks (section 4.5). The largest buffers are those of stage C (section 4.6: `R1`, `R2`, `G1` and the array of `g`, `n1 = 3,725,290,298,511,720,448` elements each, the tables and the group buffer; the Newton phase of its set-up holds three arrays of `ell` elements and the forms of one product) and those of stage D (4.4, 4.4.1); the arrays of 4.4.2 (the table of 31 scales, the four matrix arrays of `2^j + 1` words and the node arena of at most `34,359,738,112` words of each matrix-only call) are blocks of at most `2^40` bytes and are inside the slab area above.

(c) A stack bound of 65,536 bytes.

(d) The register file of the machine of claim.json: one file of 387 words (256 field registers and 131 integer address registers), each counted as a 256-bit word, 12,384 bytes.

(e) The working set of the offline derivation of section 6.2: 16 words of 32 bytes and the 64-byte digit buffer, 576 bytes.

Total of the base `213552fe`: (a) + (b) + (c) + (d) + (e) = `477,097,308,158,196,442,892` bytes `= 2^68.69284`. With the aligned split of 4.4.2 the arena (b) is `477,422,622,862,523,491,840` bytes (above): (a) + (b) + (c) + (d) + (e) = `477,422,622,862,529,782,924` bytes. Added to these: for the Graeffe prefix of 4.3G (akki-rock05 `eebae39d`), term (a) `32,768` bytes more (below) and the slab area of the arena `2^48 + 2^38 = 281,749,854,617,600` bytes more (the prefix's group buffer, slab class 48, and its kernel spectrum, class 38; 4.3G (iii)(c); the prefix's two arrays of `n1` words are pool blocks below the stage-C live peak); and `32,768` bytes of code and static data for the line program `L` (Appendix L.4). Footprint `477,422,904,612,384,466,060` bytes `= 2^68.6938297`, claimed as `memory_log2_bytes = 68.69383` (rounded up at five decimals; `30df2129`: `68.69384`). The rows of section 6 and this arena are generated by our counting program: it adds the charges of 4.2 over every call of the algorithm of section 4 in program order and runs the allocator of 4.2 on the same allocation sequence; each term is the closed formula stated in sections 4 and 6, and the program is not attached. The memory penalty is `max(0, 68.69383 - 20) = 48.69383`. The offline derivation of section 6.2 is a closed formula per constant; its working set is term (e). The algorithm has no stored advice and no precomputed data beyond the constants of section 6.2; the twiddle table is built at run time and charged in stage "init". 4.3G adds `32,768` bytes of code and static data to term (a) (the Graeffe pass, the node-set routine, the one-convolution extension of 4.3G, the scan and its literals), counted in the footprint above; the prefix's two arrays stay below the stage-C live peak and are freed before stage C proper (4.3G).

## 9. Success probability and the premises `H-ONE` and `H-NORMAL`

### 9.1 The premise `H-ONE`

Notation. `p` is the Pallas prime, `D = 5^27`, and `F` is the fixed polynomial of section 2.3 at r = 21 (degree `D`, leading coefficient `f_D(0) != 0`). `g_c` is the monic odd part about the centre `c` (section 3, degree `m = 3,725,290,298,461,914,062`), and `G(c, t) = (F(c + t) - F(c - t)) / (2 t) = g_c(t^2)`. For `c` in `F_p`, let `k(c)` be the number of nonzero squares `S` with `g_c(S) = 0`; this is `deg G_c` of section 3, the degree of `gcd(g_c, S^((p-1)/2) - 1)`. `E_c` is the event `1 <= k(c) <= DMAX` (`DMAX = 16`) under which stage E runs.

**Premise `H-ONE`.** The number of centres `c` in `F_p` with `1 <= k(c) <= 16` is at least `0.3931 p`. Equivalently, for `c` uniform on `F_p`, `P(E_c) >= q = 0.3931`.

Four fields (as in claim.json). **Statement:** the premise above. **Role:** score-critical. **Scope:** the fixed target `poseidon-orchard-r21-prefix-v1`, this line construction (the line `j = 0` of the first two rounds, section 2) and the polynomial `F` of section 2.3, with centres uniform on `F_p`. Nothing is claimed for other round counts. **Limitations:**
- The premise concerns this `F`, not every polynomial of degree `D`. It is false for permutation polynomials: every pure composition of maps `x -> a x^5 + b` is bijective and has `k = 0` at every centre. It is also false for a decomposable `F` with imprimitive monodromy (the axis line of 10.3, Theorem C).
- It is false at one layer (`F_1`, `m = 2`: the law of 9.3(a) gives exactly 0.375) and true at two and three layers (9.3(c)).
- The value `0.3931` is `0.0003693` below the value `1 - e^(-1/2) = 0.3934693` of the law of 9.3(a). With `delta = 0.001` (9.5) and `P(E_c) >= 0.3931` the bound of 9.2 is `0.39209999999999762857` at `K = 1`.
- No sample resolves a margin this small (9.3(d)). The premise rests on the law and its computed cases, not on a frequency.

What the premise does not contain: no random-polynomial model; no independence of centres (one centre is drawn); no statement about the remainder sequences (that is `H-NORMAL`, 9.5); and nothing about the cost.

### 9.2 The success bound with one centre

(a) *Centre.* The centre is one draw (4.1.1) and lies within statistical distance `2^-128.9` of uniform on `F_p`; over the at most 65 words of the run the distance is `eps_coin < 2^-122` (4.1.1), which the bound subtracts. So `P(E_c) >= q - eps_coin` for the drawn centre.

(b) *The ABORT of stage D and the zero test of stage C.* Let `N_c` be the event that the remainder sequence of `(g_c^(31), R_c - 1)` (4.3G; `R_c = S^((p-1)/2^32) mod g_c^(31)`) is normal down to its gcd: `deg(R_c - 1) = m - 1` and every quotient of degree 1 (section 6.3). By the premise `H-NORMAL` (9.5), `P(not N_c) <= delta = 0.001` for `c` uniform.

Let `Z_c` be the event that `g_c` vanishes at a point of the set `O1` of the value-domain stage C; its zero test (section 4.6) ends the trial. For each of the `n1` points `x` of `O1`, `g_c(x)` (before normalisation) is a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`, so it has at most `D - 1` roots. Each residue is drawn with probability at most `4/2^256` (4.1.1). With the Graeffe prefix of 4.3G the zero test concerns `g_c^(31)`: `g_c^(31)(y) = 0` for `y` in `O1` only if `g_c(x) = 0` for one of the `2^31` values `x` with `x^(2^31) = y` (in `F_p` or an extension), each such `g_c(x)` a polynomial in `c` of degree `D - 1` with leading coefficient `D f_D(0) != 0`. Hence `P(Z_c) <= delta_C = 2^31 n1 (D - 1) 4 / 2^256 = 2.059e-30 (2^-98.6)`, proved, no premise (the base, without the prefix: `n1 (D - 1) 4 / 2^256 = 9.588e-40`).

If `E_c` and `N_c` hold and `Z_c` does not, stages C and D run to their end and return `G = gcd(g_c^(31), R_c - 1)` with `1 <= deg G <= DMAX` (lemma of 4.3G).

(c) *Isolation.* If `E_c` holds, stage E fails with probability at most `eps_iso = 2.371e-15 (2^-48.58) < 2^-48`, over words that are fresh for that stage (lemma 9.4): each round, whatever came before, halves the degree with probability at least `w = 1/2 - 7.869e-40` (the `(p-3)/2` shifts that separate two roots, 4.1.1 weights), four halvings take `deg G <= 16` to 1, so the failure probability is at most `P[Bin(64, w) <= 3] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = 2.371e-15`. Proved, no premise.

(d) *The bound.* A trial with `E_c`, `N_c`, not `Z_c`, and a successful isolation ends in a verified collision (sections 2-5). For `c` uniform, `P(E_c and N_c and not Z_c) >= q - delta - delta_C`. So, with `K = 1`,

`P[success] >= 1 - (1 - q + delta + delta_C)^K - K (eps_coin + eps_iso) = q - delta - delta_C - eps_coin - eps_iso = 0.39209999999999762857 >= 0.39209`

with `q = 0.3931`, `delta = 0.001` and `K = 1`. This is the form of bradcush's entry 1aa56884 (9.2(f) there) at `K = 1`. The bound stays at least 0.39 for every `delta <= 0.0030999` at `q = 0.3931` (above the stated `delta = 0.001`; the delta stated in `H-NORMAL`, 9.5, is the delta used here), and for every pair with `q - delta >= 0.3900000000000023715`. The probability is over the random words of 4.1.1 for the fixed target. It is not a probability over targets and not a sampled frequency, and no run of this algorithm at r = 21 enters it.

(e) *Why one centre needs `H-ONE`.* Two moments of `k` cannot give 0.39 with one centre. The law of 9.3(a) has the exact values `E[k] = 1/2` and `E[k(k-1)] = 1/4`, and the sharp lower bound on `P(k >= 1)` over all laws with these moments is `3/8 = 0.375`: the law `P(0) = 5/8`, `P(1) = 1/4`, `P(2) = 1/8` attains it. With three moments the bound is still 0.375. This is why entries built on two moments (our earlier premise `H-GEOM-w1`, and gta6rp's linear two-moment bound) use two centres. One centre needs a statement about the event itself, or four moments (9.3(b)).

### 9.3 Where the number comes from (support of `H-ONE`; not used in the bound)

(a) *The law.* The roots of `G(c, t)` in `t` are `+-t_1, ..., +-t_m`, where `u_i = t_i^2` are the roots of `g_c`. So the Galois group `Gamma` of the cover `G(c, t) = 0` of the `c`-line acts by signed permutations: `Gamma` is a subgroup of the hyperoctahedral group `B_m` (10.3, Grok job 137). For a centre off the branch locus, `k(c)` is the number of positive fixed points of the Frobenius element: the indices `i` with `t_i` in `F_p`.

For a uniform element of `B_m`, the binomial moments of this number are `E[C(k, j)] = 2^-j / j!` for `j <= m`, so `P(k >= 1) = 1 - sum_(j <= m) (-1/2)^j / j!`. This is 0.375 at `m = 2`, 0.3958 at `m = 3`, 0.3932 at `m = 4`, and 0.3934693403 for every `m >= 12`: the Poisson(1/2) value `1 - e^(-1/2)`. The tail is negligible: `P(k > 16) < 2.3e-20`. With Chebotarev's theorem (Frobenius elements equidistributed in `Gamma`), this law is the frequency over the centres.

(b) *Moments and counts.* `E[C(k, j)] = N_j / (2^j j! p)`, where `N_j` is the number of points `(c, t_1, ..., t_j)` over `F_p` with `G(c, t_i) = 0`, `t_i != 0` and `t_a^2 != t_b^2` (for `j = 1, 2` these are the counts `N*` and `N_off` of our earlier premise `H-GEOM-w1`).

For every integer `k >= 1`, `sum_(j=1..4) (-1)^(j+1) C(k, j) = 1 - C(k-1, 4)`. This is 1 for `k <= 5` and at most 0 for `k >= 6`, and the sum is 0 at `k = 0`. So `1_(1 <= k <= DMAX) >= k - C(k, 2) + C(k, 3) - C(k, 4)` for every integer `k >= 0`, and `P(E_c) >= S_1 - S_2 + S_3 - S_4` (Bonferroni at order 4). With the moments of (a) this is `151/384 = 0.3932292`.

Hence `H-ONE` follows from four count statements, `N_1 >= (1 - eps) p`, `N_2 <= (1 + eps) p`, `N_3 >= (1 - eps) p` and `N_4 <= (1 + eps) p`, with `eps <= 0.0032835`. The premise is stated as the weaker statement `H-ONE` itself.

(c) *A theorem at two and three layers.* Let `F_N` be the truncation of 10.3: the first `N` S-box layers, degree `5^N`. On the deployed constants and the construction's line, 10.3 gives the arithmetic monodromy `Gamma = B_12` at `N = 2` and `Gamma = B_62` at `N = 3` (`pi(Gamma) = S_m`, `K = F_2^m`).

The geometric monodromy is normal in `Gamma` with a cyclic quotient. It therefore contains the commutator subgroup `{(eps, pi) : pi in A_m, prod eps = 1}` of `B_m`. That subgroup acts transitively on ordered `j`-tuples of signed distinct indices for `j <= m - 2`: `A_m` is `(m-2)`-transitive, and a free sign fixes the parity.

So for `j <= 8` the curve counted by `N_j` is absolutely irreducible, a complete intersection of degree at most `(5^N - 1)^j`. The Aubry-Perret bound gives `N_j = p (1 + rho_j)` with `|rho_j| <= (5^N - 1)^(2j) p^(-1/2)`: below `2^-53` at `N = 2` and below `2^-15` at `N = 3` (`j <= 8`).

The Bonferroni bounds of orders 7 and 8 then give `0.39346933 <= P(E_c) <= 0.39346944` for `F_2` and for `F_3`. At these depths `H-ONE` is a theorem, with margin 0.00036933.

 At `N = 4`, the cycle types `(312)` and `(311,1)` of 10.3 make `pi(Gamma)` 2-transitive of degree 312. The only such groups are `A_312`, `S_312`, and the groups between `PSL(2,311)` and `PGL(2,311)`, whose non-identity elements fix at most two points. Centres with `k(c) = 3` and `k(c) = 4` occur (our runs, 10.5.1), and the 312-cycle is odd, so `pi(Gamma) = S_312`. The sign kernel at `N = 4` is not computed.

(d) *Measured.*
-  Toy fields, exact over all centres: deployed constants reduced modulo `p = 1,048,627` and six random-constant seeds, 3 to 8 S-box layers, partial rounds included, 27 cases. `P(k >= 1)` lies between 0.39214 and 0.39436; the largest deviation from 0.3934693 is 0.00133, that is `1.36 / sqrt(p)`.
- The real field: the organizer-run tests of 10.5.1 and our runs, reproducible observations at `m = 12` and `62`; no probability bound is drawn from them.

(e) *The extrapolation.* At `N = 27` neither the monodromy nor the counts can be computed. Weil's bound exceeds `p` for `j >= 2` (relative error `2^123.8` at `j = 2`).

The premise states that this `F` stays within `0.0003693` of the law of (a) (`q = 0.3931 <= 151/384 = 0.3932292`): no structure appears between the third layer and the 27-th that changes the law of the positive fixed points by 0.1%.

The measured deviations shrink like `p^(-1/2)` and do not grow with the degree. On the toy fields the deviation is `1.36 / sqrt(p)` . The counts of Grok job 139 give `eps ~ 3.1 / sqrt(p)` over degrees 5 to 1,953,125 (10.3).

### 9.4 Lemma (isolation), proved

**Lemma.** Let `G` be monic of degree `d` with `2 <= d <= DMAX`, a product of `d` distinct linear factors over `F_p`. In one round of 4.1.2 (`a` is a coin draw, with 0 replaced by 1), with probability at least `w = (4 (p-3)/2 - (p - r))/2^256 = 1/2 - 7.869e-40` (`2^256 = 3p + r` of 4.1.1: the `p - r` residues at or above `r` have 3 preimages) both `G_+` and `G_-` are nonconstant, and then the kept part has degree at most `floor(d/2)`. The degree never increases. Hence after `Z` rounds the probability that `deg G >= 2` remains is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1]`, which for `DMAX = 16`, `Z = 64` equals at most 2.371e-15 (2^-48.58) (the exact sum below).

*Proof.* Let `u != v` be two roots of `G`, `chi` the quadratic character on `F_p`. In a round the roots of the shifted `G` are `r + a`. If `a` is not `-u`, not `-v`, and `chi(u+a) != chi(v+a)`, then exactly one of `u+a`, `v+a` is a nonzero square and the other a nonsquare; so `(u+a)^((p-1)/2) = 1` for one and `-1` for the other, one root lies in `G_+` and the other in `G_-` (a root of the shifted `G` is a root of `Z^((p-1)/2) - 1` iff its character is `+1`, of `Z^((p-1)/2) + 1` iff it is `-1`). Both parts are then nonconstant, their degrees sum to at most `d`, and the smaller has degree at most `floor(d/2)`. The number of `a` with `chi(u+a) chi(v+a) = -1`: `sum_(a != -u,-v) chi((a+u)(a+v)) = -1`, because the quadratic `a^2 + (u+v) a + uv` has nonzero discriminant `(u-v)^2` (the standard evaluation of a quadratic character sum), so the count of `a` outside `{-u,-v}` with product `-1` is `((p-2) + 1)/2 = (p-1)/2`, at least `(p-3)/2` of them nonzero. Every residue is taken by the draw with probability `3/2^256` or `4/2^256`, and `4/2^256` for all but `p - r` of them (4.1.1), so the `(p-3)/2` nonzero values of `a` listed have together probability at least `(4 (p-3)/2 - (p - r))/2^256 = w` (a zero draw is replaced by 1, which only adds probability). A part is always a divisor of `G`, so the degree is nonincreasing whatever happens in a round that is not of this kind. Conditional on any history of earlier rounds, the next `a` is made of fresh random words, so every round is of this kind with probability at least `w`, and at most `ceil(log2 DMAX)` such rounds bring `d <= DMAX` to 1 (16 -> 8 -> 4 -> 2 -> 1). The failure probability is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = 2.371e-15 (2^-48.58)`. This is a proved bound under the random words, not a premise and not a sample.

### 9.5 The premise `H-NORMAL` (bradcush's premise, entries e6dcb600 and 1aa56884, with the allowance and the organizer-run tests of gta6rp's entry fe269c23)

**Premise `H-NORMAL`** (akki-rock05 `eebae39d`: for the Graeffe-transformed pair of 4.3G). For the centre `c` uniform on `F_p`, the Euclidean remainder sequence of `(g_c^(31), R_c - 1)`, where `g_c` is the monic odd part of section 3 (degree `m = 3,725,290,298,461,914,062`), `g_c^(31)` its transform after 31 Graeffe steps (4.3G, monic of degree `m`) and `R_c = S^((p-1)/2^32) mod g_c^(31)`, is normal down to its gcd (`deg(R_c - 1) = m - 1` and every quotient has degree 1) except with probability at most `delta = 0.001` (`2^-9.966`).

Four fields (as in claim.json). **Role:** score-critical for the success probability only. The time and memory bounds hold for every sequence: stage D is charged for the normal sequence, every division tests its quotient and every call its return, and on any other case the trial ends after a prefix of the charged work (6.3). **Scope:** the pairs `(g_c^(31), R_c - 1)` (4.3G) of the target `poseidon-orchard-r21-prefix-v1`, `c` uniform on `F_p`; nothing is claimed for other round counts. **Extrapolation and evidence:** for a uniformly random pair of degrees `m` and `m - 1` the sequence is abnormal exactly when one of the `m` principal subresultant coefficients vanishes; each is a nonzero polynomial of degree at most `2m` in the coefficients, so by Schwartz-Zippel the probability is at most `2 m^2 / p < 2^-129.6`. That bound does not transfer directly, because the coefficients of `R_c` have degree about `p` in those of `g_c`; the premise asserts far less than random-pair behaviour, an abnormality probability of at most `delta = 0.001`, which is all the bound of 9.2(d) uses (every `delta <= 0.0030999` keeps it at least 0.39). (This entry: the base's untransformed organizer runs cited next concern `(g_c, R_c - 1)` and are not support for the restated premise; the organizer-run tests of the transformed pair are the -g31 entries of 10.5.1, predictions until a report exists.) Measured support, organizer-run (10.5.1): the experiments `euclid-normal-n2-t256-l2-a` to `-l2-f`, `euclid-normal-n3-t24` and `euclid-normal-n4-t2` compute the complete sequence of `(g_c, R_c - 1)` for this construction on the truncations `F_2`, `F_3`, `F_4` of the digest polynomial (10.3; `m = 12, 62, 312`), the first six for 256 organizer-seeded trials of two centres each (3,072 sequences at `m = 12`), the others for 24 and 2 organizer-seeded centres, and return a witness pair exactly when the sequences are normal; zero abnormal sequences is a reproducible observation consistent with the premise, and no population bound is drawn from it (`delta = 0.001` is the declared premise). Our runs of the same program on local seeds: 3,098 sequences at `m = 12`, `62`, `312`, every quotient of degree 1 (10.5.1). Reported by our earlier entries, not organizer-run (10.5): the complete sequences on the sibling targets with `r' = 0` and `r' = 1` partial rounds (`m = 7,812` and `39,062`), every quotient of degree 1 in all 10 runs. **Limitations:** the organizer-run tests reach `m = 312` (the sibling runs `m = 39,062`), far below `m = 3,725,290,298,461,914,062`. Normality is computed inside the submitted program; the runner checks only the returned witness pairs; the program is printed in full in `experiments/exp_euclid.py`.

## 10. Evidence

This section is the evidence for the premises `H-ONE` and `H-NORMAL` and for the digest of the target. The computations of 10.3 are ours; the experiments of 10.2 are run by the organizer's runner. None of it enters `success_probability` or the bound of section 9, and none is a lower bound on the probability of `E_c`.

### 10.2 The organizer experiments declared in `experiments/manifest.json`

Sixteen experiments of kind `python-message-pairs-v1` (five here, eleven in 10.5.1), run by the organizer's own experiment runner (the Orchard digest of the target is called by the runner). The three Python sources are 59,147 bytes together (with the -g31 option of akki-rock05 `eebae39d`) (the limit for experiment sources is 65,536).

(a) `lowbits-birthday` (`experiments/exp_lowbits.py`, kind `python-message-pairs-v1`, event `digest-xor-mask` with mask `fffc` followed by 30 zero bytes and expected value zero). For each organizer trial the program searches at most 1200 fresh inputs derived from the trial seed for two distinct canonical messages whose digests of the selected target `poseidon-orchard-r21-prefix-v1` agree in the first 14 bits of the big-endian reading, and returns the pair (or two nulls). Its source is 15,748 bytes (the limit for experiment sources is 65,536). Its event is a reduced one on the digest of the selected target: the program computes its candidates with its own copy of the permutation (constants embedded), and a returned pair counts only if the organizer's callback gives digests that agree in those 14 bits, so a pair is accepted only when that copy agrees with the target. The digest map so checked is the map whose line polynomial `F` the premise concerns.

The experiment is run by the organizer's own experiment runner (python-message-pairs-v1, the Orchard digest called by the runner), and the intake report of that run is the evidence: 256 of 256 trials returned a verified pair at r = 21, and the output was byte-identical on repetition. Our own earlier local run of the same events (plain Python on our machine) agreed: 256 of 256 trials.

(b) `line-ladder-w6`, `line-ladder-w8`, `line-ladder-w10`, `line-ladder-w12` (`experiments/exp_line.py`, event `digest-xor-mask` on the first 6, 8, 10 and 12 bits of the digest, expected value zero). The program is the line construction of section 2 for the target at r = 21: it builds the line `j = 0` of the first two rounds (the point `Q`, the direction `(a, b)`, the vectors `alpha` and `beta`), evaluates `F(W)` as the remaining twenty-seven rounds applied to `alpha + beta W` (`deg F = 5^27`), and maps a point `W` back to the canonical pair `(nk, rho)` with the inverse S-box `x -> x^e` of 2.1 and 2.2. For each organizer trial it takes a centre `c` from the trial seed, scans the antipodal pairs `W = c + s`, `W = c - s` for `s = 1, ..., 150`, and at the first pair whose digests agree on the masked bits it maps both points back, checks both messages against the full permutation inside the program and returns them (else two nulls). A returned pair counts only when the runner's own digest of the two canonical messages agrees on those bits, so each counted trial is a pair of antipodal points of the line construction whose digests `F(c+s)` and `F(c-s)` agree at width `w`: the reduced-width form of the event `F(c+s) = F(c-s)` that the premise `H-ONE` is about (a root of `g_c`). The count of returned pairs at each width is a reproducible observation of the construction's own antipodal pairs on the target; no probability, rate or population bound is drawn from it (public organizer seeds; nothing is assumed about the seeded trials being independent or identically distributed), and it does not enter section 9.

The intake report of the organizer's run records 231, 118, 33, 14 of the 256 trials with a verified pair for `w` = 6, 8, 10, 12 respectively, and byte-identical output on repetition. 

### 10.3 Computed theorems and computations for the generic line (Grok, jobs 135 and 136)

Grok (xAI), our research partner, computed the hypotheses (a) and (b) of this section exactly over the Pallas field for a toy permutation, by exact computation (the cycle types, factorisations and leading coefficients below are the printed results): width 3, S-box `x -> x^5`, `M = [[2,1,1],[1,2,1],[1,1,2]]` (every minor nonzero mod `p`), round `i` adds the constants `(3i+1, 3i+2, 3i+3)`, every round full, output coordinate 0, on the generic line `(L, 2L+1, 3L+5)`. Notation as in 9.1: `D = deg F`, `G(c,t) = (F(c+t) - F(c-t))/(2t) = H(c, t^2)`, `m = (D-1)/2`; the cycle types below are those of `H(c, u)` (or of `F(x) - a`) at the stated values over `F_p`, which by Dedekind give elements of the arithmetic monodromy.

* **Theorem A (one full round).** `D = 5`. The curve `G = 0` is absolutely irreducible (`F'` has 4 simple roots, so `u` is not a square in the function field); the cycle types of `F(x) - a` at `a = 8, 1, 5` are `(5)`, `(4,1)`, `(2,1,1,1)`, so the arithmetic monodromy is `S_5`. The pair scheme `G(c,s1) = G(c,s2) = 0` is geometrically reduced and of pure dimension 1, and its part off `s1^2 = s2^2` has exactly one absolutely irreducible component defined over `F_p`: the resultant in `c` of `G(c,s1)` and `G(c,s2)` is a constant times `(s1-s2)^4 (s1+s2)^4 Phi(s1,s2)` with `Phi` of degree 8, and `Phi` is irreducible at specialisations of `s1` over `F_(p^k)` for `k = 2, 4, 8`, hence absolutely irreducible. So the hypothesis holds with `w = 1`, with no further assumption.
* **Theorem B (two full rounds).** `D = 25`, `deg H = 12`. The cycle types of `H(c,u)` at `c = 1, 9, 103` are `(12)`, `(11,1)`, `(7,1,1,1,1,1)`; a 12-cycle, an 11-cycle and a 7-cycle (7 is prime and at most 12 - 3) give, by Jordan's theorem, `A_12` inside the arithmetic monodromy, and the 12-cycle is odd, so it is `S_12`; the geometric monodromy is `A_12` or `S_12`, both 2-transitive. Hence `G = 0` is absolutely irreducible, the pair scheme is geometrically reduced of pure dimension 1, and the off-diagonal scheme `{H(c,u1) = H(c,u2) = 0, u1 != u2}` in the coordinates `(c, u1, u2)` is absolutely irreducible.
* **Theorem D (degrees).** For every `N <= 17` rounds and every listed line and schedule, the output coordinate has degree exactly `5^N` over `F_p` (the leading coefficient is an integer, nonzero mod `p`). This is the fact of section 2.3 (`deg F = D`) for the toy.
* The axis line `(L, 0, 0)` is a different case (Theorem C): there `F = R(X + c0)^5` is decomposable, its geometric monodromy is imprimitive, and the hypothesis fails (`w = 0`). The theorems above are for the generic line.

Our line is generic in this sense. The polynomial that the construction of section 2 produces is dense: in our miniature runs (`p` of 20 and of 24 bits, `r` up to 4, run twice with identical digests of the coefficient vectors) every coefficient of the digest polynomial in `W` is nonzero up to the 0 to 2 zeros expected of a random polynomial, each residue of the exponent modulo 5 and modulo 25 carries its fair share, and the polynomial `g` that the algorithm builds is dense likewise. This is evidence for `H-ONE` at one and two rounds on a generic line, with the group-theoretic certificate (an `m`-cycle, an `(m-1)`-cycle and a prime cycle of length at most `m - 3`) that proves it for any further explicit `F` it is computed for.

**Grok job 136 (first N full rounds, Orchard parameter tuple, generic line) and its re-run on the deployed constants.** Grok (xAI) computed the hypotheses (a) and (b) of this section exactly over the Pallas field for the Orchard tuple (width 3, S-box `x -> x^5`, `R_F = 8`, `R_P = 56`) and the generic line `(L, 2L+1, 3L+5)`, for the first `N = 1, 2, 3, 4` full rounds, with the round constants and MDS produced by the Hadeshash Grain generator and the same group-theoretic certificate as in Theorems A and B. Results: degree exactly `5^N` with a nonzero leading coefficient; `F'` has `5^N - 1` simple roots; (a) `G = 0` is absolutely irreducible and (b) the pair scheme is geometrically reduced of pure dimension 1 at `N = 1, 2, 3, 4`; `w = 1` at `N = 1` (the cofactor `Phi` of degree 8 of the eliminant is absolutely irreducible); at `N = 2` and `N = 3` the arithmetic monodromy of `H` is `S_12` and `S_62` (cycle types `(12)`, `(11,1)`, `(7,1^5)` at `c = 11, 10, 457` and `(62)`, `(61,1)`, `(59,1^3)` at `c = 57, 60, 152`), so the off-diagonal `u`-scheme is absolutely irreducible; at `N = 4` the cycle types `(312)` at `c = 349` and `(311,1)` at `c = 56` give a transitive, 2-transitive monodromy, which gives (a) and (b).

The Grain output differs from the deployed table (the organizer constants that `experiments/exp_line.py` embeds and that the runner's digest uses), so we ran the same program, unchanged, on the deployed constants and on the construction's own line: `F_N` is coordinate 0 after the first `N` S-box layers of the digest polynomial of section 2.3 (start state `alpha + beta W`; layers = rounds 2 and 3, full, then the partial rounds 4 and 5), so `F_N` has degree `5^N` and is the truncation of the polynomial `F` of the premise (`N = 27`; the line and the first layers do not depend on r). The results:

| N | layers of `F_N` | `deg F_N` | `m` | cycle types of `H(c,u)` found (value of `c`) | (a), (b) | `w` / off-diagonal scheme | monodromy of `H` |
|--:|---|--:|--:|---|:-:|---|---|
| 1 | round 2 | 5 | 2 | (2) at 3, (1,1) at 1 | yes | `w = 1` (`Phi` of degree 8 absolutely irreducible: irreducible of full degree over `F_(p^k)`, `k` = 2, 4, 8) | `S_2` |
| 2 | rounds 2, 3 | 25 | 12 | (12) at 8, (11,1) at 18, (7,1^5) at 1644 | yes | off-diagonal scheme absolutely irreducible | `S_12` |
| 3 | rounds 2, 3, 4 | 125 | 62 | (62) at 82, (61,1) at 24, (59,1^3) at 622 | yes | off-diagonal scheme absolutely irreducible | `S_62` |
| 4 | rounds 2, 3, 4, 5 | 625 | 312 | (312) at 121, (311,1) at 357 | yes | not computed | transitive and 2-transitive |

For every row the spot check of `F_N` against direct iteration of the rounds passed, the leading coefficient of `F_N` equals the one propagated through the layers (section 2.3), `F_N'` has `5^N - 1` simple roots, and `H(c,0) = F_N'(c)` at `c` = 1, 2, 5, 17. The cycle types are those of the square-free specialisations of `H(c,u)` at the stated `c`; for `N = 1` the discriminant of `H` is not a square (odd-exponent factors of degrees 2 and 2), and for `N = 4` the Jordan prime cycle `(307,1^5)` was not met in 929 specialisations (expected count 0.025), so the single-component statement is not made at `N = 4`.

So (a) and (b) hold for `F_N` at `N = 1, 2, 3, 4` on the deployed constants and the construction's line, `w = 1` at `N = 1`, and the monodromy of `H` is `S_m` at `N = 2` and `N = 3`. The premise `H-ONE` (9.1) extrapolates the measured trend (`w = 1` at `N = 1, 2, 3` on the deployed constants, below) to `N = 27`.
Under (a) and 2-transitivity of the monodromy of H, w is 1 or 2 (Grok job 137, lemma: with the arithmetic monodromy Gamma inside the hyperoctahedral group B_m, K = Gamma meet F_2^m is one of 0, <1>, E, F_2^m once pi(Gamma) contains A_m, and w = 1 exactly when K contains the even-weight subspace E, w = 2 otherwise; the witnesses of Grok job 136 establish the hypotheses). Measured on the deployed Orchard constants and the construction's own line (the F_N of proof.md 10.3, using the Frobenius cycle types of H(c, u) and their lifts to G(c, t) = H(c, t^2) over F_p): N = 1 gives K = F_2^2 and w = 1; N = 2 (m = 12) gives K = F_2^12 and w = 1, witnessed by the 12-cycle specialisations c = 8 (two 12-cycles on G, omega = 0) and c = 24 (one 24-cycle, omega = 1) and the even permutation c = 6; N = 3 (m = 62) gives K = F_2^62 and w = 1, witnessed by the 62-cycle specialisations c = 82 (omega = 0) and c = 102 (omega = 1) and the even permutation c = 1. So w = 1 at N = 1, 2, 3 on the deployed constants, a measured trend, and the lemma gives w = 1 or w = 2 given (a) and 2-transitivity.

**Grok job 139 (the counts of the premise on toy copies).** Grok (xAI) computed `N*` and `N_off` exactly for width-3 Hades toy permutations over prime fields `p < 2^22` with `p mod 5 != 1` (S-box `x -> x^5`, uniformly random MDS matrix and round constants, the line `(L, 2L+1, 3L+5)`, `N` full rounds and `k` partial rounds, `deg F = 5^(N+k)` up to 1,953,125), by the fibre counts `N* = sum_y m_y (m_y - 1)` and `N_off = sum_c 4 r(c) (r(c) - 1)` (checked against brute force on the small cases), on 1,316 generic seeds with `p >= 1024` (the five degenerate seeds, where the degree drops, are excluded). The relative error `eps_obs = max(|N*/p - 1|, |N_off/p - w|/w)` with `w = 1` is `<= 0.2197` for every generic seed with `p >= 2053`, and the least-squares fit is `eps_obs = 3.10 / sqrt(p)` for a typical seed (`5.17 / sqrt(p)` for the maximum of four seeds), with no dependence on the degree (adding a term linear in `deg F` moves `R^2` from 0.5508 to 0.5509; the mean of `eps sqrt(p)` is 2.3 to 3.7 for every degree from 5 to 1,953,125); at `p = 2,097,169` the largest generic `eps_obs` is 0.0068. These counts support the premise of 9.1: the deviations shrink like `3 / sqrt(p)` and do not grow with the degree.

### 10.5 Euclidean sequences on the sibling targets

The algorithm of section 4 at `r = 21` applies the Euclidean algorithm to `g_c` (degree `m = 3,725,290,298,461,914,062`) and `R - 1`, `R = S^((p-1)/2) mod g_c` (the base algorithm; 4.3G applies it to `g_c^(31)` and `R = S^((p-1)/2^32) mod g_c^(31)`, 4.3G, and the runs of this section are of the untransformed pair). This section and 10.5.1 are the measured support of the premise `H-NORMAL` (9.5): stage D is charged for the normal remainder sequence and a trial ends at the first quotient of degree other than 1 (6.3). The digest polynomial of the same family at `r' = 0` and `r' = 1` partial rounds (same constants, same line `j = 0`, `F` of degree `5^6 = 15,625` and `5^7 = 78,125`, `m = 7,812` and `39,062`) is small enough to run the stage in full with `python-flint`: for each centre `c` we built `F(c + x)`, its odd part `g_c`, `R` by powering and the complete Euclidean sequence of `(g_c, R - 1)`. Results (centres `c` = 1, ..., 8 at `r' = 0` and `c` = 1, 2 at `r' = 1`): every quotient had degree 1 in all 10 runs, the sequences ended at the gcd (degree 0, or degree 1 at the r' = 0 centres 2, 4, 7) after `m - deg gcd` divisions, and at `r' = 0` the gcd had degree 1 (a usable root, a collision of the sibling target) at the centres 2, 4 and 7. Each `r' = 0` run takes about 20 s and each `r' = 1` run about 6 minutes on one core.

At `r = 21` the stages need about 477097308158 GB and 1.1e24 operations, which the organizer sandbox (128 MiB, 20 s) does not host; the counts at this `r` are the formula counts of sections 6 and 7.

### 10.5.1 Organizer-run tests: normality and good centres (`experiments/exp_euclid.py`)

Eleven experiments of kind `python-message-pairs-v1` (akki-rock05 `eebae39d`: the eleven of `213552fe` in their -g31 forms; the manifest holds at most 16 entries), declared in `experiments/manifest.json` and run by the organizer's runner, use the program `experiments/exp_euclid.py` (26,245 bytes with the -g31 option of akki-rock05 `eebae39d`, Python standard library only); program and entries are those of our accepted r = 9 entry `5b96dbb5`:
- (in the base `213552fe`) `euclid-normal-n2-t256-l2-a` to `-l2-f` (six entries; two centres per trial, 512 sequences each, 3,072 at `m = 12`), `euclid-normal-n3-t24` and `euclid-normal-n4-t2` (one centre per trial, the first 24 and 2 trials, `m = 62`, `312`);
- `euclid-gcdpos-n2-t256-a`, `-b` and `euclid-gcdpos-n3-t24` (one centre per trial; 256, 256 and the first 24 trials; `m = 12`, `62`).
- (akki-rock05 `eebae39d`) the same eleven entries in the Graeffe form of 4.3G, suffix `-g31` (`euclid-normal-n2-t256-l2-g31-a` to `-g31-f`, `euclid-normal-n3-t24-g31`, `euclid-normal-n4-t2-g31`, `euclid-gcdpos-n2-t256-g31-a`, `-g31-b`, `euclid-gcdpos-n3-t24-g31`): 31 Graeffe steps on the odd part, the identity `g~(9) = g(3) g(-3)` checked at every step, `R = X^((p-1)/2^32) mod g^(31)`, the pair `(g^(31), R - 1)` that stage D of this entry runs on; for the good-centre form `deg G >= 1` exactly when `k(c) >= 1` (lemma of 4.3G). This entry declares the eleven entries in the -g31 form only (the base's untransformed entries and their reports remain those of `213552fe`); the -g31 good-centre entries flag the same centres as the base's (`deg G >= 1` exactly when `k(c) >= 1`), and the -g31 entries are predictions until a report exists.

The design of the normality tests follows gta6rp's organizer-run normality tests (entry fe269c23, its 10.5.1); the program is our own.

**The common part.** For each centre the program builds, exactly over `F_p`, the polynomial `F_N(c + X)`: the `F_N` of 10.3 (start state `alpha + beta W` of the line `j = 0`; the S-box layers of rounds 2 and 3 (full), then 4 and 5 (partial, coordinate 0); the MDS after each; degree `5^N`). Then:
1. It checks `F_N` against direct iteration of those layers at `c + 1`, `c - 1`, `c + 2`, `c - 2`, and the odd-part identity `2 x g(x^2) = F_N(c + x) - F_N(c - x)` at `x = 1, 2`.
2. It takes the monic odd part `g` (degree `m = (5^N - 1)/2`) and computes `R = X^((p-1)/2) mod g` (253 squarings and 45 multiplications by `X`); in the -g31 form it first replaces `g` by `g^(31)` (31 Graeffe steps) and computes `R = X^((p-1)/2^32) mod g^(31)` (222 squarings).
3. It runs the complete Euclidean sequence of `(g, R - 1)` down to the zero remainder, recording the degree of every quotient. The sequence is normal when `deg(R - 1) = m - 1` and every quotient has degree 1, the condition of 6.3 and 9.5. Its last nonzero remainder is `G = gcd(g, R - 1)`, and `k(c) = deg G` (in the -g31 form `G = gcd(g^(31), R - 1)`, and `deg G >= 1` exactly when `k(c) >= 1`, `deg G <= k(c)`, lemma of 4.3G).

**The normality entries.** The first centre of a trial comes from the trial seed (the rule of `exp_line.py`); the second, for `-l2`, from the seed and its index. A trial is flagged when all its sequences are normal and all checks pass.

**The good-centre entries** (premise `H-ONE`, 9.1): one centre per trial from the trial seed; a trial is flagged ONLY when the checks pass and `deg G = deg gcd(g, R - 1) >= 1` (`k(c) >= 1`, a usable root), so the organizer's returned-pair count is the good-centre count.

**The witness.** A flagged trial returns two distinct canonical messages. The points `c + 1, c + 2, ...` of the line are mapped back to `(nk, rho)` as in 10.2(b), and the first two whose digests of the selected target agree on the first 6 bits of the big-endian reading are returned; among 65 points such a pair always exists. Every other trial, and every trial past the first `T` (`T` = 256, 24 or 2, the sandbox budget of 20 s), returns two nulls. The organizer-checked count of returned pairs is therefore the number of flagged trials. The per-trial counts are reported as observations, which the runner labels untrusted. For `N <= 4` the polynomial `F_N` is the same at every round count `r >= 2`, because its layers come before the final full rounds; only the witness uses the digest at r = 21.

**Expected outcomes** (fixed in the manifest).
- Normality: 256 of 256 pairs for each `-l2` entry, 24 of 256 and 2 of 256 for `n3-t24` and `n4-t2`; zero abnormal in the 3,072 sequences at `m = 12`. A reproducible observation consistent with `H-NORMAL`; no bound on the abnormality rate is drawn from it (public organizer seeds; nothing is assumed about the seeded trials being independent or identically distributed).
- Good centres (9.3(a), (c); at `m = 12` and `62` the law is a theorem, `0.39346933 <= P(1 <= k(c) <= 16) <= 0.39346944`): the returned counts are reproducible observations consistent with that law; no probability, rate or population bound is drawn from them (public organizer seeds; nothing is assumed about the seeded trials being independent or identically distributed).

**Our runs** (2026-10-21, seeds of our own, plain Python 3.14 on our machine, the program as attached; file `run_local.out` of our build, not attached):
- Normality: 256 of 256 pairs for each of the six `-l2` entries (3,072 of 3,072 sequences normal), 24 of 24 for `n3-t24` and 2 of 2 for `n4-t2`: 3,098 sequences, every quotient of degree 1; 6.6 to 7.1 s for each `-l2` entry, 5.4 s and 5.2 s for `n3-t24` and `n4-t2`.
- Good centres: 106 and 100 of 256 at `m = 12`, 12 of 24 at `m = 62` (3.7 to 5.5 s).
- (akki-rock05 `eebae39d`, the -g31 form; the program of their r = 10 entry `9a6e5a1a` and r = 9 entry `479bd57c`, observations, not organizer results) normality: 1,024 + 24 + 2 transformed sequences at `m = 12, 62, 312`, every quotient of degree 1; good centres: 101 of 256 and 7 of 24; on 24 common seeds the gcd degrees with and without the prefix were identical.

**What these tests show.** The construction's own pairs `(g_c, R_c - 1)`, and in akki-rock05's local -g31 runs the transformed pairs `(g_c^(31), R_c - 1)`, have normal remainder sequences at `m = 12` to `312`, and the returned good-centre counts at depths 2 and 3 are consistent with the law of 9.3(a).

**What they do not show.** Anything at `m = 3,725,290,298,461,914,062`, where `H-ONE` and `H-NORMAL` remain premises. Nor any probability, rate or population bound: none is drawn from the organizer-seeded counts.

## Appendix G: the ledger of the Graeffe prefix and of the new rows (the charges of akki-rock05 `eebae39d`, its Appendix G)

akki-rock05's ledger program of the prefix (`eebae39d`, its Appendix G, standard library only; the charges itemised in 4.3G) was re-run with the extension of 4.3G (iii)(b) (`X_CONV = 1,094,023,911,451,598,580,254` in place of `1.5 GEO + 14 n1 = 1,651,730,184,913,170,509,723`); its items, and the new rows of this package:

| item | operations |
|---|---:|
| one extension between cosets of `H'` (`EXT2`, 4.3G (ii)) | 1,549,426,741,615,009,626,096 |
| Graeffe pass (4.3G (i)) | 29,802,322,457,482,702,644 |
| one Graeffe step: the pass and one extension | 1,579,229,064,072,492,328,740 |
| 31 steps | 48,956,100,986,247,262,190,940 |
| prefix set-up (own tables and allocations, `g` on `O1` and `O2`) | 2,234,703,429,526,474,492,747 |
| interpolation of `g^(31)` | 4,971,376,371,377,913,332,454 |
| prefix total | 56,162,180,787,151,650,016,141 |
| the 31 loop steps with `b = 0` that the prefix removes | 94,126,998,355,640,853,755,224 |
| the loop of stage C: 163 steps, 45 with `b = 1` | 495,303,015,707,028,346,521,592 |
| **row C** = `606,998,556,432,298,400,337,481` - removed + prefix | **569,033,738,863,809,196,598,398** |
| **row F** = `47,012` + `t = y^u` (`6,000`) + `308` (the loads of L.3 before the scan) + `2^31 * 1,400` (the scan) | **3,006,477,160,520** |
| **row B** = `15,312,515,339,265,429,643,596` - `7,450,580,601,318,408,192 * (657 - 387)` + `178,098,276,972` (the loads of L.3) + `1` (`c' = c + E0_0`) (Appendix L) | **13,300,858,577,087,557,708,729** |
| **row D** (4.4, 4.4.2 item 1 with the aligned split; our program) | **477,848,936,324,260,928,287,843** |
| **N_max** (the rows of section 6) | **1,060,183,533,768,181,510,310,184** |

The scan with `L` executes `1 + 2 + 2 (387 + 2) + 2 + 3 + 1 = 787` operations per candidate and is charged `1,400` (4.3G).

## Appendix G2: toy-size checks of the prefix

akki-rock05's entry `eebae39d` (its Appendices G2 and G3; the program of their r = 9 and r = 12 entries `479bd57c` and `bdc5ccfe`, and its H^2 form) runs the construction of 4.3G over the Pallas field at `h = 2^4`, `K = 3`, `m = 40`, 8 steps (the zeta form) and at `h = 2^5`, `h' = 2^4`, `K = 3`, `m = 94`, 6 steps (the H^2 form of this round), and checks the pairing, the output positions, the extension and the interpolation against the coefficient-domain Graeffe transform and direct evaluation; we re-ran both unchanged (outputs `ok steps 8 h 16 K 3 m 40` and `ok steps 6 h 32 hp 16 K 3 2K 6 m 94`). The construction does not depend on the round count.

## Appendix L: the line program `L` (the form of mpjunior92, entry `c667182d`, its Appendix L; credited)

### L.1 Construction

`L(x) = F(x - E0_0) / OUTSCALE`, `F` the digest on the line of 2.2 (`W = tau^5`). The state after round 1 is `A + W B` (2.2: `alpha = A + c_2`, `beta = B`); the round-2 S-box input of lane `i` is `A_i + c_{2,i} + W B_i = B_i (W + E0_i)`, `E0_i = (A_i + c_{2,i}) / B_i` (every `B_i != 0` on the deployed constants). With `x = W + E0_0` lane 0 is `B_0 x` and lane `i` is `B_i (x + e_i)`, `e_i = E0_i - E0_0`: the program starts with `y1 = x + e1`, `y2 = x + e2` (2 additions) and holds lane `i` as `y_i` with the scale `B_i`. Every lane is held as its true value divided by a known nonzero scale: an S-box of a held lane is the true S-box output divided by the fifth power of the scale (3 multiplications), and the fifth powers are folded into the next linear layer, each output lane being held divided by its coefficient on `z0`: a dense layer with the next round's constants is `y_i = z0 + a_i z1 + b_i z2 + k_i` (2 multiplications, 3 additions per lane). Partial rounds use the sparse form of Grassi, Khovratovich, Rechberger, Roy and Schofnegger (USENIX Security 2021) with the same scaling, as in the r = 56 entries `3a1b25b6`, `9fb982e8` and `69e14209`: lane 0 is held as `lambda h0 + gamma`, lanes 1, 2 as `P (h1, h2) + q` with `P = Mww^j P0` after `j` partial rounds (`Mww` the lower-right 2x2 block of `M`) and `P0 = Mww^-r D`, `D` diagonal, so `P` is diagonal at the exit; one partial round is `u = h0 + k`, `x5 = u^5` (3 multiplications), `h0 = x5 + n1 h1 + n2 h2`, `h1 = h1 + v1 x5`, `h2 = h2 + v2 x5` (`h0` from the old `h1`, `h2`): 12 operations. Counts: entry 2; round 2 (S-boxes 9, dense layer with the round-3 constants 15); round 3 (S-boxes 9, into the partial form 6 multiplications and 6 additions, `D` normalising the `z0` coefficients); `r` partial rounds, 12 each; exit 3 (the constants of the first final full round); the next three full rounds (24 each); the last round (S-boxes 9, row 0 held divided by its `z0` coefficient `OUTSCALE`, 2 multiplications and 2 additions): `2 + 24 + 21 + 12 r + 3 + 72 + 13 = 135 + 12 r = 387` at r = 21. Every constant is a closed formula of the deployed constants (preprocessing: the 154 constants of L.5 are derived once, offline, by the closed formulas of this section from the organizer constants; counted exactly: 786 additions and subtractions, 1,032 multiplications, 49 fifth powers (3 multiplications each) and 112 inversions, 1,965 field operations besides the inversions; charged by the rule of 4.2 for small-degree work, 10 per field operation (the operation, 2 loads, 1 store, 6 control operations), an inversion as its 330 field operations at 10 and its 2,310 bit-loop control operations, and 324 per output constant as in 6.2(d): `10 * (1,965 + 330 * 112) + 2,310 * 112 + 324 * 154 = 697,866`; with the `138,785` of 6.2 and 6.2a, `T_off <= 836,651 < 1,000,000`, the declared cap of 6.2).

### L.2 Check

At r = 21: `E0_0 = 0x3a4bd2e80f62c6cde67f816c4a67f17bbd43a70c4d2fca9784cc22ba736569ff`, `OUTSCALE = 0x3e70c93c30abab83d881d370ab03b436cf10fa2e92f238b7a86392d0442658e9`. The form is mpjunior92's (`c667182d`, checked there at r = 0, 1, 3, 9 and 12). Our builder of L.5 and L.6 (standard library only, from the organizer constants file) gives `387` operations at r = 21; the listing of L.6, executed with the constants of L.5, satisfies `OUTSCALE * L(W + E0_0) = digest(message(W))` with the reference rounds of `verifier/poseidon.py` at r = 21 at 20 random `W` (20 of 20); `message(W)` is the canonical pair of 2.2 (`tau = W^e`, `(U, V) = Q + tau (a, b)`, `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`).

### L.3 Stage B

The loop of stage B and its charges are those of section 3 except that each evaluation is one execution of `L` (`387` operations) at `c' + s` and `c' - s` (`c' = c + E0_0`, one addition per trial). The `154` constants of L.5 are loaded into `154` of the 256 field registers at the start of each of the `578241159` cosets (a load and an address operation each, `578241159 * 2 * 154 = 178,098,276,972` per trial); `L` works in 16 further field registers. Stages C, D and E use the field registers, so the scan of stage F loads the `154` constants once more before it starts (`2 * 154 = 308`, row F) and then runs `L` in the same registers. The values become `g_c / OUTSCALE`, which the normalisation to monic absorbs; the scan compares `L(c' + s)` with `L(c' - s)`, which is the comparison of `F(c + s)` with `F(c - s)` (`OUTSCALE != 0`). Row B: `15,312,515,339,265,429,643,596 - 7,450,580,601,318,408,192 * (657 - 387) + 178,098,276,972 + 1 = 13,300,858,577,087,557,708,729`.

### L.4 Code and static data added to the footprint

`L` once, as a subroutine used by stage B and the scan: 387 instructions and its 154 constants at 32 bytes, and the call site (at most 20 instructions). At most `16 * (387 + 20) + 32 * 154 = 11,440 <= 32,768` bytes (16 bytes per instruction, as in 7(a)); `32,768` bytes are added to the footprint (section 7).

### L.5 Constants of `L` at r = 21

```
e1 = 0x3be50976ed9a36ed2193914455ff9b57110fbf67a5b17ed704b45f293ea16e52
e2 = 0x3f30a282c5b89b63ebabd204830a688ed50a9b6efae93b0434327bc6ee6794ba
r2_a0 = 0x3c6619d59a8bff38f5e82d878afa1572b0de568df0f44727f5eebde8a520bb09
r2_b0 = 0x182d2a33a05d2cf29f1f85fe18c296f96b485a4642bc47e0c096ed309334539d
r2_k0 = 0x2ee7536394e8e06338e11ac0050022dbb3b058a98b297c7058173227f0c5f0b5
r2_a1 = 0x2840fd97d3b51c865aebbadaaf03e4d7bb8a06a0ed729dcfdcb232668cc21036
r2_b1 = 0x24d83320489d9f6acf96dd55a02381c22b9ae568c345217a4d3a3ebc6c68733e
r2_k1 = 0x2ccbdb9536e63c46650cd03d3d3591a809a0e4a07b7c585b6e3b8c06db9ef42e
r2_a2 = 0x37d59d01327c0e9ea9ea53e1bb643c6d9e2dd42b1be96d0ae502e5ad6685ef91
r2_b2 = 0x3890183d51fa8d8e79f20615fc8cdc01a44e932c575a7833d6118362f946104a
r2_k2 = 0x007ee07c6df20f7997f9b145f92b2e13ed55421ba5fd692e198160cbd4b2086e
pf_a0 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
pf_b0 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
pf_a1 = 0x3fb1f3e0134d8809a0eac15a84379e896d0866ff0a15bb9bd3d56966e1244860
pf_b1 = 0x2ba57f9314386a4238b37778c6d6368aff626acf0d223c9ded4cb98d4fed5c14
pf_a2 = 0x3b3127a4556f7218a1a62d754756f35b7ea31c020d554397c2b270a3fd6fcb67
pf_b2 = 0x1250af1964e24c8511cee6fc43414923c0d35c7bdb78b4fd0364024634387e15
p0_k = 0x34058bb8920441623716adeb0155288a2cca42fa34af13309820b9953e4336cf
p0_n1 = 0x18bedc3d63bfc1b9354f9457e3c1fda679f95f01cf9835327bf3f246274dc0f4
p0_n2 = 0x324d47b0bbf27f03cd68de33044ba60c7bfca2a2c78ea67f770aa5b365999a14
p0_v1 = 0x3bd818931086b43c4e022d40459509e7058cacb1103a9ccdf3467bd16aa0e4a8
p0_v2 = 0x28a0a1cc79e508f8ef68e5ad0bdb155b09d8457743cccae061b7585c1ddfa402
p1_k = 0x266144e217c50738f29b2b098b54686e360c94c1f64cc0b43c6b0a0cc37fc9eb
p1_n1 = 0x0ec79cda079923a7b9d435341bf3e1973de4de8999b4c13c1e542a3853dd7054
p1_n2 = 0x36850ed66efeb44a02156d3bf31839ca3768dd5527609586236bb11c27a6a624
p1_v1 = 0x1a92db970a19aa1c0c09d78c6f077e3e6b9e35c3505473953584d6685d7b5d55
p1_v2 = 0x0a0b8fca9c33f3cdbd6ab85f2c5fae84a6290f7b23d429b54e1d25e7d3465e4d
p2_k = 0x1565f5ef914944ad12c16e36ec616abd4dd0f8c94d990dc4ff415ad5a506d732
p2_n1 = 0x123e37f5de70c3aebbbbe4dbcde0b1979cbd86303103a14e43d5fb59083ed2c1
p2_n2 = 0x3a37e44af8405846d14a6fff017ce03dc71f62b89581c98f12988c26f66d2e39
p2_v1 = 0x04342665add1f99341e04e50b597ddc863a88ef2753646e08489aefb2236bd61
p2_v2 = 0x3c7568137949420de33e810d987b1c17b9e019a8cb36c47a21e8db770051e53e
p3_k = 0x31f134c3cb80372eff4d98f34741c78bf04e38ca64691c338f55660789f29b61
p3_n1 = 0x0655941da2d7e9a2322485df98c64558bb8d159bd32e36bec40f28fc8ab038d1
p3_n2 = 0x1a47c43ef4320fe9f850c59f1a435caf1cc6176564a0a1b484d5f734b48bd368
p3_v1 = 0x1e6d5ebd33eaeca111ff9edea3c70284d7c500d9ac1563cf37312b272f887b01
p3_v2 = 0x22413eca4e9f772dd1ee516a67b538a2928985ea84feeb1fb71914edeb8a952a
p4_k = 0x2ca8302ed55720cd2a1b9478af5a5f4a223bd4fe9f778963e71519b2113aecb6
p4_n1 = 0x11938a9f8610755512991101a05c40051277b3685c881fe466a613cc87447716
p4_n2 = 0x0a6f27a305299048a280e809f396d73934005b00e9d0ab1c3d0ba35183e47bd6
p4_v1 = 0x3deafb04e7966088474cbdf780a036239c7d5e105f86a90b642cc503b23b96c9
p4_v2 = 0x360c2c3b0597a82a7d7f879c58475dc84a9be819f96954867718a46771085f79
p5_k = 0x0fb74a39edbf99a426252d65ab2f5b558bfc999d3ec24ddad0ab5d3c66a49cba
p5_n1 = 0x3a2c159763d677f0b3f5b5d6177269df4bfd4d2d253a3cb94fa464c909de4cd2
p5_n2 = 0x22b3000c6484babcd5ff35d0ff973a2e87092be015e17e256d3864abc5c6678e
p5_v1 = 0x132ed7625b26675324f65ea989855ba544a4e95685760a7885ee9a804b526a0a
p5_v2 = 0x146423cadd14628cb68bdad1c3cec5daa558f21f1ea1cc78d59083887ee83f0a
p6_k = 0x0111ad1e97070de2c1edeeacffc3a8f1f81c885c649e20b3955b4a2fac77be23
p6_n1 = 0x087e500622f57ca54b9f680e18b3abfd79e0055d6a9ec39437495786a4adf11e
p6_n2 = 0x22072c25aa97744127efee39519100728a61ed662054976234dd9149fe08da3c
p6_v1 = 0x1a76b44eadd050cff028be935a2edbaa4f1eb2a17214129f88658b70ec685694
p6_v2 = 0x3aee4f2f1301b53391756864bce8ca9830450e026047cb8ddf947bbcecbc6635
p7_k = 0x193745c8d553088262dcb58e17e3468dd24422f6a3987ac69306c8d2935e7ff2
p7_n1 = 0x21fac6972f200bf3b23104fc4339cddba3d9b623a8010016f6dd328640154934
p7_n2 = 0x3edc7793cb9fcd55fe911e27e551a81b50fe226f98efea361ac158872ebfc75a
p7_v1 = 0x2ed7baa574422eaacaaa18b8d14b836d428607ded73162f171cc439865cc4a62
p7_v2 = 0x18bb169d1d558a17a015eeae2704c4800c25893fb38195eae6e8492832210254
p8_k = 0x35f659b85ed4e1f3c1c3e1f1fdde5ed7f9eb3b2b83d43f106d2416dba5965f7b
p8_n1 = 0x13fc64d96d6bc320af63d9399b75f82a2cc9d2f0055b62d483fbf749a9a88056
p8_n2 = 0x3ee674e83d693e77986ce4bb19bbc27cd447227a52bbc50ee200f97df7445c48
p8_v1 = 0x0d364bdfe3350f33eacc4f84bcf39a1b2f60a35afe470da36255b928164e787d
p8_v2 = 0x2adb8e677cecc8d3bbfac41c7cfafc11e840a5797d4d4e52ad5fce4c576c6cf6
p9_k = 0x1fb04a7de4c56520f2aaf051fc8ec4eab6978daf4ad22c53ef4fde9bf6100f69
p9_n1 = 0x1a39cd53b657dcfa343104140f4d3c4d2b2a75400b5e3d14b4ef0ac75ab768d5
p9_n2 = 0x0b6fe40e0934748dbeb277e85985562fd02b72e897a963107324fdf20f7ec27e
p9_v1 = 0x21d39f0e326f7ac784d6849b4d5dbc2b36c11f52e10c426737d3df6ee6a70feb
p9_v2 = 0x1202f231b7697e0235645a977d2544dce428ecb82a850839d2c8ed16f7e997ff
p10_k = 0x0194f78e9a984a28533ec9f0ef5d08ac0ef765a3eade233a3b45b21ae5fb06ee
p10_n1 = 0x3ff48e2949e8504ce36f82a8d143e7b5dbf34344f20255f29ceb7501a180f748
p10_n2 = 0x27ed5960e073b7031454f2399fae00e5f6b7ab877c35b74309c55402dc65b5ad
p10_v1 = 0x1420b4821db1a99a5feef4913660464d696e06d6fb7b64f6dfd18f97640a2335
p10_v2 = 0x2d23786d91e9d8e72d738944afeffbf0ff74a39d4d7bc98b11d8a61bdad1e490
p11_k = 0x31a5317e72939ab937a13512d323f3d6e2545604b200351fe2c862a30e2c0059
p11_n1 = 0x332e95150d1de99853c03906966278562422c5bd6af8a5c68fb1e754fbd98bb9
p11_n2 = 0x1ac6b0d3230531caf76976e2679634e428c04b64e5217ddcf7769ed0a691395a
p11_v1 = 0x07b440f63fdd6626c1d3c6161ee0474aead71e9500d7cf2c0eb346827583e502
p11_v2 = 0x1222f2959d2557e38cbc90eb1407eedd8131e1191a498a9f55a1927475eba859
p12_k = 0x1782f320036b1c7bc40a2dd19526d90235056921c75ac9170bfe77cd1becbcb2
p12_n1 = 0x3414f79d8c8c8678a2f42cbfbb1ef9d416d4267d20af15d613dfeab784a072ff
p12_n2 = 0x203c7c7387bdedee0e30400900fd6e0927fa433eaf9220bead95b293cc089aa1
p12_v1 = 0x30e3d876dcc1c35b9dc8d793710ab34568103505e21a4f60c05307039e68f7d3
p12_v2 = 0x1edf5b12523dc7ddfefeb014df07847ab15bca55a9a1b3f053ac8683f500d00a
p13_k = 0x26d9b6dbc2d14b67b0301adf9666424dc64420144c0a37dff3d57b6cacf108c7
p13_n1 = 0x2ff8a7e9f1cac9a4de806fac937195f1438797eff83b56b64d13e97c3b9093e1
p13_n2 = 0x01a19ea7f56e0843fbb6a1b24ed7143b526ea7c48e12eb29562be7f30306cc1f
p13_v1 = 0x36704ad40d2511b64817120b55956e50eefee58681b2f6b5e0e234e5d1ac93af
p13_v2 = 0x3ae6eb11cb98c1170b4339c18e66d0a5b0b3824b4d86d426b4966fc45c069863
p14_k = 0x2bca342742d0580cf65fa95da4684862e4e0e66ed103e200add1a4f1940701ba
p14_n1 = 0x39983b57aa00978ede3625a18c129eee033dedc233cc0dfd562d9d456a1fdc77
p14_n2 = 0x19e27824cbb4e8916404c2629a765c46e7dcb96c77622be91ea918c849a82981
p14_v1 = 0x07b13868daa74cdcdccdd9f2b9fdea80d8d144793b2705f43a11f26022c76b79
p14_v2 = 0x07534f26ec9b8564781dc1bab487bb9f9841fe80938344f4c95d34dae1d35b8d
p15_k = 0x0faa11fee955d83c4d2df7dbd66296897532dab0798f422e29a978527a54c52a
p15_n1 = 0x1ed61ccfc9101d3418e69cff68428a7d315c7c1d5b45ac6564486aba4791aba8
p15_n2 = 0x0138df94be40b2087382616136a968a75d13e2d24bf36fa068e31677ce4705ec
p15_v1 = 0x24385eb0532b94c7497b19b59dc02c0f2dbc690eaa0fe1678ce2521bcd5c7e03
p15_v2 = 0x3c54ccba770e646976b0394061d94d7d7e38a0cfe74bbc18e6c13a71e35fce1b
p16_k = 0x254ff5c8d0e8ce1725d0fabdf7b0b71b6d72caf59a43c2bb470c46d1796b8942
p16_n1 = 0x3c1ef6b2e7444317459a512be5ec867e03fdbdc0c5b4482ac086c91b0e3a039b
p16_n2 = 0x3805720e54444a1a741a99af0cb9f24675df7747bf3ceff67718f2c5090af43d
p16_v1 = 0x0d0a419e9f61c6000a9c3ada8859bcb464f719fedf7d2d445d740302b7f87d65
p16_v2 = 0x1f687402bdb8cdb55abdf68e21f5c3db0e929748170c03f55dee1446f39de0d3
p17_k = 0x25ea21faa636bc6a2490218c0c3504c05f9ec23a15fdf14f291de9c40b522d08
p17_n1 = 0x0a128a7683687f9dc3c27f6a269ae7e4842fc73b0240d2ce6f50739978580dff
p17_n2 = 0x3ca41f2640c620865a82f154bed829fe63df31b5c0c3902e2bcadf6131907dcb
p17_v1 = 0x24a8675bdb0ee4da8dd017b03ba4736307d7f01330139f5763b1ce27911948bc
p17_v2 = 0x210587d5e380482d9d4d9663e60f2ff2504a6041923fb017ee52ffbbb99a1052
p18_k = 0x0b2ad0eca9aed8e6d70a3d50f137bde357ab2a4bb4e98ffe7c4bcdf1ee304c8f
p18_n1 = 0x34760999f52a1724c2dd949a570ffb21afaa0f0158245e986afa0f0794bd6e03
p18_n2 = 0x358c6f48a76d2f46129a4fcce30a27df18ed9bd97f0a846d901af28e8cdad3ad
p18_v1 = 0x22e6ae388aeb567dc8bd3cffc9c0205d92fc3575cc8ce737838469e011764c14
p18_v2 = 0x1d08a275f5724cdbf19ca131a64ab8a4d90e13aea149a136ae77bae83518f31e
p19_k = 0x2442d48cd264e8ec1f580a77f9c5aa3f5177b9d35b6727fc9c9c509afea94997
p19_n1 = 0x2e212b7c45c7481d6439e70928e9458417c36f8c152596c67d561aeebce76cb5
p19_n2 = 0x26424294a458c1bd0a9b75b3855dccc26b6462b68850fd9cfcd20f95dd39e22e
p19_v1 = 0x20319135d11b18952df5157060ddc9bca40360ddaa0cd5d41d034180bd13dedb
p19_v2 = 0x15a611461bfcdda0fe9c1a493f441853178d90f566c50b238cbdce070ee6eb3c
p20_k = 0x150cb1d46369038a25904439b651a4e5d5b8aaea057dc18f4c4864b88d85af06
p20_n1 = 0x06f5a3705be491188387789bc259b7b40ae208524554057583b8a0d714f21f74
p20_n2 = 0x1c29b93d213b01161ebb8b53d41279a0d84b4f3e59465bfd36864a7f4ae70044
p20_v1 = 0x294b3998ba257429d4210687610ea195eee6fd0b695e95b7f97dc4c9728d8f9e
p20_v2 = 0x2adb0b9d2d4923a8da7fc7ccea94efe5b15238d29180e0c76b4778ec62b84a9d
x_k0 = 0x1870e2596b6272e0df4238ead5a160b85ec308f52a2e4bd8f4487e75cab5ecb7
x_k1 = 0x38a314be0cbb8f0bd5037be3ee8f7fc2488b42192de634cff04b709f86f40a80
x_k2 = 0x37ef9381bc10f880b118103c24163c16b4da6e834b564239fc201353951bf424
r60_a0 = 0x3049adc9e8c6b4e6ed736954be5e2a6432f5fbbe9baec3d2f0adee77550239fe
r60_b0 = 0x042c9f35286f193cc451e866d7e7de7e012ad86aeca91a6d43f8ce729e53d4f8
r60_k0 = 0x20fafd298eadd21d96609474811287122973a6d1daa4cb4aefcbe1ddcb5a889a
r60_a1 = 0x01a93c4ce5be378b2dbbd151832e20f67bf1d8dcc81a1fec09a82e08fc5ec7ff
r60_b1 = 0x2adcf0784cd569800a20c95bf042f34463d6003098e05b97066efca0a5d052c0
r60_k1 = 0x1c3bae1f07ed8deb2836ac7d5feb563290169142f051ef14132efca9a833dc73
r60_a2 = 0x32b42f38dd73c1acf699665b7383ad373f5b2cc5cabee901175e1f73d2ee64ae
r60_b2 = 0x19d599ca4eedcdea68346410e1f4c2416aaca248d88f805eca94b3da48b606af
r60_k2 = 0x085960e598dfb4087e524f5cef252378310e8538a240a484a40be1c218d24b2c
r61_a0 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
r61_b0 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
r61_k0 = 0x0b6a559e45126fbf49467ef47d448a8f0875828367af6064482f171d25d4aace
r61_a1 = 0x057c2f49737c67ec746d4403d5adf0c807c741cf322cf343150d77a7d90864bf
r61_b1 = 0x0d4e7cc2d8113cc35027f4563b51c2c728b70b85ef34cea5fa2fad48f05ae387
r61_k1 = 0x087079ef692c193958dd0f32fba096c21d675aace5a02e72f302b14d7aba3ad7
r61_a2 = 0x11307fe5c772371bb9531de615997afdc2830b355d06c6657d06c01f0c76e7fa
r61_b2 = 0x283e17ae8f7dd3f06a31f3d99d6c2fe63341d0118a37f5cfc81c869b79bda6f7
r61_k2 = 0x2352d35496eff6bd47595716e57db9a31925ecc46f3ebfedd9f2d44ba4fca083
r62_a0 = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
r62_b0 = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
r62_k0 = 0x3bbb34394c2f5cdfc9009b18af3eedaa7d533cd44a1abdd6b619d211b1bfa9c8
r62_a1 = 0x057c2f49737c67ec746d4403d5adf0c807c741cf322cf343150d77a7d90864bf
r62_b1 = 0x0d4e7cc2d8113cc35027f4563b51c2c728b70b85ef34cea5fa2fad48f05ae387
r62_k1 = 0x2c1d8713cfcf53fdecb18f0ac14e1821441a4aab13ea8cb78544fda26fef216c
r62_a2 = 0x11307fe5c772371bb9531de615997afdc2830b355d06c6657d06c01f0c76e7fa
r62_b2 = 0x283e17ae8f7dd3f06a31f3d99d6c2fe63341d0118a37f5cfc81c869b79bda6f7
r62_k2 = 0x21cd9507fa7cc3ed3a49e765c74e5a0e08df37ce1429b6645e46c4b85ad52809
o_a = 0x0fbb8b592b77aa848174f415093060af73f839caad04d8c465b339a1118ec8d6
o_b = 0x2536ae3b5b386405f6e260e9f8a0277eba85b8731f11967d0497ce2eea709acf
```

### L.6 Listing of `L` at r = 21 (387 operations; `x` is input and output)

```
ADD y1, x, e1
ADD y2, x, e2
MUL t2, x, x
MUL t4, t2, t2
MUL z0, t4, x
MUL t2, y1, y1
MUL t4, t2, t2
MUL z1, t4, y1
MUL t2, y2, y2
MUL t4, t2, t2
MUL z2, t4, y2
MUL m1, r2_a0, z1
MUL m2, r2_b0, z2
ADD s, z0, m1
ADD s, s, m2
ADD x, s, r2_k0
MUL m1, r2_a1, z1
MUL m2, r2_b1, z2
ADD s, z0, m1
ADD s, s, m2
ADD y1, s, r2_k1
MUL m1, r2_a2, z1
MUL m2, r2_b2, z2
ADD s, z0, m1
ADD s, s, m2
ADD y2, s, r2_k2
MUL t2, x, x
MUL t4, t2, t2
MUL z0, t4, x
MUL t2, y1, y1
MUL t4, t2, t2
MUL z1, t4, y1
MUL t2, y2, y2
MUL t4, t2, t2
MUL z2, t4, y2
MUL m1, pf_a0, z1
MUL m2, pf_b0, z2
ADD s, z0, m1
ADD h0, s, m2
MUL m1, pf_a1, z1
MUL m2, pf_b1, z2
ADD s, z0, m1
ADD h1, s, m2
MUL m1, pf_a2, z1
MUL m2, pf_b2, z2
ADD s, z0, m1
ADD h2, s, m2
ADD u, h0, p0_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p0_n1, h1
MUL m2, p0_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p0_v1, x5
ADD h1, h1, m1
MUL m2, p0_v2, x5
ADD h2, h2, m2
ADD u, h0, p1_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p1_n1, h1
MUL m2, p1_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p1_v1, x5
ADD h1, h1, m1
MUL m2, p1_v2, x5
ADD h2, h2, m2
ADD u, h0, p2_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p2_n1, h1
MUL m2, p2_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p2_v1, x5
ADD h1, h1, m1
MUL m2, p2_v2, x5
ADD h2, h2, m2
ADD u, h0, p3_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p3_n1, h1
MUL m2, p3_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p3_v1, x5
ADD h1, h1, m1
MUL m2, p3_v2, x5
ADD h2, h2, m2
ADD u, h0, p4_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p4_n1, h1
MUL m2, p4_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p4_v1, x5
ADD h1, h1, m1
MUL m2, p4_v2, x5
ADD h2, h2, m2
ADD u, h0, p5_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p5_n1, h1
MUL m2, p5_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p5_v1, x5
ADD h1, h1, m1
MUL m2, p5_v2, x5
ADD h2, h2, m2
ADD u, h0, p6_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p6_n1, h1
MUL m2, p6_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p6_v1, x5
ADD h1, h1, m1
MUL m2, p6_v2, x5
ADD h2, h2, m2
ADD u, h0, p7_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p7_n1, h1
MUL m2, p7_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p7_v1, x5
ADD h1, h1, m1
MUL m2, p7_v2, x5
ADD h2, h2, m2
ADD u, h0, p8_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p8_n1, h1
MUL m2, p8_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p8_v1, x5
ADD h1, h1, m1
MUL m2, p8_v2, x5
ADD h2, h2, m2
ADD u, h0, p9_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p9_n1, h1
MUL m2, p9_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p9_v1, x5
ADD h1, h1, m1
MUL m2, p9_v2, x5
ADD h2, h2, m2
ADD u, h0, p10_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p10_n1, h1
MUL m2, p10_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p10_v1, x5
ADD h1, h1, m1
MUL m2, p10_v2, x5
ADD h2, h2, m2
ADD u, h0, p11_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p11_n1, h1
MUL m2, p11_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p11_v1, x5
ADD h1, h1, m1
MUL m2, p11_v2, x5
ADD h2, h2, m2
ADD u, h0, p12_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p12_n1, h1
MUL m2, p12_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p12_v1, x5
ADD h1, h1, m1
MUL m2, p12_v2, x5
ADD h2, h2, m2
ADD u, h0, p13_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p13_n1, h1
MUL m2, p13_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p13_v1, x5
ADD h1, h1, m1
MUL m2, p13_v2, x5
ADD h2, h2, m2
ADD u, h0, p14_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p14_n1, h1
MUL m2, p14_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p14_v1, x5
ADD h1, h1, m1
MUL m2, p14_v2, x5
ADD h2, h2, m2
ADD u, h0, p15_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p15_n1, h1
MUL m2, p15_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p15_v1, x5
ADD h1, h1, m1
MUL m2, p15_v2, x5
ADD h2, h2, m2
ADD u, h0, p16_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p16_n1, h1
MUL m2, p16_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p16_v1, x5
ADD h1, h1, m1
MUL m2, p16_v2, x5
ADD h2, h2, m2
ADD u, h0, p17_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p17_n1, h1
MUL m2, p17_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p17_v1, x5
ADD h1, h1, m1
MUL m2, p17_v2, x5
ADD h2, h2, m2
ADD u, h0, p18_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p18_n1, h1
MUL m2, p18_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p18_v1, x5
ADD h1, h1, m1
MUL m2, p18_v2, x5
ADD h2, h2, m2
ADD u, h0, p19_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p19_n1, h1
MUL m2, p19_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p19_v1, x5
ADD h1, h1, m1
MUL m2, p19_v2, x5
ADD h2, h2, m2
ADD u, h0, p20_k
MUL t2, u, u
MUL t4, t2, t2
MUL x5, t4, u
MUL m1, p20_n1, h1
MUL m2, p20_n2, h2
ADD s, x5, m1
ADD h0, s, m2
MUL m1, p20_v1, x5
ADD h1, h1, m1
MUL m2, p20_v2, x5
ADD h2, h2, m2
ADD x, h0, x_k0
ADD y1, h1, x_k1
ADD y2, h2, x_k2
MUL t2, x, x
MUL t4, t2, t2
MUL z0, t4, x
MUL t2, y1, y1
MUL t4, t2, t2
MUL z1, t4, y1
MUL t2, y2, y2
MUL t4, t2, t2
MUL z2, t4, y2
MUL m1, r60_a0, z1
MUL m2, r60_b0, z2
ADD s, z0, m1
ADD s, s, m2
ADD x, s, r60_k0
MUL m1, r60_a1, z1
MUL m2, r60_b1, z2
ADD s, z0, m1
ADD s, s, m2
ADD y1, s, r60_k1
MUL m1, r60_a2, z1
MUL m2, r60_b2, z2
ADD s, z0, m1
ADD s, s, m2
ADD y2, s, r60_k2
MUL t2, x, x
MUL t4, t2, t2
MUL z0, t4, x
MUL t2, y1, y1
MUL t4, t2, t2
MUL z1, t4, y1
MUL t2, y2, y2
MUL t4, t2, t2
MUL z2, t4, y2
MUL m1, r61_a0, z1
MUL m2, r61_b0, z2
ADD s, z0, m1
ADD s, s, m2
ADD x, s, r61_k0
MUL m1, r61_a1, z1
MUL m2, r61_b1, z2
ADD s, z0, m1
ADD s, s, m2
ADD y1, s, r61_k1
MUL m1, r61_a2, z1
MUL m2, r61_b2, z2
ADD s, z0, m1
ADD s, s, m2
ADD y2, s, r61_k2
MUL t2, x, x
MUL t4, t2, t2
MUL z0, t4, x
MUL t2, y1, y1
MUL t4, t2, t2
MUL z1, t4, y1
MUL t2, y2, y2
MUL t4, t2, t2
MUL z2, t4, y2
MUL m1, r62_a0, z1
MUL m2, r62_b0, z2
ADD s, z0, m1
ADD s, s, m2
ADD x, s, r62_k0
MUL m1, r62_a1, z1
MUL m2, r62_b1, z2
ADD s, z0, m1
ADD s, s, m2
ADD y1, s, r62_k1
MUL m1, r62_a2, z1
MUL m2, r62_b2, z2
ADD s, z0, m1
ADD s, s, m2
ADD y2, s, r62_k2
MUL t2, x, x
MUL t4, t2, t2
MUL z0, t4, x
MUL t2, y1, y1
MUL t4, t2, t2
MUL z1, t4, y1
MUL t2, y2, y2
MUL t4, t2, t2
MUL z2, t4, y2
MUL m1, o_a, z1
MUL m2, o_b, z2
ADD s, z0, m1
ADD x, s, m2
```
