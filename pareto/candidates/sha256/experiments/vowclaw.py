"""vowclaw.py: executable specification of the van Oorschot-Wiener claw search.

Organizer experiment for premise H2 (saturated claw rate).  The filed ledger
charges 2^11.41 evaluations per distinct claw, a figure measured in a 2^30
evaluation run that is not part of this package.  That run cannot be reproduced
inside the organizer's 20-second, 128 MB sandbox, and no experiment here claims
to reproduce it.

What this experiment supplies is an executable statement of the search's
structure at a reduced scale.  It runs ONE table size and measures no scaling
law.

The search, in the same shape as the attack runs it (but see the scope limit
below: this is a reduced instance, not the filed configuration):

  * Points are 32-bit words; in the reduced instance below they are NBITS-bit
    words so that a full birthday search fits the sandbox.
  * The walk function is two-sided, which is what makes a collision a *claw*:
        F(x) = f(x)          = s0(x) - x          for odd x   (the u side)
        F(x) = g - Kc(x, cv)                      for even x  (the a0 side)
    A collision F(x) = F(y) with x odd and y even is a claw; a collision with
    both points on the same side is a useless same-side collision and is
    counted separately here.
  * A point is distinguished when its low dp_bits bits are zero.  Walks start
    from seeded random points, iterate F until they reach a distinguished
    point, and store (start, steps) in a table keyed by that distinguished
    point.  A second walk arriving at an occupied key yields a collision, which
    is resolved by re-walking the shorter chain to the meeting point.
  * The first WARMUP evaluations are a warm-up: they fill the table but their
    claws are not attributed to any window, so the windows measure the
    saturated steady state the attack runs in rather than the fill transient.
  * The table holds `slots` entries.  When it is full a new chain replaces the
    entry it collides with, which is the saturated regime the filed rate
    describes.

What H2 actually asserts is rate *stability*: the saturated rate measured over
a 2^30-evaluation run is applied unchanged to the 2^119.70 claws the attack
needs.  The risk it carries is drift -- the claw rate falling off as a run
lengthens because the walk depletes the available collisions, enters cycles, or
revisits covered ground.  That is what this experiment measures: with the table
held at a saturated size, the run is divided into four equal windows and the
claw count of each window is reported separately.  A stable rate across windows
is consistent with H2 at this scale; a falling rate would contradict it.

Scope limit.  This runs on a reduced domain (2^NBITS points), not on 2^32, and
for a number of evaluations many orders of magnitude below the attack's.  Rate
stability over four windows of a 2^13-evaluation run is evidence about this
instance only; it does NOT establish the 2^11.41 figure, nor stability out to
2^119.70 claws, where depletion and cycle structure could behave differently.
Those remain premise H2.

Protocol: python-message-pairs-v1 (JSON on stdin/stdout).
"""
import json
import sys
import hashlib
import math
import struct

M32 = 0xFFFFFFFF
NBITS = 20
NMASK = (1 << NBITS) - 1
DP_BITS = 4
WARMUP = 1 << 12     # fill the table well before counting (2x its capacity in DPs)
EVALS = 1 << 13      # counted evaluations, split into WINDOWS equal windows
WINDOWS = 4
SLOTS = 128          # small enough that the table saturates during the warm-up


def ror32(x, r):
    return ((x >> r) | (x << (32 - r))) & M32


def sigma0(x):
    return ror32(x, 7) ^ ror32(x, 18) ^ (x >> 3)


def make_even_side(seed_hex):
    """A seeded stand-in for g - Kc(x, cv) on the reduced domain.

    At full scale this branch is the SHA-256 round expression of proof.md
    Section 6.  Its only property the search relies on is that it behaves as a
    random function of x, so on the reduced domain it is realized by a keyed
    hash, which keeps the experiment self-contained and the domain small.
    """
    key = hashlib.shake_256(bytes.fromhex(seed_hex) + b"evenside").digest(16)

    def even(x):
        h = hashlib.shake_256(key + struct.pack("<I", x)).digest(4)
        return struct.unpack("<I", h)[0] & NMASK

    return even


def walk_step(x, even):
    if x & 1:
        return (sigma0(x) - x) & NMASK
    return even(x)


def run_search(seed_hex, slots, evals, even):
    """Run the DP walk; return per-window claw counts and totals."""
    table = {}
    rng = hashlib.shake_256(bytes.fromhex(seed_hex) + b"starts")
    raw = rng.digest(4 * 256)
    starts = [struct.unpack_from("<I", raw, 4 * (i % 256))[0] & NMASK
              for i in range(256)]

    claws = 0
    same_side = 0
    collisions = 0
    unresolved = 0
    used = 0
    chain = 0
    dp_mask = (1 << DP_BITS) - 1
    window_claws = [0] * WINDOWS
    span = max(1, (evals - WARMUP) // WINDOWS)

    while used < evals:
        start = (starts[chain % 256] + chain * 0x9E3779B1) & NMASK
        chain += 1
        x = start
        steps = 0
        while used < evals:
            x = walk_step(x, even)
            used += 1
            steps += 1
            if (x & dp_mask) == 0 or steps > 20 * (1 << DP_BITS):
                break
        if (x & dp_mask) != 0:
            continue
        # index by the bits above the distinguished-point zeros, which are
        # constant by construction and carry no information
        slot = (x >> DP_BITS) % slots
        prev = table.get(slot)
        if prev is None or prev[2] != x:
            table[slot] = (start, steps, x)   # a slot holding a different point is overwritten
            continue
        collisions += 1
        # Resolve: walk both chains to the meeting point and classify the
        # two points that collide.
        pstart, psteps, _ = prev
        a, asteps = start, steps
        b, bsteps = pstart, psteps
        if asteps > bsteps:
            a, b = b, a
            asteps, bsteps = bsteps, asteps
        for _ in range(bsteps - asteps):
            b = walk_step(b, even)
            used += 1
        if a == b:
            continue  # same chain, no usable collision
        found = False
        for _ in range(asteps):
            na = walk_step(a, even)
            nb = walk_step(b, even)
            used += 2          # two applications, counted as two (cf. clawvow.c locev += 2)
            if na == nb:
                if (a & 1) != (b & 1):
                    claws += 1
                    if used >= WARMUP:
                        window_claws[min(WINDOWS - 1,
                                         (used - WARMUP) // span)] += 1
                else:
                    same_side += 1
                found = True
                break
            a, b = na, nb
        if not found:
            unresolved += 1
        table[slot] = (start, steps, x)

    return claws, same_side, collisions, used, window_claws, unresolved


def main():
    request = json.load(sys.stdin)
    trials = []

    for t in request["trials"]:
        seed = t["seed"]
        even = make_even_side(seed)
        claws, same_side, collisions, used, window_claws, unresolved = run_search(
            seed, SLOTS, WARMUP + EVALS, even)

        observations = {
            "domain_log2": NBITS,
            "dp_bits": DP_BITS,
            "slots": SLOTS,
            "evaluations": used,
            "warmup_evaluations": WARMUP,
            "claws": claws,
            "same_side_collisions": same_side,
            "dp_collisions": collisions,
            "unresolved_collisions": unresolved,
        }
        for w in range(WINDOWS):
            observations["claws_window%d" % (w + 1)] = window_claws[w]
        if claws > 0:
            observations["log2_evals_per_claw"] = round(math.log2(used / claws), 4)

        trials.append({
            "trial": t["trial"],
            "message_a_hex": None,
            "message_b_hex": None,
            "observations": observations,
        })

    json.dump({"schema_version": 1, "trials": trials}, sys.stdout)


if __name__ == "__main__":
    main()
