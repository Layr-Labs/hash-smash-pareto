# Ordinary Collision Search for 40-Round SHA-256 (`sha256-r40-prefix-v1`)

## 1. Target Specification and Summary of Claim

This construction finds an **ordinary classical collision** for complete 40-round SHA-256 (`sha256-r40-prefix-v1`): two distinct byte-string messages $M \ne M'$ of bit length $< 2^{64}$ (specifically, 64-byte / 512-bit messages) whose complete 40-round SHA-256 digests agree on all 256 output bits under the standard FIPS 180-4 fixed IV, message schedule, big-endian length padding, and feed-forward, applying compression rounds `0..39` inclusive to every padded block.

| Quantity | Value |
| :--- | :--- |
| Target profile / rounds | `sha256-r40-prefix-v1` (`40` rounds, steps `0..39` inclusive) |
| Reference compression cost $C(40)$ | `2,896` 256-bit word-RAM operations (`collision-frontier-v5`) |
| Bit-sliced Walk-B kernel (`KLEN`) | `43,548` gates (`34,123` XOR, `5,689` AND, `3,736` OR; `0` NOT, `0` MOV, `0` mixed-polarity) |
| Register file | `860` data registers + `3` pointer registers = `863` registers (`27,616` B; $\le 1,024$, 10-bit indices) |
| Body instruction encoding | Native 32-bit (4-byte) records: `2`-bit op + `3 x 10`-bit regs (`174,192` B) |
| Stage-1 DP filter & outer loop | Weighted cascade (`11` uncond + `3` loop = `14` uncond ops/batch; conditional cap `U + 30`) |
| Trail table | 47-bit bit-sliced table: `546` groups $\times$ `256` = `139,776` slots (`821,184` B; $t_{\max} = 139,520$) |
| Recovery | Two-Pass Checkpoint Recovery (`CK = 1`, `12,831` checkpoints), 2-lane SIMD Walk-B `RecProg` (`1,249` + `180` = `1,429` ops/step) |
| Search-phase peak memory | `1,047,826` bytes ($\le 2^{20} = 1,048,576$ B; `750` B slack; `memory_log2_bytes = 20`, memory penalty `0`) |
| Setup-phase peak memory | $\le 620,000$ bytes ($\le 2^{20}$ B) |
| Preprocessing work (`preprocessing_log2`) | $\le 600{,}000{,}000$ word ops $= 207{,}182.32\dots$ compressions; $\log_2(600{,}000{,}000 / 2896) = 17.660656\dots \le \mathbf{17.66066}$ |
| Non-uniform advice (`nonuniform_advice_log2_bytes`) | `0` bytes |
| Total charged work $N$ | `57,746,901,490,653,995,611,753,326,179,604,236,486,070` word operations |
| Exact $\log_2(N / 2896)$ | `123.907021446732...` |
| **Claimed `time_log2` / normalized score** | **`123.90703`** (upward-rounded at 5 decimals) |
| Certified random-function success bound $P_F$ | `>= 0.3900010000000001 >= 0.39` (exact 80-digit outward-rounded Lemma 2 proof) |

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
5. **Reverse-DAG (Dual) One-Shot Black Pebbling & Zero-Move Home-Register Borrowing:** Scheduling the pruned DAG backward from outputs to inputs by `(newly_opened_operands - 1, -idx)` (reversing to obtain a valid topological order) and borrowing dead home registers `0..255` whose target output is not yet born peaks at **`860` data registers** (`+3` pointer registers = `863 <= 1,024`), with **`0` output `MOV`s**. Every body instruction fits in a native **32-bit (4-byte)** record (`2` opcode bits + `3 x 10` register bits).

---

## 4. Machine Model, Stage-1 Weighted Cascade, Table, Recovery, and Memory Budget

### 4.1 Declared Classical 256-Bit Word-RAM Machine
The machine executes 256-bit word-RAM operations (`XOR`, `AND`, `OR`, `ADD`, `SHL`, `SHR`, `CMP`, `BR`, `LD`, `ST`, `MOV`, `SET`, `RAND`) on `863` 256-bit registers (`860` data + `3` pointer registers; `27,616` B). Every executed operation in setup, main loop, cascade, handler, table lookup/insert, and recovery is charged at 1 operation.

### 4.2 Stage-1 Weighted Cascade and Stage-2 Early-Exit DP Predicate
A lane is a distinguished point (DP) when the low $s_1 = 20$ bits of output word 0 (`e37 ^ PD_0`) are zero and the next $W = 102$ bits (bits `20..121` as an unsigned 102-bit integer) are strictly less than $T_p = 2,155 < 2^{12}$ (equivalently, planes `32..121` are all zero and bits `20..31` are $< 2,155$). Thus the exact DP probability is $p = T_p / 2^{122} = 1 / L$.
- **Unconditional stage-1 + loop (`14` ops/batch):** OR planes `0..9` (`9` ORs), compare with `ALL_ONES` (`1` op), branch (`1` op), plus `3` outer-loop counter/branch ops = `14` ops/batch.
- **Conditional stage-1 cascade (`U + 30` capped):** Levels $j \in \{10, 12, 14, 16, 18\}$ debit $d_j \in \{7, 5, 5, 5, 6\}$ from a single weighted counter $w$ initialized to $U = \sum_j d_j \lceil B(P_j + 10^{-12}) \rceil$, where $P_j = 1 - (1 - 2^{-j})^{256}$.
- **Stage-2 early-exit check (`12` ops on 20-bit hit; `100` ops on 30-bit hit):** On a 20-bit hit (prob $P_{20}$, capped at $\lceil B(P_{20} + 10^{-12}) \rceil$), OR the 10 zero-required planes `32..41` into the 20-bit mask (`10` ORs + `1` CMP + `1` BR = `12` ops). Only on a 30-bit hit (prob $P_{30}$, capped at $\lceil B(P_{30} + 10^{-12}) \rceil$) are the remaining 80 planes `42..121` ORed and the 12-bit window `20..31` compared against $T_p = 2,155$ (`<= 100` ops).

### 4.3 47-Bit Bit-Sliced Trail Table and Two-Pass Checkpoint Recovery (`CK = 1`)
Completed trails are stored in an index-layout 47-bit bit-sliced table of `546` groups $\times$ `256` trails/group (`139,776` slots; `546 * 47 * 32 = 821,184` B), reserving 1 group (`256` slots) for in-flight trails so $t_{\max} = 139,520$. Each DP's 47-bit key is extracted from unconstrained output bits `122..168`. Starting states are deterministic bijections `start(idx) = SALT ^ idx`, with active lane indices `active_slot_id[0..255]` (`1,024` B) and per-lane age counters `active_len[0..255]` (`4,096` B, enforcing age cap $\kappa L$ with $\kappa = 40$) stored inside the `16,384` B counters/work area. On any DP hit, scanning all populated groups (`<= 546` groups $\times$ `47` bit planes, `<= 150` ops/group, masking out unpopulated slots $\ge \text{next\_idx}$ and skipping any slot in `active_slot_id[0..255]` so a `0^47` key never matches an empty/in-flight slot) is conservatively charged at `100,000` ops/DP, plus `800` ops/DP for bit-sliced 47-plane insertion and 256-plane lane restart (`100,800` ops/DP total).

When a 47-bit key match occurs with a populated slot, the table memory is no longer needed and is repurposed as a checkpoint buffer of $k_{\text{chk}} = 821,184 / 64 = 12,831$ checkpoints (64 B each = two 256-bit states).
- **2-Lane SIMD Walk-B `RecProg`:** Walks both colliding trails simultaneously inside 256-bit registers (lane 0 in bits `0..31`, lane 1 in bits `128..159`), using 64-bit duplicated-word rotations `x64 = x | (x << 32)` with cached `dup64(W[k])` so every `ROTR` is 1 shift. Verified `256/256` bit-for-bit against the 43,548-gate kernel at `1,249` arithmetic ops/step, plus a conservative `+180` ops/step rolled loop/indexing/DP-check/checkpoint overhead (`1,429` ops/step total; `440` static 5-byte records = `2,200` B).
- **Two-Pass Checkpoint Search:** Pass 1 walks at most $c_r = \lceil 15.0 L \rceil + 100$ steps, storing a checkpoint every $D = \lceil c_r / k_{\text{chk}} \rceil$ steps. Pass 2 aligns the longer trail in $< D$ steps from stored checkpoint $q = \lfloor (\Delta + kD) / D \rfloor$, binary-searches the $\le k_{\text{chk}} + 1$ intervals in $\le \lceil \log_2(k_{\text{chk}} + 1) \rceil = 14$ probes of $< D$ steps, and steps both trails together for $< D$ steps to isolate the colliding predecessor pair ($M \ne M'$ with $\text{SHA256}_{40}(M) = \text{SHA256}_{40}(M')$), costing at most $(c_r + 16 D) \cdot 1,429 + 8 k_{\text{chk}} + 10,000$ operations.

### 4.4 Memory Budget ($\le 2^{20} = 1,048,576$ Bytes)
| Region (Search Phase) | Bytes |
| :--- | ---: |
| Bit-sliced body (`43,548` $\times$ `4` B) | `174,192` |
| Rolled 2-lane SIMD recovery (`440` $\times$ `5` B) | `2,200` |
| Control + weighted cascade + table routines (`1,250` $\times$ `5` B) | `6,250` |
| Register file (`863` $\times$ `32` B) | `27,616` |
| Counters (`active_slot_id`, `active_len`), & 8 KiB plane copy (recovery array overlaid post-handoff) | `16,384` |
| 47-bit bit-sliced trail table (`546` $\times$ `1,504` B; `139,776` slots) | `821,184` |
| **Total Search-Phase Peak Memory** | **`1,047,826` B** (`750` B below `1,048,576` B) |

During setup, the generator emits the `174,192`-byte body directly into the arena before the `821,184`-byte table is zeroed, keeping setup-phase peak memory below `620,000` bytes ($\le 2^{20}$ B). Thus `memory_log2_bytes = 20` and the normalized memory penalty $\max(0, 20 - 20) = 0$.

---

## 5. Exact Outward-Rounded Lemma 2 Success Bound ($P_F \ge 0.39$) and Cost Ledger

Under `H1-random-function-walk`, model $F : \{0, 1\}^{256} \to \{0, 1\}^{256}$ as a uniform random function ($S = 2^{256}$). With $m = 256$ parallel lanes, $B = 1,324,350,518,154,824 \times 10^{21}$ batches, $T_p = 2,155$ ($L = 2^{122}/2155$), $\kappa = 40$, $K_{\text{rec}} = 15.0$, and $t_{\max} = 139,520$:

1. **Integrated Detection-Delay Collision Lower Bound:**
   $$I(B) = \frac{(m B)^2}{2 S} - \frac{m^2 B L}{S} + \frac{m^2 L^2}{S}(1 - e^{-B/L}) > \frac{(m B)^2}{2 S} - \frac{m^2 B L}{S} = I_{\text{lo}}.$$
   Outward-rounded 80-digit arithmetic (`compute_certified_ledger` in `experiments/sha256_r40_search.py`) certifies $P_{\text{base}} \ge 1 - \exp_{\text{up}}(-I_{\text{lo}})$.
2. **Union-Bound Failure Upper Bounds:**
   - Table overflow ($> t_{\max}$ completed trails in $m B$ steps; Chernoff): $P_{\text{ovf}} \le 1.063 \times 10^{-7}$.
   - Recovery cap ($> c_r = \lceil 15.0 L \rceil + 100$ Pass-1 steps for $\max(X_1, X_2) + Z \le X_1 + X_2 + Z$; Gamma(3) tail $(1 + K_{\text{rec}} + K_{\text{rec}}^2/2)e^{-K_{\text{rec}}}$): $P_{\text{rec}} \le 3.931 \times 10^{-5}$.
   - 47-bit key collision among $\le t_{\max}$ stored trails: $P_{\text{key}} \le \binom{t_{\max}}{2} / 2^{47} \le 6.916 \times 10^{-5}$.
   - Self-cycle before DP across $\le t_{\max}$ trails: $P_{\text{self}} \le t_{\max} L^2 / S \le 7.335 \times 10^{-6}$.
   - Age cap ($\kappa = 40$, union-bounded across all $t_{\max}$ trails and the colliding pair): $P_{\text{age}} \le (t_{\max} + 2(1 + 40)) e^{-40} \le 5.931 \times 10^{-13}$.
   - Cascade counter $U$, stage-2 caps (`P_{20}`, `P_{30}`), duplicate start: $\le 10^{-12}$.
   - Total failure upper bound: $P_{\text{fail}} \le 1.159054 \times 10^{-4}$.
3. **Certified Lower Bound:**
   $$P_F \ge P_{\text{base,lo}} - P_{\text{fail,hi}} \ge 0.3900010000000001 \ge 0.39.$$

### Complete Total-Cost Ledger
| Component | Charged Word Operations |
| :--- | ---: |
| Main loop unconditional: $B \cdot (43,548 + 14)$ | `57,691,357,271,860,443,088,000,000,000,000,000,000,000` |
| Weighted cascade conditional (`U + 30`) | `2,588,974,029,729,786,816,368,385,693,362,695,186` |
| Stage-2 (`12` + `100` ops) + DP handler (`100,000` scan + `800` insert/restart) | `3,911,036,543,645,743,996,241,956,579,299,192` |
| Two-Pass Checkpoint Recovery (`CK = 1`, `1,429` ops/step, `12,831` checkpoints) | `52,951,333,727,279,091,192,961,551,953,694,491,692` |
| Setup, emitter & initialization (upper bound) | `600,000,000` |
| **Total Charged Word Operations $N$** | **`57,746,901,490,653,995,611,753,326,179,604,236,486,070`** |
| Normalized target compressions $T = N / 2896$ | $\log_2(N / 2896) = 123.907021446732\dots \le \mathbf{123.90703}$ |

---

## 6. Declared Heuristics, Scope, Extrapolation, and Limitations

1. **`H1-random-function-walk` (score-critical):** Assumes the iterated Walk-B transition $F(Y) = B(Y) \oplus \text{PD}$ over 40-round SHA-256 behaves like a uniform random function on $\{0, 1\}^{256}$ with respect to birthday collision hazard, DP hitting-time distribution ($p = 2155 / 2^{122}$), trail-length tails, and 47-bit key independence.
   - *Supporting evidence:* `proof:1-148`, `experiment:sha256-r40-walkb-bounded-w16-v1` (bounded merging DP collision walk embedded on the low 16 bits of the 2-block `W[0..7]`-prefix digest map at `max_evals = 265`, `dp_bits = 2`, plus deterministic `selftest()` verifying exact 256/256 equivalence of the 43,548-gate Walk-B kernel + `walk_b_inverse_to_digest`, 860-register allocation, and 1,249-op 2-lane SIMD `RecProg` against complete 40-round SHA-256), and `experiment:sha256-r40-walkb-projection-w14-v1` (fixed-budget $M = 127$ collision frequency on the low 14 bits of the 2-block `W[0..7]`-prefix digest map directly testing the $P \approx 0.39$ birthday curve). Note that the two reduced-width experiments probe the 2-block digest map directly so organizer `digest-xor-mask` verification applies to full digests, while `selftest()` verifies exact bijective equivalence between Walk-B and 2-block `sha256_r40`.
   - *Limitations:* Reduced-width ($w \in \{14, 16\}$) experiments on the 2-block digest map do not prove absence of subtle structural correlations in $F(Y)$ at full 256-bit width. If 40-round SHA-256 exhibited abnormally short cycles or non-uniform DP clustering under $F$, the true success probability could drop below 0.39.
2. **`H2-machine-and-controller-accounting` (score-critical):** Declares the 256-bit word-RAM pricing conventions used in the ledger: 1 operation per 256-bit ALU/branch/memory instruction, 4-byte (32-bit) native body records for 10-bit register addresses (`863 <= 1,024` regs), 5-byte (40-bit) control/recovery records, `1,250`-record controller allowance, `440`-record rolled 2-lane SIMD recovery allowance (`+180` loop/indexing/DP/checkpoint ops/step on top of the verified `1,249` arithmetic ops/step), `100,800`-op/DP bit-sliced table scan + insert/restart allowance, and `600,000,000`-op setup envelope.
   - *Consequence of violation:* If a stricter ISA encoding required 5-byte body records (`+43,548` B, reducing table capacity by `~7,400` slots) or if the rolled controller/recovery exceeded its declared static record or per-step operation allowance, `time_log2` would increase slightly (by `< 0.002` bits) or require re-tuning $(T_p, B)$ within 1 MiB.
