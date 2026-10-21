# SHA3-256 r24: S3-04 constants and look-ahead polarities in an eight-body bit-sliced step

## 1. Claim

This is a generic van Oorschot-Wiener distinguished-point collision search for the complete `sha3-256-r24-prefix-v1` target. It combines the eight-shared-body r24 step of c9a7e62c with the S3-04 structured constants, one-round look-ahead polarity method and 39-bit packed instruction format documented by 760073e9. The construction does not use a weakness of full SHA3. Its cost comes from implementing a generic birthday search in the benchmark's explicit word-RAM model.

| quantity | bound |
|---|---:|
| rounds | 24, prefix rounds 0 through 23 |
| operations in one 256-walk step | 147,252 |
| charged total word operations N | 196,726,229,563,718,670,526,410,399,795,092,668,422,689 |
| reference unit | 6,504 word operations |
| time_log2, rounded upward | 124.50813 |
| search memory | 1,044,273 bytes |
| generation memory | 1,022,609 bytes |
| memory_log2_bytes bound | 20 |
| normalized score | 124.50813 |
| success | at least 0.39 under H_rand |

The current public r24 frontier c9a7e62c reports 124.50895. The improvement is 0.00082 bit. It is small, so every count below is kept as an integer and the incumbent arithmetic is reproduced before the new row is evaluated.

## 2. Target and chain function

Let `u = (u0,u1,u2,u3)` be four little-endian 64-bit limbs. The 128-byte message `m(u)` has these variable lanes:

- lane 1 = u0, lane 6 = u1, lane 11 = u0 xor u1 xor K11;
- lane 4 = u2, lane 9 = u3, lane 14 = u2 xor u3 xor K14.

The other message lanes are fixed:

```
K0  0000000000000000   K2  2d58eceb83b21614   K3  0000000000000000
K5  ffffffffffffffff   K7  0000000000000000   K8  0000000000000000
K10 ffffffffffffffff   K11 8b563b3ae0ec8583   K12 0000000000000000
K13 85ab1d9d707642c2   K14 e953898a3e26f4f5   K15 ffffffffffffffff
```

SHA3 padding supplies lane 16 = `8000000000000006` and lanes 17 through 24 are zero. The target applies Keccak-f rounds 0 through 23 and returns lanes 0 through 3. Define `F(u) = SHA3-256-r24(m(u)) xor PD`, with:

```
PD fdcf1847d8033268 7f74f7c895f5028f 2110874191d40408 8100203102004191
```

The embedding is injective because lanes 1, 6, 4 and 9 expose all four limbs. Thus `F(a)=F(b)` with `a!=b` gives two distinct complete messages with the same 256-bit digest. The fixed PD XOR is a bijection and only makes the physical digest planes usable as the next point without extra NOT instructions.

### Why S3-04 shortens the prefix

Columns 1 and 4 have constant parities because each contains `u0,u1,u0 xor u1 xor K11` or the corresponding u2/u3 triple. Theta of round 0 therefore adds only constants. After rho and pi, no two variable lanes are adjacent in a chi row, so round-0 chi remains affine.

S3-04 also sets the right neighbor of each of the six variable lanes to zero and the useful left neighbors to all ones after theta, rho and pi. The 704 consistent neighbor conditions are affine in the constant bits. The fixed constants above satisfy those conditions. Round-0 chi consequently leaves only the six intended lanes variable. The independent generator tracks GF(2) affine forms through round 0 and theta of round 1 and emits each new form once.

## 3. Generated step

One machine word contains one bit plane for 256 independent walks. Rho and pi rename planes and cost nothing. XOR, AND, OR and NOT each cost one word operation. A logical AND uses one physical instruction when the operand polarities agree and two when they do not. Chi rows use the credited 10-gate dependency when it is cheaper.

The generator creates:

- P: structured affine rounds 0 and 1, with an exact three-sweep greedy pass over the 640 round-1 C/D complement choices;
- B1 through B8: one generic round each, alternating fixed 1,600-plane register banks;
- E: row 0 of round 23, restricted to the four digest lanes.

Rounds 2 through 22 call body `(r-2) mod 8 + 1`. B1 through B5 run three times and B6 through B8 run twice. Each body omits iota. The driver performs the 78 set round-constant bits as XORs with the all-ones register. Calls and returns cost 42 operations. B8 is forced to reproduce P's bank polarity, closing the cycle without a bridge.

For every generic body, the generator constructs the exact 32 by 32 row table indexed by input and requested output polarities. It searches C/D complements and explicit row output polarities. The objective is the documented 16-to-3 current-round/next-round cost, with an exact closure objective for B7/B8. All runs are deterministic. The ledger charges all three candidate chains, including the two that lose.

### Block ledger

| block | executions | XOR | AND | OR | NOT | total |
|---|---:|---:|---:|---:|---:|---:|
| P | 1 | 2,518 | 960 | 640 | 174 | 4,292 |
| B1 | 3 | 4,822 | 939 | 661 | 257 | 6,679 |
| B2 | 3 | 4,820 | 944 | 656 | 213 | 6,633 |
| B3 | 3 | 4,818 | 945 | 655 | 227 | 6,645 |
| B4 | 3 | 4,832 | 940 | 660 | 220 | 6,652 |
| B5 | 3 | 4,822 | 941 | 659 | 221 | 6,643 |
| B6 | 2 | 4,818 | 945 | 655 | 246 | 6,664 |
| B7 | 2 | 4,840 | 924 | 676 | 282 | 6,722 |
| B8 | 2 | 4,852 | 818 | 782 | 458 | 6,910 |
| E | 1 | 2,211 | 167 | 89 | 25 | 2,492 |

The blocks contain 60,332 stored instructions. Their weighted execution plus 78 iota XORs and 42 calls/returns is exactly 147,252 operations. P is 650 operations cheaper than c9a7e62c's P. The generic bodies are somewhat dearer, leaving a net 51-operation step reduction.

### Registers and encoding

The lazy theta builder defines each C and D value at its first chi-row use. The highest block register is 3,464. Eleven search and link registers make a declared file of 3,476 256-bit words, or 111,232 bytes.

Each straight-line instruction is 39 packed bits: a 3-bit opcode and three 12-bit register fields. Every independently callable block is byte aligned. P, G, B1 through B8, E, the 78 iota instructions and 15 prefilter instructions occupy 294,577 bytes including byte rounding. The 29 calls and returns occupy 928 bytes in the credited 32-byte control format, for 295,505 step-code bytes total.

Packed output hashes:

- B1.p39: `d8f072bc4a7205893f1e39ab7782a668a583a5f01f0c7a13662b67e4605ce8af` (32561 bytes)
- B2.p39: `b920b2758ccd1b379c585cd076708c65ca427d73889e0bf6324a40b1a4cfd14c` (32336 bytes)
- B3.p39: `cc573cdccfb0e8896359677878df745f253cc1fb1ce62f0af56a8254b36794c5` (32395 bytes)
- B4.p39: `77a490805b25f40a361a322dbef9b95337054649f218563cb577ad5eb3795486` (32429 bytes)
- B5.p39: `f98823025570035b5523e744653ab7daf7380c6731da9e643b039127ba417da3` (32385 bytes)
- B6.p39: `01b5bd129f9a7b9579a7d70db28a7f980b44c6505b46584d0ca8bef66d02e421` (32487 bytes)
- B7.p39: `d5c18e44cf473cdb1ace7d40df2caa40b230386b44e4fab61edb1767ca3135ba` (32770 bytes)
- B8.p39: `0ed1e08cc361ad502ef54894db39573efb0ddcf5d9769939da475976088d6c9b` (33687 bytes)
- E.p39: `e62607aa4e0bc72fa1f7f2ef862db9b04bb36c522cb0e9e8ff9881a2cfea671f` (12149 bytes)
- G.p39: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (0 bytes)
- P.p39: `a5566d20f7aeaf6ba9dd955cf965118512557672f5b83a72bd75c5aed2ef74f1` (20924 bytes)
- PD.bin: `b7c84bcab67b6b05c6b700923db8a2101f9781ed7dc895e0713020bde7284811` (32 bytes)

## 4. Independent execution checks

The generator is our C implementation. It does not compile, import or execute participant source. A separate C checker decodes every five-byte development instruction and every packed 39-bit instruction, requires the streams to agree, executes the exact P/body/iota/E schedule, and compares each physical output with a separate scalar Keccak-f implementation. The organizer experiment provides a second implementation: it expands the embedded final plans into graph nodes, register-allocates and packs every block, requires the hashes and XOR/AND/OR/NOT counts above, checks 60,332 stored and 147,252 executed instructions, and executes the schedule on eight fixed full-width points against its scalar reference.

Fresh final run:

```
reference: SHA3-256 empty and abc KATs passed; complete padding exercised at lengths 0..511
step: 147252 charged operations including 42 calls/returns and 78 iota XORs
cross-check: 65536 chained F evaluations, 0 mismatches
```

The scalar complete-message implementation wrote digests for lengths 0 through 511. A separate Python comparison found 512 of 512 equal to `hashlib.sha3_256`, covering the padding boundary at 136 bytes and several multi-block messages.

## 5. Search

This section defines the whole algorithm. The state machine and the proof in Section 7 are adapted from c9a7e62c Sections 4 and 5 and 71fefe66 Sections 4 and 5. They are reproduced here with this package's parameters so those entries are provenance, not missing premises.

### 5.1 Input coin and fixed parameters

One attempt takes one input coin `rho`, sampled uniformly from the integers `0 <= rho < 2^256`. The target function F, all constants, the program, and every rule below are fixed. No instruction samples another value. Trail `i` always starts at

```
start(i) = (rho + i) mod 2^256.
```

The first 256 trails have identifiers 0 through 255 and occupy walk lanes with the same numbers. Each later per-walk restart consumes the next identifier. This rule maps `rho` to all 66,720 possible starts, including starts not reached in a particular execution.

A point `x` is distinguished when `x < 959 * 2^134`. In the bit-sliced state, planes 144 through 255 must be zero and the integer in planes 134 through 143 must be less than 959. The distinguished-point probability for a uniform point is exactly `theta = 959 * 2^-122`.

Parameters:

| item | value |
|---|---:|
| table words S | 16,680 |
| four-record trail capacity U | 66,720 |
| table home bits | 15 |
| stored key bits | 46 |
| stored trail-identifier bits | 17 |
| replay cap LRC | 58,214,318,514,280,978,804,933,101,300,482,048 |
| lockstep steps Tb | 1,327,992,259,278,900,420,605,797,256,497,463,296 |
| evaluations | 0.9990703351795673370361328125 times 2^128 |
| prefilter-hit cap HMAX | 63,401,793,224,245,863,497,131,009,276,641,281 |

The hit cap is `floor(Tb * (1 + 2^-20) / 256) + 1 + LRC`. The replay cap is `45923 * 2^100`, or `10.4999916553497314453125 / theta`.

### 5.2 Retained state and table layout

The persistent state is:

- registers 0 through 255, whose bit `l` across the planes is the current point of walk `l`;
- the counters `c`, `idn`, and `h`, holding completed lockstep steps, the next trail identifier, and prefilter hits;
- `LID[l]` and `LST[l]`, holding the trail identifier in walk `l` and the value of `c` when that start was placed in the walk;
- `TAB[0..16679]`, where each 256-bit word has four 64-bit record slots in low-to-high order;
- the fixed message constants, PD, and eight output words.

A zero 64-bit slot is empty. For a distinguished end `x` of trail `i`, the nonzero record is

```
record(x, i) = 1 | ((x mod 2^46) << 1) | (i << 47).
```

Bit 0 is the valid bit, bits 1 through 46 are the low 46 end bits, and bits 47 through 63 are the 17-bit trail identifier. The trail length is not stored. Replay measures it from `start(i)`.

The packed-field boundary is explicit. Identifiers 65,535 and 65,536 round-trip on opposite sides of the old 16-bit boundary, and the maximum used identifier 66,719 fits below `2^17`. Identifier 66,720 is never installed because `restart` checks `idn = U` first. The organizer experiment packs these three accepted identifiers with the maximum 46-bit key into each of the four 64-bit slots, verifies that slot 3 ends at bit 255, and rejects 66,720. It also checks every emitted instruction: opcodes are 0 through 3 in a 3-bit field, and every register is at most 3,464 in a 12-bit field. The counters and `LID`/`LST` entries occupy full 256-bit words rather than narrower packed fields. These are all packed fields in the construction.

The home table word is computed without division. Set `slot = x mod 2^15`; if `slot >= 16680`, subtract 16680 once. Probe that word's four slots in order. If all four are occupied and none has the same valid bit and 46-bit key, increment `slot`, wrapping 16679 to zero, and continue. The first empty slot receives the record. A matching key starts replay. No record is deleted. At most `U - 255` records can be reached before the trail limit halts the attempt, which is less than the table's `4S = U` slots, so an empty slot or match exists.

### 5.3 Initialization and lockstep loop

Initialization performs these transitions in order:

1. Set `c = 0`, `idn = 256`, and `h = 0`.
2. Clear all 16,680 table words.
3. For each lane `l` from 0 through 255, set `LID[l] = l`, `LST[l] = 0`, and the lane point to `start(l)`.

One loop iteration starts with the current 256 points and has this fixed order:

1. Execute the 147,252-operation bit-sliced program of Section 3. Every lane now contains F of its previous point.
2. OR output planes 240 through 255 with 15 OR operations. If every lane has at least one set bit in those planes, skip the hit handler because no lane can be distinguished.
3. Otherwise increment `h`. If `h > HMAX`, halt with failure code 10. Form the exact distinguished-lane mask from planes 144 through 255 and the comparison of planes 134 through 143 with 959.
4. Set `s = c + 1`. Process each distinguished lane in increasing lane order. The handler clears the lowest set bit of the mask after it selects a lane, so this order is fixed.
5. After all selected lanes finish, set `c = s`. If `c = Tb`, halt with failure code 12. Otherwise start the next iteration.

The main loop never cuts a long trail. Every active walk receives exactly one F evaluation per loop iteration.

### 5.4 Distinguished-point handler and per-walk restart

For selected lane `l`, gather its 256 output-plane bits into the integer `x`. Build `record(x, LID[l])` and probe the table by Section 5.2.

If the probe reaches an empty slot, store the record and call `restart(l, s)`. The restart transition is:

1. If `idn = U`, halt with failure code 11. The just-written record remains in the table.
2. Set `LID[l] = idn` and `LST[l] = s`.
3. Replace the point in lane `l` with `start(idn)`.
4. Increment `idn` and return to the distinguished-lane loop.

Thus a trail restarted after the image at step `s` first receives an F evaluation at step `s + 1`. If it later ends at step `t`, its length is `t - LST[l]`.

If a probed record has the same valid bit and 46-bit key, extract its stored trail identifier `a`. Let the current trail be `b = LID[l]` and its known length be `lb = s - LST[l]`. Start the replay below. The full-size attempt never resumes the main loop after a key match, whether replay succeeds or refuses the pair.

### 5.5 Replay, merge recovery, and halts

Replay uses the scalar F evaluator, which embeds one point, executes the target permutation, extracts the digest, and XORs PD. Its transitions are:

1. If `lb > LRC`, halt with failure code 13.
2. Starting at `start(a)`, evaluate F until the first distinguished image. Let the number of evaluations be `la`. If no distinguished image occurs within LRC evaluations, halt with failure code 13.
3. Set `p = start(a)` and `q = start(b)`. If `la > lb`, advance `p` by `la - lb` evaluations. If `lb > la`, advance `q` by `lb - la` evaluations.
4. If `p = q`, halt with failure code 13. This is a start-on-trail alias, not two distinct predecessors.
5. Repeat at most `min(la, lb)` times: evaluate F on `p` and `q`; if `F(p) = F(q)`, recover `m(p)` and `m(q)`, write their eight 256-bit output words, and halt with success code 1; otherwise replace `p` and `q` with their images. If all iterations finish without equality, the common table key was a 46-bit alias, so halt with failure code 13.

On success, `p != q` and `F(p) = F(q)`. Because the embedding is injective and PD is a fixed XOR, `m(p)` and `m(q)` are distinct complete messages with equal 256-bit target digests. At most one replay runs in an attempt.

Failure codes 10 through 13 are terminal for the claimed one-attempt algorithm. The claim does not derive a replacement `rho` after failure. A caller may repeat the whole attempt only by sampling a new independent uniform 256-bit `rho` and paying the full cost again.

These rules cover every state change. Given `rho`, lane order, record placement, restarts, the replay path, the halt code, and any recovered messages are deterministic.

Each main-loop iteration costs the step 147,252, fifteen prefilter ORs, a compare and branch, and three counter operations: BSTEP = 147,272.

## 6. Exact work ledger

The independent ledger first reproduces c9a7e62c:

```
N = 196837072726569150731717239455155002654091
time_log2 = 124.50895
```

For this row:

```
main           195576076008522222743456973558894414528512
replay           1142164929250192804152787447515457781839
rare                7988625946254978800638507207819401682
preprocessing             281474976710656
N              196726229563718670526410399795092668422689
```

The rare term is:

```
(HMAX+1)*126
+ (U-255)*(1115 + 35*S)
+ (U-256)*(1289+3)
+ 3 + 1 + setup
```

Setup is `330248 + 11*S/8 = 353183` operations and includes table clearing and all 256 starts. Replay is `(6541+13079)*LRC+79`. The preprocessing charge is a deliberately loose exact budget of 2^48 word operations. It covers 1,922 prefix builds at 2^32 each, row-table construction, 622,845 free-output evaluations, 1,069,488 look-ahead objective evaluations, all graph builds, packed emission and the parameter scan. This budget is much larger than the counted loop work and observed 23.7-second single-core run; increasing it by orders of magnitude would not change the five-decimal time claim.

The exact Decimal/logarithm computation, followed by upward rounding, gives:

```
6504^100000 * 2^12450812 < N^100000 <= 6504^100000 * 2^12450813
time_log2 = 124.50813
```

## 7. Success bound

### 7.1 Probability space and H_rand

Let `A_F(rho)` be the deterministic program in Section 5 on the fixed chain function F. Its success event is halt code 1 with two distinct messages whose complete 256-bit target digests are equal. The claimed probability is

```
Pr[rho uniform in {0,...,2^256-1} : A_F(rho) succeeds].
```

There is no second algorithmic coin. In particular, restarts use the already fixed values `rho + idn`; they do not sample new starts.

H_rand is the one score-critical premise. It states that this probability for the fixed F is at least the probability computed below when F is replaced by a uniformly random function R from 256 bits to 256 bits and rho is uniform and independent of R. Given R and rho, the same state machine remains deterministic. This is a one-sided heuristic transfer, not a theorem about SHA3-256.

In the random-function model, realize R by lazy sampling. At a fresh input, its image is independent and uniform. An already sampled input returns its stored image. Put `n = 2^256`, `q = 1 - theta`, and `E = 256 Tb`. Three facts drive the calculation:

1. The chance that the first `e` fresh evaluations contain a repeated image is at least `G(e) = 1 - exp(-e(e-1)/(2n))`.
2. Just after a coincidence, the number `l` of further images through the first distinguished point has `Pr[l >= j] = q^j`.
3. Conditional on every adaptive choice and the prior history, a fresh image equals any one earlier image with probability `1/n`.

The first image coincidence is a stopping time in the exact execution order: loop step first, then lane number. Suppose the later image occurs in trail B and first equals an image in trail A. From that point both trails have the same suffix and reach the same distinguished end. B is recorded no later than `l` further steps. A is recorded earlier, or in the same lockstep step at a lower lane number. The later table probe therefore finds the earlier record unless one of the failure events below occurs.

The useful event requires all of the following: the first coincidence and its following distinguished end occur by Tb; both trails have at most LRC evaluations; fewer than U trails start; the two images belong to different trails; and neither a start-on-trail alias nor a 46-bit false key prevents recovery.

### 7.2 Birthday term

Partition the possible post-coincidence wait into `J = 45923` bins of `w = 2^100` lockstep steps. Thus `Jw = LRC`. For bin `j` from 1 through J, set

```
p_j = q^((j-1)w) - q^(jw).
```

If the wait lies in that bin, a coincidence among the first `256 * (Tb - jw)` evaluations leaves enough time to reach and record the common distinguished end. The lower birthday contribution is

```
sum_(j=1..J) p_j * G(256 * (Tb - jw))
= 0.3903654261164074385263303198438810306...
```

This sum uses the adaptive lazy-sampling order. It does not assume that completed trails form a fixed random set.

### 7.3 Failure terms

The bound subtracts every way in which that birthday contribution may fail to produce halt code 1.

- **F6, a replay trail exceeds LRC.** For an evaluation at age `a` in its trail, all `a-1` earlier images of that trail were non-distinguished, so `Pr[age >= a] <= q^(a-1)`. After a coinciding pair, let `l` be the common remaining suffix length. Replay fails when `l >= LRC + 1 - max(age_a, age_b)`. Summation by parts bounds the expected tail weight of either evaluation by `q^LRC * (1 + LRC*theta)`. A union bound over ordered evaluation pairs gives

  `F6 = E(E-1) q^LRC (1 + LRC*theta) / n = 0.0003160830570789113180968308704...`.

- **F2, the trail limit halts.** Attach an independent Bernoulli(theta) distinguished indicator to every fresh lazy-sampled image. Repeated inputs lead to a table match and do not add a restart. The number of completed restarts is therefore no larger than a binomial variable with mean `mu = E*theta = 61318.9408919811248779296875`. With `a = U - 256 = 66464`, the Chernoff bound

  `exp(-mu) * (e*mu/a)^a`

  is `5.9402438232013291e-92`. This is a conservative threshold because the actual halt needs the next restart call.

- **F3, the first coincidence is inside one trail.** A geometric(theta) trail has fewer than `1/theta^2` unordered evaluation pairs in expectation under the loose second-moment bound. There are at most U trails, and each evaluation pair has image-coincidence probability `1/n`. The union bound is

  `F3 = U / (theta^2 n) = 0.00001771164403744341788076517836...`.

- **F4, starts or stored keys alias.** There are at most U starts and fewer than E relevant images, so a direct union bound for a start landing on another trail is below `U*E/n < 2^-111`; the calculation reserves the looser `2^-90`. Two distinct distinguished ends agree on the 46 stored key bits with probability `2^-46`; fewer than `U^2/2` pairs give `U^2 * 2^-47`. Thus

  `F4 = 2^-90 + U^2 * 2^-47 = 0.00003163022483931854367256245330...`.

- **F5, the prefilter-hit counter aborts.** For fresh inputs, one lockstep step has probability at most `1 - (1 - 2^-16)^256 < 2^-8` of containing a lane whose top 16 image bits are zero. Outside F4, repeated inputs occur only after the first coincidence. Outside F6, at most LRC more hit steps occur before the attempt stops. With `delta = 2^-20` and the HMAX of Section 5, a supermartingale Chernoff bound gives

  `F5 <= exp(-delta^2 * (Tb/256) / (2 + delta)) < 2^-1000`.

The calculation also subtracts `2^-60` for numerical rounding. The table has an empty slot whenever insertion is required, as proved in Section 5.2, so table probing adds no failure term.

### 7.4 Result

Subtracting F2 through F6 and the rounding allowance from the birthday term gives the following values. The exact parameter scan selects the least multiple of `2^92` whose bound reaches 0.39.

At Tb:

```
success bound               0.3900000011904517643793184234...
bound at Tb - 2^92          0.3899999989334667529373799352...
F6, long colliding trail    3.161e-4
F2, trail-cap overflow      5.940e-92
F3, self-coincidence        1.771e-5
F4, starts/key aliases      3.163e-5
F5, hit cap                 < 2^-1000
rounding allowance          2^-60
```

The probability `0.3900000011904517643793184234...` is over uniform rho for the fixed target only after applying H_rand. Without H_rand, Sections 5 through 7 establish a complete deterministic algorithm and a random-function calculation, but not a full-scale probability theorem for this fixed SHA3 mapping.

## 8. Memory

Search peak:

| region | bytes |
|---|---:|
| 3,476-register file | 111,232 |
| packed step code and driver | 295,505 |
| 2,715 control instructions | 86,880 |
| table, 16,680 words | 533,760 |
| LID/LST walk state | 16,384 |
| constants, PD and output | 512 |
| total | 1,044,273 |

The production generator is statically linked without libc. `size` reports text 26,890, data 12 and BSS 589,448, a 616,350-byte image. It has a fixed 160-KiB heap inside BSS. The emission allocator frees the prefix snapshots before allocating the program and uses 16-bit tables for node indices and registers, whose declared maxima are 12,000 and 4,096.

`stack_audit.py` compiles those exact sources and flags with `-fstack-usage`, extracts direct calls from the linked binary with `objdump`, and sums every compiler-reported frame along the longest call chain. Its conservative maximum includes the deepest failure-reporting path:

```
_start -> main -> build_prefix_graph -> build_dynamic_row -> xor_value.isra
       -> add_form -> fail -> fprintf -> write_format -> format -> number_sink
76,384 + 30,912 + 160 + 128 + 48 + 16 + 224 + 4,128 + 80 + 24
= 112,104 stack bytes
```

Thus the generation bound is 616,350 image + 112,104 stack + 294,155 retained P/G/body/E/PD bytes = 1,022,609 bytes, 25,967 below 2^20. The observed RSS is only a cross-check and is not used as an allocation bound. Generation and search are sequential, so the overall peak is the 1,044,273-byte search bound, 4,303 below 2^20.

## 9. Organizer experiment and limitations

Both declared experiments first regenerate the exact emitted program from the embedded plan data. They require every packed hash and per-op count, the total of 60,332 stored instructions, and the 147,252-operation schedule. They then compare that schedule with the scalar chain on eight full-width points.

`rho-r24-w22` executes the state machine of Section 5 from an organizer seed through returned messages. Before searching, it audits the 3-bit opcode, 12-bit register, 46-bit key and 17-bit identifier fields, including IDs 65,535, 65,536 and 66,719 in slot 3 and rejection of 66,720. SHAKE-256 maps the seed and attempt number to a 22-bit rho. The experiment installs all 256 starts `rho+i`, runs the claimed bit-sliced step in lockstep, and truncates each image to 22 bits. Its distinguished rule has the low four bits zero and the next three-bit integer less than five, so theta is 5/128. It uses 750 table words with the same four 64-bit record slots and probing order, 3,000 trails, a replay cap of 256 evaluations, and a 400-step deadline. Replay uses the scalar F evaluator, measures the stored trail, aligns both trails, and returns the two distinct predecessors of their first merge. The program recomputes both complete target digests and requires agreement on the low 22 bits before it emits a row.

Start-on-trail aliases and cap failures are common at width 22. On replay refusal, the reduced run restarts that walk instead of taking full-size failure code 13. If the reduced trail limit or deadline ends an attempt, it derives a new rho from the same seed and attempt number. These experiment-only liveness rules are explicit in the source and manifest. The full-size claim remains the single-rho attempt and terminal replay rule of Section 5.

`proj-r24-full-width` retains the prior projection check. Each trial has 17 starts and four chained steps, or 68 images. It returns the first distinct inputs whose complete digests agree on the low 12 bits. The random projection probability is 0.4283525380. The organizer independently recomputes each returned digest and checks the mask.

The full-search experiment establishes that the submitted step is connected to starts, distinguished ends, the table, restarts, replay, merge recovery, and returned target messages. It does not infer the 256-bit attack cost or success probability. The projection experiment remains bounded evidence for H_rand and emitted-program consistency.

No experiment reaches the birthday scale. No full-width collision is claimed. The random-function transfer can be wrong even if every reduced projection looks ordinary. The machine conventions are declared rather than imposed by the target profile.

## 10. Credits

Credit is technical provenance, not an assertion that any named author reviewed this package.

- c9a7e62c-7795-422c-8a3c-2de303e892dd, mitchuski: the r24 eight-body loop, fixed-bank closure construction, four-record table, r24 search parameters and exact success/failure ledger used as the direct base. Sections 5 and 7 adapt and reproduce its complete search and probability argument at this package's parameters. We reproduced its published total and score before changing the step.
- 71fefe66-9bf4-46ee-8b74-e91b3b562816, Jbenisek: LS1 embedding, lazy theta, 10-gate chi rows, polarity representation, search/replay implementation and its earlier lineage. Sections 5 and 7 also reproduce the state transitions and failure decomposition it introduced, rather than relying on the entry as an external premise.
- 760073e9-f795-4b4f-91ff-3b5fae8e3415, Jbenisek: S3-04 structured constants, one-round look-ahead output-polarity plan and packed 39-bit encoding.
- 5700dc84-83bd-47e7-8a8a-93016b27ea72 and 0bd0022d-aa41-40a4-81b9-61d18f1c444c, Jbenisek: the LS1 step and generic r24 search lineage credited by c9a7e62c.
- e7789ea7-3a44-46b1-b5d4-67821a4a8f13, cd30f68e-3b6a-4cd4-9e1c-a9ff7098b0dd and be664ca8-59ef-4683-aec2-5a072ae53e9c, Jbenisek: the r21 LS1/search lineage and the earlier S3-04 constants credited by 760073e9.
- 67f781f8-51f7-4298-b1b9-d651446adc2e, jungjipdo: the bit-sliced word-RAM step and register/encoding convention credited by both lines.
- Guo, Liu and Song, *Linear Structures: Applications to Cryptanalysis of Round-Reduced Keccak*; van Oorschot and Wiener; Pollard; and the Keccak implementation overview for the underlying public methods.

What is ours is the independent C combination, cyclic/fixed-closure optimizer, exact r24 regeneration and execution checks, packed memory reallocation, recomputed parameter row, freestanding measured generator and this ledger. No participant code was executed on the host.

## Appendix: Independent combined-step generator

```c
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * Independent generator for the r24 S3-04 / look-ahead / eight-body step.
 *
 * The graph builder descends from our sha3-r6 generator.  The structured
 * constants and the high-level polarity and loop constructions are transcribed
 * from the public proofs, not from executable participant source.
 */

enum { O_IN = 0, O_XOR = 1, O_AND = 2, O_OR = 3, O_NOT = 4 };
enum {
    NC = -1,
    MAX_NODES = 12000,
    MAX_FORMS = 2048,
    CONS_SIZE = 1 << 15,
    FORM_SIZE = 1 << 12,
    NREG = 4096,
    PLAN_ROWS = 320,
    PLAN_BITS = 320,
};

typedef struct {
    uint8_t op;
    uint8_t k;
    int a, b, lin;
} Node;

typedef struct {
    uint64_t mask[4];
    int node;
} Form;

typedef struct {
    int n;
    uint8_t p;
} Value;

typedef struct {
    uint8_t op;
    uint16_t d, a, b;
} Insn;

typedef struct {
    uint8_t subset;
    uint8_t trick_plus_one;
    uint8_t select_mask;
    uint8_t cost;
} Decision;

typedef struct {
    uint8_t cnot[PLAN_BITS];
    uint8_t dnot[PLAN_BITS];
    uint8_t target[PLAN_ROWS];
} Plan;

_Static_assert(sizeof(Decision) == 4, "Decision must have a stable byte encoding");
_Static_assert(sizeof(Plan) == 960, "Plan must have a stable byte encoding");

static Node nodes[MAX_NODES];
static Form forms[MAX_FORMS];
static int cons_table[CONS_SIZE];
static int form_table[FORM_SIZE];
static int node_count, form_count;
static Decision row_table[32][32];
static uint8_t row_min_cost[32];
static uint8_t row_min_target[32];

static const uint64_t RC[24] = {
    UINT64_C(0x0000000000000001), UINT64_C(0x0000000000008082),
    UINT64_C(0x800000000000808a), UINT64_C(0x8000000080008000),
    UINT64_C(0x000000000000808b), UINT64_C(0x0000000080000001),
    UINT64_C(0x8000000080008081), UINT64_C(0x8000000000008009),
    UINT64_C(0x000000000000008a), UINT64_C(0x0000000000000088),
    UINT64_C(0x0000000080008009), UINT64_C(0x000000008000000a),
    UINT64_C(0x000000008000808b), UINT64_C(0x800000000000008b),
    UINT64_C(0x8000000000008089), UINT64_C(0x8000000000008003),
    UINT64_C(0x8000000000008002), UINT64_C(0x8000000000000080),
    UINT64_C(0x000000000000800a), UINT64_C(0x800000008000000a),
    UINT64_C(0x8000000080008081), UINT64_C(0x8000000000008080),
    UINT64_C(0x0000000080000001), UINT64_C(0x8000000080008008),
};

static const int ROT[5][5] = {
    {0, 36, 3, 41, 18}, {1, 44, 10, 45, 2}, {62, 6, 43, 15, 61},
    {28, 55, 25, 21, 56}, {27, 20, 39, 8, 14},
};

/* S3-04 trial 1230.  Lanes 1, 4, 6 and 9 are overwritten by the point. */
static const uint64_t KL[25] = {
    UINT64_C(0x0000000000000000), UINT64_C(0x0000000000000000),
    UINT64_C(0x2d58eceb83b21614), UINT64_C(0x0000000000000000),
    UINT64_C(0x0000000000000000), UINT64_C(0xffffffffffffffff),
    UINT64_C(0x0000000000000000), UINT64_C(0x0000000000000000),
    UINT64_C(0x0000000000000000), UINT64_C(0x0000000000000000),
    UINT64_C(0xffffffffffffffff), UINT64_C(0x8b563b3ae0ec8583),
    UINT64_C(0x0000000000000000), UINT64_C(0x85ab1d9d707642c2),
    UINT64_C(0xe953898a3e26f4f5), UINT64_C(0xffffffffffffffff),
    UINT64_C(0x8000000000000006), 0, 0, 0, 0, 0, 0, 0, 0,
};

static void fail(const char *msg) {
    fprintf(stderr, "gen_combined: %s\n", msg);
    exit(1);
}

static uint64_t mix64(uint64_t x) {
    x ^= x >> 30;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27;
    x *= UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31);
}

static uint64_t rng_next(uint64_t *state) {
    uint64_t x = *state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    *state = x;
    return x;
}

static uint64_t node_hash(int op, int a, int b) {
    return mix64((uint64_t)(uint32_t)op * UINT64_C(0x9e3779b97f4a7c15) ^
                 (uint64_t)(uint32_t)a * UINT64_C(0x85ebca77c2b2ae63) ^
                 (uint64_t)(uint32_t)b * UINT64_C(0x27d4eb2f165667c5));
}

static uint64_t form_hash(const uint64_t m[4]) {
    return mix64(m[0] ^ mix64(m[1]) ^ (m[2] << 1) ^ (m[2] >> 63) ^
                 (m[3] << 7) ^ (m[3] >> 57));
}

static int new_node(int op, int a, int b) {
    if (node_count >= MAX_NODES) fail("node capacity exceeded");
    int n = node_count++;
    nodes[n] = (Node){(uint8_t)op, 0, a, b, -1};
    return n;
}

static int cons_node(int op, int a, int b) {
    if (op != O_NOT && a > b) {
        int t = a;
        a = b;
        b = t;
    }
    size_t h = (size_t)node_hash(op, a, b) & (CONS_SIZE - 1);
    for (;;) {
        int e = cons_table[h];
        if (!e) break;
        int n = e - 1;
        if (nodes[n].op == op && nodes[n].a == a && nodes[n].b == b) return n;
        h = (h + 1) & (CONS_SIZE - 1);
    }
    int n = new_node(op, a, b);
    cons_table[h] = n + 1;
    return n;
}

static int mask_zero(const uint64_t m[4]) {
    return (m[0] | m[1] | m[2] | m[3]) == 0;
}

static int find_form(const uint64_t m[4]) {
    size_t h = (size_t)form_hash(m) & (FORM_SIZE - 1);
    for (;;) {
        int e = form_table[h];
        if (!e) return -1;
        int f = e - 1;
        if (!memcmp(forms[f].mask, m, sizeof(forms[f].mask))) return f;
        h = (h + 1) & (FORM_SIZE - 1);
    }
}

static int add_form(const uint64_t m[4], int node) {
    if (form_count >= MAX_FORMS) fail("linear-form capacity exceeded");
    int f = form_count++;
    memcpy(forms[f].mask, m, sizeof(forms[f].mask));
    forms[f].node = node;
    size_t h = (size_t)form_hash(m) & (FORM_SIZE - 1);
    while (form_table[h]) h = (h + 1) & (FORM_SIZE - 1);
    form_table[h] = f + 1;
    return f;
}

static Value val(int n, int p) { return (Value){n, (uint8_t)(p & 1)}; }
static Value constant(int p) { return val(NC, p); }

static Value xor_value(Value a, Value b) {
    if (a.n == NC) return val(b.n, b.p ^ a.p);
    if (b.n == NC) return val(a.n, a.p ^ b.p);
    if (a.n == b.n) return constant(a.p ^ b.p);
    int la = nodes[a.n].lin, lb = nodes[b.n].lin;
    if (la >= 0 && lb >= 0) {
        uint64_t m[4];
        for (int i = 0; i < 4; i++) m[i] = forms[la].mask[i] ^ forms[lb].mask[i];
        int k = nodes[a.n].k ^ nodes[b.n].k;
        if (mask_zero(m)) return constant(k ^ a.p ^ b.p);
        int f = find_form(m);
        if (f >= 0) {
            int n = forms[f].node;
            return val(n, k ^ a.p ^ b.p ^ nodes[n].k);
        }
        int n = cons_node(O_XOR, a.n, b.n);
        nodes[n].k = (uint8_t)k;
        nodes[n].lin = add_form(m, n);
        return val(n, a.p ^ b.p);
    }
    return val(cons_node(O_XOR, a.n, b.n), a.p ^ b.p);
}

static Value complement_representation(Value a) {
    if (a.n == NC) return a;
    int before = node_count;
    int n = cons_node(O_NOT, a.n, 0);
    if (node_count > before && nodes[a.n].lin >= 0) {
        nodes[n].lin = nodes[a.n].lin;
        nodes[n].k = nodes[a.n].k ^ 1;
    }
    return val(n, a.p ^ 1);
}

static Value and_value(Value a, Value b, int select_polarity) {
    if (a.n == NC) return a.p ? b : constant(0);
    if (b.n == NC) return b.p ? a : constant(0);
    if (a.n == b.n) return a.p == b.p ? a : constant(0);
    if (!a.p && !b.p) return val(cons_node(O_AND, a.n, b.n), 0);
    if (a.p && b.p) return val(cons_node(O_OR, a.n, b.n), 1);
    int A = !a.p ? a.n : b.n;
    int B = !a.p ? b.n : a.n;
    if (select_polarity) {
        Value na = complement_representation(val(A, 0));
        return val(cons_node(O_OR, na.n, B), 1);
    }
    int t = cons_node(O_AND, A, B);
    return xor_value(val(A, 0), val(t, 0));
}

static int term_cost(Value a, Value b) {
    if (a.n == NC || b.n == NC || a.n == b.n) return 0;
    return ((a.p ^ 1) == b.p) ? 1 : 2;
}

static void reset_graph(int inputs, int affine_inputs) {
    memset(cons_table, 0, sizeof(cons_table));
    memset(form_table, 0, sizeof(form_table));
    node_count = form_count = 0;
    for (int j = 0; j < inputs; j++) {
        int n = new_node(O_IN, 0, 0);
        if (affine_inputs) {
            uint64_t m[4] = {0, 0, 0, 0};
            if (j >= 256) fail("too many affine inputs");
            m[j >> 6] = UINT64_C(1) << (j & 63);
            nodes[n].lin = add_form(m, n);
        }
    }
}

static void choose_dynamic_row(const Value b[5], int need, int *subset, int *trick) {
    int distinct = 1;
    for (int x = 0; x < 5; x++) {
        if (b[x].n == NC) distinct = 0;
        for (int y = x + 1; y < 5; y++) if (b[x].n == b[y].n) distinct = 0;
    }
    int best_subset = -1, best_trick = -1, best_cost = 1 << 30;
    int jmax = distinct ? 5 : 0;
    for (int j = -1; j < jmax; j++) {
        if (j >= 0 && (!((need >> j) & 1) || !((need >> ((j + 1) % 5)) & 1))) continue;
        for (int s = 0; s < 32; s++) {
            Value bb[5];
            memcpy(bb, b, sizeof(bb));
            int cost = 0;
            for (int x = 0; x < 5; x++) if ((s >> x) & 1) {
                if (b[x].n == NC) cost = 1 << 29;
                else { bb[x].p ^= 1; cost++; }
            }
            for (int x = 0; x < 5; x++) if ((need >> x) & 1) {
                if (x == j) {
                    int k = (j + 1) % 5;
                    Value p1 = bb[(k + 1) % 5], p2 = bb[(k + 2) % 5];
                    if ((p1.p ^ 1) == p2.p) {
                        Value bk = bb[k];
                        bk.p ^= (p1.p ^ 1);
                        cost += term_cost(bk, bb[(x + 2) % 5]);
                    } else {
                        cost++;
                    }
                } else {
                    cost += term_cost(bb[(x + 1) % 5], bb[(x + 2) % 5]);
                }
            }
            if (cost < best_cost) {
                best_cost = cost;
                best_subset = s;
                best_trick = j;
            }
        }
    }
    *subset = best_subset;
    *trick = best_trick;
}

static void build_dynamic_row(Value b[5], int need, Value out[5]) {
    int subset, trick;
    choose_dynamic_row(b, need, &subset, &trick);
    for (int x = 0; x < 5; x++) if ((subset >> x) & 1)
        b[x] = complement_representation(b[x]);
    int k = (trick + 1) % 5;
    if (trick >= 0) {
        Value t = and_value(val(b[(k + 1) % 5].n, b[(k + 1) % 5].p ^ 1),
                            b[(k + 2) % 5], 0);
        out[k] = xor_value(b[k], t);
    }
    for (int x = 0; x < 5; x++) if ((need >> x) & 1) {
        if (trick >= 0 && x == k) continue;
        Value t1 = x == trick ? out[k] : b[(x + 1) % 5];
        Value t = and_value(val(t1.n, t1.p ^ 1), b[(x + 2) % 5], 0);
        out[x] = xor_value(b[x], t);
    }
}

static int sim_term(int pa, int pb, int select, int *pout) {
    if (pa == pb) {
        *pout = pa;
        return 1;
    }
    *pout = select;
    return 2;
}

static void make_row_table(void) {
    for (int pin = 0; pin < 32; pin++) {
        int min_cost = 255, min_target = 0;
        for (int target = 0; target < 32; target++) {
            Decision best = {0, 0, 0, 255};
            for (int subset = 0; subset < 32; subset++) {
                int bp[5];
                for (int x = 0; x < 5; x++) bp[x] = ((pin >> x) & 1) ^ ((subset >> x) & 1);
                for (int trick = -1; trick < 5; trick++) {
                    for (int sel = 0; sel < 32; sel++) {
                        int op[5] = {0, 0, 0, 0, 0};
                        int cost = __builtin_popcount((unsigned)subset);
                        int k = (trick + 1) % 5;
                        if (trick >= 0) {
                            int tp;
                            cost += sim_term(bp[(k + 1) % 5] ^ 1, bp[(k + 2) % 5],
                                             (sel >> k) & 1, &tp) + 1;
                            op[k] = bp[k] ^ tp;
                        }
                        for (int x = 0; x < 5; x++) {
                            if (trick >= 0 && x == k) continue;
                            int first = x == trick ? op[k] : bp[(x + 1) % 5];
                            int tp;
                            cost += sim_term(first ^ 1, bp[(x + 2) % 5],
                                             (sel >> x) & 1, &tp) + 1;
                            op[x] = bp[x] ^ tp;
                        }
                        int got = 0;
                        for (int x = 0; x < 5; x++) got |= op[x] << x;
                        if (got == target && cost < best.cost) {
                            best = (Decision){(uint8_t)subset, (uint8_t)(trick + 1),
                                              (uint8_t)sel, (uint8_t)cost};
                        }
                    }
                }
            }
            if (best.cost == 255) fail("unreachable row target polarity");
            row_table[pin][target] = best;
            if (best.cost < min_cost) {
                min_cost = best.cost;
                min_target = target;
            }
        }
        row_min_cost[pin] = (uint8_t)min_cost;
        row_min_target[pin] = (uint8_t)min_target;
    }
}

static void build_target_row(Value b[5], int target, Value out[5]) {
    int pin = 0;
    for (int x = 0; x < 5; x++) pin |= b[x].p << x;
    Decision d = row_table[pin][target];
    for (int x = 0; x < 5; x++) if ((d.subset >> x) & 1)
        b[x] = complement_representation(b[x]);
    int trick = (int)d.trick_plus_one - 1;
    int k = (trick + 1) % 5;
    if (trick >= 0) {
        Value t = and_value(val(b[(k + 1) % 5].n, b[(k + 1) % 5].p ^ 1),
                            b[(k + 2) % 5], (d.select_mask >> k) & 1);
        out[k] = xor_value(b[k], t);
    }
    for (int x = 0; x < 5; x++) {
        if (trick >= 0 && x == k) continue;
        Value t1 = x == trick ? out[k] : b[(x + 1) % 5];
        Value t = and_value(val(t1.n, t1.p ^ 1), b[(x + 2) % 5],
                            (d.select_mask >> x) & 1);
        out[x] = xor_value(b[x], t);
    }
    int got = 0;
    for (int x = 0; x < 5; x++) got |= out[x].p << x;
    if (got != target) fail("row-table construction mismatch");
}

static void row_patterns(const uint8_t state[1600], const uint8_t cnot[320],
                         const uint8_t dnot[320], uint8_t patterns[320]) {
    uint8_t cp[320], dp[320];
    for (int x = 0; x < 5; x++) for (int z = 0; z < 64; z++) {
        int p = 0;
        for (int y = 0; y < 5; y++) p ^= state[64 * (x + 5 * y) + z];
        cp[64 * x + z] = (uint8_t)(p ^ cnot[64 * x + z]);
    }
    for (int x = 0; x < 5; x++) for (int z = 0; z < 64; z++)
        dp[64 * x + z] = (uint8_t)(cp[64 * ((x + 4) % 5) + z] ^
            cp[64 * ((x + 1) % 5) + ((z + 63) & 63)] ^ dnot[64 * x + z]);
    for (int Y = 0; Y < 5; Y++) for (int z = 0; z < 64; z++) {
        int pin = 0;
        for (int X = 0; X < 5; X++) {
            int y = X, x = (3 * Y + X) % 5;
            int zz = (z - ROT[x][y]) & 63;
            int p = state[64 * (x + 5 * y) + zz] ^ dp[64 * x + zz];
            pin |= p << X;
        }
        patterns[64 * Y + z] = (uint8_t)pin;
    }
}

static void targets_to_state(const uint8_t target[320], uint8_t state[1600]) {
    for (int Y = 0; Y < 5; Y++) for (int z = 0; z < 64; z++)
        for (int X = 0; X < 5; X++)
            state[64 * (X + 5 * Y) + z] = (target[64 * Y + z] >> X) & 1;
}

static void state_to_targets(const uint8_t state[1600], uint8_t target[320]) {
    for (int Y = 0; Y < 5; Y++) for (int z = 0; z < 64; z++) {
        int t = 0;
        for (int X = 0; X < 5; X++) t |= state[64 * (X + 5 * Y) + z] << X;
        target[64 * Y + z] = (uint8_t)t;
    }
}

static int current_cost(const uint8_t input[1600], const Plan *p) {
    uint8_t patterns[320];
    row_patterns(input, p->cnot, p->dnot, patterns);
    int cost = 3200;
    for (int i = 0; i < 320; i++)
        cost += p->cnot[i] + p->dnot[i] + row_table[patterns[i]][p->target[i]].cost;
    return cost;
}

static int next_estimate(const Plan *p) {
    static const uint8_t zero[320] = {0};
    uint8_t state[1600], patterns[320];
    targets_to_state(p->target, state);
    row_patterns(state, zero, zero, patterns);
    int cost = 3200;
    for (int i = 0; i < 320; i++) cost += row_min_cost[patterns[i]];
    return cost;
}

static int fixed_next_estimate(const Plan *p, const uint8_t fixed_output[1600]) {
    static const uint8_t zero[320] = {0};
    uint8_t state[1600], patterns[320], targets[320];
    targets_to_state(p->target, state);
    state_to_targets(fixed_output, targets);
    row_patterns(state, zero, zero, patterns);
    int cost = 3200;
    for (int i = 0; i < 320; i++) cost += row_table[patterns[i]][targets[i]].cost;
    return cost;
}

static int output_distance(const Plan *p, const uint8_t reference[1600]) {
    uint8_t state[1600];
    targets_to_state(p->target, state);
    int distance = 0;
    for (int i = 0; i < 1600; i++) distance += state[i] != reference[i];
    return distance;
}

static int objective(const uint8_t input[1600], const Plan *p,
                     const uint8_t next_fixed_output[1600],
                     const uint8_t bridge_reference[1600]) {
    int tail = bridge_reference ? 16 * output_distance(p, bridge_reference) :
        next_fixed_output ? 16 * fixed_next_estimate(p, next_fixed_output) :
                            3 * next_estimate(p);
    return 16 * current_cost(input, p) + tail;
}

static int free_output_cost(const uint8_t input[1600], const Plan *p) {
    uint8_t patterns[320];
    row_patterns(input, p->cnot, p->dnot, patterns);
    int cost = 3200;
    for (int i = 0; i < 320; i++)
        cost += p->cnot[i] + p->dnot[i] + row_min_cost[patterns[i]];
    return cost;
}

static void optimize_plan(const uint8_t input[1600], const uint8_t fixed_output[1600],
                          const uint8_t next_fixed_output[1600],
                          const uint8_t bridge_reference[1600], uint64_t seed,
                          int iterations, Plan *result) {
    Plan cur = {0}, best;
    uint8_t patterns[320];
    if (!fixed_output) {
        int free_cur = free_output_cost(input, &cur), free_best = free_cur;
        Plan free_plan = cur;
        int free_iterations = iterations < 10000 ? 10000 : iterations;
        for (int it = 0; it < free_iterations; it++) {
            uint64_t r = rng_next(&seed);
            int kind = (int)(r & 1), index = (int)((r >> 8) % 320);
            uint8_t *bit = kind ? &cur.dnot[index] : &cur.cnot[index];
            *bit ^= 1;
            int trial = free_output_cost(input, &cur);
            int diff = trial - free_cur;
            int temp = 1 + (free_iterations - it) * 24 / free_iterations;
            uint64_t denom = (uint64_t)temp + (uint64_t)(diff > 0 ? diff * 12 : 0);
            int accept = diff <= 0 || (rng_next(&seed) % denom) < (uint64_t)temp;
            if (accept) {
                free_cur = trial;
                if (trial < free_best) {
                    free_best = trial;
                    free_plan = cur;
                }
            } else {
                *bit ^= 1;
            }
        }
        cur = free_plan;
        for (int sweep = 0; sweep < 3; sweep++)
            for (int kind = 0; kind < 2; kind++) for (int i = 0; i < 320; i++) {
                uint8_t *bit = kind ? &cur.dnot[i] : &cur.cnot[i];
                int before = free_output_cost(input, &cur);
                *bit ^= 1;
                if (free_output_cost(input, &cur) > before) *bit ^= 1;
            }
    }
    row_patterns(input, cur.cnot, cur.dnot, patterns);
    if (fixed_output) state_to_targets(fixed_output, cur.target);
    else for (int i = 0; i < 320; i++) cur.target[i] = row_min_target[patterns[i]];
    int cur_obj = objective(input, &cur, next_fixed_output, bridge_reference), best_obj = cur_obj;
    best = cur;
    for (int it = 0; it < iterations; it++) {
        uint64_t r = rng_next(&seed);
        int kind = fixed_output ? (int)(r & 1) : 2, index, old;
        if (kind == 0) {
            index = (int)((r >> 8) % 320);
            old = cur.cnot[index];
            cur.cnot[index] ^= 1;
        } else if (kind == 1) {
            index = (int)((r >> 8) % 320);
            old = cur.dnot[index];
            cur.dnot[index] ^= 1;
        } else if (!fixed_output) {
            index = (int)((r >> 8) % 320);
            old = cur.target[index];
            cur.target[index] ^= (uint8_t)(1 + ((r >> 24) % 31));
        } else {
            continue;
        }
        int trial = objective(input, &cur, next_fixed_output, bridge_reference);
        int diff = trial - cur_obj;
        int temp = 1 + (iterations - it) * 96 / (iterations ? iterations : 1);
        uint64_t denom = (uint64_t)temp + (uint64_t)(diff > 0 ? diff * 24 : 0);
        int accept = diff <= 0 || (rng_next(&seed) % denom) < (uint64_t)temp;
        if (accept) {
            cur_obj = trial;
            if (trial < best_obj) {
                best_obj = trial;
                best = cur;
            }
        } else if (kind == 0) cur.cnot[index] = (uint8_t)old;
        else if (kind == 1) cur.dnot[index] = (uint8_t)old;
        else cur.target[index] = (uint8_t)old;
    }
    cur = best;
    cur_obj = best_obj;
    for (int sweep = 0; sweep < 2; sweep++) {
        if (fixed_output)
            for (int kind = 0; kind < 2; kind++) for (int i = 0; i < 320; i++) {
                uint8_t *bit = kind ? &cur.dnot[i] : &cur.cnot[i];
                *bit ^= 1;
                int trial = objective(input, &cur, next_fixed_output, bridge_reference);
                if (trial <= cur_obj) cur_obj = trial;
                else *bit ^= 1;
            }
        if (!fixed_output) for (int i = 0; i < 320; i++) {
            int old = cur.target[i], chosen = old, chosen_obj = cur_obj;
            for (int t = 0; t < 32; t++) {
                cur.target[i] = (uint8_t)t;
                int trial = objective(input, &cur, next_fixed_output, bridge_reference);
                if (trial < chosen_obj) {
                    chosen_obj = trial;
                    chosen = t;
                }
            }
            cur.target[i] = (uint8_t)chosen;
            cur_obj = chosen_obj;
        }
    }
    *result = cur;
}

static void theta_graph(Value S[25][64], Value D[5][64], const uint8_t *cnot,
                        const uint8_t *dnot) {
    Value C[5][64];
    for (int x = 0; x < 5; x++) for (int z = 0; z < 64; z++) {
        Value s = S[x][z];
        for (int y = 1; y < 5; y++) s = xor_value(s, S[x + 5 * y][z]);
        if (cnot && cnot[64 * x + z]) s = complement_representation(s);
        C[x][z] = s;
    }
    for (int x = 0; x < 5; x++) for (int z = 0; z < 64; z++) {
        Value d = xor_value(C[(x + 4) % 5][z], C[(x + 1) % 5][(z + 63) & 63]);
        if (dnot && dnot[64 * x + z]) d = complement_representation(d);
        D[x][z] = d;
    }
}

static Value lazy_c(Value S[25][64], Value C[5][64], uint8_t have_c[320],
                    const uint8_t *cnot, int x, int z) {
    int index = 64 * x + z;
    if (!have_c[index]) {
        Value s = S[x][z];
        for (int y = 1; y < 5; y++) s = xor_value(s, S[x + 5 * y][z]);
        if (cnot && cnot[index]) s = complement_representation(s);
        C[x][z] = s;
        have_c[index] = 1;
    }
    return C[x][z];
}

static Value lazy_d(Value S[25][64], Value C[5][64], Value D[5][64],
                    uint8_t have_c[320], uint8_t have_d[320],
                    const uint8_t *cnot, const uint8_t *dnot, int x, int z) {
    int index = 64 * x + z;
    if (!have_d[index]) {
        Value a = lazy_c(S, C, have_c, cnot, (x + 4) % 5, z);
        Value b = lazy_c(S, C, have_c, cnot, (x + 1) % 5, (z + 63) & 63);
        Value d = xor_value(a, b);
        if (dnot && dnot[index]) d = complement_representation(d);
        D[x][z] = d;
        have_d[index] = 1;
    }
    return D[x][z];
}

static void build_prefix_graph(const Plan *prefix_plan, int outputs[1600],
                               uint8_t output_p[1600]) {
    Value S[25][64], NS[25][64], D[5][64];
    reset_graph(256, 1);
    for (int l = 0; l < 25; l++) for (int z = 0; z < 64; z++)
        S[l][z] = constant((KL[l] >> z) & 1);
    for (int z = 0; z < 64; z++) {
        S[1][z] = val(z, 0);
        S[6][z] = val(64 + z, 0);
        S[4][z] = val(128 + z, 0);
        S[9][z] = val(192 + z, 0);
        S[11][z] = xor_value(xor_value(val(z, 0), val(64 + z, 0)),
                             constant((KL[11] >> z) & 1));
        S[14][z] = xor_value(xor_value(val(128 + z, 0), val(192 + z, 0)),
                             constant((KL[14] >> z) & 1));
    }
    for (int round = 0; round < 2; round++) {
        theta_graph(S, D, round == 1 ? prefix_plan->cnot : NULL,
                    round == 1 ? prefix_plan->dnot : NULL);
        memcpy(NS, S, sizeof(NS));
        for (int Y = 0; Y < 5; Y++) for (int z = 0; z < 64; z++) {
            Value b[5], out[5];
            for (int X = 0; X < 5; X++) {
                int y = X, x = (3 * Y + X) % 5;
                int zz = (z - ROT[x][y]) & 63;
                b[X] = xor_value(S[x + 5 * y][zz], D[x][zz]);
            }
            build_dynamic_row(b, 0x1f, out);
            for (int X = 0; X < 5; X++) NS[X + 5 * Y][z] = out[X];
        }
        for (int z = 0; z < 64; z++) NS[0][z].p ^= (RC[round] >> z) & 1;
        memcpy(S, NS, sizeof(S));
    }
    for (int q = 0; q < 1600; q++) {
        Value v = S[q >> 6][q & 63];
        if (v.n == NC) fail("constant prefix output");
        outputs[q] = v.n;
        output_p[q] = v.p;
    }
}

static int live_operation_count(const int *outputs, int output_count, int input_count) {
    uint8_t *live = calloc((size_t)node_count, 1);
    if (!live) fail("live-count allocation failure");
    for (int j = 0; j < output_count; j++) live[outputs[j]] = 1;
    int count = 0;
    for (int i = node_count - 1; i >= input_count; i--) if (live[i]) {
        count++;
        live[nodes[i].a] = 1;
        if (nodes[i].op != O_NOT) live[nodes[i].b] = 1;
    }
    free(live);
    return count;
}

static void optimize_prefix(Plan *plan, int outputs[1600], uint8_t output_p[1600]) {
    memset(plan, 0, sizeof(*plan));
    build_prefix_graph(plan, outputs, output_p);
    int best = live_operation_count(outputs, 1600, 256);
    int gain = 0;
    for (int sweep = 0; sweep < 3; sweep++) {
        for (int kind = 0; kind < 2; kind++) for (int i = 0; i < 320; i++) {
            uint8_t *bit = kind ? &plan->dnot[i] : &plan->cnot[i];
            *bit ^= 1;
            build_prefix_graph(plan, outputs, output_p);
            int trial = live_operation_count(outputs, 1600, 256);
            if (trial < best) {
                gain += best - trial;
                best = trial;
            } else {
                *bit ^= 1;
            }
        }
    }
    build_prefix_graph(plan, outputs, output_p);
    if (live_operation_count(outputs, 1600, 256) != best)
        fail("prefix greedy count mismatch");
    printf("prefix-round1-greedy-gain %d\n", gain);
}

static void build_body_graph(const uint8_t input_p[1600], const Plan *plan,
                             int outputs[1600], uint8_t output_p[1600]) {
    Value S[25][64], NS[25][64], C[5][64], D[5][64];
    uint8_t have_c[320] = {0}, have_d[320] = {0};
    reset_graph(1600, 0);
    for (int q = 0; q < 1600; q++) S[q >> 6][q & 63] = val(q, input_p[q]);
    memcpy(NS, S, sizeof(NS));
    for (int Y = 0; Y < 5; Y++) for (int z = 0; z < 64; z++) {
        Value b[5], out[5];
        for (int X = 0; X < 5; X++) {
            int y = X, x = (3 * Y + X) % 5;
            int zz = (z - ROT[x][y]) & 63;
            Value d = lazy_d(S, C, D, have_c, have_d, plan->cnot, plan->dnot, x, zz);
            b[X] = xor_value(S[x + 5 * y][zz], d);
        }
        build_target_row(b, plan->target[64 * Y + z], out);
        for (int X = 0; X < 5; X++) NS[X + 5 * Y][z] = out[X];
    }
    for (int q = 0; q < 1600; q++) {
        Value v = NS[q >> 6][q & 63];
        outputs[q] = v.n;
        output_p[q] = v.p;
    }
}

static void build_end_graph(const uint8_t input_p[1600], int outputs[256],
                            uint8_t output_p[256]) {
    Value S[25][64], C[5][64], D[5][64];
    uint8_t have_c[320] = {0}, have_d[320] = {0};
    reset_graph(1600, 0);
    for (int q = 0; q < 1600; q++) S[q >> 6][q & 63] = val(q, input_p[q]);
    for (int z = 0; z < 64; z++) {
        Value b[5], out[5];
        for (int X = 0; X < 5; X++) {
            int y = X, x = X;
            int zz = (z - ROT[x][y]) & 63;
            Value d = lazy_d(S, C, D, have_c, have_d, NULL, NULL, x, zz);
            b[X] = xor_value(S[x + 5 * y][zz], d);
        }
        build_dynamic_row(b, 0x0f, out);
        for (int X = 0; X < 4; X++) {
            Value v = out[X];
            if (X == 0) v.p ^= (RC[23] >> z) & 1;
            int j = 64 * X + z;
            outputs[j] = v.n;
            output_p[j] = v.p;
        }
    }
}

static Insn *allocate_block(const int *outputs, const int *output_regs, int output_count,
                            const int *input_regs, int input_count, size_t *program_count,
                            int counts[5], int *high_reg) {
    uint8_t *live = calloc((size_t)node_count, 1);
    uint16_t *last = calloc((size_t)node_count, sizeof(*last));
    uint16_t *reg = calloc((size_t)node_count, sizeof(*reg));
    uint16_t *out_index = malloc((size_t)node_count * sizeof(*out_index));
    uint16_t *free_regs = malloc(NREG * sizeof(*free_regs));
    uint8_t *busy = calloc(NREG, 1);
    uint8_t *reserved = calloc(NREG, 1);
    Insn *prog = malloc((size_t)node_count * sizeof(*prog));
    if (!live || !last || !reg || !out_index || !free_regs || !busy || !reserved || !prog)
        fail("allocator memory failure");
    memset(out_index, 0xff, (size_t)node_count * sizeof(*out_index));
    memset(counts, 0, 5 * sizeof(*counts));
    for (int j = 0; j < output_count; j++) {
        if (outputs[j] < input_count || out_index[outputs[j]] != UINT16_MAX)
            fail("invalid/shared block output");
        live[outputs[j]] = 1;
        out_index[outputs[j]] = j;
        reserved[output_regs[j]] = 1;
    }
    for (int i = node_count - 1; i >= input_count; i--) if (live[i]) {
        live[nodes[i].a] = 1;
        if (nodes[i].op != O_NOT) live[nodes[i].b] = 1;
    }
    for (int i = input_count; i < node_count; i++) if (live[i]) {
        last[nodes[i].a] = i;
        if (nodes[i].op != O_NOT) last[nodes[i].b] = i;
    }
    for (int j = 0; j < output_count; j++) last[outputs[j]] = UINT16_MAX;
    for (int j = 0; j < input_count; j++) {
        reg[j] = input_regs[j];
        if (last[j]) busy[input_regs[j]] = 1;
    }
    int free_count = 0;
    for (int r = NREG - 1; r >= 0; r--)
        if (!busy[r] && !reserved[r]) free_regs[free_count++] = r;
    size_t pc = 0;
    int high = 0;
    for (int j = 0; j < input_count; j++) if (input_regs[j] + 1 > high) high = input_regs[j] + 1;
    for (int j = 0; j < output_count; j++) if (output_regs[j] + 1 > high) high = output_regs[j] + 1;
    for (int i = input_count; i < node_count; i++) if (live[i]) {
        int op = nodes[i].op, a = nodes[i].a, b = op == O_NOT ? a : nodes[i].b;
        if (last[a] == i) {
            int r = reg[a];
            busy[r] = 0;
            if (!reserved[r]) free_regs[free_count++] = r;
        }
        if (b != a && last[b] == i) {
            int r = reg[b];
            busy[r] = 0;
            if (!reserved[r]) free_regs[free_count++] = r;
        }
        int d;
        if (out_index[i] != UINT16_MAX) {
            d = output_regs[out_index[i]];
            if (busy[d]) fail("fixed output register busy");
        } else {
            if (!free_count) fail("register file exhausted");
            d = free_regs[--free_count];
        }
        busy[d] = 1;
        reg[i] = d;
        if (d + 1 > high) high = d + 1;
        uint8_t enc = op == O_XOR ? 0 : op == O_AND ? 1 : op == O_OR ? 2 : 3;
        prog[pc++] = (Insn){enc, (uint16_t)d, (uint16_t)reg[a],
                           (uint16_t)(op == O_NOT ? 0 : reg[nodes[i].b])};
        counts[op]++;
    }
    free(live); free(last); free(reg); free(out_index); free(free_regs); free(busy); free(reserved);
    *program_count = pc;
    *high_reg = high;
    return prog;
}

#ifndef PACKED_ONLY
static void write_program(const char *path, const Insn *prog, size_t n) {
    FILE *f = fopen(path, "wb");
    if (!f) {
        fprintf(stderr, "gen_combined: fopen %s: %s\n", path, strerror(errno));
        exit(1);
    }
    for (size_t i = 0; i < n; i++) {
        uint64_t w = (uint64_t)prog[i].op | (uint64_t)prog[i].d << 3 |
                     (uint64_t)prog[i].a << 15 | (uint64_t)prog[i].b << 27;
        uint8_t out[5];
        for (int j = 0; j < 5; j++) out[j] = (uint8_t)(w >> (8 * j));
        if (fwrite(out, 1, 5, f) != 5) fail("program write failed");
    }
    if (fclose(f)) fail("program close failed");
}
#endif

static void write_packed_program(const char *path, const Insn *prog, size_t n) {
    size_t bytes = (39 * n + 7) / 8;
    uint8_t *packed = calloc(bytes ? bytes : 1, 1);
    if (!packed) fail("packed-program allocation failure");
    for (size_t i = 0; i < n; i++) {
        uint64_t w = (uint64_t)prog[i].op | (uint64_t)prog[i].d << 3 |
                     (uint64_t)prog[i].a << 15 | (uint64_t)prog[i].b << 27;
        size_t bit = 39 * i;
        for (int k = 0; k < 39; k++)
            packed[(bit + (size_t)k) >> 3] |= (uint8_t)(((w >> k) & 1) << ((bit + (size_t)k) & 7));
    }
    FILE *f = fopen(path, "wb");
    if (!f || (bytes && fwrite(packed, 1, bytes, f) != bytes) || fclose(f))
        fail("packed program write failed");
    free(packed);
}

static size_t emit_block(const char *dir, const char *name, const int *outputs,
                         int output_count, int input_count, int input_base,
                         int output_base, int *highest) {
    int *input_regs = malloc((size_t)input_count * sizeof(*input_regs));
    int *output_regs = malloc((size_t)output_count * sizeof(*output_regs));
    if (!input_regs || !output_regs) fail("register-map allocation failure");
    for (int i = 0; i < input_count; i++) input_regs[i] = input_base + i;
    for (int i = 0; i < output_count; i++) output_regs[i] = output_base + i;
    size_t n;
    int mix[5], high;
    Insn *prog = allocate_block(outputs, output_regs, output_count, input_regs,
                                input_count, &n, mix, &high);
    char path[4096];
#ifndef PACKED_ONLY
    if (snprintf(path, sizeof(path), "%s/%s.bin", dir, name) >= (int)sizeof(path))
        fail("output path too long");
    write_program(path, prog, n);
#endif
    if (snprintf(path, sizeof(path), "%s/%s.p39", dir, name) >= (int)sizeof(path))
        fail("packed output path too long");
    write_packed_program(path, prog, n);
    printf("block %s XOR %d AND %d OR %d NOT %d total %zu highest-register+1 %d\n",
           name, mix[O_XOR], mix[O_AND], mix[O_OR], mix[O_NOT], n, high);
    if (high > *highest) *highest = high;
    free(prog); free(input_regs); free(output_regs);
    return n;
}

static size_t emit_bridge(const char *dir, const uint8_t from[1600],
                          const uint8_t to[1600]) {
    Insn *prog = malloc(1600 * sizeof(*prog));
    if (!prog) fail("bridge allocation failure");
    size_t n = 0;
    for (int q = 0; q < 1600; q++) if (from[q] != to[q])
        prog[n++] = (Insn){3, (uint16_t)(256 + q), (uint16_t)(256 + q), 0};
    char path[4096];
#ifndef PACKED_ONLY
    if (snprintf(path, sizeof(path), "%s/G.bin", dir) >= (int)sizeof(path))
        fail("output path too long");
    write_program(path, prog, n);
#endif
    if (snprintf(path, sizeof(path), "%s/G.p39", dir) >= (int)sizeof(path))
        fail("packed bridge path too long");
    write_packed_program(path, prog, n);
    printf("block G XOR 0 AND 0 OR 0 NOT %zu total %zu highest-register+1 1856\n", n, n);
    free(prog);
    return n;
}

static void write_regeneration_data(const char *path, const Plan *prefix_plan,
                                    const Plan best_chain[8],
                                    const uint8_t best_cycle[1600]) {
    static const uint8_t magic[8] = {'H', 'S', '2', '4', 'P', 'L', 'N', '1'};
    FILE *f = fopen(path, "wb");
    if (!f || fwrite(magic, sizeof(magic), 1, f) != 1 ||
        fwrite(prefix_plan, sizeof(*prefix_plan), 1, f) != 1 ||
        fwrite(best_chain, sizeof(*best_chain), 8, f) != 8 ||
        fwrite(best_cycle, 1600, 1, f) != 1 ||
        fwrite(row_table, sizeof(row_table), 1, f) != 1 || fclose(f))
        fail("cannot write regeneration data");
}

int main(int argc, char **argv) {
    const char *dir = argc > 1 ? argv[1] : ".";
    int iterations = argc > 2 ? atoi(argv[2]) : 30000;
    int trials = argc > 3 ? atoi(argv[3]) : 4;
    if (iterations < 0 || trials < 1 || trials > 32) fail("invalid optimizer settings");
    make_row_table();

    int prefix_nodes[1600], body_nodes[1600], end_nodes[256];
    uint8_t prefix_p[1600], out_p[1600], end_p[256];
    Plan prefix_plan;
    optimize_prefix(&prefix_plan, prefix_nodes, prefix_p);
    int prefix_node_count = node_count;
    Node *prefix_copy = malloc((size_t)node_count * sizeof(*prefix_copy));
    Form *form_copy = malloc((size_t)form_count * sizeof(*form_copy));
    int prefix_form_count = form_count;
    if (!prefix_copy || !form_copy) fail("prefix snapshot allocation failure");
    memcpy(prefix_copy, nodes, (size_t)node_count * sizeof(*nodes));
    memcpy(form_copy, forms, (size_t)form_count * sizeof(*forms));

    static const int runs[8] = {3, 3, 3, 3, 3, 2, 2, 2};
    Plan best_chain[8], chain[8], scratch[8];
    uint8_t best_cycle[1600];
    long long best_weighted = -1;
    for (int trial = 0; trial < trials; trial++) {
        uint8_t cycle[1600], input[1600];
        memcpy(cycle, prefix_p, sizeof(cycle));
        int derivations = trial % 3;
        for (int outer = 0; outer < derivations; outer++) {
            memcpy(input, cycle, sizeof(input));
            for (int b = 0; b < 7; b++) {
                uint64_t seed = UINT64_C(0x243f6a8885a308d3) ^
                    (uint64_t)(trial + 1) * UINT64_C(0xd1b54a32d192ed03) ^
                    (uint64_t)(outer + 1) * UINT64_C(0x9e3779b97f4a7c15) ^
                    (uint64_t)(b + 1) * UINT64_C(0x94d049bb133111eb);
                optimize_plan(input, NULL, NULL, NULL, seed, iterations, &scratch[b]);
                targets_to_state(scratch[b].target, input);
            }
            uint64_t seed = UINT64_C(0x13198a2e03707344) ^
                (uint64_t)(trial + 1) * UINT64_C(0x94d049bb133111eb) ^
                (uint64_t)(outer + 1) * UINT64_C(0xd1b54a32d192ed03);
            optimize_plan(input, NULL, NULL, prefix_p, seed, iterations, &scratch[7]);
            targets_to_state(scratch[7].target, cycle);
        }

        memcpy(input, cycle, sizeof(input));
        long long weighted = 0;
        for (int b = 0; b < 8; b++) {
            const uint8_t *fixed = b == 7 ? cycle : NULL;
            uint64_t seed = UINT64_C(0x9e3779b97f4a7c15) ^
                (uint64_t)(trial + 1) * UINT64_C(0xd1b54a32d192ed03) ^
                (uint64_t)(b + 1) * UINT64_C(0x94d049bb133111eb);
            const uint8_t *next_fixed = b == 6 ? cycle : NULL;
            optimize_plan(input, fixed, next_fixed, NULL, seed, iterations, &chain[b]);
            int cost = current_cost(input, &chain[b]);
            weighted += (long long)runs[b] * cost;
            targets_to_state(chain[b].target, input);
        }
        int bridge = 0;
        for (int i = 0; i < 1600; i++) bridge += cycle[i] != prefix_p[i];
        weighted += bridge;
        printf("optimizer trial %d body-plus-bridge-operations %lld bridge %d\n",
               trial, weighted, bridge);
        if (best_weighted < 0 || weighted < best_weighted) {
            best_weighted = weighted;
            memcpy(best_chain, chain, sizeof(best_chain));
            memcpy(best_cycle, cycle, sizeof(best_cycle));
        }
    }

    if (argc > 4)
        write_regeneration_data(argv[4], &prefix_plan, best_chain, best_cycle);

    int highest = 0;
    memcpy(nodes, prefix_copy, (size_t)prefix_node_count * sizeof(*nodes));
    memcpy(forms, form_copy, (size_t)prefix_form_count * sizeof(*forms));
    node_count = prefix_node_count;
    form_count = prefix_form_count;
    free(prefix_copy);
    free(form_copy);
    size_t stored = emit_block(dir, "P", prefix_nodes, 1600, 256, 0, 256, &highest);
    size_t prefix_count = stored;
    size_t bridge_count = emit_bridge(dir, prefix_p, best_cycle);
    stored += bridge_count;

    uint8_t input[1600];
    memcpy(input, best_cycle, sizeof(input));
    size_t body_count[8];
    for (int b = 0; b < 8; b++) {
        build_body_graph(input, &best_chain[b], body_nodes, out_p);
        int expected = current_cost(input, &best_chain[b]);
        int in_base = (b & 1) ? 1856 : 256;
        int out_base = (b & 1) ? 256 : 1856;
        char name[8];
        snprintf(name, sizeof(name), "B%d", b + 1);
        body_count[b] = emit_block(dir, name, body_nodes, 1600, 1600, in_base,
                                   out_base, &highest);
        if ((int)body_count[b] != expected) fail("body count differs from polarity ledger");
        stored += body_count[b];
        memcpy(input, out_p, sizeof(input));
    }
    if (memcmp(input, best_cycle, sizeof(input))) fail("eight-body polarity cycle does not close");

    uint8_t round22_p[1600];
    targets_to_state(best_chain[4].target, round22_p);
    build_end_graph(round22_p, end_nodes, end_p);
    size_t end_count = emit_block(dir, "E", end_nodes, 256, 1600, 1856, 0, &highest);
    stored += end_count;

    int iota = 0;
    for (int r = 2; r <= 22; r++) iota += __builtin_popcountll(RC[r]);
    int driver = 2 * 21 + iota;
    long long executed = (long long)prefix_count + bridge_count + end_count + driver;
    for (int b = 0; b < 8; b++) executed += (long long)runs[b] * body_count[b];
    uint64_t pd[4] = {0, 0, 0, 0};
    for (int j = 0; j < 256; j++) pd[j >> 6] |= (uint64_t)end_p[j] << (j & 63);
    char pd_path[4096];
    if (snprintf(pd_path, sizeof(pd_path), "%s/PD.bin", dir) >= (int)sizeof(pd_path))
        fail("PD path too long");
    FILE *pd_file = fopen(pd_path, "wb");
    if (!pd_file || fwrite(pd, sizeof(pd), 1, pd_file) != 1 || fclose(pd_file))
        fail("cannot write PD.bin");

    printf("stored-block-instructions %zu\n", stored);
    printf("iota-xors %d\n", iota);
    printf("driver %d\n", driver);
    printf("TOTAL %lld\n", executed);
    printf("highest-register+1 %d\n", highest);
    printf("PD %016" PRIx64 " %016" PRIx64 " %016" PRIx64 " %016" PRIx64 "\n",
           pd[0], pd[1], pd[2], pd[3]);
    printf("optimizer iterations-per-body %d trials %d\n", iterations, trials);
    return highest > 4096 ? 2 : 0;
}
```

## Appendix: Freestanding measured runtime

```c
#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct { int fd; } MiniFile;
static MiniFile stderr_storage = {2};
FILE *stderr = (FILE *)&stderr_storage;
static int mini_errno;

int *__errno_location(void) { return &mini_errno; }

static long call1(long n, long a) {
    long r;
    __asm__ volatile("syscall" : "=a"(r) : "a"(n), "D"(a) : "rcx", "r11", "memory");
    return r;
}

static long call3(long n, long a, long b, long c) {
    long r;
    register long r10 __asm__("r10") = c;
    __asm__ volatile("syscall" : "=a"(r) : "a"(n), "D"(a), "S"(b), "d"(r10)
                     : "rcx", "r11", "memory");
    return r;
}

static long call4(long n, long a, long b, long c, long d) {
    long r;
    register long r10 __asm__("r10") = d;
    __asm__ volatile("syscall" : "=a"(r) : "a"(n), "D"(a), "S"(b), "d"(c), "r"(r10)
                     : "rcx", "r11", "memory");
    return r;
}

void exit(int status) {
    call1(60, status);
    for (;;) {}
}

size_t strlen(const char *s) {
    const char *p = s;
    while (*p) p++;
    return (size_t)(p - s);
}

void *memset(void *dst, int c, size_t n) {
    unsigned char *p = dst;
    while (n--) *p++ = (unsigned char)c;
    return dst;
}

void *memcpy(void *dst, const void *src, size_t n) {
    unsigned char *d = dst;
    const unsigned char *s = src;
    while (n--) *d++ = *s++;
    return dst;
}

int memcmp(const void *a, const void *b, size_t n) {
    const unsigned char *x = a, *y = b;
    while (n--) if (*x++ != *y++) return x[-1] < y[-1] ? -1 : 1;
    return 0;
}

int atoi(const char *s) {
    int sign = 1, value = 0;
    if (*s == '-') { sign = -1; s++; }
    while (*s >= '0' && *s <= '9') value = value * 10 + (*s++ - '0');
    return sign * value;
}

long strtol(const char *s, char **end, int base) {
    long sign = 1, value = 0;
    if (*s == '-') { sign = -1; s++; }
    if (base == 0) base = 10;
    while (*s >= '0' && *s <= '9' && *s - '0' < base) value = value * base + (*s++ - '0');
    if (end) *end = (char *)s;
    return sign * value;
}

char *strerror(int error) {
    (void)error;
    return "system call failed";
}

#ifndef HEAP_BYTES
#define HEAP_BYTES (160 * 1024)
#endif
typedef struct Block { size_t size; struct Block *next; int free; } Block;
static union { max_align_t align; unsigned char bytes[HEAP_BYTES]; } heap_store;
static Block *heap_head;

static void heap_init(void) {
    heap_head = (Block *)heap_store.bytes;
    heap_head->size = HEAP_BYTES - sizeof(Block);
    heap_head->next = NULL;
    heap_head->free = 1;
}

void *malloc(size_t size) {
    if (!heap_head) heap_init();
    size = (size + 15) & ~(size_t)15;
    for (Block *b = heap_head; b; b = b->next) if (b->free && b->size >= size) {
        if (b->size >= size + sizeof(Block) + 16) {
            Block *next = (Block *)((unsigned char *)(b + 1) + size);
            next->size = b->size - size - sizeof(Block);
            next->next = b->next;
            next->free = 1;
            b->next = next;
            b->size = size;
        }
        b->free = 0;
        return b + 1;
    }
    return NULL;
}

void *calloc(size_t count, size_t size) {
    if (count && size > (size_t)-1 / count) return NULL;
    size_t total = count * size;
    void *p = malloc(total);
    if (p) memset(p, 0, total);
    return p;
}

void free(void *ptr) {
    if (!ptr) return;
    Block *b = (Block *)ptr - 1;
    b->free = 1;
    for (Block *p = heap_head; p && p->next;) {
        if (p->free && p->next->free) {
            p->size += sizeof(Block) + p->next->size;
            p->next = p->next->next;
        } else {
            p = p->next;
        }
    }
}

FILE *fopen(const char *path, const char *mode) {
    static MiniFile slot;
    (void)mode;
    long fd = call4(257, -100, (long)path, 577, 0644);
    if (fd < 0) { mini_errno = (int)-fd; return NULL; }
    slot.fd = (int)fd;
    return (FILE *)&slot;
}

size_t fwrite(const void *ptr, size_t size, size_t count, FILE *stream) {
    size_t total = size * count, done = 0;
    int fd = ((MiniFile *)stream)->fd;
    while (done < total) {
        long n = call3(1, fd, (long)((const unsigned char *)ptr + done), total - done);
        if (n <= 0) return done / size;
        done += (size_t)n;
    }
    return count;
}

int fclose(FILE *stream) {
    return call1(3, ((MiniFile *)stream)->fd) < 0 ? -1 : 0;
}

typedef struct { char *dst; size_t cap, used; } Sink;

static void putc_sink(Sink *s, char c) {
    if (s->used + 1 < s->cap) s->dst[s->used] = c;
    s->used++;
}

static void puts_sink(Sink *s, const char *text) {
    while (*text) putc_sink(s, *text++);
}

static void number_sink(Sink *s, uint64_t value, unsigned base, int width, int zero, int negative) {
    char digits[32];
    int n = 0;
    do {
        unsigned d = (unsigned)(value % base);
        digits[n++] = (char)(d < 10 ? '0' + d : 'a' + d - 10);
        value /= base;
    } while (value);
    int total = n + negative;
    while (total < width) { putc_sink(s, zero ? '0' : ' '); total++; }
    if (negative) putc_sink(s, '-');
    while (n) putc_sink(s, digits[--n]);
}

static int format(char *dst, size_t cap, const char *fmt, va_list ap) {
    Sink s = {dst, cap, 0};
    while (*fmt) {
        if (*fmt != '%') { putc_sink(&s, *fmt++); continue; }
        fmt++;
        int zero = 0, width = 0, long_count = 0, is_size = 0;
        if (*fmt == '0') { zero = 1; fmt++; }
        while (*fmt >= '0' && *fmt <= '9') width = width * 10 + (*fmt++ - '0');
        if (*fmt == 'z') { is_size = 1; fmt++; }
        else while (*fmt == 'l') { long_count++; fmt++; }
        char kind = *fmt++;
        if (kind == '%') putc_sink(&s, '%');
        else if (kind == 's') puts_sink(&s, va_arg(ap, const char *));
        else if (kind == 'd') {
            int64_t v = long_count >= 2 ? va_arg(ap, long long) : va_arg(ap, int);
            number_sink(&s, v < 0 ? (uint64_t)(-v) : (uint64_t)v, 10, width, zero, v < 0);
        } else if (kind == 'u') {
            uint64_t v = is_size ? va_arg(ap, size_t) : long_count ? va_arg(ap, unsigned long) : va_arg(ap, unsigned);
            number_sink(&s, v, 10, width, zero, 0);
        } else if (kind == 'x') {
            uint64_t v = is_size ? va_arg(ap, size_t) : long_count ? va_arg(ap, unsigned long) : va_arg(ap, unsigned);
            number_sink(&s, v, 16, width, zero, 0);
        }
    }
    if (cap) dst[s.used < cap ? s.used : cap - 1] = 0;
    return (int)s.used;
}

int vsnprintf(char *dst, size_t cap, const char *fmt, va_list ap) {
    return format(dst, cap, fmt, ap);
}

int snprintf(char *dst, size_t cap, const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    int n = format(dst, cap, fmt, ap);
    va_end(ap);
    return n;
}

static int write_format(int fd, const char *fmt, va_list ap) {
    char buffer[4096];
    int n = format(buffer, sizeof(buffer), fmt, ap);
    size_t bytes = (size_t)n < sizeof(buffer) ? (size_t)n : sizeof(buffer) - 1;
    return call3(1, fd, (long)buffer, bytes) == (long)bytes ? n : -1;
}

int printf(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    int n = write_format(1, fmt, ap);
    va_end(ap);
    return n;
}

int fprintf(FILE *stream, const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    int n = write_format(((MiniFile *)stream)->fd, fmt, ap);
    va_end(ap);
    return n;
}

int main(int argc, char **argv);

__attribute__((naked, noreturn)) void _start(void) {
    __asm__ volatile(
        "xor %rbp,%rbp\n"
        "mov (%rsp),%rdi\n"
        "lea 8(%rsp),%rsi\n"
        "andq $-16,%rsp\n"
        "call main\n"
        "mov %eax,%edi\n"
        "mov $60,%eax\n"
        "syscall\n"
        "ud2\n"
    );
}
```

## Appendix: Independent scalar and emitted-program checker

```c
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { NREG = 4096 };

typedef struct { uint64_t w[4]; } Word256;
typedef struct { uint8_t op; uint16_t d, a, b; } Insn;
typedef struct { Insn *p; size_t n; int mix[4]; int high; } Program;

static Word256 regs[NREG];
static uint64_t pd[4];

static const uint64_t RC[24] = {
    UINT64_C(0x0000000000000001), UINT64_C(0x0000000000008082),
    UINT64_C(0x800000000000808a), UINT64_C(0x8000000080008000),
    UINT64_C(0x000000000000808b), UINT64_C(0x0000000080000001),
    UINT64_C(0x8000000080008081), UINT64_C(0x8000000000008009),
    UINT64_C(0x000000000000008a), UINT64_C(0x0000000000000088),
    UINT64_C(0x0000000080008009), UINT64_C(0x000000008000000a),
    UINT64_C(0x000000008000808b), UINT64_C(0x800000000000008b),
    UINT64_C(0x8000000000008089), UINT64_C(0x8000000000008003),
    UINT64_C(0x8000000000008002), UINT64_C(0x8000000000000080),
    UINT64_C(0x000000000000800a), UINT64_C(0x800000008000000a),
    UINT64_C(0x8000000080008081), UINT64_C(0x8000000000008080),
    UINT64_C(0x0000000080000001), UINT64_C(0x8000000080008008),
};

static const int RHO[25] = {
    0, 1, 62, 28, 27, 36, 44, 6, 55, 20, 3, 10, 43,
    25, 39, 41, 45, 15, 21, 8, 18, 2, 61, 56, 14,
};

static const uint64_t KL[25] = {
    UINT64_C(0x0000000000000000), UINT64_C(0x0000000000000000),
    UINT64_C(0x2d58eceb83b21614), UINT64_C(0x0000000000000000),
    UINT64_C(0x0000000000000000), UINT64_C(0xffffffffffffffff),
    UINT64_C(0x0000000000000000), UINT64_C(0x0000000000000000),
    UINT64_C(0x0000000000000000), UINT64_C(0x0000000000000000),
    UINT64_C(0xffffffffffffffff), UINT64_C(0x8b563b3ae0ec8583),
    UINT64_C(0x0000000000000000), UINT64_C(0x85ab1d9d707642c2),
    UINT64_C(0xe953898a3e26f4f5), UINT64_C(0xffffffffffffffff),
    UINT64_C(0x8000000000000006), 0, 0, 0, 0, 0, 0, 0, 0,
};

static void fail(const char *msg) {
    fprintf(stderr, "check_combined: %s\n", msg);
    exit(1);
}

static uint64_t rotl64(uint64_t x, int n) {
    return n ? (x << n) | (x >> (64 - n)) : x;
}

static void keccak_prefix(uint64_t lanes[25], int rounds) {
    for (int r = 0; r < rounds; r++) {
        uint64_t parity[5], theta[5], moved[25];
        for (int x = 0; x < 5; x++)
            parity[x] = lanes[x] ^ lanes[x + 5] ^ lanes[x + 10] ^
                        lanes[x + 15] ^ lanes[x + 20];
        for (int x = 0; x < 5; x++)
            theta[x] = parity[(x + 4) % 5] ^ rotl64(parity[(x + 1) % 5], 1);
        for (int y = 0; y < 5; y++) for (int x = 0; x < 5; x++) {
            int i = x + 5 * y;
            moved[y + 5 * ((2 * x + 3 * y) % 5)] = rotl64(lanes[i] ^ theta[x], RHO[i]);
        }
        for (int y = 0; y < 5; y++) for (int x = 0; x < 5; x++)
            lanes[x + 5 * y] = moved[x + 5 * y] ^
                ((~moved[(x + 1) % 5 + 5 * y]) & moved[(x + 2) % 5 + 5 * y]);
        lanes[0] ^= RC[r];
    }
}

static uint64_t load64_le(const uint8_t p[8]) {
    uint64_t x = 0;
    for (int i = 0; i < 8; i++) x |= (uint64_t)p[i] << (8 * i);
    return x;
}

static void store64_le(uint8_t p[8], uint64_t x) {
    for (int i = 0; i < 8; i++) p[i] = (uint8_t)(x >> (8 * i));
}

static void sha3_256_ref(const uint8_t *msg, size_t len, uint8_t out[32]) {
    size_t padded_len = ((len + 1 + 135) / 136) * 136;
    uint8_t *padded = calloc(padded_len, 1);
    uint64_t lanes[25] = {0};
    if (!padded) fail("SHA3 allocation failed");
    memcpy(padded, msg, len);
    padded[len] = 0x06;
    padded[padded_len - 1] |= 0x80;
    for (size_t off = 0; off < padded_len; off += 136) {
        for (int i = 0; i < 17; i++) lanes[i] ^= load64_le(&padded[off + 8 * i]);
        keccak_prefix(lanes, 24);
    }
    for (int i = 0; i < 4; i++) store64_le(&out[8 * i], lanes[i]);
    free(padded);
}

static void reference_kats(void) {
    static const uint8_t abc[32] = {
        0x3a, 0x98, 0x5d, 0xa7, 0x4f, 0xe2, 0x25, 0xb2,
        0x04, 0x5c, 0x17, 0x2d, 0x6b, 0xd3, 0x90, 0xbd,
        0x85, 0x5f, 0x08, 0x6e, 0x3e, 0x9d, 0x52, 0x5b,
        0x46, 0xbf, 0xe2, 0x45, 0x11, 0x43, 0x15, 0x32,
    };
    static const uint8_t empty[32] = {
        0xa7, 0xff, 0xc6, 0xf8, 0xbf, 0x1e, 0xd7, 0x66,
        0x51, 0xc1, 0x47, 0x56, 0xa0, 0x61, 0xd6, 0x62,
        0xf5, 0x80, 0xff, 0x4d, 0xe4, 0x3b, 0x49, 0xfa,
        0x82, 0xd8, 0x0a, 0x4b, 0x80, 0xf8, 0x43, 0x4a,
    };
    uint8_t got[32];
    sha3_256_ref((const uint8_t *)"abc", 3, got);
    if (memcmp(got, abc, 32)) fail("SHA3-256 abc KAT failed");
    sha3_256_ref((const uint8_t *)"", 0, got);
    if (memcmp(got, empty, 32)) fail("SHA3-256 empty KAT failed");
}

static void f_reference(const uint64_t u[4], uint64_t out[4]) {
    uint64_t lanes[25];
    memcpy(lanes, KL, sizeof(lanes));
    lanes[1] = u[0];
    lanes[6] = u[1];
    lanes[11] = u[0] ^ u[1] ^ KL[11];
    lanes[4] = u[2];
    lanes[9] = u[3];
    lanes[14] = u[2] ^ u[3] ^ KL[14];
    keccak_prefix(lanes, 24);
    for (int i = 0; i < 4; i++) out[i] = lanes[i] ^ pd[i];
}

static Program read_program(const char *dir, const char *name) {
    char path[4096];
    if (snprintf(path, sizeof(path), "%s/%s.bin", dir, name) >= (int)sizeof(path))
        fail("program path too long");
    FILE *f = fopen(path, "rb");
    if (!f) {
        fprintf(stderr, "check_combined: fopen %s: %s\n", path, strerror(errno));
        exit(1);
    }
    if (fseek(f, 0, SEEK_END) || ftell(f) < 0) fail("cannot size program");
    long bytes = ftell(f);
    if (bytes % 5) fail("program length is not a multiple of five bytes");
    if (fseek(f, 0, SEEK_SET)) fail("cannot rewind program");
    Program result = {0};
    result.n = (size_t)bytes / 5;
    result.p = malloc((result.n ? result.n : 1) * sizeof(*result.p));
    if (!result.p) fail("program allocation failed");
    for (size_t i = 0; i < result.n; i++) {
        uint8_t b[5];
        if (fread(b, 1, 5, f) != 5) fail("short program read");
        uint64_t w = 0;
        for (int j = 0; j < 5; j++) w |= (uint64_t)b[j] << (8 * j);
        Insn in = {(uint8_t)(w & 7), (uint16_t)((w >> 3) & 4095),
                   (uint16_t)((w >> 15) & 4095), (uint16_t)((w >> 27) & 4095)};
        if (in.op > 3 || in.d >= NREG || in.a >= NREG || (in.op != 3 && in.b >= NREG))
            fail("invalid encoded instruction");
        result.p[i] = in;
        result.mix[in.op]++;
        int high = in.d > in.a ? in.d : in.a;
        if (in.op != 3 && in.b > high) high = in.b;
        if (high + 1 > result.high) result.high = high + 1;
    }
    if (fclose(f)) fail("program close failed");
    return result;
}

static void verify_packed_program(const char *dir, const char *name, const Program *program) {
    char path[4096];
    if (snprintf(path, sizeof(path), "%s/%s.p39", dir, name) >= (int)sizeof(path))
        fail("packed program path too long");
    FILE *f = fopen(path, "rb");
    if (!f) fail("cannot open packed program");
    size_t bytes = (39 * program->n + 7) / 8;
    uint8_t *packed = calloc(bytes ? bytes : 1, 1);
    if (!packed || (bytes && fread(packed, 1, bytes, f) != bytes) || fgetc(f) != EOF || fclose(f))
        fail("cannot read packed program");
    for (size_t i = 0; i < program->n; i++) {
        size_t bit = 39 * i;
        uint64_t w = 0;
        for (int k = 0; k < 39; k++)
            w |= (uint64_t)((packed[(bit + (size_t)k) >> 3] >> ((bit + (size_t)k) & 7)) & 1) << k;
        uint64_t expected = (uint64_t)program->p[i].op | (uint64_t)program->p[i].d << 3 |
            (uint64_t)program->p[i].a << 15 | (uint64_t)program->p[i].b << 27;
        if (w != expected) fail("packed program differs from five-byte development encoding");
    }
    free(packed);
}

static void read_pd(const char *dir) {
    char path[4096];
    if (snprintf(path, sizeof(path), "%s/PD.bin", dir) >= (int)sizeof(path))
        fail("PD path too long");
    FILE *f = fopen(path, "rb");
    if (!f || fread(pd, sizeof(pd), 1, f) != 1 || fgetc(f) != EOF || fclose(f))
        fail("cannot read PD.bin");
}

static void execute(const Program *prog) {
    for (size_t i = 0; i < prog->n; i++) {
        Word256 t;
        for (int k = 0; k < 4; k++) {
            uint64_t a = regs[prog->p[i].a].w[k];
            uint64_t b = regs[prog->p[i].b].w[k];
            t.w[k] = prog->p[i].op == 0 ? a ^ b :
                     prog->p[i].op == 1 ? a & b :
                     prog->p[i].op == 2 ? a | b : ~a;
        }
        regs[prog->p[i].d] = t;
    }
}

static void apply_iota(int round, int output_base) {
    for (int z = 0; z < 64; z++) if ((RC[round] >> z) & 1)
        for (int k = 0; k < 4; k++) regs[output_base + z].w[k] ^= UINT64_MAX;
}

static uint64_t rng_state = UINT64_C(0xd1b54a32d192ed03);

static uint64_t random64(void) {
    uint64_t z = (rng_state += UINT64_C(0x9e3779b97f4a7c15));
    z = (z ^ (z >> 30)) * UINT64_C(0xbf58476d1ce4e5b9);
    z = (z ^ (z >> 27)) * UINT64_C(0x94d049bb133111eb);
    return z ^ (z >> 31);
}

static void transpose_inputs(uint64_t points[256][4]) {
    for (int j = 0; j < 256; j++) {
        Word256 p = {{0, 0, 0, 0}};
        for (int t = 0; t < 256; t++)
            p.w[t >> 6] |= ((points[t][j >> 6] >> (j & 63)) & 1) << (t & 63);
        regs[j] = p;
    }
}

static void extract_point(int trail, uint64_t out[4]) {
    memset(out, 0, 4 * sizeof(*out));
    for (int j = 0; j < 256; j++)
        out[j >> 6] |= ((regs[j].w[trail >> 6] >> (trail & 63)) & 1) << (j & 63);
}

static void check_complete_messages(const char *output_path) {
    uint8_t message[512], digest[32];
    FILE *output = output_path ? fopen(output_path, "wb") : NULL;
    if (output_path && !output) fail("cannot create complete-message digest file");
    for (size_t len = 0; len <= 511; len++) {
        for (size_t i = 0; i < len; i++) message[i] = (uint8_t)(i * 149 + len * 37);
        sha3_256_ref(message, len, digest);
        uint64_t fold = 0;
        for (int i = 0; i < 32; i++) fold |= digest[i];
        if (!fold && len != 0) fail("impossible all-zero digest sentinel");
        if (output && fwrite(digest, 1, 32, output) != 32) fail("digest-file write failed");
    }
    if (output && fclose(output)) fail("digest-file close failed");
}

int main(int argc, char **argv) {
    const char *dir = argc > 1 ? argv[1] : "out";
    int batches = argc > 2 ? atoi(argv[2]) : 64;
    int chain_steps = argc > 3 ? atoi(argv[3]) : 4;
    if (batches < 1 || chain_steps < 1) fail("batch and chain counts must be positive");
    reference_kats();
    check_complete_messages(argc > 4 ? argv[4] : NULL);
    read_pd(dir);
    const char *names[11] = {"P", "G", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "E"};
    Program p[11];
    for (int i = 0; i < 11; i++) {
        p[i] = read_program(dir, names[i]);
        verify_packed_program(dir, names[i], &p[i]);
    }

    int iota = 0;
    for (int r = 2; r <= 22; r++) iota += __builtin_popcountll(RC[r]);
    static const int runs[8] = {3, 3, 3, 3, 3, 2, 2, 2};
    uint64_t step_ops = p[0].n + p[1].n + p[10].n + 2 * 21 + iota;
    for (int i = 0; i < 8; i++) step_ops += (uint64_t)runs[i] * p[i + 2].n;

    uint64_t points[256][4], checked = 0, mismatches = 0;
    for (int batch = 0; batch < batches; batch++) {
        memset(regs, 0, sizeof(regs));
        for (int t = 0; t < 256; t++) for (int k = 0; k < 4; k++) points[t][k] = random64();
        transpose_inputs(points);
        for (int step = 0; step < chain_steps; step++) {
            execute(&p[0]);
            execute(&p[1]);
            for (int r = 2; r <= 22; r++) {
                int b = (r - 2) & 7;
                execute(&p[b + 2]);
                apply_iota(r, (b & 1) ? 256 : 1856);
            }
            execute(&p[10]);
            for (int t = 0; t < 256; t++) {
                uint64_t expected[4], actual[4];
                f_reference(points[t], expected);
                extract_point(t, actual);
                if (memcmp(expected, actual, sizeof(expected))) {
                    if (mismatches < 4)
                        fprintf(stderr, "mismatch batch %d step %d trail %d\n", batch, step, t);
                    mismatches++;
                }
                memcpy(points[t], expected, sizeof(expected));
                checked++;
            }
        }
    }

    printf("reference: SHA3-256 empty and abc KATs passed; complete padding exercised at lengths 0..511\n");
    for (int i = 0; i < 11; i++)
        printf("program %s: %zu instructions; XOR %d AND %d OR %d NOT %d; high register %d\n",
               names[i], p[i].n, p[i].mix[0], p[i].mix[1], p[i].mix[2], p[i].mix[3], p[i].high);
    printf("step: %" PRIu64 " charged operations including 42 calls/returns and %d iota XORs\n",
           step_ops, iota);
    printf("cross-check: %" PRIu64 " chained F evaluations, %" PRIu64 " mismatches\n",
           checked, mismatches);
    for (int i = 0; i < 11; i++) free(p[i].p);
    return mismatches ? 2 : 0;
}
```

## Appendix: Exact incumbent reproduction and combined ledger

```python
#!/usr/bin/env python3
"""Independent exact ledger for the r24 combined step and incumbent reproduction."""

from decimal import Decimal as D, ROUND_CEILING, getcontext
from fractions import Fraction
import math

getcontext().prec = 80

UNIT = 6504
L = 256
N_RANGE = D(2) ** 256
WORD_BYTES = 32
MARGIN = 4096

OTHER_INSTRUCTIONS = 2715
HIT = 126
DP_FIXED = 1115
PROBE_WORD = 35
RESTART = 1289
RESTART_HALT = 3
DEADLINE_FINAL = 1
MEASURE_ITER = 6541
REPLAY_ITER = 13079
REPLAY_CONST = 79

RECORD_ID_BITS = 17
RECORD_KEY_BITS = 46
MAX_TRAILS = 1 << RECORD_ID_BITS


def theta_of(dplo, dk, dt):
    return D(dt) / D(2) ** (256 - dplo + dk)


def success(tb, theta, width, bins, trails, key_bits, parts=False):
    replay_cap = bins * width
    log_q = (1 - theta).ln()
    mean_dp = D(L * tb) * theta
    available = trails - L
    if available <= mean_dp:
        return (D(-1), None) if parts else D(-1)
    birthday = D(0)
    q_previous = D(1)
    for j in range(1, bins + 1):
        q_current = (width * j * log_q).exp()
        evaluations = L * (tb - j * width)
        if evaluations > 1:
            exponent = -D(evaluations) * (evaluations - 1) / (2 * N_RANGE)
            birthday += (q_previous - q_current) * (1 - exponent.exp())
        q_previous = q_current
    evaluations = L * tb
    f6 = D(evaluations) * (evaluations - 1) / N_RANGE
    f6 *= (replay_cap * log_q).exp() * (1 + replay_cap * theta)
    f2 = (-mean_dp + available * (1 + (mean_dp / available).ln())).exp()
    f3 = D(trails) / (theta * theta * N_RANGE)
    f4 = D(2) ** -90 + D(trails) ** 2 * D(2) ** -(key_bits + 1)
    bound = birthday - (f6 + f2 + f3 + f4 + D(2) ** -1000 + D(2) ** -60)
    return (bound, (f6, f2, f3, f4)) if parts else bound


def least_tb(theta, width, bins, trails, key_bits, granularity, low, high):
    low = low // granularity * granularity
    high = -(-high // granularity) * granularity
    if success(low, theta, width, bins, trails, key_bits) >= D("0.39"):
        raise ValueError("lower exact-search endpoint already succeeds")
    if success(high, theta, width, bins, trails, key_bits) < D("0.39"):
        raise ValueError("upper exact-search endpoint does not succeed")
    while high - low > granularity:
        middle = (low + high) // 2 // granularity * granularity
        if success(middle, theta, width, bins, trails, key_bits) >= D("0.39"):
            high = middle
        else:
            low = middle
    return high


def float_success(tb, theta, replay_cap, trails, key_bits, bins=3000):
    width = replay_cap / bins
    log_q = math.log1p(-theta)
    mean_dp = L * tb * theta
    available = trails - L
    if available <= mean_dp:
        return -1.0
    birthday = 0.0
    q_previous = 1.0
    for j in range(1, bins + 1):
        q_current = math.exp(width * j * log_q)
        evaluations = L * (tb - j * width)
        if evaluations > 1:
            birthday += (q_previous - q_current) * -math.expm1(
                -evaluations * evaluations / 2.0**257
            )
        q_previous = q_current
    evaluations = L * tb
    f6 = evaluations * evaluations / 2.0**256
    f6 *= math.exp(replay_cap * log_q) * (1 + replay_cap * theta)
    f2 = math.exp(-mean_dp + available * (1 + math.log(mean_dp / available)))
    f3 = trails / (theta * theta * 2.0**256)
    f4 = trails * trails * 2.0 ** -(key_bits + 1)
    return birthday - (f6 + f2 + f3 + f4)


def choose_parameters(trails, bstep, key_bits):
    best = None
    h0 = 128 - math.log2(trails)
    for delta_index in range(-5, 25):
        h = h0 + 0.02 * delta_index
        theta = 2.0 ** -h
        for kappa in (8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5):
            replay_cap = kappa / theta
            low, high = 2.0**119.9, 2.0**120.1
            if float_success(high, theta, replay_cap, trails, key_bits) < 0.39:
                continue
            for _ in range(28):
                middle = (low + high) / 2
                if float_success(middle, theta, replay_cap, trails, key_bits) >= 0.39:
                    high = middle
                else:
                    low = middle
            model = math.log2((high * bstep + (MEASURE_ITER + REPLAY_ITER) * replay_cap) / UNIT)
            if best is None or model < best[0]:
                best = (model, h, kappa, high)
    if best is None:
        raise RuntimeError("parameter scan found no feasible point")
    model, h, kappa, approximate_tb = best
    hf = math.floor(h)
    dk = 10
    dt = round(2**dk * 2 ** (hf - h))
    dt = max(2 ** (dk - 1), min(dt, 2**dk - 1))
    dplo = 256 - hf
    theta = theta_of(dplo, dk, dt)
    width = 2 ** (hf - 12)
    bins = round(kappa / float(theta) / width)
    granularity = 2 ** (hf - 20)
    tb = least_tb(
        theta,
        width,
        bins,
        trails,
        key_bits,
        granularity,
        int(approximate_tb * 0.995),
        int(approximate_tb * 1.005),
    )
    return {
        "model": model,
        "HF": hf,
        "DPLO": dplo,
        "DK": dk,
        "DT": dt,
        "W": width,
        "J": bins,
        "LRC": bins * width,
        "Tb": tb,
        "granularity": granularity,
    }


def setup_cost(table_words):
    if table_words % 8:
        raise ValueError("table word count must be divisible by eight")
    return 330_248 + 11 * table_words // 8


def resources(step, stored_blocks, highest_register, packed=True, max_trails=None):
    registers = highest_register + 11
    if packed:
        # Each independently callable block is byte aligned.  This list is the
        # final build's P, G, B1..B8 and E instruction counts.
        block_sizes = [4292, 0, 6679, 6633, 6645, 6652, 6643, 6664, 6722, 6910, 2492]
        assert sum(block_sizes) == stored_blocks
        straight_code = sum((39 * count + 7) // 8 for count in block_sizes)
        straight_code += (39 * (78 + 15) + 7) // 8
    else:
        straight_code = 5 * (stored_blocks + 78 + 15)
    driver_code = 29 * 32
    fixed = {
        "register file": registers * WORD_BYTES,
        "packed step blocks, iota and prefilter": straight_code + driver_code,
        "other code": OTHER_INSTRUCTIONS * 32,
        "walk state": 512 * WORD_BYTES,
        "data image": 16 * WORD_BYTES,
    }
    table_words = (2**20 - MARGIN - sum(fixed.values())) // 32 // 8 * 8
    while table_words + 100 >= 1 << table_words.bit_length():
        table_words -= 8
    if max_trails is not None:
        table_words = min(table_words, max_trails // 4)
    memory = sum(fixed.values()) + table_words * WORD_BYTES
    return fixed, table_words, 4 * table_words, memory


def check_record_layout(table_words, trails, key_bits, id_bits):
    if 1 + key_bits + id_bits != 64:
        raise AssertionError("record fields do not fill one 64-bit slot")
    if trails != 4 * table_words:
        raise AssertionError("four-record table capacity mismatch")
    if trails > 1 << id_bits:
        raise AssertionError("maximum trail identifier does not fit its field")
    maximum_id = trails - 1
    maximum_record = 1 | (((1 << key_bits) - 1) << 1) | (maximum_id << (1 + key_bits))
    if maximum_record >= 1 << 64 or maximum_record >> (1 + key_bits) != maximum_id:
        raise AssertionError("record packing crosses its 64-bit slot")
    overflow_record = 1 | ((1 << id_bits) << (1 + key_bits))
    if overflow_record < 1 << 64:
        raise AssertionError("first rejected identifier unexpectedly fits")


def exact_ledger(step, table_words, trails, key_bits, parameters, preprocessing):
    check_record_layout(table_words, trails, key_bits, 64 - 1 - key_bits)
    tb = parameters["Tb"]
    replay_cap = parameters["LRC"]
    bstep = step + 15 + 2 + 3
    replay = (MEASURE_ITER + REPLAY_ITER) * replay_cap + REPLAY_CONST
    delta = Fraction(1, 2**20)
    hit_cap = tb * (1 + delta) // 2**8 + 1 + replay_cap
    exponent = delta * delta * Fraction(tb, 2**8) / (2 + delta)
    if exponent <= 1000 * Fraction(6932, 10000):
        raise AssertionError("hit-counter tail is not below 2^-1000")
    rare = (
        (hit_cap + 1) * HIT
        + (trails - 255) * (DP_FIXED + PROBE_WORD * table_words)
        + (trails - 256) * (RESTART + 3)
        + RESTART_HALT
        + DEADLINE_FINAL
        + setup_cost(table_words)
    )
    total = tb * bstep + replay + rare + preprocessing
    theta = theta_of(parameters["DPLO"], parameters["DK"], parameters["DT"])
    bound, failures = success(tb, theta, parameters["W"], parameters["J"], trails, key_bits, True)
    lower = success(
        tb - parameters["granularity"], theta, parameters["W"], parameters["J"], trails, key_bits
    )
    if not (bound >= D("0.39") > lower):
        raise AssertionError("Tb is not the least successful grid point")
    scaled = int(
        (D(100000) * (D(total) / D(UNIT)).ln() / D(2).ln()).to_integral_value(
            rounding=ROUND_CEILING
        )
    )
    certificate_power = 100000
    total_power = total**certificate_power
    unit_power = UNIT**certificate_power
    if not (
        (unit_power << (scaled - 1)) < total_power
        <= (unit_power << scaled)
    ):
        raise AssertionError("five-decimal integer certificate failed")
    return {
        "BSTEP": bstep,
        "replay": replay,
        "hit_cap": hit_cap,
        "rare": rare,
        "preprocessing": preprocessing,
        "total": total,
        "success": bound,
        "previous_success": lower,
        "failures": failures,
        "scaled": scaled,
    }


def print_row(label, step, table_words, trails, memory, parameters, ledger):
    print(label)
    print("  rounds 24 unit", UNIT)
    print("  step", step, "BSTEP", ledger["BSTEP"])
    print("  table words", table_words, "trails", trails, "memory", memory, "margin", 2**20 - memory)
    print(
        "  DP",
        parameters["DT"],
        "x 2^-",
        256 - parameters["DPLO"] + parameters["DK"],
        "LRC",
        parameters["LRC"],
    )
    print("  Tb", parameters["Tb"], "evaluations / 2^128", float(D(256 * parameters["Tb"]) / D(2) ** 128))
    print("  success", ledger["success"], "previous", ledger["previous_success"])
    print("  failures", *(f"{x:.3E}" for x in ledger["failures"]))
    print("  main", parameters["Tb"] * ledger["BSTEP"])
    print("  replay", ledger["replay"])
    print("  rare", ledger["rare"])
    print("  preprocessing", ledger["preprocessing"])
    print("  N", ledger["total"])
    scaled = ledger["scaled"]
    print(f"  time_log2 {scaled // 100000}.{scaled % 100000:05d}")


def reproduce_incumbent():
    params = {
        "HF": 112,
        "DPLO": 144,
        "DK": 10,
        "DT": 936,
        "W": 1267650600228229401496703205376,
        "J": 47051,
        "LRC": 59644228391338421569821382516146176,
        "Tb": 1328093265282585793353186825841147904,
        "granularity": 2**92,
    }
    ledger = exact_ledger(147303, 16280, 65120, 47, params, 93893306875904)
    expected = 196837072726569150731717239455155002654091
    if ledger["total"] != expected or ledger["scaled"] != 12450895:
        raise AssertionError("incumbent reproduction failed")
    print_row("incumbent reproduction", 147303, 16280, 65120, 1042946, params, ledger)


def combined():
    fixed, table_words, trails, memory = resources(
        147252, 60332, 3465, packed=True, max_trails=MAX_TRAILS
    )
    params = choose_parameters(trails, 147252 + 20, RECORD_KEY_BITS)
    # A deliberately loose charge for row-table construction, all three plan
    # trials, prefix greedy builds, graph emission, packing and parameter scan.
    preprocessing = 2**48
    ledger = exact_ledger(
        147252, table_words, trails, RECORD_KEY_BITS, params, preprocessing
    )
    print("combined fixed memory")
    for name, amount in fixed.items():
        print(f"  {amount:9d} {name}")
    print_row("combined", 147252, table_words, trails, memory, params, ledger)
    return ledger


if __name__ == "__main__":
    reproduce_incumbent()
    combined()
```

## Appendix: Compiler stack-usage and call-graph audit

```python
#!/usr/bin/env python3
"""Build the freestanding generator and sum its longest compiler-reported call chain."""

from pathlib import Path
import re
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
FLAGS = [
    "-O2", "-march=native", "-fno-pie", "-DPACKED_ONLY", "-ffreestanding",
    "-fno-stack-protector", "-U_FORTIFY_SOURCE", "-D_FORTIFY_SOURCE=0",
    "-fstack-usage", "-nostdlib", "-static", "-no-pie", "-Wl,-e,_start",
]


def normalized(name):
    return re.sub(r"((?:\.isra|\.constprop))\.\d+$", r"\1", name)


with tempfile.TemporaryDirectory(prefix="hashsmash-stack-") as temporary:
    root = Path(temporary)
    binary = root / "gen_combined_mini"
    command = [
        "gcc", *FLAGS, str(HERE / "gen_combined.c"), str(HERE / "mini_runtime.c"),
        "-lgcc", "-o", str(binary),
    ]
    subprocess.run(command, check=True)
    frames = {}
    evidence = []
    for path in sorted(root.glob("*.su")):
        for line in path.read_text().splitlines():
            location, amount, qualifier = line.split("\t")
            name = location.rsplit(":", 1)[1]
            frames[normalized(name)] = int(amount)
            evidence.append((name, int(amount), qualifier))
    disassembly = subprocess.run(
        ["objdump", "-d", "--no-show-raw-insn", str(binary)],
        check=True, text=True, stdout=subprocess.PIPE,
    ).stdout
    graph = {name: set() for name in frames}
    current = None
    for line in disassembly.splitlines():
        label = re.match(r"^[0-9a-f]+ <([^>]+)>:$", line)
        if label:
            current = normalized(label.group(1))
            graph.setdefault(current, set())
            continue
        call = re.search(r"\bcall\s+[0-9a-f]+ <([^>]+)>", line)
        if current is not None and call:
            graph[current].add(normalized(call.group(1)))

    def longest(name, active=()):
        if name in active:
            raise RuntimeError(f"recursive call graph at {name}")
        children = [longest(child, active + (name,)) for child in graph.get(name, ())]
        suffix, path = max(children, default=(0, ()), key=lambda item: item[0])
        return frames.get(name, 0) + suffix, (name,) + path

    stack_bytes, call_chain = longest("_start")
    image_fields = subprocess.run(
        ["size", str(binary)], check=True, text=True, stdout=subprocess.PIPE,
    ).stdout.splitlines()[-1].split()
    text_bytes, data_bytes, bss_bytes, image_bytes = map(int, image_fields[:4])
    print("command:", " ".join(command[:-2] + ["-o", "gen_combined_mini"]))
    print(f"image: text={text_bytes} data={data_bytes} bss={bss_bytes} total={image_bytes}")
    print("largest frames:")
    for name, amount, qualifier in sorted(evidence, key=lambda item: item[1], reverse=True)[:12]:
        print(f"  {name}: {amount} bytes ({qualifier})")
    print(f"maximum call-chain stack: {stack_bytes} bytes")
    print("call chain:", " -> ".join(call_chain))
    print(f"retained outputs: 294155 bytes")
    print(f"generation total: {image_bytes + stack_bytes + 294155} bytes")
    print(f"margin below 2^20: {(1 << 20) - image_bytes - stack_bytes - 294155} bytes")
```
