# SHA-256 reduced to 39 steps: ordinary collision by the transplanted pair with two released state words (k = 4), each W17 test run once per key

A credited derivative of Jbenisek and dariolina's 3aa063d1 (Pareto 99.4290), built on dariolina's W17-only pass (087bf8f8), newjordan's literal-add test (90d39efd), Jbenisek's k = 4 construction (293ca62c), sraiw's walk and tail replica (fce2f19e) and the advice pair of 5f8e6192. One idea is added: two list entries with the same a2 and the same W10 run the identical W17 test, so the list is shipped with one representative per (a2, W10) key, 169,908 keys in place of 361,638 entries, and a key that hits is expanded to its mates at scalar cost. Pricing follows 3aa063d1 and 30714e48: the tail at the 14-run measured mean with the declared bound stated beside it, and the pass at the sampled maximum of the 4,096-claw protocol, used as an allowance inside a work budget. The deterministic upper bound of a pass is also computed and stated, and is larger. Memory counts data and literals row by row; instruction bytes of the k4 routines are not counted, as in every entry of this line, and Section 6 says what they would add.

Labels used below: MEASURED = run by us with the shipped program's counters; DERIVED = arithmetic from stated numbers; INHERITED = taken from 3aa063d1 or its bases and not re-measured at scale by us.

## 1. Target and output
- **Target.** `sha256-r39-prefix-v1`: SHA-256 with the first 39 steps in every compression, standard IV, FIPS 180-4 padding, feed-forward, all 256 output bits.
- **Output.** Two distinct 128-byte messages M0 || M1 and M0 || M1': the same random first block M0, second blocks with M1' = M1 + DL (word-wise modular, differences in words 8..12). The lengths are equal, so the padding block is identical and equal chaining values after block 2 give equal digests. Ordinary collision, no chaining-value difference.
- **Claim.** time_log2 = 98.8153, memory_log2_bytes = 20.1233 (1,142,084 bytes), preprocessing_log2 = 43, advice 1,796 bytes = 2^10.81058, success probability 0.39. Normalised score 98.9386.

## 2. The construction (INHERITED from 293ca62c and 38912d66; identities re-checked by us)
**2.1 Advice.** A 39-step semi-free-start pair on the characteristic of ePrint 2026/1120 Tables 21 and 23: CV_PUB, MP_PUB = BW and M_PUB, 160 bytes, the pair of 5f8e6192. It collides from CV_PUB under 39 steps (checked: experiment r39-transplant-claw trial 0, and independently by our own 39-step implementation). Charged advice is 1,796 bytes: the pair, the 1,184-byte recipe of Section 2.5 and 452 bytes of class literals.

**2.2 The transplant, k = 4.** Indexing: A[0..3], E[0..3] are the chaining value and step r writes A[r+4], E[r+4]. Fix A[8..11], E[12..15] and W12..W15 to the values of MP_PUB. For any cv and any (a0, a1, a2, a3) = A[4..7], steps 0-7 determine W0..W7 and steps 8-11 determine W8..W11 (`k4_words`); the state after step 11 is then the advice state, so both messages follow the advice states through step 15 whenever the step-8..15 differences are the advice ones. Closed forms (expanded from the step equations; 0 mismatches in 3,500 random checks of our own implementation):
- W9 = C - a1 + h4(a2, a3), h4 = MAJ(A8, a3, a2) - CH(E12, E11, E10), E10 = a2 + t(a3), E11 = a3 + c11;
- W10 = kappa(a3) - a2; W11 depends on a3 only; W2 = a2 + c2(cv, a0, a1); W0 and W1 do not depend on (a2, a3).

**2.3 Row 16 is a claw.** W16 = s1(W14) + W9 + s0(W1) + W0. On the fibre h4(a2, a3) = h4(BA[6], BA[7]) = h0, W9 and W16 are those of the base, and W16 = g holds exactly when F(a0) = F(u), a0 even, u = W1 odd, for the 32-bit map F of the walk (`fstep`). Claws are found by the distinguished-point walk of fce2f19e, unchanged.

**2.4 What remains to pay after a claw.** Once per claw: W9 in F9 (density 65/4096). Per listed (a3, a2): W8 in F8 (density 9/128; depends on a0..a3); W10 in F10 and W11 in F11 (paid in the list); and W17 = s1(W15) + W10 + s0(W2) + W1 equal to the advice value. Then the tail, rows 18 to 38 (Section 8). With x = W2 the W17 condition is s0(x) - x = R with R depending on the claw and on kappa(a3) only (0 mismatches in 500 checks). **So two entries with the same a2 and the same kappa (equivalently the same W10) pass or fail W17 together in every claw.** They are called mates; they differ in a3, hence in W11, W3..W7, W8 and every tail word.

**2.5 The list and its keys (DERIVED and MEASURED; every count below was reproduced by our own enumeration, independent of the leader's program).**
- Classes: a3 = BA[7] XOR a mask of weight at most 3: 5,489 values. 204 pass F11; 61 of those have solutions a2 of h4 = h0 (exact bit-serial search, 4,672,448 solutions); 386,788 solutions also pass F10; **361,638 of those, in 60 classes, keep the advice state-difference trail through step 15.** This is the list of 3aa063d1 (our decoder reproduces its sha256 `51ebea4a...8f5a`). The counts 179,844 and 165,662 quoted in earlier proofs of this line are the same quantities for masks of weight at most 2 (28 classes); the 115,010 list was the 13 largest of those classes.
- The trail verdict is a function of (a2, a3) only (argument of 293ca62c Section 2.5: a2 and a3 meet a difference only through CH at steps 9 and 10 and through D10, D11). We checked every entry at one point and the weight-2 entries at three points; verdicts never differed.
- Keys: the 361,638 entries have **169,908 distinct (a2, kappa) keys** in 21 kappa groups (mean 2.13 entries per key).
- Shipped recipe: 35 classes and one reject bit per F10-passing candidate, in decoder order (252,276 candidates). A candidate is rejected when it fails the trail or when its key is already listed by an earlier class. Every key of the 361,638-entry list is listed exactly once (asserted when the recipe is built: the key sets are equal). 1,184 zlib bytes (window 4,096), 1,480 base85 characters. The decoder of 3aa063d1 is unchanged; it asserts the count 169,908 and the sha256 of the decoded list at import.
- Blocks: 682 blocks of at most 256 lanes in 42 (class, chunk) groups of at most 28 blocks.

## 3. The program
`experiments/r39joint_k4.py` is 3aa063d1's file with four changes, applied by asserted textual replacement (each source text occurs once). `experiments/r39tail.py` is byte-identical.
1. **Recipe.** `W3_LIT`, `W3_SHA` and the asserted count (Section 2.5). No decoder line changes.
2. **Hit path.** The pass flags a lane when its W17 test holds. For a flagged key the program enumerates all 5,489 masks; a mask is a mate when W9 is the representative's and W17 is the advice value (both recomputed on scalar words); a mate with W8 in F8 is completed to the pair, both blocks are compressed and compared. Charge: 560 per mask (the inherited 496 for building the scalar words plus 64 for the two schedule words and the three tests) and 2 x 2,812 per compressed pair. No mate list is stored. Trail-invalid mates are not filtered: they cost their charge and cannot produce a false output, because the output is decided by the two compressions.
3. **F8 prologue.** The six bit-sliced words that only the F8 test reads are no longer built in the attack path (F8 is not evaluated bit-sliced there since 087bf8f8). In the experiment modes they are built with the op counter restored, as the F8 test itself already was, so the counted ops are equal in all modes.
4. **Adder.** In `K4BS.add` a literal-one addend bit uses carry = P OR c, the full-adder carry at Q = 1, one operation where the generic form takes two. Output-identical.

The attack is `r39joint_k4.py --attack --k4`; its halts are B windows and the work cap of `k4_budget`, in which the tail constant is 2^-74.3238, as in 3aa063d1.

Unchanged: the walk, the claw filters, the dedupe gate for repeated F9 claws (1,536 slots), the streamed flush (once per window, or when 1,023 claws are queued), the literal-add W17 test s0(Xp + w2b) = Xp + S, the class and block literal folding, the work cap `k4_budget`.

## 4. Machine model (INHERITED, unchanged)
A counted RAM of 256-bit words; XOR, AND, OR, NOT, add, subtract, shift, rotate, compare, move are 1; a load or store is 3; a branch is 2; 2,812 operations per 39-step compression. Every operation goes through `Mach`. As in the bases, a bit-sliced operation with a literal operand is folded when the pass is formed and is not charged; this convention is inherited. Neither forming the folded pass nor storing it is charged (Section 6).

## 5. The ledger
| term | value | status |
|---|---|---|
| base walk per window, 99% upper bound | 463,618,904 ops (24 windows: mean 461,649,658, s.d. 3,858,918) | INHERITED; our 8 full windows (seeds 1000-1007) reproduce the leader's per-window base ops and F9-claw counts exactly |
| arrival-order index | at most 718,848 ops per window | INHERITED (1,536 keys x 468) |
| distinct groups per window | 58,959.42 | INHERITED |
| evaluated F9 claws per distinct claw | 0.016203 (99% upper bound over 48 windows; mean 0.015997) | INHERITED |
| pass allowance per evaluated F9 claw | **167,471** = the largest pass among 4,096 sampled claws. It is an allowance inside a work budget and is not an upper bound on a pass | MEASURED; priced as 3aa063d1 prices its pass |
| hit path per evaluated F9 claw | 1,343 (expected: 169,908 keys x 2^-32 x 33,943,992 per hit) | DERIVED |
| flush per window | 34,322,747 ops = 33,150,550 plane build and list generation + 37 x 31,681 raw bytes | MEASURED (read from the program at import) |
| **ops per distinct claw, K** | **11,193** = ceil(464,337,752 / 58,959.42 + (167,471 + 1,343) x 0.016203 + 34,322,747 / 58,959.42) | asserted at import |
| list entries passing F8 per distinct claw, E[N] | 403.4328 (99% lower bound over 16 full first-block CVs; exact model 361,638 x 585 / 524,288 = 403.5153) | INHERITED; model DERIVED |
| distinct passing keys / passing entries | **0.888073** | the smaller of the bound 0.888393 of 30714e48 (entry-weighted over 16 full windows; 3aa063d1 used 0.894521) and ours: 0.888074 (mean 0.890196, s.d. 0.002002 over 8 batches of 250 real F9 claws, t(7) = 2.998) |
| W17 trials per distinct claw | 358.277 = floor(403.4328 x 0.888073) | DERIVED |
| tail | **2^-74.3238**, the linear mean of the 14 organizer runs (best-case premise, as in 3aa063d1 and 30714e48); the replica's declared bound is 2^-74.45 | Section 8 |
| windows B | 2^80.9749 | `k4_budget` |
| **time** | **98.8153** (cap 2^98.815245 compressions) | log2(B x K x 58,959.42 / 2,812) |
| **score** | **98.9386** | time + (20.1233 - 20) |

**What the pass allowance is and is not.** The counted pass depends on the claw through the literal bits of two adds. Three numbers describe it and they are different things:
- **195,327: the deterministic upper bound.** No pass of any claw can exceed it (it need not be attained: the per-block maxima are summed). It is computed per block as loads (3 per non-folded plane) + the exact maximum over all 2^32 literals of each literal add (dynamic programme over the carry state, checked against the program's adder) + sigma0 (61) + comparison (63) + block test (7), summed over the 682 blocks, plus 55 for `k4x` in each of the 42 groups.
- **167,471: the sampled maximum**, over 4,096 claws with fresh random chaining values and (a0, u), the protocol of 3aa063d1 (mean 149,211, s.d. 5,498, p99 161,222). A pass above 167,471 is not excluded; only values above 195,327 are. **This entry does not claim 167,471 bounds a pass.**
- **153,842: a 99% upper bound on the expected pass**, by Hoeffding's inequality for 4,096 independent samples of a quantity that lies in [0, 195,327]: mean + 195,327 x sqrt(ln(100) / (2 x 4,096)). The mean pass on the 7,511 real F9 claws of our 8 full windows is 149,268.
The work cap charges 167,471 per evaluated F9 claw. The cap is a budget: the run halts when it is spent. The claim is that the budget is not spent before B windows except with small probability (Section 7), which needs the expected pass to be below the allowance (153,842 < 167,471) and every pass to be bounded (195,327); it does not need, and this proof does not assert, that every pass is at most 167,471. Priced at the deterministic upper bound instead, K would be 11,645 and the time 98.8724.

**Sensitivity to the tail premise.** With the tail at the declared bound 2^-74.45 in place of the mean, the same K gives time 98.9414 (+0.1262). This entry claims the mean-priced figure and states the premise in H2.

## 6. Memory (peak; data and literals itemised; instruction bytes of the k4 routines not counted)
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
| one chunk of planes, at most 28 blocks x 32 planes x 32 B | 28,672 | per flush |
| decoder block under construction, 32 words | 1,024 | per flush |
| decoder sigma0 tables, 4 x 256 x 4 B | 4,096 | per flush |
| decoder work lists: at most 448 low halves + 560 high halves, 4 B each | 4,032 | per flush |
| decoder search stack, at most 13 entries x 16 B | 208 | per flush |
| two inflate readers: window 4,096 + state 7,500 each | 23,192 | per flush |
| reader input and output steps, 4 x 64 B, and scalars | 320 | per flush |
| recipe, decoded bytes object | 1,184 | resident |
| recipe, base85 text of the same literal | 1,480 | resident |
| per-block fold literals, 682 x 2 x 4 B | 5,456 | resident |
| per-class fold literals and class word, 35 x 3 x 4 B; current class record 28 B; K4_N 4 B | 452 | resident |
| pass working planes (Xp, y, z, sigma0(y), accumulator: at most 130 words; 256 reserved) | 8,192 | per flush |
| dedupe table, 1,536 x 8 B | 12,288 | per window |
| dedupe occupancy bitmap | 192 | per window |
| arrival-order index, 1,536 x 2 B, and cursor | 3,076 | per window |
| hit path: scalar words of one candidate pair and mask counters | 256 | transient |
| output records and parser state | 128 | transient |
| list sha256 state (import only) | 128 | import |
| **peak (all rows summed)** | **1,142,084 = 2^20.1232** | |

- The claim states memory_log2_bytes = 20.1233, rounded up.
- Walk rows. Checked against the source: table 26,052 words (`table_words`), queue 897 words (`QCAP // 4 + 1`), wheel 128 words, lanes 256 words, save 32 words, two images of at most 710 records (`KCAP`), registers up to index 206 (`RCAP`) in a 256-word file. INHERITED from 9993eaa8 Section 6 and not recounted by us: the 4,111-instruction census (1,246 executed-block, 1,100 routine, 1,765 generator and relocation), the constants, free stack, parked scalars and pair records. 3aa063d1 carried the walk as one row of 1,047,428 bytes; the itemised sum with the envelope row is 1,047,708.
- **Not counted: the instructions of the k4 routines and the folded pass code.** The walk rows above include the walk's own instruction census. No entry of the k = 4 line (293ca62c through 30714e48) has a row for the instructions of the list decoder, the flush, the pass or the hit path, and this entry follows them. Under a convention of our own (one 36-byte instruction per syntactic operation of the routines' source, 1,221, plus 600 declared for an inflate reader, and the folded pass of one block at 5 bytes per record, 336 records) the omitted rows would be 65,556 + 1,680 = 67,236 bytes, the peak 1,209,320 = 2^20.2058 and the score 99.0211. That figure is stated so that nothing is hidden; it is not claimed.
- Recipe. Both the decoded 1,184 bytes and the 1,480-character base85 text of the same literal are counted. The stream is written with a 4,096-byte window; two readers are live during a flush and both are counted.
- No list is resident: the organizer experiment asserts before each trial that no integer container of 1,024 or more items and no byte string of 4,096 or more bytes exists, other than the per-block literal table, which has its own row.

## 7. Success probability and the cap
- lambda = B x 58,959.42 x 358.277 x 2^-32 x 2^-74.3238, set to -ln(0.61) + 2^-40 by `k4_budget`; B = 2^80.9749 windows. The run stops at B windows or at the work cap B x K x 58,959.42 = 2^98.815245 compressions; the claimed time is that cap rounded up.
- **Trials.** A trial is a key with at least one valid mate passing F8, in a claw passing F9. When such a key hits W17 the program tests every mate, so the key succeeds with probability at least p_tail, whatever the dependence between the tails of its mates. No within-key independence is used; that is the pricing 3aa063d1 calls the worst case, and the dedupe realises it without paying for the duplicates. Across keys and claws independence is premise H5 (INHERITED).
- **Count of trials.** E[N] x ratio, both at 99% bounds (Section 5). Our ratio measurement: 2,000 real F9 claws from 8 full windows; per claw 25103.0 entries pass F8 (model 361,638 x 9/128 = 25427.7) and 22346.0 distinct keys (s.e. 162). Multiplied by the 938.9 distinct F9 claws per window of those windows and divided by 58,959.42, our own direct estimate is 355.8 trials per distinct claw (s.e. 4.2): consistent with the priced 358.277 and less precise than it. The 16 full windows listed in 30714e48 give 360.2.
- **The cap does not bind before B windows (H6, MODEL).** Work per window = base walk + index + D x (pass + hit) + flush + X x flush. A pass is random with expectation at most 153,842 (Section 5) and never above 195,327. Means: 461,649,658 + 718,848 + 944.60 x 155,185 + 34,322,747 x (1 + 0.009134) = 643,592,430 per window, against the cap 11,193 x 58,959.42 = 659,932,788: margin 2.48%. Per-window s.d. at most 14,095,428 (sum of the parts' deviations with the pass at its deterministic upper bound, no independence between parts). If windows are independent with these moments, Chebyshev bounds the probability that the cap binds before B windows below 3.1e-25. The moments of the walk, of D (mean 944.60, s.d. 35.37) and E[X] <= 0.009134 are INHERITED sample estimates; this is a model statement, as in 3aa063d1.
- A window with more than 1,536 distinct F9 claws evaluates the excess without storing it (the gate never fails); our 8 windows had at most 979.

## 8. The tail (INHERITED; priced at the measured mean, as in 3aa063d1 and 30714e48)
- `experiments/r39tail.py` is the replica of 5f8e6192, unchanged, run by the organizer as r39-tail-01..14. It hard-asserts: 6,398 verified collisions in 45,875,200 proposals; linear mean 2^-74.3238; one-sided 99% bound 2^-74.3978; 99.9% bound 2^-74.4326; and that both bounds exceed the declared QDECL = -74.45.
- **This entry prices the tail at the mean 2^-74.3238.** That is a best-case premise, not a lower bound: a finite-sample mean can exceed the true probability. The judge recorded it on 3aa063d1 as F-COST-TAIL-MEAN, F-TAIL-POINT-ESTIMATE and F-EXP-TAIL-MEAN-AS-BOUND (material, not fatal) and passed that entry. Priced at the declared bound the time is 98.9414, which is 0.1262 higher.
- The replica draws W8 in F8 and W9 in F9 on the advice values of W10, W11. For k = 4 variants W10, W11 and W3..W7 differ; 3aa063d1 reports a joint arm on 60,000 real variant triples with ratio 2^+0.023 (s.d. 0.026). INHERITED, not re-run by us.

## 9. Premises
- **H1-claw-model.** First-block chaining values behave as independent uniform values for the walk and the later events; W17 is uniform over claws and keys at the 2^-32 scale. Walk work and yield per window as in Section 5 (INHERITED measurements).
- **H1-ops.** The constants of Section 5. The pass allowance 167,471 is a sampled maximum; the premise is on the expected pass (153,842), and the deterministic upper bound 195,327 is a fact about the program.
- **H2-tail.** p_tail = 2^-74.3238, the measured mean, for a valid entry passing F8 in a claw passing F9 with W17 hit (Section 8). Best-case premise; the supported bound is 2^-74.45.
- **H3-advice-construction.** The advice pair costs at most 2^43 compressions including the 93-pair selection (INHERITED from 9993eaa8 Section 11); the list costs about 2^24 operations to enumerate (our enumeration: under 2 minutes of interpreted Python).
- **H5-group-independence.** Distinct claws and distinct keys are independent trials. Not used: independence between mates of one key.
- **H6-cap-completion.** Section 7, a model with inherited moments.
- **H-implicit-distinct-key-dispersion.** At the scaled event of probability 2^-7 the organizer run counts key hits per claw (Section 10).
- **Convention premise, INHERITED and stated plainly.** Literal folding of the bit-sliced pass is not charged in time (Section 4), and the instructions of the k4 routines are not counted in memory (Section 6). Both have been the accounting of every entry since 293ca62c and no review has objected, but they are modelling choices, not measurements.

## 10. Experiments (organizer sandbox; the program hard-asserts every tuple)
- `r39-transplant-claw`: unchanged from 3aa063d1 (advice collision, fibres, inversion, 255 transplant identities).
- `r39k4-window-small`, trials 0-3: windows of 2^21 evaluations on the organizer seeds, check mode, k4 on for the first 2 F9 claws, the first 181 of the 682 blocks (45,876 lanes per claw). Asserted tuples (claws, F9, F8F9, lanes, F8 lanes, W17 hits, k4 ops, total ops): (221,5,0,91752,16618,0,17649892,28141509), (215,3,0,91752,7458,0,8868033,19329597), (226,4,1,91752,6872,0,8860717,24338673), (205,2,0,91752,6020,0,8869353,19924101). Trial 0 runs with one flush per claw.
  - Identity with 3aa063d1 on the same seeds (MEASURED by running both programs): claws, F9 and F8F9 are equal, (221,5,0), (215,3,0), (226,4,1), (205,2,0); the pass-off control ops_off = 10,491,617, 10,461,564, 15,477,956, 11,054,748 is equal and still satisfies ops_off = ops - k4_ops; W17 hits are 0 in both. Lanes and F8 lanes differ because the list differs: they count representatives.
  - Check mode asserts, on every 32nd lane, the F8 verdict and W17 against `k4_words`, and that the accumulator bit equals the indicator of W17 != advice value.
  - Key-hit statistic (uncounted): per claw N F8-passing lanes, D distinct keys (equal to N here), H lanes whose hashed W17 falls in a 2^-7 target, K distinct keys among them. Sums over the four trials: N = 36,968, H = K = 301 against 288.8 expected, Pearson sum 3.3720 on 8 dof.
  - Cross-claw tail proxy (uncounted): tail_F = 0.6104, 0.0008, 0.0007, 1.8513 on tail_n = 528, 231, 218, 178 lanes.
- `r39-tail-01..14`: unchanged.
- Participant-run (tools, not in the package): the planted-hit test (on a real claw the advice W17 is replaced in memory by a listed lane's W17, for three keys: each time exactly 1 key is flagged, 5,489 masks are visited, and the program's count of F8-passing mates equals a scalar reference count: 0, 1 and 1, among 4, 7 and 3 masks sharing the representative's W9 and W17); the 4,096-claw pass sample; the 8 full windows; the ratio measurement.
- Not executed by anyone: an end-to-end collision. All experiments are component tests; the claimed time is far outside any run.

## 11. Findings on 3aa063d1 and related filings, and where this entry stands
- F-COST-SAMPLED-MAX, F-EXP-SAMPLED-OPS-MAXIMUM, F-EXP-SAMPLED-MAX-CAP (5ff42cf1): **carried, with more disclosure.** The pass allowance is a sampled maximum, as in 3aa063d1. Unlike 3aa063d1 this proof states the deterministic upper bound (195,327), a bound on the expected pass (153,842), and says in terms that the allowance is not a bound.
- F-COST-TAIL-MEAN, F-TAIL-POINT-ESTIMATE, F-EXP-TAIL-MEAN-AS-BOUND: **carried.** The tail is priced at the mean, as in 3aa063d1; the bound-priced time is stated in Sections 5 and 8.
- F-MEMORY-INHERITED-BASE: the walk rows are itemised (Section 6); the instruction census inside them remains inherited and is said so.
- F-LIST-CARDINALITY-INCONSISTENCY: Section 2.5 gives one set of counts, reproduced independently, and says which earlier figures belonged to which list.
- F-MEM-RESIDENT-LITERAL (0e43259b), F-MEM-BLOCK-CONST (cdd6b40a), F-MEMORY-TABLE-SUM (cc05fd7b): both forms of the recipe, the per-block and per-class literals each have a row, and the table is summed by the script that prints it.
- F-TIME-PASS-UNDERCHARGE, F-EXP-PASS-MAX-CONTRADICTION, F-EXP-SUBMITTED-TIME-BELOW-CAP (cc05fd7b): the claimed time is the program's cap rounded up; K is asserted at import from the same constants this proof prints; the pass figure used in K is the one this proof reports as the sampled maximum (167,471), and no smaller figure is called a maximum anywhere.
- Still open, as in 3aa063d1: F-COST-CAP-EXTRAPOLATION and F-EXP-H6-TAIL-MODEL (H6 is a model), F-PREPROCESSING-CONSTRUCTION, F-DEPENDENCE-EXTRAPOLATION, F-EXP-RARE-EVENT-EXTRAPOLATION, F-EXP-NO-END-TO-END-WITNESS, F-EXP-PUBLIC-SEED-SELECTION, F-EXP-SCALED-K4-COVERAGE.

## Appendix A. Our full windows (2^26 evaluations, attack path, seeds as in 3aa063d1 Appendix C)
| seed | base ops | F9 claws, raw | distinct F9 claws | k4 ops | pass per claw |
|---|---:|---:|---:|---:|---:|
| 1000 | 459,242,401 | 1,118 | 970 | 179,577,572 | 149,265 |
| 1001 | 460,716,162 | 1,090 | 947 | 176,024,286 | 149,150 |
| 1002 | 460,526,883 | 1,120 | 936 | 174,467,449 | 149,245 |
| 1003 | 462,769,365 | 1,071 | 914 | 171,173,453 | 149,245 |
| 1004 | 466,593,739 | 1,157 | 979 | 180,724,402 | 149,060 |
| 1005 | 461,132,561 | 1,088 | 935 | 174,473,401 | 149,412 |
| 1006 | 463,895,626 | 1,102 | 918 | 171,768,569 | 149,241 |
| 1007 | 463,168,827 | 1,057 | 912 | 171,148,540 | 149,546 |

Base ops plus 12 per raw F9 lookup equal the leader's Appendix C values for the same seeds, and the distinct F9 counts are equal, in all 8 windows.
