#!/usr/bin/env python3
"""python-message-pairs-v1 program for SHIFT39-41 (k = 2).
Reads one organizer JSON request on stdin, writes one JSON document with every trial once.
Per trial it emits the two shifted block-2 messages N, N' (hex) and numeric observations that
recompute, from the seed, the three score-critical facts of the R41 construction:
  (1) the schedule identity N_t = W_{t-2} holds for the embedded verified 39-step factory pair;
  (2) the two-step cancellation (dg = 0xc0000000, dh = -dN0 - dCh(e,f,g)) equalises the state after
      steps 0-1 for every random block-1 chaining value drawn from the seed;
  (3) the free word N1 selects |S| = 64 distinct dN0, all equal mod 2^13, and the shared-budget price.
Standard library only; deterministic from the per-trial seed; every loop bounded by a constant."""
import sys, json, hashlib

M = 0xffffffff
def rotr(x, n): return ((x >> n) | (x << (32 - n))) & M
s0 = lambda x: rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3)
s1 = lambda x: rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10)
S0 = lambda x: rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22)
S1 = lambda x: rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25)
Ch = lambda e, f, g: (e & f) ^ (~e & g & M)
Maj = lambda a, b, c: (a & b) ^ (a & c) ^ (b & c)
K = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
     0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
     0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
     0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
     0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
     0xa2bfe8a1]

def schedule(w, R):
    w = list(w)
    for t in range(16, R):
        w.append((s1(w[t - 2]) + w[t - 7] + s0(w[t - 15]) + w[t - 16]) & M)
    return w

def shift2(w):
    w = list(w)
    for _ in range(2):
        w = [(w[15] - s1(w[13]) - w[8] - s0(w[0])) & M] + w[:15]
    return w

def step(st, w, t):
    a, b, c, d, e, f, g, h = st
    t1 = (h + S1(e) + Ch(e, f, g) + K[t] + w) & M
    t2 = (S0(a) + Maj(a, b, c)) & M
    return [(t1 + t2) & M, a, b, c, (d + t1) & M, e, f, g]

# one verified 39-step factory pair (S115 000fe6c3502f.pair; block-2 messages before the shift)
W1 = [0xdf999706, 0x2e27fe92, 0xc0b21e36, 0x7e4aaabc, 0x9c6c8ceb, 0xd835174b, 0xeecc9fb6, 0x8b60521d,
      0xd96d05aa, 0x36401016, 0x99970fce, 0x571b8884, 0xa942e51e, 0xb01f06bd, 0x43660038, 0xd80d950f]
W2 = [0xdf999706, 0x2e27fe92, 0xc0b21e36, 0x7e4aaabc, 0x9c6c8ceb, 0xd835174b, 0xeecc9fb6, 0x8b60521d,
      0x996d05aa, 0x3ec00016, 0xd9970fce, 0x5119abb0, 0xa952fd1e, 0xb01f06bd, 0x43660038, 0xd80d950f]
W12, W12p = 0xa94ae11e, 0xa95af91e           # the 0f61eb7d / 9993eaa8 advice pair at W12
import math

def splitmix(x):
    x = (x + 0x9e3779b97f4a7c15) & ((1 << 64) - 1)
    z = x
    z = ((z ^ (z >> 30)) * 0xbf58476d1ce4e5b9) & ((1 << 64) - 1)
    z = ((z ^ (z >> 27)) * 0x94d049bb133111eb) & ((1 << 64) - 1)
    return (z ^ (z >> 31)) & ((1 << 64) - 1), x

def r32(state):
    v, state = splitmix(state)
    return v & M, state

def run_trial(seed_hex):
    state = int(hashlib.sha256(bytes.fromhex(seed_hex)).hexdigest(), 16) & ((1 << 64) - 1)
    n1, n2 = shift2(W1), shift2(W2)
    e1, e2 = schedule(n1, 41), schedule(n2, 41)
    o1, o2 = schedule(W1, 39), schedule(W2, 39)
    ident = 1 if all(e1[t] == o1[t - 2] and e2[t] == o2[t - 2] for t in range(2, 41)) else 0
    dN0 = (n2[0] - n1[0]) & M
    dN1 = (n2[1] - n1[1]) & M
    lit = sum(1 for t in range(41) if e1[t] != e2[t])
    # (2) two-step cancellation on random block-1 chaining values
    dg = (-dN1) & M
    ok = 0
    T = 2000
    for _ in range(T):
        c = []
        for _ in range(8):
            v, state = r32(state); c.append(v)
        e, f, g = c[4], c[5], c[6]
        dCh = (Ch(e, f, (g + dg) & M) - Ch(e, f, g)) & M
        dh = (-dN0 - dCh) & M
        c2 = c[:6] + [(g + dg) & M, (c[7] + dh) & M]
        a1 = step(step(c, n1[0], 0), n1[1], 1)
        a2 = step(step(c2, n2[0], 0), n2[1], 1)
        ok += 1 if a1 == a2 else 0
    # (3) set S of cancellable dN0 over the free word N1
    C = (s1(W12p) - s1(W12)) & M
    Sset = set()
    for _ in range(1 << 17):
        w, state = r32(state)
        Sset.add((-C - ((s0((w + (1 << 30)) & M) - s0(w)) & M)) & M)
    Slist = sorted(Sset); r = Slist[0]; v = 32
    for x in Slist:
        d = (x - r) & M
        if d:
            b = (d & -d).bit_length() - 1
            v = b if b < v else v
    U = 0.5 * len(Sset) + 0.5
    base41 = 123.92331
    walk = base41 - 0.5 * math.log2(U)
    lam0 = -math.log(0.61)
    b0 = 116.58624 - math.log2(2968.0 / 2812.0)
    pexact = 0.5 / U

    def success(lw):
        W = 2.0 ** lw; A = 2.0 ** walk; B = 2.0 ** b0; s = 0.0; n = 3000
        for i in range(n):
            t0, t1 = W * i / n, W * (i + 1) / n
            F0 = 1 - math.exp(-lam0 * (t0 / A) ** 2)
            F1 = 1 - math.exp(-lam0 * (t1 / A) ** 2)
            s += (F1 - F0) * (pexact + (1 - pexact) * (1 - math.exp(-lam0 * (W - 0.5 * (t0 + t1)) / B)))
        return s
    lo, hi = walk - 2, walk + 3
    for _ in range(60):
        mid = (lo + hi) / 2
        if success(mid) < 0.39:
            lo = mid
        else:
            hi = mid
    total = hi
    ma = ''.join('%08x' % x for x in n1)
    mb = ''.join('%08x' % x for x in n2)
    obs = {
        "schedule_identity_ok": ident,
        "lit_word_count": lit,
        "dN0": dN0,
        "dN1": dN1,
        "cancel_ok": ok,
        "cancel_total": T,
        "S_size": len(Sset),
        "S_equal_mod_bits": v,
        "usable_U": U,
        "walk_cost_log2": round(walk, 6),
        "block2_b0_log2": round(b0, 6),
        "total_log2": round(total, 6),
    }
    return ma, mb, obs

def main():
    req = json.load(sys.stdin)
    out = []
    for tr in req.get("trials", []):
        try:
            ma, mb, obs = run_trial(tr["seed"])
            out.append({"trial": tr["trial"], "message_a_hex": ma, "message_b_hex": mb, "observations": obs})
        except Exception:
            out.append({"trial": tr["trial"], "message_a_hex": None, "message_b_hex": None})
    json.dump({"schema_version": 1, "trials": out}, sys.stdout)

if __name__ == "__main__":
    main()
