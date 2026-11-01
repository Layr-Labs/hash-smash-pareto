# SHA-256 r39: composition with the 710-record kernel filter

Target `sha256-r39-prefix-v1`: standard IV, first 39 steps in every compression, FIPS padding, feed-forward and all 256 output bits. Claim: time 116.591, memory 20, preprocessing 43, success at least 0.39, advice 160 bytes. The computed time logarithm is 116.590863562833. Production storage is 1,044,640 bytes; a conservative envelope also reserving the diagnostic 1024-record image capacity is 1,047,780 bytes, below one MiB.

The exact direct base is Jbenisek's published `2ae904e3-edb6-4484-a68b-26c897e06f03` at time 116.596, package `5ba114282c022c8e5512b914a7884bcecb45df210d92dad5d941a5bb12e05034`. Its reusable technique is to accept a first block only when its folded kernel has at most 710 records, with at most 32 attempts per window, paying for rejected blocks. This replaces fce2f19e's 780-record/eight-attempt policy and changes which chaining values are walked. We retain that selection, every random draw, every accepted kernel, the advice and the tail source. The new reductions are the recent-reset scan masks and the 128-lane merge search. They do not overlap the base's kernel-selection change.

Declared dependencies are `2ae904e3-edb6-4484-a68b-26c897e06f03`, `fce2f19e-04eb-405f-b7d5-e24260d85d13` and `5f8e6192-60b3-4ba1-bded-d3b73cfbc889`. These preserve the complete direct declaration published by the base and add the base itself. The earlier program, transplant, claw, tail and cost-model contributions are credited through those sources to sraiw, Jbenisek, dkuthoore, dariolina, mitchuski and lamb356. This is not a claim to have invented the characteristic, advice, claw construction or tail estimator.

There is also a conservative accounting repair. The base computes `consts(cv)` for each attempted first block but places its 140-operation setup charge after the rejection loop. This candidate also charges that existing full allowance on each rejected attempt, changing the retry charge from two to 142. It changes cost bookkeeping only, not selection or walk state. Across the 82 rejected blocks in the declared full sample it adds 11,480 operations. Even with that extra charge, the full sample falls from 11,110,939,965 to 11,078,000,642, saving 32,939,323. No saving is obtained by omitting rejected setup.

## 1. Target and output

SHA-256 with 39 steps in every compression, FIPS 180-4 padding, the standard IV, feed-forward after step 38, all 256 digest bits. The output is two distinct 128-byte messages `M0 || M1` and `M0 || M1'`: the same first block, second blocks that give the same chaining value after the second compression; the padding block that follows is identical, so the two digests are equal. The first block `M0` is a random block, `cv = compress39(IV, M0)`.

## 2. The construction (sraiw 38912d66, dariolina)

**2.1 The base is advice: the inherited pair on the published characteristic.** The advice is the inherited 39-step semi-free-start collision (`CV_PUB`, `M_PUB`, `MP_PUB` of `experiments/r39joint.py` section [1]; 160 bytes), printed with its signed characteristic and recompute in Appendix C. Its signed characteristic is the 39-step characteristic of ePrint 2026/1120 Tables 21 and 23 unchanged (pair inherited from the credited 5f8e6192 lineage): every signed row, state and message schedule, is the published one, only the values differ, and `W16 = 0xbca1c321` and `W17 = 0x71e9ba98` are the published values. The state and message values are this pair's own, which is why the tail is re-measured on it (Section 8). It is a collision of the 39-step compression from `CV_PUB` (experiment `r39-transplant-claw`, trial 0; `compress39` equals the organizer's `verifier/hash_functions.py` on 300 random blocks). Its trajectories `BA, BE` (`M'`) and `CA, CE` (`M`) are expanded from the 160 bytes by two compressions at the start of the run (charged 2 x 2812 + 120 operations, `Attack.base_setup`).

**2.2 The transplant.** Write `A[r]` and `E[r]` for the two state registers after step `r-1`, `a0 = A[4]`, `a1 = A[5]`, `u = W1`. Fix `A[6..9]`, `E[10..13]` and `W10..W15` to the published values of `M'`. For any chaining value `cv` and any `(a0, a1)`, steps 0 to 9 then determine `W0..W9` uniquely (`build(cv, a0, a1)` in section [1]); the partner message takes `W8 + D8`, `W9 + D9` and the published `W10..W15` of `M` (`second`). Both messages then follow the published trajectories `A[6..19]`, `E[10..19]` (steps 0 to 15 only, an identity of the step function, not a probability). The map `(cv, a0, a1) <-> (W8, W9, W16..W23)` is a bijection (320 bits, triangular). Experiment `r39-transplant-claw`, trials 1 to 255, checks the identity on 255 random chaining values.

**2.3 Row 16 is a claw.** `W16 = sigma1(W14) + W9 + sigma0(W1) + W0`. With `a1 = u + h(a0, cv)` (`recover_a1`) one finds `W16 - g = F(u) - F(a0)` (mod 2^32), where `g = 0xbca1c321` is the published `W16`, `F(x) = F_even(x)` for even `x` (a 32-bit expression in `x`, `S0(x)`, `MAJ`, `S1`, `CH` and six constants of the first block: `consts`, `fstep`) and `F(x) = sigma0(x) - x` for odd `x`. So `W16 = g` exactly when `F(a0) = F(u)` with `a0` even and `u` odd: a claw of the map `F` on 32-bit words (checked in `r39-transplant-claw`, `w16_identity`). Claws are found by a van Oorschot-Wiener walk (Section 3).

**2.4 What remains to pay, after a claw.** (i) `W8 in F8` and `W9 in F9`, where `F8 = { w : sigma0(w + D8) - sigma0(w) = 0x087ff000 }`, `F9 = { w : sigma0(w + D9) - sigma0(w) = 0x03010000 }` (`inF`); both sets depend only on 14 and 17 active bits of `w`, with exactly 1152 / 2^14 = 9/128 and 2080 / 2^17 = 65/4096 members (enumerated; the active-bit masks `0xCC19E60C` and `0xF9983C0F`), so `p8 p9 = 585 / 524288 = 2^-9.807707`. (ii) `W17 = 0x71e9ba98`, the published `W17` (the program tests it on every claw): probability 2^-32 for a uniform `W17`; the entry needs only that this value works (`solve_row_exact` in `r39-transplant-claw` trial 0 verifies `|G16| = 2`, `|G17(0xbca1c121)| = 0`, and `|G17(g)| = 1` with `G17(g) = {0x71e9ba98}`). (iii) The tail: rows 18 to 38 (`W18..W23` are the six free words of the bijection) must end with equal states after step 38: probability `p_tail`, Section 8.

Events (i) to (iii), together with `W16 = g` and the parity `a0` even, `u` odd, imply the collision: the pair then follows the published trail through row 17 and its remaining rows hold with the tail event. The program ends by compressing the pair and comparing (`Attack.claw`, last block). (`r39-transplant-claw` trial 0 checks the claw equation `fstep(a0) = s0(u) - u` of the advice pair directly and runs the filters with check mode off, as in Jbenisek's 2b4af365.)

## 3. Program and exact rewrites

Each window constructs a random first block `M0`, compresses it from the standard IV to `cv`, and derives the constants of the 32-bit claw map `F`. It generates two bank-swapped 256-lane bit-sliced kernels. A generation exceeding 710 records, 206 registers, or 575,000 charged generator operations is rejected and charged; at most thirty-two attempts are made. The table is cleared and 256 trails start with IDs 0 through 255. Production uses `WIN=2^26`, `DPB=7`, `MAXS=1536`, `CUTP=512`, `LMIN=32`, `QFULL=3328`, `QCAP=3584`, `WHEEL=2048`, `D0=82`, `KRES=6` and `CMP1=10`.

Stage 1 performs `2^18` kernel iterations. A point is distinguished when its low seven planes are zero. DP lanes are visited in ascending order and batched into non-overlapping 25-bit extraction windows. One Horner pass extracts each group's high 25 bits. The bucket is `floor(167*r/2^15) = floor(171008*r/2^25)`; the packed table record is `chk(8) | length(11) | id(20)`, with `chk=r mod 256`. A bucket spans at most 197 consecutive values, so bucket plus checksum identifies `r` without false matches. A 39-bit record crossing a word boundary uses a second load/store. Keep-longer and the length-32 short-trail skip are unchanged. A match queues the two trail IDs and length difference in the unchanged 64-bit pair layout. Every restarted lane receives the next ID in the original order.

Stage 2 runs pairs in slots `(p,p+128)`. Long catch-up trails can start in any half-free lane; the other endpoint launches through the unchanged timing wheel. Moves, drops, batching, flushes, parking and resume order are unchanged. Every insert batch flushes before a move, kernel step, park or drain. All ten low planes are compared first; the remaining twenty-two planes are compared for surviving candidates. The first equality produces the predecessors. Opposite parity invokes `claw`; F9, F8, W17 and full collision verification remain in their original order. On success the program emits the two 128-byte messages with their common first block. The common padding block then preserves equality of the full target digests.

The queue cannot overflow: before a DP iteration it has fewer than 3328 entries and an iteration can add at most 256, so the peak is at most 3583. A trail is cut once its age reaches 1536 at a scan, with at most 511 intervening iterations. Recorded lengths are below 2048. If the 20-bit ID space is exhausted, stage 1 stops and the final stage 2 drains. These invariants are preserved by the following rewrites.

### 3.1 Recent-reset masks

Let `C=CUTP`; both production and the forced test use `MAXS=3C`. At a regular scan time `t`, three masks record DP restarts in `(t-C,t]`, `(t-2C,t-C]` and `(t-3C,t-2C]`. Their union contains only lanes younger than `MAXS`. The candidate visits its complement, retaining the original age and ID checks. It removes the lowest set bit each time, preserving the original ascending order and hence the assigned IDs. Cuts need not be added to the masks: omitting a recent cut can only cause an extra age check, which rejects an early cut.

For ID `i<2^20` and birth time `b`, the existing lane encoding is `LA=i-(b+1)*2^20 mod 2^256`. In the program's bounded iteration range, the original unsigned threshold comparison is exactly `b<=t-MAXS`. Thus skipping a lane marked by a genuine reset cannot skip a required cut. Each DP iteration adds its original DP mask once before the hit handler consumes it. The masks rotate on every scheduled scan, including scans before `MAXS`.

`cut_at` records the next expected scan time. A direct time jump falls back to the original full scan and clears the masks. ID exhaustion also selects the full scan because a DP bit may then refer to a restart refused by the original handler. Clearing masks is conservative; future masks contain only later resets. The original per-lane guard still handles exhaustion reached during the scan itself. Initialization costs four charged register sets; the DP accumulation, rotation, tests, loop, calls and resets all use explicit `Mach` charges. The code counts separate static blocks for the fast and fallback paths.

### 3.2 A 128-lane merge search

The active-pair mask `bact` has bits only below 128. It starts at zero. Paired launches and moves draw IDs 0–127 from the free stack; in-place callbacks originate from those launches; free-partner callbacks set `q & 127`; and merges remove such a bit and return its index to the stack. This inductively preserves both the stack range and the `bact` range. Since `full` is a subset of `bact`, its merge search never needs index bit 7. The specialization omits the known-zero high-bit test and the OR into zero, saving four operations per merge. Other callers keep the full 256-lane search. Both static instruction bodies are charged: 26 census instructions for the generic search and 22 for the specialization.

The local equivalence verifier checks 4,864 bounded reset histories, including time jumps and exhaustion, and 524,536 lane masks. All six corresponding incorrect mutants fail. Algebra supplies the general interval and range arguments; the finite checks supplement it. A tested additional comparison stage preserved semantics but increased full-window cost and was rejected. No new comparison stage is shipped.

### 3.3 Composition with the first-block filter

The rejection loop, its random draws, `KCAP=710`, `KTRY=32`, register/fuel limits and emitted kernels are unchanged. The four cache fields are initialized only after a kernel has been accepted. Neither the reset masks nor the narrowed merge search is used during selection. Thus the interval and active-lane arguments above hold for every selected map, independently of how that map was selected. A window with all 32 attempts rejected still returns no walk groups; it incurs all trial costs and needs no cache initialization.

The additional constant-setup allowance is outside all selection predicates. `Mach.o` is not an input to a branch condition inside `Attack`; the generation limit tests use `gops`, and kernel/ID/queue decisions use their original state. The extra charge is exactly `140*kskip`, including all-rejected windows. Direct probes compare complete state and RNG state for zero, 12 and 19 rejections, and synthetic three/32-rejection exits. A mutant omitting the charge fails. The global work halt is recalibrated to the resulting ledger; per-window search events and order are preserved.

The inherited advice diagnostic temporarily raises `KCAP` to 1024 for the fixed `CV_PUB`, whose image has 730 records, and restores it before checking the claw. This is not an exception to production selection. The inherited ID-stop fixture starts at `2^20-1998`, so its stop remains inside a partly restarted hit group on its fixed seed. Both details are retained.

## 4. Machine model and prices

The unchanged collision-frontier-v5 convention is a classical 256-bit word RAM. A 39-step target compression costs 2812 operations. XOR, AND, OR, NOT, move, shift, rotate, add, subtract, compare and set cost one each; a conditional branch is compare plus branch, two; a load or store costs three for index shift, base add and access; a call plus return costs two. A register-to-register Boolean kernel record costs five stored bytes. Every other instruction costs 36 bytes. The kernel and all counted primitives remain those of the pinned base.

`Mach.o` records executed operations. `Mach.blk` records the static census convention: the maximum straight-line pass per named block, with a callee body counted separately and calls/returns accounted for. The new scan branches have separate blocks. Loop bodies that represent fixed register-plane programs are unrolled in this machine model; the two `find_lane` parameter values denote two charged static bodies. Measurement dictionaries, distinct-claw sets, trace hooks and Python interpreter overhead are external bookkeeping, not an implementation of the attack's memory or time model. The production driver disables the distinct-set measurement.

The generator's WebAssembly operators are charged when the module is supplied. The reported replays use the conservative fallback halt cap of 575,000 operations per attempted generation, plus eight relocation operations per kernel record. The Python generator is the readable reference for the same emitted Boolean records. No lower native generator price is substituted into these measurements. Appendix B retains the unchanged generator construction and its prior byte-identity evidence.

For the reported fallback-counter runs, a rejected random first block is charged 2830 operations for randomness/storage/compression, 575,000 for generation, 140 for constant setup and two for retry control: 577,972. Successful setup keeps its existing 140-operation charge. The full allowance is conservative if some accepted-only constants need not be retained on a rejected attempt. The same constant-derivation routine already exists; charging another execution does not add another static instruction image.

## 5. Exact measured ledger

All 24 predeclared windows were rerun on the pinned base and this composition, sequentially on one CPU. Each has `2^26` walk evaluations in check mode. The final source SHA-256 is `df64e3dae86698ae160a030e6be69765b2f1db6a854c88be86588f8f6471a4cb`. The final sample contains 1,418,511 distinct claws and 1,416,345 groups. Its exact mean work is `5539000321/12`, rounded up to `mu+=461,583,361`. Sample standard deviation is 3,418,915.272379 operations and maximum observed work is 469,996,856.

The measured mean claw and group counts are 59104.625000000 and 59014.375000000; sample standard deviations are 185.000778494 and 183.229913188. Frozen pricing rates are `c-=59104.62`, `g-=59014.37`, `r-=0.998473`. They are assumed bounds on true complete-window expectations under H1, not confidence limits established by the finite sample. The sample has 82 rejected first blocks and no all-rejected window; the maximum is 19 rejections in one window. H1 must include the possible zero-yield outcome at the 32-attempt cap.

Aggregate work is 7809.597981263 operations per distinct claw; per-window ratios range from 7688.781190 to 7963.753766. The exclusive categories below remove accepted generation from setup and kernel work from stage-2 control. `setup_and_rejections` includes all unsuccessful trials and their added setup charges. These unrounded subtotals sum exactly to 11,078,000,642.

| Category | Operations over 24 windows | Operations/claw |
| --- | ---: | ---: |
| `accepted_generator` | 13,934,008 | 9.822982 |
| `cuts` | 268,780 | 0.189480 |
| `hits` | 2,335,242,110 | 1646.262955 |
| `run_setup` | 137,856 | 0.097184 |
| `setup_and_rejections` | 49,985,296 | 35.237863 |
| `stage1_walk` | 4,454,088,704 | 3139.974737 |
| `stage2_other` | 1,792,740,124 | 1263.818274 |
| `stage2_walk` | 2,431,603,668 | 1714.194439 |
| `window_end` | 96 | 0.000068 |

The paired saving is 32,939,323: reset masks save 19,421,675, the narrowed search saves 13,529,128, and rejected setup adds 11,480. Every production window improves. The transformations are not pointwise cheaper for every configuration: forced cut adds 18,478, forced-unpark adds 17,954, ID-stop adds 1,428, and advice setup adds 4. All those cases preserve full semantic state and order.

**Hard window bound.** The existing `R=2^51` bound remains conservative. Stage 1 has at most `2^18` iterations, at most 256 hit lanes per iteration and fewer than 4096 operations per lane; even charging a full scan below `2^16` operations on every iteration leaves it below `2^39`. The stage-2 search becomes cheaper, while trail lengths, occupancy, queue capacity and park/resume rules stay fixed; the base's stage-2 bound remains below `2^50.3`. Thirty-two capped generation attempts, including at most 4480 added setup operations, fit in the remaining margin. This resource bound does not depend on average seeds.

## 6. Memory, source and register inventory

| Production item | Bytes |
| --- | ---: |
| `advice` | 160 |
| `constants_counters` | 4,096 |
| `free_stack` | 128 |
| `kernel_images` | 7,100 |
| `lanes` | 8,192 |
| `other_instructions` | 148,068 |
| `parked_scalars` | 192 |
| `queue` | 28,704 |
| `records` | 1,024 |
| `registers` | 8,192 |
| `save` | 1,024 |
| `table` | 833,664 |
| `wheel` | 4,096 |
| Production total | 1,044,640 |

The census is 1248 instructions in 71 blocks. With the unchanged 1100 routine instructions and 1753 generator plus 12 relocation instructions, 4113 non-kernel instructions occupy 148,068 bytes. The two production images reserve `2*710*5=7100` bytes. The generator's scratch and discarded candidate construction remain in the table arena before the walk table is initialized, as in the base; reducing the accepted image cap does not reduce that scratch allowance.

For a conservative envelope, reserve two 1024-record images as well, covering the diagnostic cap rather than only the actual 730-record advice image. This gives **1,047,780 bytes**, leaving 796 below `2^20`. The claim remains memory 20. The sequential preprocessing representation is inherited from Section 11 and fits inside the same overall arena; no 93-pair history is retained online.

Four persistent scalars are added: `cut0`, `cut1`, `cut2`, `cut_at`. Across a stage-2 kernel step there are 3 driver values, 8 stage-1 values including these four, 10 stage-2 values and 7 claw constants, totaling 28. The deepest point adds at most 12 temporary values and 3 insertion-batch registers, then at most 3 return links: 46. The stage-1 peak is also 46. This fits the existing reserve of 48 scalars beside at most 206 kernel registers. The added retry charge changes accounting for an existing routine, not the live-register inventory. These are declared word-RAM/hand-counted layouts, not Python RSS measurements.

The two declared experiment sources total 63,009 bytes, below the 65,536-byte review cap. External trace hashing adds no normative source bytes or attack work. The complete static-block census is:

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
| `cut_lane` | 15 |
| `cut_linear` | 4 |
| `cut_mask` | 3 |
| `cut_pending` | 3 |
| `cut_reset` | 3 |
| `cut_roll` | 6 |
| `cut_test` | 2 |
| `cut_threshold` | 3 |
| `delta_lanes` | 74 |
| `extract25` | 74 |
| `extract32x2` | 96 |
| `find_lane` | 26 |
| `find_lane128` | 22 |
| `fpop` | 9 |
| `hb_add` | 7 |
| `hb_close` | 2 |
| `hb_ext` | 1 |
| `hb_init` | 4 |
| `hb_ins` | 1 |
| `hb_last` | 2 |
| `hb_lp` | 2 |
| `hb_sel` | 6 |
| `hb_v` | 4 |
| `hit_a` | 38 |
| `hit_c` | 9 |
| `hit_m` | 22 |
| `hit_n` | 17 |
| `insert_lane` | 94 |
| `iter1` | 7 |
| `iter1c` | 3 |
| `iter1h` | 8 |
| `l_end` | 2 |
| `l_f2s` | 2 |
| `l_half` | 1 |
| `l_pair` | 16 |
| `l_single` | 7 |
| `l_try` | 11 |
| `launch` | 6 |
| `launch_t` | 4 |
| `link` | 32 |
| `merge` | 28 |
| `move_lane` | 130 |
| `qflush` | 5 |
| `qins` | 11 |
| `qpop` | 8 |
| `qpush` | 15 |
| `s2_fl` | 1 |
| `s2_in` | 20 |
| `s2_init` | 22 |
| `s2_out` | 20 |
| `s2_q` | 4 |
| `s2_step` | 2 |
| `s2_susp` | 4 |
| `w_end` | 6 |
| `w_s2` | 5 |
| `wheel_check` | 15 |

## 7. Success and the live work budget

The inherited mean-price model uses `p=(585/524288)*2^-32*2^-74.3238`. With `lambda=-ln(0.60999)` and `G=lambda/p`, `log2(G)=115.115003108584`. H5 assumes independent group trials, giving conditional success at least `1-exp(-lambda)=0.390010`. The claw planning target is `N=G/0.998473`, with `log2(N)=115.117207787612`.

The actual program keeps `B_WINDOWS=762275399377730730492917603366`. This literal integer satisfies `B*g-*(1-2^-20)/G=1.000000871752>1`. Group counts are bounded by `2^26` per complete potential window, and the group shortfall exponent has log2 39.963784415184. Potential windows are independently sampled before global stopping; continuing virtually past a success only increases required work. The production attack may stop earlier at its first success.

Let `X_i` be complete-window charged work, including all generation attempts and their setup allowances. H1 assumes `E[X_i]<=mu+=461583361`, with `0<=X_i<=R=2^51`. The shipped constant is

```
B = 762275399377730730492917603366
W = 351853976406170674087385034931932625026
W = floor(B * 461583361 * (1 + 2^-20)) + 1
d = W/B - 461583361 - 6
```

The six driver operations are included in the slack. Its value is 434.200196266174. Hoeffding bounds work failure by `exp(-2*B*d^2/R^2)`. The exponent's log2 is **15.79066020475548**, so the conservative floor is **15.7**, not 16.0 or the previous package's 15.8. Work failure and the much smaller group failure together are at most `2*exp(-2^15.7)`. Thus success is at least `0.390010-2*exp(-2^15.7)>0.390009>0.39`, conditional on H1/H2/H5.

The driver halts at success, after B windows, or when its accumulated work reaches W, checked before starting another window. The conservative bound, retaining the extra driver term, is

```
T = (W + 2^51 + 6*B)/2812 + 2^43
log2(T) = 116.590863562833
time_log2 = 116.591
```

Preprocessing 43 covers the inherited 93-pair construction/selection charge; it is not lowered back to 36. The exact declared selection sum `93*2^36 + 93*14*2^24` is below `2^43`. Using that envelope is conservative relative to the base's displayed `2^36+2^42.545` expression and leaves the same three-decimal rounding. The normalized time-memory claim is also 116.591, because the memory envelope stays below one MiB. The hard resource cap is unconditional; the true expectation, uniformity, tail and independence premises are not established by 24 samples.

## 8. The tail p_tail (rows 18 to 38)

Definition (unchanged from 4487063 and 19034ce). Distribution `U`: `E16`, `E17` of the first member pinned to the published values (this fixes `W16 = g`, `W17 = 0x71e9ba98`); `W8` uniform on `F8`, `W9` uniform on `F9`, independent; `E18..E23` of the first member independent and uniform on 2^32 (`W18..W23` are a bijective image of them); everything else is determined by the real step function and message expansion. `Q = P_U(collision and K_P | a0 even, u odd) = 4 P_U(collision and K_P and a0 even and u odd)`, where the collision test is exact (equal 256-bit outputs of the two 39-step compressions) and `K_P` is an importance carrier (the printed cells of Tables 21 and 22 of rows 16 to 18, signed differences only for rows 19 to 22, `E23[30] = 0`). `K_P` is a subset of all routes to a collision, so `Q <= p_tail`; the claim prices `p_tail = 2^q_tail` with `q_tail` = -74.3238, the linear mean of the 14 runs (best-case premise: the tail probability equals its measured mean; the hard-asserted linear 99.9% bound is -74.4326).

Priced value and check value. The claim prices `q_tail` = -74.3238, the linear mean of the 14 runs (best-case premise, declared). The replica hard-asserts the conservative check value `QDECL` = -74.45, fixed before the organizer runs by the pre-registered rule: at least 0.01 below the one-sided 99.9% Student-t lower bound (t = 3.852, 13 df) of the frozen design, rounded down to two decimals. Design (frozen before the runs): the same estimator as 4487063 and 19034ce - trial 0 an SMC over `E18..E23` with 800 particles, exact 1- and 2-step look-ahead and multinomial resampling, trials 1..20 the rows-24..38 Monte Carlo - with the work re-allocated inside the organizer's 16-experiment and 20-second limits: stage lanes per particle 8x512 (row 18), 8x2048 (19), 8x2048 (20), 4x128 (21), 6x256 (22), 1x4 (23) - 19034ce used 1x512, 5x2048, 3x2048, 1x128, 1x256, 1x4 - and 20 trials x 80 batches x 2048 proposals = 3,276,800 proposals per run (2.0 times as many), every particle driving exactly two batches. Three constant-factor changes only: lazy pool candidates (a pool entry is the packed pair (parent index, E); the candidate's row values are recomputed for the row and look-ahead checks, never stored), `CH = g ^ (e & (f ^ g))` and `MAJ = (a & (b | c)) | (b & c)` in the packed hot paths (3 and 4 operations instead of 4 and 5, bitwise identities), and per-width cached packed constants for the trace. The v2 program, run with the published advice at 19034ce's exact parameters (`CFG 1x512, 5x2048, 3x2048, 1x128, 1x256, 1x4`, `NCH = 10`), reproduces 19034ce's outputs byte-identically - carrier, stage counts, per-trial hits and parity classes, the same RNG draw order and count - on three private seed sets, so the estimator, the filters and the Feynman-Kac product are unchanged and only their variance changed. (The regression variant is the shipped file with two constant edits - `CFG = {18: (512, 1), 19: (2048, 5), 20: (2048, 3), 21: (128, 1), 22: (256, 1), 23: (4, 1)}` and `NCH, NB, LF = 10, 80, 2048` - which the 64-KiB two-program source budget does not allow to ship alongside the shipped configuration; the byte-identity was checked on the carrier, all stage counts, every per-trial hit list and the parity classes.)

Evidence: the replica `experiments/r39tail.py` runs in the organizer sandbox as `r39-tail-01` to `r39-tail-14` (Section 10) and embeds the exact 14-run table `EXP` (packed, one line per run: stage counts `k18..k23`, `log2_carrier`, total verified hits, parity classes) and `verify_smc_stats()` with hard `assert` statements. By Del Moral's Feynman-Kac theorem, the unnormalized product estimator `Q'_r = 2^(l2_r) * (hits_r / 3276800)` is an exactly unbiased estimator of `Q'` on the linear scale (`E[Q'_r] = Q'`, zero log-scale Jensen bias). On every run, `verify_smc_stats()` hard-asserts: (1) direct stage-18 Monte Carlo calibration (`c18 == 206` out of `65,536` uniform draws, matching the 14-run SMC stage-18 rate within `0.0003`); (2) 6,398 verified collisions in 45,875,200 proposals across the 14 runs with parity classes `[1592, 1626, 1624, 1556]` (`chi-square = 2.03 < 7.81`); and (3) linear-scale unbiased sample mean `log2(mean(Q')) = -74.3238`, one-sided 99% Student-t lower confidence bound `log2(lcb_lin) = -74.3978 > -74.45`, log-scale 99% bound `-74.3987 > -74.45`, and the linear one-sided 99.9% bound `-74.4326 > -74.45` (t = 3.852, 13 df; sample sd of `log2(Q')` 0.1011). Measured sandbox wall time 12.9 to 13.7 s per run on the sizing host (ten private-seed runs of the frozen configuration in the same pinned image and sandbox flags; limit 20 s).

Selection and the tail coverage (answers `F-LC-TAIL-SELECTION` and `F-EXP-PUBLIC-SEED-SELECTION`). The shipped pair was chosen among 93 candidate pairs by the tail measurement (Section 11, Section 12); no holdout is claimed. The selection is covered by a Bonferroni correction over all 93 screened pairs, which holds for the selected pair under any selection rule over the 93: per-pair level `alpha/93`, `t_13` quantiles 5.0692 (family-wise 99%) and 6.4547 (family-wise 99.9%), on the same linear-scale estimator as `verify_smc_stats()` over the 14 runs, give family-wise lower bounds `log2 = -74.4688` (99%) and `-74.5112` (99.9%). The claim keeps pricing the linear mean `-74.3238` (declared best-case premise `H2-tail`); priced at the family-wise 99% bound `-74.4688` the time would be 116.7402 (1 bit of `log2 p_tail` moves `time_log2` by 1 bit, Section 7).

## 9. Premises and limits of the composition

**H1-claw-model.** The retained kernel filter conditions which first blocks and claw maps are used. H1's yield, free-word uniformity and mean-cost premises must hold for this selected distribution and the finite 32-attempt rule, including possible zero-yield all-rejected windows. The priced true expectations are work at most 461,583,361, claws at least 59104.62 and groups at least 59014.37, with ratio 0.998473. These are best-case mean-price assumptions, not confidence limits. Exact parity proves that the composition preserves the new leader's selected maps and events; it does not prove that filtering cannot bias W17 or the tail.

**H2-tail.** The same advice, tail source, fourteen-run EXP table and priced mean `-74.3238` are retained. Section 8 includes the inherited selection-aware diagnostics and their assumptions. The public seeds and selection among 93 pairs remain limitations. No new tail estimate or independent holdout is introduced.

**H3-advice-construction.** The dense-state dimension count and 256-candidate local slice do not execute the full `2^34` search. The inherited construction/screening charge is retained at preprocessing 43, and its sequential representation is an explicit model rather than a newly measured 93-pair campaign.

**H5-group-independence.** Grouping shared endpoints, tuple uniqueness, chi-square and lag-1 checks do not prove full-word or tail independence. The success amplification remains conditional on this premise. Complete-window state hashes are local deterministic evidence, not an organizer verification of an infeasibly long `2^99`-window run.

The counted-word instruction representation, generator macro prices and register allocation remain declared accounting conventions. The new retry allowance conservatively prices a visible per-attempt setup obligation; it does not claim a new lower price for generation. No metadata is treated as an official qualification or human acceptance.

## 10. Experiments and exact state evidence

`r39-transplant-claw` retains the temporary 1024-record diagnostic cap for `CV_PUB`, then restores production parameters. The advice kernel has 730 records, the claw costs 6140 and its census is 121. Advice collision/filters, exact row fibres, downward inversion and the 256-candidate local slice are checked. Trials 1–255 check the transplant identities; this is not an ordinary fixed-IV certificate.

`r39-window-small` runs four windows of `2^22` evaluations with the retained selection policy. Its exact assertions are:

| Observation | Four values |
| --- | --- |
| `distinct_claws` | `[834, 821, 859, 806]` |
| `distinct_groups` | `[834, 821, 859, 806]` |
| `dp_hits` | `[32470, 32624, 32731, 32819]` |
| `matches` | `[1724, 1706, 1788, 1698]` |
| `stage2_iterations` | `[2458, 2356, 2867, 2867]` |
| `raw_claws` | `[853, 843, 881, 830]` |
| `passed_f9` | `[16, 9, 16, 10]` |
| `passed_f8` | `[0, 0, 1, 0]` |
| `f8_all` | `[49, 53, 64, 60]` |
| `w17_low8` | `[4, 8, 4, 4]` |
| `w17_low12` | `[0, 0, 0, 1]` |
| `kernel_records` | `[709, 688, 708, 700]` |
| `ops` | `[22263252, 21235185, 22064071, 21298995]` |
| `blk_census` | `[1111, 1111, 1187, 1111]` |

The 3320 distinct group tuples are unique within their windows. The actual pooled low-byte chi-squares are 285.9 for W17 and 220.67 for W18; all three lag-1 tests satisfy `|r| sqrt(n)<3`. These replace the unfiltered fce2f19e sample's different counts; no old 3301-claw statistic is claimed as this selected sample.

The forced trial uses `QFULL=64`, `MAXS=192`, `CUTP=64`, compares an unparked run and restores settings. It finds 482 distinct claws, 485 raw claws, 32750 hits, 932 matches, 715 stage-2 iterations, 14 parks, 14 resumes and 7202 cuts, with zero drops. Its exact operation/census pair is **22443854 / 1189**. Operations include the final direct time jump and 256-lane cut check; the cut count is captured before that check. ID exhaustion starts at `2^20-1998`, stops at iteration 994 and drains 203 stage-2 iterations, still exercising the partly restarted group.

The forced, unparked-forced, ID-stop and advice-setup cost changes are respectively +18478, +17954, +1428 and +4. Their state, counter and event parity is exact. Bounded checks rerun 4864 cut histories and 524536 lane masks and kill the incorrect mutants. The retry allowance has separate state/RNG and cost-delta probes, including all-rejected windows; its missing-charge mutant fails.

Both joint organizer experiments run twice against final source bytes under one CPU, no network, 128 MB and a 20-second limit per execution. Full 24-window runs occur separately under the external one-CPU verifier and are labelled local evidence, not 20-second organizer execution. The unchanged tail hash is `79831aa56a5b99afd3b7210486d82b67152693dac76b2acadf9c845e29b3ce18`; the known-answer, calibration 206 and embedded statistics are checked, while the fourteen large tail runs are retained rather than presented as a new local simulation campaign.

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

The peak of the selection is `max(2^16, 62,144) = 2^16 = 65,536` bytes, inside the `2^20`-byte arena of Section 6, so `memory_log2_bytes` stays 20. (Stage lanes are recomputed per row and look-ahead check, never stored, Section 8.)

The claim retains preprocessing 43 for this full selection process. Adding the conservative `2^43` envelope to the live online ledger gives total logarithm 116.590863562833, rounded up to 116.591. The construction-scale and selection-model limitations remain H3/H2 premises.

## 12. Reuse, accounting and remaining obligations

The new leader's reusable technique is amortized first-block selection by folded-kernel size: generation is paid once, while the selected kernel repeats through hundreds of thousands of walk iterations. Its changed chaining-value distribution and bounded retries must be included in H1. The composition retains those choices, all rejected and accepted draws, and every kernel record. The two verified reductions operate after selection and therefore do not compete with it.

The full constant-setup allowance is now charged on failed attempts as well as success. This is a conservative accounting repair to existing work, not a new search heuristic. The advice diagnostic and ID-stop fixture stay as the new leader defines them. No stage-comparison, queue representation, advice, tail or dependency path is silently replaced with the previous 116.614 package.

The work-concentration floor is recomputed from this program's actual B/W/mean and six driver operations. The lower average changes the supported floor, so neither the inherited 16.0 nor a hard-coded 15.8 is used. The source/generator pricing, scalar hand count and H1/H2/H3/H5 extrapolations remain explicit obligations. Local checks and a smaller declared cost do not establish official qualification.

## Appendix A. All 24 composed windows

All seeds are retained, one CPU at a time, in check mode, with every generation charged at the fallback cap. The 82 rejected blocks and the selected kernels match the pinned leader exactly. These are the same seed multipliers 1–24 used by `--windows 1 --seed S`; the external verifier receives seed integers 1000 through 24000 directly.

| Seed | Claws | Groups | Operations | Operations/claw | Kernel records | Registers | Rejected blocks |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1000 | 59079 | 58983 | 460722071 | 7798.406727 | 701 | 132 | 0 |
| 2000 | 59262 | 59171 | 457924503 | 7727.118609 | 677 | 129 | 12 |
| 3000 | 58871 | 58782 | 461048006 | 7831.496085 | 702 | 131 | 0 |
| 4000 | 59164 | 59076 | 465311486 | 7864.773950 | 710 | 133 | 0 |
| 5000 | 59565 | 59478 | 464553146 | 7799.095878 | 709 | 131 | 0 |
| 6000 | 59231 | 59135 | 460528321 | 7775.123179 | 699 | 133 | 1 |
| 7000 | 59153 | 59059 | 464042210 | 7844.778963 | 710 | 130 | 0 |
| 8000 | 59242 | 59142 | 462444500 | 7806.024442 | 698 | 131 | 3 |
| 9000 | 59006 | 58917 | 459801852 | 7792.459275 | 697 | 131 | 2 |
| 10000 | 58704 | 58620 | 457133074 | 7787.085616 | 692 | 131 | 0 |
| 11000 | 59010 | 58924 | 462973570 | 7845.679885 | 679 | 131 | 19 |
| 12000 | 58867 | 58790 | 458352246 | 7786.234155 | 691 | 134 | 2 |
| 13000 | 59337 | 59241 | 461889344 | 7784.170821 | 700 | 130 | 3 |
| 14000 | 59133 | 59034 | 461483357 | 7804.159386 | 704 | 129 | 0 |
| 15000 | 59093 | 59007 | 461383842 | 7807.757975 | 700 | 133 | 1 |
| 16000 | 59257 | 59163 | 455614107 | 7688.781190 | 685 | 133 | 2 |
| 17000 | 59153 | 59070 | 460686367 | 7788.047386 | 701 | 131 | 0 |
| 18000 | 58910 | 58812 | 457277729 | 7762.310796 | 694 | 132 | 0 |
| 19000 | 59202 | 59095 | 464696095 | 7849.331019 | 710 | 133 | 1 |
| 20000 | 59273 | 59192 | 461264840 | 7782.039715 | 693 | 133 | 5 |
| 21000 | 59017 | 58926 | 457372244 | 7749.838928 | 690 | 130 | 2 |
| 22000 | 59076 | 58995 | 465362094 | 7877.346029 | 709 | 134 | 3 |
| 23000 | 59017 | 58936 | 469996856 | 7963.753766 | 709 | 134 | 10 |
| 24000 | 58889 | 58797 | 466138782 | 7915.549288 | 691 | 134 | 16 |

## Appendix B. The generator

`python3 r39joint.py --gen-c > gen39b.c`, then `python3 -m ziglang cc -target wasm32-freestanding -Oz -nostdlib -fno-builtin -Wl,--no-entry -Wl,--export=gen -Wl,--export=g_nreg -Wl,--export=g_dppol -Wl,-z,stack-size=8192 -Wl,--initial-memory=65536 -Wl,--max-memory=65536 -o gen39b.wasm gen39b.c`: 1,753 WebAssembly instructions. With `R39_WASM=gen39b.wasm` (and the `wasmtime` package) the program charges the executed operators of each generation (wasmtime fuel, one operator = one operation): mean 523.6k, standard deviation 8.0k, maximum 543k over 200 first blocks; it emits records equal, line by line, to those of the Python generator `make_kernels_folded` of section [2] (200 first blocks, both banks). Without the module the program charges the halt cap 575,000.

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

## Appendix D. Full-state equivalence

The external verifier runs the actual source, wrapping kernels, stage 2 and claw calls without changing `Mach.o`. It retains separate hashes for both trajectories, raw claw order, kernel records, stage-2 events and full state. `d_final_all` hashes `(tab,LA,R,sav,qw,cur,idc,it,qn,s2,lim,success,pairs_found,messages)`, including every register-list slot, complete save and raw queue arrays and the complete parked tuple. `d_stage2_all` hashes `(in/out,it,cur,qn,final,R,sav,qw,s2)` at each stage-2 entry and exit, including record arrays, timing wheel and free stack while parked. The new derived reset-cache fields are proved by the interval invariant, not matched to nonexistent baseline fields.

Every common semantic field, statistic and hash agrees across the four small windows, all forced cases and all 24 full windows. Extra cost fields and wall time are the only allowed differences. Generator selection predicates and random draws are unchanged. These hashes are external audit evidence and add no normative source bytes or online work. The following hashes are identical for the pinned leader and the composition:

| Seed | Full final state | Full stage-2/parked stream |
| ---: | --- | --- |
| 1000 | `5494df736b4fd00bec7d895a8dd52924333d39b10f5a20128a02f15ebe062811` | `ce32ef9ed439a8532fb5c01bc15065b92770ecb215a26dbd281cf94ac99db456` |
| 2000 | `86009a23d6b08c1e23346bdafdeec1e30ee2bb8d27e29fdda3096d1315520d31` | `2da47dee382cbfa7503b31f532a933e8ea782bfa7492aa754a28859643177086` |
| 3000 | `88cd62f4c92f1ec2b7ea9f942ca4b449ab70a269d0ea08833c1b74321f1ca0d7` | `7b0fb1185f362316ed5375209b6854a5293cd9cc7bf7ab467d378e7c8e3abec0` |
| 4000 | `0bccfe19e4b3f297d5e20aaba9f1083e8cd136bc31ade8b3605be42cd2fb4660` | `4268e131c83ccdc3101a8d17dfb5e7acf8b5585295d9333223a9eb94e4dd8bee` |
| 5000 | `ead07033db79cc0c35a796c549c1bf5107335907c0aadad63f7fb258e8aeec35` | `8a618dafeb69e060c6308b48436755498a9914a3c347c16ca5ce1a2480b66a0d` |
| 6000 | `09ff244a1a21f436bcc1d82c66f98c706172513fd8d97ce4e38c9bfe205faf3b` | `85de0c500b9f73cdfb4f2f56dfd3890e82b61b53c7bf0a7ff24cc33b4d284677` |
| 7000 | `77b0a0e2029e7ae17ad81b6de01de1cb33ae04e85413e05cc3073872104bac6b` | `998c35b018e73adc1a24379aba0d592cbc9239e058922208a87bf12ef844a20e` |
| 8000 | `c1862c19e22442f56d85c859a10d7af39212ff8df9eaaf25ac78d035d9dc564c` | `e176594fe91d72a9fceeec498cac8b5372e143c1f086125b5378dbb8302b5827` |
| 9000 | `daa5356f93892405418bd4ca4e40b980f159bd50208eb508c0a8e6ce18b6de14` | `ea029230a11c979de1a4f6849a924c00dd1b4c14cdba4737248ffd35497d1285` |
| 10000 | `e0cfedb2ccd92643f05798c6dd6f42f75bfe448d7116efd1e064cd27e7f0b1fe` | `8949fb0e4e43996267bef6269434887686737a0e3d4e08b2801de28d86bfd4a9` |
| 11000 | `e3cadf5911109e7bb57fdc977fd5187796244037d9d9baa5146fd56817dfe53b` | `bc80bb6f1b3bbb1b5d185b5d5db61883d6a1d1a9d651f40b3c61a7bdf32aae04` |
| 12000 | `900d2cd5a42b65b97f102fc232e1c8911b71005322113dad3f8519367d1cfb1e` | `5139eb0b82ae43b7845646b4aaffb66d4fd3bb0a1e81b8efa5af7c679a9a1651` |
| 13000 | `6ac0c5c18f8dab3a2215be9634040d566264d9f1f19016ac26ed82e553f97f5c` | `74dbfa7254853841d1e74b90061b87831464c9baa8d017b2856f03cd68cea0d9` |
| 14000 | `8255a3ffed7dd7d621c1bbf9182a02cee75a08db4c7e23c07e62130648992f3a` | `1311df423fdeb3bd096f695e8b2ffbdd953aa16b66a4d922ca3566292d900067` |
| 15000 | `e4905f9af50711c691af810c7f2caadc8acdc37d3e0ef7f2ad693ef863f81ddb` | `c9ee352e3bc1f9b642eee8e3d3c0b3a68f2b27ff8424e396f5066a68b3ee1200` |
| 16000 | `3701ac314d6279a41d2532ebba820abf7af89fce5a7aaa6f9ca1d05e4ae2ae1a` | `188456354c354251ac2218b966241c640052417c234403085276d1ca161a13f3` |
| 17000 | `276e798f670462fb310631f48cf1f99edd3e2b31d970a4823b16a62a97c02f8f` | `79373367714bb1533c4a1b161f6aad831196953463aaa0e1467fec374b282ba1` |
| 18000 | `7d3465a8ff21acf104137a648a26d71f48575c011f56a7d9b14be35f7fa70780` | `c3f58cd1e4b62ab9df6b3aecedf1e287420cb37ce1f774f08422b44ef7627028` |
| 19000 | `8a3d3cea5f83a5ecc0468596617a1590ff39842f0c085a5d7533961f05e48f53` | `7c4d04d54ab7474f71a6bb5a5bca1a3f696bb02e2e26a39844e44e3970ecf2cb` |
| 20000 | `66a7baf1d5576cbb6e2798d992cc1190c33113839dfe645f0c4b35f3285fc113` | `0ad33cd3cc09b1203c32516f52c725c352eebe3e4bcb823e8acd88f59727d8b7` |
| 21000 | `1bfac8f68552406858abdd498526a2e1805dd9c8e11a394d55d4941c1d07a8b6` | `42b51f389964bfa792899a05769c35a9791d35c23db586b53f924e0d959690b6` |
| 22000 | `6229b12445a696dae81d06c613c92ddcb3418bd320ea34c407a4cd8612e964e4` | `821ffb12cec9021ec87b77a02ad7c4171c746ba56a3ad1be25747db00a9f891d` |
| 23000 | `1fb23b91b92d86fe4cf20c22efad3f0d39d0c17ab43f67b93e2554f86702e908` | `189c08937866d568c717f5f554e3a367c149e3ae292277b2c13d7e02eb4ac447` |
| 24000 | `c21ae3679daf95dc330c9ec048adb035cc65eec4e2dfded051aca7b6477e106e` | `f1a5e7b8ca2221baddfbf65811b563747ed0d441b98c41fe95e78a5a2054eab6` |
