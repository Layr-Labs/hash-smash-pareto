# Proof: generic birthday (distinguished-point rho) collision, Orchard Poseidon r=15

Target `poseidon-orchard-r15-prefix-v1` (Pallas P128Pow5T3, ConstantLength<2>, halo2_poseidon 0.2.0 pinned constants; 8 fixed full rounds around 15 partial rounds; digest = state[0], whole element compared). Attack class `ordinary-collision`. Cost model `orchard-field-ram-v2`: every field addition/subtraction/multiplication and every 256-bit word primitive is charged 1/C target compressions with C = 216 + 21*15 = 531; exponentiation/inversion are charged as their counted constituent operations. No asymptotic-only claim is made; every bound below is a finite number at the actual dimensions.

## 1. The claim

* `time_log2` = 127.20163 `target-compressions` (exact Decimal 127.201624; rounded **up** at 5 decimals).
* `memory_log2_bytes` = 20 (reviewed total 1,048,518 bytes < 2^20; normalized memory penalty max(0, 20 - 20) = 0).
* `success_probability` = 0.39 at the filed walk budget (Section 5 for the random-function lemma, Section 6 for the measured hazard transfer).
* `preprocessing_log2` = 32; all offline derivation (constants, budget solve, the measurement campaign) is bounded by 2^41 word operations and charged **inside** `time_log2` (Section 9, ledger line "offline derivation").
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

## 3. The step program (580 charged operations per step)

| block | ops | breakdown |
| --- | ---: | --- |
| rounds 0-2, folded entry | 27 | 6 (t_k = QQ_k*x + Ptilde_k) + 9 (three S-boxes t_k^5) + 12 (round-2 linear layer in scaled bases) |
| round 3 (scaled bases) | 24 | 3 add + 9 S-box + 12 linear |
| entry rescale into partial basis | 2 | 2 mult (GAMMA_0 sig_0, GAMMA_2 sig_2; lane 1 already scaled) |
| 15 partial rounds | 255 | 17 each: 1 add (sig_0 + kappa0hat_i), 3 S-box (t0h), 7 mult + 6 add (sig'_j = MH0_j t0h + sig_1 + MH2_j sig_2; lane-1 coefficient exactly 1 in rows 0 and 2) |
| rounds 60-62 (scaled bases) | 72 | 24 each: 3 add + 9 S-box + 12 linear; partial-phase exit constants folded into round 60 |
| round 63 (output lane only) | 16 | 3 add + 9 S-box + 2 mult + 2 add (row B63R with LAMBDA folded; lane-1 coefficient 1) |
| dp test (lane-0 mask, threshold compare) | 2 | word primitives |
| loop control (counter increment, branch compare) | 2 | word primitives |
| state traffic (x load, 3 ptilde loads, x store, 1 spare) | 6 | word primitives |
| constant-table loads (QQ/_B2/_C3/_B3/GAMMA; per partial round KAPPA0HAT + MH0/MH1/MH2; rounds 60-62 C/B; round 63 C63/B63R) | 172 | word primitives |
| **total per step** | **580** | |

Derivation of the 12 state/control word primitives per step: load x (1), load the three ptilde lanes (3), dp mask (1), dp threshold compare (1), dp decision branch (1), counter increment (1), loop compare (1), loop branch (1), store the output lane to x (1) = 12 exactly (comparison and conditional branch are separate primitives). The cost model prices one field addition, subtraction or multiplication at 1/C flat (computation_model: no operand-fetch toll), and prices a load or store as the executed word primitive. Constant traffic: every constant-table access executed by the step program of Appendix A is a load - rounds 0-2: QQ (3) + _B2 rows (6) = 9; round 3: _C3 (3) + _B3 rows (6) = 9; entry rescale: GAMMA[0], GAMMA[2] = 2; each of the 15 partial rounds: KAPPA0HAT[i] (1) + MH0[j] (3) + MH1[1] (1) + MH2[j] (3) = 8; rounds 60-62: C row (3) + B rows (6) = 9 each, 27; round 63: C63 (3) + B63R[0], B63R[2] (2) = 5 - for a total of 52 + 8*15 = 172 loads per step, charged in the ledger row above. The ptilde fold itself (QQ, PP, C[2]: 9 loads) runs once per attempt and is inside the setup line of Section 7.

The partial rounds run in the fixed scaled basis MB = (MDS[0][1], 1, MDS[2][1]) * M4[1], chosen so rows 0 and 2 have lane-1 coefficient exactly 1; all per-round constants are kappa-folded into the single addition per round (the kappa recursion kappa(i+1)_j = MH1_j kappa_1 + MH2_j kappa_2 + Khat_j is exact and offline). Bases chain M3 (after round 2), M4 (after round 3), MB (partial phase), M61..M63 (rounds 60-62). The step program runs rounds 4..18 as the selected partial rounds of this target; every other block is round-independent.

The step program equals digest(message(x + rho0)) * LAMBDA on 64 of 64 random (x, rho0) trials against the organizer's trusted reference permutation at r=15 (`--selftest`), and its per-step ledger totals exactly 580. Every field multiplication/addition and every word primitive in the actual code path is counted; no operation is uncharged.

## 4. The search: one trail, distinguished points, index table, recovery

A walk value is distinguished iff its low 128 bits are < 38176; the threshold is below 2^16, so the low 16 bits determine the low 128 bits among dp values and a stored key (high 126 bits, low 16 bits) is injective on dp values. Exactly D = (2^126 + 1) * 38176 of the p field elements are distinguished (p = 2^254 + c with c = p mod 2^128 >= 38176), theta = D/N in [10^-33.95009453, 10^-33.95004902] (conditioning bounds theta_lo = (D - 2^128)/N, theta_hi = D/(N - 2^128)).

Packed table layout and per-event charge (finite derivation). The table is an open-addressed array of MCAP = 27,413 slots of one aligned 32-byte word each, plus one 16-bit side field per slot; the slot of a dp value is its low 16 bits taken modulo 27,413, collisions resolved by linear probing, and the stored key (high 126 bits, low 16 bits) is compared in full, so no false match is possible. One probe costs at most 5 word primitives (load the 32-byte word, shift out the high 126 bits, key compare, probe branch, index increment); the terminal side-field compare, the slot arithmetic and the insertion writes (store entry word, store side field, update the entry count) cost at most 16 word primitives. A scan is at most one full table pass: 27,413 probes, hence at most 5*27,413 + 16 = 137,081 word operations per dp event. Events are deterministic in count: every arriving dp value either inserts (at most MCAP = 27,413 inserts, the algorithm abandons at the cap) or is the first repeat, which returns; so at most 27,414 events occur per attempt and the dp-table charge 27,414 * 137,081 = 3757938534 word operations is a deterministic upper bound (the expectation at the mean load 20,037/27,413 would be far smaller; no expectation is charged). The two recovery index lookups (the largest stored index below a, and the largest stored index at or below q) are single scans of the same entry words - the trail index is inside each 32-byte entry word - at at most 4 word operations per entry (load, index compare, branch, iterator advance), 4*27,413 + 16 = 109,668 each, charged in the recovery line of Section 7. No auxiliary ordered index list exists in the layout or the algorithm; the runtime `Counters` of Appendix B instruments the reference implementation's dict probes, and every filed bound charges the deterministic caps above, which dominate those counts.

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
* Scope: target poseidon-orchard-r15-prefix-v1, inputs on the line of Section 2, one search with the parameters of Section 4 (walk budget S1 = 178597435891429200878561991096629710601). Not claimed for other round counts or budgets.

Budget and tolerance. Within the hazard-multiplier family (the real map's per-step repeat hazard is a constant multiple c of the random-function hazard), the repeat term of the lemma scales as exp(-c x) with x = n(n+1)/(2p); the other failure terms are unchanged. The filed budget n1 is the smallest trail budget at which the premise survives **every hazard factor c >= 0.90**: at n1 (x = 0.55043), the success at the floor c = 0.90 is exactly 0.39 by construction, and the random function (c = 1) reaches 0.4226. The floor 0.90 lies **below the pooled 95% profile-likelihood lower bound 0.9911 (all 15900 walks over the six widths; the hazard-multiplier family has the single parameter c, and the pooled interval is its estimate)**, so the reduced-width evidence dominates the tolerance. The per-width cells of the table are diagnostics of the single-multiplier model (no slope across widths); the smallest single-cell lower bound is 0.9189 (printed, not load-bearing), as in the incumbent's accepted design.

Evidence (participant-run; the organizer-run experiment is Section 10; the complete per-walk raw data is printed in Appendix D and is byte-reproducible from the deterministic seeded harness, `python3 measure_rounds.py 15`): first-repeat walks on the real r=15 map truncated to w bits (the truncated map is the birthday model at width w), fresh (rho, start) per walk, every walk run to its exact first repeat, 15900 walks over six widths, exact discrete first-repeat likelihood P(L=l|m) = (m*l/N) * prod_(j<l) (1 - m*j/N) (series-summed with bounded tail), profile-likelihood 95% intervals:

| width w | walks | hazard multiplier m-hat | 95% profile-likelihood CI | series tail bound |
| ---: | ---: | ---: | --- | ---: |
| 16 | 1200 | 1.0605 | [1.0018, 1.1215] | 2.6e-06 |
| 20 | 6000 | 1.0038 | [0.9787, 1.0294] | 5.0e-08 |
| 24 | 6000 | 1.0053 | [0.9801, 1.0310] | 0.0e+00 |
| 28 | 1200 | 1.0017 | [0.9461, 1.0594] | 0.0e+00 |
| 32 | 1200 | 0.9754 | [0.9212, 1.0316] | 0.0e+00 |
| 36 | 300 | 1.0312 | [0.9189, 1.1523] | 0.0e+00 |

Pooled multiplier 1.0066, 95% profile-likelihood CI [0.9911, 1.0223]; the per-width estimates are consistent with a constant multiplier across widths (no slope). Seeds and stopping rule: each walk draws rho0 uniform on 254 bits and a start uniform on 2^w from an independent seeded stream (Appendix C, per-chunk seeds); every walk ran to its first repeat, none was dropped, repeated or selected; there is no stopping rule. The exact discrete law is used throughout; no exponential or Gamma approximation of the first-repeat index enters the estimates.

Sensitivity at the filed budget S1 (repeat term x = 0.55043; other eps terms 6.6e-04):

| hazard factor c | 1.0223 (pooled upper) | 1 (random) | 0.9911 (pooled lower) | 0.9212 (w=32 lower) | 0.9189 (smallest single cell lower (w=36)) | 0.90 (floor) | 0.85 (below floor) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| success at S1 | 0.4297 | 0.4226 | 0.4198 | 0.3971 | 0.3963 | 0.3900 | 0.3730 |

Extrapolation: from widths 16 to 36 at r = 15, where the multiplier is measured, to width 254 at r = 15, by H1. The measurements show that the random-function first-repeat law holds on the real round function at every measured width, and the pooled 95% lower bound lies above the tolerance floor (the per-width cells are diagnostics of the single-multiplier model); they do not bound the multiplier at full width. The full-width first repeat cannot be observed at feasible cost, so the transfer is the premise itself.

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
per-step ops                 = 580  (listing in Section 3)
walk ops    S1 * 580  = 103586512817028936509565954836045232148580
recovery    3*(gmax+16) evaluations at 580 + 6 each, plus 2 recovery scans
            (<= 4*27,413 + 16 word ops each: load, compare, branch, advance) = 309514144416809282214190979181984641580
dp-table    <= 27,414 events (cap; mean 20037) * <= 137,081 word ops
            (worst-case probe+insert: <=5 ops/probe * <=27,413 probes + 16) = 3757938534
PRG          2 coin draws * 264 word ops = 528
setup + fifth roots        = 2000 + 2286
offline derivation         = 2^41 word ops (Section 9; constants + budget solve +
            Floyd measurement campaign; charged, 4141286734 compressions)
total ops                  = 103896026961445745791780145817429997989060
units = total / C, C = 531 = 195661067724003287743465434684425608265.64971751412429378531073446327683615819209
time_log2 = log2(units)     = 127.201624
filed                       = 127.20163 (rounded up at 5 decimals)
```

For reference against the frontier: this target's published entry 4ae6c95 (Jbenisek) is an algebraic collision algorithm filing time_log2 61.03269 with 67.87 bits of memory penalty (normalized cost 128.90); the organizer nominal reference `poseidon-orchard-r15-nominal-v2` is 127.0 (not a qualified baseline). This entry files 127.20163 with zero memory penalty: 1.6984 bits under the published normalized frontier at the same round count. The tight random-function convention at r=15 scores 127.12582; the 0.0758 bits over tight are the honest price of the detection-window/recovery convention plus the 0.90 tolerance floor (the incumbent's own generic entries at r=22 and r=24 file the tight n0 with no real-map transfer evidence; this entry pays for the transfer).

## 8. Memory

Peak live set: the dp table 27,413 entries * 32 bytes (877,216) + 27,413 side fields * 2 bytes (54,826) + one 32-byte start word = 932,074 bytes, plus one allowance of 116,444 bytes for every other live item (code, nonuniform constants, registers, PRG state, transient working state and I/O buffers) = 1,048,518 bytes < 2^20 = 1,048,576 (58 bytes margin). The reference implementation of Appendix B (~18 KB source plus ~6 KB of derived tables, standard library only) fits the allowance with wide margin; its whole working state besides the table, the start word and the message/output buffers is procedure locals. Every table item is one aligned 32-byte word: entry k at TAB0 + 32k holds (high 126 bits of the dp value) OR (its index < 2^128); the side word holds the 16-bit low part. Lookups extract the high part and compare, then the side field; reconstruction shifts the high part back and appends the side field (threshold < 2^16 makes this exact). The trail index is stored inside each 32-byte entry word and the recovery lookups scan the entry words directly, so no auxiliary ordered index list (nor any other structure beyond the counted items) is live: 1,048,518 bytes is the entire peak live set. Memory penalty max(0, log2(1,048,518) - 20) = 0; filed memory_log2_bytes = 20.

## 9. Preprocessing (inside time)

All constants (the line constants of Section 2; the scaled bases M3, M4, MB; GAMMA; MH0/MH1/MH2; the kappa-folded partial constants KAPPA0HAT and KAPPA_EXIT; the folded exit constants at round 60; C60..C63, B60..B62, B63R; LAMBDA) and the budget solve (80-digit Decimal bisections on n0 and n1) are offline. Their derivation, together with the participant's 15,900-walk H1 measurement campaign (the advice that fixes the 0.90 tolerance floor and the printed intervals), is construction/preprocessing under orchard-field-ram-v2 and is bounded by 2^41 word operations (constant derivation: 64 rounds of short reciprocal/fifth-power chains, a few hundred word operations each; budget solve: a few hundred 80-digit Decimal exp/log evaluations < 2^10 each; campaign: 258,754,228 first-repeat steps detected with Floyd cycle detection at at most 6 evaluations per measured step - O(1) working memory, no retained per-walk set - so at most 6 * 258,754,228 evaluations * 580 < 2^41), charged inside time_log2 in the ledger line "offline derivation" (2^41/531 = 4141286734 compressions), and declared as preprocessing_log2 = 32 (= ceil(log2(4141286734))). The measurement analysis of Section 6 is charged inside the same 2^24 cap.

## 10. Organizer experiment (declared)

`lowbits-birthday` (python-message-pairs-v1, digest-xor-mask on the first 14 bits): per trial, at most 1200 fresh canonical 64-byte messages derived deterministically from the supplied seed; the program returns a pair whose r=15 digests agree on the masked bits. Local run of the same event: 256/256 verified pairs, byte-identical on repeat. Every eighth trial the same program additionally runs one w=16 truncated first-repeat walk on the filed walk map (fresh (rho0, start) drawn from the same trial seed, 4096-step cap) and reports its length and cap flag as untrusted participant observations: 32 organizer-executed walks at width 16 under fresh organizer seeds, byte-reproducible (the runner replays the identical request twice and requires byte-identical output). These observations corroborate the width-16 cell of the participant campaign (Section 6) under organizer execution; the runner labels them untrusted (it verifies no internal semantics), they are a witness and not the estimate. The checked event is a reduced-width witness on the digest only; neither establishes H1, the cost bound, or the success probability (a 14-bit event cannot separate hazard multipliers near 0.5 from 1).

## 11. Verification

The step program, the search with its recovery, the budget solve, the measurement harness and the analysis sources are embedded verbatim as appendices below (A: `myrho_r15.py` - step program at R=15, line and tables, selftest; B: `attack_r15.py` - the filed single-trail search, recovery, exact plan, reduced-width end-to-end selftest, H1 measurement mode; C: `measure_rounds.py` + `analysis_round.py` - the r=15 H1 evidence and exact likelihood intervals). All are standard-library-only Python 3, deterministic given their seeds. Exercised locally: `myrho_r15.py --selftest` 64/64 against the trusted reference at r=15; `attack_r15.py --selftest` 64/64 plus the reduced-width end-to-end searches (any trial reaching the test gap cap is abandoned, per the lemma's gap term); `attack_r15.py --plan` prints the exact ledger of Section 7; the measurement and analysis of Section 6 ran to completion on the real r=15 map with the per-round seeds.

## Appendix A: `myrho_r15.py` (line, tables, step program at R=15, selftest)

Line construction and constants (identical to the r=23 filing; the line, the
bases and LAMBDA are round-independent), the counted `step()` program running
partial rounds 4..18, and `--selftest` (64 random (x, rho0) trials against
the trusted reference at R=15).

```python
#!/usr/bin/env python3
"""r=15 Orchard Poseidon generic birthday attack: distinguished-point trail rho.

Standard library only.  The step program counts every field operation it runs.

Offline conventions (all constants precomputed from the pinned deployed constants):
- Rounds 0..2: entry state and round-2 constants folded (t_k = QQ_k x + Ptilde_k);
  round 2 runs in scaled bases (linear layer 12 ops), leaving basis M3.
- Round 3: scaled-basis full round (24 ops), leaving basis M4.
- Rounds 4..18: partial rounds in the fixed basis m = (M01,M11,M21)*M4[1]
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
R = 15
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
# rescale 2; partial rounds 17 each; round 63: 16; dp test + loop control +
# state traffic 12 (x load 1, 3 ptilde loads, dp mask 1, dp threshold compare
# 1, dp decision branch 1, counter increment 1, loop compare 1, loop branch 1,
# x store 1 = 12 exactly; comparison and conditional branch are separate
# primitives); constant-table loads 52 + 8r (rounds 0-2: QQ 3 + _B2 6 = 9;
# round 3: _C3 3 + _B3 6 = 9; entry: GAMMA 2; each partial round: KAPPA0HAT 1
# + MH0 3 + MH1[1] 1 + MH2 3 = 8; rounds 60-62: 9 each = 27; round 63:
# C63 3 + B63R 2 = 5).
OPS = {'block02': 27, 'full': 24, 'pentry': 2, 'partial': 17, 'r63': 16,
       'dp': 12, 'c02': 9, 'c3': 9, 'centry': 2, 'cpart': 8, 'c60': 9, 'c63': 5}
STEP_OPS = (OPS['block02'] + OPS['full'] + OPS['pentry'] + R * OPS['partial']
            + 3 * OPS['full'] + OPS['r63'] + OPS['dp']
            + OPS['c02'] + OPS['c3'] + OPS['centry'] + R * OPS['cpart']
            + 3 * OPS['c60'] + OPS['c63'])


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
    led.word += OPS['c02']           # QQ 3 + _B2 6 constant loads
    # round 3 (scaled bases)
    tau = [(sig[k] + _C3[k]) % P for k in range(3)]; led.add += 3
    y = [_sbox(tk, led) for tk in tau]
    sig = [(_B3[j][0] * y[0] + y[1] + _B3[j][2] * y[2]) % P for j in range(3)]
    led.mult += 6; led.add += 6
    led.word += OPS['c3']            # _C3 3 + _B3 6 constant loads
    # enter the partial basis (lanes 0 and 2 rescale; lane 1 already there)
    sig = [sig[0] * GAMMA[0] % P, sig[1], sig[2] * GAMMA[2] % P]
    led.mult += 2
    led.word += OPS['centry']        # GAMMA[0], GAMMA[2] loads
    # partial rounds 4..18 (lane-1 coefficient 1 in rows 0 and 2)
    for i in range(R):
        t0 = (sig[0] + KAPPA0HAT[i]) % P; led.add += 1
        t0h = _sbox(t0, led)
        sig = [(MH0[j] * t0h + (sig[1] if j != 1 else MH1[1] * sig[1])
                + MH2[j] * sig[2]) % P for j in range(3)]
        led.mult += 7; led.add += 6
        led.word += OPS['cpart']     # KAPPA0HAT 1 + MH0 3 + MH1[1] 1 + MH2 3
    # rounds 60..62 (scaled bases, exit constants folded at 60)
    for cB, c in ((B60, C60), (B61, C61), (B62, C62)):
        tau = [(sig[k] + c[k]) % P for k in range(3)]; led.add += 3
        y = [_sbox(tk, led) for tk in tau]
        sig = [(cB[j][0] * y[0] + y[1] + cB[j][2] * y[2]) % P for j in range(3)]
        led.mult += 6; led.add += 6
        led.word += OPS['c60']       # C 3 + B 6 constant loads (per round)
    # round 63 (output lane, walk scale folded)
    tau = [(sig[k] + C63[k]) % P for k in range(3)]; led.add += 3
    y = [_sbox(tk, led) for tk in tau]
    out = (B63R[0] * y[0] + y[1] + B63R[2] * y[2]) % P
    led.mult += 2; led.add += 2
    led.word += OPS['c63']           # C63 3 + B63R 2 constant loads
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

## Appendix B: `attack_r15.py` (the filed search, recovery, exact plan, selftests)

`full_search` is the filed algorithm of Section 4 (one trail, distinguished
points, index table, gap-bounded lockstep recovery) with the filed literals
WALK/DETECT/GMAXC at R=15; `plan` derives and prints the exact ledger of
Section 7 (80-digit Decimal, per-round step cost 578 and
C = 531); `--selftest` runs the 64-trial step check and the
reduced-width end-to-end searches of Section 4 at R=15.

```python
#!/usr/bin/env python3
"""r=15 Orchard Poseidon generic birthday attack: full program.

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
- Rounds 4..18: partial rounds in the fixed basis MB = (M01,M11,M21)*M4[1]
  (lane-1 row coefficient exactly 1 in rows 0 and 2), constants kappa-folded
  into one addition per round: 17 ops each.
- Rounds 60..62: scaled-basis full rounds (24 ops each), exit constants
  folded at 60.
- Round 63: output lane only; walk scale LAMBDA folded into the row so the
  lane-1 coefficient is 1: 16 ops.
- dp test + loop control + state traffic: 12 word ops per step (x load 1, 3 ptilde loads, dp mask 1, dp threshold compare 1, dp decision branch 1, counter increment 1, loop compare 1, loop branch 1, x store 1 = 12 exactly; comparison and conditional branch are separate primitives); constant-table loads 52 + 8r word ops per step (rounds 0-2: 9; round 3: 9; entry: 2; each partial round: 8; rounds 60-62: 27; round 63: 5); table work charged per
  distinguished event.
"""
import argparse
import hashlib
import json
import math
import random
from decimal import Decimal, getcontext
from pathlib import Path

import myrho_r15
from myrho_r15 import (P, ref_digest, message, step, Ledger, walk_ptilde,
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
    (the tolerance floor, below the pooled 95% lower bound) the same
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

    step_ops = Decimal('580')
    rec_evals = 3 * (gmax + 16)                # recovery cap: 3 gmax charged
    rec_ops = (Decimal(rec_evals) * (step_ops + 6)
               + Decimal(2 * (4 * 27413 + 16)))    # + two recovery scans: 4 word ops per entry
    dp_events = int((Decimal(S1) * theta_hi).to_integral_value(
        rounding='ROUND_CEILING'))
    table_events = 27413 + 1                  # deterministic: first repeat ends the walk
    table_per_event = 5 * 27413 + 16           # worst-case probe+insert: 5 word ops per probe
                                               # (load, shift, key compare, branch, index increment)
    table_ops = Decimal(table_events) * Decimal(table_per_event)
    prg_ops = Decimal(2 * 264)                 # two coin draws
    setup = Decimal(2000)
    roots = Decimal(2286)                     # fifth roots for both messages
    prep = Decimal(1 << 41)                  # constants + budget solve + Floyd measurement campaign
    total = (Decimal(S1) * step_ops + rec_ops + table_ops + prg_ops + setup
             + roots + prep)
    units = total / Decimal(531)
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
        'per_step_ops': '580',
        'walk_ops': str(Decimal(S1) * step_ops),
        'recovery_ops': str(rec_ops),
        'table_ops': str(table_ops), 'prg_ops': str(prg_ops),
        'dp_events': dp_events,
        'total_ops': str(total), 'C': 531,
        'units': str(units), 'time_log2': str(score),
        'time_log2_float': float(score),
    }, indent=2))


# --------------------------- H1 measurements (evidence) --------------------
def measure(widths=(16, 20, 24, 28), walks=120, seed=0x5EED2EED):
    """Reduced-width first-repeat measurements on the real r=15 map."""
    rng = random.Random(seed)
    data = {}
    for w in widths:
        mask = (1 << w) - 1
        lens = []
        for _ in range(walks):
            rho0 = rng.randrange(0, 1 << 254)
            v = rng.randrange(0, 1 << w)
            ptilde = walk_ptilde(rho0)

            def F(z, p=ptilde):
                return step(z, p, Ledger()) & mask
            # first repeat via Floyd cycle detection: O(1) memory; the
            # first repeat of a rho-shaped walk is exactly tail + cycle
            t = h = v
            t = F(t); h = F(F(h))
            while t != h:
                t = F(t); h = F(F(h))
            m = t
            lam = 1
            u = F(m)
            while u != m:
                u = F(u); lam += 1
            t = h = v
            for _ in range(lam):
                h = F(h)
            mu = 0
            while t != h:
                t = F(t); h = F(h); mu += 1
            lens.append(mu + lam)
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
          f'per-step={led.mult + led.add + led.word:.2f} (budget 580)')
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
        myrho_r15.selftest()
```

## Appendix C: `measure_rounds.py`, `analysis.py` and `analysis_round.py` (H1 evidence)

`measure_rounds.py` runs the per-round measurement suite of Section 6: first-repeat
walks on the real r=15 map truncated to w bits (widths 16..36, fresh
(rho, start) per walk, 12 parallel chunks, per-chunk seeds), each walk's exact
first repeat detected with Floyd cycle detection at O(1) working memory (the
first repeat of a rho-shaped walk is exactly tail + cycle length; no retained
per-walk set). `analysis.py` holds
the exact discrete first-repeat likelihood (series-summed with bounded tail) and
the per-width and pooled profile-likelihood intervals; `analysis_round.py`
applies them to `measurements2_r15.json` and writes `analysis_r15.json`.

```python
#!/usr/bin/env python3
"""Per-round H1 measurements: first-repeat walks on truncated r-round maps.

Runs the v5 suite (same JOBS walk counts, widths 16..36, fresh
(rho, start) per walk, 12 parallel chunks) for each round r in 15..22,
against the per-round modules myrho_r{r} (generated from myrho.py with
R replaced). Writes measurements2_r{r}.json (same format as
measurements2.json: {str(w): sorted first-repeat lengths}).
Each walk detects its exact first repeat with Floyd cycle detection
(O(1) working memory: the first repeat of a rho-shaped walk is exactly
tail + cycle length); the (rho, start) draws are unchanged, so the
output equals the set-based walk byte for byte.

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

        def F(z, p=ptilde):
            return mod.step(z, p, mod.Ledger()) & mask
        # first repeat via Floyd cycle detection (O(1) working memory):
        # the walk enters a cycle of length lam after a tail of length mu,
        # every repeated value lies on the cycle, and the FIRST repeat is
        # x_(mu+lam) = x_mu, so the first-repeat length is exactly mu + lam.
        t = h = v
        t = F(t); h = F(F(h))
        while t != h:
            t = F(t); h = F(F(h))
        m = t
        lam = 1
        u = F(m)
        while u != m:
            u = F(u); lam += 1
        t = h = v
        for _ in range(lam):
            h = F(h)
        mu = 0
        while t != h:
            t = F(t); h = F(h); mu += 1
        out.append(mu + lam)
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

## Appendix D: raw first-repeat data (r=15, participant-run, deterministic seeds)

Per walk: the exact step count of the first repeat on the real r=15 map truncated to w bits (fresh (rho, start) per walk, seeded PRNG, seeds fixed in Appendix C `measure_rounds.py`: 0x5EED0000 + w*100 + chunk over 12 chunks). The multiset below is the complete raw data; the likelihood of Appendix C consumes exactly this multiset. Total 15900 walks, 258,754,228 measured walk steps; charged word operations at most 6 evaluations per measured step at the r=15 step cost, 897,359,662,704 <= 2^40, inside the offline line of Section 9 (Floyd cycle detection, O(1) working memory). `python3 measure_rounds.py 15` regenerates `measurements2_r15.json` byte-identically.

``
width 16 (1200 walks, sum 375964):
9 14 21 23 25x2 31 32 34 35 36x2 38x3 39x2 40x3 42x2 43x3 47x3 48x2 50x2 53 57 58 60x2 64 66 67 69 70 71x2 72x2 74x2 75 76 78 79x4 80 81 82x4 83x2 86x2 88 89x2 90 92x2 93 94 95 96 97 98x2 99x3 100 101x3 102 103x3 104x2 105x3 106 107x3 111 112x3 113x3 114x2 115 116x3 117x2 118x2 119x2 120x5 121x2 122x3 123 124x2 125x2 126x2 128x2 130x3 131x2 132 133x2 135x3 136 138x2 139x2 141 143x2 144x4 145x2 146x2 147x6 148x2 149x2 150x5 151x3 152x2 153x5 154x2 155x3 156x6 157 158x4 159x3 160 161x3 162x2 163x2 164x5 165x4 166x2 167x5 168x2 169 170x2 171 172x3 173x3 174x7 176x3 177x3 178 179x3 180x4 181x4 182x3 183x2 185x2 186x3 188x2 189x2 190x2 191 192x5 193x4 194x6 195 197x9 198x2 199x6 200x5 201 202x5 203 204x4 205x4 206x5 207x4 208 209x4 210x2 211x3 212x3 213x4 214x2 215x3 216x4 217x5 218x2 219x3 220 221 222 223x2 224x3 225x2 226x4 227x3 228x3 229x2 230x2 231x3 232x4 233x2 234x5 235x3 236x4 237x5 238x3 239x2 240x4 241x2 242x6 243x2 244x2 246x2 248x2 249x2 250 251x2 252x6 253 254x5 255x4 256 257x5 258x2 259x3 260x2 261x3 262 263x3 264x2 265x5 267x5 268x7 269x4 271 272 273x2 274x3 275x3 276x5 277x4 278x2 279x3 280x8 281x4 282x3 283x4 284x4 285x2 286x3 287x3 288x6 289x2 290 291x3 293x6 294x6 295x5 296x6 297x5 298x4 299x3 300 301x2 302 303x4 306x3 307 309x6 310x3 311x3 312 313x2 314x4 315x5 316x2 317x5 318x2 321 322x4 323x3 324x2 325x6 326 327x3 328x3 329x2 330x3 331x4 332x5 333x3 334x3 335x2 336x3 337x3 338x3 339x2 340x2 341x2 342x3 343x2 344x3 345x4 346x2 347 348x2 349x2 350x2 351x4 352x3 353x3 354 355x2 356x5 357x3 358 359x2 360x5 361x2 362x3 364x3 365x3 366x2 367x7 368x3 370x4 371x2 372x4 373x3 375x3 377x6 378x2 379x5 380 382x3 383x3 384x3 385x2 386 387x5 388x2 389 390x4 391x2 393x4 394x5 396x5 397x2 398x2 399x3 400 401x2 403 406x3 407x3 408x2 409x4 411x2 412x2 413x2 414 415x3 417 418x2 419 420x4 421 422 423x2 425x4 428 429 430x8 431x2 432x2 433 434 435x2 436x4 438 439x3 440x2 441x2 442x3 444x3 445x2 446x2 447x6 448x2 449x2 451 453x4 454x3 456 457 458 459x4 460 461 462x3 464x2 465 466x3 467 468x2 470x2 472x3 473 475 476 477x3 478 479 481x2 482x3 483 484x2 485 486 488x2 489 490x2 492 493 495 496x2 497x3 499x6 500 501 502x4 503x2 505 507 509x2 510 511x2 512x4 513 518 520x2 523x3 524 525 526 528 529 530 532x2 535 537x4 538x2 539x2 540x3 543 545 546x2 547x2 548 550 552x2 554x2 556 558x3 559 563 565 567 568 570 572x2 574 577x2 578 579x3 582 584 585 586 587 588 594 595 598 599x2 600x3 601 605x2 608x2 609 611x3 614 615 616x2 622x2 623 624 626 635 637 639 641 642 643x4 646 649 650 652 653x2 656 658 659 663 665 668 669 672 674 676 678 680x2 682x2 683 684 689 692 694 699 707 716 718 722x2 737 759 763 809 848 849 854 870
``

``
width 20 (6000 walks, sum 7683326):
10 11 12 13 20 29 33x2 35 44 58 68 74 75 78 82 83 85 88x2 90 92 93x2 94x2 97x2 98x2 103x2 104 107 115 116x2 118 120 123 124 125 126 128 129x3 130x2 131 134x2 136x3 137x2 139 144 145 146x2 148 151x2 153 154x2 155x2 159x2 161x2 162 164 165 166x2 167 169x2 171x2 173 174 176 179 180 181 183 184x2 185 186x2 187 188 189x3 190x2 191x2 192x3 194 196x2 197 198x2 200 201 202x2 203 205x2 206 207x2 208x2 209x2 210 211 212 213x2 214x3 216 217x3 220 221x3 222 223 225x2 226x2 227x2 228 229x2 231x3 233x6 234 235 236 237x2 239x2 240x4 243 244x2 245 247x2 248 249x3 250 254x2 255 256 257x3 258 259x2 260x3 261x2 262 264 265x2 266 269 270x2 272x3 273 275 276 278x3 279 280x2 282x4 283x2 284 285 286 287 289x2 290x6 291 292x2 294 295x2 296 297x2 299x2 300 301x2 303 305x2 306x2 307 308x2 309x2 310 311x3 312 313 314 315x3 316 317x2 318x2 320x2 321x2 322x2 323x4 324x4 325x2 326 327x5 328 329x4 330x3 331 332 333x3 334 335x3 336x2 337x6 340x3 342x3 343x2 344 345 346 347x2 348x2 349x2 350x3 351x2 352x2 353x3 355x2 356x4 357x3 358x4 359 360x2 361 362 363x2 364x3 365 366x4 367x2 368x3 369x4 370x2 371x2 372x3 373x3 374x5 375x4 376x4 377x2 378x2 379x4 380x4 381x2 382x2 383 384x2 385x3 386 387x3 388 389 390x5 391 392x2 394 395 396x3 397x2 398x3 399x3 401 402x2 403 404x2 405 406x3 407x3 408x3 409 410x3 411x3 412x2 413x3 414x3 415x2 416x4 417x2 419x2 420x2 421x3 422 423x2 424x2 425x4 427x2 428x3 429 431x5 432x4 433x2 434x2 435x2 436x2 437x4 438x3 439 440x2 443x3 444 445x3 446x4 447x3 448x2 449x2 450x2 451x2 452x2 453 454x4 455x3 456x4 457x4 458x2 459x4 460x2 461x5 462x2 463x3 464 465x3 466x3 467x3 468x2 469x3 470x4 471x5 472x3 473x2 474 475x3 476x2 477x3 478x4 479x3 480x4 481x5 482 484x5 485 486x2 487x3 488x2 489x2 490 491x2 492 493x2 494x2 495x3 497x3 498 499x3 500x3 501 502 503 504x6 505x4 506x5 507x4 509x4 510x2 511 512x4 514x4 515 516x6 517x4 518 519x2 520x3 521x2 522x2 523x4 524x4 525x2 526x3 527 528 529 530x3 531x10 533x3 534x2 535x2 537x3 538x4 539x2 540 541x5 542 543x3 544 545x2 546x2 547x2 548x2 550 551 552x2 553x2 554x3 555x7 556x3 557x4 558x2 559x2 560x3 561x3 562 563x2 564x5 565x2 566x3 567x2 568x4 569x4 570 571x2 572x5 573 574x4 575x7 576x2 578x2 579x3 580x2 581x8 583 584x2 586x3 588 589x2 590x4 591x5 592x2 593x2 594x4 595 596 597x6 598x3 599 600 601x3 602x4 603x4 604x3 605x2 606x4 607x2 608x7 609 610x2 611x4 612x6 613x2 614x3 615x3 616 617x2 618x6 619 620x3 621x3 622x3 623x3 624x6 625x3 626 627x6 628x2 629x5 630 631x4 632x2 633x2 634x6 635x3 636x6 637x4 638x4 639x5 640x4 641x3 642 643x2 644x4 646x3 648 649 650x3 651x4 652x4 653x4 654x5 655x3 656x5 657x3 658x4 659 660 661x3 662x6 664x4 665x4 666x6 667x3 668 669x4 670x4 671x4 672x2 673x4 674x2 675x4 676x3 677x8 678 679x4 680x5 681x2 682x4 683 684x4 685x3 686x4 687x5 688x4 689x2 690x5 691x4 692x3 693x4 694 695x2 696 697x4 698x5 699 700x3 701x5 702x4 703x3 704x4 705x4 706 707x2 708x5 709x2 710 711x2 712x5 713x2 714x3 715x2 716x4 717x5 718x5 719x2 720x3 721x3 722x2 723x5 724x5 725 726x3 727x5 728x2 729x3 730x2 731x4 732x3 733x5 735x4 736x3 737 738x3 739x2 740x4 741x4 742 744x2 745 746x4 747x3 748x3 749 751x4 753x2 754 755x4 756x2 757x3 758x4 759x3 760x2 761x7 762x2 763x5 764x5 765x2 766x3 767x5 768 769x2 770 771 772x3 773 774 775x2 776 777x4 778x5 779x2 780x3 781x8 782x2 783x2 784x2 785x4 786x4 787x7 788 789x5 790x2 791x7 792x5 793x2 794x6 795x9 796x5 797x4 798x5 799 800x4 801x6 802x2 803x8 804x3 805x5 806x2 807x3 809 810x6 811x3 812x2 814x7 815x10 816x8 817x9 818 819x7 820x2 821x4 822x5 823x3 824x4 825x4 826x6 827x3 828x3 829x3 830x3 831x2 832x2 833x6 834 835x2 836x6 837x3 838x6 839x3 840x5 841x5 842x5 843x6 844x4 845x3 846x5 847x4 849x2 850x4 851x2 852x3 853x4 854 855x5 856x3 857x7 858x3 859x5 860 861x5 862x3 863 864x4 865x4 866x5 867x2 868x10 869x2 870x4 871x5 872x6 873x4 874x2 875x2 876 877x2 878x5 879x5 880x2 881 882x2 883x8 884x4 885x9 886x2 887x4 888x2 889x3 890x3 891x8 892 893x8 894x5 895x5 896x3 897x2 898 899x4 900x4 901x4 902 903x6 904x3 905x5 906x6 907x2 908x5 909x4 911 912x4 913x7 914x5 915x2 916x2 917x4 918x8 919x3 920x4 921x5 922x3 923x2 924x6 925x2 926x5 927x6 928x3 929x3 930x2 931x2 932x3 933 935x5 936x4 937x2 938x2 940x3 941x2 942x5 943x6 944x2 945x3 946x2 947x3 948x5 949x7 950x7 951x3 953x2 954x2 955x4 956x4 957x4 958x2 959x3 960x3 961x3 962x2 963x4 964 965x4 966x2 967 968x3 969x5 970x3 971x4 972x3 973x3 974x3 975x5 976 977x2 978x4 979x5 981x7 982x4 983 984 985x5 986x2 987x2 988x2 989x2 990x3 991x6 992x4 993x5 994x7 995x3 996x5 997x2 998x3 999x3 1000 1001x4 1002x5 1003x6 1004x2 1005x4 1006x5 1007x3 1008x4 1009x3 1010x2 1011x4 1012 1013x6 1014x5 1015 1016x4 1017x9 1018x7 1019x3 1020x5 1021x5 1022x3 1024x4 1025x5 1026x3 1027x4 1028x2 1029x3 1030 1031x4 1032 1033x5 1034 1036x4 1037x5 1038x3 1039x2 1040x3 1041x5 1042x7 1043 1044x5 1045x5 1046x5 1047x2 1048x2 1049x3 1050x3 1052x5 1053x3 1054x2 1055 1056x5 1057x2 1058x2 1059x2 1060x4 1061x3 1062x4 1063 1064x4 1065 1066x6 1068x6 1069x3 1070x2 1071x5 1072x3 1073x3 1074x4 1075 1076 1077x2 1078 1079x2 1080x6 1081x5 1082x4 1083x4 1084x3 1085x2 1086x6 1087x2 1089x5 1090x2 1091x4 1093x5 1094x3 1095x2 1096x2 1097x5 1098x7 1099x5 1100x5 1101x5 1102x5 1103x2 1104x3 1105x4 1106x8 1107x3 1108x5 1109x3 1110x5 1112x3 1113x5 1114 1115 1116x4 1117x4 1118x2 1119x5 1120x2 1121x5 1122x2 1123x2 1124x2 1125x2 1126x3 1127x4 1128x2 1129x2 1130 1131x4 1132x2 1133x2 1134x3 1135x3 1136x4 1137x11 1138x4 1139x3 1140x4 1141x4 1142x4 1143x3 1144x2 1145x2 1146x2 1147x4 1148x4 1149x6 1150x5 1151x2 1152 1153x3 1154x4 1155x5 1156 1157 1158x2 1159x5 1160x3 1161x3 1163x7 1164x3 1165x6 1166x5 1167x6 1168x3 1169 1170x2 1171x3 1172x6 1173 1174x3 1175x2 1176x3 1177 1178x5 1179x2 1180x2 1181x7 1182x4 1183x5 1184x3 1185x6 1186x4 1187 1188x5 1189x3 1190x4 1191x7 1192 1193 1194x2 1195 1196x5 1197x3 1199x4 1200 1201x2 1202x6 1203 1204x3 1205x4 1206x3 1207x3 1208x2 1209x5 1210x4 1211x5 1212x4 1213x5 1214x2 1215x2 1216x7 1217x4 1218x3 1219x2 1220x4 1221 1222x3 1223x5 1224 1225x4 1226x3 1227x4 1228x4 1229x5 1230x5 1231x6 1232x6 1233x9 1234x3 1235 1236x3 1237x3 1238x3 1239x2 1240x3 1241x3 1242x3 1243x4 1244x3 1245x2 1246x2 1247x4 1248x3 1250x7 1251x7 1252x4 1253x4 1254x3 1255x3 1256x4 1257 1258x5 1259x5 1260x6 1261x2 1262x5 1263x4 1264x3 1265x5 1266x4 1267x4 1268x2 1269x5 1270x3 1271x6 1272x6 1273x3 1274x3 1275x5 1276x3 1277 1278x2 1279x4 1280x2 1281x3 1282 1283 1284x3 1285x4 1286x3 1287x6 1289x4 1290x7 1291x2 1292x2 1293x7 1294x6 1295x3 1296x2 1297x6 1298x5 1299x3 1300x6 1301x3 1302x3 1303x6 1304x3 1305 1306x4 1307 1308x7 1309x2 1310x4 1311x5 1312x3 1313x2 1314x3 1315x5 1316x2 1317x2 1318x5 1319x2 1320 1321 1322x4 1323x2 1324x3 1325x4 1326x3 1327x9 1328x4 1329x2 1330x2 1331 1332 1333x3 1334x4 1335 1336x4 1337x2 1338x8 1339x3 1340x3 1342x4 1343x4 1344 1345x4 1346x6 1347 1348x2 1349x5 1350x6 1351x2 1352x5 1353x3 1354x2 1355x5 1357x3 1358x3 1359 1360x2 1361x2 1362x5 1363x6 1364x3 1365x3 1366x4 1367x4 1368x3 1369x2 1370x2 1371 1372 1373x2 1374x3 1375x3 1376x4 1377x5 1378x6 1379x2 1380 1381x5 1382x4 1383x2 1384x2 1385x3 1386x2 1387x4 1388x5 1389x6 1390x3 1391x3 1392x4 1393x6 1394x5 1395x4 1396x3 1397x2 1398x4 1399x4 1400x4 1401x2 1403x2 1404x3 1405x3 1406x7 1407x4 1408x4 1409x4 1410x4 1411x5 1412x2 1413x4 1415 1416x5 1417x6 1418x5 1419x2 1420x3 1421x2 1422x4 1423x3 1424x2 1425x2 1426x2 1427x2 1428 1429x5 1430x4 1431x2 1432x3 1433x2 1434x2 1435x2 1436x4 1437x5 1439x2 1440x3 1441x6 1442x2 1443x6 1444x2 1445x3 1446x3 1447 1448x5 1449 1450 1451x3 1452x4 1453x2 1454x3 1456x2 1457x3 1458x2 1459x4 1460 1461x2 1462x6 1463x5 1464 1465x3 1466 1467x5 1468 1469x3 1470 1471x2 1472x5 1473x4 1474x6 1475 1476 1477x2 1478x4 1479 1480x4 1481 1482x2 1483x3 1484x2 1485x6 1486x4 1487x2 1488x6 1489x2 1490 1491x4 1492x3 1493x2 1494x2 1495 1496x6 1498x4 1499x4 1500 1501x3 1502x2 1503x3 1504x2 1505x2 1506x3 1507x2 1508x4 1509x3 1510x3 1511x3 1512 1514x3 1515x4 1516x2 1517 1518x5 1519x3 1520x5 1521x3 1522x2 1523x4 1524x3 1525x2 1526 1527x3 1528 1529x4 1530x3 1531x4 1532x4 1533x2 1534x4 1535x2 1536x5 1537x4 1538x5 1539x3 1540x2 1541x5 1542x2 1543x3 1544x4 1545 1546x2 1547x5 1548x4 1549x2 1550 1551x2 1552x3 1553 1554x2 1555x8 1556x4 1557 1558x4 1559x10 1560 1561x5 1563x2 1564x3 1565 1566x2 1567x3 1568x3 1569x4 1570x2 1571x2 1572x2 1573x3 1574x6 1575x3 1576x3 1577x3 1578x4 1579x2 1580x2 1581x4 1582x2 1583x3 1584x2 1585x3 1586 1588x2 1589x3 1590x4 1592x3 1593x3 1594x2 1595x3 1596x3 1597x2 1598x4 1599x4 1600 1601 1602x4 1604x5 1605x4 1606x3 1607 1608x3 1609 1610x9 1611x3 1612x2 1613x4 1614x2 1615 1616x3 1617x4 1618x5 1620x3 1621x3 1622x4 1623 1624 1625x2 1626 1627x2 1628x2 1629x3 1630x2 1631x5 1632 1634x7 1635x5 1636x3 1637x3 1638x3 1639 1640x3 1641x4 1642x2 1643 1644x3 1645x4 1647x4 1648x4 1649x4 1650 1651x2 1652x4 1653x4 1655x2 1656x3 1657x2 1658x2 1659x3 1660 1661 1662x5 1663x4 1664x2 1665x2 1666x2 1667x4 1668x4 1669 1670 1671x4 1672 1673x4 1674 1675x3 1676x4 1677x3 1678 1679x4 1680x5 1681x5 1682x3 1683x3 1684x3 1685x3 1686x2 1687x3 1688x3 1689x2 1690x5 1691x4 1692x4 1693 1694x5 1695x3 1697x2 1698x4 1699x2 1700x2 1701x2 1702x3 1703 1704x3 1708 1709x3 1710x2 1711x3 1712 1713x3 1714 1715x3 1716x2 1718x5 1719x3 1720x2 1721x2 1722x3 1723x5 1724x2 1725 1726 1727x3 1728x4 1729x2 1730x2 1731x2 1732x2 1733 1734 1735 1737 1738 1739 1740x2 1741x2 1742 1743x5 1744x3 1745x4 1746 1747x2 1749x4 1750 1751x4 1753x3 1755x5 1756x2 1757x3 1758x2 1760x4 1761x2 1762 1763x2 1764x3 1765 1766x4 1768 1769 1770x7 1771x2 1772x2 1773x4 1774x3 1775x3 1776x3 1777 1778x2 1779x5 1780x2 1781x3 1782x3 1783 1784x5 1785 1786x3 1787x2 1788x3 1789x2 1790x5 1791x4 1793x2 1795 1796 1797x2 1798x2 1800x2 1801x2 1802x4 1803x5 1804x2 1807 1808x3 1809 1810 1811x2 1812 1813x4 1815x3 1816x2 1818x2 1819x4 1820 1821x4 1822x3 1823x4 1824x2 1825x5 1827x3 1828x5 1829 1830x3 1831 1832x3 1833 1835x2 1837x2 1838 1840x2 1841x2 1842x3 1843x5 1844x5 1845x2 1846x2 1847x5 1848x3 1849x2 1850x5 1851x3 1852x5 1853x4 1854x4 1855 1856 1857x3 1858 1860x2 1861 1862x3 1863x2 1864x5 1865x3 1866x5 1867x2 1868x3 1869 1870x2 1871x5 1872x2 1874x3 1875 1876x5 1877x2 1878x2 1879 1880x5 1881x6 1882x2 1883x2 1884x3 1885x3 1886 1887x5 1888 1891 1892x2 1894 1895 1896x3 1897 1898x2 1899x2 1900 1901x2 1902 1903x2 1904x2 1905x3 1906 1907x3 1908x2 1910x3 1911x7 1912x5 1913x3 1914 1915x2 1917x3 1918x2 1919 1920x4 1921x2 1922 1923 1924x3 1925x2 1926 1927 1928x2 1929x2 1931x3 1932 1933 1934x4 1935 1936x4 1938 1939 1940x2 1941x6 1942x2 1943 1944x2 1945 1947x3 1948 1951x3 1952x5 1953 1954x2 1955x3 1956x2 1957 1960x2 1961x3 1962 1963 1964 1967x3 1968x4 1969x2 1970x4 1971x3 1972x3 1973 1974x2 1975 1976x2 1977 1978x2 1979x2 1980 1981x2 1982x3 1983x3 1985x2 1986x3 1988 1989 1990 1991x3 1992x3 1993 1997 1998x5 1999 2000 2001 2002x3 2004 2005x3 2006 2007 2008x2 2009x2 2010 2011x3 2012x3 2013 2015 2016x2 2017 2019 2020 2021 2022 2023x3 2025 2026 2028 2029x2 2030x2 2031x3 2032x5 2033x2 2036x4 2038x2 2039x2 2040 2041 2042 2043 2045x2 2048x2 2049x2 2051 2052x2 2053x2 2054 2057x2 2058 2059 2060x4 2061x2 2062x2 2063x2 2064 2065x4 2066 2067 2068x2 2069x2 2070x2 2071 2072x2 2073 2074x2 2075x2 2076x3 2077 2078x2 2080 2081x2 2082x2 2083 2084 2085 2086 2087 2088x3 2091x2 2092 2093x2 2094 2095x2 2096x3 2098 2099 2100x2 2101x2 2103x2 2104 2106 2107 2109 2110x2 2111x3 2112 2114 2115x2 2116 2118x2 2119x2 2120x3 2121 2123x2 2125 2126x3 2127x2 2129 2130x3 2131x3 2132x2 2133x2 2137x4 2138x2 2139 2141 2142x2 2143x2 2144x3 2145 2146x2 2148 2149 2151x2 2152x4 2154 2155 2156x2 2157 2158x2 2159 2160 2161 2162x2 2163 2164 2165x2 2167x2 2169x2 2171 2173x2 2174x2 2176x2 2178 2179 2181x2 2182 2183 2184 2185 2186x3 2188 2189x3 2191 2192x2 2193 2194x3 2195x2 2196 2197x3 2198x2 2200x2 2203x2 2205x2 2207 2209x4 2210x3 2211 2213x3 2215 2216 2218 2219x2 2220 2221x4 2222x3 2225x3 2226 2227x2 2228x2 2230x3 2232 2236 2237 2239 2240x2 2241x3 2242x3 2243x3 2244 2245x5 2246 2249x3 2250 2251x2 2252x3 2253x2 2256 2257x4 2259 2260x2 2262x2 2264 2266x2 2267x2 2268x2 2269 2270 2271 2272 2273 2278 2279 2280x2 2282x2 2283 2284 2285 2287x2 2288 2289x3 2291x3 2293x2 2296 2298x2 2299x2 2302x3 2303x4 2305x2 2307x2 2309 2310x2 2311 2312 2315 2319 2320x3 2322 2323x2 2324x2 2325 2327 2328 2329 2330 2331x2 2333x2 2334 2336 2338 2339x2 2340 2341 2342 2343x2 2344x2 2346x2 2348x2 2349 2350x2 2351 2352 2354 2355 2356 2358 2359x3 2364 2365 2366 2367x3 2369x3 2370x2 2371x2 2373 2374x2 2375x2 2376 2380x2 2383 2384x2 2385 2386 2387x3 2388x2 2390 2391x2 2392x2 2393 2394x2 2395x2 2397x3 2399 2401x2 2402x3 2404x2 2408x3 2409x3 2413 2414 2415x3 2416 2418 2420x2 2421x2 2422 2425 2426 2428x3 2429 2430 2431x2 2432x2 2433x2 2434 2435 2437 2439x2 2440 2442 2443 2444x3 2445x2 2447x2 2448 2449 2454x4 2455 2459x2 2460x2 2462x2 2463 2464 2466 2468x4 2473 2474 2476 2479 2480 2481x2 2483x2 2485 2486x2 2488 2489x2 2491 2492 2494 2498x2 2499 2500x2 2501 2502x2 2503 2504 2508 2512 2513 2514 2516 2519 2520x2 2522 2523x2 2525x3 2528 2529 2530 2533 2537 2540 2542 2543x2 2545 2546 2547 2548x2 2549x2 2550 2552 2554 2555 2557 2559x2 2562 2563 2564x2 2569 2570 2575 2578 2580 2581 2582 2586x2 2590 2592 2597 2598x3 2599 2600 2602 2605 2607 2608 2610x2 2611 2613 2616 2618 2620 2623 2625 2628 2629 2630x3 2631x2 2634 2635x2 2636x2 2637 2639 2640x2 2642 2643 2648 2649 2650x2 2652 2653 2658x3 2659x3 2660 2661 2662 2664 2665 2667 2668 2671 2675x2 2676 2682 2683 2685 2687 2688 2689x2 2691 2694 2700 2701 2703 2704 2708 2712 2714 2717x2 2723 2724 2725 2727 2728 2733 2734 2737 2738 2740 2743x2 2750 2752 2753 2757 2767 2773x2 2777 2779 2791x2 2793 2798 2799 2802 2810 2815 2820 2822 2824x2 2825 2828 2829x3 2830x2 2836 2837 2843x3 2850 2863 2877 2878 2879 2883x2 2887 2890 2894 2898 2907 2912 2918 2921 2922 2924 2926 2928 2931 2932 2935 2945 2949 2953 2974 2978 2979 2995 2997 3002 3006 3008 3013 3027 3030 3033 3043 3046 3056 3058 3062x3 3067 3076 3077 3087 3097 3104 3117 3129 3133 3142 3150 3154 3159 3160 3163 3169 3192 3193 3200 3208 3219 3224 3233 3243 3275 3279 3283 3285 3288 3289 3306 3310 3314 3315 3350 3368x2 3370 3381 3387 3398 3399 3425x2 3452 3453 3456 3519 3538 3555 3563 3596 3658 3676 3701 3704 3759 3762 3827 3859 3947 3956 3993
``

``
width 24 (6000 walks, sum 30706020):
47 84 91 109 120 128 141 149 160 185 193 242 248 249 264 277 291 297 322 329 342 346 349 353 356 361 373 377 378 383 399x2 417 418 419 427 429 430 431 450 459 472 490 501 507x2 508 509 520 525 531 532x2 540 541 543 548 554 564 567 569 571 576 585 587 591 610 615 632 645 646x2 648x2 651 653 665 676 681 684 688 692 701 705 708 717 723 731 732x2 741 742 746x2 749 750 751 757 765 768 769 773 775x3 782 784 788 792x2 795 798 802 806 808 812 821 825 826x2 841x2 844 845 851 852 877 879 885 886x2 887 888 898 902 904 907 908 909 911 912 916 923 924 927 934 935 937 944 947x2 949 951x2 952 954 956 959 961 964 967x2 968 970 971 977 979 982 983 987 996 997 999x2 1000 1004 1007 1011 1012 1014 1015 1016 1020x2 1021 1022 1024 1030x2 1031 1033 1039 1042 1053 1063x2 1065 1070 1071 1083 1085 1087x2 1090x2 1097 1098 1099 1101 1105 1106 1107 1114 1115 1116x2 1118x2 1119 1120 1122x2 1126 1129x2 1131 1133 1134 1136 1137 1141 1142 1144 1145x2 1148 1150x3 1151 1152 1154 1155 1159 1161 1163x3 1167 1168 1171 1172 1173 1175 1176 1184x2 1197 1199 1203x2 1204 1205 1207 1208x2 1213 1216 1231 1232 1234 1235x2 1236 1243 1245 1248 1251 1253 1256 1258 1259 1260 1262 1268x2 1269 1277 1280 1282 1285 1286 1287 1289 1290 1291 1295 1296 1298 1299x2 1300 1301 1304x2 1307 1309 1312 1316 1319 1322 1327x2 1329 1333 1334 1339 1341 1342x2 1344x2 1347x2 1350x2 1351 1355 1360x2 1361x2 1362 1364 1365 1367 1368 1369 1375 1377 1378 1379 1380 1381 1382x3 1384 1388 1389 1394 1395 1396 1397 1400 1401 1402 1404 1405 1412 1413x2 1414 1416 1417x2 1418 1419x2 1421 1427x3 1430 1431x2 1432 1433 1434x2 1441 1445 1446x2 1456 1465x2 1468 1469 1470 1472 1475 1476 1478x2 1479 1480 1482 1484x2 1488 1492 1495 1497 1501 1506 1509 1516 1517 1519 1523 1525x2 1527 1528 1529 1531 1533 1536 1537 1538 1539x2 1541x2 1544 1545x2 1546 1548x3 1549x2 1554 1555 1559x2 1561 1565x2 1566 1570 1572 1573 1574 1581 1582 1586 1587x2 1588x2 1591x2 1592 1594 1596 1597 1601x2 1606 1607x2 1615 1618x2 1619x2 1623 1624 1627 1632 1634 1635 1637 1638x2 1639 1640 1642 1645 1647 1650 1651 1655 1657 1660 1662 1663 1664x2 1666x2 1671 1672 1674 1675x2 1678 1682 1683x2 1685 1688 1690 1691 1692 1693 1694 1696 1699 1700x2 1703 1707 1711 1712x4 1714x2 1715 1716x3 1717 1718 1720 1722 1727x2 1730 1732 1733x4 1734 1735 1737 1740 1742 1752 1755 1756 1758 1759x2 1761 1765 1766x2 1768 1769 1777 1778 1779 1782 1785x2 1786 1787x2 1790 1794 1795 1797x2 1799x2 1800 1801 1802x2 1803 1804 1805 1806 1807 1808 1810x2 1811 1819 1820 1822x2 1823 1826 1828 1829 1830 1831 1832 1835x4 1837 1838x2 1842 1844x2 1845x2 1848 1851 1852x2 1855 1856 1857 1858 1860 1861 1863x2 1866x2 1870 1871 1875 1877 1878x2 1882x2 1883x3 1885 1886 1887x2 1889x2 1890 1891 1892x2 1893x4 1896 1897 1898 1900 1903 1906x2 1907 1910 1912x2 1914 1916 1917 1919x3 1920 1922 1924x2 1926 1928x2 1930 1931 1934 1936 1940 1942 1943x2 1946 1947 1948 1949 1951x2 1953 1954 1956 1959x3 1960 1961 1963x2 1966 1968 1970x3 1971 1973 1974 1977 1978x2 1982 1983x2 1984 1985 1988 1989 1990x2 1991x2 1992 1998x3 2003x2 2006 2008x2 2010 2011 2012 2015 2016 2019 2020 2021 2024 2026x2 2028x2 2029 2031x2 2033 2035 2038 2039 2043x2 2045 2047 2048 2050x3 2051 2052x2 2053 2056x2 2057 2058 2060x2 2062 2065 2066 2069x2 2071 2072 2077 2080 2081 2084 2091 2092 2095 2096x2 2097x3 2098 2099 2102 2103 2105 2109 2111 2113 2115 2116x2 2120 2124x2 2133 2136 2139 2141x2 2142 2147x2 2148 2149 2153x2 2156 2158x2 2159x3 2160x2 2163 2165x4 2166 2168 2170x2 2172 2174 2175x2 2176 2177 2178x2 2182 2184 2185 2186 2188 2190x2 2191 2192 2195x3 2196x2 2197 2202 2203 2206x2 2209x2 2210 2211x4 2216 2217 2220 2224 2226x2 2227x2 2228 2229 2234 2236 2237 2238 2239x2 2241 2242 2244 2245 2248 2250x2 2252 2253 2254 2255 2257x2 2258 2260 2262 2263 2264x3 2265x2 2268x2 2269 2270 2271 2272 2275 2280 2285 2287x3 2289 2290 2291 2293x2 2294x4 2299 2302 2303 2306 2307 2316 2318 2319 2323 2325 2326 2327 2328 2329x2 2330x4 2331 2333 2334x2 2337 2340x2 2341 2343x3 2344x4 2347x2 2348x2 2350 2352 2353 2356 2357x3 2358 2359x2 2361 2362 2363 2364x2 2367x2 2369 2373 2374 2375 2376 2381 2382 2383x2 2385 2388x2 2390x2 2391 2392 2398x2 2400x2 2403 2404 2405x2 2409 2416 2417x2 2418 2419 2422 2424 2425 2427 2429x2 2430 2432 2440x4 2442 2446 2449 2451 2452 2453x2 2454x2 2455 2458x3 2460 2462 2463 2464 2466x2 2467 2468 2469 2470 2471 2472 2473x2 2475 2476x2 2477 2478 2483 2485 2487x2 2488 2489x3 2493x2 2494x2 2496 2498 2499 2500 2502 2503x2 2507 2508 2511 2512x2 2514 2515 2516x2 2517x2 2519 2520 2521 2522x2 2525 2526 2527x2 2529 2532 2535 2538x2 2539x2 2541x2 2542 2543 2544x3 2545x2 2546 2548 2549 2551 2552 2553 2554 2556 2560x2 2561 2563 2564 2565x3 2567x2 2568 2571 2575 2576 2578x3 2579x2 2583x2 2584 2585 2587 2589 2590 2591 2592 2594 2595 2598x3 2600 2602x2 2603x2 2604x2 2605 2606 2607 2608 2609 2614 2615 2617 2619 2621 2624 2626 2627 2628x2 2631 2633 2635 2636 2641 2645 2647 2649 2651 2652 2653 2654 2656 2657 2660 2663 2666 2667x2 2670 2674x2 2676x2 2680 2684x2 2685 2687 2692 2695 2697 2698 2699x3 2702x2 2703 2706x2 2708x2 2713x2 2715 2718x5 2719x2 2720 2724 2725 2729 2730 2731 2733x2 2734x3 2735 2738x2 2739x2 2741 2742x2 2745 2747 2748 2749 2750 2751 2752x2 2755 2756 2759 2761 2764 2765 2767x3 2768x3 2769 2770 2771 2772 2773 2774 2775 2776 2778 2779x2 2782 2786 2787 2788 2789 2790x2 2792 2793 2795x2 2796x2 2799x2 2800 2801 2802 2803 2804 2805x3 2807 2810 2811x2 2812x2 2813 2815x2 2816 2818 2820 2822 2823 2824 2827 2828 2830x2 2834 2835 2836x2 2838x2 2839 2840x3 2842x2 2844x2 2845 2846 2847 2851 2852 2856 2858x2 2859 2863x2 2864x2 2867 2869x3 2870 2871 2874 2876 2877x2 2878x2 2880 2881 2883 2888x2 2889 2891x2 2892 2895 2898 2902 2905 2906x2 2907 2909 2910x3 2911x3 2912 2913x2 2914x2 2918 2919 2922 2923 2926x2 2927 2930 2931 2932 2935 2936 2937x2 2938x2 2939x2 2940x2 2945 2949 2950x2 2951x2 2954 2956x2 2957 2958x2 2959 2961 2962x2 2963x2 2964x3 2965 2968 2973x2 2974 2977 2982x2 2984 2985 2987x2 2988 2990 2991 2992 2993x2 2996 2997 2999 3001 3002 3003 3011x2 3012x3 3013x2 3014x3 3015x2 3016 3017 3018 3019 3020x2 3022 3023 3024x3 3025 3026x2 3031x2 3033x2 3040x2 3045x2 3046 3048x2 3049 3050 3052x2 3054 3058 3060 3062 3063 3064 3065x2 3066 3067x2 3068 3069 3071 3075x2 3077x2 3078 3079 3080 3082 3083 3087x2 3091x2 3094x2 3096 3097 3098 3099x3 3102x3 3103 3104 3107 3108x3 3110 3111 3112x2 3113 3116 3117 3118x2 3119 3120x2 3123x3 3125 3126x2 3128 3130 3131 3132 3133x3 3135 3136x2 3137x3 3138x3 3143 3145 3147 3148x2 3149 3150 3152 3154 3156 3158x2 3160 3161x2 3165 3166 3173 3175 3177x3 3178 3179x2 3182 3183x3 3184 3185x2 3188 3190x2 3192x2 3195x2 3197x2 3199x3 3201 3203 3204x2 3205 3206 3207 3208x2 3210 3212 3213 3214 3215 3219 3221 3222 3224 3226 3232x2 3234x2 3236 3238 3240 3242 3246 3247 3249 3250 3255x2 3256 3257 3259 3261 3262x2 3263 3264 3266 3267x3 3268 3270 3271 3272x2 3275 3277x2 3279 3281 3282x2 3283x4 3285 3286 3288x2 3290x2 3292 3293x2 3294 3295x3 3296x2 3297x2 3298x3 3299 3302 3304x2 3305 3306 3308x2 3309 3311 3312 3314 3315x4 3316x2 3317 3320 3321 3322 3323 3324 3325 3326 3327 3331 3333x3 3335 3336 3337 3338x3 3340 3345 3347x2 3348x2 3353 3354x2 3355 3356 3357 3358 3364 3365 3366x2 3367 3368 3370x3 3371 3372x2 3373 3376x4 3377 3378x2 3380x2 3382 3383x2 3385 3386 3388 3391 3392 3393x2 3394x3 3395 3397x3 3398 3403 3406x2 3409 3411x2 3412 3413 3415x2 3416x3 3417x2 3422x2 3424 3426 3429 3431 3432 3438 3439 3440 3443x2 3446x2 3449x2 3450 3451 3453x2 3454 3455 3456x2 3457 3458 3459x3 3460x2 3462x2 3464x2 3465 3466 3467x2 3468x2 3469 3470x3 3471 3475x2 3476 3477 3478 3479x2 3480 3481x2 3484 3485 3490 3491 3492x2 3493x2 3496 3500x3 3501x2 3502 3505 3506x4 3508 3512x2 3515 3517 3519 3523 3524 3525 3526x3 3528x2 3529x2 3531 3533x2 3537x2 3539x2 3540 3542 3543 3544x3 3550 3551 3552 3553x2 3557x2 3559 3561 3564x2 3565 3566 3567x2 3569 3571 3573x2 3574 3575 3576 3577 3578 3579 3580 3582 3583x2 3584 3585 3586 3588x6 3589 3591 3593x2 3594 3600 3603 3604 3606 3609x2 3612 3614 3615x2 3616 3623x2 3624 3625 3627 3628 3630 3633 3635 3636 3638 3640 3641x2 3642 3643 3644 3645 3646 3649x3 3650 3651 3653x2 3654 3657 3662x2 3663x2 3664 3666 3667x3 3668x2 3669x2 3670 3671 3672 3674 3678 3679 3682 3683x3 3685 3686 3692x2 3694 3695 3696x3 3697 3698 3701 3702 3705x2 3706x3 3707 3708 3710x3 3711 3713 3715x2 3716x3 3718x2 3720 3721 3722 3723x2 3724 3727x2 3728x2 3729x2 3730 3731x2 3732 3733x2 3734x2 3735 3737 3738x2 3740 3741x2 3742 3743 3746x2 3748 3749 3750 3751x4 3752x3 3753x2 3756x3 3757 3760 3762x2 3763 3764 3765 3766 3769x3 3771 3773 3776x3 3777 3778 3779 3782 3784x2 3785x2 3786x2 3788 3789x2 3790x2 3791 3792x2 3793x2 3794 3796x3 3797 3799 3803 3805 3806x2 3807 3808 3809 3810x2 3812 3813 3814 3815 3818x3 3819 3823 3825 3826 3828x3 3829 3830 3831 3832 3833 3834 3835 3837 3839 3840x2 3848x3 3849 3850 3855 3857x2 3863 3865x2 3872 3873 3876 3877 3879 3880x3 3881 3883 3886x2 3887x2 3893x2 3894x3 3895 3897 3903 3905 3907x2 3908x2 3910 3912 3913x2 3914 3915 3916x2 3918x2 3919 3920x2 3921 3922 3925x2 3927x2 3928 3930x2 3931 3935x2 3936x3 3939 3940 3942 3946x3 3950x2 3951x2 3952x2 3954 3955x2 3956x2 3957 3958 3959 3960 3961 3963 3964 3967 3968 3971x2 3976 3980 3982x2 3983 3985 3987x3 3988x2 3990x2 3991x3 3992 3995 3997 3998x4 4001x2 4003 4005x2 4006 4007 4009 4010x2 4011 4012x3 4017x2 4020 4021x2 4022 4023x2 4024 4025x2 4026x4 4027 4028 4029 4032x2 4036x3 4039 4040 4041x2 4043 4045 4047 4048 4049 4051 4053 4055 4056x4 4058 4060 4061 4063 4064 4065 4066x2 4067 4068 4069 4070x2 4072x3 4075 4077 4078 4079x3 4080 4082 4084 4085x3 4088x2 4089x4 4090 4092 4095 4099 4101 4102 4103 4104 4105 4107 4108 4109 4111 4113 4114 4116 4117 4118 4119 4121x3 4123 4125 4127 4130 4131x2 4132x2 4133x2 4134x2 4135x2 4136 4137 4139 4140 4143 4144x2 4147 4148 4150 4151 4152 4153 4154 4155x2 4156 4157x4 4158x4 4159x2 4160 4161 4162x2 4163x2 4164x3 4165x2 4168 4170x2 4173x4 4174 4176 4177 4178x2 4179 4180x3 4182 4185 4187x2 4188x2 4193 4194 4196 4197 4198 4199 4200 4203x2 4205x3 4206 4207 4208x2 4209x2 4210 4211 4212 4213 4214 4217x3 4218 4219x2 4221x2 4222 4225 4226 4227x4 4228 4231x2 4233 4234 4237 4239x3 4240 4241x3 4242x3 4245 4246x2 4247x2 4249x2 4251 4252 4254 4256x2 4258 4259x3 4261 4262x2 4264x2 4265 4266 4267 4268 4271x2 4272 4274 4275 4276x3 4278x4 4279x2 4283 4286 4287 4288 4289x2 4294 4295 4296 4298 4300 4306 4308 4309x3 4312 4313 4314 4315 4316 4317 4318x3 4322x2 4323 4324 4334 4335x2 4337 4339x2 4340x2 4341 4343 4346 4347 4350 4351 4355 4357x2 4358x2 4359x2 4361x5 4362 4363 4364 4369 4372x3 4373 4376 4377x3 4381x2 4383x2 4387 4388 4389x2 4391 4392x2 4393x2 4394 4395 4397 4398 4399 4402 4404 4405 4406 4408x2 4409 4410x2 4411x2 4415x2 4418 4420 4422 4423 4430 4432 4433 4435 4439 4440 4441x3 4442 4443 4444x2 4445 4447x3 4448x3 4449x2 4450 4451 4453 4454 4456 4459 4461 4462x2 4463x2 4465 4466 4467x2 4468 4469x2 4470x2 4471x2 4472 4474 4475x3 4478x2 4479x2 4480 4481x2 4483x3 4485 4488 4491x2 4492 4493x2 4494 4495 4498x2 4499x2 4500 4502 4503 4504x2 4506x2 4507 4508 4509 4511 4512 4513 4515x2 4516x2 4517 4519 4521 4525 4526x2 4527 4529 4530x4 4531 4533 4536x2 4544 4553x2 4555 4556x2 4559 4562 4567 4569 4571x2 4572x2 4573 4574 4578x2 4579 4580 4587x2 4588 4589 4590 4591x2 4592 4593 4594 4595 4596 4597 4598x3 4600 4603 4604 4605 4606 4607 4608x3 4609x3 4610x3 4612 4613 4615 4616x2 4619 4621x2 4625 4627 4628x2 4629 4630x2 4634x2 4635 4638 4640 4645 4646 4647 4650 4652x2 4655 4658x2 4659x2 4662x3 4663x2 4665x2 4666 4668x3 4669 4670x2 4673x2 4674x3 4677 4678 4679x2 4680 4681 4682x2 4683x3 4685 4686 4688 4689 4693 4694x2 4698x2 4699 4700x2 4701 4702 4703x3 4704 4705 4706 4708 4709x2 4711 4714 4715 4716x2 4717 4718x2 4719x2 4720x2 4722 4723 4724 4725x2 4727 4728 4730x3 4731 4733x5 4734x2 4735 4737x2 4739x2 4741x3 4742 4744 4745x2 4746 4747 4749x3 4751 4753 4755x2 4758 4759x2 4760 4761 4763 4764 4765x2 4766x3 4767x3 4768x2 4770x3 4771x4 4774 4778x3 4779 4781 4783 4786 4787 4788x2 4790 4794 4795 4796 4799x2 4800 4801x2 4803 4805 4807 4808x2 4809x2 4812x2 4813x2 4814x2 4817 4818 4819 4820 4822 4823x2 4824x3 4825x2 4827 4829 4830 4835 4836 4837 4838x2 4840 4841 4842 4844 4846x2 4847 4851 4853x2 4854 4855x2 4858 4859 4861 4862 4863 4864 4868 4870 4871x2 4873x2 4879x2 4881 4883 4884 4886 4889 4890 4892 4893x3 4894 4897 4900 4902 4903x4 4904 4905x3 4907 4908 4909 4910x2 4913 4917 4919 4921 4923 4924 4926 4929 4931x2 4933 4934x2 4935 4936x3 4938 4939x3 4940x2 4942 4943x2 4944 4946 4948 4952 4953 4954x2 4959 4960 4961x3 4962 4965 4966x2 4967x2 4968x2 4970 4974 4977 4978 4979 4980 4982 4985 4986 4991 4993 4994x2 4996x2 4997 4998x2 4999 5000x2 5001x2 5002x2 5004x2 5005 5008x2 5009x2 5011 5019 5021x3 5022 5024x2 5027 5028x3 5029x2 5030x3 5031 5035x2 5038x2 5041 5042 5044 5045 5048x2 5049 5051 5052 5053 5058x2 5060 5063x2 5064 5067 5068x2 5070 5071x2 5073x2 5075 5077 5078 5079 5080x3 5082 5083 5084x2 5085 5088 5090 5091x2 5092 5093 5094x5 5097 5100x2 5101x2 5102x2 5103 5104 5106x3 5107x2 5108x3 5109x2 5110 5111 5114x2 5115 5116x2 5118x2 5121 5122x2 5123x3 5124 5125x3 5128 5129 5130 5132 5133x2 5134x3 5135 5140x2 5144 5146x3 5148x2 5149 5150 5151 5152 5155 5156 5157 5158x2 5159 5161x3 5162 5163 5164 5165 5166x2 5168x2 5169 5170 5171 5172x3 5173 5174 5176x3 5180 5182x2 5188x3 5192 5194x3 5195 5196 5197 5199 5200 5202x2 5203x2 5205x2 5206 5207x3 5211x2 5212 5214 5215 5216x3 5217x2 5220 5221 5223x2 5224 5226 5227 5228 5232 5235 5237 5240 5246 5248 5249 5250x2 5251 5254x2 5255 5256 5261 5262x2 5268 5269 5271 5273x2 5275x2 5276 5277 5278 5282 5284 5286x2 5288 5290x3 5291 5294 5296 5297 5301 5302 5306x2 5307x2 5308 5309 5313x2 5314x2 5317x2 5319 5321 5322x3 5325x2 5327 5331 5333x2 5334 5336 5339 5340x2 5342x2 5344x2 5348x2 5349 5352 5353 5354 5355 5356 5358x2 5359 5360x2 5364x2 5365 5367 5370 5373 5375x2 5377x2 5378 5379 5380x2 5383x2 5384 5388x3 5390 5393x2 5394 5397 5399 5404 5406 5410 5412 5417 5421 5422x3 5423x3 5425 5427 5428 5430x2 5431x2 5436 5437 5438 5439 5440 5442x2 5443x3 5444 5445 5446 5447 5450 5451x2 5455x3 5460x3 5461 5464x2 5467 5468x2 5470 5472 5473 5475 5476 5477x2 5479x3 5480 5481x2 5483 5484 5485x2 5488 5489x2 5491 5493x2 5495 5497 5498 5499 5500x4 5501 5502 5503 5506 5507x2 5510x2 5511x2 5512 5517 5518 5519 5520 5521x2 5525x3 5527 5529x2 5532 5534 5536 5539x2 5540 5541 5542 5543 5547x2 5548 5549x2 5551 5556 5557 5558 5559x4 5563 5565x2 5566 5569 5571 5573 5575x2 5577 5578 5581 5585 5586 5588x2 5589 5591x2 5592 5593 5594x3 5595x2 5599 5606x3 5608x2 5611 5612 5613 5615 5620 5621 5622x2 5623 5628x2 5629 5631 5633 5634x2 5635x3 5636 5637x2 5638 5639 5642 5643 5644 5645 5648x2 5650x2 5651x2 5654x2 5655 5656 5657 5659 5660x2 5661x2 5662 5664 5665x2 5666 5667 5669 5672 5673 5676 5677 5678 5679 5680 5683 5684 5685x2 5686 5689 5691 5693 5694x4 5696 5698x2 5700 5701 5702 5703 5705 5710x2 5713x3 5714x3 5715 5718 5719x2 5721 5722x2 5726x2 5727 5728x2 5731 5732 5734 5735 5737x2 5738 5739 5740x2 5743x2 5744x2 5746x3 5747 5748x2 5750 5751x2 5755x2 5756 5757 5758 5759x2 5763x3 5766 5767 5770 5771x2 5772 5774 5775x2 5776x2 5777 5780 5781x2 5782 5783 5784 5786x2 5787 5791 5794x2 5795 5796 5799 5800 5803x2 5805x4 5806x2 5807 5810 5812 5815x2 5818 5819 5820 5822 5823 5825 5827 5828 5829 5832 5833 5836x2 5837 5838x3 5839 5840x2 5842 5845x2 5846x2 5849x2 5850x2 5851x2 5853 5854 5857 5858 5859 5860 5861 5865 5866 5869 5871x2 5872 5875x2 5877 5878 5881 5882 5883x2 5884 5885 5888 5891 5892 5893 5894x2 5895 5896x2 5897 5899 5900 5901 5903 5905 5908 5910x2 5914x2 5918x2 5921 5922 5923 5925x2 5926 5929 5932 5934x2 5935x2 5937 5938 5939 5940 5941 5942x2 5943x2 5944 5953 5954x2 5958 5961 5963 5968x2 5969 5971 5972 5973x2 5974 5975 5976x3 5978x2 5979x2 5985x2 5987x2 5988x2 5989 5990 5991 5993 5994x2 5995 5998x3 6003x2 6008 6009x2 6010 6012 6014 6015x2 6016x2 6018x3 6019x2 6026 6027 6028 6029 6030 6032x2 6034 6036 6037 6041 6043 6045 6047x2 6049 6050x2 6051 6052x3 6053 6055x3 6059 6061 6064 6066 6067 6070x2 6072x3 6073 6080x3 6081x2 6082x3 6084 6085 6087 6090x2 6092 6093x2 6094x2 6095x2 6098x2 6099 6100 6102x4 6103 6104 6105 6106 6107 6108x2 6110x2 6111 6112 6113x4 6115 6116x2 6119 6122 6123x2 6124 6125 6128 6133x2 6134 6136 6138x2 6142 6145 6147x4 6149 6150 6153 6154 6156x3 6157 6158x2 6165x2 6166x2 6167x2 6168x2 6170x2 6171 6175 6176x2 6180 6183 6186 6187x2 6188 6190 6191 6192 6193 6196 6197 6198 6201x3 6203x2 6204x4 6206 6208 6209x2 6212x2 6213 6214x3 6217 6221x2 6222 6223x2 6224 6228 6229 6232 6233x3 6238x2 6241x3 6242x2 6248 6249 6250x2 6251x3 6255 6256 6257x2 6258x2 6260 6261 6262x2 6263 6265 6266 6269x3 6272x2 6273x2 6274 6276x2 6278 6281 6283 6285 6288 6290 6292 6297 6298 6299x2 6300 6303x2 6304 6306x3 6308 6312 6313 6315x3 6316x2 6317 6319 6320 6323x2 6324 6327 6328 6333 6335 6336 6337x3 6338 6339x2 6340 6342 6344x2 6346x2 6347 6348x2 6352x2 6353 6354 6356x2 6357x2 6358x2 6360 6361 6363 6365 6366x2 6369 6375 6377 6383 6385 6386 6391x2 6392 6394 6396 6397 6399x2 6402 6403 6407 6409 6410 6412x3 6415 6417x2 6420 6421 6422 6423 6426 6427x3 6431 6433 6436 6438x2 6442 6443 6446x2 6451 6454 6458x2 6461x3 6466 6467 6468x2 6470 6471 6472x2 6473x2 6474 6475 6476 6477x2 6479 6483 6485 6486x2 6488x2 6489x2 6490 6493 6494 6495x2 6497 6498 6501x3 6502 6503x2 6504x2 6505 6510x2 6511x2 6512x2 6515 6520 6521 6522x2 6526 6527x2 6528 6529x2 6531 6532 6533 6535 6536 6537 6540x2 6541 6542 6543x3 6551 6552x2 6553x3 6564 6565x2 6567x3 6569 6572 6579 6580 6581x2 6586x3 6589x3 6590 6592 6594 6595 6598 6599x2 6600 6602 6605 6607x2 6608 6610x2 6612x2 6613 6616 6618x2 6620 6621 6622 6623 6625 6626 6632 6634 6638 6639 6640 6641x2 6646 6647x2 6649 6651 6652 6655 6656x2 6657 6663 6664x2 6673 6675 6676 6677 6686x3 6689 6696 6697x2 6698 6699 6700 6701 6705 6706 6707 6709 6710x2 6712 6713 6715 6717x2 6718 6719 6720 6721x2 6723 6726 6728x2 6735 6737 6738 6741x3 6743x2 6747x2 6748 6751 6752 6753 6754x2 6759 6760x2 6761x2 6764 6765 6766 6768 6769 6770 6778 6781 6782 6785 6786 6787 6788 6789 6790 6791 6792 6795x3 6798 6800 6803x2 6805 6807 6808 6809 6810x4 6811 6812 6814 6818x2 6824 6825 6827 6834 6837 6844 6845 6846x3 6847x2 6848 6852 6854 6855 6856 6859 6861 6862 6863x2 6864x3 6866 6868x2 6869 6871x3 6875 6876 6879 6881 6884 6885 6886x2 6887 6888 6889 6891x2 6892x2 6894 6898 6901 6902 6903 6905 6908 6911 6912 6913 6914 6917x2 6919x3 6925 6928 6930x2 6933 6934 6935 6937 6941 6942 6943 6945 6947 6955 6956x2 6958 6964 6967 6968 6971x2 6974x2 6975 6976 6977x2 6978x3 6981 6983x2 6984 6985 6987x2 6988 6989 6991 6994 6996 6997 7000 7003 7005x3 7007 7012 7013 7016 7021 7022 7023 7024x3 7026x2 7027 7028 7032 7037x2 7049 7050x3 7053 7054 7059 7062x2 7063 7064 7067x2 7072 7075x2 7076 7077 7078 7079x2 7082x3 7083 7085 7089 7092x2 7093 7098 7099 7100 7101 7103 7105 7106 7107x2 7108 7110 7113 7115 7116 7117x2 7119x2 7120 7121x4 7122 7123 7124 7125 7126x2 7129 7130x2 7133 7134 7135 7137x2 7139x2 7140 7142 7144 7148 7151 7156 7158 7163 7166x2 7168 7172x2 7175x2 7177x2 7179x2 7184 7186 7188 7190 7193 7195 7196 7197 7199 7200 7202 7203 7206 7208 7209 7210x2 7212 7213 7215 7220 7222 7223 7225 7227x3 7229 7230 7232 7233 7237 7239 7242x2 7245 7246 7247 7249x2 7250 7251 7252 7254 7255 7261x2 7262 7264 7265 7269x2 7272 7274 7279 7282 7283 7285x2 7291 7292x2 7294 7300 7305 7306 7307 7308x2 7309 7310x2 7312 7313x2 7314 7315 7316x2 7317 7318 7319 7321x2 7322 7323x3 7325x2 7326 7329 7331 7332x2 7334 7337 7340 7345 7349 7354 7355 7356 7357x2 7359 7361 7362 7366 7371 7374 7375x3 7376 7378 7380x2 7382x2 7383 7384 7386 7387 7389 7393 7395x2 7403 7404 7405x2 7406 7407x2 7410 7411 7412 7414x3 7416 7417 7419 7421 7422 7424 7436 7437 7440x2 7443 7449x3 7456 7457 7459x2 7462 7464 7465 7467 7468 7478 7479 7480 7482 7483 7491 7492 7493 7498 7501x2 7503 7506 7508 7512 7514 7518 7519x2 7524 7528 7529 7530 7532 7535 7537 7541x2 7543 7544 7547 7549 7550 7551 7555 7558 7560 7562 7566 7568 7571x2 7572 7574 7575 7576 7577 7579 7580 7584 7586 7590 7594 7595 7603 7617x2 7622 7625 7629 7635 7636x2 7637 7640 7643 7645 7646x2 7648 7649 7650 7655 7664 7668 7672 7678x2 7682 7683x2 7687 7688 7690 7692 7694 7696 7697 7700 7709 7711 7714 7718 7721 7725 7729 7732 7733 7734x2 7741x2 7743x2 7744x2 7745 7746 7747 7749 7750 7751 7752 7755 7758x2 7759 7760x2 7761x3 7762 7763x2 7765 7772x2 7780 7782 7785 7786 7787 7790 7791 7801 7804 7806 7813 7814 7816 7817 7818 7819 7820 7821 7823 7825 7826 7829 7830x2 7835 7838 7839 7841 7850 7853 7855 7858x2 7859 7860 7869 7873 7876 7882 7883 7886 7887x2 7888 7889 7892 7894 7897 7898 7901x2 7903 7904 7905 7907 7912 7915 7916x2 7923 7925 7927 7931 7934 7938 7940x3 7941 7943 7946 7949 7950 7951 7953 7954 7956x2 7957 7958 7963 7964x2 7965x2 7969 7970 7973 7974x2 7975 7979x2 7983 7987 7988x2 7990 7991 7992x3 7995 7997x2 7998 8004 8005x2 8007 8010 8011 8021x3 8023 8024 8026 8035x2 8038 8041x2 8047 8048 8054 8059 8061 8062 8066 8067x2 8070 8074 8075 8077 8078 8079x3 8080 8082 8084 8085 8091 8093 8094 8095 8097 8098 8099 8100x2 8101 8107 8109 8111x2 8114 8117 8120 8122 8124 8130 8134x2 8135 8136x2 8146 8148 8149 8150 8156 8159 8162 8164 8165 8179x2 8180 8186x2 8190 8194 8204 8205x2 8206 8207 8208 8210 8213 8217 8218 8219 8222 8223 8226 8228 8232 8233x2 8239 8241 8242 8247 8248 8252 8253 8254 8255x2 8256x2 8258 8261 8263 8268 8269 8273 8274 8279 8281 8283 8292 8298x2 8300 8301 8306 8310x3 8311 8315x2 8317 8320 8324x3 8332x2 8333 8339 8343 8344 8345 8350 8353 8361 8363 8365x2 8366 8367 8370 8373 8379x2 8381x2 8384 8389 8391 8396 8397 8398x2 8405 8406 8413 8416x2 8418 8419 8420 8421 8425 8427 8437 8438 8441 8445 8452 8465 8472 8473 8477 8478 8484 8486x2 8488x2 8490 8493x2 8499 8501x2 8502 8507x2 8509 8514 8520 8529 8538 8540 8542 8545 8546 8549x2 8555 8566 8575 8577 8581 8582x2 8583 8584 8586x2 8589x2 8593 8595 8598 8601 8610 8614 8619 8622 8624 8625 8626 8630 8635 8638 8645x2 8646 8648 8649 8653 8659 8660 8661x2 8662 8674 8677 8679x2 8680 8682 8688 8692 8693 8695 8697x2 8698 8700 8705 8721x2 8724 8726 8729 8735 8743 8745 8752 8753 8757 8762 8775 8780 8792 8795 8809 8811 8814 8815 8819 8822 8826 8827 8829 8831 8832 8836 8839 8841 8845 8851 8855 8860 8865 8871x2 8875 8877 8878 8885 8888 8892 8893 8894 8897x2 8901 8903 8905 8908 8912 8914 8915 8917x2 8918 8919x2 8922 8932x2 8934 8935 8937x2 8938 8941x2 8944 8955 8966 8974x2 8975 8976 8978 8984 8988 8990x2 8996 8998 9003 9005x2 9010 9016 9031 9043x2 9044 9051x2 9052 9054 9055 9060x2 9068x2 9077 9079 9080 9082 9095 9100x2 9104 9112 9115 9116 9117 9119 9123 9128 9132 9137 9147 9151x2 9152 9155 9165 9172 9176 9184 9191 9198 9199 9205 9217 9218 9220 9230x2 9235 9236 9239 9241 9248 9249 9250 9252 9254 9255 9256 9269 9272 9277 9280x2 9281 9285 9286 9300 9303 9305 9307 9312 9316 9321 9322 9324x3 9330 9336 9339 9340x2 9346 9356 9360 9362 9363x2 9365 9381 9383 9384 9395 9396x2 9399 9410 9424 9426 9431 9434x2 9445 9447 9452 9454 9456 9465 9476 9480 9482 9488 9492 9494 9496 9509 9519 9520 9524 9525 9530 9533 9540 9547 9548 9549x2 9553 9557x2 9561 9565x2 9566 9569 9571 9573 9574 9578 9588 9593 9598 9607x3 9608 9611 9613x2 9634 9643 9652 9655 9665 9670 9683 9691 9699 9701 9709 9711 9719 9738 9749 9755 9759 9765 9771 9773 9777 9779 9784 9800 9807 9832 9847 9849 9851x2 9861 9863 9870 9874 9882 9887 9894 9896 9898x2 9900 9902 9907 9909 9911 9912 9913 9914 9916 9919 9920 9922 9925 9932x2 9939 9942 9944 9952x2 9965x2 9972 9974 9976x2 9979 9994 9996 10016 10021 10025 10030 10034 10039 10040 10045 10047 10049 10052 10057 10058 10062 10072x2 10073x2 10082 10085 10086 10090 10094 10096 10097 10100 10104 10106 10112 10115 10118x2 10133 10134 10145x3 10146 10148 10152 10159 10162 10170 10185 10188 10190 10191 10197 10199 10204 10219 10220x2 10229 10231 10240 10242 10246 10264 10270 10271 10275 10280 10284 10288 10299 10300 10313 10314 10318 10319 10320 10326 10329 10341 10362 10380 10391 10396 10412 10416 10429 10437 10445 10467 10469 10475 10481 10483 10484 10491 10498x2 10503 10505 10509x2 10519 10538 10548 10562 10567 10574 10585 10587 10590 10591 10593 10618 10653 10660 10665 10670 10678 10690 10698 10707x2 10709 10721x2 10726 10729 10731 10755 10791 10804 10809 10811 10835 10838 10841x2 10848 10867 10873 10875 10877 10880 10881 10910 10912 10922 10936 10937 10941 10950 10954 10955 10958 10970 10971 10978 10981 10988 11005 11012 11025 11027 11028 11032 11041 11043 11064 11066 11069 11079 11085 11092x2 11098 11101 11109 11122 11151 11159x2 11187 11233 11250 11274 11309 11310 11312 11335 11338 11342 11352x2 11353 11358 11365 11370 11388 11414 11418 11422 11424 11442 11445 11455 11464 11471 11484 11486 11526 11547 11550x2 11551 11563 11566 11576 11580 11588 11606 11612 11618 11620 11634 11635 11660 11669 11697 11728x2 11730 11764 11768 11770 11802 11808 11809 11815 11898 11911 11922 11966 11972x2 11973 11974 11980 12011 12019 12020 12028 12039 12046 12053 12100 12121 12130 12209 12214x2 12218 12229 12241 12278 12331 12384 12406 12429 12456 12468 12469 12470 12486 12517 12522 12565 12584 12585 12588 12609 12647 12684 12759 12775 12777 12780 12854 12887 12901 12978 12992 13031 13096 13167 13199 13212 13337 13397 13412 13667 13712 13925 13945 14117 14162 14284 14321 14347 14821 14957 15230 15308 15984 17491 17639 18268
``

``
width 28 (1200 walks, sum 24549713):
164 470 707 827 944 1001 1066 1568 1576 1801 1830 2226 2252 2264 2475 2482 2843 2918 2963 3057x2 3075 3146 3288 3353 3391 3430 3492 3673 3771 3825 3838 3843 3875 3888 3946 3954 3964 4057 4293 4367 4521 4644 4684 4693 4716 4870 5081 5132 5184 5237 5242 5356 5377 5409 5427 5445 5451 5462 5568 5583 5670 5685 5687 5732 5766 5792 5799 5817 5829 5868 5878 5915 5994 6032 6121 6145 6153x2 6167 6171 6245 6261 6367 6394 6416 6450 6461 6492 6632 6643 6684 6709 6751 6782 6795 6826 6828 6836 6839 6845 6877 6900 6921 6950 6959 6960 7020 7135 7162 7169 7187 7195 7202 7225 7266 7275 7340 7372 7395 7396 7484 7503 7517 7586 7593 7645 7677 7711 7813 7894 7901 7939 7949 7999 8027 8037 8054 8074 8170 8209 8212 8283 8288 8296 8368 8462 8517 8519 8570 8582 8611 8618 8676 8742 8808 8906 8918 8951 9026 9053 9090 9111 9140 9158 9174 9199 9217 9237 9257 9269 9280 9286 9372 9392 9406 9413 9438 9444 9458 9479 9501 9503 9508 9509 9524 9574 9577 9586 9679 9682 9698 9747x2 9766 9767 9782 9806 9814 9846 9868 9909 9937 9972 9987 9988 10004 10048 10049 10058 10090 10115 10134 10156 10165 10191 10286 10292 10318 10408 10444 10448 10471 10502 10538 10569 10576 10609 10692 10696 10761 10820 10853 10881 10918 10924 10931 10983 11054 11063 11139 11180 11190 11218 11245 11252 11331x2 11334 11339 11345 11449 11489 11498 11510 11557 11588 11627 11634 11643 11663 11666 11668 11676 11723x2 11729 11827 11852 11858 11896 11929 11955 12005 12032 12041 12042 12056 12116 12123 12154 12156 12198 12204 12221 12277 12320 12324 12379 12395 12410 12421 12426 12435 12437 12468 12487 12502 12510x2 12515 12554 12567x2 12588 12607 12630x2 12700 12701 12731 12745 12755 12773 12776 12782 12801 12818 12898 12939 12992 13014 13034 13064 13073 13097 13110 13153 13156 13162 13176 13186 13188 13216 13267 13316 13376 13390 13403 13408 13410 13423 13434 13445 13458 13466 13482 13509 13534 13535 13538 13539 13547 13572 13643 13661 13676 13710 13747 13771 13823 13834 13845 13860 13872 13885 13910 13915 13927 13984 13990x2 13992 13994 14006 14012 14044 14051 14062 14068 14085 14105 14118 14130 14132 14228 14272 14274 14300 14315 14351 14377 14430 14434 14471 14524 14527 14650 14672 14674 14689 14690 14710 14733 14830 14847 14871 14919 14954 14969 14998 15004 15021 15030 15043 15045 15057 15063 15069 15076 15121 15177 15200 15203 15237 15282 15297 15305 15319 15356 15386 15396 15425 15436 15446 15457 15501 15533 15561 15575 15598 15639 15708 15714 15721 15724 15726 15738 15770 15773 15778 15787 15803 15830 15912 15933 15939 15947 15949 15968 15971 15974 15982 15984 15985 16005 16010 16016 16026 16034 16037 16054 16071 16077 16084 16118 16159 16173 16180 16236 16242 16249 16252 16278 16309 16329 16330 16410 16413 16415 16449 16496 16503 16507 16572 16594 16614 16616 16698 16700 16724 16789 16814 16832 16848 16858 16860x2 16866 16874 16883 16898 16908 16911 16915 16919 16922 16928 16935 16937 16954 16958 16965 16969 16984 17013 17015 17040 17046 17119 17142 17145 17164 17179 17182 17215 17259 17274 17309 17323 17327 17340 17345 17352 17377 17410 17424 17471 17479 17499 17529 17539 17541 17543 17585 17611 17631 17633 17654 17675 17696 17803 17804 17832 17876 17877 17951x2 17959 17960 17966 17995 18002 18038 18052 18053 18089 18102 18120x2 18144 18173 18182 18187 18199x2 18217 18250 18403 18405 18426 18459 18490 18494 18506 18520 18536 18539 18540 18548 18552 18568 18576 18586 18736 18748 18778 18791 18854 18861 18886 18946 19010 19019 19045 19058 19061 19109 19126 19137 19142 19170 19177 19178 19262 19304 19379 19383 19394 19449 19489 19491 19507 19577 19629 19630 19676 19677 19712 19735 19767 19772 19777 19786 19814 19830 19857 19862 19907 19990 19993 20010 20052 20061 20128 20152 20154 20170 20197 20200 20287 20320 20334 20346 20361 20369 20382 20386 20440 20517 20575 20623 20646 20652 20654 20656 20712 20724 20733 20742 20815 20824 20843 20858 20867 20885 20905x2 21023 21026 21093 21097 21153 21156 21170 21194 21234 21276 21354 21357 21397 21433 21444 21445 21474 21489 21493 21503 21551 21557 21582 21590 21603 21611 21678 21681 21683 21717 21774 21779 21794 21817 21841 21848 21860 21913 21917 21928 21964 21970 22041 22109 22219 22235 22246 22333 22384 22409 22443 22474 22499 22562 22582 22588 22708 22712 22717 22721 22753 22808 22857 22871 22923 22952 22963 22967 22977 22999 23022 23046 23057 23061 23078 23091 23305 23315 23344 23378 23385 23445x2 23459 23461 23478 23489 23538 23543 23547 23548 23552 23553 23590 23620 23632 23636 23717 23769 23786 23793 23798 23819 23835 23857 23871 23910 23939 23972 24032 24042 24045 24067 24069 24101 24129 24133 24163 24183 24195 24202 24206 24340 24350 24361 24364 24386 24391 24475 24493 24533 24559 24582 24610 24621 24627 24644 24675 24691 24734 24763 24785 24832 24844 24845 24849 24875 24893 25098 25115 25193 25244 25290 25315 25316 25322 25410 25458 25484 25494 25552 25556 25557 25648 25668 25762 25801 25821 25875 25947 25970 26029 26158 26173 26208 26231 26266 26289 26317 26327 26343 26358 26367 26375 26412 26413 26416 26449 26456 26471 26477 26489 26500 26507x2 26532 26563 26572 26574 26580 26605 26642 26713 26755 26896 27013 27018 27098 27107 27130 27144 27199 27252 27296 27310 27318 27353 27534 27588 27637 27650 27724 27761 27764 27782 27795x2 27805 27816 27878 27903 27974 28064 28073 28084 28123 28151 28158 28179 28216 28282 28294 28323 28330 28365 28377 28407 28414 28478 28479 28522 28535 28559 28575 28627 28628 28630 28654 28662 28707 28754 28801 28832 28849 28869 28902 28916 29053 29055 29149 29166 29183 29221 29241 29369 29386 29528 29566 29589 29714 29801 29858 29954 29970 30040 30042 30056 30081 30117 30122 30190 30192 30217 30231 30263x2 30284 30302 30349 30353 30391 30491 30672 30727 30770 30799 30919 30927 31023 31031 31132 31194 31268 31416 31570 31583 31585 31608 31643 31727 31756 31795 31803 31855 31863 31895 31907 32012 32068 32080 32092 32111 32170 32193 32215 32305 32311 32317 32369 32479 32548 32670 32686 32820 32839 32924 32971 33020 33036 33143 33218 33301 33336 33369 33383 33386 33406 33421 33448 33505 33513 33693 33716 33730 33796 33818 33833 33881 34113 34119 34125x2 34157 34198 34259 34274 34342 34471 34559 34606 34790 34797 34810 34831 34872 34899 34919 34923 34958 35002 35030 35054 35070 35071 35186 35251 35335 35357 35371 35411 35433 35541 35732 35878 35951 36241 36380 36395 36404 36462 36475 36523 36526 36573 36576 36582 36621 36746 36797 36892 36939 36940 37051 37214 37223 37234 37274 37303 37343 37423 37510 37569 37676 37718 37813 37953 38190 38353 38363 38373 38396 38451 38765 38861 39041 39493 39520 39524 39582 39672 39798 39862 39961 40106 40228 40331 41065 41151 41279 41281 41389 41413 41602 41614 41753 41795 41835 42361 42435 42733 42839 42874 42951 43006 43348 43703 43769 44349 44497 44508 44543 44665 45406 45458 45535 45673 46547 46630 46987 47005 48098 48191 48467 49393 49644 49992 50214 50330 50659 51407 51958 52603 52641 52673 52758 54987 55659 57269 57315 59293 63538 63683
``

``
width 32 (1200 walks, sum 99541847):
5281 5840 6249 6272 6904 7273 8300 8679 9431 9890 10774 10914 11140 11499 11854 11871 12094 12189 12209 12309 12336 12499 12639 12776 13209 13241 13534 13578 14207 14313 14361 14407 14882 15184 15467 15596 16437 16815 16951 17297 17390 17866 18084 18296 18528 18737 18769 19024 19068 19097 19369 19374 19387 19608 19662 20383 20765 21121 21246 21249 21620 21743 21810 21887 21983 22476 22672 23034 23385 23428 23438 23483 23583 23846 23888 24300 24381 24471 24494 24527 24601 24662 24665 24894 24905 25124 25279 25502 25546 25590 25817 25962 25963 26078 26578 26967 27082 27101 27529 27792 28237 28553 28568 28581 28794 28994 29146 29240 29423 29627 29739 29865 30228 30532 30544 30546 30796 30903 31244 31295 31421 31634 31950 31964 32015 32069 32088 32160 32163 32483 32491 32495 32570 32585 32633 32671 32762 33162 33333 33506 33558 33994 34165 34209 34268 34334 34345 34464 34518 34548 34576 34643 34729 34792 34817 34887 34930 34962 35076 35145 35160 35202 35302 35394 35400 35530 35612 35614 35622 35652 35674 35873 35901 35953 35964 36019 36159 36347 36361 36557 36689 36907 36975 36993 37032 37080 37131 37407 37432 37521 37664 37758 37956 37968 38118 38241 38270 38355 38364 38457 38465 38477 38544 38820 38987 39127 39148 39301 39323 39472 39589 39750 39804 39928 40097 40121 40154 40286 40381 40739 40815 40851 41329 41590 41758 42026 42120 42216 42265 42443 42569 42575 42601 42604 42672 42685 42806 42902 42937 43088 43091 43097 43169 43185 43264 43404 43563 43836 43928 43946 44026 44266 44646 44787 44823 45073 45097 45154 45191 45238 45278 45486 45550 45581 45750 45869 45916 46006 46040 46058 46075 46165 46320 46346 46535x2 46548 46569 46595 46631 46670 46739 46887 47024 47353 47485 47503 47620 47937 47999 48081 48543 48697 48712 48790 49005 49113 49275 49307 49475 49740 49783 49798 49803 49939 50083 50115 50149 50241 50357 50593 50997 51004 51017 51203 51325 51381 51432 51441 51454 51547 51616 51632 51722 51799 52004 52060 52195 52221 52241 52304 52364 52545 52564 52811 52950 53163 53220 53244 53301 53337 53486 53507 53734 53818 53842 53939 53941 53971 54159 54272 54441 54533 54607 54738 54756 54782 54816 54866 54874 54960 55022 55150 55213 55381 55520 55575 55616 55670 55735 55976 56028 56171 56370 56453 56467 56705 56725 56879 56897 57091 57149 57175 57198 57334 57418 57598 57623 57961 57993 58103 58184 58186 58201 58202 58212 58227 58358 58391 58526 58537 58630 58715 58962 58965 59004 59015 59071 59174 59351 59630 59649 59780 59807 59827 59838 59849 59887 59926 59981 59988 60006 60089 60097 60224 60247 60273 60438 60488 60489 60648 60745 60861 60908 61045 61098 61278 61298 61420 61576 61649 61984 62185 62189 62229 62333 62362 62385 62423 62437 62477 62484 62487 62500 62552 62567x2 62576 62935 63199 63327 63486 63590 63759 63810 63891 64054 64095 64185 64341 64526 64570x2 64683 64809 64810 64828 64934 65001 65097 65110 65166 65279 65297 65651 65673 65780 65797 66000 66071 66131 66266 66479 66508 66613 66705 66719 66761 67357 67501 67559 67607 67612 67783 67862 67875 67920 67931x2 68069 68125 68293 68314 68405 68522 68623 68642 68743 68845 68879 69145 69187 69195 69257 69340 69383 69451 69510 69564 69641 69682 69751 69868 69901 69936 70075 70223 70309 70347 70356 70547 70690 70730 70898 70915 70983 71089 71287 71430 71481 71495 71507 71564 71638 71700 71864 71951 72008 72089 72336 72558 72665 72776 72985 73370 73612 73719 73773 73786 73866 73929 73972 73987 74545 74801 74838 74860 74976 74983 75016 75029 75032 75165 75305 75464 75614 75619 75655 75741 75804 75870 76318 76647 76731 76839 76872 77022 77103 77129 77259 77268 77361 77362 77467 77504 77643 77684 77715 77840 77854 77860 78018 78020 78100 78128 78274 78305 78308 78324 78499 78562 78634 78702 78920 79020 79130 79359 79657 80031 80123 80257 80275 80562 80645 80720 80746 80783 81120 81149 81250 81424 81518 81527 81627 81745 81834 81835 81862 81903 82029 82118 82249 82361 82368 82410 82413 82806 82827 82933 83083 83086 83163 83291 83314 83333 83395 83418 83658 83979 84038 84078 84099 84417 84712 84790 84927 85011 85045 85105 85441 85539 85572 85954 85970 86023 86115 86226 86240 86250 86336 86435 86437 86447 86573 86895 86928 86960 87081 87141 87190 87355 87460 87812 88035 88043 88104 88200 88208 88213 88315 88660 88759 88856 89027 89464 89549 89556 89716 89723x2 89729 89736 89776 89841 89850 90085 90233 90285 90403 90437 90519 90669 90683 90725 90922 91003 91034 91066 91113 91396 91638 91711 91728 91860 91910 91932 91950 91981 92224 92282 92323 92526 92683 92716 92728 93083 93376 93476 93598 93660 93755 93859 93903 94232 94330 94402 94422 94497 94603 94610 94669 95228 95289 95295 95481 95926 95998 96131 96238 96289 96317 96489 96571 96659 96672 96901 97105 97211 97320 97512 97600 97827 97836 97927 98197 98227 98251 98434 98477 98537 98560 98622 98675 98906 99045 99088 99452 99484 99503 99524 99557 99625 99629 99684 99775 99950 100032 100082 100156 100316 100357 100546 100569 100580 100872 100898 100919 101159 101279 101414 101428 101677 101816 101958 102439 102510 102544 102735 102780 102853 102864 103028 103063 103243 103413 103426 103694 103718 103901 104142 104282 104320 104351 104544 105261 105508 105523 105563 105753 105803 105829 106177 106204 106221 106240 106382 106385 106497 106568 106898 106981 107043 107170 107461 107500 107517 107531 107628 107779 108542 108556 108746 109149 109391 109568 109787 110282 110401 110678 110846 111122 111262 111357 111434 111549 111894 112313 112435 112529 112664 113535 113691 114155 114213 114236 114242 114377 114600 114694 114860 114882 114982 115201 115203 115326 115416 115559 115585 115737 115903 116004 116133 116248 116327 116341 116383 116485 116511 116514 116518 116686 116733 116853 116931 117047 117106 117197 117213 117262 117451 117523 117664 117703 117975 118059 118121 118169 118547 118575 118637 118694 118697 118786 118797 119027 119134 119250 119594 119959 119960 120062 120101 120109 120251 120273 120508 121186 121729 122066 122291 122306 122333 122749 122813 123045 123218 123326 123400 123531 124706 124830 124881 125195 125196 125476 125507 125508 125653 125716 125722 125724 125814 125891 126103 126288 126346 126470 126530 126587 126603 126612 127003 127275 127283 127519 127583 127700 128494 128537 128669 129217 129768 129779 130284 130510 130605 130938 131218 131274 131747 131829 132100 132173 132278 132346 132481 132808 132856 132926 133180 133242 133908 134215 134306 135578 135767 136119 136289 136658 136856 136951 137077 137285 137318 137443 137462 137719 137768 137858 137973 137996 138054 138228 138292 138603 138779 139316 139381 139395 139805 140175 140531 140558 140633 141170 141369 141411 141643 141811 141816 141856 141952 142429 142682 143053 143221 143902 143933 144370 144400 145180 145275 145893 146000 146557 146685 146889 147057 147219 147230 147717 147784 147829 147895 148039 148176 148971 149260 149383 149432 149635 150000 150276 150398 150527 150543 150556 150900 151723 151731 151793 151874 152395 152575 152984 153218 153418 153828 153834 154153 154865 155018 155114 155575 155863 156131 156857 156901 157465 157530 157674 157809 158077 158523 158590 159233 159575 159576 160530 160986 161893 162899 163597 163826 166114 166236 166426 166442 166929 167159 167325 167372 167610 167812 168897 169121 170379 171063 171142 171915 172232 172233 173312 173668 175226 175306 175850 176699 177170 177478 178016 180768 181375 182169 182226 185695 186449 186954 188426 190451 193004 194915 195377 195815 198161 198835 202231 202423 203602 204017 204051 204162 205805 210595 215788 217620 225648 229366 235870 236011
``

``
width 36 (300 walks, sum 95897358):
3158 21134 32991 51511 55596 63038 65275 66841 67032 69268 70140 72362 73751 77846 82600 83909 84254 85181 85830 87633 88365 89455 89965 90829 91955 97985 99846 105729 110000 116827 117216 118282 119395 120112 125313 125472 125594 125989 131184 131482 135724 137356 138777 139535 141625 147707 147843 148308 149804 151509 152130 152707 156046 157523 159222 161535 161889 164863 165761 168566 168638 169208 169819 169847 169894 173381 176588 176678 177742 179172 179644 184501 184617 185019 185161 185636 185830 186112 187481 188775 191129 198313 198416 199283 202145 202234 204238 204302 205008 205322 205646 206350 206708 207021 208629 208855 210784 214406 219137 219436 221683 222420 222626 224919 225883 227229 229072 229264 232001 232349 233442 233472 236438 236633 237107 237182 237334 237926 240343 240452 240812 243715 250560 251022 251518 256071 256514 261194 263431 264636 266232 268169 268281 269245 272803 277227 280859 281859 283822 284698 285369 285533 286094 287713 288780 290275 290799 290936 295043 295348 296561 297469 299047 299178 303277 303941 304602 304716 308851 311413 312429 312611 312772 314844 314999 315331 315699 319094 319525 320124 320201 320900 321508 322420 325369 327131 328648 330654 332078 333841 337332 338321 338841 338860 341247 342087 344215 344786 345170 346961 347606 350451 352328 358302 358888 359067 361791 363050 363949 363986 364055 366606 366647 370347 377625 384365 386867 387278 387836 396440 403722 404315 408307 412031 414208 415520 416203 417425 417744 418951 419266 422655 424117 424304 424633 425962 431133 433570 436286 437581 444875 445609 446432 447508 450781 451002 451783 452268 452885 454560 454731 456388 457128 458243 459973 467572 474976 477902 478006 481854 486476 491760 497096 500868 501263 502830 512016 515754 516802 524567 533418 537169 548429 553333 563362 572664 573351 573853 576022 576320 580983 581039 583228 589500 590932 595409 598342 602424 614004 618169 630525 641185 642461 644751 657971 662687 667119 677743 694972 696159 703116 710111 712240 720636 721090 762975 785704 792582 847486 1021303
``
