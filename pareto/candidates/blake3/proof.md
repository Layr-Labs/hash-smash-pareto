# BLAKE3 r4: a generic 256-lane birthday search with a seven-byte quotient filter

This entry finds an ordinary collision in the complete digest of 4-round
BLAKE3 under one declared random-function premise. It claims no differential,
structural weakness, or shortcut in BLAKE3. The construction is circuit and
memory engineering for the benchmark's declared word-RAM model.

The submitted value is `time_log2 = 124.79222`. The exact ledger value is
124.792211903858. Peak memory is 1,048,555 bytes, below
2^20, so the memory term is zero.

## 1. Target and collision relation

The target is `blake3-r4-prefix-v1`. Let

```
K = 0000008000000000000000800000000000000070000000000000000000000000
```

and let `M(x) = K || LE32(x)`, where `x` is a 256-bit integer. Each message is
one 64-byte block with the standard IV, counter 0, block length 64, flags 11,
rounds 0 through 3, and all 256 output bits. Write `f(x)` for that
digest as a little-endian integer.

The generated circuit stores the fixed output-polarity mask

```
q = d5ff1030c36ff5a38b91d97fd466bac7ce5510dca9d32fcff9fd8b884a47fafe
```

and walks `g(x) = f(x) XOR q`. XOR by a fixed word is a bijection. Therefore,
`g(x) = g(y)` if and only if `f(x) = f(y)`. Recovery returns unequal
predecessors, so it returns distinct messages with equal complete digests.

## 2. Generated step

The program evaluates 256 trails in parallel. One bit of each 256-bit machine
word is one lane. A 32-bit BLAKE3 word therefore occupies 32 planes.

Signals carry a physical node and a free stored-polarity bit. Three-variable
`a + b + m` additions use one ripple of carry pairs `(u,U)`. The generator
tries both published nine-gate templates, all six addend orders, and the exact
stored-polarity circuits inherited from the reviewed r7 generator. Bit 0 is a
full adder. The last two columns omit dead outputs. With a constant one and
opposite stored polarities, the carry is the OR of the matching operand and
the sum plane, so that full-adder case costs two gates.

The charged high-nibble coordinate descent evaluates 241
complete circuits: one zero-prefix baseline, 120 candidates in the improving
sweep, and 120 candidates in the confirming sweep. Every build halts before
`2^20` generator primitive calls and 60,000 emitted gates. At 200 operations
per call or emission, one build costs less than
`200(2^20+60000) < 2^28`; the ledger charges the fixed endpoint `2^28`.
It selects the prefix above and costs
`241*2^28 = 64,692,944,896` word operations.

The final step census is:

| opcode | gates |
| --- | ---: |
| XOR | 19,189 |
| AND | 1,798 |
| OR | 2,492 |
| total | 23,479 |

The allocator uses 773 registers and writes output plane `j` back to
register `j`. The next batch needs no plane copies, moves, or polarity
operations. The C and Python generators both report 23479 gates
and 250189 charged primitive calls.

## 3. Search, stage filter, and table

A point is distinguished when its low 32 bits are all one and

```
F = (x >> 32) mod 2^90 < Tp = 1860.
```

The density is `1860 / 2^122`; write `L` for its reciprocal. One fresh
uniform 256-bit word `r` defines every start `r+t mod 2^256`. The first 256
trail numbers occupy the lanes. A finished trail either starts the next trail
or invokes recovery if its endpoint key already appears in the table.

Every batch ANDs the lowest 12 planes. Eleven ANDs and one zero branch cost 12
operations. A passing batch loads, decrements, stores, and checks its hard
budget, ANDs the remaining 20 planes, loads and checks the next scheduled
limit, and branches on the hit mask. The passing surcharge is 29 operations.
The batch loop loads, increments, stores, and branches on its counter. Thus a
main batch costs `23479 + 12 + 4 = 23495` operations.

The alternative 13-plane OR-first filter was measured with its complete
passing-batch halt row. It is slower for this program because the reviewed
AND-first checkpoint costs only 12 unconditional operations.

The 52-bit endpoint key consists of 41 bits above the 90-bit window followed by
the 11-bit value `F`. A quotient-filter run implies the high 16 key bits. Each
slot stores a 36-bit remainder, three quotient-filter bits, and a fixed 17-bit
trail number. The key and trail streams are separately aligned to 256-bit
words:

```
32 ceil(39 S / 256) + 32 ceil(17 S / 256)
= 591008 + 257632
= 848,640 bytes.
```

There are 121,232 slots and capacity
121,231. The largest reachable trail number is
121,488, below `2^17`. The 16 implied bits and 36 stored
bits retain all 52 key bits. The exact key false-match loss is
`1.796598491139e-06`.

Lookup and insertion each have an `8 S` loop-body countdown and halt. The
ledger charges `2048 S` operations for each finished endpoint, covering the
worst full lookup and insertion shift, including crossing packed-field loads
and stores.

## 4. Recovery

On a table match, pass 1 stores both time-zero starts and walks them in two
packed lanes. It checks `c_r = 35,446,079,887,597,756,610,768,188,274,142,523` before every compression.
Every `D = 4,326,914,048,779,023,023,775,413,607,684` steps it stores a checkpoint pair.
At most 8,192 pairs use 524,288 bytes in the former table region.

Pass 2 aligns the longer trail, rejects unequal endpoints and already-aligned
starts, and bisects the checkpoints with upper index
`floor(short_length / D) + 1`. It uses at most 16 single-lane probes and one
joint walk. It rejects an equal predecessor pair. The packed circuit has
845 word operations. Its permuted outputs are
snapshotted before inputs are restored, so no handoff overwrites an unread
output.

The recovery ledger charges 64 control operations per pass-1 batch, 80 per
checkpoint, 128 per pass-2 batch, 100 per probe, and 8,000 fixed operations.

## 5. Exact work ledger

The organizer reference cost is `C = 846` word operations per
selected-target compression. The exact rows are:

| row | word operations |
| --- | ---: |
| main | 31,123,362,994,657,645,000,000,000,000,000,070,485,000 |
| passing-batch rest | 2,330,039,877,627,596,938,124,082,105,062,835,444 |
| slice checks | 18,824,838,891,916,328,975,640,000 |
| stage-1 hits | 442,159,743,556,833,267,211,914,062,679,200 |
| finished endpoints and table work | 30,100,073,538,216 |
| cut | 4,200 |
| recovery | 32,292,058,103,107,214,579,024,552,257,680,919,411 |
| setup and emitter | 105,585,000 |
| prefix choice | 64,692,944,896 |
| capacity and probability planner | 1,099,511,627,776 |
| total `N` | 31,157,985,534,798,142,193,189,307,793,870,236,259,143 |

The GMP ledger checks

```
2^12479221*846^100000<=N^100000<2^12479222*846^100000.
```

Therefore `log2(N / 846) = 124.792211903858` at the displayed
precision.

The runtime emitter row is
`200(2*250189+23479)+813600 = 105585000`. The two
builds are the use-count and emission passes. The fixed 813,600 operations are
256 initial inserts at 3,100 operations each, plus 20,000 operations for the
fresh word, counters, and reloads.

The planner compares six fixed layout and stage candidates. The optimized
planner uses bisection, while the independent C verifier also executes an
exhaustive `Tp` scan. Charging both gives at most `6(4095+82) = 25062` loss
evaluations. One evaluation scans 22,000 delay bins and has fewer than `2^24`
charged arithmetic operations. All capacity bisections, integer field checks,
and final constant construction fit in another `2^37` operations. Thus
`25062*2^24 + 2^37 < 2^40`, and the ledger charges exactly
1,099,511,627,776 operations. Each table-capacity search uses at most
20 integer bisection steps and is included in that allowance.

## 6. Random-function probability and H1

Let `n = 2^256`, `theta = Tp / 2^122`, `L = 1/theta`,
`N' = n(1-theta)`, `Q = 256 B`, and `q = Q/L`. A lazy random function
supplies one independent uniform answer for each input not previously queried.
Conditioning on a non-distinguished answer leaves exactly `N'` possible
values. Repeated inputs reuse their first answer. These statements and the one
fresh uniform start `r` define the whole probability space.

Put

```
Pi(m) = product(i=0..m-1, 1-i/N')
H     = Q(Q-1)/(2N')
p     = exp(-c theta)
p2(x) = exp(-(x-1) theta) (1 + (x-1) theta/(1-theta)).
```

Here `c = ceil(20 L)`, `c_r = ceil(12.4 L)`, `S_b = 2^48`, and
`k = 121207` is the least integer for which
`exp(-q) (e q/k)^k <= 2^-40`. Set `n2 = k + 256 + 1` and
`s = 1/(1-kQ/N')`. For the first-collision product the certificate uses
`Pi(m) <= exp(-m(m-1)/(2N'))` and
`Pi(m) >= exp(-m(m-1)/(2N') - sum(i^2)/N'^2)`. The second inequality follows
from `ln(1-x) >= -x-x^2`, since every encountered `x` is below one half.

The loss formulas are:

```
no_collision       = Pi_upper(Q) s
detection_delay    = s sum_(a,b] (Pi_upper(a)-Pi_lower(b))
                         exp(-theta max(0, B-ceil(b/256)))
same_trail_partner = Q L / N'
long_partner       = (c+S_b+3000) Q p (q+256) / ((1-p) N')
age_cap            = H p2(c)
recovery_cap       = 2 H p2(12.4 L)
second_collision   = H L (Q+2^17) / N'
finished_count     = 2^-40
cut_and_disturbance= Pr[Binomial(n2,p)>1]
                     + (Q L/N') (1+22 exp(-10)+2H) + 43 H p
key_alias          = C(tmax,2) a / (2^41 Tp)
table_capacity     = exp(-q+t(1+ln(q/t))), t=tmax-59
finite_and_halts   = Q 2^17/N' + k^2 L/N' + 255 Q/N'
                     + exp(-300+(e^5-1)(C(Q,2)+2^17 Q)/N') + 2^-90.
```

For this seven-byte table `a = 1` because all 52 logical key bits
are represented by 16 implied quotient bits and 36 stored bits. The
`key_alias` formula still charges distinct distinguished endpoints that share
the 52-bit logical key. Outside the event of 60 or more collisions, which is
in `finite_and_halts`, the number of finished trails is at most `N1 + 59` for
`N1 ~ Binomial(Q,theta)`. A full table of capacity
121231 therefore implies `N1 >= 121172`.
The displayed `table_capacity` formula is the binomial Chernoff bound evaluated
at that threshold, not at a rounded capacity mean.

The delay sum uses 2,000 integer bins before the last 120 mean trail lengths
and 20,000 integer bins inside that final interval. Each bin uses the product
endpoint and batch ceiling that increase the loss. Geometric tails give the
partner, age, recovery, cut, and disturbance rows. The last row covers the
finite-domain start events, 60 or more collisions, stage and passing-budget
tails, a failed recovery not already counted as an alias, delayed limit checks,
and rounding slack.

The certificate starts from exact integers and `Fraction` rationals, evaluates
transcendentals with 90 decimal digits, and moves every upper result outward by
`abs(x)*1e-60 + 1e-85`; lower results move outward in the other direction. Its
individual upper endpoints are:

| loss | directed upper endpoint |
| --- | ---: |
| `no_collision` | `0.608605791323433435902944648419910050442496338801252447489002364959684139485442746573202214` |
| `detection_delay` | `0.00130823724002592316466977581004325774356071331492408630110888923654400761931451855398264659` |
| `same_trail_partner` | `0.00000837179664829430523499375939508901624485708277416131416167224983115295280654338798183455943` |
| `long_partner` | `4.10298283106245491996116355772423391322991230122727166547070816396800497760745840555245312E-8` |
| `age_cap` | `2.14942768761196675149613637134039025847655580074874091921788299694030512251535680738885341E-8` |
| `recovery_cap` | `0.0000548120948586719388166504087083227323151197789051835699313079438916374294514523746743712132` |
| `second_collision` | `0.00000415730466828650104326846601884014741137101397317363992511776851338064082206684795926123898` |
| `finished_count` | `9.094947017729282379150390625000000000000000000000000000000009094947017730282379150390625E-13` |
| `cut_and_disturbance` | `0.0000167701133794200600829013343501630333054463408972187033764583261339870890241680845511278461` |
| `key_alias` | `0.00000179659849113851387594496050188618321572580645161290322580645161290322580645161290322580646` |
| `table_capacity` | `1.90962810983679862344621791888891656611096280481504750556193195521337714551788437951867186E-12` |
| `finite_and_halts` | `8.07794314240798856125139759713453629020957318729364804410619070499034477754081797740498979E-28` |

Their directed-rounded sum is

```
0.609999998998429479942494625401082471166979061895109626199126750348641067549321774487297405
```

so

```
P_F >= 1 - loss_sum >= 0.390000001001570520057505374598917528833020938104890373800872859651357930880158168007227996 > 0.39.
```

H1 is the score-critical premise: the fixed walk `g` succeeds at least as
often as this lazy-random-function program. H1 grants the collision law and
distinguished membership only for this fixed message family and bounded
attempt. It is declared, not proved, and no experiment contributes a
probability to the score.

## 7. Machine convention and memory

H3 declares a classical 256-bit load/store word RAM with 775 addressable
registers and a direct zero-test branch. XOR, AND, and OR use native five-byte
records: an eight-bit opcode and three 10-bit register fields. The packed
recovery circuit uses the same native format. Every control record is charged
36 bytes, enough for a complete 256-bit immediate.

The static image contains 23,510 bitwise records,
845 packed-recovery records, and
1,335 control records. It occupies
169,835 bytes. No decoded compact instruction stream is used.

Search memory is:

| object | bytes |
| --- | ---: |
| static image | 169,835 |
| 775 registers | 24,800 |
| packed lane metadata and persistent state | 5,248 |
| prefix advice | 32 |
| quotient filter | 848,640 |
| total | 1,048,555 |

The metadata region contains 544 bytes of packed 17-bit trail numbers, 4,096
bytes of packed 128-bit birth batches, and 608 bytes of state or padding.
Persistent counters and limits are explicitly loaded and stored; step scratch
registers do not preserve them. Setup memory is 310,811
bytes and includes the emitter image, stack, and scratch.

## 8. Experiments, credit, and limits

`experiments/bsrho.py` rebuilds the round-4 step and control image before
serving organizer requests. `bsrho-n18` executes the reduced-width search and
checkpoint recovery. `proj-prefix-w256` checks 2,048 full-width points against
the fixed prefix and output mask. `h1-law-n20` selects one fixed 20-bit
coordinate restriction of the actual walk from all request seeds. Sixty-four
groups share that function. Sixty-four complete lazy-random-function ensembles
provide separate 32-ensemble fit and 32-ensemble calibration sets. The output
exports four collision bins, the calibrated score and limit, the
globally-fresh distinguished count, its z-score and limit, and `law_pass`.

This construction credits 1b7bd746-17fa-429f-84f9-bbecc944ad38 as the direct public
round-4 frontier, 11d961ad-d526-4279-8295-382cff99088b as the reviewed
generator base, 2c5a749b-e0db-4420-85fd-7b9b987efc33 for the seven-byte
quotient filter and recovery, and 10ce9f59-80a1-4304-92cc-ca4dede3bbcc for the
pair-carry columns. `dependencies.json` records the retained lineage with full
identifiers.

The limits are explicit. H1 is unproved. H3 is a declared machine convention.
The random-function probability bound has little numerical margin above 0.39.
Reduced-width first-collision statistics do not establish the 256-bit premise.
This remains a generic birthday construction, not a weakness in BLAKE3.
