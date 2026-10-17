# Ordinary Two-Block Collision Attack on 39-Step SHA-256 (`sha256-r39-prefix-v1`) via Bipartite Claw Search

## 1. Target Profile, Attack Overview, and Headline Claim

We present a complete, memory-bounded ordinary two-block collision attack on **39-step SHA-256** (`sha256-r39-prefix-v1`):
- **Target definition**: Standard SHA-256 initial chaining value $\mathrm{IV}$ applied once before block 0; steps $r = 0, \dots, 38$ (the first 39 steps of SHA-256) applied to each 512-bit padded block with Davies-Meyer feed-forward $\mathrm{CV}_{i+1} = \mathrm{CV}_i + \operatorname{State}_{39}(\mathrm{CV}_i, B_i) \pmod{2^{32}}$; standard FIPS 180-4 padding; equality on all eight 32-bit digest words; output consists of two distinct 128-byte (two-block) messages $M_0 \| M_1 \ne M_0 \| M_1'$ whose second-block chaining values collide ($\mathrm{CV}_2 = \mathrm{CV}_2'$), so the identical FIPS 180-4 padding block preserves equality across all eight digest words.
- **Headline resource bounds**:
  - **Total work**: $T \le 2^{121.30}$ target compressions ($C = 2812$ 256-bit word operations per 39-step compression under `collision-frontier-v5`). This conservative headline bound covers all three Stage-1/Stage-2 execution regimes—with Stage-2 control overhead (`+8` ops/batch for `simd7`, `+29` ops/batch for `stream7`) and per-window first-block compression (`2812 + 260 = 3072` ops per $2^{26}$ window) explicitly included:
    - **7-lane buffered Stage-2 recovery (`stream7`, 74-op SWAR Stage-1, 98-op Stage-2)**: $28,926.12\text{ ops/claw} = 10.2867\text{ compressions} \implies T = 2^{120.7039}$.
    - **2-walk-in-7-lane immediate Stage-2 recovery (`simd7`, 74-op SWAR Stage-1, 77-op Stage-2)**: $37,033.69\text{ ops/claw} = 13.1699\text{ compressions} \implies T = 2^{121.0603}$.
    - **2-walk-in-7-lane immediate Stage-2 recovery (`simd7_unpacked`, 96-op unpacked Stage-1, 77-op Stage-2)**: $43,263.97\text{ ops/claw} = 15.3855\text{ compressions} \implies T = 2^{121.2847}$.
  - **Resident memory**: $M \le 823,296\text{ bytes} < 2^{20}\text{ bytes}$ ($1\text{ MiB}$), so $\log_2 M = 20$ and the Pareto memory penalty is $\max(0, 20 - 20) = 0$.
  - **Combined Pareto score**: $\mathrm{Score} = 121.30 + \max(0, 20 - 20) = 121.30$, improving on the accepted 39-step generic birthday baseline (`124.83147`) by **3.53 bits** ($11.6\times$).
  - **Preprocessing**: $2^{36}$ target compressions (one-time Table 23 characteristic and dense-base derivation, derived explicitly in Section 4.2 and negligible against $2^{121.30}$).
  - **Non-uniform advice**: $\le 2^{11}\text{ bytes}$ ($584\text{ bytes}$ for the 39-step Table 23 dense base and row conditions, or $1,800\text{ bytes}$ including embedded verification witnesses).
  - **Success probability**: $\ge 0.39$ ($\lambda = -\ln(1 - 0.39) = 0.49429635$).

All code, constants, traced instruction schedules (`67`-op Stage-2 kernel and `71`-op Stage-1 SWAR DP kernel), register allocations (`14` peak live registers, `0` spills in 64 registers), exhaustive active-bit theorems for $\mathcal{F}_8$ and $\mathcal{F}_9$, live unselected vOW + full-32-bit claw verification across 16 independent first blocks, strictly fixed-budget GF(2)-subspace Sequential Monte Carlo (SMC) replicas, and live downward semi-free-start (SFS) collision inversion are self-contained in [`experiments/r39_claw.py`](experiments/r39_claw.py) and verified via `python3 -B experiments/r39_claw.py --selftest` and `--ledger`.

---

## 2. Why Direct A0-Variant Enumeration Fails at 39 Steps and How the Bipartite Claw Solves Row 16

In the two-block framework of Mendel, Nad, and Schläffer (EUROCRYPT 2013; IACR ePrint 2015/350) and ePrint 2026/1120 (Table 21 / Table 23), a 39-step local collision spans steps $r = 8, \dots, 26$ with active message words at steps $8, 9, 10, 11, 12, 16, 17, 24, 26$ and zero differences on steps $0, \dots, 7$ and $27, \dots, 38$.
Because the Table 23 dense base fixes the state words $(A_r, E_r)$ for $r \in \{2, \dots, 15\}$ (`BASE_A0[6..19]`, `BASE_E0[6..19]`, `BASE_A1[6..19]`, `BASE_E1[6..19]`) and message words $W_r$ for $r \in \{10, \dots, 15\}$ (including $W_{14} = \mathtt{0x43660040}$, $W_{15} = \mathtt{0x4891771f}$), the free prefix degrees of freedom before step 2 are parameterized by $(a_0, a_1) = (A_0, A_1)$.
For a chaining value $\mathrm{CV}_1 = (\mathrm{cv}_0, \dots, \mathrm{cv}_7)$ produced by a random first block $M_0$:
1. In a naive $\mathcal{A}_0$-variant sweep (used at 37 and 38 steps), $W_{16}$ depends simultaneously on $(a_0, a_1)$ and $\mathrm{CV}_1$, while exact bit-by-bit enumeration (`solve_row_exact` in [`experiments/r39_claw.py`](experiments/r39_claw.py#L401-L466)) shows that $|G_{16}| = 2$ ($\{\mathtt{0xbca1c121}, \mathtt{0xbca1c321}\}$) and only a **single** row-16 word $g = \mathtt{0xbca1c321}$ has a non-empty row-17 fiber $G_{17}(g) = \{\mathtt{0x71e9ba98}\}$.
2. Hitting $W_{16} = g$ by forward trials costs $2^{32}$ evaluations per hit. Instead, re-parameterizing $(a_0, a_1)$ by $(a_0, u)$ where $u = W_1$ separates $W_{16}$ into an additive bipartite claw equation.

### Lemma 2.1 (Exact Bipartite Claw Decomposition of $W_{16}$ and Closed-Form Prefix Reconstruction)
In the state array convention of [`experiments/r39_claw.py`](experiments/r39_claw.py#L225-L317), indices $0, 1, 2, 3$ of `A[m][0..42]` and `E[m][0..42]` hold $\mathrm{CV}_1$ in reverse order (`A[m][3 - j] = cv[j]`, `E[m][3 - j] = cv[4 + j]` for $j = 0, 1, 2, 3$), and step $r \ge 0$ produces `A[m][r + 4]` and `E[m][r + 4]` using message word `W[m][r]`.
For any chaining value $\mathrm{CV}_1 = (\mathrm{cv}_0, \dots, \mathrm{cv}_7)$ and any pair $(a_0, u) \in (\mathbb{Z}/2^{32}\mathbb{Z})^2$, define:
$$t_{2,0} = \Sigma_0(\mathrm{cv}_0) + \operatorname{MAJ}(\mathrm{cv}_0, \mathrm{cv}_1, \mathrm{cv}_2) \pmod{2^{32}}, \qquad e_{0,\text{base}} = \mathrm{cv}_3 - t_{2,0} \pmod{2^{32}},$$
$$k_0 = -t_{2,0} - \mathrm{cv}_7 - \Sigma_1(\mathrm{cv}_4) - \operatorname{CH}(\mathrm{cv}_4, \mathrm{cv}_5, \mathrm{cv}_6) - K_0 \pmod{2^{32}}, \qquad c_{9,0} = W_9^{\text{base}} + A_{\text{base}}[5] \pmod{2^{32}},$$
and set $e_0(a_0) = a_0 + e_{0,\text{base}} \pmod{2^{32}}$ and
$$a_1(a_0, u) = \operatorname{recover\_a1}(a_0, u, \mathrm{CV}_1) = u + \Sigma_0(a_0) + \operatorname{MAJ}(a_0, \mathrm{cv}_0, \mathrm{cv}_1) + \Sigma_1(e_0(a_0)) + \operatorname{CH}(e_0(a_0), \mathrm{cv}_4, \mathrm{cv}_5) + \mathrm{cv}_6 + K_1 \pmod{2^{32}}.$$
Then inverting steps $0 \dots 15$ (`build_variant(cv, a0, a1)` and `closed_form_w8_w9_w17` in [`experiments/r39_claw.py`](experiments/r39_claw.py#L273-L317)) determines $W_0, \dots, W_{15}$ uniquely with probability 1 such that:
1. $W_0 = a_0 + k_0 \pmod{2^{32}}$ depends only on $a_0$ and $\mathrm{CV}_1$.
2. $W_1 = u \pmod{2^{32}}$ equals the parameter $u$.
3. $W_9 = c_{9,0} - a_1(a_0, u) \pmod{2^{32}}$, $W_8 = E_{\text{base}}[12] - A_{\text{base}}[8] - e_4(a_0, a_1) - \Sigma_1(E_{\text{base}}[11]) - \operatorname{CH}(E_{\text{base}}[11], E_{\text{base}}[10], e_5(a_1)) - K_8 \pmod{2^{32}}$, and $W_{14} = W_{14}^{\text{base}} = \mathtt{0x43660040}$.
4. In the SHA-256 message schedule at step 16, $W_{16} = \sigma_1(W_{14}) + W_9 + \sigma_0(W_1) + W_0 \pmod{2^{32}}$ satisfies:
   $$W_{16}(a_0, u) = g + \bigl(\sigma_0(u) - u\bigr) - F_{\text{even}}(a_0, \mathrm{CV}_1) \pmod{2^{32}},$$
   where $c_{\text{walk}} = g - \sigma_1(W_{14}^{\text{base}}) - c_{9,0} - k_0 + \mathrm{cv}_6 + K_1 \pmod{2^{32}}$ and
   $$F_{\text{even}}(a_0, \mathrm{CV}_1) = c_{\text{walk}} + \Sigma_0(a_0) + \operatorname{MAJ}(a_0, \mathrm{cv}_0, \mathrm{cv}_1) + \Sigma_1(e_0(a_0)) + \operatorname{CH}(e_0(a_0), \mathrm{cv}_4, \mathrm{cv}_5) - a_0 \pmod{2^{32}}.$$
5. Furthermore, at step 17, $W_{17}(a_0, u) = \sigma_1(W_{15}^{\text{base}}) + W_{10}^{\text{base}} + \sigma_0(W_2(a_0, a_1)) + u \pmod{2^{32}}$, where $W_2(a_0, a_1) = A_{\text{base}}[6] - \Sigma_0(a_1) - \operatorname{MAJ}(a_1, a_0, \mathrm{cv}_0) - \mathrm{cv}_5 - \Sigma_1(e_1) - \operatorname{CH}(e_1, e_0, \mathrm{cv}_4) - K_2 \pmod{2^{32}}$ and $e_1 = \mathrm{cv}_2 + a_1 - \Sigma_0(a_0) - \operatorname{MAJ}(a_0, \mathrm{cv}_0, \mathrm{cv}_1) \pmod{2^{32}}$.

**Proof.**
1. At step $r = 0$ (`idx = 4`), `t1 = A[0][4] - t2_0 = a0 - t2_0`, so `E[0][4] = cv[3] + a0 - t2_0 = a0 + e0_base` and `W[0][0] = t1 - cv[7] - S1(cv[4]) - CH(cv[4], cv[5], cv[6]) - K39[0] = a0 + k0 (mod 2^32)`.
2. At step $r = 1$ (`idx = 5`), `t2_1 = S0(a0) + MAJ(a0, cv[0], cv[1])` and `t1_1 = a1 - t2_1`, so `E[0][5] = cv[2] + t1_1` and `W[0][1] = t1_1 - cv[6] - S1(e0) - CH(e0, cv[4], cv[5]) - K39[1] = u (mod 2^32)` by definition of `recover_a1(a0, u, wp)`.
3. At step $r = 2$ (`idx = 6`), `t2_2 = S0(a1) + MAJ(a1, a0, cv[0])` and `t1_2 = BASE_A0[6] - t2_2`, giving the exact formula for `W[0][2]` and hence $W_{17} = \sigma_1(W_{15}) + W_{10} + \sigma_0(W_2) + W_1 \pmod{2^{32}}$.
4. At steps $r = 4, 5, 8, 9$, `A[0][6..9]` and `E[0][10..13]` are fixed by `BASE_A0` and `BASE_E0`, giving `e5 = a1 + BASE_A0[9] - t2_5`, `e4 = a0 + BASE_A0[8] - t2_4`, and the exact closed-form expressions for $W_8$ and $W_9 = c_{9,0} - a_1$.
5. Substituting `W[0][14] = BASE_W0[14]`, `W[0][9] = c9_0 - a1`, `W[0][1] = u`, and `W[0][0] = a0 + k0` into $W_{16} = \sigma_1(W_{14}) + W_9 + \sigma_0(W_1) + W_0 \pmod{2^{32}}$ yields $W_{16}(a_0, u) = g + (\sigma_0(u) - u) - F_{\text{even}}(a_0, \mathrm{CV}_1) \pmod{2^{32}}$. $\square$

---

## 3. Bipartite Walk Function $F_{\text{step}}$ and Exact Domain Isolation

To solve $F_{\text{even}}(a_0, \mathrm{CV}_1) \equiv \sigma_0(u) - u \pmod{2^{32}}$ for the unique valid row-16 target word $g = \mathtt{0xbca1c321}$ using a distinguished-point walk (van Oorschot-Wiener, CCS 1994), we define a single step function $F_{\text{step}} : \{0, 1\}^{32} \to \{0, 1\}^{32}$ partitioned by the least significant bit $(x \bmod 2)$ of the input $x \in \{0, 1\}^{32}$ ([`experiments/r39_claw.py`](experiments/r39_claw.py#L243-L256)):
$$F_{\text{step}}(x) = \begin{cases}
c_{\text{walk}} + \Sigma_0(x) + \operatorname{MAJ}(x, \mathrm{cv}_0, \mathrm{cv}_1) + \Sigma_1(e_0(x)) + \operatorname{CH}(e_0(x), \mathrm{cv}_4, \mathrm{cv}_5) - x \pmod{2^{32}} & \text{if } (x \bmod 2) = 0 \text{ (even: } x = a_0\text{)}, \\
\sigma_0(x) - x \pmod{2^{32}} & \text{if } (x \bmod 2) = 1 \text{ (odd: } x = u\text{)}.
\end{cases}$$

### Lemma 3.1 (Opposite-Parity Walk Collision $\implies$ Exact Row-16 Claw)
For any even $a_0 \in \{0, 1\}^{32}$ ($(a_0 \bmod 2) = 0$) and any odd $u \in \{0, 1\}^{32}$ ($(u \bmod 2) = 1$), setting $a_1 = \operatorname{recover\_a1}(a_0, u, \mathrm{CV}_1)$ gives:
$$F_{\text{step}}(a_0) = F_{\text{step}}(u) \iff F_{\text{even}}(a_0, \mathrm{CV}_1) \equiv \sigma_0(u) - u \pmod{2^{32}} \iff W_{16}(a_0, u) = g = \mathtt{0xbca1c321}.$$
Every opposite-parity walk collision $(a_0, u)$ therefore satisfies $W_{16}(a_0, u) = \mathtt{0xbca1c321}$ with **100% algebraic certainty** (`mismatches = 0` across all `162,983` raw claws and `135,412` distinct claws in our 64K-slot benchmark, all live full-32-bit claws and 16 multi-step vOW DP trails in `r39-claw-vow`, and all 17 SFS witnesses in `PAIR_CLAW_SFS`). $\square$

---

## 4. Self-Contained Table 23 Dense Base, Preprocessing Bound, and Live Downward SFS Inversion

### 4.1 Embedded Dense Base and Zero Online Solver Memory
Unlike submission `f86da3c1`, which invoked an external depth-first search (DFS) solver allocating $1,048,576 + 94,483 = 1,143,059\text{ bytes}$ at runtime (exceeding the $2^{20}\text{ byte}$ zero-penalty threshold and incurring a $+1.0\text{ bit}$ Pareto memory penalty), our submission embeds the complete verified 39-step Table 23 dense base directly as static 32-bit word tuples in [`experiments/r39_claw.py`](experiments/r39_claw.py#L37-L185):
- `BASE_A0[0..19]`, `BASE_E0[0..19]`, `BASE_A1[0..19]`, `BASE_E1[0..19]` ($4 \times 20 = 80$ words $= 320\text{ bytes}$, fixing steps $2..15$).
- `BASE_W0[0..15]`, `BASE_W1[0..15]` ($2 \times 16 = 32$ words $= 128\text{ bytes}$).
- `ROW_MASKS` and `CONDS_16_18_23` (exact bitwise masks and conditions for rows $16..26$).
- `VOW_F89_TRAILS[0..15]` (16 real multi-step vOW DP trail collision pairs `(c_idx, seed_a, la, seed_b, lb, dp_val, a0, u)` with $la \ne lb$ and $(\text{dp\_val} \ \& \ \mathtt{0x7F}) = 0$ from the 4-CV $\times 2^{26}$ vOW run).
- `PAIR_CLAW_SFS[0..16]` (17 complete 39-step semi-free-start colliding tuples `(cv_hex, a0, a1)`).

Total non-uniform advice is under $2\text{ KiB}$ ($\le 2^{11}\text{ bytes}$, `nonuniform_advice_log2_bytes = 11`), and online dense-base memory is **zero beyond the embedded constants**.

### 4.2 Explicit Derivation of the One-Time $2^{36}$ Preprocessing Bound
The one-time preprocessing bound `preprocessing_log2 = 36` covers the offline derivation of the 584-byte Table 23 dense base (`BASE_A0/E0/A1/E1`, `BASE_W0/W1`) and row conditions (`ROW_MASKS`, `CONDS_16_18_23`):
1. Starting from the 39-step differential characteristic (Table 23 of ePrint 2026/1120, spanning steps $8 \dots 26$), steps $10 \dots 15$ have 6 message words ($W_{10}, \dots, W_{15}$) and 12 state words ($A_6, \dots, A_{15}, E_6, \dots, E_{15}$) subject to carries and cross-bit conditions.
2. Finding a dense base on steps $2 \dots 15$ such that $G_{16} \ne \emptyset$ and $\bigcup_{g \in G_{16}} G_{17}(g) \ne \emptyset$ searches over $\approx 2^{34}$ local state assignments on steps $6 \dots 15$, each verified by the exact bit-by-bit row-16 and row-17 DFS (`solve_row_exact`, costing $< 4$ compression equivalents per candidate), for a total one-time offline cost of $\le 2^{36}$ target compressions.
3. Once found, this single 584-byte dense base is fixed for all $2^{102.294}$ first blocks $M_0$ in the online attack.

### 4.3 Exact GF(2) Affine Subspaces for Rows $19 \dots 22$ and Live Downward SFS Inversion
In [`experiments/r39_claw.py`](experiments/r39_claw.py#L475-L639), `build_row_subspaces()` constructs the exact affine subspaces over $\mathbb{F}_2^{32}$ for the state word $E_0[r+4]$ at rows $r \in \{19, 20, 21, 22\}$ by solving the linear bitwise equations simultaneously enforcing:
1. The signed modular difference $\Delta E_r = E_0[r+4] - E_1[r+4] \pmod{2^{32}}$ specified by `ROW_MASKS[r]`.
2. The next-step lookahead condition $\Delta \Sigma_1(E_r) + \Delta \operatorname{CH}(E_r, E_{r-1}, E_{r-2}) + \Delta E_{r-3} + \Delta A_{r-3} \equiv \Delta E_{r+1} \pmod{2^{32}}$, where every active bit of $\Sigma_1(\Delta E_r)$ induces a 3-term linear equation $(E_r \gg 6)_j \oplus (E_r \gg 11)_j \oplus (E_r \gg 25)_j = y_j$ over $\mathbb{F}_2$, solved via Gaussian elimination (`solve_gf2_subspace`).

Given any rollout reaching step 38 with $\Delta A_r = \Delta E_r = 0$ for $r \in \{27, \dots, 38\}$ and $W_8 \in \mathcal{F}_8, W_9 \in \mathcal{F}_9$, `invert_rollout_to_sfs(A, E, W)` ([`experiments/r39_claw.py`](experiments/r39_claw.py#L611-L638)) inverts the message schedule downward from $r = 23$ to $16$ ($W_{r-16} = W_r - \sigma_1(W_{r-2}) - W_{r-7} - \sigma_0(W_{r-15}) \pmod{2^{32}}$) and inverts the SHA-256 step equations downward from $r = 9$ to $0$ to produce a complete, self-contained 39-step semi-free-start colliding pair $(\mathrm{CV}_1, M_1, M_1')$ satisfying $F_{\text{step}}(a_0) = F_{\text{step}}(u)$, $W_{16} = \mathtt{0xbca1c321}$, $W_{17} = \mathtt{0x71e9ba98}$, and $\operatorname{sha256\_r39\_compress}(\mathrm{CV}_1, M_1) = \operatorname{sha256\_r39\_compress}(\mathrm{CV}_1, M_1')$.

---

## 5. Packed 7-Lane $\times$ 36-Bit Word-RAM Machine Model and Traced 67/71-Op Kernels

We adopt the exact same 256-bit word-RAM SIMD packing convention used by the accepted Round 39 generic birthday baseline (`8681f9bd`, `shrho.py`) and the Round 39 claw baseline (`f86da3c1`, `clawexp.py`):
- **Word width**: 256 bits, partitioned into **`LANES = 7`** independent lanes at a **`PITCH = 36`-bit** stride (bits $36k \dots 36k+31$ hold lane $k$'s 32-bit value; bits $36k+32 \dots 36k+35$ are a 4-bit guard band).
- **Register file**: **`REGISTERS = 64`** general-purpose 256-bit registers ($64 \times 32 = 2,048\text{ bytes}$).
- **Instruction encoding**: **`INSTR_BYTES = 36`** bytes per instruction (4 bytes opcode/register specifiers + 32 bytes immediate 256-bit constant).
- **39-step compression normalization**: **`C_BLOCK = 2812`** word operations per 39-step compression (`collision-frontier-v5`).

### 5.1 Guard-Band Lane Isolation, 67-Op `F_step` Kernel, and 4-Op SWAR DP Detector
In [`experiments/r39_claw.py`](experiments/r39_claw.py#L644-L896), `Tracer` traces every word-RAM instruction and `build_traced_step(fold_maj, include_dp)` constructs both the 67-op Stage-2 `F_step` kernel and the 71-op Stage-1 kernel (which appends the 4-op SWAR distinguished-point detector):
1. **Exact lane-isolated shifts (`shrho.py` convention)**:
   - Right shift by $n \in \{1, \dots, 31\}$: `(v >> n) & broadcast36((1 << (32 - n)) - 1)` (2 ops: `shr`, `and_c`). Because the mask is `(1 << (32 - n)) - 1`, any guard bits in positions $32..35$ of lane $k$ that shift down into bits $32-n \dots 35-n$ are **masked to zero**, and no bit from lane $k+1$ (starting at bit $36$) can reach bits $0 \dots 31-n$ since $36 - n \ge 5 > 32 - n$.
   - Left shift by $32 - n$ for 32-bit rotation `ror_p(v, n)`: `(v << (32 - n)) & broadcast36(((1 << n) - 1) << (32 - n))` (2 ops: `shl`, `and_c`).
   - Thus every 32-bit rotation `ror_p(v, n)` costs $2 + 2 + 1 = 5$ ops, and every 3-term XOR rotation ($\Sigma_0, \Sigma_1, \sigma_0$) costs $14$ ops ($\sigma_0$) or $17$ ops ($\Sigma_0, \Sigma_1$).
2. **Guard-band-safe $e_0$ addition (1 op)**:
   - We compute `e0 = x + e0_base` in **1 instruction** (`add`) without an explicit `& 0xFFFFFFFF` mask because `e0` is consumed exclusively by `S1(e0)` (whose shift masks zero bits $32..35$) and `CH(e0, c4, c5) = c5 ^ (e0 & (c4 ^ c5))` (where `c4 ^ c5` has zero guard bits in positions $32..35$).
3. **Constant folding for $\operatorname{MAJ}$ and $\operatorname{CH}$ (9 ops total for `MAJ`, `CH`, and `even_pre`)**:
   - $\operatorname{MAJ}(x, \mathrm{cv}_0, \mathrm{cv}_1) = (x \ \& \ (\mathrm{cv}_0 \oplus \mathrm{cv}_1)) \oplus (\mathrm{cv}_0 \ \& \ \mathrm{cv}_1)$ costs **2 ops** (`and`, `xor`; 5 ops unfolded).
   - $\operatorname{CH}(e_0, \mathrm{cv}_4, \mathrm{cv}_5) = \mathrm{cv}_5 \oplus (e_0 \ \& \ (\mathrm{cv}_4 \oplus \mathrm{cv}_5))$ costs **2 ops** (`and`, `xor`; 3 ops unfolded).
   - Summing `even_pre = (c_walk + S0(x) + MAJ + S1(e0) + CH) & 0xFFFFFFFF` costs **5 ops** (`4` `add`s + `1` `and_c`).
4. **Shared subtraction and 2-op parity mask (9 ops)**:
   - `p = x & 1` (`and_c`), `m = p + 0xFFFFFFFF` (`add_c`), `blended = s0_x ^ (m & (s0_x ^ even_pre))` (`3` ops), `neg_x = (x ^ 0xFFFFFFFF) + 1` (`2` ops), `out = (blended + neg_x) & 0xFFFFFFFF` (`2` ops).
5. **Exact 4-op SWAR zero-field distinguished-point detector (`include_dp=True`, 71 traced ops total)**:
   - In Stage 1, we must test whether **any** of the 7 lanes in `out` has its low 7 bits equal to zero (`(out_lane & 0x7F) == 0`).
   - `build_traced_step(fold_maj=True, include_dp=True)` traces the standard 4-instruction SWAR zero-field test across all 7 lanes in parallel:
     $$\text{low7} = \text{out} \ \& \ \operatorname{broadcast36}(\mathtt{0x7F}), \qquad \text{dp\_word} = \bigl((\text{low7} + \operatorname{broadcast36}(\mathtt{0x7F})) \oplus \operatorname{broadcast36}(\mathtt{0x80})\bigr) \ \& \ \operatorname{broadcast36}(\mathtt{0x80}).$$
   - Because $\text{low7} \in [0, 127]$ occupies only bits $0 \dots 6$ of each 36-bit lane, $\text{low7} + \mathtt{0x7F} \in [127, 254]$ never carries beyond bit 7, and bit 7 ($\mathtt{0x80}$) of $\text{low7} + \mathtt{0x7F}$ is $0$ **if and only if** $\text{low7} == 0$. Thus `dp_word != 0` (`1` branch instruction `bnz` after the 4 traced ops, i.e., **`stage1_ops_swar = 5` ops total**) holds **if and only if** at least one of the 7 lanes hit a distinguished point.
   - We also report the **27-op unpacked Stage-1 check** (`stage1_ops_unpacked = 27`: 7 lanes $\times$ (`shr`, `and_c`, `bnz`)), giving `main_batch_ops_unpacked = 67 + 27 + 2 = 96` ops/batch and total work $2^{121.2847}$, which is **also strictly covered by our claimed bound $2^{121.30}$**.
6. **Stage-2 recovery control overhead (`+8` ops/batch in `simd7`, `+29` ops/batch in `stream7`)**:
   - In `simd7` ([`recover_1pair_simd7`](experiments/r39_claw.py#L919-L953)), Phase 1 steps the longer trail in lane 0 (1 batch/step) and Phase 2 steps both trails simultaneously in lanes 0 and 1 (1 batch/step), plus **`stage2_ctrl_ops_simd7 = 8` ops/batch** (`shr 36`, `xor`, `and_c`, `bz` for equality test `fa == fb`, plus `xor`, `and_c`, `bnz`, `mov` for parity check and state update), giving **`rec_batch_ops_simd7 = 67 + 2 + 8 = 77` ops/batch**.
   - In `stream7` ([`recover_7pairs_packed`](experiments/r39_claw.py#L956-L1002)), 7 colliding pairs are buffered and stepped in parallel across all 7 lanes (`stage2_ctrl_ops_stream7 = 29` ops/batch for SWAR 32-bit lane comparison and masked lane retention), giving **`rec_batch_ops_stream7 = 67 + 2 + 29 = 98` ops/batch**.

### Table 5.1: Exact Instruction Breakdown and Register Allocation of `F_step`
| Sub-block | Folded Ops | Unfolded Ops | Live Regs | Notes |
|---|---:|---:|---:|---|
| $\sigma_0(x)$ (`ror(7) ^ ror(18) ^ shr(3)`) | 14 | 14 | 10 | 5+5+2 ops + 2 XORs |
| $\Sigma_0(x)$ (`ror(2) ^ ror(13) ^ ror(22)`) | 17 | 17 | 11 | 5 ops per `ror` + 2 XORs |
| $\operatorname{MAJ}(x, \mathrm{cv}_0, \mathrm{cv}_1)$ | 2 | 5 | 10 | `and`, `xor` (folded) |
| $e_0 = x + e_{0,\text{base}}$ | 1 | 1 | 11 | Guard bits $32..35$ masked by $\Sigma_1$ and $\operatorname{CH}$ |
| $\Sigma_1(e_0)$ (`ror(6) ^ ror(11) ^ ror(25)`) | 17 | 17 | 14 | 5 ops per `ror` + 2 XORs |
| $\operatorname{CH}(e_0, \mathrm{cv}_4, \mathrm{cv}_5)$ | 2 | 3 | 12 | `and`, `xor` (folded) |
| `even_pre = (c_walk + S0 + MAJ + S1 + CH) & 0xFFFFFFFF` | 5 | 5 | 9 | 4 `add` + 1 `and_c` |
| Parity blend + shared `- x` | 9 | 9 | 10 | `p = x & 1`, `m = p + 0xFFFFFFFF`, blend, `- x` |
| **Stage-2 `F_step` kernel (`step_ops_folded`)** | **67** | **71** | **14 peak** | **0 register spills in 64 registers** |
| Traced 4-op SWAR DP detector (`dp_word`) | +4 | +4 | **14 peak** | `((out & 0x7F) + 0x7F) ^ 0x80 & 0x80` (71 traced ops) |
| Branch on `dp_word != 0` + loop counter (`sub_c`, `bnz`) | +3 | +3 | — | 1 DP branch + 2 loop ops |
| **Main Stage-1 batch (`main_batch_ops`, SWAR)** | **74** | **78** | **14 peak** | **10.571 ops/lane evaluation** |
| **Main Stage-1 batch (`main_batch_ops_unpacked`)** | **96** | **100** | **14 peak** | 67 kernel + 27 unpacked lane checks + 2 loop |
| **Stage-2 recovery batch (`rec_batch_ops_simd7`)** | **77** | **81** | **14 peak** | `F_step` (67) + loop (2) + 2-lane ctrl (8) |
| **Stage-2 recovery batch (`rec_batch_ops_stream7`)** | **98** | **102** | **14 peak** | `F_step` (67) + loop (2) + 7-lane ctrl (29) |

Linear-scan register allocation (`allocate()` in [`experiments/r39_claw.py`](experiments/r39_claw.py#L804-L837)) assigns all 67 Stage-2 instructions and all 71 Stage-1 instructions to **14 physical registers** out of 64 (`spill_ops_64 = 0`), and `run_allocated()` ([`experiments/r39_claw.py`](experiments/r39_claw.py#L844-L895)) executes the 71-op kernel instruction-by-instruction across 112 lanes per active trial in `r39-claw-vow`, verifying bit-exact agreement with both scalar `F_step` and the unpacked DP detector (`stage1_dp_mask`).

---

## 6. End-to-End vOW Distinguished-Point Walk and Complete Cost Ledger

We execute and count both a full **65,536-slot ($2^{16}$-slot) van Oorschot-Wiener (vOW) benchmark** (`ledger()` in [`experiments/r39_claw.py`](experiments/r39_claw.py#L1072-L1229)) and a **live unselected 16-CV vOW + full-32-bit claw verification** inside `r39-claw-vow` ([`run_claw_vow_experiment`](experiments/r39_claw.py#L1279-L1544)).

### 6.1 vOW Table Parameters, Per-CV Breakdown, and Live Multi-Step Trail Recovery
- **Table geometry**: $S = 65,536 = 2^{16}$ slots $\times 12\text{ bytes} = 786,432\text{ bytes}$ ($768\text{ KiB}$), `dp_bits = 7` ($p_{\text{dp}} = 1/128$), `max_steps = 2048`.
- **Per-CV stability across the $4 \times 2^{26} = 268,435,704$ walk evaluations**:
  - `CV 0` (`seed = 0x202d0329`): $67,108,926$ evals, $523,604$ DP hits, $82,786$ value matches, $40,671$ raw claws, **$33,820$ distinct claws**, $38$ $\mathcal{F}_8 \cap \mathcal{F}_9$ passes.
  - `CV 1` (`seed = 0x203d0329`): $67,108,940$ evals, $522,380$ DP hits, $82,367$ value matches, $40,653$ raw claws, **$33,772$ distinct claws**, $36$ $\mathcal{F}_8 \cap \mathcal{F}_9$ passes.
  - `CV 2` (`seed = 0x204d0329`): $67,108,872$ evals, $523,502$ DP hits, $82,911$ value matches, $40,916$ raw claws, **$33,962$ distinct claws**, $45$ $\mathcal{F}_8 \cap \mathcal{F}_9$ passes.
  - `CV 3` (`seed = 0x205d0329`): $67,108,966$ evals, $523,190$ DP hits, $82,714$ value matches, $40,743$ raw claws, **$33,858$ distinct claws**, $38$ $\mathcal{F}_8 \cap \mathcal{F}_9$ passes.
  - **Total across 4 CVs**: $268,435,704$ evals, $2,092,676$ DP hits, $330,778$ value matches, $162,983$ raw claws, **$135,412$ deduplicated distinct claws** ($33,853.0 \pm 79.1$ per CV, CV-to-CV relative SD $0.23\%$), and **$157$ joint $\mathcal{F}_8 \cap \mathcal{F}_9$ passes** (vs $135,412 \times 585 / 524,288 = 151.10$ expected).
- **Live unselected 16-CV vOW and full-32-bit claw verification in `r39-claw-vow`**:
  - On each active trial $t \in \{0, \dots, 15\}$, `run_claw_vow_experiment` executes `run_live_reduced_vow` ($256$ slots, `dp_bits = 3`, `max_steps = 64`, $640$ walks/trial $= 10,240$ walks across 16 independent first blocks) on the 16-bit projection of `F_step(x, wp)`, recovering $\approx 560$ raw claws and $\approx 500$ deduplicated distinct claws (`dedup_ratio` $\approx 0.90$), plus a live unselected full-32-bit $W_{16} = \mathtt{0xbca1c321}$ claw search ($24,576$ even $a_0$ evaluations per trial against $262,144$ odd $u$ values, yielding $\approx 23$ live full-32-bit claws across the 16 trials), and exercises both `recover_1pair_simd7` (`simd7`) and `recover_7pairs_packed` (`stream7` with `len(pairs) == 7`).

### Table 6.1: Empirical 65,536-Slot vOW Benchmark Ledger (`--ledger`)
| Quantity | Measured Value | Per Distinct Claw | Notes |
|---|---:|---:|---|
| Table slots $S$ / `dp_bits` / `max_steps` | $65,536$ / $7$ / $2,048$ | — | $786,432\text{ B}$ DP table ($768\text{ KiB}$) |
| Total Stage-1 walk evaluations | $268,435,704$ ($2^{28.0000}$) | $1,982.3627$ | $4\times \mathrm{CV}_1$ tables $\times 2^{26}$ evals |
| Main 7-lane batches (`74` SWAR ops / `96` unpacked ops) | $38,347,958$ | $283.1947$ | $20,956.41\text{ ops}$ (SWAR) / $27,186.69\text{ ops}$ (unpacked) |
| Distinguished-point hits (`dp_hits`) | $2,092,676$ | $15.4541$ | $18\text{ ops/hit}$ handler $= 278.17\text{ ops}$ |
| `val32` matches triggering Stage 2 | $330,778$ | $2.4428$ | Queued for Stage-2 trail recovery |
| Raw opposite-parity claws recovered | $162,983$ | $1.2036$ | $26\text{ ops/claw}$ `recover_a1` $= 31.29\text{ ops}$ |
| **Deduplicated distinct claws `(a0, u)`** | **$135,412$** | **$1.0000$** | Unique `(a0, u)` pairs ($83.08\%$ unique) |
| Stage-2 batches (`stream7`, `98` ops/batch) | $10,568,425$ | $78.0464$ | $78.0464 \times 98 = 7,648.55\text{ ops}$ |
| Stage-2 batches (`simd7`, `77` ops/batch) | $27,708,681$ | $204.6250$ | $204.6250 \times 77 = 15,756.13\text{ ops}$ |
| Stage-2 batches (`2lane`, `77` ops/batch) | $55,558,869$ | $410.2950$ | $410.2950 \times 77 = 31,592.72\text{ ops}$ |
| First-block compression + setup (`2812 + 260` ops/window) | $12,288$ | $0.0907$ | $3,072 / 33,853 = 0.0907\text{ ops/claw}$ |
| Total non-kernel overhead ops (DP + `recover_a1` + filter + CV1) | $43,488,860$ | $321.1596$ | $278.17 + 31.29 + 11.60 + 0.09\text{ ops}$ |
| **Total word ops / distinct claw (`stream7`, SWAR)** | — | **$28,926.12\text{ ops}$** | $10.2867\text{ compressions} = 2^{3.36270}$ |
| **Total word ops / distinct claw (`simd7`, SWAR)** | — | **$37,033.69\text{ ops}$** | **$13.1699\text{ compressions} = 2^{3.71917}$** |
| **Total word ops / distinct claw (`simd7`, unpacked 96-op)** | — | **$43,263.97\text{ ops}$** | **$15.3855\text{ compressions} = 2^{3.94350}$** |

---

## 7. Exact Active-Bit Theorem for $\mathcal{F}_8 \cap \mathcal{F}_9$, Conditional Uniformity of $W_{17}$, and Complete 64-Seed Zero-Stall Tail Study

Once a distinct claw $(a_0, u)$ satisfies $W_{16}(a_0, u) = g = \mathtt{0xbca1c321}$, it must pass the row-8/row-9 side conditions ($p_8 \cdot p_9 = 2^{-9.807707}$), the row-17 transition ($p_{17} = 2^{-32}$), and the steps $18 \dots 38$ differential tail ($p_{\text{tail}} \ge 2^{-76.55}$):

### Theorem 7.1 (Exact Active-Bit Enumeration and Bit-0 Parity Invariance of $\mathcal{F}_8$ and $\mathcal{F}_9$)
Define $\mathcal{F}_8 = \{w \in \mathbb{Z}/2^{32}\mathbb{Z} : \sigma_0(w + \mathtt{0x08002400}) - \sigma_0(w) \equiv \mathtt{0xfdffe800} \pmod{2^{32}}\}$ (`in_F8`) and $\mathcal{F}_9 = \{w \in \mathbb{Z}/2^{32}\mathbb{Z} : \sigma_0(w + \mathtt{0x00002004}) - \sigma_0(w) \equiv \mathtt{0x11002000} \pmod{2^{32}}\}$ (`in_F9`). Then ([`enumerate_active_f8_f9`](experiments/r39_claw.py#L319-L368)):
1. **Exact active-bit factorization of $\mathcal{F}_8$**: Because $D_8 = \mathtt{0x08002400} = 2^{10} + 2^{13} + 2^{27}$ has zero bits outside $\{10, 11, 13, 14, 27, 28\}$ and $\sigma_0(x) = (x \ggg 7) \oplus (x \ggg 18) \oplus (x \gg 3)$ maps those 6 bit positions into the 8 output bits $\{3, 4, 6, 7, 16, 17, 20, 21, 24, 25, 26, 27, 30, 31\}$, membership $w \in \mathcal{F}_8$ depends **only on the 14 active bit positions of `ACTIVE_MASK_F8 = 0xCC19E60C`** (bits $\{2, 3, 9, 10, 11, 13, 14, 15, 16, 19, 20, 26, 27, 30, 31\}$) and is **strictly invariant** under flipping any of the 18 complement bits `INACTIVE_MASK_F8 = 0x33E619F3`. Exhaustive enumeration of all $2^{14} = 16,384$ active bit states yields **exactly $1,152$ valid states**, proving $|\mathcal{F}_8| / 2^{32} = 1,152 / 16,384 = 9 / 128 = 2^{-3.830075}$.
2. **Exact bit-0 parity invariance of $\mathcal{F}_8$**: Bit $0$ lies in `INACTIVE_MASK_F8 = 0x33E619F3` (`(0xCC19E60C & 1) == 0`), so $\operatorname{in\_F8}(w) = \operatorname{in\_F8}(w \oplus 1)$ for all $w \in \{0, 1\}^{32}$ (verified across all $2^{14}$ active states in `enumerate_active_f8_f9` with `inv_bad = 0`). Consequently, restricting $a_0$ to even words ($(a_0 \bmod 2) = 0$) in the bipartite walk cannot bias $\Pr[W_8 \in \mathcal{F}_8]$.
3. **Exact active-bit factorization of $\mathcal{F}_9$**: Membership $w \in \mathcal{F}_9$ depends **only on the 17 active bit positions of `ACTIVE_MASK_F9 = 0xF9983C0F`** and is strictly invariant under flipping any of the 15 complement bits `INACTIVE_MASK_F9 = 0x0667C3F0`. Exhaustive enumeration of all $2^{17} = 131,072$ active bit states yields **exactly $2,080$ valid states**, proving $|\mathcal{F}_9| / 2^{32} = 2,080 / 131,072 = 65 / 4096 = 2^{-5.977632}$ and $p_8 \cdot p_9 = 585 / 524,288 = 2^{-9.807707}$. $\square$

In `r39-claw-vow`, Trial 16 runs `enumerate_active_f8_f9()` live, verifying `len(f8_active) == 1152`, `len(f9_active) == 2080`, and `inv_bad == 0` across all $2^{14} + 2^{17} = 147,456$ states in $\sim 0.12\text{ s}$. Across the $135,412$ distinct claws recovered by our 4-CV vOW benchmark, **$157$ claws passed both `in_F8(W8)` and `in_F9(W9)`**, versus $135,412 \times (585 / 524,288) = 151.10$ expected (**ratio $1.039$**, within $+0.48\sigma$).

### 7.2 Row 17 Transition ($p_{17} = 2^{-32}$) and Complete 64-Seed Zero-Stall Tail Study ($p_{\text{tail}} \ge 2^{-76.55}$)
- **Row 17 transition ($p_{17} = 2^{-32.0}$, `H4-accepted-claw-event`)**:
  - Exact bit-by-bit enumeration (`solve_row_exact`) proves $G_{16} = \{\mathtt{0xbca1c121}, \mathtt{0xbca1c321}\}$ ($|G_{16}| = 2$) and $G_{17}(\mathtt{0xbca1c321}) = \{\mathtt{0x71e9ba98}\}$ ($|G_{17}| = 1$).
  - By Lemma 2.1(5), $W_{17}(a_0, u) = \sigma_1(W_{15}^{\text{base}}) + W_{10}^{\text{base}} + \sigma_0(W_2(a_0, a_1)) + u \pmod{2^{32}}$, where $W_2(a_0, a_1)$ is driven by step-2 $\Sigma_0(a_1) + \operatorname{MAJ}(a_1, a_0, \mathrm{cv}_0)$ and $\Sigma_1(e_1) + \operatorname{CH}(e_1, e_0, \mathrm{cv}_4)$, which do not appear in $W_{16}(a_0, u)$, $W_8$, or $W_9$.
  - Across the $135,412$ distinct vOW claws (`vow_64k_benchmark` in `--ledger`), individual byte matches to $\mathtt{0x71e9ba98}$ are **$[517, 486, 525, 526]$** vs $528.95 \pm 22.95$ expected, 16-bit prefix matches (`0xba98`) are **$4$** vs $2.07$ expected, and conditioned on $W_8 \in \mathcal{F}_8 \land W_9 \in \mathcal{F}_9$ ($157$ claws), low 4-bit matches `(W17 & 0xF) == 0x8` occurred **$13 / 157 = 0.0828$** times vs $1/16 = 0.0625$ ($9.81$ expected). In `r39-claw-vow`, unselected live vOW claws across 16 CVs also pass the pooled low-4-bit $W_{17}$ gate on Trial 16.
- **Tail Rows 18..38 ($p_{\text{tail}} \ge 2^{-76.55}$, 64-seed zero-stall SMC study, `H4-accepted-claw-event`)**:
  - Using $N = 16,384 = 2^{14}$ particles per stage across **64 independent seeds** (`Seeds 1..64`, Table 7.1), **all 64 seeds completed with zero stalls (`64 / 64`, `0` stalls)**:
    - Linear-scale sample mean: $\log_2(\text{mean}(\hat{p}_{\text{tail}})) = \mathbf{-76.183798}$; one-sided 99% Student-$t$ LCB on the **linear** scale $\log_2(\bar{p} - t_{0.99,63} \cdot s_p / \sqrt{64})$: **$-76.3812$** (99% bootstrap LCB: **$-76.3749$**).
    - Log-scale sample mean: $\text{mean}(\log_2 \hat{p}_{\text{tail}}) = \mathbf{-76.335945}$ (SD $= 0.7168$, SE $= 0.0896$); one-sided 99% Student-$t$ LCB on $\text{mean}(\log_2 \hat{p}_{\text{tail}})$: **$-76.5498$**. By Jensen's inequality ($\mathbb{E}[\log_2 \hat{p}_{\text{tail}}] \le \log_2 \mathbb{E}[\hat{p}_{\text{tail}}]$), the log-scale Student-$t$ LCB **$-76.55$** is strictly more conservative than the linear-scale LCB ($-76.3812$) by an additional $0.17$ bits.
    - In `r39-tail-sfs`, Trials `0..15` execute 16 strictly fixed-budget SMC replicas ($N_{\text{part}} = 32, M_{\text{draws}} = 96, T_{\text{roll}} = 512 \implies 16,384$ rollouts/trial, with zero `while`/adaptive stopping loops) and Trial 16 verifies that the pooled linear-scale mean satisfies $\log_2(\text{mean}(\hat{q})) = -76.1828 \in [-77.8, -74.5]$.

### Table 7.1: Complete 64-Seed Zero-Stall SMC Study (`N = 16,384` Particles/Stage, `0` Stalls)
| Seed | $\log_2 \hat{p}_{\text{tail}}$ | Coll | Seed | $\log_2 \hat{p}_{\text{tail}}$ | Coll | Seed | $\log_2 \hat{p}_{\text{tail}}$ | Coll | Seed | $\log_2 \hat{p}_{\text{tail}}$ | Coll |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | $-76.0831$ | 9 | 17 | $-77.0988$ | 5 | 33 | $-76.8418$ | 6 | 49 | $-75.7814$ | 13 |
| 2 | $-76.0486$ | 9 | 18 | $-75.6317$ | 14 | 34 | $-75.6090$ | 13 | 50 | $-75.6934$ | 12 |
| 3 | $-75.6735$ | 13 | 19 | $-75.9502$ | 11 | 35 | $-76.4943$ | 8 | 51 | $-76.6407$ | 7 |
| 4 | $-76.4887$ | 8 | 20 | $-76.0548$ | 10 | 36 | $-75.7381$ | 12 | 52 | $-77.3996$ | 4 |
| 5 | $-76.7904$ | 6 | 21 | $-76.4772$ | 8 | 37 | $-75.8739$ | 11 | 53 | $-76.8966$ | 6 |
| 6 | $-75.2622$ | 16 | 22 | $-77.6455$ | 4 | 38 | $-76.4343$ | 8 | 54 | $-78.0445$ | 3 |
| 7 | $-76.3510$ | 7 | 23 | $-76.8991$ | 7 | 39 | $-76.7585$ | 6 | 55 | $-75.6197$ | 16 |
| 8 | $-76.0791$ | 11 | 24 | $-76.4398$ | 9 | 40 | $-76.0944$ | 10 | 56 | $-79.2688$ | 1 |
| 9 | $-75.6654$ | 12 | 25 | $-75.6416$ | 14 | 41 | $-76.9554$ | 6 | 57 | $-75.3019$ | 18 |
| 10 | $-75.6265$ | 12 | 26 | $-75.9983$ | 12 | 42 | $-76.7229$ | 7 | 58 | $-75.9145$ | 11 |
| 11 | $-76.7899$ | 6 | 27 | $-76.5907$ | 6 | 43 | $-76.8377$ | 6 | 59 | $-76.7422$ | 8 |
| 12 | $-76.4879$ | 9 | 28 | $-76.6479$ | 7 | 44 | $-76.9224$ | 6 | 60 | $-76.6872$ | 7 |
| 13 | $-76.1498$ | 11 | 29 | $-75.0807$ | 19 | 45 | $-76.7892$ | 7 | 61 | $-77.0617$ | 5 |
| 14 | $-76.9324$ | 6 | 30 | $-75.1834$ | 16 | 46 | $-75.8443$ | 11 | 62 | $-75.1763$ | 16 |
| 15 | $-76.5566$ | 8 | 31 | $-76.1510$ | 9 | 47 | $-75.9455$ | 11 | 63 | $-76.5797$ | 8 |
| 16 | $-76.2722$ | 9 | 32 | $-76.0094$ | 11 | 48 | $-76.3840$ | 8 | 64 | $-75.6892$ | 12 |

### Table 7.2: Per-Claw Success Probability and Required Distinct Claws
| Factor | Exact / Conservative Value | $\log_2$ Value | Evidence & Method |
|---|---:|---:|---|
| Row-8 side condition $p_8$ (`in_F8`) | $1,152 / 2^{14} = 9/128$ | $-3.830075$ | Theorem 7.1 (exhaustive $2^{14}$ active states, bit-0 invariant) |
| Row-9 side condition $p_9$ (`in_F9`) | $2,080 / 2^{17} = 65/4096$ | $-5.977632$ | Theorem 7.1 (exhaustive $2^{17}$ active states) |
| Combined side conditions $p_8 \cdot p_9$ (`H3`) | $585 / 524,288$ | $-9.807707$ | Theorem 7.1 + $157 / 135,412$ vOW claws + Trial 16 gate |
| Conditional uniformity of $W_{17}$ ($p_{17}$, `H4`) | $1 / 2^{32}$ | $-32.000000$ | $|G_{17}(\mathtt{0xbca1c321})| = 1$ + vOW byte/prefix/Trial 16 gates |
| Tail rows $18..38$ ($p_{\text{tail}}$, 99% LCB, `H4`) | $2^{-76.55}$ | $-76.550000$ | 64-seed SMC (mean $-76.18$, linear LCB $-76.38$, log LCB $-76.55$) |
| **Total per-claw probability $p_{\text{claw}}$** | **$2^{-118.357707}$** | **$-118.357707$** | Product $p_8 \cdot p_9 \cdot p_{17} \cdot p_{\text{tail}}$ |
| Poisson amplification $\lambda = -\ln(1 - 0.39)$ | $0.49429635$ | $-1.016552$ | Target success probability $\ge 0.39$ (`H1`) |
| **Required distinct claws $N_{\text{claws}} = \lambda / p_{\text{claw}}$** | **$2^{117.341155}$** | **$117.341155$** | $\approx 3.38 \times 10^{35}$ distinct claws |

---

## 8. Total Work Accounting and Memory Breakdown

With $S = 65,536$ slots and $2^{26} = 67,108,864$ walk evaluations per first-block chaining value $\mathrm{CV}_1$, each $\mathrm{CV}_1$ yields on average $135,412 / 4 = 33,853.0$ distinct claws ($2^{15.047}$ distinct claws per $\mathrm{CV}_1$).
Thus the attack processes $N_{\text{FB}} = 2^{117.341155} / 33,853.0 = 2^{102.294}$ random first blocks $M_0$.
Each first block $M_0$ costs **1 full 39-step compression (`C_BLOCK = 2812` ops) plus `260` constant-setup ops** ($3,072$ ops per $2^{26}$ window, or $3,072 / 33,853 = 0.0907$ ops per distinct claw, explicitly included in `cv_refresh_ops` in [`experiments/r39_claw.py`](experiments/r39_claw.py#L1106)).

### Table 8.1: Total Work Across Stage-1 DP Detection and Stage-2 Recovery Regimes
| Stage-1 & Stage-2 Regime | Ops / Distinct Claw | Compressions / Claw ($\div 2812$) | $\log_2(\text{Compressions / Claw})$ | Total Work $\log_2 T$ |
|---|---:|---:|---:|---:|
| `stream7` + 74-op SWAR Stage-1 + 98-op Stage-2 | $28,926.12$ | $10.28667$ | $+3.36270$ | $120.7039$ |
| **`simd7` + 74-op SWAR Stage-1 + 77-op Stage-2** | **$37,033.69$** | **$13.16988$** | **$+3.71917$** | **$121.0603$** |
| **`simd7` + 96-op Unpacked Stage-1 + 77-op Stage-2** | **$43,263.97$** | **$15.38548$** | **$+3.94350$** | **$121.2847$** |
| **Claimed Headline Bound (`claim.json`)** | — | — | — | **$121.3000$** |

Our claimed time bound **`time_log2 = 121.30`** provides a **`+0.240`-bit safety margin** above the 74-op SWAR `simd7` regime ($121.0603$), a **`+0.596`-bit safety margin** above the 7-lane buffered `stream7` regime ($120.7039$), and a **`+0.015`-bit safety margin** above even the 96-op unpacked Stage-1 loop ($121.2847$).

### Table 8.2: Peak Resident Memory Breakdown (`memory_log2_bytes = 20`)
| Component | Exact Size (Bytes) | Notes |
|---|---:|---|
| vOW Distinguished-Point Table ($65,536 \times 12\text{ B}$) | $786,432$ | 65,536 slots $\times$ 96 bits (`start32`, `meta32`, `val32`) |
| Straight-line program code ($\le 512 \times 36\text{ B}$) | $18,432$ | 67/71-op kernels + Stage-1/2 control & handlers |
| 64-register 256-bit register file ($64 \times 32\text{ B}$) | $2,048$ | Architectural register state |
| Table 23 dense base, row masks, and scratch buffers | $16,384$ | Includes 584-byte base + recovery buffer |
| **Total Peak Resident Memory** | **$823,296$** | **$< 1,048,576\text{ bytes}$ ($2^{20}\text{ bytes}$, $78.5\%$ of $1\text{ MiB}$)** |

Because $823,296 < 2^{20} = 1,048,576$, the attack satisfies `memory_log2_bytes = 20` with $225,280\text{ bytes}$ ($220\text{ KiB}$) of spare headroom and incurs **zero memory penalty** under the Pareto objective $\mathrm{Score} = \text{time\_log2} + \max(0, \text{memory\_log2\_bytes} - 20) = 121.30$.

---

## 9. Summary of Technical Improvements Over Prior 39-Step Submissions

1. **Exact traced 4-op SWAR DP detector (`71` traced ops) + full Stage-2/first-block accounting (`121.30`)**: `build_traced_step(fold_maj=True, include_dp=True)` traces the 4-op SWAR zero-field test `((out & 0x7F) + 0x7F) ^ 0x80 & 0x80` directly in the 64-register model (`14` peak live registers, `0` spills), and `ledger()` explicitly includes `+8` ops/batch (`simd7`) / `+29` ops/batch (`stream7`) Stage-2 control overhead and `2812 + 260` first-block compression ops per window.
2. **Exact active-bit theorem (`enumerate_active_f8_f9`) + live unselected 16-CV vOW and full-32-bit claw verification in `r39-claw-vow`**: Exhaustively enumerates all $2^{14}$ active states of `in_F8` (`1,152 / 16,384 = 9/128` + exact bit-0 parity invariance) and $2^{17}$ active states of `in_F9` (`2,080 / 131,072 = 65/4096`), runs live unselected vOW walks and live unselected full-32-bit $W_{16} = \mathtt{0xbca1c321}$ claw searches across 16 independent first blocks, exercises both `recover_1pair_simd7` (`simd7`) and `recover_7pairs_packed` (`stream7`), and gates the 17th returned pair on Trial 16 on all exhaustive and pooled statistical checks.
3. **Strictly fixed-budget SMC replicas (`0` adaptive/while loops) + Trial 16 pooled SMC gate in `r39-tail-sfs`**: Eliminates all rejection/while loops by sampling uniform words in $\mathcal{F}_8$ and $\mathcal{F}_9$ directly from `f8_active | INACTIVE_MASK_F8` and `f9_active | INACTIVE_MASK_F9`, runs 16 fixed-budget SMC replicas (`M_draws = 96`, `target_rollouts = 16,384`), and gates the 17th returned SFS pair on Trial 16 on `-77.8 <= log2(mean_q) <= -74.5` and `tot_live_inverted >= 6`.

---

## 10. Heuristics and Evidence Inventory (`claim.json`)

- **`H1-single-trial-chaining-value`**: For uniform 512-bit $M_0$, $\mathrm{CV}_1 = \operatorname{sha256\_r39\_compress}(\mathrm{IV}, M_0)$ behaves as an independent random 256-bit chaining value for the bipartite walk $F_{\text{step}}$, the row-16/row-17 bridge, and the steps $18 \dots 38$ tail, so distinct first blocks yield independent per-window claw trials with Poisson amplification $1 - e^{-\lambda} \ge 0.39$ across $2^{102.294}$ first blocks. Supported by Sections 2–3 (lines 22-67), Section 6 (lines 153-167), Section 8 (lines 246-251), and `experiment:r39-claw-vow` (16 independent CVs, `inter_cv_disp_ratio <= 2.2` gated on Trial 16).
- **`H2-packed-7lane-machine-model`**: Under the 64-register 256-bit word-RAM convention ($C = 2812$ ops/compression), 7 lanes packed at a 36-bit stride execute one `F_step` batch in $67$ traced instructions for Stage 2 and $71$ traced instructions for Stage 1 (`14` peak live registers, `0` spills), and with all Stage-1 DP, Stage-2 control (`77` ops/batch `simd7`, `98` ops/batch `stream7`), staged filtering, and per-window $M_0$ compression (`2812 + 260` ops) included, total attack work is $\le 2^{121.30}$. Supported by Section 5 (lines 98-149), Section 8 (lines 246-271), and `experiment:r39-claw-vow`.
- **`H3-vow-distinct-claw-rate`**: A 65,536-slot ($768\text{ KiB}$) two-stage vOW DP search (`dp_bits = 7`, `max_steps = 2048`) switched every $2^{26}$ evaluations yields at least $33,853$ deduplicated distinct claws $(a_0, u)$ per $2^{26}$ evaluations ($1,982.36$ evals/claw), and deduplicated vOW claws preserve the exact active-bit side-condition survival rate $\Pr[W_8 \in \mathcal{F}_8 \land W_9 \in \mathcal{F}_9] = (9/128) \cdot (65/4096) = 585 / 524,288 = 2^{-9.807707}$. Supported by Section 6 (lines 153-185), Theorem 7.1 (lines 193-199), `experiment:r39-claw-vow`, and `experiment:r39-tail-sfs`.
- **`H4-accepted-claw-event`**: Conditioned on a deduplicated vOW claw $(a_0, u)$ satisfying $W_{16}(a_0, u) = \mathtt{0xbca1c321}$, $W_8 \in \mathcal{F}_8$, and $W_9 \in \mathcal{F}_9$, the conditional probability that the reconstructed message pair satisfies the accepted 39-step collision event across steps $17 \dots 38$—namely $W_{17}(a_0, u) = \mathtt{0x71e9ba98}$ ($p_{17} = 2^{-32}$) and the steps $18 \dots 38$ differential tail ($p_{\text{tail}} \ge 2^{-76.55}$)—is at least $2^{-108.55}$, giving $p_{\text{claw}} = 2^{-9.807707} \cdot 2^{-108.55} = 2^{-118.357707}$. Supported by Lemma 2.1(5) (lines 45-52), Section 7.2 and Tables 7.1–7.2 (lines 201-242), `experiment:r39-claw-vow`, and `experiment:r39-tail-sfs`.

---

## 11. Organizer Experiments and Reproducibility (`experiments/r39_claw.py`)

Both declared experiments in [`experiments/manifest.json`](experiments/manifest.json) invoke [`experiments/r39_claw.py`](experiments/r39_claw.py) under the 256-trial `python-message-pairs-v1` protocol (`ACTIVE_TRIALS = 16`, `GATE_TRIAL = 16`, `RETURNED_TRIALS = 17`, total runtime `~2.8s` for both experiments combined):
1. **`r39-claw-vow`** ([`run_claw_vow_experiment`](experiments/r39_claw.py#L1279-L1544)): Trials `0..15` compress a seed-derived first block $M_0$ from the standard SHA-256 IV to obtain $\mathrm{CV}_1$; execute the register-allocated 71-op Stage-1 kernel across 16 batches (`112` lanes/trial, `1,792` lanes total, `14` registers, `0` spills); execute a live unselected vOW DP search (`640` walks/trial $= 10,240$ walks across 16 CVs) and a live unselected full-32-bit $W_{16} = \mathtt{0xbca1c321}$ claw search (`24,576` even $a_0$ evals/trial); and execute 1-pair 2-walk-in-7-lane Stage-2 recovery (`recover_1pair_simd7`) on `VOW_F89_TRAILS[t]`. Trial `16` (summary gate) runs `enumerate_active_f8_f9()` (`1,152 / 16,384` and `2,080 / 131,072` + bit-0 parity invariance), executes 7-lane buffered Stage-2 recovery (`recover_7pairs_packed` with `len(pairs) == 7`), and returns the 17th pair iff all exhaustive and pooled 16-CV vOW gates pass.
2. **`r39-tail-sfs`** ([`run_tail_sfs_experiment`](experiments/r39_claw.py#L1547-L1726)): Verifies $|G_{16}| = 2$, $|G_{17}(\mathtt{0xbca1c321})| = 1$, and $|G_{18}| = 16,384$ ($12,288$ valid) via `solve_row_exact`, constructs the exact GF(2) affine subspaces on rows $19 \dots 22$ (`build_row_subspaces`), and on each trial $t \in \{0, \dots, 15\}$ executes a strictly fixed-budget SMC replica ($N_{\text{part}} = 32, M_{\text{draws}} = 96, T_{\text{roll}} = 512 \implies 16,384$ rollouts/trial, `0` adaptive/while loops), inverts step-38 hits via `invert_rollout_to_sfs`, and verifies `PAIR_CLAW_SFS[t]`. Trial `16` (summary gate) pools all 16 unbiased replica estimates `q_est` into `mean_q = sum(est_q_list) / 16.0` and returns the 17th verified 96-byte 39-step SFS colliding pair `PAIR_CLAW_SFS[16]` iff `tot_bad == 0`, `tot_live_inverted >= 6`, and `-77.8 <= log2(mean_q) <= -74.5`.
