"""Birthday collision search on 39-step SHA-256 (sha256-r39, one block) with 256 bit-sliced lanes, a ROLLED program, and distinguished points.

The message is M(x) = PREFIX || x: 20 zero bytes then the 32-byte big-endian x, 52 bytes, one block: words W0..W4 = prefix, W5..W12 = x, W13 = 0x80000000,
W14 = 0, W15 = 0x1A0.  f(x) is the 256-bit big-endian digest integer of the first 39 steps (standard IV, feed-forward).  The walk is on g(x) = f(x) XOR q, q the fixed
mask of the polarities of the digest planes of the generated circuit (planes are fed back as stored, no complement is computed); g(x) = g(y) iff f(x) = f(y).
The organizer experiments run the same program at reduced n (low n bits of g, high input planes 0).
Sections: 1 scalar digest, 2 packed 7-lane circuit (the recovery), 3 bit-sliced generator (one plane per bit: rotations are renaming; pivot full adders),
4 the rolled program (straight part, 4-step loop body run 8 times, feed-forward; register allocation; 36-byte records; interpreter), 5 plan, ledger, success bound,
6 search and recovery, 7 organizer experiments, 8 self test and command line, 9 the generator in C (`--gen-c`; `--text` prints the records).
Credit: the pivot full adder and the mask walk are the method of jungjipdo's 6ae36351, the register-file convention that of 67f781f8; the search, handlers,
recovery, ledger method and Lemma 2 are our own earlier bit-sliced BLAKE3 and packed SHA-256 entries.
"""
import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, log, log2, log1p, exp, comb

M32 = 0xFFFFFFFF
ROUNDS = 39
UNIT = 2812                        # organizer reference operation cost C of sha256-r39 (C(r) = 84 r - 464)
LANES, ALL = 256, (1 << 256) - 1
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
K = (0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
     0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
     0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
     0x650a7354, 0x766a0abb, 0x81c2c92e)
PREFIX = bytes(20)                                      # the constant 20-byte prefix of every message (20 zero bytes; no selection among prefixes)
PREFIX_WORDS = tuple(int.from_bytes(PREFIX[4 * i:4 * i + 4], "big") for i in range(5))      # message words W0..W4
TAIL = (0x80000000, 0, 0x1A0)                           # message words W13..W15 of a 52-byte message (0x80 pad byte, zero, length 416 bits)
PITCH, PLANES7 = 36, 7
REP = sum(1 << (PITCH * i) for i in range(PLANES7))
LIM = 1 << PITCH


# ---------------------------------------------------------------- 1 scalar digest
def _ror(v, k):
    return ((v >> k) | (v << (32 - k))) & M32


def digest_words(w, prefix=PREFIX_WORDS):
    ws = list(prefix) + list(w) + list(TAIL)
    for i in range(16, ROUNDS):
        x, y = ws[i - 15], ws[i - 2]
        ws.append((ws[i - 16] + (_ror(x, 7) ^ _ror(x, 18) ^ (x >> 3)) + ws[i - 7] + (_ror(y, 17) ^ _ror(y, 19) ^ (y >> 10))) & M32)
    a, b, c, d, e, f, g, h = IV
    for i in range(ROUNDS):
        t1 = (h + (_ror(e, 6) ^ _ror(e, 11) ^ _ror(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + ws[i]) & M32
        t2 = ((_ror(a, 2) ^ _ror(a, 13) ^ _ror(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) & M32
        a, b, c, d, e, f, g, h = (t1 + t2) & M32, a, b, c, (d + t1) & M32, e, f, g
    return [(u + v) & M32 for u, v in zip(IV, (a, b, c, d, e, f, g, h))]


def words_of(x):
    return [(x >> (32 * (7 - i))) & M32 for i in range(8)]


def int_of(w):
    return sum(w[i] << (32 * (7 - i)) for i in range(8))


def f_scalar(x, n=256):
    return int_of(digest_words(words_of(x))) & ((1 << n) - 1)


def message(x):
    return PREFIX + x.to_bytes(32, "big")




# ---------------------------------------------------------------- 2 packed tracer (the recovery circuit)
class Tracer:

    def __init__(self):
        self.lines, self.k, self.calls = [], 0, 0

    def emit(self, op, a, b):
        self.k += 1
        self.calls += 1
        name = "t%d" % self.k
        self.lines.append((name, op, a, b))
        return name

    def mask(self, a):
        return ("v", self.emit("&", a[1], M32), M32)

    def clean(self, a):
        return a if a[0] == "c" or a[2] <= M32 else self.mask(a)

    def add(self, *xs):
        self.calls += 1
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
        self.calls += 1
        if a[0] == "c" and b[0] == "c":
            return ("c", a[1] ^ b[1])
        if a[0] == "c":
            a, b = b, a
        if b[0] == "c":
            return a if b[1] == 0 else ("v", self.emit("^", a[1], b[1]), (1 << max(a[2].bit_length(), b[1].bit_length())) - 1)
        return ("v", self.emit("^", a[1], b[1]), (1 << max(a[2].bit_length(), b[2].bit_length())) - 1)

    def and_(self, a, b):
        self.calls += 1
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
        self.calls += 1
        if a[0] == "c":
            return ("c", _ror(a[1], r))
        h = self.emit("&", self.emit(">>", a[1], r), (1 << (32 - r)) - 1)
        lo = self.emit("&", self.emit("<<", a[1], 32 - r), ((1 << r) - 1) << (32 - r))
        return ("v", self.emit("|", h, lo), M32)

    def shr(self, a, k):
        self.calls += 1
        if a[0] == "c":
            return ("c", a[1] >> k)
        return ("v", self.emit("&", self.emit(">>", a[1], k), (1 << (32 - k)) - 1), (1 << (32 - k)) - 1)


def build_lines():
    t = Tracer()
    W = [("c", w) for w in PREFIX_WORDS] + [("v", "i%d" % i, M32) for i in range(8)] + [("c", w) for w in TAIL]
    for i in range(16, ROUNDS):
        x, y = W[i - 15], W[i - 2]
        s0 = t.xor(t.xor(t.ror(x, 7), t.ror(x, 18)), t.shr(x, 3))
        s1 = t.xor(t.xor(t.ror(y, 17), t.ror(y, 19)), t.shr(y, 10))
        W.append(t.add(W[i - 16], s0, W[i - 7], s1))
    a, b, c, d, e, f, g, h = [("c", w) for w in IV]
    bc = t.xor(b, c)
    for i in range(ROUNDS):
        s1 = t.xor(t.xor(t.ror(e, 6), t.ror(e, 11)), t.ror(e, 25))
        ch = t.xor(g, t.and_(e, t.xor(f, g)))
        t1 = t.add(h, s1, ch, ("c", K[i]), W[i])
        s0 = t.xor(t.xor(t.ror(a, 2), t.ror(a, 13)), t.ror(a, 22))
        ab = t.xor(a, b)
        mj = t.xor(t.and_(ab, bc), b)                      # majority; a ^ b of this step is b ^ c of the next
        bc = ab
        t2 = t.add(s0, mj)
        na, ne = t.clean(t.add(t1, t2)), t.clean(t.add(d, t1))
        a, b, c, d, e, f, g, h = na, a, b, c, ne, e, f, g
    out = [t.clean(t.add(x, ("c", w))) for x, w in zip((a, b, c, d, e, f, g, h), IV)]
    return t, out


class PackedStep:

    def __init__(self):
        t, out = build_lines()
        assert all(o[0] == "v" and o[2] <= M32 for o in out)
        self.lines, self.gen_calls = t.lines, t.calls
        self.outs = [o[1] for o in out]
        self.ops = len(self.lines)
        self.by = {}
        for _, op, _, _ in self.lines:
            self.by[op] = self.by.get(op, 0) + 1
        nl = chr(10)

        def operand(v, op):
            return v if isinstance(v, str) else (str(v) if op in ("<<", ">>") else str(REP * v))
        body = "".join("    %s=%s%s%s" % (nm, a, op, operand(b, op)) + nl for nm, op, a, b in self.lines)
        self.src = "def step(%s):" % ",".join("i%d" % j for j in range(8)) + nl + body + "    return (%s,)" % ",".join(self.outs) + nl
        ns = {}
        exec(compile(self.src, "<packed-step>", "exec"), {}, ns)
        self.step = ns["step"]


_PKS = []


def packed_kernel():
    if not _PKS:
        _PKS.append(PackedStep())
    return _PKS[0]


def ppack(xs):
    """The 8 packed words for up to 7 chain values (lane l holds xs[l])."""
    return [sum(((x >> (32 * (7 - i))) & M32) << (PITCH * l) for l, x in enumerate(xs)) for i in range(8)]


def plane_ops_q(qw):
    return sum(1 for w in qw if w)


def packed_f(xs, n, qw):
    out = packed_kernel().step(*ppack(xs))
    mask = (1 << n) - 1
    return [sum((((out[i] >> (PITCH * l)) & M32) ^ qw[7 - i]) << (32 * (7 - i)) for i in range(8)) & mask for l in range(len(xs))]


def packed_ops(qw):
    """Operations of the recovery circuit per batch: the kernel plus the XORs of q."""
    return packed_kernel().ops + plane_ops_q(qw)


# ---------------------------------------------------------------- 3 bit-sliced generator
ZERO, ONE = (0, 0), (0, 1)


class Gen:

    def __init__(self, n):
        self.n, self.nodes, self.calls = n, [("c",)], 0
        self.inputs = []
        for j in range(n):
            self.nodes.append(("v", j))
            self.inputs.append((len(self.nodes) - 1, 0))

    def mk(self, op, a, b):
        self.calls += 1
        if a > b:
            a, b = b, a
        self.nodes.append((op, a, b))
        return len(self.nodes) - 1

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

    def xorw(self, A, B):
        return [self.XOR(a, b) for a, b in zip(A, B)]



def _constw(v):
    return [ONE if (v >> i) & 1 else ZERO for i in range(32)]


def _sigma(g, A, r1, r2, r3, shift):
    out = []
    for j in range(32):
        t = g.XOR(A[(j + r1) % 32], A[(j + r2) % 32])
        out.append(g.XOR(t, (A[j + r3] if j + r3 < 32 else ZERO) if shift else A[(j + r3) % 32]))
    return out



# ---------------------------------------------------------------- 4 the rolled program: three networks, register allocation, 36-byte records
# Program = setup records (once) + straight segment S (schedule W16..W38, W' = K + W stored for steps 7..38, steps 0..6) + RESET (3) + loop body L (steps 7..38
# as 8 iterations of 4 steps, W' loaded, no moves) + 4 loop-control records + feed-forward segment E.  Records are (op, d, a, b), each one 36-byte instruction:
# ^ & | xor/and/or d,a,b; N not d,a; M move d,a; S set d,a (a = 0 or all ones); L load d from [p0 + a]; T store [d] from a; R set pointer d to a;
# A add a to pointer d; C compare pointer d with pointer a; J branch to record d if the compare was less.  Registers 0..1023 of 256 bits.
def _rnd(g, st, Wd, kc, first):
    """One step on (a, b, c, d, e, f, g, h, prev) (prev = a ^ b of the previous step): kc = K constant (straight segment) or None (W' loaded)."""
    a, b, c, d, e, f, gg, h, prev = st
    S1 = _sigma(g, e, 6, 11, 25, False)
    ch = [g.XOR(gg[j], g.AND(e[j], g.XOR(f[j], gg[j]))) for j in range(32)]
    t1 = g.add(g.add(_constw(kc), h), ch) if kc is not None else g.add(h, ch)
    t1 = g.add(g.add(t1, S1), Wd)
    S0 = _sigma(g, a, 2, 13, 22, False)
    ab, mj = [], []
    for j in range(32):
        ab.append(g.XOR(a[j], b[j]))
        mj.append(g.XOR(g.AND(ab[j], prev[j]), b[j]))
    t2 = g.add(S0, mj)
    if first:
        na = g.add(t1, t2)
        ne = g.add(d, t1)
    else:
        ne = g.add(d, t1)
        na = g.add(t1, t2)
    return (na, a, b, c, ne, e, f, gg, ab)


def _net_s():
    g = Gen(256)
    W = [_constw(w) for w in PREFIX_WORDS] + [[g.inputs[32 * (7 - i) + j] for j in range(32)] for i in range(8)] + [_constw(w) for w in TAIL]
    for i in range(16, ROUNDS):
        t = g.add(W[i - 16], _sigma(g, W[i - 15], 7, 18, 3, True))
        t = g.add(t, W[i - 7])
        W.append(g.add(t, _sigma(g, W[i - 2], 17, 19, 10, True)))
    WI = list(range(7, 13)) + list(range(16, ROUNDS))
    Wp = [g.add(_constw(K[i]), W[i]) for i in WI]
    v = [_constw(w) for w in IV]
    st = tuple(v) + ([g.XOR(v[1][j], v[2][j]) for j in range(32)],)
    for i in range(7):
        st = _rnd(g, st, W[i], K[i], True)
    return g, WI, Wp, [t for w in st for t in w]


def _net_l():
    g = Gen(416)
    I = g.inputs
    st = tuple([(I[32 * w + j][0], 0) for j in range(32)] for w in range(9))
    for s in range(4):
        st = _rnd(g, st, [I[288 + 32 * s + j] for j in range(32)], None, False)
    return g, [t for w in st for t in w]


def _net_e():
    g = Gen(256)
    out = [g.add([(g.inputs[32 * w + j][0], 0) for j in range(32)], _constw(IV[w])) for w in range(8)]
    return g, [t for k in range(7, -1, -1) for t in out[k]]


def _alloc(g, nin, fixed, ldaddr, outs, tgt, pol, stores, free0, E):
    """Streaming allocator (the C generator does the same in two passes): gates in creation order; a result takes the register of an operand that dies at the
    gate (not a pending target), else the lowest free register that is not a pending target; an output node takes its target register when it can; a W' plane
    is stored (after a NOT when its polarity is negative) as soon as it exists; at the end constants are set and the outputs that missed their target are copied."""
    nodes = g.nodes
    uses = [0] * len(nodes)
    for k in range(nin + 1, len(nodes)):
        uses[nodes[k][1]] += 1
        uses[nodes[k][2]] += 1
    want = {}
    for i, o in enumerate(outs):
        if o[0]:
            uses[o[0]] += 1
            want.setdefault(o[0], tgt[i])
    reg = dict(fixed)
    st = dict(free=sum(1 << r for r in free0 if r not in fixed.values()), pend=sum(1 << t for t in tgt), moves=0)

    def take(prefer=None):
        f = st["free"]
        if prefer is not None and f >> prefer & 1:
            r = prefer
        else:
            m = f & ~st["pend"] or f
            assert m, "out of registers"
            r = (m & -m).bit_length() - 1
        st["free"] &= ~(1 << r)
        return r

    def release(r):
        st["free"] |= 1 << r

    def store(v, r):
        for addr, neg in stores[v]:
            if neg:
                t = take()
                E(("N", t, r, 0))
                E(("T", addr, t, 0))
                release(t)
            else:
                E(("T", addr, r, 0))
    for v in sorted(stores):
        if v in reg:
            store(v, reg[v])
    for k in range(nin + 1, len(nodes)):
        op, x, y = nodes[k]
        for v in (x, y):
            if v not in reg:
                reg[v] = take()
                E(("L", reg[v], ldaddr[v], 0))
        uses[x] -= 1
        uses[y] -= 1
        dying = [v for v in (x, y) if uses[v] == 0]
        w, dst = want.get(k), None
        if w is not None:
            if st["free"] >> w & 1:
                dst = take(w)
            elif any(reg[v] == w for v in dying):
                dst = w
        if dst is None:
            for v in dying:
                if not st["pend"] >> reg[v] & 1 or reg[v] == w:
                    dst = reg[v]
                    break
        for v in dying:
            if reg[v] != dst:
                release(reg[v])
        if dst is None:
            dst = take()
        reg[k] = dst
        if dst == w:
            st["pend"] &= ~(1 << w)
        E(({"x": "^", "a": "&", "o": "|"}[op], dst, reg[x], reg[y]))
        if k in stores:
            store(k, dst)
        if uses[k] == 0:
            assert k in stores, "dead gate"
            release(dst)
    for i, o in enumerate(outs):
        if o[0] == 0:
            E(("S", tgt[i], 1 if o[1] ^ pol[i] else 0, 0))
    for i, o in enumerate(outs):
        if o[0] and reg[o[0]] != tgt[i]:
            if o[1] ^ pol[i]:
                E(("N", tgt[i], reg[o[0]], 0))
            else:
                E(("M", tgt[i], reg[o[0]], 0))
                st["moves"] += 1
    for i, o in enumerate(outs):
        if o[0] and reg[o[0]] == tgt[i] and o[1] ^ pol[i]:
            E(("N", tgt[i], tgt[i], 0))
    return st["moves"]


NSETUP = 98                       # setup records: two constant registers and the 96 constant planes of W'13..W'15 (K + the constant words)


def assemble():
    """(records, [S, L, E segment lengths], moves, generator calls of both passes of the three networks)"""
    R = [("S", 1023, 0, 0), ("S", 1022, 1, 0)]
    for i in (13, 14, 15):
        w = (K[i] + TAIL[i - 13]) & M32
        R += [("T", (i - 7) * 32 + j, 1022 if w >> j & 1 else 1023, 0) for j in range(32)]
    calls = moves = 0
    g, WI, Wp, outs = _net_s()
    stores = {}
    for wi, idx in enumerate(WI):
        for j in range(32):
            assert Wp[wi][j][0] != 0
            stores.setdefault(Wp[wi][j][0], []).append(((idx - 7) * 32 + j, Wp[wi][j][1]))
    moves += _alloc(g, 256, {j + 1: j for j in range(256)}, None, outs, [256 + i for i in range(288)], [0] * 288, stores, range(256, REGISTERS), R.append)
    calls += g.calls
    n0 = len(R) - NSETUP
    R += [("R", 0, 0, 0), ("R", 1, 0, 0), ("R", 2, 8, 0)]
    g, outs = _net_l()
    moves += _alloc(g, 416, {j + 1: 256 + j for j in range(288)}, {289 + m: m for m in range(128)}, outs, [256 + i for i in range(288)], [0] * 288, {},
                    list(range(256)) + list(range(544, REGISTERS)), R.append)
    calls += g.calls
    top = len(R) - n0 - NSETUP - 3
    R += [("A", 0, 128, 0), ("A", 1, 1, 0), ("C", 1, 2, 0), ("J", NSETUP + n0 + 3, 0, 0)]
    g, outs = _net_e()
    moves += _alloc(g, 256, {j + 1: 256 + j for j in range(256)}, None, outs, list(range(256)), [o[1] for o in outs], {}, list(range(256)) + list(range(544, REGISTERS)), R.append)
    calls += g.calls
    return R, [n0, top + 4, len(R) - n0 - top - 7 - NSETUP], moves, 2 * calls, outs


class Prog:
    """The program with its interpreter.  kernel = records executed per batch (setup excluded)."""

    def __init__(self):
        self.recs, self.nseg, self.moves, self.calls, outs = assemble()
        self.q = [o[1] for o in outs]
        self.qint = sum(b << j for j, b in enumerate(self.q))
        self.qwords = [(self.qint >> (32 * i)) & M32 for i in range(8)]
        self.pin = [0] * 256
        self.instr = len(self.recs)
        n0, n1, n2 = self.nseg
        self.kernel = n0 + 3 + 8 * n1 + n2
        self.mem = [0] * 1024
        self.run(0, NSETUP, [0] * REGISTERS)
        self.compile()

    def run(self, pc, end, regs):
        """Execute records pc..end-1 (the branch goes back); returns the number of records executed."""
        mem, recs, p, flag, n = self.mem, self.recs, [0, 0, 0], False, 0
        while pc < end:
            op, d, a, b = recs[pc]
            pc += 1
            n += 1
            if op == "^":
                regs[d] = regs[a] ^ regs[b]
            elif op == "&":
                regs[d] = regs[a] & regs[b]
            elif op == "|":
                regs[d] = regs[a] | regs[b]
            elif op == "T":
                mem[d] = regs[a]
            elif op == "N":
                regs[d] = regs[a] ^ ALL
            elif op == "L":
                regs[d] = mem[p[0] + a]
            elif op == "M":
                regs[d] = regs[a]
            elif op == "S":
                regs[d] = ALL if a else 0
            elif op == "R":
                p[d] = a
            elif op == "A":
                p[d] += a
            elif op == "C":
                flag = p[d] < p[a]
            elif op == "J" and flag:
                pc = d
        return n

    def compile(self):
        n0, n1, n2 = self.nseg
        e = NSETUP + n0 + 3

        def src(rs, pad):
            f = {"^": "r[%d] = r[%d] ^ r[%d]", "&": "r[%d] = r[%d] & r[%d]", "|": "r[%d] = r[%d] | r[%d]", "N": "r[%d] = r[%d] ^ ALL", "M": "r[%d] = r[%d]", "S": "r[%d] = ALL if %d else 0",
                 "L": "r[%d] = m[b + %d]", "T": "m[%d] = r[%d]"}
            return "".join(pad + (f[o] % ((d, x, y) if o in "^&|" else (d, x))) + chr(10) for o, d, x, y in rs if o in f)
        ns = {"ALL": ALL}
        exec(compile("def step(r, m):" + chr(10) + src(self.recs[NSETUP:NSETUP + n0], "    ") + "    for b in range(0, 1024, 128):" + chr(10) + src(self.recs[e:e + n1 - 4], "        ")
                     + src(self.recs[e + n1:], "    "), "<program>", "exec"), ns)
        self.fast = ns["step"]

    def step(self, *planes):
        """One batch: the low n of the 256 input planes in (the rest 0), the n output planes (g = f XOR q) out."""
        regs = list(planes) + [0] * (REGISTERS - len(planes))
        self.fast(regs, self.mem)
        return regs[:len(planes)]


# ---------------------------------------------------------------- lane transposition, packing, extraction
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




# ---------------------------------------------------------------- 5 plan, ledger and success bound (Lemma 2 of the proof, Section 4)
LAMBDA = Fraction(497, 1000)       # 1 - exp(-LAMBDA) = 0.39165
CUTLOSS = Fraction(15, 100000)     # allowance for cut-trail points, as a fraction of Q
TAIL_AGES = 1e-6                   # probability that the 256 unfinished trails hold more than M * L points
CMAX = 2                           # halt when more than CMAX trails are cut (more is charged as failure)
EPS = 1e-3                         # Lemma 2: tail budget of the finished-trail count and of the trail sums, each
P_MIN = 0.390000001                # plan target; Appendix A proves P >= 0.39 exactly
HZ = 257 / 2                       # weight of a squared trail length in the trail sums
GRAIN = 10 ** 24                   # B is a multiple of GRAIN
STAGE1_PLANES = 32
LOOP_OPS = 3                       # batch counter, compare with the slice limit, branch
HIT_OPS = 2800                     # a stage-1 hit lane: store the 256 planes, extract the lane (2,304), window test, bookkeeping
EVENT_OPS = 3800                   # a finished trail: key, entry, insert the new start in memory (3,072), reload (256), bookkeeping
CUT_OPS = 4200                     # a cut trail: age scan share, insert (3,072), reload (256), bookkeeping
SLICE_OPS = 1300                   # slice check: 256 ages
RECOVER_EXTRA = 64                 # per recovery batch beyond the packed circuit (exact test and loop 29; call and 8 moves 10)
INSTR_BYTES = 36                   # every instruction: opcode, registers, inline 256-bit immediate
GEN_CODE = 3507                    # WebAssembly instructions of GEN_C compiled by clang -Oz (llvm-objdump -d), charged 36 bytes each
HANDLER_CODE, SETUP_CODE, RECOVERY_CODE = 1000, 160, 47   # other instructions: handlers; setup, cut and slice; recovery besides its packed circuit
REGISTERS = 1024                   # declared register file of 256-bit words, counted as memory
REGFILE = REGISTERS * 32
COUNTERS = 16384                   # trail numbers, ages, counters (8 KiB) and the plane copy used by the handlers (8 KiB)
ARRAYS = 32768                     # the W' array: 32 words (steps 7..38) of 32 planes of 32 bytes
ENTRY = 26                         # table entry: key 8 bytes, trail number 2, length 16
MEM_LIMIT = 1 << 20
ADVICE = 0                         # no nonuniform advice (the mask q is derived by the generator at setup)
KAPPA_256 = 13
GEN_FACTOR = 200                   # word operations charged per generator primitive call and per emitted line
GEN_SCRATCH = 29709                 # static data of the C generator besides the record buffer and the counters (measured: 1 KiB shadow stack included)
SETUP_FIXED = 256 * 3100 + 20000   # 256 starts inserted in memory, reloaded, random word, counters
CFG = {18: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4),
       256: dict(s1=32, W=90, kappa=KAPPA_256, Sb=1 << 48)}


def stage1_ops(pin, s1):
    """Operations of the stage-1 test (mask of lanes whose s1 low stored planes are zero): OR over the positive planes, AND over
    the inverted planes, one complement if both kinds occur, one combine, one final complement; plus compare and branch."""
    npos = sum(1 for j in range(s1) if not pin[j])
    nneg = s1 - npos
    ops = max(npos - 1, 0) + max(nneg - 1, 0)
    if nneg:
        ops += 2 if npos else 1
    return ops + 1 + 2


def stage1(planes, s1, pin):
    """Mask of lanes whose s1 low stored planes are all zero."""
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


def inflight_m(lanes=LANES, eps=TAIL_AGES):
    m = lanes
    while True:
        x = m / lanes
        if exp(-lanes * (x - 1 - log(x))) <= eps:
            return m
        m += 1


INFLIGHT = inflight_m()


def _plan(n, Tp, kappa, tmax, Sb):
    c = CFG[n]
    s1, W = c["s1"], c["W"]
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
    return dict(n=n, s1=s1, W=W, D=D, Tp=Tp, fb=fb, kb=min(64 - fb, n - D), L=L, N=N, Q=B * LANES, B=B, kappa=kappa, Sb=Sb,
                c=cc, capr=cc + Sb, tmax=tmax, e2max=2 * B * LANES // (1 << s1) + 64,
                cmax=CMAX if n == 256 else 10 ** 9)


def tail_log2(mean, k):
    """log2 of the Chernoff bound exp(-mean) (e mean / k)^k on P(count >= k), k > mean."""
    return (-mean + k * (1 + log(mean / k))) / log(2)


_PROG = []


def prog():
    if not _PROG:
        _PROG.append(Prog())
    return _PROG[0]


def other_code(pr=None):
    return HANDLER_CODE + packed_ops((pr or prog()).qwords) + RECOVERY_CODE + SETUP_CODE


def machine_constants(pr=None):
    """(kernel ops per batch, stage-1 ops, body ops per batch, code bytes, tmax): body = kernel + stage 1 + loop; code = every instruction once at 36 bytes."""
    pr = pr or prog()
    filt = stage1_ops(pr.pin, STAGE1_PLANES)
    code = (pr.instr + filt + LOOP_OPS + other_code(pr)) * INSTR_BYTES
    return pr.kernel, filt, pr.kernel + filt + LOOP_OPS, code, (MEM_LIMIT - code - REGFILE - COUNTERS - ADVICE - ARRAYS) // ENTRY


def phase_bytes(code, tmax):
    """(setup phase, search phase) resident bytes.  Setup: the whole code as large as the final code, the counters, the generator image (GEN_CODE
    instructions of 36 bytes), the generator's data (the program records are the code) and the W' array region is not yet in use (the search owns it).
    Search: code, counters, register file, the W' array, the table."""
    return code + COUNTERS + GEN_CODE * INSTR_BYTES + GEN_SCRATCH, code + COUNTERS + REGFILE + ARRAYS + ENTRY * tmax


def plan(n, kappa=None, Tp=None):
    if n != 256:
        c = CFG[n]
        p = _plan(n, c["Tp"], c["kappa"], 0, c["Sb"])
        p["tmax"] = 4 * (p["Q"] // int(p["L"])) + 64
        return p
    kappa = kappa or KAPPA_256
    tmax = machine_constants()[4]
    if Tp:
        return _plan(256, Tp, kappa, tmax, CFG[256]["Sb"])
    lo, hi = 1.0, float(tmax + 1)                        # largest mean number of trails the table holds
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= -40 else (lo, mid)
    a, z = 1, 4097                                        # bisection: a Tp that reaches 0.39 at that mean (any Tp is a valid plan; not claimed optimal)
    while z - a > 1:
        m = (a + z) // 2
        a, z = (m, z) if _lossq(m, lo, tmax, kappa, CFG[256]["Sb"])["P_lower"] >= P_MIN else (a, m)
    return _plan(256, a, kappa, tmax, CFG[256]["Sb"])


def ledger(p=None, pr=None):
    """Operation budget in word operations (exact integers); units are operations / 2812 (C of sha256-r39)."""
    p = p or plan(256)
    pr = pr or prog()
    ph, filt, body, code, _ = machine_constants(pr)
    gen = GEN_FACTOR * (pr.calls + pr.instr)
    parts = dict(main=body * p["B"],
                 slices=-(-p["B"] // p["Sb"]) * SLICE_OPS,
                 stage1_hits=p["e2max"] * HIT_OPS,
                 events=p["tmax"] * (EVENT_OPS + 3 * p["tmax"]),
                 cuts=p["cmax"] * CUT_OPS,
                 recovery=p["capr"] * (packed_ops(pr.qwords) + RECOVER_EXTRA) + 600,
                 setup=SETUP_FIXED + gen)
    return dict(parts=parts, total=sum(parts.values()), plan=p, body=body, gen=gen)


def _zq(q, uc, uh, n):
    """Upper Chernoff quantile at EPS (units L^2) of n i.i.d. block terms (proof 4, Step 5): trapezoid rule on the convex exp(lam z(u) - u)."""
    k = 20000
    h = uc / k
    us = [i * h for i in range(k + 1)]
    zs = [HZ * u * u + 2 * q * max(0.0, u - uh) for u in us]

    def f(lam):
        a = [lam * z - u for z, u in zip(zs, us)]
        m = max(a)
        e = [exp(x - m) for x in a]
        return (n * (m + log(((sum(e) - (e[0] + e[-1]) / 2) * h + e[-1]) * (1 + 2.0 ** -30))) - log(EPS)) / lam
    lo, hi = -16.0, -4.0
    for _ in range(50):
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        lo, hi = (lo, m2) if f(exp(m1)) < f(exp(m2)) else (m1, hi)
    return f(exp((lo + hi) / 2))


def _lossq(Tp, q, tmax, kappa, Sb, rate=1.0):
    """Lemma 2 of proof Section 4 for q = Q / L trails; `rate` scales the collision hazard (H1 (d) sensitivity)."""
    L = Fraction(1 << 122, Tp)
    c = -(-kappa * L.numerator // L.denominator)
    uc, uh = float((c + Sb) / L), float((c // 2) / L)
    k = int(q) + 1
    while tail_log2(q, k) > log(EPS, 2) - 1e-6:           # N1 ~ Binomial(Q, 1/L) <= k - 1 except with prob. EPS
        k += 1
    nmax = k - 1 + LANES                                  # lottery blocks
    z = _zq(q, uc, uh, nmax)
    l2n = float(L * L / (1 << 256)) * rate                # L^2 / N, scaled
    kap = (2 * q * uc + HZ * uc * uc + 2 * q * (uc - uh)) * l2n   # cost of one colliding trail, over N
    w = 1.0
    for _ in range(100):
        w = exp(w * kap)                                  # ln w = w kap
    w *= 1 + 2.0 ** -40
    s0 = q * q / 2
    th = l2n * (w * (s0 - z - CMAX * (q * uc + min(q * (uc - uh), z / (LANES + 1) + q * float(Sb / L)))) - (w - 1) * s0)
    p, hq, ql, n2 = exp(-kappa), s0 * l2n, q * l2n, k + LANES + CMAX
    cuts = 1 - sum(comb(n2, j) * p ** j * exp((n2 - j) * log1p(-p)) for j in range(CMAX + 1))   # P(Bin(n2, p) > CMAX): fresh cut trails
    cuts += ql * (1 + (2 + kappa) * exp(-kappa / 2) + 2 * hq) + hq * p * (3 + 2 * kappa)       # colliding cut trails: S, X, J2a, J2b, Y
    t = dict(main=exp(-th), finished_count=EPS, trail_sums=EPS, cut_halt=cuts,
             collision_on_path=uc * q * l2n, key_false_match=tmax * (tmax - 1) / 2 * 2.0 ** -(min(64 - (Tp - 1).bit_length(), 134) + log(Tp, 2)),
             table_capacity=2.0 ** tail_log2(q, tmax - 59), long_finish=n2 * p * float(Sb / L), recovery_no_pair=2.0 ** -90)
    t["sum"] = sum(t.values())
    t["P_lower"] = 1 - t["sum"]
    t.update(theta=th, z=z, nmax=nmax, w=w, kap=kap, uc=uc, uh=uh, trails=q, k=k)
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
        while _lossq(Tp, float(B * LANES / L), tmax, kappa, Sb)["P_lower"] < P_MIN:
            B += GRAIN
        _B[(Tp, tmax, kappa)] = B
    return _B[(Tp, tmax, kappa)]


def loss(p, rate=1.0):
    return _lossq(p["Tp"], float(p["Q"] / p["L"]), p["tmax"], p["kappa"], p["Sb"], rate)


# ---------------------------------------------------------------- 6 search and recovery
class Halt(Exception):
    pass




# ---------------------------------------------------------------- 6b the chain engine
class Engine:
    """The chain function g = f XOR q of the width-n search: step(planes) runs the program on n planes (the other input planes are 0, the other output
    planes are dropped), f2(xs) is the packed recovery circuit with the XOR of q, g_scalar the scalar form."""

    def __init__(self, n):
        self.n, self.pr, self.pin = n, prog(), [0] * n

    def step(self, *planes):
        return self.pr.step(*planes)

    def f2(self, xs):
        return packed_f(xs, self.n, self.pr.qwords)

    def g_scalar(self, x):
        return f_scalar(x, self.n) ^ (self.pr.qint & ((1 << self.n) - 1))


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


def pack_entry(key, t, length):
    assert key < 1 << 64 and t < 1 << 16 and length < 1 << 128
    return key | (t << 64) | (length << 80)


def unpack_entry(e):
    return e & ((1 << 64) - 1), (e >> 64) & 0xFFFF, e >> 80


def recover(p, r, a, b, f2):
    """a, b = (t, length) of two finished trails with the same end.  Returns (x, y), x != y, f(x) = f(y), or None.  The longer
    trail moves alone for l1 - l2 steps, then both move together (two lanes of the packed circuit)."""
    mask = p["N"] - 1
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
                    _, t0, l0 = unpack_entry(table[key])
                    cnt["recoveries"] += 1
                    res = recover(p, r, (t0, l0), (ts[l], length), eng.f2)
                    if res is None:
                        raise Halt("recovery found no pair")
                    return res
                if len(table) >= p["tmax"]:
                    raise Halt("table full")
                table[key] = pack_entry(key, ts[l], length)
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


# ---------------------------------------------------------------- 7 organizer experiments
N_T3 = 18                          # width of the search experiment and of the ideal control
N_T1 = 12                          # width of the family-law runs (fresh key)
M_T2, B_T2 = 512, 18               # points per trial (two batches), projection width (event: low 18 bits of the digest)
T2_NAMES = ("w0", "w3", "w7", "xor8", "sum8", "p01", "p23")


def t1_run(seed, n=N_T1):
    kw = words_of(derive(seed, "k", 160))[3:]
    x, seen = derive(seed, "s", n), set()
    while x not in seen:
        seen.add(x)
        x = int_of(digest_words([0] * 6 + [(x >> 32) & M32, x & M32], kw)) & ((1 << n) - 1)
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


_MB = (1 << B_T2) - 1
_FB = sum(_MB << (32 * i) for i in range(8))
_KS = sum(1 << (32 * i) for i in range(8))


def t2_columns(digs):
    m = _MB
    folded = [d ^ (d >> 128) for d in digs]
    folded = [d ^ (d >> 64) for d in folded]
    return [[d & m for d in digs], [(d >> 96) & m for d in digs], [(d >> 224) & m for d in digs],
            [(d ^ (d >> 32)) & m for d in folded],
            [(((d & _FB) * _KS) >> 224) & m for d in digs],
            [((d & 0x7FF) | (((d >> 32) & 0x7FF) << 11)) & m for d in digs],
            [(((d >> 64) & 0x7FF) | (((d >> 107) & 0x7FF) << 11)) & m for d in digs]]


def e2_trial(seed, tr, st256):
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
    if eid == "bssha-n18":
        eng = Engine(N_T3)
        for t in req["trials"]:
            a, b, obs = e1_trial(t["seed"], eng, IdealEngine)
            out.append({"trial": t["trial"], "message_a_hex": a.hex() if a else None, "message_b_hex": b.hex() if b else None,
                        "observations": obs})
    elif eid == "proj-k0-w256":
        st = prog()
        for t in req["trials"]:
            a, b, obs = e2_trial(t["seed"], t["trial"], st)
            out.append({"trial": t["trial"], "message_a_hex": a.hex() if a else None, "message_b_hex": b.hex() if b else None,
                        "observations": obs})
    else:
        raise ValueError("unknown experiment")
    return {"schema_version": 1, "trials": out}



# ---------------------------------------------------------------- 8 self test and command line
def text():
    return "".join("%s %d %d %d\n" % r for r in prog().recs)


def selftest():
    import random
    rnd = random.Random(3)
    pr = prog()
    reg = max(max(r[1:4]) for r in pr.recs if r[0] in "^&|") + 1
    print("records", pr.instr, "segments", pr.nseg, "moves", pr.moves, "kernel", pr.kernel, "registers used", reg, "text sha256", hashlib.sha256(text().encode()).hexdigest())
    lo = max(max(r[1:4]) for r in pr.recs[NSETUP + pr.nseg[0]:] if r[0] in "^&|") + 1
    print("registers used after the straight part:", lo, "(the pointer registers p0..p2 are 1021..1023)")
    ok = reg <= REGISTERS and lo <= 1021 and pr.instr == NSETUP + sum(pr.nseg) + 3
    t = True
    for xs in [[rnd.getrandbits(256) for _ in range(LANES)] for _ in range(8)] + [[0] * LANES, [(1 << 256) - 1] * LANES]:
        out = lanes_of(list(pr.step(*pack_lanes(xs, 256, pr.pin))), 256, pr.pin)
        t &= all(out[l] == f_scalar(xs[l]) ^ pr.qint for l in range(LANES))
    print("2,560 lanes (10 batches), full 256-bit g = f XOR q, program vs scalar 39-step compression:", t)
    ok &= t
    regs = [rnd.getrandbits(256) for _ in range(256)] + [0] * (REGISTERS - 256)
    ref = list(regs)
    mem1 = list(pr.mem)
    n = pr.run(NSETUP, len(pr.recs), regs)
    pr.mem[:] = mem1
    fast = list(ref)
    pr.fast(fast, pr.mem)
    t = n == pr.kernel and fast[:256] == regs[:256]
    print("records executed per batch by the interpreter", n, "kernel", pr.kernel, "; the compiled form gives the same 256 output planes:", t)
    ok &= t
    cur = [rnd.getrandbits(256) for _ in range(LANES)]
    pl = pack_lanes(cur, 256, pr.pin)
    for _ in range(4):
        pl = list(pr.step(*pl))
        cur = [f_scalar(x) ^ pr.qint for x in cur]
    t = lanes_of(pl, 256, pr.pin) == cur
    print("256 lanes chained for 4 steps:", t)
    ok &= t
    e = Engine(N_T3)
    xs = [rnd.getrandbits(N_T3) for _ in range(LANES)]
    pl = pack_lanes(xs, N_T3, e.pin)
    for _ in range(5):
        pl = list(e.step(*pl))
        xs = [e.g_scalar(x) for x in xs]
    t = lanes_of(pl, N_T3, e.pin) == xs
    print("n=%d chain, 5 steps:" % N_T3, t)
    ok &= t
    xs = [rnd.getrandbits(256) for _ in range(7)]
    t = packed_f(xs, 256, pr.qwords) == [f_scalar(x) ^ pr.qint for x in xs]
    print("packed recovery circuit (%d ops) vs scalar:" % packed_ops(pr.qwords), t)
    ok &= t
    rows = [rnd.getrandbits(256) for _ in range(256)]
    t = transpose(transpose(rows)) == rows and (transpose(rows)[5] >> 9) & 1 == (rows[9] >> 5) & 1
    print("transpose:", t)
    ok &= t
    p, found = plan(N_T3), 0
    for s in range(6):
        res, cnt = attempt(e, p, "selftest/%d" % s, "t")
        if res is not None:
            found += 1
            ok &= res[0] != res[1] and f_scalar(res[0], N_T3) == f_scalar(res[1], N_T3)
    print("search n=%d: %d of 6 attempts returned a verified pair" % (N_T3, found))
    ok &= found > 0
    print("selftest", bool(ok))
    return ok


def print_ledger(lg):
    print({k: (str(v) if isinstance(v, Fraction) else v) for k, v in lg["plan"].items()})
    print("operations per batch (body)", lg["body"])
    for k, v in lg["parts"].items():
        print(k, v)
    print("N =", lg["total"])
    print("time_log2 = %.5f (unrounded %.8f)" % (log2(lg["total"] / UNIT) + 5e-6, log2(lg["total"] / UNIT)))




# ---------------------------------------------------------------- 9 the circuit generator in C
# The generator of sections 3 and 4 (pivot adder, networks, register allocation, records) in freestanding C, two passes per network, no node table.  Compiled to
# WebAssembly (clang -Oz) and run in a sandbox with 16 pages (1,048,576 bytes) of guest memory: it emits the records of `--text` exactly (proof 3.6).
GEN_C = r'''/* Freestanding C generator of the rolled 256-lane bit-sliced 39-step SHA-256 program (bssha.py: Gen, the three networks, the register allocator, the 36-byte
   records).  No libc, no malloc, no imports.  Exports: run(), info_ptr(), code_ptr().  Each network is built twice: pass 0 counts the uses of every node (one byte
   per node) and records the outputs and the stores; pass 1 builds it again and emits.  A gate is a new node every time (no table); node numbers are creation order.
   A signal is neg bit 0, node bits 1-16, register from bit 17.  Segments: 0 straight (steps 0-6, schedule, W' stores), 1 loop body (4 steps), 2 feed-forward.
   Record of 36 bytes: byte 0 opcode character, bytes 1-6 three little-endian 16-bit fields (d, a, b), the rest zero. */
typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32;
#define NMAX 12913
#define NREC 19972
#define NSETUP 98
#define N 256
#define NODE(s) (((s) >> 1) & 0xFFFFu)
#define REG(s) ((s) >> 17)
#define ZERO 0u
#define ONE 1u
static u8 code[NREC][36];
__attribute__((used)) static u8 counters[16384];
static u8 uses[NMAX];
static u32 fb[32], pb[32], W[39][32], V[9][32], ab[32], mj[32], ch[32], S0[32], S1[32], s0[32], s1[32], T1[32], T2[32], KW[32], NA[32], NE[32];
static u16 oid[288], oix[288], oreg[288], onode[288], sid[928], sad[928], lreg[128];
static u8 oneg[288], sng[928];
static u32 seg, pass, nn, nin, nO, nE, nS, co, cs, calls, err, kk, nmov, loopat;
static struct { u32 ninst, nreg, nodes0, nodes1, nodes2, calls, err, moves, n0, n1, n2, sz_code, sz_ctr, sz_uses, sz_state; u8 q[32]; } info;
static const u32 IV[8] = {0x6A09E667u,0xBB67AE85u,0x3C6EF372u,0xA54FF53Au,0x510E527Fu,0x9B05688Cu,0x1F83D9ABu,0x5BE0CD19u};
static const u32 K[39] = {0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,
  0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
  0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,
  0x650a7354u,0x766a0abbu,0x81c2c92eu};
static void emit(u32 op, u32 d, u32 a, u32 b) {
  if (kk >= NREC) { err = 5; return; }
  u8 *r = code[kk++];
  r[0] = (u8)op; r[1] = (u8)d; r[2] = (u8)(d >> 8); r[3] = (u8)a; r[4] = (u8)(a >> 8); r[5] = (u8)b; r[6] = (u8)(b >> 8);
}
static int isfree(u32 r) { return (fb[r >> 5] >> (r & 31)) & 1; }
static void release(u32 r) { fb[r >> 5] |= 1u << (r & 31); }
static u32 take(int prefer) {
  u32 r = 0, w;
  if (prefer >= 0 && isfree((u32)prefer)) { fb[prefer >> 5] &= ~(1u << (prefer & 31)); return (u32)prefer; }
  for (w = 0; w < 32; w++) if (fb[w] & ~pb[w]) { r = 32 * w + (u32)__builtin_ctz(fb[w] & ~pb[w]); break; }
  if (w == 32) for (w = 0; w < 32; w++) if (fb[w]) { r = 32 * w + (u32)__builtin_ctz(fb[w]); break; }
  if (w == 32) { err = 8; return 0; }
  fb[r >> 5] &= ~(1u << (r & 31));
  return r;
}
static u32 tgt(u32 i) { return seg == 2 ? i : 256 + i; }
static u32 fixedreg(u32 n) { return seg == 0 ? n - 1 : 256 + n - 1; }
static void dostore(u32 r, u32 addr, u32 neg) {
  if (neg) { u32 t = take(-1); emit('N', t, r, 0); emit('T', addr, t, 0); release(t); } else emit('T', addr, r, 0);
}
static u32 getreg(u32 s) {
  u32 n = NODE(s);
  if (seg == 1 && n > 288 && n <= 416) {
    u32 m = n - 289;
    if (!lreg[m]) { u32 r = take(-1); lreg[m] = (u16)(r + 1); emit('L', r, m, 0); }
    return lreg[m] - 1u;
  }
  return REG(s);
}
static u32 mk(u32 op, u32 x, u32 y) {
  calls++;
  if (NODE(x) > NODE(y)) { u32 t = x; x = y; y = t; }
  u32 id = nn++, a = NODE(x), b = NODE(y);
  if (id >= NMAX) { err = 1; return 0; }
  if (pass == 0) {
    if (uses[a] == 255 || uses[b] == 255) { err = 6; return 0; }
    uses[a]++; uses[b]++;
    return id << 1;
  }
  u32 rx = getreg(x), ry = getreg(y), had = 0;
  int want = -1, dst = -1;
  u32 dx = --uses[a] == 0, dy = --uses[b] == 0;
  if (co < nE && oid[co] == id) want = (int)tgt(oix[co]);
  if (want >= 0) {
    if (isfree((u32)want)) dst = (int)take(want);
    else { if (dx && rx == (u32)want) dst = want; if (dy && ry == (u32)want) dst = want; }
  }
  if (dst < 0) {
    if (dx && (!((pb[rx >> 5] >> (rx & 31)) & 1) || rx == (u32)want)) dst = (int)rx;
    else if (dy && (!((pb[ry >> 5] >> (ry & 31)) & 1) || ry == (u32)want)) dst = (int)ry;
  }
  if (dx && rx != (u32)dst) release(rx);
  if (dy && ry != (u32)dst) release(ry);
  if (dst < 0) dst = (int)take(-1);
  if (dst == want) pb[dst >> 5] &= ~(1u << (dst & 31));
  emit(op == 0 ? '^' : op == 1 ? '&' : '|', (u32)dst, rx, ry);
  while (co < nE && oid[co] == id) oreg[oix[co++]] = (u16)dst;
  while (cs < nS && sid[cs] == id) { dostore((u32)dst, sad[cs], sng[cs]); cs++; had = 1; }
  if (uses[id] == 0) { if (!had) err = 9; release((u32)dst); }
  return (id << 1) | ((u32)dst << 17);
}
static u32 XOR(u32 x, u32 y) {
  calls++;
  if (!NODE(x)) return y ^ (x & 1);
  if (!NODE(y)) return x ^ (y & 1);
  if (NODE(x) == NODE(y)) return (x ^ y) & 1;
  return mk(0, x, y) ^ ((x ^ y) & 1);
}
static u32 AND(u32 x, u32 y) {
  calls++;
  if (!NODE(x)) return (x & 1) == 0 ? ZERO : y;
  if (!NODE(y)) return (y & 1) == 0 ? ZERO : x;
  if (NODE(x) == NODE(y)) return x == y ? x : ZERO;
  if (!(x & 1) && !(y & 1)) return mk(1, x, y);
  if ((x & 1) && (y & 1)) return mk(2, x, y) | 1;
  u32 p = (x & 1) == 0 ? x : y, q = (x & 1) == 0 ? y : x;
  return XOR(p, mk(1, p, q));
}
static void fa(u32 a, u32 b, u32 c, u32 *sum, u32 *carry) {
  u32 ops[3] = {a, b, c}, vs[3], nv = 0, k = 0, nc = 0, cs3[3] = {0, 0, 0};
  for (int i = 0; i < 3; i++) {
    if (!NODE(ops[i])) { cs3[nc++] = ops[i] & 1; k ^= ops[i] & 1; } else vs[nv++] = ops[i];
  }
  if (nv == 3) {
    u32 p = 0, x = 0, y = 0;
    for (int pi = 0; pi < 3; pi++) {
      u32 o0 = vs[pi == 0 ? 1 : 0], o1 = vs[pi == 2 ? 1 : 2];
      if ((o0 & 1) == (o1 & 1)) { p = vs[pi]; x = o0; y = o1; break; }
    }
    u32 u = XOR(x, p);
    u32 s = XOR(u, y);
    u32 w = XOR(y, p);
    u32 an = AND(u, w);
    *sum = s; *carry = XOR(an, p); return;
  }
  if (nv == 2) {
    u32 x = vs[0], y = vs[1];
    u32 t = XOR(x, y);
    u32 s = t ^ k;
    if ((x & 1) == (y & 1)) {
      if (k == 0) { *sum = s; *carry = AND(x, y); return; }
      *sum = s; *carry = AND(x ^ 1, y ^ 1) ^ 1; return;
    }
    u32 nt = t ^ 1;
    u32 xx = (x & 1) == (nt & 1) ? x : y;
    if (k == 0) { *sum = s; *carry = AND(xx, nt); return; }
    *sum = s; *carry = AND(xx ^ 1, t ^ 1) ^ 1; return;
  }
  if (nv == 1) {
    u32 x = vs[0], k1 = cs3[0], k2 = cs3[1];
    *sum = x ^ k; *carry = (k1 == 1 && k2 == 1) ? ONE : (k1 == 0 && k2 == 0) ? ZERO : x; return;
  }
  u32 kk3 = cs3[0] + cs3[1] + cs3[2];
  *sum = (kk3 % 2 == 0) ? ZERO : ONE; *carry = kk3 >= 2 ? ONE : ZERO;
}
static void add(const u32 *A, const u32 *B, u32 *out) {
  u32 c = ZERO;
  for (int i = 0; i < 32; i++) {
    if (i == 31) out[i] = XOR(XOR(A[i], B[i]), c);
    else { u32 si; fa(A[i], B[i], c, &si, &c); out[i] = si; }
  }
}
static void sigma(u32 *out, const u32 *A, int r1, int r2, int r3, int shift) {
  for (int j = 0; j < 32; j++) {
    u32 t = XOR(A[(j + r1) & 31], A[(j + r2) & 31]);
    u32 z = shift ? (j + r3 < 32 ? A[j + r3] : ZERO) : A[(j + r3) & 31];
    out[j] = XOR(t, z);
  }
}
static void constw(u32 *w, u32 val) { for (int i = 0; i < 32; i++) w[i] = (val >> i) & 1u; }
static u32 inp(u32 j) { return ((1 + j) << 1) | ((seg == 0 ? j : 256 + j) << 17); }
static void outp(u32 i, u32 s) { if (pass == 0) { onode[i] = (u16)NODE(s); oneg[i] = (u8)(s & 1); } }
static void stor(u32 addr, u32 s) {
  if (pass != 0) return;
  if (!NODE(s)) { err = 3; return; }
  sid[nS] = (u16)NODE(s); sad[nS] = (u16)addr; sng[nS] = (u8)(s & 1); nS++;
}
/* one step: state V[0..7] (a..h) and prv = V[8]; Wd the schedule word (W' when !withK); first: new a before new e (straight segment), else new e first (loop body) */
static void rnd(int withK, u32 kc, const u32 *Wd, int first) {
  sigma(S1, V[4], 6, 11, 25, 0);
  for (int j = 0; j < 32; j++) ch[j] = XOR(V[6][j], AND(V[4][j], XOR(V[5][j], V[6][j])));
  if (withK) { constw(KW, kc); add(KW, V[7], T1); add(T1, ch, T1); } else add(V[7], ch, T1);
  add(T1, S1, T1); add(T1, Wd, T1);
  sigma(S0, V[0], 2, 13, 22, 0);
  for (int j = 0; j < 32; j++) { ab[j] = XOR(V[0][j], V[1][j]); mj[j] = XOR(AND(ab[j], V[8][j]), V[1][j]); }
  add(S0, mj, T2);
  if (first) { add(T1, T2, NA); add(V[3], T1, NE); } else { add(V[3], T1, NE); add(T1, T2, NA); }
  for (int j = 0; j < 32; j++) {
    V[3][j] = V[2][j]; V[2][j] = V[1][j]; V[1][j] = V[0][j]; V[0][j] = NA[j];
    V[7][j] = V[6][j]; V[6][j] = V[5][j]; V[5][j] = V[4][j]; V[4][j] = NE[j]; V[8][j] = ab[j];
  }
}
static void trace(void) {
  nn = 1 + nin;
  if (seg == 0) {
    for (int i = 0; i < 5; i++) constw(W[i], 0);
    for (int i = 0; i < 8; i++) for (int b = 0; b < 32; b++) W[5 + i][b] = inp(32 * (7 - i) + b);
    constw(W[13], 0x80000000u); constw(W[14], 0); constw(W[15], 0x1A0u);
    for (int i = 16; i < 39; i++) {
      sigma(s0, W[i - 15], 7, 18, 3, 1);
      add(W[i - 16], s0, T1); add(T1, W[i - 7], T1);
      sigma(s1, W[i - 2], 17, 19, 10, 1);
      add(T1, s1, W[i]);
    }
    for (int i = 7; i < 39; i++) {
      if (i == 13) i = 16;
      constw(KW, K[i]); add(KW, W[i], T2);
      for (int j = 0; j < 32; j++) stor((u32)(i - 7) * 32 + j, T2[j]);
    }
    for (int i = 0; i < 8; i++) constw(V[i], IV[i]);
    for (int j = 0; j < 32; j++) V[8][j] = XOR(V[1][j], V[2][j]);
    for (int i = 0; i < 7; i++) rnd(1, K[i], W[i], 1);
    for (int w = 0; w < 9; w++) for (int j = 0; j < 32; j++) outp(32 * w + j, V[w][j]);
  } else if (seg == 1) {
    for (int w = 0; w < 9; w++) for (int j = 0; j < 32; j++) V[w][j] = inp(32 * w + j);
    for (int s = 0; s < 4; s++) { for (int j = 0; j < 32; j++) T2[j] = inp(288 + 32 * s + j); rnd(0, 0, T2, 0); }
    for (int w = 0; w < 9; w++) for (int j = 0; j < 32; j++) outp(32 * w + j, V[w][j]);
  } else {
    for (int w = 0; w < 8; w++) for (int j = 0; j < 32; j++) V[w][j] = inp(32 * w + j);
    for (int k = 0; k < 8; k++) {
      u32 cw[32], r[32];
      constw(cw, IV[k]);
      add(V[k], cw, r);
      for (int b = 0; b < 32; b++) outp(32 * (7 - k) + b, r[b]);
    }
  }
}
static void sortent(void) {                                   /* entries by node id, stable */
  nE = 0;
  for (u32 i = 0; i < nO; i++) if (onode[i]) {
    u32 t = nE++;
    while (t && oid[t - 1] > onode[i]) { oid[t] = oid[t - 1]; oix[t] = oix[t - 1]; t--; }
    oid[t] = onode[i]; oix[t] = (u16)i;
  }
  for (u32 m = 1; m < nS; m++) {
    u16 id = sid[m], ad = sad[m]; u8 ng = sng[m]; u32 t = m;
    while (t && sid[t - 1] > id) { sid[t] = sid[t - 1]; sad[t] = sad[t - 1]; sng[t] = sng[t - 1]; t--; }
    sid[t] = id; sad[t] = ad; sng[t] = ng;
  }
}
static void segment(u32 s) {
  seg = s; nin = s == 1 ? 416 : 256; nO = s == 2 ? 256 : 288; nS = 0; co = cs = 0;
  for (u32 m = 0; m < NMAX; m++) uses[m] = 0;
  pass = 0; trace();
  if (nn > NMAX) { err = 1; return; }
  if (s == 0) info.nodes0 = nn; else if (s == 1) info.nodes1 = nn; else info.nodes2 = nn;
  sortent();
  for (u32 e = 0; e < nE; e++) uses[oid[e]]++;
  pass = 1;
  for (u32 w = 0; w < 32; w++) { fb[w] = 0; pb[w] = 0; }
  for (u32 r = (s == 0 ? 256 : 0); r < 1024; r++) if (s == 0 || r < 256 || r >= 544) release(r);
  for (u32 i = 0; i < nO; i++) { u32 t = tgt(i); pb[t >> 5] |= 1u << (t & 31); }
  for (u32 m = 0; m < 128; m++) lreg[m] = 0;
  while (co < nE && oid[co] <= nin) { oreg[oix[co]] = (u16)fixedreg(oid[co]); co++; }
  while (cs < nS && sid[cs] <= nin) { dostore(fixedreg(sid[cs]), sad[cs], sng[cs]); cs++; }
  if (s == 1) loopat = kk;
  trace();
  for (u32 i = 0; i < nO; i++) if (!onode[i]) emit('S', tgt(i), (s != 2 && oneg[i]) ? 1 : 0, 0);
  for (u32 i = 0; i < nO; i++) if (onode[i] && oreg[i] != tgt(i)) {
    if (s != 2 && oneg[i]) emit('N', tgt(i), oreg[i], 0); else { emit('M', tgt(i), oreg[i], 0); nmov++; }
  }
  for (u32 i = 0; i < nO; i++) if (onode[i] && oreg[i] == tgt(i) && s != 2 && oneg[i]) emit('N', tgt(i), tgt(i), 0);
  if (s == 2) for (u32 i = 0; i < 256; i++) info.q[i >> 3] |= (u8)(oneg[i] << (i & 7));
}
__attribute__((export_name("info_ptr"))) u32 info_ptr(void) { return (u32)(unsigned long)&info; }
__attribute__((export_name("code_ptr"))) u32 code_ptr(void) { return (u32)(unsigned long)code; }
__attribute__((export_name("run"))) int run(void) {
  info.sz_code = sizeof code; info.sz_ctr = sizeof counters; info.sz_uses = sizeof uses;
  info.sz_state = sizeof fb + sizeof pb + sizeof W + sizeof V + 12 * 128 + sizeof oid + sizeof oix + sizeof oreg + sizeof onode + sizeof sid + sizeof sad + sizeof lreg
    + sizeof oneg + sizeof sng + sizeof info + 256;
  err = 0; calls = 0; kk = 0; nmov = 0;
  emit('S', 1023, 0, 0); emit('S', 1022, 1, 0);                                   /* setup records: the 96 constant planes of W'13..W'15 (K + the constant words) */
  for (u32 i = 13; i < 16; i++) { u32 w = K[i] + (i == 13 ? 0x80000000u : i == 15 ? 0x1A0u : 0u); for (u32 j = 0; j < 32; j++) emit('T', (i - 7) * 32 + j, (w >> j) & 1 ? 1022 : 1023, 0); }
  segment(0); info.n0 = kk - NSETUP;
  emit('R', 0, 0, 0); emit('R', 1, 0, 0); emit('R', 2, 8, 0);
  segment(1);
  emit('A', 0, 128, 0); emit('A', 1, 1, 0); emit('C', 1, 2, 0); emit('J', loopat, 0, 0); info.n1 = kk - NSETUP - info.n0 - 3;
  segment(2); info.n2 = kk - NSETUP - info.n0 - info.n1 - 3;
  info.calls = calls; info.ninst = kk; info.err = err; info.moves = nmov;
  { u32 top = 0;
    for (u32 k = 0; k < kk; k++) {
      u32 op = code[k][0], d = code[k][1] | (u32)code[k][2] << 8, a = code[k][3] | (u32)code[k][4] << 8, b = code[k][5] | (u32)code[k][6] << 8, m = 0;
      if (op == '^' || op == '&' || op == '|') { m = d > a ? d : a; m = m > b ? m : b; }
      else if (op == 'N' || op == 'M') m = d > a ? d : a;
      else if (op == 'S' || op == 'L') m = d;
      else if (op == 'T') m = a;
      else continue;
      if (m + 1 > top) top = m + 1;
    }
    info.nreg = top; }
  return (int)err;
}
'''


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--selftest":
        sys.exit(0 if selftest() else 1)
    elif arg == "--ledger":
        lg = ledger()
        print_ledger(lg)
        pr = prog()
        ph, filt, body, code, tmax = machine_constants(pr)
        print("PH", ph, "filter", filt, "body", body, "code bytes", code, "tmax", tmax, "generator calls", pr.calls, "records", pr.instr, "moves", pr.moves)
        s1, s2 = phase_bytes(code, tmax)
        print("memory bytes", s2, "limit", MEM_LIMIT, "setup phase bytes", s1, "peak", max(s1, s2), "fits", max(s1, s2) <= MEM_LIMIT)
        print("other code instructions", other_code(pr), "recovery circuit operations", packed_ops(pr.qwords), "q (hex)", "%064x" % pr.qint)
    elif arg == "--text":
        sys.stdout.write(text())
    elif arg == "--gen-c":
        sys.stdout.write(GEN_C)
    elif arg == "--loss":
        for k, v in loss(plan(256)).items():
            print(k, v)
    else:
        json.dump(serve(json.load(sys.stdin)), sys.stdout)
