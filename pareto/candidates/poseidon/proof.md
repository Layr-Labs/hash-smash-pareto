# poseidon-orchard-r56: birthday search on an equivalent-form permutation, one trail with distinguished points tested four steps at a time, a bit-packed table, single-gap recovery, one evaluation budget for the trail and the recovery

Method: the textbook collision search (Pollard rho with distinguished points, van Oorschot-Wiener) on the Orchard hash with 56 partial rounds; every evaluation of the hash is an equivalent straight-line program whose field operations are each charged 1/C. The walk, the 807-operation step program, the table layout, the DP handler, the index passes and the single-gap recovery are those of the in-review r = 56 package 69e14209 (Jbenisek), which builds on 3a1b25b6, 9fb982e8, 43caeb6a, 1533f8f0, 874894cf and 56fb07fc; the shared evaluation budget, the recovery allowance and the coupling proof (Section 5, Lemmas 3 and 4) are those of our in-review entry 2710fcc6 (credits in Section 10). This entry changes the distinguished-point test. 69e14209 and 2710fcc6 test every output (CMPLT, BZ: 2 operations per step). Here the unrolled copies of STEP write their outputs into a ring of four registers, and the test is made once per group of four consecutive outputs, on their bitwise AND: AND(x_a, x_b, x_c, x_d) <= each of them, so a group that holds a DP always passes the test, and only a passing group (a hit) checks its four values one by one. A group of four fresh values passes without a DP (a false hit) with probability at most q = 7.2574e-4 (about (15/16)^112, Lemma 4 (g)), so the test costs 5 operations per 4 steps plus 11 per hit: about 1.2520 operations per step instead of 2. False hits are capped (FPCAP) and their cap is charged. The parameters are re-tuned (U = 48, T = 51075, MCAP = 26276, TAB = 15). Claim: time_log2 = 126.20802 (2710fcc6: 126.20933; 69e14209: 126.21255), memory 1,048,560 bytes (claimed 2^20, memory term 0), success probability 0.39 under the declared premise H1 (Section 8), preprocessing inside the time (Section 6a), no advice. The program is our own code (Appendix B), edited from the one printed in 2710fcc6.

## 1. Target, line and walk

Target `poseidon-orchard-r56-prefix-v1`: input two canonical elements (m0, m1) of the Pallas base field, p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001 (N = p, about 2^254); initial state [m0, m1, 2^65]; rounds 0-3 full, 4-59 partial, 60-63 full (deployed constants and MDS M); digest = state[0]. Cost model `orchard-field-ram-v2`: C(56) = 216 + 21 * 56 = 1392; one canonical field addition or multiplication, or one primitive 256-bit word operation, costs 1/1392 unit.

Line (Appendix B, `line`, `message`). Round 0 maps (m0, m1) to U = (m0 + c_{0,0})^5 and V = (m1 + c_{0,1})^5, a bijection (gcd(5, p - 1) = 1); its third lane is a constant, so the S-box input of round 1 is affine in (U, V). On the line (U, V) = (U0 + a tau, V0 + b tau) with a = M[0][1], b = -M[0][0], lane 0 of that input is constant and lanes 1, 2 equal d_1 tau, d_2 tau (U0, V0 from a 2 x 2 system with nonzero determinant). With W = tau^5 the state after round 1 is A + W B for constant vectors A, B (computed with the reference rounds at W = 0 and W = 1; `--selftest` checks A + W B at random W). message(W) = (U^(1/5) - c_{0,0}, V^(1/5) - c_{0,1}) with tau = W^(1/5) is injective.

Walk. The attempt draws two coins, kappa and x_0, each the low 254 bits of a uniformly random 256-bit word (kappa = 1 if it is 0, probability 2^-254). It iterates F(x) = digest(message(kappa x - E0_0)) / OUTSCALE_kappa, x_i = F(x_{i-1}), with E0_0 and OUTSCALE_kappa fixed nonzero field values of the program (Section 2). F maps the field to the field. Two values x != y with F(x) = F(y) give W = kappa x - E0_0 != W' = kappa y - E0_0 (kappa != 0), hence two distinct 64-byte messages with equal digests.

## 2. The step program (807 field operations, unchanged from 69e14209)

One evaluation of F is the straight-line program `STEP` (Appendix C, `python3 rho.py --listing`): 807 = 135 + 12 * 56 operations, 329 ADD and 478 MUL, canonical Pallas field operations on 256-bit registers. It equals the reference rounds 2-63 applied to A + (kappa x - E0_0) B, divided by OUTSCALE_kappa:
- Entry. The round-2 S-box input of lane i is A_i + c_{2,i} + W B_i = B_i kappa (x + e_i) with e_0 = 0 and e_i = (E0_i - E0_0) / kappa, E0_i = (A_i + c_{2,i}) / B_i. The scales B_i kappa are folded into the constants, so lane 0 enters as x itself and lanes 1, 2 cost one ADD each (2 ADD).
- Lane scaling. A lane may be held as its true value divided by a known nonzero constant; an S-box gives (true)^5 = scale^5 (held)^5 and scale^5 is folded into the next linear layer. A linear combination is held divided by its first coefficient: 2 MUL + 2 ADD (+ 1 ADD for a round constant) per lane.
- Partial rounds (the sparse form of Grassi, Khovratovich, Rechberger, Roy and Schofnegger, USENIX Security 2021, with the scaling above). Lane 0 is held as lambda h0 + gamma, lanes 1, 2 as Q (h1, h2) + q; the hidden pair is held in the basis Pm = diag(nu) M22^56 so that Q is diagonal at the exit. A partial round is x5 = (h0 + k)^5, h0 := x5 + n1 h1 + n2 h2, h1 := h1 + w1 x5, h2 := h2 + w2 x5: 12 operations (1 ADD, 3 MUL S-box, 4 MUL, 4 ADD).
- Counts: entry 2 ADD; round 2: S-boxes 9 MUL, linear layer with round-3 constants 6 MUL + 9 ADD; round 3: S-boxes 9 MUL, into the partial form 6 MUL + 6 ADD; 56 partial rounds, 12 each; exit 3 ADD; rounds 60-62: 9 MUL + 6 MUL + 9 ADD each; round 63: 9 MUL S-boxes, output lane 0 only, 2 MUL + 2 ADD. Sum 2 + 24 + 21 + 672 + 3 + 72 + 13 = 807. An S-box x^5 is 3 MUL, as in C.
- Constants. `build_step` derives the 327 step constants as K_j(kappa) = K_j(1) kappa^(e_j), each exponent e_j a signed sum of at most two powers 5^a, a <= 62 (asserted). Per attempt the setup computes kappa^(5^a) and kappa^(-5^a), a = 1..62 (3 MUL each), kappa^-1 (square-and-multiply on p - 2, 330 operations), one MUL per constant term, e_1, e_2, and one extra MUL per message: SETUP_D = 1,237 operations, charged inside MISC (Section 6).
- Checks. `--selftest`: the program equals digest(message(kappa x - E0_0)) * OUTSCALE_kappa^-1 of the reference rounds at 6 random (x, kappa), and |STEP| = 135 + 12 r.

## 3. The program (Appendix B `rho.py`: `attempt`, `search`, `plan`, `tune`)

1. Setup: coins kappa, x_0; the kappa setup (Section 2); the 327 step constants into their registers (327 loads); the table words zeroed; down-counter c := B (the integer literal BUDGET, a multiple of U = 48); last := 0 (the index of the last stored point, the start); false-hit counter fp := 0.
2. Trail, in blocks of U = 48 unrolled steps, each block 12 groups of 4: copy k of STEP (k = 0..47) reads register x_(k mod 4) and writes x_((k + 1) mod 4) (STEP writes its input register x only in its last two operations, so the renamed copy leaves its input intact; `--selftest` runs the renamed program). After the four steps of a group, t := AND of the group's four outputs; if t >= DELTA = (2^126 + 1) T, T = 51075 (DELTA < 2^142, in a register), no output of the group is a DP and the trail goes on. Otherwise (a hit) the four outputs are tested in slot order: a value x < DELTA is a distinguished point (DP) with index i = B - c + k + 1; it is copied into the staging register A and gets the DP handler of 69e14209 (shared by the slots, Section 6): the table is scanned; if x is stored the trail has closed: go to 3; if the table already holds MCAP = 26276 DPs, halt (failure); if i - last >= 2^119, halt (failure); else append the entry (x, i - last) and set last := i. A hit with no DP is a false hit: fp := fp + 1, and if fp > FPCAP halt (failure); fp and FPCAP are held in the recovery-only registers pidx and lidx, which nothing in the trail writes. After the block c := c - 48; at c = 0 halt (failure: budget).
3. Recovery. The repeat is x_b = x_a (b = i the index of the repeated DP, a its stored index), L = b - a; the trail has evaluated its whole group, e <= b + 3 evaluations. The recovery's allowance is left := min(B - e, RCAP) with RCAP = 2^119 (a register literal): the evaluations of the budget not used by the trail, at most RCAP. Pass 1 adds the stored gaps of entries 1..k (k the matching entry) and gives a and s, the index of the entry stored just before a (the start at index 0 if k = 1). Let q = s + L. Pass 2 adds the gaps from entry 1 and keeps the last stored point r with index at or below q; walk from it to x_q: a down-counter j := q - r, and per step test j (done at 0), test left > 0 (else halt: budget), decrement both, one evaluation. If x_s = x_q halt (start on the cycle). Then iterate both from (x_s, x_q) in lockstep, each round first testing left >= 2 (else halt: budget) and subtracting 2; the first time F(A) = F(B) return (A, B). Output message(kappa A - E0_0) and message(kappa B - E0_0).

The search has no detection window, no lockstep cap and no positioning cap: the limits on evaluations are the shared counter (at most B evaluations in all) and the recovery allowance (at most RCAP recovery evaluations); false hits are limited by FPCAP. B and FPCAP are fixed offline; `plan` re-derives B in exact integer arithmetic and asserts it. Parameters (`python3 rho.py --plan`, Appendix A): B = 169218966381152594613869050637269860384 (log2 126.99216), the least multiple of 48 at or above k 2^100 with k = 133490227 the least integer at which the bound of Lemma 4 reaches 0.39; FPCAP = mu + ceil(mu / 2^30) + 2^115 with mu = 30702377229948058504875108067042125 >= (B / 4) q; T = 51075, MCAP = 26276, TAB = 15, RCAP = 2^119, U = 48 (`--tune`, Section 6a).

## 4. Correctness of the recovery and its evaluation count (deterministic)

Let t be the least index with x_t = x_j for some j < t, mu = j, lambda = t - mu; for i >= mu, x_i = x_{i+lambda}; the values x_0 .. x_{t-1} are distinct. Assume mu >= 1, that the cycle positions mu .. t - 1 hold a DP, and that neither the table nor the gap test halts. Let a' be the first DP with index >= mu (a' < t). DPs with index in [t, a' + lambda) repeat values of x_mu .. x_{a'-1}, which hold no DP, so the first repeated DP is b = a' + lambda with a = a', L = lambda, and every DP with index below b has been stored (all of them have index below t). Let s be the largest DP index below mu, or s = 0 (the start) if there is none; s is the entry stored just before a, and s < mu. Then x_s != x_{s+L} and the least m >= 1 with x_{s+m} = x_{s+m+L} is m = mu - s, so the lockstep returns (x_{mu-1}, x_{mu-1+L}), distinct with equal F, after exactly mu - s rounds; x_s = x_q cannot occur since s < mu and q = s + L < t. Every stored index is the sum of the stored gaps up to its entry (each gap below 2^119 is stored exactly), so passes 1 and 2 return exact indices; the table comparison is on the whole value x < 2^142, so it is exact.

Grouped test. Since AND(x_a, x_b, x_c, x_d) <= min(x_a, x_b, x_c, x_d) as integers, every group holding a DP is a hit, and within a hit the DPs are handled in slot order with their own indices: the table, the detection of the first repeated DP and the stored indices are exactly those of a test after every step. Evaluation count. Write D1 = a' - mu, D2 = mu - s and D3 = q - r, where r is the largest stored index at or below q (pass 2). The run uses e <= b + 3 = t + D1 + 3 trail evaluations, D3 positioning evaluations and 2 D2 lockstep evaluations. Hence (Lemma 2, this statement) the attempt returns a collision whenever, in addition to the assumptions above and fp <= FPCAP, t + D1 + 3 + D3 + 2 D2 <= B and D3 + 2 D2 <= RCAP: the trail reaches index b (and the end of its group) before the counter is exhausted (the counter is tested per block and B is a multiple of 48, so every index up to B is reached), and the recovery allowance min(B - e, RCAP) covers D3 + 2 D2.

## 5. Success probability for a uniformly random function

In this section F is a uniformly random function on the N field elements (lazy sampling) and x_0 any fixed element. D = (2^126 + 1) T = 2^141.64033 is the exact number of DPs (the field elements below DELTA = D < p), theta = D / N = 2^-112.35967. Every index of a run is at most B < 2^128. D_lo = D - 2^128, theta_lo = D_lo / N, theta_hi = D / (N - 2^128).

Lemma 1. (i) P(t > m) = prod_{i=1..m} (1 - i/N) <= exp(-m (m + 1) / 2N): t > m means that x_0 .. x_m are distinct, and given distinct x_0 .. x_{i-1}, x_i = F(x_{i-1}) is a fresh uniform value. (ii) For 1 <= l <= m, P(t = m, lambda = l) <= P(x_0 .. x_{m-1} distinct, x_m = x_{m-l}) <= 1/N, and P(t = m, mu = 0) <= 1/N. (iii) Given x_0, t and mu, the sequence x_1 .. x_{t-1} is uniform over the sequences of t - 1 distinct elements different from x_0. Hence, for any order in which the positions of [1, t) are revealed (the next position may depend on the values revealed so far), the next revealed value is uniform over the elements not yet used; when j < 2^128 positions have been revealed, it is a DP with conditional probability (D - k) / (N - 1 - j) for some k <= j + 1, which lies in [theta_lo, theta_hi].

Lemma 3 (coupling of the gaps). On one probability space with the run there are random variables G1, G2, G3, mutually independent and independent of (t, mu), each geometric with P(G = j) = theta_lo (1 - theta_lo)^j for j >= 0, such that whenever t <= B: (a) D2 <= G2 + 1; (b) if the cycle positions [mu, t) hold no DP then G1 >= lambda; (c) otherwise D1 <= G1 and D3 <= G1 + G2 + G3 + 1.
Construction. Draw x_0, t and mu with their law; then reveal the values x_1 .. x_{t-1} in four stages. Each revealed value is produced from a fresh uniform U in [0, 1): it is a DP iff U < pi, pi its conditional DP probability given everything drawn so far (pi >= theta_lo by Lemma 1 (iii)), and the value is then chosen uniformly among the unused DPs, or the unused non-DPs. By Lemma 1 (iii) this produces exactly the conditional law of x_1 .. x_{t-1} given (x_0, t, mu); the values x_t, x_{t+1}, ... are then determined. Stage A reveals positions mu - 1, mu - 2, .., 1 until the first DP (s := its position) or until position 1 is done (s := 0). Stage B reveals mu, mu + 1, .., t - 1 until the first DP (a' := its position) or until t - 1 is done. Stage C runs only if a' exists and q = s + lambda > a': it reveals q, q - 1, .., a' + 1 until the first DP. Stage D reveals the remaining positions. For stage X in {A, B, C} let J = 1{U < theta_lo} along the U's of that stage, followed by an auxiliary i.i.d. uniform sequence of its own (independent of everything); G_X is the number of J = 0 before the first J = 1. Each stage ends at a stopping time, so its U's followed by its auxiliary sequence form an i.i.d. uniform sequence independent of everything drawn before the stage; hence G2 = G_A, G1 = G_B and G3 = G_C are geometric(theta_lo), mutually independent and independent of (t, mu). Since J = 1 implies a DP:
(a) Stage A ends at the DP s after mu - s - 1 non-DPs, or exhausts after mu - 1 non-DPs (s = 0): G2 >= mu - s - 1 = D2 - 1.
(b) If [mu, t) holds no DP, stage B reveals lambda non-DPs: G1 >= lambda.
(c) Otherwise stage B reveals D1 = a' - mu non-DPs before a': G1 >= D1. For D3 (stored indices at or below q are the start and the DPs, since q < t <= b): if q > a', stage C either finds a DP r' > a' after q - r' non-DPs (r = r', G3 >= D3) or reveals q - a' non-DPs (r = a', a stored DP, G3 >= q - a' = D3); if q = a', D3 = 0; if mu <= q < a', the positions (s, q] hold no DP, so r = s and D3 = q - s < a' - s = D1 + D2 <= G1 + G2 + 1; if q < mu, r = s and D3 = q - s < D2 <= G2 + 1. In every case D3 <= G1 + G2 + G3 + 1.

Lemma 4. Let X = 2 G1 + 3 G2 + G3 + 6, X_R = G1 + 3 G2 + G3 + 3 and u = (2B + 1) / 2N. The attempt on a uniformly random function succeeds with probability at least
1 - e^(-B (B + 1) / 2N) E[e^(u X)] - B / D_lo - B / N - P(X_R > RCAP) - P(table overflow) - E_W - P(fp > FPCAP).
Proof. If t + X <= B, the cycle holds a DP, mu >= 1, X_R <= RCAP, the table does not overflow, no gap reaches 2^119 and fp <= FPCAP, then t <= B and Lemma 3 gives D1 <= G1, D2 <= G2 + 1 and D3 <= G1 + G2 + G3 + 1, so t + D1 + 3 + D3 + 2 D2 <= t + X <= B and D3 + 2 D2 <= X_R <= RCAP; by Lemma 2 the attempt succeeds. The failure probability is at most the sum of the following terms (a union bound on one probability space; no independence between the events is used).
(a) Trail. X is independent of t, so P(t + X > B) = sum_k P(X = k) P(t > B - k). For k <= B, P(t > B - k) <= exp(-(B - k)(B - k + 1) / 2N) by Lemma 1 (i), and (B - k)(B - k + 1) = B (B + 1) - k (2B + 1) + k^2 >= B (B + 1) - k (2B + 1); for k > B the exponent B (B + 1) - k (2B + 1) is negative, so the same bound exceeds 1. Hence P(t + X > B) <= e^(-B (B + 1) / 2N) E[e^(u X)].
(b) DP-free cycle. P(t <= B, [mu, t) holds no DP) <= P(t <= B, G1 >= lambda) = sum_{m <= B} sum_{l <= m} P(t = m, lambda = l) (1 - theta_lo)^l <= B (1 - theta_lo) / (theta_lo N) <= B / D_lo, by Lemma 1 (ii) and the independence of G1 and (t, mu).
(c) Start on the cycle. P(t <= B, mu = 0) <= B / N by Lemma 1 (ii).
(d) Recovery allowance. For v = theta_lo / 4: P(X_R > RCAP) <= e^(-v RCAP) E[e^(v X_R)] = e^(-v RCAP) e^(3v) M(v)^2 M(3v) <= (256 / 9) e^(-theta_lo RCAP / 4), with M as below (M(v) <= 4/3, M(3v) <= 4, e^(3v) <= 4).
(e) Table. Stored DPs have index below t (indices in [t, b) repeat x_mu .. x_{a'-1}, which hold no DP) and t <= B on the success path; revealing positions 1, 2, .. in increasing order, by Lemma 1 (iii) their number is dominated by Binomial(B, theta_hi), mean mu_B = B theta_hi = 25,399.08 < MCAP + 1, so P(more than MCAP) <= exp(-mu_B) (e mu_B / (MCAP + 1))^(MCAP + 1) = e^-15.0008 <= e^-TAB (`table_exp`, as in 69e14209).
(f) Gap width (69e14209, Lemma 2 (e)): every stored index is below t <= 2^128 (block j = 0 holds the fixed start x_0, so its exponent is 2^118 - 1 there; the change is below 10^-30 and covered by the rounding of exp_neg_ub), so a stored gap of 2^119 or more leaves at least 2^119 - 1 consecutive indices below t with no DP, which contain a whole aligned block [j 2^118, (j + 1) 2^118); at most 2^10 such blocks lie below 2^128, and by Lemma 1 (iii) each is DP-free with probability at most (1 - theta_lo)^(2^118) <= e^-(theta_lo 2^118). E_W = 2^10 e^-49.8740 = 2.2e-19.
(g) False hits. Split the groups into those whose four values all have index below t (fresh values) and the others. A group of the second kind lies in [t, e] or holds index t - 1 or t: there are at most (e - t) / 4 + 2 <= (D1 + 3) / 4 + 2 of them, at most 2^115 unless D1 > 2^117 - 11, which on the success path (D1 <= G1) has probability at most P(G1 >= 2^117 - 11) <= e^-(theta_lo (2^117 - 11)) = e^-24.937 (`fp_fail_ub` evaluates e^-(theta_lo 2^117) and the difference is below 10^-30). For a group of fresh values, given everything before it, each of its values in turn is uniform over at least N - 2^128 elements (Lemma 1 (iii), or directly: a fresh value of the walk is a fresh uniform value). Write x = h 2^142 + l with l < 2^142 and h <= 2^112 (x < p); AND(x_1..x_4) < 2^142 iff the AND of the four h is 0. Among h-tuples with entries in [0, 2^112], at most 15^112 have all entries below 2^112 and AND 0 (each of the 112 bit positions avoids the pattern 1111), and at most 4 (2^112 + 1)^3 contain the value 2^112; the low parts take 2^568 values. So the group is a false hit with conditional probability at most q = [15^112 + 4 (2^112 + 1)^3] 2^568 / (N - 2^128)^4 <= [(15/16)^112 + 4 (2^112 + 1)^3 / 2^448] (2^254 / (N - 2^128))^4 = 7.2574e-4 (`fq_ub`, fixed point rounded up). Hence the false hits among the at most B / 4 groups of fresh values are dominated by Binomial(B / 4, q), of mean mu' <= mu = ceil((B / 4) q); by the Chernoff bound P(Bin > (1 + d) mu') <= e^-(d^2 mu' / 3) with d = 2^-30, and d^2 (mu - 1) / 3 >= 200 (asserted), this has probability at most e^-200. Together P(fp > FPCAP) <= e^-200 + e^-24.937 = 1.48e-11. (q bounds the probability that a group of fresh values passes the test at all, so the bound holds whichever hits fp counts; the program counts only hits without a DP.)
Moment generating function. For G geometric(theta_lo) and 0 <= v < theta_lo, M(v) = E[e^(v G)] = theta_lo / (1 - (1 - theta_lo) e^v) <= theta_lo (1 - v) / (theta_lo - v), using e^v <= 1/(1 - v); and e^(6u) <= 1 / (1 - 6u). So E[e^(u X)] = e^(6u) M(2u) M(3u) M(u) <= [1 / (1 - 6u)] prod_{j=2,3,1} D_lo (2N - j (2B + 1)) / (N (2 D_lo - j (2B + 1))) = 1.00023373 (`mgf_ub`, fixed point rounded up).
Values at the filed budget (`plan`, exact integer arithmetic, every term rounded in the safe direction): trail term 0.60996074; B / D_lo = 3.8949e-5; B / N = 5.8e-39; recovery allowance 4.207e-10; table e^-15 = 3.059e-7; E_W = 2.2e-19; false hits 1.48e-11. Success >= 0.39000000258955871056 >= 0.39. One attempt: no restart, amplification or advice.
Comparison. With fixed caps (69e14209) the gaps enter as d - 1 >= KD / theta_lo and G = KG / theta_lo (KD = 9.47, KG = 9.65), each charged in full (S = n + d trail evaluations and 3G + d - 1 recovery evaluations, about 47.9 / theta evaluations beyond n), plus their tail probabilities e^-KD and e^-KG and the short-cycle term n d / N. Here (as in 2710fcc6) the gaps enter only through E[e^(u X)] - 1 = 2.34e-4, about u E[X] = 6 u / theta_lo, and the budget B exceeds the random-function minimum (1 - e^(-B^2/2N) = 0.39) by 2^0.00044.

## 6. Operation ledger (unit: target compressions; every operation 1/1392)

Machine: the Pallas field RAM of the cost model with 256-bit words, a declared file of 392 registers of 256 bits and 4-byte instructions (both counted in memory, Section 7; the 4-byte machine of 1533f8f0). Field ADD and MUL 1/C each; every other primitive word operation (AND, OR, shift, comparison, conditional branch, register move, load or store, random word) 1/C. A comparison and a conditional branch are two operations. Instructions outside the listed primitives are charged as their primitive constituents: an unconditional jump is a branch (1), a register move is a load/store-class move (1), RET is a branch on the link register (1), and CALL is a move of the return address into lr plus a branch (2). No reference permutation is called; every evaluation executes the 807 operations of `STEP`. The 327 step constants live in registers; no field constant is an immediate.

Trail, one block of 48 steps (807 per step, 5 per group of 4, + 2 per block):
```
block:  STEP x0 -> x1             ; 807 field operations (copy reads x0, writes x1)
        STEP x1 -> x2
        STEP x2 -> x3
        STEP x3 -> x0
        AND   t, x1, x2           ; the group test (5 operations)
        AND   t, t, x3
        AND   t, t, x0
        CMPLT g, t, DELTA         ; g := (AND < DELTA): every group with a DP passes
        BZ    g, next0            ; not a hit: skip the inline hit handler of group 0
        <hit handler of group 0>  ; executed only on a hit, falls through to next0
next0:  ...                       ; groups 1 .. 11 the same
next11: SUB   c, c, 48
        BNZ   c, block            ; else halt: budget
```
Hit handler of group g (W_HIT = 11 per hit, besides the DP handlers): for each slot j = 0..3 in order CMPLT g, x_(j+1 mod 4), DELTA; BZ g, slot_next (8; g is free once the group test has branched); a hit with no DP then ADD pidx, pidx, 1; CMPLT g, lidx, pidx; BNZ g, halt_fp (3; pidx = fp, lidx = FPCAP, both recovery-only registers): 8 + 3 = 11. A slot holding a DP runs, inline, SUB idx, BS, c; ADD idx, idx, 4g + j + 1; MOV A, x_(j+1 mod 4) (the staging register A, recovery-only, so the ring stays intact); CALL dph (2), and the shared DP handler dph is MOV cur, lr (lr saved in the recovery-only register cur); MOV bp, 0; CALL scan (2); CMPLT g, cnt, MCAPR; BZ g, halt_table; CALL insert (2); MOV lr, cur; RET: W_DP = 16 executed per DP event, besides the scan and the insertion, which compare and store A (BS holds B, MCAPR holds MCAP).
Table scan per entry examined (W_SCAN = 19 charged, 18 executed; bp is the entry's bit offset): SHR j, bp, 8; AND sh, bp, 255; SHL a, j, 5; ADD a, a, TAB0; LOAD w0, [a]; ADD a, a, 32; LOAD w1, [a]; SHR w0, w0, sh; SUB s2, R255, sh; SHL w1, w1, s2; SHL w1, w1, 1; OR v, w0, w1; AND v, v, M142; CMPEQ f, v, x; BR f, hit; ADD bp, bp, 261; CMPLT g, bp, END; BR g, scan. A 142-bit field at bit offset o lies in words o >> 8 and o >> 8 + 1 (o mod 256 + 142 <= 397 < 512); the two shifts by 255 - sh and 1 keep every shift count in 0..255.
Insertion (W_INS = 40 charged, 37 executed): SUB gp, idx, last; CMPLT g, gp, GLIM; BZ g, halt_gap; MOV last, idx (4); value field at END, a two-word read-modify-write: SHR j, END, 8; AND sh, END, 255; SHL a, j, 5; ADD a, a, TAB0; LOAD w, [a]; SHL t, x, sh; OR w, w, t; STORE [a], w; ADD a, a, 32; LOAD w, [a]; SUB s2, R255, sh; SHR t, x, s2; SHR t, t, 1; OR w, w, t; STORE [a], w (15); gap field: ADD e2, END, 142 and the same 15 with e2 and gp (16); ADD END, END, 261; ADD cnt, cnt, 1 (2).
Index passes (W_POS = 24 charged per entry walked; pass 1: ADD e2, bp, 142 and the 13-operation two-word field read of the gap (as in the scan, with M119), MOV pidx, idx, ADD idx, idx, gap, ADD bp, bp, 261, CMPLT g, bp, KEND, BR g: 19; pass 2: the gap read (14), ADD cur, cur, gap, CMPLE f, cur, q, BZ f, done, MOV lidx, cur, MOV lbp, bp, ADD bp, bp, 261, CMPLT g, bp, END, BR g: 22). Each pass walks at most MCAP entries: 2 MCAP W_POS. The two values read after the passes (entry k - 1 and the pass-2 entry, 14 each) and the allowance left := min(c - 4 (g + 1), RCAP) (SUB, SUB, CMPLT, BZ, MOV: 5) are in MISC.
Recovery (W_REC = 9 per evaluation besides STEP). The recovery holds one copy of STEP as a subroutine (entered by CALL, left by RET through the link register lr), shared by the positioning walk and both lockstep walkers: positioning walk BZ j, done; SUB j, j, 1; BZ left, halt; SUB left, left, 1; CALL step (2); (RET 1); BR walk (8 executed per evaluation, plus the final BZ j; charged 9); lockstep per 2 evaluations: CMPLT g, left, 2; BNZ g, halt; SUB left, left, 2; MOV x, A; CALL step (2); (RET 1); MOV nA, x; MOV x, B; CALL step (2); (RET 1); MOV nB, x; CMPEQ f, nA, nB; BR f, found; MOV A, nA; MOV B, nB; BR lock (18 = 2 W_REC). Every recovery evaluation also counts against the budget: the allowance is at most the counter's remainder.
Messages: W = kappa A - E0_0 (MUL, ADD); tau = W^INV5; U = U0 + a tau; V = V0 + b tau; m0 = U^INV5 - c_{0,0}; m1 = V^INV5 - c_{0,1}; the same for B. x^INV5 by square-and-multiply is 377 operations; MSG_OPS = 2 (3 * 377 + 7) = 2,276 (the extra MUL per message is in SETUP_D).
Fixed part: at most MCAP + 1 DP events, each scanning at most MCAP entries and inserting once: (MCAP + 1)(16 + 19 MCAP + 40) = 13,120,106,100; index passes 2 MCAP * 24 = 1,261,248; MSG_OPS 2,276; 327 constant loads; table zeroing 4 operations per word (STORE, ADD, CMPLT, BR) over 26,791 words = 107,164; MISC = 2^20 + SETUP_D = 1,049,813: a generous fixed charge for the loop control of the setup exponentiations (kappa^-1, the fifth roots of the messages) and the decoding of the 327 recipe fields (at most about 10^4 operations), the coins, the kappa setup, masks, the loads of BUDGET, RCAP, FPCAP and MCAP, the allowance, the two value reads, halts and report: OTHER_FIXED = 13,122,526,928. Hits: at most MCAP + 1 groups hold a DP (each such group holds a DP event) and at most FPCAP + 1 are false hits (the halt runs at the (FPCAP + 1)-th): (MCAP + 2 + FPCAP) W_HIT.

Worst case. Let e_T be the trail evaluations and e_R the recovery evaluations of a run: e_T + e_R <= B (one counter) and e_R <= RCAP (the allowance); e_T is a multiple of 4 (whole groups). At most e_T / 4 <= B / 4 group tests and B / 48 block tails run. The work is at most 807 (e_T + e_R) + 5 e_T / 4 + 2 B / 48 + 9 e_R + 11 (MCAP + 2 + FPCAP) + OTHER_FIXED <= 807 B + 5 B / 4 + 2 B / 48 + 9 RCAP + 11 (MCAP + 2 + FPCAP) + OTHER_FIXED, whatever the halt. With the offline derivation PREP_OPS = 2^58 (Section 6a):
```
807 B                136559705869590143853392323864276777329888
5 B / 4                 211523707976440743267336313296587325480
2 B / 48                  7050790265881358108911210443219577516
9 RCAP                    5981525981032121428067131771261550592
11 (MCAP + 2 + FPCAP)      794648273395025461959029427972932069
OTHER_FIXED                                          13122526928
PREP_OPS                                      288230376151711744
total                136785056542086893101658885779605092954217
```
log2(total / 1392) = 126.2080190; claimed 126.20802, the least 5-decimal q with total^100000 <= 1392^100000 * 2^(q 10^-5) (integer test). Per trail step 808.2917 operations (807 + 5/4 + 2/48), plus 11 per hit (about 0.002 per step). `--selftest` runs the search at width 14 with the real step program and checks its counted operations against the formula for its parameters (budget 240, recovery at most 160, table of 64, at most 64 false hits).

### 6a. Offline derivation: integer routines, counts and the charge

Everything the attempt loads is fixed before it starts: INV5, the line constants, the 327 constant monomials with their recipes, E0 and OUTSCALE (`build_step`), the parameter literals UNROLL, T_DP, MCAP, TAB, RCAP and BUDGET, and FPCAP (`fpcap`); BUDGET, FPCAP, MCAP and the exponent p - 2 are stored as words (Section 7). Four offline parts produce or re-derive them, each with a count or a loop bound below. PREP_OPS = 2^58 is charged inside the total of Section 6 and declared as preprocessing_log2 = 48 (log2(2^58 / 1392) = 47.56).

Integer routines and their prices (as in 69e14209). The arithmetic of `--tune` and `--plan` is on integers below 2^1000: `--tune` records the largest operand at the metered products (`fx_ratio_ub`, `exp_neg_ub`, `table_exp`, `fq_ub`), 653 bits (the numerator times 2^256 in `fx_ratio_ub`), and asserts that it is below 1000; the other operations act on sums, differences and quotients of these. The routines are priced for 1000 bits. An integer is four 256-bit words, little endian. `Wm` (Appendix B) is a counting machine whose operations are primitives of the cost model, one operation each (ADD and SUB modulo 2^256, AND, OR, SHL and SHR by a constant, CMPLT, CMPEQ; a branch, move, load or store is counted by `other`); it runs the routines, and `--selftest` compares their results with Python integers on random operands and asserts that their worst cases equal the prices:
- Add or subtract of four words: ADD, CMPLT; twice (ADD, ADD, CMPLT, CMPLT, OR) for the carry or borrow chain; ADD, ADD: 14 operations. Shift by a constant: SHL, SHR, OR for each of the three upper words and SHL: 10. Comparison: 4 CMPLT, 3 CMPEQ, 3 AND, 3 OR: 13. An integer add, subtract, compare or shift takes at most 26 operations (8 loads, 14, 4 stores; 8 loads, 13, a branch; 4 loads, 10, 4 stores) and is charged 32.
- Multiplication, shift-and-add over 1000 multiplier bits: per bit AND, BZ, the 14-operation add, two 10-operation shifts, SUB, BNZ = 38; 14 operations of loads and set-up and 4 stores: 14 + 38 * 1000 + 4 = 38,018.
- Division with remainder, restoring, over 1000 dividend bits: per bit three 10-operation shifts (quotient, dividend, remainder), the dividend's top bit, OR, the 13-operation comparison, BNZ, the 14-operation subtraction, OR, SUB, BNZ = 63; 28 operations of loads, set-up and the 24-bit shift that puts the dividend's top bit at bit 1023, and 8 stores: 28 + 63 * 1000 + 8 = 63,036. A remainder is a division.

Counts. Each offline routine adds its own statement count to CNT, its loop bound times the operations per iteration, rounded up (`exp_neg_ub`: for its loop of 100 terms 201 products, 101 divisions and 102 additions, shifts or comparisons; `fx_ratio_ub` 1, 1 and 2; `fx_mul_ub` 1, 0 and 3; `mgf_ub`, `rcap_ub`, `fq_ub`, `fpcap`, `fp_fail_ub`, `success_fp`, `budget_of`, `least_k` and `derive` their own; the source shows each increment beside its statement). (1) `--tune` is the parameter search: a cell (U, TAB) takes the largest MCAP with memory <= 2^20 (bisection on MCAP) and the largest T in [40000, 65535] passing the table bound (bisection on T, 16 probes of `derive` and `table_exp`), valued by its exact ledger total; a descent from (48, 15) tries U +- 4 and TAB +- 1 and moves to any strictly lower total until no move. It evaluates 5 cells, asserts that its result equals the program's literals (48, 15, 51075, 26276), and counts 715,977 additions (with subtractions, comparisons and shifts), 1,174,804 multiplications and 553,669 divisions (with remainders): 79,587,688,820 word operations at the prices above (2^36.21). (2) One run of `plan` counts 15,223, 24,757 and 11,598: 1,658,399,350 word operations, below 2^31 (asserted). (3) The recipe search `_terms`, at its loop bounds (unchanged): 7,885,127,349,792. (4) `build_step` and the line, at their loop bounds (unchanged): bounded by 2^17 (asserted). The offline total is at most 79,587,688,820 + 2^31 + 7,885,127,349,792 + 2^17 = 7,966,862,653,332 = 2^42.86; `--tune` asserts that it is below PREP_OPS. The charge 2^58 exceeds it by a factor 2^15.14, which covers every statement not counted (loop control, comparisons of small values, bookkeeping).

## 7. Memory: the allocation list

The table is one array of 256-bit words; entry r (r = 1 .. MCAP) occupies bits 261 (r - 1) .. 261 r - 1: the DP value (142 bits, x < DELTA < 2^142) and the gap to the previous stored index (119 bits). 26,276 entries are 6,858,036 bits, 26,790 words; one pad word follows, because every field read loads the word holding the field's first bit and the next word. The start x_0 (index 0) is its own word.
Bytes at the peak (the search; the setup holds a subset of the same items), every item allocated once:
- table: 26,791 words = 857,312;
- start word: 32;
- code: 40,676 instructions at 4 bytes = 162,704, itemised as 48 unrolled steps 48 * 807 = 38,736, per group of 4 (12 groups) the test 5, the inline hit handler 8 (slot tests) + 3 (false-hit count, compare, branch) + 16 (per slot SUB idx, ADD idx, MOV A, CALL dph): 32 per group, 384, the block tail 2, one recovery copy of STEP (a subroutine ending in RET) with 20 control instructions 827 (positioning 7, lockstep 16 with the RET counted once in the copy: 23 > 20, the excess 3 is taken from the 400 below), 327 constant loads, and 400 others (the shared DP handler 8, scan 18, insertion 37, index passes 19 + 22, two field reads 28, recovery control and allowance 25 + 3, roots and messages (two square-and-multiply loops and the line arithmetic) 32, set-up 25, recipe decoding loop 16, table zeroing 4, halts and report 14, returns and back-edges 4: 255; 400 charged);
- constants: (327 step constants at kappa = 1, E0 (3), line constants U0, V0, a, b, c00, c01, INV5 (7), and the literal words BUDGET, FPCAP, MCAP and p - 2 (4)) = 341 words = 10,912 (OUTSCALE is not stored: the attempt never divides by it);
- register file: 392 registers = 12,544 (the 347 registers of STEP, including x = x0, the group ring x1, x2, x3 and the group AND t' (4), and at most 41 control registers: DELTA, g, f, c, BS, idx, cnt, END, last, gp, GLIM, bp, j, sh, a, w0, w1, s2, v, t, e2, R255, M142, M119, TAB0, KEND, q, s, pidx, cur, lidx, lbp, A, B, nA, nB, L, left, RCAP, lr (the link register of CALL/RET), MCAPR: 41. Trail-time uses of recovery-only registers, none of which the trail's scan or insertion writes: pidx = fp, lidx = FPCAP, A = the staging register of a DP, cur = the saved lr of the DP handler; the walk counter of the positioning walk is j, which the passes no longer use by then; g serves the slot tests);
- kappa setup: 5,056 (two power chains 2 x 63 words = 4,032; one 16-bit recipe field per constant, 654 bytes in 21 words = 672; three words 96; 64 setup instructions at 4 bytes 256).
Total 857,312 + 32 + 162,704 + 10,912 + 12,544 + 5,056 = 1,048,560 <= 2^20 = 1,048,576: the memory term of the score is 0. `plan` asserts the sum.
Output: after the lockstep returns, the two messages are computed in step working registers (y1, y2, z0, z1, z2, t1, t2, u, x5, all of the declared file and dead after the recovery) and written out as the report; no buffer is added. Preprocessing: the offline derivation of Section 6a runs first, before the table exists. Its code and data are held in the address range of the table (857,312 bytes), which the setup zeroes afterwards (4 operations per word, in the table zeroing of Section 6); the attempt's own items without the table are already in place (191,248 bytes: start word, code, constants, register file, kappa setup). Offline code: at most 16,384 instructions = 65,536 bytes. The offline source (Appendix B without the attempt, the word machine and the self-checks) has 1,356 operator, call and subscript nodes (`--selftest` counts them with `ast`); a node compiles to at most 8 instructions (its operand loads, one operation or call), and the three integer routines have at most 300 instructions: 8 * 1,356 + 300 = 11,148 <= 16,384 (asserted). Offline data: at most 262,144 bytes: the round constants and MDS (225 words, 7,200 bytes), the cache of `gap_width_ub` (one entry per T value probed, at most 5 cells * 17, of 3 words: 8,160 bytes), the monomials of `build_step` (327 * 2 words, 20,928 bytes) and at most 100 working integers of 4 words (12,800 bytes): 49,088 bytes; the constants and recipes it writes are the resident ones. Code and data together are at most 327,680 bytes, within the table's range. The live bytes of the offline phase are at most 191,248 + 65,536 + 262,144 = 518,928, below the search peak (`plan` asserts it): the peak of the whole computation is the search peak, 1,048,560 bytes.
Instruction format: 32 bits, a 5-bit opcode and three 9-bit fields (register numbers below 512, or a 9-bit offset or small immediate: shift counts, 4g + j + 1, 32, 48, 142, 261, the skip of an inline handler); jumps and calls use one register field and an 18-bit offset. Every 256-bit constant (DELTA, M142, M119, GLIM = 2^119, RCAP = 2^119, BS = B, FPCAP, MCAPR = MCAP, the step constants) is in a register.

## 8. Premise H1 (score-critical), its deviation model and its price

H1 (claim.json `H1-random-function-model`). Statement: at the filed budget B = 169218966381152594613869050637269860384, where Lemma 4 gives 0.39000000259 for a uniformly random function, the search of Section 3 on the real map F (the coins of the attempt, Section 1) succeeds with probability at least 0.39. It is a declared heuristic: the success probability on the fixed target is not proved, it is the random-function value carried to the real map. The recovery, ledger and memory are proved exactly (Sections 4, 6, 7); the equality of the step program with the reference rounds and the offline counts are computational claims checked by `--selftest` and `--tune` (Appendix B), which the reader can rerun. The same premise at the same budget form is declared by the in-review r = 56 entries 69e14209, 874894cf, 43caeb6a, 9fb982e8 and 3a1b25b6.
Deviation model (the sensitivity table). The model is a uniformly random map on N / c points with the same DP fraction theta: Lemma 4 then holds with N replaced by N / c, so the trail term becomes exp(-c B (B + 1) / 2N) E[e^(c u X)], and the DP-free-cycle and start-on-cycle terms become c B / D_lo and c B / N; the allowance, table and gap-width terms (which depend on theta only) are unchanged. Under this model (`plan`, exact): c = 1, 0.9, 0.75, 0.6, 0.5, 0.4 give 0.3900, 0.3591, 0.3098, 0.2566, 0.2190, 0.1794. The table is valid under that model only; it is not derived from a collision-rate factor alone.
Price of a margin. Restoring 0.39 under a shortfall costs a larger budget: B (1 + epsilon) adds log2(1 + epsilon) bits, 0.0144 at 1 %, 0.0426 at 3 %, 0.1375 at 10 %; under the deviation model a rate shortfall to c needs B / sqrt(c) to restore 0.39 (c = 0.9: +0.076 bit). The claim is made at epsilon = 0, with a margin of 2.6e-9 in the random-function bound.
Evidence: the organizer-run experiments of Section 9 (observations only; they carry no part of the bound).

## 9. Experiments: the claim's walk on its input line

Two organizer-run experiments (`experiments/manifest.json`, kind `python-message-pairs-v1`, event `digest-xor-mask`, mask `ff3f` then zeros = the 14 low bits of the digest, expected zero; `experiments/exp_linewalk.py`, standard library only; the request's experiment id selects the experiment). Both use the claim's input line, `message()` and E0_0, and draw the coins as `attempt` does: kappa and x_0 are the low 254 bits of two 256-bit words (the two halves of SHAKE-256 of the trial seed), kappa = 1 if its word is 0. A trial returns the two line messages of a pair or two nulls; the organizer recomputes both digests and checks the event.

`search-w14-raw-bits`. The claim's search of Section 3 on x in [0, 2^14), where the walk is x -> the 14 low bits of digest(message(kappa x - E0_0)); x_0 is the low 14 bits of its word; one trail in blocks of 48, the DP test once per group of 4 on the AND of the outputs (then per value on a hit), DP iff x < 2^11 (theta = 1/8), table of 64, one budget of 192 evaluations (4 blocks) for the trail and the recovery together, the recovery at most 64 of them, single-gap recovery without other caps. This map is the claim's F without the division by OUTSCALE_kappa. That division is a bijection of the field; it cannot enter the digest-bit event, which the organizer checks on the digests themselves, and a bijection applied after a map does not in general preserve its trajectories, distinguished points or cycles. The experiment is therefore an observation on a related map, not on F. For comparison, the same search on a uniformly random map of 2^14 points succeeds with probability 0.4873 (our measurement, 200,000 runs in four seeded batches: 0.4884, 0.4889, 0.4888, 0.4830; not used by any bound). The experiment's DP threshold is the power of two 2^11, not a non-dyadic DELTA, and it has no false-hit cap, gap cap or packed table. At this width the gaps are not small beside the trail (1 / theta = 8 against a trail of about 150; at 14 bits the group test passes often, which exercises the hit handler), so the budget and the success value are not those of a scaled copy of the full-width bound; the experiment exercises the program logic (group test, shared budget, allowance, table, passes and recovery) on the real line map.

`trail-w14-exact-walk` (unchanged from 69e14209). The claim's walk itself, at full width in the 254-bit field: x_{i+1} = F(x_i) = digest(message(kappa x_i - E0_0)) / OUTSCALE_kappa with OUTSCALE_kappa = OUTSCALE_1 kappa^(5^62) (OUTSCALE_1 is `outscale_1` of Appendix A, the same literal as in the program), 128 outputs. The event is the first repeat among the 14 low bits of the raw digests along the trail; the trial returns the line messages of the two trail points with equal bits. Table, distinguished points and recovery are not part of this experiment. For a uniformly random function the 128 low-bit values are independent and uniform until the first repeat of the full value (probability below 2^-200 in 128 steps), so the event has probability 1 - prod_(i=1..127) (1 - i / 2^14) = 0.3919, exactly.

Reading the counts. Each trial uses only its own seed. The programs and their parameters were fixed before their first organizer run; the seeds are the organizer's public seeds and no seed search was made. No organizer count exists at filing time; whatever the counts are, they are observations: no probability or interval is drawn from them, and the success bound of Section 5 assumes nothing about the trials (no independence or identical distribution of the trials is used). A local smoke run of `search-w14-raw-bits` on 40 seeds (`'%064x' % (7919 i + 1)`, i < 40) returned 19 pairs, each meeting the event.

Scope: neither experiment runs the full-width search of about 2^127 steps. `trail-w14-exact-walk` executes F at full width, for 128 outputs, and tests the digest-bit statistics of its trail; `search-w14-raw-bits` exercises the search on the related reduced map. Carrying the behaviour of F to the full-width search is H1 (Section 8).

## 10. Provenance and credits

- 69e14209 (Jbenisek): the base package: the walk, the line, the 807-operation step program, the kappa setup, the table layout and its operation listings, the integer routines and offline accounting, the experiments' line code and the memory accounting, all reused; the program of 2710fcc6, which this entry edits, is itself an edit of the program printed there.
- 3a1b25b6 (newjordan) and 9fb982e8 (pierce403): the r = 56 point, the 807-operation step with the multiplicative coin, and the 142-bit value / 119-bit gap table entry (via 69e14209).
- 43caeb6a (mitchuski): the single-gap recovery; 1533f8f0 (cryptogakusei): its port and the 4-byte instruction machine; 874894cf (lamb356): the random-function budget with H1 declared; 56fb07fc (Jbenisek): the line and the search (all via 69e14209).
- 2710fcc6 (ours, in review): the shared evaluation budget with the recovery allowance (Section 3), the evaluation-count identity (Section 4), the coupling of the three gaps to independent geometric variables and the moment-generating-function convolution with the trail law (Section 5, Lemmas 3 and 4), the CALL/RET recovery charge, the budget form of `search-w14-raw-bits`.
- New in this entry: the distinguished-point test once per group of four outputs on their AND, with the register ring of the unrolled copies (Sections 3, 4, 6), the false-hit bound and cap (Lemma 4 (g), `fq_ub`, `fpcap`, `fp_fail_ub`), the renamed-copy self-check, the new ledger and memory, the re-tuned parameters (U = 48), and the grouped form of `search-w14-raw-bits`.

## Appendix A: `python3 rho.py --plan`

partial_rounds 56; C 1392; step_field_ops 807; step_add 329; step_mul 478; W_LOOP 2; W_BLOCK 2; W_REC 9; ops_per_trail_step 808.2916666666666; T_DP 51075; MCAP 26276; TAB 15; RCAP_log2 119.0; theta_log2 -112.35967032149205; k 133490227; B 169218966381152594613869050637269860384; B_log2 126.9921588832234; x 0.49459438501740866; mgf_bound 1.0002337313446568; trail_term 0.6099607421702932; eps_other 3.925524014808132e-05; success_lower_bound 0.3900000025895587; success_lower_bound_decimal 0.39000000258955871056; rate_min 1.0; rate_table 1.0 0.3900000025895587, 0.9 0.35909205251612086, 0.75 0.3097681659539033, 0.6 0.2566472338796179, 0.5 0.21898038634845182, 0.4 0.17940444500892289; mean_stored_bound 25399.078965280205; ln_P_table_overflow -15.00084741283122; cycle_term 3.894890231893471e-05; start_term 5.845614065545976e-39; rcap_term 4.207177849321976e-10; other_fixed 13122526928; gap_width_bound 2.2401999720613425e-19; prep_ops 288230376151711744; prep_log2_units 47.55705650415127; total_ops 136785056542086893101658885779605092954217; T_units 9.826512682621186e+37; time_log2 126.20801902219692; constants 327; memory table_words 26791, table 857312, start_word 32, code_instructions 40676, code 162704, constants 10912, registers 392, register_file 12544, kappa_setup 5056, total 1048560; prep_instr 16384; prep_data_bytes 262144; prep_peak_bytes 518928; outscale_1 0x8644200abf8cd4035dc449088ab93750ba0d9968f428235fce6f63bb58d8c93; plan_integer_ops add 15223, mul 24757, div 11598; plan_word_ops 1658399350; recipe_search_word_ops_bound 7885127349792

## Appendix B: the program and its ledger, `rho.py` (verbatim, standard library only; `--plan` prints the parameters and the ledger, `--tune` the parameter search)

```python
"""Generic collision search on the Orchard hash with 56 partial rounds, the permutation evaluated in an equivalent form whose every
field operation is charged: one trail of x -> F(x) = digest(message(kappa x - E0_0)) / OUTSCALE_kappa for a random coin kappa, distinguished
points, one bit-packed table (142-bit value, 119-bit index gap per entry), single-gap recovery, one evaluation budget for the trail and the recovery.

Target: poseidon-orchard-r56-prefix-v1 (initial state [m0, m1, 2^65], 8 full + 56 partial rounds, digest = state[0], no feed-forward).
Sections: 1 deployed constants (halo2_poseidon 0.2.0, copied from our own checked file), 2 the hash (reference form), 3 the input line and the
step program (`line`, `build_step`), 4 the search (`search`), 5 parameters and ledger (`plan`, `python3 rho.py --plan`; `--tune` re-derives
the parameter literals and counts the offline work at the prices of the word machine `Wm`), 6 self-checks (`--selftest`) and command line
(`--listing` prints the step program).
No outside code or library is used; standard library only.
"""
import sys
import json
import hashlib
from math import log2
from fractions import Fraction

PARTIAL = 56
LEV = "BCD"                               # the variant of this program (fixed): B whole-value DP test (compare + branch), C down-counter block, D multiplicative coin
LEV_B, LEV_C, LEV_D, LEV_1 = "B" in LEV, "C" in LEV, "D" in LEV, "1" in LEV
assert not LEV_1 or LEV_B
# ================================================================ 1 constants
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
ROUND_CONSTANTS = (
    (0x360d7470611e473d353f628f76d110f34e71162f31003b7057538c2596426303, 0x2bab94d7ae222d135dc3c6c5febfaa314908ac2f12ebe06fbdb74213bf63188b, 0x150c93fef652fb1c2bf03e1a29aa871fef77e7d736766c5d0939d92753cc5dc8),
    (0x3270661e68928b3a955d55db56dc57c103cc0a60141e894e14259dce537782b2, 0x073f116f04122e25a0b7afe4e2057299b407c370f2b5a1ccce9fb9ffc345afb3, 0x2a32ec5c4ee5b1837affd09c1f53f5fd55c9cd2061ae93ca8ebad76fc71554d8),
    (0x270326ee039df19e651e2cfc740628ca634d24fc6e2559f22d8ccbe292efeead, 0x27c6642ac633bc66dc100fe7fcfa54918af895bce012f182a068fc37c182e274, 0x1bdfd8b01401c70ad27f57396989129d710e1fb6ab976a459ca18682e26d7ff9),
    (0x162a14c62f9a89b814b9d6a9c84dd678f4f6fb3f9054d373c832d824261a35ea, 0x2d193e0f76de586b2af6f79e3127feeaac0a1fc71e2cf0c0f79824667b5b6bec, 0x044ca3cc4a85d73b81696ef1104e674f4feff82984990ff85d0bf58dc8a4aa94),
    (0x1cbaf2b371dac6a81d0453416d3e235cb8d9e2d4f314f46f6198785f0cd6b9af, 0x1d5b2777692c205b0e6c49d061b6b5f4293c4ab038fdbbdc343e07610f3fede5, 0x2e9bdbba3dd34bffaa30535bdd749a7e06a9adb0c1e6f962f60e971b8d73b04f),
    (0x2de11886b18011ca8bd5bae36969299fde40fbe26d047b05035a13661f22418b, 0x2e07de1780b8a70d0d5b4a3f1841dcd82ab9395c449be947bc998884ba96a721, 0x0f69f1854d20ca0cbbdb63dbd52dad16250440a99d6b8af3825e4c2bb74925ca),
    (0x2eb1b25417fe17670d135dc639fb09a46ce5113507f96de9816c059422dc705e, 0x115cd0a0643cfb988c24cb44c3fab48aff36c661d26cc42db8b1bdf4953bd82c, 0x26ca293f7b2c462d066d7378b999868bbb57ddf14e0f958ade801612311d04cd),
    (0x17bf1b93c4c7e01a2a830aa162412cd90f160bf9f71e967ff5209d14b24820ca, 0x35b41a7ac4f3c571a24f8456369c85dfe03c0354bd8cfd3805c86f2e7dc293c5, 0x3b1480080523c439435927994849bea964e14d3beb2dddde72ac156af435d09e),
    (0x2cc6810031dc1b0d4950856dc907d57508e286442a2d3eb2271618d874b14c6d, 0x25bdbbeda1bde8c1059618e2afd2ef999e517aa93b78341d91f318c09f0cb566, 0x392a4a8758e06ee8b95f33c25dde8ac02a5ed0a27b61926cc6313487073f7f7b),
    (0x272a55878a08442b9aa6111f4de009485e6a6fd15db89365e7bbcef02eb5866c, 0x2d5b308b0cf02cdfefa13c4e60e26239a6ebba011694dd129b925b3c5b21e0e2, 0x16549fc6af2f3b72dd5d293d72e2e5f244dff42f18b46c56ef38c57c311673ac),
    (0x1b10bb7a82afce39fa69c3a2ad52f76d76398265344203119b7126d9b46860df, 0x0f1e7505ebd91d2fc79c2df7dc98a3bed1b36968ba0405c090d27f6a00b7dfc8, 0x2f313faf0d3f6187537a7497a3b43f46797fd6e3f18eb1caff457756b819bb20),
    (0x3a5cbb6de450b481fa3ca61c0ed15bc55cad11ebf0f7ceb8f0bc3e732ecb26f6, 0x3dab54bc9bef688dd92086e253b439d651baa6e20f892b62865527cbca915982, 0x06dbfb42b979884de280d31670123f744c24b33b410fefd4368045acf2b71ae3),
    (0x068d6b4608aae810c6f039ea1973a63eb8d2de72e3d2c9eca7fc32d22f18b9d3, 0x366ebfafa3ad381c0ee258c9b8fdfccdb868a7d7e1f1f69a2b5dfcc5572555df, 0x39678f65512f1ee404db3024f41d3f567ef66d89d044d022e6bc229e95bc76b1),
    (0x21668f016a8063c0d58b7750a3bc2fe1cf82c25f99dc01a4e534c88fe53d85fe, 0x39d00994a8a5046a1bc749363e98a768e34dea56439fe1954bef429bc5331608, 0x1f9dbdc3f84312636b203bbe12fb3425b163d41605d39f99770c956f60d881b3),
    (0x027745a9cddfad95e5f17b9e0ee0cab6be0bc829fe5e66c69794a9f7c336eab2, 0x1cec0803c504b635788d695c61e932122fa43fe20a45c78d52025657abd8aee0, 0x123523d75e9fabc172077448ef87cc6eed5082c8dbf31365d3872a9559a03a73),
    (0x1723d1452c9cf02df419b848e5d694bf27feba35975ee7e5001779e3a1d357f4, 0x1739d180a16010bdfcc0573d7e61369421c3f776f572836d9dab1ee4dcf96622, 0x2d4e6354da9cc554acce32391794b627fafa96fbeb0ab89370290452042d048d),
    (0x153ee6142e535e334a869553c9d007f88f3bd43f99260621670bcf6f8b485dcd, 0x0c45bfd3a69aaa65635ef7e7a430b486968ad4424af83700d258d2e2b7782172, 0x0adfd53b256a6957f2d56aec831446006897ac0a8ffa5ff10e5633d251f73307),
    (0x315d2ac8ebdbac3c8cd1726b7cbab8ee3f87b28f1c1be4bdac9d36a8b7516d63, 0x1b8472712d02eef4cfaec23d2b16883fc9bb60d1f6959879299ce44ea423d8e1, 0x3c1cd07efda6ff24bd0b70fa2255eb6f367d2c54e36928c9c4a5404198adf70c),
    (0x136052d26bb3d373687f4e51b2e1dcd34a16073f738f7e0cbbe523aef9ab107a, 0x16c96beef6a0a848c1bdd859a1232a1d7b3cfbb873032681676c36c24ef967dd, 0x284b38c57ff65c262ab7fed8f499a9fb012387bab4f1662d067eec7f2d6340c4),
    (0x0c5993d175e81f6639e242198897d17cfc06772c1c0411a6af1dff204c922f86, 0x03bf7a3f7bd043dafcda655d1ba9c8f9f24887ad48e17759bbf53f67b1f87b15, 0x3188fe4ee9f9fafbb0cf999567f00e734c8f9cbe69f0e8279b5cd09e36d8be62),
    (0x171f528ccf6584375a39768c480d61e13af5bf77c1c42652afea99a2ec6c595a, 0x12f4175c4ab45afc196e41859b35ef88812c3286ee7000675a0563b9b8e9f1d5, 0x3a509e155cb7ebfd8f8fdcf800a9ac697e23e1aabe96cfab0e74d4d369118b79),
    (0x10f2a685df4a27c81a89920e2504c3b3984bc8f2e4c1b69e98712c65678cfd30, 0x09e5f49790c8a0e21d8d93d54ab91a0e54573c9333c56321e8a16728cc9d4918, 0x352d69bed80ee3e52bf35705d9f84a3442d17ed6ee0fab7e609a740347cf5fea),
    (0x058ee73ba9f3f293491562faf2b190d3c634debd281b76a63a758af6fa84e0e8, 0x232f99cc911eddd9cd0f1fc55b1a3250092cb92119bc76be621a132510a43904, 0x201beed7b8f3ab8186c22c6c5d4869f0f9efd52ca6bc2961c3b97c1e301bc213),
    (0x1376dce6580030c6a1c9291d58602f5129388842744a1210bf6b3431ba94e9bc, 0x1793199e6fd6ba342b3356c38238f761072ba8b02d92e7226454843c5486d7b3, 0x22de7a7488dcc7359fee9c20c87a67df3c66160dc62aacac06a3f1d3b433311b),
    (0x3514d5e9066bb160df8ff37fe2d8edf8dbe0b77fae77e1d030d6e3fd516b47a8, 0x30cd3006931ad636f919a00dabbf5fa5ff453d6f900f144a19377427137a81c7, 0x253d1a5c5293412741f81a5cf613c8df8f9e4b2cae2ebb515b6a74220692b506),
    (0x035b461c02d79d19a35e9613e7f5fe92851b3a59c990fafc73f666cb86a48e8e, 0x23a9928079d175bd5bc00eedd56b93e092b1283c2d5fccde7cfbf86a3aa04780, 0x13a7785ae134ea92f1594a0763c611abb5e2ea3436eef957f1e4ccd73fa00a82),
    (0x39fce308b7d43c574962ae3c0da17e313889c57863446d88bbf04f5252de4279, 0x1aae18833f8e1d3ac0fdf01662f60d22bef00a08c6ed38d23b57e34489b53fad, 0x1a761ce82400af018b2e80c064fd83ed27c1b3fd8f85d8a855513e033398513f),
    (0x275a03e45adda7c316dd1a87ca22e1ccdcf6af2830a502875244ca749b73e481, 0x2e5a10f08b5ab8bbeb08e47e5feabcf807e561453fc5648b58a253cfb6a95786, 0x1459cb8587208473b84e9c333b2932f1c141a5b6d594bec4e033d82cefe78ce3),
    (0x193ae5921d78b5de7b92ce810e14a40052f9332fbffcfbbd5cec7e7b338fbe1b, 0x3097898a5d0011a489111fb2c4660281374384f4a072820560224be67248e82c, 0x378d97bf8c864ae7571782fd96ce54b41979b2d1c465b4d9549980de862930f5),
    (0x2eb04ea7c01d97ec88136287ce376b08dbc7f5cb4609342137ea32a971d17884, 0x36425347ea03f6412302a1c22e49baec861cbda476804e6cead3726f1af2e7b0, 0x26b72df47408ad42cc996cd85c98a1d83f5b5ca5a19a9701ecd627e59590d09e),
    (0x130180e44e2924db1f05636c610b89aade01212ee4588f8959bece31f0a31e95, 0x219e97737d3979ba73275acaed5f579cdf7793cc89e5b52f9ea8e7bc79263550, 0x3cdb93598a5ca5283461363f81c489a23b0672dd7d42cbb49c12635df251d153),
    (0x0e59e6f332d7ed3720724b927a0ca81c4ad0447045a7c5aa2861ce16f219d5a9, 0x1b064342d51a42753d7369467222697a172cc07b9d33fbf943b0a3fcff2036bd, 0x30b82a998cbd8e8a2f363c55b2882e0b78fa9fb9171221b73eb310228a0e5f6c),
    (0x23e4ab37183acba463df7a76e858a4aa8ad71ea715be0573e46f6d4298740107, 0x2795d5c5fa4280225d33094e0beda75bacfe14640de044f2fca995e2b59914a1, 0x3001ca401e89601cd765f26dd03f4c45a6687c3df16c8fe4c26d909dee8b53c0),
    (0x0072e45cc676b08ef7bf86e89280827fe84b5bebae4e501de7fea6bdf3471380, 0x13de705484874bb5e2abe4c518ce599eb64829e2d40e41bdd0c54ddeb26b86c0, 0x0408a9fcf9d61abf315950f1211defe882bb18e5af1b05bb38915b432a9959a5),
    (0x2780b9e75b55676ebb4e4a1400ccd2c4ae4d23b0b41be9a834070cbee26886a0, 0x3a570d4d7c4e7ac3f80333ec85634ac9dc4d8fbefe24405a9405592098b4056f, 0x0c13cca7cb1f9d2cf347c247fcf09294e2cc1507bebdcc6278d2b247899520b4),
    (0x14f59baa03cd0ca4d2614a197c6b794b0b50bb2eb82df74d2e8c88f7707470e0, 0x307defee925dfb436f546e1704c39c60a51d54ede66167f5be52476e0a16f3be, 0x1960cd511a91e0607a07e7674b5a2621661106836adfe5e7380b67d80473dce3),
    (0x2301ef9c63ea84c5ca2ad0fb56672500b8ee335d88284cbe15aaf1f7712589dd, 0x029a5a47da79a488d10f4cd52be97f6bc86182d1b4246b585e68478c4d6027a9, 0x32d7b16a7f11cc962360d17d890e55cbf97fe46b6a9254282cc4f962eaae2260),
    (0x26703e48c03b81ca18e857a98d498cf7a5f2404cd7b35eb0c0cab915d5363d9f, 0x048682a35b3265bc88ac8d25a24603f1f44388bd6b89221ef691123ae112b928, 0x06b1390441fa7030d72cddc6cf06b50791d6e1715164775e3ab7defcb8d803e2),
    (0x31aa0eeb868c626d1689426dce05fcd843b360f6386a86d7bcd795414a6e2e86, 0x239464f75bf7b6af057abad3764c104b90efd8f41b2078b2ed77f5d576b99cc3, 0x0a64d4c04fd426bda45e19ed813a54aba5cc47c59654b2a7b2cb487307c1cecf),
    (0x21fbbdbb73670734576a4ad259860fb1777c7a921a062e9d1f7315322f658735, 0x31b86f3cf01705d4d9371ca2eb95acf35b86d29463d31564674324003fc52146, 0x2bfde53354377c9105ef1736d09056f613541d65157ee1ce7045f48aa4eb4f6f),
    (0x1233ca936ec24671d558f36e65f8eca7f4d5239c11d0eafa5a13a58d20011e2f, 0x27d452a43ac7dea2c437846d8e0b2b30878058d0234a576f6e70af0a7a924b3a, 0x2699dba82184e413e816ea8da493e0fa6a30641a1c3d87b2a02576b94392f980),
    (0x36c722f0efcc8803c3988baee42e4b10f18584664f8cab49608c6f7a61b56e55, 0x02b3ff48861e339b08b0f2ec89ccaa3785c38899a7b5a8336e49ac170dbb7fcd, 0x0b70d061d58d8a7f60162f4427bc657b6fc3ff4c49eb59ada8c5ae03ad98e405),
    (0x3fc2a13f127f96a4f8753adeb9d7cee2ad3de8be46ed96932e06cc4af33b0a06, 0x0c41a6e48dd23a511bd63434ac8c419f00cb3d621e171d80c12080ac117ee15f, 0x2de8072a6bd86884ed4476537169084e72aaad7e4e75339d9685213e9692f5e1),
    (0x03557a8f7b38a17f9d3496a3d9fe05ecb81cf735cc9c39c00ad01184567b027c, 0x0b5f59552f498735ee976d34282f1a37060f43363d818e5445bcb5ac00826abc, 0x0e2923a5fee7b878fedbb18570dc7300f5d646e57507e5482f2909e17e22b0df),
    (0x1d785005a7a00592c787be97020a7fddcf1cb37c3b032af6f71eed73f15b3326, 0x1ad772c273d9c6df0ba5fedcb8f25bd2a590b88a3b0602940acfbfb223f8f00d, 0x027bd64785fcbd2aa78f3275c278234b810510eb61f0672dc1ce13d60f2f5031),
    (0x20800f441b4a0526ce6f8ffea1031b6de224313469457b8e8337f5e07923a853, 0x3d5ad61d7b65f9386eea2cd49f4312b436cdc8eed662ad37a33d7bed89a4408a, 0x13338bc351fc46dd02c5f91be4dd8e3d1df96cc03ea4b26d3bbbae94cc195284),
    (0x25e52be507c92760b87db1e2af3ea923646c49f9b46cbf19c5271c297852819e, 0x1c492d64c157aaa471096d8b1b983c98a34c83a3485c6b2d5c380ab701b52ea9, 0x0c5b801579992718f4e6c5e7a573f592d43487bc288df682a20c0b3da0da4ca3),
    (0x1090b1b4d2bebe7a68695c0cd7cbf43d584e9e62a7f9554e7ea33c93e40833cf, 0x33e38018a801387a68f5ce5cbed19cad1b218e35ecf2328ee383e1ec3baa8d69, 0x1654af18772b2da5eef8d83d0e876bac5f4a02d28729e3aeb76b0b3d787ee953),
    (0x1678be3cc9c6799344742de88c5ab0d5bb0893870367ec6cef7ce6a013265477, 0x3780bd1e01f34c227ff9c6be546e928adaf1818355b13b4faf5d47893348f766, 0x1e83d6315c9f125b0786018e7cb772675d11e69aa6c0b98ca12380320d7cc1de),
    (0x354afd0a2f9d0b26160b41552f2931c8c486894d76e0c33b1799603e855ce731, 0x00cd6d29f166eadc2d8affa62905c5a560b00dbe1faced078b997ee06be1bff3, 0x1d6219352768e3aedbe0e3d7cdbc66efc60d01973f18305708d0641917082f2c),
    (0x146336e25db5181de48d2370d7d1a142afe3ca1db8d4f529fa08dd9806387577, 0x0005d8e085fd72ee997a21163e2e43df022e54b49c13d907a901d3ce84de0ad4, 0x364e97c7a38932270dd5e61c8a4e86426f8ebc1d2296021a1c36f31341964484),
    (0x01189910671bc16b561c6fff15346878fa97ec80ad307a52d7a00c03d2e0baaa, 0x162a7c80f4d2d12e5229dfaa01231a454c0f7e001df490aa63fd8ac57a95ca8c, 0x2a0d6c09576666bb2604e4afb09f8603caff31b4fda3212432e69efb22f40b96),
    (0x0978e5c51e1e5649e16a4d603d5a808ef444d10d63a74e2cc0a0180f8cbfc0d2, 0x1bdcee3aaca9cd25ebe19bbdce25101105087d903bdacfd103f4460ebc351b6e, 0x1862cccb70b5b885e49479140b1944fd0c947321e0075e3ff61964bf3ade7670),
    (0x1f3e91d863c16922bc26cc883a1987e139ee99c1cc6e5ddac3267da6e94adc50, 0x1af47a48a6016a49ef5c08f8478f663afa661465c656ad990f85b4ac2c367406, 0x3c8ee901956e3d3f009d57338c6935051c3698b0a2e3da100eabcd87e7d01b15),
    (0x1660a8cde7fec55368d0b024f591b520e10ce2b7069f4dbd8b94772189673476, 0x0f6d991929d5e4e71303936334dd11323963c2c1f5586e2f9d8d0f67fdaa79d5, 0x02b9cea1921cd9f6cc625eaaab52b4dc4e7fda770712f3437a433091e1ce2d3a),
    (0x14a323b99b900331214f7c6784acb565d8caf468976f04723797b2d8376043b3, 0x190476b580cb9277ec01ea79642d5760718b7fbc7788af78347fef2c00f0953a, 0x090a3a9d869d2eefa42463d30b442b6f9660902b60087651ff4e7e6fb268dfd7),
    (0x3877a955863675670dbe8fd2270a6795e365001304f9a11ef983387ea0456203, 0x2d894691240fe9535df39a2cc63ddc0a60118c53a218135239c0af0fe01f4a06, 0x21b9c18292bdbc597ef71780201661895914e855eeb44aa11aca9eaf9bba9850),
    (0x2fe76be7cff723e2505a05f2a6ae834c272e1cc6c36a296833f509a74ad9d39b, 0x187aa448f391e3ca929981d7cfce253bd15bff840ddae8a50df9fa97277fa8b4, 0x0b7083ad751707bf007ab3aa3617f422663ccf7b2ffe4b5ef0c66af5ffc73736),
    (0x030ddbb470493f163bc4ca9902c52acb1975b962f6cb8e0b2f9b20f1fbd49791, 0x3130fbaffb5aa82a950b0ab18d3546df8fb8ab9d60ea17b23a1c62ca8fbf2525, 0x337f544707c430f04f74d74bac2ee45715ce2ead2fcd051e43a876180dc382e0),
    (0x349979919015394fac9d91b0930dac757d8e471a9fb95fef26de98a8736d1d11, 0x027cc4efe3fb35dd2305cd7a921ec5f13bf93da6fff31d95ccfcb61831d5c775, 0x037f9f2365954c5b61b71a3698682ad267f1c6b7314764afc3fa2629635d27de),
    (0x1f697cac4d07feb710f1cc6df8b4bcd760414abe362d01c977c5b024848371ae, 0x267a750fe5d7cfbc26e6c851fbd572a63145c478063109d6786add244aa0ef29, 0x0c91feab4a43193a678c9996d9a472c8af285fa82ce4fae5180e2b4d3e756f65),
    (0x1745569a0a3e30142186c3038ea05e697e3b83af4a4ba3ba79c47c573ac410f7, 0x29863d546e7e7c0deca5120778a56711fdff66c6f3b5ffe11e0388522696191f, 0x1148d6ab2bd00192bf06bae49ef853f6a79a03df833994c62f225e6366bfe390),
    (0x02e0e121b0f3dfefe18b1499060da366f745f45d350d41d4f4f6331a8b265d15, 0x0d0aa46e76a6a278b89ef73a40a2b274690401736d44a653078ae6aa151054b7, 0x13943675b04aa986eee545f3fa6d3d08392dde710f1f06db9a4d532c7b6e0958),
    (0x2901ec61942d34aad97a11d63088f5d9c9f2b3257530dafe961fc818dcbb66b5, 0x20204a2105d22e7ef431d54434a3e0cf22ffa2a2af9fa3e3fdf544b963d1fdc7, 0x3a8a628295121d5c5c1e3e9e27a571c3a004abe8e01528c41211b9e2190d6852),
)
MDS = (
    (0x0ab5e5b874a68de7b3d59fbdc8c9ead497d7a0ab23850b56323f2486d7e11b63, 0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e, 0x07c045d5f5e9e5a6d803952bbb364fdfa0a3b71a5fb1573519d1cf25d8e8345d),
    (0x233162630ebf9ed7f8e24f66822c2d9f3a0a464048bd770ad049cdc8d085167c, 0x25cae2599892a8b0b36664548d60957d78f8365c85bbab07402270113e047a2e, 0x22f5b5e1e6081c9774938717989a19579aad3d8262efd83ff84d806f685f747a),
    (0x2e29dd59c64b1037f333aa91c383346421680eabc56bc15dfee7a9944f84dbe4, 0x1d1aab4ec1cd678892d15e7dceef1665cbeaf48b3a0624c3c771effa43263664, 0x3bf763086a18936451e0cbead65516b975872c39b59a31f615639415f6e85ef1),
)

# ================================================================ 2 the target hash (reference form: Orchard Poseidon, ConstantLength<2>, 8 full + PARTIAL partial rounds)
CAPACITY = 1 << 65
ROUND_IDX = tuple(range(4)) + tuple(range(4, 4 + PARTIAL)) + tuple(range(60, 64))   # original rounds 0-3 full, 4..PARTIAL+3 partial, 60-63 full
C_UNIT = 216 + 21 * PARTIAL               # C(r) of the cost model: one reference permutation call = C primitive operations


def _round(st, i):
    """Round i of the reference permutation on the state st (list of 3 field elements)."""
    k = ROUND_CONSTANTS[i]
    st = [(st[0] + k[0]) % P, (st[1] + k[1]) % P, (st[2] + k[2]) % P]
    for c in (range(3) if i < 4 or i >= 60 else range(1)):
        st[c] = pow(st[c], 5, P)
    return [(MDS[r][0] * st[0] + MDS[r][1] * st[1] + MDS[r][2] * st[2]) % P for r in range(3)]


def digest(m0, m1):
    """Digest of the Orchard hash of the two canonical field elements (m0, m1): initial state [m0, m1, 2^65], all rounds, output state[0]."""
    st = [m0, m1, CAPACITY]
    for i in ROUND_IDX:
        st = _round(st, i)
    return st[0]


def enc(x):
    """Canonical 32-byte little-endian encoding (x < P)."""
    assert 0 <= x < P
    return x.to_bytes(32, "little")


# ================================================================ 3 the input line and the step program
INV5 = pow(5, -1, P - 1)                  # gcd(5, p - 1) = 1: x -> x^5 is a bijection of the field, with inverse x -> x^INV5


def inv(a):
    return pow(a, P - 2, P)


def root5(a):
    return pow(a, INV5, P)


def line():
    """The input line on which rounds 0 and 1 are affine.  Round 0 maps (m0, m1) to U = (m0 + c00)^5, V = (m1 + c01)^5 (a bijection) and a constant
    third lane; the round-1 S-box input is then affine in (U, V).  On (U, V) = (U0 + a tau, V0 + b tau) its lane 0 is constant (M00 a + M01 b = 0)
    and its lanes 1, 2 are d_i tau, so the S-box gives d_i^5 tau^5: with W = tau^5 the state after round 1 is A + W B.
    message(W) = (U^(1/5) - c00, V^(1/5) - c01) is injective in W (W -> tau -> (U, V) -> (m0, m1), each step injective, a != 0)."""
    kp = pow((CAPACITY + ROUND_CONSTANTS[0][2]) % P, 5, P)
    base = [(MDS[i][2] * kp + ROUND_CONSTANTS[1][i]) % P for i in range(3)]
    a, b = MDS[0][1], (-MDS[0][0]) % P
    det = (MDS[1][0] * MDS[2][1] - MDS[2][0] * MDS[1][1]) % P
    U0 = (-base[1] * MDS[2][1] + base[2] * MDS[1][1]) * inv(det) % P
    V0 = (-MDS[1][0] * base[2] + MDS[2][0] * base[1]) * inv(det) % P
    return a, b, U0, V0


LINE_A, LINE_B, LINE_U0, LINE_V0 = line()


def message(W):
    """The two message elements of the line point W."""
    tau = root5(W)
    return (root5((LINE_U0 + LINE_A * tau) % P) - ROUND_CONSTANTS[0][0]) % P, (root5((LINE_V0 + LINE_B * tau) % P) - ROUND_CONSTANTS[0][1]) % P


def after_round1(m0, m1):
    return _round(_round([m0, m1, CAPACITY], 0), 1)


class Mono:
    """A field element times kappa^e (kappa the attempt's multiplicative coin): value v at kappa = 1, integer exponent e.  Sums are allowed
    only between equal exponents (asserted) or with zero, so every constant built from Monos is exactly K(1) * kappa^e."""
    __slots__ = ("v", "e")

    def __init__(s, v, e=0):
        s.v, s.e = v % P, e

    @staticmethod
    def c(o):
        return o if isinstance(o, Mono) else Mono(o, 0)

    def __mul__(s, o):
        o = Mono.c(o)
        return Mono(s.v * o.v, s.e + o.e)
    __rmul__ = __mul__

    def __add__(s, o):
        o = Mono.c(o)
        if o.v == 0:
            return s
        if s.v == 0:
            return o
        assert s.e == o.e, "sum of different kappa powers"
        return Mono(s.v + o.v, s.e)
    __radd__ = __add__

    def __neg__(s):
        return Mono(-s.v, s.e)

    def __sub__(s, o):
        return s + (-Mono.c(o))

    def __rsub__(s, o):
        return Mono.c(o) + (-s)

    def __mod__(s, m):
        return s

    def __pow__(s, k, m=None):
        if k == P - 2:
            return Mono(pow(s.v, P - 2, P), -s.e)
        return Mono(pow(s.v, k, P), s.e * k)

    def __eq__(s, o):
        return s.v == Mono.c(o).v

    def __ne__(s, o):
        return not s.__eq__(o)

    def __hash__(s):
        return hash((s.v, s.e))

    def at(s, kappa):
        return s.v * pow(kappa, s.e % (P - 1), P) % P


def build_step():
    """The step program: from x (register x) to F(x) = digest(message(x + rho0)) / OUTSCALE (register x), as a straight-line list of
    field operations (op, dest, src1, src2) with op ADD or MUL.  Register names: x (walk value), e0..e2 (attempt registers e_i = E0_i + rho0),
    k<n> (constants, values in the returned dict), y*, z*, h*, u, x5, t1, t2 (working).  Equivalent form of rounds 2..63:
    every lane is held divided by a known nonzero constant scale (one coefficient of each linear combination becomes 1), and the partial rounds
    keep lanes 1, 2 in a basis Q that absorbs the linear layer (only lane 0 and the two update terms are computed).  Returns
    (prog, kval, E0, OUTSCALE)."""
    A = after_round1(*message(0))
    A1 = after_round1(*message(1))
    B = [(A1[i] - A[i]) % P for i in range(3)]
    prog, kval = [], {}

    def K(v):
        name = "k%d" % len(kval)
        kval[name] = v % P if LEV_D else v % P
        return name

    def op(o, d, s, t):
        prog.append((o, d, s, t))

    def pow5(d, s):
        op("MUL", "s_" + d, s, s)
        op("MUL", "s_" + d, "s_" + d, "s_" + d)
        op("MUL", d, "s_" + d, s)

    def mds_norm(sig, cnext, src, dst):
        """dst_i = (sum_j M_ij sig_j src_j + cnext_i) / G_i0 with G = M diag(sig): 2 MUL + 2 ADD (+ 1 ADD for the constant) per lane."""
        lam = []
        for i in range(3):
            G = [MDS[i][j] * sig[j] % P for j in range(3)]
            assert G[0] != 0
            gi = inv(G[0])
            op("MUL", "t1", src[1], K(G[1] * gi))
            op("MUL", "t2", src[2], K(G[2] * gi))
            op("ADD", dst[i], src[0], "t1")
            op("ADD", dst[i], dst[i], "t2")
            if cnext is not None:
                op("ADD", dst[i], dst[i], K(cnext[i] * gi))
            lam.append(G[0])
        return lam

    Y, Z = ["y0", "y1", "y2"], ["z0", "z1", "z2"]
    # round 2: S-box input lane i = A_i + c2_i + (x + rho0) B_i = B_i (x + e_i)
    assert all(B[i] != 0 for i in range(3))
    E0 = [(A[i] + ROUND_CONSTANTS[2][i]) * inv(B[i]) % P for i in range(3)]
    if LEV_D:
        Y = ["x", "y1", "y2"]
        for i in (1, 2):
            op("ADD", Y[i], "x", "e%d" % i)
        sig = [pow(Mono(B[i], 1), 5, P) for i in range(3)]       # lane scales B_i kappa: the program is built once, every constant a Mono
    else:
        for i in range(3):
            op("ADD", Y[i], "x", "e%d" % i)
        sig = [pow(B[i], 5, P) for i in range(3)]
    for i in range(3):
        pow5(Z[i], Y[i])
    Y = ["y0", "y1", "y2"]
    lam = mds_norm(sig, ROUND_CONSTANTS[3], Z, Y)          # round 2 linear layer + round 3 constants
    sig = [pow(l, 5, P) for l in lam]
    for i in range(3):
        pow5(Z[i], Y[i])                                   # round 3 S-boxes
    # round 3 linear layer into the partial-round form: true lane 0 = lam0 h0 + gamma, true lanes (1, 2) = Q (h1, h2) + q.
    # The hidden lanes (h1, h2) = Pm (s1, s2) are held in the basis Pm = diag(nu) M22^PARTIAL, M22 the lower 2 x 2 block of M, so that
    # after the PARTIAL rounds Q = M22^PARTIAL Pm^-1 = diag(nu)^-1 is diagonal; nu_a makes the coefficient of Z0 in h_a equal to 1.
    G = [[MDS[i][j] * sig[j] % P for j in range(3)] for i in range(3)]
    assert G[0][0] != 0
    g0 = inv(G[0][0])
    op("MUL", "t1", Z[1], K(G[0][1] * g0))
    op("MUL", "t2", Z[2], K(G[0][2] * g0))
    op("ADD", "h0", Z[0], "t1")
    op("ADD", "h0", "h0", "t2")
    M22 = [[MDS[1][1], MDS[1][2]], [MDS[2][1], MDS[2][2]]]
    M22r = [[1, 0], [0, 1]]
    for _ in range(PARTIAL):
        M22r = [[(M22[a][0] * M22r[0][b] + M22[a][1] * M22r[1][b]) % P for b in range(2)] for a in range(2)]
    Pm = []
    for a in range(2):
        v = [(M22r[a][0] * G[1][j] + M22r[a][1] * G[2][j]) % P for j in range(3)]    # h_a = nu_a (v . Z)
        assert v[0] != 0
        nu = inv(v[0])
        op("MUL", "t1", Z[1], K(v[1] * nu))
        op("MUL", "t2", Z[2], K(v[2] * nu))
        op("ADD", "h%d" % (1 + a), Z[0], "t1")
        op("ADD", "h%d" % (1 + a), "h%d" % (1 + a), "t2")
        Pm.append([nu * M22r[a][0] % P, nu * M22r[a][1] % P])
    dP = (Pm[0][0] * Pm[1][1] - Pm[0][1] * Pm[1][0]) % P
    assert dP != 0
    dPi = inv(dP)
    Q = [[Pm[1][1] * dPi % P, (-Pm[0][1]) * dPi % P], [(-Pm[1][0]) * dPi % P, Pm[0][0] * dPi % P]]    # Pm^-1: (s1, s2) = Q (h1, h2)
    lam0, gamma = G[0][0], 0
    q = [0, 0]
    for k in range(PARTIAL):
        c = ROUND_CONSTANTS[4 + k]
        op("ADD", "u", "h0", K((gamma + c[0]) * inv(lam0)))
        pow5("x5", "u")
        l5 = pow(lam0, 5, P)
        q = [(q[0] + c[1]) % P, (q[1] + c[2]) % P]
        alpha = MDS[0][0] * l5 % P
        beta = [(MDS[0][1] * Q[0][j] + MDS[0][2] * Q[1][j]) % P for j in range(2)]
        gamma = (MDS[0][1] * q[0] + MDS[0][2] * q[1]) % P
        Qn = [[(MDS[1 + i][1] * Q[0][j] + MDS[1 + i][2] * Q[1][j]) % P for j in range(2)] for i in range(2)]
        q = [(MDS[1 + i][1] * q[0] + MDS[1 + i][2] * q[1]) % P for i in range(2)]
        dt = (Qn[0][0] * Qn[1][1] - Qn[0][1] * Qn[1][0]) % P
        assert alpha != 0 and dt != 0
        di = inv(dt)
        v = [MDS[1][0] * l5 % P, MDS[2][0] * l5 % P]
        w = [(Qn[1][1] * v[0] - Qn[0][1] * v[1]) * di % P, (-Qn[1][0] * v[0] + Qn[0][0] * v[1]) * di % P]   # w = Qn^-1 v
        ai = inv(alpha)
        op("MUL", "t1", "h1", K(beta[0] * ai))
        op("MUL", "t2", "h2", K(beta[1] * ai))
        op("ADD", "h0", "x5", "t1")
        op("ADD", "h0", "h0", "t2")
        op("MUL", "t1", "x5", K(w[0]))
        op("ADD", "h1", "h1", "t1")
        op("MUL", "t2", "x5", K(w[1]))
        op("ADD", "h2", "h2", "t2")
        lam0, Q = alpha, Qn
    # round 60 S-box inputs from the partial-round form, each lane divided by its scale
    c = ROUND_CONSTANTS[60]
    op("ADD", Y[0], "h0", K((gamma + c[0]) * inv(lam0)))
    sig = [pow(lam0, 5, P)]
    assert Q[0][1] == 0 and Q[1][0] == 0 and Q[0][0] != 0 and Q[1][1] != 0     # Q is diagonal after the PARTIAL rounds
    for i in range(2):
        gi = inv(Q[i][i])
        op("ADD", Y[1 + i], "h%d" % (1 + i), K((q[i] + c[1 + i]) * gi))
        sig.append(pow(Q[i][i], 5, P))
    for rnd in (60, 61, 62):
        for i in range(3):
            pow5(Z[i], Y[i])
        lam = mds_norm(sig, ROUND_CONSTANTS[rnd + 1], Z, Y)
        sig = [pow(l, 5, P) for l in lam]
    for i in range(3):
        pow5(Z[i], Y[i])                                   # round 63 S-boxes
    G0 = [MDS[0][j] * sig[j] % P for j in range(3)]        # digest = G0 . z; the step outputs digest / G0[0]
    gi = inv(G0[0])
    op("MUL", "t1", Z[1], K(G0[1] * gi))
    op("MUL", "t2", Z[2], K(G0[2] * gi))
    op("ADD", "x", Z[0], "t1")
    op("ADD", "x", "x", "t2")
    return prog, kval, E0, G0[0]


STEP, KVAL, E0, OUTSCALE = build_step()
if LEV_D:
    KMONO, OUTMONO = KVAL, Mono.c(OUTSCALE)               # constants as monomials in kappa; OUTSCALE_kappa = OUTSCALE_1 kappa^E_OUT
    KVAL = {k: Mono.c(v).v for k, v in KMONO.items()}      # values at kappa = 1
    OUTSCALE, E_OUT = OUTMONO.v, OUTMONO.e
    assert E_OUT == 5 ** (PARTIAL + 6)

    def _terms(e):
        """e = s1 5^a + s2 5^b (s in {-1, 0, 1}, a, b <= PARTIAL + 6): the signed power-of-5 terms, fewest first."""
        if e == 0:
            return ()
        for a in range(PARTIAL + 7):
            for s1 in (1, -1):
                if s1 * 5 ** a == e:
                    return ((s1, a),)
        for a in range(PARTIAL + 7):
            for b in range(PARTIAL + 7):
                for s1 in (1, -1):
                    for s2 in (1, -1):
                        if s1 * 5 ** a + s2 * 5 ** b == e:
                            return ((s1, a), (s2, b))
        raise AssertionError("exponent outside the recipe")
    KTERMS = {k: _terms(v.e) for k, v in KMONO.items()}
    INV_OPS = ((P - 2).bit_length() - 1) + (bin(P - 2).count("1") - 1)     # kappa^-1 by square-and-multiply on p - 2
    # Setup per attempt (D), exact count: kappa^(5^a) and kappa^(-5^a) for a = 1..PARTIAL+6 (3 MUL each), one inversion, one MUL per
    # constant term (K_j(1) times each kappa power of its recipe), e_1, e_2 (one MUL each), and W = kappa x - E0_0 for the two messages
    # (one MUL more each than x + rho0).
    SETUP_D = 2 * 3 * (PARTIAL + 6) + INV_OPS + sum(len(t) for t in KTERMS.values()) + 2 + 2
    # Memory of the setup (D): both power chains (2 (PARTIAL + 7) words), one 16-bit recipe field per constant, E0_1 - E0_0, E0_2 - E0_0,
    # kappa, and 64 setup instructions (4 B each, the format of the step code).
    D_BYTES = 2 * (PARTIAL + 7) * 32 + ((NCONST_D := len(KMONO)) * 2 + 31) // 32 * 32 + 3 * 32 + 64 * 4
else:
    SETUP_D, D_BYTES = 0, 0
OUTINV = inv(OUTSCALE)
NCONST = len(KVAL)                        # step constants, each loaded once per attempt into its own register
REGNAMES = sorted({r for o in STEP for r in o[1:]})
NREG_STEP = len(REGNAMES)                 # registers the step uses: constants, e0..e2, x and working registers
NREG = NREG_STEP + 45                     # + x1, x2, x3 (the group ring with x) and t, + at most 41 control registers of the search (proof.md Sections 6, 7): the declared file
_IDX = {r: n for n, r in enumerate(REGNAMES)}
_CODE = tuple((o == "MUL", _IDX[d], _IDX[s], _IDX[t]) for o, d, s, t in STEP)


def kappa_consts(kappa):
    """The attempt's register values for the coin kappa (D): every step constant K_j(1) kappa^(e_j), e_1, e_2, and OUTSCALE_kappa."""
    ki = inv(kappa)
    regs = {name: KMONO[name].at(kappa) for name in KMONO}
    for i in (1, 2):
        regs["e%d" % i] = (E0[i] - E0[0]) * ki % P
    return regs, OUTMONO.at(kappa)


def make_F(rho0):
    """F(x) = digest(message(x + rho0)) / OUTSCALE, computed by executing the step program (every operation of STEP once).
    With D, rho0 is the multiplicative coin kappa and F(x) = digest(message(kappa x - E0_0)) / OUTSCALE_kappa."""
    R = [0] * NREG_STEP
    if LEV_D:
        regs, _ = kappa_consts(rho0)
        for name, v in regs.items():
            R[_IDX[name]] = v
    else:
        for name, v in KVAL.items():
            R[_IDX[name]] = v
        for i in range(3):
            R[_IDX["e%d" % i]] = (E0[i] + rho0) % P
    ix = _IDX["x"]

    def F(x):
        R[ix] = x
        for m, d, s, t in _CODE:
            R[d] = R[s] * R[t] % P if m else (R[s] + R[t]) % P
        return R[ix]
    return F


# ================================================================ 4 the search: one trail, distinguished points, one packed table, recovery
UNROLL = 48                               # trail steps per block (a multiple of GROUP)
VBITS, GBITS = 142, 119                   # entry = the DP value (x < DELTA < 2^142) and the index gap to the previous stored point (< 2^119)
RBITS = VBITS + GBITS                     # 261 bits per entry, entries packed back to back from bit 0 of the table words
MASK256 = (1 << 256) - 1
# Operation charges (word operations, 1/C each), beside the |STEP| field operations of every evaluation (proof.md Section 6 listings):
GROUP = 4         # the DP test is made once per group of 4 consecutive trail steps, on the AND of their 4 outputs
W_GRP = 5         # per group of 4 trail steps (copy k of STEP reads x_(k mod 4), writes x_((k+1) mod 4)): AND t, x1, x2; AND t, t, x3;
                  # AND t, t, x0; CMPLT g, t, DELTA; BZ g, next (skip the group's inline handler).  AND(x_a..x_d) <= each x, so a group with a DP is a hit
W_HIT = 11        # per hit group (a DP in it, or a false hit): per slot in order CMPLT g, x_j, DELTA; BZ g (8); on a false hit ADD fp, CMPLT, BZ (3)
W_LOOP = 2        # (69e14209's per-step test; kept only to state the recovery charge: a recovery evaluation costs |STEP| + W_REC)
W_BLOCK = 2       # per block of UNROLL unrolled steps: SUB c, c, UNROLL; BNZ c, block
W_DP = 16         # per distinguished-point event besides scan and insertion, 16 executed (CALL counted 2): inline SUB idx, BS, c; ADD idx, idx, slot + 1;
                  # MOV A, x_slot (staging); CALL dph; shared handler MOV cur, lr; MOV bp, 0; CALL scan; CMPLT g, cnt, MCAPR; BZ g; CALL insert; MOV lr, cur; RET
W_SCAN = 19       # per table entry examined, charged at 19 (18 executed): word index, bit offset, address (2), two loads (+1 address add),
                  # shift, 255 - offset, two shifts, OR, AND 142-bit mask, compare, branch, pointer add 261, bound compare, branch
W_INS = 40        # per insertion, charged at 40 (37 executed): gap = index - last, compare with 2^119, branch, move; value field and gap field
                  # each a two-word read-modify-write (15 and 16); end pointer add 261; count
W_POS = 24        # per entry walked in the recovery's index passes, charged at 24 (19 and 22 executed): gap field read (14) and index add,
                  # compare with q or record of the previous index, pointer add 261, bound compare, branch
W_REC = 9         # per recovery evaluation beside the step (the one recovery copy of STEP is a subroutine; CALL charged 2, RET 1):
                  # walk loop 9 (budget test, branch, decrement, step counter decrement and test, CALL 2, RET 1, back-edge); lockstep 18 per 2 evaluations
                  # (budget compare, branch, decrement by 2, move A into x, CALL 2, RET 1, move result out, the same for B, compare, branch, two moves, back-edge)
POW_OPS = (INV5.bit_length() - 1) + (bin(INV5).count("1") - 1)   # square-and-multiply for x^INV5: squarings + multiplications
MSG_OPS = 2 * (3 * POW_OPS + 7)           # the two messages: W = A + rho0, tau = W^(1/5), U, V (2 MUL, 2 ADD), two roots, two subtractions


def table_words(m):
    """Words of a table of m packed entries, plus one pad word: every field read loads the word holding its first bit and the next one."""
    return (m * RBITS + 255) // 256 + 1


def _get(tw, off, width):
    """The field of `width` bits at bit offset off (it spans at most two words: off mod 256 + width <= 255 + 142 < 512)."""
    j, sh = off >> 8, off & 255
    return ((tw[j] >> sh) | ((tw[j + 1] << (255 - sh) << 1) & MASK256)) & ((1 << width) - 1)


def _put(tw, off, v):
    """OR the field value v (v < 2^142) into the zeroed bits at bit offset off: two read-modify-writes."""
    j, sh = off >> 8, off & 255
    tw[j] |= (v << sh) & MASK256
    tw[j + 1] |= v >> (255 - sh) >> 1


def search(F, dpt, x0, budget, mcap, rcap, fpcap):   # one evaluation budget for the trail and the recovery together; single-gap recovery (credit 43caeb6a Lemma 3 via 1533f8f0)
    """Single-trail collision search on the map F: x_0 = x0, x_i = F(x_{i-1}), UNROLL steps per block.  Every x_i (i >= 1) with is_dp(x_i) is
    stored as one packed entry (x, i - previous stored index); the start x_0 (index 0) is kept in its own word.  One down-counter holds the
    evaluations left of `budget` (a multiple of UNROLL) for the trail and the recovery together; the recovery may use at most `rcap` of them.
    Halts (failure) when the budget is used up, when the table already holds `mcap` points at a new one, when an index gap reaches 2^119, or when
    the recovery would exceed min(budget left, rcap) evaluations.  When a distinguished value repeats (x_b = x_a, a < b) the trail is periodic from a
    with period L = b - a; the recovery finds the least i with x_i = x_{i+L} and returns (x_{i-1}, x_{i+L-1}), distinct, with F equal on both.
    Returns (pair or None, status, evaluations, ops)."""
    ops = {"trail": 0, "blocks": 0, "rec": 0, "dp": 0, "table": 0, "pos": 0, "groups": 0, "hits": 0}
    fp = 0
    tw = [0] * table_words(mcap)
    cnt, last = 0, 0

    def lookup(x):
        for k in range(1, cnt + 1):
            ops["table"] += W_SCAN
            if _get(tw, (k - 1) * RBITS, VBITS) == x:
                return k
        return None

    x, i, k, b = x0, 0, None, None
    while i < budget and k is None:
        for g0 in range(0, UNROLL, GROUP):
            xs = []
            for _ in range(GROUP):
                x = F(x)
                xs.append(x)
            ops["trail"] += GROUP
            ops["groups"] += 1
            t = xs[0] & xs[1] & xs[2] & xs[3]
            if t >= dpt:                    # no value of the group is a DP (AND <= each value)
                continue
            ops["hits"] += 1
            if not any(v < dpt for v in xs):
                fp += 1                     # a false hit: no DP in the group
                if fp > fpcap:
                    return None, "false-hits", ops["trail"], ops
                continue
            for j, v in enumerate(xs):
                if v >= dpt:
                    continue
                slot = g0 + j
                ops["dp"] += W_DP
                k = lookup(v)
                if k is not None:
                    b = i + slot + 1
                    break
                if cnt >= mcap:
                    return None, "table", ops["trail"], ops
                ops["table"] += W_INS
                gap = i + slot + 1 - last
                if gap >> GBITS:
                    return None, "gap-width", ops["trail"], ops
                assert v >> VBITS == 0
                _put(tw, cnt * RBITS, v)
                _put(tw, cnt * RBITS + VBITS, gap)
                cnt, last = cnt + 1, i + slot + 1
            if k is not None:
                ev_end = i + g0 + GROUP     # the trail evaluated the whole group: up to GROUP - 1 evaluations past b
                break
        if k is None:
            i += UNROLL
            ops["blocks"] += 1
    ev = ops["trail"]
    if k is None:
        return None, "budget", ev, ops
    left = min(budget - ev_end, rcap)       # evaluations the recovery may still use (the down-counter, capped by rcap)
    a, s = 0, 0                             # pass 1: the indices of entries k - 1 and k
    for r in range(1, k + 1):
        ops["pos"] += W_POS
        s, a = a, a + _get(tw, (r - 1) * RBITS + VBITS, GBITS)
    A = x0 if k == 1 else _get(tw, (k - 2) * RBITS, VBITS)      # last stored point before a (index s < mu <= a), or the start
    L = b - a
    q = s + L
    idx, B, cur = 0, x0, 0                  # pass 2: the nearest stored point at or before q, then walk to x_q
    for r in range(1, cnt + 1):
        ops["pos"] += W_POS
        cur += _get(tw, (r - 1) * RBITS + VBITS, GBITS)
        if cur > q:
            break
        idx, B = cur, _get(tw, (r - 1) * RBITS, VBITS)
    for _ in range(q - idx):
        if left == 0:
            return None, "budget", ev, ops
        left -= 1
        B = F(B)
        ev += 1
        ops["rec"] += 1
    if A == B:
        return None, "start-on-cycle", ev, ops
    while True:                             # lockstep: the first index where the two walkers meet
        if left < 2:
            return None, "budget", ev, ops
        left -= 2
        nA, nB = F(A), F(B)
        ev += 2
        ops["rec"] += 2
        if nA == nB:
            return (A, B), "found", ev, ops
        A, B = nA, nB


# ================================================================ 5 the claim's parameters and ledger (derive, plan)
T_DP = 51075                             # a value x is a distinguished point iff x < DELTA = (2^126 + 1) T_DP (T_DP < 2^16, so DELTA < 2^142)
MCAP = 26276                             # table capacity in distinguished points
TAB = 15                                 # table overflow probability <= e^-TAB
RCAP = 1 << 119                          # at most RCAP of the budget's evaluations go to the recovery (positioning walk and lockstep)
BUDGET = 169218966381152594613869050637269860384 # B, the evaluation budget of the attempt (trail and recovery together): an integer literal, derived offline by `plan` (which asserts it)
PREP_OPS = 1 << 58                        # charged bound (word operations) of the offline derivation (`--tune` and `--plan`): proof.md Section 6a
PREP_INSTR = 1 << 14                      # bound on the compiled offline code, in instructions of 4 bytes: proof.md Section 7
PREP_DATA = 1 << 18                       # bound on the data of the offline derivation, in bytes: proof.md Section 7
SMAX = 1 << 128                           # every index of the program is below SMAX (B < 2^128)
GRAIN = 1 << 100                          # B is the least multiple of UNROLL at or above k 2^100, k the least integer that reaches the success bound
Q_CLAIM = Fraction(39, 100)               # the claimed success probability on the real map (premise H1)
Q_RANDOM = Q_CLAIM                        # the proven success bound on a uniformly random function at the filed budget: the budget is the random-function budget
MISC = (1 << 20) + SETUP_D                # (D: + the per-attempt constant setup) generous charge for the loop control of the setup exponentiations and the recipe decoding,
                                          # coins, masks, bounds, halts, counters' setup, two field reads and the report
CODE_OTHER = 400                          # instructions outside the step copies: handlers, scan, insertion, index passes, recovery control, roots, setup loop

# Exact offline arithmetic (integers only: no float, no Decimal, no library function).  A real number v is held as an integer in units of
# 2^-FB (FB = 256).  Every number named below as an upper bound is rounded up, every lower bound down, so each derived inequality is rigorous.
# CNT meters the integer operations of the offline code (add: add, subtract, compare or shift of a multiword value; mul; div: floor division or remainder)
# and the largest operand seen; each routine adds its own statement count (loop bound times operations per iteration, rounded up).  `--tune` prices the
# counts with the prices of the integer routines below (proof.md Section 6a).
FB = 256
ONE = 1 << FB
KEXP = 100                                # terms of the exponential series
KLN = 48                                  # terms of the logarithm series
CNT = {"add": 0, "mul": 0, "div": 0, "bits": 0}

# The integer routines of the offline arithmetic on the word machine of the cost model (proof.md Section 6a).  An integer below 2^IBITS is four 256-bit words
# (little endian).  Word operations, one each: ADD, SUB (mod 2^256), AND, OR, SHL, SHR (by a constant), CMPLT, CMPEQ, a branch, a move, a load, a store.
# `Wm` executes the routines and counts the operations; `--selftest` runs them and asserts that their worst cases are the prices W_IMUL and W_IDIV.
IBITS = 1000                              # every integer of the offline code is below 2^IBITS (the recorded maximum is 653 bits)
M256 = (1 << 256) - 1
W_ADD4, W_SH4, W_CMP4 = 14, 10, 13        # four-word add or subtract (carry chain), shift by a constant, comparison: the counts of Wm.add4, shl1, lt4
W_IADD = 32                               # per integer add, subtract, compare or shift: 8 loads + 14, or 8 loads + 13 + a branch, or 4 loads + 10 + 4 stores, at most 32
W_IMUL = 14 + IBITS * (2 + W_ADD4 + 2 * W_SH4 + 2) + 4                          # shift-and-add: per multiplier bit AND, BZ, add, two shifts, SUB, BNZ
W_IDIV = 28 + IBITS * (3 * W_SH4 + 2 + W_CMP4 + 1 + W_ADD4 + 1 + 2) + 8       # restoring division: three shifts, top bit, OR, compare, BNZ, subtract, OR, SUB, BNZ
# Bounds on the offline work other than `--tune` (proof.md Section 6a).  The recipe search `_terms` at its loop bounds: per constant 2 (PARTIAL + 7) iterations of at most
# 12 integer operations and 4 (PARTIAL + 7)^2 iterations of at most 24 (a power 5^a is at most 10 multiplications), each operation priced as a division.  `build_step` and
# the line at their loop bounds: PARTIAL iterations of at most 12 + 100 field operations and 3 inversions (INV_OPS operations each), at most 32 inversions, 6 fifth
# roots (POW_OPS operations each) and 500 field operations elsewhere.  One run of `plan`.
BUILD_OPS = 1 << 17
PLAN_OPS = 1 << 31
RECIPE_OPS = NCONST * (2 * (PARTIAL + 7) * 12 + 4 * (PARTIAL + 7) ** 2 * 24) * W_IDIV
assert PARTIAL * (12 + 100 + 3 * INV_OPS) + 32 * INV_OPS + 6 * POW_OPS + 500 <= BUILD_OPS


class Wm:
    """Counting word machine: every primitive adds one to n; the routines are the offline code's integer operations on four-word integers."""

    def __init__(s):
        s.n = 0

    def ADD(s, a, b): s.n += 1; return (a + b) & M256
    def SUB(s, a, b): s.n += 1; return (a - b) & M256
    def AND(s, a, b): s.n += 1; return a & b
    def OR(s, a, b): s.n += 1; return a | b
    def SHL(s, a, k): s.n += 1; return (a << k) & M256
    def SHR(s, a, k): s.n += 1; return a >> k
    def LT(s, a, b): s.n += 1; return int(a < b)
    def EQ(s, a, b): s.n += 1; return int(a == b)
    def other(s, k=1): s.n += k            # branches, moves, loads and stores

    def add4(s, a, b):                      # a + b, 14 operations
        c = [s.ADD(a[0], b[0])]
        k = s.LT(c[0], a[0])
        for i in (1, 2):
            t = s.ADD(a[i], b[i])
            c.append(s.ADD(t, k))
            k = s.OR(s.LT(t, a[i]), s.LT(c[i], t))
        return c + [s.ADD(s.ADD(a[3], b[3]), k)]

    def sub4(s, a, b):                      # a - b, 14 operations
        c = [s.SUB(a[0], b[0])]
        k = s.LT(a[0], b[0])
        for i in (1, 2):
            t = s.SUB(a[i], b[i])
            c.append(s.SUB(t, k))
            k = s.OR(s.LT(a[i], b[i]), s.LT(t, k))
        return c + [s.SUB(s.SUB(a[3], b[3]), k)]

    def shl(s, a, k):                       # a << k (0 < k < 256), 10 operations
        return [s.SHL(a[0], k)] + [s.OR(s.SHL(a[i], k), s.SHR(a[i - 1], 256 - k)) for i in (1, 2, 3)]

    def shr1(s, a):                         # a >> 1, 10 operations
        return [s.OR(s.SHR(a[i], 1), s.SHL(a[i + 1], 255)) for i in (0, 1, 2)] + [s.SHR(a[3], 1)]

    def lt4(s, a, b):                       # a < b, 13 operations
        lo = [s.LT(a[i], b[i]) for i in range(4)]
        t = lo[0]
        for i in (1, 2, 3):
            t = s.OR(lo[i], s.AND(s.EQ(a[i], b[i]), t))
        return t

    def mul(s, a, b):                       # a * b < 2^IBITS: shift-and-add over IBITS multiplier bits
        s.other(14)                         # 8 loads, 4 zeroing moves, the counter, the constant 1
        c = [0] * 4
        for _ in range(IBITS):
            t = s.AND(b[0], 1)
            s.other()                       # BZ
            if t:
                c = s.add4(c, a)
            a, b = s.shl(a, 1), s.shr1(b)
            s.other(2)                      # SUB, BNZ
        s.other(4)                          # 4 stores
        return c

    def divmod(s, a, b):                    # (a // b, a % b), a < 2^IBITS, b > 0: restoring division over IBITS dividend bits
        s.other(18)                         # 8 loads, 8 zeroing moves, the counter, the constant 1
        a = s.shl(a, 256 * 4 - IBITS)       # the dividend's top bit becomes bit 1023
        r, q = [0] * 4, [0] * 4
        for _ in range(IBITS):
            q = s.shl(q, 1)
            t = s.SHR(a[3], 255)
            a, r = s.shl(a, 1), s.shl(r, 1)
            r[0] = s.OR(r[0], t)
            lt = s.lt4(r, b)
            s.other()                       # BNZ
            if not lt:
                r = s.sub4(r, b)
                q[0] = s.OR(q[0], 1)
            s.other(2)                      # SUB, BNZ
        s.other(8)                          # 8 stores
        return q, r


def words(n):
    return [(n >> (256 * i)) & M256 for i in range(4)]


def number(w):
    return sum(v << (256 * i) for i, v in enumerate(w))


def dp_count(T):
    """Exact count over the field: p = 2^254 + c with c = p mod 2^128 >= T, so exactly (2^126 + 1) * T of the p field elements are distinguished."""
    return ((1 << 126) + 1) * T


def other_fixed(m):
    """Table scans, insertions, the two index passes, constant loads, the message roots, table zeroing (4 per word) and MISC, for m entries."""
    return (m + 1) * (W_DP + W_SCAN * m + W_INS) + 2 * m * W_POS + MSG_OPS + NCONST + 4 * table_words(m) + MISC


def ledger_ops(ops, nstep):
    """Word and field operations of a run, from its counters (nstep = |STEP|)."""
    return (nstep * ops["trail"] + W_GRP * ops["groups"] + W_HIT * ops["hits"] + W_BLOCK * ops["blocks"] + (nstep + W_REC) * ops["rec"]
            + ops["dp"] + ops["table"] + ops["pos"])


_FQ = {}


def fq_ub():
    """Upper bound (units 2^-FB) on the probability that a group of GROUP = 4 fresh values has AND < 2^142 (proof.md Section 5, Lemma 4 (g)):
    write x = h 2^142 + l, l < 2^142, h <= 2^112 (x < p); AND < 2^142 iff the AND of the four h is 0; at most 15^112 + 4 (2^112 + 1)^3 such
    h-tuples, 2^568 choices of the low parts, every value at most 1 / (N - 2^128) likely."""
    if not _FQ:                           # q <= [(15/16)^112 + 4 (2^112 + 1)^3 / 2^448] (2^254 / (N - 2^128))^4, in fixed point rounded up
        f = ONE
        for _ in range(112):
            f = fx_mul_ub(f, (15 * ONE) >> 4)
        f += fx_ratio_ub(4 * ((1 << 112) + 1) ** 3, 1 << 448)
        r = fx_ratio_ub(1 << 254, P - SMAX)
        for _ in range(4):
            f = fx_mul_ub(f, r)
        CNT["add"] += 120
        _FQ[0] = f
    return _FQ[0]


FP_DELTA = 30                             # the false-hit cap exceeds the bound on their mean by the factor 1 + 2^-FP_DELTA
FP_AFTER = 1 << 115                       # allowance for the groups at or after index t (repeated values): at most (D1 + 3) / 4 + 2 of them


def fpcap(B, T=None):
    """The false-hit cap: ceil(mu (1 + 2^-30)) + 2^115 with mu = ceil((B / 4) fq_ub) (proof.md Section 5, Lemma 4 (g))."""
    CNT["mul"] += 2
    CNT["div"] += 2
    CNT["add"] += 4
    mu = ((B // GROUP) * fq_ub() + ONE - 1) >> FB
    return mu + ((mu + (1 << FP_DELTA) - 1) >> FP_DELTA) + FP_AFTER


def fp_fail_ub(B, T):
    """Upper bound (units 2^-FB) on P(false hits > fpcap) (Lemma 4 (g)): the false hits among groups of fresh values are dominated by
    Binomial(B / 4, q), q = fq_ub / 2^FB, of mean mu' <= mu; Chernoff P(Bin > (1 + d) mu') <= e^-(d^2 mu' / 3), d = 2^-30, evaluated at
    mu' >= mu - 1; the groups at or after t number at most (D1 + 3) / 4 + 2 <= 2^115 unless G1 > 2^117, probability <= e^-(theta_lo 2^117)."""
    CNT["mul"] += 4
    CNT["div"] += 2
    CNT["add"] += 4
    mu = ((B // GROUP) * fq_ub() + ONE - 1) >> FB
    assert mu - 1 >= 200 * (3 << (2 * FP_DELTA))       # the Chernoff exponent is at least 200: e^-(d^2 mu' / 3) <= e^-200
    if T not in _FQ:                                   # the two exponentials, once per T (cached)
        _FQ[T] = exp_neg_ub(200, 1) + exp_neg_ub((dp_count(T) - SMAX) << 117, P)
    return _FQ[T]


def ledger(B, m, T):
    """The worst-case total (word operations) of the attempt without the preprocessing term: at most B evaluations in all, trail evaluations at
    |STEP| plus W_GRP per group of GROUP, at most B / UNROLL block tails, recovery evaluations at |STEP| + W_REC and at most RCAP of them,
    W_HIT per hit group: at most m + 1 groups with a DP and at most fpcap(B, T) false hits (proof.md Section 6)."""
    return (B * len(STEP) + (B // GROUP) * W_GRP + (B // UNROLL) * W_BLOCK + RCAP * W_REC + (m + 2 + fpcap(B, T)) * W_HIT
            + other_fixed(m))


def code_instr():
    return UNROLL * len(STEP) + (UNROLL // GROUP) * (W_GRP + W_HIT + 16) + W_BLOCK + (len(STEP) + 20) + NCONST + CODE_OTHER


def fixed_bytes():
    """Bytes of the peak that do not depend on the table size: start word, code, constants, register file, kappa setup."""
    return 32 + code_instr() * 4 + (NCONST + 3 + 11) * 32 + NREG * 32 + D_BYTES


def memory(m=MCAP):
    """Bytes at the peak (the search; setup holds a subset, the offline derivation runs before the attempt): every item is a 32-byte word unless stated."""
    tab = table_words(m) * 32
    consts = (NCONST + 3 + 11) * 32         # step constants, E0, line constants (U0, V0, a, b, c00, c01), INV5, BUDGET, FPCAP, MCAP, p - 2
    return {"table_words": table_words(m), "table": tab, "start_word": 32, "code_instructions": code_instr(), "code": code_instr() * 4,
            "constants": consts, "registers": NREG, "register_file": NREG * 32, "kappa_setup": D_BYTES, "total": tab + fixed_bytes()}


def exp_neg_ub(xn, xd):
    """Upper bound, in units of 2^-FB, on e^-(xn/xd) for xn/xd >= 0: 1/s with s the floored sum of the first KEXP + 1 terms of the series of e^x,
    a lower bound on e^x (all terms are positive).  Counts: 2 KEXP mul, KEXP + 1 div, KEXP + 2 add."""
    term, s, mx = ONE, ONE, 0
    for k in range(1, KEXP + 1):
        t = term * xn
        mx = max(mx, t.bit_length())
        term = t // (xd * k)
        s += term
    CNT["mul"] += 2 * KEXP + 1            # per term t = term xn and xd k; the final ONE ONE
    CNT["div"] += KEXP + 1                # per term one division; the final one
    CNT["add"] += KEXP + 2                # per term s += term; the final + 1 and the loop bound
    CNT["bits"] = max(CNT["bits"], mx)
    return (ONE * ONE) // s + 1


def exp_consts(TAB):
    """e^-TAB as an upper bound (Lemma 4 (e))."""
    return exp_neg_ub(TAB, 1)


def fx_ratio_ub(num, den):
    """ceil(num / den) in units of 2^-FB: an upper bound on the rational num / den."""
    CNT["mul"] += 1
    CNT["div"] += 1
    CNT["add"] += 2
    CNT["bits"] = max(CNT["bits"], (num * ONE).bit_length())
    return (num * ONE + den - 1) // den


def fx_mul_ub(a, b):
    """An upper bound on the product of two numbers in units of 2^-FB (rounded up)."""
    CNT["mul"] += 1
    CNT["add"] += 3
    return (a * b + ONE - 1) >> FB


def mgf_ub(B, T, c=Fraction(1)):
    """Upper bound (units 2^-FB) on E[exp(u X)], X = 2 G1 + 3 G2 + G3 + 6 with G1, G2, G3 independent geometric(theta_lo) on {0, 1, ...}
    (P(G >= j) = (1 - theta_lo)^j) and u = c (2B + 1) / 2N (proof.md Section 5, Lemma 4).  E[e^(v G)] = theta / (1 - (1 - theta) e^v) and
    e^v <= 1 / (1 - v) for 0 <= v < 1 give E[e^(v G)] <= theta (1 - v) / (theta - v) for v < theta, and e^(6u) <= 1 / (1 - 6u).
    With theta = Dl / N, Dl = D - 2^128 and c = cn / cd: theta (1 - j u) / (theta - j u) = Dl (2 N cd - j cn (2B + 1)) / (N (2 Dl cd - j cn (2B + 1)))."""
    Dl, cn, cd = dp_count(T) - SMAX, c.numerator, c.denominator
    w = cn * (2 * B + 1)
    CNT["mul"] += 4
    CNT["add"] += 4
    assert 2 * Dl * cd > 3 * w and 2 * P * cd > 6 * w
    m = fx_ratio_ub(2 * P * cd, 2 * P * cd - 6 * w)       # e^(6u) <= 1 / (1 - 6u)
    for j in (2, 3, 1):                                    # the factors of G1 (weight 2), G2 (weight 3), G3 (weight 1)
        CNT["mul"] += 6
        CNT["add"] += 4
        m = fx_mul_ub(m, fx_ratio_ub(Dl * (2 * P * cd - j * w), P * (2 * Dl * cd - j * w)))
    return m


def rcap_ub(T):
    """Upper bound (units 2^-FB) on P(G1 + 3 G2 + G3 + 3 > RCAP) by the Chernoff bound at v = theta_lo / 4: e^(3v) <= 4, E[e^(v G)] <= 4/3,
    E[e^(3v G)] <= 4, so the probability is at most (256 / 9) e^-(theta_lo RCAP / 4) (proof.md Section 5, Lemma 4 (d))."""
    Dl = dp_count(T) - SMAX
    CNT["mul"] += 3
    CNT["div"] += 1
    CNT["add"] += 3
    return (256 * exp_neg_ub(Dl * RCAP, 4 * P) + 8) // 9


_EW = {}


def gap_width_ub(T):
    """Upper bound (units 2^-FB) on P(some stored index gap >= 2^GBITS): such a gap holds 2^119 - 1 consecutive indices below t with no DP, hence a
    whole aligned block [j 2^118, (j + 1) 2^118) below t with no DP; at most 2^10 blocks lie below SMAX = 2^128, each empty with probability at
    most (1 - theta_lo)^(2^118) <= e^-(theta_lo 2^118) by Lemma 1 (iii)."""
    if T not in _EW:
        CNT["add"] += 8
        CNT["mul"] += 2
        _EW[T] = (1 << (128 - (GBITS - 1))) * exp_neg_ub((dp_count(T) - SMAX) << (GBITS - 1), P)
    return _EW[T]


def success_fp(B, T, ek, c=Fraction(1)):
    """Lower bound (units 2^-FB) on P_F(success) for the evaluation budget B (proof.md Section 5, Lemma 4):
    1 - e^(-c B (B + 1) / 2N) E[e^(u X)] - c B / (theta_lo N) - c B / N - P(X_R > RCAP) - e^-TAB - E_W, N = p, theta_lo N = D - 2^128;
    E_W = 2^10 e^-(theta_lo 2^118) bounds an index gap of 2^119 or more.  c = 1 is the random function; other c is the deviation model of Section 8:
    a uniformly random map on N / c points with the same DP fraction, so every 1/N carries c/N.  Every subtracted term is an upper bound.  Returns (bound, eps)
    with eps the sum of the subtracted terms other than the trail term."""
    e_tab = ek
    cn, cd = c.numerator, c.denominator
    Dl = dp_count(T) - SMAX
    en = exp_neg_ub(cn * B * (B + 1), cd * 2 * P)
    trail = fx_mul_ub(en, mgf_ub(B, T, c))
    cyc = fx_ratio_ub(cn * B, cd * Dl)                     # the cycle holds no DP (G1 >= lambda): at most c B / (theta_lo N)
    start = fx_ratio_ub(cn * B, cd * P)                    # the start is on the cycle (mu = 0): at most c B / N
    eps = cyc + start + rcap_ub(T) + e_tab + gap_width_ub(T) + fp_fail_ub(B, T)
    CNT["mul"] += 8
    CNT["add"] += 14
    return ONE - trail - eps, eps


def budget_of(k):
    """B: the least multiple of UNROLL at or above k 2^100."""
    CNT["mul"] += 2
    CNT["div"] += 1
    CNT["add"] += 3
    return -(-(k * GRAIN) // UNROLL) * UNROLL


def least_k(q, T, ek):
    """The least k whose budget B = budget_of(k) reaches the success bound q, by bisection on [2^26, 2^28] (B between 2^126 and 2^128; the bound is
    below q at the lower end and at least q at the upper end, both asserted; the claim needs only that the bound at the returned k reaches q).  At most 30 evaluations."""
    ok = lambda k: success_fp(budget_of(k), T, ek)[0] * q.denominator >= q.numerator * ONE
    lo, hi = 1 << 26, 1 << 28
    assert not ok(lo) and ok(hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
    CNT["add"] += 150                     # at most 30 evaluations (2 + 28 bisection steps), each with a comparison and a midpoint
    CNT["mul"] += 90                      # the comparison of each evaluation with q: three products
    CNT["div"] += 28                      # the midpoints
    return hi


def table_exp(S, T, m):
    """Upper bound (units 2^-FB) on ln P(more than m of the stored DPs), by the Chernoff bound of Section 5 (Lemma 4 (e)):
    f(mu) = -mu + a (1 + ln(mu / a)), a = m + 1, mu = ceil(S theta_hi) < a, increasing in mu below a; ln(mu / a) <= -(u + u^2/2 + ... + u^KLN / KLN),
    u = 1 - ceil(mu / a) rounded down, since the dropped terms are positive.  Returns (f, mu); f is None if mu >= a."""
    a = m + 1
    mu = (S * dp_count(T) * ONE + (P - SMAX) - 1) // (P - SMAX)
    CNT["mul"] += 3
    CNT["div"] += 1
    CNT["add"] += 12
    CNT["bits"] = max(CNT["bits"], (S * dp_count(T) * ONE).bit_length(), (a * ONE).bit_length() + FB)
    if mu >= a * ONE:
        return None, mu
    u = ONE - (mu + a - 1) // a
    pw, tot = u, 0
    for k in range(1, KLN + 1):
        tot += pw // k
        pw = (pw * u) >> FB
    CNT["mul"] += KLN + 2
    CNT["div"] += KLN + 2
    CNT["add"] += 3 * KLN + 8
    return a * (ONE - tot) - mu, mu


def derive(T, m, TAB, q=Q_RANDOM, ek=None):
    """The offline derivation of the evaluation budget B from T_DP = T (integers only)."""
    ek = ek or exp_consts(TAB)
    k = least_k(q, T, ek)
    B = budget_of(k)
    assert success_fp(B, T, ek)[0] * q.denominator >= q.numerator * ONE
    CNT["mul"] += 3
    CNT["add"] += 2
    return {"k": k, "B": B, "ek": ek}


def plan():
    """Offline: re-derives and asserts the literal BUDGET, T_DP < 2^16, the table bound and the memory, then prints the ledger.  Everything
    that fixes a literal or a charge is exact integer arithmetic above; the floats below only format the report (log2 of integers, decimal
    printing) and no literal of the program is computed from them."""
    for key in CNT:
        CNT[key] = 0
    ek = exp_consts(TAB)
    r = derive(T_DP, MCAP, TAB, Q_RANDOM, ek)
    B, k = r["B"], r["k"]
    succ, eps = success_fp(B, T_DP, ek)
    assert succ * Q_RANDOM.denominator >= Q_RANDOM.numerator * ONE
    D_DP = dp_count(T_DP)
    x = B * (B + 1) / (2 * P)             # exponent of the random-function law: P(no repeat in B steps) <= e^-x
    lo, hi = 1, 1 << 14                   # the least collision-rate factor c = j / 2^14 at which the bound reaches 0.39 (14 evaluations)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if success_fp(B, T_DP, ek, Fraction(mid, 1 << 14))[0] * Q_CLAIM.denominator >= Q_CLAIM.numerator * ONE:
            hi = mid
        else:
            lo = mid
    rate_min = hi / (1 << 14)
    CNT["mul"] += 2 * 20                  # the comparisons of the 14 + 6 evaluations above with 0.39
    rate_table = {str(float(c)): success_fp(B, T_DP, ek, c)[0] / ONE for c in (Fraction(1), Fraction(9, 10), Fraction(3, 4), Fraction(3, 5), Fraction(1, 2), Fraction(2, 5))}
    mgf = mgf_ub(B, T_DP)
    assert BUDGET is None or B == BUDGET, "BUDGET is the plan's B"
    assert B < SMAX and B % UNROLL == 0 and T_DP < (1 << 16) and RCAP < B
    total_ops = ledger(B, MCAP, T_DP) + PREP_OPS
    f, mu = table_exp(B, T_DP, MCAP)
    assert f is not None and f <= -TAB * ONE      # the table-overflow bound of Section 5: mean < MCAP + 1 and ln P(overflow) <= -TAB
    mem = memory()
    assert mem["total"] <= 1 << 20
    prep_peak = fixed_bytes() + 4 * PREP_INSTR + PREP_DATA     # offline code and data (in the table's address range, before the table exists) beside the resident items
    assert prep_peak <= mem["total"]
    ws = len(STEP) + W_LOOP
    tlog = log2(total_ops / C_UNIT)
    assert CNT["bits"] < IBITS
    plan_words = W_IADD * CNT["add"] + W_IMUL * CNT["mul"] + W_IDIV * CNT["div"]
    assert plan_words <= PLAN_OPS
    return {"partial_rounds": PARTIAL, "C": C_UNIT, "step_field_ops": len(STEP), "step_add": sum(o[0] == "ADD" for o in STEP),
            "step_mul": sum(o[0] == "MUL" for o in STEP), "W_LOOP": W_LOOP, "W_BLOCK": W_BLOCK, "W_REC": W_REC,
            "ops_per_trail_step": len(STEP) + W_GRP / GROUP + W_BLOCK / UNROLL, "T_DP": T_DP, "MCAP": MCAP, "TAB": TAB, "RCAP_log2": log2(RCAP),
            "theta_log2": log2(D_DP / P), "k": k, "B": B, "B_log2": log2(B), "x": x,
            "mgf_bound": mgf / ONE, "trail_term": (ONE - succ - eps) / ONE, "eps_other": eps / ONE,
            "success_lower_bound": succ / ONE, "success_lower_bound_decimal": "0." + str(succ * 10 ** 20 // ONE).zfill(20),
            "rate_min": rate_min, "rate_table": rate_table, "mean_stored_bound": mu / ONE, "ln_P_table_overflow": f / ONE,
            "cycle_term": fx_ratio_ub(B, D_DP - SMAX) / ONE, "start_term": fx_ratio_ub(B, P) / ONE, "rcap_term": rcap_ub(T_DP) / ONE,
            "other_fixed": other_fixed(MCAP), "gap_width_bound": gap_width_ub(T_DP) / ONE, "prep_ops": PREP_OPS,
            "prep_log2_units": log2(max(PREP_OPS, 1) / C_UNIT), "total_ops": total_ops,
            "T_units": total_ops / C_UNIT, "time_log2": tlog, "constants": NCONST, "memory": mem,
            "prep_instr": PREP_INSTR, "prep_data_bytes": PREP_DATA, "prep_peak_bytes": prep_peak, "outscale_1": hex(OUTSCALE),
            "plan_integer_ops": {k: CNT[k] for k in ("add", "mul", "div")}, "plan_word_ops": plan_words, "recipe_search_word_ops_bound": RECIPE_OPS}


def tune():
    """Offline: the finite parameter search that fixes the literals T_DP, MCAP, TAB and UNROLL.  A cell (U, TAB) takes the largest
    table MCAP with memory <= 2^20 (bisection) and the largest T in [40000, 65535] whose derivation passes the table bound (bisection, 16 probes);
    its value is the exact ledger total.  Descent from (18, 13): try U +- 1 and TAB +- 1, move to any strictly lower total, repeat until no move.
    Returns the cell count, the metered integer operations (CNT) and the word operations they price to; asserts that the result is the program's literals."""
    global UNROLL
    u0 = UNROLL
    for key in CNT:
        CNT[key] = 0
    cells, mc = [0], {}

    def mcap(U):
        lo, hi = 1, 1 << 17
        while lo < hi:
            mid = (lo + hi + 1) // 2
            CNT["add"] += 24                  # the midpoint, the comparison, and `memory` (table_words, code_instr, fixed_bytes)
            CNT["mul"] += 10
            CNT["div"] += 2
            if memory(mid)["total"] <= 1 << 20:
                lo = mid
            else:
                hi = mid - 1
        return lo

    def cell(U, tab):
        global UNROLL
        UNROLL = U
        if U not in mc:
            mc[U] = mcap(U)
        M = mc[U]
        cells[0] += 1
        ek = exp_consts(tab)

        def feas(T):
            CNT["mul"] += 1
            CNT["add"] += 1
            r = derive(T, M, tab, Q_RANDOM, ek)
            f, mu = table_exp(r["B"], T, M)
            return f is not None and f <= -tab * ONE
        lo, hi = 40000, (1 << 16) - 1
        if not feas(lo):
            return None
        while lo < hi:
            mid = (lo + hi + 1) // 2
            CNT["add"] += 5                   # the midpoint, the loop test, the update
            CNT["div"] += 1
            if feas(mid):
                lo = mid
            else:
                hi = mid - 1
        r = derive(lo, M, tab, Q_RANDOM, ek)
        CNT["add"] += 80                      # the comparison with the best total, and `ledger` with `other_fixed` and `table_words`
        CNT["mul"] += 16
        CNT["div"] += 4
        return ledger(r["B"], M, lo), (U, tab, lo, M)
    U, tab = 48, 15
    best = cell(U, tab)
    moved = True
    while moved:
        moved = False
        for c in ((U - GROUP, tab), (U + GROUP, tab), (U, tab - 1), (U, tab + 1)):
            r = cell(*c)
            if r and r[0] < best[0]:
                best, moved = r, True
                U, tab = c
    UNROLL = u0
    assert best[1] == (UNROLL, TAB, T_DP, MCAP), best[1]
    words = W_IADD * CNT["add"] + W_IMUL * CNT["mul"] + W_IDIV * CNT["div"]
    offline = words + PLAN_OPS + RECIPE_OPS + BUILD_OPS         # everything offline: this search, one run of `plan`, the recipe search, `build_step`
    assert CNT["bits"] < IBITS and offline < PREP_OPS
    return {"cells": cells[0], "result": list(best[1]),
            "integer_ops": {k: CNT[k] for k in ("add", "mul", "div")}, "prices": {"add": W_IADD, "mul": W_IMUL, "div": W_IDIV},
            "max_operand_bits": CNT["bits"], "word_ops": words, "offline_word_ops_bound": offline, "offline_log2": log2(offline),
            "word_ops_log2": log2(words), "per_cell_word_ops": words // cells[0], "charged_prep_ops_log2": log2(PREP_OPS)}


def attempt(coin):
    """The claimed attempt (one run, not repeated). It executes only the step program, the table logic and the recovery: BUDGET and RCAP are integer literals (printed with the parameters in section 5), not computed online; `plan` is the offline derivation and check of BUDGET and of the ledger. coin = two uniformly random 256-bit words; rho0 and x0 are their low 254 bits (every
    254-bit word is below p, so both are canonical). The walk is F(x) = digest(message(x + rho0)) / OUTSCALE. Returns the two 64-byte messages or None."""
    m254 = (1 << 254) - 1
    rho0, x0 = coin[0] & m254, coin[1] & m254
    if LEV_D:
        rho0 = rho0 or 1                  # kappa != 0 (the zero word has probability 2^-254)
    pair, status, ev, ops = search(make_F(rho0), dp_count(T_DP), x0, BUDGET, MCAP, RCAP, fpcap(BUDGET))
    if pair is None:
        return None
    (a0, a1), (b0, b1) = (message((rho0 * pair[0] - E0[0]) % P), message((rho0 * pair[1] - E0[0]) % P)) if LEV_D else \
        (message((pair[0] + rho0) % P), message((pair[1] + rho0) % P))
    return enc(a0) + enc(a1), enc(b0) + enc(b1)


# ================================================================ 6 self-checks (reduced width) and command line
NB = 14                                   # walk width of the self-check: the low 14 bits of F (real step program, real rounds)


def run_rho(seed):
    """The search of `attempt` on the reduced map v -> low NB bits of F(v), rho and the start taken from the seed; the pair is checked on the
    reference digest: distinct messages whose digests agree in the low bits that the reduced map keeps (after the division by OUTSCALE)."""
    rho = int(seed, 16) >> 2
    x0 = int(seed[:8], 16) % (1 << NB)
    F = make_F(rho)
    cache = {}

    def F_n(v):
        r = cache.get(v)
        if r is None:
            r = cache[v] = F(v) & ((1 << NB) - 1)
        return r
    pair, status, ev, ops = search(F_n, 1 << (NB - 4), x0, 256 - 256 % UNROLL, 64, 160, 64)   # budget 240, recovery at most 160, at most 64 false hits
    if pair is None:
        return None, {"status": status, "evals": ev, "ops": ops}
    a, b = pair
    if LEV_D:
        rho = rho or 1
        ma, mb = message((rho * a - E0[0]) % P), message((rho * b - E0[0]) % P)
        oi = inv(kappa_consts(rho)[1])
    else:
        ma, mb = message((a + rho) % P), message((b + rho) % P)
        oi = OUTINV
    assert a != b and ma != mb and F_n(a) == F_n(b)
    assert (digest(*ma) * oi % P) & ((1 << NB) - 1) == (digest(*mb) * oi % P) & ((1 << NB) - 1)
    return (ma, mb), {"status": status, "evals": ev, "ops": ops}


ATTEMPT_AND_CHECKS = ("make_F", "search", "attempt", "_get", "_put", "Wm", "words", "number", "run_rho", "offline_nodes", "selftest", "listing", "main")


def offline_nodes():
    """Operator, call and subscript nodes of the offline source: every top-level definition and statement of this file except the attempt (`make_F`, `search`,
    `attempt`, `_get`, `_put`), the word machine and the self-checks.  Proof.md Section 7 bounds the compiled offline code by 8 instructions per node."""
    import ast
    tree = ast.parse(open(__file__, encoding="utf-8").read())
    return sum(isinstance(n, (ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare, ast.Call, ast.Subscript)) for top in tree.body
               if getattr(top, "name", None) not in ATTEMPT_AND_CHECKS for n in ast.walk(top))


def selftest():
    import random
    rng = random.Random(PARTIAL)
    for _ in range(4):                    # the line: rounds 0 and 1 are affine in W, message is injective on samples
        W = rng.randrange(P)
        A, A1, S = after_round1(*message(0)), after_round1(*message(1)), after_round1(*message(W))
        assert all(S[i] == (A[i] + W * (A1[i] - A[i])) % P for i in range(3))
        assert message(W) != message((W + 1) % P)
    for _ in range(6):                    # the step program equals the reference digest of the line message, divided by OUTSCALE
        x, rho0 = rng.randrange(P), rng.randrange(1, 1 << 254)
        if LEV_D:
            _, osk = kappa_consts(rho0)
            assert make_F(rho0)(x) == digest(*message((rho0 * x - E0[0]) % P)) * inv(osk) % P
        else:
            assert make_F(rho0)(x) == digest(*message((x + rho0) % P)) * OUTINV % P
    assert len(STEP) == (135 if LEV_D else 136) + 12 * PARTIAL
    ix = _IDX["x"]                        # the group ring: STEP writes x only in its last two operations, so a copy may write a fresh register
    assert [n for n, (m, d, s1, t1) in enumerate(_CODE) if d == ix] == [len(STEP) - 2, len(STEP) - 1]
    for _ in range(3):                    # run STEP with its output renamed to a fresh register: the input register is unchanged, the output is F(x)
        x, rho0 = rng.randrange(P), rng.randrange(1, 1 << 254)
        R = [0] * (NREG_STEP + 1)
        for name, v in kappa_consts(rho0)[0].items():
            R[_IDX[name]] = v
        R[ix] = x
        out = False                       # reads of x after its first write refer to the renamed output register
        for m, d, s1, t1 in _CODE:
            s1, t1 = (NREG_STEP if out and s1 == ix else s1), (NREG_STEP if out and t1 == ix else t1)
            if d == ix:
                d, out = NREG_STEP, True
            R[d] = R[s1] * R[t1] % P if m else (R[s1] + R[t1]) % P
        assert R[ix] == x and R[NREG_STEP] == make_F(rho0)(x)
    tw, recs, off = [0] * table_words(2000), [], 0     # the packed table at full width: 2000 random entries read back exactly
    for _ in range(2000):
        v, g = rng.randrange(dp_count(T_DP)), rng.randrange(1, 1 << GBITS)
        _put(tw, off, v)
        _put(tw, off + VBITS, g)
        recs.append((v, g))
        off += RBITS
    assert all(_get(tw, j * RBITS, VBITS) == v and _get(tw, j * RBITS + VBITS, GBITS) == g for j, (v, g) in enumerate(recs))
    ok, worst = 0, 0
    for t in range(24):
        res, ob = run_rho(hashlib.sha256(b"t%d" % t).hexdigest())
        ok += res is not None
        o = ob["ops"]
        bb = 256 - 256 % UNROLL           # the ledger formula of Section 6 at the self-check's budget bb, recovery cap 160 and table of 64
        bound = len(STEP) * bb + W_GRP * (bb // GROUP) + W_BLOCK * (bb // UNROLL) + W_REC * 160 + (64 + 2 + 64) * W_HIT + (64 + 1) * (W_DP + W_SCAN * 64 + W_INS) + 2 * 64 * W_POS
        assert ledger_ops(o, len(STEP)) <= bound and o["trail"] + o["rec"] <= bb and o["rec"] <= 160
        worst = max(worst, ledger_ops(o, len(STEP)))
    for _ in range(40):                   # the integer routines on the word machine: results equal Python's, counts are within the prices
        a, b = rng.getrandbits(rng.randrange(1, IBITS // 2)), rng.getrandbits(rng.randrange(1, IBITS // 2 - 1))
        m = Wm()
        assert number(m.mul(words(a), words(b))) == a * b and m.n <= W_IMUL
        m = Wm()
        q, r = m.divmod(words(a * b + 7), words(a or 1))
        assert (number(q), number(r)) == divmod(a * b + 7, a or 1) and m.n <= W_IDIV
    full = (1 << IBITS) - 1
    m = Wm()
    assert number(m.mul(words(1), words(full))) == full and m.n == W_IMUL                  # the worst cases are the prices
    m = Wm()
    assert tuple(map(number, m.divmod(words(full), words(1)))) == (full, 0) and m.n == W_IDIV
    for f, w in ((lambda m: m.add4(words(5), words(7)), W_ADD4), (lambda m: m.sub4(words(9), words(7)), W_ADD4), (lambda m: m.shl(words(9), 1), W_SH4),
                 (lambda m: m.shr1(words(9)), W_SH4), (lambda m: m.lt4(words(9), words(7)), W_CMP4)):
        m = Wm()
        f(m)
        assert m.n == w
    assert 8 + W_ADD4 + 4 <= W_IADD and 8 + W_CMP4 + 1 <= W_IADD and 4 + W_SH4 + 4 <= W_IADD
    nodes = offline_nodes()
    assert 8 * nodes + 300 <= PREP_INSTR  # the offline code: 8 instructions per node, plus the three integer routines (at most 300 instructions)
    return {"step_ops": len(STEP), "line_affine": True, "step_equals_reference": 6, "packed_entries_checked": 2000, "rho_n14_pairs": ok, "of": 24, "largest_counted_ops": worst,
            "word_machine_mul": W_IMUL, "word_machine_div": W_IDIV, "offline_nodes": nodes}


def listing():
    return "\n".join("%s %s, %s, %s" % s for s in STEP)


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--plan":
            print(json.dumps(plan(), indent=1))
        elif sys.argv[1] == "--selftest":
            print(json.dumps(selftest()))
        elif sys.argv[1] == "--tune":
            print(json.dumps(tune(), indent=1))
        elif sys.argv[1] == "--listing":
            print(listing())
        return
    print(json.dumps(plan(), indent=1))


if __name__ == "__main__":
    main()
```

## Appendix C: the step program, `python3 rho.py --listing` (807 operations: op dest, src1, src2; k<n> are the step constants, e1, e2 the attempt registers)

```
ADD y1, x, e1
ADD y2, x, e2
MUL s_z0, x, x
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, x
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k0
MUL t2, z2, k1
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k2
MUL t1, z1, k3
MUL t2, z2, k4
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k5
MUL t1, z1, k6
MUL t2, z2, k7
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k8
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k9
MUL t2, z2, k10
ADD h0, z0, t1
ADD h0, h0, t2
MUL t1, z1, k11
MUL t2, z2, k12
ADD h1, z0, t1
ADD h1, h1, t2
MUL t1, z1, k13
MUL t2, z2, k14
ADD h2, z0, t1
ADD h2, h2, t2
ADD u, h0, k15
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k16
MUL t2, h2, k17
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k18
ADD h1, h1, t1
MUL t2, x5, k19
ADD h2, h2, t2
ADD u, h0, k20
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k21
MUL t2, h2, k22
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k23
ADD h1, h1, t1
MUL t2, x5, k24
ADD h2, h2, t2
ADD u, h0, k25
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k26
MUL t2, h2, k27
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k28
ADD h1, h1, t1
MUL t2, x5, k29
ADD h2, h2, t2
ADD u, h0, k30
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k31
MUL t2, h2, k32
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k33
ADD h1, h1, t1
MUL t2, x5, k34
ADD h2, h2, t2
ADD u, h0, k35
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k36
MUL t2, h2, k37
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k38
ADD h1, h1, t1
MUL t2, x5, k39
ADD h2, h2, t2
ADD u, h0, k40
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k41
MUL t2, h2, k42
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k43
ADD h1, h1, t1
MUL t2, x5, k44
ADD h2, h2, t2
ADD u, h0, k45
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k46
MUL t2, h2, k47
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k48
ADD h1, h1, t1
MUL t2, x5, k49
ADD h2, h2, t2
ADD u, h0, k50
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k51
MUL t2, h2, k52
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k53
ADD h1, h1, t1
MUL t2, x5, k54
ADD h2, h2, t2
ADD u, h0, k55
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k56
MUL t2, h2, k57
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k58
ADD h1, h1, t1
MUL t2, x5, k59
ADD h2, h2, t2
ADD u, h0, k60
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k61
MUL t2, h2, k62
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k63
ADD h1, h1, t1
MUL t2, x5, k64
ADD h2, h2, t2
ADD u, h0, k65
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k66
MUL t2, h2, k67
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k68
ADD h1, h1, t1
MUL t2, x5, k69
ADD h2, h2, t2
ADD u, h0, k70
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k71
MUL t2, h2, k72
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k73
ADD h1, h1, t1
MUL t2, x5, k74
ADD h2, h2, t2
ADD u, h0, k75
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k76
MUL t2, h2, k77
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k78
ADD h1, h1, t1
MUL t2, x5, k79
ADD h2, h2, t2
ADD u, h0, k80
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k81
MUL t2, h2, k82
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k83
ADD h1, h1, t1
MUL t2, x5, k84
ADD h2, h2, t2
ADD u, h0, k85
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k86
MUL t2, h2, k87
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k88
ADD h1, h1, t1
MUL t2, x5, k89
ADD h2, h2, t2
ADD u, h0, k90
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k91
MUL t2, h2, k92
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k93
ADD h1, h1, t1
MUL t2, x5, k94
ADD h2, h2, t2
ADD u, h0, k95
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k96
MUL t2, h2, k97
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k98
ADD h1, h1, t1
MUL t2, x5, k99
ADD h2, h2, t2
ADD u, h0, k100
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k101
MUL t2, h2, k102
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k103
ADD h1, h1, t1
MUL t2, x5, k104
ADD h2, h2, t2
ADD u, h0, k105
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k106
MUL t2, h2, k107
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k108
ADD h1, h1, t1
MUL t2, x5, k109
ADD h2, h2, t2
ADD u, h0, k110
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k111
MUL t2, h2, k112
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k113
ADD h1, h1, t1
MUL t2, x5, k114
ADD h2, h2, t2
ADD u, h0, k115
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k116
MUL t2, h2, k117
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k118
ADD h1, h1, t1
MUL t2, x5, k119
ADD h2, h2, t2
ADD u, h0, k120
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k121
MUL t2, h2, k122
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k123
ADD h1, h1, t1
MUL t2, x5, k124
ADD h2, h2, t2
ADD u, h0, k125
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k126
MUL t2, h2, k127
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k128
ADD h1, h1, t1
MUL t2, x5, k129
ADD h2, h2, t2
ADD u, h0, k130
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k131
MUL t2, h2, k132
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k133
ADD h1, h1, t1
MUL t2, x5, k134
ADD h2, h2, t2
ADD u, h0, k135
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k136
MUL t2, h2, k137
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k138
ADD h1, h1, t1
MUL t2, x5, k139
ADD h2, h2, t2
ADD u, h0, k140
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k141
MUL t2, h2, k142
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k143
ADD h1, h1, t1
MUL t2, x5, k144
ADD h2, h2, t2
ADD u, h0, k145
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k146
MUL t2, h2, k147
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k148
ADD h1, h1, t1
MUL t2, x5, k149
ADD h2, h2, t2
ADD u, h0, k150
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k151
MUL t2, h2, k152
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k153
ADD h1, h1, t1
MUL t2, x5, k154
ADD h2, h2, t2
ADD u, h0, k155
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k156
MUL t2, h2, k157
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k158
ADD h1, h1, t1
MUL t2, x5, k159
ADD h2, h2, t2
ADD u, h0, k160
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k161
MUL t2, h2, k162
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k163
ADD h1, h1, t1
MUL t2, x5, k164
ADD h2, h2, t2
ADD u, h0, k165
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k166
MUL t2, h2, k167
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k168
ADD h1, h1, t1
MUL t2, x5, k169
ADD h2, h2, t2
ADD u, h0, k170
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k171
MUL t2, h2, k172
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k173
ADD h1, h1, t1
MUL t2, x5, k174
ADD h2, h2, t2
ADD u, h0, k175
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k176
MUL t2, h2, k177
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k178
ADD h1, h1, t1
MUL t2, x5, k179
ADD h2, h2, t2
ADD u, h0, k180
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k181
MUL t2, h2, k182
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k183
ADD h1, h1, t1
MUL t2, x5, k184
ADD h2, h2, t2
ADD u, h0, k185
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k186
MUL t2, h2, k187
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k188
ADD h1, h1, t1
MUL t2, x5, k189
ADD h2, h2, t2
ADD u, h0, k190
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k191
MUL t2, h2, k192
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k193
ADD h1, h1, t1
MUL t2, x5, k194
ADD h2, h2, t2
ADD u, h0, k195
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k196
MUL t2, h2, k197
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k198
ADD h1, h1, t1
MUL t2, x5, k199
ADD h2, h2, t2
ADD u, h0, k200
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k201
MUL t2, h2, k202
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k203
ADD h1, h1, t1
MUL t2, x5, k204
ADD h2, h2, t2
ADD u, h0, k205
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k206
MUL t2, h2, k207
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k208
ADD h1, h1, t1
MUL t2, x5, k209
ADD h2, h2, t2
ADD u, h0, k210
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k211
MUL t2, h2, k212
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k213
ADD h1, h1, t1
MUL t2, x5, k214
ADD h2, h2, t2
ADD u, h0, k215
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k216
MUL t2, h2, k217
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k218
ADD h1, h1, t1
MUL t2, x5, k219
ADD h2, h2, t2
ADD u, h0, k220
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k221
MUL t2, h2, k222
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k223
ADD h1, h1, t1
MUL t2, x5, k224
ADD h2, h2, t2
ADD u, h0, k225
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k226
MUL t2, h2, k227
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k228
ADD h1, h1, t1
MUL t2, x5, k229
ADD h2, h2, t2
ADD u, h0, k230
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k231
MUL t2, h2, k232
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k233
ADD h1, h1, t1
MUL t2, x5, k234
ADD h2, h2, t2
ADD u, h0, k235
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k236
MUL t2, h2, k237
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k238
ADD h1, h1, t1
MUL t2, x5, k239
ADD h2, h2, t2
ADD u, h0, k240
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k241
MUL t2, h2, k242
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k243
ADD h1, h1, t1
MUL t2, x5, k244
ADD h2, h2, t2
ADD u, h0, k245
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k246
MUL t2, h2, k247
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k248
ADD h1, h1, t1
MUL t2, x5, k249
ADD h2, h2, t2
ADD u, h0, k250
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k251
MUL t2, h2, k252
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k253
ADD h1, h1, t1
MUL t2, x5, k254
ADD h2, h2, t2
ADD u, h0, k255
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k256
MUL t2, h2, k257
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k258
ADD h1, h1, t1
MUL t2, x5, k259
ADD h2, h2, t2
ADD u, h0, k260
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k261
MUL t2, h2, k262
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k263
ADD h1, h1, t1
MUL t2, x5, k264
ADD h2, h2, t2
ADD u, h0, k265
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k266
MUL t2, h2, k267
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k268
ADD h1, h1, t1
MUL t2, x5, k269
ADD h2, h2, t2
ADD u, h0, k270
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k271
MUL t2, h2, k272
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k273
ADD h1, h1, t1
MUL t2, x5, k274
ADD h2, h2, t2
ADD u, h0, k275
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k276
MUL t2, h2, k277
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k278
ADD h1, h1, t1
MUL t2, x5, k279
ADD h2, h2, t2
ADD u, h0, k280
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k281
MUL t2, h2, k282
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k283
ADD h1, h1, t1
MUL t2, x5, k284
ADD h2, h2, t2
ADD u, h0, k285
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k286
MUL t2, h2, k287
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k288
ADD h1, h1, t1
MUL t2, x5, k289
ADD h2, h2, t2
ADD u, h0, k290
MUL s_x5, u, u
MUL s_x5, s_x5, s_x5
MUL x5, s_x5, u
MUL t1, h1, k291
MUL t2, h2, k292
ADD h0, x5, t1
ADD h0, h0, t2
MUL t1, x5, k293
ADD h1, h1, t1
MUL t2, x5, k294
ADD h2, h2, t2
ADD y0, h0, k295
ADD y1, h1, k296
ADD y2, h2, k297
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k298
MUL t2, z2, k299
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k300
MUL t1, z1, k301
MUL t2, z2, k302
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k303
MUL t1, z1, k304
MUL t2, z2, k305
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k306
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k307
MUL t2, z2, k308
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k309
MUL t1, z1, k310
MUL t2, z2, k311
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k312
MUL t1, z1, k313
MUL t2, z2, k314
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k315
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k316
MUL t2, z2, k317
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k318
MUL t1, z1, k319
MUL t2, z2, k320
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k321
MUL t1, z1, k322
MUL t2, z2, k323
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k324
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k325
MUL t2, z2, k326
ADD x, z0, t1
ADD x, x, t2
```
