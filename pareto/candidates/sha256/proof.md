# SHA-256 reduced to 39 steps: ordinary collision by the transplanted Table 23 pair with two released state words (k = 4), a row-16 claw search and a bit-sliced re-try of W17

The bit-sliced pass is dariolina's W17-only pass (087bf8f8, credited; co-author), carried through Jbenisek's bd3fef7d and there applied to the w3 list; this entry rewrites its counted W17 test (Section 3, k4 pass). This entry (a credited derivative of our accepted 30714e48, Pareto 99.3638, the w3 entry of this text) replaces the w3 60-class list by the w12 256-class k = 4 list (821,520 entries in 3,329 blocks, 280 (class, chunk) groups at chunk 28; Section 3, List) and re-prices the two list-dependent inputs on the pre-declared S142 batch of 48 full w12 windows (Section 7, H6; Appendix D), carried to the shipped program by the exact cut-3 identity (Section 3, k4 pass): the work cap is set from the declared moment premise on this program's measured whole-window totals, so K4_OPS_PER_CLAW is 23,230 (w12, Section 7); and the distinct-key ratio is the entry-weighted bound 0.869384 over 48 full w12 windows, so K4_EN_LB is 789.304 (Section 5); the arrival-order index is charged 1,686 per stored key (6 + 6 x 280 group visits; Section 3, Dedupe gate), the only change to the organizer experiments' asserted counts (+1,218 per stored key, K4_WIN_EXP). 30714e48 was a credited derivative of our 3aa063d1 (Pareto 99.4290): the work cap from the measured whole-window totals instead of the per-part sum, and the entry-weighted key ratio instead of the batch-mean ratio 0.894521; all organizer-experiment outputs unchanged. 3aa063d1 was a credited derivative of our 5ef3293a (Pareto 99.4332): the flush groups each class into chunks of at most 28 blocks instead of 32, so the plane-chunk row is 28,672 B instead of 32,768 B; one group more adds exactly 772 ops to a claw's pass and 6 ops to the index charge per stored key, and the w12 list has 280 (class, chunk) groups at chunk 28 (the w3 list had 77 instead of 76); all non-charge outputs are identical on all organizer seeds. 5ef3293a was a credited derivative of newjordan's 90d39efd (Pareto 99.4430): the claw buffer is a cursor over the insertion-ordered dedupe table (outputs identical on all organizer seeds; charges differ only by the index's ops per stored key), removing the 8,184-byte buffer row; the memory peak is the sum of the table. A second derivative change: the dedupe table holds 1,536 slots (the maximum F9 claws seen in one window over 10,088 full windows is 1269, counting repeats) and the pass was priced at its sampled maximum (441,411 on the w3 list; here the pass enters the price only through the measured window totals, Section 3). Layout of the shared queue: keys sit in the linearly probed dedupe table, as in the base entry, and a 1,536 x 2 B arrival-order index (its own row) holds the slot of each new key; the flush reads that index from the cursor and loads each key from its slot. Reduced controls (MEASURED): at the shipped sizes, and with the table capacity 4 and admission limit 2, all eight experiment fields, charges included, equal 90d39efd's on the organizer seeds. A window needing more than 1,536 slots is the exception bounded under H6 (Section 7).

Prepared 2026-11-09. A credited derivative of Jbenisek's bd3fef7d (Pareto 99.8898), which is a credited derivative of newjordan's 3e96c2b6 (Pareto 101.2483), itself of f14850cb: the construction, the w3 list, the streamed and charged flush, the pass transforms A+B+C and the class/block literal folding are bd3fef7d's, kept unchanged. This entry adds one output-identical rewrite of the counted W17 test: both compared words are formed as literal adds from the shared plane word Xp, s0(Xp + w2b) against Xp + (t16 - u - C17K + W17PUB), which removes the dynamic A17 add and the Dc prelude from the counted path and turns the w2b add into a literal add (Section 3, k4 pass). The pass is now claw-dependent (literal bit patterns change the adder cost) and is priced at its measured maximum over 4,096 claws. Numbers inherited from our r39 entry 5f8e6192 are cited as RAT l.N (R39_ACCEPTED_TERMS.txt). New numbers cite the experiment or tool that produced them; sections not restated here are as in bd3fef7d's proof.

## 1. Target and output
- **Target.** SHA-256 compression reduced to 39 steps, standard IV.
- **Output.** Two 128-byte messages M0 || M1 and M0 || M1': the same random first block M0, then second blocks M1 and M1' = M1 + DL, with differences on words 8..12.
- **Padding.** SHA-256 appends a third block, identical for both messages because their lengths are equal. Equal chaining values after block 2, passed through the same padding block, give equal digests. So a collision of the second 39-step compression is a collision of the 39-step hash.
- **Class.** Ordinary collision: no chaining-value difference (HashSmash.md l.164). Same class, advice and walk as r39 (RAT l.2-3).

## 2. The construction
**2.1 Advice.** The 39-step semi-free-start pair of ePrint 2026/1120 Table 23 (CV_PUB, MP_PUB = BW, M_PUB), 160 bytes, as r39. Credit: sraiw 38912d66, dariolina. **Charged advice: 6,500 bytes = 2^12.66623:** this pair plus the 3,264-byte recipe literal and the 3,076 bytes of per-class literals (Section 6), which are target-specific precomputed data.

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
    - Of the 821,520 entries, 324,324 distinct (a2, W10) keys, 25.3% of keys singletons (9.97% of entries), list clusters of size at most 8 (MEASURED: clus_list.py on the shipped w12 list, the (a2, W10) key of k4clus.py).
    - A coinciding mate counts only if it also passes F8 in that claw. Per F9 claw on the w12 list (k4copass.py, 3,000 random claws, seed 1), 57,620.7 entries pass F8 and 50,415.3 distinct keys pass; the size-biased mean passing cluster is 1.2812, at most 8. Grouping the F8-passing entries of the first 3,000 real F9 claws (k4pair_cls.c grouping by key and by exact W17; CV1 5e2e41c2, chunk 2 of 2^5) gives 66,129.1 passing, 56,342.1 keys, m = 1.3419, at most 8; the larger value is used in Section 7.
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
- **Encoding.** Stored as a 3,264-byte zlib recipe (the 256 classes and one reject bit per candidate, in decoder order), 4,080 base85 characters.
- **Decoding.** At import the list is decoded once in 64-byte steps to verify its running sha256 and to derive the per-class and per-block literal constants; no list object is kept. In the attack, each window flush stream-decodes it again into one chunk of planes at a time (Section 3, STREAMED list; Section 6).
- **Checks.** `--k4selftest` re-verifies every entry: h4, F10, F11, W9, W16, and the trail through step 15.
- **Preprocessing.** About 2^24 operations offline (k4near.py, k4list.py), plus the decode at import.

## 3. The program
- **File.** `r39joint_k4.py` (52,229 B; with r39tail.py (unchanged), 65,535 B of 65,536; sha256 c3d16706...; block indentation at one space per level, AST-identical to the source it was built from; k4_selftest is in tools/k4selftest.py; dedupe gate k4d; pass transforms A+B+C; STREAMED list). The participant-only `--windows` mode moved to tools/windows_mode.txt. is r39joint.py with asserted patches: tools/mk_r39k4.py, then tools/apply_k4fix.py (judge-review fixes: pass-off control, attack-path cap fence, gc assert, lambda margin).
- **Dedupe gate (`k4d`).** Before the pass, each F9 claw (a0, u) is looked up in a per-window table: 1,536 entries x 8 B = 12,288 B, counted in Section 6, at 12 ops per lookup inside the 'k4' tick, plus 1,686 ops per stored key for the arrival-order index (k4d charges 6 + 6 x 280: insertion and the 280 (class, chunk) group visits of the one flush that holds the key; at most 1,536 x 1,686 = 2,589,696 per window).
  - A claw already evaluated in this window is skipped; it would repeat the same messages. If the table is full, the claw is evaluated without being stored, so the gate never fails.
  - **Measured:** 15.5% of passes were on duplicates.
  - **Controls:** a planted duplicate is evaluated once; a full table falls back to evaluating.
- **List.** This entry uses the w12 256-class k = 4 list: 821,520 entries in 3,329 blocks, decoded in the program from a 3,264-byte recipe and checked against W3_SHA at import. Every decoder operation is charged in Mach, and the decoder keeps no list longer than 560 values. Pass charge per evaluated F9 claw: every pass is charged at its own count on the counted path, and the price rests on measured whole-window totals (H6, Section 7), not on a per-claw pass constant; the pass is claw-dependent because the rewritten W17 test adds claw words as literals (Section 3, k4 pass). MEASURED on the S142 w12 windows (pre-cut program, all 48 present): the k4 category (pass, flush and index) averages 1,079,578,907.3 ops per window over 938.35 distinct F9 claws per window, 895,611,757.9 after the cut-3 identity and the index recharge (Appendix D). The organizer experiment r39k4-window-small evaluates the pass over the first 181 of the 3,329 blocks (A.k4_maxblk; the attack path asserts it is unset) and hard-asserts those counts: (221,5,0,90504,5208,0,21645157,32136774), (215,3,0,90504,5163,0,10876279,21337843), (205,2,0,90504,3866,0,10876677,21931425).
- **Work cap (`k4_budget`).** The cap is B windows x K4_OPS_PER_CLAW x 58,959.42 claws per window. K4_OPS_PER_CLAW = **23,230** = ceil((1,369,612,832 + ceil(38,279,885 / sqrt(B eps))) / 58,959.42) with eps = 0.61 x 2^-40 - 2^-78.6018, the smallest cap whose H6 binding bound is at most eps (Section 7; asserted at import). The window totals already contain every part below, so nothing below is charged again; the parts are a decomposition, and their per-part sum ceil(7,829.54 + 12.19 + 7,130.99 + 897.05) = 15,870 (12.19 = index charge 718,848 / 58,959.42) is not used:
  - **Base walk, this program:** mu+ = the nominal model-based 99% upper bound (Student t) over the pre-declared S142 batch of 48 full w12 windows (Appendix D; all 48 present: mean 460,721,008.0, s.d. 3,277,564.1, t(47) = 2.4083) = 461,860,338 ops per window = 7,833.53 per claw; a decomposition figure, not the cap (the cap is set from the whole-window totals, H6, Section 7). It includes the lookup charges (per window: total ops - k4-category ops + 24 x F9 claws, Appendix D). The arrival-order index adds 1,686 ops per stored key, charged in k4d (1,686 = 6 + 6 x 280): 6 at insertion (index store, cursor) and 6 (index and table load) on each of the 280 (class, chunk) group visits of the one flush that holds the key; at most 1,536 keys are stored per window, so at most 2,589,696 ops per window; the S142 windows were run with the earlier charge of 468 per key, and H6 adds the difference, +1,218 x D per window, before pricing. Precedent: 9993eaa8 priced its own program's mean work. The batch used the seeds 500000 + 1000w + i (w = 0..2, i = 0..15; fixed before the run) with the same window generator as the attack (a finite participant-run sample; its scope is stated in H6).
  - **k4 pass:** charged at its own count per evaluated F9 claw over the 280 (class, chunk) groups of the w12 list; no per-claw pass constant enters the price (the w3 figures of 30714e48, 441,411 at chunk 32 and + 772 at chunk 28, are not used here). The counted W17 test is this entry's only functional change on bd3fef7d: the condition A17 = E10 + W17 - W17PUB is rewritten so that both compared words are literal adds from the shared plane word Xp, s0(y) = z with y = Xp + w2b and z = Xp + (t16 - u - C17K + W17PUB) (mod 2^32), which removes the dynamic A17 add and the Dc prelude from the counted path and turns the w2b add into a literal add; the accumulator folds X(s0(y)[i], z[i]) instead of X(A17[i], E10[i]), and the w2b and u broadcasts are no longer built. Cut 3 (this entry): the five broadcast lists (a0A8, a1, a3|a1, a3&a1, a0p) and the two literal lists L8 and La3 are built only inside the index/check/measure arm of k4p, so no broadcast is built or charged on the counted attack path; MEASURED, the hoisted prologue is 197,271 v5 ops per claw over the 280 (class, chunk) groups (the program's `_PRO`, one claw), and a window's attack-path total falls by 197,271 x D for its D distinct claws (MEASURED: window seed 1 at 2^21 walk evaluations with the pass off, 136,800,459 -> 135,419,562 ops for its D = 7 distinct claws, a drop of 197,271 x 7). The S142 window totals are pre-cut counts, carried to the shipped program by this identity and the index recharge (+1,218 x D, Dedupe gate); the cap rests on them (H6). Outputs are unchanged by cut 3: the arm runs in check and measure mode, so the pass-off identity and every observation of r39k4-window-small are identical to the pre-cut program; the K4_WIN_EXP tuples differ from 30714e48's only by the index charge, +1,218 per stored key = +2,436 on the k4 and total ops of each organizer seed (2 stored keys each; MEASURED, all three seeds x trials 0, 1, 3). The pass therefore depends on the claw's literal bits (adder costs of the 0/1 constants) and is not priced at a seed-independent per-claw count but through the measured whole-window totals (H6). On the w3 list (30714e48) the per-group cost (k4x and the k4p prologue) depended on the class only (MEASURED: one value per class, 748 to 781 ops); on the w12 list the prologue is hoisted (cut 3 above) and the group count is 280. Equivalence: fields 0-5 of every K4_WIN_EXP tuple (claws, F9, F8F9, lanes, F8 lanes, W17 hits) equal bd3fef7d's; check mode asserts every 32nd lane against k4_words as before and additionally asserts that the new accumulator's lane bit equals the indicator of W17 != W17PUB, so the new test fires exactly where the old one did; the pass-off identity (ops - k4_ops = 10,491,617, 10,461,564, 11,054,748) is unchanged. Inherited from bd3fef7d and kept: transforms A+B+C, the class and block literal folding (planes constant within a class or 256-entry block folded into literals derived at import from the shipped list), the (a0, u) claw buffer with a1 and w2b recomputed and charged at the flush, and its participant equivalence check (32 seeds, 13,686,190 lanes). Historical controls of the folding chain: 644,403 (filed 5ea5554f, pre-fold), 806,200 (v3, resident planes, transforms A+B), 816,217 (A+B alone, streamed), 869,295 (before any output-identical transforms, Section 3.2); 797,352 was bd3fef7d's exact count with the dynamic test. (Trials 1-3 have one flush each.) That figure is multiplied by the distinct F9 claws per distinct claw, 0.016155: the nominal model-based 99% upper bound (Student t, t(63) = 2.3870) of the distinct evaluated F9 claws D per full window, pooled over 64 full windows of 2^26 walk evaluations (raw D counts, the window as sampling unit: n = 64, sum 60,333, mean 942.7031, s.d. 32.6339, bound 952.4403), divided by the 58,959.42 claws per window over which the cap spreads the work, and rounded up (0.0161542 -> 0.016155). Batch 1: 48 windows, seeds 777000-777011, 801000-801011, 802000-802011 and 803000-803011 (k4dup.py on the predecessor program; distinct (CV, a0, u) among the F9 claws): sum 45,341, mean 944.6042, s.d. 35.3678. Batch 2: 16 windows, the Section 5 seeds 400000 and 400100-400114 (D = the k4d table size of this program): sum 14,992, mean 937.0, s.d. 22.5211. Same count and law in both: one CV per window, the same walk and seed map, 2^26 walk evaluations, D counted before any cap (no window reached the 1,536-key table; maximum 1,016), no seed repeated; this program replays seeds 777000, 777011, 801000, 802011, 803005 and 400000 to the same distinct claws, F9 claws and D as both records (MEASURED). Batch 2 was accumulated adaptively; the bound is a fixed-n nominal Student-t bound and no sequential coverage is claimed. This gives 7,130.99.
  - **Flush (once per window):** F = 52,889,692 ops = 897.05 per claw, read from the program (F = K4_PLANE_OPS + K4_INFB x K4_RAW). (i) The plane build is now executed and charged op by op inside Mach: each entry is OR-ed into its word (12 ops), then a lane-parallel 5-stage 32 x 32 delta-swap transpose on the 256-bit words (80 pairs x 22 ops + 15 per 256-entry block), giving exactly the planes of the previous build; K4_PLANE_OPS = 51,091,677. (ii) The inflate and varint decode is charged at 37 ops per raw byte x 48,595 B = 1,798,015, from a counted puff-style decoder (36.351 ops per raw byte, byte-identical output) instead of the declared 64. (iii) The list's sha256 runs only at import (verification), not in the per-window flush. Extra flushes: X = max(ceil(N / 1,023) - 1, 0) for the N distinct F9 claws of a window, each extra flush executed and charged in Mach. Extra flushes are charged as executed and are inside the measured window totals of H6; no tail model of N is used. Raw F9 claws per window (at least N): mean 1,106.89, s.d. 41.13, max 1,250 over the 300 windows of Appendix D.
  - **List setup:** included in the flush above (the counted plane build).
  - **So the cap is 2^98.729131 compressions;** the claimed time 98.7292 is its ceiling. The stage-2 walk loops are unchanged from the base entry (identical source), so their bounds are as stated there. The per-window figure 1,369,627,326.6 is above the nominal 99% bound on the mean window total; 13 of the 48 declared windows exceed it, which is allowed: the cap is on the total over B windows (H6, Section 7).
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
| base walk ops per distinct claw | 7,833.53 (mu+, the S142 w12 windows of THIS program, nominal 99% UB; all 48 present) | Section 3, Appendix D; a decomposition figure, the price rests on the H6 totals; r39's accepted 8,331 is not used |
| k4 pass per evaluated F9 claw | charged at its own count (no per-claw constant enters the price; H6 uses measured window totals); literal-add W17 test, transforms A+B+C, class and block literal folding, no broadcasts on the counted path (cut 3: built only in the index/check/measure arm, -197,271 per claw over the 280 groups); streamed. MEASURED on the S142 w12 windows (all 48 present): k4 category (pass, flush, index) 895,611,757.9 per window over 938.35 distinct F9 claws after the cut-3 identity and the index recharge | counted k4p ops in the program; output-identical to the dynamic test |
| evaluated F9 claws per distinct claw | 0.016104 (distinct only, dedupe; 99% UB of the per-window D over the S142 w12 windows, / 58,959.42; raw rate 0.018787; all 48 present) | Appendix D (the S142 window rows) |
| list flush per window | 52,889,692 / 58,959.42 = 897.05 per claw (counted plane build 51,091,677 + decode at 37 ops per raw byte) | charged in `k4f` |
| ops per claw | 23,230 = 8.2610 compressions, term 3.0463 (cap from the H6 window totals; per-part sum 15,870 not used) | K4_OPS_PER_CLAW |
| W17 tries per distinct claw, E[N] | 907.8892, the one-sided 99% lower bound over 48 FULL w12 windows (entries per window / 58,959.42 claws: mean 919.616, s.d. 33.735, t(47) = 2.4083); cross-check: the 8-CV full enumeration of the w12 list gives a mean of 916.662 entries per claw (k4ok_w12_cv1..8), not used for the price | the S142 w12 windows (the program's `entries` field; the same 48 windows as H6, Section 7) |
| W17 | 32 | |
| tail | 74.3238 (RAT l.4) | Section 8 |
| successes needed | -1.0166 (P = 0.39) | |
| **time, unconditional on within-claw tail independence (the program's K4_EN_LB = 789.304)** | **98.7292** | -log2(907.8892 x 0.869384) + 32 + 74.3238 + 3.0463 - 1.0166 = 98.7291, ceiled to the program cap 2^98.729131. Trials are counted as distinct passing (a2, W10) keys. 0.869384 is a conservative factor chosen under a paired MODEL with the full window as the sampling unit: in 48 full w12 windows of this program, with K distinct passing keys and N passing entries per window, the lower solution r of mean(K - r N) - t(47, 0.99) sd(K - r N) / sqrt(48) = 0 is 0.86938437 (pooled sum K / sum N = 0.869893), and 0.869384 is below it. Windows (seed: K/N): 500000: 47529337/54688237, 500001: 47713421/54762235, 500002: 44731537/51406243, 500003: 46247429/53223617, 500004: 48024169/55241307, 500005: 46615087/53592836, 500006: 45386462/52191250, 500007: 46147576/52953152, 500008: 46283246/53204045, 500009: 47809659/54945540, 500010: 44987415/51677732, 500011: 46358049/53328037, 500012: 46857462/53792906, 500013: 45138721/51759631, 500014: 44625378/51159788, 500015: 50088560/57650241, 501000: 49070777/56614739, 501001: 47058928/54155049, 501002: 47467869/54491038, 501003: 49242188/56526368, 501004: 46011415/52832971, 501005: 45524505/52384695, 501006: 47238754/54274544, 501007: 46173281/52931031, 501008: 49277325/56544032, 501009: 47774520/55014008, 501010: 48209426/55460199, 501011: 47704269/54835227, 501012: 47695372/54838889, 501013: 44549154/51163150, 501014: 44939545/51597717, 501015: 45949332/52738596, 502000: 49876901/57231590, 502001: 52019771/59810375, 502002: 44622225/51417557, 502003: 47268188/54398761, 502004: 47609494/54777624, 502005: 48146208/55251288, 502006: 48841959/56306335, 502007: 49523223/57028432, 502008: 45650662/52515492, 502009: 49554851/57156689, 502010: 45458081/52239795, 502011: 48909366/56158668, 502012: 47943060/55183698, 502013: 45747490/52414820, 502014: 46178234/53103924, 502015: 48170147/55586532. The windows are the pre-declared S142 batch of 48 full w12 windows (seeds 500000 + 1000w + i, w = 0..2, i = 0..15, fixed before the run; ops/judge/LUNA_JUDGE.md L-60/J-77); every window run is kept, and no sequential 99% coverage is claimed. Entries per walk claw in these windows are 919.62 (48 x 58,959.42 claws), the normalization of E[N]. It replaces 30714e48's w3 factor 0.888393 (16 full w3 windows, the same estimator). |
| **Pareto score, unconditional** | **98.8613** | memory 2^20.1321 (Section 6). History: 99.3638 (30714e48, w3, accepted), 99.4290 (3aa063d1, accepted), 99.4332 (5ef3293a), 99.4430 (90d39efd), 99.8898 (bd3fef7d), 100.3662 (2b3f7ecc, on the board), 102.1023 (293ca62c), 101.9356 (02a8f734), 101.4490 (f14850cb), 101.1009 (3a474464), 101.0983 (9cf5ae57, on the board), 101.2483 (3e96c2b6, newjordan) |

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
| per-block literals, 3,329 x 2 x 4 B | 26,632 | resident |
| claw-buffer cursor (the queued claws are the dedupe-table entries after it) | 4 | resident (per window) |
| pass literals per (claw, chunk) group: the two shared constant planes 2 x 32 B and the literal scalars w2b and (t16 - u - C17K + W17PUB) 2 x 4 B | 72 | transient |
| decoder's current block | 1,024 | transient |
| hit-output records and varint parser state | 128 | transient |
| recipe literal (zlib) | 3,264 | resident |
| per-class literals (256 classes) and K4_N | 3,076 | resident |
| decode transient: input bytes 3,264; inflate window 4,096; zlib inflate state and z_stream 7,500; one output step 64; sha256 state about 128; scalars about 64 | 15,116 | transient (only during the list decode: `_w3gen` and its reader closures) |
| dedupe table: 1,536 x (a0, u) x 8 B | 12,288 | resident (per window) |
| dedupe occupancy bitmap, 1,536 bits | 192 | resident (per window) |
| dedupe insertion-order index (slot of each key in arrival order), 1,536 x 2 B | 3,072 | resident (per window) |
| **peak** | **1,149,096 = 2^20.1321** | |

**Memory layout.** The r39 base rows are as accepted (RAT l.8, 1,047,428 B) and are not re-described here. The rows this entry adds are flat arrays with no per-entry overhead. Dedupe table: 1,536 slots of 8 B holding (a0, u), probed linearly, with a separate occupancy bitmap of 1,536 bits (192 B, its own row). Arrival-order index: 1,536 x 2 B holding the slot of each new key in arrival order, plus a cursor register; the flush reads the index from the cursor and loads each key from its slot. There is no separate claw buffer. Per-block literals: an array of 3,329 x 2 32-bit words. Per-class literals: 256 x 3 32-bit words plus K4_N. Recipe literal: 3,264 bytes read once, front to back, by the inflate decoder, whose window and state are the decode-transient row. Decoder tables: four arrays of 256 32-bit words. Decoder work lists: at most 448 + 560 32-bit values. Plane chunk: at most 28 blocks x 1 KB. Broadcasts: none on the counted path after cut 3 (built only in the index/check/measure arm of k4p); one (claw, chunk) group holds the two shared constant planes (2 x 32 B) and the two 32-bit literal scalars (8 B). Transient rows are live only during a flush; the peak adds every resident row and every flush-transient row, as in the table.

## 7. Success probability and time
- lambda = B x groups per window x E[N] x 2^-32 x p_tail. The program sets lambda = -ln(1 - 0.39) + 2^-40 (`k4_budget`).
- Windows needed: B = 2^79.8354, matching the program's `k4_budget` at K4_EN_LB = 789.304. The work budget is 2^98.729131 compressions, from K4_OPS_PER_CLAW = 23,230 (Section 3). The 2^-40 margin moves the time by about 2^-39 bit, below every printed digit.
- **The cap does not bind before B windows (H6-cap-completion, MODEL with measured inputs).** H6 rests on the measured window totals of the shipped counter, not on per-part maxima: a window's total is every op the program charges in it (base walk, k4d gate and index, every pass at its own count, the flush, any extra flush, any table-full path), so neither the 441,411 pass maximum nor a tail model of N enters it. Batch: the pre-declared S142 batch of 48 full w12 windows (seeds 500000 + 1000w + i, w = 0..2, i = 0..15, fixed before the run; ops/judge/LUNA_JUDGE.md L-60/J-77), each of 2^26 walk evaluations, run on the Luna server by the pre-cut program (the shipped program before cut 3). Cut-3 identity (exact): the measured program differs from the shipped one in the hoisted k4p prologue, 197,271 v5 ops per distinct claw over the 280 (class, chunk) groups (the program's `_PRO`, Section 3), and in the arrival-order index charge, 1,686 instead of 468 per stored key (Section 3, Dedupe gate), so a window's attack-path total under the shipped program is total' = total - 197,271 x D + 1,218 x D for its D distinct claws (= stored keys); the moments below are of total'. Total' ops per window: mean 1,356,306,182.4, s.d. 38,279,884.0, min 1,309,881,530, max 1,559,372,096; nominal one-sided 99% bound on the mean (Student t, t(47) = 2.4083) 1,369,612,832. Cap per window: 23,230 x 58,959.42 = 1,369,627,326.6, which is 14,494.6 ops (0.0011%) above that bound; 13 of the 48 measured totals are above it (largest 13.85% above), which is not a per-window limit: the cap is on the total over all B windows. Premise (declared, true moments): windows are independent draws (distinct seeds, one generator) whose total has true mean mu <= 1,369,612,832 and true s.d. sigma <= 38,279,885. These true-moment values are extrapolated premises supported by the sample (the nominal 99% bound on the mean; the 48-window s.d. rounded up), not proven by it, and the nominal 99% coverage of the mean bound is not a runtime probability. Conditional on the premise, the cap binds only if the total over B = 2^79.8354 windows exceeds B x c with c = 1,369,627,326.6, and the variance inequality gives P(total > B c) <= sigma^2 / [B (c - mu)^2] = 6.466747e-18, below eps = 0.61 x 2^-40 - 2^-78.6018 = 5.5479e-13, the success margin left after the clustering shortfall (next item); 23,230 is the smallest K4_OPS_PER_CLAW with this bound <= eps (23,229 needs c - mu >= 49.5 and has c - mu = -44,464.8). Table overflow (N >= 1,537 distinct keys) changes only which claws are stored; its ops are charged and inside the totals, and no measured window came near it (raw F9 max 1,250).
- **Why the margin.** Hits arrive in clusters: entries in one claw that share (a2, W10) and pass F8 (2.4). Write H for the hit count. Then P(success) = 1 - E[(1 - p_tail)^H]. For clustered H this is at most 1 - exp(-lambda) (compound-Poisson, Jensen). The shortfall is about exp(-lambda) x lambda x p_tail x (m - 1)/2, where m = 1.3419 is the size-biased mean passing cluster measured on real F9 claws (2.4; the random-claw estimate 1.2812 gives 2^-78.9): 2^-78.6018. eps = 0.61 x 2^-40 - 2^-78.6018 = 5.547917680793e-13 agrees to 12 significant digits with the value at the inherited m = 1.115 (5.547917680808e-13), and K4_OPS_PER_CLAW is unchanged. The 2^-40 margin adds 0.61 x 2^-40 to P; after this shortfall and the H6 cap-binding bound 6.466747e-18, P >= 0.39 holds strictly.
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
  - Exact survival: through step 18 it is 2^-1.00; through step 19 it is below 2^-14.6 (0 of 25,462). That is why a graded distance is used. **Worst case**, if mates' tails were identical: the trial count becomes the number of distinct passing keys. Over 48 full w12 windows of this program (window as sampling unit, Section 5), the paired 99% MODEL bound of keys/entries is 0.86938 and the priced factor is 0.869384, adding -log2(0.869384) = 0.2019 bit (already included in time 98.7292, Pareto 98.8613). The shipped program prices this worst case (K4_EN_LB = 907.8892 x 0.869384 = 789.3043, rounded down to 789.304), so the filed figure needs no within-claw tail premise.
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
  - tail independence across the distinct messages of one claw that share (a2, W17) (Section 7; the fully dependent case, -log2(0.869384) = 0.2019 bit, is the case priced).

## 10. Experiments
- **Scaled W17 independence check (organizer-run, uncounted; r39k4-window-small ind_N, ind_D, ind_H, ind_K, ind_x2):** Scaled-down independence check (organizer-run, uncounted): per evaluated claw [N F8 lanes, D distinct (a2,W10) keys, H lanes with top7(W17*2654435761 mod 2^32) = 0, K distinct keys among them], reported per trial as the sums ind_N, ind_D, ind_H, ind_K, with the per-claw Pearson sum ind_x2; under H5 K ~ Binomial(D, 2^-7) independently across claws and windows. Organizer seeds trials 0, 1, 3: ind_x2 = 1.0630, 2.3376, 1.4216 (sum 4.822 on 6 dof, chi-square p about 0.57); sum K = 119 vs 110.2 expected; sum N equals k4 F8 lanes per trial (asserted).
- `r39-transplant-claw`: r39's, asserts unchanged.
- `r39k4-window-small` (k4 on, check mode):
  - 3 windows of 2^21 on the organizer seeds of trials 0, 1, 3 (trial 2 and trials 4 and up return no observations);
  - the k4 pass runs on the first 2 F9 claws of each trial (`k4_max = 2`). The cap is experiment-only: the `--attack` path asserts `A.k4_max is None` on every window, so every priced run is uncapped;
  - before each trial, a gc assert checks two shapes, the ones a decoded copy of the list (821,520 ints) or a decompressed byte copy (more than 100 kB) would have:
    - no int-element list, tuple, set or dict of 1,024 or more items;
    - no bytes, bytearray or memoryview of 4,096 B or more.
    - In the organizer's script mode, the interpreter keeps a list of 55,849 bytes objects for `__main__`, and the 2,447-byte encoded literal stays alive (resident, counted in Section 6). Neither is a copy, and neither matches these shapes; The decoded list lives only as bit planes; the largest list after a run is r39's own walk state;
  - K4_WIN_EXP hard-asserts (claws, F9, F8F9, lanes, F8 lanes, W17 hits, k4 ops, total ops);
  - K4_WIN_EXP is keyed to the r39k4-window-small organizer seeds 14672896933643966474, 15921217793420643850 and 1866586107145425828. Its tuples were measured on those seeds (an earlier version was keyed to the r39k3 seeds, harm 152);
  - **pass-off control:** each trial is rerun on the same seed with k4 off. It asserts the same (claws, F9, F8) and ops_off == ops_on - k4_ops. So the k4 hook adds exactly its counted ops and changes nothing else in the walk. ops_off per trial: 10,491,617, 10,461,564 and 11,054,748;
  - **scaled-down independence check (organizer-run, not counted in Mach, so ops and tuples are unchanged).** Per evaluated claw, ind = [N, D, H, K]:
    - N = F8-passing lanes; D = distinct passing (a2, W10) keys;
    - H = lanes whose full W17 hashes (x 2654435761 mod 2^32, top 7 bits) to 0, a target set of 2^25 values;
    - K = distinct keys among those.
    - **Asserted:** sum N = k4 F8 lanes, and K <= H <= N, K <= D <= N. In check mode, every 997th lane's W17 equals the reference.
    - **Organizer seeds:** ind_x2 = 1.0630, 2.3376 and 1.4216 (sum 4.822 on 6 dof, p about 0.57), with 119 key hits against 110.2 expected.
    - **Not used:** a top-bit slice of W17. It is correlated through the shared high bits of the listed a2 values (X² 177.7 on 6 dof on the same seeds), so it does not model the single-value target;
  - **organizer-run cross-claw tail check** (tail_F, tail_n; uncounted, so ops and tuples are unchanged):
    - **Sample:** every 16th F8-passing lane of each evaluated claw. The hit-conditioned tail is stepped from the PUBLISHED step-17 states through rows 18-22 with the lane's own words.
    - **Score:** lanes keeping the published row-18 difference get hd = Hamming distance (uncounted diagnostic) from the published (dA, dE) at rows 19-22.
    - **Statistic:** tail_F = one-way ANOVA F across the trial's claws. Asserted: k4_tail(published pair) = 0; a +1 copy trips in organizer form.
    - **Organizer seeds:** tail_F = 1.2867, 1.9701, 0.0755 (n = 169, 158, 119); sum 3.332 against chi-square(3), p about 0.34.
    - **Effect-size bound, recomputed from the reported values:**
      - With n0 = 446 / 6, about 74 lanes per claw, the random-effect model gives sum F / (1 + n0 theta) ~ chi-square(3).
      - The 5% quantile of chi-square(3) is 0.3518, so 1 + n0 theta_U = 3.332 / 0.3518 = 9.471, and theta_U = 0.1140.
      - **ICC <= 0.114 at one-sided 95%**, organizer-run. The participant-run 10-claw value is ICC <= 0.0001.
    - **It is a proxy.** Rows 19-22 are graded; rows 23-38 are assumed as in r39.
  - **List validity** (moved with k4_selftest):
    - **Exhaustive, participant-run:** tools/k4selftest.py checks every one of the 821,520 entries for h4 = h0, F10, F11, W9, W16 and the trail through step 15 at 3 points ("k4 selftest OK 115010").
    - **Organizer-run:** the sha256 assert on the decoded list (integrity), and in r39k4-window-small, every 32nd lane of the evaluated blocks checked against k4_words (the F8 verdict and W17).
  - **K4_WIN_EXP** (streamed build; trial 0 with K4B = 1): (221,5,0,90504,5208,0,21642721,32134338), (215,3,0,90504,5163,0,10873843,21335407), (205,2,0,90504,3866,0,10874241,21928989). Organizer seeds tail_F = 1.2867, 1.9701, 0.0755;
  - **organizer form:** `python3 -I r39joint_k4.py < request.json` from another directory, on Python 3.14.4. 3 trials and 256 trials both give rc 0;
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
| success >= 0.39 under clustering | proved (Section 7; margin 2^-40 against a shortfall of 2^-78.6018) |
| bit-sliced pass equals the model | executed (check mode; about 60M lanes per chunk-CV cross-checked in k4pair, 0 bad) |
| ops | executed (counted in Mach) and recomputed |
| E[N] | executed (k4pair, every claw of chunk 1 at 4 CVs) |
| end-to-end prefix pairs, rows 0-17 | executed: 8 W17 hits over chunks 0 and 1 (5 with all 28 classes, 3 with the 13-class list), all k4verify PASS |
| tail on variant points | executed (joint W8/W10/W11 arm) |
| H5 at the W17 stage, across claws, windows and distinct keys | executed, organizer-run, at a scaled-down event of probability 2^-7 (r39k4-window-small "ind", 6 claws, Pearson 4.82 on 6 dof) |
| H5 at tail rows 19-22, across claws | executed, organizer-run (graded proxy: r39k4-window-small tail_F, p about 0.34) and participant-run (10 claws, F <= 1.41, ICC <= 0.0001) |
| H5 at tail rows 23-38 (the rest of the 2^-74.3 event) | assumed, as in r39 |

## Appendix B. k4verify compares XOR state differences and modular word differences
Witnesses: R39K4/k4pair_runs.txt (chunk 0, 28 classes) and R39K4/k4sub_runs.txt (chunk 1, 13 classes).


## End-to-end evidence at scale (pre-registration 7, GPU)
- **16 full first-block CVs** (about 1.718e10 claws) with the shipped list: sum N = 2,204,591,813,978, so the expected W17 hits are sum N x 2^-32 = 513.3.
- **Observed: 518** (z = +0.21, Poisson-consistent).
- **All 518 pass k4verify** (states 0-17 and words W0-W17 equal the published pair; conditions true). 0 FAIL. Records: en16_evidence/.

## Appendix D. Base-walk batch (the pre-declared S142 batch of 48 participant-run full w12 windows of this program, 2^26 walk evaluations each) all 48 present
- Batch, fixed before the run: for each worker w = 0..2, the seeds 500000 + 1000w to 500000 + 1000w + 15 (ops/judge/LUNA_JUDGE.md L-60/J-77). Present: all 48 windows; no duplicate or error records.
- Program: the shipped program path (k4 on, no caps) before cut 3 and with the arrival-order index charged at 468 per stored key. The shipped program differs by the hoisted k4p prologue (-197,271 x D per window) and the index charge (+1,218 x D), both inside the k4 category, so the base figure below is unchanged by both; the constants K4_OPS_PER_CLAW and K4_EN_LB with their import assert set B and the cap, not a window's work.
- Per window: base = total ops - k4-category ops + 24 x F9 claws. The k4 category holds the dedupe gate, pass, index and flush; 24 ops per F9 claw add back at least the gate lookups the base walk includes (12 per lookup, plus at most 12 per miss; misses <= lookups).
- n = 48, mean 460,721,008.0, s.d. 3,277,564.1, min 452,032,092, max 467,823,128. mu+ = mean + t(47, 0.99) x s.d. / sqrt(48) = 461,860,338, with t = 2.4083: a nominal model-based one-sided 99% bound (Student t), not a distribution-free bound. Distinct F9 claws per window (D, the stored keys): mean 938.35, s.d. 32.04, max 1,037 (below the 1,536-slot table), sum 45,041; one-sided 99% upper bound on the mean 949.49 = 0.016104 per distinct claw. Raw F9 claws per window: mean 1107.65, s.d. 38.51, max 1,236.

| w | seeds | base ops per window, in seed order |
|---|---|---|
| 0 | 500000-500015 | 460413576, 457586822, 459731345, 462942419, 463966745, 452032092, 459264653, 462653862, 460514329, 463174133, 455610072, 456468194, 458725330, 463167403, 457555509, 455466946 |
| 1 | 501000-501015 | 459391894, 461369754, 462095611, 463847582, 463410748, 456669038, 465979821, 457458966, 462429814, 454895235, 463353718, 464063732, 463283913, 461859244, 461986117, 463007306 |
| 2 | 502000-502015 | 457871636, 467176297, 460599225, 459261555, 458206018, 460951116, 463250398, 458136984, 461779564, 460993308, 467823128, 462006764, 464197495, 457075592, 461804090, 459099292 |
