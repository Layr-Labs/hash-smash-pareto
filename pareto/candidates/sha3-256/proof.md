# SHA3-256, 24 rounds: a collision search that never cuts a trail, with a replay cap and an integrated detection-delay bound

| quantity | value |
|---|---|
| target | `sha3-256-r24-prefix-v1`; 24 is the complete Keccak-f[1600] round count, so this is the full SHA3-256 |
| attack class | ordinary collision, exploratory lane |
| time_log2 | **124.50790** target compressions (reference cost 6504 word operations each) |
| memory_log2_bytes | **19.93114** (999,697 bytes, below `2^20`, so the memory term of the objective is zero) |
| success probability | **0.39**; the certified random-function lower bound is 0.390000081356 (margin 8.1356E-8) |
| normalized objective | **124.50790** |
| preprocessing | charged inside the time: 375,368,283,586,560 word operations, `preprocessing_log2 = 36`: the inherited generator run that produced the blocks at the 93,893,306,875,904 its entry declares, plus a ceiling of `2^48` over every computation of ours that selected this program's constants, compared the designs or validated the program (Section 9). No table, no advice |
| step program | 147,303 operations for 256 walks, **inherited** (Section 3.4), plus 2 for the inline `KERNEL` headers our encoding traverses: 147,305 charged, 575.41 per evaluation |

Everything below is self-contained: the algorithm, the declared machine, the complete ledger, the success
bound with its rounding discipline, and the one heuristic this entry declares. Section 10 credits every
component that is not ours.

## 1. The target, the message encoding and the walk

### 1.1 The two messages

A point `u` is 256 bits, read as four little-endian 64-bit lanes `u_0..u_3`. The message is the 128-byte
`m(u)`: of the sixteen rate lanes of the first block, lane 1 is `u_0`, lane 6 is `u_1`, lane 4 is `u_2`,
lane 9 is `u_3`, lane 11 is `u_0 XOR u_1 XOR K11`, lane 14 is `u_2 XOR u_3 XOR K14`, and the remaining ten
lanes are the fixed public constants `K` of the program text. Padding makes lane 16 of the absorbed state
`0x8000000000000006`. The map `u -> m(u)` is injective, because lanes 1, 6, 4 and 9 are `u` itself, so two
different points give two different messages.

The six variable lanes are placed exactly as in the linear structure of Guo, Liu and Song: round 0 and the
theta step of round 1 are affine in `u`, which is what makes the step program short.

### 1.2 The walk

    f(u) = SHA3-256_r24(m(u)) XOR PD,     PD = 0x04020A1A40041022CEA2083A40671126EBA5262001EB0544B15DF5C53F986ED1

`PD` is the polarity of the program's digest planes (Section M.1): the physical words the step program leaves
in registers 0..255 are the planes of `f(u)`, so the next point needs no copy and no complement. Plane `j` of
a value is bit `j` of the digest read as a little-endian integer. Since the same `PD` is XORed into both
points of a pair, `f(a) = f(b)` with `a != b` gives two distinct messages with equal complete 24-round
SHA3-256 digests, which is a collision for the target.

**Lemma 0.** `f` is a bijective relabelling of the digest map composed with an injection on messages, so a
collision of `f` is a collision of the target, and the random-function model of Section P is applied to `f`
itself, not to a truncation.

## 2. The frozen algorithm

### 2.1 Parameters

| symbol | value | meaning |
|---|---|---|
| lanes | 256 | walks advanced in lockstep, one plane bit each |
| `theta` | `1/2^112` = `2^-112` exactly | a point is distinguished when its low 112 planes are zero; no window test is needed, because the density this candidate wants is a power of two |
| `L` | `2^112` | mean trail length, `1/theta` |
| `LRC` | 54,519,117,014,615,690,099,570,211,456,811,008 = **10.5 L** | replay cap: the recovery refuses a stored trail longer than this |
| age cap | **none** | no trail is ever cut; the program has no age cap and no cut scan |
| `U` | 67,456 | trails startable in one attempt; the table holds `ceil(U/4)` words of four records |
| key | 47 bits | a record is the 47 planes from plane 116 upward in bits 0..46 and the trail identifier in bits 47..63; the table is filled contiguously, so no marker bit is needed and the key keeps all 47 bits at a capacity above 65,536 |
| `B` | 1,327,649,770,787,631,727,298,943,664,789,651,456 = `2^119.998286` = `1,047,331 x 2^100` | horizon, batches of 256 evaluations: the **least** multiple of `2^100` this bound certifies at 0.39 (one grid step down fails, which `tools/verify_snapshot_c9.py` checks by recomputing the bound there). Its margin over 0.39 is 8.1356E-8; that margin is headroom over the rounding discipline of Section P, which already rounds every term against the bound, and not a buffer against the heuristic H1 of Section H, which no margin of this size addresses. Nothing is spent on margin |
| `Q` | `2^127.998286` | evaluations of `f` in one attempt, `256 B` |
| `IDL` | 131,072 = `2^17` | start identifiers reserved, which is why the identifier field is 17 bits; at most 67,712 are used |
| `E2MAX` | 2,532,290,975,165,618,376,348,388,032,512 = `32 Q/2^32` | stage-2 budget, enforced by a halt (Section P.3) |

### 2.2 State

In registers: the 256 input planes (registers 0..255), the two 1,600-plane banks and the scratch of the
inherited step (up to register 3,524), then the step counter, the next trail number, the offset
`rho`, the stage-2 counter, the link register of the body calls, the scratch and the control constants;
48 registers beyond the step's 3,525, a declared file of 3,573. In memory: `ceil(U/4)` table words of four records, and the birth batch and trail
identifier of each of the 256 lanes; 17,376 words in all.

### 2.3 Control flow

Setup loads the constants, draws `rho` uniformly, clears the table and the lane metadata, and starts lane `l`
at `rho + l`. Each batch then runs the step program once, which advances all 256 walks, and performs a
two-stage distinguished test:

* **stage 1**, every batch: the low 32 planes are OR-ed together; if some lane has them all zero the batch is
  a stage-1 hit and enters stage 2. This costs 37 operations beyond the step.
* **stage 2**, only on a hit: the counter is incremented and compared with `E2MAX` (a halt if it is reached),
  and the remaining planes up to 112 are folded in. 85 operations, or 86
  when no lane survives.

A lane whose output is distinguished has its key looked up in the table. On a miss the record is inserted and
the lane restarts at the next identifier; on a match the recovery of Section 2.4 runs once and the attempt
ends. **No trail is ever cut**: a lane keeps walking until it is distinguished or the horizon ends the
attempt, which is why there is no age cap in the parameters and no cut scan in the program.

### 2.4 Recovery (at most once)

With a key match between the stored trail `a` and the live trail `b`, the recovery first **refuses the pair if
the live trail's age has reached `LRC`** (a single comparison, before any walking), then walks `a` from its
start, counting, to its distinguished endpoint, **refusing it if `a` does not reach that endpoint within `LRC`
steps**; so an accepted pair has stored length at most `LRC` and live age at most `LRC - 1`, and both walks are
bounded by `LRC`, which is what the ledger's recovery row and `H = 3 LRC + 2` charge. It then checks that the
endpoint is the one stored;
advance the longer trail until both have the same remaining length; then advance both in lock step until their
images agree; the two points before that agreement are the collision. The walk uses the same step program at
width one through the compression unit, so each step is charged one target compression.

### 2.5 Termination codes

1 a recovered pair; 2 the stored endpoint is not reached from its start; 3 the two trails already agree at the
first compared point; 4 the table is full; 5 no start identifier is left; 6 the horizon ends the attempt;
8 either replay guard refuses (the live age has reached `LRC`, or the stored trail does not reach its endpoint within `LRC`), or the paired walk finds no agreement; 9 the stage-2 budget is
exhausted. Only code 1 is a success; Section P charges every other code.

## 3. The declared machine

### 3.1 Word RAM with a declared register file

Values are 256-bit words. The machine has a declared file of 3,573 registers, whose
114,336 bytes are inside the memory bound. An instruction on registers costs its base operations;
loads and stores to computed addresses are charged; one `COMP` is one evaluation of the target compression and
is charged the reference cost 6504 word operations plus 64 for block assembly. This is the convention of our
entries `09fe5fcd` and `55783d22` and of the comparator.

Two instructions are added to the set those entries declare, because the step of Section 3.4 is a cycle of
shared bodies rather than a straight line: `JAL r, t` writes the address of the following instruction into
register `r` and jumps to the absolute byte offset `t`, and `JR r` jumps to the address in `r`. Each costs one
operation, so a call and its return cost two, exactly as the comparator charges them.

### 3.2 Program image

The image is 327,153 bytes:

| region | bytes |
|---|---:|
| 60,733 three-operand step words of 5 bytes (the ten blocks) | 303,665 |
| 10 `KERNEL` headers of 8 bytes, one per stored block | 80 |
| 29 calls and returns of 8 bytes (21 `JAL`, 8 `JR`) | 232 |
| 78 iota XORs of 8 bytes, as control words | 624 |
| 2,734 control instructions of 8 bytes | 21,872 |
| 17 constant loads of 40 bytes | 680 |
| **total** | **327,153** |

Register fields are 12 bits, which 3,573 registers require; immediates are 20 bits, which the largest
address in this image (292,625, a call target) and the largest memory word index both fit.
The experiment serializes the program, decodes it again, asserts the round trip, the byte count, every block
word, every iota group, every call target and every return, and executes **the decoded image**.

### 3.4 The step, which is inherited

The step is **not ours**. It is the step of `c9a7e62c` (mitchuski), which builds on Jbenisek's `71fefe66` and
`0bd0022d` and on jungjipdo's `67f781f8`: generic rounds 2..22 run a cycle of eight shared bodies, round `r`
executing body `(r-2) mod 8 + 1`, so bodies 1..5 run three times and 6..8 twice, with a prefix block `P` for
rounds 0 and 1 and a closing block `E` for the last round. Ten blocks are stored instead of twenty-four
unrolled rounds, which is what makes the code image small enough for a 67,456-trail table.

The blocks are rebuilt inside the experiment from the generator decisions their entry publishes, and the
program **refuses to run** unless each of the ten hashes to the SHA-256 that their proof prints for the
generator's file and has its published length. The round constant of a generic round is applied as an XOR of
the all-ones register into the set planes of the body's output bank, which flips those planes' value and
leaves the stored polarity unchanged, so the same eight bodies serve all twenty-one rounds. Per batch the step
executes 147,303 operations: `P`, then for each generic round a `JAL` into its body, the body, its `JR`
and the round's iota XORs, then `E`. Our encoding adds 2 operations per batch, one for each inline
`KERNEL` header the batch traverses, which is `P`'s and `E`'s; a body entry traverses none, because the call
targets the body's first word, and the iota XORs are control words rather than kernel words, so no header
stands between the body calls. Those 8-byte words cost 66 bytes more than 5-byte words behind 21 further
headers would and save those 21 traversals in every batch. The charged step is therefore 147,305
operations. Section 10 credits the step in full.

## M. The machine program

### M.1 The kernel

One batch advances all 256 walks: bit `t` of a word is lane `t`, and the step of Section 3.4 leaves the
planes of `f(u)` in registers 0..255, over the input planes they replace, so the next point needs no copy and
no complement. The step is inherited; what is ours is that it is carried in our declared encoding, called as
21 calls into eight stored bodies, and that the bytes are proved to be the published
blocks: the experiment rebuilds the ten blocks from the published decisions, refuses any block whose SHA-256
or length differs from the figure their proof prints, converts each word into our register-only kernel form
(their opcode 3, "`d` is `a` complemented", is our `XOR d, a, KONES` against the all-ones register the blocks
read), encodes the image, decodes it again, and executes the decoded words. Each trial also recomputes four
seed-chosen lanes of a full-width random batch and of the projected run against the library `SHA3-256` of
`m(u)`, so a wrong word, a wrong call target or a wrong execution order would be caught by the digest and not
only by the hashes.

### M.2 Main loop, stage 2 and the handlers

The emitted regions are setup, the kernel, the stage-1 test and loop control, stage 2, the endpoint scan, key
extraction, the table scan and insertion, the restart, the recovery and the terminal handler. There is no cut
region. Each handler's cost is a closed form in the parameters (Section L.2), and the experiment's probes
assert that the measured cost of each equals its closed form at these parameters.

### M.3 Storage layout

Table words `0..ceil(U/4)-1` hold four 64-bit records each: a trail identifier and 47 key bits.
Then 256 birth batches and 256 trail identifiers. 17,376 words,
556,032 bytes.

### M.4 The fixed image is the algorithm

The claim is about this image and no other. The experiment asserts the kernel's operation count
(147,305) and its 60,733 stored words, the SHA-256 and length of every one of the ten blocks,
and its output polarity (`PD`), then builds the full program, asserts that the image is exactly
327,153 bytes and that
decoding reproduces it, and runs the decoded program.

## L. The resource ledger

### L.1 Worst-case event counts

| event | bound | why |
|---|---:|---|
| batches | 1,327,649,770,787,631,727,298,943,664,789,651,456 | the horizon |
| stage-2 batches | 2,532,290,975,165,618,376,348,388,032,512 | the counted budget, enforced by a halt |
| endpoint handlers | 67,457 | one per insertion, plus the one that fills the table |
| restarts | 67,456 | one per insertion |
| trails cut | **0** | nothing cuts a trail |
| recovery | once | the attempt ends with it |
| identifiers used | 67,712 | 256 starts and at most `U` restarts, below `IDL` |

### L.2 Word-operation terms (exact integers)

| term | operations |
|---|---:|
| setup | 401,559 |
| main batches, `B x (147,305 + 37)` | 195,618,572,527,391,233,963,680,957,457,436,824,829,952 |
| stage-2 batches, `E2MAX x 86 + 3` | 217,777,023,864,243,180,365,961,370,796,035 |
| endpoint-batch lane scans, `(U+1) x 1,795` | 121,085,315 |
| key extraction, `(U+1) x 189` | 12,749,373 |
| table scans and insertions | 29,577,938,240 |
| terminal handler | 876,933 |
| endpoint restarts, `U x 1293` | 87,220,608 |
| recovery, `1,048 + 268 + (72 + 138) LRC - 138` | 11,449,014,573,069,294,920,909,744,405,930,312,858 |
| output and halt | 3 |
| preprocessing: the inherited generator run `gen4 4096 0 3` (93,893,306,875,904) and a `2^48` ceiling over our own selection, comparison and validation computation | 375,368,283,586,560 |
| **W, total word operations** | **195,630,021,759,741,327,122,845,047,943,202,209,797,436** |

### L.3 Total time

The recovery's compressions are charged separately as target compressions:
`H = 3 LRC + 2 = 163,557,351,043,847,070,298,710,634,370,433,026`, because the measuring walk, the alignment and the paired
walk are each at most `LRC` steps. With the reference cost `C = 6504` word operations per compression,

    T = W / C + H,     log2 T = 124.507891822327,     claimed **124.50790**

The main loop is 99.453 percent of `T`; the recovery is the
remainder, and everything else is below `1e-9` of it.

### L.4 Memory

| region | bytes |
|---|---:|
| program image (declared encoding) | 327,153 |
| register file, 3,573 words of 32 bytes | 114,336 |
| table, lane births and identifiers | 556,032 |
| compression working state | 2,048 |
| output area (the two colliding points; the messages are `m(u)` of the two points and are not stored) | 128 |
| **total** | **999,697** |

`log2 999,697 = 19.931131366487`, claimed 19.93114, which is below 20,
so the memory term of the objective is zero and the normalized score equals the time:
**124.50790**. The margin to `2^20` is 48,879 bytes.

### L.5 What is asserted by execution, and by whom

Organizer-executed, inside the pinned isolated executor, on the exact submitted bytes: the rebuild of the
ten inherited blocks and their hash gate, the image round trip with every block word, iota group, call target
and return, the deployed constants and the record packing read back from the image, the 14 fixtures, the
handler probes, the projected end-to-end runs with their agreement against the scalar reference, the sampled
lane checks against the library SHA3-256, and the exact success bound (experiment
`sha3-256-r24-looped-bound-v1`). Author-run only, and reported as such: the inherited generator run that
produced the blocks, and the administrative tools that recompute this ledger and this bound outside the
executor.
Nothing in this ledger depends on an author-run measurement: every count in L.2 is a closed form that the
organizer-executed probes check against the emitted program.

### L.6 Sensitivity

Instruction fetch is not charged as a primitive operation. Charging it at one 256-bit load per 32 bytes
**traversed** is the figure that matters for a looped step, and it is not the image size: a batch traverses
736,891 bytes of code, because each of the eight bodies is fetched as often as it is
called, two or three times. That is `23,028` loads in each of the `B` batches,
which raises `T = W/C + H` by 0.20844 bits to
124.71633 (the loads are charged to the batches only,
so the recovery's compressions dilute them). Pricing the image once per batch instead, as an unrolled program
would, would understate this convention by about 0.112 bits, so that weaker figure is not used here. The
comparator declares the same uncharged-fetch convention and runs the same looped step, so a comparison under
the alternative convention would reprice both sides alike; this entry's advantage is stated under the
declared convention and the comparator's.

## P. Success probability in the random-function model

Model `f` as a uniform random function on 256-bit values, sampled lazily. The distinguished indicator is the
stated function of the value, so the program's two-stage test is exactly the nesting "stage-1 hit" contains
"distinguished"; the lottery coupling is used only where a trail length is needed, to separate the geometric
age from the value. `Pi_m` is the probability that the first `m` evaluations produce no plain duplicate. All losses are summed and subtracted once; the certified value is the result.

**Rounding discipline.** Every transcendental is a 60-digit decimal rounded in the direction that weakens the
bound (losses up, the result down), every other quantity is an exact rational, and the final value is
truncated downward at twelve places. The declared experiment `sha3-256-r24-looped-bound-v1` recomputes it inside the
organizer's executor from the frozen parameters; `tools/check_success_bound_c9.py` runs the same arithmetic
outside, and the two agree.

### P.1 The loss terms

| term | value | what it charges |
|---|---:|---|
| no plain duplicate | 0.607250808101 | the run produces no plain collision at all |
| detection delay | 0.002378057855 | the earlier trail of the first colliding pair needs more than the remaining batches to reach its endpoint, integrated over the first-collision distribution in 22000 bins |
| own trail | 0.000015240672 | the collision lands on the trail's own path |
| **replay refusal** | 0.000315917636 | the colliding pair is refused by either guard of Section 2.4. The live guard is the weaker of the two thresholds, so the term is charged at `LRC - 1`: `Q(Q-1)/N x (1-theta)^(LRC-1) x (1 + (LRC-1) theta)`, the age-weighted geometric tail. This term replaces the cut-trail losses of an age-capped design |
| disturbed suffix | 0.000007602252 | a later collision disturbs the suffix before detection |
| same-batch pair | 1E-12 | the pair occurs inside one batch |
| start hit | 1E-12 | an output equals a reserved start |
| distinguished-class duplicate | 1E-12 | two distinguished values coincide |
| count tail | 1E-12 | more than 67,373 distinguished values occur, which is also what keeps the table from overflowing |
| false key | 0.000032292129 | two different endpoints share their 47 key bits |
| stage-2 budget and rounding | 1E-12 | the budget halt of P.3, plus the rounding allowance |
| **loss sum** | **0.609999918644** | each row above is rounded up independently, so the column adds to slightly more than this sum; the certified value is the one the executor computes, and rows below `1e-12` are displayed as `1E-12` (the stage-2 row is `2^-90`) |
| **certified lower bound** | **0.390000081356** | margin 8.1356E-8 over 0.39 |

The expected number of distinguished values is 65458.1875, and 67,373 is the
least count whose tail is below `2^-40`; it is below `U = 67,456`, which is how the capacity is
justified: the table overflows only on that same `2^-40` event.

### P.2 Why the cut-trail terms are absent

An age-capped design charges two further losses: that an earlier trail was cut before its endpoint was stored,
and that the later trail's age exceeded the cap. Neither event exists here, because nothing cuts a trail. What
replaces them is the replay refusal above, in the form of the comparator's term F6: the pairs of evaluations
weighted by the geometric tail of the trail length, `Q(Q-1)/N x (1-theta)^LRC x (1 + LRC theta)`.

### P.3 Step 5: the stage-2 budget for a design that never cuts

This step is **re-derived for this program**, not inherited. In an age-capped design a merged trail re-outputs
stored values for at most `R` evaluations; here it is never cut, so it can follow a stored path, or loop a
stored cycle, until the **horizon**. That changes the arithmetic materially and is why the budget is
`32 Q/2^32` rather than the `3 Q/2^32` of our age-capped entries.

Write `mu = Q/2^32` for the mean number of batches in which some lane's low 32 planes are zero. Work outside
the start-hit and key-match events and on the event that the certified count holds.

1. **Fresh evaluations.** Each fresh plain output has its low 32 planes zero with conditional probability at
   most `2^-32` given the past, so the number of such batches is dominated by a binomial and exceeds `2 mu`
   with probability at most `e^(-mu/3)`, which is below `2^-(10^28)`.
2. **How many trails are merged.** Each fresh plain evaluation is a collision with conditional probability at
   most `(t-1+IDL)/N'`, so the number of plain collisions exceeds 60 with probability at most
   `exp(-120 + (e^2-1) Hs)` with `Hs = (Q(Q-1)/2 + IDL Q)/N' = 0.507986`, which is `2^-168.44`. A trail
   becomes non-fresh only by a collision on it, so at most 60 trails are merged, each for at most `B` further
   evaluations.
3. **Acyclic part.** For a fixed value the iterates before the first repeat are independent and uniform, so
   the distinct values on a merged trail's path carry at most `2 B/2^32` such batches except with probability
   `N e^(-B/(3 x 2^32))`; a union over all `2^256` values makes this hold for every stored path at once,
   whichever one the run selects, and the distinguished endpoint a merged trail may repeat is a key match that
   ends the run, so it costs at most one. The allowance is `60(2 B/2^32 + 1) = 2^94.92`, which is 0.469 of
   `mu` — against 0.018 in the age-capped design, the whole difference being `B` in place of `R`.
4. **Cyclic part.** A merged trail re-outputs a value only if the stored graph has a cycle, and a cycle of
   length `c` closes only at a fresh slot whose output is a stored vertex at distance `c-1` above its input.
   Before that slot the ancestors of its input form an in-tree whose leaves are starts, so there are at most
   `1 + collisions <= 61` such vertices, each with conditional probability at most `1/N'`. The `c` cycle
   values are stored before the slot, so their hit count is history-measurable; conditioning on the coins and
   on the equality pattern of the run, the distinct plain values are a uniform injection into the plain class,
   so any `h` specified ones are all hits with probability at most `2^-32h`. A trail on a cycle of length `c`
   makes at most `B/c` passes beyond the one counted in step 3. With the slack
   `tau = (30 mu - k - 60(2B/2^32 + 1))/60 = 2^94.99` per trail, summing over at most `Q` slots and over
   `c <= B`,

       P(some cycling trail exceeds tau) <= 61 (Q/N') sum_(c<=B) P(Bin(c, 2^-32) >= ceil(tau c/(B+c))) = 2^-104.91

   using the Chernoff tail `exp(-(h ln(h/lam) - h + lam))` for `h > lam = c 2^-32`. (The Poisson term bound
   `lam^h/h!` is vacuous where `h` is close to `lam` and must not be used here.)
5. **Total.** The batches counted are at most `2 mu` fresh, `k-1` for the distinguished batches allowed by
   the count tail of P.1 (already inside the fresh count under the nesting above, so this is an allowance
   added twice over), and
   `60(2B/2^32 + 1) + 60 tau = 30 mu - k` non-fresh: at most `32 mu = E2MAX`, so the halt does not occur,
   except with probability at most `e^(-mu/3) + 2^-168.44 + N e^(-B/(3 x 2^32)) + 2^-104.91 < 2^-104`, below
   the `2^-90` charged in P.1. **The headroom in this step is about 14.9 bits**, and it is headroom in the
   stage-2 failure budget only: it is not the success-probability margin of P.1 (which is
   8.1356E-8), and it says nothing about the H1 transfer of Section H.

At the inherited budget of `3 Q/2^32` the same derivation gives `2^-90.14` against the charged `2^-90`, a
margin of 0.1 bits, which is why the budget is larger here. The cost of the larger budget is the stage-2 row
of L.2, 217,777,023,864,243,180,365,961,370,796,035 operations, about `1e-9` of `W`.

## H. The fixed-target heuristic H1

**H1.** For the fixed walk `f(u) = SHA3-256_r24(m(u)) XOR PD`, the success probability of this frozen program
over its uniform offset `rho` is at least the random-function bound of Section P, and in particular at least
0.39.

This is the one score-critical heuristic and it is **not proved**. The algorithm is generic: it uses no
property of SHA3-256 beyond the embedding of Section 1.1, which keeps round 0 affine and is a property of the
message layout rather than of the permutation. What the declared experiments provide is implementation and
cost evidence and the exact recomputation of the bound; they are **not** evidence that the transfer holds, and
no coverage, confidence or calibration claim is made for them. A reviewer who rejects H1 should reject the
success probability, and with it the entry.

## 8. Declared experiments

| id | what it does |
|---|---|
| `sha3-256-r24-looped-machine-v1` | rebuilds the ten inherited blocks from the published decisions and refuses any whose SHA-256 or length differs; asserts the step's geometry (60,733 words, 10 headers, 29 calls and returns, 147,305 operations); serializes and decodes the image, asserting the round trip, the byte count, every block word, every iota group, every call target and every return; checks the deployed constants and the record packing read back from the image; runs the 14 fixtures and the handler probes; and per trial runs a 16-bit projected search with the complete program and with the scalar reference, requiring agreement on every outcome field, plus sampled lane checks and a full-width random batch against the library SHA3-256 |
| `sha3-256-r24-looped-bound-v1` | recomputes the exact bound of Section P from the frozen parameters in 60-digit decimals and reports its terms |

Both declare the same program file, `experiments/sha3_machine.py`. Its 65,531 bytes are the whole declared
experiment source, inside the 65,536-byte review budget.

## 9. Heuristics and limitations

* H1 above is score-critical and unproved.
* No collision is exhibited and the attack is not run at full scale; `B` is `2^120.00`.
* The time and memory are worst-case bounds for the fixed image under the declared machine of Section 3, not
  measurements of a run.
* Instruction fetch is uncharged; Section L.6 gives the repriced figure.
* **Preprocessing is charged in two parts** (`tools/preprocessing_c9.py` itemises both). First, the step's
  blocks are the output of a generator run that is **not ours**: the run `gen4 4096 0 3` that `c9a7e62c`
  declares, whose decisions that entry publishes and whose blocks this program rebuilds and hash-checks; it is
  charged at the 93,893,306,875,904 word operations that entry declares for it, because inheriting a
  precomputed artifact does not make producing it free. Second, **our own computation for this candidate**:
  the constants in the program (density, capacity, replay cap, horizon, stage-2 budget) were chosen by
  evaluating the success bound over a grid and certifying the chosen point exactly, the decision to carry the
  inherited step came from a priced comparison, and the program was validated by repeated executor runs. All
  of that is computation whose output is embedded in the program, so the cost model reaches it whether it is
  called search or arithmetic; it is charged at a ceiling of `2^48` word operations over itemised upper bounds
  (parameter scan, exact certifications, the comparison and its certificates, the earlier pricing scans, and
  up to 64 validation runs, and **our own abandoned kernel searches**, which the rule's "failed trials" reaches
  and which an earlier revision of this itemisation omitted while claiming completeness). The two parts sum to
  375,368,283,586,560, `2^48.42` word operations. The declared field is
  in the same unit as `time_log2`, target compressions, so
  `preprocessing_log2 = ceil(log2(375,368,283,586,560 / 6504)) = 36`,
  the comparator's convention. The row is `1.9e-27` of `W`, so the score does not move. Not charged, and said so: the
  writing of the program, the proof and the tools, which is not computation in this cost model and which no
  entry here charges.

## 10. Provenance and credits

A credit is not an endorsement; nobody named here has reviewed this entry.

* **mitchuski, entry `c9a7e62c` (sha3-256 r24, 124.50895) -- the step itself.** Everything in Section 3.4
  is theirs: the eight-body cycle over the generic rounds, the prefix and closing blocks, the ten blocks and
  their 60,733 words, the iota-as-XOR convention that keeps the cycle closed, the message embedding and
  its constants, the output polarity `PD`, the 147,305-operation step, and the generator decisions the
  program rebuilds the blocks from. Their published generator source is carried in the experiment program, in
  the section marked as inherited, renamed only where a name would clash with ours, and their decisions are
  stored compressed with the SHA-256 of the restored text asserted. The blocks it produces are refused unless
  each matches the SHA-256 their proof prints. This entry declares a dependency on that submission.
* **Jbenisek, entry `71fefe66` (sha3-256 r24, 124.54197).** The search design this entry adopts: no trail is
  cut and the replay refuses a pair **either** of whose trails reaches a cap (an entry test on the live trail
  and the measuring walk on the stored one), with the refusal charged as its term F6; its replay and
  rare-operation accounting. It credits its own `0bd0022d` for the search and accounting and jungjipdo's
  `67f781f8` for the step design, whose register-file and code-encoding conventions Section 3 here also
  follows.
* **Our entries `09fe5fcd` (BLAKE3 r7) and `55783d22` (SHA-256 r64).** The search program, the interpreter,
  the fixtures and probes, the integrated detection-delay bound and its loss list, and the declared-machine
  ledger. The cut-trail terms of those entries are absent here and the stage-2 step is re-derived (P.3).
* **J. Guo, M. Liu, L. Song, ASIACRYPT 2016.** The linear-structure placement that keeps round 0 affine.
* **P. C. van Oorschot and M. J. Wiener, J. Cryptology 12 (1999); J. M. Pollard (1975).** Parallel collision
  search with distinguished points.
* **G. Bertoni, J. Daemen, M. Peeters, G. Van Assche, Keccak implementation overview.** The lane complementing
  transform, applied plane by plane as the theta complements of M.1.
* **Jbenisek, entry `76ab339a` (Lemma 2).** The form of the detection-delay argument.

**What is ours, and what the improvement is worth.** Ours: the declared machine of Section 3 including the
two call instructions, the control program of Section M in our 8-byte encoding with its 40-byte constant
loads, the resource ledger of Section L, the success bound of Section P with its exact checker, the
experiments, and the choice of parameters. Measured against the comparator's own filed configuration, at its
step and its bound, the difference divides as follows:

| step | score | difference | whose |
|---|---:|---:|---|
| its filed configuration | 124.50895 | - | theirs |
| its parameters re-optimised in its own encoding | 124.50800 | -0.00095 | tuning of its configuration |
| the same with our control encoding | 124.50784 | -0.00016 | our encoding |
| **this entry**: its step, our machine, our predicate, our bound, our parameters | **124.50790** | **-0.00105** | as above, less the cost of our own bound and our coarser density grid |

The two middle rows are measurements of *their* configuration, not of this package: they come from
`loop_three_scores.py` and the six per-point certificates in the companion research tree
(`evidence/sha3-r24/three-scores.json`, `evidence/sha3-r24/cert-*.log`), and they are reported here because
they say whose the improvement is. Nothing in this package depends on them.

**Arm C scores 124.50784, which is 0.00006 bits better than this entry.**
That is the comparator's own configuration carried in our control encoding but priced under *its* bound and
*its* ten-plane predicate; this entry is priced under ours, which are stricter and coarser. We state it
plainly rather than leave it to be read out of the table: the lead this entry claims is over the **filed**
frontier, which is the benchmark's comparator, and not over that arm.

**Reconciliation with arm C**, computed by re-summing our own ledger with one input changed at a time
(`tools/reconcile_c9.py`, Appendix A): this entry is 0.000052 bits from arm C, of which
0.000019 is the two inline `KERNEL` headers our encoding traverses per batch,
0.000166 is our stage-1 test and loop control (37 operations per batch against the comparator's
20), 0.000075 is the horizon our bound needs at our power-of-two density against the one the
comparator's bound allowed at its density, and -0.000182 is the replay cap, where we deploy 10.5 `L`
against its 10.65826 `L` and so pay less replay work and fewer target compressions. What is left,
-0.000027 bits, is the only part that is a difference between the two accounting
systems themselves. The four named terms sum to 0.000078 and their joint effect differs from
that sum by -3.1E-8 bits, so the one-at-a-time attribution hides no interaction.
An earlier revision named only three terms and swept the replay cap into the residual, where it was most of
it and was mislabelled. The step gap is zero, because the step is theirs unchanged.

What the figures say about whose the improvement is: of the 0.00105 bits between this entry
and the filed frontier, about 0.00095 is parameter tuning available to the comparator inside its own encoding
and about 0.00016 is our control encoding, and the effects above take back part of that. Against the tested
re-tune of the comparator's own configuration (arm B) this entry is 0.00010 bits
better; that comparison is of one certified configuration against another, and the comparator could choose
differently.

## 11. Comparator

The best filed entry at this target is mitchuski's `c9a7e62c` at 124.50895, success 0.39, memory below `2^20`,
whose step this entry inherits and credits (Section 3.4). This
entry claims 124.50790 at the same success requirement and the same memory bound, an
improvement of 0.00105 bits under the declared conventions
of Section 3, which that entry also declares.

## Appendix A. Recomputation

`tools/build_ledger_c9.py` imports nothing from this candidate: it reads the figures from the
`untrusted_participant_observations` of the organizer's own `experiment-report.json` for these exact bytes and
re-sums every row of L.2, and it refuses a report from any deployment but
the frozen one (it asserts the horizon, the capacity, the replay cap, the density and the key width against
the frozen values, and the stage-2 budget against `32 Q/2^32`). `tools/check_success_bound_c9.py` recomputes
Section P from its own deployed defaults: `--find` re-derives the least certified horizon on the `2^100` grid
and prints `1,047,331 * 2^100`, and `--B 1327649770787631727298943664789651456` prices that horizon directly. Both take `--U` and
`--lrcfac`, whose defaults are the deployed 67,456 and 21/2; passing other values
prices a different design, not this one. `tools/verify_snapshot_c9.py` takes the frozen tree, the ledger, the
bound, the reports of both declared experiments and the organizer's own `experiment-report.json`, recomputes
the ledger and the bound rather than trusting them, checks that the source hash the organizer recorded is
this file's, and compares the executor's in-program certification with the artifact. The declared experiment
`sha3-256-r24-looped-bound-v1` recomputes the same bound inside the organizer's executor, and
`sha3-256-r24-looped-machine-v1` re-measures every handler cost that L.2 charges except the stage-2 miss path,
which a probe prices separately at 86 operations. The frozen snapshot's manifest records
the hash of every file.
