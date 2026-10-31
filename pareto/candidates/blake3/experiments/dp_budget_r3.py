"""Reduced-width tests of heuristic H1 for the three-round BLAKE3 collision claim.

The claim runs a distinguished-point collision search on F(x) = three-round BLAKE3
digest of the 64-byte message 0^32 || x, with a fresh-evaluation budget M chosen so
that M^2 / 2^257 = 0.5213, and claims success probability at least 0.40 under the
heuristic H1 that F has the collision and trail statistics of a random function.

This program runs the same algorithm, with the same parameter rule, on F truncated
to its first w digest bits (big-endian prefix). The experiment id selects w and the
budget. The organizer counts, per trial, whether the returned pair really collides
on the first w bits; that count divided by 256 is the quantity H1 predicts.

Experiment ids:
  dp-budget-r3-w12  w = 12, M = 66  fresh evaluations, B = M + 3 * L_max in total
  dp-budget-r3-w16  w = 16, M = 262 fresh evaluations, B = M + 3 * L_max in total
  dp-budget-r3-w18  w = 18, M = 523 fresh evaluations, B = M + 3 * L_max in total
  dp-open-r3-w16    w = 16, no budget below the hard stop of 2^20 steps
Distinguished points have their low 2 bits zero (theta = 2^-2), so L_max = 16 / theta = 64.

Stdlib only; deterministic from the per-trial seed; one JSON request on stdin, one
JSON report on stdout. Only the returned message pairs are organizer-checked; the
observations are participant counters and are not trusted by the host.
"""
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
# M = ceil(sqrt(1.0426 * 2^w)): M^2 / 2^(w+1) = 0.5317, 0.5237, 0.5217 at w = 12, 16, 18
# (0.5213 in the claim; the difference is the rounding of M up to an integer).
EXPERIMENTS = {
    "dp-budget-r3-w12": (12, 66),
    "dp-budget-r3-w16": (16, 262),
    "dp-budget-r3-w18": (18, 523),
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


def make_step(width_bits):
    shift = 32 - width_bits

    def step(x):
        """First width_bits bits of the digest of message_of(x), as the next point."""
        return int.from_bytes(digest64(message_of(x))[:4], 'big') >> shift
    return step


def is_dp(x):
    return x & ((1 << THETA_BITS) - 1) == 0


def run_trial(seed_hex, width_bits, budget):
    """The claim's algorithm (proof.md Section 3) at width width_bits.

    Budget rule, as in the claim: at most M fresh evaluations in step 3 (trail
    extension), and at most 3 * L_max further evaluations in step 5 (walking two
    trails back to the collision), so at most B = M + 3 * L_max in total.
    Returns (message_a, message_b, observations); the messages are None on failure.
    """
    step = make_step(width_bits)
    shift = 32 - width_bits
    seed = bytes.fromhex(seed_hex)
    fresh_cap = HARD_STOP if budget is None else budget
    total_cap = fresh_cap + 3 * TRAIL_CAP
    table = {}           # growable map standing in for the fixed 2^14-slot table of proof.md Section 3;
                         # the full-table failure (probability < 10^-1000 at full width) cannot occur here
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
        # Step 2: fresh start point, derived only from the organizer seed.
        start = int.from_bytes(digest64(seed + counter.to_bytes(32, 'big'))[:4], 'big') >> shift
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
        # Step 6: the organizer recomputes both digests; the program returns the messages.
        a, b = message_of(xa), message_of(xb)
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
