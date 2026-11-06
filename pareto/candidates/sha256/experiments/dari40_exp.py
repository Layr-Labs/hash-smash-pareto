#!/usr/bin/env python3
# dari40_exp.py - organizer experiment for the R40 Dariia-characteristic package (sha256-r40-prefix-v1).
# Per trial (seed): a random first block M0 (seeded), its 40-step chaining value CV, and the advice pair (M1, M1') of the
# package (Dariia's HEAD30 witness, artifacts/advice_DARIIA_HEAD30_1104.dec). Reports: the message-schedule difference
# support of the advice pair (words with nonzero difference, 0..39), the rows with zero state difference when both members
# run from the advice chaining value CV*, and the same count from the trial's CV (no transplant is applied here, so this is a
# control, not the claimed algorithm). Candidate messages: M0 || M1 and M0 || M1' (two 64-byte blocks each). No collision is
# expected at organizer scale; the full-collision event is the organizer's check on the returned pair.
import sys, json, random, hashlib
M = 0xFFFFFFFF
K = [int(x, 16) for x in """428a2f98 71374491 b5c0fbcf e9b5dba5 3956c25b 59f111f1 923f82a4 ab1c5ed5 d807aa98 12835b01 243185be 550c7dc3
72be5d74 80deb1fe 9bdc06a7 c19bf174 e49b69c1 efbe4786 0fc19dc6 240ca1cc 2de92c6f 4a7484aa 5cb0a9dc 76f988da 983e5152 a831c66d
b00327c8 bf597fc7 c6e00bf3 d5a79147 06ca6351 14292967 27b70a85 2e1b2138 4d2c6dfc 53380d13 650a7354 766a0abb 81c2c92e 92722c85
a2bfe8a1 a81a664b c24b8b70 c76c51a3 d192e819 d6990624 f40e3585 106aa070 19a4c116 1e376c08 2748774c 34b0bcb5 391c0cb3 4ed8aa4a
5b9cca4f 682e6ff3 748f82ee 78a5636f 84c87814 8cc70208 90befffa a4506ceb bef9a3f7 c67178f2""".split()]
IV = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
NR = 40
def ror(x, k): return ((x >> k) | (x << (32 - k))) & M
def s0(x): return ror(x, 7) ^ ror(x, 18) ^ (x >> 3)
def s1(x): return ror(x, 17) ^ ror(x, 19) ^ (x >> 10)
def S0(x): return ror(x, 2) ^ ror(x, 13) ^ ror(x, 22)
def S1(x): return ror(x, 6) ^ ror(x, 11) ^ ror(x, 25)
def expand(w):
    w = list(w)
    for t in range(16, NR): w.append((s1(w[t - 2]) + w[t - 7] + s0(w[t - 15]) + w[t - 16]) & M)
    return w
def states(cv, w16):
    w = expand(w16); a, b, c, d, e, f, g, h = cv; out = []
    for t in range(NR):
        t1 = (h + S1(e) + ((e & f) ^ (~e & g & M)) + K[t] + w[t]) & M; t2 = (S0(a) + ((a & b) ^ (a & c) ^ (b & c))) & M
        h, g, f, e, d, c, b, a = g, f, e, (d + t1) & M, c, b, a, (t1 + t2) & M
        out.append((a, b, c, d, e, f, g, h))
    return w, out
def compress(cv, w16):
    _, st = states(cv, w16); return [(x + y) & M for x, y in zip(cv, st[-1])]
H = lambda s: [int(x, 16) for x in s.split()]
ADV_CV = H("020890e6 6262283e 9ee680c5 9d11ccbb 4d7755c8 aed03ccc abd15148 bd6c232f")
ADV_M1 = H("df27f5d7 23ebe3a1 271e0559 fe5b91b0 061f5ae9 b907b5fb c8c7cb46 fff2e0a1 569c22c2 c0f154a9 4c289579 b026342e 4b9e8030 4c893e60 96605161 95c96dd6")
ADV_M2 = H("df27f5d7 23ebe3a1 271e0559 fe5b91b0 061f5ae9 b907b5fb c8c7cb46 fff2e0a1 469c22c2 c2d150a9 5c289579 b1a6bce3 4b9a8630 4c893e60 96605161 95c96dd6")
def zero_rows(cv):
    _, sa = states(cv, ADV_M1); _, sb = states(cv, ADV_M2)
    return [t for t in range(NR) if sa[t] == sb[t]]
def words_hex(ws): return "".join("%08x" % x for x in ws)
def trial(seed_hex):
    rng = random.Random(int(seed_hex, 16)); m0 = [rng.getrandbits(32) for _ in range(16)]
    cv = compress(IV, m0)
    wa, wb = expand(ADV_M1), expand(ADV_M2); support = [t for t in range(NR) if wa[t] != wb[t]]
    zr_adv = zero_rows(ADV_CV); zr_cv = zero_rows(cv)
    ha = compress(cv, ADV_M1); hb = compress(cv, ADV_M2)
    EXP = [8, 9, 10, 11, 12, 16, 17, 24, 26, 31, 33, 35, 37, 38, 39]
    ob = {"support_matches_characteristic": int(support == EXP), "support_words": len(support), "zero_rows_from_advice_cv": len(zr_adv),
          "zero_rows_26_30_from_advice_cv": sum(1 for t in zr_adv if 26 <= t <= 30), "zero_rows_from_trial_cv": len(zr_cv), "zero_rows_26_30_from_trial_cv": sum(1 for t in zr_cv if 26 <= t <= 30),
          "advice_cv_matches_trial_cv": int(cv == ADV_CV), "digest_xor_bits": sum(bin(x ^ y).count("1") for x, y in zip(ha, hb)), "ops_used": 2 * 40 * 3 + 40}
    return {"trial": None, "message_a_hex": words_hex(m0) + words_hex(ADV_M1), "message_b_hex": words_hex(m0) + words_hex(ADV_M2), "observations": ob}
def main():
    req = json.loads(sys.stdin.read()); w = sys.stdout.write; w('{"schema_version":1,"trials":['); first = True
    for t in req.get("trials", []):
        r = trial(str(t.get("seed", "1"))); r["trial"] = t.get("trial")
        w(("" if first else ",") + json.dumps(r, separators=(",", ":"))); first = False
    w("]}")
if __name__ == "__main__": main()
