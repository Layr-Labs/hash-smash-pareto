# SHA-256/39 ID21/age10 engine-only derivative

Local conditional endpoint: upward time_log2 **117.823**, memory_log2_bytes **20**, success_probability **0.39**. The exact modeled time is 117.82221527513362095589 bits. This is an exploratory heuristic claim; local mechanical readiness and numeric GO do not establish organizer admission, a native implementation, or human acceptance.

## 1. Target, provenance and output

The target is sha256-r39-prefix-v1: standard IV, FIPS 180-4 padding, feed-forward, the first 39 SHA-256 steps in every compression, and equality of all 256 output bits. The output consists of two distinct ordinary 128-byte messages M0||M1 and M0||M1'. Their second-block chaining values coincide, so their identical third padding block gives identical digests. The random first block M0 is retained and included in both messages; a semi-free-start witness alone is not the claimed output.

This derivative uses the officially declared 0b2616e3-b9f7-4a9a-aefc-5a926f6e2197 as its direct base. It changes the walk's record allocation and window, conservatively bills every online generator attempt at 575000, and replaces B/W with the resulting fixed endpoint. The tail source and QDECL=-75.47 are byte-identical to that base. No new tail endpoint contributes to any probability or score here. All original construction, tail and cost credits remain:

Through 0c307634 the program is mitchuski's 19034ce and lamb356's accepted 4487063 (118.346), built on Jbenisek's d90878ff (the machine program, its exact executed ledger and the whole-megabyte table) and on the construction of sraiw's 38912d66 (the transplant of the published Table 23 pair of ePrint 2026/1120 onto a random first block, the exact bijection, the row-16 claw, the exact side conditions F8 and F9, the dual-parity fibre), itself built on dariolina's row-16 claw idea (21b6653a, 1d3f2c3c, 2c48b18c, cfe5c4e2, 4e396742) and her preregistered tail methodology; the word-RAM cost convention comes from dariolina's 744875ec and Jbenisek's 3c1d7f68, 368d1718, 01e31be9; the 5-byte record convention is dariolina's 6b678689 and Jbenisek's 0c1ef7c3; the v2 tail replica is 0c307634's.

## 2. The construction (sraiw 38912d66, dariolina)

**2.1 The base is advice.** The pair of ePrint 2026/1120, Table 23, is a 39-step semi-free-start collision: a chaining value `CV_PUB` (8 words), two blocks `M'` and `M` (16 words each), 160 bytes, printed in `experiments/r39joint.py` section [1] (`CV_PUB`, `M_PUB`, `MP_PUB`). It is a collision of the 39-step compression from `CV_PUB` (experiment `r39-transplant-claw`, trial 0; the program's `compress39` equals the organizer's `verifier/hash_functions.py` on 300 random blocks, and the published pair collides under the organizer reference). It is the advice of this entry. Its trajectories `BA, BE` (message `M'`) and `CA, CE` (message `M`) are expanded from the 160 bytes by two compressions at the start of the run (charged 2 x 2812 + 120 operations, `Attack.base_setup`).

**2.2 The transplant.** Write `A[r]` and `E[r]` for the two state registers after step `r-1`, `a0 = A[4]`, `a1 = A[5]`, `u = W1`. Fix `A[6..9]`, `E[10..13]` and `W10..W15` to the published values of `M'`. For any chaining value `cv` and any `(a0, a1)`, steps 0 to 9 then determine `W0..W9` uniquely (`build(cv, a0, a1)` in section [1]); the partner message takes `W8 + D8`, `W9 + D9` and the published `W10..W15` of `M` (`second`). Both messages then follow the published trajectories `A[6..19]`, `E[10..19]` (steps 0 to 15 only, an identity of the step function, not a probability). The map `(cv, a0, a1) <-> (W8, W9, W16..W23)` is a bijection (320 bits, triangular). Experiment `r39-transplant-claw`, trials 1 to 255, checks the identity on 255 random chaining values.

**2.3 Row 16 is a claw.** `W16 = sigma1(W14) + W9 + sigma0(W1) + W0`. With `a1 = u + h(a0, cv)` (`recover_a1`) one finds `W16 - g = F(u) - F(a0)` (mod 2^32), where `g = 0xbca1c321` is the published `W16`, `F(x) = F_even(x)` for even `x` (a 32-bit expression in `x`, `S0(x)`, `MAJ`, `S1`, `CH` and six constants of the first block: `consts`, `fstep`) and `F(x) = sigma0(x) - x` for odd `x`. So `W16 = g` exactly when `F(a0) = F(u)` with `a0` even and `u` odd: a claw of the map `F` on 32-bit words (checked in `r39-transplant-claw`, `w16_identity`). Claws are found by a van Oorschot-Wiener walk (Section 3).

**2.4 What remains to pay, after a claw.** (i) `W8 in F8` and `W9 in F9`, where `F8 = { w : sigma0(w + D8) - sigma0(w) = 0x087ff000 }`, `F9 = { w : sigma0(w + D9) - sigma0(w) = 0x03010000 }` (`inF`); both sets depend only on 14 and 17 active bits of `w`, with exactly 1152 / 2^14 = 9/128 and 2080 / 2^17 = 65/4096 members (enumerated; the active-bit masks `0xCC19E60C` and `0xF9983C0F`), so `p8 p9 = 585 / 524288 = 2^-9.807707`. (ii) `W17 = 0x71e9ba98`, the published `W17` (the program tests it on every claw): probability 2^-32 for a uniform `W17`; the entry needs only that this value works (`solve_row_exact` in `r39-transplant-claw` trial 0 verifies `|G16| = 2`, `|G17(0xbca1c121)| = 0`, and `|G17(g)| = 1` with `G17(g) = {0x71e9ba98}`). (iii) The tail: rows 18 to 38 (`W18..W23` are the six free words of the bijection) must end with equal states after step 38: probability `p_tail`, Section 8.

Events (i) to (iii), together with `W16 = g` and the parity `a0` even, `u` odd, imply the collision: the pair then follows the published trail through row 17 and its remaining rows hold with the tail event. The program ends by compressing the pair and comparing (`Attack.claw`, last block).

## 3. Exact shipped algorithm and packing

The actual attack is experiments/r39joint.py --attack. Without --seed each window obtains fresh first-block words using random.SystemRandom; deterministic seeds are a reproducibility mode. A window has 2^27 evaluations, 256 lanes, and 2^19 stage-1 iterations, followed by a complete final drain. Stage 2 retains the base's keep-longer table, short-trail skip LMIN=32, parked execution, D0=82 decoupled catch-up, KRES=6 free-pair reserve, and batched extraction, inserts and XOR-delta restarts. Drops remain outcomes and reduce the measured yield.

The ID21/age10 constants are IDB=21, AGEB=10, CHECKB=8, RECB=39, PAYB=31, BMUL=670, BUCKETS=171520, MAXS=768, CUTP=256, WHEEL=1024, QCAP=3584, QFULL=3328, GCAP=575000, RCAP=206 and KCAP=780. A trail begins at its unique integer ID, 0 through 2^21-1; IDs are never recycled. Once the cap is reached, the current iteration finishes, stage 1 stops and all queued/parked work drains. A trail reaches age 768 before the next scan at most 255 iterations later, so recorded ages are at most 1023 and differences fit ten bits. A zero age is the empty-table sentinel.

A table record has ID bits0..20, age bits21..30, check tag bits31..38; its mask is 2^39-1. Record k starts at bit39*k of 26130 256-bit words, using two words on a crossing. The final used bit is 39*171520-1=6689279, within 26130*256=6689280 bits. The DP value has low7 bits zero; r=x>>7 is 25 bits and bucket=floor(670*r/2^17), tag=r mod256. Every bucket interval contains at most196 consecutive r values (ceil(2^17/670)=196), below256, so the bucket/tag pair recovers exactly r, with no false endpoint match. The shift/add schedule is WDIG=((14,1),(13,1),(10,1),(9,1),(4,1),(1,1)); summing these signed powers computes26130 table words. The bucket multiplier is computed separately as 670=2^9+2^7+2^5-2^1.

The lane scalar packs ID below bit21 and absolute start iteration above it. A pending pair uses two31-bit payloads (ID21/age10) in64 bits; four pairs fit a256-bit queue word. Stage-2 pending state uses IDs at bits0..20 and21..41, length difference bits42..51 and the catch-up selector at bit52 and the nonzero-pending marker at bit53. A callback/lane record uses ID bits0..20, catch-up flag bit21 and a9-bit next-link (0 empty,1..256 lanes) at bits22..30, fitting32 bits; eight fit a256-bit word. Timing-wheel heads are16-bit fields,16 perword;1024 buckets cover every nonnegative delay<=1023 modulo the wheel. The free stack is packed bytes (128 lane-pair indices), four256-bit words. The one-register hit group holds at most10 disjoint25-bit lane windows; shifts stay below256. Restart deltas update21 low planes and clear the remaining11. All associated masks, flag shifts, cap tests, age extraction, queue payload, callback and link shifts were generated together; the source-level scope certificate checks every executable change.

At most256 hits arise in one stage-1 iteration; draining at QFULL and QFULL+256<=QCAP prevents queue overflow. Check mode requires exact scalar fstep agreement on every recorded claw, even/odd orientation, map equality, exact filter and reconstructed message identities, and empty queue/wheel/parked state at final drain. The online attack does not keep an unbounded Python set of distinct claws: that set and edge tracing belong to evidence collection. Success amplification counts independently reconstructed connected groups of the deduplicated full32-bit claw graph per CV namespace, never raw edge count.

## 4. Machine accounting and turnkey generator limitation

collision-frontier-v5 prices the256-bit word RAM: XOR/AND/OR/NOT/move/shift/rotate/add/subtract/compare/set each cost1; a tested branch costs2; a load/store costs3; call and return together cost2. The reference target compression is2812 operations. Kernel records are5-byte register-to-register Boolean operations, charged once per execution; other native instructions reserve36 bytes each. Mach charges table accesses including crossing words, bank/save loops, flag tests, queue/callback/free-stack work, lane movement, setup, claw filtering, pair reconstruction and final verification. Stage-2 and park/resume charges use exclusive census blocks, so nested calls are not double counted.

The submitted GW.ops always returns575000 for each actual online generator attempt. It does not inspect Wasmtime fuel or require an external observer. Relocating the accepted kernel to the second register bank costs8*kernel_len separately. All attempts, including failed/capped attempts and eventual skip after KTRY=8, are charged. A current first block whose kernel exceeds780 records or206 temporaries is skipped and charged. The Python folded generator and the embedded GEN_C agree on emitted records for the archived inputs; Python's exec of a convenience kernel is reference execution, not a cost-free native compiler operation in the word-RAM model.

IMPORTANT LIMITATION (H6-native-implementation): constant billing is self-contained accounting, not a generator meter or a proof/enforcement of a native575000-op halt on every possible CV. The optional Wasmtime adapter's execution cap/fuel is not a literal-op bound, and its absence uses the Python reference. Native generator budget enforcement, the reserved hand-coded routines/register allocation/workspace and faithful direct execution of5-byte records are inherited implementation contracts. Admission requires accepting or independently implementing/certifying these contracts. We do not equate the current Clang18.1.3 artifact with an absent historical Zig build, and do not claim the submitted Python's physical CPU/RSS is the modeled machine.

For evidence, the exact current C has SHA823a1d42fd0a18d64e7c41f47a9b40ef6818a88aba9a0bad149d149846a5eb82; the Clang wasm has SHA292b35abdfda4037c8cac031e1f6e9db15f61f3e77b2c380278a665348901fb6 and1755 static CODE operators, plus12 relocation instructions. A direct CODE VM, Wasmtime49 and an independent Python construction matched all584 observations /146 unique constant-bank cases. Actual literal counts<=429435 and fuel<=398516 in the fixed archive. Fuel and literal counts remain separate quantities. Neither wasm, Wasmtime nor an external VM is a runtime dependency for the shipped constant accounting.

## 5. Fixed evidence and conservative repricing

The selection pilot only selected/sized ID21/age10; none of its outcomes enters this test. The fresh confirmation froze73 paired first blocks, requests, order, eight shards, caps, analysis, code and image before outcomes; a fresh independent auditor first acknowledged the freeze, then independently replayed KAT/design-versus-compact2^22 fixtures, then issued a separate performance ACK before dispatch. All73 pairs completed with no replacements or adaptive stopping. Baseline ID20/age11 used2^26 and candidate ID21/age10 used2^27 on the identical M0/CV. Every failure, cap, CPU limit, kernel skip, ID stop, incomplete drain or UNKNOWN was a failed primary row under the frozen protocol; there were none in this completed archive.

The seed domain was ASCII r39-id21-full-confirmation-20261023-v1|. Seed_i=SHA256(domain || raw_live_sha256 || raw_measured_compact_sha256 || uint64be(i)), i=0..72, interpreted as a big-endian integer for Python random.Random. raw_live_sha256=35c6901d5838fe9cca159cf93f429304bdc205692f20e03391bd28b2231c1b6f and raw_measured_compact_sha256=c6c8cf671de42ec1afcee969e4d920914e7864015b7c773352bb29418e764ae3. Each Attack's RNG generates exactly the archived first-block M0 and standard-IV39-step CV. The seed manifest1132348f2ef8a8dc55b59ceeb549ea4de6c0786d498a16261ffcdf5ed8c116c4 was checked disjoint from all listed development/pilot/410000..410072/old-tail values and the concurrent distinct-domain tail seeds before dispatch. No concurrent tail outcome is used.

The compact measured source had complete AST equality, including GEN_C/docstrings, to design be0405b142f2bbc3e08f2729764d892a79516da27f82582dda0a2dff8fd782e4. The shipped attack preserves that walk/map/filter/kernel/layout AST. Changes are conservative GW.ops accounting, B/W constants and organizer-only known-answer tables/boundary diagnostics. Accounting changes cannot affect a walk on these rows: each had exactly one accepted online generation, zero skips, and literal charge<575000. We recomputed every per-row Mach cost as oldMach+(575000-literal), retained relocation exactly once, and recomputed the sample variance and Student endpoint on all73 repriced costs. The6-operation window driver is separate from per-row Mach.

All146 windows'16,930,485 raw24-byte full32-bit pre-merge edges (406,331,640 bytes) were independently parsed, scalar map/filter/replay checked and rebuilt by connected components with duplicate removal and CV namespace separation. Every source row's CV/M0/seed, block/category ledger and complete drain passed. Full archive SHA89c27ca3e3d62b7d85fa3c69527e030baf9581195053ac1f19d78075bee41cd5 binds2507 files; independent audit seal3140ec9b1190291393612f9a9c7b88e59131e84828c6dd93fa1e8fa084a9c61d binds1059 files. Pre-outcome94-file freeze f6f15c8021ead84decb259b79aee49f232a78d8f19e20eaf5b00fa8964528d5d; exact fixture0897c4f1 (full receipt in the archive); no source/protocol changed after that freeze. The independent fallback integration seal52ef141bc0a72f7692ad35540b9520c71ff9b19dedfd6b0660fd1efdfac06d84 confirms conservative repricing and the core constant-return/B/combined-W semantics. These hashes identify evidence, not external notarization.

Only candidate absolute means determine the endpoint. Let n=73, s^2=sum((x-mean)^2)/72 and SE=sqrt(s^2/73). Fixed t=2.646 is the upward-rounded72-df one-sided99.5% critical value. mu+=ceil(mean_ops+2.646*SE_ops)=1051393213; g-=floor100(mean_groups-2.646*SE_groups)/100=6335919/50=126718.38. Both marginal coverages are99.5%, giving at least99% simultaneous coverage by Bonferroni under the inherited Student/iid heuristic. These are not distribution-free guarantees, and a Student interval does not prove independence or its own coverage. The score conditions on the true means satisfying these bounds. Claws and per-window groups/claw use t=2.380 as diagnostics only, and paired ratios are diagnostics; no ratio of means or product of confidence endpoints supplies the primary yield.

Every arithmetic endpoint uses exact rational mean/variance and an outward square-root: k=isqrt(floor(SE^2*10^48)), SEupper=(k+1)/10^24 for nonzero variance. Integer ceiling gives mu+, and floor to0.01 gives g-. Appendix A lists all73 rows, permitting independent variance/repricing reconstruction. No post-hoc row aggregation, cap deletion or extra sampled window was used.

## 6. Full modeled memory map

The following disjoint native arena totals1048128 bytes, below2^20 by448 bytes. Claim memory_log2_bytes=20; memory normalization adds max(0,log2(M)-20)=0.

|Region|Bytes|Reason|
|---|---:|---|
|256 registers|8192|256-bit words, including all live scalars|
|Two kernel images|7800|2*780*5|
|Other instruction reserve|150408|4178*36|
|DP table|836160|26130*32|
|Lane array|8192|256*32|
|Bank save|1024|32*32|
|Six parked scalars|192|6*32|
|Queue|28704|(3584/4+1)*32|
|Lane records|1024|32*32|
|Timing wheel|2048|1024*2|
|Free-pair stack|128|4*32|
|Counters and fixed buffers|4096|inherited reserved bound|
|Published advice|160|8+16+16 words|

The4178 nonkernel-instruction reserve retains the base4171 plus5 for ID21 layout helpers and2 for the corrected current Clang static census (1755+12 versus historical1753+12). Constant accounting does not claim a code-memory saving. It includes the inherited1100 hand-counted routines and exclusive bookkeeping census; a full executable native image and workspace certificate remain H6, not an emitted artifact proved by this Python script. The generator's <=64KiB scratch and sequential advice-construction scratch reuse the table region before table clearing. No external meter or observation buffer is an online allocation.

Evidence collection used peak worker RSS41040KiB and406331640 raw-edge bytes on disk; those are not secretly placed in this arena. The2^82 preprocessing work reserve covers collection/verification conservatively, but a policy that charges observer physical memory at the online peak would change memory normalization. Accepting separate offline evidence storage, the native register/workspace map and the preprocessing-memory convention remains H7-memory-admission; no organizer exemption is asserted.

## 7. Deterministic halts, amplification and exact score

Every window has the deterministic bound R=2^52 operations, including the6-operation driver. Put N=2^27,L=1024. Stage1 costs at most N*(8192+64)+(N/256)*790. A cut-scan lane, including insert_lane, is bounded by256 operations and scanned only everyCUTP=256 iterations, so its contribution is <=N, already below64*N allocated above. There are at mostN queued pairs; waiting-stage2 iterations are at most ceil(N*L/123), because a wait for fewer than6 free pair slots has at least123 pairs in flight. At most floor(N/3328)+1 calls each require at mostL additional drain iterations. Their scalar entry/exit work is covered by the setup reserve below. Bound every stage2 iteration by2^21 operations, covering256 launches/completions,128 scalar claw filters, fixed blocks and the kernel. Setup, scalar call entry/exit work and at most8 generator attempts are covered by2^30. Their conservative sum is2431053997277184, plus driver6, strictly below4503599627370496. This is a source bound, not an empirical maximum. Each window's distinct-group yield is in[0,N], and failed windows contribute zero.

Inherited H1 treats the first-block windows as iid and their true work/yield means as bounded by mu+ and g-. H5 treats distinct groups as independent success opportunities with per-group lower probability p=(585/524288)*2^-32*2^-75.47; within a shared connected component only one opportunity is used. These are extrapolation premises, not consequences of graph counting. Let lambda=-ln(.60999), G=lambda/p. For outward exact evaluation, let q=floor(2^(18053/100)), verified q^100<=2^18053<(q+1)^100, and p_lower=(585/524288)*2^-32*q/2^256. Use z=39001/160999, lambda_upper=2*sum(z^(2k+1)/(2k+1),k=0..127)+2*z^257/(257*(1-z*z)). Then G_upper=lambda_upper/p_lower>=G.

B=floor(G_upper*(1+2^-19)/g-)+1=785725203045486750480484226083.
W_Mach=floor(B*mu+*(1+2^-20))+1=826106933601285541243277258582331594450.
The source --attack counter adds A.m.o+6 for each completed window, so its actual W_BUDGET is W_Mach+6*B=826106938315636759516197761465236950948. It tests the budget before each window and can overshoot it by at mostR. Thus total work is (W_BUDGET+R)/2812 plus preprocessing, with no second6*B addition. B_WINDOWS and W_BUDGET are the exact shipped integers.

Hoeffding with bounded independent windows gives failure probabilities at most exp(-Ew), exp(-Eg), where Ew=2*B*(mu+/2^20)^2/R^2 and Eg=2*B*(g-/2^20)^2/N^2. Both exact rational exponents exceed32; sum(k=0..100)32^k/k!>10^12 proves exp(-32)<10^-12. B*g-*(1-2^-20)>=G_upper. Conditional on H1/H5/tail/implementation premises, the probability of reaching enough groups within the work budget and finding an ordinary collision is therefore >=.39001-2*10^-12=.390009999998>.39. The99% joint mean-confidence statement is an epistemic heuristic, not an extra algorithmic success factor silently absorbed into this .39 claim.

Preprocessing is exactly2^82+2^36 target-compressions (Section11), and total T=(W_BUDGET+2^52)/2812+2^82+2^36=206526734582308689283806951815281992681/703. log2(T)=117.822215275133620955892645863812670086...; the upward three-decimal claim is117.823. preprocessing_log2=82.000000000001 is an outward metadata bound on log2(2^82+2^36), not a separately rounded amount added again to T.

The frozen live comparator is Tlive=(833493922237739748009991264931696575188+2^51+6*1691119946747626795396529639086)/2812+2^36, log2 approximately117.83505842345855087. Acceptance uses exact integer powers: (Tlive/T)^1000>=2^11 and T_num^1000<=T_den^1000*2^117825. Both pass; exact gain is approximately0.01284314832492991bits. The upward claim117.823<=117.825 and gain>=.011 both pass without tuning the gate. The memory penalty is zero. This is a local engine-only numeric GO under explicitly inherited premises, not a qualified/accepted frontier result.

## 8. The tail p_tail (rows 18 to 38)

Definition (unchanged from 4487063 and 19034ce). Distribution `U`: `E16`, `E17` of the first member pinned to the published values (this fixes `W16 = g`, `W17 = 0x71e9ba98`); `W8` uniform on `F8`, `W9` uniform on `F9`, independent; `E18..E23` of the first member independent and uniform on 2^32 (`W18..W23` are a bijective image of them); everything else is determined by the real step function and message expansion. `Q = P_U(collision and K_P | a0 even, u odd) = 4 P_U(collision and K_P and a0 even and u odd)`, where the collision test is exact (equal 256-bit outputs of the two 39-step compressions) and `K_P` is an importance carrier (the printed cells of Tables 21 and 22 of rows 16 to 18, signed differences only for rows 19 to 22, `E23[30] = 0`). `K_P` is a subset of all routes to a collision, so `Q <= p_tail` and the cost bound uses `p_tail >= 2^q_tail` with `q_tail` = -75.47.

Declared value. `q_tail` = -75.47, fixed before the organizer runs by the pre-registered rule: at least 0.01 below the one-sided 99.9% Student-t lower bound (t = 3.852, 13 df) of the frozen design, rounded down to two decimals. Design (frozen before the runs): the same estimator as 4487063 and 19034ce - trial 0 an SMC over `E18..E23` with 800 particles, exact 1- and 2-step look-ahead and multinomial resampling, trials 1..20 the rows-24..38 Monte Carlo - with the work re-allocated inside the organizer's 16-experiment and 20-second limits: stage lanes per particle 8x512 (row 18), 8x2048 (19), 8x2048 (20), 4x128 (21), 6x256 (22), 1x4 (23) - 19034ce used 1x512, 5x2048, 3x2048, 1x128, 1x256, 1x4 - and 20 trials x 80 batches x 2048 proposals = 3,276,800 proposals per run (2.0 times as many), every particle driving exactly two batches. Three constant-factor changes only: lazy pool candidates (a pool entry is the packed pair (parent index, E); the candidate's row values are recomputed for the row and look-ahead checks, never stored), `CH = g ^ (e & (f ^ g))` and `MAJ = (a & (b | c)) | (b & c)` in the packed hot paths (3 and 4 operations instead of 4 and 5, bitwise identities), and per-width cached packed constants for the trace. The v2 program, run at 19034ce's exact parameters (`CFG 1x512, 5x2048, 3x2048, 1x128, 1x256, 1x4`, `NCH = 10`), reproduces 19034ce's outputs byte-identically - carrier, stage counts, per-trial hits and parity classes, the same RNG draw order and count - on three private seed sets, so the estimator, the filters and the Feynman-Kac product are unchanged and only their variance changed. (The regression variant is the shipped file with two constant edits - `CFG = {18: (512, 1), 19: (2048, 5), 20: (2048, 3), 21: (128, 1), 22: (256, 1), 23: (4, 1)}` and `NCH, NB, LF = 10, 80, 2048` - which the 64-KiB two-program source budget does not allow to ship alongside the shipped configuration; the byte-identity was checked on the carrier, all stage counts, every per-trial hit list and the parity classes.)

Evidence: the replica `experiments/r39tail.py` runs in the organizer sandbox as `r39-tail-01` to `r39-tail-14` (Section 10) and embeds the exact 14-run table `EXP` (packed, one line per run: stage counts `k18..k23`, `log2_carrier`, total verified hits, parity classes) and `verify_smc_stats()` with hard `assert` statements. By Del Moral's Feynman-Kac theorem, the unnormalized product estimator `Q'_r = 2^(l2_r) * (hits_r / 3276800)` is an exactly unbiased estimator of `Q'` on the linear scale (`E[Q'_r] = Q'`, zero log-scale Jensen bias). On every run, `verify_smc_stats()` hard-asserts: (1) direct stage-18 Monte Carlo calibration (`c18 == 206` out of `65,536` uniform draws, matching the 14-run SMC stage-18 rate within `0.0003`); (2) 3,365 verified collisions in 45,875,200 proposals across the 14 runs with parity classes `[834, 855, 817, 859]` (`chi-square = 1.36 < 7.81`); and (3) linear-scale unbiased sample mean `log2(mean(Q')) = -75.2474`, one-sided 99% Student-t lower confidence bound `log2(lcb_lin) = -75.3903 > -75.47`, log-scale 99% bound `-75.3885 > -75.47`, and the linear one-sided 99.9% bound `-75.4601 > -75.47` (t = 3.852, 13 df; sample sd of `log2(Q')` 0.1834). Measured sandbox wall time 12.9 to 13.7 s per run on the sizing host (ten private-seed runs of the frozen configuration in the same pinned image and sandbox flags; limit 20 s).

Sizing and pre-registration. The design and the declaration rule were frozen on private seeds only, before any organizer-seed result of this design was seen: ten private-seed runs of exactly this configuration (executed in the same pinned organizer image and sandbox flags, seeds `sha256("sizeG|r39size-k|j")`-derived, outside the organizer executor seeds) gave mean `-75.4069`, sd `0.1235`, wall `12.9` to `13.7` s. One alternative resampling scheme (systematic resampling) and four other stage configurations were measured on private seeds and rejected (higher variance or a lower mean); none of their outputs is used. The declaration rule "at least 0.01 below the 99.9% bound of the frozen design, rounded down" was fixed at that point; the organizer runs then gave mean `-75.2474`, 99.9% bound `-75.4601`, declared `-75.47`. The organizer mean sits 0.16 bits above the sizing mean (the sizing sd predicts a 2.5-sigma gap; the sizing runs and the organizer runs share no seeds); we note that the rule applied to the sizing data alone would have declared about `-75.51`. This entry's pooled and class-specific bounds (`-75.3903` and `-75.4602`) clear the declared `-75.47`. The smaller 4487063 set and 19034ce's `-75.5062` bound do not clear it on their own and are disclosed only as cross-checks.

Cross-checks, all independent of this entry's runs: 4487063's published 14 organizer runs of the same quantity (`N_P` 500, 614,400 proposals per run) have mean `-75.3927` and, alone, a one-sided 99% bound of `-75.5916` (below the declared value: that smaller set, at 18.75 percent of the proposals per run, does not by itself support `-75.47`; disclosed); an offline C run (64 seeds x 2^28 samples, 1.26M collisions) gives `-75.354`; sraiw's bound is `-75.4278` (38912d66); the last two lie above `-75.47`. 19034ce's own 14 organizer runs have mean `-75.3284`, but their 99% bound `-75.5062` is below `-75.47` and therefore does not support the present declaration by itself.

Parity. The definition of Section 8 writes `Q = P_U(collision and K_P | a0 even, u odd) = 4 P_U(collision and K_P and a0 even and u odd)`; the sampled proposals fall into the four parity classes of `(a0, u)` with exact probability 1/4 each, and the pooled hit count estimates the class-mixed probability, which equals `Q` under exchangeability of the classes. This premise is inherited from 4487063 and 19034ce (their replica pools the classes the same way; their measured classes `[427, 440, 433, 406]` and ours `[834, 855, 817, 859]`, chi-square 1.36 and 1.51, are uniform) and is now declared as part of `H2-tail`. It is also backed unconditionally: the class-specific estimator `Q01 = 4 * hits_(a0 even, u odd) / 3,276,800` per run is exactly unbiased for `Q` with no premise at all, and `verify_smc_stats()` hard-asserts its one-sided 99% Student-t lower bound `-75.4602 > QDECL = -75.47` (mean `-75.2257`, sd 0.2936, 855 class hits). Both estimators clear the declared value at 99%; the pooled one also at 99.9%.

Coverage (finding F-EXP-TAIL-COVERAGE on c30c0d70, which declared -75.53 with a 0.024-bit margin and was judged not_evaluable for that reason alone; 19034ce answered it by re-pricing to -75.60). This entry answers it by pre-registration: the design (configuration, estimator, rule) was frozen on private seeds before the organizer runs, the declared value follows mechanically from the 99.9% bound of that frozen design (margin 0.0099), and the primary 99% margin is 0.0797 bits. Read as a one-sided test of the declared value, the 14 runs give `t = 4.0183` (13 df, `p = 0.00067`); the p-value stays below 0.01 after a Bonferroni correction over every analysis listed here. The 14 runs are public-seed replays without a holdout, as in the accepted 4487063; the runs are deterministic given the seeds (the runner's two-run byte-identity check), so the coverage statement is conditional on the design being frozen before the runs, which the private-seed sizing protocol and this section document. Per-run parity classes are uniform in total (`[834, 855, 817, 859]`, chi-square 1.36) and the estimator does not use parity.

## 9. Explicit scope of the heuristics

H1-claw-model covers iid first-block behavior, the Student mean-bound transfer, W17 uniformity and the distribution of the other free words after a claw. Fixed deterministic SHA seed streams are reproducible coins, not certified ideal randomness;73 samples cannot validate asymptotic2^99.3-window behavior. Student coverage is approximate and model-dependent.

H2-tail remains exactly the base's q_tail=-75.47 hypothesis and public-replay evidence of Section8, including parity and SMC-law assumptions. Its Student confidence and transfer from the carrier distribution to this engine's claw distribution are inherited assumptions. Replaying the same14 public seeds is a regression check, not a fresh tail holdout.

H3-advice-construction retains the2^36 construction estimate and64KiB resident-workspace convention of Section11. Exact checks on the published base and a256-candidate slice do not prove a uniform runtime bound over all2^34 possible candidates. Treating that enumeration estimate as sufficient remains a heuristic.

H5-group-independence assumes different graph groups supply independent lower-probability trials. Reconstruction proves graph identities and removes duplicate overcounting, not cryptographic independence or full32-bit W17 uniformity. H6-native-implementation and H7-memory-admission are the implementation/policy contracts disclosed in Sections4/6. Native qualifications, organizer admission and human acceptance remain open even though the local arithmetic gate passes.

## 10. Organizer experiments and diagnostic refresh

The unchanged experiment IDs r39-transplant-claw and r39-window-small execute the actual shipped bytes through the pinned organizer's networkless, read-only, nonroot Docker sandbox, with256-bit target verification by trusted host code. The first checks the published SFS construction, exact transplant identities, row fibres and the advice slice. It does not output a practical ordinary full-attack collision. The second runs four2^22 fixed-seed check windows,3250 distinct claws/groups, updated exact WIN_EXP counters and235.07/262.32 W17/W18 low-byte chi-square values; the existing lag1 threshold.02 is unchanged. Trial4 checks forced park/resume/cuts and equality to the unparked walk, whole-window near-ID stop and complete drain. A deterministic valid two-lane length32 DP state additionally forces one-ID-remaining partial-group restart, because the previous chance-dependent ID20 fixture seed no longer exercises that branch under ID21. This boundary fixture changes no attack function or primary evidence.

The four known-answer tables and T4 snapshot were refreshed on the exact new layout and conservatively billed source, then independently exercised by the unmodified organizer runner. They are public fixed regression evidence, not new statistical confirmation. The unchanged r39-tail-01..14 execute r39tail.py and retain their original manifest scope/hypotheses and QDECL=-75.47. All participant-derived code, including development fixtures and reproducers, executes only in the pinned networkless image python@sha256:2986c55feb36e6cae00fa1fefb454283e4b33f35e75ff8bdd123b134130be301; the host only runs trusted organizer tooling and static parsers.

## 11. Advice, preprocessing and evidence accounting

Preprocessing (`H3-advice-construction`, the form of sraiw 38912d66 Section 4.2, credited). The program reads from the advice only the dense part of the published characteristic: the state words `a`, `e` of steps 2 to 15 of both blocks, the message words `W10..W15`, the differences `D8`, `D9`, the row-16 value `g` and the row-17 value `0x71e9ba98`; every word after row 17 is a fresh draw of the run, paid online by the 2^-32 of row 17 and by `p_tail` (Sections 2.4, 7 and 8). The cost of producing that dense part is counted and declared as `H3-advice-construction`: (1) The 6 steps 10 to 15 carry 12 state words (384 bits) under 350 bit, carry and message-schedule conditions of the Table 23 characteristic (38912d66 Section 4.2), leaving a space of 2^(384-350) = 2^34 local dense-base candidates on steps 10 to 15; once steps 10 to 15 and `W0..W15` are fixed, steps 9 down to 0 and `CV_PUB` are uniquely determined downward with zero search because each SHA-256 step is invertible (`invert_downward` in `r39joint.py`, verified in `r39-transplant-claw` trials 0 and 1: `downward_inv_ok = 1`). (2) Each candidate is tested for a non-empty row-16 fibre `G16` and row-17 fibre `G17(g)` by exact 32-bit bit-by-bit DFS (`solve_row_exact` in `r39joint.py`, using `ROW_MASKS_16_17` and `CONDS_16_17`). In `r39-transplant-claw` trials 0 and 1, `verify_advice_construction()` executes `solve_row_exact` on the published base (`g16_fibre_size = 2` with `G16 = 0xbca1c321`, `g17_fibre_size = 1` with `W17 = 0x71e9ba98`, `fibre_dfs_ops = 1944 < 2812` word operations = `< 1` target-compression) and enumerates a 256-candidate local slice of the step-15 free bits (`advice_slice_cands = 256`, `advice_slice_hits = 1`, `ops_per_cand = 408 < 4 * 2812` word operations = `< 2^2` target-compressions). Over all 2^34 candidates this is at most `2^34 x 2^2 = 2^36` target-compressions (the inherited advice-only reserve is 2^36; this entry also pays 2^82 for evidence). The paper's own figures agree: its Step 1 (a SAT search producing `W8..W13` and the states of steps 0 to 13) costs about 2^34.2 SHA-256 calls, and its Step 2 "holds with probability 1 since there are no conditions on (W5, W6, W7, E1, E2, E3)" (ePrint 2026/1120 Sect. 4.3). Memory of the enumeration: the DFS holds one candidate path at a time (fixed characteristic `< 2^12` bytes, one partial assignment `< 2^12` bytes, round state `< 2^10` bytes), at most `2^16` bytes, inside the `2^20`-byte arena of Section 6, so `memory_log2_bytes` stays 20.

In addition to that inherited2^36 advice reserve, this entry pays a conservative2^82 target-compressions for research/evidence generation, independent scalar/graph/generator verification, exact analysis and reproduction. Observed campaign worker CPU18939933700272ns, whole-archive verifier CPU248052938927ns and112309152808 Mach+driver operations are descriptive, not the full native construction theorem. The reserve is deliberately much larger than these recorded runs; it does not establish that the native-memory and evidence-storage policies are admissible. No pilot or failed tail outcome is promoted to primary evidence. Source-size and scalar correctness checks are exact; statistical/native/advice-policy premises remain declared rather than hidden as checks.

## 12. Attribution and prior findings

Direct dependency is0b2616e3; its nine official inherited dependency UUIDs are preserved in the external declaration, together with all prose credits in Section1. Historical0c307634 is retained as a prefix in the inherited narrative; no UUID has been invented for it. Exact meaning of the target, ordinary output, distinct-group amplification, source size, queue/ID stop, driver-budget inclusion and evidence/native-memory separation are stated above. Earlier exact-cost/coverage claims are not silently inherited as theorems: native enforcement and statistical transfer remain H1/H2/H3/H5/H6/H7. No network submission, commit, push or public post is part of this review package.

## Appendix A. All73 fixed candidate rows

One online generator attempt per row, no skips; delta=575000-literal, Mach_new=Mach_old+delta, relocation remains charged once, and driver6 is additional. Graph groups are reconstructed after duplicate removal. Full seeds and raw edge hashes identify every retained row; CV and M0 follow from the frozen seed rule and RNG described in Section5. The table alone reproduces the primary mean/variance/Student endpoints; raw witness replay uses the separately sealed full archive.

|i|seed hex|literal|relocation|old Mach|new Mach|claws|groups|raw edge SHA256|
|---:|---|---:|---:|---:|---:|---:|---:|---|
|0|ef1c71a0755f86b1d75a55b8b0f6c9f1fc450ab827cfb23a31d37bc8e9599ec6|393288|5848|1050335715|1050517427|126281|125989|0f5d122921d6df1b693853690a78b542653c849e65b655496b72406a9f68a0cd|
|1|92511c7211461f27476a6db61780fa1d1023b3a654fcd46a78431fadadf24542|383890|5704|1036497031|1036688141|126896|126568|b1575e775bc312c87b637311f8c9e23c3b8592b6125c1a4c973848f0f78ee62b|
|2|77b461ec3e53e0d4556191cba7df0b0e4be864aa27457e3a0411d61dfad59b1c|380780|5632|1028390907|1028585127|126623|126316|90afe90d60674cd96d3c296f37b4319d3f87c01407b134755ee15b8fdc41bbee|
|3|dae8a177c3f360b8ddd595f6d4068128803460c1d8af4a08cd8b1dc783f7d3ff|366942|5496|1014433612|1014641670|126341|126049|4ec74833887de4fe533358bbb711740c3bd95f7c3ee9272e9262e346e527f434|
|4|a676322b120ca4151cdde7bb47793c2ce8c63ef3ce27834aed8ace8c5ad747af|385491|5712|1040656950|1040846459|127611|127290|c807cdd05e3604903532307792adba1406df3f2c6c9f4ed822a65cd6d9fe80c2|
|5|9a2d0dff93e2fcdb732a356046f462e8103d866c7df002e8c31a25f73294bc66|394480|5904|1058549663|1058730183|126986|126675|d089647169cdf8bafd9798688a7990b4e0c09a78c5243c8a57be06886d98096b|
|6|8e3dfe836ebaaf27a2ac2f45dab7da8b4ee45031126924bf20e8c6468b05410d|388811|5752|1043718313|1043904502|127775|127464|e255d5e587579815c7b0bb774e41daa2ae56ca6bb46f42e67c784d7358e56a15|
|7|4bfbe648582c3e6f41b5a541353c4eef8300bf705f088201fb416df03105d102|412337|6024|1072488624|1072651287|127449|127121|c549fc4d732eb657acc4c511af012992571e7a497db6eed5d3eb989f8c1387c3|
|8|161778ec0fb6941b854c526ea4d9e6972132b01c448c2ed31d385e4f80376a73|391460|5752|1044137785|1044321325|126853|126527|08606100ba000db65345c6db54973ea42c928edd57008de34b15179e64edbc4e|
|9|941bdccf8c26eff176f34d59153874ded53c0854f7a37e40556cf29e99438b5f|404984|5904|1059733660|1059903676|128044|127731|97c09401b0f0307bef6ed1f210d0ce0c870a27ddcf536408451da9ed78e08a91|
|10|7af6d56fea35abe3fa3bbbf1f02497ec0902b3de483da491122d8eba8b83fdf0|412320|5984|1066814925|1066977605|126975|126704|f573cd88673550bb69df36df4d0ea97c203faa1c4469f0350576c68ee98f6b7a|
|11|70b4d71f2fd7ff77dc1e87164081e72f9c8270e8fcafd3379eb12b20a08aedce|383337|5704|1037235409|1037427072|127687|127355|b55ded905fe96440310afef81a545afd8eacbde0f4044b722f23d737396a67f2|
|12|018f806e3bf7dd43228d3e60b10b35c8e922c707d105a6c97e70e52ef99683dc|386397|5768|1046160571|1046349174|127324|127038|0054ac56b5253c954b183c1dcc3d3bc0567c76db893e50125eb764cf66ff79ef|
|13|b6d9efe4f7add572667b989f6ca68d07b3f36fb134a6ac60d476ff8a9de2d62f|389469|5800|1047154774|1047340305|126304|126016|2fcad0d633382bde1f3ae121e1b3b54bb4bdf10691c16bfb6d7b1a4c283dec6c|
|14|91b0c2a8c6d0748a965ba8a2e1441fb2841d79e4d43f02a68030fe55144069bb|406048|6008|1068698508|1068867460|127149|126853|f5e7930ca93fb2764f0a2b7ad653e2bf4924c5185e2f9c8b894b15bff13c071c|
|15|94a57357b55e79b41368b1aa65c342bfa1f19d420cdfcd5f3dd86daca10423e5|407126|5928|1061467015|1061634889|127041|126734|8481054f284e11eae0b8ebca5900f9f04fd3da06a89a5533138e08acb26ccd72|
|16|c99bad9be9dd91463901635d5262f0bb8a03fe787c3ab32dedd021bb736b7b2b|377325|5568|1023043091|1023240766|127560|127246|0fb42acaef9a7a97f017585aff6288090ca2d45fb0ba73e849d2eaf20b05b580|
|17|503f6eb69923d4836381fd6d0c5d04990ac5b408b5a7ec14f5e3fb05a9e5bb68|406182|5904|1061188312|1061357130|126999|126680|3735545f5668b11f892f68c15e5de392906bafc08782fcaa2da03f391eacb1b4|
|18|a9aa01dfe1576198c4cdb68dfaebcc7e7585bf2adc0bd151f13697244eb53c35|356846|5408|1005798360|1006016514|126973|126632|8575c66a696ed88e5d29a3ea02c5e66d5749f79960dfba0d244d764b772901ef|
|19|8fd9c857710541344bc00d20e7924248b090c3c0e1c7a3924bf894dce183b28f|410786|6008|1072731947|1072896161|127919|127640|4cba950e81bf487c078dabcb80b7847bc50da8dfcdce317b72616ad4b8a9343d|
|20|4b77f098170405d3212bd55fe61002563aec4a1c3625c7402e4c0d63963429f0|388234|5808|1050379351|1050566117|126981|126662|db3353a144d7817637006a122fe402cb20a4844bc8d518cfeaa4ab332e6d306f|
|21|8966cf0f88c010594397c1648db4b9a5d440ada4d537b8ea467127128fc442c6|392476|5840|1053338599|1053521123|127392|127097|8c5935af44dac4e06abea32109e317aa5ac76602c96757f7ade2b0a650c5fedf|
|22|c74c6f7b2267a5607c8a895ae646f90e7d00d952cb5685c4a619c8452564febb|394776|5872|1054762931|1054943155|127436|127127|391bd801cb4cc606fdefbe7080ac8709dbcffa88031ca882654acd517ca284e2|
|23|2994dcae23c60f4e6835a0cb78f301e1724821250f12f834fbb334c0a9ea81ec|396270|5792|1046920142|1047098872|127231|126937|68e674ddaf3c788b3c22b36b8c13bf4843526a61c7230ba3805e3af41cebe620|
|24|2a42622e3e0b638bef26309d4a0e6c02d014f0ed9c2bf6988eca9f29d18428bd|370802|5560|1021262753|1021466951|126934|126610|b365f92090dfb8044770b783f21ec235a0a7282de4bc70499e51112f3534e8b4|
|25|bdf7ae04b6c2955968818e1efb4984aa0a572f6ee64b0a6e665ebb24e8005d60|376062|5584|1026361581|1026560519|127559|127260|32cb97aa9ecfadc64afe7a5344d2901bae41042a4ec0113f07724064db84fd0a|
|26|a13011666814fa056f8c7d4c7c8208cf313a2232f6ac04653c6724a15b60890c|382849|5696|1037399853|1037592004|126913|126595|13ec06e0d68282e2ac6bad16063cdb009662ce8a1cb00e9c649d4940dec7177d|
|27|bfb84843e37417e8efe4dc9247d58c64a79c508011d92a0887c851ea192282ec|389812|5712|1037086015|1037271203|126885|126582|eee7bf8c3ab9edfe2034348a3b4d630e648da67e994ac52b1aea66de1d285174|
|28|4caf8f1cf6d57f2ffc74979235674596e115a4d5ec7820d1bed0612bb733eef3|367283|5432|1008586126|1008793843|126609|126311|07de82a56e6c0407a4a529d7e69135ac9c5a34dbcf05150fa4cbbc72c614a94a|
|29|999fa27838742c579e0012fcc6390c652f93c73ad5a48afc031c0fd38ec0233d|395391|5816|1050136862|1050316471|126931|126611|be9b6e4795a881b3cd380c6be6b2cb422daf9d2eeb0ed6a9ed60d1a8973aa958|
|30|48b1fa4624ec2c297c90f3328c6916257c826fca260fbd0333e914a38b7ff732|396693|5776|1045644314|1045822621|127869|127529|2d82505c8632036e85f0e664189ba69847a9b9ea5bc7956101b77d2ed812a5f1|
|31|60ba8b01b62d6387359d74cd059ed3f2072ca0b259d82aef3e2ef628514e8912|393774|5856|1053998430|1054179656|127037|126721|b3edb4e4e68907da15383448772d0fd80c12ee12ec2450920b7c8caead9a4fef|
|32|07c0bfcc6c4f9a91f4699c4590d3d2bd622d9b7d3f2b7eba717c592ac3c41039|385146|5752|1043476507|1043666361|127321|127034|1e9088654d7d9339a93c53b3433ef4c4ab0bd60ace651f1dde0cb307626461d7|
|33|1a55d0c996d4780b79cd13c2333aab74a9d6bb72711af8dcc27c2a9eabd4d37e|378478|5600|1027120084|1027316606|127333|127047|1a5a41bf03eef453698c87052418ceb1a8188a9d74d0b5eb51a01052d43e67e8|
|34|4b94b789402d8c66d4d2616c4a4130f101afb002ececffd21c2cf321f6cd02e2|391741|5840|1052487893|1052671152|127148|126844|30193660016a0e28176ef732ad0f65ef4bf14ca37048a5dbcbded47d65412146|
|35|5c46d44d5e46a9f748e8a7a83f65792cd8982f1d8cd4f0a3b1c7d68354ccbaf2|390434|5816|1047648596|1047833162|126979|126691|165f0532b20083b5b8ce5d65b50bb586989f69b7443dd01cf759545b116c3f24|
|36|acfda8f5855abee1b4ef07177d93a3ea334cf12ac138b582adeb883005141537|370923|5600|1024820900|1025024977|127213|126897|092141b7ae5b436a43e0031d432ba66fd8514a460307c2c1a0088671606c6987|
|37|92c2178c574c2f7ffbf3e3ce18c57469a72794e0d00f85ec2a0b215abbe8b5d0|395159|5784|1044421548|1044601389|127209|126880|c881b44edc0cbd42040d2259f333918c213c8a105d7f1494869ced979151510e|
|38|8e7f96b99d5e16089377d66d7bde461cdea04afdf0b7d71a09b6054550d68fc9|383905|5664|1034994336|1035185431|127408|127097|aae253bae7f9be3d802463ba496f9e8cc38af613025beb0f936b7427d9e32268|
|39|3dd9d035fa54b515649dcb39097662bc41f3e73cad5ead45b339fdf504349062|374406|5576|1023414431|1023615025|126950|126629|e6e9e84abb057cf50bed601dfac72a852187d4285f675ff4156ebbb7e5229aea|
|40|b5dba577fb7778064837df64c4110efef1ffc91c9ee6fc54db95407052f2f05f|407121|5912|1058211150|1058379029|126991|126654|24399b3bae3a364dac6969f995085fcc889b532f238b0e41e19b3cee29c9267b|
|41|e7dd5847fa987985a42ae233544a633531fe64fc8f0326503de52296570c6a41|387789|5680|1034394260|1034581471|127117|126791|33d72ae866284ce67995fb7b8a12933591bf693b0f14fc0d4a2e42fa917c23cf|
|42|6ef2c2c3d534c9f6d1d3c1ef143492a50818b8a50533c9be24884bd2a249e0e7|408911|6000|1067305477|1067471566|126863|126561|8291a34595286cdb3faa0f0d7ee941b64cac5ee5d3678309ab2dba2d677e4449|
|43|058b13feb04753e0d89c5aad79b0643b8dadcc62f44d0d28ad0654ab0b6fd3f4|386796|5784|1046038125|1046226329|127440|127098|98b791badba3fcb79b3d18a477ee7a07be22b0a8679105bfa31cd7a07bd9209c|
|44|d93a8027c660b2bc2081365756cd8aa799c5f9686d3a74e23afbf05ed4164356|381928|5544|1019568156|1019761228|126663|126351|4985dadc4652c91e870f49920f90fc211ecd52bead2b541d95af59950d2f1467|
|45|b657f276997b74f7ea86a65bb7ab3224b1c54a2219fe56460f37a324a42d153b|398367|5792|1045846890|1046023523|126963|126665|6a44b489deccc9cef51c4dbe5d95a29bf625be59387349e4f66f3bdbba19bd06|
|46|c4f178037923ae70e8bba1ae0fa9848ad1f7a23875509f88497cd55fcae8e911|399104|5880|1056083752|1056259648|127184|126877|5f0500f667b5eaeb2ebd2167803a4cb0b27f1ca8c115b9a7a380325027696b0d|
|47|ce7db65a947e49631368e78d1f9a74b4026d6cfbfc6b9cd19c78742dc7a35517|386149|5688|1036974913|1037163764|127339|127041|a9c74a35a2d260c751bad8ce0cd0a167a7ffc365dc92e124b87b6ff64ca6e66d|
|48|a1e7d2f63203fcf9ebbc6a11cfa87724f68f388e0e412e274ffcd62436ead0fb|404465|5912|1058630745|1058801280|127444|127158|a8fa2c72da8b06733b13a1f5c796243345b868a8c423aba18dbe54207d4680e2|
|49|99245cc23a7a1291f60f08061cf6dd042c0bdf3d8957e74e2301c686a69b06b3|376931|5584|1025376358|1025574427|126606|126281|ad94d637b10982b277ef65342a1bcfd825c5948de1f89b1fbf45b071d0a354e0|
|50|1aeb9da836214a4b07cb225ebf32407579300613f252b4cc6f11d67f327dccb7|390252|5784|1045478285|1045663033|127412|127109|8956bd068c1cca647c8fada26187cbd429a1f0bb355df7308da40ddc15f51711|
|51|77116b3651a9fe58f418898b12fa91282e75884d716f7d3db0dffcc3c843264b|377426|5672|1035612294|1035809868|127020|126730|f06de8f8625f8a22127759b10b2611a14e3ef31f659f63ee3e61b4ce9f4c56da|
|52|cc047c22cb8b94f03a6232b9c2f39a0be7c65858268f27bb18b6db6f0e9cc834|401193|5880|1054656443|1054830250|126905|126593|5e58983063e4c9d05c724bfeafffe511b2e9ea058c963711cdb2c22deb07dca5|
|53|834f28954c84e4aef785f39d38f1cf23425846d14e419433f9af9839f74626ec|400670|5848|1053663115|1053837445|127115|126768|0b487512c7520555f4d9b870e14a457e24e62b8f0a970f29a23fa81f10164171|
|54|e245688d6ce128202a730f4e118f8027185c54f3b39bc8fd92eeb0df0b74e412|389205|5768|1044347921|1044533716|127622|127327|bfaa3fbc8f185569853a8fbbca37abd853e2f8714fc438f5036c6f453db630fc|
|55|71a12556d2d012e6d971ecd0297ee171e48c89ad611eae4fb5b068ccb4809c61|390882|5768|1044552145|1044736263|126925|126616|b021e067469702840d1fdc6e73a3fec3ca3f388a1c270dd4ac0e31257d0ffff1|
|56|91c5a06964f7961b25559b6df91724582eb427a30d39ceedf10e8548eb77e901|372976|5632|1029963474|1030165498|127458|127123|57411aaf618a00b1fb9e084cf35db6efd44eb7cacda51a6207d5b1a98ec22b5d|
|57|33571bf327b83c5246615151ee82ec8c7b881d289eff5c790d3d18b828a779d6|394470|5800|1048864991|1049045521|127474|127148|745cd94d7514ca25ba9026162478fedd46c6503b7f98fb7fc4a031de267ff88c|
|58|e74407ef9f5947e8e112b8e913d859056f013883715cedc07f20352c7c95a562|377796|5608|1027760035|1027957239|127738|127454|1413fbdf1402d48739140ee72d72c408325d086a90f64ee3dcbf844d4c0a3059|
|59|477418fcabab0fae82c9ad0917125bf8313a25fde75b46160fed337e1770d3bb|391805|5808|1049139475|1049322670|126957|126651|21a2c2695e4f45e4cc1788100fea8c1c3dc71512d6f0ef606768bfd8060084a2|
|60|07fb90f250a2b6a6501ea04567a0f1b3960fc3586b8b34bb0573b351350626d9|393378|5744|1042586289|1042767911|127364|127055|e23c853ddd0cfc337dbb6e3ef92511ba8327ef449e5ee7e2295d55c7f8d97c15|
|61|953023f867feb4e064b6ace68c0dc0618e9028370933b3d01182f7ec72f131d4|401810|5864|1054573084|1054746274|127334|127005|ce68421d4adb10206b1500a32e5964771e44ac2ea14f5ea15ee2df783fec1291|
|62|37444cc8725b5baa226a3a159ac29a133a671ea9ef25d6af085653355a542ad8|403720|5872|1055900715|1056071995|126646|126310|4f27fc0ddf6497236b921fcda6b87e1e46548caa1c18d9117333e0a16dc5cd8a|
|63|7c6898b8b30ee992977821c5835def551fb9f385c2101f97ec7892635c903f13|400316|5824|1050505516|1050680200|127001|126706|ea233f33939503a285cd0b79d817671340928510587c165e71f7d0ed5a7a797a|
|64|615f1f9fa02cdfca10f27b337eb98cae6f81c2f784fc995d8a869c46d6270b48|394260|5968|1063290303|1063471043|126507|126215|9c1678e557c61565ab88cfaf72707444f9cfb5635112aec7e87fe20d995225ab|
|65|db2532f2fa341f7b98db5cb4000c7ce54e4ba339317b391e4c9194caf52fa061|383358|5672|1034590336|1034781978|127085|126784|112bc8e495020f910b4162ce9206866835bf4eec7a1a5485632e0ee7641f3e75|
|66|bcf879c1ef916c2c3fdc80df718978e2897dd235931452d0d63bafae3d47b02b|399732|5864|1053216894|1053392162|126690|126375|e69f161ae7d7bd923c6ddbe86fdbc1a878e89e8e94aaa654e218b5c8bfc04750|
|67|abf8ffc4955ecdb2331d77136254f16f1a162cf1edf4ac9a79c23adc82a25d74|406282|5984|1068693476|1068862194|127752|127454|261e9bf6cda83579cde3858de8bcd65c67455d351a1db959f7c7d6ae59b83083|
|68|a3a54c2dff406a13871a938eebafdf94361b0ce42143f4d80f81afac8b86a703|429435|6232|1095043896|1095189461|127134|126812|ee35f40daeb7362fb0af3edbb8a80d40d290903fc8ad7c24d563a3ae3c41dac4|
|69|c5d6c4ef3e9ecdbb2873ad0cfa511c79719422d41a1ecb39c8ea8121a129da86|412801|6080|1077273940|1077436139|127060|126758|ba47c09ef3ffba5c767b0064d59bc9a6b3e8d7a98ee881a5b9f218ae7759362e|
|70|49f843269c4443c1661c6ff23e11ffe3df48ab3cd0e62cc7e6c5b7309aebe940|397631|5792|1046716804|1046894173|127246|126966|2f7d766e4b051fb40aa1c19d157f08814905d9b7b47bec5549cc96b6b0483e15|
|71|36cfbe3658e1d74649fdc9ac8e4fad6791c957c30c02a87f8d701b9daa899d0f|408636|5952|1063929830|1064096194|127633|127327|12a8aafd5b77499948c5c0faf21c6affdb23edebd7e1aa380c029f0e333e77a6|
|72|fb9136265e2d07b91ce522e0d9a8b0a6286edf31ca09913954c9108f5f1eca88|398997|5888|1057038421|1057214424|126837|126495|5533f0c35c9b3eaddf31c64fe63adc0b9f4a25abf35e66bdacbc95636a5a7b00|

Exact statistics certificates:

```json
{
  "diagnostic_claws": {
    "critical_exact": "119/50",
    "lower_outward_exact": {
      "denominator": "50",
      "numerator": "6351997"
    },
    "mean_exact": {
      "denominator": "73",
      "numerator": "9281653"
    },
    "n": 73,
    "sample_variance_exact": {
      "denominator": "2628",
      "numerator": "380470111"
    },
    "standard_error_upper_exact": {
      "denominator": "200000000000000000000000",
      "numerator": "8906686326611955330852117"
    },
    "upper_outward_exact": {
      "denominator": "730000000000000000000000000",
      "numerator": "92893902384119278055959112340379"
    }
  },
  "diagnostic_groups_per_claw": {
    "critical_exact": "119/50",
    "lower_outward_exact": {
      "denominator": "500000",
      "numerator": "498763"
    },
    "mean_exact": {
      "denominator": "12488999364977744686093366242770601438487744855391821795091790832141587292344922344246695875982792336359039041523010682420747062512040491945163171403798463513494733820728889999160208356035214969082658779152981302147924282179178752270099429660807586314390572324674685600",
      "numerator": "12458581506668910903312963761820481107614532872497704230872601579595086970198837688909402583728782565541914711195324822566571500169171529470259071373025099662975357468056577573010304702968106604381264673473917088243467589867244744038885142410578620353480494327866850213"
    },
    "n": 73,
    "sample_variance_exact": {
      "denominator": "6409935827606075754349514218041617967854468278515010867469113514050664586410841715593446540323952702001187007619777634945980039859846528896633322077293190687886268784608323610466199289930347443583703954653380356060403140768572829394666380456376499999064513543448097339671614317087306361340058234023776139530019943988795805393243488278487932690027289300782845336493612811082333590880840956405328346157185789950499013784093408593838918070462045973736097440796855839466174332886011071928436027691473953034981640812090883094980936664960000",
      "numerator": "121606046771286784486387784076559615687976480760905177339113423814575507169784084987539372646984512249868559303845834215868209941953596133660464272886269267700851001555949267860825176959754181824223975370976419282064687556938897187872833921683670348767042486081037509372303688512517100772610157188250391037504007724204264247402880304040990142242332581458355912836497585236145140781583094044037566634840289020306384037648759475229778619075073908399795283203220349613748486387231777695462529783500354590730955695453400423917978889"
    },
    "standard_error_upper_exact": {
      "denominator": "1000000000000000000000000",
      "numerator": "16120901126105406717"
    },
    "upper_outward_exact": {
      "denominator": "780562460311109042880835390173162589905484053461988862193236927008849205771557646515418492248924521022439940095188167651296691407002530746572698212737403969593420863795555624947513022252200935567666173697061331384245267636198672016881214353800474144649410770292167850000000000000000000000000",
      "numerator": "778691292587991042872822613356200952621871160358860426617707020753405701135191086829111227845402804930650274583749174811579157287596288557060402806289696658184912330793428219549134076231823144185865366213446440464714809147136417823186762492867394115063827226990325053896742638111592437847311"
    }
  },
  "primary_groups": {
    "critical_exact": "1323/500",
    "lower_outward_exact": {
      "denominator": "50",
      "numerator": "6335919"
    },
    "mean_exact": {
      "denominator": "73",
      "numerator": "9259047"
    },
    "n": 73,
    "sample_variance_exact": {
      "denominator": "2628",
      "numerator": "380697995"
    },
    "standard_error_upper_exact": {
      "denominator": "500000000000000000000000",
      "numerator": "22273383184794698618373647"
    },
    "upper_outward_exact": {
      "denominator": "18250000000000000000000000000",
      "numerator": "2316912891074604287197863908453613"
    }
  },
  "primary_ops": {
    "critical_exact": "1323/500",
    "lower_outward_exact": {
      "denominator": "18250000000000000000000000000",
      "numerator": "19003419582988422125273128435635517681"
    },
    "mean_exact": {
      "denominator": "73",
      "numerator": "76382691427"
    },
    "n": 73,
    "sample_variance_exact": {
      "denominator": "1314",
      "numerator": "350087320395457973"
    },
    "standard_error_upper_exact": {
      "denominator": "500000000000000000000000",
      "numerator": "955210488424790841972598229061"
    },
    "upper_outward_exact": {
      "denominator": "1",
      "numerator": "1051393213"
    }
  }
}
```

## Appendix B. Bound source identities

Shipped joint SHA256 393bdac905f1e36d0c29edc48bd3f26bcdd449ae993913f3d51a025b22d8b77c (51126 bytes); unchanged tail SHA256 9691abebb3077522b270fab54693e33049a108e8c0a9a888563b4fc461e02b77 (13251 bytes). Combined 64377 bytes<=65536. GEN_C is included verbatim in the joint source; --gen-c emits it.
