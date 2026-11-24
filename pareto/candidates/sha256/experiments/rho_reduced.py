"""Birthday collision search on 16-bit truncation of SHA-256-r39.

Finds two distinct 32-byte messages whose SHA-256-r39 digests agree on
the low 16 bits, demonstrating random-function-like collision structure.
"""
import json
import struct
import sys

MASK32 = 0xFFFFFFFF
ROUNDS = 39

SHA256_K = (
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
)

SHA256_IV = (
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
)


def _ror(v, n):
    v &= MASK32
    return ((v >> n) | (v << (32 - n))) & MASK32


def sha256_r39(msg):
    ml = len(msg)
    padded = msg + b"\x80" + b"\x00" * ((55 - ml) % 64) + (8 * ml).to_bytes(8, "big")
    h0, h1, h2, h3, h4, h5, h6, h7 = SHA256_IV
    for off in range(0, len(padded), 64):
        w = list(struct.unpack(">16I", padded[off : off + 64]))
        for i in range(16, ROUNDS):
            x, y = w[i - 15], w[i - 2]
            s0 = _ror(x, 7) ^ _ror(x, 18) ^ (x >> 3)
            s1 = _ror(y, 17) ^ _ror(y, 19) ^ (y >> 10)
            w.append((w[i - 16] + s0 + w[i - 7] + s1) & MASK32)
        a, b, c, d, e, f, g, h = h0, h1, h2, h3, h4, h5, h6, h7
        for i in range(ROUNDS):
            s1 = _ror(e, 6) ^ _ror(e, 11) ^ _ror(e, 25)
            ch = (e & f) ^ (~e & g)
            t1 = (h + s1 + ch + SHA256_K[i] + w[i]) & MASK32
            s0 = _ror(a, 2) ^ _ror(a, 13) ^ _ror(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            t2 = (s0 + maj) & MASK32
            a, b, c, d, e, f, g, h = (
                (t1 + t2) & MASK32, a, b, c,
                (d + t1) & MASK32, e, f, g,
            )
        h0 = (h0 + a) & MASK32
        h1 = (h1 + b) & MASK32
        h2 = (h2 + c) & MASK32
        h3 = (h3 + d) & MASK32
        h4 = (h4 + e) & MASK32
        h5 = (h5 + f) & MASK32
        h6 = (h6 + g) & MASK32
        h7 = (h7 + h) & MASK32
    return struct.pack(">8I", h0, h1, h2, h3, h4, h5, h6, h7)


def derive_message(seed_bytes, counter):
    prefix = seed_bytes[:24]
    return prefix + counter.to_bytes(8, "big")


def find_partial_collision(seed_bytes):
    seen = {}
    for ctr in range(1 << 20):
        msg = derive_message(seed_bytes, ctr)
        digest = sha256_r39(msg)
        trunc = (digest[30] << 8) | digest[31]
        if trunc in seen:
            prev_ctr = seen[trunc]
            if prev_ctr != ctr:
                return derive_message(seed_bytes, prev_ctr), msg
        seen[trunc] = ctr
    return None, None


def main():
    request = json.loads(sys.stdin.read())
    trials = []
    for t in request["trials"]:
        seed_bytes = bytes.fromhex(t["seed"])
        msg_a, msg_b = find_partial_collision(seed_bytes)
        if msg_a is not None:
            trials.append({
                "trial": t["trial"],
                "message_a_hex": msg_a.hex(),
                "message_b_hex": msg_b.hex(),
                "observations": {},
            })
        else:
            trials.append({
                "trial": t["trial"],
                "message_a_hex": None,
                "message_b_hex": None,
                "observations": {},
            })
    json.dump({"schema_version": 1, "trials": trials}, sys.stdout)


if __name__ == "__main__":
    main()
