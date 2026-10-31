"""Reduced-width, keyed-coset tests of heuristic H1 for the three-round BLAKE3 collision claim.

The claim runs a distinguished-point collision search on F(x) = three-round BLAKE3
digest of the 64-byte message 0^32 || x, with a fresh-evaluation budget M chosen so
that M (M - 1) / 2^257 = 0.7684, and claims success probability at least 0.40 under the
heuristic H1 that the search on F succeeds at least 0.75 times as often as the same
search on a uniformly random function (whose success probability is at least 0.5349).

This program runs the same algorithm, with the same budget rule, on F restricted to
one coset of 2^w inputs and truncated to its first w digest bits (big-endian prefix).
The coset is chosen per trial from the organizer seed: a 256-bit offset R with its
low w bits cleared, and the walk state v (w bits) is embedded as x = R | v. Every
trial therefore runs on a different 2^w-point restriction of F, so the 256 trials
sample 256 instances instead of one fixed block of inputs. The organizer checks,
per trial, that the returned pair collides on the first w digest bits; that count
divided by 256 is the quantity the experiment measures.

Experiment ids:
  dp-budget-r3-w12  w = 12, M = 80  fresh evaluations, B = M + 3 * L_max in total
  dp-budget-r3-w16  w = 16, M = 318 fresh evaluations, B = M + 3 * L_max in total
  dp-budget-r3-w17  w = 17, M = 449 fresh evaluations, B = M + 3 * L_max in total
  dp-open-r3-w16    w = 16, no budget below the hard stop of 2^20 steps
Distinguished points have their low 2 bits zero (theta = 2^-2), so L_max = 16 / theta = 64.

Stdlib only; deterministic from the per-trial seed; one JSON request on stdin, one
JSON report on stdout. Only the returned message pairs are organizer-checked; the
observations are participant counters and are not trusted by the host.
"""
import hashlib
import json
import struct
import sys

IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
      0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
M32 = 0xFFFFFFFF
ROUNDS = 3
THETA_BITS = 2                     # theta = 2^-2
TRAIL_CAP = 16 << THETA_BITS       # L_max = 16 / theta = 64
HARD_STOP = 1 << 20

# width_bits, fresh-evaluation budget M (None: open run to the hard stop).
# M = ceil(sqrt(0.76844 * 2^(w+1))): M^2 / 2^(w+1) = 0.7812, 0.7715, 0.7690 at w = 12, 16, 17
# (0.76844 in the claim; the difference is the rounding of M up to an integer).
EXPERIMENTS = {
    "dp-budget-r3-w12": (12, 80),
    "dp-budget-r3-w16": (16, 318),
    "dp-budget-r3-w17": (17, 449),
    "dp-open-r3-w16": (16, None),
}


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


def coset_offset(seed, width_bits):
    """Per-trial 256-bit offset with its low width_bits bits cleared, derived from the seed by SHA-256."""
    r = int.from_bytes(hashlib.sha256(seed + b"coset").digest(), 'little')
    return r & ~((1 << width_bits) - 1)


def make_step(width_bits, offset):
    shift = 32 - width_bits

    def step(v):
        """First width_bits bits of the digest of message_of(offset | v), as the next point."""
        return int.from_bytes(digest64(message_of(offset | v))[:4], 'big') >> shift
    return step


def is_dp(x):
    return x & ((1 << THETA_BITS) - 1) == 0


def run_trial(seed_hex, width_bits, budget):
    """The claim's algorithm (proof.md Section 3) at width width_bits on one keyed coset.

    Budget rule, as in the claim: at most M fresh evaluations in step 3 (trail
    extension), and at most 3 * L_max further evaluations in step 5 (walking two
    trails back to the collision), so at most B = M + 3 * L_max in total.
    Returns (message_a, message_b, observations); the messages are None on failure.
    """
    seed = bytes.fromhex(seed_hex)
    offset = coset_offset(seed, width_bits)
    step = make_step(width_bits, offset)
    shift = 32 - width_bits
    fresh_cap = HARD_STOP if budget is None else budget
    total_cap = fresh_cap + 3 * TRAIL_CAP
    table = {}           # growable map standing in for the fixed 2^14-slot table of proof.md Section 3;
                         # the full-table failure (probability < 10^-500 at full width) cannot occur here
    fresh = 0            # step-3 evaluations
    steps = 0            # all evaluations (steps 3 and 5)
    trails = 0
    abandoned = 0
    merges = 0
    counter = 0

    def fail():
        return None, None, {"success": 0, "steps": steps, "fresh": fresh, "trails": trails,
                            "stored_points": len(table), "abandoned": abandoned, "merges": merges}

    while True:
        # Step 2: fresh start point in the coset, derived only from the organizer seed (SHA-256, not F).
        start = int.from_bytes(hashlib.sha256(seed + counter.to_bytes(32, 'big')).digest()[:4], 'big') >> shift
        counter += 1
        trails += 1
        x, length = start, 0
        # Step 3: extend until a distinguished point, the trail cap or the fresh budget.
        while True:
            if fresh >= fresh_cap:
                return fail()
            x = step(x); fresh += 1; steps += 1; length += 1
            if is_dp(x):
                break
            if length >= TRAIL_CAP:
                break
        if not is_dp(x):
            abandoned += 1
            continue
        # Step 4: distinguished point.
        if x not in table:
            table[x] = (start, length)
            continue
        s0, l0 = table[x]
        # Step 5: walk back both trails in lockstep (at most 3 * L_max evaluations).
        xa, la, xb, lb = s0, l0, start, length
        while la > lb:
            if steps >= total_cap:
                return fail()
            xa = step(xa); steps += 1; la -= 1
        while lb > la:
            if steps >= total_cap:
                return fail()
            xb = step(xb); steps += 1; lb -= 1
        if xa == xb:
            merges += 1        # the new start lay on the stored trail: same input, not a collision
            continue
        while True:
            if steps >= total_cap:
                return fail()
            na, nb = step(xa), step(xb); steps += 2
            if na == nb:
                break
            xa, xb = na, nb
        # Step 6: the organizer recomputes both digests; the program returns the full messages.
        a, b = message_of(offset | xa), message_of(offset | xb)
        if a == b or (int.from_bytes(digest64(a)[:4], 'big') >> shift) != (int.from_bytes(digest64(b)[:4], 'big') >> shift):
            return fail()      # cannot happen if the arithmetic above is right; reported as failure, never as a pair
        return a, b, {"success": 1, "steps": steps, "fresh": fresh, "trails": trails,
                      "stored_points": len(table), "abandoned": abandoned, "merges": merges}


def main():
    request = json.loads(sys.stdin.read())
    width_bits, budget = EXPERIMENTS[request["experiment_id"]]
    out = []
    for item in request["trials"]:
        a, b, obs = run_trial(item["seed"], width_bits, budget)
        out.append({"trial": item["trial"],
                    "message_a_hex": None if a is None else a.hex(),
                    "message_b_hex": None if b is None else b.hex(),
                    "observations": obs})
    sys.stdout.write(json.dumps({"schema_version": 1, "trials": out}, separators=(',', ':')))


if __name__ == "__main__":
    main()
