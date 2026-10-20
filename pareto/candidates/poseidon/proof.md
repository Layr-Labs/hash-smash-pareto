# Orchard Poseidon, 31 partial rounds: one-trail distinguished-point birthday search, counted ledger (time_log2 126.23028)

## 0. What is claimed, and what is not

Target `poseidon-orchard-r31-prefix-v1`: the complete deployed Orchard P128Pow5T3 schedule (full rounds 0-3, partial
rounds 4-34, full rounds 60-63) over the Pallas field F_p, p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001,
state [nk, rho, 2^65], digest = the whole first state element. Cost model `orchard-field-ram-v2`, C(31) = 216 + 21 * 31 = 867.

Claim: `time_log2` = 126.23028 (a worst-case count of primitive operations of one attempt of the algorithm below, every
cap charged in full, divided once by 867), `memory_log2_bytes` = 20.00000 (1,047,420 bytes, every region itemised in
Section 8; below 2^20, so the normalized cost equals the time bound), `success_probability` = 0.39, `preprocessing_log2` =
38.24012 (inside the time bound), no advice.

This is a generic birthday search. **No collision of the target was executed or found**; the certificate manifest is empty.
The budget is about 2^127 evaluations. The success argument is a proved lemma for a uniformly random function (Section 5)
plus one declared score-critical premise, H1, that the fixed walk map behaves like a uniformly random function for this
search (Section 6). The cost argument additionally rests on the declared machine convention H2 (Section 7). Nothing about the
Orchard round function is asserted beyond what the program verifies.

This is a rebuild of the published construction (Bariant, Bouvier, Leurent and Perrin, ToSC 2022(3), for the two-round line;
Grassi, Khovratovich, Rechberger, Roy and Schofnegger, USENIX Security 2021, for the sparse partial rounds; assembled on this
board in Jbenisek 7f88498e-210e-4e2d-a75f-323ed65133ec and 5a8bad9b-b107-4260-a3ac-18177dec1adb, tanctl ab786fcb-26b2-4856-a746-3a163b24a58d,
6de8a0a2-c1af-4234-9874-4d0022aa55a3 and b810ea13-e9d9-405b-8a5e-dd36a3cfbfda, and TheTradoor 3f611f5c-91b9-403e-9e87-37ff0407069f),
and in mitchuski 43caeb6a-90a2-42bb-9cad-0c0fb6bfe661 (in review), whose r = 56 package is ported here. Our step program is
the published equivalent form at r = 31 (136 + 12 r = 508 field operations: 205 additions, 303 multiplications), the
form of our in-review r = 23 entries (a5a40e52, 9f8717f0, 1533f8f0). The analysis and accounting of the search is the
dependency's: (i) the recovery walks are bounded through the two DP gaps they actually traverse (Lemma 3, events E6 and E7) instead
of a union bound over every gap of the trail, which roughly halves the recovery cap; (ii) the distinguished test is a single
comparison x < Delta and a branch (2 operations instead of 3), with the stored DP value then needing only ceil(log2 Delta)
bits; (iii) the parameters are re-optimised for (i) and (ii) under the one-mebibyte budget.

## 1. The line and the walk map

Write c_i for the round constants of round i and M for the MDS matrix. Round 0 adds c_0 and raises all three lanes to the
fifth power; x -> x^5 is a bijection of F_p (gcd(5, p - 1) = 1) with inverse x -> x^e5, e5 = 5^-1 mod (p - 1). With
K5 = (2^65 + c_0[2])^5, choose mu5 = -M[2][0] / M[2][1] and (A0, B0) solving M[t][0] A0 + M[t][1] B0 + M[t][2] K5 + c_1[t] = 0
for t = 0, 1 (the 2x2 minor of the MDS matrix is invertible). On the line A = T + A0, B = mu5 T + B0 the round-1 S-box
inputs are (s_0 T, s_1 T, kappa) with s_t = M[t][0] + M[t][1] mu5 (nonzero) and a constant kappa, so with W = T^5 the state
after round 1 is A1 + W B1 for constant vectors A1, B1 (all three entries of B1 nonzero; asserted by the program).
message(W) = (A^e5 - c_0[0], B^e5 - c_0[1]) with T = W^e5 is a pair of canonical field elements, and it is injective in W
(W determines T, which determines A and B, which determine the pair). The walk map, for a coin rho0, is

  F(x) = digest(message(x + rho0)) / OUTSCALE,

a map F_p -> F_p with a fixed nonzero OUTSCALE. If x != y and F(x) = F(y) then message(x + rho0) != message(y + rho0) are two
distinct canonical inputs with equal digests: an ordinary collision of the target. (This is the line of the published entries.)

## 2. The step program (508 field operations)

`step.py` (Appendix A) builds a straight-line program that computes F(x) from x with every lane held divided by a known
nonzero scale, and checks F(x) * OUTSCALE = digest(message(x + rho0)) against a direct implementation of the reduced
permutation (the round loop of the organizer's `verifier/poseidon.py`) at 8 random points for each of r = 1, 2, 7, 31, and,
when run inside the challenge repository, also against the organizer's `verifier/poseidon.py:digest` itself on the encoded
messages (32 of 32 digests equal; the output of that run is reproduced at the end of Appendix B).

- Entry (3 additions): t_i = x + K_i with K_i = rho0 + (A1_i + c_2[i]) / B1_i; the actual round-2 S-box input of lane i is
  B1_i t_i.
- Full round (24): y_i = t_i^5 (3 multiplications each), actual output B_i^5 y_i for the stored scale B_i. The next S-box input
  of lane i is sum_j M[i][j] B_j^5 y_j + c_next[i]; it is stored divided by its coefficient of y_0, so it costs 2
  multiplications and 3 additions (constant included) per lane: 9 + 15 = 24.
- Round 3 into the partial form (24): the S-boxes (9), lane 0 for round 4 as above (5), and the two passive lanes in a basis
  zeta (2 x 5, one coefficient 1 in each row).
- Partial round (12): y = t_0^5 (3 multiplications); next lane 0: t_0' = y + l_1 zeta_1 + l_2 zeta_2 + kappa (2 multiplications,
  3 additions); passive update zeta_i += g_i y (2 multiplications, 2 additions). With M = [[a, b^T], [e, D]], the passive lanes
  are z_r = P_r zeta + o_r with P_{r+1} = D P_r and o_{r+1} = D o_r + (round constants of the passive lanes), which makes the
  passive block the identity; lane 0 is rescaled by a M00 B^5 each round.
- Exit (0 operations): P_4 is chosen as D^-31 times a diagonal matrix and o_4 so that o_60 = 0; then the round-60 S-box inputs
  of lanes 1 and 2 are the stored zeta_1, zeta_2 with scales P_60 = diag(s).
- Rounds 60, 61, 62 (24 each); round 63 (13): the S-boxes (9) and only output lane 0, divided by its coefficient of y_0
  (2 multiplications, 2 additions); OUTSCALE is that coefficient.

Total 3 + 24 + 24 + 12 * 31 + 0 + 3 * 24 + 13 = 508 field operations: 205 additions and 303 multiplications, the published
count. The program uses 205 constants, three of which are the entry offsets K_i (they depend on rho0 and are formed once
per attempt by 3 additions). Lower-count variants were examined and none applies: each lane carries one free scale per round, which pays for
one unit coefficient per affine form, and every remaining coefficient and constant is a separate multiplication or addition.

## 3. The search algorithm (one attempt)

Parameters (Section 9 gives the values): Delta (the distinguished set D = {v in F_p : v < Delta}, density theta = Delta / p),
the walk budget n, the detection allowance d, the trail cap S = n + d, the table capacity MCAP, the recovery cap G, the gap
field width WG = 120 bits. The algorithm is given twice: `search.py` is a plain reference implementation, and `machine.py` emits
the instruction listing for the machine of Section 7 that the ledger of Section 9 counts. A counting interpreter
(`machine.run`) executes the full listing; `test_machine.py` runs it at reduced output width on the real step program and
checks, trial by trial, that it returns the same outcome and the same two messages as `search.py` on the same coins, that its
counted cost equals the path formula built from the listing's region costs, and that it is at most the worst-case ledger of
Section 9 at those parameters (results at the end of Appendix B). The test builds differ from the filed listing only by
one AND with the width mask after every step-program instance (and the MASKW constant) and by the shorter address chain to
their smaller constant memory; a stress run (`test_machine.py --stress`) forces every exit (table full, gap field, positioning
cap, lockstep cap, no repeat, success after hundreds of entries) and checks cost <= worst case and the path formula each time.

1. Coins. rho0 = the low 254 bits of one random 256-bit word; x_0 = the low 254 bits of a second word (both canonical). Form
   K_i = K_i(0) + rho0 (3 additions) and load the 205 program constants into registers. Store x_0 (the start word, index 0).
2. Trail. Blocks of 15 unrolled steps x_i = F(x_{i-1}), each followed by the distinguished test x_i < Delta (one comparison and
   branch), run while the block counter is below S, so S' = 15 ceil(S / 15) steps at most (S' is used in Section 5). On a distinguished point: scan the table (entries in
   index order: the value, ceil(log2 Delta) bits, and the gap to the previous stored index, WG bits, packed); if a stored
   value equals x_i, a repeat is detected at i2 = i with i1 = that entry's index (go to 3). Otherwise append (x_i, i - last) if
   the table holds fewer than MCAP entries and i - last < 2^WG; else stop (failure). After the last block, stop (failure).
3. Recovery. lambda = i2 - i1. a = the stored index immediately preceding i1 in the table (a = 0, the start word, if i1 is the
   first entry); A = x_a (its stored value). Let tb = a + lambda and b the largest stored index <= tb (b >= a); B = x_b,
   then apply F to B (tb - b) times; if tb - b > G + d - 1, stop (failure). Lockstep: at most G times, compute F(A) and F(B);
   if they are equal, output (A, B) if A != B (else failure); otherwise A, B <- F(A), F(B). If G iterations pass, stop (failure).
4. Output. The two messages message(A + rho0) and message(B + rho0).

Every loop has an explicit cap, so the operation count of Section 9 bounds every execution, successful or not.

## 4. Correctness on the good event

Let tau be the first index with x_tau in {x_0, ..., x_{tau-1}}, mu the index with x_tau = x_mu (the tail length) and
lambda* = tau - mu (the cycle length). For u >= mu, x_{u + lambda*} = x_u; the values x_0, ..., x_{tau-1} are distinct.

Good event: tau <= n; mu >= 1; lambda* >= d; some index in [mu, mu + d - 1] is distinguished; the trail stores at most MCAP
values before the detection; every stored gap is below 2^WG; mu - a <= G; and the positioning distance tb - b is at most
G + d - 1 (a, b as in step 3).

**Lemma 1 (correctness).** On the good event the algorithm outputs two distinct points with equal images under F.

Proof. Let i1* be the first distinguished index >= mu (i1* <= mu + d - 1 < tau since lambda* >= d). A distinguished value
can recur only at an index >= tau (earlier values are distinct); a tail value (index < mu) never recurs; the value at a
distinguished index j >= i1* recurs first at j + lambda* >= i1* + lambda*. Hence the first time the trail meets a stored value
is at i2 = i1* + lambda* <= tau + d - 1 <= n + d - 1 < S, with the stored entry of index i1 = i1*; the trail stores every
distinguished index below i2 (no overflow, no gap overflow). So lambda = lambda*. The stored indices below i1 are all below mu
(no distinguished index lies in [mu, i1)), so a < mu. For 0 <= t: F(x_{a+t}) = x_{a+t+1} and F(x_{a+lambda+t}) = x_{a+lambda+t+1};
these are equal exactly when a + t + 1 >= mu. The lockstep starts with A = x_a and B = x_tb, tb = a + lambda: B is reached
from the stored x_b by tb - b steps (b is the largest stored index <= tb). The first equality is at t = mu - a - 1 <= G - 1,
where A = x_{mu-1} and B = x_{mu-1+lambda}: two different indices below tau, hence distinct values, with the common image x_mu.
By Section 1 the two messages are distinct canonical inputs with equal digests. QED

## 5. The success bound for a uniformly random function

Throughout this section F is a uniformly random function F_p -> F_p, x_0 is fixed, N = p, S' = 15 ceil(S / 15) is the
largest number of trail steps, and theta_lo = (Delta - S') / N, theta_hi = Delta / (N - S').

**Lemma 2 (sequential structure).** Run the walk revealing F only at visited points. Let (u_1, u_2, ...) be a uniformly
random ordering of F_p \ {x_0}, and, independently, the shape decisions: at step i (values x_0..x_{i-1} distinct) "repeat"
with probability i/N, landing on an index uniform in {0, ..., i-1}, else "new". Setting x_i = u_i at new steps and x_i =
x_landing at the first repeat produces a sequence with the same law as the walk up to and including tau. Consequently
(tau, mu) is independent of (u_i), and given (tau, mu) the values x_1, ..., x_{tau-1} are a uniform sample without
replacement from F_p \ {x_0}.

Proof. Given x_0, ..., x_{i-1} distinct, F(x_{i-1}) is uniform on F_p and independent of everything revealed (F has not been
evaluated at x_{i-1}). In the construction, each earlier value is hit with probability (i/N)(1/i) = 1/N, and each unused value
with probability (1 - i/N) / (N - i) = 1/N. The two step laws agree for every history, so the processes agree in law. QED

**Corollary.** Let J be a set of indices in [1, tau - 1] chosen as a function of (tau, mu) and of the values at indices up to
some k < min J (k a stopping index of the sequence u, possibly depending on (tau, mu)). Then, conditionally on that
information, P(no index of J is distinguished) <= (1 - theta_lo)^|J| <= exp(-theta_lo |J|), and for every new index the
conditional probability of being distinguished is at most theta_hi.

Proof. Given (tau, mu) and u_1, ..., u_k, the values u_{k+1}, u_{k+2}, ... are a uniform ordering of the unused values. At most
S' values are used before any index of J is decided, so at least Delta - S distinguished values remain among at most N unused
ones, and at most Delta among at least N - S. Multiply the conditional probabilities in index order. QED

**Lemma 3 (failure bound).** The complement of the good event is contained in the union of:
- E1: tau > n. P(E1) = prod_{i=1}^{n} (1 - i/N) <= exp(-n(n + 1) / (2N)).
- E2: tau <= n and mu = 0. At each step the repeat lands on x_0 with probability 1/N: P(E2) <= n/N.
- E3: tau <= n and lambda* < d. At step i the repeat lands within the last d values with probability at most d/N: P(E3) <= n d / N.
- E4: tau <= n, lambda* >= d and no distinguished index in [mu, mu + d - 1]. J = [mu, mu + d - 1] lies below tau <= n <= S'
  and depends on (tau, mu) only: P(E4) <= exp(-theta_lo d).
- E5: more than MCAP distinguished values among the stored ones. Each new value is distinguished with conditional probability
  at most theta_hi, so the count over at most S' new values is stochastically dominated by Binomial(S', theta_hi):
  P(E5) <= exp(-m) (e m / (MCAP + 1))^(MCAP + 1) with m = S' theta_hi (Chernoff, valid since MCAP + 1 > m).
- E5b: a stored gap of at least 2^WG. The stored gaps lie between distinguished indices below tau (Lemma 1's proof), so such a gap
  means 2^WG - 1 consecutive non-distinguished indices below tau; each of at most S' windows has that property with probability at
  most exp(-theta_lo (2^WG - 1)): P(E5b) <= S' exp(-theta_lo (2^WG - 1)).
- E6: tau <= n and mu - a > G. Then mu > G and no index in [mu - G, mu - 1] is distinguished (otherwise a >= mu - G); J lies
  below tau and depends on (tau, mu) only: P(E6) <= exp(-theta_lo G).
- E7: tau <= n and tb - b > G + d - 1 while E3, E4, E6 fail. Let J = [tb - (G + d - 1) + 1, tb]. If tb >= i1, then b >= i1
  and E7 implies the event "min J > i1 and no index of J is distinguished"; J is a function of (tau, mu) and of the values up
  to the stopping index i1 (which fix a and i1), and on "min J > i1" it lies in (i1, tau) (tb = a + lambda < mu + lambda = tau),
  so by the Corollary this event has probability at most exp(-theta_lo (G + d - 1)). If tb < i1 then b = a and the distance is
  lambda < i1 - a = (mu - a) + (i1 - mu) <= G + d - 1 (no E6, no E4), so E7 does not occur. P(E7) <= exp(-theta_lo (G + d - 1)).

Hence P(success) >= 1 - [P(E1) + ... + P(E7)] for the random function, for every fixed x_0.

E6 and E7 are the only places where the recovery cap enters. Previous constructions bounded every gap of the trail
((S theta + 1) exp(-theta gmax)); the recovery walks only the gap that contains mu and the back-gap at tb, and Lemma 2 gives
each of them the tail bound of a single gap. That is lever (i).

## 6. Premise H1 and its evidence

**H1 (score-critical).** For the fixed r = 31 walk map family F_rho0 of Section 1, with rho0 and x_0 drawn as in Section 3,
the algorithm of Section 3 at the parameters of Section 9 succeeds with probability at least 0.39.

Scope: the target poseidon-orchard-r31-prefix-v1, this line, these parameters. Extrapolation: from the random-function
bound of Section 5 (0.3900024127182048512159623481164369397980347275362) to the fixed map; the bound exceeds 0.39 by 2.41e-06, so H1 needs the fixed map's search to
reach at least 1 - 6.186e-06 of the random-function success, i.e. a relative collision-rate deficit below about
6.2e-06 (Section 9 states the cost of absorbing larger deficits). Limitations: the measurements below are at output
widths 16 to 32 bits; their standard errors are a few percent, so they exclude gross departures from the random-function
rate but cannot resolve a deficit anywhere near the level the filed budget tolerates (the budget is the least one that
reaches 0.39 for a random function plus a relative 4e-6, so it carries almost no robustness margin, like the published
entries'); the premise is the
same kind of premise as the published entries' H1; it is not a property proved here.

Declared experiments for the organizer runs (one program, `experiments/r31_listing.py`, generated by
`mk_experiment.py` from `step.py`, `machine.py`, `search.py` and `campaign.py` with the round constants embedded):
- `r31-search-w14` (bears on H1): the search of Section 3 (`search.py`, unchanged) on the real r = 31 map with the walk on the
  low 14 bits of the digest (F_14(x) = digest(message(x + rho0)) mod 2^14; coins from each organizer seed), with its parameters
  chosen in advance by Lemma 3 at N = 2^14 for success 0.39: Delta = 6144 (theta = 0.375), n = 171, d = 16, G = 16, S = 187,
  MCAP = 96, WG = 28. Stated before the run: Lemma 3 gives success at least 0.39043 for a uniformly random function at these
  parameters, so under the random-function model the organizer's success count over 256 seeds is at least Binomial(256, 0.39043)
  in distribution; a count below 80 would be evidence against the model at the 0.5% level. A success is two distinct canonical
  messages whose digests agree on the low 14 bits (event digest-xor-mask, recomputed by the organizer); it is a mask event, not a
  collision. For `search.py`, which does not unroll, the trail cap is S' = S = 187; Lemma 3 at these parameters, with S' = 187,
  gives 0.3954, and the pre-stated 0.39043 is the more conservative value of `sim.bound` (Chernoff at MCAP instead of MCAP + 1,
  positioning cap G + d instead of G + d - 1). This experiment and `r31-listing-w10` walk on the digest mod 2^w, while the
  supplementary runs below (`campaign.py`, `sim.py`) walk on digest / OUTSCALE mod 2^w: two different reduced maps of the same
  walk. Pre-run (local, seeds = SHA-256("prerun r31-search-w14 <trial>"), `prerun.py` of Appendix A): 161 of 256 trials returned verified mask events (0.629; the stated lower bound is 0.39043, the 0.5% threshold 80), the other 95 returned no pair.
- `r31-listing-w10` (bears on H2): the complete instruction listing of `machine.py` executed by the counting interpreter on the
  real step program, walk on the low 10 bits of the digest (one MUL by OUTSCALE and one AND per step instance added), small fixed
  control-flow parameters (Delta = 128, S = 60, MCAP = 32, G = 40, positioning cap 60, DP value field 7 bits, gap field 20 bits,
  so the packing paths differ in field widths from the filed 142 and 120 bits) that are not chosen by Lemma 3; it checks
  that the counted listing runs end to end on the target. Pre-run (local, same seeds): 139 verified mask events, 110 no repeat within the budget, 7 start on the cycle (of 256), each counted cost at most the worst case of the listing.

Supplementary results we ran ourselves (not organizer-executed; programs in Appendix A, seeds stated in the programs):
- Collision-rate campaign (`campaign.py`): the real walk map F_rho0 truncated to w bits, w in {16, 20, 24, 28, 32}, a fresh
  rho0 and start per walk from SHA-256 of the label "poseidon_mage r31 h1 v1 <w> <walk>", run to the first repeat. For a
  random function the statistic X = tau(tau - 1)/(2 2^w) has an exactly computable mean E0 (computed by `render_round.py`); the hazard
  multiplier estimate is c = E0 / mean(X). Results with a keyed SHA-256 control run from the same starts:

| w | walks | E0 | c (real map) | c (SHA-256 control) |
|---:|---:|---:|---:|---:|
| 16 | 800 | 0.99511 | 1.0222 (+- 0.0361) | 0.9970 |
| 20 | 400 | 0.99878 | 0.9486 (+- 0.0474) | 1.0158 |
| 24 | 200 | 0.99969 | 0.9580 (+- 0.0677) | 1.0099 |
| 28 | 60 | 0.99992 | 1.0135 (+- 0.1308) | 1.1422 |
| 32 | 20 | 0.99998 | 0.7443 (+- 0.1664) | 0.9214 |
| pooled | 1480 | | 0.9872 (+- 0.0260) | 1.0079 |

- Reduced-width searches (`sim.py`): the search of Section 3 (`search.py`, unchanged) on the real map truncated to w bits and on
  the SHA-256 control (gap field width scaled to WG = 40), with parameters chosen by Lemma 3 at N = 2^w for success 0.39:

| w | MCAP | Delta | n | d | G | Lemma 3 bound | trials | success real | success control | max lockstep (cap G) | max positioning (cap G+d-1) | failure codes |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 24 | 1500 | 5222400 | 4126 | 20 | 23 | 0.39005 | 300 | 0.3667 | 0.3933 | 16 | 14 | {'no-repeat': 371, 'ok': 228, 'start-on-cycle': 1} |
| 28 | 3000 | 44236800 | 16427 | 43 | 40 | 0.39017 | 100 | 0.3600 | 0.4100 | 26 | 24 | {'ok': 77, 'no-repeat': 123} |

  The failure-code column pools the real-map and control trials; every failure was a halt with no repeat within the budget
  (E1-type), and every returned pair was checked to collide under the truncated map, with the recovery lengths within the caps of
  Section 3 (lockstep at most G, positioning at most G + d - 1).

## 7. Machine convention H2 and prices

**H2 (score-critical, cost convention).** The search is the instruction listing emitted by `machine.py` for a register machine
with a declared file of 344 registers of 256 bits (every register the listing names), counted in memory (Section 8), and
32-bit instructions (5-bit opcode, three 9-bit fields), counted in memory. Prices per executed instruction:
ADD, SUB, MUL (Pallas field operations with canonical results) 1; IADD, ISUB, IADDI (integer, modulo 2^256) 1; MOV (register
move) 1; AND, OR, SHRV, SHLV (shift by a register amount) 1; LD and ST 2 (the access and one address operation); BLT, BEQ, BNE
(compare and branch to an address held in a register) 2; JMP 1; RAND (one random 256-bit word) 1; HALT 1. A shift by an amount
of 256 or more returns 0 (the packed-table code relies on it when an entry starts on a word boundary). Instruction fetch is
not charged. Jump targets and all constants are loaded into registers at setup by charged LD instructions. The step program is
508 field operations on registers (its 205 constants and 6 scratch registers, allocated by liveness), so a trail step
costs 508 + 2 (the distinguished test). Limitations: the contract fixes no register count; a file too small for the 205
constants would force about 205 loads per step, adding log2(1 + 410/510) = 0.85 bits; charging instruction fetch at one unit per
instruction would add about one bit. The published entries use the same kind of convention (declared register files, no fetch charge); the dependency
43caeb6a declares 469 registers at r = 56, our in-review 9f8717f0 223 at r = 23.

## 8. Memory

| region | bytes |
|---|---:|
| table: DP values 30250 x 142 bits + gaps 30250 x 120 bits, packed, + 1 spare word (30961 words) | 990,752 |
| start word x_0 | 32 |
| program: 9063 instructions x 4 bytes (5-bit opcode, three 9-bit fields) | 36,252 |
| constant memory: 293 words (205 step constants incl. the 3 entry offsets, parameters, masks, jump targets) | 9,376 |
| register file: 344 registers of 256 bits (every register the listing names) | 11,008 |
| slack to 2^20 | 1,156 |
| **total (excluding slack)** | **1,047,420** |

Total 1,047,420 bytes, slack 1,156 bytes below 2^20 (the slack also holds the program counter and the halt code);
log2 = 19.998408627; submitted as `memory_log2_bytes` = 20.00000, i.e. the whole mebibyte, so the declared bound is above the
counted bytes with room to spare and the normalized cost is unchanged (max(0, 20 - 20) = 0). The
two output messages and the report reuse the table storage after the recovery, so they do not raise the peak.

## 9. Parameters, success bound and ledger

Parameters (from the grid search `search_params.py`, which selects for each grid point the least n with bound >= 0.39 by
`cert.minimal_n`; the filed n adds a relative 4e-6 to that least value):

| parameter | value |
|---|---:|
| Delta (D = {v < Delta}) | 4955463538568564343182868956103890945703936 (2^141.830000) |
| theta = Delta / p | 2^-112.170000 |
| n (walk budget) | 169297055886635591747237776317843690204 (2^126.992824) |
| d (detection allowance) | 55495557539318368702682515302776833 |
| S = n + d (trail cap) | 169352551444174910115940458833146467037 |
| G (recovery cap) | 56955966948247799215295948946145281 |
| MCAP (table capacity) | 30250 |
| DP value field | 142 bits |
| gap field WG | 120 bits |
| unrolling | 15 steps per block |

Failure terms of Lemma 3 at these parameters (each rounded upward):

| event | bound |
|---|---:|
| no repeat within n steps | 6.095398e-01 |
| start on the cycle (mu = 0) | 5.848312e-39 |
| cycle shorter than d | 3.245553e-04 |
| no DP in the first d cycle values | 7.487614e-05 |
| lockstep cap: mu - a > G | 5.831409e-05 |
| positioning cap: back-gap > G + d - 1 | 4.366334e-09 |
| table overflow (more than MCAP DPs) | 1.860382e-12 |
| gap field width: a DP gap >= 2^WG | 1.693526e-47 |

Success lower bound for a uniformly random function: 0.3900024127182048512159623481164369397980347275362 (90-digit Decimal arithmetic with every exponential rounded up);
the least budget that reaches 0.39 at these parameters is n0 = 169296378701120787264088719962963838349 (search_params.py), and the filed n = n0 + floor(4e-6 n0)
leaves a margin of 2.413e-06 above 0.39, large enough to be checked from the printed terms (the cost of the extra steps is
4e-6 relative, below the five-decimal ceiling of the time claim).

Ledger (primitive operations, every cap charged; Section 7 prices):

| row | operations |
|---|---:|
| setup (constants, table zeroing, coins) | 155,759 |
| trail: 11290170096278327341062697255543097803 blocks x 7653 | 86,403,671,746,818,039,141,152,822,096,671,327,486,360 |
| DP handler: 30250 insertions (stub, preamble, scan of c = 0..MCAP-1 entries, insert) | 15,557,121,250 |
| last DP call: scan of MCAP entries, then the larger of overflow and recovery (second scan, positioning cap, lockstep cap, output) | 116,578,641,477,200,739,100,026,349,936,369,964,568 |
| preprocessing: derivation of the program constants (< 2^24 operations), charged at an over-bound of 2^48 | 281,474,976,710,656 |
| **total W** | **86,520,250,388,295,239,880,252,848,728,098,231,438,593** |

Every row is the static cost of a region of the listing (label to label, Appendix A `machine.region_costs`) times its
worst-case number of executions: the trail runs ceil(S / 15) blocks of 15 x (508 + 2) + 3 operations; at most MCAP insertions,
the c-th scanning c entries (per entry 34 operations: two field extractions of 12 operations each, two loads with their
address operations, shifts and masks, the index addition, the value comparison, two moves, three pointer and counter updates
and the loop branch); the last call scans MCAP entries and then pays the larger of the overflow exit and the whole recovery
(second scan of at most MCAP entries at 34 each, at most G + d - 1 positioning iterations at 514 each, at most G
lockstep iterations at 1032 each, and the output: 11,462 operations for the six fifth-root ladders, the affine maps
and the four stores of the two messages). The insertion path (40 operations) packs the value and the gap with two
read-modify-writes of two words each. The setup loads every constant, zeroes the table and draws the coins.

Total W = 86,520,250,388,295,239,880,252,848,728,098,231,438,593 operations. T = W / 867; log2 T = 126.230273453, submitted as `time_log2` = 126.23028 (ceiling at five decimals;
W^100000 <= 2^12623028 * 867^100000 checked in exact integer arithmetic by `cert.py`).

Declared bounds against the true values: time as above; memory as in Section 8; success probability 0.39 <= 0.3900024127182048512159623481164369397980347275362 under
H1; preprocessing: the only work done before an attempt is the derivation of the program constants (the 205 step constants
and the line constants by `step.build`, Appendix A: matrix powers D^(+-31) and the passive basis, three fifth powers, a few dozen
field inversions; below 2^24 operations, a bound rather than a counted listing). It is charged in W at an over-bound of 2^48
operations and declared as `preprocessing_log2` = 38.24012 >= log2(2^48 / 867) = 38.24011. Preprocessing memory: the derivation
runs before the setup zeroes the table, inside the 990,752-byte table region: its data are the 192 round constants and the 9 MDS
entries (201 words), the derived constants and the line constants (about 360 words) and 2 x 2 matrix workspaces (under 64
words), about 20 KB, and its code, written as a loop program for the machine of Section 7, needs at most 4,096 instructions
(16 KB, a bound) in the same region; the derived constants are then stored in the constant memory of Section 8. The
preprocessing peak is therefore below the online peak of 1,047,420 bytes. The parameters (Delta, n, d, G, MCAP, the
unrolling) are constants of the algorithm's description. The computations that chose them (`plan.py`, `search_params.py`) and
that check this document (`cert.py`, `render_round.py`, including the exact 100000-th powers of `cert.py`) are design and verification work: they
are neither steps of the algorithm nor preprocessing, and no time or memory is claimed for them.

Sensitivity: each extra operation per step adds about log2(1 + 1/510) = 0.0028 bits; absorbing a 1% collision-rate deficit
in H1 needs about +0.00725 bits of budget.

## Appendix A. Programs

Standard library only (python 3). `python step.py 1 2 7 31` builds and verifies the step program (also against the
organizer `verifier/poseidon.py` when run inside the challenge repository); `python cert.py` prints the
certificate (parameters, failure terms, ledger, memory); `python search_params.py` re-runs the parameter grid;
`python render_round.py <dir>` assembles this package and asserts the declared bounds; `test_machine.py` cross-checks
the listing against `search.py` trial by trial; `campaign.py` and `sim.py` produce the evidence of Section 6 (`sim.py`
also needs `search.py`); `prerun.py` pre-runs both declared experiments locally; `mk_experiment.py` writes the
organizer experiment. The step program checks itself against a direct implementation of the reduced permutation.

### step.py

```python
"""step.py - the equivalent straight-line step program for the r-partial-round Orchard hash on the two-round line.

Walk map: F(x) = digest(message(x + rho0)) / OUTSCALE. On the line (round-0 S-box outputs (A, B) = (T + A0, mu5 T + B0),
k = 2 the constant lane of the round-1 S-box input), with W = T^5 the state after round 1 is A1 + W B1. The program
computes F(x) from x with lanes held divided by known scales:

  enter        t_i = x + K_i                                   (3 additions; K_i = rho0 + (A1_i + c2_i)/B1_i per attempt)
  full round   y_i = t_i^5 (9 mul); t'_i = y_{j_i} + k_i1 y_. + k_i2 y_. + kappa_i   (per lane 2 mul + 3 add) = 24
  last full    only lane 0: y0..y2 (9 mul), out = y0 + k1 y1 + k2 y2 (2 mul + 2 add) = 13
  into partial (after the last full round before the partial rounds): lane 0 as a full-round lane (5), the passive
               lanes in the basis zeta = Q y + q (2 rows, one coefficient 1 each: 2 x 5)
  partial      y = t0^5 (3 mul); t0' = y + l1 z1 + l2 z2 + kappa (2 mul + 3 add); z_i += g_i y (2 mul + 2 add) = 12
  out of partial: with the passive basis P_60 diagonal and the offset absorbed, t1 = z1, t2 = z2 (0 operations)
Total for r partial rounds: 3 + 24 (round 2) + 24 (round 3, into partial form) + 12 r + 0 + 3 * 24 (rounds 60-62)
+ 13 (round 63) = 136 + 12 r; r = 31: 508 field operations.

Program format: list of (op, dst, a, b) with op in {'add', 'mul'}; operands are register names; constants live in
registers 'k<i>' (loaded once per attempt). build(r, consts, rho0) returns (program, constant table, OUTSCALE) and
verify() checks F(x) * OUTSCALE == digest(message(x + rho0)) against the reference permutation.
"""
import json, os, sys
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
inv = lambda x: pow(x % P, P - 2, P)
E5 = pow(5, -1, P - 1)
HERE = os.path.dirname(os.path.abspath(__file__))
CPATH = os.path.join(HERE, '..', '..', 'pareto', 'orchard-pallas-constants.json')


def load():
    C = json.load(open(CPATH))
    RC = [[int(x, 16) for x in row] for row in C['round_constants']]
    M = [[int(x, 16) for x in row] for row in C['mds']]
    return RC, M


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) % P for j in range(len(B[0]))] for i in range(len(A))]


def matinv2(A):
    d = (A[0][0] * A[1][1] - A[0][1] * A[1][0]) % P
    di = inv(d)
    return [[A[1][1] * di % P, -A[0][1] * di % P], [-A[1][0] * di % P, A[0][0] * di % P]]


class Line:
    """the two-round line (lane k = 2 constant at the round-1 S-box input)."""
    def __init__(self, RC, M, r):
        self.RC, self.M, self.r = RC, M, r
        CAP = 1 << 65; self.CAP = CAP
        k = 2
        K5 = pow((CAP + RC[0][2]) % P, 5, P)
        i, j = 0, 1
        mu5 = (-M[k][0] * inv(M[k][1])) % P
        a, b, e = M[i][0], M[i][1], (-(M[i][2] * K5 + RC[1][i])) % P
        c, d, f = M[j][0], M[j][1], (-(M[j][2] * K5 + RC[1][j])) % P
        det = (a * d - b * c) % P; di = inv(det)
        A0 = ((e * d - b * f) * di) % P; B0 = ((a * f - e * c) * di) % P
        self.mu5, self.A0, self.B0 = mu5, A0, B0
        slope = [(M[t][0] + M[t][1] * mu5) % P for t in range(3)]
        constk = (M[k][0] * A0 + M[k][1] * B0 + M[k][2] * K5 + RC[1][k]) % P
        assert slope[k] == 0 and slope[0] and slope[1]
        sb_lin = [pow(slope[t], 5, P) if t != k else 0 for t in range(3)]
        sb_const = [pow(constk, 5, P) if t == k else 0 for t in range(3)]
        self.A1 = [sum(M[row][col] * sb_const[col] for col in range(3)) % P for row in range(3)]
        self.B1 = [sum(M[row][col] * sb_lin[col] for col in range(3)) % P for row in range(3)]
        assert all(self.B1)

    def message(self, W):
        T = pow(W, E5, P)
        A = (T + self.A0) % P; B = (self.mu5 * T + self.B0) % P
        return (pow(A, E5, P) - self.RC[0][0]) % P, (pow(B, E5, P) - self.RC[0][1]) % P

    def digest(self, m0, m1):
        s = [m0, m1, self.CAP]
        for idx in (*range(4), *range(4, 4 + self.r), *range(60, 64)):
            s = [(x + c) % P for x, c in zip(s, self.RC[idx])]
            for col in (range(3) if idx < 4 or idx >= 60 else range(1)):
                s[col] = pow(s[col], 5, P)
            s = [sum(c * x for c, x in zip(row, s)) % P for row in self.M]
        return s[0]


def build(r, rho0=None):
    RC, M = load()
    L = Line(RC, M, r)
    prog = []          # (op, dst, a, b)
    consts = {}        # name -> value (loaded once per attempt)
    cnt = [0]

    def K(v):
        name = 'k%d' % len(consts)
        consts[name] = v % P
        return name

    def op(o, d, a, b):
        prog.append((o, d, a, b))

    def pow5(src, dst):
        op('mul', dst + 's', src, src); op('mul', dst + 'q', dst + 's', dst + 's'); op('mul', dst, dst + 'q', src)

    # enter: actual round-2 S-box input u_i = A1_i + c2_i + W B1_i = B1_i (W + K_i), W = x + rho0
    beta = list(L.B1)
    kin = [(L.A1[i] + RC[2][i]) * inv(L.B1[i]) % P for i in range(3)]
    rho0 = rho0 or 0
    for i in range(3):
        op('add', 't%d' % i, 'x', K(kin[i] + rho0))
    # helper: one full round from stored t (actual = beta * t) to next S-box inputs (with constants of round nxt)
    def full_round(beta, nxt_const):
        for i in range(3):
            pow5('t%d' % i, 'y%d' % i)
        sc = [pow(b, 5, P) for b in beta]                       # actual y_i = sc_i * y_i
        coef = [[M[i][j] * sc[j] % P for j in range(3)] for i in range(3)]
        newbeta = []
        for i in range(3):
            j0 = 0
            nb = coef[i][j0]; newbeta.append(nb); ni = inv(nb)
            ks = [coef[i][j] * ni % P for j in range(3)]
            kap = nxt_const[i] * ni % P
            op('mul', 'm%da' % i, 'y1', K(ks[1])); op('mul', 'm%db' % i, 'y2', K(ks[2]))
            op('add', 'm%dc' % i, 'y0', 'm%da' % i); op('add', 'm%dd' % i, 'm%dc' % i, 'm%db' % i)
            op('add', 'n%d' % i, 'm%dd' % i, K(kap))
        for i in range(3):
            op('add', 't%d' % i, 'n%d' % i, 'ZERO') if False else None
        # rename n_i -> t_i (register renaming is free: emit as aliases)
        prog.append(('alias', None, None, None))
        return newbeta, coef
    # round 2 (full) -> constants of round 3
    beta, _ = full_round(beta, RC[3])
    # round 3 (full) into partial form (round 4 constants) -- or, if r == 0, into round 60
    if r == 0:
        beta, _ = full_round(beta, RC[60])
        rounds_tail = [60, 61, 62]
    else:
        # round 3: S-box, then MDS; lane 0 -> t0 scaled with constant c4_0; passive lanes -> zeta basis
        for i in range(3):
            pow5('t%d' % i, 'y%d' % i)
        sc = [pow(b, 5, P) for b in beta]
        coef = [[M[i][j] * sc[j] % P for j in range(3)] for i in range(3)]   # out = coef * y
        # partial-round sparse form: M = [[a, b^T],[e, D]]
        a_ = M[0][0]; bvec = [M[0][1], M[0][2]]; evec = [M[1][0], M[2][0]]; Dm = [[M[1][1], M[1][2]], [M[2][1], M[2][2]]]
        # passive basis: z_r = P_r zeta + o_r, P_{r+1} = D P_r; P_60 diagonal => P_4 = D^-(r) diag(s)
        Dinv = matinv2(Dm)
        Dn = [[1, 0], [0, 1]]
        for _ in range(r):
            Dn = matmul(Dn, Dinv)                               # D^-r
        # zeta at round 4: zeta = P_4^-1 (z_4 - o_4), z_4 = coef[1:3] y + c4[1:3]; P_4 = D^-r S, S = diag(s1, s2)
        # => zeta = S^-1 D^r (coef[1:3] y + c4[1:3] - o_4); choose s_i to normalise the first coefficient of row i
        Dr = [[1, 0], [0, 1]]
        for _ in range(r):
            Dr = matmul(Dr, Dm)
        rows = matmul(Dr, [coef[1], coef[2]])                   # 2 x 3
        s = [rows[0][0], rows[1][0]]
        P4 = matmul(Dn, [[s[0], 0], [0, s[1]]])
        # offsets: choose o_4 so that o_60 (the offset at the exit) is zero: o_{r+1} = D o_r + c_{r+1}[1:3]
        # o_60 = D^r o_4 + sum_{j} D^(r-1-j) c_{5+j}[1:3]  (constants of rounds 5..59 and 60) = 0
        acc = [0, 0]
        for rr in range(5, 4 + r):                              # constants added at rounds 5..3+r (passive lanes)
            acc = [(Dm[0][0] * acc[0] + Dm[0][1] * acc[1] + RC[rr][1]) % P, (Dm[1][0] * acc[0] + Dm[1][1] * acc[1] + RC[rr][2]) % P]
        acc = [(Dm[0][0] * acc[0] + Dm[0][1] * acc[1] + RC[60][1]) % P, (Dm[1][0] * acc[0] + Dm[1][1] * acc[1] + RC[60][2]) % P]
        # D^r o_4 + acc = 0 => o_4 = -D^-r acc
        o4 = [(-(Dn[0][0] * acc[0] + Dn[0][1] * acc[1])) % P, (-(Dn[1][0] * acc[0] + Dn[1][1] * acc[1])) % P]
        P4inv = matinv2(P4)
        # zeta = P4inv (coef[1:3] y + c4[1:3] - o4)
        zrow = matmul(P4inv, [coef[1], coef[2]])
        zc = [(P4inv[i][0] * (RC[4][1] - o4[0]) + P4inv[i][1] * (RC[4][2] - o4[1])) % P for i in range(2)]
        for i in range(2):
            assert zrow[i][0] == 1
            op('mul', 'z%da' % i, 'y1', K(zrow[i][1])); op('mul', 'z%db' % i, 'y2', K(zrow[i][2]))
            op('add', 'z%dc' % i, 'y0', 'z%da' % i); op('add', 'z%dd' % i, 'z%dc' % i, 'z%db' % i)
            op('add', 'z%d' % (i + 1), 'z%dd' % i, K(zc[i]))
        # lane 0 for round 4: actual S-box input = coef[0] y + c4_0 = b0 * t0, b0 = coef[0][0]
        b0 = coef[0][0]; ni = inv(b0)
        op('mul', 'm0a', 'y1', K(coef[0][1] * ni)); op('mul', 'm0b', 'y2', K(coef[0][2] * ni))
        op('add', 'm0c', 'y0', 'm0a'); op('add', 'm0d', 'm0c', 'm0b'); op('add', 't0', 'm0d', K(RC[4][0] * ni))
        Pr = P4; o = o4; bcur = b0
        for rr in range(4, 4 + r):
            # actual lane0 S-box input = bcur * t0; y = t0^5 (actual sc * y)
            pow5('t0', 'y')
            scv = pow(bcur, 5, P)
            # next lane 0: a sc y + b^T (Pr zeta + o) + c_{next,0}
            nxt = RC[rr + 1] if rr + 1 < 4 + r else RC[60]
            ell = [(bvec[0] * Pr[0][j] + bvec[1] * Pr[1][j]) % P for j in range(2)]
            const0 = (bvec[0] * o[0] + bvec[1] * o[1] + nxt[0]) % P
            nb = a_ * scv % P; ni = inv(nb)
            op('mul', 'pa', 'z1', K(ell[0] * ni)); op('mul', 'pb', 'z2', K(ell[1] * ni))
            op('add', 'pc', 'y', 'pa'); op('add', 'pd', 'pc', 'pb'); op('add', 't0', 'pd', K(const0 * ni))
            # passive update: zeta += P_{r+1}^-1 e sc y
            Pn = matmul(Dm, Pr)
            g = matmul(matinv2(Pn), [[evec[0] * scv % P], [evec[1] * scv % P]])
            op('mul', 'qa', 'y', K(g[0][0])); op('mul', 'qb', 'y', K(g[1][0]))
            op('add', 'z1', 'z1', 'qa'); op('add', 'z2', 'z2', 'qb')
            o = [(Dm[0][0] * o[0] + Dm[0][1] * o[1] + nxt[1]) % P, (Dm[1][0] * o[0] + Dm[1][1] * o[1] + nxt[2]) % P]
            Pr = Pn; bcur = nb
        # exit: z_60 = Pr zeta + o with Pr = diag(s), o = 0 => actual round-60 S-box inputs lanes 1,2 = s_i zeta_i
        assert Pr[0][1] == 0 and Pr[1][0] == 0 and o == [0, 0], (Pr, o)
        prog.append(('rename', 't1', 'z1', None)); prog.append(('rename', 't2', 'z2', None))
        beta = [bcur, Pr[0][0], Pr[1][1]]
        rounds_tail = [60, 61, 62]
    for rr in rounds_tail:
        beta, _ = full_round(beta, RC[rr + 1])
    # round 63: only lane 0
    for i in range(3):
        pow5('t%d' % i, 'y%d' % i)
    sc = [pow(b, 5, P) for b in beta]
    coef0 = [M[0][j] * sc[j] % P for j in range(3)]
    outscale = coef0[0]; ni = inv(outscale)
    op('mul', 'oa', 'y1', K(coef0[1] * ni)); op('mul', 'ob', 'y2', K(coef0[2] * ni))
    op('add', 'oc', 'y0', 'oa'); op('add', 'out', 'oc', 'ob')
    return L, prog, consts, outscale


def run(prog, consts, x):
    """execute the program; aliases: full_round writes n_i which become t_i at the 'alias' marker."""
    reg = dict(consts); reg['x'] = x
    for o, d, a, b in prog:
        if o == 'mul':
            reg[d] = reg[a] * reg[b] % P
        elif o == 'add':
            reg[d] = (reg[a] + reg[b]) % P
        elif o == 'alias':
            for i in range(3):
                reg['t%d' % i] = reg['n%d' % i]
        elif o == 'rename':
            reg[d] = reg[a]
    return reg['out']


def count(prog):
    n_add = sum(1 for p in prog if p[0] == 'add'); n_mul = sum(1 for p in prog if p[0] == 'mul')
    return n_add, n_mul


try:
    sys.path.insert(0, os.path.join(HERE, '..', '..'))
    from verifier.poseidon import digest as ODIGEST
except Exception:
    ODIGEST = None
checked = [0]


def verify(r, trials=8, rho0=12345):
    import random
    L, prog, consts, outscale = build(r, rho0)
    rnd = random.Random(r)
    for _ in range(trials):
        x = rnd.randrange(P)
        W = (x + rho0) % P
        m = L.message(W)
        ref = L.digest(*m)
        got = run(prog, consts, x)
        assert got * outscale % P == ref, (r, x)
        if ODIGEST is not None:                       # the organizer's verifier, when run inside the repository
            msg = m[0].to_bytes(32, 'little') + m[1].to_bytes(32, 'little')
            assert ODIGEST(msg, r) == (got * outscale % P).to_bytes(32, 'little')
            checked[0] += 1
    a, mm = count(prog)
    return a, mm, len(consts)


if __name__ == '__main__':
    for r in [int(v) for v in sys.argv[1:]] or [1, 2, 7, 31]:
        a, m, nc = verify(r)
        print(f'r={r}: step program {a + m} field operations ({a} additions, {m} multiplications); 136 + 12 r = {136 + 12 * r}; {nc} constants; '
              f'verified against the reference permutation at 8 points' + (f' and against verifier/poseidon.py ({checked[0]} digests so far)' if ODIGEST else ''))
```

### machine.py

```python
"""machine.py - the r = 31 search as an instruction listing for a declared register machine, with a counting interpreter.

Machine (proof Section 7, H2): registers R[0..511] of 256 bits, word memory MEM, 32-bit instructions
(5-bit opcode, three 9-bit fields). Costs per executed instruction:
  ADD SUB MUL (field, canonical result)            1      IADD ISUB (integer, mod 2^256)      1
  IADDI d,a,imm9                                   1      MOV d,a                             1
  AND OR d,a,b                                     1      SHRV SHLV d,a,b (shift by R[b])     1
  LD d,a  (d = MEM[R[a]])                          2      ST a,b  (MEM[R[a]] = R[b])          2
  BLT BEQ BNE a,b,t (compare, branch to R[t])      2      JMP t (to R[t])                     1
  RAND d (one random 256-bit word)                 1      HALT code                           1
Jump targets are held in registers (loaded at setup from constant memory). build_program() emits the listing for the
search of proof Section 3 with the real step program (step.py); run() executes it and counts every instruction.
For reduced-width tests (trunc=w), one AND X, X, MASKW follows every step-program instance (test builds only).
"""
import math
from step import build as build_step, P

OPS = {'ADD': 1, 'SUB': 1, 'MUL': 1, 'IADD': 1, 'ISUB': 1, 'IADDI': 1, 'MOV': 1, 'AND': 1, 'OR': 1, 'SHRV': 1, 'SHLV': 1,
       'LD': 2, 'ST': 2, 'BLT': 2, 'BEQ': 2, 'BNE': 2, 'JMP': 1, 'RAND': 1, 'HALT': 1}
M256 = (1 << 256) - 1
E5 = pow(5, -1, P - 1)


class Gen:
    def __init__(self):
        self.code = []          # (op, a, b, c)
        self.labels = {}
        self.regs = {}
        self.consts = []        # (register, value or ('label', name))

    def reg(self, name):
        if name not in self.regs:
            self.regs[name] = len(self.regs)
            assert len(self.regs) <= 512, 'register file exhausted'
        return self.regs[name]

    def emit(self, op, a=0, b=0, c=0):
        self.code.append([op, a, b, c])

    def label(self, name):
        self.labels[name] = len(self.code)

    def target(self, name):
        """register holding the address of label name (loaded at setup)."""
        r = self.reg('T:' + name)
        if ('label', name) not in [v for _, v in self.consts if isinstance(v, tuple)]:
            self.consts.append((r, ('label', name)))
        return r

    def const(self, name, value):
        r = self.reg(name)
        self.consts.append((r, value))
        return r


def build_program(Delta, S, MCAP, G, GPOS, VB, WG, K=15, trunc=None, r=31, rho_bits=254, digest_trunc=False):
    """two passes: the first collects every jump target, the second registers them before the constant-loading code."""
    first = _build(Delta, S, MCAP, G, GPOS, VB, WG, K, trunc, r, rho_bits, [], digest_trunc)
    targets = [nm for nm in first['target_names']]
    return _build(Delta, S, MCAP, G, GPOS, VB, WG, K, trunc, r, rho_bits, targets, digest_trunc)


def _build(Delta, S, MCAP, G, GPOS, VB, WG, K, trunc, r, rho_bits, pre_targets, digest_trunc=False):
    g = Gen()
    L, prog, consts, outscale = build_step(r, 0)
    # step-program registers: constants k<i> first (registers 0..329), then the step's own names
    for i in range(len(consts)):
        g.const('k%d' % i, consts['k%d' % i])
    X = g.reg('X')
    # register allocation of the step program: SSA values, freed at their last use, physical scratch registers reused
    env = {'x': ('in',)}
    seq = []
    vid = 0
    for o, d, a, b in prog:
        if o in ('add', 'mul'):
            sa = env[a] if not (a.startswith('k') and a[1:].isdigit()) else ('k', a)
            sb = env[b] if not (b.startswith('k') and b[1:].isdigit()) else ('k', b)
            vid += 1; v = ('v', vid)
            seq.append(('ADD' if o == 'add' else 'MUL', v, sa, sb)); env[d] = v
        elif o == 'alias':
            for i in range(3):
                env['t%d' % i] = env['n%d' % i]
        elif o == 'rename':
            env[d] = env[a]
    outv = env['out']
    last = {}
    for i, (_, v, sa, sb) in enumerate(seq):
        last[sa] = i; last[sb] = i
    free, phys, maxlive = [], {}, [0]
    pool = []
    def preg(v):
        if v == ('in',):
            return X
        if v[0] == 'k':
            return g.regs[v[1]]
        return phys[v]
    alloc = []
    for i, (op, v, sa, sb) in enumerate(seq):
        ra, rb = preg(sa), preg(sb)
        for s_ in ({sa, sb}):
            if s_[0] == 'v' and last.get(s_) == i and s_ in phys and phys[s_] != X:
                free.append(phys[s_])
        if v == outv:
            rd = X
        else:
            if not free:
                pool.append(g.reg('s%d' % len(pool))); free.append(pool[-1])
            rd = free.pop()
        phys[v] = rd
        alloc.append((op, rd, ra, rb))
    STEP_SCRATCH = len(pool)

    def emit_step():
        for op, rd, ra, rb in alloc:
            g.emit(op, rd, ra, rb)
        if trunc is not None:
            if digest_trunc:
                g.emit('MUL', X, X, g.regs['OUTS'])        # test builds only: walk on the low bits of the digest itself
            g.emit('AND', X, X, g.regs['MASKW'])

    # constants and parameters
    ZERO = g.const('ZERO', 0); ONE = g.const('ONE', 1)
    C256 = g.const('C256', 256); C255 = g.const('C255', 255); C8 = g.const('C8', 8)
    DELTA = g.const('DELTA', Delta); SCAPR = g.const('SCAP', S); MCAPR = g.const('MCAP', MCAP)
    GR = g.const('G', G); GPOSR = g.const('GPOS', GPOS); LIMWG = g.const('LIMWG', 1 << WG)
    VBR = g.const('VB', VB); WGR = g.const('WG', WG)
    MV = g.const('MASKV', (1 << VB) - 1); MG = g.const('MASKG', (1 << WG) - 1)
    MR = g.const('MASKRHO', (1 << rho_bits) - 1)
    GB = g.const('GAPBASEBIT', 0)                    # set below (bit offset of the gap array)
    E5R = g.const('E5', E5); TOPBIT = g.const('TOPBIT', 1 << (E5.bit_length() - 1))
    A0R = g.const('A0', L.A0); B0R = g.const('B0', L.B0); MU5 = g.const('MU5', L.mu5)
    C00 = g.const('C00', (P - L.RC[0][0]) % P); C01 = g.const('C01', (P - L.RC[0][1]) % P)
    if trunc is not None:
        g.const('MASKW', (1 << trunc) - 1)
        if digest_trunc:
            g.const('OUTS', outscale)
    for nm in ('BASE', 'POS', 'I', 'CNT', 'LAST', 'RET', 'RET2', 'RHO', 'X0', 'BPV', 'BPG', 'IDX', 'PIDX', 'PVAL', 'E', 'V', 'GV',
               'W0', 'W1', 'WI', 'OFF', 'T1', 'T2', 'GAP', 'I1', 'LAM', 'TB', 'BIDX', 'BVAL', 'DIST', 'CC', 'A', 'B', 'FA',
               'ADDR', 'RR', 'WW', 'BM', 'TT', 'XA', 'XB', 'M0', 'M1', 'OUTA'):
        g.reg(nm)
    R = g.regs
    words_v = -(-(MCAP * VB) // 256); words_g = -(-(MCAP * WG) // 256)
    TABLE_WORDS = words_v + words_g + 1
    gap_base_word = words_v
    X0ADDR = TABLE_WORDS                              # start word
    CBASE = X0ADDR + 1                                # constant memory
    ADDRX0 = g.const('ADDRX0', X0ADDR)
    TW = g.const('TABLEWORDS', TABLE_WORDS)
    # ---------------- setup: load constants (straight line), zero the table, coins
    g.label('start')
    for nm in pre_targets:
        g.target(nm)
    # constant loading: ADDR <- CBASE is itself loaded by IADDI chains? use a dedicated literal at register 'ADDR' = CBASE:
    # the machine starts with R all zero and PC 0; ADDR = CBASE is formed by IADDI steps of 511 (charged).
    rem = CBASE
    while rem > 0:
        st = min(rem, 511)
        g.emit('IADDI', R['ADDR'], R['ADDR'], st); rem -= st
    nconst_slot = []
    for reg_, val in g.consts:
        nconst_slot.append((reg_, val))
        g.emit('LD', reg_, R['ADDR'])
        g.emit('IADDI', R['ADDR'], R['ADDR'], 1)
    # zero the table (memory may hold data; every table word is written)
    g.emit('MOV', R['ADDR'], ZERO)
    g.label('zl')
    g.emit('ST', R['ADDR'], ZERO); g.emit('IADDI', R['ADDR'], R['ADDR'], 1)
    g.emit('BNE', R['ADDR'], TW, g.target('zl'))
    g.label('zl_end')
    # coins
    g.emit('RAND', R['RHO']); g.emit('AND', R['RHO'], R['RHO'], MR)
    g.emit('RAND', R['X0']); g.emit('AND', R['X0'], R['X0'], MR)
    if trunc is not None:
        g.emit('AND', R['X0'], R['X0'], R['MASKW'])
    g.emit('ST', ADDRX0, R['X0'])
    for i in range(3):
        g.emit('ADD', R['k%d' % i], R['k%d' % i], R['RHO'])
    g.emit('MOV', X, R['X0']); g.emit('MOV', R['BASE'], ZERO); g.emit('MOV', R['CNT'], ZERO); g.emit('MOV', R['LAST'], ZERO)
    # ---------------- trail: unrolled blocks of K steps
    g.label('block')
    for k in range(K):
        emit_step()
        g.emit('BLT', X, DELTA, g.target('stub%d' % k))
        g.label('ret%d' % k)
    g.emit('IADDI', R['BASE'], R['BASE'], K)
    g.emit('BLT', R['BASE'], SCAPR, g.target('block'))
    g.label('trail_end')
    g.emit('HALT', 1)                                 # no repeat within the budget
    for k in range(K):
        g.label('stub%d' % k)
        g.emit('IADDI', R['POS'], ZERO, k + 1); g.emit('MOV', R['RET'], g.target('ret%d' % k)); g.emit('JMP', g.target('handler'))

    def extract(bp, mask, dst):
        """dst = field at bit offset R[bp] (10 instructions, 12 operations)."""
        g.emit('SHRV', R['WI'], bp, C8); g.emit('AND', R['OFF'], bp, C255)
        g.emit('LD', R['W0'], R['WI']); g.emit('IADDI', R['WI'], R['WI'], 1); g.emit('LD', R['W1'], R['WI'])
        g.emit('SHRV', R['T1'], R['W0'], R['OFF']); g.emit('ISUB', R['T2'], C256, R['OFF'])
        g.emit('SHLV', R['T2'], R['W1'], R['T2']); g.emit('OR', R['T1'], R['T1'], R['T2']); g.emit('AND', dst, R['T1'], mask)

    def insert(bp, src):
        """OR the field src into the zeroed table at bit offset R[bp] (two read-modify-writes)."""
        g.emit('SHRV', R['WI'], bp, C8); g.emit('AND', R['OFF'], bp, C255)
        g.emit('LD', R['W0'], R['WI']); g.emit('SHLV', R['T1'], src, R['OFF']); g.emit('OR', R['W0'], R['W0'], R['T1'])
        g.emit('ST', R['WI'], R['W0'])
        g.emit('IADDI', R['WI'], R['WI'], 1); g.emit('LD', R['W1'], R['WI']); g.emit('ISUB', R['T2'], C256, R['OFF'])
        g.emit('SHRV', R['T1'], src, R['T2']); g.emit('OR', R['W1'], R['W1'], R['T1']); g.emit('ST', R['WI'], R['W1'])
    # ---------------- DP handler
    g.label('handler')
    g.emit('IADD', R['I'], R['BASE'], R['POS'])
    g.emit('MOV', R['BPV'], ZERO); g.emit('MOV', R['BPG'], GB); g.emit('MOV', R['IDX'], ZERO); g.emit('MOV', R['PIDX'], ZERO)
    g.emit('MOV', R['PVAL'], R['X0']); g.emit('MOV', R['E'], ZERO)
    g.emit('BEQ', R['E'], R['CNT'], g.target('notfound'))
    g.label('scan')
    extract(R['BPV'], MV, R['V']); extract(R['BPG'], MG, R['GV'])
    g.emit('IADD', R['IDX'], R['IDX'], R['GV'])
    g.emit('BEQ', R['V'], X, g.target('found'))
    g.label('scan_nohit')
    g.emit('MOV', R['PIDX'], R['IDX']); g.emit('MOV', R['PVAL'], R['V'])
    g.emit('IADD', R['BPV'], R['BPV'], VBR); g.emit('IADD', R['BPG'], R['BPG'], WGR)
    g.emit('IADDI', R['E'], R['E'], 1); g.emit('BNE', R['E'], R['CNT'], g.target('scan'))
    g.label('notfound')
    g.emit('BEQ', R['CNT'], MCAPR, g.target('fail_overflow'))
    g.label('nf_room')
    g.emit('ISUB', R['GAP'], R['I'], R['LAST'])
    g.emit('BLT', R['GAP'], LIMWG, g.target('gapok'))
    g.label('gap_fail')
    g.emit('HALT', 3)                                 # gap field width exceeded
    g.label('gapok')
    insert(R['BPV'], X); insert(R['BPG'], R['GAP'])
    g.emit('IADDI', R['CNT'], R['CNT'], 1); g.emit('MOV', R['LAST'], R['I']); g.emit('JMP', R['RET'])
    g.label('fail_overflow')
    g.emit('HALT', 2)
    # ---------------- repeat found: entry index IDX = i1, previous stored index PIDX = a with value PVAL
    g.label('found')
    g.emit('ISUB', R['LAM'], R['I'], R['IDX']); g.emit('IADD', R['TB'], R['PIDX'], R['LAM'])
    g.emit('MOV', R['A'], R['PVAL'])
    # second scan: b = largest stored index <= tb, with its value (x_0 if none)
    g.emit('MOV', R['BPV'], ZERO); g.emit('MOV', R['BPG'], GB); g.emit('MOV', R['IDX'], ZERO)
    g.emit('MOV', R['BIDX'], ZERO); g.emit('MOV', R['BVAL'], R['X0']); g.emit('MOV', R['E'], ZERO)
    g.label('scan2')
    extract(R['BPV'], MV, R['V']); extract(R['BPG'], MG, R['GV'])
    g.emit('IADD', R['IDX'], R['IDX'], R['GV'])
    g.emit('BLT', R['TB'], R['IDX'], g.target('scan2done'))
    g.label('scan2_cont')
    g.emit('MOV', R['BIDX'], R['IDX']); g.emit('MOV', R['BVAL'], R['V'])
    g.emit('IADD', R['BPV'], R['BPV'], VBR); g.emit('IADD', R['BPG'], R['BPG'], WGR)
    g.emit('IADDI', R['E'], R['E'], 1); g.emit('BNE', R['E'], R['CNT'], g.target('scan2'))
    g.label('scan2done')
    g.emit('ISUB', R['DIST'], R['TB'], R['BIDX'])
    g.emit('BLT', GPOSR, R['DIST'], g.target('fail_pos'))
    g.label('pos_setup')
    # positioning: X = x_b, DIST steps
    g.emit('MOV', X, R['BVAL']); g.emit('MOV', R['CC'], ZERO)
    g.emit('BEQ', R['CC'], R['DIST'], g.target('posdone'))
    g.label('pos')
    g.emit('MOV', R['RET2'], g.target('posret')); g.emit('JMP', g.target('stepsub'))
    g.label('posret')
    g.emit('IADDI', R['CC'], R['CC'], 1); g.emit('BNE', R['CC'], R['DIST'], g.target('pos'))
    g.label('posdone')
    g.emit('MOV', R['B'], X)
    # lockstep
    g.emit('MOV', R['CC'], ZERO)
    g.label('lock')
    g.emit('MOV', X, R['A']); g.emit('MOV', R['RET2'], g.target('lr1')); g.emit('JMP', g.target('stepsub'))
    g.label('lr1')
    g.emit('MOV', R['FA'], X); g.emit('MOV', X, R['B']); g.emit('MOV', R['RET2'], g.target('lr2')); g.emit('JMP', g.target('stepsub'))
    g.label('lr2')
    g.emit('BEQ', R['FA'], X, g.target('equal'))
    g.label('lr2_cont')
    g.emit('MOV', R['A'], R['FA']); g.emit('MOV', R['B'], X)
    g.emit('IADDI', R['CC'], R['CC'], 1); g.emit('BNE', R['CC'], GR, g.target('lock'))
    g.label('lock_cap')
    g.emit('HALT', 5)                                 # lockstep cap
    g.label('fail_pos')
    g.emit('HALT', 4)                                 # positioning cap
    g.label('equal')
    g.emit('BEQ', R['A'], R['B'], g.target('fail_cycle'))
    g.label('output')
    # output: messages of A and B; fifth root by a left-to-right ladder over the bits of e5
    frc = [0]

    def fifth_root(src, dst):
        g.emit('MOV', R['RR'], ONE); g.emit('MOV', R['BM'], TOPBIT)
        frc[0] += 1
        lab = 'fr%d' % frc[0]
        g.label(lab)
        g.emit('MUL', R['RR'], R['RR'], R['RR']); g.emit('AND', R['TT'], E5R, R['BM'])
        skip = lab + 's'
        g.emit('BEQ', R['TT'], ZERO, g.target(skip))
        g.label(lab + 'b')
        g.emit('MUL', R['RR'], R['RR'], src)
        g.label(skip)
        g.emit('SHRV', R['BM'], R['BM'], ONE); g.emit('BNE', R['BM'], ZERO, g.target(lab))
        g.label(lab + 'e')
        g.emit('MOV', dst, R['RR'])
    g.emit('MOV', R['OUTA'], ZERO)
    for P_ in ('A', 'B'):
        g.emit('ADD', R['WW'], R[P_], R['RHO'])
        fifth_root(R['WW'], R['TT'] if False else R['XA'])            # T = W^e5
        g.emit('ADD', R['XB'], R['XA'], A0R)                          # A = T + A0
        g.emit('MUL', R['M1'], MU5, R['XA']); g.emit('ADD', R['M1'], R['M1'], B0R)    # B = mu5 T + B0
        fifth_root(R['XB'], R['M0']); g.emit('ADD', R['M0'], R['M0'], C00)            # nk = A^e5 - c00
        fifth_root(R['M1'], R['XB']); g.emit('ADD', R['M1'], R['XB'], C01)            # rho = B^e5 - c01
        g.emit('ST', R['OUTA'], R['M0']); g.emit('IADDI', R['OUTA'], R['OUTA'], 1)
        g.emit('ST', R['OUTA'], R['M1']); g.emit('IADDI', R['OUTA'], R['OUTA'], 1)
    g.emit('HALT', 0)
    g.label('fail_cycle')
    g.emit('HALT', 6)
    # step subroutine (one copy)
    g.label('stepsub')
    emit_step()
    g.emit('JMP', R['RET2'])
    # fix the gap-array base and resolve label constants
    gap_base_bit = gap_base_word * 256
    consts_vals = []
    for reg_, val in g.consts:
        if isinstance(val, tuple):
            val = g.labels[val[1]]
        if reg_ == g.regs['GAPBASEBIT']:
            val = gap_base_bit
        consts_vals.append(val)
    tnames = [v[1] for _, v in g.consts if isinstance(v, tuple)]
    assert set(tnames) <= set(pre_targets) or not pre_targets, set(tnames) - set(pre_targets)
    return {'target_names': tnames, 'step_scratch': STEP_SCRATCH, 'code': g.code, 'labels': g.labels, 'regs': g.regs, 'const_regs': [r_ for r_, _ in g.consts], 'const_vals': consts_vals,
            'CBASE': CBASE, 'TABLE_WORDS': TABLE_WORDS, 'words_v': words_v, 'words_g': words_g, 'X0ADDR': X0ADDR, 'L': L, 'outscale': outscale}


def run(prog, rand_words, max_instr=10 ** 9, hits=None):
    """execute; returns (halt code, cost, instructions executed, memory, registers); hits (dict) counts label entries."""
    code = prog['code']
    labat = {v: k for k, v in prog['labels'].items()} if hits is not None else {}
    MEM = {}
    for i, v in enumerate(prog['const_vals']):
        MEM[prog['CBASE'] + i] = v
    R = [0] * 512
    pc = 0; cost = 0; n = 0
    rw = iter(rand_words)
    while True:
        if labat and pc in labat:
            hits[labat[pc]] = hits.get(labat[pc], 0) + 1
        op, a, b, c = code[pc]
        cost += OPS[op]; n += 1
        assert n < max_instr
        pc += 1
        if op == 'ADD':
            R[a] = (R[b] + R[c]) % P
        elif op == 'SUB':
            R[a] = (R[b] - R[c]) % P
        elif op == 'MUL':
            R[a] = R[b] * R[c] % P
        elif op == 'IADD':
            R[a] = (R[b] + R[c]) & M256
        elif op == 'ISUB':
            R[a] = (R[b] - R[c]) & M256
        elif op == 'IADDI':
            R[a] = (R[b] + c) & M256
        elif op == 'MOV':
            R[a] = R[b]
        elif op == 'AND':
            R[a] = R[b] & R[c]
        elif op == 'OR':
            R[a] = R[b] | R[c]
        elif op == 'SHRV':
            R[a] = R[b] >> R[c] if R[c] < 256 else 0
        elif op == 'SHLV':
            R[a] = (R[b] << R[c]) & M256 if R[c] < 256 else 0
        elif op == 'LD':
            R[a] = MEM.get(R[b], 0)
        elif op == 'ST':
            MEM[R[a]] = R[b]
        elif op == 'BLT':
            if R[a] < R[b]:
                pc = R[c]
        elif op == 'BEQ':
            if R[a] == R[b]:
                pc = R[c]
        elif op == 'BNE':
            if R[a] != R[b]:
                pc = R[c]
        elif op == 'JMP':
            pc = R[a]
        elif op == 'RAND':
            R[a] = next(rw)
        elif op == 'HALT':
            return a, cost, n, MEM, R
        else:
            raise ValueError(op)


def static_costs(prog):
    """cost of straight-line regions between labels (for the closed-form ledger)."""
    code, lab = prog['code'], prog['labels']
    def span(l0, l1):
        return sum(OPS[code[i][0]] for i in range(lab[l0], lab[l1]))
    return span


if __name__ == '__main__':
    import json
    p = build_program(Delta=1 << 20, S=1 << 10, MCAP=64, G=100, GPOS=200, VB=22, WG=16, trunc=24)
    print('instructions', len(p['code']), 'registers', len(p['regs']), 'constants', len(p['const_vals']), 'step scratch', p['step_scratch'])


def region_costs(prog):
    """static cost of the listing's regions (label spans), used by the worst-case ledger."""
    code, lab = prog['code'], prog['labels']
    def c(l0, l1):
        return sum(OPS[code[i][0]] for i in range(lab[l0], lab[l1]))
    step_sub = c('stepsub', 'stepsub') + sum(OPS[code[i][0]] for i in range(lab['stepsub'], len(code)))   # the copy + JMP RET2
    rc = {
        'setup_pre': c('start', 'zl'), 'zero_iter': c('zl', 'zl_end'), 'setup_post': c('zl_end', 'block'),
        'block': c('block', 'trail_end'), 'trail_halt': 1, 'stub': c('stub0', 'stub1'),
        'h_pre': c('handler', 'scan'), 'scan_iter': c('scan', 'notfound'), 'scan_hit_part': c('scan', 'scan_nohit'),
        'notfound': c('notfound', 'nf_room') + c('nf_room', 'gap_fail') + c('gapok', 'fail_overflow'),
        'overflow': c('notfound', 'nf_room') + 1,
        'found_pre': c('found', 'scan2'), 'scan2_iter': c('scan2', 'scan2done'), 'scan2_exit_part': c('scan2', 'scan2_cont'),
        'pos_pre': c('scan2done', 'pos_setup') + c('pos_setup', 'pos'),
        'pos_iter': c('pos', 'posdone') + step_sub, 'lock_pre': c('posdone', 'lock'),
        'lock_iter': c('lock', 'lock_cap') + 2 * step_sub, 'equal': c('equal', 'output'), 'step_sub': step_sub,
    }
    return rc


def output_cost(prog):
    """the output segment is deterministic (its branches depend only on the bits of e5): execute it on dummy values."""
    code, lab = prog['code'], prog['labels']
    R = [0] * 512
    for r_, v in zip(prog['const_regs'], prog['const_vals']):
        R[r_] = v
    R[prog['regs']['A']] = 5; R[prog['regs']['B']] = 7
    pc = lab['output']; cost = 0
    while True:
        op, a, b, c = code[pc]; cost += OPS[op]; pc += 1
        if op == 'HALT':
            return cost
        if op == 'ADD': R[a] = (R[b] + R[c]) % P
        elif op == 'MUL': R[a] = R[b] * R[c] % P
        elif op == 'IADDI': R[a] = (R[b] + c) & M256
        elif op == 'MOV': R[a] = R[b]
        elif op == 'AND': R[a] = R[b] & R[c]
        elif op == 'SHRV': R[a] = R[b] >> R[c] if R[c] < 256 else 0
        elif op == 'ST': pass
        elif op == 'BEQ':
            if R[a] == R[b]: pc = R[c]
        elif op == 'BNE':
            if R[a] != R[b]: pc = R[c]
        else: raise ValueError(op)


def worst_case(prog, S, MCAP, G, GPOS, K=15):
    """worst-case cost of one attempt over every control path (all caps charged)."""
    rc = region_costs(prog); out = output_cost(prog)
    blocks = -(-S // K)
    rows = {}
    rows['setup (constants, table zeroing, coins)'] = rc['setup_pre'] + prog['TABLE_WORDS'] * rc['zero_iter'] + rc['setup_post']
    rows['trail: %d blocks x %d' % (blocks, rc['block'])] = blocks * rc['block'] + rc['trail_halt']
    calls = MCAP
    rows['DP handler: %d insertions (stub, preamble, scan of c = 0..MCAP-1 entries, insert)' % calls] =         calls * (rc['stub'] + rc['h_pre'] + rc['notfound']) + rc['scan_iter'] * (MCAP * (MCAP - 1) // 2)
    last_found = rc['found_pre'] + MCAP * rc['scan2_iter'] + rc['pos_pre'] + GPOS * rc['pos_iter'] + rc['lock_pre'] + G * rc['lock_iter'] + rc['equal'] + out
    rows['last DP call: scan of MCAP entries, then the larger of overflow and recovery (second scan, positioning cap, lockstep cap, output)'] =         rc['stub'] + rc['h_pre'] + MCAP * rc['scan_iter'] + max(rc['overflow'], last_found)
    return sum(rows.values()), rows, rc, out


def path_cost(prog, hits, halt):
    """exact cost of an executed path from its label entry counts (every region below is straight-line from its label
    to the next listed label, so cost = sum over regions of entries x region cost)."""
    code, lab = prog['code'], prog['labels']
    order = sorted(lab.items(), key=lambda kv: kv[1])
    pos = [v for _, v in order] + [len(code)]
    cost = 0
    for (name, start), end in zip(order, pos[1:]):
        h = hits.get(name, 0)
        if not h:
            continue
        # a region may exit early only at a branch; charge up to the first taken exit: count instructions until the first
        # branch/jump/halt whose taken target leaves the region (handled by the label entry counts of the next regions)
        seg = 0
        for i in range(start, end):
            seg += OPS[code[i][0]]
        cost += h * seg
    return cost
```

### search.py

```python
"""search.py - the one-trail distinguished-point collision search (reference implementation, any map F on [0, N)).

Parameters: Delta (distinguished set D = {v < Delta}), S trail-step cap, MCAP table capacity, G (recovery cap),
d (detection allowance), WG (gap field width in bits).
Trail: x_0 given (index 0, kept as the start word). For i = 1..S: x_i = F(x_{i-1}); if x_i < Delta (DP test:
one comparison, one branch): scan the table (entries in index order: the DP value and the gap to the previous
stored index); a stored value equal to x_i -> repeat detected at i2 = i with i1 = the stored index; else append
(x_i, i - last) if the table holds fewer than MCAP entries and the gap is below 2^WG, otherwise stop (failure).
Recovery (Section 4 of the proof):
  lam = i2 - i1; a = the stored index preceding i1 in the table (0 = the start word x_0 if none); A = x_a.
  target index tb = a + lam; b = the largest stored index <= tb (b >= a); walk B from x_b for tb - b steps
  (capped at GPOS = G + d - 1; above the cap: stop, failure 'pos-cap').
  Lockstep: while F(A) != F(B): A, B = F(A), F(B) (capped at G iterations; above: failure 'lock-cap').
  Output (A, B) if A != B (two distinct points with equal images), else failure 'start-on-cycle'.
Returns (code, pair, counters).
"""


def search(F, x0, Delta, S, MCAP, G, d, WG):
    table = []                 # (value, gap)
    last = 0
    x = x0
    cnt = {'trail_steps': 0, 'dp_hits': 0, 'scan_entries': 0, 'pos_evals': 0, 'lock_iters': 0}
    for i in range(1, S + 1):
        x = F(x)
        cnt['trail_steps'] += 1
        if x < Delta:
            cnt['dp_hits'] += 1
            idx = 0
            hit = None
            prev_idx = 0
            for (v, gap) in table:
                cnt['scan_entries'] += 1
                idx += gap
                if v == x:
                    hit = idx
                    break
                prev_idx = idx
            if hit is not None:
                return recover(F, x0, table, hit, prev_idx, i, G, d, cnt)
            if len(table) >= MCAP:
                return 'table-full', None, cnt
            if i - last >= 1 << WG:
                return 'gap-width', None, cnt
            table.append((x, i - last))
            last = i
    return 'no-repeat', None, cnt


def stored_value(x0, table, index):
    if index == 0:
        return x0
    idx = 0
    for (v, gap) in table:
        idx += gap
        if idx == index:
            return v
    raise KeyError(index)


def recover(F, x0, table, i1, a, i2, G, d, cnt):
    lam = i2 - i1
    A = stored_value(x0, table, a)
    tb = a + lam
    b, idx = 0, 0
    for (v, gap) in table:                       # largest stored index <= tb
        if idx + gap > tb:
            break
        idx += gap
        b = idx
    B = stored_value(x0, table, b)
    dist = tb - b
    if dist > G + d - 1:
        return 'pos-cap', None, cnt
    for _ in range(dist):
        B = F(B); cnt['pos_evals'] += 1
    for _ in range(G):
        FA, FB = F(A), F(B)
        cnt['lock_iters'] += 1
        if FA == FB:
            if A == B:
                return 'start-on-cycle', None, cnt
            cnt['mu_minus_a'] = cnt['lock_iters']
            cnt['pos_dist'] = dist
            return 'ok', (A, B), cnt
        A, B = FA, FB
    return 'lock-cap', None, cnt
```

### cert.py

```python
"""cert.py - exact parameters, success bound, operation ledger and memory layout of the r = 31 search.
All arithmetic is exact (integers, fractions) or Decimal at 90 digits with every transcendental term rounded
upward by an explicit margin, so each printed bound is on the safe side.
Usage: python cert.py            (prints the certificate as JSON and asserts every inequality)
       python cert.py --search   (re-derives the parameters: grid over Delta, d, G with n minimal)
"""
import sys, json, math
from decimal import Decimal, getcontext
from fractions import Fraction
getcontext().prec = 90
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
N = P
C31 = 216 + 21 * 31            # 867
STEP = 508                     # step program (step.py), verified against the reference permutation
DP_OPS = 2                     # distinguished test: x < Delta (one 256-bit comparison) and one conditional branch
K_UNROLL = 15                  # steps per unrolled block
BLOCK_OPS = 3                  # per block: counter increment, comparison with the block cap, branch
WG = 120                       # gap field width (bits)
ULP = Decimal(10) ** -85


def dexp(x):
    """upper bound of exp(x) for a Decimal x (Decimal exp is correctly rounded; add a relative margin)."""
    return x.exp() * (1 + ULP) + ULP


def to_dec(fr):
    return Decimal(fr.numerator) / Decimal(fr.denominator)


def value_bits(Delta):
    return (Delta - 1).bit_length()


PRE_OPS = 1 << 48               # preprocessing = derivation of the program constants (< 2^24 operations), charged at this over-bound


def listing(Delta, d, G, MCAP, n):
    import machine
    S = n + d
    return machine.build_program(Delta, S, MCAP, G, G + d - 1, value_bits(Delta), WG, K=K_UNROLL)


def memory(MCAP, Delta, prog=None):
    """byte layout of the listing (machine.py); returns (total, regions)."""
    if prog is None:
        import machine
        prog = machine.build_program(Delta, 1 << 127, MCAP, 1 << 112, 1 << 113, value_bits(Delta), WG, K=K_UNROLL)
    regions = {
        'table: DP values %d x %d bits + gaps %d x %d bits, packed, + 1 spare word (%d words)' % (MCAP, value_bits(Delta), MCAP, WG, prog['TABLE_WORDS']): prog['TABLE_WORDS'] * 32,
        'start word x_0': 32,
        'program: %d instructions x 4 bytes (5-bit opcode, three 9-bit fields)' % len(prog['code']): len(prog['code']) * 4,
        'constant memory: %d words (%d step constants incl. the 3 entry offsets, parameters, masks, jump targets)' % (len(prog['const_vals']), len(prog['const_vals']) - 88): len(prog['const_vals']) * 32,
        'register file: %d registers of 256 bits (every register the listing names)' % len(prog['regs']): len(prog['regs']) * 32,
    }
    return sum(regions.values()), regions


def fail_bound(Delta, n, d, G, MCAP):
    """upper bound of the failure probability (Lemma 3), Decimal, rounded up. The trail runs whole blocks, so at most
    S' = K ceil((n + d) / K) values are visited; S' is used wherever the lemma needs the number of values."""
    S = K_UNROLL * (-(-(n + d) // K_UNROLL))
    th_lo = Fraction(Delta - S, N); th_hi = Fraction(Delta, N - S)
    t = {}
    t['no repeat within n steps'] = dexp(-to_dec(Fraction(n * (n + 1), 2 * N)))
    t['start on the cycle (mu = 0)'] = to_dec(Fraction(n, N)) + ULP
    t['cycle shorter than d'] = to_dec(Fraction(n * d, N)) + ULP
    t['no DP in the first d cycle values'] = dexp(-to_dec(th_lo) * d)
    t['lockstep cap: mu - a > G'] = dexp(-to_dec(th_lo) * G)
    t['positioning cap: back-gap > G + d - 1'] = dexp(-to_dec(th_lo) * (G + d - 1))
    mu = to_dec(th_hi) * S
    a = MCAP + 1
    # Chernoff: P(Bin(S, th_hi) >= a) <= exp(-mu) (e mu / a)^a = exp(a - mu + a ln(mu / a))
    # valid only above the mean (a > mu); otherwise the term is bounded by 1
    t['table overflow (more than MCAP DPs)'] = (dexp(Decimal(a) - mu + Decimal(a) * (mu / a).ln() * (1 - ULP) + ULP)
                                               if Decimal(a) > mu else Decimal(1))
    t['gap field width: a DP gap >= 2^WG'] = Decimal(S) * dexp(-to_dec(th_lo) * ((1 << WG) - 1))
    return sum(t.values()), t


def ledger(Delta, n, d, G, MCAP):
    import machine
    prog = listing(Delta, d, G, MCAP, n)
    S = n + d
    W, rows, rc, out = machine.worst_case(prog, S, MCAP, G, G + d - 1, K=K_UNROLL)
    rows = dict(rows)
    rows['preprocessing: derivation of the program constants (< 2^24 operations), charged at an over-bound of 2^48'] = PRE_OPS
    return W + PRE_OPS, rows


def minimal_n(Delta, d, G, MCAP, target=Decimal('0.39')):
    lo, hi = 1 << 126, 1 << 128
    def ok(n):
        f, _ = fail_bound(Delta, n, d, G, MCAP)
        return 1 - f >= target
    # find the least n with ok(n) on the unimodal side below the table-overflow wall
    lo, hi = int(Decimal(2) ** Decimal('126.95')), int(Decimal(2) ** Decimal('127.03'))
    assert not ok(lo) and ok(hi), (ok(lo), ok(hi))
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return hi


def score(Delta, d, G, MCAP):
    n = minimal_n(Delta, d, G, MCAP)
    W, _ = ledger(Delta, n, d, G, MCAP)
    return math.log2(W / C31), n


PARAMS = (4955463538568564343182868956103890945703936, 55495557539318368702682515302776833,
          56955966948247799215295948946145281, 30250, 169297055886635591747237776317843690204)   # (Delta, d, G, MCAP, n): search_params.py's least n (grid at r = 31) raised by 4e-6 (relative) for a visible success margin   # (Delta, d, G, MCAP, n): search_params.py's least n (grid dl=141.83, kd=9.5, H=9.75, MCAP 30550) raised by 4e-6 (relative) for a visible success margin


def certify(Delta, d, G, MCAP, n):
    f, terms = fail_bound(Delta, n, d, G, MCAP)
    succ = 1 - f
    W, rows = ledger(Delta, n, d, G, MCAP)
    mem, regions = memory(MCAP, Delta, listing(Delta, d, G, MCAP, n))
    t = Fraction(W, C31)
    tl = math.log2(W) - math.log2(C31)
    claim_t = math.ceil(tl * 100000) / 100000
    T5 = round(claim_t * 100000)
    assert W ** 100000 <= (1 << T5) * C31 ** 100000
    assert mem <= 1 << 20
    f2, _ = fail_bound(Delta, n - 1, d, G, MCAP)
    return {'Delta': Delta, 'n': n, 'd': d, 'G': G, 'MCAP': MCAP, 'S': n + d, 'theta_log2': math.log2(Delta) - math.log2(N),
            'success_lower_bound': str(succ), 'success_at_n_minus_1': str(1 - f2),
            'fail_terms': {k: '%.6e' % v for k, v in terms.items()},
            'W_ops': W, 'ledger': rows, 'time_log2': tl, 'claim_time_log2': claim_t,
            'memory_bytes': mem, 'memory_regions': regions, 'memory_slack': (1 << 20) - mem,
            'memory_log2': math.log2(mem)}


if __name__ == '__main__':
    if '--search' in sys.argv:
        best = None
        for MCAP in range(28800, 29401, 100):
            for dl in [141.86 + 0.01 * i for i in range(25)]:
                Delta = int(2 ** dl)
                mem, _ = memory(MCAP, Delta)
                if mem > (1 << 20):
                    continue
                th = Delta / N
                for kd in (9.0, 9.25, 9.5, 9.75, 10.0):
                    for H in (8.5, 8.75, 9.0, 9.25, 9.5, 9.75):
                        d = int(kd / th) + 1; G = int(H / th) + 1
                        try:
                            s, n = score(Delta, d, G, MCAP)
                        except AssertionError:
                            continue
                        if best is None or s < best[0]:
                            best = (s, Delta, d, G, MCAP, n)
                            print(json.dumps({'score': s, 'Delta_log2': dl, 'MCAP': MCAP, 'kd': kd, 'H': H}), flush=True)
        print('BEST', best)
    else:
        print(json.dumps(certify(*PARAMS), indent=1, default=str))

COST = C31
```

### search_params.py

```python
"""search_params.py - the grid search that fixed the r = 31 parameters: for each Delta = 2^dl, the largest table capacity
MCAP (step 50) that fits 2^20 bytes, and d = kd / theta, G = H / theta on a grid; n is the least budget with bound >= 0.39
(cert.minimal_n). Prints each improvement and the best tuple (Delta, d, G, MCAP, n)."""
import cert, json
best=None
for dl in [141.70 + 0.01*i for i in range(14)]:
    Delta=int(2**dl)
    M=29000
    while cert.memory(M+50,Delta)[0] <= (1<<20): M+=50
    th=Delta/cert.N
    for kd in (9.0,9.25,9.5,9.75):
        for H in (9.0,9.25,9.5,9.75):
            d=int(kd/th)+1; G=int(H/th)+1
            try: s,n=cert.score(Delta,d,G,M)
            except AssertionError: continue
            if best is None or s<best[0]:
                best=(s,Delta,d,G,M,n); print(json.dumps({'s':s,'dl':dl,'M':M,'kd':kd,'H':H}),flush=True)
print('BEST',best)
```

### render_round.py

```python
"""render_r23.py - assemble the r = 23 package (proof.md, claim.json, experiment manifest, certificate manifest)
from cert.py (parameters, ledger, memory), the campaign and reduced-width search runs of Section 6, the machine
tests of Appendix B and the programs of Appendix A. Every declared bound is asserted in exact arithmetic.

The proof text is the r = 56 proof of the dependency 43caeb6a-90a2-42bb-9cad-0c0fb6bfe661 (in review) ported to
r = 23: the round-dependent figures are replaced by this round's certificate (step program 136 + 12 r, memory at
this round's listing, parameters re-optimised by search_params.py at r = 23) and the Section 6 evidence is
re-measured on the r = 23 map (campaign.py, sim.py, prerun.py; Appendix A).

Usage: python3 render_r23.py <outdir>"""
import json, math, os, sys
from collections import defaultdict
from decimal import Decimal
import cert, machine

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = '/tmp/hs/ag/frnt3/r56/poseidon/proof.md'
NL = chr(10)


def ceil5(x):
    return math.ceil(x * 100000 - 1e-9) / 100000


def exp_mean(w):
    """exact mean of X = tau(tau-1)/(2N) for a uniformly random function on N = 2^w points."""
    N = 1 << w
    surv = 1.0; E = 0.0
    for t in range(1, N + 1):
        p = surv * t / N
        E += p * t * (t - 1) / (2 * N)
        surv *= (1 - t / N)
        if surv < 1e-30:
            break
    return E

import cert, machine
from step import build as _build_step

R = int(os.environ['PORT_ROUND'])
COST = 216 + 21 * R
STEPN = 136 + 12 * R
assert cert.COST == COST and cert.STEP == STEPN, (cert.COST, cert.STEP, R)
def campaign_table():
    rows = defaultdict(list)
    for l in open(os.path.join(HERE, 'h1_campaign.jsonl')):
        r = json.loads(l); rows[r['w']].append(r)
    out = ['| w | walks | E0 | c (real map) | c (SHA-256 control) |', '|---:|---:|---:|---:|---:|']
    allr, allc, alle = 0.0, 0.0, 0
    for w in sorted(rows):
        L = rows[w]; N = 1 << w
        E0 = exp_mean(w)
        mr = sum(r['tau'] * (r['tau'] - 1) / (2 * N) for r in L) / len(L)
        mc = sum(r['tau_control'] * (r['tau_control'] - 1) / (2 * N) for r in L) / len(L)
        se = 1 / math.sqrt(len(L))
        out.append(f'| {w} | {len(L)} | {E0:.5f} | {E0 / mr:.4f} (+- {se * E0 / mr:.4f}) | {E0 / mc:.4f} |')
        allr += sum(r['tau'] * (r['tau'] - 1) / (2 * N) / E0 for r in L)
        allc += sum(r['tau_control'] * (r['tau_control'] - 1) / (2 * N) / E0 for r in L)
        alle += len(L)
    out.append(f'| pooled | {alle} | | {alle / allr:.4f} (+- {1 / math.sqrt(alle):.4f}) | {alle / allc:.4f} |')
    return NL.join(out)


def sim_table():
    out = ['| w | MCAP | Delta | n | d | G | Lemma 3 bound | trials | success real | success control | max lockstep (cap G) | max positioning (cap G+d-1) | failure codes |',
           '|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for fn in sorted(f for f in os.listdir(HERE) if f.startswith('sim_w') and f.endswith('.jsonl')):
        w = int(fn[5:-6])
        par = json.loads(open(os.path.join(HERE, fn[:-6] + '.log')).readline())
        rs = [json.loads(l) for l in open(os.path.join(HERE, fn))]
        codes = defaultdict(int)
        sr = sum(r['real']['code'] == 'ok' for r in rs) / len(rs)
        sc = sum(r['control']['code'] == 'ok' for r in rs) / len(rs)
        lk = max([r[k]['lock'] for r in rs for k in ('real', 'control') if r[k]['code'] == 'ok'])
        ps = max([r[k]['pos'] for r in rs for k in ('real', 'control') if r[k]['code'] == 'ok'])
        for r in rs:
            for k in ('real', 'control'):
                codes[r[k]['code']] += 1
        out.append(f"| {w} | {par['MCAP']} | {par['Delta']} | {par['n']} | {par['d']} | {par['G']} | {par['bound']:.5f} | {len(rs)} | {sr:.4f} | {sc:.4f} | {lk} | {ps} | {dict(codes)} |")
    return NL.join(out)


def swap_block(t, header, block):
    """replace the table whose header row equals `header` (header + consecutive '|' rows) by `block`."""
    lines = t.split(NL)
    i = next(j for j, l in enumerate(lines) if l == header)
    k = i + 1
    while k < len(lines) and lines[k].startswith('|'):
        k += 1
    return NL.join(lines[:i] + block.split(NL) + lines[k:])


def main(outdir):
    c = cert.certify(*cert.PARAMS)
    Delta, d, G, MCAP, n = cert.PARAMS
    prog = cert.listing(Delta, d, G, MCAP, n)
    _, _, rc, out = machine.worst_case(prog, n + d, MCAP, G, G + d - 1, K=cert.K_UNROLL)
    W = c['W_ops']
    tl = c['time_log2']; tcl = ceil5(tl); T5 = round(tcl * 100000)
    assert W ** 100000 <= (1 << T5) * cert.COST ** 100000
    mem = c['memory_bytes']; assert mem <= 1 << 20
    mcl = 20.0
    pre = math.log2(cert.PRE_OPS / cert.COST); pcl = ceil5(pre)
    succ = c['success_lower_bound']
    margin = Decimal(succ) - Decimal('0.39')
    n0 = json.load(open(os.path.join(HERE, 'grid_n0.json')))['n0']   # search_params.py's least n at this round
    assert n == n0 + (n0 * 4) // 1000000
    PRE = json.load(open(os.path.join(HERE, 'prerun.json')))
    pre14 = PRE[f'r{R}-search-w14']; pre10 = PRE[f'r{R}-listing-w10']
    ct = campaign_table(); st = sim_table()

    PARAMS = NL.join(['| parameter | value |', '|---|---:|',
                     f'| Delta (D = {{v < Delta}}) | {Delta} (2^{math.log2(Delta):.6f}) |',
                     f'| theta = Delta / p | 2^{c["theta_log2"]:.6f} |',
                     f'| n (walk budget) | {n} (2^{math.log2(n):.6f}) |',
                     f'| d (detection allowance) | {d} |',
                     f'| S = n + d (trail cap) | {n + d} |',
                     f'| G (recovery cap) | {G} |',
                     f'| MCAP (table capacity) | {MCAP} |',
                     f'| DP value field | {cert.value_bits(Delta)} bits |',
                     f'| gap field WG | {cert.WG} bits |',
                     f'| unrolling | {cert.K_UNROLL} steps per block |'])
    FAILTERMS = NL.join(['| event | bound |', '|---|---:|'] + [f'| {k} | {v} |' for k, v in c['fail_terms'].items()])
    LEDGER = NL.join(['| row | operations |', '|---|---:|'] + [f'| {k} | {v:,} |' for k, v in c['ledger'].items()]
                     + [f'| **total W** | **{W:,}** |'])
    MEMTABLE = NL.join(['| region | bytes |', '|---|---:|'] + [f'| {k} | {v:,} |' for k, v in c['memory_regions'].items()]
                        + [f'| slack to 2^20 | {c["memory_slack"]:,} |', f'| **total (excluding slack)** | **{mem:,}** |'])

    text = open(BASE, encoding='utf-8').read()
    i = text.index('## Appendix A. Programs')
    text = text[:i].rstrip(NL) + NL

    stepcost = cert.STEP + cert.DP_OPS                     # STEP + 2
    nconst = len(_build_step(R, 0)[2])                # step constants at r = R
    import step as _step_mod
    nadd, nmul = _step_mod.count(_build_step(R, 0)[1])
    reps = [
        ('# Orchard Poseidon, 56 partial rounds: one-trail distinguished-point birthday search, counted ledger (time_log2 126.21454)',
         f'# Orchard Poseidon, {R} partial rounds: one-trail distinguished-point birthday search, counted ledger (time_log2 {tcl:.5f})', 1),
        ('Target `poseidon-orchard-r56-prefix-v1`: the complete deployed Orchard P128Pow5T3 schedule (full rounds 0-3, partial\nrounds 4-59, full rounds 60-63)',
         f'Target `poseidon-orchard-r{R}-prefix-v1`: the complete deployed Orchard P128Pow5T3 schedule (full rounds 0-3, partial\nrounds 4-{3 + R}, full rounds 60-63)', 1),
        ('Cost model `orchard-field-ram-v2`, C(56) = 216 + 21 * 56 = 1392.',
         f'Cost model `orchard-field-ram-v2`, C({R}) = 216 + 21 * {R} = {COST}.', 1),
        ('Claim: `time_log2` = 126.21454 (a worst-case count of primitive operations of one attempt of the algorithm below, every\ncap charged in full, divided once by 1392), `memory_log2_bytes` = 20.00000 (1,047,772 bytes, every region itemised in\nSection 8; below 2^20, so the normalized cost equals the time bound), `success_probability` = 0.39, `preprocessing_log2` =\n37.55706 (inside the time bound), no advice.',
         f'Claim: `time_log2` = {tcl:.5f} (a worst-case count of primitive operations of one attempt of the algorithm below, every\ncap charged in full, divided once by {COST}), `memory_log2_bytes` = 20.00000 ({mem:,} bytes, every region itemised in\nSection 8; below 2^20, so the normalized cost equals the time bound), `success_probability` = 0.39, `preprocessing_log2` =\n{pcl:.5f} (inside the time bound), no advice.', 1),
        ('written from their public notes without copying or running any of their files. Our step program reproduces the published\n808-operation count exactly (330 additions, 478 multiplications). What is new here is the analysis and accounting of the\nsearch: ',
         f'and in mitchuski 43caeb6a-90a2-42bb-9cad-0c0fb6bfe661 (in review), whose r = 56 package is ported here. Our step program is\nthe published equivalent form at r = {R} (136 + 12 r = {STEPN} field operations: {nadd} additions, {nmul} multiplications), the\nform of our in-review r = 23 entries (a5a40e52, 9f8717f0, 1533f8f0). The analysis and accounting of the search is the\ndependency\'s: ', 1),
        ('## 2. The step program (808 field operations)', f'## 2. The step program ({STEPN} field operations)', 1),
        ('P_4 is chosen as D^-56 times a diagonal matrix', f'P_4 is chosen as D^-{R} times a diagonal matrix', 1),
        ('Total 3 + 24 + 24 + 12 * 56 + 0 + 3 * 24 + 13 = 808 field operations: 330 additions and 478 multiplications, the published',
         f'Total 3 + 24 + 24 + 12 * {R} + 0 + 3 * 24 + 13 = {STEPN} field operations: {nadd} additions and {nmul} multiplications, the published', 1),
        ('The program uses 330 constants', f'The program uses {nconst} constants', 1),
        ('load the 330 program constants into registers', f'load the {nconst} program constants into registers', 1),
        ('at 8 random points for each of r = 1, 2, 7, 56', f'at 8 random points for each of r = 1, 2, 7, {R}', 1),
        ('**H1 (score-critical).** For the fixed r = 56 walk map family', f'**H1 (score-critical).** For the fixed r = {R} walk map family', 1),
        ('Scope: the target poseidon-orchard-r56-prefix-v1', f'Scope: the target poseidon-orchard-r{R}-prefix-v1', 1),
        ('`experiments/r56_listing.py`', f'`experiments/r{R}_listing.py`', 1),
        ('- `r56-search-w14`', f'- `r{R}-search-w14`', 1),
        ('`r56-listing-w10`', f'`r{R}-listing-w10`', 2),
        ('with a declared file of 469 registers of 256 bits', f'with a declared file of {len(prog["regs"])} registers of 256 bits', 1),
        (f'The step program is\n808 field operations on registers (its 330 constants and 6 scratch registers, allocated by liveness), so a trail step\ncosts 808 + 2 (the distinguished test).',
         f'The step program is\n{cert.STEP} field operations on registers (its {nconst} constants and {prog["step_scratch"]} scratch registers, allocated by liveness), so a trail step\ncosts {cert.STEP} + 2 (the distinguished test).', 1),
        ('a file too small for the 330\nconstants would force about 330 loads per step, adding log2(1 + 660/810) = 0.86 bits',
         f'a file too small for the {nconst}\nconstants would force about {nconst} loads per step, adding log2(1 + {2 * nconst}/{STEPN + 2}) = {math.log2(1 + 2 * nconst / (STEPN + 2)):.2f} bits', 1),
        ('The published r = 56 entries use the same kind of convention (declared register files of\n348 to 414 registers, no fetch charge).',
         'The published entries use the same kind of convention (declared register files, no fetch charge); the dependency\n43caeb6a declares 469 registers at r = 56, our in-review 9f8717f0 223 at r = 23.', 1),
        ('Total 1,047,772 bytes, slack 804 bytes below 2^20', f'Total {mem:,} bytes, slack {c["memory_slack"]:,} bytes below 2^20', 1),
        ('log2 = 19.998893383;', f'log2 = {math.log2(mem):.9f};', 1),
        ('The\npreprocessing peak is therefore below the online peak of 1,047,772 bytes.',
         f'The\npreprocessing peak is therefore below the online peak of {mem:,} bytes.', 1),
        ('n0 = 169299591604647008664007118706234438984 (search_params.py)', f'n0 = {n0} (search_params.py)', 1),
        ('leaves a margin of 2.413e-06 above 0.39, large enough to be checked from the printed terms (the cost of the extra steps is\n2.4e-6 relative, below the five-decimal ceiling of the time claim).',
         f'leaves a margin of {float(margin):.3e} above 0.39, large enough to be checked from the printed terms (the cost of the extra steps is\n4e-6 relative, below the five-decimal ceiling of the time claim).', 1),
        ('the trail runs ceil(S / 15) blocks of 15 x (808 + 2) + 3 operations', f'the trail runs ceil(S / 15) blocks of 15 x ({cert.STEP} + 2) + 3 operations', 1),
        ('at most G + d - 1 positioning iterations at 814 each, at most G\nlockstep iterations at 1632 each, and the output: 11,462 operations',
         f'at most G + d - 1 positioning iterations at {rc["pos_iter"]} each, at most G\nlockstep iterations at {rc["lock_iter"]} each, and the output: {out:,} operations', 1),
        (f'Total W = 137,404,619,507,025,141,827,880,540,151,407,956,629,077 operations. T = W / 1392; log2 T = 126.214538903, submitted as `time_log2` = 126.21454 (ceiling at five decimals;\nW^100000 <= 2^12621454 * 1392^100000 checked in exact integer arithmetic by `final.py`).',
         f'Total W = {W:,} operations. T = W / {COST}; log2 T = {tl:.9f}, submitted as `time_log2` = {tcl:.5f} (ceiling at five decimals;\nW^100000 <= 2^{T5} * {COST}^100000 checked in exact integer arithmetic by `cert.py`).', 1),
        ('declared as `preprocessing_log2` = 37.55706 >= log2(2^48 / 1392) = 37.556',
         f'declared as `preprocessing_log2` = {pcl:.5f} >= log2(2^48 / {COST}) = {pre:.5f}', 1),
        ('(the 330 step constants', f'(the {nconst} step constants', 1),
        ('matrix powers D^(+-56)', f'matrix powers D^(+-{R})', 1),
        ('Sensitivity: each extra operation per step adds about log2(1 + 1/811) = 0.0018 bits',
         f'Sensitivity: each extra operation per step adds about log2(1 + 1/{stepcost}) = {math.log2(1 + 1 / stepcost):.4f} bits', 1),
        ('(computed by `final.py`)', '(computed by `render_round.py`)', 1),
        ('0.390002412718666974609790578045434880751265717235', succ[:51], 3),
        ('the bound exceeds 0.39 by 2.413e-06, so H1 needs the fixed map\'s search to\nreach at least 1 - 6.186e-06 of the random-function success',
         f'the bound exceeds 0.39 by {float(margin):.2e}, so H1 needs the fixed map\'s search to\nreach at least 1 - {float(margin) / 0.39:.3e} of the random-function success', 1),
        ('Pre-run: emulated in the pinned organizer image with the organizer runner and its public seed protocol (hashsmash-public-seed-v1), 166 of 256 trials returned verified mask events (0.648; the stated lower bound is 0.39043, the 0.5% threshold 80), the other 90 returned no pair; 6.9 s per run.',
         f'Pre-run (local, seeds = SHA-256("prerun r{R}-search-w14 <trial>"), `prerun.py` of Appendix A): {pre14["ok"]} of 256 trials returned verified mask events ({pre14["ok"] / 256:.3f}; the stated lower bound is 0.39043, the 0.5% threshold 80), the other {pre14["null"]} returned no pair.', 1),
        ('Pre-run: emulated in the pinned organizer image with the organizer runner and its public seed protocol, 112 verified mask events, 138 no repeat within the budget, 6 start on the cycle (of 256), each counted cost at most the worst case of the listing; 4.7 s per run.',
         f'Pre-run (local, same seeds): {pre10["obs"].get("0", 0)} verified mask events, {pre10["obs"].get("1", 0)} no repeat within the budget, {sum(v for k, v in pre10["obs"].items() if k not in ("0", "1"))} start on the cycle (of 256), each counted cost at most the worst case of the listing.', 1),
        (f'Evidence executed by the organizer (declared experiments; one program, `experiments/r{R}_listing.py`, generated by\n`mk_experiment.py` from `step.py`, `machine.py`, `search.py` and `campaign.py` with the round constants embedded):',
         f'Declared experiments for the organizer runs (one program, `experiments/r{R}_listing.py`, generated by\n`mk_experiment.py` from `step.py`, `machine.py`, `search.py` and `campaign.py` with the round constants embedded):', 1),
        ('poseidon_mage r56 h1 v1 <w> <walk>', f'poseidon_mage r{R} h1 v1 <w> <walk>', 1),
        ('inside the 962,912-byte table region', f'inside the {prog["TABLE_WORDS"] * 32:,}-byte table region', 1),
        ('that check this document (`cert.py`, `final.py`, including its exact 100000-th powers)',
         'that check this document (`cert.py`, `render_round.py`, including the exact 100000-th powers of `cert.py`)', 1),
        ('on the real r = 56 map with the walk on the', f'on the real r = {R} map with the walk on the', 1),
    ]
    for old, new, cnt in reps:
        k = text.count(old)
        assert k == cnt, (k, cnt, old[:100])
        text = text.replace(old, new)

    for header, block in (('| parameter | value |', PARAMS), ('| event | bound |', FAILTERMS),
                          ('| row | operations |', LEDGER), ('| region | bytes |', MEMTABLE),
                          ('| w | walks | E0 | c (real map) | c (SHA-256 control) |', ct),
                          ('| w | MCAP | Delta | n | d | G | Lemma 3 bound | trials | success real | success control | max lockstep (cap G) | max positioning (cap G+d-1) | failure codes |', st)):
        text = swap_block(text, header, block)

    tabbytes = prog['TABLE_WORDS'] * 32
    for tok in ('r56', '1392', ' 808', '478 multiplications', '330 ', '14111', '56,444',
                '1,047,772', '37.55706', '126.214', '29,400', '29400', '4-59', '12 * 56',
                'D^-56', '/811', 'at 814 each', 'at 1632 each', 'final.py', '804 bytes',
                '808 field operations', '13,376', '15,008', '30091', f'962,912', 'hashsmash-public-seed-v1',
                '6.9 s per run', '4.7 s per run', '19.998893383'):
        start = 0
        while True:
            i = text.find(tok, start)
            if i < 0:
                break
            before = text[i - 1] if i > 0 else ''
            j = i + len(tok)
            after = text[j] if j < len(text) else ''
            # a hit embedded in a longer digit/comma/period run is a fragment of one of this
            # round's own figures (e.g. '804 bytes' inside '1,047,804 bytes'), not r56 residue
            if (tok[0].isdigit() and (before.isdigit() or before in ',.')) or \
               (tok[-1].isdigit() and (after.isdigit() or after in ',.')):
                print('sweep: number-fragment hit skipped:', tok, repr(text[max(0, i - 25):j + 25]))
            else:
                raise AssertionError(('leftover', tok, text[max(0, i - 60):j + 60]))
            start = j

    app = ['', '## Appendix A. Programs', '',
           f'Standard library only (python 3). `python step.py 1 2 7 {R}` builds and verifies the step program (also against the',
           'organizer `verifier/poseidon.py` when run inside the challenge repository); `python cert.py` prints the',
           'certificate (parameters, failure terms, ledger, memory); `python search_params.py` re-runs the parameter grid;',
           '`python render_round.py <dir>` assembles this package and asserts the declared bounds; `test_machine.py` cross-checks',
           'the listing against `search.py` trial by trial; `campaign.py` and `sim.py` produce the evidence of Section 6 (`sim.py`',
           'also needs `search.py`); `prerun.py` pre-runs both declared experiments locally; `mk_experiment.py` writes the',
           'organizer experiment. The step program checks itself against a direct implementation of the reduced permutation.', '']
    for fn in ('step.py', 'machine.py', 'search.py', 'cert.py', 'search_params.py', 'render_round.py', 'test_machine.py',
               'mk_experiment.py', 'campaign.py', 'sim.py', 'plan.py', 'prerun.py'):
        app += [f'### {fn}', '', '```python', open(os.path.join(HERE, fn), encoding='utf-8').read().rstrip(), '```', '']
    app += ['## Appendix B. Certificate output (`python cert.py`)', '', '```json', json.dumps(c, indent=1, default=str), '```', '',
            f'Output of `python step.py 1 2 7 {R}` (against `verifier/poseidon.py`, the archived organizer verifier):', '', '```',
            open(os.path.join(HERE, 'step_verify.txt'), encoding='utf-8').read().rstrip(), '```', '']
    for fn, desc in (('machine_test_w16.txt', 'w16'), ('machine_test_w20.txt', 'w20')):
        app += [f'Output of `python test_machine.py {desc} <trials>` ({fn}): every trial compares the listing with search.py on the same coins (outcome and both messages), the counted cost with the path formula, and the cost with the worst-case ledger:', '',
                '```', open(os.path.join(HERE, fn), encoding='utf-8').read().rstrip(), '```', '']
    app += ['Output of `python test_machine.py --stress` (machine_stress.txt): forced exits, cost at most the worst case and equal to the path formula each time:', '',
            '```', open(os.path.join(HERE, 'machine_stress.txt'), encoding='utf-8').read().rstrip(), '```', '']
    text = text.rstrip(NL) + NL + NL.join(app)

    lines = text.split(NL)
    def sec(title):
        i = next(j for j, l in enumerate(lines) if l.startswith(title)) + 1
        k = next((j for j in range(i, len(lines)) if lines[j].startswith('## ')), len(lines))
        k = min(k, len(lines) - (1 if lines and lines[-1] == '' else 0))
        return f'proof:{i}-{k}'
    def sub_sec(title):
        i = next(j for j, l in enumerate(lines) if l == title) + 1
        k = next((j for j in range(i, len(lines)) if lines[j].startswith('## ') or lines[j].startswith('### ')), len(lines))
        k = min(k, len(lines) - (1 if lines and lines[-1] == '' else 0))
        return f'proof:{i}-{k}'
    appB = sec('## Appendix B.')
    ev1 = [sec('## 3.'), sec('## 4.'), sec('## 5.'), sec('## 6.'), sec('## 9.'), sub_sec('### search.py'), sub_sec('### campaign.py'),
           sub_sec('### sim.py'), appB]
    ev2 = [sec('## 7.'), sec('## 8.'), sec('## 9.'), sec('## 2.'), sub_sec('### machine.py'), sub_sec('### test_machine.py'), appB]
    claim = {"schema_version": 3, "submission_state": "ready", "target_profile": f"poseidon-orchard-r{R}-prefix-v1",
             "attack_class": "ordinary-collision", "rounds": R,
             "claim": {"time_log2": tcl, "time_unit": "target-compressions", "memory_log2_bytes": mcl,
                       "preprocessing_log2": pcl, "success_probability": 0.39, "nonuniform_advice_log2_bytes": 0},
             "restrictions": [], "baseline_improved": f"poseidon-orchard-r{R}-nominal-v2",
             "certificate_manifest": "certificates/manifest.json", "lane": "exploratory",
             "heuristics": [
                 {"id": "H1-fixed-map-random-function",
                  "statement": f"For the fixed r = {R} walk map family F_rho0 of proof Section 1, with rho0 and x_0 drawn as in proof Section 3, the search of proof Section 3 at the parameters of proof Section 9 succeeds with probability at least 0.39 (the random-function bound of proof Section 5 is " + succ[:51] + ").",
                  "role": "score-critical", "scope": f"poseidon-orchard-r{R}-prefix-v1, the two-round line of proof Section 1, the parameters of proof Section 9.",
                  "extrapolation": "From a proved bound for a uniformly random function and from measurements at output widths 16 to 32 bits to the full 254-bit map; the bound exceeds 0.39 by " + f'{float(margin):.2e}' + ", so the premise needs the fixed map's success to be within that of the random-function value.",
                  "evidence_ids": ev1,
                  "limitations": "Unproved. The pooled standard error of the collision-rate measurement is about 0.017 (about 3.4% at two standard errors), far above the deficit the filed budget tolerates: the budget has essentially no robustness margin (proof Section 9 gives the cost of absorbing a deficit)."},
                 {"id": "H2-machine-register-file",
                  "statement": "Operation prices on the register machine of proof Section 7, whose listing (machine.py) is the algorithm: a declared file of " + str(len(prog['regs'])) + " registers of 256 bits and 4-byte instructions, both counted in memory; field operations (canonical results), integer and bit operations, register moves and RAND 1; loads and stores 2 (access and address); compare-and-branch 2; jumps 1; instruction fetch not charged.",
                  "role": "score-critical", "scope": "The cost and memory claims of this package.",
                  "extrapolation": f"None; a declared convention, the same kind as the published entries' register files (the dependency 43caeb6a declares 469 at r = 56; our in-review 9f8717f0 declares 223 at r = 23; this package declares {len(prog['regs'])} at r = {R}).",
                  "evidence_ids": ev2,
                  "limitations": "The contract fixes no register count; proof Section 7 states the cost of a smaller file or of charging instruction fetch."}]}
    import subprocess
    os.makedirs(os.path.join(outdir, 'experiments'), exist_ok=True)
    subprocess.run([sys.executable, os.path.join(HERE, 'mk_experiment.py'), os.path.join(outdir, 'experiments', f'r{R}_listing.py')], check=True)
    man = {'schema_version': 1, 'experiments': [{
        'id': f'r{R}-search-w14', 'kind': 'python-message-pairs-v1',
        'scope': f'poseidon-orchard-r{R}-prefix-v1; the search of proof Section 3 (search.py) on the real map with the walk on the low 14 bits of the digest; parameters chosen in advance by Lemma 3 at N = 2^14 (Delta 6144, n 171, d 16, G 16, S 187, MCAP 96); organizer seeds.',
        'hypothesis': 'Premise H1 at reduced width: the real-map search succeeds at least as often as the random-function bound 0.39043 of Lemma 3 at these parameters (count at least Binomial(256, 0.39043) in distribution; below 80 of 256 would contradict it at the 0.5% level). Successes are mask events on the low 14 digest bits, not collisions.',
        'program': f'experiments/r{R}_listing.py',
        'event': {'kind': 'digest-xor-mask', 'mask_hex': 'ff3f' + '00' * 30, 'expected_hex': '00' * 32}}, {
        'id': f'r{R}-listing-w10', 'kind': 'python-message-pairs-v1',
        'scope': f'poseidon-orchard-r{R}-prefix-v1; the complete search listing of proof Section 3 on the real step program, walk on the low 10 bits of the digest, small fixed control-flow parameters; organizer seeds.',
        'hypothesis': 'The instruction listing whose counted cost is the ledger of proof Section 9 runs end to end on the target: successful attempts return distinct canonical messages whose digests agree on the low 10 bits (a mask event, not a collision).',
        'program': f'experiments/r{R}_listing.py',
        'event': {'kind': 'digest-xor-mask', 'mask_hex': 'ff03' + '00' * 30, 'expected_hex': '00' * 32}}]}
    json.dump(man, open(os.path.join(outdir, 'experiments', 'manifest.json'), 'w', newline=NL), indent=1)
    claim['experiment_manifest'] = 'experiments/manifest.json'
    claim['heuristics'][1]['evidence_ids'].append(f'experiment:r{R}-listing-w10')
    claim['heuristics'][0]['evidence_ids'].append(f'experiment:r{R}-search-w14')
    os.makedirs(os.path.join(outdir, 'certificates'), exist_ok=True)
    open(os.path.join(outdir, 'proof.md'), 'w', encoding='utf-8', newline=NL).write(text)
    json.dump(claim, open(os.path.join(outdir, 'claim.json'), 'w', newline=NL), indent=2)
    json.dump({'schema_version': 2, 'certificates': []}, open(os.path.join(outdir, 'certificates', 'manifest.json'), 'w', newline=NL), indent=1)
    print('wrote', outdir, 'proof bytes', len(text.encode()), 'claim', claim['claim'], 'evidence', ev1, ev2)


if __name__ == '__main__':
    main(sys.argv[1])
```

### test_machine.py

```python
"""test_machine.py <w> <trials>: execute the instruction listing (machine.py) at output width w on the real step program and
compare every trial with the reference search (search.py) on the same coins: same outcome code, same pair, and the
counted cost equal to the closed-form ledger evaluated on the trial's path (ledger_path in this file).
Prints one JSON line per trial and a summary."""
import sys, json, hashlib, math
from step import build, P
from campaign import compile_prog
from search import search
from machine import build_program, run, OPS
from sim import choose

CODES = {0: 'ok', 1: 'no-repeat', 2: 'table-full', 3: 'gap-width', 4: 'pos-cap', 5: 'lock-cap', 6: 'start-on-cycle'}


def main(w, trials, MCAP=200):
    N = 1 << w; mask = N - 1
    par = choose(N, MCAP)
    Delta, S, G, d = par['Delta'], par['S'], par['G'], par['d']
    VB = (Delta - 1).bit_length(); WG = 2 * w
    prog = build_program(Delta, S, MCAP, G, G + d - 1, VB, WG, trunc=w)
    L, sp, consts, outscale = build(31, 0)
    F0 = compile_prog(sp, consts)
    ok_all = True
    stats = {'trials': 0, 'agree': 0, 'codes': {}}
    for tr in range(trials):
        h = hashlib.sha256(f'poseidon_mage r31 machine test {w} {tr}'.encode()).digest()
        rw = [int.from_bytes(hashlib.sha256(h + bytes([j])).digest(), 'little') for j in range(4)]
        rho0 = rw[0] & ((1 << 254) - 1); x0 = rw[1] & ((1 << 254) - 1) & mask
        Fm = lambda x: F0((x + rho0) % P) & mask
        # the listing walks whole blocks of 15 while BASE < S: the reference runs the same number of steps
        Sx = 15 * (-(-S // 15))
        code_ref, pair, cnt = search(Fm, x0, Delta, Sx, MCAP, G, d, WG)
        hits = {}
        hc, cost, ninstr, MEM, R = run(prog, rw, hits=hits)
        from machine import path_cost, worst_case
        pc_ = path_cost(prog, hits, hc)
        wc, _, _, _ = worst_case(prog, S, MCAP, G, G + d - 1)
        assert pc_ == cost, (pc_, cost)
        assert cost <= wc, (cost, wc)
        code_m = CODES[hc]
        agree = code_m == code_ref
        if agree and code_ref == 'ok':
            A, B = pair
            # messages written by the listing at MEM[0..3]: check against the reference message map
            ma = L.message((A + rho0) % P); mb = L.message((B + rho0) % P)
            agree = [MEM.get(0), MEM.get(1), MEM.get(2), MEM.get(3)] == [ma[0], ma[1], mb[0], mb[1]] or \
                    [MEM.get(0), MEM.get(1), MEM.get(2), MEM.get(3)] == [mb[0], mb[1], ma[0], ma[1]]
        stats['trials'] += 1; stats['agree'] += agree
        stats['codes'][code_m] = stats['codes'].get(code_m, 0) + 1
        print(json.dumps({'w': w, 'trial': tr, 'machine': code_m, 'reference': code_ref, 'agree': agree, 'cost': cost,
                          'instructions_executed': ninstr, 'worst_case': wc, 'path_formula': pc_, 'steps': cnt['trail_steps'], 'dp': cnt['dp_hits']}), flush=True)
        ok_all &= agree
    print(json.dumps({'summary': stats, 'params': par, 'VB': VB, 'WG': WG, 'listing_instructions': len(prog['code']),
                      'registers': len(prog['regs'])}))
    return ok_all


def stress(w=10, trials=10):
    """force every exit of the listing at small width: cost <= worst case and path formula == counted cost on every trial."""
    from machine import worst_case, path_cost
    N = 1 << w
    configs = [(N, 200, 8, 50, 60, 2 * w), (N, 400, 400, 50, 60, 2 * w), (N // 4, 400, 64, 1, 1, 2 * w),
               (N // 64, 400, 64, 3, 2, 2 * w), (N // 16, 400, 64, 50, 60, 3), (8, 200, 4, 50, 60, 2 * w)]
    seen = {}
    for ci, (Delta, S, MCAP, G, GPOS, WG) in enumerate(configs):
        VB = max(1, (Delta - 1).bit_length())
        prog = build_program(Delta, S, MCAP, G, GPOS, VB, WG, trunc=w)
        wc, _, _, _ = worst_case(prog, S, MCAP, G, GPOS)
        mx = 0
        for tr in range(trials):
            h = hashlib.sha256(b'poseidon_mage r56 stress %d %d %d' % (w, ci, tr)).digest()
            rw = [int.from_bytes(hashlib.sha256(h + bytes([j])).digest(), 'little') for j in range(4)]
            hits = {}
            hc, cost, ni, MEM, R = run(prog, rw, max_instr=10 ** 8, hits=hits)
            assert cost <= wc and path_cost(prog, hits, hc) == cost
            assert max(MEM) < prog['CBASE'] + len(prog['const_vals'])
            seen[CODES[hc]] = seen.get(CODES[hc], 0) + 1
            mx = max(mx, cost / wc)
        print(json.dumps({'config': ci, 'Delta': Delta, 'S': S, 'MCAP': MCAP, 'G': G, 'GPOS': GPOS, 'WG': WG, 'max_cost_over_worst_case': round(mx, 4)}), flush=True)
    print(json.dumps({'exits_seen': seen}))


if __name__ == '__main__':
    if sys.argv[1] == '--stress':
        stress()
    else:
        assert main(int(sys.argv[1]), int(sys.argv[2]))
```

### mk_experiment.py

```python
"""mk_experiment.py <out.py>: write the self-contained organizer experiment program (python-message-pairs-v1).
It concatenates step.py (constants embedded instead of read from a file) and machine.py, and adds a main that, for every
organizer trial seed, runs the complete instruction listing at output width W_BITS with the walk on the low W_BITS bits of the
digest itself, and returns the two messages the listing writes (or nulls when the attempt fails)."""
import sys, os, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
from sim import choose

W_BITS = 10
MCAP = 32
SEARCH = {'w': 14, 'MCAP': 96, 'Delta': 6144, 'n': 171, 'd': 16, 'G': 16, 'S': 187}   # chosen by Lemma 3 at N = 2^14 (sim.choose(2**14, 96))


def main(outp):
    C = json.load(open(os.path.join(HERE, '..', '..', 'pareto', 'orchard-pallas-constants.json')))
    step = open(os.path.join(HERE, 'step.py'), encoding='utf-8').read()
    mach = open(os.path.join(HERE, 'machine.py'), encoding='utf-8').read()
    # step.py: embedded constants, no file access, no organizer import
    step = step.replace("""def load():
    C = json.load(open(CPATH))""", """def load():
    C = EMBEDDED""")
    i = step.index('try:\n    sys.path.insert'); j = step.index('checked = [0]')
    step = step[:i] + 'ODIGEST = None\n' + step[j:]
    step = step[:step.index("if __name__ == '__main__':")]
    mach = mach.replace('from step import build as build_step, P\n', 'build_step = build\n')
    if "if __name__ == '__main__':" in mach:                 # drop the self-test block, keep the functions after it
        i = mach.index("if __name__ == '__main__':"); j = mach.find(chr(10) + 'def ', i)
        mach = mach[:i] + (mach[j + 1:] if j >= 0 else '')
    par = {'Delta': 128, 'S': 60, 'G': 40, 'd': 21, 'n': 39}       # fixed small parameters: a control-flow exercise, not a bound
    emb = {'round_constants': C['round_constants'], 'mds': C['mds']}
    head = ('"""r31_listing.py - organizer experiment (python-message-pairs-v1) for poseidon-orchard-r31-prefix-v1.\n'
            'For each trial seed: coins from SHA-256(seed), the complete search listing of proof Section 3 (machine.py, unchanged\n'
            'except one MUL by OUTSCALE and one AND with the width mask after each step-program instance, so the walk runs on the\n'
            'low %d bits of the digest), executed by the counting interpreter on the real r = 31 step program. A successful\n'
            'attempt returns two distinct canonical messages whose digests agree on the low %d bits (a mask event, not a\n'
            'collision); a failed attempt returns nulls. Observations: the counted cost and the worst-case bound of the listing."""\n'
            % (W_BITS, W_BITS))
    srch = open(os.path.join(HERE, 'search.py'), encoding='utf-8').read()
    camp = open(os.path.join(HERE, 'campaign.py'), encoding='utf-8').read()
    cp_src = camp[camp.index('def compile_prog('):camp.index('def main(')]
    body = ('import sys, json, hashlib\n' + 'EMBEDDED = ' + json.dumps(emb) + '\n' + step + '\n' + mach + '\n' + srch + '\n' + cp_src + '\n' +
            'SEARCH = %s\n' % json.dumps(SEARCH) +
            'W_BITS = %d\nPARAMS = %s\nMCAP_X = %d\n' % (W_BITS, json.dumps(par), MCAP) + '''

def search_experiment(req):
    w, Delta, S, MC, G, d = SEARCH['w'], SEARCH['Delta'], SEARCH['S'], SEARCH['MCAP'], SEARCH['G'], SEARCH['d']
    L, sp, consts, outs = build(31, 0)
    F0 = compile_prog(sp, consts)
    mask = (1 << w) - 1
    out = []
    for t in req['trials']:
        seed = bytes.fromhex(t['seed'])
        rw = [int.from_bytes(hashlib.sha256(seed + bytes([j])).digest(), 'little') for j in range(2)]
        rho0 = rw[0] & ((1 << 254) - 1); x0 = rw[1] & mask
        F = lambda x: F0((x + rho0) % P) * outs % P & mask
        code, pair, cnt = search(F, x0, Delta, S, MC, G, d, 2 * w)
        obs = {'outcome_ok': 1 if code == 'ok' else 0, 'trail_steps': cnt['trail_steps'], 'dp_hits': cnt['dp_hits']}
        if code == 'ok':
            ma = L.message((pair[0] + rho0) % P); mb = L.message((pair[1] + rho0) % P)
            a = ma[0].to_bytes(32, 'little') + ma[1].to_bytes(32, 'little')
            b = mb[0].to_bytes(32, 'little') + mb[1].to_bytes(32, 'little')
            out.append({'trial': t['trial'], 'message_a_hex': a.hex(), 'message_b_hex': b.hex(), 'observations': obs})
        else:
            out.append({'trial': t['trial'], 'message_a_hex': None, 'message_b_hex': None, 'observations': obs})
    sys.stdout.write(json.dumps({'schema_version': 1, 'trials': out}, separators=(',', ':')))


def experiment_main():
    req = json.loads(sys.stdin.read())
    if req.get('experiment_id') == 'r31-search-w%d' % SEARCH['w']:
        return search_experiment(req)
    par = PARAMS
    Delta, S, G, d = par['Delta'], par['S'], par['G'], par['d']
    VB = max(1, (Delta - 1).bit_length())
    prog = build_program(Delta, S, MCAP_X, G, G + d - 1, VB, 2 * W_BITS, trunc=W_BITS, digest_trunc=True)
    wc = worst_case(prog, S, MCAP_X, G, G + d - 1)[0]
    out = []
    for t in req['trials']:
        seed = bytes.fromhex(t['seed'])
        rw = [int.from_bytes(hashlib.sha256(seed + bytes([j])).digest(), 'little') for j in range(4)]
        code, cost, ni, MEM, R = run(prog, rw, max_instr=10 ** 8)
        if code == 0:
            a = MEM[0].to_bytes(32, 'little') + MEM[1].to_bytes(32, 'little')
            b = MEM[2].to_bytes(32, 'little') + MEM[3].to_bytes(32, 'little')
            out.append({'trial': t['trial'], 'message_a_hex': a.hex(), 'message_b_hex': b.hex(),
                        'observations': {'halt_code': code, 'counted_cost': cost, 'worst_case': wc}})
        else:
            out.append({'trial': t['trial'], 'message_a_hex': None, 'message_b_hex': None,
                        'observations': {'halt_code': code, 'counted_cost': cost, 'worst_case': wc}})
    sys.stdout.write(json.dumps({'schema_version': 1, 'trials': out}, separators=(',', ':')))


if __name__ == '__main__':
    experiment_main()
''')
    src = head + body
    open(outp, 'w', encoding='utf-8', newline='\n').write(src)
    print(outp, len(src.encode()), 'bytes', par)


if __name__ == '__main__':
    main(sys.argv[1])
```

### campaign.py

```python
"""campaign.py - collision-rate measurement for premise H1 on the real r = 31 walk map, truncated to w bits.

For each walk: rho0 and x0 from SHA-256("poseidon_mage r31 h1 v1 <w> <walk>") (rho0 reduced mod p, x0 mod 2^w);
iterate x <- F(x) mod 2^w with F the real step program (step.py, verified against the reference permutation)
until the first repeat; record tau (index of the first repeated value). A control runs the same loop with
F replaced by SHA-256 keyed by the walk (a pseudo-random function). For a random function on N = 2^w points
P(tau > t) = prod_{i<t} (1 - i/N); the hazard multiplier c is estimated by maximum likelihood under
P(tau > t) = prod_{i<t} (1 - c i/N) (approximately exp(-c t(t-1)/2N)): c_hat = W / sum tau(tau-1)/(2N).
Usage: python campaign.py <w> <walks> <out.jsonl>
"""
import sys, json, hashlib, math
from step import build, P


def compile_prog(prog, consts):
    lines = ['def F(x):']
    for name, v in consts.items():
        pass
    reg = {}
    for o, d, a, b in prog:
        if o == 'mul':
            lines.append(f'    {d} = {a} * {b} % P')
        elif o == 'add':
            lines.append(f'    {d} = ({a} + {b}) % P')
        elif o == 'alias':
            lines.append('    t0, t1, t2 = n0, n1, n2')
        elif o == 'rename':
            lines.append(f'    {d} = {a}')
    lines.append('    return out')
    env = {'P': P}
    env.update(consts)
    exec('\n'.join(lines), env)
    return env['F']


def main(w, walks, outp):
    N = 1 << w
    mask = N - 1
    L, prog, consts, outscale = build(31, 0)
    base = dict(consts)
    kin = [k for k in consts]                       # the first three constants are the entry offsets K_i (rho0 = 0)
    F0 = compile_prog(prog, base)            # entry offsets with rho0 = 0; the walk feeds x + rho0
    with open(outp, 'a', newline='\n') as fo:
        for wk in range(walks):
            h = hashlib.sha256(f'poseidon_mage r31 h1 v1 {w} {wk}'.encode()).digest()
            rho0 = int.from_bytes(h, 'little') % P
            x0 = int.from_bytes(hashlib.sha256(h).digest(), 'little') & mask
            seen = {}
            x = x0; t = 0
            while x not in seen:
                seen[x] = t
                x = F0((x + rho0) % P) & mask
                t += 1
            tau = t
            # control: keyed SHA-256 function on w bits
            seen = {}; y = x0; t2 = 0
            key = hashlib.sha256(b'control' + h).digest()
            while y not in seen:
                seen[y] = t2
                y = int.from_bytes(hashlib.sha256(key + y.to_bytes(8, 'little')).digest()[:8], 'little') & mask
                t2 += 1
            fo.write(json.dumps({'w': w, 'walk': wk, 'tau': tau, 'tau_control': t2}) + '\n'); fo.flush()


if __name__ == '__main__':
    main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
```

### sim.py

```python
"""sim.py - reduced-width runs of search.py on the real r = 31 walk map truncated to w bits, and on a keyed
SHA-256 control, with parameters chosen by the same success bound (Lemma 3) at N = 2^w.
Records per trial: outcome, recovery lockstep length (mu - a), positioning distance, and checks every returned
pair collides under the truncated map. Usage: python sim.py <w> <MCAP> <trials> <out.jsonl>"""
import sys, json, math, hashlib
from step import build, P
from campaign import compile_prog
from search import search


def bound(N, Delta, n, d, G, MCAP, WG):
    S = n + d
    th_lo = (Delta - S) / N
    th_hi = Delta / (N - S)
    mu = S * th_hi
    tab = 1.0 if MCAP <= mu else math.exp(MCAP - mu - MCAP * math.log(MCAP / mu))
    fail = (math.exp(-n * (n + 1) / (2 * N)) + n / N + math.exp(-th_lo * d) + n * d / N + math.exp(-th_lo * G)
            + math.exp(-th_lo * (G + d)) + tab + S * math.exp(-th_lo * 2 ** WG))
    return 1 - fail


def choose(N, MCAP, target=0.39):
    best = None
    for fr in [0.5 + 0.05 * i for i in range(10)]:
        for kd in [6 + 0.5 * i for i in range(10)]:
            for H in [6 + 0.5 * i for i in range(12)]:
                Delta = max(1, int(fr * MCAP / math.sqrt(N) * N))
                th = Delta / N
                d = int(math.ceil(kd / th)); G = int(math.ceil(H / th))
                lo = None
                step = max(1, int(math.sqrt(N)) // 400)
                prev = -1
                for nn in range(int(0.8 * math.sqrt(N)), int(2 * math.sqrt(N)), step):
                    bb = bound(N, Delta, nn, d, G, MCAP, 40)
                    if bb >= target:
                        lo = nn; break
                    if bb < prev:
                        break
                    prev = bb
                if lo is None:
                    continue
                cost = lo + d + 3 * G + d
                if best is None or cost < best[0]:
                    best = (cost, {'Delta': Delta, 'n': lo, 'd': d, 'G': G, 'S': lo + d, 'bound': bound(N, Delta, lo, d, G, MCAP, 40)})
    return best[1]


def main(w, MCAP, trials, outp):
    N = 1 << w; mask = N - 1
    L, prog, consts, outscale = build(31, 0)
    F0 = compile_prog(prog, consts)
    par = choose(N, MCAP)
    print(json.dumps({'w': w, 'MCAP': MCAP, **par}), flush=True)
    with open(outp, 'a', newline='\n') as fo:
        for tr in range(trials):
            h = hashlib.sha256(f'poseidon_mage r31 search sim v1 {w} {tr}'.encode()).digest()
            rho0 = int.from_bytes(h, 'little') % P
            x0 = int.from_bytes(hashlib.sha256(h).digest(), 'little') & mask
            Freal = lambda x: F0((x + rho0) % P) & mask
            key = hashlib.sha256(b'control' + h).digest()
            Fctl = lambda x: int.from_bytes(hashlib.sha256(key + x.to_bytes(8, 'little')).digest()[:8], 'little') & mask
            rec = {'w': w, 'trial': tr}
            for name, Fm in (('real', Freal), ('control', Fctl)):
                code, pair, cnt = search(Fm, x0, par['Delta'], par['S'], MCAP, par['G'], par['d'], 40)
                if code == 'ok':
                    assert pair[0] != pair[1] and Fm(pair[0]) == Fm(pair[1])
                rec[name] = {'code': code, 'steps': cnt['trail_steps'], 'dp': cnt['dp_hits'],
                             'lock': cnt.get('mu_minus_a'), 'pos': cnt.get('pos_dist')}
            fo.write(json.dumps(rec) + '\n'); fo.flush()


if __name__ == '__main__':
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
```

### plan.py

```python
"""plan.py - success bound and worst-case cost of the one-trail distinguished-point birthday search (r = 31),
float exploration (the final certificate is in cert.py with exact arithmetic).

N = p. Walk x_{i+1} = F(x_i) for a uniformly random F (premise H1 transfers this to the fixed map).
theta = |D| / N for the distinguished set D; theta_lo = (|D| - S) / N, theta_hi = |D| / (N - S).

Model 'A' (the published construction, TheTradoor 3f611f5 / tanctl b810ea13 / Jbenisek 7f88498e):
  fail <= exp(-n(n+1)/2N) + n/N + exp(-theta_lo d) + n d/N + (S theta_hi + 1) exp(-theta_lo gmax) + exp(-TAB)
  cost = S (STEP + DP + LOOP/k) + 3 gmax (STEP + 6) + small
Model 'B' (this entry): recovery needs only the two gaps it walks:
  fail <= exp(-n(n+1)/2N) + n/N + exp(-theta_lo d) + n d/N + 2 exp(-theta_lo G) + n (G + d)/N [short-cycle abort]
          + exp(-TAB) + MCAP^2 / 2^(f+1) [fingerprints] + (S theta_hi + 1) exp(-theta_lo 2^w) [gap field width]
  cost = S (STEP + DP + LOOP/k) + 3 G (STEP + RECSTEP) + small
"""
import math
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
N = P
C31 = 216 + 21 * 31
STEP = 508


def chernoff_log(S, th, cap):
    """log P(Binomial(S, th) > cap) <= cap - mu - cap log(cap/mu) (mu = S th < cap)."""
    mu = S * th
    if cap <= mu:
        return 0.0
    return cap - mu - cap * math.log(cap / mu)


def model(kind, MCAP, theta, n, kd, H, dp_ops, k_unroll, loop=3, tab_min=13.0, f=64, w=120, rec_extra=6):
    S0 = n
    d = kd / theta
    S = n + d
    th_lo = theta - S / N
    th_hi = theta * N / (N - S)
    fail = math.exp(-n * (n + 1) / (2 * N)) + n / N + math.exp(-th_lo * d) + n * d / N
    tabl = chernoff_log(S, th_hi, MCAP)
    if tabl > -tab_min:
        return None
    fail += math.exp(tabl)
    if kind == 'A':
        gmax = H / th_lo
        fail += (S * th_hi + 1) * math.exp(-th_lo * gmax)
        rec = 3 * gmax * (STEP + rec_extra)
    else:
        G = H / th_lo
        fail += math.exp(-th_lo * G) + math.exp(-th_lo * (G + d)) + (MCAP + 1) ** 2 / 2 * (2.0 ** -f + 1 / (theta * N))             + S * math.exp(-th_lo * 2 ** w)
        rec = (3 * G + d) * (STEP + rec_extra)
    succ = 1 - fail
    cost = S * (STEP + dp_ops + loop / k_unroll) + rec
    return succ, cost, {'S': S, 'd': d, 'n': n}


def solve(kind, MCAP, theta, kd, H, dp_ops, k_unroll, target=0.39):
    """least n (bisection on a real n) with succ >= target; returns log2(cost / C)."""
    lo, hi = 2 ** 126.5, 2 ** 127.5
    for _ in range(200):
        mid = (lo + hi) / 2
        r = model(kind, MCAP, theta, mid, kd, H, dp_ops, k_unroll)
        if r is None:
            return None
        if r[0] >= target:
            hi = mid
        else:
            lo = mid
    r = model(kind, MCAP, theta, hi, kd, H, dp_ops, k_unroll)
    return math.log2(r[1] / C31), hi, r


def best(kind, MCAP, dp_ops, k_unroll):
    """grid search over theta (via mean DP count), kd, H."""
    out = None
    for frac in [0.80 + 0.005 * i for i in range(30)]:
        S_guess = 2 ** 126.995
        theta = frac * MCAP / S_guess
        for kd in [8 + 0.25 * i for i in range(12)]:
            for H in ([16 + 0.25 * i for i in range(20)] if kind == 'A' else [8 + 0.25 * i for i in range(16)]):
                r = solve(kind, MCAP, theta, kd, H, dp_ops, k_unroll)
                if r and (out is None or r[0] < out[0]):
                    out = (r[0], {'theta_log2': math.log2(theta), 'frac': frac, 'kd': kd, 'H': H, 'n_log2': math.log2(r[1])})
    return out


if __name__ == '__main__':
    # model A at the published capacity (895,904 table bytes / 32 = 27,997 words), DP test 3 ops, 16-step unrolling
    print('A, MCAP 27997, dp 3, k 16:', best('A', 27997, 3, 16))
    print('B, MCAP 27997, dp 2, k 16:', best('B', 27997, 2, 16))
    print('B, MCAP 42000, dp 2, k 16:', best('B', 42000, 2, 16))
```

### prerun.py

```python
"""prerun.py - local pre-run of both declared experiments (256 trials each), seeds stated here."""
import json, subprocess, sys, hashlib
res = {}
for eid, sec in (('r31-search-w14', 'search'), ('r31-listing-w10', 'listing')):
    seeds = [{'trial': i, 'seed': hashlib.sha256(f'prerun {eid} {i}'.encode()).hexdigest()} for i in range(256)]
    req = json.dumps({'experiment_id': eid, 'trials': seeds})
    p = subprocess.run([sys.executable, 'experiments/r31_listing.py'], input=req.encode(), capture_output=True)
    assert p.returncode == 0, p.stderr[-2000:]
    out = json.loads(p.stdout)
    ok = sum(1 for t in out['trials'] if t['message_a_hex'])
    obs = {}
    for t in out['trials']:
        o = t['observations']
        k = o.get('halt_code', 'ok' if t['message_a_hex'] else '?') if sec == 'listing' else o.get('outcome_ok')
        obs[str(k)] = obs.get(str(k), 0) + 1
    res[eid] = {'ok': ok, 'null': 256 - ok, 'obs': obs}
    print(eid, json.dumps(res[eid]), flush=True)
json.dump(res, open('prerun.json', 'w'), indent=1)
```

## Appendix B. Certificate output (`python cert.py`)

```json
{
 "Delta": 4955463538568564343182868956103890945703936,
 "n": 169297055886635591747237776317843690204,
 "d": 55495557539318368702682515302776833,
 "G": 56955966948247799215295948946145281,
 "MCAP": 30250,
 "S": 169352551444174910115940458833146467037,
 "theta_log2": -112.17000000000002,
 "success_lower_bound": "0.390002412718204851215962348116436939798034727536294437283761922349149876917950045637033753",
 "success_at_n_minus_1": "0.390002412718204851215962348116436939794471865685040769666802767109147722942300481023760971",
 "fail_terms": {
  "no repeat within n steps": "6.095398e-01",
  "start on the cycle (mu = 0)": "5.848312e-39",
  "cycle shorter than d": "3.245553e-04",
  "no DP in the first d cycle values": "7.487614e-05",
  "lockstep cap: mu - a > G": "5.831409e-05",
  "positioning cap: back-gap > G + d - 1": "4.366334e-09",
  "table overflow (more than MCAP DPs)": "1.860382e-12",
  "gap field width: a DP gap >= 2^WG": "1.693526e-47"
 },
 "W_ops": 86520250388295239880252848728098231438593,
 "ledger": {
  "setup (constants, table zeroing, coins)": 155759,
  "trail: 11290170096278327341062697255543097803 blocks x 7653": 86403671746818039141152822096671327486360,
  "DP handler: 30250 insertions (stub, preamble, scan of c = 0..MCAP-1 entries, insert)": 15557121250,
  "last DP call: scan of MCAP entries, then the larger of overflow and recovery (second scan, positioning cap, lockstep cap, output)": 116578641477200739100026349936369964568,
  "preprocessing: derivation of the program constants (< 2^24 operations), charged at an over-bound of 2^48": 281474976710656
 },
 "time_log2": 126.23027345271622,
 "claim_time_log2": 126.23028,
 "memory_bytes": 1047420,
 "memory_regions": {
  "table: DP values 30250 x 142 bits + gaps 30250 x 120 bits, packed, + 1 spare word (30961 words)": 990752,
  "start word x_0": 32,
  "program: 9063 instructions x 4 bytes (5-bit opcode, three 9-bit fields)": 36252,
  "constant memory: 293 words (205 step constants incl. the 3 entry offsets, parameters, masks, jump targets)": 9376,
  "register file: 344 registers of 256 bits (every register the listing names)": 11008
 },
 "memory_slack": 1156,
 "memory_log2": 19.998408627080998
}
```

Output of `python step.py 1 2 7 31` (against `verifier/poseidon.py`, the archived organizer verifier):

```
r=1: step program 148 field operations (55 additions, 93 multiplications); 136 + 12 r = 148; 55 constants; verified against the reference permutation at 8 points
r=2: step program 160 field operations (60 additions, 100 multiplications); 136 + 12 r = 160; 60 constants; verified against the reference permutation at 8 points
r=7: step program 220 field operations (85 additions, 135 multiplications); 136 + 12 r = 220; 85 constants; verified against the reference permutation at 8 points
r=31: step program 508 field operations (205 additions, 303 multiplications); 136 + 12 r = 508; 205 constants; verified against the reference permutation at 8 points
```

Output of `python test_machine.py w16 <trials>` (machine_test_w16.txt): every trial compares the listing with search.py on the same coins (outcome and both messages), the counted cost with the path formula, and the cost with the worst-case ledger:

```
{"w": 16, "trial": 0, "machine": "no-repeat", "reference": "no-repeat", "agree": true, "cost": 563016, "instructions_executed": 489943, "worst_case": 890801, "path_formula": 563016, "steps": 300, "dp": 154}
{"w": 16, "trial": 1, "machine": "ok", "reference": "ok", "agree": true, "cost": 508651, "instructions_executed": 440959, "worst_case": 890801, "path_formula": 508651, "steps": 260, "dp": 144}
{"w": 16, "trial": 2, "machine": "ok", "reference": "ok", "agree": true, "cost": 79401, "instructions_executed": 71790, "worst_case": 890801, "path_formula": 79401, "steps": 82, "dp": 35}
{"w": 16, "trial": 3, "machine": "ok", "reference": "ok", "agree": true, "cost": 542288, "instructions_executed": 472312, "worst_case": 890801, "path_formula": 542288, "steps": 299, "dp": 147}
{"w": 16, "trial": 4, "machine": "ok", "reference": "ok", "agree": true, "cost": 49544, "instructions_executed": 44371, "worst_case": 890801, "path_formula": 49544, "steps": 52, "dp": 22}
{"w": 16, "trial": 5, "machine": "ok", "reference": "ok", "agree": true, "cost": 372447, "instructions_executed": 325725, "worst_case": 890801, "path_formula": 372447, "steps": 219, "dp": 118}
{"w": 16, "trial": 6, "machine": "ok", "reference": "ok", "agree": true, "cost": 484747, "instructions_executed": 423695, "worst_case": 890801, "path_formula": 484747, "steps": 286, "dp": 136}
{"w": 16, "trial": 7, "machine": "ok", "reference": "ok", "agree": true, "cost": 487439, "instructions_executed": 425732, "worst_case": 890801, "path_formula": 487439, "steps": 285, "dp": 137}
{"w": 16, "trial": 8, "machine": "no-repeat", "reference": "no-repeat", "agree": true, "cost": 578982, "instructions_executed": 503086, "worst_case": 890801, "path_formula": 578982, "steps": 300, "dp": 157}
{"w": 16, "trial": 9, "machine": "ok", "reference": "ok", "agree": true, "cost": 180048, "instructions_executed": 159598, "worst_case": 890801, "path_formula": 180048, "steps": 138, "dp": 73}
{"w": 16, "trial": 10, "machine": "ok", "reference": "ok", "agree": true, "cost": 529202, "instructions_executed": 460554, "worst_case": 890801, "path_formula": 529202, "steps": 292, "dp": 145}
{"w": 16, "trial": 11, "machine": "ok", "reference": "ok", "agree": true, "cost": 454044, "instructions_executed": 398511, "worst_case": 890801, "path_formula": 454044, "steps": 287, "dp": 130}
{"w": 16, "trial": 12, "machine": "ok", "reference": "ok", "agree": true, "cost": 223393, "instructions_executed": 199831, "worst_case": 890801, "path_formula": 223393, "steps": 186, "dp": 80}
{"w": 16, "trial": 13, "machine": "ok", "reference": "ok", "agree": true, "cost": 521848, "instructions_executed": 453874, "worst_case": 890801, "path_formula": 521848, "steps": 285, "dp": 145}
{"w": 16, "trial": 14, "machine": "ok", "reference": "ok", "agree": true, "cost": 289030, "instructions_executed": 254381, "worst_case": 890801, "path_formula": 289030, "steps": 195, "dp": 100}
{"w": 16, "trial": 15, "machine": "no-repeat", "reference": "no-repeat", "agree": true, "cost": 552542, "instructions_executed": 481321, "worst_case": 890801, "path_formula": 552542, "steps": 300, "dp": 152}
{"w": 16, "trial": 16, "machine": "ok", "reference": "ok", "agree": true, "cost": 496748, "instructions_executed": 429732, "worst_case": 890801, "path_formula": 496748, "steps": 244, "dp": 143}
{"w": 16, "trial": 17, "machine": "no-repeat", "reference": "no-repeat", "agree": true, "cost": 628716, "instructions_executed": 544027, "worst_case": 890801, "path_formula": 628716, "steps": 300, "dp": 166}
{"w": 16, "trial": 18, "machine": "no-repeat", "reference": "no-repeat", "agree": true, "cost": 526952, "instructions_executed": 460256, "worst_case": 890801, "path_formula": 526952, "steps": 300, "dp": 147}
{"w": 16, "trial": 19, "machine": "ok", "reference": "ok", "agree": true, "cost": 158246, "instructions_executed": 141126, "worst_case": 890801, "path_formula": 158246, "steps": 130, "dp": 65}
{"summary": {"trials": 20, "agree": 20, "codes": {"no-repeat": 5, "ok": 15}}, "params": {"Delta": 33280, "n": 280, "d": 12, "G": 12, "S": 292, "bound": 0.3906596838404599}, "VB": 16, "WG": 32, "listing_instructions": 9022, "registers": 345}
```

Output of `python test_machine.py w20 <trials>` (machine_test_w20.txt): every trial compares the listing with search.py on the same coins (outcome and both messages), the counted cost with the path formula, and the cost with the worst-case ledger:

```
{"w": 20, "trial": 0, "machine": "no-repeat", "reference": "no-repeat", "agree": true, "cost": 1029161, "instructions_executed": 951366, "worst_case": 1401638, "path_formula": 1029161, "steps": 1170, "dp": 158}
{"w": 20, "trial": 1, "machine": "no-repeat", "reference": "no-repeat", "agree": true, "cost": 971741, "instructions_executed": 904099, "worst_case": 1401638, "path_formula": 971741, "steps": 1170, "dp": 147}
{"w": 20, "trial": 2, "machine": "no-repeat", "reference": "no-repeat", "agree": true, "cost": 1073505, "instructions_executed": 987870, "worst_case": 1401638, "path_formula": 1073505, "steps": 1170, "dp": 166}
{"w": 20, "trial": 3, "machine": "ok", "reference": "ok", "agree": true, "cost": 66697, "instructions_executed": 62430, "worst_case": 1401638, "path_formula": 66697, "steps": 89, "dp": 14}
{"w": 20, "trial": 4, "machine": "ok", "reference": "ok", "agree": true, "cost": 864741, "instructions_executed": 809648, "worst_case": 1401638, "path_formula": 864741, "steps": 1103, "dp": 128}
{"w": 20, "trial": 5, "machine": "ok", "reference": "ok", "agree": true, "cost": 921162, "instructions_executed": 853421, "worst_case": 1401638, "path_formula": 921162, "steps": 1062, "dp": 143}
{"summary": {"trials": 6, "agree": 6, "codes": {"no-repeat": 3, "ok": 3}}, "params": {"Delta": 143360, "n": 1125, "d": 44, "G": 44, "S": 1169, "bound": 0.39021147264965095}, "VB": 18, "WG": 40, "listing_instructions": 9022, "registers": 345}
```

Output of `python test_machine.py --stress` (machine_stress.txt): forced exits, cost at most the worst case and equal to the path formula each time:

```
{"config": 0, "Delta": 1024, "S": 200, "MCAP": 8, "G": 50, "GPOS": 60, "WG": 20, "max_cost_over_worst_case": 0.0351}
{"config": 1, "Delta": 1024, "S": 400, "MCAP": 400, "G": 50, "GPOS": 60, "WG": 20, "max_cost_over_worst_case": 0.0475}
{"config": 2, "Delta": 256, "S": 400, "MCAP": 64, "G": 1, "GPOS": 1, "WG": 20, "max_cost_over_worst_case": 0.2128}
{"config": 3, "Delta": 16, "S": 400, "MCAP": 64, "G": 3, "GPOS": 2, "WG": 20, "max_cost_over_worst_case": 0.6938}
{"config": 4, "Delta": 64, "S": 400, "MCAP": 64, "G": 50, "GPOS": 60, "WG": 3, "max_cost_over_worst_case": 0.5504}
{"config": 5, "Delta": 8, "S": 200, "MCAP": 4, "G": 50, "GPOS": 60, "WG": 20, "max_cost_over_worst_case": 0.5335}
{"exits_seen": {"table-full": 10, "ok": 13, "start-on-cycle": 1, "pos-cap": 7, "lock-cap": 2, "no-repeat": 22, "gap-width": 5}}
```
