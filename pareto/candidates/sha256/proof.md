# sha256-r64: an 86,375-record bit-sliced birthday walk

This package is a credited derivative of d22ae1b2-2368-460a-b6d4-1e5e37ceb735 and 95263e47-d61b-43a6-bb46-30ced2488280. It combines d22ae1b2's exact T2 pair-carry columns and index-layout table with 95263e47's constant-aware circuit selection. It also changes six fixed message offsets. The resulting kernel has 86,375 records, 56 fewer than d22ae1b2's 86,431.

The construction is generic collision search. It assumes that the fixed 64-step walk behaves like a random function in the precise sense of premise H1 below. It claims no differential, structural, or other weakness in SHA-256.

## 1. Target, message family, and collision relation

The target is `sha256-r64-prefix-v1`. SHA-256 processes both blocks of a padded 64-byte message, with all 64 steps and the standard feed-forward on each block.

Write a 256-bit point x as eight big-endian 32-bit words y0 through y7. Define the first message block by

```text
W0..W7 = 3e73281c 752d8ed2 ad19eff1 7250fceb
          d4095422 44fdb519 43f22c5b d8d6aac4
W8      = y0
W9      = y1
W10     = y2 + dbce7a42
W11     = y3 + aaf3823d
W12     = y4 + 8d41a28c
W13     = y5 + ff214e02
W14     = y6 + 6423f959
W15     = y7 + 18000000                 modulo 2^32.
```

The offset map is a bijection, so x differs from x' exactly when M(x) differs from M(x'). FIPS padding adds `80`, 55 zero bytes, and the 64-bit length 512. The padded input has two 64-byte blocks. The second block is fixed.

The prefix W0 through W7 is computed from the standard IV so that, after its eight steps,

```text
a1 = K9 - K8,  a2 = -K9,  a3 = ... = a8 = 0.
```

Thus steps 0 through 7 are constant and steps 8 and 9 cancel K8 and K9. The changed offsets affect only the bijective parametrization of W10 through W15. They do not affect the argument below.

Let a_i and e_i denote the working words after i steps of block 1. Let T1_i denote the T1 value that produces step i. Define f(x) as the following eight words, in this order:

```text
e61,
e62,
X  = e59 + (~e62 & e60) + W62,
T1_60,
Q  = T1_59 + Maj(a58,a57,a56),
a58,
a57,
Y  = e60 + W63.
```

This is walk B with its no-move output permutation. It is a bijection of the working state after step 63. The inverse first recovers

```text
a59 = Q + Sigma0(a58)
```

and then a60, a61, a62, T1_62, T1_63, and all eight final working words by the SHA-256 step equations. In particular,

```text
T1_62 = X + (e62 & e61) + Sigma1(e62) + K62.
```

The shipped `enc_invert` implements these equations directly.

The allocated program leaves some output planes complemented. Let q be that fixed 256-bit polarity mask and set g(x) = f(x) XOR q. In canonical big-endian hexadecimal,

```text
q = 83719e5368e5c5064d42d446b413f5fdd5bc79c27182e4541a52bdee6a59c788.
```

The emitted output registers already hold g, including q. No runtime XOR or mask is omitted. Since XOR by q and f are bijections of the final state, g(x) = g(y) implies equal block-1 working states. The feed-forward values are then equal, the fixed second block starts from the same chaining value, and the complete 256-bit digests are equal.

## 2. Search algorithm

The probability space contains one fresh uniform 256-bit word r. There is one attempt, with no restart or amplification. Trail t starts at `r + t mod 2^256` and repeatedly applies g.

A point is distinguished when its low 32 bits are zero and

```text
F = (x >> 32) mod 2^90 < Tp,    Tp = 1294.
```

The density is theta = 1294 / 2^122 and the mean trail length is

```text
L = 1/theta = 2658455991569831745807614120560689152 / 647.
```

The DP key has 46 bits: the 35 bits above bit 121, followed by the low 11 bits of F. Since F is below 1294, 11 bits suffice.

The program advances 256 trails together. One 256-bit machine word holds one bit position from all 256 trails. After each batch, 31 OR operations combine the low 32 physical output planes, followed by the charged test and branch. Those planes are the low bits of g, not unmasked bits of f, because q is already represented by the stored output polarities. Stage 1 therefore needs no extra mask operation. Each set lane is extracted and checked against Tp.

The table uses index layout. Slot t belongs to trail number t. A slot contains the 46-bit key and one written bit, for 47 bits total. It stores neither t nor the trail length. A key lookup scans the slots and compares the written bit and key. On a match, recovery pass 1 recomputes the stored trail's length from its start. The current trail length is already known. Recovery aligns the longer trail, then advances both trails until their next values agree. The predecessor pair is the collision.

At each multiple of S = 2^48 batches, a trail of age at least

```text
c = ceil(14 L) = 57524550049424489090118389007495593
```

is cut and restarted. The attempt halts on a third cut, a full table, a stage-1 budget overrun, an overlong recovery, a false key match that produces no pair, or after B batches.

The exact plan is

```text
tmax  = 84827 stored trails
slots = tmax + 256 starts + 2 cuts = 85085
B     = 1326205536293000000000000000000000000 batches
Q     = 256 B evaluations
e2max = 158096019779801368713378906314 stage-1 hits
capr  = c + 2^48 recovery calls per pass bound.
```

Pass 1 uses at most capr calls. Alignment plus the paired walk uses at most capr + 1 calls. The ledger charges `2 capr + 1` calls.

## 3. The 86,375-record kernel

The machine has 1,024 registers of 256 bits. The allocator uses 1,021 data registers and reserves three pointer registers. A body record has a one-byte opcode and three 10-bit register fields, for five bytes. It contains one register-to-register XOR, AND, OR, NOT, or move and no immediate. Every body record costs one word operation. Rotating a bit-sliced 32-bit word only renames planes and costs no record.

Signals are stored as a node and a free polarity bit. The two-input full adder uses five gates. For sums of three words, a carry is the pair (u,U), representing `1 if U else 2u`. Bit 0 uses the full adder. Bits 1 through 30 use T0, T1, or T2. T0 and T1 are

```text
T0: n5=z^U; n9=x^n5; s=y^n9; n8=U|(z^u);
    n11=!(x^y)&n9; u'=n5^n11; U'=n8^n11.

T1: w=y^U; n8=z^w; s=x^n8; n6=U|(y^u);
    u'=n6^w; U'=n6^(n8&(x^w)).
```

For stored-polarity masks 7, 8, 16, and 31, a T0 or T1 order can cost ten gates. The shipped `SYN` table contains exact nine-gate circuits for those masks and eight-gate circuits at bit 30, where u' is dead. Each circuit is checked on all 32 rows of `(x,y,z,u,U)`. Output polarity is free. These are the T2 circuits documented by d22ae1b2 and transcribed into the normative C emitter and its Python mirror.

The constant-aware selector compares equivalent first triples for every multiword sum and uses one-column carry lookahead. XOR cancellation is applied when a recent XOR and one of its operands meet again.

The six offsets in Section 1 are preprocessing output. Their deterministic search evaluates exactly 1,641 complete candidates: 64 endpoint placements, one initial coordinate point, three complete sweeps of 192 bits, and 1,000 perturbations from the fixed xorshift seed `6a09e667bb67ae85`. Bits are visited by increasing word and then increasing bit. A strict improvement replaces the incumbent, so ties retain the earlier candidate.

The search uses a count-only builder with an eight-probe CSE table and an eight-entry recent-gate ring. One complete candidate has at most two builder passes, 160 multiword sums, 64 first-triple masks per sum, 32 columns, 13 current-column forms, 13 lookahead forms, and 12 trial gates per form. Charging 1,024 word operations for each trial gate, including lookup, rollback, and bookkeeping, gives

```text
2 * 160 * 64 * 32 * 13 * 13 * 12 * 1024
= 1,360,967,761,920 < 2^41 operations.
```

One more copy of this bound covers the rest of the network, scoring, comparisons, loop control, and the deterministic generator. The package charges `2^48` operations per complete candidate, more than 128 times that doubled bound. Offset selection therefore costs exactly

```text
1641 * 2^48 = 461900436782186496 operations.
```

The frozen `AH[149]` and `CH[4470]` tables are also preprocessing output. The selector makes 149 multiword-reduction decisions and 4,470 column decisions. It tests at most 64 first-triple masks at each reduction and at most `13 * 13` current and lookahead forms at each column. With the same two passes, 32 columns, 12 trial gates, and 1,024-operation gate allowance, the complete selector search costs at most

```text
2 * 149 * 64 * 32 * 13 * 13 * 12 * 1024
+ 4470 * 13 * 13 * 12 * 1024
= 1,276,683,952,128 < 2^41 operations.
```

Again, a second copy covers all remaining builder and selection work. The ledger charges `2^48 = 281474976710656` operations. These structural envelopes replace the development tool's call counters. They cover every candidate allowed by the search loops and do not depend on replaying a hidden call trace.

T2 replacement, every selector choice, every fixed offset, and recent-XOR cancellation are exact Boolean or modular-arithmetic equivalences. They are not model assumptions. The shipped self-test exhausts all 32 input rows for every T2 circuit, runs the bounded Python mirror, compares every emitted record with the ordinary builder, checks the C source hash, the stream hash, and q, and compares the resulting program with the scalar SHA-256 walk. H1 remains the only score-critical premise.

The final emitted stream has

```text
68,038 XOR
10,925 AND
 7,412 OR
     0 NOT, move, set, load, or store
--------
86,375 records
```

The normative setup program is the freestanding C source embedded in `experiments/bssha.py` as `GEN_C`. `python3 experiments/bssha.py --gen-c` prints its exact 21,549 bytes. The source SHA-256 is `150d894317ba8a9f31e495a649dc1dd4f93f1bee96b12e41ee9f066e3580ac73`. Pass 0 counts node uses and records output nodes. Pass 1 rebuilds the same network, allocates registers online, and writes records directly to the final buffer. The builder has a 1,024-slot CSE table for gates on two input planes and an eight-gate ring for other recent gates. It enforces at most 900 occupied CSE slots, at most eight probes per lookup, at most 87,150 nodes, at most 86,375 records, and register indices below 1,024. The measured maximum is three probes. It reports 86,632 nodes, 358,660 helper calls across both passes, zero moves, and highest register 1020. Its 431,875 emitted bytes have SHA-256

```text
dc43874011ff558bd4d13f5032fb19b6773d631827647518ce1bd319d510b24a
```

The participant compiled that source with Ubuntu clang 18.1.3 and LLD 22.1.2:

```sh
clang-18 --target=wasm32 -Oz -ffreestanding -fno-builtin -nostdlib -c emitter.c -o emitter.o
wasm-ld --no-entry --allow-undefined --strip-all emitter.o -o emitter.wasm
```

Two clean builds produced the same 17,435-byte module with SHA-256 `d017ddd6dbc5237ea8fd18a87a8de7df042bfcbe34577805b9dd00d1541300f3`. `llvm-objdump -d` counts 5,142 static instructions. Wasmtime 49.0.0, with fuel consumption enabled, reports exactly 181,015,345 executed operators for the exported `run` function. The module has no `if`, `else`, `call_indirect`, or bulk-memory operator. Wasmtime does not charge structural operators such as `block`, `loop`, and `end`; every uncharged return closes a charged call or the one entry call. Charging two word operations per fuel unit plus one covers both charged and uncharged operators:

```text
2 * 181015345 + 1 = 362030691 operations.
```

The organizer does not compile or run this wasm module. Both declared experiments execute `BGen` and `BoundedEmitter`, the packaged byte-exact Python mirror, before every request. `bounded_check` checks all 15 C-reported fields, the C source hash, the polarity mask, the stream hash, and equality with the ordinary Python network interpreter. The wasm build, instruction count, fuel count, and module hash above are participant-run setup accounting. The organizer-run mirror is functional evidence for the exact emitted byte stream.

One batch costs

```text
86,375 kernel records + 34 stage-1 operations + 3 loop operations
= 86,412 operations for 256 trails.
```

## 4. Exact operation ledger

Every row below is an enforced upper bound. The handler limits are 2,800 operations per stage-1 hit, 3,800 fixed operations per finished trail, six operations per scanned table slot, 4,200 per cut, and 1,300 per slice check. The rolled recovery executes 3,161 records per call plus 47 surrounding operations. Its one-time work is 608 + 146 operations.

```text
main loop                                      114600072802150716000000000000000000000000
slice checks                                   6125117114595823863966200
stage-1 hits                                   442668855383443832397460937679200
finished trails                                43627374370
two cut trails                                 8400
recovery                                       369077513117107522004005527322667297546
bounded emitter and fixed setup                362844291
offset coordinate search                       461900436782186496
selector choice search                         281474976710656
total N                                        114969150757936685030565414702563218067159
```

The emitter row is `813600 + 2 * 181015345 + 1`. The fixed 813,600 operations cover the 256 input and output records at 3,100 operations each plus 20,000 operations for pass initialization, final output placement, checks, and return. Section 3 derives the two search rows. All three preprocessing rows are part of total time.

The organizer Pareto contract sets `reference_operation_cost = 4912` for `sha256-r64-prefix-v1`. The package contract can be printed with `python3 scripts/pareto_candidate.py --family sha256 --rounds 64 --show-contract`. Therefore

```text
log2(N / C) = 124.1382038451458780378999733235418909642.
```

The claimed `time_log2` is the upward-rounded 124.13821. The integer certificate is

```text
2^12413820 * 4912^100000 <= N^100000
N^100000 < 2^12413821 * 4912^100000.
```

## 5. Success probability and premise H1

Let F be a uniformly random function on N = 2^256 points, exposed by lazy sampling. Mark every fresh output independently as distinguished with probability theta. Run the exact bounded algorithm of Section 2 with every call to g replaced by F. Let P_F be its success probability.

The random-function proof uses N' = N(1-theta), q = Q/L, `k` chosen so the Chernoff bound for `Binomial(Q,theta) >= k` is at most 2^-40, and

```text
Pi(m) = product from i=0 to m-1 of (1 - i/N').
```

The successful birthday event loses probability only through the following disjointly charged causes: no useful collision among Q evaluations; detection after batch B; a partner on the same trail; a partner on a cut trail; a trail too old when its DP arrives; another collision on the remaining path; the Chernoff overflow; more than two cuts; a false 46-bit key match; table overflow; and the explicitly bounded early-halt terms.

For cuts, scan each lane's DP lottery. A fresh trail cut at age c contributes a run of c non-DP outputs. Except with the Chernoff event, at most `k + 256 + 2` such disjoint runs are exposed. Their count is dominated by `Binomial(k+258, exp(-c/L))`. Non-fresh trails are charged by the lazy-sampling collision hazard. Splitting at the first joining collision gives five root events: a self-join, a join whose combined remaining ages reach c, a second collision before the target DP, a target inside a run of c non-DPs, or a collision after c-1 fresh evaluations. Summing their expectations gives the cut-loss terms used by `certify`.

The detection-delay term integrates the chance that the first useful collision occurs at evaluation b against the chance that its partner trail sees no DP in the remaining `B-ceil(b/256)` batches. The certificate partitions the early region into 2,000 bins and the last 120 mean trail lengths into 20,000 bins. It uses outward-rounded 60-digit decimals for every exponential and logarithm. All integer counts are exact.

For the constants in Section 2, the certificate obtains

```text
P_F >= 0.390000001000... >= 0.39.
```

Premise H1 is score-critical and is not proved. It says that the real fixed walk g succeeds at least as often as F in this one attempt. More explicitly:

1. Distinct fresh evaluated inputs have independent uniform 256-bit outputs, so their collision hazard is 2^-256.
2. Iterates from the starts `r+t` have the first-collision law of a random mapping.
3. A fresh output is distinguished with probability 1294/2^122, independently of collision events.
4. Adaptivity does not reduce the hazard: after conditioning on the full earlier history and on which later outputs are DPs, a fresh evaluation equals any fixed earlier non-DP output with probability at least 2^-256.

H1 concerns this message family, this walk, trails of mean length about 2^111.66, and about 2^128 evaluations. It is not claimed for other domains or as a theorem about SHA-256. A higher collision hazard helps. A lower hazard requires more time.

## 6. Memory and preprocessing

Search memory is

```text
body code:        86,375 * 5                         = 431,875 bytes
other code:       1,766 * 36                         =  63,576 bytes
table:            ceil(85,085 * 47 / 8)              = 499,875 bytes
counters/copies                                         16,384 bytes
1,024 registers                                         32,768 bytes
recovery arrays                                           4,096 bytes
total                                                  1,048,574 bytes
```

The table field widths fit their maxima: key 46 bits, one written bit, and slot index below 85,085 < 2^17. Length is not stored.

The normative wasm emitter has 5,142 instructions at 36 bytes, for a 185,112-byte code image. Its scratch is 120,055 bytes:

```text
use counts                                                   87,150
recent gates                                                  192
CSE keys and values                                         8,192
free and pending register maps                                256
W, V, and Y arrays                                          4,352
15 one-word scratch arrays                                  1,920
TB carry arrays                                             1,408
four tail scratch arrays                                      512
AW pointers                                                    32
six output and allocator arrays                             6,144
output polarities                                             256
info block                                                      92
alignment allowance                                           128
12 scalar globals                                               48
state subtotal                                              23,532
AH and CH choices                                            4,619
IV, K, PW, OFF, PM, PERM, and SYN constants                    658
shadow stack                                                4,096
total                                                     120,055
```

`experiments/bssha.py` computes the 23,532-byte and 658-byte subtotals from these named arrays and compares them with the C emitter's live report. The complete setup peak is

```text
495451 program bytes + 16384 counters + 32768 registers
+ 4096 recovery arrays + 185112 emitter image + 120055 scratch
= 853866 bytes.
```

The count-only searches rebuild a candidate rather than retaining candidate DAGs. Their declared search image has at most 10,000 instructions, or 360,000 bytes. Both use the 120,055-byte builder scratch and at most 65,536 bytes of trial state. The offset search adds two 24-byte vectors and peaks at 545,639 bytes. The selector adds the 4,619-byte result tables and peaks at 550,210 bytes. The searches run sequentially with setup and the main search, so their peaks do not add. The main search remains the overall peak at 1,048,574 bytes. The claim rounds memory upward to 20 bits.

Total preprocessing is the 362,844,291-operation setup, the 461,900,436,782,186,496-operation offset search, and the 281,474,976,710,656-operation selector search:

```text
preprocessing_log2 = log2(462181912121741443 / 4912)
                   = 46.4191435675402393148348193010109386961.
```

The claim rounds this upward to 46.41915. There is no nonuniform advice because preprocessing constructs both the fixed offsets and the frozen selector tables, and setup constructs the body program.

The preprocessing integer certificate is

```text
2^4641914 * 4912^100000 <= 462181912121741443^100000
462181912121741443^100000 < 2^4641915 * 4912^100000.
```

## 7. Experiments and validation

`experiments/bssha.py` uses only the Python standard library. Both declared experiments first execute the `BGen` and `BoundedEmitter` byte-exact mirror and refuse the request if its count, bounds, fields, C source hash, SLP hash, polarity mask, or byte stream differ. The organizer runs this mirror, not the participant-run wasm measurement.

`bssha-n16` runs the same 256-lane search at width 16. The walk value is the low 16 bits of the complete two-block digest. Every returned pair therefore has distinct messages and equal low 16 digest bits. The organizer recomputes that event.

`proj-k0-w256` evaluates 256 full-width points per trial. Its sources rotate among independent seed-derived points, consecutive points, and iterates of g. The experiment inverts walk B, runs the fixed second block, and returns a pair only when the complete digests agree in the low 16 bits. This checks the message offsets, emitted program, inverse, feed-forward, and second block.

These experiments are functional checks. Their counts do not estimate the full-width success probability. H1 supplies the extrapolation to 2^128 evaluations.

A local development check evaluated the bounded-emitter SLP on 25,600 deterministic points and found no difference from the scalar walk or explicit inverse. Its driver and output are not packaged and are not claim evidence. The shipped self-test is the packaged evidence: it checks every emitted record, every T2 truth row, 2,560 lanes, 10,000 inverse round trips, four chained batches, the rolled recovery program, the complete digest network, and a width-16 search.

## 8. Credits and limits

Direct dependencies are d22ae1b2-2368-460a-b6d4-1e5e37ceb735 and 95263e47-d61b-43a6-bb46-30ced2488280. The dependency manifest also records their same-challenge lineage. From d22ae1b2 this package uses the T2 circuits, 47-bit index-layout table, two-pass recovery accounting, success plan, and its lineage. From 95263e47 it uses the constant-aware selection method, bounded emitter structure, and its lineage. The changed message offsets and the recent-XOR cancellation are new here.

The package does not test the full 256-bit functional graph, trails longer than 2^40, or the complete 2^128-scale attempt. It does not claim a practical collision or a weakness in deployed SHA-256.

## Appendix A. Reproduction output

Run `python3 experiments/bssha.py --ledger` to regenerate the plan, operation rows, program hash, and phase memory. Run `python3 experiments/bssha.py --selftest` for the functional checks. The exact random-function calculation uses the formulas in Section 5 and outward-rounded decimal arithmetic; its decisive output is

```text
Tp = 1294
tmax = 84827
B = 1326205536293000000000000000000000000
q = 83719e5368e5c5064d42d446b413f5fdd5bc79c27182e4541a52bdee6a59c788
memory bytes = 1048574
setup bytes = 853866
offset-search operations = 461900436782186496
selector-search operations = 281474976710656
P_lower certified = 0.390000001000...
N = 114969150757936685030565414702563218067159
log2(N/C) = 124.1382038451
time_log2 = 124.13821
```

## Appendix B. Exact certificate program

This standard-library program recomputes the exact ledger and the outward-rounded random-function bound.

```python
from fractions import Fraction
from math import log, exp, log2, log1p, comb, expm1

PH, FILT, LOOP, LANES = 86375, 34, 3, 256      # emitted records executed per batch, stage-1 test, loop control, lanes
INSTR_REC = 86375                                # emitted body records; SHA-256 bound in Section 3
PH7, EXTRA, RECINIT = 3161, 47, 146          # records executed per call of the rolled recovery program, extra operations per recovery batch, records executed once per recovery
N_BITS, S1, W, KAPPA = 256, 32, 90, 14          # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE, GEN_FUEL = 2800, 3800, 4200, 1300, 181015345
GEN_CODE, GEN_SCRATCH = 5142, 120055
OFFSET_EVALS, OFFSET_EVAL_OPS = 1641, 1 << 48
SELECTOR_SEARCH_OPS = 1 << 48
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 2
INSTR, OTHER_CODE, REGFILE, COUNTERS, SLOTB, ADVICE, ARRAYS = 36, 1729, 32768, 16384, 47, 0, 4096
KEYB = 46                                             # key bits (5 bytes)
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
GRAIN, TB = 10 ** 24, 17                       # B is a multiple of GRAIN; trail-number bits of a table entry
FINE, COARSE = 20000, 2000                      # bins of the detection-delay sum (last 120 L batches, earlier part)
body = PH + FILT + LOOP                                        # one batch = 86,412 operations
code_bytes = INSTR_REC * 5 + (FILT + LOOP + OTHER_CODE) * INSTR     # the body records once at 5 bytes, every other instruction once at 36 bytes
tmax = 84827
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def tail_log2(mean, k):                                        # Chernoff bound on P(count >= k)
    return (-mean + k * (1 + log(mean / k))) / log(2)


def plower(Tp, q):            # the lower bound of Lemma 2 on the success probability, q = Q / L (floats, as the program's _lossq; certify() below is the proof)
    L = Fraction(1 << D, Tp)
    c = -(-KAPPA * L.numerator // L.denominator)
    th, Lf, cf = Tp / 2.0 ** D, float(L), float(c)
    Q, B, Np = q * Lf, q * Lf / LANES, 2.0 ** N_BITS
    k = int(q) + 1
    while tail_log2(q, k) > -40:                               # N1 ~ Binomial(Q, theta) <= k - 1 except with probability 2^-40
        k += 1
    n2, shift = k + LANES + CMAX, 1 / (1 - k * Q / Np)
    pi = lambda m: exp(-m * (m - 1) / (2 * Np))
    split = max(1.0, Q - 120 * LANES * Lf)
    edges = [split * i / COARSE for i in range(COARSE + 1)] + [split + (Q - split) * i / FINE for i in range(1, FINE + 1)]
    delay, pa = 0.0, 1.0
    for b in edges[1:]:
        pb = pi(b)
        delay += (pa - pb) * exp(-th * max(0.0, B - b / LANES))
        pa = pb
    p, ql, hq = exp(-cf * th), Q * Lf / Np, Q * (Q - 1) / (2 * Np)
    p2 = exp(-(cf - 1) * th) * (1 + (cf - 1) * th / (1 - th))
    hh = (Q * (Q - 1) / 2 + 2.0 ** TB * Q) / Np
    cuts = 1 - sum(comb(n2, j) * p ** j * exp((n2 - j) * log1p(-p)) for j in range(CMAX + 1))
    t = [pi(Q) * shift, delay * shift, ql, (cf + SB) * Q * p * (q + LANES) / ((1 - p) * Np), hq * p2, hq * Lf * (Q + 2.0 ** TB) / Np, 2.0 ** -40,
         cuts + ql * (1 + (2 + KAPPA) * exp(-KAPPA / 2) + 2 * hq) + hq * p * (3 + 2 * KAPPA),
         tmax * (tmax - 1) / 2 * 2.0 ** -(min(KEYB - (Tp - 1).bit_length(), N_BITS - D) + log2(Tp)), 2.0 ** tail_log2(q, tmax - 59),
         Q * 2.0 ** TB / Np + k * k * Lf / Np + 255 * Q / Np + exp(min(700.0, -300 + (exp(5) - 1) * hh)) + 2.0 ** -90]
    return 1 - sum(t)


def plan_tp(Tp):              # the least B (a multiple of GRAIN) with plower >= 0.39
    L = Fraction(1 << D, Tp)
    lo, hi = 1.0, tmax + 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if plower(Tp, mid) >= P_MIN else (mid, hi)
    b = -(-int(hi * L / LANES) // GRAIN) * GRAIN
    while plower(Tp, float(b * LANES / L)) < P_MIN:
        b += GRAIN
    return L, b, -(-KAPPA * L.numerator // L.denominator)


def certify(Tp, B):           # Lemma 2 in exact rationals and 60-digit decimals (every exp and ln correctly rounded), results moved outward by 1e-40
    from decimal import Decimal as Dm, getcontext, localcontext, ROUND_CEILING, ROUND_FLOOR
    getcontext().prec = 60
    up = lambda x: x * (1 + Dm("1e-40")) + Dm("1e-58")
    dn = lambda x: x * (1 - Dm("1e-40")) - Dm("1e-58")

    def fd(x, u):             # Fraction -> Decimal rounded up (u) or down
        with localcontext() as cx:
            cx.rounding = ROUND_CEILING if u else ROUND_FLOOR
            return Dm(x.numerator) / Dm(x.denominator)
    ex = lambda x: up(fd(x, True).exp())                         # upper bound on exp(x), x rational
    L = Fraction(1 << D, Tp)
    th, Q = 1 / L, LANES * B
    Np = Fraction(Nn - Tp * (1 << (N_BITS - D)))                 # N' = N (1 - theta), an integer
    q = Q / L
    c = -(-KAPPA * L.numerator // L.denominator)
    M = c + SB
    qu, qd, lne = fd(q, True), fd(q, False), -Dm(2).ln() * 40
    k = int(q) + 1                                               # P(N1 >= k) <= e^-q (e q / k)^k <= 2^-40
    while up(-qd + k * (1 + (qu / k).ln())) > lne * (1 - Dm("1e-40")):
        k += 1
    n2 = k + LANES + CMAX
    shift = fd(1 / (1 - k * Q / Np), True)                       # Pi_(t-k) <= Pi_(t-1) shift, t <= Q
    lam = lambda m: Fraction(m * (m - 1), 2) / Np
    pi_up = lambda m: up((-fd(lam(m), False)).exp())             # Pi_m <= exp(-m (m - 1) / (2 N'))
    pi_lo = lambda m: dn((-fd(lam(m) + Fraction((m - 1) * m * (2 * m - 1), 6) / Np ** 2, True)).exp())   # ln (1 - x) >= -x - x^2 for x <= 1/2
    split = max(1, Q - 120 * LANES * (1 << D) // Tp)
    E = [split * i // COARSE for i in range(COARSE + 1)] + [split + (Q - split) * i // FINE for i in range(1, FINE + 1)]
    delay, pa = Dm(0), pi_up(E[0])
    for a, b in zip(E, E[1:]):
        pb = pi_lo(b)
        R = max(0, B - (-(-b // LANES)))
        delay += (pa - pb) * ex(-th * R)                         # sum over the bins (a, b] of (Pi_a - Pi_b) (1 - theta)^(B - ceil(b / 256)) <= e^(-theta R)
        pa = pi_up(b)
    delay = up(delay) * shift
    p = ex(-c * th)                                              # (1 - 1/L)^c <= e^(-c / L)
    p2 = ex(-(c - 1) * th) * fd(1 + (c - 1) * th / (1 - th), True)
    Hs = Fraction(Q * (Q - 1), 2) + (1 << TB) * Q
    H, PP = Hs / Np, Fraction(Q * (Q - 1), 2) / Np
    EK = p * (fd(q, True) + LANES) / (1 - p)
    terms = [pi_up(Q) * shift, delay,                            # collision (no partner), detection delay
             fd(Q * L / Np, True),                               # the partner is on the trail of t
             up(fd(Fraction(M * Q) / Np, True) * EK),            # the partner is on a trail with c free evaluations
             fd(PP, True) * p2,                                  # trail of t too old when the DP is reached
             fd(PP * L * (Q + (1 << TB)) / Np, True),            # a collision on the rest of the path
             Dm(2) ** -40,                                       # N1 >= k
             up(1 - sum(comb(n2, j) * p ** j * (1 - p) ** (n2 - j) for j in range(CMAX + 1))),   # step 6: fresh cut trails, P(Bin(n2, p) > CMAX)
             fd(Q * L / Np, True),                               # S
             fd(Q / Np, True) * fd(L, True) * ex(-(c - 2) * th / 2) * fd(2 + (c - 1) * th, True) + fd(PP, True) * p2,   # X
             fd(Q * L * H / Np + (Q + (1 << TB)) * L * PP / Np, True),   # J2a
             fd(PP * (1 - th), True) * p2, ex(-(c - 1) * th) * fd(H, True),   # J2b, Y
             fd(Fraction(tmax * (tmax - 1), 2 * Tp) / (1 << min(KEYB - (Tp - 1).bit_length(), N_BITS - D)), True),   # key false match
             up((-qd + (tmax - 59) * (1 + (qu / (tmax - 59)).ln())).exp()),   # table capacity
             fd(Fraction(Q << TB, Nn) + Fraction(k * k) * L / Np + 255 * Q / Np, True) + up((-300 + (Dm(5).exp() - 1) * fd(H, True)).exp()) + Dm(2) ** -90]
    assert Fraction(Q, 1 << 32) * Fraction(108, 1000) > 1000 and 240 * M <= Q   # stage-1 budget (Step 7): below e^-1000, inside the last term
    return 1 - sum(terms)


lo, hi = 1.0, tmax + 1.0                                       # the largest mean number of trails the table holds (tail within 2^-40)
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= -40 else (lo, mid)
a, z = 1, 4097                                                 # bisection: a Tp that reaches 0.39 at that mean (any Tp is a valid plan; not claimed optimal)
while z - a > 1:
    m = (a + z) // 2
    a, z = (m, z) if plower(m, lo) >= P_MIN else (a, m)
Tp = a
L, B, c = plan_tp(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
emitter = 2 * GEN_FUEL + 1
rows = [("main loop: B * %d" % body, body * B),
        ("slice checks: ceil(B / 2^48) * 1300", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished trails: tmax * (3800 + 6 * (tmax + 258))", tmax * (EVENT + 6 * (tmax + LANES + CMAX))),
        ("cut trails: 2 * 4200", CMAX * CUTOPS),
        ("recovery: (2 (c + 2^48) + 1) * (%d + 47) + 608 + %d" % (PH7, RECINIT), (2 * capr + 1) * (PH7 + EXTRA) + 608 + RECINIT),
        ("bounded emitter and fixed setup", SETUP_FIXED + emitter),
        ("offset coordinate search", OFFSET_EVALS * OFFSET_EVAL_OPS),
        ("selector choice search", SELECTOR_SEARCH_OPS)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", -(-(tmax + LANES + CMAX) * SLOTB // 8) + code_bytes + REGFILE + COUNTERS + ADVICE + ARRAYS)
print("setup bytes =", code_bytes + REGFILE + COUNTERS + ARRAYS + GEN_CODE * INSTR + GEN_SCRATCH)
print("P_lower = %.5f" % plower(Tp, float(B * LANES / L)))
pc = certify(Tp, B)
print("P_lower certified (exact rationals, 60-digit decimals) = %s" % str(pc)[:14])
assert pc >= Fraction(39, 100)
for k, v in rows:
    print(k.ljust(52), int(v))
print("N =", N)
P, C = 100000, 4912
preprocessing = sum(v for _, v in rows[-3:])


def log_certificate(label, value):
    a = (value ** P // C ** P).bit_length() - 1                 # 2^a * C^P <= value^P < 2^(a+1) * C^P
    while (1 << (a + 1)) * C ** P <= value ** P:
        a += 1
    while (1 << a) * C ** P > value ** P:
        a -= 1
    print("%s certificate: 2^%d * %d^%d <= value^%d < 2^%d * %d^%d" % (label, a, C, P, P, a + 1, C, P))
    return a


a = log_certificate("time", N)
pa = log_certificate("preprocessing", preprocessing)
print("log2(N/C) = %.10f" % (log2(N) - log2(C)))
print("time_log2 = %.5f" % ((a + 1) / P))
print("preprocessing_log2 = %.5f" % ((pa + 1) / P))
```
