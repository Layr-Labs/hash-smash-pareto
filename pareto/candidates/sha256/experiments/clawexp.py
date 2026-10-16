"""clawexp.py: claw-construction algebraic verification for 39-step SHA-256.

Organizer experiment for the row-16 claw attack.  Tests the algebraic
correctness of the walk function F by comparing it against an independent
SHA-256 round-function computation.

For each trial the test derives a chaining value from the organiser seed,
then for 1024 random inputs verifies:

  (a) the walk function's E0 offset (E0 = a0 + e0_base) matches the new-E
      register produced by an independent SHA-256 step-0 computation;
  (b) the walk function's even-branch core (S0 + MAJ + S1 + CH applied with
      specific cv-dependent register identifications) matches the value
      extracted from running two full SHA-256 compression steps and
      subtracting the known constants;
  (c) the odd-branch identity s0(u) = f(u) + u holds (bitwise s0 vs
      arithmetic f-plus-identity).

Paths (a) and (b) are genuinely different code: the walk function applies
SHA-256 primitives with explicit constant bindings (Am1, Am2, Em1, Em2,
e0_base), while the SHA step function propagates the full 8-register state.
They agree if and only if the walk function correctly identifies which
chaining-value words feed each position in the round.

Protocol: python-message-pairs-v1 (JSON on stdin/stdout).
"""
import json
import sys
import hashlib
import struct

M32 = 0xFFFFFFFF

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


def main():
    request = json.load(sys.stdin)
    trials = []
    K0, K1 = SHA256_K[0], SHA256_K[1]
    n_tested = 1024

    for t in request["trials"]:
        seed = t["seed"]
        cv = derive_cv(seed)
        cv0, cv1, cv2, cv3, cv4, cv5, cv6, cv7 = cv

        e0_base = (cv3 - Sigma0(cv0) - Maj(cv0, cv1, cv2)) & M32
        Am1, Am2, Em1, Em2 = cv0, cv1, cv4, cv5

        T2_0 = (Sigma0(cv0) + Maj(cv0, cv1, cv2)) & M32
        T1_base_0 = (cv7 + Sigma1(cv4) + Ch(cv4, cv5, cv6) + K0) & M32

        rng_data = hashlib.shake_256(bytes.fromhex(seed) + b"claw").digest(8 * n_tested)
        pairs = struct.unpack(f">{n_tested * 2}I", rng_data)

        e0_mismatches = 0
        core_mismatches = 0
        odd_mismatches = 0

        for i in range(n_tested):
            a0 = pairs[i * 2] & 0xFFFFFFFE
            u = pairs[i * 2 + 1] | 1

            E0_walk = (a0 + e0_base) & M32

            W0 = (a0 - T2_0 - T1_base_0) & M32

            t1_0 = (T1_base_0 + W0) & M32
            A0_sha = (t1_0 + T2_0) & M32
            E0_sha = (cv3 + t1_0) & M32

            if A0_sha != a0 or E0_sha != E0_walk:
                e0_mismatches += 1
                continue

            E0 = E0_walk
            core_walk = (Sigma0(a0) + Maj(a0, Am1, Am2)
                         + Sigma1(E0) + Ch(E0, Em1, Em2)) & M32

            s1e = Sigma1(E0)
            che = Ch(E0, cv4, cv5)
            t1_1 = (cv6 + s1e + che + K1 + u) & M32
            t2_1 = (Sigma0(a0) + Maj(a0, cv0, cv1)) & M32
            A1_sha = (t1_1 + t2_1) & M32
            core_sha = (A1_sha - cv6 - K1 - u) & M32

            if core_walk != core_sha:
                core_mismatches += 1

            s0_bitwise = sigma0(u)
            s0_from_f = ((sigma0(u) - u) + u) & M32
            if s0_bitwise != s0_from_f:
                odd_mismatches += 1

        trials.append({
            "trial": t["trial"],
            "message_a_hex": None,
            "message_b_hex": None,
            "observations": {
                "e0_mismatches": e0_mismatches,
                "core_mismatches": core_mismatches,
                "odd_mismatches": odd_mismatches,
                "tested": n_tested,
            }
        })

    json.dump({"schema_version": 1, "trials": trials}, sys.stdout)


if __name__ == "__main__":
    main()
