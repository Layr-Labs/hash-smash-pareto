# sha256-r44: a 51,004-record bit-sliced birthday walk

This package is a credited derivative of the judged-valid same-design parent `7523902c-ff00-468e-8214-fa0cfdeaa4ef`, the same-round prior entry `5049693c-558b-437a-a5d2-89fbad6b2d28`, `d22ae1b2-2368-460a-b6d4-1e5e37ceb735`, and `95263e47-d61b-43a6-bb46-30ced2488280`. It reimplements the round-44 walk with the exact T2 carry columns, constant-aware selector, recent-XOR cancellation, charged offset search, index-layout table, and compact normative emitter.

The construction is a generic collision search. It assumes only premise H1 below. It claims no differential, structural, or other weakness in SHA-256.

## 1. Target, message family, and collision relation

The target is `sha256-r44-prefix-v1`. SHA-256 executes steps 0 through 43 on both blocks of a padded 64-byte message, with the standard IV, feed-forward, and all 256 output bits.

Write a 256-bit point x as eight big-endian 32-bit words y0 through y7. The first message block is

```text
W0..W7 = 3e73281c 752d8ed2 ad19eff1 7250fceb
          d4095422 44fdb519 43f22c5b d8d6aac4
W8      = y0
W9      = y1
W10..15 = y2..y7 plus dbce7a42 aaf3823d 8d41a28c 7f214e02 6423f959 7e640e8c, respectively, modulo 2^32.
```

The offset map is a bijection. FIPS padding adds `80`, 55 zero bytes, and the 64-bit length 512, so every message has a fixed second block. The prefix is computed from the standard IV so that after its eight steps `a1 = K9-K8`, `a2 = -K9`, and `a3` through `a8` are zero. Steps 8 and 9 then cancel K8 and K9.

Let a_i and e_i be the working words after i steps of block 1. Let T1_i be the T1 value that produces step i. First define the logical walk-B vector `bw` as

```text
e_41, e_42,
X  = e_39 + (~e_42 & e_40) + W_42,
T1_40,
Q  = T1_39 + Maj(a_38,a_37,a_36),
a_38, a_37,
Y  = e_40 + W_43.
```

The physical no-move output order is `out[k] = bw[PERM[k]]` for `PERM = (6,1,7,0,5,4,2,3)`. The proof names f as this permuted eight-word output, matching both the Python generator and `GEN_C`. The inverse first applies the inverse permutation and then the equations below.

This encoding is bijective. Its inverse first recovers `a_39 = Q + Sigma0(a_38)`, then reconstructs the remaining a words, T1 values, and the complete state with the SHA-256 step equations. In particular, `T1_42 = X + (e_42 & e_41) + Sigma1(e_42) + K_42`.

The allocated program leaves a fixed set of output planes complemented. In canonical big-endian hexadecimal,

```text
q = f3adf239ece8a7a904a1ea96542fd7fc7b0d699485609fd06c14347e71be56d4.
```

The output registers already hold `g(x) = f(x) XOR q`. A collision of g gives equal block-1 working states. Feed-forward and the fixed second block then give equal complete digests.

## 2. Search algorithm and probability space

The only random input is one fresh uniform 256-bit word r. Trail t starts at `r+t mod 2^256` and repeatedly applies g. A point is distinguished when its low 32 bits are zero and its next 90-bit field is below `Tp = 1765`. Thus

```text
theta = 1765 / 2^122
L     = 5316911983139663491615228241121378304/1765
B     = 1325321001494000000000000000000000000 batches
Q     = 339282176382464000000000000000000000000 evaluations
c     = 42173806098558237327259600779433030
S     = 2^48
PLAN_TP = 1765
PLAN_TMAX = 115148
PLAN_C = 42173806098558237327259600779433030
PLAN_CMAX = 2
PLAN_CUT_HALT = 3
PLAN_BINOMIAL_FIRST_REJECTED = 3
```

The program advances 256 trails at once. One 256-bit word holds one bit plane across all lanes. After a batch, 31 ORs combine the low 32 physical g planes; the charged comparison and branch complete the stage-1 test. The published q makes this convention explicit. No runtime mask is omitted.

The table has 115,406 index-layout slots. Slot t belongs to trail t and stores a 46-bit key plus one written bit. It stores neither the trail number nor the length. At most 115,148 completed trails are retained. The slot index fits 17 bits.

On a key match, recovery pass 1 recomputes the stored trail length. Pass 2 aligns the trails and advances them until their next values agree. The two predecessors form the collision. Each pass is bounded by `capr = 42173806098558237327259600779433030 + 2^48`; the ledger charges `2 capr + 1` calls. The cut counter permits at most `CMAX = 2` cuts and halts when cut number 3 would occur. The attempt also halts after B batches, a full table, a stage-1 overflow, an overlong recovery, or a false key match that yields no pair.

For a uniformly random function F on 256-bit points, expose outputs by lazy sampling and mark each fresh output distinguished independently with probability theta. Let P_F be the success probability of this exact bounded program with g replaced by F. The proof partitions failure into no useful birthday collision, delayed detection, a same-trail partner, a cut-trail partner, an old partner trail, a second collision on the remaining path, the finished-trail Chernoff overflow, cut number 3, a false key match, table overflow, and the stated early halts.

For fresh evaluations, lazy sampling gives collision hazard 1/2^256. Conditioning on non-DP values replaces the range size by `N' = 2^256(1-theta)`. The no-collision factor is `Pi(m) = product_(i=0)^(m-1)(1-i/N')`. Trail lengths are handled directly by the independent DP lottery. The finished-trail count uses the Chernoff bound for `Binomial(Q,theta)`.

Lemma 2 uses the live cut budget. A cut requires `c = 42173806098558237327259600779433030` consecutive non-DP values. Let `p = exp(-c*theta)` and let `n2 = k + 256 + CMAX`, where k is the certified finished-trail cutoff. Step 6 charges

```text
Pr[Binomial(n2,p) > CMAX]
= 1 - sum from j=0 through CMAX of binom(n2,j) p^j (1-p)^(n2-j),
CMAX = 2.
```

The first rejected count is therefore 3 successes, exactly the program's halt on cut number 3. Appendix B evaluates this same sum with `range(CMAX + 1)` in both the planning mirror and the 60-digit outward-rounded certificate. The detection-delay term sums the first-collision mass over 2,000 early bins and 20,000 bins covering the final 120 mean trail lengths. False keys use the 46 disclosed key bits. All remaining collision and stage-1 terms are union bounds.

The 60-digit outward-rounded evaluation of those formulas gives `P_F >= 0.390000001000`, hence `P_F >= 0.39`. The plan is deterministic and is printed by the shipped `--ledger` mode.

Premise H1 is score-critical and is not proved. It says that this fixed walk g succeeds at least as often as F in this one attempt. Concretely: fresh outputs have the 2^-256 collision hazard; iterates have the first-collision law of a random mapping; a fresh output is distinguished with probability `1765/2^122` independently of collisions; and conditioning on the adaptive history does not lower the hazard of hitting an earlier non-DP value. H1 is limited to this message family and this approximately 2^128-evaluation experiment.

## 3. The 51,004-record kernel

The declared word-RAM has 1,024 256-bit registers: 1,021 data registers and three pointers. A body record is one opcode byte plus three 10-bit register fields, five bytes in all. Every XOR, AND, OR, NOT, move, set, load, store, comparison, branch, and pointer operation costs one word operation. Bit-sliced rotations only rename planes.

The three-word adder carries a pair `(u,U)` with value `1 if U else 2u`. T0 and T1 are the two published nine-gate column templates. For the four stored-polarity masks where every T0 or T1 order costs ten gates, the shipped `SYN` table holds exact nine-gate T2 circuits, or eight gates at bit 30 where u' is dead. The self-test exhausts all 32 Boolean inputs for every T2 circuit.

The selector compares at most 64 first-triple masks at each of 89 multiword decisions and at most `13*13` current and lookahead forms at each of 2670 column decisions. Recent-XOR cancellation removes an XOR when a recent XOR meets one of its operands, or when two recent XORs share a child.

The offset search evaluates exactly 1,641 candidates: 64 endpoint masks, one initial coordinate point, three 192-bit sweeps, and 1,000 fixed-seed perturbations. A structural upper bound for one complete candidate is

```text
2 * 160 * 64 * 32 * 13 * 13 * 12 * 1024 < 2^41 operations.
```

The ledger charges `2^48` per candidate, including all remaining construction and comparison work. The complete selector search has structural bound

```text
2 * 89 * 64 * 32 * 13 * 13 * 12 * 1024
+ 2670 * 13 * 13 * 12 * 1024 < 2^41,
```

and is charged another `2^48` operations. The searches retain one candidate at a time and have the memory bounds in Section 6.

The final body has 40,046 XOR, 6,687 AND, and 4,271 OR records, with 0 moves. Total: 51,004 records. One batch costs `51004 + 34 + 3 = 51041` operations.

## 4. Normative compact emitter

`experiments/bssha.py` embeds the normative freestanding C source as `GEN_C`. It is 19,791 bytes with SHA-256 `3bc61352a5b1433a61826661358ba29ba158421cdd08d1a0517b7d164a716476`. The source performs the bounded two-pass build, online allocation, and direct five-byte emission. It reports 51,261 nodes, 216,518 helper calls, 1021 registers, and 51,004 records.

The participant build used Ubuntu clang 18.1.3 and LLD 22.1.2:

```sh
clang-18 --target=wasm32 -Oz -ffreestanding -fno-builtin -nostdlib -c emitter.c -o emitter.o
wasm-ld --no-entry --allow-undefined --strip-all emitter.o -o emitter.wasm
```

The stripped module has 5,142 static instructions, 15,562 bytes, and SHA-256 `9e5d1772d1a714f8eb2f1c3d1f7f8a9aca9905b7e95318f73b926ab154c8527a`. Wasmtime 49.0.0 reports exactly 105,819,482 executed operators for `run`. Charging two word operations per fuel unit plus one gives `211638965` operations. The emitter outputs 255,020 SLP bytes with SHA-256 `2239f3f926c796f25332176e8f8e82b619602f2f1dac5a934311f7563a5cfc18`.

The organizer runs `BGen` and `BoundedEmitter`, the packaged byte-exact Python mirror. Before every request it checks all 15 C fields, the embedded C source hash, q, the SLP hash, and every emitted byte. The native and wasm measurements are participant-run accounting.

## 5. Exact operation ledger

```text
main                                             67645709237255254000000000000000000000000
slices                                           6121031866052106806819900
stage1_hits                                      442373610041522979736328125179200
events                                           80170182928
cuts                                             8400
recovery                                         166417838864910804494477084933742987643
setup                                            212452565
offset_search                                    461900436782186496
selector_search                                  281474976710656
total N                                          67812127518493780967049785055360816527788
```

The organizer contract gives `reference_operation_cost = 3232` for this target. Therefore

```text
log2(N / 3232) = 123.98045562070868695849688211191586828431171172704561115683276896310805357118884.
```

The upward-rounded claim is `123.98046`. At precision 1/100000 bit, the integer certificate is

```text
2^12398045 * 3232^100000 <= N^100000
N^100000 < 2^12398046 * 3232^100000.
```

## 6. Memory and preprocessing

Search memory is

```text
body code             51004 * 5 = 255,020
other code            1,766 * 36 = 63,576
table                 ceil(115406 * 47 / 8) = 678,011
counters and copies   16,384
register file         32,768
recovery arrays       2,816
total                 1,048,575 bytes
```

The emitter image is `5142 * 36 = 185,112` bytes. Scratch is `51261 + 23532 + 2759 + 658 + 4096 = 82,306` bytes for use counts, named state arrays, choices, constants, and stack. Setup peaks at 637,982 bytes.

The count-only offset and selector searches peak at 507,890 and 510,601 bytes. They execute sequentially, so peaks do not add. The overall peak is 1,048,575 bytes and the claim rounds memory upward to 20 bits.

Preprocessing consists of setup `212452565`, offset search `461900436782186496`, and selector search `281474976710656` operations:

```text
preprocessing = 462181911971349717
log2(preprocessing / 3232) = 47.023026929689178079578385652472532077041911107125203020399425201821341454156273
```

The upward-rounded preprocessing claim is `47.02303`. Its integer certificate uses exponents 4702302 and 4702303 at precision 1/100000 bit. There is no nonuniform advice.

## 7. Experiments and checks

All declared experiments run the packaged Python mirror before processing a request. `bssha-n16` executes the complete 256-lane search at width 16 and returns only distinct messages whose complete round-44 digests agree in the low 16 bits. `proj-k0-w256` evaluates 256 full-width points, reconstructs the complete two-block digest, and returns a pair only on a low-16 match. The organizer recomputes every returned pair event.

`h1-law-n20` and `h1-law-n22` probe H1 at two reduced widths without treating dependent orbits as independent functions. The source commits both statistics, bins, null constructions, and acceptance rules before an organizer holdout nonce is chosen. The width-20 request retains the committed `h1-shared-v2` domain from the prior package. Width 22 uses the disjoint `h1-shared-v2/22` domain. Each request hashes all 256 organizer seeds to select one coordinate injection, one fixed assignment for the other input bits, one w-coordinate output projection, and one output XOR constant. This defines one fixed function per request:

```text
h_w(x) = project_w(g(inject_w(x))) on w-bit points, w in {20,22}.
```

For each width, the first 64 organizer seeds select 64 starts. All 64 groups iterate the same h_w. Width 20 uses a 1,200-step cap and width 22 uses a 1,700-step cap. Each group records the first output already in that group's visited set. Groups therefore share function values and retain merged tails. Each request keeps one global set of evaluated inputs. It counts the scaled distinguished-point event, low four output bits zero, only once when an input first enters that global set.

Each width has 64 complete null ensembles on `2^w` points. Each ensemble has one shared lazy random mapping, 64 uniform starts, 64 per-group visited sets, one global mapping dictionary, and the observed request's censoring rule. A mapping value sampled for one group is reused by every other group. The null also counts distinguished points only when an input first enters the shared dictionary. Thus both nulls include shared inputs, shared outputs, merged tails, censoring, and dependence among all groups.

Width 20 bins first-collision steps at 400, 700, and 1,000. Width 22 bins them at 550, 950, and 1,400. Values above the last boundary include censored groups. At each width, the first 32 null ensembles estimate each bin's mean and sample variance. For bin counts `b_j`, the committed score is `sum_j (b_j - mean_j)^2 / max(1, variance_j)`. The other 32 ensembles form a calibration set. The collision acceptance limit is 1.25 times the largest calibration score. For distinguished points, `dp_z = (hits - fresh/16) / sqrt(fresh*(1/16)*(15/16))`; its limit is the larger of 4 and 1.25 times the largest absolute calibration `dp_z`. A width passes only when both observed statistics lie within its limits.

At width 20, the same fixed h_20 separately runs the actual distinguished-point table, cut, restart, probe, insertion, and recovery logic for the first 16 organizer seeds. Those table counters are descriptive. Every result row at both widths exports the width, observed bin counts, collision score and limit, DP z-score and limit, number of globally fresh inputs, DP hits, group and null counts, table successes, and `law_pass`. The complete trusted organizer report retains these numeric observations. A judge view binds them by hash but may omit the raw values.

A genuine holdout run requires the organizer to choose an unpredictable `holdout_nonce` after committing the candidate and experiment source, as specified by the organizer experiment contract. A public-seed intake run is a reproducibility check, not a holdout. Passing both widths supports only that two fixed reduced functions, h_20 and h_22, are consistent with their shared-random-mapping ensembles under these tests. It checks whether the same qualitative first-collision and globally-fresh-input DP behavior persists when the state space grows by a factor of four. It does not prove H1, test 256-bit collision rates, estimate the full success probability, or justify extrapolation to width 256.

The shipped self-test checks every emitted record, every T2 truth row, 2,560 full-width lanes, 10,000 inverse round trips, four chained batches, the rolled recovery program, the complete padded digest network, and a width-16 search. These are functional checks. H1 alone supplies the full-width extrapolation.

## 8. Credits and limits

The direct comparison point is `5049693c-558b-437a-a5d2-89fbad6b2d28`. The T2 circuits and index-layout table come through `d22ae1b2-2368-460a-b6d4-1e5e37ceb735`. The constant-aware selector and bounded-emitter structure come through `95263e47-d61b-43a6-bb46-30ced2488280`. `d62a0936-923e-4589-87b7-c479847fda01` supplies same-challenge target, search, recovery, and accounting lineage. The dependency manifest records the ancestry for walk B, constant absorption, five-byte records, the fixed prefix, and two-block messages.

The package does not test the full functional graph, trails beyond 2^40, or the complete 2^128-scale attempt. It does not claim a practical collision or a weakness in deployed full-round SHA-256.

## Appendix. Reproduction

Run `python3 experiments/bssha.py --ledger` for the exact plan, rows, hashes, and memory. Run `python3 experiments/bssha.py --selftest` for the functional checks. Run `python3 experiments/bssha.py --gen-c > emitter.c` to extract the normative emitter. The package source is below the organizer's 64 KiB experiment limit.

## Appendix B. Exact certificate program

This standard-library program independently recomputes the exact ledger, the integer logarithm certificates, and the random-function lower bound with 60-digit outward-rounded decimals.

```python
from fractions import Fraction
from math import log, exp, log2, log1p, comb, expm1

PH, FILT, LOOP, LANES = 51004, 34, 3, 256
INSTR_REC = 51004
PH7, EXTRA, RECINIT = 1926, 47, 106
N_BITS, S1, W, KAPPA = 256, 32, 90, 14          # live plan parameters
HIT, EVENT, CUTOPS, SLICE, GEN_FUEL = 2800, 3800, 4200, 1300, 105819482
GEN_CODE, GEN_SCRATCH = 5142, 82306
OFFSET_EVALS, OFFSET_EVAL_OPS = 1641, 1 << 48
SELECTOR_SEARCH_OPS = 1 << 48
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 2
INSTR, OTHER_CODE, REGFILE, COUNTERS, SLOTB, ADVICE, ARRAYS = 36, 1729, 32768, 16384, 47, 0, 2816
KEYB = 46                                             # key bits (5 bytes)
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
GRAIN, TB = 10 ** 24, 17                       # B is a multiple of GRAIN; trail-number bits of a table entry
FINE, COARSE = 20000, 2000                      # bins of the detection-delay sum (last 120 L batches, earlier part)
body = PH + FILT + LOOP                         # one batch = 51,041 operations
code_bytes = INSTR_REC * 5 + (FILT + LOOP + OTHER_CODE) * INSTR     # the body records once at 5 bytes, every other instruction once at 36 bytes
tmax = 115148
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
assert (Tp, tmax, B, c, CMAX) == (1765, 115148, 1325321001494000000000000000000000000, 42173806098558237327259600779433030, 2)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
emitter = 2 * GEN_FUEL + 1
rows = [("main loop: B * %d" % body, body * B),
        ("slice checks: ceil(B / 2^48) * 1300", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished trails: tmax * (3800 + 6 * (tmax + LANES + CMAX))", tmax * (EVENT + 6 * (tmax + LANES + CMAX))),
        ("cut trails: CMAX * 4200", CMAX * CUTOPS),
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
P, C = 100000, 3232
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
