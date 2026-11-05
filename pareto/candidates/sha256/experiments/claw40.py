"""r40 SHIFT39-40 claw-rate measurement, block 2 (sha256-r40-shift-v1).

The r39 window/claw/tail measurement of
  research/pkg_r39_pf013_fix/sha256/experiments/r39joint.py
moved to block 2 of the R40 construction
  (research/runs_1105/pkg_r40_shift/submission-note.md, sec 2-3):
round constants K1..K39 for the characteristic steps (KOFF=1), the shifted
advice words, and a block-2 incoming chaining value whose two members differ
only in h by 0xc0000000.  Per trial it runs 2 windows of the claw search on
the shifted folded step function F, counts claw groups and the F9/F8/W17 tail
events, and emits the same kind of per-trial observations r39joint emits.
256 trials finish in well under 4 s on one CPU; stdlib only; deterministic
from the trial seed; exactly one JSON document out; two null messages per
trial unless a full collision is found.  Credits: Halley (r40 shift),
sraiw 38912d66, dariolina (r39 joint)."""
import sys, json, random

M = 0xFFFFFFFF
# standard SHA-256 round constants K0..K39 (first 40)
K_ALL = [int(x, 16) for x in """428a2f98 71374491 b5c0fbcf e9b5dba5 3956c25b 59f111f1 923f82a4 ab1c5ed5 d807aa98 12835b01 243185be 550c7dc3 72be5d74 80deb1fe 9bdc06a7 c19bf174 e49b69c1 efbe4786 0fc19dc6 240ca1cc 2de92c6f 4a7484aa 5cb0a9dc 76f988da 983e5152 a831c66d b00327c8 bf597fc7 c6e00bf3 d5a79147 06ca6351 14292967 27b70a85 2e1b2138 4d2c6dfc 53380d13 650a7354 766a0abb 81c2c92e 92722c85""".split()]
KOFF = 1                       # block-2 characteristic step r uses K[r+KOFF]
K = K_ALL[KOFF:KOFF + 39]      # K1..K39, indexed 0..38
KC = K[0]                      # K1, the step-0 cancelling constant

# ---- window budget (static; no wall-clock branching -> deterministic reruns) ----
WINDOWS = 2
WIN_STEPS = 1536               # claw-walk evaluations per window
LANE = 384                     # walk restart length (avoids rho cycling)

def ror(x, k): return ((x >> k) | (x << (32 - k))) & M
def S0(x): return ror(x, 2) ^ ror(x, 13) ^ ror(x, 22)
def S1(x): return ror(x, 6) ^ ror(x, 11) ^ ror(x, 25)
def s0(x): return ror(x, 7) ^ ror(x, 18) ^ (x >> 3)
def s1(x): return ror(x, 17) ^ ror(x, 19) ^ (x >> 10)
def CH(e, f, g): return (e & f) ^ (~e & g & M)
def MAJ(a, b, c): return (a & b) ^ (a & c) ^ (b & c)
H = lambda s: [int(x, 16) for x in s.split()]

# advice characteristic data carried from r39joint (message words; K-independent)
CV_PUB = H("aa79ff87 65c5bb49 d0a84bfd 90ccc398 fac64fb6 4ff7998a b1af5ec5 aa1ed4d5")
M_PUB  = H("8334d670 3813877e f19d46d5 77556fc4 902f98c7 0500282c a4235533 9100e365 e76f5fe2 5633326d 9d603088 06a64487 a94ae11e b06304ad 43660038 d80d950f")
MP_PUB = H("8334d670 3813877e f19d46d5 77556fc4 902f98c7 0500282c a4235533 9100e365 a76f5fe2 5eb3226d dd603088 00a467b3 a95af91e b06304ad 43660038 d80d950f")
D8 = (M_PUB[8] - MP_PUB[8]) & M
D9 = (M_PUB[9] - MP_PUB[9]) & M
T8, T9 = 0x087FF000, 0x03010000     # the s0-difference tail targets (K-independent)

def expand(w, n=39):
    w = list(w)
    for i in range(16, n):
        w.append((w[i - 16] + s0(w[i - 15]) + w[i - 7] + s1(w[i - 2])) & M)
    return w

def traj(cv, w16, n=39):
    w = expand(w16, n)
    A = [cv[3], cv[2], cv[1], cv[0]]; E = [cv[7], cv[6], cv[5], cv[4]]
    for r in range(n):
        a, b, c, d = A[r + 3], A[r + 2], A[r + 1], A[r]
        e, f, g, h = E[r + 3], E[r + 2], E[r + 1], E[r]
        t1 = (h + S1(e) + CH(e, f, g) + K[r] + w[r]) & M
        t2 = (S0(a) + MAJ(a, b, c)) & M
        A.append((t1 + t2) & M); E.append((d + t1) & M)
    return A, E, w

def compress(cv, w16, n=39):
    A, E, _ = traj(cv, w16, n)
    st = [A[n + 3], A[n + 2], A[n + 1], A[n], E[n + 3], E[n + 2], E[n + 1], E[n]]
    return [(st[i] + cv[i]) & M for i in range(8)]

# advice trajectory under the SHIFTED constants K1..K39, and the K-independent
# message-schedule anchors used by the step-16/17 identities.
BA, BE, BW = traj(CV_PUB, MP_PUB)[0], traj(CV_PUB, MP_PUB)[1], MP_PUB
CA, CE, _CW = traj(CV_PUB, M_PUB)[0], traj(CV_PUB, M_PUB)[1], M_PUB
G16 = expand(MP_PUB)[16]
W17PUB = expand(MP_PUB)[17]

# folded-step constants (base_setup of r39joint, Attack.claw), on shifted K / advice
K24 = S0(BA[7]); A7 = BA[7]; A6 = BA[6]
t25 = (S0(BA[8]) + MAJ(BA[8], BA[7], BA[6])) & M
CE5 = (BA[9] - t25) & M
NE11 = (BE[11] ^ M); CH0 = BE[11] & BE[10]
CW8 = (BE[12] - BA[8] - S1(BE[11]) - K[8]) & M
C17 = (s1(BW[15]) + BW[10]) & M
C9 = (BW[9] + BA[5]) & M

def consts(cv):
    t20 = (S0(cv[0]) + MAJ(cv[0], cv[1], cv[2])) & M
    eb = (cv[3] - t20) & M
    k0 = (-t20 - cv[7] - S1(cv[4]) - CH(cv[4], cv[5], cv[6]) - K[0]) & M
    c9 = (BW[9] + BA[5]) & M
    cw = (G16 - s1(BW[14]) - c9 - k0 + cv[6] + K[1]) & M
    return (cw, eb, cv[0], cv[1], cv[4], cv[5])

def fstep(x, c):
    if x & 1:
        return (s0(x) - x) & M
    cw, eb, cv0, cv1, cv4, cv5 = c
    e0 = (x + eb) & M
    return (cw + S0(x) + MAJ(x, cv0, cv1) + S1(e0) + CH(e0, cv4, cv5) - x) & M

def recover_a1(cv, a0, u):
    t20 = (S0(cv[0]) + MAJ(cv[0], cv[1], cv[2])) & M
    e0 = (cv[3] + a0 - t20) & M
    return (u + S0(a0) + MAJ(a0, cv[0], cv[1]) + S1(e0) + CH(e0, cv[4], cv[5]) + cv[6] + K[1]) & M

def build(cv, a0, a1):
    A = [cv[3], cv[2], cv[1], cv[0], a0, a1, BA[6], BA[7], BA[8], BA[9]]
    E = [cv[7], cv[6], cv[5], cv[4]] + [None] * 6
    W = [None] * 16
    for r in range(6):
        a, b, c = A[r + 3], A[r + 2], A[r + 1]
        t2 = (S0(a) + MAJ(a, b, c)) & M
        t1 = (A[r + 4] - t2) & M
        e, f, g, h = E[r + 3], E[r + 2], E[r + 1], E[r]
        W[r] = (t1 - h - S1(e) - CH(e, f, g) - K[r]) & M
        E[r + 4] = (A[r] + t1) & M
    A += [BA[10], BA[11], BA[12], BA[13]]
    E += [None] * 4
    for k in range(10, 14): E[k] = BE[k]
    for r in range(6, 10):
        e, f, g, h = E[r + 3], E[r + 2], E[r + 1], E[r]
        t1 = (E[r + 4] - A[r]) & M
        W[r] = (t1 - h - S1(e) - CH(e, f, g) - K[r]) & M
    for r in range(10, 16): W[r] = BW[r]
    return W

def second(W):
    V = list(W)
    V[8] = (W[8] + D8) & M; V[9] = (W[9] + D9) & M
    for r in range(10, 16): V[r] = M_PUB[r]
    return V

# ---- block-2 shift + step-0 cancellation (submission-note.md sec 2) ----
def shift(w):
    return [(w[15] - s1(w[13]) - w[8] - s0(w[0])) & M] + w[:15]

def back(s, w, kc):
    a, b, c, d, e, f, g, h = s
    T2 = (S0(b) + MAJ(b, c, d)) & M
    T1 = (a - T2) & M
    pd = (e - T1) & M
    ph = (T1 - S1(f) - CH(f, g, h) - kc - w) & M
    return [b, c, d, pd, f, g, h, ph]

# ---- the claw search window (van-Oorschot-Wiener style, folded F) ----
def walk_window(c, rng, steps):
    """Run `steps` evaluations of the folded step function F over short restarted
    lanes sharing one DP table; return every even/odd claw (a0 even, u odd, F=F)."""
    cw, eb, cv0, cv1, cv4, cv5 = c
    seen = {}
    pairs = []
    done = 0
    while done < steps:
        pos = rng.getrandbits(32)
        n = LANE if steps - done >= LANE else steps - done
        for _ in range(n):
            x = pos
            if x & 1:
                s0x = (((x >> 7) | (x << 25)) ^ ((x >> 18) | (x << 14)) ^ (x >> 3)) & M
                nxt = (s0x - x) & M
            else:
                e0 = (x + eb) & M
                S0x = (((x >> 2) | (x << 30)) ^ ((x >> 13) | (x << 19)) ^ ((x >> 22) | (x << 10))) & M
                maj = (x & cv0) ^ (x & cv1) ^ (cv0 & cv1)
                S1e = (((e0 >> 6) | (e0 << 26)) ^ ((e0 >> 11) | (e0 << 21)) ^ ((e0 >> 25) | (e0 << 7))) & M
                ch = (e0 & cv4) ^ ((e0 ^ M) & cv5)
                nxt = (cw + S0x + maj + S1e + ch - x) & M
            p = seen.get(nxt)
            if p is None:
                seen[nxt] = x
            elif (p ^ x) & 1:
                pairs.append((p, x) if (p & 1) == 0 else (x, p))
            pos = nxt
        done += n
    return pairs

def tail_stats(cv, c, pairs):
    """F9 / F8 / W17 tail filters of r39joint.Attack.claw, on shifted K / advice."""
    cw, eb = c[0], c[1]
    cv0, cv1, cv4, cv5 = cv[0], cv[1], cv[4], cv[5]
    CA1 = (cv[6] + K[1] - cw) & M
    f9 = f8 = w17 = 0
    coll = None
    for a0, u in pairs:
        a1 = (s0(u) + a0 + CA1) & M
        W9 = (C9 - a1) & M
        if ((s0((W9 + D9) & M) - s0(W9)) & M) != T9: continue
        f9 += 1
        e4 = ((a0 + BA[8]) - (K24 + MAJ(A7, A6, a1))) & M
        e5 = (a1 + CE5) & M
        W8 = (CW8 - e4 - (CH0 ^ (e5 & NE11))) & M
        if ((s0((W8 + D8) & M) - s0(W8)) & M) != T8: continue
        f8 += 1
        e1 = ((cv[2] + a1) - S0(a0) - MAJ(a0, cv0, cv1)) & M
        e0 = (a0 + eb) & M
        w2 = (BA[6] - S0(a1) - MAJ(a1, a0, cv0) - cv5 - S1(e1) - CH(e1, e0, cv4)) & M
        w2 = (w2 - K[2]) & M
        if ((C17 + s0(w2) + u) & M) != W17PUB: continue
        w17 += 1
        a1r = recover_a1(cv, a0, u)
        Wc = build(cv, a0, a1r); Wc2 = second(Wc)
        if Wc != Wc2 and compress(cv, Wc) == compress(cv, Wc2):
            coll = (Wc, Wc2)
    return f9, f8, w17, coll

def count_groups(dset):
    pa = {}
    def fd(x):
        while pa[x] != x:
            pa[x] = pa[pa[x]]; x = pa[x]
        return x
    for win, a0, u in dset:
        ka, ku = (win, 0, a0), (win, 1, u)
        pa.setdefault(ka, ka); pa.setdefault(ku, ku)
        ra, ru = fd(ka), fd(ku)
        if ra != ru: pa[ra] = ru
    return sum(1 for x in pa if pa[x] == x)

def shift_identity_ok():
    NA, NB = shift(M_PUB), shift(MP_PUB)
    oA, oB = expand(M_PUB, 64), expand(MP_PUB, 64)
    SA, SB = expand(NA, 64), expand(NB, 64)
    return int(all(SA[t + 1] == oA[t] and SB[t + 1] == oB[t] for t in range(63)))

def kat():
    """Trial-0 known-answer check: the advice pair claws and clears every tail
    filter on the shifted constants, and the schedule shift reproduces block 2."""
    cv = CV_PUB; c = consts(cv)
    a0, u = BA[4], MP_PUB[1]
    claw_ok = int(fstep(a0, c) == (s0(u) - u) & M)
    f9 = f8 = w17 = 0; ca = None
    if claw_ok:
        f9, f8, w17, ca = tail_stats(cv, c, [(a0, u)])
    return {"kat_advice_claw_ok": claw_ok, "kat_passed_f9": f9, "kat_passed_f8": f8,
            "kat_passed_w17": w17, "kat_full_collision": int(ca is not None),
            "kat_shift_identity_ok": shift_identity_ok()}

def run_trial(trial, sd):
    rng = random.Random(sd)
    # block-2 structural facts from a drawn transplant pair (value-independent)
    cv = [rng.getrandbits(32) for _ in range(8)]
    a0f = rng.getrandbits(32) & ~1
    uf = rng.getrandbits(32) | 1
    Wmp = build(cv, a0f, recover_a1(cv, a0f, uf)); Wm = second(Wmp)
    NA, NB = shift(Wm), shift(Wmp)
    dN0 = (NB[0] - NA[0]) & M
    cvA, cvB = back(cv, NA[0], KC), back(cv, NB[0], KC)
    diff = [r for r in range(8) if cvA[r] != cvB[r]]
    dh = (cvB[7] - cvA[7]) & M
    # window claw search on the shifted folded step function
    allpairs = []
    f9 = f8 = w17 = 0; coll = None
    for w in range(WINDOWS):
        cvw = [rng.getrandbits(32) for _ in range(8)]
        c = consts(cvw)
        ps = walk_window(c, rng, WIN_STEPS)
        for a0, u in ps:
            allpairs.append((w, a0, u))
        nf9, nf8, nw17, c2 = tail_stats(cvw, c, ps)
        f9 += nf9; f8 += nf8; w17 += nw17
        if c2 is not None and coll is None:
            coll = c2
    distinct = set(allpairs)
    obs = {"windows": WINDOWS, "window_steps": WIN_STEPS,
           "walk_evals": WINDOWS * WIN_STEPS,
           "raw_claws": len(allpairs), "distinct_claws": len(distinct),
           "distinct_groups": count_groups(distinct),
           "passed_f9": f9, "passed_f8": f8, "passed_w17": w17,
           "cv_diff_h_only": int(diff == [7])}
    if trial == 0:
        obs.update(kat())
    msgs = (None, None)
    if coll is not None:
        W1, W2 = coll
        msgs = ("".join("%08x" % x for x in W1), "".join("%08x" % x for x in W2))
    return obs, msgs

GEN_EXPERIMENTS = ("claw40-window-01",)   # any other id falls back to this one

def serve():
    req = json.load(sys.stdin)
    rows = []
    for t in req["trials"]:
        obs, msgs = run_trial(t["trial"], int(t["seed"][:16], 16))
        row = {"trial": t["trial"], "message_a_hex": msgs[0], "message_b_hex": msgs[1]}
        if obs:
            row["observations"] = obs
        rows.append(row)
    sys.stdout.write(json.dumps({"schema_version": 1, "trials": rows},
                                sort_keys=True, separators=(",", ":")) + "\n")

def _selftest():
    import time, hashlib
    trials = [{"trial": i, "seed": hashlib.sha256(("claw40-%d" % i).encode()).hexdigest()}
              for i in range(256)]
    t = time.time(); rows = []
    for tr in trials:
        obs, msgs = run_trial(tr["trial"], int(tr["seed"][:16], 16))
        rows.append({"trial": tr["trial"], "message_a_hex": msgs[0],
                     "message_b_hex": msgs[1], "observations": obs})
    dt = time.time() - t
    s = json.dumps({"schema_version": 1, "trials": rows}, sort_keys=True, separators=(",", ":"))
    sys.stderr.write("wall_seconds %.3f\n" % dt)
    sys.stderr.write("trials %d\n" % len(rows))
    sys.stderr.write("windows_per_trial %d  walk_evals_per_trial %d\n" % (WINDOWS, WINDOWS * WIN_STEPS))
    sys.stderr.write("raw_claws_total %d\n" % sum(r["observations"]["raw_claws"] for r in rows))
    sys.stderr.write("distinct_groups_total %d\n" % sum(r["observations"]["distinct_groups"] for r in rows))
    sys.stderr.write("full_collision_events %d\n" % sum(1 for r in rows if r["message_a_hex"] is not None))
    sys.stderr.write("trial 0: %s\n" % json.dumps(rows[0]["observations"], sort_keys=True))
    sys.stdout.write(s + "\n")

def main():
    if "--selftest" in sys.argv[1:]:
        _selftest(); return
    serve()

if __name__ == "__main__":
    main()
