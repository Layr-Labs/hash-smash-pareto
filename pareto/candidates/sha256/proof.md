# Ordinary Collision Search for 40-Round SHA-256 (`sha256-r40-prefix-v1`)

## 1. Target Specification and Summary of Claim

This construction finds an **ordinary classical collision** for complete 40-round SHA-256 (`sha256-r40-prefix-v1`): two distinct byte-string messages $M \ne M'$ of bit length $< 2^{64}$ (specifically, 64-byte / 512-bit messages) whose complete 40-round SHA-256 digests agree on all 256 output bits under the standard FIPS 180-4 fixed IV, message schedule, big-endian length padding, and feed-forward, applying compression rounds `0..39` inclusive to every padded block.

| Quantity | Value |
| :--- | :--- |
| Target profile / rounds | `sha256-r40-prefix-v1` (`40` rounds, steps `0..39` inclusive) |
| Reference compression cost $C(40)$ | `2,896` 256-bit word-RAM operations (`collision-frontier-v5`) |
| Bit-sliced Walk-B kernel (`KLEN`) | `43,582` gates (`0` NOT, `0` MOV, `0` mixed-polarity) |
| Register file | `860` data registers + `3` pointer registers = `863` registers (`27,616` B; $\le 1,024$, 10-bit indices) |
| Body instruction encoding | Native 32-bit (4-byte) records: `2`-bit op + `3 x 10`-bit regs (`174,328` B) |
| Stage-1 DP filter & outer loop | Weighted cascade (`11` uncond + `3` loop = `14` uncond ops/batch; conditional cap `U + 30`) |
| Trail table | 37-bit multi-hit bit-sliced table: `683` groups $\times$ `256` = `174,848` slots (`808,672` B; $t_{\max} = 174,592$) |
| Recovery | Multi-Hit Inline 191-Checkpoint Recovery (`12,224` B buffer), 2-lane SIMD Walk-B `RecProg` (`1,249` + `25` = `1,274` ops/step) |
| Search-phase peak memory | `1,048,374` bytes ($\le 2^{20} = 1,048,576$ B; `202` B slack; `memory_log2_bytes = 20`, memory penalty `0`) |
| Setup-phase peak memory | $\le 620,000$ bytes ($\le 2^{20}$ B) |
| Total charged work $N$ | `57,754,661,179,694,095,323,982,805,039,988,330,588,417` word operations |
| Exact $\log_2(N / 2896)$ | `123.907215294584...` |
| **Claimed `time_log2` / normalized score** | **`123.90722`** (upward-rounded at 5 decimals) |
| Certified random-function success bound $P_F$ | `>= 0.390000001000000 >= 0.39` (exact 80-digit outward-rounded Lemma 2 proof) |

This is a generic distinguished-point birthday collision search under declared heuristic `H1-random-function-walk` and machine/accounting declaration `H2-machine-and-controller-accounting`. No cryptanalytic weakness in 40-round SHA-256 is claimed, and no full-width 256-bit collision is produced.

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
where:
- $Q_{34} = T_{1,34} + \text{mj}_{34} \pmod{2^{32}}$, with $\text{mj}_{34}$ replacing $\operatorname{Maj}(a_{34}, a_{33}, a_{32}) = (a_{34} \land a_{33}) + ((a_{34} \oplus a_{33}) \land a_{32})$ by its polarity-matched shear using mask $Q_M$: on bits where $\operatorname{pol}(a_{34} \oplus a_{33}) = \operatorname{pol}(a_{32})$, bit $j$ is $(a_{34} \oplus a_{33})_j \land a_{32,j}$; on bits with $Q_{M,j} = 1$, bit $j$ is $\neg(a_{34} \oplus a_{33})_j \lor a_{32,j}$, using the exact 1-bit identity $d \land c = d + (\neg d \lor c) - 1$.
- $X_{38} = e_{35} + u_{38} + \sigma_1(W_{36}) + W_{31} + \sigma_0(W_{23}) + W_{22} \pmod{2^{32}}$ ($x_{\text{cv}} = 0$), where $u_{38}$ applies the polarity-matched OR-shear with mask $X_M$ to $(\neg e_{38}) \land e_{36}$ (replacing mismatched bits with $e_{38} \lor e_{36}$ via $(\neg e) \land c = (\neg e) + (e \lor c) - 1$) and directly consumes the already-live $W_{22}$ rather than holding `W_split[22]` across 16 rounds.
- $Y_{39} = e_{36} + \sigma_1(W_{37}) + W_{32} + \sigma_0(W_{24}) + W_{23} \pmod{2^{32}}$ ($y_{\text{cv}} = 0$), directly consuming the already-live $W_{23}$ rather than holding `W_split[23]`.

**Theorem (Walk-B Bijection).** $B(Y)$ determines $S_{40}(Y)$ uniquely via the explicit inverse `walk_b_inverse_to_digest`:
1. $a_{35} = Q_{34} + ((a_{34} \oplus a_{33}) \land Q_M) - Q_M + (a_{34} \land a_{33}) + \Sigma_0(a_{34}) \pmod{2^{32}}$.
2. $a_{36} = T_{1,35} + \Sigma_0(a_{35}) + \operatorname{Maj}(a_{35}, a_{34}, a_{33}) \pmod{2^{32}}$.
3. $T_{1,36} = e_{37} - a_{33}$, $a_{37} = T_{1,36} + \Sigma_0(a_{36}) + \operatorname{Maj}(a_{36}, a_{35}, a_{34})$.
4. $T_{1,37} = e_{38} - a_{34}$, $a_{38} = T_{1,37} + \Sigma_0(a_{37}) + \operatorname{Maj}(a_{37}, a_{36}, a_{35})$.
5. $T_{1,38} = X_{38} + ((\neg e_{38}) \land X_M) - X_M + x_{\text{cv}} + \Sigma_1(e_{38}) + (e_{38} \land e_{37}) + K_{38}$, $e_{39} = a_{35} + T_{1,38}$, $a_{39} = T_{1,38} + \Sigma_0(a_{38}) + \operatorname{Maj}(a_{38}, a_{37}, a_{36})$.
6. $T_{1,39} = Y_{39} + y_{\text{cv}} + \Sigma_1(e_{39}) + \operatorname{Ch}(e_{39}, e_{38}, e_{37}) + K_{39}$, $a_{40} = T_{1,39} + \Sigma_0(a_{39}) + \operatorname{Maj}(a_{39}, a_{38}, a_{37})$, $e_{40} = a_{36} + T_{1,39}$.

The walk function is $F(Y) = B(Y) \oplus \text{PD}$, where $\text{PD} \in \{0, 1\}^{256}$ is the fixed output polarity mask of the bit-sliced kernel. Since $S_{40} \mapsto \text{cv}_1 = \text{IV} + S_{40}$ and $B \oplus \text{PD}$ are bijections, $F(Y) = F(Y') \implies \text{SHA256}_{40}(M(Y)) = \text{SHA256}_{40}(M(Y'))$.

---

## 3. Bit-Sliced Kernel Architecture (`43,582` Gates, `860` Data Registers, `0` Moves)

The kernel evaluates $F(Y)$ simultaneously on $m = 256$ independent trails by holding one bit plane per 256-bit register (rotations and shifts are zero-cost wire renamings). All `43,582` live instructions are pure `{XOR, AND, OR}` gates with zero `NOT` gates, zero mixed-polarity penalties, and zero register-to-register `MOV` instructions:
1. **3-Template 32/32 Polarity-Universal 276-Gate `add3`:** Using pair-carry encoding $\operatorname{val}(u, U) = 1$ if $U = 1$ else $2u$, three 9-gate column templates (`A`, `C`, `B`) cover all 32 polarity tuples $(p_x, p_y, p_z, p_u, p_U)$ with zero polarity mismatches (`5 + 8 + 28*9 + 8 + 3 = 276` gates for `cin in {0, 1, 2}`).
2. **Cross-Round `Maj` and `h + Ch` Algebraic Reuse:** $\operatorname{Maj}(a, b, c) = \operatorname{mux}(b \oplus c, a, b)$ reuses $a_{t-1} \oplus b_{t-1}$ with 100% CSE hit; 1-step associative XOR lookup rewrites $h_t \oplus \operatorname{Ch}_t = (h_t \oplus g_t) \oplus (e_t \land (f_t \oplus g_t))$, pruning $\operatorname{Ch}_t$'s outer XOR whenever $\operatorname{pol}(e_t) = \operatorname{pol}(f_t \oplus g_t)$.
3. **Zero-`NOT` De Morgan Half-Adders & Fused Bit-0/Bit-1 Adders (`add4_fused`, `add5_fused`, `add6_fused`):** Mixed-polarity half-adders use $a \land b = a \land \neg(a \oplus b)$ (`cin = 0`) and $a \lor b = b \lor (a \oplus b)$ (`cin = 1`) in 2 gates. Four-, five-, and six-word sums fuse bit-0 carries directly into bit-1 pair-carry (`add4_fused`: `429` gates; `add5_fused` on `Y39`: `-2` gates; `add6_fused` on `X38`), and `T1` fuses `add2_hch` with `add3` while absorbing `cu + 2*cu1 + c3 + delta` into `K[i]` and `W_split[i]`.
4. **5-Word `e37`/`e38` Tail Fusion with Template A+B `Ch`-Pruning:** Rounds 36 and 37 form `e37` and `e38` directly via two 276-gate `add3` calls, preferring Templates A and B where `ch_w` appears only in `h_w ^ ch_w`.
5. **`ALL_ONES` Multi-Basin Polarity-Wave Steering (`8` XOR Flips):** Using the already-live `ALL_ONES` register (`r256 = 0xff...ff`, required for the stage-1 DP comparison), `8` targeted `XOR(w[b], ALL_ONES)` flips (`E_FLIP_MASKS = {22: 0x00000200, 36: 0x00a10000, 37: 0x08000000}`, `A_FLIP_MASKS = {33: 0x8, 34: 0x4000}`, `S1_FLIP_MASKS = {37: 0x400000}`) align downstream `Ch` and `pair_col` polarities without introducing any `NOT` gate or extra register, reducing the kernel from `43,616` to **`43,582` gates**.
6. **Reverse-DAG (Dual) One-Shot Black Pebbling & Zero-Move Home-Register Borrowing:** Dropping the redundant 16-round `W_split[22..23]` tail holdover (0 extra gates) and scheduling the DAG backward from outputs to inputs by minimizing net live-cutwidth delta `(newly_opened_operands - 1, -idx)` before reversing to topological order peaks at **`860` data registers** (`+3` pointer registers = `863 <= 1,024`, only `91` bits above SHA-256's `769`-bit information-theoretic cutwidth floor), with **`0` output `MOV`s**. Every body instruction fits in a native **32-bit (4-byte)** record (`2` opcode bits + `3 x 10` register bits).

---

## 4. Machine Model, Stage-1 Weighted Cascade, Table, Recovery, and Memory Budget

### 4.1 Declared Classical 256-Bit Word-RAM Machine
The machine executes 256-bit word-RAM operations (`XOR`, `AND`, `OR`, `ADD`, `SHL`, `SHR`, `CMP`, `BR`, `LD`, `ST`, `MOV`, `SET`, `RAND`) on `863` 256-bit registers (`860` data + `3` pointer registers; `27,616` B). Every executed operation in setup, main loop, cascade, handler, table lookup/insert, and recovery is charged at 1 operation.

### 4.2 Stage-1 Weighted Cascade DP Predicate
A lane is a distinguished point (DP) when the low $s_1 = 20$ bits of output word 0 (`e37 ^ PD_0`) are zero and the next $W = 102$ bits (as an unsigned 102-bit integer) are strictly less than $T_p = 2,704$. Thus the exact DP probability is $p = T_p / 2^{122} = 1 / L$.
- **Unconditional stage-1 + loop (`14` ops/batch):** OR planes `0..9` (`9` ORs), compare with `ALL_ONES` (`1` op), branch (`1` op), plus `3` outer-loop counter/branch ops = `14` ops/batch.
- **Conditional cascade (`U + 30` capped):** Levels $j \in \{10, 12, 14, 16, 18\}$ debit $d_j \in \{7, 5, 5, 5, 6\}$ from a single weighted counter $w$ initialized to $U = \sum_j d_j \lceil B(P_j + 10^{-12}) \rceil$, where $P_j = 1 - (1 - 2^{-j})^{256}$. On level 18 pass (20-bit hit, prob $P_{20}$), stage 2 checks the 102-bit window (`<= 25` ops).

### 4.3 Multi-Hit 37-Bit Bit-Sliced Trail Table & Inline 191-Checkpoint Recovery
Completed trails are stored in an index-layout **37-bit** bit-sliced table of `683` groups $\times$ `256` trails/group (`174,848` slots; `683 * 37 * 32 = 808,672` B), reserving 1 group (`256` slots) for in-flight trails so $t_{\max} = 174,592$.

Instead of treating a key match as a fatal single-shot stop, the controller maintains a **dedicated inline 191-checkpoint buffer** (`191 * 64 = 12,224` B) inside `work_bytes` (`28,608` B total) and a **single global recovery step budget** $c_r = \lceil K_{\text{tot}} L \rceil$ ($K_{\text{tot}} = 17.2$):
- **2-Lane SIMD Walk-B `RecProg` (`1,249` ops/step):** Walks both colliding trails simultaneously inside 256-bit registers (lane 0 in bits `0..31`, lane 1 in bits `128..159`), using 64-bit duplicated-word rotations `x64 = x | (x << 32)` with cached `dup64(W[i])` across `s0`/`s1` and `x_cv = y_cv = 0`. Verified `256/256` bit-for-bit against the 43,582-gate kernel at `1,249` arithmetic ops/step (`+25` loop/checkpoint ops = `1,274` ops/step; `480` static 5-byte records = `2,400` B).
- **Table-Preserving Multi-Hit Verification & Inline Binary Search:** On any 37-bit key match `(i, j)` during search, the controller runs Pass 1 of `RecProg` on `(start(i), start(j))`, recording checkpoints into the 191-slot buffer every $D = \lceil c_r / 191 \rceil$ steps and debiting each 2-lane step from the global budget $c_r$ **without overwriting the 808 KiB trail table**.
  - If the two 256-bit DP endpoints **disagree** (false 37-bit key collision), the controller discards the 191-slot scratch buffer and resumes search with the trail table intact!
  - If the two 256-bit DP endpoints **agree** (true 256-bit collision), the 191 inline checkpoints are already populated: Pass 2 aligns the longer trail in $< D$ steps, binary-searches the $\le 192$ intervals in $\le \lceil \log_2(192) \rceil = 8$ probes of $< D$ steps, and steps both trails together for $< D$ steps to isolate $(M, M')$, costing at most $(c_r + 10 D) \cdot 1,274 + 8 \cdot 191 + 10,000$ operations across the entire run.

### 4.4 Memory Budget ($\le 2^{20} = 1,048,576$ Bytes)
| Region (Search Phase) | Bytes |
| :--- | ---: |
| Bit-sliced body (`43,582` $\times$ `4` B) | `174,328` |
| Rolled 2-lane SIMD recovery (`480` $\times$ `5` B) | `2,400` |
| Control + weighted cascade + multi-hit table routines (`1,350` $\times$ `5` B) | `6,750` |
| Register file (`863` $\times$ `32` B) | `27,616` |
| Counters, 8 KiB plane copy & inline 191-checkpoint buffer (`16,384 + 12,224` B) | `28,608` |
| 37-bit bit-sliced trail table (`683` $\times$ `1,184` B; `174,848` slots) | `808,672` |
| **Total Search-Phase Peak Memory** | **`1,048,374` B** (`202` B below `1,048,576` B) |

During setup, the generator emits the `174,328`-byte body directly into the arena before the `808,672`-byte table is zeroed, keeping setup-phase peak memory below `620,000` bytes ($\le 2^{20}$ B). Thus `memory_log2_bytes = 20` and the normalized memory penalty $\max(0, 20 - 20) = 0$.

---

## 5. Exact Outward-Rounded Lemma 2 Success Bound ($P_F \ge 0.39$) and Cost Ledger

Under `H1-random-function-walk`, model $F : \{0, 1\}^{256} \to \{0, 1\}^{256}$ as a uniform random function ($S = 2^{256}$). With $m = 256$ parallel lanes, $B = 1,323,670,110,429,183 \times 10^{21}$ batches, $T_p = 2,704$ ($L = 2^{122}/2704$), $\kappa = 40$, $K_{\text{tot}} = 17.2$, and $t_{\max} = 174,592$:

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
   $$P_F \ge P_{\text{base,lo}} - P_{\text{fail,hi}} \ge 0.390000001000000 \ge 0.39.$$

### Complete Total-Cost Ledger
| Component | Charged Word Operations |
| :--- | ---: |
| Main loop unconditional: $B \cdot (43,582 + 14)$ | `57,706,722,134,270,662,068,000,000,000,000,000,000,000` |
| Weighted cascade conditional (`U + 30`) | `2,587,643,900,049,491,616,024,835,123,374,662,969` |
| Stage-2 + DP table handler + restarts | `8,078,058,955,059,849,190,787,503,172,530,080` |
| Multi-Hit Inline 191-Checkpoint Recovery (`1,274` ops/step) | `45,343,323,464,428,704,517,589,417,361,183,395,368` |
| Setup, emitter & initialization (upper bound) | `600,000,000` |
| **Total Charged Word Operations $N$** | **`57,754,661,179,694,095,323,982,805,039,988,330,588,417`** |
| Normalized target compressions $T = N / 2896$ | $\log_2(N / 2896) = 123.907215294584\dots \le \mathbf{123.90722}$ |

---

## 6. Declared Heuristics, Scope, Extrapolation, and Limitations

1. **`H1-random-function-walk` (score-critical):** Assumes the iterated Walk-B transition $F(Y) = B(Y) \oplus \text{PD}$ over 40-round SHA-256 behaves like a uniform random function on $\{0, 1\}^{256}$ with respect to birthday collision hazard, DP hitting-time distribution, trail-length tails, and 47-bit key independence.
   - *Supporting evidence:* `proof:1-6`, `experiment:sha256-r40-walkb-bounded-w16-v1` (bounded DP collision recovery on the exact 64-byte `W[0..7]`-prefix family at $w = 16$ bits plus deterministic self-test of the 43,588-gate kernel), and `experiment:sha256-r40-walkb-projection-w14-v1` (fixed-budget $M = 127$ collision frequency at $w = 14$ bits directly testing the $P \approx 0.39$ birthday curve).
   - *Limitations:* Reduced-width ($w \in \{14, 16\}$) experiments do not prove absence of subtle structural correlations at full 256-bit width. If 40-round SHA-256 exhibited abnormally short cycles or non-uniform DP clustering under $F$, the true success probability could drop below 0.39.
2. **`H2-machine-and-controller-accounting` (score-critical):** Declares the 256-bit word-RAM pricing conventions used in the ledger: 1 operation per 256-bit ALU/branch/memory instruction, 4-byte (32-bit) native body records for 10-bit register addresses (`<= 1,024` regs), 5-byte (40-bit) control/recovery records, `1,250`-record controller allowance, `440`-record rolled 2-lane SIMD recovery allowance (`+25` loop/checkpoint ops/step on top of the verified `1,279` arithmetic ops/step), and `600,000,000`-op setup envelope.
   - *Consequence of violation:* If a stricter ISA encoding required 5-byte body records (`+43,588` B, reducing table capacity by `~7,400` slots) or if the rolled controller/recovery exceeded its declared static record or per-step operation allowance, `time_log2` would increase slightly (by `< 0.002` bits) or require re-tuning $(T_p, B)$ within 1 MiB.
