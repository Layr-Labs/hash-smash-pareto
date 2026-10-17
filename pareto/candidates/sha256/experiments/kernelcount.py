"""kernelcount.py: packed-kernel operation count for the 39-step claw search.

Organizer experiment for premise H3 (machine convention).  The filed time
ledger charges 70 word operations per packed 7-lane evaluation of the walk
function F.  Until now that figure was produced by a tracer run outside the
package and reported only in prose, so it could not be checked.  This
experiment rebuilds the tracer, emits the straight-line program, counts it,
and checks that the emitted program computes the same function as a scalar
reference implementation.

The walk function on 32-bit points x, one point per 36-bit lane, 7 lanes in a
256-bit word:

    F(x) = s0(x) - x                                       for odd  x
    F(x) = C + S0(x) + MAJ(x, Am1, Am2)
             + S1(E0) + CH(E0, Em1, Em2) - x,  E0 = x + e0  for even x

Both sides are evaluated for every lane and blended by the low bit of x:
m = ((x & 1) << 32) - (x & 1) is 2^32 - 1 or 0 in each lane and never borrows
across the 36-bit lane pitch.

Pricing (collision-frontier-v5 word RAM, 256-bit words, the convention of
submission 744875ec): every emitted line is one operation (+, -, &, |, ^, <<,
>>); immediates are free; a rotation costs 5 operations and a right shift 2,
which is what the Tracer below actually emits rather than asserts.

Each trial derives a chaining value from the organizer seed, derives the
cv-dependent constants, builds the program, counts the emitted lines, computes
peak live registers, and then runs the emitted program on packed random lane
vectors, comparing every lane against the scalar reference.

Scope limit: this measures the kernel proper.  The DP test, loop and handler
overhead (22.4 operations, charged as 23) are NOT traced here and remain
estimated, exactly as H3 discloses.  The constant C is derived from the trial
seed rather than from the filed dense base: the operation count and the
packed-vs-scalar equivalence do not depend on C's provenance, only on it being
a 32-bit constant.

Protocol: python-message-pairs-v1 (JSON on stdin/stdout).
"""
import json
import sys
import hashlib
import struct

M32 = 0xFFFFFFFF
LANES, PITCH = 7, 36
REP = sum(1 << (PITCH * i) for i in range(LANES))
LIM = 1 << PITCH


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


class Tracer:
    """Straight-line code over packed 256-bit words.

    A value is ('c', k) for a folded constant or ('v', name, bound) for a
    register whose per-lane value is bounded by `bound`.  `bound` is what keeps
    lane arithmetic honest: whenever an addition could carry past the 36-bit
    lane pitch the accumulator is masked back to 32 bits first, and that mask
    is itself an emitted operation.
    """

    def __init__(self):
        self.lines = []
        self.k = 0

    def emit(self, op, a, b):
        self.k += 1
        name = "t%d" % self.k
        self.lines.append((name, op, a, b))
        return name

    def mask(self, a):
        return ("v", self.emit("&", a[1], M32), M32)

    def clean(self, a):
        return a if a[0] == "c" or a[2] <= M32 else self.mask(a)

    def add(self, *xs):
        c = sum(x[1] for x in xs if x[0] == "c") & M32
        vs = [x for x in xs if x[0] == "v"]
        if not vs:
            return ("c", c)
        acc = vs[0]
        for v in vs[1:]:
            while acc[2] + v[2] >= LIM:
                if acc[2] >= v[2]:
                    acc = self.mask(acc)
                else:
                    v = self.mask(v)
            acc = ("v", self.emit("+", acc[1], v[1]), acc[2] + v[2])
        if c:
            if acc[2] + c >= LIM:
                acc = self.mask(acc)
            acc = ("v", self.emit("+", acc[1], c), acc[2] + c)
        return acc

    def xor(self, a, b):
        if a[0] == "c" and b[0] == "c":
            return ("c", a[1] ^ b[1])
        if a[0] == "c":
            a, b = b, a
        if b[0] == "c":
            if b[1] == 0:
                return a
            width = (1 << max(a[2].bit_length(), b[1].bit_length())) - 1
            return ("v", self.emit("^", a[1], b[1]), width)
        width = (1 << max(a[2].bit_length(), b[2].bit_length())) - 1
        return ("v", self.emit("^", a[1], b[1]), width)

    def and_(self, a, b):
        if a[0] == "c" and b[0] == "c":
            return ("c", a[1] & b[1])
        if a[0] == "c":
            a, b = b, a
        if b[0] == "c":
            if b[1] == 0:
                return ("c", 0)
            return ("v", self.emit("&", a[1], b[1]), min(a[2], b[1]))
        return ("v", self.emit("&", a[1], b[1]), min(a[2], b[2]))

    def ror(self, a, r):
        if a[0] == "c":
            return ("c", ror32(a[1], r))
        hi = self.emit("&", self.emit(">>", a[1], r), (1 << (32 - r)) - 1)
        lo = self.emit("&", self.emit("<<", a[1], 32 - r), ((1 << r) - 1) << (32 - r))
        return ("v", self.emit("|", hi, lo), M32)

    def shr(self, a, k):
        if a[0] == "c":
            return ("c", a[1] >> k)
        shifted = self.emit(">>", a[1], k)
        return ("v", self.emit("&", shifted, (1 << (32 - k)) - 1), (1 << (32 - k)) - 1)

    def notw(self, a):
        return ("v", self.emit("^", a[1], M32), M32)


def build(k):
    """Emit the kernel and return (tracer, output value)."""
    t = Tracer()
    x = ("v", "x", M32)
    # even side: C + S0(x) + MAJ(x, Am1, Am2) + S1(E0) + CH(E0, Em1, Em2) + ~x + 1
    e0 = t.add(x, ("c", k["e0"]))
    s0a = t.xor(t.xor(t.ror(x, 2), t.ror(x, 13)), t.ror(x, 22))
    mj = t.xor(t.and_(x, ("c", k["Am1"] ^ k["Am2"])), ("c", k["Am1"] & k["Am2"]))
    s1e = t.xor(t.xor(t.ror(e0, 6), t.ror(e0, 11)), t.ror(e0, 25))
    ch = t.xor(t.and_(e0, ("c", k["Em1"] ^ k["Em2"])), ("c", k["Em2"]))
    ev = t.clean(t.add(s0a, mj, s1e, ch, t.notw(x), ("c", (k["C"] + 1) & M32)))
    # odd side: s0(x) + ~x + 1
    s0x = t.xor(t.xor(t.ror(x, 7), t.ror(x, 18)), t.shr(x, 3))
    od = t.clean(t.add(s0x, t.notw(x), ("c", 1)))
    # blend by the low bit of x
    b = t.and_(x, ("c", 1))
    m = ("v", t.emit("-", t.emit("<<", b[1], 32), b[1]), M32)
    out = t.xor(ev, t.and_(t.xor(od, ev), m))
    return t, out


def run_program(lines, out, packed_x):
    """Interpret the emitted straight-line program on one packed word."""
    env = {"x": packed_x}
    for name, op, a, b in lines:
        va = env[a]
        if isinstance(b, str):
            vb = env[b]
        elif op in ("<<", ">>"):
            vb = b
        else:
            vb = REP * b
        if op == "+":
            env[name] = va + vb
        elif op == "-":
            env[name] = va - vb
        elif op == "&":
            env[name] = va & vb
        elif op == "|":
            env[name] = va | vb
        elif op == "^":
            env[name] = va ^ vb
        elif op == ">>":
            env[name] = va >> vb
        else:
            env[name] = (va << vb) & ((1 << 256) - 1)
    return env[out]


def peak_live(lines, out):
    last = {}
    for i, (_, _, a, b) in enumerate(lines):
        for v in (a, b):
            if isinstance(v, str):
                last[v] = i
    live, peak = {"x"}, 1
    for i, (name, _, _, _) in enumerate(lines):
        live.add(name)
        live = {v for v in live if last.get(v, -1) > i or v == name or v == out}
        peak = max(peak, len(live))
    return peak


def F_scalar(x, k):
    if x & 1:
        return (sigma0(x) - x) & M32
    e0 = (x + k["e0"]) & M32
    return (k["C"] + Sigma0(x) + Maj(x, k["Am1"], k["Am2"])
            + Sigma1(e0) + Ch(e0, k["Em1"], k["Em2"]) - x) & M32


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
        s0w = ror32(w[i - 15], 7) ^ ror32(w[i - 15], 18) ^ (w[i - 15] >> 3)
        s1w = ror32(w[i - 2], 17) ^ ror32(w[i - 2], 19) ^ (w[i - 2] >> 10)
        w.append((s1w + w[i - 7] + s0w + w[i - 16]) & M32)
    a, b, c, d, e, f, g, h = state
    for i in range(39):
        t1 = (h + Sigma1(e) + Ch(e, f, g) + SHA256_K[i] + w[i]) & M32
        t2 = (Sigma0(a) + Maj(a, b, c)) & M32
        h, g, f, e, d, c, b, a = g, f, e, (d + t1) & M32, c, b, a, (t1 + t2) & M32
    return [(s + v) & M32 for s, v in zip(state, [a, b, c, d, e, f, g, h])]


def derive_cv(seed_hex):
    raw = hashlib.shake_256(bytes.fromhex(seed_hex)).digest(64)
    return sha256_r39_compress(list(IV), struct.unpack(">16I", raw))


def main():
    request = json.load(sys.stdin)
    trials = []
    n_vectors = 48

    for t in request["trials"]:
        seed = t["seed"]
        cv = derive_cv(seed)
        # The walk function's register identifications, as in proof.md Section 6:
        # A[-1-j] = cv[j] and E[-1-j] = cv[4+j], so Am1 = cv[0], Am2 = cv[1],
        # Em1 = cv[4], Em2 = cv[5] and e0 = cv[3] - S0(cv[0]) - MAJ(cv[0], cv[1], cv[2]).
        k = {
            "e0": (cv[3] - Sigma0(cv[0]) - Maj(cv[0], cv[1], cv[2])) & M32,
            "Am1": cv[0], "Am2": cv[1], "Em1": cv[4], "Em2": cv[5],
            "C": struct.unpack(">I", hashlib.shake_256(
                bytes.fromhex(seed) + b"kernelC").digest(4))[0],
        }

        tracer, out = build(k)
        ops = len(tracer.lines)
        live = peak_live(tracer.lines, out[1])
        by_op = {}
        for _, op, _, _ in tracer.lines:
            by_op[op] = by_op.get(op, 0) + 1

        rng = hashlib.shake_256(bytes.fromhex(seed) + b"kernelvec")
        raw = rng.digest(4 * LANES * n_vectors)
        lanes_checked = 0
        mismatches = 0
        for v in range(n_vectors):
            xs = struct.unpack_from(">%dI" % LANES, raw, 4 * LANES * v)
            packed = 0
            for j, xv in enumerate(xs):
                packed |= xv << (PITCH * j)
            result = run_program(tracer.lines, out[1], packed)
            for j, xv in enumerate(xs):
                lanes_checked += 1
                got = (result >> (PITCH * j)) & (LIM - 1)
                if got != F_scalar(xv, k):
                    mismatches += 1

        trials.append({
            "trial": t["trial"],
            "message_a_hex": None,
            "message_b_hex": None,
            "observations": {
                "ops_per_word": ops,
                "lanes": LANES,
                "peak_live_registers": live,
                "lanes_checked": lanes_checked,
                "mismatches": mismatches,
                "op_add": by_op.get("+", 0),
                "op_sub": by_op.get("-", 0),
                "op_and": by_op.get("&", 0),
                "op_or": by_op.get("|", 0),
                "op_xor": by_op.get("^", 0),
                "op_shl": by_op.get("<<", 0),
                "op_shr": by_op.get(">>", 0),
            },
        })

    json.dump({"schema_version": 1, "trials": trials}, sys.stdout)


if __name__ == "__main__":
    main()
