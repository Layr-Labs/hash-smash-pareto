# A fixed-budget C39 table solver for 39-step SHA-256

## 1. Target and output

The construction targets `sha256-r39-prefix-v1`. It uses the standard SHA-256 IV, FIPS 180-4 padding, feed-forward, rounds 0 through 38 in every compression, and all 256 output bits. A success consists of two distinct 128-byte messages `M0 || M1` and `M0 || M1'`. Both messages use the same first block. Their padding block is identical.

For a first-block chaining value `H = F39(IV, M0)`, the solver constructs `M1 != M1'` such that `F39(H, M1) = F39(H, M1')`. Feed-forward therefore gives the same chaining value after block two. The common padding block preserves equality.

## 2. Fixed C39 parameters

The construction uses one 39-step core, one coupling value `j = 0xadc6d187`, and a deterministically constructed list of 299 values of `A3` in 50 classes of equal `X10(A3)`. The list SHA-256 is `3630571a02d5815a6b300068ab032c6cbee5920a49f1d003e91de1e15ec5acff`; 298 entries equal the earlier published list. The core fixes both executions from step 12 through step 17 and fixes `W16`, `W17`, `W16'`, and `W17'`. The message XOR is nonzero in words 8 through 12.

The runtime stores at most 4,096 bytes of fixed parameters. This envelope includes the core, `j`, the `A3` list, the difference masks, and all derived constants. The claim records this entire envelope as nonuniform advice even though some values are public algorithm constants.

## 3. The inverse table

Define `s(z) = sigma0(z) - z mod 2^32`. Preprocessing makes two complete `2^32` passes over `z`: one pass counts high-28-bit buckets, and one pass writes the values. It groups values by `s(z) >> 4`. The resident table stores `2^32` four-byte values and `2^28 + 1` four-byte offsets. The final endpoint `2^32` is implicit because it does not fit in a four-byte offset. Exact resident size is `2^34 + 2^30 + 4 = 18,253,611,012` bytes, or 17 GiB plus four bytes.

A lookup scans every entry between its two offsets and recomputes the full 32-bit key. Bucket size has mean 16 for a uniform target; 16 is not a scan cap. The recorded maximum full-key fibre is 14, so a bucket, which covers 16 full keys, has at most 224 entries. The cost proof charges 224 entries for every lookup.

The recorded exhaustive histogram has exactly `2^32` targets and `2^32` preimages, with its last nonzero bin at 14. `inputs.json` binds the primary histogram file by SHA-256. The submitted experiment checks the stored bins and their arithmetic; it does not rerun the `2^32` enumeration.

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

For every prefix output, the solver reconstructs both second blocks, executes both 39-step compressions, and compares all eight feed-forward words. It returns the two complete messages only after this final comparison succeeds.

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

Here `d f(x)=f(x')-f(x)` and all additions are modulo `2^32`. `experiments/gold39.py` embeds the exact characteristic strings and all applicable two-bit relations, implements this predicate, reconstructs every word, and checks both lookup equations on 16 records from 16 distinct real chaining values.

Fix `H` and `A0`. Any valid prefix solution has one value `W1`. Its first matching equation places that value in the exact fibre returned by Stage 1. The early `W9` tests are necessary prefix conditions, so they remove no valid solution.

The valid solution's `A3` belongs to exactly one `X10` class. Its second matching equation places its `W2` in that class's exact fibre. The equation fixes `A2`; `J = j` and the full prefix check then accept it. Conversely, each emitted prefix passes both equations and every deterministic condition through step 17. The final compression comparison prevents a false collision.

The source checks `H=F39(IV,M0)`, full reconstruction, the complete predicate, both lookup targets, both early `W9` filters, `J=j`, the `X10` class, and `W10=X10(A3)-A2`. It also checks the published semi-free-start pair and all 299 distinct list values. Each accepted online prefix is tested immediately, so no unbounded output list is retained.

## 6. Rate and tail evidence

The list was frozen before a fresh paired holdout. An exact reduction integrates all `A0` values: for fixed `A1,A2,A3`, the relevant `W8` conditions are four independent linear forms, so the complete prefix predicate is represented by one value with a constant `1/16` factor. The fixed holdout ran 262,144 conditional indices and found 7,987 accepted selected-list prefixes. Its point `q` is `0.0019042491913`. A one-sided 99.9% Hoeffding endpoint under independent ideal coins is `0.0016773862647 = 2^-9.219569337`.

The exact list factor is `M=0.9926934242248535`; the necessary `W9` filter contributes exactly `1/64`. A fresh modular-tail campaign used the first 64 accepted prefixes, 512 paths per prefix, and `2^18` candidates per free row. Its point mean is `2^-74.6615796907`. A one-sided 99.9% Student-t endpoint is `2^-75.1552592620`. The product gives the declared event endpoint

`p0 = (1/64) * M * q_L * pbar_L = 2^-90.38540845807911 = 6.184162369678295060419643842089090663339214433150192275469050024944493760160291153599619123184143356E-28`.

The q-aware construction and holdout ran before the tail outcome was inspected. Full training replay was byte-identical. Independent implementations checked all 15,778 holdout prefixes and all 33,444,580 conditional SFS continuation vectors with zero failures. These continuations are not independent probability observations and are not ordinary fixed-IV collisions.

The q and tail campaigns sample the matching-class model. H1 transfers that model to a real first-block chaining value; the fresh data do not test this transfer. The tail estimator samples the six words `W18` through `W23` that are uniform in a matching class. It uses sequential importance sampling with every dead path included at weight zero.

The q endpoint is Hoeffding-valid only for independent ideal coins. The tail endpoint uses nominal Student-t coverage on nonnormal importance weights. Together they give a 99.8% simultaneous nominal guarantee by the union bound, conditional on both marginal models. Fixed reproducibility seeds do not establish ideal independent coins. These confidence statements support H1 and H2; they are distinct from the algorithmic 0.39 success calculation.

## 7. Probability premises

Premise H1 says that `F39(IV,M0)` for a fresh random first block behaves as an independent uniform chaining value for the matching-class and tail quantities. This transfers the reconstructed-class tail mean to a real first block.

Premise H2 says that a fresh-first-block trial has collision probability at least `p0` and that distinct trials amplify as independent Bernoulli trials. This premise includes the conversion from expected collision count to trial success when one trial emits correlated siblings. The construction does not present linearity of expectation as that conversion.

Both premises are score-critical. The rate evidence tests real chaining values, but no feasible direct run can observe a `2^-90.43` complete event. The claim therefore uses the exploratory lane.

## 8. Fixed success and work budgets

The run uses

`N = 1173433569311756739413236012` fresh-first-block trials.

Under H2, `1 - exp(-N p0) >= 0.5160000000000000000000000000769187180819046011100917864593255845739903709271439437558797258068201784`. The mean charged work is at most 64 target-compression units per trial under the cost premise in Section 9. The program keeps an exact global work counter and stops with failure at `8 * 64 * N` units. Markov's inequality bounds budget exhaustion by `1/8`, without assuming that high work and success are independent.

The union bound gives success at least

`0.5160000000000000000000000000769187180819046011100917864593255845739903709271439437558797258068201784 - 1/8 = 0.3910000000000000000000000000769187180819046011100917864593255845739903709271439437558797258068201784 > 0.39`.

The implementation uses an integer credit counter. A whole r39 compression or a charged table lookup adds 2,812 credits; every other v5 primitive adds one. It aborts before an operation would make the counter exceed `2812 * 8 * 64 * N`. Preprocessing has its own `2812 * 2^74` cap. This wrapper turns the expected-cost solver into a fixed-work algorithm. A run that reaches either cap returns failure.

## 9. Complete online cost envelope

The selected profile prices one whole r39 compression at one unit and every other primitive operation at `1/2812` unit. A random table lookup is conservatively charged as one whole compression in addition to its full bucket scan.

The branch envelopes round the recorded means upward: 1.01 Stage-1 preimages, 0.80 Stage-2 lookups, 5 `J` tests, 0.018 prefix checks, and `3.0e-5` outputs per trial. Each scan charges the deterministic 224-entry maximum at 32 primitives per entry. Common work receives 4,096 primitives; a preimage test 128; a `J` test 64; and a full prefix/reconstruction 4,096. These include random draws, address formation, loads, stores, arithmetic, comparisons, both sides of branches, loops, counters, reconstruction, and failed paths.

| Item | Whole units | Primitive operations | Target units |
| --- | ---: | ---: | ---: |
| fresh first-block compression | 1.00000000 | 0.000000 | 1.000000000 |
| stage-1 table lookup | 1.00000000 | 0.000000 | 1.000000000 |
| common generation, arithmetic, memory, counters and control | 0.00000000 | 4096.000000 | 1.456614509 |
| complete stage-1 bucket scan, maximum 224 entries | 0.00000000 | 7168.000000 | 2.549075391 |
| stage-1 returned preimages and W9 tests | 0.00000000 | 129.280000 | 0.045974395 |
| stage-2 table lookups | 0.80000000 | 0.000000 | 0.800000000 |
| complete stage-2 bucket scans and loop control | 0.00000000 | 5734.400000 | 2.039260313 |
| J tests, rounded to five per trial | 0.00000000 | 320.000000 | 0.113798009 |
| prefix checks and immediate collision reconstruction | 0.00000000 | 73.728000 | 0.026219061 |
| two final target compressions per emitted output | 0.00006000 | 0.000000 | 0.000060000 |
| padding equality, output comparison and recovery | 0.00000000 | 0.122880 | 0.000043698 |

The rows total 9.031045376956 expected units per trial. The claim raises this to 64 units, a factor 7.086666. H4 explicitly transfers the recorded branch means to fresh-first-block trials; the finite primitive allowances are visible here and in the admitted experiment source.

The fixed online cap is `600797987487619450579576838144` target units. Preprocessing adds `2^74` units. Total charged time is `600798006377085382058157692928` units, whose logarithm is `98.92279477731095191620635546414565664035572758544745044010514785003936741560141204198865458496580789`. `claim.json` rounds this upward to `98.9228`.

## 10. Memory

The complete declared peak is 19 GiB = 20401094656 bytes. The inverse table and offsets need 17 GiB plus four bytes. Table construction needs a temporary 1 GiB positions array. Exactly 1,073,741,820 bytes remain for code, the 4 KiB parameter envelope, stack, allocator state, messages, state, counters, lookup buffers, retained randomness, and runtime data.

The memory logarithm is `34.24792751344358549379351942290683442269350756966153401458152473086456520820546488680270805417217652`. The Pareto memory term is `14.24792751344358549379351942290683442269350756966153401458152473086456520820546488680270805417217652`. The exact-cap normalized score is `113.1707222907545374099998748870524910630492351551089844546866725809039326238068769287913626391379844`. The upward-rounded claim field `time_log2=98.9228` yields 113.170727513444, which rounds to 113.17073 and remains about 4.97441 bits below the recorded 118.14514 entry.

## 11. Parameter construction

The claim charges `2^74` target compressions for the inverse table, dense core, `j` and group-label discovery, and list construction. The table builder makes exactly `2^33` evaluations of `s`, plus initialization, prefix sums, stores, and loop work. The dense-core enumeration is bounded below `2^36` target compressions under the declared 34-free-bit model and exact row-fibre tests.

The 299-entry list no longer relies on the missing historical transcript. A fixed two-round algorithm enumerates every positive-J candidate in the 50 groups. Round 1 tests 512 conditional prefixes per candidate and retains 64 per group by descending integer `N_j * pass_count`, then descending `N_j`, then ascending `A3`. Round 2 tests 32,768 fresh prefixes per retained candidate and applies the same total order to select each group's fixed size. It uses fixed domain-separated seeds. A complete replay produced byte-identical training transcripts and list bytes. Executed training used 126,025,728 predicate checks; a 65,536-primitive allowance per check remains far below the `2^74` cap.

There is also a finite exact route. Integrating `A0` leaves exactly `2^26 * sum N_j = 2^62.494745` `(W9,A2)` checks over all 200,192 candidates. With 65,536 primitives per check and `C39=2812`, the exact route is below `2^68` target units. It is specified by resumable bounded code but was not physically completed. The executed two-round algorithm is the construction actually bound to this candidate.

The core, published `j`, and 50 group labels remain fixed parameters. Their historical selection transcript is absent. H3 declares that the published SAT and parameter search finds these remaining 300 bytes within the total `2^74` allowance; this is still a score-critical preprocessing premise. The claim counts the full 4 KiB parameter envelope as advice and does not present list reproducibility as evidence for the missing core/`j` transcript.

## 12. Executable evidence

`experiments/gold39.py` has SHA-256 `eb63e40b2000eec89d2e69f4903b3457d1c83cae201b85d74d6f840dc174dc1b`. It contains no package code. It embeds hash-checked inert records, the exact predicate data, and the cost rows, then uses its own FIPS 180-4 and solver-formula implementation. Trial 0 internally checks the Table 23 semi-free-start collision, 16 real prefix records, all 299 `A3` values, the 50 `X10` classes, the stored preimage histogram, both nominal endpoints, the cost sum, and the stored final-success value. Other trials replay one embedded prefix record selected by the organizer seed.

The program returns null messages because a direct ordinary collision occurs with probability near `2^-90.43` per online trial. The organizer report records reproducible isolated execution and null output pairs. Internal identity and arithmetic results are untrusted participant observations; reviewers assess them from the submitted source and independent checks. The run does not measure attack success probability, expected work, or parameter discovery, and it does not turn H1-H4 into theorems.

## 13. Reproduction and limits

Run `python3 r39_goldzweig_candidate/extract_inputs.py`, `python3 r39_goldzweig_candidate/cost_envelope.py`, `python3 r39_goldzweig_candidate/score_model.py`, then `python3 r39_goldzweig_candidate/build_candidate.py`. From `_yukon_r39_goldzweig/pareto`, run `python3 ../scripts/pareto_candidate.py --family sha256 --rounds 39`.

The construction is specific to the C39 core and deterministic q-aware list `3630571a...`. It makes no claim for another core, another list, or round 40. The score depends on H1, H2, H3, and the empirical cost-rate transfer. The A2-free worst-case sibling bound is not competitive and is not used.
