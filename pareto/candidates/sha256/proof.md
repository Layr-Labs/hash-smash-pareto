# SHA-256 reduced to 39 steps: ordinary collision by the transplanted pair with two released state words (k = 4); the W17 condition solved on 18-bit prefixes by a generic counted pass

A credited derivative of Jbenisek and dariolina's 3aa063d1, built on dariolina's W17-only pass (087bf8f8), newjordan's literal-add test (90d39efd), Jbenisek's k = 4 construction (293ca62c), sraiw's walk and tail replica (fce2f19e) and the advice pair of 5f8e6192. It replaces our 165eb217, which was refuted on two cost findings: forming and storing the claw-dependent folded pass had no charge (F-TIME-FOLDED-PASS-OMISSION), and the code of the k4 routines had no memory row (F-MEMORY-ATTACK-CODE-OMISSION). In this entry there is no folded pass. The W17 test is one fixed routine whose every operation, including loop control, table loads, register spill and the per-claw constant words, goes through the program's operation counter, and every instruction the attack executes has a memory row. The three claimed figures carry deliberate headroom over the program's own arithmetic (Sections 5 and 6).

Labels: MEASURED = run by us with the shipped program's counters; DERIVED = arithmetic from stated numbers; INHERITED = taken from 3aa063d1 or its bases and not re-measured at scale by us.

## 1. Target and output
- **Target.** `sha256-r39-prefix-v1`: SHA-256 with the first 39 steps in every compression, standard IV, FIPS 180-4 padding, feed-forward, all 256 output bits.
- **Output.** Two distinct 128-byte messages M0 || M1 and M0 || M1': the same random first block M0, second blocks with M1' = M1 + DL (word-wise modular, differences in words 8..12). The lengths are equal, so the padding block is identical and equal chaining values after block 2 give equal digests. Ordinary collision, no chaining-value difference.
- **Claim.** time_log2 = 98.5761, memory_log2_bytes = 20.4095, preprocessing_log2 = 43, advice 1,344 bytes = 2^10.39232, success probability 0.39. The time is total charged work (work cap, one-time setup, 2^43 preprocessing) plus a stated headroom; the memory is the row sum 1,359,915 bytes plus a stated headroom of 32,768 bytes.

## 2. The construction (INHERITED from 293ca62c and 38912d66; identities re-checked by us)
**2.1 Advice.** A 39-step semi-free-start pair on the characteristic of ePrint 2026/1120 Tables 21 and 23: CV_PUB, MP_PUB = BW and M_PUB, 160 bytes, the pair of 5f8e6192. It collides from CV_PUB under 39 steps (checked: experiment r39-transplant-claw trial 0, and independently by our own 39-step implementation). Charged advice is 1,344 bytes: the pair and the 1,184-byte recipe of Section 2.5. The tables derived from the recipe are built at import (Section 4) and have memory rows (Section 6).

**2.2 The transplant, k = 4.** Indexing: A[0..3], E[0..3] are the chaining value and step r writes A[r+4], E[r+4]. Fix A[8..11], E[12..15] and W12..W15 to the values of MP_PUB. For any cv and any (a0, a1, a2, a3) = A[4..7], steps 0-7 determine W0..W7 and steps 8-11 determine W8..W11 (`k4_words`); the state after step 11 is then the advice state, so both messages follow the advice states through step 15 whenever the step-8..15 differences are the advice ones. Closed forms (expanded from the step equations; 0 mismatches in 3,500 random checks of our own implementation):
- W9 = C - a1 + h4(a2, a3), h4 = MAJ(A8, a3, a2) - CH(E12, E11, E10), E10 = a2 + t(a3), E11 = a3 + c11;
- W10 = kappa(a3) - a2; W11 depends on a3 only; W2 = a2 + c2(cv, a0, a1); W0 and W1 do not depend on (a2, a3).

**2.3 Row 16 is a claw.** W16 = s1(W14) + W9 + s0(W1) + W0. On the fibre h4(a2, a3) = h4(BA[6], BA[7]) = h0, W9 and W16 are those of the base, and W16 = g holds exactly when F(a0) = F(u), a0 even, u = W1 odd, for the 32-bit map F of the walk (`fstep`). Claws are found by the distinguished-point walk of fce2f19e, unchanged.

**2.4 What remains to pay after a claw.** Once per claw: W9 in F9 (density 65/4096). Per listed (a3, a2): W8 in F8 (density 9/128; depends on a0..a3); W10 in F10 and W11 in F11 (paid in the list); and W17 = s1(W15) + W10 + s0(W2) + W1 equal to the advice value. Then the tail, rows 18 to 38 (Section 8). With x = W2 the W17 condition is s0(x) - x = R with R depending on the claw and on kappa(a3) only (0 mismatches in 500 checks). **So two entries with the same a2 and the same kappa (equivalently the same W10) pass or fail W17 together in every claw.** They are called mates; they differ in a3, hence in W11, W3..W7, W8 and every tail word.

**2.5 The list and its keys (DERIVED and MEASURED; every count below was reproduced by our own enumeration, independent of the leader's program).**
- Classes: a3 = BA[7] XOR a mask of weight at most 3: 5,489 values. 204 pass F11; 61 of those have solutions a2 of h4 = h0 (exact bit-serial search, 4,672,448 solutions); 386,788 solutions also pass F10; **361,638 of those, in 60 classes, keep the advice state-difference trail through step 15.** This is the list of 3aa063d1 (our decoder reproduces its sha256 `51ebea4a...8f5a`). The counts 179,844 and 165,662 quoted in earlier proofs of this line are the same quantities for masks of weight at most 2 (28 classes); the 115,010 list was the 13 largest of those classes.
- The trail verdict is a function of (a2, a3) only (argument of 293ca62c Section 2.5: a2 and a3 meet a difference only through CH at steps 9 and 10 and through D10, D11). We checked every entry at one point and the weight-2 entries at three points; verdicts never differed.
- Keys: the 361,638 entries have **169,908 distinct (a2, kappa) keys** in 21 kappa groups (mean 2.13 entries per key).
- Shipped recipe: 35 classes and one reject bit per F10-passing candidate, in decoder order (252,276 candidates). A candidate is rejected when it fails the trail or when its key is already listed by an earlier class. Every key of the 361,638-entry list is listed exactly once (asserted when the recipe is built: the key sets are equal). 1,184 zlib bytes (window 4,096), 1,480 base85 characters. The decoder is 3aa063d1's with three changes: its two inflate readers are opened with a 4,096-byte window, both are counted, and the sha256 self-check of the decoded list runs only in the experiment entry. Every import asserts the count 169,908.
- From the decoded list the program derives, once at import, the table the attack uses: for each of the 21 kappa groups, the distinct values of a2 mod 2^18 over the group's keys. There are **7,960 such prefixes in all, in 41 blocks of at most 256 lanes** (640 per group at most), stored as 18 bit planes per block.

## 3. The W17 pass
**3.1 The equation.** For a claw and a kappa group the W17 condition on a listed key is s0(y) = y + r (mod 2^32), with y = a2 + w, w = w2b of the claw and r = kd + W17 - u - w, where kd is the group constant and W17 the advice value (Section 2.4; s0 is the small sigma0 of SHA-256). Write k_i for the carries of y + r. Bit i of the equation reads y_i XOR r_i XOR k_i = y_(i+7 mod 32) XOR y_(i+18 mod 32) XOR y_(i+3), the last term absent for i >= 29.
- For i = 0..13 the equation gives y_(i+18) from bits already known. **So the low 18 bits of y determine the other 14.**
- For i = 14..31 the equation is a check: 18 checks.
- A solution of the W17 condition is therefore the unique completion of its low 18 bits, and those are (a2 + w) mod 2^18, a function of a2 mod 2^18 and the claw.

**3.2 The pass (`k4q`).** Lanes are the 7,960 prefixes of Section 2.5, 256 per word. Per evaluated F9 claw:
1. Spill and later restore 104 registers of the interrupted walk (2 x 104 x 3 = 624). Compute a1 and w (`k4x`, 55). Form the 18 constant words of w's low bits (3 each, 54).
2. Per group: loop control (4), loads of the group constant and of the block list (2 x 3), r (4), the 32 constant words of r (96): 110.
3. Per block: loop control (4); load of the lane count (3); the lane mask built from it (shift, subtract: 2); the lane counter update (2); load 18 planes and add w (138); run bits 0..31 of y + r with the 14 determinations and the 18 accumulated checks (250); mask and test (4). **403 operations, the same for every claw and every block.**
4. A lane that passes all 18 checks is a survivor. Its y is extracted and the candidate a2 = y - w is tested on scalar words against each shipped class of the group (same W9 as the base, W17 equal to the advice value, W10 in F10). Counted cost: 711 for the survivor (5 operations of the survivor loop, then 16 + 128 extraction + 2 + 560 for the base words) and 563 per class tested (3 for the class load, 560 for the candidate), so between 1,274 and 2,963.
5. A candidate that matches a class is a key hit. All 5,489 masks of weight at most 3 are then enumerated as in 165eb217: a mask with the same W9 and W17 is a mate, a mate with W8 in F8 is completed, both blocks are compressed and compared. Charge 560 per mask and 2 x 2,812 per compressed pair. Mates that fail the trail cost their charge and cannot produce a false output.

Every operation of steps 1 to 3 is a call of `Mach` (XOR, AND, OR, NOT, add, subtract, shift, load) or an explicit charge for loop control, a table load or the spill. There is no literal folding and no claw-dependent code: constants enter as words built by counted operations. The pass count is K4_PASS = 733 + sum over groups of (110 + 403 x blocks) = **19,566**, a formula of the table, evaluated in the program and asserted at import inside the cap constant.

**3.3 Why it finds exactly the same hits.** A listed key satisfies W17 in a claw if and only if its prefix lane survives and the scalar test accepts it: the pass enumerates every prefix of every group, the completion is unique, and the scalar test is the definition. MEASURED: on 200 planted cases (a real F9 claw, an entry drawn from the 361,638-entry list of 3aa063d1 including mates outside the shipped classes, the advice W17 replaced in memory by that entry's W17) this pass and the per-key pass of 165eb217 flag the same number of keys and compress the same number of F8-passing mates, every time. The organizer experiment repeats a planted check for all 21 groups on every evaluated claw (Section 10).

**3.4 Other changes to the program.** The recipe and its decoder are those of 165eb217. The per-window flush of the list is gone: the list is decoded once, at import. The sha256 self-check of the decoded list runs only in the experiment entry; on the `--attack` path the import executes no hash (the count of decoded entries is still asserted). The register file is allocated at 256 words and the inflate readers are opened with a 4,096-byte window. The old per-key bit-sliced pass remains in the file only as a diagnostic of the experiment modes (it feeds the key-dispersion and tail statistics of Section 10); the attack path (`--attack`, check and measure off) does not execute it. The participant-only wasm runner of the kernel generator is removed; the generator is charged at its halt cap, as it already was whenever the runner was absent. The attack is `r39joint_k4.py --attack`.

## 4. Machine model and where each activity is charged
A counted RAM of 256-bit words (collision-frontier-v5): load, store, add, subtract, AND, OR, XOR, NOT, shift, rotate, comparison and conditional branch are primitive operations; 2,812 operations are one 39-step compression. In `Mach` an operation is 1, a load or store 3 (index shift, base add, access) and a branch 2, the prices of the accepted base.

| activity | time charge | memory |
|---|---|---|
| walk kernel, generated per window with the first block's constants folded in | every generation is charged at the generator's halt cap, 575,000 operations, plus 8 per record for relocation; rejected first blocks are charged too (`window_setup`). INHERITED from the accepted walk | two images (7,100 B) and envelope; generator code inside the walk's instruction census |
| walk, distinguished points, stage 2, claw filters | executed through `Mach` | walk rows of Section 6 |
| dedupe gate of repeated F9 claws | 12 per lookup and 468 per stored key | dedupe rows |
| W17 pass | executed through `Mach`, plus explicit spill and loop charges (Section 3.2): 19,566 per evaluated claw | prefix planes, group table, save area, code |
| survivors and key hits | 711 + 563 per class; 560 per mask; 2 x 2,812 per pair (Section 3.2). 560 is a stated composite price for building one candidate's words and testing them; our count of that routine at the walk's prices is 422 | hit-path row, code |
| setup, once per run: inflate by both readers, candidate search, plane build, per-group prefix sets, sort, and every other statement the import executes (constants, advice trajectories, condition tables, base85 decode) | K4_SETUP = 1,185,067,606 operations, asserted in the program, emitted by the experiment and added to the claimed time: the counted decode of 3aa063d1's decoder with inflate at 1,024 operations per raw byte of either reader (their counted figure is 36.351), 256 per accepted lane, 256 per prefix, and 2^30 for everything else the import executes. The 2^30 also covers the decoder's candidate search at this proof's own prices: an operation trace of the import puts that search above 111 million operations where the decoder's own counters charge about 30 million | setup rows |
| advice construction and selection | 2^43 compressions, added to the claimed time. INHERITED | within the walk arena (9993eaa8 Section 11) |
| folded or claw-specialised code | none exists in this entry outside the walk kernel above | |

## 5. The ledger
| term | value | status |
|---|---|---|
| base walk per window, 99% upper bound | 463,618,904 ops (24 windows: mean 461,649,658, s.d. 3,858,918) | INHERITED; our 8 full windows (seeds 1000-1007) reproduce the leader's per-window base ops and F9-claw counts exactly |
| arrival-order index | at most 718,848 ops per window | INHERITED (1,536 keys x 468) |
| distinct groups per window | 58,959.42 | INHERITED |
| evaluated F9 claws per distinct claw | 0.016203 (99% upper bound over 48 windows; mean 0.015997) | INHERITED |
| W17 pass per evaluated F9 claw | **19,566**, exact and the same for every claw | DERIVED from the table; MEASURED: 19,913 of 20,480 sampled claws were free of survivors and each counted exactly this; all 7,511 evaluated claws of our 8 full windows fit the formula |
| survivors per evaluated claw | at most 0.03111 (one-sided 99% bound (S + 2.326 x sqrt(S) + 2) / n from S = 579 survivors in n = 20,480 sampled claws; uniform model 7,960 x 2^-18 = 0.03036; our windows: 218 in 7,511 claws) | MEASURED |
| survivor work per evaluated claw | 93 (rate bound x 2,963, rounded up) | DERIVED |
| key-hit work per evaluated claw | 1,994 (expected: 252,276 candidates x 2^-32 x 33,943,992, every mask priced as a compressed pair; the candidates are the F10-passing solutions of the shipped classes, a superset of the 169,908 keys) | DERIVED |
| ops per distinct claw, raw | 8226.40 (rounded up) = 464,337,752 / 58,959.42 + (19,566 + 2,087) x 0.016203 | DERIVED |
| **ops per distinct claw, K** | **8,309** = ceil(1.01 x raw): 1.00% deliberate headroom | the program asserts K >= 1.01 x raw at import |
| W17 trials per distinct claw | **343.1**, the one-sided 99% lower bound of our own direct measurement (Section 7) | MEASURED |
| tail | **2^-74.45, the declared bound of the shipped replica** | Section 8 |
| windows B | 2^81.163529 (rounded up) | `k4_budget` |
| work cap | 2^98.574042 compressions (rounded up) | B x K x 58,959.42 / 2,812 |
| one-time setup and preprocessing | 1,185,067,606 / 2,812 + 2^43 compressions | Section 4 |
| total charged work | 2^98.574042 compressions (rounded up) | cap + setup + preprocessing |
| **time, claimed** | **98.5761** | at least 0.002 bit above the line above (asserted at import) |

**Headroom is deliberate.** K is at least 1 percent above its formula, the claimed time is at least 0.002 bit above the program's total, and the claimed memory is 32,768 bytes above the row sum. It is a margin against slips of arithmetic and counting; nothing in this proof is paid for out of it.

**Tail pricing.** This entry prices the tail at the declared bound 2^-74.45. At the 14-run mean 2^-74.3238, which 3aa063d1 uses, the same program and K would give 98.4499; that figure is not claimed.

For comparison, 165eb217 charged a folded pass at 167,471 and a flush of 34,322,747 per window (K = 11,193) with forming the fold left out. The pass of this entry costs 19,566 with every operation counted, and there is no flush.

## 6. Memory of the attack path, setup included (every row summed)
| item | bytes | live |
|---|---:|---|
| advice pair (CV_PUB, M, M') | 160 | walk |
| constants and counters | 4,096 | walk |
| free-slot stack | 128 | walk |
| kernel images, 2 x 710 x 5 | 7,100 | walk |
| lane array, 256 words | 8,192 | walk |
| other instructions of the walk, 4,111 x 36 | 147,996 | walk |
| parked scalars | 192 | walk |
| queue, 897 words | 28,704 | walk |
| pair records | 1,024 | walk |
| register file, 256 x 32 | 8,192 | walk |
| stage-1 save area, 32 words | 1,024 | walk |
| walk table, 26,052 words x 32 | 833,664 | walk |
| timing wheel, 128 words | 4,096 | walk |
| *walk subtotal (the table of 9993eaa8, whose walk this program runs)* | *1,044,568* | |
| kernel-image envelope (two 1,024-record images, as 9993eaa8 reserves) | 3,140 | reserve |
| prefix table K4_Q: 41 blocks x 18 planes x 32 B, plus lane counts, group constants, class words, sample keys | 24,172 | resident |
| register save area of the pass, 104 words | 3,328 | per claw |
| walk-kernel generator, one generation: graph records, liveness and register maps, emitted records (largest of 300 sampled chaining values: 781 graph records) | 25,922 | per window |
| walk-kernel generator: generated source text and its line list, 11,491 characters each | 22,982 | per window |
| first-block compression word lists in window setup, 125 words x 4 B | 500 | per window |
| hit path: word lists of two compressions and of the candidate words, 512 words x 4 B | 2,048 | transient |
| output: hex strings of the two messages | 512 | transient |
| output: two 128-byte messages, the first block and one found-pair record | 576 | transient |
| dedupe table, 1,536 x 8 B | 12,288 | per window |
| dedupe occupancy bitmap | 192 | per window |
| arrival-order index, 1,536 x 2 B, and cursor | 3,076 | per window |
| attack state scalars and statistics counters (every other attribute of the Attack object, audit) | 4,128 | resident |
| operation counter: category and census tables, 77 entries x 8 B | 616 | resident |
| recipe W3_LIT, decoded bytes object | 1,184 | resident |
| recipe, base85 text of the same literal | 1,480 | resident |
| fold literals K4_BLOCK_CONST and K4_CLASS_CONST (audit) | 5,876 | resident |
| all other module-level data left by import (audit; largest: BY_BIT_16_17, CONDS_16_17, p, _W18_HIST) | 15,675 | resident |
| setup: three decoder blocks of 32 words (under construction, transposition copy, consumer) | 3,072 | setup |
| setup: decoder sigma0 tables, 4 x 256 x 4 B | 4,096 | setup |
| setup: decoder work lists, 448 low halves, and 560 high halves held twice, 4 B each | 6,272 | setup |
| setup: decoder search stack, at most 13 entries x 16 B | 208 | setup |
| setup: two inflate readers opened with a 4,096-byte window: window 4,096 + state 7,500 each | 23,192 | setup |
| setup: reader input and output steps, 4 x 64 B, and scalars | 320 | setup |
| setup: per-group prefix sets, 7,960 x 4 B, and class sets | 32,428 | setup |
| setup: sorted copy of one group (640 x 4 B), one slice (256 x 4 B), one block of planes | 4,160 | setup |
| k4 code, 3,164 instructions x 36 B (convention below) | 113,904 | resident |
| **row sum** | **1,359,915 = 2^20.3751** | |

- **Claimed: memory_log2_bytes = 20.4095, which is the row sum plus 32,768 bytes of deliberate headroom (1,392,683 bytes), rounded up.**
- **How the table was made.** Element counts come from an audit of the shipped source: every module-level object left by the `--attack` import, every attribute of the attack object after a window, and every growth site were listed and sized. Element widths are the machine model's: 32 bytes for a 256-bit word, 4 for a scalar or 32-bit word, 5 for a walk-kernel record, 1 per byte of text. Rows marked setup are live only during import and are summed with the rest.
- **Walk rows.** Checked against the allocations of the source: table 26,052 words (`table_words`), queue 897 words, wheel 128 words, lanes 256 words, save 32 words, register file 256 words (`s.R`), two images of at most 710 records (`KCAP`). Four small rows (constants and counters, free stack, parked scalars, pair records) and the 4,111-instruction census (1,246 executed-block, 1,100 routine, 1,765 generator and relocation) are INHERITED from 9993eaa8 Section 6 and not recounted by us; the two audit rows for attack-state scalars and other module data are added on top of them.
- **Growth sites.** The dedupe table stops storing at 1,536 keys (in code). The output lists receive entries only on a collision, which ends the run. The per-group prefix sets exist during import only. The statistics dictionary has a fixed set of keys.
- **Code.** Every k4 instruction has a row, at 36 bytes, the walk's own price for a general instruction. Count: one instruction per syntactic operation of the source of every k4 routine, the experiment-only diagnostic routines included (`_w3gen`, `_k4class`, `_k4new`, `_k4acc`, `_k4tr`, `k4_x`, `k4_eval`, `k4x`, `k4f`, `k4p`, `k4q`, `k4d`, `k4_budget`, `k4_words`, `k4_second`, `K4BS`, `inF`: 1,318); the W17 pass a second time in looped machine form, one instruction per counted operation of one block, one group prologue and the claw prologue (403 + 110 + 733 = 1,246); and 600 for an inflate reader. 3,164 instructions, 113,904 bytes. The count is a convention of ours and is deliberately on the high side.
- **Walk-kernel generator.** Its working memory is measured at allocated size: the generator was run as `window_setup` runs it on 300 chaining values and the largest element counts were taken (781 graph records, 11,491 characters of generated text). One generation is live at a time. `--attack` releases the previous attack object before it builds the next.
- **What the table covers.** All memory the `--attack` path allocates, setup included, and all k4 code, whichever path runs it. The experiment entry allocates, on top of that, the statistics containers and plane chunks of its diagnostics; the `--attack` path never allocates them, and they are the experiments' memory, listed nowhere in this table.

## 7. Success probability and the cap
- lambda = B x 58,959.42 x 343.1 x 2^-32 x p_tail with p_tail = 2^-74.45, set to -ln(0.61) + 2^-40 by `k4_budget`; B = 2^81.163529 windows. The run stops at B windows or at the work cap.
- **Trials.** A trial is a key with at least one valid mate passing F8, in a claw passing F9. When such a key hits W17 the program tests every mate, so the key succeeds with probability at least p_tail, whatever the dependence between the tails of its mates. No within-key independence is used; that is the pricing 3aa063d1 calls the worst case, and it is realised here without evaluating any key twice. Across keys and claws independence is premise H5 (INHERITED).
- **Count of trials: 343.1 per distinct claw, from our own measurement.** On 2,000 real F9 claws (8 batches of 250 from 8 full windows) the number of distinct listed keys with a valid mate in F8 is 22346.042 per evaluated F9 claw (s.e. 161.579). The 8 windows have 938.875 distinct F9 claws each on average (s.e. 8.909). Their product divided by the 58,959.42 groups per window is 355.840 trials per distinct claw (s.e. 4.245, from the two relative errors). Its one-sided 99% lower bound, estimate - 2.998 x s.e. with t(7) = 2.998, is 343.113, priced as 343.1. For comparison only, and not used here: 3aa063d1 priced 360.880 and 30714e48 358.406 for the same quantity, from larger enumerations.
- **The cap does not bind before B windows (H6, MODEL).** Work per window = base walk + index + D x (pass + survivors + key hits). The pass is a constant. Means: 461,649,658 + 718,848 + 944.60 x 21,653 = 482,821,930 per window, against the cap 8,309 x 58,959.42 = 489,893,821: margin 1.44% of the cap. Per-window s.d. at most 12,636,332: the walk's 3,858,918, plus 35.37 x 21,653 for D, plus 16,060 for the number of survivors and 7,995,487 for the rare key hit (33,943,992 operations with probability 0.0555 per window), summed with no independence assumed between parts. If windows are independent with these moments, Chebyshev bounds the probability that the cap binds before B windows below 1.2e-24. The moments of the walk and of D (mean 944.60, s.d. 35.37) are INHERITED sample estimates, not proven bounds; this is a model statement, as in 3aa063d1.
- A window with more than 1,536 distinct F9 claws evaluates the excess without storing it (the gate never fails; a repeated claw then costs a second pass, inside the same per-claw charge); our 8 windows had at most 979. The dedupe lookup is priced at 12 operations, the price of the base (INHERITED).

## 8. The tail (INHERITED; priced at the declared bound)
- `experiments/r39tail.py` is the replica of 5f8e6192, unchanged, run by the organizer as r39-tail-01..14. It hard-asserts: 6,398 verified collisions in 45,875,200 proposals; linear mean 2^-74.3238; one-sided 99% bound 2^-74.3978; 99.9% bound 2^-74.4326; and that both bounds exceed the declared QDECL = -74.45.
- **This entry prices the tail at 2^-74.45.** 3aa063d1 prices it at the mean; the judge recorded that as F-COST-TAIL-MEAN and F-EXP-TAIL-MEAN-AS-BOUND. The difference is 0.1262 bit.
- The replica draws W8 in F8 and W9 in F9 on the advice values of W10, W11. For k = 4 variants W10, W11 and W3..W7 differ; 3aa063d1 reports a joint arm on 60,000 real variant triples with ratio 2^+0.023 (s.d. 0.026). INHERITED, not re-run by us.

## 9. Premises
- **H1-claw-model.** First-block chaining values behave as independent uniform values for the walk and the later events; W17 is uniform over claws and keys at the 2^-32 scale, and the 18 check bits of the pass are uniform at the 2^-18 scale (MEASURED: 579 survivors against 621.9 expected). Walk work and yield per window as in Section 5 (INHERITED measurements).
- **H1-ops.** The constants of Section 5. The pass is a constant of the program, not a premise.
- **H2-tail.** p_tail >= 2^-74.45 for a valid entry passing F8 in a claw passing F9 with W17 hit (Section 8).
- **H3-advice-construction.** The advice pair costs at most 2^43 compressions including the 93-pair selection (INHERITED from 9993eaa8 Section 11) and that amount is inside the claimed time; the list costs about 2^24 operations to enumerate offline.
- **H5-group-independence.** Distinct claws and distinct keys are independent trials. Independence between mates of one key is not used.
- **H6-cap-completion.** Section 7, a model with inherited moments.
- **H-implicit-distinct-key-dispersion.** At the scaled event of probability 2^-7 the organizer run counts key hits per claw (Section 10).

## 10. Experiments (organizer sandbox; the program hard-asserts every tuple)
- `r39-transplant-claw`: as in 3aa063d1 (advice collision, fibres, inversion, 255 transplant identities).
- `r39k4-window-small`, trials 0-3: windows of 2^21 evaluations on the organizer seeds, check mode, k4 on for the first 2 F9 claws. The counted pass runs in full on both claws: all 7,960 lanes. Asserted tuples (claws, F9, F8F9, pass lanes, survivors, key hits, k4 ops, total ops): (221,5,0,15920,0,0,40092,10531709), (215,3,0,15920,0,0,40092,10501656), (226,4,1,15920,0,0,40092,15518048), (205,2,0,15920,0,0,40092,11094840). Each k4 ops value is 2 x (19,566 + 480): two full passes and two dedupe-gate charges, to the operation. Each trial also emits k4_setup = 1,185,067,606, the setup constant of the program.
  - Pass-off control: each trial is re-run with k4 off; claws, F9 and F8F9 are equal and ops_off = ops - k4_ops = 10,491,617, 10,461,564, 15,477,956, 11,054,748, the values of 3aa063d1 on the same seeds. The pass adds exactly its counted operations and changes nothing else.
  - Planted check, on every evaluated claw and for each of the 21 groups: a listed key of the group is taken, its W17 in this claw is computed on scalar words, and the pass is run on that group with that value as target; the program asserts that the key is found and that the counted cost of that run is the group's pass cost plus 711 per survivor plus a multiple of 563 between one and the group's class count per survivor. 168 planted keys per run, so survivors are costed under the counter in the organizer run. A survivor is always asserted to satisfy s0(y) = y + r on scalar words.
  - Diagnostics from the per-key pass of 165eb217, run in the experiment modes on the first 181 of its 682 blocks with the operation counter restored afterwards: key hits at a hashed 2^-7 target, N = 36,968 F8-passing lanes, H = K = 301 against 288.8 expected, Pearson sum 3.3720 on 8 dof; cross-claw tail proxy tail_F = 0.3204, 0.0008, 0.0007, 1.8513 on tail_n = 506, 231, 218, 178 lanes.
- `r39-tail-01..14`: unchanged.
- Participant-run (tools, not in the package): the 200 planted equivalence cases of Section 3.3; 20,480 sampled claws; 8 full windows (Appendix A); the ratio measurement on 2,000 real F9 claws.
- No end-to-end collision has been executed by anyone. All experiments are component tests; the claimed time is far outside any run.

## 11. Findings on our 165eb217 and on 3aa063d1, and what this entry does
- F-TIME-FOLDED-PASS-OMISSION (fatal on 165eb217): there is no folded pass. The W17 pass is one fixed routine, executed and charged operation by operation (Section 3.2); its cost is a constant asserted at import.
- F-MEMORY-ATTACK-CODE-OMISSION (fatal on 165eb217), F-EVAL-OMITTED-CODE-AND-FORMATION-COST: every k4 instruction has a row (Section 6).
- F-SCORE-METRIC-MISMATCH: this proof states time and memory separately and nothing else.
- Margins: K, time and memory each carry stated headroom (Sections 5 and 6).
- F-COST-SAMPLED-MAX and its family: the pass is a constant.
- F-COST-TAIL-MEAN, F-CRYPT-TAIL-POINT-ESTIMATE, F-EXP-TAIL-MEAN-AS-PROBABILITY: the tail is priced at the declared bound.
- F-MEMORY-INHERITED-BASE: walk rows itemised; the instruction census inside them is inherited from 9993eaa8 and said so.
- F-MEM-RESIDENT-LITERAL, F-MEM-BLOCK-CONST, F-MEMORY-TABLE-SUM, F-TIME-PASS-UNDERCHARGE, F-EXP-SUBMITTED-TIME-BELOW-CAP: rows for both forms of the recipe and for the literals; the table is summed by the script that prints it; the claimed time is recomputed from the program's constants.
- Still open, as in 3aa063d1: F-PREPROCESSING-CONSTRUCTION-GAP (2^43 inherited), F-CRYPT-CAP-MOMENT-BOUND and F-EXP-CAP-MOMENTS-UNVALIDATED (H6 moments are samples), F-CRYPT-DEPENDENCE-EXTRAPOLATION, F-EXP-RARE-EVENT-EXTRAPOLATION, F-CRYPT-FULL-LIST-VALIDATION, F-EXP-TAIL-VARIANT-TRANSFER, F-EXP-PUBLIC-SEED-SELECTION, F-EXP-SCALED-K4-COVERAGE for the diagnostics, F-EXP-NO-END-TO-END-WITNESS.

## Appendix A. Our full windows of this program (2^26 evaluations, attack path, seeds as in 3aa063d1 Appendix C)
| seed | base ops | F9 claws, raw | distinct F9 claws | k4 ops | survivors | key hits | survivor work |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 459,242,401 | 1,118 | 970 | 19,481,862 | 19 | 0 | 35,466 |
| 1001 | 460,716,162 | 1,090 | 947 | 19,033,751 | 27 | 0 | 48,473 |
| 1002 | 460,526,883 | 1,120 | 936 | 18,817,263 | 28 | 0 | 51,999 |
| 1003 | 462,769,365 | 1,071 | 914 | 18,376,075 | 29 | 0 | 52,147 |
| 1004 | 466,593,739 | 1,157 | 979 | 19,695,258 | 34 | 0 | 68,088 |
| 1005 | 461,132,561 | 1,088 | 935 | 18,792,460 | 25 | 0 | 47,614 |
| 1006 | 463,895,626 | 1,102 | 918 | 18,473,383 | 36 | 0 | 68,947 |
| 1007 | 463,168,827 | 1,057 | 912 | 18,318,743 | 20 | 0 | 35,051 |

Base ops plus 12 per raw F9 lookup equal 3aa063d1's Appendix C values for the same seeds, and the distinct F9 counts are equal, in all 8 windows. Survivor work is k4 ops less 12 per raw lookup, less (468 + 19,566) per distinct claw, less 5,489 x 560 per key hit; it is 711 per survivor plus a multiple of 563, between 1,274 and 2,963 per survivor, in every window. A key hit here is a candidate accepted by a class test; none led to a collision.
