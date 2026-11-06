# Proof — SHA-256 reduced to 40 steps on Dariia's characteristic (r39 structure)

## 1. Target and prices
Target profile: sha256-r40-prefix-v1. Primitive: SHA-256 compression reduced
to 40 steps, standard IV, standard padding and feed-forward, all 256 output
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
   (advice_DARIIA_HEAD30_1104.dec of the research record; the two blocks and CV* are embedded verbatim in experiments/dari40_exp.py; 0 violations). It plays the role
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
          = 16.37 + |log2 p_tail|

| Term | R40 | Status |
|---|---|---|
| claw: ops per claw surviving row 17 | 2^28.89 ops (46 of 677,878 distinct claws; 828 windows of 2^22) | MEASURED (logs/darijoint_head30_run.json) |
| tail carrier rows 18-23 | -123.915 / -123.933 / -124.051 (3 seeds) | MEASURED (logs/wtdeep_dari_s5..7.txt) |
| tail rows 24-39 + collision | premise H2b: one bit per counted A/E condition on rows 24-39: 77 (71 late-block char); Dariia's own late block: 97 | COUNT, declared |
| GPU stage 2 (executed alongside) | seed-8 carrier (-123.555), 0 hits at 2^30 / 2^34 draws (printed bounds < -159.50 / < -163.50); not continued | MEASURED bound |
| success term | -1.02 (success 0.39) | RULE + MATH |
| time_log2 (R40, late 71) | 16.37 + 124.0 + 77 = 217.37 | measured claw + measured rows 18-23 + counted rows 24-39 |
| time_log2 (R40, Dariia's late block) | 16.37 + 124.0 + 97 = 236.4 | same |

Count method beside measurement (same split, presented as computed): pub39
rows 18-23 count 39 vs measured 59.9; pub39 rows 24-38 count 1 (+4 W) vs
measured 14.8; Dariia rows 18-23 count 117 vs measured 124.0 (COUNT). W-row
conditions on rows 24-39 (64) are listed separately: the collision test does
not require the W rows to follow their signs.
Count-based figures (COUNT, presented as computed): late block 71 conditions
-> 2^105.8 (1 h head) / 2^70 (head floor); calibration of the count method on
pub39: count 40 vs accepted SMC tail 74.3.
Memory: the walk's table (r39 class, 2^20 bytes) plus one advice pair (160 bytes), the program code (under 2^16 bytes), the two current messages and the walk's working state (under 2^14 bytes): total under 2^20.16 bytes, declared memory_log2_bytes 20.16; the advice is
- Peak memory inventory (bytes, all held simultaneously at the peak of one walk step): walk table 1,048,576 (the r39 class) + program source 60,361 + advice pair 160 + the two current two-block messages 256 + walk working state (r39joint registers, window buffers, counters) under 16,384 + the organizer request (at most 256 trials) 40,960 and the current trial result 4,096 (streamed, none retained) = under 1,170,793 bytes = 2^20.1591 (rounded up), declared memory_log2_bytes 20.16 (rounded up); score term max(0, 20.16 - 20) = 0.16.
a 160-byte class, so nonuniform_advice_log2_bytes = log2(160) = 7.322.
Preprocessing: the construction of the advice pair is charged: the HEAD30 head solve, one CaDiCaL run of about 7,200 CPU-seconds, charged by the method of the accepted entry 6eeefb64 (solver CPU-seconds at 2^21.43 units per CPU-second): 7,200 x 2^21.43 = 2^34.25 target compressions, DECLARED preprocessing_log2 34.25 (the solve is not re-run by the organizer; MEASURED wall times of Dariia's head solves: min 3,600 s, median 6,000 s, max 8,400 s).

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
Scope: rows 24-39 collision term. Evidence: counted conditions; GPU stage 2
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
| transplant + one claw window at 2^8 per organizer trial | EXECUTED by the organizer (experiment v40d-advice-01, experiments/dari40_exp.py + r39joint.py) | advice_row 31 on 256/256; transplant first violated row 8/9/16 (133/110/13); window_skipped 200/256; claws through row 17 at 2^8: 0 (expected ~0.05); block2_collision 0 |
| organizer program loop bounds | STATED | Every loop of the organizer program is bounded by its constants: one window of 2^8 walk steps per trial (KTRY = 1), r39joint's kernel caps (a CV over the caps is reported as window_skipped and the trial ends), and the walk table's bucket chains, bounded by the table size (the 2^20-byte class); the 256-trial request completes in under 3 s. |
| rows 24-39 | ASSUMED (H2b, counted) | GPU stage 2 executed to 2^34 draws: 0 hits (bound only) |
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
Totals (section 3): time_log2 (R40, late 71) = 16.37 + 124.0 + 77 = 217.37;
time_log2 (R40, Dariia's late block) = 16.37 + 124.0 + 97 = 236.4.
