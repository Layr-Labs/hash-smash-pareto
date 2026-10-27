# Orchard/Pallas Poseidon, 56 partial rounds: bounded distinguished-point search

## 1. Target and status

Let `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`.
`H(nk,rho)` is the entire first field element of the pinned P128Pow5T3 hash
of `[nk,rho,2^65]`, using full rounds 0--3 and 60--63, partial rounds 4--59,
exponent 5, and deployed Orchard constants and MDS. Both inputs and output use
canonical 32-byte little-endian encoding. The proposed algorithm returns two
distinct canonical pairs with the same `rho` and verifies equality of their
complete output elements. It does not use aliases, free capacity, or the
complete Orchard nullifier construction. The certificate manifest is empty:
this is a finite construction and cost claim, not an executed full collision.
The fixed-function probability rests on the score-critical H1 in section 5.

## 2. Algorithm and deterministic recovery

Use one uniform random 256-bit word with its top two bits masked as `rho`.
For each new trail, use another independent masked word as `start`. These
values are less than `2^254 < p` and need no rejection. Define `f(x)=H(x,rho)`.
Each trail iterates `x=f(x)` until its first distinguished *output*, defined
by `x<D`. Cap a trail at `L` calls, and fail if no distinguished output occurs.
The fixed integer parameters are

```
B = ceil(sqrt(p)) = 170141183460469231731687303715884105729
Q = ceil(33*B/32) = 175458095443608895223302531957005484034
L = 2^118 = 332306998946228968225951765070086144
D = ceil(p/2^114) = 1393796574908163946345982392040522594125970
M = 10000 records.
```

Write `R=Q+L+M+1` for an upper bound on all visited states, including
independently sampled starts, in the probability deductions below.

Store `(start, full endpoint, length)` in an 80-byte record (32+32+16).
Scan prior records by their *full* endpoint. If one matches, recover and
verify as below. Otherwise append, unless this exceeds `M`, in which case
fail. Start trails until `Q` hash calls have been made; allow the trail in
progress at that point at most `L` extra calls to finish. If no duplicate
endpoint is found, fail. This is one attempt, with no restarts or parallelism.

For equal endpoints of trails of lengths `a,b <= L`, advance the longer
trail's start by `|a-b|` calls. Both walks now have equal remaining distance
to the endpoint. Step them together, retaining each previous state, until
their first equal state. If this is an aligned start, fail. Otherwise the
previous states `u != v` satisfy `f(u)=f(v)`. Recompute both complete target
hashes and return `(u,rho),(v,rho)` only if all 32 canonical output bytes
match. This argument is deterministic. It does not rely on a truncated digest.

## 3. Finite ideal-map probability

For this section only, model each `f(x)` on a first query as an independent
uniform element of `F_p`. Fresh starts are independent masked random words.
Until a repeat or failure, query `j` has at least `j` distinct earlier states,
so the birthday-event lower bound by `Q` calls is

```
P_birth >= 1 - product(j=1..Q)(1-j/p)
        >= 1 - exp[-Q(Q+1)/(2p)]
        > 0.4124173025483614760.
```

Conservatively subtract all possible missed-event classes. A first repeat
inside the current trail can leave a cycle without a distinguished point;
its probability is at most `Q*L/p < 0.002014160157`, because that trail has
at most `L` previous states. For any of at most `M+1` trails, failure to hit a
distinguished output among `L` fresh outputs has probability at most
`(M+1)*exp[-L*(D-R)/p] < 0.001127737735`: before the call cap at least
`D-R` distinguished values are unvisited. A new start on a prior trail
has probability at most `(M+1)R/2^254 < 6.074e-35`. A first repeated
output hitting an earlier trail start, where that trail has no predecessor,
has probability at most `Q(M+1)/p < 6.062e-35`.

Before a repeat, each distinguished indicator has conditional probability at
most `D/(p-R)`. The number of completed trails before the cap is dominated
by a binomial variable with `Q+L` trials and mean
`mu=(Q+L)*D/(p-R) < 8464.000001`. For `delta=M/mu-1`, the Chernoff bound
`Pr[X>=M] <= exp[-mu*delta^2/(2+delta)] < 3.212e-56` covers table overflow.
Using `mu=8464.000001` as an upper mean preserves that inequality. Thus the
ideal-map lower bound after all deductions is greater than `0.4092754046`,
which exceeds 0.39. If the first repeat is across two trails and away from
their starts, and no cap event occurs, both trails end at the same full
distinguished point, so the scan and recovery find a true collision.
Failure paths are already charged in the fixed budget below. This ideal-map
calculation does not prove the probability for fixed Orchard constants.

## 4. Complete resource and memory account

At `r=56`, the target's field-RAM denominator is `C=216+21*56=1392`.
Each exact target call costs one compression unit. Trails use at most `Q+L`
calls, alignment at most `L`, lockstep at most `2L`, and full verification
two. The absolute cap, including failed paths, is

```
H_max=Q+4L+2=176787323439393811096206339017285828612 calls.
```

In addition, charge 64 primitive 256-bit operations *per call* for state
copies, canonical input/output handling, comparisons, counters, branches,
and loop control. An ordinary trail step needs at most 18 (state load/store,
two predicate operations, counters, and at most eight branch/pointer/control
operations); a lockstep iteration needs two calls and under 32 operations.
The 64 allowance also covers interfaces and final comparison. Counters fit
in one 256-bit word. Charge a further `2^33` operations for all fixed work:
at most `M(M+1)/2 < 50,005,001` record scans at a generous 64 operations
each (<3,200,320,064), at most 10,000 insertions at 64 operations each,
at most 10,001 random words plus masking and at most 16 operations each,
table zeroing, constant loading, and initialization under `2^20` operations.
These terms total less than `2^33`; the cap covers all lookups, memory
operations, randomness, preprocessing, failed trials, and recovery control.
There is no sorting, inversion, exponentiation outside paid target calls, or
unpriced processor. The field hash is called as the reference primitive,
so its arithmetic must not be charged a second time.

```
W_max=64*H_max+2^33
     =11314388700121203910157205697114882965760 primitive operations.
T_max=H_max+W_max/1392
     =184915476241205020801779044259466060627.6321839080... units.
log2(T_max)=127.120133579851... < claimed 127.12014.
```

Finite setup under `2^20/1392` target units has log2 less than 10; the
claim's `preprocessing_log2=10` covers it and it is already in `W_max`.
There is no nonuniform advice or stored collision. The 1-MiB memory floor
gives `M'=1`, hence normalized score 127.12014. This is total work across
all processors, not wall time, and is not asserted to beat prior claims.

Memory is explicitly reserved as follows: 800,000 bytes for 10,000 packed
records; 6,432 bytes for the 192 round constants and nine MDS entries;
65,536 bytes for code; 8,192 bytes for stack and scratch state; 4,096 bytes
for counters and registers; and 256 bytes for input/output and randomness
buffers. The sum is 884,512 bytes. Reserve another 164,064 bytes for padding
and allocator allowance: the reported peak is **1,048,576 bytes**, exactly
`2^20`. There is no other retained data. The 16-byte length holds `L=2^118`;
the 32-byte fields and endpoints are never truncated.

## 5. H1, experiment, extrapolation, and limitations

H1: for masked random `rho` and trail starts, the concrete map
`x -> H_56(x,rho)` has the birthday and distinguished-point behavior of
section 3 closely enough for this finite algorithm to succeed with
probability at least 0.39. The algorithmic coins are the random `rho` and
starts; the fixed Orchard constants are not randomized. This is a
score-critical fixed-function heuristic, not a theorem. A random permutation
on width-three states has `p^2` complete output states for each first
coordinate, making its first-coordinate occupancy close to the random-map
calculation at `O(sqrt p)` queries. That motivates H1 but does not prove it
for the deployed algebraic permutation.

The declared `truncated-brent7` experiment evaluates the *selected 56-round
target* for 256 organizer-seeded `rho` values. It iterates the seven-low-bit
projection as a closed 128-state map, recovers a distinct pair by a bounded
Brent search, and submits both canonical messages for the organizer to check
the seven digest bits. This tests small-projection cycle and output behavior
on the real target, and the pair-recovery logic. Its results are not known
at filing. The seven-bit projection can conceal full-field structure; 256
seeds cannot resolve a few-percent hazard change, and no full-width
`Q`-step run is feasible. These are material extrapolation limits.

The separate `fullwidth-trail8` experiment uses 20 sequential full-field
outputs per organizer-seeded trail and asks the organizer to check equality
of eight low digest bits. This directly probes adaptive full-width inputs,
but its event is still a truncated-output event and its short trails cannot
validate the cryptanalytic-scale 254-bit collision probability.

If the birthday hazard is multiplied by `c` while the failure deductions remain,
the principal probability is `1-exp[-c*Q(Q+1)/(2p)]`; at `c=0.93` the
deducted lower bound falls below 0.39. Increasing the call budget by a
factor `k` adds about `log2(k)` time bits. No rigorous qualification or
human acceptance is claimed here.

The two suggested papers were considered only as research context.
ePrint 2025/1916 concerns Graeffe-style univariate root recovery for
reduced-round constrained-input/output problems. ePrint 2026/1254 develops
degree annihilation for a cubic Poseidon CICO-2 setting. Neither supplies
an Orchard `x^5`, eight-full-round, fixed-capacity collision construction,
probability, or finite operation ledger; no headline factor from either
paper is imported into this claim.
