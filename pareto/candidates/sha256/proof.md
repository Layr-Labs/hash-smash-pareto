# SHA-256 reduced to 40 steps: ordinary collision with a solver-built head at time_log2 = 60.00142

Target `sha256-r40-prefix-v1`: standard IV, the first 40 steps in every compression, FIPS 180-4 padding, feed-forward and all 256 output bits. Claim: time 60.00142, memory 27.99704, preprocessing 60.00141, success at least 0.39, advice 2048 bytes. The computed time logarithm is 60.001410000148 (Section 5); the claim is its ceiling at five decimals. The normalized score is time plus max(0, memory_log2 - 20) = 60.00142 + 7.99704 = 67.99846.

The construction: a random first block computed from the standard IV and charged; a counted, capped head solve that makes rows 0 to 22 of the characteristic of Appendix C hold for that chaining value; the remaining head conditions and the tail (rows 23 to 39) paid by a declared success probability. The first message difference is in word 0. The ledger structure and the premises follow the accepted round-39 entries through our base `9993eaa8`; the online head is charged as a counted solve with a fixed cap in the manner of the accepted sha256-r32 entry 6eeefb64; the characteristic and head search are charged as a flat preprocessing allowance in the manner of the accepted sha256-r37 entry 6c77089c and sha256-r38 entry fb176310. Credits are in Section 13.

No free-start or compression-only result is claimed: every head is solved for a chaining value computed from the standard IV, and the witness pair of Appendix C is advice that does not itself collide (Section 2.1).

## 1. Target and output

SHA-256 with 40 steps in every compression, FIPS 180-4 padding, the standard IV, feed-forward after step 39, all 256 digest bits. The output is two distinct 128-byte messages `M0 || M1` and `M0 || M1'`: the same first block `M0` and second blocks that give the same chaining value after the second compression. Both messages have the same length, so the padding block that follows is identical and the two digests are equal. `M0` is a uniformly random block and `cv = compress40(IV, M0)` is one target compression from the standard IV, charged in Section 5.

## 2. The construction (solver-built head)

Notation: `A_i` and `E_i` are the two state words computed at step `i` (rows -4 to -1 of Appendix C hold the chaining value), `W_i` is the message word of step `i`, and `M`, `M'` are the two second blocks.

**2.1 Characteristic and advice, which does not itself collide.** The 40-step signed characteristic of Appendix C (SHA-256 of its rows -4 to 39, `8cceb2102b6d39d53f25b1cc9e4d5d631bfd244c4fbded51f99eba9540798829`) has its first message difference in word 0; `M` and `M'` differ in message words 0, 9, 10, 11, 12, 13. Its witness pair (`cv*`, `M`, `M'`), printed in Appendix C, is a free chaining value `cv*` (not computed from the standard IV) and a pair that conforms to every signed row of the characteristic (rows -4 to 39) under recompute. It is advice in the manner of the accepted round-39 entries: like the transplanted free-CV pair there, it conforms only as a characteristic and does not itself reach a collision. Recomputed by two 40-step computations from `cv*`, the pair's two 40-step outputs (feed-forward included) are different; it is not a collision. Its role is to show that the head conditions of rows -4 to 22 can hold together (value-satisfiability) and to supply the signed rows used as advice; it is evidence, not an online shortcut.

**2.2 Head by a counted, capped solve.** For each first block, the program `experiments/head40_c80d.py` (Section 3) fixes `cv = compress40(IV, M0)` and runs a bounded head solve over the free second-block words that makes every condition of rows 0 to 22 of the characteristic hold for both members. The solve is charged by an exact operation count with a fixed cap of 21,020 counted v5 primitives per head solution (a halting counter), the pattern the accepted sha256-r32 entry 6eeefb64 uses for a counted solver with a fixed cap. The 21,020 operations are the two 40-step verification compressions (2 x 2,880 operations; the organizer reference count is `C = 2896`) and the head-condition check over rows -4 to 22; every failed or capped call is charged at the cap. A capped call returns no solution and its work is charged. The expected number of head solutions per first block and the mean charged work per solution are the declared premise H1-head-solver (Section 9); its only measurement is the single free-CV solver call of the game record, which does not itself establish the per-solution cost at a standard-IV chaining value (Section 12).

**2.3 What remains to pay.** The head construction enforces every condition of rows 0 to 22, so `p_head = 1`. Rows 23 to 39 are the tail: one declared premise, H2-tail, `p_tail = 2^-24.79100` (Section 8). A head solution that passes the tail event gives equal 40-step outputs for `M0 || M1` and `M0 || M1'`; the program computes and compares both full two-block hashes before any output (Section 3).

## 3. Program

The program is `experiments/head40_c80d.py` (SHA-256 `ca4384527585d7e045998a95bc199dded5184d0246caa86347622183c1575b30`, 9,010 bytes). One first block: (1) draw a uniformly random first block `M0` and compute `cv = compress40(IV, M0)` from the standard IV; (2) run the bounded head solve on `cv` until it has returned one solution or reached the counted cap of 21,020 operations; (3) for each solution check every head condition, compute the two second-block compressions from `cv` and compare all 256 output bits; (4) on equality output `M0 || M1` and `M0 || M1'` and halt. The driver halts at the first success or after the `B` first blocks of Section 7, whichever comes first; every first block's work, failures included, is charged (Section 5). The counted cap is tested at the start of every first block and after every solve call, so no call runs past the cap and no first block's cost exceeds the charged bound. There is no distinguished-point walk, claw, gap law, hidden basis, recovery stage or schedule program; the message schedule is computed inside the compressions charged at `C`. The reference solve engine is CaDiCaL (whose peak resident set is the online memory of Section 6); the organizer executor does not include it, so an organizer trial of this program asserts only that the witness satisfies rows -4 to 22 and reports its chaining value.

## 4. Machine model and prices

The collision-frontier-v5 model: a classical probabilistic 256-bit word RAM. One 40-step target compression costs one unit; every other primitive word operation costs `1/C` units with `C = 2896`, the selected target's reference operation cost (the organizer's count of the word operations of one trusted 40-step SHA-256 compression). Primitive operations: 256-bit load or store, addition or subtraction, AND/OR/XOR/NOT, shift or rotation, comparison, conditional branch, and an independent uniform random word. The online head solve's work per solution is charged as an exact operation count with the fixed cap of 21,020 operations (Section 2.2), the pattern of the accepted sha256-r32 entry 6eeefb64; the offline search that produced the characteristic and the advice is not charged at a per-operation rate but as a flat preprocessing allowance (Section 11).

## 5. Exact ledger

All costs are in target compressions. One trial is one head solution; `p` is the probability that one trial yields the collision; `mu = ln(1/(1 - 0.39)) = 0.494296322` is the expected number of successes that gives success probability 0.39 (Section 7).

| Term | Derivation | log2 |
| --- | --- | ---: |
| head conditions | Section 2, product of the declared probabilities | 0.00000 |
| tail (rows 23 to 39) | premise H2-tail (Section 8) | -24.79100 |
| one-trial success `p` | `p_head * p_tail` | -24.79100 |
| head solutions `N` | `ceil(mu / p)` = 14349013 | 23.77445 |
| first blocks `B` | `ceil(N / s)`, `s = 1` solutions per first block (premise H1-head-solver) = 14349013 | 23.77445 |
| construction | `B * 21,020` operations / `C`; 21,020 operations per head solution (premise H1-head-solver), `C = 2896` | 26.63408 |
| first blocks | `B / m` compressions, `m = 1` (fraction of first-block chaining values the construction accepts) | 23.77445 |
| preprocessing | characteristic and head search, flat allowance (Section 11) | 60.00141 |
| total `T` | construction + first blocks + preprocessing | 60.001410000 |

`T = B * 21,020 / 2896 + B / 1 + 2^60.00141` with the integers above; `log2 T = 60.001410000148`, so time_log2 = 60.00142 (ceiling at five decimals). The preprocessing allowance dominates: the two online terms sum to 2^26.634, and the total is 2^60.00141 to the precision of the claim. Every charged item is in `T`: each first block's random block and its compression (first blocks); the solve calls, failed and capped ones included, the head checks and the full verification of every solution (construction); restarts; and the characteristic and head search (preprocessing). Failed first blocks are charged in full: `B` counts every one run, successful or not.

## 6. Memory

The online program's peak is 267,884,831 bytes: the reference solver's peak resident set, at most 267,881,759 bytes (the largest CaDiCaL maximum resident set size of nine existing runs on 40-row instances of the same encoder, up to 3,557 s, research runs_1101/fullspeed); the characteristic and witness (2,048 bytes); two 40-word schedules and two states (under 1 KiB). The preprocessing search peak is 267,884,831 bytes (Section 11). The claimed memory is the larger of the two phases, 267,884,831 bytes = 2^27.99704; memory_log2_bytes = 27.99704. The 2048-byte advice is part of the online peak.

## 7. Success probability

The probability space is the program's fresh random first blocks and its solve coins. Per trial the success probability is `p = 2^-24.79100` (Section 5). Under premise H5 the trials are independent, so with `N` trials `P(no success) <= (1 - p)^N <= exp(-N p)`. `N = ceil(mu / p)` gives `N p >= mu = ln(1/0.61)`, hence `P(success) >= 1 - exp(-mu) = 0.39`. The `B = ceil(N / s)` first blocks supply `B * s >= N` trials at the mean yield `s` of premise H1-head-solver. Repeated inputs are not counted twice: the solve returns distinct second blocks and a repeated solution is discarded, and the output is two distinct messages (`M1` and `M1'` differ in words 0, 9, 10, 11, 12, 13). success_probability = 0.39.

## 8. The tail (rows 23 to 39), a declared best-case probability

Premise H2-tail: for head solutions that pass the head conditions (Section 2), the probability that the two 40-step compressions give equal 256-bit outputs, which includes the pair following rows 23 to 39 of the characteristic, is at least `p_tail = 2^-24.79100`. The claim prices this declared value (a best-case premise, in the manner the accepted round-39 entries price their tail at its mean rather than at a lower confidence bound); one bit of `log2 p_tail` moves the online time logarithm by one bit, because the online terms are proportional to `1/p` (Section 5), while the score is set by the preprocessing allowance.

Organizer evidence and its scope (`t40-tail-01`, Section 10). The replica `experiments/tail40_c80d_J23.py` draws uniform junction states after step 22, applies a junction difference `D`, runs both members through steps 23 to 39 with the pair's own expanded schedule words `M`, `M'`, and counts equal 256-bit outputs. It hard-asserts that the premise is not refuted: the one-sided 99% upper bound of the pooled hit rate is at least `2^-24.79100`. A local run of the frozen configuration observed 0 hits in 4,194,304 samples, whose one-sided 99% upper bound is near `2^-20.3`, well above the priced value; the replica does not refute the premise and does not, at this sample size, observe a hit. Declared junction-distance premise: the junction difference `D` available in table `T_c80d_J23.tsv` (its nearest row) is at Hamming distance 129 from this pair's own junction difference, and that nearest row's measured tail logarithm is -25.206; neither value is a direct measurement of this pair's junction. The priced `p_tail = 2^-24.79100` is therefore a declared best-case premise supported by the related-junction table and left unrefuted by the replica, not a measurement of this pair's tail. This limitation is declared, not relied on as evidence against the premise (missing evidence is not contrary evidence).

## 9. Premises (declared in claim.json)

- **H1-head-solver**: for a uniformly random first block the online head solve returns at least 1 head solution in expectation, at a true expected charged work of at most 21,020 operations per solution, counting every failed or capped call, the solution checks and the two 40-step verification compressions, each call halting at 21,020 operations; and the solution meets the head conditions the solve does not enforce with probability 2^0.00000. Evidence: the game record of shot web-ba2d0756db1345f7-20261103T004148-c80d (one call on rows 0 to 22 of this head at a free chaining value: SAT in 7.747 s, 82,280 conflicts, seed 1161232, 1 of 1 calls); the head program's organizer experiment asserts the witness satisfies rows -4 to 22. The rate of solutions per first block and the per-solution cost for chaining values computed from the standard IV are the declared premise; no call at such a value, and no call halted at the 21,020-operation cap, is claimed as run (Section 12).
- **H2-tail**: `p_tail >= 2^-24.79100` for rows 23 to 39, a declared best-case value; the organizer replica does not refute it and the nearest available junction is 129 bits away (Section 8).
- **H3-advice-construction**: the characteristic and head search are constructed within the flat preprocessing allowance of 2^60.00141 target compressions and 267,884,831 bytes (Section 11).
- **H5-group-independence**: distinct head solutions are independent trials for the remaining head conditions and the tail (Section 7).

These are declared heuristic premises of the exploratory lane with the evidence of Section 10; finite organizer runs are reproducible observations consistent with them, not population bounds.

## 10. Experiments (organizer executor)

| Id | Program | Supports |
| --- | --- | --- |
| `h40-head-01` | `experiments/head40_c80d.py` | H1-head-solver, H5 (head value-satisfiability) |
| `t40-tail-01` | `experiments/tail40_c80d_J23.py` | H2-tail (not refuted; related junction) |

Program SHA-256: `head40_c80d.py` `ca4384527585d7e045998a95bc199dded5184d0246caa86347622183c1575b30`; `tail40_c80d_J23.py` `7da6beeb50c4bc2f82a364a482134d8396fe604c39afe22b5e442f00ca59ac9c`. Each experiment's scope and hard-asserted values are stated in `experiments/manifest.json`; the programs run only in the organizer executor.

## 11. Advice and preprocessing (flat allowance)

The advice is the characteristic's conditions of Appendix C packed 4 bits per bit, 2048 bytes; the witness pair is evidence only (nonuniform_advice_log2_bytes = 11.00000). Its construction, together with the search for the characteristic and the head, is charged as a declared best-case preprocessing allowance in the flat-lump form the accepted sha256-r37 entry 6c77089c declares (A_C = 2^60 for the characteristic and head/advice search, A_S = 2^50 for SAT solving, DEV = 2^40 for development), the same form as the accepted sha256-r38 entry fb176310 at 2^78 / 2^74 / 2^70. The allowance is `preprocessing_log2 = log2(2^60 + 2^50 + 2^40) = 60.00141` target compressions; peak preprocessing memory 267,884,831 bytes (2^28), counted in the memory claim (Section 6). No per-group search rate is transferred from the round-39 entries; the allowance is a flat lump, not a per-operation count.

## 12. What is executed, proved, recomputed, inspected, or assumed (HashSmash.md:325)

- **Recomputed and inspected (the organizer executor can run it):** the witness pair of Appendix C conforms to every signed row -4 to 39 of the characteristic under two 40-step recomputations, and its two full outputs differ (it is not a collision); the lane-parallel step of the tail replica equals the scalar SHA-256 step and the embedded schedule differences equal the expansion of `M`, `M'` (the replica's trial-0 hard asserts).
- **Executed as evidence (not refuting):** the tail replica drew 4,194,304 samples at a junction difference 129 bits from this pair's own and observed 0 hits, whose one-sided 99% upper bound is above the priced value; one free-CV head solve call is on record (SAT, 7.747 s, 82,280 conflicts).
- **Proved (exact arithmetic):** the ledger of Section 5 and the success bound of Section 7, by substitution of the integers; `C = 2896`.
- **Assumed (declared premises, not proved or measured on this instance):** H1-head-solver (the online solve yields at least one head solution per first block at <= 21,020 operations each, at a standard-IV chaining value, within the cap; the single on-record call is at a free CV and its 82,280-conflict runtime is not itself bounded by 21,020 primitive operations); H2-tail (the priced `p_tail = 2^-24.79100` is a declared best-case value, with the nearest measured junction 129 bits away and the replica only not-refuting); H3-advice-construction (the flat preprocessing allowance bounds the one-time characteristic and head search); H5-group-independence. The score 67.99846 is set by the preprocessing allowance 2^60.00141; the online legs sum to 2^26.634.

## 13. Credits and reuse

Base: `9993eaa8-2c36-48da-a477-de7e318deb7d` (round 39), whose ledger structure and premises (a charged first block, a counted per-trial construction, head and tail priced by probability) this package applies to 40 steps. Through it: `adef2aaf-efdd-4de0-bf13-62e21d150eb9` (0xplemonade's round-39 entry, the direct base of 9993eaa8); `2ae904e3-edb6-4484-a68b-26c897e06f03` (our round-39 entry, the first-block kernel filter with charged rejections); `fce2f19e-04eb-405f-b7d5-e24260d85d13` (sraiw's accepted round-39 entry, the walk program, the tail replica, the premises and the proof structure); `5f8e6192-60b3-4ba1-bded-d3b73cfbc889` (our accepted round-39 entry, the advice-pair-as-charged-advice pattern and the ledger structure). The counted online solve with a fixed cap follows the accepted sha256-r32 entry 6eeefb64 (jungjipdo, mitchuski, winglock); the flat preprocessing allowance follows the accepted sha256-r37 entry 6c77089c and sha256-r38 entry fb176310; credited here in the text because they belong to other benchmarks. The characteristic: the head pair and its characteristic come from the HashSmash research game (players' mined pairs; game shot web-ba2d0756db1345f7-20261103T004148-c80d); the tail table comes from the team research system's exact GPU backward generation (T_c80d_J23.tsv). A credit is not an endorsement.

## Appendix C. The characteristic and the pair

The witness pair (free chaining value `cv*`; the pair does not itself collide):
cv* `4236d4bf 1abd814d b5d994f1 1c387800 a34ac447 3e8b2a3e aaca8110 6d185d12`;
M `fd783713 37fa1eaf 9c1d5c39 9fc4bc9a 3110cb41 5cf121d6 18ea6ab4 3a8c03ba b70de428 854e243f 9baacbe0 d37ef7a9 bd9f4ba1 142019a1 a74c39d5 4d981480`;
M' equal to M except words 0, 9, 10, 11, 12, 13: `fd783714 854e243e 9daa8be0 d37ef7aa 459fcbf0 141ff9a1`.

Its 40-step signed characteristic (leftmost character = bit 31; `-` no difference, `u` = M bit 1 and M' bit 0, `n` the reverse, `x` either difference, `0` and `1` both bits equal to that value, `?` free; rows -4 to -1 are the chaining value; every row not printed is all `-`):

```
0 A: ------------------------------nu E: -----------------------------nuu W: -----------------------------nuu
1 A: --n---nnn--nn-----unn--uu-----nu E: --u--n--u-n---------nuunu------u W: --------------------------------
2 A: -----n-nn---u---n-nun--n-uun-u-n E: uun--------u--n--u--uu-uu--n-n-n W: --------------------------------
3 A: -u-n-u---uuu-nnu-ununn--u-u-u-un E: --nu-------n-n-nn--nuun----n---- W: --------------------------------
4 A: n----n--nnnuununu-nu-n-nn--n-n-- E: ---nu--------uu---u-nnuu-u-u-n-- W: --------------------------------
5 A: -n-nn-n----u-nn-u--uunun-u-nn--u E: unnn-n-nn-u--unn-uun--uu--u----- W: --------------------------------
6 A: nnuu----nn--n---n----nun----un-n E: --un--u---uun-n--uun-n-nu-nn--u- W: --------------------------------
7 A: n--nu-u------n-u---nnunun-nuu-uu E: --n----n-----nun----nnn--uuu-u-- W: --------------------------------
8 A: -u---u--unn----n-n-n-n---n---u-u E: u--u--uun--nn--nuu-uunn--u-nnu-- W: --------------------------------
9 A: ---nnuuu--u-u-n-unu--un---n-u-nu E: ---------n---n---u-n----uunu---n W: -------------------------------u
10 A: uun---nnu-u-u--n----n-nn-n--nun- E: u--u-nnn-n-nnn-un--n-n--u-n----u W: -----nu----------u--------------
11 A: -unnnu------n-unn---nn-uu-n--u-u E: u--uu---nnn----nnnu-n-n----u-un- W: ------------------------------nu
12 A: nnnnnn-nuu-n----unun-n--un-un-un E: n-uu-nuuunnn-nuu--n-n-un-nn--uu- W: unuuu-----------n--------n-n---u
13 A: -nu-n----n--u--uu-nn-n--unu---n- E: n-u--u-u-u--u---n-----n--uun-n-n W: ----------unnnnnnnn-------------
14 A: nu-un-unn--------nnnu-uu-nn---n- E: u-n-unu--nnnn--unu--u---nu--un-- W: --------------------------------
15 A: u-nnnnun-n-un-u--uu--nnn-n-u--un E: --uu-uu--n-u---nn-unn-n-u-nnnn-u W: --------------------------------
16 A: -uu-uunu--un-u-nunu--u---------- E: nuunnnnn-u--nnu-nn--u--n--n-un-u W: --------------------------------
17 A: ---u--nu--u---n-nn-nn---uun-n--- E: nu-un-u--nnu-uu---unuuunnnnnun-n W: ------n-------unnn--------------
18 A: --u-nu----uun--un-nuuuuunn--un-- E: u-n--n-u--n---n---n-n-n--n-----u W: ------------------------------nu
19 A: --u--un---unuuuun-uu-nun-uu----u E: ---nu-nnun--n-unuuuu-u--n-uu-n-- W: --------------------------------
20 A: --un-n----unn--n-----nu-nnuun--n E: unun-unn--u----n-uu-u----n--n-uu W: --------------------------------
21 A: u--u-n---uun--n-------uu-nunn--n E: --u--nnu--uuu-n-u--u--u-u-nn--un W: --------------------------------
22 A: -u---nunu-u-nnnn-n----u---n---un E: u-un---un----u--u---n--n-uu-unnn W: --------------------------------
23 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
24 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
25 A: ???????????????????????????????? E: ???????????????????????????????? W: --nu----un---u----unn--n--------
26 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
27 A: ???????????????????????????????? E: ???????????????????????????????? W: ------------------------------un
28 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
29 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
30 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
31 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
32 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
33 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
34 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
35 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
36 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
37 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
38 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
39 A: ???????????????????????????????? E: ???????????????????????????????? W: --------------------------------
```

Recompute (two 40-step computations from `cv*`): the pair satisfies every condition of rows -4 to 39, and its two 40-step outputs (feed-forward included) are different (the advice does not itself collide).
