# Weighted selected-output C39 construction for 39-step SHA-256

## 1. Target and output

The construction targets `sha256-r39-prefix-v1`. It uses the standard SHA-256 IV, FIPS 180-4 padding, feed-forward, rounds 0 through 38 in every compression, and all 256 output bits. A success consists of two distinct 128-byte messages `M0 || M1` and `M0 || M1'`. Both messages use the same first block. Their padding block is identical.

For a first-block chaining value `H = F39(IV, M0)`, the solver constructs `M1 != M1'` such that `F39(H, M1) = F39(H, M1')`. Feed-forward therefore gives the same chaining value after block two. The common padding block preserves equality.

## 2. Fixed C39 parameters

The construction uses one 39-step core, one coupling value `j = 0xadc6d187`, and a deterministically constructed list of 299 values of `A3` in 50 classes of equal `X10(A3)`. A deterministic cross-j q-aware rule constructs all fifty labels and 299 values. The list SHA-256 is `5532657e4e9259c964f9b58829512e4c4036fad6cc3dda3d007192b95b4fadbd`. Published j ranks ninth by exact radius-eight mass, then first in both q-aware selection stages. The core fixes both executions from step 12 through step 17 and fixes `W16`, `W17`, `W16'`, and `W17'`. The message XOR is nonzero in words 8 through 12.

The runtime stores at most 4,096 bytes of fixed parameters. This envelope includes the core, `j`, the `A3` list, the difference masks, and all derived constants. The claim records this entire envelope as nonuniform advice even though some values are public algorithm constants.

## 3. The inverse table

Define `s(z) = sigma0(z) - z mod 2^32`. Preprocessing makes two complete `2^32` passes over `z`: one pass counts high-28-bit buckets, and one pass writes the values. It groups values by `s(z) >> 4`. The resident table stores `2^32` four-byte values and `2^28 + 1` four-byte offsets. The final endpoint `2^32` is implicit because it does not fit in a four-byte offset. Exact resident size is `2^34 + 2^30 + 4 = 18,253,611,012` bytes, or 17 GiB plus four bytes.

A lookup scans every entry between its two offsets and recomputes the full 32-bit key. Bucket size has mean 16 for a uniform target; 16 is not a scan cap. The recorded maximum full-key fibre is 14, so a bucket, which covers 16 full keys, has at most 224 entries. The cost proof charges 224 entries for every lookup.

The recorded exhaustive histogram has exactly `2^32` targets and `2^32` preimages, with its last nonzero bin at 14. The admitted native experiment instead reruns the full `2^32` W9 predicate census and bounded low-memory inverse cases, including sixteen complete exact-X counts. It does not rebuild the 17-GiB table.

## 4. One fresh-first-block trial

Each trial draws a fresh uniform 64-byte block `M0` and a fresh uniform `A0`. It computes `H = F39(IV, M0)`.

All following arithmetic is modulo `2^32`. `A_t,E_t` denote registers after step `t`; `H0..H3=A_-1..A_-4` and `H4..H7=E_-1..E_-4`. Define

```
E0 = A0 + H3 - Sigma0(H0) - Maj(H0,H1,H2)
c0 = -Sigma0(H0)-Maj(H0,H1,H2)-H7-Sigma1(H4)-Ch(H4,H5,H6)-K0
phi = -Sigma0(A0)-Maj(A0,H0,H1)-H6-Sigma1(E0)-Ch(E0,H4,H5)-K1
E1 = A1 + H2 - Sigma0(A0) - Maj(A0,H0,H1)
psi = -Sigma0(A1)-Maj(A1,A0,H0)-H5-Sigma1(E1)-Ch(E1,E0,H4)-K2
W0 = A0 + c0; W1 = A1 + phi; W2 = A2 + psi.
```

For core registers, set

```
e7 = A7 - Sigma0(A6) - Maj(A6,A5,A4)
e6(A3) = A6 - Sigma0(A5) - Maj(A5,A4,A3)
J(A2,A3) = Maj(A4,A3,A2) - Ch(E8,A3+e7,A2+e6(A3))
X10(A3) = E10-A6-e6(A3)-Sigma1(E9)-Ch(E9,E8,A3+e7)-K10
X9 = E9 - 2*A5 + Sigma0(A4) - Sigma1(E8) - K9
K16* = W16_core - sigma1(W14_core)
K17* = W17_core - sigma1(W15_core).
```

Stage 1 fixes `J=j` and queries the exact fibre

`s(W1) = K16* - X9 - W0 - phi - j`.

Every returned `u=W1` fixes `A1=u-phi` and `W9=K16*-W0-sigma0(u)`. The solver keeps the candidate only if `W9 XOR (W9+d9)` equals the fixed word mask and `sigma0(W9+d9)-sigma0(W9)` equals the required expansion difference. Both are necessary prefix conditions.

For each survivor and each of the 50 `X10` classes, Stage 2 queries

`s(W2) = K17* - X10(class) - W1 - psi`.

Every returned `W2` fixes `A2=W2-psi`. For each `A3` in that class, the solver tests `J(A2,A3)=j`, then runs the complete predicate in Section 5. Fibre enumeration scans the full bucket and emits every matching `z`; it does not keep only one preimage.

The solver completely enumerates every prefix output. If the count X is positive, exact one-item reservoir sampling chooses one ordinal uniformly from 0 through X-1. Only that output is reconstructed into both second blocks, executed through both complete 39-step compressions, and compared on all eight feed-forward words. It returns the two complete messages only after this final comparison succeeds.

## 5. Why the two lookups are complete

Given `H` and `(A0,A1,A2,A3)`, reconstruct the first second-block words with the following exact loop. Initialize `A_-1..A_-4=H0..H3` and `E_-1..E_-4=H4..H7`; use the candidate for `A0..A3` and the fixed core for `A4..A15`. For `t=0..15`, compute

```
E_t = A_t + A_(t-4) - Sigma0(A_(t-1)) - Maj(A_(t-1),A_(t-2),A_(t-3))
W_t = E_t - A_(t-4) - E_(t-4) - Sigma1(E_(t-1))
      - Ch(E_(t-1),E_(t-2),E_(t-3)) - K_t.
```

Set `M1=(W0..W15)` and `M1'=M1 XOR Delta`, where the admitted source lists all 16 masks. Recompute both executions. The complete relaxed prefix predicate requires: the submitted signed/fixed-bit masks on `A_t,E_t,W_t` for `t=12..17`; every submitted two-bit relation whose endpoints lie in those steps; exact equality to both core trajectories for `t=12..17`; the four matching words `W16,W17,W16',W17'`; and expansion conditions S1-S9:

```
S1  d sigma1(W16) + d W11 = 0
S2  d sigma1(W17) + d W12 = 0
S3  d W16 + d sigma0(W8) = 0
S4  d W17 + d sigma0(W9) + d W8 = 0x03010000
S5  d sigma0(W10) + d W9 = 0
S6  d sigma0(W12) + d W11 = 0
S7  d W24 + d sigma0(W16) = 0
S8  d sigma0(W17) + d W16 = 0
S9  2^30 - d sigma0(W11) - d W10 is a signed sum over the set bits of sigma1(0x03010000).
```

Here `d f(x)=f(x')-f(x)` and all additions are modulo `2^32`. The frozen exact-X replay uses these characteristic strings, relations, lookup equations and the complete predicate. The admitted source recomputes the coordinate algebra, exact J fibres and exact X at sixteen declared points, including eight fresh SIS successes weighted in the same sandbox process. It does not claim to reproduce the full 130,048-record, 22-GiB X campaign.

Fix `H` and `A0`. Any valid prefix solution has one value `W1`. Its first matching equation places that value in the exact fibre returned by Stage 1. The early `W9` tests are necessary prefix conditions, so they remove no valid solution.

The valid solution's `A3` belongs to exactly one `X10` class. Its second matching equation places its `W2` in that class's exact fibre. The equation fixes `A2`; `J = j` and the full prefix check then accept it. Conversely, each emitted prefix passes both equations and every deterministic condition through step 17. The final compression comparison prevents a false collision.

The complete solver checks `H=F39(IV,M0)`, full reconstruction, the complete predicate, both lookup targets, both W9 filters, `J=j`, the `X10` class, and `W10=X10(A3)-A2`. Complete enumeration determines X before the selected output is tested. The deterministic bound `14*14*299=58604` limits the temporary output buffer. Exactly one output is rebuilt and tested when X is positive.


## 6. Itemized parameter construction

The construction charges four independent one-time allowances. They are deliberately double-counting where scopes overlap. Each remains an explicit exploratory premise unless stated otherwise.

**A_C, Table-23 characteristic and upper target: `2^78` target units.** The exact upper construction inherited from submission `7c4da9b7-54cc-4c6a-9754-883588e3b019` starts from the Table-23 conditions. Steps 10 through 15 carry 384 state bits under 350 differential, carry and schedule conditions, leaving `2^34` dense candidates. For each candidate, SHA-256 step inversion determines steps 9 through 0 and the chaining value without search. Exact bit-by-bit DFS enumerates the row-16 and row-17 fibres in fewer than `2^2` target compressions per candidate, giving the submitted `2^36` construction bound and at most `2^16` bytes. The organizer evidence executes the exact downward inversion, the two fibre solvers on the published base, and a 256-candidate slice. It does not execute all `2^34` candidates or rediscover the characteristic. That submission is evaluated valid and `plausible_not_refuted`, not human-accepted. This candidate charges `2^78`, 42 bits above its stated construction, and preserves the full-space and characteristic-discovery gap as H3A.

**A_U, arbitrary-A10 upper reconstruction: `2^72` target units.** U39 is a 57,504-variable bit-vector CNF whose primary variables are the common CV and sixteen block words; the partner is derived from the characteristic. It contains no pin to the published primary CV or message. An emitter adds the 32 unit clauses for an arbitrary unsigned A10. Each value receives one CPU, 3 GiB, a 300-second solver kill, caps of `2^19` conflicts and `2^20` decisions, independent scalar decoding, and a complete 2,812-core-second envelope including generation and checking. Scanning all `2^32` values at the declared `2^40` word-operations per core-second costs exactly

```text
2^32 * 2812 * 2^40 / C39 = 2^72,  where C39=2812.
```

At `A10=0x24b9a00a`, two fresh capped runs recover byte-identical scalar-valid models with an upper signature matching the frozen target and a primary CV/message different from the published primary. A non-target A10 also produces a distinct scalar-valid upper, exercising the general emitter. Separately, the exact unsigned formula `A10 < 0x24b9a00a` is UNSAT in Kissat404 and CaDiCaL300, in 117.78 and 197.88 wall-seconds, while the target is SAT. Thus the target is the least unsigned admitted A10 subject to the encoding and solver verdicts. Neither backend emitted a DRAT/LRAT certificate, and a target-independent 32-query greedy minimizer timed out UNKNOWN on bit 31. The full sweep was not executed, and the seconds conversion is H3B rather than a strict instruction trace.

**A_L, lower core and selector: `2^90` target units.** The fixed three-stage lower SAT recipe has 32,916, 32,916 and 32,756 variables, and 118,402, 118,403 and 117,778 clauses. All three assignments replay byte for byte. A separate evaluator checks all 354,583 clauses, 983,289 literal occurrences, every relaxed condition, S1-S9 and all 54 applicable row-12-through-17 relations. The resulting selector input core has SHA-256 `fdb66daab2199aa45688259422b5368b849740df1b240412d587f193be6f2501`. Conditional on that core, exact radius-eight counts rank 256 deterministic j candidates. The top sixteen receive a complete first q-aware screen and the top four receive the second. The rule enumerates 240,530,768 A3 records and executes 506,008,224 prefix tests, including every loser. It selects `j=adc6d187`, fifty `X10` labels and the 299-entry list above. The supported selector envelope is 58,161,946,387,712 primitives. A strict native audit completed a matching stage-3 trace but not matching traces for stages 1 and 2; its pessimistic 1,024-operation source sensitivity is `2^74.4690432754` target units before extras. `A_L=2^90` adds 15.5309567246 bits, but the complete x86/VEX-to-v5 conversion remains H3C.

**DEV, all other construction work: `2^90` target units.** The dated interval 2026-10-21T00:00:00Z through 2026-10-23T00:00:00Z contains the local construction work. The recorded host has 16 logical Ryzen 7 3700X CPUs and one GTX 1070 Ti; the ledger instead charges `2^20` CPU threads and `2^10` accelerators for `2^18` seconds, at `2^40` and `2^47` word operations per device-second, then multiplies all work by `2^10` for operating-system service, I/O, compilation, setup, instrumentation and accounting. This is `2^88.169925...` word operations, or `2^76.712544...` target units, leaving 13.287455 bits below DEV. Model authorship is outside the classical construction. Work outside the interval or host requires an expanded ledger. The inflated rates are conservative premises, not measured traces; this is H3D.

The cross-j rule was defined after earlier development outcomes, so none of those q or tail results enters the binding endpoint. The complete PB=0 confirmation protocol was hash-frozen later, before its new trial and tail outcomes, with separate randomness domains.

## 7. Uniform selection and the selected-law correction

Let `O(H,A0)` be the complete prefix-output set of a fresh trial and let
`X(H,A0)=|O(H,A0)|`. If X is positive, one-item reservoir sampling processes
the deterministic output order and retains each ordinal with probability
`1/X`. Induction proves this for every finite positive X. The admitted source
checks every success mask for output counts one through eight.

The old unweighted tail estimate did not yet target this law. Fix one selected
prefix coordinate `C=(A0,A1,A2,A3)`. The six schedule words
`U=(W18,...,W23)` parameterize its matching class:

1. Backward schedule recurrence determines W7 through W2 from U.
2. The fixed W16 and W17 equations determine W1 and W0.
3. Eight inverse SHA-256 steps determine H and the second block.

Running the operations forward recovers U, so this is a bijection. Under the
explicit ideal-uniform matching-class premise, uniform U is the base law. The
actual reservoir-selected density within the class is proportional to `1/X`.
For terminal success indicator Y, define

```text
N_C = E_U[Y/X]
D_C = E_U[1/X].
```

The desired conditional selected mean is `N_C/D_C`. Since the fixed coordinate
is always one output, `X>=1`, hence `0<D_C<=1` and `N_C/D_C>=N_C`. The numerator
alone gives a conservative lower quantity without estimating D.

For one SIS path, let q be its pre-final importance factor, K=`2^18`, and let
`H_1,...,H_s` be its successful final candidates. Its corrected contribution is

```text
q/K * sum_(i=1)^s 1/X(H_i,A0).
```

The archived unweighted path value is `q*s/K`. The correction uniformly samples
`min(512,s)` success records without replacement and multiplies the archived
path value by their sample mean of `1/X`. Algorithm R uses a separate public
randomness domain for every block and path. This estimator is unbiased for the
corrected path contribution conditional on the archived SIS run.

The fixed-IV first-block law need not be uniform. If its density is `mu(H)`, the
correct weight is proportional to `mu(H)/X`, not merely `1/X`. The claim keeps
uniform matching-class transfer as H1 instead of hiding it in the correction.

## 8. Frozen weighted evidence and the DKW bound

The fresh PB=0 campaign contains exactly `2^24` trials, 450 outputs and 406 nonempty trials. Its exact one-sided ideal-iid 99.5% binomial lower endpoint is

```text
P(X>0)_L = 0.0000212179473118378.
```

The first 64 selected outputs in trial order were frozen before their tail outcomes. Each block has 512 SIS paths and `2^18` proposals at every reached free row. Across all blocks, 254 paths have positive terminal weight and contain 15,661,579 successful final vectors. Before any multiplicity was inspected, Algorithm R froze at most 512 terminal successes from every positive path, giving 130,048 vectors. The full PB=0 enumerator reconstructed H, reran the complete prefix search and required the selected coordinate exactly once. The multiplicity histogram is

```text
X=1    120,634
X=2      9,383
X=3         31
total   130,048
sum X   139,493
```

An independent audit replayed every selection and block calculation. The admitted low-memory implementation also recomputes exact X and H for eight frozen overlap records and eight freshly generated same-process SIS records. Those bounded points test the implementation; they do not replace the 130,048-record campaign. The multiplicity JSONL SHA-256 is `73e75d554872595b91f30bfe92f11db0954e42763cb4e151a206aa5c1b8013f9`.

For one positive SIS path with pre-final importance factor q, `K=2^18` and successful candidates `H_1,...,H_s`, the corrected target is

```text
q/K * sum_(i=1)^s 1/X(H_i,A0).
```

The archived path weight is `q*s/K`. With ideal rejection sampling, multiplying it by the Algorithm-R sample mean of `1/X` is unbiased for that path target because the sample is uniform without replacement. Zero-success paths contribute zero. The archived endpoint caps each helper draw at sixteen attempts and fails the entire block closed to `Z=0` on exhaustion. The executed Z is therefore pointwise no greater than the ideal unbiased statistic, which preserves a conservative lower bound. The cap failure is below `2^-736` per tail draw and below `2^-696` even over `2^40` draws. Averaging all 512 paths gives one nonnegative whole-block variable. Thinning the declared iid fresh-trial stream by `X>0`, then using independent tail coins, makes the 64 blocks iid under that ideal experiment. H1 separately handles fixed-IV transfer.

For `alpha=0.005`, the one-sided Dvoretzky-Kiefer-Wolfowitz/Massart inequality gives, simultaneously for all thresholds t,

```text
epsilon = sqrt(log(1/0.005)/(2*64))
        = 0.2034529538398411568822745807...
        < 0.203452953839842.
P[Z >= t] >= 1 - count(Z_i < t)/64 - epsilon.
E[Z] >= t * P[Z >= t].
```

The event is simultaneous in t, so choosing the best observed threshold adds no multiple-testing penalty. The optimizer selects the 25th ascending order statistic. Exactly 24 blocks are strictly below it:

```text
t observed             1.538405597029847551021575927734375e-23
t binding, 1ppm down   1.538404058624250521174024906158447265625e-23
survival lower         0.421547046160158
tail mean lower        6.4850968671385134838601336609171013369152069091796875e-24
```

Archived path weights use binary64. Every positive weight is at least `2^-108` and its at-most-six-operation Decimal/exact relative ratio is bounded above by `1.0000000000000007771561...`. Multiplying that bound by `0.999999` is `0.9999990000000007771553... < 1`, so the one-part-per-million guard is conservative for this computation.

Combining the DKW event with the exact one-sided 99.5% nonempty event by a union bound gives simultaneous confidence at least 0.99 and

```text
lambda_L
  = 0.0000212179473118378
    * 6.4850968671385134838601336609171013369152069091796875e-24
  = 1.376004436391093605946960115075346160866308669737053319549560546875e-28
  = 2^-92.5535015353896287... .
```

The earlier nested-bootstrap endpoint `1.8342433461896596e-23` is retained only as historical sensitivity. It does not enter lambda, N, work or score. The DKW statement is distribution-free over Z, conditional on iid whole blocks and the ideal SIS/Algorithm-R construction; fail-closed cap exhaustion can only reduce Z. Public deterministic seeds establish reproducibility, not ideal coins.

## 9. Success and work wrapper

The wrapper fixes

```text
N = 5,273,750,237,090,459,099,267,675,734
```

ideal fresh-trial slots. Since `(1-lambda_L)^N <= exp(-N*lambda_L)`, untruncated success is at least 0.516. The implementation stops before

```text
8 * 64 * N = 2700160121390315058825049975808
```

target units. Under H4, expected work is at most `64*N`, so Markov bounds work exhaustion by 1/8. Across all N slots, sixteen-attempt reservoir rejection failure is at most

```text
N * 58604 * (58604/2^64)^16
  = 3.3278781218...e-200 = 2^-662.651... .
```

Subtracting both failure terms leaves success above 0.391 and therefore above 0.39, without assuming independence between success and work.

Preprocessing is itemized as

```text
A_C       2^78 =    302231454903657293676544
A_U       2^72 =      4722366482869645213696
A_L       2^90 = 1237940039285380274899124224
DEV       2^90 = 1237940039285380274899124224
finite                 1812688333559
----------------------------------------------
total      2476187032392148889425472247
log2       91.000178850870371147895...
```

`preprocessing_log2=91.00018` rounds upward. Adding preprocessing to online work gives

```text
2702636308422707207714475448055 target units
log2 = 101.092210229252875145942... .
```

The submitted `time_log2=101.09222` rounds upward.

## 10. Memory and normalized cost

The inverse table has 18,253,611,012 resident bytes and its build arrays peak at 19,327,352,836 bytes. The exact-X replay peaked at 19,367,407,616 cgroup bytes with no high, max, OOM or swap event. U39 and lower-core phases run sequentially under 3 GiB, and their intermediate formulas, assignments and traces are discarded before the online phase. The claim retains 22 GiB:

```text
memory bytes       23622320128
memory log2 bytes  34.459431618637297256199...
normalized score   101.09222 + 34.459431618637297... - 20
                 = 115.551651618637297... .
```

This is 2.563488381362703 bits below the current valid r39 review score 118.11514. Against the earlier 118.14514 reference frozen in the binding analysis it is 2.593488381362703 bits lower. The newer frontier is used for the submission comparison; no construction from it is reused.

## 11. Conditional analytic H4 sensitivity

The native evidence reruns all `2^32` W9 words and finds exactly `2^26` survivors. It also recomputes all 299 J fibres, whose sizes sum to 7,531,010,048. Under ideal-uniform independent CV words, H7 is a modular translation of the Stage-1 target. After W9 is fixed, A1 is independent of H6, and H6 is a modular translation of every Stage-2 target. Complete inversion gives

```text
stage-1 preimages       1
W9 survivors            1/64
stage-2 lookups          50/64
stage-2 preimages        50/64
J checks                 299/64
J passes                 7531010048 / 2^38
```

A conservative charge for all remaining branches gives 9.0848191316275305588 target units per trial under that ideal-CV law. The submitted mean remains 64. The gap is deliberate, but the transfer to chaining values generated from the fixed IV is H4: a uniform first block does not prove uniform independent CV words.

## 12. Admitted executable evidence

`experiments/weighted39.py` is a single 54,623-byte UTF-8 source, below the 64-KiB total source limit. It embeds two disclosed freestanding native images and public inputs, loaded through anonymous memfd objects inside the pinned networkless organizer container. The manifest has fifteen entries, below the sixteen-entry limit. Its SHA-256 is `142fb83210f74b6f0b9a38617c5e9097e75de385f3370aff8423f30d4836c95a`.

The experiments perform eight exhaustive W9 slices covering all `2^32` words; 256 coordinate-algebra cases and all J fibres; one fresh 512-path SIS run; bounded exact-R, exact-X overlap and fresh same-process exact-X cases; and the selected-law arithmetic. The arithmetic entry embeds all 64 block values and independently recomputes epsilon, simultaneous threshold selection, the 1ppm guard, tail mean, lambda, N, four preprocessing allowances, total work, upward rounding, both reference margins, reservoir failure and conditional H4 sensitivity.

Every declared trial returns null messages because this finite evidence run is not expected to find an ordinary collision. Numeric observations remain participant data. The organizer checks the selected-target predicate for returned pairs and labels the computations as evidence rather than full attack-cost inference. The two complete organizer replays are byte-identical, and each entry is itself executed twice in fresh isolated containers with byte-identical stdout.

## 13. Dependencies and limits of reuse

The dependency declaration names:

- `82f61c7f-89e6-437a-9f02-f5b21b7a8206`, the direct selected-output lineage supplying complete PB=0 enumeration, one-output reservoir semantics and the fixed C39 selector lineage;
- `7c4da9b7-54cc-4c6a-9754-883588e3b019`, for the Table-23 base construction and upper trajectory; and
- `69616879-8f53-4bff-a45d-a2bb7367418e`, the reviewed direct derivative carrying the same r39 upper and implementation lineage.

This candidate replaces 82f61c7f's unweighted/nominal tail with exact-X weighting and the whole-block DKW bound. Dependencies provide attribution, not cost waivers. The candidate separately charges A_C, A_U, A_L, DEV and all finite evidence. It does not use the later 022fed5e construction; that submission appears only as the live score comparison in Section 10.

## 14. Ordinary-message validity

On success the byte strings are `M0 || M1` and `M0 || M1'`, each 128 bytes before padding. They share M0 and differ in words 8 through 12 of block two. Both start from the standard fixed IV. Each compression applies rounds 0 through 38 and feed-forward. The final comparison covers all 256 bits. Standard big-endian padding for bit length 1024 is the same full third block, so equality is preserved. The length is below `2^64` bits.

## 15. Readiness and epistemic status

The candidate is `submission_state: ready` for exploratory review. Ready means the construction, probability space, resource vector, experiments and limitations are internally specified; it does not mean the heuristics are proved or the result is qualified. The binding DKW theorem removes the old bootstrap-coverage premise. The remaining score-critical premises are H1 fixed-IV matching-class transfer, H3A/H3B/H3C/H3D construction allowances and conversions, and H4 fixed-IV online-mean transfer. H2 and H5 still require the declared ideal independent coins.

No ordinary fixed-IV collision has been computed. The organizer experiments return no pairs and make no full-scale cost inference. The full A10 sweep and full nominal attack are not executed. Two-backend UNSAT without a proof certificate is evidence, not a theorem. The native lower conversion and dated device envelope remain exploratory accounting premises. A `plausible_not_refuted` screen would not be mathematical proof or human acceptance.

