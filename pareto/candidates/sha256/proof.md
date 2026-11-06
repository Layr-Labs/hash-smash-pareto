# Proof — SHA-256 reduced to 41 steps on Dariia's characteristic (r39 structure)

## 1. Target and prices
Target profile: sha256-r41-prefix-v1. Primitive: SHA-256 compression reduced
to 41 steps, standard IV, standard padding and feed-forward, all 256 output
bits equal. Collision type: ordinary two-block collision, M0||M1 and M0||M1'
with the same random first block M0 (no chaining-value difference), identical
to the accepted r39 entry.
Message difference: r39's support W8..W12 (Dariia's 40-step characteristic);
expanded schedule differences at 16, 17, 24, 26, 31, 33, 35, 37, 38, 39.
Price: C = 2,896 ops per compression (DECLARED); costs reported in target
compressions.

## 2. Construction (r39 structure, step by step)
1. Advice. Dariia's head pair: a chaining value CV* and blocks (M1, M1')
   following her signed characteristic through row 30
   (advice_DARIIA_HEAD30_1104.dec of the research record; the two blocks and CV* are embedded verbatim in experiments/dari41_exp.py; 0 violations). It plays the role
   of r39's 160-byte advice pair.
2. Transplant. For a random first block M0 with chaining value CV, the advice
   is carried onto CV by the exact bijection of the r39 transplant
   (sraiw 38912d66). The dense head rows are inherited, not re-solved.
3. Claw. A distinguished-point walk over windows finds claws that make the
   transplant line up (tools/darijoint.py, general path of r39joint.py);
   survivors are checked against every bit condition of the characteristic,
   row by row.
4. Tail, rows 18..R-1. Paid probabilistically, measured with the r39 tail
   replica (tools/wintail.py): SMC over E18..E23 with exact look-ahead (the
   "carrier"), then W8/W9 redrawn in their classes, rows 24..R-1 rebuilt,
   hit = equal state after step R-1, every hit replayed in scalar code.
   Stage 2 on GPU: tools/wt2gpu.cu (same draws as Python; hits replayed by
   tools/wt2verify.py).

## 3. Cost ledger (target compressions)
Formula:
time_log2 = log2(ops per row-17 claw survivor / C) + log2(1 / p_tail(18..R-1))
          + log2(ln(1/0.61))
          = (28.89 - 11.50) + |log2 p_tail| - 1.02
          = 15.37 + |log2 p_tail|

| Term | R41 | Status |
|---|---|---|
| claw: ops per claw surviving row 17 | 2^28.89 ops (46 of 677,878 distinct claws; 828 windows of 2^22) | MEASURED (logs/darijoint_head30_run.json) |
| tail carrier rows 18-23 | -123.915 / -123.933 / -124.051 (3 seeds) | MEASURED (logs/wtdeep_dari_s5..7.txt) |
| tail rows 24-40 + collision | premise H2b: one bit per counted A/E condition on rows 24-40: 147 (137 late-block char, nldtool characteristic_R41_late137.xml) | COUNT, declared |
| GPU stage 2 (executed alongside) | seed-8 carrier (-123.555), 0 hits at 2^30 / 2^34 draws (printed bounds < -159.50 / < -163.50); not continued | MEASURED bound |
| success term | -1.02 (success 0.39) | RULE + MATH |
| time_log2 (R41, late 137) | 15.37 + 124.0 + 147 = 286.4 | measured claw + measured rows 18-23 + counted rows 24-40 |

Count method beside measurement (same split, presented as computed): pub39
rows 18-23 count 39 vs measured 59.9; pub39 rows 24-38 count 1 (+4 W) vs
measured 14.8; Dariia rows 18-23 count 117 vs measured 124.0 (COUNT). W-row
conditions on rows 24-40 (64) are listed separately: the collision test does
not require the W rows to follow their signs.
Count-based figures (COUNT, presented as computed): late block 137 conditions
-> 2^171.8 (1 h head) / 2^136 (head floor); calibration of the count method on
pub39: count 40 vs accepted SMC tail 74.3.
Memory: the walk's table (r39 class, 2^20) plus one advice pair; the advice is
a 160-byte class, so nonuniform_advice_log2_bytes = log2(160) = 7.322.
Preprocessing: none beyond the advice, which is given (DECLARED 0).

## 4. Premises
H1-claw. Statement: claws behave independently (untested); window CVs random
as in r39; per-claw charge equals the r39 final-verify (an upper bound).
Scope: the claw term of block 1. Evidence: darijoint run; r39-tool control.
H2-tail. Statement: the tail on transplanted states equals the tail measured
on the advice window (the r39 premise of the same name). Scope: rows 18-23
carrier transfer. Evidence: pub39 tail control; 3-seed recomputation.
H3-advice. Statement: the advice pair is given (r39 likewise ships its
advice). Scope: preprocessing accounting. Evidence: advice pair inspected,
0 violations.
H2b-rows-24+. Statement: rows 24..R-1 hold with probability 2^-(counted A/E
conditions) given the carrier (R40: 77; R41: 147; R42: 201). Declared.
Scope: rows 24-40 collision term. Evidence: counted conditions; GPU stage 2
bound.

## 5. Validity evidence table
| Item | Status | Evidence |
|---|---|---|
| claw walk on the advice pair | EXECUTED | darijoint run: 677,878 distinct claws, survival by row |
| claw tool = accepted r39 tool | EXECUTED control | r39 pair through the general path: distinct 828/793, dp 32510/32570 = r39joint exact |
| tail sampler = accepted method | EXECUTED control | pub39: Python -74.25 / -74.51 (deep cap), GPU stage 2 -74.690 (2^26) / -74.681 (2^30), 1024/1024 replayed; board -74.32 |
| tail carrier rows 18-23 | RECOMPUTED (3 seeds) | -123.92 / -123.93 / -124.05 |
| window built from the advice | EXECUTED control | mkwin.py on HEAD30 reproduces the window values 120/120 |
| advice pair through row 30 | INSPECTED | 0 violations |
| rows 24-40 | ASSUMED (H2b, counted) | GPU stage 2 executed to 2^34 draws: 0 hits (bound only) |
| H1-claw independence, H2-tail transfer | ASSUMED | declared in section 4 |

## 6. Measurement logs (quoted from the draft sections 3 and 5)
Claw (section 3): 2^28.89 ops per row-17 survivor; 46 of 677,878 distinct
claws; 828 windows of 2^22 (logs/darijoint_head30_run.json).
Tail carrier rows 18-23 (sections 3, 5): -123.915 / -123.933 / -124.051 across
3 seeds (logs/wtdeep_dari_s5..7.txt); recomputed -123.92 / -123.93 / -124.05.
GPU stage 2 (section 3): seed-8 carrier -123.555; 0 hits at 2^30 and 2^34
draws; printed bounds < -159.50 / < -163.50.
Tail control (section 5): pub39 Python -74.25 / -74.51 (deep cap); GPU stage 2
-74.690 (2^26) / -74.681 (2^30); 1024/1024 replayed; board -74.32.
Claw control (section 5): distinct 828/793, dp 32510/32570 = r39joint exact.
Window control (section 5): mkwin.py on HEAD30 reproduces window values
120/120.
Count calibration (section 3): pub39 count 40 vs accepted SMC tail 74.3;
pub39 rows 18-23 count 39 vs measured 59.9; pub39 rows 24-38 count 1 (+4 W)
vs measured 14.8; Dariia rows 18-23 count 117 vs measured 124.0.
Totals (section 3): time_log2 (R41, late 137) = 15.37 + 124.0 + 147 = 286.4.
