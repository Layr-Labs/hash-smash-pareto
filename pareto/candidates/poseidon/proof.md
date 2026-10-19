# Proof: generic birthday (distinguished-point rho) collision, Orchard Poseidon r=23

Target `poseidon-orchard-r23-prefix-v1` (Pallas P128Pow5T3, ConstantLength<2>, halo2_poseidon 0.2.0 pinned constants; 8 fixed full rounds around 23 partial rounds; digest = state[0], whole element compared). Attack class `ordinary-collision`. Cost model `orchard-field-ram-v2`: every field addition/subtraction/multiplication and every 256-bit word primitive is charged 1/C target compressions with C = 216 + 21*23 = 699; exponentiation/inversion are charged as their counted constituent operations. No asymptotic-only claim is made; every bound below is a finite number at the actual dimensions.

## 1. The claim

* `time_log2` = 126.26274 `target-compressions` (exact Decimal 126.262737; rounded **up** at 5 decimals).
* `memory_log2_bytes` = 20 (reviewed total 1,048,518 bytes < 2^20; normalized memory penalty max(0, 20 - 20) = 0).
* `success_probability` = 0.39 at the filed walk budget (Section 5 for the random-function lemma, Section 6 for the measured hazard transfer).
* `preprocessing_log2` = 32; all offline derivation (constants, budget solve, the 16,380-walk measurement campaign) is bounded by 2^41 word operations and charged **inside** `time_log2` (Section 9, ledger line "offline derivation").
* `nonuniform_advice_log2_bytes` = 0 (no precomputed collision, no nonuniform advice; the master seed is drawn by the attack itself).

## 2. The walk map (two-round bypass line)

Round 0 maps (m0, m1) bijectively to (U, V) = ((m0 + C[0][0])^5, (m1 + C[0][1])^5). On the line (U, V) = (U0 + a*tau, V0 + b*tau) with a = MDS[0][1] and b = -MDS[0][0] mod p, the round-1 S-box inputs are (U0 + a*tau)^5, (V0 + b*tau)^5 and the capacity-lane constant, so with W = tau^5 the state after round 1 is A + W*B (two-round bypass; Bariant, Bouvier, Leurent, Perrin, ToSC 2022). The line constants, from the pinned deployed constants:

```
p   = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
a   = 0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e
b   = 0x354a1a478b5972184c2a60423736152b8a6ef850e5c7edc566ee0c66281ee49e
U0  = 0x2de17246e844b000296eefaaf2116b9705e3af63806d80541c7d6b4be442036c
V0  = 0x2622542e119aef1f7c021664aae329063a3e73651cd62e02756427f9437fdd96
A0  = 0x2a78890d8503b228bfa6bd9b312401c7af4e02a6376ceebb003ef1138f67c72c
D1  = 0x2b1cf2a34b2b6723837c31d51d5c91d12d1a715784a437124e3daf150a8d2b15
D2  = 0x194af15c17a9f125b198b4fcacb6f6a0d7525c1960573b90b20d8c6a16f61d57
d   = 1/5 mod (p-1) = 0x333333333333333333333333333333334e9ee0c9a10a60e2e0f0f3f0cccccccd
OUTSCALE = 0x13c5dbad6a2a02dbb84d5e5216e20252ebad4fea87739d30c0c9a6e39debfd5f
LAMBDA = inv(OUTSCALE) = 0x18b086c96248e65dbbd569d395c708068742b4759f253f51acb76393a5a14bff
```

U0, V0 solve the 2x2 linear system that fixes A's first two lanes through the capacity lane; A0 closes A's third lane; D1, D2 are B's first two lanes. message(W) inverts the line injectively: tau = W^d, U = U0 + a*tau, V = V0 + b*tau, m0 = U^d - C[0][0], m1 = V^d - C[0][1]; both are canonical field elements by construction. The attack fixes one random rho0 (low 254 bits of a PRG draw) and one random start x0 (a second PRG draw) and walks

F(x) = digest(message(x + rho0)) / OUTSCALE mod p,

where OUTSCALE = G0[0] mod p (G0 = MDS row 0 * diag(sig) at round 63) is the forced output normalization of the sparse equivalent form: the 3-mul S-box x5 = u^5 pins the lane-0 chain lam0 and the first-column pivot divisions of rounds 60..62 pin the output row's unit at lane 0 (Section 3). This is the incumbent ab786fc's own walk map, bit-identical: its Appendix D OUTINV_HEX[23] equals LAMBDA here (verified). Two distinct walk values x != y with F(x) = F(y) give distinct W_x != W_y (message is injective), hence distinct canonical messages with equal digests: an ordinary collision.

## 3. The step program (419.75 charged operations per step)

| block | ops | breakdown |
| --- | ---: | --- |
| entry (attempt registers) | 3 | y_i = x + e_i, with e_i = E0_i + rho0 set once per attempt (E0_i = (A_i + C[2][i]) / B_i, offline) |
| round 2 | 24 | three S-boxes y_i^5 (9 mult) + the linear layer with the round-3 constants folded in scaled coordinates (6 mult + 9 add) |
| round 3 (into the partial form) | 21 | three S-boxes (9 mult) + the linear layer into the partial-round form (6 mult + 6 add) |
| 23 partial rounds 4..26 | 276 | 12 each: 1 add (u = h0 + PU_k), 3 S-box mult (x5 = u^5), 2 mult + 2 add (h0 = x5 + NB0_k h1 + NB1_k h2), 1 mult + 1 add (h1 = h1 + W0_k x5), 1 mult + 1 add (h2 = h2 + W1_k x5); the linear layer of the round is absorbed offline into the next basis Q' = M'Q and the offsets gamma, q (M' the lower 2x2 block of MDS) |
| round-60 inputs from the partial form | 7 | 1 add (lane 0: y0 = h0 + E60) + 2 x (1 mult + 2 add) (lanes 1, 2 from the running basis Q, q) |
| rounds 60-62 | 72 | 24 each: 3 add + 9 S-box + the linear layer with the next round's constants in first-column-pivot scaled coordinates (6 mult + 6 add) |
| round 63 (output row) | 13 | 3 add + 9 S-box + the output row z_0 + CO_1 z_1 + CO_2 z_2 = digest / OUTSCALE (unit coefficient at lane 0): 2 mult + 2 add |
| dp test + loop control | 3.75 | dp mask 1, dp threshold compare 1, dp decision branch 1 + loop control 0.75 (counter increment, compare and branch per 4-step unrolled block); x and e_0..e_2 stay in registers (no per-step loads or stores) |
| **total per step** | **419.75** | **416 field (249 mult + 167 add) + 3.75 word** |

The partial rounds run in the SPARSE equivalent form (Grassi et al., "Poseidon: A New Hash Function for Zero-Knowledge Proof Systems", partial rounds; the running-basis form of the incumbent entry ab786fc, independently re-derived here): lane 0 is held as lam0*h0 + gamma and lanes 1, 2 as Q(h1, h2) + q, with lam0, gamma, the 2x2 basis Q and q constants of the program. A partial round is then u = h0 + (gamma + c0)/lam0 (1 add), x5 = u^5 (3 mult), h0 = x5 + (beta0/alpha) h1 + (beta1/alpha) h2 (2 mult + 2 add), h1 = h1 + w0 x5 (1 mult + 1 add), h2 = h2 + w1 x5 (1 mult + 1 add) - twelve charged field operations - with alpha = MDS[0][0]*lam0^5, beta_j = MDS[0][1]*Q[0][j] + MDS[0][2]*Q[1][j], w = Q'^-1 v, v = (MDS[1][0]*lam0^5, MDS[2][0]*lam0^5), Q' = M'Q, all offline; the linear layer of the round is absorbed into the NEXT basis Q' and the offsets, so no per-round matrix product is charged. The chain is forced, not chosen: the 3-mul powering x5 = u^5 pins the lane-0 output scale l5 = lam0^5 every round, so lam0 chains as alpha = MDS[0][0]*lam0^5, the exit scale into round 60 is fixed, and the first-column pivot normalizations of rounds 60..62 pin the output row's unit at lane 0 with OUTSCALE = G0[0] (Section 2). Rounds 2 and 3 fold the entry and the transition into the partial form; round 60 folds the partial-form exit. All 167 step constants (per-round PU_k, NB0_k, NB1_k, W0_k, W1_k; the round-2/3 scaled tables; the rounds 60..63 tables; E0) are derived offline from the pinned deployed constants and MDS, and asserted nonzero/invertible as they are derived.

Checks (all run locally, `python3 myrho.py` / `attack.py --selftest`): the step program equals digest(message(x + rho0)) / OUTSCALE on 64 of 64 random (x, rho0) trials against the trusted reference permutation; the reference rounds equal the organizer's `verifier/poseidon.py` permute at r = 23 on 24 of 24 random inputs; F(x) * OUTSCALE equals the organizer digest of the 64-byte message message(x + rho0) on 8 of 8 random (x, rho0); LAMBDA equals the incumbent entry's published OUTINV_HEX[23] (its Appendix D) exactly - the walk map is bit-identical to the incumbent's; and the per-step ledger totals exactly 419.75 (249 mult + 167 add + 3.75 word). Every field multiplication/addition and every word primitive in the actual code path is counted; no operation is uncharged.

## 4. The search: one trail, distinguished points, index table, recovery

A walk value is distinguished iff its low 128 bits are < 38176; the threshold is below 2^16, so the low 16 bits determine the low 128 bits among dp values and a stored key (high 126 bits, low 16 bits) is injective on dp values. Exactly D = (2^126 + 1) * 38176 of the p field elements are distinguished (p = 2^254 + c with c = p mod 2^128 >= 38176), theta = D/N in [10^-33.95009, 10^-33.95005] (conditioning bounds theta_lo = (D - 2^128)/N, theta_hi = D/(N - 2^128)).

The algorithm (Appendix B, `full_search`): draw the coins rho0 and x0 (two PRG draws); walk x_{i+1} = F(x_i) from x0 for at most S0 = n0 + d steps (82458658022075887745892673130667924 = detection window, Section 5; the trail budget is the tight n0). Each distinguished value is probed in the table (at most 137,081 word operations per dp event: a full scan of the packed 27,413-entry table at 5 word operations per probe + 16) and, if new, stored with its trail index: one 32-byte word holding the high 126 bits of the value and the index, plus a 16-bit side field holding the low 16 bits. A distinguished value can be reconstructed exactly from its word and side field (injectivity above). Distinguished values on the tail never repeat (a cycle value cannot equal a tail value); the first repeat of a stored dp value detects the cycle.

Recovery (deterministic, Appendix B): the repeat is x_b = x_a (a the stored index, b the current index, L = b - a). Let s be the index stored just before a (the start x0 at index 0 if none). Compute x_{s+L} from the nearest stored point at or before s + L (at most gmax evaluations, else abandon). If x_s = x_{s+L}, abandon (start on the cycle). Otherwise iterate both walkers from (x_s, x_{s+L}) in lockstep (at most gmax rounds); the first time their images agree, the two predecessor states (A, B) satisfy F(A) = F(B) with A on the tail and B on the cycle, hence A != B: an ordinary collision. The output is the two messages message(A + rho0), message(B + rho0) (three fifth roots each). Recovery uses at most gmax (positioning) + 2 gmax (lockstep) = 3 gmax evaluations when every gap between consecutive stored distinguished points is at most gmax, plus at most four linear scans over the order list and the packed table (two index lookups, two reconstructions), each at most 109,668 word operations (4 word operations per entry over at most 27,413 entries + 16), charged in the ledger; the gap event is a lemma term, and a capped walk abandons the pair.

Reduced-width end-to-end check of the same search (Appendix B `--selftest`): truncated map (w = 40 bits), dense dp test (threshold 512 on the low 20 bits), trail budget 2^22: three seeded trials: two find and verify truncated collisions (messages distinct, 40-bit digests equal) against the trusted reference, one abandons the pair at the test gap cap (the lemma's gap term; the filed gmax is far larger relative to the filed density); these are test parameters, not the filed literals.

## 5. Success lemma (uniform random function, exact)

F a uniformly random function on N = p points, x0 any fixed element (every statement conditional on the start). With the parameters of Section 4 (threshold T = 38176, D = (2^126 + 1) T, theta_lo <= theta <= theta_hi, detection window d = ceil(9.25/theta_lo) rounded up to a multiple of 4, gap cap gmax = ceil(19.75/theta_lo) + 2, table cap MCAP = 27413, trail budget n, total budget S = n + d), the attempt fails with probability at most

1. no repeat within the trail budget: exp(-n(n+1)/(2N)) — a fresh value repeats one of the i + 1 earlier values with probability (i + 1)/N, and the chain rule over i < n gives the product bound;
2. start on the cycle: n/N;
3. no dp in the first d cycle values given the repeat (t <= n, mu, lambda >= d): (1 - theta_lo)^d <= e^-9.25 (a fresh value is distinguished with conditional probability at least theta_lo whatever the history);
4. cycle shorter than d: n*d/N;
5. a dp-to-dp gap (or start-to-first-dp gap) above gmax: (S*theta_hi + 1) e^-19.75 — positioning and lockstep walks are capped at gmax and the pair abandoned;
6. dp-table overflow: e^-12 (Chernoff on the number of stored dps, mean S*theta_hi = 20037 << MCAP + 1);
7. degenerate recovery pair: 4/N.

Solving 1 - fail(n) >= 0.39 in 80-digit Decimal gives the tight random-function trail budget n0 = 169346087099996799090729207472420809487 (success at n0 exactly 0.390000000...). **The filed trail budget IS this tight n0** (plus the detection window d on top); it is not scaled by any hazard margin.

## 6. Premise H1 and the filed budget

H1 (`H1-random-walk-rate`), the only premise of the claim.
* Statement: the filed trail has n0 = 169346087099996799090729207472420809487 steps, the tight random-function budget of Section 5 (the lemma at c = 1 gives success 0.390000000 exactly). Premise: for the attempt's coins (rho0 and x0, uniform 254-bit words), the search of Section 4 on the real map F(x) = digest(message(x + rho0)) / OUTSCALE, at the trail budget n0, succeeds with probability at least 0.39. **H1 is our theory that, for this search, the fixed map with a random rho0 behaves like a uniformly random function; this is an assumption and no proof is known.**
* Role: score-critical. It is the only step from the lemma to the claimed success probability; the step program (Section 3), the search and recovery (Section 4), the ledger (Section 7) and the memory (Section 8) are proved or checked exactly.
* Scope: target poseidon-orchard-r23-prefix-v1, inputs on the line of Section 2, one search with the parameters of Section 4 (walk budget S0 = 169428545758018874978475100145551477411 evaluations: the tight trail n0 plus the detection window). Not claimed for other round counts or budgets.

Budget and tolerance. Within the hazard-multiplier family (the real map's per-step repeat hazard is a constant multiple c of the random-function hazard), the repeat term of the lemma scales as exp(-c x) with x = n(n+1)/(2p); the other failure terms are unchanged. **This entry files the tight convention: the trail budget is n0, at which the random function (c = 1) reaches 0.390000000 exactly, and the real-map transfer is the bare premise H1 with NO tolerance margin.** This is the filing convention of the accepted r=22 and r=24+ incumbents (tight n0, 0.39). The measured multiplier supports it (pooled 1.0044, 95% CI [0.9891, 1.0198], no slope across widths) but does not dominate it: at the pooled lower endpoint 0.9891 the success at n0 is 0.3867, just under the 0.39 minimum, so the claim is evidence-consistent, not evidence-forced. The refuted companion filing 370aba08 paid 0.0758 bits for the dominated floor budget n1 (c >= 0.90); this entry pays none.

Evidence (participant-run; the organizer-run experiment is Section 10): first-repeat walks on the real r=23 map of the companion construction (the same line and rounds with the output rescaled by the fixed nonzero constant LAMBDA_lean * OUTSCALE; a fixed output rescaling of the map family, disclosed) truncated to w bits (the truncated map is the birthday model at width w), fresh (rho, start) per walk, every walk run to its exact first repeat, 16380 walks over six widths, exact discrete first-repeat likelihood P(L=l|m) = (m*l/N) * prod_(j<l) (1 - m*j/N) (series-summed with bounded tail), profile-likelihood 95% intervals:

| width w | walks | hazard multiplier m-hat | 95% profile-likelihood CI | series tail bound |
| ---: | ---: | ---: | --- | ---: |
| 16 | 1320 | 1.0145 | [0.9609, 1.0701] | 2.9e-06 |
| 20 | 6120 | 0.9936 | [0.9689, 1.0187] | 5.0e-08 |
| 24 | 6120 | 1.0143 | [0.9891, 1.0399] | 0.0e+00 |
| 28 | 1320 | 1.0190 | [0.9650, 1.0750] | 0.0e+00 |
| 32 | 1200 | 0.9800 | [0.9256, 1.0365] | 0.0e+00 |
| 36 | 300 | 1.0190 | [0.9080, 1.1387] | 0.0e+00 |

Pooled multiplier 1.0044, 95% profile-likelihood CI [0.9891, 1.0198]; the per-width estimates are consistent with a constant multiplier across widths (no slope). Seeds and stopping rule: each walk draws rho0 uniform on 254 bits and a start uniform on 2^w from an independent seeded stream (Appendix C, `measure2.py` per-chunk seeds); every walk ran to its first repeat, none was dropped, repeated or selected; there is no stopping rule. The exact discrete law is used throughout; no exponential or Gamma approximation of the first-repeat index enters the estimates.

Sensitivity at the filed budget n0 (repeat term x = 0.49534; other eps terms 6.3e-04):

| hazard factor c | 1.0198 (pooled upper) | 1 (random) | 0.9891 (pooled lower) | 0.9256 (w=32 lower) | 0.9080 (w=36 lower) | 0.90 (floor) | 0.85 (below floor) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| success at n0 | 0.3959 | 0.3900 | 0.3867 | 0.3671 | 0.3616 | 0.3591 | 0.3430 |

Same-map cross-evidence: the incumbent entry ab786fc (a dependency) publishes participant measurements of exactly this map family - the state after round 1 on the same line, the reference rounds 2-63 at r partial rounds, the output divided by OUTSCALE_r (its Appendix D lmeas, `kat` check) - at r = 7, 23 and 56, trails up to 2,970,429 steps, 14,879 pairs, on the bit-identical r = 23 map (its OUTINV_HEX[23] equals this entry's LAMBDA). Those measurements and the campaign above are the evidence for H1; neither bounds the full-width multiplier. The measurements show that the random-function first-repeat law holds on the real round function at every measured width, and every measured lower bound lies above the tolerance floor; they do not bound the multiplier at full width. The full-width first repeat cannot be observed at feasible cost, so the transfer is the premise itself.

Limitations: the measurements are reduced-width only (16 to 36 bits, first-repeat indexes of order 2^19 steps); they say nothing about the 254-bit map beyond the premise. The interval is a profile-likelihood interval, asymptotic in the number of walks and conditional on the hazard-multiplier family; it is evidence about the multiplier, not a bound on it. The organizer experiment (Section 10) is one width (14 bits), one round count, a witness-only event on the digest, and cannot validate H1, the cost or the success probability. On a single fixed map the success over starts varies with that map's cycle structure; the attempt therefore draws rho0 as a coin, and H1 concerns the average over rho0.

## 7. Ledger at the filed budget

```
walk budget S0 = n0 + d  = 169428545758018874978475100145551477411   (tight trail 169346087099996799090729207472420809487 + detection window 82458658022075887745892673130667924)
dp threshold                = 38176 (low 128 bits); D = (2^126 + 1) * 38176
theta_lo = (D - 2^128)/p   = 10^-33.95009
theta_hi = D/(p - 2^128)   = 10^-33.95005
d (detection window)       = 82458658022075887745892673130667924   = ceil(9.25/theta_lo) rounded up to 4
gmax (gap cap)             = 176060377939026895457446518306020702   = ceil(19.75/theta_lo) + 2
MCAP                       = 27413 entries
per-step ops               = 419.75  (416 field + 3.75 word; listing in Section 3)
walk ops    S0 * 419.75    = 71117632081928422772214923286095232643267.25
recovery    3*(gmax+16) evaluations at 419.75 + 6 each + 4 scans (109,668 word ops each) = 224873117722622102223023565506365400737.50
dp-table    27,414 events * 137,081 word ops (full scan, 5 word ops per probe + 16) = 3757938534
PRG          2 coin draws * 264 word ops = 528
setup + fifth roots        = 2000 + 2286
offline derivation         = 2^41 word ops (Section 9; constants + budget solve + measurement campaign; charged, 3145956016 compressions)
total ops                  = 71342505199651044874437946853804379242904.75
units = total / C, C = 699 = 102063669813520808117936976901007695626.47317596566523605150214592274678111587983
time_log2 = log2(units)     = 126.262737
filed                       = 126.26274 (rounded up at 5 decimals)
```

For reference against the frontier: the incumbent ab786fc files 126.74586 at 1.3993*n0 with success 0.62 under its own convention. This entry files the tight n0/0.39 convention - the same convention as the accepted r=22 incumbent abdf0ee (126.2478) and the r=24+ incumbents - with the incumbent's own sparse equivalent-form step program (independently re-derived here, 416 field ops as in its validated listing, on the bit-identical walk map), and its 126.26274 beats the r=23 incumbent by 0.4831 bits: the incumbent pays 0.4847 bits of probability margin (its 0.62 at 1.3993*n0) where this entry pays none.
## 8. Memory

Peak live set: 27,413 dp entries * 32 bytes (877,216) + 27,413 side fields * 2 bytes (54,826) + one 32-byte start word + 103,644 code + 5,600 constants + 7,200 registers = 1,048,518 bytes < 2^20 = 1,048,576. Every table item is one aligned 32-byte word: entry k at TAB0 + 32k holds (high 126 bits of the dp value) OR (its index < 2^128); the side word holds the 16-bit low part. Lookups extract the high part and compare, then the side field; reconstruction shifts the high part back and appends the side field (threshold < 2^16 makes this exact). Memory penalty max(0, log2(1,048,518) - 20) = 0; filed memory_log2_bytes = 20.

## 9. Preprocessing (inside time)

All constants (the line constants of Section 2; the per-round partial bases V(4)..V(27) with their folded unit coefficients; the kappa-folded per-round offsets kappahat0_i; the round-3 scaled bases; the folded exit constants at round 60; C60..C63, B60..B62, B63R; LAMBDA) and the budget solve (80-digit Decimal bisections on n0 and n1) are offline. Their derivation, together with the participant's 16,380-walk H1 measurement campaign (the evidence of Section 6: 263675434 measured walk steps, each at most 6 harness word operations plus one 419.75-op step evaluation, at most 112259816025 <= 2^37 word operations), is construction/preprocessing under orchard-field-ram-v2 and is bounded by 2^41 word operations (constant derivation: 64 rounds of short reciprocal/fifth-power chains, a few hundred word operations each; budget solve: a few hundred 80-digit Decimal exp/log evaluations, each < 2^10 word operations; campaign as stated), charged inside time_log2 in the ledger line "offline derivation" (2^41/699 = 3145956016 compressions), and declared as preprocessing_log2 = 32 (= ceil(log2(3145956016))). The measurement analysis of Section 6 is evidence generation for H1, not attack preprocessing beyond the campaign charged above; it is disclosed as such. The search program itself uses only integer literals (WALK, DETECT, GMAXC, DVAL, DPMASK, MCAP); nothing is derived online.

## 10. Organizer experiment (declared)

`lowbits-birthday` (python-message-pairs-v1, digest-xor-mask on the first 14 bits): per trial, at most 1200 fresh canonical 64-byte messages derived deterministically from the supplied seed; the program returns a pair whose r=23 digests agree on the masked bits. Local run of the same event: 256/256 verified pairs in 5.0 s single-CPU (mean ~144 draws per trial), byte-identical on repeat. It is a reduced-width witness on the digest only; it does not establish H1, the cost bound, or the success probability (a 14-bit event cannot separate hazard multipliers near 0.5 from 1).

## 11. Verification

The step program, the search with its recovery, the budget solve, the measurement harness and the analysis sources are embedded verbatim as appendices below (A: `myrho.py` - step program, line and tables, selftest; B: `attack.py` - the filed single-trail search, recovery, exact plan, reduced-width end-to-end selftest, H1 measurement mode; C: `measure2.py` + `analysis.py` - H1 evidence and exact likelihood intervals). All are standard-library-only Python 3, deterministic given their seeds. Exercised locally: `myrho.py --selftest` 64/64 against the trusted reference; `attack.py --selftest` 64/64 plus two-of-three reduced-width searches (one pair abandoned at the test gap cap); `attack.py --plan` prints the exact ledger of Section 7; Appendices C produced the Section 6 table (with `attack.py --measure` seeding widths 16..28).
## Appendix A: `myrho.py` (line, tables, SPARSE step program at 419.75 ops, selftest)

Line construction, the sparse partial-round running bases Q with absorbed linear layers, the register-held constants and the counted `step()` at exactly 419.75 charged operations (416 field: 249 mult + 167 add; 3.75 word); `--selftest` runs the 64-trial check against `ref_permute` (the organizer's verifier semantics) plus the per-step ledger reconciliation.

```python
#!/usr/bin/env python3
"""r=23 Orchard Poseidon generic birthday attack, SPARSE step program.

Distinguished-point single-trail rho on the line of message(W); the walk
step is F(x) = digest(message(x + rho0)) / OUTSCALE, the map convention of
the incumbent entry ab786fc: the sparse chain's forced normalizations (the
3-mul S-box x5 = u^5 pins l5 = lam0^5; the first-column pivot divisions of
rounds 60..62) pin OUTSCALE = G0[0] (G0 = MDS row 0 * diag(sig) at round
63), and the output row carries its unit at lane 0.  LAMBDA = 1/OUTSCALE
below.  This variant runs the partial rounds in the SPARSE equivalent form
(Grassi et al., "Poseidon: A New Hash Function for Zero-Knowledge Proof
Systems", partial rounds; the running-basis form of the r=23 incumbent
entry ab786fc):
lane 0 is held as lam0*h0 + gamma and lanes 1, 2 as Q(h1, h2) + q, with
lam0, gamma, the 2x2 basis Q and q constants of the program; the linear
layer of every partial round is absorbed into the NEXT Q = M' Q (M' the
lower 2x2 block of the MDS matrix) and into gamma, all offline.  A partial
round is then

    u  = h0 + (gamma + c0)/lam0            1 add
    x5 = u^5                               3 mult
    h0 = x5 + (beta0/alpha) h1 + (beta1/alpha) h2   2 mult + 2 add
    h1 = h1 + w0 x5                         1 mult + 1 add
    h2 = h2 + w1 x5                         1 mult + 1 add

with alpha = M00*lam0^5, beta_j = M01*Q[0][j] + M02*Q[1][j], w = Q'^-1 v,
v = (M10*lam0^5, M20*lam0^5), Q' = M' Q - twelve charged field operations
(7 mult + 5 add), with the five per-round constants derived offline.

* entry: e_i = E0_i + rho0 (E0_i = (A_i + c2_i)/B_i, one add per attempt);
  per step y_i = x + e_i: 3 add; round 2: three S-boxes 9 mult, linear
  layer with the round-3 constants folded in scaled coordinates 6 mult +
  9 add;
* round 3: three S-boxes 9 mult, linear layer into the partial-round form
  6 mult + 6 add (the partial phase opens in the round-3 output basis with
  Q = diag(G10, G20), q = 0, gamma = 0);
* 23 partial rounds 4..26: 12 field operations each;
* round-60 S-box inputs from the partial form: 1 add (lane 0) + per lane
  1, 2: 1 mult + 2 add;
* rounds 60..62: 24 each (three S-boxes 9 mult, scaled linear layer with
  the next round's constants 6 mult + 9 add);
* round 63: three S-boxes 9 mult, output row = digest / OUTSCALE with the
  unit coefficient at lane 0 (the forced first-column pivot normalization
  of rounds 60..62): 2 mult + 2 add;
* dp test + loop control: 3.75 word operations per step (dp test: AND
  with the low-128-bit mask, compare with the threshold, conditional
  branch = 3; loop control in a 4-step unrolled block: counter increment,
  compare, branch = 3 per 4 steps).  x and e_0..e_2 stay in registers (no
  per-step loads or stores).

STEP_OPS = 3 + 24 + 21 + 23*12 + 7 + 3*24 + 9 + 4 + 3.75 = 419.75
(field: 249 mult + 167 add = 416; word: 3.75) - the same equivalent-form
step count as the incumbent's validated listing (ab786fc: 416 = 140 +
12*23 field operations).  All constants are derived
once at import (offline derivation; the setup loads are charged in the
ledger setup line) and held in registers; no per-step table loads.  Cost
model orchard-field-ram-v2, C = 216 + 21*23 = 699.

The sparse chain is asserted as it is derived: every B_i, every pivot
G_i0, alpha and det(Q') nonzero; --selftest verifies the whole program
against the trusted reference permutation on 64 random (x, rho0).
"""
import json
import random
from pathlib import Path

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
CAP = 1 << 65
R = 23
CONSTS = Path(__file__).resolve().parent / 'orchard-pallas-constants.json'

_d = json.loads(CONSTS.read_text())
C = [tuple(int(x, 16) for x in row) for row in _d['round_constants']]
MDS = tuple(tuple(int(x, 16) for x in row) for row in _d['mds'])


def inv(x):
    return pow(x, -1, P)


def ref_permute(state, rounds=R):
    s = list(state)
    for i in (*range(4), *range(4, 4 + rounds), *range(60, 64)):
        s = [(x + c) % P for x, c in zip(s, C[i])]
        for col in (range(3) if (i < 4 or i >= 60) else range(1)):
            s[col] = pow(s[col], 5, P)
        s = [sum(m * x for m, x in zip(row, s)) % P for row in MDS]
    return tuple(s)


def ref_digest(m0, m1, rounds=R):
    return ref_permute((m0 % P, m1 % P, CAP), rounds)[0]


# ---------------- line construction (two-round bypass) ----------------
CAPp = pow(CAP + C[0][2], 5, P)
A1c = (-((MDS[1][2] * CAPp + C[1][1]) % P)) % P
A2c = (-((MDS[2][2] * CAPp + C[1][2]) % P)) % P
_det = (MDS[1][0] * MDS[2][1] - MDS[1][1] * MDS[2][0]) % P
U0 = ((A1c * MDS[2][1] - A2c * MDS[1][1]) * inv(_det)) % P
V0L = ((MDS[1][0] * A2c - MDS[2][0] * A1c) * inv(_det)) % P
a_, b_ = MDS[0][1] % P, (-MDS[0][0]) % P
D1 = (MDS[1][0] * a_ + MDS[1][1] * b_) % P
D2 = (MDS[2][0] * a_ + MDS[2][1] * b_) % P
A0 = (MDS[0][0] * U0 + MDS[0][1] * V0L + MDS[0][2] * CAPp + C[1][0]) % P
QQ = tuple((MDS[j][1] * pow(D1, 5, P) + MDS[j][2] * pow(D2, 5, P)) % P for j in range(3))
PP = tuple((MDS[j][0] * pow(A0, 5, P)) % P for j in range(3))
D_EXP = pow(5, -1, P - 1)
# LAMBDA (the walk scale) is derived below: LAMBDA = inv(OUTSCALE) with
# OUTSCALE = G0[0] the forced output normalization of the sparse chain.


def message(W):
    tau = pow(W, D_EXP, P)
    U = (U0 + a_ * tau) % P
    V = (V0L + b_ * tau) % P
    m0 = (pow(U, D_EXP, P) - C[0][0]) % P
    m1 = (pow(V, D_EXP, P) - C[0][1]) % P
    return m0, m1


# ---------------- offline derivation (setup; no per-step loads) --------
# state after round 1: A + W B with A = PP, B = QQ (asserted in the line
# construction).  Round-2 S-box input lane i = A_i + c2_i + (x + rho0) B_i
# = B_i (x + e_i) with e_i = E0_i + rho0, E0_i = (A_i + c2_i) / B_i.
A, B = PP, QQ
assert all(B[i] != 0 for i in range(3))
E0 = [(A[i] + C[2][i]) * inv(B[i]) % P for i in range(3)]

# round 2: held y_i = x + e_i (true input B_i y_i); z_i = y_i^5; the
# linear layer with the round-3 constants, each output lane divided by
# its pivot G_i0 (G = MDS * diag(B^5)): s_i = z_0 + K2_i1 z_1 + K2_i2 z_2
# + KC3_i, lam_i = G_i0 the scale of s_i.
sig = [pow(B[i], 5, P) for i in range(3)]
G2 = [[MDS[i][j] * sig[j] % P for j in range(3)] for i in range(3)]
assert all(G2[i][0] != 0 for i in range(3))
K2 = [[G2[i][j] * inv(G2[i][0]) % P for j in (1, 2)] for i in range(3)]
KC3 = [C[3][i] * inv(G2[i][0]) % P for i in range(3)]
lam = [G2[i][0] for i in range(3)]

# round 3: held s_i (true input lam_i s_i); z_i = s_i^5; into the partial
# form: h_i = z_0 + G3_i1 z_1 + G3_i2 z_2 with G3 = MDS * diag(lam^5);
# true lane 0 = lam0 h0 + gamma (lam0 = G3_00, gamma = 0), true lanes
# (1, 2) = Q (h1, h2) + q with Q = diag(G3_10, G3_20), q = 0.
sig = [pow(l, 5, P) for l in lam]
G3 = [[MDS[i][j] * sig[j] % P for j in range(3)] for i in range(3)]
assert all(G3[i][0] != 0 for i in range(3))
H3 = [[G3[i][j] * inv(G3[i][0]) % P for j in (1, 2)] for i in range(3)]
lam0, gamma = G3[0][0], 0
Qp = [[G3[1][0], 0], [0, G3[2][0]]]
qp = [0, 0]

# the 23 sparse partial rounds: per round the five constants PU (the
# S-box input offset (gamma + c0)/lam0), NB0, NB1 (the lane-0 update
# coefficients beta/alpha) and W0, W1 (the lane-1,2 update coefficients
# w = Q'^-1 v); the basis update Q' = M' Q and q' = M' q, gamma' and the
# scales are all offline.
# the partial chain is FORCED: the S-box x5 = u^5 pins the lane-0 output
# scale l5 = lam0^5 every round (a 3-mul powering admits no free basis),
# so lam0 chains as alpha = MDS[0][0] * lam0^5 and the exit scale into
# round 60 is fixed (the incumbent's own builder: l5 = pow(lam0, 5, P)).
PU = [None] * R
NB = [None] * R
Wc = [None] * R
for k in range(R):
    c = C[4 + k]
    PU[k] = (gamma + c[0]) * inv(lam0) % P
    l5 = pow(lam0, 5, P)
    qp = [(qp[0] + c[1]) % P, (qp[1] + c[2]) % P]
    alpha = MDS[0][0] * l5 % P
    beta = [(MDS[0][1] * Qp[0][j] + MDS[0][2] * Qp[1][j]) % P for j in range(2)]
    gamma = (MDS[0][1] * qp[0] + MDS[0][2] * qp[1]) % P
    Qn = [[(MDS[1 + i][1] * Qp[0][j] + MDS[1 + i][2] * Qp[1][j]) % P
           for j in range(2)] for i in range(2)]
    qp = [(MDS[1 + i][1] * qp[0] + MDS[1 + i][2] * qp[1]) % P for i in range(2)]
    dt = (Qn[0][0] * Qn[1][1] - Qn[0][1] * Qn[1][0]) % P
    assert alpha != 0 and dt != 0, (4 + k, alpha, dt)
    di = inv(dt)
    v = [MDS[1][0] * l5 % P, MDS[2][0] * l5 % P]
    Wc[k] = [(Qn[1][1] * v[0] - Qn[0][1] * v[1]) * di % P,
              (-Qn[1][0] * v[0] + Qn[0][0] * v[1]) * di % P]
    ai = inv(alpha)
    NB[k] = [beta[0] * ai % P, beta[1] * ai % P]
    lam0, Qp = alpha, Qn

# round-60 S-box inputs from the partial form: lane 0 y0 = h0 + (gamma +
# c60_0)/lam0; lanes 1, 2: y_{1+i} = h1 + (Q_i1/Q_i0) h2 + (q_i +
# c60_{1+i})/Q_i0, each divided by its scale Q_i0.
c60 = C[60]
E60 = (gamma + c60[0]) * inv(lam0) % P
Q60 = [None] * 2
EC60 = [None] * 2
for i in range(2):
    assert Qp[i][0] != 0
    gi = inv(Qp[i][0])
    Q60[i] = Qp[i][1] * gi % P
    EC60[i] = (qp[i] + c60[1 + i]) * gi % P
sig = [pow(lam0, 5, P)] + [pow(Qp[i][0], 5, P) for i in range(2)]

# rounds 60..62: per round three S-boxes (9 mult) and the scaled linear
# layer with the NEXT round's constants (per lane 2 mult + 3 add).
K6 = [None] * 3
KC6 = [None] * 3
for rnd in (60, 61, 62):
    Gr = [[MDS[i][j] * sig[j] % P for j in range(3)] for i in range(3)]
    assert all(Gr[i][0] != 0 for i in range(3))
    K6[rnd - 60] = [[Gr[i][j] * inv(Gr[i][0]) % P for j in (1, 2)] for i in range(3)]
    KC6[rnd - 60] = [C[rnd + 1][i] * inv(Gr[i][0]) % P for i in range(3)]
    lam = [Gr[i][0] for i in range(3)]
    sig = [pow(l, 5, P) for l in lam]

# round 63: three S-boxes, then the output row digest = G0 . z (G0 =
# MDS row 0 * diag(sig)) with OUTSCALE = G0[0]: out = digest / OUTSCALE =
# z_0 + CO_1 z_1 + CO_2 z_2, the unit coefficient at lane 0.
G0 = [MDS[0][j] * sig[j] % P for j in range(3)]
OUTSCALE = G0[0]
assert OUTSCALE != 0
LAMBDA = inv(OUTSCALE)             # the walk map: F = digest / OUTSCALE
CO = [LAMBDA * G0[j] % P for j in range(3)]
assert CO[0] == 1 % P, CO[0]       # the forced normalization placed it
NCONST = (3 + 9 + 6 + 5 * R + 5 + 27 + 2
          + 0)  # E0 3; K2 6 + KC3 3; H3 6; PU/NB/W 5R; E60/Q60/EC60 5; K6/KC6 27; CO 2

# register-held constants (one-time setup loads, charged in the ledger
# setup line; the step body below never indexes a table)
E0_0, E0_1, E0_2 = E0
(K2_0_1, K2_0_2), (K2_1_1, K2_1_2), (K2_2_1, K2_2_2) = K2
KC3_0, KC3_1, KC3_2 = KC3
(H3_0_1, H3_0_2), (H3_1_1, H3_1_2), (H3_2_1, H3_2_2) = H3
PU_4, PU_5, PU_6, PU_7, PU_8, PU_9, PU_10, PU_11, PU_12, PU_13, PU_14, \
    PU_15, PU_16, PU_17, PU_18, PU_19, PU_20, PU_21, PU_22, PU_23, PU_24, \
    PU_25, PU_26 = PU
(NB0_4, NB1_4), (NB0_5, NB1_5), (NB0_6, NB1_6), (NB0_7, NB1_7), \
    (NB0_8, NB1_8), (NB0_9, NB1_9), (NB0_10, NB1_10), (NB0_11, NB1_11), \
    (NB0_12, NB1_12), (NB0_13, NB1_13), (NB0_14, NB1_14), (NB0_15, NB1_15), \
    (NB0_16, NB1_16), (NB0_17, NB1_17), (NB0_18, NB1_18), (NB0_19, NB1_19), \
    (NB0_20, NB1_20), (NB0_21, NB1_21), (NB0_22, NB1_22), (NB0_23, NB1_23), \
    (NB0_24, NB1_24), (NB0_25, NB1_25), (NB0_26, NB1_26) = NB
(W0_4, W1_4), (W0_5, W1_5), (W0_6, W1_6), (W0_7, W1_7), (W0_8, W1_8), \
    (W0_9, W1_9), (W0_10, W1_10), (W0_11, W1_11), (W0_12, W1_12), \
    (W0_13, W1_13), (W0_14, W1_14), (W0_15, W1_15), (W0_16, W1_16), \
    (W0_17, W1_17), (W0_18, W1_18), (W0_19, W1_19), (W0_20, W1_20), \
    (W0_21, W1_21), (W0_22, W1_22), (W0_23, W1_23), (W0_24, W1_24), \
    (W0_25, W1_25), (W0_26, W1_26) = Wc
E60_0 = E60
Q60_1, EC60_1 = Q60[0], EC60[0]
Q60_2, EC60_2 = Q60[1], EC60[1]
(K60_0_1, K60_0_2), (K60_1_1, K60_1_2), (K60_2_1, K60_2_2) = K6[0]
C61_0, C61_1, C61_2 = KC6[0]
(K61_0_1, K61_0_2), (K61_1_1, K61_1_2), (K61_2_1, K61_2_2) = K6[1]
C62_0, C62_1, C62_2 = KC6[1]
(K62_0_1, K62_0_2), (K62_1_1, K62_1_2), (K62_2_1, K62_2_2) = K6[2]
C63_0, C63_1, C63_2 = KC6[2]
CO_0, CO_1, CO_2 = CO


def walk_e(rho0):
    """The attempt registers e_i = E0_i + rho0 (3 adds per attempt)."""
    return tuple((E0[i] + rho0) % P for i in range(3))


OPS = {'entry': 3, 'r2sbox': 9, 'r2lin': 15, 'r3sbox': 9, 'r3lin': 12,
       'partial': 12, 'r60in': 7, 'full': 24, 'r63sbox': 9,
       'out': 4, 'dp': 3.75}
FIELD_OPS = (OPS['entry'] + OPS['r2sbox'] + OPS['r2lin'] + OPS['r3sbox']
             + OPS['r3lin'] + R * OPS['partial'] + OPS['r60in']
             + 3 * OPS['full'] + OPS['r63sbox'] + OPS['out'])
STEP_OPS = FIELD_OPS + OPS['dp']


class Ledger:
    def __init__(self):
        self.mult = 0
        self.add = 0
        self.word = 0.0

    def reset(self):
        self.mult = self.add = 0
        self.word = 0.0


def _sbox(x, led):
    y = x * x % P; led.mult += 1
    y = y * y % P; led.mult += 1
    y = y * x % P; led.mult += 1
    return y


def step(x, e, led):
    """One counted walk step: x -> digest(message(x + rho0)) / OUTSCALE (= digest * LAMBDA)."""
    e0, e1, e2 = e
    # entry: y_i = x + e_i (true round-2 S-box input B_i y_i)   [3 add]
    y0 = (x + e0) % P
    y1 = (x + e1) % P
    y2 = (x + e2) % P
    led.add += 3
    # round 2: three S-boxes [9 mult]
    z0 = _sbox(y0, led)
    z1 = _sbox(y1, led)
    z2 = _sbox(y2, led)
    # round-2 linear layer + round-3 constants, scaled [6 mult + 9 add]
    t1 = K2_0_1 * z1 % P
    t2 = K2_0_2 * z2 % P
    s0 = (z0 + t1 + t2 + KC3_0) % P
    t1 = K2_1_1 * z1 % P
    t2 = K2_1_2 * z2 % P
    s1 = (z0 + t1 + t2 + KC3_1) % P
    t1 = K2_2_1 * z1 % P
    t2 = K2_2_2 * z2 % P
    s2 = (z0 + t1 + t2 + KC3_2) % P
    led.mult += 6; led.add += 9
    # round 3: three S-boxes [9 mult]
    z0 = _sbox(s0, led)
    z1 = _sbox(s1, led)
    z2 = _sbox(s2, led)
    # round-3 linear layer into the partial form [6 mult + 6 add]
    t1 = H3_0_1 * z1 % P
    t2 = H3_0_2 * z2 % P
    h0 = (z0 + t1 + t2) % P
    t1 = H3_1_1 * z1 % P
    t2 = H3_1_2 * z2 % P
    h1 = (z0 + t1 + t2) % P
    t1 = H3_2_1 * z1 % P
    t2 = H3_2_2 * z2 % P
    h2 = (z0 + t1 + t2) % P
    led.mult += 6; led.add += 6
    # 23 sparse partial rounds 4..26 [12 each: 7 mult + 5 add]
    x5 = _sbox((h0 + PU_4) % P, led); led.add += 1
    t1 = NB0_4 * h1 % P
    t2 = NB1_4 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_4 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_4 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_5) % P, led); led.add += 1
    t1 = NB0_5 * h1 % P
    t2 = NB1_5 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_5 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_5 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_6) % P, led); led.add += 1
    t1 = NB0_6 * h1 % P
    t2 = NB1_6 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_6 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_6 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_7) % P, led); led.add += 1
    t1 = NB0_7 * h1 % P
    t2 = NB1_7 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_7 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_7 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_8) % P, led); led.add += 1
    t1 = NB0_8 * h1 % P
    t2 = NB1_8 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_8 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_8 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_9) % P, led); led.add += 1
    t1 = NB0_9 * h1 % P
    t2 = NB1_9 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_9 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_9 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_10) % P, led); led.add += 1
    t1 = NB0_10 * h1 % P
    t2 = NB1_10 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_10 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_10 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_11) % P, led); led.add += 1
    t1 = NB0_11 * h1 % P
    t2 = NB1_11 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_11 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_11 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_12) % P, led); led.add += 1
    t1 = NB0_12 * h1 % P
    t2 = NB1_12 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_12 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_12 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_13) % P, led); led.add += 1
    t1 = NB0_13 * h1 % P
    t2 = NB1_13 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_13 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_13 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_14) % P, led); led.add += 1
    t1 = NB0_14 * h1 % P
    t2 = NB1_14 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_14 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_14 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_15) % P, led); led.add += 1
    t1 = NB0_15 * h1 % P
    t2 = NB1_15 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_15 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_15 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_16) % P, led); led.add += 1
    t1 = NB0_16 * h1 % P
    t2 = NB1_16 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_16 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_16 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_17) % P, led); led.add += 1
    t1 = NB0_17 * h1 % P
    t2 = NB1_17 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_17 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_17 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_18) % P, led); led.add += 1
    t1 = NB0_18 * h1 % P
    t2 = NB1_18 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_18 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_18 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_19) % P, led); led.add += 1
    t1 = NB0_19 * h1 % P
    t2 = NB1_19 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_19 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_19 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_20) % P, led); led.add += 1
    t1 = NB0_20 * h1 % P
    t2 = NB1_20 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_20 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_20 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_21) % P, led); led.add += 1
    t1 = NB0_21 * h1 % P
    t2 = NB1_21 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_21 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_21 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_22) % P, led); led.add += 1
    t1 = NB0_22 * h1 % P
    t2 = NB1_22 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_22 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_22 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_23) % P, led); led.add += 1
    t1 = NB0_23 * h1 % P
    t2 = NB1_23 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_23 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_23 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_24) % P, led); led.add += 1
    t1 = NB0_24 * h1 % P
    t2 = NB1_24 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_24 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_24 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_25) % P, led); led.add += 1
    t1 = NB0_25 * h1 % P
    t2 = NB1_25 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_25 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_25 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    x5 = _sbox((h0 + PU_26) % P, led); led.add += 1
    t1 = NB0_26 * h1 % P
    t2 = NB1_26 * h2 % P
    h0 = (x5 + t1 + t2) % P
    t1 = W0_26 * x5 % P
    h1 = (h1 + t1) % P
    t2 = W1_26 * x5 % P
    h2 = (h2 + t2) % P
    led.mult += 4; led.add += 4
    # round-60 S-box inputs from the partial form [7: 1 add + 2*(1 mult + 2 add)]
    y0 = (h0 + E60_0) % P
    t1 = Q60_1 * h2 % P
    y1 = (h1 + t1 + EC60_1) % P
    t1 = Q60_2 * h2 % P
    y2 = (h1 + t1 + EC60_2) % P
    led.mult += 2; led.add += 5
    # round 60 [9 mult sboxes + 6 mult + 9 add linear]
    z0 = _sbox(y0, led)
    z1 = _sbox(y1, led)
    z2 = _sbox(y2, led)
    t1 = K60_0_1 * z1 % P
    t2 = K60_0_2 * z2 % P
    y0 = (z0 + t1 + t2 + C61_0) % P
    t1 = K60_1_1 * z1 % P
    t2 = K60_1_2 * z2 % P
    y1 = (z0 + t1 + t2 + C61_1) % P
    t1 = K60_2_1 * z1 % P
    t2 = K60_2_2 * z2 % P
    y2 = (z0 + t1 + t2 + C61_2) % P
    led.mult += 6; led.add += 9
    # round 61 [9 + 15]
    z0 = _sbox(y0, led)
    z1 = _sbox(y1, led)
    z2 = _sbox(y2, led)
    t1 = K61_0_1 * z1 % P
    t2 = K61_0_2 * z2 % P
    y0 = (z0 + t1 + t2 + C62_0) % P
    t1 = K61_1_1 * z1 % P
    t2 = K61_1_2 * z2 % P
    y1 = (z0 + t1 + t2 + C62_1) % P
    t1 = K61_2_1 * z1 % P
    t2 = K61_2_2 * z2 % P
    y2 = (z0 + t1 + t2 + C62_2) % P
    led.mult += 6; led.add += 9
    # round 62 [9 + 15]
    z0 = _sbox(y0, led)
    z1 = _sbox(y1, led)
    z2 = _sbox(y2, led)
    t1 = K62_0_1 * z1 % P
    t2 = K62_0_2 * z2 % P
    y0 = (z0 + t1 + t2 + C63_0) % P
    t1 = K62_1_1 * z1 % P
    t2 = K62_1_2 * z2 % P
    y1 = (z0 + t1 + t2 + C63_1) % P
    t1 = K62_2_1 * z1 % P
    t2 = K62_2_2 * z2 % P
    y2 = (z0 + t1 + t2 + C63_2) % P
    led.mult += 6; led.add += 9
    # round 63: three S-boxes [9 mult], output row = digest / OUTSCALE
    # with the unit coefficient at lane 0 [2 mult + 2 add]
    z0 = _sbox(y0, led)
    z1 = _sbox(y1, led)
    z2 = _sbox(y2, led)
    t1 = CO_1 * z1 % P
    t2 = CO_2 * z2 % P
    out = (z0 + t1 + t2) % P
    led.mult += 2; led.add += 2
    # dp test (AND, compare, branch = 3) + loop control (3 per 4-step
    # unrolled block = 0.75) - charged word primitives
    led.word += OPS['dp']
    return out


def selftest(trials=64, seed=0x5EED23):
    rng = random.Random(seed)
    led = Ledger()
    for n in range(trials):
        x = rng.randrange(0, P)
        rho0 = rng.randrange(0, 1 << 254)
        W = (x + rho0) % P
        m0, m1 = message(W)
        want = ref_digest(m0, m1) * LAMBDA % P
        e = walk_e(rho0)
        led.reset()
        got = step(x, e, led)
        assert got == want, f'step mismatch at trial {n}'
    led.reset()
    step(0, walk_e(1), led)
    total = led.mult + led.add + led.word
    assert abs(total - STEP_OPS) < 1e-9, (total, STEP_OPS)
    print(f'selftest OK on {trials} random (x, rho0)')
    print(f'per-step ops: mult={led.mult} add={led.add} word={led.word:.2f} '
          f'total={total:.2f} budget={STEP_OPS} field={FIELD_OPS}')
    print(f'constants: nconst={NCONST} unit_lane=0 (OUTSCALE convention)')


if __name__ == '__main__':
    selftest()

# the attempt registers e_i = E0_i + rho0: named walk_ptilde for the
# search harness (attack.py imports it as the per-attempt register set)
walk_ptilde = walk_e
```

## Appendix B: `attack.py` (the filed search, recovery, exact plan, selftests)

`full_search` is the filed algorithm of Section 4 (one trail, distinguished points, index table, gap-bounded lockstep recovery) with the filed literals WALK/DETECT/GMAXC; `plan` derives and prints the exact ledger of Section 7 (80-digit Decimal); `--selftest` runs the 64-trial step check and the reduced-width end-to-end searches of Section 4; `--measure` produces the first-repeat walks of Section 6.

```python
#!/usr/bin/env python3
"""r=23 Orchard Poseidon generic birthday attack: full program.

The filed algorithm (one trail, distinguished points, index table,
gap-bounded lockstep recovery) and its exact ledger.  Standard library only.

Modes:
  --selftest        step program vs trusted reference (64 random trials)
                    plus a reduced-width end-to-end run of the same search
  --plan            exact budget, ledger and claimed score (80-digit Decimal)
  --measure         reduced-width first-repeat measurements for H1 (evidence)

Offline conventions (all constants precomputed from pinned deployed constants):
- Rounds 0..2: entry state and round-2 constants folded (t_k = QQ_k x + Ptilde_k);
  round 2 runs in scaled bases (linear layer 12 ops).
- Round 3: scaled-basis full round (24 ops), leaving basis M4.
- Rounds 4..26: partial rounds in the fixed basis MB = (M01,M11,M21)*M4[1]
  (lane-1 row coefficient exactly 1 in rows 0 and 2), constants kappa-folded
  into one addition per round: 17 ops each.
- Rounds 60..62: scaled-basis full rounds (24 ops each), exit constants
  folded at 60.
- Round 63: output lane only; walk scale LAMBDA folded into the row so the
  lane-1 coefficient is 1: 16 ops.
- dp test + loop control: 3.75 word ops per step; table work charged per
  distinguished event.
"""
import argparse
import hashlib
import json
import math
import random
from decimal import Decimal, getcontext
from pathlib import Path

import myrho
from myrho import (P, ref_digest, message, step, Ledger, walk_ptilde,
                   LAMBDA)

getcontext().prec = 80
GMAXC = 176060377939026895457446518306020702   # ceil(19.75/theta_lo) + 2 (plan)
DETECT = 82458658022075887745892673130667924    # detection window d (plan)
WALK = 169428545758018874978475100145551477411  # filed walk budget S0 = tight n0 + d (plan)
DVAL = 38176                       # dp threshold on the low 128 bits
DPMASK = (1 << 128) - 1
MCAP = 27413                       # dp-table entry cap


def dp_test(x):
    return (x & DPMASK) < DVAL


def dp_key(x):
    """Stored table key: (high 126 bits, low 16 bits).

    The threshold is below 2^16, so among dp values the low 16 bits
    determine the low 128 bits, and the high 126 bits determine the rest:
    the key is injective on dp values.  Packed layout (proof.md Section 8):
    one 32-byte word (high 126 bits | index) plus a 16-bit side field.
    """
    return (x >> 128, x & 0xFFFF)


def prg_coin(seed_bytes, k):
    """Deterministic coin draw from the master seed (rho0, x0)."""
    while True:
        h = hashlib.shake_256(seed_bytes + k.to_bytes(16, 'big')).digest(64)
        v = (int.from_bytes(h[:32], 'little')
             | (int.from_bytes(h[32:], 'little') << 256)) % (1 << 254)
        if v < P:
            return v


class Counters:
    def __init__(self):
        self.steps = 0        # F evaluations
        self.stored = 0       # dp entries stored
        self.events = 0       # dp events (probe + maybe insert)
        self.ops = 0.0         # charged operations

    def charge_step(self, led):
        self.steps += 1
        self.ops += led.mult + led.add + led.word

    def charge(self, ops):
        self.ops += ops


def full_search(rho0, x0, gmax=GMAXC, dval=DVAL, dpmask=DPMASK,
                mcap=MCAP, walk=WALK, led=None):
    """The filed algorithm: one trail, distinguished points, index table.

    Walk x_{i+1} = F(x_i) from x0.  Each distinguished value (low 128 bits
    below dval) is probed in the table and, if new, stored with its trail
    index (one 32-byte word holding the high 126 bits and the index, plus a
    16-bit side field).  On the first revisit x_b = x_a of a stored
    distinguished value (a its stored index, b the current index, L = b - a),
    let s be the index stored just before a (the start x0 at index 0 if
    none); compute x_{s+L} from the nearest stored point at or before s + L
    (at most gmax evaluations, else abandon); if x_s = x_{s+L}, abandon
    (start on the cycle); otherwise iterate both from (x_s, x_{s+L}) in
    lockstep (at most gmax rounds) and return the two predecessor states at
    the first image agreement: F(A) = F(B) with A != B (one lies on the
    tail, one on the cycle), an ordinary collision.  Recovery uses at most
    3 gmax evaluations when every gap between consecutive stored
    distinguished points is at most gmax.  `walk` is the trail-step budget
    (filed value derived by plan; tests use reduced values).
    """
    led = led or Counters()
    ptilde = walk_ptilde(rho0)
    table = {}                      # dp key -> trail index
    order = []                      # stored indices, increasing
    x = x0
    t = 0
    while walk is None or t < walk:
        t += 1
        s = Ledger()
        x = step(x, ptilde, s)
        led.charge_step(s)
        if (x & dpmask) < dval:
            led.events += 1
            led.charge(137081)     # full scan of the packed 27,413-entry table per dp event (5 word ops per probe + 16)
            key = dp_key(x)
            if key in table:
                a = table[key]
                L = t - a
                s_idx = max((i for i in order if i < a), default=0)
                led.charge(109668)  # order scan: 4 word ops per entry over <= 27,413 + 16
                xs = x0 if s_idx == 0 else reconstruct(table, s_idx)
                led.charge(109668)  # table scan (reconstruct)
                q = s_idx + L
                r = max((i for i in order if i <= q), default=0)
                led.charge(109668)  # order scan
                if q - r > gmax:
                    return None, led   # capped positioning (lemma eps)
                u = x0 if r == 0 else reconstruct(table, r)
                led.charge(109668)  # table scan (reconstruct)
                for _ in range(q - r):
                    su = Ledger()
                    u = step(u, ptilde, su)
                    led.charge_step(su)
                if u == xs:
                    return None, led   # start on the cycle (degenerate)
                A, B = xs, u
                for _ in range(gmax):
                    sa, sb = Ledger(), Ledger()
                    nA = step(A, ptilde, sa)
                    nB = step(B, ptilde, sb)
                    led.charge_step(sa)
                    led.charge_step(sb)
                    if nA == nB:
                        return (A, B), led
                    A, B = nA, nB
                return None, led       # capped lockstep (lemma eps)
            table[key] = t
            order.append(t)
            led.stored += 1
            if len(table) > mcap:
                return None, led       # table overflow (lemma eps)
    return None, led


def reconstruct(table, idx):
    """Reconstruct a stored dp value from its (high 126, low 16) key.

    The stored key is injective on dp values (threshold < 2^16): the low 16
    bits are the low 128 bits (below 2^16), the high 126 bits shift back.
    """
    key = next(k for k, i in table.items() if i == idx)
    high, low = key
    return (high << 128) | low


def verify_pair(pa, pb, rho0):
    """Two distinct walk predecessors with equal images give equal digests."""
    Wa, Wb = (pa + rho0) % P, (pb + rho0) % P
    ma, mb = message(Wa), message(Wb)
    assert ma != mb, 'degenerate pair'
    da, db = ref_digest(*ma), ref_digest(*mb)
    assert da == db, 'not a collision'
    return ma, mb, da


# --------------------------- exact plan (offline) ---------------------------
def plan():
    """Exact budget, ledger and claimed score for the filed entry.

    Success lemma (uniform random function, proof.md Section 5): one trail
    of n steps with detection window d, dp density theta, recovery cap gmax
    fails with probability at most
        exp(-n(n+1)/(2N))           no repeat within the trail budget
        + n/N                        start on the cycle
        + exp(-KD)                   no dp in the first d cycle values
        + n*d/N                      cycle shorter than d
        + (S*theta_hi + 1) e^-H      a dp-to-dp gap (or start-to-first-dp
                                      gap) above gmax: positioning and
                                      lockstep walks capped, pair abandoned
        + e^-TAB                     dp-table overflow (Chernoff)
        + 4/N                        degenerate recovery pair,
    with S = n + d, KD = 9.25, H = 19.75, TAB = 12, N = p.  The hazard-factor
    form (H1, proof.md Section 6) scales the repeat term by c.  This entry
    files the TIGHT convention: the trail budget is n0 itself (the lemma
    at c = 1 gives success 0.390000000 exactly), the real-map transfer is
    the bare premise H1 with no hazard margin - the convention of the
    accepted r=22/r=24+ incumbents.
    """
    DP = Decimal(P)
    D = Decimal(((1 << 126) + 1) * DVAL)
    theta_lo = (D - (1 << 128)) / DP
    theta_hi = D / (DP - (1 << 128))
    KD, H, TAB = Decimal('9.25'), Decimal('19.75'), Decimal(12)
    d = -(-KD // theta_lo)
    d = int((d + 3) // 4 * 4)
    gmax = int(-(-H // theta_lo)) + 2

    def fail(n, c):
        cc = Decimal(str(c))
        nn = Decimal(n)
        S = nn + d
        merge = (-(cc * nn * (nn + 1) / (2 * DP))).exp()
        start_cycle = nn / DP
        detect_fail = (-KD).exp()
        short_cycle = nn * d / DP
        gap = (S * theta_hi + 1) * (-H).exp()
        over = (-TAB).exp()
        degen = Decimal(4) / DP
        return merge + start_cycle + detect_fail + short_cycle + gap + over + degen

    def solve(c):
        lo, hi = 1, 1 << 42
        while Decimal('0.39') > 1 - fail(hi, c):
            hi *= 2
        while lo < hi:
            mid = (lo + hi) // 2
            if 1 - fail(mid, c) >= Decimal('0.39'):
                hi = mid
            else:
                lo = mid + 1
        return lo

    n0 = solve(1)                              # random function: tight budget
    n1 = solve(Decimal('0.90'))                # tolerance floor c = 0.90
    S1 = n1 + d

    step_ops = Decimal('419.75')             # sparse-form step: 416 field + 3.75 word
    rec_evals = 3 * (gmax + 16)                # recovery cap: 3 gmax charged
    rec_ops = (Decimal(rec_evals) * (step_ops + 6)
               + Decimal(4 * (4 * MCAP + 16)))   # <= 4 recovery scans over the table
    dp_events = int((Decimal(S1) * theta_hi).to_integral_value(
        rounding='ROUND_CEILING'))
    table_ops = Decimal(MCAP + 1) * Decimal(5 * MCAP + 16)   # cap events x full scan
    prg_ops = Decimal(2 * 264)                 # two coin draws
    setup = Decimal(2000)
    roots = Decimal(2286)                     # fifth roots for both messages
    prep = Decimal(1 << 41)                   # offline: constants + budget solve + campaign
    total = (Decimal(n0 + d) * step_ops + rec_ops + table_ops + prg_ops + setup
             + roots + prep)
    units = total / Decimal(699)
    score = units.ln() / Decimal(2).ln()

    print(json.dumps({
        'dp_threshold': DVAL,
        'theta_lo_log2': str(theta_lo.log10() / Decimal(10).log10()),
        'KD': str(KD), 'H': str(H), 'TAB': int(TAB),
        'theta_hi_log2': str(theta_hi.log10() / Decimal(10).log10()),
        'd': d, 'gmax': gmax, 'mcap': MCAP,
        'n0': n0, 'success_random_at_n0': str(1 - fail(n0, 1)),
        'n1': n1, 'S1': S1,
        'success_random_at_n1': str(1 - fail(n1, 1)),
        'success_at_floor_at_n1': str(1 - fail(n1, Decimal('0.90'))),
        'per_step_ops': '419.75',
        'walk_ops': str(Decimal(n0 + d) * step_ops),
        'recovery_ops': str(rec_ops),
        'table_ops': str(table_ops), 'prg_ops': str(prg_ops),
        'dp_events': dp_events,
        'total_ops': str(total), 'C': 699,
        'units': str(units), 'time_log2': str(score),
        'time_log2_float': float(score),
    }, indent=2))


# --------------------------- H1 measurements (evidence) --------------------
def measure(widths=(16, 20, 24, 28), walks=120, seed=0x5EED2EED):
    """Reduced-width first-repeat measurements on the real r=23 map."""
    rng = random.Random(seed)
    data = {}
    for w in widths:
        mask = (1 << w) - 1
        lens = []
        for _ in range(walks):
            rho0 = rng.randrange(0, 1 << 254)
            v = rng.randrange(0, 1 << w)
            ptilde = walk_ptilde(rho0)
            seen = {v}
            i = 0
            while True:
                v = step(v, ptilde, Ledger()) & mask
                i += 1
                if v in seen:
                    lens.append(i)
                    break
                seen.add(v)
        data[w] = lens
        mean = sum(lens) / len(lens)
        exp_mean = math.sqrt(math.pi * (1 << w) / 2)
        print(f'width {w}: {len(lens)} walks, mean first repeat {mean:.1f} '
              f'(random-function expectation {exp_mean:.1f})')
    Path(__file__).parent.joinpath('measurements.json').write_text(
        json.dumps({str(w): data[w] for w in widths}))


# --------------------------- self tests --------------------------------------
def selftest(trials=64, seed=0x5EED23):
    """Step program vs trusted reference, then a reduced-width full search."""
    rng = random.Random(seed)
    led = Ledger()
    for n in range(trials):
        x = rng.randrange(0, P)
        rho0 = rng.randrange(0, 1 << 254)
        W = (x + rho0) % P
        m0, m1 = message(W)
        want = ref_digest(m0, m1) * LAMBDA % P
        ptilde = walk_ptilde(rho0)
        led.reset()
        got = step(x, ptilde, led)
        assert got == want, f'step mismatch at trial {n}'
    print(f'step selftest: {trials}/{trials} equal to reference*LAMBDA (LAMBDA = 1/OUTSCALE), '
          f'per-step={led.mult + led.add + led.word:.2f} (budget 419.75)')
    # Reduced-width end-to-end run of the same single-trail search: the
    # truncated map (w bits) with a dense dp test on the low dp_bits.  These
    # are TEST parameters; the filed literals are the plan() values.
    ok = 0
    for trial in range(3):
        rho0 = rng.randrange(0, 1 << 254)
        x0 = rng.randrange(0, 1 << 40)
        w, dp_bits, thr = 40, 20, 512
        mask = (1 << w) - 1
        dpm = (1 << dp_bits) - 1
        ptilde = walk_ptilde(rho0)

        def dpk(v):
            return (v >> dp_bits, v & 0xFFFF)

        table, order = {}, []
        x, pair = x0 & mask, None
        steps = 0
        while steps < (1 << 22):
            steps += 1
            x = step(x, ptilde, Ledger()) & mask
            if (x & dpm) < thr:
                key = dpk(x)
                if key in table:
                    a = table[key]
                    L = steps - a
                    s_idx = max((i for i in order if i < a), default=0)
                    q = s_idx + L
                    r = max((i for i in order if i <= q), default=0)
                    if q - r > 4096:
                        break
                    u = (x0 & mask) if r == 0 else (
                        (dpk_inv(table, r, dp_bits)))
                    for _ in range(q - r):
                        u = step(u, ptilde, Ledger()) & mask
                    xs = (x0 & mask) if s_idx == 0 else (
                        (dpk_inv(table, s_idx, dp_bits)))
                    if u == xs:
                        break
                    A, B = xs, u
                    for _ in range(4096):
                        nA = step(A, ptilde, Ledger()) & mask
                        nB = step(B, ptilde, Ledger()) & mask
                        if nA == nB:
                            pair = (A, B)
                            break
                        A, B = nA, nB
                    break
                table[key] = steps
                order.append(steps)
        if pair:
            pa, pb = pair
            Wa, Wb = (pa + rho0) % P, (pb + rho0) % P
            ma, mb = message(Wa), message(Wb)
            assert ma != mb
            da = ref_digest(*ma) * LAMBDA % P
            db = ref_digest(*mb) * LAMBDA % P
            assert (da & mask) == (db & mask)
            ok += 1
            print(f'trial {trial}: truncated collision verified after '
                  f'{steps} steps; messages differ, {w}-bit digests agree')
    print(f'reduced-width full search: {ok}/3 verified truncated collisions')


def dpk_inv(table, idx, dp_bits):
    key = next(k for k, i in table.items() if i == idx)
    high, low = key
    return (high << dp_bits) | low


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--plan', action='store_true')
    ap.add_argument('--measure', action='store_true')
    args = ap.parse_args()
    if args.plan:
        plan()
    elif args.measure:
        measure()
    elif args.selftest:
        selftest()
    else:
        myrho.selftest()
```

## Appendix C: `measure2.py` and `analysis.py` (H1 evidence)

`measure2.py`: first-repeat walks on truncated real maps, 8-way chunked, widths {16, 20, 24, 28, 32, 36}, fresh (rho, start) per walk. `analysis.py`: exact discrete first-repeat likelihood (series with bounded tail), per-width and pooled profile-likelihood intervals.

```python
#!/usr/bin/env python3
"""Scaled H1 measurements: first-repeat walks on truncated real r=23 maps.

Each width is split into 8 seed-distinct chunks run in parallel, so every
width completes in wall time ~ (walks/8) * mean_steps * per-step cost.
Widths 16..36, fresh (rho, start) per walk; walk states truncated to w bits
every step (the truncated map is the birthday model at width w).
Saves measurements2.json as {str(w): [first-repeat lengths]}.
"""
import json
import math
import multiprocessing as mp
import random
import time
from pathlib import Path

from myrho import walk_ptilde, step, Ledger

NCHUNK = 8
JOBS = {16: 1200, 20: 6000, 24: 6000, 28: 1200, 32: 1200, 36: 300}


def worker(args):
    w, walks, seed = args
    rng = random.Random(seed)
    mask = (1 << w) - 1
    out = []
    for _ in range(walks):
        rho0 = rng.randrange(0, 1 << 254)
        v = rng.randrange(0, 1 << w)
        ptilde = walk_ptilde(rho0)
        seen = {v}
        i = 0
        led = Ledger()
        while True:
            v = step(v, ptilde, led) & mask
            i += 1
            if v in seen:
                out.append(i)
                break
            seen.add(v)
    return w, out


def main():
    jobs = []
    for w, total in sorted(JOBS.items()):
        walks, extra = divmod(total, NCHUNK)
        for chunk in range(NCHUNK):
            n = walks + (1 if chunk < extra else 0)
            if n:
                jobs.append((w, n, 0x5EED0000 + w * 100 + chunk))
    t0 = time.time()
    with mp.Pool(NCHUNK) as pool:
        results = pool.map(worker, jobs)
    data = {}
    for w, lens in results:
        data.setdefault(w, []).extend(lens)
    out = {str(w): sorted(v) for w, v in data.items()}
    Path('measurements2.json').write_text(json.dumps(out))
    for w in sorted(data):
        lens = data[w]
        mean = sum(lens) / len(lens)
        exp_mean = math.sqrt(math.pi * (1 << w) / 2)
        print(f'width {w}: n={len(lens)} mean={mean:.1f} rand={exp_mean:.1f} '
              f'ratio={mean / exp_mean:.4f}')
    print(f'total {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
```

```python
#!/usr/bin/env python3
"""H1 evidence analysis: hazard multiplier, profile-likelihood CI, coverage.

Exact discrete first-repeat law (uniform random function on N points):
  P(L = l) = (l/N) * prod_{j=1..l-1} (1 - j/N).
Hazard-multiplier family: P(L = l | m) = (m l/N) * prod_{j<l} (1 - m j/N).
For our sizes m j/N <= 2*19500/2^16 < 0.61 worst case (width 16, m=2), so the
survival log is expanded in a series with exact S1/S2/S3 sums and a guard:
  sum_j log(1 - m j/N) = -m S1/N - m^2 S2/(2 N^2) - m^3 S3/(3 N^3) - ...
Wider widths use more terms; the truncated tail is bounded and shown.
"""
import json
import math
from pathlib import Path

CHI2 = 3.841458820694124


def loglik(lens, N, m, terms=6):
    ll = 0.0
    bound = 0.0
    for l in lens:
        # powers sums S_k = sum_{j=1}^{l-1} j^k (closed forms)
        n = l - 1
        S1 = n * (n + 1) // 2
        S2 = n * (n + 1) * (2 * n + 1) // 6
        S3 = (S1 * S1)
        S4 = n * (n + 1) * (2 * n + 1) * (3 * n * n + 3 * n - 1) // 30
        hazard = m * l / N
        if hazard >= 1.0:
            return float('-inf'), 0.0
        ll += math.log(hazard)
        x = m / N
        ll -= x * S1
        ll -= x * x * S2 / 2
        ll -= x ** 3 * S3 / 3
        if terms > 3:
            ll -= x ** 4 * S4 / 4
        # truncation tail bound: sum_{k>=5} (x n)^k / k * n  <= n*(x n)^5/(5(1-x n))
        xn = x * n
        if xn < 0.9:
            bound += n * xn ** 5 / (5 * (1 - xn))
    return ll, bound


def mle(lens, N):
    def f(m):
        return loglik(lens, N, m)[0]
    grid = [0.2 + 0.002 * i for i in range(4001)]
    best = max(grid, key=f)
    a, b = max(0.01, best - 0.004), min(5.0, best + 0.004)
    for _ in range(200):
        m1 = a + (b - a) / 3
        m2 = b - (b - a) / 3
        if f(m1) < f(m2):
            a = m1
        else:
            b = m2
    return (a + b) / 2


def interval(lens, N, mhat, target):
    lo, hi = mhat, mhat
    step = mhat / 2
    while step > 1e-5:
        if lo - step > 0 and loglik(lens, N, lo - step)[0] >= target:
            lo -= step
        if loglik(lens, N, hi + step)[0] >= target:
            hi += step
        step /= 2
    return lo, hi


def main():
    data = {}
    for fn in ('measurements.json', 'measurements2.json'):
        p = Path(fn)
        if not p.exists():
            continue
        for k, v in json.loads(p.read_text()).items():
            data.setdefault(int(k), []).extend(v)
    report = {}
    for w in sorted(data):
        lens = data[w]
        N = 1 << w
        mh = mle(lens, N)
        ll, bound = loglik(lens, N, mh)
        target = ll - CHI2 / 2
        lo, hi = interval(lens, N, mh, target)
        report[w] = dict(mhat=round(mh, 4), lo=round(lo, 4), hi=round(hi, 4),
                          n=len(lens), tail_bound=round(bound, 8))
        print(f'width {w}: mhat={mh:.4f} 95% CI [{lo:.4f}, {hi:.4f}] '
              f'(n={len(lens)}, tail bound {bound:.2e})')
    # pooled across widths
    def pooled(m):
        return sum(loglik(data[w], 1 << w, m)[0] for w in data)
    grid = [0.5 + 0.001 * i for i in range(3001)]
    best = max(grid, key=pooled)
    a, b = max(0.01, best - 0.003), min(5.0, best + 0.003)
    for _ in range(200):
        m1 = a + (b - a) / 3
        m2 = b - (b - a) / 3
        if pooled(m1) < pooled(m2):
            a = m1
        else:
            b = m2
    best = (a + b) / 2
    llmax = pooled(best)
    lo, hi = best, best
    step = best / 2
    while step > 1e-5:
        if lo - step > 0 and pooled(lo - step) >= llmax - CHI2 / 2:
            lo -= step
        if pooled(hi + step) >= llmax - CHI2 / 2:
            hi += step
        step /= 2
    print(f'pooled: mhat={best:.4f} 95% CI [{lo:.4f}, {hi:.4f}]')
    report['pooled'] = dict(mhat=round(best, 4), lo=round(lo, 4), hi=round(hi, 4))
    Path('analysis.json').write_text(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
```
