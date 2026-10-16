"""jointside.py: JOINT side-condition rate on real variant words (39-step claw attack).

Organizer experiment answering a specific gap in the filed ledger.  The
per-claw success exponent multiplies the two side-condition rates,

    p8 x p9 = 2^-3.830 x 2^-5.978 = 2^-9.808,

as if the two events were independent.  The earlier experiment (sidecond.py)
samples W8 and W9 as two *independent uniform* 32-bit words, which cannot see
any dependence: it measures the marginals and nothing else.

But W8 and W9 are not independent draws.  In the two-block variant attack both
are derived from the same two free words (a0, a1) through the message
schedule.  Writing A[0] = a0, A[1] = a1 and taking A[2..5], E[6..9] and
W[10..15] from the filed dense base b1:

    E[i] = A[i] + A[i-4] - S0(A[i-1]) - MAJ(A[i-1], A[i-2], A[i-3])   i = 0..5
    W[i] = E[i] - A[i-4] - E[i-4] - S1(E[i-1]) - CH(E[i-1], E[i-2], E[i-3]) - K[i]

E[5] = a1 + const, so W9 = c9 - a1 depends on a1 alone, while W8 depends on
both a0 and a1 -- through E[4] and through CH(E[7], E[6], E[5]).

IMPORTANT, and the reason this file's earlier description was wrong: a0 enters
W8 only as a single additive term.  Expanding,

    E[4] = A4 + a0 - S0(A3) - MAJ(A3, A2, a1)
    W8   = [E8 - A4 - S1(E7) - K8] - E[4] - CH(E7, E6, E[5])
         = C(a1) - a0                                    for a constant C(a1)

so for every fixed a1, as a0 ranges uniformly over 2^32 the word W8 is uniform
and independent of a1.  Hence under the variant distribution with a0 and a1
drawn uniformly and independently,

    P(cond8 AND cond9) = p8 * p9       EXACTLY, as an identity, not an estimate.

This experiment therefore CANNOT refute the factorization, and no run of it
should be read as evidence for it.  The factorization under uniform (a0, a1)
is a theorem, proved above in two lines, and that is the right support for it.

What the run is still worth: it is a numerical consistency check that the
implemented schedule relations really do reproduce the exhaustively computed
marginals p8 and p9 on variant-derived words rather than on uniform words, and
that the derivation of W8 and W9 from (a0, a1) is implemented correctly.  If
the schedule were coded wrongly the marginals would drift off their exhaustive
values and that would show.

Scope limit, which is where the real open question lives: under claw selection
a0 is NOT free.  The claw fixes the pair (a0, u) and hence a1, so the very
uniformity of a0 that makes the identity above hold is unavailable in the
attack.  The factorization under the claw-selected distribution is premise H4
and is neither proved nor measured here or anywhere else in the package.

Protocol: python-message-pairs-v1 (JSON on stdin/stdout).
"""
import json
import sys
import hashlib
import math
import struct

M32 = 0xFFFFFFFF

# Modular differences imposed by the characteristic, derived from the filed
# dense base b1 (proof.md Appendix B): D = Wy - Wx, DS = s0(Wy) - s0(Wx).
D8 = 0x40000000
DS8 = 0x087ff000
D9 = 0xf7801000
DS9 = 0x03010000

# Filed dense base b1, member x (proof.md Appendix B).  Only the words that
# enter W8 and W9 are needed here.
BASE_A = {2: 0x11b4d46d, 3: 0xe9bdf656, 4: 0x9f0216f0, 5: 0x583f3ec8}
BASE_E = {6: 0x8f5f9eda, 7: 0x3a20889f, 8: 0x94dfb329, 9: 0xac230e77}

K8, K9 = 0xd807aa98, 0x12835b01

SHA256_K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e,
]

IV = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]


def ror32(x, r):
    return ((x >> r) | (x << (32 - r))) & M32


def Sigma0(x):
    return ror32(x, 2) ^ ror32(x, 13) ^ ror32(x, 22)


def Sigma1(x):
    return ror32(x, 6) ^ ror32(x, 11) ^ ror32(x, 25)


def Ch(e, f, g):
    return (e & f) ^ (~e & g) & M32


def Maj(a, b, c):
    return (a & b) ^ (a & c) ^ (b & c)


def sha256_r39_compress(state, block_words):
    w = list(block_words[:16])
    for i in range(16, 39):
        s0w = ror32(w[i - 15], 7) ^ ror32(w[i - 15], 18) ^ (w[i - 15] >> 3)
        s1w = ror32(w[i - 2], 17) ^ ror32(w[i - 2], 19) ^ (w[i - 2] >> 10)
        w.append((s1w + w[i - 7] + s0w + w[i - 16]) & M32)
    a, b, c, d, e, f, g, h = state
    for i in range(39):
        t1 = (h + Sigma1(e) + Ch(e, f, g) + SHA256_K[i] + w[i]) & M32
        t2 = (Sigma0(a) + Maj(a, b, c)) & M32
        h, g, f, e, d, c, b, a = g, f, e, (d + t1) & M32, c, b, a, (t1 + t2) & M32
    return [(s + v) & M32 for s, v in zip(state, [a, b, c, d, e, f, g, h])]


def derive_cv(seed_hex):
    raw = hashlib.shake_256(bytes.fromhex(seed_hex)).digest(64)
    return sha256_r39_compress(list(IV), struct.unpack(">16I", raw))


def main():
    request = json.load(sys.stdin)
    trials = []
    n_sample = 1 << 12

    for t in request["trials"]:
        seed = t["seed"]
        cv = derive_cv(seed)
        # A[-1-j] = cv[j]; the base supplies A[2..5] and E[6..9].
        Am1, Am2, Am3, Am4 = cv[0], cv[1], cv[2], cv[3]
        A2, A3, A4, A5 = BASE_A[2], BASE_A[3], BASE_A[4], BASE_A[5]
        E6, E7, E8, E9 = BASE_E[6], BASE_E[7], BASE_E[8], BASE_E[9]

        # Quantities that do not move with (a0, a1).
        s1_E7 = Sigma1(E7)
        s1_E8 = Sigma1(E8)
        ch_876 = Ch(E8, E7, E6)
        # E[5] = A5 + A1 - S0(A4) - MAJ(A4, A3, A2) = a1 + e5_base
        e5_base = (A5 - Sigma0(A4) - Maj(A4, A3, A2)) & M32
        # W9 = E9 - A5 - E5 - S1(E8) - CH(E8, E7, E6) - K9  (depends on a1 only)
        w9_base = (E9 - A5 - s1_E8 - ch_876 - K9) & M32
        # W8 = E8 - A4 - E4 - S1(E7) - CH(E7, E6, E5) - K8
        w8_base = (E8 - A4 - s1_E7 - K8) & M32

        rng = hashlib.shake_256(bytes.fromhex(seed) + b"jointside")
        raw = rng.digest(8 * n_sample)

        pass8 = 0
        pass9 = 0
        pass_both = 0

        for i in range(n_sample):
            a0, a1 = struct.unpack_from(">II", raw, 8 * i)
            # E[4] = A4 + A0 - S0(A3) - MAJ(A3, A2, A1)
            e4 = (A4 + a0 - Sigma0(A3) - Maj(A3, A2, a1)) & M32
            e5 = (e5_base + a1) & M32
            w9 = (w9_base - e5) & M32
            w8 = (w8_base - e4 - Ch(E7, E6, e5)) & M32

            s0_w8 = ror32(w8, 7) ^ ror32(w8, 18) ^ (w8 >> 3)
            w8p = (w8 + D8) & M32
            s0_w8p = ror32(w8p, 7) ^ ror32(w8p, 18) ^ (w8p >> 3)
            ok8 = ((s0_w8p - s0_w8) & M32) == DS8

            s0_w9 = ror32(w9, 7) ^ ror32(w9, 18) ^ (w9 >> 3)
            w9p = (w9 + D9) & M32
            s0_w9p = ror32(w9p, 7) ^ ror32(w9p, 18) ^ (w9p >> 3)
            ok9 = ((s0_w9p - s0_w9) & M32) == DS9

            if ok8:
                pass8 += 1
            if ok9:
                pass9 += 1
            if ok8 and ok9:
                pass_both += 1

        observations = {
            "n_sample": n_sample,
            "pass_w8": pass8,
            "pass_w9": pass9,
            "pass_both": pass_both,
        }
        if pass8 > 0:
            observations["log2_p8"] = round(math.log2(pass8 / n_sample), 4)
        if pass9 > 0:
            observations["log2_p9"] = round(math.log2(pass9 / n_sample), 4)
        if pass_both > 0:
            observations["log2_joint"] = round(math.log2(pass_both / n_sample), 4)

        trials.append({
            "trial": t["trial"],
            "message_a_hex": None,
            "message_b_hex": None,
            "observations": observations,
        })

    json.dump({"schema_version": 1, "trials": trials}, sys.stdout)


if __name__ == "__main__":
    main()
