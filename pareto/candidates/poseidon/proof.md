# Orchard Poseidon at $r=56$ partial rounds: a re-tuned one-MiB parameter corner of the 807-operation multiplicative-coin distinguished-point attack

## 1. Target and boundary

`target_profile: poseidon-orchard-r56-prefix-v1`, `attack_class: ordinary-collision`,
`lane: exploratory`. The target is the fixed-length two-input Orchard/Pallas
P128Pow5T3 permutation with eight full rounds at indices $0..3$ and $60..63$, the
first $r=56$ partial rounds at indices $4..59$, deployed constants and MDS from
`orchard-pallas-constants.json` (Pallas)
$$p=\text{0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001},$$
initial state $[nk,\rho,2^{65}]$, no feed-forward, and digest = the first output
field element in canonical 32-byte little-endian encoding. Two distinct canonical
pairs $(nk,\rho)\in[0,p)^2$ forming a full-field-collision are required. Modular
aliases, a chosen capacity, free-start/permutation collisions, and the complete
Orchard nullifier are outside this claim.

The width-3 permutation follows the deployed schedule: for every active round,
add the round constant, raise coordinate $0$ (all three coordinates in full rounds)
to the fifth power, and apply the dense MDS. Because $\gcd(5,p-1)=1$, the
$u\mapsto u^5$ S-box is a bijection on $\mathbb{F}_p$ with inverse
$u^{\text{INV5}}$, $\text{INV5}=5^{-1}\bmod(p-1)$.

We target the **maximum admitted round count** $r=56$. This is not a limitation:
the normalized per-step cost $(135+12r)/C(r)$ with $C(r)=216+21r$ is decreasing in
$r$ (it tends to $12/21$), so higher $r$ both maximizes the round objective and
lowers the cost objective. The $r=56$ point therefore dominates smaller $r$ on
both axes, and we optimize inside it.

## 2. Construction

### 2.1 Two-round BBLP affine input line

This is the Bariant–Bouvier–Leurent–Perrin two-round algebraic bypass
(ToSC 2022), as instantiated in the accepted Orchard entries (`ab786fcb`, and
the $r=56$ line `6de8a0a2`/`3f611f5c`/`43caeb6a`/`874894cf`). Round 0 maps
$(m_0,m_1)$ bijectively to the Round-0 S-box outputs $(U,V)$ because fifth powering
is a permutation; the capacity S-box output $C_0$ is a fixed constant. The Round-1
S-box inputs are affine in $(U,V)$, and choosing the line
$$U(\tau)=U_0+A_{\text{line}}\tau,\qquad V(\tau)=V_0+B_{\text{line}}\tau$$
with $M_{0,0}A_{\text{line}}+M_{0,1}B_{\text{line}}\equiv0$ makes $u_0^{(1)}$
constant, while $(U_0,V_0)$ is chosen to cancel the constant terms of
$u_1^{(1)},u_2^{(1)}$. With $W=\tau^5$, the Round-1 S-box outputs are
$[s_{1,0}^5,\,L_1^5W,\,L_2^5W]$, so the three Round-2 S-box inputs are affine in
$W$: $u_{2,i}(W)=B_i(W+d_i)$.

`line_message(W)` inverts the construction with three fifth roots, so
$W\mapsto(nk(W),\rho(W))$ is injective on $\mathbb{F}_p$; distinct $W$ give distinct
canonical message pairs.

### 2.2 Origin-shifted multiplicative coin and the 807-operation step

Instead of an additive coin $W(x)=x+\rho_0$, we shift the line origin to $-d_0$ and
use a multiplicative coin $\rho_0\in\mathbb{F}_p^\ast$,
$W_{\rho_0}(x)=(\rho_0 x-d_0)\bmod p$. This cancels $d_0$ on lane $0$, so the
normalized Round-2 S-box inputs are $y_0=x$, $y_1=x+e_1(\rho_0)$, $y_2=x+e_2(\rho_0)$
with $e_i(\rho_0)=(d_i-d_0)\rho_0^{-1}$; lane $0$ needs no addition, saving one field
operation and one constant per step. Propagating the diagonal lane scales and the
backward partial-round basis change yields the straight-line step program
`emit_step_807` of exactly
$$135+12r = 135+12\cdot56 = 807$$
field operations (329 FADD + 478 FMUL) with $49+5r=329$ step constants. Each partial
round costs 12 field operations (1 constant add, 3 multiplications for $x^5$, 4
multiplications and 4 additions for the sparse normalized MDS update); the eight
fixed full rounds and the two-round entry account for the remaining $135$. This is
the accepted $r=56$ step cost; we do not change it.

**Theorem 1 (online monomial scaling).** Every step constant at a trial coin
$\rho_0$ is an exact monomial in $\rho_0$ times its $\rho_0=1$ base value
(entry offsets scale by $\rho_0^{-1}$, matrix ratios by invariant degrees, partial
constants by powers of $\rho_0^{\pm5^{k+2}}$, etc.). The machine therefore stores only
the base table and derives the 329 scaled constants online after drawing
$\rho_0$. This theorem is inherited unchanged and is what allows the single
base constant table.

### 2.3 Correctness relation

For every $x$ and $\rho_0$, the construction satisfies
$$\operatorname{digest}\bigl(nk(W_{\rho_0}(x)),\rho(W_{\rho_0}(x))\bigr)
=\bigl(\operatorname{outscale}(\rho_0)\cdot F_{\rho_0}(x)\bigr)\bmod p,$$
with $\operatorname{outscale}(1)=\text{0x8644200abf8cd4035dc449088ab93750ba0d9968f428235fce6f63bb58d8c93}\ne0$
and $\operatorname{outscale}(\rho_0)$ a nonzero monomial in $\rho_0$. Hence
$F_{\rho_0}(x_a)=F_{\rho_0}(x_b)\iff \operatorname{digest}_a=\operatorname{digest}_b$
on canonical messages. We verified this identity independently (Section 7).

## 3. Distinguished-point collision algorithm and Lemma 3

A trial draws $(\rho_0,x_0)$ uniform in $\mathbb{F}_p^\ast\times\mathbb{F}_p$ and
iterates $x_t=F_{\rho_0}(x_{t-1})$ for up to $S=n+d$ steps in unrolled blocks of
$K=24$. A state $x<\Delta$ is a distinguished point (DP); DPs are packed
losslessly (low $\text{VB}=142$ bits plus a $\text{WG}=119$-bit inter-DP gap) into the
table up to capacity $\text{MCAP}$. When a DP repeats a stored value, single-segment
van Oorschot–Wiener recovery returns the two distinct preimages and hence a
canonical Orchard collision. *Distinctness of the returned pair.* The table stores
only pairwise-distinct DP values, and every stored DP except the first is preceded
by at least one non-DP (or a different DP); the left and right segments therefore
begin at different states. Recovery aligns them to equal distance from the common
endpoint by advancing only the longer segment, so the aligned states remain
distinct (they were distinct at the start and a shared state would require two
distinct stored DPs to coincide), and lockstep advances both equally until the
first step where $F_{\rho_0}$ agrees on two distinct states. The reconstructed
messages are $(nk(W_{\rho_0}(x_{\text{left}})),\rho(W_{\rho_0}(x_{\text{left}})))$
and the same for $x_{\text{right}}$; because $W_{\rho_0}$ is a bijection and
$W\mapsto(nk,\rho)$ is injective (Section 2.1), distinct $x$ give distinct message
pairs. Substituting the correctness relation of Section 2.3 makes the equality of
$F$ values an equality of complete digests.

**Lemma 3 (inherited, unchanged).** For a uniform random mapping and a uniform
start, with $\theta_{\text{lo}}=(\Delta-S)/p$, $\theta_{\text{hi}}=\Delta/(p-S)$,
$\mu=S\theta_{\text{hi}}$, $m=\text{MCAP}+1$, if $\mu<m$ then
$$P_{\text{succ}}\ge 1-\sum_{i=1}^{8}e_i,$$
$$e_1=e^{-\frac{n(n+1)}{2p}},\; e_2=\tfrac{n}{p},\; e_3=\tfrac{nd}{p},\;
e_4=e^{-\theta_{\text{lo}}d},\; e_5=e^{-\theta_{\text{lo}}G},\;
e_6=e^{-\theta_{\text{lo}}(G+d-1)},$$
$$e_7=e^{\,m-\mu-m\ln(m/\mu)},\qquad e_8=S\,e^{-\theta_{\text{lo}}2^{\text{WG}}}.$$
The eight events are (1) no repeat within $n$ steps, (2) start on the cycle,
(3) a second repeat within the $d$-window, (4) no post-merge DP within $d$ steps,
(5) lockstep cap $G$, (6) positioning cap $\text{GPOS}=G+d-1$, (7) table overflow,
(8) inter-DP gap $\ge2^{\text{WG}}$. The union bound gives the stated lower bound.

## 4. Parameter re-tuning (this contribution)

The construction depends on $(\Delta,\text{MCAP},K,n,d,G)$ subject to
(i) $\mu<m$, (ii) memory $\le1$ MiB, (iii) $e_8$ small, and
(iv) $P_{\text{succ}}\ge0.39$, i.e. $\sum_i e_i\le0.61$. The accepted $r=56$ rows
(`9fb982e8`, `3a1b25b`) placed $(\text{MCAP},K)=(28880,24)$ and left
$1{,}048{,}160-2^{20}=416$ bytes and about $1.17\times10^{-6}$ of gate budget
unused. Re-solving the coupled minimization over the whole feasible region gives a
strictly better admissible point at the same $r=56$, step program, and recovery
algorithm.

**Why $\Delta$ is interior.** Raising $\Delta$ lowers $e_4,e_5,e_6$ but raises
$\mu$, hence $e_7$; the optimum is interior, and the accepted
$\Delta=4786662258565900106892948537883617543585792$ is already essentially that
interior optimum, so we keep it. The exploitable axes are therefore
$\text{MCAP}$ (memory slack), and the split of $S=n+d$ together with $G$ (which the
accepted rows fixed at one particular representative). We re-optimize those:

- $\text{MCAP}=28893$: the unique largest capacity that keeps the compiled machine
  within $2^{20}$ bytes at $K=24$. This uses the full one-MiB budget (previously
  416 bytes were unused), which marginally lowers $e_7$ and is exactly what allows
  a smaller $n$.
- $d=\lfloor 0.99\cdot d_{\text{base}}\rfloor$, $G=\lfloor 1.01\cdot
  d_{\text{base}}\rfloor$ with $d_{\text{base}}=57452604149476538717129741053198337$
  the accepted value. This trades a marginally smaller $d$ (less trail length) for
  a marginally larger $G$ (recovery is not on the trail path), keeping every
  failure term inside the gate.
- $n$ is set to the smallest integer with $\sum_i e_i\le0.61-10^{-7}$, a deliberate
  $10^{-7}$ safety margin against boundary rounding.

The exact admissible point is

| parameter | value |
| --- | --- |
| $r$ | 56 |
| step field operations | $807$ |
| $K$ | 24 |
| $\text{VB},\text{WG}$ | 142, 119 |
| $\Delta$ | $4786662258565900106892948537883617543585792$ |
| $\text{MCAP}$ | 28893 |
| $n$ | $169303753018948806054888286350548523201$ |
| $d$ | $56878078107981773329958443642666353$ |
| $G$ | $58027130190971304104301038463730320$ |
| $\text{GPOS}=G+d-1$ | $114905208298953077434259482106396672$ |
| $S=n+d$ | $169360631097056787828218244794191189554$ |

with, at 90-digit arithmetic,
$\theta_{\text{lo}}=1.653478378173\ldots\times10^{-34}$,
$\theta_{\text{hi}}=1.653536883251\ldots\times10^{-34}$,
$\mu=28004.40500897\ldots<28894$ and a failure sum

| term | value |
| --- | ---: |
| $e_1$ | $6.095159635711\ldots\times10^{-1}$ |
| $e_2$ | $5.848542992326\ldots\times10^{-39}$ |
| $e_3$ | $3.326538851354\ldots\times10^{-4}$ |
| $e_4$ | $8.233887254780\ldots\times10^{-5}$ |
| $e_5$ | $6.809134047710\ldots\times10^{-5}$ |
| $e_6$ | $5.606564205154\ldots\times10^{-9}$ |
| $e_7$ | $8.464056395467\ldots\times10^{-7}$ |
| $e_8$ | $3.185015311127\ldots\times10^{-10}$ |
| $\sum_i e_i$ | $0.609999900000\ldots$ |
| $P_{\text{succ}}$ | $\ge0.390000100000\ldots\ge0.39$ |

(The filed time bound rounds this point upward; the claim carries the conservative
value.)

## 5. Memory

The compiled register machine uses exactly the accepted layout with the single
change $\text{MCAP}=28893$. The peak allocation is

| item | bytes |
| --- | ---: |
| program instructions, $1456+811\cdot24=20920$ at 4 bytes | 83,680 |
| register file, 351 words at 32 bytes | 11,232 |
| base constant table, 342 words at 32 bytes | 10,944 |
| DP table, 29,459 words ($\lceil28893\cdot142/256\rceil+\lceil28893\cdot119/256\rceil+1$) at 32 bytes | 942,688 |
| start-state word | 32 |
| **total** | **1,048,576** |

The total equals $2^{20}$ exactly, so $M'=\max(1,\text{memory}/2^{20})=1$ and the
memory penalty is zero. The DP value array uses $\lceil28893\cdot142/256\rceil=16027$
words and the gap array $\lceil28893\cdot119/256\rceil=13431$ words; the sentinel
word (index $29458$) preserves the accepted boundary-safety argument, as every DP
value satisfies $x<\Delta<2^{142}$ and the final packed entry reads only masked bits.

## 6. Total computation

The worst-case single-trial operation ledger is inherited verbatim from the
accepted register machine (`worst_case_ledger`), instantiated at the parameters
above. Each unrolled block costs $K\,(807+2)+3=19{,}419$ operations; recovery is
charged at its full cap; all table, constant-load, zeroing, setup, halt, coin-draw
and reconstruction work is included. With
$\text{blocks}=\lceil S/K\rceil=7{,}056{,}692{,}962{,}377{,}366{,}159{,}509{,}093{,}533{,}091{,}299{,}565$
we obtain

| phase | operations |
| --- | ---: |
| setup (coin draw, $\rho_0^{-1}$, scaling, table zeroing) | 152,597 |
| unrolled trail walk | 137,033,920,636,406,073,451,507,087,319,099,946,252,735 |
| non-colliding DP insertions (scan + pack) | 8,349,354,675 |
| colliding scan, single-segment recovery, reconstruction | 188,464,075,495,693,869,015,349,374,766,449,223,132 |
| worst-case single trial | 137,222,384,711,901,767,320,522,436,693,874,744,983,139 |

Adding the same explicit $2^{48}$ margin as the accepted rows gives the filed
bound
$$W=137{,}222{,}384{,}711{,}901{,}767{,}320{,}522{,}436{,}975{,}349{,}721{,}693{,}795
\text{ primitive operations.}$$
Dividing once by $C(56)=216+21\cdot56=1392$,
$$T=W/1392=9.8570694460722\times10^{37},\qquad
\log_2 T=126.21262423813327\ldots\le 126.212625.$$

The preprocessing cost is the offline derivation of the base constants and this
plan. It is the same finite derivation the accepted rows charge (the notation
builders and the parameter search); it is negligible beside $2^{48}$ and is covered
by the $2^{48}$ margin, so `preprocessing_log2 = 0`. There is no separate run-time
preprocessing loop beyond `setup`. Memory operations, randomness, failed trials,
sorting/lookups, recovery and all success amplification are inside the phases above;
the attempt is one processor and one charged trial, with no uncharged restart.

**Frontier position.** The previous best admissible $r=56$ normalized bound was
$126.21263$ (`3a1b25b`, refining `9fb982e8` at $126.21264$). This package's
$126.212624238\ldots$, filed as $126.212625$, is strictly smaller at the same round
and the same construction/algorithm, a $4.31\times10^{-6}$-bit improvement with the
memory penalty unchanged at zero.

## 7. Reproducibility checks performed

All of the following were executed locally by the author without running the
participant experiment programs on the host (they run in the organizer container):

1. Reconstructed the reference permutation and `digest` from
   `orchard-pallas-constants.json`; it matches `verifier.poseidon` at $r=0,3,56$.
2. Verified the correctness relation of Section 2.3 independently on six random
   $(x,\rho_0)$ points: the compiled step output times `outscale` equals the
   reference digest of the reconstructed canonical message, and found
   $\operatorname{outscale}(1)=\text{0x0864}4200abf8cd4035dc449088ab93750ba0d9968f428235fce6f63bb58d8c93$.
3. Ran an independent reduced-width end-to-end search using the reference digest:
   the step-program projection matches the reference low bits and a projected
   collision at $w=18$ yields two distinct canonical messages whose full reference
   digests agree on the low 18 bits.
4. Re-evaluated Lemma 3 in 90-digit `decimal` at the filed parameters; the table in
   Section 4 is that evaluation, with $\sum_i e_i\le0.61-10^{-7}$.
5. Instantiated `worst_case_ledger` and `memory_bytes` at the filed parameters; the
   memory total is $2^{20}$ exactly and the ledger is the table in Section 6.
6. Ran `python3 ../scripts/pareto_candidate.py --family poseidon --rounds 56` for
   credential-free intake, schema and certificate validation.

These are finite consistency checks. The transfer of the random-mapping behaviour
to the real 255-bit permutation is the declared heuristic H1 (below).

## 8. Support, scope, extrapolation, limitations, sensitivity

`H1` (score-critical). *Statement:* For a uniformly chosen $(\rho_0,x_0)$ the trail
of $F_{\rho_0}$ on the origin-shifted BBLP line meets the Lemma-3 random-mapping
lower bound, $P_{\text{succ}}\ge0.39$ at the filed budget. *Evidence:* two
organizer-run reduced-width experiments (Section 9) on the exact $r=56$ step
function; both rates lie at or above an idealised uniform random function at their
width, the conservative direction. *Scope:* single-trial distinguished-point
collision behaviour of the fixed-$r$ step map. *Extrapolation:* reduced widths
$w\in\{10,14\}$ to the full field across degree $5^{62}$. *Limitations:* no
full-width execution is possible ($\sim2^{126.2}$ compressions); random-mapping
behaviour at full width is a standard cryptographic heuristic, not a theorem.
*Sensitivity:* the filed point sits essentially on the gate by design ($\sum_i e_i=0.61-10^{-7}$
exactly), so it is tight one-sidedly: at the **fixed** $n$, a $\Delta$ change of
$\pm0.5\%$ already moves $\sum_i e_i$ past $0.61$. The margin is therefore not
against a fixed-$n$ density error but against the *re-solved* $n$: re-solving the
minimal admissible $n$ for a perturbed density recovers a valid point, and a $1\%$
DP-density deviation changes the required $n$ by only $\sim10^{-4}$ of its value,
i.e. below $0.0002$ bits of $\log_2 S$. We choose the $10^{-7}$ gate margin so the
filed $n$ is exactly the minimal admissible integer for the stated parameters, and
the filed $126.212625$ bound is computed at those exact parameters, not at a
perturbed density.

`H2` (supporting). *Statement:* the compiled register machine implements the
807-operation step, online scaling, bit-packing, single-segment recovery and
fifth-root reconstruction within $2^{20}$ bytes and $W$. *Evidence:* the $w=10$
instruction-level experiment (Section 9). *Limitations:* executed at reduced walk
horizon $S=69$, not full width.

## 9. Experiments

Two organizer-run `python-message-pairs-v1` experiments are declared unchanged from
the accepted $r=56$ package; they test the mechanism, are parameter-independent of
the filed cost, and require no new evidence for the $4.31\times10^{-6}$-bit retune:

- `r56-search-w14`: exact $r=56$ step function at $w=14$, 256 deterministic trials,
  returning canonical message pairs whose verified digest agrees in the low 14 bits.
- `r56-listing-w10`: the compiled register machine executed
  instruction-by-instruction at $w=10$, cross-checked against the reference and the
  ledger.

Neither establishes full-width collisions, the resource bound, or H1; they are
reduced-width witnesses whose regime, extrapolation and limitations are recorded
above.

## 10. Scope of this claim

The claim is an ordinary, canonical two-input full-field Orchard collision at the
maximum admitted round count $r=56$, with a classical probabilistic algorithm and
success probability at least $0.39$, total charged work $W$ over one processor and
one trial, and peak memory $2^{20}$ bytes. AI qualification and human acceptance
are separate from these mechanical and analytic statements.
