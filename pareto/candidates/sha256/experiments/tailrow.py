"""tailrow.py: the tail estimator's row predicate, run by the organizer.

The tail (2^-79.759) is the largest term in the per-claw exponent and the one
with no organizer-executed evidence.  The estimator that produced it is C code
driving a multilevel splitting scheme over 2^36 proposals per stage; it is not a
Python program and cannot ship, and the deep stages are unreachable here because
getting to them costs more than the sandbox's whole budget.

What CAN be put in the package is the estimator's inner object -- the per-row
predicate -- together with a direct measurement of the first tail stage, row 18,
which is the one stage the filed base can reach without any search.  That is what
this experiment does.

The base b1 (proof.md Appendix B) supplies A14..A17 and E14..E17 for both
members.  Stepping to row 18 with a proposed W18 gives, for member m,

    T1_m = E_{14,m} + S1(E_{17,m}) + CH(E_{17,m}, E_{16,m}, E_{15,m}) + K18 + W18
    T2_m = S0(A_{17,m}) + MAJ(A_{17,m}, A_{16,m}, A_{15,m})
    A_{18,m} = T1_m + T2_m            E_{18,m} = A_{14,m} + T1_m

Every term except W18 is fixed by the base, so A18 and E18 are each a constant
plus W18 and the inner loop is additions -- which is what makes a meaningful
number of proposals affordable here.

Row 18 holds when the signed differences match the characteristic's ROW 18 record
(A mask 40000000 with sign 40000000, E difference zero, W difference zero,
proof.md Appendix A.2) and all 17 bit conditions keyed at step 18 evaluate true
(Appendix A.3, reproduced below in the same encoding).

Each trial draws uniform W18 values and counts those for which row 18 holds.
Pooled, this estimates the row-18 conditional probability, which the filed study
reports as about 2^-18.0.

Scope limits:
  * This measures ONE stage of the tail.  The filed 2^-79.759 is the product of
    rows 18..23 and the run to row 38; the remaining stages are not reachable
    from the base without the search this sandbox cannot run, so they remain
    reported rather than executed.
  * The precision is set by the budget: roughly 2^22 pooled proposals against a
    rate near 2^-18 gives on the order of sixteen hits, so the measurement
    resolves the stage to a few tenths of a bit, not better.
  * It uses the filed base and the filed characteristic.  It therefore checks
    that those two objects, as filed, reproduce the row-18 rate the study
    reports; it does not independently confirm the characteristic.

Protocol: python-message-pairs-v1 (JSON on stdin/stdout).
"""
import json
import sys
import hashlib
import math
import struct

M32 = 0xFFFFFFFF
K18 = 0xe49b69c1
PROPOSALS = 1 << 14

# Filed dense base b1, rows 14..17, both members (proof.md Appendix B).
AX = {14: 0xbd4f5653, 15: 0x269f8f4f, 16: 0xcc8fd4cb, 17: 0xce7b54b4}
AY = {14: 0xfd4b5673, 15: 0x36998e6f, 16: 0xc98ed4cb, 17: 0xce7b54b4}
EX = {14: 0x9cca05a1, 15: 0xd2c3ec33, 16: 0x9776869e, 17: 0x771adf7e}
EY = {14: 0x9cca05a1, 15: 0xc2c3ec33, 16: 0x9776879e, 17: 0xf798437f}

# ROW 18 of the characteristic (Appendix A.2): MA SA ME SE MW SW.
MA18, SA18 = 0x40000000, 0x40000000
ME18, SE18 = 0x00000000, 0x00000000

# The 17 bit conditions keyed at step 18 (Appendix A.3), each as
# (n, [(kind, row, bit), ...], allowed).  kind 0 = A bit, 1 = E bit, 2 = W bit.
COND18 = [
    (2, [(1, 18, 0), (1, 16, 0)], 0x5),
    (2, [(1, 18, 8), (1, 17, 8)], 0x5),
    (2, [(0, 18, 10), (0, 18, 21)], 0x9),
    (2, [(1, 18, 10), (1, 16, 10)], 0x5),
    (2, [(1, 18, 11), (1, 16, 11)], 0x5),
    (2, [(1, 18, 12), (1, 16, 12)], 0x5),
    (2, [(1, 18, 15), (1, 16, 15)], 0x5),
    (2, [(0, 18, 16), (0, 17, 16)], 0x9),
    (2, [(1, 18, 17), (1, 16, 17)], 0xa),
    (2, [(0, 18, 19), (0, 18, 7)], 0x6),
    (2, [(1, 18, 23), (1, 16, 23)], 0x5),
    (2, [(0, 18, 24), (0, 17, 24)], 0x9),
    (2, [(0, 18, 26), (0, 17, 26)], 0x9),
    (2, [(0, 18, 9), (0, 18, 18)], 0x6),
    (2, [(1, 18, 31), (1, 16, 31)], 0x5),
    (2, [(1, 18, 5), (1, 17, 5)], 0x9),
    (2, [(1, 18, 19), (1, 17, 19)], 0x9),
]


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


def constants(A, E):
    """The parts of A18 and E18 that do not move with W18."""
    t1 = (E[14] + Sigma1(E[17]) + Ch(E[17], E[16], E[15]) + K18) & M32
    t2 = (Sigma0(A[17]) + Maj(A[17], A[16], A[15])) & M32
    return (t1 + t2) & M32, (A[14] + t1) & M32      # A18 base, E18 base


def main():
    request = json.load(sys.stdin)
    trials = []

    a18x0, e18x0 = constants(AX, EX)
    a18y0, e18y0 = constants(AY, EY)

    # The conditions read A and E bits at rows 16, 17 (fixed by the base) and 18
    # (which moves with W18).  Pre-split them so the hot path only touches 18.
    fixed = {(0, 16): AX[16], (0, 17): AX[17], (1, 16): EX[16], (1, 17): EX[17]}

    for t in request["trials"]:
        seed = t["seed"]
        raw = hashlib.shake_256(bytes.fromhex(seed) + b"tailrow").digest(4 * PROPOSALS)
        unpack = struct.unpack_from

        diff_ok = 0
        row_ok = 0
        for i in range(PROPOSALS):
            w18 = unpack(">I", raw, 4 * i)[0]
            ax = (a18x0 + w18) & M32
            ay = (a18y0 + w18) & M32
            if (ax ^ ay) != MA18:
                continue
            if (ax & MA18) != SA18:
                continue
            ex = (e18x0 + w18) & M32
            ey = (e18y0 + w18) & M32
            if (ex ^ ey) != ME18:
                continue
            diff_ok += 1
            vals = dict(fixed)
            vals[(0, 18)] = ax
            vals[(1, 18)] = ex
            vals[(2, 18)] = w18
            good = True
            for n, pos, allowed in COND18:
                idx = 0
                for j, (kind, row, bit) in enumerate(pos):
                    idx |= ((vals[(kind, row)] >> bit) & 1) << j
                if not ((allowed >> idx) & 1):
                    good = False
                    break
            if good:
                row_ok += 1

        observations = {
            "proposals": PROPOSALS,
            "signed_diff_ok": diff_ok,
            "row18_ok": row_ok,
            "conditions": len(COND18),
        }
        if row_ok:
            observations["log2_p18"] = round(math.log2(row_ok / PROPOSALS), 4)
        trials.append({
            "trial": t["trial"],
            "message_a_hex": None,
            "message_b_hex": None,
            "observations": observations,
        })

    json.dump({"schema_version": 1, "trials": trials}, sys.stdout)


if __name__ == "__main__":
    main()
