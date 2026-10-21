# sha256-r59: a 77,547-record bit-sliced birthday walk

This package is a credited derivative of the judged-valid same-design parent `7523902c-ff00-468e-8214-fa0cfdeaa4ef`, the judged-valid native-record entry `ff37a322-c5e7-4656-bb89-02f1a5d0e213`, the same-round prior entry `64dc4a97-0669-428b-976c-7eacc6cba143`, `d22ae1b2-2368-460a-b6d4-1e5e37ceb735`, and `95263e47-d61b-43a6-bb46-30ced2488280`. It reimplements the round-59 walk with the exact T2 carry columns, constant-aware selector, recent-XOR cancellation, charged offset search, index-layout table, and bounded native-record emitter.

The construction is a generic collision search. It assumes only premise H1 below. It claims no differential, structural, or other weakness in SHA-256.

## 1. Target, message family, and collision relation

The target is `sha256-r59-prefix-v1`. SHA-256 executes steps 0 through 58 on both blocks of a padded 64-byte message, with the standard IV, feed-forward, and all 256 output bits.

Write a 256-bit point x as eight big-endian 32-bit words y0 through y7. The first message block is

```text
W0..W7 = 3e73281c 752d8ed2 ad19eff1 7250fceb
          d4095422 44fdb519 43f22c5b d8d6aac4
W8      = y0
W9      = y1
W10..15 = y2..y7 plus dbce7a42 aaf3823d 8d41a28c 7f214e02 6423f959 08000000, respectively, modulo 2^32.
```

The offset map is a bijection. FIPS padding adds `80`, 55 zero bytes, and the 64-bit length 512, so every message has a fixed second block. The prefix is computed from the standard IV so that after its eight steps `a1 = K9-K8`, `a2 = -K9`, and `a3` through `a8` are zero. Steps 8 and 9 then cancel K8 and K9.

Let a_i and e_i be the working words after i steps of block 1. Let T1_i be the T1 value that produces step i. First define the logical walk-B vector `bw` as

```text
e_56, e_57,
X  = e_54 + (~e_57 & e_55) + W_57,
T1_55,
Q  = T1_54 + Maj(a_53,a_52,a_51),
a_53, a_52,
Y  = e_55 + W_58.
```

The physical no-move output order is `out[k] = bw[PERM[k]]` for `PERM = (6,1,7,0,5,4,2,3)`. The proof names f as this permuted eight-word output, matching both the Python generator and `GEN_C`. The inverse first applies the inverse permutation and then the equations below.

This encoding is bijective. Its inverse first recovers `a_54 = Q + Sigma0(a_53)`, then reconstructs the remaining a words, T1 values, and the complete state with the SHA-256 step equations. In particular, `T1_57 = X + (e_57 & e_56) + Sigma1(e_57) + K_57`.

The allocated program leaves a fixed set of output planes complemented. In canonical big-endian hexadecimal,

```text
q = 3a7b6c304683f1da9aa8f568050ccf116e5a78c6d242ab1d78a921de25fa3184.
```

The output registers already hold `g(x) = f(x) XOR q`. A collision of g gives equal block-1 working states. Feed-forward and the fixed second block then give equal complete digests.

## 2. Search algorithm and probability space

The only random input is one fresh uniform 256-bit word r. Trail t starts at `r+t mod 2^256` and repeatedly applies g. A point is distinguished when its low 32 bits are zero and its next 90-bit field is below `Tp = 1761`. Thus

```text
theta = 1761 / 2^122
L     = 5316911983139663491615228241121378304/1761
B     = 1325325622231000000000000000000000000 batches
Q     = 339283359291136000000000000000000000000 evaluations
c     = 42269601228821856264970582268994490
S     = 2^48
PLAN_TP = 1761
PLAN_TMAX = 114913
PLAN_C = 42269601228821856264970582268994490
PLAN_CMAX = 2
PLAN_CUT_HALT = 3
PLAN_BINOMIAL_FIRST_REJECTED = 3
```

The program advances 256 trails at once. One 256-bit word holds one bit plane across all lanes. After a batch, 31 ORs combine the low 32 physical g planes; the charged comparison and branch complete the stage-1 test. The published q makes this convention explicit. No runtime mask is omitted.

The table has 115,171 index-layout slots. Slot t belongs to trail t and stores a 46-bit key plus one written bit. It stores neither the trail number nor the length. At most 114,913 completed trails are retained. The slot index fits 17 bits.

On a key match, recovery pass 1 recomputes the stored trail length. Pass 2 aligns the trails and advances them until their next values agree. The two predecessors form the collision. Each pass is bounded by `capr = 42269601228821856264970582268994490 + 2^48`; the ledger charges `2 capr + 1` calls. The cut counter permits at most `CMAX = 2` cuts and halts when cut number 3 would occur. The attempt also halts after B batches, a full table, a stage-1 overflow, an overlong recovery, or a false key match that yields no pair.

For a uniformly random function F on 256-bit points, expose outputs by lazy sampling and mark each fresh output distinguished independently with probability theta. Let P_F be the success probability of this exact bounded program with g replaced by F. The proof partitions failure into no useful birthday collision, delayed detection, a same-trail partner, a cut-trail partner, an old partner trail, a second collision on the remaining path, the finished-trail Chernoff overflow, cut number 3, a false key match, table overflow, and the stated early halts.

For fresh evaluations, lazy sampling gives collision hazard 1/2^256. Conditioning on non-DP values replaces the range size by `N' = 2^256(1-theta)`. The no-collision factor is `Pi(m) = product_(i=0)^(m-1)(1-i/N')`. Trail lengths are handled directly by the independent DP lottery. The finished-trail count uses the Chernoff bound for `Binomial(Q,theta)`.

Lemma 2 uses the live cut budget. A cut requires `c = 42269601228821856264970582268994490` consecutive non-DP values. Let `p = exp(-c*theta)` and let `n2 = k + 256 + CMAX`, where k is the certified finished-trail cutoff. Step 6 charges

```text
Pr[Binomial(n2,p) > CMAX]
= 1 - sum from j=0 through CMAX of binom(n2,j) p^j (1-p)^(n2-j),
CMAX = 2.
```

The first rejected count is therefore 3 successes, exactly the program's halt on cut number 3. Appendix B evaluates this same sum with `range(CMAX + 1)` in both the planning mirror and the 60-digit outward-rounded certificate. The detection-delay term sums the first-collision mass over 2,000 early bins and 20,000 bins covering the final 120 mean trail lengths. False keys use the 46 disclosed key bits. All remaining collision and stage-1 terms are union bounds.

The 60-digit outward-rounded evaluation of those formulas gives `P_F >= 0.390000001000`, hence `P_F >= 0.39`. The plan is deterministic and is printed by the shipped `--ledger` mode.

Premise H1 is score-critical and is not proved. It says that this fixed walk g succeeds at least as often as F in this one attempt. Concretely: fresh outputs have the 2^-256 collision hazard; iterates have the first-collision law of a random mapping; a fresh output is distinguished with probability `1761/2^122` independently of collisions; and conditioning on the adaptive history does not lower the hazard of hitting an earlier non-DP value. H1 is limited to this message family and this approximately 2^128-evaluation experiment.

## 3. The 77,547-record kernel

The declared word-RAM has 1,024 256-bit registers: 1,021 data registers and three pointers. A body record is the machine's native 32-bit instruction: a 2-bit opcode followed by three 10-bit register fields. Opcodes 0, 1, and 2 are XOR, AND, and OR; opcode 3 is reserved. The body contains only those three operations. The machine executes each native record directly for one word operation. It does not fetch a packed software stream, decode records, or access a software register file. Recovery and all other control records use separate fixed 5-byte formats and still cost one word operation each. Bit-sliced rotations only rename planes.

The body uses registers 0 through 1020, so its maximum index is 1020 and `1021 < 1024`. The C emitter rejects any opcode outside the three live values and any field above 1023 before writing a record. The shipped boundary test independently requires `nreg = 1021`, all fields below 1024, exactly four bytes per body record, and zero moves.

The three-word adder carries a pair `(u,U)` with value `1 if U else 2u`. T0 and T1 are the two published nine-gate column templates. For the four stored-polarity masks where every T0 or T1 order costs ten gates, the shipped `SYN` table holds exact nine-gate T2 circuits, or eight gates at bit 30 where u' is dead. The self-test exhausts all 32 Boolean inputs for every T2 circuit.

The selector compares at most 64 first-triple masks at each of 134 multiword decisions and at most `13*13` current and lookahead forms at each of 4020 column decisions. Recent-XOR cancellation removes an XOR when a recent XOR meets one of its operands, or when two recent XORs share a child.

The offset search evaluates exactly 1,641 candidates: 64 endpoint masks, one initial coordinate point, three 192-bit sweeps, and 1,000 fixed-seed perturbations. A structural upper bound for one complete candidate is

```text
2 * 160 * 64 * 32 * 13 * 13 * 12 * 1024 < 2^41 operations.
```

The ledger charges `2^48` per candidate, including all remaining construction and comparison work. The complete selector search has structural bound

```text
2 * 134 * 64 * 32 * 13 * 13 * 12 * 1024
+ 4020 * 13 * 13 * 12 * 1024 < 2^41,
```

and is charged another `2^48` operations. The searches retain one candidate at a time and have the memory bounds in Section 4.2.

The final body has 61,054 XOR, 9,817 AND, and 6,676 OR records, with 0 moves. Total: 77,547 records. One batch costs `77547 + 34 + 3 = 77584` operations.

## 4. Normative native-record emitter

`experiments/bssha.py` embeds the normative freestanding C source as `GEN_C`. It is 21,199 bytes with SHA-256 `7e7d3b14936029099f0d7f7282fe7ac16d28e6853f446df014894c03f9821c5a`. The source performs the bounded two-pass build, online allocation, and direct native 32-bit emission. It reports 77,804 nodes, 323,194 helper calls, 1021 registers, and 77,547 records. It tracks the register boundary while emitting and never decodes the emitted stream.

The participant build used Ubuntu clang 18.1.3 and LLD 22.1.2:

```sh
clang-18 --target=wasm32 -Oz -ffreestanding -fno-builtin -nostdlib -c emitter.c -o emitter.o
wasm-ld --no-entry --allow-undefined --strip-all emitter.o -o emitter.wasm
```

The stripped module has 5,070 static instructions, 16,899 bytes, and SHA-256 `935effd6d5be02b398616374312dcd0d4e6a40b0390caf9c34472ba2ed33a6a9`. Wasmtime 49.0.0 reports exactly 157,866,153 executed operators for `run`. Charging two word operations per fuel unit plus one gives `315732307` operations. The emitter outputs 310,188 native-record bytes with SHA-256 `6142b14f285673ae0e01a76edbd53996bdd37c352e46028716d08e21fbecb991`.

The organizer runs `BGen` and `BoundedEmitter`, the packaged byte-exact Python test mirror. Before every request the mirror packs its logical gate tuples and checks the 14 material C fields, the embedded C source hash, q, the native-record hash, every emitted byte, the opcode range, and the 10-bit field boundaries. The C helper-call total is diagnostic, not a construction field or a charged operation count: nested C arguments and Python's left-to-right evaluation can take different helper paths while emitting identical records. The exact wasm fuel is the charged setup count. `Prog.run` and `Prog.compile` evaluate logical tuples only for functional tests and organizer experiments. They neither decode the native record image nor define the priced machine.

## 4.1 Exact operation ledger

```text
main                                             102824063075169904000000000000000000000000
slices                                           6121053207054316658286900
stage1_hits                                      442375152378892898559570312679200
events                                           79844540138
cuts                                             8400
recovery                                         245163687127166766338461932025089850444
setup                                            316545907
offset_search                                    461900436782186496
selector_search                                  281474976710656
total N                                          103069227204672229266285029727903980808141
```

The organizer contract gives `reference_operation_cost = 4492` for this target. Therefore

```text
log2(N / 4492) = 124.10952333768970746536846020297760735478459559131608453389890038571881121070890.
```

The upward-rounded claim is `124.10953`. At precision 1/100000 bit, the integer certificate is

```text
2^12410952 * 4492^100000 <= N^100000
N^100000 < 2^12410953 * 4492^100000.
```

## 4.2 Memory and preprocessing

Search memory is

```text
body code             77547 * 4 = 310,188
control/recovery code 1766 * 5 = 8,830
total code            319,018
table                 ceil(115171 * 47 / 8) = 676,630
counters and copies   16,384
register file         32,768
recovery arrays       3,776
total                 1,048,576 bytes
```

The table capacity is the largest fit:

```text
tmax = floor(8 * (2^20 - 319018 - 32,768 - 16,384 - 3776) / 47)
       - 256 - 2 = 114913.
```

The emitter image is `5070 * 36 = 182,520` bytes. Scratch is `77804 + 23536 + 4154 + 658 + 4096 = 110,248` bytes for use counts, named state arrays, choices, constants, and stack. Setup peaks at 664,714 bytes.

The count-only offset and selector searches peak at 535,832 and 539,938 bytes. They execute sequentially, so peaks do not add. The overall peak is 1,048,576 bytes and the claim rounds memory upward to 20 bits.

Preprocessing consists of setup `316545907`, offset search `461900436782186496`, and selector search `281474976710656` operations:

```text
preprocessing = 462181912075443059
log2(preprocessing / 4492) = 46.548096200365297711323430409874810260729380431804313009631668700978620202538756
```

The upward-rounded preprocessing claim is `46.54810`. Its integer certificate uses exponents 4654809 and 4654810 at precision 1/100000 bit. There is no nonuniform advice.

## 5. Premise H1 and its evidence

Model premise comparing two success events. Let F be a uniformly random function on 256-bit values. The probability that this single attempt succeeds for the fixed walk g is at least the probability P_F that the same bounded program succeeds when every g evaluation is replaced by lazy sampling from F. Clauses: (a) outputs on distinct evaluated inputs are uniform and independent, with collision hazard 2^-256; (b) iterates from the starts r+t have the first-collision law of a random mapping; (c) the exact DP rule, low 32 bits zero and the next 90-bit field below 1761, is independent of collision events and has probability 1761/2^122; (d) adaptivity does not lower the hazard: conditioned on the complete prior run history and later DP classifications, a fresh evaluation equals any given earlier non-DP output with probability at least 2^-256. Lemma 2 proves P_F >= 0.390000001000 from the lazy-sampling hazard alone. Clause (d) transfers that hazard to g. Nothing else in the success bound is heuristic.

Scope. The fixed target sha256-r59-prefix-v1 and the 64-byte message family of proof Section 1: about 112373.12 trails, mean trail length 2^111.21782, 256 simultaneous lanes, and exactly 339283359291136000000000000000000000000 evaluations. No claim is made for another message family, round count, or evaluation scale.

The sensitivity calculation re-solves Tp under the modified hazard and recomputes every integer ledger row. The extra bits are `log2(N_eps/N)`; the target-compression reference cost cancels exactly.

| Hazard deficit eps | Re-solved Tp | Exact integer N_eps | Extra time bits |
| ---: | ---: | ---: | ---: |
| 0.01 | 1752 | 103588608369143685868468301212198365529641 | 0.00725170 |
| 0.05 | 1716 | 105747398590915743756763898175988567814041 | 0.03700851 |
| 0.10 | 1671 | 108645461675978769127250540282513119652341 | 0.07601425 |
| 0.25 | 1525 | 119017432863015559174769995844102385363241 | 0.20755925 |

Support of H1 (stated; it is not measured at width 256):

1. H1 is the generic premise of parallel collision search with distinguished points. Paul C. van Oorschot and Michael J. Wiener, "Parallel Collision Search with Cryptanalytic Applications", Journal of Cryptology 12(1):1-28, 1999, DOI 10.1007/PL00003816, model a fixed compression function iterated from fresh starts, without a chosen input difference, by a random function. The generic entries of this track use the same premise: mitchuski 3017c952-db81-4c15-8782-d191a7d479ee (r51), mitchuski 1884db5b-acc6-42e7-ac3c-5877e77b8277 (r57), mitchuski 4684dfc2-cdac-4441-af91-c9979e2888a9 (r64), lamb356 3642e1cd-e391-41a7-81e0-456c02e4becd (r64), dariolina 6b678689-e6a2-42b0-87d8-fff55432f2f6 (r64), ours 7523902c-ff00-468e-8214-fa0cfdeaa4ef (r64), ours 7347a2b6-63db-4f1c-965f-c4dc1596bb22 (r41), ours 60dbf898-8af2-4f6b-9aa1-cbc971c2f674 (r42), ours 332b47e1-37c3-4b55-90e4-6c62514fc608 (r43), ours 5ed693e8-e780-4e70-b4f7-9faea9ae4ea1 (r45), ours 4aed9243-f6b8-40ae-8588-2bd00b82eb82 (r46), ours ff37a322-c5e7-4656-bb89-02f1a5d0e213 (r40).
2. Clause (d) fails in the adverse direction only if g, along its own iterates, collides less often than a random function by a factor 1-eps. Such a property would separate this 59-step function from a random function in a way no published result shows. This entry chooses no input difference and uses no differential property.
3. A higher collision hazard helps. The live-plan sensitivity calculation prices a deficit exactly: eps=0.01: 0.00725170 bit (Tp 1752); eps=0.05: 0.03700851 bit (Tp 1716); eps=0.10: 0.07601425 bit (Tp 1671); eps=0.25: 0.20755925 bit (Tp 1525).
4. The organizer program checks agree with random-function reference values at their scopes. proj-k0-w256 returned 104 of 256 against 100.53 expected. bssha-n16 returned 171 of 256; an exact-plan lazy-random-function reference over 10,000,000 mappings gives probability 0.6958435 with standard error 0.00014548, or 178.14 per 256. These counts are consistency checks, not inputs to the score.

Limitations. H1 cannot be tested at width 256: the experiments reach the complete search at width 16 and 16-bit projections of 256 full-width points, so they cannot measure the full-width collision hazard or the success probability at 2^128 scale. The exact sensitivity costs above restore 0.39 under specified hazard deficits: eps=0.01: 0.00725170 bit (Tp 1752); eps=0.05: 0.03700851 bit (Tp 1716); eps=0.10: 0.07601425 bit (Tp 1671); eps=0.25: 0.20755925 bit (Tp 1525). Circuit equivalences, instruction counts, memory bounds, and the theorem for F do not depend on H1.

## 6. Experiments as program checks

Only `bssha-n16` and `proj-k0-w256` are declared. Both run the packaged Python test mirror, and the organizer recomputes the complete two-block target digest of every returned pair. They test the generator, native-record image, walk, inverse, padding, second block, table, and recovery. No interval, population bound, or claim number is inferred from any experiment count.

For `proj-k0-w256`, the exact reference for 256 independent uniform 16-bit values in one trial is

```text
P(at least one equal pair) = 1 - product for i=0..255 of (1 - i/2^16)
                           = 0.392677526732.
Expected successful trials among 256 = 100.52544684.
Expected equal pairs per trial = C(256,2)/2^16 = 0.498046875.
```

The actual experiment also uses counter and iterate input sources, so this reference is a scope-matched consistency value rather than an iid interval for its combined count. The organizer observed 104 successful trials. For `bssha-n16`, the live plan has `B = 7`, `Q = 1792`, DP density `1/4`, and `tmax = 1856`. An independent exact-plan lazy-random-function simulator over 10,000,000 complete mappings gives success probability 0.6958435 with standard error 0.00014548, or 178.14 successes per 256 trials. It assigns a uniform 16-bit output on the first query of each input, then runs the same starts, DP rule, table, cut rule, and recovery. The organizer observed 171 successful trials.

The shipped self-test checks every emitted record, every T2 truth row, 2,560 full-width lanes, 10,000 inverse round trips, four chained batches, the rolled recovery program, the complete padded digest network, and a width-16 search. Together with the organizer counts above, these are scope-matched implementation and random-function consistency checks; no count changes the claimed score.

## 7. Credits and limits

The direct comparison point is `64dc4a97-0669-428b-976c-7eacc6cba143`. The accepted native four-byte body format comes through `ff37a322-c5e7-4656-bb89-02f1a5d0e213`. The T2 circuits and index-layout table come through `d22ae1b2-2368-460a-b6d4-1e5e37ceb735`. The constant-aware selector and bounded-emitter structure come through `95263e47-d61b-43a6-bb46-30ced2488280`. `d62a0936-923e-4589-87b7-c479847fda01` supplies same-challenge target, search, recovery, and accounting lineage. The dependency manifest records the ancestry for walk B, constant absorption, the fixed prefix, and two-block messages.

The package does not test the full functional graph, trails beyond 2^40, or the complete 2^128-scale attempt. It does not claim a practical collision or a weakness in deployed full-round SHA-256.

## Appendix. Reproduction

Run `python3 experiments/bssha.py --ledger` for the exact plan, rows, hashes, and memory. Run `python3 experiments/bssha.py --selftest` for the functional checks. Run `python3 experiments/bssha.py --gen-c > emitter.c` to extract the normative emitter. The package source is below the organizer's 64 KiB experiment limit.

## Appendix B. Exact certificate program

This standard-library program independently recomputes the exact ledger, the integer logarithm certificates, and the random-function lower bound with 60-digit outward-rounded decimals.

```python
from fractions import Fraction
from math import log, exp, log2, log1p, comb, expm1

PH, FILT, LOOP, LANES = 77547, 34, 3, 256
INSTR_REC = 77547
PH7, EXTRA, RECINIT = 2853, 47, 136
N_BITS, S1, W, KAPPA = 256, 32, 90, 14          # live plan parameters
HIT, EVENT, CUTOPS, SLICE, GEN_FUEL = 2800, 3800, 4200, 1300, 157866153
GEN_CODE, GEN_SCRATCH = 5070, 110248
OFFSET_EVALS, OFFSET_EVAL_OPS = 1641, 1 << 48
SELECTOR_SEARCH_OPS = 1 << 48
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 2
INSTR, OTHER_CODE, REGFILE, COUNTERS, SLOTB, ADVICE, ARRAYS = 36, 1729, 32768, 16384, 47, 0, 3776
KEYB = 46                                             # key bits (5 bytes)
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
GRAIN, TB = 10 ** 24, 17                       # B is a multiple of GRAIN; trail-number bits of a table entry
FINE, COARSE = 20000, 2000                      # bins of the detection-delay sum (last 120 L batches, earlier part)
body = PH + FILT + LOOP                         # one batch = 77,584 operations
code_bytes = INSTR_REC * 4 + (FILT + LOOP + OTHER_CODE) * 5
tmax = 8 * ((1 << 20) - code_bytes - REGFILE - COUNTERS - ADVICE - ARRAYS) // SLOTB - LANES - CMAX
assert tmax == 114913
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
assert (Tp, tmax, B, c, CMAX) == (1761, 114913, 1325325622231000000000000000000000000, 42269601228821856264970582268994490, 2)
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
P, C = 100000, 4492
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
