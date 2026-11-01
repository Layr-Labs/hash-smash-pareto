# SHA-256 r40: five-key packing and one-MiB phase reuse

This is a derivative of de42b4cc-7d45-4f4d-85bd-65fd00fad5aa, source commit
e830ebfc6bcc2f0eef51b46bac6ab517692104f9. It retains the 43,541-gate,
884-data-register kernel, message family, walk, random-function argument, and
native machine prices. It changes table representation, storage lifetimes,
integer plan parameters, and the recovery controller. Section 8 lists the
material inherited submissions. No independence from that work is claimed.

The live program computes

```
N = 57746540188414149168689811531111805080261 word operations
log2(N/2896) = 123.907012420264
time_log2 = 123.90702, rounded upward
peak = 1048576 bytes
```

The new result is 0.000058314151 time bits below
the predecessor's exact ledger. This is a bounded generic collision construction
under H1, not a demonstrated full-width collision or a claim of a SHA-256 weakness.

## 1. Target and relation

Target `sha256-r40-prefix-v1` (the Pareto lane `sha256`, round 40). The two colliding messages have 64 bytes each. With x a 256-bit integer and y0..y7 its eight 32-bit words (big-endian, y0 the highest), M(x) is the 16 big-endian words W0..W15 with
- W0..W7 = the constant words 3e73281c, 752d8ed2, ad19eff1, 7250fceb, d4095422, 44fdb519, 43f22c5b, d8d6aac4 (the base-source appendix gives how they are computed),
- W8 = y0, W9 = y1, and W(8+k) = y_k - K(8+k) modulo 2^32 for k = 2..7.
FIPS 180-4 padding appends 0x80, 55 zero bytes and the 64-bit length 512: the padded message is 128 bytes, two blocks, and block 2 is the same for every x. The target runs the steps 0 to 39 on each block, block 1 from the standard IV and block 2 from the chaining value cv1 = IV + s(x) word by word, where s(x) is the working state after step 39 of block 1; the digest is the result of block 2 with its feed-forward (`verifier/hash_functions.py:digest(M(x), "sha256", 40)`). The profile's message domain is "finite byte strings of bit length below 2^64"; a 64-byte string is in it.
Write a_i, e_i for the a and e words after i steps of block 1 (a_0, e_0 from the IV), T1_i for the T1 of the step that produces them and W_j for the schedule word of step j. With the fixed 32-bit polarity masks `QM = 0x74a40866` and `XM = 0x46eb57e6`, f(x) is walk B (4684dfc2) with per-bit polarity-matched disjoint-support shears on Q and X: the eight words e_(40-3), e_(40-2), X = e_(40-5) + Ch(e_(40-2), XM, e_(40-4)) + W_38 (at bit j: `e_(40-2)[j] | e_(40-4)[j]` when `(XM >> j) & 1 == 1` and `~e_(40-2)[j] & e_(40-4)[j]` when `(XM >> j) & 1 == 0`; since `Ch(e2, e3, e4) = Ch(e2, XM, e4) + (e2 & e3 & ~XM) - (e2 & ~e3 & XM) mod 2^32`, the inverse adds `(e2 & e3 & ~XM) - (e2 & ~e3 & XM)`), T1_(40-4), Q = T1_(40-5) + Ch(a_(40-6) ^ a_(40-7), a_(40-8), QM) (at bit j: `~(a_(40-6)[j] ^ a_(40-7)[j]) | a_(40-8)[j]` when `(QM >> j) & 1 == 1` and `(a_(40-6)[j] ^ a_(40-7)[j]) & a_(40-8)[j]` when `(QM >> j) & 1 == 0`; since `Maj(a6, a7, a8) = Ch(a6 ^ a7, a8, QM) + (a6 & a7 & ~QM) - (~a6 & ~a7 & QM) mod 2^32`, the inverse adds `(a6 & a7 & ~QM) - (~a6 & ~a7 & QM)`), a_(40-6), a_(40-7), Y = e_(40-4) + W_39, in this order (permutation (6, 1, 7, 0, 5, 4, 2, 3) of bw, the order with no register move, the base-source appendix), as a 256-bit integer. These words determine s(x): the program's `enc_invert` recovers a_(40-5) = Q + (a_(40-6) & a_(40-7) & ~QM) - (~a_(40-6) & ~a_(40-7) & QM) + Sigma0(a_(40-6)), then a_(40-4), a_(40-3), a_(40-2), the T1 of steps 38 (= X + (e_(40-2) & e_(40-3) & ~XM) - (e_(40-2) & ~e_(40-3) & XM) + Sigma1(e_(40-2)) + K_38) and 39 and the whole state, by additions, subtractions and the round functions. The walk is g(x) = f(x) XOR q, q a fixed 256-bit mask (127 output planes that the generator leaves complemented instead of spending a NOT).
So g(x) = g(y) gives s(x) = s(y), hence the same cv1, the same block 2 and equal digests. x != y gives M(x) != M(y), since x -> W8..W15 is a bijection. The attack outputs two distinct 64-byte messages with equal complete 256-bit digests.
The selftest (`python3 bssha.py --selftest`) compares the program with scalar g on 2,560 lanes, including all-zero and all-one inputs, checks four chained steps, checks the inverse on 10,000 random states, checks the recovery program and experiment digest network, and runs six width-16 search attempts. It also runs the independent ordinary builder and requires byte equality with the normative bounded emitter.



## 2. One attempt and its exact representation

The full-width plan has `Tp=2135`, `tmax=138177`, `KAPPA_256=48`,
`KR=1273/100`, and `B=1324410828041367000000000000000000000`. B is an explicit attempt parameter.
The program recomputes every resource bound and independently certifies that B
suffices. It does not load a stored ledger or a research result file.

There are 256 lanes. A point is distinguished when its low 20 bits are zero and
its next 102-bit window F is less than 2135. Its key is the same pair `(H,F)` as
the predecessor: 36 bits H above bit 121 and the 12-bit window value F. Trail t
starts at `r+t mod 2^256`, from one fresh uniform r. No attempt restarts.

1. Advance all 256 lanes with the unchanged bit-sliced program. Process stage-1
   flags in increasing lane order. The stage-1 hit budget is checked before extraction.
2. On a DP, increment the finished count, then scan trail slots in increasing
   order. The first equal key transfers to recovery. The capacity halt comes
   after this scan, so the ledger includes `tmax+1` completed events.
3. If no key matches, store the key in the current trail's slot, allocate the
   next trail number, and restart that lane from `r+t`. Zero slots remain empty.
4. Every `2^48` batches, cut lanes with age at least `c=ceil(48 L)`. The eighth
   cut halts. A stage-1 budget failure, table full, exhausted batch budget,
   failed recovery, and successful recovery all end the attempt.

The original 48-bit key has unused encodings because `F<Tp`. Use the exact digit

```
digit = 1 + H*Tp + F
R = 1 + Tp*2^36
block = digit[0] + R*digit[1] + ... + R^4*digit[4]
```

Legal key digits are 1 through R-1. Zero is the sole empty sentinel. Division
of `digit-1` by Tp recovers H and F exactly. All five-digit combinations fit in
236 bits. This is a bijection on the entire allowed domain, with no entropy or
randomness assumption. Equal digits are exactly equal old keys.

The 138,440 slots include 256 initial trails, 138,177 completed trails, and
seven cuts. There are 27,688 consecutive 236-bit groups: 816,796 payload bytes,
four final-word padding bytes, and a 32-byte guard word, totaling 816,832 bytes.
Each native access reads two aligned words and masks the selected group. Stores
preserve neighboring bits. The scanner may stop at the next unused trail index,
since every later slot is zero and a query digit is positive. Its charged bound
still scans the entire allocated capacity.

## 3. Native instructions, controls, and ledger

The machine is the predecessor's classical 256-bit load/store RAM with 884 data
registers and three pointer registers. The body has 43,541 native 32-bit records:
34,096 XOR, 5,866 AND, and 3,579 OR. Every body record costs one word operation.
Stage 1 costs 22 operations, and the main loop costs three, totaling 43,566.
The full-width search executes the 32-bit body records from the live arena
against that arena's register file. The projected experiment has a separate
checked fast mirror; it does not supply the full-width computation path.
The body stream SHA-256 remains
`cff4d5fb7f9293ddec010dc88c4923fe4b136040aa6a342692035210318be3ce`.

The new routines use native 40-bit records: a four-bit opcode and three ten-bit
fields, with six zero reserved bits. The opcode order in the shipped assembler
is `set, add, sub, and, or, xor, shl, shr, lt, jz, jmp, load, store, ret,
jif, jabs`.
Jumps name an instruction index relative to the routine entry. `ret` branches
through pointer register P2 to the retained caller. Every argument move, the
set of P2, and the entry branch is charged. Four routine calls require at most
14 caller operations; the ledger reserves 16. No return stack is allocated.

Generic SET uses the two source fields as one 20-bit literal. The table emitter
deliberately retains its ten-bit-chunk construction. JABS uses a 20-bit absolute
byte address, sufficient for this one-MiB image. Four call sites are encoded in
the retained controller allowance and executed by the interpreter: argument OR
moves, SET P2 to the continuation, and JABS to the routine. Their continuations
enter the inherited controller flow. The helper and caller register clobbers are
explicit: data registers 0..102 and P2 during table handling; input planes and
the main counter pointer survive.

Recovery uses the same generic opcode numbering. Bit 34 selects the counted
64-word recovery array for indexed loads/stores; bit 35 marks an immediate
arithmetic operand. JIF branches on a Boolean comparison result in register 127.
A tagged SET32 form has bit 39 set, a seven-bit destination, and a 32-bit literal.
It sets the word with that literal in bits 0..31 and 128..159. Every recovery
constant has exactly this form, checked by the encoder. This structured native
immediate uses the inherited one-word SET price; it needs no separate literal
pool or software decoding. All other unused flag bits are zero.

Every opcode other than `jz` costs one listed primitive operation. `jz` is
conservatively charged two: a zero comparison and a conditional branch.
Explicit comparisons followed by branches therefore receive no hidden discount.
The native instruction fetch/execute convention is inherited; no software
decoder runs in the priced path. `Arena.native_call` is the counted test interpreter.

Multiplication uses shift-and-add, bounded by 2,576 operations. Restoring division
uses 256 iterations, bounded by 4,112 operations. Its divisors are below `2^49`,
so no doubled remainder overflows a word. Constants are built from ten-bit
immediates. Group addresses are expanded into shifts and additions. There is no
multiply/divide primitive or excluded unpacking work.

The scan has 165 records, insertion 273, and key conversion 30, totaling 468
records and 2,340 bytes. Their scratch is registers 0 through 99. A def-use
check proves that the body reads only input planes or registers it has already
written, so handler scratch does not require a hidden zeroing pass.

With G groups, group size g=5, and the operation bounds above, the added charges are:

```
scan   = G*(g*(4112+8)+80)+40
insert = 4112+g*(4112+2576+16)+240
key    = 2576+40
event  = scan+insert+2*key+16
setup  = 5*table_words+10+2*added_code_bytes+100
```

The old event bound is retained as well. Stage-1 extraction costs at most 2,800
operations per hit, completed-trail handling 3,800 plus six per allocated slot,
slice checks 1,300, and cuts 4,200. These inherited handler/code envelopes are
kept explicitly. The arena model reserves their full code capacity and marks
that reserve with canaries; it does not present those canaries as executable
native instructions. Their source control flow is executable. The new table
routines and rolled recovery records are actual encoded instructions read from
the arena. The inherited 1,279-record control allowance remains a declared
machine/accounting assumption, not a newly measured instruction listing.

The counter region has an 8,192-byte plane copy and 256 aligned 32-byte birth
words. Before recovery, the 2,048-byte recovery-array region holds 32 words of
trail IDs, eight 18-bit IDs per word, and 32 scalar words. The seed, next trail
index, and all early-halt counters are authoritative values in that arena.
The live main batch counter uses a pointer register. Restart metadata work fits
inside the retained 3,800-operation event allowance. A bit-insertion loop needs
at most 2,560 operations, 256 reloads, and fewer than 984 other operations.
Slice checking can unroll eight birth tests: 32 blocks of at most 27 operations,
plus setup, remain below 1,300. Cut processing is charged separately.

### 3.1 Persistent recovery

Recovery's 404 records execute 1,393 operations per paired step. Seven constants
are relocated into spare registers 32 through 38, keeping the record and operation
counts unchanged. Four initially zero state registers, 3, 4, 7, and 8, are
explicitly cleared between steps. The predecessor's cold-call mirror obscured
this requirement. Native tests now preserve registers and arrays between calls.

A packed two-lane DP screen costs 19 operations. It forms zero-prefix flags and
less-than-Tp flags with guarded subtraction at bits 64 and 192, so lane borrows
cannot interact. A persistent active-lane mask suppresses completed trails.
Two ANDs canonicalize the first two output limbs before the next head's rotations.
The other six inputs are canonicalized inside the head. The DP comparison masks
the low word and compares it to `Tp<<20`, while the zero-prefix test handles its
low 20 bits. Four zero clears, eight polarity XORs, two limb masks, 19 screen
operations, three checkpoint countdown operations, and three loop operations
total 39, exactly the charged allowance.
The at-most-two endpoint updates and initial constants fit the fixed 600-operation
allowance. The 76-record recovery initialization executes once.
The actual encoded recovery records execute against the arena's register file
and array region, including persistent state across successive calls.

Pass 1 advances both trails until their first DPs, for at most `cr=ceil(KR L)`
steps. It stores both states at every multiple of D. States after a lane's first
DP are never read. Checkpoint record zero holds the starts. For k noninitial
records, `floor(cr/D)<=k`; the smallest feasible stride is
`D=floor(cr/(k+1))+1`. Thus

```
cr = 31702243346776541568272531854555104
kchk = 15520
D = 2042538711859837740369340368183
```

Pass 2 aligns the longer trail using its checkpoints, binary-searches the last
unequal aligned checkpoint pair, and advances the final interval to the first
merge. Fourteen binary-search probes, an initial comparison, and a final lookup
give at most 16 probes. Each replays fewer than D steps; the last interval costs
at most D. The bound is `cr+17*D` paired calls, `80*kchk` checkpoint work,
`16*100` probe work, and `600+76` fixed operations. The returned predecessors are
distinct and their next walk values agree. False keys and cap failures terminate.

### 3.2 Complete integer ledger

| Item | Word operations |
| --- | ---: |
| cuts | 29400 |
| events | 115301250320 |
| main | 57699282134450194722000000000000000000000 |
| offset_search | 461900436782186496 |
| radix_events | 79125006318000 |
| radix_setup | 132420 |
| recovery | 45447336034985523415717816837647199756 |
| selector_search | 114560315521236992 |
| setup | 180309477 |
| slices | 6116828204674281366238200 |
| stage1_hits | 1810717928962806445312500000000179200 |
| Total | 57746540188414149168689811531111805080261 |

All rows are recomputed by `--ledger` from the emitted programs and live plan.
`EXPECTED_N` is an assertion oracle only. No row or total is loaded from saved
research output. Exact integer-power comparison gives
`2^12390701 * 2896^100000 <= N^100000 < 2^12390702 * 2896^100000`.

### 3.3 Setup and preprocessing

The embedded normative C emitter is unchanged: 27,033 source bytes, SHA-256
`0838d00e6b24114617a61f90592b5f0b7232bc986d8106e345f5270e620672fa`.
The charged fuel upper bound remains 89,747,938 operators, at two word operations
per operator plus one. The predecessor reported Homebrew clang 20.1.6,
LLD 22.1.8, Wasmtime 50.0.0 and module SHA-256
`25d311c7e5b359fd90cc5629e3755c69250ac995b4e6a7a10ae2b4f8047276f4`.
That exact module is not reproduced here. A fresh build of the same C source
with Ubuntu clang 18.1.3, `-Os -ffreestanding -fno-builtin -nostdlib`,
`--target=wasm32`, LLD 22.1.2 and
`--no-entry --allow-undefined --strip-all` produces a 22,515-byte module,
SHA-256 `cf47b49441572ac2a150ea2ff942212d4446d65e93163cffcb6e806c9cf62d8b`.
Wasmtime 50.0.1 measures 88,683,456 fuel units, below the unchanged charged bound.
Its 9,708 static instructions replace the old 9,465 for setup memory, without
changing search storage. Its emitted body and all 15 metadata fields agree.
The C source remains unchanged. This remains participant setup accounting,
distinct from the organizer's Python correctness experiments.

The unchanged emitter can produce a temporary body image in the unused table
region. An eight-word unrolled copy relocates it to its final address. The live
`setup_bound` includes that copy, all starts, plane/birth clears, trail IDs,
scalar initialization, reloads, and phase work. It is below the retained 813,600
fixed-setup allowance. The separate 132,420-operation radix setup charge remains
in full. Temporary body storage rounds to 174,176 bytes; setup peaks at 832,964
bytes including both temporary and final images, below one MiB.

The 1,641-build offset search and 407-build selector envelope remain charged at
`2^48` operations per build. Total preprocessing is 576460752483865385 operations, with
upward-rounded `preprocessing_log2=47.50016`. No retained collision or advice is used.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values and N = 2^256. Write A_F for the procedure with every evaluation of g replaced by an evaluation of F (lazy sampling), and P_F for its success probability over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Lemma 2 below is a theorem about F with no premise: its inputs are Lemma 1 (a statement about g itself) and the lazy-sampling facts of Step 1 (statements about F, exact for the adaptive choices of the program: which trails finish, are cut or abort depend on earlier outputs). H1 enters only in the passage from A_F to the real attempt; its clause (d) (Section 5) says that g has the collision hazard that F has by construction. The numbers below are printed by `python3 bssha.py --details` (the function `_lossq`); the probability-certificate unit below recomputes them with its own copy.

Lemma 1 (a statement about g itself, no premise). A pair x != y of evaluated inputs on two different finished trails with g(x) = g(y) is output: both trails continue identically from g(x), so they end at the same DP with the same key and
when both trails have length <= cr, pass 1 of step 6 records every D-th point of each walk and the terminal lengths l0, l1 <= cr, and pass 2 aligns the longer walk via its checkpoints and binary-searches the floor(min(l0, l1) / D) + 1 checkpoint intervals (at most 16 probes of < D steps) before stepping the two walks together for at most D steps to the first merge pair, found within cr + 17 D batches. The returned pair satisfies g(x) = g(y) with x != y, so f(x) = f(y); the recovery checks equality before it returns.
The key determines F because F < 2135 < 2^12 and the low 12 key bits hold F. Equal keys of two DPs can differ only above bit 157. The lanes do not interact.
The stage-1 test loses no event. A 48-bit key match without a merge ends the run; its probability and one recovery are charged.

Lemma 2 (for the random function F; no premise). Let LANES = 256, B batches, Q = 256 B evaluations, N = 2^256, theta = Tp / 2^122 = 1 / L, c = ceil(48 L), cr = ceil((1273/100) L), S = 2^48, M = c + S, N' = (1 - theta) N, q = Q / L = 136144.8120, tmax = 138,177, and CMAX = 7. Let Pi_m = product from i = 0 to m - 1 of (1 - i/N'), PP = Q(Q - 1)/(2N'), and H = (Q(Q - 1)/2 + 2^18 Q)/N'. Let k = 138902 be the least integer with e^-q (e q / k)^k <= 2^-40, n2 = k + 263, p = e^(-c/L), and p2 = e^(-(c-1)/L) (1 + (c - 1) theta / (1 - theta)). Let F be uniformly random on 256-bit values and P_F the success probability when every evaluation of g is replaced by lazy sampling from F. Then
    P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_rec - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny,
where the component bounds for the present plan have the following approximate values.
These rounded planner values are descriptive; the outward-rounded certificate
below decides feasibility.

| Component | Bound |
| --- | ---: |
| P_rec | 4.03597315413529e-05 |
| cut_halt | 1.45312003679317e-05 |
| delay | 0.00113973115062673 |
| finished_count | 9.09494701772928e-13 |
| key_false_match | 6.50669810137507e-05 |
| misc | 8.07794750226857e-28 |
| no_collision | 0.608728737947552 |
| partner_cut_trail | 6.80406496137313e-20 |
| partner_own_trail | 7.29197867227398e-06 |
| rest_of_path | 3.6196108409468e-06 |
| table_capacity | 6.60398393086236e-07 |
| too_old | 3.46639012807223e-20 |

Step 7 derives every component and proves that the two remaining stage-1 tails fit together inside the charged `2^-90` reserve. the probability-certificate unit below evaluates each component with outward rounding.
The numbers are printed by `python3 bssha.py --details` (the function `_lossq`) and the probability-certificate unit below recomputes the whole bound in exact rationals and 60-digit decimals (`probability_certificate`, outward rounding) and asserts the result >= 0.39: P_F >= 0.390000001000 (the program's float value, planned at the target 0.390000001, is 0.390000001). B is a fixed multiple of 10^21; the certificate proves sufficiency without claiming global minimality. H1 (Section 5) is the only premise of this entry: it states that the real attempt succeeds at least as often as A_F.

Proof.
Step 0 (notation). A trail is the run of evaluations of one lane between two restarts; a(t) is the number of earlier evaluations of the trail of t (its age); the length of a trail is its number of evaluations. A trail is finished when an evaluation returns a distinguished point (DP; that evaluation is its last), cut when a slice check restarts it at age >= c, open when the halt comes first. Every length is at most M, and a trail of length at most c is never cut. An evaluation is fresh when its input has not been evaluated before. A collision is a fresh evaluation whose value equals an earlier value (an earlier output or a start). The starts r + t' (t' < 2^18) differ from every value the run produces except with probability Q 2^18 / N (r is uniform and independent of F); this event is excluded below and charged in P_tiny, so a non-fresh evaluation exists only after a collision on its trail.

Step 1 (lazy sampling with a lottery). Realise F by independent uniform values V_1, V_2, ...: the t-th evaluation returns V_t if it is fresh and the value stored for its input otherwise. This is the lazy sampling of F for every adaptive choice of the points. Put xi_t = 1 when V_t is a DP. The xi_t are independent Bernoulli(theta), one per evaluation index, fresh or not; given all of them the V_t are independent and uniform on their class (the theta N DP values, or the N' other values). Index t belongs to lane (t - 1) mod 256, and the lane positions of a lane are its indices in increasing order; the lottery is extended beyond Q by further independent draws (used in the proof only). G_t is the history of the first t evaluations together with the whole lottery; F_t is the history of the first t evaluations together with xi_1, ..., xi_t only.
(L1) If t is fresh and xi_t = 0, then P(V_t = v | G_(t-1)) = 1 / N' for every non-DP value v (and 0 for DP values), and the events for different v are disjoint.
(L2) Whether t is fresh, its input, its batch, its age and the trails before t are determined by G_(t-1).
(L3) The lottery of a lane is i.i.d. Bernoulli(theta); the lanes are independent. Scanning the lanes one after the other, a scan that takes from each lane a number of positions that is a stopping time of that lane (with further independent coins after the run) reads one i.i.d. Bernoulli(theta) sequence.
(L4) N1 = xi_1 + ... + xi_Q is exactly Binomial(Q, theta), so P(N1 >= k) <= e^-q (e q / k)^k <= 2^-40 (Chernoff: the binomial moment generating function is below the Poisson one); P(N1 >= k) is charged once, as 2^-40.
(L5) The run up to evaluation t is F_t-measurable (it depends on V_1, ..., V_t only, and V_s depends on xi_s and an independent uniform). If s is a stopping time of (F_t), the lottery after s is independent of F_s and i.i.d. (strong Markov property of an i.i.d. sequence).

Step 2 (the free run and the first collision). Given the whole lottery xi, the free run is the run in which every evaluation is fresh: the trail boundaries (a DP at every xi = 1, a restart of a trail of age >= c at a slice check), the ages a(t), the lengths and the batches are functions of xi alone, and so are the sets of long trails (a trail is long when its first c coins are all 0, i.e. when it has c evaluations without a DP; the other trails are short, of length at most c, and are never cut) and the numbers rho(y) = the number of evaluations of the lane of y after y up to and including the first with xi = 1. Let n0(t) be the number of s <= t with xi_s = 0. Let tau be the first t with xi_t = 0 whose value V_t equals V_y for some y < t with xi_y = 0 (the first collision of the non-DP class), E1 the event that a start equals a value of the run (Q 2^18 / N), E2 the event that some DP-valued evaluation equals an earlier DP value (on N1 <= k - 1 its probability is at most k^2 L / N': a DP-valued evaluation is uniform on the theta N DP values, at most k - 1 earlier DP values exist, and there are at most k - 1 such evaluations). Outside E1 and E2 the real run is the free run up to tau (every evaluation is fresh), and until then the non-DP values are independent uniform on the N' non-DP values (L1). Hence, for t with xi_t = 0 and y < t with xi_y = 0,
    P(tau = t, V_t = V_y | xi) = Pi_(n0(t) - 1) / N',    sum over y of that = Pi_(n0(t)-1) - Pi_(n0(t)),    P(tau <= Q | xi) = 1 - Pi_(n0(Q)).
On N1 <= k - 1, n0(t) - 1 >= t - k, and Pi_(t-k) <= Pi_(t-1) / (1 - kQ/N') for t <= Q (Pi_(t-1) = Pi_(t-k) times at most k - 1 factors that are each at least 1 - Q/N'; Pi_m = 1 for m <= 1). Pi_m is bounded by exp(-m (m - 1) / (2 N')) from above and by exp(-m (m - 1) / (2 N') - (m - 1) m (2m - 1) / (6 N'^2)) from below (ln (1 - x) >= -x - x^2 for 0 <= x <= 1/2).

Step 3 (a first collision with a good partner is output). Say that the pair (t, y) with tau = t and V_t = V_y is good when (G1) y is not on the trail of t, (G2) b(y) < b(t), (G3) the trail of y is short, (G4) rho(y) <= B - b(t) and a(t) + rho(y) <= c - 1, (G5) a(t) + rho(y) <= cr - 1 and a(y) + rho(y) <= cr - 1, and that it is undisturbed when no fresh evaluation of the trail of y after t, up to its first DP, is a collision. Claim. On a good undisturbed pair, if the run does not halt early (eighth cut, table full, stage-1 budget, key false match, recovery cap) and is outside E1 and E2, the program outputs a pair. Proof. Let X and Y be the trails of t and y. The input of X after t is V_t = V_y, the input of Y after y, so the evaluations that X performs after t are the evaluations Y performs after y, the j-th of them in batch b(t) + j for X and in batch b(y) + j for Y (Y does not restart before its DP, because its trail is short, hence never cut, and its first DP is the (rho(y))-th evaluation after y). By (G2) Y evaluates each of them strictly before X, so X only repeats points. Undisturbed, Y reaches its DP first and stores the key; X later repeats it before any cut. By (G5) both trails have length <= cr, so pass 1 reaches both DPs and pass 2 returns the distinct predecessor pair. QED.

Step 4 (the pairs that are not good, and the disturbance). Let W(t, y) be the event (tau = t, V_t = V_y) with xi_t = xi_y = 0 and work on N1 <= k - 1 outside E1 and E2. By Step 2, P(W(t, y) | xi) <= Pi_(t-1) / ((1 - kQ/N') N') <= 1 / ((1 - kQ/N') N'), and sum over t of P(W(t, y) | xi) is at most the sum over t of 1 / N', so at most Q / N'. A pair that is not good fails one of the following; each failure is bounded by the expected number of pairs of that kind times the hazard.
(a) (G1) fails: y is among the a(t) earlier evaluations of the trail of t; a(t) is at most g(t), the number of consecutive 0 coins just before t on its lane (g(t) as in Step 6 (ii)), E g(t) <= sum over i >= 1 of (1 - theta)^i <= L - 1, so the failure has probability at most Q L / N' = P_own.
(b) (G2) fails: y is in the batch of t before t, at most 255 pairs per t: 255 Q / N' (charged in P_tiny).
(c) (G3) fails: y is on a long trail. A long trail has at most M evaluations (it is cut at the first slice check at age >= c, or finishes before), a y has at most Q partners t, and the number of long trails is at most the number of successes of the scan of Step 6 (i) (disjoint windows of c coins 0), with expectation at most p (q + 256) / (1 - p) there: M Q p (q + 256) / ((1 - p) N') = P_long.
(d) (G4) fails. rho(y) > B - b(t) means that the B - b(t) coins after y on its lane are all 0 (they lie in the batches b(y) + 1, ..., b(y) + B - b(t) <= B, inside the run), probability (1 - theta)^(B - b(t)) <= e^(-theta (B - b(t))) for each y. By Step 2 the pairs (t, y) with y < t contribute at most sum over t of (t - 1) Pi_(t-1) / ((1 - kQ/N') N') e^(-theta (B - b(t))), and (t - 1) Pi_(t-1) / N' = Pi_(t-1) - Pi_t, so, with b(t) <= ceil(b / 256) for t <= b and the sum of Pi_(t-1) - Pi_t over t in (a, b] equal to Pi_a - Pi_b, at most (1 - kQ/N')^-1 sum over the bins (a, b] (Pi_a - Pi_b) e^(-theta (B - ceil(b / 256))) = P_delay (the bins and the enclosures of Pi are in the probability-certificate unit below). The second part, a(t) + rho(y) >= c: a(t) <= g(t) and rho(y) >= 1, so it requires g(t) + (rho(y) - 1) >= c - 1. If t and y are on different lanes the two coin sets are disjoint and g(t), rho(y) - 1 are dominated by independent geometric variables with values in 0, 1, 2, ...; the sum of two such variables is at least c - 1 only if a single i.i.d. sequence of coins has at most one 1 among its first c coins, hence among its first c - 1 coins: probability at most (1 - theta)^(c-1) + (c - 1) theta (1 - theta)^(c-2) <= p2. If they are on the same lane and (G1) and (G3) hold, y is on an earlier trail of the lane that is short, so it ended with a 1 before the start of the trail of t, and the two coin sets (those of rho(y) up to that 1, those of g(t) after it) are disjoint: the same bound. At most Q (Q - 1) / 2 pairs, each with hazard at most 1 / N': PP p2 = P_age.
(e) Disturbance. For a good pair let r' be the number of evaluations of the lane of y with index > t up to and including the first with xi = 1; the coins there are independent of F_t (L5, t is a stopping time) and r' is dominated by a geometric variable of mean L. The evaluations of Y after t and before its DP are at most r' fresh evaluations, each a collision with conditional probability at most (Q + 2^18) / N' given the history (L1; the last one, a DP-valued evaluation, is covered by E2, and counting it here only overcounts). For this bound W(t, y) is taken without the restriction to N1 <= k - 1 and outside E1, E2: it is the event (tau = t, V_t = V_y), which is F_t-measurable, so P(W(t, y) and disturbed) <= P(W(t, y)) L (Q + 2^18) / N'; the events W(t, y) for different (t, y) are disjoint (the values V_y are distinct before tau), so the sum of P(W(t, y)) is at most P(tau <= Q) <= sum over t of (t - 1)/N' = PP: PP L (Q + 2^18) / N' = P_dist.
(f) (G5) fails. The first part, a(t) + rho(y) >= cr, is the second part of (d) with cr in place of c: probability at most p2(cr) = e^(-(cr-1)/L) (1 + (cr - 1) theta / (1 - theta)) per pair. The second part, a(y) + rho(y) >= cr: the g(y) coins 0 before y, the coin of y and the rho(y) - 1 coins 0 after it form a run of 0s of length at least cr among coins disjoint and dominated by independent geometric variables, so the probability is again at most p2(cr). At most Q (Q - 1) / 2 pairs, each with hazard at most 1 / N': 2 PP p2(cr) <= P_rec (cr = ceil(12.73 L), and p2(cr) <= p2(12.73 L)). The union bound runs over all Q (Q - 1) / 2 pairs, so it covers every collision pair, in particular the pair behind the first detected key match, not only the first collision.

Step 5 (the sum). With P(tau <= Q, N1 <= k - 1) >= 1 - Pi_(Q-k+1) - 2^-40 and the failure bounds above (including the recovery-cap failure (f), P_rec), the early halts are charged in Step 6 (eighth cut) and Step 7 (table full, key false match, stage-1 budget, recovery cap).

Step 6 (the cut count and the long trails; no premise). Let K be the number of trails that the run cuts or would cut; the eighth one halts the run because `CMAX = 7`. Split K = K_A + K_B: K_A counts the cut trails whose first c evaluations are all fresh, K_B the others.
(i) K_A. The disjoint-window scan from the credited proof bounds eight fresh cut trails by the upper tail of `Binomial(n2,p)` with `n2 = k + 263` and `p = exp(-c/L)`. The certificate evaluates this tail from the live n2 and p.
    P(K_A >= 8, N1 <= k - 1) <= P(Binomial(n2, p) >= 8) = 1 - sum_{j=0..7} C(n2, j) p^j (1 - p)^(n2 - j)
(the tail increases with p, so p = e^(-c/L) is allowed).
Any run with at least eight total cuts has either eight fresh cuts, or at least one non-fresh cut. The displayed order-8 tail covers the first case. Step 6 (ii) covers the second case through the S, X, J2a, J2b, and Y root events.
The same scan counts the long trails of Step 2: a long trail of the free run is a window of c coins 0 at its start, the windows of different trails of a lane are disjoint, and a run of 0s holds at most floor(length / c) disjoint windows, which is what the scan finds; so the number of long trails is at most the number S_c of successes. The trial outcomes form one i.i.d. Bernoulli(p') sequence read in a stopping-time order (L3), so Wald's identity gives E S_c = p' E T, T = S_c + F_c the number of trials, with F_c <= N1 + 256 the number of failures, E F_c <= q + 256: E S_c <= p (q + 256) / (1 - p) (used in Step 4 (c)).
(ii) K_B. A trail T in K_B has a first non-fresh evaluation at age <= c - 1. Its previous evaluation t (age a(t) <= c - 2, T fresh up to t, so a(t) <= g(t), where g(t) is the number of consecutive 0s of the lottery just before t on its lane) is fresh, and V_t equals the input of an earlier fresh evaluation e' (the first evaluation of that input; a start is excluded). Call t the joining collision of T and e' its target. For a lane position e let sigma(e) be the number of positions from e to the first 1 at or after e (inclusive), and f'(e) that position: sigma is a function of the lottery, so it is determined by G. Choose T in K_B with the earliest joining collision. One of the following root events occurs:
- S: e' is on T itself. T then cycles through its own non-DP points and is cut.
- X: e' is on another trail T' and a(t) + sigma(e') >= c (hence g(t) + sigma(e') >= c).
- J2a: e' on T', a(t) + sigma(e') <= c - 1, and T' has a collision at a fresh position in [e', f'(e')).
- J2b: e' on T', and e' lies in a run of 0s of length >= c of its lane.
- Y: some trail has a collision at a fresh evaluation t'' while it has been fresh for at least c - 1 evaluations (g(t'') >= c - 1).
Proof that one occurs. Suppose not S, X, J2a. T evaluates the inputs evaluated by T' from e' on, one batch later or more, so T repeats them (non-fresh) while T' is ahead. If T' evaluates e', e' + 256, ..., f'(e') freshly (no collision there by not-J2a, and every non-fresh evaluation of T' is preceded by a collision of T'), the output at f'(e') is a DP (fresh, xi = 1), and T outputs the same DP at age a(t) + sigma(e') <= c - 1, before any slice check can cut it: T is not cut, a contradiction. If the run ends first, T, which is behind, is not cut either. So T' is cut before f'(e'), with all its evaluations from e' to the cut fresh. If all evaluations of T' from its start to the cut are fresh, they are >= c consecutive 0s containing e': J2b. Otherwise T' has a non-fresh evaluation before e', hence a joining collision before e' and before t; if it is at age <= c - 1, T' is in K_B with an earlier joining collision than T, against the choice of T; if not, the first c evaluations of T' were fresh and T' collided at age >= c - 1 while fresh: Y. QED.
Expected numbers of root events, each from the hazard (L1) (a collision of t with a given earlier value has conditional probability at most 1 / N' given G_(t-1), which includes the lottery, so lottery conditions can be attached):
- S: the inputs of T before and at t are a(t) + 1 <= g(t) + 1 values; the bound is `Q L / N' = 7.291978672274e-06`.
- X: the same-lane and different-lane geometric-tail calculation gives `E_X <= (Q L/N') exp(-(c-2)/(2L)) (2+(c-1)/L) + PP p2`.
- J2a: two collisions, t (joining onto e') and t' on T' at a position in [e', f'(e')). If t' < t: for a given t', the e' with t' in [e', f'(e')) on the same lane are at most g(t') + 1, so the targets of t are at most the sum over collisions t' < t of g(t') + 1, and E_J2a1 <= Q L H / N'. If t' > t: the positions in the windows [e', f'(e')) of earlier joining targets number at most the sum of sigma(e') over collisions t, with expectation at most L Q (Q - 1) / (2 N') (E sigma = L), and each such position is a collision with probability at most (Q + 2^18) / N': E_J2a2 <= (Q + 2^18) L Q (Q - 1) / (2 N'^2). E_J2a <= E_J2a1 + E_J2a2.
- J2b: P(e' lies in a run of 0s of length >= c) <= (1 - theta) p2 (the 0s before and after e' are dominated by two independent geometric variables), so E_J2b <= PP (1 - theta) p2.
- Y: P(g(t'') >= c - 1) <= (1 - theta)^(c - 1) <= e^(-(c-1)/L), times the collision hazard summed over t'': E_Y <= e^(-(c-1)/L) H.
Combining the fresh tail with the same S, X, J2a, J2b, and Y root-event bounds gives `P_cut = 1.453120036793e-05`. There is no cut-count premise.

Step 7 (the early halts and residual events). The early halts are the eighth cut, table full, key false match, stage-1 budget, or recovery failure.

Table capacity and key matches. Outside `P_60`, fewer than 60 collisions occur. The number of finished trails is then at most `N1 + 59`, so filling `tmax` entries requires `N1 >= tmax - 59`. The Chernoff bound is `P_table = 6.603983930862e-07`. A false 48-bit key match costs `P_key = 6.506698101375e-05`, using key space `2^36 * 2135`.

Sixty collisions. At a fresh evaluation t, the collision probability is at most `(t - 1 + 2^18) / N'`. For `w = e^5`, multiplication of the conditional moment bounds gives

```text
E[w^C] <= exp((w - 1) H),
P(C >= 60) <= exp(-300 + (e^5 - 1) H)
             = P_60 = 3.093309208323e-99.
```

Stage-1 budget. Let `eta_t` mark that the low 20 bits of the independent uniform value `V_t` are zero, and let `mu2 = Q / 2^20 = 323342487314786865234375000000000`. Fresh stage-1 hits are at most `sum eta_t`, which is `Binomial(Q, 2^-20)`. The multiplicative Chernoff bound gives

```text
P(fresh hits > 1.5 mu2) <= exp(-0.108 mu2)
                            = exp(-34920988629996981445312500000000)
                            < exp(-1000).
```

Repeated-hit partition. Work on `N1 <= k - 1` outside E1 and E2, as in Steps 2 through 6. Outside `P_60`, fewer than 60 fresh collisions occur, so there are at most 60 maximal replay windows. A replay window starts after a trail joins a previously evaluated orbit and ends at its next DP, cut, or halt. Split these windows into non-simple and simple windows according to whether an input repeats before the terminal DP.

Non-simple replay lemma. A non-simple replay is contained in the root-event union `S union X union J2a union J2b union Y` already charged inside `P_cut`. To see this, choose the non-simple replay whose first joining collision t is earliest, and call its target e'. If e' is on the trail of t, event S holds. Otherwise use the target trail T' from Step 6 (ii). If `a(t) + sigma(e') >= c`, event X holds. If T' has a fresh collision between e' and `f'(e')`, event J2a holds. Assume neither event occurs. If T' evaluates the segment from e' through `f'(e')` freshly, T replays that distinct segment and reaches its DP before age c. That contradicts non-simplicity. The observed non-simple replay occurs before the run ends, so T' either is cut before `f'(e')` or has a nonfresh evaluation before e'. In the first case, an all-zero run of length c through e' gives J2b. If the trail was already nonfresh, take its first earlier joining collision. At age at least `c - 1`, that collision gives Y. Below age `c - 1`, if T' is cut before the downstream repeat, then T' is a nonfresh cut trail in `K_B`, and Step 6 (ii) gives S, X, J2a, J2b, or Y. If T' is not cut before the observed repeat, its replay follows the same DP-free suffix to that repeated input, so it is an earlier non-simple replay, contrary to the choice of t. This is the same exhaustive descent used in Step 6 (ii), with non-simplicity replacing the assumption that T is cut. A DP-free cycle is the direct special case: the collision that closes it is S when it closes on the same trail, and otherwise the descent gives X, J2a, J2b, or Y. The cycle cannot contain a DP because the first traversal would have ended there. Step 6 bounds the occurrence of each root event, not only the final cut halt, so this use adds no second charge.

Simple replay lemma. Fix any deterministic 256-bit point z. Expose the random-function orbit from z until either an input repeats or M outputs have been sampled. Each output at a distinct input is an independent uniform 256-bit value. Pad the sequence with independent uniform values after the first repeat. Its low-20-zero indicators are then `M` independent `Bernoulli(2^-20)` variables. Every simple replay from z is a prefix of this sequence. A DP-ended prefix includes its terminal DP hit; a cut-ended or halt-ended prefix is shorter. In every case its stage-1 count is at most the count in the padded length-M sequence. Therefore its stage-1 count is bounded by `Binomial(M, 2^-20)`, and, since `2 ln 2 - 1 > 0.386`,

```text
P(a fixed simple replay has more than 2 M / 2^20 hits)
    <= exp(-0.386 M / 2^20).
```

The merge target may be selected adaptively from the earlier history. Rather than condition on that selection, take a union bound over all `N = 2^256` possible targets and all 60 replay windows. This simultaneous event covers every adaptive choice:

```text
P_replay-simple
    <= 60 * 2^256 * exp(-0.386 M / 2^20)
    = exp(-A_replay),
A_replay = 0.386 M / 2^20 - 256 ln 2 - ln 60
         = 44003803880147324310981212137.1814164253236237371706080936417
         > 1000.
```

the probability-certificate unit below evaluates `A_replay` downward and charges the outward upper bound `P_replay-simple < exp(-1000)`. It also checks

```text
240 M = 28688911496847270924380167267346519280
      <= 339049171978589952000000000000000000000 = Q.
```

Outside the root-event union and the new `P_replay-simple` term, each of the 60 replay windows has at most `2 M / 2^20` hits. Thus the repeated hits are at most `120 M / 2^20 <= mu2 / 2`. Together with at most `1.5 mu2` fresh hits, this is at most `2 mu2`, below `e2max = 2 mu2 + 64`. The residual probability of the stage-1 budget halt is below `P_stage-fresh + P_replay-simple < 2 exp(-1000)`, in addition to `P_60` and the root-event union already charged in `P_cut`.

Recovery and the three small structural events. A recovery without a pair comes from a false key match, already charged by `P_key`, or from one of the fewer than `2^18` starts lying on an evaluated trail. The latter event is `P_start = Q 2^18 / N = 7.675801233450e-34`. Outside those events, Lemma 1 returns a pair within `cr + 17 D` calls (when both trails have length <= cr; longer colliding trails are charged in `P_rec`). A repeated DP-valued output costs `P_DP-repeat = k^2 L / N' = 4.149537557375e-34`. A partner in the same batch costs `P_same-batch = 255 Q / N' = 7.466618784064e-37`.

The outward-rounded certificate computes this subtotal and verifies the complete residual reserve. It adds `P_stage-fresh` and the new `P_replay-simple` term to `residual_actual`; each is below `exp(-1000)`. The total fits inside the charged `2^-90 = 8.077936e-28` reserve. The certificate uses outward rounding for every exponential and rational term, so it needs no probabilistic rounding allowance. This proves the lemma. QED.
The outward-rounded certificate gives `P_F >= 0.390000001000082853534934631642142850501745205189605206393696 >= 0.39`.


## 5. H1 and its scope

H1 is the predecessor's four-clause random-function comparison. It states that
this fixed SHA-256 attempt succeeds at least as often as the same bounded
algorithm using a uniformly random function. The clauses concern fresh-output
independence and collision hazard, random-mapping counter-start iterates, DP
probability `2135/2^122`, and the conditional collision hazard under adaptive
history and later DP flags. No differential property is assumed.

The original random-function proof is retained above with the new parameters.
It now applies to B=1324410828041367000000000000000000000 batches, Q=339049171978589952000000000000000000000 evaluations,
and L=5316911983139663491615228241121378304/2135. Packing is injective, the slot scan retains increasing trail
order and first-match selection, and recovery retains the first predecessor pair.
Code reuse changes no search event. The attempt's four terminal failure bounds
and recovery-cap bound are recomputed, not copied from the older numerical plan.

The 60-digit outward-rounded certificate gives
`P_F >= 0.390000001000082853534934631642142850501745205189605206393696` and checks the residual reserve explicitly.
H1 remains heuristic for the fixed target. The source of the generic premise is
van Oorschot and Wiener, Parallel Collision Search with Cryptanalytic
Applications, Journal of Cryptology 12, 1999, DOI 10.1007/PL00003816, together with
the credited same-challenge generic constructions. Their premise, not an
empirical full-width birthday experiment, is what the claim uses.

## 6. Executable checks and organizer experiments

The original kernel tests still check the bounded emitter, independent builder,
43,541-record stream, scalar walk, inverse encoding, chained batches, rolled
recovery, and complete two-block digests. The native interpreter additionally
checks arithmetic against Python integers, every packed-table boundary,
increasing first-match order, persistent recovery registers, and the DP screen.

One common acceptance gate runs the construction and twelve actual
instruction/control mutants. The mutants alter digit encoding, lookup index
direction, a packed shift, the radix, a checkpoint address, stride arithmetic,
the post-recovery branch, returned predecessors, the handoff position, a constant
register binding, a required zero clear, or the chained-call limb masks. Each mutated program fails the same
semantic or lifetime checks passed by the unmutated program. Truncation,
corruption, and legitimate early halts are separate negative controls.

Unified-arena tests run actual search-to-recovery transitions. A synthetic map
keeps the search live until a genuine key match, then recovery writes through
memory that held the search body. Tests also cover every terminal path, the last
checkpoint record, retained-code boundaries, dead-body/decoder fetches, and
capture of seed and trail IDs. A 100-call persistent chain checks each native
paired step against the scalar walk, including fresh probe inputs. Full-width
controls execute two arena body batches and force an actual native matched-key
handoff while rejecting calls to a detached engine. Independent retained leader search and recovery
check candidate order, counters, and returned pairs at width 16.

`bssha-n16` uses the complete two-block digest projected to 16 bits, with the
original bounded seven-batch plan. It now uses the packed table and physical
arena. Batching eight independent trials at a time limits organizer host memory;
it changes no trial's inputs or ordering. `proj-k0-w256` retains the three source
types and complete-digest low-16 check. The organizer recomputes every returned
event. Neither experiment supplies a full-width probability estimate or changes
the score. Persistent-state and mutation tests are deterministic correctness checks.

## 7. One-MiB arena and lifetimes

| Byte interval, end excluded | Bytes | Search | Recovery |
| --- | ---: | --- | --- |
| 0..816832 | 816832 | Table, final-word padding, guard | Checkpoints |
| 816832..990996 | 174164 | Body | Checkpoints |
| 990996..993336 | 2340 | Native table routines | Checkpoints |
| 993336..993344 | 8 | Padding | Checkpoints |
| 993344..1001759 | 8415 | Recovery and retained controller allowance | Retained |
| 1001759..1001760 | 1 | Alignment | Alignment |
| 1001760..1018144 | 16384 | Plane copy and birth words | Retained allocation |
| 1018144..1020192 | 2048 | Trail IDs and scalars | Recovery arrays |
| 1020192..1048576 | 28384 | 887 registers | Same register file |

The search contains 184919 code bytes. Both search and recovery peak at
exactly 1,048,576 bytes. The 993,344-byte recovery pool has 15,521 records of
64 bytes. The table, body, and table routines are reused only after setup has
exited and a matched-key handler has captured r, t0, and t1 in retained registers.
The recovery array is then reinitialized. All recovery exits are terminal, so no
path resumes a body or decoder fetch. `Arena` enforces these phases in execution.
The main table and checkpoint pool are never added as simultaneous allocations.

Memory has no direct scoring credit below one MiB. The benefit comes from more
table entries, a larger recovery checkpoint capacity, and the re-optimized plan.
The native word/instruction pricing and legacy handler/setup envelopes remain
inherited assumptions. Python interpreter objects and test instrumentation are
not proposed as the priced implementation.

## 8. Attribution and source binding

The immediate dependency is de42b4cc-7d45-4f4d-85bd-65fd00fad5aa. Its existing
material lineage is retained in the accompanying dependency declaration. No
publication, contribution, or independence relationship is inferred from a
matching name. The public submission note identifies the reused components.

The exact dependency declaration contains the immediate source plus all 18 entries in its complete published declaration:

- `de42b4cc-7d45-4f4d-85bd-65fd00fad5aa`
- `068ba228-dd60-437d-b36d-6773fec1a7be`
- `1f18d544-cd04-4177-8739-fad19d55a98a`
- `26d9ad0b-e6f1-4370-abb4-b36aa97ab9e6`
- `27984c2d-fc4b-4285-a430-c5f364c10a7e`
- `6f66a099-7772-441d-ab2c-67d94c620e13`
- `87cb17fa-d025-4066-bd13-91d9936ce327`
- `93618c27-3783-4744-904a-5d688ff610f8`
- `95263e47-d61b-43a6-bb46-30ced2488280`
- `a4c6ba2c-25e0-4d35-80e9-ae2ea22eb05d`
- `a74a20c8-3a52-4742-8970-e20dc0ad8b76`
- `b3f10279-3fa4-4d7b-9011-3faa2ae352c8`
- `bfcaad61-9487-4edb-8778-b5408e713d01`
- `c83bda97-88bb-4125-b581-5b76c6c7de6a`
- `d22ae1b2-2368-460a-b6d4-1e5e37ceb735`
- `e7631f7c-9d3e-489d-b7fc-6baac3a2ed45`
- `f7b1dea4-2883-45d6-9c0c-89a5d4ad1b1a`
- `fb8a3bce-1839-4b9a-ab67-76670b4a05c9`
- `ff37a322-c5e7-4656-bb89-02f1a5d0e213`

Publication and same-benchmark membership were checked through the live Pareto evaluation metadata. Declared references are not described as verified attribution edges.

The experiment source SHA-256 is `1540c09b781fc85da4ecf389fd0d28aec2edd2f1caef90331a80839e161338c2`. To fit the organizer's 64-KiB
source-view limit, some helper units are losslessly compressed, checked by SHA-256,
and loaded into the same module. This is organizer-test packaging only. It adds
no decompression to the native attack. The full plaintext of every loaded unit
and the live controller follows, so review requires no external retrieval.

## Appendix: base

SHA-256 `cc32693c5455566399b9ab8064c7ab3aac66c54bf43bd836538a0674acf1abc3`.

```python
import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt,log,log2,log1p,exp,comb
M32=0xFFFFFFFF
ROUNDS=40
UNIT=2896
LANES,ALL=256,(1<<256)- 1
GEN_C=__import__('lzma').decompress(__import__('base64').b85decode(b'{Wp48S^xk9=GL@E0stWa761SMbT8$j;Axm7vt0l>9!f+7EcWv7Lz|0s4)@dlRYKFC%Ru5;*dPDz@ko%eHoL=sDmUb#(BDY$sOdRsL4LgFV@TvGnBm&8X*$+kcDh^O@~cv2g3#G!SX9KwuG9sp<qJ;^M}*3J<%9IUy}q*H_Fc<iOI%ppo;J+@9zbLL9UKt2Lt+Zy4idiVT5z9G925GS+^ot`X7ccF=aT&{6i<&gzCS?kQwNK1EB+PZ-_k!ZoVSm{A!2Py?tcBB)lR>~bl)*f<5_z?o)t<ej0ruIua?K*-L7{7C<$+bgPaSZvs7U88<}}nM=a{fvx*znq>Y!+?lg}bw!@_zGSNs4xOWi$@`2zT-D8URM>HDq@ASkYQ!{<OKz`FBA^XZ{ZzKAl8Ci5jyG&6*!Uw6-*rJ+BUe@IHs%}zQ=#euV=|SF8s1x5-D09-AkBCveQDAKICo&ic`YG3mlY8C1Z%MS$o3!f?R+Mr7TD4o^wkHlZ6AxV#FYEk7)Q8%=Hh&A)1s69I+?<y%t?4ChHoXR<lK$sS0m?u=O6Q(wZu7LV_h@TGgiM2LJNhWPHa}cfS&=D_i~wlGh#blQ_l=qCtiKc9Otci-K$vwrpiX^+qU`_pzcO~6&^oi&xmwv;c2$sToS-JMy7^xmGXoyqZMh-)=LRuD-__SJr1yT62G2OxLhLa$H)L*-Ey!O));-9>_eW2^oXojJQW08+!vot_vPL5%vXc~ivx-5|$8~Ni0vlcD{oX8p-nJZ(`A;H|gWFnV;XcQ^6jZl&PgKdQc$PTrpsCsLWJBQ1sneC94<L>Dk+~x4N6<7|xg>`$0^br6?wMf(R8t!+Haf+wtW85WtYTm7)@zl$iWeQdYbc_UX=X+!JS-qNSh{m<iLda8mphl#xlO@|epO7BhTq#Ktd&Y?rEP>mr@@!@vK6XVp;B>%?u*}pUwiHk3UO&V>$8t2-P(pE<*I52@_-99FurBKF-I7^A|3%`nDIpk4$01-nMaG15lCS0%|_pYoN`;^Ay?$MPqc;X8LD?ay2ZT#nLM}<&l#TWS%Cq~lD9ZAs!*ACCGF0!7T-d9n_kVCmtJ`sH?YF*tw(g=gQwIb6hMv?4F7m5DP1GHR?2QG0`2V?I`#>318#KA^5wqpy2%nQz$<t^>}Jmi%^^$Gh<B3NR$t%-No@)$&zO*o)49bU5}sEkG0<>t^O_>Umf)xVuE~_8VHK08Vlv$T+?0J>3=h9u6>vl2Q{Y$)9!G!wsUy_{4NKH-%0E0b71K7~z_khDu!A@E09$W}<;9^~87KxLllQJuC^L=N23%!|0tdMh+S>+xQCG==3z!zU0q}B*(p$$59nD!b0JeDNf>~raTEq}qzDEyte>K54_5^#1CD^UOdBwtqj9(Oh@R(=F>0N{^;^Bv&QE2y$pBwpC=!iA4xkZ`Fhe-a~fF~gMx1mv|k7vjD^8Sr&#5IE2sPb-FkC+#H4#<1a_i7k4b~4pID$$-De7nF?;2od7p|#AKiyd@vb@kzQ`p+eOJNto|3FGxzd+QLm;ZK>{kz^$Dot7}A)%ANmr~iQ|xkA;RX-9Iz!VZTgQ#T4Rts%Rui=u~v>Lj+Wi`;@|?K4z+jJ7_q>EU73q4~n`yiAaZVNN{@T13XkF_1xOP^SJku-GPTB5S%&S`2HhpKO)1*~1sPdTBlw%a}vy81zV$ex(<W*E;?|0Rfhe^k>A={EM&s;Z?(g-4N%%UcJs{u`zF1P56)uUu-$iuA!x8P!0HWl)I8_=uM?o+s7~{FrFAt5!nb%8Y8=wYS~i7xS{kmY|e_)4Xv$;ec^_uL_gwoWre$rm`h?(#=}>)=TNYSdQY^L0P7|XxsCI2c}5ksmwWkQcgK*qIJ90v6tMs%DNoc~#L6XKoIe3^+<2buAYlk=D5u0m<hnTo0}!0}Q`GLF_-(uU73KjDbu8Xu$^+?7vL6h?WN7OehpJ^vHSKQ9#fCG?u&ao&HR?6jF5P#LibsJz%JR!CcRFuC%Y4x7!@X@h8G1b_FN)+G-gmkb_x#11biqS8ZQz4KDQ#k~bE}x?L%ogX(C~Ck5PSf5Qj<uYac!qs1~hk8O@ImG6a6-x^{|cDzD`=SfTAZNQ%7T7Nn3ZXGj-xHOBNkY(HCwwD0+f8p*s3v=A&bbGcRim<77%Q8F&kL>Zvo77OHy*N{F7m**XQX`7rfCAs30n?7O5tmb${$xOeWASzVuq4zK$1k(Iz3j%|#Ufw0NfG7<NX4Yf!K_9r@CQ5u;SK#+kPyb63|3O`|-&-Zs{AxLe<rRYS3Tq)_+qtDCDqJ8>-xk8yR4vg%UR9SYLB$XMmx5dvNUgOWieDw2G6G`32kbEO~8ZNoXz7konDb6e3{mP83oIH`o#Gf04Sy{sKcLUGGvQ0z81TGA3?ESteA^_mE#G)g@$g)tx6SfD>v*0-YKX-&*Ewu10Izg$?T|SV(<a+P^kOu~#PTJI(^)?Vg2V+PRW<ZA;jB_DA2Xj#nTvP(mhc=~32g>19@h(S6h;h;+4?C<w)hpRgS=q^YGk&PP@AlPXF<xya>8P1K@o;m+%A$V<Q^E4!45}S$E<=;KQMJwWa;o9jiQL0zzKzh6=px1Em_(v=4dDNyVLqRLian8`S+J_}l{Ih@eK05M&6{%cIG}AO%cGW*Dyldeo1FQC&Z$T!JjU8N->cC%A0KRWEpX0FWYhti$)8t_RR<Sm8y*dL;=;5T3qiTFbMKDvM?4NzOBb{lGUjqjS53p7Eh8k$JeffGiCgT4<j%u9f#cz{fCK3Z6_#w+B(4;j%#-_1FE`5F;98PIX7q$4beY~fQ4#hY6{7=KU;dtx54}SMGPz+>eDpY(bVB${s>X!1$?MW@bs1Nw!=CIOd|w1GWX!XKndW(yqGZIow-EjEh8k!Y<Ahz=j272K+$+VlR5%8d1o%!e+%u}bR8sZ83+QOL#`oo9J4k|%gZc4>oHwIqPK`wJVQo#y`SY^1aMb@2{dgL_%a0@KMUo}>J_^u1|JqJozrga}DaA{Y1I=>QEOVTC4eH;MUt-yET<@1vO2=a+gs8#b;t(K=LGLnWp=Zn9AbW&)6m$4-yS9zcl^^m7T+_yJhq<dVWmTl{hR^TsCv=KRGtuN5N*Y8CWm@WohuW4;)MR9+K$QB&9gs(MG`kJy32T9ULggrq7LM}z*=I5tp;WV>loGbp@y<q5SueANInmBExsX6_a=bSMSqbNL{%u~GoUQtz;^F^}-Ao}`e|L2w)|Br44louJNke&AeM})Uj3{4X!vHK<=xHM>(TStk9p}l9Kks`=Og^itTzWB0ys66ZqVfj=GyT?%<aq{ts{Ad;$5{rp<=f%kuLs<rZXBMy`d#}!ijX&;PQ^*m2iX8Qg!r~?#*ZB8NNpMd%x)sfF??KaFfhjhQ`an;OgY{vVBeN|{&D3!_jmR-me;$Y!}T9O-5hPna6jFFztCdEnD+itm3U*8%5{7r?@sA?eaT{(-j?&@9bDiiT(;4+dwMTqd%jJWD$lfX;GJVe$}xwnnnFZ|!8Wb!Gh<zbc-Gt7B*bCN_39eY@r<%W`M_jQHYNTl`bC@&yax|0HX?}zuJ^1RHAd4I7#-^@=8Guv!87S?%P|8PRExg?$PUqqvg{fV<H(&5S|jgD`zdyUmtv+bCT9h`bu^cDC9(B?=HbZZE1)ZWi9nTwsb>F(#j#}nRsl0@B{ZwLE~gF12u-A}7ES~<5>o+bh{k&@6Y7e<1^H~wdNVCpOe(2LICib%s_wj<d!EVAkj%s7YG{H%fmBGY>{Td-H1mSL(C|=2cyK7>Z?}4`q2KC!wOgm}mM-&(CF$@5tk1T#yPMz9T;E$&U(tV2DkgDJHAOV?dQb$=n2D6OrW3d!$Ok*yOZ&C{df_B>FTzO5Gdx3M7w>Nfp1I3~iQISjHO!5C56J=yhvMlq+}*46D&ZU=QqVATg&2$;hFvm@bmdMX4h~<j!@QQ)iAg<1sz`;P3Z$ra_j@{E?<Z}!6ww~Z2`YaFZZ`e&EK<sqW0APS(In|I5zj9?ipn44+5zf4+@-$@q-eGCdcx~YOzl&AK)m(8LbHs#V)9xm!Qhl;l_<2uM_m2D@io8FAif1J=d^Gp_QyNWpd9`W$0a%)Ii^}9_wIw&@Dq&#-T(Mi)Nqj<7SYcf1o5yegVfQEmOw|Lk=imxs8K_A4=KM8jgoVB!?*D&=^&VQHY4~5_PV}%q?`sva?``Wl`1(k&wD*RA6K%WWJ=l@_b7;Uq(m3b0S;KKj?03c>JT<IbUJJF!$5~A0f$pw$QrA2iMY?)FYDgO4_)r!x<O}Rvv{Z0YK5wdMDK|Mc?_@Ozb!tAx=qH(5emb|bQXC&%M_&8=ee=IY`7#|{1PQKTaX)&daKt+dE@%;TDD@F;@`Pzfw(uT{!as#bDL2@_xzHok|J?a8ZX3SrCR_yTiG1BkMFb-Z*THuNqaOmQVHVcY=tF`rtCL>X)nq^WZUXiUsS*-J+Mj0+|hTg8W;&XTGAt?$S-mM<QjVA%Tso-z{9~PMC}o!4qLYPt9VJmI~&M)xUY@CL#uRE5V|)_vAyq;Lbp&SGU?>K;hJx3N=;?t1Nso#yyk-SY|4{56A!Tif5p%IZJd7tr=VPD`*CMW@ZJz_0tct%)sk_~*3Ag{E1|uxBr%-lBV6I?lg#^4F+UV0Rv{l=rnhCbe-_Sr^=^}quLDOcEW}jSAJ>thvw_n=#(1>fpOh}B0<=fg!pUf>J>lwVacl0^@Z;PlWSDGAu_U{>SVXITod1MTy{z&1H&8mJ<=PbRRkrr}aC9tEx_Vr?8V&<0VI)$)yaBa1HjN#MX~eQG+HgDh)lb)&q5gFY`+wC0+^_eD8Z|aWvvtqM&=12PU<J!e9@m3k(ERl54Ex2&gtH+b`?Qxs<yEkVJo?m0jG|l^tilR9av8m|fK(aK_$Mo(IX;A;U=*yUz;Z$sqqR4+!98AWnA(=B=n{3e&!~*ewA$Q9?Aw&E;IMmQ%t=@rKt~iz-Z+(^)lHO|^49B9q3Kj*_VqAUSuKG#f@|6EW8?7+IZvDs8zfa?K11Acv7dqrP$E3Y+vmchT#7ZD0NLO)m&IFDbS=iQcAvGk{QF_vLmw4OlprA4#I(lq-6N2XxL*y%gdbZldL$6|EB%R4={T~qCO~BSs4mJl_grV!js38-cvGiC>0(3w;unVem@IvvM+OS^B|oyRe_oE?)0;S*2FW)$FD4j_KOWvbq4@&u<2?p3n*=*TPa?YX?qEK?)Squ@2+NHb0xc8<lHndEV$%OO{0<WNRvLh02OF%08~g$%^TF`PZYm8`?-cqS=-m{)kHrZL9tn1>yfCzjmMjy=)xX}6WRtZx68y34AES8Mtgzb#x*xM96DP&1uHQg9TtknV4WGyo{k)$%gs#g|>iF-FKc0gtOCf=f2CDX3v;4_p)Lq#osKtVfnXwfObX6Gs!nV03>DWOoM+ZxVt7EPM%M?>~6#n;_zq3>rvJcLBl!FCoCqjT!(er-h0`SY8>1<d{P)tHgnElbn?JoYZjw#~DO#K5cEi*nap@nV)&&nZvK^~d9xy(<Ljm}Bt7<xtcE#+~{8IO{yDOtfG|4*t#228Rb1B!=qW2zzb<(~r_`+}r;e8CRJFE5o7pXn4DE-5VS_9NxFZsTe?7k!qvq9#uZJY3s(;a)y*>`!(E2GtuTl~q*nrOALl$(eMfBJghLU6}uxhwsg+H-y!QVM^2B5NljVU2&Te{y<vB=+=d+WdM`8es{Fw&4O>QE7*+3mJbQAQM75!8*_^ZClR=g%^Gl~BhOYY0&qmIu@;9ZB(HWwsv|-wMa6o%Quo-A^H7f2Q?*!|tE>ab7PsYsjPj4tpQzBYFZ+Q`dBVh{x=W`N-X-)E-8TO;>b7!Lop=t-WyxAovj>IIpt6`ZR|9&Mn!x9>Zbp$lLXaExj+NhN-R;?WJat%{CqJ6}qRtH?3ONfOt-D|OY~FxL&l{{~_)gD0gg>^6QDB(o))OZx+v$CJ>_JLR9cFvqCCbp!%F<GM{V!~)X4k;<m_)jU7}$?&&HwaZ;U!;Z<ZN_9H@t42J5CChGx&#z^Qcv6ua}#L;;_b$&cMz8VN9E#O&7)WB~aEB6U5nt;{IRqUfn1l9iTw~q7jGDi^p0(jIuR~05)2lMQ@n2hO)TnzCt~KhnvF;!bFLhiF0iq3fXAwa3a^6>Zw40XgawjNEH8>xLGDQ6fWR7rFV}g9^)HhHc7?Bnuz=f`=UkaoZ)CS5;BzG9dQKk$_lp4s;@X7`@u;SIHZUsv17dDu6u{)_#D2a_>L|PWzBrM`Ep!J^iQ!P;+?0qvU%#$hGVftAf$5GrSP=YaHB&YG?tisZL;8AFW6JiogL1p2A|Zj(J<}kK@AG~+4UFEIZk@6UH`|1n~>sc1r0xEc@mEXQ%gJ2=lz;i1xCjFND_xqL2C_Bu+cW_(=seUA#X5wL9SPl*tI2uTIvq+{ZWL0MsU?&@>%spmP=RhF`*;Mbr+LmYm=NXR0?-gTScuw{+giSB?1UXa05^ewu~&Q^#|ZT{CyGo^unOu@MCs<U-Lu^ltN-y714pCyiA(B1eJ`2v3HXQKn^dJkr_|ROBWF#wghhjA;#B+^e_PA8bJdTc;=^FnTt*OxhCAp6$nq?l$U&j>%p4?@So_Z48N{WR4HsHaK+1AS<VEs<@758C!zc1+!PC9Ao>ID^HKz&7_td49(y*9G0is3Rc;>lNd7xhBtJ5x3=#6@ZWf6KdjuwO8AZ$&5H0ft?a#6*)B2+0K5a)?oA=dYp<9Y*o-~;|Y0wBGywF83%4l?;Z9#T>vu0D;KSYd9xiN*x@yQiXbj}SkUki1@=hcIg)!7zHJ8z!f!7L!MV@O;a%{2)Bm9O7{!j;tAl5o~`N}cT5!d<5a^93Cqk}K5-h2w+rGW@qpi;N@wd4s2TaD91NX_v1f;Ez-ymVHHIKA79$#SHkd3sL|2TIkT8v5_q!FJI)@V5OGG-({J+HK=uq_IV=aBmkKyMxkiV^y~-m=AUZh3-XyU04>D0fAq3x>3oP!um%8VbHdef>a%vq+v9|mYB_Wv$K6zDH-|O}y3BgTx_$Dq)jKqxTI2(IsU9);A>*Rga30M)BbntPnveSD1q#|FZLAnAuV|)<y4K#|UlRa^lOXlMV?mj_%d+y)faC4PB9XRXMdx#00DaJJDSi2CTnju0JRta`Gv5m=eT~`vz`I{1HA7CH9Cq4MEcvD3*rZDKw=ssXB|tiSqv04<7LGC2*-y8+3p;?u{(##iPE0(5^~NPrbEYap)v#LSLgE`nl44SoQ`}8x2s4psn@>PqO?QbM=bms?jI>AwlR{+fhIKZcLvj>&X{7&4v>^h&!n`mYqb18v>h0Z%=NRG_Lj>Mn3qj?J$lON_@YN|d*DYMNd*k$jWH{~ApNrdaRjuOy9z{&dTLg~An;GGgb?bFZhkob#xM#d=8A6IyM*Kf+{c|Ae?VflIS&HwO-EWclSrR`?eR9Y00W*0PXF`JkEK9vUYXbis-UnphlIX%f5wuMsUP*@q$Tv}jV?atDjgE*fqX<lb7_~9%XJoJyh=V;tb?x9h4VO<6vdf^J8bOWWl3V6<5lZ7siU>5%PX(4Kt`<En%+Rfds8Be^^l%qcx$I&Hg8j<sMM!P7ZY>9jlMjFd`cpm~pa4jEn<Os{;se3`8N+iaPl$6Tfbi}M>RO6S87FsLi|8)%X%1`2+IZfZTOrnTH&EBNad*&{h|jGqo#bHgByp%v0c$mIhOa4mcCf&5*z!i4lvEtx5g<-568Fqyn=Qs|<PTNnXXAMvE}kuVh?H4=k2C~h2z4<FNsH{CKJ7=cn;-FV>ls(W5|aGv>(;U{nZ9&oJ+ZFS@ZS>KtJt2_K<c#_^U2Rh)Qbf>iPVi6-M^9B@B#TW$??LSJFek#TM_7uo!AN{kqP$ZjN)xwU00l`Tc5#gfL4pic0RwL^1C%u<p<+3urTjrJDpjIeh_3ooheq%=iwa5!+-Ti%CnX{Rp?&0aP*YMw;~*kxM>HlzrjKh#HqU&?J6XhF<H^+@wGLB)p`!qC#y(_l?krw)k??i1lN>!wbi0@nV4sUc>d~qB<%j0kz)I-3kjqkn-C_Fs6Z<e&)gbElBCQD0lSlfk8KHOp*?yqt7E0Qn--nWkug4M9rSHewLHJXmJG;{S){e29EF*EeA^ukN{nM)-i`{(qb?88P~J)r0?5nA5>U0>UJ>9K?bB7~zAEdmI4f!*#$I}sJ%H74e%_r!YZ}G%R1-by;QUQ68<u!}X!DT;k#`6qSN!u_q5AvMtbBvY?raQd`GjWyjGMb~WO>!71=<R8Z0i*ClFPj2&{P|Z%>5~nnW=pPfyr~oyG{ztHb{4NBn<L4hXd%wDPtNN%cSKi62rejRz@%cO`Am6xx7viG*G31s~dYt-3Jbg_1bGrQwj;dkEl}UCxG$!WdeAdnm8rKm#^1W6zKP>RJ6?l4RxcvZE;;-Qw+D3Bzz5fpz~PjU|U-=4J(_skp#Bf%N8(tCqAqntJ9y@0k7%~tCi!|t=!c{c;$wz>M=hm*AknRoe*S^g}LDW=L5N^^q*(^lIWF)IT08q`t?=<JY@xktM|YDNPq7<_{+@c`o!{-!SQ|Q`U^65*(S(@^y+<!wD-b<8(o}=sO%i5aI)kB)p5fDL?6#G^5PM)_#T9jXUS#sYzAWba&$rG+{i8cRXY<BRAnZZOCalI6;(Yb8Ryjqxf6N;A#W{Pc<^RfA5D6is`@yMAWn~*dLNBh%(RbiG|ayH2O`v|6Y*PWUDluXp!-<tR%vH!DiY~X0aA0**rI+ytu=Hvd;RIQuzfpwC8lN-tbIB~vIDVh08#YmriWA{GCb3xl}xONvgI7@90b=>@3_Re=CoAmD>*Z8l5S$ai@OLtySsHhSx|_eZ0Jr;doS))09-w1YS$+e#=HuJPjJQ3nziS>U-IX15Ba-&sEA<F0XYW?#q1lH-isByiY^yzE_KI0E&Bw%xBy#v5ww?+0Iny0z9IPs2Drbum#O*0y#Z&9eE2)o0d>pL_?gc{2OgcLsZCgM%>nD*U}}Sq;yAh)G2JD+BIIpvD_cE5s?!-$c52gco3CUy4zEkm$5KT|_5^IrUbpBL@`nIg*CYppR!y{hN3oL$!aXv<3QoT~YT8v-NL!1}+_Wg!`j=hjAc^L7Wv~%XOjXiO{4!}}^EY9M9g<+o#19n*+WzaY61AFbjHDiFragF*ozfgi{?UB*nACyTFrp-DYgO9azT}w-&}D+3oCmJy=4`Yyt<I(m6;S>(deC1p7-K*oQ(&f3lkdtZiHGCDLW}<;3zNXvuYZsOSc)$(%R<hwEMsfO->-`jlgq<(thvF@Un_Z^BMES0d42f00Y7Q(p$0%q^LrwR=#{MDvqbl1yoh!XTI5hQjVVgF-H^~MkK`Lgo&Rf0@2+)=W)wd6V-$#m6n3bV-_A_f84!!DQ<JhwXVH*;_f3SJ@mbpf_ani!&)5$}0_T*eia0qQod^L^PTSs8nrA)mwO&}Wbh1-Q!%<bEWyv|#F$-%l0Ge>|#}~<p0?%LY0b_RZp(1mic@%-;Ezn*#_h9^~cQ1V2;3!XfbbB9H`^PERdVFxiUS{Pav}K(w8|}WmHOv#{<InNaBX6#6cLr}`Nrx2HSLnpoB6{;P42f}vEE)>#P53}MEd#VG>roPU6J}A`G!gbThmdLM2Ez|vi7W%SRjn*6%&6BrE)sOb`zNUO#QxMjbKu~jZ+8B>qH4NEc?C<<o3vLe=^DP0&@WD3G;*gf(nG?496NNPH53u|2jp)>O!Y{*A!@WYx@^D1s9G&4xKc__$XoRZlN~ulEbF^PTl<jBY=*z?NdKU!hH~=13(?B$ZTr0xu}rqn*(|4_LN#Oi&cKGMsf4JmmH~#&;ezjFF&Dny77*G=ODPWP&ys|jwbk>V^8uw`xFJz^+UdlVP>Fp=wTiE|baF;-eb8P_{JiS#(ZB_MV*%@2K(Wu8+d7Ec$qF^qy8Q*iDfzukK!V)hVrVT&X#eMQ>iEI&v=M(6h1hfH+u#tL9c*u$%HVEgFp!cDayApoZ59i0=X=W!`g)&TEMD$yfF1vzp-PXb(-r1QtxA4;TOaS+N)}XZ)K2{fY|_0ZAlCh|Q>WAE)7+yAp80WL8&Ni(@p`1#0UU*<9?{#2p|8#ysZGCwV=V9s+EHff50i;uE}Gi??_m&Ck1tgFzIq^7V2^uu?afBU;Yg)n2YUz2ZP_H{qRG<0W9_aMBHQlh&J(59qm?cy@C?&{b%-fmFKX%n<H&d(C;!`8p+EX9N`7=qTr7%RAH~VmI_dEwi6+gYp`FWr?Lug@Lax8(u?-9Q44|ZE1?MUiw-i2vRQJe+Z2#Xo9pnjyL^n2iG7+t!CGfJM=PHpmIUccVoro4N%*rtEgY1aWol}?Prs=^XQ!2E&RI6$cgBUxHd8y(-0YwlZ!t7y#vod7==E583@6AhaYzi>%B$#f}h%pjPiwN0QyYm!zz<gwn-Qn^`JziPrj{6M8a?|jbMl?q;z8cQ3_TzC9qd=o?v2ksG>S1Emg)D<rGM1UwPIX%Q2=S}5f@=V69Q*8OS;G9($xfa+H?haJ5>1gTY67lVZbM`)*&E)q%N5`q$}1+r1Qxg1*2^fXz`O}&D(&_Ue|E{fMte$llpN3Pj#48JV-)vuOgOm4+$QG{E|LV^?Gkg}(kva&9n&6?{AfpyJ$jLvulS90;B>t$@<Gdua&l7+@IAd3z@>;vqH=Sx6;_pi(F|EDu<FqdN_}PO3bKGnKMa)_m^ahf*a@T<EQCwFPtc_8-$Q07w(nn7cP4VeE(KA6d;p)2e_-BhV4Lum_5<`^nw3LiZOLa1mm`+=?1<U~HKv%GZi+y<jYG15XHf5kC01VSBbwj&6P8Km8diADvxPL}jD5vN$zn;%=zJ%9@W}yzSFI9LBa0*c_M!c~MAFqnZ{OKHpD|oZoXW&_2$pRA^wCJ6xNwdXrA#5`L#+q2z4xc?i;9PqXy&ji>S{`wM@e04ha6cG@XQJBW$`N6zdy*AM4kJaqYg%IGRVRX47k5*L%Q?`UkdEmt<89DZ+gRs?(7JV2qfu#aqhL<e~a=Jvn7Kna49I%To1coBy>xVP=n5uN}q>=tS9X(tgWhW8cv*_mt%NY?3sw}NR@q1=QZSJ@`xu2mVC6J2G+B&4g3FE2!bqnV;n&x_|T#hf~HL*O_>yhhpB`QmWy~oElY;8Rir88wJWv?Z4k@+_4~GX5RokGyq>+BuXZH%0|~5dNp6zKKE_yj?=Ot;yR9+^$n~M=*vtADyq6nYY4CD60=<JJ|Azh{t%TsMpn4ZIL2U8>286Q^_pm&1PG=^=p%bvs5N3C3cPdr(U2x<(f5MkEqa~KNp(ZHa#17@nluE90vZJ>g&~6O*et|?lCmdScM+bp~9rCQ2!o*}Y+iO9-@n^&2&BC{@j!FGKAbNA=(=g+83ja?fbz_?vnUCIA7t0rvDh<LO))%9w2Cb}ho_CT<PpBocvztA{s*ORgB0oKfwPyP9dsfFC@IW3{<!nxkO6{qK&gHkoLv~rCucbOb+WxGY3hzM~m_}x3V`xM8?RpN--$wIWXJM<HY6s2KrK*xgxBcBjE~t{$S0zkvzAXi(?Hega4elz*0kR#Mo;Lrvgmdb1<H4iE@nM*;D{<A0G{zx(Dc60!L#0loJ(t0B&lwTapFSWz)M!8_4=Cku_{<nsYEz0398E=>g9{tCcm>Yso=~z#r~h3TrZ*rnMoGVUw(lmiZ=dE1K@OaN&G|f@4Xp+~8s*tqH}q2HTbCX{d^3dmXeiNF15~PP$iP#>CN_Eztea+ZUFO(J`-Zq*3Pc5;gkzvkG^69+!?}{Hh&E7JLS9HLi`5xA2x!EpAw@4yIk}l8>WNXB{HGs2b?CT+RE5Fi)X1h)NDr#%_o03$Ak|H7Yd~|`-e-o#v~P+s;ps#>#cYYU<OCzc3gCE=Tjt`)SyQ+0csoTN&6h<_Tc7$7&rS?Ybr&7vx1JFK@O$4r)S6NWenlq;=L?EtnzSQDOk!XeW(vcK(G@!9)P*mL`rrTn2OaA3HOO@<00GZQnbQFPf>x9uvBYQl0ssI200dcD')).decode()
_gc=lambda s:tuple(int(x.strip().rstrip("u"),0)for x in GEN_C.split(s+"={")[1].split("}")[0].split(","))
IV,K,PERM,PREFIX_WORDS,UCD=_gc("IV[8]"),_gc("K[RND]"),_gc("PERM[8]"),_gc("PW[8]"),_gc("UCD[96]")
PAD2=bytes([128])+bytes(55)+(512).to_bytes(8,"big")
_fn=lambda*xs:(x if callable(x)else x.__getitem__ for x in xs)
def _ror(v,k):return((v>>k)|(v<<(32-k)))&M32
def words_of(x):return[(x>>(32*(7-i)))&M32 for i in range(8)]
def int_of(w):return sum(w[i]<<(32*(7-i))for i in range(8))
def _SIG0(a):return _ror(a,2)^_ror(a,13)^_ror(a,22)
def _SIG1(e):return _ror(e,6)^_ror(e,11)^_ror(e,25)
def _CH(e,f,g):return(e&f)^(~e&g)
def _MAJ(a,b,c):return(a&b)^(a&c)^(b&c)
def _exp40(ws):
	ws=list(ws)
	for i in range(16,ROUNDS):x,y=ws[i- 15],ws[i- 2];ws.append((ws[i- 16]+(_ror(x,7)^_ror(x,18)^(x>>3))+ws[i- 7]+(_ror(y,17)^_ror(y,19)^(y>>10)))&M32)
	return ws
TAILB=1
CIN=1
NTAIL=6 if TAILB else 4
QM,XM=0x74a40866,0x46eb57e6
PRE,VARBASE,TAILMAP,OFFSET=8,8,{},set(range(10,16))
def _build_ws(w,prefix=None):
	prefix=PREFIX_WORDS if prefix is None else prefix;ws=list(prefix[:PRE])+[0]*(16-PRE)
	for k in range(8):ws[VARBASE+k]=(w[k]-(K[VARBASE+k]if VARBASE+k in OFFSET else 0))&M32
	for pos,v in TAILMAP.items():ws[pos]=v
	return ws
def _trace(w,prefix=None):
	ws=_exp40(_build_ws(w,prefix));a,b,c,d,e,f,g,h=IV;A,E,T={0:a,- 1:b,- 2:c,- 3:d},{0:e,- 1:f,- 2:g,- 3:h},{}
	for i in range(ROUNDS):t1=(h+_SIG1(e)+_CH(e,f,g)+K[i]+ws[i])&M32;t2=(_SIG0(a)+_MAJ(a,b,c))&M32;a,b,c,d,e,f,g,h=(t1+t2)&M32,a,b,c,(d+t1)&M32,e,f,g;A[i+1],E[i+1],T[i+1]=a,e,t1
	return ws,A,E,T
def state_words(w,prefix=None):_,A,E,_=_trace(w,prefix);r=ROUNDS;return[A[r],A[r- 1],A[r- 2],A[r- 3],E[r],E[r- 1],E[r- 2],E[r- 3]]
def enc_words(w,prefix=None):ws,A,E,T=_trace(w,prefix);r=ROUNDS;bw=[E[r- 3],E[r- 2],A[r- 7],A[r- 6],(T[r- 5]+_CH(A[r- 6]^A[r- 7],A[r- 8],QM))&M32,T[r- 4],(E[r- 5]+_CH(E[r- 2],XM,E[r- 4])+ws[r- 2])&M32,(E[r- 4]+ws[r- 1])&M32];return[bw[PERM[k]]for k in range(8)]
def enc_invert(enc):
	r,bw=ROUNDS,[0]*8
	for k in range(8):bw[PERM[k]]=enc[k]
	e3,e2,a7,a6,Q,T4,X,Y=bw;a5=(Q+(a6&a7&~QM)-(~a6&~a7&QM)+_SIG0(a6))&M32;a4=(T4+_SIG0(a5)+_MAJ(a5,a6,a7))&M32;a3=(e3-a7+_SIG0(a4)+_MAJ(a4,a5,a6))&M32;a2=(e2-a6+_SIG0(a3)+_MAJ(a3,a4,a5))&M32;t1=(X+(e2&e3&~XM)-(e2&~e3&XM)+_SIG1(e2)+K[r- 2])&M32;e1=(a5+t1)&M32;a1=(t1+_SIG0(a2)+_MAJ(a2,a3,a4))&M32;t0=(Y+_SIG1(e1)+_CH(e1,e2,e3)+K[r- 1])&M32;return[(t0+_SIG0(a1)+_MAJ(a1,a2,a3))&M32,a1,a2,a3,(a4+t0)&M32,e1,e2,e3]
def f_scalar(x,n=256):return int_of(enc_words(words_of(x)))&((1<<n)- 1)
PAD2W=tuple(int.from_bytes(PAD2[4*i:4*i+4],"big")for i in range(16))
_KW2=tuple((K[i]+w)&M32 for i,w in enumerate(_exp40(PAD2W)))
def digest_of_state(s):
	cv=[(u+v)&M32 for u,v in zip(IV,s)];a,b,c,d,e,f,g,h=cv
	for kw in _KW2:t1=(h+_SIG1(e)+_CH(e,f,g)+kw)&M32;t2=(_SIG0(a)+_MAJ(a,b,c))&M32;a,b,c,d,e,f,g,h=(t1+t2)&M32,a,b,c,(d+t1)&M32,e,f,g
	return int_of([(u+v)&M32 for u,v in zip(cv,[a,b,c,d,e,f,g,h])])
def digest_of_g(o,qint):return digest_of_state(enc_invert(words_of(o^qint)))
def message(x):return b"".join(v.to_bytes(4,"big")for v in _build_ws(words_of(x)))
RP,RMASK=128,M32|(M32<<128)
WM,KM=0,30
def _rep(v):return v|(v<<RP)
class RecProg:
	def __init__(self):
		n=ROUNDS;self.imm,self.init=[],[];MASK,T0,T1,T2,T3,T4=0,11,12,13,14,15;ST,PB=list(range(1,9)),[9,10];W0,W1,W2,W3,WC0,WC1,WC2,WC3,E0,E1,WN=19,20,21,22,24,25,26,27,28,29,30
		def S(out,x,v):self.imm.append(v);out.append(("S",x,len(self.imm)- 1,0))
		S(self.init,MASK,RMASK);S(self.init,38,_rep(PREFIX_WORDS[0]))
		for i in range(10,n- 6):S(self.init,T0,_rep(K[i]));self.init.append(("T",KM+i,T0,2))
		constpos={i:PREFIX_WORDS[i]for i in range(1,PRE)};constpos.update(TAILMAP)
		for i in sorted(constpos):S(self.init,T0,_rep(constpos[i]));self.init.append(("T",WM+i,T0,2))
		hregs=[32,33,34,35,36,37]
		for j,k in enumerate(range(2,8)):S(self.init,hregs[j],_rep((-K[VARBASE+k])&M32))
		for rk,vk in zip((13,14,16,18,23,29),(K[n- 6],K[n- 5],K[n- 4],K[n- 3],XM,QM)):S(self.init,rk,_rep(vk))
		def sigma(out,dst,src,rs,shr,mask=True,dup=True):
			if dup:out+=[("<",T0,src,32),("|",T0,src,T0)]
			out+=[(">",dst,T0,rs[0]),(">",T1,T0,rs[1]),("^",dst,dst,T1)];out+=[(">",T1,src,shr)if shr else(">",T1,T0,rs[2]),("^",dst,dst,T1)]
			if mask:out.append(("&",dst,dst,MASK))
		def rnd(out,st,pi,wreg,addrk):a,b,c,d,e,f,g,h=st;P,PN=PB[pi],PB[1-pi];sigma(out,E0,e,(6,11,25),0,False);out+=[("^",T1,f,g),("&",T1,e,T1),("^",T1,g,T1)];out+=[("L",T0,addrk+KM,0),("+",E0,h,E0),("+",E0,E0,T1),("+",E0,E0,wreg),("+",E0,E0,T0)];sigma(out,h,a,(2,13,22),0,True);out+=[("^",PN,a,b),("&",T0,PN,P),("^",T0,T0,b),("+",T1,h,T0)];out+=[("+",h,d,E0),("&",h,h,MASK),("+",d,E0,T1),("&",d,d,MASK)];return[d,a,b,c,h,e,f,g],1-pi
		assert WM==0;body=[];st,pi=list(ST),0;stl,pil=list(st),pi
		for j,wr in enumerate((WC0,WC1,W0,W1)):stl,pil=rnd(body,stl,pil,wr,10+j)
		assert stl==st and pil==pi,"the round loop does not rename back";body+=[("L",WN,4,0)];sigma(body,E0,WN,(7,18,0),3,True);body+=[("+",WC2,W0,E0),("L",W0,1,0)];sigma(body,E0,W0,(7,18,0),3,True);body+=[("+",E0,WC3,E0),("+",WC3,WN,W1),("+",W1,W0,WC0)];sigma(body,W0,W2,(17,19,0),10,False);body+=[("+",W0,W0,E0),("&",W0,W0,MASK),("T",16,W0,0),("|",WC0,W2,W2),("L",W2,2,0)];sigma(body,E0,W2,(7,18,0),3,True);body+=[("+",W1,W1,E0),("+",W2,W2,WC1)];sigma(body,E0,W3,(17,19,0),10,False);body+=[("+",W1,W1,E0),("&",W1,W1,MASK),("T",17,W1,0),("|",WC1,W3,W3),("L",W3,3,0)];sigma(body,E0,W3,(7,18,0),3,True);body+=[("+",W2,W2,E0),("+",W3,W3,WC2)];sigma(body,E0,W0,(17,19,0),10,False);body+=[("+",W2,W2,E0),("&",W2,W2,MASK),("T",18,W2,0)];sigma(body,E0,W1,(17,19,0),10,False);body+=[("+",W3,W3,E0),("&",W3,W3,MASK),("T",19,W3,0)];ra,rb,rc,rd,re,rf,rg,rh=st
		def t1(out,dst,hr,er,fr,gr,wi,wreg,kreg):
			sigma(out,E0,er,(6,11,25),0,False);out+=[("^",T1,fr,gr),("&",T1,er,T1),("^",T1,gr,T1)]
			if wreg is None:out.append(("L",T0,WM+wi,2));wreg=T0
			out+=[("+",E0,hr,E0),("+",E0,E0,T1),("+",E0,E0,wreg),("+",dst,E0,kreg)]
		tail=[]
		if TAILB:R5,QQ,E5,R4,E4,E3,E2,XX,YY=8,17,4,24,25,26,WC3,PB[0],31;t1(tail,R5,rh,re,rf,rg,n- 6,WC0,13);tail+=[("+",E5,rd,R5),("&",E5,E5,MASK)];t1(tail,R4,rg,E5,re,rf,n- 5,WC1,14);tail+=[("+",E4,rc,R4),("&",E4,E4,MASK)];t1(tail,E0,rf,E4,E5,re,n- 4,W0,16);tail+=[("+",E3,rb,E0),("&",E3,E3,MASK)];t1(tail,E0,re,E3,E4,E5,n- 3,W1,18);tail+=[("+",E2,ra,E0)];tail+=[("^",T1,E4,23),("&",T1,E2,T1),("^",T1,E4,T1),("+",XX,E5,T1),("+",XX,XX,W2)];tail+=[("+",YY,E4,W3)];tail+=[("^",T0,ra,rb),("^",E0,rc,29),("&",T0,T0,E0),("^",T0,29,T0),("+",QQ,R5,T0)];fb=[E3,E2,rb,ra,QQ,R4,XX,YY];self.fin=[fb[PERM[k]]for k in range(8)]
		head=[];wregs=(WC0,WC1,W0,W1,W2,W3)
		for k in range(7,- 1,- 1):
			if VARBASE+k in OFFSET:dst_reg=wregs[k- 2];head+=[("+",dst_reg,self.fin[k],hregs[k- 2]),("&",dst_reg,dst_reg,MASK)];head.append(("T",WM+VARBASE+k,dst_reg,2))
			else:head.append(("T",WM+VARBASE+k,self.fin[k],2))
		y0,y1=self.fin[0],self.fin[1];sigma(head,ST[4],y0,(6,11,25),0,False,dup=True);head+=[("+",ST[4],ST[4],y1),("&",ST[4],ST[4],MASK),("+",WC3,y1,38)];sigma(head,ST[0],y0,(2,13,22),0,False,dup=False);head+=[("+",ST[0],ST[0],ST[4]),("&",ST[0],ST[0],MASK)];head+=[("|",ST[1],y0,ST[2]),("|",ST[5],y0,ST[2])];self.blocks=[("S",head),("L",body,0,n- 16,4),("S",tail)];self.flat=[]
		for blk in self.blocks:
			if blk[0]=="S":self.flat+=blk[1]
			else:_,bd,start,count,stepw=blk;self.flat+=[("R",0,start,0),("R",1,start+count,0)];top=len(self.flat);self.flat+=bd+[("A",0,stepw,0),("C",0,1,0),("J",top,0,0)]
		self.instr=len(self.init)+len(self.flat);self.mem,self.regs=[0]*64,[0]*39;self.run(self.init);self.mem0,self.regs0=list(self.mem),list(self.regs);self.ops=self.run(self.flat)
	def run(self,recs):
		r,mem,p,flag,pc,cnt=self.regs,self.mem,[0,0,0],False,0,0
		while pc<len(recs):
			op,x,y,z=recs[pc];pc+=1;cnt+=1
			if op=="^":r[x]=r[y]^r[z]
			elif op=="&":r[x]=r[y]&r[z]
			elif op=="|":r[x]=r[y]|r[z]
			elif op=="+":r[x]=(r[y]+r[z])&ALL
			elif op==">":r[x]=r[y]>>z
			elif op=="<":r[x]=(r[y]<<z)&ALL
			elif op=="S":(mem if z else r)[x]=self.imm[y]
			elif op=="L":r[x]=mem[p[z]+y]
			elif op=="T":mem[p[z]+x]=r[y]
			elif op=="R":p[x]=y
			elif op=="A":p[x]+=y
			elif op=="C":flag=p[x]<p[y]
			elif op=="J"and flag:pc=x
		return cnt
	def f(self,xs,fast=True):
		if fast:return[f_scalar(x)for x in xs]

		for i in(3,4,7,8):self.regs[i]=0
		for k in range(8):self.regs[self.fin[k]]=sum(((x>>(32*(7-k)))&M32)<<(RP*l)for l,x in enumerate(xs))
		self.run(self.flat);return[sum(((self.regs[self.fin[k]]>>(RP*l))&M32)<<(32*(7-k))for k in range(8))for l in range(len(xs))]
_REC=[]
def rec():
	if not _REC:_REC.append(RecProg())
	return _REC[0]
def packed_f(xs,n,qw=None):q=sum(qw[i]<<(32*i)for i in range(8))if qw else 0;return[(v^q)&((1<<n)- 1)for v in rec().f(xs)]
def packed_ops(qw=None):return rec().ops
ZERO,ONE=(0,0),(0,1)
_ADD_HINTS=(0,)*56
EXPECTED_EMITTER_INFO=(43541,884,43798,174430,0,0,34096,5866,3579,174164,16384,43836,28928,56,640)
STATIC_SLP_SHA256="cff4d5fb7f9293ddec010dc88c4923fe4b136040aa6a342692035210318be3ce"
STATIC_C_SHA256="0838d00e6b24114617a61f90592b5f0b7232bc986d8106e345f5270e620672fa"
STATIC_WASM_SHA256="cf47b49441572ac2a150ea2ff942212d4446d65e93163cffcb6e806c9cf62d8b"
POLARITY_Q=int("e7309a100cc5bf67eea64df025e3b2545785e20fdeb3df8208948c9c227bb195",16)
class Gen:
	def __init__(self,n):
		self.n,self.nodes,self.calls=n,[("c",)],0;self.ahi=0;self.inputs,self.cse=[],{}
		for j in range(n):self.nodes.append(("v",j));self.inputs.append((len(self.nodes)-1,0))
	def mk(self,op,a,b):
		self.calls+=1
		if a>b:a,b=b,a
		k=self.cse.get((op,a,b))
		if k is None:self.nodes.append((op,a,b));k=self.cse[(op,a,b)]=len(self.nodes)-1
		return k
	def _gate(self,node):
		if node<=self.n or node<len(self.nodes)-8:return None
		g=self.nodes[node];return g if g[0]in("x","a","o")else None
	def XOR(self,x,y):
		self.calls+=1
		if x[0]==0:return(y[0],y[1]^x[1])
		if y[0]==0:return(x[0],x[1]^y[1])
		if x[0]==y[0]:return(0,x[1]^y[1])
		gx,gy=self._gate(x[0]),self._gate(y[0]);inv=x[1]^y[1]
		if gx and gx[0]=="x"and y[0]in gx[1:]:return(gx[2]if gx[1]==y[0]else gx[1],inv)
		if gy and gy[0]=="x"and x[0]in gy[1:]:return(gy[2]if gy[1]==x[0]else gy[1],inv)
		if gx and gy and gx[0]==gy[0]=="x":
			cm=set(gx[1:])&set(gy[1:])
			if cm:c= min(cm);r=self.XOR((gx[2]if gx[1]==c else gx[1],0),(gy[2]if gy[1]==c else gy[1],0));return(r[0],r[1]^inv)
		return(self.mk("x",x[0],y[0]),x[1]^y[1])
	def AND(self,x,y):
		self.calls+=1
		if x[0]==0:return ZERO if x[1]==0 else y
		if y[0]==0:return ZERO if y[1]==0 else x
		if x[0]==y[0]:return x if x[1]==y[1]else ZERO
		if x[1]==0 and y[1]==0:return(self.mk("a",x[0],y[0]),0)
		if x[1]==1 and y[1]==1:return(self.mk("o",x[0],y[0]),1)
		p,q=(x,y)if x[1]==0 else(y,x);return self.XOR(p,(self.mk("a",p[0],q[0]),0))
	def fa(self,a,b,c):
		ops=(a,b,c);cs=[t for t in ops if t[0]==0];vs=[t for t in ops if t[0]!=0];k=0
		for t in cs:k^=t[1]
		if len(vs)==3:
			for pi in range(3):
				o=[vs[j]for j in range(3)if j!=pi]
				if o[0][1]==o[1][1]:p,x,y=vs[pi],o[0],o[1];break
			u=self.XOR(x,p);return self.XOR(u,y),self.XOR(self.AND(u,self.XOR(y,p)),p)
		if len(vs)==2:
			x,y=vs;t=self.XOR(x,y);s=(t[0],t[1]^k)
			if x[1]==y[1]:
				if k==0:return s,self.AND(x,y)
				cr=self.AND((x[0],x[1]^1),(y[0],y[1]^1));return s,(cr[0],cr[1]^1)
			nt=(t[0],t[1]^1);xx=x if x[1]==nt[1]else y
			if k==0:return s,self.AND(xx,nt)
			xx=x if x[1]==t[1]else y;cr=self.AND((xx[0],xx[1]^1),(t[0],t[1]^1));return s,(cr[0],cr[1]^1)
		if len(vs)==1:x=vs[0];k1,k2=cs[0][1],cs[1][1];return(x[0],x[1]^k),(ONE if k1==k2==1 else ZERO if k1==k2==0 else x)
		kk=cs[0][1]+cs[1][1]+cs[2][1];return(ZERO if kk%2==0 else ONE),(ONE if kk>=2 else ZERO)
	def add(self,A,B,cin=ZERO):
		a,b=_fn(A,B);s,c=[],cin
		for i in range(32):
			if i==31:s.append(self.XOR(self.XOR(a(i),b(i)),c))
			else:si,c=self.fa(a(i),b(i),c);s.append(si)
		return s
	def OR(self,x,y):r=self.AND((x[0],x[1]^1),(y[0],y[1]^1));return(r[0],r[1]^1)
	def _col(self,t,u,U,oU,rev=False):
		X,A,O,pt=self.XOR,self.AND,self.OR,U[1]^u[1]
		if t[0][1]==t[1][1]==t[2][1]:(x,y,z),tm=t,(1 if t[0][1]==pt else 2)
		else:
			for zi in((2,1,0)if rev else(0,1,2)):
				if t[zi][1]==pt:r0,r1=[t[j]for j in range(3)if j!=zi];(x,y,z),tm=((r1,r0,t[zi]),0)if r0[1]!=u[1]else((r0,r1,t[zi]),0)if r1[1]!=u[1]else((r0,t[zi],r1),1);break
		if tm==1:w=X(y,U);n8=X(z,w);s=X(x,n8);n6=O(U,X(y,u));return s,(ZERO if oU else X(n6,w)),X(n6,A(n8,X(x,w)))
		if tm==2:w5=X(x,y);w6=X(z,w5);s=X(U,w6);w9=X(u,w6);w10=O(U,(w9[0],w9[1]^1));w11=O(w5,X(x,z));return s,(ZERO if oU else X(w6,(w10[0],w10[1]^1))),X(w10,(w11[0],w11[1]^1))
		n5=X(z,U);n9=X(x,n5);s=X(y,n9);n6=X(x,y);n8=O(U,X(z,u));n11=A((n6[0],n6[1]^1),n9);return s,(ZERO if oU else X(n5,n11)),X(n8,n11)
	def add3(self,A,B,C,cin=0,d0=None,h0=None,u0=None):
		a,b,c=_fn(A,B,C);s=[None]*32
		if h0 is not None:
			sw0,u=self.fa(b(0),c(0),ONE if cin else ZERO);s[0]=self.XOR(u0,sw0);w=self.XOR(h0,sw0)
			if u0[0]and w[0]and u0[0]!=w[0]and u0[1]!=w[1]:cm=self.XOR(self.AND((u0[0],u0[1]^1),w),sw0)
			else:cm=self.XOR(self.AND(u0,w),h0)
			U=self.XOR(u,cm)
		elif cin==0:
			s[0],U=self.fa(a(0),b(0),c(0))
			if d0 is not None:s[0],u=self.fa(s[0],d0,ZERO);U=self.XOR(U,u)
			else:u=ZERO
		elif cin==2:s[0],c0=self.fa(a(0),b(0),c(0));u,U=ONE,(c0[0],c0[1]^1)
		else:
			ops=(a(0),b(0),c(0))
			for pi in range(3):
				o=[ops[j]for j in range(3)if j!=pi]
				if o[0][1]==o[1][1]:p,x,y=ops[pi],o[0],o[1];break
			u0=self.XOR(x,p);s[0]=self.XOR(u0,(y[0],y[1]^1));u,U=p,self.OR(u0,self.XOR(y,p))
		for i in range(1,31):s[i],u,U=self._col((a(i),b(i),c(i)),u,U,i==30)
		s[31]=self.XOR(self.XOR(self.XOR(a(31),b(31)),c(31)),U);return s
	def add2c(self,A,B,cv):
		a,b=_fn(A,B);cin=1 if _tz((cv-1)&M32)>_tz(cv)else 0;cv2=(cv-cin)&M32
		if not cv2:return self.add(a,b,ONE if cin else ZERO)
		k,s,c=_tz(cv2),[None]*32,ONE if cin else ZERO
		for i in range(k):s[i],c=self.fa(a(i),b(i),c)
		if k==31:s[31]=self.XOR(self.XOR(a(31),b(31)),(c[0],c[1]^1));return s
		ops=(a(k),b(k),c)
		for pi in range(3):
			o=[ops[j]for j in range(3)if j!=pi]
			if o[0][1]==o[1][1]:p,x,y=ops[pi],o[0],o[1];break
		u0=self.XOR(x,p);s[k]=self.XOR(u0,(y[0],y[1]^1));u,U,C=p,self.OR(u0,self.XOR(y,p)),_constw(cv2)
		for i in range(k+1,31):s[i],u,U=self._col((C[i],a(i),b(i)),u,U,i==30,True)
		s[31]=self.XOR(self.XOR(self.XOR(a(31),b(31)),C[31]),U);return s
	def _baseline(self,cv,vs,fb=None,cid=None):
		if len(vs)==2 and cv and fb is None:
			if cid in(20,23,24,27):return self.add2c(vs[0],vs[1],cv)
			if cid in(16,18,22):
				rem=((-K[17])&M32)if cid==18 else((4-K[19])&M32)if cid==22 else((6-PREFIX_WORDS[7]-K[23])&M32);s=self.add2c(vs[0],vs[1],(cv-rem)&M32);out=self.add(s,_constw(rem));sp=getattr(self,"split",None)
				if sp is not None:sp[tuple(out)]=(s,rem)
				return out
		bb=fb if fb is not None else(max(range(len(vs)),key=lambda k:(_tz((cv-k)&M32),-k))if CIN and cv else 0)
		if len(vs)==4 and bb==0 and not cv:A,B,D,C=vs;s=self.add3(A,B,C,0,D[0]);return self.add(s,[ZERO]+D[1:])
		ub=0
		while len(vs)>2:c3=min(bb-ub,2);ub+=c3;vs=[self.add3(*vs[:3],c3)]+vs[3:]
		s=vs[0]
		for w in vs[1:]:c1=1 if ub<bb else 0;ub+=c1;s=self.add(s,w,ONE if c1 else ZERO)
		cv=(cv-ub)&M32
		if cv:
			out=self.add(s,_constw(cv));sp=getattr(self,"split",None)
			if sp is not None:sp[tuple(out)]=(s,cv)
			return out
		return s
	def _choice(self,op,mask):
		pick=[op[i]for i in range(len(op))if(mask>>i)&1];rest=[op[i]for i in range(len(op))if not((mask>>i)&1)];first=self.add3(*pick)
		if not rest:return first
		if len(rest)==1:return self.add(first,rest[0])
		if len(rest)==2:return self.add3(first,*rest)
		assert 0
	def addm(self,*ws,force_bb=None):
		cv,vs=0,[]
		for w in ws:
			if all(x[0]==0 for x in w):cv+=sum(x[1]<<i for i,x in enumerate(w))
			else:vs.append(w)
		cv&=M32
		if not vs:return _constw(cv)
		cid=self.ahi;self.ahi+=1;hint=_ADD_HINTS[cid]
		if hint and force_bb is None:op=list(vs)+([_constw(cv)]if cv else[]);assert hint<(1<<len(op))and hint.bit_count()==3;return self._choice(op,hint)
		return self._baseline(cv,list(vs),force_bb,cid)
	def xorw(self,A,B):return[self.XOR(a,b)for a,b in zip(A,B)]
def _tz(v):return 32 if v==0 else(v&-v).bit_length()-1
def _constw(v):return[ONE if(v>>i)&1 else ZERO for i in range(32)]
def _sigb(g,A,r1,r2,r3,shift,j):return g.XOR(g.XOR(A[(j+r1)%32],A[(j+r2)%32]),(A[j+r3]if j+r3<32 else ZERO)if shift else A[(j+r3)%32])
def _sigma(g,A,r1,r2,r3,shift):return[_sigb(g,A,r1,r2,r3,shift,j)for j in range(32)]
def _add_u(g,A,u,c1=0,ch1=None):
	s=[None]
	if ch1 is not None:s1,c=g.fa(A[1],ch1,ONE if c1 else ZERO);s.append(s1)
	elif c1:s.append((u[1][0],u[1][1]^1));c=g.OR(A[1],u[1])
	else:s.append(u[1]);c=g.AND(A[1],(u[1][0],u[1][1]^1))
	for i in range(2,31):
		s.append(g.XOR(u[i],c));w=g.XOR(A[i],c)
		if u[i][0]and w[0]and u[i][0]!=w[0]and u[i][1]!=w[1]:c=g.XOR(g.AND((u[i][0],u[i][1]^1),w),c)
		else:c=g.XOR(g.AND(u[i],w),A[i])
	s.append(g.XOR(u[31],c));return s
def _col_uc(g,hw,ui,u,U,cb,ch,oU):
	idx=(cb<<4)|hw[1]|(ui[1]<<1)|(u[1]<<2)|(U[1]<<3);code=UCD[64+idx]if oU else UCD[2*idx+ch]
	if not code:w6=(ui[0],ui[1]^cb);s=g.XOR(U,w6);w9=g.XOR(u,w6);w10=g.OR(U,(w9[0],w9[1]^1));w11=g.OR(ui,(hw[0],hw[1]^cb));return s,(ZERO if oU else g.XOR(w6,(w10[0],w10[1]^1))),g.XOR(w10,(w11[0],w11[1]^1))
	ops=("x","a","o");sr=g.mk("x",ui[0],U[0]);rs=[hw[0],ui[0],u[0],U[0],sr]if oU and((code>>26)&1)else[ui[0],u[0],U[0],sr,g.mk("a"if ui[1]else "o",hw[0],ui[0])]
	for q in range(3):c=(code>>(8*q))&255;rs.append(g.mk(ops[c&3],rs[(c>>2)&7],rs[c>>5]))
	a3=(code>>24)&3;Ur=g.mk("x",rs[4+a3],rs[7])if a3<3 else rs[7];return(sr,ui[1]^U[1]^cb),(ZERO if oU else(rs[4+((code>>26)&3)],(code>>28)&1)),(Ur,(code>>29)&1)
def _adduc(g,A,u,cv,c1=0,ch1=None):
	if not cv:return _add_u(g,A,u,c1,ch1),0
	k=_tz(cv)
	if k<=1 or k>=31:return _add_u(g,A,u,c1,ch1),cv
	dc,dh=[[[0,0],[0,0]]for _ in range(31)],[[[0,0],[0,0]]for _ in range(31)];cb30=(cv>>30)&1
	for pu in(0,1):
		for pU in(0,1):code=UCD[64+((cb30<<4)|A[30][1]|(u[30][1]<<1)|(pu<<2)|(pU<<3))];dc[30][pu][pU]=(5+((code>>27)&1))if code else 6
	for i in range(29,k,-1):
		cb=(cv>>i)&1
		for pu in(0,1):
			for pU in(0,1):
				idx=(cb<<4)|A[i][1]|(u[i][1]<<1)|(pu<<2)|(pU<<3)
				if not UCD[2*idx]:dc[i][pu][pU]=7+dc[i+1][cb][0]
				else:
					bc,bch=999,0
					for ch in(0,1):
						code=UCD[2*idx+ch]
						if code:
							tc=6+dc[i+1][(code>>28)&1][(code>>29)&1]
							if tc<bc:bc,bch=tc,ch
					dc[i][pu][pU],dh[i][pu][pU]=bc,bch
	out=[None]*32
	if ch1 is not None:out[1],c=g.fa(A[1],ch1,ONE if c1 else ZERO)
	elif c1:out[1],c=(u[1][0],u[1][1]^1),g.OR(A[1],u[1])
	else:out[1],c=u[1],g.AND(A[1],(u[1][0],u[1][1]^1))
	for i in range(2,k):
		out[i]=g.XOR(u[i],c);w=g.XOR(A[i],c)
		if u[i][0]and w[0]and u[i][0]!=w[0]and u[i][1]!=w[1]:c=g.XOR(g.AND((u[i][0],u[i][1]^1),w),c)
		else:c=g.XOR(g.AND(u[i],w),A[i])
	pw=A[k][1]^c[1];cck=3 if u[k][1]==pw else 4;pUk=0 if(u[k][1]==0 and pw==0)else 1;cmk=cck+(1 if k==30 else min(dc[k+1][A[k][1]][pUk],dc[k+1][c[1]][pUk])+1);base=6*(31-k);pcu,pcc=c[1],0;bm,bc=(k,cmk)if cmk<base else(31,base)
	for i in range(k,30):
		pti,pwi=u[i][1]^pcu,A[i][1]^pcu;pcun=(pwi^pcu)if u[i][1]!=pwi else(u[i][1]^A[i][1]);cb=(cv>>i)&1;pccn=pti if i==k else(pti if pti==pcc else cb);pcu,pcc=pcun,pccn;m,pUm=i+1,pcu^pcc;cm=6*(m-k)+min(dc[m][pcu][pUm],dc[m][pcc][pUm])
		if cm<bc:bc,bm=cm,m
	if bm==31:
		for i in range(k,31):
			out[i]=g.XOR(u[i],c);w=g.XOR(A[i],c)
			if u[i][0]and w[0]and u[i][0]!=w[0]and u[i][1]!=w[1]:c=g.XOR(g.AND((u[i][0],u[i][1]^1),w),c)
			else:c=g.XOR(g.AND(u[i],w),A[i])
		out[31]=g.XOR(u[31],c);return out,cv
	if bm==k:s0=g.XOR(u[k],c);out[k]=(s0[0],s0[1]^1);Ucs=g.OR(u[k],g.XOR(A[k],c));ucs=(A[k]if dc[k+1][A[k][1]][Ucs[1]]<=dc[k+1][c[1]][Ucs[1]]else c)if k<30 else ZERO;sc=k+1
	else:
		cu,cc,cw=c,ZERO,_constw(cv)
		for i in range(k,bm):
			ti=g.XOR(u[i],cu);w=g.XOR(A[i],cu)
			if u[i][0]and w[0]and u[i][0]!=w[0]and u[i][1]!=w[1]:cu=g.XOR(g.AND((u[i][0],u[i][1]^1),w),cu)
			else:cu=g.XOR(g.AND(u[i],w),A[i])
			out[i],cc=g.fa(ti,cw[i],cc)
		Ucs=g.XOR(cu,cc);ucs=cu if dc[bm][cu[1]][Ucs[1]]<=dc[bm][cc[1]][Ucs[1]]else cc;sc=bm
	for i in range(sc,31):cb=(cv>>i)&1;ch=0 if i==30 else dh[i][ucs[1]][Ucs[1]];out[i],ucs,Ucs=_col_uc(g,A[i],u[i],ucs,Ucs,cb,ch,i==30)
	s31=g.XOR(u[31],Ucs);out[31]=(s31[0],s31[1]^((cv>>31)&1));return out,0
def _t1hg(g,e,f,gg,h,hg,Wd,d=None):
	sp=getattr(g,"split",{});fg=[g.XOR(f[j],gg[j])for j in range(32)];hh=any(x[0]!=0 for x in h);ch1=g.XOR(f[1],g.AND((e[1][0],e[1][1]^1),fg[1]))if(hh and e[1][0]and fg[1][0]and e[1][1]!=fg[1][1])else None;u=[None if(j==1 and ch1 is not None)else g.XOR(hg[j],g.AND(e[j],fg[j]))for j in range(32)];s1=lambda j:_sigb(g,e,6,11,25,False,j);cv,vs=0,[s1]
	for w in Wd:
		if all(x[0]==0 for x in w):cv+=sum(x[1]<<i for i,x in enumerate(w))
		else:vs.append(w)
	cv&=M32;hd=d is not None and any(x[0]!=0 for x in d)
	if hh and len(vs)==2:
		if not cv:t=_add_u(g,h,u,0,ch1);return g.add3(t,vs[0],vs[1],0,None,h[0],u[0]),fg,0
		p1=None if ch1 is not None else(1 if(h[1][0]and u[1][0]and h[1][1]==u[1][1])else 0);cands=[(vs[1],cv)]
		if tuple(vs[1])in sp:sr,cr=sp[tuple(vs[1])];cands.append((sr,(cv+cr)&M32))
		best=None
		for wc,cc in cands:
			for c0 in(0,1):
				for c1 in(0,1):
					for d_ in((0,1)if hd else(0,)):
						tot=c0+2*c1+d_;b1=1 if(p1 is None or c1==p1)else 0;sc=(2*_tz((cc-tot)&M32)+b1,-tot,-d_)
						if best is None or sc>best[0]:best=(sc,c0,c1,d_,wc,cc)
		_,c0,c1,dl,wb,cb=best;cv2=(cb-c0-2*c1-dl)&M32;t,rem=_adduc(g,h,u,cv2,c1,ch1);s=g.add3(t,vs[0],wb,c0,None,h[0],u[0]);return(g.add(s,_constw(rem))if rem else s),fg,dl
	return g.addm(u,_sigma(g,e,6,11,25,False),*Wd),fg,0
def _rnd2(g,st,Wd):
	a,b,c,d,e,f,gg,h,prev,hg=st;t1,fg,delta=_t1hg(g,e,f,gg,h,hg,Wd,d);ne=g.add(d,t1,ONE if delta else ZERO);ab,mj=[None]*32,[None]*32
	def mb(j):
		ab[j]=g.XOR(a[j],b[j])
		if c[j]==ZERO:mj[j]=g.AND(a[j],b[j])
		elif ab[j][0]and prev[j][0]and ab[j][0]!=prev[j][0]and ab[j][1]!=prev[j][1]:mj[j]=g.XOR(g.AND((ab[j][0],ab[j][1]^1),prev[j]),c[j])
		else:mj[j]=g.XOR(g.AND(ab[j],prev[j]),b[j])
		return mj[j]
	if all(x[0]==0 for x in b):
		S0=_sigma(g,a,2,13,22,False)
		for j in range(32):mb(j)
		na=g.add3(t1,S0,mj,delta)if delta else g.addm(t1,S0,mj)
	else:g.ahi+=(not delta);na=g.add3(t1,lambda j:_sigb(g,a,2,13,22,False,j),mb,delta)
	return(na,a,b,c,ne,e,f,gg,ab,fg)
def _ch3(g,cs,B,e,f,gg,hg,kv):
	X,AN,OR=g.XOR,g.AND,g.OR;fg=[X(f[j],gg[j])for j in range(32)];s,R1,R2,u,U=[None]*32,[None]*32,[None]*32,ONE,ZERO
	for i in range(32):
		sm=not(e[i][0]and fg[i][0]and e[i][1]!=fg[i][1]);cp=(gg[i][1]^(e[i][1]&fg[i][1]))if sm else(f[i][1]^e[i][1]^1);z,R1[i],R2[i],x,pt,oU=cs[0][i],cs[1][i],cs[2][i],B[i],U[1]^u[1],i==30;pw5,ok,b1,b2=x[1]^cp,(i in(0,31)and sm),0,0
		if sm and 0<i<31:
			for k in range(3):
				w=cs[k][i];wb=w[1];pw6=wb^pw5;ca=(wb in(cp,x[1]))and(pw6!=pt or pw6!=u[1]);cb=wb==pt and cp!=u[1]
				if ca or cb or(u==ONE and wb==U[1]==pw5!=x[1]):z,R1[i],R2[i],ok,b1,b2=w,cs[k==0][i],cs[2-(k==2)][i],1,ca,cb;break
		w5=X(hg[i],AN(e[i],fg[i]))if ok else X(gg[i]if sm else f[i],AN(e[i]if sm else(e[i][0],e[i][1]^1),fg[i]))
		if i==0:
			if ok:u0=X(z,x);s[0]=X(z,w5);c0=X(AN(u0,w5),x)if z[1]==cp else X(AN(u0,(w5[0],w5[1]^1)),z)
			else:s[0],c0=g.fa(z,x,w5)
			U=(c0[0],c0[1]^1)
		elif i==31:s[31]=X(X(z,w5)if ok else X(X(z,x),w5),U)
		elif not ok:s[i],u,U=g._col((z,x,w5),u,U,oU)
		elif b1:
			w6=X(z,w5);s[i]=X(U,w6);w11=OR(w5,X(x,z)if z[1]==cp else X(x,w6))
			if(z[1]^pw5)!=pt:w9=X(u,w6);w10=OR(U,(w9[0],w9[1]^1));u,U=(ZERO if oU else X(w6,(w10[0],w10[1]^1))),X(w10,(w11[0],w11[1]^1))
			else:w9=X(u,s[i]);w10=AN((U[0],U[1]^1),w9);u,U=(ZERO if oU else X(w6,w11)),X(w10,w11)
		elif b2:n5=X(z,U);n9=X(x,n5);s[i]=X(w5,n5);n8=OR(U,X(z,u));n11=AN((w5[0],w5[1]^1),n9);u,U=(ZERO if oU else X(n5,n11)),X(n8,n11)
		else:n5=X(z,U);w5U=X(w5,U);s[i]=X(w5,n5);g1=OR((x[0],x[1]^1),w5);g2=AN(n5,w5U);u,U=(ZERO if oU else X(w5,(g1[0],g1[1]^1))),X(g1,g2)
	return g.addm(s,R1,R2,_constw(kv)),fg
def _net_u(G=Gen):
	g=G(256);g.split={};Y=[[g.inputs[32*(7-k)+j]for j in range(32)]for k in range(8)];W=[None]*ROUNDS
	for i in range(PRE):W[i]=_constw(PREFIX_WORDS[i])
	for k in range(8):pos=VARBASE+k;W[pos]=g.addm(Y[k],_constw((-K[pos])&M32))if pos in OFFSET else Y[k]
	for pos,val in TAILMAP.items():W[pos]=_constw(val)
	wd=lambda i:(Y[i-VARBASE],)if i in OFFSET else(_constw(4 if i==23 else K[i]),W[i]);z,nk9=_constw(0),_constw((-K[9])&M32);st=(Y[0],z,z,z,Y[0],z,z,nk9,z,nk9);r=ROUNDS;s0f=lambda A:lambda j:_sigb(g,A,7,18,3,True,j);s1f=lambda A:lambda j:_sigb(g,A,17,19,10,True,j)
	def make_w(i):
		if W[i]is not None:return
		if i>=r-2:W[i]=g.add3(W[i-16],s0f(W[i-15]),W[i-7]);return
		if i==21:s0=_sigma(g,W[6],7,18,3,True);v=sum(s0[b][1]<<b for b in range(32));g.ahi+=1;W[21]=g.add2c(Y[6],s1f(W[19]),(PREFIX_WORDS[5]+v-K[14])&M32);return
		if i>=24 and not _ADD_HINTS[g.ahi]:g.ahi+=1;s=g.add3(W[i-16],s0f(W[i-15]),s1f(W[i-2]),0,W[i-7][0]);W[i]=g.add(s,[ZERO]+W[i-7][1:]);return
		w_m7=(Y[i-15],_constw((-K[i-7])&M32))if i in(17,21,22)else((g.split[tuple(W[16])][0],_constw(g.split[tuple(W[16])][1]))if i==23 else(W[i-7],));W[i]=g.addm(W[i-16],_sigma(g,W[i-15],7,18,3,True),*w_m7,_sigma(g,W[i-2],17,19,10,True),force_bb=2 if i==23 else None)
	for i in range(9,r):
		if i>=16:
			if i==19:make_w(19);make_w(21);s23=g.add3(s0f(W[8]),g.split[tuple(W[16])][0],s1f(W[21]),2);cv23=(4-K[23])&M32
			elif i==23:W[23]=s23;g.split[tuple(s23)]=(s23,cv23)
			else:
				make_w(i)
				if i==31:make_w(32)
		if i<r-NTAIL:
			st=_rnd2(g,st,wd(i))
			if i==23:s_r,cv_r=g.split[tuple(W[i])];W[i]=g.add(s_r,_constw(cv_r))
	if TAILB:a6,a7,a8,a9,e6,e7,e8,e9,prev,hg=st;T5,fg,_=_t1hg(g,e6,e7,e8,e9,hg,(_constw(K[r-6]-1),W[r-6]));e5=g.add(a9,T5,ONE);mj=[g.OR((ab[0],ab[1]^1),a8[j])if(QM>>j)&1 else g.AND(ab,a8[j])for j in range(32)for ab in(g.XOR(a6[j],a7[j]),)];Q=g.add(T5,mj,ONE);T4,fg,_=_t1hg(g,e5,e6,e7,e8,fg,wd(r-5));e4=g.add(a8,T4);e3,fg=_ch3(g,[W[r-4],a7,_sigma(g,e4,6,11,25,False)],e7,e4,e5,e6,fg,K[r-4]-2);e2,_=_ch3(g,[W[r-3],a6,_sigma(g,e3,6,11,25,False)],e6,e3,e4,e5,fg,K[r-3]-2);X=g.addm(W[r-2],_sigma(g,W[r-4],17,19,10,True),e5,[g.OR(e2[j],e4[j])if(XM>>j)&1 else g.AND((e2[j][0],e2[j][1]^1),e4[j])for j in range(32)]);Y_out=g.addm(W[r-1],_sigma(g,W[r-3],17,19,10,True),e4);bw=[e3,e2,a7,a6,Q,T4,X,Y_out];out=[bw[PERM[k]]for k in range(8)];assert g.ahi==len(_ADD_HINTS);return g,[t for w in out for t in w]
MAX_NODES=43836
MAX_RECORDS=43541
CSE_PROBE_LIMIT=8
class BGen(Gen):
	def __init__(self,n,run,pas):self.n,self.run,self.pas,self.calls=n,run,pas,0;self.ahi=0;self.inputs=[(j+1,0)for j in range(n)];self.nn,self.rn,self.ncse,self.mp=n+1,0,0,0;self.recent,self.cse_k,self.cse_v=[None]*8,[0]*1024,[None]*1024
	def _gate(self,node):
		for d in range(min(8,self.rn)):
			r=self.recent[(self.rn-1-d)&7]
			if r[3]==node:return r[:3]
		return None
	def _new(self,op,a,b):
		k,self.nn=self.nn,self.nn+1
		if k>=MAX_NODES:self.run.err=1;return 0
		if self.pas==0:
			if self.run.uses[a]==255 or self.run.uses[b]==255:self.run.err=6
			self.run.uses[a]+=1;self.run.uses[b]+=1
		else:self.run.alloc(op,k,a,b)
		return k
	def mk(self,op,x,y):
		self.calls+=1
		if x>y:x,y=y,x
		a,b=x,y
		if b<=256:
			key=({"x":1,"a":2,"o":3}[op])|(a<<2)|(b<<11);p=((key*2654435761)&M32)>>22;prb=1
			while self.cse_k[p]:
				if self.cse_k[p]==key:self.mp=max(self.mp,prb);return self.cse_v[p]
				p=(p+1)&1023;prb+=1
				if prb>CSE_PROBE_LIMIT:self.run.err=16;return 0
			self.mp=max(self.mp,prb);self.ncse+=1
			if self.ncse>900:self.run.err=10
			s=self._new(op,a,b);self.cse_k[p],self.cse_v[p]=key,s
		else:
			for d in range(min(8,self.rn)):
				r=self.recent[(self.rn-1-d)&7]
				if r[:3]==(op,a,b):return r[3]
			s=self._new(op,a,b)
		self.recent[self.rn&7]=(op,a,b,s);self.rn+=1;return s
_M8,_M14=(1<<288)-(1<<256),(1<<480)-(1<<448)
_MF=((1<<512)-(1<<384),(1<<512)-(1<<416),(1<<512)-(1<<448),_M14,0)
def _pick(f,p):
	for q in(p,*_MF):
		if f&~q:m=f&~q;return(m&-m).bit_length()-1
	return-1
class BoundedEmitter:
	def __init__(self):self.uses,self.err,self.records=[0]*MAX_NODES,0,[]
	def emit(self,op,d,a,b):
		if len(self.records)>=MAX_RECORDS or max(d,a,b)>=1024:self.err=5;return
		self.records.append((op,d,a,b))
	def take(self,pf=None,p=0):
		r=pf if pf is not None and self.free>>pf&1 else _pick(self.free,p)
		if r<0:self.err=8;return 0
		self.free&=~(1<<r);return r
	def alloc(self,op,k,x,y):
		self.uses[x]-=1;self.uses[y]-=1;dx,dy=self.uses[x]==0,self.uses[y]==0;w=256+self.order[self.co][1]if self.co<len(self.order)and self.order[self.co][0]==k else None;b=~((self.pend if k<self.f0-1800 else self.pend&~_M14)&~_M8)if self.uses[k]<=3 and k<self.f1-1800 and w is None else self.pend;okx=dx and(not(b>>self.reg[x]&1)or self.reg[x]==w);oky=dy and(not(b>>self.reg[y]&1)or self.reg[y]==w);dst=self.take(w)if w is not None and self.free>>w&1 else w if(dx and self.reg[x]==w)or(dy and self.reg[y]==w)else self.reg[x]if okx else self.reg[y]if oky else None
		if dx and self.reg[x]!=dst:self.free|=1<<self.reg[x]
		if dy and self.reg[y]!=dst:self.free|=1<<self.reg[y]
		if dst is None:dst=self.take(p=b)
		if dst==w:self.pend&=~(1<<dst)
		self.emit({"x":1,"a":2,"o":3}[op],dst,self.reg[x],self.reg[y]);self.reg[k]=dst
		while self.co<len(self.order)and self.order[self.co][0]==k:self.oreg[self.order[self.co][1]]=dst;self.co+=1
		if not self.uses[k]:self.err=9;self.free|=1<<dst
	def run(self):
		g0,out0=_net_u(lambda n:BGen(n,self,0));nodes,self.calls=g0.nn,g0.calls;self.onode=[x[0]for x in out0];self.oneg=[x[1]for x in out0];self.order=sorted((n,i)for i,n in enumerate(self.onode)if n)
		for n,_ in self.order:self.uses[n]+=1
		self.f0,self.f1=self.order[0][0],self.order[32][0];self.free=sum(1<<r for r in range(REGISTERS)if r<256 or r>=512);self.pend=sum(1<<(256+i)for i,n in enumerate(self.onode)if n);self.reg={n:INREG(n-1)for n in range(1,257)};self.oreg,self.co=[0]*256,0
		while self.co<len(self.order)and self.order[self.co][0]<=256:n,i=self.order[self.co];self.oreg[i]=INREG(n-1);self.co+=1
		for n in range(1,257):
			if not self.uses[n]:self.free|=1<<INREG(n-1)
		g1,out1=_net_u(lambda n:BGen(n,self,1));self.calls+=g1.calls;self.mp=max(g0.mp,g1.mp);assert out1==out0 and self.mp<=CSE_PROBE_LIMIT;todo=[(i,self.oreg[i])for i,n in enumerate(self.onode)if n and self.oreg[i]!=256+i];moves=0
		while todo:
			srcs=[s for _,s in todo];k=next((k for k,(i,s)in enumerate(todo)if 256+i not in srcs),None)
			if k is None:s,t=todo[0][1],self.take();self.emit(4,t,s,0);moves+=1;todo=[(i,t if r==s else r)for i,r in todo]
			else:i,s=todo.pop(k);self.emit(4,256+i,s,0);moves+=1
		for i,n in enumerate(self.onode):
			if not n:self.emit(5,256+i,self.oneg[i],0)
		top=max(max(r[1:4])if r[0]<=3 else max(r[1:3])if r[0]==4 else r[1]for r in self.records)+1;q=sum(self.oneg[i]<<(32*(7-i//32)+i%32)for i in range(256)if self.onode[i]);counts=[sum(r[0]==op for r in self.records)for op in(1,2,3)];info=(len(self.records),top,nodes,self.calls,moves,self.err,*counts,4*MAX_RECORDS,COUNTERS,MAX_NODES,GEN_STATE_BYTES,len(_ADD_HINTS),GEN_CONSTANT_BYTES);return info,q,self.records
def _encode_body(records):
	out=bytearray()
	for op,d,a,b in records:assert 1<=op<=3 and max(d,a,b)<1024;out+=((op-1)|(d<<2)|(a<<12)|(b<<22)).to_bytes(4,"little")
	return bytes(out)
def bounded_check(pr):info,q,records=BoundedEmitter().run();py=[({"^":1,"&":2,"|":3,"M":4,"S":5}[o],d,a,b)for o,d,a,b in pr.recs];assert info==EXPECTED_EMITTER_INFO;assert q==pr.qint==POLARITY_Q and records==py;assert hashlib.sha256(GEN_C.encode()).hexdigest()==STATIC_C_SHA256;stream=_encode_body(records);digest=hashlib.sha256(stream).hexdigest();assert len(stream)==4*pr.instr and digest==STATIC_SLP_SHA256;return info,digest
def _alloc(g,nin,fixed,outs,tgt,free0,E):
	N=g.nodes;uses=[0]*len(N);want={}
	for _,x,y in N[nin+1:]:uses[x]+=1;uses[y]+=1
	for i,(n,_)in enumerate(outs):uses[n]+=1;want.setdefault(n,tgt[i])
	oids=sorted(want);f0,f1=oids[0],oids[32];reg=dict(fixed);free=sum(1<<r for r in free0 if r not in fixed.values())|sum(1<<r for v,r in fixed.items()if not uses[v]);pend=sum(1<<tgt[i]for i,(n,_)in enumerate(outs)if n)
	def take(w=None,p=0):nonlocal free;r=w if w is not None and free>>w&1 else _pick(free,p);free&=~(1<<r);return r
	for k in range(nin+1,len(N)):
		op,x,y=N[k];uses[x]-=1;uses[y]-=1;dying=[v for v in(x,y)if not uses[v]];w=want.get(k);p=~((pend if k<f0-1800 else pend&~_M14)&~_M8)if(uses[k]<=3 and k<f1-1800 and w is None)else pend;ok=[reg[v]for v in dying if not p>>reg[v]&1 or reg[v]==w];dst=take(w)if w is not None and free>>w&1 else w if any(reg[v]==w for v in dying)else ok[0]if ok else None
		for v in dying:
			if reg[v]!=dst:free|=1<<reg[v]
		if dst is None:dst=take(p=p)
		reg[k]=dst
		if dst==w:pend&=~(1<<w)
		E(({"x":"^","a":"&","o":"|"}[op],dst,reg[x],reg[y]))
	return sum(reg[n]!=tgt[i]for i,(n,_)in enumerate(outs)if n)
def INREG(j):return 256+32*(7-j//32)+j%32
def assemble():info,q,records=BoundedEmitter().run();assert info[4:6]==(0,0);_QM[:]=[q];return[({1:"^",2:"&",3:"|"}[op],d,a,b)for op,d,a,b in records],info[4],info[3]
class Prog:
	def __init__(self):self.recs,self.moves,self.calls=assemble();self.q,self.qint,self.pin=[0]*256,_QM[0],[0]*256;self.qwords=[(self.qint>>(32*i))&M32 for i in range(8)];self.instr=self.kernel=len(self.recs);self.nregs=max(max(r[1:4])for r in self.recs)+1;self.compile()
	def run(self,pc,end,regs):
		for op,d,a,b in self.recs[pc:end]:regs[d]=regs[a]^regs[b]if op=="^"else regs[a]&regs[b]if op=="&"else regs[a]|regs[b]
		return end-pc
	def compile(self):
		ns,fs={"ALL":ALL},[]
		for a in range(0,len(self.recs),4096):exec(compile("def c(r):\n"+"".join(" r[%d]=r[%d]%sr[%d]\n"%(d,x,o,y)for o,d,x,y in self.recs[a:a+4096]),"<p>","exec"),ns);fs.append(ns["c"])
		self.ns=ns;self.fast=lambda r:[c(r)for c in fs]
	def step(self,*planes):
		regs=[0]*REGISTERS
		for j,pl in enumerate(planes):regs[INREG(j)]=pl
		self.fast(regs);return[regs[INREG(j)]for j in range(len(planes))]
_TM={1<<k:sum(1<<c for c in range(256)if not c>>k&1)for k in range(8)}
def transpose(rows):
	R=list(rows)+[0]*(256-len(rows));s=128
	while s:
		m=_TM[s]
		for i in range(256):
			if not i&s:t=((R[i]>>s)^R[i+s])&m;R[i+s]^=t;R[i]^=t<<s
		s>>=1
	return R
def pack_lanes(xs,n,pin):T=transpose(xs);return[T[j]^(ALL if pin[j]else 0)for j in range(n)]
def lanes_of(planes,n,pin):T=transpose([planes[j]^(ALL if pin[j]else 0)for j in range(n)]);return T[:256]
def lane_value(planes,l,pin,n):
	x=0
	for j in range(n):x|=(((planes[j]>>l)&1)^pin[j])<<j
	return x
def set_lane(planes,l,x,pin,n):bit=1<<l;return[(planes[j]&~bit)|((((x>>j)&1)^pin[j])<<l)for j in range(n)]
LAMBDA=Fraction(497,1000)
CUTLOSS=Fraction(15,100000)
TAIL_AGES=1e-6
CMAX=7
CUT_HALT_ORDER=CMAX+1
P_MIN=0.390000001
GRAIN=10**21
STAGE1_PLANES=20
LOOP_OPS=3
HIT_OPS=2800
EVENT_OPS=3800
CUT_OPS=4200
SLICE_OPS=1300
RECOVER_EXTRA=39
INSTR_BYTES=5
BODY_BYTES=4
REC_RECORD_BYTES=5
GEN_INSTR_BYTES=36
HANDLER_CODE,SETUP_CODE,RECOVERY_CODE=1000,160,94
REGISTERS=884
REGFILE=REGISTERS*32
COUNTERS=16384
ARRAYS=64*32
KEYB=48
SLOTB=KEYB
MEM_LIMIT=1<<20
ADVICE=0
KAPPA_256=48
KR=Fraction(1273,100)
KCHK=8192
CHK_OPS=80
PROBE_OPS=100
WASM_RUN_OPERATORS=89747938
WASM_OPERATOR_FACTOR=2
WASM_EMITTER_INSTR=9708
GEN_STATE_BYTES,GEN_CONSTANT_BYTES=EXPECTED_EMITTER_INFO[12],EXPECTED_EMITTER_INFO[14]
SETUP_FIXED=256*3100+20000
OFFSET_SEARCH_EVALS=64+1+3*192+1000
SELECTOR_THREE_WORD_SITES=31
SELECTOR_FOUR_WORD_SITES=17
SELECTOR_ALTERNATIVES=SELECTOR_THREE_WORD_SITES+SELECTOR_FOUR_WORD_SITES*10+2
SELECTOR_SEARCH_EVALS=1+2*SELECTOR_ALTERNATIVES
SEARCH_EVAL_OPS=1<<48
OFFSET_SEARCH_OPS=OFFSET_SEARCH_EVALS*SEARCH_EVAL_OPS
SELECTOR_SEARCH_OPS=SELECTOR_SEARCH_EVALS*SEARCH_EVAL_OPS
CFG={16:dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),18:dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),256:dict(s1=20,W=102,kappa=KAPPA_256,Sb=1<<48)}
def stage1_ops(pin,s1):
	npos=sum(1 for j in range(s1)if not pin[j]);nneg=s1-npos;ops=max(npos- 1,0)+max(nneg- 1,0)
	if nneg:ops+=2 if npos else 1
	return ops+1+2
def stage1(planes,s1,pin):
	nz=0;pos=[planes[j]for j in range(s1)if not pin[j]];neg=[planes[j]for j in range(s1)if pin[j]]
	if pos:
		acc=pos[0]
		for q in pos[1:]:acc|=q
		nz|=acc
	if neg:
		acc=neg[0]
		for q in neg[1:]:acc&=q
		nz|=acc^ALL
	return ALL^nz
def inflight_m(lanes=LANES,eps=TAIL_AGES):
	m=lanes
	while True:
		x=m/lanes
		if exp(-lanes*(x- 1-log(x)))<=eps:return m
		m+=1
INFLIGHT=inflight_m()
def tail_log2(mean,k):return(-mean+k*(1+log(mean/k)))/log(2)
_PROG=[]
_QM=[0]
def prog():
	global REGFILE
	if not _PROG:_PROG.append(Prog());REGFILE=32*(_PROG[0].nregs+3)
	return _PROG[0]
def table_bytes(tmax):return-(-(tmax+LANES+CMAX)*SLOTB//8)
def search_envelopes():gate_ops=1024;raw=2*160*64*32*13*13*12*gate_ops;assert 2*raw<SEARCH_EVAL_OPS;assert OFFSET_SEARCH_EVALS==1641 and SELECTOR_ALTERNATIVES==203 and SELECTOR_SEARCH_EVALS==407;return raw,raw
TB=18
FINE,COARSE=20000,2000
def _lossq(Tp,q,tmax,kappa,Sb,rate=1.0):
	from math import expm1;D=122;L=Fraction(1<<D,Tp);c=-(-kappa*L.numerator//L.denominator);th,Lf,cf=Tp/2.0**D,float(L),float(c);Q,B,Np=q*Lf,q*Lf/LANES,2.0**256/rate;k=int(q)+1
	while tail_log2(q,k)>- 40:k+=1
	n2,shift=k+LANES+CMAX,1/(1-k*Q/Np);pi=lambda m:exp(-m*(m- 1)/(2*Np));split=max(1.0,Q- 120*LANES*Lf);edges=[split*i/COARSE for i in range(COARSE+1)]+[split+(Q-split)*i/FINE for i in range(1,FINE+1)];delay,pa=0.0,1.0
	for b in edges[1:]:pb=pi(b);delay+=(pa-pb)*exp(-th*max(0.0,B-b/LANES));pa=pb
	p,ql,hq=exp(-cf*th),Q*Lf/Np,Q*(Q- 1)/(2*Np);p2=exp(-(cf-1)*th)*(1+(cf-1)*th/(1-th));kr=float(KR)*Lf;prec=2*hq*exp(-(kr-1)*th)*(1+(kr-1)*th/(1-th));hh=(Q*(Q- 1)/2+2.0**TB*Q)/Np;cuts=1-sum(comb(n2,j)*p**j*exp((n2-j)*log1p(-p))for j in range(CUT_HALT_ORDER));t=dict(no_collision=pi(Q)*shift,delay=delay*shift,partner_own_trail=ql,partner_cut_trail=(cf+Sb)*Q*p*(q+LANES)/((1-p)*Np),too_old=hq*p2,P_rec=prec,rest_of_path=hq*Lf*(Q+2.0**TB)/Np,finished_count=2.0**- 40,cut_halt=cuts+ql*(1+(2+kappa)*exp(-kappa/2)+2*hq)+hq*p*(3+2*kappa),key_false_match=tmax*(tmax- 1)/2*2.0**-(min(KEYB-(Tp- 1).bit_length(),256-D)+log2(Tp)),table_capacity=2.0**tail_log2(q,tmax- 59),misc=Q*2.0**TB/Np+k*k*Lf/Np+255*Q/Np+exp(min(700.0,- 300+(exp(5)- 1)*hh))+2.0**- 90);t["sum"]=sum(t.values());t["P_lower"]=1-t["sum"];t.update(trails=q,k=k);return t
_B={}
def loss(p,rate=1.0):return _lossq(p["Tp"],float(p["Q"]/p["L"]),p["tmax"],p["kappa"],p["Sb"],rate)
class Halt(Exception):pass
class DigestNet:
	def __init__(self,qint):
		assert TAILB;g=Gen(256);E=[[(g.inputs[32*(7-k)+j][0],(qint>>(32*(7-k)+j))&1)for j in range(32)]for k in range(8)];S0=lambda x:_sigma(g,x,2,13,22,False);S1=lambda x:_sigma(g,x,6,11,25,False);mj=lambda a,b,c:[g.XOR(g.AND(g.XOR(a[j],b[j]),g.XOR(b[j],c[j])),b[j])for j in range(32)];ch=lambda e,f,gv:[g.XOR(gv[j],g.AND(e[j],g.XOR(f[j],gv[j])))for j in range(32)];neg=lambda x:[(s[0],s[1]^1)for s in x];bw=[None]*8
		for k in range(8):bw[PERM[k]]=E[k]
		e3,e2,a7,a6,Q,T4,X,Y=bw;a5=g.addm(Q,[ZERO if(QM>>j)&1 else g.AND(a6[j],a7[j])for j in range(32)],neg([g.AND((a6[j][0],a6[j][1]^1),(a7[j][0],a7[j][1]^1))if(QM>>j)&1 else ZERO for j in range(32)]),_constw(1),S0(a6));a4=g.addm(T4,S0(a5),mj(a5,a6,a7));a3=g.addm(e3,neg(a7),_constw(1),S0(a4),mj(a4,a5,a6));a2=g.addm(e2,neg(a6),_constw(1),S0(a3),mj(a3,a4,a5));t1=g.addm(X,[ZERO if(XM>>j)&1 else g.AND(e2[j],e3[j])for j in range(32)],neg([g.AND(e2[j],(e3[j][0],e3[j][1]^1))if(XM>>j)&1 else ZERO for j in range(32)]),_constw((1+K[ROUNDS- 2])&M32),S1(e2));e1=g.add(a5,t1);a1=g.addm(t1,S0(a2),mj(a2,a3,a4));t0=g.addm(Y,S1(e1),ch(e1,e2,e3),_constw(K[ROUNDS- 1]));st=[g.addm(t0,S0(a1),mj(a1,a2,a3)),a1,a2,a3,g.add(a4,t0),e1,e2,e3];cv=[g.addm(w,_constw(v))for w,v in zip(st,IV)];a,b,c,d,e,f,gg,h=cv
		for kw in _KW2:t1=g.addm(h,S1(e),ch(e,f,gg),_constw(kw));t2=g.add(S0(a),mj(a,b,c));a,b,c,d,e,f,gg,h=g.add(t1,t2),a,b,c,g.add(d,t1),e,f,gg
		dw=[g.add(x,y)for x,y in zip(cv,[a,b,c,d,e,f,gg,h])];self.out=[dw[7-i//32][i%32]for i in range(256)];ops,N={"x":"^","a":"&","o":"|"},g.nodes;last,slot,free,src,m={},list(range(257))+[0]*(len(N)- 257),[],[],257
		for k in range(257,len(N)):last[N[k][1]]=last[N[k][2]]=k
		for s in self.out:last[s[0]]=len(N)
		for k in range(257,len(N)):
			o,x,y=N[k];free+=[slot[z]for z in{x,y}if last[z]==k]
			if free:slot[k]=free.pop()
			else:slot[k],m=m,m+1
			src.append("    v[%d] = v[%d] %s v[%d]"%(slot[k],slot[x],ops[o],slot[y]))
			if k not in last:free.append(slot[k])
		self.out=[(slot[s[0]],s[1])for s in self.out];ns,self.fs={},[]
		for i in range(0,len(src),4096):exec(compile("def c(v):"+chr(10)+chr(10).join(src[i:i+4096])+chr(10),"<digest>","exec"),ns);self.fs.append(ns["c"])
		self.nn=m
	def step(self,planes,k=256,a=ALL):
		v=[0]*self.nn;v[1:257]=planes
		for c in self.fs:c(v)
		return[v[s[0]]^(a if s[1]else 0)for s in self.out[:k]]
_DN=[]
def dnet():
	if not _DN:_DN.append(DigestNet(prog().qint))
	return _DN[0]
class Engine:
	def __init__(self,n):self.n,self.pr,self.pin=n,prog(),[0]*n
	def _low(self,o):return digest_of_g(o,self.pr.qint)&((1<<self.n)- 1)
	def step(self,*planes):return dnet().step(list(self.pr.step(*(list(planes)+[0]*(256-len(planes))))))[:self.n]
	def wstep(self,P):n,a,ns=self.n,(1<<256*len(P))- 1,self.pr.ns;W=[sum(q[j]<<256*i for i,q in enumerate(P))for j in range(n)];ns["ALL"]=a;o=dnet().step(self.pr.step(*(W+[0]*(256-n))),n,a);ns["ALL"]=ALL;return[[(x>>256*i)&ALL for x in o]for i in range(len(P))]
	def f2(self,xs):return[self._low(o)for o in packed_f(xs,256,self.pr.qwords)]
	def g_scalar(self,x):return digest_of_state(state_words(words_of(x)))&((1<<self.n)- 1)
def is_dp(x,p):return x&((1<<p["s1"])- 1)==0 and(x>>p["s1"])&((1<<p["W"])- 1)<p["Tp"]
def dp_key(x,p):return(((x>>p["D"])&((1<<p["kb"])- 1))<<p["fb"])|((x>>p["s1"])&((1<<p["fb"])- 1))
def walk(xs,k,f2):
	for _ in range(k):xs=f2(xs)
	return xs
def reference_recover(p,r,t0,t1,f2,kchk=None):
	mask,cr=p["N"]-1,p["cr"];kchk=kchk or p["kchk"];D=-(-cr//kchk);xs,ls,ends=[(r+t0)&mask,(r+t1)&mask],[None,None],[None,None];ck=[[xs[0]],[xs[1]]]
	for k in range(1,cr+1):
		xs=f2(xs)
		for i in(0,1):
			if ls[i]is None:
				if k%D==0:ck[i].append(xs[i])
				if is_dp(xs[i],p):ls[i],ends[i]=k,xs[i]
		if None not in ls:break
	else:raise Halt()
	a=0 if ls[0]>=ls[1]else 1;lb,(qd,rd)=ls[1-a],divmod(abs(ls[0]-ls[1]),D);A=lambda i:walk([ck[a][i+qd]],rd,f2)[0]
	if ends[0]!=ends[1]or A(0)==ck[1-a][0]:return None
	lo,hi=0,lb//D+1
	while hi-lo>1:mid=(lo+hi)//2;lo,hi=(lo,mid)if A(mid)==ck[1-a][mid]else(mid,hi)
	x,y=A(lo),ck[1-a][lo]
	for _ in range(min(hi*D,lb)-lo*D):
		fx,fy=f2([x,y])
		if fx==fy:
			if p["n"]==256:s0,s1=enc_invert(words_of(f_scalar(x))),enc_invert(words_of(f_scalar(y)));assert s0==s1==state_words(words_of(x))
			return x,y
		x,y=fx,fy
	return None
	for _ in range(b[1]+1):
		ya,yb=f2(xs)
		if ya==yb:
			if p["n"]==256:s0,s1=enc_invert(words_of(f_scalar(xs[0]))),enc_invert(words_of(f_scalar(xs[1])));assert s0==s1==state_words(words_of(xs[0])),"encoding collision is not a state collision"
			return xs[0],xs[1]
		xs=[ya,yb]
	return None
def search(eng,p,r,cnt):
	g,x=_search(eng,p,r,cnt),None
	try:
		while True:x=g.send(x and eng.step(*x))
	except StopIteration as e:return e.value
def reference_search(eng,p,r,cnt):
	n,mask,pin=p["n"],p["N"]- 1,eng.pin;table,births,ts,nxt=[],[0]*LANES,list(range(LANES)),LANES;planes=pack_lanes([(r+t)&mask for t in ts],n,pin);cnt["inserts"]+=LANES;batches=0
	while batches<p["B"]:
		planes=list((yield planes));batches+=1;cnt["batches"]+=1;hit=stage1(planes,p["s1"],pin)
		while hit:
			cnt["stage1_hits"]+=1
			if cnt["stage1_hits"]>p["e2max"]:raise Halt("stage-1 budget")
			l=(hit&-hit).bit_length()- 1;hit&=hit- 1;x=lane_value(planes,l,pin,n)
			if is_dp(x,p):
				key=dp_key(x,p);cnt["finished"]+=1;w=key+1
				if w in table:
					t0=table.index(w);cnt["recoveries"]+=1;res=reference_recover(p,r,t0,ts[l],eng.f2)
					if res is None:raise Halt("recovery found no pair")
					return res
				if cnt["finished"]>p["tmax"]:raise Halt("table full")
				assert 0<w<1<<KEYB and ts[l]<p["tmax"]+LANES+p["cmax"];table+=[0]*(ts[l]+1-len(table));table[ts[l]]=w;ts[l],nxt,births[l]=nxt,nxt+1,batches;planes=set_lane(planes,l,(r+ts[l])&mask,pin,n);cnt["inserts"]+=1
		if batches%p["Sb"]==0:
			for l in range(LANES):
				if batches-births[l]>=p["c"]:
					cnt["cut"]+=1
					if cnt["cut"]>p["cmax"]:raise Halt("cut budget")
					ts[l],nxt,births[l]=nxt,nxt+1,batches;planes=set_lane(planes,l,(r+ts[l])&mask,pin,n);cnt["inserts"]+=1
	return None
class Counters(dict):
	def __missing__(self,k):return 0
def derive(seed,tag,bits=256):return int.from_bytes(hashlib.shake_256(("%s/%s"%(seed,tag)).encode()).digest((bits+7)//8),"little")&((1<<bits)- 1)
def attempt(eng,p,seed,tag):
	cnt=Counters()
	try:res=search(eng,p,derive(seed,tag,p["n"]),cnt)
	except Halt as e:cnt["halt"]+=1;res=None
	return res,cnt
N_T3=16
M_T2,B_T2=256,16
def parallel_rows(trials):
	eng,p,G,C,R,cur=Engine(N_T3),plan(N_T3),{},{},{},{}
	def adv(i,v):
		try:cur[i]=G[i].send(v);return
		except StopIteration as e:R[i]=e.value
		except Halt:C[i]["halt"]+=1
		del cur[i]
	for i,t in enumerate(trials):C[i]=Counters();G[i]=_search(eng,p,derive(t["seed"],"t",p["n"]),C[i]);adv(i,None)
	while cur:
		ks=list(cur)
		for i,o in zip(ks,eng.wstep([cur[i]for i in ks])):adv(i,o)
	return[e1_obs(R.get(i),C[i])for i in range(len(trials))]
def e1_obs(res,cnt):obs=dict(target_ok=int(res is not None),batches=cnt["batches"],halt=cnt["halt"]);return(None,None,obs)if res is None else(message(res[0]),message(res[1]),obs)
def e2_trial(seed,tr,st):
	src,z=tr%3,[0]*256
	if src==0:xs=[derive(seed,"u%d"%i)for i in range(M_T2)]
	elif src==1:r=derive(seed,"r");xs=[(r+i)&ALL for i in range(M_T2)]
	else:
		xs,cur=[],[derive(seed,"c%d"%l)for l in range(LANES)]
		for _ in range(M_T2//LANES):cur=lanes_of(list(st.step(*pack_lanes(cur,256,st.pin))),256,st.pin);xs+=cur
	digs=[]
	for b in range(M_T2//LANES):digs+=lanes_of(dnet().step(list(st.step(*pack_lanes(xs[b*LANES:(b+1)*LANES],256,st.pin)))),256,z)
	first,pair={},None
	for i,d in enumerate(digs):
		c=d&((1<<B_T2)- 1)
		if c in first and xs[first[c]]!=xs[i]and pair is None:pair=(xs[first[c]],xs[i])
		first.setdefault(c,i)
	obs=dict(source=src,dup_w0=len(digs)-len(first));return(None,None,obs)if pair is None else(message(pair[0]),message(pair[1]),obs)
def serve(req):
	eid,out=req["experiment_id"],[];bounded_check(prog())
	if eid=="bssha-n16":rows=e1_rows(req["trials"])
	elif eid=="proj-k0-w256":st=prog();rows=[e2_trial(t["seed"],t["trial"],st)for t in req["trials"]]
	else:raise ValueError("unknown experiment")
	for t,(a,b,obs)in zip(req["trials"],rows):out.append({"trial":t["trial"],"message_a_hex":a.hex()if a else None,"message_b_hex":b.hex()if b else None,"observations":obs})
	return{"schema_version":1,"trials":out}
def kernel_selftest():
	import random;assert CUT_HALT_ORDER==CMAX+1==8;r=random.Random(3);p=prog();info,h=bounded_check(p);bt=boundary_test(p,plan(256));g,o=_net_u();ref=[];m=_alloc(g,256,{j+1:INREG(j)for j in range(256)},o,[256+i for i in range(256)],range(REGISTERS),ref.append);enc=lambda z:_encode_body([({"^":1,"&":2,"|":3}[a],b,c,d)for a,b,c,d in z]);assert m==0 and enc(ref)==enc(p.recs);assert max(max(x[1:])for x in p.recs)<REGISTERS and all(x[0]in "^&|"for x in p.recs)
	for xs in[[r.getrandbits(256)for _ in range(256)]for _ in range(8)]+[[0]*256,[ALL]*256]:assert lanes_of(list(p.step(*pack_lanes(xs,256,p.pin))),256,p.pin)==[f_scalar(x)^p.qint for x in xs]
	for _ in range(10000):w=[r.getrandbits(32)for _ in range(8)];assert enc_invert(enc_words(w))==state_words(w)
	regs=[0]*REGISTERS
	for j in range(256):regs[INREG(j)]=r.getrandbits(256)
	a=list(regs);assert p.run(0,len(p.recs),regs)==p.kernel;p.fast(a);assert[a[INREG(j)]for j in range(256)]==[regs[INREG(j)]for j in range(256)];cur=[r.getrandbits(256)for _ in range(256)];pl=pack_lanes(cur,256,p.pin)
	for _ in range(4):pl=list(p.step(*pl));cur=[f_scalar(x)^p.qint for x in cur]
	assert lanes_of(pl,256,p.pin)==cur;e=Engine(N_T3);xs=[r.getrandbits(N_T3)for _ in range(256)];pl=pack_lanes(xs,N_T3,e.pin)
	for _ in range(5):pl=list(e.step(*pl));xs=[e.g_scalar(x)for x in xs]
	assert lanes_of(pl,N_T3,e.pin)==xs;xs=[r.getrandbits(256)for _ in range(2)];f=[f_scalar(x)for x in xs];assert packed_f(xs,256)==f==rec().f(xs,False)and packed_f(xs[:1],256)==f[:1];assert rec().f([0,ALL])==[f_scalar(0),f_scalar(ALL)]and packed_f(xs,256,p.qwords)==[x^p.qint for x in f];rows=[r.getrandbits(256)for _ in range(256)];assert transpose(transpose(rows))==rows;assert(transpose(rows)[5]>>9)&1==(rows[9]>>5)&1;xs=[r.getrandbits(256)for _ in range(256)];assert lanes_of(dnet().step(list(p.step(*pack_lanes(xs,256,p.pin)))),256,[0]*256)==[digest_of_state(state_words(words_of(x)))for x in xs];q,found=plan(N_T3),0
	r0,ends,ckok,pairs=r.getrandbits(N_T3),{},True,0
	for t in range(400):
		xx,l=(r0+t)%q["N"],0
		while l<q["cr"]:
			xx,l=e.f2([xx])[0],l+1
			if is_dp(xx,q):
				if xx in ends and pairs<20:aa,bb=recover(q,r0,ends[xx],t,e.f2),recover(q,r0,ends[xx],t,e.f2,3);ckok&=aa==bb and(aa is None or(aa[0]!=aa[1]and e.g_scalar(aa[0])==e.g_scalar(aa[1])));pairs+=aa is not None
				ends.setdefault(xx,t);break
	assert ckok and pairs>0
	for s in range(6):
		z,_=attempt(e,q,"selftest/%d"%s,"t")
		if z is not None:found+=1;assert z[0]!=z[1]and e.g_scalar(z[0])==e.g_scalar(z[1])
	assert found;print(info,h,bt,p.instr,"ok",True);return True
def print_ledger(lg):
	print({k:(str(v)if isinstance(v,Fraction)else v)for k,v in lg["plan"].items()});print("body",lg["body"])
	for k,v in lg["parts"].items():print(k,v)
	print("N =",lg["total"]);print("time %.5f %.8f"%(log2(lg["total"]/UNIT)+5e-6,log2(lg["total"]/UNIT)))

```

## Appendix: native

SHA-256 `d6a55aec18040869b2e3ea806fd7ae5966457113d8769b56e0da674ddfc2ed98`.

```python
"""Exact mixed-radix table on the leader's primitive 256-bit word RAM.

Each emitted 40-bit table record is charged its allowed primitives. JZ includes
a comparison and a branch. All table constants are built from 10-bit
immediates, so there is no uncounted literal pool or multiply/divide opcode.
"""
from dataclasses import dataclass

MASK = (1 << 256) - 1
OPS = ('set', 'add', 'sub', 'and', 'or', 'xor', 'shl', 'shr', 'lt',
       'jz', 'jmp', 'load', 'store', 'ret', 'jif', 'jabs')


class Program:
    def __init__(self):
        self.code = []

    def emit(self, op, d=0, a=0, b=0):
        self.code.append((op, d, a, b))
        return len(self.code) - 1

    def patch(self, at, label):
        op, _, a, b = self.code[at]
        self.code[at] = op, label, a, b

    def const(self, dst, value):
        chunks = []
        while value >= 1024:
            chunks.append(value & 1023)
            value >>= 10
        self.emit('set', dst, value)
        if chunks:
            self.emit('set', 99, 10)
            for chunk in reversed(chunks):
                self.emit('shl', dst, dst, 99)
                self.emit('set', 98, chunk)
                self.emit('or', dst, dst, 98)

    def init(self):
        for r, v in ((0, 0), (1, 1), (2, 256), (3, 255)):
            self.const(r, v)

    def mul(self, dst, x, y):
        # Unsigned shift/add. Inputs copied before dst is overwritten.
        self.emit('or', 40, x, x)
        self.emit('or', 41, y, y)
        self.emit('set', dst, 0)
        top = len(self.code)
        stop = self.emit('jz', 0, 41)
        self.emit('and', 42, 41, 1)
        skip = self.emit('jz', 0, 42)
        self.emit('add', dst, dst, 40)
        self.patch(skip, len(self.code))
        self.emit('shl', 40, 40, 1)
        self.emit('shr', 41, 41, 1)
        self.emit('jmp', top)
        self.patch(stop, len(self.code))

    def div(self, quotient, remainder, x, divisor):
        # Restoring division. The actual divisors are <2^49, so the
        # doubled remainder never overflows the 256-bit word.
        self.emit('or', 43, x, x)
        self.emit('set', quotient, 0)
        self.emit('set', remainder, 0)
        self.emit('set', 44, 256)
        top = len(self.code)
        self.emit('sub', 44, 44, 1)
        self.emit('shl', remainder, remainder, 1)
        self.emit('shr', 45, 43, 44)
        self.emit('and', 45, 45, 1)
        self.emit('or', remainder, remainder, 45)
        self.emit('shl', quotient, quotient, 1)
        self.emit('lt', 46, remainder, divisor)
        take = self.emit('jz', 0, 46)
        join = self.emit('jmp', 0)
        self.patch(take, len(self.code))
        self.emit('sub', remainder, remainder, divisor)
        self.emit('or', quotient, quotient, 1)
        self.patch(join, len(self.code))
        stop = self.emit('jz', 0, 44)
        self.emit('jmp', top)
        self.patch(stop, len(self.code))

    def address(self, bits):
        # r10 = block index. Compute bits*r10 with constant shifts/adds.
        self.emit('set', 30, 0)
        for bit in range(bits.bit_length()):
            if (bits >> bit) & 1:
                self.emit('set', 31, bit)
                self.emit('shl', 32, 10, 31)
                self.emit('add', 30, 30, 32)
        self.emit('set', 31, 8)
        self.emit('shr', 33, 30, 31)
        self.emit('and', 34, 30, 3)
        self.emit('sub', 35, 2, 34)
        self.emit('add', 36, 33, 1)
        self.emit('set', 37, bits)
        self.emit('shl', 38, 1, 37)
        self.emit('sub', 38, 38, 1)

    def read_block(self, bits):
        self.address(bits)
        self.emit('load', 14, 33)
        self.emit('load', 39, 36)
        self.emit('shr', 14, 14, 34)
        self.emit('shl', 39, 39, 35)
        self.emit('or', 14, 14, 39)
        self.emit('and', 14, 14, 38)

    def write_block(self, bits):
        self.address(bits)
        self.emit('set', 47, 0)
        self.emit('sub', 47, 47, 1)
        for address, shift, direction in ((33, 34, 'shl'), (36, 35, 'shr')):
            self.emit(direction, 48, 38, shift)
            self.emit('xor', 48, 48, 47)
            self.emit('load', 49, address)
            self.emit('and', 49, 49, 48)
            self.emit(direction, 50, 14, shift)
            self.emit('or', 49, 49, 50)
            self.emit('store', address, 49)

    def packed(self):
        out = bytearray()
        for op, d, a, b in self.code:
            assert 0 <= max(d, a, b) < 1024
            word = OPS.index(op) | (d << 4) | (a << 14) | (b << 24)
            out.extend(word.to_bytes(5, 'little'))
        assert len(self.code) < 1024
        return bytes(out)



@dataclass(frozen=True)
class Layout:
    group: int
    tp: int
    key_bits: int = 48

    @property
    def fb(self): return (self.tp - 1).bit_length()

    @property
    def radix(self): return (self.tp << (self.key_bits - self.fb)) + 1

    @property
    def bits(self): return (self.radix ** self.group - 1).bit_length()

    def groups(self, slots): return (slots + self.group - 1) // self.group

    def words(self, slots):
        # Full final word plus a guard word for every two-word read.
        return (self.groups(slots) * self.bits + 255) // 256 + 1

    def table_bytes(self, slots): return 32 * self.words(slots)

    def digit(self, legacy_key):
        h, f = divmod(legacy_key, 1 << self.fb)
        if not 0 <= f < self.tp or not 0 <= h < 1 << (self.key_bits - self.fb):
            raise ValueError('not a valid distinguished-point key')
        return h * self.tp + f + 1

    def key(self, digit):
        if not 0 < digit < self.radix:
            raise ValueError('invalid digit')
        h, f = divmod(digit - 1, self.tp)
        return (h << self.fb) | f

    def programs(self):
        assert 1 <= self.group <= 5 and self.bits < 256
        scan = Program(); scan.init(); scan.const(60, self.radix)
        scan.const(10, 0); scan.const(15, 0)
        top = len(scan.code)
        scan.emit('lt', 25, 15, 11)
        stops = [scan.emit('jz', 0, 25)]
        scan.read_block(self.bits)
        for _ in range(self.group):
            scan.div(14, 24, 14, 60)
            scan.emit('lt', 25, 15, 11)
            stops.append(scan.emit('jz', 0, 25))
            scan.emit('xor', 25, 24, 12)
            stops.append(scan.emit('jz', 0, 25))
            scan.emit('add', 15, 15, 1)
        scan.emit('add', 10, 10, 1); scan.emit('jmp', top)
        for stop in stops: scan.patch(stop, len(scan.code))
        scan.emit('ret')

        insert = Program(); insert.init(); insert.const(60, self.radix)
        insert.const(61, self.group); insert.div(10, 62, 15, 61)
        insert.read_block(self.bits)
        for i in range(self.group):
            insert.div(14, 70+i, 14, 60)
            insert.const(63, i); insert.emit('xor', 64, 62, 63)
            replace = insert.emit('jz', 0, 64); skip = insert.emit('jmp', 0)
            insert.patch(replace, len(insert.code)); insert.emit('or', 70+i, 12, 12)
            insert.patch(skip, len(insert.code))
        insert.const(14, 0)
        for i in reversed(range(self.group)):
            insert.mul(14, 14, 60); insert.emit('add', 14, 14, 70+i)
        insert.write_block(self.bits); insert.emit('ret')

        key = Program(); key.init(); key.const(60, self.tp)
        key.const(61, self.fb); key.const(62, (1 << self.fb)-1)
        key.emit('and', 63, 12, 62); key.emit('shr', 64, 12, 61)
        key.mul(12, 64, 60); key.emit('add', 12, 12, 63)
        key.emit('add', 12, 12, 1); key.emit('ret')
        return dict(scan=scan, insert=insert, key=key)

    def costs(self, slots):
        programs = self.programs()
        # Every loop iteration in division executes <=14 records, <=8 in
        # multiplication. These deliberately round to 16 and 10, including
        # setup and exits. Driver and address code are charged again per block.
        div_bound, mul_bound = 16*256+16, 10*256+16
        groups = self.groups(slots)
        return dict(code_bytes=sum(len(p.packed()) for p in programs.values()),
                    scan=groups*(self.group*(div_bound+8)+80)+40,
                    insert=div_bound+self.group*(div_bound+mul_bound+16)+240,
                    key=mul_bound+40, clear=5*self.words(slots)+10,
                    registers=100, div_bound=div_bound, mul_bound=mul_bound)


```

## Appendix: arena

SHA-256 `99a498b583c55de54fa0d5b812ae0685eba3017c152c9d491bfcbe564c13fc64`.

```python
"""One physical arena for native search, table access, and recovery."""
ARENA_BYTES=1<<20
BODY_SIZE=43541*4
LIVE_CODE_SIZE=404*5+1279*5
REG_BYTES=887*32
COUNTER_BYTES=16384
REC_ARRAY_BYTES=2048
REC_POOL_BYTES=993344
COUNTER_BASE=1001760
ARRAY_BASE=1018144
REG_BASE=1020192
POINTER2=886
_BODY_IMAGE=[]


def encode_recovery(records):
    output=bytearray()
    for op,x,y,z in records:
        if op=='S':
            value=rec().imm[y]
            assert z==0 and x<128 and value==_rep(value&M32)
            word=(1<<39)|(x<<32)|(value&M32)
        else:
            flags=0
            if op in ('+','&','|','^'):
                name={'+':'add','&':'and','|':'or','^':'xor'}[op];d,a,b=x,y,z
            elif op in ('<','>'):name='shl' if op=='<' else 'shr';d,a,b=x,y,z;flags=2
            elif op=='L':name='load';d,a,b=x,884+z,y;flags=1
            elif op=='T':name='store';d,a,b=884+z,y,x;flags=1
            elif op=='R':name='set';d,a,b=884+x,y,0
            elif op=='A':name='add';d,a,b=884+x,884+x,y;flags=2
            elif op=='C':name='lt';d,a,b=127,884+x,884+y
            elif op=='J':name='jif';d,a,b=x,127,0
            else:raise ValueError(op)
            assert max(d,a,b)<1024
            word=OPS.index(name)|(d<<4)|(a<<14)|(b<<24)|(flags<<34)
        output.extend(word.to_bytes(5,'little'))
    return bytes(output)


class Arena:
    def __init__(self,p,mutation=None,native=False):
        self.p=p;self.mutation=mutation;self.native=native
        self.data=bytearray(ARENA_BYTES);self.phase='setup';self.reason=None
        self.layout=Layout(5,p['Tp'],p['kb']+p['fb'])
        self.slots=p['tmax']+LANES+min(p['cmax'],7)
        self.table_size=self.layout.table_bytes(self.slots)
        self.programs=self.layout.programs();self.entries={};self.calls=0;self.operations=0
        self.high_slot=0;self.trace=[]
        if mutation=='zero_digit':
            program=self.programs['key']
            i=len(program.code)-2
            assert program.code[i]==('add',12,12,1)
            program.code[i]=('or',12,12,12)
        if mutation=='decrement_scan':
            program=self.programs['scan']
            i=next(i for i,r in enumerate(program.code) if r==('add',15,15,1))
            program.code[i]=('sub',15,15,1)
        if mutation=='wrong_shift':
            program=self.programs['scan']
            i=next(i for i,r in enumerate(program.code) if r[0]=='shr' and r[1]==14)
            op,d,a,b=program.code[i];program.code[i]=('shl',d,a,b)
        if mutation=='wrong_radix':
            self.programs=Layout(5,p['Tp']-1,p['kb']+p['fb']).programs()
        if not _BODY_IMAGE:_BODY_IMAGE.append(_encode_body([({'^':1,'&':2,'|':3}[op],d,a,b) for op,d,a,b in prog().recs]))
        body=_BODY_IMAGE[0]
        assert len(body)==BODY_SIZE
        self.body_start=self.table_size
        self.data[self.body_start:self.body_start+BODY_SIZE]=body
        at=self.body_start+BODY_SIZE
        for name,program in self.programs.items():
            image=program.packed();self.entries[name]=(at,len(image));self.data[at:at+len(image)]=image;at+=len(image)
        assert at<=REC_POOL_BYTES
        self.dead_padding=REC_POOL_BYTES-at
        # RecProg records are real encoded instructions. The inherited controller
        # byte allowance has canaries, not fabricated executable instructions.
        # Its source control flow executes below; its 1,279-record allowance is
        # the explicitly retained legacy accounting assumption.
        recovery=rec().init+rec().flat
        if mutation=='clobbered_constant':
            recovery=[(op,5 if op=='S' and d==32 else d,
                       5 if i>=len(rec().init) and a==32 else a,
                       5 if i>=len(rec().init) and b==32 else b)
                      for i,(op,d,a,b) in enumerate(recovery)]
        retained=encode_recovery(recovery)
        retained+=bytes([0xA7])*(LIVE_CODE_SIZE-len(retained))
        self.data[REC_POOL_BYTES:REC_POOL_BYTES+LIVE_CODE_SIZE]=retained
        self.retained_hash=hashlib.sha256(retained).digest();self.body_hash=hashlib.sha256(body).digest()
        self.codec_hash=hashlib.sha256(self.data[self.body_start+BODY_SIZE:at]).digest()
        self.retpc=REC_POOL_BYTES+LIVE_CODE_SIZE-5
        self.callers={}
        self.link_caller('query_key','key',((12,100),))
        self.link_caller('scan','scan',((12,12),(11,102)))
        self.link_caller('insert_key','key',((12,100),))
        self.link_caller('insert','insert',((12,12),(15,101)))
        self.trace.append('setup')

    def link_caller(self,site,name,mapping):
        if self.phase!='setup':raise ValueError('caller linked after setup')
        address=REC_POOL_BYTES+LIVE_CODE_SIZE-256+32*len(self.callers)
        target=self.entries[name][0];retpc=address+5*(len(mapping)+2)
        assert len(self.callers)<8 and target<1<<20 and retpc<1<<20
        records=[('or',dst,src,src) for dst,src in mapping]
        records+=[('set',POINTER2,retpc&1023,retpc>>10),('jabs',target&1023,target>>10,0)]
        image=b''.join((OPS.index(op)|(d<<4)|(a<<14)|(b<<24)).to_bytes(5,'little') for op,d,a,b in records)
        self.data[address:address+len(image)]=image
        self.callers[site]=(address,len(records),retpc,mapping)
        self.retained_hash=hashlib.sha256(self.data[REC_POOL_BYTES:REC_POOL_BYTES+LIVE_CODE_SIZE]).digest()

    def reg(self,index,value=None):
        if not 0<=index<887:raise ValueError('register field')
        at=REG_BASE+32*index
        if value is None:return int.from_bytes(self.data[at:at+32],'little')
        self.data[at:at+32]=(value&ALL).to_bytes(32,'little')

    def word(self,at,value=None):
        if at<0 or at+32>ARENA_BYTES or at%32:raise ValueError('unaligned or out-of-arena word')
        if value is None:return int.from_bytes(self.data[at:at+32],'little')
        self.data[at:at+32]=(value&ALL).to_bytes(32,'little')

    def scalar(self,index,value=None):
        # Main scalar state shares the recovery array before recovery starts.
        if not 0<=index<32:raise ValueError('scalar slot')
        if self.phase in ('recovery','done'):return self.reg(128+index,value)
        return self.word(ARRAY_BASE+1024+32*index,value)

    def trail(self,lane,value=None):
        if self.phase!='search':raise ValueError('trail access after search')
        at=ARRAY_BASE+32*(lane>>3);shift=18*(lane&7);word=self.word(at)
        if value is None:return (word>>shift)&((1<<18)-1)
        if not 0<=value<1<<18:raise ValueError('trail field overflow')
        self.word(at,(word&~(((1<<18)-1)<<shift))|(value<<shift))

    def birth(self,lane,value=None):return self.word(COUNTER_BASE+8192+32*lane,value)

    def planes(self,values=None):
        if self.phase!='search':raise ValueError('planes after search')
        if values is None:return [self.word(COUNTER_BASE+32*i) for i in range(self.p['n'])]
        for i,value in enumerate(values):self.word(COUNTER_BASE+32*i,value)

    def begin(self,seed):
        if self.phase!='setup':raise ValueError('setup did not exit once')
        self.phase='search';self.trace.append('search');self.scalar(0,seed)
        for lane in range(LANES):self.trail(lane,lane);self.birth(lane,0)
        self.high_slot=LANES

    def body_fetch(self):
        if self.phase!='search':raise ValueError('fetch of dead body')
        if hashlib.sha256(self.data[self.body_start:self.body_start+BODY_SIZE]).digest()!=self.body_hash:
            raise ValueError('search body overwritten')

    def body_step(self):
        self.body_fetch()
        for pc in range(self.body_start,self.body_start+BODY_SIZE,4):
            raw=int.from_bytes(self.data[pc:pc+4],'little')
            op=raw&3;d=(raw>>2)&1023;a=(raw>>12)&1023;b=(raw>>22)&1023
            if op>2 or max(d,a,b)>=884:raise ValueError('body instruction encoding')
            x,y=self.reg(a),self.reg(b)
            self.reg(d,x^y if op==0 else x&y if op==1 else x|y)
        return [self.reg(INREG(j)) for j in range(256)]

    def retained_fetch(self):
        if hashlib.sha256(self.data[REC_POOL_BYTES:REC_POOL_BYTES+LIVE_CODE_SIZE]).digest()!=self.retained_hash:
            raise ValueError('live code overwritten')

    def handoff(self,t0,t1):
        if self.phase!='search':raise ValueError('recovery entered outside search')
        self.retained_fetch();seed=self.scalar(0)
        self.reg(128,seed);self.reg(129,t0);self.reg(130,t1)
        self.phase='recovery';self.trace.append('recovery')
        # Reuse the main trail-ID/scalar array only after preserving these words.
        self.data[ARRAY_BASE:ARRAY_BASE+REC_ARRAY_BYTES]=bytes(REC_ARRAY_BYTES)
        for index in (884,885,886):self.reg(index,0)
        self.rec_ready=False;self.rec_last=None;self.rec_meter=[]
        return seed,t0,t1

    def rec_execute(self,start,records):
        pc=start;end=start+records*5;flag=False;count=0
        while pc<end:
            raw=int.from_bytes(self.data[pc:pc+5],'little');pc+=5;count+=1
            if raw>>39:self.reg((raw>>32)&127,_rep(raw&M32));continue
            if raw>>36 or (raw&15)>=len(OPS):raise ValueError('recovery instruction encoding')
            op=OPS[raw&15];x=(raw>>4)&1023;y=(raw>>14)&1023;z=(raw>>24)&1023;flags=(raw>>34)&3
            right=z if flags&2 else self.reg(z)
            if op=='xor':self.reg(x,self.reg(y)^right)
            elif op=='and':self.reg(x,self.reg(y)&right)
            elif op=='or':self.reg(x,self.reg(y)|right)
            elif op=='add':self.reg(x,self.reg(y)+right)
            elif op=='shr':self.reg(x,self.reg(y)>>right)
            elif op=='shl':self.reg(x,self.reg(y)<<right)
            elif op=='set':self.reg(x,y|(z<<10))
            elif op in ('load','store'):
                index=self.reg(y if op=='load' else x)+z
                if flags!=1 or not 0<=index<64:raise ValueError('recovery array boundary')
                if op=='load':self.reg(x,self.word(ARRAY_BASE+32*index))
                else:self.word(ARRAY_BASE+32*index,self.reg(y))
            elif op=='lt':self.reg(x,int(self.reg(y)<right))
            elif op=='jif':
                if self.reg(y):pc=start+5*x
            else:raise ValueError('unsupported recovery opcode')
            if not start<=pc<=end:raise ValueError('recovery branch escaped')
        return count

    def rec_step(self,values):
        if self.phase!='recovery':raise ValueError('recovery step before handoff')
        rp=rec();initial=seed=0
        if not self.rec_ready:
            initial=self.rec_execute(REC_POOL_BYTES,len(rp.init))
            self.rec_ready=True
        # This is the test mirror's explicit reload at entry and probe boundaries.
        # Consecutive loop calls already have their input in the output registers.
        if tuple(values)!=self.rec_last:
            for k in range(8):self.reg(rp.fin[k],sum(((v>>(32*(7-k)))&M32)<<(128*lane) for lane,v in enumerate(values)))
            seed=48
        for index in (3,4,7,8):
            if not(self.mutation=='missing_zero_clear' and index==3):self.reg(index,0)
        inner=self.rec_execute(REC_POOL_BYTES+5*len(rp.init),len(rp.flat))
        assert inner==rp.ops
        for k in range(8):self.reg(rp.fin[k],self.reg(rp.fin[k])^_rep(prog().qwords[7-k]))
        # The first two head inputs feed rotations before a mask. The other six
        # are masked by the head itself. Keep chained calls in that same domain.
        for index in rp.fin[:2]:
            if self.mutation!='missing_output_mask':self.reg(index,self.reg(index)&RMASK)
        output=[sum(((self.reg(rp.fin[k])>>(128*lane))&M32)<<(32*(7-k)) for k in range(8)) for lane in range(len(values))]
        self.rec_last=tuple(output)
        if len(self.rec_meter)<16:self.rec_meter.append(dict(initial=initial,seed=seed,inner=inner,clears=4,polarity=8))
        return output

    def finish(self,reason):
        if self.phase not in ('search','recovery'):raise ValueError('terminal transition twice')
        self.retained_fetch();self.phase='done';self.reason=reason;self.trace.append(reason)

    def checkpoint(self,lane,index,value=None):
        if self.phase!='recovery' or lane not in (0,1) or not 0<=index<=self.p['kchk']:
            raise ValueError('checkpoint lifetime or index')
        at=64*index+32*lane
        if self.mutation=='overwrite_live' and index==self.p['kchk']:at+=64
        if at+32>REC_POOL_BYTES and self.mutation!='overwrite_live':raise ValueError('checkpoint boundary')
        return self.word(at,value)

    def native_call(self,name,args,site=None):
        if self.phase!='search':raise ValueError('fetch of dead decoder')
        start,size=self.entries[name];pc=start;count=0
        site=site or ('query_key' if name=='key' else name)
        call_at,caller,retpc,mapping=self.callers[site]
        # These source values are outputs of the separately charged legacy
        # handler. Every new argument move/set/branch is decoded below.
        for dst,src in mapping:self.reg(src,args[dst])
        for i in range(caller):
            raw=int.from_bytes(self.data[call_at+5*i:call_at+5*i+5],'little')
            if raw>>34:raise ValueError('caller encoding')
            op=OPS[raw&15];d=(raw>>4)&1023;a=(raw>>14)&1023;b=(raw>>24)&1023
            if op=='or':self.reg(d,self.reg(a)|self.reg(b))
            elif op=='set':self.reg(d,a|(b<<10))
            elif op=='jabs':pc=d|(a<<10)
            else:raise ValueError('caller opcode')
        if pc!=start:raise ValueError('caller entry mismatch')
        while True:
            if not start<=pc<start+size or (pc-start)%5:raise ValueError('native branch target')
            raw=int.from_bytes(self.data[pc:pc+5],'little');pc+=5;count+=1
            if raw>>34 or (raw&15)>=len(OPS):raise ValueError('native instruction encoding')
            op=OPS[raw&15];d=(raw>>4)&1023;a=(raw>>14)&1023;b=(raw>>24)&1023
            if op=='jz':count+=1  # comparison plus conditional branch
            if op=='set':self.reg(d,a|(b<<10))
            elif op=='add':self.reg(d,self.reg(a)+self.reg(b))
            elif op=='sub':self.reg(d,self.reg(a)-self.reg(b))
            elif op=='and':self.reg(d,self.reg(a)&self.reg(b))
            elif op=='or':self.reg(d,self.reg(a)|self.reg(b))
            elif op=='xor':self.reg(d,self.reg(a)^self.reg(b))
            elif op=='shl':self.reg(d,self.reg(a)<<self.reg(b) if self.reg(b)<256 else 0)
            elif op=='shr':self.reg(d,self.reg(a)>>self.reg(b) if self.reg(b)<256 else 0)
            elif op=='lt':self.reg(d,int(self.reg(a)<self.reg(b)))
            elif op=='jz':
                if self.reg(a)==0:pc=start+5*d
            elif op=='jmp':pc=start+5*d
            elif op=='jif':
                if self.reg(a):pc=start+5*d
            elif op in ('load','store'):
                address=32*self.reg(a if op=='load' else d)
                if address<0 or address+32>self.table_size:raise ValueError('native table access escaped')
                if op=='load':self.reg(d,self.word(address))
                else:self.word(address,self.reg(a))
            elif op=='ret':
                pc=self.reg(POINTER2)
                if pc!=retpc:raise ValueError('return escaped retained control')
                self.retained_fetch();self.operations+=count+caller;self.calls+=1
                return count,caller
            if count>20_000_000:raise ValueError('native execution cap')

    def block(self,group,value=None):
        if self.phase!='search':raise ValueError('table after handoff')
        bit=group*self.layout.bits;at=bit//8;shift=bit%8;length=(shift+self.layout.bits+7)//8
        if at+length>self.table_size:raise ValueError('table block boundary')
        old=int.from_bytes(self.data[at:at+length],'little');mask=(1<<self.layout.bits)-1
        if value is None:return (old>>shift)&mask
        if not 0<=value<self.layout.radix**5:raise ValueError('invalid packed block')
        self.data[at:at+length]=((old&~(mask<<shift))|(value<<shift)).to_bytes(length,'little')

    def find(self,key):
        digit=self.layout.digit(key)
        if self.native:
            self.native_call('key',{12:key});self.native_call('scan',{12:self.reg(12),11:self.high_slot})
            index=self.reg(15);return index if index<self.high_slot else None
        for group in range(self.layout.groups(self.high_slot)):
            block=self.block(group)
            for i in range(5):
                block,value=divmod(block,self.layout.radix);index=5*group+i
                if index>=self.high_slot:return None
                if value==digit:return index
        return None

    def insert(self,slot,key):
        if not 0<=slot<self.slots:raise ValueError('slot overflow')
        digit=self.layout.digit(key)
        if self.native:
            self.native_call('key',{12:key},'insert_key');self.native_call('insert',{12:self.reg(12),15:slot})
        else:
            group,i=divmod(slot,5);value=self.block(group);power=self.layout.radix**i
            old=(value//power)%self.layout.radix;self.block(group,value+(digit-old)*power)
        self.high_slot=max(self.high_slot,slot+1)

    def snapshot(self):return bytes(self.data)

    def restore(self,blob):
        if len(blob)!=ARENA_BYTES:raise ValueError('truncated arena')
        self.data[:]=blob;self.retained_fetch()
        if self.phase=='search':
            self.body_fetch()
            end=self.body_start+BODY_SIZE+sum(size for _,size in self.entries.values())
            if hashlib.sha256(self.data[self.body_start+BODY_SIZE:end]).digest()!=self.codec_hash:
                raise ValueError('decoder corrupted')
            packed=int.from_bytes(self.data[:self.table_size],'little')
            for _ in range(self.layout.groups(self.slots)):
                value=packed&((1<<self.layout.bits)-1);packed>>=self.layout.bits
                if value>=self.layout.radix**5:raise ValueError('noncanonical packed block')
            if packed:raise ValueError('nonzero table padding')

```

## Appendix: probability

SHA-256 `cc402f129d052ad5b9403859aa97813e24ea9b9db7696a2c8efe6128cbf5fe55`.

```python
def probability_certificate(p=None):           # Lemma 2 in exact rationals and 60-digit decimals (every exp and ln correctly rounded), results moved outward by 1e-40
    p=p or plan(256)
    Tp,B,KAPPA,tmax=p['Tp'],p['B'],p['kappa'],p['tmax']
    N_BITS,S1,D,LANES,SB,TB,CMAX,CUT_HALT_ORDER,KEYB,CK=256,20,122,256,1<<48,18,7,8,48,1
    Nn,FINE,COARSE=1<<256,20000,2000
    from decimal import Decimal as Dm, getcontext, localcontext, ROUND_CEILING, ROUND_FLOOR
    getcontext().prec = 60
    up = lambda x: x * (1 + Dm("1e-40")) + Dm("1e-58")
    upr = lambda x: x * (1 + Dm("1e-40"))
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
    p_start = fd(Fraction(Q << TB, Nn), True)
    p_dp_repeat = fd(Fraction(k * k) * L / Np, True)
    p_same_batch = fd(Fraction(255 * Q, Np), True)
    exp5 = up(Dm(5).exp())
    p_60 = upr((-Dm(300) + (exp5 - 1) * fd(H, True)).exp())
    fresh_exponent = Fraction(108 * Q, 1000 * (1 << S1))
    replay_raw_exponent = Fraction(386 * M, 1000 * (1 << S1))
    replay_exponent = fd(replay_raw_exponent, False) - 256 * upr(Dm(2).ln()) - upr(Dm(60).ln())
    assert fresh_exponent > 1000 and replay_exponent > 1000 and 240 * M <= Q
    exp_minus_1000 = upr(Dm(-1000).exp())
    p_stage_fresh = exp_minus_1000
    p_replay_simple = exp_minus_1000
    residual_actual = p_start + p_dp_repeat + p_same_batch + p_60 + p_stage_fresh + p_replay_simple
    residual_reserve = Dm(2) ** -90
    assert residual_actual < residual_reserve
    residual_slack = residual_reserve - residual_actual
    p_tiny = p_start + p_dp_repeat + p_same_batch + p_60 + residual_reserve
    terms = [pi_up(Q) * shift, delay,                            # collision (no partner), detection delay
             fd(Q * L / Np, True),                               # the partner is on the trail of t
             up(fd(Fraction(M * Q) / Np, True) * EK),            # the partner is on a trail with c free evaluations
             fd(PP, True) * p2,                                  # trail of t too old when the DP is reached
             CK * 2 * fd(PP, True) * ex(-(KR * L - 1) * th) * fd(1 + (KR * L - 1) * th / (1 - th), True),   # P_rec
             fd(PP * L * (Q + (1 << TB)) / Np, True),            # a collision on the rest of the path
             Dm(2) ** -40,                                       # N1 >= k
             up(1 - sum(comb(n2, j) * p ** j * (1 - p) ** (n2 - j) for j in range(CUT_HALT_ORDER))),   # step 6: fresh cut trails, P(Bin(n2, p) >= CMAX + 1)
             fd(Q * L / Np, True),                               # S
             fd(Q / Np, True) * fd(L, True) * ex(-(c - 2) * th / 2) * fd(2 + (c - 1) * th, True) + fd(PP, True) * p2,   # X
             fd(Q * L * H / Np + (Q + (1 << TB)) * L * PP / Np, True),   # J2a
             fd(PP * (1 - th), True) * p2, ex(-(c - 1) * th) * fd(H, True),   # J2b, Y
             fd(Fraction(tmax * (tmax - 1), 2 * Tp) / (1 << min(KEYB - (Tp - 1).bit_length(), N_BITS - D)), True),   # key false match
             up((-qd + (tmax - 59) * (1 + (qu / (tmax - 59)).ln())).exp()),   # table capacity
             p_tiny]
    residual = {"P_start": p_start, "P_DP-repeat": p_dp_repeat,
                "P_same-batch": p_same_batch, "P_60": p_60,
                "fresh exponent": fd(fresh_exponent, False),
                "replay exponent": replay_exponent,
                "P_stage-fresh": p_stage_fresh,
                "P_replay-simple": p_replay_simple,
                "residual actual": residual_actual,
                "2^-90 reserve": residual_reserve,
                "reserve slack": residual_slack, "P_tiny charged": p_tiny}
    return 1 - sum(terms), residual

```

## Appendix: recovery_native

SHA-256 `e6c0ac606e518d8713ff2bdb33bd14bb81392f2e851a796f5d8f70798e5394c9`.

```python
"""Persistent recovery registers and the packed two-lane DP control."""


def persistent_recovery(xs,rp=None):
    rp=rp or rec()
    for index in (3,4,7,8):rp.regs[index]=0
    for k in range(8):
        rp.regs[rp.fin[k]]=sum(((value>>(32*(7-k)))&M32)<<(128*lane) for lane,value in enumerate(xs))
    operations=rp.run(rp.flat)
    result=[sum(((rp.regs[rp.fin[k]]>>(128*lane))&M32)<<(32*(7-k)) for k in range(8)) for lane in range(len(xs))]
    return result,operations


def packed_dp_flags(words,tp,alive):
    # Inputs are the eight raw two-lane output registers after polarity XOR.
    # Every primitive operation below corresponds to one named record.
    rep1=1|(1<<128);guard=(1<<64)|(1<<192)
    mask32=M32|(M32<<128);mask26=((1<<26)-1)*rep1
    mask20=((1<<20)-1)*rep1;mask12=4095*rep1
    count=0
    prefix=words[6]|words[5];count+=1
    prefix&=mask32;count+=1
    scratch=words[4]&mask26;count+=1
    prefix|=scratch;count+=1
    scratch=words[7]&mask20;count+=1
    prefix|=scratch;count+=1
    prefix|=guard;count+=1
    prefix=(prefix-rep1)&ALL;count+=1
    prefix>>=63;count+=1
    prefix&=rep1;count+=1
    window=words[7]&mask32;count+=1
    window|=guard;count+=1
    window=(window-(tp<<20)*rep1)&ALL;count+=1
    window>>=63;count+=1
    window&=rep1;count+=1
    flags=prefix&window;count+=1
    flags&=alive;count+=1
    count+=2  # comparison with zero and branch using the resulting flag
    assert count==19
    return flags,count


def recovery_overhead_bound():
    parts=dict(clear_initial_zero_registers=4,polarity_xor=8,canonical_input_limbs=2,packed_dp=19,
               checkpoint_countdown=3,step_limit_loop=3)
    assert sum(parts.values())==39==RECOVER_EXTRA
    return parts

```

## Appendix: control.py

SHA-256 `4c44c0cb8cc9e3328ca97f04393200d7767243ee841e057d2c3b9a6a1793b5ea`.

```python
"""Live plan, ledger, unified search, and checkpoint recovery."""
KAPPA_256=48
KR=Fraction(1273,100)
TP_256=2135
BATCHES_256=1324410828041367000000000000000000000
EXPECTED_N=57746540188414149168689811531111805080261
LAST_ARENAS=[]
TRACE_ARENAS=False


def live_layout(pr=None):
    pr=pr or prog();filt=stage1_ops(pr.pin,STAGE1_PLANES)
    base=pr.instr*4+rec().instr*5+(filt+LOOP_OPS+HANDLER_CODE+RECOVERY_CODE+SETUP_CODE)*5
    layout=Layout(5,TP_256);added=layout.costs(1)['code_bytes'];code=base+added
    regs=32*(pr.nregs+3);counter=16384;arrays=2048;live=base-pr.instr*4;pad=(-live)%32
    lo,hi=0,200000
    while hi-lo>1:
        mid=(lo+hi)//2
        if layout.table_bytes(mid+LANES+CMAX)+code+regs+counter+arrays+pad<=MEM_LIMIT:lo=mid
        else:hi=mid
    table=layout.table_bytes(lo+LANES+CMAX)
    pool=MEM_LIMIT-regs-counter-arrays-live-pad
    deadpad=pool-table-pr.instr*4-added
    assert deadpad>=0 and pool%64==0
    result=dict(code=code,body=pr.instr*4,added_code=added,retained_code=live,
        registers=regs,counters=counter,arrays=arrays,table=table,tmax=lo,
        slots=lo+LANES+CMAX,pool=pool,kchk=pool//64-1,dead_padding=deadpad,
        live_padding=pad,total_bytes=code+regs+counter+arrays+table+deadpad+pad)
    scratch=43836+GEN_STATE_BYTES+56+GEN_CONSTANT_BYTES+4096
    result['setup_bytes']=code+regs+counter+arrays+deadpad+pad+WASM_EMITTER_INSTR*36+scratch
    return result


def machine_constants(pr=None):
    pr=pr or prog();m=live_layout(pr);filt=stage1_ops(pr.pin,STAGE1_PLANES)
    return pr.kernel,filt,pr.kernel+filt+LOOP_OPS,m['code'],m['tmax']


def table_bytes(tmax):return Layout(5,TP_256).table_bytes(tmax+LANES+CMAX)


def plan(n,kappa=None,Tp=None):
    if n!=256:
        cfg=CFG[n];s1,W=cfg['s1'],cfg['W'];N=1<<n;tp=cfg['Tp'];L=Fraction(1<<(s1+W),tp)
        u=isqrt(2*N*LAMBDA.numerator//LAMBDA.denominator)+2
        num,den=u+INFLIGHT*L+1,CUTLOSS.denominator
        q=-(-(num*den)//(den-CUTLOSS.numerator));B=-(-q//LANES)
        cap=-(-cfg['kappa']*L.numerator//L.denominator);fb=(tp-1).bit_length()
        return dict(n=n,s1=s1,W=W,D=s1+W,Tp=tp,fb=fb,kb=min(KEYB-fb,n-s1-W),
            L=L,N=N,Q=B*LANES,B=B,kappa=cfg['kappa'],Sb=cfg['Sb'],c=cap,
            capr=cap+cfg['Sb'],cr=cap+cfg['Sb'],kchk=KCHK,
            tmax=4*(B*LANES//int(L))+64,e2max=2*B*LANES//(1<<s1)+64,cmax=10**9)
    assert kappa in (None,KAPPA_256) and Tp in (None,TP_256)
    m=live_layout();L=Fraction(1<<122,TP_256);B=BATCHES_256
    c=-(-KAPPA_256*L.numerator//L.denominator)
    cr=-(-(KR*L.numerator)//L.denominator)
    k=m['kchk'];stride=cr//(k+1)+1
    return dict(n=256,s1=20,W=102,D=122,Tp=TP_256,fb=12,kb=36,L=L,N=1<<256,
        Q=256*B,B=B,kappa=KAPPA_256,Sb=1<<48,c=c,capr=c+(1<<48),cr=cr,
        kchk=k,checkpoint_stride=stride,tmax=m['tmax'],
        e2max=2*B*256//(1<<20)+64,cmax=CMAX)


def rec_ops(p,pk):
    D=p['cr']//(p['kchk']+1)+1;probes=p['kchk'].bit_length()+2
    return p['cr']*(pk+RECOVER_EXTRA)+p['kchk']*CHK_OPS+(probes+1)*D*(pk+RECOVER_EXTRA)+probes*PROBE_OPS+600+len(rec().init)


def ledger(p=None,pr=None):
    p=p or plan(256);pr=pr or prog();search_envelopes()
    ph,filt,body,code,_=machine_constants(pr);m=live_layout(pr)
    costs=Layout(5,p['Tp']).costs(p['tmax']+LANES+CMAX)
    emitter=WASM_OPERATOR_FACTOR*WASM_RUN_OPERATORS+1
    parts=dict(main=body*p['B'],slices=-(-p['B']//p['Sb'])*SLICE_OPS,
        stage1_hits=p['e2max']*HIT_OPS,
        events=(p['tmax']+1)*(EVENT_OPS+6*(p['tmax']+LANES+CMAX)),
        cuts=p['cmax']*CUT_OPS,recovery=rec_ops(p,packed_ops()),
        setup=SETUP_FIXED+emitter,offset_search=OFFSET_SEARCH_OPS,selector_search=SELECTOR_SEARCH_OPS,
        radix_events=(p['tmax']+1)*(costs['scan']+costs['insert']+2*costs['key']+16),
        radix_setup=costs['clear']+2*costs['code_bytes']+100)
    assert sum(setup_bound(m).values())<=SETUP_FIXED
    return dict(parts=parts,total=sum(parts.values()),plan=p,body=body,emitter=emitter,memory=m)


def setup_bound(m):
    # Includes relocation of the unchanged emitter's temporary output. The
    # separately charged radix clearing/installation row is retained in full.
    return dict(start_lane_construction=256*2400,plane_clear=256*5,birth_clear=256*5,
        trail_ids=256*20,table_clear=5*(m['table']//32)+10,
        body_relocation=5*((m['body']+31)//32)+17,scalar_initialization=4096,
        plane_register_reload=512,phase_control=2048)


def boundary_test(pr,p):
    stream=_encode_body([({'^':1,'&':2,'|':3}[op],d,a,b) for op,d,a,b in pr.recs])
    assert len(stream)==4*pr.instr and all(max(r[1:])<1024 for r in pr.recs)
    layout=Layout(5,p['Tp']);m=live_layout(pr)
    largest=(((1<<p['kb'])-1)<<p['fb'])|(p['Tp']-1)
    assert layout.key(layout.digit(largest))==largest and layout.radix**5<1<<256
    assert m['slots']<1<<18 and m['total_bytes']==1<<20 and m['table']==table_bytes(p['tmax'])
    assert (m['kchk']+1)*64==m['pool'] and p['cr']//p['checkpoint_stride']<=m['kchk']
    for image in layout.programs().values():assert len(image.packed())==5*len(image.code)
    return dict(body_bytes=len(stream),max_register=max(max(r[1:]) for r in pr.recs),
                table_bytes=m['table'],added_code=m['added_code'],total_bytes=m['total_bytes'])


def recover(p,r,t0,t1,f2,kchk=None,arena=None):
    kchk=kchk or p['kchk'];cap=p['cr'];D=cap//(kchk+1)+1
    if arena is None:
        arena=Arena(dict(p,kchk=kchk));arena.begin(r);arena.handoff(t0,t1)
    if arena.phase!='recovery':raise ValueError('missing recovery handoff')
    if p['n']==256:f2=arena.rec_step
    if arena.mutation=='bad_stride':D=max(1,cap//kchk)
    mask=p['N']-1;xs=[(r+t0)&mask,(r+t1)&mask];lengths=[None,None];ends=[None,None]
    for lane,x in enumerate(xs):arena.checkpoint(lane,0,x)
    for distance in range(1,cap+1):
        xs=f2(xs)
        if distance%D==0:
            for lane in (0,1):arena.checkpoint(lane,distance//D,xs[lane])
        if p['n']==256 and (p['s1'],p['W'])==(20,102):
            alive=sum(1<<(128*i) for i in (0,1) if lengths[i] is None)
            flags,_=packed_dp_flags([arena.reg(rec().fin[k]) for k in range(8)],p['Tp'],alive)
        else:flags=sum(int(is_dp(xs[i],p))<<(128*i) for i in (0,1))
        for lane in (0,1):
            if lengths[lane] is None:
                if (flags>>(128*lane))&1:lengths[lane],ends[lane]=distance,xs[lane]
        if None not in lengths:break
    else:raise Halt('recovery cap')
    long=0 if lengths[0]>=lengths[1] else 1;short=1-long
    lb=lengths[short];q,rem=divmod(abs(lengths[0]-lengths[1]),D)
    def aligned(index):return walk([arena.checkpoint(long,index+q)],rem,f2)[0]
    if ends[0]!=ends[1] or aligned(0)==arena.checkpoint(short,0):return None
    low,high=0,lb//D+1
    while high-low>1:
        mid=(low+high)//2
        if aligned(mid)==arena.checkpoint(short,mid):high=mid
        else:low=mid
    x,y=aligned(low),arena.checkpoint(short,low)
    for _ in range(min(high*D,lb)-low*D):
        fx,fy=f2([x,y])
        if fx==fy:
            if arena.mutation=='same_input':return x,x
            if arena.mutation=='resume_body':arena.body_fetch()
            return x,y
        x,y=fx,fy
    return None


def _search(eng,p,r,cnt,mutation=None):
    n=p['n'];mask=p['N']-1;pin=eng.pin
    arena=Arena(p,mutation,native=n==256);arena.begin(r)
    if TRACE_ARENAS:LAST_ARENAS.append(arena)
    nxt=LANES;arena.scalar(1,nxt)
    for index in (2,3,4):arena.scalar(index,0)
    planes=pack_lanes([(r+t)&mask for t in range(LANES)],n,pin)
    for j,value in enumerate(planes):arena.reg(INREG(j),value)
    cnt['inserts']+=LANES;batches=0
    try:
        while batches<p['B']:
            if mutation=='early_handoff':arena.handoff(0,1)
            arena.body_fetch();planes=[arena.reg(INREG(j)) for j in range(n)]
            planes=arena.body_step() if n==256 else list((yield planes));batches+=1
            arena.reg(884,batches);cnt['batches']+=1;hit=stage1(planes,p['s1'],pin)
            for j,v in enumerate(planes):arena.reg(INREG(j),v)
            while hit:
                hits=arena.scalar(3)+1;arena.scalar(3,hits);cnt['stage1_hits']=hits
                if hits>p['e2max']:raise Halt('stage-1 budget')
                arena.planes(planes)
                lane=(hit&-hit).bit_length()-1;hit&=hit-1;x=lane_value(planes,lane,pin,n)
                if is_dp(x,p):
                    key=dp_key(x,p);finished=arena.scalar(2)+1;arena.scalar(2,finished)
                    cnt['finished']=finished;t0=arena.find(key)
                    if t0 is not None:
                        t1=arena.trail(lane);seed,t0,t1=arena.handoff(t0,t1);cnt['recoveries']+=1
                        result=recover(p,seed,t0,t1,eng.f2,arena=arena)
                        if result is None:raise Halt('recovery found no pair')
                        if result[0]==result[1]:
                            raise ValueError('invalid recovered pair')
                        arena.finish('success');return result
                    if finished>p['tmax']:raise Halt('table full')
                    trail=arena.trail(lane);arena.insert(trail,key)
                    nxt=arena.scalar(1);arena.trail(lane,nxt);nxt+=1;arena.scalar(1,nxt)
                    arena.high_slot=nxt;arena.birth(lane,batches)
                    planes=set_lane(planes,lane,(r+arena.trail(lane))&mask,pin,n);cnt['inserts']+=1
                    for j,value in enumerate(planes):arena.reg(INREG(j),value)
            if batches%p['Sb']==0:
                for lane in range(LANES):
                    if batches-arena.birth(lane)>=p['c']:
                        cuts=arena.scalar(4)+1;arena.scalar(4,cuts);cnt['cut']=cuts
                        if cuts>p['cmax']:raise Halt('cut budget')
                        nxt=arena.scalar(1);arena.trail(lane,nxt);nxt+=1;arena.scalar(1,nxt)
                        arena.high_slot=nxt;arena.birth(lane,batches)
                        planes=set_lane(planes,lane,(r+arena.trail(lane))&mask,pin,n);cnt['inserts']+=1
                        for j,value in enumerate(planes):arena.reg(INREG(j),value)
        arena.finish('batch budget');return None
    except Halt as error:
        arena.finish(str(error) or 'failure');raise
    except BaseException:
        if arena.phase in ('search','recovery'):arena.finish('error')
        raise


def e1_rows(trials):
    # Keep a bounded number of physical one-MiB arenas in the organizer's
    # 128-MiB process. Batching changes only the test mirror's host scheduling.
    rows=[]
    for offset in range(0,len(trials),8):rows.extend(parallel_rows(trials[offset:offset+8]))
    return rows

```

## Appendix: acceptance

SHA-256 `a64fb9f37c4107e32bd06c72563c4d824388fac29197b9a463c9fcfd51aa5edc`.

```python
"""One acceptance gate for the real program and instruction/control mutants."""


def _drive(engine,p,seed,mutation=None,reference=False):
    global TRACE_ARENAS
    counter=Counters();answer=None;TRACE_ARENAS=not reference;LAST_ARENAS[:]=[]
    gen=reference_search(engine,p,seed,counter) if reference else _search(engine,p,seed,counter,mutation)
    try:
        while True:
            planes=gen.send(answer);answer=engine.step(*planes)
    except StopIteration as stop:result=stop.value;reason='success' if result else 'batch budget'
    except Halt as error:result=None;reason=str(error) or 'failure'
    arena=LAST_ARENAS[-1] if LAST_ARENAS else None;TRACE_ARENAS=False
    return result,dict(counter),reason,arena


class ToyEngine:
    def __init__(self,mapping,n=16):self.mapping=mapping;self.n=n;self.pin=[0]*n
    def g(self,x):return self.mapping.get(x,x if x%4 else x+1)&((1<<self.n)-1)
    def f2(self,xs):return [self.g(x) for x in xs]
    def step(self,*planes):return pack_lanes(self.f2(lanes_of(planes,self.n,self.pin)),self.n,self.pin)


def _toy_plan(cap=64,count=64):
    p=plan(16);p.update(B=cap+4,cr=cap,kchk=count,tmax=128,c=10**6,Sb=10**6,cmax=7,e2max=10000)
    return p


def _toy_graph(length):
    a=[1]+[1001+4*i for i in range(5)]
    b=[2]+[2001+4*i for i in range(5)]
    shared=[3001+4*i for i in range(length-len(a))]+[0]
    graph={0:0}
    for path in (a+shared,b+shared):graph.update(zip(path,path[1:]))
    return graph,(a[-1],b[-1])


def _gate_table(mutation):
    p=plan(256);native=Arena(p,mutation,True);mirror=Arena(p,None,False)
    native.begin(17);mirror.begin(17)
    keys=[0,(7<<12)|4,(((1<<36)-1)<<12)|(p['Tp']-1)]
    slots=[0,8,11];costs=native.layout.costs(native.slots)
    for slot,key in zip(slots,keys):
        before=native.operations;native.insert(slot,key);mirror.insert(slot,key)
        assert native.data[:native.table_size]==mirror.data[:mirror.table_size],'native insertion parity'
        assert native.operations-before<=costs['key']+costs['insert']+8,'insertion operation cap'
    native.insert(9,keys[1]);mirror.insert(9,keys[1])
    for key,expected in zip(keys,slots):
        before=native.operations;found=native.find(key)
        assert found==expected,'native lookup/first-match order'
        assert native.operations-before<=costs['key']+costs['scan']+8,'scan operation cap'
    assert native.phase=='search'
    # Reach the same handoff through an actual table match before the last-slot write.
    matched=native.find(keys[0]);seed,t0,t1=native.handoff(matched,1)
    assert (seed,t0,t1)==(17,0,1) and native.scalar(0)==17
    native.checkpoint(1,p['kchk'],ALL);native.retained_fetch()
    assert native.checkpoint(1,p['kchk'])==ALL
    try:native.body_fetch()
    except ValueError:pass
    else:raise AssertionError('dead body fetch accepted')
    try:native.native_call('key',{12:0})
    except ValueError:pass
    else:raise AssertionError('dead decoder fetch accepted')
    native.finish('boundary control')
    return dict(native_records=sum(len(v.code) for v in native.programs.values()),bytes=live_layout()['added_code'])


def _gate_persistent(mutation):
    import random
    rng=random.Random(912);p=plan(256);arena=Arena(p,mutation);arena.begin(1);arena.handoff(0,1)
    xs=None
    for i in range(100):
        if i<4:xs=[rng.getrandbits(256),rng.getrandbits(256)]
        got=arena.rec_step(xs)
        assert got==[f_scalar(x)^prog().qint for x in xs],'persistent recovery parity'
        assert arena.rec_meter[-1]['inner']==1393
        xs=got
    assert sum(item['initial'] for item in arena.rec_meter)==76,'initialization repeated'
    parts=recovery_overhead_bound();assert sum(parts.values())<=39
    # Check the packed DP screen on both lanes, all active masks, boundary windows,
    # and harmless carry bits above the 32-bit output limbs.
    rep1=1|(1<<128)
    values=[0,1,p['Tp']<<20,(p['Tp']-1)<<20,1<<32,1<<121,1<<122,ALL]
    for x in values:
        for y in values:
            words=[((x>>(32*(7-i)))&M32)|(((y>>(32*(7-i)))&M32)<<128) for i in range(8)]
            words[5]|=3<<32;words[5]|=5<<160
            for alive in (0,1,1<<128,rep1):
                flags,count=packed_dp_flags(words,p['Tp'],alive)
                expected=(int(is_dp(x,p))|(int(is_dp(y,p))<<128))&alive
                assert flags==expected and count==19,'packed DP screen'
    arena.finish('persistent control')
    return dict(calls=100,inner=1393,outer_bound=sum(parts.values()))


def _gate_full_width():
    class NativeOnly:
        pin=[0]*256
        def step(self,*planes):raise AssertionError('detached full-width body')
        def f2(self,xs):raise AssertionError('detached full-width recovery')
    engine=NativeOnly();p=plan(256);p['B']=2
    result,counters,reason,arena=_drive(engine,p,7)
    assert result is None and reason=='batch budget' and counters['batches']==2
    values=[7+i for i in range(256)]
    for _ in range(2):values=[f_scalar(x)^prog().qint for x in values]
    planes=[arena.reg(INREG(j)) for j in range(256)]
    assert lanes_of(planes,256,engine.pin)==values,'arena body execution'
    p=plan(256);p.update(B=1,s1=0,W=0,D=0,Tp=1,fb=0,kb=0,tmax=4,cr=2,kchk=2)
    result,counters,reason,arena=_drive(engine,p,7)
    assert result is None and reason=='recovery found no pair'
    assert counters['recoveries']==1 and arena.trace==['setup','search','recovery',reason]
    assert (arena.scalar(0),arena.scalar(1),arena.scalar(2))==(7,0,1)
    assert len(arena.rec_meter)==1 and arena.rec_meter[0]['inner']==1393
    assert hashlib.sha256(arena.data[arena.body_start:arena.body_start+BODY_SIZE]).digest()!=arena.body_hash
    return dict(body_batches=2,body_records=2*43541,forced_native_recovery=True)


def _gate_transitions(mutation):
    checked=[]
    for cap,count in ((64,64),(32,7)):
        graph,expected=_toy_graph(cap);engine=ToyEngine(graph);p=_toy_plan(cap,count)
        result,counters,reason,arena=_drive(engine,p,1,mutation)
        assert result==expected and reason=='success','search/recovery result'
        assert arena.phase=='done' and arena.trace==['setup','search','recovery','success']
        assert arena.scalar(0)==1 and (arena.scalar(1),arena.scalar(2))==(0,1)
        if cap==64:
            assert hashlib.sha256(arena.data[arena.body_start:arena.body_start+BODY_SIZE]).digest()!=arena.body_hash,'body not reused'
        checked.append(reason)
    scenarios=[]
    p=_toy_plan();p['B']=0;scenarios.append((p,ToyEngine({}),'batch budget'))
    p=_toy_plan();p['e2max']=0;scenarios.append((p,ToyEngine({1:0,2:0}),'stage-1 budget'))
    p=_toy_plan();p['tmax']=0;scenarios.append((p,ToyEngine({1:0,2:0}),'table full'))
    p=_toy_plan();p.update(Sb=1,c=1);scenarios.append((p,ToyEngine({}),'cut budget'))
    p=_toy_plan();p['cr']=1;graph,_=_toy_graph(32);scenarios.append((p,ToyEngine(graph),'recovery cap'))
    p=_toy_plan();p['kb']=2;scenarios.append((p,ToyEngine({1:0,2:16,0:0,16:16}),'recovery found no pair'))
    p=_toy_plan();scenarios.append((p,ToyEngine({1:2,2:0,0:0}),'recovery found no pair'))
    for p,engine,expected in scenarios:
        result,counters,reason,arena=_drive(engine,p,1,mutation)
        assert result is None and reason==expected,(reason,expected)
        assert arena.phase=='done' and arena.reason==expected
        try:arena.body_fetch()
        except ValueError:pass
        else:raise AssertionError('body fetch after terminal exit')
        checked.append(reason)
    return checked


def acceptance_gate(mutation=None):
    table=_gate_table(mutation);persistent=_gate_persistent(mutation)
    transitions=_gate_transitions(mutation)
    result=ledger();assert result['total']==EXPECTED_N and result['memory']['total_bytes']==1<<20
    return dict(table=table,persistent=persistent,transitions=transitions,total=result['total'])


def arithmetic_parity():
    import random
    rng=random.Random(47);p=plan(256);counts={}
    for name in ('mul','div'):
        program=Program();program.init()
        if name=='mul':program.mul(12,10,11)
        else:program.div(12,13,10,11)
        program.emit('ret');image=program.packed()
        arena=Arena(p);start,size=arena.entries['key'];assert len(image)<=size
        arena.data[start:start+len(image)]=image;arena.entries['arithmetic']=(start,len(image))
        arena.link_caller('arithmetic','arithmetic',((10,100),(11,101)));arena.begin(0)
        cases=[(0,1),(ALL,1),(ALL,(1<<48)+1),(ALL,ALL if name=='mul' else (1<<48)-1)]
        cases += [(rng.getrandbits(256),rng.randrange(1,1<<48)) for _ in range(12)]
        largest=0
        for a,b in cases:
            count,caller=arena.native_call('arithmetic',{10:a,11:b});largest=max(largest,count)
            if name=='mul':assert arena.reg(12)==a*b&ALL
            else:assert (arena.reg(12),arena.reg(13))==divmod(a,b)
            assert caller==4 and count<=(2576 if name=='mul' else 4112)
        counts[name]=dict(cases=len(cases),maximum_operations=largest)
    return counts


def table_boundary_parity():
    p=plan(256);arena=Arena(p,native=True);mirror=Arena(p);arena.begin(0);mirror.begin(0)
    offsets=set();count=0
    for group in range(64):
        slot=5*group+group%5;key=((group+1)<<12)|(group%p['Tp'])
        arena.insert(slot,key);mirror.insert(slot,key);offsets.add(group*arena.layout.bits%256);count+=1
        assert arena.data[:arena.table_size]==mirror.data[:mirror.table_size],'packed boundary insertion'
    slot=arena.slots-1;key=(((1<<36)-1)<<12)|(p['Tp']-1)
    arena.insert(slot,key);mirror.insert(slot,key);count+=1
    assert arena.data[:arena.table_size]==mirror.data[:mirror.table_size],'last allocated slot'
    assert len(offsets)==64 and not any(arena.data[arena.table_size-32:arena.table_size]),'guard word'
    for key in (p['Tp'],1<<48):
        try:arena.layout.digit(key)
        except ValueError:pass
        else:raise AssertionError('invalid key accepted')
    return dict(insertions=count,bit_offsets=len(offsets),last_slot=slot,guard_zero=True)


def acceptance_suite():
    import random
    result=acceptance_gate();result['native_arithmetic']=arithmetic_parity();result['table_boundaries']=table_boundary_parity();result['full_width']=_gate_full_width();mutants=[]
    for name in ('zero_digit','decrement_scan','wrong_shift','wrong_radix','overwrite_live',
                 'bad_stride','resume_body','same_input','early_handoff','clobbered_constant','missing_zero_clear','missing_output_mask'):
        try:acceptance_gate(name)
        except (AssertionError,ValueError,IndexError,Halt) as error:mutants.append(dict(name=name,rejected=True,reason=str(error)))
        else:raise AssertionError('surviving mutant: '+name)
    # Corruption/truncation are negative controls, separately reported.
    p=plan(256);arena=Arena(p);arena.begin(2);snapshot=arena.snapshot();negative=[]
    for label,blob in [('truncated',snapshot[:-1]),('oversized',snapshot+b'\x00')]:
        try:arena.restore(blob)
        except ValueError:negative.append(label)
        else:raise AssertionError(label)
    for label,at in [('body corruption',arena.body_start),('decoder corruption',arena.entries['scan'][0]),
                     ('retained corruption',REC_POOL_BYTES),('guard corruption',arena.table_size-1)]:
        arena.data[:]=snapshot;bad=bytearray(snapshot);bad[at]^=128
        try:arena.restore(bad)
        except ValueError:negative.append(label)
        else:raise AssertionError(label)
    bad=bytearray(snapshot);size=(arena.layout.bits+7)//8
    bad[:size]=((1<<arena.layout.bits)-1).to_bytes(size,'little')
    try:arena.restore(bad)
    except ValueError:negative.append('noncanonical block')
    else:raise AssertionError('noncanonical block')
    # Exact whole-attempt parity against the independent retained leader search.
    engine=Engine(16);small=plan(16);parity=[]
    for i in range(8):
        seed=derive('official-port-parity',str(i),16)
        expected,c1,_,_=_drive(engine,small,seed,reference=True)
        actual,c2,_,_=_drive(engine,small,seed)
        assert actual==expected and c1==c2,'candidate-order parity'
        if actual is not None:assert actual[0]!=actual[1] and engine.g_scalar(actual[0])==engine.g_scalar(actual[1])
        parity.append(dict(seed=seed,pair=actual,counters=c2))
    # Scratch clobbering between batches must not introduce a hidden zero assumption.
    pr=prog();defined={INREG(i) for i in range(256)}
    for op,d,a,b in pr.recs:assert {a,b}<=defined;defined.add(d)
    rng=random.Random(55);xs=[rng.getrandbits(256) for _ in range(256)]
    registers=[rng.getrandbits(256) for _ in range(REGISTERS)]
    for i,value in enumerate(pack_lanes(xs,256,pr.pin)):registers[INREG(i)]=value
    pr.fast(registers)
    assert lanes_of([registers[INREG(i)] for i in range(256)],256,pr.pin)==[f_scalar(x)^pr.qint for x in xs]
    result.update(mutants=mutants,negative_controls=negative,whole_attempt_parity=parity,
                  kernel_stream_sha256=hashlib.sha256(_encode_body([({'^':1,'&':2,'|':3}[o],d,a,b) for o,d,a,b in pr.recs])).hexdigest())
    return result

```
