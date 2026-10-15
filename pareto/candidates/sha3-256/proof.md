# Bitsliced distinguished-point collision search on SHA3-256 reduced to 7 rounds

This package claims a classical ordinary collision attack on `sha3-256-r7-prefix-v1` by van
Oorschot-Wiener parallel collision search (distinguished points, one processor). It uses no
property of Keccak beyond the declared random-function heuristic RF-WALK (Section 9). It is a
birthday-bound construction: the gain over the nominal 2^128 comes only from pricing. The main
phase evaluates the 7-round permutation as a counted program of 256-bit word operations that
computes 256 independent evaluations at once (bitslicing), and is charged by its counted
operations at 1/C each (C = 1897), as the cost model prices every word operation (Section 2).
Any pair the algorithm outputs is a genuine collision regardless of the heuristic; the
heuristic is used only for the success probability.

## 1. Exact target and the iterated map

Target: SHA3-256 (FIPS 202) with Keccak-f[1600] reduced to its first r = 7 rounds (rounds
0..6 with iota constants RC[0..6], prefix convention) in every permutation call. Rate 1088
bits (136 bytes), capacity 512, zero initial state, domain suffix 01 and pad10*1 (byte 0x06 after
the message, 0x80 in byte 135), little-endian lanes, lane index x + 5y, digest = first 32 bytes.

Encoding. For a 256-bit word v let w0..w3 be its four little-endian 64-bit words. enc(v) is
the 135-byte message K with w0, w1, w2, w3 written (little-endian) into lanes 0, 1, 2, 4 and
again into lanes 10, 11, 12, 14 (byte offsets 0, 8, 16, 32 and 80, 88, 96, 112), where K is the
fixed 135-byte constant below (zero on those 64 bytes). In state coordinates: lanes (x,0) =
(x,2) = w_X for (x, X) = (0,0), (1,1), (2,2), (4,3); every other rate lane is the constant lane
of K; byte 135 of the padded block is 0x86 (suffix 0x06 and the final 0x80 of pad10*1 in one
byte). One 7-round permutation; the digest is lanes (0..3, 0), 32 bytes < 136, no further
squeeze. Define F(v) = dec(SHA3-256-r7(enc(v))), a map {0,1}^256 -> {0,1}^256 (the complete
digest re-read as the next word).

K (hex, 135 bytes; bs7.py K_HEX):

```
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000ffffffffffffff860000000000000000ffffffffffffffffffffffffffffffff00000000000000000000
0000000000000000000000000000ffffffffffffffff0000000000000000ffffffffffffffffffffffffffffff
```

Lemma 1. If v != v' and F(v) = F(v'), then enc(v) != enc(v') are two 135-byte messages with
equal complete 7-round SHA3-256 digests: an ordinary collision. (enc is injective.)

Why this encoding (a linear structure in the sense of Guo, Liu and Song, "Linear Structures:
Applications to Cryptanalysis of Round-Reduced Keccak", ASIACRYPT 2016): every column x of the
first permutation input holds the same word twice (rows 0 and 2, x = 0, 1, 2, 4) or only
constants (x = 3), so all column parities of round 0 are constants and theta of round 0 adds
constants only. rho and pi send row 0 to column X = 0 and row 2 to column X = 2 of the chi rows; these
are not neighbours, so no chi row of round 0 multiplies two message bits: chi of round 0 is
affine in v, and so is theta of round 1. The batch program therefore computes round 0 and
theta of round 1 with XORs only (Section 4). The constant K is chosen (linsolve3.py, by
GF(2) elimination over its free bits) so that, in as many chi rows of round 0 as compatible,
the constant neighbours keep each message bit in place (out = (v XOR w, 0, NOT w, 0, 1) for a
row (v, b1, w, b3, b4) with (b1, b3, b4) = (0, 0, 1)); then whole columns of the round-1 state
are constant and theta of round 1 needs fewer XORs. This is a property of the inputs we choose, used
to shorten the counted program; it changes neither the target nor the random-function
heuristic.

## 2. Pricing convention (cost model collision-frontier-v5)

The rule, quoted (paths are in the challenge source repository):

- cost-models/collision-frontier-v5.json line 9 (computation_model): "Classical probabilistic
  256-bit word RAM. One selected-round target compression or sponge permutation costs one unit;
  every other primitive word operation costs 1/C units, where C is the selected target
  reference_operation_cost." Lines 10-18 list the primitives: 256-bit load or store,
  addition/subtraction, bitwise AND/OR/XOR/NOT, shift or rotation, comparison, conditional branch,
  independent uniform random 256-bit word. C = 271 r = 1897 (the per-round reference count).
- docs/RESCORING.md lines 5-6: "One selected compression/permutation costs 1; each other 256-bit
  RAM primitive costs 1/C." Lines 19-26: C counts "additions, logical operations, shifts and masks
  on data words" of the trusted reference core; "Narrow rotations use their explicit 256-bit-RAM
  implementation"; "Public loop/index arithmetic, Python overhead, memory traffic and
  serialization are excluded from this reference normalization"; "All actual attack work,
  including memory accesses, remains charged; a whole compression's internals must not also be
  charged individually." scripts/reference_operation_costs.py lines 50-52 obtain C by running the
  lane-form permutation (keccak._permute_lanes, 25 lanes of 64 bits) on counted words.
- The exploratory example packages shipped in the source repository price bitsliced Keccak rounds
  the same way. lanes/exploratory/candidates/sha3-256-r6/claim.json (restriction 3): "no
  permutation call is made: verification evaluates the six rounds in 1271 word operations per
  message, constant-folded"; its proof.md Section 5.1 (lines 215-221): "Every executed primitive
  other than a permutation call is one word operation ... The machine has 64 registers ... an
  address or constant fixed at generation time is an immediate operand of its instruction and
  costs no operation"; Section 6.3 (lines 357-359, "Bit-sliced evaluation"): "the word
  operations below apply theta, rho, pi, chi and iota to the 256 states at once". The sha3-256-r5
  example, lanes/exploratory/candidates/sha3-256-r5/proof.md line 709: "Our counted programs count
  every executed load, store, operation, comparison and branch as one primitive ... values live in
  at most 64 registers ... A 256-bit word holds one bit of each of 256 pairs (or leaves):
  bitslicing."

How this package applies it. (a) A permutation CALL (an atomic evaluation of the 7-round
permutation) costs 1 unit; LOCATE (Section 3) uses such calls, plus 64 word operations each.
(b) The main phase makes no permutation call. It runs a program of primitive word operations
whose outputs are 256 permutation results (one bit of each of 256 independent evaluations per
256-bit word), and every executed primitive of that program, loads and stores included, is
charged 1/C, as line 9 prices every primitive that is not a permutation call. Nothing is charged
twice: no evaluation is both a call and counted operations. (c) C itself is the price the model
assigns to computing one permutation of 64-bit lanes with 256-bit word operations (data-path
operations only, memory traffic excluded); our program is a different word program and is priced
by its own complete count (memory traffic included), which is what RESCORING.md line 25 requires
("All actual attack work, including memory accesses, remains charged").

Machine (declared; the cost model fixes no register count). One processor with 1024 registers
of 256 bits. Every register is counted as memory (32768 bytes, Section 6). Instructions: XOR, AND,
OR with three register fields, NOT and MOV with two, LD (register <- memory word) and ST
(memory word <- register). Every executed instruction counts as one primitive operation (1/C
units): every load, store and register-to-register move is charged, as in the organizer
examples (sha3-256-r5 proof line 709: "every executed load, store, operation, comparison and
branch as one primitive"). Reading a register operand inside an instruction costs nothing;
addresses are instruction fields of straight-line generated code (as in the r6 example, Section
5.1: "an address or constant fixed at generation time is an immediate operand of its
instruction and costs no operation"); rho and pi are realised as register names and addresses
(renaming), never as data movement. The batch program of Section 4 uses at most 1016 of the
registers; 8 are kept for the control of Section 3. Total work is summed over the single
processor.

## 3. Algorithm

Constants:

- theta = 2^-115: v is distinguished, DP(v), iff its top 115 bits are zero.
- P = 256 walks run in lockstep; walk i keeps its start word s_i, its start batch t0_i and its
  current word (held bitsliced: bit i of 256 message words).
- E = 9728 table entries of 64 bytes: the low 128 bits of the distinguished word, the 256-bit
  start, the 128-bit trail length.
- Lrun = 20/theta = 20 * 2^115, Lcap = 2 Lrun + 2: a walk whose trail reaches Lcap steps without a
  distinguished point is restarted (abandoned).
- Kb = 39168 charged word operations per batch step (Section 4), cL = C + 64 = 1961 operations
  per LOCATE evaluation (one permutation call = C/C = 1 unit, plus 64 word operations).
- Op budget Wmax = 53915610871005774460990425822521150236199 (= 1.03558 * 2^128/256 * Kb), counter W.

Coins: one fresh uniform 256-bit word per start (256 initial starts and one per restart).

```
MAIN:
  for i in 0..255: s_i = fresh word; walk i's word = s_i; t0_i = 0
  t = 0; W = 0; dps = 0
  loop:
    if W + Kb > Wmax: halt with failure
    t = t + 1; W = W + Kb
    BATCH-STEP: every walk's word v_i <- F(v_i) (the counted bitsliced program, Section 4),
                and dmask = the 256-bit word whose bit i is DP(v_i)
    for each set bit i of dmask, in increasing i:
      dps = dps + 1; if dps > E: halt with failure
      v = v_i (extracted); len = t - t0_i
      search the table for an entry whose stored 128 bits equal the low 128 bits of v
      if none: insert (v mod 2^128, s_i, len)
      else with entry (s', len'):
        if W + (len + len') cL <= Wmax:      # else skip this detection (no LOCATE)
          out = LOCATE(s_i, len, s', len'); if out != none: output out and halt
      restart walk i: s_i = fresh word, v_i = s_i, t0_i = t
    for each walk i with t - t0_i >= Lcap: restart walk i (abandon)

LOCATE(s, l, s', l'):            # scalar; each F evaluation is one permutation call, W += cL
  a = s; b = s'
  while l > l': a = F(a); l = l - 1
  while l' > l: b = F(b); l' = l' - 1
  while l > 0:
    if a = b: return none
    fa = F(a); fb = F(b)
    if fa = fb: return (enc(a), enc(b))
    a = fa; b = fb; l = l - 1
  return none
```

LOCATE evaluates F at most l + l' times, so the check before it guarantees W <= Wmax at every
moment of every run. Every output satisfies a != b and F(a) = F(b): a collision by Lemma 1.
The abandonment test is one comparison of t against the smallest deadline t0_i + Lcap
(recomputed at each restart).

## 4. The counted bitsliced batch program

Representation. Word (x, y, z) holds bit z of lane (x, y) of all 256 walks (bit i = walk i).
Message word j (j = 64 X + z: bit z of digest lane X) holds bit j of every walk's current v. The
256 message words stay in 256 fixed registers from one batch to the next: the last round writes
digest word j into the register that held message word j. A register may hold the complement
of its value; this complement flag is a compile-time property of the generated code.

The batch program is straight-line code generated in two passes (bs7.py). Pass 1 writes it with
unbounded virtual registers and no memory traffic:

1. Round 0 and theta of round 1 (affine stage). theta of round 0 adds constants (Section 1);
   rho and pi are renaming; in every chi row of round 0 each product ~b_{x+1} b_{x+2} has a
   constant factor, so chi outputs are message words, constants or XORs of message words.
   theta of round 1 (column parities, D, S1 = o XOR D) is computed with XORs. The generator
   keeps the linear form (over the 256 message bits) of every affine value and emits no XOR
   whose result form is already held or cancels to a constant. No AND, OR or NOT is executed.
2. Rounds 1 .. r-2. For each output slice z, chi row by row: out_x = b_x XOR (NOT b_{x+1} AND
   b_{x+2}), with AND(~b1, b2) or OR(b1, ~b2) = ~(~b1 AND b2) chosen by the stored complement
   flags, a constant or repeated operand folded (~c AND c = 0), and a smallest set of NOTs per
   row. Lane complementing (Bertoni, Daemen, Peeters, Van Assche, Keccak implementation
   overview, "lane complementing transform"): the outputs are steered to the polarity pattern
   f below, in which every chi row needs exactly one NOT; iota is a NOT of word (0, 0, z) where
   RC has a 1 (this keeps the pattern). Then the next round's theta is fused: column parities
   C'[x][z] (20 XOR), D'[x][z] = C'[x-1][z] XOR C'[x+1][z-1] (5 XOR, once slices z and z-1 are
   done), S' = out XOR D' (25 XOR). Round r-2 applies D' only to the 5 diagonal lanes (x, x),
   the only lanes round r-1 reads.
3. Round r-1: only row y = 0, lanes 0..3 (4 AND/OR + 4 XOR per slice): the 256 digest words, in
   the polarity round 0 was compiled for (a NOT where it differs); then the distinguished test:
   an OR of the 115 top digest words that are stored true and an AND of those stored
   complemented, then OR/NOT: dmask bit i = 1 iff walk i's top 115 digest bits are zero.

Pass 2 maps the virtual registers to the 1016 registers (Belady's furthest-next-use rule): when
all registers are taken, the value whose next use is furthest is evicted; a value evicted while
still needed is written once (ST) and read back (LD) before its next use. Digest word j is
written into message word j's register (a MOV moves any other occupant away first). Every
ST, LD and MOV that pass 2 inserts is part of the program and of the count.

Counted operations of the final program (executed; bs7.py runs it on 3 chained batches of
256 random words, the digest registers of one batch being the message registers of the next,
and checks all digests and dmask bits against an independent bytewise SHA3-256-r of enc(v)
whose 24-round form equals Python's hashlib.sha3_256; as random digests are never
distinguished, it also runs the emitted DP-test instructions on 64 synthetic digest batches in
which about a third of the walks are distinguished and a third miss by one top bit):

| part | LD | ST | MOV | XOR | AND | OR | NOT | total |
|---|---|---|---|---|---|---|---|---|
| round 0 + theta of round 1 | 0 | 0 | 0 | 1290 | 0 | 0 | 0 | 1290 |
| round 1 + theta of round 2 | 0 | 599 | 0 | 4682 | 613 | 869 | 610 | 7373 |
| round 2 + theta of round 3 | 599 | 599 | 0 | 4800 | 896 | 704 | 325 | 7923 |
| round 3 + theta of round 4 | 599 | 599 | 0 | 4800 | 896 | 704 | 323 | 7921 |
| round 4 + theta of round 5 | 599 | 599 | 0 | 4800 | 896 | 704 | 325 | 7923 |
| round 5 + theta of round 6 | 599 | 0 | 0 | 3520 | 896 | 704 | 322 | 6041 |
| round 6 | 0 | 0 | 0 | 256 | 128 | 128 | 59 | 571 |
| DP test | 0 | 0 | 0 | 0 | 0 | 114 | 1 | 115 |
| control (budget add/compare/branch, dmask test, deadline) | | | | | | | | 8 |

Batch step: 39157 + 8 = 39165 operations, charged Kb = 39168 (rounded up to a multiple of 64): 153.00
operations per evaluation of F, i.e. 0.08065 units per evaluation (C = 1897). Of these, 4792 are
loads, stores and moves (18.72 per evaluation).

Why the rounds cost what they cost: a middle round is 64 x (25 AND/OR + 25 XOR (chi) + 20 + 5 +
25 XOR (theta)) = 6400, plus one NOT per chi row (320), plus iota NOTs, plus the loads and stores
of the values that do not fit in the registers (the state is 1600 words, the registers 1016).
Round 1 reads affine values that do not follow the pattern and needs more NOTs. Polarity
pattern f(x, y) (x = 0..4 across, y = 0..4 down; 1 = stored complemented) and the D' polarity
per column, found by exhaustive search over the row patterns:

```
  y=0: 0 0 1 1 0
  y=1: 1 0 1 0 0
  y=2: 1 0 1 0 0
  y=3: 1 0 1 0 1
  y=4: 0 0 1 1 1
  D' polarity by x: 1 0 1 1 1
```

Registers: the batch program uses at most 1016 registers (pass 2 never exceeds this bound; bs7.py
executes the program on a register file of exactly 1024 entries); the control of Section 3 keeps
W, t, the smallest deadline, dps and dmask in 8 further registers. Spill memory: 603 words.

## 5. Time (total work, target-compression units)

Every phase of every run, and where it is charged:

| phase | what runs | charge |
|---|---|---|
| preprocessing (once) | polarity-pattern search and generation of the batch program (Section 7) | 2^36 word operations, in X |
| initialisation | 256 fresh start words, injected into the message words; counters | in X |
| main phase, every batch | the counted bitsliced program of Section 4 (256 evaluations of F) and the control | Kb, in W |
| distinguished-point handling | extraction, table scan and insert, restart | in X (<= E calls by the dps cap) |
| abandonment restarts | fresh word, injection, deadline | in X |
| LOCATE, every evaluation of F | one permutation call (1 unit = C operations) + 64 word operations | cL, in W |
| output | LOCATE's own comparison fa = fb; enc is a byte copy | in cL and X |

F is evaluated nowhere else: there is no separate verification pass, and LOCATE's evaluations
are counted one by one (W += cL before each). W <= Wmax always (Section 3). Other work X (not
in W), word operations:

- preprocessing: <= 2^36 (Section 7);
- per distinguished point handled (at most E by the dps cap): extract walk i's word from the 256
  message registers (<= 1536), table scan (<= 8 per entry, <= 8E), insert (<= 16), LOCATE call
  set-up and checks (<= 64), restart: fresh word, store start, inject 256 bits into the
  message words in their stored polarity (<= 2048), deadline recomputation (<= 512);
  together <= 8E + 4096 + 64;
- initial starts 256 x 2560; abandonment restarts (at most 256 Tmax/Lcap + 1, Tmax = Wmax/Kb
  batches) x 2560; initialisation <= 4096.

  X <= (E + 1)(8E + 4160) + 256 * 2560 + (256 Tmax / Lcap + 1) * 2560 + 4096 + 2^36 = 69518303808.

LOCATE's per-evaluation word work: split a into 4 lanes (7), store them into lanes 0, 1, 2, 4,
10, 11, 12, 14 (8), store the 17 other lanes from registers that hold the 9 constant lanes of
K and zero (17), read the digest (10), comparisons a = b, fa = fb with branches and moves (6),
loop counter (3), W update and check (3): 54 <= 64 = cL - C.

  T <= (Wmax + X) / C = 0.083523321 * 2^128,   log2 T <= 124.418323.

Claimed time_log2 = 124.419. This bounds the total work of every run (the budget is enforced).

## 6. Memory

- straight-line batch code: Kb instructions of 8 bytes (an 8-bit opcode and three 16-bit
  register or address fields): 313344 bytes; other code (DP handling, table, LOCATE with a looped
  scalar permutation): <= 32768 bytes;
- spill words of the batch program: 603 x 32 = 19296 bytes;
- walk starts and start batches: 256 x 48 = 12288 bytes; LOCATE state, counters, constants:
  <= 4096 bytes; 1024 registers of 32 bytes: 32768 bytes;
- table: E x 64 = 622592 bytes (E = 9728 entries of 16 + 32 + 16 bytes: low 128 bits of the
  distinguished word, 256-bit start, 128-bit length);
- nothing else is retained: a run keeps no list of evaluated points, and coins are consumed
  as they are drawn (each start word is kept only as s_i and in the table).

| item | bytes |
|---|---|
| batch code | 313344 |
| other code | 32768 |
| spill words | 19296 |
| walk starts and start batches | 12288 |
| LOCATE state, counters, constants | 4096 |
| registers (1024 x 32) | 32768 |
| table | 622592 |
| total | 1037152 |
| 2^20 - total (slack) | 11424 |

Total <= 1037152 bytes (log2 = 19.984196).
Claimed memory_log2_bytes = 20 (no memory penalty).

## 7. Preprocessing and advice

No advice: nonuniform_advice_log2_bytes = 0. The batch program is generated from the Keccak
specification at the start of the run, and that generation is charged as preprocessing (cost
model line 20: total time includes preprocessing): (i) the polarity-pattern search of Section 4
(bs7.py lane_patterns: the 10 chi-row patterns with exactly one equal neighbour pair, 10^5
row combinations x 32 D' polarities, each checked in <= 2^11 word operations: <= 2^32.7);
(ii) program generation (bs7.py program: at most 7 polarity choices x 6 message-polarity
iterations = 42 builds, each <= 2^16 instructions and <= 2^11 chi rows, at <= 2^12 word
operations per instruction or row: <= 2^33.4); (iii) register allocation of each build (one
heap operation and next-use update per operand, <= 2^12 word operations per instruction:
<= 2^33.4). Together <= 2^34.9 <= 2^36 word operations =
2^25.11 units (C = 1897), included in X (Section 5). Claimed preprocessing_log2 = 25.12.

## 8. Success probability

Probability space: the algorithm's fresh start words, with F under RF-WALK (Section 9). Number
the main-phase evaluations k = 256 (t - 1) + i + 1 (batch t, walk i). Fresh process: draw
U_1, U_2, ... iid uniform in {0,1}^256 and use U_k as the image of evaluation k while every
evaluated point is new; c_k = DP(U_k) are then iid Bernoulli(theta) coins. The run equals the
fresh process up to the first repeat K (the first k with U_k in the visited set V_k: starts
and images so far) and while no start word hits a visited point. In lockstep, walk i's images
are U at indices i + 1, i + 257, ...: the trail structure is a function of the coins only.

Lemma 2 (target and factorisation). For an image index i < k and an event G of the coins
other than c_k, P(K = k, U_k = U_i, G) = E[1{K >= k} 1_G] / N, because U_k is uniform and
independent of U_1..U_{k-1}, the starts and the coins after k. (So the target of a repeat is
uniform over the images, and its position in the trail structure is a function of coins.)
Gamma and Lambda below are read on the coins other than c_k (the real image of evaluation k
is U_i, whose coin is c_i).

Lemma 3 (hazard given the coins). Given all coins, the values are independent and uniform
within their class (distinguished or not). On Gamma = {at most E - 2 distinguished images in
the run besides index k}, given the history without a repeat, the probability that
evaluation j repeats is at most
u_j = (j - 1 + 256 + E) / (N (1 - theta)) if c_j = 0 and (2E + 256)/(N theta) if c_j = 1, and
at least (j - 1 - E)/N if c_j = 0. Hence, on Gamma,
Q-(k) = exp(-sum_{j<k} (u_j + u_j^2)) (1 - (2E + 256)/(N theta))^E <= P(K >= k | coins)
<= Q+(k) = exp(-[(k - 1 - E)(k - 2 - E)/2 - E (k - 1)] / N).

Lemma 4 (one good first repeat succeeds). Let K = k (batch t, walk w) with U_k = U_i, i an
image of a walk w' != w; let l = number of images of w's current trail before k, m = position
of U_i in its trail (m >= 1), D = min{d >= 0 : c_{i + 256 d} = 1} (steps from U_i to the
end of its trail). Assume Gamma, not-Lambda (no walk has a run of Lrun non-distinguished
images in a row), no start word hits a visited point or is hit, no repeat by walk w' in its next
D evaluations, no two distinct distinguished points equal on their low 128 bits, and
FIT: (t + D) Kb + (l + 1 + m + 2D) cL <= Wmax. Then the run outputs a
collision. Proof: walk w continues along the trail of w' (F is deterministic); w' is ahead
(or level, with w' < w in the same batch) and reaches its distinguished point d' at batch
<= t + D, inserting it (Gamma; trail length m + D < Lcap by not-Lambda; no abandonment). Walk
w reaches d' at batch t + D (length l + 1 + D < Lcap), finds the entry (s', m + D), and
len + len' = (l + 1 + D) + (m + D), so FIT lets LOCATE run; LOCATE aligns the two trails and
returns (enc(t_l), enc(u_{m-1})) after l + 1 + m evaluations (the generic distinguished-point
argument: the fresh part of w's trail and the trail of w' are disjoint, starts are not on
other trails). If an earlier detection happens instead, it is a merge of two trails, its
LOCATE runs only if it fits, and it returns a collision (no start hits): success as well; a
skipped detection costs no budget. Distinguished walks of one batch are handled in increasing
index, so a level pair (w' < w) is inserted before it is looked up.

Lemma 5 (distributions). D, l, m are functions of disjoint sets of coins (walk w' from i on;
walk w before k; walk w' before i), so they are independent, D is Geom0(theta) exactly,
P(l >= x), P(m - 1 >= x) <= (1 - theta)^x (runs are cut by walk starts). FIT is decreasing in
D, l, m, and Geom0(theta) = floor(X/(-ln(1 - theta))) <= X/theta for X ~ Exp(1), so with
X1, X2, X3 iid Exp(1), D, l, m - 1 are stochastically below X1/theta, X2/theta, X3/theta and
P(FIT) >= F(t) = P(a X1 + b (X2 + X3) <= Wmax - t Kb - 2 cL),
a = (Kb + 2 cL)/theta, b = cL/theta, a hypoexponential distribution in closed form.

Bound. Summing Lemma 2 over k and over the k - t images of other walks before k (per batch
t: 256 (255 t - 127.5)), with Lemma 3 and Lemma 5:

  P(success) >= sum_t 256 (255 t - 127.5)/N Q-(256 t) F(t)
               - A+ (P(not Gamma) + P(Lambda)) - P(start events) - A+ (rho_n/theta + rho_D),

where A+ = sum_k (k - t)/N Q+(k) bounds the total weight, rho_n = (Kmax + starts)/(N(1 - theta))
and rho_D = (2E + 256)/(N theta) bound the repeat probability of one evaluation, and
A+ (rho_n/theta + rho_D) bounds a repeat by walk w' within its next D evaluations (E D =
(1 - theta)/theta). P(not Gamma): Chernoff on Binomial(Kmax, theta), Kmax = 256 Tmax.
P(Lambda) <= (Kmax theta + 256)(1 - theta)^Lrun (expected number of run starts). Sums over t
are taken in 4000 blocks with each factor at its worst end of the block; Decimal arithmetic,
60 digits (bound.py).

| term | value |
|---|---|
| main sum | 0.390565 |
| A+ | 0.413568 |
| A+ P(not Gamma) (mean distinguished count 8483.5, cap E = 9728) | 6.9e-39 |
| A+ P(Lambda) | 7.45e-06 |
| start events and 128-bit DP aliasing ((E + 256)^2 / 2^129) | 1.5e-31 |
| repeat by w' before detection | 5.23e-05 |
| success lower bound | 0.390505 |

Success probability >= 0.390505 >= 0.39. Claimed success_probability = 0.39.

The lockstep detection delay is the term 2D cL + D Kb in FIT: after the first repeat every
further step of the merged trail costs a whole batch (Kb, 256 evaluations). Its mean,
(Kb + 2 cL)/theta operations, is 0.03438 of the budget unit 2^128/256 * Kb (2^128 evaluations);
with LOCATE's own l + 1 + m it is what the budget multiplier 1.03558 pays for over the delay-free
birthday bound.

## 9. Heuristic RF-WALK (declared, score-critical)

Statement: for the fixed map F of Section 1, the walks generated by this algorithm from fresh
uniform start words behave, for the events of Section 8, as walks of a uniformly random
function on {0,1}^256: the value of F at a point not evaluated before is a fresh uniform
256-bit word independent of all values observed so far.

Role: score-critical for the success probability only. Lemma 1 and LOCATE's check make every
output a collision, and the budget makes the time bound unconditional.

Support. (a) Over the algorithm's coins the bound concerns about 2^128 evaluations and a few
thousand trails of mean length 2^115, far below the 2^256 domain, so the success probability
depends on F only through its collision structure at the scale of a birthday search; for a
random function it concentrates around the value computed above. (b) F is 256 bits of the
output of a 7-round, 1600-bit permutation on a 256-dimensional affine input space;
there is no structural reason for F to be closer to injective than a random function. (c) The
best published collision attacks on SHA3-256 reach 5 rounds; no 6- or 7-round structure that
changes the number of colliding pairs is known. (d) The scaled simulation of Section 8 tests the
algorithm (not F) under the random-function model.

Sensitivity: if F produced repeats at kappa times the random-function rate, the bound of
Section 8 recomputed with all repeat probabilities scaled by kappa stays >= 0.39 for
kappa >= 0.9984; a smaller kappa raises the budget by about kappa^(-1/2).

Limitations: F is not a random function; this package gives no proof that F restricted to the
encoding is not closer to injective than a random function. Structure normally yields more
collisions, not fewer, but this is not established here. For r <= 2 the encoding leaves
digest lanes with low degree or constant parts and the heuristic is not credible there.

## 10. Summary of the claim

- target_profile sha3-256-r7-prefix-v1, rounds 7, ordinary collision, exploratory lane;
- time_log2 = 124.419 (total work in target-compression units, C = 1897);
- memory_log2_bytes = 20 (1037152 bytes);
- preprocessing_log2 = 25.12 (included in time), nonuniform_advice_log2_bytes = 0;
- success_probability = 0.39 (bound 0.3905);
- normalized cost = time_log2 + max(0, memory_log2_bytes - 20) = 124.419.

No certificates (a 2^124-unit search is not executed); the manifest is present and empty.

## Appendix. Scripts (verbatim, Python 3 stdlib / C99)

Reproduce: `python3 bs7.py 7 115` prints program_ops = 39157 (Section 4), spill_slots 603, after
executing the allocated program on chained random batches against the bytewise reference
(hashlib-checked at 24 rounds) and the DP-test check. `python3 bound.py 115 39168 1961 9728 20 1.03558 4000`
prints the Section 8 terms and success bound. `cc -O2 -o sim sim.c; ./sim n runs seed
multiplier Kb cL E` is the scaled simulator of Section 8.

### bs7.py (SHA-256 aaa78799be3c822b02d480c77a5c1941815dcb8cb098bef68ead68a3b6b6b8ca)

```python
#!/usr/bin/env python3
"""Counted bitsliced program for F(v) = SHA3-256-r(enc(v)) on 256 walks at once, on an R-register machine.

Usage: python3 -I bs7.py ROUNDS [DBITS] [--regs R]

Machine: R registers of 256 bits; instructions XOR/AND/OR (3 register operands), NOT and MOV (2 register
operands), LD (register <- memory word), ST (memory word <- register). Every executed instruction counts 1.
Bit i of every word belongs to walk i (bitslicing).

Stages:
1. build(): a straight-line SSA program (unbounded virtual registers, no memory traffic). Each virtual
   register carries its linear form over the 256 message variables when it is affine (round 0 and theta of
   round 1), so XORs that cancel or repeat a known form are not emitted. rho/pi are renaming. chi is computed
   row by row with complement flags (a register may hold the complement of the value; the flag is a
   compile-time property), a minimum NOT set per row, and target polarities (lane complementing pattern) in
   the rounds that use it. theta of round i+1 is fused at the end of round i (column parities, D, S' = o ^ D).
   Round r-2 keeps only the 5 diagonal lanes; round r-1 computes only row 0, lanes 0..3 (the digest) and the
   distinguished-point test.
2. allocate(): Belady (furthest next use) register allocation on R_ALLOC = R - RESERVED registers: a value
   evicted while still needed is stored once (ST) and loaded (LD) before each later use that finds it absent.
   The 256 message words live in fixed registers across batches: the digest word j is produced into the
   register that held message word j (a MOV moves an occupant out of the way when needed).
3. verify(): executes the allocated program on random batches, chained (the digest registers of batch t are
   the message registers of batch t+1), against an independent bytewise SHA3-256-r of enc(v) whose 24-round
   form is checked against hashlib.sha3_256; and runs the DP-test instructions on synthetic distinguished
   digests.
"""
import hashlib
import heapq
import json
import random
import sys

MASK256 = (1 << 256) - 1
M64 = (1 << 64) - 1
RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
      0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
      0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
      0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
      0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
      0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]
ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56],
       [27, 20, 39, 8, 14]]   # ROT[x][y]
MSGLEN = 135                  # message bytes; padding byte 135 = 0x86 (domain bits 01, pad10*1)
REGS = 1024
RESERVED = 8                  # control registers (budget W, batch t, deadline, dps, dmask test, spare)


# ---------------- independent reference (lane form, bytewise sponge) ----------------
def rol(v, n):
    n %= 64
    return ((v << n) | (v >> (64 - n))) & M64 if n else v


def keccak_f(A, rounds):
    A = [row[:] for row in A]
    for rnd in range(rounds):
        C = [A[x][0] ^ A[x][1] ^ A[x][2] ^ A[x][3] ^ A[x][4] for x in range(5)]
        D = [C[(x - 1) % 5] ^ rol(C[(x + 1) % 5], 1) for x in range(5)]
        A = [[A[x][y] ^ D[x] for y in range(5)] for x in range(5)]
        B = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                B[y][(2 * x + 3 * y) % 5] = rol(A[x][y], ROT[x][y])
        A = [[B[x][y] ^ (~B[(x + 1) % 5][y] & B[(x + 2) % 5][y] & M64) for y in range(5)] for x in range(5)]
        A[0][0] ^= RC[rnd]
    return A


def sha3_256(msg, rounds):
    rate = 136
    m = bytearray(msg) + b"\x06"
    while len(m) % rate:
        m.append(0)
    m[-1] |= 0x80
    A = [[0] * 5 for _ in range(5)]
    for off in range(0, len(m), rate):
        blk = m[off:off + rate]
        for i in range(rate // 8):
            x, y = i % 5, i // 5
            A[x][y] ^= int.from_bytes(blk[8 * i:8 * i + 8], "little")
        A = keccak_f(A, rounds)
    return b"".join(A[i % 5][i // 5].to_bytes(8, "little") for i in range(4))


def self_check():
    rng = random.Random(1)
    for n in (0, 5, 72, 135, 136, 200):
        m = bytes(rng.randrange(256) for _ in range(n))
        assert sha3_256(m, 24) == hashlib.sha3_256(m).digest(), n


# ---------------- encoding ----------------
def bitpos(x, y, z):
    """message bit index of state bit (x, y, z): lane x + 5y, little-endian."""
    return 64 * (x + 5 * y) + z


PAD_FIXED = {bitpos(1, 3, z) for z in range(56, 64)}   # byte 135 (0x86) lies in lane (1,3), bits 56..63


class Enc:
    """enc(v): bit j of v is written to message bits (x, 0, z) and (x, 2, z), (x, z) = slots[j]; every other
    message bit (of 135 bytes) is the constant const.get(pos, 0). Injective (each v bit is copied)."""

    def __init__(self, slots, const=None):
        assert len(slots) == 256 and len(set(slots)) == 256
        self.slots = list(slots)
        self.const = dict(const or {})
        self.varpos = {}
        for j, (x, z) in enumerate(self.slots):
            self.varpos[bitpos(x, 0, z)] = j
            self.varpos[bitpos(x, 2, z)] = j
        for p in self.const:
            assert p not in self.varpos and p not in PAD_FIXED and p < 8 * MSGLEN

    def msg(self, v):
        b = bytearray(MSGLEN)
        for p, c in self.const.items():
            if c:
                b[p >> 3] |= 1 << (p & 7)
        for p, j in self.varpos.items():
            if (v >> j) & 1:
                b[p >> 3] |= 1 << (p & 7)
        return bytes(b)

    def const_lanes(self):
        """lanes of the first permutation input with every message variable set to 0 (padding included)."""
        m = bytearray(self.msg(0)) + b"\x06"
        m[-1] |= 0x80
        assert len(m) == 136
        A = [[0] * 5 for _ in range(5)]
        for i in range(17):
            A[i % 5][i // 5] = int.from_bytes(m[8 * i:8 * i + 8], "little")
        return A

    def F_ref(self, v, r):
        return int.from_bytes(sha3_256(self.msg(v), r), "little")


VAR_COLS = (0, 1, 2, 4)        # word X of v goes to lanes (VAR_COLS[X], 0) and (VAR_COLS[X], 2)
# K: the 135-byte constant message (zero at the 64 variable bytes); chosen by linsolve3.py so that chi of round 0
# keeps the variables in chi-row positions X = 0 and X = 2 as far as the constraints are compatible.
K_HEX = ("000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
         "ffffffffffffff860000000000000000ffffffffffffffffffffffffffffffff0000000000000000000000000000000000"
         "00000000000000ffffffffffffffff0000000000000000ffffffffffffffffffffffffffffff")


def default_slots():
    """bit j = 64 X + z of v (digest lane X, bit z) -> slot (VAR_COLS[X], z)."""
    return [(VAR_COLS[j // 64], j % 64) for j in range(256)]


def default_enc():
    K = bytes.fromhex(K_HEX)
    assert len(K) == MSGLEN
    slots = default_slots()
    varp = set()
    for (x, z) in slots:
        varp.add(bitpos(x, 0, z))
        varp.add(bitpos(x, 2, z))
    const = {}
    for p in range(8 * MSGLEN):
        if (K[p >> 3] >> (p & 7)) & 1:
            assert p not in varp
            const[p] = 1
    return Enc(slots, const)


# ---------------- SSA builder ----------------
class SSA:
    def __init__(self):
        self.ins = []      # (op, dst, a, b)
        self.tags = []
        self.n = 0
        self.form = {}     # reg -> linear form (int bitmask over the 256 variables) or None
        self.cst = {}      # reg -> constant bit of its affine content
        self.fcache = {}   # form -> reg
        self.dpin = []

    def new(self, form=None, cst=0):
        self.n += 1
        r = self.n
        self.form[r] = form
        self.cst[r] = cst
        if form is not None and form not in self.fcache:
            self.fcache[form] = r
        return r

    def emit(self, op, a, b, tag, form=None, cst=0):
        d = self.new(form, cst)
        self.ins.append((op, d, a, b))
        self.tags.append(tag)
        return d


# operand: ("C", bit) | ("R", reg, flag): value = content(reg) ^ flag
def xor_op(P, u, v, tag):
    if u[0] == "C" and v[0] == "C":
        return ("C", u[1] ^ v[1])
    if u[0] == "C":
        return ("R", v[1], v[2] ^ u[1])
    if v[0] == "C":
        return ("R", u[1], u[2] ^ v[1])
    if u[1] == v[1]:
        return ("C", u[2] ^ v[2])
    fu, fv = P.form[u[1]], P.form[v[1]]
    if fu is not None and fv is not None:
        f = fu ^ fv
        c = P.cst[u[1]] ^ P.cst[v[1]]
        if f == 0:
            return ("C", c ^ u[2] ^ v[2])
        if f in P.fcache:
            r = P.fcache[f]
            return ("R", r, P.cst[r] ^ c ^ u[2] ^ v[2])
        d = P.emit("XOR", u[1], v[1], tag, form=f, cst=c)
        return ("R", d, u[2] ^ v[2])
    d = P.emit("XOR", u[1], v[1], tag)
    return ("R", d, u[2] ^ v[2])


def not_reg(P, r, tag):
    return P.emit("NOT", r, None, tag, form=P.form[r], cst=P.cst[r] ^ 1)


def chi_row(P, b, need, tag, target=None):
    """b: 5 operands of one row; out_x = b_x ^ (~b_{x+1} & b_{x+2}) for x in need. Returns {x: operand}.
    g = ~b_j & b_k: constant/renaming when b_j or b_k is constant or both are the same register; else
    AND(stored-complemented b_j, stored-true b_k) (flag 0) or OR(stored-true b_j, stored-complemented b_k)
    (= ~g, flag 1). A NOT on b_i makes both stored polarities available. The smallest NOT set that meets the
    target output flags is used (else the smallest NOT set, ignoring targets)."""
    var = [i for i in range(5) if b[i][0] == "R"]
    pairinfo = {}
    for x in need:
        j, k = (x + 1) % 5, (x + 2) % 5
        bj, bk = b[j], b[k]
        if bj[0] == "C":
            pairinfo[x] = ("const", ("C", 0) if bj[1] == 1 else bk)
        elif bk[0] == "C":
            pairinfo[x] = ("const", ("C", 0) if bk[1] == 0 else ("R", bj[1], bj[2] ^ 1))
        elif bj[1] == bk[1]:
            pairinfo[x] = ("const", ("C", 0) if bj[2] == bk[2] else bk)
        else:
            pairinfo[x] = ("var", None)
    subsets = sorted(({var[t] for t in range(len(var)) if mask >> t & 1} for mask in range(1 << len(var))),
                     key=lambda s: (len(s), sorted(s)))

    def plan(S, tgt):
        choices = {}
        for x in need:
            j, k = (x + 1) % 5, (x + 2) % 5
            kind, g = pairinfo[x]
            if kind == "const":
                gopts = [("const", g)]
            else:
                aj = {b[j][2]} | ({b[j][2] ^ 1} if j in S else set())
                ak = {b[k][2]} | ({b[k][2] ^ 1} if k in S else set())
                gopts = []
                if 1 in aj and 0 in ak:
                    gopts.append(("AND", ("R", None, 0)))
                if 0 in aj and 1 in ak:
                    gopts.append(("OR", ("R", None, 1)))
            if not gopts:
                return None
            b0opts = [("plain", b[x])] + ([("neg", ("R", None, b[x][2] ^ 1))] if x in S else [])
            want = None if tgt is None else tgt.get(x)
            pick = None
            for bv, b0 in b0opts:
                for gf, g2 in gopts:
                    if b0[0] == "C" and g2[0] == "C":
                        res = None
                    else:
                        res = (b0[2] if b0[0] == "R" else b0[1]) ^ (g2[2] if g2[0] == "R" else g2[1])
                    if want is None or res is None or res == want:
                        pick = (bv, gf)
                        break
                if pick:
                    break
            if pick is None:
                return None
            choices[x] = pick
        return choices

    chosen = None
    for tgt in ([target, None] if target is not None else [None]):
        for S in subsets:
            ch = plan(S, tgt)
            if ch is not None:
                chosen = (S, ch)
                break
        if chosen:
            break
    S, choices = chosen
    negs = {}
    for i in sorted(S):
        d = not_reg(P, b[i][1], tag)
        negs[i] = ("R", d, b[i][2] ^ 1)

    def pol(i, want_comp):
        for c in [b[i]] + ([negs[i]] if i in negs else []):
            if c[2] == want_comp:
                return c
        return None
    out = {}
    for x in need:
        bv, gf = choices[x]
        j, k = (x + 1) % 5, (x + 2) % 5
        if gf == "const":
            g = pairinfo[x][1]
        elif gf == "AND":
            u, v = pol(j, 1), pol(k, 0)
            g = ("R", P.emit("AND", u[1], v[1], tag), 0)
        else:
            u, v = pol(j, 0), pol(k, 1)
            g = ("R", P.emit("OR", u[1], v[1], tag), 1)
        b0 = negs[x] if bv == "neg" else b[x]
        out[x] = xor_op(P, b0, g, tag)
    return out


def src_of(X, Y):
    """B[X][Y] = rot(S[x'][y'], ROT[x'][y']) with X = y', Y = 2x' + 3y'."""
    yp = X
    xp = ((Y - 3 * X) * 3) % 5
    return xp, yp


def build(r, enc, flags, pattern=None, dbits=115, order=None, target_rounds=None, upto=None):
    """flags[j]: stored polarity of message word j (register content = v_j ^ flags[j]).
    pattern: (f, dfl) lane complementing fixed point; target_rounds: rounds whose chi steers to it."""
    P = SSA()
    inreg = [P.new(form=1 << j, cst=flags[j]) for j in range(256)]
    A = enc.const_lanes()
    C0 = [A[x][0] ^ A[x][1] ^ A[x][2] ^ A[x][3] ^ A[x][4] for x in range(5)]   # variables cancel (2 copies)
    D0 = [C0[(x - 1) % 5] ^ rol(C0[(x + 1) % 5], 1) for x in range(5)]
    desc = {}
    for x in range(5):
        for y in range(5):
            for z in range(64):
                c = ((A[x][y] ^ D0[x]) >> z) & 1
                j = enc.varpos.get(bitpos(x, y, z)) if y in (0, 2) else None
                if j is not None:
                    desc[(x, y, z)] = ("R", inreg[j], flags[j] ^ c)
                else:
                    desc[(x, y, z)] = ("C", c)
    if target_rounds is None:
        target_rounds = set(range(1, r - 1))
    outs = {}
    outflag = {}
    for rnd in range(r):
        tag = "r%d" % rnd
        mode = "final" if rnd == r - 1 else ("diag" if rnd == r - 2 else "full")
        zs = order[rnd] if order else list(range(64))
        o = {}
        Cp = {}
        done = set()
        applied = set()
        newdesc = {}
        keep = [(X, X) for X in range(5)] if mode == "diag" else [(X, Y) for X in range(5) for Y in range(5)]
        use_t = pattern is not None and mode != "final" and rnd in target_rounds
        for z in zs:
            rows = [0] if mode == "final" else range(5)
            for Y in rows:
                bb = []
                for X in range(5):
                    xp, yp = src_of(X, Y)
                    bb.append(desc[(xp, yp, (z - ROT[xp][yp]) % 64)])
                need = [0, 1, 2, 3] if mode == "final" else [0, 1, 2, 3, 4]
                tgt = None
                if use_t:
                    f, dfl = pattern
                    tgt = {X: f[(X, Y)] ^ dfl[X] for X in need}
                res = chi_row(P, bb, need, tag, tgt)
                for X in need:
                    o[(X, Y, z)] = res[X]
            if (RC[rnd] >> z) & 1:
                v = o[(0, 0, z)]
                if v[0] == "C":
                    o[(0, 0, z)] = ("C", v[1] ^ 1)
                elif use_t:
                    o[(0, 0, z)] = ("R", not_reg(P, v[1], tag), v[2])   # iota as a NOT keeps the pattern
                else:
                    o[(0, 0, z)] = ("R", v[1], v[2] ^ 1)
            if mode == "final":
                for X in range(4):
                    j = 64 * X + z
                    v = o[(X, 0, z)]
                    assert v[0] == "R"
                    outflag[j] = v[2]
                    if v[2] != flags[j]:
                        v = ("R", not_reg(P, v[1], tag), v[2] ^ 1)
                    outs[j] = v[1]
                continue
            cur = []
            for X in range(5):
                acc = o[(X, 0, z)]
                for Y in range(1, 5):
                    acc = xor_op(P, acc, o[(X, Y, z)], tag)
                cur.append(acc)
            Cp[z] = cur
            done.add(z)
            for zz in (z, (z + 1) % 64):
                if zz in done and (zz - 1) % 64 in done and zz not in applied:
                    applied.add(zz)
                    for X in range(5):
                        D = xor_op(P, Cp[zz][(X - 1) % 5], Cp[(zz - 1) % 64][(X + 1) % 5], tag)
                        for Y in range(5):
                            if (X, Y) in keep:
                                newdesc[(X, Y, zz)] = xor_op(P, o[(X, Y, zz)], D, tag)
        if mode != "final":
            assert len(applied) == 64
            desc = newdesc
        if upto is not None and rnd == upto:
            return P
    # distinguished test: DP iff the top dbits digest bits are 0
    ors, ands = [], []
    for j in range(256 - dbits, 256):
        P.dpin.append((outs[j], j, flags[j]))
        (ands if flags[j] else ors).append(outs[j])

    def chain(op, lst):
        acc = lst[0]
        for u in lst[1:]:
            acc = P.emit(op, acc, u, "dp")
        return acc
    nd = None
    if ors:
        nd = chain("OR", ors)
    if ands:
        a = chain("AND", ands)
        na = P.emit("NOT", a, None, "dp")
        nd = na if nd is None else P.emit("OR", nd, na, "dp")
    P.dmask = P.emit("NOT", nd, None, "dp")
    P.inreg, P.outs, P.outflag = inreg, outs, outflag
    return P


# ---------------- register allocation ----------------
INF = 1 << 60


def allocate(P, R=REGS, reserved=RESERVED, inphys=None):
    """Belady allocation of the SSA program on R - reserved registers. Returns (program, info).
    program: list of (op, d, a, b, tag); LD: (LD, reg, addr), ST: (ST, addr, reg)."""
    cap = R - reserved
    n = len(P.ins)
    if inphys is None:
        inphys = list(range(256))
    uses = {}
    for i, (op, d, a, b) in enumerate(P.ins):
        for u in (a, b):
            if u is not None:
                uses.setdefault(u, []).append(i)
    endv = [P.outs[j] for j in range(256)] + [P.dmask]
    for u in endv:
        uses.setdefault(u, []).append(n)
    ptr = {u: 0 for u in uses}

    def nxt(u):
        lst = uses.get(u)
        if not lst:
            return INF
        p = ptr[u]
        return lst[p] if p < len(lst) else INF
    outtarget = {P.outs[j]: inphys[j] for j in range(256)}
    targetset = set(inphys)
    pending_t = set(inphys)          # target registers whose output is not produced yet
    res = {}                         # value -> phys
    occ = {}                         # phys -> value
    free = set(range(cap))
    heap = []
    inmem = {}                       # value -> addr
    freeslots = []
    nslots = 0
    prog = []
    stats = {"LD": 0, "ST": 0, "MOV": 0}
    maxslots = 0

    def push(u):
        heapq.heappush(heap, (-nxt(u), u))

    for j in range(256):
        u = P.inreg[j]
        res[u] = inphys[j]
        occ[inphys[j]] = u
        free.discard(inphys[j])
        push(u)

    def take_free(prefer=None):
        if prefer is not None and prefer in free:
            free.discard(prefer)
            return prefer
        plain = free - pending_t
        pool = plain if plain else free
        p = min(pool)
        free.discard(p)
        return p

    def evict(protect, tag):
        nonlocal nslots, maxslots
        while True:
            negnu, u = heapq.heappop(heap)
            if u not in res or u in protect or -negnu != nxt(u):
                if u in res and u in protect:
                    keep_back.append((negnu, u))
                continue
            break
        for it in keep_back:
            heapq.heappush(heap, it)
        keep_back.clear()
        p = res.pop(u)
        del occ[p]
        if nxt(u) < INF and u not in inmem:
            if freeslots:
                a = freeslots.pop()
            else:
                a = nslots
                nslots += 1
            inmem[u] = a
            prog.append(("ST", a, p, None, tag))
            stats["ST"] += 1
            maxslots = max(maxslots, nslots - len(freeslots))
        free.add(p)
        return p

    keep_back = []

    def get_reg(protect, tag, prefer=None):
        if free:
            return take_free(prefer)
        p = evict(protect, tag)
        free.discard(p)
        return p

    def ensure(u, protect, tag):
        if u in res:
            return res[u]
        assert u in inmem, ("value lost", u)
        p = get_reg(protect, tag)
        prog.append(("LD", p, inmem[u], None, tag))
        stats["LD"] += 1
        res[u] = p
        occ[p] = u
        return p

    for i, (op, d, a, b) in enumerate(P.ins):
        tag = P.tags[i]
        ops_ = [u for u in (a, b) if u is not None]
        protect = set(ops_)
        phys = [ensure(u, protect, tag) for u in ops_]
        for u in ops_:
            ptr[u] += 1
        for u in set(ops_):
            if nxt(u) == INF:
                p = res.pop(u)
                del occ[p]
                free.add(p)
                if u in inmem:
                    freeslots.append(inmem.pop(u))
            else:
                push(u)
        prefer = outtarget.get(d)
        if prefer is not None:
            if prefer in occ:          # move the occupant out of the way
                w = occ[prefer]
                if free - {prefer}:
                    q = take_free()
                    prog.append(("MOV", q, prefer, None, tag))
                    stats["MOV"] += 1
                    del occ[prefer]
                    res[w] = q
                    occ[q] = w
                    free.add(prefer)
                else:
                    raise RuntimeError("no free register for output move")
            elif prefer not in free:
                raise RuntimeError("target register reserved")
            pd = take_free(prefer)
            assert pd == prefer
            pending_t.discard(prefer)
        else:
            pd = get_reg(protect, tag)
        res[d] = pd
        occ[pd] = d
        if op == "NOT":
            prog.append(("NOT", pd, phys[0], None, tag))
        else:
            prog.append((op, pd, phys[0], phys[1], tag))
        if nxt(d) == INF:
            res.pop(d)
            del occ[pd]
            free.add(pd)
        else:
            push(d)
    for j in range(256):
        u = P.outs[j]
        assert res.get(u) == inphys[j], ("output not in place", j)
    assert P.dmask in res
    info = dict(stats, spill_slots=nslots, max_spilled=maxslots, dmask_reg=res[P.dmask], cap=cap)
    return prog, info


def run_phys(prog, regs, mem):
    for op, d, a, b, _ in prog:
        if op == "LD":
            regs[d] = mem[a]
        elif op == "ST":
            mem[d] = regs[a]
        elif op == "XOR":
            regs[d] = regs[a] ^ regs[b]
        elif op == "AND":
            regs[d] = regs[a] & regs[b]
        elif op == "OR":
            regs[d] = regs[a] | regs[b]
        elif op == "NOT":
            regs[d] = regs[a] ^ MASK256
        elif op == "MOV":
            regs[d] = regs[a]
        else:
            raise ValueError(op)


def transpose_in(xs):
    w = [0] * 256
    for i, x in enumerate(xs):
        for j in range(256):
            if (x >> j) & 1:
                w[j] |= 1 << i
    return w


def transpose_out(w):
    xs = [0] * 256
    for j in range(256):
        for i in range(256):
            if (w[j] >> i) & 1:
                xs[i] |= 1 << j
    return xs


def verify(r, enc, P, prog, info, dbits, trials=2, seed=7, R=REGS, inphys=None):
    """chained batches: registers carry the digests into the next batch."""
    if inphys is None:
        inphys = list(range(256))
    rng = random.Random(seed)
    flags = [P.cst[P.inreg[j]] for j in range(256)]
    xs = [rng.getrandbits(256) for _ in range(256)]
    regs = [0] * R
    w = transpose_in(xs)
    for j in range(256):
        regs[inphys[j]] = w[j] ^ (MASK256 if flags[j] else 0)
    for t in range(trials):
        mem = {}
        run_phys(prog, regs, mem)
        w = [regs[inphys[j]] ^ (MASK256 if flags[j] else 0) for j in range(256)]
        outs = transpose_out(w)
        exp = [enc.F_ref(x, r) for x in xs]
        assert outs == exp, ("digest mismatch", t)
        dm = regs[info["dmask_reg"]]
        for i in range(256):
            assert ((dm >> i) & 1) == (1 if outs[i] >> (256 - dbits) == 0 else 0)
        xs = outs
    dp_logic_check(P, dbits, rng)
    return True


def dp_logic_check(P, dbits, rng, trials=64):
    dp_ins = [ins for ins, tg in zip(P.ins, P.tags) if tg == "dp"]
    assert len(P.dpin) == dbits
    for t in range(trials):
        outs = []
        for i in range(256):
            o = rng.getrandbits(256)
            kind = rng.randrange(3)
            if kind == 0:
                o &= (1 << (256 - dbits)) - 1
            elif kind == 1:
                o &= (1 << (256 - dbits)) - 1
                o |= 1 << (256 - dbits + rng.randrange(dbits))
            outs.append(o)
        Rg = {}
        for reg, bit, pol in P.dpin:
            w = 0
            for i in range(256):
                w |= ((outs[i] >> bit) & 1) << i
            Rg[reg] = w ^ (MASK256 if pol else 0)
        for op, d, a, b in dp_ins:
            if op == "OR":
                Rg[d] = Rg[a] | Rg[b]
            elif op == "AND":
                Rg[d] = Rg[a] & Rg[b]
            elif op == "NOT":
                Rg[d] = Rg[a] ^ MASK256
            else:
                raise ValueError(op)
        dm = Rg[P.dmask]
        for i in range(256):
            assert ((dm >> i) & 1) == (1 if outs[i] >> (256 - dbits) == 0 else 0), (t, i)
    return True


# ---------------- lane complementing patterns (as in lane r6bs) ----------------
def _row_achievable(fin):
    import itertools
    res = set()
    bad = [j for j in range(5) if fin[j] == fin[(j + 1) % 5]]
    if len(bad) != 1:
        return res
    j0 = bad[0]
    for jstar in (j0, (j0 + 1) % 5):
        avail = [{fin[i]} | ({1 - fin[i]} if i == jstar else set()) for i in range(5)]
        opts = []
        for X in range(5):
            j, k = (X + 1) % 5, (X + 2) % 5
            forms = set()
            if 1 in avail[j] and 0 in avail[k]:
                forms.add(0)
            if 0 in avail[j] and 1 in avail[k]:
                forms.add(1)
            opts.append({p ^ fm for p in avail[X] for fm in forms})
        for combo in itertools.product(*opts):
            res.add(combo)
    return res


def lane_patterns():
    """Lane-uniform polarity patterns f of the stored theta output such that every chi row needs exactly
    one NOT and chi + theta reproduce f."""
    import itertools
    ach = {fin: _row_achievable(fin) for fin in itertools.product((0, 1), repeat=5)}
    good = [p for p in ach if ach[p]]
    rowsrc = [[src_of(X, Y) for X in range(5)] for Y in range(5)]
    sols = []
    for pats in itertools.product(good, repeat=5):
        f = {}
        for Y in range(5):
            for X in range(5):
                f[rowsrc[Y][X]] = pats[Y][X]
        pf = [sum(f[(x, y)] for y in range(5)) & 1 for x in range(5)]
        for dfl in itertools.product((0, 1), repeat=5):
            if not all(dfl[x] == (pf[(x - 1) % 5] ^ dfl[(x - 1) % 5] ^ pf[(x + 1) % 5] ^ dfl[(x + 1) % 5])
                       for x in range(5)):
                continue
            if all(tuple(f[(X, Y)] ^ dfl[X] for X in range(5)) in ach[pats[Y]] for Y in range(5)):
                sols.append((f, dfl))
    return sols


def orders(r, kind):
    if kind == "fwd":
        return [list(range(64)) for _ in range(r)]
    if kind == "alt":
        return [list(range(64)) if k % 2 == 0 else list(range(63, -1, -1)) for k in range(r)]
    raise ValueError(kind)


def program(r, dbits, enc=None, R=REGS, order_kind="alt", patterns=None, verbose=False):
    """Compile: polarity pattern choice and message polarity fixed point (the last round stores the digest
    in the polarity round 0 was compiled for). Keeps the shortest allocated program."""
    if enc is None:
        enc = default_enc()
    if patterns is None:
        patterns = [None] + lane_patterns()
    best = None
    order = orders(r, order_kind)
    for pattern in patterns:
        flags = [0] * 256
        seen = []
        for it in range(6):
            P = build(r, enc, flags, pattern, dbits, order)
            prog, info = allocate(P, R)
            if verbose:
                print("pattern", patterns.index(pattern), "it", it, "ssa", len(P.ins), "alloc", len(prog), info,
                      file=sys.stderr)
            if best is None or len(prog) < len(best[1]):
                best = (P, prog, info, list(flags), pattern)
            out = [P.outflag[j] for j in range(256)]
            if out == flags or out in seen:
                break
            seen.append(out)
            flags = out
    return best + (enc,)


def counts(r, dbits, enc=None, R=REGS, order_kind="alt", trials=2, verbose=False, patterns=None):
    P, prog, info, flags, pattern, enc = program(r, dbits, enc, R, order_kind, patterns, verbose)
    verify(r, enc, P, prog, info, dbits, trials)
    by = {}
    kinds = {}
    for op, d, a, b, tag in prog:
        by["%s:%s" % (tag, op)] = by.get("%s:%s" % (tag, op), 0) + 1
        kinds[op] = kinds.get(op, 0) + 1
    by_tag = {}
    for k, v in by.items():
        t = k.split(":")[0]
        by_tag[t] = by_tag.get(t, 0) + v
    return dict(rounds=r, dbits=dbits, regs=R, program_ops=len(prog), ssa_ops=len(P.ins), kinds=kinds,
                by_tag=by_tag, by_tag_op=dict(sorted(by.items())), spill_slots=info["spill_slots"],
                max_spilled=info["max_spilled"], dmask_reg=info["dmask_reg"], msgflag_ones=sum(flags),
                order=order_kind,
                pattern=None if pattern is None else
                {"f": {"%d,%d" % k: v for k, v in sorted(pattern[0].items())}, "dflag": list(pattern[1])})


if __name__ == "__main__":
    self_check()
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("rounds", type=int)
    ap.add_argument("dbits", type=int, nargs="?", default=115)
    ap.add_argument("--regs", type=int, default=REGS)
    ap.add_argument("--order", default="alt")
    ap.add_argument("-v", action="store_true")
    A = ap.parse_args()
    r, dbits, R, ok = A.rounds, A.dbits, A.regs, A.order
    res = counts(r, dbits, R=R, order_kind=ok, verbose=A.v)
    print(json.dumps(res, indent=1, sort_keys=True))
```

### bound.py (SHA-256 e31daf54ea78e734f4f846f85d746eba33276b642532b0f83cbece72117bb311)

```python
#!/usr/bin/env python3
"""Success-probability lower bound for the lockstep bitsliced distinguished-point search.

All arithmetic in Decimal (60 digits); every block sum is bounded in the safe direction by
monotonicity of its factors. Notation (proof Section 6):
  N = 2^256, theta = 2^-d, P = 256 walks, Kb = word ops per batch, cL = C + w ops per LOCATE
  evaluation, Wmax = op budget for batches + LOCATE evaluations, E = table cap,
  Lrun: run bound (event Lambda), Lcap = 2 Lrun + 2 trail cap, Delta = 2 Lcap max LOCATE length.
  First repeat at evaluation k (batch t = ceil(k/256)) into an image i of another walk:
  success if (t + D) Kb + (Z + 2D) cL <= Wmax (a detection runs LOCATE only if len + len' fits the
  remaining budget; len + len' = Z + 2D for this merge), D ~ Geom0(theta) (lockstep delay),
  Z = l + 1 + m <= 2 + (X2 + X3)/theta, D <= X1/theta, X1, X2, X3 iid Exp(1).
"""
from decimal import Decimal as Dm, getcontext
import sys

getcontext().prec = 60
ONE = Dm(1)


def hypo_sf(u, a, b):
    """P(a X1 + b (X2 + X3) > u), X iid Exp(1), a != b > 0, u real."""
    if u <= 0:
        return ONE
    l1, l2 = ONE / a, ONE / b
    A = l1 * l2 * l2 / ((l2 - l1) ** 2)
    B = -A
    C = l1 * l2 * l2 / (l1 - l2)
    return (A / l1) * (-l1 * u).exp() + (B / l2) * (-l2 * u).exp() + C * (u / l2 + ONE / (l2 * l2)) * (-l2 * u).exp()


def chernoff_ln(mu, t):
    """ln of P(Bin >= t) bound exp(-mu) (e mu / t)^t, t > mu."""
    return -mu + t * (ONE + (mu / t).ln())


def bound(d, Kb, cL, Wmax, E, Lrun, J=4000, verbose=False, kappa=1):
    """kappa: sensitivity run, repeat probabilities multiplied by kappa (N replaced by N / kappa
    in the repeat hazards and pair weights; the distinguished-point class sizes keep N)."""
    N0 = Dm(2) ** 256
    N = N0 / Dm(kappa)
    th = Dm(2) ** (-d)
    Kb, cL, Wmax = Dm(Kb), Dm(cL), Dm(Wmax)
    Tmax = int(Wmax / Kb)               # batches possible
    kmax = 256 * Tmax
    Lcap = 2 * Lrun + 2
    Delta = 2 * Lcap
    a = (Kb + 2 * cL) / th          # LOCATE length is checked as len + len' = Z + 2D
    b = cL / th
    ln1m = (ONE - th).ln()              # ln(1 - theta)
    starts = 256 + E + (256 * Tmax) // Lcap + 1
    # hazards
    rho_n = (Dm(kmax) + starts) / (N * (ONE - th))
    rho_D = Dm(2 * E + 256) / (N0 * th) * Dm(kappa)
    dpfac_ln = Dm(E) * (ONE - rho_D).ln()

    def lnQminus(k):    # ln of lower bound on P(K >= k | coins) on Gamma
        k = Dm(k)
        s = ((k - 1) * k / 2 + (255 + E) * (k - 1)) / (N * (ONE - th))
        v = (k + 255 + E) / (N * (ONE - th))
        return -s - (k - 1) * v * v + dpfac_ln

    def lnQplus(k):     # ln of upper bound on P(K >= k | coins) on Gamma
        k = Dm(k)
        if k <= E + 2:
            return Dm(0)
        s = ((k - 1 - E) * (k - 2 - E) / 2 - E * (k - 1)) / N
        return -max(s, Dm(0))

    def F(t):           # lower bound on P(fit) for a first repeat in batch t
        u = Wmax - Dm(t) * Kb - 2 * cL
        return ONE - hypo_sf(u, a, b)

    def Dwin(t_lo, t_hi):
        """upper bound on E[(D+1) 1{lo < D <= hi}] over batches t in [t_lo, t_hi]."""
        hi = (Wmax - 2 * cL) / Kb - Dm(t_lo)
        lo = (Wmax - Dm(Delta) * cL) / Kb - Dm(t_hi)
        if hi < 0:
            return Dm(0)
        hiF = int(hi)
        p_hi = ((hiF + 1) * ln1m).exp()
        p_lo = ONE if lo < 0 else ((int(lo) + 1) * ln1m).exp()
        return (Dm(hiF) + 1) * max(p_lo - p_hi, Dm(0))

    # blocks of batches
    edges = [1 + (Tmax * j) // J for j in range(J + 1)]
    edges[-1] = Tmax + 1
    S = Dm(0)
    Aplus = Dm(0)
    for j in range(J):
        ta, tb = edges[j], edges[j + 1]          # t in [ta, tb)
        if tb <= ta:
            continue
        n = Dm(tb - ta)
        # per batch t: sum_w (k - t_k) = 256 (255 t - 127.5)
        wlo = 256 * (255 * Dm(ta) - Dm("127.5"))
        whi = 256 * (255 * Dm(tb - 1) - Dm("127.5"))
        if wlo < 0:
            wlo = Dm(0)
        qm = lnQminus(256 * (tb - 1)).exp()      # k <= 256 (tb - 1)
        qp = lnQplus(256 * (ta - 1) + 1).exp()   # k >= 256 (ta - 1) + 1
        S += n * wlo / N * qm * F(tb - 1)
        Aplus += n * whi / N * qp
    # bad events
    mu_dp = Dm(kmax) * th
    pGam = chernoff_ln(mu_dp, Dm(E - 1)).exp() if E - 1 > mu_dp else ONE   # >= E-1 heads off index k
    pLam = (Dm(kmax) * th + 256) * (Dm(Lrun) * ln1m).exp()
    b3 = 2 * Dm(starts) * (Dm(kmax) + starts) / N + Dm((E + 256) ** 2) / Dm(2) ** 129
    b4 = Aplus * (rho_n / th + rho_D)
    fail_terms = dict(Gamma=Aplus * pGam, Lambda=Aplus * pLam, starts=b3, wprime=b4)
    succ = S - sum(fail_terms.values())
    out = dict(S_main=S, Aplus=Aplus, terms=fail_terms, success=succ, Tmax=Tmax, mu_dp=mu_dp,
               pGamma=pGam, pLambda=pLam, rho_n=rho_n)
    return out


if __name__ == "__main__":
    d, Kb, cL, E, Lrun_f, bmul = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), Dm(sys.argv[5]), Dm(sys.argv[6])
    J = int(sys.argv[7]) if len(sys.argv) > 7 else 2000
    th = Dm(2) ** (-d)
    Lrun = int(Lrun_f / th)
    Wmax = int(bmul * Dm(2) ** 128 / 256 * Kb)
    r = bound(d, Kb, cL, Wmax, E, Lrun, J)
    for k, v in r.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                print(" ", kk, "%.6e" % vv)
        else:
            print(k, "%.8g" % v if not isinstance(v, int) else v)
```

### sim.c (SHA-256 a6d40389dd66c26bb1f5bc46b393591ea4f91117653e28da9254fc7e0bfa676b)

```c
/* Scaled simulator of the r6bs algorithm (lane r6bs proof Section 2) on a keyed random function.
   n-bit domain, sqrt = 2^(n/2); theta = 2^-(n/2 - 13) (same offset as d = 115 at n = 256);
   P = 256 walks in lockstep (one batch = 256 evaluations, cost Kb ops); LOCATE evaluation cost cL;
   budget Wmax = bmul * 2^(n/2) / 256 * Kb ops; E table cap; Lrun = 20/theta, Lcap = 2 Lrun + 2.
   A detection runs LOCATE only if len + len' evaluations fit the remaining budget; else it is
   skipped (walk restarts). Distinguished walks are handled in increasing walk index.
   usage: sim n runs seed bmul Kb cL E      prints successes / runs */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
static uint64_t key, key2, MASK; static int DPSHIFT;
static uint64_t rs;
static inline uint64_t rnd64(void){ uint64_t z = (rs += 0x9E3779B97F4A7C15ULL); z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; return z ^ (z >> 31); }
static inline uint64_t F(uint64_t x){ uint64_t z = x * 0xD6E8FEB86659FD93ULL ^ key; z = (z ^ (z >> 32)) * 0xD6E8FEB86659FD93ULL; z ^= key2; z = (z ^ (z >> 29)) * 0x9E3779B97F4A7C15ULL; z ^= z >> 32; return z & MASK; }
#define TS (1<<16)
static uint64_t tdp[TS], tst[TS], tlen[TS]; static unsigned char tuse[TS];
static int tfind(uint64_t d){ unsigned h = (unsigned)((d * 0x9E3779B97F4A7C15ULL) >> 48) & (TS-1); while (tuse[h] && tdp[h] != d) h = (h+1)&(TS-1); return h; }
/* returns 1 if a collision is found; counts evaluations */
static int LOCATE(uint64_t a, uint64_t l, uint64_t b, uint64_t l2, uint64_t *ev){
  while (l > l2){ a = F(a); l--; (*ev)++; }
  while (l2 > l){ b = F(b); l2--; (*ev)++; }
  while (l > 0){ if (a == b) return 0; uint64_t fa = F(a), fb = F(b); *ev += 2; if (fa == fb) return 1; a = fa; b = fb; l--; }
  return 0;
}
int main(int argc, char **argv){
  int n = atoi(argv[1]), runs = atoi(argv[2]); rs = strtoull(argv[3],0,10) * 0x2545F4914F6CDD1DULL + 7;
  double bmul = atof(argv[4]); double Kb = atof(argv[5]), cL = atof(argv[6]); int E = atoi(argv[7]);
  const int P = 256;
  MASK = (1ULL << n) - 1;
  int h = n/2; int dbits = h - 13; uint64_t invth = 1ULL << dbits; DPSHIFT = n - dbits;
  uint64_t Lrun = 20 * invth, Lcap = 2*Lrun + 2;
  double Wmax = bmul * (double)(1ULL << h) / 256.0 * Kb;
  uint64_t x[256], s[256], t0[256];
  int succ = 0, skipped = 0, nonelocate = 0, capfail = 0; double dpsum = 0;
  for (int run = 0; run < runs; run++){
    key = rnd64() & MASK; key2 = rnd64(); memset(tuse, 0, sizeof tuse);
    for (int i = 0; i < P; i++){ s[i] = x[i] = rnd64() & MASK; t0[i] = 0; }
    double W = 0; uint64_t t = 0; int dps = 0, done = 0;
    while (!done){
      if (W + Kb > Wmax){ done = 3; break; }
      t++; W += Kb;
      for (int i = 0; i < P; i++) x[i] = F(x[i]);
      for (int i = 0; i < P && !done; i++){
        if ((x[i] >> DPSHIFT) == 0){
          if (++dps > E){ done = 2; capfail++; break; }
          uint64_t len = t - t0[i];
          int k = tfind(x[i]);
          if (!tuse[k]){ tuse[k] = 1; tdp[k] = x[i]; tst[k] = s[i]; tlen[k] = len; }
          else {
            if (W + (double)(len + tlen[k]) * cL <= Wmax){
              uint64_t ev = 0;
              int ok = LOCATE(s[i], len, tst[k], tlen[k], &ev);
              W += ev * cL;
              if (ok){ done = 1; break; }
              nonelocate++;
            } else skipped++;
          }
          s[i] = x[i] = rnd64() & MASK; t0[i] = t;
        } else if (t - t0[i] >= Lcap){ s[i] = x[i] = rnd64() & MASK; t0[i] = t; }
      }
    }
    if (done == 1) succ++;
    dpsum += dps;
  }
  printf("{\"n\":%d,\"runs\":%d,\"bmul\":%.4f,\"success\":%d,\"rate\":%.4f,\"skipped\":%d,\"locate_none\":%d,\"capfail\":%d,\"mean_dps\":%.1f}\n",
         n, runs, bmul, succ, (double)succ/runs, skipped, nonelocate, capfail, dpsum/runs);
  return 0;
}
```

