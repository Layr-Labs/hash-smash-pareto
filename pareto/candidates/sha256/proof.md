# Ordinary Two-Block Collision Attack on 39-Step SHA-256 (`sha256-r39-prefix-v1`) via Bipartite Claw Search

## 1. Target Profile, Attack Overview, and Headline Claim

We present a complete, memory-bounded ordinary two-block collision attack on **39-step SHA-256** (`sha256-r39-prefix-v1`):
- **Target definition**: Standard SHA-256 initial chaining value $\mathrm{IV}$ applied once before block 0; steps $r = 0, \dots, 38$ (the first 39 steps of SHA-256) applied to each 512-bit padded block with Davies-Meyer feed-forward $\mathrm{CV}_{i+1} = \mathrm{CV}_i + \operatorname{State}_{39}(\mathrm{CV}_i, B_i) \pmod{2^{32}}$; standard FIPS 180-4 padding; equality on all eight 32-bit digest words; output consists of two distinct 128-byte (two-block) messages $M_0 \| M_1 \ne M_0 \| M_1'$ whose second-block chaining values collide ($\mathrm{CV}_2 = \mathrm{CV}_2'$), so the identical FIPS 180-4 padding block preserves equality across all eight digest words.
- **Headline resource bounds**:
  - **Total work**: $T \le 2^{121.07}$ target compressions ($C = 2812$ 256-bit word operations per 39-step compression under `collision-frontier-v5`).
  - **Resident memory**: $M \le 823,296\text{ bytes} < 2^{20}\text{ bytes}$ ($1\text{ MiB}$), so $\log_2 M = 20$ and the Pareto memory penalty is $\max(0, 20 - 20) = 0$.
  - **Combined Pareto score**: $\mathrm{Score} = 121.07 + \max(0, 20 - 20) = 121.07$, improving on the accepted 39-step generic birthday baseline (`124.83147`) by **3.76 bits** ($13.5\times$) and on prior 39-step claw submissions (`123.42` and `121.67`).
  - **Preprocessing**: $2^{36}$ target compressions (one-time characteristic and dense-base derivation, negligible against $2^{121.07}$).
  - **Non-uniform advice**: $\le 2^{11}\text{ bytes}$ ($584\text{ bytes}$ for the 39-step Table 23 dense base and row conditions, or $1,800\text{ bytes}$ including all 16 embedded verification witnesses).
  - **Success probability**: $\ge 0.39$ ($\lambda = -\ln(1 - 0.39) = 0.49429635$).

All code, constants, traced instruction schedules, register allocations, live van Oorschot-Wiener (vOW) claw recovery, and 16 verified 39-step semi-free-start colliding pairs are self-contained in [`experiments/r39_claw.py`](experiments/r39_claw.py) and verified via `python3 -B experiments/r39_claw.py --selftest` and `--ledger`.

---

## 2. Why Direct A0-Variant Enumeration Fails at 39 Steps and How the Bipartite Claw Solves Row 16

In the two-block framework of Mendel, Nad, and Schläffer (EUROCRYPT 2013; IACR ePrint 2015/350) and ePrint 2026/1120 (Table 21 / Table 23), a 39-step local collision spans steps $r = 8, \dots, 26$ with active message words at steps $8, 9, 10, 11, 12, 16, 17, 24, 26$ and zero differences on steps $0, \dots, 7$ and $27, \dots, 38$.
Because the Table 23 dense base fixes the state words $(A_r, E_r)$ for $r \in \{2, \dots, 15\}$ (`BASE_A0[6..19]`, `BASE_E0[6..19]`, `BASE_A1[6..19]`, `BASE_E1[6..19]`) and message words $W_r$ for $r \in \{10, \dots, 15\}$ (including $W_{14} = \mathtt{0x43660040}$, $W_{15} = \mathtt{0x4891771f}$), the free prefix degrees of freedom before step 2 are parameterized by $(a_0, a_1) = (A_0, A_1)$.
For a chaining value $\mathrm{CV}_1 = (\mathrm{cv}_0, \dots, \mathrm{cv}_7)$ produced by a random first block $M_0$:
1. In a naive $\mathcal{A}_0$-variant sweep (used at 37 and 38 steps), $W_{16}$ depends simultaneously on $(a_0, a_1)$ and $\mathrm{CV}_1$, while exact bit-by-bit enumeration (`solve_row_exact` in [`experiments/r39_claw.py`](experiments/r39_claw.py#L293-L360)) shows that $|G_{16}| = 2$ ($\{\mathtt{0xbca1c121}, \mathtt{0xbca1c321}\}$) and only a **single** row-16 word $g = \mathtt{0xbca1c321}$ has a non-empty row-17 fiber $G_{17}(g) = \{\mathtt{0x71e9ba98}\}$.
2. Hitting $W_{16} = g$ by forward trials costs $2^{32}$ evaluations per hit. Instead, re-parameterizing $(a_0, a_1)$ by $(a_0, u)$ where $u = W_1$ separates $W_{16}$ into an additive bipartite claw equation.

### Lemma 2.1 (Exact Bipartite Claw Decomposition of $W_{16}$)
In the state array convention of [`experiments/r39_claw.py`](experiments/r39_claw.py#L190-L264), indices $0, 1, 2, 3$ of `A[m][0..42]` and `E[m][0..42]` hold $\mathrm{CV}_1$ in reverse order (`A[m][3 - j] = cv[j]`, `E[m][3 - j] = cv[4 + j]` for $j = 0, 1, 2, 3$), and step $r \ge 0$ produces `A[m][r + 4]` and `E[m][r + 4]` using message word `W[m][r]`.
For any chaining value $\mathrm{CV}_1 = (\mathrm{cv}_0, \dots, \mathrm{cv}_7)$ and any pair $(a_0, u) \in (\mathbb{Z}/2^{32}\mathbb{Z})^2$, define:
$$t_{2,0} = \Sigma_0(\mathrm{cv}_0) + \operatorname{MAJ}(\mathrm{cv}_0, \mathrm{cv}_1, \mathrm{cv}_2) \pmod{2^{32}}, \qquad e_{0,\text{base}} = \mathrm{cv}_3 - t_{2,0} \pmod{2^{32}},$$
$$k_0 = -t_{2,0} - \mathrm{cv}_7 - \Sigma_1(\mathrm{cv}_4) - \operatorname{CH}(\mathrm{cv}_4, \mathrm{cv}_5, \mathrm{cv}_6) - K_0 \pmod{2^{32}}, \qquad c_{9,0} = W_9^{\text{base}} + A_{\text{base}}[5] \pmod{2^{32}},$$
and set $e_0(a_0) = a_0 + e_{0,\text{base}} \pmod{2^{32}}$ and
$$a_1(a_0, u) = \operatorname{recover\_a1}(a_0, u, \mathrm{CV}_1) = u + \Sigma_0(a_0) + \operatorname{MAJ}(a_0, \mathrm{cv}_0, \mathrm{cv}_1) + \Sigma_1(e_0(a_0)) + \operatorname{CH}(e_0(a_0), \mathrm{cv}_4, \mathrm{cv}_5) + \mathrm{cv}_6 + K_1 \pmod{2^{32}}.$$
Then inverting steps $0 \dots 15$ (`build_variant(cv, a0, a1)` in [`experiments/r39_claw.py`](experiments/r39_claw.py#L238-L264)) determines $W_0, \dots, W_{15}$ uniquely with probability 1 such that:
1. $W_0 = a_0 + k_0 \pmod{2^{32}}$ depends only on $a_0$ and $\mathrm{CV}_1$.
2. $W_1 = u \pmod{2^{32}}$ equals the parameter $u$.
3. $W_9 = c_{9,0} - a_1(a_0, u) \pmod{2^{32}}$ and $W_{14} = W_{14}^{\text{base}} = \mathtt{0x43660040}$.
4. In the SHA-256 message schedule at step 16, $W_{16} = \sigma_1(W_{14}) + W_9 + \sigma_0(W_1) + W_0 \pmod{2^{32}}$ satisfies:
   $$W_{16}(a_0, u) = g + \bigl(\sigma_0(u) - u\bigr) - F_{\text{even}}(a_0, \mathrm{CV}_1) \pmod{2^{32}},$$
   where $c_{\text{walk}} = g - \sigma_1(W_{14}^{\text{base}}) - c_{9,0} - k_0 + \mathrm{cv}_6 + K_1 \pmod{2^{32}}$ and
   $$F_{\text{even}}(a_0, \mathrm{CV}_1) = c_{\text{walk}} + \Sigma_0(a_0) + \operatorname{MAJ}(a_0, \mathrm{cv}_0, \mathrm{cv}_1) + \Sigma_1(e_0(a_0)) + \operatorname{CH}(e_0(a_0), \mathrm{cv}_4, \mathrm{cv}_5) - a_0 \pmod{2^{32}}.$$

**Proof.**
1. At step $r = 0$ (`idx = 4`), `t1 = A[0][4] - t2_0 = a0 - t2_0`, so `E[0][4] = cv[3] + a0 - t2_0 = a0 + e0_base` and `W[0][0] = t1 - cv[7] - S1(cv[4]) - CH(cv[4], cv[5], cv[6]) - K39[0] = a0 + k0 (mod 2^32)`.
2. At step $r = 1$ (`idx = 5`), `t2_1 = S0(a0) + MAJ(a0, cv[0], cv[1])` and `t1_1 = a1 - t2_1`, so `W[0][1] = a1 - t2_1 - cv[6] - S1(e0) - CH(e0, cv[4], cv[5]) - K39[1] = u (mod 2^32)` by definition of `recover_a1(a0, u, wp)`.
3. At step $r = 5$ (`idx = 9`), `A[0][6..9]` are fixed by `BASE_A0[6..9]`, so `E[0][9] = A[0][5] + (BASE_A0[9] - t2_5) = a1 + (BASE_E0[9] - BASE_A0[5])`, and at step $r = 9$ (`idx = 13`), `W[0][9] = E[0][13] - A[0][9] - E[0][9] - S1(E[0][12]) - CH(E[0][12], E[0][11], E[0][10]) - K39[9] = BASE_W0[9] + BASE_A0[5] - a1 = c9_0 - a1 (mod 2^32)`.
4. Substituting `W[0][14] = BASE_W0[14]`, `W[0][9] = c9_0 - a1`, `W[0][1] = u`, and `W[0][0] = a0 + k0` into $W_{16} = \sigma_1(W_{14}) + W_9 + \sigma_0(W_1) + W_0 \pmod{2^{32}}$ yields $W_{16}(a_0, u) = g + (\sigma_0(u) - u) - F_{\text{even}}(a_0, \mathrm{CV}_1) \pmod{2^{32}}$. $\square$

---

## 3. Bipartite Walk Function $F_{\text{step}}$ and Exact Domain Isolation

To solve $F_{\text{even}}(a_0, \mathrm{CV}_1) \equiv \sigma_0(u) - u \pmod{2^{32}}$ for the unique valid row-16 target word $g = \mathtt{0xbca1c321}$ using a distinguished-point walk (van Oorschot-Wiener, CCS 1994), we define a single step function $F_{\text{step}} : \{0, 1\}^{32} \to \{0, 1\}^{32}$ partitioned by the least significant bit $(x \bmod 2)$ of the input $x \in \{0, 1\}^{32}$ ([`experiments/r39_claw.py`](experiments/r39_claw.py#L208-L221)):
$$F_{\text{step}}(x) = \begin{cases}
c_{\text{walk}} + \Sigma_0(x) + \operatorname{MAJ}(x, \mathrm{cv}_0, \mathrm{cv}_1) + \Sigma_1(e_0(x)) + \operatorname{CH}(e_0(x), \mathrm{cv}_4, \mathrm{cv}_5) - x \pmod{2^{32}} & \text{if } (x \bmod 2) = 0 \text{ (even: } x = a_0\text{)}, \\
\sigma_0(x) - x \pmod{2^{32}} & \text{if } (x \bmod 2) = 1 \text{ (odd: } x = u\text{)}.
\end{cases}$$

### Lemma 3.1 (Opposite-Parity Walk Collision $\implies$ Exact Row-16 Claw)
For any even $a_0 \in \{0, 1\}^{32}$ ($(a_0 \bmod 2) = 0$) and any odd $u \in \{0, 1\}^{32}$ ($(u \bmod 2) = 1$), setting $a_1 = \operatorname{recover\_a1}(a_0, u, \mathrm{CV}_1)$ gives:
$$F_{\text{step}}(a_0) = F_{\text{step}}(u) \iff F_{\text{even}}(a_0, \mathrm{CV}_1) \equiv \sigma_0(u) - u \pmod{2^{32}} \iff W_{16}(a_0, u) = g = \mathtt{0xbca1c321}.$$
Every opposite-parity walk collision $(a_0, u)$ therefore satisfies $W_{16}(a_0, u) = \mathtt{0xbca1c321}$ with **100% algebraic certainty** (`mismatches = 0` across all `162,983` raw claws and `135,412` distinct claws in our benchmark and across all 16 embedded witnesses in `PAIR_CLAW_SFS`). $\square$

---

## 4. Self-Contained Table 23 Dense Base and Memory-Free Verification

Unlike submission `f86da3c1`, which invoked an external depth-first search (DFS) solver allocating $1,048,576 + 94,483 = 1,143,059\text{ bytes}$ at runtime (exceeding the $2^{20}\text{ byte}$ zero-penalty threshold and incurring a $+1.0\text{ bit}$ Pareto memory penalty), our submission embeds the complete verified 39-step Table 23 dense base directly as static 32-bit word tuples in [`experiments/r39_claw.py`](experiments/r39_claw.py#L37-L144):
- `BASE_A0[0..19]`, `BASE_E0[0..19]`, `BASE_A1[0..19]`, `BASE_E1[0..19]` ($4 \times 20 = 80$ words $= 320\text{ bytes}$, fixing steps $2..15$).
- `BASE_W0[0..15]`, `BASE_W1[0..15]` ($2 \times 16 = 32$ words $= 128\text{ bytes}$).
- `ROW_MASKS` and `CONDS_16_18_23` (exact bitwise masks and conditions for rows $16..26$).
- `PAIR_CLAW_SFS[0..15]` (16 complete 39-step semi-free-start colliding tuples `(cv_hex, a0, a1)` constructed from the Table 23 dense base and satisfying the bipartite claw equation $F_{\text{step}}(a_0) = F_{\text{step}}(u)$, $W_{16} = \mathtt{0xbca1c321}$, $W_{17} = \mathtt{0x71e9ba98}$, and rows 8..9 side conditions `in_F8(W8)` and `in_F9(W9)`).

In [`experiments/r39_claw.py`](experiments/r39_claw.py#L826-L858), `verify_claw_sfs_tuple()` verifies in $O(1)$ scratch memory ($< 4\text{ KiB}$) that:
1. All 16 embedded tuples in `PAIR_CLAW_SFS` have $M_1 \ne M_1'$ and identical 8-word 39-step SHA-256 outputs $\operatorname{sha256\_r39\_compress}(\mathrm{CV}_1, M_1) == \operatorname{sha256\_r39\_compress}(\mathrm{CV}_1, M_1')$.
2. Every tuple satisfies $(a_0 \bmod 2) = 0$, $(u \bmod 2) = 1$, $F_{\text{step}}(a_0) = F_{\text{step}}(u)$, $\operatorname{recover\_a1}(a_0, u) = a_1$, $W_{16} = \mathtt{0xbca1c321}$, $W_{17} = \mathtt{0x71e9ba98}$ ($W_{17}' = \mathtt{0x31e9ba98}$), and the exact row-8 and row-9 conditions `in_F8(W[0][8])` and `in_F9(W[0][9])`.

Total non-uniform advice is under $2\text{ KiB}$ ($\le 2^{11}\text{ bytes}$, `nonuniform_advice_log2_bytes = 11`), and online dense-base memory is **zero beyond the embedded constants**.

---

## 5. Packed 7-Lane $\times$ 36-Bit Word-RAM Machine Model and 67-Op Spill-Free Kernel

We adopt the exact same 256-bit word-RAM SIMD packing convention used by the accepted Round 39 generic birthday baseline (`8681f9bd`, `shrho.py`) and the Round 39 claw baseline (`f86da3c1`, `clawexp.py`):
- **Word width**: 256 bits, partitioned into **`LANES = 7`** independent lanes at a **`PITCH = 36`-bit** stride (bits $36k \dots 36k+31$ hold lane $k$'s 32-bit value; bits $36k+32 \dots 36k+35$ are a 4-bit guard band).
- **Register file**: **`REGISTERS = 64`** general-purpose 256-bit registers ($64 \times 32 = 2,048\text{ bytes}$).
- **Instruction encoding**: **`INSTR_BYTES = 36`** bytes per instruction (4 bytes opcode/register specifiers + 32 bytes immediate 256-bit constant).
- **39-step compression normalization**: **`C_BLOCK = 2812`** word operations per 39-step compression (`collision-frontier-v5`).

### 5.1 Guard-Band Lane Isolation and 67-Instruction Straight-Line Schedule
In [`experiments/r39_claw.py`](experiments/r39_claw.py#L397-L596), `Tracer` traces every word-RAM instruction and `build_traced_step()` constructs the packed 7-lane evaluation of $F_{\text{step}}(x)$:
1. **Exact lane-isolated shifts (`shrho.py` convention)**:
    - Right shift by $n \in \{1, \dots, 31\}$: `(v >> n) & broadcast36((1 << (32 - n)) - 1)` (2 ops: `shr`, `and_c`). Because the mask is `(1 << (32 - n)) - 1`, any guard bits in positions $32..35$ of lane $k$ that shift down into bits $32-n \dots 35-n$ are **masked to zero**, and no bit from lane $k+1$ (starting at bit $36$) can reach bits $0 \dots 31-n$ since $36 - n \ge 5 > 32 - n$.
   - Left shift by $32 - n$ for 32-bit rotation `ror_p(v, n)`: `(v << (32 - n)) & broadcast36(((1 << n) - 1) << (32 - n))` (2 ops: `shl`, `and_c`).
   - Thus every 32-bit rotation `ror_p(v, n)` costs $2 + 2 + 1 = 5$ ops, and every 3-term XOR rotation ($\Sigma_0, \Sigma_1, \sigma_0$) costs:
     - $\sigma_0(x) = \operatorname{ror}(x, 7) \oplus \operatorname{ror}(x, 18) \oplus (x \gg 3)$: $5 + 5 + 2 + 2 = 14$ ops.
     - $\Sigma_0(x) = \operatorname{ror}(x, 2) \oplus \operatorname{ror}(x, 13) \oplus \operatorname{ror}(x, 22)$: $5 + 5 + 5 + 2 = 17$ ops.
     - $\Sigma_1(e_0) = \operatorname{ror}(e_0, 6) \oplus \operatorname{ror}(e_0, 11) \oplus \operatorname{ror}(e_0, 25)$: $5 + 5 + 5 + 2 = 17$ ops.
2. **Guard-band-safe $e_0$ addition (1 op)**:
   - We compute `e0 = x + e0_base` in **1 instruction** (`add`) without an explicit `& 0xFFFFFFFF` mask. Why is this bit-exact? Because `e0` is consumed exclusively by `S1(e0)` and `CH(e0, c4, c5) = c5 ^ (e0 & (c4 ^ c5))`. In `S1(e0)`, the shift masks `(1 << (32 - n)) - 1` and `((1 << n) - 1) << (32 - n)` zero out bits $32..35$ of `e0` on all three rotation arms; in `CH(e0, c4, c5)`, `c4 ^ c5` is precomputed with zero guard bits (`0x0` in bits $32..35$), so `e0 & (c4 ^ c5)` automatically zeros bits $32..35$!
3. **Constant folding for $\operatorname{MAJ}$ and $\operatorname{CH}$ (9 ops total for `MAJ`, `CH`, and `even_pre`)**:
   - Per chaining value $\mathrm{CV}_1$, the broadcast immediates `c0_xor_c1 = cv[0] ^ cv[1]`, `c0_and_c1 = cv[0] & cv[1]`, `c4_xor_c5 = cv[4] ^ cv[5]`, and `c5 = cv[5]` are fixed across all walk steps of that $\mathrm{CV}_1$.
   - $\operatorname{MAJ}(x, \mathrm{cv}_0, \mathrm{cv}_1) = (x \ \& \ (\mathrm{cv}_0 \oplus \mathrm{cv}_1)) \oplus (\mathrm{cv}_0 \ \& \ \mathrm{cv}_1)$ costs **2 ops** (`and`, `xor`; 5 ops unfolded).
   - $\operatorname{CH}(e_0, \mathrm{cv}_4, \mathrm{cv}_5) = \mathrm{cv}_5 \oplus (e_0 \ \& \ (\mathrm{cv}_4 \oplus \mathrm{cv}_5))$ costs **2 ops** (`and`, `xor`; 3 ops unfolded).
   - Summing `even_pre = (c_walk + S0(x) + MAJ + S1(e0) + CH) & 0xFFFFFFFF` costs **5 ops** (`4` `add`s + `1` `and_c`).
4. **Shared subtraction and 2-op parity mask (8 ops)**:
   - Both branches subtract $x \pmod{2^{32}}$: the even branch outputs $\text{even\_pre} - x \pmod{2^{32}}$ and the odd branch outputs $\sigma_0(x) - x \pmod{2^{32}}$.
   - We compute the parity mask in **2 ops**: `p = x & 1` (`and_c`), `m = p + 0xFFFFFFFF` (`add_c`). When $p = 0$ (even lane), $m = \mathtt{0xFFFFFFFF}$ in bits $0..31$ (carry into bit 32 is 0); when $p = 1$ (odd lane), $m = \mathtt{0x100000000}$ so bits $0..31$ are $\mathtt{0x00000000}$!
   - Blending before subtracting $x$: `blended = s0_x ^ (m & (s0_x ^ even_pre))` (**3 ops**: `xor`, `and`, `xor`), followed by `neg_x = (x ^ 0xFFFFFFFF) + 1` (**2 ops**) and `out = (blended + neg_x) & 0xFFFFFFFF` (**2 ops**; total $2 + 3 + 2 + 2 = 9$ ops, or $5 + 9 = 14$ ops for `even_pre` + blend + `- x`).

### Table 5.1: Exact Instruction Breakdown and Register Allocation of `F_step`
| Sub-block | Folded Ops | Unfolded Ops | Live Regs | Notes |
|---|---:|---:|---:|---|
| $\sigma_0(x)$ (`ror(7) ^ ror(18) ^ shr(3)`) | 14 | 14 | 10 | 5+5+2 ops + 2 XORs |
| $\Sigma_0(x)$ (`ror(2) ^ ror(13) ^ ror(22)`) | 17 | 17 | 11 | 5 ops per `ror` + 2 XORs |
| $\operatorname{MAJ}(x, \mathrm{cv}_0, \mathrm{cv}_1)$ | 2 | 5 | 10 | `and`, `xor` (folded) |
| $e_0 = x + e_{0,\text{base}}$ | 1 | 1 | 11 | Guard bits $32..35$ masked by $\Sigma_1$ and $\operatorname{CH}$ |
| $\Sigma_1(e_0)$ (`ror(6) ^ ror(11) ^ ror(25)`) | 17 | 17 | 13 | 5 ops per `ror` + 2 XORs |
| $\operatorname{CH}(e_0, \mathrm{cv}_4, \mathrm{cv}_5)$ | 2 | 3 | 12 | `and`, `xor` (folded) |
| `even_pre = (c_walk + S0 + MAJ + S1 + CH) & 0xFFFFFFFF` | 5 | 5 | 9 | 4 `add` + 1 `and_c` |
| Parity blend + shared `- x` | 9 | 9 | 10 | `p = x & 1`, `m = p + 0xFFFFFFFF`, blend, `- x` |
| **Total `F_step` kernel (`step_ops_folded`)** | **67** | **71** | **13 peak** | **0 register spills in 64 registers** |
| Stage-1 DP check (`out & dp_mask`, `bz`) | +2 | +2 | — | Tests if any of the 7 lanes hit `dp_bits = 7` |
| Loop counter & branch (`sub_c`, `bnz`) | +2 | +2 | — | Advances packed walk batch |
| **Main stage-1 batch (`main_batch_ops`)** | **71** | **75** | **13 peak** | **10.143 ops/lane evaluation** |
| **Stage-2 recovery batch (`rec_batch_ops`)** | **69** | **73** | **13 peak** | `F_step` (67 ops) + loop/cmp (2 ops) |

Linear-scan register allocation (`allocate()` in [`experiments/r39_claw.py`](experiments/r39_claw.py#L513-L543)) assigns all 67 instructions to **13 physical registers** out of 64 (`spill_ops_64 = 0`), and `run_allocated()` ([`experiments/r39_claw.py`](experiments/r39_claw.py#L550-L596)) executes the register-allocated program on the simulated 64-register file across 112 lanes per active trial in `r39-claw-vow` with **0 mismatches** against scalar `F_step`.

---

## 6. End-to-End vOW Distinguished-Point Walk and Complete Cost Ledger

To eliminate the judge refutation of prior claw submissions (`6807f974` and `f86da3c1`, where stage-2 path recovery and table-handling overhead were uncounted or roughly estimated without simulation), we execute and count a full **65,536-slot ($2^{16}$-slot) van Oorschot-Wiener (vOW) benchmark** (`ledger()` in [`experiments/r39_claw.py`](experiments/r39_claw.py#L687-L813), reproduced deterministically by `python3 -B experiments/r39_claw.py --ledger`).

### 6.1 vOW Table Parameters and Two-Stage Walk Architecture
- **Table geometry**: $S = 65,536 = 2^{16}$ slots. Each slot stores a 96-bit (**12-byte**) entry `(start_seed32, steps16_meta16, val32)`, totaling $65,536 \times 12 = 786,432\text{ bytes}$ ($768\text{ KiB}$).
- **Distinguished-point predicate**: `dp_bits = 7` (`(val32 & 0x7F) == 0`, hit probability $p_{\text{dp}} = 2^{-7} = 1/128$, mean walk length $128$ steps, cutoff `max_steps = 2048` $= 16 / p_{\text{dp}}$).
- **Stage 1 (Main 7-lane walk)**: All 7 lanes step in lockstep via the 71-op main batch (`67` kernel ops + `2` DP-mask ops + `2` loop ops). Whenever the 2-op packed DP mask triggers, an 18-op handler extracts the hitting lane, probes `table[idx]`, overwrites the slot with the new walk, and if `old.val32 == new.val32` and `old.start != new.start`, queues `(old, new)` for stage-2 path recovery.
- **Stage 2 (Path recovery, `recover_7pairs_packed` in [`experiments/r39_claw.py`](experiments/r39_claw.py#L609-L665))**: Given two walks `(start_A, len_A)` and `(start_B, len_B)` reaching the same distinguished point `val32`, stage 2 advances the longer walk by $|len_A - len_B|$ steps and then advances both walks synchronously until their states collide ($F_{\text{step}}(x_A) = F_{\text{step}}(x_B)$ with $x_A \ne x_B$). If $(x_A \oplus x_B) \ \& \ 1 == 1$ (opposite LSB parity), then $(a_0, u) = (x_{\text{even}}, x_{\text{odd}})$ is a valid claw satisfying $W_{16}(a_0, u) = \mathtt{0xbca1c321}$.

### 6.2 Three Explicit Stage-2 Recovery Regimes
We account for stage-2 path recovery under three explicit SIMD execution models:
1. **`stream7` (Buffered 7-lane recovery)**: Colliding DP pairs `(old, new)` are buffered until 7 recovery walks are ready, then stepped in parallel across all 7 lanes of the 69-op recovery batch (`100%` lane occupancy, `ceil(total_single_walk_recovery_steps / 7)` batches).
2. **`simd7` (Immediate 2-walk-in-7-lane synchronous recovery)**: Each value match is recovered immediately without buffering across matches: the length-equalization prefix steps 1 lane, and the synchronous lockstep phase steps both walks simultaneously in lanes 0 and 1 of a single 7-lane register (`max(len_A, len_B) - rem_steps` batches per match).
3. **`2lane` (Unbuffered single-lane charging)**: Worst-case charging where even the synchronous two-walk phase is charged as two separate 69-op batches (`len_A + len_B - 2 * rem_steps` batches per match).

### Table 6.1: Empirical 65,536-Slot vOW Benchmark Ledger (`--ledger`)
| Quantity | Measured Value | Per Distinct Claw | Notes |
|---|---:|---:|---|
| Table slots $S$ / `dp_bits` / `max_steps` | $65,536$ / $7$ / $2,048$ | — | $786,432\text{ B}$ DP table ($768\text{ KiB}$) |
| Total stage-1 walk evaluations | $268,435,704$ ($2^{28.0000}$) | $1,982.3627$ | $4\times \mathrm{CV}_1$ tables $\times 2^{26}$ evals |
| Main 7-lane batches (`71` ops/batch) | $38,347,958$ | $283.1947$ | $283.1947 \times 71 = 20,106.82\text{ ops}$ |
| Distinguished-point hits (`dp_hits`) | $2,092,676$ | $15.4541$ | $18\text{ ops/hit}$ handler $= 278.17\text{ ops}$ |
| `val32` matches triggering stage 2 | $330,778$ | $2.4428$ | Queued for stage-2 trail recovery |
| Raw opposite-parity claws recovered | $162,983$ | $1.2036$ | $26\text{ ops/claw}$ `recover_a1` $= 31.29\text{ ops}$ |
| **Deduplicated distinct claws `(a0, u)`** | **$135,412$** | **$1.0000$** | Unique `(a0, u)` pairs ($83.08\%$ unique) |
| Stage-2 batches (`stream7`, `69` ops/batch) | $10,568,425$ | $78.0464$ | $78.0464 \times 69 = 5,385.20\text{ ops}$ |
| Stage-2 batches (`simd7`, `69` ops/batch) | $27,708,681$ | $204.6250$ | $204.6250 \times 69 = 14,119.13\text{ ops}$ |
| Stage-2 batches (`2lane`, `69` ops/batch) | $55,558,869$ | $410.2950$ | $410.2950 \times 69 = 28,310.36\text{ ops}$ |
| Non-kernel overhead ops (DP + `recover_a1` + filter) | $43,477,620$ | $321.0766$ | $278.17 + 31.29 + 11.60 + 0.01\text{ ops}$ |
| **Total word ops / distinct claw (`stream7`)** | — | **$25,813.10\text{ ops}$** | $9.1796\text{ compressions} = 2^{3.19843}$ |
| **Total word ops / distinct claw (`simd7`)** | — | **$34,547.02\text{ ops}$** | **$12.2856\text{ compressions} = 2^{3.61889}$** |
| **Total word ops / distinct claw (`2lane`)** | — | **$48,738.26\text{ ops}$** | $17.3322\text{ compressions} = 2^{4.11539}$ |

---

## 7. Exact Prefix Probabilities and 64-Seed Zero-Stall Tail Study

Once a distinct claw $(a_0, u)$ satisfies $W_{16}(a_0, u) = g = \mathtt{0xbca1c321}$, it must pass three successive events to yield a full 39-step collision:
1. **Row 8 (`in_F8`) and Row 9 (`in_F9`) side conditions ($p_8 \cdot p_9$)**:
   - In the message schedule at steps 23 and 24, $\Delta W_{23} = 0$ and $\Delta W_{24}$ require $W_8$ and $W_9$ to produce the exact modular $\sigma_0$-differences of the Table 23 dense base (`in_F8` and `in_F9` in [`experiments/r39_claw.py`](experiments/r39_claw.py#L178-L188)):
     $$\operatorname{in\_F8}(W_8) \iff \sigma_0(W_8 + D_8) - \sigma_0(W_8) \equiv T_8 \pmod{2^{32}}, \qquad D_8 = \mathtt{0x40000000}, \; T_8 = \mathtt{0x087ff000},$$
     $$\operatorname{in\_F9}(W_9) \iff \sigma_0(W_9 + D_9) - \sigma_0(W_9) \equiv T_9 \pmod{2^{32}}, \qquad D_9 = \mathtt{0xf7801000}, \; T_9 = \mathtt{0xffff0df0}.$$
   - Exhaustive enumeration over all $2^{32}$ 32-bit words gives:
     $$p_8 = \Pr_{w}[\operatorname{in\_F8}(w)] = \frac{301,989,888}{2^{32}} = \frac{9}{128} = 2^{-3.830075}, \qquad p_9 = \Pr_{w}[\operatorname{in\_F9}(w)] = \frac{68,157,440}{2^{32}} = \frac{65}{4096} = 2^{-5.977632}.$$
   - Because $W_9 = c_{9,0} - a_1(a_0, u)$ and $W_8 = c_{8,w} - e_4(a_0, a_1) - \operatorname{CH}(E_{\text{base}}[11], E_{\text{base}}[10], e_5(a_1))$ are evaluated on $(a_0, a_1)$, a staged filter checks `in_F9(W9)` first (11 ops, passing with probability $65/4096$), then evaluates $W_8$ and checks `in_F8(W8)` (28 ops), and only on joint passes ($p_8 \cdot p_9 = 585 / 524,288 = 2^{-9.807707}$) reconstructs $W_{17}$ (140 ops), giving an average filter cost of $11 + \frac{65}{4096} \times 28 + \frac{585}{524,288} \times 140 = 11.60\text{ ops}$ per claw.
   - **Direct empirical check on vOW-recovered claws**: Across the $135,412$ distinct claws recovered by our live vOW benchmark, $150$ claws passed both `in_F8(W8)` and `in_F9(W9)` unconditionally, versus $135,412 \times (585 / 524,288) = 151.10$ expected (**ratio $0.9927$**, confirming zero negative correlation between $F_{\text{step}}$ walk collisions and the row-8/9 side conditions).
2. **Row 16 (`G16`) and Row 17 (`G17`) exact transition ($p_{17} = 2^{-32.0}$)**:
   - Exact bit-by-bit enumeration (`solve_row_exact` in [`experiments/r39_claw.py`](experiments/r39_claw.py#L293-L360) and [`run_tail_sfs_experiment`](experiments/r39_claw.py#L964-L974)) proves that $G_{16} = \{\mathtt{0xbca1c121}, \mathtt{0xbca1c321}\}$ ($|G_{16}| = 2$) and that $g = \mathtt{0xbca1c321}$ ($W_{16}' = \mathtt{0xb421d321}$) is the **unique** row-16 word for which the row-17 fiber $G_{17}(W_{16})$ is non-empty, with a **single** valid word pair (`|G17(0xbca1c321)| = 1`):
     $$(W_{17}, W_{17}') = (\mathtt{0x71e9ba98}, \mathtt{0x31e9ba98}).$$
   - Since $W_{17} = \sigma_1(W_{15}) + W_{10} + \sigma_0(W_2(a_0, a_1)) + u \pmod{2^{32}}$ is unconstrained by the claw search on $W_{16}$, hitting $W_{17} = \mathtt{0x71e9ba98}$ occurs with probability $p_{17} = 2^{-32.0}$.
3. **Tail Rows 18..38 ($p_{\text{tail}} \ge 2^{-76.55}$, 64-seed zero-stall SMC study)**:
   - Conditioning on $W_{16} = \mathtt{0xbca1c321}$, $W_{17} = \mathtt{0x71e9ba98}$, and `in_F8(W8) && in_F9(W9)`, the remaining active rows are steps $18 \dots 38$. Following the accepted event of ePrint 2026/1120 and `f86da3c1`, row 20 is evaluated on exact signed modular differences while rows $18, 19, 21, 22, 23$ enforce the exact bitwise conditions of Table 23 (`ROW_MASKS` and `CONDS_16_18_23`), and row 38 checks full 8-word digest equality $\operatorname{sha256\_r39\_compress}(\mathrm{CV}_1, M_1) == \operatorname{sha256\_r39\_compress}(\mathrm{CV}_1, M_1')$.
   - Why did `f86da3c1` suffer a stalled seed (`1/20` stalled at $N = 4,096$ particles)? Because row 19 has survival probability $\approx 2^{-13.35}$, so $N = 4,096 = 2^{12}$ particles have mean $0.39$ survivors at row 19, causing $\approx e^{-0.39} \approx 68\%$ single-stage extinction unless amplified.
   - Using $N = 16,384 = 2^{14}$ particles per stage across **64 independent seeds** (`seeds 1..64` in `bench_t23.c`), **all 64 seeds completed with zero stalls (`64 / 64`, `0` stalls)**, producing verified 39-step colliding message pairs on every seed:
     - Mean of $\log_2 \hat{p}_{\text{tail}}$ across 64 seeds: **$-76.335945$**
     - Sample standard deviation of $\log_2 \hat{p}_{\text{tail}}$: **$0.678879$** (standard error $0.678879 / \sqrt{64} = 0.084860$)
     - $\log_2(\text{mean}(\hat{p}_{\text{tail}}))$ across 64 seeds: **$-76.183798$**
     - One-sided 99% Student-$t$ lower confidence bound ($t_{0.99, 63} = 2.386$): $-76.335945 - 2.386 \times 0.084860 = -76.5384$
     - Adopted conservative lower bound: **$p_{\text{tail}} = 2^{-76.55}$**.

### Table 7.1: Per-Claw Success Probability and Required Distinct Claws
| Factor | Exact / Conservative Value | $\log_2$ Value | Evidence & Method |
|---|---:|---:|---|
| Row-8 side condition $p_8$ (`in_F8`) | $301,989,888 / 2^{32} = 9/128$ | $-3.830075$ | Exhaustive over all $2^{32}$ words $W_8$ |
| Row-9 side condition $p_9$ (`in_F9`) | $68,157,440 / 2^{32} = 65/4096$ | $-5.977632$ | Exhaustive over all $2^{32}$ words $W_9$ |
| Combined side conditions $p_8 \cdot p_9$ | $585 / 524,288$ | $-9.807707$ | Exhaustive + verified on $135,412$ vOW claws |
| Row-17 exact transition $p_{17}$ | $1 / 2^{32}$ | $-32.000000$ | Unique pair $\mathtt{0x71e9ba98} \in G_{17}(\mathtt{0xbca1c321})$ |
| Tail rows $18..38$ ($p_{\text{tail}}$, 99% LCB) | $2^{-76.55}$ | $-76.550000$ | 64-seed SMC ($N=16,384$, **0 stalls**; mean $-76.18$) |
| **Total per-claw probability $p_{\text{claw}}$** | **$2^{-118.357707}$** | **$-118.357707$** | Product $p_8 \cdot p_9 \cdot p_{17} \cdot p_{\text{tail}}$ |
| Poisson amplification $\lambda = -\ln(1 - 0.39)$ | $0.49429635$ | $-1.016552$ | Target success probability $\ge 0.39$ |
| **Required distinct claws $N_{\text{claws}} = \lambda / p_{\text{claw}}$** | **$2^{117.341155}$** | **$117.341155$** | $\approx 3.38 \times 10^{35}$ distinct claws |

---

## 8. Total Work Accounting and Memory Breakdown

With $S = 65,536$ slots and $2^{26} = 67,108,864$ walk evaluations per first-block chaining value $\mathrm{CV}_1$, each $\mathrm{CV}_1$ yields on average $135,412 / 4 = 33,853.0$ distinct claws ($2^{15.047}$ distinct claws per $\mathrm{CV}_1$).
Thus the attack processes $N_{\text{FB}} = 2^{117.341155} / 33,853.0 = 2^{102.294}$ random first blocks $M_0$.
Each first block $M_0$ costs 1 target compression plus per-$\mathrm{CV}_1$ constant setup (`260` ops total, or $260 / 33,853 = 0.0077$ ops per distinct claw, explicitly included in `cv_refresh_ops` in [`experiments/r39_claw.py`](experiments/r39_claw.py#L719)).

### Table 8.1: Total Work Across the Three Stage-2 Recovery Regimes
| Recovery Regime | Ops / Distinct Claw | Compressions / Claw ($\div 2812$) | $\log_2(\text{Compressions / Claw})$ | Total Work $\log_2 T$ |
|---|---:|---:|---:|---:|
| `stream7` (7-lane buffered recovery) | $25,813.10$ | $9.17962$ | $+3.19843$ | $120.5396$ |
| **`simd7` (2-walk-in-7-lane immediate)** | **$34,547.02$** | **$12.28557$** | **$+3.61889$** | **$120.9600$** |
| `2lane` (unbuffered 1-walk per batch) | $48,738.26$ | $17.33224$ | $+4.11539$ | $121.4565$ |
| **Claimed Headline Bound (`claim.json`)** | — | — | — | **$121.0700$** |

Our claimed time bound **`time_log2 = 121.07`** includes a **`+0.11`-bit safety margin** above the fully counted `simd7` regime ($120.9600$) and a **`+0.53`-bit margin** above the buffered `stream7` regime ($120.5396$).

### Table 8.2: Peak Resident Memory Breakdown (`memory_log2_bytes = 20`)
| Component | Exact Size (Bytes) | Notes |
|---|---:|---|
| vOW Distinguished-Point Table ($65,536 \times 12\text{ B}$) | $786,432$ | 65,536 slots $\times$ 96 bits (`start32`, `meta32`, `val32`) |
| Straight-line program code ($\le 512 \times 36\text{ B}$) | $18,432$ | 67-op kernel + stage-1/2 control & handlers |
| 64-register 256-bit register file ($64 \times 32\text{ B}$) | $2,048$ | Architectural register state |
| Table 23 dense base, row masks, and scratch buffers | $16,384$ | Includes 584-byte base + recovery buffer |
| **Total Peak Resident Memory** | **$823,296$** | **$< 1,048,576\text{ bytes}$ ($2^{20}\text{ bytes}$, $78.5\%$ of $1\text{ MiB}$)** |

Because $823,296 < 2^{20} = 1,048,576$, the attack satisfies `memory_log2_bytes = 20` with $225,280\text{ bytes}$ ($220\text{ KiB}$) of spare headroom and incurs **zero memory penalty** under the Pareto objective $\mathrm{Score} = \text{time\_log2} + \max(0, \text{memory\_log2\_bytes} - 20) = 121.07$.

---

## 9. Addressing Every Refutation Flaw of Prior 39-Step Submissions

1. **No external runtime DFS solver (`2^20` vs `2^21` memory)**: Prior submission `f86da3c1` ran a 1.14 MiB DFS solver online, pushing memory to $2^{21}\text{ bytes}$ ($+1.0$ penalty). We embed the 584-byte Table 23 dense base directly and verify it in $O(1)$ space, keeping total memory at $823,296\text{ bytes} < 2^{20}\text{ bytes}$.
2. **Fully traced and counted stage-2 recovery and table overhead**: Prior submissions `6807f974` and `f86da3c1` estimated DP and recovery overhead at `22.4` ops without tracing stage-2 walks. We execute the complete two-stage vOW cycle across $268,435,704$ evaluations and count every main batch, recovery batch (`stream7`, `simd7`, `2lane`), DP probe, `recover_a1`, and side-condition filter.
3. **Deduplicated distinct claws**: We count only **distinct** recovered pairs $(a_0, u)$ ($135,412$ distinct out of $162,983$ raw claws, $83.08\%$), absorbing all within-table duplicate walk collisions into the empirical rate of $34,547.02\text{ ops}$ per distinct claw.
4. **Zero-stall 64-seed tail estimation**: By increasing the SMC particle population to $N = 16,384$ across 64 independent seeds, we achieve **64 / 64 completed seeds (`0` stalls)** and use the 99% Student-$t$ lower confidence bound ($2^{-76.55}$ vs point estimate $2^{-76.18}$).
5. **Real colliding message pairs and packed stage-2 recovery in organizer experiments**: Whereas `f86da3c1` returned `0` message pairs (`[None, None]`) and only checked scalar algebra, our [`experiments/r39_claw.py`](experiments/r39_claw.py) executes the register-allocated 67-op 7-lane kernel and packed stage-2 trail recovery (`recover_7pairs_packed`) on every active trial of `r39-claw-vow` and returns **16 verified 39-step semi-free-start colliding pairs** in `r39-tail-sfs`.

---

## 10. Heuristics and Evidence Inventory (`claim.json`)

- **`H1-bipartite-claw-fixed-target`**: Success probability on the unique valid row-16 target word $g = \mathtt{0xbca1c321}$ matches the marginal product over distinct vOW claws. Supported by Lemma 2.1, Lemma 3.1, and `experiment:r39-claw-vow` (Section 2, lines 19-48; Section 3, lines 51-63; Section 11, lines 257-261).
- **`H2-packed-7lane-machine-model`**: 64-register 256-bit word-RAM packing 7 lanes of 36 bits (`C_BLOCK = 2812`, `step_ops_folded = 67`, `13` peak live registers, `0` spills). Supported by Section 5 (lines 82-129) and `experiment:r39-claw-vow`.
- **`H3-vow-distinct-claw-amortization`**: The 65,536-slot ($768\text{ KiB}$) vOW walk with `dp_bits = 7` produces one deduplicated distinct claw per $34,547.02$ word operations ($12.2856$ compressions) under `simd7` ($25,813.10$ ops under `stream7`), including all stage-1, stage-2 recovery, and handler operations. Supported by Section 6 (lines 132-165), Section 8 (lines 207-233), and `experiment:r39-claw-vow`.
- **`H4-side-condition-independence`**: Row-8 ($p_8 = 9/128$) and row-9 ($p_9 = 65/4096$) side conditions hold with joint probability $p_8 \cdot p_9 = 585 / 524,288 = 2^{-9.807707}$ conditionally on vOW-recovered claws. Verified exhaustively over $2^{32}$ inputs and empirically on $135,412$ vOW claws ($150$ observed vs $151.10$ expected, ratio $0.9927$; Section 7, lines 168-178; `experiment:r39-claw-vow`, `experiment:r39-tail-sfs`).
- **`H5-tail-rows-18-to-38-smc`**: Conditional on $W_{16} = \mathtt{0xbca1c321}$, $W_{17} = \mathtt{0x71e9ba98}$, and rows 8..9, the tail probability across steps $18 \dots 38$ (with row 20 on signed modular differences) is at least $p_{\text{tail}} = 2^{-76.55}$ (99% Student-$t$ LCB from 64 zero-stall SMC runs at $N = 16,384$; mean $2^{-76.1838}$; Section 7, lines 179-204; `experiment:r39-tail-sfs`).
- **`H6-inter-claw-poisson-amplification`**: Generating $N_{\text{claws}} = 2^{117.341155}$ deduplicated distinct claws across $2^{102.294}$ independent first blocks $M_0$ achieves collision success probability at least $1 - e^{-\lambda} = 0.39$ ($\lambda = 0.49429635$). Supported by Section 7 (lines 193-204) and Section 8 (lines 207-233).

---

## 11. Organizer Experiments and Reproducibility (`experiments/r39_claw.py`)

Both declared experiments in [`experiments/manifest.json`](experiments/manifest.json) invoke [`experiments/r39_claw.py`](experiments/r39_claw.py) under the 256-trial `python-message-pairs-v1` protocol (`ACTIVE_TRIALS = 16`, keeping JSON output under `21 KiB < 32 KiB` and runtime under `0.3s`):
1. **`r39-claw-vow`** ([`run_claw_vow_experiment`](experiments/r39_claw.py#L861-L961)): Across 256 protocol trials (trials `0..15` active, trials `16..255` returning `message_a_hex=None, message_b_hex=None`), derives $M_0$ and $\mathrm{CV}_1 = \operatorname{sha256\_r39\_compress}(\mathrm{IV}, M_0)$ from SHAKE-256 of the experiment id and trial seed, compiles and runs the register-allocated 67-op 7-lane kernel across 16 batches (`112` lanes per active trial, `1,792` lanes total; `step_ops_folded = 67`, `peak_live_regs = 13`, `mismatches = 0`), tests 256 seeded $(a_0, a_1)$ candidates per active trial (`4,096` total) against the fast `W8`/`W9` recurrence and `in_F8`/`in_F9` filter (`5` passes observed vs `4.57` expected at $585/524,288$), runs packed 7-lane stage-2 trail recovery (`recover_7pairs_packed`) on the $t$-th embedded SFS claw (`stage2_recovered = 1`, `W16 = 0xbca1c321`), and returns a distinct 128-byte two-block variant pair $(M_0 \| M_1, M_0 \| M_1')$ (`returned_pairs = 16`, `repeated_pairs = 0`, `full_collisions = 0` from the standard IV).
2. **`r39-tail-sfs`** ([`run_tail_sfs_experiment`](experiments/r39_claw.py#L964-L996)): Across 256 protocol trials (trials `0..15` active, trials `16..255` returning `None`), runs the exact bit-by-bit row solver (`solve_row_exact`) on the Table 23 dense base to verify $|G_{16}| = 2$ (`row16_exact_count = 2`) and $|G_{17}(\mathtt{0xbca1c321})| = 1$ (`row17_exact_count = 1`, $W_{17} = \mathtt{0x71e9ba98}$), reconstructs and verifies all 16 embedded bipartite-claw 39-step SFS colliding pairs in `PAIR_CLAW_SFS` (`claw_verified = 1`, `sfs_collision_verified = 1`, `mismatches = 0`), and returns the 16 verified 96-byte SFS colliding pairs $(\mathrm{CV}_1 \| M_1, \mathrm{CV}_1 \| M_1')$ (`returned_pairs = 16`, `repeated_pairs = 0`, `full_collisions = 0` from the standard IV).
