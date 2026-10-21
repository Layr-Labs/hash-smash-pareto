# BLAKE3 r7: a generic 256-lane birthday search with a split quotient filter and checkpoint recovery

This entry finds an ordinary collision in the complete digest of seven-round
BLAKE3 under one declared random-function premise. It claims no differential,
structural weakness, or shortcut in BLAKE3. The construction is circuit and
memory engineering for the benchmark's declared word-RAM model.

The exact submitted value is `time_log2 = 124.90969`. The unrounded value is
124.909684496472. Peak memory is 1,048,558 bytes, below 2^20, so the memory
penalty is zero.

## 1. Target and collision relation

The target is `blake3-r7-prefix-v1`. Let

```
K = 0000008000000000000000800000000000000080000000000000000000000000
```

and let `M(x) = K || LE32(x)`, where `x` is a 256-bit integer and `LE32`
emits 32 little-endian bytes. Each message is one 64-byte block with the
standard IV, counter 0, block length 64, flags 11, seven compression rounds,
and output words `v[i] XOR v[i+8]` for `0 <= i < 8`. Write `f(x)` for that
complete 256-bit digest read as a little-endian integer.

The bit-sliced emitter stores some output planes complemented. Their fixed
polarity mask is

```
q = 435ce946177aeb0342c1963f123ebb02537dabf38aa8e0eb030a731ce33b4869.
```

The walk is `g(x) = f(x) XOR q`. XOR by a fixed word is a bijection, so
`g(x) = g(y)` if and only if `f(x) = f(y)`. Recovery returns distinct `x`
and `y`, hence distinct `M(x)` and `M(y)` with equal complete digests.

## 2. Search algorithm

The search runs 256 trails in parallel. One bit of each 256-bit word is one
lane. A 32-bit BLAKE3 word is therefore 32 machine words called planes.
One generated straight-line circuit evaluates `g` on all lanes.

The distinguished-point predicate uses all ones rather than all zeros. A
point is distinguished when its low 32 bits are `0xffffffff` and

```
F = (x >> 32) mod 2^90
```

is less than `Tp = 1968`. Its density is
`theta = 1968 / 2^122`, and `L = 1 / theta`.

One fresh uniform 256-bit word `r` defines every start. Trail number `t`
starts at `r + t mod 2^256`. The first 256 starts occupy the lanes. After a
trail reaches a distinguished point, the program either starts the next trail
in that lane or invokes recovery if the point's key is already in the table.

The 52-bit key contains the 41 bits above the 90-bit window followed by the
11 low bits of `F`. Since `F < 1968 < 2^11`, those 11 bits identify `F`.
The table retains 45 bits of this logical key.

The main limits are:

| quantity | value |
| --- | ---: |
| table capacity | 128,231 keys |
| table slots | 128,232 |
| `B` planned batches | 1,325,048,516,671,000,000,000,000,000,000,000,000 |
| charged batches | `B + 3,000` |
| evaluations `Q = 256 B` | 339,212,420,267,776,000,000,000,000,000,000,000,000 |
| age cap `c = ceil(20 L)` | 54,033,658,365,240,482,638,366,140,661,802,626 |
| recovery cap `c_r = ceil(12.4 L)` | 33,500,868,186,449,099,235,787,007,210,317,628 |
| checkpoint spacing | 4,089,461,448,541,149,809,056,031,153,604 |
| stage-1-hit limit | 157,958,092,292,666,435,241,699,218,814 |
| passing-batch limit | 80,368,537,913,363,358,574,902,023,491,743 |

Every limit has a halt. The main batch count and the slice limit are checked
only when a batch passes the 12-plane checkpoint. A run that goes more than
3,000 batches beyond a limit fails. The work ledger charges all 3,000 batches,
and the random-function bound includes the late-check event in its small-term
allowance.

## 3. Generated seven-round step

Each signal is `(node, polarity)`. The register holds the physical node, while
the semantic plane is the physical value XOR the polarity bit. Complementing
a signal therefore changes metadata and costs no word operation.

Two-addend sums use a pivot full adder. Among three variable inputs, two have
the same stored polarity. Call those `x` and `y`, and call the third `p`:

```
u     = x XOR p
sum   = u XOR y
carry = (u AND (y XOR p)) XOR p
```

This costs five gates. With one constant input, the sum starts with
`t = x XOR y`. For constant one and opposite stored polarities, choose `yy`
whose polarity equals the stored polarity of `t`; then
`carry = yy OR t`. The XOR for `t` and the OR are two gates. The complete
digest checker covers this branch.

Every all-variable `a + b + m` uses one pair-carry ripple. The incoming carry
is `(u,U)` with value `U ? 1 : 2u`. A middle column maps `x,y,z,u,U` to the
sum and the next pair. The emitter tries both published nine-gate templates,
all six addend orders, and the exact circuits for stored-polarity masks 0x10
and 0x07. It keeps the first minimum under its fixed order. Bit 0 is a full
adder, bit 30 omits dead `u'`, and bit 31 emits only the sum.

An independent C test evaluates all four exact circuits on all 32 physical
input rows. It enforces `s` and `U'` on every row and enforces `u'` whenever
`U'` is zero. The same test checks the two-gate constant-one identity.

The fixed prefix came from this charged coordinate descent: start at eight
zero words; for words 0 through 7, try the 16 values `v << 28` in increasing
order; keep a value only when the full gate count falls; repeat until a sweep
keeps nothing. The 241 evaluations select words

```
(80000000, 00000000, 80000000, 00000000,
 80000000, 00000000, 00000000, 00000000).
```

The search evaluates 241 circuits: one zero-prefix baseline, 120 candidates in
the improving sweep, and 120 candidates in the confirming sweep. Every build
halts before `2^20` generator primitive calls and 60,000 emitted gates. At 200
operations per call or emission, one build costs less than
`200(2^20+60000) < 2^28`. The ledger charges the fixed endpoint `2^28`, so the
prefix search costs exactly `241*2^28 = 64,692,944,896` word operations. Its
result is 32 bytes of declared advice.

The final step census is:

| opcode | gates |
| --- | ---: |
| XOR | 36,277 |
| AND | 3,306 |
| OR | 4,683 |
| total | 44,266 |

The allocator uses 773 registers and no spill or move. Output plane `j` is
written back to input register `j`. The next batch therefore starts without
loads, stores, moves, or complement operations.

The shipped experiment independently rebuilds the same 44,266 gates, opcode
counts, 773-register peak, 464,782 charged generator calls, mask `q`, and
packed recovery circuit. Its self-test compares 4,096 full-width lanes with a
scalar seven-round implementation, checks 4,096 lanes chained for seven steps,
executes the register-allocated line, and checks the 1,558-operation packed
recovery circuit.

## 4. Stage test, table, handlers, and recovery

### Stage test

A distinguished point has its low 32 bits all one. Every batch ANDs the lowest
12 planes. Eleven ANDs and a direct zero-test branch cost 12 operations. If the
result is zero, the batch ends. Otherwise the program ANDs the other 20 planes,
loads, decrements, stores, and checks the passing budget, loads and checks the
next scheduled main or slice limit, and branches on the hit mask. This costs
29 extra operations. The
passing-batch halt is

```
pmax = ceil((1 + 2^-10) B P12) + 64,
P12  = 1 - (1 - 2^-12)^256.
```

The loop's unconditional work is a load, batch-counter increment, store, and
backward branch. One main batch therefore costs
`44,266 + 12 + 4 = 44,282` operations.

### Split quotient filter

The table has `S = 128,232` slots and capacity 128,231. Each slot has a
32-bit key word: a 29-bit remainder and the quotient filter's occupied,
continuation, and shifted bits. A separate fixed-width stream packs one
17-bit trail number per slot. For a logical 52-bit key `z`, the stored code is
`z mod 2^45`; its high 16 bits select the quotient run and its low 29 bits are
the stored remainder. Lookup compares a remainder only inside that quotient's
run. Thus a displaced entry can never match a key from a different quotient.
Insertion uses the standard quotient-filter shift while preserving run order.

The largest reachable trail number is
`256 + 128,231 + 1 = 128,488 < 2^17`. The shipped self-test accepts the
largest 17-bit value, rejects `2^17`, and checks that one more table slot would
exceed the available bytes. The table occupies

```
32 ceil(S / 8) + 32 ceil(17 S / 256) = 785,440 bytes.
```

The two backing streams are word aligned: 16,029 key words and 8,516 trail
words. The last word of each stream is charged in full.

The valid distinguished-key space has `2^41 * 1968 = 4,327,677,766,926,336`
elements. There are `2^45` stored codes, and one code has at most
`ceil(2^52 / 2^45) = 128` numeric preimages. A union bound over stored pairs
therefore charges

```
C(128231, 2) * 128 / (2^41 * 1968) = 2.431687313604e-4
```

as the alias loss. On a code match, recovery recomputes both full endpoints;
an alias fails the attempt and is already covered by this term. A finished
trail is charged `2048 S` operations for the table, in addition to its
3,800-operation handler. Lookup and insertion each carry an explicit `8 S`
loop-body countdown and halt on exhaustion. One visit executes fewer than 128
primitive records even on a crossing 17-bit read and write, so `2 * 8 S * 128`
is a direct worst-case bound for lookup plus insertion. It covers loads, tests,
comparisons, branches, packed-key access, and a full insertion shift. The
program halts immediately when an insertion reaches capacity, so there are at
most 128,231 finished-trail handlers.

The compression effects were measured with the same conservative control
image and probability ledger:

| code and table layout | capacity | `time_log2` |
| --- | ---: | ---: |
| five-byte gates, seven-byte quotient filter | 105,877 | 124.910039899738 |
| four-byte gates, seven-byte quotient filter | 112,204 | 124.909736060611 |
| four-byte gates, split compressed quotient filter | 128,231 | 124.909684496472 |

The four-byte gate format saves 44,297 bytes and 0.000303839127 bit in the
seven-byte-filter comparison. The split table then adds 16,027 entries and
saves another 0.000051564139 bit after charging its 45-bit-code alias term.
For comparison, 2c5a749b's round-3 quotient filter has 124,634 slots; this
round-7 table holds 128,232 slots despite the larger seven-round image.

### Recovery

When two trail numbers have the same key, pass 1 stores both time-zero starts,
then walks them in two packed lanes. It checks the `c_r` cap before every
compression and stops when both reach distinguished points. Every
`D = ceil(c_r / 8192)` steps, it writes the current pair as a checkpoint. At
most 8,192 pairs use 524,288 bytes. Recovery reuses the table region, whose
785,440 bytes are no longer needed.

Let `A` be the longer trail, let `B` be the shorter, and let `d` be the length
difference. The predicate `A[j+d] = B[j]` changes from false to true once and
stays true. Pass 2 bisects the checkpoint indices. A probe loads two
checkpoints and walks `d mod D` steps. There are at most 16 single-lane walks
and one final joint walk, hence at most `17 D` packed batches. The final walk
returns the unequal predecessors of the first equal outputs.

Recovery rejects unequal endpoints, already-aligned starts, aliases, and an
equal predecessor pair. The bisection upper index is
`floor(short_length / D) + 1`, matching the stored time-zero checkpoint.

The packed circuit evaluates up to seven 36-bit-spaced scalar lanes in one
256-bit word. On this prefix and mask it has 1,558 word operations and 34
loaded constants. Its eight output registers permute its eight input registers,
so each call first snapshots all outputs into eight dead-step scratch registers,
then performs predicates and the parallel handoff from that snapshot. The
ledger charges 64 extra operations per pass-1 batch, 80
per checkpoint pair, 128 extra per pass-2 batch, 100 per probe, and 8,000 fixed
operations. The fixed term covers two explicit 256-iteration long divisions,
endpoint checks, selection, and bisection setup.

## 5. Exact work ledger

The organizer's reference cost for seven-round BLAKE3 is `C = 1470` word
operations per target-compression unit. The exact rows are:

| row | word operations |
| --- | ---: |
| main, `(B + 3000) * 44282` | 58,675,798,415,225,222,000,000,000,000,000,132,846,000 |
| passing-batch rest | 2,330,687,599,487,537,398,672,158,580,681,260,547 |
| slice checks | 18,830,071,961,005,501,179,900,000 |
| stage-1 hits | 442,282,658,419,466,018,676,757,812,679,200 |
| finished trails and quotient-filter work | 33,676,401,706,216 |
| one cut | 4,200 |
| checkpoint recovery | 54,455,620,342,458,525,396,273,689,660,060,455,424 |
| setup and runtime emitter | 195,579,600 |
| prefix choice | 64,692,944,896 |
| capacity and probability planner | 1,099,511,627,776 |
| total `N` | 58,732,585,165,449,845,312,332,925,565,340,669,003,859 |

The C ledger uses GMP integers for every row and checks

```
2^12490968 * 1470^100000 <= N^100000
N^100000 < 2^12490969 * 1470^100000.
```

Thus `124.90968 <= log2(N / 1470) < 124.90969`. The unrounded long-double
display is 124.909684496472, and the claim submits the certified upper endpoint
124.90969.

The runtime-emitter row is derived as
`200(2*464782+44266)+813600 = 195579600`. The two builds are the use-count and
emission passes. The fixed 813,600 operations are 256 initial inserts at 3,100
operations each, plus 20,000 operations for the fresh word, counters, and
reloads.

The planner compares six fixed layout and stage candidates. The optimized
planner uses bisection, while the independent C verifier also executes an
exhaustive `Tp` scan. Charging both paths gives at most
`6(4095+82) = 25062` loss evaluations. One loss evaluation scans 22,000 delay
bins and has fewer than `2^24` charged arithmetic operations. Capacity
bisections, field checks, and final constant construction fit in another
`2^37` operations. Therefore `25062*2^24 + 2^37 < 2^40`; the row charges the
fixed endpoint `2^40`. Each table-capacity computation uses at most 20 integer
bisection steps and is inside that allowance. Preprocessing is the sum of the
last three rows and has `log2(preprocessing/1470) = 29.561123632163`.

## 6. Random-function probability bound and premise H1

Let `n = 2^256`, `theta = 1968/2^122`, `L = 1/theta`,
`N' = n(1-theta)`, `Q = 256 B`, and `q = Q/L`. A lazy random function supplies
one independent uniform answer for each input not previously queried. Repeated
inputs reuse their first answer. Conditioning on a non-distinguished answer
leaves exactly `N'` possible values. These rules and the one fresh uniform
start `r` define the full probability space.

Put

```
Pi(m) = product(i=0..m-1, 1-i/N')
H     = Q(Q-1)/(2N')
p     = exp(-c theta)
p2(x) = exp(-(x-1) theta) (1 + (x-1) theta/(1-theta)).
```

Here `tmax = 128,231` is the table capacity (the split quotient filter above), `c = ceil(20 L)`,
`c_r = ceil(12.4 L)`, `S_b = 2^48`, and
`k = 128204` is the least integer satisfying
`exp(-q) (e q/k)^k <= 2^-40`. Set `n2 = k + 256 + 1` and
`s = 1/(1-kQ/N')`. The certificate encloses the random-mapping product by

```
Pi(m) <= exp(-m(m-1)/(2N')),
Pi(m) >= exp(-m(m-1)/(2N') - sum(i^2)/N'^2).
```

The lower enclosure follows from `ln(1-x) >= -x-x^2`; every encountered `x`
is below one half. The proof subtracts the following union bounds:

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
key_alias          = C(tmax,2) 128 / (2^41 Tp)
table_capacity     = exp(-q+t(1+ln(q/t))), t=tmax-59
finite_and_halts   = Q 2^17/N' + k^2 L/N' + 255 Q/N'
                     + exp(-300+(e^5-1)(C(Q,2)+2^17 Q)/N') + 2^-90.
```

The factor 128 is `ceil(2^52/2^45)` for the split table code. Outside the
event of 60 or more collisions, which is part of `finite_and_halts`, the
number of finished trails is at most `N1+59`, where
`N1 ~ Binomial(Q,theta)`. Filling capacity 128,231 therefore requires
`N1 >= 128172`. The binomial Chernoff formula above is evaluated at that exact
threshold. This derives the capacity term instead of importing a chosen
capacity mean.

The delay sum uses 2,000 integer bins before the final 120 mean trail lengths
and 20,000 integer bins in that final interval. Every bin uses the product
endpoint and batch ceiling that increase the loss. Geometric tails give the
partner, age, recovery, cut, and disturbance bounds. The final row covers the
finite-domain start events, 60 or more collisions, stage and passing-budget
tails, recovery failure not already counted as an alias, delayed limit checks,
and rounding slack.

The certificate starts from exact integers and rational numbers, evaluates
transcendentals with 90 decimal digits, and moves every upper result outward by
`abs(x)*1e-60 + 1e-85`; lower results move outward in the other direction. The
individual directed upper endpoints are:

| loss | directed upper endpoint |
| --- | ---: |
| no collision | 0.608437762084547866501348377669060322227929024120476241364362757762291704312152937025165717 |
| detection delay | 0.00123644961451861652640266442944312732655880254312658905031485732111703404334813323333315673 |
| same-trail partner | 0.00000791456832272465524167209065492041763507065653456427694425647354825389009995710150116226720 |
| long partner | 4.10477687309398893933355879499876556973829891074316762064537221752513843992704046275044462E-8 |
| age cap | 2.15062288158647027146049434047498965337441074117800244673392818186598713753756226914750088E-8 |
| recovery cap | 0.0000548425732440963786891638494067862184284345327387622479323393619524567894114394535167971409 |
| second collision | 0.00000393243758239510142782259066525831089899301587205121469994646952842389443884695561870886783 |
| finished count | 9.094947017729282379150390625000000000000000000000000000000009094947017730282379150390625E-13 |
| cut and disturbance | 0.0000158664323065346961591204717888867121073024508922894270145820141127312768232145292008814204 |
| key alias | 0.000243168731360380136506344244732120172764227642276422764227642276422764227642276422764227643 |
| table capacity | 1.75966400311827160148610175000707038992532165647078980488505200297354147109502110586591311E-12 |
| finite domain, halts, and rounding | 8.07794335162246530766734873764452325881642906671196915204461941678910696429386276629535756E-28 |

Their directed-rounded sum is

```
0.609999998998549319505258473933478252098627687245673634978120781158504320478157243074287104
```

and therefore

```
P_F >= 0.390000001001450680494741526066521747901372312754326365021878828841494678071162262184086829 > 0.39.
```

H1 is the score-critical premise that the fixed walk `g` succeeds at least as
often as this lazy-random-function program. It grants the collision law and
distinguished membership only for this fixed family and bounded attempt. H1 is
declared, not proved, and no experiment supplies a probability used in the
score.

## 7. Machine convention and memory

H3 declares a classical 256-bit load/store word RAM with 775 addressable
registers. A conditional branch may test whether a register is zero. The
benchmark prices word operations but does not prescribe a register count,
instruction encoding, or branch encoding, so these are explicit supporting
assumptions.

The shipped emitter assembles symbolic labels and virtual temporaries into
numeric branch targets and registers, then prints the complete static image and
its SHA-256. The control image contains primitive loop bodies for setup, all
256 lane insertions, cut and slice handling, quotient-run discovery, crossing
17-bit loads and stores, insertion shifting, checkpoint creation, two long
divisions, bisection, and the final joint walk. There are no aggregate
`SHIFT_RUN`, `BISECT`, extraction, or packed-field opcodes. All organizer
experiments invoke this emitter and assert its byte and record census before
running trials. The census is:

| record kind | count | bytes each | bytes |
| --- | ---: | ---: | ---: |
| step and stage XOR/AND/OR records | 44,297 | 4 | 177,188 |
| packed-recovery records | 1,558 | 5 | 7,790 |
| conservative control records | 1,335 | 36 | 48,060 |
| total | 47,190 |  | 233,038 |

The gate format is the machine's native instruction format: a two-bit opcode
and three 10-bit register fields, exactly 32 bits. The priced step fetches and
executes those records directly. It has no decoder, interpreter, expanded
stream, or decode buffer in any priced path. The Python record reader is a
test-only byte-exact mirror used by organizer experiments; it is not the
declared machine. Packed recovery uses an eight-bit opcode and three 10-bit
fields in five bytes. Every control record is charged a conservative 36 bytes, enough
for an opcode, operands, and a 256-bit immediate even when that particular
record has no immediate. The step's dead intermediate registers are reused only
as scratch by the controls; persistent random, counter, budget, and limit state
is explicitly loaded from and stored to memory. The assembler checks that every
assigned register is below 775. Handlers address the register file, so they do
not allocate an 8 KiB plane copy. Of the 1,335 control records, 300 are
unreachable padding: they consume code memory but never cost an operation.

Search memory is:

| object | bytes |
| --- | ---: |
| static image | 233,038 |
| 775 registers | 24,800 |
| packed lane metadata and persistent state | 5,248 |
| prefix advice | 32 |
| 128,232 key words and packed trail fields | 785,440 |
| total | 1,048,558 |

The 5,248-byte metadata region is exactly 544 bytes for 256 fixed 17-bit trail
numbers, 4,096 bytes for 256 fixed 128-bit birth batches, and 608 bytes for 19
word-aligned state or padding words. The emitted load/store routines implement
both packed lane fields. The total is 18 bytes below 2^20. Every packed-field boundary is asserted by
the shipped plan.

During setup, the table and search registers do not coexist with the runtime
emitter. Setup holds the 233,038-byte image, 5,248 bytes of counters, 32 bytes
of advice, an 86,400-byte emitter image, and 49,296 bytes of emitter stack and
scratch. The setup peak is 374,014 bytes. The search peak is therefore the
claimed peak. `memory_log2_bytes = 20`, so the scalar memory term is zero.

## 8. Experiments, limits, and credit

`experiments/bsrho.py` is the shipped emitter and experiment program. Before
every request it rebuilds and checks the static image and executes the packed
field boundary test. `bsrho-n18` runs one reduced-width attempt with the
all-ones predicate, split AND test, split quotient filter, and checkpoint
recovery. `proj-prefix-w256` evaluates 2,048 full-width points with the shipped
44,266-gate circuit. The organizer independently checks every returned pair.

`h1-law-n20` commits its statistic and null before the organizer supplies a
holdout nonce. All request seeds select one coordinate injection, one fixed
assignment of the other 236 input bits, one 20-coordinate output projection,
and one output XOR constant. This defines one fixed 20-bit restriction `h` of
the shipped walk. Sixty-four groups iterate that same `h` for at most 1,200
steps. Per-group visited sets retain merges and shared tails. A single global
set records evaluated inputs, and the scaled distinguished event, low four
output bits all one, is counted only the first time an input enters that set.

The null has 64 complete ensembles. Each ensemble has one shared lazy random
mapping on `2^20` points, 64 uniform starts, 64 per-group visited sets, one
global mapping dictionary, and the same censoring rule. The first 32 ensembles
fit the means and sample variances of four first-collision bins: at most 400,
401 through 700, 701 through 1,000, and later or censored. The other 32
ensembles calibrate the Pearson-style score. Its limit is 1.25 times the
largest calibration score. The distinguished z-score limit is the larger of
4 and 1.25 times the largest calibration magnitude. Every result exports the
four bins, score and limit, z-score and limit, globally fresh input count,
distinguished hit count, fit and calibration sizes, and `law_pass`.

A genuine holdout requires the organizer to choose an unpredictable nonce
after the package and experiment source are fixed. Public intake seeds check
reproducibility, not holdout validity. The experiment tests reduced-width
consistency with a shared random mapping. It does not prove H1, observe the
256-bit graph, or justify extrapolation to the full attempt.

The construction depends on these public Pareto entries:

- 11d961ad-d526-4279-8295-382cff99088b is the direct round-7 base and supplies
  the mask-0x10 exact columns, independent C validation pattern, and complete
  package lineage.
- f88f3751-f08b-4561-a764-a04b5f7a899a and
  10ce9f59-80a1-4304-92cc-ca4dede3bbcc supply the pair-carry column family.
- 2c5a749b-e0db-4420-85fd-7b9b987efc33 supplies the charged fixed-prefix
  method, split-stage idea, seven-byte quotient filter, and checkpoint recovery.
- 25a6d43b-5253-4ac4-9f43-3fff24c8a927 supplies the all-ones stage test,
  late-limit check, addressable-register handlers, 775-register convention,
  and 5,248-byte counter layout.
- b9f7a2bc-2ba7-4a34-a4c0-8efa7527fba1 supplies the complete birthday search,
  first-collision proof structure, mask walk, emitter, and experiment design.
- 6ae36351-5836-4a46-ad34-227688264123 supplies the pivot full adder and fixed
  mask walk. 09fe5fcd-5614-4329-8b7d-48957c238fac and
  b1e6de75-6ea4-4946-82ad-addc9a6b909e supply earlier table and key layouts.

The dependency manifest records the rest of the retained lineage. The program
and proof here restate the complete target, algorithm, operation count, memory
layout, random-function probability space, H1, and H3. No claim depends on a
reader retrieving a prior package.

The limits are plain. H1 is unproved. H3 is a declared machine convention. The
success bound has little margin above 0.39. The experiments cannot inspect the
full functional graph or trails of length near `L`. None of those limitations
changes the fact that this is a generic birthday construction, not a claim
about a weakness in full BLAKE3.
