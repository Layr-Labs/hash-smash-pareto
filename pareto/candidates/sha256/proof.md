# One-selected-output C39 construction for 39-step SHA-256

## 1. Target and output

The construction targets `sha256-r39-prefix-v1`. It uses the standard SHA-256 IV, FIPS 180-4 padding, feed-forward, rounds 0 through 38 in every compression, and all 256 output bits. A success consists of two distinct 128-byte messages `M0 || M1` and `M0 || M1'`. Both messages use the same first block. Their padding block is identical.

For a first-block chaining value `H = F39(IV, M0)`, the solver constructs `M1 != M1'` such that `F39(H, M1) = F39(H, M1')`. Feed-forward therefore gives the same chaining value after block two. The common padding block preserves equality.

## 2. Fixed C39 parameters

The construction uses one 39-step core, one coupling value `j = 0xadc6d187`, and a deterministically constructed list of 299 values of `A3` in 50 classes of equal `X10(A3)`. A deterministic cross-j q-aware rule constructs all fifty labels and 299 values. The list SHA-256 is `5532657e4e9259c964f9b58829512e4c4036fad6cc3dda3d007192b95b4fadbd`. Published j ranks ninth by exact radius-eight mass, then first in both q-aware selection stages. The core fixes both executions from step 12 through step 17 and fixes `W16`, `W17`, `W16'`, and `W17'`. The message XOR is nonzero in words 8 through 12.

The runtime stores at most 4,096 bytes of fixed parameters. This envelope includes the core, `j`, the `A3` list, the difference masks, and all derived constants. The claim records this entire envelope as nonuniform advice even though some values are public algorithm constants.

## 3. The inverse table

Define `s(z) = sigma0(z) - z mod 2^32`. Preprocessing makes two complete `2^32` passes over `z`: one pass counts high-28-bit buckets, and one pass writes the values. It groups values by `s(z) >> 4`. The resident table stores `2^32` four-byte values and `2^28 + 1` four-byte offsets. The final endpoint `2^32` is implicit because it does not fit in a four-byte offset. Exact resident size is `2^34 + 2^30 + 4 = 18,253,611,012` bytes, or 17 GiB plus four bytes.

A lookup scans every entry between its two offsets and recomputes the full 32-bit key. Bucket size has mean 16 for a uniform target; 16 is not a scan cap. The recorded maximum full-key fibre is 14, so a bucket, which covers 16 full keys, has at most 224 entries. The cost proof charges 224 entries for every lookup.

The recorded exhaustive histogram has exactly `2^32` targets and `2^32` preimages, with its last nonzero bin at 14. The admitted experiment embeds the stored bins and checks their exact arithmetic; it does not rerun the `2^32` enumeration.

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

Here `d f(x)=f(x')-f(x)` and all additions are modulo `2^32`. `experiments/selected39.py` embeds the exact characteristic strings and all applicable two-bit relations, implements this predicate, reconstructs every word, and checks both lookup equations on 16 records from 16 distinct real chaining values.

Fix `H` and `A0`. Any valid prefix solution has one value `W1`. Its first matching equation places that value in the exact fibre returned by Stage 1. The early `W9` tests are necessary prefix conditions, so they remove no valid solution.

The valid solution's `A3` belongs to exactly one `X10` class. Its second matching equation places its `W2` in that class's exact fibre. The equation fixes `A2`; `J = j` and the full prefix check then accept it. Conversely, each emitted prefix passes both equations and every deterministic condition through step 17. The final compression comparison prevents a false collision.

The source checks `H=F39(IV,M0)`, full reconstruction, the complete predicate, both lookup targets, both early `W9` filters, `J=j`, the `X10` class, and `W10=X10(A3)-A2`. It also checks the published semi-free-start pair and all 299 distinct list values. Complete enumeration determines X before the selected output is tested. The deterministic bound 14*14*299=58604 limits the temporary output buffer. Exactly one selected output is rebuilt and tested when X is positive.


## 6. Deterministic parameter construction

The construction begins with the supplied Table-23 upper trajectory and a fixed three-stage lower-core SAT recipe. The three formulas have 32,916, 32,916 and 32,756 variables, and 118,402, 118,403 and 117,778 clauses. They reproduce SAT assignments byte-for-byte. A separate evaluator checks all 354,583 clauses and 983,289 literals, every relaxed condition, S1-S9 and all 54 applicable row-12-through-17 relations. The resulting core-pair SHA-256 is `fdb66daab2199aa45688259422b5368b849740df1b240412d587f193be6f2501`.

Conditional on that core, exact radius-eight counts rank 256 deterministic j candidates. The top sixteen receive a complete first q-aware screen. Its top four receive the second screen. The rule enumerates 240,530,768 A3 records and executes 506,008,224 prefix tests, including every losing j. It selects `j=adc6d187`, fifty `X10` labels and the list above. The supported selector envelope is 58,161,946,387,712 primitives.

The cross-j rule was defined after earlier development outcomes, so none of those q or tail results enters this endpoint. The complete PB=0 selected-output confirmation protocol was hash-frozen later, before its new trial and tail outcomes, and uses separate domains.

This closes the rejected package's missing j/label/list rule and supplies an executed lower-core reconstruction. It does not close H3. The Table-23 upper trajectory, characteristic and relations remain supplied advice, and native SAT conflict/propagation counters do not price every memory and control operation. The score therefore retains the explicit premise that all such work fits the separate `2^74` preprocessing allowance. Material reuse of Yukon submissions `7c4da9b7-54cc-4c6a-9754-883588e3b019` and `69616879-8f53-4bff-a45d-a2bb7367418e` is declared. Attribution is not a cost waiver.

## 7. Exact one-output probability identity

Let X be the complete prefix-output count in a fresh trial. For X>0, reservoir sampling processes outputs in deterministic order and replaces its retained ordinal k with probability `1/(k+1)`. Induction gives probability `1/X` for every final ordinal. Let S be the event that the selected output passes the modular sufficient event and final complete comparison. Then

```text
P(S) = P(X>0) * P(S | X>0).
```

This is a probability identity. It has no expected sibling count, sibling independence, deterministic output cap, or retained-successful-mass premise. The admitted experiment checks the induction exhaustively for all success masks up to eight outputs; the proof holds for every positive X.

Reservoir draws use rejection from 64-bit words with at most sixteen attempts. Since X is at most 58,604, one trial's rejection-exhaustion probability is at most `58604*(58604/2^64)^16`. Across the complete nominal run, the union bound is below `2^-664.23`. It fits far inside the margin between 0.391 and the claimed 0.39 success probability. All attempts are charged.

## 8. Fresh complete-table and selected-tail evidence

The preregistered PB=0 campaign ran `2^24` trials. It recorded 450 prefix outputs in 406 nonempty trials: 366 singletons, 36 doubletons and four triples. The maximum multiplicity was three. An independent implementation replayed every raw count, all 450 prefix predicates, all 406 reservoir choices, every first block/chaining value and both selected second blocks. No check failed. The exact one-sided 99.5% binomial lower endpoint under ideal iid trials is

```text
P(X>0)_L = 2.12179473118378e-5.
```

The first 64 selected outputs in trial order were frozen before their tail outcomes. Each block used 512 sequential-importance paths and `2^18` candidates at each reached free row W18 through W23. The point mean is `2.460945035043473e-23`; the nominal one-sided 99.5% block-bootstrap endpoint is

```text
p_tail_L = 1.947202378075925e-23.
```

A separate C inverse/eight-register implementation verifies all 15,661,579 emitted continuation vectors, and a separate Python forward implementation checks one pair in every nonempty block. These are conditional semi-free-start continuations, not ordinary fixed-IV collisions. The 64 selected prefixes are the statistical units; the millions of vectors are verification records. The ideal-coin distribution-free Hoeffding lower endpoint over 64 blocks is zero. Rare-event bootstrap coverage, matching-class transfer and deterministic PRNG independence remain explicit limitations.

With alpha 0.005 assigned to each component, the nominal simultaneous 99% endpoint is

```text
lambda_L = P(X>0)_L * p_tail_L
         = 4.13156374635002443599396849650e-28
         = 2^-90.96729872941097.
```

H1 states that the selected-prefix matching-class mean applies to the actual selected output of a real first-block trial. The campaign samples the correct uniform-per-trial selected-prefix distribution, but its inverse tail sampler varies the chaining value inside the matching class and does not prove H1.

## 9. Fixed success and work budget

Use exactly

```text
N = 1756406089356818651915999597
```

ideal fresh trial slots. Since `(1-lambda_L)^N <= exp(-N*lambda_L)`, untruncated success is at least 0.516. The program maintains an integer primitive counter and stops with failure before exceeding

```text
8 * 64 * N = 899279917750691149780991793664
```

target-compression units. Under H4, expected total online work is at most `64*N`; Markov bounds cap exhaustion by 1/8. The union bound leaves more than 0.391 before the negligible reservoir-rejection term, and remains above 0.39 after it. Work/success independence is unnecessary.

The finite construction and evidence envelope is 4,588,592,331,898,368 primitives, or 1,631,789,591,714 target units rounded upward. The candidate separately charges `2^74` target units for the H3 preprocessing premise. Double-charging the known finite work gives total

```text
899279936640157082891362240162 target units.
```

Its exact base-two logarithm is `99.5046850335875283221...`; `time_log2=99.50469` rounds upward.

## 10. Complete online cost and memory

The new full-table campaign gives 0.999863 stage-1 preimages, 0.780601 stage-2 lookups, 4.667464 J tests, 0.027371 full prefix predicates and 0.00002683 outputs per trial. The declared envelope rounds these to 1.01, 0.80, 5, 0.04 and 0.00003. It charges every bucket scan at 224 entries although the complete table observed maximum 46.

| Item | Target units per trial |
| --- | ---: |
| fresh first-block compression | 1.000000 |
| stage-1 table lookup | 1.000000 |
| common generation, arithmetic, memory and control | 1.456615 |
| stage-1 scan at 224 entries | 2.549075 |
| returned preimages and W9 tests | 0.045974 |
| stage-2 lookups | 0.800000 |
| stage-2 scans | 2.039260 |
| J tests | 0.113798 |
| complete prefix predicates | 0.058265 |
| reservoir draws | 0.000022 |
| selected reconstruction and recovery | 0.000044 |
| selected final compressions | 0.000060 |

The rows sum to 9.063113 units. The 64-unit premise gives a factor above seven and includes all failed trials, randomness, memory operations, counters and the single final test.

The exact table arrays use 18,253,611,012 resident bytes and 19,327,352,836 bytes while building. The campaign cgroup peaked at 19,366,563,840 bytes with no memory-limit or OOM events and no swap. The complete declaration is 22 GiB, `memory_log2_bytes=34.4594316186373`. Under `hashsmash-scalar-tm-v1`, the upward normalized score is

```text
99.50469 + 34.4594316186373 - 20
  = 113.9641216186373.
```

This is 4.1810183814 bits below the stated r39 reference 118.14514.

## 11. Ordinary message validity

On success the returned byte strings are `M0 || M1` and `M0 || M1'`, each exactly 128 bytes before padding. They share M0 and differ in words 8 through 12 of the second block. Both start from the standard fixed IV. Each block uses exactly rounds 0 through 38 and feed-forward. Equality after block two is checked on all 256 bits. Standard big-endian SHA-256 padding for bit length 1024 is the same full third block for both messages, so equality is preserved. The bit length is below `2^64`.

## 12. Executable evidence

`experiments/selected39.py` is self-contained. It embeds the core, complete 299-entry list, characteristic masks and relations, sixteen actual selected prefixes from distinct fresh trials, all four campaign summaries, the inverse-table histograms, 64 tail block means, memory receipts, cross-j result and lower-core hashes. It independently recomputes the SHA-256 traces, both lookup equations, complete prefix predicate, exact binomial tail probability, selected-output identity, work rows, success wrapper and score. It returns null message pairs because no event near `2^-90.97` is expected in organizer trials.

The pinned organizer experiment validates deterministic identities and stored evidence. It does not prove H1, bootstrap coverage, H3, H4, ideal randomness or the full-scale success probability. Package state `ready` means ready for exploratory screening, not qualified or human accepted.

## 13. Limitations

- The positive tail endpoint is nominal. Its distribution-free lower endpoint is zero.
- Public deterministic seeds aid reproduction but do not establish iid coins.
- H1-selected transfer is score-critical and unproved.
- H3 upper-advice discovery and complete native SAT cost are explicit score-critical premises inside the `2^74` allowance.
- H4 transfers finite branch rates and source-level allowances to a full run.
- No ordinary fixed-IV collision was computed. A plausible screening verdict would not be a mathematical proof or human acceptance.
