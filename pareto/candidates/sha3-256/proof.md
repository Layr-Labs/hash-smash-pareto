# SHA3-256 r24: chained 10-gate chi rows in the frozen polarity plan, a 145974-operation derivative of 911bffce

## 1. Claim

This package is the smallest derivative of `911bffce-8e7a-4502-90ab-c69a473fff48` (0xplemonade, 124.49149) that we could make: its controller, five-slot table, density, horizon, replay cap, probability argument, certificate source and controller emitter are carried byte for byte and marked inherited below. One thing changes, inside the bit-sliced step: the chi rows of the eight shared bodies are built with **chained 10-gate tricks** (Section 3), with every row's output polarity vector pinned to the frozen plan's, and one D complement of the closing body's round is flipped. The executed step falls from 146,036 to **145974** operations; every other ledger term is the inherited one. It is a circuit-accounting result and does not claim a structural weakness in SHA3-256.

| quantity | exact value or bound |
|---|---:|
| step operations for 256 walks | 145,974 |
| table | 18,360 words, five slots each, 91,800 trails (inherited) |
| controller | 949 instructions, 30368 bytes (inherited) |
| total word operations N | 194387117646175602294056853691822571586681 |
| unit C | 6,504 word operations |
| time_log2, rounded upward | 124.49088 |
| peak memory | 1,048,220 bytes |
| success | at least 0.39 under H_rand (inherited argument, unchanged parameters) |

Against the direct base `911bffce` at 124.49149 the difference is 0.00061 bits, entirely from the 62 executed operations per step; the horizon, the replay cap, the table and the bound are identical, so the success probability is identical.

## 2. Target, embedding and chain function (inherited verbatim from 911bffce, its Section 2; unchanged)

Write a 256-bit point `u` as four little-endian 64-bit limbs `u0` through `u3`. The 128-byte message `m(u)` is the first 16 lanes of the absorbed state:

- lane 1 is `u0`, lane 6 is `u1`, and lane 11 is `u0 xor u1 xor K11`;
- lane 4 is `u2`, lane 9 is `u3`, and lane 14 is `u2 xor u3 xor K14`;
- all other lanes are fixed S3-04 constants.

The nonzero fixed lanes are `K2=2d58eceb83b21614`, `K5=ffffffffffffffff`, `K10=ffffffffffffffff`, `K11=8b563b3ae0ec8583`, `K13=85ab1d9d707642c2`, `K14=e953898a3e26f4f5`, and `K15=ffffffffffffffff`. The other fixed message lanes are zero. SHA3 padding places `0x8000000000000006` in lane 16. The target starts from the zero state, applies rounds 0 through 23, and returns lanes 0 through 3.

Define `F(u)=SHA3-256-r24(m(u)) xor PD`, where the four little-endian words of PD are:

```
12aba10bcb8967d2 649c982060850444 6c545ef4b4771820 094046d494721825
```

The map from `u` to `m(u)` is injective because lanes 1, 6, 4 and 9 contain the four limbs. Thus `F(a)=F(b)` at distinct points gives two distinct messages with equal complete digests. XOR by PD is a fixed bijection and does not change collision equality.

The two three-lane columns have constant parity, so round-0 theta is affine in `u`. The S3-04 constants make the useful chi neighbors zero or all ones after theta, rho and pi. Round 0 and theta of round 1 therefore admit a short affine prefix. The search uses no algebraic property after evaluation of F.

## 3. The step: the inherited construction and what this derivative changes

**Inherited.** One 256-bit word is one bit plane across 256 walks; rho and pi rename planes; XOR, AND, OR and NOT cost one word operation; each logical value has a stored word and a polarity bit; constants and logical complements change polarity without an instruction; a mixed-polarity product costs two operations and an equal-polarity product one. Rounds 0 and 1 form the affine prefix P; rounds 2 through 22 call eight bodies B1..B8 in a cycle (B1-B5 three times, B6-B8 twice) between two fixed banks, registers 256-1,855 and 1,856-3,455; B8 applies closing output complements so its output polarity equals P's; each body folds a fixed iota word and the driver applies the 33 remaining iota NOTs; E is round 23 restricted to the four digest lanes; the 21 calls and 21 returns are charged. The frozen plan -- every C and D complement, every row's complement subset, 10-gate position and mixed-term polarities, the folded iota words and the closing complements -- is `911bffce`'s, embedded unchanged as `PLAN_DATA` in Appendix B.

**Instruction format and packing (inherited, unchanged).** Each step instruction is 39 bits. Bits 0 through 2 are the opcode. Bits 3 through 14 are `d`, bits 15 through 26 are `a`, and bits 27 through 38 are `b`. The opcode map is 0 XOR, 1 AND, 2 OR, 3 NOT, 4 JAL and 5 JR. XOR, AND and OR set `R[d]` from `R[a]` and `R[b]`. NOT sets `R[d]=R[a] xor ONES`. JAL stores the next prog instruction index in `R[d]` and calls body instruction `a | (b << 12)`. JR returns to the prog index in `R[a]`. Every instruction costs one word operation.

Instructions are packed without per-instruction padding. Instruction `i` occupies bits `39*i` through `39*i+38`; bit `k` of a block is bit `k mod 8` of byte `floor(k/8)`. `prog.bin` and `body.bin` start on separate byte boundaries.

**The 10-gate trick, generalized.** For a chi row `out[x] = b[x] xor ((not b[x+1]) and b[x+2])`, the identity `(not out[k]) and b[k+1] == (not b[k]) and b[k+1]` holds for every position k (when `b[k+1]` is 1, `out[k] = b[k]`; when it is 0 both sides are 0). The inherited plan uses it in at most one position per row, which breaks the odd polarity cycle so that a row can cost its floor of ten operations. This derivative allows any set of positions except all five: the outputs are computed from a plainly computed position backwards, each trick product reading the already computed output and its polarity. The row model (`_row_cost` in Appendix B) prices a row as its complement count plus one or two operations per product, exactly as the inherited builder does; a table of the least cost over the complement subset, the trick set and the mixed-term polarities is built once for every (input pattern, output polarity vector), and **every entry is verified against chi on all 32 input values through the polarity interpretation before use** (`_chained_table`). The table has an entry for all 1,024 pairs.

**The rule.** For each body, the generator first replays the frozen plan on its frozen C and D complements to read the output polarity vector of every row, then rebuilds the body with every row taken from the chained table's minimum for its (input pattern, that pinned output vector). Because the output vectors are pinned, every polarity that reaches the next round, the closing complements, the folded iota words, the prefix P, the end block E and the output polarity PD are unchanged; the eight-body cycle closes exactly as before (the generator asserts it). `PLAN_DELTA` flips one D complement, index 177 (column 2, slice 49), in the closing body's round; the five rows that read it are built for their new input pattern and their pinned output vector. No other plan bit changes. Rows whose chained minimum is cheaper than the inherited decision: B1 1, B2 3, B3 4, B4 2, B5 2, B6 4, B7 0, B8 8 (in B8 ten rows are cheaper and two dearer against the inherited decisions, net 8; the five rows that read the flipped D complement cost the same in total, and B8's ninth saved operation is the theta complement the plan delta removes); every other row is emitted at the inherited cost.

**Result.** Body costs `[6662, 6588, 6587, 6599, 6594, 6583, 6595, 6848]` against the inherited `[6663, 6591, 6591, 6601, 6596, 6587, 6595, 6857]`; P 4,292 and E 2,465 unchanged; iota 33 and 42 calls and returns unchanged. Executed operations `4,292 + 2,465 + 33 + 42 + 139,142 = 145,974`. Stored instructions 59,875 (6,811 prog, 53,064 body). Every body still has exactly 1,600 products and 3,200 theta XORs; the saving is 62 polarity-repair operations per cycle. The allocator is the inherited one; the register peak of the packed step is 3,464 before and after (banks to 3,455 and nine temporaries), inside the inherited 3,540-word file.

`prog.bin` is 33,204 bytes with SHA-256 `de85b18a14cfd66b9916d350a5e72fef6225cc57fdb4e06fa32539de58bbf6de`. `body.bin` is 258,687 bytes with SHA-256 `fc869df5cba74abcf373ae4b112f236c423f798320820f8d460bf8c18f37a33b`. The generator requires both hashes and both counts (`generate()` in Appendix B); the organizer experiment regenerates and executes them (Section 9).

**Construction charge.** The inherited preprocessing allowance is `2^60` word operations. Its itemized components are bounded above by `2^58` for frozen polarity-plan construction, `2^50` for the parameter scan, `2^46` for the structured-constant basis and scan, `2^46` for step generation, and `2^36` for controller emission, packing and hashing. Their sum is below `2^59`, so `2^60` includes a factor-of-two reserve. This derivative adds the chained table (under 2^21 row evaluations), its verification (under 2^16), the pinned-output complement searches that found the one flipped bit and the emission probes, bounded by 2^40 word operations in all; the total stays below `2^59 + 2^40 < 2^60`, so the inherited allowance covers it and is charged unchanged in N.

**Generator storage schedule.** The normative generator uses a streaming storage schedule. It retains the 291,891 output bytes and one graph at a time. The largest graph has 8,448 nodes (the inherited bound of 8,457 holds) and the affine prefix has 1,255 live forms. A concrete bound is 291,891 output bytes, 67,656 node bytes, 43,925 affine-form bytes, 147,456 hash-table bytes, 59,199 liveness and register-allocation bytes, 24,825 frozen-plan bytes, 32,768 state and polarity bytes, 12,288 register maps, a 262,144-byte generator image and a 16,384-byte stack. The sum is 958,536 bytes. The controller emitter runs in a separate phase below that bound. Both finish before the search. The chained table adds 1,024 six-tuples, under 49,152 bytes as Python objects, so the generator stays below the search peak of Section 8.

## 4. Compact controller (inherited verbatim from 911bffce, its Section 4; unchanged)

The original controller gathers one walk by naming all 256 plane registers four times and inserts a point by naming all 256 planes five times. Those straight-line routines account for 1,022 and 1,283 static instructions. Their operation cost matters only after a distinguished point, but their 32-byte encodings occupy table memory for the whole search.

This controller reserves 256 memory words called `SCRATCH`. If the distinguished-point mask is nonzero, 256 static stores copy plane registers 0 through 255 to `SCRATCH`. The gather routine loops over `j=0..255`, loads scratch word j, extracts lane `l`, shifts the bit to position j and ORs it into the scalar point. It executes 2308 operations including its return. The setwalk routine loops over the same words, clears bit l and inserts bit j of the new point. It executes 2822 operations. Before the next step, 256 static loads restore the plane registers; the restore costs 257 operations.

The rare-path bound charges the store and restore copy once for every processed distinguished walk. A hit containing several distinguished walks performs each copy only once, so this is an overcount. The exact per-walk fixed cost is 2892; restart is 2834; setup is 750088. The extra no-DP hit work is 125 operations. The two-instruction prefilter compare is already in BSTEP, so adding 127 here would count those instructions twice. One table word probe remains 24 operations. The emitter derives these values from label differences and loop trip counts.

The emitted controller has 949 instructions and 30368 bytes. Its SHA-256 is `7ced52e4d8394cde8d7eb8ce95dff3d9d27622312e57a7e6489fe685c0d8c2e2`. Appendix C contains the complete emitter. The organizer experiment decodes this exact program and executes its evaluation, probe, restart, replay and recovery paths.

The 16-word data image exists before instruction 0. Words 0 through 6 pack the 25 fixed state lanes four 64-bit lanes per word. The variable lanes are zero in this template, lane 16 contains `0x8000000000000006`, and the remaining capacity lanes are zero. Word 7 packs the four PD limbs. Words 8 through 15 are output space. The loader writes these 512 bytes once; the memory table includes them. `LDA d,imm` places the address literal `imm` in register d. `LD d,a,imm` loads memory word `M[R[a]+imm]`. The replay uses seven LD instructions from the zero base for the template and one LD for PD. Pointer setup uses LDA. These substitutions are one-for-one, so `e=6533`, every handler count and N remain unchanged.

## 5. Table and one-attempt algorithm (inherited verbatim from 911bffce, its Section 5; unchanged)

The table has S=18,360 words. Each word has five 51-bit slots at bit offsets 0, 51, 102, 153 and 204; bit 255 is unused. Trail index `i` owns word `i mod S` and slot `floor(i/S)`. Its encoded trail number is

```
t(i) = (i mod S) | ((51 * floor(i/S)) << 15).
```

The maximum index is 91,799 and maps to word 18,359, slot 4. Index 91,800 is rejected before a restart. A written slot is `1 | ((endpoint mod 2^50) << 1)`. Zero denotes an empty slot. The table does not store the trail number; the matching word and slot recover it. A record is repeated in all five slot positions, XORed with each loaded word, and each 51-bit field is tested for zero.

One attempt samples one uniform 256-bit `rho`. This is the only random coin. The first 256 trails start at `rho+t(i)` for `i=0..255`, one per walk. Each restart consumes the next index. The controller stores each walk's trail number and start step in `LID` and `LST`.

A point is distinguished when it is less than `696 * 2^135`. Equivalently, planes 145 through 255 are zero and the ten lower comparison planes are less than 696. Its random-function probability is exactly `theta=696*2^-121`. A trail runs to its first distinguished point; the main loop does not cut it.

At a distinguished point, the handler gathers the endpoint and scans all S words. If no slot matches, it writes the record into the slot owned by the current trail and restarts the walk. If a slot matches, it recovers that stored trail's number from the word and slot. The current trail length is `c1-LST[l]`. Replay walks the stored trail from `rho+t(a)` to its first distinguished point to measure its length. It rejects either length above LRC. It advances the longer trail, walks both in lockstep, and returns the two distinct predecessors of the first equal image. A false 50-bit key match exhausts replay and fails the attempt.

The replay cap is `LRC=63276*2^99=40105929690020721804552696011685888` evaluations. The attempt has `Tb=535585213*2^91=1326044759243777524635692002048999424` lockstep steps. The prefilter hit counter aborts after `HMAX+1`, where `HMAX=45285796970718404697269819089616897`. Other terminal states are table-capacity exhaustion, the Tb deadline, replay refusal, a nonmerge after a key match, and success.

## 6. Exact operation ledger

Every loop iteration costs the 145,974-operation step, 15 prefilter ORs, a compare and branch, then the three-operation counter path (inherited): BSTEP is **145,994**.

The replay bound, the rare-path bound R and the preprocessing allowance are the inherited ones, unchanged because nothing they price changed. One scalar replay evaluation loads the message constants, inserts the point, executes one target permutation and XORs PD; it costs `e=6533`, a measuring iteration 6,541 and a lockstep replay iteration 13,079; at most one replay runs, bounded by `(6541+13079)*LRC+79 = 786878340518206561805323895749277122639` operations.

At most HMAX+1 prefilter hits, U-255 distinguished walks and U-256 completed restarts occur. With `Cdp=2892+24*S`, the rare bound is

```
R = (HMAX+1)*125
  + (U-255)*Cdp
  + (U-256)*(2834+3)
  + 3 + 1 + 750088
  = 5660724621339800587158727427065709610.
```

The preprocessing allowance is `2^60` word operations (Section 3). Therefore

```
N = Tb*145994 + replay + R + 2^60
  = 194387117646175602294056853691822571586681.
```

The integer certificate is

```
6504^100000 * 2^12449087 < N^100000 <= 6504^100000 * 2^12449088.
```

Hence `log2(N/6504)`, rounded upward at five decimal places, is **124.49088**. (The inherited row: `N = Tb*146056 + replay + R + 2^60 = 194469332421248716500584266595949609550969`, 124.49149.)

Appendix A is the inherited certificate source and still carries the source's `step_ops=146_036` and `body=258_809`; run as shipped it prints the inherited row. With `step_ops=145974` and `body=258687` its `compact_handler_row` yields the N above; the components listed here are what the certificate was computed from, and the parameter certificate (Section 7) does not depend on the step cost.

## 7. Probability space and success bound (inherited verbatim from 911bffce, its Section 7; unchanged)

H_rand is the one score-critical premise. The target F and all program choices are fixed. Given rho, the run is deterministic. H_rand says that the success probability over rho is at least the probability below for a uniform random function from 256 bits to 256 bits. This is not proved for fixed SHA3-256-r24.

In the random-function model, lazy sampling gives an independent uniform image at each fresh input. Let `n=2^256`, `q=1-theta`, `E=256*Tb`, `w=2^99`, and `J=63276`. For bin j, the tail from the first image coincidence to the common distinguished point lies in `[(j-1)w,jw-1]` with probability `q^((j-1)w)-q^(jw)`. The birthday lower bound at `e` evaluations is `G(e)=1-exp(-e(e-1)/(2n))`. The covered success term is

```
sum_(j=1..J) (q^((j-1)w)-q^(jw)) * G(256*(Tb-jw)).
```

The subtraction terms are as follows.

- F6 bounds a first-coincidence pair whose replay length exceeds LRC. For one evaluation, summation by parts gives `G6=q^LRC*(1+LRC*theta)`. Bounding the probability of a first coincidence and conditioning on at most U distinguished points gives `F6=2*G6*(1-exp(-E^2/(2n)-E^3/(3n^2)))*(1-E/n)^(-U)`.
- F2 bounds at least U-256 random-function distinguished outputs. With `mu=E*theta` and `k=U-256`, Chernoff gives `exp(-mu+k*(1+ln(mu/k)))`.
- F3 bounds a coincidence inside one trail by `U/(theta^2*n)`.
- F4 is `2^-90 + U^2*2^-51`. The first term covers start/replay coincidences. The second covers two different endpoints with equal 50-bit stored keys.
- F5 is below `2^-1000` from the hit-counter supermartingale bound. A further `2^-60` covers numeric rounding.

For this row the four displayed terms are F6=`2.482844704527E-4`, F2=`5.783711109333E-18`, F3=`1.156656126914E-5`, and F4=`3.742446352817E-6`. The resulting bound at Tb is `0.39000000019218266921109449828941416160612989235679650920463306527630152297669790`. One grid point lower gives `0.38999999906321868365338964463524695291945346845796282947972348052285334553368635`. Thus Tb is the least multiple of `2^91` whose bound reaches 0.39.

The six-slot alternative was rejected. Six 42-bit slots leave only 41 key bits. At its 110,112-trail capacity, the alias component alone is `U^2*2^-42 = 0.002756826812401414`. Charging this term raises the best local scanned score to about 124.49642.

## 8. Memory

| region | bytes |
|---|---:|
| register file, 3,540 words | 113,280 |
| prog plus prefilter | 33,277 |
| body code | 258,687 |
| controller, 949 instructions | 30368 |
| scratch transpose, 256 words | 8,192 |
| table, 18,360 words | 587,520 |
| LID and LST, 512 words | 16,384 |
| data image, 16 words | 512 |
| total | 1,048,220 |

Only the body-code row changes (122 bytes fewer); the table is deliberately not enlarged, so the capacity, the density, the horizon and the bound stay the inherited ones. The margin to `2^20` is 356 bytes. The hashed `prog.bin` is 33,204 bytes; the 15 prefilter OR instructions are appended to the same packed block and add exactly 73 bytes, as inherited. The step generator peaks below the search by the storage schedule in Section 3; the controller emitter runs separately. The search is therefore the largest phase at 1,048,220 bytes.

## 9. Organizer experiment and limits

`step-controller-recovery` runs the step generator of Appendix B and requires both packed hashes above. It decodes the 39-bit words, applies the declared JAL and JR semantics, executes eight full-width inputs and requires exactly 145,974 traced operations. A separate scalar Keccak implementation checks every output. The chained-row table is rebuilt and verified against chi inside the run.

The controller part of the experiment is inherited unchanged: it decodes the 949-instruction controller and requires SHA-256 `7ced52e4d8394cde8d7eb8ce95dff3d9d27622312e57a7e6489fe685c0d8c2e2`, executes `evalF` against scalar Keccak, a matching table probe, a full-table no-match probe, restart across the slot boundary, the last accepted trail and first rejected trail, a successful replay that recovers both messages, and a false-key replay that takes the failure path. It then tests 68 full-width r24 images per organizer trial for a low-12-bit agreement. The organizer recomputes every returned target event.

The projection is bounded implementation evidence. It does not estimate the full-scale collision probability and does not validate H_rand at birthday scale. Null trials are retained. The source uses only the Python standard library and is below the organizer's 64 KiB source limit.

## 10. Credits

This package is a derivative of `911bffce-8e7a-4502-90ab-c69a473fff48` (0xplemonade): its controller, table, density, horizon, replay cap, probability argument, certificate source (Appendix A), controller emitter (Appendix C), frozen polarity plan and organizer experiment are carried verbatim and credited in full; Sections 2, 4, 5 and 7 are that entry's text, marked inherited. Its own lineage is credited with it: `23a6a5a9-90f0-4d0e-8ed3-9b6b677ae964` (Jbenisek) for the 146,036-operation construction, its polarity campaign and the five-slot layout; `c9a7e62c-7795-422c-8a3c-2de303e892dd` for the shared-body cycle; `03f3772a-eed5-4d3b-aad9-30f722ff0574` for the graph-builder and allocator lineage; `760073e9-f795-4b4f-91ff-3b5fae8e3415` for the S3-04 constants, look-ahead polarity planning and packed encoding; `71fefe66-9bf4-46ee-8b74-e91b3b562816` and `5700dc84-83bd-47e7-8a8a-93016b27ea72` for the LS1 bit-sliced step and search; `0bd0022d-aa41-40a4-81b9-61d18f1c444c` for generic r24 replay and accounting; and `e7789ea7-3a44-46b1-b5d4-67821a4a8f13`, `cd30f68e-3b6a-4cd4-9e1c-a9ff7098b0dd` and `be664ca8-59ef-4683-aec2-5a072ae53e9c` for the structured-constant lineage.

New here: the chained 10-gate row construction, its exhaustively verified cost table, the pinned-output rule that keeps every downstream polarity fixed, the one-bit plan delta, and the measurements. Credits identify provenance; they do not imply review or endorsement.

## Appendix A. Exact certificate source (inherited verbatim from 911bffce, its Appendix A; unchanged)

```python
#!/usr/bin/env python3
"""Exact collision-search ledger and parameter search for SHA3-256 r24.

The module contains no participant code.  It implements the probability and
word-RAM formulas stated in the public proof so that candidate emitters can
feed it measured instruction counts.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal as D, ROUND_CEILING, getcontext
from fractions import Fraction
import math
from typing import Mapping


getcontext().prec = 80

UNIT = 6_504
LANES = 256
RANGE = D(2) ** 256
TARGET_SUCCESS = D("0.39")
CERT_DENOMINATOR = 100_000


@dataclass(frozen=True)
class HandlerCounts:
    instructions: int
    hit: int
    dp_fixed: int
    probe_word: int
    restart: int
    restart_halt: int
    deadline_final: int
    setup: int
    measure_iter: int = 6_541
    replay_iter: int = 13_079
    replay_const: int = 79


@dataclass(frozen=True)
class Parameters:
    hf: int
    dplo: int
    dk: int
    dt: int
    width: int
    bins: int
    replay_cap: int
    tb: int
    granularity: int

    @property
    def theta(self) -> D:
        return D(self.dt) / D(2) ** (256 - self.dplo + self.dk)


@dataclass(frozen=True)
class Row:
    step_ops: int
    table_words: int
    trails: int
    key_bits: int
    memory_bytes: int
    memory_regions: Mapping[str, int]
    parameters: Parameters
    handlers: HandlerCounts
    preprocessing: int
    bstep: int
    replay_ops: int
    rare_ops: int
    total_ops: int
    success: D
    previous_success: D
    failures: tuple[D, D, D, D]
    hit_cap: int
    time_scaled: int

    @property
    def time_log2(self) -> str:
        whole, fraction = divmod(self.time_scaled, CERT_DENOMINATOR)
        return f"{whole}.{fraction:05d}"


def success_bound(
    tb: int,
    theta: D,
    width: int,
    bins: int,
    trails: int,
    key_bits: int,
    *,
    parts: bool = False,
):
    """Return the proof's exact Decimal lower bound in the random-function model."""

    replay_cap = bins * width
    log_q = (D(1) - theta).ln()
    mean_dp = D(LANES * tb) * theta
    available = trails - LANES
    if D(available) <= mean_dp:
        return (D(-1), None) if parts else D(-1)

    birthday = D(0)
    q_previous = D(1)
    for j in range(1, bins + 1):
        q_current = (D(width * j) * log_q).exp()
        evaluations = LANES * (tb - j * width)
        if evaluations > 1:
            exponent = -D(evaluations) * (evaluations - 1) / (2 * RANGE)
            birthday += (q_previous - q_current) * (D(1) - exponent.exp())
        q_previous = q_current

    evaluations = LANES * tb
    g6 = (D(replay_cap) * log_q).exp() * (D(1) + replay_cap * theta)
    coincidence_upper = D(1) - (
        -D(evaluations) * evaluations / (2 * RANGE)
        - D(evaluations) ** 3 / (3 * RANGE * RANGE)
    ).exp()
    inflation = (-D(trails) * (D(1) - D(evaluations) / RANGE).ln()).exp()
    f6 = 2 * g6 * coincidence_upper * inflation
    f2 = (-mean_dp + available * (D(1) + (mean_dp / available).ln())).exp()
    f3 = D(trails) / (theta * theta * RANGE)
    f4 = D(2) ** -90 + D(trails) ** 2 * D(2) ** -(key_bits + 1)
    bound = birthday - (f6 + f2 + f3 + f4 + D(2) ** -1000 + D(2) ** -60)
    failures = (f6, f2, f3, f4)
    return (bound, failures) if parts else bound


def hit_cap(tb: int, replay_cap: int) -> int:
    delta = Fraction(1, 2**20)
    exponent = delta * delta * Fraction(tb, 2**8) / (2 + delta)
    assert exponent > 1_000 * Fraction(6_932, 10_000)
    return tb * (1 + delta) // 2**8 + 1 + replay_cap


def rounded_time(total_ops: int, *, verify_integer: bool = False) -> int:
    scaled = int(
        (D(CERT_DENOMINATOR) * (D(total_ops) / UNIT).ln() / D(2).ln())
        .to_integral_value(rounding=ROUND_CEILING)
    )
    if verify_integer:
        total_power = total_ops**CERT_DENOMINATOR
        unit_power = UNIT**CERT_DENOMINATOR
        assert (unit_power << (scaled - 1)) < total_power <= (unit_power << scaled)
    return scaled


def make_row(
    *,
    step_ops: int,
    table_words: int,
    slots_per_word: int,
    key_bits: int,
    memory_regions: Mapping[str, int],
    parameters: Parameters,
    handlers: HandlerCounts,
    preprocessing: int,
    verify_integer: bool = False,
) -> Row:
    trails = slots_per_word * table_words
    assert parameters.replay_cap == parameters.width * parameters.bins
    bstep = step_ops + 15 + 2 + 3
    replay = (
        (handlers.measure_iter + handlers.replay_iter) * parameters.replay_cap
        + handlers.replay_const
    )
    hmax = hit_cap(parameters.tb, parameters.replay_cap)
    dp_cost = handlers.dp_fixed + handlers.probe_word * table_words
    rare = (
        (hmax + 1) * handlers.hit
        + (trails - 255) * dp_cost
        + (trails - 256) * (handlers.restart + 3)
        + handlers.restart_halt
        + handlers.deadline_final
        + handlers.setup
    )
    total = parameters.tb * bstep + replay + rare + preprocessing
    success, failures = success_bound(
        parameters.tb,
        parameters.theta,
        parameters.width,
        parameters.bins,
        trails,
        key_bits,
        parts=True,
    )
    previous = success_bound(
        parameters.tb - parameters.granularity,
        parameters.theta,
        parameters.width,
        parameters.bins,
        trails,
        key_bits,
    )
    assert success >= TARGET_SUCCESS > previous
    memory_bytes = sum(memory_regions.values())
    return Row(
        step_ops=step_ops,
        table_words=table_words,
        trails=trails,
        key_bits=key_bits,
        memory_bytes=memory_bytes,
        memory_regions=dict(memory_regions),
        parameters=parameters,
        handlers=handlers,
        preprocessing=preprocessing,
        bstep=bstep,
        replay_ops=replay,
        rare_ops=rare,
        total_ops=total,
        success=success,
        previous_success=previous,
        failures=failures,
        hit_cap=hmax,
        time_scaled=rounded_time(total, verify_integer=verify_integer),
    )


def baseline_row(*, verify_integer: bool = False) -> Row:
    parameters = Parameters(
        hf=111,
        dplo=145,
        dk=10,
        dt=646,
        width=633_825_300_114_114_700_748_351_602_688,
        bins=68_174,
        replay_cap=43_210_406_009_979_655_608_818_122_161_651_712,
        tb=1_326_345_234_525_992_950_706_776_067_278_897_152,
        granularity=2**91,
    )
    handlers = HandlerCounts(
        instructions=2_705,
        hit=127,
        dp_fixed=1_091,
        probe_word=24,
        restart=1_293,
        restart_halt=3,
        deadline_final=1,
        setup=353_414,
    )
    regions = {
        "register_file": 113_280,
        "prog_and_prefilter": 33_277,
        "body": 258_809,
        "other_code": 86_560,
        "table": 539_136,
        "walk_state": 16_384,
        "data_image": 512,
    }
    return make_row(
        step_ops=146_036,
        table_words=16_848,
        slots_per_word=5,
        key_bits=50,
        memory_regions=regions,
        parameters=parameters,
        handlers=handlers,
        preprocessing=212_142_541_709_568,
        verify_integer=verify_integer,
    )


def compact_handler_row(*, verify_integer: bool = False) -> Row:
    """Return the selected five-slot row from the emitted compact controller."""
    from emitter import Layout, build_program, counts

    parameters = Parameters(
        hf=111,
        dplo=145,
        dk=10,
        dt=696,
        width=2**99,
        bins=63_276,
        replay_cap=63_276 * 2**99,
        tb=535_585_213 * 2**91,
        granularity=2**91,
    )
    layout = Layout(table_words=18_360, slots_per_word=5, slot_bits=51)
    emitted = counts(
        build_program(
            layout,
            replay_cap=parameters.replay_cap,
            tb=parameters.tb,
            hit_limit=hit_cap(parameters.tb, parameters.replay_cap),
            dplo=parameters.dplo,
            dk=parameters.dk,
            dt=parameters.dt,
        ),
        layout,
    )
    handlers = HandlerCounts(
        instructions=emitted.instructions,
        hit=emitted.hit,
        dp_fixed=emitted.dp_fixed,
        probe_word=emitted.probe_word,
        restart=emitted.restart,
        restart_halt=emitted.restart_halt,
        deadline_final=emitted.deadline_final,
        setup=emitted.setup,
        measure_iter=emitted.measure_iter,
        replay_iter=emitted.replay_iter,
        replay_const=emitted.replay_const,
    )
    regions = {
        "register_file": 113_280,
        "prog_and_prefilter": 33_277,
        "body": 258_809,
        "other_code": emitted.instructions * 32,
        "scratch": 256 * 32,
        "table": layout.table_words * 32,
        "walk_state": 512 * 32,
        "data_image": 16 * 32,
    }
    return make_row(
        step_ops=146_036,
        table_words=layout.table_words,
        slots_per_word=layout.slots_per_word,
        key_bits=layout.key_bits,
        memory_regions=regions,
        parameters=parameters,
        handlers=handlers,
        preprocessing=2**60,
        verify_integer=verify_integer,
    )
def float_success(
    tb: float,
    theta: float,
    replay_cap: float,
    trails: int,
    key_bits: int,
    *,
    bins: int = 3_000,
) -> float:
    width = replay_cap / bins
    log_q = math.log1p(-theta)
    mean_dp = LANES * tb * theta
    available = trails - LANES
    if available <= mean_dp:
        return -1.0
    birthday = 0.0
    previous = 1.0
    for j in range(1, bins + 1):
        current = math.exp(width * j * log_q)
        evaluations = LANES * (tb - j * width)
        if evaluations > 1:
            birthday += (previous - current) * -math.expm1(
                -evaluations * (evaluations - 1) / 2.0**257
            )
        previous = current
    evaluations = LANES * tb
    g6 = math.exp(replay_cap * log_q) * (1.0 + replay_cap * theta)
    coincidence = -math.expm1(
        -evaluations * evaluations / 2.0**257
        - evaluations**3 / (3.0 * 2.0**512)
    )
    inflation = math.exp(-trails * math.log1p(-evaluations / 2.0**256))
    f6 = 2.0 * g6 * coincidence * inflation
    f2 = math.exp(-mean_dp + available * (1.0 + math.log(mean_dp / available)))
    f3 = trails / (theta * theta * 2.0**256)
    f4 = 2.0**-90 + trails * trails * 2.0 ** -(key_bits + 1)
    return birthday - f6 - f2 - f3 - f4


def least_tb(
    theta: D,
    width: int,
    bins: int,
    trails: int,
    key_bits: int,
    granularity: int,
    low: int,
    high: int,
) -> int:
    low = low // granularity * granularity
    high = -(-high // granularity) * granularity
    assert success_bound(low, theta, width, bins, trails, key_bits) < TARGET_SUCCESS
    assert success_bound(high, theta, width, bins, trails, key_bits) >= TARGET_SUCCESS
    while high - low > granularity:
        middle = (low + high) // 2 // granularity * granularity
        if success_bound(middle, theta, width, bins, trails, key_bits) >= TARGET_SUCCESS:
            high = middle
        else:
            low = middle
    return high


def parameter_candidates(trails: int, key_bits: int):
    """Yield promising exact parameter sets ordered by a float-model score."""

    candidates = []
    center = 128.0 - math.log2(trails)
    for h_index in range(-30, 31):
        h = center + 0.01 * h_index
        theta_float = 2.0**-h
        for kappa_index in range(900, 1201, 5):
            kappa = kappa_index / 100.0
            replay_float = kappa / theta_float
            low = 2.0**119.8
            high = 2.0**120.2
            if float_success(high, theta_float, replay_float, trails, key_bits) < 0.39:
                continue
            for _ in range(34):
                middle = (low + high) / 2.0
                if float_success(middle, theta_float, replay_float, trails, key_bits) >= 0.39:
                    high = middle
                else:
                    low = middle
            candidates.append((high, h, kappa))
    candidates.sort()
    yielded = set()
    for approximate_tb, h, kappa in candidates[:24]:
        hf = math.floor(h)
        dk = 10
        dt = round(2**dk * 2 ** (hf - h))
        dt = max(2 ** (dk - 1), min(dt, 2**dk - 1))
        dplo = 256 - hf
        theta = D(dt) / D(2) ** (256 - dplo + dk)
        width = 2 ** (hf - 12)
        bins = round(kappa / float(theta) / width)
        granularity = 2 ** (hf - 20)
        signature = (dplo, dk, dt, width, bins, granularity)
        if signature in yielded:
            continue
        yielded.add(signature)
        tb = least_tb(
            theta,
            width,
            bins,
            trails,
            key_bits,
            granularity,
            int(approximate_tb * 0.99),
            int(approximate_tb * 1.01),
        )
        yield Parameters(
            hf=hf,
            dplo=dplo,
            dk=dk,
            dt=dt,
            width=width,
            bins=bins,
            replay_cap=bins * width,
            tb=tb,
            granularity=granularity,
        )


if __name__ == "__main__":
    row = compact_handler_row(verify_integer=True)
    print(f"step_ops={row.step_ops}")
    print(f"trails={row.trails}")
    print(f"memory={row.memory_bytes}")
    print(f"total_ops={row.total_ops}")
    print(f"success={row.success}")
    print(f"time_log2={row.time_log2}")

```

## Appendix B. Standalone frozen-plan step generator, with chained rows (this derivative)

```python
#!/usr/bin/env python3

"""Bounded generator for a 145,974-operation r24 step: 911bffce's frozen plan with chained 10-gate
chi rows and one flipped D complement; everything else is that entry's, unchanged."""

import base64, hashlib, json, sys, zlib

MASK64 = (1 << 64) - 1

PLAN_DATA = 'c-rk;+m0N$4Sk=ls80|nmYVgN%Wf73;(f>usCzfSBF;K+{QpQxBBdksjP1Y<&<%8Bz0*^pk|>foJfuqX>Emzt{YD(a%kLjImhHp8KmF^&FTZZGefs#@<)0gE@AH2?`S;&HeEP?S_rGl6<p<hmKPZH7=q3Dm{VBv0I7nckNOJuWm_ty#{w-VrY1l*g&esOz|MerGfB5A`+5)YY%XjhS?L#uR_{`_!haWfI+IKywFxRfGa!Szaf7H8C(l!Ry|I|j<%a{6%DAb$FFGWl$m#)`Ti^!?|9*J}7EY)@ri0hr@lFOX0`YK)3mV00|G2=GG-d~-dsL2Y~*tNCe#ddS=kWhJU5)S|Kr-&)ra*?5D8a7ij;4Jfevu@!#e~Os<hQhQ@o<(Z5q++E>L$4`@sy220qlC}Q3|r~Y49{Ywt+tpAD<}zn)ga^ZJ+vvSHc!@TLT{osZoBH0P-dyW&#mLPiD_QXi<st0uR5HX$g;|<uNb>tJHAGnH1|Yb<D183gVJjgldd;vKFX8d$fE1FSNhj2ad}fr3g3NY{$G|l(Syjz4<cuL5IN;R<lG-b&h#L1o*qO_eGoa1$B>gBBp&gD#3O!?c*H#($=hu3hU-iWOO{NfaCv@(1wr;n^KgS$T~oSB%!q|8A<*#h^Iv}2zW?-}pKo-ZVitOu<sQw#PqW;kS>n?y_h=S*n&lqNvOmpok7h|vv)rRuPEWJkqgnK6mU}eI@ifa_rjyS!|32;V%=7QlF3&{&KJD_%^zYLy&s6_D?efg^@6#^NWdA<x^33+{(=N|+|32;V%=hooF8s{*@6#^NeE&Y}^33<|(=N|^|L*Mar$7I3<E@;k$Vaf#QR88>a@`IC)PqXr@^?F#RQ{E}C$_fI&bN#+E`ds0wLT8JrhYGtv3y+rS&k2#tbMjIlJ#B36qCjJ^>M|nl{T`sYgGmwW67o6pJ9&vNokftxZMMD>M~^bu0B4s@yfN69X&fsJA0MvR8%=#A^udL>7dLnU#~~#E1-_;dJ04L<+xQj)spQjnu^IKqYu<cwj1l1rOl<auk)pL$jqNN<Yi2^d06ag$G9lloQt08xHL|+xc{izklL}lV0O%QXr;)NXw0SjUi9yNl40KN6HLRul8pKE@wNI-OyE~&SF=m&PseemxcE}{@!=b>w!I2-(2&vlNcJ6{->fp2o!$3D!H3{LO@?v7*VzBY)}DEiGx~aAILB4>WzVAKGJb4pN5PNLuf@ha^Q;f_d2bs`r#bXfL*+DEx0U^j(uAq9MU%;FQ*GhC5f;5G_*7{x=Chf{80vNf`xRfP_nA-IdaD>#bWzvnKE|mq7`Lp$O|n5yX_l5{ufAkMTjEueqq&7G*I3O!O&$St+bKzki`%-3x|pttVurl8b^(@uJvqp23GVG)RvD0y!Ig9|s{r)6+QgSKk85eUUwvr;q?Gxmqs_HKtsU<?hXF^W?WsA(1W^&@nO$c9d%jG&Teo&(@YX|v7_=7Gt_N(%<Th8VveB4__pb^e2jEI&EHO2RVpt|8SSqSRAG*M1=3#@#1D1VRCs-z^?=tU9Q|KuNn|<Elq+`4g#`1wB*CEIC$EIHuJQoSRr)^$`*`?aSVR(^K0N%>-t~xw|A2+V!l<-@1x6IpVgo4i>VZeBq%kI9o!dxEhI1IZue4ZiPbe-y~U-#qPLk`%HWnPmf569Xd-feqATbYg=)=^g;lGQ?zhd)_hwD_jLI&|5@A@~@wAw@$7_jTp?5lzk$=oPU6A=GiF!k}!<V5;iMzYDM*>d~dTW3u0Und9<B)+8_#ANG@H_;Xg67pB7=LA1May?+NcRB(NVD1fdSIZwV!XvliQ8j&f&b&N<h9(VHra}tm(qAMCyS|lFK3!*Exw%zTM3<yEDj=&nL9cbvl)#Q=Sm<%CAsWSxEla1r-D*%I3aI*yV@%gGw@L5@&7|Rh4kvxx$ZtAd_Y#AwBV}L(jsw@M#lgU}eiQwXHduRD)zFjizpV9o`+Fy)zPeizb`8h)un7`YzXA{m^m!&F=8WcZ_XIu+m3de+@fsJt@<CD=RIlQ?}*Q|lTZ!29TV?YM4&bqU?16ycuwnoO-kS=6kg%w5tDqRoGY87p<WH7vhsf6&!bGYRpXYh<N0p2juC>qe|Yvv}@<*`<rW$!S@3WNLRCRLglg1eP5GRn*HMEE+483u?_9^u$TtR@tTjyhDe6TqxT1R5rg1xD&}YkkH9$!&tAC-8f52WJyICLQiZd>b`8qtx-8!wjqL{vIZfg^05;bM*;Yuw5Meo|h$n^C}`%a<4Pwqw55V(wG=`Xy@)C)ET{9!SIj)0(_Z8iz^JpglKkUn|}r<GdnSlq@6G{_96)1E}Ii%9C>M1+ZY2+z&sQn)uBlN=Dpo%(HRyr*a|~cS8;^jys+0~;i|v}+JSfQ&pC0VHN+~7BFb(IatGKm2y1I)pTl(8=i(AC{*Iw#q6#|ORTg-vbLY8;by%NA7@>|KD?BgkZ=xBVg^V~?W%d^m=|VvQ;7TCCAa45dzwHptv@!C?z*JR7sH=q&SbL?2q<PLB3T9OpOk1y&2)Kxh1khgf6PyitR9<s(n<_iI6zVGK5aG#2GKkbA@_8~IU^xn?I9r=_`C#2BcvP3!g#wJ@?Guc#LsAz3%H55e0n0-05kez`jT1!WfKa2OPK3!h)>5-AH%{Z805vX8VC(!Z4XRf6u8@$2yQVpbC17C@**P-86C`1!7}24@5*pDFnH6M65a}&3iU>&==ACJVECJZZ+7vP;WE04a03N7@DIUpXhdijGI;8F}&kEf<5@~1q0`^M~1~S&rfT7-GK1<@to)}Vx-6r#4axZKu&8&|-1Wydo<T%3`I%ATH;YUVD6RX*(`MxK<Sp4YompRGCtb~z1S;659MXS2LO;BfWzOH(vL8A}B!a=yDX%4T4jhA5mAb=0Et!pe6)WU`s44yWu3wdoKExC9`cU(%VSn~H0c>r;)a#m5XHWGkMy|xX43^2mqcbm={f!zH{0^XMz&9x)}rXjFQ72TI6h>aPbp_FME;Bqw&vK{>C5qK^4Cu3N}pRu0U+w0`^bOv@|eMfjfTz#_^G6R=8k(HPSdmgrJ?nVO1R1ZmJ$9<{)t+iTY90_W{35qFa2(LX9hBkLzTwKG<Od>2{;SuJL)mtJS-CqJE=0by!I5SQF1;}tz#}-2dhTV0VW=6|4hdM8rlWPt07#Y?J`hq8|3N?2lgtXMpdwok6_H~9DTHpH7nUyLeoGNo&Fe|V-pa;AbN_Z{=9iS&#AU<Ovx`g3iwR(fpTA+x_maNyii(bzPdR@XU!m@^Wi_l@!Ga+ZB0$W-Y26aPKrJ-6*P#;M;NPJ#OuE^RjGWCBvmvnEEgk@_2`zd3d)|wr|ZXb_2g+l4IC!PchMw;0e%;_fCc_iBo-#w|gG}rPdiAx7nuFh1Q$m<9x$?BpA7k#Tn=h|q8_kCuvhbLdOFbkR49+t^@fqi%b4JDf0RA8Hc84@gyy3US$E*F3$x!q2Sz^t*3>xr%|TP>_}GM8pQ;x$ZSvXhp2kZ%$7U1fwop9_RlUJ^%VqFKjW*1|~uSx>O#f;-dMmTfH<(I_nWQweOW=nPwE0;PQSPtUHd0*_=|fmtmq+_r5-fy#d#ZO$j}!~FX2dF^w?Grb&XKsSXjL#=Oxl>2?BUUp!kmw8(XlX>^88cs~#XH3|^r}Da00(%7~4-w4<tjju1K-C27S7ER|Cril^ZGV7b$KAT(LPZ6(b&{7|w~`nY#+RCWwJ*j8H*6V^?fi9kppoE~Yc)bdLvLUbWl5fBFi7RO?onBq?FM7{x~N6s90_Z(sZCvh`U4xJmf#tys+;pc=OjlwnTmZA-zU~w^J1p7G501+)m?p2>M`mZo@Z8lc>NGy#~&Eth5_Z3(p46+2OnxZmMs~u;@h+gtlw<W)Y(&!J?hwIAb@jc?ZI@8TRv(E+>IXUF&0NjyvdT!Dx;W;?LD>j7H6v$na`$C6K=L@LR6dOWXYP?zLbTsUc08j2>n3}e=w?U3+yednNN{Tka`JS+k+kDHQLD&(%tseuKgY6Q;`RgNKo^t_nS<v=L(Z?K#3@XloEa+!Bp<N!wVBsvY7rLmqD0Va$eyynjcuk<M7|>^tLW)c5#`WRwDnG)#Nq#T^E83$-i4-UfL-zz{4OfL%kW^l}+TusH25!*rs7*z0U4>7<Jnm24glx#T6Ohw9ccYCDreu=_{pa?j(8C2YX$d8aCzJe9v*<<*)DF{d}c^Cw}?q56f%kN|SPxw&fA9dUZUT+gwb~<!apKmmn*Zt1|VVc6FcH7BDJTZ_Z#<$<`A<8eZQ0?cLuE!9Vk0<m-Q%-@PrbH~-=rm|y#R?)BR6R370w&c|EB`78USH>Bj7vA!tlYh6u!9=G$Lk?wr$>%?V|P!>sOnLU4l-i7#$(O<KESX%2B$H5l#@?XL{!x;'
def _public_plan(path=None):
 records = {}
 text = zlib.decompress(base64.b85decode(PLAN_DATA)).decode()
 for raw in text.splitlines():
  fields = raw.split()
  if not fields: continue
  kind = fields[0]
  if kind in {'trial','F1','G1'}: records[kind] = fields[1]
  elif kind in {'FG','PHI','DEC','IB','ONOT'}: records[(kind,int(fields[1]))] = fields[2:] if len(fields)>3 else fields[2]
  elif kind == 'LOOP': records[kind] = tuple(map(int,fields[1:]))
  elif kind == 'nr': records['nr'],records['optmode'] = int(fields[1]),int(fields[3])
 if records.get('nr') != 24 or records.get('LOOP') != (8,72): raise AssertionError('bad frozen plan')
 return records

MASK256 = (1 << 256) - 1

NC = -1

O_IN, O_XOR, O_AND, O_OR, O_NOT = range(5)

NREG = 4096

RC = (1, 32898, 9223372036854808714, 9223372039002292224, 32907, 2147483649, 9223372039002292353, 9223372036854808585, 138, 136, 2147516425, 2147483658, 2147516555, 9223372036854775947, 9223372036854808713, 9223372036854808579, 9223372036854808578, 9223372036854775936, 32778, 9223372039002259466, 9223372039002292353, 9223372036854808704, 2147483649, 9223372039002292232)

RHO = (0, 1, 62, 28, 27, 36, 44, 6, 55, 20, 3, 10, 43, 25, 39, 41, 45, 15, 21, 8, 18, 2, 61, 56, 14)

KL = (0, 0, 3267622025928250900, 0, 0, 18446744073709551615, 0, 0, 0, 0, 18446744073709551615, 10040277543336838531, 0, 9631824790095807170, 16812933060745426165, 18446744073709551615, 9223372036854775814, 0, 0, 0, 0, 0, 0, 0, 0)

class Graph:

    def __init__(self, inputs, affine_inputs=False):
        self.op = []
        self.a = []
        self.b = []
        self.k = []
        self.linear = []
        self.cons_table = {}
        self.form_nodes = {}
        for j in range(inputs):
            n = self.new_node(O_IN, 0, 0)
            if affine_inputs:
                mask = [0, 0, 0, 0]
                mask[j >> 6] = 1 << (j & 63)
                mask = tuple(mask)
                self.linear[n] = mask
                self.form_nodes[mask] = n

    def new_node(self, op, a, b):
        n = len(self.op)
        self.op.append(op)
        self.a.append(a)
        self.b.append(b)
        self.k.append(0)
        self.linear.append(None)
        return n

    def cons(self, op, a, b):
        if op != O_NOT and a > b:
            a, b = (b, a)
        key = (op, a, b)
        n = self.cons_table.get(key)
        if n is not None:
            return (n, False)
        n = self.new_node(op, a, b)
        self.cons_table[key] = n
        return (n, True)

    def xor(self, left, right):
        an, ap = left
        bn, bp = right
        if an == NC:
            return (bn, bp ^ ap)
        if bn == NC:
            return (an, ap ^ bp)
        if an == bn:
            return (NC, ap ^ bp)
        am = self.linear[an]
        bm = self.linear[bn]
        if am is not None and bm is not None:
            mask = tuple((x ^ y for x, y in zip(am, bm)))
            k = self.k[an] ^ self.k[bn]
            if not any(mask):
                return (NC, k ^ ap ^ bp)
            n = self.form_nodes.get(mask)
            if n is not None:
                return (n, k ^ ap ^ bp ^ self.k[n])
            n, _ = self.cons(O_XOR, an, bn)
            self.k[n] = k
            self.linear[n] = mask
            self.form_nodes[mask] = n
            return (n, ap ^ bp)
        n, _ = self.cons(O_XOR, an, bn)
        return (n, ap ^ bp)

    def complement(self, value):
        n, p = value
        if n == NC:
            return value
        out, created = self.cons(O_NOT, n, 0)
        if created and self.linear[n] is not None:
            self.linear[out] = self.linear[n]
            self.k[out] = self.k[n] ^ 1
        return (out, p ^ 1)

    def and_value(self, left, right, select):
        an, ap = left
        bn, bp = right
        if an == NC:
            return right if ap else (NC, 0)
        if bn == NC:
            return left if bp else (NC, 0)
        if an == bn:
            return left if ap == bp else (NC, 0)
        if not ap and (not bp):
            return (self.cons(O_AND, an, bn)[0], 0)
        if ap and bp:
            return (self.cons(O_OR, an, bn)[0], 1)
        plain = an if not ap else bn
        other = bn if not ap else an
        if select:
            negated = self.complement((plain, 0))
            return (self.cons(O_OR, negated[0], other)[0], 1)
        term = self.cons(O_AND, plain, other)[0]
        return self.xor((plain, 0), (term, 0))

def term_cost(a, b):
    if a[0] == NC or b[0] == NC or a[0] == b[0]:
        return 0
    return 1 if a[1] ^ 1 == b[1] else 2

def dynamic_row(graph, row, need):
    distinct = all((v[0] != NC for v in row)) and len({v[0] for v in row}) == 5
    best = None
    for trick in range(-1, 5 if distinct else 0):
        if trick >= 0 and (not need >> trick & 1 or not need >> (trick + 1) % 5 & 1):
            continue
        for subset in range(32):
            values = list(row)
            cost = 0
            for x in range(5):
                if subset >> x & 1:
                    if row[x][0] == NC:
                        cost = 1 << 29
                    else:
                        values[x] = (values[x][0], values[x][1] ^ 1)
                        cost += 1
            for x in range(5):
                if not need >> x & 1:
                    continue
                if x == trick:
                    k = (trick + 1) % 5
                    p1, p2 = (values[(k + 1) % 5], values[(k + 2) % 5])
                    if p1[1] ^ 1 == p2[1]:
                        bk = (values[k][0], values[k][1] ^ (p1[1] ^ 1))
                        cost += term_cost(bk, values[(x + 2) % 5])
                    else:
                        cost += 1
                else:
                    cost += term_cost(values[(x + 1) % 5], values[(x + 2) % 5])
            candidate = (cost, subset, trick)
            if best is None or candidate[0] < best[0]:
                best = candidate
    _, subset, trick = best
    row = list(row)
    for x in range(5):
        if subset >> x & 1:
            row[x] = graph.complement(row[x])
    out = [None] * 5
    k = (trick + 1) % 5
    if trick >= 0:
        first = (row[(k + 1) % 5][0], row[(k + 1) % 5][1] ^ 1)
        out[k] = graph.xor(row[k], graph.and_value(first, row[(k + 2) % 5], 0))
    for x in range(5):
        if not need >> x & 1 or (trick >= 0 and x == k):
            continue
        first = out[k] if x == trick else row[(x + 1) % 5]
        first = (first[0], first[1] ^ 1)
        out[x] = graph.xor(row[x], graph.and_value(first, row[(x + 2) % 5], 0))
    return out

def theta(graph, state, cnot, dnot):
    parity = [None] * 320
    delta = [None] * 320
    for x in range(5):
        for z in range(64):
            value = state[64 * x + z]
            for y in range(1, 5):
                value = graph.xor(value, state[64 * (x + 5 * y) + z])
            if cnot is not None and cnot[64 * x + z]:
                value = graph.complement(value)
            parity[64 * x + z] = value
    for x in range(5):
        for z in range(64):
            value = graph.xor(parity[64 * ((x + 4) % 5) + z], parity[64 * ((x + 1) % 5) + (z + 63 & 63)])
            if dnot is not None and dnot[64 * x + z]:
                value = graph.complement(value)
            delta[64 * x + z] = value
    return delta

def build_prefix(plan):
    graph = Graph(256, True)
    state = [(NC, KL[lane] >> z & 1) for lane in range(25) for z in range(64)]
    for z in range(64):
        state[64 + z] = (z, 0)
        state[6 * 64 + z] = (64 + z, 0)
        state[4 * 64 + z] = (128 + z, 0)
        state[9 * 64 + z] = (192 + z, 0)
        state[11 * 64 + z] = graph.xor(graph.xor((z, 0), (64 + z, 0)), (NC, KL[11] >> z & 1))
        state[14 * 64 + z] = graph.xor(graph.xor((128 + z, 0), (192 + z, 0)), (NC, KL[14] >> z & 1))
    for round_index in range(2):
        delta = theta(graph, state, plan[0] if round_index else None, plan[1] if round_index else None)
        new_state = list(state)
        for y_out in range(5):
            for z in range(64):
                row = []
                for x_out in range(5):
                    y = x_out
                    x = (3 * y_out + x_out) % 5
                    zz = z - RHO[x + 5 * y] & 63
                    row.append(graph.xor(state[64 * (x + 5 * y) + zz], delta[64 * x + zz]))
                out = dynamic_row(graph, row, 31)
                for x_out in range(5):
                    new_state[64 * (x_out + 5 * y_out) + z] = out[x_out]
        for z in range(64):
            n, p = new_state[z]
            new_state[z] = (n, p ^ RC[round_index] >> z & 1)
        state = new_state
    if any((value[0] == NC for value in state)):
        raise AssertionError('constant prefix output')
    return (graph, [v[0] for v in state], bytes((v[1] for v in state)))

def lazy_delta(graph, state, parity, delta, cnot, dnot, x, z):

    def get_parity(px, pz):
        index = 64 * px + pz
        if parity[index] is None:
            value = state[64 * px + pz]
            for py in range(1, 5):
                value = graph.xor(value, state[64 * (px + 5 * py) + pz])
            if cnot is not None and cnot[index]:
                value = graph.complement(value)
            parity[index] = value
        return parity[index]
    index = 64 * x + z
    if delta[index] is None:
        value = graph.xor(get_parity((x + 4) % 5, z), get_parity((x + 1) % 5, z + 63 & 63))
        if dnot is not None and dnot[index]:
            value = graph.complement(value)
        delta[index] = value
    return delta[index]

def allocate(graph, outputs, output_regs, input_regs):
    count = len(graph.op)
    input_count = len(input_regs)
    live = bytearray(count)
    output_index = [-1] * count
    reserved = bytearray(NREG)
    for j, node in enumerate(outputs):
        if node < input_count or output_index[node] >= 0:
            raise AssertionError('invalid/shared output')
        live[node] = 1
        output_index[node] = j
        reserved[output_regs[j]] = 1
    for i in range(count - 1, input_count - 1, -1):
        if live[i]:
            live[graph.a[i]] = 1
            if graph.op[i] != O_NOT:
                live[graph.b[i]] = 1
    last = [0] * count
    for i in range(input_count, count):
        if live[i]:
            last[graph.a[i]] = i
            if graph.op[i] != O_NOT:
                last[graph.b[i]] = i
    for node in outputs:
        last[node] = 65535
    reg = [0] * count
    busy = bytearray(NREG)
    for j, physical in enumerate(input_regs):
        reg[j] = physical
        if last[j]:
            busy[physical] = 1
    free_regs = [r for r in range(NREG - 1, -1, -1) if not busy[r] and (not reserved[r])]
    program = []
    mix = [0, 0, 0, 0]
    for i in range(input_count, count):
        if not live[i]:
            continue
        op = graph.op[i]
        a = graph.a[i]
        b = a if op == O_NOT else graph.b[i]
        if last[a] == i:
            physical = reg[a]
            busy[physical] = 0
            if not reserved[physical]:
                free_regs.append(physical)
        if b != a and last[b] == i:
            physical = reg[b]
            busy[physical] = 0
            if not reserved[physical]:
                free_regs.append(physical)
        if output_index[i] >= 0:
            destination = output_regs[output_index[i]]
            if busy[destination]:
                raise AssertionError('fixed output register busy')
        else:
            destination = free_regs.pop()
        busy[destination] = 1
        reg[i] = destination
        encoded = 0 if op == O_XOR else 1 if op == O_AND else 2 if op == O_OR else 3
        program.append((encoded, destination, reg[a], 0 if op == O_NOT else reg[graph.b[i]]))
        mix[encoded] += 1
    return (program, tuple(mix))

def _hex_bits(text, count):
    value = int.from_bytes(bytes.fromhex(text), 'little')
    return bytes((value >> bit & 1 for bit in range(count)))

def _row_choice(row, need):
    """Return the cheapest complement subset and 10-gate position."""
    distinct = all((value[0] != NC for value in row)) and len({value[0] for value in row}) == 5
    winner = None
    for trick in range(-1, 5 if distinct else 0):
        if trick >= 0 and (not need >> trick & 1 or not need >> (trick + 1) % 5 & 1):
            continue
        for subset in range(32):
            values = list(row)
            cost = 0
            for x in range(5):
                if subset >> x & 1:
                    if row[x][0] == NC:
                        cost = 1 << 29
                    else:
                        values[x] = (values[x][0], values[x][1] ^ 1)
                        cost += 1
            for x in range(5):
                if not need >> x & 1:
                    continue
                if x == trick:
                    k = (trick + 1) % 5
                    left = values[(k + 1) % 5]
                    right = values[(k + 2) % 5]
                    if left[1] ^ 1 == right[1]:
                        substitute = (values[k][0], values[k][1] ^ (left[1] ^ 1))
                        cost += term_cost(substitute, values[(x + 2) % 5])
                    else:
                        cost += 1
                else:
                    cost += term_cost(values[(x + 1) % 5], values[(x + 2) % 5])
            candidate = (cost, subset, trick)
            if winner is None or candidate[0] < winner[0]:
                winner = candidate
    return (winner[1], winner[2])

def _selected_terms(pattern, subset, trick, compact):
    """Expand compact mixed-term polarity bits into one bit per output."""
    polarity = [pattern >> x & 1 ^ subset >> x & 1 for x in range(5)]
    selected = [0] * 5
    output_polarity = [0] * 5
    bit = 0
    k = (trick + 1) % 5
    for x in range(5):
        if x == trick:
            continue
        left = polarity[(x + 1) % 5] ^ 1
        right = polarity[(x + 2) % 5]
        term = left if left == right else compact >> bit & 1
        if left != right:
            selected[x] = term
            bit += 1
        output_polarity[x] = polarity[x] ^ term
    if trick >= 0:
        left = output_polarity[k] ^ 1
        right = polarity[(trick + 2) % 5]
        if left != right:
            selected[trick] = compact >> bit & 1
    return selected

def _emit_planned_row(graph, row, subset, trick, selected, need=31):
    values = list(row)
    for x in range(5):
        if subset >> x & 1:
            values[x] = graph.complement(values[x])
    output = [None] * 5
    k = (trick + 1) % 5
    if trick >= 0:
        first = (values[(k + 1) % 5][0], values[(k + 1) % 5][1] ^ 1)
        term = graph.and_value(first, values[(k + 2) % 5], selected[k])
        output[k] = graph.xor(values[k], term)
    for x in range(5):
        if not need >> x & 1 or (trick >= 0 and x == k):
            continue
        first = output[k] if x == trick else values[(x + 1) % 5]
        first = (first[0], first[1] ^ 1)
        term = graph.and_value(first, values[(x + 2) % 5], selected[x])
        output[x] = graph.xor(values[x], term)
    return output


# ---- Chained 10-gate rows (this derivative). The identity ~out[k] & b[k+1] == ~b[k] & b[k+1] holds for every
# position, so a row may compute several outputs from already-computed outputs; the chain is resolved from a
# plainly computed position backwards. The table below is the least cost over complement subset, trick set
# and mixed-term polarities for every (input pattern, output polarity vector), built once and verified
# against chi on every input value before use. Rows are built from it with the frozen plan's output vector
# pinned, so the polarity flow into the next round is unchanged.

PLAN_DELTA = {9: (177,)}   # D complement flipped in the closing body's round (index 64*x+z: x=2, z=49)

def _chain_order(tricks):
    start = next((x for x in range(5) if not tricks >> x & 1))
    return [(start - i) % 5 for i in range(5)]

def _row_cost(pattern, subset, tricks, selected):
    pol = [(pattern >> x & 1) ^ (subset >> x & 1) for x in range(5)]
    cost = bin(subset).count('1')
    q = [None] * 5
    for x in _chain_order(tricks):
        lit = (q[(x + 1) % 5] ^ 1) if tricks >> x & 1 else (pol[(x + 1) % 5] ^ 1)
        other = pol[(x + 2) % 5]
        if lit == other:
            cost += 1
            term = other
        else:
            cost += 2
            term = selected >> x & 1
        q[x] = pol[x] ^ term
    return (cost, sum((q[x] << x for x in range(5))))

def _row_check(pattern, subset, tricks, selected, bits):
    """Execute the construction on concrete bits through the polarity interpretation; return chi outputs."""
    w = [(bits >> x & 1) ^ (pattern >> x & 1) for x in range(5)]
    pol = [pattern >> x & 1 for x in range(5)]
    for x in range(5):
        if subset >> x & 1:
            w[x] ^= 1
            pol[x] ^= 1
    ow, op = [None] * 5, [None] * 5
    for x in _chain_order(tricks):
        if tricks >> x & 1:
            lw, lp = ow[(x + 1) % 5], op[(x + 1) % 5] ^ 1
        else:
            lw, lp = w[(x + 1) % 5], pol[(x + 1) % 5] ^ 1
        rw, rp = w[(x + 2) % 5], pol[(x + 2) % 5]
        if lp == rp:
            tw, tp = (lw & rw, 0) if lp == 0 else (lw | rw, 1)
        else:
            pw, ow_ = (lw, rw) if lp == 0 else (rw, lw)
            tw, tp = ((pw ^ 1) | ow_, 1) if selected >> x & 1 else (pw ^ (pw & ow_), 0)
        ow[x], op[x] = w[x] ^ tw, pol[x] ^ tp
    return [ow[x] ^ op[x] for x in range(5)], sum((op[x] << x for x in range(5)))

_CHAIN_TABLE = None

def _chained_table():
    global _CHAIN_TABLE
    if _CHAIN_TABLE is None:
        table = {}
        for pattern in range(32):
            for subset in range(32):
                for tricks in range(31):
                    for selected in range(32):
                        cost, q = _row_cost(pattern, subset, tricks, selected)
                        key = (pattern, q)
                        cand = (cost, bin(tricks).count('1'), bin(subset).count('1'), subset, tricks, selected)
                        if key not in table or cand < table[key]:
                            table[key] = cand
        if len(table) != 1024:
            raise AssertionError('chained row table is incomplete')
        for (pattern, q), (cost, _, _, subset, tricks, selected) in table.items():
            for bits in range(32):
                b = [bits >> x & 1 for x in range(5)]
                truth = [b[x] ^ (b[(x + 1) % 5] ^ 1) & b[(x + 2) % 5] for x in range(5)]
                values, qq = _row_check(pattern, subset, tricks, selected, bits)
                if values != truth or qq != q:
                    raise AssertionError('chained row construction does not compute chi')
        _CHAIN_TABLE = table
    return _CHAIN_TABLE

def _emit_row_chained(graph, row, subset, tricks, selected):
    values = list(row)
    for x in range(5):
        if subset >> x & 1:
            values[x] = graph.complement(values[x])
    output = [None] * 5
    for x in _chain_order(tricks):
        first = output[(x + 1) % 5] if tricks >> x & 1 else values[(x + 1) % 5]
        first = (first[0], first[1] ^ 1)
        term = graph.and_value(first, values[(x + 2) % 5], selected >> x & 1)
        output[x] = graph.xor(values[x], term)
    return output

def _public_body(input_p, cnot, dnot, decisions, folded_iota, output_not=None, pinned=None, record=None):
    graph = Graph(1600)
    state = [(plane, input_p[plane]) for plane in range(1600)]
    output_state = list(state)
    parity = [None] * 320
    delta = [None] * 320
    for y_out in range(5):
        for z in range(64):
            row = []
            for x_out in range(5):
                y = x_out
                x = (3 * y_out + x_out) % 5
                zz = z - RHO[x + 5 * y] & 63
                d = lazy_delta(graph, state, parity, delta, cnot, dnot, x, zz)
                row.append(graph.xor(state[64 * (x + 5 * y) + zz], d))
            pattern = sum((value[1] << x for x, value in enumerate(row)))
            if pinned is None:
                decision = decisions[64 * y_out + z]
                subset = decision & 31
                trick = (decision >> 5 & 7) - 1
                selected = _selected_terms(pattern, subset, trick, decision >> 8)
                built = _emit_planned_row(graph, row, subset, trick, selected)
            else:
                subset, tricks, selected = _chained_table()[pattern, pinned[64 * y_out + z]][3:]
                built = _emit_row_chained(graph, row, subset, tricks, selected)
            if record is not None:
                record.append(sum((built[x][1] << x for x in range(5))))
            for x_out in range(5):
                value = built[x_out]
                if output_not is not None and output_not[64 * y_out + z] >> x_out & 1:
                    value = graph.complement(value)
                output_state[64 * (x_out + 5 * y_out) + z] = value
    for z in range(64):
        node, polarity = output_state[z]
        output_state[z] = (node, polarity ^ folded_iota >> z & 1)
    return (graph, [value[0] for value in output_state], bytes((value[1] for value in output_state)))

def _public_end(input_p, cnot, dnot, phi):
    graph = Graph(1600)
    state = [(plane, input_p[plane]) for plane in range(1600)]
    parity = [None] * 320
    delta = [None] * 320
    nodes = [0] * 256
    polarities = bytearray(256)
    for z in range(64):
        row = []
        for x_out in range(5):
            x = y = x_out
            zz = z - RHO[x + 5 * y] & 63
            d = lazy_delta(graph, state, parity, delta, cnot, dnot, x, zz)
            row.append(graph.xor(state[64 * (x + 5 * y) + zz], d))
        subset, trick = _row_choice(row, 15)
        values = list(row)
        for x in range(5):
            if subset >> x & 1:
                values[x] = (values[x][0], values[x][1] ^ 1)
        selected = [phi[64 * x + z] for x in range(5)]
        if trick >= 0:
            k = (trick + 1) % 5
            left = values[(k + 1) % 5]
            right = values[(k + 2) % 5]
            selected[k] = values[(trick + 2) % 5][1] ^ 1 ^ values[k][1] if left[1] ^ 1 != right[1] else 0
        built = _emit_planned_row(graph, row, subset, trick, selected, 15)
        for x_out in range(4):
            node, polarity = built[x_out]
            if x_out == 0:
                polarity ^= RC[23] >> z & 1
            index = 64 * x_out + z
            nodes[index] = node
            polarities[index] = polarity
    return (graph, nodes, bytes(polarities))

def reproduce_public_step(plan_path='step-plan.txt'):
    plan = _public_plan(plan_path)
    f1 = _hex_bits(plan['F1'], 320)
    g1 = _hex_bits(plan['G1'], 320)
    graph, outputs, prefix_p = build_prefix((g1, f1, bytes(320)))
    programs = {}
    programs['P'], prefix_mix = allocate(graph, outputs, list(range(256, 1856)), list(range(256)))
    body_counts = []
    body_mixes = []
    input_p = prefix_p
    round22_p = None
    folded = []
    for body in range(8):
        round_index = body + 2
        fg = plan['FG', round_index]
        dnot = _hex_bits(fg[0], 320)
        cnot = _hex_bits(fg[1], 320)
        raw = bytes.fromhex(plan['DEC', round_index])
        decisions = [raw[2 * index] | raw[2 * index + 1] << 8 for index in range(320)]
        iota = int(plan['IB', body], 16)
        folded.append(iota)
        output_not = None
        if body == 7:
            output_not = bytes.fromhex(plan['ONOT', round_index])
        pinned = []
        _public_body(input_p, cnot, dnot, decisions, iota, output_not, record=pinned)
        for index in PLAN_DELTA.get(round_index, ()):
            dnot = bytes((bit ^ (1 if i == index else 0) for i, bit in enumerate(dnot)))
        graph, outputs, output_p = _public_body(input_p, cnot, dnot, decisions, iota, output_not, pinned=pinned)
        input_base = 1856 if body & 1 else 256
        output_base = 256 if body & 1 else 1856
        program, mix = allocate(graph, outputs, list(range(output_base, output_base + 1600)), list(range(input_base, input_base + 1600)))
        programs[f'B{body + 1}'] = program
        body_counts.append(len(program))
        body_mixes.append(mix)
        input_p = output_p
        if body == 4:
            round22_p = output_p
    if input_p != prefix_p:
        raise AssertionError('the eight-body polarity cycle does not close')
    fg = plan['FG', 23]
    phi = _hex_bits(plan['PHI', 23], 1600)
    graph, outputs, end_p = _public_end(round22_p, _hex_bits(fg[1], 320), _hex_bits(fg[0], 320), phi)
    programs['E'], end_mix = allocate(graph, outputs, list(range(256)), list(range(1856, 3456)))
    pd = tuple((sum((end_p[64 * lane + bit] << bit for bit in range(64))) for lane in range(4)))
    runs = (3, 3, 3, 3, 3, 2, 2, 2)
    iota_ops = sum(((RC[round_index] ^ folded[(round_index - 2) % 8]).bit_count() for round_index in range(2, 23)))
    calls_and_returns = 42
    executed = len(programs['P']) + len(programs['E']) + iota_ops + calls_and_returns
    executed += sum((runs[index] * body_counts[index] for index in range(8)))
    prog_instructions = len(programs['P']) + len(programs['E']) + 21 + iota_ops
    body_instructions = sum(body_counts) + 8
    result = {'prefix': len(programs['P']), 'prefix_mix': prefix_mix, 'bodies': body_counts, 'body_mixes': body_mixes, 'end': len(programs['E']), 'end_mix': end_mix, 'iota': iota_ops, 'calls_and_returns': calls_and_returns, 'executed': executed, 'prog_instructions': prog_instructions, 'body_instructions': body_instructions, 'stored_instructions': prog_instructions + body_instructions, 'pd': pd}
    return (programs, result)

def emit_public_binaries(programs, plan_path='step-plan.txt'):
    """Pack the two static step blocks in the declared 39-bit format."""
    plan = _public_plan(plan_path)
    folded = [int(plan['IB', body], 16) for body in range(8)]
    body_words = []
    offsets = []
    for body in range(8):
        offsets.append(len(body_words))
        body_words.extend(programs[f'B{body + 1}'])
        body_words.append((5, 0, 3528, 0))
    prog_words = list(programs['P'])
    for round_index in range(2, 23):
        body = (round_index - 2) % 8
        offset = offsets[body]
        prog_words.append((4, 3528, offset & 4095, offset >> 12))
        output_base = 1856 if not body & 1 else 256
        difference = RC[round_index] ^ folded[body]
        for bit in range(64):
            if difference >> bit & 1:
                prog_words.append((3, output_base + bit, output_base + bit, 0))
    prog_words.extend(programs['E'])
    if len(prog_words) != 6811 or len(body_words) != 53064:
        raise AssertionError('packed block instruction count mismatch')

    def pack39(words):
        output = bytearray()
        accumulator = 0
        bits = 0
        for opcode, destination, left, right in words:
            if opcode >= 8 or max(destination, left, right) >= 4096:
                raise AssertionError('packed instruction field overflow')
            accumulator |= (opcode | destination << 3 | left << 15 | right << 27) << bits
            bits += 39
            while bits >= 8:
                output.append(accumulator & 255)
                accumulator >>= 8
                bits -= 8
        if bits:
            output.append(accumulator)
        return bytes(output)
    return (pack39(prog_words), pack39(body_words))

EXPECTED_PROG = 'de85b18a14cfd66b9916d350a5e72fef6225cc57fdb4e06fa32539de58bbf6de'
EXPECTED_BODY = 'fc869df5cba74abcf373ae4b112f236c423f798320820f8d460bf8c18f37a33b'
def generate():
 programs,result = reproduce_public_step()
 prog,body = emit_public_binaries(programs)
 if len(prog)!=33204 or hashlib.sha256(prog).hexdigest()!=EXPECTED_PROG: raise AssertionError('prog mismatch')
 if len(body)!=258687 or hashlib.sha256(body).hexdigest()!=EXPECTED_BODY: raise AssertionError('body mismatch')
 if result['executed']!=145974 or result['stored_instructions']!=59875: raise AssertionError('ledger mismatch')
 return prog,body,result
def main():
 prog,body,result = generate()
 if len(sys.argv)==2:
  from pathlib import Path
  out=Path(sys.argv[1]); out.mkdir(parents=True,exist_ok=True); (out/'prog.bin').write_bytes(prog); (out/'body.bin').write_bytes(body)
 print(json.dumps({'prog_sha256':hashlib.sha256(prog).hexdigest(),'body_sha256':hashlib.sha256(body).hexdigest(),**result},sort_keys=True))
```

## Appendix C. Normative controller emitter (inherited verbatim from 911bffce, its Appendix C; unchanged)

```python
#!/usr/bin/env python3
"""Emitter for the compact r24 search controller.

The step keeps its 256 carried planes in registers.  On a distinguished-point
hit, this controller copies those planes to a 256-word scratch matrix.  Two
small indexed loops then gather one lane or replace one lane.  Static loads
restore the planes before the next step.  The rare handler does more work, but
the retained 32-byte control image is much smaller than two fully unrolled
bit-matrix routines.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


MASK256 = (1 << 256) - 1
MASK64 = (1 << 64) - 1
UNIT = 6_504
LNK = 3_528


class Op(IntEnum):
    XOR = 0
    AND = 1
    OR = 2
    NOT = 3
    ADD = 4
    SUB = 5
    SHL = 6
    SHR = 7
    EQ = 8
    LT = 9
    MOV = 10
    ADDI = 11
    SUBI = 12
    SHLI = 13
    SHRI = 14
    ANDI = 15
    EQI = 16
    LTI = 17
    MOVI = 18
    LD = 19
    ST = 20
    LDA = 21
    BNZ = 22
    BZ = 23
    JMP = 24
    JAL = 25
    JR = 26
    RND = 27
    PERM = 28
    HALT = 29


COMPARE_OPS = {Op.EQ, Op.LT, Op.EQI, Op.LTI}

# Persistent search registers.
R_COUNTER = LNK + 1
R_NEXT_ID = LNK + 2
R_RHO = LNK + 3
R_ONES = LNK + 4
R_PREFILTER = LNK + 5
R_HITS = LNK + 6
R_LINK = LNK + 7
R_LINK2 = LNK + 8
R_ZERO = LNK + 9

# Handler temporaries.  Step temporaries are dead while the handler runs.
R_LANE = 256
R_DPM = 257
R_C1 = 258
R_ACC = 259
R_TMP = 260
R_RECORD = 261
R_SLOT = 262
R_WORD = 263
R_FLAG = 264
R_X = 265
R_Y = 266
R_POINT = 267
R_MASK = 268
R_PTR = 269
R_INDEX = 270
R_ID = 271
R_REPEATED = 272
R_ONEBIT = 273
R_P = 280
R_Q = 281
R_N = 282
R_MIN = 283
R_LA = 284
R_LB = 285
R_U = 286
R_F = 287
R_FP = 288
R_PD = 289
R_X0 = 290
R_X1 = 291
R_X2 = 292
R_X3 = 293
R_TQ = 294
R_STATE = 300
NREGS = LNK + 12


@dataclass(frozen=True)
class Layout:
    table_words: int
    slots_per_word: int = 5
    slot_bits: int = 51

    def __post_init__(self):
        if self.table_words < 264 or self.table_words % 8:
            raise ValueError("table_words must be a multiple of eight and at least 264")
        if self.slots_per_word * self.slot_bits > 256:
            raise ValueError("slots do not fit one word")
        if self.slot_bits < 2:
            raise ValueError("a slot needs a written bit and at least one key bit")

    @property
    def key_bits(self) -> int:
        return self.slot_bits - 1

    @property
    def capacity(self) -> int:
        return self.table_words * self.slots_per_word

    @property
    def home_bits(self) -> int:
        return self.table_words.bit_length()

    @property
    def scratch(self) -> int:
        return self.table_words

    @property
    def lane_ids(self) -> int:
        return self.scratch + 256

    @property
    def lane_starts(self) -> int:
        return self.lane_ids + 256

    @property
    def data(self) -> int:
        return self.lane_starts + 256

    @property
    def memory_words(self) -> int:
        return self.data + 16


def trail_number(index: int, layout: Layout) -> int:
    if not 0 <= index < layout.capacity:
        raise ValueError("trail index is outside the table capacity")
    word = index % layout.table_words
    slot = index // layout.table_words
    return word | ((layout.slot_bits * slot) << layout.home_bits)


def decode_trail_number(number: int, layout: Layout) -> tuple[int, int]:
    word = number & ((1 << layout.home_bits) - 1)
    shift = number >> layout.home_bits
    if word >= layout.table_words or shift % layout.slot_bits:
        raise ValueError("invalid encoded trail number")
    slot = shift // layout.slot_bits
    if slot >= layout.slots_per_word:
        raise ValueError("invalid encoded trail slot")
    return word, slot


def record_for_key(key: int, layout: Layout) -> int:
    if not 0 <= key < 1 << layout.key_bits:
        raise ValueError("key does not fit the record")
    return 1 | (key << 1)


def slot_value(word: int, slot: int, layout: Layout) -> int:
    if not 0 <= slot < layout.slots_per_word:
        raise ValueError("slot is outside the word")
    return (word >> (slot * layout.slot_bits)) & ((1 << layout.slot_bits) - 1)


@dataclass
class Instruction:
    op: Op
    d: int = 0
    a: int = 0
    b: int = 0
    imm: int = 0

    def encode(self) -> bytes:
        if not (0 <= self.d < 1 << 16 and 0 <= self.a < 1 << 16 and 0 <= self.b < 1 << 16):
            raise ValueError("register field does not fit 16 bits")
        if not 0 <= self.imm < 1 << 192:
            raise ValueError("immediate does not fit 192 bits")
        return (
            bytes([int(self.op)])
            + self.d.to_bytes(2, "little")
            + self.a.to_bytes(2, "little")
            + self.b.to_bytes(2, "little")
            + b"\0"
            + self.imm.to_bytes(24, "little")
        )


class Assembly:
    def __init__(self, layout: Layout):
        self.layout = layout
        self.instructions: list[Instruction] = []
        self.labels: dict[str, int] = {}
        self.fixups: list[tuple[int, str]] = []

    def label(self, name: str) -> None:
        if name in self.labels:
            raise ValueError(f"duplicate label {name}")
        self.labels[name] = len(self.instructions)

    def emit(self, op: Op, d=0, a=0, b=0, imm=0, target: Optional[str] = None):
        self.instructions.append(Instruction(op, d, a, b, imm))
        if target is not None:
            self.fixups.append((len(self.instructions) - 1, target))

    def binary(self, op: Op, d: int, a: int, b: int):
        self.emit(op, d, a, b)

    def immediate(self, op: Op, d: int, a: int, imm: int):
        self.emit(op, d, a, 0, imm)

    def mov(self, d, a): self.emit(Op.MOV, d, a)
    def movi(self, d, value): self.emit(Op.MOVI, d, imm=value)
    def add(self, d, a, b): self.binary(Op.ADD, d, a, b)
    def sub(self, d, a, b): self.binary(Op.SUB, d, a, b)
    def xor(self, d, a, b): self.binary(Op.XOR, d, a, b)
    def and_(self, d, a, b): self.binary(Op.AND, d, a, b)
    def or_(self, d, a, b): self.binary(Op.OR, d, a, b)
    def shl(self, d, a, b): self.binary(Op.SHL, d, a, b)
    def shr(self, d, a, b): self.binary(Op.SHR, d, a, b)
    def not_(self, d, a): self.emit(Op.NOT, d, a)
    def addi(self, d, a, value): self.immediate(Op.ADDI, d, a, value)
    def subi(self, d, a, value): self.immediate(Op.SUBI, d, a, value)
    def shli(self, d, a, value): self.immediate(Op.SHLI, d, a, value)
    def shri(self, d, a, value): self.immediate(Op.SHRI, d, a, value)
    def andi(self, d, a, value): self.immediate(Op.ANDI, d, a, value)
    def ld(self, d, base, offset=0): self.immediate(Op.LD, d, base, offset)
    def st(self, base, offset, source): self.emit(Op.ST, 0, base, source, offset)
    def lda(self, d, address): self.emit(Op.LDA, d, imm=address)
    def jmp(self, target): self.emit(Op.JMP, target=target)
    def jal(self, link, target): self.emit(Op.JAL, d=link, target=target)
    def jr(self, link): self.emit(Op.JR, a=link)
    def halt(self, code): self.emit(Op.HALT, imm=code)

    def _branch(self, op: Op, target: str):
        self.emit(op, a=R_FLAG, target=target)

    def jeqi(self, a, value, target):
        self.immediate(Op.EQI, R_FLAG, a, value); self._branch(Op.BNZ, target)

    def jnei(self, a, value, target):
        self.immediate(Op.EQI, R_FLAG, a, value); self._branch(Op.BZ, target)

    def jlti(self, a, value, target):
        self.immediate(Op.LTI, R_FLAG, a, value); self._branch(Op.BNZ, target)

    def jgei(self, a, value, target):
        self.immediate(Op.LTI, R_FLAG, a, value); self._branch(Op.BZ, target)

    def jeq(self, a, b, target):
        self.binary(Op.EQ, R_FLAG, a, b); self._branch(Op.BNZ, target)

    def jne(self, a, b, target):
        self.binary(Op.EQ, R_FLAG, a, b); self._branch(Op.BZ, target)

    def jlt(self, a, b, target):
        self.binary(Op.LT, R_FLAG, a, b); self._branch(Op.BNZ, target)

    def resolve(self):
        for index, target in self.fixups:
            if target == "@STEP":
                self.instructions[index].imm = (1 << 192) - 1
            else:
                self.instructions[index].imm = self.labels[target]
        for index, ins in enumerate(self.instructions):
            if max(ins.d, ins.a, ins.b) >= NREGS:
                raise ValueError(f"instruction {index} names register outside the file")
            if ins.op in {Op.BNZ, Op.BZ}:
                previous = self.instructions[index - 1]
                if previous.op not in COMPARE_OPS or previous.d != ins.a:
                    raise ValueError(f"branch {index} does not follow its comparison")


def _emit_message_state(a: Assembly, data: int):
    for word in range(7):
        a.ld(R_STATE + word, R_ZERO, data + word)
    a.andi(R_X0, R_U, MASK64)
    a.shri(R_X1, R_U, 64); a.andi(R_X1, R_X1, MASK64)
    a.shri(R_X2, R_U, 128); a.andi(R_X2, R_X2, MASK64)
    a.shri(R_X3, R_U, 192)
    a.shli(R_TQ, R_X0, 64); a.xor(R_STATE, R_STATE, R_TQ)
    a.shli(R_TQ, R_X1, 128); a.xor(R_STATE + 1, R_STATE + 1, R_TQ)
    a.xor(R_STATE + 1, R_STATE + 1, R_X2)
    a.shli(R_TQ, R_X3, 64); a.xor(R_STATE + 2, R_STATE + 2, R_TQ)
    a.xor(R_TQ, R_X0, R_X1); a.shli(R_TQ, R_TQ, 192); a.xor(R_STATE + 2, R_STATE + 2, R_TQ)
    a.xor(R_TQ, R_X2, R_X3); a.shli(R_TQ, R_TQ, 128); a.xor(R_STATE + 3, R_STATE + 3, R_TQ)


def build_program(
    layout: Layout,
    *,
    replay_cap: int = 43_210_406_009_979_655_608_818_122_161_651_712,
    tb: int = 1_326_345_234_525_992_950_706_776_067_278_897_152,
    hit_limit: int = 48_391_447_023_367_850_163_390_149_816_221_697,
    dplo: int = 145,
    dk: int = 10,
    dt: int = 646,
) -> Assembly:
    a = Assembly(layout)
    home_mask = (1 << layout.home_bits) - 1
    slot_mask = (1 << layout.slot_bits) - 1
    limit = trail_number(layout.capacity - 1, layout)
    limit += 1
    if layout.capacity % layout.table_words == 0:
        limit = layout.slot_bits * layout.slots_per_word << layout.home_bits
    threshold = dt << (dplo - dk)

    a.label("start")
    a.emit(Op.RND, d=R_RHO)
    a.movi(R_NEXT_ID, trail_number(256, layout))
    a.movi(R_HITS, 0); a.movi(R_COUNTER, 0); a.movi(R_ZERO, 0); a.not_(R_ONES, R_ZERO)
    a.movi(R_PTR, 0)
    a.label("clear")
    for offset in range(8):
        a.st(R_PTR, offset, R_ZERO)
    a.addi(R_PTR, R_PTR, 8); a.jlti(R_PTR, layout.table_words + 256, "clear")
    a.movi(R_LANE, 0)
    a.label("initial_walks")
    a.add(R_POINT, R_RHO, R_LANE)
    a.st(R_LANE, layout.lane_ids, R_LANE)
    a.st(R_LANE, layout.lane_starts, R_ZERO)
    a.jal(R_LINK, "setwalk")
    a.addi(R_LANE, R_LANE, 1); a.jlti(R_LANE, 256, "initial_walks")
    a.jal(R_LINK, "restore_planes")
    a.jmp("@STEP")

    a.label("loop")
    a.jeq(R_PREFILTER, R_ONES, "continue")
    a.label("hit")
    a.addi(R_HITS, R_HITS, 1); a.jlti(R_HITS, hit_limit + 1, "hit_ok"); a.halt(10)
    a.label("hit_ok")
    a.or_(R_TMP, dplo, dplo + 1)
    for plane in range(dplo + 2, 240):
        a.or_(R_TMP, R_TMP, plane)
    a.or_(R_DPM, R_PREFILTER, R_TMP); a.not_(R_DPM, R_DPM)
    bits = [(dt >> (dk - 1 - i)) & 1 for i in range(dk)]
    last_one = max(i for i, bit in enumerate(bits) if bit)
    first = True
    for i in range(last_one + 1):
        plane = dplo - 1 - i
        a.not_(R_X, plane)
        if bits[i]:
            if first:
                a.and_(R_Y, R_DPM, R_X); first = False
            else:
                a.and_(R_X, R_DPM, R_X); a.or_(R_Y, R_Y, R_X)
            if i < last_one:
                a.and_(R_DPM, R_DPM, plane)
        else:
            a.and_(R_DPM, R_DPM, R_X)
    a.mov(R_DPM, R_Y)
    a.addi(R_C1, R_COUNTER, 1)
    a.jeqi(R_DPM, 0, "continue")

    a.label("save_planes")
    for plane in range(256):
        a.st(R_ZERO, layout.scratch + plane, plane)
    a.label("dp_loop")
    a.jeqi(R_DPM, 0, "restore_after_hit")
    a.label("one_dp")
    a.movi(R_LANE, 0); a.mov(R_X, R_DPM)
    for i, shift in enumerate((128, 64, 32, 16, 8, 4, 2, 1)):
        a.andi(R_Y, R_X, (1 << shift) - 1)
        a.jnei(R_Y, 0, f"ctz_{i}")
        a.shri(R_X, R_X, shift); a.addi(R_LANE, R_LANE, shift)
        a.label(f"ctz_{i}")
    a.subi(R_Y, R_DPM, 1); a.and_(R_DPM, R_DPM, R_Y)
    a.jal(R_LINK, "gather")

    a.label("record")
    a.andi(R_RECORD, R_ACC, (1 << layout.key_bits) - 1)
    a.shli(R_RECORD, R_RECORD, 1); a.addi(R_RECORD, R_RECORD, 1)
    a.mov(R_REPEATED, R_RECORD)
    for slot in range(1, layout.slots_per_word):
        a.shli(R_X, R_RECORD, layout.slot_bits * slot); a.or_(R_REPEATED, R_REPEATED, R_X)
    a.movi(R_SLOT, 0)
    a.label("probe")
    a.ld(R_WORD, R_SLOT); a.xor(R_WORD, R_WORD, R_REPEATED)
    for slot in range(layout.slots_per_word):
        if slot:
            a.shri(R_Y, R_WORD, layout.slot_bits * slot); a.andi(R_X, R_Y, slot_mask)
        else:
            a.andi(R_X, R_WORD, slot_mask)
        a.jeqi(R_X, 0, f"match_{slot}")
    a.addi(R_SLOT, R_SLOT, 1); a.jnei(R_SLOT, layout.table_words, "probe")

    a.label("insert")
    a.ld(R_ID, R_LANE, layout.lane_ids)
    a.andi(R_SLOT, R_ID, home_mask); a.shri(R_Y, R_ID, layout.home_bits)
    a.shl(R_X, R_RECORD, R_Y)
    a.ld(R_WORD, R_SLOT); a.or_(R_WORD, R_WORD, R_X); a.st(R_SLOT, 0, R_WORD)
    a.label("insert_done")
    a.mov(R_TMP, R_C1); a.jal(R_LINK2, "restart"); a.jmp("dp_loop")

    for slot in range(layout.slots_per_word):
        a.label(f"match_{slot}")
        a.movi(R_X, (layout.slot_bits * slot) << layout.home_bits)
        a.or_(R_X, R_X, R_SLOT); a.jmp("match")

    a.label("restore_after_hit")
    a.jal(R_LINK, "restore_planes")
    a.label("continue")
    a.addi(R_COUNTER, R_COUNTER, 1); a.jnei(R_COUNTER, tb, "@STEP")
    a.label("deadline")
    a.halt(12)

    a.label("restart")
    a.jnei(R_NEXT_ID, limit, "restart_ok"); a.halt(11)
    a.label("restart_ok")
    a.st(R_LANE, layout.lane_ids, R_NEXT_ID); a.st(R_LANE, layout.lane_starts, R_TMP)
    a.add(R_POINT, R_RHO, R_NEXT_ID); a.addi(R_NEXT_ID, R_NEXT_ID, 1)
    a.andi(R_X, R_NEXT_ID, home_mask); a.jnei(R_X, layout.table_words, "restart_nowrap")
    a.addi(R_NEXT_ID, R_NEXT_ID, (layout.slot_bits << layout.home_bits) - layout.table_words)
    a.label("restart_nowrap")
    a.jal(R_LINK, "setwalk"); a.jr(R_LINK2)

    a.label("setwalk")
    a.movi(R_ONEBIT, 1); a.shl(R_ONEBIT, R_ONEBIT, R_LANE); a.not_(R_MASK, R_ONEBIT)
    a.lda(R_PTR, layout.scratch); a.movi(R_INDEX, 0)
    a.label("setwalk_loop")
    a.ld(R_X, R_PTR); a.and_(R_X, R_X, R_MASK)
    a.shr(R_Y, R_POINT, R_INDEX); a.andi(R_Y, R_Y, 1); a.shl(R_Y, R_Y, R_LANE)
    a.or_(R_X, R_X, R_Y); a.st(R_PTR, 0, R_X)
    a.addi(R_PTR, R_PTR, 1); a.addi(R_INDEX, R_INDEX, 1)
    a.jnei(R_INDEX, 256, "setwalk_loop"); a.jr(R_LINK)

    a.label("gather")
    a.movi(R_ACC, 0); a.lda(R_PTR, layout.scratch); a.movi(R_INDEX, 0)
    a.label("gather_loop")
    a.ld(R_X, R_PTR); a.shr(R_X, R_X, R_LANE); a.andi(R_X, R_X, 1)
    a.shl(R_X, R_X, R_INDEX); a.or_(R_ACC, R_ACC, R_X)
    a.addi(R_PTR, R_PTR, 1); a.addi(R_INDEX, R_INDEX, 1)
    a.jnei(R_INDEX, 256, "gather_loop"); a.jr(R_LINK)

    a.label("restore_planes")
    for plane in range(256):
        a.ld(plane, R_ZERO, layout.scratch + plane)
    a.jr(R_LINK)

    a.label("eval_f")
    _emit_message_state(a, layout.data)
    a.emit(Op.PERM, a=R_STATE); a.ld(R_PD, R_ZERO, layout.data + 7); a.xor(R_F, R_STATE, R_PD); a.jr(R_LINK2)
    a.label("output_message")
    _emit_message_state(a, layout.data); a.jr(R_LINK2)

    a.label("match")
    a.ld(R_Y, R_LANE, layout.lane_ids); a.ld(R_LB, R_LANE, layout.lane_starts); a.sub(R_LB, R_C1, R_LB)
    a.jgei(R_LB, replay_cap + 1, "replay_fail")
    a.add(R_P, R_RHO, R_X); a.add(R_Q, R_RHO, R_Y)
    a.mov(R_U, R_P); a.movi(R_LA, 0)
    a.label("measure")
    a.jal(R_LINK2, "eval_f"); a.addi(R_LA, R_LA, 1); a.jlti(R_F, threshold, "measured")
    a.jgei(R_LA, replay_cap, "replay_fail"); a.mov(R_U, R_F); a.jmp("measure")
    a.label("measured")
    a.jlt(R_LA, R_LB, "advance_q"); a.sub(R_N, R_LA, R_LB); a.mov(R_MIN, R_LB)
    a.label("advance_p")
    a.jeqi(R_N, 0, "lock"); a.mov(R_U, R_P); a.jal(R_LINK2, "eval_f"); a.mov(R_P, R_F); a.subi(R_N, R_N, 1); a.jmp("advance_p")
    a.label("advance_q")
    a.sub(R_N, R_LB, R_LA); a.mov(R_MIN, R_LA)
    a.label("advance_q_loop")
    a.jeqi(R_N, 0, "lock"); a.mov(R_U, R_Q); a.jal(R_LINK2, "eval_f"); a.mov(R_Q, R_F); a.subi(R_N, R_N, 1); a.jmp("advance_q_loop")
    a.label("lock")
    a.jeq(R_P, R_Q, "replay_fail")
    a.label("lock_loop")
    a.jeqi(R_MIN, 0, "replay_fail")
    a.mov(R_U, R_P); a.jal(R_LINK2, "eval_f"); a.mov(R_FP, R_F)
    a.mov(R_U, R_Q); a.jal(R_LINK2, "eval_f"); a.jeq(R_FP, R_F, "found")
    a.mov(R_P, R_FP); a.mov(R_Q, R_F); a.subi(R_MIN, R_MIN, 1); a.jmp("lock_loop")
    a.label("found")
    a.mov(R_U, R_P); a.jal(R_LINK2, "output_message")
    for word in range(4): a.st(R_ZERO, layout.data + 8 + word, R_STATE + word)
    a.mov(R_U, R_Q); a.jal(R_LINK2, "output_message")
    for word in range(4): a.st(R_ZERO, layout.data + 12 + word, R_STATE + word)
    a.halt(1)
    a.label("replay_fail")
    a.halt(13)
    a.label("end")
    a.resolve()
    return a


@dataclass(frozen=True)
class Counts:
    instructions: int
    setwalk: int
    gather: int
    restore: int
    restart: int
    restart_halt: int
    hit: int
    ctz_clear: int
    record_slot: int
    probe_word: int
    insert: int
    dp_fixed: int
    deadline_final: int
    eval_f: int
    output_message: int
    measure_iter: int
    replay_iter: int
    replay_const: int
    setup: int


def counts(a: Assembly, layout: Layout) -> Counts:
    labels = a.labels
    segment = lambda first, last: labels[last] - labels[first]
    setwalk_prefix = segment("setwalk", "setwalk_loop")
    setwalk_body = labels["gather"] - 1 - labels["setwalk_loop"]
    setwalk = setwalk_prefix + 256 * setwalk_body + 1
    gather_prefix = segment("gather", "gather_loop")
    gather_body = labels["restore_planes"] - 1 - labels["gather_loop"]
    gather = gather_prefix + 256 * gather_body + 1
    restore = segment("restore_planes", "eval_f")
    restart_halt = segment("restart", "restart_ok") - 1 + 1
    restart = (segment("restart", "restart_ok") - 1) + segment("restart_ok", "setwalk") + setwalk
    hit = (segment("hit", "hit_ok") - 1) + segment("hit_ok", "save_planes")
    ctz_clear = segment("one_dp", "record") - 1  # omit the call to gather; gather is added below
    record_slot = segment("record", "probe")
    probe_word = segment("probe", "insert")
    insert = segment("insert", "insert_done")
    # The bound charges save and restore for every DP.  A hit with several DPs
    # executes each copy once, so this is a safe per-DP overcount.
    dp_fixed = 2 + 256 + ctz_clear + 1 + gather + record_slot + insert + 3 + 1 + restore
    eval_f = segment("eval_f", "output_message") - 1 + UNIT
    output_message = segment("output_message", "match")
    measure_iter = eval_f + 8
    replay_iter = 2 * eval_f + 13
    replay_const = 79
    # Clear TAB and scratch together, initialize 256 lanes through the looped
    # setwalk, restore the planes, and jump to the packed step.
    clear_iterations = (layout.table_words + 256) // 8
    setup = segment("start", "clear") + clear_iterations * 11 + 1
    setup += 256 * (7 + setwalk) + 1 + restore + 1
    return Counts(
        instructions=len(a.instructions),
        setwalk=setwalk,
        gather=gather,
        restore=restore,
        restart=restart,
        restart_halt=restart_halt,
        hit=hit,
        ctz_clear=ctz_clear,
        record_slot=record_slot,
        probe_word=probe_word,
        insert=insert,
        dp_fixed=dp_fixed,
        deadline_final=segment("deadline", "restart"),
        eval_f=eval_f,
        output_message=output_message,
        measure_iter=measure_iter,
        replay_iter=replay_iter,
        replay_const=replay_const,
        setup=setup,
    )


class Machine:
    """Small interpreter used to execute emitted helper routines in tests."""

    def __init__(self, assembly: Assembly):
        self.assembly = assembly
        self.reg = [0] * NREGS
        self.mem = [0] * assembly.layout.memory_words
        self.pc = 0

    def call_subroutine(self, label: str, *, max_steps: int = 20_000):
        self.reg[R_LINK] = len(self.assembly.instructions)
        self.pc = self.assembly.labels[label]
        steps = 0
        while self.pc != len(self.assembly.instructions):
            if steps >= max_steps:
                raise RuntimeError("subroutine step limit exceeded")
            self.step(); steps += 1
        return steps

    def step(self):
        ins = self.assembly.instructions[self.pc]
        self.pc += 1
        r = self.reg
        op = ins.op
        if op == Op.MOV: r[ins.d] = r[ins.a]
        elif op == Op.MOVI: r[ins.d] = ins.imm
        elif op == Op.XOR: r[ins.d] = r[ins.a] ^ r[ins.b]
        elif op == Op.AND: r[ins.d] = r[ins.a] & r[ins.b]
        elif op == Op.OR: r[ins.d] = r[ins.a] | r[ins.b]
        elif op == Op.NOT: r[ins.d] = r[ins.a] ^ MASK256
        elif op == Op.ADD: r[ins.d] = (r[ins.a] + r[ins.b]) & MASK256
        elif op == Op.SUB: r[ins.d] = (r[ins.a] - r[ins.b]) & MASK256
        elif op == Op.SHL: r[ins.d] = (r[ins.a] << (r[ins.b] & 255)) & MASK256
        elif op == Op.SHR: r[ins.d] = r[ins.a] >> (r[ins.b] & 255)
        elif op == Op.ADDI: r[ins.d] = (r[ins.a] + ins.imm) & MASK256
        elif op == Op.SUBI: r[ins.d] = (r[ins.a] - ins.imm) & MASK256
        elif op == Op.SHLI: r[ins.d] = (r[ins.a] << (ins.imm & 255)) & MASK256
        elif op == Op.SHRI: r[ins.d] = r[ins.a] >> (ins.imm & 255)
        elif op == Op.ANDI: r[ins.d] = r[ins.a] & ins.imm
        elif op == Op.EQ: r[ins.d] = int(r[ins.a] == r[ins.b])
        elif op == Op.LT: r[ins.d] = int(r[ins.a] < r[ins.b])
        elif op == Op.EQI: r[ins.d] = int(r[ins.a] == ins.imm)
        elif op == Op.LTI: r[ins.d] = int(r[ins.a] < ins.imm)
        elif op in {Op.LD, Op.LDA}:
            if op == Op.LDA: r[ins.d] = ins.imm
            else: r[ins.d] = self.mem[r[ins.a] + ins.imm]
        elif op == Op.ST: self.mem[r[ins.a] + ins.imm] = r[ins.b]
        elif op == Op.BNZ:
            if r[ins.a] != 0: self.pc = ins.imm
        elif op == Op.BZ:
            if r[ins.a] == 0: self.pc = ins.imm
        elif op == Op.JMP: self.pc = ins.imm
        elif op == Op.JAL: r[ins.d] = self.pc; self.pc = ins.imm
        elif op == Op.JR: self.pc = r[ins.a]
        else:
            raise RuntimeError(f"unsupported test opcode {op.name}")
        if op not in {Op.ST, Op.BNZ, Op.BZ, Op.JMP, Op.JAL, Op.JR} and ins.d:
            r[ins.d] &= MASK256


if __name__ == "__main__":
    layout = Layout(16_848)
    assembly = build_program(layout)
    c = counts(assembly, layout)
    print(c)
    print(f"other_bytes={32 * c.instructions}")

```

