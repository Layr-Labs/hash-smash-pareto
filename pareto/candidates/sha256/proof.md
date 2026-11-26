# Ordinary Collision Search for 41-Round SHA-256 (`sha256-r41-prefix-v1`)

## 1. Target Specification and Summary of Claim

This construction finds an **ordinary classical collision** for complete 41-round SHA-256 (`sha256-r41-prefix-v1`): two distinct byte-string messages $M \ne M'$ of bit length $< 2^{64}$ (specifically, 64-byte / 512-bit messages) whose complete 41-round SHA-256 digests agree on all 256 output bits under the standard FIPS 180-4 fixed IV, message schedule, big-endian length padding, and feed-forward, applying compression rounds `0..40` inclusive to every padded block.

| Quantity | Value |
| :--- | :--- |
| Target profile / rounds | `sha256-r41-prefix-v1` (`41` rounds, steps `0..40` inclusive) |
| Reference compression cost $C(41)$ | `2,980` 256-bit word-RAM operations (`collision-frontier-v5`) |
| Bit-sliced Walk-B kernel (`KLEN`) | `45,312` gates (`35,520` XOR, `5,888` AND, `3,904` OR; `0` NOT, `0` MOV, `0` mixed-polarity) |
| Register file (unified single bank) | `860` body data registers (`0..859`) + `24` disjoint controller/temp/link registers (`860..883`) = `884` registers (`28,288` B; $\le 1,024$, 10-bit indices; `OP_BODY` executes in-place on `regs[0..859]`) |
| Native bytecode image (emitted & executed) | `45,312` $\times$ `4` B body (`181,248` B) + `1,433` $\times$ `5` B 8x-unrolled controller (`7,165` B) + `1,238` $\times$ `5` B unrolled `RecProg` (`6,190` B) = `194,603` B |
| Stage-1 DP filter & 8x-unrolled loop | Bellman-optimal emitted cascade (`12` uncond + `3/8` inner-loop = `12.375` ops/batch; 3 levels `11, 14, 17` at debits `8, 12, 8`, unsigned-safe `R_WC == 0 -> halt_cap` cap `U + 40`) |
| Trail table | 47-bit bit-sliced table: `538` groups $\times$ `256` = `137,728` slots (`809,152` B; `R_TLIM = 137,728`, $t_{\max} = 137,472$) |
| Recovery | Two-Pass Dead-Table Checkpoint Recovery (`CK = 1`, $D = 2^{102}$, `7,402` $\le$ `12,643` checkpoints), emitted unrolled 2-lane SIMD `RecProg` (`1,238` exact VM ops + `22` Pass-1 / `110` Pass-2 driver ops; explicit $\le D$ lockstep cap) |
| Search-phase peak memory | `1,048,427` bytes ($\le 2^{20} = 1,048,576$ B; `149` B slack; `memory_log2_bytes = 20`, memory penalty `0`) |
| Setup-phase peak memory | $\le 620,000$ bytes ($\le 2^{20}$ B) |
| Preprocessing work (`preprocessing_log2`) | $\le 610{,}000{,}000$ word ops $= 204{,}697.98\dots$ compressions; $\log_2(610{,}000{,}000 / 2980) = 17.643137\dots \le \mathbf{17.64320}$ |
| Non-uniform advice (`nonuniform_advice_log2_bytes`) | `88` bytes (`22` 32-bit polarity-steering masks / `25` bit flips; $\lceil \log_2(88) \rceil = \mathbf{7}$) |
| Total charged work $N$ | `60,075,733,120,587,843,341,320,063,280,133,280,710,360` word operations |
| Exact $\log_2(N / 2980)$ | `123.922809529209...` |
| **Claimed `time_log2` / normalized score** | **`123.92281`** (conservative upward-rounded 5-decimal bound) |
| Certified random-function success bound $P_F$ | `>= 0.3900011539787848 >= 0.39` (exact 80-digit outward-rounded Lemma 2 proof) |

This is a generic distinguished-point birthday collision search under declared heuristic `H1-random-function-walk` and the `collision-frontier-v5` 256-bit word-RAM cost model. All body, outer-controller, and unrolled 2-lane SIMD recovery instructions are concretely emitted and executed in `experiments/sha256_r41_search.py` (`encode_body_4b`, `emit_controller_5b`, `emit_recprog_5b`, `run_vm`). No cryptanalytic weakness in 41-round SHA-256 is claimed, and no full-width 256-bit collision is produced.

---

## 2. Message Family and Walk-B Bijection

### 2.1 Two-Block 64-Byte Message Family with Constant Prefix `W[0..7]`
Every candidate message $M(Y)$ is 64 bytes (512 bits). Standard FIPS 180-4 padding appends a fixed 64-byte second block
$$B_2 = \texttt{0x80} \,\|\, \texttt{0x00}^{55} \,\|\, \operatorname{be64}(512).$$
Block 1 is $B_1(Y) = (W_0, \dots, W_7, W_8, \dots, W_{15})$, where:
- $W_0, \dots, W_7$ is the unique fixed 8-word constant prefix
  $$(\texttt{0x3e73281c}, \texttt{0x752d8ed2}, \texttt{0xad19eff1}, \texttt{0x7250fceb}, \texttt{0xd4095422}, \texttt{0x44fdb519}, \texttt{0x43f22c5b}, \texttt{0xd8d6aac4})$$
  which drives the SHA-256 working state after step 7 from the standard IV to
  $$(a_8, b_8, c_8, d_8, e_8, f_8, g_8, h_8) = (0, 0, 0, 0, 0, 0, -K_9, K_9 - K_8) \pmod{2^{32}},$$
  cancelling $K_8$ (via $h_8 + \operatorname{Ch}(0, 0, -K_9) + K_8 = 0$) and $K_9$ identically at steps 8 and 9 and eliminating all non-trivial gates for rounds `0..8`.
- $W_8 = Y_0$, $W_9 = Y_1$, and $W_{8+k} = (Y_k - K_{8+k}) \bmod 2^{32}$ for $k \in \{2, \dots, 7\}$, where $Y = (Y_0, \dots, Y_7) \in (\{0, 1\}^{32})^8$ is the 256-bit walk state. Because $Y \mapsto B_1(Y)$ is an affine bijection, $M(Y) = M(Y') \iff Y = Y'$.

Because $B_2$ is identical for every message in this family, equal block-1 chaining values $\text{cv}_1(Y) = \text{cv}_1(Y')$ imply equal 41-round digests $\text{SHA256}_{41}(M(Y)) = \text{SHA256}_{41}(M(Y'))$.

### 2.2 Invertible 6-Step Early-Stop Map (Walk B) with Polarity-Matched `Q`/`X` Shears
Let $S_{41}(Y) = (a_{41}, a_{40}, a_{39}, a_{38}, e_{41}, e_{40}, e_{39}, e_{38})$ be the working state after step 40. Instead of computing steps 35..40 in full, the bit-sliced kernel outputs the 8-word tuple
$$B(Y) = (e_{38},\; e_{39},\; a_{34},\; a_{35},\; Q_{35},\; T'_{1,36},\; X_{39},\; Y_{40}),$$
with $T'_{1,36} = (T_{1,36} - 1) \bmod 2^{32}$ (absorbing `delta = 1` into $e_{37} = a_{33} + T'_{1,36} + 1$ so $(K_{36} - 4) \bmod 2^{32}$ has 4 trailing zeros), fixed shear masks $Q_M = \texttt{0xcb88c133}$, $X_M = \texttt{0xbdd140fb}$, and zero constant offsets $x_{\text{cv}} = y_{\text{cv}} = 0$:
- $Q_{35} = T_{1,35} + \text{mj}_{35} \pmod{2^{32}}$, where $\operatorname{Maj}(a_{35}, a_{34}, a_{33}) = (a_{35} \land a_{34}) + ((a_{35} \oplus a_{34}) \land a_{33})$ and $\text{mj}_{35}$ replaces **only** the second term $((a_{35} \oplus a_{34}) \land a_{33})$ by its polarity-matched shear using mask $Q_M$: bit $j$ is $(a_{35} \oplus a_{34})_j \land a_{33,j}$ when $Q_{M,j} = 0$ and $\neg(a_{35} \oplus a_{34})_j \lor a_{33,j}$ when $Q_{M,j} = 1$, using the exact 1-bit identity $d \land c = d + (\neg d \lor c) - 1$.
- $X_{39} = e_{36} + u_{39} + \sigma_1(W_{37}) + W_{32} + \sigma_0(W_{24}) + W_{23} \pmod{2^{32}}$, where $u_{39}$ applies the polarity-matched OR-shear with mask $X_M$ to $(\neg e_{39}) \land e_{37}$ (replacing mismatched bits with $e_{39} \lor e_{37}$ via $(\neg e) \land c = (\neg e) + (e \lor c) - 1$) and directly consumes the already-live $W_{23}$.
- $Y_{40} = e_{37} + \sigma_1(W_{38}) + W_{33} + \sigma_0(W_{25}) + W_{24} \pmod{2^{32}}$, directly consuming the already-live $W_{24}$.

**Theorem (Walk-B Bijection).** $B(Y)$ determines $S_{41}(Y)$ uniquely via the explicit inverse `walk_b_inverse_to_digest`:
1. $a_{36} = Q_{35} + ((a_{35} \oplus a_{34}) \land Q_M) - Q_M + (a_{35} \land a_{34}) + \Sigma_0(a_{35}) \pmod{2^{32}}$.
2. $a_{37} = (T'_{1,36} + 1) + \Sigma_0(a_{36}) + \operatorname{Maj}(a_{36}, a_{35}, a_{34}) \pmod{2^{32}}$.
3. $T_{1,37} = e_{38} - a_{34}$, $a_{38} = T_{1,37} + \Sigma_0(a_{37}) + \operatorname{Maj}(a_{37}, a_{36}, a_{35})$.
4. $T_{1,38} = e_{39} - a_{35}$, $a_{39} = T_{1,38} + \Sigma_0(a_{38}) + \operatorname{Maj}(a_{38}, a_{37}, a_{36})$.
5. $T_{1,39} = X_{39} + ((\neg e_{39}) \land X_M) - X_M + \Sigma_1(e_{39}) + (e_{39} \land e_{38}) + K_{39}$, $e_{40} = a_{36} + T_{1,39}$, $a_{40} = T_{1,39} + \Sigma_0(a_{39}) + \operatorname{Maj}(a_{39}, a_{38}, a_{37})$.
6. $T_{1,40} = Y_{40} + \Sigma_1(e_{40}) + \operatorname{Ch}(e_{40}, e_{39}, e_{38}) + K_{40}$, $a_{41} = T_{1,40} + \Sigma_0(a_{40}) + \operatorname{Maj}(a_{40}, a_{39}, a_{38})$, $e_{41} = a_{37} + T_{1,40}$.

The walk function is $F(Y) = B(Y) \oplus \text{PD}$, where the fixed 256-bit output polarity mask of the bit-sliced kernel is
$$\text{PD} = (\texttt{0x37625d37}, \texttt{0x6934097d}, \texttt{0xcd067bd3}, \texttt{0xd6b0c558}, \texttt{0xcaaefcde}, \texttt{0x5adc3680}, \texttt{0x0996ea31}, \texttt{0xe5545220}).$$
Since $S_{41} \mapsto \text{cv}_1 = \text{IV} + S_{41}$ and $B \oplus \text{PD}$ are bijections, $F(Y) = F(Y') \implies \text{SHA256}_{41}(M(Y)) = \text{SHA256}_{41}(M(Y'))$.

---

## 3. Bit-Sliced Kernel Architecture (`45,312` Gates, `860` Data Registers, `0` Moves)

The kernel evaluates $F(Y)$ simultaneously on $m = 256$ independent trails by holding one bit plane per 256-bit register (rotations and shifts are zero-cost wire renamings). All `45,312` live instructions (`35,520` XOR, `5,888` AND, `3,904` OR) are pure `{XOR, AND, OR}` gates with zero `NOT` gates, zero mixed-polarity penalties, and zero register-to-register `MOV` instructions:
1. **3-Template 32/32 Polarity-Universal 276-Gate `add3`:** Using pair-carry encoding $\operatorname{val}(u, U) = 1$ if $U = 1$ else $2u$ with cyclic operand order `(B, C, A)`, three 9-gate column templates (`A`, `C`, `B`) cover all 32 polarity tuples $(p_x, p_y, p_z, p_u, p_U)$ with zero polarity mismatches (`5 + 8 + 28*9 + 8 + 3 = 276` gates for `cin in {0, 1, 2}`).
2. **Cross-Round `Maj` and `h + Ch` Algebraic Reuse:** $\operatorname{Maj}(a, b, c) = \operatorname{mux}(b \oplus c, a, b)$ reuses $a_{t-1} \oplus b_{t-1}$ with 100% CSE hit; 1-step associative XOR lookup rewrites $h_t \oplus \operatorname{Ch}_t = (h_t \oplus g_t) \oplus (e_t \land (f_t \oplus g_t))$, pruning $\operatorname{Ch}_t$'s outer XOR whenever $\operatorname{pol}(e_t) = \operatorname{pol}(f_t \oplus g_t)$.
3. **Zero-`NOT` De Morgan Half-Adders & Fused Bit-0/Bit-1 Adders:** Mixed-polarity half-adders use $a \land b = a \land \neg(a \oplus b)$ (`cin = 0`) and $a \lor b = b \lor (a \oplus b)$ (`cin = 1`) in 2 gates. Four-word sums fuse bit-0 carries into bit-1 pair-carry (`429` gates), `T1` fuses `add2_hch` with `add3` while absorbing `cu + 2*cu1 + c3 + delta` into `K[i]` and `W_split[i]` (including `delta = 1` on $T'_{1,36}$ for $K_{36} - 4 \equiv 0 \pmod{16}$), and 5-/6-word tail sums (`e38`, `e39`, `Y40`, `X39`) fuse stacked bit-0 carries into bit-1 pair-carry with Template A+B `Ch`-pruning.
4. **`ALL_ONES` Multi-Basin Polarity-Wave Steering (`25` XOR Flips; `22` 32-Bit Masks = `88` B Declared Advice):** Using the already-live `ALL_ONES` register (`r256 = 0xff...ff`, required for the stage-1 DP comparison), `25` targeted `XOR(w[b], ALL_ONES)` flips across `22` 32-bit `e` and `a` masks (`88` bytes, explicitly declared as `nonuniform_advice_log2_bytes = 7`) align downstream `Ch` and `pair_col` polarities without introducing any `NOT` gate or extra register, yielding **`45,312` gates**.
5. **Reverse-DAG (Dual) One-Shot Black Pebbling & Zero-Move Home-Register Borrowing:** Scheduling the pruned DAG backward from outputs to inputs by `(newly_opened_operands - 1, -idx)` (reversing to obtain a valid topological order) and borrowing dead home registers `0..255` whose target output is not yet born peaks at **`860` data registers** (`0..859`, with `r256 = ALL_ONES` preserved read-only), leaving disjoint controller/temp/link registers `860..883` (`884 <= 1,024`) completely untouched by `OP_BODY` and requiring **`0` output `MOV`s**. Every body instruction fits in a native **32-bit (4-byte)** record (`2` opcode bits + `3 x 10` register bits).

---

## 4. Concrete Native 5-Byte Word-RAM VM, Bytecode Image, Recovery, and Memory Budget

### 4.1 Declared Classical 256-Bit Word-RAM Machine & Native Bytecode (`run_vm`)
The machine executes 256-bit word-RAM operations (`ADD`, `SUB`, `XOR`, `AND`, `OR`, `SHL`, `SHR`, `SHRR`, `SHLR`, `ADDI`, `SUBI`, `MOV`, `SETI`, `LD`, `ST`, `CMP`, `BEQ`, `BNE`, `BLT`, `BGE`, `JMP`, `CALL`, `RET`, `BODY`, `HALT`) on a single unified `884`-register bank (`860` body data registers `0..859` + `24` disjoint controller/temp/link registers `860..883`; `28,288` B; `OP_BODY` executes in-place on `regs[0..859]` with zero shadow register bank). Body instructions use native 32-bit (4-byte) records (`2`-bit opcode + `3 x 10`-bit regs); outer-controller and unrolled-recovery instructions use native 40-bit (5-byte) records (`6`-bit opcode + `3 x 10`-bit regs/imm + `4`-bit aux). Every executed instruction in setup, main loop, cascade, Stage-2, DP handler, super-batch age check, and recovery is charged at 1 operation. The complete native image (`45,312` 4-byte body records + `1,433` 5-byte 8x-unrolled controller records + `1,238` 5-byte unrolled `RecProg` records, `code5_sha256: d13ff2cf...`) is emitted and executed directly on `run_vm` inside `experiments/sha256_r41_search.py:selftest()`, which verifies 8-batch unrolled execution, unsigned `halt_cap` triggering, `dp_restart_only` `start_batch` updates + `age_loop`, and Pass-2 lockstep `< D` cap termination.

### 4.2 8x-Unrolled Bellman-Optimal Stage-1 Cascade and Stage-2 Early-Exit DP Predicate
A lane is a distinguished point (DP) when the low $s_1 = 20$ bits of output word 0 (`e38 ^ PD_0`) are zero and the next $W = 102$ bits (bits `20..121` as an unsigned 102-bit integer) are strictly less than $T_p = 2,125 < 2^{12}$ (equivalently, planes `32..121` are all zero and bits `20..31` are $< 2,125$). Thus the exact DP probability is $p = T_p / 2^{122} = 1 / L$.
- **Unconditional stage-1 + 8x-unrolled inner loop (`12.375` exact VM ops/batch):** `batch_loop` unrolls `U = 8` consecutive batches (`B` divisible by `8`), each executing `OP_BODY`, ORing planes `0..10` (`10` ORs), `CMP R_M, RA` (`1` op), and `BNE cas_r` (`1` op), followed once every 8 batches by `SUBI R_BIN, 8; CMP R_BIN, RZ; BNE batch_loop` (`3` ops) = `12 + 3/8 = 12.375` ops/batch (Bellman-optimal $k_0 = 11$, verified by `run_vm`).
- **Conditional stage-1 cascade (`U + 40` capped):** Inline per-slot `cas_r` handles Level 1 ($j = 11$) in `8` exact VM ops (`3` ORs on planes `11..13`, unsigned-safe `CMP R_WC, RZ; BEQ halt_cap; SUBI R_WC, 1`, `CMP R_M, RA; BEQ bn_{r+1}`), and on a 14-bit hit sets `R_CAP = r`, calls shared `cas_lvl2`, and jumps to `bn_{r+1}` (`+4` ops -> Level 2 debit `12`, Level 3 debit `8`), bounding total cascade work by $U = \sum_{(j,d)} d \lceil B(P_j + 10^{-12}) \rceil$ with $P_j = 1 - (1 - 2^{-j})^{256}$.
- **Stage-2 early-exit check (`15 <= 16` ops on 20-bit hit; `<= 2,000` ops on 30-bit / 110-bit non-DP hit):** On a 20-bit hit (prob $P_{20}$, capped at $\lceil B(P_{20} + 10^{-12}) \rceil$), the emitted code checks `CMP R_S20, 0; BEQ halt_cap; SUBI R_S20, 1` (`3` ops), ORs planes `32..41` (`10` ops), and compares/branches (`2` ops) = `15 <= 16` ops. On a 30-bit hit (prob $P_{30}$, capped at $\lceil B(P_{30} + 10^{-12}) \rceil$), it checks `R_S30` (`3` ops), ORs planes `42..121` (`80` ops), and on a 110-bit hit spills planes `0..255` (`257` ops), locates the lane (`<= 1,536` ops), and compares the 12-bit window `20..31` against $T_p = 2,125$ (`115` ops), totaling `<= 1,993 <= 2,000` ops.

### 4.3 47-Bit Bit-Sliced Trail Table and Emitted Unrolled Two-Pass Checkpoint Recovery (`CK = 1`)
Completed trails are stored in an index-layout 47-bit bit-sliced table of `538` groups $\times$ `256` trails/group (`137,728` slots; `538 * 47 * 32 = 809,152` B; `R_TLIM = 137,728`), reserving 1 group (`256` slots, initial `R_NIDX = 256`) for in-flight trails so $t_{\max} = 137,472$. Each DP's 47-bit key is extracted from unconstrained output bits `122..168`. Starting states are deterministic bijections `start(idx) = SALT ^ idx`, where `SALT` is drawn uniformly at random from $\{0, 1\}^{256}$ using fresh algorithmic coins; packed `active_slot_id[0..255]` (`2,048` B), packed `start_batch[0..255]` (`4,096` B), the `48` `RecProg` constants (`1,536` B), scalars (`512` B), and the 8 KiB plane copy (`8,192` B) reside inside the exact `16,384` B work area (`512` 32-byte words). To enforce age cap $\kappa L$ ($\kappa = 40$) with zero per-inner-batch cost, the $B$ batches are partitioned into $\lceil B / 2^{103} \rceil = 130,595$ super-batches of $2^{103}$ batches each; once per super-batch, `age_loop` checks all 256 lanes (`130,595 * 1,931 + 3 = 252,178,948 <= 300,000,000` ops total, explicitly charged in $N$), and `dp_restart_only` updates the restarted lane's 128-bit `start_batch[R_L]` slot in `PW[128 + (R_L >> 1)]` to `PW[1] + (PW[0] - R_BIN) + R_CAP` (`18` ops/DP). On any DP hit, `key47 == 0^47` is skipped (`2` ops; probability $2^{-47} \approx 7.1 \times 10^{-15}$ on the winning collision, folded into $10^{-12}$), so zero-initialized empty/in-flight slots never match and **zero** per-group masking is needed. The emitted `scan_grp`/`scan_plane` loop executes `538 * (47 * 11 + 9) + 2 = 282,990` ops/DP, plus `<= 4,342` ops/DP for 47-plane insertion, `start_batch` update, and 256-plane lane restart (`<= 287,332 <= 305,000` ops/DP budgeted).

When a 47-bit key match occurs with a populated slot, the table memory (`809,152` B = `12,643` 64-byte slots) is repurposed as a checkpoint buffer with power-of-two stride $D = 2^{102}$, requiring $k_{\text{chk}} = \lceil c_r / 2^{102} \rceil = 7,402 \le 12,643$ checkpoints:
- **Emitted Unrolled 2-Lane SIMD `RecProg` (`1,238` exact VM ops/step, `6,190` B):** All 48 constants and working registers fit in `regs[0..859]`. Because the 2-lane packing places lanes at bits `0..31` and `128..159` with bits `64..102` identically zero in `SHR(x64, k)`, adding one unmasked rotation (`S1_f`, `s0_f`, `s1_u` in `W[16..22]`, `S0_u` in `a10..a12`) to clean 32-bit operands never carries across bit `127 -> 128`, eliminating `58` redundant `AND` ops; algebraic shear simplification (`mj_a ^ mj_o == ~d35`, `xa ^ xo == e39`) removes `4` more ops, yielding `1,237` arithmetic ops + `1` `RET` = `1,238` static 5-byte records (`6,190` B), verified `256/256` bit-for-bit on `run_vm` against both `exec_body_4b` and `sha256_r41`. Caching `0xFFFFF` in `R_K47` gives `<= 22` exact Pass-1 driver ops/step (`1,260` ops/step; measured `21.50` ops/step) and `<= 110` Pass-2 driver ops/step (`1,348` ops/step).
- **Two-Pass Checkpoint Search:** Pass 1 walks at most $c_r = \lceil 15.0 L \rceil + 100$ steps, checking the 122-bit DP predicate on each lane and packing/storing a 64-byte `(state_i, state_j)` checkpoint every $D = 2^{102}$ steps. Pass 2 sets `R_TLIM = (R_S30 - 1) >> 102`, binary-searches the $\le 7,403$ checkpoint intervals in $\le \lceil \log_2(7,403) \rceil = 13$ probes of $< D$ steps (with $q = (\Delta + kD) \gg 102$ and $r = (\Delta + kD) \land (D - 1)$), aligns in $< D$ steps, masks lane 0 (`wi &= 0xFFFFFFFF`) before packing lane 1 in `p2_pack2`, and steps both trails in lockstep for at most $D$ steps (explicitly guarded by `R_BIN = D` -> `halt_cap`) (`15` total segments of $\le D$ steps) to isolate distinct colliding predecessors ($M \ne M'$ with $\text{SHA256}_{41}(M) = \text{SHA256}_{41}(M')$), costing at most $c_r \cdot 1,260 + 15 D \cdot 1,348 + 80 k_{\text{chk}} + 10,000$ operations.

### 4.4 Memory Budget ($\le 2^{20} = 1,048,576$ Bytes)
| Region (Search Phase) | Bytes |
| :--- | ---: |
| Emitted bit-sliced body (`45,312` $\times$ `4` B) | `181,248` |
| Emitted unrolled 2-lane SIMD `RecProg` (`1,238` $\times$ `5` B) | `6,190` |
| Emitted 8x-unrolled zero-stub outer controller (`1,433` $\times$ `5` B) | `7,165` |
| Unified single register file (`884` $\times$ `32` B; `0..859` body, `860..883` controller) | `28,288` |
| Work area (`active_slot_id`, `start_batch`, `48` `RecProg` consts, 8 KiB plane copy) | `16,384` |
| 47-bit bit-sliced trail table (`538` $\times$ `1,504` B; `137,728` slots) | `809,152` |
| **Total Search-Phase Peak Memory** | **`1,048,427` B** (`149` B below `1,048,576` B) |

During setup, the emitter writes the `194,603`-byte native code image directly into the arena before the `809,152`-byte table is zeroed, keeping setup-phase peak memory below `620,000` bytes ($\le 2^{20}$ B). Thus `memory_log2_bytes = 20` and the normalized memory penalty $\max(0, 20 - 20) = 0$.

---

## 5. Exact Outward-Rounded Lemma 2 Success Bound ($P_F \ge 0.39$) and Cost Ledger

Under `H1-random-function-walk`, model $F : \{0, 1\}^{256} \to \{0, 1\}^{256}$ as a uniform random function ($S = 2^{256}$). With $m = 256$ parallel lanes, $B = 1,324,382,812,500,000 \times 10^{21}$ batches (divisible by `U = 8`), $T_p = 2,125$ ($L = 2^{122}/2125$), $\kappa = 40$, $K_{\text{rec}} = 15.0$, `slots = 137,728`, and $t_{\max} = 137,472$:

1. **Integrated Detection-Delay Collision Lower Bound:**
   $$I(B) = \frac{(m B)^2}{2 S} - \frac{m^2 B L}{S} + \frac{m^2 L^2}{S}(1 - e^{-B/L}) > \frac{(m B)^2}{2 S} - \frac{m^2 B L}{S} = I_{\text{lo}}.$$
   Outward-rounded 80-digit arithmetic (`compute_certified_ledger` in `experiments/sha256_r41_search.py`) certifies $P_{\text{base}} \ge 1 - \exp_{\text{up}}(-I_{\text{lo}})$.
2. **Union-Bound Failure Upper Bounds:**
   - Table overflow ($> t_{\max} = 137,472$ completed trails in $m B$ steps; Chernoff): $P_{\text{ovf}} \le 6.684 \times 10^{-7}$.
   - Recovery cap ($> c_r = \lceil 15.0 L \rceil + 100$ Pass-1 steps for $\max(X_1, X_2) + Z \le X_1 + X_2 + Z$; Gamma(3) tail $(1 + K_{\text{rec}} + K_{\text{rec}}^2/2)e^{-K_{\text{rec}}}$): $P_{\text{rec}} \le 3.931 \times 10^{-5}$.
   - 47-bit key collision among $\le t_{\max}$ stored trails: $P_{\text{key}} \le \binom{t_{\max}}{2} / 2^{47} \le 6.715 \times 10^{-5}$.
   - Self-cycle before DP across all $\le 137,728$ trails (including 256 in-flight): $P_{\text{self}} \le 137,728 \cdot L^2 / S \le 7.447 \times 10^{-6}$.
   - Age cap ($\kappa = 40$, union-bounded across all $137,728$ trails and the colliding pair): $P_{\text{age}} \le (137,728 + 2(1 + 40)) e^{-40} \le 5.855 \times 10^{-13}$.
   - Cascade counter $U$, stage-2 caps (`P_{20}`, `P_{30}`), skipped `0^47` key ($2^{-47}$), duplicate start: $\le 10^{-12}$.
   - Total failure upper bound: $P_{\text{fail}} \le 1.145638 \times 10^{-4}$.
3. **Certified Lower Bound:**
   $$P_F \ge P_{\text{base,lo}} - P_{\text{fail,hi}} \ge 0.3900011539787848 \ge 0.39.$$

### Complete Total-Cost Ledger
| Component | Charged Word Operations |
| :--- | ---: |
| Main loop unconditional (`U = 8`): $(B / 8) \cdot (8 \cdot (45,312 + 12) + 3)$ | `60,026,823,237,304,687,500,000,000,000,000,000,000,000` |
| Bellman-optimal cascade conditional (`U + 40`; exact VM debits `8, 12, 8`) | `1,512,310,746,612,686,404,912,493,321,819,116,808` |
| Stage-2 (`16` + `2,000` ops) + DP handler (`305,000` ops/DP) + super-batch age checks (`3e8`) | `5,804,258,895,688,666,321,115,218,000,054,512` |
| Two-Pass Checkpoint Recovery (`CK = 1`, `1,260` P1 / `1,348` P2 ops/step, $D = 2^{102}$, `7,402` checkpoints) | `47,391,768,277,647,466,248,829,671,592,851,539,040` |
| Setup, emitter & initialization (upper bound) | `610,000,000` |
| **Total Charged Word Operations $N$** | **`60,075,733,120,587,843,341,320,063,280,133,280,710,360`** |
| Normalized target compressions $T = N / 2980$ | $\log_2(N / 2980) = 123.922809529209\dots \le \mathbf{123.92281}$ |

---

## 6. Declared Heuristic, Scope, Extrapolation, and Limitations

1. **`H1-random-function-walk` (score-critical):** Assumes the iterated Walk-B transition $F(Y) = B(Y) \oplus \text{PD}$ over 41-round SHA-256 behaves like a uniform random function on $\{0, 1\}^{256}$ with respect to birthday collision hazard, DP hitting-time distribution ($p = 2125 / 2^{122}$), stage-1/stage-2 prefix uniformity, trail-length tails, and 47-bit key independence.
   - *Supporting evidence:* `proof:1-146`, `experiment:sha256-r41-walkb-bounded-w16-v1` (bounded merging DP collision walk embedded on the low 16 bits of the 2-block `W[0..7]`-prefix digest map with strict total budget `max_evals = 285` covering both Pass-1 search and Pass-2 recovery, `dp_bits = 2`, plus deterministic `selftest()` emitting and executing the complete 4-byte + 5-byte native bytecode image on `run_vm`, verifying 256/256 single-step equivalence of both body and unrolled `RecProg` at exact `1,238` ops/step, verifying 8-batch unrolled outer-controller execution, unsigned `halt_cap`, `dp_restart_only` `start_batch` update + `age_loop`, Pass-2 `< D` lockstep cap, and a direct 64-trial `w=12, budget=64` iterated Walk-B $F(Y)$ birthday check on `run_vm`), and `experiment:sha256-r41-walkb-projection-w14-v1` (fixed-budget $M = 127$ collision frequency on the low 14 bits of the 2-block `W[0..7]`-prefix digest map directly testing the $P \approx 0.39$ birthday curve; note `python-message-pairs-v1` verifies digest-prefix collisions on complete 41-round SHA-256, so the two message-pair experiments iterate the 2-block digest while `selftest()` tests iterated Walk-B $F(Y)$ directly).
   - *Limitations:* Reduced-width experiments ($w \in \{12, 14, 16\}$) cannot prove the absence of subtle structural correlations or non-random cycle behavior in $F(Y)$ at full 256-bit width. If 41-round SHA-256 exhibited abnormally short cycles or non-uniform DP clustering under $F$, the true success probability could drop below 0.39.
