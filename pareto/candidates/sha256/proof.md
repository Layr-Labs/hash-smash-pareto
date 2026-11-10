# SHA-256 reduced to 39 steps: ordinary collision by the transplanted Table 23 pair with two released state words (k = 4), a row-16 claw search and a bit-sliced re-try of W17

The bit-sliced pass is dariolina's W17-only pass (087bf8f8, credited; co-author), carried through Jbenisek's bd3fef7d and there applied to the w3 list; this entry rewrites its counted W17 test (Section 3, k4 pass). This entry (a credited derivative of our accepted 3aa063d1, Pareto 99.4290) changes two priced inputs: the work cap is set from the declared moment premise on this program's measured whole-window totals (H6, Section 7) instead of the per-part sum (15,870, with the base-walk bound over 300 full windows, Appendix D, and the distinct-F9 rate 0.016155 over 64 pooled windows, Section 3), so K4_OPS_PER_CLAW is 15,116 instead of 15,925; and the distinct-key ratio is the entry-weighted bound 0.888393 over 16 full windows instead of 0.894521, so K4_EN_LB is 358.406 instead of 360.880 (Section 5); all organizer-experiment outputs are unchanged. 3aa063d1 was a credited derivative of our 5ef3293a (Pareto 99.4332): the flush groups each class into chunks of at most 28 blocks instead of 32, so the plane-chunk row is 28,672 B instead of 32,768 B; the list then has 77 (class, chunk) groups instead of 76, which adds exactly 772 ops to every claw's pass and 6 ops to the index charge per stored key (468); all non-charge outputs are identical on all organizer seeds. 5ef3293a was a credited derivative of newjordan's 90d39efd (Pareto 99.4430): the claw buffer is a cursor over the insertion-ordered dedupe table (outputs identical on all organizer seeds; charges differ only by the index's ops per stored key), removing the 8,184-byte buffer row; the memory peak is the sum of the table. A second derivative change: the dedupe table holds 1,536 slots (the maximum F9 claws seen in one window over 10,088 full windows is 1269, counting repeats) and the pass is priced at its sampled maximum 441,411. Layout of the shared queue: keys sit in the linearly probed dedupe table, as in the base entry, and a 1,536 x 2 B arrival-order index (its own row) holds the slot of each new key; the flush reads that index from the cursor and loads each key from its slot. Reduced controls (MEASURED): at the shipped sizes, and with the table capacity 4 and admission limit 2, all eight experiment fields, charges included, equal 90d39efd's on the four organizer seeds. A window needing more than 1,536 slots is the exception bounded under H6 (Section 7).

Prepared 2026-11-09. A credited derivative of Jbenisek's bd3fef7d (Pareto 99.8898), which is a credited derivative of newjordan's 3e96c2b6 (Pareto 101.2483), itself of f14850cb: the construction, the w3 list, the streamed and charged flush, the pass transforms A+B+C and the class/block literal folding are bd3fef7d's, kept unchanged. This entry adds one output-identical rewrite of the counted W17 test: both compared words are formed as literal adds from the shared plane word Xp, s0(Xp + w2b) against Xp + (t16 - u - C17K + W17PUB), which removes the dynamic A17 add and the Dc prelude from the counted path and turns the w2b add into a literal add (Section 3, k4 pass). The pass is now claw-dependent (literal bit patterns change the adder cost) and is priced at its measured maximum over 4,096 claws. Numbers inherited from our r39 entry 5f8e6192 are cited as RAT l.N (R39_ACCEPTED_TERMS.txt). New numbers cite the experiment or tool that produced them; sections not restated here are as in bd3fef7d's proof.

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
- **File.** `r39joint_k4.py` (52,229 B; with r39tail.py (unchanged), 65,535 B of 65,536; sha256 c3d16706...; block indentation at one space per level, AST-identical to the source it was built from; k4_selftest is in tools/k4selftest.py; dedupe gate k4d; pass transforms A+B+C; STREAMED list). The participant-only `--windows` mode moved to tools/windows_mode.txt. is r39joint.py with asserted patches: tools/mk_r39k4.py, then tools/apply_k4fix.py (judge-review fixes: pass-off control, attack-path cap fence, gc assert, lambda margin).
- **Dedupe gate (`k4d`).** Before the pass, each F9 claw (a0, u) is looked up in a per-window table: 1,536 entries x 8 B = 12,288 B, counted in Section 6, at 12 ops per lookup inside the 'k4' tick, plus 468 ops per stored key for the arrival-order index (insertion and 77 flush visits).
  - A claw already evaluated in this window is skipped; it would repeat the same messages. If the table is full, the claw is evaluated without being stored, so the gate never fails.
  - **Measured:** 15.5% of passes were on duplicates.
  - **Controls:** a planted duplicate is evaluated once; a full table falls back to evaluating.
- **List.** This entry uses the w3 60-class k = 4 list: 361,638 entries in 1,447 blocks, decoded in the program from a 1,341-byte recipe and checked against W3_SHA at import. Every decoder operation is charged in Mach, and the decoder keeps no list longer than 560 values. Pass charge per evaluated F9 claw in the per-part sum (not the cap): 441,411, the maximum of the counted pass over 4,096 sampled claws at full scale (mean 399,864, p50 399,820, p99 428,703, max 441,411); it is a pricing constant, not a per-claw bound: every pass is charged at its own count, and cap completion rests on measured window totals (H6, Section 7); the pass is claw-dependent because the rewritten W17 test adds claw words as literals (Section 3, k4 pass). The organizer experiment r39k4-window-small evaluates the pass over the first 181 of the 1,447 blocks (A.k4_maxblk; the attack path asserts it is unset) and hard-asserts those counts: (221,5,0,90504,5208,0,17118583,27610200), (215,3,0,90504,5163,0,8611774,19073338), (226,4,1,90504,9744,0,8605264,24083220), (205,2,0,90504,3866,0,8612172,19666920).
- **Work cap (`k4_budget`).** The cap is B windows x K4_OPS_PER_CLAW x 58,959.42 claws per window. K4_OPS_PER_CLAW = **15,116** = ceil((891,207,473 + ceil(13,323,625 / sqrt(B eps))) / 58,959.42) with eps = 0.61 x 2^-40 - 2^-80.2, the smallest cap whose H6 binding bound is at most eps (Section 7; asserted at import). The window totals already contain every part below, so nothing below is charged again; the parts are a decomposition, and their per-part sum ceil(7,829.54 + 12.19 + 7,130.99 + 897.05) = 15,870 (12.19 = index charge 718,848 / 58,959.42) is not used:
  - **Base walk, this program:** mu+ = the nominal model-based 99% upper bound (Student t) over a fixed batch of 300 full windows (Appendix D; mean 461,115,972.1, s.d. 3,769,098.7, t(299) = 2.3389) = 461,624,938 ops per window = 7,829.54 per claw. It includes the lookup charges (per window: total ops - k4-category ops + 24 x F9 claws, Appendix D). The arrival-order index adds 468 ops per stored key, charged in k4d: 6 at insertion (index store, cursor) and 6 (index and table load) on each of the 77 (class, chunk) group visits of the one flush that holds the key; at most 1,536 keys are stored per window, so at most 718,848 ops per window, added to mu+ in the per-part sum. Precedent: 9993eaa8 priced its own program's mean work. The batch used the seeds 400000 + 1000w + i (w = 0..5, i = 0..49; 300 windows, none dropped) with the same window generator as the attack (a finite participant-run sample; its scope is stated in H6).
  - **k4 pass:** 441,411 per evaluated F9 claw, its counted maximum over 4,096 sampled claws (full 1,447-block list; mean 399,864, p50 399,820, p99 428,703, max 441,411). The counted W17 test is this entry's only functional change on bd3fef7d: the condition A17 = E10 + W17 - W17PUB is rewritten so that both compared words are literal adds from the shared plane word Xp, s0(y) = z with y = Xp + w2b and z = Xp + (t16 - u - C17K + W17PUB) (mod 2^32), which removes the dynamic A17 add and the Dc prelude from the counted path and turns the w2b add into a literal add; the accumulator folds X(s0(y)[i], z[i]) instead of X(A17[i], E10[i]), and the w2b and u broadcasts are no longer built. The pass therefore depends on the claw's literal bits (adder costs of the 0/1 constants) and is priced at the measured maximum instead of a seed-independent exact count; the distribution was sampled through the shipped k4p over all 76 (class, chunk) groups of chunk 32 for 4,096 claws with fresh random CVs and (a0, u) (a0 even, u odd), k4x recompute included, and every sample replays deterministically. At chunk 28 every claw's pass is that value + 772 exactly: the per-group cost (k4x and the k4p prologue) depends on the class only (MEASURED: one value per class, 748 to 781 ops, over 512 claws x 8 windows x 60 classes), and chunk 28 adds one group (a 29-block class splits 28 + 1); full-list passes at chunk 28 vs 32 differ by exactly 772 on 6 claws in 3 windows. Equivalence: fields 0-5 of every K4_WIN_EXP tuple (claws, F9, F8F9, lanes, F8 lanes, W17 hits) equal bd3fef7d's; check mode asserts every 32nd lane against k4_words as before and additionally asserts that the new accumulator's lane bit equals the indicator of W17 != W17PUB, so the new test fires exactly where the old one did; the pass-off identity (ops - k4_ops = 10,491,617, 10,461,564, 15,477,956, 11,054,748) is unchanged. Inherited from bd3fef7d and kept: transforms A+B+C, the class and block literal folding (planes constant within a class or 256-entry block folded into literals derived at import from the shipped list), the per-(claw, chunk) broadcast rebuilds charged there, the (a0, u) claw buffer with a1 and w2b recomputed and charged at the flush, and its participant equivalence check (32 seeds, 13,686,190 lanes). Historical controls of the folding chain: 644,403 (filed 5ea5554f, pre-fold), 806,200 (v3, resident planes, transforms A+B), 816,217 (A+B alone, streamed), 869,295 (before any output-identical transforms, Section 3.2); 797,352 was bd3fef7d's exact count with the dynamic test. (Trials 1-3 have one flush each.) That figure is multiplied by the distinct F9 claws per distinct claw, 0.016155: the nominal model-based 99% upper bound (Student t, t(63) = 2.3870) of the distinct evaluated F9 claws D per full window, pooled over 64 full windows of 2^26 walk evaluations (raw D counts, the window as sampling unit: n = 64, sum 60,333, mean 942.7031, s.d. 32.6339, bound 952.4403), divided by the 58,959.42 claws per window over which the cap spreads the work, and rounded up (0.0161542 -> 0.016155). Batch 1: 48 windows, seeds 777000-777011, 801000-801011, 802000-802011 and 803000-803011 (k4dup.py on the predecessor program; distinct (CV, a0, u) among the F9 claws): sum 45,341, mean 944.6042, s.d. 35.3678. Batch 2: 16 windows, the Section 5 seeds 400000 and 400100-400114 (D = the k4d table size of this program): sum 14,992, mean 937.0, s.d. 22.5211. Same count and law in both: one CV per window, the same walk and seed map, 2^26 walk evaluations, D counted before any cap (no window reached the 1,536-key table; maximum 1,016), no seed repeated; this program replays seeds 777000, 777011, 801000, 802011, 803005 and 400000 to the same distinct claws, F9 claws and D as both records (MEASURED). Batch 2 was accumulated adaptively; the bound is a fixed-n nominal Student-t bound and no sequential coverage is claimed. This gives 7,130.99.
  - **Flush (once per window):** F = 52,889,692 ops = 897.05 per claw, read from the program (F = K4_PLANE_OPS + K4_INFB x K4_RAW). (i) The plane build is now executed and charged op by op inside Mach: each entry is OR-ed into its word (12 ops), then a lane-parallel 5-stage 32 x 32 delta-swap transpose on the 256-bit words (80 pairs x 22 ops + 15 per 256-entry block), giving exactly the planes of the previous build; K4_PLANE_OPS = 51,091,677. (ii) The inflate and varint decode is charged at 37 ops per raw byte x 48,595 B = 1,798,015, from a counted puff-style decoder (36.351 ops per raw byte, byte-identical output) instead of the declared 64. (iii) The list's sha256 runs only at import (verification), not in the per-window flush. Extra flushes: X = max(ceil(N / 1,023) - 1, 0) for the N distinct F9 claws of a window, each extra flush executed and charged in Mach. Extra flushes are charged as executed and are inside the measured window totals of H6; no tail model of N is used. Raw F9 claws per window (at least N): mean 1,106.89, s.d. 41.13, max 1,250 over the 300 windows of Appendix D.
  - **List setup:** included in the flush above (the counted plane build).
  - **So the cap is 2^99.248205 compressions;** the claimed time 99.2483 is its ceiling. The stage-2 walk loops are unchanged from the base entry (identical source), so their bounds are as stated there. The per-window figure 891,230,592.7 is above the nominal 99% bound on the mean window total; 131 of the 300 declared windows exceed it, which is allowed: the cap is on the total over B windows (H6, Section 7).
  - **Each premise sits at its own nominal 99% bound,** not 99% jointly. The price assumes each true value lies at or beyond its stated bound (declared premises); no joint or sequential coverage guarantee is claimed (the key-ratio windows were accumulated adaptively, Section 5).
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
    - at a full buffer or at window end (run_window calls k4f), the compressed literal is stream-decoded once, grouping each class into chunks of at most 28 blocks, and every buffered claw runs the unchanged pass on each chunk;
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
| base walk ops per distinct claw | 7,829.54 (mu+, 300 full windows of THIS program, nominal 99% UB) | Section 3; r39's accepted 8,331 is not used |
| k4 pass per evaluated F9 claw | 441,411 (per-part sum only; H6 uses measured window totals; max over 4,096 uniformly sampled claws; literal-add W17 test, transforms A+B+C, class and block literal folding, broadcasts rebuilt per (claw, chunk); streamed; sampled mean 399,864, p50 399,820, p99 428,703) | counted k4p ops in the program, flush subtracted; output-identical to the dynamic test, whose exact count was 797,352 |
| evaluated F9 claws per distinct claw | 0.016155 (distinct only, dedupe; 99% UB of the per-window D pooled over 64 full windows, / 58,959.42; raw rate 0.019078) | k4dup.py, winmeasure_k4b.py |
| list flush per window | 52,889,692 / 58,959.42 = 897.05 per claw (counted plane build 51,091,677 + decode at 37 ops per raw byte) | charged in `k4f` |
| ops per claw | 15,116 = 5.3755 compressions, term 2.4264 (cap from the H6 window totals; per-part sum 15,870 not used) | K4_OPS_PER_CLAW |
| W17 tries per distinct claw, E[N] | 403.4328, the one-sided 99% bound over 16 FULL first-block CVs (mean 403.4904, s.d. 0.0885, t(15) = 2.602), pre-registration 7. Earlier: 127.7125 from 4 single chunks | k4pair_gpu (exact match with k4pair: same claws, F9, N on chunk 2 CV1, and same hits on chunk 1 CV3): every claw of cvs.txt CVs 1-16, about 1.718e10 claws |
| W17 | 32 | |
| tail | 74.3238 (RAT l.4) | Section 8 |
| successes needed | -1.0166 (P = 0.39) | |
| **time, unconditional on within-claw tail independence (the program's K4_EN_LB = 358.406)** | **99.2483** | -log2(403.4328 x 0.888393) + 32 + 74.3238 + 2.4264 - 1.0166, ceiled to the program cap 2^99.248205. Trials are counted as distinct passing (a2, W10) keys. 0.888393 is a conservative factor chosen under a paired MODEL with the full window as the sampling unit: in 16 full windows of this program, with K distinct passing keys and N passing entries per window, the lower solution r of mean(K - r N) - t(15, 0.99) sd(K - r N) / 4 = 0 is 0.88840451936 (pooled sum K / sum N = 0.889544), and 0.888393 is below it. Windows (seed: K/N): 400000: 21003854/23661818, 400100: 21488479/24139511, 400101: 21225827/23876216, 400102: 21315659/23930073, 400103: 21555260/24174438, 400104: 20863963/23517071, 400105: 21410245/24009998, 400106: 21487214/24143538, 400107: 22150566/24896232, 400108: 21346321/24003795, 400109: 20313801/22743040, 400110: 21935515/24690077, 400111: 21079295/23774481, 400112: 21456875/24164571, 400113: 20284836/22818428, 400114: 20879817/23447230. The 16 windows were accumulated adaptively (the seed list was extended as runs finished); every window run is kept, and no sequential 99% coverage is claimed. Entries per walk claw in these windows are 404.93 (16 x 58,959.42 claws), the normalization of E[N]. It replaces the earlier 0.894521 (a bound over 16 batches of 1,000 F9 claws): that bound's historical aggregation was not recovered, and the explanation that it weighted ratios equally, while the price needs the entry-weighted E[keys]/E[entries], is inferred. |
| **Pareto score, unconditional** | **99.3638** | memory 2^20.1155 (Section 6). History: 99.4290 (3aa063d1, accepted), 99.4332 (5ef3293a), 99.4430 (90d39efd), 99.8898 (bd3fef7d), 100.3662 (2b3f7ecc, on the board), 102.1023 (293ca62c), 101.9356 (02a8f734), 101.4490 (f14850cb), 101.1009 (3a474464), 101.0983 (9cf5ae57, on the board), 101.2483 (3e96c2b6, newjordan) |

**Class subset.**
- With all 28 classes the measured E[N] is 184.07 (chunk 0, 4 CVs). That gives time 101.32, memory 2^20.72 and Pareto 102.04.
- The 13-class subset is optimal under the Pareto objective: each 256-variant block costs 1,024 B of memory and the same ops.
- Under time-only scoring, all 28 classes would be preferred.

## 6. Memory (peak; every representation of the list is counted)
| item | bytes | kind |
|---|---|---|
| r39 accepted base (RAT l.8) | 1,047,428 | resident |
| one chunk of planes (at most 28 blocks x 1 KB), streamed | 28,672 | transient (per flush) |
| decoder tables, 4 x 256 x 4 B | 4,096 | transient (per flush) |
| decoder work lists, at most 448 + 560 values x 4 B | 4,032 | transient (per flush) |
| per-block literals, 1,447 x 2 x 4 B | 11,576 | resident |
| claw-buffer cursor (the queued claws are the dedupe-table entries after it) | 4 | resident (per window) |
| per-(claw, chunk) broadcast lists, 8 x 32 words | 8,192 | transient |
| decoder's current block | 1,024 | transient |
| hit-output records and varint parser state | 128 | transient |
| recipe literal (zlib) | 1,341 | resident |
| per-class literals (60 classes) and K4_N | 724 | resident |
| decode transient: input bytes 1,341; inflate window 4,096; zlib inflate state and z_stream 7,500; one output step 64; sha256 state about 128; scalars about 64 | 13,193 | transient (only during the list decode: `_w3gen` and its reader closures) |
| dedupe table: 1,536 x (a0, u) x 8 B | 12,288 | resident (per window) |
| dedupe occupancy bitmap, 1,536 bits | 192 | resident (per window) |
| dedupe insertion-order index (slot of each key in arrival order), 1,536 x 2 B | 3,072 | resident (per window) |
| **peak** | **1,135,962 = 2^20.1155** | |

**Memory layout.** The r39 base rows are as accepted (RAT l.8, 1,047,428 B) and are not re-described here. The rows this entry adds are flat arrays with no per-entry overhead. Dedupe table: 1,536 slots of 8 B holding (a0, u), probed linearly, with a separate occupancy bitmap of 1,536 bits (192 B, its own row). Arrival-order index: 1,536 x 2 B holding the slot of each new key in arrival order, plus a cursor register; the flush reads the index from the cursor and loads each key from its slot. There is no separate claw buffer. Per-block literals: an array of 1,447 x 2 32-bit words. Per-class literals: 60 x 3 32-bit words plus K4_N. Recipe literal: 1,341 bytes read once, front to back, by the inflate decoder, whose window and state are the decode-transient row. Decoder tables: four arrays of 256 32-bit words. Decoder work lists: at most 448 + 560 32-bit values. Plane chunk: at most 28 blocks x 1 KB. Broadcasts: 8 x 32 words for one (claw, chunk) pass. Transient rows are live only during a flush; the peak adds every resident row and every flush-transient row, as in the table.

## 7. Success probability and time
- lambda = B x groups per window x E[N] x 2^-32 x p_tail. The program sets lambda = -ln(1 - 0.39) + 2^-40 (`k4_budget`).
- Windows needed: B = 2^80.9744, matching the program's `k4_budget` at K4_EN_LB = 358.406. The work budget is 2^99.248205 compressions, from K4_OPS_PER_CLAW = 15,116 (Section 3). The 2^-40 margin moves the time by about 2^-39 bit, below every printed digit.
- **The cap does not bind before B windows (H6-cap-completion, MODEL with measured inputs).** H6 rests on the measured window totals of the shipped counter, not on per-part maxima: a window's total is every op the program charges in it (base walk, k4d gate and index, every pass at its own count, the flush, any extra flush, any table-full path), so neither the 441,411 pass maximum nor a tail model of N enters it. Batch: the 300 declared windows of Appendix D (same runs; the measured program differs from this one only in K4_EN_LB and K4_OPS_PER_CLAW, which set B and the cap, not a window's work). Total ops per window: mean 889,492,558.4, s.d. 12,699,639.9, min 853,349,384, max 931,254,387; nominal one-sided 99% bound on the mean (Student t, t(299) = 2.3389) 891,207,473. Cap per window: 15,116 x 58,959.42 = 891,230,592.7, which is 23,119.7 ops (0.0026%) above that bound; 131 of the 300 measured totals are above it (largest 4.49% above); the six workers' means are 888,837,178 to 890,060,782. All 1,263 windows the six workers completed (seeds 400000 + 1000w + i, i = 0 to 209 or 210, the 300 included): mean 889,543,121.3, s.d. 13,323,624.2, max 983,152,890; 557 are above the per-window figure 891,230,592.7 (at most 10.31% above), which is not a per-window limit: the cap is on the total over all B windows. Premise (declared, true moments): windows are independent draws (distinct seeds, one generator) whose total has true mean mu <= 891,207,473 and true s.d. sigma <= 13,323,625. These true-moment values are extrapolated premises supported by the sample (the nominal 99% bound on the mean; the 1,263-window s.d. rounded up), not proven by it, and the nominal 99% coverage of the mean bound is not a runtime probability. Conditional on the premise, the cap binds only if the total over B = 2^80.9744 windows exceeds B x c with c = 891,230,592.7, and the variance inequality gives P(total > B c) <= sigma^2 / [B (c - mu)^2] = 1.398195e-19, below eps = 0.61 x 2^-40 - 2^-80.2 = 5.5479e-13, the success margin left after the clustering shortfall (next item); 15,116 is the smallest K4_OPS_PER_CLAW with this bound <= eps (15,115 needs c - mu >= 11.61 and has c - mu < 0). Table overflow (N >= 1,537 distinct keys) changes only which claws are stored; its ops are charged and inside the totals, and no measured window came near it (raw F9 max 1,250).
- **Why the margin.** Hits arrive in clusters: entries in one claw that share (a2, W10) and pass F8 (2.4). Write H for the hit count. Then P(success) = 1 - E[(1 - p_tail)^H]. For clustered H this is at most 1 - exp(-lambda) (compound-Poisson, Jensen). The shortfall is about exp(-lambda) x lambda x p_tail x (m - 1)/2, where m = 1.115 is the size-biased mean passing cluster: 2^-80.2. The 2^-40 margin adds 0.61 x 2^-40 to P; after this shortfall and the H6 cap-binding bound 1.398195e-19, P >= 0.39 holds strictly.
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
  - Exact survival: through step 18 it is 2^-1.00; through step 19 it is below 2^-14.6 (0 of 25,462). That is why a graded distance is used. **Worst case**, if mates' tails were identical: the trial count becomes the number of distinct passing keys. Over 16 full windows of this program (window as sampling unit, Section 5), the paired 99% MODEL bound of keys/entries is 0.88840 and the priced factor is 0.888393, adding -log2(0.888393) = 0.1707 bit (already included in time 99.2483, Pareto 99.3638). The shipped program prices this worst case (K4_EN_LB = 403.4328 x 0.888393 = 358.4069, rounded down to 358.406), so the filed figure needs no within-claw tail premise.
- E[N] comes from distinct-claw enumerations only.

## 8. The tail
- The term is 74.3238 (RAT l.10), not credited or adjusted.
- Joint arm: (W8, W10, W11) drawn per lane from 60,000 real k = 4 variant triples (r39tail_k4.py; the same seeds as the advice arm; 14 runs, kat = 1). It gives 6,344 verified collisions against 6,242 for the advice arm, a ratio of 2^+0.023 (s.d. 0.026): no change.
- Pricing at the declared bound QDECL = -74.45 instead would add 0.126 bit (time 99.4447, Pareto 99.5602).

## 9. Premises
- **H1:** as in r39, extended to the listed (a3, a2). E[N] is measured by exhaustive enumeration of every claw in chunks of the claw space at two-block CVs.
- **H2:** p_tail >= 2^-74.3238 on variant points (Section 8).
- **H3 (changed):** A[6] and A[7] are released over the listed set, and the step-function identity holds through step 15 (Section 2.5).
- **H5:** as in r39. Assumed, not proved:
  - tail independence across claws that share listed W10 and W11 values;
  - tail independence across the distinct messages of one claw that share (a2, W17) (Section 7; the fully dependent case, -log2(0.888393) = 0.1707 bit, is the case priced).

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
  - **K4_WIN_EXP** (streamed build; trial 0 with K4B = 1): (221,5,0,90504,5208,0,17118583,27610200), (215,3,0,90504,5163,0,8611774,19073338), (226,4,1,90504,9744,0,8605264,24083220), (205,2,0,90504,3866,0,8612172,19666920). Organizer seeds tail_F = 1.2709, 0.0143, 0.0128, 1.4452;
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
| within-claw W17 clustering | executed (k4clus.py, k4copass.py); worst-case tail dependence priced at +0.1707 bit (-log2(0.888393)) |
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

## Appendix D. Base-walk batch (300 participant-run windows of this program, 2^26 walk evaluations each)
- Batch, fixed before its statistic was computed: for each worker w = 0..5, the seeds 400000 + 1000w to 400000 + 1000w + 49. All 300 windows completed; none dropped; no duplicate or error records.
- Program: the shipped program path (k4 on, no caps). Its only changes since the run are the cap constant K4_OPS_PER_CLAW with its import assert, and a diagnostic dict now built only when the reduced-window instrumentation is on; neither changes the operations charged in a window, and the organizer experiments' asserted counts are unchanged.
- Per window: base = total ops - k4-category ops + 24 x F9 claws. The k4 category holds the dedupe gate, pass and flush; 24 ops per F9 claw add back at least the gate lookups the base walk includes (12 per lookup, plus at most 12 per miss; misses <= lookups).
- n = 300, mean 461,115,972.1, s.d. 3,769,098.7, min 446,076,019, max 472,252,630. mu+ = mean + t(299, 0.99) x s.d. / sqrt(300) = 461,624,938, with t = 2.3389 (2.33888 rounded up): a nominal model-based one-sided 99% bound (Student t), not a distribution-free bound.

| w | seeds | base ops per window, in seed order |
|---|---|---|
| 0 | 400000-400049 | 449186587, 457120456, 463907401, 463489224, 460892149, 463513974, 462287693, 462392122, 458442511, 466927278, 464742815, 459318464, 459482027, 463199446, 457272902, 456886110, 463165058, 463021573, 460062819, 462607631, 466578731, 460398424, 456560392, 462840317, 458127869, 462343812, 463330709, 461597826, 460628026, 460300416, 462460738, 464687454, 457927176, 457651767, 458674883, 460348537, 467617136, 464746064, 459365748, 460301108, 463495421, 461799052, 458795890, 465931795, 469914247, 463085044, 446076019, 463413256, 464981333, 459278458 |
| 1 | 401000-401049 | 462664679, 460822708, 462169407, 466146028, 461171915, 460412941, 464528707, 450245249, 465181392, 459074575, 460807799, 461654372, 468366302, 456518854, 461928202, 464103993, 457331616, 452693599, 460291876, 458941379, 463419569, 464730691, 464287868, 461736897, 462552514, 465071116, 462687747, 472252630, 465419078, 458146289, 458232386, 463281033, 465038025, 459707475, 464615044, 459766699, 460065072, 455949332, 451147531, 465808227, 461444435, 466748742, 467276984, 465092739, 454863709, 457001913, 463588742, 457528556, 463177276, 455034592 |
| 2 | 402000-402049 | 460886149, 465862551, 461420128, 459409968, 450096264, 459654304, 464974348, 461976266, 463163005, 462360091, 463679849, 462250035, 466215737, 459145221, 463674260, 460187165, 463949596, 462809696, 461702885, 462802720, 467714549, 460101322, 463091124, 459390125, 463279365, 463318563, 461293932, 460799332, 460692420, 464407104, 460898722, 467521527, 461336041, 457165914, 456761034, 452709580, 462766372, 455741135, 457818739, 461298516, 469550918, 458563999, 459954575, 459938514, 460312903, 462852404, 462280995, 459018357, 462449179, 459298792 |
| 3 | 403000-403049 | 452701515, 463654797, 467135453, 461618009, 453273008, 466295213, 464196936, 461098962, 456104333, 461090122, 455044900, 455706446, 456202588, 459362102, 461640143, 462393275, 459439223, 456787041, 461783308, 463582072, 456392146, 460236349, 460320390, 456733848, 468796702, 464710083, 462905864, 464104399, 464793390, 457874755, 452807037, 463142579, 461814679, 459908930, 461864754, 462779149, 465525582, 464678969, 458111528, 461934713, 463348704, 460320104, 469462824, 455717768, 462958923, 459270344, 463274121, 461750285, 460900046, 461368986 |
| 4 | 404000-404049 | 460632194, 464542033, 460665018, 462985577, 459493244, 459931164, 464349186, 461740054, 462959172, 453930051, 463729824, 462656854, 458342296, 463516673, 463933545, 461119644, 460283737, 462932016, 458483417, 461492204, 458936502, 462249673, 457830656, 460484135, 450752821, 465849913, 457130530, 470413697, 459221675, 460362099, 460339409, 458222365, 462577998, 455180830, 463146511, 466442232, 464927789, 460311368, 462381619, 455206769, 460882060, 462473500, 463632655, 457362215, 456991905, 458842830, 460882605, 454726125, 461902381, 451516741 |
| 5 | 405000-405049 | 463834194, 456666702, 459566162, 461532179, 452629627, 463471878, 458724095, 461898468, 460999716, 462528548, 455936821, 460866218, 458932186, 461910525, 461831193, 461402429, 460054305, 466198911, 457495822, 465270015, 466165503, 459852185, 461242918, 462167445, 463533490, 461943259, 460772969, 462346234, 462613263, 458478270, 461897111, 457237129, 460852461, 456562744, 463020717, 453724592, 459680596, 463587145, 463225355, 463440438, 462685941, 465536349, 462527811, 464945190, 463445528, 460024410, 460083318, 458031007, 466332607, 460818071 |
