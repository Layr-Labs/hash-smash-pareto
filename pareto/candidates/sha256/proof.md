# sha256-r64 compression v3: four-byte body records

This package is a credited derivative of `7523902c-ff00-468e-8214-fa0cfdeaa4ef`, the judged-valid 124.13821 round-64 point. It keeps the same 86,375-record Boolean program, search, table semantics, charged offline searches, compact emitter, probability space, and premise H1. It changes the fixed-width body encoding from five bytes to four bytes. The released memory enlarges the full-key index table from 84,827 to 99,529 stored trails.

The exact result is `124.13693720423046990885048791749964405919423128465415038950831959937271239711881`, rounded upward to `124.13694`. This is 0.00126664 bit below the v2 exact bound. The construction remains a generic birthday search and claims no weakness in SHA-256.

## 1. Target and walk

The target is `sha256-r64-prefix-v1`: standard SHA-256 with the fixed IV, all 64 steps on both padded blocks, feed-forward, and all 256 output bits. Messages are the same 64-byte family as v2:

```text
W0..W7 = 3e73281c 752d8ed2 ad19eff1 7250fceb
          d4095422 44fdb519 43f22c5b d8d6aac4
W8      = y0
W9      = y1
W10..15 = y2..y7 plus dbce7a42 aaf3823d 8d41a28c
          ff214e02 6423f959 18000000, modulo 2^32.
```

The offset map is bijective. Padding adds a fixed second block. Walk B is the eight-word encoding

```text
e61, e62,
X = e59 + (~e62 & e60) + W62,
T1_60,
Q = T1_59 + Maj(a58,a57,a56),
a58, a57,
Y = e60 + W63.
```

The inverse reconstructs the entire block-1 state. The allocated program leaves a fixed output polarity mask

```text
q = 83719e5368e5c5064d42d446b413f5fdd5bc79c27182e4541a52bdee6a59c788.
```

The physical output registers already hold `g = f XOR q`. A collision of g gives equal block-1 states and therefore equal complete two-block digests.

## 2. Fixed-width 32-bit body records

The declared machine has 1,024 256-bit registers: 1,021 data registers and three pointers. The body uses only XOR, AND, and OR. Each body record is exactly 32 bits:

```text
bits  0..1   opcode: 0 XOR, 1 AND, 2 OR, 3 reserved
bits  2..11  destination register
bits 12..21  first source register
bits 22..31  second source register
```

Every register field is ten bits and accepts values 0 through 1,023. Opcode 3 is rejected. The emitter rejects moves, sets, out-of-range registers, and excess records. There is no variable-length stream, entropy coding, dictionary, or hidden decoder state. The interpreter and self-test decode this exact layout.

The body has 68,038 XOR, 10,925 AND, and 7,412 OR records. Its fixed code size is `86,375 * 4 = 345,500` bytes, 86,375 bytes below v2. The 1,766 non-body instructions remain 36 bytes each. Total resident program code is 409,076 bytes. Executed operations are unchanged: one batch costs 86,375 body operations, 34 stage-1 operations, and three loop operations, or 86,412 operations for 256 trails.

## 3. Table design and the rejected quotient shortcut

The final package retains the lossless index layout. Slot t belongs to trail number t and therefore implies the start `r+t`. A slot stores the complete 46-bit DP key and one written bit, exactly 47 bits. It stores neither t nor the trail length. Recovery recomputes the stored length.

The key is the 35 bits above bit 121 followed by the exact 11-bit value F, where `F < Tp = 1522`. Boundary checks enforce F below Tp, a key below `2^46`, a slot below `99787 < 2^17`, and at most 99,529 completed trails. Every finished trail scans at most 99,787 slots. The ledger charges six operations per probe and 3,800 fixed operations for extraction, tests, insertion, lane restart, and counters. Thus the complete finished-trail row is `99529 * (3800 + 6 * 99787) = 59968412138` operations.

The exact false-key union bound is

```text
C(99529,2) / (2^35 * 1522)
= 1238240289 / 13073880449024
= 0.000094710999831.
```

This term is charged in the random-function success certificate.

The requested 30–31-bit bucket residual was analyzed but is not used because it cannot preserve both required facts for generic random keys: the bucket must encode key bits, while the slot must encode the arbitrary trail number. Once entries are reordered into key buckets, a lossless fixed-width record must also carry the 17-bit trail number. With a 30-bit residual and one written bit, the record is at least `30 + 17 + 1 = 48` bits, worse than the 47-bit index slot.

Keeping the index slot and dropping key bits is lossy. A 31-bit total fingerprint at the requested 142,000 trails has expected pair-alias term

```text
C(142000,2) / 2^31 = 4.694764036685228,
```

so it cannot be a probability-loss term. A milder 31-high-bit residual plus the 11-bit F field uses 43 bits per slot, holds 108,812 trails, and has exact alias bound 0.001658665126685. Replanning with that term gives `time_log2 = 124.14006`, worse than both v2 and this package. The package therefore does not claim an invalid bucket prefix or omit trail-number information.

## 4. Search algorithm and random-function proof

One fresh uniform 256-bit word r defines every start `r+t`. A point is distinguished when its low 32 bits are zero and its following 90-bit field F is below `1522`. The exact plan is

```text
L     = 2658455991569831745807614120560689152/761
B     = 1325677760920000000000000000000000000 batches
Q     = 339373506795520000000000000000000000000 evaluations
c     = 48907206152401635271099339931471286
tmax  = 99529
slots = 99787
```

At each batch, 256 trails advance through the bit-sliced program. Stage 1 combines the low 32 physical g planes. At a DP, the table is scanned and the full key is compared. On a match, pass 1 recomputes the stored trail length; pass 2 aligns the two trails and finds the colliding predecessors. Each pass is bounded by `capr = c + 2^48`; the ledger charges `2 capr + 1` calls.

For a lazy-sampled uniformly random function F, fresh outputs have collision hazard 2^-256 and independent DP probability `1522/2^122`. The failure budget covers no useful collision, delayed detection, same-trail and cut-trail partners, old trails, a second path collision, the finished-trail Chernoff overflow, a third cut, the exact false-key term above, table overflow, and stated early halts. The outward-rounded certificate gives `P_F >= 0.390000001000 >= 0.39`.

H1 is the only score-critical premise. It says that this fixed SHA-256 walk succeeds at least as often as F in this one bounded attempt, including the adaptive collision hazard. H1 is declared, not proved.

## 5. Circuit construction and charged preprocessing

The exact T2 circuits replace the four stored-polarity carry contexts where every ordinary order/template pair costs ten gates. The constant-aware selector compares first triples and one-column carry choices. Recent-XOR cancellation removes local identities. The six offsets and the frozen selector tables are charged preprocessing output.

Offset selection charges `1641 * 2^48 = 461900436782186496` operations. The complete selector envelope charges another `2^48 = 281474976710656`. The shipped self-test exhausts every T2 truth row and compares every emitted record.

## 6. Normative compact emitter

`experiments/bssha.py` embeds the normative freestanding C emitter as `GEN_C`. The source is 21,667 bytes with SHA-256 `71ff2359a1a531e000bcc4f3b73fcea18b519ca5954593b712eedc175230730f`. It enforces the two-bit opcode and ten-bit register boundaries while writing four bytes per record.

The participant build used Ubuntu clang 18.1.3 and LLD 22.1.2:

```sh
clang-18 --target=wasm32 -Oz -ffreestanding -fno-builtin -nostdlib -c emitter.c -o emitter.o
wasm-ld --no-entry --allow-undefined --strip-all emitter.o -o emitter.wasm
```

The stripped wasm is 17,343 bytes, has 5,098 static instructions, and has SHA-256 `d4928b7973f29e308fe18b4080b34a23447b5dff8896f44622adf9b58d3d5cad`. Wasmtime 49.0.0 measures exactly 180,496,581 executed operators. The charge is `2 * 180496581 + 1 = 360993163` word operations. The emitted 345,500-byte SLP has SHA-256 `0c9e0356c48cc1a7f4f8c143822517aa59d4c6a08a9e96d560381e8fbc79adc4`.

The organizer executes the packaged Python byte-exact mirror before every experiment request. It checks all 15 C fields, the C source hash, q, the SLP hash, and every emitted byte. Native and wasm counts are participant-run accounting.

## 7. Exact operation ledger

```text
main                                             114554466676619040000000000000000000000000
slices                                           6122679569372735386423900
stage1_hits                                      442492691347122192382812500179200
events                                           59968412138
cuts                                             8400
recovery                                         313788634673808891901179308450895343834
setup                                            361806763
offset_search                                    461900436782186496
selector_search                                  281474976710656
total N                                          114868255753785546361703403245970871071387
```

The organizer reference cost is C = 4912. Therefore

```text
log2(N / C) = 124.13693720423046990885048791749964405919423128465415038950831959937271239711881.
```

The claim rounds upward to `124.13694`. The integer certificate is

```text
2^12413693 * 4912^100000 <= N^100000
N^100000 < 2^12413694 * 4912^100000.
```

## 8. Memory and preprocessing

```text
four-byte body code                              345,500
other code                                        63,576
47-bit table                                     586,249
counters and copies                               16,384
1,024-register file                               32,768
recovery arrays                                    4,096
total                                           1,048,573 bytes
```

The emitter image is `5098 * 36 = 183,528` bytes. Scratch is 120,055 bytes: 87,150 use bytes, 23,532 named state arrays, 4,619 choice bytes, 658 constants, and a 4,096-byte stack. Setup peaks at 765,907 bytes. The count-only searches peak below setup. Search is the overall peak and `memory_log2_bytes` is 20.

Preprocessing totals `462181912120703915` operations:

```text
log2(preprocessing / 4912) = 46.419143567537000684197991503769008581530768671588070944015151255793831338400672.
```

The upward-rounded preprocessing claim is `46.41915`. There is no advice.

## 9. Experiments, credits, and limits

`bssha-n16` runs the complete search at width 16. `proj-k0-w256` evaluates full-width points and reconstructs the complete two-block digest. Both run the normative mirror first, and the organizer recomputes every returned event. These are functional checks, not estimates of H1.

The direct parent is `7523902c-ff00-468e-8214-fa0cfdeaa4ef`. The package also credits d22ae1b2 for T2 and the index table, 95263e47 for the selector, and the same-challenge lineage for walk B, constant absorption, the prefix, two-block messages, and fixed-width body records.

The package does not observe the full functional graph or a 256-bit collision. It does not claim a practical collision or a weakness in deployed SHA-256.

## Appendix. Exact certificate program

```python
from fractions import Fraction
from math import log, exp, log2, log1p, comb, expm1

PH, FILT, LOOP, LANES = 86375, 34, 3, 256
INSTR_REC = 86375
PH7, EXTRA, RECINIT = 3161, 47, 146
N_BITS, S1, W, KAPPA = 256, 32, 90, 14          # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE, GEN_FUEL = 2800, 3800, 4200, 1300, 180496581
GEN_CODE, GEN_SCRATCH = 5098, 120055
OFFSET_EVALS, OFFSET_EVAL_OPS = 1641, 1 << 48
SELECTOR_SEARCH_OPS = 1 << 48
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 2
INSTR, OTHER_CODE, REGFILE, COUNTERS, SLOTB, ADVICE, ARRAYS = 36, 1729, 32768, 16384, 47, 0, 4096
KEYB = 46                                             # key bits (5 bytes)
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
GRAIN, TB = 10 ** 24, 17                       # B is a multiple of GRAIN; trail-number bits of a table entry
FINE, COARSE = 20000, 2000                      # bins of the detection-delay sum (last 120 L batches, earlier part)
body = PH + FILT + LOOP                                        # one batch = 86,412 operations
code_bytes = INSTR_REC * 4 + (FILT + LOOP + OTHER_CODE) * INSTR     # the body records once at 5 bytes, every other instruction once at 36 bytes
tmax = 99529
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
