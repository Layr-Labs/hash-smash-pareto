# r = 3 Orchard collision by a two-round skip

Ordinary collision for `poseidon-orchard-r3-prefix-v1`. The modulus is the Pallas prime

p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001.

A message is two canonical little-endian field elements, each strictly less than p. The initial state is (nk, rho, 2^65). The rounds are the deployed rounds 0, 1, 2, 3, 4, 5, 6, 60, 61, 62, 63 of halo2_poseidon 0.2.0: add the deployed round constants, raise every coordinate to the fifth power in a full round and only coordinate 0 in a partial round, then apply the deployed 3×3 MDS. Indices below 4 and at least 60 are full rounds. The digest is the entire final coordinate 0.

The map x ↦ x^5 is a bijection of the field, because gcd(5, p − 1) = 1. Write x^{1/5} for the inverse map, which is exponentiation by the inverse of 5 modulo p − 1.

## The curve that skips two nonlinear layers

Let M be the deployed MDS and write M_i for its i-th row. Let c^{(k)} be the deployed round-constant vector of round k, and let

K = (2^65 + c^{(0)}_2)^5.

The two rate elements after the round-0 S-box are free, and the capacity element is K. The state that enters the round-1 S-box is therefore an affine plane. Inside that plane there is a line on which every coordinate is either independent of the line parameter or has zero constant term. On that line the round-1 S-box is linear in a fifth power of the parameter, so both the round-0 S-box and the round-1 S-box drop out of the degree count.

Concretely, solve for field elements a0, a1, b0, b1 as follows. The direction (b0, b1) satisfies

b0 M_2,0 + b1 M_2,1 = 0,

and the solution used here is b0 = M_2,1, b1 = −M_2,0. Both are nonzero. The base (a0, a1) solves the 2×2 system

a0 M_0,0 + a1 M_0,1 = −c^{(1)}_0 − K M_0,2,

a0 M_1,0 + a1 M_1,1 = −c^{(1)}_1 − K M_1,2.

The determinant M_0,0 M_1,1 − M_0,1 M_1,0 is

9447423477431292545946511771861146227523252734540954864491633838524783056108,

which is nonzero, so there is one solution. It is

a0 = 26423688467856277395344114545906460604958006772231448874854208420150712184437,

a1 = 10115894732851039909259149659720871312848186328176966730228545878049859860155.

Define

D_i = b0 M_i,0 + b1 M_i,1,

C_i = a0 M_i,0 + a1 M_i,1 + K M_i,2 + c^{(1)}_i.

The construction forces D_2 = 0 and C_0 = C_1 = 0. The two nonzero direction coordinates are

D_0 = 17507788608277026017839124676887059124499120322495927799406946236694012748458,

D_1 = 9952007621573045305190690792618508888597688982621060415715206235516014093119,

and the constant coordinate is

C_2 = 4386804503965664894627402629137738961009814456374217284364700524756457976336.

For each field element X set λ = X^{1/5} and

s0 = a0 + λ b0, s1 = a1 + λ b1,

nk = s0^{1/5} − c^{(0)}_0, rho = s1^{1/5} − c^{(0)}_1.

Both message elements are in {0, …, p − 1}. Different values of X give different λ, hence different s0, because b0 ≠ 0, hence different nk. The resulting messages are therefore distinct whenever the parameters are distinct.

Running round 0 on (nk, rho, 2^65) produces S-box output (s0, s1, K) and MDS output M · (s0, s1, K). Adding c^{(1)} produces the round-1 S-box input (D_0 λ, D_1 λ, C_2). Its S-box output is

(D_0^5 X, D_1^5 X, C_2^5).

That is an affine function of X. The MDS of round 1, which is linear, keeps the state affine in X. Rounds 0 and 1 have both been applied, and every later coordinate is a polynomial in X of degree 1 at this point. The fifth powers that would have made the degree 25 are inside the message encoding, not inside the polynomial.

## Degree

From that affine state, the remaining rounds are 2, 3, 4, 5, 6, 60, 61, 62, 63. Six of them are full and three are partial, nine nonlinear layers in all. Write H(X) for the final coordinate 0 as a polynomial in X.

Track the degree-D leading vector L of the three coordinates, starting after the round-1 MDS at degree 1 with

L_i = D_0^5 M_i,0 + D_1^5 M_i,1.

A full round replaces L by M · (L_0^5, L_1^5, L_2^5) and multiplies the degree by 5. A partial round replaces L by L_0^5 times the first column of M and multiplies the degree by 5. In either case a zero output vector would stay zero. Evaluating the recurrence on the deployed MDS through the nine rounds leaves every coordinate nonzero after every round. The final coordinate-0 coefficient, at degree 5^9, is

22422092890086069301514433790408465908103586438175633615990032743912502134023.

Thus H has degree exactly n = 5^9 = 1953125. The same count is what the composed polynomial had: degree 1953125.

The eight full rounds of the target are not all present as degree multiplications. Two of their nonlinear layers are the skipped round-0 and round-1 S-boxes. The other six full rounds and the three partial rounds each multiply the degree by 5. A partial round does not cancel this degree: the leading coordinate 0 stayed nonzero, so the single partial S-box still contributes a factor 5.

## Algorithm

There is no advice string. The bases below are the integers 0 and 1, in that order, fixed before the execution.

Build H by composition. The state starts as the three polynomials (D_0^5 X, D_1^5 X, C_2^5). Apply the MDS, then each selected round: add constants, replace each S-boxed coordinate P by P^5, and replace the state by its MDS image. A fifth power is two squarings and one product.

For a base β, set f = H − H(β) and make no other change. Compute X^p modulo f by square-and-multiply, subtract X, and take the monic half-gcd of the two polynomials. The exponent p has 255 bits and Hamming weight 47, so the schedule that starts from the leading bit is 254 squarings and 46 multiplications by X. Each modular squaring is one product followed by reduction by the monic degree-n polynomial, using a Newton inverse of the reverse of f that is computed once per base. Multiplication by X is a shift and one scalar subtraction of the modulus.

X^p − X is separable because its derivative is −1, so the gcd degree is the number of distinct roots in the field. The root β is always one of them. If the gcd has degree 1, the base has no second root and the procedure goes to the next base. If the gcd has degree 2 and equals (X − r)(X − s), the quadratic formula returns both roots. The procedure then returns the two messages belonging to those roots. A gcd of any other degree is outside the path that this execution took; the cost bound below still covers the half-gcd itself.

A root lies in the field because it is a root of X^p − X. It is a root of f because the gcd divides f, so the two parameters have the same value of H and therefore the same digest. The messages differ because the parameters differ.

## Execution

The procedure was executed on this index list.

For β = 0 the constructed difference had degree 1953125. Its monic gcd with X^p − X had degree 1 and was X. That base has no second root. The procedure continued. This failed base is included in the cost.

For β = 1 the constructed difference had degree 1953125. Its monic gcd with X^p − X had degree 2. The roots were

r = 13768782537159585682094643193913549826095386322623631211636205761512609213242

and s = 1.

The message for r is (nk, rho) with

nk = 13072160540290311549004898157537406814579792797515271158927608126631628384239,

rho = 10348942081604705559077538401035514262487193192046920938729081134478529533138.

The message for s = 1 is

nk = 17946124148602739112217466493388044143735006600724443613447171569993166782735,

rho = 15696401230817611163028568727772910279185938734441472916034461153010233218439.

These are the files `certificates/message-a.bin` and `certificates/message-b.bin`, in that order. Their common digest is

8c9e81c0b8bf46772da708f555f1b310ec9f68c73207be8e39a9182286cd6011.

The organizer checker recomputes both digests from those files at partial-round count 3. That check does not use the polynomial. It is an independent confirmation that these two messages collide under the r = 3 round function.

The procedure reads no random words. Every execution builds the same H, tries β = 0, observes a degree-1 gcd, tries β = 1, and obtains the same degree-2 gcd. The executed path returns this pair. The success probability is 1. There is no third base and no stored advice.

## Cost

One r = 3 permutation costs C = 216 + 21·3 = 279 primitive units. A field addition, subtraction, or multiplication, and a primitive word operation, each cost one unit before division by C. A field multiplication is not expanded into limb products. Inversions are expanded. The matrix exponent 2.8 is not used. The bound counts the loops of the procedure above, once for the build and twice for the two bases. The failed base is not omitted.

Let n = 1953125 and m = n + 1 = 1953126. The transform length is N = 2^22 = 4194304, the least power of two that is at least 2n − 1 = 3906249. A primitive 2^32-nd root of unity exists because the multiplicative group has 2-adicity 32, so a primitive N-th root exists. Twiddles are multiplied on the fly. Bit-reversal indices may be stored; they are not field elements.

### One transform

An in-place transform of length L = 2^e does (L/2)·e butterflies and one bit reversal of L indices.

One butterfly is 16 operations: load both values, compute the on-the-fly twiddle and multiply by it, add, subtract, store both results, three address calculations, a loop increment, and a branch. Bit reversal of one index is 4 word operations. One transform of length L therefore costs

L · (8e + 4)

operations. At L = N and e = 22 this is 754974720 operations. Every product below whose operands have length at most m is charged at this length, which is an upper bound on the transform that the operand's own degree would have used.

A product is three transforms and one pointwise loop of 8 operations at each of N points, together with one normalization loop of 3 operations at each point on the inverse transform. That pointwise package is 11N operations and is listed separately from the transforms.

### Build, once

Nine rounds apply 21 fifth powers: six full rounds on three coordinates and three partial rounds on one coordinate. Each fifth power is two squares and one product, hence three products, and each product is three transforms. The build is 189 transforms,

189 · 754974720 = 142690222080,

plus 63 pointwise packages,

63 · 11 · N = 2906652672.

Early rounds are shorter than N. Charging them at N is the upper bound.

### Each base

The Newton inverse of the reversed modulus doubles precision from 1 through 2^21. That is 22 iterations. Two products per iteration, three transforms each, is 132 transforms,

132 · 754974720 = 99656663040,

and 44 pointwise packages,

44 · 11 · N = 2030043136.

Iterations shorter than N are charged at N.

Each of the 254 modular squarings is one product and two reduction products. None of the three operands is stored in transformed form, so each product is three transforms and the squaring's own forward and inverse transforms are the first of those three. The count is 8 transforms per squaring, 2032 transforms,

2032 · 754974720 = 1534108631040.

Pointwise work on those squarings is one square at 6 operations per point, two products at 8 operations per point, and three normalizations at 3 operations per point, 31N per squaring,

254 · 31 · N = 33025949696.

Each of the 46 multiplications by X shifts m coefficients and subtracts a scalar multiple of the modulus, 10 operations per coefficient,

46 · 10 · m = 898437960.

Reversals, scalar multiplications by MDS entries, and constant additions are charged together at 12532m. The itemized part is 4064m for two reversals on each of 254 squarings at 8 operations per coefficient, 360m for 90 MDS scalar multiplications at 4 operations, and 108m for the constant additions. The remainder up to 12532m is an allowance of 8000m, which also covers forming f, monic scaling, and solving the degree-2 gcd by one square root. The charge is

12532 · m = 24476575032.

### Half-gcd, each base

Let M(d) be the cost of one product of two polynomials with d coefficients, using a transform of length the least power of two that is at least 2d − 1, with 16 operations per butterfly, 4 per bit-reversal index, and 8d′ pointwise operations at that transform length. For d ≤ 1 the charge is 8.

The half-gcd charge H(s) on a degree-s input is the schoolbook charge 2s^2 · 24 when s < 256. For s ≥ 256,

H(s) = 2 H(⌈s/2⌉) + 20 M(s + 1).

The 20 products are four for the first matrix-vector application, four for the exact division, four for the second matrix-vector application, and eight for the 2×2 matrix product. Products whose true length is at most s + 1 are charged as M(s + 1).

The outer gcd charge G(s) starts at s = n. While s ≥ 256 it adds H(s) + 4 M(s + 1) and replaces s by ⌈s/2⌉. The terminal value, which is below 256, adds the schoolbook charge 2s^2 · 24. The added 4 M(s + 1) is one exact division between half-gcd calls. Evaluating this recurrence gives

G(n) = 855731808720

operations per base.

### Inversions, each base

The half-gcd inverts at most m leading coefficients, counting one inversion to clear a denominator at each degree and one to scale the input. An inversion is x^{p−2}. The exponent p − 2 has 255 bits and Hamming weight 77, so the schedule is 254 squarings and 76 multiplications, 330 field multiplications. The charge uses 332 field multiplications and 8 operations per field multiplication,

m · 332 · 8 = 5187502656.

### Comparison

The build is performed once. Each of the two bases pays the Newton inverse, the modular exponentiation, the linear scans, the inversions, and the half-gcd. The sum of these pieces is

W = 5255828097312.

Verification of the returned pair is two permutations, so the numerator is

W + 2C = 5255828097870.

C · 2^34 = 4793183502336 and C · 2^35 = 9586367004672. The numerator is strictly larger than C · 2^34 and strictly smaller than C · 2^35. The itemized logarithm is 34.13293391709011. The submitted time_log2 is 35.

Replacing G(n) by 2 G(n) on both bases adds 1711463617440 and leaves the numerator strictly below C · 2^35. The submitted ceiling is 35 for that reason. It is not the itemized logarithm, and it is not a downward rounding.

## Memory

Peak storage for the schedule above, with on-the-fly twiddles, is one table of N bit-reversal indices at 4 bytes, two length-N transform buffers, and three length-m coefficient arrays (the modulus, the Newton inverse, and one scratch). The unreduced square and the quotient occupy a transform buffer, because N ≥ 2n. Bytes:

N · 4 + 2 · N · 32 + 3 · m · 32 + 2^20 = 473761344,

where 2^20 is the allowance for code and the pinned constants. This is strictly less than 2^29 = 536870912 and strictly greater than 2^28 = 268435456. The submitted memory_log2_bytes is 29.

The normalized cost is 35 + max(0, 29 − 20) = 44. Preprocessing is empty. The advice string is empty. The two bases are fixed constants of the procedure, not advice and not the output of a search.
