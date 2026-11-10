# Deterministic full-round Orchard collision by overfull output intervals

## Claim and scope

For `poseidon-orchard-r56-prefix-v1`, the exact fixed-input, fixed-capacity Orchard P128Pow5T3 hash specified by the profile, the following deterministic classical algorithm outputs two different canonical input pairs having exactly the same complete output field element. Its success probability is 1, its total work is strictly below 2^270 target-compressions under `orchard-field-ram-v2`, and its total memory is at most 2^20 bytes. No random-oracle, independence, distribution, algebraic-attack, or computational heuristic is assumed. The bound is much worse than the nominal birthday exponent: we do **not** claim an improvement to that reference or a practical attack. The metadata `baseline_improved` identifies the required nominal reference only.

This is a finite constructive existence and resource bound. No full-size run has been made and no specific collision is claimed. The method is generic and the pigeonhole principle is classical; there is no claim of novel cryptanalysis. It applies to any deterministic function from the specified input set to the canonical field output, including this fixed full-round function. No published Yukon submission is incorporated.

## Target

Let p be the exact prime `0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`. In particular 1 < p < 2^255. The hash H evaluates the exact profile: input state `[nk,rho,2^65]`, full rounds 0–3, partial rounds 4–59, full rounds 60–63, deployed halo2_poseidon 0.2.0 constants and dense MDS, with output its first field coordinate in canonical representation. We compare the entire element, not a prefix; the 32-byte output has a unique canonical encoding. H is evaluated with the profile's fixed capacity and no free-start modification.

Index p+1 distinct valid inputs by integers i in [0,p] inclusive:

* for i < p, M(i) is `(i,0)`;
* for i = p, M(i) is `(0,1)`.

Both elements of every pair are less than p, and the final pair differs from all earlier pairs because p>1. Integers are encoded as canonical 32-byte little-endian field elements. Let F(i) be the canonical integer in [0,p) represented by H(M(i)).

## Algorithm

All integer intervals below are half-open. `count(a,b)` loops through every i from 0 to p inclusive, computes F(i), and counts values with a <= F(i) < b. It uses one counter, never a table. Execute:

```text
lo = 0; hi = p; n = p+1
while hi-lo > 1:
    mid = lo + floor((hi-lo)/2)
    left = count(lo,mid)
    if left > mid-lo:
        hi = mid; n = left
    else:
        lo = mid; n = n-left
# scan every i again, retaining the first two indices with F(i)=lo
# compute their hashes once more and output both canonical input pairs
```

The `n` counter is not used to decide the branch, but makes the invariant explicit. The implementation checks that two indices were collected and that their independently recomputed canonical full outputs match before returning. This is a specified finite algorithm, not pseudorandom sampling or an expected-time search.

## Correctness

Initially `[lo,hi)` contains p possible canonical outputs and n=p+1 indexed inputs, so n>hi-lo. The two disjoint subintervals partition the original interval. If the left subinterval contains more inputs than output values, retaining it preserves the invariant. Otherwise its count is at most its length, so the right count `n-left` exceeds the right length. Thus the branch always retains an interval with strictly more indexed inputs than distinct possible outputs.

At termination the retained interval has length one, so at least two distinct indices have output equal to `lo`. The final complete scan finds them. The input-index mapping is injective, so their canonical input pairs are distinct. Their complete canonical output field elements, and consequently all 32 output bytes, are equal. This proves deterministic success 1 even for a highly nonuniform or adversarial H. The check cannot fail in exact arithmetic. The method needs neither random coins nor a success amplification argument.

## Finite resource accounting

All counters, indices, interval endpoints and differences lie in [0,p+1] and fit in one unsigned 256-bit word because p+1 < 2^255. `mid` is computed as `lo + ((hi-lo)>>1)` without overflow. The interval length is at most halved with rounding upward on each iteration. Since p<2^255, there are at most 255 interval scans and one final collection scan. Independent final verification needs two further H evaluations. Therefore

```
H_calls <= 256*(p+1)+2 < 2^263 + 2.
```

Implement each scan as a fixed loop with 256-bit counter, comparison, increment, input selection, two output-bound comparisons, conditional increment or storage of two indices, and branches. At most 128 primitive 256-bit word operations per H call conservatively cover loop and branch instructions, word reads/writes, constructing canonical inputs and comparing canonical outputs; this bound is independent of p and includes the final scan. Interval updates, initialization, final encoding, and loop setup require fewer than 10,000 additional word operations total. The full reference permutation is charged as one target-compression per call, with all its field arithmetic and input/output state already included; it is not also counted as separate field operations. Thus, with the specified 56-round conversion C=216+21*56=1392,

```
T <= H_calls + (128*H_calls + 10000)/1392 + 16 < 2^270.
```

The additive 16 compression units are an allowance for one-time setup including loop initialization and copying the pinned public constants. These are also covered in the declared preprocessing upper bound 2^4; double counting them above is conservative. There is no preprocessing table and no nonuniform advice. No RNG, sort, external storage, parallel workers, restarted trials or hidden query oracle is used. All of the loops' work, including unsuccessful intermediate scans, is counted in the total, not just wall-clock or a successful path. The bound is deliberately loose rather than rounded down.

The algorithm holds only a constant number of 256-bit words: p, interval endpoints, midpoint, count, index, two retained indices, temporary outputs, the three-element hash state and implementation scratch. The 64 rounds' three field constants plus the nine MDS constants require at most (192+9)*32 = 6,432 bytes, even if stored all at once. A direct fixed-code implementation can reserve 64 KiB for executable instructions, these constants and stack together, with remaining working data below 64 KiB. The declared 2^20-byte bound leaves a factor-eight margin over this 128 KiB reservation and includes code, constants, scratch, and the two returned messages; it is not only a bound on mutable data. Under the score policy, memory at exactly 2^20 bytes incurs no extra cost, so the declared normalized upper cost is 270. This is an upper bound, not a claim that the search has actually been executed.

## Evidence and limitations

The proof is pointwise and uses no asymptotic distribution assumption. Its mathematical argument applies to a finite total function, so small toy executions are not used to extrapolate an unproved success heuristic. The organizer's deterministic setup and candidate-structure checks test the package, not a full-size execution or independent implementation of this resource proof. The bound is astronomically large and is not a practical collision-finding method. Remote qualification and human acceptance are separate from this mathematical argument; neither has been assumed here.
