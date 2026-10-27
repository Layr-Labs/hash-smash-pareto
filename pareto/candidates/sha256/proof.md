# SHA-256 reduced to 39 steps: ordinary collision by a transplanted semi-free-start pair on a re-signed 39-step characteristic, a row-16 claw search and a bit-sliced 256-lane walk

Target `sha256-r39-prefix-v1`. Claim: `time_log2` = 118.2659 target-compressions, `memory_log2_bytes` = 20 (1,047,548 bytes, the 160-byte advice included), success probability at least 0.39, `preprocessing_log2` = 37 (Section 11), advice 160 bytes.

Credit. The attack is the construction of sraiw's 38912d66 (the transplant of a 39-step semi-free-start pair onto a random first block, the exact bijection, the row-16 claw, the exact side conditions F8 and F9, the dual-parity fibre) built on dariolina's row-16 claw idea (21b6653a, 1d3f2c3c, 2c48b18c, cfe5c4e2, 4e396742) and on her preregistered tail methodology. The word-RAM cost convention comes from dariolina's 744875ec and our 3c1d7f68, 368d1718, 01e31be9; the 5-byte record convention is dariolina's 6b678689 and our 0c1ef7c3. The program, ledger and table are those of our entry bb21016d; lamb356's accepted 44870635 is the accepted entry of this construction. The contribution of this entry is a NEW 39-step signed characteristic (W11 and W12 re-signed, Section 2.1 and Appendix C) with a pair conforming to it, found by row-release/re-sign valuation at full 32-bit width; the valuation method is Kepler's (characteristic-guided SAT valuation, an outside researcher working with us), and the 32-bit support screens it builds on are Dariia Porechna's (co-author). The tail is re-measured on the new advice (Section 8). Everything below was written and re-derived by us from the construction; no code of any other participant was run, imported or compiled.

## 1. Target and output

SHA-256 with 39 steps in every compression, FIPS 180-4 padding, the standard IV, feed-forward after step 38, all 256 digest bits. The output is two distinct 128-byte messages `M0 || M1` and `M0 || M1'`: the same first block, second blocks that give the same chaining value after the second compression; the padding block that follows is identical, so the two digests are equal. The first block `M0` is a random block, `cv = compress39(IV, M0)`.

## 2. The construction (sraiw 38912d66, dariolina)

**2.1 The base is advice: a new pair on a new signed characteristic (the contribution).** The advice is our 39-step semi-free-start collision: a chaining value `CV_PUB` (8 words) and two blocks `M'` and `M` (16 words each), 160 bytes, printed in `experiments/r39joint.py` section [1] (`CV_PUB`, `M_PUB`, `MP_PUB`; the names are kept from the program of bb21016d). Its signed characteristic is the 39-step characteristic of ePrint 2026/1120 (Table 21) with a different signed expansion of two message words: the modular differences of every word and the signed A and E rows of every step are the same, but `W11` carries 14 signed bits (XOR difference `0x1a026ddc`) instead of 9 (`0x06022334`), both with modular difference `0x0601dcd4`, and `W12` carries `0x00102800` instead of `0x00101800`, both `0xffefe800`. Different signed bits are different bit conditions on `W11` and `W12`, so the characteristic is a different one (Appendix C prints it, with the pair and its recompute) and the pair is a different dense solution: its chaining value, `W0..W15` and states before step 8 (A) and step 12 (E) differ from the published Table 23 pair; its A words after steps 8 to 17, its E words after steps 12 to 17, `W16 = 0xbca1c321` and `W17 = 0x71e9ba98` equal the published ones. It is a collision of the 39-step compression from `CV_PUB` (experiment `r39-transplant-claw`, trial 0; our `compress39` equals the organizer's `verifier/hash_functions.py` on 300 random blocks). Its trajectories `BA, BE` (message `M'`) and `CA, CE` (message `M`) are expanded from the 160 bytes by two compressions at the start of the run (charged 2 x 2812 + 120 operations, `Attack.base_setup`).

**2.2 The transplant.** Write `A[r]` and `E[r]` for the two state registers after step `r-1`, `a0 = A[4]`, `a1 = A[5]`, `u = W1`. Fix `A[6..9]`, `E[10..13]` and `W10..W15` to the advice values of `M'`. For any chaining value `cv` and any `(a0, a1)`, steps 0 to 9 then determine `W0..W9` uniquely (`build(cv, a0, a1)` in section [1]); the partner message takes `W8 + D8`, `W9 + D9` and the advice `W10..W15` of `M` (`second`). Both messages then follow the advice trajectories `A[6..19]`, `E[10..19]` (steps 0 to 15 only, an identity of the step function, not a probability). The map `(cv, a0, a1) <-> (W8, W9, W16..W23)` is a bijection (320 bits, triangular). Experiment `r39-transplant-claw`, trials 1 to 255, checks the identity on 255 random chaining values.

**2.3 Row 16 is a claw.** `W16 = sigma1(W14) + W9 + sigma0(W1) + W0`. With `a1 = u + h(a0, cv)` (`recover_a1`) one finds `W16 - g = F(u) - F(a0)` (mod 2^32), where `g = 0xbca1c321` is the advice's `W16`, `F(x) = F_even(x)` for even `x` (a 32-bit expression in `x`, `S0(x)`, `MAJ`, `S1`, `CH` and six constants of the first block: `consts`, `fstep`) and `F(x) = sigma0(x) - x` for odd `x`. So `W16 = g` exactly when `F(a0) = F(u)` with `a0` even and `u` odd: a claw of the map `F` on 32-bit words (checked in `r39-transplant-claw`, `w16_identity`). Claws are found by a van Oorschot-Wiener walk (Section 3).

**2.4 What remains to pay, after a claw.** (i) `W8 in F8` and `W9 in F9`, where `F8 = { w : sigma0(w + D8) - sigma0(w) = 0x087ff000 }`, `F9 = { w : sigma0(w + D9) - sigma0(w) = 0x03010000 }` (`inF`); both sets depend only on 14 and 17 active bits of `w`, with exactly 1152 / 2^14 = 9/128 and 2080 / 2^17 = 65/4096 members (enumerated; the active-bit masks `0xCC19E60C` and `0xF9983C0F`), so `p8 p9 = 585 / 524288 = 2^-9.807707`. (ii) `W17 = 0x71e9ba98`, the advice's `W17` (the program tests it on every claw): probability 2^-32 for a uniform `W17`; the entry needs only that this value works (the exhaustive counts `|G16| = 2` and `|G17(g)| = 1` of 38912d66 and 2c48b18c say no other `W17` is available; they depend only on the states of steps 12 to 15, which the advice shares with the published pair; the second `W16` value is not used). (iii) The tail: rows 18 to 38 (`W18..W23` are the six free words of the bijection) must end with equal states after step 38: probability `p_tail`, Section 8.

Events (i) to (iii), together with `W16 = g` and the parity `a0` even, `u` odd, imply the collision: the pair then follows the advice trail through row 17 and its remaining rows hold with the tail event. The program ends by compressing the pair and comparing (`Attack.claw`, last block).

## 3. The program

One file, `experiments/r39joint.py` (sections [1] to [5]; the generator source is the string `GEN_C`, printed by `--gen-c`). Per first block `M0` the program runs one WINDOW of 2^26 walk evaluations (`Attack.run_window`):

1. Two random 256-bit words give `M0`; one target compression gives `cv`; the six constants of `F` (`consts`, 140 operations).
2. The generator `GEN_C` (freestanding C, compiled to WebAssembly, Appendix B) runs inside the attack and emits the bank A to bank B program of the 256-lane walk step, about 955 records of 5 bytes, with the five constants of the first block folded in; the bank B to bank A program is the same records with the bank bits of every register field swapped (a relocation pass, 8 operations per record). A first block whose image has more than 1030 records, needs more than 206 registers, or whose generator runs over 575,000 operators is skipped and charged (`Attack.window_setup`). The executed-operator count of `GEN_C` is the full cost of producing the window's kernel: the construction of the data-flow graph, the register allocation, and the emission of the 5-byte records are each steps of `GEN_C`, and every one of its operators is charged (Section 4), inside `m.o` and the work budget of Section 7. The Python routine `make_kernels_folded` of section [1] is only a readable reference that produces byte-identical records (Appendix B: 200 first blocks, both banks; the attack asserts the equality in check mode); its `to_source`/`exec` step (compiling a Python function) has no counterpart in the machine model, which executes the 5-byte records directly, charged per record per iteration in stages 1 and 2 (steps 4-5). No construction step is left uncharged.
3. The table is cleared (4 operations per 32-byte word); 256 trails start in the 256 lanes, trail `i` at `x0 = i`.
4. Stage 1 (`Attack.iter1`): 2^18 iterations of the kernel (one record = XOR, AND, OR or NOT of two 256-bit registers into a third: bit `j` of the 256 words of the lanes lives in plane `j`, rotations are renaming). A distinguished point (DP) is a new point whose low 7 bits are zero; the kernel ends with the OR of the low 7 planes. On a DP (`Attack.hit`): the lane is found (binary search), the 25 high bits `r` are extracted by a Horner pass over the planes, the slot is `r * 26112 words >> 25` split into word and sub-slot, the 5-byte entry is `chk(8) | len(12) | id(20)` with `chk = r mod 256`, 6 entries per 32-byte word, always overwrite; so (slot, chk) determines `r` and there is no false match. An entry with the same `chk` and a nonzero length is a MATCH (two trails end at one DP): the pair of (id, len) goes into a queue of 4096 pairs. The lane receives a new trail (next id, inserted plane by plane). A trail older than 2048 steps is cut by a scan every 1024 iterations.
5. Stage 2 (`Attack.stage2`), when the queue holds QFULL = 3840 pairs and at the end of the window (an iteration pushes at most one pair per lane, so the queue never holds more than 3839 + 256 = 4095 < QCAP = 4096 pairs: a constant inequality, no probability): pairs run in lane pairs `(p, p + 128)`, 128 slots, continuous refill. The longer trail starts at its start point, the shorter one `len` difference iterations later (a timing wheel); after each iteration the two states of a pair are compared (12 planes first, the other 20 only for candidates); the first iteration with equal states gives the predecessors `(a, b)`. Opposite parity is a claw (`a0` even, `u` odd).
6. Claw filters (`Attack.claw`, exact, scalar, every operation counted): `a1 = sigma0(u) + a0 + const` (uses the claw equation), `W9 = c9 - a1 in F9`; then `W8 in F8`; then `W17 = 0x71e9ba98`. A claw that passes all three is built into the pair `(M1, M1')`; both are compressed (2 target compressions, charged) and compared; a collision ends the run.

The attack is the loop over first blocks. In `--attack` the 16 words of each window's first block are drawn from the operating system's random source (`random.SystemRandom`, i.e. `os.urandom`): fresh algorithmic coins for every window, so the windows are independent trials of the algorithm (H1 part (a) is about the hash, not about the coins); `--seed S` exists only to make the experiments and the `--windows` measurements reproducible and is not used by the attack. Its halts are the window count B (Section 7), a skipped image (charged), an exhausted id space (a window creates one trail per DP hit, about 525,000, below the 2^20 ids of the entry layout), and success.

## 4. Machine model and prices (declared once)

A counted word RAM of 256-bit words with 256 registers (8,192 bytes, counted as memory), the cost model collision-frontier-v5: the unit is the target compression, 2812 operations (`C` of `sha256-r39`). Charged, one operation each: XOR, AND, OR, NOT, move, shift, rotate, add, subtract, compare and set; a conditional branch is a compare and a branch (2); a load or a store is 3 (index shift, base add, access); a call and its return are 2. A main-loop body record (register-to-register XOR, AND, OR, NOT, no immediate operand) is 5 bytes (an opcode and three 10-bit register fields), the price of dariolina's 6b678689 and of our 0c1ef7c3; every other instruction is 36 bytes. One executed WebAssembly operator of the generator is one charged operation (generator halts at 575,000 operators); this count is the whole kernel-construction cost -- the data-flow graph build, the register allocation and the 5-byte record emission performed by `GEN_C` -- and not a surrogate for it, since `GEN_C` and the Python reference `make_kernels_folded` emit identical records (Appendix B). These are prices of the cost model; they are not probabilistic premises. Every operation of the attack goes through the class `Mach` of the program (one method = one charged primitive, `m.o` counts them); there is no averaged price anywhere in the ledger.

## 5. The exact ledger

The cost of a window is the number of operations it executes, `m.o` after the window. It is not an estimate and not a table of prices: the program prints it for every window (`python3 r39joint.py --windows N`, about 80 seconds per window) and `--out` stores the category counts and the event counts from which the split below is formed; the categories add up to the total. 24 windows were run on the real step function, random first blocks, in check mode (every raw claw asserted against the construction: `F(a0) = F(u)`, parity, `W16 = g`, the closed forms of `W9`, `W8`, `W17`; 0 failures; check mode adds no counted operation). Per distinct claw, summed over the 24 windows (1,213,630 distinct claws, 50,567.9 per window; window minimum 12,203, maximum 12,731 operations per claw):

| category | operations per distinct claw | share |
| --- | ---: | ---: |
| stage-1 walk: kernel records + DP test + loop (L + 7 per iteration of 256 lanes) | 4950.9 | 40.1% |
| stage-1 handlers: DP hit (find lane, extract, table, entry, queue push, new start, insert) | 2771.2 | 22.4% |
| stage-1 cut scan | 13.0 | 0.1% |
| stage-2 walk: kernel records + loop (L + 3 per iteration) | 3320.5 | 26.9% |
| stage-2 other: launches, wheel, pair compare, merges, claw filters (of which the filters 50.9) | 1290.9 | 10.4% |
| window setup (first block compression, constants, table clear, lanes) | 2.1 | 0.0% |
| generator (executed wasm operators of one generation + relocation) | 11.5 | 0.1% |
| run setup (expansion of the advice) | 0.1 | 0.0% |
| **total** | **12,360.2 = 4.3955 compressions** | 100% |

Events per distinct claw: 10.37 DP hits, 2.540 matches, 1.250 opposite-parity claws (1.290 same parity, discarded), 5.184 stage-1 iterations (1327.1 evaluations), 3.491 stage-2 iterations (893.8 lane-iterations), 2.540 pairs. The kernel image has 924 to 974 records (limit 1030) and at most 206 registers. Filter passes over the 24 windows: `W9 in F9` 24,069 of 1,517,394 raw claws (0.0159; 65/4096 = 0.0159), `W8 in F8` 1,735 of 24,069 (0.0721; 9/128 = 0.0703), `W17 = published` 0. A verified passing pair is charged 2 x 2812 + 400 operations and occurs with probability 2^-41.8 per claw, 1.56e-9 operations per claw. Per window (Appendix A lists the 24 windows): mean 625,030,817 operations, standard deviation 5,833,095, largest 636,813,616; mean 50,567.9 distinct claws, standard deviation 186.7. The claim does not use these means as they stand: it uses their one-sided 99% bounds (Student t, 23 degrees of freedom, 2.500 standard errors), at most `mu+ = 628,007,505` operations and at least `c- = 50,472.66` distinct claws per window, and the run has a hard charged-work budget (Section 7).

**Every window has a worst-case cost (R).** Every loop of a window is bounded by a constant of the program: 2^18 stage-1 iterations, each at most 1,037 operations of kernel and loop plus at most 256 DP handlers (straight-line code apart from one loop over the 25 weight digits; under 4,096 operations each) and the cut scan; a trail is at most `MAXS + CUTP = 3,072` iterations long (a trail older than 2,048 is cut at the next scan, every 1,024 iterations), so the at most 2^26 pairs of a window (one per DP hit) take at most 2^26 x 3,072 pair-iterations, i.e. at most 2^30.6 full stage-2 iterations of 128 pairs plus at most 3,072 partly filled iterations per stage-2 call (at most 2^14.02 calls), each iteration at most 2^20.1 operations (kernel, launches, compares, and at most 128 claw filters with their verification); and at most `KTRY = 8` kernel generations, each charged (a window whose 8 generations all fail is skipped). Hence the charged work of one window is at most `R = 2^51` operations, and its number of distinct claws is at most 2^26.

## 6. Memory, exact by construction

Bytes, including everything the program holds at its peak:

| item | bytes |
| --- | ---: |
| register file, 256 x 32 | 8,192 |
| body records: 2 kernel images x 1030 x 5 | 10,300 |
| other instructions: (759 executed-block + 1100 routines + 1661 generator and relocation) x 36 | 126,720 |
| table: 26,112 words x 32 (6 entries of 5 bytes per word, 156,672 slots) | 835,584 |
| lane array, 256 words | 8,192 |
| stage-1 save area, 32 words | 1,024 |
| queue, 4096 pairs x 8 bytes (4 per word) | 32,800 |
| pair slots (bid and next, 128 words each) | 8,192 |
| timing wheel, 4096 buckets x 2 | 8,192 |
| free-slot stack, 128 words | 4,096 |
| constants and counters, 128 words | 4,096 |
| advice: our pair, `CV_PUB`, `M`, `M'` | 160 |
| **total** | **1,047,548 = 2^19.9986** (2^20 = 1,048,576; 1,028 bytes spare) |

The generator's scratch (15.9 KB static, 8 KB stack) lies inside the table region during the generation; the table is cleared after the generation, so the scratch adds nothing to the peak. Setup and attack have the same peak: there is no solver, no search campaign and no preprocessing buffer. Three of these numbers are hand counts: the 1100 routine instructions (a rolled 39-step compression 350, the pair builder and verification 400, window constants 170, run constants 120, driver loops 60; each counted from the source), the generator's 1649 WebAssembly instructions (lines of the llvm-mc listing) plus 12 for the relocation pass, and the peak of 45 scalar registers beside the kernel's 206 (50 are left). The 759 executed-block instructions are the program's own census (`Mach.blk`: the largest number of operations of one straight-line pass of each code block, stored with the counts of every window by `--out`).

## 7. Success probability and time

`p_claw = p8 p9 2^-32 p_tail`, `log2 p_claw` = -117.1347 (with `log2 p_tail` = -75.327, Section 8). **Claws are counted by groups.** Two claws of a window can depend on each other only if they share `a0` or `u` (a value with three or more preimages under `F`); grouping the claws of a window by shared endpoint, one claw per group is enough for the event, and distinct groups have disjoint inputs `(a0, u)` of the bijection. The run succeeds with probability `1 - (1 - p_claw)^G >= 1 - exp(-G p_claw)` for `G` groups; for probability at least 0.39, `G p_claw = lambda = -ln(0.61) = 0.494296`, so `log2 G` = 116.1182, and with the measured ratio of groups to distinct claws, 303,550 / 304,000 = 0.99858 (6 full windows), `log2 N` = 116.1202 distinct claws. The F9 and F8 counts are binomial from window to window (chi-square 22.6 and 32.0 on 24 degrees of freedom; 4.8 and 5.3 on 6 for 6 more windows) and the lag-1 autocorrelation of the F9 indicator in discovery order is within 0.012. At the lower bound `c- = 50,472.66` distinct claws per window, with a margin `(1 + 2^-19)`, this is `B = floor(N (1 + 2^-19) / c-) + 1 = 2^100.4970` windows (first blocks).

**Total work and total claws (Hoeffding).** The windows are independent trials (fresh coins per window, H1 part (a)), each with charged work in `[0, R]` and distinct claws in `[0, 2^26]`. By Hoeffding's inequality the total work of B windows exceeds `B (mu + mu 2^-20)` with probability at most `exp(-2 B (mu 2^-20)^2 / R^2) <= exp(-2^17.9)`, and the total number of distinct claws falls below `B c (1 - 2^-20)` with probability at most `exp(-2^40.8)` (mu, c the true means; `mu <= mu+` and `c >= c-` is premise H1 part (b)). So with probability at least `1 - 2 exp(-2^17.9)` all B windows run inside the budget and produce at least N distinct claws.

**The budget.** `--attack` stops at a success, after `B_WINDOWS` windows, or as soon as its charged work reaches `W_BUDGET = floor(B x 628,007,505 x (1 + 2^-20)) + 1 = 2^129.7232` operations (checked before each window, 6 operations per window), whichever comes first, so its charged work is at most `W_BUDGET + R + 6 B` in every run. The time is

`T = (W_BUDGET + R + 6 B) / 2812` target-compressions, `time_log2` = 118.2659 (exact 118.26582, rounded up), against 118.2542 at the plain means; the success probability is at least `0.39 - 2 exp(-2^17.9)`, i.e. 0.39 at any printed precision, because B carries the margin `(1 + 2^-19)`.

On a success `--attack` prints the two messages; otherwise it prints the number of windows and the charged work and exits with status 1. Each 1 bit of `log2 p_tail` moves `time_log2` by 1 bit: at `log2 p_tail` = -75.70 the time is 118.6388, at -75.34 it is 118.2788, at -77.41 it is 120.3488.

## 8. The tail p_tail (rows 18 to 38)

Definition. Distribution `U`: `E16`, `E17` of the first member pinned to the advice values (equal to the published ones) (this fixes `W16 = g`, `W17 = 0x71e9ba98`); `W8` uniform on `F8`, `W9` uniform on `F9`, independent; `E18..E23` of the first member independent and uniform on 2^32 (`W18..W23` are a bijective image of them); everything else is determined by the real step function and message expansion. `Q = P_U(collision and K_P | a0 even, u odd) = 4 P_U(collision and K_P and a0 even and u odd)`, where the collision test is exact (equal 256-bit outputs of the two 39-step compressions) and `K_P` is an importance carrier (the printed cells of Tables 21 and 22 of rows 16 to 18, signed differences only for rows 19 to 22, `E23[30] = 0`). `K_P` is a subset of all routes to a collision, so `Q <= p_tail` and the cost bound uses `p_tail >= 2^q_tail` with `q_tail` = -75.327.

Declared value. `q_tail` = -75.327, the measured mean (620 verified hits in 8,601,600 proposals over 14 runs, standard error of the mean 4.9 percent (0.07 bit)). Evidence: the replica `experiments/r39tail.py`, with this entry's advice, runs in the organizer sandbox as `r39-tail-01` to `r39-tail-14` (Section 10). Each run estimates `Q'` (this event without the parity condition) as an SMC estimate of the carrier `K_P` over rows 18 to 23 times the fraction of proposals with equal 256-bit states after step 38 (`W8`, `W9` redrawn in `F8`, `F9` for every proposal); every hit is rebuilt into a chaining value and checked by the two 39-step compressions. Our run of the 14 entries with the organizer's public seeds: 620 hits in 8,601,600 proposals, all 620 verified collisions, parity classes 151, 172, 149, 148; mean log2 Q' = -75.327 (linear-scale mean of the 14 run estimates; per-run values -75.867 to -74.886), standard error of the mean 4.9 percent (0.07 bit); these are reproducible observations consistent with the premise, and the declared value is their mean. This is the tail as measured on this advice; no tail gain over the published advice is claimed (the same runs on the published pair give 601 hits, a difference within run-to-run variation): the two advices share every state word the tail reads from step 12 on.

## 9. Premises (declared in claim.json)

`H1-claw-model` (score-critical), four parts. (a) The chaining value `cv` of a random first block behaves as an independent random value for the walk map and the later events, so the windows are independent trials. (b) The program's yield and cost per window are those measured on the real step function over 24 full-size windows (50,567.9 distinct claws, 12,360.2 operations per claw); the program cannot be run for 2^100.8 windows. The 24 windows ran with the published pair as advice. The advice enters the walk only through the per-window constant `cw = g - sigma1(W14) - c9 - k0 + cv6 + K1` (`consts`), where `-k0` contains `+cv7` and no other constant of `F` contains `cv7`; for a uniform `cv` (part (a)) the six constants `(cw, eb, cv0, cv1, cv4, cv5)` are uniform for either advice, so the per-window distribution of yield and cost is the same (experiment `r39-window-small` with this advice: 808 distinct claws against 807). (c) A distinct claw is, for the events `W8 in F8`, `W9 in F9`, `W17 = 0x71e9ba98` and the tail, a trial with the probabilities of Sections 2.4 and 8, independent of the walk's yield. (d) `W17` is uniform over the claws.

Test of (c) and (d), on claws of the real walk (our test script, not shipped; 310,224 distinct claws from 6 random first blocks, found by our C model of the same walk, whose stage-1 and stage-2 counts agree with the program to 0.1 percent; each with `F(a0) = F(u)`, `a0` even, `u` odd, `W16 = g` verified against the construction): `W9 in F9` 5,015 (0.01617; expected 0.01587); `W8 in F8` 22,002 (0.07092; 0.07031); both 360 (0.001160; 0.001116). Matches of `W17` with the published value in the low `k` bits (expected `n 2^-k`): k = 8: 1,199 (1,211.8); k = 12: 82 (75.7); k = 16: 5 (4.73); k = 20: 0 (0.30); k = 24: 0 (0.02). Chi-square of the low 16 bits of `W17` against uniform: 65,830.2 with 65,535 degrees of freedom, z = 0.82. The test covers the low 16 bits of `W17` and the side-condition rates; the high 16 bits of `W17`, the independence of `W17` from the tail event and the full 2^-32 are not testable at this sample size and are the premise (d).

`H2-tail` (score-critical): `p_tail >= 2^q_tail` for claws uniform on the fibre, Section 8.

## 10. Experiments (organizer sandbox)

The first two run the attack program (`experiments/r39joint.py`) and return no message pair: the advice pair is a collision from `CV_PUB`, not from the standard IV, so the organizer's digest check on blocks hashed from the IV would not be a collision, and a full collision of the target is not produced by any run at this scale. They are program checks; nothing in the ledger or the probability is estimated from them.

`r39-transplant-claw`. Trial 0: the advice pair through `Attack.claw` with the folded kernel built for `CV_PUB` (`W9 in F9`, `W8 in F8`, `W17 = 0x71e9ba98`, both second blocks compressed from `CV_PUB` for 39 steps and compared; check off, parity exempt: the advice's own `W1` is even while the walk only emits `u` odd; the arithmetic does not use the parity): `claw_returned_pair` 1, `passed_f9` 1, `passed_f8` 1, `passed_w17` 1, `pair_is_published` 1 (the returned pair is the advice), `sfs_collision` 1, `advice_u_parity` 0, `kernel_records` 953, `claw_ops` 6174. Trials 1 to 255: random `cv`, even `a0`, odd `u`, `a1` recovered, both messages built; `transplant_ok` 1 and `w16_identity` 1 on all 255.

`r39-window-small`. Trial 0: one window of the program (folded kernel, all parameters unchanged, check mode: every raw claw is asserted to satisfy `F(a0) = F(u)`, `a0` even, `u` odd, `W16 = g` by `build` and `expand`), cut to 2^22 walk evaluations (16,384 iterations): `dp_hits` 32743, `matches` 1727, `stage2_iterations` 3126, `raw_claws` 838, `distinct_claws` 808, `passed_f9` 12, `passed_f8` 0, `passed_w17` 0, `kernel_records` 924. The generator is charged at its halt cap 575,000 in the sandbox (no WebAssembly runtime there). The tail is replicated by the entries below.

`r39-tail-01` to `r39-tail-14`: `experiments/r39tail.py` (12,188 bytes, standard library only). Trial 0 runs the SMC of Section 8 (500 particles) and reports the stage counts `k18..k23`, the carrier estimate, a known-answer check on the advice pair (`kat` 1) and the F8/F9 mask check (`mask_viol` 0); trials 1 to 10 run 30 x 2048 proposals each and report hits, verified collisions and their parity classes. With the public seeds: 620 hits, 620 verified, mean log2 Q' -75.327, standard error of the mean 4.9 percent (0.07 bit).

## 11. Advice and preprocessing

The advice is our pair of Section 2.1, embedded as 160 bytes and verified here as a 39-step collision from its chaining value (experiment `r39-transplant-claw`). Its offline construction (premise H3-base) is one run of a characteristic-guided SAT instance: our CNF encoding of two 39-step compressions from a common free chaining value, every signed A, E and W row of the re-signed characteristic of Section 2.1 fixed as clauses, the signs of `W0..W15` left free, solved by kissat on one core; the pair was decoded from the assignment and checked by two 39-step compressions. Charged time: the timed replay of the same instance (kissat 4.0.3, one core, read by /usr/bin/time), 1,499 s. A core executes fewer than 2^35 instructions per second (8 GHz x 4 per cycle) and each instruction is at most 3 word operations of the model, so one core-second is under 2^36.6 / 2812 < 2^25.2 target compressions; we charge 2^26 per core-second: 1,499 x 2^26 = 2^36.55 target compressions, `preprocessing_log2` = 37. Construction memory: the replay peaked at 156,286,976 bytes; we state the bound 268,435,456 bytes = 2^28 for this one-time offline advice construction. It ends before the attack starts and leaves only the 160-byte advice, which the attack's 2^20 bytes (Section 6) include; the attack itself holds no solver state. Because 2^36.55 is below 2^98, `time_log2` does not change (2^118.2659 + 2^36.55 rounds to the same value).

## 12. What differs from the base entries

- The advice: the published Table 23 pair (bb21016d, 44870635) is replaced by our pair on the re-signed characteristic (Section 2.1); the program reads only `CV_PUB`, `M_PUB`, `MP_PUB` from it and derives `g`, `W17`, `D8`, `D9` from them (`D8`, `D9`, `g`, `W17` are unchanged).
- The tail: re-measured on this advice with the same replica and seeds, q_tail = -75.327, the measured mean (Section 8); time_log2 118.2659 (Section 7).
- Preprocessing: the guided SAT run of Section 11 replaces the counted enumeration of the published pair.
- Everything else (program, ledger, memory, windows, premises H1 and H2 and their tests) is bb21016d's, which answers the earlier findings on this construction.

## Appendix C. The characteristic, the pair, the recompute

The pair (also `CV_PUB`, `M_PUB`, `MP_PUB` of `experiments/r39joint.py`):
cv `13afac33 175c84d9 7857ed69 9032dbbb 565ae88b 61991e38 27c1f3da 3d1135bb`;
M `a73b8b63 39c25742 23c084b8 d889ec41 6b477b58 32e42a90 27cc2766 efbdea22 43f93094 963f1769 0d98e0e1 d1c3a778 59058cdf 302206cd 43670038 4891771b`;
M' equal to M except words 8 to 12: `03f93094 9ebf0769 4d98e0e1 cbc1caa4 5915a4df`.

Its signed characteristic (rows as `-`/`u`/`n`, leftmost character = bit 31; `u` = M bit 1 and M' bit 0, `n` the reverse; every row not printed, steps -4 to 7 and 27 to 38, is all `-`):

```
  8 A: -u------------------------------ E: -u------------------------------ W: -u------------------------------
  9 A: ----u---u---n-u----u---n--n----- E: ----n---u-nuu------u------n----- W: ----n---n----------u------------
 10 A: -------------------------------- E: n-u----u--n------n--nnn-nnn-n-u- W: -n------------------------------
 11 A: -------------------------------- E: -n--n-------u----------u-------- W: ---un-n-------u--nu-nu-unu-uun--
 12 A: -----u--uu---------------------- E: -u---n--un----n----------------- W: -----------n------n-u-----------
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

Against the published Table 21/23 characteristic only two rows differ: W11 `-----uu-------u---n---nn--nn-u--` -> the row above, W12 `-----------n-------nn-----------` -> the row above; every A and E row is the published one. Recompute (our profiler, two 39-step computations from cv): `collision=True`; over steps 16 to 38, 19 signed state bits (A 4, E 15), 36 Maj and 61 Ch conditions, 116 in total, the same count as the published characteristic.

## Appendix A. The 24 windows

| window seed | distinct claws | operations | operations per claw | kernel records | registers |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 61000 | 50898 | 627943333 | 12337.3 | 951 | 192 |
| 62000 | 50530 | 623020418 | 12329.7 | 948 | 192 |
| 63000 | 50267 | 617609471 | 12286.6 | 936 | 185 |
| 64000 | 50413 | 628416467 | 12465.4 | 961 | 195 |
| 65000 | 50609 | 622605444 | 12302.3 | 939 | 189 |
| 66000 | 50841 | 626025737 | 12313.4 | 950 | 191 |
| 67000 | 50322 | 625152678 | 12423.0 | 945 | 189 |
| 68000 | 50686 | 629057519 | 12410.9 | 955 | 193 |
| 69000 | 50747 | 618817853 | 12194.2 | 933 | 186 |
| 70000 | 50317 | 628945221 | 12499.7 | 957 | 196 |
| 71000 | 50588 | 623997488 | 12334.9 | 949 | 191 |
| 72000 | 50387 | 623331320 | 12370.9 | 946 | 196 |
| 73000 | 50543 | 625400681 | 12373.6 | 952 | 193 |
| 74000 | 50413 | 620286366 | 12304.1 | 936 | 190 |
| 75000 | 50274 | 613284185 | 12198.8 | 924 | 188 |
| 76000 | 50406 | 627821841 | 12455.3 | 956 | 196 |
| 77000 | 50738 | 624050479 | 12299.5 | 943 | 189 |
| 78000 | 50569 | 622061571 | 12301.2 | 940 | 192 |
| 79000 | 50505 | 620710280 | 12290.1 | 938 | 189 |
| 80000 | 50631 | 617570661 | 12197.5 | 929 | 184 |
| 81000 | 50706 | 636813616 | 12558.9 | 970 | 199 |
| 82000 | 50693 | 636674778 | 12559.4 | 974 | 197 |
| 83000 | 50820 | 634706712 | 12489.3 | 968 | 200 |
| 84000 | 50727 | 626435476 | 12349.2 | 953 | 191 |

## Appendix B. The generator

`python3 r39joint.py --gen-c > gen39b.c`, then `python3 -m ziglang cc -target wasm32-freestanding -Oz -nostdlib -fno-builtin -Wl,--no-entry -Wl,--export=gen -Wl,--export=g_nreg -Wl,--export=g_dppol -Wl,-z,stack-size=8192 -Wl,--initial-memory=65536 -Wl,--max-memory=65536 -o gen39b.wasm gen39b.c`: 3,849 bytes, sha256 `d6a1fedd47d51e2a268264768836f83a59723d7a6b1ddd97508c4f2f3e76787c`, 1,649 WebAssembly instructions. With `R39_WASM=gen39b.wasm` (and the `wasmtime` package) the program charges the executed operators of each generation (wasmtime fuel, one operator = one operation): mean 523.6k, standard deviation 8.0k, maximum 543k over 200 first blocks; it emits records equal, line by line, to those of the Python generator `make_kernels_folded` of section [2] (200 first blocks, both banks). Without the module the program charges the halt cap 575,000.
