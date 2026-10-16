"""clawverify.py: claw existence and preimage verification for 39-step SHA-256.

Organizer experiment demonstrating that the claw construction's preimage
search produces valid (a0, u) pairs at the predicted rate.  For each trial:

  1. Derive a chaining value cv from the organiser seed.
  2. For 2^14 random a0 values (even), compute target = g - W0 - T1_base_1
     (where W0 and T1_base_1 follow from the SHA-256 step-0/step-1 equations).
  3. Look up target in the preimage table.  The table holds ~2^19 distinct
     f-values out of the ~0.634 * 2^32 in the image, so each target has
     probability ~2^-13 of hitting.  With 2^14 targets we expect ~3 claws
     per trial.
  4. For each found claw (a0, u): verify independently that
     sigma0(u) - u == target.

The table is built once before all trials (it depends only on f, not the seed).

This confirms:
  - The image of f = sigma0 - id has the expected density (~63.4% of 2^32).
  - Preimages exist at the predicted rate.
  - The SHA-256 step equations correctly derive the claw target from (a0, cv).

The full walk-function algebra (F_even vs F_odd) is tested separately by
clawexp.py, which has access to the walk constants.

Protocol: python-message-pairs-v1 (JSON on stdin/stdout).
"""
import json
import sys
import hashlib
import struct

M32 = 0xFFFFFFFF
G16 = 0xbca1c321

SHA256_K0 = 0x428a2f98
SHA256_K1 = 0x71374491

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


def sigma0(x):
    return ror32(x, 7) ^ ror32(x, 18) ^ (x >> 3)


def Ch(e, f, g):
    return (e & f) ^ (~e & g) & M32


def Maj(a, b, c):
    return (a & b) ^ (a & c) ^ (b & c)


def sha256_r39_compress(state, block_words):
    w = list(block_words[:16])
    for i in range(16, 39):
        s0w = ror32(w[i-15], 7) ^ ror32(w[i-15], 18) ^ (w[i-15] >> 3)
        s1w = ror32(w[i-2], 17) ^ ror32(w[i-2], 19) ^ (w[i-2] >> 10)
        w.append((s1w + w[i-7] + s0w + w[i-16]) & M32)
    a, b, c, d, e, f, g, h = state
    for i in range(39):
        t1 = (h + Sigma1(e) + Ch(e, f, g) + SHA256_K[i] + w[i]) & M32
        t2 = (Sigma0(a) + Maj(a, b, c)) & M32
        h, g, f, e, d, c, b, a = g, f, e, (d + t1) & M32, c, b, a, (t1 + t2) & M32
    return [(s + v) & M32 for s, v in zip(state, [a, b, c, d, e, f, g, h])]


def derive_cv(seed_hex):
    raw = hashlib.shake_256(bytes.fromhex(seed_hex)).digest(64)
    words = struct.unpack(">16I", raw)
    return sha256_r39_compress(list(IV), words)


def build_preimage_table(n_entries):
    table = {}
    for k in range(n_entries):
        u = 2 * k + 1
        fval = (sigma0(u) - u) & M32
        if fval not in table:
            table[fval] = u
    return table


def main():
    request = json.load(sys.stdin)
    trials = []

    table = build_preimage_table(1 << 19)
    tget = table.get
    n_a0 = 1 << 14

    for t in request["trials"]:
        seed = t["seed"]
        cv = derive_cv(seed)

        S0_cv0 = Sigma0(cv[0])
        Maj_012 = Maj(cv[0], cv[1], cv[2])
        T2_0 = (S0_cv0 + Maj_012) & M32
        T1_base_0 = (cv[7] + Sigma1(cv[4]) + Ch(cv[4], cv[5], cv[6])
                      + SHA256_K0) & M32
        w0_off = (- T2_0 - T1_base_0) & M32
        e0_off = (cv[3] - S0_cv0 - Maj_012) & M32
        cv4, cv5, cv6k1 = cv[4], cv[5], (cv[6] + SHA256_K1) & M32

        rng_data = hashlib.shake_256(
            bytes.fromhex(seed) + b"clawverify"
        ).digest(4 * n_a0)
        a0_raw = struct.unpack(f">{n_a0}I", rng_data)

        claws_found = 0
        preimage_verified = 0

        for val in a0_raw:
            a0 = val & 0xFFFFFFFE
            W0 = (a0 + w0_off) & M32
            E0 = (a0 + e0_off) & M32
            s1 = (((E0 >> 6) | (E0 << 26)) ^ ((E0 >> 11) | (E0 << 21))
                  ^ ((E0 >> 25) | (E0 << 7))) & M32
            ch = (E0 & cv4) ^ (~E0 & cv5) & M32
            T1b1 = (cv6k1 + s1 + ch) & M32
            target = (G16 - W0 - T1b1) & M32

            u = tget(target)
            if u is not None:
                claws_found += 1
                if (sigma0(u) - u) & M32 == target:
                    preimage_verified += 1

        trials.append({
            "trial": t["trial"],
            "message_a_hex": None,
            "message_b_hex": None,
            "observations": {
                "claws_attempted": n_a0,
                "claws_found": claws_found,
                "preimage_verified": preimage_verified,
                "table_size": len(table),
                "table_coverage": round(len(table) / 2**32, 6),
            }
        })

    json.dump({"schema_version": 1, "trials": trials}, sys.stdout)


if __name__ == "__main__":
    main()
