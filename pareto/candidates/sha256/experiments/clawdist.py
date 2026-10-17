"""clawdist.py: the per-claw factors measured under the CLAW-SELECTED distribution.

Organizer experiment closing the gap every earlier experiment left open.

The per-claw exponent multiplies three factors: the side conditions (2^-9.81),
row 17 (2^-32) and the tail (2^-77.96).  Until now all three were evaluated
under distributions the attack does not produce:

  * sidecond.py  samples W8 and W9 as independent uniform 32-bit words;
  * jointside.py samples (a0, a1) uniformly -- and the factorization is then an
    identity, because W8 = C(a1) - a0 with a0 free, so it cannot fail;
  * the row-17 factor assumes W17 uniform on 2^32.

The attack produces none of those.  Its claws come from the two-sided walk, so
every claw has **a0 even and u odd**, and a0 is not free: it is selected jointly
with u by the claw relation f(u) = F_even(a0).  a1 = u - h(a0, cv) is then
determined, and W8, W9 and W17 follow.

This experiment constructs genuine claws and measures the factors on them.

Per trial:
  1. Derive cv from the organizer seed and the walk constants.
  2. Draw random EVEN a0, evaluate F_even(a0), and look it up in a preimage
     table of f(u) = s0(u) - u built over ODD u.  A hit is a real claw (a0, u)
     satisfying the same relation the attack's vOW search satisfies.
  3. For each claw, recover a1 = u - h(a0, cv), run the schedule relations of
     the filed base b1 to get W0..W9 and then W16, W17, and test both exact
     modular sigma0 side conditions and record W17.

Reported: the side-condition counts on claw-selected variants, and the low-bit
distribution of W17 over claws, which is the premise that buys the -32 term.

Scope limits, stated plainly:
  * The preimage table covers 2^21 of the 2^31 odd u, so a claw here is one
    whose u lies in that table.  The table is a prefix of the odd integers, not
    a random subset, which is a restriction on u beyond oddness.
  * Claw counts per trial are small, so the resolution is limited; the
    hypothesis states the achieved resolution rather than claiming more.
  * This measures the side conditions and W17.  It does NOT measure the tail
    under claw selection, which remains the open part of premise H4.

Protocol: python-message-pairs-v1 (JSON on stdin/stdout).
"""
import json
import sys
import hashlib
import math
import struct
from array import array

M32 = 0xFFFFFFFF

D8, DS8 = 0x40000000, 0x087ff000
D9, DS9 = 0xf7801000, 0x03010000

# Filed dense base b1, member x (proof.md Appendix B).
BASE_A = {2: 0x11b4d46d, 3: 0xe9bdf656, 4: 0x9f0216f0, 5: 0x583f3ec8,
          6: 0x73a03068, 7: 0xcaeefa06, 8: 0x29f1c95e, 9: 0xc76d0d7b}
BASE_E = {6: 0x8f5f9eda, 7: 0x3a20889f, 8: 0x94dfb329, 9: 0xac230e77}
BASE_W = {10: 0xdf4464b2, 11: 0xd1007b3b, 12: 0xe8d6fe22,
          13: 0xb06304c1, 14: 0x43660040, 15: 0x4891771f}

G16_TARGET = 0xbca1c321      # the one G16 word admitting a row-17 word
TABLE_LOG2 = 21
SLOTS_LOG2 = 22
A0_PER_TRIAL = 1 << 13
W17_BITS = 6

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


def sigma0(x):
    return ror32(x, 7) ^ ror32(x, 18) ^ (x >> 3)


def sigma1(x):
    return ror32(x, 17) ^ ror32(x, 19) ^ (x >> 10)


def sha256_r39_compress(state, block_words):
    w = list(block_words[:16])
    for i in range(16, 39):
        w.append((sigma1(w[i - 2]) + w[i - 7] + sigma0(w[i - 15]) + w[i - 16]) & M32)
    a, b, c, d, e, f, g, h = state
    for i in range(39):
        t1 = (h + Sigma1(e) + Ch(e, f, g) + SHA256_K[i] + w[i]) & M32
        t2 = (Sigma0(a) + Maj(a, b, c)) & M32
        h, g, f, e, d, c, b, a = g, f, e, (d + t1) & M32, c, b, a, (t1 + t2) & M32
    return [(s + v) & M32 for s, v in zip(state, [a, b, c, d, e, f, g, h])]


def derive_cv(seed_hex):
    raw = hashlib.shake_256(bytes.fromhex(seed_hex)).digest(64)
    return sha256_r39_compress(list(IV), struct.unpack(">16I", raw))


def build_table():
    """Open-addressed preimage table for f over the 2^21 smallest odd u.

    Two flat arrays rather than a dict: a dict of this size does not fit the
    organizer's 128 MB, while these are 2 x 2^22 x 4 bytes = 32 MB.
    """
    n = 1 << SLOTS_LOG2
    mask = n - 1
    keys = array('I', bytes(4 * n))
    vals = array('I', bytes(4 * n))
    used = array('B', bytes(n))
    for k in range(1 << TABLE_LOG2):
        u = 2 * k + 1
        fv = (sigma0(u) - u) & M32
        i = (fv * 2654435761) & mask
        while used[i]:
            if keys[i] == fv:
                break
            i = (i + 1) & mask
        if not used[i]:
            used[i] = 1
            keys[i] = fv
            vals[i] = u
    return keys, vals, used, mask


def schedule(a0, a1, cv, A_base, E_base):
    """W0..W9 of the variant (a0, a1) over the filed base."""
    A = {-4: cv[3], -3: cv[2], -2: cv[1], -1: cv[0], 0: a0, 1: a1}
    A.update(A_base)
    E = {-4: cv[7], -3: cv[6], -2: cv[5], -1: cv[4]}
    for j in range(6):
        E[j] = (A[j] + A[j - 4] - Sigma0(A[j - 1])
                - Maj(A[j - 1], A[j - 2], A[j - 3])) & M32
    E.update(E_base)
    return [(E[j] - A[j - 4] - E[j - 4] - Sigma1(E[j - 1])
             - Ch(E[j - 1], E[j - 2], E[j - 3]) - SHA256_K[j]) & M32
            for j in range(10)]


def main():
    request = json.load(sys.stdin)
    trials = []
    keys, vals, used, mask = build_table()
    table_entries = sum(used)

    A_base = {i: BASE_A[i] for i in range(2, 10)}
    E_base = {i: BASE_E[i] for i in range(6, 10)}
    W10, W14, W15 = BASE_W[10], BASE_W[14], BASE_W[15]

    for t in request["trials"]:
        seed = t["seed"]
        cv = derive_cv(seed)
        Am1, Am2, Am3, Am4 = cv[0], cv[1], cv[2], cv[3]
        Em1, Em2, Em3, Em4 = cv[4], cv[5], cv[6], cv[7]
        e0 = (Am4 - Sigma0(Am1) - Maj(Am1, Am2, Am3)) & M32
        # The real constant of the even branch, derived from the base rather
        # than seeded, so that a claw makes W16 land exactly on g.  Following
        # proof.md Section 2: k0 is the W0 offset and C folds the rest.
        k0 = (e0 - Am4 - Em4 - Sigma1(Em1) - Ch(Em1, Em2, Em3) - SHA256_K[0]) & M32
        w00 = schedule(0, 0, cv, A_base, E_base)       # the a0 = a1 = 0 variant
        Cc = (G16_TARGET - sigma1(BASE_W[14]) - w00[9] - k0 + Em3
              + SHA256_K[1]) & M32

        # Fold the two-constant forms the kernel uses (proof.md Appendix F):
        # MAJ(x, Am1, Am2) = (x & (Am1 ^ Am2)) ^ (Am1 & Am2) and
        # CH(E0, Em1, Em2) = (E0 & (Em1 ^ Em2)) ^ Em2, so the hot loop below
        # costs two operations each instead of five and four.
        MJ_X, MJ_C = Am1 ^ Am2, Am1 & Am2
        CH_X, CH_C = Em1 ^ Em2, Em2

        rng = hashlib.shake_256(bytes.fromhex(seed) + b"clawdist")
        raw = rng.digest(4 * A0_PER_TRIAL)
        unpack = struct.unpack_from

        claws = 0
        w16_ok = w1_ok = 0
        pass8 = pass9 = pass_both = 0
        w17_hist = [0] * (1 << W17_BITS)
        a0_even = u_odd = 0

        for idx in range(A0_PER_TRIAL):
            a0 = unpack(">I", raw, 4 * idx)[0] & 0xFFFFFFFE
            E0 = (a0 + e0) & M32
            s0a = (((a0 >> 2) | (a0 << 30)) ^ ((a0 >> 13) | (a0 << 19))
                   ^ ((a0 >> 22) | (a0 << 10))) & M32
            s1e = (((E0 >> 6) | (E0 << 26)) ^ ((E0 >> 11) | (E0 << 21))
                   ^ ((E0 >> 25) | (E0 << 7))) & M32
            fv = (Cc + s0a + ((a0 & MJ_X) ^ MJ_C)
                  + s1e + ((E0 & CH_X) ^ CH_C) - a0) & M32
            i = (fv * 2654435761) & mask
            u = 0
            while used[i]:
                if keys[i] == fv:
                    u = vals[i]
                    break
                i = (i + 1) & mask
            if not u:
                continue

            claws += 1
            if not (a0 & 1):
                a0_even += 1
            if u & 1:
                u_odd += 1

            # a1 from u: W1 = u = a1 + h(a0, cv), and the schedule gives
            # W1 = E1 - A[-3] - E[-3] - S1(E0) - CH(E0, Em1, Em2) - K1 with
            # E1 = A1 + A[-3] - S0(A0) - MAJ(A0, Am1, Am2), so W1 is a1 plus a
            # constant in a0; invert it directly.
            h_a0 = (-Am3 - Sigma0(a0) - Maj(a0, Am1, Am2) + Am3
                    - Em3 - Sigma1(E0) - Ch(E0, Em1, Em2) - SHA256_K[1]) & M32
            a1 = (u - h_a0) & M32

            W = schedule(a0, a1, cv, A_base, E_base)

            # End-to-end check through the REAL message expansion: build the
            # full 16-word block and expand it, and require W16 = g.  This is
            # the claw construction's central claim, and nothing in earlier
            # filings exercised it inside the package.
            blk = W + [BASE_W[i] for i in range(10, 16)]
            w16 = (sigma1(blk[14]) + blk[9] + sigma0(blk[1]) + blk[0]) & M32
            if w16 == G16_TARGET:
                w16_ok += 1
            if blk[1] == u:
                w1_ok += 1

            w8, w9 = W[8], W[9]
            s0_w8 = sigma0(w8)
            ok8 = ((sigma0((w8 + D8) & M32) - s0_w8) & M32) == DS8
            s0_w9 = sigma0(w9)
            ok9 = ((sigma0((w9 + D9) & M32) - s0_w9) & M32) == DS9
            if ok8:
                pass8 += 1
            if ok9:
                pass9 += 1
            if ok8 and ok9:
                pass_both += 1

            w17 = (sigma1(W15) + W10 + sigma0(blk[2]) + blk[1]) & M32
            w17_hist[w17 & ((1 << W17_BITS) - 1)] += 1

        observations = {
            "a0_tried": A0_PER_TRIAL,
            "claws": claws,
            "claws_a0_even": a0_even,
            "claws_u_odd": u_odd,
            "pass_w8": pass8,
            "pass_w9": pass9,
            "pass_both": pass_both,
            "w16_equals_g": w16_ok,
            "w1_equals_u": w1_ok,
            "table_entries": table_entries,
        }
        if claws:
            exp = claws / (1 << W17_BITS)
            chi2 = sum((c - exp) ** 2 / exp for c in w17_hist) if exp > 0 else 0.0
            observations["w17_chi2"] = round(chi2, 3)
            observations["w17_bins"] = 1 << W17_BITS
        trials.append({
            "trial": t["trial"],
            "message_a_hex": None,
            "message_b_hex": None,
            "observations": observations,
        })

    json.dump({"schema_version": 1, "trials": trials}, sys.stdout)


if __name__ == "__main__":
    main()
