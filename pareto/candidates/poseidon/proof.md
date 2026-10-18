# Proof: generic birthday (distinguished-point rho) collision, Orchard Poseidon r=21

Target `poseidon-orchard-r21-prefix-v1` (Pallas P128Pow5T3, ConstantLength<2>, halo2_poseidon 0.2.0 pinned constants; 8 fixed full rounds around 21 partial rounds; digest = state[0], whole element compared). Attack class `ordinary-collision`. Cost model `orchard-field-ram-v2`: every field addition/subtraction/multiplication and every 256-bit word primitive is charged 1/C target compressions with C = 216 + 21*21 = 657; exponentiation/inversion are charged as their counted constituent operations. No asymptotic-only claim is made; every bound below is a finite number at the actual dimensions.

## 1. The claim

* `time_log2` = 126.70323 `target-compressions` (exact Decimal 126.703225; rounded **up** at 5 decimals).
* `memory_log2_bytes` = 20 (reviewed total 1,048,518 bytes < 2^20; normalized memory penalty max(0, 20 - 20) = 0).
* `success_probability` = 0.39 at the filed walk budget (Section 5 for the random-function lemma, Section 6 for the measured hazard transfer).
* `preprocessing_log2` = 29; all offline derivation (constants, budget solve, the measurement campaign) is bounded by 2^38 word operations and charged **inside** `time_log2` (Section 9, ledger line "offline derivation").
* `nonuniform_advice_log2_bytes` = 0 (no precomputed collision, no nonuniform advice; the master seed is drawn by the attack itself).

## 2. The walk map (two-round bypass line)

Round 0 maps (m0, m1) bijectively to (U, V) = ((m0 + C[0][0])^5, (m1 + C[0][1])^5). On the line (U, V) = (U0 + a*tau, V0 + b*tau) with a = MDS[0][1] and b = -MDS[0][0] mod p, the round-1 S-box inputs are (U0 + a*tau)^5, (V0 + b*tau)^5 and the capacity-lane constant, so with W = tau^5 the state after round 1 is A + W*B (two-round bypass; Bariant, Bouvier, Leurent, Perrin, ToSC 2022). The line constants, from the pinned deployed constants:

```
p   = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
a   = 0x31916628e58a5abb293f0f0d886c7954240d4a7cbf735736 8eca5596e996ab5e
b   = 0x354a1a478b5972184c2a60423736152b8a6ef850e5c7edc566ee0c66281ee49e
U0  = 0x2de17246e844b000296eefaaf2116b9705e3af63806d80541c7d6b4be442036c
V0  = 0x2622542e119aef1f7c021664aae329063a3e73651cd62e02756427f9437fdd96
A0  = 0x2a78890d8503b228bfa6bd9b312401c7af4e02a6376ceebb003ef1138f67c72c
D1  = 0x2b1cf2a34b2b6723837c31d51d5c91d12d1a715784a437124e3daf150a8d2b15
D2  = 0x194af15c17a9f125b198b4fcacb6f6a0d7525c1960573b90b20d8c6a16f61d57
d   = 1/5 mod (p-1) = 0x333333333333333333333333333333334e9ee0c9a10a60e2e0f0f3f0cccccccd
LAMBDA = 0x1c402ca73c17b5bc5fdda9e57cea27f28529b69aa141504bab0f6543e852f392
```

U0, V0 solve the 2x2 linear system that fixes A's first two lanes through the capacity lane; A0 closes A's third lane; D1, D2 are B's first two lanes. message(W) inverts the line injectively: tau = W^d, U = U0 + a*tau, V = V0 + b*tau, m0 = U^d - C[0][0], m1 = V^d - C[0][1]; both are canonical field elements by construction. The attack fixes one random rho0 (low 254 bits of a PRG draw) and one random start x0 (a second PRG draw) and walks

F(x) = digest(message(x + rho0)) * LAMBDA mod p,

where the walk scale LAMBDA = (MDS[0][1] * M63[1]^5)^-1 mod p is folded into the round-63 row so the lane-1 coefficient stays 1 (Section 3). Two distinct walk values x != y with F(x) = F(y) give distinct W_x != W_y (message is injective), hence distinct canonical messages with equal digests: an ordinary collision.

## 3. The step program (508 charged operations per step)

| block | ops | breakdown |
| --- | ---: | --- |
| rounds 0-2, folded entry | 27 | 6 (t_k = QQ_k*x + Ptilde_k) + 9 (three S-boxes t_k^5) + 12 (round-2 linear layer in scaled bases) |
| round 3 (scaled bases) | 24 | 3 add + 9 S-box + 12 linear |
| entry rescale into partial basis | 2 | 2 mult (GAMMA_0 sig_0, GAMMA_2 sig_2; lane 1 already scaled) |
| 21 partial rounds | 357 | 17 each: 1 add (sig_0 + kappa0hat_i), 3 S-box (t0h), 7 mult + 6 add (sig'_j = MH0_j t0h + sig_1 + MH2_j sig_2; lane-1 coefficient exactly 1 in rows 0 and 2) |
| rounds 60-62 (scaled bases) | 72 | 24 each: 3 add + 9 S-box + 12 linear; partial-phase exit constants folded into round 60 |
| round 63 (output lane only) | 16 | 3 add + 9 S-box + 2 mult + 2 add (row B63R with LAMBDA folded; lane-1 coefficient 1) |
| dp test (lane-0 mask, threshold compare) | 2 | word primitives |
| loop control (counter increment, branch compare) | 2 | word primitives |
| state traffic (x load, 3 ptilde loads, x store, 1 spare) | 6 | word primitives |
| **total per step** | **508** | |

Derivation of the 10 word primitives per step: load x (1), load the three ptilde lanes (3), dp mask + threshold compare on the output lane (2), store the output lane to x (1), counter increment + branch compare (2) = 9, charged as 10 (one spare for alignment). The cost model prices one field addition, subtraction or multiplication at 1/C flat (computation_model: no operand-fetch toll), and prices a load or store only as the executed word primitive; the walk lanes, ptilde and accumulators of the reference implementation (Appendix B) are procedure locals for the whole step, and the list above is the complete memory-primitive traffic of the step in that implementation.

The partial rounds run in the fixed scaled basis MB = (MDS[0][1], 1, MDS[2][1]) * M4[1], chosen so rows 0 and 2 have lane-1 coefficient exactly 1; all per-round constants are kappa-folded into the single addition per round (the kappa recursion kappa(i+1)_j = MH1_j kappa_1 + MH2_j kappa_2 + Khat_j is exact and offline). Bases chain M3 (after round 2), M4 (after round 3), MB (partial phase), M61..M63 (rounds 60-62). The step program runs rounds 4..24 as the selected partial rounds of this target; every other block is round-independent.

The step program equals digest(message(x + rho0)) * LAMBDA on 64 of 64 random (x, rho0) trials against the organizer's trusted reference permutation at r=21 (`--selftest`), and its per-step ledger totals exactly 508. Every field multiplication/addition and every word primitive in the actual code path is counted; no operation is uncharged.

## 4. The search: one trail, distinguished points, index table, recovery

A walk value is distinguished iff its low 128 bits are < 38176; the threshold is below 2^16, so the low 16 bits determine the low 128 bits among dp values and a stored key (high 126 bits, low 16 bits) is injective on dp values. Exactly D = (2^126 + 1) * 38176 of the p field elements are distinguished (p = 2^254 + c with c = p mod 2^128 >= 38176), theta = D/N in [10^-33.95009453, 10^-33.95004902] (conditioning bounds theta_lo = (D - 2^128)/N, theta_hi = D/(N - 2^128)).

Packed table layout and per-event charge (finite derivation). The table is an open-addressed array of MCAP = 27,413 slots of one aligned 32-byte word each, plus one 16-bit side field per slot; the slot of a dp value is its low 16 bits taken modulo 27,413, collisions resolved by linear probing, and the stored key (high 126 bits, low 16 bits) is compared in full, so no false match is possible. One probe costs at most 3 word primitives (load the 32-byte word, shift out the high 126 bits, compare); the terminal compare against the side field, the slot arithmetic and the insertion writes (store entry word, store side field, update the entry count) cost at most 16 word primitives. A scan is at most one full table pass: 27,413 probes, hence at most 3*27,413 + 16 = 82,455 word operations per dp event. Events are deterministic in count: every arriving dp value either inserts (at most MCAP = 27,413 inserts, the algorithm abandons at the cap) or is the first repeat, which returns; so at most 27,414 events occur per attempt and the dp-table charge 27,414 * 82,455 = 2254938570 word operations is a deterministic upper bound (the expectation at the mean load 20,037/27,413 would be far smaller; no expectation is charged). The two recovery index lookups (the largest stored index below a, and the largest stored index at or below q) are single scans of the same entry words - the trail index is inside each 32-byte entry word - at the same <= 82,455 word operations each, charged in the recovery line of Section 7. No auxiliary ordered index list exists in the layout or the algorithm; the runtime `Counters` of Appendix B instruments the reference implementation's dict probes, and every filed bound charges the deterministic caps above, which dominate those counts.

The algorithm (Appendix B, `full_search`): draw the coins rho0 and x0 (two PRG draws - domain-separated SHAKE-256 outputs of the algorithm's own master seed, `prg_coin`; the coins-as-drawn uniformity is part of premise H1, Section 6); walk x_(i+1) = F(x_i) from x0 for at most S1 = n1 + d steps (82458658022075887745892673130667924 = detection window, Section 5). Each distinguished value is probed in the table and, if new, stored with its trail index: one 32-byte word holding the high 126 bits of the value and the index, plus a 16-bit side field holding the low 16 bits. A distinguished value can be reconstructed exactly from its word and side field (injectivity above). Distinguished values on the tail never repeat (a cycle value cannot equal a tail value); the first repeat of a stored dp value detects the cycle.

Recovery (deterministic, Appendix B): the repeat is x_b = x_a (a the stored index, b the current index, L = b - a). Let s be the index stored just before a (the start x0 at index 0 if none). Compute x_(s+L) from the nearest stored point at or before s + L (at most gmax evaluations, else abandon). If x_s = x_(s+L), abandon (start on the cycle). Otherwise iterate both walkers from (x_s, x_(s+L)) in lockstep (at most gmax rounds); the first time their images agree, the two predecessor states (A, B) satisfy F(A) = F(B) with A on the tail and B on the cycle, hence A != B: an ordinary collision. The output is the two messages message(A + rho0), message(B + rho0) (three fifth roots each). Recovery uses at most gmax (positioning) + 2 gmax (lockstep) = 3 gmax evaluations when every gap between consecutive stored distinguished points is at most gmax; the recovery ledger charges 3*(gmax+16) evaluations in full.

Reduced-width end-to-end check of the same search (Appendix B `--selftest`): truncated map (w = 40 bits), dense dp test (threshold 512 on the low 20 bits), trail budget 2^22: three seeded trials; each trial either finds and verifies a truncated collision (messages distinct, 40-bit digests equal) against the trusted reference or is abandoned at the test gap cap (the lemma's gap term; the filed gmax is far larger relative to the filed density); these are test parameters, not the filed literals.

## 5. Success lemma (uniform random function, exact)

F a uniformly random function on N = p points, x0 any fixed element (every statement conditional on the start). With the parameters of Section 4 (threshold T = 38176, D = (2^126 + 1) T, theta_lo <= theta <= theta_hi, detection window d = ceil(9.25/theta_lo) rounded up to a multiple of 4, gap cap gmax = ceil(19.75/theta_lo) + 2, table cap MCAP = 27413, trail budget n, total budget S = n + d), the attempt fails with probability at most

1. no repeat within the trail budget: exp(-n(n+1)/(2N)) - a fresh value repeats one of the i + 1 earlier values with probability (i + 1)/N, and the chain rule over i < n gives the product bound;
2. start on the cycle: n/N;
3. no dp in the first d cycle values given the repeat (t <= n, mu, lambda >= d): (1 - theta_lo)^d <= e^-9.25 (a fresh value is distinguished with conditional probability at least theta_lo whatever the history);
4. cycle shorter than d: n*d/N;
5. a dp-to-dp gap (or start-to-first-dp gap) above gmax: (S*theta_hi + 1) e^-19.75 - positioning and lockstep walks are capped at gmax and the pair abandoned;
6. dp-table overflow: e^-12 (Chernoff on the number of stored dps, mean S*theta_hi = 20037 << MCAP + 1);
7. degenerate recovery pair: 4/N.

Conditioning (each term is exact under its hypothesis). Given no repeat among the first i iterates, the chain rule leaves x_i uniform and independent of the earlier values, so the next iterate equals one fixed earlier value with probability exactly (i + 1)/N; term 1 is the product of these over i < n. Given the first repeat at index t = mu + lambda <= n with the cycle length lambda >= d (term 4 bounds the complement P(lambda < d) <= n*d/N), the d detection-window values x_(t+1)..x_(t+d) are d distinct cycle values, and each fails the dp test with conditional probability at most 1 - theta_lo (term 3); the dp-to-dp gaps between consecutive distinguished cycle values dominate a geometric with success parameter at least theta_lo, so P(gap > gmax) <= (1 - theta_lo)^gmax <= e^-19.75 (term 5). Term 6 is Chernoff on the number of inserts (each arriving value is distinguished with conditional probability at most theta_hi whatever the history); term 7 bounds the degenerate recovery pair.

Solving 1 - fail(n) >= 0.39 in 80-digit Decimal gives the tight random-function trail budget n0 = 169346087099996799090729207472420809487 (success at n0 exactly 0.390000000...). The filed budget below scales this by the measured hazard floor.

## 6. Premise H1 and the filed budget

H1 (`H1-random-walk-rate`), the only premise of the claim.
* Statement: the filed trail has n1 = 178514977233407124990816098423499042677 steps, at which the lemma of Section 5 with the repeat hazard scaled by c = 0.90 (see below) bounds the success at exactly 0.39. Premise: for the attempt's coins (rho0 and x0, uniform 254-bit words), the search of Section 4 on the real map F(x) = digest(message(x + rho0)) * LAMBDA, at the trail budget n1, succeeds with probability at least 0.39. **H1 is our theory that, for this search, the fixed map with a random rho0 behaves like a uniformly random function; this is an assumption and no proof is known.**
* Role: score-critical. It is the only step from the lemma to the claimed success probability; the step program (Section 3), the search and recovery (Section 4), the ledger (Section 7) and the memory (Section 8) are proved or checked exactly.
* Scope: target poseidon-orchard-r21-prefix-v1, inputs on the line of Section 2, one search with the parameters of Section 4 (walk budget S1 = 178597435891429200878561991096629710601). Not claimed for other round counts or budgets.

Budget and tolerance. Within the hazard-multiplier family (the real map's per-step repeat hazard is a constant multiple c of the random-function hazard), the repeat term of the lemma scales as exp(-c x) with x = n(n+1)/(2p); the other failure terms are unchanged. The filed budget n1 is the smallest trail budget at which the premise survives **every hazard factor c >= 0.90**: at n1 (x = 0.55043), the success at the floor c = 0.90 is exactly 0.39 by construction, and the random function (c = 1) reaches 0.4226. The floor 0.90 lies **below the pooled 95% profile-likelihood lower bound 1.0037 (all 15900 walks over the six widths; the hazard-multiplier family has the single parameter c, and the pooled interval is its estimate)**, so the reduced-width evidence dominates the tolerance. The per-width cells of the table are diagnostics of the single-multiplier model (no slope across widths); the smallest single-cell lower bound is 0.9434 (printed, not load-bearing), as in the incumbent's accepted design.

Evidence (participant-run; the organizer-run experiment is Section 10; the complete per-walk raw data is printed in Appendix D and is byte-reproducible from the deterministic seeded harness, `python3 measure_rounds.py 21`): first-repeat walks on the real r=21 map truncated to w bits (the truncated map is the birthday model at width w), fresh (rho, start) per walk, every walk run to its exact first repeat, 15900 walks over six widths, exact discrete first-repeat likelihood P(L=l|m) = (m*l/N) * prod_(j<l) (1 - m*j/N) (series-summed with bounded tail), profile-likelihood 95% intervals:

| width w | walks | hazard multiplier m-hat | 95% profile-likelihood CI | series tail bound |
| ---: | ---: | ---: | --- | ---: |
| 16 | 1200 | 1.0421 | [0.9844, 1.1020] | 2.6e-06 |
| 20 | 6000 | 1.0074 | [0.9821, 1.0330] | 5.0e-08 |
| 24 | 6000 | 1.0112 | [0.9858, 1.0370] | 0.0e+00 |
| 28 | 1200 | 1.0477 | [0.9896, 1.1081] | 0.0e+00 |
| 32 | 1200 | 1.0658 | [1.0066, 1.1272] | 0.0e+00 |
| 36 | 300 | 1.0587 | [0.9434, 1.1830] | 0.0e+00 |

Pooled multiplier 1.0195, 95% profile-likelihood CI [1.0037, 1.0354]; the per-width estimates are consistent with a constant multiplier across widths (no slope). Seeds and stopping rule: each walk draws rho0 uniform on 254 bits and a start uniform on 2^w from an independent seeded stream (Appendix C, per-chunk seeds); every walk ran to its first repeat, none was dropped, repeated or selected; there is no stopping rule. The exact discrete law is used throughout; no exponential or Gamma approximation of the first-repeat index enters the estimates.

Sensitivity at the filed budget S1 (repeat term x = 0.55043; other eps terms 6.6e-04):

| hazard factor c | 1.0354 (pooled upper) | 1 (random) | 1.0037 (pooled lower) | 1.0066 (w=32 lower) | 0.9434 (smallest single cell lower (w=36)) | 0.90 (floor) | 0.85 (below floor) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| success at S1 | 0.4338 | 0.4226 | 0.4238 | 0.4247 | 0.4044 | 0.3900 | 0.3730 |

Extrapolation: from widths 16 to 36 at r = 21, where the multiplier is measured, to width 254 at r = 21, by H1. The measurements show that the random-function first-repeat law holds on the real round function at every measured width, and every measured lower bound lies above the tolerance floor; they do not bound the multiplier at full width. The full-width first repeat cannot be observed at feasible cost, so the transfer is the premise itself.

Limitations: the measurements are reduced-width only (16 to 36 bits, first-repeat indexes of order 2^19 steps); they say nothing about the 254-bit map beyond the premise. The interval is a profile-likelihood interval, asymptotic in the number of walks and conditional on the hazard-multiplier family; it is evidence about the multiplier, not a bound on it. The organizer experiment's checked event (Section 10) is one width (14 bits), one round count, a witness-only event on the digest; its w=16 witness walks (untrusted observations) corroborate the width-16 cell only. Neither validates H1, the cost or the success probability. On a single fixed map the success over starts varies with that map's cycle structure; the attempt therefore draws rho0 as a coin, and H1 concerns the average over rho0.

## 7. Ledger at the filed budget

```
walk budget S1 = n1 + d  = 178597435891429200878561991096629710601   (trail 178514977233407124990816098423499042677 + detection window 82458658022075887745892673130667924)
dp threshold                = 38176 (low 128 bits); D = (2^126 + 1) * 38176
theta_lo = (D - 2^128)/p   = 10^-33.95009453
theta_hi = D/(p - 2^128)   = 10^-33.95004902
d (detection window)       = 82458658022075887745892673130667924   = ceil(9.25/theta_lo) rounded up to 4
gmax (gap cap)              = 176060377939026895457446518306020702   = ceil(19.75/theta_lo) + 2
MCAP                       = 27413 entries
per-step ops                 = 508  (listing in Section 3)
walk ops    S1 * 508  = 90727497432846034046309491477087892985308
recovery    3*(gmax+16) evaluations at 508 + 6 each, plus 2 table scans
            (<= 3*27,413 + 16 word ops each, cap charge) = 271485102781979472795382531227884111666
dp-table    <= 27,414 events (cap; mean 20037) * <= 82,455 word ops
            (worst-case scan+insert: <=3 ops/probe * <=27,413 probes + 16) = 2254938570
PRG          2 coin draws * 264 word ops = 528
setup + fifth roots        = 2000 + 2286
offline derivation         = 2^38 word ops (Section 9; constants + budget solve +
            measurement campaign; charged, 418383420 compressions)
total ops                  = 90998982535628013519104874008592909947302
units = total / C, C = 657 = 138506822733071557867739534259654353040.03348554033485540334855403348554033485540
time_log2 = log2(units)     = 126.703225
filed                       = 126.70323 (rounded up at 5 decimals)
```

For reference against the frontier: this target's published entry f62fb39 (Jbenisek) is an algebraic collision algorithm filing time_log2 75.36046 with 53.54 bits of memory penalty (normalized cost 128.90); the organizer nominal reference `poseidon-orchard-r21-nominal-v2` is 127.0 (not a qualified baseline). This entry files 126.70323 with zero memory penalty: 2.1968 bits under the published normalized frontier at the same round count. The tight random-function convention at r=21 scores 126.62742; the 0.0758 bits over tight are the honest price of the detection-window/recovery convention plus the 0.90 tolerance floor (the incumbent's own generic entries at r=22 and r=24 file the tight n0 with no real-map transfer evidence; this entry pays for the transfer).

## 8. Memory

Peak live set: the dp table 27,413 entries * 32 bytes (877,216) + 27,413 side fields * 2 bytes (54,826) + one 32-byte start word = 932,074 bytes, plus one allowance of 116,444 bytes for every other live item (code, nonuniform constants, registers, PRG state, transient working state and I/O buffers) = 1,048,518 bytes < 2^20 = 1,048,576 (58 bytes margin). The reference implementation of Appendix B (~18 KB source plus ~6 KB of derived tables, standard library only) fits the allowance with wide margin; its whole working state besides the table, the start word and the message/output buffers is procedure locals. Every table item is one aligned 32-byte word: entry k at TAB0 + 32k holds (high 126 bits of the dp value) OR (its index < 2^128); the side word holds the 16-bit low part. Lookups extract the high part and compare, then the side field; reconstruction shifts the high part back and appends the side field (threshold < 2^16 makes this exact). The trail index is stored inside each 32-byte entry word and the recovery lookups scan the entry words directly, so no auxiliary ordered index list (nor any other structure beyond the counted items) is live: 1,048,518 bytes is the entire peak live set. Memory penalty max(0, log2(1,048,518) - 20) = 0; filed memory_log2_bytes = 20.

## 9. Preprocessing (inside time)

All constants (the line constants of Section 2; the scaled bases M3, M4, MB; GAMMA; MH0/MH1/MH2; the kappa-folded partial constants KAPPA0HAT and KAPPA_EXIT; the folded exit constants at round 60; C60..C63, B60..B62, B63R; LAMBDA) and the budget solve (80-digit Decimal bisections on n0 and n1) are offline. Their derivation, together with the participant's 15,900-walk H1 measurement campaign (the advice that fixes the 0.90 tolerance floor and the printed intervals; 130,319,779,492 charged walk steps at the r=21 step cost), is construction/preprocessing under orchard-field-ram-v2 and is bounded by 2^38 word operations (constant derivation: 64 rounds of short reciprocal/fifth-power chains, a few hundred word operations each; budget solve: a few hundred 80-digit Decimal exp/log evaluations < 2^10 each; campaign: 256,534,999 steps * 508 < 2^37), charged inside time_log2 in the ledger line "offline derivation" (2^38/657 = 418383420 compressions), and declared as preprocessing_log2 = 29 (= ceil(log2(418383420))). The measurement analysis of Section 6 is charged inside the same 2^24 cap.

## 10. Organizer experiment (declared)

`lowbits-birthday` (python-message-pairs-v1, digest-xor-mask on the first 14 bits): per trial, at most 1200 fresh canonical 64-byte messages derived deterministically from the supplied seed; the program returns a pair whose r=21 digests agree on the masked bits. Local run of the same event: 256/256 verified pairs, byte-identical on repeat. Every eighth trial the same program additionally runs one w=16 truncated first-repeat walk on the filed walk map (fresh (rho0, start) drawn from the same trial seed, 4096-step cap) and reports its length and cap flag as untrusted participant observations: 32 organizer-executed walks at width 16 under fresh organizer seeds, byte-reproducible (the runner replays the identical request twice and requires byte-identical output). These observations corroborate the width-16 cell of the participant campaign (Section 6) under organizer execution; the runner labels them untrusted (it verifies no internal semantics), they are a witness and not the estimate. The checked event is a reduced-width witness on the digest only; neither establishes H1, the cost bound, or the success probability (a 14-bit event cannot separate hazard multipliers near 0.5 from 1).

## 11. Verification

The step program, the search with its recovery, the budget solve, the measurement harness and the analysis sources are embedded verbatim as appendices below (A: `myrho_r21.py` - step program at R=21, line and tables, selftest; B: `attack_r21.py` - the filed single-trail search, recovery, exact plan, reduced-width end-to-end selftest, H1 measurement mode; C: `measure_rounds.py` + `analysis_round.py` - the r=21 H1 evidence and exact likelihood intervals). All are standard-library-only Python 3, deterministic given their seeds. Exercised locally: `myrho_r21.py --selftest` 64/64 against the trusted reference at r=21; `attack_r21.py --selftest` 64/64 plus the reduced-width end-to-end searches (any trial reaching the test gap cap is abandoned, per the lemma's gap term); `attack_r21.py --plan` prints the exact ledger of Section 7; the measurement and analysis of Section 6 ran to completion on the real r=21 map with the per-round seeds.

## Appendix A: `myrho_r21.py` (line, tables, step program at R=21, selftest)

Line construction and constants (identical to the r=23 filing; the line, the
bases and LAMBDA are round-independent), the counted `step()` program running
partial rounds 4..24, and `--selftest` (64 random (x, rho0) trials against
the trusted reference at R=21).

```python
#!/usr/bin/env python3
"""r=23 Orchard Poseidon generic birthday attack: distinguished-point trail rho.

Standard library only.  The step program counts every field operation it runs.

Offline conventions (all constants precomputed from the pinned deployed constants):
- Rounds 0..2: entry state and round-2 constants folded (t_k = QQ_k x + Ptilde_k);
  round 2 runs in scaled bases (linear layer 12 ops), leaving basis M3.
- Round 3: scaled-basis full round (24 ops), leaving basis M4.
- Rounds 4..26: partial rounds in the fixed basis m = (M01,M11,M21)*M4[1]
  (chosen so the lane-1 row coefficient is exactly 1 in rows 0 and 2), with the
  per-round constants kappa-folded: per round 17 ops.
- Rounds 60..62: scaled-basis full rounds (24 ops each), bases chained from m;
  the partial-phase exit constants are folded into round 60.
- Round 63: output lane only; all three S-box inputs powered; the walk scale
  LAMBDA is folded into the row so the lane-1 row coefficient is 1: 16 ops.
"""
import argparse
import json
import random
from pathlib import Path

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
CAP = 1 << 65
R = 21
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


# --------------------------- line construction (two-round bypass) -----------
CAPp = pow(CAP + C[0][2], 5, P)
A1c = (-((MDS[1][2] * CAPp + C[1][1]) % P)) % P
A2c = (-((MDS[2][2] * CAPp + C[1][2]) % P)) % P
_det = (MDS[1][0] * MDS[2][1] - MDS[1][1] * MDS[2][0]) % P
U0 = ((A1c * MDS[2][1] - A2c * MDS[1][1]) * inv(_det)) % P
V0 = ((MDS[1][0] * A2c - MDS[2][0] * A1c) * inv(_det)) % P
a_, b_ = MDS[0][1] % P, (-MDS[0][0]) % P
D1 = (MDS[1][0] * a_ + MDS[1][1] * b_) % P
D2 = (MDS[2][0] * a_ + MDS[2][1] * b_) % P
A0 = (MDS[0][0] * U0 + MDS[0][1] * V0 + MDS[0][2] * CAPp + C[1][0]) % P
QQ = tuple((MDS[j][1] * pow(D1, 5, P) + MDS[j][2] * pow(D2, 5, P)) % P for j in range(3))
PP = tuple((MDS[j][0] * pow(A0, 5, P)) % P for j in range(3))
D_EXP = pow(5, -1, P - 1)


def message(W):
    tau = pow(W, D_EXP, P)
    U = (U0 + a_ * tau) % P
    V = (V0 + b_ * tau) % P
    m0 = (pow(U, D_EXP, P) - C[0][0]) % P
    m1 = (pow(V, D_EXP, P) - C[0][1]) % P
    return m0, m1


# --------------------------- offline tables ----------------------------------
def full_round_tables(i, m):
    """Full round i in scaled bases: tau = sig + ctilde; y = tau^5;
    rho_j = B_j0 y0 + y1 + B_j2 y2.  Returns (ctilde, B, m')."""
    m5 = [pow(mk, 5, P) for mk in m]
    mp = [(MDS[j][1] * m5[1]) % P for j in range(3)]
    ctilde = [(C[i][k] * inv(m[k])) % P for k in range(3)]
    B = [[(MDS[j][0] * m5[0] * inv(mp[j])) % P, 1,
          (MDS[j][2] * m5[2] * inv(mp[j])) % P] for j in range(3)]
    return ctilde, B, mp


_C2, _B2, M3 = full_round_tables(2, (1, 1, 1))
_C3, _B3, M4 = full_round_tables(3, M3)

# partial-phase basis: m = (M01, M11, M21) * M4[1] (lane-1 coefficient 1 in
# partial-phase basis: m = (M01, M11, M21)*M4[1] with lane 1 kept in M4[1]
# (rows 0 and 2 have lane-1 coefficient exactly 1; row 1 has M11).
MB = ((MDS[0][1] * M4[1]) % P, M4[1], (MDS[2][1] * M4[1]) % P)
GAMMA = tuple((M4[k] * inv(MB[k])) % P for k in range(3))
MH0 = [(MDS[j][0] * pow(MB[0], 5, P) * inv(MB[j])) % P for j in range(3)]
MH1 = [(MDS[j][1] * MB[1] * inv(MB[j])) % P for j in range(3)]
MH2 = [(MDS[j][2] * MB[2] * inv(MB[j])) % P for j in range(3)]
assert GAMMA[1] == 1 and MH1[0] == 1 and MH1[2] == 1

# kappa-folded partial constants.  True state s_k = MB_k (sig_k + kappa_k(i)).
# Runtime per round: t0h = (sig_0 + kappa0hat_i)^5 ;
#   sig'_j = MH0_j t0h + MH1_j sig1 + MH2_j sig2   (kappa recursion zeroes
#   the constants), with kappa_j(i+1) = MH1_j kappa_1 + MH2_j kappa_2 + Khat_j,
#   kappa0hat_i = kappa_0(i) + c_i0/MB_0, Khat_j = (M_j1 c_i1 + M_j2 c_i2)/MB_j.
KAPPA0HAT = []
_kh = [0, 0, 0]
for _i in range(4, 4 + R):
    KAPPA0HAT.append((_kh[0] + C[_i][0] * inv(MB[0])) % P)
    _Kh = [((MDS[j][1] * C[_i][1] + MDS[j][2] * C[_i][2]) * inv(MB[j])) % P for j in range(3)]
    _kh = [(MH1[j] * _kh[1] + MH2[j] * _kh[2] + _Kh[j]) % P for j in range(3)]
KAPPA_EXIT = list(_kh)

# rounds 60..62: input basis chained from MB; exit constants folded at 60
C60, B60, M61 = full_round_tables(60, MB)
C60 = [(C60[k] + KAPPA_EXIT[k]) % P for k in range(3)]
C61, B61, M62 = full_round_tables(61, M61)
C62, B62, M63 = full_round_tables(62, M62)
LAMBDA = inv(MDS[0][1] * pow(M63[1], 5, P)) % P
C63 = [(C[63][k] * inv(M63[k])) % P for k in range(3)]
B63R = [(MDS[0][0] * pow(M63[0], 5, P) * LAMBDA) % P,
        1,
        (MDS[0][2] * pow(M63[2], 5, P) * LAMBDA) % P]


def walk_ptilde(rho0):
    PPp = tuple((PP[j] + rho0 * QQ[j]) % P for j in range(3))
    return tuple((PPp[j] + C[2][j]) % P for j in range(3))


# literal per-step budget: rounds 0..2 block (t-forming 6, three S-boxes 9,
# rescaled linear layer 12) = 27; round 3 and rounds 60..62: 24 each; entry
# rescale 2; partial rounds 17 each; round 63: 16; dp test + counter + state traffic 10 (mask 1, threshold compare 1, counter increment 1, branch compare 1, 3 lane loads, 3 lane stores).
OPS = {'block02': 27, 'full': 24, 'pentry': 2, 'partial': 17, 'r63': 16, 'dp': 10}
STEP_OPS = (OPS['block02'] + OPS['full'] + OPS['pentry'] + R * OPS['partial']
            + 3 * OPS['full'] + OPS['r63'] + OPS['dp'])


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


def step(x, ptilde, led):
    """One counted walk step: x -> digest(message(x + rho0)) * LAMBDA."""
    # rounds 0..2 (entry + round 2 folded; round 2 in scaled bases)
    t = [(QQ[k] * x + ptilde[k]) % P for k in range(3)]
    led.mult += 3; led.add += 3
    y = [_sbox(tk, led) for tk in t]
    sig = [(_B2[j][0] * y[0] + y[1] + _B2[j][2] * y[2]) % P for j in range(3)]
    led.mult += 6; led.add += 6
    # round 3 (scaled bases)
    tau = [(sig[k] + _C3[k]) % P for k in range(3)]; led.add += 3
    y = [_sbox(tk, led) for tk in tau]
    sig = [(_B3[j][0] * y[0] + y[1] + _B3[j][2] * y[2]) % P for j in range(3)]
    led.mult += 6; led.add += 6
    # enter the partial basis (lanes 0 and 2 rescale; lane 1 already there)
    sig = [sig[0] * GAMMA[0] % P, sig[1], sig[2] * GAMMA[2] % P]
    led.mult += 2
    # partial rounds 4..26 (lane-1 coefficient 1 in rows 0 and 2)
    for i in range(R):
        t0 = (sig[0] + KAPPA0HAT[i]) % P; led.add += 1
        t0h = _sbox(t0, led)
        sig = [(MH0[j] * t0h + (sig[1] if j != 1 else MH1[1] * sig[1])
                + MH2[j] * sig[2]) % P for j in range(3)]
        led.mult += 7; led.add += 6
    # rounds 60..62 (scaled bases, exit constants folded at 60)
    for cB, c in ((B60, C60), (B61, C61), (B62, C62)):
        tau = [(sig[k] + c[k]) % P for k in range(3)]; led.add += 3
        y = [_sbox(tk, led) for tk in tau]
        sig = [(cB[j][0] * y[0] + y[1] + cB[j][2] * y[2]) % P for j in range(3)]
        led.mult += 6; led.add += 6
    # round 63 (output lane, walk scale folded)
    tau = [(sig[k] + C63[k]) % P for k in range(3)]; led.add += 3
    y = [_sbox(tk, led) for tk in tau]
    out = (B63R[0] * y[0] + y[1] + B63R[2] * y[2]) % P
    led.mult += 2; led.add += 2
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
        ptilde = walk_ptilde(rho0)
        led.reset()
        got = step(x, ptilde, led)
        assert got == want, f'step mismatch at trial {n}'
    led.reset()
    step(0, walk_ptilde(1), led)
    print(f'selftest OK on {trials} random (x, rho0)')
    print(f'per-step ops: mult={led.mult} add={led.add} word={led.word:.2f} '
          f'total={led.mult + led.add + led.word:.2f} budget={STEP_OPS}')


if __name__ == '__main__':
    selftest()
```

## Appendix B: `attack_r21.py` (the filed search, recovery, exact plan, selftests)

`full_search` is the filed algorithm of Section 4 (one trail, distinguished
points, index table, gap-bounded lockstep recovery) with the filed literals
WALK/DETECT/GMAXC at R=21; `plan` derives and prints the exact ledger of
Section 7 (80-digit Decimal, per-round step cost 508 and
C = 657); `--selftest` runs the 64-trial step check and the
reduced-width end-to-end searches of Section 4 at R=21.

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
- dp test + loop control + state traffic: 10 word ops per step (2 dp: mask + threshold compare; 2 control: increment + branch compare; 6 state: 3 loads + 3 stores); table work charged per
  distinguished event.
"""
import argparse
import hashlib
import json
import math
import random
from decimal import Decimal, getcontext
from pathlib import Path

import myrho_r21
from myrho_r21 import (P, ref_digest, message, step, Ledger, walk_ptilde,
                   LAMBDA)

getcontext().prec = 80
GMAXC = 176060377939026895457446518306020702   # ceil(19.75/theta_lo) + 2 (plan)
DETECT = 82458658022075887745892673130667924    # detection window d (plan)
WALK = 178597435891429200878561991096629710601  # filed trail budget S1 = n1 + d (plan)
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
    distinguished points is at most gmax.  The two recovery index lookups
    (s and r) are single scans of the packed entry words (the trail index
    is inside each entry word), charged at the scan cap each.  `walk` is the trail-step budget
    (filed value derived by plan; tests use reduced values).
    """
    led = led or Counters()
    ptilde = walk_ptilde(rho0)
    table = {}                      # dp key -> trail index (packed entry word)
    x = x0
    t = 0
    while walk is None or t < walk:
        t += 1
        s = Ledger()
        x = step(x, ptilde, s)
        led.charge_step(s)
        if (x & dpmask) < dval:
            led.events += 1
            led.charge(224)         # probe + insert word work per event
            key = dp_key(x)
            if key in table:
                a = table[key]
                L = t - a
                # one scan of the entry words finds the largest stored
                # index below a (the trail index is inside each packed
                # entry word; there is no auxiliary ordered index list)
                s_idx = max((v for v in table.values() if v < a), default=0)
                xs = x0 if s_idx == 0 else reconstruct(table, s_idx)
                q = s_idx + L
                r = max((v for v in table.values() if v <= q), default=0)
                led.charge(2 * (3 * 27413 + 16))       # the two recovery scans, cap charge
                if q - r > gmax:
                    return None, led   # capped positioning (lemma eps)
                u = x0 if r == 0 else reconstruct(table, r)
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
    form (H1, proof.md Section 6) scales the repeat term by c: at c = 0.90
    (the tolerance floor, below every measured 95% lower bound) the same
    solve gives the filed budget n1; the random function (c = 1) needs only
    n0 < n1.
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

    step_ops = Decimal('508')
    rec_evals = 3 * (gmax + 16)                # recovery cap: 3 gmax charged
    rec_ops = (Decimal(rec_evals) * (step_ops + 6)
               + Decimal(2 * (3 * 27413 + 16)))    # + the two recovery scans
    dp_events = int((Decimal(S1) * theta_hi).to_integral_value(
        rounding='ROUND_CEILING'))
    table_events = 27413 + 1                  # deterministic: first repeat ends the walk
    table_per_event = 3 * 27413 + 16           # worst-case scan+insert, packed layout
    table_ops = Decimal(table_events) * Decimal(table_per_event)
    prg_ops = Decimal(2 * 264)                 # two coin draws
    setup = Decimal(2000)
    roots = Decimal(2286)                     # fifth roots for both messages
    prep = Decimal(1 << 38)                  # constants + budget solve + measurement campaign
    total = (Decimal(S1) * step_ops + rec_ops + table_ops + prg_ops + setup
             + roots + prep)
    units = total / Decimal(657)
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
        'per_step_ops': '508',
        'walk_ops': str(Decimal(S1) * step_ops),
        'recovery_ops': str(rec_ops),
        'table_ops': str(table_ops), 'prg_ops': str(prg_ops),
        'dp_events': dp_events,
        'total_ops': str(total), 'C': 657,
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
    print(f'step selftest: {trials}/{trials} equal to reference*LAMBDA, '
          f'per-step={led.mult + led.add + led.word:.2f} (budget 508)')
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

        table = {}
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
                    # one scan finds the largest stored index below a (the
                    # trail index is inside each entry word; no index list)
                    s_idx = max((v for v in table.values() if v < a), default=0)
                    q = s_idx + L
                    r = max((v for v in table.values() if v <= q), default=0)
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
        myrho_r21.selftest()
```

## Appendix C: `measure_rounds.py`, `analysis.py` and `analysis_round.py` (H1 evidence)

`measure_rounds.py` runs the per-round measurement suite of Section 6: first-repeat
walks on the real r=21 map truncated to w bits (widths 16..36, fresh
(rho, start) per walk, 12 parallel chunks, per-chunk seeds). `analysis.py` holds
the exact discrete first-repeat likelihood (series-summed with bounded tail) and
the per-width and pooled profile-likelihood intervals; `analysis_round.py`
applies them to `measurements2_r21.json` and writes `analysis_r21.json`.

```python
#!/usr/bin/env python3
"""Per-round H1 measurements: first-repeat walks on truncated r-round maps.

Runs the v5 suite (same JOBS walk counts, widths 16..36, fresh
(rho, start) per walk, 8 parallel chunks) for each round r in 15..22,
against the per-round modules myrho_r{r} (generated from myrho.py with
R replaced). Writes measurements2_r{r}.json (same format as
measurements2.json: {str(w): sorted first-repeat lengths}).

Rounds run sequentially; within a round the 8 chunks run in parallel.
"""
import importlib
import json
import multiprocessing as mp
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NCHUNK = 12
JOBS = {16: 1200, 20: 6000, 24: 6000, 28: 1200, 32: 1200, 36: 300}


def worker(args):
    r, w, walks, seed = args
    mod = importlib.import_module(f'myrho_r{r}')
    rng = random.Random(seed)
    mask = (1 << w) - 1
    out = []
    for _ in range(walks):
        rho0 = rng.randrange(0, 1 << 254)
        v = rng.randrange(0, 1 << w)
        ptilde = mod.walk_ptilde(rho0)
        seen = {v}   # every iterate lands in seen; the loop exits at the FIRST repeat
        i = 0
        led = mod.Ledger()
        while True:
            v = mod.step(v, ptilde, led) & mask
            i += 1
            if v in seen:
                out.append(i)
                break
            seen.add(v)
    return w, out


def main():
    sys.path.insert(0, str(HERE))
    rounds = [int(a) for a in sys.argv[1:]] or list(range(15, 23))
    for r in rounds:
        t0 = time.time()
        jobs = []
        for w, total in sorted(JOBS.items()):
            walks, extra = divmod(total, NCHUNK)
            for chunk in range(NCHUNK):
                n = walks + (1 if chunk < extra else 0)
                if n:
                    jobs.append((r, w, n, 0x5EED0000 + w * 100 + chunk))
        with mp.Pool(NCHUNK) as pool:
            results = pool.map(worker, jobs)
        data = {}
        for w, lens in results:
            data.setdefault(w, []).extend(lens)
        out = {str(w): sorted(v) for w, v in data.items()}
        (HERE / f'measurements2_r{r}.json').write_text(json.dumps(out))
        print(f'r={r} done in {time.time()-t0:.0f}s: '
              + ', '.join(f'{w}:{len(v)}' for w, v in sorted(out.items())),
              flush=True)


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

```python
#!/usr/bin/env python3
"""Per-round H1 analysis: run the exact analysis on one measurements file.

Usage: analysis_round.py <r>
Reads measurements2_r{r}.json (the per-round measure2-style suite),
writes analysis_r{r}.json. Same estimators as analysis.py (exact discrete
first-repeat likelihood, profile-likelihood 95% intervals, pooled
multiplier); single input file per round.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analysis import loglik, mle, interval, CHI2  # noqa: E402


def main():
    r = int(sys.argv[1])
    data = {}
    src = HERE / f'measurements2_r{r}.json'
    for k, v in json.loads(src.read_text()).items():
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
        print(f'r={r} width {w}: mhat={mh:.4f} 95% CI [{lo:.4f}, {hi:.4f}] '
              f'(n={len(lens)}, tail {bound:.2e})')

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
    print(f'r={r} pooled: mhat={best:.4f} 95% CI [{lo:.4f}, {hi:.4f}]')
    report['pooled'] = dict(mhat=round(best, 4), lo=round(lo, 4),
                            hi=round(hi, 4))
    (HERE / f'analysis_r{r}.json').write_text(json.dumps(report, indent=1))
    print(f'wrote analysis_r{r}.json')


if __name__ == '__main__':
    main()
```

## Appendix D: raw first-repeat data (r=21, participant-run, deterministic seeds)

Per walk: the exact step count of the first repeat on the real r=21 map truncated to w bits (fresh (rho, start) per walk, seeded PRNG, seeds fixed in Appendix C `measure_rounds.py`: 0x5EED0000 + w*100 + chunk over 12 chunks). The multiset below is the complete raw data; the likelihood of Appendix C consumes exactly this multiset. Total 15900 walks, 256,534,999 walk steps, 130,319,779,492 charged word operations (inside the 2^38 offline line of Section 9). `python3 measure_rounds.py 21` regenerates `measurements2_r21.json` byte-identically.

``
width 16 (1200 walks, sum 379712):
11 12 14 17 22x2 23x2 30 33 35 36x2 39 42 43x2 45x4 47x2 50 51x2 56x2 57x3 58 60x2 61x2 62 65x2 68 70x3 73x2 74 75 76 79x3 82 83 84 85x3 86x3 88 89 90x3 91x3 92x2 94x3 95x3 96 97 99x2 101x2 102 103 105x3 107x4 108x3 109x2 111 112x4 113x3 115x3 116 117x2 118 120x2 121 122x3 123 124x2 125x3 126 127 128 129x4 131 132x3 133x5 135x2 136 138x2 139x3 140x3 141x2 142x5 144x3 145x3 146 147x2 148x2 149x3 150x5 151x2 152x3 153x2 154x2 155x3 156x3 157x5 158 159x2 160 161x3 162x2 163x5 164x2 165x2 166 167 168 169x2 170x2 171x3 172x2 173x2 174x3 175x4 177x3 178x4 179x2 180x4 181 182x2 183x3 184x4 185 186x2 188 189x3 190x2 191x4 192x5 193x6 194x3 196x2 197x2 198x3 199x7 200x3 201x7 202x3 203x3 204x5 205x2 206 207x4 208 209x5 210 211x3 212x7 213x6 214x5 215x5 216x2 217x6 218x3 219x2 220x4 221x3 222x3 223 224x4 225x2 226x4 227x2 230 231x7 232 233x3 234x4 235x3 236 237x2 238x3 239x3 240x4 241x4 242x6 243x3 244x2 245 246x4 247x3 248x4 249 250x3 251x7 253 254x2 255x2 256x6 257x3 258x6 259x4 260x4 261x2 262x2 263x4 264x6 265x4 266x2 267x3 268x2 270x2 271x2 273x5 274x6 275x4 276x3 277 278x2 279x3 280x4 281 282x3 283x4 284x3 285x2 286x6 287x2 288x6 289 290x3 291x2 292x5 293 294x2 295 296x2 298x3 299x5 300x2 302x5 303x3 304x3 305x6 306x3 307 308x3 309x2 310x2 311x4 312x4 313x6 314x4 315x3 316x6 317x3 318x4 319x2 320x2 321 322 323x3 325x2 326x2 327x2 328 329x2 330 331x4 332 333x2 334 335x4 336 337x2 338x4 339x5 340x4 341 342x5 343 344 345x4 346x2 347x5 348 349 350x3 351x4 352x2 353x5 354 355x4 356x2 357x3 358x4 359x3 361x5 362 363x4 364x4 365x2 366x2 367 368x3 369x4 370x5 372x3 373 375 376x5 377x3 378x3 379x5 380x3 381x6 382x2 383x3 384x3 385x4 386 387 388x3 389x3 390x2 391x5 392 393x2 394x2 395x2 396x2 397x2 398x3 400 401 402x2 403x2 405x3 406x2 407 408x2 409x3 410x4 411 412x3 414x3 415x2 416x3 418x3 419 420x2 421x4 422x2 423x2 424 425x3 427x4 429x5 430x2 431x3 432 434x2 435 437x3 438x5 440x2 441 443 444 445x2 447x4 449x2 450x3 451 452x2 453 454x3 455 456 457x2 458 459 462 463x2 464x2 465x6 466x2 467x7 468x3 469 471 472x4 473x2 474x2 477 479 480 481 482x2 483x3 484x4 485x3 486x2 487 488 489x3 491x3 492x2 493x2 494x3 495 496x2 498 499x2 500 502 503x2 504x2 506 507x2 508 509 510x2 511 512x2 513 514x4 515x2 516x2 517 519 524 525x2 526x3 527 531 532 533 534 536 537 538x2 539x3 543 544x2 547x3 549 550x2 551 552 555 558 560x4 566 567 568 569 575x2 577 580x2 582 583 584 585 588 589 591x2 594x3 595 598 599x3 601 602 603x2 607x2 608x2 610 616 617 620x2 621 622 623x2 624 625 628 639 644 645 646x3 652 655 657 661x2 663 668 671 672 676 678 684 689x2 692 695 699x2 700 706 711 716 724 730 744 747 748 750 753 756 757 769 773 776 778 779 794 815 819 825 886
``

``
width 20 (6000 walks, sum 7664193):
17 24 30 36 44 52x3 53 57 58 59 60x2 61x3 64 67x2 69 70 72 73 74 77 82 86 88 97 98 103x2 104x2 107 108 109 111x2 112x2 113 117 118 123 126 128 129x2 131 133 135 136 139x2 140 141x3 145x2 146 147x2 148x2 149x3 150x2 151 152x2 153 156 159 162x2 163x2 164x3 167 168 169x2 171x4 172 174x3 176 180 181 182 183x2 185 186 188 190x2 191 194x2 195x3 196x2 200 201x2 203 204x2 205 207x6 208x3 209 214x2 215x2 216 217 218 220x2 221x3 222 224x2 226x2 227 228x3 231x2 232 235 236 240 243 244 245x3 246x2 247 248x3 249x2 250 251 253 254x3 255x2 257x2 258x3 259x2 262x2 263x2 265 267x2 268x3 269 270x2 271x2 273x2 274x3 275x2 277 278x4 279x2 281x4 283x2 284x3 285 286x2 287x2 288 289x4 290x2 291x3 292x4 294x3 295x3 296 297x2 298x3 300x3 301 302 303x2 304x2 305 306 307 310x3 311x2 312 313 314x5 317x2 318 321 322x5 323 324 325x3 326x5 327 328 329x5 330 331x4 333x2 334x2 335 336 338 339 340x2 342x2 343 344x2 345 346 347 348x4 349 350x4 351x2 353x7 354x5 355x4 356x2 357x3 358x3 359 360x3 361x7 362x2 363 364x4 365x3 366 367x2 368x2 369x5 370x3 371x3 372x2 373x2 374x2 376x2 377x2 378x2 379 380 381x3 382x4 383x2 384x6 385x5 386x3 387 388x6 389 390 391x2 393x2 394x3 395 396 397 398x2 399 400x2 401x2 403 404 405x5 406x5 407 408 409x2 410x4 411x2 412x2 413x4 414x3 415x3 417x4 418x2 419x3 420 421x4 422x2 423x2 425x4 426x3 427x2 428x4 430 431x2 432x2 433x3 434 435x4 436x2 437x2 440x5 442 443x2 444x3 445 446x5 447x2 448x4 449 450x2 451x3 452x3 453x2 454 455x3 457x3 458 459x3 460x4 462x4 464x6 465 466x2 467x5 468 469x5 470 471x3 472 473x3 474x2 475x4 476 477 478x4 479x4 480x3 481x4 482 483x4 485x2 486x2 487x4 488x5 489x2 490x4 491x3 492x3 493 494x6 495x6 496x2 497x3 498x3 499x2 500x3 501x2 502x2 503x3 504 506x5 507 508 509x3 510x6 511 512x3 513x4 514 515x2 516x6 517x3 518x2 519x3 520x2 521x5 524x4 525x4 526x4 527x3 528x3 529x6 530x3 531 532 533x4 534x5 535x2 536 537x2 538 539x4 540x2 541x3 542 543x5 545x3 546x2 547 548x4 549x2 550 552 553x3 554x3 555x3 556x2 557x5 558 560x4 561x2 562x6 563x6 564x2 565 566x4 567x5 568 569x2 570 571x4 572x2 573x3 574 575 576x2 577x3 578 579x4 580x7 581x2 582x5 583x5 584x3 585x4 586x7 587x3 588x3 589x3 590x4 591x2 593 594x5 595x5 596x5 597x3 598x3 599x4 600 601 602x2 603x2 604x5 605x3 606x4 607x3 608x5 609x3 610x5 611x2 612x2 613x3 615x2 616x3 617 618x2 619x2 620x4 621 622x3 623x3 624x2 625x3 626x4 627x3 628x3 629x2 630 631x4 632x3 633x2 634x4 635x4 636x5 637x6 638x3 639x5 640x5 641x4 642x3 643x4 644 645x4 646x2 647x3 648x2 649x4 650x4 651x3 652x2 653 654x2 655x7 656x2 657x2 658 659x2 660x8 661x5 662x2 663x4 664x2 665 666x3 667 668x4 669x5 670x3 671x4 672x5 673x3 674x4 675x2 676x5 677x2 678x5 679x2 680x4 681x5 682x9 683 684 685x5 686x3 687x5 688x4 689x2 690x2 691x4 692x2 693x3 695 696x3 697x5 698x2 699x2 700x3 701x2 702x8 703x3 704x3 705x3 706x3 707x4 708x6 709x8 710x4 711x5 712x4 713x3 714x7 715 716x3 717x5 718 719x4 720x3 721x4 722x3 723x3 724x3 725x3 726x2 728x4 729x3 730 731x6 732x4 733x2 734x5 735x5 736x3 737 738x6 739x4 741 742 743x5 744x3 745x2 746x3 747 748x7 749x2 750x3 751x2 752x2 753x3 754 755x3 756x2 757x5 758x3 759x4 760 761x4 764x3 765x3 766x2 767x2 768x2 769x2 770x3 771x4 772x2 773x2 774x3 775x4 776 777x5 778x2 779x4 780x5 781x5 782x6 783x3 784x2 785x2 786x3 787x4 788x2 789 790x2 791x2 792x4 793x4 794x2 795x4 796x5 797 798x6 799x3 800x4 801x2 802 803 804x4 805x3 806x2 807x2 808x3 809x6 811x2 812x4 813x2 814x3 815x3 816x4 817x3 818x3 819x3 820x5 821x3 822x2 823x3 824x3 825 826x4 827x2 828 829x6 830x4 831x3 832x4 833x4 834x5 835x2 836x3 837x2 838x2 839x2 840x4 841x3 842x2 843x4 844x2 845x3 846 847x4 848x2 849x2 850x7 851x4 852x3 853x6 854x2 855x5 856x2 858x4 859x2 860x4 861x4 862x4 863x7 864x4 865x3 866x3 867x8 868x2 869x5 870 871x4 872x3 874x4 875x2 876x3 877x2 878 879x6 881 882x3 883x5 884x2 885x2 886x5 887x4 888x3 889x3 890x2 891x3 892x5 893 894 895 896x2 897x4 898x3 900x3 901 902x3 903x5 904x6 905x7 906x2 907x5 908x3 909x4 910x2 911x4 912x4 913x3 914x4 915x3 916 917x4 918x2 919x3 920x4 921x4 922x3 923x2 924x4 925 926x2 927x3 928x4 929x3 930x2 931x4 932x3 933x3 934x5 935 936x2 937x3 938x3 939x2 940x2 941x3 942x4 943x3 944x7 945x3 946x5 947x2 948x6 949x6 950x5 951x5 952x6 953x3 954x4 955x5 956 957x4 958x8 959 960x8 961x5 962x3 963 964 965x3 966x3 967 968x3 969x2 970x4 971x2 972x4 973x4 974x6 975x2 976x4 977x4 978x2 979x2 980x8 981x4 982x3 983x5 984x4 985x5 986x6 987x2 988x4 989x2 990 991x6 992x4 993x3 994x4 995x4 996 997x3 998x5 999x3 1000x3 1001x5 1002x3 1003x2 1004x5 1005x2 1006x4 1007x5 1008x5 1009x3 1010x2 1011 1012x9 1013 1014x3 1016x4 1017x6 1018x9 1019x7 1020x8 1021x3 1022x2 1023 1024x3 1025x5 1026x9 1027x6 1028 1029 1030x3 1031x2 1032x4 1033x3 1034x2 1035x5 1036x4 1037x4 1038x6 1039x6 1040x2 1041x3 1042x2 1043x7 1044x5 1045x4 1046x5 1047x5 1048x3 1049x2 1050x5 1051x5 1052x5 1053 1054x3 1055x3 1056x2 1057x3 1058x4 1059x2 1060x2 1062x6 1063x4 1064x8 1065x4 1066x7 1067x3 1068 1069x2 1070x2 1071x4 1072x5 1073x5 1074x3 1075x4 1076x2 1077x3 1078x2 1079x5 1080x3 1081x2 1082x4 1083x5 1084x3 1085x6 1086x2 1087x4 1088x5 1089x6 1090x4 1091x2 1092x2 1093x2 1094x6 1095 1096x2 1097x3 1098x2 1099x4 1100x2 1101x4 1102x4 1103x6 1104x3 1105x4 1106x5 1107x4 1108x5 1109x4 1110 1111x6 1112x6 1113x4 1114x3 1115x7 1116x6 1117x5 1118x4 1119x2 1120x8 1121x4 1122x4 1123x4 1124x5 1125x5 1126x3 1127x3 1128x3 1129x9 1130x5 1131x4 1132x5 1133x6 1134x3 1135x2 1136x2 1137x3 1138x2 1139x4 1140x4 1141x2 1142x3 1143x3 1144x2 1145x6 1146x3 1147x4 1148x4 1149 1150x4 1151 1152x2 1153x4 1154x3 1155x2 1156x2 1157x3 1158x3 1159x4 1160x4 1161x4 1162x2 1163x2 1164x4 1165x3 1166x3 1167x3 1168x4 1169x2 1170x2 1171x7 1172x5 1173x4 1174x2 1175x2 1176x2 1177x6 1178x4 1179x2 1180x4 1181x3 1182x7 1183 1184x2 1185x5 1186x2 1187x4 1188x3 1189x5 1190 1191x6 1192x7 1193x5 1194x2 1195x5 1196x6 1197x7 1198x4 1199x2 1200x4 1201x2 1202x4 1203x2 1204x3 1205x4 1206x4 1207x3 1208x2 1209x3 1210x2 1211x4 1212x2 1213x2 1214x6 1215x3 1216x7 1217x2 1218x5 1219x5 1220x2 1221x4 1222x4 1223x6 1224x7 1225x4 1226x4 1229x2 1230x2 1231x3 1232x2 1233x4 1234x4 1235x4 1236x3 1237x4 1238x4 1239x4 1240x3 1241x3 1242x6 1243x2 1244x4 1245x7 1246x8 1247x3 1248x3 1249x5 1250x3 1251x4 1252x2 1253x3 1254x3 1255x5 1256x2 1257x3 1258x6 1259 1260x4 1261x6 1262x5 1263x2 1264x7 1265x7 1266x2 1267 1268x6 1269 1270x6 1271x4 1272x8 1273x5 1274 1275x2 1276 1277x5 1278x4 1279x4 1280x3 1281x6 1282x5 1283x2 1284x6 1285x5 1286x3 1287 1288x3 1289x2 1290x2 1292x3 1293x6 1294x2 1295x2 1296x3 1297 1298x3 1299x3 1300x2 1301x3 1302x2 1303x2 1304x4 1305x4 1306x3 1307x3 1308x2 1309x3 1310x3 1311x4 1312x4 1313x2 1314x2 1315x3 1316x2 1317x4 1318x5 1319 1320x4 1321x2 1322x6 1323x3 1324 1325x4 1326x5 1327x5 1328x5 1329x4 1330 1332x6 1333x4 1334x4 1335x6 1336x3 1337x6 1338x4 1339x4 1340x4 1341x4 1342x2 1343x3 1344x5 1345x3 1346x5 1347x6 1348x3 1349x5 1350x2 1351x3 1352x2 1353x3 1354x2 1355x3 1356x3 1357 1358x5 1359 1360x4 1361x4 1362x3 1363x5 1364 1365x6 1366x4 1367x3 1368x2 1370x4 1371 1372x2 1373x2 1374 1376x3 1377x2 1378 1379x3 1380x2 1381x7 1382x2 1383x3 1384x5 1385x2 1386x3 1387x6 1388x3 1389x6 1390x4 1391x4 1392x3 1393x4 1394x2 1395x3 1396x5 1397x4 1398x5 1399 1400x6 1401x2 1402x3 1403x2 1404x4 1405 1406 1407x7 1408x2 1409x7 1410x3 1411x7 1412x8 1413x3 1414x3 1415x4 1416x3 1417x3 1418x4 1419x2 1420x2 1421 1422x2 1423 1424x2 1425x2 1426x4 1427x6 1428x2 1429x2 1430x2 1431x3 1432x3 1433 1434x4 1435x2 1436x5 1437x3 1438x3 1439x4 1440x6 1441x2 1442x3 1443 1444x2 1445x4 1446x3 1447x4 1448x6 1449x4 1450x2 1451x3 1452x3 1453x3 1454x2 1455x3 1457x4 1458 1459x3 1461x4 1462x4 1463 1464 1465 1466 1467x2 1468x8 1469x2 1470x3 1471x2 1472x5 1473x3 1474x4 1475x5 1476x2 1477x2 1478 1479x2 1480x3 1481x2 1482x2 1483x5 1484x4 1485 1486x2 1488x5 1489 1491x5 1492 1493x5 1494x2 1495 1496x6 1497x4 1498x9 1499x4 1500x6 1501x7 1502x2 1503x3 1505 1506x4 1507 1508x3 1509x2 1510x3 1511 1512x5 1513x3 1515 1516x3 1517x4 1518x2 1519 1521x2 1522x6 1523 1524x4 1526x4 1527x4 1528x5 1529 1530x5 1531x4 1532x4 1533 1534x4 1535x4 1536x2 1537x5 1538x3 1539x2 1540 1541x2 1542x3 1543 1544 1545x3 1546x3 1547 1549x2 1550x2 1551x2 1552x6 1553 1554x5 1555x3 1556x4 1557 1558x2 1559 1560x3 1561x5 1562 1563x2 1564x3 1565 1566 1567x2 1568x3 1569x5 1570 1571 1572x2 1573x2 1574 1575x3 1576x5 1577 1578x2 1579x2 1580x2 1581x2 1582x4 1583x2 1584x7 1585x2 1586x3 1587 1588 1589x7 1590x5 1591 1592 1593 1594x2 1595x2 1596x2 1597x3 1598x5 1599 1600x2 1601x3 1602x3 1603 1605x3 1607x6 1608 1609x3 1610x2 1611x2 1612x2 1613x2 1614 1616x2 1617x5 1618x2 1619x4 1620x3 1621 1623x2 1624 1625x2 1627x6 1628x5 1629 1630x4 1631x4 1632x4 1634x2 1635x2 1636x4 1637x2 1638 1639x4 1640x4 1641x2 1642x3 1643x3 1644x4 1645 1646x3 1648 1649x5 1650x2 1651 1652x2 1653 1654x5 1655x2 1656x3 1657x5 1658x5 1659x4 1660 1661x3 1662 1663x5 1664x4 1665x3 1666x2 1667 1668x4 1669 1670 1671x2 1672x3 1673x4 1674x3 1676x4 1677x4 1678x3 1680x4 1681x2 1682x5 1683 1684x3 1685x2 1686x2 1687x2 1688x2 1689x3 1690x5 1691x4 1692x2 1693x3 1694x5 1695x4 1696x7 1698x3 1699x2 1700x4 1701x3 1702x4 1703 1704x2 1705x2 1707x2 1708x2 1709x5 1710x3 1711 1712x5 1713x4 1714x2 1715 1716 1717x4 1718x4 1719x2 1720x5 1721x2 1722x3 1723x4 1724x2 1725x4 1726x5 1727x3 1728x2 1729x2 1730 1731x2 1732x2 1733x3 1734x2 1735x4 1736x3 1737x4 1738x2 1739x2 1740x4 1741x6 1742x2 1743x3 1744x3 1745 1747x2 1748x2 1749x3 1750 1751x2 1752x5 1753x3 1754x4 1756 1757x5 1759x2 1760 1761x2 1762 1763x2 1764x3 1766x2 1767x4 1768x5 1769x2 1770x2 1771x2 1772x2 1774 1776x2 1777x4 1778x2 1779x2 1780x3 1781 1782x5 1783x2 1784x3 1786 1787x2 1788x2 1789x5 1790x2 1793x3 1794x2 1795x3 1796x5 1797 1798x3 1799x6 1800 1801x2 1802x3 1804 1806 1807 1808x3 1809x2 1810 1811x2 1812x2 1813x3 1814x4 1815x4 1816 1817x2 1818 1820 1821x2 1822 1824x7 1825 1826x5 1827 1828 1830x4 1831 1832 1833x3 1834x3 1835x3 1836x2 1837 1838x4 1839x4 1840 1841 1842x8 1843x3 1844x2 1846x4 1847 1848 1849 1850x2 1851x2 1852 1854x8 1855x2 1856 1857x4 1858x3 1859x3 1860x2 1861x4 1863x2 1864x2 1865 1866 1867 1868x4 1869 1871x6 1872 1873x3 1874x3 1875x2 1877x3 1878x2 1880x3 1881x4 1882x5 1883x2 1884x3 1885x2 1887 1888x5 1889x4 1890x4 1891x2 1892 1893x3 1894 1895 1896x2 1897x3 1898x3 1899x4 1900x2 1901x3 1902x2 1903x3 1904 1906 1907x2 1908x3 1909 1913x2 1914x2 1915x2 1917x3 1918 1919x2 1920 1921x3 1922x2 1923 1924x2 1925 1926x2 1928x2 1929x4 1930 1932 1933x4 1934 1935 1936x2 1937 1939x4 1940x2 1941x3 1942x3 1943x4 1944x3 1945x2 1947x3 1948x3 1949x2 1950 1951x3 1952 1953x4 1954x2 1955x3 1956x3 1957 1959x3 1961 1962x3 1965x4 1966x3 1967x2 1968 1969x2 1970x4 1971 1972x2 1973 1974 1975x3 1976x2 1977x2 1978x2 1979 1980 1981 1982x2 1983 1984 1985x2 1986 1988x2 1989x2 1990x4 1991x2 1992x3 1993x2 1994 1995 1996 1997x3 1998x3 1999 2000x2 2002x6 2003x2 2004 2005 2006x2 2008x3 2009x3 2010x2 2011 2012 2014 2016x2 2018 2019 2020x3 2021 2023x2 2024x3 2027x4 2028 2029 2032x3 2033 2034x2 2035 2036 2037x2 2039x3 2040x2 2041 2042x2 2043 2044 2047x5 2048x5 2049x3 2050x2 2051 2052x3 2053x3 2054x3 2055x3 2056x2 2057 2058 2059 2061x3 2062x4 2063x2 2066 2068 2069x4 2070x3 2072x5 2073x4 2074x2 2075 2076x4 2077 2078 2082x4 2083 2084 2085 2086x2 2087x3 2088x3 2089x2 2090x2 2091 2092 2093 2095x2 2096x2 2097x3 2098 2101x2 2103x2 2106x3 2108x3 2109 2110 2111x2 2112 2115 2116x2 2118x2 2119x2 2120 2121 2124x3 2125x3 2126x3 2127 2128 2130x2 2131 2132x3 2134 2136x2 2137 2139x2 2140x2 2141x2 2142x3 2143x2 2144 2145 2146 2148x2 2149 2151x3 2152x2 2153x4 2155x2 2156x3 2157 2159x2 2160x3 2161x2 2162x2 2163x2 2166 2173x3 2174 2175x2 2176x2 2177x3 2179 2182x3 2183 2184 2185 2186 2187x2 2189x3 2190 2192x3 2193 2194x2 2195 2196 2198 2199x2 2201x2 2202 2203 2204 2206 2207x2 2210 2212 2213x2 2214 2215 2216x2 2217x3 2218 2220 2221x2 2223x2 2224x3 2225 2227x2 2228 2229x3 2230x2 2232 2235x3 2236x3 2237 2238x3 2239 2240 2241 2242 2243x2 2245x2 2246 2247 2248x2 2249x2 2251x3 2253x2 2255 2256 2257x3 2258 2260x2 2264 2267x2 2269x2 2272x3 2275 2276 2277 2279 2281 2282 2283 2284x2 2286 2287x2 2290x2 2294x2 2295 2297x2 2300 2301 2302 2303 2304 2305 2309 2311 2312x2 2314 2317x3 2318x2 2319 2320 2323 2325 2327x2 2328x2 2329 2330 2335 2336x2 2338 2339 2341 2342 2343 2344x2 2348 2352x2 2353x2 2354 2355x2 2356 2358 2359 2361x2 2362 2363x4 2364 2367x3 2369 2372 2373 2374 2376 2377 2378 2381 2382 2383x2 2384x2 2385 2387 2390x2 2393x2 2394x2 2396x2 2397 2398x2 2399 2400x2 2401x2 2402 2403 2404 2406x2 2408 2409x2 2412x2 2413 2415x2 2416 2419 2420 2421x3 2424 2425x2 2426 2428x3 2430 2431 2432x2 2435 2436x2 2438x2 2439 2440x3 2441x2 2442 2443x2 2444 2448 2449x3 2452x2 2456x2 2458 2460 2461 2465 2466 2467 2468 2469x2 2471 2472 2475 2476x2 2477 2479 2482x2 2484 2485 2487x2 2491 2492x2 2498 2502x2 2503 2505x2 2507 2508 2513 2514 2516 2519 2521x2 2523 2524 2525x2 2526 2528 2529 2530x2 2531 2532x3 2533x2 2535 2536 2538x2 2540 2542 2543 2544 2546x2 2554x3 2557x2 2561x2 2563 2566 2567 2570 2571x3 2574 2575 2577 2579 2580 2581 2583 2584x2 2586 2587 2588 2590 2593 2596 2598 2600x2 2602 2604x2 2607 2609 2615 2618 2620 2622x2 2627 2629x2 2630 2633 2637x4 2644 2645x2 2648 2649 2650 2651 2657 2666 2667 2669 2670 2671 2678 2679 2681 2682 2685 2688 2690 2691 2692 2694x2 2697x2 2698 2701 2708x2 2710 2712 2713 2716 2718 2719 2721x2 2731 2736 2737 2741 2745 2746 2747x2 2748x2 2751 2752 2754 2755x2 2756 2759 2762 2764 2765 2769 2775 2779 2782 2783 2784 2786 2791 2795 2798 2804 2806 2811 2812 2816 2817 2820 2821x2 2822 2823 2824 2825x2 2833 2834 2835x2 2837x3 2838x3 2843x2 2847x2 2848 2852 2855 2863 2866 2867 2871x2 2874x2 2875x2 2882 2888 2889 2891 2901 2904 2917x2 2918 2930 2931 2934 2935 2937 2940 2944 2951 2955 2956x2 2959 2961 2964 2969 2970 2974x2 2976x2 2991 2992 3000x2 3002x2 3006 3009 3013 3015 3030 3034 3036 3038 3046 3051 3055 3069 3072x2 3077 3081 3087x2 3093 3094 3103 3108 3124 3125 3137 3139 3142 3154 3163 3170 3171 3174 3180 3183 3193 3243 3245 3251 3269x2 3290 3291 3293 3332 3380x2 3411 3428 3430 3477 3482 3487 3495 3497 3499 3512 3518x2 3520 3522 3540 3547 3552 3592 3623 3636 3641 3701 3785 3827 3844 3851 3863 3950 4111
``

``
width 24 (6000 walks, sum 30671188):
86 116 121 124 166 182 189 202 208 210 246 249 263 264 265 268 273 304 313 335 342 378 404 407 411x2 412 414 418 420 427 453 455 467 484 488 490 493x2 500x2 501 503 517 529 531 540 542 547 555x2 560 562 571 574 578 582 592 596 598 599 600 601 604 607 610 618 620 621 627 629 633 644 652 654x2 656 672 673 679 684 685 687 690 693x2 695 696 698 706 718x2 720x2 724 726 728 734x2 738 739 741 742 743 744 748 753 764 771 774 776 777 789 801x2 805 807 808 814 815 820 822x2 823 825 830 833 834x2 841 842 851x2 853x2 862x2 871 877 879 884 886 887 889 891 892 894 896 898 900 903 906 909 913 914 918 932 934 935 942 943 944 957 960x2 965 969 972 973 986 988x2 989 998 1003 1006 1008 1015 1020 1028 1029 1030 1034 1038 1039 1041 1048 1049 1050 1054 1057 1059 1062 1064x2 1067 1072 1074 1080 1083 1084 1093 1094 1095 1099 1103x3 1104 1109 1112 1114x2 1115 1117 1119 1120 1121 1125 1126 1129 1136 1137 1139 1140 1144 1149 1152x2 1153 1156 1160 1169 1174 1182x2 1195 1199x2 1201 1207 1208 1214 1215 1216 1218 1219 1222 1223 1224 1225 1227 1228 1230x2 1234 1235 1239x2 1242 1244 1245x2 1247 1251x2 1256x3 1260 1264 1265x2 1267 1273 1274x3 1275 1276 1279 1281 1282 1283 1288 1297x2 1301 1303x2 1304 1312 1315 1319x2 1321 1322 1324 1327 1328 1329 1330 1332 1334 1335 1341 1342 1346 1350x2 1355 1357 1359 1361 1367 1369x2 1370 1372 1374 1379 1384 1385 1395x3 1400x2 1401x2 1404 1405 1406 1407 1408 1409x2 1410 1413 1415x2 1418 1421 1425x2 1437 1440 1442 1452 1455x2 1456 1457 1465 1467 1469 1470x3 1471 1472x2 1473 1474 1476 1478 1481 1483 1484 1487 1489x2 1490 1491 1492 1494 1495 1496 1497 1499 1501 1502 1504 1507 1508 1518 1522 1523 1526x2 1527x2 1529x2 1531 1532 1535 1536x3 1538 1541x3 1542x3 1544 1546 1548x2 1550 1551 1553x2 1559 1560 1561x2 1562x2 1566x3 1569x2 1571 1572x2 1574 1575 1577 1578 1579x2 1582 1583x4 1589 1590 1591 1592 1593 1595x2 1600 1604 1607 1613 1614 1620x2 1622 1625 1629 1630 1632x2 1633 1640 1642 1643x2 1645 1650 1652 1653 1654 1659 1661x2 1662 1664 1665 1667 1668 1669 1673 1675x2 1676 1677 1678 1679 1686x2 1687x2 1688 1690 1691 1693 1694x2 1695 1697 1698x2 1701x2 1702 1708 1712 1715 1716 1721x2 1725 1732 1734 1735x2 1740x3 1741 1749 1756x2 1760 1762 1763x3 1765 1767 1768 1769x2 1770 1771 1772 1775 1777x2 1778 1779 1780 1782 1786x2 1787x2 1790 1792x2 1797 1798 1799 1803 1807 1809x3 1811 1813x2 1814 1815 1816 1817x2 1818x2 1819x3 1822 1824 1825x2 1826 1830x3 1836 1837 1839 1841 1842x2 1846x2 1848 1849 1850 1857 1862 1864x3 1866 1867 1869 1871 1875 1881x2 1887 1888 1889 1890x2 1891 1894 1897 1904 1909 1911 1912x2 1917 1918x2 1919x2 1923x2 1925x2 1928x2 1930x2 1932 1933 1934x3 1935 1937 1939 1940 1942x2 1943x2 1944 1945 1948x2 1950 1951 1956 1958x2 1959 1961 1962 1963 1966 1967 1971 1973 1974 1976x2 1978 1979x2 1980 1981x2 1982 1986 1990 1991x3 1992 1996 1997 1998 1999x2 2000 2002 2004 2007 2009x2 2010 2011 2012 2013 2015x2 2016 2019x2 2020x3 2023 2026 2027x3 2029 2030 2032 2036 2039 2042 2044x2 2048x2 2049 2052 2056x2 2058 2061 2063x2 2065 2068x2 2069 2070 2071x2 2073x2 2074 2075x2 2076 2078 2080x2 2082 2084x2 2085 2086x2 2087x2 2088x2 2091 2095 2097x2 2100x2 2101x2 2103 2104 2106 2107 2108 2109 2110 2111x2 2113 2114 2115x2 2117 2119 2120 2121 2122 2123x3 2126 2130x3 2136x2 2137 2141x2 2142 2143x2 2145x2 2146 2148 2150 2152 2153 2154x2 2162 2165 2166 2167 2168 2173 2179 2181 2184 2186 2190 2191 2192 2194x3 2195 2196x3 2199x2 2200x2 2202 2203 2209 2210x2 2214 2216x2 2218 2219 2222 2224x3 2226x2 2227 2229 2232x2 2235 2237 2238 2239 2245x2 2246 2248 2250 2252x2 2253 2254 2258 2260 2261 2264 2265 2267x2 2268 2271x2 2273 2274 2275x2 2279x2 2280x2 2282 2283x2 2285 2287 2295x2 2298 2301 2304x2 2305 2309x2 2311x3 2312 2313 2314x2 2315x2 2317 2319 2320 2321 2322 2324 2326 2327 2331 2332 2333 2339 2343 2344 2347x3 2349 2350 2352 2353 2355 2356 2357x3 2359 2361x2 2365 2366 2371 2372x2 2374 2375 2377 2378 2381 2383 2384 2386 2387 2390 2391 2392x3 2394x4 2397 2398 2399 2400x2 2402x3 2406 2408x2 2409x2 2412x2 2413 2416 2419x2 2422x2 2425 2429 2430 2431x2 2432x3 2433x3 2434 2438x3 2439 2440 2441 2443 2444 2445 2446 2448 2449x2 2450 2451x3 2453x2 2454 2458x2 2459x3 2460x3 2462 2464x2 2466 2471 2473x2 2474 2476 2479 2480 2481x2 2482 2485 2488 2490 2492 2495x2 2497 2500 2503 2504 2507 2508x2 2512 2514 2517x2 2518x2 2520 2522 2524 2525 2527x3 2532 2533 2534 2535 2538 2541 2542x2 2543 2545 2546 2547 2548 2550 2551x3 2552 2553x2 2557 2558x2 2560x2 2561 2563 2565 2566 2569 2570 2573 2574 2577 2578 2579 2581 2582 2584 2586x2 2587x2 2588x2 2589x2 2592x2 2596 2599 2600 2601 2606 2609 2612x3 2614 2616x3 2619 2620x2 2621 2622 2624 2626x2 2627 2628x2 2629x2 2630 2631x2 2632x2 2634 2636 2637 2640 2641 2642 2643x2 2645 2646x3 2648 2650x2 2651 2653 2655x2 2656 2658 2659 2660 2661 2663x3 2664x2 2667x2 2669 2670 2671 2673 2675 2676x2 2677x2 2679 2682 2683x3 2685x3 2686x3 2689x2 2693 2694x3 2695 2696x3 2698 2700 2703x2 2704 2705x2 2706x2 2707 2709x2 2710 2712 2714x3 2715 2717x2 2718x2 2723 2727x2 2729 2732 2734x3 2739 2740 2743x2 2745x2 2746x3 2752 2753 2757 2758 2761 2762x2 2765 2767x2 2768 2769 2773x3 2774x2 2775 2778 2779 2780 2781x3 2782 2785 2788 2789 2790 2795 2797 2798 2799 2800 2804 2807x2 2810x3 2812x2 2814x2 2817 2818 2819x2 2821 2822 2826 2827 2829 2830x2 2831 2834 2836x3 2837 2838 2839 2840 2842 2844 2845x2 2846 2848 2849 2850 2851x5 2858x2 2860x4 2861x2 2863x2 2864 2865 2866x2 2867 2868 2871x2 2872 2873 2874 2875x2 2879 2881 2882x3 2887 2888x2 2890x2 2891 2895 2896x2 2897 2898 2900 2902x3 2903x2 2904 2906 2907 2908 2910x3 2911 2912x3 2913 2915x3 2917 2920 2921x3 2922 2924 2926 2927x2 2929 2932 2933x2 2934x3 2935 2936 2937x2 2938 2941 2943x2 2945x3 2946x2 2947 2948x4 2949 2950 2952 2956 2962 2966 2967x2 2968x2 2969x3 2971 2972x2 2973x2 2976 2978x2 2980x3 2981 2982 2984x2 2988x2 2990 2991x2 2993x2 3000 3002 3003 3004x2 3005 3006x3 3007x2 3015 3020x3 3021 3025 3027 3028x2 3031 3033 3034x2 3038 3040 3042 3043 3045 3048 3050 3052 3056 3057 3059 3060 3063 3065 3067x2 3068 3070x3 3072 3073x2 3075 3078 3079 3080 3081 3083x2 3084x2 3085 3086 3090x2 3091 3092x2 3094x3 3097 3100 3101 3102 3104x2 3105 3106x4 3107 3109x3 3110 3112 3113x2 3114 3115x2 3116 3117 3118 3119 3120x2 3121x3 3123x2 3125 3126 3127x3 3128 3129 3131 3133 3134x2 3136 3137x2 3138x2 3140 3143 3144x2 3145 3146 3148x2 3150 3151 3152 3153 3154 3157x2 3158x3 3159x3 3160 3162 3163x2 3164x3 3165x2 3166 3167 3170x2 3171 3172 3174 3177 3179 3180x2 3182 3184 3185x2 3188 3190 3191 3192 3193 3194 3196x3 3199 3200 3202 3205x2 3206x3 3210 3211 3213x2 3214x3 3217 3218 3220 3222x2 3223 3224x4 3225 3226x3 3227 3228x2 3230x2 3231 3232 3233 3236x2 3238x2 3240x4 3241 3242 3246 3249x2 3254 3255x3 3256 3257x2 3261 3264x2 3265x4 3266 3269 3270 3272x2 3273x3 3274 3278 3279x5 3286x2 3291 3293x2 3294 3296x2 3298 3299 3301 3303x2 3305 3308x2 3309x2 3311x2 3313x3 3314 3315 3316 3317 3318 3321x3 3322 3323x2 3324x3 3325 3326x2 3332 3333 3334 3338 3339 3340x2 3342x2 3344 3345 3346 3348 3350x2 3351 3352 3354 3355x2 3356 3358x2 3359 3360x5 3361 3363 3365x2 3368 3370x2 3372 3375x2 3380x3 3381x3 3382 3386 3389x4 3391 3392 3393 3395x3 3397 3398 3399 3400 3403x2 3404x2 3405x2 3408x3 3409x2 3410 3413 3414 3417 3418 3421x2 3423x2 3425 3426 3428 3429x2 3430x2 3431x2 3432 3434 3435 3436x3 3438 3439 3441 3443 3445 3446x2 3447 3448 3450x2 3451x2 3452 3453x2 3454x4 3455 3459 3461x2 3470x2 3471 3475x2 3477 3478x4 3480x2 3481x2 3482 3483 3484x2 3485 3486x3 3488 3489 3490 3491 3493 3497x2 3500 3501 3504 3505 3507 3508 3515 3517x3 3521x3 3522x2 3525 3526x2 3528 3529 3530 3532 3533x2 3534 3535 3536x2 3537x4 3538x2 3540x3 3541 3542 3543 3545x3 3546 3548x2 3549x2 3550 3551 3552 3553 3554x3 3556x2 3559 3560 3563 3564x2 3565x2 3566x3 3567x2 3568 3572x2 3573x3 3574x2 3575 3576x3 3577 3578 3580 3581 3583 3584 3586 3587 3588 3590 3593 3594x3 3596x2 3599 3602x3 3603 3605 3606 3607 3608 3612 3615 3616 3617x3 3618 3620x3 3621 3623 3625x2 3626x3 3627 3629x2 3630x2 3631x2 3632 3634x2 3637 3638x2 3639 3643x2 3646x4 3647x2 3648 3649x2 3650 3651 3652x2 3654 3656 3657 3659 3660x2 3663 3672 3675 3678x2 3679x2 3680 3681x2 3682 3684 3686x2 3687x2 3690x2 3691x2 3692 3693 3694x2 3697x2 3699 3700x2 3701 3703 3705 3707 3708x3 3711x2 3714 3716x2 3717 3719x2 3722 3723 3724x2 3727 3729x2 3731 3732 3733 3735 3736 3737 3739 3740x2 3741 3742x2 3744x2 3746 3748 3750 3753 3754 3755 3758 3759x2 3760 3761x2 3762 3764 3765x2 3766 3768 3769x2 3773 3774 3775 3779 3781 3785 3786 3787 3790 3791 3793 3794x2 3795 3798 3800x2 3801x4 3802 3803 3805x2 3809 3812x3 3814x2 3815x2 3816x2 3817x2 3820x2 3821 3822 3823 3824 3827x2 3828 3830 3832 3833x2 3834 3835 3838x4 3839 3840 3841x2 3842x2 3844 3846x2 3849x2 3850 3852x2 3855x2 3856x2 3857 3859 3862 3864x2 3867 3868 3869x5 3870 3871x2 3874x2 3875 3878x2 3879 3880 3882 3883x2 3884 3886x2 3888 3889 3890 3891 3892 3893x2 3895 3896 3897 3898 3899 3901 3902 3903 3905x2 3907x2 3908x3 3909 3910 3911 3914 3915x4 3923 3925x2 3926x3 3928 3929 3930 3931 3932 3935 3937x2 3938 3939 3940 3942 3943 3944x2 3945x3 3946 3948 3949 3950x3 3951x2 3954x2 3955 3959 3961 3962 3963x2 3964 3965x2 3967x2 3968 3969 3971x2 3972 3973x2 3974x2 3975x3 3976x3 3981x3 3982 3983 3984x2 3987x2 3989 3991x2 3993 3995 3998 4002 4004x2 4005x2 4006 4008 4009x3 4010 4011 4012 4014x2 4016 4018 4019 4021 4022x2 4024x2 4025 4026 4027x2 4029x3 4032 4034x2 4035 4036 4037x2 4039x2 4041 4042 4043 4044 4045x3 4046 4047x3 4051 4054 4057x2 4060x2 4061 4062 4065x2 4066 4067 4068x2 4070 4073x2 4075 4076 4077 4082x2 4083 4085 4086x2 4087x2 4090x2 4093 4094x3 4095x2 4098x2 4099 4101 4102x2 4103x2 4104 4105 4106 4108 4111x2 4112 4114x2 4117 4121x3 4124 4125 4127 4128x2 4129x2 4130x3 4131 4132x2 4139 4141 4144 4145x2 4146 4148 4151x2 4155 4157 4159 4161x2 4162 4163 4164x2 4168 4170 4171 4172 4173 4175 4176x2 4177 4178 4179 4180x2 4181x2 4182 4183x4 4185 4186x2 4187 4188 4189x4 4190 4193 4194 4195 4196x3 4199 4200x2 4202x2 4203 4205x4 4206 4209 4212x2 4214 4216x3 4217 4218x2 4220 4221x2 4222 4225 4226x3 4231x3 4232 4238x3 4241 4243 4244x2 4246x3 4247 4248 4249 4251x2 4254 4256x4 4259 4261 4262 4263x2 4264 4266 4268x3 4270 4271 4277 4278 4279x2 4282 4283 4284x2 4285x2 4286 4288 4289x2 4290x3 4291 4292 4299 4301x2 4304x3 4305 4306x3 4309 4310 4313 4315 4316 4317 4318x3 4321 4325x3 4326 4327 4328 4329 4332x2 4333x2 4337x2 4343x2 4344 4347 4350 4353x3 4354 4356 4357 4360 4361 4363x2 4365 4368x2 4369 4370 4371 4372 4373x3 4375 4377x3 4379x2 4380x2 4381 4382x2 4385 4386 4388 4391x2 4393 4394 4395 4397 4399 4400 4401x2 4406 4408x3 4411 4412 4415 4416x2 4418 4419 4420 4423x2 4430 4433 4434 4437 4438x2 4439 4440 4441 4442 4445 4446x2 4448 4449x2 4451x2 4452 4453x3 4454x3 4455x4 4456x3 4458 4459x2 4461x2 4463x2 4464 4466 4468x2 4469 4471 4472 4475x3 4476 4477 4478 4484 4485x4 4486 4488 4489 4494x2 4497 4498 4499 4504x2 4509 4511x2 4513 4515x2 4518x2 4519 4522 4526 4527x2 4528x2 4529 4530 4533 4534x2 4535 4536 4539 4540x4 4543 4544x2 4547 4548x2 4550 4552 4555x2 4558 4560 4561x2 4562 4564 4565 4567x2 4569x2 4572 4573x2 4575 4576 4577 4580x2 4581x2 4582 4584 4586 4587x3 4589 4590 4592x2 4595 4597 4598x2 4599 4600 4602 4604 4605 4606 4607x2 4608 4609x3 4610x3 4612 4613 4615 4616 4617x2 4621 4623x2 4628 4629 4634 4637x2 4638 4639x2 4641 4642 4645x3 4646 4647 4648x2 4649x2 4651 4652 4653 4654 4657 4661 4663x2 4664 4668 4669 4671x2 4673 4678x2 4679x2 4681 4682x2 4685 4686x2 4687 4690 4691 4693x2 4695x4 4696 4697 4700 4701x2 4703 4706x2 4708 4711x4 4712 4714 4715x2 4718x2 4719 4720 4722x3 4724 4727 4728 4732x3 4734 4735 4737 4738 4740x2 4742 4750 4753x2 4754 4756 4760 4761 4763 4764x2 4766 4767 4768 4769 4770 4771 4774 4775 4777 4778 4779 4783 4785 4787x2 4788 4789 4792 4793 4794 4795 4796 4797 4798 4801 4802 4804x2 4805 4806 4807x2 4810x3 4812 4814x2 4815 4816x3 4817x2 4819x2 4820x2 4823 4824 4826 4827x2 4828 4830 4832 4833 4834 4835 4837 4838 4839 4842x5 4843 4844 4847x4 4848x2 4851x2 4852x2 4855 4857 4859 4863x3 4865 4866 4867 4868x2 4869x4 4873 4874x4 4876x2 4877 4878x2 4882x2 4883 4884 4885 4886x2 4887x2 4889 4890 4893x2 4899x2 4902 4904x2 4905x2 4908 4911 4913x2 4914x2 4915 4917 4918x2 4924 4925x2 4926x2 4927 4930x2 4931 4933 4934x2 4936 4938 4939 4943x2 4944x2 4946 4948 4951 4953 4954 4955 4957 4958x2 4959x3 4960x2 4961 4963x2 4965x3 4967x3 4969 4971x3 4972 4975 4976 4977x2 4979x3 4982x3 4984 4985 4986 4989x3 4990 4991 4992x2 4993 4994 4995 4996 4997 4998 5002x3 5006x2 5010 5011x2 5014x2 5015 5016 5018x2 5019 5020 5022 5024 5025 5026 5030x4 5032 5036x2 5037x2 5039 5040x2 5041x2 5042 5043 5044 5045x3 5047 5048 5049 5051x2 5054 5057 5058 5062x5 5063 5065 5067x2 5068x2 5069 5070 5071x2 5072 5075 5078 5081 5082x2 5084x3 5086 5087 5091x2 5092x2 5093 5095x2 5097 5099x2 5100 5102 5104x2 5108 5110 5113 5115 5116x2 5117 5118 5119x2 5120 5121x2 5122 5124 5125 5129 5130 5131 5133 5134 5135x2 5137 5138 5139 5140x2 5142 5145 5149 5150 5152x2 5153x4 5154x2 5156 5158x2 5159x3 5160x4 5163 5166 5167x2 5169x2 5170x2 5172x2 5173x2 5174x2 5176 5178 5179 5180 5183 5184x2 5188x2 5190 5191x2 5194x3 5195 5196 5198 5199x3 5200 5201x2 5202 5204x3 5206x2 5207 5208 5209 5210x2 5212 5214x2 5216 5217x2 5220x2 5223 5224 5225x2 5229x2 5231x2 5232x2 5233x2 5234 5235x2 5236 5237 5239x3 5242 5245 5246 5251 5252 5257 5259x2 5260x2 5262 5265 5268 5269 5272 5273x2 5275x2 5276 5278 5279 5282 5283x2 5284 5286 5287 5288x2 5289 5290x2 5292 5293 5294 5295 5300x2 5301x2 5302x2 5303x2 5308 5310x2 5313 5316x2 5318 5319 5320x3 5321x2 5322 5323 5324 5325 5326 5327 5328 5329 5330 5332 5333 5334 5335 5336 5337 5338x2 5339 5343 5344x2 5346 5349 5351 5352 5356 5357x5 5359 5360x2 5361x3 5363 5365 5366x3 5368 5369 5371 5372 5374 5375x3 5376x2 5377 5378 5379 5380x2 5381x2 5382 5383 5384 5385 5386x2 5387 5388x5 5389 5390 5391x2 5392 5393 5397x2 5400 5401 5403 5404x2 5408 5410 5414 5417 5419 5420x2 5421x2 5422x2 5423 5424x2 5425x3 5426 5429 5430 5432 5433 5434x5 5435 5436 5437 5438 5439 5440 5441 5443 5444 5445x2 5446x2 5447 5449x3 5450 5457 5458 5459x2 5462x2 5463 5464x2 5466 5467x2 5469x2 5472 5473x2 5478x2 5479x3 5481 5482 5486 5490x2 5491 5494 5495 5497x2 5498 5499x3 5501x2 5503x2 5506 5508x2 5509 5511 5512 5516 5520 5525 5526x3 5527x2 5528 5529 5530 5532 5533 5534x2 5537x3 5540 5542 5546x2 5548 5554 5555x2 5556x2 5558 5561x2 5563 5564 5566 5568 5570 5572 5574 5575 5576 5578 5579 5580 5581 5585 5586 5588 5589 5590 5591x2 5593x2 5595 5596 5597 5598x2 5600 5601 5603x2 5604 5606 5610 5611 5612 5613 5615x2 5616x3 5617 5618 5619x2 5620 5622x2 5623x2 5624x2 5626 5629 5631 5632 5636x3 5639 5642 5643x2 5644 5645 5650 5654 5655 5656x2 5658 5659 5660 5665x2 5668 5670 5671x3 5674 5675x2 5676 5677 5679 5681 5682 5683 5684 5685 5687x4 5688 5690x2 5692 5693 5694 5695 5696x2 5698 5701 5704 5705x2 5709 5712x4 5714 5717 5719 5720 5721x3 5722 5723 5724x2 5725x2 5728 5729x2 5731 5732x2 5733 5737 5741x2 5746 5750x4 5751 5752 5753x2 5757x3 5758x2 5759 5762x2 5763 5764 5765x3 5766x2 5767x2 5768x2 5770 5772 5775x2 5776 5778 5780 5782 5784x3 5785 5786 5789 5791 5792 5793 5794x2 5795 5797 5798 5800x2 5801 5805x4 5810 5812 5816x3 5817x2 5819 5820 5828 5830x2 5835 5836 5837 5845 5847x2 5850 5851x3 5852x3 5854x2 5856x2 5858x2 5859 5861x2 5863 5865x2 5866x2 5871 5873 5876x2 5877 5880 5881 5883 5886 5888 5889x2 5890 5891 5893 5895 5896 5899x2 5901x2 5902 5903 5904 5905 5906 5908 5910 5911x2 5914x2 5915 5917 5918 5919x2 5920 5929x2 5932 5934 5936 5937x2 5938 5940 5941 5942 5944 5945 5950x2 5951 5952x2 5954 5955 5956x2 5957x2 5964 5966x3 5967 5968 5969x2 5972 5973x2 5974x2 5975 5980x2 5981 5982x3 5983x2 5987x2 5991x4 5996 5997 5999x2 6000 6003 6004 6008 6009 6011x2 6012x2 6014x2 6016 6019 6021 6022 6023x2 6024 6025x2 6028 6031 6032 6039x2 6040 6042 6043 6044x2 6045 6046x4 6047 6048 6051 6053x2 6054x2 6056 6057 6058 6059 6063 6064 6065x2 6067 6071 6074 6075 6076 6078 6080 6083x2 6084 6085x2 6090 6091 6093x2 6095 6096 6101 6103 6106x3 6107 6109 6111x3 6114x2 6115x2 6117x2 6118 6120x2 6125 6126x2 6127 6128 6131 6137 6138 6143 6146x2 6148x4 6150x3 6151 6152 6154 6158 6160 6161 6163 6166 6169x2 6171x2 6172x2 6173 6177 6182 6184 6185 6186 6189 6190x2 6193 6194 6198 6200x2 6201x2 6202x2 6203 6204 6205x2 6211x2 6215 6219x2 6223 6225 6226 6227 6228 6229 6231 6233 6235 6238 6241 6244 6247 6248 6249 6251x2 6253x3 6254 6255x2 6257 6260 6261 6262 6264 6265x2 6270x2 6271x2 6272 6273 6275x2 6277 6279x2 6283 6284 6285 6287 6288 6296 6299x2 6305 6306 6307 6310x2 6312 6314 6316x2 6317x2 6325 6328x2 6329 6330 6332 6334x2 6335 6336x2 6338x2 6340 6342 6344 6345 6346 6348x3 6349 6351 6352 6354 6355 6358 6359 6360 6361 6363 6364 6366 6368 6369 6371 6372 6374x3 6376x2 6382x3 6384 6385 6390 6391 6393 6394 6395 6397x2 6398 6399 6400x2 6401 6404x3 6406x2 6407 6408 6410 6411 6413 6414 6415x2 6416 6417 6419x2 6420x2 6421 6423 6424x2 6427 6428 6429 6432 6433 6436 6437x2 6438 6441 6442 6443 6444 6445 6446 6447 6448 6450 6451x3 6452 6456 6457 6462 6465 6466x2 6468x2 6469 6472 6475 6476x2 6478 6479x2 6480 6481 6482x2 6485 6489 6490x2 6491x2 6494x2 6500 6501x4 6506 6508 6509x2 6510 6511 6513 6514 6515 6516 6523x2 6525 6527x2 6528x2 6530 6532x2 6533 6534 6541 6543x2 6544 6548 6550 6551 6555 6558 6559 6560 6561 6562 6563x2 6567 6569 6573 6575x2 6578 6579 6580 6581 6583 6586 6587 6591 6593 6594x2 6598 6599 6601x2 6604 6606 6608 6614 6615 6626x2 6628x2 6629 6632 6633 6646x2 6648x2 6649 6654x2 6655x2 6657 6658 6659 6660x2 6661 6664 6666x3 6667x2 6668 6670 6671x3 6672 6684 6685 6688x2 6691 6692 6693 6697 6698 6699 6700 6701 6704 6709x2 6710 6715 6716x2 6718x2 6721x3 6723 6726 6728 6729 6730x2 6731x2 6732 6736x2 6740 6741 6744 6746 6747x2 6748 6749 6751 6753 6754x2 6755x3 6756x2 6757 6761 6763 6764x3 6767 6768x2 6770x2 6771 6774 6777 6778 6780 6786 6791x2 6793x2 6794 6795x2 6798x2 6806 6810x3 6813 6814x2 6816 6821 6823 6824 6825x2 6828x2 6832x3 6833 6834 6836x2 6837 6839 6840 6842x2 6849 6851 6856x2 6857 6860x2 6864 6868 6869 6871x2 6873 6874x2 6875x2 6878x2 6879 6881 6882 6883x2 6885 6888x2 6889 6890 6891 6892x3 6894x2 6897 6898 6899 6901 6904 6905 6906 6910 6913 6918 6919x2 6920 6921 6924x2 6926x3 6927x2 6929 6934 6936 6937x2 6938 6941 6943 6944 6945 6946x2 6947 6949 6950 6951 6955 6959x3 6960 6963x5 6965 6966 6967x2 6969 6972 6973 6974 6982 6986 6988 6989 6992x2 6994 6996 6997 7000 7001 7002 7007 7009 7012x2 7014 7015x2 7023 7024x3 7027 7029 7033 7038x2 7039 7040x2 7041 7042 7046 7048 7051x3 7052x3 7053 7054 7055 7056x3 7057x3 7061 7062x2 7063x2 7064 7067 7069x2 7070 7072 7074x2 7082 7084 7085 7086 7089 7092 7093 7096 7101 7102x2 7104 7108 7109x3 7110 7117 7119 7123 7128 7129 7130 7131 7133x2 7139x3 7142 7145 7148 7149 7150 7152 7153x2 7155 7156 7157 7158 7159 7162 7164 7166 7169x2 7171x2 7173 7174 7175 7177 7178 7180 7189 7193 7195 7196 7197 7198 7202 7203 7205 7207 7208x2 7209 7210 7214x2 7215x2 7217x2 7226 7227 7232x2 7238 7243 7245 7247 7248 7249 7250 7252x2 7254 7259 7263x2 7264 7265 7266 7269 7270x3 7271x2 7273 7275 7279x2 7281 7285 7286 7287 7289 7290x2 7298 7301 7303 7305 7306 7309 7310 7314 7315x2 7316x2 7318 7320 7322x2 7323x2 7324 7325 7326 7327x2 7328 7329 7330 7332 7333 7337 7338 7340x2 7341x2 7345 7346x3 7347 7352 7353 7355 7356x2 7358 7361 7364 7365 7367 7369 7370 7375 7376 7377 7380x2 7381x2 7382 7383 7385 7387 7388 7391 7395 7396 7398 7401 7402x2 7404x2 7405 7406 7408 7410 7414 7415 7418 7421 7424x3 7427x3 7432 7433 7436 7438 7439x3 7444x2 7447x2 7448 7450 7454 7459 7460 7462 7463 7469 7475 7478x2 7479x2 7483 7484x2 7487 7494 7496 7505x2 7506 7507x2 7510 7511 7513 7514 7516 7518 7520x2 7527 7533 7534x3 7535 7538 7539 7542x2 7544x2 7545 7546 7548 7549 7550 7553x2 7555 7558x3 7562 7563 7564 7571 7576 7578 7584 7585 7593 7594 7595x2 7597 7598 7599 7600 7601 7605 7608x2 7609 7610 7613x2 7618 7619x2 7620x2 7623 7624x2 7625 7630 7632x3 7638 7646 7648 7649 7650x2 7651x2 7657x3 7659 7667 7670 7678 7680 7684 7685 7688 7689 7690 7692 7697 7698 7703 7705 7706x2 7709x3 7720 7721 7726 7728 7742 7745 7747 7748 7751 7755 7757 7758x2 7766x2 7771x2 7773 7777 7778 7781 7782x2 7783 7785 7788 7791 7797 7799 7802 7804 7807x3 7812 7815x2 7817 7818 7822 7824 7827 7829 7830 7832 7834 7835 7836x2 7838 7839 7841 7842 7846 7847 7848 7849 7852 7857 7858 7859 7860 7862 7865 7868x2 7870 7874x2 7876x2 7878 7879 7881 7882x3 7886 7889 7890 7891 7892 7896 7900x2 7903 7904x2 7909 7912x2 7929 7934 7940 7943 7945 7946 7948 7953 7956 7958x2 7960 7961 7962 7965 7973 7978x4 7982 7985 7989 7990 7993 7995x3 7996x2 7998 8000 8003 8005 8012 8013 8015 8017 8018 8021 8025 8029 8033 8037 8038x3 8039 8040 8042x2 8046x2 8047 8048 8049 8050 8052 8057 8061 8065 8067 8073 8075 8081 8083x2 8085 8089 8092x2 8093 8099 8100 8102 8103 8104x2 8105x4 8106 8107 8108x3 8115 8116x3 8117 8120 8121 8123 8126x2 8130 8132 8134 8136 8137 8140 8144 8147 8148 8150x2 8159 8160 8161 8162 8164 8168 8169 8177 8178 8180 8184x2 8185 8186 8188x2 8190 8192x2 8193 8195x2 8200 8201x3 8212x2 8217 8218 8222 8225 8236 8239 8243 8246 8251x2 8254 8256 8257 8258 8260x2 8264 8266 8267 8268 8272 8278 8279x2 8280 8281x3 8286 8287 8293 8298 8301x2 8304 8310 8312x3 8313 8320 8321x2 8322 8324 8325 8328 8330 8338 8342 8345x2 8346 8349 8352 8354 8358 8359 8362 8363 8364x2 8366 8369 8371 8374 8380 8385x2 8386 8388 8396 8398 8400 8407 8408x2 8412 8414 8416 8418 8419 8426 8432 8434 8436 8441 8444 8446 8451 8454x2 8458 8459 8463 8464 8468 8469x2 8471 8472 8473 8475 8477 8480 8481 8482 8484 8489 8492 8496x2 8498 8501 8502 8509 8510 8513 8524 8528 8530 8534 8537 8538x2 8540 8543 8547 8549 8563 8569 8572 8573x2 8582 8585x3 8587 8590 8597x2 8599 8609 8611 8614x2 8615 8616 8618 8620x2 8627 8632 8635 8636x3 8637 8640 8644 8645 8652 8656 8659 8660 8665 8667 8669 8676 8677 8679 8682 8688x2 8691 8696 8699x2 8712 8715 8716 8718 8721x2 8724 8725 8727x2 8729 8737 8738 8740 8744x2 8751 8752x2 8755 8758 8762 8767 8768 8776 8782x2 8783x2 8786 8787x2 8794 8799 8801 8802 8807 8810x2 8818 8820 8821 8824 8828 8830x3 8833 8835x2 8836 8843 8847 8855 8859 8860x2 8863 8867 8868 8871 8878 8879 8887 8889 8902 8911 8916 8918 8924 8929 8939 8943 8947 8957x2 8958 8962x2 8965 8968x3 8974 8982 8984 8985 8986 8990 8993 8996 8997 8999 9007 9009 9014 9023 9025 9032 9036 9048 9050 9051 9053 9054 9059 9061 9072 9073x2 9075 9076 9077 9083 9085 9088 9091 9099 9103 9104 9105 9106x2 9112 9117 9118 9119x2 9127 9128x2 9131 9144 9153 9156x2 9157 9162 9168 9171 9172 9179x2 9182 9185 9190 9192 9195 9198x2 9200 9204 9206x2 9207 9217 9221 9222 9225 9226 9231 9233x2 9237 9238 9246 9249 9255 9256 9260 9265 9275 9278 9282 9286x2 9293 9294 9296 9299 9304 9308 9310 9316 9318 9321 9322 9323 9328 9337x2 9339 9345 9348 9353 9355 9360 9362 9367 9368 9371 9373 9382 9385 9387 9392 9393 9395 9398 9399 9400 9403 9405 9406 9408 9409 9418 9427 9431 9436x2 9451 9454 9457 9461 9462 9463 9474 9475 9478 9479 9493 9494 9498 9499 9502 9506 9513x2 9514 9527 9528 9537x2 9538 9543 9554 9555 9556 9563x2 9567 9573 9576 9581 9585 9586x2 9587x2 9592 9594 9597x2 9608 9615 9623x2 9624 9626 9640 9649 9653 9654 9655 9656x2 9661 9665 9666 9667 9673 9675 9685 9690 9703 9704 9716 9718 9720x3 9724 9725x2 9728 9741 9756 9757 9768 9772 9773 9777 9790 9791 9796 9807 9818 9819 9822 9823 9830 9851 9860x2 9869 9873 9876 9881x2 9889 9896 9897 9913 9915 9923 9936 9939 9941 9945 9947 9948 9952 9957 9965 9966 9978 9982 9988 9996x2 9999 10002 10003 10014 10017 10018 10024 10025 10029 10037 10041 10051 10069x2 10070 10073 10075 10076 10093 10102 10103 10108 10109 10110 10116 10130 10133 10135 10137x2 10154 10172 10183 10185 10187 10206 10214x2 10219 10223 10225 10226 10246 10260 10263 10289 10296 10304 10311 10318 10340 10343 10349x2 10374 10375x2 10378x2 10394 10407 10416 10422 10429 10435 10447x2 10457x2 10461 10462 10466 10478 10510x2 10516 10519 10534 10538 10555 10559 10563 10569 10584 10620 10645x2 10651 10652 10658 10681 10682 10687 10688 10693 10698 10711 10712 10715 10736 10741 10744x2 10766 10769 10785 10815 10820 10830 10831 10835 10846 10848 10850 10884 10889 10892 10905 10914 10923 10940 10950 10966 10968 10970 10978 10988 11015 11017 11033 11062 11065 11069 11074 11089 11093x2 11102 11106 11109 11113 11114x2 11141 11151 11162 11167 11171 11192 11204 11209 11222 11227 11228 11234 11250 11251 11257 11265 11273 11275 11277 11283 11290 11300 11303 11313 11318 11319 11352 11366 11375 11377 11390 11407 11412 11436 11440 11442 11443 11446x2 11464 11490 11509 11518 11532 11537 11547 11565 11631 11646 11648 11661 11674 11683 11698 11725 11747 11761 11764 11766 11788 11795 11804 11811 11857 11863 11874 11883 11906 11934 11935 11937 11951 11955 11983 12004 12031 12035 12050 12117 12140 12182 12262 12302 12312 12408 12420 12449 12484 12500 12502 12503 12510 12514 12602 12605 12654 12659 12737 12777 12782 12784 12833 12855 12874 13138 13159 13232 13248 13290 13294 13308 13316 13355 13597 13721 13923 13985 14098 14114 14117 14243 14496 14637 14899 14980 15162 15490 15587 16472 16803 17225 17714
``

``
width 28 (1200 walks, sum 23913256):
174 313 1091 1218 1320 1428 1511 1583 1715 1904 1955 1973 2100 2161 2215 2231 2255 2263 2369 2436 2576 2704 2718 2761 2778 2783 2887 2975 3051 3179 3230 3294 3309 3404 3517 3527 3589 3715 3772 3776 3795 3815 3841 3856 3858 3910 3984 3992 3995 4013 4024 4039 4042 4117 4124 4212 4226 4256 4393 4434 4536 4549 4565 4629 4666 4750 4864 4891 4947 4951 5053 5094 5124x2 5129 5186 5235 5288 5292 5307 5352 5427 5529 5591 5668 5671 5676 5761 5784 5839 5886 5915 5923 5978x2 6015 6124 6136 6139 6148 6153 6167 6183 6322 6342 6377 6409 6445 6481 6511 6517 6561 6691 6780x2 6799 6818 6864 6929 6943 6961 6963 6975 7014 7124 7127 7145 7163x2 7186 7223 7257 7261 7270 7332 7349 7380 7443 7477 7516 7529 7546 7591 7611 7613 7615 7620 7623 7662 7696 7701 7781 7797 7896 7902 7935 8022 8060 8067 8068 8077 8098 8129 8144 8153 8154 8200x2 8205 8223 8260 8308 8319 8329 8354 8382 8411 8454 8461 8502 8564 8587 8597 8600 8623 8659 8687 8744 8761 8804 8864 8867 8883 8891 9049 9069 9086 9115 9165 9214 9231 9286 9314 9318 9325 9353 9377 9381 9395 9411 9458 9482 9500 9612 9633 9651 9662 9705 9708 9718 9785 9798 9835 9847 9861 9864 9883 9900 9901 9909 9938 9987 10055 10060 10063 10070 10095 10162 10168 10178 10179 10180 10187 10218 10240 10246 10306 10409 10427 10451 10469 10491 10500 10516 10540 10542 10570 10581 10607 10622 10681 10694 10727 10730 10743 10817 10832 10847 10910 10913 10924 10941 10946 10948 10965 10983 11074 11144 11157 11179 11203 11219 11226 11253 11264 11270 11276 11321 11341 11383 11394 11402 11420 11466 11514 11555 11577 11585 11621 11663 11669 11733 11757 11758 11760 11780 11790 11810 11871 11877 11880 11914 12048 12067 12101 12124 12132 12133 12144 12155 12159 12173 12176 12312 12332 12357 12365 12417 12450 12461 12528 12536 12576 12581 12650 12712 12729 12754 12775 12813 12825 12836 12854 12958 12981 13000 13007 13043 13057 13112 13128 13147 13158 13203 13226 13235 13239 13286 13298 13343 13344 13349 13396 13417 13553 13620 13624 13645 13676 13704 13707 13752x2 13761 13787 13791 13801 13846 13856 13874 13878 13880 13884x2 13893 13942 13956 13977 13987 14003 14023x2 14037 14088 14124 14125 14126 14161 14164 14184 14220 14231 14240 14276 14281 14288 14340 14391 14396 14506 14546 14551 14556 14575 14588 14599 14606 14669 14671 14713 14736 14747 14776 14794 14799 14802 14851 14857 14867 14877 14894 14901 14903 14914 14964 14987 14995 15033 15088 15103 15106 15130 15133 15141 15146 15166 15181 15182 15185 15238 15241 15248 15274 15322 15398 15405 15409 15446 15455 15463 15474 15477 15487 15506 15530 15534 15544 15553 15562 15564 15588x2 15660 15669 15682 15752 15753 15756 15795 15801 15846 15927 15933 15940 15972 15993 16001x2 16044 16053 16070 16081 16082 16092 16154 16159 16166 16169 16206 16215 16229 16326 16337 16348 16368 16404 16405 16410 16482 16518 16550 16558 16573 16603 16657 16705 16721 16747 16757 16773 16776 16799 16859 16860 16871 16886 16888 16939 16942 16944 16946 16950x2 16955 17106 17146 17184 17196 17216 17225 17250 17267 17290 17302 17317 17321 17328 17375 17393 17421 17447 17465 17505 17510 17549 17559 17565 17573 17597x2 17612 17724 17725 17750 17777 17814 17825 17873x2 17888 17919 17922 17970 17971 17984 18004 18025 18050 18070 18089 18138 18139 18147 18163 18223 18274 18310 18348 18352 18362 18404 18433 18508 18532 18602 18682 18701 18729 18841 18844 18857 18924 18936 18954 18972 18976 19035 19040 19044x2 19049 19125x2 19136 19139 19181 19297 19366 19379 19401 19408 19431 19448 19449 19496 19504x2 19511 19531 19542 19573 19587 19590 19599 19649 19784 19790 19838 19878 19889 19898 19910 19982 20020 20107 20164 20205 20208 20214 20216x2 20228 20243x3 20252 20256 20263 20321 20324 20395 20417 20442 20444 20475 20569 20577 20602 20603 20623 20625 20633 20657 20666 20716 20721 20738 20764 20806 20827 20862 20878 20955 20966 20987 21001 21003 21006 21013 21052 21064 21080 21123 21128 21162 21197 21245 21248 21266 21355 21362 21403 21458 21475 21479 21493 21548 21576 21598 21640 21678 21690 21693 21717 21728 21740 21772 21773 21776 21791 21798x2 21804 21836 21854 21910 21913 21920 21931 21955 21996 21997 22018 22029 22063 22154 22217 22239 22248 22270 22354 22360 22388 22402 22465 22475 22521 22577 22673 22819 22857 22880 22889 22901 22908 22958 22968 23007 23042 23052 23068 23078 23109 23125 23157 23166 23186 23193 23194x2 23197 23247 23250 23287 23338 23351 23404 23412 23424 23449 23560 23561 23566 23594 23604 23615 23635 23676 23738 23747 23751 23807 23847 23888 23893 23899 23910 23955 23959 23961 23966 23978 23988 24001 24037 24074 24119 24125 24138 24180 24242x2 24249 24250 24256 24266 24290 24304 24321 24425 24461 24464 24468 24473 24474 24476 24478 24488 24520 24527 24575 24621 24710 24724 24740 24786 24823 24842 24851 24929 24932 24953 24956 25011 25018 25032 25047 25092 25120 25178 25289 25334 25365 25378 25385 25408 25458 25493 25515 25529 25550 25603 25604 25612 25630 25688 25708 25780 25781 25823 25890 25893 25928 25932 25947 25997 26013 26074 26110 26185 26234 26245 26251 26261 26268 26299 26324 26421 26465 26476 26503 26515 26525 26571 26580 26595 26601 26622 26632 26721 26733 26760 26787 26804 26863 26869 26900 27003 27004 27006 27010 27076 27083 27092 27191 27234 27235 27244 27251 27266 27299 27314 27319 27383 27441 27498 27549 27569 27585 27641 27677x2 27689 27699 27811 27817 27824 27932 27975 28001 28034 28042 28072 28129 28130 28131x2 28198 28230 28246 28285 28310 28313 28332 28335 28356 28411 28433 28516 28541 28562 28567 28575 28639 28648 28672 28673 28821 28825 28942 28954 28965 28994 29008 29058 29065 29120x2 29135 29245 29276 29279 29319 29320 29354 29401 29409 29486 29510 29580 29607 29650 29701 29740 29757 29838 29850 29855 29866 29917 29928 29944 29945 29955 29975 29991 30089 30118 30133 30161 30216 30271 30332 30340 30438 30588 30600 30846 30870 30871 30956 30990 31135 31194 31227 31269 31342 31399 31403 31494 31511 31556 31755 31812 31813 31900 31957 32005 32073 32109 32151 32167 32179 32180 32222 32246 32260 32271 32332 32354 32407 32470 32560x2 32637 32681 32701 32782 32789 32792 32812 32862 33190 33215 33336 33391 33426 33464 33485 33493 33556 33559 33575 33606 33708 33737 33756 33844 33922 33938 33949 33972 34061 34161 34163 34248 34249 34256 34356 34412 34676 34806 34870 34889 34892 34942 35023 35189 35346 35377 35395 35532 35576 35850 36099 36277 36324 36344 36453 36991 37033 37062 37251 37312 37439 37465 37502 37774 37844 37925 37940 38083 38118 38175 38351 38406 38408 38530 38559 38580 38587 38819 38842 38879 38918 38919 38933 38957 39033 39043 39255 39356 39534 39594 39718 40072 40197 40360 40556 40699 40924 40928 41053 41242 41374 41543 41551 41864 41897 42025 42411 42440 42463 42492 42504 42681 42855 43590 43700 43783 44747 44818 44924 45457 45582 45693 46230 46308 46905 47162 47289 47401 48811 48881 49115 49747 50433 50483 51052 51121 51603 51715 52045 54357 54390 54464 55363 56023 57740 58601
``

``
width 32 (1200 walks, sum 96654175):
317 1926 2308 2582 4300 5769 6313 7408 7868 8212 8407 10403 11756 11950 11983 12076 12345 12702 13184 13213 13584 13623 13685 14326 14350 15001 15067 15239 15443 15917 16450 17021 17129 17260 17317 17557 17594 17698 17840 17877 17889 17909 18394 18682 18924 18942 19252 19401 19550 19735 20050 20348 20569 20960 21429 22332 22366 22436 22671 23075 23396 23473 23782 24142 24193 24281 24400 24551 24593 24665 24681 24795 25103 25461 25680 25706 25778 25973 25975 25988 26675 26698 26742 26791 26976 27558 27768 28426 28535 28573 28614 28620 28623 28636 28793 28797 28806 29202 29301 29672 29748 29784 29862 29905 29932 29940 30055 30201 30460 30663 30744 30810 30857 31040 31046 31161 31279 31304 31622 31813 31894 32214 32422 32452 32932 33049 33316 33536 33636 33772 33867 33969 34024 34360 34737 34758 34771 35020 35071 35245 35298 35368 35576 35611 35645 35664 35894 35942 35999 36077 36092 36100 36190 36195 36525 36580 36629 36696 36840 36916 37097 37147 37160 37283 37284 37301 37322 37483 37827 38099 38188 38259 38278 38553 38759 39106 39163 39230 39437 39700 39718 39788 40019 40131 40456 40538 40651 40763 40910 41195 41209 41711 41761 41885 42030 42290 42291 42338 42390 42510 42523 42640 42780 42917 43414 43535 43589 43694 44031 44123 44195 44212 44355 44586 44692 44759 44884 45131 45169 45244 45246 45346 45434 45443 45453 45461 45549 45615 45712 45895 45898 45999 46202 46207 46324 46510 46645 46808 47101 47125 47145 47151 47212 47296 47451 47519 47571 47592 47663 47698 47935 48078 48102 48447 48586 48741 48743 48830 48841 48870 48907 48962 48990 49021 49036 49064 49083 49100 49128 49282 49288 49482 49515 49536 49549 49636 49720 49839 49893 50047 50080 50094 50123 50155 50282 50305 50551 50611 50755 50811 50818 50856 50973 51054 51151 51181 51236 51251 51361 51464 51570 51620 51673 51789 51826 51827 51858 51917 52047 52217 52305 52350 52390 52399 52424 52612 52664 52839 52840 52867 53047 53248 53627 53659 53729 53844 53895 53935 54043 54151 54174 54438 54451 54521 54593 54638 54822 55004 55038 55040 55338 55500 55600 55671 55884 55976 56096 56221 56299 56398 56486 56552 56599 56637 56776 56799 57212 57429 57487 57596 57618 57828 57866 57889 57916 58088 58159 58217 58382 58473 58534 58546 58624 58744 58795 58821 58882 59146 59252 59310 59335 59409 59502 59519 59672 59721 59860 59879 59955 60044 60188 60227 60282 60413 60424 60456 60600 60657 60676 60680 60799 60853 61085 61112 61135 61169 61172 61253 61255 61259 61279 61427 61785 61844 61856 62004 62054 62120 62156 62260 62618 62672 62881 62963 63028 63074 63165 63174 63199 63232 63241 63362 63613 63642 63644 63766 63893 63922 63945 63974 63991 63998 64013 64035 64147 64208 64367 64399 64423 64432 64433 64445 64466 64496 64573 64650 64735 64973 65070 65473 65486 65494 65526 65545 65613 65640 65801 65809 65822 65878 65889 65967 65997 66018 66152 66245 66282 66367 66561 66616 66687 66924 67000 67047 67061 67164 67298 67348 67351 67442 67473 67566 67675 67684 67704 67770 67875 67894 68188 68295 68296 68372 68408 68494 68586 68774 68837 68896 68949 69089 69190 69344 69435 69548 69612 69659 69681 69834 69876 69930 69932 69977 70284 70296 70315 70541 70544 70581 70618 70707 70710 70837 70849 70976 71006 71125 71126 71372 71406 71446 71491 71561 71599 71758 71765 71781 71908 72097 72120 72127 72165 72205 72241 72327 72336 72354 72362 72411 72719 72768 72783 72929 73227 73252 73255 73357 73456 73495 73511 73574 73620 73702 73768 74051 74302 74435 74492 74521 74525 74867 74920x2 75010 75104 75151 75162 75195 75204 75286 75365 75383 75404 75454 75509 75600 75747 75852 75920 75973 75992 76051 76053 76193 76290 76295 76306 76403 76455 76694 76772 76924 76940 77125 77251 77352 77392 77426 77486 77564 77704 77735 77936 78091 78104 78112 78164 78194 78238 78511 78810 79281 79380 79415 79479 79621 79710 79766 79794 79828 79852 79877 79944 79946 79997 80001 80200 80244 80299 80350 80444 80531 80600 80632 80636 80684 80720 80790 80887 80935 81021 81118 81229 81294 81379 81449 81450 81500 81526 81590 81751 81755 81816 82009 82059 82108 82130 82192 82462 82499 82718 82919 82946 82970 83138 83236 83594 83621 83656 83748 83811 83820 83845x2 84063 84157 84211 84499 84601 84722 84768 84856 85311 85388 85588 85607 85627 85683 85842 85869 85898 85926x2 86168 86329 86565 86592 86596 86675 86677 86724 86755 86786 86893 86910 87200 87326 87433 87471 87508 87545 87650 87669 87717 87787 87953 88058 88062 88090 88161 88367 88524 88792 89096 89146 89162 89171 89330 89394 89461 89817 89840 89893 90006 90013 90081 90157 90441 90832 90905 90912 91029 91308 91322 91414 91438 91478 91612x2 91700 91713 91892 91928 91968 91988 92062 92166 92308 92346 92347 92421 92494 92580 92589 92630 92650 92878 93021 93115 93207 93227 93249 93265 93351 93428 93469 93491 93497 93525 93624 93693 93713 93750 93849 94037 94054 94132 94134 94165 94194 94253 94529 94668 94694 94774 94944 94972 95125 95207 95323 95665 95711 95730 95916 95960 95968 95975 96099 96100 96169 96320 96523 96524 96545 96876 96979 97025 97068 97116 97145 97213 97234 97395 97414 97470 97615 97672 97710 97922 98047 98106 98218 98240 98256 98312 98322 98342 98500 98951 99076 99100 99451 99506 99572 99602 99739 99755 100399 100529 100538 100576 100638 100709 100933 101004 101081 101162 101235 101282 101484 101835 101908 102035 102139 102161 102326 102561 102574 102739 102826 102833 102967 102995 103208 103659 103772 103916 104037 104328 104416 104936 105030 105263 105277 105698 105771 105791 105860 105980 106004 106020 106094 106266 106627 106817 107103 107435 107521 107714 108153 108286 108331 108494 108550 108657 108739 108820 108827 108923 109113 109671 109700 109785 109786 109851 109894 109975 110313 110363 110490 110558 110612 110633 110903 111140 111288 111357 111600 111636 111759 111791 111883 111917 111920 112063 112160 112198 112261 112510 112613 112694 112962 112966 113321 113384 113457 113489 113536 113672 113724 113726 114002 114029 114101 114257 114343 114355 114488 114641 114908 114999 115386 115580 115833 116057 116106 116113 116150 116155 116220 116235 116273 116738 116823 116939 117029 117044 117054 117073 117124 117608 117633 117716 117816 117834 117994 118169 118199 118380 118420 118453 118454 118667 118794 118823 119068 119112 119236 119835 119977 120138 120404 120459 120649 121216 121286 121418 121434 121893 122120 122130 122240 122839 122879 122924 123222 123396 123498 124302 124341 124466 124608 124617 124661 124689 124746 125176 125247 125345 125409 126050 126134 126159 126173 126279 126300 126464 126931 127126 127213 127245 127287 128051 128119 128127 128205 128515 128521 128652 128700 129318 129455 129617 129640 129760 130521 130681 131406 131444 131594 131878 132018 132410 132477 132801 132882 133263 133924 133962 134111 134231 134823 134857 135534 135778 135879 136063 136366 136723 136848 137068 137313 137744 137980 138066 138240 138641 138828 139958 139986 140105 140958 140990 141008 141279 141402 141518 141718 141906 142361 142385 142516 143513 144323 144725 144973 145612 145709 146165 148982 149248 149256 149651 149878 150587 150907 151257 151387 151895 151900 152301 152636 152779 154249 154661 154850 155316 155824 156631 157020 157076 157235 157263 157340 157569 160473 161115 161354 161387 161445 163720 163752 164207 165117 165656 167001 167809 168409 169624 170871 171394 173058 174853 174965 177238 177466 177980 178711 179933 180888 181732 181897 182276 182617 186182 186825 188902 189016 189068 196517 197560 199360 200132 201527 204820 205402 206607 217775 230998 234297 257990
``

``
width 36 (300 walks, sum 97252475):
29920 34541 45381 53747 54990 64446 65058 65283 83431 85479 86043 88133 89139 98686 99251 103862 104394 111452 113612 115725 119848 120598 121122 121825 122000 126266 126652 128589 129278 132718 133314 136652 137052 138242 139357 143692 147756 155229 155487 155971 156809 158078 158686 158811 159911 160570 163497 164744 167848 168343 170910 171047 177322 178347 179996 182264 186968 188312 188995 191399 192287 192302 193078 193996 194779 196128 196597 196611 198235 199420 201122 202656 202838 205237 205272 209110 209593 210837 211940 213011 213352 214718 214958 216941 218108 218243 218533 219940 220773 221468 224780 228369 231542 232633 235412 235727 236915 237827 237918 238278 238654 240211 240306 240657 242589 242673 244482 244794 246834 246959 247494 247903 249885 250194 250947 255581 256148 256453 259304 261436 263004 265613 266193 266372 266825 267749 268493 269050 272209 272343 272700 273775 273841 274137 275072 278058 278234 279953 280137 283235 286278 286526 287517 288294 289835 289880 290224 291087 292543 297398 298638 299117 304340 304699 305655 306403 310836 312132 312957 314017 318768 319224 320062 320652 322402 326087 329756 330021 334010 335919 339662 341085 342934 343287 344404 346201 356588 357082 358379 359225 359407 361849 362716 364055 370806 371047 371517 371529 371682 374346 374388 375873 375880 377055 381711 384755 385346 386054 387242 387308 387510 387596 388277 389762 391172 392003 399389 399977 400569 400937 401581 401743 405474 409225 409779 410305 412260 412621 417704 418423 420030 420109 421116 421643 424389 424653 425357 425757 427494 431590 432686 434910 435593 437079 440172 441748 449083 450745 456991 458168 458283 461518 463322 469589 470710 472648 475479 478475 482226 484343 485845 486265 491289 500508 503994 507624 508632 511127 512251 512374 513229 514814 516726 517557 520804 527233 528668 532871 533783 536236 536554 538268 541904 542861 543403 545020 549200 549954 550772 551819 555104 567458 577690 580908 592087 594869 610701 621154 624654 631282 642185 642600 661711 667824 683467 694044 734988 750755 770143 1027304
``
