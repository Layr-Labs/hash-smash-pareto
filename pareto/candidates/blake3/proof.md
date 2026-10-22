# BLAKE3 r6: a generic 256-lane birthday search with a seven-byte quotient filter

This entry finds an ordinary collision in the complete digest of 6-round
BLAKE3 under one declared random-function premise. It claims no differential,
structural weakness, or shortcut in BLAKE3. The construction is circuit and
memory engineering for the benchmark's declared word-RAM model.

The submitted value is `time_log2 = 124.88418`. The exact ledger value is
124.884175700155. Peak memory is 1,048,567 bytes, below
2^20, so the memory term is zero.

## 1. Target and collision relation

The target is `blake3-r6-prefix-v1`. Let

```
K = 0000008000000000000000800000000000000080000000000000000000000000
```

and let `M(x) = K || LE32(x)`, where `x` is a 256-bit integer. Each message is
one 64-byte block with the standard IV, counter 0, block length 64, flags 11,
rounds 0 through 5, and all 256 output bits. Write `f(x)` for that
digest as a little-endian integer.

The generated circuit stores the fixed output-polarity mask

```
q = 7588105370eaa8c914e1877c0c25b4159c0b35ccc453aec3b417e882fc51b943
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

More explicitly, let `t = x XOR y` and choose `yy` whose stored polarity
matches `t`. Then `carry = yy OR t = x OR y`. The older choice used the other
operand and still computed `x OR y`, but its mixed stored polarities required
an AND followed by an XOR. The all-zero round-7 prefix reaches this case in 26
columns, all in round 0 calls 4 through 7 at the first `c += d` step. The
column checker exhausts all eight physical input and polarity rows. Complete
organizer vectors and scalar digest comparisons cover the emitted circuit.

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
| XOR | 30,581 |
| AND | 2,806 |
| OR | 3,951 |
| total | 37,338 |

The allocator uses 773 registers and writes output plane `j` back to
register `j`. The next batch needs no plane copies, moves, or polarity
operations. The C and Python generators both report 37338 gates
and 393278 charged primitive calls.

## 3. Search, stage filter, and table

A point is distinguished when its low 32 bits are all one and

```
F = (x >> 32) mod 2^90 < Tp = 1783.
```

The density is `1783 / 2^122`; write `L` for its reciprocal. One fresh
uniform 256-bit word `r` defines every start `r+t mod 2^256`. The first 256
trail numbers occupy the lanes. A finished trail either starts the next trail
or invokes recovery if its endpoint key already appears in the table.

Every batch ANDs the lowest 11 planes. The
10 ANDs and direct zero branch cost 11
operations. Further zero-branch checkpoints occur after planes
`11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 32`. Each of the first 11 checkpoints has a
persistent 256-bit countdown register initialized to
`ceil((1+2^-8) B P_k)+64`, where
`P_k = 1-(1-2^-k)^256`. A passing batch executes `SUBI; BRLT` before it extends
the accumulator. The first extension also executes the three-operation
`CMP; BRGT; CALL` slice-threshold check. The exact bounds and extra costs are:

| passed planes | halt bound | extra operations |
| ---: | ---: | ---: |
| 11 | `156312804900052156160937764760898909` | 8 |
| 13 | `40921695548880910117976517881394195` | 5 |
| 15 | `10350157408449240467106219750819222` | 5 |
| 17 | `2595095407576941994006316958496561` | 5 |
| 19 | `649247250112223196443089128758524` | 5 |
| 21 | `162341417837424263780015249815988` | 5 |
| 23 | `40587205071336250855461524554999` | 5 |
| 25 | `10146916935460604355340610355328` | 5 |
| 27 | `2536736463160214786055044710594` | 5 |
| 29 | `634184567622064011220338947158` | 5 |
| 31 | `158546170145033348030708395769` | 4 |

The optimizer exhausts every checkpoint count and uses dynamic programming for
all increasing schedules at that count. Schedules with 27 or more budget
checkpoints fail the retained repeated-window proof condition. The minimum
valid total uses 11 budget checkpoints and 786
registers. The selected schedule is `11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 32`.
For every budget checkpoint the C optimizer verifies the three exact
conditions used by the retained union bound: `2^-18 B P_k / 3 > 1000`,
`2^10 M <= 2^k B P_k`, and `0.386 M / 2^k > 1000`, with
`M = c + 2^48 + 3000`. A failed condition rejects the schedule.
The batch loop stores `left = B + 3000 - completed_batches`. It loads,
decrements, stores, and conditionally branches on `left`. Zero falls through
to `HALT batch_limit`, so even a path with no passing batch executes at most
`B + 3000` steps. Thus a main batch costs
`37338 + 11 + 4 = 37353` operations.

The passing path compares `left` directly with descending slice thresholds.
The 256 initial trails store `T+1`, where `T=B+3000`; a trail replaced after
batch `b` stores the current pre-decrement `left = T-b+1`. During batch `j`,
`left = T-j+1`, so `birth_left-left` is exactly `j` for an initial trail and
`j-b` for a replacement. No conversion to an increasing batch number is needed
and the passing-batch costs are the exact rows above.

The 52-bit endpoint key consists of 41 bits above the 90-bit window followed by
the 11-bit value `F`. A quotient-filter run implies the high
16 key bits. Each slot stores a 36-bit remainder, 3 quotient-filter bits, and a fixed 17-bit trail number. The key and trail
streams are separately aligned to 256-bit words:

```
32 ceil(39 S / 256) + 32 ceil(17 S / 256)
= 566880 + 247104
= 813,984 bytes.
```

There are 116,283 slots and capacity
116,282. The largest reachable trail number is
116,539, below `2^17`.
The 16 implied bits and 36 stored bits retain all 52 key bits. The exact key false-match loss is
`1.724289127484e-06`.

Lookup and insertion each have an `8 S` loop-body countdown and halt. The
ledger charges `2048 S` operations for each finished endpoint, covering the
worst full lookup and insertion shift, including crossing packed-field loads
and stores.

## 4. Recovery

On a table match, pass 1 stores both time-zero starts and walks them in two
packed lanes. It checks `c_r = 36,976,841,610,169,280,592,276,405,042,010,708` before every compression.
Every `D = 4,513,774,610,616,367,259,799,365,849,855` steps it stores a checkpoint pair.
At most 8,192 pairs use 524,288 bytes in the former table region.

Pass 2 aligns the longer trail, rejects unequal endpoints and already-aligned
starts, and bisects the checkpoints with upper index
`floor(short_length / D) + 1`. It uses at most 16 single-lane probes and one
joint walk. It rejects an equal predecessor pair. The packed circuit has
1,323 word operations. Its permuted outputs are
snapshotted before inputs are restored, so no handoff overwrites an unread
output.

The recovery ledger charges 64 control operations per pass-1 batch, 80 per
checkpoint, 128 per pass-2 batch, 100 per probe, and 8,000 fixed operations.

## 5. Exact work ledger

The organizer reference cost is `C = 1262` word operations per
selected-target compression. The exact rows are:

| row | word operations |
| --- | ---: |
| main | 49,485,505,559,554,938,000,000,000,000,000,112,059,000 |
| passing-batch rest | 1,524,165,283,764,569,425,287,495,423,360,037,193 |
| slice checks | 18,826,635,879,719,333,388,496,000 |
| stage-1 hits | 442,201,951,390,361,785,888,671,875,179,200 |
| finished endpoints and table work | 27,692,719,234,288 |
| cut | 4,200 |
| recovery | 51,398,220,591,624,866,112,684,844,750,687,890,241 |
| setup and emitter | 165,592,400 |
| prefix choice | 64,692,944,896 |
| capacity and probability planner | 1,099,511,627,776 |
| total `N` | 49,538,428,387,632,297,652,535,637,977,036,513,065,194 |

The GMP ledger checks

```
2^12488417*1262^100000<=N^100000<2^12488418*1262^100000.
```

Therefore `log2(N / 1262) = 124.884175700155` at the displayed
precision.

The runtime emitter row is
`200(2*393278+37338)+813600 = 165592400`. The two
builds are the use-count and emission passes. The fixed 813,600 operations are
256 initial inserts at 3,100 operations each, plus 20,000 operations for the
fresh word, counters, and reloads.

The planner compares six fixed layout families. For each family it checks all
31 possible checkpoint counts and uses a dynamic program over all increasing
checkpoint schedules. The optimized probability planner uses bisection, while
the independent C verifier also executes an exhaustive `Tp` scan. Charging
both gives at most `6(4095+82) = 25062` loss evaluations. One evaluation scans
22,000 delay bins and has fewer than `2^24` charged arithmetic operations. All
schedule dynamic programs, capacity bisections, integer field checks, and final
constant construction fit in another `2^37` operations. Thus
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
`k = 116253` is the least integer for which
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

For this table `a = 1`, the exact maximum number of 52-bit logical
keys represented by one stored quotient-filter code. The `key_alias` formula
charges distinct distinguished endpoints that share a stored code. Outside
the event of 60 or more collisions, which is
in `finite_and_halts`, the number of finished trails is at most `N1 + 59` for
`N1 ~ Binomial(Q,theta)`. A full table of capacity
116282 therefore implies `N1 >= 116223`.
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
| `no_collision` | `0.608548091662627033012916628337457678674662732143475918637554631994551741048770777972769236` |
| `detection_delay` | `0.00136473377861346900895483742517830650172095903555619244319638052232603737927231360982457113` |
| `same_trail_partner` | `0.00000873417173264108090114291767171169997519833368778395889051985035151800788535738936815262553` |
| `long_partner` | `4.10414692776877701943762909505775425957960340397022428870949247844189797912424135422377051E-8` |
| `age_cap` | `2.14983806878058615215658954433594647225505639222914334202031957580040717827959459080823913E-8` |
| `recovery_cap` | `0.0000548225599009118897227228456048463364806259867654725360747826996447306246224428116048202914` |
| `second_collision` | `0.00000433808262141680088285477328064969565066484554349713055961129468883912493451634399583153080` |
| `finished_count` | `9.094947017729282379150390625000000000000000000000000000000009094947017730282379150390625E-13` |
| `cut_and_disturbance` | `0.0000174919110957492368834874177222838406133992152809499762250145836081100201753441692143006025` |
| `key_alias` | `0.00000172428912748444568944559027756858393508132361189007291082445316881660123387549074593381941` |
| `table_capacity` | `1.74768842720187087833955561434329524945203995514832298698971347905418236429026750079047025E-12` |
| `finite_and_halts` | `8.07794299644730732667349349609826886664528839914896330368514518878646208089028262982493115E-28` |

Their directed-rounded sum is

```
0.609999998998225854098557635173428333591620007147321056314063892347977887759245514889450495
```

so

```
P_F >= 1 - loss_sum >= 0.390000001001774145901442364826571666408379992852678943685935717652021110466608583668084678 > 0.39.
```

H1 is the score-critical premise: the fixed walk `g` succeeds at least as
often as this lazy-random-function program. H1 grants the collision law and
distinguished membership only for this fixed message family and bounded
attempt. It is declared, not proved, and no experiment contributes a
probability to the score.

The comparator is the standard distinguished-point birthday-search model of
van Oorschot and Wiener, and the generic entries of this track rest on it. The
comparison is aggregate: probability is taken over the random start for `g`
and over the random start and lazy-sampled mapping for the comparator. The
comparator samples one uniform output on the first query to each new input and
reuses that output on repeats. If its pair-collision rate were smaller by a
factor `1-eps`, the retained sensitivity calculation prices the extra work at
0.0073 bit for `eps=0.01`, 0.0370 bit for `eps=0.05`, 0.0760 bit for
`eps=0.10`, and 0.2075 bit for `eps=0.25`.

## 7. Machine convention and memory

H3 declares a classical 256-bit load/store word RAM with 786 addressable
registers and a direct zero-test branch. XOR, AND, and OR use native
four-byte records: a two-bit opcode and three 10-bit register fields. These records are the
machine's instruction format; no decoder, interpreter, expanded stream, or
decode buffer appears in a priced path. Python unpacking helpers are test-only
mirrors of the native format and never execute in the priced program. The packed recovery circuit uses
native five-byte records with an eight-bit opcode and three 10-bit register
fields. Every control record is charged 36 bytes, enough for a complete
256-bit immediate. The batch loop's `BRNZ` is the same native direct nonzero
branch already used by stage 1 and the table handlers.

The static image contains 37,369 bitwise records,
1,323 packed-recovery records, and
1,335 control records. It occupies
204,151 bytes. No decoded compact instruction stream is used.

Search memory is:

| object | bytes |
| --- | ---: |
| static image | 204,151 |
| 786 registers | 25,152 |
| packed lane metadata and persistent state | 5,248 |
| prefix advice | 32 |
| quotient filter | 813,984 |
| total | 1,048,567 |

The metadata region contains 544 bytes of packed 17-bit trail numbers, 4,096
bytes of packed 128-bit birth batches, and 608 bytes of state or padding.
The checkpoint countdowns, `left`, and `next_left` occupy registers
773 through 785; the step uses only registers 0 through 772. Other
persistent counters and limits are explicitly loaded and stored.

Setup memory is:

| object | bytes |
| --- | ---: |
| static image | 204,151 |
| packed lane metadata and persistent state | 5,248 |
| prefix advice | 32 |
| bounded runtime emitter, `2400 * 36` | 86,400 |
| charged generator stack and scratch bound | 49,296 |
| total | 345,127 |

The 49,296-byte conservative bound is derived as 44,524 bytes of use counters
for the sentinel, 256 inputs, and the 44,266-gate round-7 envelope, plus 2,400
bytes of generator state, 256 bytes of constants, a 2,048-byte shadow stack,
and a 68-byte result record. The shipped phase checker computes the smaller
round-specific need and asserts that it does not exceed this charged bound.

## 8. Experiments, credit, and limits

`experiments/bsrho.py` rebuilds the round-6 step and control image before
serving organizer requests. `bsrho-n18` executes the reduced-width search and
checkpoint recovery. `proj-prefix-w256` checks 2,048 full-width points against
the fixed prefix and output mask. `h1-law-n20` selects one fixed 20-bit
coordinate restriction of the actual walk from all request seeds. Sixty-four
groups share that function. Sixty-four complete lazy-random-function ensembles
provide separate 32-ensemble fit and 32-ensemble calibration sets. The output
exports four collision bins, the calibrated score and limit, the
globally-fresh distinguished count, its z-score and limit, and `law_pass`.
The experiment program structurally checks that the batch loop is exactly
`LOAD, SUBI, STORE, BRNZ, HALT`, that its only direct back-edge is conditional,
and that a three-batch no-passing simulation reaches `HALT batch_limit`.
It also identifies all three emitted birth writes, requires the initial write
to be `T+1`, requires both replacement writes to copy pre-decrement `left`, and
checks their ages against the increasing-batch equations above.
Every request also tests the maximum value and first overflow of the two-bit
gate opcode, each 10-bit gate register, the eight-bit recovery opcode, each
10-bit recovery register, the 16-bit quotient, 36-bit remainder, 3 filter
bits, 17-bit trail number, and 128-bit birth batch. It checks the exact last
table slot and rejects the next slot.

This construction credits 0e117e0b-23ba-468f-836f-e2c3314e18cc as the direct public
round-6 frontier, 11d961ad-d526-4279-8295-382cff99088b as the reviewed
generator base, 2c5a749b-e0db-4420-85fd-7b9b987efc33 for the quotient-filter
and recovery methods, and 10ce9f59-80a1-4304-92cc-ca4dede3bbcc for the
pair-carry columns. `dependencies.json` records the retained lineage with full
identifiers.

The limits are explicit. H1 is unproved. H3 is a declared machine convention.
The random-function probability bound has little numerical margin above 0.39.
Reduced-width first-collision statistics do not establish the 256-bit premise.
This remains a generic birthday construction, not a weakness in BLAKE3.
