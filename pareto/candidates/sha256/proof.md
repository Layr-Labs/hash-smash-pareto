# SHA-256 reduced to 39 steps: ordinary collision by the transplanted pair with two released state words (k = 4); the W17 condition solved on 18-bit prefixes by a generic counted pass

A credited derivative of Jbenisek and dariolina's 3aa063d1, built on dariolina's W17-only pass (087bf8f8), newjordan's literal-add test (90d39efd), Jbenisek's k = 4 construction (293ca62c), sraiw's walk and tail replica (fce2f19e) and the advice pair of 5f8e6192. It replaces our 165eb217, which was refuted on two cost findings: forming and storing the claw-dependent folded pass had no charge, and the code of the k4 routines had no memory row. In this entry there is no folded pass. The W17 test is one fixed routine whose every operation, including loop control, table loads, register spill and the per-claw constant words, goes through the program's operation counter, and every instruction the attack executes has a memory row. The three claimed figures carry deliberate headroom over the program's own arithmetic (Sections 5 and 6). Our ee52c3c5 was this attack; it was returned not evaluable because four of its premises were stated with too little evidence. This entry adds the accounting of the advice construction (Section 9), prices the cap with confidence bounds on the sample moments (Section 7), counts only the first hit of each window, at a price of 0.0037 bit, so that no independence between tails is used (Section 7), and lets the organizer experiment test key dispersion on all keys of every F9 claw against an acceptance region the program asserts on the measured values (Section 11).

Labels: MEASURED = run by us with the shipped program's counters; DERIVED = arithmetic from stated numbers; CITED = measured and published by the named earlier entry, restated here with its sample size and its source.

## 1. Target and output
- **Target.** `sha256-r39-prefix-v1`: SHA-256 with the first 39 steps in every compression, standard IV, FIPS 180-4 padding, feed-forward, all 256 output bits.
- **Output.** Two distinct 128-byte messages M0 || M1 and M0 || M1': the same random first block M0, second blocks with M1' = M1 + DL (word-wise modular, differences in words 8..12). The lengths are equal, so the padding block is identical and equal chaining values after block 2 give equal digests. Ordinary collision, no chaining-value difference.
- **Claim.** time_log2 = 98.5798, memory_log2_bytes = 20.4095, preprocessing_log2 = 43, advice 1,344 bytes = 2^10.39232, success probability 0.39. The time is total charged work (work cap, one-time setup, 2^43 preprocessing) plus a stated headroom; the memory is the row sum 1,359,951 bytes plus a stated headroom of 32,768 bytes.

## 2. The construction (CITED from 293ca62c and 38912d66; identities re-checked by us)
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

**3.3 Why it finds exactly the same hits.** A listed key satisfies W17 in a claw if and only if its prefix lane survives and the scalar test accepts it: the pass enumerates every prefix of every group, the completion is unique, and the scalar test is the definition. MEASURED: on 200 planted cases (a real F9 claw, an entry drawn from the 361,638-entry list of 3aa063d1 including mates outside the shipped classes, the advice W17 replaced in memory by that entry's W17) this pass and the per-key pass of 165eb217 flag the same number of keys and compress the same number of F8-passing mates, every time. The organizer experiment repeats a planted check for all 21 groups on every evaluated claw (Section 11).

**3.4 Other changes to the program.** The recipe and its decoder are those of 165eb217. The per-window flush of the list is gone: the list is decoded once, at import. The sha256 self-check of the decoded list runs only in the experiment entry; on the `--attack` path the import executes no hash (the count of decoded entries is still asserted). The register file is allocated at 256 words and the inflate readers are opened with a 4,096-byte window. The old per-key bit-sliced pass remains in the file only as a diagnostic of the experiment modes (it feeds the key-dispersion and tail statistics of Section 11); the attack path (`--attack`, check and measure off) does not execute it. The participant-only wasm runner of the kernel generator is removed; the generator is charged at its halt cap, as it already was whenever the runner was absent. The attack is `r39joint_k4.py --attack`.

## 4. Machine model and where each activity is charged
A counted RAM of 256-bit words (collision-frontier-v5): load, store, add, subtract, AND, OR, XOR, NOT, shift, rotate, comparison and conditional branch are primitive operations; 2,812 operations are one 39-step compression. In `Mach` an operation is 1, a load or store 3 (index shift, base add, access) and a branch 2, the prices of the accepted base.

| activity | time charge | memory |
|---|---|---|
| walk kernel, generated per window with the first block's constants folded in | every generation is charged at the generator's halt cap, 575,000 operations, plus 8 per record for relocation; rejected first blocks are charged too (`window_setup`). CITED from the accepted walk | two images (7,100 B) and envelope; generator code inside the walk's instruction census |
| walk, distinguished points, stage 2, claw filters | executed through `Mach` | walk rows of Section 6 |
| dedupe gate of repeated F9 claws | 12 per lookup and 468 per stored key | dedupe rows |
| W17 pass | executed through `Mach`, plus explicit spill and loop charges (Section 3.2): 19,566 per evaluated claw | prefix planes, group table, save area, code |
| survivors and key hits | 711 + 563 per class; 560 per mask; 2 x 2,812 per pair (Section 3.2). 560 is a stated composite price for building one candidate's words and testing them; our count of that routine at the walk's prices is 422 | hit-path row, code |
| setup, once per run: inflate by both readers, candidate search, plane build, per-group prefix sets, sort, and every other statement the import executes (constants, advice trajectories, condition tables, base85 decode) | K4_SETUP = 1,185,067,606 operations, asserted in the program, emitted by the experiment and added to the claimed time: the counted decode of 3aa063d1's decoder with inflate at 1,024 operations per raw byte of either reader (their counted figure is 36.351), 256 per accepted lane, 256 per prefix, and 2^30 for everything else the import executes. The 2^30 also covers the decoder's candidate search at this proof's own prices: an operation trace of the import puts that search above 111 million operations where the decoder's own counters charge about 30 million | setup rows |
| advice construction and selection | 2^43 compressions, added to the claimed time; the sum behind it is in Section 9 | within the walk arena: the selection peaks at 65,536 bytes (Section 9) |
| folded or claw-specialised code | none exists in this entry outside the walk kernel above | |

## 5. The ledger
| term | value | status |
|---|---|---|
| base walk per window, 99% upper bound | 463,618,904 ops (24 windows: mean 461,649,658, s.d. 3,858,918) | CITED; our 8 full windows (seeds 1000-1007) reproduce the leader's per-window base ops and F9-claw counts exactly |
| arrival-order index | at most 718,848 ops per window | CITED (1,536 keys x 468) |
| distinct groups per window | 58,959.42 | CITED |
| evaluated F9 claws per distinct claw | 0.016203 (99% upper bound over 48 windows; mean 0.015997) | CITED |
| W17 pass per evaluated F9 claw | **19,566**, exact and the same for every claw | DERIVED from the table; MEASURED: 19,913 of 20,480 sampled claws were free of survivors and each counted exactly this; all 7,511 evaluated claws of our 8 full windows fit the formula |
| survivors per evaluated claw | at most 0.03111 (one-sided 99% bound (S + 2.326 x sqrt(S) + 2) / n from S = 579 survivors in n = 20,480 sampled claws; uniform model 7,960 x 2^-18 = 0.03036; our windows: 218 in 7,511 claws) | MEASURED |
| survivor work per evaluated claw | 93 (rate bound x 2,963, rounded up) | DERIVED |
| key-hit work per evaluated claw | 1,994 (expected: 252,276 candidates x 2^-32 x 33,943,992, every mask priced as a compressed pair; the candidates are the F10-passing solutions of the shipped classes, a superset of the 169,908 keys) | DERIVED |
| ops per distinct claw, raw | 8226.40 (rounded up) = 464,337,752 / 58,959.42 + (19,566 + 2,087) x 0.016203 | DERIVED |
| **ops per distinct claw, K** | **8,309** = ceil(1.01 x raw): 1.00% deliberate headroom | the program asserts K >= 1.01 x raw at import |
| W17 trials per distinct claw | **343.1**, the one-sided 99% lower bound of our own direct measurement (Section 7) | MEASURED |
| tail | **2^-74.45, the declared bound of the shipped replica** | Section 8 |
| windows B | 2^81.167198 (rounded up) | `k4_budget` |
| work cap | 2^98.577711 compressions (rounded up) | B x K x 58,959.42 / 2,812 |
| one-time setup and preprocessing | 1,185,067,606 / 2,812 + 2^43 compressions | Section 4 |
| total charged work | 2^98.577711 compressions (rounded up) | cap + setup + preprocessing |
| **time, claimed** | **98.5798** | at least 0.002 bit above the line above (asserted at import) |

**Headroom is deliberate.** K is at least 1 percent above its formula, the claimed time is at least 0.002 bit above the program's total, and the claimed memory is 32,768 bytes above the row sum. It is a margin against slips of arithmetic and counting; nothing in this proof is paid for out of it.

**Tail pricing.** This entry prices the tail at the declared bound 2^-74.45. At the 14-run mean 2^-74.3238, which 3aa063d1 uses, the same program and K would give 98.4536; that figure is not claimed.

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
| k4 code, 3,165 instructions x 36 B (convention below) | 113,940 | resident |
| **row sum** | **1,359,951 = 2^20.3751** | |

- **Claimed: memory_log2_bytes = 20.4095, which is the row sum plus 32,768 bytes of deliberate headroom (1,392,719 bytes), rounded up.**
- **How the table was made.** Element counts come from an audit of the shipped source: every module-level object left by the `--attack` import, every attribute of the attack object after a window, and every growth site were listed and sized. Element widths are the machine model's: 32 bytes for a 256-bit word, 4 for a scalar or 32-bit word, 5 for a walk-kernel record, 1 per byte of text. Rows marked setup are live only during import and are summed with the rest.
- **Walk rows.** Checked against the allocations of the source: table 26,052 words (`table_words`), queue 897 words, wheel 128 words, lanes 256 words, save 32 words, register file 256 words (`s.R`), two images of at most 710 records (`KCAP`). Four small rows (constants and counters, free stack, parked scalars, pair records) and the 4,111-instruction census (1,246 executed-block, 1,100 routine, 1,765 generator and relocation) are CITED from 9993eaa8 Section 6 and not recounted by us; the two audit rows for attack-state scalars and other module data are added on top of them.
- **Growth sites.** The dedupe table stops storing at 1,536 keys (in code). The output lists receive entries only on a collision, which ends the run. The per-group prefix sets exist during import only. The statistics dictionary has a fixed set of keys.
- **Code.** Every k4 instruction has a row, at 36 bytes, the walk's own price for a general instruction. Count: one instruction per syntactic operation of the source of every k4 routine, the experiment-only diagnostic routines included (`_w3gen`, `_k4class`, `_k4new`, `_k4acc`, `_k4tr`, `k4_x`, `k4_eval`, `k4x`, `k4f`, `k4p`, `k4q`, `k4d`, `k4_budget`, `k4_words`, `k4_second`, `K4BS`, `inF`, and the experiment's list cache `_k4c1`: 1,319); the W17 pass a second time in looped machine form, one instruction per counted operation of one block, one group prologue and the claw prologue (403 + 110 + 733 = 1,246); and 600 for an inflate reader. 3,165 instructions, 113,940 bytes. The count is a convention of ours and is deliberately on the high side.
- **Walk-kernel generator.** Its working memory is measured at allocated size: the generator was run as `window_setup` runs it on 300 chaining values and the largest element counts were taken (781 graph records, 11,491 characters of generated text). One generation is live at a time. `--attack` releases the previous attack object before it builds the next.
- **What the table covers.** All memory the `--attack` path allocates, setup included, and all k4 code, whichever path runs it. The experiment entry allocates, on top of that, the statistics containers and plane chunks of its diagnostics; the `--attack` path never allocates them, and they are the experiments' memory, listed nowhere in this table.

## 7. Success probability and the cap
- lambda = B x 58,959.42 x 343.1 x 2^-32 x p_tail with p_tail = 2^-74.45, set to (-ln(0.61) + 2^-40) / (1 - 0.00254) by `k4_budget` (the divisor is explained below); B = 2^81.167198 windows. The run stops at B windows or at the work cap.
- **Trials.** A trial is a key with at least one valid mate passing F8, in a claw passing F9. When such a key hits W17 the program tests every mate, so the key succeeds with probability at least p_tail, whatever the dependence between the tails of its mates. No within-key independence is used; that is the pricing 3aa063d1 calls the worst case, and it is realised here without evaluating any key twice. What the count uses of independence is premise H5 (Section 10) and is set out below.
- **Count of trials: 343.1 per distinct claw, from our own measurement.** On 2,000 real F9 claws (8 batches of 250 from 8 full windows) the number of distinct listed keys with a valid mate in F8 is 22346.042 per evaluated F9 claw (s.e. 161.579). The 8 windows have 938.875 distinct F9 claws each on average (s.e. 8.909). Their product divided by the 58,959.42 groups per window is 355.840 trials per distinct claw (s.e. 4.245, from the two relative errors). Its one-sided 99% lower bound, estimate - 2.998 x s.e. with t(7) = 2.998, is 343.113, priced as 343.1. For comparison only, and not used here: 3aa063d1 priced 360.880 and 30714e48 358.406 for the same quantity, from larger enumerations.
- **The trial count in a bracket.** Each figure is a number of keys per F9 claw, times 938.875 F9 claws per window, divided by 58,959.42. Floor, 193.1: the organizer run counts on its 14 claws the keys whose shipped entry passes F8, 12,124 per claw (the rate 9/128 on 169,908 keys gives 11,947), and asserts a floor for their sum (Section 11). Priced, 343.1. Measured, 355.840: on 2,000 claws, 22,346 keys per claw have a listed entry in F8, the shipped one or a mate. Independent-mates model, 375.8: if every listed entry passed F8 at 9/128 independently, the key multiplicities of the list (78,446 keys with 1, 44,912 keys with 2, 18,704 keys with 3, 16,870 keys with 4, 3,136 keys with 5, 3,136 keys with 6, 2,352 keys with 7, 2,352 keys with 8) would give 23,600 keys per claw. The priced figure is 3.6% under the measurement and 8.7% under the model. The measurement is under the model because the mates of one key pass F8 together more often than independent entries would. The floor is what the organizer run observes on its own claws; the 150.0 trials between the floor and the price are keys that are trials through a mate, counted on the 2,000 claws.
- **The cap does not bind before B windows (H6).** Work per window = base walk + index + D x (pass + survivors + key hits), D the distinct evaluated F9 claws; the pass is a constant. The random inputs are known from samples, so each sample moment is replaced by its one-sided upper confidence bound at level 99.75%, which makes the four bounds hold together at 99% (Bonferroni). Samples: base walk, 24 full windows of this walk (3aa063d1 Appendix C: mean 461,649,658, s.d. 3,858,918; the 8 windows re-run here are 8 of those seeds and reproduce their values, Appendix A); D, 48 full windows (3aa063d1 H1-ops: mean 944.60, s.d. 35.37; our 8 windows: mean 938.875, s.d. 25.20). Mean bounds, mean + t x s.d. / sqrt(n) with t(23) = 3.104 and t(47) = 2.946: 464,094,674 and 959.64. S.d. bounds, s.d. x sqrt((n - 1) / q) with q the 0.25% quantile of chi-square, 8.450 on 23 and 24.316 on 47 degrees of freedom: 6,366,506 and 49.18. Both are the normal-theory intervals. Mean work: 464,094,674 + 718,848 + 959.64 x 21,653 = 485,592,607 per window, against the cap 8,309 x 58,959.42 = 489,893,820: margin 4,301,213, 0.87% of the cap. Per-window s.d. at most 15,508,843: 6,366,506 for the walk, plus 49.18 x 21,653 for D, plus 16,190 for the number of survivors and 8,061,252 for the rare key hit (33,943,992 operations with probability 0.0564 per window), summed with no independence assumed between the parts. For independent windows Chebyshev's inequality bounds the probability that the cap binds before B windows below 4.9e-24. At the sample moments themselves the margin is 1.44% of the cap. The organizer's four pass-off windows reproduce 3aa063d1's operation counts on the same seeds to the unit (hard-asserted, Section 11), so the cited samples are samples of the walk the organizer ran. The cap exceeds the sample mean of the work by 7.87 combined standard errors (898,242 operations: 3,858,918 / sqrt(24) for the walk plus 35.37 / sqrt(48) x 21,653 for D), and the Chebyshev figure leaves room for a far larger s.d.
- **The success count uses three things, and no more.** (i) Windows are independent: each has a fresh first block. (ii) A hit is a trial key whose W17 equals the advice value. A window has H hits; E[H] is the mean number of trials of a window times 2^-32, and with 343.1 trials per distinct claw or more, E[H] is 58,959.42 x 343.1 x 2^-32 or more. (iii) Only the first hit of a window is counted. It succeeds with probability p_tail, and a window has a hit with probability E[H] - E[H(H-1)]/2 or more. Given the claws, the W17 events of distinct keys are independent (tested at a scaled event, Section 11), so E[H(H-1)] is E[H]^2 x (1 + c^2), c being the relative spread of the trial count of a window: 2.8% measured (per-claw s.d. 6,391 on 22,346 keys over 939 claws, and 2.7% for the number of claws), which makes the factor 1.002 or less. E[H] is 58,959.42 x 368.57 x 2^-32 = 0.00506 at its upper value (368.57 is the upper one-sided 99% bound of the trial count, 355.840 + 2.998 x 4.245), so the second term takes 1.002 x 0.00506 / 2 = 0.254% of the first. Hence a window succeeds with probability p_tail x 58,959.42 x 343.1 x 2^-32 x (1 - 0.00254) or more, and over B independent windows P(no success) is exp(-lambda x (1 - 0.00254)) or less. `k4_budget` sets lambda = (-ln(0.61) + 2^-40) / (1 - 0.00254), so the success probability is 0.39 or more. Counting first hits only costs 0.0037 bit of time. No independence between the tails of different hits is used, inside a claw or inside a window.
- A window with more than 1,536 distinct F9 claws evaluates the excess without storing it (the gate never fails; a repeated claw then costs a second pass, inside the same per-claw charge); our 8 windows had at most 979. The dedupe lookup is priced at 12 operations, the price of the base (CITED).

## 8. The tail (replica of 5f8e6192, run by the organizer; priced at the declared bound)
- `experiments/r39tail.py` is the replica of 5f8e6192, unchanged, run by the organizer as r39-tail-01..14. It hard-asserts: 6,398 verified collisions in 45,875,200 proposals; linear mean 2^-74.3238; one-sided 99% bound 2^-74.3978; 99.9% bound 2^-74.4326; and that both bounds exceed the declared QDECL = -74.45.
- **This entry prices the tail at 2^-74.45.** 3aa063d1 prices it at the 14-run mean, 0.1262 bit lower.
- The replica draws W8 in F8 and W9 in F9 on the advice values of W10, W11. For k = 4 variants W10, W11 and W3..W7 differ; 3aa063d1 measured the transfer with a joint arm on 60,000 real variant triples, 14 runs: ratio 2^+0.023 (s.d. 0.026). CITED (3aa063d1 H5).

## 9. Advice construction and preprocessing (H3)
The advice pair is the pair of 5f8e6192, chosen among 93 candidate pairs. The accounting is that of 9993eaa8 Section 11, in the form of sraiw's 38912d66 Section 4.2, restated here in full. Its two executed components run in this package's organizer experiment `r39-transplant-claw`.
- **One pair.** Steps 10 to 15 carry 12 state words, 384 bits, under the 350 bit, carry and message-schedule conditions of the Table 23 characteristic: 2^(384 - 350) = 2^34 candidate dense parts. Given steps 10 to 15 and W0..W15, steps 9 down to 0 and the chaining value follow by inverting the step function, with no search (`invert_downward`; the experiment asserts downward_inv_ok = 1). Each candidate is tested for non-empty row-16 and row-17 fibres by an exact bit-by-bit search (`solve_row_exact`). The experiment runs that search on the shipped pair (g16_fibre_size = 2, g17_fibre_size = 1, fibre_dfs_ops = 1,944 word operations) and enumerates a 256-candidate slice of the step-15 free bits (advice_slice_cands = 256, advice_slice_hits = 1, ops_per_cand = 411 word operations). 411 word operations are 0.146 compressions; the charge per candidate is 4 compressions, 27 times that. One pair: 2^34 x 2^2 = 2^36 compressions. The source paper measures about 2^34.2 SHA-256 calls for the same step (ePrint 2026/1120 Section 4.3, Step 1; its Step 2 holds with probability 1).
- **Selection.** 93 pairs were constructed and screened by the tail measurement, one after another. Constructions: 93 x 2^36 = 2^42.5392. Screens: each is charged as the full 14-run design of Section 8. One run is 3,276,800 proposals of two 39-step compressions (2^22.64) plus 800 particles x 38,916 stage lanes of 3 steps each (2^21.2), inside 2^24 compressions; 93 x 14 x 2^24 = 2^34.35. Sum: 2^42.545 compressions.
- **Declared: preprocessing_log2 = 43**, which is 2^0.455 times the sum. The 2^43 is added to the claimed time (Section 5), where it is a 2^-55.6 part of the total.
- **Memory of the selection.** It is sequential. One construction holds one candidate path, 65,536 bytes; one tail run holds 62,144 bytes (table of 9993eaa8 Section 11). Both fit the walk arena of Section 6.
- **The list** costs about 2^24 operations to enumerate offline (Section 2.5). The attack rebuilds what it needs at import, inside K4_SETUP.
- **Scale of the evidence.** Executed in the organizer run: the fibre search on one pair and 256 of the 2^34 candidates. The 2^34 is the dimension count above. The 93-pair campaign was run by the authors of the pair and is charged at its full declared cost.

## 10. Premises, and the limits of their evidence
- **H1-claw-model.** First-block chaining values behave as independent uniform values for the walk and the later events; W17 is uniform over claws and keys at the 2^-32 scale, and the 18 check bits of the pass are uniform at the 2^-18 scale (MEASURED: 579 survivors against 621.9 expected). Walk work and yield per window as in Section 5 (CITED measurements).
- **H1-ops.** The constants of Section 5. The pass is a constant of the program, not a premise.
- **H2-tail.** p_tail >= 2^-74.45 for a valid entry passing F8 in a claw passing F9 with W17 hit (Section 8).
- **H3-advice-construction.** Constructing and selecting the advice pair costs 2^42.545 compressions by the accounting of Section 9, declared as 2^43 and added to the claimed time; the list costs about 2^24 operations to enumerate offline.
- **H5-group-independence.** Windows are independent. The trials of a claw are its keys with a valid mate in F8; their number is a property of the claw and varies between claws (Appendix B), and the count uses its mean, 343.1 per distinct claw or more (bracket in Section 7). Given the claws of a window, the W17 events of distinct keys are independent with probability 2^-32 each. Only the first hit of each window is counted (Section 7). Evidence: the trial count is measured on 2,000 real F9 claws of 8 full windows; the organizer run measures on its own 14 claws the F8 rate of the shipped entries and the dispersion of scaled key hits (Section 11).
- **H6-cap-completion.** Section 7: the four sample moments at joint 99% upper confidence bounds, then Chebyshev.
- **H-implicit-distinct-key-dispersion.** Given the claws, W17 events of distinct keys are dispersed as independent trials: tested in the organizer run at a scaled event over all keys of 14 claws, against an acceptance region the program asserts on the measured sums (Section 11).
- **Limits of the evidence.** The walk and F9 samples are 24 and 48 full windows on public seeds, and their confidence bounds are normal-theory intervals. The trial count is measured on this entry's 2,000 claws; the organizer's 14 claws measure the F8 rate of the shipped entries (7.14% against 9/128 = 7.03%), the floor of the bracket in Section 7. The dispersion test runs at probability 2^-7; the attack's event has probability 2^-32 on the same keys and the same words. The tail replica samples the advice values of W10 and W11, and its transfer to the variants is the 14-run joint arm of 3aa063d1. The rows 19-22 statistic tail_F is replayed for continuity with 3aa063d1; on 20 further local windows its pooled value is 75.08 on 58 degrees of freedom, and the count uses no premise about it (Section 7). The memory peak uses the generator's largest allocation over 300 chaining values. No full collision has been executed: every experiment is a component test, and the claimed time is far outside any run.

## 11. Experiments (organizer sandbox; every organizer-run value is hard-asserted by the program)
- `r39-transplant-claw`: advice collision, fibres, downward inversion and the 256-candidate slice of Section 9, 255 transplant identities.
- `r39k4-window-small`, trials 0-3: windows of 2^21 evaluations on the organizer seeds, check mode, k4 on for every F9 claw of the window (5, 3, 4 and 2 claws, 14 in all). The counted pass runs in full on each: all 7,960 lanes. Asserted tuples (claws, F9, F8F9, pass lanes, survivors, key hits, k4 ops, total ops): (221,5,0,39800,0,0,100230,10591847), (215,3,0,23880,0,0,60138,10521702), (226,4,1,31840,0,0,80184,15558140), (205,2,0,15920,0,0,40092,11094840). Each k4 ops value is F9 x (19,566 + 480): one full pass and one dedupe-gate charge per F9 claw, to the operation. Each trial also emits k4_setup = 1,185,067,606, the setup constant of the program.
  - Pass-off control: each trial is re-run with k4 off; claws, F9 and F8F9 are equal and ops_off = ops - k4_ops = 10,491,617, 10,461,564, 15,477,956, 11,054,748, the values of 3aa063d1 on the same seeds. The pass adds exactly its counted operations and changes nothing else.
  - Planted check, on every evaluated claw and for each of the 21 groups: a listed key of the group is taken, its W17 in this claw is computed on scalar words, and the pass is run on that group with that value as target; the program asserts that the key is found and that the counted cost of that run is the group's pass cost plus 711 per survivor plus a multiple of 563 between one and the group's class count per survivor. 294 planted keys per run, so survivors are costed under the counter in the organizer run. A survivor is always asserted to satisfy s0(y) = y + r on scalar words.
  - Key dispersion (H-implicit-distinct-key-dispersion), from the per-key pass of 165eb217 run with the operation counter restored afterwards, on all 682 of its blocks: every one of the 169,908 keys, in every F9 claw. Per claw, D is the number of keys whose shipped entry passes F8, and K the number of those whose W17, multiplied by 2654435761 mod 2^32, has its top 7 bits zero. That event has probability 2^-7; it is the attack's event with its single target scaled up. Under independent key events K is Binomial(D, 2^-7) in each claw. Acceptance region, fixed in the manifest and asserted by the program on the sums it measures over the four trials: the sum of K within 2.576 standard deviations of the sum of D / 128, and the Pearson sum over claws smaller than 29.14, the 99% quantile of chi-square on 14 degrees of freedom. Asserted per trial, (sum D, sum K, Pearson, tail_F, tail_n, claws): (66,757, 509, 2.7948, 1.6252, 2,055, 5), (36,016, 296, 5.1893, 1.6335, 1,132, 3), (42,074, 317, 4.5737, 0.2648, 1,325, 4), (24,884, 197, 0.0738, 0.2137, 786, 2). Pooled: 169,731 key events, 1,319 hits against 1326.0 expected (z = -0.19), Pearson 12.63. One claw of the 14 lies beyond two standard deviations: 117 hits for 95.4 expected, z = +2.22 (Appendix B); 0.6 such claws are expected among 14.
  - F8 rate (H5): the same pass gives D, 12,124 per claw on average against 11,947 for the rate 9/128 on the 169,908 shipped entries. Asserted on the measured sum: the sum of D is not smaller than 142,165, which is 85% of that rate for 14 claws. The organizer run thus measures and asserts the F8 rate of the shipped entry of every key, the floor of the bracket in Section 7. The further keys that are trials through another mate are counted on this entry's 2,000 claws (22,346 keys per claw; on the same claws the 361,638 entries pass F8 at 25,103 per claw against 25,428 for the rate 9/128) and lie under the independent-mates model.
  - Replayed values, not premises of the claim: tail_F and tail_n. For every 16th F8-passing lane the hit-conditioned tail is stepped through rows 18-22 and its distance from the advice trail at rows 19-22 is taken; tail_F is the one-way analysis-of-variance F of that distance across the claws of the trial, on tail_n lanes. Both are asserted equal to the values above, as in 3aa063d1.
  - Local seed sets, run by this entry with the same program: 5 sets of 4 windows, 78 claws, 7,217 hits against 7298.1 expected (z = -0.95). One set has z = -2.32, two-sided probability 0.02 for one set and 0.12 for the 6 sets run, the organizer's included.
- `r39-tail-01..14`: unchanged.
- Run by this entry (tools, not in the package): the 200 planted equivalence cases of Section 3.3; 20,480 sampled claws; 8 full windows (Appendix A); the ratio measurement on 2,000 real F9 claws.
- No end-to-end collision has been executed by anyone. All experiments are component tests; the claimed time is far outside any run.

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

## Appendix B. Key dispersion per claw, organizer seeds (Section 11)
| trial | D: keys with the shipped entry in F8 | K: scaled hits | D / 128 | z |
|---|---:|---:|---:|---:|
| 0 | 11,910 | 81 | 93.0 | -1.25 |
| 0 | 12,948 | 97 | 101.2 | -0.41 |
| 0 | 10,913 | 79 | 85.3 | -0.68 |
| 0 | 17,490 | 139 | 136.6 | +0.20 |
| 0 | 13,496 | 113 | 105.4 | +0.74 |
| 1 | 14,241 | 107 | 111.3 | -0.41 |
| 1 | 9,563 | 72 | 74.7 | -0.31 |
| 1 | 12,212 | 117 | 95.4 | +2.22 |
| 2 | 11,526 | 85 | 90.0 | -0.53 |
| 2 | 9,367 | 58 | 73.2 | -1.78 |
| 2 | 8,623 | 76 | 67.4 | +1.06 |
| 2 | 12,558 | 98 | 98.1 | -0.01 |
| 3 | 16,510 | 132 | 129.0 | +0.27 |
| 3 | 8,374 | 65 | 65.4 | -0.05 |
| all | 169,731 | 1,319 | 1326.0 | -0.19 |
