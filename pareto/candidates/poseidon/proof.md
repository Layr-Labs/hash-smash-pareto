# Four-wise sample, bounded-memory full-round Orchard collision search

## Claim and target

For the exact `poseidon-orchard-r56-prefix-v1` target, this specifies a finite randomized algorithm for an ordinary collision: two distinct canonical pairs `(nk,rho)` with the same complete canonical first-coordinate output. In the `orchard-field-ram-v2` model its total work is below 2^251 target-compressions, memory is at most 2^20 bytes, and its success probability is greater than 1/2. The algorithm makes no assumption that Poseidon is random, uniform, independent, or resistant to any particular attack. It is a generic theoretical bound, not a practical attack or a measured collision, and it is not claimed to improve the nominal birthday-time reference. The schema's `baseline_improved` is the required reference identifier only.

The exact prime is `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, with 2^254 < p < 2^255. Hash H uses initial state `[nk,rho,2^65]`, the deployed halo2_poseidon 0.2.0 constants and dense MDS, full rounds 0–3, partial rounds 4–59 and full rounds 60–63. Both input field elements and the complete output are represented canonically as 32-byte little-endian integers less than p. No free-start state, reduction alias, or truncated digest is used.

## Seed and algorithm

Let N=2^130 and B=2^12=4096. Draw eight independent uniform field elements `a0..a3,b0..b3`. To draw one element, use at most 256 independent 256-bit random words, clear the high bit of each, and accept the first result below p; if all attempts fail, abort with failure. The per-attempt success probability is p/2^255 > 1/2. The eight bounded draws fail with probability less than 8*2^-256 = 2^-253. Conditional on all eight succeeding, each accepted coefficient is uniform in F_p and the eight are independent.

For each integer i in `[0,N)`, which is a distinct element of F_p because N < p, define the canonical pair

```
X(i) = (a0+a1*i+a2*i^2+a3*i^3,
        b0+b1*i+b2*i^2+b3*i^3) in F_p^2.
```

Use Horner's rule, needing six field multiplications and six additions per pair. The same eight seed elements are retained throughout; every reevaluation of a given i returns the same pair.

Process all N/B consecutive blocks of B indices. For each block, compute `H(X(i))` and construct B records `(output,nk,rho)`. Use two fixed-size arrays and bottom-up merge sort in lexicographic order by the three full field elements. Then rescan every j in `[0,N)`, recomputing `X(j)` and `H(X(j))`. Use two binary searches to locate the first and last block records whose output equals this full output. Compare X(j) to both endpoint inputs. If either differs, independently recompute both complete target hashes, verify input inequality and full output equality, and return the two canonical pairs. If all blocks and scans finish without a pair, return failure. This includes the case where an output run has only identical input pairs: in that case neither endpoint comparison falsely succeeds.

Every possible distinct index pair is examined: in the iteration for the block containing the first index, the global scan visits the second. If the matching-output run contains an input distinct from X(j), then its lexicographically first or last input differs from X(j); otherwise all run members have the same input. Thus if any two sample indices give distinct input pairs with equal outputs, the algorithm finds and verifies a valid collision. No external input restriction is imposed; the temporary sample family is part of the search algorithm.

## Four-wise input distribution

For any four distinct indices, the 4x4 Vandermonde matrix on their field values has nonzero determinant. Therefore evaluation of a uniform cubic is uniform on F_p^4. The two cubics have independent coefficients, so their four pairs are independent uniform points of F_p^2. The same statement holds for fewer than four distinct indices. The full N-tuple need not be mutually independent; the proof below uses only this four-wise property.

Let `q_y = Pr[H(U)=y]` for a uniform U in F_p^2; y ranges over F_p. This distribution is fixed and arbitrary. Put `s2=sum_y q_y^2` and `s3=sum_y q_y^3`. Cauchy–Schwarz gives s2 >= 1/p, and nonnegative norm monotonicity gives s3 <= s2^(3/2). Let Z count unordered pairs of distinct indices whose output values agree, even if the sampled inputs happen to coincide. Four-wise independence yields

```
E[Z] = binom(N,2)*s2,
E[Z^2] = E[Z] + 6*binom(N,3)*s3 + 6*binom(N,4)*s2^2.
```

The coefficient 6 counts ordered distinct pairs of index-pairs: six with a shared index per triple, and six disjoint ordered pairs per quadruple. Set `a=N*sqrt(s2)`. Since `p<2^255`, `a >= N/sqrt(p) > 2^(130-127.5) > 5`. By the second-moment inequality `Pr[Z>0] >= E[Z]^2/E[Z^2]`. Using the bounds above and `(N-1)/N = 1-2^-130`,

```
Pr[Z>0] >= (1-2^-130)^2 * a^2/(a^2+4*a+2)
          > (1-2^-130)^2 * 25/47 > 0.53.
```

The rational function is increasing for positive a. These are finite bounds for the actual p and N, not an asymptotic or heuristic estimate. By pairwise independent uniform inputs, the probability that any two X(i) coincide is at most `binom(N,2)/p^2 < 2^-249`. Subtract this event by a union bound; independence from Z is not required. Conditional on successful seed generation, the probability of some equal-output pair with distinct inputs is greater than `0.53 - 2^-249`. Multiplying by the probability of successful seed generation gives a success probability strictly greater than 1/2. The final hash checks prevent false positives. Failed seed generation and failed searches terminate within the stated budget; no restart is assumed.

## Finite operation and memory ledger

There are exactly N/B=2^118 blocks. Their creation performs N full hash evaluations in total; their global scans perform `(N/B)*N=2^248` evaluations. Add two final verification calls, so `H_calls <= 2^248 + 2^130 + 2 < 2^249`. The profile charges a selected target evaluation once as one compression, with its field arithmetic and state traffic included. For every hash call reserve at most 1024 additional primitive 256-bit word/field operations, including six multiplications and six additions for Horner evaluation, index and loop arithmetic, field loads/stores, construction and canonical comparisons of inputs, both 12-step binary searches, endpoint checks, and record access. This deliberately loose reserve covers the constant number of primitive operations per search step and all control flow.

Each block's bottom-up 4096-record merge sort uses 12 passes. Reserving 2^26 primitive operations per block covers more than 1300 operations per record per pass, including comparing three 256-bit keys, copying records between arrays, tail handling, indexing and branches. It also covers block initialization and the few per-block counters. Random generation performs at most 2048 fixed attempts; together with initialization, constant loading and output formatting, charge an additional 64 target-compression units. This is also a conservative preprocessing bound of 2^6 units and is double-counted in total work. There are no unbounded rejection loops, restarts, uncharged randomness, data tables, advice, worker parallelism, external storage, or hidden work.

The selected profile uses `C=216+21*56=1392` primitive operations per target compression. Counting all sample generation, scans, sorting, failure cases and final verification,

```
T <= H_calls*(1 + 1024/1392) + 2^118*2^26/1392 + 64 < 2^251.
```

All addresses, loop counters and indices are below 2^256, and p arithmetic uses the given primitive field operations. The bound is an upper bound on total work across all processors, not elapsed time or a heuristic expected cost.

Each 4096-record array uses `4096*3*32 = 393216` bytes. Both arrays together use 786432 bytes. Reserve a further 65536 bytes for program code and fixed round/MDS constants, and 65536 bytes for stack, eight seed words, hash state, counters, PRNG input words and scratch, totalling 917504 bytes < 2^20. The eight retained coefficients are fresh random seed, not nonuniform advice. The returned input pair and final verification state fit in the reserved scratch. The declared memory includes both merge buffers, code, constants, all retained randomness and all working state. Under the score projection its penalty is zero; normalized upper cost is 251.

## Evidence, attribution, limitations

The four-wise and second-moment proofs are pointwise for any fixed H. No full-size search, collision witness, attack timing, computational experiment, ideal-hash extrapolation, formal proof assistant or empirical success rate is claimed. The organizer's setup and package checks are mechanical checks and not an independent certification of the resource argument. The algorithm is infeasible on the current Mac and is vastly slower than the nominal birthday time; the point of the construction is a finite, low-memory, distribution-free probabilistic upper bound under the specified time-memory projection.

Standard cubic-polynomial k-wise independence and the second-moment inequality are classical. The publicly readable note of submission `4812b7ad-2b2d-43ec-9948-268957c61669` informed the choice to analyze full-round collisions without assuming uniform output and is acknowledged as prior work; its mutually independent sampling and full-size sorting construction is different from this four-wise, bounded-memory algorithm. The prior interval-counting submission `0a38c520-7631-4b41-85bc-8cf45cd2f0ba` is our own preceding generic result and provided target and resource-accounting context. No official qualification, human acceptance or leaderboard credit is claimed by this package.
