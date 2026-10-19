# Proof: generic birthday (distinguished-point rho) collision, Orchard Poseidon r=23

Target `poseidon-orchard-r23-prefix-v1` (Pallas P128Pow5T3, ConstantLength<2>, halo2_poseidon 0.2.0 pinned constants; 8 fixed full rounds around 23 partial rounds; digest = state[0], whole element compared). Attack class `ordinary-collision`. Cost model `orchard-field-ram-v2`: every field addition/subtraction/multiplication and every 256-bit word primitive is charged 1/C target compressions with C = 216 + 21*23 = 699; exponentiation/inversion are charged as their counted constituent operations. No asymptotic-only claim is made; every bound below is a finite number at the actual dimensions.

## 1. The claim

* `time_log2` = 126.64474 `target-compressions` (exact Decimal 126.644731; rounded **up** at 5 decimals).
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
LAMBDA = 0x1c402ca73c17b5bc5fdda9e57cea27f28529b69aa141504bab0f6543e852f392
```

U0, V0 solve the 2x2 linear system that fixes A's first two lanes through the capacity lane; A0 closes A's third lane; D1, D2 are B's first two lanes. message(W) inverts the line injectively: tau = W^d, U = U0 + a*tau, V = V0 + b*tau, m0 = U^d - C[0][0], m1 = V^d - C[0][1]; both are canonical field elements by construction. The attack fixes one random rho0 (low 254 bits of a PRG draw) and one random start x0 (a second PRG draw) and walks

F(x) = digest(message(x + rho0)) * LAMBDA mod p,

where the walk scale LAMBDA = (MDS[0][1] * M63[1]^5)^-1 mod p is folded into the round-63 row so the lane-1 coefficient stays 1 (Section 3). Two distinct walk values x != y with F(x) = F(y) give distinct W_x != W_y (message is injective), hence distinct canonical messages with equal digests: an ordinary collision.

## 3. The step program (519 charged operations per step)

| block | ops | breakdown |
| --- | ---: | --- |
| rounds 0-2, folded entry | 27 | 6 (t_k = QQ_k*x + Ptilde_k) + 9 (three S-boxes t_k^5) + 12 (round-2 linear layer in scaled bases) |
| round 3 (scaled bases) | 24 | 3 add + 9 S-box + 12 linear |
| entry rescale into partial basis | 0 | FOLDED into the round-3 tables: the partial phase opens in the round-3 output basis V(4) = M4 with offset kappa(4) = 0; zero runtime operations |
| 23 partial rounds 4..26 | 368 | 16 each: 1 add (sig_0 + kappahat0_i), 3 S-box (t0h), 6 mult + 6 add linear with exactly one unit coefficient per row (units (0,1), (1,0), (2,1) via per-round output scalings V(i+1) = (MDS[0][1]*V_1, MDS[1][0]*V_0^5, MDS[2][1]*V_1); every basis, offset and coefficient is an offline import-time constant) |
| rounds 60-62 (scaled bases) | 72 | 24 each: 3 add + 9 S-box + 12 linear; partial-phase exit constants folded into round 60 |
| round 63 (output lane only) | 16 | 3 add + 9 S-box + 2 mult + 2 add (row B63R with LAMBDA folded; lane-1 coefficient 1) |
| dp test + loop control + state traffic | 12 | x load 1, three Ptilde loads, dp mask 1, dp threshold compare 1, dp decision branch 1, counter increment 1, loop compare 1, loop branch 1, x store 1 = 12 exactly (comparison and conditional branch are separate primitives) |
| **total per step** | **519** | |

The partial rounds run in per-round output-scaled bases: the state after round 3 enters at V(4) = M4 (the round-3 output basis itself, so the entry rescale of the earlier filings is folded and costs nothing); each partial round i rescales by V(i+1) = (MDS[0][1]*V_1, MDS[1][0]*V_0^5, MDS[2][1]*V_1), so the update matrix Mhat_jk = MDS[j][k]*B_k / V(i+1)_j (with B = (V_0^5, V_1, V_2)) carries its unit at (0,1), (1,0) or (2,1) - one unit per row - and the per-round offset kappa(i+1)_j = (MDS[j][1]*V_1*kappa_1 + MDS[j][1]*C[i][1] + MDS[j][2]*V_2*kappa_2 + MDS[j][2]*C[i][2]) / V(i+1)_j is folded offline into the single addition sig_0 + kappahat0_i. Bases chain M3 (after round 2), M4 (after round 3), V(4)..V(27) (partial phase), M61..M63 (rounds 60-62). A companion-form (Krylov) detertour was evaluated and rejected numerically: +12 ops/round of basis conversion against -2/round saved; the fixed-basis 17-op form of the earlier filings is superseded by this 16-op per-round form.

The step program equals digest(message(x + rho0)) * LAMBDA on 64 of 64 random (x, rho0) trials against the organizer's trusted reference permutation (`--selftest`), and its per-step ledger totals exactly 519. Every field multiplication/addition and every word primitive in the actual code path is counted; no operation is uncharged.


## 4. The search: one trail, distinguished points, index table, recovery

A walk value is distinguished iff its low 128 bits are < 38176; the threshold is below 2^16, so the low 16 bits determine the low 128 bits among dp values and a stored key (high 126 bits, low 16 bits) is injective on dp values. Exactly D = (2^126 + 1) * 38176 of the p field elements are distinguished (p = 2^254 + c with c = p mod 2^128 >= 38176), theta = D/N in [10^-33.95009, 10^-33.95005] (conditioning bounds theta_lo = (D - 2^128)/N, theta_hi = D/(N - 2^128)).

The algorithm (Appendix B, `full_search`): draw the coins rho0 and x0 (two PRG draws); walk x_{i+1} = F(x_i) from x0 for at most S1 = n1 + d steps (82458658022075887745892673130667924 = detection window, Section 5). Each distinguished value is probed in the table (at most 137,081 word operations per dp event: a full scan of the packed 27,413-entry table at 5 word operations per probe + 16) and, if new, stored with its trail index: one 32-byte word holding the high 126 bits of the value and the index, plus a 16-bit side field holding the low 16 bits. A distinguished value can be reconstructed exactly from its word and side field (injectivity above). Distinguished values on the tail never repeat (a cycle value cannot equal a tail value); the first repeat of a stored dp value detects the cycle.

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

Solving 1 - fail(n) >= 0.39 in 80-digit Decimal gives the tight random-function trail budget n0 = 169346087099996799090729207472420809487 (success at n0 exactly 0.390000000...). The filed budget below scales this by the measured hazard floor.

## 6. Premise H1 and the filed budget

H1 (`H1-random-walk-rate`), the only premise of the claim.
* Statement: the filed trail has n1 = 178514977233407124990816098423499042677 steps, at which the lemma of Section 5 with the repeat hazard scaled by c = 0.90 (see below) bounds the success at exactly 0.39. Premise: for the attempt's coins (rho0 and x0, uniform 254-bit words), the search of Section 4 on the real map F(x) = digest(message(x + rho0)) * LAMBDA, at the trail budget n1, succeeds with probability at least 0.39. **H1 is our theory that, for this search, the fixed map with a random rho0 behaves like a uniformly random function; this is an assumption and no proof is known.**
* Role: score-critical. It is the only step from the lemma to the claimed success probability; the step program (Section 3), the search and recovery (Section 4), the ledger (Section 7) and the memory (Section 8) are proved or checked exactly.
* Scope: target poseidon-orchard-r23-prefix-v1, inputs on the line of Section 2, one search with the parameters of Section 4 (walk budget S1 = 178597435891429200878561991096629710601). Not claimed for other round counts or budgets.

Budget and tolerance. Within the hazard-multiplier family (the real map's per-step repeat hazard is a constant multiple c of the random-function hazard), the repeat term of the lemma scales as exp(-c x) with x = n(n+1)/(2p); the other failure terms are unchanged. The filed budget n1 is the smallest trail budget at which the premise survives **every hazard factor c >= 0.90**: at n1 (x = 0.55043), the success at the floor c = 0.90 is exactly 0.39 by construction, and the random function (c = 1) reaches 0.4226. The floor 0.90 lies **below the smallest 95% lower bound measured at any width (0.9080 at w = 36)**, so the reduced-width evidence dominates the tolerance: every measured cell's 95% profile-likelihood lower bound exceeds the floor, as in the incumbent r=23 filing (their floor 0.511 lay below every measured lower bound). A hazard factor above the random one only helps and is tolerated without bound.

Evidence (participant-run; the organizer-run experiment is Section 10): first-repeat walks on the real r=23 map truncated to w bits (the truncated map is the birthday model at width w), fresh (rho, start) per walk, every walk run to its exact first repeat, 16380 walks over six widths, exact discrete first-repeat likelihood P(L=l|m) = (m*l/N) * prod_(j<l) (1 - m*j/N) (series-summed with bounded tail), profile-likelihood 95% intervals:

| width w | walks | hazard multiplier m-hat | 95% profile-likelihood CI | series tail bound |
| ---: | ---: | ---: | --- | ---: |
| 16 | 1320 | 1.0145 | [0.9609, 1.0701] | 2.9e-06 |
| 20 | 6120 | 0.9936 | [0.9689, 1.0187] | 5.0e-08 |
| 24 | 6120 | 1.0143 | [0.9891, 1.0399] | 0.0e+00 |
| 28 | 1320 | 1.0190 | [0.9650, 1.0750] | 0.0e+00 |
| 32 | 1200 | 0.9800 | [0.9256, 1.0365] | 0.0e+00 |
| 36 | 300 | 1.0190 | [0.9080, 1.1387] | 0.0e+00 |

Pooled multiplier 1.0044, 95% profile-likelihood CI [0.9891, 1.0198]; the per-width estimates are consistent with a constant multiplier across widths (no slope). Seeds and stopping rule: each walk draws rho0 uniform on 254 bits and a start uniform on 2^w from an independent seeded stream (Appendix C, `measure2.py` per-chunk seeds); every walk ran to its first repeat, none was dropped, repeated or selected; there is no stopping rule. The exact discrete law is used throughout; no exponential or Gamma approximation of the first-repeat index enters the estimates.

Sensitivity at the filed budget S1 (repeat term x = 0.55043; other eps terms 6.6e-04):

| hazard factor c | 1.0198 (pooled upper) | 1 (random) | 0.9891 (pooled lower) | 0.9256 (w=32 lower) | 0.9080 (w=36 lower) | 0.90 (floor) | 0.85 (below floor) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| success at S1 | 0.4289 | 0.4226 | 0.4192 | 0.3985 | 0.3927 | 0.3900 | 0.3730 |

Extrapolation: from widths 16 to 36 at r = 23, where the multiplier is measured, to width 254 at r = 23, by H1. The measurements show that the random-function first-repeat law holds on the real round function at every measured width, and every measured lower bound lies above the tolerance floor; they do not bound the multiplier at full width. The full-width first repeat cannot be observed at feasible cost, so the transfer is the premise itself.

Limitations: the measurements are reduced-width only (16 to 36 bits, first-repeat indexes of order 2^19 steps); they say nothing about the 254-bit map beyond the premise. The interval is a profile-likelihood interval, asymptotic in the number of walks and conditional on the hazard-multiplier family; it is evidence about the multiplier, not a bound on it. The organizer experiment (Section 10) is one width (14 bits), one round count, a witness-only event on the digest, and cannot validate H1, the cost or the success probability. On a single fixed map the success over starts varies with that map's cycle structure; the attempt therefore draws rho0 as a coin, and H1 concerns the average over rho0.

## 7. Ledger at the filed budget

```
walk budget S1 = n1 + d  = 178597435891429200878561991096629710601   (trail 178514977233407124990816098423499042677 + detection window 82458658022075887745892673130667924)
dp threshold                = 38176 (low 128 bits); D = (2^126 + 1) * 38176
theta_lo = (D - 2^128)/p   = 10^-33.95009
theta_hi = D/(p - 2^128)   = 10^-33.95005
d (detection window)       = 82458658022075887745892673130667924   = ceil(9.25/theta_lo) rounded up to 4
gmax (gap cap)             = 176060377939026895457446518306020702   = ceil(19.75/theta_lo) + 2
MCAP                       = 27413 entries
per-step ops               = 519  (listing in Section 3)
walk ops    S1 * 519       = 92692069227651755255973673379150819801919.00
units = total / C, C = 699 = 133003382436202750524061733401553053033.39198855507868383404864091559370529327611
time_log2 = log2(units)     = 126.644731
filed                       = 126.64474 (rounded up at 5 decimals)
```

For reference against the frontier: the incumbent ab786fc files 126.74586 at 1.3993*n0 with success 0.62 under its own convention; at the tight n0/0.39 convention the r=23 random function scores 126.56893. This entry's 126.64474 beats the incumbent by 0.1011 bits: the exact solve plus the detection-window/gap-cap recovery convention (their 3 gmax) costs 0.0758 bits over the tight random-function score, against their 0.4847 bits of probability margin.
## 8. Memory

Peak live set: 27,413 dp entries * 32 bytes (877,216) + 27,413 side fields * 2 bytes (54,826) + one 32-byte start word + 103,644 code + 5,600 constants + 7,200 registers = 1,048,518 bytes < 2^20 = 1,048,576. Every table item is one aligned 32-byte word: entry k at TAB0 + 32k holds (high 126 bits of the dp value) OR (its index < 2^128); the side word holds the 16-bit low part. Lookups extract the high part and compare, then the side field; reconstruction shifts the high part back and appends the side field (threshold < 2^16 makes this exact). Memory penalty max(0, log2(1,048,518) - 20) = 0; filed memory_log2_bytes = 20.

## 9. Preprocessing (inside time)

All constants (the line constants of Section 2; the per-round partial bases V(4)..V(27) with their folded unit coefficients; the kappa-folded per-round offsets kappahat0_i; the round-3 scaled bases; the folded exit constants at round 60; C60..C63, B60..B62, B63R; LAMBDA) and the budget solve (80-digit Decimal bisections on n0 and n1) are offline. Their derivation, together with the participant's 16,380-walk H1 measurement campaign (the evidence of Section 6: 263675434 measured walk steps, each at most 6 harness word operations plus one 519-op step evaluation, at most 138429602850 <= 2^37 word operations), is construction/preprocessing under orchard-field-ram-v2 and is bounded by 2^41 word operations (constant derivation: 64 rounds of short reciprocal/fifth-power chains, a few hundred word operations each; budget solve: a few hundred 80-digit Decimal exp/log evaluations, each < 2^10 word operations; campaign as stated), charged inside time_log2 in the ledger line "offline derivation" (2^41/699 = 3145956016 compressions), and declared as preprocessing_log2 = 32 (= ceil(log2(3145956016))). The measurement analysis of Section 6 is evidence generation for H1, not attack preprocessing beyond the campaign charged above; it is disclosed as such. The search program itself uses only integer literals (WALK, DETECT, GMAXC, DVAL, DPMASK, MCAP); nothing is derived online.

## 10. Organizer experiment (declared)

`lowbits-birthday` (python-message-pairs-v1, digest-xor-mask on the first 14 bits): per trial, at most 1200 fresh canonical 64-byte messages derived deterministically from the supplied seed; the program returns a pair whose r=23 digests agree on the masked bits. Local run of the same event: 256/256 verified pairs in 5.0 s single-CPU (mean ~144 draws per trial), byte-identical on repeat. It is a reduced-width witness on the digest only; it does not establish H1, the cost bound, or the success probability (a 14-bit event cannot separate hazard multipliers near 0.5 from 1).

## 11. Verification

The step program, the search with its recovery, the budget solve, the measurement harness and the analysis sources are embedded verbatim as appendices below (A: `myrho.py` - step program, line and tables, selftest; B: `attack.py` - the filed single-trail search, recovery, exact plan, reduced-width end-to-end selftest, H1 measurement mode; C: `measure2.py` + `analysis.py` - H1 evidence and exact likelihood intervals). All are standard-library-only Python 3, deterministic given their seeds. Exercised locally: `myrho.py --selftest` 64/64 against the trusted reference; `attack.py --selftest` 64/64 plus two-of-three reduced-width searches (one pair abandoned at the test gap cap); `attack.py --plan` prints the exact ledger of Section 7; Appendices C produced the Section 6 table (with `attack.py --measure` seeding widths 16..28).
## Appendix A: `myrho.py` (line, tables, LEAN step program at 519 ops, selftest)

Line construction, the per-round output-scaled partial bases with folded offsets, the register-held constants and the counted `step()` at exactly 519 charged operations; `--selftest` runs the 64-trial check against `ref_permute` (the organizer's verifier semantics) plus the per-step ledger reconciliation.

```python
#!/usr/bin/env python3
"""r=23 Orchard Poseidon generic birthday attack, LEAN step program.

Distinguished-point single-trail rho on the line of message(W); the walk
step is F(x) = digest(message(x + rho0)) * LAMBDA with LAMBDA rescaling the
digest lane to the walk scale.  This variant charges the equivalent-form
family honestly and minimally:

* rounds 0..2 block: 27 field ops (entry t-forming 3 mult + 3 add, three
  S-boxes 9, rescaled linear layer 6 mult + 6 add);
* round 3: 24 (3 add + 9 S-box + 12 linear); the partial-phase entry
  rescale is FOLDED into the round-3 tables (the partial phase opens in
  the round-3 output basis V(4) = M4 with kappa(4) = 0; zero runtime ops);
* each of the 23 partial rounds 4..26: 16 field ops -- 1 add (t0), 3
  S-box, 6 mult + 6 add linear with one unit coefficient per row (units
  (0,1), (1,0), (2,1) via per-round output scalings V(i+1) =
  (MDS01*V1, MDS10*V0^5, MDS21*V1); every basis, offset and coefficient
  is an offline constant computed once at import);
* rounds 60..62: 24 each; round 63: 16; dp test + loop control + state
  traffic 12 word ops (x load 1, 3 ptilde loads, dp mask 1, dp threshold
  compare 1, dp decision branch 1, counter increment 1, loop compare 1,
  loop branch 1, x store 1 = 12 exactly; comparison and conditional
  branch are separate primitives).
STEP_OPS = 27 + 24 + 23*16 + 3*24 + 16 + 12 = 519.  All round
constants are computed once at import (offline derivation; the setup
loads are charged in the ledger setup line) and held in registers; no
per-step table loads.  Cost model orchard-field-ram-v2,
C = 216 + 21*23 = 699.
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


def message(W):
    tau = pow(W, D_EXP, P)
    U = (U0 + a_ * tau) % P
    V = (V0L + b_ * tau) % P
    m0 = (pow(U, D_EXP, P) - C[0][0]) % P
    m1 = (pow(V, D_EXP, P) - C[0][1]) % P
    return m0, m1


# ---------------- offline derivation (setup; no per-step loads) --------
def full_round_tables(i, m):
    m5 = [pow(mk, 5, P) for mk in m]
    mp = [(MDS[j][1] * m5[1]) % P for j in range(3)]
    ctilde = [(C[i][k] * inv(m[k])) % P for k in range(3)]
    B = [[(MDS[j][0] * m5[0] * inv(mp[j])) % P, 1,
          (MDS[j][2] * m5[2] * inv(mp[j])) % P] for j in range(3)]
    return ctilde, B, mp


C2T, B2T, M3 = full_round_tables(2, (1, 1, 1))
C3T, B3T, M4 = full_round_tables(3, M3)

# lean per-round partial bases: V(4) = M4 (entry folded); V(i+1) =
# (MDS01*V1, MDS10*V0^5, MDS21*V1); units (0,1) (1,0) (2,1) each round.
V = [None] * (R + 5)
V[4] = tuple(M4)
KH0L = [None] * R
M00L = [None] * R
M02L = [None] * R
M11L = [None] * R
M12L = [None] * R
M20L = [None] * R
M22L = [None] * R
kap = [None] * (R + 5)
kap[4] = (0, 0, 0)
for _i in range(4, 4 + R):
    V0, V1, V2 = V[_i]
    V[_i + 1] = ((MDS[0][1] * V1) % P,
                 (MDS[1][0] * pow(V0, 5, P)) % P,
                 (MDS[2][1] * V1) % P)
    W0, W1, W2 = V[_i + 1]
    _k = kap[_i]
    _b0 = pow(V0, 5, P)
    KH0L[_i - 4] = (_k[0] + C[_i][0] * inv(V0)) % P
    M00L[_i - 4] = (MDS[0][0] * _b0 * inv(W0)) % P
    M02L[_i - 4] = (MDS[0][2] * V2 * inv(W0)) % P
    M11L[_i - 4] = (MDS[1][1] * V1 * inv(W1)) % P
    M12L[_i - 4] = (MDS[1][2] * V2 * inv(W1)) % P
    M20L[_i - 4] = (MDS[2][0] * _b0 * inv(W2)) % P
    M22L[_i - 4] = (MDS[2][2] * V2 * inv(W2)) % P
    assert (MDS[0][1] * V1 * inv(W0)) % P == 1
    assert (MDS[1][0] * _b0 * inv(W1)) % P == 1
    assert (MDS[2][1] * V1 * inv(W2)) % P == 1
    kap[_i + 1] = tuple(
        ((MDS[j][1] * V1 * _k[1] + MDS[j][1] * C[_i][1]
           + MDS[j][2] * V2 * _k[2] + MDS[j][2] * C[_i][2]) % P)
        * inv(Wj) % P for j, Wj in enumerate(V[_i + 1]))
V27 = V[4 + R]
K27 = kap[4 + R]

C60T, B60T, M61 = full_round_tables(60, V27)
C60T = [(C60T[k] + K27[k]) % P for k in range(3)]
C61T, B61T, M62 = full_round_tables(61, M61)
C62T, B62T, M63 = full_round_tables(62, M62)
LAMBDA = inv(MDS[0][1] * pow(M63[1], 5, P)) % P
C63T = [(C[63][k] * inv(M63[k])) % P for k in range(3)]
B63R0 = (MDS[0][0] * pow(M63[0], 5, P) * LAMBDA) % P
B63R2 = (MDS[0][2] * pow(M63[2], 5, P) * LAMBDA) % P

# register-held constants (one-time setup loads, charged in the ledger
# setup line; the step body below never indexes a table)
QQ_0, QQ_1, QQ_2 = QQ
B2_00 = B2T[0][0]
B2_02 = B2T[0][2]
B2_10 = B2T[1][0]
B2_12 = B2T[1][2]
B2_20 = B2T[2][0]
B2_22 = B2T[2][2]
C2_0, C2_1, C2_2 = C2T
B3_00 = B3T[0][0]
B3_02 = B3T[0][2]
B3_10 = B3T[1][0]
B3_12 = B3T[1][2]
B3_20 = B3T[2][0]
B3_22 = B3T[2][2]
C3_0, C3_1, C3_2 = C3T
KH0_4 = KH0L[0]
KH0_5 = KH0L[1]
KH0_6 = KH0L[2]
KH0_7 = KH0L[3]
KH0_8 = KH0L[4]
KH0_9 = KH0L[5]
KH0_10 = KH0L[6]
KH0_11 = KH0L[7]
KH0_12 = KH0L[8]
KH0_13 = KH0L[9]
KH0_14 = KH0L[10]
KH0_15 = KH0L[11]
KH0_16 = KH0L[12]
KH0_17 = KH0L[13]
KH0_18 = KH0L[14]
KH0_19 = KH0L[15]
KH0_20 = KH0L[16]
KH0_21 = KH0L[17]
KH0_22 = KH0L[18]
KH0_23 = KH0L[19]
KH0_24 = KH0L[20]
KH0_25 = KH0L[21]
KH0_26 = KH0L[22]
M00_4 = M00L[0]
M00_5 = M00L[1]
M00_6 = M00L[2]
M00_7 = M00L[3]
M00_8 = M00L[4]
M00_9 = M00L[5]
M00_10 = M00L[6]
M00_11 = M00L[7]
M00_12 = M00L[8]
M00_13 = M00L[9]
M00_14 = M00L[10]
M00_15 = M00L[11]
M00_16 = M00L[12]
M00_17 = M00L[13]
M00_18 = M00L[14]
M00_19 = M00L[15]
M00_20 = M00L[16]
M00_21 = M00L[17]
M00_22 = M00L[18]
M00_23 = M00L[19]
M00_24 = M00L[20]
M00_25 = M00L[21]
M00_26 = M00L[22]
M02_4 = M02L[0]
M02_5 = M02L[1]
M02_6 = M02L[2]
M02_7 = M02L[3]
M02_8 = M02L[4]
M02_9 = M02L[5]
M02_10 = M02L[6]
M02_11 = M02L[7]
M02_12 = M02L[8]
M02_13 = M02L[9]
M02_14 = M02L[10]
M02_15 = M02L[11]
M02_16 = M02L[12]
M02_17 = M02L[13]
M02_18 = M02L[14]
M02_19 = M02L[15]
M02_20 = M02L[16]
M02_21 = M02L[17]
M02_22 = M02L[18]
M02_23 = M02L[19]
M02_24 = M02L[20]
M02_25 = M02L[21]
M02_26 = M02L[22]
M11_4 = M11L[0]
M11_5 = M11L[1]
M11_6 = M11L[2]
M11_7 = M11L[3]
M11_8 = M11L[4]
M11_9 = M11L[5]
M11_10 = M11L[6]
M11_11 = M11L[7]
M11_12 = M11L[8]
M11_13 = M11L[9]
M11_14 = M11L[10]
M11_15 = M11L[11]
M11_16 = M11L[12]
M11_17 = M11L[13]
M11_18 = M11L[14]
M11_19 = M11L[15]
M11_20 = M11L[16]
M11_21 = M11L[17]
M11_22 = M11L[18]
M11_23 = M11L[19]
M11_24 = M11L[20]
M11_25 = M11L[21]
M11_26 = M11L[22]
M12_4 = M12L[0]
M12_5 = M12L[1]
M12_6 = M12L[2]
M12_7 = M12L[3]
M12_8 = M12L[4]
M12_9 = M12L[5]
M12_10 = M12L[6]
M12_11 = M12L[7]
M12_12 = M12L[8]
M12_13 = M12L[9]
M12_14 = M12L[10]
M12_15 = M12L[11]
M12_16 = M12L[12]
M12_17 = M12L[13]
M12_18 = M12L[14]
M12_19 = M12L[15]
M12_20 = M12L[16]
M12_21 = M12L[17]
M12_22 = M12L[18]
M12_23 = M12L[19]
M12_24 = M12L[20]
M12_25 = M12L[21]
M12_26 = M12L[22]
M20_4 = M20L[0]
M20_5 = M20L[1]
M20_6 = M20L[2]
M20_7 = M20L[3]
M20_8 = M20L[4]
M20_9 = M20L[5]
M20_10 = M20L[6]
M20_11 = M20L[7]
M20_12 = M20L[8]
M20_13 = M20L[9]
M20_14 = M20L[10]
M20_15 = M20L[11]
M20_16 = M20L[12]
M20_17 = M20L[13]
M20_18 = M20L[14]
M20_19 = M20L[15]
M20_20 = M20L[16]
M20_21 = M20L[17]
M20_22 = M20L[18]
M20_23 = M20L[19]
M20_24 = M20L[20]
M20_25 = M20L[21]
M20_26 = M20L[22]
M22_4 = M22L[0]
M22_5 = M22L[1]
M22_6 = M22L[2]
M22_7 = M22L[3]
M22_8 = M22L[4]
M22_9 = M22L[5]
M22_10 = M22L[6]
M22_11 = M22L[7]
M22_12 = M22L[8]
M22_13 = M22L[9]
M22_14 = M22L[10]
M22_15 = M22L[11]
M22_16 = M22L[12]
M22_17 = M22L[13]
M22_18 = M22L[14]
M22_19 = M22L[15]
M22_20 = M22L[16]
M22_21 = M22L[17]
M22_22 = M22L[18]
M22_23 = M22L[19]
M22_24 = M22L[20]
M22_25 = M22L[21]
M22_26 = M22L[22]
QA60_00 = B60T[0][0]
QA60_02 = B60T[0][2]
QA60_10 = B60T[1][0]
QA60_12 = B60T[1][2]
QA60_20 = B60T[2][0]
QA60_22 = B60T[2][2]
A60C_0, A60C_1, A60C_2 = C60T
QA61_00 = B61T[0][0]
QA61_02 = B61T[0][2]
QA61_10 = B61T[1][0]
QA61_12 = B61T[1][2]
QA61_20 = B61T[2][0]
QA61_22 = B61T[2][2]
A61C_0, A61C_1, A61C_2 = C61T
QA62_00 = B62T[0][0]
QA62_02 = B62T[0][2]
QA62_10 = B62T[1][0]
QA62_12 = B62T[1][2]
QA62_20 = B62T[2][0]
QA62_22 = B62T[2][2]
A62C_0, A62C_1, A62C_2 = C62T
C63_0, C63_1, C63_2 = C63T
Q63R0, Q63R2 = B63R0, B63R2


def walk_ptilde(rho0):
    PPp = tuple((PP[j] + rho0 * QQ[j]) % P for j in range(3))
    return tuple((PPp[j] + C[2][j]) % P for j in range(3))


OPS = {'block02': 27, 'full': 24, 'partial': 16, 'r63': 16, 'dp': 12}
STEP_OPS = (OPS['block02'] + OPS['full'] + R * OPS['partial']
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
    p0, p1, p2 = ptilde
    # rounds 0..2 block: entry t-forming, three S-boxes, rescaled linear
    t0 = (QQ_0 * x + p0) % P
    t1 = (QQ_1 * x + p1) % P
    t2 = (QQ_2 * x + p2) % P
    led.mult += 3; led.add += 3
    y0, y1, y2 = _sbox(t0, led), _sbox(t1, led), _sbox(t2, led)
    s0 = (B2_00 * y0 + y1 + B2_02 * y2) % P
    s1 = (B2_10 * y0 + y1 + B2_12 * y2) % P
    s2 = (B2_20 * y0 + y1 + B2_22 * y2) % P
    led.mult += 6; led.add += 6
    # round 3 (scaled bases)
    t0 = (s0 + C3_0) % P
    t1 = (s1 + C3_1) % P
    t2 = (s2 + C3_2) % P
    led.add += 3
    y0, y1, y2 = _sbox(t0, led), _sbox(t1, led), _sbox(t2, led)
    s0 = (B3_00 * y0 + y1 + B3_02 * y2) % P
    s1 = (B3_10 * y0 + y1 + B3_12 * y2) % P
    s2 = (B3_20 * y0 + y1 + B3_22 * y2) % P
    led.mult += 6; led.add += 6
    # entry rescale FOLDED: the partial phase opens in the round-3 output
    # basis V(4) = M4 with kappa(4) = 0; zero runtime ops.
    # partial round 4: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_4) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_4 * t0h + s1 + M02_4 * s2) % P,
                  (t0h + M11_4 * s1 + M12_4 * s2) % P,
                  (M20_4 * t0h + s1 + M22_4 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 5: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_5) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_5 * t0h + s1 + M02_5 * s2) % P,
                  (t0h + M11_5 * s1 + M12_5 * s2) % P,
                  (M20_5 * t0h + s1 + M22_5 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 6: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_6) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_6 * t0h + s1 + M02_6 * s2) % P,
                  (t0h + M11_6 * s1 + M12_6 * s2) % P,
                  (M20_6 * t0h + s1 + M22_6 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 7: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_7) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_7 * t0h + s1 + M02_7 * s2) % P,
                  (t0h + M11_7 * s1 + M12_7 * s2) % P,
                  (M20_7 * t0h + s1 + M22_7 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 8: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_8) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_8 * t0h + s1 + M02_8 * s2) % P,
                  (t0h + M11_8 * s1 + M12_8 * s2) % P,
                  (M20_8 * t0h + s1 + M22_8 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 9: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_9) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_9 * t0h + s1 + M02_9 * s2) % P,
                  (t0h + M11_9 * s1 + M12_9 * s2) % P,
                  (M20_9 * t0h + s1 + M22_9 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 10: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_10) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_10 * t0h + s1 + M02_10 * s2) % P,
                  (t0h + M11_10 * s1 + M12_10 * s2) % P,
                  (M20_10 * t0h + s1 + M22_10 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 11: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_11) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_11 * t0h + s1 + M02_11 * s2) % P,
                  (t0h + M11_11 * s1 + M12_11 * s2) % P,
                  (M20_11 * t0h + s1 + M22_11 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 12: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_12) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_12 * t0h + s1 + M02_12 * s2) % P,
                  (t0h + M11_12 * s1 + M12_12 * s2) % P,
                  (M20_12 * t0h + s1 + M22_12 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 13: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_13) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_13 * t0h + s1 + M02_13 * s2) % P,
                  (t0h + M11_13 * s1 + M12_13 * s2) % P,
                  (M20_13 * t0h + s1 + M22_13 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 14: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_14) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_14 * t0h + s1 + M02_14 * s2) % P,
                  (t0h + M11_14 * s1 + M12_14 * s2) % P,
                  (M20_14 * t0h + s1 + M22_14 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 15: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_15) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_15 * t0h + s1 + M02_15 * s2) % P,
                  (t0h + M11_15 * s1 + M12_15 * s2) % P,
                  (M20_15 * t0h + s1 + M22_15 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 16: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_16) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_16 * t0h + s1 + M02_16 * s2) % P,
                  (t0h + M11_16 * s1 + M12_16 * s2) % P,
                  (M20_16 * t0h + s1 + M22_16 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 17: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_17) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_17 * t0h + s1 + M02_17 * s2) % P,
                  (t0h + M11_17 * s1 + M12_17 * s2) % P,
                  (M20_17 * t0h + s1 + M22_17 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 18: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_18) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_18 * t0h + s1 + M02_18 * s2) % P,
                  (t0h + M11_18 * s1 + M12_18 * s2) % P,
                  (M20_18 * t0h + s1 + M22_18 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 19: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_19) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_19 * t0h + s1 + M02_19 * s2) % P,
                  (t0h + M11_19 * s1 + M12_19 * s2) % P,
                  (M20_19 * t0h + s1 + M22_19 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 20: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_20) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_20 * t0h + s1 + M02_20 * s2) % P,
                  (t0h + M11_20 * s1 + M12_20 * s2) % P,
                  (M20_20 * t0h + s1 + M22_20 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 21: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_21) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_21 * t0h + s1 + M02_21 * s2) % P,
                  (t0h + M11_21 * s1 + M12_21 * s2) % P,
                  (M20_21 * t0h + s1 + M22_21 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 22: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_22) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_22 * t0h + s1 + M02_22 * s2) % P,
                  (t0h + M11_22 * s1 + M12_22 * s2) % P,
                  (M20_22 * t0h + s1 + M22_22 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 23: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_23) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_23 * t0h + s1 + M02_23 * s2) % P,
                  (t0h + M11_23 * s1 + M12_23 * s2) % P,
                  (M20_23 * t0h + s1 + M22_23 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 24: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_24) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_24 * t0h + s1 + M02_24 * s2) % P,
                  (t0h + M11_24 * s1 + M12_24 * s2) % P,
                  (M20_24 * t0h + s1 + M22_24 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 25: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_25) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_25 * t0h + s1 + M02_25 * s2) % P,
                  (t0h + M11_25 * s1 + M12_25 * s2) % P,
                  (M20_25 * t0h + s1 + M22_25 * s2) % P)
    led.mult += 6; led.add += 6
    # partial round 26: units (0,1) (1,0) (2,1)
    t0 = (s0 + KH0_26) % P; led.add += 1
    t0h = _sbox(t0, led)
    s0, s1, s2 = ((M00_26 * t0h + s1 + M02_26 * s2) % P,
                  (t0h + M11_26 * s1 + M12_26 * s2) % P,
                  (M20_26 * t0h + s1 + M22_26 * s2) % P)
    led.mult += 6; led.add += 6
    # rounds 60..62 (scaled bases, exit offsets folded at 60)
    # round 60 (scaled bases)
    t0 = (s0 + A60C_0) % P
    t1 = (s1 + A60C_1) % P
    t2 = (s2 + A60C_2) % P
    led.add += 3
    y0, y1, y2 = _sbox(t0, led), _sbox(t1, led), _sbox(t2, led)
    s0 = (QA60_00 * y0 + y1 + QA60_02 * y2) % P
    s1 = (QA60_10 * y0 + y1 + QA60_12 * y2) % P
    s2 = (QA60_20 * y0 + y1 + QA60_22 * y2) % P
    led.mult += 6; led.add += 6
    # round 61 (scaled bases)
    t0 = (s0 + A61C_0) % P
    t1 = (s1 + A61C_1) % P
    t2 = (s2 + A61C_2) % P
    led.add += 3
    y0, y1, y2 = _sbox(t0, led), _sbox(t1, led), _sbox(t2, led)
    s0 = (QA61_00 * y0 + y1 + QA61_02 * y2) % P
    s1 = (QA61_10 * y0 + y1 + QA61_12 * y2) % P
    s2 = (QA61_20 * y0 + y1 + QA61_22 * y2) % P
    led.mult += 6; led.add += 6
    # round 62 (scaled bases)
    t0 = (s0 + A62C_0) % P
    t1 = (s1 + A62C_1) % P
    t2 = (s2 + A62C_2) % P
    led.add += 3
    y0, y1, y2 = _sbox(t0, led), _sbox(t1, led), _sbox(t2, led)
    s0 = (QA62_00 * y0 + y1 + QA62_02 * y2) % P
    s1 = (QA62_10 * y0 + y1 + QA62_12 * y2) % P
    s2 = (QA62_20 * y0 + y1 + QA62_22 * y2) % P
    led.mult += 6; led.add += 6
    # round 63 (output lane, walk scale folded)
    t0 = (s0 + C63_0) % P
    t1 = (s1 + C63_1) % P
    t2 = (s2 + C63_2) % P
    led.add += 3
    y0, y1, y2 = _sbox(t0, led), _sbox(t1, led), _sbox(t2, led)
    out = (Q63R0 * y0 + y1 + Q63R2 * y2) % P
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
    total = led.mult + led.add + led.word
    assert abs(total - STEP_OPS) < 1e-9, (total, STEP_OPS)
    print(f'selftest OK on {trials} random (x, rho0)')
    print(f'per-step ops: mult={led.mult} add={led.add} word={led.word:.2f} '
          f'total={total:.2f} budget={STEP_OPS}')


if __name__ == '__main__':
    selftest()

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

    step_ops = Decimal('519')
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
    total = (Decimal(S1) * step_ops + rec_ops + table_ops + prg_ops + setup
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
        'per_step_ops': '519',
        'walk_ops': str(Decimal(S1) * step_ops),
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
    print(f'step selftest: {trials}/{trials} equal to reference*LAMBDA, '
          f'per-step={led.mult + led.add + led.word:.2f} (budget 519)')
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
