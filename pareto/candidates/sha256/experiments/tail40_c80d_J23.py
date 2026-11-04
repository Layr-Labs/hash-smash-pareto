#!/usr/bin/env python3
"""Tail replica (proof Section 8). Stdlib only. Organizer stdin-JSON trials format.
Uniform random 8-register states S at the junction (state after step J-1, registers a..h), S' = S xor D (D = the
junction pattern), both run through steps J..R-1 with the pair's own expanded schedule words (M, M'); a hit is
S == S' after step R-1 (with equal chaining inputs, equal R-step outputs). Trial 0 hard-asserts the known answers
(the lane-parallel step equals the scalar step; the embedded schedule differences equal the expansion of M, M').
Trials 1..NT each run NB batches of L samples from their organizer seed. Across them the program hard-asserts the
premise p_tail >= 2^DECL is not refuted: the one-sided 99% upper bound of the pooled hit rate is >= 2^DECL."""
import sys, json, math, random
P = {'R': 40, 'J': 23, 'L': 4096, 'NB': 32, 'NT': 32, 'DECL': -24.791, 'M1': ['fd783713', '37fa1eaf', '9c1d5c39', '9fc4bc9a', '3110cb41', '5cf121d6', '18ea6ab4', '3a8c03ba', 'b70de428', '854e243f', '9baacbe0', 'd37ef7a9', 'bd9f4ba1', '142019a1', 'a74c39d5', '4d981480'], 'M2': ['fd783714', '37fa1eaf', '9c1d5c39', '9fc4bc9a', '3110cb41', '5cf121d6', '18ea6ab4', '3a8c03ba', 'b70de428', '854e243e', '9daa8be0', 'd37ef7aa', '459fcbf0', '141ff9a1', 'a74c39d5', '4d981480'], 'D': ['00000000', '00000000', '00000000', '00000001', '00000000', '10440900', '04200080', '00000000'], 'DW': {'0': '00000001', '9': 'ffffffff', '10': '01ffc000', '11': '00000001', '12': '8800804f', '13': 'ffffe000', '17': '01ffc000', '18': '00000001', '25': '0fbbf900', '27': 'ffffffff'}}
R, J, L, NB, NT, DECL = P['R'], P['J'], P['L'], P['NB'], P['NT'], P['DECL']
M = 0xffffffff
K = [int(x, 16) for x in '428a2f98 71374491 b5c0fbcf e9b5dba5 3956c25b 59f111f1 923f82a4 ab1c5ed5 d807aa98 12835b01 243185be 550c7dc3 '
     '72be5d74 80deb1fe 9bdc06a7 c19bf174 e49b69c1 efbe4786 0fc19dc6 240ca1cc 2de92c6f 4a7484aa 5cb0a9dc 76f988da 983e5152 a831c66d '
     'b00327c8 bf597fc7 c6e00bf3 d5a79147 06ca6351 14292967 27b70a85 2e1b2138 4d2c6dfc 53380d13 650a7354 766a0abb 81c2c92e 92722c85 '
     'a2bfe8a1 a81a664b c24b8b70 c76c51a3 d192e819 d6990624 f40e3585 106aa070 19a4c116 1e376c08 2748774c 34b0bcb5 391c0cb3 4ed8aa4a '
     '5b9cca4f 682e6ff3 748f82ee 78a5636f 84c87814 8cc70208 90befffa a4506ceb bef9a3f7 c67178f2'.split()]
def rr(x, n): return ((x >> n) | (x << (32 - n))) & M
def expand(Mh):
    w = [int(x, 16) for x in Mh]
    for t in range(16, R):
        w.append((rr(w[t-2], 17) ^ rr(w[t-2], 19) ^ (w[t-2] >> 10)) + w[t-7] + (rr(w[t-15], 7) ^ rr(w[t-15], 18) ^ (w[t-15] >> 3)) + w[t-16] & M)
    return w
W1, W2 = expand(P['M1']), expand(P['M2'])
D = [int(x, 16) for x in P['D']]
def step1(s, kw):
    a, b, c, d, e, f, g, h = s
    t1 = h + (rr(e, 6) ^ rr(e, 11) ^ rr(e, 25)) + ((e & f) ^ (~e & g & M)) + kw
    t2 = (rr(a, 2) ^ rr(a, 13) ^ rr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))
    return ((t1 + t2) & M, a, b, c, (d + t1) & M, e, f, g)
class Sw:  # L lanes of 64 bits, one 32-bit word per lane (no carry crosses a lane)
    def __init__(w, L):
        w.m = int.from_bytes(M.to_bytes(8, 'little') * L, 'little'); w.o = int.from_bytes((1).to_bytes(8, 'little') * L, 'little'); w.L = L
    def bc(w, c): return (c & M) * w.o
    def r(w, x, n): return ((x >> n) | (x << (32 - n))) & w.m
    def step(w, s, kw):
        a, b, c, d, e, f, g, h = s; m = w.m; r = w.r
        t1 = h + (r(e, 6) ^ r(e, 11) ^ r(e, 25)) + ((e & f) ^ ((e ^ m) & g)) + kw
        t2 = (r(a, 2) ^ r(a, 13) ^ r(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))
        return ((t1 + t2) & m, a, b, c, (d + t1) & m, e, f, g)
    def nzero(w, x): return bin((((x + w.m) >> 32) & w.o) ^ w.o).count('1')
    def get(w, x, i): return (x >> (64 * i)) & M
def run(sw, rng):
    s = tuple(rng.getrandbits(64 * sw.L) & sw.m for _ in range(8))
    s2 = tuple(x ^ sw.bc(d) for x, d in zip(s, D))
    for t in range(J, R):
        s = sw.step(s, sw.bc(K[t] + W1[t])); s2 = sw.step(s2, sw.bc(K[t] + W2[t]))
    x = 0
    for u, v in zip(s, s2): x |= u ^ v
    return sw.nzero(x), s, s2
def kat(seed):
    sw = Sw(64); rng = random.Random(seed + "kat")
    s0 = tuple(rng.getrandbits(64 * 64) & sw.m for _ in range(8)); ok = 1
    for i in (0, 17, 63):
        a = tuple(sw.get(x, i) for x in s0); b = tuple(x ^ d for x, d in zip(a, D)); A, B = s0, tuple(x ^ sw.bc(d) for x, d in zip(s0, D))
        for t in range(J, R):
            a = step1(a, (K[t] + W1[t]) & M); b = step1(b, (K[t] + W2[t]) & M)
            A = sw.step(A, sw.bc(K[t] + W1[t])); B = sw.step(B, sw.bc(K[t] + W2[t]))
            ok &= all(sw.get(X, i) == y for X, y in zip(A, a)) and all(sw.get(X, i) == y for X, y in zip(B, b))
    dw = {str(t): '%08x' % ((W2[t] - W1[t]) & M) for t in range(R) if W1[t] != W2[t]}
    return int(ok and dw == P['DW'])
def main():
    req = json.loads(sys.stdin.read()); tr = req['trials']; n = len(tr)
    assert n > NT, 'the organizer budget gives %d trials; this replica needs %d' % (n, NT + 1)
    k = kat(tr[0]['seed']); assert k == 1
    sw = Sw(L); obs = [None] * n; hits = 0
    for j in range(1, NT + 1):
        rng = random.Random(tr[j]['seed']); h = 0
        for _ in range(NB): h += run(sw, rng)[0]
        obs[j] = {'n': NB * L, 'hits': h}; hits += h
    N = NT * NB * L
    ub = (hits + 2.326348 * math.sqrt(max(hits, 1)) + 1.0) / N        # one-sided 99% upper bound (normal approx., +1 continuity)
    o0 = {'kat': k, 'R': R, 'J': J, 'n_total': N, 'hits_total': hits, 'log2_p_hat': round(math.log2(hits / N), 6) if hits else -999.0,
          'log2_ub99': round(math.log2(ub), 6)}
    if DECL is not None:
        assert math.log2(ub) >= DECL, 'premise refuted: one-sided 99%% upper bound 2^%.4f < declared 2^%s' % (math.log2(ub), DECL)
        o0['decl_not_refuted'] = 1
    obs[0] = o0
    out = [dict({'trial': j, 'message_a_hex': None, 'message_b_hex': None}, **({'observations': obs[j]} if obs[j] else {})) for j in range(n)]
    sys.stdout.write(json.dumps({'schema_version': 1, 'trials': out}, separators=(',', ':')))
if __name__ == '__main__': main()
