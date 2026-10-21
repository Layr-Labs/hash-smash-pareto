"""Toy birthday search on the r7 BLAKE3 digest, masked to 12 bits.

Self-contained (stdlib only) organizer experiment. Reads one JSON request on
stdin and writes one strict JSON document on stdout. For each trial it derives
fresh 32-byte candidate messages from the organizer seed and returns the first
pair whose r7 digests agree on the organizer-declared 12-bit mask.

Scope: it corroborates the search loop and the birthday scaling at a 12-bit
mask (expected ~sqrt(pi/2 * 2^12) = 80 evaluations per trial). It does not
corroborate, and is not offered as evidence for, the declared 2^128 cost.
"""
import hashlib
import json
import struct
import sys

IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
      0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERMUTATION = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
CHUNK_START, CHUNK_END, PARENT, ROOT = 1, 2, 4, 8
MASK32 = 0xFFFFFFFF
ROUNDS = 7


def _ror(value, count):
    return ((value >> count) | (value << (32 - count))) & MASK32


def _g(v, a, b, c, d, x, y):
    v[a] = (v[a] + v[b] + x) & MASK32
    v[d] = _ror(v[d] ^ v[a], 16)
    v[c] = (v[c] + v[d]) & MASK32
    v[b] = _ror(v[b] ^ v[c], 12)
    v[a] = (v[a] + v[b] + y) & MASK32
    v[d] = _ror(v[d] ^ v[a], 8)
    v[c] = (v[c] + v[d]) & MASK32
    v[b] = _ror(v[b] ^ v[c], 7)


def _digest32(message):
    """First 32 root-output bytes for a 32-byte message (one compression)."""
    words = list(struct.unpack("<8I", message)) + [0] * 8
    v = list(IV) + list(IV[:4]) + [0, 0, len(message), CHUNK_START | CHUNK_END | ROOT]
    m = list(words)
    for _ in range(ROUNDS):
        _g(v, 0, 4, 8, 12, m[0], m[1])
        _g(v, 1, 5, 9, 13, m[2], m[3])
        _g(v, 2, 6, 10, 14, m[4], m[5])
        _g(v, 3, 7, 11, 15, m[6], m[7])
        _g(v, 0, 5, 10, 15, m[8], m[9])
        _g(v, 1, 6, 11, 12, m[10], m[11])
        _g(v, 2, 7, 8, 13, m[12], m[13])
        _g(v, 3, 4, 9, 14, m[14], m[15])
        m = [m[i] for i in PERMUTATION]
    return struct.pack("<8I", *(v[i] ^ v[i + 8] for i in range(8)))


def _mask_of(event):
    mask = bytes.fromhex(event["mask_hex"])
    return int.from_bytes(mask, "big"), len(mask)


def _stream(seed_hex, counter):
    """Deterministic message stream: SHAKE-256(seed || counter) in 32-byte pieces."""
    base = bytes.fromhex(seed_hex)
    index = counter
    while True:
        material = hashlib.shake_256(base + struct.pack("<Q", index)).digest(32 * 8)
        for offset in range(0, len(material), 32):
            yield material[offset:offset + 32]
        index += 1


def main():
    request = json.load(sys.stdin)
    event = request["event"]
    mask_int, mask_bytes = _mask_of(event)
    trials = []
    for row in request["trials"]:
        seen = {}
        evaluations = 0
        pair = None
        for message in _stream(row["seed"], row["trial"]):
            evaluations += 1
            digest = _digest32(message)
            key = int.from_bytes(digest[:mask_bytes], "big") & mask_int
            prior = seen.get(key)
            if prior is not None and prior != message:
                pair = (prior, message)
                break
            seen[key] = message
            if evaluations >= 1 << 20:
                break
        if pair is None:
            raise SystemExit("no pair")
        trials.append({
            "trial": row["trial"],
            "message_a_hex": pair[0].hex(),
            "message_b_hex": pair[1].hex(),
            "observations": {"evaluations": evaluations, "table_entries": len(seen)},
        })
    json.dump({"schema_version": 1, "trials": trials}, sys.stdout, separators=(",", ":"))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
