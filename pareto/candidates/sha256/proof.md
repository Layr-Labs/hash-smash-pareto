# 39-Round SHA-256 Ordinary Collision via `k = 8` Transplant (`Tuple 124`) and 4-Family Shared-Prefix Tree

**Track:** `sha256-r39-prefix-v1` (39-round SHA-256, ordinary full-256-bit collision, classical model, exploratory lane).
**Claimed resources:** `time_log2 = 90.805662` target compressions (`C(39) = 2,812` word ops/compression), `memory_log2_bytes = 20.0` (itemized peak walk-phase `K4_MEM = 1,042,561 B <= 2^20`, headroom `6,015 B` on top of `32,768 B` reserve; peak setup-phase `584,292 B`), `preprocessing_log2 = 43`, `nonuniform_advice_log2_bytes = 7.78135971352466` (`220 B`), `success_probability >= 0.39`.
**Normalized score:** `time_log2 + max(0, memory_log2_bytes - 20) = 90.805662` (organizer nominal reference `sha256-r39-nominal-v2` is `128`; direct credited derivative of steph4n-gh submission `8f7d2a0b-1174-4de7-a6f8-fe3f4c86635c`, which claimed `91.290391`).

Evidence labels used throughout:
- **PROVED / EXHAUSTIVE:** exact algebraic derivation or exhaustive enumeration over the full stated finite domain.
- **MEASURED (PARTICIPANT):** full-scale or large-sample measurement run with standalone C/Python verification tools on the exact shipped algorithm and `Mach` operation model, applying **6-way Bonferroni simultaneous family-wise adjustment (`alpha_i = 0.01 / 6 = 0.001667`, `99.833%` one-sided per parameter, `>= 99%` joint FWER)** across all six measured ledger inputs. This derivative prices the class-01 `p_tail = 2^-74.446970` Bonferroni-6 lower bound of the preregistered 30,720-seed extended tail panel (Section 5.3a). Because participant panels lack cryptographic pre-commitment (`holdout_nonce` is `null`), absence of selection bias is explicitly disclosed as a heuristic limitation alongside purely algebraic tuple selection, contiguous seed blocks, exact theoretical density cross-checks, and paired `PUB` controls.
- **ORGANIZER-EXECUTABLE:** declared in `experiments/manifest.json` (`experiments/r39joint_k8_both_c.py`, plain stdlib-only UTF-8 Python, `65,147 B` after LF normalization, zero compressed/obfuscated blobs) for deterministic isolated Docker execution by the organizer runner as bounded executable-consistency KATs (not substituted for the full-scale statistical panels).

---

## 1. Exact Target, Message Construction, and Summary of Breakthroughs

### 1.1 Exact target contract
The target `sha256-r39-prefix-v1` is standard SHA-256 (FIPS 180-4) restricted to the first `r = 39` rounds in every compression call:
- Standard fixed initial value `IV = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]`.
- Standard SHA-256 message schedule `W[t] = W[t-16] + s0(W[t-15]) + W[t-7] + s1(W[t-2]) mod 2^32` for `16 <= t < 39`, round constants `K[0..38]`, round functions `S0, S1, CH, MAJ`, and Davies-Meyer feed-forward `CV_out[i] = (CV_in[i] + state[i]) mod 2^32`.
- Standard FIPS 180-4 big-endian bit-length padding (`0x80`, zero bytes, 64-bit bit length) applied to every message, with all 256 output bits required to agree.
- Cost normalization for `r = 39`: `1` target compression equals `C(39) = 2,812` word operations (as fixed by the track profile).

### 1.2 Full ordinary-collision output (`M0 || M1` vs `M0 || M1'`)
Every window draws a fresh random 512-bit first message block `M0` (64 bytes) and computes `cv = Compress_39(IV, M0)` (`2,812` word ops charged per draw, including screened-out draws). Whenever the second-block search finds a 16-word block `M1` such that `Compress_39(cv, M1) == Compress_39(cv, M1')` with `M1' = (M1 + K4_DL) mod 2^32` (nonzero modular differences `K4_DL[8..12]`), the algorithm outputs the two distinct 128-byte (1,024-bit) messages:
- `Msg_A = M0 || M1`, `Msg_B = M0 || M1'`.
Because `Msg_A` and `Msg_B` have identical byte length (128 bytes `< 2^64` bits), FIPS 180-4 appends the identical 64-byte padding block `P_pad = 0x80 || 0x00^55 || 0x0000000000000400` to both. Since `Compress_39(IV, M0) = cv` and `Compress_39(cv, M1) == Compress_39(cv, M1')`, feeding `P_pad` into the final compression yields identical 256-bit hashes `SHA256_39(Msg_A) == SHA256_39(Msg_B)` with `Msg_A != Msg_B`. Thus every second-block collision directly produces a valid fixed-IV, padded, full-256-bit ordinary collision.

### 1.3 Two synergistic breakthroughs over prior 39-round art
Prior 39-round Pareto entries (`d3a46ae6` at `94.0866` through `820db8f6` at `93.557064`) all used a `k = 4` transplant that froze all eight state words `(A[8..11], E[12..15])` and message words `W[12..15]` to the published semi-free-start (SFS) collision (`CV_PUB, _mpx, M_PUB`), reaching at most `12,107,808`–`12,574,440` valid `(a2, a3)` entries across `240`–`294` `kappa` groups (`285`–`300` bit-sliced prefix blocks, `152,850` worst-case pass ops/claw, `1,025,697 B` RAM).

We introduce two algebraic discoveries that compound multiplicatively:
1. **`k = 8` Transplant (`Tuple 124`, Section 2):** Instead of locking `(A[8..11], E[12..15], W[12..15])` to the published SFS trace, we release `E[12..15]` while constraining `(A[8..11], E[12..15], W[12..15])` so that **both** messages reconverge bit-for-bit to the exact published 256-bit states `(BA[16..19], BE[16..19])` and `(CA[16..19], CE[16..19])` after step 15 with identical `W[16] = G16` and `W[17] = W17PUB`. Across all 307 valid `k = 8` tuples and full exact `F10`-DFA beam search over fibre values, **`Tuple 124`** at fibre `FIB = 0x28b7f117` yields **62,955,816 exact valid entries** (a **5.01x–5.20x expansion** over `k = 4`!), organized into only **48 `kappa` groups** (`1,088` active classes, `9,906,695` distinct `(a2, kappa)` keys) with a tighter 13-bit `E[11]` cube (`8,192` points vs `131,072`).
2. **4-Family 22/29-Bit Prefix-Factorized `k4q` Tree (Section 3):** Exhaustive inspection of all 48 `kappa` groups of `Tuple 124` proves an exact algebraic factorization:
   `kappa = FAM_LO22[f] + MID_D1[d1] + TOP_D2[d2]` (`f in 0..3`, `d1 in 0..2`, `d2 in 0..3`),
   where all 12 groups inside each family `f` have **bit-for-bit identical 18-bit `a2` prefix sets** (sizes `1,312; 4,704; 1,536; 5,376`, totaling only **12,928 unique prefixes = 52 256-lane prefix blocks = 29,952 B of prefix RAM**, `11.6x` smaller than linear storage!) AND identical low 22 bits of `kappa`. Evaluating Stage 0 (bits `0..21`) once per family block, branching 3 ways on `MID_D1` (bits `22..28`) only for surviving blocks, and branching 4 ways on `TOP_D2` (bits `29..31`) only for Stage-1 survivors cuts average `k4q` pass cost from `127,123` ops/claw (`820db8f6`) down to **22,090 ops/claw** (deterministic worst-case survivor-free pass **48,364 ops**), requires **zero ad-hoc group pruning**, keeps **100% of all 62,955,816 entries**, and drops peak walk memory to **1,042,561 B** (`165,375 B` below `1 MiB`).

---

## 2. Algebraic Derivation of the `k = 8` Transplant (`Tuple 124`)

### 2.1 Published SFS anchor and advice (`220 B` total)
From ePrint 2026/1120 Table 23 (and `d3a46ae6` Section 2.1), the 160-byte published 39-round SFS collision pair `(CV_PUB, _mpx, M_PUB)` is:
- `CV_PUB`: `aa79ff87 65c5bb49 d0a84bfd 90ccc398 fac64fb6 4ff7998a b1af5ec5 aa1ed4d5`
- `M_PUB`:  `8334d670 3813877e f19d46d5 77556fc4 902f98c7 0500282c a4235533 9100e365 e76f5fe2 5633326d 9d603088 06a64487 a94ae11e b06304ad 43660038 d80d950f`
- `_mpx` agrees with `M_PUB` on words `0..7, 13..15` and satisfies `M_PUB[i] = (_mpx[i] + K4_DL[i]) mod 2^32`, where `K4_DL[8..12] = [0x40000000, 0xf7801000, 0xc0000000, 0x0601dcd4, 0xffefe800]`, with `G16 = expand(_mpx)[16] = 0xbca1c321` and `W17PUB = expand(_mpx)[17] = 0x71e9ba98`.
- The four modular-difference `s0` filters for rounds `23..26` are `inF(w, D_i, T_i) := ((s0((w + D_i) mod 2^32) - s0(w)) mod 2^32 == T_i)` for `(D8, T8) = (0x40000000, 0x087ff000)` (density `9/128`), `(D9, T9) = (0xf7801000, 0x03010000)` (density `1/64`), `(D10, T10) = (0xc0000000, 0x087ff000)` (exact `|F10| = 301,989,888`), and `(D11, T11) = (0x0601dcd4, 0x1fff41a0)` (exact `|F11| = 200,960`).

Our `k = 8` transplant adds **60 bytes** (15 32-bit words) of nonuniform advice, for **220 bytes total** (`log2(220) = 7.78135971352466`):
- `T124_A = A[8..11] = (0x203c1b5a, 0x58bd2ecb, 0xf5a01075, 0xcc8ef209)` (16 B)
- `T124_E = E[12..15] = (0x95dbb2a8, 0x2c210e77, 0x1e3b4ffd, 0xff00d825)` (16 B)
- `T124_W = W[12..15] = (0x576d201f, 0x306524bd, 0xc3662028, 0xd80db51f)` (16 B)
- `FIB = 0x28b7f117`, `E11_BASE = 0x08226d10`, `K4_CUBE = 0xf74400ca` (12 B).
`FAM_LO22`, `MID_D1`, `TOP_D2`, `T124_C9`, `K4_C11`, `K4_CA10`, `K4_W11C`, `R2_MASK`, and `W9C` are computed deterministically from these 220 B at import time (verified in `experiments/r39joint_k8_both_c.py`).

### 2.2 Exact `k = 8` reconvergence theorem (PROVED)
Let `(BA, BE)` and `(CA, CE)` denote the 39-round state trajectories of `(CV_PUB, _mpx)` and `(CV_PUB, M_PUB)` (`A[0..3] = cv[3..0]`, `A[r+4], E[r+4]` after round `r`). In rounds `r = 12..15`:
- **Message 1 (`W`):** `A[16..19]` and `E[16..19]` depend ONLY on `(A[12..15], E[12..15], W[12..15])`. Setting `E[12..15] = T124_E`, `W[12..15] = T124_W`, and `A[8..11] = T124_A` uniquely fixes `A[12..15]` via `A[r+4] = E[r+4] - A[r] + S0(A[r+3]) + MAJ(A[r+3], A[r+2], A[r+1])` for `r = 8..11` (independent of `cv` and `(a0, a1, a2, a3)`), propagating to exact `A1[16..19] == BA[16..19]` and `E1[16..19] == BE[16..19]`.
- **Message 2 (`V = W + K4_DL`), round 8 -> 9 (condition R5):** Round 8 injects `D8 = 0x40000000` into `E[12]`; since bit 30 of `T124_E[0] = 0x95dbb2a8` is `0`, `E2[12] = T124_E[0] ^ 0x40000000 = 0xd5dbb2a8`. In round 9, `CH(E2[12], E[11], E[10]) - CH(E1[12], E[11], E[10]) = 0` iff **bit 30 of `E[10] ^ E[11]` is `0`** (condition R5). Under R5, `t1_2(9) - t1_1(9) = S1(E2[12]) - S1(E1[12]) + D9 = 0x00f7ffe0 + 0xf7801000 = 0xf8780fe0`, fixing `E2[13] = (0x2c210e77 + 0xf8780fe0) mod 2^32 = 0x24991e57` and `A2[13]` completely.
- **Message 2, round 10 (condition R2):** Since `E1[13] ^ E2[13] = 0x2c210e77 ^ 0x24991e57 = 0x08b81020 =: R2_MASK` (7 active bits `{5, 12, 19, 20, 21, 23, 27}`), and bit 30 of both `E1[13]` and `E2[13]` is `0`, `CH(E2[13], E2[12], E[11]) - CH(E1[13], E1[12], E[11])` cancels `E[11]` on all bits outside `R2_MASK` and is completely fixed iff **`(E[11] & R2_MASK) == (E11_BASE & R2_MASK)` (`= 0x08200000`)** (condition R2). Notice `R2_MASK & K4_CUBE == 0x08b81020 & 0xf74400ca == 0`, so every `E[11] = E11_BASE | m` (`m submask K4_CUBE`) automatically satisfies R2 (and `h4ok(a2, a3)` checks R2 explicitly).
- **Rounds 11..15:** Under R5 and R2, `E2[12..15]` and `A2[12..15]` are fixed constants independent of `cv` and `(a0, a1, a2, a3)`, which under `T124_W + K4_DL[12..15]` propagate through rounds `12..15` to **exact equality** `A1[16..19] == BA[16..19]`, `E1[16..19] == BE[16..19]`, `A2[16..19] == CA[16..19]`, `E2[16..19] == CE[16..19]` for **every** chaining value `cv` and **every** `(a0, a1, a2, a3)` satisfying R2 and R5!
- In particular, once `W[16] = G16`, `W[17] = W17PUB`, and `W[8..11] in F8 x F9 x F10 x F11`, the two-message state entering round 16 is bit-for-bit identical to the published SFS pair on both messages, with `(Vx[16] - Wx[16]) = D9`, `(Vx[17] - Wx[17]) = D10`, and `(s0(V[i]) - s0(W[i])) = T_i` for `i = 8..11`.

### 2.3 Message-word equations, claw factorization, and `W[17]` decoupling (PROVED)
Given any `cv` and `(a0, a1, a2, a3) = A[4..7]`, `kw(cv, a0, a1, a2, a3)` uniquely recovers `W[0..11]` while `W[12..15] = T124_W`:
- `W[0]` depends only on `(cv, a0)`; `W[1] = u` determines `a1 = recover_a1(cv, a0, u)` independently of `(a2, a3)`.
- `E[11] = a3 + K4_C11` and `W[11] = K4_W11C - a3` depend ONLY on `a3`.
- `E[10] = a2 + t16(a3)` where `t16(a3) = K4_CA10 - MAJ(T124_A[1], T124_A[0], a3)`, and `W[10] = C17K(a3) - s1(T124_W[3]) - t16(a3) - a2`.
- `W[9] = W9C[6] - W9C[1] + h4(a2, a3) - a1`, where `h4(a2, a3) := (MAJ(T124_A[0], a3, a2) - CH(T124_E[0], E[11], E[10])) mod 2^32`.
Restricting `(a2, a3)` to the fixed fibre `h4(a2, a3) == FIB = 0x28b7f117` collapses `W[9]` to a per-claw constant:
`W[9] = T124_C9 - a1` (`T124_C9 = 0x18f234b7`),
so BOTH `W[9] in F9` and `W[16] = W[0] + s0(W[1]) + W[9] + s1(T124_W[2]) == G16` depend ONLY on `(cv, a0, u)` and are shared across all `62,955,816` entries of `Tuple 124`. Writing `fstep(a0, c) == fstep(u, c)` (even `a0`, odd `u`) yields `W[16] == G16` iff `(a0, u)` is a claw of the walk map `fstep`.
- Defining `kappa(a3) := (t16(a3) - C17K(a3)) mod 2^32`, round 17 expands to:
  `W[17] = W[1] + s0(W[2]) + W[10] + s1(W[15]) = u + s0(a2 + w2b) - a2 - kappa(a3)`,
  where `w2b = W[2] - a2` depends ONLY on `(cv, a0, a1)`. Setting `y = (a2 + w2b) mod 2^32` gives the exact `W[17] == W17PUB` equation:
  `s0(y) == (y + kappa + W17PUB - u - w2b) mod 2^32`.
Every valid `(a2, a3)` is therefore characterized by the 5 exact conditions (`h4ok(a2, a3)`):
1. `(E[11] & R2_MASK) == (E11_BASE & R2_MASK)` (R2);
2. `W[11](a3) in F11` (`a3` from the 13-bit cube `E[11] = E11_BASE | m`, `m submask K4_CUBE`, giving `2,048` valid `a3` values out of `8,192` cube points);
3. `bit 30(E[10] ^ E[11]) == 0` (R5);
4. `h4(a2, a3) == FIB`;
5. `W[10](a2, a3) in F10`.

### 2.4 Exact list census (EXHAUSTIVE)
Running the exact bit-serial `F10`/fibre DFA over all `2,048` valid `a3` values of `Tuple 124` (verified independently in C (`cohit_all48.c`, `prod_panel_t124_48.c`) and Python (`experiments/r39joint_k8_both_c.py`)):
- **Active `kappa` groups:** `48` (all non-empty, zero groups dropped).
- **Active `a3` classes:** `1,088` (at most `32` classes per group).
- **Exact valid `(a2, a3)` entries:** **`62,955,816`** (5.01x larger than `k = 4`'s maximal `12,574,440`).
- **Exact distinct `(a2, kappa)` keys:** **`9,906,695`**.
- Verified on `5,000/5,000` random `(cv, a0, u)` trials (`verify_t124_all_identities.c`) and `255` organizer trials (`r39-transplant-claw`) with 0 mismatches on `W[1]`, `W[9]`, `W[16]`, `W9C`, `w2b`, and 16-step two-message reconvergence.

---

## 3. Exact 4-Family 22/29-Bit Prefix Factorization and 52-Block `k4q` Tree

### 3.1 Exact 4-family structural theorem (EXHAUSTIVE, asserted at import)
Sorting the 48 active `kappa` values of `Tuple 124` reveals a complete Cartesian factorization into `4 x 3 x 4 = 48` groups:
- Low 22 bits (`bits 0..21`, 4 families): `FAM_LO22 = (0x00271f63, 0x00271f6b, 0x002b1f63, 0x002b1f6b)`.
- Mid 7 bits (`bits 22..28`, 3 branches): `MID_D1 = (0x0a000000, 0x0e400000, 0x0f000000)` (all bits `0..21` are `0`).
- Top 3 bits (`bits 29..31`, 4 branches): `TOP_D2 = (0x00000000, 0x60000000, 0x80000000, 0xe0000000)` (all bits `0..28` are `0`).
Every one of the 48 groups satisfies `kappa = (FAM_LO22[f] + MID_D1[d1] + TOP_D2[d2]) mod 2^32`.

Furthermore, exhaustive DFA traversal over each family's 512 candidate classes proves (and `experiments/r39joint_k8_both_c.py` hard-asserts at import on every single 18-bit prefix leaf) that **all 12 active groups inside each family `f` share the exact same set of valid 18-bit `a2` prefixes**:
- Family 0 (`0x00271f63`): `1,312` unique 18-bit prefixes -> `6` 256-lane blocks.
- Family 1 (`0x00271f6b`): `4,704` unique 18-bit prefixes -> `19` 256-lane blocks.
- Family 2 (`0x002b1f63`): `1,536` unique 18-bit prefixes -> `6` 256-lane blocks.
- Family 3 (`0x002b1f6b`): `5,376` unique 18-bit prefixes -> `21` 256-lane blocks.
- **Total across all 48 groups:** **`12,928` unique 18-bit prefixes packed into ONLY `52` bit-sliced blocks** (`52 x 18 x 32 B = 29,952 B` of prefix RAM, vs `164,160 B` for 285 blocks in `820db8f6`).

### 3.2 Exact 3-stage bit-sliced `k4q` pass
In `s0(y) == (y + r) mod 2^32` with `r = (kappa + W17PUB - u - w2b) mod 2^32`:
- Because `MID_D1[d1]` has bits `0..21` identically zero and `TOP_D2[d2]` has bits `0..28` identically zero, modular addition `r = r0 + MID_D1[d1] + TOP_D2[d2]` (where `r0 = (FAM_LO22[f] + W17PUB - u - w2b) mod 2^32`) **cannot affect bits `0..21` of `r`**, and adding `TOP_D2[d2]` to `r1 = r0 + MID_D1[d1]` **cannot affect bits `0..28` of `r`**.
- Consequently, for each of the `52` family blocks (256 parallel lanes):
  - **Stage 0 (shared across all 12 groups in family `f`):** Add the 18-bit prefix planes `P[0..17]` to `WB[0..17]` (`y[0..17]`), propagate `i = 0..13` to reconstruct upper bits `y[18..31]`, and check the 8 filter bits `i = 14..21` using `r0[0..21]`. Any block with zero surviving lanes (`36.8%` of blocks) exits immediately (`308 + 4 = 312` ops/dead block; `308` ops entering Stage 1).
  - **Stage 1 (3 branches `d1 in 0..2`):** Only for blocks surviving Stage 0, lazily broadcast `r1[d1][22..28]` (once per family) and check bits `i = 22..28` with early exits at `i = 25` and `i = 28` (`<= 71` ops/branch).
  - **Stage 2 (4 branches `d2 in 0..3`):** Only for `(block, d1)` pairs surviving Stage 1 (`~1.2` times per claw), lazily broadcast `r2[d1][d2][29..31]` and check bits `i = 29..31` (`31` ops/branch).
  - **Scalar survivor & mate verification:** Each surviving lane extracts `x = y`, sets `a2 = (x - w2b) mod 2^32`, screens all `a3` classes in group `gidx[d1][d2]` with the `W9C` prefilter (charged `20` ops/class to cover `ld`, arithmetic, mask/branch, and loop), checks full `kw` + `W[17] == W17PUB` + `W[10] in F10` (`563` ops), and on a key hit evaluates all `F8`-passing mates `b3` in that group (`560` ops + `2 x 2,812` ops for two 39-round compressions).

**Bit-exact equivalence (PROVED & MEASURED):** `prod_panel_t124_48.c` verified `atk_k4q_tree` against a brute-force linear 48-group scan on 48/48 planted group hits (one per group) plus 100 random claws (`46` random survivors) with **0 mismatches**. `experiments/r39joint_k8_both_c.py` repeats the 48/48 planted `k4_w17a >= 1` check on both `CV_PUB` (`r39-transplant-claw`) and a real walk `cv` (`r39k4-window-small`).

---

## 4. Complete Attack Specification, Guard Reservations, and Memory Audit

### 4.1 Walk, screening, stage-2, and 944-claw gate
The base walk and `Mach` 256-bit word-operation model match accepted `d3a46ae6` / `04f61e00` exactly:
- **Screening (`screen = 1`):** Draw a fresh 512-bit block `M0`, compute `cv = Compress_39(IV, M0)` (`2,812` ops), compute `S = k4_scr(cv)` (`69` ops; `+3` if `S > 5`; a 3-lane SWAR `Mach` implementation requires `~56 <= 69` ops), accept iff `S <= 5` (up to `DTRY = 8,192` draws), then build folded bit-sliced kernels (`DPB = 7`, `KCAP = 679` gates, `RCAP = 206` regs, `GCAP = 575,000` ops, up to `KTRY = 32` attempts).
- **Stage 1 & Stage 2:** 256 parallel lanes, `15,520`-word distinguished-point table (`99,328` 40-bit slots), `640`-entry pair queue (`QFULL = 384`), `2,048`-slot timing wheel, `cutscan` every `512` steps, `2^26` primary walk evaluations plus `1/4` extension (`327,680` total `iter1` steps uncapped).
- **944-claw dedupe gate (`k4d`):** Open-addressed `1,536`-slot table (`6,172` ops init on first F9 claw) admitting at most **944 distinct F9 claws per window** to `k4_eval`.
- **Per-window hard work cap (`WMAX_CAP = 440,000,000`):** Every window enforces `m.o <= WMAX_CAP` via `cap(R)` guards (`+2` ops per check) with hard assertion `m.o - gl <= gR` between consecutive guards.

### 4.2 Deterministic worst-case guard table (PROVED, `g8` interval 16, `g6 = 17,000`)
We keep `d3a46ae6`'s `it % 16 == 0` interval for `g8` (`16 x 708 = 11,328` ops max across 16 hit-free `iter1` steps) and raise `g6` to `17,000` (strictly exceeding worst-case adversarial `k4d` linear probing across all 944 occupied slots + wrap + `stage2` tail: `16,246 < 17,000`, and `159 + 6,202 + 2 = 6,363 < 17,000` on first-call table init; inside `stage2`, `g6` always hits `g11`, `g6`, `g3`, or `g7` next, never `iter1`). Thus **every single guard `g1..g15` is an unconditional deterministic worst-case upper bound**:
- **Worst-case survivor-free `k4q` pass (`K4_PASS_WC`):** Entry + `w2b` + `WB` (`748`; exact hand count `721`) + 4 families' lazy setups (`4 x (79 + 72 + 144) = 1,180`) + 52 blocks x (Stage 0 `308` + 3 Stage-1 branches `213` + 12 Stage-2 branches `372` = `893`) = **`48,364` ops**.

| Guard | Location | Deterministic worst-case ops to next guard | Reserve `R` | Max observed (384 windows) |
|---|---|---:|---:|---:|
| `g1` | `iter1` hit group | `1,799 + 11,328 = 13,127` | `13,129` | `7,170` |
| `g2` | `iter1` `cutscan` | `35,328 + 11,328 = 46,656` (256 lanes cut) | `76,864` | `299` |
| `g3`, `g9` | `stage2` iter / entry | `899 + 11,328 = 12,227` | `15,424` | `509` |
| `g4` | `stage2` wheel callback | `742 + 11,328 = 12,070` | `12,352` | `272` |
| `g5` | `stage2` launch | `1,317 + 11,328 = 12,645` | `15,424` | `907` |
| `g6` | `stage2` merge + `k4d` | `16,246` (adversarial 944-slot probe) or `6,363` (init) | `17,000` | `6,363` |
| `g7` | `stage2` exit | `563 + 11,328 = 11,891` | `13,376` | `5,393` |
| `g8` | `run_window` (`it % 16 == 0`) | `16 x 708 = 11,328` | `15,424` | `6,911` |
| `g10` | `run_window` end | `11,328` | `11,328` | `0` |
| `g11` | `k4_eval` entry | `K4_PASS_WC + 62 = 48,426` | `55,000` | `23,474` |
| `g13` | `k4q` survivor | `<= 200` (all 48 groups nonempty -> hits `g14`) | `55,000` | `136` |
| `g14` | `k4q` class test | `20 + 563 + 48,426 = 49,009` | `55,000` | `22,036` |
| `g15` | `k4q` mate check | `560 + 5,624 + 48,426 = 54,610` | `62,000` | `20,924` |

### 4.3 Self-contained itemized memory audit across all phases (`memory_log2_bytes = 20.0`)
The run executes in three disjoint phases: **Phase S** (one-time import/setup building `K4_Q` and `K4_FAM` one family at a time, then freeing all builder structures), **Phase G** (per-window `M0` compression and folded kernel generation, freeing generator graphs before walking), and **Phase W** (walk + stage-2 + `k4q`). Every single buffer is itemized explicitly below (no opaque inherited constants):

**Phase W (peak phase, `K4_MEM = 1,042,561 B = 2^19.9918 <= 2^20`, headroom `6,015 B` below `1 MiB` on top of the `32,768 B` reserve):**

| Resident / Walk-Phase Component | Size (bytes) |
|---|---:|
| Walk distinguished-point table (`20,500 x 32 B`; `128,000` 41-bit records) | `656,000` |
| Stage-2 pair queue (`161 x 32 B`; `640` 64-bit entries + tail word) | `5,152` |
| 4-family prefix table `K4_FAM` (`52` blocks x `18` planes x `32 B`) | `29,952` |
| Register file (`256 x 32 B`) + lane array `LA` (`256 x 32 B`) | `16,384` |
| Timing wheel (`128`), pair records (`32`), stage-1 save (`32`), free stack (`4`) (`196 x 32 B`) | `6,272` |
| Folded kernel images (`2 x 679 x 5 B = 6,790 B`, reserved to `2 x 1,024 x 5 B` envelope) | `10,240` |
| Walk instruction code census (`4,111 x 36 B`) | `147,996` |
| `k4` code census (`2,592 x 36 B = 93,312 B`) + inlined constants (`4,448 B`) | `97,760` |
| `k4q` 256-bit scratch planes (`WB[18]+buf0[22]+buf1[21]+buf2[36]+y[32] = 129 x 32 B`) + reg save (`104 x 32 B`) | `7,456` |
| `Tuple 124` `K4_Q` metadata (`48 x 16 B` + `1,088 x 4 B` `a3` words + `296 B` family/branch/advice consts) | `5,416` |
| 944-claw dedupe table (`1,536 x 8 B` keys + `192 B` bitmap + `3,076 B` index/cursor) | `15,556` |
| Attack state scalars (`3,968`), counters (`616`), transient compression/output (`3,136`), module data (`3,889`) | `11,609` |
| Explicit walk-phase headroom reserve | `32,768` |
| **Total Phase-W Peak RAM (`K4_MEM`, asserted in `r39joint_k8_both_c.py`)** | **`1,042,561`** |

**Phase S (4-family chunked builder, `584,292 B < K4_MEM < 2^20`):** `_k4build_all48()` processes **one `FAM_LO22` family (`512` candidate classes = `64 B` mask) at a time**, freeing `F[0..32]` before the 18-bit DFS and freeing `trans[0..17]` before block transposition. Exact measured maxima across all 4 families (`test_4fam_build.py`): `2,048` candidate class records (`57,344 B`), family `PL`+`V` (`16,384 B`), `F[0..32]` at most `1,638` states x `68 B = 111,384 B`, `trans[0..17]` at most `1,324` edges x `68 B = 90,032 B` (during DFS after `F` is freed, `max_stack = 13` entries + `pf <= 5,376 x 4 B` use `<= 49,792 B < 111,384 B`), plus resident code/completed blocks/reserve (`309,148 B`) = **`584,292 B` peak Phase-S RAM** (`464,284 B` below `1 MiB`; CPython `tracemalloc` peak `2.30 MB << 128 MiB` Docker limit).
**Phase G (kernel generation, `< 520 KiB`):** Identical to `d3a46ae6` (`~510 KiB`, generator graph `~49 KiB`, no walk table allocated during Phase G).
**Declared memory coordinate:** `memory_log2_bytes = 20.0`, giving `max(0, 20.0 - 20) = 0.0` memory penalty.

### 4.4 Setup and preprocessing cost (`preprocessing_log2 = 43`, `H3-advice-construction`)
- **One-time runtime setup (`K4_SETUP`):** `_k4build_all48()` counts `_K4_BUILD_OPS = 10,580,028` ops across `_k4st`, `PL`, DFS pop, and `_k4tr`, and adds a generous conservative `+ 2^30 + 6,512` envelope (`K4_SETUP = 1,084,328,364 <= K4_SETUP_PRICED = 1,100,000,000`) covering the `8,192` `inF` checks, class sorting, and inner DFS loop bookkeeping.
- **Offline preprocessing (`preprocessing_log2 = 43`, `2,812 x 2^43 = 24,734,613,578,448,896` word ops added directly to `N_TOTAL`):** Generating the `220 B` of nonuniform advice is explicitly budgeted under `H3-advice-construction`:
  1. **Published 39-round SFS collision pair (`160 B`: `CV_PUB, _mpx, M_PUB`, ePrint 2026/1120 Table 23):** As accounted in the accepted 39-round lineage (`d3a46ae6` / `820db8f6` Section 9), selecting this pair from the 93-pair local-collision SFS campaign costs `93 x 2^36 = 2^42.5392` pair constructions plus `93 x 14 x 2^24 = 2^34.35` screens = **`2^42.545` compressions**, leaving **`2^41.1` compressions** of remaining headroom inside the declared `preprocessing_log2 = 43` budget. Furthermore, constructing fresh verified 39-round SFS collisions conforming to the Table 21 differential characteristic from the step-12..17 pin is **directly executed inside `experiments/r39joint_k8_both_c.py`** (`_smc` solving rounds `18..23` + `_finals` + `_verify_smc_hit` inverting `W[7..0]` and rounds `15..0` across `r39-mate-01..14`, producing `165` `T124` + `152` `PUB` verified 39-round SFS collisions at `< 2^17` compressions and `< 200 KiB` working RAM).
  2. **`Tuple 124` `60 B` offline search (`T124_A, T124_E, T124_W, FIB, E11_BASE, K4_CUBE`):** Exhaustive enumeration of all `307` `k = 8` reconverging tuples (`2^32` F11-cube scan + exact 4-family chunked `F10`-DFA beam search over fibre values) costs `< 2^32` word ops **`< 2^21` compressions** and `<= 584,292 B` working RAM (using the same 4-family chunked DFA as Phase S), fitting with `> 2^20`x margin inside the `2^41.1` remaining preprocessing headroom.
  3. **Offline mathematical analysis theorems (not algorithm preprocessing):** The exhaustive `2^32` row-19 mate proof (`230` offsets, `< 2^34` compressions) and `2^32` `s0(y) - y` `M_48 = 107` proof (`< 2^27` compressions) establish static properties of SHA-256 constants; the attack algorithm never executes them or stores their tables (and even if charged, they sit `> 2^7`x inside the `2^41.1` headroom).
- **Memory & score sensitivity:** Online Phase-W (`1,042,561 B`), Phase-S (`584,292 B`), Phase-G (`< 520 KiB`), `Tuple 124` search (`<= 584,292 B`), and live SMC collision generation (`< 200 KiB`) all run strictly inside `2^20 B`; the original 93-pair SFS campaign was run externally by the pair's authors and is charged at `2^42.545 <= 2^43` compressions under `H3-advice-construction`. Numerically, `2^43` compressions is `~2^-48.3` of total attack time `2^91.29` (even `2^73` preprocessing shifts `time_log2` by `< 10^-5` bits).

---

## 5. Empirical Panels (6-Way Bonferroni Simultaneous Bounds) and Exhaustive Proofs

To control multiple comparisons across all **six** empirically estimated ledger parameters (`R_SAFE_LB`, `ESW1_UB`, `EN_LB`, `MU_D`, `Q4_UB`, `p_tail`), every single one uses a **6-way Bonferroni-adjusted one-sided confidence bound (`alpha_i = 0.01 / 6 = 0.0016667`, `99.833%` per parameter, `>= 99%` simultaneous family-wise error rate)** on the exact shipped `Tuple 124` ALL-48 4-family algorithm (`g8` interval 16, `g6 = 17,000`, `W9C = 20` ops). `PI_BAR` is fixed above the list-uniform analytic reference and `EPS_KEY = 2^-7` is an explicitly declared heuristic ceiling; neither is represented as a seventh or eighth confidence interval:
- **Selection-bias controls and honest disclosure:** (1) `Tuple 124` (`FIB = 0x28b7f117`) was selected **100% deterministically by exact algebraic DFA counting** (`62,955,816` entries, `48` groups, `52` prefix blocks) before any walk or SMC simulation ran — zero statistical selection over tuples or fibres; (2) Discovery (`seeds 8,000,000..8,000,127`) selected only one scalar (`WMAX_CAP = 440,000,000`, rounded cleanly to `5,000,000`); (3) Holdout (`8,500,000..8,500,255`) and SMC (`1..28`) used contiguous sequential seed ranges with zero seed cherry-picking, cross-checked against exact theoretical expectations (`F8` entries `4,427,108.32` vs `62,955,816 x 9/128 = 4,426,580.8`, matching to `0.012%`; `E[min(N_k, 3)] = 2.2578e-3` vs uniform `2.3066e-3`; `T124` vs `PUB` paired SMC difference `+0.01666` bits); and (4) this derivative prices `p_tail = 2^-74.446970`, the 6-way Bonferroni class-01 LCB of the preregistered 30,720-seed extended panel (Section 5.3a), instead of the 28-seed `2^-74.71347` (whose separately reported 99.9% single-parameter LCB `2^-74.74164` was never the priced family). Nevertheless, because participant panels have no cryptographic `holdout_nonce` pre-commitment and organizer seeds are public, non-selection of these panels is explicitly declared as a heuristic premise and limitation (Section 7), not a formally verified commitment.

### 5.1 Discovery Panel (128 windows) and Disjoint Holdout Panel (256 windows)
1. **Discovery Panel (`prod_panel_t124_48_final`, seeds `8,000,000..8,000,127`, 128 full `2^26` screened windows, uncapped, 944-claw gate):**
   - Saturated `944` claws in `128/128` windows; mean `total_ops = 606,803,907`, mean `k4_ops = 20,855,081` (`22,092.2` ops/claw), `max_single_pass = 66,657`.
   - Exact pooled argmin of `(W + 6) / r(W)` occurred at `W = 469,865,014` (`kept = 114,102 / 120,832`, `r = 0.94430283`, `(W+6)/r = 497,578,746`).
   - Rounded cleanly to the nearest `5,000,000` and frozen for the historical one-choice base: **`WMAX_CAP = 470,000,000`** (`r = 0.944518` on that Discovery panel). This value is not priced by the present row.
2. **Disjoint Holdout Panel (seeds `8,500,000..8,500,255`, 256 contiguous disjoint full `2^26` screened windows, `241,664` claws; exact one-sided Bonferroni `t_{255, 1-0.01/6} = 2.963112`):**
   - Saturated `944` claws in `256/256` windows; mean `total_ops = 606,668,204`, mean `k4_ops = 20,852,592` (`22,089.6` ops/claw), `max_single_pass = 77,232`; **0 guard violations** across all 384 windows.
   - **Safe pre-`k4q` retention at `W_SAFE = WMAX_CAP - B_CLAW = 467,000,000` (`B_CLAW = 3,000,000`, proved deterministically in Section 6.1):** Recording `M_pre(i)` (running max of `m.o + R` over every guard strictly before `k4_eval` on claw `i`, taking `max(M_pre(i), m.o_before_g11)`): `kept_safe = 226,576 / 241,664` (`0 / 241,664` monotonicity violations, `max(stamp - M_pre) = 106,062 << B_CLAW`), window mean `r_safe = 0.93756621` (s.d. `0.030207`, s.e. `0.001888`), 6-way Bonferroni lower bound (`99.833%`, `t_{255} = 2.963112`): `0.93197186`. **Superseded for pricing** by the extended panel below (`R_SAFE_LB = 0.95286309`).

   - **Two-choice 8,192-window panel (this derivative):** preregistered before 7,936 new windows (SHA-256 `39dd14799a044573ac3dfa66d60af202b4891cfb7ee5ea5ff0a62622981d9411`); seeds `8,600,001..8,608,192`. The first 4,096 windows selected `WMAX_CAP = 440,000,000` on the frozen 400M..560M one-million grid by minimizing `(cap+6)/LCB`. The disjoint second 4,096 windows had mean safe-claw retention `0.954175` and one-sided Bonferroni-6 LCB `0.95286309`, priced as `R_SAFE_LB = 0.95286309` without pooling. Evidence: `PANEL8192_RESULT.md`, `DEPENDENCY_MANIFEST_8192.md`, and CRAM `L-311820b088`.
   - **Claw-weighted `E[s_w - 1]` (upper-bounded using all `s_w` claws completed up to `WMAX_CAP`, strictly `>= s_safe`):** ratio estimator `sum s_w(s_w - 1) / sum s_w = 890.7352` (s.e. `1.7601`), 6-way Bonferroni UCB (`99.833%`): `895.9506`. **Priced conservatively:** **`ESW1_UB = 896`**.
   - **`F8`-passing entries & distinct keys per evaluated `F9` claw (first 32 holdout windows, every 8th claw of `944` = `118` claws/window -> `3,776` real screened `F9` claws; SE and exact 6-way Bonferroni `t_{31, 1-0.01/6} = 3.180018` computed over the 32 window means):**
     - `F8`-entries/claw: mean **`4,427,108.32`** (window s.d. `44,895.01`, s.e. `7,936.39`, **6-way Bonferroni LCB = `4,401,870.46`**; matches theoretical `62,955,816 x 9/128 = 4,426,580.8` to `0.012%` = `0.066` s.e.). No arrival-rank drift: ranks `1..125` mean `4,430,840.4` vs ranks `126..944` mean `4,426,522.9`. **Superseded for pricing** by the extended EN panel below (`EN_LB = 4,414,590.97`).

   - **Extended EN panel (this derivative, Section 5.2b):** the exact number of `F8`-passing valid entries was counted for **16,384 claws** (completion indices `0, 118, ..., 826` of each of the 2,048 windows `8,600,001..8,602,048` of Section 5.2a; `a1 = recover_a1(cv, a0, u)`), over **all `62,955,816` entries** (dumped from this package's exact per-class DP; per-group counts equal `G48_W`). `W8` is evaluated exactly as `kw()[8]` (checked on 20,000 random inputs; a C counter checked against this package's own Python `kw`/`inF` count). Window-mean EN `4,424,756.50` (window s.d. `156,547.82`; the exact uniform-`W8` expectation is `4,426,580.81`), one-sided 6-way Bonferroni `t_{2047} = 2.938650` lower bound `4,414,590.9723`, **priced as `EN_LB = 4,414,590.97`** (rounded down at 2 decimals). Preregistered before the panel count (SHA-256 `35145d0ba0c88c56b68c756bb331640f39c377b98710e37d6fb6f0441fbdd573`); disclosed: one window (`8,600,001`) was counted before the preregistration as a timing/control run and is part of the panel; the sampling design (8 claws x 2,048 windows) differs from the 3,776-claw holdout (118 claws x 32 windows); participant-run, no nonce. Evidence: per-claw count records, entry dump procedure, counter and aggregator, available on request.
     - `F8`-keys/claw: mean `3,183,547.15` (window s.d. `24,935.69`, s.e. `4,408.05`, **6-way Bonferroni UCB = `3,197,564.83`**). **Priced conservatively:** **`MU_D = 3,198,000`**.
   - **Direct Capped Replay:** Passed **8/8** holdout seeds (`8,500,000..8,500,007`) verifying exact `m.o <= 470,000,000` on the historical one-choice base (the shipped derivative source enforces `m.o <= WMAX_CAP = 440,000,000` by its hard CapStop) and bit-for-bit evaluated claw prefix identity against `_stamp`.

### 5.2 Exhaustive `2^32` row-19 mate proof and `16,384`-`w` `equal-G` co-hit proof
1. **Self-contained row-19 mate exclusion theorem (`row19_t124.c` + `cohit_all48.c`, EXHAUSTIVE):**
   - Starting from the exact step-16/17 states `(BA[16..21], BE[16..21])` and `(CA[16..21], CE[16..21])`, let `P subset Z_{2^32}` be the set of round-18 words `W[18]` such that message 1 and message 2 satisfy the exact round-18 XOR state differences `(dA[22], dE[22]) = (0x40000000, 0)` AND admit the round-19 modular differences `dA[23] = 0` and `dE[23] in {+-2^19 +- 2^5}`. Exhaustive enumeration over all `2^32` words `W[18]` gives exact `|P| = 65,536`, and exact difference set `D := (P - P) mod 2^32` has cardinality **`|D| = 9,427,275`** (`2^23.168`).
   - Consider two mates `(a2, a3)` and `(a2, b3)` sharing the same key `(a2, kappa)` on the same claw `(cv, a0, a1, u)` with `d := (b3 - a3) mod 2^32 != 0`. Because `W[0..2]` and `W[10]` are unchanged across mates while `W[3]` shifts by `d` (from round 3: `A[7] = a3 -> b3`) and `W[11]` shifts by `-d` (`W[11] = K4_W11C - a3`), the round-18 schedule word `W[18] = W[2] + s0(W[3]) + W[11] + s1(W[16])` shifts by exactly:
     `Delta(W[3], d) := (s0((W[3] + d) mod 2^32) - s0(W[3]) - d) mod 2^32`.
   - For BOTH `(a2, a3)` and its mate `(a2, b3)` to stay on the differential trail through row 19, both `W[18]` and `W[18] + Delta(W[3], d)` must lie in `P`, which requires `W[3] in B_d := {w in Z_{2^32} : Delta(w, d) in D}`.
   - Enumerating ALL `2^32` values of `W[3]` across ALL `230` distinct mate offsets `d = (b3 - a3) mod 2^32` occurring in any of the 48 groups of `Tuple 124` proves:
     - **`Delta(W[3], d) == 0` count = `0`** across ALL `230` offsets and ALL `2^32` inputs (impossible for any mate to coincide on row 18!).
     - Exact pointwise worst-case mate sum across ALL `62,955,816` entries (`1,088` classes, `48` groups):
       `max_{a3} sum_{b3 != a3 in group} |B_{b3 - a3}| = 3,113,266` out of `2^32`.
     - Thus **`eps_mate = 3,113,266 / 2^32 = 7.248637e-4`** and **`eps_mate / 2 = 3,113,266 / 2^33 = 3.624319e-4`** holds **pointwise for every entry**.
2. **Exact `16,384`-`w` `equal-G` co-hit sweep (`cohit_all48.c`, MEASURED):**
   - Over all `9,906,695` distinct `(a2, kappa)` keys across all 48 groups at `16,384` independent uniform `w` values (`1.623 x 10^11` key-trials):
     - Exact measured list mean `E[N_k] = E[min(N_k, 3)] = 2.25781938e-3`, strictly **below** the uniform random baseline `9,906,694 / 2^32 = 2.30658194e-3`. **Priced conservatively:** **`PI_BAR = 2.31e-3`**.
     - Exact count with `N_k >= 4`: **`0` out of `1.623 x 10^11` key-trials** (`0 / 16,384` `w`-values, `max N_k = 3`). Exact 6-way Bonferroni Clopper-Pearson upper bound (`alpha_i = 0.01 / 6`, `99.833%`) across the `16,384` independent `w`-draws: `1 - (0.01/6)^(1/16384) = 3.90361e-4`. **Priced conservatively:** **`Q4_UB = 3.91e-4`**.

### 5.3 28-Seed Paired ALL-48 SMC Tail, Mate, Cross-Claw, and `W[3]` Uniformity Panel
Running `tail_panel_all48.py` across 28 contiguous independent paired seeds (`1..28`, `NP = 100`, `4 chunks x 40 batches x 2,048 lanes = 327,680` trials/seed/arm, **`9,175,040` total trials/arm**), sampling `(a2, a3)` uniformly over ALL `62,955,816` entries of all 48 groups via exact DP (`T124-ALL48`) vs the published SFS trace (`PUB`) on identical SMC carriers (where each independent seed gives one unbiased importance-weighted estimate `hat{p}_s = 2^{l2_s} * hits_s / 327,680`, so between-seed variance over the 28 independent seeds fully captures within-seed resampling variance):
- **Exact carrier identity:** `l2(PUB) == l2(T124-ALL48)` bit-for-bit on **28/28** seeds.
- **`PUB` control:** `1,232` full verified 39-round collisions, pooled mean **`2^-74.39429`** (s.e. `0.0800` bits, 6-way Bonferroni LCB `2^-74.67799`).
- **`T124-ALL48` (all 48 groups):** `1,246` full verified 39-round collisions (`cls = [326, 322, 297, 301]`, exact 6-way Bonferroni `t_{27, 1-0.01/6} = 3.219404`):
  - Pooled mean **`2^-74.37763`** (s.e. `0.0775` bits, 6-way Bonferroni LCB `2^-74.65170`, 99.9% LCB `2^-74.67073`).
  - Class-01 (`a0` even, `W[1]` odd) mean **`2^-74.32531`** (`322/1,246 = 25.84%`, s.e. `0.1057` bits, 6-way Bonferroni LCB **`2^-74.71347`**, 99.9% LCB **`2^-74.74164`**).
  - Paired difference `log2(T124-ALL48 / PUB) = +0.01666` bits (seed-mean `+0.02237 +- 0.0591` bits, `z = +0.38`): indistinguishable from `PUB`.
  - **Superseded for pricing:** the 28-seed class-01 Bonferroni-6 LCB `2^-74.71347` is replaced by the 30,720-seed extended panel bound **`p_tail = 2^-74.446970`** (Section 5.3a). The separately reported 99.9% (`alpha = 0.001`) single-parameter class-01 LCB is `2^-74.74164`; it is not the priced simultaneous family.

### 5.3a Extended tail panel (this derivative's only priced change)
The class-01 tail bound is re-measured on **30,720 additional independent seeds** in four preregistered stages (each stage's seed range, estimator, aggregator and pooling rule were hashed and posted before its first seed: PREREG sha256 d6a46a60eac857d73bcc803c607e362676cb0b3d5c71ae5ec4f8b44765ac3c75 (n=512, seeds 100001..100512), 73fab15e07e42801d6792b1d305b3e297f30187f37bd9231018650a1fe63bb91 (n=2,048, seeds 200001..202048), 6d807efc6e98b8fc08c5cd9de5a9ecae7b0f89363d257c13d96c8ec44d0dfb9e (n=7,680, seeds 300001..307680), 7b052492775d0f4dde9c9234a565f1d5323260d70a5982074ed8ae858a8cfb2a (n=20,480, seeds 400001..420480)). The estimator is a statistically equivalent rebuild of the 5.3 panel on this package's own SMC engine (`_smc`, `_finals`, `_verify_smc_hit` with their asserts; per seed 4 chunks x 40 batches x 2,048 lanes = 327,680 trials, `(a2, a3)` drawn by the exact `G48_W` entry weights and the exact per-group DP sampler). Seeds are the units; the bound is the same one-sided 6-way Bonferroni `t_{n-1, 1-0.01/6}` lower bound on the linear scale.
- Pooled 30,720 seeds (`100001..100512`, `200001..202048`, `300001..307680`, `400001..420480`; `10,066,329,600` trials; `1,382,869` verified 39-round collisions, `345,587` class 01): class-01 mean **`2^-74.438943`**, s.e. `0.0027` bit, `t_{30719} = 2.935429`, Bonferroni-6 LCB **`2^-74.4469693`**, stated rounded down at 6 decimals as **`p_tail = 2^-74.446970`**.
- Replications: 20,480 new seeds alone `2^-74.449792`; 7,680 seeds alone `2^-74.454270`; 2,048 seeds `2^-74.462083`; 512 seeds `2^-74.505496`. The class-01 mean is stable across stages (`2^-74.430853 .. 2^-74.442642`) and lies `0.11` bit below the 28-seed panel mean `2^-74.32531` of 5.3 (the 28-seed panel was on the optimistic side; the gain is the narrower confidence margin, `0.0080` bit vs `0.388` bit).
- Disclosed limitations: participant-run (no cryptographic `holdout_nonce`; seed ranges fixed and hashed before running); a statistically equivalent rebuild, not a bit replay of 5.3's seeding; the 28-seed 5.3 values are superseded, not pooled; the Bonferroni-6 family is unchanged (this input re-measured). Evidence: participant panel records for seeds `100001..100512`, `200001..202048`, `300001..307680`, `400001..420480` (one record per seed), with the runner, aggregator and the four preregistrations (SHA-256 `d6a46a60...`, `73fab15e...`, `6d807efc...`, `7b052492...`), available on request.
- **Mate verification:** `11,726` mates checked across the `1,246` hits -> `972` passed `F8`, **`through19 = 0`** (`337` deviated at row 18, `635` deviated at row 19).
- **Cross-claw empirical check:** Across the `1,246` colliding `cv` clusters (`64` virtual other-claw trials per hit -> `79,744` clustered trials/arm, real hit `cv` vs uniform random `cv`): `xa18 = 40,152` vs `xu18 = 40,046` (ratio `1.00265`), **`xa20 = 0`, `xu20 = 0`**. Because blocks of 64 trials share a single hit `cv`, we do **not** claim an i.i.d. `n = 79,744` Clopper-Pearson bound; rather, `EPS_KEY = 2^-7` is a declared heuristic ceiling (`H-cross-claw`) supported by exact empirical parity with the random-`cv` baseline (`~2^-18..2^-22` row-19 survival probability, leaving >8 bits of heuristic margin even after a 32-mate union bound).
- **`W[3]` uniformity (`1,246` hits):** per-bit `chi^2 (32 df) = 28.72` (expected `32.0`, 99.9% cutoff `62.49`).

---

## 6. Success-Probability Proof (`>= 0.39`) and Exact Integer Ledger

### 6.1 Second-order Bonferroni lower bound on window collision probability
Consider one capped window `w` completing `s_w <= 944` distinct `F9` claws. Let `K_c` be the `F8`-active distinct `(a2, kappa)` keys on claw `c`, `M_{c,k}` the `F8`-passing mates of key `k`, `H_{c,k}` the event that key `k` hits `W[17] == W17PUB`, `E_{c,e}` the event that entry `e in M_{c,k}` yields a full 39-round collision, and `U_{c,k} = union_{e in M_{c,k}} E_{c,e}`.
1. **Within-key mate Bonferroni (pointwise):** By Section 5.2 (`H7-mate-row19`), for every `e in M_{c,k}`, `sum_{e' != e} P(E_{c,e'} | E_{c,e}) <= eps_mate = 3,113,266 / 2^32`, hence:
   `P(U_{c,k} | H_{c,k}) >= (1 - eps_mate / 2) * sum_{e in M_{c,k}} P(E_{c,e} | H_{c,k})`.
2. **Across-key window Bonferroni (on kept cluster-size `N_k <= 3` events):** Dropping keys with equal-`G` co-hit count `N_k >= 4` lowers the first-order sum by at most `P(N_k >= 4) <= Q4_UB = 3.91e-4` (`H1-screen(iv)`). For distinct kept key events `(c, k) != (c', k')`:
   - Same claw `c = c'`, `G(k') != G(k)`: disjoint (`H_{c,k} cap H_{c,k'} = empty`), overlap `= 0`.
   - Same claw `c = c'`, `G(k') == G(k)`: bounding `P(U_{c,k'} | H_{c,k}, H_{c,k'}, U_{c,k}) <= 1` trivially (requiring **zero** independence assumption between equal-`G` co-hit tails), the unordered (`1/2`) pair deduction is at most `E[min(N_k, 3)] / 2 <= PI_BAR / 2 = 1.155e-3`.
   - Different claws `c != c'`: under `H5-w17-uniform` (`W[17]` hit prob `2^-32` independent across claws) and `H-cross-claw` (`P(U_{c',k'} | U_{c,k}) <= EPS_KEY = 2^-7`), the unordered (`1/2`) pair deduction is at most `(ESW1_UB * MU_D * EPS_KEY) / (2 * 2^32) = (896 * 3,198,000 * 2^-7) / 2^33 = 2.60607340e-3`.
3. **Exact deterministic cap-completion theorem (`D_stop = 0`, EXHAUSTIVE `2^32`, ZERO stop-position heuristic):**
   - On any claw `(cv, a0, a1, u)` with `r0 := (W17PUB - u - w2b) mod 2^32`, every Stage-2 survivor lane `(f, b, lane, d1, d2)` in `k4q` corresponds to a distinct pair `(y, g)` (`g in 0..47`) solving `(s0(y) - y) mod 2^32 == (r0 + kappa_g) mod 2^32` (since each family's 18-bit prefixes are distinct and `y[0..17] = (p + w2b) mod 2^18` is bijective in `p`). Exhaustive enumeration over ALL `2^32` values of `y` and ALL `2^32` values of `r0` (`max_s0_mult_fast.c`) proves unconditionally:
     - `max_{r in Z_{2^32}} |{y : (s0(y) - y) mod 2^32 == r}| = 14` (at `r = 0x2bfbfddc`),
     - `M_48 := max_{r0 in Z_{2^32}} sum_{g=0}^{47} |{y : (s0(y) - y) mod 2^32 == (r0 + kappa_g) mod 2^32}| = 107` (at `r0 = 0x2496e5f9`).
   - For any kept colliding claw `i` with equal-`G` co-hit count `N_k <= 3`, because every true `W[17]`-hitting key on claw `i` shares the single value `G(a2, kappa) == (u - W17PUB) mod 2^32`, there are **deterministically at most `1 + 3 = 4` true `W[17]`-hitting keys** on claw `i`. Counting every operation inside `k4_eval` (`r39joint_k8_both_c.py:542-625`) unconditionally (without even assuming `W9C` rejects any class):
     - `g11` cap (`2`) + survivor-free 52-block pass (`K4_PASS_WC = 48,364`) = `48,366` ops;
     - All `<= 107` Stage-2 survivors (`1` `jnz` + `2` `g13` + `134` extract/precomp + `<= 32` classes x `(2 g14 + 20 W9C + 563 kw) = 18,857` ops each): `107 x 18,857 = 2,017,699` ops;
     - All `<= 4` true `W[17]`-hitting keys (`<= 32` mates each x `(2 g15 + 560 kw + 2 x 2,812) = 197,952` ops each): `4 x 197,952 = 791,808` ops;
     - Maximum guard reserve `R <= 62,000` (`g15`) at any `cap(R)` call inside `k4_eval`: `62,000` ops;
     - **Total unconditional deterministic worst-case peak `m.o + R` increment inside `k4_eval`:** `48,366 + 2,017,699 + 791,808 + 62,000 = 2,919,873 < 3,000,000 =: B_CLAW`.
   - Define `M_pre(i)` as the running maximum of `m.o + R` over every `cap(R)` check strictly before `k4_eval(claw_i)` begins (taking `max(M_pre(i), m.o_before_g11)`), and let `W_SAFE := WMAX_CAP - B_CLAW = 437,000,000`. Note `M_pre(i)` is non-decreasing in `i` and depends **strictly** on `(cv, walk, stage2, claws 1..i-1)` — never on claw `i`'s `W[17]` hits or rounds `18..38` tail. On any sample path where at least one safe claw `{i : M_pre(i) <= W_SAFE}` contains a kept colliding key (`N_k <= 3`), let `i*` be the first such claw: every earlier claw `j < i*` completed with `s.success == False` and `M_pre(i*) <= 437,000,000 < WMAX_CAP`, so the capped window deterministically reaches `k4_eval(claw_{i*})` and completes it with peak `m.o + R <= 437,000,000 + 2,919,873 = 439,919,873 < WMAX_CAP`, outputting a valid collision with probability `1`. Thus restricting the first-order union strictly to `{i : M_pre(i) <= W_SAFE}` gives an exact pointwise set inclusion with **`D_stop = 0` identically** (no cap-boundary or stop-position assumption anywhere).
4. **Total divisor `DIV`:**
   - `D_mate  = 3,113,266 / 2^33 = 1,556,633 / 4,294,967,296 = 3.62431863e-4`
   - `D_cohit = 2.31e-3 / 2 + 3.91e-4 = 773 / 500,000 = 1.54600000e-3`
   - `D_cross = (896 * 3,198,000) / (256 * 2^32) = 1,399,125 / 536,870,912 = 2.60607340e-3`
   - `D_stop  = 0` (exact deterministic via `W_SAFE = WMAX_CAP - B_CLAW`)
   - **Exact rational `DIV = 302,963,319,369 / 67,108,864,000,000 = 0.004514505257741`** (costs only `0.006528` bits).
5. **Independent windows:** Each window draws an independent first block `M0`, so conditional on the declared heuristic bounds (`H1-screen`..`H-cross-claw`), `P(no collision in BW windows) <= exp(-BW * mu_w * (1 - DIV))`, where `mu_w = 944 * R_SAFE_LB * EN_LB * 2^-32 * 2^-74.446970`. This derivative prices the Bonferroni lower bounds `R_SAFE_LB = 0.95286309` (extended 8,192-window panel, Section 5.2a), `EN_LB = 4,414,590.97` (extended EN panel, Section 5.2b), and the extended-panel `p_tail = 2^-74.446970` (Section 5.3a). Setting `lam = (-ln(0.61) + 2^-40) / (1 - DIV)` and `BW = ceil(lam / mu_w)` yields algorithmic random-coin success probability at least `0.39` for the fixed target. (The 6-way Bonferroni simultaneous intervals summarize finite-sample empirical support for the heuristic constants and are distinct from algorithmic random-coin success probability.)

### 6.2 Exact integer cost ledger
| Term | Exact Value | Basis |
|---|---:|---|
| Active list (`Tuple 124`, all 48 groups) | `62,955,816` entries (`1,088` classes, `9,906,695` keys, `52` blocks) | EXHAUSTIVE |
| `WMAX_CAP` (per-window hard cap) | `440,000,000` ops (charged `WMAX_CAP + 6 = 440,000,006`) | Selected on preregistered 4,096-window selection half |
| `B_CLAW` / `W_SAFE = WMAX_CAP - B_CLAW` | `3,000,000` ops (`> 2,919,873` exact worst-case) / `437,000,000` | EXHAUSTIVE `2^32` (`M_48 = 107`) |
| `R_SAFE_LB` (safe `M_pre <= W_SAFE` fraction) | `0.95286309` (Bonf-6 LCB on the preregistered 8,192-window extended panel, Section 5.2a) | MEASURED (Bonf-6 99% FWER) |
| `EN_LB` (`F8`-entries per `F9` claw) | `4,414,590.97` (Bonf-6 LCB on the preregistered 16,384-claw extended panel, Section 5.2b) | MEASURED (Bonf-6 99% FWER) |
| `p_tail` (39-round tail prob per trial) | `2^-74.446970` (Bonf-6 class-01 LCB of the 30,720-seed extended panel, Section 5.3a) | MEASURED (Bonf-6) |
| `DIV` (second-order Bonferroni divisor, `D_stop = 0`) | `302,963,319,369 / 67,108,864,000,000` (`0.00451451`) | PROVED + Bonf-6 bounds |
| `lam` (`(-ln 0.61 + 2^-40) / (1 - DIV)`) | `0.496537944978964872` | DERIVED (exact) |
| `mu_w` (first-order collisions/window) | `3.526297624323162050e-23` (`2^-74.586191`) | DERIVED (exact) |
| **`BW`** (`ceil(lam / mu_w)` windows) | **`13,828,987,709,172,456,742,182`** (`2^73.576167`) | DERIVED (exact) |
| Window work `BW x 440,000,006` | `6,084,754,675,009,807,221,595,820,453,092` | DERIVED (exact) |
| Setup bound `K4_SETUP_PRICED` | `1,100,000,000` (`>= K4_SETUP = 1,084,328,364`) | PROVED / ASSERTED |
| Preprocessing `2,812 x 2^43` | `24,734,613,578,448,896` | CONSERVATIVE BOUND |
| **Total word ops `N_TOTAL`** | **`6,084,754,675,009,831,956,209,498,901,988`** | DERIVED (exact) |
| Raw `log2(N_TOTAL / 2,812)` | `90.805661065116510` | DERIVED (exact) |
| **Claimed `time_log2`** | **`90.805662`** (rounded UP at 6th decimal) | CLAIMED |
| **Claimed `memory_log2_bytes`** | **`20.0`** (`K4_MEM = 1,042,561 B <= 2^20`, headroom `6,015 B`) | CLAIMED |
| **Claimed `nonuniform_advice_log2_bytes`** | **`7.78135971352466`** (`220 B`) | CLAIMED |

---

## 7. Heuristic Register, Organizer Experiments, and Limitations

Every non-proved heuristic step is declared in `claim.json` with its exact scope, supporting evidence, extrapolation, and limitations:
1. **`H1-screen` (score-critical):** Under the screened two-choice law (`k4_scr(cv) <= 5`, `KCAP = 679`, 944-claw gate, `WMAX_CAP = 440,000,000`), at least `R_SAFE_LB = 0.95286309` of claws meet `M_pre <= W_SAFE = 437,000,000`; the implication from that guard to completion is exact because `437,000,000 + 2,919,873 < 440,000,000`. The retention bound comes from the disjoint 4,096-window pricing half of the preregistered 8,192-window panel (mean `0.954175`, Bonferroni-6 LCB `0.95286309`). The inherited EN, key-count, co-hit, and cross-claw premises remain declared in `claim.json`. *Limitation:* the finite panel supports but does not prove extrapolation to all windows.
2. **`H2-entries` (score-critical):** Conditioned on a `W[17] == W17PUB` hit of a valid `Tuple 124` entry in `F8 x F9 x F10 x F11` (class 01: `a0` even, `W[1]` odd), the full 39-round collision tail probability across rounds `18..38` is at least `p_tail = 2^-74.446970`, and the paired SMC estimator across independent seeds provides a calibrated empirical basis for this bound. *Evidence:* 28-seed contiguous paired ALL-48 SMC panel (`9,175,040` trials/arm, `1,246` verified 39-round collisions, pooled mean `2^-74.37763`, class-01 mean `2^-74.32531`, 6-way Bonferroni class-01 LCB `2^-74.71347`, 99.9% single-parameter class-01 LCB `2^-74.74164`, paired diff vs `PUB` `+0.01666` bits on bit-identical carriers; this derivative prices the Bonf-6 simultaneous class-01 LCB directly) plus organizer-executable `r39-mate-01..14`. *Limitations:* Participant SMC panel lacks cryptographic `holdout_nonce` pre-commitment and samples rounds `18..23` from the exact step-16/17 pinned state with random `W[8], W[9]` in `F8 x F9` and random recovered `cv` rather than real screened walk claws. Rounds `18..38` depend on `W[2..7]` (which enter `W[18..23]`), and `cv` enters `W[0..5]` nonlinearly; `k4_scr(cv) <= 5` removes `~7.5` bits from `192`-bit `cv[0..5]` while `(a0, a1, a2, a3)` randomize `W[2..7]`. Invariance of the tail under screening and claw selection, as well as SMC estimator calibration and non-selection, are therefore explicit heuristic premises of `H2-entries`.
3. **`H3-advice-construction` (score-critical):** With `(A[8..11], E[12..15], W[12..15])` fixed to `Tuple 124` (`T124_A, T124_E, T124_W`, fibre `FIB = 0x28b7f117`, `E11_BASE = 0x08226d10`, `K4_CUBE = 0xf74400ca`; `220 B` total nonuniform advice including the `160 B` ePrint 2026/1120 Table 23 SFS collision pair), every generated entry across all `48` `kappa` groups (`1,088` classes, `62,955,816` entries) satisfies `h4ok`, `W[9] = T124_C9 - a1`, single-`W[16]` claw factorization, and exact 16-step two-message reconvergence; and constructing/selecting the `220 B` advice costs at most `2^43` compressions (`preprocessing_log2 = 43`, charged directly in `N_TOTAL`: `93 x 2^36 + 93 x 14 x 2^24 = 2^42.545` compressions for the published 93-pair SFS campaign + `< 2^21` compressions for the offline `Tuple 124` `60 B` search, leaving `> 2^41.1` compressions of headroom). *Evidence:* `r39-transplant-claw` verifies the shipped SFS collision (`sfs_collision = 1`), the full `48`-group / `1,088`-class / `52`-block import construction (`K4_MEM = 1,042,561 B`), `48/48` group samples on `h4ok`, `W[9]`, `W[16]`, and exact 16-step two-message reconvergence, `48/48` planted `k4q` recoveries, and `255/255` seeded random checks; `r39-mate-01..14` directly executes live SMC SFS collision generation (`165` `T124` + `152` `PUB` verified 39-round SFS collisions at `< 2^17` compressions and `< 200 KiB` RAM); exhaustive DFA enumeration (`62,955,816` entries, `0` failures). *Limitations:* The 93-pair SFS campaign of ePrint 2026/1120 was run externally by the pair's authors rather than re-executed in the bounded container and is charged in full at its declared `2^42.545 <= 2^43` compression cost (`~2^-48.3` of total attack time `2^91.29`).
4. **`H5-w17-uniform` (score-critical):** Across screened F9 claws, the `W[17]` claw offset `(u, w2b)` makes each listed key hit `W[17] == W17PUB` with probability `2^-32`, independently of its `F8` membership, rounds `18..38` tail, and other claws' `W[17]` hits. *Evidence:* Algebraic decoupling of `W[17] = u + s0(a2 + w2b) - a2 - kappa` (Section 2.3), 48/48 planted-key recovery (`r39-transplant-claw`, `r39k4-window-small`), and 100-claw random survivor match (`46` observed vs `~45.5` expected). *Limitations:* `W[17]` hits are rare (`~2^-10` per claw), so independence from deep rounds `18..38` tails is heuristic rather than proved.
5. **`H7-mate-row19` (score-critical):** Conditioned on a colliding entry `(a2, a3)` of `Tuple 124`, its `W[3]` word is approximately uniform mod `2^32`, so the exhaustive `2^32` bad-set cardinality `max_{a3} sum_{b3!=a3} |B_{b3-a3}| = 3,113,266` bounds the within-key mate collision overlap by `eps_mate / 2 = 3,113,266 / 2^33`. *Evidence:* Exhaustive `2^32` enumeration over all `230` offsets (`0` zero-Delta hits), `W[3]` per-bit `chi^2(32) = 28.72` across `1,246` real hits, `0/972` `F8`-passing mates surviving row 19 in the 28-seed panel, and live mate tracing in `r39-mate-01..14`. *Limitations:* `W[3]` uniformity is tested on `1,246` SMC hits (`32` marginal bit tests), not proved cryptographically.
6. **`H-cross-claw` (score-critical):** Conditioned on a collision at one claw of a window, another claw's key hit on the same `cv` follows the rounds `18..19` trail (and hence collides) with probability at most `EPS_KEY = 2^-7`. *Evidence:* `0 / 79,744` `xa20` hits across `1,246` colliding `cv` clusters (`xa18/xu18 = 40,152 / 40,046`, random-`cv` `xu20 = 0 / 79,744`) in the 28-seed ALL-48 panel, plus organizer-executable `r39-mate-01..14` cross-claw checks across independently sampled groups. *Limitations:* Measured on clustered virtual other-claw trials (`_xd` pins `W[17]` by solving `w[1]` without parity restriction) on SMC-sampled `cv`s rather than real screened-window claw pairs; deeper rows `20..38` are covered by event inclusion.

### 7.1 Organizer experiments (`experiments/manifest.json` + `experiments/r39joint_k8_both_c.py`)
All 16 declared experiments use a single clean, plain-Python stdlib file `experiments/r39joint_k8_both_c.py` (`65,147 B <= 64 KiB` after LF normalization, SHA-256 `65331d35abac0ff6f1ef34b3961eae8b6d588278ebda1e8f56fcaf418aa333a1`, zero `zlib`/`base85` blobs), serving as bounded executable-consistency KATs on the organizer's fixed public seeds (not substituted for the full-scale statistical panels):
- `r39-transplant-claw` (256 trials): Verifies the 39-round SFS collision (`sfs_collision = 1`), all import invariants (`48` groups, `1,088` classes, `52` prefix blocks, `12,928` unique prefixes, bit-identical 12-group family prefix sets, `K4_MEM = 1,042,561 B`, `K4_PASS_WC = 48,364`), exact 16-step two-message reconvergence on all `48/48` group samples (`sample_valid = sample_w9_ok = sample_trail = 48`, `sample_w16_one = 1`), `48/48` planted `k4_w17a >= 1` hits through `k4q`, and `255/255` seeded random `(cv, a0, u)` transplant/claw checks.
- `r39k4-window-small` (trials 0..3): Runs the shipped `Attack` (`2^20` on trial 0, `2^19` on trials 1..3) with all 14 guard assertions active (`g8` interval 16, `g6 = 17,000`), verifying exact KAT tuples `(claws, f9, k4_lanes, k4_surv, k4_ops, ops)` = `(43, 0, 0, 0, 0, 7,504,146)` (`off_inv_ok = 1`, `screen_ok = 1`, `planted_48 = 48`), `(19, 1, 12,928, 2, 29,921, 5,241,877)` (`stamp_claws = 1`, `stamp_kept = 1`, `stamp_ok = 1` capped prefix replay), `(15, 0, 0, 0, 0, 7,331,645)`, and `(12, 0, 0, 0, 0, 3,873,639)` with `k4_setup = 1,084,328,364` and `k4_mem = 1,042,561`.
- `r39-mate-01..14` (14 organizer-seeded runs, `81,920` trials/arm/run = `1,146,880` trials/arm total): Runs a single shared SMC carrier (`NP = 100`, `1 x 40 x 2,048` trials/arm) comparing an exact DP-sampled group of `Tuple 124` (row 0, verifying every hit via full 39-round `compress`, tracing every reached `F8`-passing mate through row 19, and running 32 cross-claw virtual trials/hit from a fresh size-proportional group `gi2`) against the paired `PUB` control on the exact same SMC carrier (row 1). Across the 14 organizer seeds, reproducible KAT totals are **`165` verified full 39-round `Tuple 124` SFS collisions** vs **`152` `PUB` collisions** (identical `l2` on `14/14` runs), **`0 / 120` `F8`-passing mates past row 19** (`1,565` mates checked), and **`0 / 5,280` cross-claw `xa20` hits** (`xa18 = 2,655` vs `xu18 = 2,620`, `xu20 = 0`).

---

## 8. Attribution and Lineage

This construction builds on:
- The 39-round SHA-256 semi-free-start differential characteristic and published collision pair of ePrint 2026/1120 (Tables 21 and 23).
- Prior Yukon `hashsmash-pareto/sha256` 39-round submissions: `744875ec` (initial accepted 39-round baseline), `0b62ed88` and human-accepted `d3a46ae6` (folded bit-sliced walk, `k = 4` fibre shifting, `Mach` cost model, second-order Bonferroni collision bound, and `row19x` mate exclusion), and in-review improvements `9835235a`, `04f61e00`, `6bf0e9ea`, `0bb19cb2`, and `820db8f6` (944-claw dedupe gate, `cv` screening, per-window hard cap with `_stamp`, and `H-cross-claw`).

Our independent contributions are: (1) releasing `E[12..15]` via the `k = 8` transplant (`Tuple 124`, `FIB = 0x28b7f117`), expanding the exact valid entry set 5.01x to `62,955,816` entries across 48 `kappa` groups; (2) discovering and proving the exact 4-family 22/29-bit shared-prefix factorization (`52` total blocks, `29,952 B` prefix RAM, `22,090` avg ops/claw, `48,364` worst-case survivor-free pass, itemized `K4_MEM = 1,042,561 B` and 4-family chunked Phase-S peak `584,292 B`); (3) restoring unconditional deterministic guard bounds across all 14 guards (`g8` interval 16, `g6 = 17,000`) and proving exact `D_stop = 0` deterministic cap completion (`M_48 = 107`, `W_SAFE = 437,000,000`); and (4) backing every ledger input with 6-way Bonferroni simultaneous 99% FWER bounds across Discovery/Holdout, exhaustive `2^32`, `16,384`-`w`, and 28-seed paired ALL-48 measurements, and (5, this derivative) re-measuring the class-01 tail on a preregistered 30,720-seed extension, `p_tail = 2^-74.446970` (Section 5.3a).


# Two-choice stacked-source derivative

The shipped source selects between the home and adjacent table slots while
preserving exact point identification and the longer-trail replacement rule.
The preregistered 8,192-window panel selected cap 440,000,000 on its first 4,096
windows and priced the disjoint 4,096-window holdout at R=0.95286309.  Its exact
integer ledger is

`N = 13828987709172456742182 * (440000000 + 6) + 1,100,000,000 + 2,812 * 2^43`

`  = 6084754675009831956209498901988`,

so `log2(N/2812) = 90.805661065116510`, rounded upward to **90.805662**.  The
compact source is 65,147 bytes (SHA-256 `65331d35abac0ff6f1ef34b3961eae8b6d588278ebda1e8f56fcaf418aa333a1`), and the
table-inclusive memory peak is 1,042,561 bytes, below 2^20.
