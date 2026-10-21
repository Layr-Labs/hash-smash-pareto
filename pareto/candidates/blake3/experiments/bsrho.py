"""Credited 256-lane distinguished-point birthday search for complete BLAKE3-r7.

Messages are 0^32 || x. The walk is g(x)=digest(x) XOR the generated output-
polarity mask. This derivative keeps f88f3751 and b9f7a2bc's search, recovery,
and experiments, and adds exact mask-0x10 carry columns. See proof.md for the
complete target, accounting, probability premise, and lineage.
"""
import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, log, exp, expm1, log1p

M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
ROUNDS = 7                         # rounds of the target (blake3-r7-prefix-v1)
UNIT = 1470                         # organizer reference operation cost C of blake3-r7 (222, 430, 638, 846, 1054, 1262, 1470 for 1..7 rounds)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
GCALLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
          (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
LANES, ALL = 256, (1 << 256) - 1
FLAGS = 11


# -------- 1 scalar digest
def _ror(v, k):
    return ((v >> k) | (v << (32 - k))) & M32


def digest_words(m, rounds=ROUNDS, flags=FLAGS, blen=64, counter=0):
    """Compression of the single block m (16 words) with chaining value IV, counter 0, length 64, flags 11 (CHUNK_START|CHUNK_END|ROOT):
    8 digest words v[i] XOR v[i+8], `rounds` rounds (7 for the target)."""
    v = list(IV) + list(IV[:4]) + [counter & M32, counter >> 32, blen, flags]
    m = list(m)
    for _ in range(rounds):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2 * j], m[2 * j + 1]
            v[a] = (v[a] + v[b] + x) & M32
            v[d] = _ror(v[d] ^ v[a], 16)
            v[c] = (v[c] + v[d]) & M32
            v[b] = _ror(v[b] ^ v[c], 12)
            v[a] = (v[a] + v[b] + y) & M32
            v[d] = _ror(v[d] ^ v[a], 8)
            v[c] = (v[c] + v[d]) & M32
            v[b] = _ror(v[b] ^ v[c], 7)
        m = [m[i] for i in PERM]
    return [v[i] ^ v[i + 8] for i in range(8)]


def f_scalar(x, n, key=0):
    """f(x): the low n bits of the digest of the message key(32 bytes) || x.  key = 0 is the target."""
    kw = [(key >> (32 * i)) & M32 for i in range(8)]
    d = digest_words(kw + [(x >> (32 * i)) & M32 for i in range(8)])
    return sum(d[i] << (32 * i) for i in range(8)) & ((1 << n) - 1)


def message(x):
    return bytes(32) + x.to_bytes(32, "little")


# -------- 2 packed tracer (recovery circuit)
PITCH, PLANES7 = 36, 7
REP = sum(1 << (PITCH * i) for i in range(PLANES7))
LIM = 1 << PITCH


class Tracer:
    """Straight-line code over 256-bit words holding 7 lanes of 36 bits (32 data bits and 4 guard bits).  A value is ('c', k),
    the same constant in every lane (folded at build time, no operation), or ('v', register, bound).  Every emitted line is one
    machine operation (add, and, or, xor, shl, shr; constants are immediates)."""

    def __init__(self):
        self.lines, self.ops, self.k = [], 0, 0

    def emit(self, expr):
        self.k += 1
        name = "t%d" % self.k
        self.lines.append("%s=%s" % (name, expr))
        self.ops += 1
        return name

    def mask(self, a):
        return ("v", self.emit("%s&%d" % (a[1], REP * M32)), M32)

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
            acc = ("v", self.emit("%s+%s" % (acc[1], v[1])), acc[2] + v[2])
        if c:
            if acc[2] + c >= LIM:
                acc = self.mask(acc)
            acc = ("v", self.emit("%s+%d" % (acc[1], REP * c)), acc[2] + c)
        return acc

    def xor(self, a, b):
        if a[0] == "c" and b[0] == "c":
            return ("c", a[1] ^ b[1])
        if a[0] == "c":
            a, b = b, a
        if b[0] == "c":
            if b[1] == 0:
                return a
            return ("v", self.emit("%s^%d" % (a[1], REP * b[1])), (1 << max(a[2].bit_length(), b[1].bit_length())) - 1)
        return ("v", self.emit("%s^%s" % (a[1], b[1])), (1 << max(a[2].bit_length(), b[2].bit_length())) - 1)

    def ror(self, a, r):
        if a[0] == "c":
            return ("c", _ror(a[1], r))
        s1 = self.emit("%s>>%d" % (a[1], r))
        h = self.emit("%s&%d" % (s1, REP * ((1 << (32 - r)) - 1)))
        s2 = self.emit("%s<<%d" % (a[1], 32 - r))
        lw = self.emit("%s&%d" % (s2, REP * (((1 << r) - 1) << (32 - r))))
        return ("v", self.emit("%s|%s" % (h, lw)), M32)


def build_packed(qw):
    """The recovery circuit for the walk g = f XOR q: the plain 7-round compression of the block 0^32 || x followed by one XOR of each of the 8
    output words with the 32-bit word of q (a word that is 0 costs no operation).  qw = the 8 words of q."""
    tr = Tracer()
    v = [("c", w) for w in IV] + [("c", w) for w in IV[:4]] + [("c", 0), ("c", 0), ("c", 64), ("c", FLAGS)]
    m = [("c", 0)] * 8 + [("v", "i%d" % i, M32) for i in range(8, 16)]
    for _ in range(ROUNDS):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2 * j], m[2 * j + 1]
            v[a] = tr.add(v[a], v[b], x)
            v[d] = tr.ror(tr.xor(v[d], v[a]), 16)
            v[c] = tr.add(v[c], v[d])
            v[b] = tr.ror(tr.xor(v[b], v[c]), 12)
            v[a] = tr.add(v[a], v[b], y)
            v[d] = tr.ror(tr.xor(v[d], v[a]), 8)
            v[c] = tr.add(v[c], v[d])
            v[b] = tr.ror(tr.xor(v[b], v[c]), 7)
        m = [m[i] for i in PERM]
    out = []
    for i in range(8):
        z = tr.xor(tr.xor(v[i], v[i + 8]), ("c", qw[i]))
        if z[2] > M32:
            z = tr.mask(z)
        out.append(z[1])
    nl = chr(10)
    src = "def batch(%s):" % ",".join("i%d" % i for i in range(8, 16)) + nl
    src += "".join("    %s" % ln + nl for ln in tr.lines) + "    return (%s,)" % ",".join(out) + nl
    ns = {}
    exec(src, {}, ns)
    imm = set()
    for ln in tr.lines:
        e = ln.split("=", 1)[1]
        for opch in "&^+|":
            if opch in e and e.split(opch)[1].isdigit():
                imm.add((opch, int(e.split(opch)[1])))
    return ns["batch"], tr.ops, len(imm), tuple(tr.lines), tuple(out)


_PACKED = {}


def packed_circuit(qw):
    qw = tuple(qw)
    if qw not in _PACKED:
        _PACKED[qw] = build_packed(qw)
    return _PACKED[qw]


def packed_f(xs, n, qw):
    """g on up to 7 values at once with the packed recovery circuit (g = f XOR q, low n bits; qw = the 8 words of q)."""
    words = [sum(((x >> (32 * i)) & M32) << (PITCH * l) for l, x in enumerate(xs)) for i in range(8)]
    out = packed_circuit(qw)[0](*words)
    mask = (1 << n) - 1
    return [sum(((out[i] >> (PITCH * l)) & M32) << (32 * i) for i in range(8)) & mask for l in range(len(xs))]


# -------- 3 bit-sliced generator
ZERO, ONE = (0, 0), (0, 1)


class Gen:
    """Hash-consed gate network over signals (node, neg): the stored plane is the true plane xor all-ones when neg = 1.
    Node kinds: ('v', j) input plane j, (op, a, b) with op x (xor), a (and), o (or).  calls counts generator primitives."""

    def __init__(self, n):
        self.n, self.nodes, self.memo, self.calls, self.hits, self.mkc = n, [("c",)], {}, 0, 0, 0
        self.inputs = []
        for j in range(n):
            self.nodes.append(("v", j))
            self.inputs.append((len(self.nodes) - 1, 0))

    def mk(self, op, a, b):
        self.calls += 1
        self.mkc += 1
        if a > b:
            a, b = b, a
        k = (op, a, b)
        if k in self.memo:
            self.hits += 1                                   # a shared gate (none at the 7-round target: see selftest)
        else:
            self.nodes.append(k)
            self.memo[k] = len(self.nodes) - 1
        return self.memo[k]

    def XOR(self, x, y):
        self.calls += 1
        if x[0] == 0:
            return (y[0], y[1] ^ x[1])
        if y[0] == 0:
            return (x[0], x[1] ^ y[1])
        if x[0] == y[0]:
            return (0, x[1] ^ y[1])
        return (self.mk("x", x[0], y[0]), x[1] ^ y[1])

    def AND(self, x, y):
        self.calls += 1
        if x[0] == 0:
            return ZERO if x[1] == 0 else y
        if y[0] == 0:
            return ZERO if y[1] == 0 else x
        if x[0] == y[0]:
            return x if x[1] == y[1] else ZERO
        if x[1] == 0 and y[1] == 0:
            return (self.mk("a", x[0], y[0]), 0)
        if x[1] == 1 and y[1] == 1:
            return (self.mk("o", x[0], y[0]), 1)           # !a & !b = !(a | b)
        p, q = (x, y) if x[1] == 0 else (y, x)               # p positive, q negative: p & !qn = p ^ (p & qn)
        return self.XOR(p, (self.mk("a", p[0], q[0]), 0))

    def fa(self, a, b, c):
        """(sum, carry) of three planes a + b + c by the pivot rule (the method of 6ae36351 proof 3.3, implemented here from its text)."""
        ops = (a, b, c)
        cs = [t for t in ops if t[0] == 0]
        vs = [t for t in ops if t[0] != 0]
        k = 0
        for t in cs:
            k ^= t[1]
        if len(vs) == 3:
            for pi in range(3):
                o = [vs[j] for j in range(3) if j != pi]
                if o[0][1] == o[1][1]:
                    p, x, y = vs[pi], o[0], o[1]
                    break
            u = self.XOR(x, p)
            return self.XOR(u, y), self.XOR(self.AND(u, self.XOR(y, p)), p)
        if len(vs) == 2:
            x, y = vs
            t = self.XOR(x, y)
            s = (t[0], t[1] ^ k)
            if x[1] == y[1]:
                if k == 0:
                    return s, self.AND(x, y)
                cr = self.AND((x[0], x[1] ^ 1), (y[0], y[1] ^ 1))
                return s, (cr[0], cr[1] ^ 1)
            nt = (t[0], t[1] ^ 1)
            xx = x if x[1] == nt[1] else y
            if k == 0:
                return s, self.AND(xx, nt)
            cr = self.AND((xx[0], xx[1] ^ 1), (t[0], t[1] ^ 1))
            return s, (cr[0], cr[1] ^ 1)
        if len(vs) == 1:
            x = vs[0]
            k1, k2 = cs[0][1], cs[1][1]
            return (x[0], x[1] ^ k), (ONE if k1 == k2 == 1 else ZERO if k1 == k2 == 0 else x)
        kk = cs[0][1] + cs[1][1] + cs[2][1]
        return (ZERO if kk % 2 == 0 else ONE), (ONE if kk >= 2 else ZERO)

    def add(self, A, B):
        """Ripple add of two 32-plane words, carry out of bit 31 dropped (full adders by `fa`)."""
        s, c = [], ZERO
        for i in range(32):
            if i == 31:
                s.append(self.XOR(self.XOR(A[i], B[i]), c))
            else:
                si, c = self.fa(A[i], B[i], c)
                s.append(si)
        return s


    def col3(self, t, x, y, z, u, U, cy, cu):
        """Column of x+y+z+carry; carry pair (u, U) = U ? 1 : 2u; 9 gates (proof 3.2), cy/cu: build U'/u'.  -> (s, u', U')"""
        X, A, n = self.XOR, self.AND, lambda a: (a[0], a[1] ^ 1)
        if t == 0:
            n5 = X(z, U); n9 = X(x, n5); s = X(y, n9)
            if not cy:
                return s, None, None
            n6 = X(x, y); n8 = n(A(n(U), n(X(z, u)))); n11 = A(n(n6), n9)
            return s, (X(n5, n11) if cu else None), X(n8, n11)
        w = X(y, U); n8 = X(z, w); s = X(x, n8)
        if not cy:
            return s, None, None
        n6 = n(A(n(U), n(X(y, u)))); n10 = X(x, w); Uo = X(n6, A(n8, n10))
        return s, (X(n6, w) if cu else None), Uo

    def col3_m10(self, x, y, z, u, U):
        """SAT-synthesized 9-gate column for stored polarities 00001 (mask 0x10)."""
        X, A, n = self.XOR, self.AND, lambda a: (a[0], a[1] ^ 1)
        O = lambda a, b: n(A(n(a), n(b)))
        x, y, z, u, U = ((a[0], 0) for a in (x, y, z, u, U))
        g5 = X(x, z); g6 = X(y, U); g7 = X(u, g6); g8 = A(U, g7)
        g9 = X(g5, g6); g10 = X(x, g6); g11 = X(g6, g8)
        g12 = O(g5, g10); g13 = X(g8, g12)
        return n(g9), g11, g13

    def col3_m10_no_u(self, x, y, z, u, U):
        """SAT-synthesized 8-gate penultimate column; u' is not consumed."""
        X, A, n = self.XOR, self.AND, lambda a: (a[0], a[1] ^ 1)
        O = lambda a, b: n(A(n(a), n(b)))
        x, y, z, u, U = ((a[0], 0) for a in (x, y, z, u, U))
        g5 = X(y, U); g6 = X(u, g5); g7 = A(U, g6); g8 = X(x, g5)
        g9 = X(x, z); g10 = X(z, g8); g11 = O(g8, g9); g12 = X(g7, g11)
        return n(g10), ZERO, g12

    def add3(self, X, Y, Z):
        """X+Y+Z mod 2^32: bit 0 pivot adder (carry pair (0, k)); bits 1-31 one column each, order and template by a dry trial
        (fewest mk calls, first of the 12 in order; trial nodes are removed, its calls stay counted)."""
        import itertools
        s0, U = self.fa(X[0], Y[0], Z[0])
        s, u = [s0], ZERO
        for i in range(1, 32):
            best = None
            for p in itertools.permutations((X[i], Y[i], Z[i])):
                for t in (0, 1):
                    n0, h0, k0 = len(self.nodes), self.hits, self.mkc
                    self.col3(t, *p, u, U, i < 31, i < 30)
                    for k in self.nodes[n0:]:
                        del self.memo[k]
                    del self.nodes[n0:]
                    self.hits = h0
                    if best is None or self.mkc - k0 < best[0]:
                        best = (self.mkc - k0, t, p)
            px, py, pz = best[2]
            mask = px[1] | (py[1] << 1) | (pz[1] << 2) | ((u[1] if u is not None else 0) << 3) | (U[1] << 4)
            if i < 30 and mask == 0x10:
                si, u, U = self.col3_m10(px, py, pz, u, U)
            elif i == 30 and mask == 0x10:
                si, u, U = self.col3_m10_no_u(px, py, pz, u, U)
            else:
                si, u, U = self.col3(best[1], px, py, pz, u, U, i < 31, i < 30)
            s.append(si)
        return s

    def xorw(self, A, B):
        return [self.XOR(a, b) for a, b in zip(A, B)]


def _var3(*W):
    return all(any(t[0] != 0 for t in w) for w in W)


def _ror_planes(A, r):
    return [A[(i + r) % 32] for i in range(32)]


def _constw(v):
    return [ONE if (v >> i) & 1 else ZERO for i in range(32)]


def trace(n):
    """The network of the 7-round digest of the block 0^32 || x (chaining value IV, flags 11), x = low n bits of the input planes (planes >= n are 0).
    Input planes are upright; output plane j is the signal (node, neg): the plane the circuit stores is the node, so the stored value is the digest
    plane XOR neg."""
    g = Gen(n)
    zero = _constw(0)
    m = [zero] * 8 + [[g.inputs[32 * i + b] if 32 * i + b < n else ZERO for b in range(32)] for i in range(8)]
    v = [_constw(w) for w in IV] + [_constw(w) for w in IV[:4]] + [zero, zero, _constw(64), _constw(FLAGS)]
    for _ in range(ROUNDS):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2 * j], m[2 * j + 1]
            v[a] = g.add3(v[a], v[b], x) if _var3(v[a], v[b], x) else g.add(g.add(v[a], v[b]), x)
            v[d] = _ror_planes(g.xorw(v[d], v[a]), 16)
            v[c] = g.add(v[c], v[d])
            v[b] = _ror_planes(g.xorw(v[b], v[c]), 12)
            v[a] = g.add3(v[a], v[b], y) if _var3(v[a], v[b], y) else g.add(g.add(v[a], v[b]), y)
            v[d] = _ror_planes(g.xorw(v[d], v[a]), 8)
            v[c] = g.add(v[c], v[d])
            v[b] = _ror_planes(g.xorw(v[b], v[c]), 7)
        m = [m[i] for i in PERM]
    return g, [s for i in range(8) for s in g.xorw(v[i], v[i + 8])]      # output plane 32 i + b


class Step:
    """The straight-line chain step for width n."""

    def __init__(self, n=256):
        g, out = trace(n)
        self.n, self.pin, self.gen_calls, self.hits = n, [0] * n, g.calls, g.hits
        assert all(out[j][0] != 0 for j in range(n))
        self.q = [out[j][1] for j in range(n)]
        self.qint = sum(b << j for j, b in enumerate(self.q))
        self.qwords = [(self.qint >> (32 * i)) & M32 for i in range(8)]
        seen = set(out[j][0] for j in range(n))
        for k in range(len(g.nodes) - 1, 0, -1):
            if k in seen and g.nodes[k][0] in "xao":
                seen.add(g.nodes[k][1])
                seen.add(g.nodes[k][2])
        order = [k for k in range(1, len(g.nodes)) if k in seen and g.nodes[k][0] in "xao"]
        names, lines, self.lines, self.by, self.opsym = {0: "0"}, [], [], {}, {}
        for j, (nid, _) in enumerate(g.inputs):
            names[nid] = "i%d" % j
        sym = {"x": "^", "a": "&", "o": "|"}
        for k in order:
            op, a, b = g.nodes[k]
            names[k] = "t%d" % k
            lines.append("%s=%s%s%s" % (names[k], names[a], sym[op], names[b]))
            self.lines.append((names[k], names[a], names[b]))
            self.opsym[names[k]] = (sym[op], False)
            self.by[op] = self.by.get(op, 0) + 1
        self.gates = len(order)
        self.dead = len(g.nodes) - 1 - n - len(order)           # gates built that no output uses
        outs = [names[out[j][0]] for j in range(n)]
        self.ops, self.outs = self.gates, outs
        nl, K, live, lu = chr(10), 2000, ["i%d" % j for j in range(n)], {}
        for k, (_, a, b) in enumerate(self.lines):
            lu[a] = lu[b] = k
        for o in outs:
            lu[o] = len(lines)
        self.fns = []                                         # compiled in chunks of K lines (a single 46,000-line function needs 100 MB to compile)
        for s0 in range(0, len(lines), K):
            e0 = min(s0 + K, len(lines))
            nxt = [v for v in live + [d for d, _, _ in self.lines[s0:e0]] if lu.get(v, -1) >= e0]
            src = "def c(%s):" % ",".join(live) + nl + "".join("    %s" % ln + nl for ln in lines[s0:e0]) + "    return (%s,)" % ",".join(outs if e0 == len(lines) else nxt) + nl
            ns = {}
            exec(compile(src, "<bitslice-step-n%d>" % n, "exec"), {}, ns)
            self.fns.append(ns["c"])
            live = nxt
        self.step = self._chain

    def _chain(self, *x):
        for f in self.fns:
            x = f(*x)
        return x

    def _last(self):
        last = {}
        for k, (_, a, b) in enumerate(self.lines):
            for v in (a, b):
                last[v] = k
        return last

    def peak_live(self):
        """Largest number of live plane registers after one operation (inputs live at the start, a result may reuse the register
        of a dying operand, outputs live to the end)."""
        last, outs = self._last(), set(self.outs)
        live = {"i%d" % j for j in range(self.n)}
        peak = len(live)
        for k, (nm, a, b) in enumerate(self.lines):
            live.add(nm)
            live = {v for v in live if last.get(v, -1) > k or v == nm or v in outs}
            peak = max(peak, len(live))
        return peak

    def spill_ops(self, R):
        """Loads plus stores one step needs with R plane registers (Belady farthest-next-use; inputs beyond R start in memory)."""
        from bisect import bisect_left
        INF = 10 ** 10
        uses = {}
        for k, (_, a, b) in enumerate(self.lines):
            for v in (a, b):
                if v not in ("0", "#"):
                    uses.setdefault(v, []).append(k)
        outs = set(self.outs)

        def nxt(v, k):
            u = uses.get(v)
            if u:
                i = bisect_left(u, k)
                if i < len(u):
                    return u[i]
            return 10 ** 9 if v in outs else INF

        reg, mem, cost = {"i%d" % j for j in range(self.n)}, set(), 0
        if len(reg) > R:
            for v in sorted(reg, key=lambda y: -nxt(y, 0))[:len(reg) - R]:
                reg.discard(v)
                mem.add(v)
        for k, (nm, a, b) in enumerate(self.lines):
            need = [v for v in {a, b} if v not in ("0", "#")]
            for v in need:
                if v not in reg:
                    cost += 1
                    while len(reg) >= R:
                        w = max((y for y in reg if y not in need), key=lambda y: nxt(y, k))
                        reg.discard(w)
                        if w not in mem and nxt(w, k) < INF:
                            cost += 1
                            mem.add(w)
                    reg.add(v)
            for v in need:
                if nxt(v, k + 1) >= INF:
                    reg.discard(v)
            while len(reg) >= R:
                w = max(reg, key=lambda y: nxt(y, k + 1))
                reg.discard(w)
                if w not in mem and nxt(w, k + 1) < INF:
                    cost += 1
                    mem.add(w)
            reg.add(nm)
        return cost


# -------- 4 register allocation
def allocate(st):
    """Register assignment of the straight line: input plane j and output plane j both live in register j (the chain feed is renaming, no moves); temporaries take the lowest free register above n."""
    import heapq
    n, last, free, nxt = st.n, st._last(), [], st.n
    reg = {"i%d" % j: j for j in range(n)}
    outpin = {nm: j for j, nm in enumerate(st.outs)}
    code, top = [], n
    for k, (nm, a, b) in enumerate(st.lines):
        ra, rb = reg.get(a, -1), reg.get(b, -1)
        for v in {a, b}:
            if v in reg and last.get(v, -1) == k and v not in outpin:
                if reg[v] >= n:
                    heapq.heappush(free, reg[v])
        if nm in outpin:
            j = outpin[nm]
            if last.get("i%d" % j, -1) > k:
                raise ValueError("input %d still live when output %d is produced" % (j, j))
            reg[nm] = j
        elif free:
            reg[nm] = heapq.heappop(free)
        else:
            reg[nm] = nxt
            nxt += 1
        top = max(top, reg[nm] + 1)
        code.append((nm, reg[nm], ra, rb))
    return code, top


def run_allocated(st, code, planes):
    """Execute the allocated code on a register file; returns the first n registers (the next input planes)."""
    regs = [0] * (max(c[1] for c in code) + 1)
    regs[:st.n] = planes
    for (nm, d, ra, rb) in code:
        va = regs[ra] if ra >= 0 else 0
        vb = ALL if st.opsym[nm][1] else (regs[rb] if rb >= 0 else 0)
        o = st.opsym[nm][0]
        regs[d] = va ^ vb if o == "^" else (va & vb if o == "&" else va | vb)
    return regs[:st.n]


# -------- lane transposition, packing, extraction
def _tmasks():
    res, s = {}, 128
    while s:
        m = 0
        for c in range(256):
            if not c & s:
                m |= 1 << c
        res[s] = m
        s >>= 1
    return res


_TM = _tmasks()


def transpose(rows):
    """Transpose a 256 x 256 bit matrix given as 256 integers of 256 bits (bit c of rows[i] = element (i, c))."""
    R = list(rows) + [0] * (256 - len(rows))
    s = 128
    while s:
        m = _TM[s]
        for i in range(256):
            if not i & s:
                t = ((R[i] >> s) ^ R[i + s]) & m
                R[i + s] ^= t
                R[i] ^= t << s
        s >>= 1
    return R


def pack_lanes(xs, n, pin):
    """Stored input planes (low n) for up to 256 lane values."""
    T = transpose(xs)
    return [T[j] ^ (ALL if pin[j] else 0) for j in range(n)]


def lanes_of(planes, n, pin):
    """All 256 lane values (n bits) from n stored planes."""
    T = transpose([planes[j] ^ (ALL if pin[j] else 0) for j in range(n)])
    return T[:256]


def lane_value(planes, l, pin, n):
    x = 0
    for j in range(n):
        x |= (((planes[j] >> l) & 1) ^ pin[j]) << j
    return x


def set_lane(planes, l, x, pin, n):
    bit = 1 << l
    return [(planes[j] & ~bit) | ((((x >> j) & 1) ^ pin[j]) << l) for j in range(n)]


# -------- 5 plan and ledger
LAMBDA = Fraction(497, 1000)       # 1 - exp(-LAMBDA) = 0.39165
CUTLOSS = Fraction(15, 100000)     # allowance for cut-trail points, as a fraction of Q
P_MIN = 0.390000001                # plan target; Appendix A proves P_F >= 0.39 exactly
GRAIN = 10 ** 24                   # B is a multiple of GRAIN
CMAX = 1                           # halt when more than CMAX trails are cut (more is charged as failure)
STAGE1_PLANES = 32
# machine charges (proof 3.3)
LOOP_OPS = 3                       # batch counter increment, compare with the slice limit, branch
HIT_OPS = 2800                     # a stage-1 hit lane (proof 3.3)
EVENT_OPS = 3800                   # a finished trail (proof 3.3)
CUT_OPS = 4200                     # a cut trail (proof 3.3)
SLICE_OPS = 1300                   # slice check: 256 ages
RECOVER_EXTRA = 64                 # per recovery batch beyond the packed circuit (proof 3.3)
RECOVER_PASSES = 2                 # pass 1 uses at most capr calls; pass 2 can use capr + 1 calls
INSTR_BYTES = 36                   # other instructions (handlers, setup, recovery besides its circuit, loop control, generator image): opcode, registers and an inline 256-bit immediate
GATE_BYTES = 5                     # register-format instruction, 40 bits = 8-bit opcode + three 10-bit fields: ^ & | + of two registers, NOT, or shift by a count in the third field (proof 3.1)
S1_BRANCH = 2                      # compare and branch of the stage-1 test: 36 bytes each, not register-format
GEN_CODE = 2200                    # conservative generator-image bound; native -Os emits 1,159 instructions, and 2,200 covers the parent wasm count plus the specializations
HANDLER_CODE, SETUP_CODE, RECOVERY_CODE = 1000, 160, 59   # emitted instructions besides the main body: handlers; setup/cut/slice; 13 shared + 20 pass-1 + 26 pass-2 recovery
REGISTERS = 800                    # declared register file of 256-bit words, counted as memory (the generated line needs 773)
REGFILE = REGISTERS * 32
COUNTERS = 16384                   # trail numbers, ages, counters (8 KiB) and the plane copy of the handlers (8 KiB)
KEYBITS, TBITS = 47, 17           # entry fields: 47-bit key, 17-bit trail number (64 bits = 8 bytes, one 64-bit slot); trail numbers stay below LANES + tmax + CMAX + 1 < 2^17
ENTRY = 8                          # table entry: one 64-bit slot, key in the low 47 bits, trail number in the top 17; no length is stored, the recovery recomputes both lengths (two passes)
MEM_LIMIT = 1048576                   # bytes: 2^20
SPARE = 64                         # bytes left unused under the limit
ADVICE = 0                         # bytes of nonuniform advice: none (the mask q is derived by the generator at setup)
TAIL_LOG2 = -40
KAPPA_256 = 16
GEN_FACTOR = 200                   # word operations charged per generator primitive call and per emitted line
GEN_STATE = 2528                   # generator state words (v 2,048, tmp, mw and s3 128 each, free-register bitmap 96)
GEN_STACK = 2048                   # shadow stack of the generator
GEN_INFO = 68                      # result record of the generator
GEN_GLOBALS = 128                  # 11 scalar globals and IV/PERM/GC tables are 124 bytes; charge 128 outside the image
SETUP_FIXED = 256 * 3100 + 20000   # 256 starts inserted in memory, reloaded, random word, counters
# reduced widths: s1, W, Tp, kappa
CFG = {18: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4), 20: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4),
       256: dict(s1=32, W=90, kappa=KAPPA_256, Sb=1 << 48)}


# The search image is emitted as canonical abstract machine instructions with
# physical registers. `--program` prints the complete listing and `--ledger`
# prints its SHA-256. Five-byte records are the declared register format; every
# other record is charged at 36 bytes.
def _ins(section, op, d="-", a="-", b="-", size=INSTR_BYTES):
    return section, op, str(d), str(a), str(b), size


def _parse_expr(line):
    name, expr = line.split("=", 1)
    for op in ("<<", ">>", "&", "^", "+", "|"):
        if op in expr:
            a, b = expr.split(op, 1)
            return name, op, a, int(b) if b.isdigit() else b
    raise ValueError("bad packed instruction: " + line)


def _packed_program(qw):
    """Register-allocate the 1,540-line packed recovery circuit and its constants."""
    import heapq
    pc = packed_circuit(qw)
    parsed = [_parse_expr(x) for x in pc[3]]
    constants = sorted({(op, b) for _, op, _, b in parsed if isinstance(b, int) and op in "&^+|"})
    assert len(parsed) == pc[1] and len(constants) == pc[2]
    creg = {x: j for j, x in enumerate(constants)}
    reg = {"i%d" % j: len(constants) + j - 8 for j in range(8, 16)}
    last, outputs = {}, set(pc[4])
    for k, (_, _, a, b) in enumerate(parsed):
        last[a] = k
        if isinstance(b, str):
            last[b] = k
    for x in outputs:
        last[x] = len(parsed)
    free, nxt, code = [], len(constants) + 8, []
    for k, (name, op, a, b) in enumerate(parsed):
        ra = reg[a]
        rb = reg[b] if isinstance(b, str) else (b if op in ("<<", ">>") else creg[(op, b)])
        for x in {a, b}:
            if isinstance(x, str) and last[x] == k and x not in outputs:
                heapq.heappush(free, reg.pop(x))
        d = heapq.heappop(free) if free else nxt
        if d == nxt:
            nxt += 1
        reg[name] = d
        code.append(_ins("recovery_circuit", {"+": "ADD", "^": "XOR", "&": "AND", "|": "OR", "<<": "SHL", ">>": "SHR"}[op],
                         "r%d" % d, "r%d" % ra, str(rb) if op in ("<<", ">>") else "r%d" % rb, GATE_BYTES))
    loads = [_ins("recovery_constants", "LOADI", "r%d" % creg[x], x[0], hex(x[1])) for x in constants]
    assert nxt <= REGISTERS
    return loads, code, nxt, [reg[x] for x in pc[4]]


def _fixed_program(st):
    """Emit the loop, handlers, setup and recovery control with fixed physical registers."""
    code, top = allocate(st)
    out = [_ins("step", {"^": "XOR", "&": "AND", "|": "OR"}[st.opsym[nm][0]],
                "r%d" % d, "r%d" % a, "r%d" % b, GATE_BYTES) for nm, d, a, b in code]
    assert top == 773 and not any(st.pin[:STAGE1_PLANES])
    acc, tmp, count, limit = ("r%d" % x for x in range(top, top + 4))
    out.append(_ins("stage1", "OR", acc, "r0", "r1", GATE_BYTES))
    out += [_ins("stage1", "OR", acc, acc, "r%d" % j, GATE_BYTES) for j in range(2, STAGE1_PLANES)]
    out.append(_ins("stage1", "NOT", acc, acc, "-", GATE_BYTES))
    out += [_ins("stage1_control", "CMP", tmp, acc, "0"), _ins("stage1_control", "BRZ", "@loop", tmp),
            _ins("loop", "ADDI", count, count, "1"), _ins("loop", "CMP", tmp, count, limit), _ins("loop", "BRGE", "@slice", tmp)]

    # Store and reload every plane explicitly. The compact loop bodies implement
    # lane extraction, the DP/key test, table scan and new-lane insertion.
    hs = [_ins("handlers", "STORE", "plane_copy+%d" % j, "r%d" % j) for j in range(256)]
    body = (("LOAD", tmp, "hit_budget"), ("ADDI", tmp, tmp, "1"), ("STORE", "hit_budget", tmp), ("CMP", tmp, "e2max"),
            ("BRGT", "@halt_stage1", tmp), ("CTZ", "r777", acc), ("BCLR", acc, acc), ("MOVI", "r778", "0"),
            ("MOVI", "r779", "0"), ("LOAD", "r780", "plane_copy[r779]"), ("SHR", "r780", "r780", "r777"),
            ("ANDI", "r780", "r780", "1"), ("SHL", "r780", "r780", "r779"), ("OR", "r778", "r778", "r780"),
            ("ADDI", "r779", "r779", "1"), ("CMP", tmp, "r779", "256"), ("BRLT", "@extract", tmp),
            ("ANDI", "r781", "r778", hex((1 << STAGE1_PLANES) - 1)), ("BRNZ", "@next_hit", "r781"), ("SHR", "r781", "r778", str(STAGE1_PLANES)),
            ("ANDI", "r781", "r781", hex((1 << 90) - 1)), ("CMP", tmp, "r781", "Tp"), ("BRGE", "@next_hit", tmp),
            ("LOAD", "r790", "finished"), ("ADDI", "r790", "r790", "1"), ("STORE", "finished", "r790"),
            ("SHR", "r782", "r778", "122"), ("SHL", "r783", "r782", "11"), ("OR", "r783", "r783", "r781"),
            ("MOVI", "r785", "0"),
            ("LOAD", "r784", "table[r785]"), ("ANDI", "r786", "r784", hex((1 << KEYBITS) - 1)), ("CMP", tmp, "r786", "r783"),
            ("BRZ", "@recover_match", tmp), ("ADDI", "r785", "r785", "1"), ("CMP", tmp, "r785", "table_count"),
            ("BRLT", "@scan", tmp), ("CMP", tmp, "table_count", "tmax"), ("BRGE", "@halt_full", tmp),
            ("LOAD", "r787", "trail[lane]"), ("SHL", "r786", "r787", str(KEYBITS)), ("OR", "r783", "r783", "r786"),
            ("STORE", "table[r785]", "r783"), ("ADDI", "r790", "r785", "1"), ("STORE", "table_count", "r790"),
            ("LOAD", "r787", "next_trail"), ("ADDI", "r788", "r787", "1"), ("STORE", "next_trail", "r788"),
            ("ADD", "r789", "random", "r787"), ("BR", "@insert_lane"),
            ("SHR", "r790", "r784", str(KEYBITS)), ("LOAD", "r791", "trail[lane]"), ("CALL", "@recover_pass1"),
            ("BR", "@halt_bad_recovery"), ("MOVI", "r779", "0"),
            ("LOAD", "r780", "plane_copy[r779]"), ("SHR", "r781", "r789", "r779"), ("ANDI", "r781", "r781", "1"),
            ("SHL", "r781", "r781", "r777"), ("ANDI", "r780", "r780", "~lane_bit"), ("OR", "r780", "r780", "r781"),
            ("STORE", "plane_copy[r779]", "r780"), ("ADDI", "r779", "r779", "1"), ("CMP", tmp, "r779", "256"),
            ("BRLT", "@insert_lane", tmp), ("STORE", "birth[lane]", count), ("STORE", "trail[lane]", "r787"),
            ("BR", "@reload"))
    hs += [_ins("handlers", *x) for x in body]
    hs += [_ins("handlers", "LOAD", "r%d" % j, "plane_copy+%d" % j) for j in range(256)]
    hs += [_ins("handlers", "NOP") for _ in range(HANDLER_CODE - len(hs))]
    assert len(hs) == HANDLER_CODE
    out += hs

    setup = [("RANDOM", "r773"), ("STORE", "random", "r773"), ("MOVI", "r774", "0"), ("MOVI", "r775", "256"),
             ("STORE", "plane_copy[r774]", "0"), ("ADDI", "r774", "r774", "1"), ("CMP", "r777", "r774", "r775"),
             ("BRLT", "@setup_zero", "r777"), ("MOVI", "r774", "0"), ("ADD", "r776", "r773", "r774"),
             ("STORE", "starts[r774]", "r776"), ("STORE", "trail[r774]", "r774"), ("STORE", "birth[r774]", "0"),
             ("MOV", "r777", "r774"), ("MOV", "r787", "r774"), ("MOV", "r789", "r776"), ("CALL", "@insert_lane"),
             ("ADDI", "r774", "r774", "1"), ("CMP", "r777", "r774", "r775"), ("BRLT", "@setup_starts", "r777"), ("CALL", "@reload"),
             ("MOVI", "r774", "0"), ("STORE", "batch", "r774"), ("STORE", "table_count", "r774"),
             ("LOAD", "r774", "batch"), ("LOAD", "r775", "birth[r774]"), ("SUB", "r776", "r774", "r775"),
             ("CMP", "r777", "r776", "age_cap"), ("BRLT", "@slice_next", "r777"), ("CALL", "@cut_insert"),
             ("LOAD", "r778", "cut_count"), ("ADDI", "r778", "r778", "1"), ("STORE", "cut_count", "r778"),
             ("CMP", "r777", "r778", "cmax"), ("BRGT", "@halt_cut", "r777"), ("ADDI", "r774", "r774", "1"),
             ("CMP", "r777", "r774", "256"), ("BRLT", "@slice_lane", "r777"), ("ADDI", limit, limit, str(1 << 48)),
             ("BR", "@step")]
    ss = [_ins("setup_cut_slice", *x) for x in setup]
    ss += [_ins("setup_cut_slice", "NOP") for _ in range(SETUP_CODE - len(ss))]
    assert len(ss) == SETUP_CODE
    out += ss

    loads, packed, packed_top, packed_outputs = _packed_program(st.qwords)
    assert packed_top < 700
    out += loads + packed
    common = [("CALL", "@packed"), ("RET",), *(("MOV", "r%d" % (33 + j), "r%d" % packed_outputs[j]) for j in range(8)),
              ("ADDI", "r708", "r708", "1"), ("CMP", "r709", "r708", "capr"), ("BRLE", "@recovery_batch", "r709")]
    pass1 = []
    for lane in (0, 1):
        pass1 += [("SHR", "r710", "r33", str(PITCH * lane)), ("ANDI", "r710", "r710", hex(M32)), ("BRNZ", "@p1_next", "r710"),
                  ("SHR", "r710", "r34", str(PITCH * lane)), ("ANDI", "r710", "r710", hex((1 << 90) - 1)), ("CMP", "r711", "r710", "Tp"),
                  ("BRGE", "@p1_next", "r711")]
    pass1 += [("CMP", "r711", "len0"), ("BRNZ", "@p1_flag0", "r711"), ("CMP", "r711", "len1"),
              ("BRNZ", "@p1_flag1", "r711"), ("MOV", "len0", "r708"), ("MOV", "len1", "r708")]
    pass2 = [("SHR", "r%d" % (712 + j), "r%d" % (33 + j), str(PITCH)) for j in range(8)]
    pass2 += [("XOR", "r%d" % (712 + j), "r%d" % (712 + j), "r%d" % (33 + j)) for j in range(8)]
    pass2 += [("OR", "r712", "r712", "r%d" % (712 + j)) for j in range(1, 8)]
    pass2 += [("ANDI", "r712", "r712", hex(REP * M32)), ("CMP", "r711", "r712", "0"), ("BRZ", "@collision", "r711")]
    rc = [_ins("recovery_common", *x) for x in common] + [_ins("recovery_pass1", *x) for x in pass1] + [_ins("recovery_pass2", *x) for x in pass2]
    assert (len(common), len(pass1), len(pass2), len(rc)) == (13, 20, 26, RECOVERY_CODE)
    return out + rc


_PROGRAM = {}


def program_image(st=None):
    st = st or step256()
    key = tuple(st.qwords)
    if key not in _PROGRAM:
        recs = _fixed_program(st)
        for rec in recs:
            for x in rec[2:5]:
                if x.startswith("r") and x[1:].isdigit():
                    assert int(x[1:]) < REGISTERS
        listing = "".join("%05d|%s|%s|%s|%s|%s|%d\n" % ((j,) + x) for j, x in enumerate(recs))
        by = {}
        for x in recs:
            by[x[0]] = by.get(x[0], 0) + 1
        _PROGRAM[key] = dict(records=recs, listing=listing, sha256=hashlib.sha256(listing.encode()).hexdigest(),
                             bytes=sum(x[5] for x in recs), short=sum(x[5] == GATE_BYTES for x in recs),
                             long=sum(x[5] == INSTR_BYTES for x in recs), sections=by)
    return _PROGRAM[key]


def stage1_ops(pin, s1):
    """Operations of the stage-1 test (mask of lanes whose s1 low digest bits are zero): OR over the positive planes, AND over
    the inverted planes, one complement if both kinds occur, one combine, one final complement; plus compare and branch."""
    npos = sum(1 for j in range(s1) if not pin[j])
    nneg = s1 - npos
    ops = max(npos - 1, 0) + max(nneg - 1, 0)
    if nneg:
        ops += 2 if npos else 1
    return ops + 1 + 2


def stage1(planes, s1, pin):
    """Mask of lanes whose s1 low digest bits are all zero."""
    nz = 0
    pos = [planes[j] for j in range(s1) if not pin[j]]
    neg = [planes[j] for j in range(s1) if pin[j]]
    if pos:
        acc = pos[0]
        for q in pos[1:]:
            acc |= q
        nz |= acc
    if neg:
        acc = neg[0]
        for q in neg[1:]:
            acc &= q
        nz |= acc ^ ALL
    return ALL ^ nz


INFLIGHT = 350                     # n = 18 plan only (sum of 256 exponential ages, units of L)


def _plan(n, Tp, kappa, tmax, Sb):
    c = CFG[n]
    s1, W = c["s1"], c["W"]
    if n == 256:
        assert LANES + tmax + CMAX < 1 << TBITS     # every trail number stored in an entry fits its field
    N, D = 1 << n, s1 + W
    L = Fraction(1 << D, Tp)
    if n == 256:
        B = _b256(Tp, tmax, kappa, Sb)
    else:                                                     # reduced widths: the plan of the 18-bit experiment
        ureq = isqrt(2 * N * LAMBDA.numerator // LAMBDA.denominator) + 2
        num, den = ureq + INFLIGHT * L + 1, CUTLOSS.denominator
        q = -(-(num * den) // (den - CUTLOSS.numerator))
        B = -(-q // LANES)
    cc = -(-kappa * L.numerator // L.denominator)
    fb = (Tp - 1).bit_length()
    return dict(n=n, s1=s1, W=W, D=D, Tp=Tp, fb=fb, kb=min(KEYBITS - fb, n - D), L=L, N=N, Q=B * LANES, B=B, kappa=kappa, Sb=Sb,
                c=cc, capr=cc + Sb, tmax=tmax, e2max=2 * B * LANES // (1 << s1) + 64,
                cmax=CMAX if n == 256 else 10 ** 9)


def tail_log2(mean, k):
    """log2 of the Chernoff bound exp(-mean) (e mean / k)^k on P(count >= k), k > mean."""
    return (-mean + k * (1 + log(mean / k))) / log(2)


_STEP256 = {}


def step256():
    if 256 not in _STEP256:
        _STEP256[256] = Step(256)
    return _STEP256[256]


def other_code(st=None):
    """Instructions besides the main body: handlers, recovery circuit/control, setup, cut and slice."""
    st = st or step256()
    return HANDLER_CODE + packed_circuit(st.qwords)[1] + RECOVERY_CODE + SETUP_CODE


def machine_constants(st=None, R=REGISTERS):
    """(PH, FILT, BODY, code bytes, tmax) of the n = 256 program with R registers (spill loads and stores added to the body)."""
    st = st or step256()
    ph = st.ops
    filt = stage1_ops(st.pin, STAGE1_PLANES)
    body = ph + (st.spill_ops(R) if R < REGISTERS else 0) + filt + LOOP_OPS
    pc = packed_circuit(st.qwords)                        # constants are loaded once into registers, 36 bytes each
    if R == REGISTERS:
        code = program_image(st)["bytes"]
        formula = (ph + filt - S1_BRANCH + pc[1]) * GATE_BYTES + (body - ph - filt + S1_BRANCH + other_code(st) - pc[1] + pc[2]) * INSTR_BYTES
        assert code == formula
    else:
        code = (ph + filt - S1_BRANCH + pc[1]) * GATE_BYTES + (body - ph - filt + S1_BRANCH + other_code(st) - pc[1] + pc[2]) * INSTR_BYTES
    tmax = (MEM_LIMIT - SPARE - code - R * 32 - COUNTERS - ADVICE) // ENTRY
    return ph, filt, body, code, tmax


def gen_scratch(nodes=None):
    """Scratch bytes of the runtime C generator (two passes, no node table): 8-bit use counts (a node is used up to 19 times at 7 rounds), one byte per node, for the nodes of the n = 256 network
    (constant, 256 inputs, one per gate), the signal state, the shadow stack and the result record.  Returns (total, use counts, nodes)."""
    nodes = nodes or len(trace(256)[0].nodes)
    assert nodes < 1 << 16
    uses = nodes + 1
    return uses + GEN_STATE + GEN_STACK + GEN_INFO + GEN_GLOBALS, uses, nodes


def gen_idle(tmax):
    """Bytes of the region that holds the table, the register file, and the counters and plane copy once the search runs; while the generator
    runs the search has not started and the same region holds the generator's code image and its scratch."""
    return ENTRY * tmax + REGFILE + COUNTERS


def phase_bytes(code, tmax):
    """(setup phase, search phase) resident bytes."""
    scratch = gen_scratch()[0]
    return code + ADVICE + COUNTERS + REGFILE + GEN_CODE * INSTR_BYTES + scratch, code + ADVICE + COUNTERS + REGFILE + ENTRY * tmax

def plan(n, kappa=None, Tp=None, R=REGISTERS):
    if n != 256:
        c = CFG[n]
        p = _plan(n, c["Tp"], c["kappa"], 0, c["Sb"])
        p["tmax"] = 4 * (p["Q"] // int(p["L"])) + 64
        return p
    kappa = kappa or KAPPA_256
    tmax = machine_constants(None, R)[4]
    if Tp:
        return _plan(256, Tp, kappa, tmax, CFG[256]["Sb"])
    if tmax < 1:
        return None
    lo, hi = 1.0, float(tmax + 1)                        # largest mean number of trails the table holds
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= TAIL_LOG2 else (lo, mid)
    for t in range(1500, 0, -1):                           # the largest Tp that reaches 0.39 at that mean
        if _lossq(t, lo, tmax, kappa, CFG[256]["Sb"])["P_lower"] >= P_MIN:
            return _plan(256, t, kappa, tmax, CFG[256]["Sb"])
    return None


def ledger(p=None, st=None, R=REGISTERS):
    """Operation budget in word operations (exact Fractions); units are operations / 1470 (C of blake3-r7)."""
    p = p or plan(256, None, None, R)
    st = st or step256()
    ph, filt, body, code, _ = machine_constants(st, R)
    gen = GEN_FACTOR * (2 * st.gen_calls + st.ops)           # the generator builds the network twice (use counts, then emission)
    parts = dict(main=body * p["B"],
                 slices=-(-p["B"] // p["Sb"]) * SLICE_OPS,
                 stage1_hits=p["e2max"] * HIT_OPS,
                 events=(p["tmax"] + 1) * (EVENT_OPS + 3 * p["tmax"]),
                 cuts=p["cmax"] * CUT_OPS,
                 recovery=(RECOVER_PASSES * p["capr"] + 1) * (packed_circuit(st.qwords)[1] + RECOVER_EXTRA) + 600 + packed_circuit(st.qwords)[2],
                 setup=SETUP_FIXED + gen)
    return dict(parts=parts, total=sum(parts.values()), plan=p, body=body, gen=gen)


def _lossq(Tp, q, tmax, kappa, Sb, rate=1.0, fine=20000, coarse=2000):
    """Lemma 2 of proof Section 4 for q = Q / L trails; `rate` scales the collision hazard (H1 (d) sensitivity)."""
    L = Fraction(1 << 122, Tp)
    c = -(-kappa * L.numerator // L.denominator)
    th, Lf, cf = Tp / 2.0 ** 122, float(L), float(c)
    Q, B, Np = q * Lf, q * Lf / LANES, 2.0 ** 256 / rate         # Q evaluations, B batches, N' (theta N is below float resolution)
    k = int(q) + 1
    while tail_log2(q, k) > -40:                                   # N1 ~ Binomial(Q, theta) <= k - 1 except with probability 2^-40
        k += 1
    n2, shift = k + LANES + 1, 1 / (1 - k * Q / Np)
    pi = lambda m: exp(-m * (m - 1) / (2 * Np))                    # Pi_m <= this; the collision term uses Pi_(Q-k+1) <= Pi_Q shift
    split = max(1.0, Q - 120 * LANES * Lf)                         # the detection penalty lives on the last 120 L batches: fine bins there
    edges = [split * i / coarse for i in range(coarse + 1)] + [split + (Q - split) * i / fine for i in range(1, fine + 1)]
    delay, pa = 0.0, 1.0
    for b in edges[1:]:
        pb = pi(b)
        delay += (pa - pb) * exp(-th * max(0.0, B - b / LANES))   # sum of (Pi_a - Pi_b) (1 - theta)^(B - ceil(b / 256)) over the bins (a, b]
        pa = pb
    p, ql, hq = exp(-cf * th), Q * Lf / Np, Q * (Q - 1) / (2 * Np)
    p2 = exp(-(cf - 1) * th) * (1 + (cf - 1) * th / (1 - th))
    hh = (Q * (Q - 1) / 2 + 2.0 ** TBITS * Q) / Np
    t = dict(collision=pi(Q) * shift, delay=delay * shift, own_trail=ql, long_partner=(cf + Sb) * Q * p * (q + LANES) / ((1 - p) * Np), age_cap=hq * p2,
             disturbance=hq * Lf * (Q + 2.0 ** TBITS) / Np, finished_count=2.0 ** -40,
             cut_halt=-expm1(n2 * log1p(-p)) - n2 * p * exp((n2 - 1) * log1p(-p)) + ql * (1 + (2 + kappa) * exp(-kappa / 2) + 2 * hq) + hq * p * (3 + 2 * kappa),
             key_false_match=tmax * (tmax - 1) / 2 * 2.0 ** -(min(KEYBITS - (Tp - 1).bit_length(), 134) + log(Tp, 2)),
             table_capacity=2.0 ** tail_log2(q, tmax - 59),
             tiny=Q * 2.0 ** TBITS / Np + k * k * Lf / Np + 255 * Q / Np + exp(min(700.0, -120 + (exp(2) - 1) * hh)) + 2.0 ** -90)
    t["sum"] = sum(t.values())
    t["P_lower"] = 1 - t["sum"]
    t.update(trails=q, k=k, n2=n2, p=p, p2=p2, ql=ql, hq=hq, hh=hh, shift=shift)
    return t


_B = {}


def _b256(Tp, tmax, kappa, Sb):
    """The least B (multiple of GRAIN) with P_lower >= P_MIN."""
    if (Tp, tmax, kappa) not in _B:
        L = Fraction(1 << 122, Tp)
        lo, hi = 1.0, float(tmax + 1)
        for _ in range(40):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if _lossq(Tp, mid, tmax, kappa, Sb)["P_lower"] >= P_MIN else (mid, hi)
        B = -(-int(hi * L / LANES) // GRAIN) * GRAIN
        B += GRAIN                     # one public planning grain above the floating transition
        while _lossq(Tp, float(B * LANES / L), tmax, kappa, Sb)["P_lower"] < P_MIN:
            B += GRAIN
        _B[(Tp, tmax, kappa)] = B
    return _B[(Tp, tmax, kappa)]


def loss(p, rate=1.0):
    """The probability losses of proof Section 4 (floats): the terms, their sum and the lower bound on the success probability."""
    return _lossq(p["Tp"], float(p["Q"] / p["L"]), p["tmax"], p["kappa"], p["Sb"], rate)


# -------- 6 search and recovery
class Halt(Exception):
    pass


class Engine:
    """The chain function g = f XOR q in two forms: step(planes) for 256 lanes and f2(xs) for the recovery (packed circuit with the XOR of q)."""

    def __init__(self, n):
        self.n = n
        st = Step(n)
        self.st, self.pin, self.step = st, st.pin, st.step

    def f2(self, xs):
        return packed_f(xs, self.n, self.st.qwords)

    def g_scalar(self, x):
        return f_scalar(x, self.n) ^ self.st.qint


class IdealEngine:
    """An ideal function of the same width (keyed blake2b) used as the control of test T3."""

    def __init__(self, n, key):
        self.n, self.key, self.pin = n, key, [0] * n
        self.nb = (n + 7) // 8

    def g(self, v):
        h = hashlib.blake2b(v.to_bytes(self.nb, "little"), key=self.key, digest_size=self.nb).digest()
        return int.from_bytes(h, "little") & ((1 << self.n) - 1)

    def step(self, *planes):
        vals = lanes_of(planes, self.n, self.pin)
        return pack_lanes([self.g(v) for v in vals], self.n, self.pin)

    def f2(self, xs):
        return [self.g(x) for x in xs]


def is_dp(x, p):
    """Mixed distinguished point: low s1 bits zero and the window above them below Tp."""
    return x & ((1 << p["s1"]) - 1) == 0 and (x >> p["s1"]) & ((1 << p["W"]) - 1) < p["Tp"]


def dp_key(x, p):
    """The kb bits above the window, then the fb low bits of the window value (which determine it)."""
    return (((x >> p["D"]) & ((1 << p["kb"]) - 1)) << p["fb"]) | ((x >> p["s1"]) & ((1 << p["fb"]) - 1))


def pack_entry(key, t):
    assert key < 1 << KEYBITS and t < 1 << TBITS
    return key | (t << KEYBITS)


def unpack_entry(e):
    return e & ((1 << KEYBITS) - 1), (e >> KEYBITS) & ((1 << TBITS) - 1)


def trail_lengths(p, r, ts, f2):
    """Pass 1 of the recovery: both trails (numbers ts) walk together from their starts, one packed batch per step, until each has
    reached a distinguished point; returns the two lengths.  More than capr steps is a halt."""
    mask = p["N"] - 1
    xs = [(r + ts[0]) & mask, (r + ts[1]) & mask]
    ls = [None, None]
    for k in range(1, p["capr"] + 1):
        xs = f2(xs)
        for i in (0, 1):
            if ls[i] is None and is_dp(xs[i], p):
                ls[i] = k
        if ls[0] is not None and ls[1] is not None:
            return ls
    raise Halt("recovery length")


def recover(p, r, t0, t1, f2):
    """t0, t1 = the numbers of two finished trails with the same end.  Returns (x, y), x != y, f(x) = f(y), or None.  Pass 1 recomputes
    the two lengths; pass 2: the longer trail moves alone for l1 - l2 steps, then both move together (two lanes of the packed circuit)."""
    mask = p["N"] - 1
    la, lb = trail_lengths(p, r, (t0, t1), f2)
    a, b = (t0, la), (t1, lb)
    if a[1] < b[1]:
        a, b = b, a
    if a[1] > p["capr"]:
        raise Halt("recovery length")
    xs = [(r + a[0]) & mask, (r + b[0]) & mask]
    for _ in range(a[1] - b[1]):
        xs[0] = f2([xs[0]])[0]
    if xs[0] == xs[1]:
        return None
    for _ in range(b[1] + 1):
        ya, yb = f2(xs)
        if ya == yb:
            return xs[0], xs[1]
        xs = [ya, yb]
    return None


def search(eng, p, r, cnt):
    """One attempt with the fresh random word r: the pair (x, y) or None.  Raises Halt at a budget.  Budgets: B batches,
    e2max stage-1 hits, tmax table keys, cmax cut trails, a recovery of at most capr batches."""
    n, mask, pin = p["n"], p["N"] - 1, eng.pin
    table, births, ts, nxt = {}, [0] * LANES, list(range(LANES)), LANES
    planes = pack_lanes([(r + t) & mask for t in ts], n, pin)
    cnt["inserts"] += LANES
    batches = 0
    while batches < p["B"]:
        planes = list(eng.step(*planes))
        batches += 1
        cnt["batches"] += 1
        hit = stage1(planes, p["s1"], pin)
        while hit:
            cnt["stage1_hits"] += 1
            if cnt["stage1_hits"] > p["e2max"]:
                raise Halt("stage-1 budget")
            l = (hit & -hit).bit_length() - 1
            hit &= hit - 1
            x = lane_value(planes, l, pin, n)
            if is_dp(x, p):
                key, length = dp_key(x, p), batches - births[l]
                cnt["finished"] += 1
                if key in table:
                    _, t0 = unpack_entry(table[key])
                    cnt["recoveries"] += 1
                    res = recover(p, r, t0, ts[l], eng.f2)
                    if res is None:
                        raise Halt("recovery found no pair")
                    return res
                if len(table) >= p["tmax"]:
                    raise Halt("table full")
                table[key] = pack_entry(key, ts[l])
                ts[l], nxt, births[l] = nxt, nxt + 1, batches
                planes = set_lane(planes, l, (r + ts[l]) & mask, pin, n)
                cnt["inserts"] += 1
        if batches % p["Sb"] == 0:
            for l in range(LANES):
                if batches - births[l] >= p["c"]:
                    cnt["cut"] += 1
                    if cnt["cut"] > p["cmax"]:
                        raise Halt("cut budget")
                    ts[l], nxt, births[l] = nxt, nxt + 1, batches
                    planes = set_lane(planes, l, (r + ts[l]) & mask, pin, n)
                    cnt["inserts"] += 1
    return None


class Counters(dict):
    def __missing__(self, k):
        return 0


def derive(seed, tag, bits=256):
    return int.from_bytes(hashlib.shake_256(("%s/%s" % (seed, tag)).encode()).digest((bits + 7) // 8), "little") & ((1 << bits) - 1)


def attempt(eng, p, seed, tag):
    cnt = Counters()
    try:
        res = search(eng, p, derive(seed, tag, p["n"]), cnt)
    except Halt as e:
        cnt["halt"] += 1
        res = None
    return res, cnt


# -------- 7 organizer experiments
N_T3 = 18                          # width of the search experiment and of the ideal control
N_T1 = 12                          # width of the family-law runs (fresh key)
M_T2, B_T2 = 2048, 21              # points per trial, projection width (event: low 21 bits of the digest)
T2_NAMES = ("w0", "w3", "w7", "xor8", "sum8", "p01", "p23")


def t1_run(seed, n=N_T1):
    """Family law, fresh random key K: steps until the first repeat of x -> low n bits of digest(K || x)."""
    key, x, seen = derive(seed, "k"), derive(seed, "s", n), set()
    while x not in seen:
        seen.add(x)
        x = f_scalar(x, n, key)
    return len(seen)


def e1_trial(seed, eng, ideal_cls):
    """T3 (target, organizer-checked pair) and the ideal control, one attempt each; T1 as an observation."""
    p = plan(N_T3)
    res, cnt = attempt(eng, p, seed, "t")
    ideal = ideal_cls(N_T3, hashlib.blake2b(("%s/ideal" % seed).encode(), digest_size=32).digest())
    res_i, cnt_i = attempt(ideal, p, seed, "i")
    obs = dict(target_ok=int(res is not None), ideal_ok=int(res_i is not None), target_batches=cnt["batches"],
               target_halt=cnt["halt"], ideal_halt=cnt_i["halt"], t1_steps=t1_run(seed))
    if res is None:
        return None, None, obs
    return message(res[0]), message(res[1]), obs


_M21 = (1 << B_T2) - 1
_F21 = sum(_M21 << (32 * i) for i in range(8))
_KS = sum(1 << (32 * i) for i in range(8))


def t2_columns(digs):
    """The seven projections (T2_NAMES) of each 256-bit digest, as seven lists of B_T2-bit values:
    word 0, word 3, word 7, xor of the 8 words, sum of the 8 words, and two 22-bit concatenations of 11-bit pieces."""
    m = _M21
    folded = [d ^ (d >> 128) for d in digs]
    folded = [d ^ (d >> 64) for d in folded]
    return [[d & m for d in digs], [(d >> 96) & m for d in digs], [(d >> 224) & m for d in digs],
            [(d ^ (d >> 32)) & m for d in folded],
            [(((d & _F21) * _KS) >> 224) & m for d in digs],
            [((d & 0x7FF) | (((d >> 32) & 0x7FF) << 11)) & m for d in digs],
            [(((d >> 64) & 0x7FF) | (((d >> 107) & 0x7FF) << 11)) & m for d in digs]]


def e2_trial(seed, tr, st256):
    """T2: M_T2 points of the target function (the block 0^32 || x, K = 0) at width 256 (source by trial index: uniform inputs, counter r + i, or iterates of g
    from 256 random starts), the 256-bit digests f(x) = (stored planes) XOR q, equal pairs in seven 21-bit projections.  w0 is the checked event."""
    src = tr % 3
    if src == 0:
        xs = [derive(seed, "u%d" % i) for i in range(M_T2)]
    elif src == 1:
        r = derive(seed, "r")
        xs = [(r + i) & ((1 << 256) - 1) for i in range(M_T2)]
    else:
        xs = None
    digs = []
    if xs is not None:
        for b in range(M_T2 // LANES):
            pl = pack_lanes(xs[b * LANES:(b + 1) * LANES], 256, st256.pin)
            digs += lanes_of(list(st256.step(*pl)), 256, st256.pin)
    else:
        cur = [derive(seed, "c%d" % l) for l in range(LANES)]
        xs = []
        for b in range(M_T2 // LANES):
            xs += cur
            cur = lanes_of(list(st256.step(*pack_lanes(cur, 256, st256.pin))), 256, st256.pin)
            digs += cur
    digs = [d ^ st256.qint for d in digs]                  # the circuit stores g(x) = f(x) XOR q; the projections are of the digest f(x)
    obs = {"source": src}
    pair = None
    for k, col in enumerate(t2_columns(digs)):
        name = T2_NAMES[k]
        obs["dup_" + name] = len(col) - len(set(col))
        if k == 0 and obs["dup_w0"]:
            first = {}
            for i, c in enumerate(col):
                if c in first and xs[first[c]] != xs[i]:
                    pair = (xs[first[c]], xs[i])
                    break
                first.setdefault(c, i)
    if pair is None:
        return None, None, obs
    return message(pair[0]), message(pair[1]), obs


def serve(req):
    eid, out = req["experiment_id"], []
    if eid == "bsrho-n18":
        eng = Engine(N_T3)
        for t in req["trials"]:
            a, b, obs = e1_trial(t["seed"], eng, IdealEngine)
            out.append({"trial": t["trial"], "message_a_hex": a.hex() if a else None, "message_b_hex": b.hex() if b else None,
                        "observations": obs})
    elif eid == "proj-k0-w256":
        st = step256()
        for t in req["trials"]:
            a, b, obs = e2_trial(t["seed"], t["trial"], st)
            out.append({"trial": t["trial"], "message_a_hex": a.hex() if a else None, "message_b_hex": b.hex() if b else None,
                        "observations": obs})
    else:
        raise ValueError("unknown experiment")
    return {"schema_version": 1, "trials": out}


# -------- 8 command line
def selftest():
    import random
    ok = True
    rnd = random.Random(3)
    st = step256()
    print("hash-consing hits", st.hits, "dead gates", st.dead, "(the machine generator keeps no node table: both must be 0)")
    ok &= st.hits == 0 and st.dead == 0
    print("n=256 step: ops", st.ops, "gates", st.gates, st.by, "peak live", st.peak_live(), "spill_ops(1024)", st.spill_ops(1024), "q weight", bin(st.qint).count("1"))
    code, regs = allocate(st)
    print("allocation: registers used", regs, "moves 0 (output j in register j)")
    pl0 = [rnd.getrandbits(256) for _ in range(256)]
    good = run_allocated(st, code, pl0) == list(st.step(*pl0))
    print("allocated code on a register file equals the step:", good)
    ok &= good
    # regression of the stored-plane step against the scalar 7-round compression: 4,096 lanes (16 batches of 256), full 256-bit g = f XOR q
    good, tot = True, 0
    for _ in range(16):
        xs = [rnd.getrandbits(256) for _ in range(LANES)]
        out = lanes_of(list(st.step(*pack_lanes(xs, 256, st.pin))), 256, st.pin)
        good &= all(out[l] == f_scalar(xs[l], 256) ^ st.qint for l in range(LANES))
        tot += LANES
    print("%d lanes, full 256-bit g = f XOR q, step vs scalar compression: %s" % (tot, good))
    ok &= good
    good = True
    for _ in range(16):
        cur = [rnd.getrandbits(256) for _ in range(LANES)]
        pl = pack_lanes(cur, 256, st.pin)
        for _ in range(7):
            pl = list(st.step(*pl))
            cur = [f_scalar(x, 256) ^ st.qint for x in cur]
        good &= lanes_of(pl, 256, st.pin) == cur
    print("4,096 lanes (16 x 256) chained for 7 steps, g = f XOR q vs scalar compression:", good)
    ok &= good
    e = Engine(N_T3)
    xs = [rnd.getrandbits(N_T3) for _ in range(LANES)]
    pl = pack_lanes(xs, N_T3, e.pin)
    for _ in range(5):
        pl = list(e.step(*pl))
        xs = [e.g_scalar(x) for x in xs]
    good = lanes_of(pl, N_T3, e.pin)[:LANES] == xs
    print("n=%d chain, 5 steps, 256 lanes:" % N_T3, good)
    ok &= good
    xs = [rnd.getrandbits(256) for _ in range(7)]
    good = packed_f(xs, 256, st.qwords) == [f_scalar(x, 256) ^ st.qint for x in xs]
    print("packed recovery circuit (%d ops, with the 8 XORs of q) vs scalar:" % packed_circuit(st.qwords)[1], good)
    ok &= good
    rows = [rnd.getrandbits(256) for _ in range(256)]
    good = transpose(transpose(rows)) == rows and (transpose(rows)[5] >> 9) & 1 == (rows[9] >> 5) & 1
    print("transpose:", good)
    ok &= good
    # the search at n = 18 finds recoverable collisions
    p = plan(N_T3)
    found = 0
    for s in range(6):
        res, cnt = attempt(e, p, "selftest/%d" % s, "t")
        if res is not None:
            found += 1
            ok &= res[0] != res[1] and f_scalar(res[0], N_T3) == f_scalar(res[1], N_T3)
    print("search n=%d: %d of 6 attempts returned a verified pair" % (N_T3, found))
    ok &= found > 0
    print("selftest", ok)
    return ok


def print_ledger(lg):
    from math import log2
    print({k: (str(v) if isinstance(v, Fraction) else v) for k, v in lg["plan"].items()})
    print("operations per batch (body)", lg["body"])
    for k, v in lg["parts"].items():
        print(k, v)
    print("N =", lg["total"])
    print("time_log2 = %.5f (unrounded %.8f)" % (log2(lg["total"] / UNIT) + 5e-6, log2(lg["total"] / UNIT)))


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--selftest":
        sys.exit(0 if selftest() else 1)
    elif arg == "--ledger":
        print_ledger(ledger())
        from math import log2
        for R in (512, 256):
            pR = plan(256, None, None, R)
            if pR is None:
                print("smaller file R = %d: spill ops per batch %d, no table fits in 2^20 bytes" % (R, step256().spill_ops(R)))
                continue
            lgR = ledger(pR, None, R)
            print("smaller file R = %d: spill ops per batch %d, body %d, tmax %d, Tp %d, time_log2 %.5f, success lower bound %.4f%s" % (
                R, step256().spill_ops(R), lgR["body"], pR["tmax"], pR["Tp"], log2(lgR["total"] / UNIT), loss(pR)["P_lower"],
                "" if loss(pR)["P_lower"] >= 0.39 else " (below 0.39: not a valid plan)"))
        st = step256()
        ph, filt, body, code, tmax = machine_constants(st)
        print("PH", ph, "filter", filt, "body", body, "code bytes", code, "tmax", tmax, "generator calls", st.gen_calls)
        print("memory bytes", ENTRY * tmax + code + REGFILE + COUNTERS + ADVICE, "limit", MEM_LIMIT)
        sc = gen_scratch()
        ph1, ph2 = phase_bytes(code, tmax)
        print("setup phase bytes", ph1, "search phase bytes", ph2, "peak", max(ph1, ph2), "limit", MEM_LIMIT, "fits", max(ph1, ph2) <= MEM_LIMIT)
        print("generator scratch", sc[0], "(use counts", sc[1], ", nodes", sc[2], ") + image", GEN_CODE * INSTR_BYTES, "=", sc[0] + GEN_CODE * INSTR_BYTES, "idle region", gen_idle(tmax), "fits", sc[0] + GEN_CODE * INSTR_BYTES <= gen_idle(tmax), "generator code instructions", GEN_CODE)
        image = program_image(st)
        print("program image", image["short"], "register-format +", image["long"], "long instructions =", image["bytes"], "bytes; sha256", image["sha256"])
        print("program sections", json.dumps(image["sections"], sort_keys=True, separators=(",", ":")))
        print("other code instructions", other_code(st), "main body", body, "total instructions", body + other_code(st))
        print("recovery circuit operations", packed_circuit(st.qwords)[1], "constants in registers", packed_circuit(st.qwords)[2], "q (hex)", "%064x" % st.qint)
    elif arg == "--program":
        sys.stdout.write(program_image()["listing"])
    elif arg == "--loss":
        for k, v in loss(plan(256)).items():
            print(k, v)
    elif arg == "--sweep":
        from math import log2
        for kappa in range(8, 17):
            p = plan(256, kappa)
            lg = ledger(p)
            ls = loss(p)
            print("kappa", kappa, "Tp", p["Tp"], "tmax", p["tmax"], "time_log2 %.5f" % log2(lg["total"] / UNIT), "P_lower %.5f" % ls["P_lower"])
    else:
        json.dump(serve(json.load(sys.stdin)), sys.stdout)
