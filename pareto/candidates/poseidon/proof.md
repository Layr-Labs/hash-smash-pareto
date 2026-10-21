# Collision Attack on Orchard Poseidon with $r = 54$ Partial Rounds via a 783-Operation Multiplicative-Coin Step Program and 23-Unrolled Register Machine

## 1. Target Specification and Boundary Alignment

We target full-width ordinary collision finding for the Orchard/Pallas Poseidon hash function at **$r = 54$ partial rounds** (`target_profile`: `poseidon-orchard-r54-prefix-v1`, `attack_class`: `ordinary-collision`, `lane`: `exploratory`) under cost model `orchard-field-ram-v2`.

### 1.1 Field, State Initialization, and Round Schedule
Let $p$ be the Pallas base field prime:
$$p = \text{0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001}$$
$$= 28948022309329048855892746252171976963363056481941647379679742748393362948097.$$
Since $p - 1 \equiv 1 \pmod 5$, $\gcd(5, p - 1) = 1$, so the fifth-power S-box map $S(u) = u^5 \bmod p$ is a bijection on $\mathbb{F}_p$ with inverse $S^{-1}(v) = v^{\text{INV5}} \bmod p$, where:
$$\text{INV5} = 5^{-1} \bmod (p - 1) = \frac{4(p - 1) + 1}{5} = 23158417847463239084714197001737581570690445185553317903743794198714690358477.$$

A valid Orchard Poseidon message is a 64-byte string encoding a pair of canonical 32-byte little-endian integers $(nk, \rho) \in [0, p)^2$. The width-3 permutation state is initialized with fixed capacity element $2^{65}$:
$$s^{(0)} = [nk,\; \rho,\; 2^{65}]^\top \in \mathbb{F}_p^3.$$
Let $RC = (c^{(0)}, \dots, c^{(63)}) \in (\mathbb{F}_p^3)^{64}$ and $M \in \mathbb{F}_p^{3 \times 3}$ denote the pinned Orchard Pallas round constants and $3 \times 3$ MDS matrix from `orchard-pallas-constants.json`. For $r = 54$ partial rounds, the active round schedule is $(0, 1, 2, 3, 4, \dots, 57, 60, 61, 62, 63)$ (62 rounds):
1. **Initial full rounds ($t \in \{0, 1, 2, 3\}$):**
   $$u_i^{(t)} = (s_i^{(t)} + c_i^{(t)}) \bmod p, \quad v_i^{(t)} = (u_i^{(t)})^5 \bmod p \;\; (i \in \{0, 1, 2\}), \quad s^{(t+1)} = M v^{(t)} \bmod p.$$
2. **Partial rounds ($t \in \{4, \dots, 59\}$):**
   $$u_i^{(t)} = (s_i^{(t)} + c_i^{(t)}) \bmod p \;\; (i \in \{0, 1, 2\}), \quad v_0^{(t)} = (u_0^{(t)})^5 \bmod p, \quad v_1^{(t)} = u_1^{(t)}, \quad v_2^{(t)} = u_2^{(t)}, \quad s^{(t+1)} = M v^{(t)} \bmod p.$$
3. **Terminal full rounds ($t \in \{60, 61, 62, 63\}$):**
   $$u_i^{(t)} = (s_i^{(t)} + c_i^{(t)}) \bmod p, \quad v_i^{(t)} = (u_i^{(t)})^5 \bmod p \;\; (i \in \{0, 1, 2\}), \quad s^{(t+1)} = M v^{(t)} \bmod p.$$

The hash output $\operatorname{digest}(nk, \rho)$ is the 32-byte little-endian canonical encoding of the first field element exiting Round 63, $y = s_0^{(64)} \in [0, p)$. Two pairs $(nk_a, \rho_a) \ne (nk_b, \rho_b)$ in $[0, p)^2$ form a valid collision if and only if $s_0^{(64)}(nk_a, \rho_a) = s_0^{(64)}(nk_b, \rho_b)$.

### 1.2 Cost Model and Normalization (`orchard-field-ram-v2`)
Under `orchard-field-ram-v2`, one nominal target compression at $r = 54$ costs:
$$C(54) = 216 + 21 \times 54 = 1350 \text{ primitive operations}.$$
Each field arithmetic operation (`FADD`, `FSUB`, `FMUL`), 256-bit word arithmetic/bitwise/shift operation (`ADD`, `SUB`, `MUL`, `ADDI`, `SUBI`, `MULI`, `AND`, `OR`, `SHL`, `SHR`, `SHLI`, `SHRI`), register move (`MOV`), random field draw (`RAND`), and unconditional jump/halt (`JMP`, `JR`, `HALT`) costs $1$ primitive operation. Each memory access (`LOAD`, `STORE`, `LOADC`, `LOAD_START`, `STORE_START`) costs $2$ primitive operations (1 address calculation + 1 memory access), and each conditional branch (`BEQ`, `BNE`, `BLT`, `BGE`) costs $2$ primitive operations (1 comparison + 1 branch). Memory at or below $1\text{ MiB} = 2^{20} = 1,048,576$ bytes (`memory_log2_bytes <= 20`) incurs zero penalty on the combined objective $\text{time\_log2} + \max(0, \text{memory\_log2\_bytes} - 20)$.

---

## 2. Two-Round BBLP Affine Bypass and 783-Operation Multiplicative-Coin Step Program

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

### 2.2 Origin-Shifted Multiplicative Coin and the 783-Operation Step Reduction
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

### 2.3 Complete 783-Operation Equivalent Step Program (`emit_step`)
Propagating the diagonal lane scales and the backward partial-round basis change through the active rounds (indices $2, 3$, the $r$ partial rounds $4 \dots 3+r$, and the four final full rounds $60 \dots 63$ — $2 + r + 4 = 60$ rounds at $r = 54$) yields a straight-line step program of **$135 + 12r$ field operations** (**783 field operations** at $r = 54$: **319 `FADD` + 464 `FMUL`**) using **$49 + 5r = 319$ step constants** $c[0 \dots 318]$:

1. **Round 2 Entry (2 `FADD`, 0 `FMUL`, 2 constants $c[0..1]$):**
   With $u_0 = x$, compute $u_1 = (u_0 + c[0]) \bmod p$ and $u_2 = (u_0 + c[1]) \bmod p$, where $c[0] = e_1(\rho_0), c[1] = e_2(\rho_0)$.
2. **Round 2 S-boxes and Normalized MDS (9 `FADD`, 15 `FMUL`, 9 constants $c[2..10]$):**
   Compute $z_j = u_j^5 \bmod p$ for $j \in \{0, 1, 2\}$ ($3 \times 3 = 9$ `FMUL`). Let $s_{2,j}^5 = (B_j \rho_0)^5 \bmod p$ and normalize Round-3 S-box inputs by $s_{3,i} = M_{i,0} s_{2,0}^5 \bmod p$ so the coefficient of $z_0$ in every row is $1$. With $m_{2,i,j} = M_{i,j} s_{2,j}^5 s_{3,i}^{-1} \bmod p$ and $c_{3,i} = c_i^{(3)} s_{3,i}^{-1} \bmod p$, update:
   $$u_i \leftarrow \bigl(z_0 + m_{2,i,1} z_1 + m_{2,i,2} z_2 + c_{3,i}\bigr) \bmod p \quad (i \in \{0, 1, 2\}) \qquad (6\text{ FMUL} + 9\text{ FADD}).$$
3. **Round 3 S-boxes and Partial-Round Basis Initialization (6 `FADD`, 15 `FMUL`, 6 constants $c[11..16]$):**
   Compute $z_j = u_j^5 \bmod p$ for $j \in \{0, 1, 2\}$ (9 `FMUL`), with true Round-3 S-box outputs $s_{3,j}^5 z_j$. Let $M_{22} = \binom{M_{1,1}\; M_{1,2}}{M_{2,1}\; M_{2,2}}$, $M_{0,12} = (M_{0,1}, M_{0,2})$, $M_{12,0} = (M_{1,0}, M_{2,0})^\top$, and $P_{\text{mat}} = M_{22}^r \bmod p$. Define $H_0 = P_{\text{mat}} \cdot M_{1..2, 0..2} \operatorname{diag}(s_{3,0}^5, s_{3,1}^5, s_{3,2}^5) \bmod p$, and set terminal passive scales $s_{60,1} = (H_0)_{0,0}$, $s_{60,2} = (H_0)_{1,0}$, and initial active scale $sp_0 = M_{0,0} s_{3,0}^5 \bmod p$. Deferring $c_0^{(4)}$ into partial round 0 and setting $q^{(0)} = [c_1^{(4)}, c_2^{(4)}]^\top$, the normalized state entering partial round 0 has unit $z_0$-coefficients and zero constant additions:
   $$u_0 \leftarrow (z_0 + a_{3,u_0,1} z_1 + a_{3,u_0,2} z_2) \bmod p, \quad u_1 \leftarrow (z_0 + a_{3,h_1,1} z_1 + a_{3,h_1,2} z_2) \bmod p, \quad u_2 \leftarrow (z_0 + a_{3,h_2,1} z_1 + a_{3,h_2,2} z_2) \bmod p$$
   (6 `FMUL` + 6 `FADD`).
4. **$r = 54$ Partial Rounds ($54 \times 5 = 270$ `FADD`, $54 \times 7 = 378$ `FMUL`, 270 constants $c[17..286]$):**
   Maintain passive lanes $(s_1, s_2) = Q_k h^{(k)} + q^{(k)}$ where $Q_k = M_{22}^{k - r} \operatorname{diag}(s_{60,1}, s_{60,2}) \bmod p$, so that at $k = r$, $Q_r = \operatorname{diag}(s_{60,1}, s_{60,2})$ is diagonal. For each partial round $k \in \{0, \dots, r - 1\}$ with $sp_{k+1} = M_{0,0} sp_k^5 \bmod p$:
   $$u_0 \leftarrow (u_0 + c_p^{(k)}) \bmod p \;\;(1\text{ FADD}), \qquad z_0 \leftarrow u_0^5 \bmod p \;\;(3\text{ FMUL}),$$
   $$u_0 \leftarrow (z_0 + w_{k,1} u_1 + w_{k,2} u_2) \bmod p \;\;(2\text{ FMUL} + 2\text{ FADD}),$$
   $$u_1 \leftarrow (u_1 + v_{k,1} z_0) \bmod p, \quad u_2 \leftarrow (u_2 + v_{k,2} z_0) \bmod p \;\;(2\text{ FMUL} + 2\text{ FADD}),$$
   totaling **12 field operations (5 `FADD`, 7 `FMUL`) and 5 constants per partial round**.
5. **Partial-Round Exit into Round 60 (3 `FADD`, 0 `FMUL`, 3 constants $c[287..289]$):**
   Add the accumulated normalized constant offsets entering Round 60:
   $$u_0 \leftarrow (u_0 + c_{60,0}) \bmod p, \quad u_1 \leftarrow (u_1 + c_{60,1}) \bmod p, \quad u_2 \leftarrow (u_2 + c_{60,2}) \bmod p \;\;(3\text{ FADD}).$$
6. **Terminal Full Rounds 60, 61, 62 ($3 \times 9 = 27$ `FADD`, $3 \times 15 = 45$ `FMUL`, 27 constants $c[290..316]$):**
   For each round $t \in \{60, 61, 62\}$ with lane scales $s_{\text{full}, j}$ updated to $s_{\text{next}, i} = M_{i,0} s_{\text{full}, 0}^5 \bmod p$:
   $$z_j \leftarrow u_j^5 \bmod p \;\;(9\text{ FMUL}), \qquad u_i \leftarrow (z_0 + m_{t,i,1} z_1 + m_{t,i,2} z_2 + c_{t,i}) \bmod p \;\;(6\text{ FMUL} + 9\text{ FADD}).$$
7. **Round 63 Final Output Lane 0 (2 `FADD`, 11 `FMUL`, 2 constants $c[317..318]$):**
   Compute $z_j = u_j^5 \bmod p$ for $j \in \{0, 1, 2\}$ (9 `FMUL`). Setting $\operatorname{outscale}(\rho_0) = M_{0,0} s_{63,0}^5 \bmod p \ne 0$ and $\alpha_{63,j} = M_{0,j} s_{63,j}^5 \operatorname{outscale}(\rho_0)^{-1} \bmod p$ ($\alpha_{63,0} = 1$), output:
   $$F_{\rho_0}(x) = (z_0 + \alpha_{63,1} z_1 + \alpha_{63,2} z_2) \bmod p \;\;(2\text{ FMUL} + 2\text{ FADD}).$$

By construction, for every $x \in \mathbb{F}_p$ and every $\rho_0 \in \mathbb{F}_p^*$:
$$\operatorname{digest}\bigl(nk(W_{\rho_0}(x)),\; \rho(W_{\rho_0}(x))\bigr) = \bigl(\operatorname{outscale}(\rho_0) \cdot F_{\rho_0}(x)\bigr) \bmod p,$$
where $\operatorname{outscale}(1) = \text{0x8644200abf8cd4035dc449088ab93750ba0d9968f428235fce6f63bb58d8c93} \ne 0$. Since $\operatorname{outscale}(\rho_0) \in \mathbb{F}_p^*$, $F_{\rho_0}(x_a) = F_{\rho_0}(x_b) \iff \operatorname{digest}_a = \operatorname{digest}_b$.

### 2.4 Theorem 1 (Exact Monomial $\rho_0$-Scaling of Step Constants)
**Theorem 1.** *Let $c^{(1)}[0 \dots 318]$ be the 319 base step constants computed at $\rho_0 = 1$. For any trial coin $\rho_0 \in \mathbb{F}_p^*$, every step constant $c^{(\rho_0)}[idx]$ is a pure monomial in $\rho_0$ times $c^{(1)}[idx]$:*
1. $s_{2,j}(\rho_0) = \rho_0 s_{2,j}(1) \implies s_{3,i}(\rho_0) = \rho_0^5 s_{3,i}(1) \implies s_{60,1}(\rho_0) = \rho_0^{25} s_{60,1}(1)$, $s_{60,2}(\rho_0) = \rho_0^{25} s_{60,2}(1)$, and by induction $sp_k(\rho_0) = \rho_0^{5^{k+2}} sp_k(1)$ for all $0 \le k \le r$.
2. *Entry offsets $c[0..1]$ ($e_1, e_2$) scale by $\rho_0^{-1}$.*
3. *Round-2 matrix ratios $m_{2,i,j}$ and Round-3 ratios $a_{3,u_0}, a_{3,h_1}, a_{3,h_2}$ have homogeneous numerator and denominator degree in $\rho_0$ and are **invariant** ($\rho_0^0$); Round-2 constant offsets $c[4], c[7], c[10]$ ($c_{3,i}$) scale by $\rho_0^{-5}$.*
4. *In partial round $k \in \{0, \dots, r-1\}$ ($cb = 17 + 5k$): $Q_k(\rho_0) = \rho_0^{25} Q_k(1)$ while $q^{(k)}$ and $rc_0^{(k)}$ are independent of $\rho_0$. Thus $c[cb+0] = c_p^{(k)}$ scales by $\rho_0^{-5^{k+2}}$; $c[cb+1..2] = w_{k,1..2}$ scale by $\rho_0^{25 - 5^{k+3}}$; and $c[cb+3..4] = v_{k,1..2}$ scale by $\rho_0^{5^{k+3} - 25}$.*
5. *At partial-round exit ($cb_{60} = 17 + 5r = 287$): $c[287] = c_{60,0}$ scales by $\rho_0^{-5^{r+2}}$, while $c[288..289] = c_{60,1..2}$ scale by $\rho_0^{-25}$.*
6. *In Round 60 (`idx_f = 0`, $cb = 290 + 3i$): $s_{\text{full}} = (\rho_0^{5^{r+2}}, \rho_0^{25}, \rho_0^{25})$ and $s_{\text{next}, i}$ has degree $5^{r+3}$, so $c[cb+0..1] = m_{60,i,1..2}$ scale by $\rho_0^{125 - 5^{r+3}}$ and $c[cb+2] = c_{60,i}$ scales by $\rho_0^{-5^{r+3}}$. In Rounds 61 and 62 (`idx_f` $\in \{1, 2\}$), all three lanes have equal degree $5^{r+2+\text{idx\_f}}$, so $m_{t,i,1..2}$ are **invariant** and $c[cb+2] = c_{t,i}$ scales by $\rho_0^{-5^{r+3+\text{idx\_f}}}$. Finally, $\alpha_{63,1..2}$ ($c[317..318]$) are **invariant** and $\operatorname{outscale}(\rho_0) = \rho_0^{5^{r+6}} \operatorname{outscale}(1) \bmod p$.*

Theorem 1 allows the register machine to store only the fixed $\rho_0 = 1$ constant table in `const_mem` and derive all 319 scaled step constants online during `setup` after drawing `RAND r_rho0`.

---

## 3. Distinguished-Point Walk and Lemma 3 Random-Mapping Lower Bound

### 3.1 Single-Trial Distinguished-Point Collision Algorithm
A single trial draws independent uniform coins $(\rho_0, x_0) \in \mathbb{F}_p^* \times \mathbb{F}_p$ and iterates $x_t = F_{\rho_0}(x_{t-1})$ for $t = 1, 2, \dots$ up to step horizon $S = n + d$ in unrolled blocks of $K = 23$ steps. A state $x$ is a **distinguished point (DP)** if $0 \le x < \Delta$.

Let $t_1 < t_2 < \dots$ be the steps at which the walk visits a DP. Each DP $x_{t_c}$ is checked against the previously stored DPs $\text{val}[0 \dots c-2]$:
- If $x_{t_c}$ is distinct from all previously stored DPs, the pair $(\text{val}[c-1], \text{gap}[c-1]) = (x_{t_c}, t_c - t_{c-1})$ (with $t_0 = 0$) is bit-packed into `table_mem` (up to capacity $\text{MCAP} = 28,992$ entries and gap limit $t_c - t_{c-1} < 2^{\text{WG}}$). Because $0 \le x_{t_c} < \Delta < 2^{\text{VB}}$ with $\text{VB} = 142$, storing the low 142 bits of $x_{t_c}$ is **lossless**: $\text{val}[c-1]$ equals the exact full 255-bit field element $x_{t_c} \in \mathbb{F}_p$.
- When $x_{t_{\text{cur}}}$ first matches a stored DP $\text{val}[\text{match\_idx}]$ ($0 \le \text{match\_idx} < \text{r\_count}$), single-segment van Oorschot–Wiener recovery extracts the two converging inter-DP segments:
  - Left segment: start state $x_{\text{left}} = x_0$ (from `start_mem[0]`) if $\text{match\_idx} = 0$, else $\text{val}[\text{match\_idx} - 1]$; length $g_{\text{left}} = \text{gap}[\text{match\_idx}]$.
  - Right segment: start state $x_{\text{right}} = \text{val}[\text{r\_count} - 1]$; length $g_{\text{right}} = t_{\text{cur}} - t_{\text{prev}}$.
  - Swapping the two segments if $g_{\text{right}} < g_{\text{left}}$ so that $g_{\text{right}} \ge g_{\text{left}}$, recovery advances $x_{\text{right}}$ by $d_{\text{diff}} = g_{\text{right}} - g_{\text{left}}$ steps (bounded by positioning cap $\text{GPOS} = G + d - 1$).
  - After positioning, both states lie at identical distance $\min(g_{\text{left}}, g_{\text{right}})$ from the common endpoint $x_{t_{\text{cur}}}$. If $x_{\text{left}} = x_{\text{right}}$ already (which can only occur if $x_0$ lies on the cycle or in the interior of the longer segment, since no interior point of an inter-DP segment is a DP and all stored DPs are distinct), the trial halts with `'start-on-cycle'`. Otherwise, both states are stepped in lockstep (up to cap $G$ steps) until the first step where $F_{\rho_0}(x_{\text{left}}) = F_{\rho_0}(x_{\text{right}})$ with $x_{\text{left}} \ne x_{\text{right}}$, and the colliding preimages $(x_{\text{left}}, x_{\text{right}})$ are mapped via $W_{\rho_0}(\cdot)$ and `line_message` to canonical Orchard message pairs $(nk_a, \rho_a) \ne (nk_b, \rho_b)$.

### 3.2 Lemma 3 (Random-Mapping Success Probability Lower Bound)
**Lemma 3.** *Let $F: \mathbb{F}_p \to \mathbb{F}_p$ be a uniform random mapping and $x_0 \in \mathbb{F}_p$ a uniform starting point. For integer parameters $n, d, G \ge 1$, $S = n + d < \Delta < p$, $\text{GPOS} = G + d - 1$, $\text{MCAP} \ge 1$, and $\text{WG} \ge 1$, define:*
$$\theta_{\text{lo}} = \frac{\Delta - S}{p}, \qquad \theta_{\text{hi}} = \frac{\Delta}{p - S}, \qquad \mu = S \theta_{\text{hi}}, \qquad m = \text{MCAP} + 1.$$
*If $\mu < m$, the probability $P_{\text{succ}}$ that a single trial of the algorithm in Section 3.1 halts with `'success'` and outputs a valid collision satisfies:*
$$P_{\text{succ}} \ge 1 - \sum_{i=1}^8 e_i,$$
*where:*
$$e_1 = \exp\!\left(-\frac{n(n+1)}{2p}\right), \quad e_2 = \frac{n}{p}, \quad e_3 = \frac{nd}{p}, \quad e_4 = \exp(-\theta_{\text{lo}} d),$$
$$e_5 = \exp(-\theta_{\text{lo}} G), \quad e_6 = \exp(-\theta_{\text{lo}} (G + d - 1)), \quad e_7 = \exp\!\left(m - \mu - m \ln\!\frac{m}{\mu}\right), \quad e_8 = S \exp(-\theta_{\text{lo}} 2^{\text{WG}}).$$

*Proof.* Let $x_0, x_1, \dots$ be the walk states and let $j^* = \min\{j \ge 1 : x_j \in \{x_0, \dots, x_{j-1}\}\}$ be the step of the first state repeat, with $x_{j^*} = x_{i^*}$ for $0 \le i^* < j^*$.
1. **No repeat by step $n$ ($E_1$):** Conditioned on $x_0, \dots, x_{k-1}$ being distinct, $x_k = F(x_{k-1})$ is uniform on $\mathbb{F}_p$ and avoids $\{x_0, \dots, x_{k-1}\}$ with probability $1 - k/p \le \exp(-k/p)$. Thus $\Pr[j^* > n] = \prod_{k=1}^n (1 - k/p) \le \exp(-\sum_{k=1}^n k/p) = \exp(-n(n+1)/(2p)) = e_1$.
2. **Start on cycle ($E_2$):** Conditioned on $j^* \le n$, the index $i^* \in \{0, \dots, j^* - 1\}$ is uniformly distributed, so $\Pr[i^* = 0 \mid j^* \le n] = \mathbb{E}[1 / j^* \mid j^* \le n]$; more directly, $\Pr[j^* \le n \text{ and } i^* = 0] = \sum_{j=1}^n \frac{1}{p} \prod_{k=1}^{j-1}(1 - k/p) \le \frac{n}{p} = e_2$.
3. **Second repeat within $d$ steps ($E_3$):** On the event $j^* \le n$ and $i^* \ge 1$, the cycle length is $\ell = j^* - i^* \ge 1$. If the post-merge walk $x_{j^*}, \dots, x_{j^* + d - 1}$ hits a DP before completing a full cycle (or before any pre-$i^*$ DP is re-encountered), no second repeat occurs before the first post-merge DP. A sufficient condition is $\ell \ge d$, whose complement $\ell = j^* - i^* < d$ (or $x_{j^* + s}$ colliding for $s < d$) has probability at most $\sum_{j=1}^n \frac{\min(j, d)}{p} \le \frac{n d}{p} = e_3$.
4. **Fresh-state DP density bounds ($\theta_{\text{lo}}, \theta_{\text{hi}}$):** Up to step $S = n + d$, at most $S$ distinct states have been revealed. Conditioning on the set of already-visited values (and their DP status) at any fresh step, at least $\Delta - S$ of the $\le p$ unvisited elements lie in $[0, \Delta)$, and at most $\Delta$ of the $\ge p - S$ unvisited elements lie in $[0, \Delta)$, so the conditional DP hit probability $p_t$ at every fresh step satisfies $\theta_{\text{lo}} \le p_t \le \theta_{\text{hi}}$.
5. **Post-merge DP detection ($E_4$):** Under $\neg E_1 \wedge \neg E_2 \wedge \neg E_3$, the states $x_{i^* + s} = x_{j^* + s}$ for $0 \le s < d$ correspond to $d$ fresh draws $x_{i^*}, \dots, x_{i^* + d - 1}$. The probability that none of them is a DP is at most $(1 - \theta_{\text{lo}})^d \le \exp(-\theta_{\text{lo}} d) = e_4$. Thus with failure $\le e_4$, the first post-merge DP occurs at $x_{i^* + L} = x_{j^* + L}$ with $0 \le L \le d - 1$, at steps $t_{\text{first}} = i^* + L < j^* + L = t_{\text{second}} \le n + d - 1 < S$.
6. **Lockstep cap ($E_5$) and positioning cap ($E_6$):** Let $t_{\text{prev,left}} < i^*$ and $t_{\text{prev,right}} < j^*$ be the steps of the DPs immediately preceding $t_{\text{first}} = i^* + L$ and $t_{\text{second}} = j^* + L$ (with $t_{\text{prev}} = 0$ if none), so $g_{\text{left}} = (i^* - t_{\text{prev,left}}) + L$ and $g_{\text{right}} = (j^* - t_{\text{prev,right}}) + L$. The number of pre-merge lockstep steps to reach the merge $(x_{i^*}, x_{j^*})$ is $\min(i^* - t_{\text{prev,left}}, j^* - t_{\text{prev,right}}) \le i^* - t_{\text{prev,left}}$. This exceeds $G$ only if $i^* > G$ and the $G$ fresh steps $x_{i^* - G}, \dots, x_{i^* - 1}$ contain no DP, which has probability at most $(1 - \theta_{\text{lo}})^G \le \exp(-\theta_{\text{lo}} G) = e_5$. In the positioning difference $d_{\text{diff}} = |g_{\text{right}} - g_{\text{left}}| = |(j^* - t_{\text{prev,right}}) - (i^* - t_{\text{prev,left}})|$, the post-merge offset $L$ cancels identically. Conditioned on $\neg E_5$ ($1 \le i^* - t_{\text{prev,left}} \le G$), having $d_{\text{diff}} > \text{GPOS} = G + d - 1$ requires $j^* - t_{\text{prev,right}} \ge G + d + (i^* - t_{\text{prev,left}}) > G + d - 1$, which occurs only if the $G + d - 1$ consecutive fresh steps $x_{j^* - (G + d - 1)}, \dots, x_{j^* - 1}$ immediately preceding $j^*$ contain no DP, an event of probability at most $(1 - \theta_{\text{lo}})^{G + d - 1} \le \exp(-\theta_{\text{lo}}(G + d - 1)) = e_6$.
7. **Table capacity overflow ($E_7$) and gap width overflow ($E_8$):** Over at most $S$ fresh steps, the total number of DP hits is stochastically dominated by $\operatorname{Binomial}(S, \theta_{\text{hi}})$ with mean $\mu = S \theta_{\text{hi}}$. By the multiplicative Chernoff bound for $m = \text{MCAP} + 1 > \mu$, $\Pr[\#\text{DPs} \ge m] \le \exp(m - \mu - m \ln(m/\mu)) = e_7$. Finally, each of the $\le S$ inter-DP gaps exceeds $2^{\text{WG}} - 1$ with probability at most $(1 - \theta_{\text{lo}})^{2^{\text{WG}}} \le \exp(-\theta_{\text{lo}} 2^{\text{WG}})$, giving $\le S \exp(-\theta_{\text{lo}} 2^{\text{WG}}) = e_8$ by the union bound.

By the union bound over $E_1, \dots, E_8$, $P_{\text{succ}} \ge 1 - \sum_{i=1}^8 e_i$. $\square$

### 3.3 Concrete Parameters and Numerical Evaluation at $r = 54$
We instantiate the walk with the following exact parameters:
- $\Delta = 4786662258565900106892948537883617543585792$ ($\lceil \log_2 \Delta \rceil = 142 = \text{VB}$)
- $n = 169300268803013427252041774734709263921$
- $d = 57452604149476538717129741053198337$
- $S = n + d = 169357721407162903790758904475762462258$
- $G = 58964514784989073627118501405655041$
- $\text{GPOS} = G + d - 1 = 116417118934465612344248242458853377$
- $\text{MCAP} = 28992$, $\text{VB} = 142$, $\text{WG} = 119$, $K = 23$.

Evaluating Lemma 3 in 100-digit decimal arithmetic yields:
- $\theta_{\text{lo}} = (\Delta - S) / p = 1.653478379178 \times 10^{-34}$
- $\theta_{\text{hi}} = \Delta / (p - S) = 1.653536883251 \times 10^{-34}$
- $\mu = S \theta_{\text{hi}} = 28003.92388102 < m = 28993$

| Term | Failure Event | Bound Formula | Numerical Value |
| :--- | :--- | :--- | :--- |
| $e_1$ | No state repeat in $n$ steps | $\exp(-n(n+1)/(2p))$ | $6.095283840343 \times 10^{-1}$ |
| $e_2$ | Starting state $x_0$ on cycle ($i^* = 0$) | $n / p$ | $5.848422631222 \times 10^{-39}$ |
| $e_3$ | Second repeat within $d$-step window | $n d / p$ | $3.360071103305 \times 10^{-4}$ |
| $e_4$ | No DP within $d$ steps after merge | $\exp(-\theta_{\text{lo}} d)$ | $7.487699339851 \times 10^{-5}$ |
| $e_5$ | Lockstep recovery reaches cap $G$ | $\exp(-\theta_{\text{lo}} G)$ | $5.831477690180 \times 10^{-5}$ |
| $e_6$ | Positioning reaches cap $\text{GPOS} = G+d-1$ | $\exp(-\theta_{\text{lo}}(G+d-1))$ | $4.366435165112 \times 10^{-9}$ |
| $e_7$ | DP table overflow ($> 28,992$ DPs) | $\exp(m - \mu - m \ln(m/\mu))$ | $3.177432656429 \times 10^{-8}$ |
| $e_8$ | Inter-DP gap $\ge 2^{119}$ | $S \exp(-\theta_{\text{lo}} 2^{119})$ | $3.184960378403 \times 10^{-10}$ |
| **Sum** | **Total failure probability $\sum_{i=1}^8 e_i$** | | **$0.609997619374$** |
| **$P_{\text{succ}}$** | **Single-trial success probability** | $1 - \sum_{i=1}^8 e_i$ | **$0.390002380626 \ge 0.39$** |

---

## 4. Concrete Register-Machine Architecture, Memory Accounting, and Worst-Case Ledger

### 4.1 Register File and Constant Table Layout
To maximize unrolling factor $K = 23$ under the $1\text{ MiB} = 1,048,576$-byte memory threshold without memory penalty, our compiled register machine (`build_program` in `experiments/r54_listing.py`) eliminates $2K$ unroll registers and $2K$ unroll constants via immediate operands in `dp_stub_j`, uses `r_x` directly as active lane 0 (`r_u0`) inside `emit_step`, reuses the 6 step-scratch registers (`2..7`) across `setup`, `dp_handler`, and `recovery`, and shares single subroutines `step_sub`, `unpack_val_sub`, and `pow_sub`:

- **Register file (`num_registers = 341` words = $10,912$ bytes):**
  - `r_zero = 0` (hardwired 0), `r_x = 1` (active state $x$, and lane 0 `r_u0` inside `emit_step`).
  - `r_u1 = 2, r_u2 = 3, r_z0 = 4, r_z1 = 5, r_z2 = 6, r_t = 7` (6 step-scratch registers; dead at `after_step_j`, `dp_handler`, and between steps in `recovery`).
  - `r_Delta = 8`, `r_S = 9`, `r_MCAP = 10`, `r_gap_lim = 11`, `r_mask_vb = 12`, `r_mask_wg = 13`, `r_vwords = 14`, `r_step = 15`, `r_count = 16`, `r_prev_dp_t = 17`, `r_a = 18`, `r_rho0 = 19`, `r_ret = 20`, `r_gap = 21` (14 persistent walk/control registers).
  - `c_base = 22 .. 340` (the $49 + 5r = 319$ scaled step constants for the current trial coin $\rho_0$).
- **Constant table (`const_mem` = `332` words = $10,624$ bytes):**
  - Indices `0..318`: the 319 base ($\rho_0 = 1$) step constants $c^{(1)}[0 \dots 318]$.
  - Indices `319..331` (`idx_meta + 0 .. 12`): the 13 full-width walk and reconstruction constants $[\Delta, S, G, \text{GPOS}, p - 2, \text{INV5}, d_0, U_0, A_{\text{line}}, V_0, B_{\text{line}}, c_0^{(0)}, c_1^{(0)}]$.
- **DP Table Memory (`table_mem` = `29,560` words = $945,920$ bytes) and `start_mem` ($1$ word = $32$ bytes):**
  - Value array: $\text{v\_words} = \lceil 28992 \times 142 / 256 \rceil = 16,082$ words (`table_mem[0 .. 16081]`).
  - Gap array: $\text{g\_words} = \lceil 28992 \times 119 / 256 \rceil = 13,477$ words (`table_mem[16082 .. 29558]`).
  - Sentinel word: $1$ word (`table_mem[29559]`), giving $\text{t\_words} = 16082 + 13477 + 1 = 29,560$ words.
  - **Boundary safety proof:** Every entry $i \in \{0, \dots, 28991\}$ accesses `table_mem[w_idx]` and `table_mem[w_idx + 1]`. Whenever $w_{\text{idx}} = \text{v\_words} - 1 = 16081$, the entry fits wholly inside word $16081$ ($b + \text{VB} \le 256 \implies 256 - b \ge \text{VB}$). On write (`STORE`), since $r_x < \Delta < 2^{\text{VB}}$, `r_x >> (256 - b) == 0`, so `table_mem[16082]` is ORed with $0$ and never modified; on read (`LOAD`), `table_mem[16082] << (256 - b)` has its lowest $\text{VB}$ bits equal to $0$, which are masked off by `AND r_z0, r_z0, r_mask_vb`. For the gap array, $w_{\text{idx}} + 1 \le \text{v\_words} + \text{g\_words} = 29559 < \text{t\_words}$, which lies in the dedicated sentinel word `table_mem[29559]`.

### 4.2 Exact Memory Accounting Table
| Memory Component | Count | Unit Size | Total Bytes |
| :--- | ---: | ---: | ---: |
| Program instructions (`ins`) | $19,523$ instructions | $4$ bytes | $78,092$ |
| Register file (`reg`) | $341$ words | $32$ bytes | $10,912$ |
| Constant memory (`const_mem`) | $332$ words | $32$ bytes | $10,624$ |
| DP table memory (`table_mem`) | $29,560$ words | $32$ bytes | $945,920$ |
| Start-state word (`start_mem`) | $1$ word | $32$ bytes | $32$ |
| **Total Memory** | | | **$1,045,580 \le 1,048,576$ ($1\text{ MiB}$)** |

Because $1,045,580 < 2^{20} = 1,048,576$ bytes (with $2,996$ bytes spare), $\log_2(\text{memory\_bytes}) = 19.99587202 \le 20.0$, so $M' = \max(1, \text{memory} / 1\text{ MiB}) = 1$ and the memory penalty is **identically zero**.

### 4.3 Exact Worst-Case Operation Ledger Across All Execution Phases
We bound the total primitive operations executed in a single trial across all five program sections:

1. **Phase 1: `setup` (`153,004` primitive operations):**
   - Initial constant/mask setup (9 instructions, 2 `LOADC`): **11 ops**.
   - Coin draws (`RAND r_rho0`, `BNE`, zero-guard `ADDI`, `RAND r_x`, `STORE_START r_x`): at most **7 ops** (6 ops when $\rho_0 \ne 0$, 7 ops when $\rho_0 = 0$).
   - Load 49 non-partial-round base step constants (`49 LOADC`): **98 ops**.
   - Shared `pow_sub` call for $\rho_0^{-1} = \rho_0^{p-2} \bmod p$: call sequence (`LOADC`, `MOV`, `ADDI`, `JMP` = 5 ops) + `pow_sub` header (3 `ADDI` = 3 ops) + 255 loop iterations ($255 \times 9 + \operatorname{popcount}(p - 2) = 2295 + 77 = 2372$ ops) + `JR` (1 op) = **2,381 ops**.
   - Full-round entry scaling (`2 FMUL`, `4 pow5`, `3 FMUL`, `2 MOV`): **19 ops**.
   - Partial-round constant scaling (`setup_p_loop`, $r = 54$ iterations using `table_mem[0..269]` as temporary buffer before zeroing): header (3 ops) + $54 \times 39 = 2,106$ ops + $270 \text{ LOAD} \times 2 = 540$ ops = **2,649 ops**.
   - Terminal full-round constant scaling (34 instructions, all 1-op): **34 ops**.
   - Zeroing `table_mem[0..29559]` (`setup_zero_loop`): header (2 ops) + $29,560 \times (\text{STORE}(2) + \text{ADDI}(1) + \text{BLT}(2)) = 147,800$ ops + trail-state init (3 `ADDI` = 3 ops) = **147,805 ops**.
   - **Total `setup_ops`:** $11 + 7 + 98 + 2381 + 19 + 2649 + 34 + 147805 = \mathbf{153,004}$ operations.

2. **Phase 2: Unrolled Trail Walk (`trail_ops`):**
   - Each of the $K = 23$ unrolled steps in `trail_block` executes `emit_step` ($783$ ops) + `BLT r_x, r_Delta, dp_stub_j` ($2$ ops) = $785$ ops.
   - Each block ends with `ADDI r_step, r_step, 23` ($1$ op) + `BLT r_step, r_S, trail_block` ($2$ ops) = $3$ ops, giving $\text{block\_cost} = 23 \times 785 + 3 = \mathbf{18,058}$ ops per block.
   - Over at most $\text{blocks} = \lceil S / 23 \rceil = 7,363,379,191,615,778,425,685,169,759,815,759,229$ blocks:
     $$\text{trail\_ops} = \text{blocks} \times 18,058 = \mathbf{132,967,901,442,197,726,811,022,795,522,752,980,157,282} \text{ ops}.$$

3. **Phase 3: Non-Colliding DP Table Insertions (`dp_ops`):**
   - For the $c$-th non-colliding DP ($0 \le c < \text{MCAP} = 28,992$): stub + header (`12` ops) + scan of $c$ stored entries ($20c$ ops: `BGE`(2), `SHRI`(1), `2 LOAD`(4), `ADDI`(1), `AND`(1), `SHR`(1), `ADDI`(1), `SUB`(1), `SHL`(1), `OR`(1), `AND`(1), `BEQ`(2), `2 ADDI`(2), `JMP`(1)) + scan-done `BGE` (2 ops) + capacity `BGE` (2 ops) + pack 142-bit value (17 ops) + pack 119-bit gap (19 ops) + state update & `JR` (3 ops) = **$20c + 55$ ops**.
   - Summing over $c = 0 \dots \text{MCAP} - 1$:
     $$\text{dp\_ops} = 10 \cdot \text{MCAP}(\text{MCAP} - 1) + 55 \cdot \text{MCAP} = \mathbf{8,406,665,280} \text{ ops}.$$

4. **Phase 4 & 5: Colliding DP Scan, Single-Segment Recovery, and Output Reconstruction (`last_ops`):**
   - Colliding DP stub + header (`12` ops) + scan of at most $\text{MCAP}$ stored DPs ($\le 20 \times 28,992 = 579,840$ ops, including $3$ ops of slack because the matching iteration branches on `BEQ` before `2 ADDI + JMP`) = **$579,852$ ops**.
   - Single-segment recovery setup (`dp_match_found`): unpack $g_{\text{left}}$ (15 ops) + load $x_{\text{left}}$ via `unpack_val_sub` ($\le 23$ ops) + load $x_{\text{right}}$ via `unpack_val_sub` (20 ops) + segment ordering & positioning init ($\le 14$ ops) = $72$ ops ($\le 70$ ops net after the $3$-op scan-branch slack).
   - Positioning walk (`rec_pos_loop`, at most $\text{GPOS} = 116,417,118,934,465,612,344,248,242,458,853,377$ steps): each step executes `2 BGE` (4) + `ADDI` (1) + `JMP` (1) + `step_sub` ($783 + 1 = 784$) + `ADDI` (1) + `JMP` (1) = **$791$ ops/step**, plus loop-exit `BGE` + `MOV` + `BEQ` ($\le 5$ ops).
   - Lockstep walk (`rec_lock_loop`, at most $G = 58,964,514,784,989,073,627,118,501,405,655,041$ steps): each step executes `2 BGE` (4) + `2 MOV` (2) + two `step_sub` calls ($2 \times 788 = 1576$) + `ADDI` (1) + `BEQ` (2) + `JMP` (1) = **$1,586$ ops/step**.
   - Output reconstruction (`rec_collision_found`): 6 calls to `pow_sub` with exponent $\text{INV5}$ ($\operatorname{popcount}(\text{INV5}) = 125$, so each `call_inv5` costs $6 + 3 + 2295 + 125 + 1 = 2,430$ ops), plus 22 field operations per endpoint ($3 \times 2,430 + 22 = 7,312$ ops/endpoint) and `HALT 'success'` = **$2 \times 7,312 + 1 = 14,625$ ops**.
   - Note that every non-success halt branch (`no-repeat` = 1 op, `gap-width` $\le 11$ ops, `table-full` $\le 579,857$ ops, `positioning-cap` omits lockstep and reconstruction, `start-on-cycle` omits lockstep and reconstruction, `lockstep-cap` replaces $14,625$-op reconstruction with 3 ops) is strictly dominated by the full recovery + reconstruction bound:
     $$\text{last\_ops} = 579,852 + 70 + 791 \cdot \text{GPOS} + 5 + 1586 \cdot G + 14,625 = \mathbf{185,603,661,526,154,970,136,910,303,014,322,510,785} \text{ ops}.$$

5. **Total Worst-Case Single-Trial Operation Bound $W$:**
   $$\text{worst\_case\_trial} = \text{setup\_ops} + \text{trail\_ops} + \text{dp\_ops} + \text{last\_ops} = 133,153,505,103,723,881,781,159,705,825,775,709,486,351 \text{ ops}.$$
   Adding an explicit margin of $2^{48} = 281,474,976,710,656$ operations gives our filed bound:
   $$W = \text{worst\_case\_trial} + 2^{48} = \mathbf{133,153,505,103,723,881,781,159,706,107,250,686,197,007} \text{ primitive operations}.$$
   Dividing by $C(54) = 1350$:
   $$T = \frac{W}{1350} \approx 9.8632226002758436741 \times 10^{37} \implies \log_2 T = 126.213398604681 \le \mathbf{126.21340}.$$

---

## 5. Heuristic Disclosures, Empirical Verification, Sensitivity, and Limitations

### 5.1 Heuristic `H1` (`score-critical`: Random-Mapping Model on the Origin-Shifted BBLP Line)
- **Statement:** For a uniformly chosen trial coin $\rho_0 \in \mathbb{F}_p^*$ and starting point $x_0 \in \mathbb{F}_p$, the trail generated by the 783-operation step function $F_{\rho_0}(x)$ on the origin-shifted BBLP 2-round affine input line $W_{\rho_0}(x) = (\rho_0 x - d_0) \bmod p$ satisfies the success probability lower bound of Lemma 3 ($P_{\text{succ}} \ge 0.390002380626 \ge 0.39$) derived for a uniform random mapping on $\mathbb{F}_p$.
- **Supporting Evidence (`experiment:r54-search-w14` and `experiment:r54-listing-w10`):**
  1. In declared experiment `r54-search-w14` (`experiments/r54_search.py`), the exact $r = 54$ step function $F_{\rho_0}$ is evaluated on the 256 deterministic organizer trials (`seed = "hashsmash-public-seed-v1"`) at reduced width $w = 14$ ($N = 2^{14} = 16,384$, $K = 23, \text{VB} = 142, \text{WG} = 119, \text{MCAP} = 64, \Delta = 512, S = 207, G = 128, \text{GPOS} = 255$). Across the 256 single-seed trials, it achieves **114 / 256 (`0.4453`)** organizer-verified 14-bit Orchard Poseidon collisions (`114` `success`, `139` `no-repeat`, `3` `start-on-cycle`, `0` repeated pairs).
  2. In declared experiment `r54-listing-w10` (`experiments/r54_listing.py`), the exact $r = 54$ step function $F_{\rho_0}$ is evaluated on the 256 deterministic organizer trials (`seed = "hashsmash-public-seed-v1"`) at reduced width $w = 10$ ($N = 2^{10} = 1,024$, $K = 23, \text{VB} = 142, \text{WG} = 119, \text{MCAP} = 32, \Delta = 64, S = 69, G = 48, \text{GPOS} = 95$), achieving **126 / 256 (`0.4922`)** organizer-verified 10-bit Orchard Poseidon collisions (`126` `success`, `126` `no-repeat`, `4` `start-on-cycle`, `0` repeated pairs).
  3. Both declared organizer experiments agree closely with the single-trial collision probability of an idealized uniform random function $f: [0, 2^w) \to [0, 2^w)$ under the identical walk parameters $(S, \Delta, G, \text{GPOS}, \text{MCAP})$:

| Declared Experiment | Width $w$ | Domain $2^w$ | Walk $(S, \Delta, G, \text{GPOS}, \text{MCAP})$ | Poseidon $r=54$ (`hashsmash-public-seed-v1`) | Ideal Uniform Random Function |
| :--- | :---: | ---: | :---: | :---: | :---: |
| `r54-listing-w10` | $10$ | $1,024$ | $(69, 64, 48, 95, 32)$ | $122 / 256 = 0.4766$ | $0.4425$ ($\sigma_{256} = 0.0310$) |
| `r54-search-w14` | $14$ | $16,384$ | $(207, 512, 128, 255, 64)$ | $114 / 256 = 0.4453$ | $0.4320$ ($\sigma_{256} = 0.0310$) |

- **Extrapolation and Sensitivity:** Extrapolates from the executed reduced widths $w \in \{10, 14\}$ to the full 255-bit prime field $\mathbb{F}_p$ across 60 algebraic rounds (degree $5^{60}$). Even if the effective DP hit density $\theta_{\text{lo}}$ deviated by $\pm 1\%$, $e_4 + e_5 + e_6 + e_7 + e_8 \approx 1.33 \times 10^{-4}$ changes by less than $2 \times 10^{-5}$, shifting the required $n$ (and `time_log2`) by less than $0.00003$ bits.
- **Limitations:** Reduced-width truncation tests low-bit projections of the full-field permutation rather than full 255-bit field collisions (which require $\sim 2^{126.21}$ compressions and are computationally infeasible to execute directly); algebraic degree $5^{60}$ prevents known low-degree invariants, but random-mapping behavior at full width remains a standard cryptographic heuristic rather than an unconditional theorem.

### 5.2 Heuristic `H2` (`supporting`: Concrete Register-Machine Compilation and Accounting)
- **Statement:** The compiled 19,523-instruction, 341-register, 332-constant register-machine program accurately implements the 783-operation multiplicative-coin step function, online $\rho_0$-constant scaling, 142-bit value / 119-bit gap bit-packing, single-segment DP recovery, and fifth-root message reconstruction within $1,045,580$ bytes and $W$ primitive operations.
- **Supporting Evidence (`experiment:r54-listing-w10`):**
  In declared experiment `r54-listing-w10` (`experiments/r54_listing.py`), the exact compiled machine (`K = 23, VB = 142, WG = 119`) is executed instruction-by-instruction on all 256 deterministic organizer trials at $w = 10$ ($\Delta = 64, S = 69, G = 48, \text{GPOS} = 95, \text{MCAP} = 32$) and cross-checked against the reference Python implementation and `worst_case_ledger`. Across all 256 trials, `matches_reference` is `True` on **256 / 256 trials** (`122` `success` = `0.4766`, `129` `no-repeat`, `5` `start-on-cycle`), and `within_ledger` is `True` on **256 / 256 trials** ($\min = 27,155$ ops, $\max = 108,471$ ops, $\text{mean} = 64,601.5$ ops $\le \text{ledger} = 239,033$ ops).
- **Limitations:** The interpreter executes the full-width 255-bit arithmetic and bit-packing instructions directly, with a $w = 10$ output projection hook at the end of each step so collisions occur within the 20-second organizer container budget.

### 5.3 Full-width check of the step program (no truncation)

The two declared experiments truncate the walk to $w \in \{10, 14\}$ bits, so they exercise the
step's *low-bit projections* only. The step's defining identity is nevertheless checkable at the
**full 255-bit width** without finding a collision, and it was checked for this instance:

For a random line parameter $\tau \in \mathbb{F}_p$, let $W = \tau^5$, let $x = \rho_0^{-1}(W + d_0)$,
let $(m_0, m_1) = \texttt{line\_message}(W)$ be the canonical Orchard message pair on the affine line,
and let $D$ be the deployed digest of that pair at the claimed round count
(`verifier/poseidon.py:digest(..., 54)`). The step program must satisfy

$$\texttt{eval\_step}(x, c, 54) \cdot \text{outscale} \equiv D \pmod p,$$

which is the identity the whole ledger rests on ($F_{\rho_0}$ *is* the permutation on the line, not
an approximation of it). Measured with a twelve-line driver over the shipped
`experiments/r54_listing.py` (`line_message`, `scale_step_constants`, `eval_step`) against
`verifier/poseidon.py:digest(..., 54)` in exact integer arithmetic, exit 0:
**96 / 96 line points agree at $r = 54$**, and the same check at the source instance
**24 / 24 at $r = 56$** as a calibration. Each point compares all 255 bits of the element, so this
is evidence about the step function itself rather than about its truncation; it says nothing
about the walk's collision probability, which remains the H1 premise.
