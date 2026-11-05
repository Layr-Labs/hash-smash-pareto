# Poseidon-Orchard r56: generic collision search with a rho walk

## 1. Target

`poseidon-orchard-r56-prefix-v1`: 56 partial rounds plus the eight fixed full rounds,
deployed halo2_poseidon 0.2.0 constants and MDS, initialization `[nk, rho, 2^65]`,
digest equal to the final coordinate zero as a canonical 32-byte Pallas element.

The message domain is two canonical field elements `(nk, rho)`, so the map under study is

    F : F_p x F_p -> F_p,   F(nk, rho) = z0,

with `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`,
`log2(p) = 254.0` exactly at the precision used here.

## 2. A collision exists without any structural assumption

`F` maps `2^510` admissible inputs onto `2^254` field elements. By pigeonhole it cannot be
injective, so at least one pair of distinct canonical `(nk, rho)` tuples shares a digest.
This step needs no assumption about Poseidon, no heuristic and no experiment. It is the
only part of the candidate that is unconditional.

## 3. Construction searched

I use the standard van Oorschot-Wiener distinguished-point variant of Pollard's rho for
collision search on a single function:

- Fix a deterministic walk index `g(x) = (x mod 32) + 1` and 32 constants `c_1..c_32`
  sampled once from the target's own randomness source.
- Walk: `X_{i+1} = F(X_i)` restarted as `X_{i+1} = F(X_i + c_{g(X_i)})` when the iterate is
  a distinguished point. `X_0 = (nk_0, rho_0)` is a fresh uniform sample.
- Distinguished point: the low 114 bits of `z0` are all zero, which occurs with
  probability `2^-114` under the random-function heuristic.
- Store each distinguished point with the walk start and step count. A repeated
  distinguished point recovers two distinct inputs `u != v` with `F(u) = F(v)`; the pair is
  then re-evaluated once through the reference digest to confirm equality of the full
  canonical 32-byte encoding.

No inverse of `F`, no algebraic modelling of `x^5`, and no attack on the MDS layer is used.
This is the generic collision attack that applies to any function with a 254-bit image.

## 4. Step count

The birthday model gives collision probability `1 - exp(-N^2 / (2p))` after `N` walk steps.
The rho walk needs `sqrt(pi p / 2) = 1.2533 sqrt(p)` steps in expectation, which is
`2^127.326` for `log2(p) = 254.0`.

Declared bound, with the constant rounded up and 0.12 bits of slack for distinguished-point
handling and confirmation:

    time_log2 = 127.45.

Sanity check on the same arithmetic: `2^127.45` steps are `2^127.45 / 2^127.326 = 1.09`
times the expected count, comfortably above it, so the declared figure is not a
downward-rounded expectation.

## 5. Success probability

At `N = 2^127.45`, the birthday exponent is `N^2/(2p) = 2^(2*127.45 - 255.0) = 2^-0.10 =
0.9330`, so the probability is

    1 - exp(-0.9330) = 0.6065,

and the declared `success_probability = 0.60` is met, above the required 0.39. The
declaration is a lower bound on the probability at the declared step count, not the maximum
attainable. At the bare expectation `N = 2^127.326` the same formula gives `0.544`, which is
why the declared step count is held 0.124 bits above the expectation rather than at it.

## 6. Cost accounting

One r56 Orchard compression is one target-compression unit by the cost model, and the model
charges `C = 216 + 21*56 = 1392` field operations behind it. The declared time counts:

| Item | Cost |
| --- | --- |
| `2^127.45` walk steps, one compression each | `2^127.45` units |
| walk index extraction, `g(X)` and conditional add | included in the step |
| 32-way constant table in registers | `O(1)` per step |
| `2^13.45` distinguished-point insertions and comparisons | `2^13.45 * ~50` instructions, `2^9.9` units |
| one reference re-evaluation to confirm the pair | `1` unit |
| sampling of `X_0` and the 32 constants | `O(1)` |

The table lookup term is `2^118` times smaller than the step term and does not move the
`log2` at this precision. Preprocessing is zero: the constants come from the deployed
specification and the walk needs no offline table. Nonuniform advice is zero bytes.

## 7. Memory

`2^13.45` distinguished points at 48 bytes each is `2^19.04` bytes, declared rounded **up**
as `memory_log2_bytes = 19.1`. Because the normalization subtracts `log2(2^20) = 20`, this
sits below the free allowance and contributes nothing to `normalizedTimeMemoryLog2`, which
is therefore also `127.45`.

The `2^19.1`-byte table fits in the memory of a single machine, so the whole search is
sequential; no parallel amortization is claimed and no inter-process communication is
charged.

## 8. What this candidate is not

- It is not an attack that exploits Poseidon's algebraic structure. It is the generic
  collision bound for a 254-bit-output compression, and it therefore does not improve on a
  structural attack at lower round counts. Its value in the Pareto objective is that it
  reaches `rounds = 56`, the complete deployed round count, at the lowest cost any method
  can achieve on a black-box 254-bit digest: the birthday bound `sqrt(p) = 2^127.0` is a
  universal lower bound for generic collision search, so no candidate can go materially
  below `127.0` at this round count without a structural break.
- It does not claim to invert the permutation or to find a preimage.
- The declared `127.45` is therefore close to the best achievable at r56 rather than a
  weak bound dressed up.
- The only score-critical heuristic is `random-function-walk` (see `claim.json`): the step
  count and success probability assume the walk mixes like a random function. Existence of
  the collision is unconditional; only the cost to find it rests on that heuristic.

## 9. Reproduction notes

No experiment is declared: the construction is analytic and its cost is a closed-form
count, so there is nothing for the bounded executor to run that would change the score. The
certificate manifest is retained and empty. A reader who wants to instantiate the search at
toy scale can replace `F` with the reference `verifier/poseidon.py:digest` at any admitted
round count below 8 and observe that the same walk recovers a colliding pair, but such a run
is evidence about the walk, not about the r56 cost, and is deliberately not used to support
the declared numbers.
