"""clawverify.py: claw existence rate for the 39-step row-16 construction.

Organizer experiment measuring how often the claw construction's preimage
search succeeds.  For each trial:

  1. Derive a chaining value cv from the organiser seed.
  2. For 2^13 random even a0, evaluate the walk function's even branch
     F_even(a0) = C + S0(a0) + MAJ(a0, Am1, Am2) + S1(E0) + CH(E0, Em1, Em2) - a0
     with E0 = a0 + e0, which is the branch given in proof.md Section 6 and
     implemented identically in kernelcount.py.  A claw needs an odd u with
     f(u) = F_even(a0), where f(u) = s0(u) - u.
  3. Look up that value in a preimage table of f over the 2^19 smallest odd u.
  4. Count the hits.  With a 2^19-entry table the expected count is
     2^13 * table_size / 2^32 = 1.00 claws per trial.

The table is built once before all trials (it depends only on f, not the seed).

What this measures, and only this: the rate at which a random even a0 produces
a hit in a table of fixed size.  That rate is table_size / 2^32 per target,
which is arithmetic, not a property of f -- so the experiment confirms the
construction runs and produces (a0, u) pairs at the rate the table size
predicts, and nothing stronger.

What it does NOT do, stated explicitly because earlier versions of this file
claimed otherwise:

  * It does not verify preimages.  A u returned by table[v] satisfies
    f(u) == v by construction, so such a check is a dictionary-key identity
    and is not performed here.
  * It does not measure the image density of f.  The table is built from the
    2^19 smallest odd u, a structured subset, not a sample of f's image.
  * It does not establish the full-scale claw rate, which is premise H2.

The constant C is seed-derived rather than taken from the filed base: the hit
rate does not depend on its value.

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
    n_a0 = 1 << 13

    for t in request["trials"]:
        seed = t["seed"]
        cv = derive_cv(seed)

        # The walk function's register identifications, exactly as in
        # proof.md Section 6 and kernelcount.py: Am1 = cv[0], Am2 = cv[1],
        # Em1 = cv[4], Em2 = cv[5], e0 = cv[3] - S0(cv[0]) - MAJ(cv[0], cv[1], cv[2]).
        e0_off = (cv[3] - Sigma0(cv[0]) - Maj(cv[0], cv[1], cv[2])) & M32
        Am1, Am2, Em1, Em2 = cv[0], cv[1], cv[4], cv[5]
        Cc = struct.unpack(">I", hashlib.shake_256(
            bytes.fromhex(seed) + b"clawC").digest(4))[0]

        rng_data = hashlib.shake_256(
            bytes.fromhex(seed) + b"clawverify"
        ).digest(4 * n_a0)
        a0_raw = struct.unpack(f">{n_a0}I", rng_data)

        claws_found = 0
        odd_u = 0

        for val in a0_raw:
            a0 = val & 0xFFFFFFFE
            E0 = (a0 + e0_off) & M32
            target = (Cc + Sigma0(a0) + Maj(a0, Am1, Am2)
                      + Sigma1(E0) + Ch(E0, Em1, Em2) - a0) & M32

            u = tget(target)
            if u is not None:
                claws_found += 1
                if u & 1:
                    odd_u += 1

        trials.append({
            "trial": t["trial"],
            "message_a_hex": None,
            "message_b_hex": None,
            "observations": {
                "claws_attempted": n_a0,
                "claws_found": claws_found,
                "odd_u": odd_u,
                "table_size": len(table),
                "table_coverage": round(len(table) / 2**32, 6),
            }
        })

    json.dump({"schema_version": 1, "trials": trials}, sys.stdout)


if __name__ == "__main__":
    main()
