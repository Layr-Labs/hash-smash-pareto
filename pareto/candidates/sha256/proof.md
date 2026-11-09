# SHA-256 reduced to 39 steps: ordinary collision by the transplanted Table 23 pair with two released state words (k = 4), a row-16 claw search and a bit-sliced re-try of W17

The bit-sliced pass is dariolina's W17-only pass (087bf8f8, credited; co-author), used unchanged on the w3 list.

Prepared 2026-11-08. A credited derivative of newjordan's 3e96c2b6 (Pareto 101.2483), which is a credited derivative of our f14850cb; its pass (transforms A+B+C) is kept unchanged. This entry changes how the per-window list flush is built and charged (Section 3, Flush) and adds one output-identical pass rewrite, class-literal folding (Section 3, k4 pass). Numbers inherited from our r39 entry 5f8e6192 are cited as RAT l.N (R39_ACCEPTED_TERMS.txt). New numbers cite the experiment or tool that produced them. This entry supersedes the k = 3 entry (one released word) by the same author; sections not restated here are as in that proof.

## 1. Target and output
- **Target.** SHA-256 compression reduced to 39 steps, standard IV.
- **Output.** Two 128-byte messages M0 || M1 and M0 || M1': the same random first block M0, then second blocks M1 and M1' = M1 + DL, with differences on words 8..12.
- **Padding.** SHA-256 appends a third block, identical for both messages because their lengths are equal. Equal chaining values after block 2, passed through the same padding block, give equal digests. So a collision of the second 39-step compression is a collision of the 39-step hash.
- **Class.** Ordinary collision: no chaining-value difference (HashSmash.md l.164). Same class, advice and walk as r39 (RAT l.2-3).

## 2. The construction
**2.1 Advice.** The 39-step semi-free-start pair of ePrint 2026/1120 Table 23 (CV_PUB, MP_PUB = BW, M_PUB), 160 bytes, as r39. Credit: sraiw 38912d66, dariolina. **Charged advice: 2,225 bytes = 2^11.11959:** this pair plus the 1,341-byte recipe literal and the 724 bytes of per-class literals (Section 6), which are target-specific precomputed data.

**2.2 The transplant, k = 4.** Fix A[8..11], E[12..15] and W12..W15 to the published values of MP_PUB. For any chaining value cv and any (a0, a1, a2, a3) = A[4..7]:
- Steps 0-7 determine W0..W7 from the A registers and give E[4..11].
- Steps 8-11 determine W8..W11 from the fixed E[12..15] (`k4_words`).
- At (a2, a3) = (BA[6], BA[7]) this is r39's `build` exactly, checked on 200 random (cv, a0, a1) by `--k4selftest`.
- **Consistency.** A[8..11] equal t1(r) + t2(r) for r = 4..7 with E[8..11] derived. The published state block from step 8 on is therefore preserved for every (cv, a0, a1, a2, a3). So the states after step 11 are the published ones for message 1.
- **Second block.** M1' = M1 + DL word-wise modular, with DL = M_PUB - BW (`k4_second`). The derived W10 and W11 carry the published modular differences D10 and D11.
- **Closed forms (proved by expanding the step equations; checked 0/500 numerically):**
  - W9 = C - a1 + h4(a2, a3), with h4(a2, a3) = MAJ(A8, a3, a2) - CH(E12, E11, E10);
  - E10 = a2 + A10 - S0(A9) - MAJ(A9, A8, a3);
  - E11 = a3 + A11 - S0(A10) - MAJ(A10, A9, A8);
  - W10 = E14 - A10 - E10 - S1(E13) - CH(E13, E12, E11) - K10 (depends on a2, a3);
  - W11 = E15 - A11 - E11 - S1(E14) - CH(E14, E13, E12) - K11 (depends on a3 only).

**2.3 Row 16 is a claw (unchanged from r39).**
- W16 = s1(W14) + W9 + s0(W1) + W0. W0 and W1 do not depend on (a2, a3).
- Every listed (a3, a2) has h4(a2, a3) = h4(BA[6], BA[7]), so W9 and W16 are the same as at the base. W16 = g holds exactly when r39's claw condition F(a0) = F(u) does.

**2.4 What remains to pay after a claw.**
- **Once per claw:** W9 in F9.
- **Per listed (a3, a2):**
  - W8 in F8, which depends on (a0, a1, a2, a3);
  - W10 in F10 and W11 in F11, both guaranteed by the list (they depend on (a2, a3) only);
  - W17 = 0x71e9ba98, where W17 = s1(W15) + W10 + s0(W2) + W1 and W2 = a2 + c2(a0, a1). W17 values coincide within a claw when two entries share a2 and W10. W10 depends only on (a2, a3), so these coincidences are the same in every claw (k4clus.py):
    - Of the 361,638 entries, 65,142 distinct (a2, W10) keys, 28% singletons, list clusters of size at most 5.
    - A coinciding mate counts only if it also passes F8 in that claw. Per F9 claw (k4copass.py, 3,000 claws), 8,072 entries pass F8 (the enumerator gives 8,082) and 7,621 distinct keys pass. The size-biased mean passing cluster is 1.115, at most 4.
    - Each variant is a distinct message, so hits are counted per variant (all-hits loop) and each hit's tail is a separate trial (Section 7).
    - The 8 observed hits came from 8 distinct claws, and no list mate of theirs passed F8.
- **The tail:** rows 18-38, Section 8.
- **dW18 = 0.** W18 = s1(W16) + W11 + s0(W3) + W2. Its difference is s1(g + dW16) - s1(g) + D11, with dW16 = D9 fixed because W16 = g on both messages. That is the published value for every claw, so dW18 is quiet as in the published pair.
- **Implication.** All of the above plus the tail give a collision. The program confirms each candidate by compressing both blocks.

**2.5 The list.**
- **a3 classes.** a3 = BA[7] XOR masks of weight <= 2 (528 values): 57 pass F11, and 27 have solutions of h4 = h0. Random F11-passing a3 had none (12/12 sampled).
- **Solutions.** For each class, all a2 with h4 = h0 come from an exact bit-serial search. 179,844 also pass F10. Of those, 165,662 keep the published state-difference trail through step 15 at 3 points, with 0 mixed verdicts (structural).
- **The filter depends on (a3, a2) only.** Indexing as in `k4_words`: A[0..3] and E[0..3] are the CV, and step r (r = 0..15) writes A[r+4] and E[r+4]. Its inputs are MAJ(A[r+3], A[r+2], A[r+1]), CH(E[r+3], E[r+2], E[r+1]), h = E[r] and W_r.
  - **Message 1 values.** A[8..11], E[12..15] and W12..W15 are the published values, so every state from A[8] and E[12] on is published for message 1 (2.2).
  - **Where the difference enters.** The modular word difference DL is fixed. The first nonzero word difference is at step 8, so the first state difference is in A[12], E[12].
  - **What meets a difference, step by step:**
    - MAJ at steps 9-11 takes A[10..14], all published.
    - CH at step 9 is CH(E[12], E[11], E[10]): E[12] differs and E[11], E[10] vary with the construction. E[10] = a2 + A10 - S0(A9) - MAJ(A9, A8, a3) and E[11] = a3 + A11 - S0(A10) - MAJ(A10, A9, A8).
    - CH at step 10 is CH(E[13], E[12], E[11]): E[11] varies.
    - CH at steps 11-15 takes E[12..18], published for message 1.
  - **Inputs that vary but meet no difference.** The h inputs E[8] and E[9] at steps 8 and 9, and W8, W9 on message 1, vary but carry no difference. They are added equally to both messages, so the modular differences of T1, and with them every state difference, depend on the varying values only through CH at steps 9-10 (E[10], E[11]) and the derived word differences D10, D11 (F10, F11, guaranteed by the list).
  - **A6 and A7 never meet a difference.** a2 = A[6] and a3 = A[7] enter MAJ only up to step 6, before any difference exists.
  - **Conclusion.** The trail through step 15 is a function of (a2, a3) only. The verdict holds for every (cv, a0, a1) iff it holds at one point. Any condition the characteristic places on rows 7-11 is paid inside this filter. (An earlier review called the varying CH input "E7"; that is the same variable in shifted indexing.)
  - **Structural check** (k4trail6.py): all 361,638 entries at 6 points (the published point and 5 random CVs with random (a0, a1)), trail through step 15, 0 failures (41 s).
- **Shipped set.** The Pareto-optimal subset: the 13 largest classes, 361,638 variants (Section 5 model).
- **Encoding.** Stored as a 1,341-byte zlib recipe (the 60 classes and one reject bit per candidate, in decoder order), 1,677 base85 characters.
- **Decoding.** At import the list is decoded once in 64-byte steps to verify its running sha256 and to derive the per-class and per-block literal constants; no list object is kept. In the attack, each window flush stream-decodes it again into one chunk of planes at a time (Section 3, STREAMED list; Section 6).
- **Checks.** `--k4selftest` re-verifies every entry: h4, F10, F11, W9, W16, and the trail through step 15.
- **Preprocessing.** About 2^24 operations offline (k4near.py, k4list.py), plus the decode at import.

## 3. The program
- **File.** `r39joint_k4.py` (51,934 B; with r39tail.py (unchanged), 65,240 B of 65,536; sha256 2690f064...; block indentation at one space per level, AST-identical to the source it was built from; k4_selftest is in tools/k4selftest.py; dedupe gate k4d; pass transforms A+B+C; STREAMED list). The participant-only `--windows` mode moved to tools/windows_mode.txt. is r39joint.py with asserted patches: tools/mk_r39k4.py, then tools/apply_k4fix.py (judge-review fixes: pass-off control, attack-path cap fence, gc assert, lambda margin).
- **Dedupe gate (`k4d`).** Before the pass, each F9 claw (a0, u) is looked up in a per-window table: 2,048 entries x 8 B = 16,384 B, counted in Section 6, at 12 ops per lookup inside the 'k4' tick.
  - A claw already evaluated in this window is skipped; it would repeat the same messages. If the table is full, the claw is evaluated without being stored, so the gate never fails.
  - **Measured:** 15.5% of passes were on duplicates.
  - **Controls:** a planted duplicate is evaluated once; a full table falls back to evaluating.
- **List.** This entry uses the w3 60-class k = 4 list: 361,638 entries in 1,447 blocks, decoded in the program from a 1,341-byte recipe and checked against W3_SHA at import. Every decoder operation is charged in Mach, and the decoder keeps no list longer than 560 values. Pass charge per evaluated F9 claw: 797,352, an exact count that is identical on every organizer seed and replays deterministically. The organizer experiment r39k4-window-small evaluates the pass over the first 181 of the 1,447 blocks (A.k4_maxblk; the attack path asserts it is unset) and hard-asserts those counts: (221,5,0,90504,5208,0,17462224,27953841), (215,3,0,90504,5163,0,8955189,19416753), (226,4,1,90504,9744,0,8955189,24433145), (205,2,0,90504,3866,0,8955189,20009937).
- **Work cap (`k4_budget`).** The cap is B windows x K4_OPS_PER_CLAW x 58,959.42 claws per window. K4_OPS_PER_CLAW = **21,680** = ceil(7,863.36 + 12,919.49 + 897.05) (asserted at import from the program's own counters):
  - **Base walk, this program:** mu+ = the 99% upper bound over 24 full windows (mean 461,649,658, s.d. 3,858,918, t(23) = 2.500) = 463,618,904 ops per window = 7,863.36 per claw. It includes the lookup charges. Precedent: 9993eaa8 priced its own program's mean work. The measurement used the public seeds 1000-1023 with the same window generator as the attack (a finite public-seed sample; its scope is stated in H6).
  - **k4 pass:** 797,352 per evaluated F9 claw (per-claw prelude + buffer + pass), read back from the asserted tuples: k4_ops = flush + 2 x 797,352 + 2 x 12. Output-identical rewrites on top of transforms A+B+C: planes that are constant within a class or within a 256-entry block are folded into literals derived at import from the shipped list, and the four claw-only broadcasts are rebuilt for each (claw, chunk) pass and charged there (no stored per-flush broadcast cache); the claw buffer keeps (a0, u) only, and a1 and w2b are recomputed and charged at the flush. Participant equivalence check against the unfolded program: 32 random seeds with up to 8 evaluated F9 claws per window (13,686,190 lanes), identical claws, F9, F8F9, lanes, F8 lanes and W17 hits, check mode asserting every 32nd lane against k4_words in both. Fields 0-5 of every K4_WIN_EXP tuple (claws, F9, F8F9, lanes, F8 lanes, W17 hits) are unchanged, and check mode asserts every 32nd lane against k4_words as before. (Trials 1-3 have one flush each.) Pre-fold control: before this rewrite the same read-back gave 644,403 (filed 5ea5554f). In v3, with resident planes and transforms A+B, it was 806,200; A and B alone give 816,217 in the streamed build. It was 869,295 before any output-identical transforms (Section 3.2). That figure is multiplied by the distinct F9 claws per distinct claw at its 99% upper bound over 48 full windows (mean 0.015997, s.d. 0.000594, t(47) = 2.408) = 0.016203, which gives 12,919.49.
  - **Flush (once per window):** F = 52,889,692 ops = 897.05 per claw, read from the program (F = K4_PLANE_OPS + K4_INFB x K4_RAW). (i) The plane build is now executed and charged op by op inside Mach: each entry is OR-ed into its word (12 ops), then a lane-parallel 5-stage 32 x 32 delta-swap transpose on the 256-bit words (80 pairs x 22 ops + 15 per 256-entry block), giving exactly the planes of the previous build; K4_PLANE_OPS = 51,091,677. (ii) The inflate and varint decode is charged at 37 ops per raw byte x 48,595 B = 1,798,015, from a counted puff-style decoder (36.351 ops per raw byte, byte-identical output) instead of the declared 64. (iii) The list's sha256 runs only at import (verification), not in the per-window flush. Extra flushes: X = max(ceil(N / 1,023) - 1, 0) for the N distinct F9 claws of a window, each extra flush executed and charged in Mach. MODEL (declared): N is tail-dominated by Poisson(950), so E[X] = sum over j >= 1 of P(N > 1,023 j) <= 0.009134 and E[X^2] <= 0.009134. Sources: 48 full windows of the predecessor (mean 944.60, s.d. 35.37) and 216 later participant-run windows (mean 936.48, s.d. 29.95, maximum 1,022). The expected extra work is at most 66,883 ops per window, counted in H6.
  - **List setup:** included in the flush above (the counted plane build).
  - **So the cap is 2^99.758569 compressions;** the claimed time 99.7586 is its ceiling. The stage-2 walk loops are unchanged from the base entry (identical source), so their bounds are as stated there. Every rate is at its own upper bound, so expected work is at most the cap.
  - **Each premise sits at its own 99% bound,** not 99% jointly. By the union bound the joint coverage of the four bounds (E[N], key ratio, F9 rate, base walk) is at least about 96%.
- **Hook.** After each claw that passes F9, `k4_eval` runs the bit-sliced pass, one class at a time and 256 lanes per block.
- **Literals.** Per class, a3-only constants are build-time literals: S0(a3), E11, MAJ(A9, A8, a3), CW8, C17.
- **Broadcasts.** Per claw: a0 + A8, a1, W2 - a2 and W1. Per claw and class: a3|a1, a3&a1 and a0 + A8 - S0(a3), at 3 operations per bit.
- **Hits.** Every lane passing F8 and W17 builds the pair and compresses both blocks, charged 2 x 2812 + 400 + 96 + 16.
- **Check mode.** Every 32nd lane is asserted against `k4_words`.
- **3.1 Loops.** As in the k = 3 proof (r39's stage-2 loops are unchanged).
  - The class decoder's loop is bounded by the input length, with each step at most 64 output bytes.
  - The lane loop runs at most 256 passes per block.
- **3.2 Deviations from the accepted r39joint.py:**
  - `_t4` and T4_EXP removed;
  - GEN_C and `--gen-c` removed (participant-only; r39_gen.c ships in tools/);
  - **STREAMED list (judge items 101/102/106).** The list's bit planes are no longer resident:
    - each F9 claw that passes the dedupe gate is appended to a per-window buffer (a0, a1, u, w2b), with K4B = 1,023;
    - at a full buffer or at window end (run_window calls k4f), the compressed literal is stream-decoded once, grouping each class into chunks of at most 32 blocks, and every buffered claw runs the unchanged pass on each chunk;
    - the dedupe table persists for the whole window, so no claw is evaluated twice across flushes;
    - **output-identical to v3:** claws, F9, F8, lanes, F8 lanes and W17 hits are unchanged on all 4 organizer seeds. Trial 0 runs with K4B = 1 (two flushes), and its asserted fields 0-5 equal the K4B = 1,023 values, so batch-size equality is organizer-checked;
  - the W17-stage 'ind' observation is dropped (bytes). It only bounded W17 multiplicity, which is priced through the distinct-key bound (judge item 106); tail_F stays as the organizer-run H5 evidence;
  - **pass transforms A, B and C** (API L1108_k4pass_answer):
    - A: Sa reuses s0p(W8), since W8D differs only in bits 30 and 31, so only s0 output bits 12, 13, 23, 24, 27, 28 are recomputed;
    - B: W17 = (s0p + (W1 + C17K)) - E10.
    - C: E8 is eliminated and folded into the W8 path, since W8 = (CW8 - a0p) - E8 - CH and CW8 - a0p is a per-claw literal; the a0p' and a1' hoists absorb the a3 broadcasts, and Dc' = W1 + C17K - W17PUB. W17 is tested without building it: the pass accumulates the 32-lane equality A17 = E10, and check mode reconstructs W17 = A17 + W17PUB - E10 for its lane assertions.
    - Output-identical: tuple fields 0-5, ind_* and tail_* are unchanged on all 4 organizer seeds, and check mode asserts W17 and F8 on every 32nd lane;
  - the r39-window-small harness (`_e2` and its serve() statistics) removed, since the manifest does not run it (16-entry limit);
  - the k4 hooks (Attack(k4=...), `--k4`, `--k4selftest`, `--attack --k4`).
  - With k4 off, r39-transplant-claw passes its asserts.

## 4. Machine model
As r39: a counted word RAM of 256-bit words, one operation per primitive, a load or store at 3, a branch at 2, and 2812 operations per compression. Every operation goes through `Mach`.

## 5. The ledger
| term | value | source |
|---|---|---|
| base walk ops per distinct claw | 7,863.36 (mu+, 24 full windows of THIS program, 99% UB) | Section 3; r39's accepted 8,331 is not used |
| k4 pass per evaluated F9 claw | 797,352 (transforms A+B+C, class and block literal folding, broadcasts rebuilt per (claw, chunk); streamed) | count in the program (`m.cat['k4']`, flush subtracted) |
| evaluated F9 claws per distinct claw | 0.016203 (distinct only, dedupe; 99% UB over 48 full windows; raw rate 0.019078) | k4dup.py |
| list flush per window | 52,889,692 / 58,959.42 = 897.05 per claw (counted plane build 51,091,677 + decode at 37 ops per raw byte) | charged in `k4f` |
| ops per claw | 21,680 = 6.1611 compressions, term 2.6232 | K4_OPS_PER_CLAW |
| W17 tries per distinct claw, E[N] | 403.4328, the one-sided 99% bound over 16 FULL first-block CVs (mean 403.4904, s.d. 0.0885, t(15) = 2.602), pre-registration 7. Earlier: 127.7125 from 4 single chunks | k4pair_gpu (exact match with k4pair: same claws, F9, N on chunk 2 CV1, and same hits on chunk 1 CV3): every claw of cvs.txt CVs 1-16, about 1.718e10 claws |
| W17 | 32 | |
| tail | 74.3238 (RAT l.4) | Section 8 |
| successes needed | -1.0166 (P = 0.39) | |
| **time, unconditional on within-claw tail independence (the program's K4_EN_LB = 360.880)** | **99.7586** | -log2(403.4328 x 0.894521) + 32 + 74.3238 + 2.6232 - 1.0166, ceiled to the program cap 2^99.758569. Trials are counted as distinct passing (a2, W10) keys. 0.894521 is the one-sided 99% lower bound of distinct/entries over 16 batches of 1,000 F9 claws (16 batches of 1,000 F9 claws, s.d. 0.0016, t(15) = 2.602; k4ratio.out) |
| **Pareto score, unconditional** | **99.8898** | memory 2^20.1312 (Section 6). History: 102.1023 (293ca62c), 101.9356 (02a8f734), 101.4490 (f14850cb), 101.1009 (3a474464), 101.0983 (9cf5ae57, on the board), 101.2483 (3e96c2b6, newjordan) |

**Class subset.**
- With all 28 classes the measured E[N] is 184.07 (chunk 0, 4 CVs). That gives time 101.32, memory 2^20.72 and Pareto 102.04.
- The 13-class subset is optimal under the Pareto objective: each 256-variant block costs 1,024 B of memory and the same ops.
- Under time-only scoring, all 28 classes would be preferred.

## 6. Memory (peak; every representation of the list is counted)
| item | bytes | kind |
|---|---|---|
| r39 accepted base (RAT l.8) | 1,047,428 | resident |
| one chunk of planes (at most 32 blocks x 1 KB), streamed | 32,768 | transient (per flush) |
| decoder tables, 4 x 256 x 4 B | 4,096 | transient (per flush) |
| decoder work lists, at most 448 + 560 values x 4 B | 4,032 | transient (per flush) |
| per-block literals, 1,447 x 2 x 4 B | 11,576 | resident |
| claw buffer, 1,023 x (a0, u) 8 B | 8,184 | resident (per window) |
| per-(claw, chunk) broadcast lists, 8 x 32 words | 8,192 | transient |
| decoder's current block | 1,024 | transient |
| hit-output records and varint parser state | 128 | transient |
| recipe literal (zlib) | 1,341 | resident |
| per-class literals (60 classes) and K4_N | 724 | resident |
| decode transient: input bytes 1,341; inflate window 4,096; zlib inflate state and z_stream 7,500; one output step 64; sha256 state about 128; scalars about 64 | 13,193 | transient (only during `_k4build`) |
| dedupe table: 2,048 x (a0, u) x 8 B | 16,384 | resident (per window) |
| dedupe occupancy bitmap, 2,048 bits | 256 | resident (per window) |
| **peak** | **1,148,391 = 2^20.1312** | |

**Memory layout.** The r39 base rows are as accepted (RAT l.8, 1,047,428 B) and are not re-described here. The rows this entry adds are flat arrays with no per-entry overhead. Dedupe table: 2,048 slots of 8 B holding (a0, u), probed linearly, with a separate occupancy bitmap of 2,048 bits (256 B, its own row); there is no other index. Claw buffer: an array of 1,023 x 8 B (a0, u) in claw order plus a count register. Per-block literals: an array of 1,447 x 2 32-bit words. Per-class literals: 60 x 3 32-bit words plus K4_N. Recipe literal: 1,341 bytes read once, front to back, by the inflate decoder, whose window and state are the decode-transient row. Decoder tables: four arrays of 256 32-bit words. Decoder work lists: at most 448 + 560 32-bit values. Plane chunk: at most 32 blocks x 1 KB. Broadcasts: 8 x 32 words for one (claw, chunk) pass. Transient rows are live only during a flush; the peak adds every resident row and every flush-transient row, as in the table.

## 7. Success probability and time
- lambda = B x groups per window x E[N] x 2^-32 x p_tail. The program sets lambda = -ln(1 - 0.39) + 2^-40 (`k4_budget`).
- Windows needed: B = 2^80.9644, matching the program's `k4_budget` at K4_EN_LB = 360.880. The work budget is 2^99.758569 compressions, from K4_OPS_PER_CLAW = 21,680 (Section 3). The 2^-40 margin moves the time by about 2^-39 bit, below every printed digit.
- **The cap does not bind before B windows (H6-cap-completion, MODEL with measured inputs).** Work per window = base walk + D x pass + flush + X x flush, with D the distinct evaluated F9 claws of the window. Means: base walk 461,649,658 (24 full windows, Appendix C), D 944.60 (48 full windows), pass 797,352, flush 52,889,692, E[X] <= 0.009134: mean work per window <= 1,268,204,466 = 21,509.79 per claw against the cap 21,680, a margin of 0.791%. Per window, s.d. <= 3,858,918 + 35.37 x 797,352 + sqrt(0.009134) x 52,889,692 = 37,114,290 (Cauchy-Schwarz, no independence assumed between the parts). If windows are independent with these moments, the total over B = 2^80.9644 windows has relative s.d. 1.91e-14, the margin is 4.15e+11 s.d., and Chebyshev bounds P(cap before B) below 5.9e-24. The moments are finite participant-run sample estimates; the bound is conditional on them.
- **Why the margin.** Hits arrive in clusters: entries in one claw that share (a2, W10) and pass F8 (2.4). Write H for the hit count. Then P(success) = 1 - E[(1 - p_tail)^H]. For clustered H this is at most 1 - exp(-lambda) (compound-Poisson, Jensen). The shortfall is about exp(-lambda) x lambda x p_tail x (m - 1)/2, where m = 1.115 is the size-biased mean passing cluster: 2^-80.2. The 2^-40 margin adds 0.61 x 2^-40 to P, so P >= 0.39 holds strictly.
- **Var(H).** Var(H) = sum over claws of Var(H_c) <= m_max x E[H], with m_max = 4 passing entries per key (measured). Two keys in one claw both hitting has probability about 2^-64 per claw pair of keys.
- **Tail independence within a cluster: MEASURED, and NOT supported at step 19.** Measured with k4tailicc.py over 10 real claws and 50,812 F8-passing lanes.
  - **Method:** the tail starts, hit-conditioned, at the published step-17 states. hd_r is the Hamming distance (uncounted diagnostic) of the lane's (dA, dE) from the published trail at step r.
  - **Within a key:** pairs of cluster mates (same a2, W10; 2,964 pairs) have hd correlation 0.227 at step 19. That is about 12 standard errors from 0. It falls to 0.014 at step 20 and about 0 at steps 21-22.
  - **Cause:** mates share a2, and the a3 masks are low-weight, so W18 = s1(W16) + W11 + s0(W3) + W2 differs only slightly between mates. Their step-18 states are close.
  - **Consequence:** the H5-extended figure (102.0163) is not supported. The price used is the worst case below, which needs no within-key premise.
- **Tail independence across claws (r39's H5), measured at rows 19-22:**
  - Between-claw one-way ANOVA F = 1.405, 0.330, 0.217 and 0.827 on (9, 50,802) dof, ICC at most 0.0001.
  - Random different-key pairs within a claw: correlation at most 0.010.
  - So there is no claw-level component in tail-row behaviour.
  - Exact survival: through step 18 it is 2^-1.00; through step 19 it is below 2^-14.6 (0 of 25,462). That is why a graded distance is used. **Worst case**, if mates' tails were identical: the trial count becomes the number of distinct passing keys. Over 16 pre-registered batches of 1,000 F9 claws on this list, the 99% lower bound is of 0.894521 over 16,000 claws, adding 0.0859 bit (already included in time 99.7586, Pareto 99.8898). The shipped program prices this worst case (K4_EN_LB = 403.4328 x 0.894521 = 360.880), so the filed figure needs no within-claw tail premise.
- E[N] comes from distinct-claw enumerations only.

## 8. The tail
- The term is 74.3238 (RAT l.10), not credited or adjusted.
- Joint arm: (W8, W10, W11) drawn per lane from 60,000 real k = 4 variant triples (r39tail_k4.py; the same seeds as the advice arm; 14 runs, kat = 1). It gives 6,344 verified collisions against 6,242 for the advice arm, a ratio of 2^+0.023 (s.d. 0.026): no change.
- Pricing at the declared bound QDECL = -74.45 instead would add 0.126 bit (time 101.595, Pareto 102.142).

## 9. Premises
- **H1:** as in r39, extended to the listed (a3, a2). E[N] is measured by exhaustive enumeration of every claw in chunks of the claw space at two-block CVs.
- **H2:** p_tail >= 2^-74.3238 on variant points (Section 8).
- **H3 (changed):** A[6] and A[7] are released over the listed set, and the step-function identity holds through step 15 (Section 2.5).
- **H5:** as in r39. Assumed, not proved:
  - tail independence across claws that share listed W10 and W11 values;
  - tail independence across the distinct messages of one claw that share (a2, W17) (Section 7; the fully dependent case costs at most 0.083 bit).

## 10. Experiments
- **Scaled W17 independence check (organizer-run, uncounted; r39k4-window-small ind_N, ind_D, ind_H, ind_K, ind_x2):** Scaled-down independence check (organizer-run, uncounted): per evaluated claw [N F8 lanes, D distinct (a2,W10) keys, H lanes with top7(W17*2654435761 mod 2^32) = 0, K distinct keys among them], reported per trial as the sums ind_N, ind_D, ind_H, ind_K, with the per-claw Pearson sum ind_x2; under H5 K ~ Binomial(D, 2^-7) independently across claws and windows. Organizer seeds trials 0-3: ind_x2 = 2.7236, 1.4100, 1.0910, 0.5175 (sum 5.742 on 8 dof, chi-square p about 0.68); sum K = 541 vs 525.7 expected; sum N equals k4 F8 lanes per trial (asserted).
- `r39-transplant-claw`: r39's, asserts unchanged.
- `r39k4-window-small` (k4 on, check mode):
  - 4 windows of 2^21 on the organizer seeds of trials 0-3;
  - the k4 pass runs on the first 2 F9 claws of each trial (`k4_max = 2`). The cap is experiment-only: the `--attack` path asserts `A.k4_max is None` on every window, so every priced run is uncapped;
  - before each trial, a gc assert checks two shapes, the ones a decoded copy of the list (361,638 ints) or a decompressed byte copy (more than 100 kB) would have:
    - no int-element list, tuple, set or dict of 1,024 or more items;
    - no bytes, bytearray or memoryview of 4,096 B or more.
    - In the organizer's script mode, the interpreter keeps a list of 55,849 bytes objects for `__main__`, and the 2,447-byte encoded literal stays alive (resident, counted in Section 6). Neither is a copy, and neither matches these shapes; The decoded list lives only as bit planes; the largest list after a run is r39's own walk state;
  - K4_WIN_EXP hard-asserts (claws, F9, F8F9, lanes, F8 lanes, W17 hits, k4 ops, total ops);
  - K4_WIN_EXP is keyed to the r39k4-window-small organizer seeds 14672896933643966474, 15921217793420643850, 17552297034189817508 and 1866586107145425828. Its tuples were measured on those seeds (an earlier version was keyed to the r39k3 seeds, harm 152);
  - **pass-off control:** each trial is rerun on the same seed with k4 off. It asserts the same (claws, F9, F8) and ops_off == ops_on - k4_ops. So the k4 hook adds exactly its counted ops and changes nothing else in the walk. ops_off per trial: 10,491,617, 10,461,564, 15,477,956 and 11,054,748;
  - **scaled-down independence check (organizer-run, not counted in Mach, so ops and tuples are unchanged).** Per evaluated claw, ind = [N, D, H, K]:
    - N = F8-passing lanes; D = distinct passing (a2, W10) keys;
    - H = lanes whose full W17 hashes (x 2654435761 mod 2^32, top 7 bits) to 0, a target set of 2^25 values;
    - K = distinct keys among those.
    - **Asserted:** sum N = k4 F8 lanes, and K <= H <= N, K <= D <= N. In check mode, every 997th lane's W17 equals the reference.
    - **Organizer seeds:** ind_x2 = 2.7236, 1.4100, 1.0910 and 0.5175 (sum 5.742 on 8 dof, p about 0.68), with 541 key hits against 525.7 expected.
    - **Not used:** a top-bit slice of W17. It is correlated through the shared high bits of the listed a2 values (X² 3,178 on 8 dof on the same seeds), so it does not model the single-value target;
  - **organizer-run cross-claw tail check** (tail_F, tail_n; uncounted, so ops and tuples are unchanged):
    - **Sample:** every 16th F8-passing lane of each evaluated claw. The hit-conditioned tail is stepped from the PUBLISHED step-17 states through rows 18-22 with the lane's own words.
    - **Score:** lanes keeping the published row-18 difference get hd = Hamming distance (uncounted diagnostic) from the published (dA, dE) at rows 19-22.
    - **Statistic:** tail_F = one-way ANOVA F across the trial's claws. Asserted: k4_tail(published pair) = 0; a +1 copy trips in organizer form.
    - **Organizer seeds:** tail_F = 1.2709, 0.0143, 0.0128, 1.4452 (n = 528, 528, 587, 570); sum 2.743 against chi-square(4), p about 0.60.
    - **Effect-size bound, recomputed from the reported values:**
      - With n0 = 2,213 / 8, about 277 lanes per claw, the random-effect model gives sum F / (1 + n0 theta) ~ chi-square(4).
      - The 5% quantile of chi-square(4) is 0.7107, so 1 + n0 theta_U = 2.743 / 0.7107 = 3.860, and theta_U = 0.01034.
      - **ICC <= 0.0103 at one-sided 95%**, organizer-run. The participant-run 10-claw value is ICC <= 0.0001.
    - **It is a proxy.** Rows 19-22 are graded; rows 23-38 are assumed as in r39.
  - **List validity** (moved with k4_selftest):
    - **Exhaustive, participant-run:** tools/k4selftest.py checks every one of the 361,638 entries for h4 = h0, F10, F11, W9, W16 and the trail through step 15 at 3 points ("k4 selftest OK 115010").
    - **Organizer-run:** the sha256 assert on the decoded list (integrity), and in r39k4-window-small, every 32nd lane of the evaluated blocks checked against k4_words (the F8 verdict and W17).
  - **K4_WIN_EXP** (streamed build; trial 0 with K4B = 1): (221,5,0,90504,5208,0,17462224,27953841), (215,3,0,90504,5163,0,8955189,19416753), (226,4,1,90504,9744,0,8955189,24433145), (205,2,0,90504,3866,0,8955189,20009937). Organizer seeds tail_F = 1.2709, 0.0143, 0.0128, 1.4452;
  - **organizer form:** `python3 -I r39joint_k4.py < request.json` from another directory, on Python 3.14.4. 4 trials and 256 trials both give rc 0;
  - negative controls (k4neg2.py), each of which trips its assert:
    - one tuple field +1 in a copy (organizer form) trips 'k4 win';
    - a planted int list, int dict, int set or 5,000-byte bytes object trips 'k4 dup';
    - a k4 tick inflated by 1 op trips 'k4 off';
    - a capped Attack trips the fence.
- `r39-tail-01..14`: r39's.
- **Offline tools:** k4near.py, k4list.py, k4claw.c, k4pair.c, k4verify.py, mk_tailk4.py, mk_r39k4.py.

## l.325 table
| part | status |
|---|---|
| list completeness for the weight <= 2 family | executed (exact bit-serial search per class); higher-weight classes not explored |
| list validity | executed (--k4selftest, every entry) |
| trail universality | proved by hand (Section 2.5, k4 indices), checked at 6 points (0 failures) |
| k4 hook changes nothing but its counted ops | executed (pass-off control in r39k4-window-small, hard-asserted; negative control trips) |
| experiment cap not in the priced path | executed (attack-path assert; negative control trips) |
| one representation of the list | executed (gc assert per trial; negative control trips) |
| within-claw W17 clustering | executed (k4clus.py, k4copass.py); worst-case tail dependence bounded at +0.083 bit (recomputed) |
| success >= 0.39 under clustering | proved (Section 7; margin 2^-40 against a shortfall of 2^-80.2) |
| bit-sliced pass equals the model | executed (check mode; about 60M lanes per chunk-CV cross-checked in k4pair, 0 bad) |
| ops | executed (counted in Mach) and recomputed |
| E[N] | executed (k4pair, every claw of chunk 1 at 4 CVs) |
| end-to-end prefix pairs, rows 0-17 | executed: 8 W17 hits over chunks 0 and 1 (5 with all 28 classes, 3 with the 13-class list), all k4verify PASS |
| tail on variant points | executed (joint W8/W10/W11 arm) |
| H5 at the W17 stage, across claws, windows and distinct keys | executed, organizer-run, at a scaled-down event of probability 2^-7 (r39k4-window-small "ind", 8 claws, Pearson 5.74 on 8 dof) |
| H5 at tail rows 19-22, across claws | executed, organizer-run (graded proxy: r39k4-window-small tail_F, p about 0.76) and participant-run (10 claws, F <= 1.41, ICC <= 0.0001) |
| H5 at tail rows 23-38 (the rest of the 2^-74.3 event) | assumed, as in r39 |

## Appendix B. k4verify compares XOR state differences and modular word differences
Witnesses: R39K4/k4pair_runs.txt (chunk 0, 28 classes) and R39K4/k4sub_runs.txt (chunk 1, 13 classes).


## End-to-end evidence at scale (pre-registration 7, GPU)
- **16 full first-block CVs** (about 1.718e10 claws) with the shipped list: sum N = 2,204,591,813,978, so the expected W17 hits are sum N x 2^-32 = 513.3.
- **Observed: 518** (z = +0.21, Poisson-consistent).
- **All 518 pass k4verify** (states 0-17 and words W0-W17 equal the published pair; conditions true). 0 FAIL. Records: en16_evidence/.

## Appendix C. Full-window base walk of this program (24 participant-run windows of 2^26 walk evaluations, seeds 1000-1023)
| window | base ops | evaluated F9 claws (k4 calls) |
|---|---|---|
| 0 | 459,255,817 | 970 |
| 1 | 460,729,242 | 947 |
| 2 | 460,540,323 | 936 |
| 3 | 462,782,217 | 914 |
| 4 | 466,607,623 | 979 |
| 5 | 461,145,617 | 935 |
| 6 | 463,908,850 | 918 |
| 7 | 463,181,511 | 912 |
| 8 | 460,962,599 | 879 |
| 9 | 461,689,431 | 930 |
| 10 | 466,689,028 | 957 |
| 11 | 461,205,736 | 934 |
| 12 | 461,674,199 | 941 |
| 13 | 460,515,776 | 930 |
| 14 | 463,623,375 | 912 |
| 15 | 463,099,264 | 929 |
| 16 | 458,793,392 | 954 |
| 17 | 463,485,101 | 921 |
| 18 | 463,995,823 | 981 |
| 19 | 462,339,900 | 937 |
| 20 | 462,334,017 | 861 |
| 21 | 464,488,890 | 967 |
| 22 | 460,391,227 | 918 |
| 23 | 446,152,841 | 980 |
| **mean (s.d.)** | **461,649,658 (3,858,918)** | **935.1 (29.7)** |
