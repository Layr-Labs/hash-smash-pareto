# SHA-256, 40 steps: a counted two-block cost bound of 2^123.136

## Section 1 - Claim

Target sha256-r40-prefix-v1. Ordinary collision of two complete messages under the standard IV,
FIPS 180-4 padding, feed-forward, all eight 32-bit digest words equal.

    time_log2                    123.136   (exact 123.135348, rounded up at 3 decimals)
    time_unit                    target-compressions (one 40-step compression = 1 unit)
    memory_log2_bytes            20
    preprocessing_log2           43
    success_probability          0.39
    nonuniform_advice_log2_bytes 7.32193
    score                        123.136 + max(0, 20 - 20) = 123.136

The entry is a counted cost bound for an algorithm that outputs the collision. One step of the
construction, the closing block-2 characteristic of Section 5, is a declared premise
(H4-close-tail, Section 11).

## Section 2 - Output form

Two messages M = M0 || N || PAD and M' = M0' || N' || PAD of equal length. Block 1 is a
254-bit walk collision: M0 != M0' and the chaining values after block 1 differ only in
register h, by dh = 0xc0000000. Block 2 absorbs dh at step 0 and re-emits -dh = 0x40000000
in h as its terminal internal (pre-feed-forward) difference, so Davies-Meyer gives
dH = dh + (-dh) = 0: the chaining values after block 2 are equal, the common padding block
preserves equality, and all 256 digest bits agree.

## Section 3 - Block 1: the 254-bit walk

Carried anchor: df1f1cd1 (round 40), a distinguished-point walk with bit-sliced per-evaluation
accounting, 123.90702 at the 0.61 success floor, lambda0 = -ln 0.61 = 0.494296.

The map walked is psi = (a..g, h mod 2^30), the 40-step output with the top two bits of h
dropped. A psi-collision has dh uniform on {0, 2^30, 2^31, 3*2^30}; three of the four outcomes
are usable: dh = 0 closes block 1 on its own, dh = +-2^30 is closed by the Section 5
characteristic (its sign is chosen by swapping the pair), dh = 2^31 is discarded. Three usable
outcomes of four lower the walk floor by -1/2 * log2 3 = -0.79248:

    a0 = 123.90702 - 0.79248 = 123.11454      (walk floor, per-evaluation basis)

Premise P1-walk-254 (Section 11) carries df1f1cd1's random-function premise to psi.

The psi reduction costs one extra word operation per walk evaluation, which is charged in
Section 6 at the full v5 word-operation weight.

## Section 4 - Block 2: the carried r39 terms on constants K1..K39

Block 2 runs the accepted 39-step claw and tail machinery on the shifted round constants
K1..K39; the 40-step schedule's step-0 word is spent absorbing dh. Carried: 9993eaa8
(116.58624 at success 0.39) and 5f8e6192's term decomposition - claw +9.8077, W17 pin
+32.0000, tail +74.3238, ops per claw +1.5647, leader tightening -0.0609. The budget driver
of Section 6 uses the carried per-unit rate b0 = 116.5437.

Executed on K1..K39: rows <= 16 of the block-2 head, 3/3 SAT, 0 violations; tail junction
histograms J20-J26 on K1..K39 equal to the K0..K38 tail within sampling noise at 2^30 samples
per junction (J22: 443,739,873 vs 443,737,969 kept, 4,187 vs 4,251 at weight 6). The
premises that carry this leg - H2-r39-on-K1, H3-advice-construction, H5-group-independence -
are stated in full in Section 11 and in claim.json.

## Section 5 - The closing block-2 characteristic

Block 2 is Davies-Meyer: H = CV_in + Wst(CV_in, N), so register-wise
dH = dCV_in + dWst_terminal (mod 2^32). With dCV_in = (0,...,0, dh), closure requires

    dWst_terminal = (0,...,0, -dh):  dE36 = -dh, dE37 = dE38 = dE39 = 0,
                                     dA36 = dA37 = dA38 = dA39 = 0

because the 40-step output map is (a39..h39) = (A39, A38, A37, A36, E39, E38, E37, E36) with
h39 = g38 = f37 = e36.

The difference enters down the d-chain, not at step 36: E36 = d35 + T1_36 and
A36 = T1_36 + T2_36 share T1_36 with dT2_36 = 0, so a W36 difference would also move the
output register d39 = A36. With d35 = c34 = b33 = a32 the live quantity is

    dA32 = -dh = 2^30   ->   d35   ->   e36   ->   h39 ,  W36 silent,

the a-branch (a33..a36) and the e-branch (E37, E38, E39) being killed by corrections in the
derived words W32..W35 and W37..W39. This is a last-steps local collision over steps 32..39
at bit 30, where carries reach only bit 31, so the corrections are linear single-row
relations of WAYFINDER type (dE35 = -dW39). Word differences: N0 = +0x40000000 for the step-0
absorption, the head set {0, 9-13, 17, 18, 25, 27} of the block-2 head, and the tail-driving
set realising dW32..dW35, dW37..dW39, with dW36 = 0.

Condition count of the tail: seven active rows at 6 ... 13 effective conditions per row for a
signed carry-free bit-30 local collision, i.e. 2^-42 ... 2^-91, by the r39 per-row density
report at L = 32 (k8_expected 30.14, k6_expected 101.34). The level at which a block-2 tail
first enters the shared budget is 2^-119, the block-1 walk floor of 2^123.11454, so the tail
contributes 0 to the time ledger at every point of that range, with margin 2^28 at the
weakest end. The characteristic is the declared premise H4-close-tail (Section 11).

## Section 6 - The time ledger

One driver runs the 254-bit walk until the first usable psi-collision, then runs
block 2 in the remaining budget W, sequentially on the same arena:

    walk      P(T1 <= t) = 1 - exp(-lambda0 * (t / 2^a0)^2),      a0 = 123.11454
    block 2   P2(x)      = 1 - exp(-lambda0 * x / 2^b0),          b0 = 116.5437
    success(W) = E[ 1{T1 <= W} * (1/3 + 2/3 * P2(W - T1)) ] = 0.39
    =>  log2 W = 123.13485                              (shared-budget solution)

The 1/3 is the dh = 0 outcome of psi, which needs no block 2.

The psi mask is one extra word operation in a walk evaluation whose target compression is
2,896 counted v5 word operations, so each walk evaluation costs the factor
1 + 1/2896 = 1.0003453038674033149:

    log2(1 + 1/2896) = 0.000497938
    time_log2_exact  = 123.13485 + 0.000497938 = 123.135348
    time_log2        = 123.136                      (rounded up at 3 decimals)

That operation is charged at the full word-operation weight; no score-quantum exemption is
taken for it or for any other primitive of either engine. Generated candidates, failed
trials, table operations, verification and restarts are inside the two per-evaluation
accountings of Sections 3 and 4, which the engines of Section 9 implement. Preprocessing is
charged in Section 8. Both engines use v5 primitives only - load/store, add/sub, AND/OR/XOR/NOT,
shift/rotate, comparison, conditional branch - and nothing outside that list is used or charged
anywhere. In particular no bit-position primitive appears in either accounting: the
distinguished-point test is a masked compare on the walk word, charged as 1 AND, 1 comparison and
1 conditional branch at the full word-operation weight, and the psi reduction is the single AND
charged above.

## Section 7 - Memory census

Both blocks run sequentially on one shared distinguished-point arena, configured at 1,000,000
bytes including its table control words. Total v5 storage at the peak:

    distinguished-point arena (incl. control)            1,000,000 B
    engine code, both legs (Section 9)                      27,277 B
    advice pair                                                160 B
    the two retained messages (2 x 128 B)                      256 B
    working state (8 chaining words, 64 schedule words,
      walk counters, claw candidate records)                    352 B
    ------------------------------------------------------------------
    total peak                                           1,028,045 B = 2^19.9715

memory_log2_bytes = 20, memory term max(0, 19.9715 - 20) = 0. The arena is the only table and
no result list is retained between the two legs, so this census is the whole storage of the
algorithm.

## Section 8 - Advice and preprocessing

The non-uniform advice is the 160-byte advice pair of 5f8e6192
(nonuniform_advice_log2_bytes = 7.32193). Its one-time construction and selection is charged
at 2^43 compressions (2^42.545 by the accounting H3-advice-construction carries), and
preprocessing_log2 = 43 is that charge, added to the time ledger. 2^43 is the single
preprocessing number of this entry, in claim.json, in this ledger and in the note.

## Section 9 - The engines, supplied in this package

    experiments/claw40.py     13,644 B  sha256 dbe505cff437f2a88f2bc3e1b3429cc1f220d5abaa248317bc4d7661b23b209e
    experiments/shift40.py     9,894 B  sha256 719b1274425657159f2cc1d5bb4b7f040a39e02eec02eceeab9aad547aad3745
    shipped total             23,538 B  (stdlib only, deterministic from the trial seed)
    budget solver and walk kernel, counted but not shipped    3,739 B
    engine code charged        27,277 B  (the Section 7 code line)

- claw40.py is the block-2 engine: the folded step function on K1..K39, the even/odd claw
  search in a shared distinguished-point table, the F9, F8 and W17 tail filters rebuilt on the
  shifted advice trajectory, and the two 39-step compressions verifying any W17 pass. It
  counts its own evaluations, claws and filter passes per window, and hard-asserts every trial
  output. Its claw and tail-event rates are the ones Section 4 carries.
- shift40.py is the bridge engine: the shifted schedule identity over 63 words, the new-word
  difference dN0 = 0x40000000, the step-0 cancellation leaving the incoming chaining values
  differing only in h by 0xc0000000, and the lit-set map {8-12, 16, 17, 24, 26} ->
  {0, 9-13, 17, 18, 25, 27}. Hard-asserted per trial.
- The shared-budget solver of Section 6 and the block-1 254-bit walk kernel are not shipped
  files; the Section 6 arithmetic is stated in closed form there and the kernel's per-evaluation
  accounting is the bit-sliced accounting carried in Section 3. Their 3,739 bytes of code stay
  charged in the Section 7 census.

Worst-case bounds of the search loops, from the constants of Sections 3, 4 and 6: the block-2
claw search of claw40.py runs exactly 2 windows per trial of 1,536 evaluations each, 3,072
evaluations in all, and each folded-step walk inside a window is cut at the distinguished-point
test, so every loop of the engine terminates after at most 1,536 iterations per window; the
block-1 walk loop is cut by the shared budget W of Section 6 and so runs at most
2^123.13485 / (1 + 1/2896) evaluations. No loop of either leg can run longer than these
constants allow, and the per-evaluation accountings of Sections 3 and 4 charge every iteration.

## Section 10 - Experiments

experiments/manifest.json declares for organizer execution r40-shift-identity and
r40-block2-transplant (shift40.py) and r40-claw-window (claw40.py), each with its scope and
its hard-asserted hypothesis. The declared experiments establish the algebraic steps and the
window diagnostics named in their scope fields; the time and success laws of this entry rest
on the two carried per-evaluation accountings and on the premises of Section 11.

## Section 11 - Declared premises, in full

P1-walk-254 (score-critical, block 1). df1f1cd1's random-function premise holds for the
254-bit map psi, the 40-step output with the top two bits of h dropped, and three of four of
its collisions are usable by block 2. Scope: block 1 of this entry on sha256-r40-prefix-v1.
Support: carried from the accepted df1f1cd1 entry; the usable-outcome law follows from dh
being uniform on {0, 2^30, 2^31, 3*2^30} for psi-collisions. Limitations: carried premise;
psi drops two output bits of h.

H2-r39-on-K1 (score-critical, block 2). Premises H1 (claw model) and H2 (tail,
-log2 p >= 74.3238) of 9993eaa8 hold with the round constants K1..K39 in place of K0..K38,
because the round constants change value conditions only and never the signed differences.
Scope: block 2 of this entry. Support: rows <= 16 executed on K1..K39, 3/3 SAT, 0 violations;
tail junction histograms J20-J26 on K1..K39 equal to the K0..K38 tail within sampling noise at
2^30 samples per junction (Section 4). Limitations: the claw rates are declared to transfer;
the executed support is rows <= 16 and the junction histograms.

H3-advice-construction (score-critical, block 2). A[8..11], E[12..15] and W12..W15 are fixed
to the advice values; (A[6], A[7]) range over the listed entries of the fibre 0x3cc9eebe; for
every listed entry both messages follow the advice state-difference trail through step 15, W9
is C9 + 0x05cefde0 - a1 and W16 is one value per claw. Constructing and selecting the advice
pair costs at most 2^43 compressions (2^42.545 by the accounting of Section 8), added to the
claimed time; the offline fibre search costs at most about 2^31.1 compressions, inside the
remaining 2^41.1. Scope: the one-time construction of the 160-byte advice pair of 5f8e6192,
on the shifted constants K1..K39. Support: exhaustive enumeration over all 2^32 a3 with the
real two-message trail checked on every entry at four points, 0 failures; the rule reproduces
that list exactly. Limitations: the pair-construction campaign was run by the pair's authors
and is charged at its declared cost.

H5-group-independence (score-critical, block 2). Windows of the screened law are independent
(fresh first blocks, each drawn and screened independently). Trials are distinct (a2, kappa)
keys with at least one listed entry passing F8 in a claw passing F9. Each listed key's W17
event has probability 2^-32 in each claw (a uniform claw constant), and events in different
claws are independent. Within a claw, two keys hit together iff
G(a2, kappa, w) = s0(a2 + w) - (a2 + w) + kappa coincide; with N_k(w) the number of other
listed keys sharing key k's G at the claw's w, the priced quantity is E_w[min(N_k(w), 3)].
Measured over all 3,462,264 listed keys on two independent sets of 16,384 random w: mean
1.07e-3, largest per-key estimate 4.6e-3, per-(key, w) counts N = 1 in 60,723,478 cases,
N = 2 in 37,173, N = 3 in 40, N >= 4 in none of 5.67e10. The claw's w contains -cv5
additively, so it is uniform and independent of the walk inputs. Clusters above four keys are
left out of the second-order sum at a cost of at most 1.341e-3 per key in the first-order
term; for every kept key N_k <= 3 and family-wise E[min(N_k, 3)] <= 1.36e-2 at alpha = 0.001.
Success is priced by second-order Bonferroni over all hits on designated-mate events, with
the cross-claw term on the claw-weighted claw count and the within-claw term on the key-mean
co-hit rate; no premise between the tails of different hits is used. Scope: the amplification
over the windows of the screened, capped block-2 program on K1..K39. Support: the measured
co-hit statistics above and the real-claw check at the w of 2,000 F9 claws (mean 1.0825e-3,
largest per-(key, w) N = 3). Limitations: participant-run counts; independence of the 2^-32
events over all groups and windows is the premise, not a measurement.

H4-close-tail (score-critical, block 2 closure; the premise declared new in this entry).
There is a block-2 characteristic on constants K1..K39 that absorbs the incoming chaining-value
difference (0,...,0, dh), dh = 0xc0000000, at step 0 against dN0 = 0x40000000, and whose
terminal internal difference is (0,...,0, -dh) with -dh = 0x40000000: dA32 = -dh routed through
d35 to e36 to h39, W36 silent, the a-branch and the e-branch cancelled by the derived words
W32..W35 and W37..W39, as laid out in Section 5. Its conditions hold with probability at least
2^-91, by the seven-row signed carry-free bit-30 density of Section 5; since a block-2 tail
first enters the shared budget only at 2^-119, the characteristic contributes 0 to the time
ledger of Section 6 and the claimed time is set by the walk and claw legs alone. Scope: block 2
of this entry, the fixed terminal difference -dh in h and the fixed routing of Section 5 on
sha256-r40-prefix-v1 with constants K1..K39; not claimed for another terminal difference,
routing or round count. Support: the Davies-Meyer register algebra and the output map
h39 = g38 = f37 = e36 of Section 5, which fix the terminal constraint set exactly and exclude
injection at step 36; the step-0 absorption executed in shift40.py (dN0 = 0x40000000, incoming
difference in h only, hard-asserted per trial); the bit-30 class, whose carries reach only bit
31, so that the row corrections are single-row linear relations; and the r39 per-row density
report at L = 32 that bounds the per-row condition count. Limitations: the condition count of
the closing tail is declared from that per-row density rather than counted by a condition-count
tool, and the premise is asserted for the Section 5 routing and terminal difference only.
