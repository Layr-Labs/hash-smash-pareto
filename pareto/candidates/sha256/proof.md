# Ordinary Collision Search for 40-Round SHA-256 (`sha256-r40-prefix-v1`)

## 1. Target Specification and Complete Cost Vector

This construction finds an **ordinary classical collision** for complete 40-round SHA-256 (`sha256-r40-prefix-v1`): two distinct byte-string messages $M \ne M'$ of bit length $< 2^{64}$ (specifically, 64-byte / 512-bit messages) whose complete 40-round SHA-256 digests agree on all 256 output bits under the standard FIPS 180-4 fixed IV, message schedule, big-endian length padding, and feed-forward, applying compression rounds `0..39` inclusive to every padded block.

| Quantity | Value |
| :--- | :--- |
| Target profile / rounds | `sha256-r40-prefix-v1` (`40` rounds, steps `0..39` inclusive) |
| Reference compression cost $C(40)$ | `2,896` 256-bit word-RAM operations (`collision-frontier-v5`) |
| Bit-sliced Walk-B kernel (`KLEN`) | `43,548` gates (`34,123` XOR, `5,689` AND, `3,736` OR; `0` NOT, `0` MOV, `0` mixed-polarity) |
| Register file | `860` data registers + `3` pointer registers = `863` registers (`27,616` B; $\le 1,024$, 10-bit indices) |
| Body instruction encoding | Native 32-bit (4-byte) records: `2`-bit op + `3 x 10`-bit regs (`174,192` B) |
| Stage-1 DP filter & outer loop | Weighted cascade (`11` uncond + `3` loop = `14` uncond ops/batch; conditional cap `U + 30`) |
| Trail table | 37-bit multi-hit bit-sliced table: `683` groups $\times$ `256` = `174,848` slots (`808,672` B; $t_{\max} = 174,592$) |
| Recovery | Multi-Hit Inline 191-Checkpoint Recovery (`12,224` B buffer), 2-lane SIMD Walk-B `RecProg` (`1,249` + `25` = `1,274` ops/step) |
| Search-phase peak memory | `1,048,238` bytes ($\le 2^{20} = 1,048,576$ B; `338` B slack; `memory_log2_bytes = 20`, memory penalty `0`) |
| Setup-phase peak memory | $\le 620,000$ bytes ($\le 2^{20}$ B) |
| Preprocessing work (`preprocessing_log2`) | $\le 600{,}000{,}000$ word ops $= 207{,}182.32\dots$ compressions; $\log_2(600{,}000{,}000 / 2896) = 17.660656\dots \le \mathbf{17.66066}$ |
| Non-uniform advice (`nonuniform_advice_log2_bytes`) | `0` bytes (all constants are fixed FIPS 180-4 `IV`/`K` or generated deterministically during setup) |
| Total charged work $N$ (including setup & recovery) | `57,709,656,395,939,503,101,982,805,039,988,330,588,417` word operations |
| Exact $\log_2(N / 2896)$ | `123.906090649621...` |
| **Claimed `time_log2` / normalized score** | **`123.90610`** (upward-rounded at 5 decimals; `memory_log2_bytes = 20`) |
| Certified random-function success bound $P_F$ | `>= 0.390000001000000 >= 0.39` (exact 80-digit outward-rounded Lemma 2 proof) |

This is a generic distinguished-point birthday collision search under declared heuristic `H1-random-function-walk` and the `collision-frontier-v5` 256-bit word-RAM cost model. No cryptanalytic weakness in 40-round SHA-256 is claimed, and no full-width 256-bit collision is produced.

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
  cancelling $K_8$ (via $h_8 + \operatorname{Ch}(0, 0, -K_9) + K_8 = (K_9 - K_8) + (-K_9) + K_8 = 0$) and $K_9$ identically at steps 8 and 9 and eliminating all non-trivial gates for rounds `0..8`.
- $W_8 = Y_0$, $W_9 = Y_1$, and $W_{8+k} = (Y_k - K_{8+k}) \bmod 2^{32}$ for $k \in \{2, \dots, 7\}$, where $Y = (Y_0, \dots, Y_7) \in (\{0, 1\}^{32})^8$ is the 256-bit walk state. Because $Y \mapsto B_1(Y)$ is an affine bijection, $M(Y) = M(Y') \iff Y = Y'$.

Because $B_2$ is identical for every message in this family, equal block-1 chaining values $\text{cv}_1(Y) = \text{cv}_1(Y')$ imply equal 40-round digests $\text{SHA256}_{40}(M(Y)) = \text{SHA256}_{40}(M(Y'))$.

### 2.2 Invertible 6-Step Early-Stop Map (Walk B) with Polarity-Matched `Q`/`X` Shears
Let $S_{40}(Y) = (a_{40}, a_{39}, a_{38}, a_{37}, e_{40}, e_{39}, e_{38}, e_{37})$ be the working state after step 39. Instead of computing steps 34..39 in full, the bit-sliced kernel outputs the 8-word tuple
$$B(Y) = (e_{37},\; e_{38},\; a_{33},\; a_{34},\; Q_{34},\; T_{1,35},\; X_{38},\; Y_{39}),$$
with fixed shear masks $Q_M = \texttt{0xb40e844b}$, $X_M = \texttt{0x1b3b3f81}$, and zero constant offsets $x_{\text{cv}} = y_{\text{cv}} = 0$:
- $Q_{34} = T_{1,34} + \text{mj}_{34} \pmod{2^{32}}$, where $\text{mj}_{34}$ replaces $(a_{34} \oplus a_{33}) \land a_{32}$ by its polarity-matched shear using $Q_M$: bit $j$ is $(a_{34} \oplus a_{33})_j \land a_{32,j}$ when $Q_{M,j} = 0$ and $\neg(a_{34} \oplus a_{33})_j \lor a_{32,j}$ when $Q_{M,j} = 1$, using the exact 1-bit identity $d \land c = d + (\neg d \lor c) - 1$.
- $X_{38} = e_{35} + u_{38} + \sigma_1(W_{36}) + W_{31} + \sigma_0(W_{23}) + W_{22} \pmod{2^{32}}$, where $u_{38}$ applies the polarity-matched OR-shear with mask $X_M$ to $(\neg e_{38}) \land e_{36}$ (replacing mismatched bits with $e_{38} \lor e_{36}$ via $(\neg e) \land c = (\neg e) + (e \lor c) - 1$) and directly consumes the already-live $W_{22}$.
- $Y_{39} = e_{36} + \sigma_1(W_{37}) + W_{32} + \sigma_0(W_{24}) + W_{23} \pmod{2^{32}}$, directly consuming the already-live $W_{23}$.

**Theorem (Walk-B Bijection).** $B(Y)$ determines $S_{40}(Y)$ uniquely via the explicit inverse `walk_b_inverse_to_digest`:
1. $a_{35} = Q_{34} + ((a_{34} \oplus a_{33}) \land Q_M) - Q_M + (a_{34} \land a_{33}) + \Sigma_0(a_{34}) \pmod{2^{32}}$.
2. $a_{36} = T_{1,35} + \Sigma_0(a_{35}) + \operatorname{Maj}(a_{35}, a_{34}, a_{33}) \pmod{2^{32}}$.
3. $T_{1,36} = e_{37} - a_{33}$, $a_{37} = T_{1,36} + \Sigma_0(a_{36}) + \operatorname{Maj}(a_{36}, a_{35}, a_{34})$.
4. $T_{1,37} = e_{38} - a_{34}$, $a_{38} = T_{1,37} + \Sigma_0(a_{37}) + \operatorname{Maj}(a_{37}, a_{36}, a_{35})$.
5. $T_{1,38} = X_{38} + ((\neg e_{38}) \land X_M) - X_M + \Sigma_1(e_{38}) + (e_{38} \land e_{37}) + K_{38}$, $e_{39} = a_{35} + T_{1,38}$, $a_{39} = T_{1,38} + \Sigma_0(a_{38}) + \operatorname{Maj}(a_{38}, a_{37}, a_{36})$.
6. $T_{1,39} = Y_{39} + \Sigma_1(e_{39}) + \operatorname{Ch}(e_{39}, e_{38}, e_{37}) + K_{39}$, $a_{40} = T_{1,39} + \Sigma_0(a_{39}) + \operatorname{Maj}(a_{39}, a_{38}, a_{37})$, $e_{40} = a_{36} + T_{1,39}$.

The walk function is $F(Y) = B(Y) \oplus \text{PD}$, where the fixed 256-bit output polarity mask of the kernel is
$$\text{PD} = (\texttt{0x2b1ab639}, \texttt{0x41623d38}, \texttt{0xd03e7fb8}, \texttt{0xcf067bd3}, \texttt{0x84800fd9}, \texttt{0xfa707d26}, \texttt{0x47cac528}, \texttt{0xde7c33b8}).$$
Since $S_{40} \mapsto \text{cv}_1 = \text{IV} + S_{40}$ and $B \oplus \text{PD}$ are bijections, $F(Y) = F(Y') \implies \text{SHA256}_{40}(M(Y)) = \text{SHA256}_{40}(M(Y'))$.

---

## 3. Bit-Sliced Kernel Architecture (`43,548` Gates, `860` Data Registers, `0` Moves)

The kernel evaluates $F(Y)$ simultaneously on $m = 256$ independent trails by holding one bit plane per 256-bit register (rotations and shifts are zero-cost wire renamings). Every signal is tracked as a signed literal `(wire_id << 1) | pol`, where `pol = 1` means the stored register holds the logical complement. De Morgan's laws map $(\neg u) \land (\neg v) = \neg(u \lor v)$ and $(\neg u) \lor (\neg v) = \neg(u \land v)$ to single polarity-matched `OR`/`AND` gates. All `43,548` live instructions (`34,123` XOR, `5,689` AND, `3,736` OR) have **zero `NOT` gates, zero mixed-polarity gates, and zero `MOV` instructions**:

### 3.1 Exact Gate-Level Primitives
1. **Polarity-Matched Multiplexer (`mux(sel, t, f)`):** Let $d = t \oplus f$. If $\operatorname{pol}(\text{sel}) = \operatorname{pol}(d)$, return $f \oplus (\text{sel} \land d)$; else return $t \oplus ((\neg \text{sel}) \land d)$. Used for $\operatorname{Ch}(e, f, g) = \operatorname{mux}(e, f, g)$ and $\operatorname{Maj}(a, b, c) = \operatorname{mux}(b \oplus c, a, b)$ (reusing $b \oplus c = a_{t-1} \oplus b_{t-1}$ with 100% CSE hit $\to$ 64 gates/round).
2. **Zero-`NOT` De Morgan Half-Adders (`ha`, `ha1`, `ha_assoc`, `ha1_assoc`, 2 gates):** For $s = a \oplus b$:
   - `cin = 0`: if $\operatorname{pol}(a) = \operatorname{pol}(b)$, $c = a \land b$; else let $u \in \{a, b\}$ have $\operatorname{pol}(u) = 0$, then $c = u \land \neg s$ (same polarity since $\operatorname{pol}(s) = 1$).
   - `cin = 1`: if $\operatorname{pol}(a) = \operatorname{pol}(b)$, $c = a \lor b$; else let $u \in \{a, b\}$ have $\operatorname{pol}(u) = 1$, then $c = u \lor s$.
   - When 1-step associative XOR lookup finds $h_t \oplus \operatorname{Ch}_t = (h_t \oplus g_t) \oplus (e_t \land (f_t \oplus g_t))$, `ha_assoc`/`ha1_assoc` avoid referencing $\operatorname{Ch}_t$ directly, pruning its outer XOR gate.
3. **Full Adder (`fa`, 5 gates):** If `has_assoc_xor(a, b)`, compute $t = a \oplus b$, $s = t \oplus c$, $c_{\text{out}} = \operatorname{mux}(t, c, a)$ (pruning $\operatorname{Ch}_t$'s outer XOR). Otherwise let $p$ be the odd-polarity input among $\{a, b, c\}$ and $u, v$ the equal-polarity pair: $t_1 = p \oplus u$, $t_2 = p \oplus v$, $s = t_1 \oplus v$, $c_{\text{out}} = p \oplus (t_1 \land t_2)$.
4. **3-Template 32/32 Polarity-Universal 276-Gate `add3` (`pair_col`, 9 gates/column):** Carry between columns is encoded by $(u, U)$ with $\operatorname{val}(u, U) = 1$ if $U = 1$ else $2u$. Across the 6 permutations $(a, b, c)$ of $(x, y, z)$, three 9-gate templates cover all 32 polarity tuples $(p_x, p_y, p_z, p_u, p_U)$ with zero polarity mismatches:
   - **Template A** ($p_U = p_c \oplus p_u$ and $p_b \ne p_c \oplus p_U$): $w_1 = c \oplus u$, $g_A = U \lor w_1$, $w_2 = a \oplus b$, $w_3 = c \oplus U$, $s = w_2 \oplus w_3$, $w_4 = a \oplus w_3$, $g_B = w_2 \lor \neg w_4$, $u' = (\neg w_3) \oplus g_B$, $U' = (\neg g_A) \oplus g_B$.
   - **Template C** ($p_U = p_c \oplus p_u$ and $p_a = p_b$): $w_1 = c \oplus u$, $g_A = U \lor w_1$, $w_3 = c \oplus U$, $w_4 = a \oplus w_3$, $w_5 = b \oplus w_3$, $s = w_4 \oplus b$, $g_B = w_4 \land w_5$, $u' = w_3 \oplus g_B$, $U' = g_A \oplus g_B$.
   - **Template B** ($p_U = 1 \oplus p_u \oplus p_a \oplus p_b \oplus p_c$ and $p_b = p_c$): $w_5 = a \oplus b$, $w_6 = c \oplus w_5$, $s = U \oplus w_6$, $w_9 = u \oplus w_6$, $g_A = U \lor \neg w_9$, $g_B = w_5 \lor (a \oplus c)$, $u' = w_6 \oplus \neg g_A$, $U' = g_A \oplus \neg g_B$.
   Total `add3` cost: `5` (col 0) + `29 * 9` (cols 1..29) + `8` (col 30, `u'` unneeded) + `3` (col 31) = `276` gates (274–276 depending on `cin in {0, 1, 2}`).
5. **Fused Multi-Word Adders (`add4_fused`, `add5_fused`, `add6_fused`, `add2_hch_fused_add3`):**
   - `add4_fused` (429 gates, used in `W[23..37]`): fuses bit-0 carries $(c_{a1}, c_{d1})$ into bit-1 pair-carry $(u_1, U_1) = (c_{a1}, c_{a1} \oplus c_{d1})$, replacing bit-1 `fa` of the `add2` pass with a 2-gate `ha`.
   - `add2_hch_fused_add3` (used in `T1` for rounds `12..35`): fuses bit-0 carries of `h + Ch` and `add3` into $(u_1, U_1)$, freeing bit 1 of `h + Ch` to use a 2-gate `ha_assoc` with carry-in `cu1 in {0, 1}`, and absorbs `cu + 2*cu1 + c3 + delta` into `K[i]` and `W_split[i]` to maximize trailing zeros of `add_const_word(t1_raw, rem)`.
   - `add5_fused` / `add6_fused` (used in `e37`, `e38`, `Y39`, `X38`): fuses bit-0 carries of stacked `add3` passes into bit-1 pair-carry, saving 2 gates on `Y39`, and prefers Templates A and B in `e37`/`e38` to prune `Ch` outer XORs.
6. **`ALL_ONES` Multi-Basin Polarity-Wave Steering (`22` XOR Flips):** Using the already-live `ALL_ONES` register (`r256 = 0xff...ff`, required for stage-1 DP comparison), `22` targeted `XOR(w[b], ALL_ONES)` flips (`E_FLIP_MASKS = {17: 0x04000000, 18: 0x8000, 19: 0x1000, 20: 0x400000, 21: 0x80, 25: 0x10, 32: 0x04000002, 33: 0x900000, 34: 0x20000, 35: 0x110000}`, `A_FLIP_MASKS = {17: 0x40000, 22: 0x10, 26: 0x800, 28: 0x2000, 29: 0x80000000, 30: 0x8, 31: 0x80, 32: 0x01000000}`, `S1_FLIP_MASKS = {37: 0x2}`) align downstream `Ch` and `pair_col` polarities with zero `NOT` gates and zero extra registers, reducing the live kernel from `43,616` to **`43,548` gates**.

### 3.2 Reverse-DAG (Dual) One-Shot Black Pebbling (`860` Data Registers, `0` Moves)
Given the pruned `43,548`-gate DAG (inputs `1..256`, `ALL_ONES = 257`, gates `258..43805`), we schedule gates **backward from outputs to inputs**:
1. Initialize `opened[w] = True` for all 256 output wires and `ALL_ONES = 257`, and `out_deg[g]` = fanout of gate `g`.
2. Maintain a min-heap of ready gates (`out_deg[g] == 0`) keyed by `(newly_opened_operands(g) - 1, -g)`, where `newly_opened_operands(g) in {0, 1, 2}` is the exact net cutwidth change when scheduling `g` in reverse time.
3. Pop the minimum-key gate `g`, append to `rev_order`, mark its operands `opened`, decrement their `out_deg`, and push newly ready producers.
4. Reverse `rev_order` to obtain a valid topological order.
5. Allocate registers linearly in one pass: free dead operands before allocating the destination; assign output wires directly to their home registers `0..255`; borrow dead home registers `hr` only for non-output wires whose `last_use <= home_birth[hr]`.

This peaks at **`860` data registers** (`+3` pointer registers = `863 <= 1,024`, only `91` bits above SHA-256's `769`-bit cutwidth floor of `512` bits for `W[14..29]` + `256` bits for `a26..a29, e26..e29` + `1` bit for `ALL_ONES`) with **`0` output `MOV`s**. Every body instruction fits in a native 32-bit (4-byte) record (`2` opcode bits + `3 x 10` register bits = `174,192` B).

---

## 4. Complete Algorithm, Machine Model, Recovery, and Memory Budget

### 4.1 Declared Classical 256-Bit Word-RAM Machine (`collision-frontier-v5`)
The machine executes 256-bit word-RAM operations (`XOR`, `AND`, `OR`, `ADD`, `SHL`, `SHR`, `CMP`, `BR`, `LD`, `ST`, `MOV`, `SET`, `RAND`) on `863` 256-bit registers (`860` data + `3` pointer registers; `27,616` B). Every executed instruction in setup, main loop, cascade, handler, table lookup/insert, and recovery is charged at 1 operation.

### 4.2 End-to-End Algorithm Specification
1. **Setup Phase ($\le 600{,}000{,}000$ ops, $\le 620{,}000$ B peak):**
   - Draw a fresh 256-bit random run salt `SALT` (`RAND`).
   - Emit the `43,548` 4-byte body instructions (`174,192` B) directly into the code arena, zero the `808,672`-byte 37-bit bit-sliced trail table and `12,224`-byte 191-checkpoint buffer, initialize the weighted cascade budget $w \leftarrow U$, global recovery step budget $C_{\text{rec}} \leftarrow \lceil 17.2 L \rceil$, trail counter $t \leftarrow 0$, and batch counter $b \leftarrow B$.
   - Initialize the 256 parallel lanes (`in_planes[0..255]`) to deterministic index-layout starting points `start(0), ..., start(255)`, where `start(idx) = F_seed(SALT, idx)` is a 1-step deterministic bijection from slot index `idx in [0, 174847]` (so start states are recomputed on demand from `idx` and never stored in the trail table).
2. **Main 256-Lane Loop (repeated $B$ batches):**
   - Execute the `43,548`-gate unrolled Walk-B body on `regs[0..255]` (`43,548` ops).
   - **Stage-1 Unconditional Filter + Loop (`14` ops/batch):** OR output planes `0..9` (`9` ORs), compare with `ALL_ONES` (`1` op), branch to cascade if any lane has all 10 low bits zero (`1` op), decrement `b` and branch (`3` ops).
   - **Weighted Cascade (`U + 30` capped):** On a 10-bit hit, test plane pairs at levels $j \in \{10, 12, 14, 16, 18\}$, debiting $d_j \in \{7, 5, 5, 5, 6\}$ from $w$ (abort if $w < 0$), where $U = \sum_j d_j \lceil B(P_j + 10^{-12}) \rceil$ and $P_j = 1 - (1 - 2^{-j})^{256}$.
   - **Stage-2 Threshold & DP Handler:** On a 20-bit hit (prob $P_{20}$), check whether the next $W = 102$ bits of the hitting lane are $< T_p = 2,704$ (`<= 25` ops; exact DP probability $p = T_p / 2^{122} = 1 / L$). If a lane hits a DP (or exceeds age cap $\kappa L$ with $\kappa = 40$):
     - If $t \ge t_{\max} = 174,592$, abort (table overflow).
     - Extract the lane's 37-bit key `key37` (bits `122..158` of the DP state) and scan the `683` bit-sliced groups in parallel (`<= 150` ops total per DP): for each group `g`, compute `match_mask = AND_{k=0}^{36} (table[g][k] ^ ~key37_k)` and check `match_mask != 0`.
     - If no match, write `key37` into slot `t`, increment `t`, and restart the lane at `start(t + 255)` (`<= 40` ops).
     - **If a 37-bit key match `(i, j)` occurs:** invoke **Multi-Hit Inline 191-Checkpoint Verification** below without overwriting the trail table.
3. **Multi-Hit Inline 191-Checkpoint Verification & Collision Recovery (`1,249 + 25 = 1,274` ops/step):**
   - **2-Lane SIMD `RecProg` (`1,249` arithmetic ops/step):** Packs trail `i` in bits `0..31` and trail `j` in bits `128..159` of 256-bit registers, using 64-bit duplicated-word rotations `x64 = x | (x << 32)` with cached `dup64(W[k])` across `s0`/`s1`. Exact arithmetic op breakdown: `W[10..15]` = 12, `W[16..22]` = 70, `W[23]` = 19, `W[24..37]` = 266, `R9..R11` = 64, `R12..R33` = 572, `R34..R37` + `Q34`/`X38`/`Y39` + `PD` XOR = 246; total = **`1,249` ops/step** (`+25` loop/checkpoint ops = `1,274` ops/step; `480` static 5-byte records = `2,400` B).
   - **Pass 1 (Table-Preserving Confirmation + Checkpointing):** Walk `(start(i), start(j))` simultaneously via `RecProg`, stopping each lane upon reaching its DP, recording a 64-byte `(state_i, state_j)` checkpoint into the dedicated 191-slot inline buffer (`191 * 64 = 12,224` B) every $D = \lceil c_r / 191 \rceil$ steps, and debiting each 2-lane step from the global budget $C_{\text{rec}}$ (abort if $C_{\text{rec}} < 0$).
     - If the two 256-bit DP endpoints **disagree** (false 37-bit key collision): discard the 191-slot scratch buffer and resume the main search loop with the 808 KiB trail table 100% intact.
     - If the two 256-bit DP endpoints **agree** (true 256-bit collision): proceed to Pass 2.
   - **Pass 2 (Inline Binary Search):** Align the longer trail to the shorter trail's length in $< D$ steps from the nearest inline checkpoint, binary-search the $\le 192$ checkpoint intervals in $\le \lceil \log_2(192) \rceil = 8$ probes of $< D$ steps each, and step both trails in lockstep for $< D$ steps to isolate distinct predecessors $Y \ne Y'$ with $F(Y) = F(Y')$. Output the colliding 64-byte messages $M(Y) \ne M(Y')$ satisfying $\text{SHA256}_{40}(M(Y)) = \text{SHA256}_{40}(M(Y'))$. Total recovery ops across the entire run are deterministically bounded by $(c_r + 10 D) \cdot 1,274 + 8 \cdot 191 + 10,000$.

### 4.3 Memory Budget ($\le 2^{20} = 1,048,576$ Bytes)
| Region (Search Phase) | Bytes |
| :--- | ---: |
| Bit-sliced body (`43,548` $\times$ `4` B) | `174,192` |
| Rolled 2-lane SIMD recovery (`480` $\times$ `5` B) | `2,400` |
| Control + weighted cascade + multi-hit table routines (`1,350` $\times$ `5` B) | `6,750` |
| Register file (`863` $\times$ `32` B) | `27,616` |
| Counters, 8 KiB plane copy & inline 191-checkpoint buffer (`16,384 + 12,224` B) | `28,608` |
| 37-bit bit-sliced trail table (`683` $\times$ `1,184` B; `174,848` slots) | `808,672` |
| **Total Search-Phase Peak Memory** | **`1,048,238` B** (`338` B below `1,048,576` B) |

During setup, the emitter writes the `174,192`-byte body directly into the arena before zeroing the `808,672`-byte table, keeping setup peak memory $\le 620,000$ B ($\le 2^{20}$ B). Thus `memory_log2_bytes = 20` and the normalized memory penalty $\max(0, 20 - 20) = 0$.

---

## 5. Probability Space, Exact Lemma 2 Bound ($P_F \ge 0.39$), and Cost Ledger

### 5.1 Probability Space and Success Event
Under `H1-random-function-walk`, let $(\Omega, \mathcal{F}, \mathbb{P})$ be the uniform probability space over all functions $F : \{0, 1\}^{256} \to \{0, 1\}^{256}$ ($S = 2^{256}$) and uniform random run salt `SALT`. The success event $\mathcal{E}_{\text{succ}}$ is that the algorithm terminates within the declared deterministic step budgets and outputs distinct 64-byte messages $M \ne M'$ with $\text{SHA256}_{40}(M) = \text{SHA256}_{40}(M')$.

With $m = 256$ parallel lanes, $B = 1,323,670,110,429,183 \times 10^{21}$ batches, $T_p = 2,704$ ($L = 2^{122}/2704$), $\kappa = 40$, $K_{\text{tot}} = 17.2$, and $t_{\max} = 174,592$:

1. **Integrated Detection-Delay Collision Lower Bound:**
   $$I(B) = \frac{(m B)^2}{2 S} - \frac{m^2 B L}{S} + \frac{m^2 L^2}{S}(1 - e^{-B/L}) > \frac{(m B)^2}{2 S} - \frac{m^2 B L}{S} = I_{\text{lo}}.$$
   Outward-rounded 80-digit arithmetic (`compute_certified_ledger` in `experiments/sha256_r40_search.py`) certifies $P_{\text{base}} \ge 1 - \exp_{\text{up}}(-I_{\text{lo}})$.
2. **Union-Bound Failure Upper Bounds (Elementary Abel-Summation Multi-Hit Proof):**
   - Table overflow ($> t_{\max}$ completed trails in $m B$ steps; Chernoff): $P_{\text{ovf}} \le 3.931 \times 10^{-7}$.
   - **Shared Recovery Step Budget ($> c_r = 17.2 L$ total Pass-1 steps across all false 37-bit key matches plus the true colliding pair):** When trail $i \in \{1, \dots, t_{\max}\}$ is inserted, its 37-bit key matches a prior key with probability $p_i \le (i-1)/2^{37}$ independently of earlier trails; thus the number of false key matches $F = \sum_{i=1}^{t_{\max}} X_i$ satisfies the elementary subset union bound $P(F \ge f) \le \lambda^f / f!$ with $\lambda = \binom{t_{\max}}{2} / 2^{37} \le 0.1109$. Each false hit uses $\max(L_i, L_j) \le L_i + L_j \sim \operatorname{Gamma}(2, L)$ 2-lane steps, and the true colliding pair uses $\max(X_1, X_2) + Z \le X_1 + X_2 + Z \sim \operatorname{Gamma}(3, L)$ 2-lane steps, so total Pass-1 steps are stochastically dominated by $\operatorname{Gamma}(2F + 3, L)$. By Abel summation,
     $$P_{\text{rec}} = \mathbb{E}[g(F)] = g(0) + \sum_{f=1}^{t_{\max}} (g(f) - g(f-1)) P(F \ge f) \le g(0) + \sum_{f=1}^{34} (g(f) - g(f-1))\frac{\lambda^f}{f!} + \frac{\lambda^{35}}{35!} \le 3.500 \times 10^{-5},$$
     where $g(f) = P(\operatorname{Gamma}(2f + 3, 1) > 17.2)$. Note that $P_{\text{key}}$ is completely absorbed into $P_{\text{rec}}$ with zero Poisson approximation.
   - Age cap ($\kappa = 40$): $P_{\text{age}} \le 3.48 \times 10^{-16}$.
   - Cascade counter $U$, stage-2 cap, self-cycle, duplicate start: $\le 10^{-12}$.
   - Total failure upper bound: $P_{\text{fail}} \le 3.539441 \times 10^{-5}$.
3. **Certified Lower Bound:**
   $$\mathbb{P}(\mathcal{E}_{\text{succ}}) \ge P_{\text{base,lo}} - P_{\text{fail,hi}} \ge 0.390000001000000 \ge 0.39.$$

### 5.2 Complete Total-Cost Ledger
| Component | Charged Word Operations |
| :--- | ---: |
| Main loop unconditional: $B \cdot (43,548 + 14)$ | `57,661,717,350,516,069,846,000,000,000,000,000,000,000` |
| Weighted cascade conditional (`U + 30`) | `2,587,643,900,049,491,616,024,835,123,374,662,969` |
| Stage-2 + DP table handler + restarts | `8,078,058,955,059,849,190,787,503,172,530,080` |
| Multi-Hit Inline 191-Checkpoint Recovery (`1,274` ops/step) | `45,343,323,464,428,704,517,589,417,361,183,395,368` |
| Setup, emitter & initialization (upper bound) | `600,000,000` |
| **Total Charged Word Operations $N$** | **`57,709,656,395,939,503,101,982,805,039,988,330,588,417`** |
| Normalized target compressions $T = N / 2896$ | $\log_2(N / 2896) = 123.906090649621\dots \le \mathbf{123.90610}$ |

---

## 6. Declared Heuristic, Evidence, Sensitivity, and Limitations

1. **`H1-random-function-walk` (score-critical):** Assumes the iterated Walk-B transition $F(Y) = B(Y) \oplus \text{PD}$ over complete 40-round SHA-256 behaves like a uniform random function on $\{0, 1\}^{256}$ with respect to birthday collision hazard, DP hitting-time distribution ($p = 2704 / 2^{122}$), trail-length tails, and 37-bit key independence.
   - *Supporting evidence:* `proof:1-6`, `experiment:sha256-r40-walkb-bounded-w16-v1` (organizer-executed bounded DP collision recovery on the exact 64-byte `W[0..7]`-prefix family at $w = 16$ bits, `max_evals = 160`, `dp_bits = 1`, plus deterministic self-test verifying the `43,548`-gate kernel, `860`-register zero-move schedule, and `1,249`-op 2-lane SIMD `RecProg` across all 256 lanes), and `experiment:sha256-r40-walkb-projection-w14-v1` (organizer-executed fixed-budget $M = 127$ collision frequency at $w = 14$ bits directly testing the $P \approx 0.39$ birthday curve).
   - *Limitations:* Reduced-width ($w \in \{14, 16\}$) experiments do not prove absence of subtle structural correlations at full 256-bit width. If 40-round SHA-256 exhibited abnormally short cycles or non-uniform DP clustering under $F$, the true success probability could drop below 0.39.
2. **Deterministic Accounting Sensitivity:** The `43,548`-gate body, `860`-register allocation, and `1,249`-op 2-lane SIMD `RecProg` are exact deterministic counts verified in `experiments/sha256_r40_search.py`. The rolled recovery wrapper (`480` 5-byte records, `+25` loop/checkpoint ops/step), rolled controller/table routines (`1,350` 5-byte records), and setup work (`600,000,000` ops) are conservative deterministic upper bounds; even `+200` extra static records (`+1,000` B) would reduce `groups` by at most 1 (`683 -> 682`) and shift `time_log2` by `< 0.00001` bits.
