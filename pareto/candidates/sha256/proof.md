# SHA-256 reduced to 39 steps: ordinary collision by the transplanted pair with two released state words (k = 4); the W17 condition solved on 18-bit prefixes by a generic counted pass

The list is Jbenisek's: this entry takes the 256-class k = 4 list of f92b8068 (821,520 entries, credited) in place of the 60-class list. The W17 pass and its accounting are ours, as accepted in 837b7139: one fixed routine over the distinct 18-bit prefixes of the list keys, every operation through the program's operation counter, a memory row for every k4 instruction. f92b8068 runs a folded per-key pass on this list; under the prefix pass the larger list costs 57,013 operations per F9 claw where the 60-class list cost 19,566, and gives 770.4 trials per distinct claw where it gave 343.1. The rest is the line of Jbenisek and dariolina's 3aa063d1: dariolina's W17-only pass (087bf8f8), newjordan's literal-add test (90d39efd), Jbenisek's k = 4 construction (293ca62c), sraiw's walk and tail replica (fce2f19e) and the advice pair of 5f8e6192. Against 837b7139 three things change: the recipe and its tables; the mates of a key hit, which are now the 4,096 submasks of the 12 free bits of a3; and the trial count, measured again on this list. The three claimed figures carry deliberate headroom over the program's own arithmetic (Sections 5 and 6); only the first hit of each window is counted (Section 7); the organizer experiment tests key dispersion on all keys of every F9 claw against an acceptance region the program asserts on the measured values (Section 11).

Labels: MEASURED = run by us with the shipped program's counters; DERIVED = arithmetic from stated numbers; CITED = measured and published by the named earlier entry, restated here with its sample size and its source.

## 1. Target and output
- **Target.** `sha256-r39-prefix-v1`: SHA-256 with the first 39 steps in every compression, standard IV, FIPS 180-4 padding, feed-forward, all 256 output bits.
- **Output.** Two distinct 128-byte messages M0 || M1 and M0 || M1': the same random first block M0, second blocks with M1' = M1 + DL (word-wise modular, differences in words 8..12). The lengths are equal, so the padding block is identical and equal chaining values after block 2 give equal digests. Ordinary collision, no chaining-value difference.
- **Claim.** time_log2 = 97.6124, memory_log2_bytes = 20.4378, preprocessing_log2 = 43, advice 2,013 bytes = 2^10.97514, success probability 0.39. The time is total charged work (work cap, one-time setup, 2^43 preprocessing) plus a stated headroom; the memory is the row sum 1,387,485 bytes plus a stated headroom of 32,768 bytes.

## 2. The construction (CITED from 293ca62c and 38912d66; identities re-checked by us)
**2.1 Advice.** A 39-step semi-free-start pair on the characteristic of ePrint 2026/1120 Tables 21 and 23: CV_PUB, MP_PUB = BW and M_PUB, 160 bytes, the pair of 5f8e6192. It collides from CV_PUB under 39 steps (checked: experiment r39-transplant-claw trial 0, and independently by our own 39-step implementation). Charged advice is 2,013 bytes: the pair and the 1,853-byte recipe of Section 2.5. The tables derived from the recipe are built at import (Section 4) and have memory rows (Section 6).

**2.2 The transplant, k = 4.** Indexing: A[0..3], E[0..3] are the chaining value and step r writes A[r+4], E[r+4]. Fix A[8..11], E[12..15] and W12..W15 to the values of MP_PUB. For any cv and any (a0, a1, a2, a3) = A[4..7], steps 0-7 determine W0..W7 and steps 8-11 determine W8..W11 (`k4_words`); the state after step 11 is then the advice state, so both messages follow the advice states through step 15 whenever the step-8..15 differences are the advice ones. Closed forms (expanded from the step equations; 0 mismatches in 3,500 random checks of our own implementation):
- W9 = C - a1 + h4(a2, a3), h4 = MAJ(A8, a3, a2) - CH(E12, E11, E10), E10 = a2 + t(a3), E11 = a3 + c11;
- W10 = kappa(a3) - a2; W11 depends on a3 only; W2 = a2 + c2(cv, a0, a1); W0 and W1 do not depend on (a2, a3).

**2.3 Row 16 is a claw.** W16 = s1(W14) + W9 + s0(W1) + W0. On the fibre h4(a2, a3) = h4(BA[6], BA[7]) = h0, W9 and W16 are those of the base, and W16 = g holds exactly when F(a0) = F(u), a0 even, u = W1 odd, for the 32-bit map F of the walk (`fstep`). Claws are found by the distinguished-point walk of fce2f19e, unchanged.

**2.4 What remains to pay after a claw.** Once per claw: W9 in F9 (density 65/4096). Per listed (a3, a2): W8 in F8 (density 9/128; depends on a0..a3); W10 in F10 and W11 in F11 (paid in the list); and W17 = s1(W15) + W10 + s0(W2) + W1 equal to the advice value. Then the tail, rows 18 to 38 (Section 8). With x = W2 the W17 condition is s0(x) - x = R with R depending on the claw and on kappa(a3) only (0 mismatches in 500 checks). **So two entries with the same a2 and the same kappa (equivalently the same W10) pass or fail W17 together in every claw.** They are called mates; they differ in a3, hence in W11, W3..W7, W8 and every tail word.

**2.5 The list and its keys (DERIVED and MEASURED; every count below was reproduced by our own enumeration, independent of the leader's program).**
- Classes: the list is the 256-class list of f92b8068. Its classes are a3 = BA[7] XOR a mask inside 12 bits of a3 (bits 1, 3, 4, 6, 7, 22, 23, 24, 28, 29, 30, 31, mask 0xF1C000DA): 4,096 masks. Our enumeration over all 4,096: 576 pass F11; 256 of those have solutions a2 of h4 = h0 (exact bit-serial search, 10,160,640 solutions); 869,616 solutions also pass F10; **821,520 of those, in 256 classes, keep the advice state-difference trail through step 15.** The sorted entry set has the sha256 of the list decoded by f92b8068's own program (`0ae6aff0...e5b9`). Classes by mask weight: 1 of weight 0, 7 of weight 1, 20 of weight 2, 32 of weight 3, 37 of weight 4, 41 of weight 5, 43 of weight 6, 35 of weight 7, 22 of weight 8, 12 of weight 9, 5 of weight 10, 1 of weight 11. The 60 classes of weight 3 or less are the list of 3aa063d1 and of 837b7139 (361,638 entries). For 837b7139 all 5,489 masks of weight 3 or less over the 32 bits of a3 were enumerated: they give these 60 classes and no other. Masks of higher weight outside the 12 bits were not searched by us.
- The trail verdict is a function of (a2, a3) only (argument of 293ca62c Section 2.5: a2 and a3 meet a difference only through CH at steps 9 and 10 and through D10, D11). We checked every entry at one point and 4,000 sampled entries at three points; verdicts never differed.
- Keys: the 821,520 entries have **324,324 distinct (a2, kappa) keys** in 72 kappa groups: 81,900 keys with 1 entry, 143,262 keys with 2 entries, 85,050 keys with 4 entries, 14,112 keys with 8 entries (mean 2.53 entries per key).
- Shipped recipe: 112 classes and one reject bit per F10-passing candidate, in decoder order (464,472 candidates). A candidate is rejected when it fails the trail or when its key is already listed by an earlier class. Every key of the 821,520-entry list is listed exactly once (asserted when the recipe is built: the key sets are equal). 1,853 zlib bytes (window 4,096), 2,317 base85 characters. The decoder is 3aa063d1's with three changes: its two inflate readers are opened with a 4,096-byte window, both are counted, and the sha256 self-check of the decoded list runs only in the experiment entry. Every import asserts the count 324,324.
- From the decoded list the program derives, once at import, the table the attack uses: for each of the 72 kappa groups, the distinct values of a2 mod 2^18 over the group's keys. There are **22,176 such prefixes in all, in 120 blocks of at most 256 lanes** (640 per group at most), stored as 18 bit planes per block.

## 3. The W17 pass
**3.1 The equation.** For a claw and a kappa group the W17 condition on a listed key is s0(y) = y + r (mod 2^32), with y = a2 + w, w = w2b of the claw and r = kd + W17 - u - w, where kd is the group constant and W17 the advice value (Section 2.4; s0 is the small sigma0 of SHA-256). Write k_i for the carries of y + r. Bit i of the equation reads y_i XOR r_i XOR k_i = y_(i+7 mod 32) XOR y_(i+18 mod 32) XOR y_(i+3), the last term absent for i >= 29.
- For i = 0..13 the equation gives y_(i+18) from bits already known. **So the low 18 bits of y determine the other 14.**
- For i = 14..31 the equation is a check: 18 checks.
- A solution of the W17 condition is therefore the unique completion of its low 18 bits, and those are (a2 + w) mod 2^18, a function of a2 mod 2^18 and the claw.

**3.2 The pass (`k4q`).** Lanes are the 22,176 prefixes of Section 2.5, 256 per word. Per evaluated F9 claw:
1. Spill and later restore 104 registers of the interrupted walk (2 x 104 x 3 = 624). Compute a1 and w (`k4x`, 55). Form the 18 constant words of w's low bits (3 each, 54).
2. Per group: loop control (4), loads of the group constant and of the block list (2 x 3), r (4), the 32 constant words of r (96): 110.
3. Per block: loop control (4); load of the lane count (3); the lane mask built from it (shift, subtract: 2); the lane counter update (2); load 18 planes and add w (138); run bits 0..31 of y + r with the 14 determinations and the 18 accumulated checks (250); mask and test (4). **403 operations, the same for every claw and every block.**
4. A lane that passes all 18 checks is a survivor. Its y is extracted and the candidate a2 = y - w is tested on scalar words against each shipped class of the group (same W9 as the base, W17 equal to the advice value, W10 in F10). Counted cost: 711 for the survivor (5 operations of the survivor loop, then 16 + 128 extraction + 2 + 560 for the base words) and 563 per class tested (3 for the class load, 560 for the candidate), so between 1,274 and 2,963.
5. A candidate that matches a class is a key hit. All 4,096 submasks of the 12 free bits of a3 are then enumerated, from the full mask down to zero: a mask with the same W9 and W17 is a mate, a mate with W8 in F8 is completed, both blocks are compressed and compared. Charge 560 per mask and 2 x 2,812 per compressed pair. Mates that fail the trail cost their charge and cannot produce a false output.

Every operation of steps 1 to 3 is a call of `Mach` (XOR, AND, OR, NOT, add, subtract, shift, load) or an explicit charge for loop control, a table load or the spill. There is no literal folding and no claw-dependent code: constants enter as words built by counted operations. The pass count is K4_PASS = 733 + sum over groups of (110 + 403 x blocks) = **57,013**, a formula of the table, evaluated in the program and asserted at import inside the cap constant.

**3.3 Why it finds exactly the same hits.** A listed key satisfies W17 in a claw if and only if its prefix lane survives and the scalar test accepts it: the pass enumerates every prefix of every group, the completion is unique, and the scalar test is the definition. MEASURED: on 200 planted cases (a real F9 claw, an entry drawn from the 821,520-entry list, the advice W17 replaced in memory by that entry's W17) the attack-path pass hit the key every time and compressed every listed mate of that key that passes F8 in that claw: 60 such mates, none missed. 99 of the 200 entries drawn lie in classes the recipe does not ship. The organizer experiment repeats a planted check for all 72 groups on the first F9 claw of each window (Section 11).

**3.4 Other changes to the program.** The decoder is that of 837b7139; the recipe is rebuilt for the 256-class list. The per-window flush of the list is gone: the list is decoded once, at import. The sha256 self-check of the decoded list runs only in the experiment entry; on the `--attack` path the import executes no hash (the count of decoded entries is still asserted). The register file is allocated at 256 words and the inflate readers are opened with a 4,096-byte window. The old per-key bit-sliced pass remains in the file only as a diagnostic of the experiment modes (it feeds the key-dispersion test of Section 11); the attack path (`--attack`, check and measure off) does not execute it. The participant-only wasm runner of the kernel generator is removed; the generator is charged at its halt cap, as it already was whenever the runner was absent. The attack is `r39joint_k4.py --attack`.

## 4. Machine model and where each activity is charged
A counted RAM of 256-bit words (collision-frontier-v5): load, store, add, subtract, AND, OR, XOR, NOT, shift, rotate, comparison and conditional branch are primitive operations; 2,812 operations are one 39-step compression. In `Mach` an operation is 1, a load or store 3 (index shift, base add, access) and a branch 2, the prices of the accepted base.

| activity | time charge | memory |
|---|---|---|
| walk kernel, generated per window with the first block's constants folded in | every generation is charged at the generator's halt cap, 575,000 operations, plus 8 per record for relocation; rejected first blocks are charged too (`window_setup`). CITED from the accepted walk | two images (7,100 B) and envelope; generator code inside the walk's instruction census |
| walk, distinguished points, stage 2, claw filters | executed through `Mach` | walk rows of Section 6 |
| dedupe gate of repeated F9 claws | 12 per lookup and 468 per stored key | dedupe rows |
| W17 pass | executed through `Mach`, plus explicit spill and loop charges (Section 3.2): 57,013 per evaluated claw | prefix planes, group table, save area, code |
| survivors and key hits | 711 + 563 per class; 560 per mask; 2 x 2,812 per pair (Section 3.2). 560 is a stated composite price for building one candidate's words and testing them; our count of that routine at the walk's prices is 422 | hit-path row, code |
| setup, once per run: inflate by both readers, candidate search, plane build, per-group prefix sets, sort, and every other statement the import executes (constants, advice trajectories, condition tables, base85 decode) | K4_SETUP = 1,281,422,913 operations, asserted in the program, emitted by the experiment and added to the claimed time: the counted decode of 3aa063d1's decoder with inflate at 1,024 operations per raw byte of either reader (their counted figure is 36.351), 256 per accepted lane, 256 per prefix, and 2^30 for everything else the import executes. The 2^30 also covers the decoder's candidate search at this proof's own prices: an operation trace of the import of 837b7139 put that search above 111 million operations for the 60-class recipe, where the decoder's own counters charged about 30 million; this recipe has 464,472 candidates, 1.84 times as many, which scales the trace to about 204 million, about a fifth of the 2^30 | setup rows |
| advice construction and selection | 2^43 compressions, added to the claimed time; the sum behind it is in Section 9 | within the walk arena: the selection peaks at 65,536 bytes (Section 9) |
| folded or claw-specialised code | none exists in this entry outside the walk kernel above | |

## 5. The ledger
| term | value | status |
|---|---|---|
| base walk per window, 99% upper bound | 463,618,904 ops (24 windows: mean 461,649,658, s.d. 3,858,918) | CITED; our 8 full windows (seeds 1000-1007) reproduce the leader's per-window base ops and F9-claw counts exactly |
| arrival-order index | at most 718,848 ops per window | CITED (1,536 keys x 468) |
| distinct groups per window | 58,959.42 | CITED |
| evaluated F9 claws per distinct claw | 0.016203 (99% upper bound over 48 windows; mean 0.015997) | CITED |
| W17 pass per evaluated F9 claw | **57,013**, exact and the same for every claw | DERIVED from the table; MEASURED: 18,932 of 20,480 sampled claws were free of survivors and each counted exactly this; all 7,511 evaluated claws of our 8 full windows fit the formula |
| survivors per evaluated claw | at most 0.08460 (the uniform rate; the sample lies under it: one-sided 99% bound (S + 2.326 x sqrt(S) + 2) / n = 0.08417 from S = 1,628 survivors in n = 20,480 sampled claws; uniform model 22,176 x 2^-18 = 0.08459; our windows: 607 in 7,511 claws) | MEASURED |
| survivor work per evaluated claw | 251 (rate bound x 2,963, rounded up) | DERIVED |
| key-hit work per evaluated claw | 2,740 (expected: 464,472 candidates x 2^-32 x 25,329,680, every mask priced as a compressed pair; the candidates are the F10-passing solutions of the shipped classes, a superset of the 324,324 keys) | DERIVED |
| ops per distinct claw, raw | 8847.80 (rounded up) = 464,337,752 / 58,959.42 + (57,013 + 2,991) x 0.016203 | DERIVED |
| **ops per distinct claw, K** | **8,937** = ceil(1.01 x raw): 1.01% deliberate headroom | the program asserts K >= 1.01 x raw at import |
| W17 trials per distinct claw | **770.4**, the one-sided 99% lower bound of our own direct measurement (Section 7) | MEASURED |
| tail | **2^-74.54, the declared bound of the shipped replica** | Section 8 |
| windows B | 2^80.094710 (rounded up) | `k4_budget` |
| work cap | 2^97.610339 compressions (rounded up) | B x K x 58,959.42 / 2,812 |
| one-time setup and preprocessing | 1,281,422,913 / 2,812 + 2^43 compressions | Section 4 |
| total charged work | 2^97.610339 compressions (rounded up) | cap + setup + preprocessing |
| **time, claimed** | **97.6124** | at least 0.002 bit above the line above (asserted at import) |

**Headroom is deliberate.** K is at least 1 percent above its formula, the claimed time is at least 0.002 bit above the program's total, and the claimed memory is 32,768 bytes above the row sum. It is a margin against slips of arithmetic and counting; nothing in this proof is paid for out of it.

**Tail pricing.** This entry prices the tail at the declared bound 2^-74.54. At the 14-run mean 2^-74.3238, which 3aa063d1 uses, the same program and K would give 97.3962; that figure is not claimed.

For comparison, 165eb217 charged a folded pass at 167,471 and a flush of 34,322,747 per window (K = 11,193) with forming the fold left out. The pass of this entry costs 57,013 with every operation counted, and there is no flush.

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
| prefix table K4_Q: 120 blocks x 18 planes x 32 B, plus lane counts, group constants, class words, sample keys | 70,912 | resident |
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
| recipe W3_LIT, decoded bytes object | 1,853 | resident |
| recipe, base85 text of the same literal | 2,317 | resident |
| fold literals K4_BLOCK_CONST and K4_CLASS_CONST (audit) | 11,896 | resident |
| all other module-level data left by import (audit; largest: BY_BIT_16_17, CONDS_16_17, p, _W18_HIST) | 15,691 | resident |
| setup: three decoder blocks of 32 words (under construction, transposition copy, consumer) | 3,072 | setup |
| setup: decoder sigma0 tables, 4 x 256 x 4 B | 4,096 | setup |
| setup: decoder work lists, 448 low halves, and 560 high halves held twice, 4 B each | 6,272 | setup |
| setup: decoder search stack, at most 13 entries x 16 B | 208 | setup |
| setup: two inflate readers opened with a 4,096-byte window: window 4,096 + state 7,500 each | 23,192 | setup |
| setup: reader input and output steps, 4 x 64 B, and scalars | 320 | setup |
| setup: prefix sets of at most two kappa groups at a time, 2 x 640 x 4 B, and their class sets | 5,176 | setup |
| setup: sorted copy of one group (640 x 4 B), one slice (256 x 4 B), one block of planes | 4,160 | setup |
| k4 code, 3,179 instructions x 36 B (convention below) | 114,444 | resident |
| **row sum** | **1,387,485 = 2^20.4040** | |

- **Claimed: memory_log2_bytes = 20.4378, which is the row sum plus 32,768 bytes of deliberate headroom (1,420,253 bytes), rounded up.**
- **How the table was made.** Element counts come from an audit of the shipped source: every module-level object left by the `--attack` import, every attribute of the attack object after a window, and every growth site were listed and sized. Element widths are the machine model's: 32 bytes for a 256-bit word, 4 for a scalar or 32-bit word, 5 for a walk-kernel record, 1 per byte of text. Rows marked setup are live only during import and are summed with the rest.
- **Walk rows.** Checked against the allocations of the source: table 26,052 words (`table_words`), queue 897 words, wheel 128 words, lanes 256 words, save 32 words, register file 256 words (`s.R`), two images of at most 710 records (`KCAP`). Four small rows (constants and counters, free stack, parked scalars, pair records) and the 4,111-instruction census (1,246 executed-block, 1,100 routine, 1,765 generator and relocation) are CITED from 9993eaa8 Section 6 and not recounted by us; the two audit rows for attack-state scalars and other module data are added on top of them.
- **Growth sites.** The dedupe table stops storing at 1,536 keys (in code). The output lists receive entries only on a collision, which ends the run. The per-group prefix sets exist during import only. The statistics dictionary has a fixed set of keys.
- **Code.** Every k4 instruction has a row, at 36 bytes, the walk's own price for a general instruction. Count: one instruction per syntactic operation of the source of every k4 routine, the experiment-only diagnostic routines included (`_w3gen`, `_k4class`, `_k4new`, `_k4acc`, `_k4tr`, `k4_x`, `k4_eval`, `k4x`, `k4f`, `k4p`, `k4q`, `k4d`, `k4_budget`, `k4_words`, `k4_second`, `K4BS`, `inF`, `_k4fin`, `_sm`, and the experiment's list cache `_k4c1`: 1,333); the W17 pass a second time in looped machine form, one instruction per counted operation of one block, one group prologue and the claw prologue (403 + 110 + 733 = 1,246); and 600 for an inflate reader. 3,179 instructions, 114,444 bytes. The count is a convention of ours and is deliberately on the high side.
- **Walk-kernel generator.** Its working memory is measured at allocated size: the generator was run as `window_setup` runs it on 300 chaining values and the largest element counts were taken (781 graph records, 11,491 characters of generated text). One generation is live at a time. `--attack` releases the previous attack object before it builds the next.
- **What the table covers.** All memory the `--attack` path allocates, setup included, and all k4 code, whichever path runs it. The experiment entry allocates, on top of that, the statistics containers and plane chunks of its diagnostics; the `--attack` path never allocates them, and they are the experiments' memory, listed nowhere in this table.

## 7. Success probability and the cap
- lambda = B x 58,959.42 x 770.4 x 2^-32 x p_tail with p_tail = 2^-74.54, set to (-ln(0.61) + 2^-40) / (1 - 0.00564) by `k4_budget` (the divisor is explained below); B = 2^80.094710 windows. The run stops at B windows or at the work cap.
- **Trials.** A trial is a key with at least one valid mate passing F8, in a claw passing F9. When such a key hits W17 the program tests every mate, so the key succeeds with probability at least p_tail, whatever the dependence between the tails of its mates. No within-key independence is used; that is the pricing 3aa063d1 calls the worst case, and it is realised here without evaluating any key twice. What the count uses of independence is premise H5 (Section 10) and is set out below.
- **Count of trials: 770.4 per distinct claw, from our own measurement.** On 2,000 real F9 claws (8 batches of 250 from 8 full windows) the number of distinct listed keys with a valid mate in F8 is 49912.594 per evaluated F9 claw (s.e. 191.337). The 8 windows have 938.875 distinct F9 claws each on average (s.e. 8.909). Their product divided by the 58,959.42 groups per window is 794.813 trials per distinct claw (s.e. 8.134, from the two relative errors). Its one-sided 99% lower bound, estimate - 2.998 x s.e. with t(7) = 2.998, is 770.426, priced as 770.4. For comparison only: f92b8068 prices 789.304 for this list, from 48 full windows and its own estimator; that figure is not used here.
- **The trial count in a bracket.** Each figure is a number of keys per F9 claw, times 938.875 F9 claws per window, divided by 58,959.42. Floor, 357.3: the organizer run counts on its 14 claws the keys whose shipped entry passes F8, 22,439 per claw (the rate 9/128 on 324,324 keys gives 22,804), and asserts a floor for their sum (Section 11). Priced, 770.4. Measured, 794.813: on 2,000 claws, 49,913 keys per claw have a listed entry in F8, the shipped one or a mate. Independent-mates model, 843.1: if every listed entry passed F8 at 9/128 independently, the key multiplicities of the list (81,900 keys with 1, 143,262 keys with 2, 85,050 keys with 4, 14,112 keys with 8) would give 52,947 keys per claw. The priced figure is 3.1% under the measurement and 8.6% under the model. The measurement is under the model because the mates of one key pass F8 together more often than independent entries would. The floor is what the organizer run observes on its own claws; the 413.1 trials between the floor and the price are keys that are trials through a mate, counted on the 2,000 claws.
- **The cap does not bind before B windows (H6).** Work per window = base walk + index + D x (pass + survivors + key hits), D the distinct evaluated F9 claws; the pass is a constant. The random inputs are known from samples, so each sample moment is replaced by its one-sided upper confidence bound at level 99.75%, which makes the four bounds hold together at 99% (Bonferroni). Samples: base walk, 24 full windows of this walk (3aa063d1 Appendix C: mean 461,649,658, s.d. 3,858,918; the 8 windows re-run here are 8 of those seeds and reproduce their values, Appendix A); D, 48 full windows (3aa063d1 H1-ops: mean 944.60, s.d. 35.37; our 8 windows: mean 938.875, s.d. 25.20). Mean bounds, mean + t x s.d. / sqrt(n) with t(23) = 3.104 and t(47) = 2.946: 464,094,674 and 959.64. S.d. bounds, s.d. x sqrt((n - 1) / q) with q the 0.25% quantile of chi-square, 8.450 on 23 and 24.316 on 47 degrees of freedom: 6,366,506 and 49.18. Both are the normal-theory intervals. Mean work: 464,094,674 + 718,848 + 959.64 x 60,004 = 522,395,761 per window, against the cap 8,937 x 58,959.42 = 526,920,336: margin 4,524,575, 0.85% of the cap. Per-window s.d. at most 17,504,920: 6,366,506 for the walk, plus 49.18 x 60,004 for D, plus 26,698 for the number of survivors and 8,160,719 for the rare key hit (25,329,680 operations with probability 0.1038 per window), summed with no independence assumed between the parts. For independent windows Chebyshev's inequality bounds the probability that the cap binds before B windows below 1.2e-23. At the sample moments themselves the margin is 1.49% of the cap. The organizer's four windows reproduce 3aa063d1's operation counts on the same seeds to the unit once the counted k4 operations are subtracted (hard-asserted, Section 11), so the cited samples are samples of the walk the organizer ran. The cap exceeds the sample mean of the work by 7.19 combined standard errors (1,094,032 operations: 3,858,918 / sqrt(24) for the walk plus 35.37 / sqrt(48) x 60,004 for D), and the Chebyshev figure leaves room for a far larger s.d.
- **The success count uses three things, and no more.** (i) Windows are independent: each has a fresh first block. (ii) A hit is a trial key whose W17 equals the advice value. A window has H hits; E[H] is the mean number of trials of a window times 2^-32, and with 770.4 trials per distinct claw or more, E[H] is 58,959.42 x 770.4 x 2^-32 or more. (iii) Only the first hit of a window is counted. It succeeds with probability p_tail, and a window has a hit with probability E[H] - E[H(H-1)]/2 or more. Given the claws, the W17 events of distinct keys are independent (tested at a scaled event, Section 11), so E[H(H-1)] is E[H]^2 x (1 + c^2), c being the relative spread of the trial count of a window: 2.8% measured (per-claw s.d. 9,167 on 49,913 keys over 939 claws, and 2.7% for the number of claws), which makes the factor 1.002 or less. E[H] is 58,959.42 x 819.20 x 2^-32 = 0.01125 at its upper value (819.20 is the upper one-sided 99% bound of the trial count, 794.813 + 2.998 x 8.134), so the second term takes 1.002 x 0.01125 / 2 = 0.564% of the first. Hence a window succeeds with probability p_tail x 58,959.42 x 770.4 x 2^-32 x (1 - 0.00564) or more, and over B independent windows P(no success) is exp(-lambda x (1 - 0.00564)) or less. `k4_budget` sets lambda = (-ln(0.61) + 2^-40) / (1 - 0.00564), so the success probability is 0.39 or more. Counting first hits only costs 0.0082 bit of time. No independence between the tails of different hits is used, inside a claw or inside a window.
- A window with more than 1,536 distinct F9 claws evaluates the excess without storing it (the gate never fails; a repeated claw then costs a second pass, inside the same per-claw charge); our 8 windows had at most 979. The dedupe lookup is priced at 12 operations, the price of the base (CITED).

## 8. The tail (replica of 5f8e6192, run by the organizer; priced at the declared bound)
- `experiments/r39tail.py` is the replica of 5f8e6192 with one constant changed, the declared value QDECL, run by the organizer as r39-tail-01..14. It hard-asserts: 6,398 verified collisions in 45,875,200 proposals; linear mean 2^-74.3238; one-sided 99% bound 2^-74.3978; 99.9% bound 2^-74.4326; and that both bounds exceed the declared QDECL = -74.54.
- **This entry prices the tail at 2^-74.54.** The declared bound rests on 42 further runs of the shipped replica, 3,276,800 proposals each, none of them used to choose the advice pair: 28 under the organizer's seed protocol on the experiment ids r39-tail-15 to r39-tail-42, and 14 on local seeds (trial i of run Lnn has the seed sha256 of the text `tail_fibre|Lnn|i`). Three of the 28 were run again for this package and returned the same bytes. The declared value lies 0.0104 bit under the one-sided 99.9% bound of the 42 runs and under the mean of each set of 14.

| runs of the replica | verified collisions | mean | one-sided 99% bound | one-sided 99.9% bound |
|---|---:|---:|---:|---:|
| r39-tail-15..28, organizer seed protocol | 6,222 | 2^-74.4242 | 2^-74.5159 | 2^-74.5594 |
| r39-tail-29..42, organizer seed protocol | 6,184 | 2^-74.3865 | 2^-74.5404 | 2^-74.6160 |
| L01..L14, local seeds | 6,205 | 2^-74.5230 | 2^-74.6091 | 2^-74.6498 |
| the 42 runs together | 18,611 | 2^-74.4434 | 2^-74.5061 | 2^-74.5296 |
| r39-tail-01..14, the runs the organizer executes (asserted by the replica) | 6,398 | 2^-74.3238 | 2^-74.3978 | 2^-74.4326 |

- Each run gives 2^l2 x hits / 3,276,800, the linear-scale estimator of the replica; the bounds are Student t on the run values (42 runs: t = 2.421 and 3.301; 14 runs: t = 2.650 and 3.852). 3aa063d1 and f92b8068 price the tail at the mean of r39-tail-01..14, 2^-74.3238. Among the 42 runs, the 14 on local seeds have a lower mean than the 28 under the organizer's seed protocol (Welch t = -2.62 on the run values); the declared value rests on the one-sided 99.9% bound of all 42 runs pooled.
- The replica draws W8 in F8 and W9 in F9 on the advice values of W10, W11. For k = 4 variants W10, W11 and W3..W7 differ; 3aa063d1 measured the transfer with a joint arm on 60,000 real variant triples, 14 runs: ratio 2^+0.023 (s.d. 0.026). CITED (3aa063d1 H5).

## 9. Advice construction and preprocessing (H3)
The advice pair is the pair of 5f8e6192, chosen among 93 candidate pairs. The accounting is that of 9993eaa8 Section 11, in the form of sraiw's 38912d66 Section 4.2, restated here in full. Its two executed components run in this package's organizer experiment `r39-transplant-claw`.
- **One pair.** Steps 10 to 15 carry 12 state words, 384 bits, under the 350 bit, carry and message-schedule conditions of the Table 23 characteristic: 2^(384 - 350) = 2^34 candidate dense parts. Given steps 10 to 15 and W0..W15, steps 9 down to 0 and the chaining value follow by inverting the step function, with no search (`invert_downward`; the experiment asserts downward_inv_ok = 1). Each candidate is tested for non-empty row-16 and row-17 fibres by an exact bit-by-bit search (`solve_row_exact`). The experiment runs that search on the shipped pair (g16_fibre_size = 2, g17_fibre_size = 1, fibre_dfs_ops = 1,944 word operations) and enumerates a 256-candidate slice of the step-15 free bits (advice_slice_cands = 256, advice_slice_hits = 1, ops_per_cand = 411 word operations). 411 word operations are 0.146 compressions; the charge per candidate is 4 compressions, 27 times that. One pair: 2^34 x 2^2 = 2^36 compressions. The source paper measures about 2^34.2 SHA-256 calls for the same step (ePrint 2026/1120 Section 4.3, Step 1; its Step 2 holds with probability 1).
- **Selection.** 93 pairs were constructed and screened by the tail measurement, one after another. Constructions: 93 x 2^36 = 2^42.5392. Screens: each is charged as the full 14-run design of Section 8. One run is 3,276,800 proposals of two 39-step compressions (2^22.64) plus 800 particles x 38,916 stage lanes of 3 steps each (2^21.2), inside 2^24 compressions; 93 x 14 x 2^24 = 2^34.35. Sum: 2^42.545 compressions.
- **Declared: preprocessing_log2 = 43**, which is 2^0.455 times the sum. The 2^43 is added to the claimed time (Section 5), where it is a 2^-54.6 part of the total.
- **Memory of the selection.** It is sequential. One construction holds one candidate path, 65,536 bytes; one tail run holds 62,144 bytes (table of 9993eaa8 Section 11). Both fit the walk arena of Section 6.
- **The list** costs about 2^33.3 operations to enumerate offline (Section 2.5). The attack rebuilds what it needs at import, inside K4_SETUP.
- **Scale of the evidence.** Executed in the organizer run: the fibre search on one pair and 256 of the 2^34 candidates. The 2^34 is the dimension count above. The 93-pair campaign was run by the authors of the pair and is charged at its full declared cost.

## 10. Premises, and the limits of their evidence
- **H1-claw-model.** First-block chaining values behave as independent uniform values for the walk and the later events; W17 is uniform over claws and keys at the 2^-32 scale, and survivors of the pass per evaluated claw are at most the uniform rate, 22,176 x 2^-18 (the sampled count is in the ledger of Section 5). Walk work and yield per window as in Section 5 (CITED measurements).
- **H1-ops.** The constants of Section 5. The pass is a constant of the program, not a premise.
- **H2-tail.** p_tail >= 2^-74.54 for a valid entry passing F8 in a claw passing F9 with W17 hit (Section 8).
- **H3-advice-construction.** Constructing and selecting the advice pair costs 2^42.545 compressions by the accounting of Section 9, declared as 2^43 and added to the claimed time; the list costs about 2^33.3 operations to enumerate offline.
- **H5-group-independence.** Windows are independent. The trials of a claw are its keys with a valid mate in F8; their number is a property of the claw and varies between claws (Appendix B), and the count uses its mean, 770.4 per distinct claw or more (bracket in Section 7). Given the claws of a window, the W17 events of distinct keys are independent with probability 2^-32 each. Only the first hit of each window is counted (Section 7). Evidence: the trial count is measured on 2,000 real F9 claws of 8 full windows; the organizer run measures on its own 14 claws the F8 rate of the shipped entries and the dispersion of scaled key hits (Section 11).
- **H6-cap-completion.** Section 7: the four sample moments at joint 99% upper confidence bounds, then Chebyshev.
- **H-implicit-distinct-key-dispersion.** Given the claws, W17 events of distinct keys are dispersed as independent trials: tested in the organizer run at a scaled event over all keys of 14 claws, against an acceptance region the program asserts on the measured sums (Section 11).
- **Limits of the evidence.** The walk and F9 samples are 24 and 48 full windows on public seeds, and their confidence bounds are normal-theory intervals. The trial count is measured on this entry's 2,000 claws; the organizer's 14 claws measure the F8 rate of the shipped entries (6.92% against 9/128 = 7.03%), the floor of the bracket in Section 7. The dispersion test runs at probability 2^-7; the attack's event has probability 2^-32 on the same keys and the same words. The tail replica samples the advice values of W10 and W11, and its transfer to the variants is the 14-run joint arm of 3aa063d1, measured on variants of the 60 classes of weight at most 3; the classes of higher weight differ from them in the same 12 bits of a3. The memory peak uses the generator's largest allocation over 300 chaining values. No full collision has been executed: every experiment is a component test, and the claimed time is far outside any run.

## 11. Experiments (organizer sandbox; every organizer-run value is hard-asserted by the program)
- `r39-transplant-claw`: advice collision, fibres, downward inversion and the 256-candidate slice of Section 9, 255 transplant identities.
- `r39k4-window-small`, trials 0-3: windows of 2^21 evaluations on the organizer seeds, check mode, k4 on for every F9 claw of the window (5, 3, 4 and 2 claws, 14 in all). The counted pass runs in full on each: all 22,176 lanes. Asserted tuples (claws, F9, F8F9, pass lanes, survivors, key hits, k4 ops, total ops): (221,5,0,110880,0,0,287465,10779082), (215,3,0,66528,0,0,172479,10634043), (226,4,1,88704,1,0,231246,15709202), (205,2,0,44352,0,0,114986,11169734). Each k4 ops value is F9 x (57,013 + 480): one full pass and one dedupe-gate charge per F9 claw, to the operation. Trial 2 has one real survivor of the pass; its counted cost, 1,274 = 711 + 563 x 1, is in the value of that trial. Each trial also emits k4_setup = 1,281,422,913, the setup constant of the program.
  - Pass-off control: trials 0 and 1 are re-run with k4 off; claws, F9 and F8F9 are equal and ops_off = ops - k4_ops = 10,491,617, 10,461,564. In trials 2 and 3 the asserted total ops less the asserted k4 ops are 15,477,956 and 11,054,748. All four are the values of 3aa063d1 on the same seeds: the pass adds exactly its counted operations and changes nothing else.
  - Planted check, on the first F9 claw of each window and for each of the 72 groups: a listed key of the group is taken, its W17 in this claw is computed on scalar words, and the pass is run on that group with that value as target; the program asserts that the key is found and that the counted cost of that run is the group's pass cost plus 711 per survivor plus a multiple of 563 between one and the group's class count per survivor. 288 planted keys per run, so survivors are costed under the counter in the organizer run. A survivor is always asserted to satisfy s0(y) = y + r on scalar words.
  - Key dispersion (H-implicit-distinct-key-dispersion), from the per-key pass run with the operation counter restored afterwards, on all 1,319 of its blocks: every one of the 324,324 keys, in every F9 claw. Per claw, D is the number of keys whose shipped entry passes F8, and K the number of those whose W17, multiplied by 2654435761 mod 2^32, has its top 7 bits zero. That event has probability 2^-7; it is the attack's event with its single target scaled up. Under independent key events K is Binomial(D, 2^-7) in each claw. Acceptance region, fixed in the manifest and asserted by the program on the sums it measures over the four trials: the sum of K within 2.576 standard deviations of the sum of D / 128, and the Pearson sum over claws smaller than 29.14, the 99% quantile of chi-square on 14 degrees of freedom. Asserted per trial, (sum D, sum K, Pearson, claws): (123,763, 991, 6.8763, 5), (67,657, 503, 2.2271, 3), (79,806, 634, 1.9812, 4), (42,919, 334, 0.4056, 2). Pooled: 314,145 key events, 2,462 hits against 2,454.3 expected (z = +0.16), Pearson 11.49. No claw of the 14 lies beyond two standard deviations (largest |z| = 1.45). See Appendix B.
  - F8 rate (H5): the same pass gives D, 22,439 per claw on average against 22,804 for the rate 9/128 on the 324,324 shipped entries. Asserted on the measured sum: the sum of D is not smaller than 271,367, which is 85% of that rate for 14 claws. The organizer run thus measures and asserts the F8 rate of the shipped entry of every key, the floor of the bracket in Section 7. The further keys that are trials through another mate are counted on this entry's 2,000 claws (49,913 keys per claw; on the same claws the 821,520 entries pass F8 at 57,343 per claw against 57,763 for the rate 9/128) and lie under the independent-mates model.
  - Local seed sets, run by this entry with the same program and the same code path: 11 sets of 4 windows fixed before any run, 149 claws, 27,087 hits against 27,080.0 expected (z = +0.04), Pearson 124.18 on 149 degrees of freedom. The largest set value is z = -1.37.
- `r39-tail-01..14`: the replica with QDECL = -74.54; its tables and asserts are those of 5f8e6192.
- Run by this entry (tools, not in the package): the 200 planted equivalence cases of Section 3.3; 20,480 sampled claws; 8 full windows (Appendix A); the ratio measurement on 2,000 real F9 claws.
- No end-to-end collision has been executed by anyone. All experiments are component tests; the claimed time is far outside any run.

## Appendix A. Our full windows of this program (2^26 evaluations, attack path, seeds as in 3aa063d1 Appendix C)
| seed | base ops | F9 claws, raw | distinct F9 claws | k4 ops | survivors | key hits | survivor work |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1000 | 459,242,401 | 1,118 | 970 | 55,914,279 | 81 | 0 | 144,293 |
| 1001 | 460,716,162 | 1,090 | 947 | 54,580,443 | 76 | 0 | 132,856 |
| 1002 | 460,526,883 | 1,120 | 936 | 53,947,238 | 75 | 0 | 131,582 |
| 1003 | 462,769,365 | 1,071 | 914 | 52,696,735 | 79 | 0 | 146,249 |
| 1004 | 466,593,739 | 1,157 | 979 | 56,449,143 | 86 | 0 | 161,360 |
| 1005 | 461,132,561 | 1,088 | 935 | 53,903,892 | 78 | 0 | 146,101 |
| 1006 | 463,895,626 | 1,102 | 918 | 52,905,254 | 65 | 0 | 124,472 |
| 1007 | 463,168,827 | 1,057 | 912 | 52,553,368 | 67 | 0 | 118,012 |

Base ops plus 12 per raw F9 lookup equal 3aa063d1's Appendix C values for the same seeds, and the distinct F9 counts are equal, in all 8 windows. Survivor work is k4 ops less 12 per raw lookup, less (468 + 57,013) per distinct claw, less 4,096 x 560 per key hit; it is 711 per survivor plus a multiple of 563, between 1,274 and 2,963 per survivor, in every window. A key hit here is a candidate accepted by a class test; none led to a collision.

## Appendix B. Key dispersion per claw, organizer seeds (Section 11)
| trial | D: keys with the shipped entry in F8 | K: scaled hits | D / 128 | z |
|---|---:|---:|---:|---:|
| 0 | 21,374 | 149 | 167.0 | -1.40 |
| 0 | 20,667 | 152 | 161.5 | -0.75 |
| 0 | 30,276 | 251 | 236.5 | +0.94 |
| 0 | 26,648 | 229 | 208.2 | +1.45 |
| 0 | 24,798 | 210 | 193.7 | +1.17 |
| 1 | 24,522 | 192 | 191.6 | +0.03 |
| 1 | 26,905 | 198 | 210.2 | -0.84 |
| 1 | 16,230 | 113 | 126.8 | -1.23 |
| 2 | 21,078 | 180 | 164.7 | +1.20 |
| 2 | 17,884 | 144 | 139.7 | +0.36 |
| 2 | 18,634 | 138 | 145.6 | -0.63 |
| 2 | 22,210 | 172 | 173.5 | -0.12 |
| 3 | 27,313 | 207 | 213.4 | -0.44 |
| 3 | 15,606 | 127 | 121.9 | +0.46 |
| all | 314,145 | 2,462 | 2454.3 | +0.16 |
