# Orchard Poseidon r = 3: two-free-round line, odd part, one square-root test; executed full-width collision certificate

## 1. Claim

Target `poseidon-orchard-r3-prefix-v1`: Orchard P128Pow5T3 over Pallas, width 3,
state `[nk, rho, 2^65]`, full rounds 0-3, partial rounds 4, 5, 6, full rounds
60-63, digest = coordinate 0 in canonical 32-byte little-endian encoding. The
claim is an ordinary collision: two distinct canonical pairs `(nk, rho)` whose
complete digests are equal.

* `time_log2 = 30.86920` target-compression units, `C(3) = 279` primitive
  operations per unit (section 6).
* `memory_log2_bytes = 27.76509` (228,098,752 bytes, section 7).
* `success_probability = 0.39126` for one centre, from the premise H-ONE
  (section 8); the executed instance in section 9 is a good centre.
* `preprocessing_log2 = 20`: the offline derivation is a closed formula
  (section 6.2), charged at the declared cap of 1,048,576 operations (2^20) inside
  `time_log2`.
* Normalized cost `30.86920 + (27.76509 - 20) = 38.63429`.

**What is new in this entry.** The full-width collision in section 9 was
executed: the two 64-byte messages, their common digest and the search
parameters are in `certificates/`, and the organizer's reference checker
recomputes both digests. The construction is the two-free-round line of the
r = 14 lineage applied at r = 3 with a simple coefficient-domain NTT
implementation; its cost bound is higher than the best r = 3 paper entries
and is not claimed to improve the frontier. The value of the entry is the
verified certificate and an end-to-end check of the line/odd-part construction
at depth N = 9 S-box layers.

## 2. Target

`p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`.
`p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a bijection of `F_p`;
write `e = (4(p-1)+1)/5` for its inverse. `M` is the deployed 3x3 MDS and
`c_{i,k}` the deployed round constant of round `i`, lane `k`
(`pareto/orchard-pallas-constants.json`; never regenerated).

A round is: add the three constants, raise the S-boxed lanes to the fifth
power (all three lanes in a full round, lane 0 only in a partial round),
multiply by `M`. The permutation is the rounds `0,1,2,3`, `4,...,4+r-1`,
`60,...,63` with r = 3. Inputs are two canonical field elements `nk, rho < p`
encoded as 32 little-endian bytes each; the digest is the whole first lane of
the final state, 32 little-endian bytes. Everything below is one fixed target.

## 3. Two free rounds on a line

Write `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5`.
The map `(nk,rho) -> (U,V)` is a bijection of `[0,p)^2` with inverse
`nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`, and `K` is a constant. After round
0 the state is `M (U,V,K)^T`.

The round-1 S-box input is `x_k = M_{k0} U + M_{k1} V + b_k` with
`b_k = M_{k2} K + c_{1,k}`, affine in `(U,V)`. Use the line `j = 0`: let
`Q = (U_Q,V_Q)` solve `x_1 = x_2 = 0` (the 2x2 minor `M_{10}M_{21}-M_{11}M_{20}`
is nonzero on the deployed constants), put `(a,b) = (M_{01}, -M_{00})` and

```
(U,V) = Q + tau (a,b).
```

Then `x_0 = kappa` is constant and `x_i = d_i tau` for `i = 1,2`, with
`d_i = M_{i0} a + M_{i1} b` and `d_0 = M_{00}M_{01} - M_{01}M_{00} = 0`. With
`W = tau^5` the round-1 S-box output is `v_0 + W v_1`, where
`v_0 = kappa^5 e_0` and `v_1 = d_1^5 e_1 + d_2^5 e_2` have disjoint support.
After the round-1 MDS the state is `alpha + beta W` with
`alpha = M v_0`, `beta = M v_1`.

Rounds 2, 3 (full), 4, 5, 6 (partial), 60, 61, 62, 63 (full) put nine S-box
layers on top of this affine map, so the digest is `F(W)` with

```
deg F = 5^9 = D = 1,953,125,
```

and the leading coefficient is nonzero on the deployed constants (checked by
propagating leading coefficients; the certificate run re-derives `F` at
`tau` and compares with the reference hash). For every `tau != 0`,
`F(tau^5)` equals the reference digest of the canonical pair built from
`tau`; this identity was checked against `verifier/poseidon.py` at
r = 0,...,5 on random `tau` and is re-checked by the declared experiment
`line-ladder-w10` when the organizer executes it.

## 4. Odd part and the collision criterion

For a centre `c` in `F_p` define

```
G(c,t) = (F(c+t) - F(c-t)) / (2t) = g_c(t^2),
```

where `g_c` is the monic odd part of `F` about `c`, of degree
`m = (D-1)/2 = 976,562`. If `S = s^2 != 0` is a root of `g_c` in `F_p` then
`F(c+s) = F(c-s)` with `c+s != c-s`. Since `x -> x^5` is injective, the two
values `W_1 = c+s`, `W_2 = c-s` give distinct `tau_i = W_i^e`, distinct line
points `Q + tau_i (a,b)`, and hence distinct canonical pairs
`(U_i^e - c_{0,0}, V_i^e - c_{0,1})`; their digests are `F(c+s) = F(c-s)`.
This is an ordinary collision of the complete digest. A root `S = 0` is not
used (it gives `s = 0`). Conversely every collision produced by this
construction arises this way.

## 5. Algorithm (one centre, one thread)

```
A  draw c uniformly from F_p from one fresh random 256-bit word
B  interpolate g_c: B = 2^20; theta of order 2^21; for i < B evaluate
   v_i = (F(c + theta^i) - F(c - theta^i)) / (2 theta^i) and recover the
   coefficients of g_c by one inverse NTT of length B (deg g_c = m < B)
C  R := x^((p-1)/2) mod g_c by left-to-right binary powering
D  G := gcd(g_c, R - 1) (monic)
E  if deg G = 0 or deg G > 16: the trial fails. Otherwise isolate a root S of
   G (degree at most 16, Cantor-Zassenhaus), take s with s^2 = S, form
   W_1 = c+s, W_2 = c-s, tau_i = W_i^e, the two canonical pairs, and verify
   both reference hashes; output the pair.
```

One centre is tried (`K = 1`); a failed trial ends the algorithm. The
algorithm never outputs a non-collision: the last step recomputes both
reference digests and compares them and the pairs.

The roots of `G` are exactly the roots of `g_c` that are nonzero squares:
`G = gcd(g_c, x^E - 1)` with `E = (p-1)/2` is squarefree and splits into the
distinct linear factors `(x - S)` for such `S` (`x^E - 1` is squarefree because
`gcd(x^E - 1, E x^(E-1)) = 1`). If `1 <= deg G <= 16` stage E isolates one in
at most 16 rounds with failure probability at most `120 (1/2 + 2^-127)^16 =
0.0018311`: a failed isolation leaves some pair of distinct roots unseparated
in every round, a uniform shift separates a fixed pair whenever their
quadratic characters differ (failure at most `1/2 + 2^-127` per round), and
there are at most `C(16,2) = 120` pairs.

## 6. Ledger: worst-case operation count

Model `orchard-field-ram-v2`: field addition/subtraction/multiplication,
256-bit word operations, loads/stores and control operations each cost 1;
one selected-round permutation is one unit; `C(3) = 216 + 21*3 = 279`.
Every operation below is counted; nothing is charged as a permutation call.

A transform of size `n` is a radix-2 in-place NTT: `(n/2) log2(n)` butterflies
at 9 operations each (one twiddle formation, one butterfly multiplication, two
additions, two loads, two stores, one control operation) plus `2n` operations
for the index permutation and the normalisation. Twiddles are formed on the
fly, so no twiddle table is stored. Write `T(n)` for this cost,
`T(2^21) = 202,375,168` and `T(2^20) = 96,468,992`.

| row | what is charged | operations |
|---|---|---:|
| init | line setup (4,910) and constants/bookkeeping | 14,910 |
| A | one coin draw (31) and stage bookkeeping | 1,031 |
| B | `2B = 2,097,152` line evaluations at 231 operations each (3 entries, 2 full rounds, 3 partial rounds, 4 full rounds; 147 multiplications and 84 additions), the point loop (11 per node), one inverse NTT of length B at `T(2^20)`, normalisation | 593,494,016 |
| C | the Newton reciprocal of the reversed `g_c` (4 products = 12 transforms), 253 squarings and 45 multiplications by `x` modulo `g_c`: a modular squaring is 8 transforms of size `2^21` (2 for the product, 3 for the quotient and 3 for the remainder product), a modular multiplication 9 (3+3+3) | 493,997,785,088 |
| D | half-gcd of `(g_c, R-1)`: `4 M(m) ceil(log2 m)` with `M(m) = 3` transforms of size `2^21`, plus 20 transforms | 52,617,543,680 |
| E | root isolation at degree at most 16: 16 rounds at the lineage's register-resident charge `R(16) = 196,915` per round plus bookkeeping | 3,160,000 |
| F | square root (Tonelli-Shanks, 2-adicity 32), three fifth roots (`x^e`, 330 multiplications each) and back-map | 100,000 |
| G | two reference hashes at 279 operations each, plus bookkeeping | 1,590 |
| output | fixed formatting and write | 3,390,000 |
| offline | closed-form derivation of the literals, counted (section 6.2) and charged at the declared cap `2^20` | 1,048,576 |
| **N_max** | | **547,216,538,891** |

`N_max = 547,216,538,891` operations `= 1,961,349,601.76` units;
`log2(N_max/279) = 30.8691917...`, claimed as `30.86920` (rounded up at five
decimals). Every row is an upper bound that the algorithm meets for every coin
sequence: the loops of B and C have lengths fixed by `m`, `B` and the exponent;
stage D is charged for the normal remainder sequence and any other sequence
ends the trial after a prefix (the half-gcd tests every quotient and return;
a failed test aborts the trial, and the trial price is charged in full);
stage E is capped at 16 rounds at degree at most 16; stage F is a fixed number
of exponentiations. The transform size is `2^21 >= 2m-1`, so a product of two
degree-`<m` polynomials is exact; the reduction uses the precomputed reciprocal
of the reversed `g_c` and two further products per multiplication. Every load,
store, permutation and normalisation is included; nothing is charged as a
memory-free operation.

### 6.2 Offline derivation

The line parameters `(U_Q,V_Q,kappa,d_1,d_2,alpha,beta)` and the NTT roots
`theta, omega` are closed formulas in `p` and the 192 round constants and 9
MDS entries, computed once by at most 136,785 operations (202 constants at
324 each, 489 field operations at 4, 90 word operations at 3, 211 output
literals at 324). This is charged at the declared cap `2^20 = 1,048,576`
inside `N_max`; `preprocessing_log2 = 20`.

## 7. Memory

| term | bytes |
|---|---:|
| `g_c` coefficients (m words of 32 bytes) | 31,249,984 |
| exponentiation accumulator and residues (m words) | 31,249,984 |
| Newton reciprocal of the reversed `g_c` (m words) | 31,249,984 |
| two transform arrays of `2^21` words (they hold the products and the reduction scratch) | 134,217,728 |
| code, constants and stack | 131,072 |
| **total** | **228,098,752** |

`log2(228,098,752) = 27.76508...`, claimed as `27.76509` (rounded up). The
algorithm is single-threaded; twiddles are formed on the fly and no twiddle
table is stored; no precomputed advice is stored.

## 8. Success probability

Randomness: one fresh uniform 256-bit word for the centre (the cost model's
random-word primitive; the draw is within statistical distance `< 2^-128` of
uniform on `F_p`, as in the lineage's section 4.1.1). Isolation uses the same
primitive; its failure probability is at most `120 (1/2 + 2^-127)^16 =
0.0018311` (section 5).

**Premise H-ONE.** For `c` uniform on `F_p`, `P(1 <= k(c) <= 16) >= 0.3931`,
where `k(c)` is the number of nonzero squares `S` with `g_c(S) = 0`.

*Statement and scope:* this fixed target, this line (`j = 0` of the first two
rounds), this `F`; centres uniform on `F_p`. Nothing is claimed for other round
counts.
*Evidence:* `k(c)` counts the positive fixed points of the Frobenius element in
the hyperoctahedral monodromy group `B_m` of the cover `G(c,t) = g_c(t^2) = 0`;
for the full group the limit law is Poisson(1/2), giving
`1 - e^{-1/2} = 0.3934693`, and the four-moment Bonferroni bound is
`151/384 = 0.3932292 >= 0.3931`. The monodromy is computed to be `B_12` and
`B_62` at N = 2 and 3 S-box layers on the deployed constants in the lineage
(proof 9.3(c)); toy-field counts over 27 cases with 3 to 8 layers lie in
`[0.39214, 0.39436]` (the lowest toy value is 0.00096 below `q`; with
`q = 0.39214` the bound below would still be 0.39031 > 0.39). The executed
instance of section 9 is at the target
depth N = 9 and its centre has `k(c) = 1` (1 <= 1 <= 16), one
direct observation of a good centre at the target depth.
*Extrapolation and limitations:* the law is a theorem only at N = 2, 3; the
premise extrapolates it to N = 9 with an allowance of 0.0003693. It concerns
this `F`, not every polynomial of degree D; it is false for permutation
polynomials and for decomposable `F` with imprimitive monodromy. No
independence between centres is used (K = 1). The executed instance is one
sample, not a probability estimate.

With H-ONE and the coin/isolation bounds, `P(success) >= 0.3931 - 0.0018311 -
2^-48 - 2^-128 = 0.3912689... > 0.39126`, claimed as `0.39126` (the claim schema
requires at least 0.39, so the value is rounded down).

## 9. Executed certificate

The search of section 5 was run with centre `c = 123456789`. The polynomial `g_c`
was interpolated at `B = 2^20` nodes, its degree is exactly 976,562, and
`G = gcd(g_c, x^((p-1)/2) - 1)` has degree `1`; a root `S` gave
`s = 0x2dc2ce9e75c3149a003f51f258c6e3bc83a3fef291951e58afce108203ec724`. The two canonical messages and their common digest are stored in
`certificates/message_a.bin`, `certificates/message_b.bin` and
`certificates/manifest.json`. They were produced by an independent
big-integer implementation (the same line, odd part and root criterion) and
verified with the organizer's `verifier/poseidon.py`:

```
message_a = 5305d1349eec6c774659a15af6b44637d7fb8a8827a21c6acddf4df55f7eb62f773581cea72b9b96a56db465dedf735a9f63e0ea111c16e6a7d89cbf46611f29
message_b = cd37cb09497a79c2e7d279599308c732ccde14a3838d050153c454bc65f4ef069aa36a18e75d71789f321e9b3d90fe084436ce3c59f0f95d8a203d5c8007861a
digest    = 46fc99ff4bac7ac6d59eddad56ba4b9ac902e2dbb145b5674f61e7594d724b2a
```

The declared experiments are designed to run under the organizer's isolated
executor: `line-ladder-w10` checks the line map and the digest at 10 leading
bits on 256 fresh centres, and `certificate-replay` replays this full collision
in every one of 256 trials. They are evidence only when the organizer executes
them; no execution report is claimed here. The certificate checker recomputes
both digests directly and does not execute participant code.

## 10. Limitations

* H-ONE is a premise, not proved at the target depth; the executed instance is
  one good centre, not a probability bound.
* The cost bound is for the simple coefficient-domain NTT algorithm of
  section 5 and is higher than the best published r = 3 paper entries; this
  entry does not claim a Pareto improvement in cost.
* The certificate was found by an independent implementation; the resource
  bound describes the specified algorithm, not that implementation's constant
  factors. The certificate is verified by the organizer's reference, so the
  collision itself does not depend on either implementation's accounting.
* No claim is made for other round counts, for chosen capacity, for encoding
  aliases or for the complete Orchard nullifier.
