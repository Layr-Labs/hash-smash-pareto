# r = 1 Orchard collision by a degree-1953120 slice

Ordinary collision for `poseidon-orchard-r1-prefix-v1`. The modulus is the Pallas prime

p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001.

A message is two canonical little-endian field elements, each strictly less than p. The initial state is (nk, rho, 2^65). The rounds are the deployed rounds 0, 1, 2, 3, 4, 60, 61, 62, 63 of halo2_poseidon 0.2.0: add the deployed round constants, raise every coordinate to the fifth power in a full round and only coordinate 0 in a partial round, then apply the deployed 3×3 MDS. Indices below 4 and at least 60 are full rounds. The digest is the entire final coordinate 0. Equality is equality of that field element.

Write H(a, b) for that coordinate on input (a, b, 2^65). The procedure below returns the messages (r, 0) and (r, 1).

## Degree

Let σ(β) = (β + c)^5 - c^5, where c is the second round constant of round 0,

c = 0x2bab94d7ae222d135dc3c6c5febfaa314908ac2f12ebe06fbdb74213bf63188b.

The map x ↦ x^5 is a permutation of the field, because gcd(5, p - 1) = 1, so σ(β) = 0 if and only if β = 0.

For β ≠ 0 the difference g_β(a) = H(a, β) - H(a, 0) is a polynomial of degree exactly n = 5^9 - 5 = 1953120. The absolute coordinate H(a, β) has degree exactly 5^9 = 1953125. Both statements are the following finite leading-coefficient calculation.

Track two vectors in the field. L is the degree-D leading coefficient of each absolute coordinate, starting after round 0 at degree 5 with L equal to the first column of the MDS. The leading term of (a + c_0)^5 is a^5, and round 0 does not depend on a in the other two S-box inputs. Ld is the coefficient of σ in the degree-(D - 5) term of each coordinate of the difference, starting after round 0 as the second column of the MDS. The initial difference of the states is exactly the constant vector σ times that column, because the first and third S-box inputs do not depend on β and the second inputs differ by σ before the MDS.

A full round replaces L by M · (L_0^5, L_1^5, L_2^5) and Ld by M · (5 L_0^4 Ld_0, 5 L_1^4 Ld_1, 5 L_2^4 Ld_2), and replaces D by 5D. A partial round does the same using only coordinate 0 and the first column: the new absolute leading vector is (L_0^5) times that column, at degree 5D, and the new difference leading vector is (5 L_0^4 Ld_0) times that column, at degree 5D - 5. Coordinates 1 and 2 of a partial round stay at the old degree, which is strictly smaller, so they do not affect the new leading term.

The identity used for the fifth-power difference is exact. If a coordinate has degree d, leading coefficient λ, and the two paths differ by a polynomial of degree d - 5 with leading coefficient μ, then

(u + Δ)^5 - u^5 = 5 u^4 Δ + 10 u^3 Δ^2 + 10 u^2 Δ^3 + 5 u Δ^4 + Δ^5.

The first summand has degree 4d + (d - 5) = 5d - 5. The second has degree 3d + 2(d - 5) = 5d - 10. Every later summand is smaller. The leading coefficient is exactly 5 λ^4 μ. Since 5 ≠ 0 and the tracked λ, μ stay nonzero, the degree rises by the stated amount.

Running the recurrence on the deployed MDS through rounds 1, 2, 3, 4, 60, 61, 62, 63, after the round-0 initialization above, leaves every coordinate of L and of Ld nonzero. The final coefficient of σ in coordinate 0 of the difference, at degree 1953120, is

C_lead = 10431619794572519868904532390899450171137171840602430212551006592048446307512.

Thus for every β ≠ 0 the leading term is C_lead · σ(β) · a^1953120 with both factors nonzero. In particular this holds for β = 1.

The same recurrence reproduces fully expanded differences on shorter index lists. For rounds (0, 60) and β = 1 the expanded difference has degree 20 and leading coefficient 15603644654870160706620950292949448045795424022457571466664041130195912060724, equal to C · σ(1) for the coefficient C predicted on that list. For rounds (0, 4, 60) and β = 1 the expanded difference has degree 120 and leading coefficient 21219246024623122122148605958015170566023079529816009743412447405870563498821, again equal to the prediction. The polynomial constructed for the r = 1 index list and β = 1 had degree 1953120, equal to 5^9 - 5.

The eight full rounds do not drop this degree. After each full round the new leading vector is M times a nonzero vector, and M is invertible, so the vector stays nonzero. One partial round does not remove those rounds: it multiplies the degree by 5 on the coordinate that already carries the top term.

## Algorithm

There are no random coins and no advice string. Set β = 1.

Build H(a, 0) by composition. The state starts as the polynomials (a, 0, 2^65). Each selected round adds constants, replaces each S-boxed coordinate P by P^5, and replaces the state by its MDS image. A fifth power is two squarings and one product. Build H(a, 1) the same way and set g = H(a, 1) - H(a, 0). Make g monic. Its degree is n = 1953120.

Compute X^p modulo g by square-and-multiply, subtract X, and take the monic gcd with g by the schoolbook Euclidean algorithm. Square-and-multiply follows the bits of p from bit 253 down to bit 0, starting from X: 254 squarings and 46 multiplications by X, since p has 255 bits and Hamming weight 47. Each modular product uses a length-N number-theoretic transform, N = 2^22 = 4194304, and the Newton inverse of the reverse of g, computed once. Multiplication by X is a shift followed by one scalar subtraction of the modulus when the degree reaches n.

If the gcd has degree 1 and equals X - r, return the messages (r, 0) and (r, 1), each element written as 32 canonical little-endian bytes. Any other gcd degree fails. The procedure does not try another β.

X^p - X is separable because its derivative is -1, so the gcd degree equals the number of distinct roots. A degree-1 gcd is exactly one root. The root lies in the field because it is a root of X^p - X. It is a root of g because the gcd divides g, so H(r, 1) = H(r, 0). The messages differ because the second elements are 0 and 1. Both are canonical because a field element produced as a root of X^p - X is an integer in {0, ..., p - 1}.

## Execution

The procedure was executed on this index list with β = 1. The constructed difference had degree 1953120. The monic gcd of that difference with X^p - X had degree 1. The root was

r = 21295018245332138659184472221807390184989200179957268241054586399316369967481.

The two messages are the files `certificates/message-a.bin` and `certificates/message-b.bin`. Their common digest is

b4fd8d123c3495d91a90a26c29f9034076c2548fd1dd3765c7a5a3b8eccebd30.

The organizer checker recomputes both digests from those files and compares them with that value. That check does not use the polynomial. It is an independent confirmation that these two messages collide under the r = 1 round function.

The procedure has no coins. Every execution builds the same polynomials, runs the same 254 squarings, and obtains the same gcd. The executed gcd had degree 1, so the procedure returns this pair and does not fail. The success probability is 1. No trial is hidden, and β was fixed before the execution rather than chosen from a search.

## Cost

One r = 1 permutation costs C = 216 + 21·1 = 237 primitive units. A field addition, subtraction, or multiplication, and a primitive word operation, each cost one unit before division by C. A field multiplication is not expanded into limb products. Inversions are expanded. The matrix exponent 2.8 is not used. The bound below counts the loops of the procedure above. There is one execution. Failed trials are not present.

Let n = 1953120 and m = n + 1 = 1953121. The transform length is N = 2^22 = 4194304, the least power of two that is at least 2n - 1 = 3906239. A primitive 2^32-th root of unity exists because the multiplicative group has 2-adicity 32, so a primitive N-th root exists.

Verification of the returned pair is two permutations, so H = 2. Every other operation is in W below. The normalized time is T = H + W/C.

### Transforms

An in-place transform of length N does a bit reversal and (N/2)·22 butterflies.

Bit reversal of one index is charged 40 word operations. That covers a 22-step loop that extracts each bit, deposits it, advances the index, compares, and branches, with spare operations in the charge. The bit-reversal total is 40N.

One butterfly is charged 20 operations: load both values, load the twiddle, one field multiply, one field add, one field subtract, two stores, and index arithmetic, a compare, and a branch. Twiddles may be multiplied on the fly; the 20 operations include that multiply. No twiddle table is required by the bound.

One transform therefore costs

40N + 20·(N/2)·22 = 1090519040

operations.

A polynomial square is two transforms and one pointwise loop. A polynomial product is three transforms and one pointwise loop. Reducing a product modulo the monic degree-n polynomial is two further products: one against the precomputed series inverse of the reverse, truncated to degree below n, and one against the modulus. Truncation is not credited; each of those products is charged as a full product at length N. A modular square is therefore 2 + 2·3 = 8 transforms. Multiplication by X is not a transform.

The exponent uses 254 modular squares. The series inverse is built by 22 Newton iterations, from precision 1 through 2^21 = 2097152, which is the least power of two that is at least n. Two full products per iteration give 132 transforms. Iterations whose current precision is shorter than N are still charged at length N.

Each hash applies 25 fifth powers: eight full rounds on three coordinates and one partial round on one coordinate. Two hashes are 50 fifth powers. A fifth power is two squares and one product, 7 transforms, and every one of them is charged at length N even when the current degree is smaller. The build costs 350 transforms.

The transform total is 350 + 254·8 + 132 = 2514 transforms, and

2514 · 1090519040 = 2741564866560.

Pointwise square, fused with multiplication by N^{-1}, is charged 12 operations at each of N points. Pointwise product is charged 16 operations at each point. There are 354 pointwise squares: 50 fifth powers contribute two each, and 254 modular squares contribute one each. There are 602 pointwise products: 50 from the fifth powers, 508 from the two reduction products in each modular square, and 44 from the Newton iteration. The pointwise total is

354·12·N + 602·16·N = 58216939520.

### Linear scans, the MDS, and multiplication by X

Each scalar multiplication of an m-coefficient polynomial by a constant is charged 8 operations per coefficient, at the final length.

Nine rounds, two paths, and nine scalar multiplications per round give 162m scalar multiplications, 1296m operations. Constant additions are 9·3·2 = 54 polynomials, charged 500m operations, above 54·8m = 432m. Reversals inside the 254 modular squares are two length-m reversals per square at 8 operations per coefficient, 4064m. Newton reversals are charged 400m, above 22·2·8m = 352m. The difference that forms g is charged 16m, monic scaling 16m, and quotient-digit setup 64m. The sum of these charges is 6356m. The budget below uses 8000m = 15624968000, which is larger.

Each of the 46 multiplications by X shifts m coefficients and, in the worst case, subtracts a scalar multiple of the modulus. The charge is 24 operations per coefficient, 46·24·m = 2156245584.

### Euclidean algorithm and inversions

The monic gcd input has degree n, and X^p - X modulo it has degree at most n - 1. Each division drops the divisor degree by at least 1, so there are at most n divisions. Dividing degree d' by degree d < d' performs (d' - d + 1)(d + 1) coefficient updates, which equals (d' - d)(d + 1) + (d + 1). The gaps d' - d sum to at most n. Each d + 1 is at most n. The two sums are therefore at most n^2 each, and the single execution performs at most 2n^2 coefficient updates.

Each update is charged 24 operations: load the remainder coefficient, load the divisor coefficient, load the quotient digit, one field multiply, one field subtract, one store, address and index arithmetic, compares, branches, and bookkeeping moves. The Euclidean total is

2n^2 · 24 = 183104531251200.

The execution also inverts at most n leading coefficients during the divisions, plus one inversion to make g monic, m inversions in total. An inversion of a nonzero field element is x^(p - 2). The exponent p - 2 has 255 bits and Hamming weight 77, so the schedule is 254 squarings and 76 multiplications, 330 field multiplications. The charge uses 332 field multiplications and 8 operations per field multiplication:

m · 332 · 8 = 5187489376.

### Comparison

The sum of these pieces is

W = 185927281760240.

With H = 2 and C = 237,

W + H·C = 185927281760714,

C · 2^39 = 130292127891456,

C · 2^40 = 260584255782912,

C · 2^41 = 521168511565824.

The work numerator is strictly larger than C · 2^39 and strictly smaller than C · 2^40, so the itemized T lies strictly between 2^39 and 2^40. The submitted time_log2 is 41. Replacing the single-execution update bound 2n^2 by 4n^2, with the same 24 operations per update, produces a numerator still strictly below C · 2^41. The submitted bound is 41 in either case.

## Memory

Peak storage, with two length-N transform buffers and no twiddle table, is three arrays of m field elements (the modulus, the series inverse, and the accumulator), one unreduced product of length 2n, one quotient of length n, and one product against the modulus of length 2n. Elements:

3m + 5n + 2N = 24013571.

At 32 bytes each, plus a 2^20-byte allowance for code and the pinned constants,

24013571 · 32 + 2^20 = 769482848.

This is strictly less than 2^30 = 1073741824 and strictly greater than 2^29 = 536870912. The submitted memory_log2_bytes is 30.

The normalized cost is 41 + max(0, 30 - 20) = 51. Preprocessing is empty. The advice string is empty. The second input β = 1 is a fixed constant of the procedure, not advice and not the output of a search.
