"""Reduced-width check of the random-mapping premise for the three-round BLAKE3 collision claim.

Runs the claim's distinguished-point collision search on a 16-bit truncation of the
three-round digest and returns the colliding message pair for each trial.
Stdlib only, deterministic from the per-trial seed, one JSON request on stdin,
one JSON report on stdout. Event: digest-xor-mask on the first two digest bytes.
"""
import json
import struct
import sys

IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
      0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
M32 = 0xFFFFFFFF
ROUNDS = 3
WIDTH_BYTES = 2            # 16-bit truncated output
THETA_BITS = 4             # distinguished point: low 4 bits of the truncated value are zero
TRAIL_CAP = 16 << THETA_BITS
MAX_STEPS = 1 << 20        # hard stop per trial


def _g(v, a, b, c, d, x, y):
    v[a] = (v[a] + v[b] + x) & M32; v[d] ^= v[a]; v[d] = (v[d] >> 16) | ((v[d] << 16) & M32)
    v[c] = (v[c] + v[d]) & M32;     v[b] ^= v[c]; v[b] = (v[b] >> 12) | ((v[b] << 20) & M32)
    v[a] = (v[a] + v[b] + y) & M32; v[d] ^= v[a]; v[d] = (v[d] >> 8) | ((v[d] << 24) & M32)
    v[c] = (v[c] + v[d]) & M32;     v[b] ^= v[c]; v[b] = (v[b] >> 7) | ((v[b] << 25) & M32)


def compress(cv, m, counter, block_len, flags, rounds):
    v = list(cv) + list(IV[:4]) + [counter & M32, (counter >> 32) & M32, block_len, flags]
    m = list(m)
    for r in range(rounds):
        _g(v, 0, 4, 8, 12, m[0], m[1]); _g(v, 1, 5, 9, 13, m[2], m[3])
        _g(v, 2, 6, 10, 14, m[4], m[5]); _g(v, 3, 7, 11, 15, m[6], m[7])
        _g(v, 0, 5, 10, 15, m[8], m[9]); _g(v, 1, 6, 11, 12, m[10], m[11])
        _g(v, 2, 7, 8, 13, m[12], m[13]); _g(v, 3, 4, 9, 14, m[14], m[15])
        if r != rounds - 1:
            m = [m[i] for i in PERM]
    return [v[i] ^ v[i + 8] for i in range(8)]


def digest64(message):
    """Three-round BLAKE3 of one 64-byte message: one chunk, one block, CHUNK_START|CHUNK_END|ROOT."""
    words = struct.unpack('<16I', message)
    return struct.pack('<8I', *compress(IV, words, 0, 64, 1 | 2 | 8, ROUNDS))


def message_of(x):
    """Message family of the claim: 32 zero bytes followed by the 32-byte little-endian value x."""
    return bytes(32) + x.to_bytes(32, 'little')


def step(x):
    """Truncated digest of message_of(x), read as the next point."""
    return int.from_bytes(digest64(message_of(x))[:WIDTH_BYTES], 'little')


def is_dp(x):
    return x & ((1 << THETA_BITS) - 1) == 0


def walk_back(start_a, len_a, start_b, len_b):
    """Both trails end at the same distinguished point. Return the colliding predecessors."""
    xa, xb = start_a, start_b
    while len_a > len_b:
        xa = step(xa); len_a -= 1
    while len_b > len_a:
        xb = step(xb); len_b -= 1
    if xa == xb:
        return None            # one start lies on the other trail: same input, not a collision
    while True:
        na, nb = step(xa), step(xb)
        if na == nb:
            return xa, xb
        xa, xb = na, nb


def run_trial(seed_hex):
    seed = int(seed_hex, 16)
    table = {}
    steps = 0
    trails = 0
    counter = 0
    while steps < MAX_STEPS:
        # fresh start point derived from the seed (the real search uses an independent random word)
        start = int.from_bytes(digest64(seed.to_bytes(32, 'big') + counter.to_bytes(32, 'big'))[:WIDTH_BYTES], 'little')
        counter += 1
        x, length = start, 0
        while True:
            x = step(x); length += 1; steps += 1
            if is_dp(x) or length >= TRAIL_CAP:
                break
        trails += 1
        if length >= TRAIL_CAP and not is_dp(x):
            continue           # abandoned trail
        if x in table:
            s0, l0 = table[x]
            found = walk_back(s0, l0, start, length)
            if found is None:
                continue
            a, b = found
            return message_of(a), message_of(b), {"evaluations": steps, "trails": trails,
                                                   "stored_points": len(table)}
        table[x] = (start, length)
    return None, None, {"evaluations": steps, "trails": trails, "stored_points": len(table)}


def main():
    request = json.loads(sys.stdin.read())
    out = []
    for item in request["trials"]:
        a, b, obs = run_trial(item["seed"])
        out.append({"trial": item["trial"],
                    "message_a_hex": None if a is None else a.hex(),
                    "message_b_hex": None if b is None else b.hex(),
                    "observations": obs})
    sys.stdout.write(json.dumps({"schema_version": 1, "trials": out}, separators=(',', ':')))


if __name__ == "__main__":
    main()
