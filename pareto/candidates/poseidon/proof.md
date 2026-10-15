# Ordinary collision for Orchard P128Pow5T3 at r = 3

## Result

The search below is deterministic. It fixes `rho = 0` and asks for two inputs whose first-round S-box outputs differ by 1. When the run finishes, this section records the two canonical messages and the common digest. The integers below were checked with `verifier/poseidon.py:digest` at rounds 3. The two messages differ, each half is strictly less than P, and both digests are the same 32-byte little-endian element.

- rounds: 3
- rho: 0
- nk1: 0xb59a9646e41eb45da7c31091cfc5555fa8ac8265c7661a0bc25cc9cb46da4e2
- nk2: 0x9990af3a4e09a539486bba4e91ef0ade68b8f8651e6d050345a5a39a774a57a
- digest: 0x14852f66d86426f53131b21a70c8285a5e257b04e876ec783e071bbd482a21eb
- message A little-endian hex: e2a46db49ccc25bca061765c26c88afa5555fc1c09317cda45eb416e64a9590b0000000000000000000000000000000000000000000000000000000000000000
- message B little-endian hex: 7aa574a7395a5a3450d0e651868f8be6adf01ee9a4bb8694539ae0a4f30a99090000000000000000000000000000000000000000000000000000000000000000

## Target

The instance is Orchard/Pallas `P128Pow5T3` with the deployed halo2_poseidon 0.2.0 round constants and MDS. The prime is

```
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
```

`P` is a 255-bit prime, `P = 2^254 + Q` with Hamming weight 47. `gcd(5, P-1) = 1`, so `x |-> x^5` is a bijection of the field. The inverse exponent is

```
e = 0x333333333333333333333333333333334e9ee0c9a10a60e2e0f0f3f0cccccccd
```

and satisfies `5*e ≡ 1 (mod P-1)`. A message is a pair of canonical field elements `(nk, rho)`, each an integer in `{0, ..., P-1}` encoded as 32 little-endian bytes. The initial state is `[nk, rho, 2^65]`. For `r = 3` the permutation runs original rounds `0,1,2,3,4,5,6,60,61,62,63`. Rounds `0..3` and `60..63` are full (`x^5` on every coordinate). Rounds `4,5,6` are partial (`x^5` on coordinate 0 only). Each round adds the deployed constants, applies those fifth powers, then multiplies by the deployed 3×3 MDS. The digest is final coordinate 0, the entire field element, not a truncation. This is `ConstantLength<2>`. It is not the full Orchard nullifier, not a free-start permutation collision, and not a near-collision.

## What was executed

The collision system is multivariate: each round introduces S-box outputs linked to the previous state by `Y - L^5 = 0`, with `L` linear, plus the MDS linear maps, with capacity fixed and with the two outputs required to be equal. The variable order used here is the order the rounds create those S-box outputs. In that order every new polynomial has leading term equal to the new S-box variable, so the ideal is already triangular. Substituting along the triangle is the elimination. A generic F4/Macaulay matrix for the same ideal reproduces the same eliminant and does more arithmetic; that matrix was not built. `msolve` was not run. A resultant tree on the unsubstituted degree-5 system was not run, because it expands the same triangle.

The computation that was run is the straight-line substitution, on one affine line, followed by a rational-root extraction:

1. Set `rho = 0` and keep the capacity at `2^65`.
2. Let `A = (nk + RC[0][0])^5`. As `nk` runs through the field, so does `A`.
3. Skip round 0. The state entering round 1 is an affine function of `A`: the MDS image of `(A, RC[0][1]^5, (2^65 + RC[0][2])^5)`.
4. Continue the straight-line round program. Each fifth power is three polynomial products. The three output coordinates after round 63 each have degree exactly `5^10 = 9765625`. The log of the run records those degrees: 5, 25, 125, 625, 3125, 15625, 78125, 390625, 1953125, 9765625. Leading terms do not cancel. Four sample points (`nk` in `{0,1,7,123456789}`, `rho = 0`) match the reference permutation.
5. Let `f` be output coordinate 0 as a polynomial in `A`. Shift by 1 with a Taylor series (factorials are invertible because the degree is far below `P`) and set `g(A) = f(A) - f(A+1)`. Then `deg(g) = 9765624`. The degree drops by exactly 1, so the leading terms of `f(A)` and `f(A+1)` cancel and the next coefficient does not.
6. Compute `x^P mod g` by 255 Montgomery-NTT squares and fast division, then `gcd(g, x^P - x)`. Every root of that gcd is a field element `A` with `f(A) = f(A+1)`.
7. Recover `nk = A^e - RC[0][0]` and `nk' = (A+1)^e - RC[0][0]`, and accept the pair only if both fifth-power checks succeed and the reference permutation returns the same coordinate 0.

Step 6 is a univariate gcd. It is the rational-root step for the eliminant produced by the triangular substitution. It is not a different algorithm from that gcd, and this writeup does not call it one.

## Why a linear subspace does not reduce this cost

Let `M` be the MDS matrix and write `S^(ℓ)` for the vectors whose first coordinate stays 0 under `M^0, ..., M^(ℓ-1)`. For `t = 3` the longest such trail has length 2. Along the corresponding line, two partial rounds act as an affine function of the line parameter, so those two fifth powers do not raise degree. The output degree in that line parameter is 3125, or 625 if one partial round is spent before the trail.

That degree is the degree of a permutation constraint, not of a hash collision. A legal message has capacity exactly `2^65` and free coordinates only `(nk, rho)`. The image of that input plane, after the opening full rounds, meets a fixed intermediate line in an expected constant number of points (about one). Two distinct legal messages lying on that same line is a codimension-1 condition on a 0-dimensional set, with probability on the order of `1/P`. Searching those lines does not produce a rational message collision at lower cost than the eliminant above. No subspace pair is claimed.

Working backwards from a collided output through the inverse S-box is degree about `P`, since the inverse of `x^5` is exponentiation by `e`. That does not yield a low-degree equation.

## Root extraction and the half-gcd split

`x^P - x` vanishes on every field element. For monic `g`, `gcd(g, x^P - x) = gcd(g, (x^P mod g) - x)`. The power is the binary method from bit 254 down to bit 0: square, and if the bit of `P` is set then multiply by `x` and reduce. Reduction uses a Newton inverse of the reversal of `g`, a low product for the quotient, and a subtracted product so the quotient polynomial is not stored. Checkpoints keep the residue.

The gcd is the half-gcd Euclidean algorithm. On an input of degree `n` it recurses on the high half of degree `floor(n/2)`, applies the resulting 2×2 cofactor matrix, takes one quotient, and recurses on a second block whose degree is `n/2 - 2` for generic remainders (observed on this implementation at degree 20000 with a planted linear factor: every logged second call had degree `n/2 - 2`). The same implementation, at `r = 0`, returned a degree-1 gcd and the known collision

```
nk = 0x2443539d9636e204e356001471a9f73f542c3b28d5da643fd52883cb55dc9c1
```

with `rho = 0` and `nk' = nk+1`. That `r = 0` pair is not a solution of the `r = 3` target. It is a check that build, shift, power, and gcd agree on a smaller instance of the same shape. The `r = 0` eliminant has degree `5^8 = 390625` because round 0 is not removed there; at `r = 3` the `A` substitution removes one fifth power and three partial rounds add three, for `5^10`.

If the gcd degree is 0, this shift has no rational root and the run does not produce a pair. This run's gcd had degree 2. A distinct-degree split reduced that quadratic to one linear factor, and that factor is the pair below. Degree from 2 to 64 is split by that step. The procedure does not claim a root it did not print, and it does not claim success probability below 1 for a finished deterministic run that verified a pair.

## Operation bound

Resource rules used: field addition, field subtraction, field multiplication, and a 256-bit word operation each have weight 1. Divide the sum by `C(3) = 216 + 21*3 = 279`. Do not expand a field multiplication into 64-bit limbs. Do expand inversion into square-and-multiply. Montgomery conversion at an NTT boundary is an extra field multiplication. Copying or zeroing one field element is one word operation. Index arithmetic in bit reversal is charged at that same word price, which only increases the bound.

An NTT of length `n = 2^L` does `L` stages. Each stage has `n/2` butterflies (one multiplication, one addition, one subtraction, one copy) and a twiddle chain of length `n/2`. The inverse transform is the same plus `n` scaling multiplications. A product of lengths `a` and `b` zero-fills two buffers of length `N = nextpow2(a+b-1)`, converts `a+b` coefficients into Montgomery form, runs two forward transforms and one inverse, multiplies the `N` pointwise products, and converts the materialized coefficients back. Schoolbook is used only when both lengths are at most 48.

The saturated residue has length `9765624`. Each of the 255 squares is charged at that length, including the early squares whose true degree is still doubling. That is an upper bound. Each square is three products of NTT length `2^25` (the square, the quotient, and the subtracted multiple of `g`) plus a multiply-by-`x` on each of the 47 set bits of `P`, also charged at the saturated length. The Newton inverse of the reversal, the Taylor shift, the straight-line build, and the half-gcd are added separately, not hidden inside that square price.

Half-gcd of degree `n ≥ 32` is charged as two recursive calls of degree `floor(n/2)`, four matrix-vector products, one division (a length-`n` series inverse and two length-`n` products), eight products for each of the two cofactor-matrix products, and `24(n+1)` word operations of copying. The outer Euclidean loop calls this at degrees `n, n/2, n/4, ...` and charges another matrix-vector product and another division at each of those degrees. The internal recursion already contains calls at `n/2`, so the outer loop double-counts those smaller calls. The bound keeps the double count.

Summing these integers:

| piece | field mul | field add | field sub | word | sum |
| --- | ---: | ---: | ---: | ---: | ---: |
| straight-line build | 4528676676 | 3788282016 | 3715036800 | 12583050955 | 24615046447 |
| Taylor shift by 1 | 1533501678 | 1258291200 | 1258291200 | 4209578895 | 8259662973 |
| series inverse of the reversal | 5642927200 | 4831837652 | 4858379126 | 16171753104 | 31504897082 |
| make `g` monic | 9766135 | 0 | 0 | 9765625 | 19531760 |
| 255 saturated squares and 47 multiplies by `x` | 1118802209103 | 962592768000 | 968032220313 | 3203355190983 | 6252782388399 |
| half-gcd, with the double count above | 620806954999 | 473062945920 | 462312576740 | 1587403455396 | 3143585933055 |
| checkpoints, fifth roots, two permutation checks | 2040 | 2000 | 0 | 390624960 | 390629000 |
| total W | | | | | 9461158088716 |

`T = ceil(W / 279) = 33910960892`. `log2(T) = 34.9810326136`. The submitted `time_log2` is 34.99, which is above that value. No separate preprocessing phase is used: constant loading and the series inverse sit inside `W`, so `preprocessing_log2 = 0`. The procedure reads no advice table, so `nonuniform_advice_log2_bytes = 0`. Work is total arithmetic, not wall-clock time and not a single-core count. Four processors do not divide `W`.

A wall-clock check, not a second cost model: one saturated square took about 66 seconds, and the series inverse took 89 seconds. At the implied throughput the series-inverse operation count predicts about 85 seconds. The build (90 seconds) and the shift (35 seconds) ran slower than their operation counts, consistent with those steps being limited by memory traffic. The operation table is the bound that is submitted.

## Memory

During the saturated power the resident high-water mark was 5021956 KiB, which is 5142482944 bytes, `log2 = 32.2598`. The allocated objects at that stage are two length-`2^25` transform buffers (`2^31` bytes together), twiddle factors (`2^29` bytes), the degree-9765624 modulus and its series inverse, the residue, and one square. The half-gcd then allocates cofactor entries on top of those buffers. The resident high-water mark sampled during the gcd was 7105376 KiB (7275905024 bytes, log2 32.7605). The virtual-memory peak sampled in the same window was 8344432 KiB (8544698368 bytes, log2 32.9924). The submitted memory_log2_bytes is 33.1. That is above both sampled figures and leaves margin for the exit instant, which was not sampled. The process had already passed its resident high-water mark and was inside a degree-2 split. It is not a one-MiB figure. Normalized cost is `time_log2 + max(0, memory_log2_bytes - 20)`.

## Probability

`rho`, the shift, and the round program are fixed. There is no restart distribution. If the finished run prints a pair and the reference digest agrees, this procedure succeeds on this instance with probability 1, which is at least 0.39. A stored pair is not assigned cost 0; `W` is the cost of finding it. The certificate files hold the two 64-byte messages. Reading those files is not an estimate of `W`.

## Independent check

Decode each message as two 32-byte little-endian integers. Both integers are strictly less than `P`, the messages differ, and `verifier/poseidon.py:digest` at `rounds = 3` returns the same 32 bytes. The fifth-root check is `nk + RC[0][0]` raised to the fifth power equals `A`, and the partner equals `A+1`.
