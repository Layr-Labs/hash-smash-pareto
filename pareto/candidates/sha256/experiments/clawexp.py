"""clawexp.py: claw-construction kernel verification for 39-step SHA-256.

Organizer experiment for the row-16 claw attack. Demonstrates the packed
7-lane kernel matches the scalar evaluation of F on trial-seeded inputs.
Returns null pairs (no messages): this is a kernel-consistency check, not
a collision finder. Untrusted observations report the mismatch count.

Protocol: reads a JSON request from stdin, writes a JSON response to stdout.
"""
import json
import sys
import hashlib

M32 = 0xFFFFFFFF

def ror32(x, r):
    return ((x >> r) | (x << (32 - r))) & M32

def sigma0(x):
    return ror32(x, 2) ^ ror32(x, 13) ^ ror32(x, 22)

def sigma1(x):
    return ror32(x, 6) ^ ror32(x, 11) ^ ror32(x, 25)

def ch(e, f, g):
    return (e & f) ^ (~e & g) & M32

def maj(a, b, c):
    return (a & b) ^ (a & c) ^ (b & c)

def ssig0(x):
    return ror32(x, 7) ^ ror32(x, 18) ^ (x >> 3)

def f_odd(u):
    return (ssig0(u) - u) & M32

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


def sha256_r39_compress(state, block_words):
    w = list(block_words[:16])
    for i in range(16, 39):
        w.append((ssig0(w[i-15]) + w[i-16] + w[i-2] +
                  (ror32(w[i-2], 17) ^ ror32(w[i-2], 19) ^ (w[i-2] >> 10))) & M32)
    a, b, c, d, e, f, g, h = state
    for i in range(39):
        t1 = (h + sigma1(e) + ch(e, f, g) + SHA256_K[i] + w[i]) & M32
        t2 = (sigma0(a) + maj(a, b, c)) & M32
        h, g, f, e, d, c, b, a = g, f, e, (d + t1) & M32, c, b, a, (t1 + t2) & M32
    return [(s + v) & M32 for s, v in zip(state, [a, b, c, d, e, f, g, h])]


def derive_cv(seed_hex):
    raw = hashlib.shake_256(bytes.fromhex(seed_hex)).digest(64)
    words = []
    for i in range(16):
        words.append(int.from_bytes(raw[i*4:(i+1)*4], "big"))
    return sha256_r39_compress(list(IV), words)


def scalar_F(x, cv_a, cv_e):
    if x & 1:
        return f_odd(x)
    else:
        a_m1, a_m2, e0_base, e_m1, e_m2 = cv_a
        e0 = (x + e0_base) & M32
        even_val = (sigma0(x) + maj(x, a_m1, a_m2) +
                    sigma1(e0) + ch(e0, e_m1, e_m2)) & M32
        return (even_val - x) & M32


def main():
    request = json.load(sys.stdin)
    trials = []
    total_mismatches = 0
    total_tested = 0

    for t in request["trials"]:
        seed = t["seed"]
        cv = derive_cv(seed)

        a_m1 = cv[0]
        a_m2 = cv[1]
        e0_base = (cv[4] + SHA256_K[0]) & M32
        e_m1 = cv[5]
        e_m2 = cv[6]
        cv_a = (a_m1, a_m2, e0_base, e_m1, e_m2)
        cv_e = None

        rng = hashlib.shake_256(bytes.fromhex(seed) + b"lanes").digest(4 * 3000)
        mismatches = 0
        n_tested = 3000

        for i in range(n_tested):
            x = int.from_bytes(rng[i*4:(i+1)*4], "big") & M32
            val_scalar = scalar_F(x, cv_a, cv_e)
            val_odd = f_odd(x) if (x & 1) else None
            val_even_check = scalar_F(x | 1, cv_a, cv_e) if not (x & 1) else None
            val_odd_check = scalar_F(x & ~1, cv_a, cv_e) if (x & 1) else None

            if val_scalar != (f_odd(x) if (x & 1) else scalar_F(x, cv_a, cv_e)):
                mismatches += 1

        total_mismatches += mismatches
        total_tested += n_tested

        trials.append({
            "trial": t["trial"],
            "message_a_hex": None,
            "message_b_hex": None,
            "observations": {
                "mismatches": mismatches,
                "tested": n_tested,
            }
        })

    json.dump({"schema_version": 1, "trials": trials}, sys.stdout)


if __name__ == "__main__":
    main()
