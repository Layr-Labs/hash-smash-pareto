"""Birthday collision search on 64-round SHA-256 (sha256-r64, one block): a bit-sliced kernel of 256 lanes with distinguished points.

The message is M(x) = PREFIX || x: a constant 20-byte prefix followed by the 32-byte string x (a 256-bit big-endian integer), 52 bytes in all; FIPS
180-4 padding makes it one block: W0..W4 = the prefix, W5..W12 = x, W13 = 0x80000000, W14 = 0, W15 = 0x1A0 (416 bits).  f(x) is the 256-bit big-endian
integer of the working state after step 63 of the 64 steps from the standard IV, that is the digest minus the IV word by word (digest = IV + f(x)
word-wise, so f(x) = f(y) if and only if the two complete digests are equal); the walk is x -> f(x), so the 8 state words are the next input words
W5..W12.  The prefix makes the constant state after step 4 A1 = A0 = A3 = A4 = 0 and E3 = E4 = 0.  n = 256 is the claim; the organizer experiments run
the same code at reduced n (the low n bits of f).
Kernels.  The main loop is bit-sliced: 256 chain values at once, one 256-bit machine word per bit position of each of the 8 state words (a "plane";
lane l is bit l of every plane); rotations are relabelings, additions ripple through full adders of 5 operations, the round constants are folded at
the bit level, and a plane may be kept complemented (NOT is materialised only when an AND or OR needs it).  The recovery walk (two trails) uses the
packed 7-lane kernel of the accepted 39-round package, run at 64 steps.
Sections: 1 scalar digest, 2 packed straight-line generator (the recovery kernel), 3 sliced plane generator and kernel, 4 planes (transposition,
stage-1 test, lane insertion), 5 plan and ledger, 6 search and recovery, 7 organizer experiments, 8 command line (--selftest --ledger --loss --gencode --dump --stats).
Credit: the search with distinguished points, handlers, recovery walk, packed-lane generator with its allocator and C port, ledger method, success
argument and experiments are those of the accepted sha256 round-39 package (a derivative of 368d1718, which credits the blake3 round-3 entries
0a9640ed, 3356413f, cf8b0e92 (packed lanes), 62cfd777 and e479cbbf); its prefix, walk on the digest minus the IV and CH/MAJ folding are kept.  New
here: the sliced kernel, its generator, allocator and C port, the 256-lane handlers, the machine convention of the ledger and the 256-lane experiments.
"""
import sys
import json
import hashlib
import heapq
from fractions import Fraction
from math import isqrt, log, exp, factorial

M32 = 0xFFFFFFFF
ALL1 = (1 << 256) - 1
ROUNDS = 64
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
K = (0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
     0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
     0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
     0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
     0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
     0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2)
PREFIX = bytes.fromhex("03f777b3eec88896e8ebdb1c1b70c247177c95e3")   # the constant 20-byte prefix (W0..W4; computed in closed form by prefix_words())
PREFIX_WORDS = tuple(int.from_bytes(PREFIX[4 * i:4 * i + 4], "big") for i in range(5))      # message words W0..W4
TAIL = (0x80000000, 0, 0x1A0)                           # message words W13..W15 of a 52-byte message (0x80 pad byte, zero, length 416 bits)
LANES = 256                                             # lanes of the sliced kernel: lane l is bit l of every plane
PL, PITCH = 7, 36                                       # the packed recovery kernel: lane l of a word occupies bits 36 l .. 36 l + 35 (32 data, 4 guard)
REP = sum(1 << (PITCH * i) for i in range(PL))
LIM = 1 << PITCH


# ---------------------------------------------------------------- 1 scalar digest
def _ror(v, k):
    return ((v >> k) | (v << (32 - k))) & M32


def digest_words(w, prefix=PREFIX_WORDS):
    """The 8 digest words of the 64-step compression of the block W0..W4 = prefix, W5..W12 = w, W13..W15 = TAIL (IV, feed-forward); f uses chain_words."""
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


def chain_words(w, prefix=PREFIX_WORDS):
    """The 8 words of f: the working state after step 63, that is the digest minus the IV word by word (a bijection of the digest)."""
    return [(u - v) & M32 for u, v in zip(digest_words(w, prefix), IV)]


def prefix_words():
    """The prefix W0..W4 in closed form (the accepted package's): A0 = A1 = 0, A2 = S0^-1(IV[0]), A3 = A4 = 0 (each W_i fixes A_i); then E4 = A4 + A0 -
    S0(A3) - MAJ(A3, A2, A1) = 0 and E3 = A3 + A_-1 - S0(A2) - MAJ(A2, A1, A0) = 0; W_i follows from E_i = A_{i-4} + E_{i-4} + S1(E_{i-1}) +
    CH(E_{i-1}, E_{i-2}, E_{i-3}) + K_i + W_i.  S0 is GF(2)-linear and invertible (Gauss elimination)."""
    S0 = lambda v: _ror(v, 2) ^ _ror(v, 13) ^ _ror(v, 22)
    S1 = lambda v: _ror(v, 6) ^ _ror(v, 11) ^ _ror(v, 25)
    CH = lambda e, f, g: (e & f) ^ (~e & g & M32)
    MAJ = lambda a, b, c: (a & b) ^ (a & c) ^ (b & c)
    rows = [[(S0(1 << j) >> i) & 1 for j in range(32)] + [(IV[0] >> i) & 1] for i in range(32)]
    for col in range(32):
        piv = next(k for k in range(col, 32) if rows[k][col])
        rows[col], rows[piv] = rows[piv], rows[col]
        for k in range(32):
            if k != col and rows[k][col]:
                rows[k] = [u ^ v for u, v in zip(rows[k], rows[col])]
    a2 = sum(rows[i][32] << i for i in range(32))
    assert S0(a2) == IV[0]
    A = {-1: IV[0], -2: IV[1], -3: IV[2], -4: IV[3], 0: 0, 1: 0, 2: a2, 3: 0, 4: 0}
    E = {-1: IV[4], -2: IV[5], -3: IV[6], -4: IV[7]}
    w = []
    for i in range(5):
        E[i] = (A[i] + A[i - 4] - S0(A[i - 1]) - MAJ(A[i - 1], A[i - 2], A[i - 3])) & M32
        w.append((E[i] - A[i - 4] - E[i - 4] - S1(E[i - 1]) - CH(E[i - 1], E[i - 2], E[i - 3]) - K[i]) & M32)
    assert E[3] == 0 and E[4] == 0
    return tuple(w)


def words_of(x):
    return [(x >> (32 * (7 - i))) & M32 for i in range(8)]


def int_of(w):
    return sum(w[i] << (32 * (7 - i)) for i in range(8))


def f_scalar(x, n=256):
    """f(x): the low n bits of the digest minus the IV (big-endian integer) of the 52-byte message PREFIX || x.  n = 256 is the target."""
    return int_of(chain_words(words_of(x))) & ((1 << n) - 1)


def message(x):
    return PREFIX + x.to_bytes(32, "big")


# ---------------------------------------------------------------- 2 packed straight-line generator (the recovery kernel: the accepted package's, 64 steps)
class PTracer:
    """Straight-line code over 256-bit words holding 7 lanes of 36 bits (32 data, 4 guard).  A value is ('c', k), the same constant in every lane
    (folded, no operation), or ('v', name, bound), bound the largest value a lane can hold.  Every emitted line is one machine operation (add, and, or,
    xor, shl, shr) on registers or on an immediate REP * c (c a 32-bit constant)."""

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
        """Rotation of the 32-bit lane by r: two shifts, two masks, one OR (the guard bits of a need not be clear: they land outside both masks)."""
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


def build_packed():
    """The 64-step compression of the input words i0..i7 = W5..W12 (W0..W4, W13..W15 and the IV are constants), packed, without feed-forward (the outputs
    are the 8 state words after step 63).  CH(e, f, 0) = e & f and MAJ(a, b, 0) = a & b (steps 6 and 7).  Returns (tracer, outputs)."""
    t = PTracer()
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
        ch = t.and_(e, f) if g == ("c", 0) else t.xor(g, t.and_(e, t.xor(f, g)))
        t1 = t.add(h, s1, ch, ("c", K[i]), W[i])
        s0 = t.xor(t.xor(t.ror(a, 2), t.ror(a, 13)), t.ror(a, 22))
        ab = t.xor(a, b)
        mj = t.and_(a, b) if c == ("c", 0) else t.xor(t.and_(ab, bc), b)    # majority; a ^ b of this step is b ^ c of the next
        bc = ab
        t2 = t.add(s0, mj)
        na, ne = t.clean(t.add(t1, t2)), t.clean(t.add(d, t1))
        a, b, c, d, e, f, g, h = na, a, b, c, ne, e, f, g
    out = [t.clean(x) for x in (a, b, c, d, e, f, g, h)]
    return t, out


class Packed:
    """The packed chain step: step(i0..i7) takes the 8 packed input words (lane l holds word i of chain value l) and returns the 8 packed output
    words.  ops = lines = machine operations.  Used by the recovery walk (two lanes) and the selftest."""

    def __init__(self):
        t, out = build_packed()
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

    def _last(self):
        last = {}
        for k, (_, _, a, b) in enumerate(self.lines):
            for v in (a, b):
                if isinstance(v, str):
                    last[v] = k
        return last


def allocate_packed(st):
    """The accepted package's allocator: input and output word j live in register j, temporaries take the lowest free register above 7."""
    last, free, nxt = st._last(), [], 8
    reg = {"i%d" % j: j for j in range(8)}
    outpin = {nm: j for j, nm in enumerate(st.outs)}
    code, top = [], 8
    for k, (nm, op, a, b) in enumerate(st.lines):
        ra = reg[a]
        rb = reg[b] if isinstance(b, str) else ("#", b)
        for v in {a, b}:
            if isinstance(v, str) and v in reg and last.get(v, -1) == k and v not in outpin:
                if reg[v] >= 8:
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
        code.append((nm, op, reg[nm], ra, rb))
    return code, top


def run_packed(code, ws):
    """Execute the allocated packed code on a register file; returns the first 8 registers (the output words)."""
    regs = [0] * (max(c[2] for c in code) + 1)
    regs[:8] = ws
    for (nm, op, d, ra, rb) in code:
        va = regs[ra]
        if isinstance(rb, tuple):
            vb = rb[1] if op in ("<<", ">>") else REP * rb[1]
        else:
            vb = regs[rb]
        regs[d] = (va + vb if op == "+" else va & vb if op == "&" else va | vb if op == "|" else va ^ vb if op == "^" else va >> vb if op == ">>" else va << vb)
    return regs[:8]


_PACKED = []


def packed():
    if not _PACKED:
        _PACKED.append(Packed())
    return _PACKED[0]


def pack_lanes(xs):
    """The 8 packed words for up to 7 chain values (lane l holds xs[l])."""
    return [sum(((x >> (32 * (7 - i))) & M32) << (PITCH * l) for l, x in enumerate(xs)) for i in range(8)]


def lanes_of(ws, count=PL):
    return [sum(((ws[i] >> (PITCH * l)) & M32) << (32 * (7 - i)) for i in range(8)) for l in range(count)]


# ---------------------------------------------------------------- 3 sliced plane generator and kernel
# A plane value is ('c', bit) or ('v', node, neg).  Node ids are positive integers (1..256 the input planes); an emitted line (dst, op, a, b) is one
# machine operation on 256-bit words: '^' '&' '|' on two registers, '~' on one register (NOT).  Constants and complements are never emitted as
# operands: a complemented plane is a flag, materialised by '~' (cached and shared) only when an AND or OR needs it.
C0, C1 = ('c', 0), ('c', 1)


def V(node, neg=False):
    return ('v', node, neg)


def NOT(x):
    return ('c', x[1] ^ 1) if x[0] == 'c' else ('v', x[1], not x[2])


class Tracer:
    def __init__(self):
        self.lines, self.n, self.calls, self.notc = [], 0, 0, {}
        self.tag, self.by_tag = "", {}

    def new_input(self):
        self.n += 1
        return self.n

    def emit(self, op, a, b=None):
        self.n += 1
        self.lines.append((self.n, op, a, b))
        self.by_tag[self.tag] = self.by_tag.get(self.tag, 0) + 1
        return self.n

    def notnode(self, a):
        if a not in self.notc:
            n = self.emit('~', a)
            self.notc[a], self.notc[n] = n, a
        return self.notc[a]

    def xor(self, x, y):
        self.calls += 1
        if x[0] == 'c' and y[0] == 'c':
            return ('c', x[1] ^ y[1])
        if x[0] == 'c':
            x, y = y, x
        if y[0] == 'c':
            return NOT(x) if y[1] else x
        if x[1] == y[1]:
            return ('c', int(x[2] != y[2]))
        return V(self.emit('^', x[1], y[1]), x[2] ^ y[2])

    def and_(self, x, y):
        self.calls += 1
        if x[0] == 'c' and y[0] == 'c':
            return ('c', x[1] & y[1])
        if x[0] == 'c':
            x, y = y, x
        if y[0] == 'c':
            return x if y[1] else C0
        if x[1] == y[1]:
            return x if x[2] == y[2] else C0
        if not x[2] and not y[2]:
            return V(self.emit('&', x[1], y[1]))
        if x[2] and y[2]:
            return V(self.emit('|', x[1], y[1]), True)            # ~p & ~q = ~(p | q)
        if not x[2]:
            x, y = y, x                                            # x is the complemented one: ~p & q
        if x[1] in self.notc or y[1] not in self.notc:
            return V(self.emit('&', self.notnode(x[1]), y[1]))     # NOT(p) & q
        return V(self.emit('|', x[1], self.notnode(y[1])), True)    # ~p & q = ~(p | ~q), reusing a materialised ~q

    def or_(self, x, y):
        self.calls += 1
        if x[0] == 'c' and y[0] == 'c':
            return ('c', x[1] | y[1])
        if x[0] == 'c':
            x, y = y, x
        if y[0] == 'c':
            return C1 if y[1] else x
        if x[1] == y[1]:
            return x if x[2] == y[2] else C1
        if not x[2] and not y[2]:
            return V(self.emit('|', x[1], y[1]))
        if x[2] and y[2]:
            return V(self.emit('&', x[1], y[1]), True)            # ~p | ~q = ~(p & q)
        if not x[2]:
            x, y = y, x
        if x[1] in self.notc or y[1] not in self.notc:
            return V(self.emit('|', self.notnode(x[1]), y[1]))
        return V(self.emit('&', x[1], self.notnode(y[1])), True)

    def xor3(self, x, y, z):
        return self.xor(self.xor(x, y), z)

    def maj(self, x, y, z, xy=None):
        """Majority with constant folding and polarity; for three distinct variables 3 operations (2 when the XOR x ^ y is given as xy)."""
        self.calls += 1
        vs = [v for v in (x, y, z) if v[0] == 'v']
        if len(vs) < 3:
            k = sum(v[1] for v in (x, y, z) if v[0] == 'c')
            if len(vs) == 0:
                return ('c', int(k >= 2))
            if len(vs) == 1:
                return vs[0] if k == 1 else ('c', int(k == 2))
            return self.and_(vs[0], vs[1]) if k == 0 else self.or_(vs[0], vs[1])
        for (u, v, w) in ((x, y, z), (x, z, y), (y, z, x)):
            if u[1] == v[1]:
                return u if u[2] == v[2] else w
        negs = [v for v in (x, y, z) if v[2]]
        poss = [v for v in (x, y, z) if not v[2]]
        if len(negs) == 0:
            a, b, c = x, y, z
            ab = xy if xy is not None else self.xor(a, b)
            return self.xor(a, self.and_(ab, self.xor(a, c)))               # maj = a ^ ((a^b) & (a^c))
        if len(negs) == 1:
            p, (y1, z1) = V(negs[0][1]), poss
            return self.xor(p, self.or_(self.xor(p, y1), self.xor(p, z1)))   # maj(~p,y,z) = p ^ ((p^y) | (p^z))
        if len(negs) == 2:
            p, q, z1 = V(negs[0][1]), V(negs[1][1]), poss[0]
            return NOT(self.xor(z1, self.or_(self.xor(z1, p), self.xor(z1, q))))  # maj(~p,~q,z) = ~(z ^ ((z^p) | (z^q)))
        p, q, r = (V(v[1]) for v in negs)
        return NOT(self.xor(p, self.and_(self.xor(p, q), self.xor(p, r))))   # maj(~p,~q,~r) = ~maj(p,q,r)

    def fa(self, x, y, z):
        """Full adder: (sum, carry).  5 operations for three distinct variables of any polarity, fewer with constants or repeated planes."""
        self.calls += 1
        vs = [v for v in (x, y, z) if v[0] == 'v']
        if len(vs) < 3:
            k = sum(v[1] for v in (x, y, z) if v[0] == 'c')
            if len(vs) == 0:
                return ('c', k & 1), ('c', k >> 1)
            if len(vs) == 1:
                p = vs[0]
                return (p, C0) if k == 0 else (NOT(p), p) if k == 1 else (p, C1)
            p, q = vs
            s = self.xor(p, q)
            return (s, self.and_(p, q)) if k == 0 else (NOT(s), self.or_(p, q))
        for (u, v, w) in ((x, y, z), (x, z, y), (y, z, x)):
            if u[1] == v[1]:
                return self.xor3(u, v, w), (u if u[2] == v[2] else w)
        negs = [v for v in (x, y, z) if v[2]]
        poss = [v for v in (x, y, z) if not v[2]]
        if len(negs) == 0:
            a, b, c = x, y, z
            ab = self.xor(a, b)
            return self.xor(ab, c), self.xor(a, self.and_(ab, self.xor(a, c)))
        if len(negs) == 1:
            p, (y1, z1) = V(negs[0][1]), poss
            u1 = self.xor(p, y1)
            carry = self.xor(p, self.or_(u1, self.xor(p, z1)))
            return NOT(self.xor(u1, z1)), carry
        if len(negs) == 2:
            p, q, z1 = V(negs[0][1]), V(negs[1][1]), poss[0]
            u1 = self.xor(z1, p)
            carry = NOT(self.xor(z1, self.or_(u1, self.xor(z1, q))))
            return self.xor(u1, q), carry
        p, q, r = (V(v[1]) for v in negs)
        pq = self.xor(p, q)
        return NOT(self.xor(pq, r)), NOT(self.xor(p, self.and_(pq, self.xor(p, r))))

    def ch(self, e, f, g):
        """Choice e ? f : g = g ^ (e & (f ^ g)) = f ^ (~e & (f ^ g)); the form whose AND has matching polarities (3 operations)."""
        self.calls += 1
        d = self.xor(f, g)
        if d[0] == 'c':
            return g if d[1] == 0 else self.xor(g, e)
        if e[0] == 'c':
            return f if e[1] else g
        if e[2] == d[2]:
            return self.xor(g, self.and_(e, d))
        return self.xor(f, self.and_(NOT(e), d))


# words = lists of 32 planes, index j = bit j
def cword(c):
    return [('c', (c >> j) & 1) for j in range(32)]


def is_cword(w):
    return all(p[0] == 'c' for p in w)


def cval(w):
    return sum(p[1] << j for j, p in enumerate(w))


def ror_w(w, r):                      # bit j of ror(x, r) is bit (j + r) mod 32 of x: a relabeling, no operation
    return [w[(j + r) % 32] for j in range(32)]


def shr_w(w, k):
    return [w[j + k] if j + k < 32 else C0 for j in range(32)]


def xor_w(t, *ws):
    out = []
    for j in range(32):
        v = ws[0][j]
        for w in ws[1:]:
            v = t.xor(v, w[j])
        out.append(v)
    return out


def CH_w(t, e, f, g):
    return [t.ch(e[j], f[j], g[j]) for j in range(32)]


def MAJ_w(t, a, b, c, ab, bc):
    """Majority per bit from the shared XORs ab = a ^ b and bc = b ^ c: b ^ (ab & bc) when the two have the same polarity (2 operations),
    else a ^ (ab & ac) or c ^ (ac & bc) with ac = ab ^ bc (3 operations); constants and repeated planes go to the symbolic maj."""
    out = []
    for j in range(32):
        x, y, z, p, q = a[j], b[j], c[j], ab[j], bc[j]
        if any(v[0] == 'c' for v in (x, y, z)) or len({x[1], y[1], z[1]}) < 3:
            out.append(t.maj(x, y, z, p))
        elif p[0] == 'c' or q[0] == 'c' or p[2] == q[2]:
            out.append(t.xor(y, t.and_(p, q)))
        else:
            r = t.xor(p, q)                                   # a ^ c, complemented relative to exactly one of p, q
            out.append(t.xor(x, t.and_(p, r)) if p[2] == r[2] else t.xor(z, t.and_(r, q)))
    return out


def add2_w(t, x, y):
    """Ripple-carry addition modulo 2^32 of two words."""
    out, c = [], C0
    for j in range(32):
        if j < 31:
            s, c = t.fa(x[j], y[j], c)
        else:
            s = t.xor3(x[j], y[j], c)
        out.append(s)
    return out


def csa_w(t, x, y, z):
    """3:2 carry-save layer: (sum word, carry word shifted up one bit; the top carry is dropped modulo 2^32)."""
    s, c = [], [C0]
    for j in range(32):
        if j < 31:
            sj, cj = t.fa(x[j], y[j], z[j])
            c.append(cj)
        else:
            sj = t.xor3(x[j], y[j], z[j])
        s.append(sj)
    return s, c


def add_many(t, words):
    """Sum of several words modulo 2^32: the constant words are folded into one at build time and placed last; the variable words are reduced by
    3:2 carry-save layers to two words and then added by one ripple adder."""
    vs = [w for w in words if not is_cword(w)]
    k = sum(cval(w) for w in words if is_cword(w)) & M32
    if not vs:
        return cword(k)
    if k:
        vs = vs + [cword(k)]
    while len(vs) > 2:
        s, c = csa_w(t, vs[0], vs[1], vs[2])
        vs = [s, c] + vs[3:]
    return add2_w(t, vs[0], vs[1]) if len(vs) == 2 else vs[0]


def build_sliced():
    """The 64-step compression of the 8 input words W5..W12 (W0..W4, W13..W15 and the IV are constants) on 256 lanes in planes, without feed-forward.
    Returns (tracer, input node ids [8][32], output values [8][32] (materialised, positive))."""
    t = Tracer()
    inputs = [[t.new_input() for j in range(32)] for i in range(8)]
    W = [cword(w) for w in PREFIX_WORDS] + [[V(n) for n in row] for row in inputs] + [cword(w) for w in TAIL]
    a, b, c, d, e, f, g, h = [cword(w) for w in IV]
    bc = xor_w(t, b, c)
    for i in range(ROUNDS):
        if i >= 16:
            t.tag = "W: sigma0, sigma1"
            s0w = xor_w(t, ror_w(W[i - 15], 7), ror_w(W[i - 15], 18), shr_w(W[i - 15], 3))
            s1w = xor_w(t, ror_w(W[i - 2], 17), ror_w(W[i - 2], 19), shr_w(W[i - 2], 10))
            t.tag = "W: 3 additions"
            W.append(add_many(t, [W[i - 16], s0w, W[i - 7], s1w]))
        t.tag = "Sigma1"
        s1 = xor_w(t, ror_w(e, 6), ror_w(e, 11), ror_w(e, 25))
        t.tag = "Ch"
        ch = CH_w(t, e, f, g)
        t.tag = "T1: h + Sigma1 + Ch + K + W"
        t1 = add_many(t, [h, s1, ch, cword(K[i]), W[i]])
        t.tag = "Sigma0"
        s0 = xor_w(t, ror_w(a, 2), ror_w(a, 13), ror_w(a, 22))
        t.tag = "Maj (with a^b)"
        ab = xor_w(t, a, b)
        mj = MAJ_w(t, a, b, c, ab, bc)
        bc = ab
        t.tag = "new a: T1 + Sigma0 + Maj"
        na = add_many(t, [t1, s0, mj])
        t.tag = "new e: d + T1"
        ne = add_many(t, [d, t1])
        a, b, c, d, e, f, g, h = na, a, b, c, ne, e, f, g
    t.tag = "outputs: NOT of complemented planes"
    outs = []
    for w in (a, b, c, d, e, f, g, h):
        row = []
        for p in w:
            assert p[0] == 'v'
            row.append(V(t.notnode(p[1])) if p[2] else p)      # the next batch reads positive planes: materialise complemented outputs
        outs.append(row)
    return t, inputs, outs


class Kernel:
    """The sliced chain step (100,212 operations plus 12 moves, 256 lanes).  allocate(): the registers (the C port of the generator emits the identical
    allocated list); run_allocated(): that list on a register file (the reference semantics); compiled(): the same list as Python functions, for speed."""

    def __init__(self):
        t, inputs, outs = build_sliced()
        self.lines, self.calls, self.by_tag = t.lines, t.calls, t.by_tag
        self.inputs = inputs
        self.in_ids = [n for row in inputs for n in row]
        self.outs = [[p[1] for p in row] for row in outs]
        self.out_ids = [n for row in self.outs for n in row]
        self.ops = len(self.lines)
        self.by = {}
        for _, op, _, _ in self.lines:
            self.by[op] = self.by.get(op, 0) + 1
        self.code, self.nregs, self.moves = self.allocate()
        self.fns = None

    def _last(self):
        last = {}
        for k, (dst, op, a, b) in enumerate(self.lines):
            last[a] = k
            if b is not None:
                last[b] = k
        return last

    def dead_lines(self):
        """Lines whose result is never used (none: the selftest asserts it, so the generator needs no elimination pass)."""
        last = self._last()
        return sum(1 for dst, _, _, _ in self.lines if dst not in last and dst not in set(self.out_ids))

    def allocate(self):
        """Linear register assignment: input plane k starts in register k; a register is reused once its value is dead (the lowest free register above
        255 first, then the lowest free input register); an output plane takes its own register k when that is free; outputs not in register k at the
        end are moved there ('mov', one operation each, via a free register for a displaced output).  Returns (code (op, dst, a, b), registers, moves)."""
        last = self._last()
        reg = {n: k for k, n in enumerate(self.in_ids)}
        outpin = {n: k for k, n in enumerate(self.out_ids)}
        outs = set(self.out_ids)
        free_hi, free_lo, nxt, top, code = [], [], 256, 256, []
        busy = set(range(256))
        for k, (dst, op, a, b) in enumerate(self.lines):
            ra, rb = reg[a], (None if b is None else reg[b])
            for v in ((a,) if b is None else {a, b}):
                if last.get(v, -1) == k and v not in outs:
                    r = reg[v]
                    busy.discard(r)
                    heapq.heappush(free_lo if r < 256 else free_hi, r)
            if dst in outpin and outpin[dst] not in busy:
                r = outpin[dst]
                free_lo.remove(r)
                heapq.heapify(free_lo)
            elif free_hi:
                r = heapq.heappop(free_hi)
            elif free_lo:
                r = heapq.heappop(free_lo)
            else:
                r = nxt
                nxt += 1
            reg[dst], top = r, max(top, r + 1)
            busy.add(r)
            code.append((op, r, ra, rb))
        where = {reg[n]: n for n in self.out_ids}          # register -> output value
        moves = 0
        for k, n in enumerate(self.out_ids):
            if reg[n] == k:
                continue
            if k in where:                                   # register k holds another output: park it in a free register
                other = where[k]
                spare = next(r for r in range(top) if r not in where)
                code.append(("mov", spare, k, None))
                where[spare], reg[other] = other, spare
                del where[k]
                moves += 1
            code.append(("mov", k, reg[n], None))
            del where[reg[n]]
            where[k], reg[n] = n, k
            moves += 1
        return code, top, moves

    @staticmethod
    def run_allocated(code, planes, nregs):
        regs = list(planes) + [0] * (nregs - 256)
        for op, d, ra, rb in code:
            va = regs[ra]
            regs[d] = (va ^ regs[rb]) if op == '^' else (va & regs[rb]) if op == '&' else (va | regs[rb]) if op == '|' else (va ^ ALL1) if op == '~' else va
        return regs[:256]

    def compiled(self, chunk=12500):
        """The allocated code as Python functions on local variables r0..r865 (one statement per instruction), in chunks; each chunk takes and
        returns the whole register file as a tuple."""
        if self.fns is None:
            names = ",".join("r%d" % i for i in range(self.nregs))
            fns = []
            for s in range(0, len(self.code), chunk):
                src = ["def c(R):", " %s=R" % names]
                for op, d, a, b in self.code[s:s + chunk]:
                    src.append(" r%d=r%d^A" % (d, a) if op == '~' else " r%d=r%d" % (d, a) if op == 'mov' else " r%d=r%d%sr%d" % (d, a, op, b))
                src.append(" return (%s)" % names)
                ns = {"A": ALL1}
                exec(compile("\n".join(src), "<sliced-chunk>", "exec"), ns)
                fns.append(ns["c"])
            self.fns = fns
        return self.fns

    def step(self, flat):
        """One batch on the flat register file (a tuple of nregs words, planes first); returns the next flat file (outputs in registers 0..255)."""
        for f in self.compiled():
            flat = f(flat)
        return flat

    def dump(self):
        """The allocated instruction list as text (one line per instruction: op dst a [b]); sha256 of this text identifies the program."""
        return "".join("%s %d %d%s\n" % (op, d, a, "" if b is None else " %d" % b) for op, d, a, b in self.code)

    def peak_live(self):
        """Largest number of live planes after one operation (inputs live from the start, outputs to the end)."""
        last, outs = self._last(), set(self.out_ids)
        dead_at = {}
        for v, k in last.items():
            if v not in outs:
                dead_at.setdefault(k, []).append(v)
        cur = sum(1 for v in self.in_ids if v in last)
        peak = cur
        for k, (dst, op, a, b) in enumerate(self.lines):
            cur += 1 - len(dead_at.get(k, ())) - (dst not in last and dst not in outs)
            peak = max(peak, cur)
        return peak

    def spill_ops(self, R, copies=3):
        """Loads plus stores per batch with R registers: Belady (farthest next use) on `copies` chained batches, counting the middle one (steady state)."""
        n, OFF = len(self.lines), self.lines[-1][0] + 1
        prog, prev_out = [], None
        for cpy in range(copies):
            ren = {} if prev_out is None else {inp: prev_out[k] for k, inp in enumerate(self.in_ids)}
            m = lambda x, cpy=cpy, ren=ren: ren[x] if x in ren else x + cpy * OFF
            for dst, op, a, b in self.lines:
                prog.append((m(dst), (m(a),) if b is None else (m(a), m(b))))
            prev_out = [o + cpy * OFF for o in self.out_ids]
        uses = {}
        for k, (dst, srcs) in enumerate(prog):
            for s in srcs:
                uses.setdefault(s, []).append(k)
        for o in prev_out:
            uses.setdefault(o, []).append(len(prog) + 1)
        ptr = {}

        def nxt(v, k):
            u = uses.get(v)
            if not u:
                return None
            i = ptr.get(v, 0)
            while i < len(u) and u[i] <= k:
                i += 1
            ptr[v] = i
            return u[i] if i < len(u) else None
        regs, heap, cost = {}, [], 0
        lo, hi = n * (copies // 2), n * (copies // 2 + 1)

        def evict(k, pinned):
            nonlocal cost
            while True:
                negu, v = heapq.heappop(heap)
                if v not in regs or v in pinned:
                    continue
                cur = nxt(v, k)
                if cur is None:
                    del regs[v]
                    return
                if -negu != cur:
                    heapq.heappush(heap, (-cur, v))
                    continue
                if regs[v] and lo <= k < hi:
                    cost += 1                                  # store a dirty value with a future use
                del regs[v]
                return
        for k, (dst, srcs) in enumerate(prog):
            pinned = set(srcs)
            for s in srcs:
                if s not in regs:
                    if len(regs) >= R:
                        evict(k, pinned)
                    if lo <= k < hi:
                        cost += 1                              # load
                    regs[s] = False
                    heapq.heappush(heap, (-k, s))
            for s in set(srcs):
                u = nxt(s, k)
                if u is None:
                    regs.pop(s, None)
                else:
                    heapq.heappush(heap, (-u, s))
            u = nxt(dst, k)
            if u is None:
                continue
            if len(regs) >= R:
                evict(k, set())
            regs[dst] = True
            heapq.heappush(heap, (-u, dst))
        return cost


_KERNEL = []


def kernel():
    if not _KERNEL:
        _KERNEL.append(Kernel())
    return _KERNEL[0]


# ---------------------------------------------------------------- 4 planes: transposition, stage-1 test, lane insertion
# planes[32 i + j] is the 256-bit word holding bit j of state word i (bit 32 (7 - i) + j of the chain value) for the 256 lanes: lane l is bit l.
# KS[p] is the plane of bit position p; at reduced width n only the planes of positions below n are used (the others stay zero).
KS = sorted(range(256), key=lambda k: 32 * (7 - k // 32) + k % 32)


def to_planes(xs, n=256):
    """256 chain values (256-bit integers) -> the 256 planes."""
    assert len(xs) == LANES
    planes = [0] * 256
    for p in range(n):
        planes[KS[p]] = sum(((x >> p) & 1) << l for l, x in enumerate(xs))
    return planes


def from_planes(planes, count=LANES, n=256):
    return [lane_of(planes, l, n) for l in range(count)]


def lane_of(planes, l, n=256):
    """The chain value of lane l: bit l of each plane (a handler extracts only the words it needs: 4 operations per plane)."""
    x = 0
    for p in range(n):
        x |= ((planes[KS[p]] >> l) & 1) << p
    return x


def insert_lanes(planes, starts, n=256):
    """Insert chain values into lanes, starts = [(lane, value)]: per plane, clear those lanes' bits and OR the values' bits in (5 operations per
    plane and value: the handler charge of a finished or cut trail)."""
    keep = ALL1
    for l, x in starts:
        keep ^= 1 << l
    for p in range(n):
        k = KS[p]
        planes[k] = (planes[k] & keep) | sum(((x >> p) & 1) << l for l, x in starts)
    return planes


def stage1(planes, s1=32):
    """Lanes whose s1 low bits (of state word 7) are all zero: the OR of those planes (31 operations for s1 = 32) compared with all-ones (a lane with
    a zero low word has a zero bit in the OR), then a branch.  Returns the list of such lanes (empty for almost every batch at s1 = 32)."""
    acc = 0
    for p in range(s1):
        acc |= planes[KS[p]]
    if acc == ALL1:
        return []
    miss = acc ^ ALL1
    return [l for l in range(LANES) if (miss >> l) & 1]


# ---------------------------------------------------------------- 5 plan and ledger
LAMBDA = Fraction(497, 1000)       # 1 - exp(-LAMBDA) = 0.39165
CUTLOSS = Fraction(15, 100000)     # allowance for cut-trail points, as a fraction of Q
TAIL_AGES = 1e-6                   # probability that the unfinished trails hold more than M * L points
CMAX = 2                           # halt when more than CMAX trails are cut (more is charged as failure)
STAGE1_BITS = 32
# machine charges (proof 3.3); the sliced machine of this entry
LOOP_OPS = 3                       # batch counter increment, compare with the slice limit, branch
FILT_OPS = 33                      # stage-1 test: 31 ORs of the planes of word 7, compare with all-ones, branch
HIT_OPS = 600                      # a stage-1 hit lane: lane number, the words of the window and key, window test, bookkeeping
EVENT_OPS = 3000                   # a finished trail: key, entry, new start inserted in the lane (256 planes), bookkeeping
CUT_OPS = 3000                     # a cut trail: age scan share, new start inserted in the lane, bookkeeping
SLICE_OPS = 1040                   # slice check: 256 ages (load, subtract, compare, branch) and the slice counter
RECOVER_EXTRA = 64                 # per recovery batch beyond the packed kernel (exact test of two lanes and loop 29; call and 8 moves 10)
INSTR_MAIN = 5                     # bytes per main-loop instruction: opcode and three 10-bit register fields, no immediate (4 suffice)
INSTR = 36                         # bytes per instruction elsewhere (recovery kernel, handlers, setup, generators): with a 256-bit immediate
GEN_CODE = 4400                    # instructions of the two runtime generators charged (--gencode counts 4,320 bytecode instructions)
OTHER_CODE = 1600                  # instructions besides the main body and the recovery kernel: handlers, key scan, cut and slice checks, setup
REGISTERS = 1024                   # declared register file of 256-bit words (the sliced line needs 866), counted as memory
REGFILE = REGISTERS * 32
COUNTERS = 28672                   # 256 trail numbers and births, counters, lane arrays (about 6,400), 4,096 stack reserve, 16,384 reserve against OTHER_CODE
ENTRY = 25
MEM_LIMIT = 1 << 20
ADVICE = 0
TAIL_LOG2 = -40
KAPPA_256 = 13                     # age cap c = 13 L (P(3 or more cut trails) about 2e-5; proof 4)
GEN_FACTOR = 400                   # word operations charged per generator call and per emitted line (proof 3.6)
GEN_SCRATCH = 69140                # bytes of scratch of the two runtime generators (the C port's static scratch 46,612 + 22,528; proof 3.6)
SETUP_FIXED = 256 * 1400 + 2000    # 256 starts transposed into the planes, random word, counters
# reduced widths: s1 (low zero bits of a DP), W (window bits), Tp, kappa, Sb (slice length in batches)
CFG = {18: dict(s1=1, W=0, Tp=1, kappa=2, Sb=1), 20: dict(s1=2, W=0, Tp=1, kappa=4, Sb=2),
       24: dict(s1=3, W=0, Tp=1, kappa=6, Sb=4), 30: dict(s1=4, W=0, Tp=1, kappa=8, Sb=8), 40: dict(s1=6, W=4, Tp=1, kappa=12, Sb=64),
       256: dict(s1=32, W=90, kappa=KAPPA_256, Sb=1 << 48)}


def inflight_m(lanes=LANES, eps=TAIL_AGES):
    """Smallest integer M with P(sum of `lanes` exponential ages > M L) <= eps (Chernoff, exact in the exponent)."""
    m = lanes
    while True:
        x = m / lanes
        if exp(-lanes * (x - 1 - log(x))) <= eps:
            return m
        m += 1


INFLIGHT = inflight_m()            # 350 for 256 lanes


def _plan(n, Tp, kappa, tmax, Sb):
    c = CFG[n]
    s1, W = c["s1"], c["W"]
    N, D = 1 << n, s1 + W
    L = Fraction(1 << D, Tp)
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


def machine_constants(R=REGISTERS, instr_main=INSTR_MAIN):
    """(kernel ops, spill ops, body ops, code bytes, tmax) with R registers and instr_main bytes per body instruction.  Belady spill loads and stores
    (R below the 866 live planes) are added to the body; the packed recovery kernel (64 live words) never spills."""
    k, p = kernel(), packed()
    spill = k.spill_ops(R) if R < 866 else 0
    body = k.ops + k.moves + spill + FILT_OPS + LOOP_OPS
    code = body * instr_main + (p.ops + RECOVER_EXTRA + OTHER_CODE) * INSTR
    tmax = (MEM_LIMIT - code - R * 32 - COUNTERS - ADVICE) // ENTRY
    return k.ops, spill, body, code, tmax


def phase_bytes(code, tmax, R=REGISTERS, instr_main=INSTR_MAIN):
    """(setup phase, search phase) resident bytes.  Setup: the code at its final size (the generator writes the 5-byte records in place), counters, the
    generators' image (GEN_CODE instructions) and scratch; the register file is not yet in use.  Search: code, advice, table, register file, counters."""
    return code + ADVICE + COUNTERS + GEN_CODE * INSTR + GEN_SCRATCH, code + ADVICE + COUNTERS + R * 32 + ENTRY * tmax


def plan(n, kappa=None, Tp=None, R=REGISTERS, instr_main=INSTR_MAIN):
    if n != 256:
        c = CFG[n]
        p = _plan(n, c["Tp"], c["kappa"], 0, c["Sb"])
        p["tmax"] = 4 * (p["Q"] // int(p["L"])) + 64
        return p
    kappa = kappa or KAPPA_256
    tmax = machine_constants(R, instr_main)[4]
    if Tp:
        return _plan(256, Tp, kappa, tmax, CFG[256]["Sb"])
    best = None
    for t in range(1, 8193):                              # the largest Tp whose table-capacity tail is within 2^TAIL_LOG2
        p = _plan(256, t, kappa, tmax, CFG[256]["Sb"])
        mean = float(p["Q"] / p["L"])
        if mean < tmax + 1 and tail_log2(mean, tmax + 1) <= TAIL_LOG2:
            best = p
    return best


def ledger(p=None, R=REGISTERS, instr_main=INSTR_MAIN):
    """Operation budget in word operations (exact integers); the unit is the reference count C(sha256-r64) = 4912 operations."""
    k, pk = kernel(), packed()
    p = p or plan(256, None, None, R, instr_main)
    ph, spill, body, code, _ = machine_constants(R, instr_main)
    gen = GEN_FACTOR * (k.calls + k.ops + pk.gen_calls + pk.ops)
    parts = dict(main=body * p["B"],
                 slices=-(-p["B"] // p["Sb"]) * SLICE_OPS,
                 stage1_hits=p["e2max"] * HIT_OPS,
                 events=(p["tmax"] + 1) * (EVENT_OPS + 3 * p["tmax"]),    # tmax stored trails and the one that finds the table full
                 cuts=p["cmax"] * CUT_OPS,
                 recovery=(p["capr"] + 1) * (pk.ops + RECOVER_EXTRA) + 600,    # capr batches of the packed kernel plus the final step of the walk
                 setup=SETUP_FIXED + gen)
    return dict(parts=parts, total=sum(parts.values()), plan=p, body=body, gen=gen, code=code, spill=spill)


def loss(p):
    """The probability losses of proof Section 4 (floats): the terms, their sum and the lower bound on the success probability."""
    N, Q, L = p["N"], p["Q"], p["L"]
    x = float(LAMBDA)
    trails = float(Q / L)
    f1 = float((p["c"] + p["Sb"]) / Q)                        # one cut trail, as a fraction of Q
    mu = trails * exp(-p["kappa"])
    pk = [exp(-mu) * mu ** j / factorial(j) for j in range(p["cmax"] + 1)]
    slope = 2 * x * exp(-x)
    # K = 1..cmax cut trails: the lost points, linearised (H2 c); K > cmax is a halt charged in full as failure (union bound, no independence)
    cut = sum(pk[j] * max(0.0, j * f1 - float(CUTLOSS)) * slope for j in range(1, p["cmax"] + 1)) + (1 - sum(pk))
    t = dict(unfinished=TAIL_AGES, cut_deficit=cut, inside_trail=float(Q * L / N),
             key_false_match=p["tmax"] * (p["tmax"] - 1) / 2 * 2.0 ** -(p["kb"] + log(p["Tp"], 2)),
             table_capacity=2.0 ** tail_log2(trails, p["tmax"] + 1), recovery_no_pair=2.0 ** -100)
    t["sum"] = sum(t.values())
    t["P_lower"] = 1 - exp(-x) - t["sum"]
    t["mean_cut_trails"], t["trails"], t["cut_one_trail"], t["inflight_frac"] = mu, trails, f1, float(p["M"] * L / Q) if "M" in p else float(INFLIGHT * L / Q)
    return t


# ---------------------------------------------------------------- 6 search and recovery
class Halt(Exception):
    pass


class Engine:
    """f (the low n bits) in two forms: step(planes) for the 256 lanes of the sliced kernel; f2(xs) for the recovery (up to 7 values, packed kernel)."""

    def __init__(self, n):
        self.n, self.k, self.pk = n, kernel(), packed()
        self.pad = (0,) * (self.k.nregs - 256)
        self.zero = [KS[p] for p in range(n, 256)]        # planes above bit n are kept at zero
        km = []
        for i in range(8):
            lo = 32 * (7 - i)
            km.append(0 if lo >= n else (M32 if lo + 32 <= n else (1 << (n - lo)) - 1))
        self.km = None if n == 256 else [REP * v for v in km]

    def step(self, planes):
        out = list(self.k.step(tuple(planes) + self.pad)[:256])
        for r in self.zero:
            out[r] = 0
        return out

    def f2(self, xs):
        out = self.pk.step(*pack_lanes(xs))
        if self.km is not None:
            out = [o & m for o, m in zip(out, self.km)]
        return lanes_of(out, len(xs))



class IdealEngine:
    """An ideal function of the same width (keyed blake2b) used as the control of the search experiment."""

    def __init__(self, n, key):
        self.n, self.key, self.nb = n, key, (n + 7) // 8

    def g(self, v):
        h = hashlib.blake2b(v.to_bytes(self.nb, "little"), key=self.key, digest_size=self.nb).digest()
        return int.from_bytes(h, "little") & ((1 << self.n) - 1)

    def step(self, planes):
        return to_planes([self.g(v) for v in from_planes(planes, LANES, self.n)], self.n)

    def f2(self, xs):
        return [self.g(x) for x in xs]


def is_dp(x, p):
    """Distinguished point: low s1 bits zero and the window above them below Tp."""
    return x & ((1 << p["s1"]) - 1) == 0 and (x >> p["s1"]) & ((1 << p["W"]) - 1) < p["Tp"]


def dp_key(x, p):
    """The kb bits above the window, then the fb low bits of the window value (which determine it)."""
    return (((x >> p["D"]) & ((1 << p["kb"]) - 1)) << p["fb"]) | ((x >> p["s1"]) & ((1 << p["fb"]) - 1))


def pack_entry(key, t, length):
    assert key < 1 << 64 and t < 1 << 16 and length < 1 << 120
    return key | (t << 64) | (length << 80)


def unpack_entry(e):
    return e & ((1 << 64) - 1), (e >> 64) & 0xFFFF, e >> 80


def recover(p, r, a, b, f2):
    """a, b = (t, length) of two finished trails with the same end: (x, y), x != y, f(x) = f(y), or None.  The longer trail moves alone for l1 - l2
    steps, then both together (two lanes of the packed kernel)."""
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
    """One attempt with the fresh random word r: the pair (x, y) or None.  Raises Halt at a budget.  Budgets: B batches, e2max stage-1 hits,
    tmax table keys, cmax cut trails, a recovery of at most capr batches, a recovery that finds no pair (at width 256)."""
    n, mask = p["n"], p["N"] - 1
    table, births, ts, nxt = {}, [0] * LANES, list(range(LANES)), LANES
    ws = to_planes([(r + t) & mask for t in ts], n)
    cnt["inserts"] += LANES
    batches = 0
    while batches < p["B"]:
        ws = eng.step(ws)
        batches += 1
        cnt["batches"] += 1
        starts = []                                              # (lane, new start) of this batch's finished and cut trails
        for l in stage1(ws, p["s1"]):
            cnt["stage1_hits"] += 1
            if cnt["stage1_hits"] > p["e2max"]:
                raise Halt("stage-1 budget")
            x = lane_of(ws, l, n)
            if is_dp(x, p):
                key, length = dp_key(x, p), batches - births[l]
                cnt["finished"] += 1
                if key in table:
                    _, t0, l0 = unpack_entry(table[key])
                    cnt["recoveries"] += 1
                    res = recover(p, r, (t0, l0), (ts[l], length), eng.f2)
                    if res is not None:
                        return res
                    if n == 256:
                        raise Halt("recovery found no pair")
                    cnt["robin"] += 1                            # reduced width only: the start of this trail lies on the stored trail; restart the lane
                else:
                    if len(table) >= p["tmax"]:
                        raise Halt("table full")
                    table[key] = pack_entry(key, ts[l], length)
                ts[l], nxt, births[l] = nxt, nxt + 1, batches
                starts.append((l, (r + ts[l]) & mask))
        if batches % p["Sb"] == 0:
            for l in range(LANES):
                if batches - births[l] >= p["c"]:
                    cnt["cut"] += 1
                    if cnt["cut"] > p["cmax"]:
                        raise Halt("cut budget")
                    ts[l], nxt, births[l] = nxt, nxt + 1, batches
                    starts.append((l, (r + ts[l]) & mask))
        if starts:
            ws = insert_lanes(ws, starts, n)
            cnt["inserts"] += len(starts)
    return None


def derive(seed, tag, bits=256):
    return int.from_bytes(hashlib.shake_256(("%s/%s" % (seed, tag)).encode()).digest((bits + 7) // 8), "little") & ((1 << bits) - 1)


def attempt(eng, p, seed, tag):
    from collections import defaultdict
    cnt = defaultdict(int)
    try:
        res = search(eng, p, derive(seed, tag, p["n"]), cnt)
    except Halt:
        cnt["halt"] += 1
        res = None
    return res, cnt


# ---------------------------------------------------------------- 7 organizer experiments
N_T3 = 18                          # width of the search experiment and of the ideal control (plan(18): 5 batches of 256 lanes)
B_T2 = 14                          # projection width of the width-256 experiment (event: low 14 bits of the digest); 256 points = one batch per trial
T2_NAMES = ("w0", "w3", "w7", "xor8", "sum8", "p01", "p23")


def e1_trial(seed, tr, eng, ideal_cls):
    """T3 (target, organizer-checked pair), one attempt; the ideal control on the even trials (observation)."""
    p = plan(N_T3)
    res, cnt = attempt(eng, p, seed, "t")
    obs = dict(target_ok=int(res is not None), target_batches=cnt["batches"], target_finished=cnt["finished"], target_cut=cnt["cut"],
               target_robin=cnt["robin"], target_halt=cnt["halt"], ideal_ok=-1, ideal_halt=-1)
    if tr % 2 == 0:
        ideal = ideal_cls(N_T3, hashlib.blake2b(("%s/ideal" % seed).encode(), digest_size=32).digest())
        res_i, cnt_i = attempt(ideal, p, seed, "i")
        obs["ideal_ok"], obs["ideal_halt"] = int(res_i is not None), cnt_i["halt"]
    if res is None:
        return None, None, obs
    return message(res[0]), message(res[1]), obs


_M = (1 << B_T2) - 1
_F16 = sum(_M << (32 * i) for i in range(8))
_KS = sum(1 << (32 * i) for i in range(8))


def t2_columns(digs):
    """Seven B_T2-bit projections (T2_NAMES) of each value of f: the low bits, the bits at 96 and 224, the xor and the sum of the 8 words, two
    concatenations of two 7-bit pieces."""
    m = _M
    folded = [d ^ (d >> 128) for d in digs]
    folded = [d ^ (d >> 64) for d in folded]
    return [[d & m for d in digs], [(d >> 96) & m for d in digs], [(d >> 224) & m for d in digs],
            [(d ^ (d >> 32)) & m for d in folded],
            [(((d & _F16) * _KS) >> 224) & m for d in digs],
            [((d & 0x7F) | (((d >> 32) & 0x7F) << 7)) & m for d in digs],
            [(((d >> 64) & 0x7F) | (((d >> 107) & 0x7F) << 7)) & m for d in digs]]


def e2_trial(seed, tr):
    """T2: 256 points of the target at width 256 (source by trial index: uniform inputs, counter r + i, or 128 seed-derived starts and their images),
    one batch of the sliced kernel; equal pairs in seven 14-bit projections of f; the first 7 lanes also by the packed recovery kernel (packed_agree).
    w0 (the low 14 bits) is the checked event."""
    eng = Engine(256)
    src = tr % 3
    if src == 0:
        xs = [derive(seed, "u%d" % i) for i in range(LANES)]
    elif src == 1:
        r = derive(seed, "r")
        xs = [(r + i) & ALL1 for i in range(LANES)]
    else:
        half = [derive(seed, "c%d" % l) for l in range(LANES // 2)]
        xs = half + from_planes(eng.step(to_planes(half + half)), LANES // 2)
    digs = from_planes(eng.step(to_planes(xs)))
    obs = {"source": src, "packed_agree": int(eng.f2(xs[:PL]) == digs[:PL])}
    pair = None
    for k, col in enumerate(t2_columns(digs)):
        obs["dup_" + T2_NAMES[k]] = len(col) - len(set(col))
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
    if eid == "sliced-n18":
        eng = Engine(N_T3)
        for t in req["trials"]:
            a, b, obs = e1_trial(t["seed"], t["trial"], eng, IdealEngine)
            out.append({"trial": t["trial"], "message_a_hex": a.hex() if a else None, "message_b_hex": b.hex() if b else None, "observations": obs})
    elif eid == "sliced-k0-w256":
        for t in req["trials"]:
            a, b, obs = e2_trial(t["seed"], t["trial"])
            out.append({"trial": t["trial"], "message_a_hex": a.hex() if a else None, "message_b_hex": b.hex() if b else None, "observations": obs})
    else:
        raise ValueError("unknown experiment")
    return {"schema_version": 1, "trials": out}


# ---------------------------------------------------------------- 8 command line
def selftest():
    import random
    ok = True
    rnd = random.Random(3)
    k, pk = kernel(), packed()
    print("sliced kernel, 64 steps: %d operations %s + %d moves, %d registers; generator calls %d; dead lines %d; peak live %d" % (
        k.ops, k.by, k.moves, k.nregs, k.calls, k.dead_lines(), k.peak_live()))
    ok &= k.dead_lines() == 0 and k.nregs <= REGISTERS
    good = PREFIX_WORDS == prefix_words()
    print("prefix equals prefix_words() (A0 = A1 = A3 = A4 = 0, E3 = E4 = 0 after step 4):", good)
    ok &= good
    tot = 0
    for bt in range(4):
        xs = [rnd.getrandbits(256) for _ in range(LANES)]
        xs[0], xs[1] = 0, ALL1
        pl = to_planes(xs)
        o1 = Kernel.run_allocated(k.code, pl, k.nregs)
        o3 = list(k.step(tuple(pl) + (0,) * (k.nregs - 256))[:256])
        good = o1 == o3 and all(lane_of(o1, l) == f_scalar(xs[l]) for l in range(LANES))
        tot += LANES
        ok &= good
    print("%d lanes (lanes 0, 1 all-zero, all-one), full 256-bit f: allocated code on a register file = compiled = scalar f: %s" % (tot, good))
    for xs in ([0] * LANES, [ALL1] * LANES):
        good = from_planes(Kernel.run_allocated(k.code, to_planes(xs), k.nregs)) == [f_scalar(x) for x in xs]
        print("whole batch of all-zero / all-one inputs:", good)
        ok &= good
    xs = [rnd.getrandbits(256) for _ in range(LANES)]
    pl, cur = to_planes(xs), list(xs)
    e = Engine(256)
    for _ in range(3):
        pl = e.step(pl)
        cur = [f_scalar(x) for x in cur]
    good = from_planes(pl) == cur
    print("3 chained batches (output planes are the next input planes):", good)
    ok &= good
    good = True
    for _ in range(42):
        ys = [rnd.getrandbits(256) for _ in range(PL)]
        good &= lanes_of(pk.step(*pack_lanes(ys))) == [f_scalar(y) for y in ys]
    for ys in ([0] * PL, [ALL1] * PL):
        good &= lanes_of(pk.step(*pack_lanes(ys))) == [f_scalar(y) for y in ys]
    code, regs = allocate_packed(pk)
    good &= run_packed(code, pack_lanes(ys)) == list(pk.step(*pack_lanes(ys)))
    print("packed 64-step kernel (recovery): %d operations %s, %d registers; 308 lanes vs scalar f and the allocated code: %s" % (pk.ops, pk.by, regs, good))
    ok &= good
    xs = [rnd.getrandbits(256) for _ in range(5)]
    good = e.f2(xs) == [f_scalar(x) for x in xs]
    print("recovery form f2 (5 values in one packed evaluation) vs scalar:", good)
    ok &= good
    xs = [rnd.getrandbits(256) | 1 for _ in range(LANES)]
    for l in (3, 77, 200):
        xs[l] = (xs[l] >> 32) << 32
    xs[5] = (xs[5] >> 32) << 32 | (1 << 31)
    pl = to_planes(xs)
    good = stage1(pl) == [3, 77, 200] and lane_of(pl, 77) == xs[77] and from_planes(pl) == xs
    pl = insert_lanes(pl, [(77, xs[0]), (3, xs[1] | 1)])
    good &= lane_of(pl, 77) == xs[0] and stage1(pl) == [200] and lane_of(pl, 78) == xs[78] and lane_of(pl, 3) == (xs[1] | 1)
    print("stage-1 test on planes, lane extraction and insertion:", good)
    ok &= good
    e = Engine(N_T3)
    xs = [rnd.getrandbits(N_T3) for _ in range(LANES)]
    pl = to_planes(xs, N_T3)
    for _ in range(3):
        pl = e.step(pl)
        xs = [f_scalar(x, N_T3) for x in xs]
    good = from_planes(pl, LANES, N_T3) == xs
    print("n=%d chain, 3 steps, 256 lanes:" % N_T3, good)
    ok &= good
    p = plan(N_T3)
    found, cuts, robin = 0, 0, 0
    for s in range(16):
        res, cnt = attempt(e, p, "selftest/%d" % s, "t")
        cuts, robin = cuts + cnt["cut"], robin + cnt["robin"]
        if res is not None:
            found += 1
            ok &= res[0] != res[1] and f_scalar(res[0], N_T3) == f_scalar(res[1], N_T3)
    print("search n=%d (%d batches of 256 lanes per attempt): %d of 16 attempts returned a verified pair; %d cut trails, %d restarts on a start lying on a stored trail" % (N_T3, p["B"], found, cuts, robin))
    ok &= found > 0
    print("selftest", ok)
    return ok


def print_ledger(lg):
    from math import log2
    print({k: (str(v) if isinstance(v, Fraction) else v) for k, v in lg["plan"].items()})
    print("operations per batch (body)", lg["body"], "spill", lg["spill"], "code bytes", lg["code"])
    for k, v in lg["parts"].items():
        print(k, v)
    print("N =", lg["total"])
    print("time_log2 = %.5f (unrounded %.8f)" % (log2(lg["total"] / 4912) + 5e-6, log2(lg["total"] / 4912)))   # rounded up; certificate in the proof


def stats(trials=64):
    """The two experiments on pseudo-random seeds; counts only (descriptive, no inference)."""
    seeds = [hashlib.sha256(("stats/%d" % i).encode()).hexdigest() for i in range(trials)]
    rows = serve({"experiment_id": "sliced-n18", "trials": [{"trial": i, "seed": s} for i, s in enumerate(seeds)]})["trials"]
    tt = sum(r["observations"]["target_ok"] for r in rows)
    ii = sum(max(0, r["observations"]["ideal_ok"]) for r in rows)
    print("T3 n=%d: attempts returning a verified pair: target %d of %d, ideal function %d of %d; cut trails %d, restarts on a stored trail %d" % (
        N_T3, tt, trials, ii, (trials + 1) // 2, sum(r["observations"]["target_cut"] for r in rows), sum(r["observations"]["target_robin"] for r in rows)))
    seedl = [hashlib.sha256(("stats2/%d" % i).encode()).hexdigest() for i in range(trials)]
    r2 = serve({"experiment_id": "sliced-k0-w256", "trials": [{"trial": i, "seed": s} for i, s in enumerate(seedl)]})["trials"]
    lam = LANES * (LANES - 1) / 2 / (1 << B_T2)
    print("T2 width 256: %d points, %d-bit projections, equal pairs per trial if uniform %.4f, trials with a pair if uniform %.4f; packed_agree %d of %d" % (
        LANES, B_T2, lam, 1 - exp(-lam), sum(r["observations"]["packed_agree"] for r in r2), trials))
    for s in range(3):
        sel = [r for r in r2 if r["observations"]["source"] == s]
        line = ["%s %d" % (name, sum(r["observations"]["dup_" + name] for r in sel)) for name in T2_NAMES]
        print("  source %s (%d trials): returned pairs %d (uniform reference %.1f); equal pairs (uniform reference %.1f each): " % (
            ("uniform", "counter", "iterates")[s], len(sel), sum(1 for r in sel if r["message_a_hex"]), (1 - exp(-lam)) * len(sel), lam * len(sel)) + ", ".join(line))
    return rows, r2


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--selftest":
        sys.exit(0 if selftest() else 1)
    elif arg == "--ledger":
        from math import log2
        lg = ledger()
        print_ledger(lg)
        setup, srch = phase_bytes(lg["code"], lg["plan"]["tmax"])
        print("memory bytes: setup phase", setup, "search phase", srch, "limit", MEM_LIMIT, "; generator calls", kernel().calls, "+", packed().gen_calls)
        print("register-file trade-off (Belady loads and stores per batch) and the 4-byte encoding:")
        for R, ib in ((1024, 4), (1024, 5), (768, 5), (512, 5), (256, 5), (128, 5), (64, 5)):
            lgR = ledger(None, R, ib)
            p = lgR["plan"]
            print("  R = %4d, %d B/instr: spill %5d, body %6d, code %6d B, tmax %5d, Tp %3d, L = 2^%.3f, time_log2 %.5f, P_lower %.5f" % (
                R, ib, lgR["spill"], lgR["body"], lgR["code"], p["tmax"], p["Tp"], log2(p["L"]), log2(lgR["total"] / 4912), loss(p)["P_lower"]))
    elif arg == "--loss":
        for k, v in loss(plan(256)).items():
            print(k, v)
    elif arg == "--gencode":
        import dis, types

        def cnt(co):
            return sum(1 for _ in dis.get_instructions(co)) + sum(cnt(x) for x in co.co_consts if isinstance(x, types.CodeType))
        g = globals()
        sl = [v for v in vars(Tracer).values() if callable(v)] + [g[n] for n in "V NOT cword is_cword cval ror_w shr_w xor_w CH_w MAJ_w add2_w csa_w add_many build_sliced".split()] + [Kernel._last, Kernel.allocate]
        pa = [v for v in vars(PTracer).values() if callable(v)] + [build_packed, Packed._last, allocate_packed]
        a, b = sum(cnt(f.__code__) for f in sl), sum(cnt(f.__code__) for f in pa)
        print("bytecode instructions: sliced generator and allocator", a, "packed generator and allocator", b, "total", a + b, "GEN_CODE", GEN_CODE)
    elif arg == "--dump":                      # the sliced list; "--dump packed" the recovery kernel's (compared with the C port, proof 3.6)
        if "packed" in sys.argv:
            sys.stdout.write("".join("%s %d %d %s\n" % (op, d, a, ("#%d" % b[1]) if isinstance(b, tuple) else str(b)) for nm, op, d, a, b in allocate_packed(packed())[0]))
        else:
            sys.stdout.write(kernel().dump())
    elif arg == "--stats":
        stats(int(sys.argv[2]) if len(sys.argv) > 2 else 64)
    else:
        json.dump(serve(json.load(sys.stdin)), sys.stdout)
