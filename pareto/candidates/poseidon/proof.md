# Ordinary collision for Orchard Poseidon with two partial rounds

## Target

The target is `poseidon-orchard-r2-prefix-v1`. The permutation is Orchard P128Pow5T3 over the Pallas field

```
p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
```

with the deployed halo2_poseidon 0.2.0 round constants and MDS matrix. Every input is exactly 64 bytes, interpreted as two integers `(nk, rho)` in little-endian 32-byte form. Each integer must lie in `{0, 1, ..., p-1}`. The initial state is `(nk, rho, 2^65)`. The round indices are the full rounds `0,1,2,3`, the partial rounds `4,5`, and the full rounds `60,61,62,63`, in that order. Each round adds the pinned round constants, replaces every full-round coordinate, or only coordinate 0 in a partial round, by its fifth power, and multiplies by the pinned dense 3×3 MDS matrix. The digest is the entire final coordinate 0, encoded as 32 little-endian bytes. A collision is equality of those field elements for two distinct canonical inputs. Capacity, constants, MDS, exponent, round indices, and output width stay at the values above.

The same round function, called on the index list `(0,1,2,3,4,5,60,61,62,63)`, agrees with `verifier/poseidon.py` `permute` at partial-round count 2 on the three states `(0,0,2^65)`, `(1,2,2^65)`, and `(10^9, 2^200 mod p, 2^65)`.

## Degree of one slice

Write `H(a,b)` for the final coordinate 0 on input state `(a, b, 2^65)`. For a fixed second input `b`, this is a polynomial function of `a`. The initial degrees in `a` are `(1,0,0)`. Adding a constant does not raise degree. A fifth-power S-box multiplies the degree of that coordinate by 5. A partial round applies the S-box only to coordinate 0. The MDS step replaces the state by linear combinations, so the maximum degree does not increase. After `k` rounds the maximum degree is therefore at most `5^k`. The target applies 10 rounds, and

```
5^10 = 9765625.
```

Hence there is a polynomial `H_b(X)` of degree at most `D = 9765625` with `H_b(a) = H(a,b)` for every field element `a`. The difference

```
g_b(X) = H_b(X) - H_0(X)
```

also has degree at most `D`. All nine deployed MDS entries are nonzero, but the degree induction does not use that fact. Cancellation can only lower the degree. `D < p`, so a polynomial of degree at most `D` over this field has at most `D` roots unless it is the zero polynomial, and `k!` is nonzero in the field for every `k ≤ D`.

## Algorithm

The procedure always performs two trials, trial 1 and then trial 2, with disjoint random coins. It never stops early. If both trials succeed, it returns the pair from trial 1. The charged work is the work of two completed trials on every outcome, including sampling failure, the zero polynomial, and a gcd whose degree is not 1.

One trial:

1. Draw at most 256 independent uniform 256-bit words. Interpret each word as an integer `w` in `{0, 1, ..., 2^256-1}`. Accept the first `w` that lies in `{1, 2, ..., p-1}`, and call it `β`. If none of the 256 words is accepted, the trial fails.
2. For `a = 0, 1, ..., D`, evaluate `v_a = H(a, β) - H(a, 0)`. This uses two target permutations per abscissa.
3. If every `v_a` is 0, return the messages for first field element `1` and second field elements `0` and `β`, as encoded below. This is the identically zero case.
4. Otherwise recover the Newton coefficients of `g_β` from the values at `0, 1, ..., D`. In place, for `k = 1, ..., D` and for `i = D, D-1, ..., k`, replace `v_i` by `v_i - v_{i-1}`. After that pass, `v_k = Δ^k g_β(0)`. Set `f_0 = 1` and `f_k = f_{k-1} · k` for `k = 1, ..., D`. Invert all of `f_0, ..., f_D` with one Fermat inversion and Montgomery's batch product: form the prefix products, invert the last prefix by raising it to `p-2`, and walk backward. Set `c_k = v_k · f_k^{-1}`.
5. Convert Newton form to monomial form by Horner's rule. Start from `π(X) = c_D` and, for `k = D-1, D-2, ..., 0`, replace `π` by `(X - k) · π + c_k`. The result is `g_β`.
6. If the resulting polynomial has degree 0, the trial fails. A nonzero constant has no root, and the zero polynomial was already returned in step 3.
7. Make `g_β` monic by one Fermat inversion of its leading coefficient and one scaling of every coefficient.
8. Compute `X^p mod g_β` by left-to-right square-and-multiply. The binary length of `p` is 255 and its Hamming weight is 47, with leading bit 1. Initialize the accumulator to `X` and process the remaining 254 bits: square modulo the monic `g_β`, and multiply by `X` modulo `g_β` when the bit is 1. That is 254 squarings and 46 multiplications by `X`, hence 300 modular multiplications. The budget below allows 320.
9. Let `h = (X^p mod g_β) - X`. Compute `G = gcd(g_β, h)` by the Euclidean algorithm, making the current divisor monic at the start of each remainder step and then eliminating in place. Because the divisor is monic, each elimination coefficient is the current leading coefficient of the dividend; no inversion is performed inside the inner loop.
10. If the monic gcd has degree 1, write it as `X + c` and set `r = -c` reduced into `{0, 1, ..., p-1}`. Return the two messages below. Every other degree is a failed trial. In particular, degree 0 means there is no root, and degree greater than 1 means several distinct roots, which this procedure does not separate.

Message encoding. For a returned field element `s` and the trial's `β`, the two messages are the 64-byte strings

```
s as 32 little-endian bytes, followed by 0 as 32 little-endian bytes
s as 32 little-endian bytes, followed by β as 32 little-endian bytes.
```

In the identically zero case, `s = 1`.

The model primitive used for coins is one uniform 256-bit word. No advice string and no precomputed table of collisions is read. Both trials are sequential; the total is the sum of their operations.

## Why a returned pair collides

Throughout, `D < p`. The Newton identity `g(a) = Σ_k c_k · a(a-1)...(a-k+1)` holds for the unique polynomial of degree at most `D` that agrees with the computed values on `{0, 1, ..., D}`, because each factorial `k!` for `k ≤ D` is invertible. Horner's recurrence produces that same polynomial. The polynomial function of `H(·, β) - H(·, 0)` has degree at most `D` and agrees with these values, so it equals `g_β` as a function on the whole field.

In characteristic `p`, the derivative of `X^p - X` is `-1`. Therefore `X^p - X` is square-free, and

```
X^p - X = ∏_{u in F_p} (X - u).
```

For a nonzero polynomial `g` of degree less than `p`,

```
gcd(g, X^p - X) = gcd(g, (X^p mod g) - X),
```

and that gcd is the product of `(X - u)` over the distinct roots of `g` in the field. Its degree is the number of distinct roots. A monic gcd of degree 1 is `X + c` with unique root `r = -c`. Then `g_β(r) = 0`, so `H(r, β) = H(r, 0)`. The two messages differ in the second field element because `β ≠ 0`. Both field elements are in `{0, 1, ..., p-1}`, so both encodings are canonical 64-byte inputs. Their digests are the same 32-byte encoding of one field element.

If every sample value is 0, then `g_β` has `D+1` roots and degree at most `D`, so `g_β` is the zero function. Then `H(1, β) = H(1, 0)`, and the messages for `s = 1` are distinct canonical inputs with equal digests.

A trial that fails the sampling test, or whose gcd degree is not 1, returns no pair. The procedure succeeds when at least one trial returns a pair.

## Success probability

Let `ε = 2^{-100}`. The number of accepted residues is `p - 1`. Since

```
p = 2^254 + 0x224698fc094cf91b992d30ed00000001,
```

one has `p - 1 > 2^254`, so a uniform 256-bit word lands in `{1, ..., p-1}` with probability greater than `1/4`. The probability that all 256 words fall outside that set is therefore strictly less than `(3/4)^256`. From `3^5 = 243 < 256 = 2^8`,

```
3^256 = 3 · (3^5)^51 < 3 · (2^8)^51 = 3 · 2^408 < 2^2 · 2^408 = 2^410 < 2^412.
```

Hence `(3/4)^256 = 3^256 / 2^{512} < 2^{-100}`. Sampling fails with probability less than `ε`. Conditional on acceptance, `β` is uniform on `{1, ..., p-1}`.

The following statement is the score-critical heuristic H-slice-root. It is not proved in this note.

> For `β` uniform on `{1, ..., p-1}`, the polynomial `g_β` of the r=2 target has exactly one distinct Pallas root with probability at least `1/4`.

Under that statement, one trial succeeds with probability at least `(1-ε)/4`: sampling must succeed, and the accepted `β` must be a one-root element. The identically zero polynomial is an additional success and is not required for the bound. A one-root polynomial is exactly the event that the monic gcd has degree 1. The two trials use independent words, and success of a trial is a function of that trial's words, so the two success bits are independent once the marginal bound is granted. The probability that both trials fail is at most

```
(1 - (1-ε)/4)^2.
```

The complementary probability equals `[7 - 6ε - ε^2] / 16`. This exceeds `2/5`, because

```
5(7 - 6ε - ε^2) - 32 = 3 - 30ε - 5ε^2
```

and `30ε + 5ε^2 < 32ε = 2^{-95} < 3`. The procedure therefore succeeds with probability strictly greater than `2/5 = 0.40` whenever H-slice-root holds. The submitted success probability is `0.40`. There is no third trial and no restart. If the true probability of exactly one root is smaller than `1/4`, this numerical claim is false; the time bound does not contain spare trials that would replace it.

## Measurements behind H-slice-root

These counts use the deployed Pallas modulus, round constants, MDS, and capacity `2^65`, and the same add-then-S-box-then-MDS order as the target. They do not use the target index list. For each listed index list the Newton polynomial of `H(a,0)` on `a = 0, ..., D` was compared with a direct evaluation at `a = D+3`. The values agreed, and the monomial degree was exactly `5` raised to the number of indices in the list: degree 25, 625, and 125 respectively. That checks the interpolant and shows that the degree upper bound is tight on these three reduced lists. It is not a claim that the ten-round target degree is exactly `5^10`.

Consecutive second inputs `β = 1, 2, ...` :

| Index list | Degree | β values | Distinct-root counts | Count of exactly one root |
| --- | --- | --- | --- | --- |
| `0,60` | 25 | 1 through 20 | 1,1,0,1,0,1,0,2,2,0,0,2,0,2,2,1,1,0,2,1 | 7 of 20 |
| `0,1,62,63` | 625 | 1 through 7 | 1,0,2,0,3,1,1 | 3 of 7 |
| `0,4,60` | 125 | 1 through 10 | 1,0,1,1,0,0,1,2,1,0 | 5 of 10 |

Uniform nonzero samples use SHA-256 as specified by FIPS 180-4. For a domain string and a counter `c` starting at 0, interpret the 32-byte SHA-256 digest of `domain || uint32le(c)` as a little-endian integer and accept it when it lies in `{1, ..., p-1}`. The degree-25 domain is the ASCII string `HS-POSEIDON-BETA-D25-v1`. The degree-125 domain is `HS-POSEIDON-BETA-D125-v1`. The degree-25 stream accepted 32 values in 101 draws, in one pass, with distinct-root counts

```
2,4,0,2,1,1,2,1,1,0,1,4,2,0,2,2,0,2,1,0,1,0,0,0,0,2,1,1,1,0,1,0
```

so exactly one root occurs 11 times. The degree-125 stream was inspected after 8 accepts, where exactly one root had occurred twice, and was then continued without replacement through 32 accepts. Those 32 accepts took 139 draws. The full sequence is

```
1,2,3,4,2,0,0,1,1,0,1,0,0,1,0,0,2,1,1,0,1,1,0,0,2,1,1,0,1,2,0,1
```

so exactly one root occurs 13 times. No further draws were taken. Across the five completed series, exactly one root occurs in `7+3+5+11+13 = 39` of `20+7+10+32+32 = 101` trials. Every completed series has a one-root frequency of at least `11/32`. The floor `1/4` lies below those five frequencies. The samples are small, the consecutive series are not uniform, and the degree-125 series was extended after its prefix was seen. None of these series is the ten-round target.

On index list `(0,60)` and `β = 1`, the same Newton-and-gcd procedure returned a degree-1 gcd whose root is

```
1082000611383057448526764194216407303369567148163237967480880096101339401657.
```

Evaluating the round function on indices `(0,60)` at `(root, 0, 2^65)` and `(root, 1, 2^65)` produced the same coordinate 0. The corresponding 64-byte messages are

```
b98d6a4fec62204b68bea941f3b788351f08c39d4e5591d73e62573a016464020000000000000000000000000000000000000000000000000000000000000000
b98d6a4fec62204b68bea941f3b788351f08c39d4e5591d73e62573a016464020100000000000000000000000000000000000000000000000000000000000000
```

This pair collides for those two round indices only. It was not evaluated as an r=2 target collision, and the ten-round attack was not executed. The root check does confirm that a degree-1 gcd produced by this reduction yields `r = -c` and equal slice outputs.

H-slice-root extrapolates the one-root frequencies above from degrees 25, 125, and 625, and from at most one partial round, to the target slice of degree at most `5^10` with eight full rounds and two partial rounds. A relation special to the full index list could make the target frequency smaller than `1/4`. The heuristic records that possibility. The classical Poisson picture for the number of roots of a random polynomial, with mean near 1 and `P(K=1)` near `1/e`, is motivation for looking at a floor below the measured frequencies. It is not a proof for this structured family, and the submitted floor is `1/4` rather than `1/e`.

Gröbner-basis analyses of Poseidon model several field elements as simultaneous variables and then depend on an extrapolated solving degree. This attack does not. It fixes the second rate element, builds one univariate polynomial by interpolation, and extracts a single linear factor of `gcd(g, X^p-X)`. The degree bound used for the number of sample points is the round-by-round bound proved above.

## Operation prices

The cost model is `orchard-field-ram-v2` with rules `orchard-finite-work-v1`. One target permutation, meaning one call to the r=2 round list above, costs 1. One canonical Pallas addition, subtraction, or multiplication, and one primitive 256-bit word operation, each cost 1 before division by `C(2) = 216 + 21·2 = 258`. A field multiplication is one primitive; it is not expanded into limb products. Inversion and exponentiation are expanded into multiplications, squarings, and word operations. The algorithm is an explicit arithmetic circuit of loops, not an `ω`-parameterized matrix algorithm, so the matrix exponent 2.8 is not substituted for the cubic elimination count. Work is summed across the two sequential trials before the logarithm. Memory addresses fit in one 256-bit word: every index used below is smaller than `2n`.

Let `n = D + 1 = 9765626`. Each trial charges `2n` target permutations: two calls at each of `n` abscissae. Two trials charge

```
H = 4n
```

permutations. Internal arithmetic of a permutation is inside that unit and is not added again. Packing an input and storing an output are outside the unit and are charged below.

The remaining primitive count for one trial is bounded by

```
W1 = 20 n^3 + 12048 n^2 + 20000 n + 100000.
```

Two trials charge `W = 2 W1`, including failed trials. The pieces of `W1` are the following upper bounds.

Cubic elimination. The Euclidean algorithm performs at most `n` remainder steps because each successful remainder has strictly smaller degree. Each step, after the divisor has been made monic, performs at most `n` elimination rounds, and each round updates at most `n` coefficients in place. Each coefficient update is charged as these 20 word or field primitives: load the elimination scale; load the modulus coefficient; multiply those two field elements; load the dividend coefficient; subtract; store the dividend coefficient; add the shift to the inner index; shift that sum by 5; add the dividend base address; shift the inner index by 5; add the modulus base address; increment the inner index; compare it with the degree; branch; compare the address with the array length; branch on that comparison; copy the scale into the multiplier input; clear the field temporary used by the multiply; test whether the scale is zero; branch on that test. The last four are bookkeeping charged on every coefficient so that a direct implementation can spill the scale and the product. The product of these limits is `20 n^3`.

Quadratic terms, summing to `12048 n^2`:

- Forward differences perform `n(n-1)/2` subtractions. Each subtraction is charged these 16 primitives: load `v_i`; load `v_{i-1}`; subtract; move the difference into the store register; store `v_i`; shift `i`; add the value-table base; form `i-1`; shift that index; add the base again; decrement `i`; compare `i` with `k`; branch; compare `k` with `D`; branch; compare the address with the array length. Sixteen times `n(n-1)/2` equals `8 n(n-1)`, which is at most `16 n^2`.
- Horner conversion performs at most `n(n+1)/2 ≤ n^2` coefficient updates. Each update is charged 16 primitives: load the old coefficient; multiply by the node index; load the shifted coefficient; subtract; store; shift the source index; add the source base; shift the destination index; add the destination base; increment; compare; branch; copy the node index into the multiplier; test the loop limit; branch; bounds-check the destination. The charge is at most `16 n^2`.
- Each modular multiplication of two polynomials of degree less than `n` is bounded by `32 n^2`. A schoolbook product step is these 16 primitives: load the first factor; load the second factor; multiply; load the accumulator; add; store; shift the first index; add the first base; shift the second index; add the second base; add the two indices; shift that sum; add the accumulator base; increment; compare; branch. A monic-reduction step is these 16: load the scale; load the modulus coefficient; multiply; load the destination; subtract; store; shift the modulus index; add the modulus base; add the shift; shift the destination index; add the destination base; increment; compare; branch; bounds-check; branch on the bounds check. There are at most `n^2` steps of each kind. The exponentiation uses at most 320 such modular multiplications, which is `10240 n^2`, charged as `12000 n^2`.
- Making the Euclidean divisor monic scales at most `n` coefficients in each of at most `n` steps. Each coefficient is charged 8 primitives: load, multiply by the inverse, store, shift the index, add the base, increment, compare, and branch. That is at most `8 n^2`, charged as `16 n^2`.

Linear and constant terms. The sum of the following itemized bounds is at most `20000 n + 100000`.

- At most 256 sampling attempts. Each attempt is charged 8 primitives: draw one word, compare it with 1, branch, compare it with `p`, branch, increment the counter, compare the counter with 256, and branch. Encoding the two 64-byte messages is inside the same constant. Together these cost at most `10000` primitives, charged inside the constant `100000`.
- Evaluation traffic outside the permutation unit: at most 32 primitives per abscissa for the counter, the two input packings, the two output stores, the field subtraction, and the loop branch. That is at most `32 n`.
- The factorial chain, prefix products, backward batch-inversion products, and scalings by `f_k^{-1}` are at most `6n` field multiplications. At 10 primitives each, that is at most `60 n`, charged as `80 n`.
- Scaling a polynomial by the inverse of its leading coefficient costs at most `16 n`.
- Degree scans and zero tests cost at most `16 n`.
- Fermat inversion of `x^{p-2}` starts from the accumulator `1` and, for every one of the 255 bits, squares and then multiplies by `x` when the bit is set. The Hamming weight of `p-2` is 77, so this is 255 squarings and 77 multiplications, 332 field multiplications. Each of those 332 field multiplications is charged 8 primitives: the field multiplication, a load of the base, a store of the accumulator, a bit test, a shift of the exponent, a comparison, a branch, and a move of the selected bit. That is 2656 primitives per inversion. The trial inverts at most `n + 2` elements: one leading coefficient, one factorial prefix, and one divisor lead per remainder step. That is at most `2656(n+2)` primitives.

These linear pieces sum to at most `2800 n + 15312`, and `2800 n + 15312 ≤ 20000 n + 100000` at `n = 9765626`. The gap is unused linear budget, not a second copy of the cubic term.

Thus one trial's non-permutation work is at most `W1`, and the attack charges `W = 2 W1` whether or not a trial returns a pair.

## The time bound

Substitute `n = 9765626`:

```
n^2 = 95367451171876
n^3 = 931322860717802734376
W1  = 18627606201603086069568
H·C + W = 4 n C + 2 W1 = 37255212403216250265168
C · 2^67 = 38074079768136514535424
```

The first integer is strictly smaller than the second, so

```
T = H + W / C < 2^67.
```

The same integers with `2^66` in place of `2^67` reverse the inequality, because the cubic term alone already exceeds that threshold: `2 · 20 · n^3 = 37252914428712109375040 > 258 · 2^66 = 19037039884068257267712`. Therefore `log2(T)` lies strictly between 66 and 67. The submitted `time_log2` is 67, the least integer upper bound on this budget. It is not an estimate of a faster polynomial-arithmetic implementation. Replacing the inner-loop charge 20 by 21 makes `4 n C + 2 W1` exceed `C · 2^67`, so the budget has no anonymous extra primitive per coefficient update. The twenty operations listed above are the whole inner-loop charge.

`preprocessing_log2 = 0` and `nonuniform_advice_log2_bytes = 0`: the procedure reads no advice and performs no precomputation outside the two charged trials.

## Memory

Five arrays are allocated for the whole trial and reused, rather than grown transiently. Their lengths sum to `6n` field elements:

| Array | Length in field elements | Role |
| --- | --- | --- |
| V | `n` | Sample values, then the exponent accumulator after `g_β` has been stored |
| G | `n` | Monomial coefficients of `g_β` |
| R | `n` | Euclidean partner polynomial |
| P | `2n` | Unreduced product |
| S | `n` | Horner and scaling scratch |

That is `6n` field elements. Each stored element is a canonical residue in `32` bytes. Round constants for 64 rounds occupy `64 · 3 · 32 = 6144` bytes, the MDS matrix occupies `9 · 32 = 288` bytes, and the modulus, the two messages, and `β` occupy less than `1024` bytes. Code for the loops above fits in the remaining part of a `2^20`-byte code-and-constant allowance. Every cell is written before it is read. The reserved volume is

```
6 · 9765626 · 32 + 2^20 = 1876048768 < 2^31 = 2147483648.
```

The submitted `memory_log2_bytes` is 31. Under the Orchard scoring projection the normalized cost is `time_log2 + max(0, memory_log2_bytes - 20) = 67 + 11 = 78`. The claim records the raw bounds 67 and 31; the projection is the adapter's score, not a second time claim.

## Execution status

The degree checks, the five root-count series, and the degree-25 pair for `β = 1` on indices `(0,60)` were carried out. No message pair was produced or checked for the target round list `(0,1,2,3,4,5,60,61,62,63)`. The submitted cost is the budget of that unexecuted procedure.
