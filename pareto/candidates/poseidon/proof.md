# Collision Attack on Orchard Poseidon with $r = 56$ Partial Rounds via an 807-Operation Multiplicative-Coin Step Program and 31-Unrolled Gap-Free Register Machine

## 1. Target Specification and Boundary Alignment

We target full-width ordinary collision finding for the Orchard/Pallas Poseidon hash function at **$r = 56$ partial rounds** (`target_profile`: `poseidon-orchard-r56-prefix-v1`, `attack_class`: `ordinary-collision`, `lane`: `exploratory`) under cost model `orchard-field-ram-v2`.

### 1.1 Field, State Initialization, and Round Schedule
Let $p$ be the Pallas base field prime:
$$p = \text{0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001}$$
$$= 28948022309329048855892746252171976963363056481941647379679742748393362948097.$$
Since $p - 1 \equiv 1 \pmod 5$, $\gcd(5, p - 1) = 1$, so the fifth-power S-box map $S(u) = u^5 \bmod p$ is a bijection on $\mathbb{F}_p$ with inverse $S^{-1}(v) = v^{\text{INV5}} \bmod p$, where:
$$\text{INV5} = 5^{-1} \bmod (p - 1) = \frac{4(p - 1) + 1}{5} = 23158417847463239084714197001737581570690445185553317903743794198714690358477.$$

A valid Orchard Poseidon message is a 64-byte string encoding a pair of canonical 32-byte little-endian integers $(nk, \rho) \in [0, p)^2$. The width-3 permutation state is initialized with fixed capacity element $2^{65}$:
$$s^{(0)} = [nk,\; \rho,\; 2^{65}]^\top \in \mathbb{F}_p^3.$$
Let $RC = (c^{(0)}, \dots, c^{(63)}) \in (\mathbb{F}_p^3)^{64}$ and $M \in \mathbb{F}_p^{3 \times 3}$ denote the pinned Orchard Pallas round constants and $3 \times 3$ MDS matrix from `orchard-pallas-constants.json`. For $r = 56$ partial rounds, the active round schedule is $(0, 1, 2, 3, 4, 5, \dots, 59, 60, 61, 62, 63)$ (all 64 rounds):
1. **Initial full rounds ($t \in \{0, 1, 2, 3\}$):**
   $$u_i^{(t)} = (s_i^{(t)} + c_i^{(t)}) \bmod p, \quad v_i^{(t)} = (u_i^{(t)})^5 \bmod p \;\; (i \in \{0, 1, 2\}), \quad s^{(t+1)} = M v^{(t)} \bmod p.$$
2. **Partial rounds ($t \in \{4, \dots, 59\}$):**
   $$u_i^{(t)} = (s_i^{(t)} + c_i^{(t)}) \bmod p \;\; (i \in \{0, 1, 2\}), \quad v_0^{(t)} = (u_0^{(t)})^5 \bmod p, \quad v_1^{(t)} = u_1^{(t)}, \quad v_2^{(t)} = u_2^{(t)}, \quad s^{(t+1)} = M v^{(t)} \bmod p.$$
3. **Terminal full rounds ($t \in \{60, 61, 62, 63\}$):**
   $$u_i^{(t)} = (s_i^{(t)} + c_i^{(t)}) \bmod p, \quad v_i^{(t)} = (u_i^{(t)})^5 \bmod p \;\; (i \in \{0, 1, 2\}), \quad s^{(t+1)} = M v^{(t)} \bmod p.$$

The hash output $\operatorname{digest}(nk, \rho)$ is the 32-byte little-endian canonical encoding of the first field element exiting Round 63, $y = s_0^{(64)} \in [0, p)$. Two pairs $(nk_a, \rho_a) \ne (nk_b, \rho_b)$ in $[0, p)^2$ form a valid collision if and only if $s_0^{(64)}(nk_a, \rho_a) = s_0^{(64)}(nk_b, \rho_b)$.

### 1.2 Cost Model and Normalization (`orchard-field-ram-v2`)
Under `orchard-field-ram-v2`, one nominal target compression at $r = 56$ costs:
$$C(56) = 216 + 21 \times 56 = 1392 \text{ primitive operations}.$$
Each field arithmetic operation (`FADD`, `FSUB`, `FMUL`), 256-bit word arithmetic/bitwise/shift operation (`ADD`, `SUB`, `MUL`, `ADDI`, `SUBI`, `MULI`, `AND`, `OR`, `SHL`, `SHR`, `SHLI`, `SHRI`), register move (`MOV`), random field draw (`RAND`), and unconditional jump/halt (`JMP`, `JR`, `HALT`) costs $1$ primitive operation. Each memory access (`LOAD`, `STORE`, `LOADC`, `LOAD_START`, `STORE_START`) costs $2$ primitive operations (1 address calculation + 1 memory access), and each conditional branch (`BEQ`, `BNE`, `BLT`, `BGE`) costs $2$ primitive operations (1 comparison + 1 branch). Memory at or below $1\text{ MiB} = 2^{20} = 1,048,576$ bytes (`memory_log2_bytes <= 20`) incurs zero penalty on the combined objective $\text{time\_log2} + \max(0, \text{memory\_log2\_bytes} - 20)$.

---

## 2. Two-Round BBLP Affine Bypass and 807-Operation Multiplicative-Coin Step Program

### 2.1 Bariant–Bouvier–Leurent–Perrin (BBLP) Two-Round Affine Input Line
Following the algebraic 2-round bypass of Bariant, Bouvier, Leurent, and Perrin (ToSC 2022) as instantiated in prior Orchard Poseidon entries (`6de8a0a2`, `b810ea13`, `3f611f5c`, `43caeb6a`, `874894cf`), we parameterize the Round-0 S-box outputs $v^{(0)} = [U, V, C_0]^\top$, where the capacity lane has fixed Round-0 S-box output:
$$C_0 = (2^{65} + c_2^{(0)})^5 \bmod p = \text{0x1bb8b6550fd0a299151ec6e764ce7a0e7639053ef68202d771242177f32f108c}.$$
The Round-1 S-box inputs are $u_i^{(1)} = M_{i,0} U + M_{i,1} V + M_{i,2} C_0 + c_i^{(1)} \bmod p$. Setting $A_{\text{line}} = M_{0,1} \bmod p$ and $B_{\text{line}} = (-M_{0,0}) \bmod p$, any affine line
$$U(\tau) = (U_0 + A_{\text{line}} \tau) \bmod p, \qquad V(\tau) = (V_0 + B_{\text{line}} \tau) \bmod p$$
makes $u_0^{(1)}$ constant in $\tau$ because $M_{0,0} A_{\text{line}} + M_{0,1} B_{\text{line}} \equiv 0 \pmod p$. Since $\Delta_{12} = (M_{1,0} M_{2,1} - M_{1,1} M_{2,0}) \bmod p \ne 0$, we choose $(U_0, V_0)$ uniquely to cancel the constant terms of $u_1^{(1)}$ and $u_2^{(1)}$:
$$U_0 = \text{0x2de17246e844b000296eefaaf2116b9705e3af63806d80541c7d6b4be442036c},$$
$$A_{\text{line}} = \text{0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e},$$
$$V_0 = \text{0x2622542e119aef1f7c021664aae329063a3e73651cd62e02756427f9437fdd96},$$
$$B_{\text{line}} = \text{0x354a1a478b5972184c2a60423736152b8a6ef850e5c7edc566ee0c66281ee49e}.$$
Then the Round-1 S-box inputs are $u_0^{(1)} = s_{1,0}$, $u_1^{(1)} = L_1 \tau$, and $u_2^{(1)} = L_2 \tau \pmod p$, where $s_{1,0} = M_{0,0} U_0 + M_{0,1} V_0 + M_{0,2} C_0 + c_0^{(1)} \bmod p$ and $L_i = M_{i,0} A_{\text{line}} + M_{i,1} B_{\text{line}} \bmod p$ ($i \in \{1, 2\}$). Raising to the fifth power and setting $W = \tau^5 \bmod p$, the Round-1 S-box outputs are $v^{(1)} = [s_{1,0}^5,\; L_1^5 W,\; L_2^5 W]^\top \bmod p$. Consequently, the three Round-2 S-box inputs are affine functions of $W$:
$$u_{2,i}(W) = (A_{2,i} + B_i W) \bmod p = B_i (W + d_i) \bmod p, \qquad i \in \{0, 1, 2\},$$
where $A_{2,i} = (M_{i,0} s_{1,0}^5 + c_i^{(2)}) \bmod p$, $B_i = (M_{i,1} L_1^5 + M_{i,2} L_2^5) \bmod p \ne 0$, and $d_i = A_{2,i} B_i^{-1} \bmod p$:
$$B_0 = \text{0x23c27f31affe3355705c3436661672f812bf595c8c693caf2632952857b4f542},$$
$$B_1 = \text{0x0bf0a531e547aaee0a858122cd51bf61d3410fbc8972013ce3666a6f47a5b802},$$
$$B_2 = \text{0x3b86955a87b71c2631869b9fb992631c4a32ee6dea0ad3a8fc3e1f12f348c40a},$$
$$d_0 = \text{0x3a4bd2e80f62c6cde67f816c4a67f17bbd43a70c4d2fca9784cc22ba736569ff},$$
$$d_1 = \text{0x3630dc5efcfcfdbb081312b0a0678cd2ac0ccd77e9945052f05350f6b206d850},$$
$$d_2 = \text{0x397c756ad51b6231d22b5370cd725a0a7007a97f3ecc0c801fd16d9461ccfeb8}.$$

Given any $W \in \mathbb{F}_p$, the unique corresponding canonical input pair $(nk(W), \rho(W)) \in [0, p)^2$ is recovered via three fifth-root extractions:
$$\tau = W^{\text{INV5}} \bmod p, \quad nk(W) = \bigl((U_0 + A_{\text{line}} \tau)^{\text{INV5}} - c_0^{(0)}\bigr) \bmod p, \quad \rho(W) = \bigl((V_0 + B_{\text{line}} \tau)^{\text{INV5}} - c_1^{(0)}\bigr) \bmod p.$$
Because $x \mapsto x^5 \bmod p$ is a bijection on $\mathbb{F}_p$ and $(A_{\text{line}}, B_{\text{line}}) \ne (0, 0)$, the map $W \mapsto (nk(W), \rho(W))$ is injective on $\mathbb{F}_p$: distinct parameters $W_a \not\equiv W_b \pmod p$ always yield distinct canonical message pairs $(nk_a, \rho_a) \ne (nk_b, \rho_b)$.

### 2.2 Origin-Shifted Multiplicative Coin and the 807-Operation Step Reduction
Prior $r = 56$ constructions (`43caeb6a`, `874894cf`) parameterized $W$ using an additive trial coin $W(x) = (x + \rho_0) \bmod p$, which leaves a non-zero offset $\rho_0 + d_i$ on all three lanes entering Round 2 and requires **3 field additions** at the start of every step evaluation.

Instead, we shift the line origin to $-d_0$ and introduce a **multiplicative trial coin** $\rho_0 \in \mathbb{F}_p^*$ via:
$$W_{\rho_0}(x) = (\rho_0 x - d_0) \bmod p.$$
Since $\rho_0 \in \mathbb{F}_p^*$, $x \mapsto W_{\rho_0}(x)$ is a bijection on $\mathbb{F}_p$, so $x_a \not\equiv x_b \pmod p \iff W_{\rho_0}(x_a) \not\equiv W_{\rho_0}(x_b) \pmod p$. Substituting $W_{\rho_0}(x) = \rho_0 x - d_0$ into $u_{2,i} = B_i(W + d_i)$ cancels $d_0$ on lane 0:
$$u_{2,0}(x) = (B_0 \rho_0) x \pmod p, \qquad u_{2,i}(x) = (B_i \rho_0)\bigl(x + e_i(\rho_0)\bigr) \pmod p \quad (i \in \{1, 2\}),$$
where $e_i(\rho_0) = (d_i - d_0) \rho_0^{-1} \bmod p$ for $i \in \{1, 2\}$, with base ($\rho_0 = 1$) values:
$$e_1(1) = \text{0x3be50976ed9a36ed2193914455ff9b57110fbf67a5b17ed704b45f293ea16e52},$$
$$e_2(1) = \text{0x3f30a282c5b89b63ebabd204830a688ed50a9b6efae93b0434327bc6ee6794ba}.$$
Defining the Round-2 lane scales $s_{2,i}(\rho_0) = B_i \rho_0 \bmod p \ne 0$, the normalized Round-2 S-box inputs $y_i = u_{2,i} / s_{2,i}$ are:
$$y_0 = x, \qquad y_1 = (x + e_1(\rho_0)) \bmod p, \qquad y_2 = (x + e_2(\rho_0)) \bmod p.$$
Lane 0 requires **zero additions** (`r_x` is used directly as active lane 0 `r_u0`), reducing Round-2 entry from 3 additions to **2 additions** and saving **1 field addition and 1 constant register/word** on every step evaluation.

### 2.3 Complete 807-Operation Equivalent Step Program (`emit_step_807`)
Propagating the diagonal lane scales and the backward partial-round basis change through Rounds $2 \dots 63$ yields a straight-line step program of **$135 + 12r$ field operations** (**807 field operations** at $r = 56$: **329 `FADD` + 478 `FMUL`**) using **$49 + 5r = 329$ step constants** $c[0 \dots 328]$:

1. **Round 2 Entry (2 `FADD`, 0 `FMUL`, 2 constants $c[0..1]$):**
   With $u_0 = x$, compute $u_1 = (u_0 + c[0]) \bmod p$ and $u_2 = (u_0 + c[1]) \bmod p$, where $c[0] = e_1(\rho_0), c[1] = e_2(\rho_0)$.
2. **Round 2 S-boxes and Normalized MDS (9 `FADD`, 15 `FMUL`, 9 constants $c[2..10]$):**
   Compute $z_j = u_j^5 \bmod p$ for $j \in \{0, 1, 2\}$ ($3 \times 3 = 9$ `FMUL`). Let $s_{2,j}^5 = (B_j \rho_0)^5 \bmod p$ and normalize Round-3 S-box inputs by $s_{3,i} = M_{i,0} s_{2,0}^5 \bmod p$ so the coefficient of $z_0$ in every row is $1$. With $m_{2,i,j} = M_{i,j} s_{2,j}^5 s_{3,i}^{-1} \bmod p$ and $c_{3,i} = c_i^{(3)} s_{3,i}^{-1} \bmod p$, update:
   $$u_i \leftarrow \bigl(z_0 + m_{2,i,1} z_1 + m_{2,i,2} z_2 + c_{3,i}\bigr) \bmod p \quad (i \in \{0, 1, 2\}) \qquad (6\text{ FMUL} + 9\text{ FADD}).$$
3. **Round 3 S-boxes and Partial-Round Basis Initialization (6 `FADD`, 15 `FMUL`, 6 constants $c[11..16]$):**
   Compute $z_j = u_j^5 \bmod p$ for $j \in \{0, 1, 2\}$ (9 `FMUL`), with true Round-3 S-box outputs $s_{3,j}^5 z_j$. Let $M_{22} = \binom{M_{1,1}\; M_{1,2}}{M_{2,1}\; M_{2,2}}$, $M_{0,12} = (M_{0,1}, M_{0,2})$, $M_{12,0} = (M_{1,0}, M_{2,0})^\top$, and $P_{\text{mat}} = M_{22}^r \bmod p$. Define $H_0 = P_{\text{mat}} \cdot M_{1..2, 0..2} \operatorname{diag}(s_{3,0}^5, s_{3,1}^5, s_{3,2}^5) \bmod p$, and set terminal passive scales $s_{60,1} = (H_0)_{0,0}$, $s_{60,2} = (H_0)_{1,0}$, and initial active scale $sp_0 = M_{0,0} s_{3,0}^5 \bmod p$. Deferring $c_0^{(4)}$ into partial round 0 and setting $q^{(0)} = [c_1^{(4)}, c_2^{(4)}]^\top$, the normalized state entering partial round 0 has unit $z_0$-coefficients and zero constant additions:
   $$u_0 \leftarrow (z_0 + a_{3,u_0,1} z_1 + a_{3,u_0,2} z_2) \bmod p, \quad u_1 \leftarrow (z_0 + a_{3,h_1,1} z_1 + a_{3,h_1,2} z_2) \bmod p, \quad u_2 \leftarrow (z_0 + a_{3,h_2,1} z_1 + a_{3,h_2,2} z_2) \bmod p$$
   (6 `FMUL` + 6 `FADD`).
4. **$r = 56$ Partial Rounds ($56 \times 5 = 280$ `FADD`, $56 \times 7 = 392$ `FMUL`, 280 constants $c[17..296]$):**
   Maintain passive lanes $(s_1, s_2) = Q_k h^{(k)} + q^{(k)}$ where $Q_k = M_{22}^{k - r} \operatorname{diag}(s_{60,1}, s_{60,2}) \bmod p$, so that at $k = r$, $Q_r = \operatorname{diag}(s_{60,1}, s_{60,2})$ is diagonal. For each partial round $k \in \{0, \dots, r - 1\}$ with $sp_{k+1} = M_{0,0} sp_k^5 \bmod p$:
   $$u_0 \leftarrow (u_0 + c_p^{(k)}) \bmod p \;\;(1\text{ FADD}), \qquad z_0 \leftarrow u_0^5 \bmod p \;\;(3\text{ FMUL}),$$
   $$u_0 \leftarrow (z_0 + w_{k,1} u_1 + w_{k,2} u_2) \bmod p \;\;(2\text{ FMUL} + 2\text{ FADD}),$$
   $$u_1 \leftarrow (u_1 + v_{k,1} z_0) \bmod p, \quad u_2 \leftarrow (u_2 + v_{k,2} z_0) \bmod p \;\;(2\text{ FMUL} + 2\text{ FADD}),$$
   totaling **12 field operations (5 `FADD`, 7 `FMUL`) and 5 constants per partial round**.
5. **Partial-Round Exit into Round 60 (3 `FADD`, 0 `FMUL`, 3 constants $c[297..299]$):**
   Add the accumulated normalized constant offsets entering Round 60:
   $$u_0 \leftarrow (u_0 + c_{60,0}) \bmod p, \quad u_1 \leftarrow (u_1 + c_{60,1}) \bmod p, \quad u_2 \leftarrow (u_2 + c_{60,2}) \bmod p \;\;(3\text{ FADD}).$$
6. **Terminal Full Rounds 60, 61, 62 ($3 \times 9 = 27$ `FADD`, $3 \times 15 = 45$ `FMUL`, 27 constants $c[300..326]$):**
   For each round $t \in \{60, 61, 62\}$ with lane scales $s_{\text{full}, j}$ updated to $s_{\text{next}, i} = M_{i,0} s_{\text{full}, 0}^5 \bmod p$:
   $$z_j \leftarrow u_j^5 \bmod p \;\;(9\text{ FMUL}), \qquad u_i \leftarrow (z_0 + m_{t,i,1} z_1 + m_{t,i,2} z_2 + c_{t,i}) \bmod p \;\;(6\text{ FMUL} + 9\text{ FADD}).$$
7. **Round 63 Final Output Lane 0 (2 `FADD`, 11 `FMUL`, 2 constants $c[327..328]$):**
   Compute $z_j = u_j^5 \bmod p$ for $j \in \{0, 1, 2\}$ (9 `FMUL`). Setting $\operatorname{outscale}(\rho_0) = M_{0,0} s_{63,0}^5 \bmod p \ne 0$ and $\alpha_{63,j} = M_{0,j} s_{63,j}^5 \operatorname{outscale}(\rho_0)^{-1} \bmod p$ ($\alpha_{63,0} = 1$), output:
   $$F_{\rho_0}(x) = (z_0 + \alpha_{63,1} z_1 + \alpha_{63,2} z_2) \bmod p \;\;(2\text{ FMUL} + 2\text{ FADD}).$$

By construction, for every $x \in \mathbb{F}_p$ and every $\rho_0 \in \mathbb{F}_p^*$:
$$\operatorname{digest}\bigl(nk(W_{\rho_0}(x)),\; \rho(W_{\rho_0}(x))\bigr) = \bigl(\operatorname{outscale}(\rho_0) \cdot F_{\rho_0}(x)\bigr) \bmod p,$$
where $\operatorname{outscale}(1) = \text{0x8644200abf8cd4035dc449088ab93750ba0d9968f428235fce6f63bb58d8c93} \ne 0$. Since $\operatorname{outscale}(\rho_0) \in \mathbb{F}_p^*$, $F_{\rho_0}(x_a) = F_{\rho_0}(x_b) \iff \operatorname{digest}_a = \operatorname{digest}_b$.

### 2.4 Theorem 1 (Exact Monomial $\rho_0$-Scaling of Step Constants)
**Theorem 1.** *Let $c^{(1)}[0 \dots 328]$ be the 329 base step constants computed at $\rho_0 = 1$. For any trial coin $\rho_0 \in \mathbb{F}_p^*$, every step constant $c^{(\rho_0)}[idx]$ is a pure monomial in $\rho_0$ times $c^{(1)}[idx]$:*
1. $s_{2,j}(\rho_0) = \rho_0 s_{2,j}(1) \implies s_{3,i}(\rho_0) = \rho_0^5 s_{3,i}(1) \implies s_{60,1}(\rho_0) = \rho_0^{25} s_{60,1}(1)$, $s_{60,2}(\rho_0) = \rho_0^{25} s_{60,2}(1)$, and by induction $sp_k(\rho_0) = \rho_0^{5^{k+2}} sp_k(1)$ for all $0 \le k \le r$.
2. *Entry offsets $c[0..1]$ ($e_1, e_2$) scale by $\rho_0^{-1}$.*
3. *Round-2 matrix ratios $m_{2,i,j}$ and Round-3 ratios $a_{3,u_0}, a_{3,h_1}, a_{3,h_2}$ have homogeneous numerator and denominator degree in $\rho_0$ and are **invariant** ($\rho_0^0$); Round-2 constant offsets $c[4], c[7], c[10]$ ($c_{3,i}$) scale by $\rho_0^{-5}$.*
4. *In partial round $k \in \{0, \dots, r-1\}$ ($cb = 17 + 5k$): $Q_k(\rho_0) = \rho_0^{25} Q_k(1)$ while $q^{(k)}$ and $rc_0^{(k)}$ are independent of $\rho_0$. Thus $c[cb+0] = c_p^{(k)}$ scales by $\rho_0^{-5^{k+2}}$; $c[cb+1..2] = w_{k,1..2}$ scale by $\rho_0^{25 - 5^{k+3}}$; and $c[cb+3..4] = v_{k,1..2}$ scale by $\rho_0^{5^{k+3} - 25}$.*
5. *At partial-round exit ($cb_{60} = 17 + 5r = 297$): $c[297] = c_{60,0}$ scales by $\rho_0^{-5^{r+2}}$, while $c[298..299] = c_{60,1..2}$ scale by $\rho_0^{-25}$.*
6. *In Round 60 (`idx_f = 0`, $cb = 300 + 3i$): $s_{\text{full}} = (\rho_0^{5^{r+2}}, \rho_0^{25}, \rho_0^{25})$ and $s_{\text{next}, i}$ has degree $5^{r+3}$, so $c[cb+0..1] = m_{60,i,1..2}$ scale by $\rho_0^{125 - 5^{r+3}}$ and $c[cb+2] = c_{60,i}$ scales by $\rho_0^{-5^{r+3}}$. In Rounds 61 and 62 (`idx_f` $\in \{1, 2\}$), all three lanes have equal degree $5^{r+2+\text{idx\_f}}$, so $m_{t,i,1..2}$ are **invariant** and $c[cb+2] = c_{t,i}$ scales by $\rho_0^{-5^{r+3+\text{idx\_f}}}$. Finally, $\alpha_{63,1..2}$ ($c[327..328]$) are **invariant** and $\operatorname{outscale}(\rho_0) = \rho_0^{5^{r+6}} \operatorname{outscale}(1) \bmod p$.*

Theorem 1 allows the register machine to store only the fixed $\rho_0 = 1$ constant table in `const_mem` and derive all 329 scaled step constants online during `setup` after drawing `RAND r_rho0`.

---

## 3. Gap-Free Distinguished-Point Walk and Lemma 3 Random-Mapping Lower Bound

### 3.1 Value-Only (Gap-Free) Distinguished-Point Table and Online Left-Gap Recovery
Prior distinguished-point implementations (`43caeb6a`, `874894cf`, `9fb982e8`) stored both a $\text{VB}$-bit DP value array (`val[0 .. MCAP-1]`) and a $\text{WG}$-bit inter-DP step-gap array (`gap[0 .. MCAP-1]`) in `table_mem`, consuming over $41\%$ of the $1\text{ MiB}$ RAM budget for `gap[0 .. MCAP-1]` even though `gap` is never read during `dp_scan_loop` and only a single entry `gap[match_idx]` is ever read once per trial upon collision.

We eliminate the gap array from `table_mem` altogether ($\text{g\_words} = 0$) and keep only the most recent DP step index `r_prev_dp_t` and most recent DP value `r_prev_dp_val` (initialized to $0$ and $x_0$, respectively) in registers:
1. **Walk and Value-Only DP Storage:** The walk iterates $x_t = F_{\rho_0}(x_{t-1})$ for $t = 1, 2, \dots$ up to step horizon $S = n + d$ in unrolled blocks of $K = 31$ steps. A state $x_t$ is a **distinguished point (DP)** if $0 \le x_t < \Delta < 2^{\text{VB}}$ ($\text{VB} = 143$). When a DP $x_{t_c}$ is visited, the machine computes the current step gap `r_gap = cur_t - r_prev_dp_t` in a 256-bit register (which never overflows since $S < 2^{128}$) and scans the previously stored DP values $\text{val}[0 \dots c-2]$. If no match is found, only the 143-bit value $x_{t_c}$ is bit-packed into `table_mem` (up to capacity $\text{MCAP} = 51,475$), and `r_prev_dp_t` and `r_prev_dp_val` are updated to `cur_t` and $x_{t_c}$. Because $0 \le x_{t_c} < \Delta < 2^{143}$, storing the low 143 bits of $x_{t_c}$ is **lossless**: $\text{val}[c-1]$ equals the exact 255-bit field element $x_{t_c} \in \mathbb{F}_p$.
2. **Online Left-Gap Measurement and Shared-Counter Recovery (`dp_match_found`):** When $x_{t_{\text{cur}}}$ first matches a stored DP $\text{val}[\text{match\_idx}]$ ($0 \le \text{match\_idx} < \text{r\_count}$), let $x_{\text{target}} = x_{t_{\text{cur}}}$. The right segment starting state $x_{\text{right}} = \text{r\_prev\_dp\_val}$ and length $g_{\text{right}} = \text{r\_gap} = t_{\text{cur}} - t_{\text{prev}}$ are already in registers! The left segment starting state $x_{\text{left}}$ is loaded from `start_mem[0]` ($x_0$) if $\text{match\_idx} = 0$, or unpacked from $\text{val}[\text{match\_idx} - 1]$ if $\text{match\_idx} > 0$. Because $x_{\text{left}}$ and $x_{\text{target}} = \text{val}[\text{match\_idx}]$ are consecutive checkpoints on the walk prior to the first repeat, $x_{\text{target}}$ is the **first** state along the trajectory from $x_{\text{left}}$ that equals $x_{\text{target}}$. The machine recovers $g_{\text{left}}$ online (`rec_measure_loop`) by stepping $y$ forward from $x_{\text{left}}$ (up to cap $B_{\text{left}}$ steps) until $y = x_{\text{target}}$, counting the exact step length $g_{\text{left}} \ge 1$.
3. **Positioning and Lockstep with Shared Step Budget $B_{12}$:** Once $g_{\text{left}}$ is known, $(x_{\text{left}}, g_{\text{left}})$ and $(x_{\text{right}}, g_{\text{right}})$ are ordered so $g_{\text{right}} \ge g_{\text{left}}$. A single shared `step_sub` counter `r_count` (capped at $B_{12}$) tracks all `step_sub` calls across both positioning ($d_{\text{diff}} = g_{\text{right}} - g_{\text{left}}$ single-pointer steps on $x_{\text{right}}$) and lockstep ($2$ `step_sub` calls per lockstep iteration on $x_{\text{left}}, x_{\text{right}}$ until $F_{\rho_0}(x_{\text{left}}) = F_{\rho_0}(x_{\text{right}})$). By the exact algebraic identity:
   $$|g_{\text{right}} - g_{\text{left}}| + 2 \min(g_{\text{left}} - L,\; g_{\text{right}} - L) = |(r_2 + L) - (r_1 + L)| + 2 \min(r_1, r_2) = r_1 + r_2,$$
   the total number of `step_sub` evaluations across positioning and lockstep combined is **identically $r_1 + r_2$**, where $r_1 = i^* - t_{\text{prev,left}} \ge 1$ and $r_2 = j^* - t_{\text{prev,right}} \ge 1$ are the pre-merge non-DP run lengths immediately preceding $i^*$ and $j^*$.

### 3.2 Lemma 3 (Random-Mapping Success Probability Lower Bound)
**Lemma 3.** *Let $F: \mathbb{F}_p \to \mathbb{F}_p$ be a uniform random mapping and $x_0 \in \mathbb{F}_p$ a uniform starting point. For integer parameters $n, d \ge 1$, $B_{\text{left}} \ge d$, $B_{12} \ge B_{\text{left}}$, $S = n + d < \Delta < p$, and $\text{MCAP} \ge 1$, define:*
$$\theta_{\text{lo}} = \frac{\Delta - S}{p}, \qquad \theta_{\text{hi}} = \frac{\Delta}{p - S}, \qquad \mu = S \theta_{\text{hi}}, \qquad m = \text{MCAP} + 1.$$
*If $\mu < m$, the probability $P_{\text{succ}}$ that a single trial of the algorithm in Section 3.1 halts with `'success'` and outputs a valid collision satisfies:*
$$P_{\text{succ}} \ge 1 - \sum_{i=1}^7 e_i,$$
*where:*
$$e_1 = \exp\!\left(-\frac{n(n+1)}{2p}\right), \qquad e_2 = \frac{n}{p}, \qquad e_3 = \frac{nd}{p}, \qquad e_4 = \exp(-\theta_{\text{lo}} d),$$
$$e_5 = d \theta_{\text{hi}} \exp(-\theta_{\text{lo}} B_{\text{left}}), \qquad e_6 = (1 + B_{\text{left}} \theta_{\text{hi}}) \exp\bigl(-\theta_{\text{lo}} (B_{12} - 1)\bigr), \qquad e_7 = \exp\!\left(m - \mu - m \ln\!\frac{m}{\mu}\right).$$

*Proof.* Let $x_0, x_1, \dots$ be the walk states and let $j^* = \min\{j \ge 1 : x_j \in \{x_0, \dots, x_{j-1}\}\}$ be the step of the first state repeat, with $x_{j^*} = x_{i^*}$ for $0 \le i^* < j^*$.
1. **No repeat by step $n$ ($E_1$), start on cycle ($E_2$), and short cycle ($E_3$):** By standard birthday bounds on $\mathbb{F}_p$, $\Pr[j^* > n] = \prod_{k=1}^n (1 - k/p) \le \exp(-n(n+1)/(2p)) = e_1$; $\Pr[j^* \le n \text{ and } i^* = 0] = \sum_{j=1}^n \frac{1}{p}\prod_{k=1}^{j-1}(1 - k/p) \le n/p = e_2$; and $\Pr[j^* \le n, i^* \ge 1, j^* - i^* < d] \le \sum_{j=1}^n \frac{\min(j,d)}{p} \le nd/p = e_3$. On $\neg E_1 \wedge \neg E_2 \wedge \neg E_3$, we have $1 \le i^* < j^* \le n$ and cycle length $j^* - i^* \ge d$, so $x_0, x_1, \dots, x_{j^*-1}$ are $j^*$ distinct elements of $\mathbb{F}_p$ and $i^* + d - 1 \le j^* - 1$.
2. **Fresh-state DP density bounds ($\theta_{\text{lo}}, \theta_{\text{hi}}$):** Up to step $S = n + d$ (and in particular across the distinct states $x_1, \dots, x_{j^*-1}$), at most $S$ states have been revealed. Conditional on any history of visited states at a fresh transition $x_t = F(x_{t-1})$, at least $\Delta - S$ of the $\le p$ unvisited field elements lie in $[0, \Delta)$ and at most $\Delta$ of the $\ge p - S$ unvisited field elements lie in $[0, \Delta)$, so the conditional DP hit probability $p_t$ at every fresh step satisfies $\theta_{\text{lo}} \le p_t \le \theta_{\text{hi}}$.
3. **Post-merge DP detection within $d$ steps ($E_4$):** On $\neg E_1 \wedge \neg E_2 \wedge \neg E_3$, the $d$ states $x_{i^*}, x_{i^*+1}, \dots, x_{i^*+d-1}$ lie in $\{x_1, \dots, x_{j^*-1}\}$. The probability that none of them lies in $[0, \Delta)$ is at most $(1 - \theta_{\text{lo}})^d \le \exp(-\theta_{\text{lo}} d) = e_4$. On $\neg E_4$, there is a unique first post-merge DP offset $L \in \{0, 1, \dots, d - 1\}$ such that $x_{i^*}, \dots, x_{i^*+L-1} \notin [0, \Delta)$ and $x_{i^*+L} = x_{j^*+L} \in [0, \Delta)$, visited at steps $t_{\text{first}} = i^* + L \le j^* - 1$ and $t_{\text{second}} = j^* + L \le n + d - 1 < S$.
4. **Online left-gap measurement cap ($E_5$):** Let $t_{\text{prev,left}} = i^* - r_1 \in \{0, \dots, i^* - 1\}$ ($1 \le r_1 \le i^*$) be the step of the checkpoint $x_{\text{left}}$ immediately preceding $t_{\text{first}} = i^* + L$, so $x_{i^* - r_1 + 1}, \dots, x_{i^* - 1} \notin [0, \Delta)$ and $g_{\text{left}} = r_1 + L$. On $\neg E_4$, the event $\{g_{\text{left}} > B_{\text{left}}\}$ is the disjoint union over $\ell \in \{0, \dots, d - 1\}$ of $\{L = \ell \text{ and } r_1 \ge B_{\text{left}} + 1 - \ell\}$. Since $r_1 \le i^*$, this requires $i^* \ge B_{\text{left}} + 1 - \ell$ and that the $B_{\text{left}} - \ell$ pre-merge states $x_{i^* - (B_{\text{left}} - \ell)}, \dots, x_{i^* - 1}$ (whose indices lie in $\{1, \dots, i^* - 1\}$) all avoid $[0, \Delta)$, while the $\ell + 1$ post-merge states $x_{i^*}, \dots, x_{i^*+\ell}$ (whose indices lie in $\{i^*, \dots, j^* - 1\}$, disjoint from $\{1, \dots, i^* - 1\}$) satisfy $x_{i^*}, \dots, x_{i^*+\ell-1} \notin [0, \Delta)$ and $x_{i^*+\ell} \in [0, \Delta)$. For each $\ell \in \{0, \dots, d - 1\}$, this joint event has probability at most:
   $$(1 - \theta_{\text{lo}})^{B_{\text{left}} - \ell} \cdot (1 - \theta_{\text{lo}})^{\ell} \theta_{\text{hi}} = \theta_{\text{hi}} (1 - \theta_{\text{lo}})^{B_{\text{left}}}.$$
   Summing over all $d$ values $\ell \in \{0, \dots, d - 1\}$ gives $\Pr[\neg E_4 \text{ and } g_{\text{left}} > B_{\text{left}} \mid \neg E_1 \wedge \neg E_2 \wedge \neg E_3] \le d \theta_{\text{hi}} (1 - \theta_{\text{lo}})^{B_{\text{left}}} \le d \theta_{\text{hi}} \exp(-\theta_{\text{lo}} B_{\text{left}}) = e_5$.
5. **Shared positioning + lockstep cap ($E_6$):** On $\neg E_4 \wedge \neg E_5$, we have $g_{\text{left}} = r_1 + L \le B_{\text{left}}$, which implies $1 \le r_1 \le \min(i^*, B_{\text{left}})$. Let $t_{\text{prev,right}} = j^* - r_2$ be the step of the DP immediately preceding $t_{\text{second}} = j^* + L$. Because $x_{i^* + s} = x_{j^* + s} \notin [0, \Delta)$ for $0 \le s < L$ and $x_{i^* + L} \in [0, \Delta)$ at step $i^* + L < j^*$, we have $i^* \le i^* + L \le t_{\text{prev,right}} \le j^* - 1$, so $1 \le r_2 \le j^* - i^*$ and the $r_2 - 1$ states $x_{j^* - r_2 + 1}, \dots, x_{j^* - 1}$ all avoid $[0, \Delta)$ and have indices in $\{i^* + 1, \dots, j^* - 1\}$. For each fixed $r \in \{1, \dots, \min(i^*, B_{\text{left}})\}$, the event $\{r_1 = r \text{ and } r_1 + r_2 \ge B_{12} + 1\}$ requires $r_2 \ge B_{12} + 1 - r$ (which is empty unless $B_{12} + 1 - r \le j^* - i^*$), so:
   - the $r - 1$ left states $x_{i^* - r + 1}, \dots, x_{i^* - 1}$ (indices in $\{1, \dots, i^* - 1\}$) avoid $[0, \Delta)$, and if $r < i^*$, $x_{i^* - r} \in [0, \Delta)$ (probability $\le \theta_{\text{hi}}$; if $r = i^*$, $x_{i^* - r} = x_0$ has probability $\le 1$);
   - the $B_{12} - r$ right states $x_{j^* - (B_{12} - r)}, \dots, x_{j^* - 1}$ (indices in $\{i^* + 1, \dots, j^* - 1\}$, disjoint from $\{1, \dots, i^* - 1\}$) avoid $[0, \Delta)$.
   Thus the $r = i^*$ term (at most one value of $r$) has probability at most $(1 - \theta_{\text{lo}})^{(i^* - 1) + (B_{12} - i^*)} = (1 - \theta_{\text{lo}})^{B_{12} - 1}$, and each of the $\le B_{\text{left}}$ terms with $1 \le r < i^*$ has probability at most $\theta_{\text{hi}} (1 - \theta_{\text{lo}})^{(r - 1) + (B_{12} - r)} = \theta_{\text{hi}} (1 - \theta_{\text{lo}})^{B_{12} - 1}$. Summing over $1 \le r \le \min(i^*, B_{\text{left}})$ yields:
   $$\Pr[\neg E_4 \wedge \neg E_5 \text{ and } r_1 + r_2 > B_{12} \mid \neg E_1 \wedge \neg E_2 \wedge \neg E_3] \le (1 + B_{\text{left}} \theta_{\text{hi}}) (1 - \theta_{\text{lo}})^{B_{12} - 1} \le (1 + B_{\text{left}} \theta_{\text{hi}}) \exp\bigl(-\theta_{\text{lo}} (B_{12} - 1)\bigr) = e_6.$$
6. **Table capacity overflow ($E_7$):** Over at most $S$ fresh steps, the total number of DP hits is stochastically dominated by $\operatorname{Binomial}(S, \theta_{\text{hi}})$ with mean $\mu = S \theta_{\text{hi}}$. By the multiplicative Chernoff bound for $m = \text{MCAP} + 1 > \mu$, $\Pr[\#\text{DPs} \ge m] \le \exp(m - \mu - m \ln(m/\mu)) = e_7$.

By the union bound over $E_1, \dots, E_7$, $P_{\text{succ}} \ge 1 - \sum_{i=1}^7 e_i$. $\square$

### 3.3 Concrete Parameters and Numerical Evaluation at $r = 56$
We instantiate the walk with the following exact parameters:
- $\Delta = 8597264981472998977621816562396716044573835$ ($\lceil \log_2 \Delta \rceil = 143 = \text{VB}$)
- $n = 169242150199934234679024572255841649827$
- $d = 34816705660447746846788047350633493$
- $S = n + d = 169276966905594682425871360303192283320$ ($S = 31 \times 5,460,547,319,535,312,336,318,430,977,522,331,720$)
- $B_{\text{left}} = 45793732783567636084750236360601113$
- $B_{12} = 46635529342089099983366968646641575$
- $\text{MCAP} = 51475$, $\text{VB} = 143$, $K = 31$.

Evaluating Lemma 3 in 100-digit decimal arithmetic yields:
- $\theta_{\text{lo}} = (\Delta - S) / p = 2.969838703536 \times 10^{-34}$
- $\theta_{\text{hi}} = \Delta / (p - S) = 2.969897179712 \times 10^{-34}$
- $\mu = S \theta_{\text{hi}} = 50273.51866032 < m = 51476$

| Term | Failure Event | Bound Formula | Numerical Value |
| :--- | :--- | :--- | :--- |
| $e_1$ | No state repeat in $n$ steps | $\exp(-n(n+1)/(2p))$ | $6.097355636859 \times 10^{-1}$ |
| $e_2$ | Starting state $x_0$ on cycle ($i^* = 0$) | $n / p$ | $5.846414943013 \times 10^{-39}$ |
| $e_3$ | Second repeat within $d$-step window | $n d / p$ | $2.035529082397 \times 10^{-4}$ |
| $e_4$ | No DP within $d$ steps after merge | $\exp(-\theta_{\text{lo}} d)$ | $3.231432266041 \times 10^{-5}$ |
| $e_5$ | Left-gap measurement reaches cap $B_{\text{left}}$ | $d \theta_{\text{hi}} \exp(-\theta_{\text{lo}} B_{\text{left}})$ | $1.282697168507 \times 10^{-5}$ |
| $e_6$ | Positioning + lockstep reaches cap $B_{12}$ | $(1 + B_{\text{left}} \theta_{\text{hi}}) \exp(-\theta_{\text{lo}}(B_{12}-1))$ | $1.410529738508 \times 10^{-5}$ |
| $e_7$ | DP table overflow ($> 51,475$ DPs) | $\exp(m - \mu - m \ln(m/\mu))$ | $6.362729277117 \times 10^{-7}$ |
| **Sum** | **Total failure probability $\sum_{i=1}^7 e_i$** | | **$0.609998999459$** |
| **$P_{\text{succ}}$** | **Single-trial success probability** | $1 - \sum_{i=1}^7 e_i$ | **$0.390001000541 \ge 0.39$** |

---

## 4. Concrete Register-Machine Architecture, Memory Accounting, and Worst-Case Ledger

### 4.1 Register File and Constant Table Layout
By eliminating the gap array (`g_words = 0`), our compiled register machine (`build_program` in `experiments/r56_listing.py`) expands the DP table capacity by $77.5\%$ (from $28,992$ to $51,475$ entries) while simultaneously increasing the loop unrolling factor from $K = 23$ to **$K = 31$** within the exact $1\text{ MiB} = 1,048,576$-byte threshold:

- **Register file (`num_registers = 349` words = $11,168$ bytes):**
  - `r_zero = 0` (hardwired 0), `r_x = 1` (active state $x$, and lane 0 `r_u0` inside `emit_step_807`).
  - `r_u1 = 2, r_u2 = 3, r_z0 = 4, r_z1 = 5, r_z2 = 6, r_t = 7` (6 step-scratch registers; dead at `after_step_j`, `dp_handler`, and between steps in `recovery`).
  - `r_Delta = 8`, `r_S = 9`, `r_MCAP = 10`, `r_mask_vb = 11`, `r_step = 12`, `r_count = 13`, `r_prev_dp_t = 14`, `r_prev_dp_val = 15`, `r_a = 16`, `r_rho0 = 17`, `r_ret = 18`, `r_gap = 19` (12 persistent walk/control registers).
  - `c_base = 20 .. 348` (the $49 + 5r = 329$ scaled step constants for the current trial coin $\rho_0$).
- **Constant table (`const_mem` = `342` words = $10,944$ bytes):**
  - Indices `0..328`: the 329 base ($\rho_0 = 1$) step constants $c^{(1)}[0 \dots 328]$.
  - Indices `329..341` (`idx_meta + 0 .. 12`): the 13 full-width walk and reconstruction constants $[\Delta, S, B_{\text{left}}, B_{12}, p - 2, \text{INV5}, d_0, U_0, A_{\text{line}}, V_0, B_{\text{line}}, c_0^{(0)}, c_1^{(0)}]$.
- **DP Table Memory (`table_mem` = `28,755` words = $920,160$ bytes) and `start_mem` ($1$ word = $32$ bytes):**
  - Value array: $\text{v\_words} = \lceil 51475 \times 143 / 256 \rceil = 28,754$ words (`table_mem[0 .. 28753]`).
  - Sentinel word: $1$ word (`table_mem[28754]`), giving $\text{t\_words} = 28,754 + 1 = 28,755$ words.
  - **Boundary safety proof:** Every entry $i \in \{0, \dots, 51474\}$ accesses `table_mem[w_idx]` and `table_mem[w_idx + 1]`, where $w_{\text{idx}} = \lfloor 143 i / 256 \rfloor \le 28,753$. Thus $w_{\text{idx}} + 1 \le 28,754 < \text{t\_words} = 28,755$, which lies in the dedicated sentinel word `table_mem[28754]`.

### 4.2 Exact Memory Accounting Table
| Memory Component | Count | Unit Size | Total Bytes |
| :--- | ---: | ---: | ---: |
| Program instructions (`ins`) | $26,568$ instructions | $4$ bytes | $106,272$ |
| Register file (`reg`) | $349$ words | $32$ bytes | $11,168$ |
| Constant memory (`const_mem`) | $342$ words | $32$ bytes | $10,944$ |
| DP table memory (`table_mem`) | $28,755$ words | $32$ bytes | $920,160$ |
| Start-state word (`start_mem`) | $1$ word | $32$ bytes | $32$ |
| **Total Memory** | | | **$1,048,576 = 2^{20}$ ($1\text{ MiB}$)** |

Because total memory is **exactly $1,048,576$ bytes $= 2^{20}$ bytes ($1\text{ MiB}$)**, $\text{memory\_log2\_bytes} = 20.0$, so $M' = \max(1, \text{memory} / 1\text{ MiB}) = 1$ and the memory penalty is **identically zero**.

### 4.3 Exact Worst-Case Operation Ledger Across All Execution Phases
We bound the total primitive operations executed in a single trial across all five program sections:

1. **Phase 1: `setup` (`148,790` primitive operations):**
   - Initial constant/mask setup (6 instructions, 2 `LOADC`): **8 ops**.
   - Coin draws (`RAND r_rho0`, `BNE`, zero-guard `ADDI`, `RAND r_x`, `STORE_START r_x`): at most **7 ops**.
   - Load 49 non-partial-round base step constants (`49 LOADC`): **98 ops**.
   - Shared `pow_sub` call for $\rho_0^{-1} = \rho_0^{p-2} \bmod p$: call sequence (`LOADC`, `MOV`, `ADDI`, `JMP` = 5 ops) + `pow_sub` header (3 `ADDI` = 3 ops) + 255 loop iterations ($255 \times 9 + \operatorname{popcount}(p - 2) = 2295 + 77 = 2372$ ops) + `JR` (1 op) = **2,381 ops**.
   - Full-round entry scaling (`2 FMUL`, `4 pow5`, `3 FMUL`, `2 MOV`): **19 ops**.
   - Partial-round constant scaling (`setup_p_loop`, $r = 56$ iterations using `table_mem[0..279]` as temporary buffer before zeroing): header (3 ops) + $56 \times 39 = 2,184$ ops + $280 \text{ LOAD} \times 2 = 560$ ops = **2,747 ops**.
   - Terminal full-round constant scaling (34 instructions, all 1-op): **34 ops**.
   - Zeroing `table_mem[0..28754]` (`setup_zero_loop`): header (2 ops) + $28,755 \times (\text{STORE}(2) + \text{ADDI}(1) + \text{BLT}(2)) = 143,775$ ops + trail-state init (`3 ADDI + 1 MOV` = 4 ops) = **143,781 ops**.
   - **Total `setup_ops`:** $8 + 7 + 98 + 2381 + 19 + 2747 + 34 + 143781 = 2383 + 47 \times 56 + 5 \times 28755 = \mathbf{148,790}$ operations.

2. **Phase 2: Unrolled Trail Walk (`trail_ops`):**
   - Each of the $K = 31$ unrolled steps in `trail_block` executes `emit_step_807` ($807$ ops) + `BLT r_x, r_Delta, dp_stub_j` ($2$ ops) = $809$ ops.
   - Each block ends with `ADDI r_step, r_step, 31` ($1$ op) + `BLT r_step, r_S, trail_block` ($2$ ops) = $3$ ops, giving $\text{block\_cost} = 31 \times 809 + 3 = \mathbf{25,082}$ ops per block.
   - Over $\text{blocks} = S / 31 = 5,460,547,319,535,312,336,318,430,977,522,331,720$ blocks:
     $$\text{trail\_ops} = \text{blocks} \times 25,082 = \mathbf{136,961,447,868,584,704,019,538,885,778,215,124,201,040} \text{ ops}.$$

3. **Phase 3: Non-Colliding DP Table Insertions (`dp_ops`):**
   - For the $c$-th non-colliding DP ($0 \le c < \text{MCAP} = 51,475$): stub (`3` ops) + header (`7` ops) + scan of $c$ stored entries ($20c$ ops: `BGE`(2), `SHRI`(1), `2 LOAD`(4), `ADDI`(1), `AND`(1), `SHR`(1), `ADDI`(1), `SUB`(1), `SHL`(1), `OR`(1), `AND`(1), `BEQ`(2), `2 ADDI`(2), `JMP`(1)) + scan-done `BGE` (2 ops) + capacity `BGE` (2 ops) + pack 143-bit value (17 ops) + state update & `JR` (`ADDI`, `MOV`, `MOV`, `JR` = 4 ops) = **$20c + 35$ ops**.
   - Summing over $c = 0 \dots \text{MCAP} - 1$:
     $$\text{dp\_ops} = 10 \cdot \text{MCAP}(\text{MCAP} - 1) + 35 \cdot \text{MCAP} = \mathbf{26,498,043,125} \text{ ops}.$$

4. **Phase 4 & 5: Colliding DP Scan, Gap-Free Recovery, and Output Reconstruction (`last_ops`):**
   - Colliding DP stub + header (`10` ops) + scan up to `match_idx <= MCAP - 1` ($\le 20(\text{MCAP} - 1) + 17 = 20 \cdot \text{MCAP} - 3 = 1,029,497$ ops).
   - Unpack $x_{\text{left}}$ (`dp_match_found`): `MOV` (1) + `BEQ` (2) + inline 143-bit unpack of `val[match_idx - 1]` (16 ops, dominating `LOAD_START` = 2 ops) = **19 ops**.
   - Online left-gap measurement (`rec_measure_loop`): setup (`LOADC`, `MOV`, `ADDI` = **4 ops**) + at most $B_{\text{left}}$ iterations, each executing `BGE` (2) + `ADDI` (1) + `JMP` (1) + `step_sub` ($807 + 1 = 808$) + `ADDI` (1) + `BNE` (2) = **$815$ ops/step**.
   - Segment ordering + positioning/lockstep init: `MOV` (1) + `BGE` (2) + 6 swap `MOV`s (6) + `SUB` (1) + `LOADC` (2) + `2 ADDI` (2) = **14 ops**.
   - Positioning (`rec_pos_loop`) + lockstep (`rec_lock_loop`) under shared counter $B_{12}$: each positioning `step_sub` call executes `2 BGE` (4) + `ADDI` (1) + `JMP` (1) + `step_sub` (808) + `2 ADDI` (2) + `JMP` (1) = **$817$ ops per `step_sub` call**; exiting `rec_pos_loop` into `rec_lock_loop` executes `BGE` (2) + `MOV` (1) + `BEQ` (2) = **5 ops**; each lockstep iteration executes 2 `step_sub` calls in `ADDI` (1) + `BGE` (2) + `3 MOV` (3) + `ADDI` (1) + `JMP` (1) + `step_sub` (808) + `2 MOV` (2) + `ADDI` (1) + `JMP` (1) + `step_sub` (808) + `MOV` (1) + `ADDI` (1) + `BNE` (2) = $1,632$ ops ($816 \le 817$ ops per `step_sub` call). Across at most $B_{12}$ total `step_sub` calls in positioning and lockstep combined, the cost is at most **$817 \cdot B_{12} + 5$ ops**.
   - Output reconstruction: 6 calls to `pow_sub` with exponent $\text{INV5}$ ($6 \times 2,430$ ops) + 44 field operations + `HALT 'success'` = **$14,625$ ops**.
   - Every non-success halt branch is strictly dominated by this bound:
     $$\text{last\_ops} = 10 + (20 \cdot \text{MCAP} - 3) + 19 + 4 + 815 \cdot B_{\text{left}} + 14 + 817 \cdot B_{12} + 5 + 14,625 = \mathbf{75,423,119,691,094,418,095,482,256,018,197,118,044} \text{ ops}.$$

5. **Total Worst-Case Single-Trial Operation Bound $W$:**
   $$\text{worst\_case\_trial} = \text{setup\_ops} + \text{trail\_ops} + \text{dp\_ops} + \text{last\_ops} = 137,036,870,988,275,798,437,634,368,034,259,819,510,999 \text{ ops}.$$
   Adding an explicit margin of $2^{48} = 281,474,976,710,656$ operations gives our filed bound:
   $$W = \text{worst\_case\_trial} + 2^{48} = \mathbf{137,036,870,988,275,798,437,634,368,315,734,796,221,655} \text{ primitive operations}.$$
   Dividing by $C(56) = 1392$:
   $$T = \frac{W}{1392} \approx 9.8446028008818820717 \times 10^{37} \implies \log_2 T = 126.210672509874 \le \mathbf{126.21068}.$$

---

## 5. Heuristic Disclosures, Empirical Verification, Sensitivity, and Limitations

### 5.1 Heuristic `H1` (`score-critical`: Random-Mapping Model on the Origin-Shifted BBLP Line)
- **Statement:** For a uniformly chosen trial coin $\rho_0 \in \mathbb{F}_p^*$ and starting point $x_0 \in \mathbb{F}_p$, the trail generated by the 807-operation step function $F_{\rho_0}(x)$ on the origin-shifted BBLP 2-round affine input line $W_{\rho_0}(x) = (\rho_0 x - d_0) \bmod p$ satisfies the success probability lower bound of Lemma 3 ($P_{\text{succ}} \ge 0.390001000541 \ge 0.39$) derived for a uniform random mapping on $\mathbb{F}_p$.
- **Supporting Evidence (`experiment:r56-search-w14` and `experiment:r56-listing-w10`):**
  1. In declared experiment `r56-search-w14` (`experiments/r56_search.py`), the exact $r = 56$ step function $F_{\rho_0}$ with gap-free DP recovery is evaluated on the 256 deterministic organizer trials (`seed = "hashsmash-public-seed-v1"`) at reduced width $w = 14$ ($N = 2^{14} = 16,384$, $K = 31, \text{VB} = 143, \text{MCAP} = 64, \Delta = 512, S = 217, B_{\text{left}} = 256, B_{12} = 256$). Across the 256 single-seed trials, it achieves **124 / 256 (`0.4844`)** organizer-verified 14-bit Orchard Poseidon collisions (`124` `success`, `131` `no-repeat`, `1` `start-on-cycle`, `0` repeated pairs).
  2. In declared experiment `r56-listing-w10` (`experiments/r56_listing.py`), the exact $r = 56$ step function $F_{\rho_0}$ is evaluated on the 256 deterministic organizer trials (`seed = "hashsmash-public-seed-v1"`) at reduced width $w = 10$ ($N = 2^{10} = 1,024$, $K = 31, \text{VB} = 143, \text{MCAP} = 32, \Delta = 64, S = 93, B_{\text{left}} = 96, B_{12} = 96$), achieving **151 / 256 (`0.5898`)** organizer-verified 10-bit Orchard Poseidon collisions (`151` `success`, `101` `no-repeat`, `4` `start-on-cycle`, `0` repeated pairs).
  3. Both declared organizer experiments agree closely with the single-trial collision probability of an idealized uniform random function $f: [0, 2^w) \to [0, 2^w)$ under the identical walk parameters $(S, \Delta, B_{\text{left}}, B_{12}, \text{MCAP})$:

| Declared Experiment | Width $w$ | Domain $2^w$ | Walk $(S, \Delta, B_{\text{left}}, B_{12}, \text{MCAP})$ | Poseidon $r=56$ (`hashsmash-public-seed-v1`) | Ideal Uniform Random Function |
| :--- | :---: | ---: | :---: | :---: | :---: |
| `r56-listing-w10` | $10$ | $1,024$ | $(93, 64, 96, 96, 32)$ | $151 / 256 = 0.5898$ | $0.5314$ ($\sigma_{256} = 0.0312$) |
| `r56-search-w14` | $14$ | $16,384$ | $(217, 512, 256, 256, 64)$ | $124 / 256 = 0.4844$ | $0.4634$ ($\sigma_{256} = 0.0312$) |

- **Extrapolation and Sensitivity:** Extrapolates from the executed reduced widths $w \in \{10, 14\}$ to the full 255-bit prime field $\mathbb{F}_p$ across 62 algebraic rounds (degree $5^{62}$). Even if the effective DP hit density $\theta_{\text{lo}}$ deviated by $\pm 1\%$, $e_4 + e_5 + e_6 + e_7 \approx 5.99 \times 10^{-5}$ changes by less than $10^{-5}$, shifting the required $n$ (and `time_log2`) by less than $0.00002$ bits.
- **Limitations:** Reduced-width truncation tests low-bit projections of the full-field permutation rather than full 255-bit field collisions (which require $\sim 2^{126.21}$ compressions and are computationally infeasible to execute directly); algebraic degree $5^{62}$ prevents known low-degree invariants, but random-mapping behavior at full width remains a standard cryptographic heuristic rather than an unconditional theorem.

### 5.2 Heuristic `H2` (`supporting`: Concrete Register-Machine Compilation and Accounting)
- **Statement:** The compiled 26,568-instruction, 349-register, 342-constant gap-free register-machine program accurately implements the 807-operation multiplicative-coin step function, online $\rho_0$-constant scaling, 143-bit value-only bit-packing, online left-gap measurement plus shared-counter positioning/lockstep recovery, and fifth-root message reconstruction within $1,048,576$ bytes and $W$ primitive operations.
- **Supporting Evidence (`experiment:r56-listing-w10`):**
  In declared experiment `r56-listing-w10` (`experiments/r56_listing.py`), the exact compiled machine (`K = 31, VB = 143`) is executed instruction-by-instruction on all 256 deterministic organizer trials at $w = 10$ ($\Delta = 64, S = 93, B_{\text{left}} = 96, B_{12} = 96, \text{MCAP} = 32$) and cross-checked against the reference Python implementation and `worst_case_ledger`. Across all 256 trials, `matches_reference` is `True` on **256 / 256 trials** (`151` `success` = `0.5898`, `101` `no-repeat`, `4` `start-on-cycle`), and `within_ledger` is `True` on **256 / 256 trials** ($\min = 23,326$ ops, $\max = 146,795$ ops, $\text{mean} = 85,876.1$ ops $\le \text{ledger} = 264,687$ ops).
- **Limitations:** The interpreter executes the full-width 255-bit arithmetic and bit-packing instructions directly, with a $w = 10$ output projection hook at the end of each step so collisions occur within the 20-second organizer container budget.
