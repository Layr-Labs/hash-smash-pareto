# Orchard Poseidon, 56 partial rounds: birthday search on an equivalent-form permutation, one trail with distinguished points

Target `poseidon-orchard-r56-prefix-v1`. Claim: `time_log2 = 126.21753` target-compressions, memory
`1,048,552` bytes (`memory_log2_bytes = 19.99997`, at or below 2^20, so the normalized cost equals the time
bound), success probability 0.39, preprocessing bounded inside the time (Section 8), no nonuniform advice.
Cost model `orchard-field-ram-v2`, `C(56) = 216 + 21 * 56 = 1392`; every field and word operation is charged
`1/C` and no permutation call is charged as a unit.

## 0. What this is, and what it is not

This is the textbook collision search of van Oorschot and Wiener (Pollard rho with distinguished points) applied
to the complete deployed Orchard Poseidon schedule, with every evaluation of the hash priced as an equivalent straight-line program whose field operations are
each charged by the cost model. Its success probability uses no
weakness of the permutation: the argument is the generic birthday bound for a uniformly random function, plus one
declared premise (H1) that the fixed map behaves like a random function for this search.

This is not a break of Orchard Poseidon, not a practical collision, and not a statement that the primitive is
weaker than its design target. The filed budget is about 2^127 evaluations of the permutation; nothing of that
size was executed, and no collision of the full target is exhibited. The nominal reference
`poseidon-orchard-r56-nominal-v2` is an organizer metadata identifier, not an established attack or baseline, and
the claim here is close to, not below, the generic birthday cost of a 254-bit field.

## 1. Credit, and what is ours

The construction is a replication of published work, with two small additions of our own. We separate them
explicitly.

Borrowed, with credit:

* **Two free rounds on a line.** Bariant, Bouvier, Leurent and Perrin, "Algebraic Attacks against Some
  Arithmetization-Oriented Primitives", IACR Transactions on Symmetric Cryptology 2022(3): on a suitable affine
  line in the two message coordinates the first two full rounds become affine in one parameter. Section 2.
* **Sparse partial rounds.** Grassi, Khovratovich, Rechberger, Roy and Schofnegger, "Poseidon: A New Hash
  Function for Zero-Knowledge Proof Systems", USENIX Security 2021: the equivalent form in which a partial round
  touches only the active lane and two accumulated lanes. Section 3.
* **The assembled attack: line, equivalent step program with lane scaling and a hidden-lane basis, one-trail
  distinguished-point search with an index-packed table, deterministic recovery, and the single-trail success
  lemma.** Public submission `7f88498e-210e-4e2d-a75f-323ed65133ec` (Jbenisek, `poseidon-orchard-r48`,
  normalized cost 126.22283) and its predecessors in the same lineage, and public submission
  `6de8a0a2-c1af-4234-9874-4d0022aa55a3` (tanctl, `poseidon-orchard-r56`, normalized cost 126.363427), whose
  notes describe the same method at 56 partial rounds. We read those public notes and the r48 proof. Every
  component listed here comes from them; our programs are written from those descriptions, and no participant's
  file was copied or executed.

Also credited, and declared in the submission's dependency list: public submission
`56fb07fc-e6b7-4bc3-83e6-929b4e4f0018` (Jbenisek, `poseidon-orchard-r56`, 126.711170), the earlier 56-round
entry; and the r23 entry of the same lineage, whose success-lemma structure the certification program follows.

Ours in this entry:

1. **Accounting parameters re-tuned at this round count.** The step program is rebuilt at `r = 56`
   (808 field operations, Section 3) following the published construction, and the unrolling `U`, the
   distinguished-point density `T` and the table capacity `MCAP` are re-derived against the one-mebibyte memory
   budget at that larger code size (Section 7). The rebuild itself is the published method applied at a round
   count that entry `6de8a0a2` already covers; what is ours is the parameter choice and the ledger below.
2. **One tightening of the ledger.** The table scan of the `c`-th insertion is charged for `c` examined entries
   rather than for a full table.

The parameters were chosen by a grid over the accounting constants `(U, TAB, KD, H)`, with `T` maximised by
bisection and the budget minimised by bisection inside each cell. 72 cells admitted a certified
parameter tuple and were scored; cells in which the gating conditions of Lemma 2 fail (for example a table mean
at or above `MCAP + 1`) admit no tuple and were discarded, not scored. The choice among the admitted cells
changes the ledger and not the validity of Lemma 2, which is certified for the submitted tuple by the declared
experiment of Section 10; the grid itself is not part of the filed package, and its only role is to select the
tuple that is certified there. The selection does, however, drive the budget to the least value reaching 0.39,
which is what leaves this entry without a probability margin (Section 9).

### 1.1 How much of the difference against the comparators is ours

Two 56-round entries by the same author bracket this one (Section 11): `b810ea13` at 126.226166, filed
at the contract-minimum success probability 0.39 and the current best, and its predecessor `6de8a0a2` at
126.363427, filed at a 0.45 random-function bound. Against the current best the difference is
**0.00864 bits, and all of it is this entry's parameters and ledger**: the same method, the same success
bound, a 808-operation step against 812, 16-step unrolling against 4, a larger table (27,997 entries against
24,832) and so denser distinguished points and a smaller recovery cap, and the scan charge of Section 1 item 2.
Against the predecessor the difference decomposes as follows, and the newer entry confirms the decomposition
almost exactly, since re-filing at 0.39 moved it by 0.137261 bits:

| component | bits | what it is |
| --- | ---: | --- |
| filing at success probability 0.39 rather than 0.45 | 0.13725 | a filing choice open to any entry, which `6de8a0a2` declined and `b810ea13` then took |
| our parameters and ledger at an equal success bound | 0.00865 | the part that is ours |
| total difference against `6de8a0a2` | 0.14590 | |

Re-tuned at a 0.45 bound, this construction gives 126.354773 against 126.363427. A further reference point,
the 48-round entry's accounting parameters applied at this round count under our own ledger, is 126.21894,
which is 0.0014 bits above this entry. The gain that is ours is therefore of the order of a hundredth of a
bit, and we claim no more than that.

## 2. Target, the line, and the walk

The target is the Orchard P128Pow5T3 hash over the Pallas base field
`p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001` (`N = p`, about 2^254), with the
deployed `halo2_poseidon-0.2.0` round constants and MDS matrix `M`, in the schedule: original full rounds 0-3,
all 56 original partial rounds 4-59, original full rounds 60-63. The input is exactly two canonical field
elements `(m0, m1)`, each a 32-byte little-endian encoding below `p`; the state is initialized `[m0, m1, 2^65]`;
the digest is the complete first coordinate of the final state in its canonical encoding. Modular aliases, a
chosen capacity, free-start permutation collisions and the complete Orchard nullifier construction are out of
scope, as the profile states.

**The line.** Round 0 maps `(m0, m1)` to `U = (m0 + c_{0,0})^5` and `V = (m1 + c_{0,1})^5`, a bijection in each
coordinate because `gcd(5, p - 1) = 1`, and its third lane is the constant `K = (2^65 + c_{0,2})^5`. The S-box
input of round 1 is therefore affine in `(U, V)`. Take `a = M[0][1]`, `b = -M[0][0]`, so that lane 0 of that
input is constant along `(U, V) = (U0 + a tau, V0 + b tau)`, and solve the 2 x 2 system (its determinant
`M[1][0] M[2][1] - M[2][0] M[1][1]` is nonzero for the deployed matrix, asserted by the program) for `U0, V0`
making lanes 1 and 2 equal `d_1 tau` and `d_2 tau`. The round-1 S-boxes then output a constant and
`d_i^5 tau^5`, so with `W = tau^5` the state after round 1 is `A + W B` for two constant vectors `A, B`. The
program computes `A` and `B` by running the reference rounds at `W = 0` and `W = 1`, and asserts
`A + W B` against the reference rounds at random `W`.

`message(W) = (U^{1/5} - c_{0,0}, V^{1/5} - c_{0,1})` with `tau = W^{1/5}` is injective in `W`, because
`W -> tau`, `tau -> (U, V)` (as `a != 0`) and `(U, V) -> (m0, m1)` are each injective. Both outputs are canonical
field elements, so every `W` gives a legal message.

**The walk.** An attempt draws two coins `rho0` and `x_0`, each the low 254 bits of a uniform 256-bit word, and
iterates

```
F(x) = digest(message(x + rho0)) / OUTSCALE,
```

where `OUTSCALE` is a fixed nonzero field constant of the step program (Section 3). `F` maps the field to the
field, so its output feeds straight back in. Two values `x != y` with `F(x) = F(y)` give `W = x + rho0 !=
W' = y + rho0`, hence two distinct 64-byte messages with equal digests: a collision of the target. Division by a
fixed nonzero constant preserves equality, so the equality the program establishes is `F(A) = F(B)` in its
lockstep (Section 5); it does not recompute the two digests and the ledger funds no such recomputation. The
organizer recomputes the digests of any pair that is returned.

## 3. The step program: the hash in an equivalent form (808 field operations)

One evaluation of `F` is the straight-line program `STEP` built by `build_step` in
`experiments/trail_machine.py`: **808 operations, 330 ADD and 478 MUL**, all canonical
Pallas field operations on named 256-bit registers, with 327 step constants.

* **Lane scaling.** A lane may be held as its true value divided by a known nonzero constant `lambda`. An S-box
  then gives `(true)^5 = lambda^5 (held)^5`, and `lambda^5` is folded into the constants of the next linear
  layer. A linear combination `sum_j g_j z_j + c` is held divided by `g_0`, which makes one coefficient 1 and
  costs 2 MUL + 2 ADD, plus 1 ADD when a round constant enters.
* **Partial rounds.** Lane 0 is held as `lambda h0 + gamma`, and lanes 1 and 2 as `Q (h1, h2) + q`, with
  `lambda, gamma, Q, q` constants of the program. The basis of the hidden pair is a free choice: taking
  `h = diag(nu) M22^56 s` for the true lanes `s`, where `M22` is the lower 2 x 2 block of `M` and `nu_a`
  normalizes a coefficient, the matrix `Q` returns to `diag(nu)^{-1}` after the 56 partial rounds, so leaving the
  partial-round form costs one ADD per lane. Each partial round is
  `x5 = (h0 + kappa)^5; h0 := x5 + n1 h1 + n2 h2; h1 := h1 + w1 x5; h2 := h2 + w2 x5`, which is **12
  operations** (1 ADD, 3 MUL for `x^5`, then 4 MUL and 4 ADD), with the round's five constants; the linear layer
  of the round is absorbed into the next constant matrix.
* **Counts.** Entry `x + e_i` (3 ADD, with `e_i = E0_i + rho0` set once per attempt); round 2 S-boxes 9 MUL and
  its linear layer with the round-3 constants 6 MUL + 9 ADD; round 3 S-boxes 9 MUL and the linear layer into the
  partial-round form 6 MUL + 6 ADD; 56 partial rounds at 12; leaving the partial-round form 3 ADD; rounds 60, 61
  and 62 at 9 MUL + 6 MUL + 9 ADD each; round 63 S-boxes 9 MUL and the output lane only, 2 MUL + 2 ADD. The sum
  is `3 + 24 + 21 + 12 * 56 + 3 + 72 + 13 = 808 = 136 + 12 * 56`. An `x^5` is 3 MUL (square, square, multiply).
* **Checks.** `build_step` asserts that every scale, pivot and matrix it forms is nonzero or invertible, and that
  `Q` is diagonal on leaving the partial rounds. The declared experiment (Section 10) recomputes, in the
  organizer's executor, that `F(x) * OUTSCALE` equals the digest of `message(x + rho0)` at `r = 56` on a
  seed-derived point in every trial. That comparison is against the reference implementation embedded in the
  submitted program, not the organizer's own function, which the container does not hold; the embedded
  implementation is pinned to the organizer's semantics by three digest vectors checked at import time, and the
  only organizer-side check of the target's digest is its recomputation of any returned pair.

## 4. The frozen algorithm

### 4.1 Parameters

| parameter | value |
| --- | --- |
| unrolled steps per block `U` | 16 |
| distinguished-point threshold `T` | 54,556 |
| table capacity `MCAP` | 27,997 |
| detection-delay constant `KD` | 10 |
| gap constant `H` | 20 |
| table constant `TAB` | 13 |
| trail budget `n = k * 2^100`, `k` | 133,553,654 |
| `n` | 2^126.99284 |
| detection delay `d` | 2^115.587 |
| step budget `S = n + d` | 2^126.99338 |
| gap cap `gmax` | 2^116.587 |
| distinguished density `theta` | 2^-112.26455 |



`D = (2^126 + 1) T` is the exact number of distinguished field elements, because `p = 2^254 + c` with
`T <= c < 2^128`; the distinguished predicate is `x mod 2^128 < T`, and `theta = D / N = 2^-112.26455`.

### 4.2 Control flow

1. **Setup.** Load the 327 step constants and the 26 control constants into their registers;
   draw `rho0` and `x_0` (two random words, two masks); store `x_0` in the start word; form `e_i = E0_i + rho0`;
   zero the side array.
2. **Trail**, in blocks of `U = 16 `unrolled steps (counter `I` = steps done before the block): in each slot,
   `x := F(x)` by the step program; then `u = x AND (2^128 - 1)`, `u < T`, branch. A distinguished value with
   index `I + k + 1` enters the handler: the table is scanned; if the value is already stored, the trail has
   closed on its cycle and the attempt goes to recovery; if the table already holds `MCAP` entries, the attempt
   halts (code 2); otherwise the value and index are inserted. After `S` steps the attempt halts (code 1).
3. **Recovery** (Section 5): at most `gmax` evaluations to reach the target index and at most `gmax` lockstep
   rounds of two evaluations each; the halts are codes 3, 4 and 5.
4. **Output.** The two colliding `x` values are mapped back through `message` (three fifth-root exponentiations
   each) and the four field elements are stored in the output area; halt code 0.

### 4.3 Termination codes

`0` a collision (the only success); `1` the step budget `S` is exhausted; `2` the table is full; `3` the start
lies on the cycle; `4` the walk to the target index exceeded `gmax`; `5` the lockstep exceeded `gmax` rounds.
Every code is charged at its limit in the ledger, so the time bound covers all of them.

## 5. The recovery is deterministic

Let `t` be the least index with `x_t = x_j` for some `j < t`, write `mu = j` and `lambda = t - mu`; for
`i >= mu`, `x_i = x_{i + lambda}`.

The first repeated distinguished value found is at index `b = a + lambda`, where `a` is the index of the first
distinguished point at or after `mu`: distinguished points with index in `[t, a + lambda)` repeat values
`x_mu .. x_{a - 1}`, none of which is distinguished and stored, so the first stored value seen twice is the one
at `a`. Hence `L = b - a = lambda` exactly.

Let `(s, x_s)` be the stored entry immediately before `a`, or the start `(0, x_0)` if none. Then `s < mu <= a`,
or `s = 0 = mu`, in which case the start lies on the cycle and the attempt halts (code 3). With `s < mu`, we have
`x_s != x_{s + L}`, and the least `m >= 1` with `x_{s + m} = x_{s + m + L}` is `m = mu - s <= a - s`. So the
lockstep from `(x_s, x_{s + L})` stops within `a - s` rounds and returns `(x_{mu - 1}, x_{mu - 1 + L})`: two
distinct values with equal image under `F`. The program reaches `x_{s + L}` from the stored entry with the
largest index at most `s + L`, found by bisection on the table (whose indices increase with address), and all of
`s`, `a` and `s + L` are below `t`.

When every gap between consecutive stored points below `t` is at most `gmax`, the recovery uses at most `gmax`
evaluations for the walk and at most `gmax` lockstep rounds. The table comparison is exact: an entry holds the value's bits 128 and above (127 bits, as `p < 2^255`) with its index in the low 128
bits, and the value's low part, which is below
`T < 2^16`, is kept in a packed side array, so a lookup compares the whole field element.

## 6. Success probability for a uniformly random function

In this section `F` is a uniformly random function on the `N` field elements (lazy sampling) and `x_0` is any
fixed element; every statement is conditional on the start. Write `theta_lo = (D - 2^128) / N` and
`theta_hi = D / (N - 2^128)`. Every index used is below `2^128`.

**Lemma 1.** (i) Given `x_0 .. x_i` with no repeat, `x_{i + 1}` is uniform on the field, so it repeats one of the
`i + 1` earlier values with probability `(i + 1) / N`. (ii) Given `x_0`, `t` and `mu`, the sequence
`x_1 .. x_{t - 1}` is uniform over all sequences of `t - 1` distinct elements different from `x_0`, because every
such sequence together with the event `x_t = x_mu` has probability `N^{-t}`. (iii) Hence for `1 <= j < t`, given
`x_0, t, mu` and `x_1 .. x_{j - 1}`, the value `x_j` is uniform over the `N - j` unused elements, of which
`D - k` are distinguished with `k <= j`; therefore

```
theta_lo <= P(x_j distinguished | x_0, t, mu, x_1 .. x_{j-1}) <= theta_hi.
```

*Proof of (iii).* `(D - k) / (N - j) >= (D - j) / N >= theta_lo` and `(D - k) / (N - j) <= D / (N - j) <=
theta_hi`, using `j < 2^128`. The bound conditions on every earlier value, including the distinguished status of
earlier points, so it still applies immediately after a stored point.

**Lemma 2.** With `d >= KD / theta_lo` (rounded up to a multiple of `U`), `gmax >= H / theta_lo`, `S = n + d`,
and the table capacity `MCAP`, an attempt on a uniformly random function succeeds with probability at least

```
1 - exp(-n (n + 1) / 2N) - n / N - [ e^{-KD} + n d / N + (S theta_hi + 1) e^{-H} + P_table ].
```

*Proof.* The attempt fails only in these ways.

(a) *No repeat within `n` steps.* By Lemma 1(i), `P(t > n) = prod_{i < n} (1 - (i + 1) / N) <=
exp(-n (n + 1) / 2N)`.

(b) *The start lies on the cycle.* `mu = 0` has probability at most `1 / N` at each step, so at most `n / N` in
all.

(c) *The repeat is not detected.* Given `x_0`, `t <= n`, `mu` and `lambda >= d`, the `d` values
`x_mu .. x_{mu + d - 1}` are all below `t`, and by Lemma 1(iii), applied in increasing order, none of them is
distinguished with probability at most `(1 - theta_lo)^d <= e^{-theta_lo d} <= e^{-KD}`. A distinguished point at
`a` among them gives `b = a + lambda <= t + d - 1 < S`, so the repeat is seen inside the budget. The remaining
case `lambda < d` has probability at most `n d / N`, because for each `t <= n` and each `lambda < d` the event
`x_t = x_{t - lambda}` has probability at most `1 / N`.

(d) *A gap above `gmax`.* For a stored point at position `i < t`, the probability that the next `gmax` positions
below `t` hold no distinguished point is at most `exp(-theta_lo gmax) <= e^{-H}`, again by Lemma 1(iii) applied
after conditioning on `x_i` being distinguished; each later `x_j` fails to be distinguished with conditional
probability `1 - (D - k) / (N - j) <= 1 - theta_lo`, and the chain rule over `gmax` positions gives
`(1 - theta_lo)^{gmax}`. Union-bounding over positions: for each of the at most `S` positions `i`, the event
"`x_i` is distinguished and the next `gmax` positions below `t` are not" has probability at most
`theta_hi e^{-H}` by Lemma 1(iii), and the start contributes its own gap at `e^{-H}`, so the total is at most
`(S theta_hi + 1) e^{-H}`. The sum is over positions, not over an expected number of stored points.

(e) *The table overflows.* The stored points lie below `t`, and by Lemma 1(iii) their number is dominated by
`Binomial(S, theta_hi)`, whose mean `mu_S = S theta_hi` is below `a = MCAP + 1`. The Chernoff bound gives
`P(> MCAP) <= exp(-mu_S) (e mu_S / a)^a = P_table <= e^{-TAB}`.

Adding the failure probabilities proves the lemma. `qed`

**The certified value.** At the parameters of Section 4.1 the bound is

| failure | term | value |
| --- | --- | ---: |
| no repeat in `n` steps | `exp(-n (n + 1) / 2N)` | 0.609531589296 |
| start on the cycle | `n / N` | 5.84839157047e-39 |
| repeat not detected | `e^{-KD}` | 4.53999297625e-05 |
| cycle shorter than `d` | `n d / N` | 0.000364808719439 |
| a gap above `gmax` | `(S theta_hi + 1) e^{-H}` | 5.59686404221e-05 |
| table overflow | `Chernoff` | 2.23171479325e-06 |
| **success** | `1 - sum` | **0.390000001700** |



so the attempt succeeds with probability at least **0.390000001700** for a uniformly random function. `n` is the least
multiple of `2^100` in the searched range at which the bound reaches 0.39. The arithmetic is evaluated in
60-digit decimals with every exponential, quotient and product rounded in the direction that weakens the bound,
by the declared experiment `poseidon-orchard-r56-success-bound-v1`, whose source is
`experiments/success_bound.py`. One attempt: no restart, no amplification, no advice.

## 7. The machine, and the resource ledger

### 7.1 Machine model and charging (declared convention H-MACHINE)

The Pallas field RAM of `orchard-cost-v2.json` with 256-bit words, realized as a load/store machine with a
**declared file of 414 registers** of 256 bits: 345 named by the step program and 69 for
the search control and the constants. Registers are named statically by instruction fields and are never reached
by a computed address; the file's 13,248 bytes are counted in memory. Everything else (the start word, the
table, the side array, the output area and the constant area) is memory, reached only by charged loads and
stores. Prices: a canonical field addition or multiplication, and every other primitive word operation (AND, OR,
shift, comparison, conditional branch, register move, aligned 256-bit load or store, random word), cost `1/C`
each. Instruction fetch is not a primitive operation and is not charged; the program image is counted in memory.
The step words carry three register fields of 9 bits and one opcode bit, so a step word is 4 bytes; control
instructions are 8 bytes. No field constant is an immediate operand: the 327 step constants are loaded
once per attempt into their registers, and that is charged.

This register-file declaration is an accounting convention, disclosed as a score-critical heuristic in
`claim.json`. The benchmark contract neither fixes nor bounds a register count. We are aware of 56-round
entries that declare files of comparable size, but that is an observation about another participant's package
which a judge cannot check from inside this one, so it is context and not support. The deterministic event
counts and the success argument do not depend on this convention; the main-loop operation count does. The
declared experiment reports the listing's structural counts, which the protocol labels participant observations
and does not credit as resource costs; the memory figure of Section 7.3 is derived in this proof from the
layout, and the reported counts only let a reader check that derivation against the executed listing.

### 7.2 Worst-case operation count

Every row is an upper bound met or exceeded by the listing for every coin sequence, with each halt charged at its
limit. `tools/ledger_p56.py` recomputes the rows from the submitted experiment source.

| row | what is charged | operations | log2 |
| --- | --- | ---: | ---: |
| `setup` | setup: constant loads, coins, side-array zeroing | 7,366 | 12.847 |
| `trail` | trail: `S` steps at `808 + 3`, plus 3 per block of `U`, plus the budget halt | 137,384,132,364,444,288,116,185,333,303,143,903,734,670 | 136.657 |
| `dp_events` | distinguished-point events: handlers, scans, insertions (the `c`-th insertion scans `c` entries) | 7,839,216,002 | 32.868 |
| `recovery_fixed` | recovery: fixed work and the bisection | 235 | 7.877 |
| `recovery_walk` | recovery: walk to the target index, at its cap `gmax` | 101,675,512,919,990,045,359,528,698,507,410,201,585 | 126.257 |
| `recovery_lockstep` | recovery: lockstep, at its cap `gmax` rounds of two evaluations | 203,101,515,378,826,740,914,494,136,404,986,267,699 | 127.255 |
| `messages` | output: two messages, three fifth-root exponentiations each | 12,250 | 13.580 |
| `prep` | preprocessing (Section 8), charged flat | 68,719,476,736 | 36.000 |
| **total** | every halt at its limit | **137,688,909,392,743,104,902,459,356,138,132,858,916,543** | **136.66046** |

`total / C = 9.891445e+37`, so `log2 = 126.217521`, claimed as **126.21753** (rounded up at five decimals).


Per trail step the charge is `808 + 3 + 3 / 16` operations against `C = 1392`.

### 7.3 Memory

| item | bytes |
| --- | ---: |
| start word | 32 |
| table, `MCAP` entries of 32 bytes | 895,904 |
| side array, 1750 words | 56,000 |
| output area, four field elements | 128 |
| constant area, 353 words | 11,296 |
| program image: 19 step copies of 808 words (4 bytes) and 1317 control instructions (8 bytes) | 71,944 |
| register file, 414 registers | 13,248 |
| **total** | **1,048,552** |



The total is **1,048,552 bytes**, at or below `2^20 = 1,048,576`, so `memory_log2_bytes = 19.99997` and the
memory term of the normalized cost is zero. Nothing else is stored: there is no advice, no precomputed table and
no retained randomness beyond the two coins.

## 8. Preprocessing

The constants the attempt loads are: the deployed round constants and MDS entries (organizer data, embedded in
the source); the line constants `LINE_A, LINE_B, LINE_U0, LINE_V0`; the 327 step constants with `E0` and
`OUTSCALE`; the exponent `INV5 = 5^{-1} mod (p - 1)`; and the integer literals of Section 4.1. The line and step constants are each the value of one closed formula in the organizer's constants, computed by
`line` and `build_step`. The integer literals of Section 4.1 are not closed formulas: they are the output of the
parameter selection of Section 1, a grid over accounting constants with two nested bisections. Neither depends
on a collision, a message pair or a search result, and nothing of the kind is stored; the selection reads only
the organizer's constants and the stated candidate ranges, so the program holds no advice. Their construction is charged as the row `prep` of Section 7.2, a conservative flat bound of
`2^36` word operations, which exceeds a direct count of the derivation by more than a factor of 100 and is
`2^{-90}` of the total; it is declared as `preprocessing_log2 = 36` and is inside the time bound, not added a
second time. The derivation's own memory is below the figure of Section 7.3.

## 9. Premise H1 and its evidence

**H1 (score-critical).** For the fixed map `F(x) = digest(message(x + rho0)) / OUTSCALE` at 56 partial rounds,
with `rho0` drawn as the frozen program draws it (the low 254 bits of a uniform 256-bit word), the attempt of
Section 4 succeeds with probability at least 0.39 at the filed budget, where Lemma 2 gives 0.390000001700 for a
uniformly random function.

This is our theory about a fixed function, not a theorem. The permutation is a fixed public map; the only
randomness is the attempt's two coins.

**What the premise actually has to transfer.** Lemma 2 uses four distinct properties of a random function, and
they are not equally supported:

1. the first-repeat (collision) rate of the walk, used in (a) and (b);
2. the distinguished-point rate for the predicate `x mod 2^128 < T`, used in (c), (d) and (e);
3. the distribution of gaps between consecutive distinguished points, used in (d);
4. the resulting table occupancy, used in (e).

**How the evidence is classified.** The qualification rules ask that exact small cases, organizer-executed
checks, measured behaviour of the target, extrapolation and heuristic conclusions be kept apart, so they are
separated here.

* *Exact small cases.* The nine control-flow fixtures of the declared experiment, which pin all six termination
  codes against a plainly written reference implementation of the same algorithm. These establish that the
  listing implements the algorithm, not anything about probability.
* *Organizer-executed.* The declared experiments of Section 10: the listing run on the real step program at
  output width 11 with the organizer recomputing the digests of every returned pair, and the exact
  recomputation of Lemma 2's arithmetic. The experiment protocol labels the programs' numeric observations
  participant data and does not credit them as resource costs.
* *Measured behaviour of the target (author-run).* The two campaigns below. They are proof-internal evidence,
  not organizer artifacts.
* *Extrapolation.* Everything from the widths and densities measured to the filed regime. This is the premise
  itself, and nothing below establishes it.

**Campaign 1: the first-repeat rate of the walk map.** For output widths `w = 16, 20, 24, 28, 30, 32` we ran
independent walks of the width-`w` reduction of the walk map itself, `x -> F(x) mod 2^w`, with a fresh coin and
a fresh start per walk derived from the disclosed seed `p56-h1-campaign-v1`, each walk continued to its exact
first repeated value, recording the repeat index `t`. For a uniformly random function on `M` points the
statistic `t (t - 1) / 2M` has mean `1 - O(M^{-1/2})`. A control ran the same procedure on seeded random
functions through the same code path, so the comparison between the two columns, not the distance of either
from 1, is what the measurement supports.

| width | walks | walk map | 95 percent interval | control | 95 percent interval |
| ---: | ---: | ---: | --- | ---: | --- |
| 16 | 4000 | 0.9839 | [0.954, 1.014] | 1.0138 | [0.983, 1.045] |
| 20 | 2000 | 0.9913 | [0.947, 1.036] | 1.0449 | [0.998, 1.091] |
| 24 | 1000 | 1.0094 | [0.946, 1.073] | 0.9805 | [0.919, 1.042] |
| 28 | 700 | 1.0068 | [0.936, 1.078] | 0.9789 | [0.903, 1.054] |
| 30 | 400 | 0.9522 | [0.862, 1.042] | 1.0018 | [0.908, 1.096] |
| 32 | 200 | 1.0188 | [0.880, 1.158] | 1.0996 | [0.970, 1.229] |



Pooled over 8,300 walks the walk map gives **0.9900** (95 percent interval [0.9688, 1.0112]) and the control
1.0158 (95 percent interval [0.9940, 1.0376]). The walk map's pooled value sits 0.0258 below the control's, about 1.7 standard errors
of the difference, which is consistent with noise and is reported rather than smoothed over: if it were a real
shortfall of that size in the collision rate, the sensitivity paragraph below prices it at about 0.0186
bits of additional budget to keep the success probability at 0.39.

**Campaign 2: the three properties campaign 1 does not measure.** The distinguished-point predicate depends
only on the low 128 bits of `F`, so its rate, the gap law and the table occupancy can be measured at densities a
sample can resolve, against the same seeded random-function control:

| property | measurement | walk map | control |
| --- | --- | ---: | ---: |
| distinguished-point rate | frequency of `F(x) mod 2^128 < 2^(128-8)` over 4,194,240 samples, as a z-score of the binomial | +1.76 | +0.62 |
| distinguished-point rate | frequency of `F(x) mod 2^128 < 2^(128-12)` over 4,194,240 samples, as a z-score of the binomial | +0.47 | -0.94 |
| distinguished-point rate | frequency of `F(x) mod 2^128 < 2^(128-16)` over 4,194,240 samples, as a z-score of the binomial | -1.25 | -1.75 |
| low-bit uniformity | chi-squared of the low 16 bits of `F(x) mod 2^128`, 65,536 cells, as a z-score | +0.86 | +0.29 |
| gap law | mean gap between distinguished points at density 2^-8, width 30 (ideal 256) | 257.3 | 253.5 |
| gap law | chi-squared of the gaps against the geometric law, 6 degrees of freedom, as a z-score | -1.31 | -0.41 |
| table occupancy | distinguished points per 4,096-step walk (ideal 16.00), as a z-score of the binomial | -0.54 | +1.30 |


Campaign 2 used 4,194,240 independent samples of `F` and 1,000 walks of 4,096 steps per column, with the coin drawn as the program draws it. Every z-score above is a deviation from the ideal value in units of its own standard error, so values within about two are consistent with random-function behaviour at the measured density.

**Disclosure of the run history.** Neither campaign was a single pre-specified run, and we do not present them
as such. Campaign 1 ran in three stages under the same seed. The first two measured
`x -> (F(x) * OUTSCALE) mod 2^w`, that is the truncated digest rather than the truncated walk map: widths 16, 20,
24 and 28 first, then, after seeing those results, width 28 extended and widths 30 and 32 added. A review of
this package observed that the digest and the walk map differ as maps, because truncation does not commute with
the division by `OUTSCALE`, and that the later widths had been left out of the write-up. The third stage
therefore re-ran all six widths on the walk map itself with the program's own coin distribution, and that run is
the table above; the earlier digest runs are archived with the submission and are statistically similar. Campaign 2 was specified after campaign 1. Its gap test was first run with a design that recorded the gaps falling inside a fixed number of steps, which censors the last gap of every walk and biased both the walk map and its control short (means 241.8 and 237.7 against 256, with both arms failing the geometric fit); that run is archived with the submission as `h1_properties-v1-censored`, and the test was re-run collecting a fixed number of gaps per walk, which is the table above. The rate, low-bit and occupancy tests were unchanged between the two runs apart from a larger sample. Because widths and tests were chosen partly after seeing earlier
results, every interval here is descriptive and none is the coverage of a pre-registered test; the rules name
exactly this pattern as something that invalidates an advertised coverage claim, so no coverage is advertised.
No width, seed, walk or test was discarded, and no result is withheld.

**What these experiments cannot establish.** The filed budget needs the four transfers to hold at a
distinguished density of `2^-112.26455` over about `2^127` steps of a 254-bit map. Campaign 1 reaches 32-bit
outputs and trails of about 2^16 steps; campaign 2 reaches densities of 2^-8 to 2^-16 and walks of 4,096 steps.
The ratio between what is measured and what is filed is more than 2^95 in density and more than 2^110 in trail
length, and no feasible experiment closes it: a single full-width trail is the attack itself. Sampled
measurements at these scales can exclude gross departures from random-function behaviour; they cannot bound the
deficit at the `5.6e-09` level the filed budget needs, and the rules are explicit that a sampled experiment
does not prove a full-scale success bound. The measurements are evidence that the premise is not visibly false
where it can be seen; they are not validation of the premise, and this entry does not present them as such.

**Coin distribution.** The frozen program draws `rho0` as the low 254 bits of a uniform word, which is uniform
on `[0, 2^254)` rather than on the field, because `p = 2^254 + c` with `c = p mod 2^128`. The campaign drew its
coin uniformly on the field. The total variation distance between the two is `c / p < 2^-128`, so the premise is
insensitive to the difference; H1 is stated for the distribution the program uses. Lemma 2 is unaffected because
it holds for every fixed start.

**Sensitivity.** A collision rate `c` times the random-function rate changes the success bound to about
`1 - exp(-c x) - n / N - eps` with `x = 0.49506`. The budget is the least one that reaches 0.39, so the margin
over 0.39 is only `1.70e-09` and the claim as filed tolerates a relative shortfall of about `5.6e-09` in
the collision rate: this entry buys no robustness margin. Absorbing a real shortfall costs budget, at
`-0.5 log2(c)` bits:

| collision rate `c` | extra time to still reach 0.39 |
| ---: | ---: |
| 0.99 | +0.00725 bits |
| 0.95 | +0.03700 bits |
| 0.90 | +0.07600 bits |


The measurement has a standard error of 0.0108 on the pooled statistic, so it can exclude departures of a few
percent and cannot speak to the `5.6e-09` level the filed budget needs. This gap between the precision the
filed budget requires and the resolution of the evidence is a property of this entry as filed, and it is stated
here rather than left for a reviewer to find. The same construction re-tuned at a 0.45 random-function bound
gives 126.354773 (Section 1.1); that figure is not what is claimed here.

## 10. Declared experiments

Two experiments, both `python-message-pairs-v1`, in `experiments/manifest.json`.

1. **`poseidon-orchard-r56-trail-machine-w11-v1`** (`experiments/trail_machine.py`). The complete search program
   of Section 4 as an instruction listing, executed by a counting interpreter, on the real step program at output
   width 11, with the reduced-width parameters stated in the program. Each organizer trial derives its coins from
   the organizer's seed, runs the search and returns a pair of distinct messages whose digests agree on the
   low 11 bits when the search succeeds; the organizer recomputes that agreement with its own digest. An 11-bit
   mask event is not a collision of the target, and nothing here is offered as one. The program also checks, in
   every trial, that `F(x) * OUTSCALE` equals the digest of `message(x + rho0)` at `r = 56` on a seed-derived
   point, against the reference implementation embedded in the submitted source rather than the organizer's own
   function, which the container does not hold. It reports whether the listing's termination and recovered pair
   agree with a plainly written reference search on the same map, and whether its 9 deterministic
   control-flow fixtures pass, among them the step-budget halt, the table-full halt and the start-on-cycle halt.
   The reported observations are participant counters, which the experiment protocol does not credit as resource
   costs: termination code, trail steps, walk steps, lockstep rounds, insertions, executed steps, control
   operations, memory operations, the total charge, and the structural counts of the listing. **Success frequencies in this experiment are control-flow coverage, not
   a probability estimate**: the width is small, the parameters are reduced, and no full-width probability is
   inferred from them.
2. **`poseidon-orchard-r56-success-bound-v1`** (`experiments/success_bound.py`). Exact certification of Lemma 2
   at the submitted parameters in the organizer's executor: the six loss terms and the resulting bound, in
   60-digit decimals rounded outward. The program ignores the organizer seeds, certifies once, reports the same
   terms in every trial row and returns no message pairs. Its evidentiary content is that the organizer's
   executor reproduces the quoted arithmetic from the submitted source. **It establishes arithmetic in the
   random-function model only; it says nothing about the fixed target, which is premise H1.**

## 11. Comparator

Comparisons are made within the same round count and cost model, since `C(r)` differs per round and normalized
costs at different round counts are not comparable.

| entry | rounds | normalized cost | note |
| --- | --- | --- | --- |
| `b810ea13` (tanctl) | 56 | 126.226166 | current best 56-round entry; the predecessor re-tuned to a 0.39 bound, 812-operation step, 4-step unrolling |
| `6de8a0a2` (tanctl) | 56 | 126.363427 | its predecessor; a 0.45 random-function margin |
| `56fb07fc` (Jbenisek) | 56 | 126.711170 | earlier method at 56 rounds |
| this entry | 56 | 126.21753 | 0.00864 bits below `b810ea13`, 0.14590 below `6de8a0a2` |
| `7f88498e` (Jbenisek) | 48 | 126.22283 | same method at 48 rounds, not comparable across `r` |

The 0.00864-bit difference against the current best, `b810ea13`, is this entry's parameters and
ledger at the same success bound; the 0.14590-bit difference against `6de8a0a2` adds that entry's 0.45
probability margin (Section 1.1). Only the former is ours. Review status on the public
entries is `plausible_not_refuted`; none is human-accepted.

## 12. Heuristics and limitations

* **H1** (score-critical), Section 9: the fixed map behaves like a uniformly random function for this search.
  The random-function bound exceeds 0.39 by 1.70e-09, so a fixed-target deficit larger than that defeats the
  claim; the filed budget is the least one reaching 0.39, so it buys no robustness margin, and absorbing a
  one percent shortfall in the collision rate would cost about 0.00725 bits of time (Section 9).
* **H-MACHINE** (score-critical), Section 7.1: the declared register file and the instruction encoding. The
  contract fixes no register count. Charging instruction fetch at one 32-byte load per fetched step word would
  add about 0.17 bits to the time bound, counting the trail rows only. The memory axis is a knife edge
  rather than a slope: the layout sits 24 bytes below 2^20, so a reviewer who declines the 4-byte step
  encoding and charges 8 bytes per step word adds 61,408 bytes to the image, which pushes memory above one
  mebibyte and turns the memory term of the normalized cost from zero into about 0.08208 bits.
* The success argument is generic. No property of the Orchard round function is used or claimed, and no
  cryptanalytic weakness is asserted.
* The attack was not executed at full scale, and no collision of the complete target is exhibited. The claimed
  figures are upper bounds on the resources of the frozen program, in the cost model's units.

## Appendix A: recomputation of the ledger and the score

The rows of Section 7.2 and the total are reproduced by this script, which uses only the integers printed in
that table. It is included so that the score can be rechecked inside the candidate, without the host-side tool.

```python
from math import log2, ceil
C = 1392
rows = {
    'setup': 7366,
    'trail': 137384132364444288116185333303143903734670,
    'dp_events': 7839216002,
    'recovery_fixed': 235,
    'recovery_walk': 101675512919990045359528698507410201585,
    'recovery_lockstep': 203101515378826740914494136404986267699,
    'messages': 12250,
    'prep': 68719476736,
}
total = sum(rows.values())
print('total', total)
print('log2(total / C) = %.6f' % log2(total / C))
print('claimed %.5f' % (ceil(log2(total / C) * 100000) / 100000))

```

## Appendix B: the collision-rate campaign program

The measurement of Section 9 was produced by the following program (standard library only, plus the step
program of Appendix C of this package's experiment source, which it imports). It is reproduced so that the
evidence for H1 is inside the candidate. The per-width results it produced are the table of Section 9.

```python
"""Author-run collision-rate measurement for the P56 heuristic H1 (host side; not an organizer experiment).

For each output width w, runs K independent walks of the width-w reduction of the walk map itself,
x -> F(x) mod 2^w with F(x) = digest(message(x + rho0)) / OUTSCALE (fresh coin and start per walk from a seeded
generator), until the first repeated value, and records the repeat index t. The coin is drawn as the frozen
program draws it, as the low 254 bits of a uniform word. Passing "digest" as the map measures
x -> digest(message(x + rho0)) mod 2^w instead, which is the walk map times a fixed nonzero constant; the two
differ as maps, and the earlier stages of this campaign measured that variant.
A control runs the same procedure on seeded uniformly random functions on 2^w points. For a uniformly random
function P(t > m) = prod_{i<m} (1 - (i + 1) / 2^w); the statistic t (t - 1) / (2 N) has mean 1 - O(N^-1/2) under that law,
so mean values and their standard errors are reported per width for the real map and the control. Results are
written as JSON. Usage: python3 tools/h1_campaign_p56.py <out.json> <procs> w:K [w:K ...]
"""
import hashlib
import json
import math
import sys
from multiprocessing import Pool

sys.dont_write_bytecode = True
sys.path.insert(0, __file__.rsplit("/", 2)[0] + "/candidates-dev/poseidon-p56/experiments")
import trail_machine as tm      # noqa: E402

SEED = b"p56-h1-campaign-v1"


MAP = "walk"          # "walk" for F itself, "digest" for F times OUTSCALE


def coins(tag, w, i):
    """The coin is drawn as the frozen program draws it: the low 254 bits of a uniform word."""
    h = hashlib.sha256(SEED + tag + bytes([w]) + i.to_bytes(4, "big")).digest()
    g = hashlib.sha256(h).digest()
    return int.from_bytes(h, "little") & ((1 << 254) - 1), int.from_bytes(g, "little") & ((1 << w) - 1)


def walk_real(args):
    w, i = args
    rho0, x = coins(b"real", w, i)
    F = tm.make_F(rho0)
    mask = (1 << w) - 1
    scale = tm.OUTSCALE if MAP == "digest" else 1
    seen = {x}
    t = 0
    while True:
        x = (F(x) * scale % tm.P) & mask
        t += 1
        if x in seen:
            return t
        seen.add(x)


def walk_control(args):
    w, i = args
    _, x = coins(b"ctrl", w, i)
    mask = (1 << w) - 1
    key = hashlib.sha256(SEED + b"ctrl-fn" + bytes([w]) + i.to_bytes(4, "big")).digest()
    seen = {x}
    t = 0
    while True:
        x = int.from_bytes(hashlib.sha256(key + x.to_bytes(8, "big")).digest()[:8], "big") & mask
        t += 1
        if x in seen:
            return t
        seen.add(x)


def summarize(ts, w):
    n = 1 << w
    vals = [t * (t - 1) / (2 * n) for t in ts]
    m = sum(vals) / len(vals)
    var = sum((v - m) ** 2 for v in vals) / (len(vals) - 1)
    se = math.sqrt(var / len(vals))
    return dict(walks=len(ts), mean_t=sum(ts) / len(ts), mean_stat=m, se_stat=se, ci95=[m - 1.96 * se, m + 1.96 * se])


def main():
    global MAP
    out, procs = sys.argv[1], int(sys.argv[2])
    args = sys.argv[3:]
    if args and args[0] in ("walk", "digest"):
        MAP = args.pop(0)
    plan = [(int(a.split(":")[0]), int(a.split(":")[1])) for a in args]
    print("map:", MAP, flush=True)
    res = {}
    with Pool(procs) as pool:
        for w, K in plan:
            real = pool.map(walk_real, [(w, i) for i in range(K)], chunksize=1)
            ctrl = pool.map(walk_control, [(w, i) for i in range(K)], chunksize=4)
            res[str(w)] = dict(real=summarize(real, w), control=summarize(ctrl, w), t_real=real, t_control=ctrl)
            r, c = res[str(w)]["real"], res[str(w)]["control"]
            print(f"w={w}: real mean stat {r['mean_stat']:.3f} +- {r['se_stat']:.3f} (mean t {r['mean_t']:.1f}); "
                  f"control {c['mean_stat']:.3f} +- {c['se_stat']:.3f} (mean t {c['mean_t']:.1f}); walks {K}", flush=True)
            json.dump(dict(seed=SEED.decode(), map=MAP, results=res), open(out, "w"))


if __name__ == "__main__":
    main()
```
