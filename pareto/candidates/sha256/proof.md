# SHA-256 r39: four exact charged-operation rewrites on the screen entry a3eb4a8a

Target `sha256-r39-prefix-v1`: standard IV, the first 39 steps in every compression, FIPS padding, feed-forward and all 256 output bits. Claim: time_log2 116.54012 (log2 T 116.54011458336), memory 20.00577 (1,052,266 bytes production; 1,052,776 bytes in the 730-record diagnostic envelope; normalized score 116.54589), preprocessing 43, success at least 0.39 conditional on H1 restated at best-case mean prices from a3eb4a8a's 124 check-mode windows and on the inherited H2, H3 and H5, advice 160 bytes. This entry replays those 124 windows exactly. Every walk value, DP, table record, queue entry, trail ID, claw and group is identical, window by window, and each window's charged work falls by exactly the predicted saving of four rewrites (Section 3.6): 5,042,399 operations per window on average (1.120%). The groups are identical, so `log2(mean work / mean groups)` changes by approximately -0.01625, with no sampling error in that comparison. The marginal one-sided 95% raw-time sensitivity is 116.54256; the memory penalty applies separately.

The exact direct base is 0xplemonade's published `a3eb4a8a-5cf7-463b-a90d-c2325d7dcd41` at time 116.55637. It is Jbenisek's `9993eaa8-2c36-48da-a477-de7e318deb7d` (116.58624) with a 183-operation pre-generation screen of the drawn chaining value and an exact 679-record gate (Section 3.5). 9993eaa8 is 0xplemonade's `adef2aaf-efdd-4de0-bf13-62e21d150eb9` (116.591) with three charged-operation rewrites, and its first-block selection is 2ae904e3's. This entry keeps a3eb4a8a's selection, walk, advice, tail source and every charge for work that is performed. It rewrites four charged steps exactly (Section 3.6): the stage-2 kernel without the DP accumulator, a one-comparison first lane-search step, and two batch layouts with narrower fields.

Declared dependencies are `a3eb4a8a-5cf7-463b-a90d-c2325d7dcd41`, `9993eaa8-2c36-48da-a477-de7e318deb7d`, `adef2aaf-efdd-4de0-bf13-62e21d150eb9`, `2ae904e3-edb6-4484-a68b-26c897e06f03`, `5f8e6192-60b3-4ba1-bded-d3b73cfbc889`, `fce2f19e-04eb-405f-b7d5-e24260d85d13` and `0b2616e3-b9f7-4a9a-aefc-5a926f6e2197`. The last is credited directly because `experiments/r39tail.py` is its v2 tail-replica program; later entries in the lineage changed only the file's advice constants, run table and check value. The earlier program, transplant, claw, tail, selection, screen, rewrite and cost-model contributions are credited through those sources to Jbenisek, 0xplemonade, sraiw, dkuthoore, dariolina, mitchuski and lamb356. This is not a claim to have invented the characteristic, advice, claw construction, kernel filter, screen, reset masks, merge search, earlier rewrites or tail estimator.

Accounting. Selection is a3eb4a8a's: a drawn block costs 3157 operations (2830 for randomness, storage and compression, 140 for constant setup, 4 for packing and 183 for the screen), a discarded block 3 more, and every generation keeps the base's charges. Over the same 124 declared windows the mean window work is `mu+=445,257,295`, against a3eb4a8a's 450,299,695. Per window, 868,682 fewer operations come from the stage-2 kernel, 726,206 from the lane search, 2,595,382 from the hit groups and 852,138 from the insert batches; the cuts cost 8.08 more. No saving comes from omitting a charge for work that is performed. Apart from one uncharged register set per window, disclosed in Section 3.5, every operation is charged.

## 1. Target and output

SHA-256 with 39 steps in every compression, FIPS 180-4 padding, the standard IV, feed-forward after step 38, all 256 digest bits. The output is two distinct 128-byte messages `M0 || M1` and `M0 || M1'`: the same first block, second blocks that give the same chaining value after the second compression; the padding block that follows is identical, so the two digests are equal. The first block `M0` is a random block, `cv = compress39(IV, M0)`.

## 2. The construction (sraiw 38912d66, dariolina)

**2.1 The base is advice: the inherited pair on the published characteristic.** The advice is the inherited 39-step semi-free-start collision (`CV_PUB`, `M_PUB`, `MP_PUB` of `experiments/r39joint.py` section [1]; 160 bytes), printed with its signed characteristic and recompute in Appendix C. Its signed characteristic is the 39-step characteristic of ePrint 2026/1120 Tables 21 and 23 unchanged (pair inherited from the credited 5f8e6192 lineage): every signed row, state and message schedule, is the published one, only the values differ, and `W16 = 0xbca1c321` and `W17 = 0x71e9ba98` are the published values. The state and message values are this pair's own, which is why the tail is re-measured on it (Section 8). It is a collision of the 39-step compression from `CV_PUB` (experiment `r39-transplant-claw`, trial 0; `compress39` equals the organizer's `verifier/hash_functions.py` on 300 random blocks). Its trajectories `BA, BE` (`M'`) and `CA, CE` (`M`) are expanded from the 160 bytes by two compressions at the start of the run (charged 2 x 2812 + 120 operations, `Attack.base_setup`).

**2.2 The transplant.** Write `A[r]` and `E[r]` for the two state registers after step `r-1`, `a0 = A[4]`, `a1 = A[5]`, `u = W1`. Fix `A[6..9]`, `E[10..13]` and `W10..W15` to the published values of `M'`. For any chaining value `cv` and any `(a0, a1)`, steps 0 to 9 then determine `W0..W9` uniquely (`build(cv, a0, a1)` in section [1]); the partner message takes `W8 + D8`, `W9 + D9` and the published `W10..W15` of `M` (`second`). Both messages then follow the published trajectories `A[6..19]`, `E[10..19]` (steps 0 to 15 only, an identity of the step function, not a probability). The map `(cv, a0, a1) <-> (W8, W9, W16..W23)` is a bijection (320 bits, triangular). Experiment `r39-transplant-claw`, trials 1 to 255, checks the identity on 255 random chaining values.

**2.3 Row 16 is a claw.** `W16 = sigma1(W14) + W9 + sigma0(W1) + W0`. With `a1 = u + h(a0, cv)` (`recover_a1`) one finds `W16 - g = F(u) - F(a0)` (mod 2^32), where `g = 0xbca1c321` is the published `W16`, `F(x) = F_even(x)` for even `x` (a 32-bit expression in `x`, `S0(x)`, `MAJ`, `S1`, `CH` and six constants of the first block: `consts`, `fstep`) and `F(x) = sigma0(x) - x` for odd `x`. So `W16 = g` exactly when `F(a0) = F(u)` with `a0` even and `u` odd: a claw of the map `F` on 32-bit words (checked in `r39-transplant-claw`, `w16_identity`). Claws are found by a van Oorschot-Wiener walk (Section 3).

**2.4 What remains to pay, after a claw.** (i) `W8 in F8` and `W9 in F9`, where `F8 = { w : sigma0(w + D8) - sigma0(w) = 0x087ff000 }`, `F9 = { w : sigma0(w + D9) - sigma0(w) = 0x03010000 }` (`inF`); both sets depend only on 14 and 17 active bits of `w`, with exactly 1152 / 2^14 = 9/128 and 2080 / 2^17 = 65/4096 members (enumerated; the active-bit masks `0xCC19E60C` and `0xF9983C0F`), so `p8 p9 = 585 / 524288 = 2^-9.807707`. (ii) `W17 = 0x71e9ba98`, the published `W17` (the program tests it on every claw): probability 2^-32 for a uniform `W17`; the entry needs only that this value works (`solve_row_exact` in `r39-transplant-claw` trial 0 verifies `|G16| = 2`, `|G17(0xbca1c121)| = 0`, and `|G17(g)| = 1` with `G17(g) = {0x71e9ba98}`). (iii) The tail: rows 18 to 38 (`W18..W23` are the six free words of the bijection) must end with equal states after step 38: probability `p_tail`, Section 8.

Events (i) to (iii), together with `W16 = g` and the parity `a0` even, `u` odd, imply the collision: the pair then follows the published trail through row 17 and its remaining rows hold with the tail event. The program ends by compressing the pair and comparing (`Attack.claw`, last block). (`r39-transplant-claw` trial 0 checks the claw equation `fstep(a0) = s0(u) - u` of the advice pair directly and runs the filters with check mode off, as in Jbenisek's 2b4af365.)

## 3. Program and exact rewrites

Sections 3.1 to 3.3 are adef2aaf's changes, Section 3.4 is 9993eaa8's and Section 3.5 is a3eb4a8a's, all retained; Section 3.6 is this entry's change.

Each window constructs a random first block `M0`, compresses it from the standard IV to `cv`, and derives the constants of the 32-bit claw map `F`. A block whose screen value exceeds the threshold is discarded before generation (Section 3.5; at most 8192 discarded draws). Otherwise it generates two bank-swapped 256-lane bit-sliced kernels. A generation exceeding 679 records, 206 registers, or 575,000 charged generator operations is rejected and charged; at most thirty-two attempts are made. The table is cleared and 256 trails start with IDs 0 through 255. Production uses `WIN=2^26`, `DPB=7`, `MAXS=1536`, `CUTP=512`, `LMIN=32`, `QFULL=3328`, `QCAP=3584`, `WHEEL=2048`, `D0=82`, `KRES=6` and `CMP1=10`.

Stage 1 performs `2^18` kernel iterations. A point is distinguished when its low seven planes are zero. DP lanes are visited in ascending order and batched into non-overlapping 13-bit extraction windows. Two Horner passes extract planes 7 to 19 and 20 to 31; Section 3.6 gives the reconstruction. The bucket is `floor(167*r/2^15) = floor(171008*r/2^25)`; the packed table record is `chk(8) | length(11) | id(20)`, with `chk=r mod 256`. A bucket spans at most 197 consecutive values, so bucket plus checksum identifies `r` without false matches. A 39-bit record crossing a word boundary uses a second load/store. Keep-longer and the length-32 short-trail skip are unchanged. A match queues the two trail IDs and length difference in the unchanged 64-bit pair layout. Every restarted lane receives the next ID in the original order.

Stage 2 runs pairs in slots `(p,p+128)`. Long catch-up trails can start in any half-free lane; the other endpoint launches through the unchanged timing wheel. Moves, drops, batching, flushes, parking and resume order are unchanged. Every insert batch flushes before a move, kernel step, park or drain. All ten low planes are compared first; the remaining twenty-two planes are compared for surviving candidates. The first equality produces the predecessors. Opposite parity invokes `claw`; F9, F8, W17 and full collision verification remain in their original order. On success the program emits the two 128-byte messages with their common first block. The common padding block then preserves equality of the full target digests.

The queue cannot overflow: before a DP iteration it has fewer than 3328 entries and an iteration can add at most 256, so the peak is at most 3583. A trail is cut once its age reaches 1536 at a scan, with at most 511 intervening iterations. Recorded lengths are below 2048. If the 20-bit ID space is exhausted, stage 1 stops and the final stage 2 drains. These invariants are preserved by the following rewrites.

### 3.1 Recent-reset masks

Let `C=CUTP`; both production and the forced test use `MAXS=3C`. At a regular scan time `t`, three masks record DP restarts in `(t-C,t]`, `(t-2C,t-C]` and `(t-3C,t-2C]`. Their union contains only lanes younger than `MAXS`. The program visits its complement, retaining the original age and ID checks. It removes the lowest set bit each time, preserving the original ascending order and hence the assigned IDs. Cuts need not be added to the masks: omitting a recent cut can only cause an extra age check, which rejects an early cut.

For ID `i<2^20` and birth time `b`, the existing lane encoding is `LA=i-(b+1)*2^20 mod 2^256`. In the program's bounded iteration range, the original unsigned threshold comparison is exactly `b<=t-MAXS`. Thus skipping a lane marked by a genuine reset cannot skip a required cut. Each DP iteration adds its original DP mask once before the hit handler consumes it. The masks rotate on every scheduled scan, including scans before `MAXS`.

`cut_at` records the next expected scan time. A direct time jump falls back to the original full scan and clears the masks. ID exhaustion also selects the full scan because a DP bit may then refer to a restart refused by the original handler. Clearing masks is conservative; future masks contain only later resets. The original per-lane guard still handles exhaustion reached during the scan itself. Initialization costs four charged register sets; the DP accumulation, rotation, tests, loop, calls and resets all use explicit `Mach` charges. The code counts separate static blocks for the fast and fallback paths.

### 3.2 A 128-lane merge search

The active-pair mask `bact` has bits only below 128. It starts at zero. Paired launches and moves draw IDs 0–127 from the free stack; in-place callbacks originate from those launches; free-partner callbacks set `q & 127`; and merges remove such a bit and return its index to the stack. This inductively preserves both the stack range and the `bact` range. Since `full` is a subset of `bact`, its merge search never needs index bit 7. The specialization omits the known-zero high-bit test and the OR into zero, saving four operations per merge. Other callers keep the full 256-lane search. The historical adef2aaf bodies cost 26 and 22 census instructions. The current first-comparison rewrite in Section 3.6 reduces these to 25 for the generic search and 21 for the specialization.

The local equivalence verifier checks 4,864 bounded reset histories, including time jumps and exhaustion, and 524,536 lane masks. All six corresponding incorrect mutants fail. Algebra supplies the general interval and range arguments; the finite checks supplement it. In adef2aaf, a tested additional comparison stage preserved semantics but increased full-window cost and was rejected. The present entry changes only the first lane-search comparison, as described in Section 3.6.

### 3.3 Composition with the first-block filter (adef2aaf)

The rejection loop, its random draws, `KTRY=32`, register/fuel limits and emitted kernels are those of the base; this entry's screen (Section 3.5) and `KCAP=679` only change which drawn blocks reach the generator and which images are accepted. The four cache fields are initialized only after a kernel has been accepted. Neither the reset masks nor the narrowed merge search is used during selection. Thus the interval and active-lane arguments above hold for every selected map, independently of how that map was selected. A window with all 32 attempts rejected still returns no walk groups; it incurs all trial costs and needs no cache initialization.

The additional constant-setup allowance is outside all selection predicates. `Mach.o` is not an input to a branch condition inside `Attack`; the generation limit tests use `gops`, and kernel/ID/queue decisions use their original state. The extra charge is exactly `140*kskip`, including all-rejected windows. Direct probes compare complete state and RNG state for zero, 12 and 19 rejections, and synthetic three/32-rejection exits. A mutant omitting the charge fails. The global work halt is recalibrated to the resulting ledger; per-window search events and order are preserved.

The advice diagnostic temporarily raises `KCAP` for the fixed `CV_PUB`, whose image has 730 records, and restores it before checking the claw. This entry sets the temporary cap to 730 (1024 in the base), the asserted size of that image, so the diagnostic accepts exactly the same kernel. The cap was lowered after the measured program was frozen, and it is the only reason the conservative envelope carries no memory penalty (Section 6). A supplied chaining value bypasses the screen. This is not an exception to production selection. The ID-stop fixture starts at `2^20-2131` (`2^20-1998` in the base): under the screened selection the forced seed selects another map. Of the 267 offsets scanned for that seed (every offset from 1990 to 2029 and from 2130 to 2280, and every 50th from 2030 to 5980), 2131 is the smallest at which the stop again falls inside a partly restarted hit group and the final stage 2 drains. The 98 offsets from 2031 to 2129 other than 2080 were not scanned, so 2131 is not shown to be the smallest such offset (Section 10).

### 3.4 Three rewrites (9993eaa8)

(a) `hb_clr`. In adef2aaf, `delta_lanes` clears planes 20 to 31 of each hit group's lanes (`nG = NOT G` and 12 ANDs: 13 operations per group). This entry removes that clear and, after the last group of a DP iteration, ANDs planes 20 to 31 once with the DP register `R[dpreg]` (12 operations per DP iteration, block `hb_clr`). `R[dpreg]` is the complement of the union of the iteration's groups (check mode asserts it equals the iteration's `n0`), no handler writes it, and each group handler reads and writes only its own lanes (`extract25` and `delta_lanes` are masked by `G`), so the register state after the iteration is identical. An iteration with a DP has at least one group, so 12 <= 13 x groups.

(b) `lowqh`. A paired launch computed `lowq << 128` twice, for the occupancy update and for the second `qins`; it is computed once and reused, saving one operation per paired launch with `d = 0` (block `l_pair` 16 to 15).

(c) `ppd`. The merge loop recomputed `pp XOR rotl(pp, 128)` for each merged lane (two operations), where `pp` is plane 0 of the predecessor bank. It is computed at the first merged lane of a comparison and reused; nothing in the loop writes that plane (check mode asserts `pp` unchanged at every lane).

Each rewrite never adds a charged operation, so the hard window bound is unaffected. On all 24 published-protocol windows, 9993eaa8's claws, groups, kernel records, registers and rejected blocks equal adef2aaf's (Appendix A of 9993eaa8's proof; Appendix A here lists this entry's own 124 windows), and both joint experiments reproduced adef2aaf's semantic expectations exactly, including the forced park, cut and ID-exhaustion trial; only `ops` and `blk_census` changed. Rerunning both programs on those 24 seeds for this entry gave the same parity.

### 3.5 The pre-generation screen (a3eb4a8a)

Every drawn first block is compressed. Its claw-map constants `c = consts(cv)` and generator inputs `c5 = (cw + (cv0 AND cv1), eb, P, R, G)`, with `P = cv0 XOR cv1`, `R = cv4 XOR cv5` and `G = cv5`, are formed exactly as the base forms them for a generation attempt. The screen then computes

```
S = 3 pop(R AND 0x00F27618) + 2 pop(R AND 0x7F0D89E6) + 2 eb[1] + eb[2] + P[31] - pop(P AND 0x1FFFFFFE)
```

and generates the block only if `S <= 5`. Otherwise the block is discarded and the next one is drawn. The two R masks are disjoint and together cover R bits 1 to 30. P bits 1 to 28 carry weight -1 and P bit 31 weight +1. R bits 0 and 31, `cw` and `G` do not enter. The test is the study's level form `677.99 + 2 S <= 687.99` with its constants cancelled. The masks and threshold were frozen before any window of a3eb4a8a was run (see Provenance below).

**Program (`Attack.scr`).** Let `T = S + 28`. One 128-bit word `Z` holds four 32-bit fields:

- field 0 is `R AND 0x7FFFFFFE` with `eb[1]` at bit 31;
- field 1 is the same word shifted by 32;
- field 2 is `(R AND 0x00F27618) OR (eb AND 4)`, shifted by 64;
- field 3 is `((P AND 0x9FFFFFFE) XOR 0x1FFFFFFE)`, shifted by 96. It holds P bit 31 and the complement of P bits 1 to 28.

Since `0x7FFFFFFE = 0x00F27618 + 0x7F0D89E6`, `pop(Z) = 2 pop(R AND 0x7FFFFFFE) + 2 eb[1] + pop(R AND 0x00F27618) + eb[2] + P[31] + 28 - pop(P AND 0x1FFFFFFE) = T`. Fifteen charged operations build `Z`, and a move sets `k = 33`. A fixed loop of 33 passes then clears the lowest set bit (`Z = Z AND (Z - 1)`), decrements `k` and branches on `k`, at five operations per pass. After the loop `Z = 0` exactly when `pop(Z) <= 33`, that is `S <= 5`. One compare-and-branch on `Z` decides. The screen charges 16 + 33 x 5 + 2 = 183 operations on every draw, independent of the data. It has 23 static instructions in three census blocks: `scr` 16, `scr_lp` 5 and `scr_end` 2. A discarded block adds the draw-counter update and the cap test, block `scr_cap` with 3 operations. The screen uses scalars only, with no table and no memory access.

**Charges.** Each drawn block is charged:

- 2 for randomness, 16 for storage and 2812 for compression, as in the base;
- 140 for the existing constant-setup allowance;
- 4 for packing `c5`;
- 183 for the screen.

That totals 3157. A discarded block adds 3, giving 3160. A block that passes is generated exactly as in the base and keeps every base charge: 575,000 + 142 if the generation is rejected, and 140 + generator + 8 per record if it is accepted. Its constant setup is therefore charged twice, at about 340 operations per window. No base charge is removed or lowered. `Mach.o` is not an input to any branch. One operation is not charged: setting the draw counter to zero at the start of a window (`dr=0`), like the base's uncharged `tries=0` beside it. Over all B windows it adds at most B operations, below 3.2e-09 bit of `log2 T`, which the rounded claim absorbs.

**Caps and zero yield.** A window makes at most `DTRY = 8192` discarded draws and at most `KTRY = 32` rejected generations. Reaching either cap ends the window with no walk and no groups, and all its charges count. Section 7 and H1 include these windows. With screen pass rate `p` per draw and gate precision `q` per passing block, the KTRY exit has probability `(1-q)^32` and the DTRY exit, 8192 discards before an accepted block, `((1-p)/(1-p+p*q))^8192`. On 2,000,000 fresh synthetic blocks `p = 0.00528` and `q = 0.4077`, so the exits have probabilities 5.3e-08 and 2.0e-08, 7.3e-08 together. On the program's own streams of window seeds 1000 to 248000 (1,488,000 draws) `p = 0.00533` and `q = 0.3957`, giving 1.3e-07; at the 95% lower limits of the pooled rates it is 1.4e-07. A factor `1 - 10^-7` would therefore not be conservative. H1 prices claws and groups with the factor `1 - 10^-6`, which covers every precision above 0.355 at the pooled pass rate.

**Draw order.** The screen consumes no randomness, and the generator never runs for a discarded block. A window therefore draws exactly the base's blocks in the base's order, and it accepts the first block that passes both the screen and the exact gate. The exact gate is unchanged apart from `KCAP = 679`: every accepted kernel has at most 679 records and at most 206 registers, as the generator itself reports. A supplied chaining value, used by the advice diagnostic only, bypasses the screen.

**Exactness of the decision.** In check mode the program asserts, for every drawn block, that the charged decision equals `S > 5` evaluated by a separate popcount expression. Every declared window ran in check mode, 50,303 draws in all. Outside the program, an independent native oracle supplies the stream, records and registers. That oracle has its own 39-step compression, constants and Python-compatible MT19937, plus the program's own C generator text compiled natively. It agreed with the program's Python generator on records, registers and both banks for all 1,160 compared blocks. Against the oracle, the program's screen also matched:

- 200,000 random and constructed `c5` values (decision and the 183-operation charge);
- 38 complete first-block streams (discarded draws, rejected generations, the accepted block, its records and the exact setup charge);
- both cap exits;
- the selection and setup charge of every one of the 124 declared windows, and of the 124 windows of the unchanged program.

Eight planted mutants are each caught by at least one of these tests: a dropped mask bit, a lost weight, an off-by-one threshold, a sign error, swapped P/R words, the screen applied to another block, uncharged loop operations, and an extra random draw.

**What the screen predicts.** The acceptance criterion is still the generator's record count, and S is a correlated proxy for it, not an exact predictor. On 2,000,000 fresh synthetic first blocks (records mean 722.45, sd 16.53), `S <= 5` holds with probability 0.00528. Among blocks that pass, 0.4077 have at most 679 records; their records are 681.47 (sd 9.20, range 647 to 715). Of all blocks with at most 679 records (probability 0.00475), the screen keeps 0.4535. The errors take two forms:

- a passing block with more than 679 records costs a generation and is rejected by the exact gate;
- a discarded block with at most 679 records costs only its draw, but the accepted set is then narrower than the record criterion alone.

That second effect is why a3eb4a8a re-measured H1 rather than inheriting it. The predictor `677.99 + 2 S` has residual sd 8.19 records. A 160-bit least-squares fit has 7.60 on held-out blocks, so most of the remaining error is nonlinear in the constants.

**Derivation.** Flipping single bits of `c5` exactly, over 20,000 random contexts, gives the generator's mean record change per set bit:

- R bits 1 to 24: 4.97 to 5.02; bits 25 to 31: 4.94, 4.87, 4.77, 4.50, 3.99, 3.00, 1.00. Each set R bit inserts the operand `e0[j] XOR G[j]` of `CH(e0, cv4, cv5) = cv5 XOR (e0 AND R)` into the bit-j adder, which costs one compressor and its carry.
- P bits 1 to 28: -2.33 to -1.49; P29 -1.00; P31 2.00. A set P bit turns the variable row `NOT x[j]` of `-(x AND NOT P)` into a constant. The even-branch sum then needs one compression less at bit j, partly offset by the parity multiplexer its second operand then needs.
- eb bits 1 to 5: 3.95, 2.00, 1.00, 0.49, 0.24. The lowest set bit of `eb` above bit 0 starts the variable carry chain of `e0 = x + eb`.
- `cw` bits 4 to 27: about -0.48. `cw` enters only through the constant operand `cwe`, whose set bits make the adders that take them cheaper.
- `G`: about 0.

The frozen weights match this structure: 4 and 6 records on R, which average 4.8 against 5.0; -2 on P; and 4, 2 on `eb[1]`, `eb[2]`. The R split into 6 and 4 has no structural counterpart. It is a property of the distilled integer form and is not refitted here.

**Provenance.** The masks come unchanged from an unpublished scratch study of compute-saving filters and rankers for rounds 37 to 40, run on 2026-11-03 before a3eb4a8a's work began. It was not made for a3eb4a8a. For r39 it did four things:

- it re-implemented the generator's record count and validated it on the `CV_PUB` image (730 records) and by replaying the published-protocol seeds 1000 to 24000 under the base's 710-record gate, matching the records, registers and rejections of all 24 published windows;
- it fitted the record count by least squares on the 160 bits of `c5` over 150,000 synthetic first blocks, drawn from `random.Random` seeded by a SHA-256 domain hash and never from a window seed, and rounded each coefficient to a multiple of 2, which gives the four masked popcounts above and the intercept 677.99 (a 160-16-1 network trained on the same blocks for comparison put its weight on the same words, but the masks do not come from it);
- it chose `K = 679` and `tau = 687.99` on 50,000 further development blocks and scored them once on 100,000 blocks of a separate domain;
- its walk-cost model, used to rank candidate policies, was a linear fit to Appendix A of adef2aaf's 116.591 proof, the same 24 published windows.

It used no fresh seed of a3eb4a8a and no tail data. Its frozen policy file (`r39_policy_dev.json`, SHA-256 `78bdd3badc626bafe18892eff89a5959b084f1124526b55c86924419e99a539a`) was bound by hash before any fresh window ran. The claim does not depend on the study: every acceptance is decided by the exact gate, and the selection, its cost and its yield are measured here.

### 3.6 This entry: four exact rewrites (a3eb4a8a)

Sections 3.1 to 3.5 are retained byte for byte in behaviour. This entry changes only how four existing steps are charged and laid out. Every walk value, DP, table record, queue entry, trail ID, restart value, claw and group is the same as in a3eb4a8a, window by window. Each rewrite either removes work whose result is never read or changes how values are packed for a batch. None removes a charge for work that is still performed. `Mach.o` is still not an input to any branch.

**(a) Stage-2 kernel without the DP accumulator.** The generator's last `DPB-1 = 6` records are the OR chain `acc = res0 | res1 | ... | res6` into `R[64]`. `build_folded` emits it after the column loop, where every output `res_j` is a distinct non-constant node of polarity 0. Each `Gen.A(..., orr=True)` on two such nodes emits exactly one OR record, and `allocate` keeps the record order. The intermediate `acc` nodes are neither inputs nor forced outputs, so they get scratch registers of at least 65, and no earlier record writes `R[64]`. Only stage 1 reads `R[64]`, in `iter1`, right after the stage-1 kernel and before any stage-2 call. Stage 2 never reads it. The installed image is therefore the body without those six records. `iter1` computes the same chain, in the same order, from planes 0 to 6 of the destination bank: six charged ORs, so stage 1 costs exactly what it did. Each stage-2 step is charged six fewer operations. Check mode asserts the tail structure of every accepted kernel. A unit test runs 600 kernels on 2,400 random register states and finds all 64 bank registers and `R[64]` identical.

**(b) The first `find_lane` step by one comparison.** For the isolated bit `low = mask AND -mask`, `low AND HIGHMASK[7] != 0` holds exactly when `low >= 2^128`. In `find_lane128`, Section 3.2 proves `mask < 2^128`, so `low AND HIGHMASK[6] != 0` holds exactly when `low >= 2^64`. A comparison that sets 0 or 1 is one primitive operation, like the program's existing `ne`, and it replaces an AND and a comparison. That saves one operation on every call. Check mode asserts the equality and the range on every call. A unit test of 40,514 masks, including the empty mask and all 256 single bits, finds identical results with exactly one operation fewer.

**(c) Split hit extraction, 13-bit groups.** Planes 7 to 19 of the group's lanes are extracted into `Z1`, and planes 20 to 31 into `Z2`, which is then rotated by 13. A hit's value is `(rr(Z1,l) AND M13) OR (rr(Z2,l) AND (M12 << 13))`. New IDs are kept as `ZL` (bits 0 to 6) and `ZH` (bits 7 to 19), each placed at its lane. Every field is at most 13 bits wide, so the existing greedy grouping can use 13-bit windows instead of 25-bit ones. Lanes of one group are then pairwise at least 13 apart, and no field overlaps another lane's. `delta_lanes` writes planes 0 to 6 from `ZL` and planes 7 to 19 from `Z1 XOR ZH`, the same old-XOR-new trick as before, so every restart value is unchanged. Hits are still handled in ascending lane order across groups. The grouping only batches extraction, so every table, queue and ID operation happens in the same order on the same values. Check mode still asserts each hit's value against the planes. On the 124 declared windows the groups fall from 315,348 to 273,788 per window on average. For windows where every hit receives a restart ID, the change per window is exactly `128*G13 - 131*G25 + 7*H`, where `G` is the group count at the given width and `H` the hit count. The first-ID predicate is `ZH == 0`: production IDs start at 256 and never wrap, so every assigned high field `nid >> 7` is nonzero. Rotation preserves nonzero and OR cannot cancel it. ID refusal leaves ZH unchanged. Thus this predicate exactly replaces the earlier fst flag without adding a stored boolean or changing the inherited uncharged first-ID-test convention.

**(d) Split stage-2 inserts, 10-bit batches.** Each queued ID is kept as `QL`, bits 0 to 9 at `[l, l+9]` (`z AND wl`), and `QH`, bits 10 to 19 at `[l+10, l+19]` (`z XOR QL`). The batch conflict test uses 10-bit windows. Planes 0 to 9 read `rr(QL, j)` and planes 10 to 19 read `rr(QH, j)`. Fields of lanes at least 10 apart never meet, so every inserted value is the queued ID. Batches still flush before every kernel step and move, so no lane value seen by a kernel step changes. Conflict flushes fall from 39,883 to 23,093 per window on average. The change per window is exactly `2*Q + (Q - F20) - 90*(C20 - C10)`, plus three per cut, where `Q` is inserts, `F` flushes and `C` conflict flushes.

**Evidence.** The rewritten program replayed all 124 declared windows in check mode. The four savings average 868,682, 726,206, 2,595,382 and 852,138 operations per window, and the three-operation cut path costs 8.08 more, 5,042,399 in all. Per window, the following match a3eb4a8a's records exactly: claw-set hash, distinct claws and groups, every counter except the three batching counters hgroups, qfl and qconf, kernel, registers, accepted block and chaining value. Each window's operation change equals the sum of the four formulas exactly. 12 fresh windows (window seeds 300000 to 311000), never used before, give the same result against the unchanged a3eb4a8a program run on the same seeds. Twelve planted mutants are each caught: a wrong tail length, uncharged ORs, wrong thresholds, wrong masks, rotations, shifts and window widths, and uncharged split operations. Six fall to check-mode assertions, three to the exact ledger and three to an external lane-value invariant (restarted lane equals its new ID; inserted lane equals its queued ID).

## 4. Machine model and prices

The unchanged collision-frontier-v5 convention is a classical 256-bit word RAM. A 39-step target compression costs 2812 operations. XOR, AND, OR, NOT, move, shift, rotate, add, subtract, compare and set cost one each; a conditional branch is compare plus branch, two; a load or store costs three for index shift, base add and access; a call plus return costs two. A register-to-register Boolean kernel record costs five stored bytes. Every other instruction costs 36 bytes. The kernel and all counted primitives remain those of the pinned base.

`Mach.o` records executed operations. `Mach.blk` records the static census convention: the maximum straight-line pass per named block, with a callee body counted separately and calls/returns accounted for. The new scan branches have separate blocks. Loop bodies that represent fixed register-plane programs are unrolled in this machine model; the two `find_lane` parameter values denote two charged static bodies. Measurement dictionaries, distinct-claw sets, trace hooks and Python interpreter overhead are external bookkeeping, not an implementation of the attack's memory or time model. The production driver disables the distinct-set measurement.

The generator's WebAssembly operators are charged when the module is supplied. The reported replays use the conservative fallback halt cap of 575,000 operations per attempted generation, plus eight relocation operations per kernel record. The Python generator is the readable reference for the same emitted Boolean records. No lower native generator price is substituted into these measurements. Appendix B retains the unchanged generator construction and its prior byte-identity evidence.

For the reported fallback-counter runs, a rejected random first block is charged 2830 operations for randomness/storage/compression, 575,000 for generation, 140 for constant setup and two for retry control: 577,972. Successful setup keeps its existing 140-operation charge. The full allowance is conservative if some accepted-only constants need not be retained on a rejected attempt. The same constant-derivation routine already exists; charging another execution does not add another static instruction image.

With the screen, a drawn block is charged 3157 operations: the unchanged 2830, plus 140 constant setup, 4 packing and 183 screen. A discarded block is charged 3160. A block that passes the screen and fails the generator gate is charged 3157 + 575,142 = 578,299, and the accepted block 3157 + 140 + generator + 8 x records. The screen's masks are instruction immediates; the conservative variant of Section 6 also counts them as six data words. Its loop is a fixed 33-pass loop with one census body, so it is counted once, as the base counts its other per-lane blocks.

## 5. Exact measured ledger

The original four-rewrite source replayed all 124 declared windows of a3eb4a8a in check mode, each with `2^26` walk evaluations: the 24 published-protocol seeds 1000 to 24000 and the 100 fresh seeds 25000 to 124000 (`--windows 1 --seed S`, S = 1 to 124). The program that ran them has SHA-256 `08ad31bac35034d3e7e0e6aa9effd69386e3bddfd751910179cc901dd17d83fd`. The reviewed source had SHA-256 fa48fede66be974ac8634224d7a248291a351f9e93cd53d3fa53582c7afb481d. The shipped source now has SHA-256 `af8d7b16563fff9b82af1578cdcefbaae35ba68e48ba5e46c2bca1e5b34de7e5` and additionally replaces fst by the equivalent ZH predicate proved in Section 3.6. It otherwise differs from the frozen replay source only in the declared experiment expectations and W_BUDGET. The original 124-window raw records are retained evidence, and fresh exact-source reproductions are identified separately in the remediation report. No window was chosen, added or dropped: the sample is a3eb4a8a's.

**Exact replay.** In every window, this program's claw-set hash, distinct claws and groups, kernel, registers, accepted block and chaining value equal a3eb4a8a's recorded values. So does every counter except the batching counters `hgroups`, `qfl` and `qconf`. For the measured windows, where every hit receives a restart ID, each window's change of charged work equals

`-6*s2iters - (find_lane + find_lane128 calls) + (128*G13 - 131*G25 + 7*H) + (3*Q - F20 - 90*(C20 - C10)) + 3*cuts`

exactly. At ID exhaustion use the general R3 term `130*G13 - 132*G25 + 3*H + 4*A - 2*K13 + K25`, where A counts assigned hit IDs and K13/K25 count groups with at least one assignment. It reduces to the compact term when A=H and K13=G13, K25=G25. In the forced ID-stop control one ID is refused; the delta is -13,924, four below the compact formula's -13,920. Here `G13` and `G25` are the hit groups at 13- and 25-bit windows, `H` the hits, `Q` the inserts, `F20` a3eb4a8a's insert flushes, and `C10` and `C20` the conflict flushes at 10- and 20-bit windows. Over the 124 windows:

| Rewrite (Section 3.6) | Operations saved | Per window |
| --- | ---: | ---: |
| (a) stage-2 kernel body | 107,716,524 | 868,682 |
| (b) one-comparison lane search | 90,049,559 | 726,206 |
| (c) 13-bit hit groups | 321,827,309 | 2,595,382 |
| (d) 10-bit insert batches | 105,665,129 | 852,138 |
| cut path (three more per cut) | 1,002 | 8.08 |
| Total | 625,257,519 | 5,042,399 |

The sample contains 7,322,621 distinct claws and 7,311,677 groups, as in a3eb4a8a. Its exact mean work is `55211904577/124`, rounded up to `mu+=445,257,295`. The sample standard deviation is 2913047.535948 operations, and the largest window has 454,931,124 operations (seed 95000). Mean claws and groups are 59053.395161290 and 58965.137096774, unchanged, and the priced rates `c-=59053.33`, `g-=58965.07` and `r-=0.998505` are a3eb4a8a's. Aggregate work is 7539.910173830 operations per distinct claw, with per-window ratios from 7401.895052 to 7765.168147.

The selection is a3eb4a8a's: 50,303 draws, 49,998 discarded by the screen, 305 generated, 181 rejected by the exact gate and no zero-yield window. Accepted kernels have 659 to 679 generator records (mean 673.411), so each installed body has 653 to 673, with at most 134 registers.

The table gives the program's own counters, summed and made exclusive by the base's convention. The change column is the mean per window minus a3eb4a8a's on the same windows.

| Category | Operations over 124 windows | Operations/claw | Change per window vs a3eb4a8a |
| --- | ---: | ---: | ---: |
| `run_setup` | 712,256 | 0.097268 | 0 |
| `accepted_generator` | 71,968,024 | 9.828178 | 0 |
| `setup_and_rejections` | 276,096,239 | 37.704565 | 0 |
| `hits` | 11,509,570,510 | 1571.782905 | -3,119,712 |
| `cuts` | 1,379,084 | 0.188332 | 5 |
| `stage1_walk` | 22,214,869,488 | 3033.731978 | 0 |
| `stage2` | 21,137,308,976 | 2886.576948 | -1,922,693 |
| Total | 55,211,904,577 | 7539.910174 | -5,042,399 |

**Inherited comparison.** a3eb4a8a's matched fresh comparison against the unchanged 9993eaa8 and its walk model are inherited unchanged, because this entry's windows are a3eb4a8a's windows. That comparison gives `log2(mean work / mean groups)` -0.0333 (95% bootstrap -0.0366 to -0.0300) and claws +19.6 (-55.4 to 94.5). This entry's finite-sample log-ratio change against a3eb4a8a is -0.0162462500857..., approximately -0.01625. It has no resampling error for these fixed windows; population saving remains a premise.

**Hard window bound.** The existing `R=2^51` bound remains conservative. Selection costs are a3eb4a8a's, below `2^25.5`. The rewrites lower each stage-2 step by six operations and raise no step by more than eight per hit and three per insert, far inside the stage bounds of the base: stage 1 below `2^39` and stage 2 below `2^50.3`.

## 6. Memory, source and register inventory

| Production item | Bytes |
| --- | ---: |
| `advice` | 160 |
| `constants_counters` | 4,096 |
| `free_stack` | 128 |
| `kernel_images` | 6,730 |
| `lanes` | 8,192 |
| `other_instructions` | 149,472 |
| `parked_scalars` | 192 |
| `queue` | 28,704 |
| `records` | 1,024 |
| `registers` | 14,784 |
| `save` | 1,024 |
| `table` | 833,664 |
| `wheel` | 4,096 |
| Production total | 1,052,266 |

The census is 1287 instructions in 76 blocks. a3eb4a8a had 1272 in 76. This entry removes `extract25` (74), adds `extract13x2` (73) and changes `cut_lane` 15 -> 19, `delta_lanes` 61 -> 60, `find_lane` 26 -> 25, `find_lane128` 22 -> 21, `hb_v` 4 -> 7, `hit_c` 9 -> 13, `insert_lane` 94 -> 93, `iter1` 7 -> 13, `qins` 11 -> 14. The census is measured as the per-block maximum over the advice claw, the four small windows, the forced, parked and ID-stop trial, and all 124 full windows. With the unchanged 1100 routine instructions and 1753 generator plus 12 relocation instructions, 4,152 non-kernel instructions occupy 149,472 bytes. The six accumulator ORs are now six instructions of `iter1` (Section 3.6), and the installed kernel images hold only the bodies: at most 673 records each, `2*673*5 = 6730` bytes. The generator's scratch and every rejected candidate construction, including kernels above 679 records, live in the 833,664-byte table arena before the walk table is initialized, as in the base. The generator still emits all records there, and the body is its first records. The constant routine and its packing already exist for every generation attempt.

For the diagnostic envelope, reserve two 724-record kernel bodies, corresponding to the inherited 730-record full-image cap. With the revised scalar reservation this is **1,052,776 bytes**, 4,200 above one MiB. The upward-rounded memory claim is 20.00577, so the normalized time-memory claim is **116.54589**. At the older 1024-record full-image reservation the envelope is 1,055,716 bytes and the upward-rounded normalized score is 116.54992. Storing the six screen masks as data adds 192 bytes; the shipped version uses immediates. These are word-RAM storage bounds, not Python RSS.

The prior 48-scalar claim is withdrawn. This revision reserves **256 scalar words**, each 256 bits or **32 bytes**, beside the 206-word kernel bound. Registers therefore occupy `(206+256)*32 = 14,784` bytes. The following deliberately conservative assignment needs 244 words: 51 permanent state/address words, 7 driver words, and 186 words for mutually nested procedure frames. No liveness-based slot sharing is needed within a frame, so the disputed split temporaries have distinct reserved words.

Permanent words, in ascending name order, are `A6, A7, BA8P, C17, C9, C9P, CA1, CE5, CH0, CW8, CW8P, K24, LA, NE11, QG, QH, QL, QW, R, W, ZH, ZL, c, cur, cut0, cut1, cut2, cut_at, cv, cv_try, dpreg, idc, idc0, it, it20, it20p, ks, lim, m, m0, messages, pairs_found, qn, qw, rnd, s2, sav, skip, success, tab, win`. These include fixed-address aliases conservatively; array contents remain in their separate memory rows. The 7 driver words are argument-vector address, attack address, two output-message addresses, seed, completed-window count and accumulated work. Frame-relative slot 0 begins after those 58 words. A frame assigns locals in ascending name order, then expression-result slots, then one return link. The expression bound counts every value-producing AST node in one expression, including expanded mS0/mS1/ms0/mMAJ/mCH/a32/s32 macros, with no reuse even for results that die earlier. A caller keeps its entire frame during a call. Each callee begins at or above the end of every possible ancestor frame; the call graph is acyclic. Thus no ancestor and descendant intervals overlap, and the last endpoint is 186. Fixed intervals require no dynamic stack pointer, spills or extra runtime instructions. Formal parameters and aliases may refer directly to operand slots; the reservation does not require extra copies.

| Procedure | Frame start | Named locals | Expression results | End including return link |
| --- | ---: | ---: | ---: | ---: |
| `insert_lane` | 135 | 11 | 3 | 150 |
| `delta_lanes` | 71 | 11 | 4 | 87 |
| `find_lane` | 122 | 10 | 5 | 138 |
| `extract2` | 71 | 8 | 5 | 85 |
| `extract` | 122 | 12 | 5 | 140 |
| `claw` | 122 | 24 | 39 | 186 |
| `qpush` | 103 | 6 | 6 | 116 |
| `qpop` | 122 | 5 | 3 | 131 |
| `iter1` | 12 | 23 | 19 | 55 |
| `wr` | 103 | 10 | 3 | 117 |
| `hit_group` | 55 | 10 | 5 | 71 |
| `hit` | 71 | 25 | 6 | 103 |
| `cut_lane` | 72 | 11 | 3 | 87 |
| `cutscan` | 55 | 12 | 4 | 72 |
| `bank` | 122 | 7 | 3 | 133 |
| `qins` | 122 | 10 | 2 | 135 |
| `qflush` | 122 | 3 | 1 | 127 |
| `move_lane` | 122 | 10 | 4 | 137 |
| `link` | 122 | 16 | 6 | 145 |
| `fpop` | 122 | 6 | 3 | 132 |
| `stage2` | 55 | 59 | 7 | 122 |
| `run_window` | 0 | 5 | 6 | 12 |

The deepest endpoint is `run_window -> iter1 -> stage2 -> claw`, at absolute word 243; the remaining 12 reserved words are spare. The hit path allocates Z1/Z2 in hit_group, ZL/ZH in permanent words and zl/zh in hit. The conflict-flush path retains QW/QL/QH/QG permanently and qins.wl/z/zl/zh in its caller frame while insert_lane uses a disjoint frame. The cut path keeps cut_lane.z/zl until the insert returns. These lifetimes deliberately extend through the entire frame, so early last-use optimizations cannot invalidate the bound. ZH replaces fst under the production ID invariant above.

Explicit checking, measurement dictionaries, distinct-claw sets and Mach census instrumentation are external evidence machinery under Section 4. The allocation excludes them, while retaining ordinary loop/control variables and address aliases. Selection and generation retain their inherited table-arena workspace; the complete compression and message-recovery primitives retain the existing constants/counters workspace and their charged allowances. The allocation establishes the online walk/filter scalar reservation under those inherited primitive contracts; it does not claim a compiled Python-memory bound. The packet's REGISTER_ALLOCATION.md and AST-only register_inventory.py give every local-to-word assignment and the extraction rule.

The two declared experiment sources total 65,293 bytes, below the 65,536-byte review cap. The complete static-block census is:

| Block | Instructions |
| --- | ---: |
| `bank_in` | 12 |
| `bank_out` | 12 |
| `bank_sw` | 18 |
| `cb_a` | 21 |
| `cb_drop` | 2 |
| `cb_free` | 5 |
| `cb_in` | 2 |
| `cb_move` | 11 |
| `claw_f8` | 29 |
| `claw_filter` | 30 |
| `claw_w17` | 57 |
| `cmp1` | 31 |
| `cmp2` | 67 |
| `cut_gate` | 5 |
| `cut_kind` | 2 |
| `cut_lane` | 19 |
| `cut_linear` | 4 |
| `cut_mask` | 3 |
| `cut_pending` | 3 |
| `cut_reset` | 3 |
| `cut_roll` | 6 |
| `cut_test` | 2 |
| `cut_threshold` | 3 |
| `delta_lanes` | 60 |
| `extract13x2` | 73 |
| `extract32x2` | 96 |
| `find_lane` | 25 |
| `find_lane128` | 21 |
| `fpop` | 9 |
| `hb_add` | 7 |
| `hb_close` | 2 |
| `hb_clr` | 12 |
| `hb_ext` | 1 |
| `hb_init` | 4 |
| `hb_ins` | 1 |
| `hb_last` | 2 |
| `hb_lp` | 2 |
| `hb_sel` | 6 |
| `hb_v` | 7 |
| `hit_a` | 38 |
| `hit_c` | 13 |
| `hit_m` | 22 |
| `hit_n` | 17 |
| `insert_lane` | 93 |
| `iter1` | 13 |
| `iter1c` | 3 |
| `iter1h` | 8 |
| `l_end` | 2 |
| `l_f2s` | 2 |
| `l_half` | 1 |
| `l_pair` | 15 |
| `l_single` | 7 |
| `l_try` | 11 |
| `launch` | 6 |
| `launch_t` | 4 |
| `link` | 32 |
| `merge` | 28 |
| `move_lane` | 130 |
| `qflush` | 5 |
| `qins` | 14 |
| `qpop` | 8 |
| `qpush` | 15 |
| `s2_fl` | 1 |
| `s2_in` | 20 |
| `s2_init` | 22 |
| `s2_out` | 20 |
| `s2_q` | 4 |
| `s2_step` | 2 |
| `s2_susp` | 4 |
| `scr` | 16 |
| `scr_cap` | 3 |
| `scr_end` | 2 |
| `scr_lp` | 5 |
| `w_end` | 6 |
| `w_s2` | 5 |
| `wheel_check` | 15 |

## 7. Success and the live work budget

The inherited mean-price model uses `p=(585/524288)*2^-32*2^-74.3238`. With `lambda=-ln(0.60999)` and `G=lambda/p`, `log2(G)=115.115003108584`. H5 assumes independent group trials, giving conditional success at least `1-exp(-lambda)=0.390010` once G groups are tried.

The program ships a3eb4a8a's `B_WINDOWS=762911287482054727600421276984`, unchanged, because the groups are unchanged. It is the least integer with `B*g*(1-2^-20)>=G` for `g=58965.13`, the group rate with the zero-yield factor `1-10^-7`. At the priced `g-=58965.07` the same B gives `B*g-*(1-2^-20) = (1-1.02*10^-6)*G`. Group counts are bounded by `2^26` per potential window, and the group shortfall exponent at `g-` has log2 39.962575973149. Potential windows are independently sampled before global stopping, and zero-yield windows are potential windows with no groups. H1 includes them in `g-` and `mu+`.

Let `X_i` be complete-window charged work, including every drawn block, the screen, every generation attempt and its setup allowance. H1 assumes `E[X_i]<=mu+=445,257,295`, with `0<=X_i<=R=2^51`. The shipped constant is

```
B = 762911287482054727600421276984
W = 339692140144587642111958320152396432972
W = floor(B * 445257295 * (1 + 2^-20)) + 1
d = W/B - 445257295 - 6
```

The six driver operations are included in the slack, and `d = 418.630446434`. Hoeffding bounds work failure by `exp(-2*B*d^2/R^2)`, whose exponent has log2 **15.686496920650**. Work and group failure together are at most `2*exp(-2^15.6)`. With at least `(1-1.02*10^-6)*G` groups, H5 gives conditional success at least `1-exp(-lambda*(1-1.02*10^-6))=0.3900096`, so success is at least `0.3900096-2*exp(-2^15.6)>0.390009>0.39`, conditional on H1, H2 and H5.

The driver halts at success, after B windows, or once its accumulated work reaches W, which it checks before starting another window. The bound is

```
T = (W + 2^51 + 6*B)/2812 + 2^43
log2(T) = 116.540114583364
time_log2 = 116.54012
```

Re-deriving the constants at the priced rate, as the least `B` with `B*g-*(1-2^-20)>=G` and the matching `W`, would give `B=762912063783638850595334299648`, `W=339692485798860734219854176419625530187` and `log2(T)=116.540116051`, rounded up to 116.54012.

**Mean pricing.** H1 assumes true mean work at most 445,257,295. The fixed-B Hoeffding argument has work slack d = 418.630446434. Allowing its work-failure term to consume the approximately 9.693e-6 success margin permits a mean excess of only about 412.44 operations. This is 0.00158 sample standard errors, since the measured SE is 261,599.39. The sample does not establish such a tight upper bound. If the true mean exceeds this margin, this fixed-B argument no longer certifies 0.39; it does not prove that the attack's actual success probability is below 0.39. The driver retains its declared work cap, subject to the inherited per-window bound and accounting model.

**Other pricings.** Priced instead at one-sided 95% limits (`mu+=445,690,766` and `g-=58922.95`, with B and W re-derived), the bound would be `log2(T)=116.5425507`, rounded up to 116.54256; with the factor `1-10^-7` (`g-=58923.01`) it is 116.5425493, rounded up to 116.54255. a3eb4a8a's 124 windows drew 405.7 blocks each, against 468.3 expected from the pooled pass rate 0.00530 and precision 0.4025 of Section 3.5. Pooled expected-draw pricing adds about 212,112.224009043 operations to the unrounded sample mean. After upward rounding the mean is 445,469,408 and the raw-time sensitivity is 116.54081. These one-sided 95% prices are marginal sensitivities using t=1.657, not a jointly established 95% full-attack guarantee. The rewrites leave selection untouched, so these selection sensitivities are a3eb4a8a's, shifted by the exact saving.

The claim 116.54012 is -0.01625 against a3eb4a8a's 116.55637 and -0.04612 against 9993eaa8's 116.58624. Preprocessing 43 is inherited unchanged. The revised memory reservation makes the normalized time-memory claim 116.54589; the raw time claim remains 116.54012. The resource caps hold under the declared word-RAM, per-window and primitive-workspace contracts. The true expectation, uniformity, tail and independence premises are not established by 124 samples.

## 8. The tail p_tail (rows 18 to 38)

Definition (unchanged from 4487063 and 19034ce). Distribution `U`: `E16`, `E17` of the first member pinned to the published values (this fixes `W16 = g`, `W17 = 0x71e9ba98`); `W8` uniform on `F8`, `W9` uniform on `F9`, independent; `E18..E23` of the first member independent and uniform on 2^32 (`W18..W23` are a bijective image of them); everything else is determined by the real step function and message expansion. `Q = P_U(collision and K_P | a0 even, u odd) = 4 P_U(collision and K_P and a0 even and u odd)`, where the collision test is exact (equal 256-bit outputs of the two 39-step compressions) and `K_P` is an importance carrier (the printed cells of Tables 21 and 22 of rows 16 to 18, signed differences only for rows 19 to 22, `E23[30] = 0`). `K_P` is a subset of all routes to a collision, so `Q <= p_tail`; the claim prices `p_tail = 2^q_tail` with `q_tail` = -74.3238, the linear mean of the 14 runs (best-case premise: the tail probability equals its measured mean; the hard-asserted linear 99.9% bound is -74.4326).

Priced value and check value. The claim prices `q_tail` = -74.3238, the linear mean of the 14 runs (best-case premise, declared). The replica hard-asserts the conservative check value `QDECL` = -74.45, fixed before the organizer runs by the pre-registered rule: at least 0.01 below the one-sided 99.9% Student-t lower bound (t = 3.852, 13 df) of the frozen design, rounded down to two decimals. Design (frozen before the runs): the same estimator as 4487063 and 19034ce - trial 0 an SMC over `E18..E23` with 800 particles, exact 1- and 2-step look-ahead and multinomial resampling, trials 1..20 the rows-24..38 Monte Carlo - with the work re-allocated inside the organizer's 16-experiment and 20-second limits: stage lanes per particle 8x512 (row 18), 8x2048 (19), 8x2048 (20), 4x128 (21), 6x256 (22), 1x4 (23) - 19034ce used 1x512, 5x2048, 3x2048, 1x128, 1x256, 1x4 - and 20 trials x 80 batches x 2048 proposals = 3,276,800 proposals per run (2.0 times as many), every particle driving exactly two batches. Three constant-factor changes only: lazy pool candidates (a pool entry is the packed pair (parent index, E); the candidate's row values are recomputed for the row and look-ahead checks, never stored), `CH = g ^ (e & (f ^ g))` and `MAJ = (a & (b | c)) | (b & c)` in the packed hot paths (3 and 4 operations instead of 4 and 5, bitwise identities), and per-width cached packed constants for the trace. The v2 program, run with the published advice at 19034ce's exact parameters (`CFG 1x512, 5x2048, 3x2048, 1x128, 1x256, 1x4`, `NCH = 10`), reproduces 19034ce's outputs byte-identically - carrier, stage counts, per-trial hits and parity classes, the same RNG draw order and count - on three private seed sets, so the estimator, the filters and the Feynman-Kac product are unchanged and only their variance changed. (The regression variant is the shipped file with two constant edits - `CFG = {18: (512, 1), 19: (2048, 5), 20: (2048, 3), 21: (128, 1), 22: (256, 1), 23: (4, 1)}` and `NCH, NB, LF = 10, 80, 2048` - which the 64-KiB two-program source budget does not allow to ship alongside the shipped configuration; the byte-identity was checked on the carrier, all stage counts, every per-trial hit list and the parity classes.)

Evidence: the replica `experiments/r39tail.py` runs in the organizer sandbox as `r39-tail-01` to `r39-tail-14` (Section 10) and embeds the exact 14-run table `EXP` (packed, one line per run: stage counts `k18..k23`, `log2_carrier`, total verified hits, parity classes) and `verify_smc_stats()` with hard `assert` statements. By Del Moral's Feynman-Kac theorem, the unnormalized product estimator `Q'_r = 2^(l2_r) * (hits_r / 3276800)` is an exactly unbiased estimator of `Q'` on the linear scale (`E[Q'_r] = Q'`, zero log-scale Jensen bias). On every run, `verify_smc_stats()` hard-asserts: (1) direct stage-18 Monte Carlo calibration (`c18 == 206` out of `65,536` uniform draws, matching the 14-run SMC stage-18 rate within `0.0003`); (2) 6,398 verified collisions in 45,875,200 proposals across the 14 runs with parity classes `[1592, 1626, 1624, 1556]` (`chi-square = 2.03 < 7.81`); and (3) linear-scale unbiased sample mean `log2(mean(Q')) = -74.3238`, one-sided 99% Student-t lower confidence bound `log2(lcb_lin) = -74.3978 > -74.45`, log-scale 99% bound `-74.3987 > -74.45`, and the linear one-sided 99.9% bound `-74.4326 > -74.45` (t = 3.852, 13 df; sample sd of `log2(Q')` 0.1011). Measured sandbox wall time 12.9 to 13.7 s per run on the sizing host (ten private-seed runs of the frozen configuration in the same pinned image and sandbox flags; limit 20 s).

Selection and the tail coverage (answers `F-LC-TAIL-SELECTION` and `F-EXP-PUBLIC-SEED-SELECTION`). The shipped pair was chosen among 93 candidate pairs by the tail measurement (Section 11, Section 12); no holdout is claimed. The selection is covered by a Bonferroni correction over all 93 screened pairs, which holds for the selected pair under any selection rule over the 93: per-pair level `alpha/93`, `t_13` quantiles 5.0692 (family-wise 99%) and 6.4547 (family-wise 99.9%), on the same linear-scale estimator as `verify_smc_stats()` over the 14 runs, give family-wise lower bounds `log2 = -74.4688` (99%) and `-74.5112` (99.9%). The mean-price claim still uses q_tail = -74.3238. Repricing the shipped fourteen-run EXP table at the family-wise 99% lower bound, using the stated quantile 5.0692 and rederiving B and W at g- = 58965.07, gives q_tail = -74.468830662 and log2 T = 116.685146713, rounded upward to 116.68515. The corresponding family-wise 99.9% raw-time sensitivity is 116.72748 using quantile 6.4547. These remain sensitivities under the inherited tail model, not established full-attack success bounds. The memory penalty must be added separately for normalized scores.

**Relevance under the screened selection.** The replica measures the tail on the fixed advice state with `W8` uniform on `F8`, `W9` uniform on `F9` and `E18..E23` uniform. It never uses a window's chaining value, so it is unchanged and still applies if the screened claws' free words keep that law. The screen selects chaining values whose R word is sparse, so this is tested directly on the distinct claws of all 124 windows, against the claws of the fresh baseline windows:

- `W8` in `F8`: 0.07028 vs 0.07033 (p = 0.73);
- `W9` in `F9`: 0.01588 vs 0.01578 (p = 0.146);
- `W17` low byte equal to that of `0x71e9ba98`: 0.003929 vs 0.003886 (p = 0.216);
- low-byte homogeneity of `W17..W23` (two-sample chi-square, 255 df) has p-values W17 0.189, W18 0.182, W19 0.928, W20 0.899, W21 0.13, W22 0.52, W23 0.767.

The smallest of the ten p-values is 0.13, against the preregistered Bonferroni level of 0.001. The pooled goodness-of-fit chi-squares of the screened claws (255 df) are W17 267.7, W18 279.0, W19 206.2, W20 254.1, W21 252.7, W22 258.0, W23 242.7. These finite tests find no detectable departure from that law. They do not prove the H2 premise for the screened selection.

**Power.** With 7,322,621 screened and 5,903,868 baseline claws, the two rate tests would detect relative shifts of 0.66% (F8) and 1.43% (F9) at the Bonferroni level, and of 0.83% and 1.80% with 80% power: about 0.012 and 0.026 bit of success probability. Measured directly, the screened claws' rates differ from the exact 9/128 and 65/4096 that the price uses by -0.044% (standard error 0.13%) and +0.093% (standard error 0.29%), so the F8/F9 factor of the price is supported to about 0.005 bit at one standard error. The low-byte tests constrain marginal byte frequencies only. An independent review re-extracted every distinct claw of the 348 measured windows; its per-window counts equal this entry's records in every window. It compared every bit and byte of `W8`, `W9` and `W17..W23` between screened and fresh-baseline claws: 287 bit tests (`W8` bit 0 is constant) with largest `|z|` 2.61 (W21 bit 4), and 36 byte tests with Bonferroni p 0.26. At the family-wise 1% level they would detect a bit-frequency shift of about 0.11 percentage points (0.14 with 80% power). None of these tests reaches the joint law of `W18..W23` and the advice state, on which the tail probability depends. Transfer of the measured tail to screened claws therefore remains the premise H2; the evidence above is conditional support for it, with no detectable departure.

## 9. Premises and limits of the composition

**H1-claw-model (restated).** The selection and every window are a3eb4a8a's, so H1 keeps a3eb4a8a's selection (`S<=5`, `KCAP=679`, `KTRY=32`, `DTRY=8192`, including zero-yield windows), with claws at least 59053.33, groups at least 58965.07 and ratio 0.998505. Only the work price changes: the true expected work is priced at most 445,257,295, the exact mean of the same 124 windows under this program. These are best-case mean-price assumptions from 124 windows, not confidence limits. The particular fixed-B Hoeffding certificate tolerates only about 412.44 operations of mean excess over mu+, against a standard error of 261,599.39; this is a sufficient-argument limitation, not a necessary condition for actual success 0.39 (Section 7). The rewrites change no walk, claw or group (Section 3.6), so every claw and group statistic of a3eb4a8a's H1 transfers exactly; only the work of each window is re-priced, by an exact formula verified on every window. The screened maps have sparser R words (mean `pop(R)` over bits 1 to 30 is 7.85, against 12.09 for the fresh baseline) and denser P words (16.85 against 14.74 over bits 1 to 28). Uniformity of the claw free words after this conditioning is a premise, tested in Section 8.

**H2-tail.** The same advice, tail source, fourteen-run EXP table and priced mean `-74.3238` are retained. Section 8 adds tests of the screened claws' free words, with their power. They find no detectable departure and are conditional evidence that the measured tail transfers, not a proof. The public seeds and the selection among 93 pairs remain limitations.

**H3-advice-construction.** Unchanged. Preprocessing 43 covers the inherited construction and selection.

**H5-group-independence.** Unchanged in form. Each window gives three within-window lag-1 statistics `|r| sqrt(n)`, over `W9 in F9`, `W17 bit 0` and `W18 bit 0` in claw order. Of the 372 statistics of the 124 windows, the number at or above 3 is 1, and the largest is 3.01 (seed 5000, W17 bit 0). Under independence about 1.0 are expected (`P(|Z|>=3)=0.0027`). The unchanged 9993eaa8 program on the same 124 seeds also has 1 of 372, but its largest is 4.24 (fresh seed 51000, W9 in F9). The small-window experiment still hard-asserts the pooled tests.

The counted-word instruction representation, the generator macro prices and the register allocation remain declared accounting conventions. The screen adds charged work for an exact decision and claims no lower price for generation.

## 10. Experiments and exact state evidence

`r39-transplant-claw` runs the advice diagnostic with its temporary cap of 730 records, then restores production parameters. The advice kernel has 730 generator records (a 724-record installed body), the claw costs 6140 and its census is 121, all unchanged. The supplied `CV_PUB` bypasses the screen. Its organizer output is byte-identical to a3eb4a8a's: the stdout hash is the same in every run.

`r39-window-small` runs four windows of `2^22` evaluations under the screened selection, with every screen, generation and setup cost charged. Its exact assertions are:

| Observation | Four values |
| --- | --- |
| `distinct_claws` | `[784, 883, 820, 808]` |
| `distinct_groups` | `[784, 883, 820, 808]` |
| `dp_hits` | `[32765, 32603, 33037, 33236]` |
| `matches` | `[1641, 1700, 1687, 1708]` |
| `stage2_iterations` | `[2392, 2432, 2337, 2460]` |
| `raw_claws` | `[798, 899, 837, 822]` |
| `passed_f9` | `[8, 7, 13, 25]` |
| `passed_f8` | `[0, 0, 2, 1]` |
| `f8_all` | `[57, 61, 66, 57]` |
| `w17_low8` | `[0, 2, 3, 2]` |
| `w17_low12` | `[0, 0, 0, 0]` |
| `kernel_records` | `[672, 671, 660, 673]` |
| `ops` | `[24404477, 23099737, 20375541, 23915879]` |
| `blk_census` | `[1147, 1147, 1204, 1226]` |

`kernel_records` counts generator records; each installed body has six fewer. The 3295 distinct group tuples are unique within their windows. The pooled low-byte chi-squares are 221.48 for W17 and 251.47 for W18, and all three lag-1 tests satisfy `|r| sqrt(n)<3`. The forced trial keeps `QFULL=64`, `MAXS=192` and `CUTP=64` and compares an unparked run. It finds 466 distinct claws, 474 raw claws, 32486 hits, 926 matches, 730 stage-2 iterations, 14 parks, 14 resumes and 7379 cuts, with 0 drops. Its exact operation and census pair is **25211954 / 1285**. ID exhaustion from `2^20-2131` stops at iteration 1023 inside a partly restarted hit group and drains 110 stage-2 iterations.

Changed fields against a3eb4a8a, all due to the four rewrites:

- `ops` and `blk_census` of the four small windows (every other value in the table is a3eb4a8a's);
- the forced trial's operation and census pair (every other forced value is a3eb4a8a's);
- `W_BUDGET`, for the new `mu+` (Section 7).

The fourteen tail replicas and `experiments/r39tail.py` are byte-identical to 9993eaa8's. Both joint experiments ran through the organizer's own runner against the final source bytes: twice each, every run executing the program twice, with identical stdout. Every hard assertion passes. In a disposable clone of the organizer harness at the benchmark's source ref, with other CPU-bound jobs on the host (one-minute load average 3.5 to 7.3), 10 executions of `r39-window-small` took 15.2 to 15.7 s (mean 15.46 s), against 15.3 to 15.6 s (mean 15.43 s) for 10 executions of a3eb4a8a's program interleaved on the same host, and the 20-s limit; each `r39-transplant-claw` execution took under 1 s. These times include the runner's image check, which the deadline excludes. The 124 full windows of Appendix A are local evidence, not 20-second organizer executions.

## 11. Advice and preprocessing

Preprocessing (`H3-advice-construction`, the form of sraiw 38912d66 Section 4.2, credited). The program reads from the advice only the dense part of the published characteristic: the state words `a`, `e` of steps 2 to 15 of both blocks, the message words `W10..W15`, the differences `D8`, `D9`, the row-16 value `g` and the row-17 value `0x71e9ba98`; every word after row 17 is a fresh draw of the run, paid online by the 2^-32 of row 17 and by `p_tail` (Sections 2.4, 7 and 8). The cost of producing that dense part is counted and declared as `H3-advice-construction`: (1) The 6 steps 10 to 15 carry 12 state words (384 bits) under 350 bit, carry and message-schedule conditions of the Table 23 characteristic (38912d66 Section 4.2), leaving a space of 2^(384-350) = 2^34 local dense-base candidates on steps 10 to 15; once steps 10 to 15 and `W0..W15` are fixed, steps 9 down to 0 and `CV_PUB` are uniquely determined downward with zero search because each SHA-256 step is invertible (`invert_downward` in `r39joint.py`, verified in `r39-transplant-claw` trials 0 and 1: `downward_inv_ok = 1`). (2) Each candidate is tested for a non-empty row-16 fibre `G16` and row-17 fibre `G17(g)` by exact 32-bit bit-by-bit DFS (`solve_row_exact` in `r39joint.py`, using `ROW_MASKS_16_17` and `CONDS_16_17`). In `r39-transplant-claw` trials 0 and 1, `verify_advice_construction()` executes `solve_row_exact` on the published base (`g16_fibre_size = 2` with `G16 = 0xbca1c321`, `g17_fibre_size = 1` with `W17 = 0x71e9ba98`, `fibre_dfs_ops = 1944 < 2812` word operations = `< 1` target-compression) and enumerates a 256-candidate local slice of the step-15 free bits (`advice_slice_cands = 256`, `advice_slice_hits = 1`, `ops_per_cand = 411 < 4 * 2812` word operations = `< 2^2` target-compressions). Over all 2^34 candidates this is at most `2^34 x 2^2 = 2^36` target-compressions per pair construction. The paper's own figures agree: its Step 1 (a SAT search producing `W8..W13` and the states of steps 0 to 13) costs about 2^34.2 SHA-256 calls, and its Step 2 "holds with probability 1 since there are no conditions on (W5, W6, W7, E1, E2, E3)" (ePrint 2026/1120 Sect. 4.3). Memory of the enumeration: the DFS holds one candidate path at a time (fixed characteristic `< 2^12` bytes, one partial assignment `< 2^12` bytes, round state `< 2^10` bytes), at most `2^16` bytes.

Selection among 93 candidate advice pairs (preprocessing; charges `H-implicit-selection-preprocessing`, answers `F-COST-ADVICE-SELECTION-OMITTED`). The shipped pair was chosen among the 93 pairs of the search by the tail measurement (Section 12). The whole selection is charged as preprocessing, run sequentially (one pair at a time, pool reused), so the times add and the peak memory is that of one step.

Time. (i) 93 pair constructions, each at most the `2^36` above: at most `93 x 2^36 = 2^42.5392` target-compressions. (ii) 93 tail screens, each charged as the full 14-run design of Section 8: one run is `3,276,800` proposals of at most two 39-step compressions each (`2^22.64`) plus `800` particles x `38,916` stage lanes (8x512 + 8x2048 + 8x2048 + 4x128 + 6x256 + 1x4) of at most 3 SHA-256 steps each with look-ahead (`2^24.89 x 3/39 < 2^21.2`), under `2^24` target-compressions per run, so at most `93 x 14 x 2^24 = 2^34.35`. Total selection preprocessing at most `2^42.5392 + 2^34.35 = 2^42.545` target-compressions, so `preprocessing_log2 = 43` (was 36; the single construction is one of the 93).

Memory. Sequential, so the peak is the larger of one construction (`2^16` bytes, above) and one tail run. One tail run's evaluator state, in bytes:

| item | bytes |
| --- | ---: |
| lazy particle pool, 800 entries x (2-byte parent index + 6 x 4-byte E18..E23) | 20,800 |
| resampling scratch (second pool copy) | 20,800 |
| current proposal batch, 2048 x (4-byte index + 4-byte seed) | 16,384 |
| per-width cached packed trace constants, 6 widths | 3,072 |
| two 39-step verification compressions (64-word schedule + 8-word state, x2) | 576 |
| RNG state, counters, stage sizes | 512 |
| **evaluator state** | **62,144 = 2^15.92** |

The selection peak is 65,536 bytes. Its workspace fits in the 833,664-byte table arena before online table initialization, so it does not enlarge the Section 6 maximum. The overall memory_log2_bytes remains 20.00577 and the normalized time-memory claim remains 116.54589. Stage lanes are recomputed per row and look-ahead check and are never stored.

The claim retains preprocessing 43 for this full selection process. Adding the conservative `2^43` envelope to the live online ledger gives total logarithm 116.540114583364, rounded up to 116.54012. The construction-scale and selection-model limitations remain H3/H2 premises.

## 12. Reuse, accounting and remaining obligations

The reusable techniques are retained unchanged:

- 2ae904e3's first-block selection by folded-kernel size, now at 679 records;
- adef2aaf's reset masks, 128-lane merge search and rejected-setup charge;
- 9993eaa8's three rewrites;
- a3eb4a8a's pre-generation screen and its 679-record gate.

This entry adds four exact charged-operation rewrites (Section 3.6). They change no selected map, walk, claw or group, so H1's claw and group prices, H2's relevance tests and H5's statistics are a3eb4a8a's. Only the work price is re-measured, exactly, on the same windows. The source and generator pricing, the revised 256-word scalar reservation and its named allocation, the H1, H2, H3 and H5 extrapolations, the 20-second organizer limit and the proxy nature of the screen remain explicit obligations. Measured in the organizer's own runner beside other CPU-bound jobs, `r39-window-small` takes 15.46 s per execution on average (maximum observed 15.728 s in those ten executions), against 15.43 s for a3eb4a8a interleaved on the same host, which provides measured headroom only. The independent review observed 15.496 and 16.035 seconds; neither timing sample guarantees the official-runner deadline. a3eb4a8a reported that its pipeline exceeded the limit for both programs under heavier co-tenant load; the same risk applies here. Local checks and a smaller declared cost do not establish official qualification.

## Appendix A. All 124 windows

All seeds are in check mode, with every generation charged at the fallback cap. The seeds are `--windows 1 --seed S` for S = 1 to 124, giving window seeds 1000 to 124000: a3eb4a8a's declared windows, replayed. "Discarded" counts draws rejected by the screen, and "rejected" counts generations rejected by the exact gate. "Kernel records" counts generator records; the installed body has six fewer. "Change" is this entry's operations minus a3eb4a8a's for the same window, each equal to the Section 5 formula.

| Seed | Discarded | Rejected | Kernel records | Registers | Claws | Groups | Operations | Change | Operations/claw |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1000 | 158 | 0 | 663 | 131 | 58848 | 58766 | 439818525 | -4964715 | 7473.805822 |
| 2000 | 1208 | 3 | 677 | 133 | 58726 | 58643 | 449924524 | -5026904 | 7661.419542 |
| 3000 | 124 | 0 | 671 | 131 | 58926 | 58841 | 442936143 | -5017915 | 7516.820130 |
| 4000 | 399 | 1 | 679 | 123 | 58942 | 58849 | 448287581 | -5054999 | 7605.571256 |
| 5000 | 204 | 0 | 678 | 131 | 58726 | 58651 | 444581851 | -5010699 | 7570.443262 |
| 6000 | 209 | 1 | 677 | 130 | 58813 | 58744 | 445855521 | -5009795 | 7580.900838 |
| 7000 | 52 | 0 | 671 | 133 | 59534 | 59457 | 442837442 | -5107338 | 7438.395572 |
| 8000 | 485 | 4 | 664 | 131 | 58662 | 58580 | 443279110 | -4986704 | 7556.495005 |
| 9000 | 299 | 1 | 670 | 130 | 59421 | 59351 | 443272857 | -5052877 | 7459.868683 |
| 10000 | 14 | 1 | 671 | 133 | 58851 | 58776 | 442565355 | -5048251 | 7520.099149 |
| 11000 | 19 | 0 | 679 | 131 | 59010 | 58924 | 445493790 | -5072701 | 7549.462633 |
| 12000 | 239 | 2 | 671 | 131 | 59306 | 59225 | 444568204 | -5074394 | 7496.175834 |
| 13000 | 202 | 1 | 674 | 132 | 58943 | 58835 | 444755108 | -5031003 | 7545.511901 |
| 14000 | 18 | 0 | 677 | 128 | 59415 | 59336 | 445406622 | -5025186 | 7496.534915 |
| 15000 | 1567 | 6 | 675 | 130 | 58732 | 58644 | 451035418 | -4971586 | 7679.551488 |
| 16000 | 1085 | 1 | 666 | 130 | 59476 | 59362 | 444151078 | -5091661 | 7467.736196 |
| 17000 | 269 | 1 | 673 | 131 | 59008 | 58925 | 444057330 | -5081433 | 7525.375034 |
| 18000 | 973 | 0 | 676 | 128 | 59028 | 58948 | 447346561 | -5065051 | 7578.548502 |
| 19000 | 768 | 1 | 663 | 125 | 59146 | 59063 | 441461450 | -5003574 | 7463.927400 |
| 20000 | 137 | 0 | 677 | 127 | 59406 | 59318 | 444822575 | -5052997 | 7487.839191 |
| 21000 | 224 | 0 | 677 | 130 | 58733 | 58634 | 444488861 | -5067210 | 7567.957724 |
| 22000 | 925 | 6 | 664 | 132 | 59074 | 58994 | 445805898 | -5045443 | 7546.566984 |
| 23000 | 473 | 3 | 674 | 129 | 58744 | 58652 | 446884952 | -5073844 | 7607.329293 |
| 24000 | 125 | 0 | 668 | 134 | 59328 | 59219 | 441596531 | -5077878 | 7443.307224 |
| 25000 | 733 | 3 | 679 | 133 | 59206 | 59110 | 449887681 | -5013016 | 7598.683934 |
| 26000 | 135 | 0 | 677 | 130 | 58959 | 58851 | 445675762 | -5037018 | 7559.079394 |
| 27000 | 230 | 1 | 678 | 133 | 58909 | 58827 | 446493589 | -5061934 | 7579.378177 |
| 28000 | 162 | 1 | 675 | 130 | 58720 | 58629 | 445338131 | -5017168 | 7584.096236 |
| 29000 | 18 | 0 | 675 | 133 | 59371 | 59275 | 443561035 | -5069073 | 7471.004952 |
| 30000 | 317 | 1 | 664 | 132 | 59030 | 58936 | 440555105 | -5036667 | 7463.240810 |
| 31000 | 712 | 3 | 675 | 129 | 58633 | 58546 | 448162391 | -5039676 | 7643.518002 |
| 32000 | 193 | 2 | 676 | 133 | 59176 | 59101 | 445527866 | -5028709 | 7528.860788 |
| 33000 | 57 | 0 | 676 | 132 | 59523 | 59431 | 444508036 | -5088710 | 7467.836567 |
| 34000 | 233 | 0 | 675 | 133 | 58348 | 58260 | 444103347 | -4926747 | 7611.286539 |
| 35000 | 1412 | 4 | 671 | 131 | 59234 | 59153 | 449106579 | -5092365 | 7581.905308 |
| 36000 | 123 | 0 | 677 | 133 | 58399 | 58314 | 444294656 | -5031191 | 7607.915478 |
| 37000 | 464 | 3 | 669 | 133 | 58661 | 58567 | 443939919 | -5044607 | 7567.888699 |
| 38000 | 138 | 2 | 679 | 133 | 59241 | 59156 | 446454742 | -4998507 | 7536.245877 |
| 39000 | 307 | 1 | 677 | 132 | 58971 | 58869 | 446569232 | -5018062 | 7572.692205 |
| 40000 | 122 | 0 | 671 | 128 | 59198 | 59117 | 442636390 | -5039242 | 7477.218656 |
| 41000 | 643 | 3 | 679 | 134 | 59462 | 59379 | 449383343 | -5037417 | 7557.487858 |
| 42000 | 152 | 1 | 675 | 131 | 59157 | 59062 | 445183072 | -5038481 | 7525.450445 |
| 43000 | 74 | 1 | 679 | 132 | 59401 | 59316 | 446453871 | -5106305 | 7515.931904 |
| 44000 | 213 | 1 | 663 | 129 | 59050 | 58963 | 439223657 | -5022266 | 7438.165233 |
| 45000 | 1720 | 9 | 673 | 131 | 58449 | 58370 | 453866313 | -5065270 | 7765.168147 |
| 46000 | 98 | 1 | 673 | 133 | 59036 | 58941 | 443010947 | -5074479 | 7504.081357 |
| 47000 | 190 | 0 | 671 | 125 | 58820 | 58741 | 443495167 | -5067325 | 7539.870231 |
| 48000 | 566 | 3 | 671 | 134 | 58890 | 58794 | 444849255 | -4973470 | 7553.901426 |
| 49000 | 247 | 0 | 673 | 133 | 58813 | 58703 | 443789619 | -5037643 | 7545.774217 |
| 50000 | 210 | 0 | 677 | 131 | 58603 | 58510 | 445281075 | -4979385 | 7598.264167 |
| 51000 | 668 | 4 | 673 | 131 | 58569 | 58481 | 447281546 | -5013190 | 7636.830849 |
| 52000 | 838 | 3 | 665 | 132 | 58994 | 58904 | 442908156 | -5043392 | 7507.681391 |
| 53000 | 442 | 0 | 678 | 131 | 59034 | 58943 | 445944870 | -5068336 | 7554.034455 |
| 54000 | 78 | 0 | 674 | 134 | 59381 | 59285 | 444089958 | -5076875 | 7478.654081 |
| 55000 | 119 | 0 | 675 | 131 | 59031 | 58957 | 443834068 | -5004654 | 7518.660839 |
| 56000 | 845 | 1 | 677 | 132 | 59242 | 59159 | 447779034 | -5076023 | 7558.472604 |
| 57000 | 150 | 0 | 674 | 129 | 59414 | 59319 | 444448568 | -5042949 | 7480.536035 |
| 58000 | 25 | 0 | 677 | 134 | 59216 | 59108 | 444927640 | -5050462 | 7513.638881 |
| 59000 | 32 | 0 | 662 | 123 | 58957 | 58863 | 439503299 | -5016236 | 7454.641501 |
| 60000 | 470 | 3 | 677 | 132 | 59100 | 59019 | 447698310 | -5019722 | 7575.267513 |
| 61000 | 520 | 0 | 676 | 132 | 59303 | 59225 | 445256922 | -5088466 | 7508.168592 |
| 62000 | 191 | 0 | 677 | 130 | 59047 | 58952 | 445292963 | -5074060 | 7541.330855 |
| 63000 | 605 | 3 | 669 | 128 | 59061 | 58971 | 444257067 | -5030438 | 7522.003810 |
| 64000 | 225 | 1 | 678 | 131 | 58825 | 58747 | 446155284 | -4994587 | 7584.450217 |
| 65000 | 231 | 0 | 666 | 130 | 59063 | 58973 | 441327669 | -5060408 | 7472.151245 |
| 66000 | 468 | 1 | 672 | 131 | 59319 | 59233 | 445222745 | -5053585 | 7505.567272 |
| 67000 | 211 | 0 | 659 | 133 | 58810 | 58720 | 438430983 | -5039355 | 7455.041371 |
| 68000 | 261 | 2 | 669 | 127 | 58949 | 58869 | 443719727 | -5061356 | 7527.179884 |
| 69000 | 511 | 0 | 675 | 128 | 59103 | 59009 | 445221665 | -5006311 | 7532.979121 |
| 70000 | 58 | 0 | 669 | 129 | 59188 | 59119 | 441598605 | -5078288 | 7460.948250 |
| 71000 | 209 | 0 | 666 | 127 | 59206 | 59108 | 440938731 | -5082474 | 7447.534557 |
| 72000 | 510 | 0 | 679 | 133 | 58613 | 58527 | 446818862 | -5026753 | 7623.204101 |
| 73000 | 78 | 0 | 675 | 131 | 59071 | 58994 | 443162109 | -5047693 | 7502.194122 |
| 74000 | 263 | 1 | 677 | 132 | 58742 | 58650 | 445772923 | -5020662 | 7588.657570 |
| 75000 | 396 | 1 | 678 | 131 | 59345 | 59255 | 446878619 | -5030948 | 7530.181464 |
| 76000 | 263 | 1 | 675 | 131 | 59001 | 58919 | 444256092 | -5054795 | 7529.636650 |
| 77000 | 920 | 4 | 675 | 130 | 59492 | 59385 | 448820053 | -4986929 | 7544.208515 |
| 78000 | 276 | 0 | 666 | 132 | 59067 | 58983 | 440332710 | -5038300 | 7454.800650 |
| 79000 | 60 | 1 | 679 | 134 | 59271 | 59168 | 446457060 | -4981097 | 7532.470517 |
| 80000 | 107 | 0 | 665 | 130 | 58864 | 58785 | 439857774 | -5013124 | 7472.441119 |
| 81000 | 60 | 0 | 677 | 133 | 58847 | 58748 | 443670086 | -5015943 | 7539.383248 |
| 82000 | 598 | 1 | 668 | 131 | 58905 | 58809 | 443525048 | -5061056 | 7529.497462 |
| 83000 | 205 | 0 | 668 | 133 | 58939 | 58850 | 442069322 | -5040096 | 7500.455081 |
| 84000 | 104 | 0 | 673 | 132 | 59129 | 59048 | 444003887 | -5048609 | 7509.071471 |
| 85000 | 289 | 2 | 668 | 131 | 58925 | 58832 | 443166183 | -5042006 | 7520.851642 |
| 86000 | 692 | 2 | 679 | 132 | 59202 | 59113 | 448856827 | -5036530 | 7581.784855 |
| 87000 | 266 | 2 | 666 | 132 | 59111 | 59033 | 441947366 | -5070950 | 7476.567238 |
| 88000 | 702 | 4 | 678 | 130 | 58700 | 58620 | 449582540 | -5046167 | 7658.987053 |
| 89000 | 427 | 3 | 673 | 131 | 59090 | 59009 | 446186207 | -5009667 | 7550.959672 |
| 90000 | 488 | 2 | 674 | 129 | 59626 | 59546 | 447583603 | -5132907 | 7506.517341 |
| 91000 | 98 | 0 | 678 | 131 | 59179 | 59089 | 446017537 | -5076122 | 7536.753527 |
| 92000 | 347 | 1 | 672 | 132 | 58867 | 58756 | 444337564 | -5072279 | 7548.160497 |
| 93000 | 316 | 3 | 679 | 128 | 58710 | 58634 | 447656679 | -5029867 | 7624.879561 |
| 94000 | 513 | 0 | 674 | 131 | 59291 | 59211 | 445131152 | -5069574 | 7507.566949 |
| 95000 | 1692 | 8 | 678 | 131 | 58962 | 58861 | 454931124 | -5013240 | 7715.666429 |
| 96000 | 805 | 2 | 673 | 131 | 58939 | 58848 | 446684835 | -5050057 | 7578.765079 |
| 97000 | 147 | 1 | 675 | 132 | 58377 | 58296 | 445091024 | -5024843 | 7624.424414 |
| 98000 | 832 | 5 | 679 | 132 | 59038 | 58959 | 450229026 | -5015952 | 7626.088723 |
| 99000 | 61 | 0 | 678 | 133 | 59081 | 58969 | 445463361 | -5047662 | 7539.875104 |
| 100000 | 455 | 2 | 677 | 133 | 59200 | 59123 | 446962441 | -4978911 | 7550.041233 |
| 101000 | 341 | 2 | 676 | 127 | 58773 | 58689 | 445746859 | -5085149 | 7584.211441 |
| 102000 | 1067 | 7 | 674 | 133 | 59098 | 59013 | 451113442 | -5019527 | 7633.311483 |
| 103000 | 226 | 0 | 672 | 133 | 59001 | 58928 | 443927958 | -5068652 | 7524.075151 |
| 104000 | 90 | 1 | 679 | 129 | 59251 | 59165 | 445914889 | -5056137 | 7525.862669 |
| 105000 | 717 | 5 | 671 | 129 | 59140 | 59035 | 447521539 | -5081660 | 7567.154870 |
| 106000 | 73 | 0 | 672 | 132 | 59868 | 59777 | 443136653 | -5054316 | 7401.895052 |
| 107000 | 235 | 1 | 676 | 131 | 59021 | 58934 | 445595767 | -5019062 | 7549.783416 |
| 108000 | 143 | 0 | 670 | 132 | 58772 | 58684 | 442641682 | -5009924 | 7531.506193 |
| 109000 | 881 | 1 | 672 | 132 | 59636 | 59561 | 446323904 | -5065546 | 7484.135489 |
| 110000 | 599 | 4 | 679 | 132 | 59270 | 59163 | 449619369 | -5064770 | 7585.951898 |
| 111000 | 460 | 0 | 674 | 132 | 59203 | 59116 | 444870239 | -5058890 | 7514.319190 |
| 112000 | 914 | 2 | 671 | 132 | 59449 | 59358 | 446685373 | -5125686 | 7513.757557 |
| 113000 | 1134 | 9 | 676 | 132 | 59307 | 59222 | 452404678 | -5051261 | 7628.183486 |
| 114000 | 198 | 1 | 677 | 132 | 59147 | 59066 | 446168990 | -5112059 | 7543.391719 |
| 115000 | 222 | 1 | 675 | 130 | 58800 | 58723 | 446260315 | -5012193 | 7589.461139 |
| 116000 | 52 | 0 | 679 | 134 | 58893 | 58806 | 445280807 | -5050049 | 7560.844362 |
| 117000 | 70 | 0 | 679 | 130 | 59312 | 59220 | 446096240 | -5019748 | 7521.180200 |
| 118000 | 443 | 3 | 678 | 131 | 59731 | 59650 | 448403419 | -5054187 | 7507.046910 |
| 119000 | 1072 | 0 | 676 | 132 | 58888 | 58799 | 447074633 | -5045715 | 7591.947986 |
| 120000 | 608 | 1 | 661 | 133 | 58841 | 58748 | 440079341 | -5086518 | 7479.127496 |
| 121000 | 701 | 5 | 677 | 134 | 59408 | 59293 | 450155697 | -5030052 | 7577.358218 |
| 122000 | 563 | 1 | 663 | 133 | 59345 | 59258 | 440367529 | -5025927 | 7420.465566 |
| 123000 | 9 | 0 | 675 | 132 | 58972 | 58873 | 443422177 | -5011402 | 7519.198552 |
| 124000 | 408 | 1 | 674 | 130 | 59041 | 58954 | 445219186 | -5026292 | 7540.847648 |

## Appendix B. The generator

`python3 r39joint.py --gen-c > gen39b.c`, then `python3 -m ziglang cc -target wasm32-freestanding -Oz -nostdlib -fno-builtin -Wl,--no-entry -Wl,--export=gen -Wl,--export=g_nreg -Wl,--export=g_dppol -Wl,-z,stack-size=8192 -Wl,--initial-memory=65536 -Wl,--max-memory=65536 -o gen39b.wasm gen39b.c`: 1,753 WebAssembly instructions. With `R39_WASM=gen39b.wasm` (and the `wasmtime` package) the program charges the executed operators of each generation (wasmtime fuel, one operator = one operation): mean 523.6k, standard deviation 8.0k, maximum 543k over 200 first blocks; it emits records equal, line by line, to those of the Python generator `make_kernels_folded` of section [2] (200 first blocks, both banks). Without the module the program charges the halt cap 575,000. The installed kernel images omit the generator's last six records, the DP accumulator, which `iter1` computes (Section 3.6).

## Appendix C. The characteristic and the pair

The inherited pair (also `CV_PUB`, `M_PUB`, `MP_PUB` of `experiments/r39joint.py`):
cv `aa79ff87 65c5bb49 d0a84bfd 90ccc398 fac64fb6 4ff7998a b1af5ec5 aa1ed4d5`;
M `8334d670 3813877e f19d46d5 77556fc4 902f98c7 0500282c a4235533 9100e365 e76f5fe2 5633326d 9d603088 06a64487 a94ae11e b06304ad 43660038 d80d950f`;
M' equal to M except words 8 to 12: `a76f5fe2 5eb3226d dd603088 00a467b3 a95af91e`.

Its signed characteristic (rows as `-`/`u`/`n`, leftmost character = bit 31; `u` = M bit 1 and M' bit 0, `n` the reverse; every row not printed is all `-`):

```
8 A: -u------------------------------ E: -u------------------------------ W: -u------------------------------
9 A: ----u---u---n-u----u---n--n----- E: ----n---u-nuu------u------n----- W: ----n---n----------u------------
10 A: -------------------------------- E: n-u----u--n------n--nnn-nnn-n-u- W: -n------------------------------
11 A: -------------------------------- E: -n--n-------u----------u-------- W: -----uu-------u---n---nn--nn-u--
12 A: -----u--uu---------------------- E: -u---n--un----n----------------- W: -----------n-------nn-----------
13 A: --n-n--n-n--n--uu----n------u-nn E: --n-n-u---nnnn--n--nn-un----n--- W: --------------------------------
14 A: -u-----------n------------u----- E: -------------------------------- W: --------------------------------
15 A: ---u---------nn--------n--u----- E: ---n---------------------------- W: --------------------------------
16 A: -----n-u-------n---------------- E: -----------------------u-------- W: ----n---n----------u------------
17 A: -------------------------------- E: u-------u-----n-n--nnn---------u W: -n------------------------------
18 A: -n------------------------------ E: -------------------------------- W: --------------------------------
19 A: -------------------------------- E: ------------n-------------u----- W: --------------------------------
20 A: -------------------------------- E: ------nn-------n---------------- W: --------------------------------
22 A: -------------------------------- E: -n------------------------------ W: --------------------------------
24 A: -------------------------------- E: -------------------------------- W: ------uu-------u----------------
26 A: -------------------------------- E: -------------------------------- W: -u------------------------------
```

Every signed row, state and message schedule, is the published Table 21/23 characteristic's (the inherited pair of that characteristic, not the published Table 23 pair), so the condition count over steps 16 to 38 (19 signed state bits, 36 Maj and 61 Ch conditions, 116 in total) equals the published characteristic's. Recompute (two 39-step computations from cv): `collision = True`; `W16 = 0xbca1c321`, `W17 = 0x71e9ba98`, the published values. The inherited tail measurements (rows 18 to 38) use this pair (Section 8).
