# SHA-256 reduced to 39 steps: ordinary collision by the transplanted Table 23 pair with a released third state word, a row-16 claw search and a bit-sliced re-try of W17

Halley, 2026-11-07. Final numbers are frozen at 20:07 from 9 full CVs (Appendix A). This is not filed; the filing agent files. Every number inherited from the r39 entry is cited to R39_ACCEPTED_TERMS.txt ("RAT", l.N). Every new number is cited to the experiment or tool that produced it.

## 1. Target and output
- **Target.** SHA-256 compression reduced to 39 steps, standard IV.
- **Output.** Two 2-block messages (M0 || M1, M0 || M1'), with the same random first block M0. They collide after the second 39-step compression. This is an ordinary collision with no chaining-value difference (HashSmash.md l.164).
- **Inheritance.** The attack class, the advice and the walk are those of our r39 entry 5f8e6192 (RAT l.2-3), which is judge-valid and not yet human-accepted (RAT l.1).
- **Padding.** Each message is 128 bytes (two 64-byte blocks). SHA-256 padding appends a third block that is the same for both messages, since their lengths are equal. Equal chaining values after block 2, pushed through the same padding block, give equal digests. So the collision of the second 39-step compression carries through to a collision of the 39-step hash.

## 2. The construction
**2.1 The advice.** The advice is the 39-step semi-free-start pair of ePrint 2026/1120, Table 23 (CV_PUB, M_PUB, MP_PUB), 160 bytes. It is the same as r39 (sraiw 38912d66, dariolina; RAT l.3). Its trajectories are BA, BE (message MP_PUB = BW).

**2.2 The transplant with A[6] released.** Fix A[7..10], E[11..14] and W11..W15 to the published values of MP_PUB. For any chaining value cv and any (a0, a1, x):
- Steps 0-6 determine W0..W6 from the A registers and give E[4..10].
- Steps 7-10 determine W7..W10 from the fixed E[11..14] (`k3_words`). A[6] = x is free.
- At x = BA[6] this is r39's `build` exactly. `--k3selftest` checks this on 200 random (cv, a0, a1).
- A[7] is not free. With E[11] and A[11] published, step 7 forces A[7] = E[11] - A[11] + S0(A[10]) + MAJ(A[10], A[9], A[8]).
- The partner block is M1' = M1 + DL, word-wise modular, with DL = M_PUB - MP_PUB (non-zero on words 8..12; `k3_second`). This is r39's `second()`, except that W10' = W10 + D10 for the changed W10.

**2.3 Row 16 is a claw.** This is unchanged from r39.
- W16 = s1(W14) + W9 + s0(W1) + W0. W0 and W1 do not depend on x.
- W9 = C - a1 + h(x), with h(x) = MAJ(A8, A7, x) - CH(E12, E11, x + t1(6)). This identity was checked numerically, with 0 mismatches in 2,000 trials (enum_a2_gen.py).
- For every listed x, h(x) = h(BA[6]). So W16 = g holds exactly when r39's claw condition F(a0) = F(u) does, with a0 even and u odd.

**2.4 What remains to pay, after a claw.**
- **Once per claw:** W9 in F9 (r39's F9; W9 is the same for every listed x).
- **Per listed x:**
  - (i) W8 in F8 (r39's F8).
  - (ii) W10 in F10 = { w : s0(w + D10) - s0(w) = s0(BW10 + D10) - s0(BW10) }. W10 = c10 - E10(x) depends on x only, so every listed x passes by construction.
  - (iii) W17 = 0x71e9ba98. W17 = s1(W15) + W10 + s0(W2) + W1, with W2 = x + c2(a0, a1), so the listed x give distinct W17 values (k3neutral_all.py).
- **The tail:** rows 18-38 (Section 8).
- **Implication.** W16 = g, W9 in F9, W8 in F8, W17 = published, x listed, and the tail event together give a collision. The program confirms each candidate by compressing both blocks.

**2.5 The list.**
- All x in [0, 2^32) with h(x) = h(BA[6]): 69,888 values, from an exhaustive scan (tools/enum_a2.c).
- Of these, 4,886 put W10 in F10.
- 70 of those break the state-difference trail at step 9. The message-2 increment at step 9 contains CH(E12, E11, E10) at the bits where E12 differs, and E10 = x + t1(6). These 70 are removed (tools/k3trail4.py).
- The list therefore holds the base plus 4,815 variants.
- **Shipped form.** The list is stored delta+zlib+base85 in 172 bytes (`_k3dec`) and decoded at import. It is asserted equal to tools/a2ok.txt by sha256. 4,816 arbitrary 32-bit values could not fit in 172 bytes. These do because they are a structured set, the solutions of h(x) = h(BA6), whose sorted gaps repeat heavily.
- **Independent regeneration (offline).** A bit-serial search over the carry of x + t1(6) and the borrow of MAJ - CH finds all 69,888 solutions without a 2^32 scan. The F10 test and the trail check at the published point then reproduce the same list. This is tools/mk_r39k3.py's `_k3_regenerate`, about 28.0M operations, 2^13.2 compressions.
- `--k3selftest` re-verifies each entry: h, F10, W9, W16, and the trail through step 15 at the published point and 2 random points.
- An independent reviewer's own SHA-256 code reproduced the trail on random listed x.

## 3. The program
- `r39joint_k3.py` is r39joint.py plus asserted text patches (tools/mk_r39k3.py).
- With k3 off, every r39 code path and hard assert is unchanged. Verified on r39's WIN_EXP seeds.
- With k3 on, after each claw that passes F9, `k3_eval` tries the 4,815 variants in 19 bit-sliced blocks of 256 lanes.
- Per block: E10, MAJ(A7, x, a1), E8, MAJ(A8, A7, x), E9, CH with E11 folded, W8, the F8 test as s0(W8 + D8) = s0(W8) + T8, W2, s0(W2), W17, the compare with the published W17, and a branch on the combined lane mask.
- Global constants derived from the advice are folded, as in r39's folded kernels.
- Per-claw values a0 + A8 - S0(A7), a1, A7|a1, A7&a1, W2 - x and W1 are broadcast at 3 operations per bit, charged.
- Every passing lane builds the pair and compresses both blocks. That costs 2 x 2812 + 400 operations, plus 16 for lane location.
- In check mode, every lane is asserted against `k3_words`.

**3.1 Every loop is bounded.** Line numbers are in the shipped r39joint_k3.py.
- **Stage-2 loops (l.730 and l.737).** These are r39's, unchanged.
  - The outer `while True` (l.730) runs one stage-2 kernel iteration per pass (it2 += 1). It exits when no lane is live (`if m.jz(live): break`) or when the call suspends with no pending work (`if sp: break`).
  - r39's worst-case argument (r39 proof Section 5, "Every window has a worst-case cost (R)") applies unchanged. A trail is at most MAXS + CUTP = 3,072 iterations long, a window has at most 2^26 pairs, and each stage-2 call has at most 3,072 partly filled iterations. Hence the charged work of a window is at most R = 2^51 operations.
  - R is a termination bound and is not an extra cost. The ledger charges what windows actually execute: r39's accepted 8,331 ops per claw, about 491M per window, plus the measured k3 pass. R only shows that no window can run unbounded.
  - The inner `while True` (l.737) walks the callback chain of one wheel slot. Each pass consumes one record (head = next index), and the loop stops when the next index is 0 (`if not m.jnz(head): break`). It is bounded by the 256 records in `rec`.
- **List decoder (l.924, l.926; new).** The outer loop runs once per varint byte of a finite string. The inner loop reads one varint, at most 5 bytes for a 32-bit delta.
- **k3 pass (l.1031; new).** `while m.jnz(hm)` clears one set lane bit per pass, so it runs at most 256 times per block.
- **Other loops.** `--k3selftest` (l.1068) samples random points until 6 pass F9, about 1 in 60 per draw; it is not part of any experiment. `--attack` (l.1122) is bounded by the window count B and the work budget.

**3.2 Files.** The program is r39joint.py with these changes:
- the k=3 block;
- the list stored delta+zlib+base85 (172 bytes), decoded at import and asserted equal to the shipped list by sha256;
- GEN_C moved verbatim to the supporting file r39_gen.c, which `--gen-c` still prints. The generator runs from the wasm file, never from GEN_C.
- r39-window-small's trial-4 harness `_t4` removed. r39-window-small is not in this manifest (the organizer allows at most 16 experiments); its figures are r39's accepted ones (RAT), and r39k3-window-small runs the same window code.

Deviations from the accepted r39joint.py, for the implementation-versus-paper check (l.322):

| change | where | reason | effect on r39's experiments |
|---|---|---|---|
| `_t4` and T4_EXP deleted; `_e2` trial 4 returns None | r39joint.py l.1018, l.1041-1055 | 64 KiB experiment-source limit; trial 4 is not in the manifest | none for trials 0-3. T4_EXP was used only inside `_t4`, and no WIN_EXP assert refers to it (checked: no remaining reference) |
| GEN_C moved verbatim to r39_gen.c | r39joint.py l.338 | 64 KiB limit; GEN_C is only printed by `--gen-c`, and the generator runs from the wasm file | none. `--gen-c` prints r39_gen.c byte-identically |
| Attack.__init__ takes k3=False; claw() calls k3_eval after the F9 test when k3 is on; main passes --k3 | three one-line patches | the k=3 pass | none with k3 off. r39's WIN_EXP and transplant asserts pass |
| new experiment id, `--k3selftest`, `--attack --k3` | serve() and main() dispatch lines | the k=3 experiments | none for r39's ids |

Experiment sources: r39joint_k3.py 51,716 B + r39tail.py 13,306 B = 65,022 B, under the 65,536 B limit.

## 4. Machine model and prices
These are those of r39: a counted word RAM of 256-bit words, one operation per primitive, a load or store at 3, a branch at 2, and 2812 operations per compression. Every operation goes through the class `Mach`, and `m.o` counts them.

## 5. The ledger
| term | value | source |
|---|---|---|
| r39 ops per distinct claw | 8,331.0 (RAT l.6) | accepted. This program's own base measures about 7,800 per claw in 12 full windows; the accepted figure is kept |
| k3 pass per distinct claw | 695.5 | 12 full windows, r39joint_k3.py --windows --k3. 39.6M-44.6M ops per window. Includes the pass on duplicate raw claws (1.18 raw per distinct) and 462,240 ops per window for list setup |
| ops per claw | 9,026.5 = 3.210 compressions, term +1.6826 | |
| W17 tries per distinct claw, E[N] | 5.372239, the one-sided 99% Student-t lower bound over 9 full CVs (mean 5.374402, s.d. 0.002240, t(8) = 2.896) | k3pair2: every claw of each first-block CV, enumerated (Appendix A) |
| W17 | 32 | |
| tail | 74.3238 (RAT l.4) | unchanged; Section 8 |
| successes needed | -1.0166 (lambda = 0.494, P = 0.39; RAT l.5) | |
| **time** (log2 target compressions; the scalar objective) | **104.5643** | -log2(5.372239) + 32 + 74.3238 + 1.6826 - 1.0166 |
| **Pareto score** (normalizedTimeMemoryLog2 = time + max(0, memory_log2 - 20)) | **104.5893** | memory 1,066,884 B = 2^20.0250 (Section 6) |

## 6. Memory
- r39's 1,047,428 bytes (RAT l.8), plus the bit-sliced list: 19 blocks x 32 planes x 32 bytes = 19,456 bytes.
- Total 1,066,884 bytes = 2^20.025 (log2 = 20.02497, rounded up). Under normalizedTimeMemoryLog2 that adds +0.025.

## 7. Success probability and time
- lambda = B x groups per window x E[N] x 2^-32 x p_tail, and P = 1 - exp(-lambda) = 0.39.
- **Windows needed:** B = 0.494 / (58,959.42 x E[N] x 2^-106.3238) = 2^87.034 at E[N] = 5.372239. The program's `k3_budget` gives the same: windows 2^87.034, work budget 2^116.022 operations.
- **Why successes stay Poisson:**
  - Within a claw at most one variant can pass W17: the W17 values are distinct, each passing with probability 2^-32, over at most 4,815 variants.
  - Across claws, the trials are independent as in r39 (H5).
- **Duplicates.** A duplicate raw claw repeats its variants exactly. The yield is therefore counted per distinct claw, from enumerations, and the in-program counter is not used.
- **Run limit.** `--attack --k3` runs until it finds a collision or uses up B windows and the matching work budget (`k3_budget`, from K3_EN_LB).

## 8. The tail p_tail
- p_tail >= 2^-74.3238, r39's figure (RAT l.10).
- **Variant regime.** The variant points change W2..W8 and W10. W10 takes one of the 4,816 listed values.
- **Replica.** The replica r39tail.py was patched by asserted text edits (tools/mk_tailk3*.py). W10 is drawn per lane from the list, or (W8, W10) is drawn jointly from 57,646 real variant pairs, using a separate random stream.
  - Carrier particles and W8/W9 lanes are identical to the advice arm (same seeds).
  - 14 runs per arm, kat = 1 on all.
  - Advice arm 6,242 verified collisions; list arm 6,265 (ratio 2^+0.005); joint arm 6,276 (2^+0.008); s.d. 0.026.
- The tail term is stated as "no change": the measured ratios (+0.005 to +0.033 across the 419-variant and 4,815-variant arms, s.d. 0.026) are within noise. No credit is taken, and the term stays 74.3238. The measured ratio is favourable, so not applying it is conservative.

## 9. Premises
- **H1 claw model.**
  - r39's parts (a)-(d) apply (RAT l.9).
  - Extension: each listed x passing F8 is a trial for W17 = published and for the tail.
  - W17 is uniform over (claw, x).
  - E[N] is measured in regime: real claws, all of them, at random two-block CVs.
- **H2 tail.** p_tail >= 2^-74.3238 also on variant points (Section 8).
- **H3 advice construction (CHANGED).** A[6] is released, and the list replaces the single value BA[6]. The step-function identity holds through step 15 for every listed x (Section 2.5). End-to-end pairs confirm rows 0-17 (Appendix B).
- **H5 group independence.**
  - Across claws: as in r39.
  - Within a claw: at most one W17 hit.
  - Assumed, not proved: tail independence across claws that share one of the 4,816 W10 values.

## 10. Experiments
- `r39-transplant-claw` keeps r39's hard asserts.
- `r39k3-window-small` (pass on, check mode):
  - It hard-asserts K3_WIN_EXP on r39's 4 WIN_EXP seeds; claws, F9, F8F9, lanes, F8 lanes, W17 hits, k3 ops and total ops are all deterministic.
  - In check mode, every lane is asserted against `k3_words`.
- `--k3selftest`: the list, the k=2 equivalence, and the bit-sliced pass against the model.
- Offline tools (shipped):
  - enum_a2.c: completeness.
  - k3trail4.py: the filter.
  - realclaw.py: yield on real claws.
  - k3pair2.c + k3verify.py: full-CV enumeration and an independent check of every W17 hit.
  - mvariant5.py: the bit-sliced op count.
  - the replica arms.
  - price.py and final_price.py: the ledger.

## 11. Advice and preprocessing
- **Advice:** 160 bytes, as r39.
- **Preprocessing:** r39's (RAT l.5), plus building the list once, offline: the bit-serial search, about 2^13.2 compressions, or the exhaustive 2^32 scan (enum_a2.c), about 2^23.9. Both are shipped as tools. The program carries the 172-byte encoded list, and `--k3selftest` re-verifies every entry.

## 12. Credits and novelty
- Built on sraiw 38912d66 and dariolina (r39), and on our r39 entry 5f8e6192.
- Neither r39 proof.md (d90878ff, lamb356) mentions releasing A[6], neutral bits or amortisation. ePrint 2026/1120 mentions message modification only in its introduction.
- Earlier team censuses ("neutral bits 0/512", LEVERS_sha256_slice l.48) tested flips that keep every paid condition, including W17. That is a different property from the one used here.

## l.325 table
| part | status |
|---|---|
| list completeness (2^32 scan) | executed (enum_a2.c; reproducible in seconds) |
| list validity (h, F10, W9, W16, trail through step 15) | executed (--k3selftest) and independently reproduced (reviewer's own SHA-256) |
| bit-sliced pass equals the model | executed (check mode, every lane; 161M lanes in k3pair2's cross-check) |
| ops per claw | executed (12 full windows) and recomputed (ledger) |
| E[N] | executed (k3pair2: every claw of each of 9 CVs, 9.66e9 claws; 99% lower bound 5.372239) |
| end-to-end prefix pairs, rows 0-17 | executed (k3pair2 hits, k3verify; judge's independent SHA-256) |
| tail on variant points | executed (3 paired replica arms) |
| W9 identity, W10 = c10 - E10(x), A[7] pinned | proved by hand; W9 also checked numerically |
| cross-claw independence (H5), W17 uniform over (claw, x) beyond the tested bits | assumed |
| organizer-style reproduction | executed 2026-11-07 19:48 on the delivered 51,716-byte program (sha256 4d8db921f47679df...) from a fresh copy of the package folder, `python3 -I`, no absolute paths, 47 s total (first run 19:15 on the earlier 97,998-byte form). --k3selftest OK. r39k3-window-small (4 hard-asserted seeds), r39-window-small (pass off) and r39-transplant-claw trials 0-3 all rc 0. enum_a2 regenerates a2all.txt and k3trail4 regenerates a2ok.txt byte-identically. mvariant5 reproduces 7.56 ops per variant, 0 mismatches. |

## Appendix A. Full-CV E[N] (k3pair2; every claw of each first-block CV, cv = 39-step compress(IV, random M0))
| CV | E[N] |
|---|---|
| cv1 | 5.37291 |
| cv2 | 5.37358 |
| cv3 | 5.37557 |
| cv4 | 5.37314 |
| cv5 | 5.37670 |
| cv6 | 5.37618 |
| cv101 | 5.37524 |
| cv102 | 5.37646 |
| cv103 | 5.36983 |

- 9 CVs, 9,663,607,751 claws in total.
- Controls: 0 claws with W16 != g. About 80M lanes per CV were cross-checked against the full model, with 0 mismatches.
- W17 hits: 10, all k3verify PASS, against 12.09 expected.
- Lower bound: mean 5.374402, s.d. 0.002240; the one-sided 99% bound with t(8) = 2.896 is 5.372239.
- **Pre-registration deviation.** The bound was pre-registered over 24 CVs. It was frozen at the 9 complete CVs on the owner's request to file.
  - Stopping after seeing the data is optional stopping, so this is not conservative by construction.
  - It is immaterial in practice. The per-CV spread is 0.04% (s.d. 0.002240 on 5.3744), so any 24-CV bound differs by about 0.001 bit or less. The estimate at 24 CVs is about 104.5640.
- **Commitment.** The 24-CV bound will be published when the remaining 15 CVs finish. If it falls below 5.372239, the price will be revised.
## Appendix B. End-to-end prefix pairs (K3_PREFIX_PAIRS_CV2.md and later CVs)
- **Which differences k3verify compares:**
  - State differences are XOR: A ^ A', E ^ E'.
  - Expanded-word differences are modular: (W' - W) mod 2^32.
  - The PASS criterion is the XOR state trail through step 17, plus the modular word differences through W17, plus the paid conditions.
- **The two CV-2 pairs:** their XOR word differences differ from each other at W8 (0x40000000 vs 0xC0000000, the same modular D8 with a different carry) and at W24 (0x050F0000 vs 0x03010000). Their modular word differences agree through W25, and their XOR state trails agree through step 18.
- **The judge's check:** reproduced W16 = g, W17 = W17PUB and the state trails with independent SHA-256 code.
- **Status:** these are prefix pairs, not collisions; the tail (rows 18-38) is unpaid.
