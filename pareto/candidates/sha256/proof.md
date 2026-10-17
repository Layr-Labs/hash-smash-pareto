# SHA-256 reduced to 39 steps: ordinary collision by the transplanted Table 23 pair, a row-16 claw search and a bit-sliced 256-lane walk

Target `sha256-r39-prefix-v1`. Claim: `time_log2` = 118.3593 target-compressions, `memory_log2_bytes` = 20 (1,047,548 bytes, the 160-byte advice included), success probability at least 0.39, `preprocessing_log2` = 0 (Section 11), advice 160 bytes.

Credit. The attack is the construction of sraiw's 38912d66 (the transplant of the published Table 23 pair of ePrint 2026/1120 onto a random first block, the exact bijection, the row-16 claw, the exact side conditions F8 and F9, the dual-parity fibre) built on dariolina's row-16 claw idea (21b6653a, 1d3f2c3c, 2c48b18c, cfe5c4e2, 4e396742) and on her preregistered tail methodology; dariolina is co-author of this entry. The word-RAM cost convention comes from dariolina's 744875ec and our 3c1d7f68, 368d1718, 01e31be9; the 5-byte record convention is dariolina's 6b678689 and our 0c1ef7c3. What this entry adds is the machine program (Sections 3 to 6), its exact executed ledger, a whole-megabyte table; the tail value is the credited published calibration (Section 8). Everything below was written and re-derived by us from the construction; no code of any other participant was run, imported or compiled.

## 1. Target and output

SHA-256 with 39 steps in every compression, FIPS 180-4 padding, the standard IV, feed-forward after step 38, all 256 digest bits. The output is two distinct 128-byte messages `M0 || M1` and `M0 || M1'`: the same first block, second blocks that give the same chaining value after the second compression; the padding block that follows is identical, so the two digests are equal. The first block `M0` is a random block, `cv = compress39(IV, M0)`.

## 2. The construction (sraiw 38912d66, dariolina)

**2.1 The base is advice.** The pair of ePrint 2026/1120, Table 23, is a 39-step semi-free-start collision: a chaining value `CV_PUB` (8 words), two blocks `M'` and `M` (16 words each), 160 bytes, printed in `experiments/r39joint.py` section [1] (`CV_PUB`, `M_PUB`, `MP_PUB`). It is a collision of the 39-step compression from `CV_PUB` (experiment `r39-transplant-claw`, trial 0; our `compress39` equals the organizer's `verifier/hash_functions.py` on 300 random blocks, and the published pair collides under the organizer reference). It is the advice of this entry. Its trajectories `BA, BE` (message `M'`) and `CA, CE` (message `M`) are expanded from the 160 bytes by two compressions at the start of the run (charged 2 x 2812 + 120 operations, `Attack.base_setup`).

**2.2 The transplant.** Write `A[r]` and `E[r]` for the two state registers after step `r-1`, `a0 = A[4]`, `a1 = A[5]`, `u = W1`. Fix `A[6..9]`, `E[10..13]` and `W10..W15` to the published values of `M'`. For any chaining value `cv` and any `(a0, a1)`, steps 0 to 9 then determine `W0..W9` uniquely (`build(cv, a0, a1)` in section [1]); the partner message takes `W8 + D8`, `W9 + D9` and the published `W10..W15` of `M` (`second`). Both messages then follow the published trajectories `A[6..19]`, `E[10..19]` (steps 0 to 15 only, an identity of the step function, not a probability). The map `(cv, a0, a1) <-> (W8, W9, W16..W23)` is a bijection (320 bits, triangular). Experiment `r39-transplant-claw`, trials 1 to 255, checks the identity on 255 random chaining values.

**2.3 Row 16 is a claw.** `W16 = sigma1(W14) + W9 + sigma0(W1) + W0`. With `a1 = u + h(a0, cv)` (`recover_a1`) one finds `W16 - g = F(u) - F(a0)` (mod 2^32), where `g = 0xbca1c321` is the published `W16`, `F(x) = F_even(x)` for even `x` (a 32-bit expression in `x`, `S0(x)`, `MAJ`, `S1`, `CH` and six constants of the first block: `consts`, `fstep`) and `F(x) = sigma0(x) - x` for odd `x`. So `W16 = g` exactly when `F(a0) = F(u)` with `a0` even and `u` odd: a claw of the map `F` on 32-bit words (checked in `r39-transplant-claw`, `w16_identity`). Claws are found by a van Oorschot-Wiener walk (Section 3).

**2.4 What remains to pay, after a claw.** (i) `W8 in F8` and `W9 in F9`, where `F8 = { w : sigma0(w + D8) - sigma0(w) = 0x087ff000 }`, `F9 = { w : sigma0(w + D9) - sigma0(w) = 0x03010000 }` (`inF`); both sets depend only on 14 and 17 active bits of `w`, with exactly 1152 / 2^14 = 9/128 and 2080 / 2^17 = 65/4096 members (enumerated; the active-bit masks `0xCC19E60C` and `0xF9983C0F`), so `p8 p9 = 585 / 524288 = 2^-9.807707`. (ii) `W17 = 0x71e9ba98`, the published `W17` (the program tests it on every claw): probability 2^-32 for a uniform `W17`; the entry needs only that this value works (the exhaustive counts `|G16| = 2` and `|G17(g)| = 1` of 38912d66 and 2c48b18c say no other `W17` is available; the second `W16` value is not used). (iii) The tail: rows 18 to 38 (`W18..W23` are the six free words of the bijection) must end with equal states after step 38: probability `p_tail`, Section 8.

Events (i) to (iii), together with `W16 = g` and the parity `a0` even, `u` odd, imply the collision: the pair then follows the published trail through row 17 and its remaining rows hold with the tail event. The program ends by compressing the pair and comparing (`Attack.claw`, last block).

## 3. The program

One file, `experiments/r39joint.py` (sections [1] to [5]; the generator source is the string `GEN_C`, printed by `--gen-c`). Per first block `M0` the program runs one WINDOW of 2^26 walk evaluations (`Attack.run_window`):

1. Two random 256-bit words give `M0`; one target compression gives `cv`; the six constants of `F` (`consts`, 140 operations).
2. The generator `GEN_C` (freestanding C, compiled to WebAssembly, Appendix B) runs inside the attack and emits the bank A to bank B program of the 256-lane walk step, about 955 records of 5 bytes, with the five constants of the first block folded in; the bank B to bank A program is the same records with the bank bits of every register field swapped (a relocation pass, 8 operations per record). A first block whose image has more than 1030 records, needs more than 206 registers, or whose generator runs over 575,000 operators is skipped and charged (`Attack.window_setup`).
3. The table is cleared (4 operations per 32-byte word); 256 trails start in the 256 lanes, trail `i` at `x0 = i`.
4. Stage 1 (`Attack.iter1`): 2^18 iterations of the kernel (one record = XOR, AND, OR or NOT of two 256-bit registers into a third: bit `j` of the 256 words of the lanes lives in plane `j`, rotations are renaming). A distinguished point (DP) is a new point whose low 7 bits are zero; the kernel ends with the OR of the low 7 planes. On a DP (`Attack.hit`): the lane is found (binary search), the 25 high bits `r` are extracted by a Horner pass over the planes, the slot is `r * 26112 words >> 25` split into word and sub-slot, the 5-byte entry is `chk(8) | len(12) | id(20)` with `chk = r mod 256`, 6 entries per 32-byte word, always overwrite; so (slot, chk) determines `r` and there is no false match. An entry with the same `chk` and a nonzero length is a MATCH (two trails end at one DP): the pair of (id, len) goes into a queue of 4096 pairs. The lane receives a new trail (next id, inserted plane by plane). A trail older than 2048 steps is cut by a scan every 1024 iterations.
5. Stage 2 (`Attack.stage2`), when the queue holds 4032 pairs and at the end of the window: pairs run in lane pairs `(p, p + 128)`, 128 slots, continuous refill. The longer trail starts at its start point, the shorter one `len` difference iterations later (a timing wheel); after each iteration the two states of a pair are compared (12 planes first, the other 20 only for candidates); the first iteration with equal states gives the predecessors `(a, b)`. Opposite parity is a claw (`a0` even, `u` odd).
6. Claw filters (`Attack.claw`, exact, scalar, every operation counted): `a1 = sigma0(u) + a0 + const` (uses the claw equation), `W9 = c9 - a1 in F9`; then `W8 in F8`; then `W17 = 0x71e9ba98`. A claw that passes all three is built into the pair `(M1, M1')`; both are compressed (2 target compressions, charged) and compared; a collision ends the run.

The attack is the loop over first blocks; its halts are the window count B (Section 7), a skipped image (charged), an exhausted id space (a window creates one trail per DP hit, about 525,000, below the 2^20 ids of the entry layout), and success.

## 4. Machine model and prices (declared once)

A counted word RAM of 256-bit words with 256 registers (8,192 bytes, counted as memory), the cost model collision-frontier-v5: the unit is the target compression, 2812 operations (`C` of `sha256-r39`). Charged, one operation each: XOR, AND, OR, NOT, move, shift, rotate, add, subtract, compare and set; a conditional branch is a compare and a branch (2); a load or a store is 3 (index shift, base add, access); a call and its return are 2. A main-loop body record (register-to-register XOR, AND, OR, NOT, no immediate operand) is 5 bytes (an opcode and three 10-bit register fields), the price of dariolina's 6b678689 and of our 0c1ef7c3; every other instruction is 36 bytes. One executed WebAssembly operator of the generator is one charged operation (generator halts at 575,000 operators). These are prices of the cost model; they are not probabilistic premises. Every operation of the attack goes through the class `Mach` of the program (one method = one charged primitive, `m.o` counts them); there is no averaged price anywhere in the ledger.

## 5. The exact ledger

The cost of a window is the number of operations it executes, `m.o` after the window. It is not an estimate and not a table of prices: the program prints it for every window (`python3 r39joint.py --windows N`, about 80 seconds per window) and `--out` stores the category counts and the event counts from which the split below is formed; the categories add up to the total. 24 windows were run on the real step function, random first blocks, in check mode (every raw claw asserted against the construction: `F(a0) = F(u)`, parity, `W16 = g`, the closed forms of `W9`, `W8`, `W17`; 0 failures; check mode adds no counted operation). Per distinct claw, summed over the 24 windows (1,215,886 distinct claws, 50,662 per window; window minimum 12,203, maximum 12,731 operations per claw):

| category | operations per distinct claw | share |
| --- | ---: | ---: |
| stage-1 walk: kernel records + DP test + loop (L + 7 per iteration of 256 lanes) | 4990.0 | 40.3% |
| stage-1 handlers: DP hit (find lane, extract, table, entry, queue push, new start, insert) | 2764.2 | 22.3% |
| stage-1 cut scan | 12.9 | 0.1% |
| stage-2 walk: kernel records + loop (L + 3 per iteration) | 3329.1 | 26.9% |
| stage-2 other: launches, wheel, pair compare, merges, claw filters (of which the filters 50.9) | 1287.8 | 10.4% |
| window setup (first block compression, constants, table clear, lanes) | 2.1 | 0.0% |
| generator (executed wasm operators of one generation + relocation) | 10.5 | 0.1% |
| run setup (expansion of the advice) | 0.1 | 0.0% |
| **total** | **12,396.9 = 4.4086 compressions** | 100% |

Events per distinct claw: 10.35 DP hits, 2.535 matches, 1.250 opposite-parity claws (1.285 same parity, discarded), 5.174 stage-1 iterations (1324.6 evaluations), 3.466 stage-2 iterations (887.4 lane-iterations), 2.535 pairs. The kernel image has 937 to 991 records (limit 1030) and at most 206 registers. Filter passes over the 24 windows: `W9 in F9` 24,063 of 1,519,918 raw claws (0.0158; 65/4096 = 0.0159), `W8 in F8` 1,628 of 24,063 (0.0677; 9/128 = 0.0703), `W17 = published` 0. A verified passing pair is charged 2 x 2812 + 400 operations and occurs with probability 2^-41.8 per claw, 1.56e-9 operations per claw. The cost of the whole attack is (number of windows) x (mean operations per window); the number of windows is 2^100.5903, and the sum of that many independent windows has a relative fluctuation below 2^-50, so the cost of the run is the mean; the measured mean has a standard error of 27.6 operations (0.22%, 0.003 bit). Appendix A lists the 24 windows.

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
| advice: the published pair, `CV_PUB`, `M`, `M'` | 160 |
| **total** | **1,047,548 = 2^19.9986** (2^20 = 1,048,576; 1,028 bytes spare) |

The generator's scratch (15.9 KB static, 8 KB stack) lies inside the table region during the generation; the table is cleared after the generation, so the scratch adds nothing to the peak. Setup and attack have the same peak: there is no solver, no search campaign and no preprocessing buffer. Three of these numbers are hand counts: the 1100 routine instructions (a rolled 39-step compression 350, the pair builder and verification 400, window constants 170, run constants 120, driver loops 60; each counted from the source), the generator's 1649 WebAssembly instructions (lines of the llvm-mc listing) plus 12 for the relocation pass, and the peak of 45 scalar registers beside the kernel's 206 (50 are left). The 759 executed-block instructions are the program's own census (`Mach.blk`: the largest number of operations of one straight-line pass of each code block, stored with the counts of every window by `--out`).

## 7. Success probability and time

`p_claw = p8 p9 2^-32 p_tail`, `log2 p_claw` = -117.2355 (with `log2 p_tail` = -75.4278, Section 8). The run succeeds with probability `1 - (1 - p_claw)^N >= 1 - exp(-N p_claw)`; for probability at least 0.39, `N p_claw = lambda = -ln(0.61) = 0.494296`, so `log2 N` = 116.2190 distinct claws. At 50,661.9 distinct claws per window this is B = 2^100.5903 windows (first blocks). The time is

`T = N x (12,396.9 + 1.56e-9) / 2812` target-compressions, `time_log2` = 118.3593.

The program stops after B windows. Each 1 bit of `log2 p_tail` moves `time_log2` by 1 bit: at `log2 p_tail` = -75.70 the time is 118.6315, at -75.34 it is 118.2715, at -77.41 it is 120.3415.

## 8. The tail p_tail (rows 18 to 38)

Definition. Distribution `U`: `E16`, `E17` of the first member pinned to the published values (this fixes `W16 = g`, `W17 = 0x71e9ba98`); `W8` uniform on `F8`, `W9` uniform on `F9`, independent; `E18..E23` of the first member independent and uniform on 2^32 (`W18..W23` are a bijective image of them); everything else is determined by the real step function and message expansion. `Q = P_U(collision and K_P | a0 even, u odd) = 4 P_U(collision and K_P and a0 even and u odd)`, where the collision test is exact (equal 256-bit outputs of the two 39-step compressions) and `K_P` is an importance carrier (the printed cells of Tables 21 and 22 of rows 16 to 18, signed differences only for rows 19 to 22, `E23[30] = 0`). `K_P` is a subset of all routes to a collision, so `Q <= p_tail` and the cost bound uses `p_tail >= 2^q_tail` with `q_tail` = -75.4278.

Declared value. `q_tail` = -75.4278, the 64-seed 99% lower confidence bound of the tail calibration published by sraiw with 38912d66 (repeated in 793185f6) for this same event on this trail and fibre (sequential Monte Carlo, 64 seeds, Student-t bound over seeds); credited by id and used as data. The definition of the quantity is the one above; the value is our theory, declared as heuristic `H2-tail`; no replica of it runs in the organizer sandbox.

## 9. Premises (declared in claim.json)

`H1-claw-model` (score-critical), four parts. (a) The chaining value `cv` of a random first block behaves as an independent random value for the walk map and the later events, so the windows are independent trials. (b) The program's yield and cost per window are those measured on the real step function over 24 full-size windows (50,661.9 distinct claws, 12,396.9 operations per claw); the program cannot be run for 2^100.9 windows. (c) A distinct claw is, for the events `W8 in F8`, `W9 in F9`, `W17 = published` and the tail, a trial with the probabilities of Sections 2.4 and 8, independent of the walk's yield. (d) `W17` is uniform over the claws.

Test of (c) and (d), on claws of the real walk (our test script, not shipped; 310,224 distinct claws from 6 random first blocks, found by our C model of the same walk, whose stage-1 and stage-2 counts agree with the program to 0.1 percent; each with `F(a0) = F(u)`, `a0` even, `u` odd, `W16 = g` verified against the construction): `W9 in F9` 5,015 (0.01617; expected 0.01587); `W8 in F8` 22,002 (0.07092; 0.07031); both 360 (0.001160; 0.001116). Matches of `W17` with the published value in the low `k` bits (expected `n 2^-k`): k = 8: 1,199 (1,211.8); k = 12: 82 (75.7); k = 16: 5 (4.73); k = 20: 0 (0.30); k = 24: 0 (0.02). Chi-square of the low 16 bits of `W17` against uniform: 65,830.2 with 65,535 degrees of freedom, z = 0.82. The test covers the low 16 bits of `W17` and the side-condition rates; the high 16 bits of `W17`, the independence of `W17` from the tail event and the full 2^-32 are not testable at this sample size and are the premise (d).

`H2-tail` (score-critical): `p_tail >= 2^q_tail` for claws uniform on the fibre, Section 8.

## 10. Experiments (organizer sandbox)

Both run the program of this file (`experiments/r39joint.py`, one file, 64 KiB limit) and return no message pair: the published pair is a collision from `CV_PUB`, not from the standard IV, so the organizer's digest check on blocks hashed from the IV would not be a collision, and a full collision of the target is not produced by any run at this scale. They are program checks; nothing in the ledger or the probability is estimated from them.

`r39-transplant-claw`. Trial 0: the published pair through `Attack.claw` with the folded kernel built for `CV_PUB` (claw equation, `W9 in F9`, `W8 in F8`, `W17 = published`, both second blocks compressed from `CV_PUB` for 39 steps and compared): `claw_returned_pair` 1, `passed_f9` 1, `passed_f8` 1, `passed_w17` 1, `pair_is_published` 1, `sfs_collision` 1, `kernel_records` 962, `claw_ops` 6174. Trials 1 to 255: random `cv`, even `a0`, odd `u`, `a1` recovered, both messages built; `transplant_ok` 1 and `w16_identity` 1 on all 255.

`r39-window-small`. Trial 0: one window of the program (folded kernel, all parameters unchanged, check mode: every raw claw is asserted to satisfy `F(a0) = F(u)`, `a0` even, `u` odd, `W16 = g` by `build` and `expand`), cut to 2^22 walk evaluations (16,384 iterations): `dp_hits` 32865, `matches` 1705, `stage2_iterations` 2892, `raw_claws` 836, `distinct_claws` 807, `passed_f9` 11, `passed_f8` 0, `passed_w17` 0, `kernel_records` 926. The generator is charged at its halt cap 575,000 in the sandbox (no WebAssembly runtime there). A tail replica is not part of this entry: the tail estimators are C and CUDA programs.

## 11. Advice and preprocessing

The base is the published Table 23 pair, embedded as 160 bytes of advice, as in 38912d66. Its construction is CHARGED as preprocessing: `preprocessing_log2` = 36 target compressions, the allowance 38912d66 declares for this same base (judged plausible_not_refuted). This is the declared premise H3-base: the search that produced the pair cost at most 2^36 target compressions and ran within the claimed 2^20-byte peak. Total time is 2^118.3593 + 2^36, which rounds to the same `time_log2`; any preprocessing below 2^108 moves it by less than 0.001 bit. The memory of Section 6 is the memory of the program, the advice included.

## 12. Findings on 38912d66, and what this entry does

- F-COST-LEDGER-1 (totals embedded as constants in `ledger()`): no total is embedded; Section 5 is the output of `Mach` counters of the shipped program, every category adds to the total, Appendix A lists the windows.
- F-CRYPTO-OUTPUT-1 (b6c6978b): the program now keeps the first block M0 of each window (16 stores, charged), acts on claw()'s success return (the window stops), and emits the two 128-byte messages M0||M1, M0||M1'; `--attack` runs windows until a success and prints them.
- F-PREPROCESS-1, and b6c6978b's F-COST-PREPROCESS-1 / F-PREPROCESS-ADVICE-OMISSION: the pair's construction is now charged, preprocessing_log2 = 36, declared as premise H3-base (Section 11).
- F-TAIL-CALIBRATION-1, F3 (floor asserted, Student-t from replicas): the declared tail is the published 64-seed 99% lower confidence bound 2^-75.4278 itself (a statistic over 64 seeds, not an asserted floor), declared as the heuristic H2-tail (Section 8).
- F1, F-EXP-1 (no full-target witness): none is possible at 2^118; experiment `r39-transplant-claw` runs the published pair through the program's `claw` path and returns a true compression-function collision from `CV_PUB` (Section 10).
- F2 (`W17` uniformity under claw selection): tested on 310,224 real claws, low 16 bits, z = 0.82; its limit is stated in Section 9.
- F4 (extrapolation of the yield to the full number of windows): 24 full-size windows on the real step function, minimum, maximum and standard error stated (Sections 5 and 9, part (b)).
- dariolina's 4e396742 (F-COST-1, F-EVAL-RESOURCE-MEMORY-OMISSION): Section 6 is the memory of everything the program does, there is no campaign whose memory is left out.

## Appendix A. The 24 windows

| window seed | distinct claws | operations | operations per claw | kernel records | registers |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 31000 | 50602 | 625594451 | 12363.0 | 954 | 197 |
| 31001 | 50441 | 626316017 | 12416.8 | 956 | 193 |
| 31002 | 50492 | 630283659 | 12482.8 | 962 | 196 |
| 31003 | 51038 | 623847818 | 12223.2 | 944 | 190 |
| 32000 | 50870 | 634298884 | 12469.0 | 967 | 198 |
| 32001 | 50296 | 628226974 | 12490.6 | 958 | 197 |
| 32002 | 50636 | 621534709 | 12274.6 | 942 | 187 |
| 32003 | 50527 | 622844163 | 12327.0 | 949 | 192 |
| 33000 | 50929 | 621483499 | 12202.9 | 946 | 193 |
| 33001 | 50835 | 630962700 | 12412.0 | 960 | 192 |
| 33002 | 50714 | 626001690 | 12343.8 | 950 | 192 |
| 33003 | 50488 | 631323795 | 12504.4 | 970 | 196 |
| 34000 | 50701 | 627288726 | 12372.3 | 957 | 198 |
| 34001 | 50388 | 641482299 | 12730.9 | 991 | 201 |
| 34002 | 50679 | 621461453 | 12262.7 | 941 | 192 |
| 34003 | 50633 | 618963775 | 12224.5 | 937 | 192 |
| 35000 | 50596 | 638701177 | 12623.6 | 980 | 200 |
| 35001 | 50800 | 639915693 | 12596.8 | 983 | 204 |
| 35002 | 50299 | 629212344 | 12509.4 | 961 | 198 |
| 35003 | 50945 | 633021852 | 12425.6 | 965 | 196 |
| 36000 | 50540 | 624367908 | 12353.9 | 951 | 188 |
| 36001 | 50676 | 621833529 | 12270.8 | 944 | 190 |
| 36002 | 51093 | 624516602 | 12223.1 | 947 | 190 |
| 36003 | 50668 | 629750954 | 12429.0 | 962 | 195 |
| total (24) | 1215886 | 15073234671 | 12396.9 | | |

## Appendix B. The generator

`python3 r39joint.py --gen-c > gen39b.c`, then `python3 -m ziglang cc -target wasm32-freestanding -Oz -nostdlib -fno-builtin -Wl,--no-entry -Wl,--export=gen -Wl,--export=g_nreg -Wl,--export=g_dppol -Wl,-z,stack-size=8192 -Wl,--initial-memory=65536 -Wl,--max-memory=65536 -o gen39b.wasm gen39b.c`: 3,849 bytes, sha256 `d6a1fedd47d51e2a268264768836f83a59723d7a6b1ddd97508c4f2f3e76787c`, 1,649 WebAssembly instructions. With `R39_WASM=gen39b.wasm` (and the `wasmtime` package) the program charges the executed operators of each generation (wasmtime fuel, one operator = one operation): mean 523.6k, standard deviation 8.0k, maximum 543k over 200 first blocks; it emits records equal, line by line, to those of the Python generator `make_kernels_folded` of section [2] (200 first blocks, both banks). Without the module the program charges the halt cap 575,000.
