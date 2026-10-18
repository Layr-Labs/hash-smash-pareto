# Proof: generic birthday (distinguished-point rho) collision, Orchard Poseidon r=23

Target `poseidon-orchard-r23-prefix-v1` (Pallas P128Pow5T3, ConstantLength<2>, halo2_poseidon 0.2.0 pinned constants; 8 fixed full rounds around 23 partial rounds; digest = state[0], whole element compared). Attack class `ordinary-collision`. Cost model `orchard-field-ram-v2`: every field addition/subtraction/multiplication and every 256-bit word primitive is charged 1/C target compressions with C = 216 + 21*23 = 699; exponentiation/inversion are charged as their counted constituent operations. No asymptotic-only claim is made; every bound below is a finite number at the actual dimensions.

## 1. The claim

* `time_log2` = 126.69056 `target-compressions` (exact Decimal 126.690554; rounded **up** at 5 decimals).
* `memory_log2_bytes` = 20 (reviewed total 1,048,518 bytes < 2^20; normalized memory penalty max(0, 20 - 20) = 0).
* `success_probability` = 0.39 at the filed walk budget (Section 5 for the random-function lemma, Section 6 for the measured hazard transfer).
* `preprocessing_log2` = 15; all offline derivation is bounded and charged **inside** `time_log2` (Section 9, ledger line "offline derivation").
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

## 3. The step program (535.75 charged operations per step)

| block | ops | breakdown |
| --- | ---: | --- |
| rounds 0-2, folded entry | 27 | 6 (t_k = QQ_k*x + Ptilde_k) + 9 (three S-boxes t_k^5) + 12 (round-2 linear layer in scaled bases) |
| round 3 (scaled bases) | 24 | 3 add + 9 S-box + 12 linear |
| entry rescale into partial basis | 2 | 2 mult (GAMMA_0 sig_0, GAMMA_2 sig_2; lane 1 already scaled) |
| 23 partial rounds | 391 | 17 each: 1 add (sig_0 + kappa0hat_i), 3 S-box (t0h), 7 mult + 6 add (sig'_j = MH0_j t0h + sig_1 + MH2_j sig_2; lane-1 coefficient exactly 1 in rows 0 and 2) |
| rounds 60-62 (scaled bases) | 72 | 24 each: 3 add + 9 S-box + 12 linear; partial-phase exit constants folded into round 60 |
| round 63 (output lane only) | 16 | 3 add + 9 S-box + 2 mult + 2 add (row B63R with LAMBDA folded; lane-1 coefficient 1) |
| dp test + loop control | 3.75 | word primitives |
| **total per step** | **535.75** | |

The partial rounds run in the fixed scaled basis MB = (MDS[0][1], 1, MDS[2][1]) * M4[1], chosen so rows 0 and 2 have lane-1 coefficient exactly 1; all per-round constants are kappa-folded into the single addition per round (the kappa recursion kappa(i+1)_j = MH1_j kappa_1 + MH2_j kappa_2 + Khat_j is exact and offline). Bases chain M3 (after round 2), M4 (after round 3), MB (partial phase), M61..M63 (rounds 60-62). A companion-form (Krylov) detertour was evaluated and rejected numerically: +12 ops/round of basis conversion against -2/round saved.

The step program equals digest(message(x + rho0)) * LAMBDA on 64 of 64 random (x, rho0) trials against the organizer's trusted reference permutation (`--selftest`), and its per-step ledger totals exactly 535.75. Every field multiplication/addition and every word primitive in the actual code path is counted; no operation is uncharged.

## 4. The search: one trail, distinguished points, index table, recovery

A walk value is distinguished iff its low 128 bits are < 38176; the threshold is below 2^16, so the low 16 bits determine the low 128 bits among dp values and a stored key (high 126 bits, low 16 bits) is injective on dp values. Exactly D = (2^126 + 1) * 38176 of the p field elements are distinguished (p = 2^254 + c with c = p mod 2^128 >= 38176), theta = D/N in [10^-33.95009, 10^-33.95005] (conditioning bounds theta_lo = (D - 2^128)/N, theta_hi = D/(N - 2^128)).

The algorithm (Appendix B, `full_search`): draw the coins rho0 and x0 (two PRG draws); walk x_{i+1} = F(x_i) from x0 for at most S1 = n1 + d steps (82458658022075887745892673130667924 @ = detection window, Section 5). Each distinguished value is probed in the table (224 word operations per dp event: scan + insertion) and, if new, stored with its trail index: one 32-byte word holding the high 126 bits of the value and the index, plus a 16-bit side field holding the low 16 bits. A distinguished value can be reconstructed exactly from its word and side field (injectivity above). Distinguished values on the tail never repeat (a cycle value cannot equal a tail value); the first repeat of a stored dp value detects the cycle.

Recovery (deterministic, Appendix B): the repeat is x_b = x_a (a the stored index, b the current index, L = b - a). Let s be the index stored just before a (the start x0 at index 0 if none). Compute x_{s+L} from the nearest stored point at or before s + L (at most gmax evaluations, else abandon). If x_s = x_{s+L}, abandon (start on the cycle). Otherwise iterate both walkers from (x_s, x_{s+L}) in lockstep (at most gmax rounds); the first time their images agree, the two predecessor states (A, B) satisfy F(A) = F(B) with A on the tail and B on the cycle, hence A != B: an ordinary collision. The output is the two messages message(A + rho0), message(B + rho0) (three fifth roots each). Recovery uses at most gmax (positioning) + 2 gmax (lockstep) = 3 gmax evaluations when every gap between consecutive stored distinguished points is at most gmax; the gap event is a lemma term, and a capped walk abandons the pair.

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
per-step ops               = 535.75  (listing in Section 3)
walk ops    S1 * 535.75    = 95683576278833194370689586730019367454485.75
recovery    3*(gmax+16) evaluations at 535.75 + 6 each = 286142129245403461842214953876860171929.50
dp-table    20037 events * 224 word ops = 4488288
PRG          2 coin draws * 264 word ops = 528
setup + fifth roots        = 2000 + 2286
offline derivation         = 2^24 word ops (Section 9; charged, 23934 compressions)
total ops                  = 95969718408078597832531801683896248896733.25
units = total / C, C = 699 = 137295734489382829517212877945488195846.54256080114449213161659513590844062947067
time_log2 = log2(units)     = 126.690554
filed                       = 126.69056 (rounded up at 5 decimals)
```

For reference against the frontier: the incumbent ab786fc files 126.74586 at 1.3993*n0 with success 0.62 under its own convention; at the tight n0/0.39 convention the r=23 random function scores 126.61475. This entry's 126.69056 beats the incumbent by 0.0553 bits: the exact solve plus the detection-window/gap-cap recovery convention (their 3 gmax) costs 0.0758 bits over the tight random-function score, against their 0.4847 bits of probability margin.

## 8. Memory

Peak live set: 27,413 dp entries * 32 bytes (877,216) + 27,413 side fields * 2 bytes (54,826) + one 32-byte start word + 103,644 code + 5,600 constants + 7,200 registers = 1,048,518 bytes < 2^20 = 1,048,576. Every table item is one aligned 32-byte word: entry k at TAB0 + 32k holds (high 126 bits of the dp value) OR (its index < 2^128); the side word holds the 16-bit low part. Lookups extract the high part and compare, then the side field; reconstruction shifts the high part back and appends the side field (threshold < 2^16 makes this exact). Memory penalty max(0, log2(1,048,518) - 20) = 0; filed memory_log2_bytes = 20.

## 9. Preprocessing (inside time)

All constants (the line constants of Section 2; the scaled bases M3, M4, MB; GAMMA; MH0/MH1/MH2; the kappa-folded partial constants KAPPA0HAT and KAPPA_EXIT; the folded exit constants at round 60; C60..C63, B60..B62, B63R; LAMBDA) and the budget solve (80-digit Decimal bisections on n0 and n1) are offline. Their derivation is bounded by 2^24 word operations from stated caps (table derivation: 64 rounds of short reciprocal/fifth-power chains, each a few hundred word operations; budget solve: a few hundred 80-digit Decimal exp/log evaluations, each < 2^10 word operations), charged inside time_log2 in the ledger line "offline derivation" (2^24/699 = 23934 compressions), and declared as preprocessing_log2 = 15 (= ceil(log2(23934))). The measurement analysis of Section 6 is evidence generation for H1, not attack preprocessing; it is disclosed as such and not charged to the attack. The search program itself uses only integer literals (WALK, DETECT, GMAXC, DVAL, DPMASK, MCAP); nothing is derived online.

## 10. Organizer experiment (declared)

`lowbits-birthday` (python-message-pairs-v1, digest-xor-mask on the first 14 bits): per trial, at most 1200 fresh canonical 64-byte messages derived deterministically from the supplied seed; the program returns a pair whose r=23 digests agree on the masked bits. Local run of the same event: 256/256 verified pairs in 5.0 s single-CPU (mean ~144 draws per trial), byte-identical on repeat. It is a reduced-width witness on the digest only; it does not establish H1, the cost bound, or the success probability (a 14-bit event cannot separate hazard multipliers near 0.5 from 1).

## 11. Verification

The step program, the search with its recovery, the budget solve, the measurement harness and the analysis sources are embedded verbatim as appendices below (A: `myrho.py` - step program, line and tables, selftest; B: `attack.py` - the filed single-trail search, recovery, exact plan, reduced-width end-to-end selftest, H1 measurement mode; C: `measure2.py` + `analysis.py` - H1 evidence and exact likelihood intervals). All are standard-library-only Python 3, deterministic given their seeds. Exercised locally: `myrho.py --selftest` 64/64 against the trusted reference; `attack.py --selftest` 64/64 plus two-of-three reduced-width searches (one pair abandoned at the test gap cap); `attack.py --plan` prints the exact ledger of Section 7; Appendices C produced the Section 6 table (with `attack.py --measure` seeding widths 16..28).

## Appendix A: `myrho.py` (line, tables, step program, selftest)

Line construction, scaled/kappa tables and the counted `step()`; `--selftest` runs the 64-trial check against `ref_permute` (the organizer's verifier semantics) plus the per-step ledger reconciliation.

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
# rescale 2; partial rounds 17 each; round 63: 16; dp test + counter 3.75.
OPS = {'block02': 27, 'full': 24, 'pentry': 2, 'partial': 17, 'r63': 16, 'dp': 3.75}
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
            led.charge(224)         # probe + insert word work per event
            key = dp_key(x)
            if key in table:
                a = table[key]
                L = t - a
                s_idx = max((i for i in order if i < a), default=0)
                xs = x0 if s_idx == 0 else reconstruct(table, s_idx)
                q = s_idx + L
                r = max((i for i in order if i <= q), default=0)
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

    step_ops = Decimal('535.75')
    rec_evals = 3 * (gmax + 16)                # recovery cap: 3 gmax charged
    rec_ops = Decimal(rec_evals) * (step_ops + 6)
    dp_events = int((Decimal(S1) * theta_hi).to_integral_value(
        rounding='ROUND_CEILING'))
    table_ops = Decimal(dp_events) * 224       # probe + insert per event
    prg_ops = Decimal(2 * 264)                 # two coin draws
    setup = Decimal(2000)
    roots = Decimal(2286)                     # fifth roots for both messages
    prep = Decimal(1 << 24)                   # offline derivation allowance
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
        'per_step_ops': '535.75',
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
          f'per-step={led.mult + led.add + led.word:.2f} (budget 535.75)')
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
