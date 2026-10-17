# poseidon-orchard-r24: birthday search on an equivalent-form permutation, one trail with distinguished points

Method: the textbook collision search (Pollard rho with distinguished points, van Oorschot-Wiener) on the Orchard hash with 24 partial rounds, with every evaluation of the hash executed as an equivalent straight-line program whose field operations are each charged 1/C. The equivalent form uses two published techniques: the input line on which the first two full rounds are affine (the two-round bypass of Bariant, Bouvier, Leurent and Perrin, ToSC 2022) and the sparse partial-round form of the linear layer (Grassi, Khovratovich, Rechberger, Roy and Schofnegger, Poseidon, USENIX Security 2021), here with every lane held divided by a known constant so that one coefficient of each linear combination is 1. The search, the table logic and the success lemma are those of our r = 23 entry e51feba1, re-parametrised for this row. No other participant's program was used or run. Claim: time_log2 = 126.24451, memory 1,048,568 bytes (claimed 2^20), success probability 0.39, preprocessing as bounded in Section 6a (inside the time), no advice. The probability does not use any property of the rounds.

## 1. Target, line and walk

Target `poseidon-orchard-r24-prefix-v1`: input two canonical elements (m0, m1) of the Pallas base field, p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001 (N = p, about 2^254); initial state [m0, m1, 2^65]; rounds 0-3 full, 4-27 partial, 60-63 full (deployed constants and MDS M); digest = state[0], the complete element compared. Cost model `orchard-field-ram-v2`: C(24) = 216 + 21 * 24 = 720; one canonical field addition or multiplication, or one primitive 256-bit word operation, costs 1/720 unit.

Line (Appendix B, `line`, `message`). Round 0 maps (m0, m1) to U = (m0 + c_{0,0})^5 and V = (m1 + c_{0,1})^5, a bijection (gcd(5, p - 1) = 1), and its third lane is the constant K = (2^65 + c_{0,2})^5; the S-box input of round 1 is therefore affine in (U, V). On the line (U, V) = (U0 + a tau, V0 + b tau) with a = M[0][1], b = -M[0][0], lane 0 of that input is constant, and U0, V0 are chosen (a 2 x 2 system, determinant M[1][0] M[2][1] - M[2][0] M[1][1] != 0) so that lanes 1 and 2 equal d_1 tau and d_2 tau. The round-1 S-boxes then output a constant and d_i^5 tau^5, so with W = tau^5 the state after round 1 is A + W B for two constant vectors A, B; the program computes A and B with the reference rounds at W = 0 and W = 1, and `--selftest` checks A + W B against the reference rounds at random W. message(W) = (U^(1/5) - c_{0,0}, V^(1/5) - c_{0,1}) with tau = W^(1/5) is injective: W -> tau, tau -> (U, V) (a != 0) and (U, V) -> (m0, m1) are each injective.

Walk. The attempt draws two coins, rho0 and x_0, each the low 254 bits of a uniformly random 256-bit word (canonical). It iterates F(x) = digest(message(x + rho0)) / OUTSCALE, where OUTSCALE is a fixed nonzero field constant of the program (Section 2): x_i = F(x_{i-1}). F maps the field to the field. Two values x != y with F(x) = F(y) give W = x + rho0 != W' = y + rho0, hence two distinct 64-byte messages message(W), message(W') with equal digests: a collision of the target.

## 2. The step program: the hash in an equivalent form (424 field operations)

One evaluation of F is the straight-line program `STEP` (Appendix C, printed by `python3 rho.py --listing`): 424 = 136 + 12 * 24 operations, 170 ADD and 254 MUL, all canonical Pallas field operations on 256-bit registers. It computes the same field element as the reference rounds 2-63 applied to A + (x + rho0) B, divided by OUTSCALE:
- Lane scaling. A lane may be held as its true value divided by a known nonzero constant lambda. An S-box then gives (true)^5 = lambda^5 (held)^5, and lambda^5 is folded into the constants of the next linear layer. A linear combination sum_j g_j z_j + c is held divided by g_0, which makes one coefficient 1: 2 MUL + 2 ADD (+ 1 ADD for a round constant) per lane instead of 3 MUL + 2 ADD (+ 1).
- Partial rounds. Lane 0 is held as lambda h0 + gamma and lanes 1, 2 as Q (h1, h2) + q, with lambda, gamma, the 2 x 2 matrix Q and q constants of the program. The basis of the hidden pair (h1, h2) is a free choice of the program: with s = (s1, s2) the true lanes 1, 2 after round 3, it holds h = Pm s for Pm = diag(nu) M22^r (M22 the lower 2 x 2 block of M, r = 24), where nu_a makes the coefficient of Z0 in h_a equal to 1. Each partial round multiplies Q by M22, so after the 24 partial rounds Q = M22^r Pm^-1 = diag(nu)^-1 is diagonal and the exit needs one ADD per lane. A partial round is then x5 = (h0 + kappa)^5, h0 := x5 + n1 h1 + n2 h2, h1 := h1 + w1 x5, h2 := h2 + w2 x5: 12 operations (1 ADD, 3 MUL for the S-box, 4 MUL, 4 ADD), with the five constants kappa, n1, n2, w1, w2 of that round; the linear layer of the round is absorbed into the next Q = M' Q (M' the lower 2 x 2 block of M), which is a constant. This is the sparse form of Grassi et al. with the lane scaling above.
- Counts: entry x + e_i (3 ADD, e_i = E0_i + rho0 set once per attempt); round 2: S-boxes 9 MUL, linear layer with the round-3 constants 6 MUL + 9 ADD; round 3: S-boxes 9 MUL, linear layer into the partial-round form 6 MUL + 6 ADD; 24 partial rounds, 12 each; round-60 S-box inputs from the partial-round form 1 ADD + 2 ADD (Q diagonal); rounds 60, 61, 62: 9 MUL + 6 MUL + 9 ADD each; round 63: S-boxes 9 MUL, output lane 0 only, 2 MUL + 2 ADD. Sum 3 + 24 + 21 + 12 * 24 + 3 + 72 + 13 = 424. An S-box x^5 is 3 MUL (square, square, multiply), as in C.
- Constants. `build_step` derives all 167 step constants from the deployed round constants and M, and asserts that every scale, every pivot and every Q is nonzero or invertible. OUTSCALE is the scale of the output lane.
- Checks. `--selftest`: the program equals digest(message(x + rho0)) / OUTSCALE of the reference rounds (`digest`) at 6 random (x, rho0); the program's `digest` equals the organizer's `verifier/poseidon.py` digest at r = 24 on 24 of 24 inputs, and F(x) * OUTSCALE equals the organizer digest of the 64-byte message message(x + rho0) at 8 of 8 random (x, rho0).

## 3. The program (Appendix B `rho.py`: `attack`, `search`, `plan`)

1. Setup: coins rho0, x_0 (two random words, two ANDs); the 167 step constants are loaded once into their registers (167 loads); e_i = E0_i + rho0 (3 ADD); the side array is zeroed.
2. Trail, in blocks of 8 unrolled steps (counter i = steps done before the block): for each slot k = 0..7: x := F(x) (the step program, x in place); if x mod 2^128 < T (T = 49780) x is a distinguished point (DP) with index i + k + 1: the table is scanned (Section 6); if x is already stored the trail has closed: go to 3; if the table already holds MCAP = 25553 DPs, halt (failure); otherwise store (x, index). After the block i := i + 8; after S steps, halt (failure).
3. Recovery. The repeat is x_b = x_a (b the current index, a its stored index), L = b - a. Let (s, x_s) be the entry stored just before a (the start x_0 at index 0 if none). Compute x_{s+L} from the nearest stored point at or before s + L (bisection on the stored indices, then at most gmax evaluations, else halt). If x_s = x_{s+L} halt (start on the cycle). Then iterate both from (x_s, x_{s+L}) in lockstep; the first time F(A) = F(B) return (A, B); after gmax rounds halt. The output is the two messages message(A + rho0) and message(B + rho0) (three fifth roots each, Section 6).

The attempt computes no exponential, root, division or parameter search: S and gmax are the integer literals STEPS and GMAXC of the program, loaded once into the registers BS and GM, and `tune.py` (run offline, never by the attempt; Section 6a) derives them in exact integer arithmetic; `plan` re-derives them and asserts that they are its S and gmax. The only work of the attempt is the step program, the table logic, the recovery and the messages of the ledger of Section 6.

Parameters (integers, `python3 rho.py --plan`, Appendix A): S = n + d = 169380592158660633169079816392825298528 (a multiple of 8), n = 169315647557130801213862401197337477120 (= 133566495 * 2^100, log2 126.9930), d = 64944601529831955217415195487821408, gmax = 135016408443598012162521064303628701, T = 49780, MCAP = 25553, KD = 9.5, H = 19.75, TAB = 12.

## 4. Correctness of the recovery (deterministic)

Let t be the least index with x_t = x_j for some j < t, mu = j, lambda = t - mu. For i >= mu, x_i = x_{i+lambda}. A repeated DP is found at b = a' + lambda where a' is the first DP with index at least mu: DPs with index in [t, a' + lambda) repeat values of x_mu .. x_{a'-1}, which hold no DP; so a = a' and L = lambda. The entry stored before a is a DP with index < mu or the start, so s < mu <= a, or s = 0 = mu (halt: start on the cycle). With s < mu, x_s != x_{s+L} and the least m >= 1 with x_{s+m} = x_{s+m+L} is m = mu - s <= a - s, so the lockstep stops within a - s rounds and returns (x_{mu-1}, x_{mu-1+L}): distinct, with equal F. All of s, a and q = s + L are below t. The recovery uses at most gmax + 2 gmax = 3 gmax evaluations when every gap between consecutive stored points below t is at most gmax. The table comparison is exact (high part and 16-bit low part, Section 7), so a lookup reports exactly the stored entries equal to x.

## 5. Success probability for a uniformly random function

In this section F is a uniformly random function on the N field elements (lazy sampling) and x_0 is any fixed element: every statement holds conditionally on the start. D = (2^126 + 1) T is the exact number of DPs in the field (p = 2^254 + c with c = p mod 2^128 >= T), theta = D / N = 2^-112.39672. Every index used below is at most S < SMAX = 2^128. Write theta_lo = (D - 2^128) / N and theta_hi = D / (N - 2^128).

Lemma 1. (i) Given x_0 .. x_i with no repeat, x_{i+1} is uniform on the field, so it repeats one of the i + 1 earlier values with probability (i + 1) / N. (ii) Given x_0, t and mu, the sequence x_1 .. x_{t-1} is uniform over all sequences of t - 1 distinct elements different from x_0: every such sequence together with the event x_t = x_mu has probability N^-t. (iii) Hence for 1 <= j < t, given x_0, t, mu and x_1 .. x_{j-1}, the value x_j is uniform over the N - j unused elements, of which D - k are DPs with k <= j; so theta_lo <= P(x_j is a DP | x_0, t, mu, x_1 .. x_{j-1}) <= theta_hi.

Proof of (iii): (D - k) / (N - j) >= (D - j) / N >= theta_lo and (D - k) / (N - j) <= D / (N - j) <= theta_hi, as j < 2^128. The bound conditions on every earlier value, including the DP status of earlier points, so it applies after a stored point as well.

Lemma 2. With n, d >= KD / theta_lo (d = ceil(KD / theta_lo) rounded up to a multiple of 8), gmax = ceil(H / theta_lo), S = n + d and MCAP, the attempt on a uniformly random function succeeds with probability at least 0.39 (n = 133566495 * 2^100).
(a) Trail: P(t > n) = prod_{i<n} (1 - (i + 1)/N) <= exp(-n (n + 1) / 2N) by (i). The start lies on the cycle (mu = 0) with probability at most 1/N at each step: n / N in all.
(b) Detection: given x_0, t <= n, mu and lambda >= d, the d values x_mu .. x_{mu+d-1} (all below t) contain no DP with probability at most (1 - theta_lo)^d <= exp(-theta_lo d) <= e^-KD, by (iii) in increasing order. A DP at a' among them gives b = a' + lambda <= t + d - 1 < S. P(lambda < d, t <= n) <= n d / N (at each t <= n and each lambda < d, x_t = x_{t-lambda} has probability at most 1/N).
(c) Table: the stored DPs lie below t (Section 4); by (iii) their number is dominated by Binomial(S, theta_hi), mean mu_S = S theta_hi = 24778.73 < MCAP + 1, so P(more than MCAP) <= exp(-mu_S) (e mu_S / (MCAP + 1))^(MCAP + 1) = e^-12.00 <= e^-TAB.
(d) Gaps: a stored point at position i < t followed by gmax positions below t with no DP has probability at most P(x_i is a DP) exp(-theta_lo gmax); summed over i, with the start: (S theta_hi + 1) e^-H. The factor exp(-theta_lo gmax) is taken after conditioning on x_i being a DP: by Lemma 1 (iii) each later x_j, given the whole history (k <= j DPs among the j used elements, x_0 included), is not a DP with probability exactly (N - j - D + k) / (N - j) = 1 - (D - k) / (N - j) <= 1 - (D - j) / N <= 1 - theta_lo. For one stored DP and j = 1 this is (N - D) / (N - 1), which is above 1 - D / N by (N - D) / (N (N - 1)) < 2^-253 and still below 1 - theta_lo, because theta_lo = (D - 2^128) / N removes 2^128 / N from theta. The chain rule over the gmax positions gives (1 - theta_lo)^gmax <= e^-H.
Total: success >= 1 - exp(-n (n + 1) / 2N) - n / N - eps, eps = e^-KD + n d / N + (S theta_hi + 1) e^-H + e^-TAB = 5.2644e-04. `plan` evaluates this in exact integer arithmetic (every term rounded in the safe direction; Section 6a): 0.39000000244948219830 >= 0.39; n is the least multiple of 2^100 that reaches 0.39. One attempt: no restart, no amplification, no advice.

## 6. Operation ledger (unit: target compressions; every operation 1/720)

Machine: the Pallas field RAM of `orchard-cost-v2.json` with 256-bit words and a declared file of 228 256-bit registers (counted in memory, Section 7). Arithmetic takes register operands. Prices: canonical field ADD and MUL 1/C each; every other primitive word operation (AND, OR, shift, compare, branch, register move, aligned 256-bit load or store, random word) 1/C. No reference permutation is called; every evaluation of F executes the 424 operations of `STEP`. The 167 step constants are loaded once per attempt into their registers (167 loads, charged); no field constant of STEP is an immediate operand (instructions carry only small offsets, shift counts and masks within their 36 bytes). Register names below: M128 (2^128 - 1), HI (2^256 - 2^128), TAB0 (table base: the start word, entry k at TAB0 + 32 k), SIDE (side array base), END (next free entry), BS (S), GM (gmax).

Trail, one block of 8 steps (424 + 3 per step, + 3 per block):
```
block: STEP                     ; 424 field operations, x := F(x) in place
       AND   u, x, M128
       CMPLT f, u, T
       BR    f, dp0             ; DP handler of slot 0, returns to next0
next0: STEP
       AND   u, x, M128
       CMPLT f, u, T
       BR    f, dp1
next1: STEP                     ; slots 2 to 6: the same 3 operations, BR f, dp2 .. dp6
next6: STEP                     ; slot 7: the same 3 operations, BR f, dp7
next7: ADD   i, i, 8
       CMPLT g, i, BS
       BR    g, block           ; else halt: steps
```
DP handler of slot k, 6 operations (W_DP) besides the scan and the insertion: ADD idx, i, k + 1; AND xh, x, HI; MOV p, TAB0 + 32 (scan start; u = x AND M128 is the low part); after a miss CMPLT c, cnt, MCAP; BR c (else halt: table); after the insertion BR nextk.
Table scan, per entry examined (W_SCAN = 19, worst case): LOAD v, [p]; AND v, v, HI; CMPEQ f, v, xh; BR f, low; ADD p, p, 32; CMPLT g, p, END; BR g, scan (7). At `low` (high parts equal): SUB o, p, TAB0 + 32; SHR wq, o, 9; SHL wq, wq, 5; ADD a, SIDE, wq; LOAD sw, [a]; AND sh, o, 480; SHR sh, sh, 1; SHR sw, sw, sh; AND sw, sw, 65535; CMPEQ f, sw, u; BR f, hit; BR next-entry (12).
Insertion (W_INS = 16, 14 executed): OR v, xh, idx; STORE [END], v; SUB o, END, TAB0 + 32; ADD END, END, 32; SHR wq, o, 9; SHL wq, wq, 5; ADD a, SIDE, wq; LOAD sw, [a]; AND sh, o, 480; SHR sh, sh, 1; SHL v, u, sh; OR sw, sw, v; STORE [a], sw; ADD cnt, cnt, 1.
Bisection probe (W_PROBE = 13, 12 executed): ADD m, lo, hi; ADD m, m, 1; SHR m, m, 1; SHL o, m, 5; ADD a, TAB0, o; LOAD v, [a]; AND v, v, M128; CMPLE f, v, q; BR f; MOV lo, m or SUB hi, m, 1; CMPLT g, lo, hi; BR g. At most 16 probes (entries 0 .. MCAP).
Recovery (W_REC = 6 per evaluation besides STEP): walk to x_q: STEP; ADD j, j, 1; CMPLT g, j, cnt; BR g (3); lockstep, per 2 evaluations: MOV x, A; STEP; MOV nA, x; MOV x, B; STEP; MOV nB, x; CMPEQ f, nA, nB; BR f, found; MOV A, nA; MOV B, nB; ADD j, j, 1; CMPLT g, j, GM; BR g (11, 5.5 per evaluation).
Messages: W = A + rho0; tau = W^INV5; U = U0 + a tau; V = V0 + b tau; m0 = U^INV5 - c_{0,0}; m1 = V^INV5 - c_{0,1}; the same for B. x^INV5 by square-and-multiply is 377 MUL (INV5 = 5^-1 mod (p - 1)); MSG_OPS = 2 (3 * 377 + 7) = 2,276.
Fixed part: at most MCAP + 1 DP events, each scanning at most MCAP entries and inserting once; at most 16 probes; MSG_OPS; 167 constant loads; 4 operations per side word for zeroing (1,598 words); MISC = 2000 for the coins, masks, bounds (the loads of STEPS and GMAXC into BS and GM), e_i, the reads of the two stored values, halts and report; these are straight-line instructions executed once (the set-up and halt/report listings of Section 7 total 25 + 14 = 39 instructions), so the 2000 charged is more than fifty times the count: OTHER_FIXED = (MCAP + 1)(6 + 19 MCAP + 16) + 16 * 13 + 2,276 + 167 + 4 * 1,598 + 2000 = 12,407,219,109 operations.

Total (every halt charged at its limit): T = [S (424 + 3) + (S / 8) 3 + 3 gmax (424 + 6) + OTHER_FIXED + PREP_OPS] / 720 = 72563201740699829536325138704034328194963 / 720 = 1.007822e38 units, log2 T = 126.244509; claimed 126.24451 (rounded up). Per trail step 427.375 operations against C = 720. `python3 rho.py --selftest` runs the search at width 14 with the real step program and checks that its counted operations stay below this formula for its parameters.

### 6a. Offline derivation of the constants and parameters: a finite charged bound

Everything the attempt loads or compares with is fixed before it starts, by four offline derivations: (i) INV5 = 5^-1 mod (p - 1); (ii) the line constants LINE_A, LINE_B, LINE_U0, LINE_V0 (`line`); (iii) the 167 step constants, E0 and OUTSCALE (`build_step`, which calls `message` at W = 0 and W = 1 and the reference rounds); (iv) the parameter literals T_DP, MCAP, KD, H, TAB, STEPS and GMAXC, printed by `python3 tune.py rho.py` (Appendix G). Each is the output of a finite procedure that depends only on the deployed constants of the target and the stated candidate ranges; no collision, message pair or search result is stored. Their storage and loading are charged in Sections 6 and 7; their construction is charged here, as `PREP_OPS` in the program and in the total of Section 6.

No source is left out. (iv) is the whole of `tune.py` (Appendix G, about 100 lines). It imports the program of Appendix B and calls only its functions `fixed_bytes`, `exp_consts`, `derive`, `table_exp`, `ledger` and the constants `Q_RANDOM`, `ONE`, `CNT`. It assembles no program text (an earlier version assembled candidate texts from a template; this one does not) and imports no other module of ours. The parameter lines of Appendix B are the lines `tune.py` prints, and `python3 tune.py rho.py` on the shipped `rho.py` prints them again together with the operation counts below. Besides the Python integers it uses `Fraction` for the literals KD and H and the standard module loader that reads Appendix B.

Exact arithmetic. There is no float, no Decimal and no transcendental library call in (i)-(iv); the only exponentials and logarithms are the two series below, in integer fixed point (a real number is an integer in units of 2^-256). Every quantity that bounds a failure probability is rounded up and every lower bound down, so each resulting inequality is rigorous; Lemma 2 needs only upper bounds on its failure terms.
- e^-x for a rational x >= 0 (`exp_neg_ub`): s = the sum of the first 101 terms x^k / k! of the series of e^x, each term floored in units of 2^-256 (100 iterations of 2 MUL, 1 floor DIV, 1 ADD on integers); s is at most e^x 2^256 because every term is positive, so (2^512 // s) + 1 is at least e^-x 2^256. The truncation costs less than a factor 1 + 2^-100 for x <= 20 (the largest argument is H = 20); the program needs only that the result is an upper bound.
- The success bound (`success_fp`): e^(-n (n + 1) / 2N), n / N, n d / N, ((n + d) theta_hi + 1) e^-H and the other terms of eps are formed as ceilings of integer quotients and the exponential above (6 MUL, 4 DIV, 16 ADD besides the exponential). It is the bound of Section 5 with every term rounded up.
- The budget (`least_k`): bisection on k in [2^26, 2^28] (n = k 2^100 between 2^126 and 2^128), at most 28 + 2 evaluations of the success bound. The bound is below the target at the lower end and reaches it at the upper end (both asserted); the returned k is one at which the bound reaches the target, which is all the claim needs, and the bound at k - 1 is below it when the bound is increasing in n there.
- The table bound (`table_exp`): ln P(more than MCAP DPs) <= -mu + a (1 + ln(mu / a)), a = MCAP + 1, mu = ceil(S theta_hi) < a (Section 5(c)); the bound is increasing in mu below a, so the rounded-up mu is safe. ln(mu / a) <= -(u + u^2/2 + ... + u^48/48) with u = 1 - ceil(mu / a) rounded down, because the dropped terms of the series of -ln(1 - u) are positive (48 iterations of 1 MUL, 1 DIV, 3 ADD).
- `tune.py`: MCAP is the largest table with (MCAP + 1) 32 + ceil((MCAP + 1) / 16) 32 + fixed bytes <= 2^20 (at most 64 trips). For each of the 25 pairs (KD, H) in {17/2, 35/4, 9, 37/4, 19/2} x {19, 77/4, 39/2, 79/4, 20}, with TAB = 12, T_DP is the largest value in [1000, 65535] whose table bound is at most -TAB (bisection, 16 probes; a probe is one `derive`, which includes one `least_k`, and one `table_exp`); the candidate with the least `ledger` (the total of Section 6 without PREP_OPS) is chosen. The choice among candidates affects only the ledger, never the validity of the bounds, and is charged anyway.

Prices. An integer operand is below 2^2048 (8 limbs of 256 bits; the largest operand seen in the runs is 527 bits, asserted below 2048). ADD, subtract, compare, shift: 8 word operations (one per limb). The product of two limbs (256 x 256 -> 512 bits): 64 word operations (nine exact field multiplications of 86-bit pieces, each below 2^172 < p, at 1 each, plus splitting, carries and accumulation); MUL of two operands: 8 x 8 limb products = 4,096. Floor DIV: schoolbook with at most 9 quotient limbs, each at most one multiplication of the divisor by a limb (8 limb products) plus the quotient estimate and the subtraction: at most 8,192. Each metered integer operation is charged 8 times (the operation and at most 7 loads, stores and loop operations around it). Field operations of `build_step` are metered by running its code on metered elements (`prep_count.py`, Appendix G), 8 word operations each, plus 2^16 for INV5 (extended Euclid on 254-bit integers). The integer operations are counted by the shipped code itself (`CNT` in Appendix B section 5, incremented where they occur); they are counts of the run, not caps: every loop of (iv) has a fixed trip count (series of 100 and 48 terms, bisections on fixed intervals).

| part | procedure and count | charged word operations |
|---|---|---|
| (i)-(iii) `build_step`, `line`, `message` | metered: 552 ADD, 1,131 MUL, 71 compares, 26,520 squarings and 8,247 multiplications inside the exponentiations (pow(x, e, p) = bit_length(e) - 1 squarings + popcount(e) - 1 multiplications) = 36,521 field operations; 8 each, plus 2^16 for INV5 | 357,704 |
| (iv) `python3 tune.py rho.py` | 1,763,920 integer ADD, 2,803,777 MUL, 1,424,950 DIV; 8 x (8 per ADD + 4,096 per MUL + 8,192 per DIV) | 185,372,578,816 |
| one run of `plan` (re-derivation and check of the literals) | 10,512 ADD, 17,501 MUL, 8,863 DIV, same prices | 1,154,991,104 |
| loading | reading and compiling the text of rho.py, the other module-level statements | 65,536 |
| total `PREP_OPS` | sum | 186,527,993,160 |

The report lines of `plan` (log2 of integers, decimal printing, the sensitivity table of Section 8) use Python floats only to print: no literal of the program and no charge is computed from them, and the claimed time_log2 is the ceiling at 5 decimals of log2(total / C), which exceeds it by more than 10^-9 (the float error is below 10^-12).

PREP_OPS = 186,527,993,160 word operations = 2^27.95 target-compressions after division by C = 720; it is the integer literal `PREP_OPS` of the program, added to the total of Section 6 and so inside time_log2, and declared as `preprocessing_log2` = 28 in claim.json. These are one quantity: it is not added a second time. It is a fraction 2^-98 of the total, so the claimed time is 126.244509 with or without it at the printed precision. `python3 -B prep_bound.py rho.py` (Appendix G) runs `tune.py` and `plan` and reproduces the table; the run that produced the parameters of Section 3 is that run.

Memory of the preprocessing. peak = max(preprocessing peak 290,272 bytes, search peak 1,048,568 bytes) = 1,048,568 bytes, the memory figure of Section 7: the derivations run one after the other, before the search, and the largest holds at most 9,071 words of 32 bytes: the program's step list and its compiled form (8 words per operation, 424 operations), the 167 constants, the text of rho.py twice (1,476 words each), 512 words of round constants and matrices, and 2,048 words of integer temporaries (at most 256 operands of 8 words) = 290,272 bytes.

## 7. Memory and the table

The table is one array of 32-byte entries: entry k >= 1 is the word (x AND HI) OR index, the high 126 bits of the DP value with its index (< 2^128) in the low half. The low half of a DP value is below T < 2^16 and is kept in a side array, 16 fields of 16 bits per word, field k - 1 for entry k. Word 0 is the start (its value is also held in register X0). Entries are in increasing index order, so the bisection runs on the array itself; a lookup compares the high part and then the low part, so it is exact. Nothing else is stored. `rho.py` keeps the same array (`tab`, `side`) and the same scan (`lookup`).
Bytes at the peak (the search phase; setup holds a subset): entries (MCAP + 1) * 32 = 817,728; side array 1,598 * 32 = 51,136; start word 32; code at most 4,630 instructions at 36 bytes = 166,680 (8 unrolled step copies and one recovery copy of STEP, 167 constant loads, at most 600 other instructions); constants in memory (step constants, E0, line constants, INV5, OUTSCALE) 5,696; register file 228 * 32 = 7,296. Total 1,048,568 <= 2^20 = 1,048,576: the memory term of the score is 0.

Layout on the 256-bit word machine. Every table item is one aligned 256-bit word: entry k at TAB0 + 32 k, side word w at SIDE + 32 w. There is no 48-byte record and no unaligned access; the extraction of an entry's low part from its side word is the listed offset, shifts and AND (the 12 operations at `low`, the 6 address and shift operations of the insertion), each charged 1/C. Entries plus side array: 817,728 + 51,136 = 868,864 bytes.

Code size. code_instr = 8 (|STEP| + 3) + 3 + (|STEP| + 20) + 167 + 600 = 4,630: eight unrolled trail steps of |STEP| = 424 operations plus the 3-operation test, the 3-operation block tail, one recovery copy of STEP plus 20 control instructions (walk loop 3, lockstep 11, walk-target set-up 6), and 167 constant loads. The 600 other instructions are itemised from the listings of Section 6: DP handlers 8 x 6 = 48; table scan 7 + 12 = 19; insertion 14; bisection loop 13 + 4 initialisation = 17; fifth-root loop 8 and two messages 2 x 7, with 8 call and return instructions = 30; set-up (2 coins, 3 e_i additions, 14 register initialisations, 6-instruction zeroing loop) = 25; halt exits 6 and report 8 = 14; handler returns 8 and loop back-edges 3 = 11. The sum is 178; 600 is charged.

## 8. Premise H1 and its evidence

H1 (claim.json `H1-random-function-model`), the only premise of the claim.
- Statement: the filed trail has n = 133566495 * 2^100 steps, at which Lemma 2 gives 0.390000002 for a uniformly random function (the least multiple of 2^100 that reaches 0.39). Premise: for the attempt's coins rho0 and x_0 (uniform 254-bit words), the search of Section 3 on the real map F(x) = digest(message(x + rho0)) / OUTSCALE, at the budget n, succeeds with probability at least 0.39. H1 is our theory that, for this search, the fixed map behaves like a uniformly random function.
- Role: score-critical. It is the only step from Lemma 2 to the claimed success probability; the step program (Section 2), the recovery (Section 4), the ledger (Section 6) and the memory (Section 7) are proved or checked exactly.
- Scope: target poseidon-orchard-r24-prefix-v1, inputs on the line of Section 1, one trail with the parameters of Section 3 (S = 1.694e38 evaluations). Applies to this round count and budget.
- Evidence scope: outputs truncated to 16 to 40 bits, trails of at most 2,970,429 steps, r = 7, 23 and 56 partial rounds; H1 applies the measured law to this row (r = 24) at 254 bits over 2^127 steps.

Evidence: measurements of the real map family with our own code (Appendix D, linked with our C field library). The measured map is the walk map of this construction: the state after round 1 is A + (v + rho) B, then the reference rounds 2-63 at r partial rounds, the output divided by OUTSCALE_r; `lmeas kat` equals the row program's F on 18 of 18 random (x, rho0) at r = 7, 23, 56. These measurements were run by the participant (the organizer-run experiment is Section 9). The organizer's digest code, run by us, confirms all 14,879 of the 14,879 pairs the runs returned: distinct messages message(A + rho), message(B + rho) whose digests divided by OUTSCALE_r agree in the low w bits. 39 minutes in all. The measurements are evidence for H1 only: no parameter of the attempt is taken from them.
- Map at width w: F_w(v) = low w bits of F(v) with rho, v in [0, 2^w). Each trial draws its own rho (a 254-bit word from the function index) and start, as the attempt draws rho0 and x_0. The walk runs until its first repeat, with every value kept, giving the exact t (first repeat), mu and lambda of Section 4.
- Collision rate: for a function whose collision hazard is c times that of a uniformly random function on N = 2^w points, the first-repeat index t has the exact discrete law P(t > n) = prod_{i<=n} (1 - c i / N) and P(t = n) = P(t > n - 1) c n / N (c = 1: a random function). The hazard multiplier c is estimated by maximum likelihood on this exact law (pooled estimates maximise the sum of the log-likelihoods over the cells pooled); the 95% interval is the profile-likelihood interval 2 (l(c_hat) - l(c)) <= 3.84, which is asymptotic in the number of walks K and not in N. No exponential or Gamma approximation of t^2 / 2N is used. Coverage was checked by simulating walks from the exact law at the K and w of each cell, at c = 1 and c = 0.6 (`analyze_route2.py`, Appendix G; 400 repetitions per row, standard error 0.011): the nominal 95% interval covered the true c in 0.932 to 0.980 of the repetitions for w = 16 to 40 (K = 2000 down to 12), and in 0.930 for the pooled K = 6,872 of one round count (100 repetitions, standard error 0.025). Against the exponential approximation of our earlier analysis the estimate moves by at most 0.0025 in c_hat and 0.034 in an interval end (largest in the w = 40 cells with 12 walks); the table below is the exact-law one.
- Distinguished points at density theta = 2^10 / 2^(w/2) (1/16 at w = 16, 20): theta times the mean gap between consecutive DPs (1 for a random function).
- The full search (`search` of Section 3, with Lemma 2 parameters computed by the same formula for N = 2^w, D = 2^(w/2+10), SMAX = 2^(w/2+3), at widths 24 to 40): the fraction of runs that return a verified pair, against the Lemma 2 bound for that width.
- Control: the same program on a keyed pseudo-random function (splitmix64), five times as many trials per width.
- Counts. The organizer digest confirmed all 14,879 pairs returned by all runs; the success counts of the table are only the full search at the Lemma 2 parameters at widths 24 to 40 (3,463/8,616 = 0.402 runs). Of the 14,879 pairs, 3,463 come from those runs (one per success) and 11,416 from the runs at widths 16 and 20 (3 round counts x 4,000 walks), which run the same search with relaxed parameters (T = 2^(h-4), S = 2^(h+2), table 100,000, gmax 2^12), whose pairs were verified but are not successes of the table: 14,879 = 3,463 + 11,416. Appendix F lists every job.
- Seeds, invocations, stopping rule, raw output. Each job is one invocation `lmeas family 0 r w T h S mcap gmax K seedbase`; the parameters per width and the per-job records (K, seedbase, found, sum of t, sum of evaluations, SHA-256 prefix of the raw file) are in Appendix F. Trial k of a job uses the function index j = seedbase * 1000003 + k (rho from four splitmix64 words of j, the control key from j) and the start splitmix64(j) mod 2^w; seedbase = 300000 + 1000 r + 10 w + chunk (+5 for the control). K per job was fixed in advance by the job list; there is no stopping rule: every job ran its K trials and every walk ran to its first repeat (no walk reached the cap of 12 sqrt(N)); no walk was dropped, repeated or selected, and all 108 jobs enter every figure. One JSON line per trial (fam, fn, r, w, seedbase, k, v0, t, mu, lambda, cens, ndp, ngap, sgap, maxgap, aprime, status, evals, rec, A, B, pair_ok) is kept by the participant in 108 raw files of 14 MB, which do not fit the evidence budget; the SHA-256 over the concatenated per-file digests is 9f1406161facbdc83921532ae4cc47d56dc14346ec3711e526988e432725a548. Measurement operation counts: the walks of the three line ladders evaluate 240,328,298 map values in all, their searches 167,341,473 further evaluations, and the control ladder 394,293,160 and 277,877,879.

| r | w | trials | c [95%] | control c [95%] | success (found/K, [95%]) | Lemma 2 bound | theta x mean DP gap | largest DP gap / gmax |
|---|---|---|---|---|---|---|---|---|
| 7 | 16 | 2000 | 0.998 [0.955, 1.043] | 0.995 [0.976, 1.014] | - | - | 0.949 | - |
| 7 | 20 | 2000 | 1.009 [0.966, 1.054] | 1.003 [0.983, 1.023] | - | - | 0.986 | - |
| 7 | 24 | 2000 | 1.038 [0.993, 1.084] | 0.998 [0.979, 1.018] | 0.412 (825/2000, [0.391, 0.434]) | 0.3900 | 0.999 | 54 / 73 |
| 7 | 28 | 600 | 1.013 [0.934, 1.096] | 1.010 [0.974, 1.047] | 0.422 (253/600, [0.383, 0.462]) | 0.3900 | 0.997 | 230 / 291 |
| 7 | 32 | 200 | 0.921 [0.799, 1.055] | 1.006 [0.945, 1.070] | 0.315 (63/200, [0.255, 0.382]) | 0.3900 | 1.001 | 780 / 1162 |
| 7 | 36 | 60 | 1.081 [0.830, 1.378] | 1.057 [0.942, 1.181] | 0.367 (22/60, [0.256, 0.493]) | 0.3900 | 1.004 | 3686 / 4645 |
| 7 | 40 | 12 | 0.861 [0.461, 1.444] | 0.884 [0.678, 1.127] | 0.250 (3/12, [0.089, 0.532]) | 0.3900 | 0.996 | 11571 / 18578 |
| 23 | 16 | 2000 | 0.993 [0.950, 1.037] | (as above) | - | - | 0.962 | - |
| 23 | 20 | 2000 | 1.016 [0.972, 1.061] | (as above) | - | - | 0.986 | - |
| 23 | 24 | 2000 | 0.976 [0.934, 1.020] | (as above) | 0.403 (805/2000, [0.381, 0.424]) | 0.3900 | 0.999 | 64 / 73 |
| 23 | 28 | 600 | 0.934 [0.861, 1.010] | (as above) | 0.392 (235/600, [0.353, 0.431]) | 0.3900 | 1.000 | 241 / 291 |
| 23 | 32 | 200 | 1.015 [0.881, 1.163] | (as above) | 0.385 (77/200, [0.320, 0.454]) | 0.3900 | 0.999 | 910 / 1162 |
| 23 | 36 | 60 | 0.924 [0.710, 1.178] | (as above) | 0.417 (25/60, [0.301, 0.543]) | 0.3900 | 0.998 | 2929 / 4645 |
| 23 | 40 | 12 | 0.908 [0.486, 1.524] | (as above) | 0.417 (5/12, [0.193, 0.680]) | 0.3900 | 1.006 | 9245 / 18578 |
| 56 | 16 | 2000 | 1.021 [0.977, 1.066] | (as above) | - | - | 0.959 | - |
| 56 | 20 | 2000 | 0.981 [0.939, 1.025] | (as above) | - | - | 0.987 | - |
| 56 | 24 | 2000 | 0.997 [0.954, 1.042] | (as above) | 0.397 (793/2000, [0.375, 0.418]) | 0.3900 | 1.000 | 58 / 73 |
| 56 | 28 | 600 | 1.038 [0.958, 1.124] | (as above) | 0.412 (247/600, [0.373, 0.452]) | 0.3900 | 0.998 | 279 / 291 |
| 56 | 32 | 200 | 1.039 [0.901, 1.190] | (as above) | 0.425 (85/200, [0.358, 0.494]) | 0.3900 | 1.000 | 829 / 1162 |
| 56 | 36 | 60 | 0.900 [0.691, 1.148] | (as above) | 0.367 (22/60, [0.256, 0.493]) | 0.3900 | 1.005 | 2945 / 4645 |
| 56 | 40 | 12 | 0.779 [0.417, 1.307] | (as above) | 0.250 (3/12, [0.089, 0.532]) | 0.3900 | 0.997 | 12026 / 18578 |

Result: in 21 of 21 of the run-and-width cells the 95% interval of the hazard multiplier contains 1. Pooled over 20,616 walks it is 1.001, 95% interval [0.987, 1.015]. The weighted slope of log c against width is -0.0011 per bit (standard error 0.0015). The search succeeded in 3,463/8,616 = 0.402 of its runs at widths 24 to 40, against a mean Lemma 2 bound of 0.3900. DP gaps follow the geometric law the lemma uses (theta x mean gap 0.996 to 1.006 at widths 24 to 40), and no gap reached gmax.
Extrapolation: from widths 16 to 40 and r = 7, 23, 56, where c is measured, to width 254 at r = 24, by H1. The measurements show the rate law that Lemma 2 uses on the real round function.
Sensitivity: if the real map has the collision rate of a random function times a factor c, the search succeeds with probability about 1 - exp(-c x) - n / N - eps, with x = n (n + 1) / 2N = 0.49516 and n / N + eps = 0.00053. c = 1 gives the 0.39 of the premise. The measured interval is c in [0.987, 1.015].

| collision-rate factor c | 1 | 0.9 | 0.75 | 0.6 | 0.5 | 0.4 |
|---|---|---|---|---|---|---|
| success probability | 0.390 | 0.359 | 0.310 | 0.257 | 0.219 | 0.179 |
The attempt draws rho0 as a coin, so its success probability is an average over the maps x -> F(x) with different rho0, which is what Lemma 2 bounds; on one fixed map the success over starts alone depends on that map's longest cycle.

## 9. Experiments

One organizer-run experiment is declared (`experiments/manifest.json`, id `lowbits-birthday`, kind `python-message-pairs-v1`, event `digest-xor-mask`; program `experiments/exp_lowbits.py`, 15,748 bytes, standard library only). Per organizer trial the program derives 1200 candidate inputs (pairs of canonical field elements) from the trial seed with SHAKE-256, evaluates the target digest with its own copy of the reference permutation at the round count taken from the target profile name, and returns the first two distinct inputs whose digests agree in the first 14 bits of the big-endian reading of the 32-byte digest (mask `fffc` followed by zeros, expected zero). The organizer recomputes both digests with the target's verifier and checks the event; it runs the program twice and compares the outputs byte for byte, under its limits (20 s, 128 MiB, 1 CPU, sources at most 64 KiB). Our local run of the same manifest events with the organizer's digest code: 256 of 256 trials return a verified pair at r = 7 (3.2 s), r = 23 (5.9 s) and r = 56 (10.3 s), and the two runs are byte-identical; no full collision occurs and none is claimed.

How the reduced event supports H1 (regime, extrapolation, scope, sensitivity).
- Regime. The event is observed on this target's own digest at r = 24 partial rounds, on fresh random inputs, at 14 output bits, with at most 1200 evaluations per trial; a random function reaches a 14-bit match after about 160 evaluations on average, so a trial that returns a pair is the event H1 is about (a collision), run by the organizer on the real round function.
- Extrapolation. H1 concerns the walk map F(x) = digest(message(x + rho0)) / OUTSCALE at 254 bits over 2^127 steps. The experiment is an organizer-executed check that the r-round digest collides at the random-function rate in its leading bits. The participant measurements of Section 8 carry the same law to widths 16 to 40 on the line inputs and the scaled map, and H1 applies it to F at full width.
- Scope. One width (14 bits), this round count, 256 trials.
- Sensitivity. If the 14-bit collision rate of the digest were c times the random-function rate, a trial would need more than 1200 evaluations with probability exp(-1200^2 c / (2 * 2^14)) = exp(-43.95 c); the probability that all 256 trials succeed is (1 - exp(-43.95 c))^256, which is at least 0.99 only for c >= 0.23. The experiment detects a collision-rate deficit of a factor of about four or more at 14 bits; H1 is the case c = 1 (Section 8).

## Appendix A: `python3 rho.py --plan`

partial_rounds 24; C 720; step_field_ops 424; step_add 170; step_mul 254; W_LOOP 3; W_BLOCK 3; W_REC 6; ops_per_trail_step 427.375; T_DP 49780; MCAP 25553; KD 19/2; H 79/4; TAB 12; theta_log2 -112.3967213901316; n 169315647557130801213862401197337477120; n_over_2^100 133566495; n_log2 126.99298291392029; d 64944601529831955217415195487821408; gmax 135016408443598012162521064303628701; steps 169380592158660633169079816392825298528; eps_total 0.0005264354095366106; success_lower_bound 0.3900000024494822; success_lower_bound_decimal 0.39000000244948219830; slack {'n0': 169315647557130801213862401197337477120, 'n_over_n0': 1.0, 'slack_bits': 0.0, 'x': 0.4951597073084298, 'rate_min': 1.0, 'rate_table': {'1.0': 0.3900000024494822, '0.9': 0.3590616778351602, '0.75': 0.3096847406408544, '0.6': 0.25650075055275673, '0.5': 0.21878568704849644, '0.4': 0.1791561174031565}}; mean_stored_bound 24778.732891608135; ln_P_table_overflow -12.003579692996102; other_fixed 12407219109; prep_ops 186527993160; prep_log2_units 27.948748106397233; total_ops 72563201740699829536325138704034328194963; T_units 1.0078222463986087e+38; time_log2 126.24450881315587; constants 167; memory table_entries 817728, side_array 51136, start_word 32, code_instructions 4630, code 166680, constants 5696, registers 228, register_file 7296, total 1048568

## Appendix B: the program and its ledger, `rho.py` (verbatim, standard library only; `--plan` prints the parameters and the ledger)

```python
"""Generic collision search on the Orchard hash with 24 partial rounds, the permutation evaluated in an equivalent form whose every
field operation is charged: one trail of x -> F(x) = digest(message(x + rho0)) / OUTSCALE for a random rho0, distinguished points, one table.

Target: poseidon-orchard-r24-prefix-v1 (initial state [m0, m1, 2^65], 8 full + 24 partial rounds, digest = state[0], no feed-forward).
Sections: 1 deployed constants (halo2_poseidon 0.2.0, copied from our own checked file), 2 the hash (reference form), 3 the input line and the
step program (`line`, `build_step`), 4 the search (`search`), 5 parameters and ledger (`plan`, `python3 rho.py --plan`), 6 self-checks
(`--selftest`) and command line (`--listing` prints the step program). No outside code or library is used; standard library only.
"""
import sys
import json
import hashlib
from math import log2
from fractions import Fraction

PARTIAL = 24
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
        kval[name] = v % P
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
    for i in range(3):
        op("ADD", Y[i], "x", "e%d" % i)
    sig = [pow(B[i], 5, P) for i in range(3)]
    for i in range(3):
        pow5(Z[i], Y[i])
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
OUTINV = inv(OUTSCALE)
NCONST = len(KVAL)                        # step constants, each loaded once per attempt into its own register
REGNAMES = sorted({r for o in STEP for r in o[1:]})
NREG_STEP = len(REGNAMES)                 # registers the step uses: constants, e0..e2, x and working registers
NREG = NREG_STEP + 40                     # + at most 40 control registers of the search (proof.md Section 6 listings): the declared file
_IDX = {r: n for n, r in enumerate(REGNAMES)}
_CODE = tuple((o == "MUL", _IDX[d], _IDX[s], _IDX[t]) for o, d, s, t in STEP)


def make_F(rho0):
    """F(x) = digest(message(x + rho0)) / OUTSCALE, computed by executing the step program (every operation of STEP once)."""
    R = [0] * NREG_STEP
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


# ================================================================ 4 the search: one trail, distinguished points, one table, recovery
M128 = (1 << 128) - 1
HI = ((1 << 256) - 1) ^ M128
UNROLL = 8                                # trail steps per block
# Operation charges (word operations, 1/C each), beside the |STEP| field operations of every evaluation (proof.md Section 5 listings):
W_LOOP = 3        # per trail step, after the step program: AND with the 128-bit mask, compare with T, branch to the DP handler
W_BLOCK = 3       # per block of 8 unrolled steps: counter add 8, compare with S, branch
W_DP = 6          # per distinguished-point event: index = counter + slot, high part = x AND HI, scan pointer, capacity compare and branch, return branch
W_SCAN = 19       # per table entry examined, worst case: load, AND HI, compare, branch, pointer add, bound compare, branch (7); on a high-part
                  # match also the side field: offset, two shifts, address add, load, AND, shift, shift, AND 16 bits, compare, two branches (12)
W_INS = 16        # per insertion: entry word, store, offset, end-pointer add; side word read-modify-write (6 address/shift, load, shift, OR, store); count (14)
W_PROBE = 13      # per bisection probe: lo+hi, +1, shift, shift 5, base add, load, AND M128, compare, branch, bound update, loop compare, branch, slack
W_REC = 6         # per recovery evaluation beside the step: walk loop 3 (counter, compare, branch); lockstep 11 per 2 evaluations
                  # (move A into x, move result out, the same for B, compare, branch, two moves, counter, compare, branch)
POW_OPS = (INV5.bit_length() - 1) + (bin(INV5).count("1") - 1)   # square-and-multiply for x^INV5: squarings + multiplications
MSG_OPS = 2 * (3 * POW_OPS + 7)           # the two messages: W = A + rho0, tau = W^(1/5), U, V (2 MUL, 2 ADD), two roots, two subtractions


def lookup(tab, side, x, ops):
    """Linear scan of the entries 1.. for the value x (a distinguished point: x mod 2^128 < T < 2^16): returns k or None."""
    xh, xl = x & HI, x & M128
    for k in range(1, len(tab)):
        ops["table"] += 7
        if tab[k] & HI == xh:
            ops["table"] += 12
            if (side[(k - 1) >> 4] >> (16 * ((k - 1) & 15))) & 0xFFFF == xl:
                return k
    return None


def insert(tab, side, x, i, ops):
    ops["table"] += W_INS
    k = len(tab)
    tab.append((x & HI) | i)
    if (k - 1) & 15 == 0:
        side.append(0)
    side[(k - 1) >> 4] |= (x & M128) << (16 * ((k - 1) & 15))


def search(F, is_dp, x0, steps, mcap, gmax):
    """Single-trail collision search on the map F: x_0 = x0, x_i = F(x_{i-1}), 8 steps per block.  Every x_i (i >= 1) with is_dp(x_i) is
    stored as one entry word (x AND HI) OR i and a 16-bit side field x mod 2^128; the start x_0 is kept in its own word.  Halts (failure)
    after `steps` evaluations (a multiple of 8), when the table already holds `mcap` points at a new one, or when the recovery needs a gap
    longer than gmax.  When a distinguished value repeats (x_b = x_a, a < b) the trail is periodic from a with period L = b - a; the
    recovery finds the least i with x_i = x_{i+L} and returns (x_{i-1}, x_{i+L-1}), distinct, with F equal on both.
    Returns (pair or None, status, evaluations, ops)."""
    ops = {"trail": 0, "blocks": 0, "rec": 0, "dp": 0, "table": 0, "probe": 0}
    tab, side = [None], []

    def value(k):
        return x0 if k == 0 else (tab[k] & HI) | ((side[(k - 1) >> 4] >> (16 * ((k - 1) & 15))) & 0xFFFF)

    def index(k):
        return 0 if k == 0 else tab[k] & M128
    x, i, k, b = x0, 0, None, None
    while i < steps and k is None:
        for slot in range(UNROLL):
            x = F(x)
            ops["trail"] += 1
            if is_dp(x):
                ops["dp"] += W_DP
                k = lookup(tab, side, x, ops)
                if k is not None:
                    b = i + slot + 1
                    break
                if len(tab) - 1 >= mcap:
                    return None, "table", ops["trail"], ops
                insert(tab, side, x, i + slot + 1, ops)
        if k is None:
            i += UNROLL
            ops["blocks"] += 1
    ev = ops["trail"]
    if k is None:
        return None, "steps", ev, ops
    a = index(k)
    L = b - a
    s, A = index(k - 1), value(k - 1)       # last stored point before a (index s < mu <= a), or the start
    q = s + L
    lo, hi = 0, len(tab) - 1                # nearest stored point at or before q, then walk to x_q
    while lo < hi:
        mid = (lo + hi + 1) // 2
        ops["probe"] += W_PROBE
        if index(mid) <= q:
            lo = mid
        else:
            hi = mid - 1
    idx, B = index(lo), value(lo)
    if q - idx > gmax:
        return None, "gap", ev, ops
    for _ in range(q - idx):
        B = F(B)
        ev += 1
        ops["rec"] += 1
    if A == B:
        return None, "start-on-cycle", ev, ops
    for _ in range(gmax):                   # lockstep: the first index where the two walkers meet
        nA, nB = F(A), F(B)
        ev += 2
        ops["rec"] += 2
        if nA == nB:
            return (A, B), "found", ev, ops
        A, B = nA, nB
    return None, "gap", ev, ops


# ================================================================ 5 the claim's parameters and ledger (derive, plan)
T_DP = 49780                             # a value x is a distinguished point iff (x mod 2^128) < T_DP (T_DP < 2^16: the side field)
MCAP = 25553                             # table capacity in distinguished points
KD = Fraction(19, 2)                    # detection window d = ceil(KD / theta_lo), rounded up to a multiple of 8
H = Fraction(79, 4)                     # gap cap gmax = ceil(H / theta_lo)
TAB = 12                                 # table overflow probability <= e^-TAB
STEPS = 169380592158660633169079816392825298528                 # S = n + d, the trail length of the attempt: an integer literal, derived offline by `plan` (which asserts it)
GMAXC = 135016408443598012162521064303628701                 # gmax, the gap cap: an integer literal, derived offline by `plan` (which asserts it)
PREP_OPS = 186527993160                 # charged bound (word operations) of the offline derivation of the constants and parameters: proof.md Section 6a
SMAX = 1 << 128                           # every index of the program is below SMAX (S < 2^128; the index field has 128 bits)
GRAIN = 1 << 100                          # n is the least multiple of 2^100 that reaches the success bound
Q_CLAIM = Fraction(39, 100)               # the claimed success probability on the real map (premise H1)
Q_RANDOM = Q_CLAIM                        # the proven success bound on a uniformly random function at the filed budget: the budget is the random-function budget
MISC = 2000                               # coins, masks, bounds, e_i = E0_i + rho0, halts, counters' setup and the report
CODE_OTHER = 600                          # instructions outside the step copies: handlers, scan, insertion, bisection, recovery control, roots, setup loop

# Exact offline arithmetic (integers only: no float, no Decimal, no library function).  A real number v is held as an integer in units of
# 2^-FB (FB = 256).  Every number named below as an upper bound is rounded up, every lower bound down, so each derived inequality is rigorous.
# CNT meters the integer operations (add: add, subtract, compare, shift of an operand below 2^2048; mul; div: floor division) and the largest
# operand seen; `python3 tune.py rho.py` prices them (proof.md Section 6a).
FB = 256
ONE = 1 << FB
KEXP = 100                                # terms of the exponential series
KLN = 48                                  # terms of the logarithm series
CNT = {"add": 0, "mul": 0, "div": 0, "bits": 0}


def dp_count(T):
    """Exact count over the field: p = 2^254 + c with c = p mod 2^128 >= T, so exactly (2^126 + 1) * T of the p field elements are distinguished."""
    return ((1 << 126) + 1) * T


def side_words(m):
    return (m + 1 + 15) // 16             # side array words (16 fields of 16 bits each), zeroed at setup: 4 operations per word


def probes(m):
    return m.bit_length() + 1             # bisection probes over at most m + 1 entries


def other_fixed(m):
    """Table scan, insertion, bisection, constant loads, the message roots, side-array zeroing and MISC, for a table of m entries."""
    return (m + 1) * (W_DP + W_SCAN * m + W_INS) + probes(m) * W_PROBE + MSG_OPS + NCONST + 4 * side_words(m) + MISC


PROBES, SIDE_WORDS, OTHER_FIXED = probes(MCAP), side_words(MCAP), other_fixed(MCAP)


def ledger_ops(ops, nstep):
    """Word and field operations of a run, from its counters (nstep = |STEP|)."""
    return ((nstep + W_LOOP) * ops["trail"] + W_BLOCK * ops["blocks"] + (nstep + W_REC) * ops["rec"] + ops["dp"] + ops["table"] + ops["probe"])


def ledger(S, gmax, m):
    """The worst-case total (word operations) of the attempt without the preprocessing term: every halt charged at its limit."""
    return S * (len(STEP) + W_LOOP) + (S // UNROLL) * W_BLOCK + 3 * gmax * (len(STEP) + W_REC) + other_fixed(m)


def fixed_bytes():
    """Bytes of the peak that do not depend on the table size: start word, code, constants, register file."""
    code_instr = UNROLL * (len(STEP) + W_LOOP) + W_BLOCK + (len(STEP) + 20) + NCONST + CODE_OTHER
    return 32 + code_instr * 36 + (NCONST + 3 + 8) * 32 + NREG * 32


def memory(m=MCAP):
    """Bytes at the peak (the search; the only other phase, setup, holds a subset): every item is a 32-byte word unless stated."""
    entries, sidew = (m + 1) * 32, side_words(m) * 32
    code_instr = UNROLL * (len(STEP) + W_LOOP) + W_BLOCK + (len(STEP) + 20) + NCONST + CODE_OTHER
    consts = (NCONST + 3 + 8) * 32         # step constants, E0, line constants (U0, V0, a, b, c00, c01), INV5, OUTSCALE
    total = entries + sidew + fixed_bytes()
    return {"table_entries": entries, "side_array": sidew, "start_word": 32, "code_instructions": code_instr, "code": code_instr * 36,
            "constants": consts, "registers": NREG, "register_file": NREG * 32, "total": total}


def exp_neg_ub(xn, xd):
    """Upper bound, in units of 2^-FB, on e^-(xn/xd) for xn/xd >= 0: 1/s with s the floored sum of the first KEXP + 1 terms of the series of e^x,
    a lower bound on e^x (all terms are positive).  Counts: 2 KEXP mul, KEXP + 1 div, KEXP + 2 add."""
    term, s, mx = ONE, ONE, 0
    for k in range(1, KEXP + 1):
        t = term * xn
        mx = max(mx, t.bit_length())
        term = t // (xd * k)
        s += term
    CNT["mul"] += 2 * KEXP
    CNT["div"] += KEXP + 1
    CNT["add"] += KEXP + 2
    CNT["bits"] = max(CNT["bits"], mx)
    return (ONE * ONE) // s + 1


def exp_consts(KD, H, TAB):
    """(e^-KD, e^-H, e^-TAB) as upper bounds."""
    return exp_neg_ub(KD.numerator, KD.denominator), exp_neg_ub(H.numerator, H.denominator), exp_neg_ub(TAB, 1)


def success_fp(n, d, T, ek, c=Fraction(1)):
    """Lower bound (units 2^-FB) on P_F(success) for budget n and detection window d (proof.md Section 5, Lemma 2):
    1 - e^(-c n (n + 1) / 2N) - n / N - eps, eps = e^-KD + n d / N + ((n + d) theta_hi + 1) e^-H + e^-TAB, N = p, theta_hi = D / (N - 2^128);
    c = 1 is the random function, other c the sensitivity of Section 8.  Every term of the subtraction is an upper bound.  Returns (bound, eps)."""
    e_kd, e_h, e_tab = ek
    en = exp_neg_ub(c.numerator * n * (n + 1), c.denominator * 2 * P)
    nN = (n * ONE + P - 1) // P                                                   # ceil(n / N)
    ndN = (n * d * ONE + P - 1) // P                                              # ceil(n d / N)
    m_up = ((n + d) * dp_count(T) * ONE + (P - SMAX) - 1) // (P - SMAX)          # ceil((n + d) theta_hi)
    t3 = ((m_up + ONE) * e_h + ONE - 1) >> FB                                     # ceil(((n + d) theta_hi + 1) e^-H)
    eps = e_kd + ndN + t3 + e_tab
    CNT["mul"] += 6
    CNT["div"] += 4
    CNT["add"] += 16
    CNT["bits"] = max(CNT["bits"], (n * d * ONE).bit_length(), ((n + d) * dp_count(T) * ONE).bit_length(), ((m_up + ONE) * e_h).bit_length())
    return ONE - en - nN - eps, eps


def least_k(q, d, T, ek):
    """The least k (n = k 2^100) whose success bound reaches q, by bisection on [2^26, 2^28] (n between 2^126 and 2^128; the bound is below q at the
    lower end and at least q at the upper end, both asserted; the claim needs only that the bound at the returned k reaches q).  At most 30 evaluations."""
    ok = lambda k: success_fp(k * GRAIN, d, T, ek)[0] * q.denominator >= q.numerator * ONE
    lo, hi = 1 << 26, 1 << 28
    assert not ok(lo) and ok(hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
    CNT["add"] += 8 * 30
    CNT["mul"] += 2 * 30                  # the comparison of each evaluation with q: two products
    return hi


def table_exp(S, T, m):
    """Upper bound (units 2^-FB) on ln P(more than m of the stored DPs), by the Chernoff bound of Section 5(c):
    f(mu) = -mu + a (1 + ln(mu / a)), a = m + 1, mu = ceil(S theta_hi) < a, increasing in mu below a; ln(mu / a) <= -(u + u^2/2 + ... + u^KLN / KLN),
    u = 1 - ceil(mu / a) rounded down, since the dropped terms are positive.  Returns (f, mu); f is None if mu >= a."""
    a = m + 1
    mu = (S * dp_count(T) * ONE + (P - SMAX) - 1) // (P - SMAX)
    CNT["mul"] += 1
    CNT["div"] += 1
    CNT["add"] += 4
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


def derive(T, m, KD, H, TAB, q=Q_RANDOM, ek=None):
    """The offline derivation of the trail length S = n + d and the gap cap gmax from T_DP = T and the table size m (integers only)."""
    D = dp_count(T)
    d = -(-(KD.numerator * P) // (KD.denominator * (D - SMAX)))
    d = -(-d // UNROLL) * UNROLL          # a multiple of 8 (S = n + d is a whole number of blocks)
    gmax = -(-(H.numerator * P) // (H.denominator * (D - SMAX)))
    ek = ek or exp_consts(KD, H, TAB)
    n = least_k(q, d, T, ek) * GRAIN
    CNT["mul"] += 4
    CNT["div"] += 4
    CNT["add"] += 12
    return {"d": d, "gmax": gmax, "n": n, "S": n + d, "ek": ek}


def plan():
    """Offline: re-derives and asserts the literals (STEPS, GMAXC, T_DP < 2^16, the table bound, the memory), then prints the ledger.  Everything
    that fixes a literal or a charge is exact integer arithmetic above; the floats below only format the report (log2 of integers, decimal
    printing) and no literal of the program is computed from them."""
    ek = exp_consts(KD, H, TAB)
    r = derive(T_DP, MCAP, KD, H, TAB, Q_RANDOM, ek)
    d, gmax, n, steps = r["d"], r["gmax"], r["n"], r["S"]
    k0 = least_k(Q_CLAIM, d, T_DP, ek)    # the budget at which the random-function bound is 0.39
    n0, k = k0 * GRAIN, n // GRAIN
    succ, eps = success_fp(n, d, T_DP, ek)
    assert succ * Q_RANDOM.denominator >= Q_RANDOM.numerator * ONE
    D_DP = dp_count(T_DP)
    x = n * (n + 1) / (2 * P)             # exponent of the random-function law: P(no repeat in n steps) = e^-x
    lo, hi = 1, 1 << 14                   # the least collision-rate factor c = j / 2^14 at which the bound reaches 0.39 (14 evaluations)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if success_fp(n, d, T_DP, ek, Fraction(mid, 1 << 14))[0] * Q_CLAIM.denominator >= Q_CLAIM.numerator * ONE:
            hi = mid
        else:
            lo = mid
    rate_min = hi / (1 << 14)
    CNT["mul"] += 2 * 20                  # the comparisons of the 14 + 6 evaluations above with 0.39
    rate_table = {str(float(c)): success_fp(n, d, T_DP, ek, c)[0] / ONE for c in (Fraction(1), Fraction(9, 10), Fraction(3, 4), Fraction(3, 5), Fraction(1, 2), Fraction(2, 5))}
    slack = {"n0": n0, "n_over_n0": n / n0, "slack_bits": log2(n / n0), "x": x, "rate_min": rate_min, "rate_table": rate_table}
    assert STEPS is None or (steps == STEPS and gmax == GMAXC), "STEPS and GMAXC are the plan's S and gmax"
    assert steps < SMAX and steps % UNROLL == 0 and T_DP < (1 << 16)
    total_ops = ledger(steps, gmax, MCAP) + PREP_OPS
    f, mu = table_exp(steps, T_DP, MCAP)
    assert f is not None and f <= -TAB * ONE      # the table-overflow bound of Section 5(c): mean < MCAP + 1 and ln P(overflow) <= -TAB
    mem = memory()
    assert mem["total"] <= 1 << 20
    ws = len(STEP) + W_LOOP
    tlog = log2(total_ops / C_UNIT)
    assert CNT["bits"] < 1 << 11
    return {"partial_rounds": PARTIAL, "C": C_UNIT, "step_field_ops": len(STEP), "step_add": sum(o[0] == "ADD" for o in STEP),
            "step_mul": sum(o[0] == "MUL" for o in STEP), "W_LOOP": W_LOOP, "W_BLOCK": W_BLOCK, "W_REC": W_REC,
            "ops_per_trail_step": ws + W_BLOCK / UNROLL, "T_DP": T_DP, "MCAP": MCAP, "KD": str(KD), "H": str(H), "TAB": TAB,
            "theta_log2": log2(D_DP / P), "n": n, "n_over_2^100": k, "n_log2": log2(n), "d": d, "gmax": gmax, "steps": steps,
            "eps_total": eps / ONE, "success_lower_bound": succ / ONE, "success_lower_bound_decimal": "0." + str(succ * 10 ** 20 // ONE).zfill(20),
            "slack": slack, "mean_stored_bound": mu / ONE, "ln_P_table_overflow": f / ONE, "other_fixed": OTHER_FIXED, "prep_ops": PREP_OPS,
            "prep_log2_units": log2(max(PREP_OPS, 1) / C_UNIT), "total_ops": total_ops,
            "T_units": total_ops / C_UNIT, "time_log2": tlog, "constants": NCONST, "memory": mem}


def attack(coin):
    """The claimed attempt (one run, not repeated). It executes only the step program, the table logic and the recovery: STEPS and GMAXC are integer literals (printed with the parameters in section 5), not computed online; `plan` is the offline derivation and check of those literals and of the ledger. coin = two uniformly random 256-bit words; rho0 and x0 are their low 254 bits (every
    254-bit word is below p, so both are canonical). The walk is F(x) = digest(message(x + rho0)) / OUTSCALE. Returns the two 64-byte messages or None."""
    m254 = (1 << 254) - 1
    rho0, x0 = coin[0] & m254, coin[1] & m254
    pair, status, ev, ops = search(make_F(rho0), lambda x: (x & M128) < T_DP, x0, STEPS, MCAP, GMAXC)
    if pair is None:
        return None
    (a0, a1), (b0, b1) = message((pair[0] + rho0) % P), message((pair[1] + rho0) % P)
    return enc(a0) + enc(a1), enc(b0) + enc(b1)


# ================================================================ 6 self-checks (reduced width) and command line
NB = 14                                   # walk width of the self-check: the low 14 bits of F (real step program, real rounds)


def run_rho(seed):
    """The search of `attack` on the reduced map v -> low NB bits of F(v), rho and the start taken from the seed; the pair is checked on the
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
    pair, status, ev, ops = search(F_n, lambda v: v < (1 << (NB - 4)), x0, 256, 64, 160)
    if pair is None:
        return None, {"status": status, "evals": ev, "ops": ops}
    a, b = pair
    ma, mb = message((a + rho) % P), message((b + rho) % P)
    assert a != b and ma != mb and F_n(a) == F_n(b)
    assert (digest(*ma) * OUTINV % P) & ((1 << NB) - 1) == (digest(*mb) * OUTINV % P) & ((1 << NB) - 1)
    return (ma, mb), {"status": status, "evals": ev, "ops": ops}


def selftest():
    import random
    rng = random.Random(PARTIAL)
    for _ in range(4):                    # the line: rounds 0 and 1 are affine in W, message is injective on samples
        W = rng.randrange(P)
        A, A1, S = after_round1(*message(0)), after_round1(*message(1)), after_round1(*message(W))
        assert all(S[i] == (A[i] + W * (A1[i] - A[i])) % P for i in range(3))
        assert message(W) != message((W + 1) % P)
    for _ in range(6):                    # the step program equals the reference digest of the line message, divided by OUTSCALE
        x, rho0 = rng.randrange(P), rng.randrange(1 << 254)
        assert make_F(rho0)(x) == digest(*message((x + rho0) % P)) * OUTINV % P
    assert len(STEP) == 136 + 12 * PARTIAL
    ok, worst = 0, 0
    for t in range(24):
        res, ob = run_rho(hashlib.sha256(b"t%d" % t).hexdigest())
        ok += res is not None
        o = ob["ops"]
        bound = (len(STEP) + W_LOOP) * 256 + W_BLOCK * 32 + (len(STEP) + W_REC) * 3 * 160 + (64 + 1) * (W_DP + W_SCAN * 64 + W_INS) + 8 * W_PROBE
        assert ledger_ops(o, len(STEP)) <= bound and o["trail"] <= 256 and o["rec"] <= 3 * 160
        worst = max(worst, ledger_ops(o, len(STEP)))
    return {"step_ops": len(STEP), "line_affine": True, "step_equals_reference": 6, "rho_n14_pairs": ok, "of": 24, "largest_counted_ops": worst}


def listing():
    return "\n".join("%s %s, %s, %s" % s for s in STEP)


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--plan":
            print(json.dumps(plan(), indent=1))
        elif sys.argv[1] == "--selftest":
            print(json.dumps(selftest()))
        elif sys.argv[1] == "--listing":
            print(listing())
        return
    print(json.dumps(plan(), indent=1))


if __name__ == "__main__":
    main()
```

## Appendix C: the step program, `python3 rho.py --listing` (424 operations: op dest, src1, src2; k<n> are the step constants, e0..e2 the attempt registers)

```
ADD y0, x, e0
ADD y1, x, e1
ADD y2, x, e2
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
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
ADD y0, h0, k135
ADD y1, h1, k136
ADD y2, h2, k137
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k138
MUL t2, z2, k139
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k140
MUL t1, z1, k141
MUL t2, z2, k142
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k143
MUL t1, z1, k144
MUL t2, z2, k145
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k146
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k147
MUL t2, z2, k148
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k149
MUL t1, z1, k150
MUL t2, z2, k151
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k152
MUL t1, z1, k153
MUL t2, z2, k154
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k155
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k156
MUL t2, z2, k157
ADD y0, z0, t1
ADD y0, y0, t2
ADD y0, y0, k158
MUL t1, z1, k159
MUL t2, z2, k160
ADD y1, z0, t1
ADD y1, y1, t2
ADD y1, y1, k161
MUL t1, z1, k162
MUL t2, z2, k163
ADD y2, z0, t1
ADD y2, y2, t2
ADD y2, y2, k164
MUL s_z0, y0, y0
MUL s_z0, s_z0, s_z0
MUL z0, s_z0, y0
MUL s_z1, y1, y1
MUL s_z1, s_z1, s_z1
MUL z1, s_z1, y1
MUL s_z2, y2, y2
MUL s_z2, s_z2, s_z2
MUL z2, s_z2, y2
MUL t1, z1, k165
MUL t2, z2, k166
ADD x, z0, t1
ADD x, x, t2
```

## Appendix D: replay sources of the measurements (verbatim)

Files: `lmeas.c` (measurement program), `lconsts.h` (A, B and OUTINV_r = 1 / OUTSCALE_r as computed by the row programs), `pallas.h`, `pallas.c` (our C Pallas field and Orchard permutation, with `poseidon_perm_from2_r` for rounds 2..63 from a supplied state) and `pallas_consts.h` (deployed round constants and MDS). Build: `gcc -O2 -march=native -Wall -Wextra -o lmeas lmeas.c pallas.c`. Arguments per job: family (l: the line map at r partial rounds; c: control), fixed (0), r, w, T, h, S, mcap, gmax (Lemma 2 parameters for N = 2^w, D = T * 2^(w-h), SMAX = 2^(h+3)), trials, seedbase.

### lmeas.c

```c
/* lmeas.c - measurements of the v3 walk map at r partial rounds on truncated outputs (our own code, 2026-10-16; derived from our h1meas.c).
 * Map at width w (family l): F_w(v) = low w bits of digest(message(v + rho)) / OUTSCALE_r, v in [0, 2^w), computed as: state after round 1
 *   = A + (v + rho) B (the line of the row program, constants in lconsts.h), rounds 2..63 of the reference permutation, lane 0 times OUTINV_r.
 *   rho is a 254-bit word drawn per trial from the function index j (four splitmix64 words), as the attempt draws rho0.
 * Per trial: walk v_0 (from the seed), v_i = F_w(v_{i-1}) until the first repeat (exact, hash map of all values):
 *   t = least index with v_t in {v_0..v_{t-1}}, mu = index of that earlier value, lambda = t - mu.
 * DP statistics at density theta = T/2^h (DP iff (v mod 2^h) < T): gaps between consecutive DPs among v_1..v_{t-1}.
 * Then the search of rho.py (one trail, DPs, table cap mcap, budget S, recovery with gap cap gmax) is run on the same map;
 * trail values are taken from the stored walk (they are digest values), the recovery evaluates the digest afresh and the returned
 * pair is checked (distinct, equal F_w).
 * Usage: h1meas fam fixed r w T h S mcap gmax K seedbase   -> one JSON line per trial on stdout.
 *   fam o|c; fixed 0: trial k uses function index j = seedbase*1000003 + k (rho = j, or control key j), fixed f >= 1: j = f - 1 for every trial (one fixed function, many starts).
 *   start v_0 = splitmix(seedbase*1000003 + k) mod 2^w.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "pallas.h"
#include "lconsts.h"

static int R, W, FAM;              /* FAM 'o': Orchard digest(v, rho) ; FAM 'l': the v3 line map ; FAM 'c': control, keyed splitmix (a pseudo-random function) */
static fp LA[3], LB[3], OUTINV_M, RHOF;
static uint64_t MASK, RHO, CKEY;
static uint64_t splitmix(uint64_t x) {
    x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}
static uint64_t Fw(uint64_t v) {
    if (FAM == 'c') return splitmix(splitmix(v ^ CKEY) + CKEY) & MASK;
    if (FAM == 'l') {
        fp Wv, s[3], o; uint64_t lim[4];
        fp_from_u64(&Wv, v); fp_add(&Wv, &Wv, &RHOF);
        for (int i = 0; i < 3; i++) { fp_mul(&s[i], &Wv, &LB[i]); fp_add(&s[i], &s[i], &LA[i]); }
        poseidon_perm_from2_r(s, R);
        fp_mul(&o, &s[0], &OUTINV_M); fp_to_limbs(lim, &o);
        return lim[0] & MASK;
    }
    uint64_t a[4] = {v, 0, 0, 0}, z[4] = {RHO, 0, 0, 0}, o[4];
    poseidon_hash_r(a, z, R, o);
    return o[0] & MASK;          /* W <= 62 */
}

static void set_rho(uint64_t j) {
    uint64_t lim[4];
    for (int c = 0; c < 4; c++) lim[c] = splitmix(j * 4ULL + (uint64_t)c + 0x77ULL);
    lim[3] &= (1ULL << 62) - 1;          /* 254-bit word, below p */
    fp_from_limbs(&RHOF, lim);
}
static void line_init(int r) {
    for (int i = 0; i < 3; i++) { fp_from_hex(&LA[i], LINE_A_HEX[i]); fp_from_hex(&LB[i], LINE_B_HEX[i]); }
    fp_from_hex(&OUTINV_M, OUTINV_HEX[r]);
}

int main(int argc, char **argv) {
    if (argc == 5 && !strcmp(argv[1], "kat")) {   /* kat r rhohex xhex: prints the full F(x) = digest(message(x + rho)) / OUTSCALE_r */
        R = atoi(argv[2]); line_init(R);
        fp x, o, s[3], Wv; char h[65];
        fp_from_hex(&RHOF, argv[3]); fp_from_hex(&x, argv[4]); fp_add(&Wv, &x, &RHOF);
        for (int i = 0; i < 3; i++) { fp_mul(&s[i], &Wv, &LB[i]); fp_add(&s[i], &s[i], &LA[i]); }
        poseidon_perm_from2_r(s, R); fp_mul(&o, &s[0], &OUTINV_M); fp_to_hex(h, &o); printf("%s\n", h); return 0;
    }
    if (argc != 12) { fprintf(stderr, "usage: h1meas fam fixed r w T h S mcap gmax K seedbase\n"); return 2; }
    FAM = argv[1][0]; int FIXED = atoi(argv[2]); argv += 2;
    R = atoi(argv[1]); W = atoi(argv[2]); if (FAM == 'l') line_init(R);
    uint64_t T = strtoull(argv[3], 0, 10); int H = atoi(argv[4]);
    uint64_t S = strtoull(argv[5], 0, 10), MCAP = strtoull(argv[6], 0, 10), GMAX = strtoull(argv[7], 0, 10);
    int K = atoi(argv[8]); uint64_t SB = strtoull(argv[9], 0, 10);
    MASK = (W >= 64) ? ~0ULL : ((1ULL << W) - 1); uint64_t HM = (1ULL << H) - 1;
    /* walk cap: 12 sqrt(N) (P(t > cap) <= exp(-72) for a random mapping); hash table 2^k >= 2 cap */
    uint64_t cap = (uint64_t)(12.0 * (double)(1ULL << (W / 2)) * ((W & 1) ? 1.41421356 : 1.0));
    uint64_t hsz = 1; while (hsz < 2 * cap) hsz <<= 1;
    uint64_t *hk = malloc(hsz * 8); uint32_t *hv = malloc(hsz * 4); uint64_t *tr = malloc((cap + 1) * 8);
    uint64_t *pi = malloc((MCAP + 2) * 8), *pv = malloc((MCAP + 2) * 8);   /* table: index word, value word */
    if (!hk || !hv || !tr || !pi || !pv) { fprintf(stderr, "alloc\n"); return 1; }
    for (int k = 0; k < K; k++) {
        memset(hk, 0, hsz * 8);
        uint64_t j = FIXED ? (uint64_t)(FIXED - 1) : SB * 1000003ULL + (uint64_t)k; RHO = j; CKEY = splitmix(j ^ 0x5bd1e995ULL); if (FAM == 'l') set_rho(j);
        uint64_t v = splitmix(SB * 1000003ULL + (uint64_t)k) & MASK;
        uint64_t t = 0, mu = 0; int cens = 0;
        uint64_t hm = hsz - 1;
        /* insert v_0 */
        for (uint64_t i = 0;; i++) {
            tr[i] = v;
            uint64_t h = (splitmix(v) & hm);
            while (hk[h] && hk[h] != v + 1) h = (h + 1) & hm;
            if (hk[h]) { t = i; mu = hv[h]; break; }
            hk[h] = v + 1; hv[h] = (uint32_t)i;
            if (i >= cap) { cens = 1; t = i; break; }
            v = Fw(v);
        }
        uint64_t lam = t - mu;
        /* DP gaps among v_1..v_{t-1} */
        uint64_t ndp = 0, last = 0, ngap = 0, sgap = 0, maxgap = 0; int first = 1;
        for (uint64_t i = 1; i < t; i++) if ((tr[i] & HM) < T) {
            ndp++;
            if (!first) { uint64_t g = i - last; ngap++; sgap += g; if (g > maxgap) maxgap = g; }
            first = 0; last = i;
        }
        /* first DP at index >= mu (cycle), detection delay */
        int64_t aprime = -1;
        for (uint64_t i = (mu ? mu : 1); i < t; i++) if ((tr[i] & HM) < T) { aprime = (int64_t)i; break; }
        if (mu == 0 && aprime < 0 && (tr[0] & HM) < T) aprime = -1;  /* start is not a stored DP */
        /* the search of rho.py on this trail */
        const char *st = "steps"; uint64_t ev = 0, rec = 0, A = 0, B = 0; int ok = 0;
        if (!cens) {
            uint64_t np = 1; pi[0] = 0; pv[0] = tr[0];
            uint64_t i = 0, x = tr[0]; int64_t hit = -1;
            while (i < S) {
                i++; ev++;
                x = (i < t) ? tr[i] : tr[mu + (i - mu) % lam];
                if ((x & HM) < T) {
                    for (uint64_t q = 1; q < np; q++) if (pv[q] == x) { hit = (int64_t)q; break; }
                    if (hit >= 0) break;
                    if (np > MCAP) { st = "table"; break; }
                    pi[np] = i; pv[np] = x; np++;
                }
            }
            if (hit >= 0) {
                uint64_t a = pi[hit], L = i - a, s = pi[hit - 1]; A = pv[hit - 1];
                uint64_t q = s + L; uint64_t lo = 0, hi = np - 1;
                while (lo < hi) { uint64_t m = (lo + hi + 1) / 2; if (pi[m] <= q) lo = m; else hi = m - 1; }
                uint64_t idx = pi[lo]; B = pv[lo];
                if (q - idx > GMAX) st = "gap";
                else {
                    for (uint64_t j = 0; j < q - idx; j++) { B = Fw(B); rec++; }
                    if (A == B) st = "start-on-cycle";
                    else {
                        st = "gap";
                        for (uint64_t j = 0; j < GMAX; j++) {
                            uint64_t nA = Fw(A), nB = Fw(B); rec += 2;
                            if (nA == nB) { st = "found"; ok = (A != B) && (Fw(A) == Fw(B)); break; }
                            A = nA; B = nB;
                        }
                    }
                }
            } else if (strcmp(st, "table")) st = "steps";
        }
        printf("{\"fam\":\"%c\",\"fn\":%llu,\"r\":%d,\"w\":%d,\"seedbase\":%llu,\"k\":%d,\"v0\":%llu,\"t\":%llu,\"mu\":%llu,\"lambda\":%llu,\"cens\":%d,"
               "\"ndp\":%llu,\"ngap\":%llu,\"sgap\":%llu,\"maxgap\":%llu,\"aprime\":%lld,\"status\":\"%s\",\"evals\":%llu,\"rec\":%llu,"
               "\"A\":%llu,\"B\":%llu,\"pair_ok\":%d}\n",
               FAM, (unsigned long long)j, R, W, (unsigned long long)SB, k, (unsigned long long)tr[0], (unsigned long long)t, (unsigned long long)mu,
               (unsigned long long)lam, cens, (unsigned long long)ndp, (unsigned long long)ngap, (unsigned long long)sgap,
               (unsigned long long)maxgap, (long long)aprime, st, (unsigned long long)ev, (unsigned long long)rec,
               (unsigned long long)(strcmp(st, "found") ? 0 : A), (unsigned long long)(strcmp(st, "found") ? 0 : B), ok);
        fflush(stdout);
    }
    return 0;
}
```

### lconsts.h

```c
/* GENERATED by gen_lconsts.py from the v3 row program: canonical big-endian hex */
static const char *LINE_A_HEX[3] = {"21ae29fc9f5fea88f6ad6f9c4372552064f48d10001e85a23ba49ec39b1be098","2033979f9d72b250c8a1f9f698f9d9d357909b3b5b3805f1899074b9eaf5e132","1cf7a82f2fc4e03dc7d963b0c2c9201baab9f1d0967a2ba1d646de0370c3f0ed"};
static const char *LINE_B_HEX[3] = {"23c27f31affe3355705c3436661672f812bf595c8c693caf2632952857b4f542","0bf0a531e547aaee0a858122cd51bf61d3410fbc8972013ce3666a6f47a5b802","3b86955a87b71c2631869b9fb992631c4a32ee6dea0ad3a8fc3e1f12f348c40a"};
static const char *OUTINV_HEX[57] = {"0000000000000000000000000000000000000000000000000000000000000000",
"0d19c03a14909b962db7a6d9c0f23ed965a5f8a5af75a8896d7ef3e2e4deee12",
"01933b5f71af11359bcf65f9525bb44bd6b94004613c3188533bbd3eedfc6318",
"285edfd689baa07d08561e6b91d66ceb4f1a62722c96858ef5c59ff1627a33d7",
"07e12c0bd0dd61a2a54498502f09f5b65cfd5447ee79db8e8a3d86440176be6d",
"0e9f47447654ff32f8160953f7357c0193978d0274c960731413f64ec86a806d",
"032374e6848a4ee44dffa18cc7b64da5c3a558b5dc3293afc53bc6881ab70ab9",
"10063a14e044a8a2d531dc37fdf758bc2bad3d4d4ae0b6683137de9b211b2a24",
"3bfb0b1d07b61ab3387e6d4fa35a33627f56de65a4b379ab1113093c1c387b09",
"36db150313d234393d2ea3e52b0c2962161aa8c9fb04198ed8fac06a9a5ec7fc",
"3d2ab8e7c51bf9349bf827e08147f8e5423f9e3ff78589d084faf5f1172b5cdd",
"252371aca4b3119acb0dcc9e6832ded11bc688638fb79fced115596f4dc3bbff",
"2744ed2107f65bb31de80060e9e74ee41b9b78e9c24fb5e2870951fec6e4c8fa",
"319d222f795ef4c71cd339f69f7084b3487c996873ca3e256d14a9b8429601ee",
"1954062edd8c45193cb0228572b25765c4164ee196026c8a2ebf5776ec00fe19",
"28218b0c73ed56d52d3adef616181a5b027477357945e322cc2f6f8bc4f59005",
"3343c16dc5c691b33aee3c020291f1a97b2287a90f6d92ac17d5b119fd5f21ca",
"31c8782bcbe630226623d1e2cd34655357778d3bb1590d818ce4d5bed909d069",
"060d58e34901531862c8c608360559fb02f6aa9dd88d41880a315a9b544b525c",
"3b0637f64dd8837c46b84e6acf31e5eedacf40a0e7b33c6e6ebd9adcc6280446",
"015a19c4cc1645d7f79e321091a49c9aa7c70c528de8d55c3592e25a455ca254",
"3887b125d8a8c33d7dfd233465a395997bd327e239dafe5eee8095b27033f6c8",
"12a7f8f5998be5ac60fab7eaddcd53a01361909172e8f304d5590b0f6d456724",
"18b086c96248e65dbbd569d395c708068742b4759f253f51acb76393a5a14bff",
"254a9dfdff9245bca5b712fa38dc87e6203275efec4edddfa9d66fdaa0716efb",
"156b2ecb9d3618ab96f3ad081ebe7fcecf142fd712b5338375505b8699c0266e",
"3716d5567884e4a054500c227a89a6669334d47b7780ea109b255f0f355e366e",
"0f7a20375e1cb531717e5bca827ccb91357799097b58c7386e384490937c7224",
"3b9211f7917ba58516faa74b2537fa98ad5659829cf5d7f2a464e411a13b1ee7",
"2b996491a18f451ee57a8fad5443a5f3f94769067361a2ce36e9b20e6abc0457",
"14e72a162090c128a19c878c676a7a8ec00fab2613f531eda484d7109800997c",
"19eb6a842b6b9731f3f204090bcdb945a4fd0c5cc393d09be4859a6a36a8220e",
"1171cc3e3bf3f5608ae5eb6ebfb0b064508708c2d0f4be037c0f1d23956a2af3",
"21cf771c5375ee8a3e31c8657e4df784d78fbb648e961436156e070f82b118f3",
"3563aec914367fc30d0a223a3e6bf2dfc456c55a2e5477bd8dc33233842ddab1",
"15b08a42da9115400f1ab23123507f88b0f3748ad79c21cbd0e0f3e859614fdb",
"26fae65ffb52368ba7cf53007f3ef2efbf75fa762e57a335871f360b1a8968e1",
"1fc5d0cf36de0a38b8cc47f60bb433f90c6e5767b061da78fad37f088850e7eb",
"108ffd673ac0c4d4e6fac3f50dc09ea038485d63f024e204b4b2b9c03a466698",
"3589396a6e5f8a3b8e480bfaed97a40ce1fc3792641c2b0ac0eeff5caa33280f",
"245abf565a9d8149658b24957a238e79571b4b3511c691793906ac8b6f21675e",
"2d193002e3a1d6cac8a986cb0d6959de50a9bb65e7cd1671bc5832510730a7ad",
"093625d7aad99bb06a0376b4bc9a776a410ec752e44e267916890f441d3db77b",
"2a497ffe8fa66e0c89eace599826b75a99afd69dd84377d472476df7c60f66d5",
"058c4eb36e029006c8ec006c30cee9f86dea1f4c08308ae9ea0c1647e1033afe",
"04f8cce8f7f9b00795ce45c6de8fc3c47cad96cb4c1e4e7561529cce3f3a6d0d",
"09f54baf3dd754be91ce1d2743110fdbfbde5ab7cbb5854e71a7ba1e6fffc530",
"262b2fbebfef86168ac55b8758006a0496bb5b3a7cc4ff9096bf801deb0722b8",
"331d9f7d45780f84ca187bd69344603851bf3bff210c95a0fa703a380a95cd65",
"2e49fde4935c8f9aabd8b3f7619f6ac2228fc9e11c09f36b15896cf97cf74e3c",
"2e1c37863fbc89e76f9967dd66d992b1ca7858cfa0b04b822ea07cb88bdde476",
"09f07c28dd224722c3103ff1f4b9c09e3dceeb79d9d52a846d5518fc834f8f71",
"18354a2540eaaf7c48884bb6d48da9dc19a55c4be78666b0fa37b2b3f9543dfd",
"1a08eb5b80e515991ac3aea5cefa5c0b488a6e5fe8a63a5d3d9462df032c77d5",
"08bd3935b9e20e47f77d3bc17329cb975b62c3aa1fde0e286f5ffa92b09ba370",
"1c03607bef4f7ea4c3b82a6a5fa5ea66755dd42a5f8cb9e343af8e4eec7007ee",
"26e29bed745e471f0fcedd4ed1a3d5f86a717a84754b8e41bd4d5dee75266e78"};
```

### pallas.h

```c
/* Pallas base field (p = 0x4000...224698fc094cf91b992d30ed00000001), 4x64-bit Montgomery representation,
 * exact operation counters, and the Orchard P128Pow5T3 reduced hash. Not constant time. */
#ifndef PALLAS_H
#define PALLAS_H
#include <stdint.h>
#include <stddef.h>

typedef struct { uint64_t l[4]; } fp;          /* Montgomery form, always fully reduced (< p), little-endian limbs */

/* ---- exact counters (global, single-threaded). Charged primitives = add + sub + mul + sqr.
 * inv/pow/sqrt "calls" are informational ONLY: their constituent ops are already counted in add/sub/mul/sqr. */
typedef struct {
    uint64_t add, sub, mul, sqr;               /* primitive field operations actually executed */
    uint64_t inv_calls, pow_calls, sqrt_calls; /* informational, not charged separately */
} fp_counters;
extern fp_counters fp_cnt;
void     fp_counters_reset(void);
uint64_t fp_prim_total(void);                  /* add+sub+mul+sqr  (each = 1/C(r) target-compression units) */

/* ---- conversions (I/O encodings; NOT counted: a program may store constants/inputs in Montgomery form) */
void fp_from_limbs(fp *r, const uint64_t v[4]);    /* canonical integer limbs (< p) -> Montgomery */
void fp_to_limbs(uint64_t v[4], const fp *a);      /* Montgomery -> canonical integer limbs */
int  fp_limbs_canonical(const uint64_t v[4]);      /* 1 iff v < p */
void fp_from_u64(fp *r, uint64_t x);
int  fp_from_hex(fp *r, const char *hex64);        /* 64 hex digits big-endian; returns 0 ok, -1 bad/noncanonical */
void fp_to_hex(char out[65], const fp *a);

/* ---- field operations (each counted) */
void fp_add(fp *r, const fp *a, const fp *b);
void fp_sub(fp *r, const fp *a, const fp *b);
void fp_neg(fp *r, const fp *a);                   /* counted as one sub (0 - a) */
void fp_dbl(fp *r, const fp *a);                   /* counted as one add */
void fp_mul(fp *r, const fp *a, const fp *b);
void fp_sqr(fp *r, const fp *a);                   /* counted as one sqr (a primitive multiplication) */
void fp_pow5(fp *r, const fp *a);                  /* sqr, sqr, mul = 3 primitives */
void fp_pow(fp *r, const fp *a, const uint64_t e[4]); /* left-to-right square-and-multiply, exact count (no op on zero-bit multiplies) */
void fp_inv(fp *r, const fp *a);                   /* a^(p-2); inv(0)=0. Expands to its sqr/mul ops. */
int  fp_sqrt(fp *r, const fp *a);                  /* Tonelli-Shanks (2-adicity 32); 1 and a root if a is a square (0 -> 0), else 0 */
int  fp_legendre(const fp *a);                     /* 0, 1, -1 via a^((p-1)/2); counted */

/* ---- uncounted helpers (comparisons are NOT charged here; charge them yourself if your algorithm needs them) */
int  fp_eq(const fp *a, const fp *b);
int  fp_is_zero(const fp *a);
void fp_set_zero(fp *r);
void fp_set_one(fp *r);

/* ---- Orchard P128Pow5T3, reduced to full rounds 0..3, r partial rounds 4..4+r-1, full rounds 60..63 (0<=r<=56) */
int  poseidon_C(int r);                            /* 216 + 21 r */
void poseidon_perm_r(fp s[3], int r);              /* faithful reference arithmetic: 27*8 + 21*r primitives */
void poseidon_perm_from2_r(fp s[3], int r);        /* rounds 2..63 only (v3 line-map measurements) */
int  poseidon_hash_r(const uint64_t nk[4], const uint64_t rho[4], int r, uint64_t out[4]); /* canonical limbs; 0 ok, -1 invalid */
void poseidon_hash_r_fp(fp *out, const fp *nk, const fp *rho, int r); /* state [nk, rho, 2^65], returns state[0] */
#endif
```

### pallas.c

```c
#include "pallas.h"
#include "pallas_consts.h"
#include <string.h>
#include <stdio.h>

typedef unsigned __int128 u128;
fp_counters fp_cnt;
void fp_counters_reset(void) { memset(&fp_cnt, 0, sizeof fp_cnt); }
uint64_t fp_prim_total(void) { return fp_cnt.add + fp_cnt.sub + fp_cnt.mul + fp_cnt.sqr; }

/* ---------- raw (uncounted) limb helpers ---------- */
static int geq_p(const uint64_t a[4]) {
    for (int i = 3; i >= 0; i--) { if (a[i] > PALLAS_P[i]) return 1; if (a[i] < PALLAS_P[i]) return 0; }
    return 1;
}
static void sub_p(uint64_t a[4]) {
    uint64_t b = 0;
    for (int i = 0; i < 4; i++) { u128 d = (u128)a[i] - PALLAS_P[i] - b; a[i] = (uint64_t)d; b = (uint64_t)(d >> 64) & 1; }
}
static void mont_mul_raw(uint64_t r[4], const uint64_t a[4], const uint64_t b[4]) {
    uint64_t t[6] = {0, 0, 0, 0, 0, 0};
    for (int i = 0; i < 4; i++) {
        uint64_t carry = 0;
        for (int j = 0; j < 4; j++) { u128 s = (u128)a[i] * b[j] + t[j] + carry; t[j] = (uint64_t)s; carry = (uint64_t)(s >> 64); }
        u128 s = (u128)t[4] + carry; t[4] = (uint64_t)s; t[5] = (uint64_t)(s >> 64);
        uint64_t m = t[0] * PALLAS_INV;
        s = (u128)m * PALLAS_P[0] + t[0]; carry = (uint64_t)(s >> 64);
        for (int j = 1; j < 4; j++) { s = (u128)m * PALLAS_P[j] + t[j] + carry; t[j - 1] = (uint64_t)s; carry = (uint64_t)(s >> 64); }
        s = (u128)t[4] + carry; t[3] = (uint64_t)s; carry = (uint64_t)(s >> 64);
        t[4] = t[5] + carry;
    }
    /* t < 2p here; t[4] is 0 because p < 2^255 */
    r[0] = t[0]; r[1] = t[1]; r[2] = t[2]; r[3] = t[3];
    if (t[4] || geq_p(r)) sub_p(r);
}

/* ---------- conversions ---------- */
int fp_limbs_canonical(const uint64_t v[4]) { return !geq_p(v); }
void fp_from_limbs(fp *r, const uint64_t v[4]) { uint64_t t[4]; mont_mul_raw(t, v, PALLAS_R2); memcpy(r->l, t, 32); }
void fp_to_limbs(uint64_t v[4], const fp *a) { static const uint64_t one[4] = {1, 0, 0, 0}; uint64_t t[4]; mont_mul_raw(t, a->l, one); memcpy(v, t, 32); }
void fp_from_u64(fp *r, uint64_t x) { uint64_t v[4] = {x, 0, 0, 0}; fp_from_limbs(r, v); }
int fp_from_hex(fp *r, const char *hex) {
    uint64_t v[4] = {0, 0, 0, 0};
    for (int i = 0; i < 64; i++) {
        char c = hex[i]; int d;
        if (c >= '0' && c <= '9') d = c - '0'; else if (c >= 'a' && c <= 'f') d = c - 'a' + 10; else if (c >= 'A' && c <= 'F') d = c - 'A' + 10; else return -1;
        int pos = 63 - i;                       /* nibble index from least significant */
        v[pos / 16] |= (uint64_t)d << (4 * (pos % 16));
    }
    if (!fp_limbs_canonical(v)) return -1;
    fp_from_limbs(r, v); return 0;
}
void fp_to_hex(char out[65], const fp *a) {
    uint64_t v[4]; fp_to_limbs(v, a);
    snprintf(out, 65, "%016llx%016llx%016llx%016llx", (unsigned long long)v[3], (unsigned long long)v[2], (unsigned long long)v[1], (unsigned long long)v[0]);
}

/* ---------- counted field ops ---------- */
void fp_add(fp *r, const fp *a, const fp *b) {
    fp_cnt.add++;
    uint64_t t[4], c = 0;
    for (int i = 0; i < 4; i++) { u128 s = (u128)a->l[i] + b->l[i] + c; t[i] = (uint64_t)s; c = (uint64_t)(s >> 64); }
    if (c || geq_p(t)) sub_p(t);
    memcpy(r->l, t, 32);
}
void fp_dbl(fp *r, const fp *a) { fp_add(r, a, a); }
void fp_sub(fp *r, const fp *a, const fp *b) {
    fp_cnt.sub++;
    uint64_t t[4], br = 0;
    for (int i = 0; i < 4; i++) { u128 d = (u128)a->l[i] - b->l[i] - br; t[i] = (uint64_t)d; br = (uint64_t)(d >> 64) & 1; }
    if (br) { uint64_t c = 0; for (int i = 0; i < 4; i++) { u128 s = (u128)t[i] + PALLAS_P[i] + c; t[i] = (uint64_t)s; c = (uint64_t)(s >> 64); } }
    memcpy(r->l, t, 32);
}
void fp_neg(fp *r, const fp *a) { fp z; fp_set_zero(&z); fp_sub(r, &z, a); }
void fp_mul(fp *r, const fp *a, const fp *b) { fp_cnt.mul++; uint64_t t[4]; mont_mul_raw(t, a->l, b->l); memcpy(r->l, t, 32); }
void fp_sqr(fp *r, const fp *a) { fp_cnt.sqr++; uint64_t t[4]; mont_mul_raw(t, a->l, a->l); memcpy(r->l, t, 32); }
void fp_pow5(fp *r, const fp *a) { fp t; fp_sqr(&t, a); fp_sqr(&t, &t); fp_mul(r, &t, a); }

void fp_set_zero(fp *r) { memset(r, 0, sizeof *r); }
void fp_set_one(fp *r) { memcpy(r->l, PALLAS_ONE_M, 32); }
int fp_eq(const fp *a, const fp *b) { return memcmp(a->l, b->l, 32) == 0; }
int fp_is_zero(const fp *a) { return (a->l[0] | a->l[1] | a->l[2] | a->l[3]) == 0; }

void fp_pow(fp *r, const fp *a, const uint64_t e[4]) {
    fp_cnt.pow_calls++;
    int top = -1;
    for (int i = 255; i >= 0; i--) if ((e[i / 64] >> (i % 64)) & 1) { top = i; break; }
    if (top < 0) { fp_set_one(r); return; }
    fp base = *a, acc = *a;                    /* leading 1 bit: acc = a, no operation */
    for (int i = top - 1; i >= 0; i--) {
        fp_sqr(&acc, &acc);
        if ((e[i / 64] >> (i % 64)) & 1) fp_mul(&acc, &acc, &base);
    }
    *r = acc;
}
void fp_inv(fp *r, const fp *a) { fp_cnt.inv_calls++; fp_pow(r, a, PALLAS_PM2); }
int fp_legendre(const fp *a) {
    if (fp_is_zero(a)) return 0;
    fp t, one; fp_pow(&t, a, PALLAS_PM1H); fp_set_one(&one);
    return fp_eq(&t, &one) ? 1 : -1;
}
/* Tonelli-Shanks with p-1 = 2^32 * q. Invariant: x^2 = a*t, z has order 2^m, t has order dividing 2^(m-1) iff a is a square. */
int fp_sqrt(fp *r, const fp *a) {
    fp_cnt.sqrt_calls++;
    if (fp_is_zero(a)) { fp_set_zero(r); return 1; }
    fp one; fp_set_one(&one);
    fp z, t, x, b;
    memcpy(z.l, PALLAS_Z_M, 32);                /* z = 5^q, order 2^32 */
    fp_pow(&t, a, PALLAS_Q);                    /* t = a^q   */
    fp_pow(&x, a, PALLAS_QP1H);                 /* x = a^((q+1)/2) */
    unsigned m = 32;
    while (!fp_eq(&t, &one)) {
        unsigned i = 0; fp u = t;
        while (!fp_eq(&u, &one)) { fp_sqr(&u, &u); i++; if (i >= m) return 0; }   /* i == m: t has order 2^m => non-residue */
        b = z;
        for (unsigned k = 0; k + i + 1 < m; k++) fp_sqr(&b, &b);                  /* b = z^(2^(m-i-1)) */
        fp_mul(&x, &x, &b);
        fp_sqr(&z, &b);
        fp_mul(&t, &t, &z);
        m = i;
    }
    *r = x; return 1;
}

/* ---------- Poseidon ---------- */
int poseidon_C(int r) { return 216 + 21 * r; }
static void mds_mul(fp s[3]) {
    fp o[3], t;
    for (int i = 0; i < 3; i++) {
        fp_mul(&o[i], &POSEIDON_MDS_M[i][0], &s[0]);
        fp_mul(&t, &POSEIDON_MDS_M[i][1], &s[1]); fp_add(&o[i], &o[i], &t);
        fp_mul(&t, &POSEIDON_MDS_M[i][2], &s[2]); fp_add(&o[i], &o[i], &t);
    }
    s[0] = o[0]; s[1] = o[1]; s[2] = o[2];
}
static void round_fn(fp s[3], int idx, int full) {
    for (int i = 0; i < 3; i++) fp_add(&s[i], &s[i], &POSEIDON_RC_M[idx][i]);
    if (full) for (int i = 0; i < 3; i++) fp_pow5(&s[i], &s[i]); else fp_pow5(&s[0], &s[0]);
    mds_mul(s);
}
void poseidon_perm_r(fp s[3], int r) {
    for (int i = 0; i < 4; i++) round_fn(s, i, 1);
    for (int i = 0; i < r; i++) round_fn(s, 4 + i, 0);
    for (int i = 60; i < 64; i++) round_fn(s, i, 1);
}
void poseidon_hash_r_fp(fp *out, const fp *nk, const fp *rho, int r) {
    fp s[3]; s[0] = *nk; s[1] = *rho; memcpy(s[2].l, POSEIDON_CAP_M, 32);
    poseidon_perm_r(s, r);
    *out = s[0];
}
int poseidon_hash_r(const uint64_t nk[4], const uint64_t rho[4], int r, uint64_t out[4]) {
    if (r < 0 || r > 56 || !fp_limbs_canonical(nk) || !fp_limbs_canonical(rho)) return -1;
    fp a, b, o; fp_from_limbs(&a, nk); fp_from_limbs(&b, rho);
    poseidon_hash_r_fp(&o, &a, &b, r); fp_to_limbs(out, &o); return 0;
}

/* added for the v3 line-map measurements: rounds 2..63 only (the state after round 1 is supplied by the caller) */
void poseidon_perm_from2_r(fp s[3], int r) {
    for (int i = 2; i < 4; i++) round_fn(s, i, 1);
    for (int i = 0; i < r; i++) round_fn(s, 4 + i, 0);
    for (int i = 60; i < 64; i++) round_fn(s, i, 1);
}
```

### pallas_consts.h

```c
/* GENERATED by gen_c_consts.py from the organizer JSON; limbs little-endian, values in Montgomery form */
#ifndef PALLAS_CONSTS_H
#define PALLAS_CONSTS_H
#define PALLAS_INV 0x992d30ecffffffffULL /* -p^{-1} mod 2^64 */
static const uint64_t PALLAS_P[4] = {0x992d30ed00000001ULL,0x224698fc094cf91bULL,0x0000000000000000ULL,0x4000000000000000ULL};
static const uint64_t PALLAS_R2[4] = {0x8c78ecb30000000fULL,0xd7d30dbd8b0de0e7ULL,0x7797a99bc3c95d18ULL,0x096d41af7b9cb714ULL};
static const uint64_t PALLAS_ONE_M[4] = {0x34786d38fffffffdULL,0x992c350be41914adULL,0xffffffffffffffffULL,0x3fffffffffffffffULL};
/* q = (p-1)/2^32, odd */
static const uint64_t PALLAS_Q[4] = {0x094cf91b992d30edULL,0x00000000224698fcULL,0x0000000000000000ULL,0x0000000040000000ULL};
/* (q+1)/2 */
static const uint64_t PALLAS_QP1H[4] = {0x04a67c8dcc969877ULL,0x0000000011234c7eULL,0x0000000000000000ULL,0x0000000020000000ULL};
/* (p-1)/2 */
static const uint64_t PALLAS_PM1H[4] = {0xcc96987680000000ULL,0x11234c7e04a67c8dULL,0x0000000000000000ULL,0x2000000000000000ULL};
/* p-2 */
static const uint64_t PALLAS_PM2[4] = {0x992d30ecffffffffULL,0x224698fc094cf91bULL,0x0000000000000000ULL,0x4000000000000000ULL};
/* Z = 5^q, primitive 2^32-th root of unity (Montgomery form) */
static const uint64_t PALLAS_Z_M[4] = {0xa28db849bad6dbf0ULL,0x9083cd03d3b539dfULL,0xfba6b9ca9dc8448eULL,0x3ec928747b89c6daULL};
static const uint64_t POSEIDON_CAP_M[4] = {0x992d30ed00000001ULL,0x58dd1194094cf913ULL,0xedcb381fb5983723ULL,0x3ffffffffffffffeULL}; /* 2^65 */
static const fp POSEIDON_RC_M[64][3] = {
  {{{0x2d6110568f8fb1cdULL,0xe436f09787ae5fc6ULL,0x51ea32d50f7be93fULL,0x3ee3b205efa6ab5dULL}},{{0x5564975171925a88ULL,0x4ccc244f2b4cee87ULL,0xa473a9e22140ab94ULL,0x293983c6cd66b132ULL}},{{0x1650a1e8d6eb3b9dULL,0xe1d084ae973c80a4ULL,0xc6b0e48a821b7324ULL,0x26f40bdecf47ed19ULL}}},
  {{{0xc6687b9c41161a23ULL,0x7132cacb8362ca7aULL,0xd85a41c272c6bbb5ULL,0x201e196e95c1d5a7ULL}},{{0xfac81e29844529d7ULL,0x55cd21dd6e3519aaULL,0xdac6e75068b2d6e6ULL,0x1db160cfe68f1791ULL}},{{0xd0380768fd7d233eULL,0x1e9be9783f636613ULL,0x072a39e85b32c9c0ULL,0x12451bc216857272ULL}}},
  {{{0x28238cb2f9610a03ULL,0xa5bf3dbbb71c1a95ULL,0xcfa2634c3dcdc1cfULL,0x30d475d91c9d2660ULL}},{{0xe54edcbe9506d50dULL,0x6336d456820cd730ULL,0x62f946f09a61cd4cULL,0x3dbf6a7660d1c1f2ULL}},{{0xa1f0f09ab6b52ec7ULL,0xa0256009a9a655c0ULL,0x02d87cd8131e6863ULL,0x1d82928e0581f03dULL}}},
  {{{0xd40988e46aa0d84aULL,0xcb83b98a6c3311b6ULL,0x1faecd3d4f5ba6feULL,0x21816a2ace1e6ceeULL}},{{0x12966345b9eb55e6ULL,0xe7207d68cede2273ULL,0xc5e2cfe134e17a59ULL,0x3b77812fa31cbea0ULL}},{{0x7c6cf91aa5ec91b8ULL,0x788439799fc5e819ULL,0x420b62303e699297ULL,0x03cf4743b88562d7ULL}}},
  {{{0x62a23ec7246945beULL,0xf0ce22ea72865fbdULL,0x656887c5d7179774ULL,0x0387c6accf862ddbULL}},{{0x3a8498acade3e889ULL,0x11837e2c04524a39ULL,0x1d734b9714471abcULL,0x123cb78b6fa1e7f0ULL}},{{0xd9e655459801f98aULL,0xfc579cc290c7c6f9ULL,0x2027d70ac2d2c545ULL,0x347d84f327297c50ULL}}},
  {{{0x0c514cbe25cd5dceULL,0xecce789089b36388ULL,0xe8ae18e6cf5c2d28ULL,0x09508b80b79c153cULL}},{{0xf1c79b4f210c1577ULL,0x39d1fa61fe64ebd8ULL,0xb8d92fd604863955ULL,0x16356b23d117fcf8ULL}},{{0x075b151491dd1191ULL,0x61dc8c496394e6dbULL,0x3db07ac8572c1d58ULL,0x0cd7d3fd2c41152eULL}}},
  {{{0xf2f6633139c4b05eULL,0x01dbcb2916c3253dULL,0xf1172b5fa58201e9ULL,0x16ce288f5de472a7ULL}},{{0x74b411041f0f061bULL,0x119ca91c82f60867ULL,0x88a45446cea98b5fULL,0x3f947ecf9f672579ULL}},{{0x9bc2a35b9de62d46ULL,0x040c50a583d292a1ULL,0x1f62387715c339a0ULL,0x2b0e1ed4a55c9b51ULL}}},
  {{{0x0988c91b9e85fef9ULL,0xe8ad133faa5d1bcdULL,0xd8df562e7b09d6efULL,0x0ce401a7279eeb38ULL}},{{0xc4dfd87b16cb67c7ULL,0x63d16458323b64bcULL,0xc8c653cf8e63bcccULL,0x11242b4450a3daa4ULL}},{{0x6768a64cd32ee7f7ULL,0xc2e49f96bbd21fb0ULL,0x97aae974ebac14cbULL,0x01d1a1069ea732f8ULL}}},
  {{{0xd11a4d50cdf5c831ULL,0xf0141a1730a04151ULL,0x4839556e137af540ULL,0x337fc238de198aacULL}},{{0x65126e84b58b3ba7ULL,0xc8d56c47b3b29eeeULL,0x8f7755c67ad08f38ULL,0x032b374daf0f5daeULL}},{{0x03c37d36570461bdULL,0xf7af83659d08e8f8ULL,0x5ab5a972d3ed3a2cULL,0x3ea0dc7d347f4499ULL}}},
  {{{0x6c9388c1bf9426b6ULL,0x6ef2023f27f48878ULL,0x4858081b3f9d5fc7ULL,0x022a53a4a03a61b2ULL}},{{0x8d8bbf6d29f2c488ULL,0xf1fb6efb14f6c308ULL,0x12566c68cdf47685ULL,0x2874c6e0c2f51250ULL}},{{0x0cbd4d8959832848ULL,0x0be4c3aaeae1eec8ULL,0x8ff6a34de0e0041bULL,0x35a497e0ae1c0c6fULL}}},
  {{{0xf265123421944696ULL,0x58c83e93fd718498ULL,0xf5d679bbfa9b691dULL,0x16394bccd2d2fddaULL}},{{0x6b0b7673c8d01fe1ULL,0x43d92fddf33b2e84ULL,0xc2c2fb35e711d5baULL,0x3310e80bcf0c079cULL}},{{0xba2001a87d410461ULL,0x92db1732f98ac5bfULL,0x46b53d2f258b21a0ULL,0x2431dc11acaf9487ULL}}},
  {{{0x4e5eac0c7809dac9ULL,0x88d278a88757b06dULL,0xb1caa105e8cfd525ULL,0x38c5e465b0998789ULL}},{{0x8d582cd16028d0b6ULL,0x02f5f6f2049341fbULL,0x14da884cd65b6d4cULL,0x175b5e71ccbd92ccULL}},{{0x7a4f279b84faae3fULL,0xdc9cf712aa7020eaULL,0xd282adb6f153c7ceULL,0x3dc87f51bee14157ULL}}},
  {{{0x54cf83685b98d9ecULL,0xf982055b2e3f539fULL,0xa9150eebebecca51ULL,0x101de276dcdc3feaULL}},{{0x07ff3281e556dffaULL,0x8e411f5f9f08c47aULL,0x901151014e2336c7ULL,0x051670efbebe0450ULL}},{{0x9e49643f069395b7ULL,0x28bf9db3e38928cdULL,0x8c02c832008df673ULL,0x079d4a1265f1f9b8ULL}}},
  {{{0x174d2c5549935069ULL,0xf449d64ba7afd980ULL,0x17489be3cbeb8217ULL,0x3dde70f1a49ecc6cULL}},{{0x7dfd80ab7fad4deeULL,0x8f7d70f1057b7365ULL,0x432c8e8ae0ea2f2dULL,0x21a4f21cbad39e96ULL}},{{0x97383a22729d1abaULL,0x4120a9e5df48c0aeULL,0x0ac4c5efc2eedad4ULL,0x1b96fd1670bdf887ULL}}},
  {{{0x663798be9e2ca816ULL,0x74a1d330e5c2746dULL,0xaf106b2043e0b1cdULL,0x1d3b129ea32c0690ULL}},{{0x623d1657253b3822ULL,0xde6cd3acc6c1e3daULL,0x1bbcb5725404e77dULL,0x1555343383b9e912ULL}},{{0x5e942b15b6542262ULL,0x99c8b631c5e985c4ULL,0x22cd0b12f24838eaULL,0x342e25680ac0f457ULL}}},
  {{{0xacee1be8258f1974ULL,0x330f1daa7a0a82d3ULL,0x30cf05803e57f42fULL,0x05af97ff16360de2ULL}},{{0xf60d13bc70fb7261ULL,0x89323aa335da65e0ULL,0xa230cf39306ada27ULL,0x37ec8d60f94c0e00ULL}},{{0x77cb61b22f0fef36ULL,0x97b9c176aa4f29dcULL,0x753951ba534b64ccULL,0x39d864f4db0d66e5ULL}}},
  {{{0x1c93a280de7e6390ULL,0x89bbe99192d5942bULL,0xd298630838ac97b4ULL,0x1fdee9515ec23733ULL}},{{0x1b1500ea3ea52e7cULL,0xab66b5200e504be8ULL,0xf2ca2fc2dd1238ceULL,0x2e99ac0058887a8eULL}},{{0x797a75c017355c08ULL,0x95753d5fbfe4b639ULL,0x99d90146a1022ee1ULL,0x18c6c282437c0106ULL}}},
  {{{0x28c41cb0f6a427aaULL,0x7a6274209547e747ULL,0x409958bab0ce8004ULL,0x0f5c9a21669c3561ULL}},{{0x4f458041d5a49e9aULL,0x70bf9be212724995ULL,0x16bb868a425b1357ULL,0x11bbfdbd72e6c273ULL}},{{0x840d988bb266eb39ULL,0x32ee4645ac430194ULL,0xdf94525d6b695073ULL,0x26f7032e169d741eULL}}},
  {{{0xed032a7242155f1cULL,0xd3bf87a6d0fc1c34ULL,0x6e6b7f2bba883e7aULL,0x03bee947acf8d869ULL}},{{0x54124791da75f84cULL,0xdea3fdd86d09154cULL,0xa8b1b78ee689124bULL,0x08cc569a704f8ae7ULL}},{{0x16e420feed279927ULL,0xd4e9f90a2430cadeULL,0xbda76f8c724ed3c4ULL,0x26f0c2eb7941a2edULL}}},
  {{{0xfa8bcd50c49a6dc1ULL,0x1b75bef3f3b40443ULL,0x16306d7f83e6e86fULL,0x2cb265185a682f74ULL}},{{0x816198532054502fULL,0xa53e572f12c3401fULL,0xe9a8f617740903c3ULL,0x2c9ba61ca6f41275ULL}},{{0xf5b6a307021d72c4ULL,0xf9b09e3b204957faULL,0x1ef85c62ca5473eeULL,0x0efc66dcec9a30aeULL}}},
  {{{0x005b369d1ddec201ULL,0x1a842b0d7196bbe6ULL,0x737adf896a50cea4ULL,0x236df79cb9f4188bULL}},{{0xea5b61d7bd606ab0ULL,0xccb039d4615a540eULL,0x1408af70b00d1a59ULL,0x225863cd3b10bb9dULL}},{{0x6cb2f4bcc26de564ULL,0xbb358e5aee7406abULL,0xf08ffcbb81863becULL,0x00f144f53402205fULL}}},
  {{{0x47dac6922bd0e686ULL,0x7d618f7ba9d32c8eULL,0x6118919ff121628cULL,0x074faa94927b7786ULL}},{{0x3af193a3ff7b9d4dULL,0x5b4be86fcf9052b0ULL,0xa9433b495aa64416ULL,0x041c30de6dcc571eULL}},{{0x3d90f898029f92e2ULL,0xfcbb9e4743c48e1dULL,0x20bc4ddedcf505afULL,0x0ce8a49fa10949e7ULL}}},
  {{{0x6bb524c3db961189ULL,0xe93f7a4d2c5cd069ULL,0xc7c572085a58c1f2ULL,0x157be04d9af4f4b7ULL}},{{0xcce74e4ac292398dULL,0xaed371d912fb1d56ULL,0x356e0c2dbf7bc066ULL,0x3514dcf22466a19fULL}},{{0xfd1e5928b50de13cULL,0x00f1d7fb3cb6d5ffULL,0xfe3bd8a8f595d931ULL,0x2aef30e01461acebULL}}},
  {{{0xa86cd7f133554ebbULL,0x094a97d9d8908309ULL,0x3de9cf716c0e5531ULL,0x2a215295d3b86a1cULL}},{{0xd53c009bb1e61c5cULL,0xfb9b2a40c066fa76ULL,0xfc69157a958ea7d9ULL,0x2a396665f94e134fULL}},{{0xf86e48d38ebb1402ULL,0x06e4f55e6bfb3e89ULL,0x16bf492bbf874eb3ULL,0x335d71a30027eccdULL}}},
  {{{0x1e4bb73ffb93a6d1ULL,0x9ef465a03f553915ULL,0xa986466f8cb39340ULL,0x344b522709d83fd6ULL}},{{0x54d1385a73cedc14ULL,0x554f9d50f1aa4237ULL,0x6c40c2c46e70eb08ULL,0x08d14481b53d311cULL}},{{0x1424438d34dfc1daULL,0x2409171b46a1ca37ULL,0x1a1c4cfb701efcc3ULL,0x3238d087fe0f487bULL}}},
  {{{0xe4e41151ef95cfa8ULL,0x5ac9a18bf328f9a7ULL,0xa74bc957b4f0312fULL,0x2a7229e81bd17e27ULL}},{{0x128b64e508a63bd9ULL,0xbc72e63f546c4584ULL,0x88cf7accb6e0e0eeULL,0x113c3d59a596d700ULL}},{{0xf4d7b2de93df79c1ULL,0xd48511fd9b630fa2ULL,0x66d2195a8ed94ca5ULL,0x1c0c0ca45eee2c44ULL}}},
  {{{0x466d86d03c2466caULL,0x8227a59ab7462664ULL,0xd2fd28964ffc5f0eULL,0x047b0867cd0bb8bcULL}},{{0xd789d21c1d4ea83cULL,0x7401f29ebae79841ULL,0xe0abd0eb46b46cb8ULL,0x28e0786cd4de5a8fULL}},{{0x7402eeab3141e20fULL,0xd768b71e6068c79bULL,0x3db2195fe3a15590ULL,0x2ae0bdb635468021ULL}}},
  {{{0xc16e17aec4c8c257ULL,0xcbe2e0daf07542ffULL,0xbfe62521350c02fbULL,0x1228614aa1224324ULL}},{{0x75e7f93077ae107aULL,0x4393dd80790be351ULL,0xdff377ea2fa44416ULL,0x1e8508e864d3a7c5ULL}},{{0xb1ec20078a1957fdULL,0x763ab46a70baa519ULL,0x7738685a419fd1cbULL,0x2a5e0a5a9db64745ULL}}},
  {{{0xc22212c67483d82eULL,0xa75cc24295d6ff8dULL,0x7992eb54a6a2ed5dULL,0x07404560d0b2cbd5ULL}},{{0x2a285911ee339ba5ULL,0x8893e0badb13c939ULL,0xd83525d7431b9b62ULL,0x25f63b980e96e6dbULL}},{{0xa15a39ed0b3d0589ULL,0xd368b459a4b900e0ULL,0x4efa56d549364219ULL,0x0b5ca2beedd7dd3eULL}}},
  {{{0xeb7ba4127d2e6354ULL,0x6986145a2941fb14ULL,0x0e3e7c6c97a14312ULL,0x1ed53f1aa1bf808fULL}},{{0xaf8ab4c0d2b2669dULL,0x7e7a7326eb971e3fULL,0xa2d3848e9ce2fc69ULL,0x29ea52e7093a43d4ULL}},{{0x1e72622bdb4569a9ULL,0x874356996d93fcdeULL,0x5c7c464758b32bc2ULL,0x105fe2acbcc84897ULL}}},
  {{{0x0653a67e86f62c0fULL,0xda058f0b6767498aULL,0xa49ef164a0280442ULL,0x348a3f44e29a1db3ULL}},{{0x4ebc09df098dddf4ULL,0x7953e2582fc1806cULL,0x4c7c4749054887c8ULL,0x0ea7f29878781fb8ULL}},{{0x9e9e28ff373a00a1ULL,0x59d68a2c32f0aeaeULL,0x030aa50eb0d116f4ULL,0x265063100e234ee0ULL}}},
  {{{0xc65436d24cba466aULL,0x461c6791d1c4df7bULL,0x44a880f485ffa101ULL,0x3fbc3cf75118c62eULL}},{{0xd77ac655ca67b1c2ULL,0x76d88fda6b1d115cULL,0x089c758c1ba6ef20ULL,0x0964db39bd4b200bULL}},{{0xbd5667e04c034a11ULL,0x5d4c63fffa29c3a1ULL,0xf6831d76df36eaa1ULL,0x255644c108880d6dULL}}},
  {{{0xafa80ea9d8392946ULL,0xb374fe3c3d852b90ULL,0x6ac7be0421200289ULL,0x20e4c096c4dd72e6ULL}},{{0x7896f449e943831eULL,0x1ce40ea3c4383e92ULL,0xb49ab8f65a18dfb3ULL,0x022f6ae3e0d1f236ULL}},{{0x3befcfdbe8dd042cULL,0x1f23c41b8459e28cULL,0x9d3df3e0c372ff8aULL,0x18dc26fa862b191eULL}}},
  {{{0x56dd436505fd7a95ULL,0xde6df28980a2b7d9ULL,0x0363df341e40f38bULL,0x07e2bca200e16abaULL}},{{0xd411d472d8dc23daULL,0xf50cfab4071be3cfULL,0x3c259a5e3e76eb62ULL,0x0ac0b7df209f51acULL}},{{0x5ed3556cb6eccdaaULL,0x5a77f234139d70b3ULL,0xfcb189da416e3bcaULL,0x0cafd03316e3da67ULL}}},
  {{{0x3ded6d76360a45beULL,0x6c429cb169faa590ULL,0x2fb017c34a83a077ULL,0x31f542859f15f500ULL}},{{0x3429130c2c719a28ULL,0x2c9ef140b71e34edULL,0x483fc18d0a310a87ULL,0x1495571d0705997cULL}},{{0x3af7365d394648aeULL,0x5cf1b21e24262136ULL,0xc0fc62acf9bb6f72ULL,0x1115c26a2fa746d9ULL}}},
  {{{0x8099beda71efd72fULL,0xd36c358a6cb42b28ULL,0xeec3d42dc5d22579ULL,0x22193d634f4398d4ULL}},{{0x69fa4c8431c72241ULL,0x3d493a2870de9ecaULL,0xfa85379fa7f96e96ULL,0x06ed1793aac4bac5ULL}},{{0x469e500151fe112eULL,0xf15b462bf229e21fULL,0xf700e5a684cc210eULL,0x208c794ee061495bULL}}},
  {{{0x42e1de787c5ac045ULL,0xdaf7f483c5ac2542ULL,0x3a179e90ac57dc06ULL,0x3ccede2a70073e55ULL}},{{0x9907bebdd515efcdULL,0x5c5759cc9d41d88aULL,0x3674aac584e9815eULL,0x256eccb4ae6815a8ULL}},{{0xfbecb087cd94ed86ULL,0xe2c856bd76367ef6ULL,0x4eb80ed90b2de128ULL,0x259f3b2f4d72a341ULL}}},
  {{{0x8aee7138a3e493efULL,0xc097e3916e39d301ULL,0x3f4edaab5fade903ULL,0x26341785bebb55d1ULL}},{{0x81743dbd685bfc78ULL,0x51e1df5405018bb4ULL,0x5e7f09f43fab73dcULL,0x300dc575584e1165ULL}},{{0xcf5e72012088079fULL,0x5ee47f6039ea45b0ULL,0x1376a4ad287da55cULL,0x15c592ab8709a775ULL}}},
  {{{0xd1ba83ae61ab349cULL,0x54c4ebfa46c6c5ddULL,0x6811f417646c4a9bULL,0x0304e5f3b22fd1e6ULL}},{{0x96b0a28615104eebULL,0xddc28384fa498de1ULL,0x2e588de186363997ULL,0x35279da4cf2bc018ULL}},{{0xd0533b7b914aa30eULL,0xf91091f7f642e389ULL,0xe768cc728d9ffd9fULL,0x3512143a077d0fa6ULL}}},
  {{{0xa64b6584aa7777b6ULL,0xa9ecd008c97413bdULL,0x42db693e89469246ULL,0x000f9bd1021c5922ULL}},{{0x0208b8d66e15fe3bULL,0xeb7cb55bbc327ae8ULL,0x63a2418e20a3ba6cULL,0x38a5ea6f82db3d5dULL}},{{0x9a649745f40e953eULL,0x9d6406d52cb622f5ULL,0x200a4cbd0f1f267cULL,0x3db51a34b6e9fe06ULL}}},
  {{{0x17c83056e2c382a1ULL,0x2f4c8b882d658eb4ULL,0x96acd13fcc26bf82ULL,0x000c6a1b1bf90012ULL}},{{0xf616d545a5d3e939ULL,0x2af7464619d365cbULL,0xf097308d468c947dULL,0x291ffc707a48e2ccULL}},{{0xd3b637e65a834971ULL,0x8fa7365afde54fe7ULL,0x118cc5ff60f24404ULL,0x1430b62cbd021f4aULL}}},
  {{{0xab3d6c0df3ce0ca0ULL,0x08144b4c79d86499ULL,0xf91d2462d75a2286ULL,0x2bf52870c017cf4eULL}},{{0xe5e5488d5162898eULL,0xe83c6c0ca21e9962ULL,0x66f17a5cce9bd5eeULL,0x0faa86932fc9ec52ULL}},{{0x6a601060296db14dULL,0xecf3cf47c1dc4442ULL,0x6a950536b5584542ULL,0x313de4b333fc8118ULL}}},
  {{{0xc2bb2bdb161c0d43ULL,0xe42240232ae44172ULL,0x305435bec7528b04ULL,0x2da4e7173aee4d48ULL}},{{0x923370757c286129ULL,0xbf9fcef7fa21e1f3ULL,0x0e1971e6add36a32ULL,0x05f07747dffb6336ULL}},{{0xb63765a7f3c491d9ULL,0xc6da1f9e3e9828c7ULL,0xde242a4e2279090dULL,0x2cca495816249692ULL}}},
  {{{0x1ff64be92cab7091ULL,0x3d79404b46d72eb9ULL,0x1710f1c5af14541aULL,0x0ebaf248a381fe31ULL}},{{0xa40aa7f2f4be8e45ULL,0x135a66ac8749ce1cULL,0xd8d76ea87865c570ULL,0x044ec20c80c90b04ULL}},{{0x4a9da72cba665450ULL,0xd5295d8e27bb7bfbULL,0x3626ca8c336dd990ULL,0x022408a1fb0b3800ULL}}},
  {{{0x8446ea40f76089b3ULL,0xdbfa50f0a581e128ULL,0xd7685cd42f8f7c21ULL,0x398f3c2662df6e9aULL}},{{0x37d44d6ed12e5836ULL,0xdd62ee99a8b6cc55ULL,0xaf6d348d1857a659ULL,0x1f9c9041980969afULL}},{{0xf749702efd480758ULL,0x323710fe973ef206ULL,0xddb2efafff6e26bfULL,0x3281013f35baa4d1ULL}}},
  {{{0x36f8bf09755e3fd1ULL,0x5d77e2be7cd25b26ULL,0xb3f18051ec66d481ULL,0x228b840f19b7f6edULL}},{{0x1e20bd7e9007dc99ULL,0x7f9c083ce884876dULL,0xb113ce50640f20f6ULL,0x2bf716d6b3cd9a18ULL}},{{0xe0f986df949e09f8ULL,0x32d8dd9249948d2eULL,0x9ae905c32961e96fULL,0x30553eb90e4d277aULL}}},
  {{{0x2acddfb558ce6fd8ULL,0xc70f8fcddfdb34a1ULL,0xfa66e72c6937e86fULL,0x385df4d2ddcdcaa5ULL}},{{0x3e7465e402206318ULL,0xf6ead3f9d9e048b3ULL,0x619112a188adb41eULL,0x2c34febcf9def460ULL}},{{0xe8a7c82fa2625b3fULL,0xaebb23cc8147e2bdULL,0xf587afa348f34bf0ULL,0x07ccc87a97eee0b3ULL}}},
  {{{0xd679b84eef1994b9ULL,0x7def28d56667062cULL,0xac3068742ec64b40ULL,0x14479d04a6999fefULL}},{{0x1bf627000bfe0e4aULL,0x1c54cb5d1844ccffULL,0x76ba72dfe568a18aULL,0x1eb61f5d4af67fbdULL}},{{0x48f5e53e337b002aULL,0xa2cd1072d615602fULL,0x6bb93f9dad34bed7ULL,0x320e9200e22d4464ULL}}},
  {{{0x5aa93dae91a2e4b9ULL,0xfaacb53728337d8aULL,0x1081dbb00247523bULL,0x397bf21666510308ULL}},{{0x8f7f76f47d9ff019ULL,0x24de8ffa0fad4008ULL,0x2018e79b576a6bc7ULL,0x158acea556828e27ULL}},{{0xe905f10b227bbf42ULL,0xc2edbfc5a426c09fULL,0xd95d18ff73154263ULL,0x040333330a351778ULL}}},
  {{{0x91a0adc20b096a81ULL,0x8ed3f92a943f4990ULL,0x09dca1eb774a58aaULL,0x3190de39a08e30d0ULL}},{{0xa186477461610158ULL,0x49dcf00c9a3f4cdcULL,0xc24bd4292b6300a8ULL,0x2353ebbae73e6b0bULL}},{{0xd86fe6c3fd5d72d6ULL,0xcb092c676b2faf59ULL,0x41de6a751b2ab6b8ULL,0x36d1c42ec123b236ULL}}},
  {{{0x6eeb8c14a580493fULL,0xa63fafe1762d0433ULL,0x2535874ab3d5feb7ULL,0x3f9fd0c9caf16f44ULL}},{{0x097b1331d5d5fdcdULL,0xb69a099bd2707e4bULL,0xa00d654aab61139bULL,0x04a51f72fbc8f91eULL}},{{0xec1ba969b57bc21aULL,0x757b333a7ffa3b3dULL,0x0e597273fe4ac666ULL,0x114d73316180d61bULL}}},
  {{{0x042ec88c94422adfULL,0x84669dfab8f97048ULL,0xdcc347c19ad69842ULL,0x293316fbfcb11e39ULL}},{{0x63d9ab3880316efeULL,0xd06d752adf2b43fcULL,0xa236c0995704aa60ULL,0x286ce110716c2974ULL}},{{0x25fd65694898efb4ULL,0x99cb620dfc63fbcdULL,0xf3a0a1e1aedec074ULL,0x097462528778299bULL}}},
  {{{0x418c3f6d880e3244ULL,0x20a933100425e4d5ULL,0x5366e37bd79dd77dULL,0x1c5640c60b10f088ULL}},{{0x062556e677ce1aeeULL,0x551bb969a99a27d8ULL,0xbd64e65f6d50ce56ULL,0x3670f79b1ebd37eaULL}},{{0x6340a6e40b2cb449ULL,0x75a66980082192d0ULL,0xf26997d2e59968b8ULL,0x1ba8ef4ddba030a2ULL}}},
  {{{0x9e81ed6bcca99ca8ULL,0xe283e6741c1c8c1aULL,0x4dcbab4c903e7d6cULL,0x144287df706d7d35ULL}},{{0xf307d19656785140ULL,0xf2359f3af40af740ULL,0x073120eaab4c104dULL,0x372a560cedb19147ULL}},{{0x0917ef782f366a32ULL,0x118e0d62997e0761ULL,0x85a794632bd1186eULL,0x3fd8af8f75a55735ULL}}},
  {{{0x45f1327d29d5bb47ULL,0x1d267c203c076406ULL,0x54568d3ebb89dbacULL,0x050c1e7fd4e0840aULL}},{{0x8918a0f53d47ef87ULL,0xd801c477ffe38754ULL,0x6f614c3c03eab522ULL,0x3e22c9f862e9d961ULL}},{{0x0a6c3b558ff7fb9dULL,0x916c06f103a297bfULL,0xfe331bfa4f477e45ULL,0x02fda085e0882d39ULL}}},
  {{{0xe00d560c1922bd80ULL,0xbe5fb99f7823e7ceULL,0x9b8ab20ee58d07d2ULL,0x3cf282a530973229ULL}},{{0x61f5e4a62789d305ULL,0xe79e5db989d235c2ULL,0x779fd5723b0e4c8cULL,0x1fb84c68e272aacdULL}},{{0x9f8bc8af370f0e1fULL,0x628b777da9608e7aULL,0x56f3fce27af86d3dULL,0x3ed0ea844bce3f7cULL}}},
  {{{0xa81ca9ad3596718eULL,0xa2e243ebc26d8786ULL,0xbdd0c75e49311133ULL,0x0491f56bad943b95ULL}},{{0x662a89747f07eb48ULL,0xbfd2949f2198be29ULL,0x61faee803ba6ad21ULL,0x0d92b19df57965e5ULL}},{{0x74c0170dcb26b9a3ULL,0x6e043841ae89ad9cULL,0x9c21986513bb6c95ULL,0x32c850785ef8c550ULL}}},
  {{{0xed4d002f16bc787fULL,0x06ebf8cb07196aa9ULL,0x14eb45e365573e2bULL,0x25032cef4a7000efULL}},{{0x3b118891deafe0c1ULL,0x13f9c32f82aa94f5ULL,0xa02a82d122209fb7ULL,0x1ce89d10d60cb6f5ULL}},{{0xf371d6ce33fea695ULL,0x5505eca4ffdb4f3aULL,0x2c1c430f4a00cc14ULL,0x18679130f2053d1bULL}}},
  {{{0x8f93a25b2e5c3ac9ULL,0xf65309c16f7c2122ULL,0x448ec71a1bb9c43fULL,0x1c9901bfdaead7bbULL}},{{0xce3903ea34b01eb4ULL,0x3743ef7a61a75b0dULL,0xc4b3b804343ab52cULL,0x21525c6921c10348ULL}},{{0x3e58ceccf33d9fd6ULL,0x0a4405f0f3f9ecddULL,0x5e439182f7d467e3ULL,0x2fdbb7666a8d4e93ULL}}},
  {{{0xd95c47374d92d769ULL,0x6e7a4d28152762eeULL,0x70aca0ccc8b1e64cULL,0x00224355557620cdULL}},{{0xd546a4caccd86c58ULL,0x94e61f808ca9e38fULL,0xd4dcc0ca96cc3b32ULL,0x19e80175f12ee906ULL}},{{0xdd1c43055a2df184ULL,0x21ea7e74be932b7bULL,0xeb9bd9f6301efde3ULL,0x204f1be7c3153361ULL}}},
  {{{0x669a1bfa4452e5b9ULL,0xb50119f9ba5913e4ULL,0x376e862381f50e26ULL,0x2fb4218313d636abULL}},{{0x79c6708a2d8292c2ULL,0x2684a5342d6e29c4ULL,0x77efae4ea0f85e94ULL,0x26a86c00b42234b5ULL}},{{0xacb8a62ec21f1790ULL,0xa532d1c96fd777b0ULL,0xbce6beb99cd715c5ULL,0x2205f95b96860426ULL}}},
  {{{0xeea18d332c6ba201ULL,0x7e49750fe17b0c48ULL,0x84b958e355658851ULL,0x1af476c6c11beb7cULL}},{{0xac7444171b9ed2a4ULL,0xb13b491258203302ULL,0x7bbd82c67d980d63ULL,0x288fef4833b6612bULL}},{{0xdb2f5426a3ce3a28ULL,0xe35f66b7b35fd095ULL,0xc2911efe8acaa8d3ULL,0x20adef5e2b2bc83fULL}}},
  {{{0x668c5c60dc165271ULL,0xa20833455f8c9082ULL,0x7ea98ee735477650ULL,0x3742df583c401d58ULL}},{{0x76bb56ba0777dd32ULL,0x57ae5691adfd5bb6ULL,0xc25cd5eaaad89961ULL,0x0ba64c73d78f268aULL}},{{0x77f195a810966117ULL,0x5a4fa67cbe740274ULL,0xc195daea12525beaULL,0x116979774227425cULL}}},
  {{{0x5d58cfd09c2210bbULL,0x4ba345d05d37c73aULL,0x6e8d9dd33f2a5189ULL,0x1a0e98c3ef88d4cfULL}},{{0x561643bef1c2f375ULL,0xd28ed380885331acULL,0xba76d3ad613a46f5ULL,0x3ef76bf14ed05706ULL}},{{0x0fe0d46abf50f962ULL,0xb8c8c797af9d04b6ULL,0xd19d4f33430a128fULL,0x11ffb1bc451c07d1ULL}}},
};
static const fp POSEIDON_MDS_M[3][3] = {
  {{{0x7c1a669d208e8b4dULL,0x5f51868647bdf2a3ULL,0x00fcf9354819f613ULL,0x3103a7de3b678ebdULL}},{{0xd02c6b7336d40cfaULL,0x3a1a0851864fb4a7ULL,0x2282de236a32af60ULL,0x0e799762bd549615ULL}},{{0xb3624a21289b4249ULL,0xca6c5877b9c3c7c5ULL,0xb02a2a0100ebb202ULL,0x117cb780c908530aULL}}},
  {{{0xe3ff3f5c313a6a34ULL,0x51c6f61bd721544dULL,0x8ed31b47cae66704ULL,0x02087f41039c75bbULL}},{{0xd2f9d522444ac1a0ULL,0xe69ac4d3b9d1c5a0ULL,0x6edec07987aaee83ULL,0x1e43c65722df71bdULL}},{{0x10a0d86e38d77e7bULL,0xf0b93da384af65e0ULL,0x62ed3679f9a91794ULL,0x2345494383dd3fb8ULL}}},
  {{{0x1ff15b66b7bbe66dULL,0x75ecdd64110a734fULL,0x78f0280d37007108ULL,0x376408280c7418bcULL}},{{0x934d00845da6461dULL,0x930aa4624cdae4b4ULL,0xdcd1ebac0098612dULL,0x2de64334636be38dULL}},{{0x0f957fede68e9322ULL,0x14ac4b874d7324dbULL,0x4007b97b032e6d5dULL,0x22011675ded37456ULL}}},
};
#endif
```

## Appendix E: measurement data (per round count r and width w, and the control; keys as in Section 8)

```json
{"r7/w16":{"K":2000,"censored":0,"c_hat":0.9984,"c_lo":0.9554,"c_hi":1.0427,"mean_t_over_sqrt_piN_2":0.9979,"dp_theta":0.0625,"dp_gaps":37919,"theta_x_mean_gap":0.9489,"theta_x_mean_detection_delay":0.967,"max_gap_x_theta":10.0,"c_hat_gamma_old":1.0009,"c_lo_gamma_old":0.9575,"c_hi_gamma_old":1.0452},
"r7/w20":{"K":2000,"censored":0,"c_hat":1.0093,"c_lo":0.9657,"c_hi":1.0542,"mean_t_over_sqrt_piN_2":1.0056,"dp_theta":0.0625,"dp_gaps":159596,"theta_x_mean_gap":0.9856,"theta_x_mean_detection_delay":0.9602,"max_gap_x_theta":12.0,"c_hat_gamma_old":1.0099,"c_lo_gamma_old":0.9661,"c_hi_gamma_old":1.0546},
"r7/w24":{"K":2000,"censored":0,"c_hat":1.0381,"c_lo":0.9932,"c_hi":1.0842,"mean_t_over_sqrt_piN_2":0.9804,"dp_theta":0.25,"dp_gaps":2515121,"theta_x_mean_gap":0.9989,"theta_x_mean_detection_delay":0.7759,"max_gap_x_theta":13.5,"n":4131,"S":4164,"gmax":73,"mcap":1532,"lemma_bound":0.39,"success":825,"success_frac":0.4125,"success_ci":[0.3911,0.4342],"pairs_verified":825,"status":{"steps":1174,"found":825,"start-on-cycle":1},
"frac_t_le_n":0.4095,"model_t_le_n":0.3987,"max_gap_vs_gmax":"54 / 73","c_hat_gamma_old":1.0382,"c_lo_gamma_old":0.9932,"c_hi_gamma_old":1.0842},
"r7/w28":{"K":600,"censored":0,"c_hat":1.0129,"c_lo":0.934,"c_hi":1.0961,"mean_t_over_sqrt_piN_2":0.9853,"dp_theta":0.0625,"dp_gaps":759936,"theta_x_mean_gap":0.9967,"theta_x_mean_detection_delay":0.9147,"max_gap_x_theta":14.38,"n":16518,"S":16648,"gmax":291,"mcap":1529,"lemma_bound":0.39004,"success":253,"success_frac":0.4217,"success_ci":[0.3828,0.4616],"pairs_verified":253,"status":{"steps":347,"found":253},
"frac_t_le_n":0.415,"model_t_le_n":0.3984,"max_gap_vs_gmax":"230 / 291","c_hat_gamma_old":1.0129,"c_lo_gamma_old":0.9335,"c_hi_gamma_old":1.0956},
"r7/w32":{"K":200,"censored":0,"c_hat":0.921,"c_lo":0.7992,"c_hi":1.0546,"mean_t_over_sqrt_piN_2":1.0488,"dp_theta":0.015625,"dp_gaps":268646,"theta_x_mean_gap":1.0006,"theta_x_mean_detection_delay":0.9405,"max_gap_x_theta":12.19,"n":66060,"S":66577,"gmax":1162,"mcap":1528,"lemma_bound":0.39,"success":63,"success_frac":0.315,"success_ci":[0.2546,0.3823],"pairs_verified":63,"status":{"steps":137,"found":63},
"frac_t_le_n":0.32,"model_t_le_n":0.3983,"max_gap_vs_gmax":"780 / 1162","c_hat_gamma_old":0.921,"c_lo_gamma_old":0.7978,"c_hi_gamma_old":1.0529},
"r7/w36":{"K":60,"censored":0,"c_hat":1.0809,"c_lo":0.8299,"c_hi":1.3779,"mean_t_over_sqrt_piN_2":0.9693,"dp_theta":0.00390625,"dp_gaps":74216,"theta_x_mean_gap":1.0041,"theta_x_mean_detection_delay":0.8857,"max_gap_x_theta":14.4,"n":264230,"S":266295,"gmax":4645,"mcap":1528,"lemma_bound":0.39,"success":22,"success_frac":0.3667,"success_ci":[0.2562,0.4932],"pairs_verified":22,"status":{"found":22,"steps":38},
"frac_t_le_n":0.3667,"model_t_le_n":0.3983,"max_gap_vs_gmax":"3686 / 4645","c_hat_gamma_old":1.0809,"c_lo_gamma_old":0.8248,"c_hi_gamma_old":1.371},
"r7/w40":{"K":12,"censored":0,"c_hat":0.8612,"c_lo":0.4612,"c_hi":1.4444,"mean_t_over_sqrt_piN_2":1.1331,"dp_theta":0.0009765625,"dp_gaps":17490,"theta_x_mean_gap":0.9962,"theta_x_mean_detection_delay":1.0598,"max_gap_x_theta":11.3,"n":1056909,"S":1065166,"gmax":18578,"mcap":1528,"lemma_bound":0.39,"success":3,"success_frac":0.25,"success_ci":[0.0889,0.5323],"pairs_verified":3,"status":{"steps":9,"found":3},
"frac_t_le_n":0.1667,"model_t_le_n":0.3983,"max_gap_vs_gmax":"11571 / 18578","c_hat_gamma_old":0.8612,"c_lo_gamma_old":0.4445,"c_hi_gamma_old":1.4127},
"r23/w16":{"K":2000,"censored":0,"c_hat":0.9928,"c_lo":0.9501,"c_hi":1.0369,"mean_t_over_sqrt_piN_2":1.0068,"dp_theta":0.0625,"dp_gaps":37845,"theta_x_mean_gap":0.9615,"theta_x_mean_detection_delay":0.8829,"max_gap_x_theta":10.19,"c_hat_gamma_old":0.9952,"c_lo_gamma_old":0.9521,"c_hi_gamma_old":1.0393},
"r23/w20":{"K":2000,"censored":0,"c_hat":1.0156,"c_lo":0.9717,"c_hi":1.0607,"mean_t_over_sqrt_piN_2":0.9929,"dp_theta":0.0625,"dp_gaps":157457,"theta_x_mean_gap":0.9855,"theta_x_mean_detection_delay":0.9095,"max_gap_x_theta":11.06,"c_hat_gamma_old":1.0162,"c_lo_gamma_old":0.9721,"c_hi_gamma_old":1.0612},
"r23/w24":{"K":2000,"censored":0,"c_hat":0.9763,"c_lo":0.9341,"c_hi":1.0197,"mean_t_over_sqrt_piN_2":1.0064,"dp_theta":0.25,"dp_gaps":2581230,"theta_x_mean_gap":0.9993,"theta_x_mean_detection_delay":0.7409,"max_gap_x_theta":16.0,"n":4131,"S":4164,"gmax":73,"mcap":1532,"lemma_bound":0.39,"success":805,"success_frac":0.4025,"success_ci":[0.3812,0.4242],"pairs_verified":805,"status":{"steps":1194,"found":805,"start-on-cycle":1},
"frac_t_le_n":0.4,"model_t_le_n":0.3987,"max_gap_vs_gmax":"64 / 73","c_hat_gamma_old":0.9764,"c_lo_gamma_old":0.9341,"c_hi_gamma_old":1.0197},
"r23/w28":{"K":600,"censored":0,"c_hat":0.9337,"c_lo":0.861,"c_hi":1.0104,"mean_t_over_sqrt_piN_2":1.0297,"dp_theta":0.0625,"dp_gaps":791914,"theta_x_mean_gap":0.9997,"theta_x_mean_detection_delay":0.9356,"max_gap_x_theta":15.06,"n":16518,"S":16648,"gmax":291,"mcap":1529,"lemma_bound":0.39004,"success":235,"success_frac":0.3917,"success_ci":[0.3534,0.4313],"pairs_verified":235,"status":{"steps":365,"found":235},
"frac_t_le_n":0.385,"model_t_le_n":0.3984,"max_gap_vs_gmax":"241 / 291","c_hat_gamma_old":0.9338,"c_lo_gamma_old":0.8605,"c_hi_gamma_old":1.0099},
"r23/w32":{"K":200,"censored":0,"c_hat":1.0152,"c_lo":0.881,"c_hi":1.1625,"mean_t_over_sqrt_piN_2":0.9967,"dp_theta":0.015625,"dp_gaps":255611,"theta_x_mean_gap":0.9993,"theta_x_mean_detection_delay":0.9913,"max_gap_x_theta":14.22,"n":66060,"S":66577,"gmax":1162,"mcap":1528,"lemma_bound":0.39,"success":77,"success_frac":0.385,"success_ci":[0.3203,0.454],"pairs_verified":77,"status":{"found":77,"steps":123},
"frac_t_le_n":0.385,"model_t_le_n":0.3983,"max_gap_vs_gmax":"910 / 1162","c_hat_gamma_old":1.0152,"c_lo_gamma_old":0.8794,"c_hi_gamma_old":1.1607},
"r23/w36":{"K":60,"censored":0,"c_hat":0.9243,"c_lo":0.7097,"c_hi":1.1783,"mean_t_over_sqrt_piN_2":1.0526,"dp_theta":0.00390625,"dp_gaps":81083,"theta_x_mean_gap":0.9984,"theta_x_mean_detection_delay":0.8041,"max_gap_x_theta":11.44,"n":264230,"S":266295,"gmax":4645,"mcap":1528,"lemma_bound":0.39,"success":25,"success_frac":0.4167,"success_ci":[0.3006,0.5427],"pairs_verified":25,"status":{"steps":35,"found":25},
"frac_t_le_n":0.4167,"model_t_le_n":0.3983,"max_gap_vs_gmax":"2929 / 4645","c_hat_gamma_old":0.9243,"c_lo_gamma_old":0.7053,"c_hi_gamma_old":1.1725},
"r23/w40":{"K":12,"censored":0,"c_hat":0.9084,"c_lo":0.4864,"c_hi":1.5235,"mean_t_over_sqrt_piN_2":1.023,"dp_theta":0.0009765625,"dp_gaps":15626,"theta_x_mean_gap":1.0064,"theta_x_mean_detection_delay":1.6243,"max_gap_x_theta":9.03,"n":1056909,"S":1065166,"gmax":18578,"mcap":1528,"lemma_bound":0.39,"success":5,"success_frac":0.4167,"success_ci":[0.1933,0.6805],"pairs_verified":5,"status":{"steps":7,"found":5},
"frac_t_le_n":0.4167,"model_t_le_n":0.3983,"max_gap_vs_gmax":"9245 / 18578","c_hat_gamma_old":0.9084,"c_lo_gamma_old":0.4688,"c_hi_gamma_old":1.49},
"r56/w16":{"K":2000,"censored":0,"c_hat":1.0206,"c_lo":0.9766,"c_hi":1.0658,"mean_t_over_sqrt_piN_2":0.9919,"dp_theta":0.0625,"dp_gaps":37361,"theta_x_mean_gap":0.9589,"theta_x_mean_detection_delay":0.8997,"max_gap_x_theta":10.69,"c_hat_gamma_old":1.0231,"c_lo_gamma_old":0.9787,"c_hi_gamma_old":1.0684},
"r56/w20":{"K":2000,"censored":0,"c_hat":0.9813,"c_lo":0.9389,"c_hi":1.0249,"mean_t_over_sqrt_piN_2":1.0089,"dp_theta":0.0625,"dp_gaps":159822,"theta_x_mean_gap":0.9874,"theta_x_mean_detection_delay":0.9261,"max_gap_x_theta":11.12,"c_hat_gamma_old":0.9819,"c_lo_gamma_old":0.9393,"c_hi_gamma_old":1.0254},
"r56/w24":{"K":2000,"censored":0,"c_hat":0.9972,"c_lo":0.9541,"c_hi":1.0415,"mean_t_over_sqrt_piN_2":1.002,"dp_theta":0.25,"dp_gaps":2567789,"theta_x_mean_gap":1.0,"theta_x_mean_detection_delay":0.7229,"max_gap_x_theta":14.5,"n":4131,"S":4164,"gmax":73,"mcap":1532,"lemma_bound":0.39,"success":793,"success_frac":0.3965,"success_ci":[0.3753,0.4181],"pairs_verified":793,"status":{"found":793,"steps":1206,"start-on-cycle":1},
"frac_t_le_n":0.394,"model_t_le_n":0.3987,"max_gap_vs_gmax":"58 / 73","c_hat_gamma_old":0.9973,"c_lo_gamma_old":0.9541,"c_hi_gamma_old":1.0415},
"r56/w28":{"K":600,"censored":0,"c_hat":1.0384,"c_lo":0.9575,"c_hi":1.1237,"mean_t_over_sqrt_piN_2":0.9821,"dp_theta":0.0625,"dp_gaps":756376,"theta_x_mean_gap":0.9983,"theta_x_mean_detection_delay":0.9909,"max_gap_x_theta":17.44,"n":16518,"S":16648,"gmax":291,"mcap":1529,"lemma_bound":0.39004,"success":247,"success_frac":0.4117,"success_ci":[0.373,0.4515],"pairs_verified":247,"status":{"found":247,"steps":353},
"frac_t_le_n":0.4067,"model_t_le_n":0.3984,"max_gap_vs_gmax":"279 / 291","c_hat_gamma_old":1.0384,"c_lo_gamma_old":0.957,"c_hi_gamma_old":1.1231},
"r56/w32":{"K":200,"censored":0,"c_hat":1.039,"c_lo":0.9015,"c_hi":1.1897,"mean_t_over_sqrt_piN_2":0.9826,"dp_theta":0.015625,"dp_gaps":251787,"theta_x_mean_gap":1.0001,"theta_x_mean_detection_delay":0.9639,"max_gap_x_theta":12.95,"n":66060,"S":66577,"gmax":1162,"mcap":1528,"lemma_bound":0.39,"success":85,"success_frac":0.425,"success_ci":[0.3585,0.4943],"pairs_verified":85,"status":{"found":85,"steps":115},
"frac_t_le_n":0.425,"model_t_le_n":0.3983,"max_gap_vs_gmax":"829 / 1162","c_hat_gamma_old":1.039,"c_lo_gamma_old":0.8999,"c_hi_gamma_old":1.1878},
"r56/w36":{"K":60,"censored":0,"c_hat":0.9004,"c_lo":0.6914,"c_hi":1.1479,"mean_t_over_sqrt_piN_2":1.0557,"dp_theta":0.00390625,"dp_gaps":80749,"theta_x_mean_gap":1.0052,"theta_x_mean_detection_delay":1.015,"max_gap_x_theta":11.5,"n":264230,"S":266295,"gmax":4645,"mcap":1528,"lemma_bound":0.39,"success":22,"success_frac":0.3667,"success_ci":[0.2562,0.4932],"pairs_verified":22,"status":{"steps":38,"found":22},
"frac_t_le_n":0.3667,"model_t_le_n":0.3983,"max_gap_vs_gmax":"2945 / 4645","c_hat_gamma_old":0.9004,"c_lo_gamma_old":0.6871,"c_hi_gamma_old":1.1422},
"r56/w40":{"K":12,"censored":0,"c_hat":0.7793,"c_lo":0.4173,"c_hi":1.307,"mean_t_over_sqrt_piN_2":1.1831,"dp_theta":0.0009765625,"dp_gaps":18247,"theta_x_mean_gap":0.9972,"theta_x_mean_detection_delay":0.9061,"max_gap_x_theta":11.74,"n":1056909,"S":1065166,"gmax":18578,"mcap":1528,"lemma_bound":0.39,"success":3,"success_frac":0.25,"success_ci":[0.0889,0.5323],"pairs_verified":3,"status":{"steps":9,"found":3},
"frac_t_le_n":0.25,"model_t_le_n":0.3983,"max_gap_vs_gmax":"12026 / 18578","c_hat_gamma_old":0.7793,"c_lo_gamma_old":0.4022,"c_hi_gamma_old":1.2782},
"ctrl/w16":{"K":10000,"censored":0,"c_hat":0.995,"c_lo":0.9756,"c_hi":1.0145,"mean_t_over_sqrt_piN_2":1.0002,"dp_theta":0.0625,"dp_gaps":190180,"theta_x_mean_gap":0.9496,"theta_x_mean_detection_delay":0.9451,"max_gap_x_theta":13.5,"c_hat_gamma_old":0.9974,"c_lo_gamma_old":0.978,"c_hi_gamma_old":1.0171},
"ctrl/w20":{"K":10000,"censored":0,"c_hat":1.0029,"c_lo":0.9833,"c_hi":1.0226,"mean_t_over_sqrt_piN_2":0.9971,"dp_theta":0.0625,"dp_gaps":788588,"theta_x_mean_gap":0.9889,"theta_x_mean_detection_delay":0.9303,"max_gap_x_theta":15.94,"c_hat_gamma_old":1.0035,"c_lo_gamma_old":0.9839,"c_hi_gamma_old":1.0232},
"ctrl/w24":{"K":10000,"censored":0,"c_hat":0.998,"c_lo":0.9785,"c_hi":1.0177,"mean_t_over_sqrt_piN_2":0.9998,"dp_theta":0.25,"dp_gaps":12820668,"theta_x_mean_gap":0.9992,"theta_x_mean_detection_delay":0.7474,"max_gap_x_theta":15.0,"n":4131,"S":4164,"gmax":73,"mcap":1532,"lemma_bound":0.39,"success":4041,"success_frac":0.4041,"success_ci":[0.3945,0.4138],"pairs_verified":4041,"status":{"steps":5958,"found":4041,"start-on-cycle":1},
"frac_t_le_n":0.4006,"model_t_le_n":0.3987,"max_gap_vs_gmax":"60 / 73","c_hat_gamma_old":0.9981,"c_lo_gamma_old":0.9787,"c_hi_gamma_old":1.0178},
"ctrl/w28":{"K":3000,"censored":0,"c_hat":1.0101,"c_lo":0.9743,"c_hi":1.0466,"mean_t_over_sqrt_piN_2":0.9942,"dp_theta":0.0625,"dp_gaps":3821070,"theta_x_mean_gap":1.0003,"theta_x_mean_detection_delay":0.9466,"max_gap_x_theta":16.0,"n":16518,"S":16648,"gmax":291,"mcap":1529,"lemma_bound":0.39004,"success":1226,"success_frac":0.4087,"success_ci":[0.3912,0.4264],"pairs_verified":1226,"status":{"steps":1774,"found":1226},
"frac_t_le_n":0.4067,"model_t_le_n":0.3984,"max_gap_vs_gmax":"256 / 291","c_hat_gamma_old":1.0101,"c_lo_gamma_old":0.9743,"c_hi_gamma_old":1.0466},
"ctrl/w32":{"K":1000,"censored":0,"c_hat":1.0065,"c_lo":0.9454,"c_hi":1.0701,"mean_t_over_sqrt_piN_2":0.9926,"dp_theta":0.015625,"dp_gaps":1276357,"theta_x_mean_gap":0.9965,"theta_x_mean_detection_delay":0.966,"max_gap_x_theta":14.45,"n":66060,"S":66577,"gmax":1162,"mcap":1528,"lemma_bound":0.39,"success":410,"success_frac":0.41,"success_ci":[0.3799,0.4408],"pairs_verified":410,"status":{"steps":590,"found":410},
"frac_t_le_n":0.41,"model_t_le_n":0.3983,"max_gap_vs_gmax":"925 / 1162","c_hat_gamma_old":1.0065,"c_lo_gamma_old":0.945,"c_hi_gamma_old":1.0698},
"ctrl/w36":{"K":300,"censored":0,"c_hat":1.0573,"c_lo":0.9421,"c_hi":1.1815,"mean_t_over_sqrt_piN_2":0.9907,"dp_theta":0.00390625,"dp_gaps":380924,"theta_x_mean_gap":0.9998,"theta_x_mean_detection_delay":1.029,"max_gap_x_theta":12.16,"n":264230,"S":266295,"gmax":4645,"mcap":1528,"lemma_bound":0.39,"success":120,"success_frac":0.4,"success_ci":[0.3462,0.4564],"pairs_verified":120,"status":{"steps":180,"found":120},
"frac_t_le_n":0.4,"model_t_le_n":0.3983,"max_gap_vs_gmax":"3112 / 4645","c_hat_gamma_old":1.0573,"c_lo_gamma_old":0.941,"c_hi_gamma_old":1.1802},
"ctrl/w40":{"K":60,"censored":0,"c_hat":0.8836,"c_lo":0.6785,"c_hi":1.1265,"mean_t_over_sqrt_piN_2":1.0975,"dp_theta":0.0009765625,"dp_gaps":85018,"theta_x_mean_gap":0.9928,"theta_x_mean_detection_delay":0.9948,"max_gap_x_theta":12.78,"n":1056909,"S":1065166,"gmax":18578,"mcap":1528,"lemma_bound":0.39,"success":17,"success_frac":0.2833,"success_ci":[0.1851,0.4077],"pairs_verified":17,"status":{"steps":43,"found":17},
"frac_t_le_n":0.2833,"model_t_le_n":0.3983,"max_gap_vs_gmax":"13091 / 18578","c_hat_gamma_old":0.8836,"c_lo_gamma_old":0.6743,"c_hi_gamma_old":1.1209}}
```

## Appendix F: measurement jobs, seeds and per-job records (raw per-trial files are kept by the participant; see Section 8)

Every job is `lmeas fam 0 r w T h S mcap gmax K seedbase` with fam l (line map, r = 7, 23, 56) or c (control, r = 23 parameters). Parameters per width (identical for all round counts and the control):

| w | T | h | S | mcap | gmax | K per job | jobs per round count |
|---|---|---|---|---|---|---|---|
| 16 | 16 | 8 | 1024 | 100000 | 4096 | 2000 | 1 |
| 20 | 64 | 10 | 4096 | 100000 | 4096 | 1000 | 2 |
| 24 | 1024 | 12 | 4164 | 1532 | 73 | 500 | 4 |
| 28 | 1024 | 14 | 16648 | 1529 | 291 | 150 | 4 |
| 32 | 1024 | 16 | 66577 | 1528 | 1162 | 50 | 4 |
| 36 | 1024 | 18 | 266295 | 1528 | 4645 | 10 | 6 |
| 40 | 1024 | 20 | 1065166 | 1528 | 18578 | 2 | 6 |

Per job (run: r7, r23, r56 or ctrl; job = file name without .jsonl, chunk number last; found = trials whose search returned a verified pair; sum_t = sum of the first-repeat indices; sum_evals = the search's evaluations; sha256_16 = first 16 hex digits of the SHA-256 of the raw file). Control jobs use K = 5x the line K and seedbase + 5. SHA-256 over the concatenation of the 108 full digests: 9f1406161facbdc83921532ae4cc47d56dc14346ec3711e526988e432725a548.

```
run,job,r,w,K,seedbase,found,sum_t,sum_evals,sha256_16
r7,line_w16_c0,7,16,2000,307160,1849,640324,777773,4fea9fd951ebb69c
r7,line_w20_c0,7,20,1000,307200,976,1281987,1367354,4a4c0cba170fd39e
r7,line_w20_c1,7,20,1000,307201,977,1299260,1382750,c40d62ddbdb488e7
r7,line_w24_c0,7,24,500,307240,202,2572298,1778272,28ea2034dffb8da7
r7,line_w24_c1,7,24,500,307241,215,2534520,1765072,93e5dd0d2adcee26
r7,line_w24_c2,7,24,500,307242,223,2424553,1751227,c613fe23e9c7f5b0
r7,line_w24_c3,7,24,500,307243,185,2534247,1797751,48f9d12ccd6f296c
r7,line_w28_c0,7,28,150,307280,66,2927942,2065045,58523a1c544f4113
r7,line_w28_c1,7,28,150,307281,63,3019975,2126833,b757b1d183fcca2b
r7,line_w28_c2,7,28,150,307282,60,3180451,2105012,43d1d3b09ef79cd0
r7,line_w28_c3,7,28,150,307283,64,3010560,2082495,aa75f1f4963fb404
r7,line_w32_c0,7,32,50,307320,14,4836291,2876628,255fd443dd322c87
r7,line_w32_c1,7,32,50,307321,17,3991744,2861795,b4f6de0c205479ae
r7,line_w32_c2,7,32,50,307322,15,4316589,2945336,e39d06f4039cb499
r7,line_w32_c3,7,32,50,307323,17,4084559,2976999,1eeafaf2ff4f8773
r7,line_w36_c0,7,36,10,307360,4,2408700,1995651,72867aeaef381381
r7,line_w36_c1,7,36,10,307361,2,3670774,2461438,cfb80e120c3438cc
r7,line_w36_c2,7,36,10,307362,4,2828951,2255179,dcacffb6cc9b4658
r7,line_w36_c3,7,36,10,307363,4,3889169,2445021,e2879c629d96b448
r7,line_w36_c4,7,36,10,307364,2,3459123,2362900,6b94868f17bc9e8c
r7,line_w36_c5,7,36,10,307365,6,2851606,2084754,b85ff17f3ab1b115
r7,line_w40_c0,7,40,2,307400,0,2264890,2130332,ebb087a1b9eebf23
r7,line_w40_c1,7,40,2,307401,1,2532135,1776769,97094d3c1b0bf237
r7,line_w40_c2,7,40,2,307402,1,2920513,1947184,ab23cda7fca43e09
r7,line_w40_c3,7,40,2,307403,0,3835189,2130332,3ab4e55f0a643fcb
r7,line_w40_c4,7,40,2,307404,0,4103507,2130332,f592b185fa632dc3
r7,line_w40_c5,7,40,2,307405,1,2212518,2128339,ba8afad44185f36f
r23,line_w16_c0,23,16,2000,323160,1849,646069,786457,706c8427f30369b7
r23,line_w20_c0,23,20,1000,323200,977,1258063,1347546,27974f0126dac6f0
r23,line_w20_c1,23,20,1000,323201,977,1290494,1380895,d3a3318b7bfbf605
r23,line_w24_c0,23,24,500,323240,197,2613015,1754339,35de230707eb6bc6
r23,line_w24_c1,23,24,500,323241,203,2561252,1765949,913dc7ddc356a2be
r23,line_w24_c2,23,24,500,323242,201,2561313,1769175,b380d263b2ab2ab8
r23,line_w24_c3,23,24,500,323243,204,2597502,1762168,892653351c63d857
r23,line_w28_c0,23,28,150,323280,61,3008985,2092747,e40b55a739cb12e3
r23,line_w28_c1,23,28,150,323281,56,3333728,2210679,4d97c806a43544f7
r23,line_w28_c2,23,28,150,323282,60,3275361,2142505,e418eef6830942e2
r23,line_w28_c3,23,28,150,323283,58,3067911,2082366,914583d4645e0ae5
r23,line_w32_c0,23,32,50,323320,24,3757788,2761649,c9808b8013aef85c
r23,line_w32_c1,23,32,50,323321,18,4356644,2881246,8612bc6df2e6a195
r23,line_w32_c2,23,32,50,323322,19,3979458,2850746,0e298af0cb304a57
r23,line_w32_c3,23,32,50,323323,16,4279230,2841211,c9480d69f3cfcd47
r23,line_w36_c0,23,36,10,323360,1,4833316,2487199,64a83385b536d0e1
r23,line_w36_c1,23,36,10,323361,6,2872433,2247177,4a65a60ec79901c5
r23,line_w36_c2,23,36,10,323362,4,3135908,2364666,7ecaa2e23c7a360f
r23,line_w36_c3,23,36,10,323363,6,2824535,2072356,a63c175abdaf6b28
r23,line_w36_c4,23,36,10,323364,3,3912500,2458537,66b47189b2c8d2d7
r23,line_w36_c5,23,36,10,323365,5,3171580,2345122,7d9d62eb3ae7a4a9
r23,line_w40_c0,23,40,2,323400,1,2258432,1689896,18d3515962b8a8eb
r23,line_w40_c1,23,40,2,323401,0,3715193,2130332,02d28dff42a9e142
r23,line_w40_c2,23,40,2,323402,1,1724316,1463848,d664b7c433cd3c62
r23,line_w40_c3,23,40,2,323403,0,4545162,2130332,fa5e80d363ccb5e0
r23,line_w40_c4,23,40,2,323404,1,2136655,1210843,328cd8251ae2d825
r23,line_w40_c5,23,40,2,323405,2,1753958,1756268,33dbc9180232d18a
r56,line_w16_c0,56,16,2000,356160,1852,636493,769400,512820c4b6c693b4
r56,line_w20_c0,56,20,1000,356200,979,1303472,1386082,28551a5d03f94a39
r56,line_w20_c1,56,20,1000,356201,980,1286147,1361739,a57f525e109d3c0e
r56,line_w24_c0,56,24,500,356240,210,2501062,1761941,a2504bcf91ab9952
r56,line_w24_c1,56,24,500,356241,197,2591508,1763282,ec2846ea2de43ff8
r56,line_w24_c2,56,24,500,356242,193,2580689,1769193,72eed5cf3265fb68
r56,line_w24_c3,56,24,500,356243,193,2614197,1804690,4b42d3811c4ad30e
r56,line_w28_c0,56,28,150,356280,70,2943438,2081253,ea9b77427f186192
r56,line_w28_c1,56,28,150,356281,55,3047693,2172757,86fe42d6191f250c
r56,line_w28_c2,56,28,150,356282,62,3099161,2192759,e895701f1840f637
r56,line_w28_c3,56,28,150,356283,60,3009849,2122652,f74253cdaa4ac10e
r56,line_w32_c0,56,32,50,356320,25,3776510,2643931,dd66c8b224bbcd3e
r56,line_w32_c1,56,32,50,356321,23,3798315,2911613,3dba1dd0dde7b05f
r56,line_w32_c2,56,32,50,356322,20,4112815,2842995,d76797beaffcc7eb
r56,line_w32_c3,56,32,50,356323,17,4454147,2954734,c0074a84ce14d253
r56,line_w36_c0,56,36,10,356360,3,4047861,2364600,6b39a3fe70e7b64d
r56,line_w36_c1,56,36,10,356361,2,3980888,2587114,2ae3740f28731b07
r56,line_w36_c2,56,36,10,356362,5,2710707,1917636,1695f73c8bfed156
r56,line_w36_c3,56,36,10,356363,3,3621047,2366656,40d71302cd8bf10a
r56,line_w36_c4,56,36,10,356364,3,3431666,2352867,031cff61f0c7cc61
r56,line_w36_c5,56,36,10,356365,6,3018886,2278699,c4dcb4ae7c74741b
r56,line_w40_c0,56,40,2,356400,1,2941368,1604533,a97b81c3f27dd4b1
r56,line_w40_c1,56,40,2,356401,0,2814559,2130332,6391c67e13b1596b
r56,line_w40_c2,56,40,2,356402,0,4030180,2130332,27e1f305a602f914
r56,line_w40_c3,56,40,2,356403,0,3445468,2130332,a8785519c5416476
r56,line_w40_c4,56,40,2,356404,1,2924900,1563278,74c472120faa37a1
r56,line_w40_c5,56,40,2,356405,1,2502096,2081246,17cffc2a824e9a2b
ctrl,ctrl_w16_c0,23,16,10000,323165,9283,3209178,3885209,9615a20a8e02fde7
ctrl,ctrl_w20_c0,23,20,5000,323205,4893,6357981,6754734,7563d019b3f89181
ctrl,ctrl_w20_c1,23,20,5000,323206,4911,6438971,6769172,e1865ea280957868
ctrl,ctrl_w24_c0,23,24,2500,323245,1023,12809237,8854485,3dfe1e896b0266d1
ctrl,ctrl_w24_c1,23,24,2500,323246,1035,12778228,8827670,9cde85f85fb6c318
ctrl,ctrl_w24_c2,23,24,2500,323247,968,12913494,8900700,a467cc57f97bb86d
ctrl,ctrl_w24_c3,23,24,2500,323248,1015,12823597,8807429,dd6e6e95697ee5a1
ctrl,ctrl_w28_c0,23,28,750,323285,300,15402561,10626080,5dbaa932222fce20
ctrl,ctrl_w28_c1,23,28,750,323286,323,15052818,10659541,590b1395cf62fd1a
ctrl,ctrl_w28_c2,23,28,750,323287,308,15227236,10530162,a9573cc7ea066a5c
ctrl,ctrl_w28_c3,23,28,750,323288,295,15565701,10650891,9ef5f4a93c9b896e
ctrl,ctrl_w32_c0,23,32,250,323325,107,20379993,13932490,2fdbb29573d3a758
ctrl,ctrl_w32_c1,23,32,250,323326,115,19079430,13417345,3c34b19b4da6cacb
ctrl,ctrl_w32_c2,23,32,250,323327,92,20825453,14144206,414af20f321f2cbd
ctrl,ctrl_w32_c3,23,32,250,323328,96,21242787,14279349,3166be67da068bd1
ctrl,ctrl_w36_c0,23,36,50,323365,21,15426215,11480627,915277da98c3abfb
ctrl,ctrl_w36_c1,23,36,50,323366,17,17367209,12039354,db4565c417dacaeb
ctrl,ctrl_w36_c2,23,36,50,323367,18,16858152,11865025,5a35a53e34add774
ctrl,ctrl_w36_c3,23,36,50,323368,21,16852911,11618281,819bab950054d8bc
ctrl,ctrl_w36_c4,23,36,50,323369,23,15965646,11013137,a0722802f53a47d1
ctrl,ctrl_w36_c5,23,36,50,323370,20,15173891,11289227,b96219f873dbc0c6
ctrl,ctrl_w40_c0,23,40,10,323405,4,10850267,8985194,c36ef32a9aadffca
ctrl,ctrl_w40_c1,23,40,10,323406,5,12734109,9040670,87891fa27989b42b
ctrl,ctrl_w40_c2,23,40,10,323407,3,15908220,9460484,5179d246f5833830
ctrl,ctrl_w40_c3,23,40,10,323408,0,15806924,10651660,aa8b113265f0c688
ctrl,ctrl_w40_c4,23,40,10,323409,2,15817693,9469103,50fad0dd519888f5
ctrl,ctrl_w40_c5,23,40,10,323410,3,15425258,9925654,e45e9d6c1c033d9e
```

## Appendix G: offline-derivation and analysis sources (verbatim)

`tune.py` derives the parameter literals T_DP, MCAP, KD, H, TAB, STEPS, GMAXC offline in exact integer arithmetic by calling the functions of Appendix B (it assembles no program text, and no other module of ours is imported); `prep_count.py` meters the field operations of `build_step`; `prep_bound.py` runs `tune.py` and `plan` and prints the table of Section 6a; `analyze_route2.py` computes the exact-law estimates, intervals and coverage of Section 8.

### tune.py

```python
"""Offline choice of the row parameters (T_DP, MCAP, KD, H, TAB) and the literals STEPS and GMAXC, in exact integer arithmetic (no float, no Decimal,
no assembly of program text).  Usage: python3 -B tune.py rho.py   (rho.py: the program of proof.md Appendix B, any parameter literals)
It imports the program and calls its `derive` and `table_exp` (exact integer arithmetic, their operations metered in rho.CNT).
Table size MCAP: the largest that fits 2^20 bytes with the row's code, constants and registers.  For each of the 25 candidate pairs (KD, H) and TAB = 12:
T_DP is the largest value in [1000, 65535] whose table-overflow bound holds (bisection, 16 probes), the budget n the least multiple of 2^100 whose
success bound reaches 0.39 (`least_k`), and the candidate with the least total (`ledger`) wins.  Prints the parameter block, the metered counts and the
result of `price`: the number of word operations charged for this run.  `python3 -B tune.py rho.py` run on the shipped rho.py reproduces its literals."""
import importlib.util
import json
import sys
from fractions import Fraction

CAND_KD = (Fraction(17, 2), Fraction(35, 4), Fraction(9), Fraction(37, 4), Fraction(19, 2))
CAND_H = (Fraction(19), Fraction(77, 4), Fraction(39, 2), Fraction(79, 4), Fraction(20))
TAB = 12
LIMIT = 1 << 20
T_LO, T_HI = 1000, (1 << 16) - 1          # T_DP < 2^16 (the side field has 16 bits)


def load(path):
    spec = importlib.util.spec_from_file_location("rho_mod", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def frac(q):
    return str(q.numerator) if q.denominator == 1 else "%d/%d" % (q.numerator, q.denominator)


def tune(path):
    m = load(path)
    for k in m.CNT:
        m.CNT[k] = 0
    fixed = m.fixed_bytes()
    M = (LIMIT - fixed) * 16 // (16 * 32 + 32) + 2
    for _ in range(64):                  # at most 64 trips (M overshoots the maximum by at most 3)
        m.CNT["add"] += 10
        m.CNT["mul"] += 2
        if (M + 1) * 32 + ((M + 1 + 15) // 16) * 32 + fixed <= LIMIT:
            break
        M -= 1
    else:
        raise AssertionError("tune: table size loop")
    best = None
    for KD in CAND_KD:
        for H in CAND_H:
            ek = m.exp_consts(KD, H, TAB)

            def feasible(T):
                r = m.derive(T, M, KD, H, TAB, m.Q_RANDOM, ek)
                f, mu = m.table_exp(r["S"], T, M)
                m.CNT["add"] += 40
                return f is not None and f <= -TAB * m.ONE
            lo, hi = T_LO, T_HI
            assert feasible(lo)
            while lo < hi:               # 16 probes
                mid = (lo + hi + 1) // 2
                if feasible(mid):
                    lo = mid
                else:
                    hi = mid - 1
            r = m.derive(lo, M, KD, H, TAB, m.Q_RANDOM, ek)
            tot = m.ledger(r["S"], r["gmax"], M)
            m.CNT["add"] += 40
            if best is None or tot < best[0]:
                best = (tot, lo, KD, H, r["S"], r["gmax"])
    tot, T, KD, H, S, gmax = best
    out = {"T_DP": T, "MCAP": M, "KD": frac(KD), "H": frac(H), "TAB": TAB, "STEPS": S, "GMAXC": gmax, "ledger_without_prep": tot}
    assert m.CNT["bits"] < 1 << 11, "an operand reached 2048 bits"
    return out, dict(m.CNT)


# Prices, in word operations (256-bit words).  An integer operand is below 2^2048 (8 limbs; the largest seen is in `bits`).
# add/subtract/compare/shift: 8 (one per limb).  A 256 x 256 -> 512-bit limb product: 64 (nine exact field products of 86-bit pieces plus the
# splitting, carries and accumulation); mul: 8 x 8 limb products = 4096; floor division: schoolbook, 9 quotient limbs each at most one
# multiplication of the divisor by a limb (8 products) plus the estimate and the subtraction, at most 8192.  Every metered operation is charged
# STMT = 8 times (the operation and at most 7 loads, stores and loop operations around it).
PRICE = {"add": 8, "mul": 4096, "div": 8192}
STMT = 8


def price(cnt):
    return STMT * sum(cnt[k] * PRICE[k] for k in PRICE)


if __name__ == "__main__":
    out, cnt = tune(sys.argv[1])
    out["metered"] = cnt
    out["charged_word_operations"] = price(cnt)
    print(json.dumps(out))
```

### prep_count.py

```python
"""Counts the field operations of the offline derivation of the step constants (module-level code of rho.py from section 3 `INV5 =` through
`OUTINV`, i.e. line(), message(0), message(1), build_step()), by executing that code on metered field elements.
Usage: python3 -B prep_count.py rho.py   -> JSON {add, mul, cmp, pow_squarings, pow_mults, field_ops}
Prices: ADD, MUL, compare 1 each; pow(x, e, P) = (bit_length(e) - 1) squarings + (popcount(e) - 1) multiplications; a reduction `% P` is part of the operation."""
import json
import sys

CNT = {"add": 0, "mul": 0, "cmp": 0, "sq": 0, "pm": 0}
PP = [None]


class Fe:
    __slots__ = ("v",)

    def __init__(self, v):
        self.v = v.v if isinstance(v, Fe) else v

    @staticmethod
    def u(o):
        return o.v if isinstance(o, Fe) else o

    def __add__(self, o):
        CNT["add"] += 1
        return Fe(self.v + Fe.u(o))
    __radd__ = __add__

    def __sub__(self, o):
        CNT["add"] += 1
        return Fe(self.v - Fe.u(o))

    def __rsub__(self, o):
        CNT["add"] += 1
        return Fe(Fe.u(o) - self.v)

    def __neg__(self):
        CNT["add"] += 1
        return Fe(-self.v)

    def __mul__(self, o):
        CNT["mul"] += 1
        return Fe(self.v * Fe.u(o))
    __rmul__ = __mul__

    def __mod__(self, m):
        return Fe(self.v % m)

    def __pow__(self, e, m=None):
        CNT["sq"] += e.bit_length() - 1
        CNT["pm"] += bin(e).count("1") - 1
        return Fe(pow(self.v, e, m))

    def __eq__(self, o):
        CNT["cmp"] += 1
        return self.v % PP[0] == Fe.u(o) % PP[0]

    def __ne__(self, o):
        CNT["cmp"] += 1
        return self.v % PP[0] != Fe.u(o) % PP[0]

    def __hash__(self):
        return hash(self.v)

    def __index__(self):
        return self.v


def count(src):
    for k in CNT:
        CNT[k] = 0
    i2 = src.index("# ================================================================ 3 the input line")
    i3 = src.index("NCONST = len(KVAL)")
    head, mid = src[:i2], src[i2:i3]
    ns = {"__name__": "metered"}
    exec(compile(head, "head", "exec"), ns)
    PP[0] = ns["P"]
    ns["ROUND_CONSTANTS"] = tuple(tuple(Fe(x) for x in k) for k in ns["ROUND_CONSTANTS"])
    ns["MDS"] = tuple(tuple(Fe(x) for x in k) for k in ns["MDS"])
    ns["CAPACITY"] = Fe(ns["CAPACITY"])
    ns["Fe"] = Fe
    mid = mid.replace("tau = root5(W)", "tau = root5(Fe(W))")
    exec(compile(mid, "mid", "exec"), ns)
    fops = CNT["add"] + CNT["mul"] + CNT["cmp"] + CNT["sq"] + CNT["pm"]
    return {"add": CNT["add"], "mul": CNT["mul"], "cmp": CNT["cmp"], "pow_squarings": CNT["sq"], "pow_mults": CNT["pm"], "field_ops": fops,
            "steps_built": len(ns["STEP"]), "consts": len(ns["KVAL"])}


if __name__ == "__main__":
    print(json.dumps(count(open(sys.argv[1], encoding="utf-8").read())))
```

### prep_bound.py

```python
"""Finite charged bound for the offline derivation of the program's constants and parameters (word operations of the cost model).
Usage: python3 -B prep_bound.py rho.py -> JSON (the table of proof.md Section 6a).  Everything is metered by running the shipped code:
(a) field operations of the module-level derivation (INV5, `line`, `message`, `build_step`), by `prep_count.py` (8 word operations per field operation,
plus 2^16 for INV5); (b) integer operations of `tune.py` (its calls of `derive`, `table_exp`, `exp_consts` in exact integer arithmetic),
counted by the program itself (rho.CNT) and priced by `tune.price`; (c) the same for one run of `plan` (the offline re-check of the literals).
Nothing is estimated by a cap: the loops of the program have fixed trip counts (bisections on fixed intervals, series of KEXP and KLN terms)."""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from prep_count import count  # noqa: E402
import tune  # noqa: E402

INV5_OPS = 1 << 16                     # INV5 = pow(5, -1, p - 1): extended Euclid on 254-bit integers, fewer than 2^16 word operations
LOAD_OPS = 1 << 16                     # reading and compiling the 41 KB text of rho.py, the other module-level statements, the output


def plan_counts(path):
    spec = importlib.util.spec_from_file_location("rho_plan", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for k in m.CNT:
        m.CNT[k] = 0
    try:
        m.plan()
    except AssertionError:             # first pass with provisional literals: the counts are those of the work done before the assertion
        pass
    return dict(m.CNT)


def prep_bound(path, tcount):
    src = open(path, encoding="utf-8").read()
    c = count(src)
    bs = 8 * c["field_ops"] + INV5_OPS
    pc = plan_counts(path)
    tp, pp = tune.price(tcount), tune.price(pc)
    tot = bs + tp + pp + LOAD_OPS
    return {"field_ops": c, "build_step": bs, "tune_counts": tcount, "tune": tp, "plan_counts": pc, "plan": pp, "load": LOAD_OPS, "total": tot}


if __name__ == "__main__":
    out, cnt = tune.tune(sys.argv[1])
    print(json.dumps(prep_bound(sys.argv[1], cnt), indent=1))
```

### analyze_route2.py

```python
"""Route 2 re-analysis of the posgen_v3 line-map ladders (raw per-trial JSON lines kept in RAW).
(1) Hazard multiplier c from the EXACT discrete first-repeat law, not from the exponential approximation:
    for a function whose collision hazard is c times that of a uniformly random function on N points,
        P(t > n) = prod_{i=1..n} (1 - c i / N)            (c = 1: the exact law of a random function; t = first repeat index of the walk),
        P(t = n) = P(t > n-1) * (c n / N),
    ln P(t > n) is summed term by term (power series of ln(1 - x) to order 6, exact to double precision for the n/N' <= 0.05 reached here).
    c_hat = maximiser of the exact log-likelihood; the 95% interval is the profile-likelihood interval 2 (l(c_hat) - l(c)) <= 3.8415
    (asymptotic in the number of walks K, not in N). Its coverage is checked by simulation from the exact law (table in the output).
(2) Per-job record (invocation, seedbase, K, found, sums, sha256 of the raw file).
Usage: python3 -B analyze_route2.py   -> summary.json (same keys as the Route 1 summary), jobs_table.txt, coverage.json
"""
import glob
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = r"D:\~~Projects\~HashSmash\workspace\research\rows_1015\factory\posgen_v3\meas"
if not os.path.isdir(RAW):
    RAW = "/mnt/d/~~Projects/~HashSmash/workspace/research/rows_1015/factory/posgen_v3/meas"
WIDTHS = (16, 20, 24, 28, 32, 36, 40)
CHI2_95 = 3.841458820694124


def lnS(n, Np):
    """ln prod_{i=1..n} (1 - i / Np) for arrays n, hazard-scaled size Np (series to order 6)."""
    n = np.asarray(n, dtype=np.float64)
    s1 = n * (n + 1) / 2
    s2 = n * (n + 1) * (2 * n + 1) / 6
    s3 = s1 ** 2
    s4 = n * (n + 1) * (2 * n + 1) * (3 * n * n + 3 * n - 1) / 30
    s5 = n * n * (n + 1) ** 2 * (2 * n * n + 2 * n - 1) / 12
    s6 = n * (n + 1) * (2 * n + 1) * (3 * n ** 4 + 6 * n ** 3 - 3 * n + 1) / 42
    x = 1.0 / Np
    return -(s1 * x + s2 * x ** 2 / 2 + s3 * x ** 3 / 3 + s4 * x ** 4 / 4 + s5 * x ** 5 / 5 + s6 * x ** 6 / 6)


def loglik(c, groups):
    """Exact log-likelihood of hazard multiplier c; groups = [(N, t array)]."""
    tot = 0.0
    for N, t in groups:
        Np = N / c
        tot += float(np.sum(lnS(t - 1, Np) + np.log(t / Np)))
    return tot


def mle(groups):
    lo, hi = 0.2, 3.0
    g = (math.sqrt(5) - 1) / 2
    a, b = lo, hi
    x1, x2 = b - g * (b - a), a + g * (b - a)
    f1, f2 = loglik(x1, groups), loglik(x2, groups)
    for _ in range(80):
        if f1 < f2:
            a, x1, f1 = x1, x2, f2
            x2 = a + g * (b - a)
            f2 = loglik(x2, groups)
        else:
            b, x2, f2 = x2, x1, f1
            x1 = b - g * (b - a)
            f1 = loglik(x1, groups)
    return (a + b) / 2


def interval(groups, chat=None):
    chat = mle(groups) if chat is None else chat
    lmax = loglik(chat, groups)

    def root(side):
        a, b = (chat, 3.0) if side > 0 else (0.05, chat)
        # f(c) = 2 (lmax - l(c)) - chi2; f(chat) < 0, f(far end) > 0
        for _ in range(70):
            m = (a + b) / 2
            v = 2 * (lmax - loglik(m, groups)) - CHI2_95
            if (v > 0) == (side > 0):
                b = m
            else:
                a = m
        return (a + b) / 2
    return chat, root(-1), root(+1)


def sample_t(N, Np, K, rng):
    """K draws of t from the exact law with hazard-scaled size Np: smallest n with P(t > n) < 1 - U (bisection on the exact ln S)."""
    u = rng.random(K)
    target = np.log1p(-u)           # ln(1 - U); t = least n with ln S(n) <= target
    lo = np.ones(K)
    hi = np.full(K, 12.0 * math.sqrt(N) + 4)
    for _ in range(60):
        mid = np.floor((lo + hi) / 2)
        ok = lnS(mid, Np) <= target
        hi = np.where(ok, mid, hi)
        lo = np.where(ok, lo, mid + 1)
        if np.all(lo >= hi):
            break
    return hi


def read_job(path):
    rows = []
    for line in open(path, encoding="utf-8"):
        if line.strip():
            rows.append(json.loads(line))
    return rows


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    S = json.load(open(os.path.join(RAW, "summary.json")))
    data = {}                        # key -> list of (w, trial dict)
    jobs_out = []
    totals = {}
    for folder in ("7", "23", "56", "ctrl"):
        jobs = [l.split() for l in open(os.path.join(RAW, "data", folder, "jobs.txt")) if l.strip()]
        jobs.sort(key=lambda j: (int(j[3]), j[11]))
        tag = "ctrl" if folder == "ctrl" else "line"
        for j in jobs:
            fam, fixed, r, w, T, h, Sx, mcap, gmax, K, sb, fn = j
            path = os.path.join(RAW, "data", folder, fn)
            rows = read_job(path)
            assert len(rows) == int(K), (fn, len(rows), K)
            assert all(d["seedbase"] == int(sb) and d["w"] == int(w) for d in rows)
            key = ("ctrl", int(w)) if folder == "ctrl" else (int(folder), int(w))
            data.setdefault(key, []).extend(rows)
            found = sum(d["status"] == "found" for d in rows)
            cens = sum(d["cens"] for d in rows)
            assert cens == 0
            jobs_out.append((folder, fn, fam, r, w, T, h, Sx, mcap, gmax, K, sb, found, sum(d["t"] for d in rows), sum(d["evals"] for d in rows),
                             sha(path)))
            tt = totals.setdefault(folder, [0, 0, 0, 0])
            tt[0] += int(K); tt[1] += sum(d["t"] for d in rows); tt[2] += sum(d["evals"] for d in rows); tt[3] += 1
    # exact-law estimates per cell
    new = json.loads(json.dumps(S))
    cellkeys = {}
    for (kind, w), rows in sorted(data.items(), key=lambda kv: (str(kv[0][0]), kv[0][1])):
        t = np.array([d["t"] for d in rows], dtype=np.float64)
        N = float(1 << w)
        ch, lo, hi = interval([(N, t)])
        k = f"ctrl/w{w}" if kind == "ctrl" else f"r{kind}/w{w}"
        cellkeys[k] = (ch, lo, hi)
        old = S[k]
        new[k].update({"c_hat": round(ch, 4), "c_lo": round(lo, 4), "c_hi": round(hi, 4), "c_hat_gamma_old": old["c_hat"],
                       "c_lo_gamma_old": old["c_lo"], "c_hi_gamma_old": old["c_hi"]})
    # per r, pooled
    for r in (7, 23, 56):
        grp = [(float(1 << w), np.array([d["t"] for d in data[(r, w)]], dtype=np.float64)) for w in WIDTHS if (r, w) in data]
        ch, lo, hi = interval(grp)
        new[f"r{r}/all"].update({"c_hat": round(ch, 4), "c_lo": round(lo, 4), "c_hi": round(hi, 4)})
    # pooled by width over r
    pooled = {}
    for w in WIDTHS:
        t = np.array([d["t"] for r in (7, 23, 56) for d in data[(r, w)]], dtype=np.float64)
        ch, lo, hi = interval([(float(1 << w), t)])
        pooled[w] = (ch, lo, hi, len(t))
        new["pooled_by_width"][f"w{w}"].update({"c_hat": round(ch, 4), "c_lo": round(lo, 4), "c_hi": round(hi, 4)})
    # overall pooled
    grp = [(float(1 << w), np.array([d["t"] for r in (7, 23, 56) for d in data[(r, w)]], dtype=np.float64)) for w in WIDTHS]
    ch, lo, hi = interval(grp)
    Ktot = sum(len(g[1]) for g in grp)
    new["c_all"] = {"K": Ktot, "c_hat": round(ch, 4), "c_lo": round(lo, 4), "c_hi": round(hi, 4), "dt_lo": round(0.5 * math.log2(1 / lo), 4) if lo < 1 else 0.0,
                    "c_hat_gamma_old": S["c_all"]["c_hat"], "c_lo_gamma_old": S["c_all"]["c_lo"], "c_hi_gamma_old": S["c_all"]["c_hi"]}
    # trend: weighted LS of log c on width, weights K (as in the Route 1 analysis)
    pts = [(w, v[0], v[3]) for w, v in pooled.items()]
    sw = sum(K for _, _, K in pts)
    mx = sum(w * K for w, _, K in pts) / sw
    my = sum(math.log(c) * K for _, c, K in pts) / sw
    sxx = sum(K * (w - mx) ** 2 for w, _, K in pts)
    sxy = sum(K * (w - mx) * (math.log(c) - my) for w, c, K in pts)
    new["trend"] = {"slope_log_c_per_bit": round(sxy / sxx, 5), "se": round(1 / math.sqrt(sxx), 5)}
    cells = [(k, v) for k, v in new.items() if k.startswith("r") and "/w" in k]
    new["cells_ci_contains_1"] = f'{sum(v["c_lo"] <= 1 <= v["c_hi"] for _, v in cells)}/{len(cells)}'
    new["cells_outside"] = {k: [v["c_lo"], v["c_hi"]] for k, v in cells if not v["c_lo"] <= 1 <= v["c_hi"]}
    new["estimator"] = "exact discrete first-repeat law, profile-likelihood 95% interval (asymptotic in K only)"
    json.dump(new, open(os.path.join(HERE, "summary.json"), "w"), indent=1)

    # coverage by simulation from the exact law (true c = 1 and true c = 0.6), same K and widths as the cells
    rng = np.random.default_rng(20261016)
    cov = {}
    B = 400
    for w, K in ((16, 2000), (24, 2000), (28, 600), (32, 200), (36, 60), (40, 12)):
        N = float(1 << w)
        for ctrue in (1.0, 0.6):
            hit = 0
            below = 0
            for _ in range(B):
                t = sample_t(N, N / ctrue, K, rng)
                ch, lo, hi = interval([(N, t)])
                hit += lo <= ctrue <= hi
            cov[f"w{w}_K{K}_c{ctrue}"] = round(hit / B, 3)
    # the whole composition of one r (K = 6872) at c = 1
    comp = [(float(1 << w), len(data[(23, w)])) for w in WIDTHS]
    hit = 0
    for _ in range(100):
        grp = [(N, sample_t(N, N, K, rng)) for N, K in comp]
        ch, lo, hi = interval(grp)
        hit += lo <= 1.0 <= hi
    cov["r23_all_widths_K%d_c1.0" % sum(K for _, K in comp)] = round(hit / 100, 3)
    json.dump({"reps_per_row": B, "coverage_of_nominal_95": cov}, open(os.path.join(HERE, "coverage.json"), "w"), indent=1)

    # sanity: exact-law log-likelihood vs a direct product at w = 16, and agreement of the series with lgamma at w = 16
    N = 65536.0
    n = np.array([10, 300, 1000, 3000])
    direct = np.array([np.sum(np.log1p(-np.arange(1, int(x) + 1) / N)) for x in n])
    assert np.max(np.abs(direct - lnS(n, N))) < 1e-6, (direct, lnS(n, N))   # series truncation at the cap n = 3000 (n/N = 0.046) is the largest error

    with open(os.path.join(HERE, "jobs_table.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("run,job,r,w,K,seedbase,found,sum_t,sum_evals,sha256_16\n")
        for (folder, fn, fam, r, w, T, h, Sx, mcap, gmax, K, sb, found, st, se, sh) in jobs_out:
            f.write(f"{'ctrl' if folder == 'ctrl' else 'r' + folder},{fn[:-6]},{r},{w},{K},{sb},{found},{st},{se},{sh[:16]}\n")
    json.dump({k: {"walks": v[0], "sum_t": v[1], "sum_evals": v[2], "jobs": v[3]} for k, v in totals.items()},
              open(os.path.join(HERE, "totals.json"), "w"), indent=1)
    allh = hashlib.sha256("".join(j[-1] for j in jobs_out).encode()).hexdigest()
    open(os.path.join(HERE, "rawhash.txt"), "w").write(allh + "\n")
    print("done", allh[:16], json.dumps(new["c_all"]), json.dumps(cov))


if __name__ == "__main__":
    main()
```

