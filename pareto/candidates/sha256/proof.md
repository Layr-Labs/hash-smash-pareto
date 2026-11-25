# Ordinary Collision Search for 40-Round SHA-256 (`sha256-r40-prefix-v1`)

## 1. Target Specification and Summary of Claim

This construction finds an **ordinary classical collision** for complete 40-round SHA-256 (`sha256-r40-prefix-v1`): two distinct byte-string messages $M \ne M'$ of bit length $< 2^{64}$ (specifically, 64-byte / 512-bit messages) whose complete 40-round SHA-256 digests agree on all 256 output bits under the standard FIPS 180-4 fixed IV, message schedule, big-endian length padding, and feed-forward, applying compression rounds `0..39` inclusive to every padded block.

| Quantity | Value |
| :--- | :--- |
| Target profile / rounds | `sha256-r40-prefix-v1` (`40` rounds, steps `0..39` inclusive) |
| Reference compression cost $C(40)$ | `2,896` 256-bit word-RAM operations (`collision-frontier-v5`) |
| Bit-sliced Walk-B kernel (`KLEN`) | `43,548` gates (`34,123` XOR, `5,689` AND, `3,736` OR; `0` NOT, `0` MOV, `0` mixed-polarity) |
| Register file | `860` data registers + `3` pointer/link registers = `863` registers (`27,616` B; $\le 1,024$, 10-bit indices) |
| Native bytecode image (emitted & executed) | `43,548` $\times$ `4` B body (`174,192` B) + `1,333` $\times$ `5` B zero-stub controller (`6,665` B) + `1,250` $\times$ `5` B unrolled `RecProg` (`6,250` B) = `187,107` B |
| Stage-1 DP filter & outer loop | Emitted weighted cascade (`11` uncond + `3` inner-loop = `14` ops/batch; conditional cap `U + 30`) |
| Trail table | 47-bit bit-sliced table: `543` groups $\times$ `256` = `139,008` slots (`816,672` B; $t_{\max} = 138,752$) |
| Recovery | Two-Pass Dead-Table Checkpoint Recovery (`CK = 1`, $D = 2^{102}$, `7,333` $\le$ `12,760` checkpoints), emitted unrolled 2-lane SIMD `RecProg` (`1,250` exact VM ops + `100` driver ops = `1,350` ops/step) |
| Search-phase peak memory | `1,047,779` bytes ($\le 2^{20} = 1,048,576$ B; `797` B slack; `memory_log2_bytes = 20`, memory penalty `0`) |
| Setup-phase peak memory | $\le 620,000$ bytes ($\le 2^{20}$ B) |
| Preprocessing work (`preprocessing_log2`) | $\le 610{,}000{,}000$ word ops $= 210{,}635.35\dots$ compressions; $\log_2(610{,}000{,}000 / 2896) = 17.684388\dots \le \mathbf{17.68440}$ |
| Non-uniform advice (`nonuniform_advice_log2_bytes`) | `0` bytes |
| Total charged work $N$ | `57,744,738,186,179,891,490,220,610,799,571,408,468,010` word operations |
| Exact $\log_2(N / 2896)$ | `123.906967399727...` |
| **Claimed `time_log2` / normalized score** | **`123.90700`** (conservative upward-rounded bound with `> 3.2e-5` bit margin) |
| Certified random-function success bound $P_F$ | `>= 0.3900010000000003 >= 0.39` (exact 80-digit outward-rounded Lemma 2 proof) |

This is a generic distinguished-point birthday collision search under declared heuristic `H1-random-function-walk` and the `collision-frontier-v5` 256-bit word-RAM cost model. All body, outer-controller, and unrolled 2-lane SIMD recovery instructions are concretely emitted and executed in `experiments/sha256_r40_search.py` (`encode_body_4b`, `emit_controller_5b`, `emit_recprog_5b`, `run_vm`). No cryptanalytic weakness in 40-round SHA-256 is claimed, and no full-width 256-bit collision is produced.

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

Because $B_2$ is identical for every message in this family, equal block-1 chaining values $\text{cv}_1(Y) = \text{cv}_1(Y')$ imply equal 40-round digests $\text{SHA256}_{40}(M(Y)) = \text{SHA256}_{40}(M(Y'))$.

### 2.2 Invertible 6-Step Early-Stop Map (Walk B) with Polarity-Matched `Q`/`X` Shears
Let $S_{40}(Y) = (a_{40}, a_{39}, a_{38}, a_{37}, e_{40}, e_{39}, e_{38}, e_{37})$ be the working state after step 39. Instead of computing steps 34..39 in full, the bit-sliced kernel outputs the 8-word tuple
$$B(Y) = (e_{37},\; e_{38},\; a_{33},\; a_{34},\; Q_{34},\; T_{1,35},\; X_{38},\; Y_{39}),$$
with fixed shear masks $Q_M = \texttt{0xb40e844b}$, $X_M = \texttt{0x1b3b3f81}$, and zero constant offsets $x_{\text{cv}} = y_{\text{cv}} = 0$:
- $Q_{34} = T_{1,34} + \text{mj}_{34} \pmod{2^{32}}$, where $\operatorname{Maj}(a_{34}, a_{33}, a_{32}) = (a_{34} \land a_{33}) + ((a_{34} \oplus a_{33}) \land a_{32})$ and $\text{mj}_{34}$ replaces **only** the second term $((a_{34} \oplus a_{33}) \land a_{32})$ by its polarity-matched shear using mask $Q_M$: bit $j$ is $(a_{34} \oplus a_{33})_j \land a_{32,j}$ when $Q_{M,j} = 0$ and $\neg(a_{34} \oplus a_{33})_j \lor a_{32,j}$ when $Q_{M,j} = 1$, using the exact 1-bit identity $d \land c = d + (\neg d \lor c) - 1$.
- $X_{38} = e_{35} + u_{38} + \sigma_1(W_{36}) + W_{31} + \sigma_0(W_{23}) + W_{22} \pmod{2^{32}}$, where $u_{38}$ applies the polarity-matched OR-shear with mask $X_M$ to $(\neg e_{38}) \land e_{36}$ (replacing mismatched bits with $e_{38} \lor e_{36}$ via $(\neg e) \land c = (\neg e) + (e \lor c) - 1$) and directly consumes the already-live $W_{22}$.
- $Y_{39} = e_{36} + \sigma_1(W_{37}) + W_{32} + \sigma_0(W_{24}) + W_{23} \pmod{2^{32}}$, directly consuming the already-live $W_{23}$.

**Theorem (Walk-B Bijection).** $B(Y)$ determines $S_{40}(Y)$ uniquely via the explicit inverse `walk_b_inverse_to_digest`:
1. $a_{35} = Q_{34} + ((a_{34} \oplus a_{33}) \land Q_M) - Q_M + (a_{34} \land a_{33}) + \Sigma_0(a_{34}) \pmod{2^{32}}$.
2. $a_{36} = T_{1,35} + \Sigma_0(a_{35}) + \operatorname{Maj}(a_{35}, a_{34}, a_{33}) \pmod{2^{32}}$.
3. $T_{1,36} = e_{37} - a_{33}$, $a_{37} = T_{1,36} + \Sigma_0(a_{36}) + \operatorname{Maj}(a_{36}, a_{35}, a_{34})$.
4. $T_{1,37} = e_{38} - a_{34}$, $a_{38} = T_{1,37} + \Sigma_0(a_{37}) + \operatorname{Maj}(a_{37}, a_{36}, a_{35})$.
5. $T_{1,38} = X_{38} + ((\neg e_{38}) \land X_M) - X_M + \Sigma_1(e_{38}) + (e_{38} \land e_{37}) + K_{38}$, $e_{39} = a_{35} + T_{1,38}$, $a_{39} = T_{1,38} + \Sigma_0(a_{38}) + \operatorname{Maj}(a_{38}, a_{37}, a_{36})$.
6. $T_{1,39} = Y_{39} + \Sigma_1(e_{39}) + \operatorname{Ch}(e_{39}, e_{38}, e_{37}) + K_{39}$, $a_{40} = T_{1,39} + \Sigma_0(a_{39}) + \operatorname{Maj}(a_{39}, a_{38}, a_{37})$, $e_{40} = a_{36} + T_{1,39}$.

The walk function is $F(Y) = B(Y) \oplus \text{PD}$, where the fixed 256-bit output polarity mask of the bit-sliced kernel is
$$\text{PD} = (\texttt{0x2b1ab639}, \texttt{0x41623d38}, \texttt{0xd03e7fb8}, \texttt{0xcf067bd3}, \texttt{0x84800fd9}, \texttt{0xfa707d26}, \texttt{0x47cac528}, \texttt{0xde7c33b8}).$$
Since $S_{40} \mapsto \text{cv}_1 = \text{IV} + S_{40}$ and $B \oplus \text{PD}$ are bijections, $F(Y) = F(Y') \implies \text{SHA256}_{40}(M(Y)) = \text{SHA256}_{40}(M(Y'))$.

---

## 3. Bit-Sliced Kernel Architecture (`43,548` Gates, `860` Data Registers, `0` Moves)

The kernel evaluates $F(Y)$ simultaneously on $m = 256$ independent trails by holding one bit plane per 256-bit register (rotations and shifts are zero-cost wire renamings). All `43,548` live instructions (`34,123` XOR, `5,689` AND, `3,736` OR) are pure `{XOR, AND, OR}` gates with zero `NOT` gates, zero mixed-polarity penalties, and zero register-to-register `MOV` instructions:
1. **3-Template 32/32 Polarity-Universal 276-Gate `add3`:** Using pair-carry encoding $\operatorname{val}(u, U) = 1$ if $U = 1$ else $2u$, three 9-gate column templates (`A`, `C`, `B`) cover all 32 polarity tuples $(p_x, p_y, p_z, p_u, p_U)$ with zero polarity mismatches (`5 + 8 + 28*9 + 8 + 3 = 276` gates for `cin in {0, 1, 2}`).
2. **Cross-Round `Maj` and `h + Ch` Algebraic Reuse:** $\operatorname{Maj}(a, b, c) = \operatorname{mux}(b \oplus c, a, b)$ reuses $a_{t-1} \oplus b_{t-1}$ with 100% CSE hit; 1-step associative XOR lookup rewrites $h_t \oplus \operatorname{Ch}_t = (h_t \oplus g_t) \oplus (e_t \land (f_t \oplus g_t))$, pruning $\operatorname{Ch}_t$'s outer XOR whenever $\operatorname{pol}(e_t) = \operatorname{pol}(f_t \oplus g_t)$.
3. **Zero-`NOT` De Morgan Half-Adders & Fused Bit-0/Bit-1 Adders:** Mixed-polarity half-adders use $a \land b = a \land \neg(a \oplus b)$ (`cin = 0`) and $a \lor b = b \lor (a \oplus b)$ (`cin = 1`) in 2 gates. Four-word sums fuse bit-0 carries into bit-1 pair-carry (`429` gates), `T1` fuses `add2_hch` with `add3` while absorbing `cu + 2*cu1 + c3 + delta` into `K[i]` and `W_split[i]`, and 5-/6-word tail sums (`e37`, `e38`, `Y39`, `X38`) fuse stacked bit-0 carries into bit-1 pair-carry with Template A+B `Ch`-pruning.
4. **`ALL_ONES` Multi-Basin Polarity-Wave Steering (`22` XOR Flips):** Using the already-live `ALL_ONES` register (`r256 = 0xff...ff`, required for the stage-1 DP comparison), `22` targeted `XOR(w[b], ALL_ONES)` flips across `e`, `a`, and `s1` wires align downstream `Ch` and `pair_col` polarities without introducing any `NOT` gate or extra register, reducing the kernel from `43,616` to **`43,548` gates**.
5. **Reverse-DAG (Dual) One-Shot Black Pebbling & Zero-Move Home-Register Borrowing:** Scheduling the pruned DAG backward from outputs to inputs by `(newly_opened_operands - 1, -idx)` (reversing to obtain a valid topological order) and borrowing dead home registers `0..255` whose target output is not yet born peaks at **`860` data registers** (`+3` pointer/link registers = `863 <= 1,024`), with **`0` output `MOV`s**. Every body instruction fits in a native **32-bit (4-byte)** record (`2` opcode bits + `3 x 10` register bits).

---

## 4. Concrete Native 5-Byte Word-RAM VM, Bytecode Image, Recovery, and Memory Budget

### 4.1 Declared Classical 256-Bit Word-RAM Machine & Native Bytecode (`run_vm`)
The machine executes 256-bit word-RAM operations (`ADD`, `SUB`, `XOR`, `AND`, `OR`, `SHL`, `SHR`, `SHRR`, `ADDI`, `SUBI`, `MOV`, `SETI`, `LD`, `ST`, `CMP`, `BEQ`, `BNE`, `BLT`, `BGE`, `JMP`, `CALL`, `RET`, `BODY`, `HALT`) on `863` 256-bit registers (`860` data + `3` pointer/link registers; `27,616` B). Body instructions use native 32-bit (4-byte) records (`2`-bit opcode + `3 x 10`-bit regs); outer-controller and unrolled-recovery instructions use native 40-bit (5-byte) records (`6`-bit opcode + `3 x 10`-bit regs/imm + `4`-bit aux). Every executed instruction in setup, main loop, cascade, Stage-2, DP handler, super-batch age check, and recovery is charged at 1 operation. The complete native image (`43,548` 4-byte body records + `1,333` 5-byte zero-stub controller records + `1,250` 5-byte unrolled `RecProg` records, SHA-256 `a49fcfb7...`) is emitted and executed directly on `run_vm` inside `experiments/sha256_r40_search.py:selftest()`.

### 4.2 Emitted Stage-1 Weighted Cascade and Stage-2 Early-Exit DP Predicate
A lane is a distinguished point (DP) when the low $s_1 = 20$ bits of output word 0 (`e37 ^ PD_0`) are zero and the next $W = 102$ bits (bits `20..121` as an unsigned 102-bit integer) are strictly less than $T_p = 2,145 < 2^{12}$ (equivalently, planes `32..121` are all zero and bits `20..31` are $< 2,145$). Thus the exact DP probability is $p = T_p / 2^{122} = 1 / L$.
- **Unconditional stage-1 + inner loop (`14` exact VM ops/batch):** OR planes `0..9` (`9` ORs), `CMP` with `ALL_ONES` (`1` op), `BNE cascade` (`1` op), `SUBI b_in, 1` (`1` op), `CMP b_in, 0` (`1` op), `BNE batch_loop` (`1` op) = **`14` ops/batch** (verified by `run_vm` multi-batch execution).
- **Conditional stage-1 cascade (`U + 30` capped):** Emitted levels $j \in \{10, 12, 14, 16, 18\}$ execute exact VM instruction counts $d_j \in \{7, 5, 5, 5, 7\}$, debiting from a single weighted counter $w$ initialized to $U = \sum_j d_j \lceil B(P_j + 10^{-12}) \rceil$, where $P_j = 1 - (1 - 2^{-j})^{256}$.
- **Stage-2 early-exit check (`15 <= 16` ops on 20-bit hit; `<= 400` ops on 30-bit hit):** On a 20-bit hit (prob $P_{20}$, capped at $\lceil B(P_{20} + 10^{-12}) \rceil$), the emitted code decrements/checks `s20_cap` (`3` ops), ORs planes `32..41` (`10` ops), and compares/branches (`2` ops) = `15 <= 16` ops. Only on a 30-bit hit (prob $P_{30}$, capped at $\lceil B(P_{30} + 10^{-12}) \rceil$) does it check the remaining 80 planes `42..121`, spill planes `0..255` on a 110-bit hit, and compare the 12-bit window `20..31` against $T_p = 2,145$ (`<= 400` ops).

### 4.3 47-Bit Bit-Sliced Trail Table and Emitted Unrolled Two-Pass Checkpoint Recovery (`CK = 1`)
Completed trails are stored in an index-layout 47-bit bit-sliced table of `543` groups $\times$ `256` trails/group (`139,008` slots; `543 * 47 * 32 = 816,672` B), reserving 1 group (`256` slots) for in-flight trails so $t_{\max} = 138,752$. Each DP's 47-bit key is extracted from unconstrained output bits `122..168`. Starting states are deterministic bijections `start(idx) = SALT ^ idx`, with packed `active_slot_id[0..255]` (`2,048` B), packed `start_batch[0..255]` (`4,096` B), the `47` `RecProg` constants (`1,536` B), scalars (`512` B), and the 8 KiB plane copy (`8,192` B) stored inside the exact `16,384` B work area (`512` 32-byte words). To enforce age cap $\kappa L$ ($\kappa = 40$) with zero per-inner-batch cost, the $B$ batches are partitioned into $\lceil B / 2^{103} \rceil \le 131{,}000$ super-batches of $2^{103}$ batches each; once per super-batch, the emitted `age_loop` checks all 256 lanes (`<= 200,000,000` ops total, explicitly charged in $N$). On any DP hit, `key47 == 0^47` is skipped (`2` ops; probability $2^{-47} \approx 7.1 \times 10^{-15}$ on the winning collision, folded into $10^{-12}$), so zero-initialized empty/in-flight slots never match and **zero** per-group masking is needed. The emitted `scan_grp`/`scan_plane` loop executes `543 * (47 * 11 + 8) = 285,075 <= 300,000` ops/DP, plus `<= 5,000` ops/DP for concrete bit-sliced 47-plane table insertion (`ins_plane`) and 256-plane lane restart (`rst_plane` + `256 LD`) (`305,000` ops/DP total).

When a 47-bit key match occurs with a populated slot, the table memory (`816,672` B = `12,760` 64-byte slots) is repurposed as a checkpoint buffer with power-of-two stride $D = 2^{102}$, requiring $k_{\text{chk}} = \lceil c_r / 2^{102} \rceil = 7,333 \le 12,760$ checkpoints:
- **Emitted Unrolled 2-Lane SIMD `RecProg` (`1,250` exact VM ops/step, `6,250` B):** Because all 47 constants and all working registers fit inside `regs[0..859]`, `emit_recprog_5b` emits the entire 2-lane SIMD Walk-B step unrolled (`1,249` arithmetic instructions + `1` `RET` = `1,250` static 5-byte records = `6,250` B) with **zero** `LD`/`ST` array indexing and **zero** rolled-loop overhead. Verified `256/256` bit-for-bit on `run_vm` against both `exec_body_4b` and `sha256_r40` at exact `1,250` ops/step; adding the Pass-1/Pass-2 driver loop/DP/checkpoint ops (`<= 100` ops/step) gives `1,350` ops/step.
- **Two-Pass Checkpoint Search:** Pass 1 walks at most $c_r = \lceil 15.0 L \rceil + 100$ steps, checking the 122-bit DP predicate on each lane and packing/storing a 64-byte `(state_i, state_j)` checkpoint every $D = 2^{102}$ steps. Pass 2 binary-searches the $\le 7,334$ checkpoint intervals in $\le \lceil \log_2(7,334) \rceil = 13$ probes of $< D$ steps (with $q = (\Delta + kD) \gg 102$ and $r = (\Delta + kD) \land (D - 1)$), aligns in $< D$ steps, and steps both trails in lockstep for $< D$ steps (`15` total segments of $< D$ steps) to isolate distinct colliding predecessors ($M \ne M'$ with $\text{SHA256}_{40}(M) = \text{SHA256}_{40}(M')$), costing at most $(c_r + 15 D) \cdot 1,350 + 80 k_{\text{chk}} + 10,000$ operations.

### 4.4 Memory Budget ($\le 2^{20} = 1,048,576$ Bytes)
| Region (Search Phase) | Bytes |
| :--- | ---: |
| Emitted bit-sliced body (`43,548` $\times$ `4` B) | `174,192` |
| Emitted unrolled 2-lane SIMD `RecProg` (`1,250` $\times$ `5` B) | `6,250` |
| Emitted zero-stub outer controller (`1,333` $\times$ `5` B) | `6,665` |
| Register file (`863` $\times$ `32` B) | `27,616` |
| Work area (`active_slot_id`, `start_batch`, `47` `RecProg` consts, 8 KiB plane copy) | `16,384` |
| 47-bit bit-sliced trail table (`543` $\times$ `1,504` B; `139,008` slots) | `816,672` |
| **Total Search-Phase Peak Memory** | **`1,047,779` B** (`797` B below `1,048,576` B) |

During setup, the emitter writes the `187,107`-byte native code image directly into the arena before the `816,672`-byte table is zeroed, keeping setup-phase peak memory below `620,000` bytes ($\le 2^{20}$ B). Thus `memory_log2_bytes = 20` and the normalized memory penalty $\max(0, 20 - 20) = 0$.

---

## 5. Exact Outward-Rounded Lemma 2 Success Bound ($P_F \ge 0.39$) and Cost Ledger

Under `H1-random-function-walk`, model $F : \{0, 1\}^{256} \to \{0, 1\}^{256}$ as a uniform random function ($S = 2^{256}$). With $m = 256$ parallel lanes, $B = 1,324,361,721,116,573 \times 10^{21}$ batches, $T_p = 2,145$ ($L = 2^{122}/2145$), $\kappa = 40$, $K_{\text{rec}} = 15.0$, and $t_{\max} = 138,752$:

1. **Integrated Detection-Delay Collision Lower Bound:**
   $$I(B) = \frac{(m B)^2}{2 S} - \frac{m^2 B L}{S} + \frac{m^2 L^2}{S}(1 - e^{-B/L}) > \frac{(m B)^2}{2 S} - \frac{m^2 B L}{S} = I_{\text{lo}}.$$
   Outward-rounded 80-digit arithmetic (`compute_certified_ledger` in `experiments/sha256_r40_search.py`) certifies $P_{\text{base}} \ge 1 - \exp_{\text{up}}(-I_{\text{lo}})$.
2. **Union-Bound Failure Upper Bounds:**
   - Table overflow ($> t_{\max}$ completed trails in $m B$ steps; Chernoff): $P_{\text{ovf}} \le 6.914 \times 10^{-7}$.
   - Recovery cap ($> c_r = \lceil 15.0 L \rceil + 100$ Pass-1 steps for $\max(X_1, X_2) + Z \le X_1 + X_2 + Z$; Gamma(3) tail $(1 + K_{\text{rec}} + K_{\text{rec}}^2/2)e^{-K_{\text{rec}}}$): $P_{\text{rec}} \le 3.931 \times 10^{-5}$.
   - 47-bit key collision among $\le t_{\max}$ stored trails: $P_{\text{key}} \le \binom{t_{\max}}{2} / 2^{47} \le 6.840 \times 10^{-5}$.
   - Self-cycle before DP across $\le t_{\max}$ trails: $P_{\text{self}} \le t_{\max} L^2 / S \le 7.362 \times 10^{-6}$.
   - Age cap ($\kappa = 40$, union-bounded across all $t_{\max}$ trails and the colliding pair): $P_{\text{age}} \le (t_{\max} + 2(1 + 40)) e^{-40} \le 5.899 \times 10^{-13}$.
   - Cascade counter $U$, stage-2 caps (`P_{20}`, `P_{30}`), skipped `0^47` key ($2^{-47}$), duplicate start: $\le 10^{-12}$.
   - Total failure upper bound: $P_{\text{fail}} \le 1.157630 \times 10^{-4}$.
3. **Certified Lower Bound:**
   $$P_F \ge P_{\text{base,lo}} - P_{\text{fail,hi}} \ge 0.3900010000000003 \ge 0.39.$$

### Complete Total-Cost Ledger
| Component | Charged Word Operations |
| :--- | ---: |
| Main loop unconditional: $B \cdot (43,548 + 14)$ | `57,691,845,295,280,153,026,000,000,000,000,000,000,000` |
| Weighted cascade conditional (`U + 30`; exact VM debits `7, 5, 5, 5, 7`) | `2,590,288,623,569,531,052,098,545,195,735,602,354` |
| Stage-2 (`16` + `400` ops) + DP handler (`305,000` ops/DP) + super-batch age checks (`2e8`) | `5,298,960,497,679,358,455,649,917,176,678,016` |
| Two-Pass Checkpoint Recovery (`CK = 1`, `1,350` ops/step, $D = 2^{102}$, `7,333` checkpoints) | `50,297,303,315,671,253,810,056,604,457,886,187,640` |
| Setup, emitter & initialization (upper bound) | `610,000,000` |
| **Total Charged Word Operations $N$** | **`57,744,738,186,179,891,490,220,610,799,571,408,468,010`** |
| Normalized target compressions $T = N / 2896$ | $\log_2(N / 2896) = 123.906967399727\dots \le \mathbf{123.90700}$ |

---

## 6. Declared Heuristic, Scope, Extrapolation, and Limitations

1. **`H1-random-function-walk` (score-critical):** Assumes the iterated Walk-B transition $F(Y) = B(Y) \oplus \text{PD}$ over 40-round SHA-256 behaves like a uniform random function on $\{0, 1\}^{256}$ with respect to birthday collision hazard, DP hitting-time distribution ($p = 2145 / 2^{122}$), trail-length tails, and 47-bit key independence.
   - *Supporting evidence:* `proof:1-146`, `experiment:sha256-r40-walkb-bounded-w16-v1` (bounded merging DP collision walk embedded on the low 16 bits of the 2-block `W[0..7]`-prefix digest map with strict total budget `max_evals = 285` covering both Pass-1 search and Pass-2 recovery, `dp_bits = 2`, plus deterministic `selftest()` emitting and executing the complete 4-byte + 5-byte native bytecode image on `run_vm`, verifying 256/256 single-step equivalence of both body and unrolled `RecProg` at exact `1,250` ops/step, verifying multi-batch outer-controller execution, and running a direct 64-trial `w=12, budget=64` iterated Walk-B $F(Y)$ birthday check on `run_vm`), and `experiment:sha256-r40-walkb-projection-w14-v1` (fixed-budget $M = 127$ collision frequency on the low 14 bits of the 2-block `W[0..7]`-prefix digest map directly testing the $P \approx 0.39$ birthday curve).
   - *Limitations:* Reduced-width experiments ($w \in \{12, 14, 16\}$) cannot prove the absence of subtle structural correlations or non-random cycle behavior in $F(Y)$ at full 256-bit width. If 40-round SHA-256 exhibited abnormally short cycles or non-uniform DP clustering under $F$, the true success probability could drop below 0.39.
