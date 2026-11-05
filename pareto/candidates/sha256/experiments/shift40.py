"""r40 SHIFT39-40, block 2 (sha256-r40-shift-v1). The r39 experiment program
(research/pkg_r39_pf013_fix/sha256/experiments/r39joint.py) adapted to block 2 of
the R40 construction (research/runs_1105/pkg_r40_shift/submission-note.md, sec 2-3):
round constants K1..K39 for the characteristic steps, block-2 messages
N = (W_-1, W0..W14), block-2 chaining values differing only in h by 0xc0000000.
Emits the same kind of per-trial observation events r39joint emits. Stdlib only.
Credits: Halley (r40 shift), sraiw 38912d66, dariolina (r39 joint)."""
import sys, json, random

M = 0xFFFFFFFF
# standard SHA-256 round constants K0..K39 (first 40)
K_ALL = [int(x, 16) for x in """428a2f98 71374491 b5c0fbcf e9b5dba5 3956c25b 59f111f1 923f82a4 ab1c5ed5 d807aa98 12835b01 243185be 550c7dc3 72be5d74 80deb1fe 9bdc06a7 c19bf174 e49b69c1 efbe4786 0fc19dc6 240ca1cc 2de92c6f 4a7484aa 5cb0a9dc 76f988da 983e5152 a831c66d b00327c8 bf597fc7 c6e00bf3 d5a79147 06ca6351 14292967 27b70a85 2e1b2138 4d2c6dfc 53380d13 650a7354 766a0abb 81c2c92e 92722c85""".split()]
# KOFF = 1: block-2 characteristic step r (of the 39-step sub-problem) uses K[r+KOFF].
KOFF = 1
K = K_ALL[KOFF:KOFF + 39]   # K1..K39, indexed 0..38
KC = K[0]                   # K1, the step-0 cancelling constant (as in shiftchk.py, k=1)

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

# advice trajectory under the SHIFTED constants K1..K39
BA, BE, BW = traj(CV_PUB, MP_PUB)[0], traj(CV_PUB, MP_PUB)[1], MP_PUB
CA, CE, _CW = traj(CV_PUB, M_PUB)[0], traj(CV_PUB, M_PUB)[1], M_PUB

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

# ---- the two exact block-2 steps (submission-note.md sec 2) ----
def shift(w):
    """N = (W_-1, W0..W14) with W_-1 = W15 - s1(W13) - W8 - s0(W0) (back recurrence)."""
    return [(w[15] - s1(w[13]) - w[8] - s0(w[0])) & M] + w[:15]

def back(s, w, kc):
    """Recover the block-2 chaining value (state before step 0) from the common
    post-step-0 state s and this member's N0; step 0 uses constant kc."""
    a, b, c, d, e, f, g, h = s
    T2 = (S0(b) + MAJ(b, c, d)) & M
    T1 = (a - T2) & M
    pd = (e - T1) & M
    ph = (T1 - S1(f) - CH(f, g, h) - kc - w) & M
    return [b, c, d, pd, f, g, h, ph]

def lit_mask(aw, bw, n):
    return sum(1 << t for t in range(n) if aw[t] != bw[t])

# advice lit sets from submission-note.md sec 2a (old 0..38 -> new 0..39)
NOTE_LIT_R39 = sum(1 << t for t in (8, 9, 10, 11, 12, 16, 17, 24, 26))
NOTE_LIT_B2 = sum(1 << t for t in (0, 9, 10, 11, 12, 13, 17, 18, 25, 27))

def _common(cv, Wmp, Wm, i):
    """Compute and hard-assert the value-independent block-2 facts; return obs dict.
    Member A = M-side (second), member B = MP-side (build), matching the note's sign."""
    A1, E1, _ = traj(cv, Wmp); A2, E2, _ = traj(cv, Wm)
    transplant_ok = int(A1[6:20] == BA[6:20] and E1[10:20] == BE[10:20]
                        and A2[6:20] == CA[6:20] and E2[10:20] == CE[10:20])
    NA, NB = shift(Wm), shift(Wmp)
    oA, oB = expand(Wm, 64), expand(Wmp, 64)
    SA, SB = expand(NA, 64), expand(NB, 64)
    shift_ok = int(all(SA[t + 1] == oA[t] and SB[t + 1] == oB[t] for t in range(63)))
    dN0 = (NB[0] - NA[0]) & M
    cvA, cvB = back(cv, NA[0], KC), back(cv, NB[0], KC)
    diff = [r for r in range(8) if cvA[r] != cvB[r]]
    dh = (cvB[7] - cvA[7]) & M
    assert shift_ok == 1 and dN0 == 0x40000000 and dh == 0xc0000000
    assert diff == [7] and transplant_ok == 1
    out = {"shift_identity_ok": shift_ok, "dN0": dN0, "dh": dh,
           "cv_diff_h_only": int(diff == [7]), "cv_diff_count": len(diff),
           "transplant_ok": transplant_ok, "koff": KOFF, "k_first": K[0], "k_last": K[38]}
    if i == 0:
        out["lit_r39_matches_note"] = int(lit_mask(expand(Wmp, 39), expand(Wm, 39), 39) == NOTE_LIT_R39)
        out["lit_block2_matches_note"] = int(lit_mask(expand(NB, 40), expand(NA, 40), 40) == NOTE_LIT_B2)
    return out

def block2(i, sd):
    """r40shift-block2-transplant: trial 0 is the advice pair; trials 1..255 draw a
    chaining value, an even a0 and an odd u, build a transplant and its partner, then
    apply the schedule shift and the step-0 cancellation on constants K1..K39."""
    if i == 0:
        return _common(CV_PUB, MP_PUB, M_PUB, 0)
    rnd = random.Random(sd)
    cv = [rnd.getrandbits(32) for _ in range(8)]
    a0 = rnd.getrandbits(32) & ~1
    u = rnd.getrandbits(32) | 1
    a1 = recover_a1(cv, a0, u)
    Wmp = build(cv, a0, a1); Wm = second(Wmp)
    return _common(cv, Wmp, Wm, i)

def shiftid(i, sd):
    """r40shift-shift-identity: the pure algebraic shift + step-0 cancellation on a
    random 16-word message with the characteristic difference dW8 = 0xc0000000 and a
    random block-2 post-step-0 state; checks value-independence of dN0, dh and h-only."""
    rnd = random.Random(sd ^ 0x5bd1e995)
    W = [rnd.getrandbits(32) for _ in range(16)]
    Wp = list(W); Wp[8] = (W[8] + 0xc0000000) & M
    for j in (9, 10, 11, 12): Wp[j] = (W[j] + rnd.getrandbits(32)) & M
    cv = [rnd.getrandbits(32) for _ in range(8)]
    NA, NB = shift(W), shift(Wp)
    oA, oB = expand(W, 64), expand(Wp, 64)
    SA, SB = expand(NA, 64), expand(NB, 64)
    shift_ok = int(all(SA[t + 1] == oA[t] and SB[t + 1] == oB[t] for t in range(63)))
    dN0 = (NB[0] - NA[0]) & M
    cvA, cvB = back(cv, NA[0], KC), back(cv, NB[0], KC)
    diff = [r for r in range(8) if cvA[r] != cvB[r]]
    dh = (cvB[7] - cvA[7]) & M
    assert shift_ok == 1 and dN0 == 0x40000000 and dh == 0xc0000000 and diff == [7]
    return {"shift_identity_ok": shift_ok, "dN0": dN0, "dh": dh,
            "cv_diff_h_only": int(diff == [7]), "cv_diff_count": len(diff), "koff": KOFF}

GEN_EXPERIMENTS = ("r40shift-block2-transplant", "r40shift-shift-identity")

def serve():
    req = json.load(sys.stdin)
    eid = req["experiment_id"]
    fn = shiftid if eid == GEN_EXPERIMENTS[1] else block2
    rows = []
    for t in req["trials"]:
        obs = fn(t["trial"], int(t["seed"][:16], 16))
        row = {"trial": t["trial"], "message_a_hex": None, "message_b_hex": None}
        if obs:
            row["observations"] = obs
        rows.append(row)
    sys.stdout.write(json.dumps({"schema_version": 1, "trials": rows},
                                sort_keys=True, separators=(",", ":")) + "\n")

def _selftest():
    import time, hashlib
    trials = [{"trial": i, "seed": hashlib.sha256(("r40-%d" % i).encode()).hexdigest()}
              for i in range(256)]
    t = time.time()
    rows = []
    for tr in trials:
        obs = block2(tr["trial"], int(tr["seed"][:16], 16))
        rows.append({"trial": tr["trial"], "message_a_hex": None,
                     "message_b_hex": None, "observations": obs})
    dt = time.time() - t
    s = json.dumps({"schema_version": 1, "trials": rows}, sort_keys=True, separators=(",", ":"))
    sys.stderr.write("wall_seconds %.3f\n" % dt)
    sys.stderr.write("trials %d\n" % len(rows))
    sys.stderr.write("observation_events %d\n" % sum(1 for r in rows if "observations" in r))
    sys.stderr.write("full_collision_events %d\n" % 0)
    for i in (0, 1, 2):
        sys.stderr.write("sample trial %d: %s\n" % (i, json.dumps(rows[i]["observations"], sort_keys=True)))
    sys.stdout.write(s + "\n")

def main():
    if "--selftest" in sys.argv[1:]:
        _selftest(); return
    serve()

if __name__ == "__main__":
    main()
