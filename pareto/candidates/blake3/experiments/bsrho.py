import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, log, exp, expm1, log1p
gU = 4294967295
IV = (1779033703, 3144134277, 1013904242, 2773480762, 1359893119, 2600822924, 528734635, 1541459225)
gar = 3
gaF = 638
gZ = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
gp = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15), (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
gR, gb = (256, (1 << 256) - 1)
gn = 11
gK = (2147483648, 0, 2147483648, 0, 1879048192, 0, 0, 0)
gM = sum((w << 32 * i for i, w in enumerate(gK)))
gL = b''.join((w.to_bytes(4, 'little') for w in gK))

def gaV(v, k):
    return (v >> k | v << 32 - k) & gU

def gbe(m, pb=gar, pc=gn, pd=64, pe=0):
    v = list(IV) + list(IV[:4]) + [pe & gU, pe >> 32, pd, pc]
    m = list(m)
    for _ in range(pb):
        for j, (a, b, c, d) in enumerate(gp):
            x, y = (m[2 * j], m[2 * j + 1])
            v[a] = v[a] + v[b] + x & gU
            v[d] = gaV(v[d] ^ v[a], 16)
            v[c] = v[c] + v[d] & gU
            v[b] = gaV(v[b] ^ v[c], 12)
            v[a] = v[a] + v[b] + y & gU
            v[d] = gaV(v[d] ^ v[a], 8)
            v[c] = v[c] + v[d] & gU
            v[b] = gaV(v[b] ^ v[c], 7)
        m = [m[i] for i in gZ]
    return [v[i] ^ v[i + 8] for i in range(8)]

def gbi(x, n, pc=gM):
    kw = [pc >> 32 * i & gU for i in range(8)]
    d = gbe(kw + [x >> 32 * i & gU for i in range(8)])
    return sum((d[i] << 32 * i for i in range(8))) & (1 << n) - 1

def gbu(x):
    return gL + x.to_bytes(32, 'little')
gaa, gab = (36, 7)
gaq = sum((1 << gaa * i for i in range(gab)))
gS = 1 << gaa

class gaE:

    def __init__(self):
        self.lines, self.ops, self.k = ([], 0, 0)

    def emit(self, expr):
        self.k += 1
        _0 = 't%d' % self.k
        self.lines.append('%s=%s' % (_0, expr))
        self.ops += 1
        return _0

    def mask(self, a):
        return ('v', self.emit('%s&%d' % (a[1], gaq * gU)), gU)

    def add(self, *xs):
        c = sum((x[1] for x in xs if x[0] == 'c')) & gU
        vs = [x for x in xs if x[0] == 'v']
        if not vs:
            return ('c', c)
        _0 = vs[0]
        for v in vs[1:]:
            while _0[2] + v[2] >= gS:
                if _0[2] >= v[2]:
                    _0 = self.mask(_0)
                else:
                    v = self.mask(v)
            _0 = ('v', self.emit('%s+%s' % (_0[1], v[1])), _0[2] + v[2])
        if c:
            if _0[2] + c >= gS:
                _0 = self.mask(_0)
            _0 = ('v', self.emit('%s+%d' % (_0[1], gaq * c)), _0[2] + c)
        return _0

    def xor(self, a, b):
        if a[0] == 'c' and b[0] == 'c':
            return ('c', a[1] ^ b[1])
        if a[0] == 'c':
            a, b = (b, a)
        if b[0] == 'c':
            if b[1] == 0:
                return a
            return ('v', self.emit('%s^%d' % (a[1], gaq * b[1])), (1 << max(a[2].bit_length(), b[1].bit_length())) - 1)
        return ('v', self.emit('%s^%s' % (a[1], b[1])), (1 << max(a[2].bit_length(), b[2].bit_length())) - 1)

    def ror(self, a, r):
        if a[0] == 'c':
            return ('c', gaV(a[1], r))
        s1 = self.emit('%s>>%d' % (a[1], r))
        h = self.emit('%s&%d' % (s1, gaq * ((1 << 32 - r) - 1)))
        s2 = self.emit('%s<<%d' % (a[1], 32 - r))
        lw = self.emit('%s&%d' % (s2, gaq * ((1 << r) - 1 << 32 - r)))
        return ('v', self.emit('%s|%s' % (h, lw)), gU)

def gbc(qw):
    tr = gaE()
    v = [('c', w) for w in IV] + [('c', w) for w in IV[:4]] + [('c', 0), ('c', 0), ('c', 64), ('c', gn)]
    m = [('c', w) for w in gK] + [('v', 'i%d' % i, gU) for i in range(8, 16)]
    for _ in range(gar):
        for j, (a, b, c, d) in enumerate(gp):
            x, y = (m[2 * j], m[2 * j + 1])
            v[a] = tr.add(v[a], v[b], x)
            v[d] = tr.ror(tr.xor(v[d], v[a]), 16)
            v[c] = tr.add(v[c], v[d])
            v[b] = tr.ror(tr.xor(v[b], v[c]), 12)
            v[a] = tr.add(v[a], v[b], y)
            v[d] = tr.ror(tr.xor(v[d], v[a]), 8)
            v[c] = tr.add(v[c], v[d])
            v[b] = tr.ror(tr.xor(v[b], v[c]), 7)
        m = [m[i] for i in gZ]
    _e = []
    for i in range(8):
        z = tr.xor(tr.xor(v[i], v[i + 8]), ('c', qw[i]))
        if z[2] > gU:
            z = tr.mask(z)
        _e.append(z[1])
    nl = chr(10)
    _f = 'def batch(%s):' % ','.join(('i%d' % i for i in range(8, 16))) + nl
    _f += ''.join(('    %s' % ln + nl for ln in tr.lines)) + '    return (%s,)' % ','.join(_e) + nl
    ns = {}
    exec(_f, {}, ns)
    _7 = set()
    for ln in tr.lines:
        e = ln.split('=', 1)[1]
        for _d in '&^+|':
            if _d in e and e.split(_d)[1].isdigit():
                _7.add((_d, int(e.split(_d)[1])))
    return (ns['batch'], tr.ops, len(_7), tuple(tr.lines), tuple(_e))
gaJ = {}

def gbx(qw):
    qw = tuple(qw)
    if qw not in gaJ:
        gaJ[qw] = gbc(qw)
    return gaJ[qw]

def gby(xs, n, qw):
    _4 = [sum(((x >> 32 * i & gU) << gaa * l for l, x in enumerate(xs))) for i in range(8)]
    _3 = gbx(qw)[0](*_4)
    _2 = (1 << n) - 1
    return [sum(((_3[i] >> gaa * l & gU) << 32 * i for i in range(8))) & _2 for l in range(len(xs))]
gaG, gY = ((0, 0), (0, 1))

class gB:

    def __init__(self, n):
        self.n, self.nodes, self.memo, self.calls, self.hits, self.mkc = (n, [('c',)], {}, 0, 0, 0)
        self.inputs = []
        for j in range(n):
            self.nodes.append(('v', j))
            self.inputs.append((len(self.nodes) - 1, 0))

    def mk(self, op, a, b):
        self.calls += 1
        self.mkc += 1
        if a > b:
            a, b = (b, a)
        k = (op, a, b)
        if k in self.memo:
            self.hits += 1
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
        return (self.mk('x', x[0], y[0]), x[1] ^ y[1])

    def AND(self, x, y):
        self.calls += 1
        if x[0] == 0:
            return gaG if x[1] == 0 else y
        if y[0] == 0:
            return gaG if y[1] == 0 else x
        if x[0] == y[0]:
            return x if x[1] == y[1] else gaG
        if x[1] == 0 and y[1] == 0:
            return (self.mk('a', x[0], y[0]), 0)
        if x[1] == 1 and y[1] == 1:
            return (self.mk('o', x[0], y[0]), 1)
        p, q = (x, y) if x[1] == 0 else (y, x)
        return self.XOR(p, (self.mk('a', p[0], q[0]), 0))

    def fa(self, a, b, c):
        _9 = (a, b, c)
        cs = [t for t in _9 if t[0] == 0]
        vs = [t for t in _9 if t[0] != 0]
        k = 0
        for t in cs:
            k ^= t[1]
        if len(vs) == 3:
            for pi in range(3):
                o = [vs[j] for j in range(3) if j != pi]
                if o[0][1] == o[1][1]:
                    p, x, y = (vs[pi], o[0], o[1])
                    break
            u = self.XOR(x, p)
            return (self.XOR(u, y), self.XOR(self.AND(u, self.XOR(y, p)), p))
        if len(vs) == 2:
            x, y = vs
            t = self.XOR(x, y)
            s = (t[0], t[1] ^ k)
            if x[1] == y[1]:
                if k == 0:
                    return (s, self.AND(x, y))
                cr = self.AND((x[0], x[1] ^ 1), (y[0], y[1] ^ 1))
                return (s, (cr[0], cr[1] ^ 1))
            nt = (t[0], t[1] ^ 1)
            xx = x if x[1] == nt[1] else y
            if k == 0:
                return (s, self.AND(xx, nt))
            yy = x if x[1] == t[1] else y
            cr = self.AND((yy[0], yy[1] ^ 1), (t[0], t[1] ^ 1))
            return (s, (cr[0], cr[1] ^ 1))
        if len(vs) == 1:
            x = vs[0]
            k1, k2 = (cs[0][1], cs[1][1])
            return ((x[0], x[1] ^ k), gY if k1 == k2 == 1 else gaG if k1 == k2 == 0 else x)
        kk = cs[0][1] + cs[1][1] + cs[2][1]
        return (gaG if kk % 2 == 0 else gY, gY if kk >= 2 else gaG)

    def add(self, A, B):
        s, c = ([], gaG)
        for i in range(32):
            if i == 31:
                s.append(self.XOR(self.XOR(A[i], B[i]), c))
            else:
                si, c = self.fa(A[i], B[i], c)
                s.append(si)
        return s

    def col3(self, t, x, y, z, u, U, cy, cu):
        X, A, n = (self.XOR, self.AND, lambda a: (a[0], a[1] ^ 1))
        if t == 0:
            n5 = X(z, U)
            n9 = X(x, n5)
            s = X(y, n9)
            if not cy:
                return (s, None, None)
            n6 = X(x, y)
            n8 = n(A(n(U), n(X(z, u))))
            _5 = A(n(n6), n9)
            return (s, X(n5, _5) if cu else u, X(n8, _5))
        w = X(y, U)
        n8 = X(z, w)
        s = X(x, n8)
        if not cy:
            return (s, None, None)
        n6 = n(A(n(U), n(X(y, u))))
        _4 = X(x, w)
        Uo = X(n6, A(n8, _4))
        return (s, X(n6, w) if cu else u, Uo)

    def col3_m10(self, x, y, z, u, U):
        X, A, n = (self.XOR, self.AND, lambda a: (a[0], a[1] ^ 1))
        O = lambda a, b: n(A(n(a), n(b)))
        x, y, z, u, U = ((a[0], 0) for a in (x, y, z, u, U))
        g5 = X(x, z)
        g6 = X(y, U)
        g7 = X(u, g6)
        g8 = A(U, g7)
        g9 = X(g5, g6)
        _4 = X(x, g6)
        _5 = X(g6, g8)
        _6 = O(g5, _4)
        _7 = X(g8, _6)
        return (n(g9), _5, _7)

    def col3_m10_no_u(self, x, y, z, u, U):
        X, A, n = (self.XOR, self.AND, lambda a: (a[0], a[1] ^ 1))
        O = lambda a, b: n(A(n(a), n(b)))
        x, y, z, u, U = ((a[0], 0) for a in (x, y, z, u, U))
        g5 = X(y, U)
        g6 = X(u, g5)
        g7 = A(U, g6)
        g8 = X(x, g5)
        g9 = X(x, z)
        _4 = X(z, g8)
        _5 = O(g8, g9)
        _6 = X(g7, _5)
        return (n(_4), u, _6)

    def col3_m07(self, x, y, z, u, U):
        X, A, n = (self.XOR, self.AND, lambda a: (a[0], a[1] ^ 1))
        O = lambda a, b: n(A(n(a), n(b)))
        x, y, z, u, U = ((a[0], 0) for a in (x, y, z, u, U))
        g5 = X(x, z)
        g6 = X(y, g5)
        g7 = X(u, g6)
        g8 = X(x, y)
        g9 = O(U, g7)
        _4 = O(g5, g8)
        _5 = X(g6, g9)
        _6 = X(g9, _4)
        _7 = X(U, g6)
        return (n(_7), _5, n(_6))

    def col3_m07_no_u(self, x, y, z, u, U):
        X, A, n = (self.XOR, self.AND, lambda a: (a[0], a[1] ^ 1))
        O = lambda a, b: n(A(n(a), n(b)))
        x, y, z, u, U = ((a[0], 0) for a in (x, y, z, u, U))
        g5 = X(y, z)
        g6 = X(x, g5)
        g7 = X(x, y)
        g8 = O(g5, g7)
        g9 = X(U, g6)
        _4 = X(u, g9)
        _5 = O(U, _4)
        _6 = X(g8, _5)
        return (n(g9), u, n(_6))

    def col3_exact(self, mask, x, y, z, u, U, need_u):
        if mask == 16:
            return self.col3_m10(x, y, z, u, U) if need_u else self.col3_m10_no_u(x, y, z, u, U)
        if mask == 7:
            return self.col3_m07(x, y, z, u, U) if need_u else self.col3_m07_no_u(x, y, z, u, U)
        raise ValueError('unsupported exact-column mask')

    def add3(self, X, Y, Z):
        import itertools
        s0, U = self.fa(X[0], Y[0], Z[0])
        s, u = ([s0], gaG)
        for i in range(1, 32):
            _1 = None
            for p in itertools.permutations((X[i], Y[i], Z[i])):
                for t in (1, 0, 2):
                    n0, h0, k0 = (len(self.nodes), self.hits, self.mkc)
                    _6 = p[0][1] | p[1][1] << 1 | p[2][1] << 2 | (u[1] if u is not None else 0) << 3 | U[1] << 4
                    if t == 2 and _6 not in (7, 16):
                        continue
                    if t == 2:
                        self.col3_exact(_6, *p, u, U, i < 30)
                    else:
                        self.col3(t, *p, u, U, i < 31, i < 30)
                    for k in self.nodes[n0:]:
                        del self.memo[k]
                    del self.nodes[n0:]
                    self.hits = h0
                    if _1 is None or self.mkc - k0 < _1[0]:
                        _1 = (self.mkc - k0, t, p)
            px, py, pz = _1[2]
            _6 = px[1] | py[1] << 1 | pz[1] << 2 | (u[1] if u is not None else 0) << 3 | U[1] << 4
            if _1[1] == 2:
                si, u, U = self.col3_exact(_6, px, py, pz, u, U, i < 30)
            else:
                si, u, U = self.col3(_1[1], px, py, pz, u, U, i < 31, i < 30)
            s.append(si)
        return s

    def xorw(self, A, B):
        return [self.XOR(a, b) for a, b in zip(A, B)]

def gaY(*W):
    return all((any((t[0] != 0 for t in w)) for w in W))

def gaW(A, r):
    return [A[(i + r) % 32] for i in range(32)]

def gaO(v):
    return [gY if v >> i & 1 else gaG for i in range(32)]

def gbQ(n):
    g = gB(n)
    _e = gaO(0)
    m = [gaO(w) for w in gK] + [[g.inputs[32 * i + b] if 32 * i + b < n else gaG for b in range(32)] for i in range(8)]
    v = [gaO(w) for w in IV] + [gaO(w) for w in IV[:4]] + [_e, _e, gaO(64), gaO(gn)]
    for _ in range(gar):
        for j, (a, b, c, d) in enumerate(gp):
            x, y = (m[2 * j], m[2 * j + 1])
            v[a] = g.add3(v[a], v[b], x) if gaY(v[a], v[b], x) else g.add(g.add(v[a], v[b]), x)
            v[d] = gaW(g.xorw(v[d], v[a]), 16)
            v[c] = g.add(v[c], v[d])
            v[b] = gaW(g.xorw(v[b], v[c]), 12)
            v[a] = g.add3(v[a], v[b], y) if gaY(v[a], v[b], y) else g.add(g.add(v[a], v[b]), y)
            v[d] = gaW(g.xorw(v[d], v[a]), 8)
            v[c] = g.add(v[c], v[d])
            v[b] = gaW(g.xorw(v[b], v[c]), 7)
        m = [m[i] for i in gZ]
    return (g, [s for i in range(8) for s in g.xorw(v[i], v[i + 8])])

class gaA:

    def __init__(self, n=256):
        g, _16 = gbQ(n)
        self.n, self.pin, self.gen_calls, self.hits = (n, [0] * n, g.calls, g.hits)
        assert all((_16[j][0] != 0 for j in range(n)))
        self.q = [_16[j][1] for j in range(n)]
        self.qint = sum((b << j for j, b in enumerate(self.q)))
        self.qwords = [self.qint >> 32 * i & gU for i in range(8)]
        _19 = set((_16[j][0] for j in range(n)))
        for k in range(len(g.nodes) - 1, 0, -1):
            if k in _19 and g.nodes[k][0] in 'xao':
                _19.add(g.nodes[k][1])
                _19.add(g.nodes[k][2])
        _15 = [k for k in range(1, len(g.nodes)) if k in _19 and g.nodes[k][0] in 'xao']
        _e, _a, self.lines, self.by, self.opsym = ({0: '0'}, [], [], {}, {})
        for j, (_f, _) in enumerate(g.inputs):
            _e[_f] = 'i%d' % j
        _1b = {'x': '^', 'a': '&', 'o': '|'}
        for k in _15:
            op, a, b = g.nodes[k]
            _e[k] = 't%d' % k
            _a.append('%s=%s%s%s' % (_e[k], _e[a], _1b[op], _e[b]))
            self.lines.append((_e[k], _e[a], _e[b]))
            self.opsym[_e[k]] = (_1b[op], False)
            self.by[op] = self.by.get(op, 0) + 1
        self.gates = len(_15)
        self.dead = len(g.nodes) - 1 - n - len(_15)
        _17 = [_e[_16[j][0]] for j in range(n)]
        self.ops, self.outs = (self.gates, _17)
        nl, K, _b, lu = (chr(10), 2000, ['i%d' % j for j in range(n)], {})
        for k, (_, a, b) in enumerate(self.lines):
            lu[a] = lu[b] = k
        for o in _17:
            lu[o] = len(_a)
        self.fns = []
        for s0 in range(0, len(_a), K):
            e0 = min(s0 + K, len(_a))
            _12 = [v for v in _b + [d for d, _, _ in self.lines[s0:e0]] if lu.get(v, -1) >= e0]
            _1a = 'def c(%s):' % ','.join(_b) + nl + ''.join(('    %s' % ln + nl for ln in _a[s0:e0])) + '    return (%s,)' % ','.join(_17 if e0 == len(_a) else _12) + nl
            ns = {}
            exec(compile(_1a, '<bitslice-step-n%d>' % n, 'exec'), {}, ns)
            self.fns.append(ns['c'])
            _b = _12
        self.step = self._chain

    def _chain(self, *x):
        for f in self.fns:
            x = f(*x)
        return x

    def _last(self):
        _4 = {}
        for k, (_, a, b) in enumerate(self.lines):
            for v in (a, b):
                _4[v] = k
        return _4

    def peak_live(self):
        _4, _7 = (self._last(), set(self.outs))
        _5 = {'i%d' % j for j in range(self.n)}
        _8 = len(_5)
        for k, (nm, a, b) in enumerate(self.lines):
            _5.add(nm)
            _5 = {v for v in _5 if _4.get(v, -1) > k or v == nm or v in _7}
            _8 = max(_8, len(_5))
        return _8

def gaZ(st):
    import heapq
    n, _6, _3, _9 = (st.n, st._last(), [], st.n)
    _d = {'i%d' % j: j for j in range(n)}
    _a = {nm: j for j, nm in enumerate(st.outs)}
    _2, _e = ([], n)
    for k, (nm, a, b) in enumerate(st.lines):
        ra, rb = (_d.get(a, -1), _d.get(b, -1))
        for v in {a, b}:
            if v in _d and _6.get(v, -1) == k and (v not in _a):
                if _d[v] >= n:
                    heapq.heappush(_3, _d[v])
        if nm in _a:
            j = _a[nm]
            if _6.get('i%d' % j, -1) > k:
                raise ValueError('input %d still live when output %d is produced' % (j, j))
            _d[nm] = j
        elif _3:
            _d[nm] = heapq.heappop(_3)
        else:
            _d[nm] = _9
            _9 += 1
        _e = max(_e, _d[nm] + 1)
        _2.append((nm, _d[nm], ra, rb))
    return (_2, _e)

def gbE(st, pb, pc):
    _6 = [0] * (max((c[1] for c in pb)) + 1)
    _6[:st.n] = pc
    for nm, d, ra, rb in pb:
        va = _6[ra] if ra >= 0 else 0
        vb = gb if st.opsym[nm][1] else _6[rb] if rb >= 0 else 0
        o = st.opsym[nm][0]
        _6[d] = va ^ vb if o == '^' else va & vb if o == '&' else va | vb
    return _6[:st.n]

def gaX():
    _2, s = ({}, 128)
    while s:
        m = 0
        for c in range(256):
            if not c & s:
                m |= 1 << c
        _2[s] = m
        s >>= 1
    return _2
gaM = gaX()

def gbR(pa):
    R = list(pa) + [0] * (256 - len(pa))
    s = 128
    while s:
        m = gaM[s]
        for i in range(256):
            if not i & s:
                t = (R[i] >> s ^ R[i + s]) & m
                R[i + s] ^= t
                R[i] ^= t << s
        s >>= 1
    return R

def gbw(xs, n, pc):
    T = gbR(xs)
    return [T[j] ^ (gb if pc[j] else 0) for j in range(n)]

def gbq(pa, n, pc):
    T = gbR([pa[j] ^ (gb if pc[j] else 0) for j in range(n)])
    return T[:256]

def gbp(pa, l, pc, n):
    x = 0
    for j in range(n):
        x |= (pa[j] >> l & 1 ^ pc[j]) << j
    return x

def gbI(pa, l, x, pd, n):
    _0 = 1 << l
    return [pa[j] & ~_0 | (x >> j & 1 ^ pd[j]) << l for j in range(n)]
gQ = Fraction(497, 1000)
gh = Fraction(15, 100000)
gaf = 0.390000001
gA = 10 ** 24
gf = 1
gaz, SC = (32, 12)
gT = 4
gD = 2800
gk = 3800
gaw = 2048
gi = 4200
gav = 4000
KR, gJ = (Fraction(62, 5), 8192)
gai, gaj = (64, 128)
ge, gae, gam = (80, 100, 8000)
gG = 36
gal = 5
gu = 36
go = 4
gay = 0
gq = 2400
gC, gat, gak = (625, 35, 110)
gao = 775
gan = gao * 32
gg = 5248
gaD, gm, gap, gah, gO = (17, 3, 36, 16, 7)
gV = 1048576
gax = 0
ga = 32
gaC = -40
gI = 20
gs = 200
gx = 2400
gr = 256
gw = 2048
gt = 68
gy = 44524
gv = gy + gx + gr + gw + gt
gau = 256 * 3100 + 20000
gN = 64692944896
gad = 1 << 40
gac = 1324508407811000000000000000000000000
gd = {18: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4), 20: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4), 256: dict(s1=32, W=90, kappa=gI, Sb=1 << 48)}

def gaQ(pa, op, d='-', a='-', b='-', pf=gG):
    return (pa, op, str(d), str(a), str(b), pf)

def gaT(pa):
    _3, _2 = pa.split('=', 1)
    for op in ('<<', '>>', '&', '^', '+', '|'):
        if op in _2:
            a, b = _2.split(op, 1)
            return (_3, op, a, int(b) if b.isdigit() else b)
    raise ValueError('bad packed instruction: ' + pa)

def gaS(qw):
    import heapq
    pc = gbx(qw)
    _10 = [gaT(x) for x in pc[3]]
    _4 = sorted({(op, b) for _, op, _, b in _10 if isinstance(b, int) and op in '&^+|'})
    assert len(_10) == pc[1] and len(_4) == pc[2]
    _5 = {x: j for j, x in enumerate(_4)}
    _14 = {'i%d' % j: len(_4) + j - 8 for j in range(8, 16)}
    _a, _f = ({}, set(pc[4]))
    for k, (_, _, a, b) in enumerate(_10):
        _a[a] = k
        if isinstance(b, str):
            _a[b] = k
    for x in _f:
        _a[x] = len(_10)
    _7, _d, _3 = ([], len(_4) + 8, [])
    for k, (_c, op, a, b) in enumerate(_10):
        ra = _14[a]
        rb = _14[b] if isinstance(b, str) else b if op in ('<<', '>>') else _5[op, b]
        for x in {a, b}:
            if isinstance(x, str) and _a[x] == k and (x not in _f):
                heapq.heappush(_7, _14.pop(x))
        d = heapq.heappop(_7) if _7 else _d
        if d == _d:
            _d += 1
        _14[_c] = d
        _3.append(gaQ('P', {'+': 'ADD', '^': 'XOR', '&': 'AND', '|': 'OR', '<<': 'SHL', '>>': 'SHR'}[op], 'r%d' % d, 'r%d' % ra, str(rb) if op in ('<<', '>>') else 'r%d' % rb, gal))
    _b = [gaQ('K', 'LOADI', 'r%d' % _5[x], x[0], hex(x[1])) for x in _4]
    assert _d <= gao
    return (_b, _3, _d, [_14[x] for x in pc[4]])

def gaP(st):
    import re
    _5, _27 = gaZ(st)
    assert _27 == 773
    _7 = gac + 3000
    _1b = 3001
    _b = _7 - (1 << 48) + 1
    _25 = [gaQ('step', {'^': 'XOR', '&': 'AND', '|': 'OR'}[st.opsym[n][0]], 'r%d' % d, 'r%d' % a, 'r%d' % b, go) for n, d, a, b in _5]

    def L(section, name):
        return gaQ(section, 'LABEL', name, pf=0)

    def C(section, rows):
        return [gaQ(section, *x) for x in rows]
    _4 = '%a'
    _24 = [gaQ('stage1', 'AND', _4, 'r0', 'r1', go)]
    _24 += [gaQ('stage1', 'AND', _4, _4, 'r%d' % j, go) for j in range(2, SC)]
    _24 += C('S', [('BRZ', '@d', _4), ('LOAD', '%ae', 'state.passing_left'), ('SUBI', '%ae', '%ae', '1'), ('STORE', 'state.passing_left', '%ae'), ('BRLT', '@W', '%ae')])
    _24 += [gaQ('stage1', 'AND', _4, _4, 'r%d' % j, go) for j in range(SC, gaz)]
    _24 += C('S', [('LOAD', '%e', 'state.left'), ('LOAD', '%af', 'state.next_left'), ('CMP', '%ag', '%e', '%af'), ('BRGT', '@b', '%ag'), ('CALL', '@i')])
    _24 += [L('S', '@b'), gaQ('S', 'BRNZ', '@c', _4)]
    _24 += [L('loop', '@d'), gaQ('loop', 'LOAD', '%e', 'state.left'), gaQ('loop', 'SUBI', '%e', '%e', '1'), gaQ('loop', 'STORE', 'state.left', '%e'), gaQ('loop', 'BRNZ', '@f', '%e'), gaQ('loop', 'HALT', 'batch_limit')]
    _20 = [L('U', '@g')]
    _20 += C('U', [('RANDOM', '%ah'), ('MOVI', '%e', str(_7)), ('MOVI', '%ai', '256'), ('MOVI', '%aj', '0'), ('MOVI', '%ae', '80335778539765998217810134676225009'), ('MOVI', '%ak', '157893706299185752868652343814'), ('MOVI', '%af', str(_b)), ('MOVI', '%al', '0'), ('STORE', 'state.random', '%ah'), ('STORE', 'state.left', '%e'), ('STORE', 'state.next_trail', '%ai'), ('STORE', 'state.table_count', '%aj'), ('STORE', 'state.passing_left', '%ae'), ('STORE', 'state.hit_left', '%ak'), ('STORE', 'state.next_left', '%af'), ('STORE', 'state.cut_count', '%al'), ('MOVI', '%am', '0')])
    _20 += [L('U', '@h')]
    _20 += C('U', [('MOV', '%an', '%am'), ('CALL', '@ao'), ('MOVI', '%ap', str(_7 + 1)), ('CALL', '@o'), ('ADD', '%aq', '%ah', '%am'), ('CALL', '@ar'), ('ADDI', '%am', '%am', '1'), ('CMP', '%ag', '%am', '256'), ('BRLT', '@h', '%ag'), ('BR', '@f')])
    _20 += [L('U', '@i')]
    _20 += C('U', [('CMP', '%ag', '%e', str(_1b)), ('BRLE', '@aa', '%ag'), ('CALL', '@k'), ('LOAD', '%af', 'state.next_left'), ('SUBI', '%af', '%af', str(1 << 48)), ('STORE', 'state.next_left', '%af'), ('CMP', '%ag', '%af', str(_1b)), ('BRGE', '@j', '%ag'), ('MOVI', '%af', str(_1b)), ('STORE', 'state.next_left', '%af'), ('RET',)])
    _20 += [L('U', '@j'), gaQ('U', 'RET'), L('U', '@k')]
    _20 += C('U', [('MOVI', '%am', '0')]) + [L('U', '@as')]
    _20 += C('U', [('CALL', '@at'), ('SUB', '%au', '%ap', '%e'), ('CMP', '%ag', '%au', '53814898614773921979911217015398566'), ('BRLT', '@l', '%ag'), ('LOAD', '%al', 'state.cut_count'), ('ADDI', '%al', '%al', '1'), ('STORE', 'state.cut_count', '%al'), ('CMP', '%ag', '%al', '1'), ('BRGT', '@Z', '%ag'), ('LOAD', '%ai', 'state.next_trail'), ('MOV', '%av', '%ai'), ('ADDI', '%ai', '%ai', '1'), ('STORE', 'state.next_trail', '%ai'), ('MOV', '%an', '%av'), ('CALL', '@ao'), ('MOV', '%ap', '%e'), ('CALL', '@o'), ('LOAD', '%ah', 'state.random'), ('ADD', '%aq', '%ah', '%av'), ('CALL', '@ar')])
    _20 += [L('U', '@l')]
    _20 += C('U', [('ADDI', '%am', '%am', '1'), ('CMP', '%ag', '%am', '256'), ('BRLT', '@as', '%ag'), ('RET',)]) + [L('U', '@ar')]
    _20 += C('U', [('MOV', '%aw', '%aq'), ('MOVI', '%ax', '0'), ('MOVI', '%ay', '1'), ('SHL', '%ay', '%ay', '%am'), ('NOT', '%az', '%ay')])
    _20 += [L('U', '@m')]
    _20 += C('U', [('SHR', '%aA', '%aw', '%ax'), ('ANDI', '%aA', '%aA', '1'), ('SHL', '%aA', '%aA', '%am'), ('LOAD', '%aB', 'R[%ax]'), ('AND', '%aB', '%aB', '%az'), ('OR', '%aB', '%aB', '%aA'), ('STORE', 'R[%ax]', '%aB'), ('ADDI', '%ax', '%ax', '1'), ('CMP', '%ag', '%ax', '256'), ('BRLT', '@m', '%ag'), ('RET',)])
    _20 += [L('U', '@n')]
    _20 += C('U', [('MOV', '%bl', '%am'), ('MOVI', '%bv', 'active_trails'), ('CALL', '@B'), ('RET',)]) + [L('U', '@ao')]
    _20 += C('U', [('MOV', '%bl', '%am'), ('MOVI', '%bv', 'active_trails'), ('CALL', '@C'), ('RET',)]) + [L('U', '@at')]
    _20 += C('U', [('SHR', '%aC', '%am', '1'), ('LOAD', '%aD', 'birth_words[%aC]'), ('ANDI', '%aE', '%am', '1'), ('SHL', '%aF', '%aE', '7'), ('SHR', '%ap', '%aD', '%aF'), ('ANDI', '%ap', '%ap', hex((1 << 128) - 1)), ('RET',)])
    _20 += [L('U', '@o')]
    _20 += C('U', [('SHR', '%aC', '%am', '1'), ('ANDI', '%aE', '%am', '1'), ('SHL', '%aF', '%aE', '7'), ('MOVI', '%aG', hex((1 << 128) - 1)), ('SHL', '%aG', '%aG', '%aF'), ('NOT', '%aH', '%aG'), ('LOAD', '%aD', 'birth_words[%aC]'), ('AND', '%aD', '%aD', '%aH'), ('SHL', '%aI', '%ap', '%aF'), ('OR', '%aD', '%aD', '%aI'), ('STORE', 'birth_words[%aC]', '%aD'), ('RET',)])
    _d = [L('H', '@c')]
    _d += C('H', [('MOVI', '%am', '0')]) + [L('H', '@aJ')]
    _d += C('H', [('SHR', '%aL', _4, '%am'), ('ANDI', '%aL', '%aL', '1'), ('BRZ', '@aO', '%aL'), ('LOAD', '%ak', 'state.hit_left'), ('SUBI', '%ak', '%ak', '1'), ('STORE', 'state.hit_left', '%ak'), ('BRLT', '@X', '%ak'), ('MOVI', '%aM', '0'), ('MOVI', '%ax', '32')]) + [L('H', '@aK')]
    _d += C('H', [('LOAD', '%aB', 'R[%ax]'), ('SHR', '%aL', '%aB', '%am'), ('ANDI', '%aL', '%aL', '1'), ('SHL', '%aL', '%aL', '%ax'), ('OR', '%aM', '%aM', '%aL'), ('ADDI', '%ax', '%ax', '1'), ('CMP', '%ag', '%ax', '122'), ('BRLT', '@aK', '%ag'), ('SHR', '%aN', '%aM', '32'), ('ANDI', '%aN', '%aN', hex((1 << 90) - 1)), ('CMP', '%ag', '%aN', '1976'), ('BRGE', '@aO', '%ag')])
    _d += [L('H', '@p')]
    _d += C('H', [('LOAD', '%aB', 'R[%ax]'), ('SHR', '%aL', '%aB', '%am'), ('ANDI', '%aL', '%aL', '1'), ('SHL', '%aL', '%aL', '%ax'), ('OR', '%aM', '%aM', '%aL'), ('ADDI', '%ax', '%ax', '1'), ('CMP', '%ag', '%ax', '163'), ('BRLT', '@p', '%ag'), ('SHR', '%aP', '%aM', '122'), ('SHL', '%aP', '%aP', '11'), ('ANDI', '%aN', '%aN', '2047'), ('OR', '%aP', '%aP', '%aN'), ('CALL', '@r'), ('BRNZ', '@q', '%aQ'), ('LOAD', '%aj', 'state.table_count'), ('CMP', '%ag', '%aj', '128721'), ('BRGE', '@Y', '%ag'), ('CALL', '@n'), ('MOV', '%aR', '%an'), ('MOV', '%aS', '%aR'), ('CALL', '@aT'), ('ADDI', '%aj', '%aj', '1'), ('STORE', 'state.table_count', '%aj'), ('CMP', '%ag', '%aj', '128721'), ('BRGE', '@Y', '%ag'), ('LOAD', '%ai', 'state.next_trail'), ('MOV', '%av', '%ai'), ('ADDI', '%ai', '%ai', '1'), ('STORE', 'state.next_trail', '%ai'), ('MOV', '%an', '%av'), ('CALL', '@ao'), ('MOV', '%ap', '%e'), ('CALL', '@o'), ('LOAD', '%ah', 'state.random'), ('ADD', '%aq', '%ah', '%av'), ('CALL', '@ar'), ('BR', '@aO')])
    _d += [L('H', '@q')]
    _d += C('H', [('MOV', '%by', '%cm'), ('CALL', '@n'), ('MOV', '%bA', '%an'), ('CALL', '@bw'), ('HALT', 'recovery_returned')]) + [L('H', '@aO')]
    _d += C('H', [('ADDI', '%am', '%am', '1'), ('CMP', '%ag', '%am', '256'), ('BRLT', '@aJ', '%ag'), ('BR', '@d')])
    q = [L('H', '@r')]
    q += C('H', [('ANDI', '%cn', '%aP', hex((1 << 52) - 1)), ('SHR', '%co', '%cn', '36'), ('ANDI', '%cp', '%cn', hex((1 << 36) - 1)), ('MOVI', '%aZ', str(8 * 128722)), ('MOV', '%bl', '%co'), ('CALL', '@ba'), ('SHR', '%aI', '%bb', '36'), ('ANDI', '%aI', '%aI', '1'), ('BRZ', '@aV', '%aI'), ('CALL', '@t'), ('MOV', '%bl', '%bn')]) + [L('H', '@aU')]
    q += C('H', [('SUBI', '%aZ', '%aZ', '1'), ('BRLT', '@ac', '%aZ'), ('CALL', '@ba'), ('ANDI', '%aI', '%bb', hex((1 << 36) - 1)), ('CMP', '%ag', '%aI', '%cp'), ('BREQ', '@aW', '%ag'), ('CALL', '@w'), ('CALL', '@ba'), ('SHR', '%aI', '%bb', '37'), ('ANDI', '%aI', '%aI', '1'), ('BRNZ', '@aU', '%aI')]) + [L('H', '@aV')]
    q += C('H', [('MOVI', '%aQ', '0'), ('RET',)]) + [L('H', '@aW')]
    q += C('H', [('MOVI', '%bv', 'table_trails'), ('CALL', '@B'), ('MOV', '%cm', '%an'), ('MOVI', '%aQ', '1'), ('RET',)]) + [L('H', '@aT')]
    q += C('H', [('ANDI', '%cn', '%aP', hex((1 << 52) - 1)), ('SHR', '%co', '%cn', '36'), ('ANDI', '%cq', '%cn', hex((1 << 36) - 1)), ('MOVI', '%aZ', str(8 * 128722)), ('MOV', '%bl', '%co'), ('CALL', '@ba'), ('SHR', '%cr', '%bb', '36'), ('ANDI', '%cr', '%cr', '1'), ('BRNZ', '@aX', '%cr'), ('ORI', '%bb', '%bb', hex(1 << 36)), ('CALL', '@z'), ('CALL', '@t'), ('MOV', '%bl', '%bn'), ('MOVI', '%bc', '0'), ('BR', '@s')]) + [L('H', '@aX')]
    q += C('H', [('CALL', '@t'), ('MOV', '%bl', '%bn')]) + [L('H', '@aY')]
    q += C('H', [('SUBI', '%aZ', '%aZ', '1'), ('BRLT', '@ac', '%aZ'), ('CALL', '@w'), ('CALL', '@ba'), ('SHR', '%aI', '%bb', '37'), ('ANDI', '%aI', '%aI', '1'), ('BRNZ', '@aY', '%aI'), ('MOVI', '%bc', '1')])
    q += [L('H', '@s')]
    q += C('H', [('MOVI', '%cs', '1'), ('CMP', '%ag', '%bl', '%co'), ('BRNE', '@bd', '%ag'), ('MOVI', '%cs', '0')]) + [L('H', '@bd')]
    q += C('H', [('SUBI', '%aZ', '%aZ', '1'), ('BRLT', '@ac', '%aZ'), ('CALL', '@ba'), ('MOV', '%ct', '%bb'), ('MOVI', '%bv', 'table_trails'), ('CALL', '@B'), ('MOV', '%cu', '%an'), ('SHR', '%cv', '%ct', '37'), ('ANDI', '%cv', '%cv', '1'), ('SHR', '%cw', '%ct', '38'), ('OR', '%cx', '%cv', '%cw'), ('SHR', '%cy', '%ct', '36'), ('ANDI', '%cy', '%cy', '1'), ('CMP', '%ag', '%bl', '%co'), ('BRNE', '@be', '%ag'), ('BRNZ', '@be', '%bc'), ('MOVI', '%cy', '0')]) + [L('H', '@be')]
    q += C('H', [('OR', '%cx', '%cx', '%cy'), ('ANDI', '%cz', '%ct', hex(1 << 36)), ('SHL', '%bb', '%bc', '37'), ('SHL', '%aI', '%cs', '38'), ('OR', '%bb', '%bb', '%aI'), ('OR', '%bb', '%bb', '%cq'), ('OR', '%bb', '%bb', '%cz'), ('CALL', '@z'), ('MOV', '%an', '%aS'), ('MOVI', '%bv', 'table_trails'), ('CALL', '@C'), ('BRZ', '@bf', '%cx'), ('ANDI', '%cq', '%ct', hex((1 << 36) - 1)), ('MOV', '%bc', '%cv'), ('MOVI', '%cs', '1'), ('MOV', '%aS', '%cu'), ('CALL', '@w'), ('BR', '@bd')]) + [L('H', '@bf'), gaQ('H', 'RET')]
    q += [L('H', '@t')]
    q += C('H', [('MOV', '%bm', '%co')]) + [L('H', '@bg')]
    q += C('H', [('SUBI', '%aZ', '%aZ', '1'), ('BRLT', '@ac', '%aZ'), ('MOV', '%bl', '%bm'), ('CALL', '@ba'), ('SHR', '%aI', '%bb', '38'), ('BRZ', '@bh', '%aI'), ('MOV', '%bl', '%bm'), ('CALL', '@x'), ('MOV', '%bm', '%bl'), ('BR', '@bg')]) + [L('H', '@bh')]
    q += C('H', [('MOV', '%bo', '%bm')]) + [L('H', '@bi')]
    q += C('H', [('CMP', '%ag', '%bm', '%co'), ('BREQ', '@v', '%ag'), ('MOV', '%bl', '%bo'), ('CALL', '@w'), ('MOV', '%bo', '%bl')]) + [L('H', '@bj')]
    q += C('H', [('SUBI', '%aZ', '%aZ', '1'), ('BRLT', '@ac', '%aZ'), ('MOV', '%bl', '%bo'), ('CALL', '@ba'), ('SHR', '%aI', '%bb', '37'), ('ANDI', '%aI', '%aI', '1'), ('BRZ', '@bk', '%aI'), ('CALL', '@w'), ('MOV', '%bo', '%bl'), ('BR', '@bj')]) + [L('H', '@bk')]
    q += C('H', [('MOV', '%bl', '%bm'), ('CALL', '@w'), ('MOV', '%bm', '%bl')])
    q += [L('H', '@u')]
    q += C('H', [('SUBI', '%aZ', '%aZ', '1'), ('BRLT', '@ac', '%aZ'), ('MOV', '%bl', '%bm'), ('CALL', '@ba'), ('SHR', '%aI', '%bb', '36'), ('ANDI', '%aI', '%aI', '1'), ('BRNZ', '@bi', '%aI'), ('CALL', '@w'), ('MOV', '%bm', '%bl'), ('BR', '@u')])
    q += [L('H', '@v')]
    q += C('H', [('MOV', '%bn', '%bo'), ('RET',), ('HALT', 'qf_scan_bound')])
    q += [L('H', '@w')]
    q += C('H', [('ADDI', '%bl', '%bl', '1'), ('CMP', '%ag', '%bl', '128722'), ('BRLT', '@bp', '%ag'), ('MOVI', '%bl', '0')]) + [L('H', '@bp'), gaQ('H', 'RET')]
    q += [L('H', '@x')]
    q += C('H', [('BRNZ', '@y', '%bl'), ('MOVI', '%bl', '128721'), ('RET',)])
    q += [L('H', '@y')]
    q += C('H', [('SUBI', '%bl', '%bl', '1'), ('RET',)]) + [L('H', '@ba')]
    q += C('H', [('SHL', '%br', '%bl', '5'), ('SHL', '%aI', '%bl', '2'), ('ADD', '%br', '%br', '%aI'), ('SHL', '%aI', '%bl', '1'), ('ADD', '%br', '%br', '%aI'), ('ADD', '%br', '%br', '%bl'), ('SHR', '%aC', '%br', '8'), ('ANDI', '%aF', '%br', '255'), ('LOAD', '%aD', 'K[%aC]'), ('SHR', '%bb', '%aD', '%aF'), ('CMP', '%ag', '%aF', '217'), ('BRLE', '@bq', '%ag'), ('ADDI', '%aC', '%aC', '1'), ('LOAD', '%cA', 'K[%aC]'), ('SUB', '%cB', '256', '%aF'), ('SHL', '%cA', '%cA', '%cB'), ('OR', '%bb', '%bb', '%cA')]) + [L('H', '@bq')]
    q += C('H', [('ANDI', '%bb', '%bb', hex((1 << 39) - 1)), ('RET',)])
    q += [L('H', '@z')]
    q += C('H', [('SHL', '%br', '%bl', '5'), ('SHL', '%aI', '%bl', '2'), ('ADD', '%br', '%br', '%aI'), ('SHL', '%aI', '%bl', '1'), ('ADD', '%br', '%br', '%aI'), ('ADD', '%br', '%br', '%bl'), ('SHR', '%aC', '%br', '8'), ('ANDI', '%aF', '%br', '255'), ('CMP', '%ag', '%aF', '217'), ('BRGT', '@A', '%ag'), ('MOVI', '%aG', hex((1 << 39) - 1)), ('SHL', '%aG', '%aG', '%aF'), ('NOT', '%aH', '%aG'), ('LOAD', '%aD', 'K[%aC]'), ('AND', '%aD', '%aD', '%aH'), ('SHL', '%aI', '%bb', '%aF'), ('OR', '%aD', '%aD', '%aI'), ('STORE', 'K[%aC]', '%aD'), ('RET',)])
    q += [L('H', '@A')]
    q += C('H', [('SUB', '%bs', '256', '%aF'), ('MOVI', '%aG', '1'), ('SHL', '%aG', '%aG', '%bs'), ('SUBI', '%aG', '%aG', '1'), ('AND', '%aI', '%bb', '%aG'), ('SHL', '%aI', '%aI', '%aF'), ('LOAD', '%aD', 'K[%aC]'), ('MOV', '%aH', '%aG'), ('SHL', '%aH', '%aH', '%aF'), ('NOT', '%aH', '%aH'), ('AND', '%aD', '%aD', '%aH'), ('OR', '%aD', '%aD', '%aI'), ('STORE', 'K[%aC]', '%aD'), ('ADDI', '%aC', '%aC', '1'), ('SHR', '%aI', '%bb', '%bs'), ('SUB', '%bt', '39', '%bs'), ('MOVI', '%aG', '1'), ('SHL', '%aG', '%aG', '%bt'), ('SUBI', '%aG', '%aG', '1'), ('NOT', '%aH', '%aG'), ('LOAD', '%aD', 'K[%aC]'), ('AND', '%aD', '%aD', '%aH'), ('OR', '%aD', '%aD', '%aI'), ('STORE', 'K[%aC]', '%aD'), ('RET',)])
    q += [L('H', '@B')]
    q += C('H', [('SHL', '%br', '%bl', '4'), ('ADD', '%br', '%br', '%bl'), ('SHR', '%aC', '%br', '8'), ('ANDI', '%aF', '%br', '255'), ('LOAD', '%aD', 'm[%bv+%aC]'), ('SHR', '%an', '%aD', '%aF'), ('CMP', '%ag', '%aF', '239'), ('BRLE', '@bu', '%ag'), ('ADDI', '%aC', '%aC', '1'), ('LOAD', '%cA', 'm[%bv+%aC]'), ('SUB', '%cB', '256', '%aF'), ('SHL', '%cA', '%cA', '%cB'), ('OR', '%an', '%an', '%cA')]) + [L('H', '@bu')]
    q += C('H', [('ANDI', '%an', '%an', hex((1 << 17) - 1)), ('RET',)])
    q += [L('H', '@C')]
    q += C('H', [('SHL', '%br', '%bl', '4'), ('ADD', '%br', '%br', '%bl'), ('SHR', '%aC', '%br', '8'), ('ANDI', '%aF', '%br', '255'), ('CMP', '%ag', '%aF', '239'), ('BRGT', '@D', '%ag'), ('MOVI', '%aG', hex((1 << 17) - 1)), ('SHL', '%aG', '%aG', '%aF'), ('NOT', '%aH', '%aG'), ('LOAD', '%aD', 'm[%bv+%aC]'), ('AND', '%aD', '%aD', '%aH'), ('SHL', '%aI', '%an', '%aF'), ('OR', '%aD', '%aD', '%aI'), ('STORE', 'm[%bv+%aC]', '%aD'), ('RET',)])
    q += [L('H', '@D')]
    q += C('H', [('SUB', '%bs', '256', '%aF'), ('MOVI', '%aG', '1'), ('SHL', '%aG', '%aG', '%bs'), ('SUBI', '%aG', '%aG', '1'), ('AND', '%aI', '%an', '%aG'), ('SHL', '%aI', '%aI', '%aF'), ('LOAD', '%aD', 'm[%bv+%aC]'), ('MOV', '%aH', '%aG'), ('SHL', '%aH', '%aH', '%aF'), ('NOT', '%aH', '%aH'), ('AND', '%aD', '%aD', '%aH'), ('OR', '%aD', '%aD', '%aI'), ('STORE', 'm[%bv+%aC]', '%aD'), ('ADDI', '%aC', '%aC', '1'), ('SHR', '%aI', '%an', '%bs'), ('SUB', '%bt', '17', '%bs'), ('MOVI', '%aG', '1'), ('SHL', '%aG', '%aG', '%bt'), ('SUBI', '%aG', '%aG', '1'), ('NOT', '%aH', '%aG'), ('LOAD', '%aD', 'm[%bv+%aC]'), ('AND', '%aD', '%aD', '%aH'), ('OR', '%aD', '%aD', '%aI'), ('STORE', 'm[%bv+%aC]', '%aD'), ('RET',)])
    _d += q
    _12, _16, _19, _18 = gaS(st.qwords)
    assert _19 < gao
    _e = ['r%d' % (len(_12) + j) for j in range(8)]
    _15 = ['r%d' % x for x in _18]
    _22 = [f'%E{j}' for j in range(8)]
    _1e = [L('R', '@bw')] + _12
    _1e += C('R', [('LOAD', '%ah', 'state.random'), ('ADD', '%bx', '%ah', '%by'), ('ADD', '%bz', '%ah', '%bA'), ('MOVI', '%bB', '0'), ('MOVI', '%bC', '-1'), ('MOVI', '%bD', '-1'), ('MOVI', '%bE', '4072904924457987259221796209662'), ('STORE', 'C0[0]', '%bx'), ('STORE', 'C1[0]', '%bz'), ('MOVI', '%bF', '1')])
    _1e += [L('R', '@F')]
    for j, _a in enumerate(_e):
        _1e += C('R', [('SHR', '%cC', '%bx', str(32 * j)), ('ANDI', '%cC', '%cC', hex(gU)), ('SHR', '%cD', '%bz', str(32 * j)), ('ANDI', '%cD', '%cD', hex(gU)), ('SHL', '%cD', '%cD', '36'), ('OR', _a, '%cC', '%cD')])
    _1e += [L('R', '@G')]
    _1e += C('R', [('CMP', '%ag', '%bB', '33365237141159831627544954549547111'), ('BRGE', '@ab', '%ag'), ('CALL', '@bG'), ('ADDI', '%bB', '%bB', '1')])
    for j, _23 in enumerate(_15):
        _1e.append(gaQ('R', 'MOV', _22[j], _23))
    for j, _a in enumerate(_e):
        _1e.append(gaQ('R', 'MOV', _a, _22[j]))
    for _11 in (0, 1):
        sh = str(36 * _11)
        _1e += C('R', [('SHR', '%cE', _22[0], sh), ('ANDI', '%cE', '%cE', hex(gU)), ('XORI', '%cE', '%cE', hex(gU)), ('BRNZ', '@cI%d' % _11, '%cE'), ('SHR', '%cF', _22[1], sh), ('ANDI', '%cF', '%cF', hex(gU)), ('SHR', '%cG', _22[2], sh), ('ANDI', '%cG', '%cG', hex(gU)), ('SHR', '%cH', _22[3], sh), ('ANDI', '%cH', '%cH', hex((1 << 26) - 1)), ('SHL', '%cG', '%cG', '32'), ('SHL', '%cH', '%cH', '64'), ('OR', '%aN', '%cF', '%cG'), ('OR', '%aN', '%aN', '%cH'), ('CMP', '%ag', '%aN', '1976'), ('BRGE', '@cI%d' % _11, '%ag'), ('CMP', '%ag', f'%cM{_11}', '-1'), ('BRNE', '@cI%d' % _11, '%ag'), ('MOV', f'%cM{_11}', '%bB'), ('MOVI', '%aM', '0')])
        for j, _23 in enumerate(_22):
            _1e += C('R', [('SHR', '%cL', _23, sh), ('ANDI', '%cL', '%cL', hex(gU)), ('SHL', '%cL', '%cL', str(32 * j)), ('OR', '%aM', '%aM', '%cL')])
        _1e += C('R', [('MOV', f'%cN{_11}', '%aM')])
        _1e += [L('R', '@cI%d' % _11)]
    _1e += C('R', [('SUBI', '%bE', '%bE', '1'), ('BRNZ', '@H', '%bE'), ('MOVI', '%bE', '4072904924457987259221796209662')])
    for _11 in (0, 1):
        _1e += C('R', [('MOVI', '%aM', '0')])
        for j, _23 in enumerate(_22):
            _1e += C('R', [('SHR', '%cL', _23, str(36 * _11)), ('ANDI', '%cL', '%cL', hex(gU)), ('SHL', '%cL', '%cL', str(32 * j)), ('OR', '%aM', '%aM', '%cL')])
        _1e.append(gaQ('R', 'STORE', 'C%d[%%bF]' % _11, '%aM'))
    _1e += C('R', [('ADDI', '%bF', '%bF', '1')])
    _1e += [L('R', '@H')]
    _1e += C('R', [('CMP', '%ag', '%bC', '-1'), ('BREQ', '@G', '%ag'), ('CMP', '%ag', '%bD', '-1'), ('BREQ', '@G', '%ag'), ('CMP', '%ag', '%cJ', '%cK'), ('BRNE', '@ad', '%ag'), ('SUB', '%bK', '%bC', '%bD'), ('MOVI', '%bQ', '0'), ('BRGE', '@bH', '%bK'), ('SUB', '%bK', '%bD', '%bC'), ('MOVI', '%bQ', '1')]) + [L('R', '@bH')]
    _1e += C('R', [('MOVI', '%bS', 'C0'), ('MOVI', '%bU', 'C1'), ('BRZ', '@bI', '%bQ'), ('MOVI', '%bS', 'C1'), ('MOVI', '%bU', 'C0')]) + [L('R', '@bI')]
    _1e += C('R', [('MOV', '%bJ', '%bK'), ('CALL', '@O'), ('MOV', '%bL', '%bM'), ('MOV', '%bN', '%bO'), ('MOV', '%bP', '%bD'), ('BRZ', '@I', '%bQ'), ('MOV', '%bP', '%bC')])
    _1e += [L('R', '@I')]
    _1e += C('R', [('LOAD', '%bR', 'm[%bS+%bL]'), ('LOAD', '%bT', 'm[%bU]'), ('MOV', '%bV', '%bN'), ('CALL', '@Q'), ('CMP', '%ag', '%bR', '%bT'), ('BREQ', '@ad', '%ag')])
    _1e += C('R', [('MOV', '%bJ', '%bP'), ('CALL', '@O'), ('MOVI', '%bW', '0'), ('ADDI', '%K', '%bM', '1')]) + [L('R', '@M')]
    _1e += C('R', [('SUB', '%aI', '%K', '%bW'), ('CMP', '%ag', '%aI', '1'), ('BRLE', '@N', '%ag'), ('ADD', '%L', '%K', '%bW'), ('SHR', '%L', '%L', '1'), ('ADD', '%bX', '%L', '%bL'), ('LOAD', '%bY', 'm[%bS+%bX]'), ('LOAD', '%bZ', 'm[%bU+%L]'), ('MOV', '%bR', '%bY'), ('MOV', '%bV', '%bN'), ('CALL', '@Q'), ('CMP', '%ag', '%bR', '%bZ'), ('BREQ', '@J', '%ag'), ('MOV', '%bW', '%L'), ('BR', '@M')])
    _1e += [L('R', '@J'), gaQ('R', 'MOV', '%K', '%L'), gaQ('R', 'BR', '@M'), L('R', '@N')]
    _1e += C('R', [('ADD', '%bX', '%bW', '%bL'), ('LOAD', '%bR', 'm[%bS+%bX]'), ('LOAD', '%bT', 'm[%bU+%bW]'), ('MOV', '%bV', '%bN'), ('CALL', '@Q'), ('MOV', '%ca', '4072904924457987259221796209662'), ('CALL', '@cb'), ('RET',)])
    _1e += [L('R', '@O')]
    _1e += C('R', [('MOVI', '%bM', '0'), ('MOVI', '%bO', '0'), ('MOVI', '%cd', '255')]) + [L('R', '@cc')]
    _1e += C('R', [('SHL', '%bO', '%bO', '1'), ('SHR', '%aL', '%bJ', '%cd'), ('ANDI', '%aL', '%aL', '1'), ('OR', '%bO', '%bO', '%aL'), ('CMP', '%ag', '%bO', '4072904924457987259221796209662'), ('BRLT', '@P', '%ag'), ('SUB', '%bO', '%bO', '4072904924457987259221796209662'), ('MOVI', '%aL', '1'), ('SHL', '%aL', '%aL', '%cd'), ('OR', '%bM', '%bM', '%aL')])
    _1e += [L('R', '@P')]
    _1e += C('R', [('SUBI', '%cd', '%cd', '1'), ('BRGE', '@cc', '%cd'), ('RET',)])
    _1e += [L('R', '@Q')]
    _1e += C('R', [('CALL', '@T')]) + [L('R', '@ce')]
    _1e += C('R', [('BRZ', '@R', '%bV'), ('CALL', '@bG')])
    for j, _23 in enumerate(_15):
        _1e.append(gaQ('R', 'MOV', _22[j], _23))
    for j, _a in enumerate(_e):
        _1e.append(gaQ('R', 'MOV', _a, _22[j]))
    _1e += C('R', [('SUBI', '%bV', '%bV', '1'), ('BR', '@ce')])
    _1e += [L('R', '@R'), gaQ('R', 'CALL', '@S'), gaQ('R', 'RET'), L('R', '@T')]
    for j, _a in enumerate(_e):
        _1e += C('R', [('SHR', '%cL', '%bR', str(32 * j)), ('ANDI', _a, '%cL', hex(gU))])
    _1e += C('R', [('RET',)]) + [L('R', '@S')]
    _1e += C('R', [('MOVI', '%bR', '0')])
    for j, _23 in enumerate(_e):
        _1e += C('R', [('ANDI', '%cL', _23, hex(gU)), ('SHL', '%cL', '%cL', str(32 * j)), ('OR', '%bR', '%bR', '%cL')])
    _1e += C('R', [('RET',)]) + [L('R', '@cb')]
    _1e += C('R', [('CALL', '@V')]) + [L('R', '@cf')]
    _1e += C('R', [('BRZ', '@ab', '%ca'), ('MOV', '%cg', '%bR'), ('MOV', '%ch', '%bT'), ('CALL', '@bG'), ('MOVI', '%ci', '0')])
    for j, _23 in enumerate(_15):
        _1e.append(gaQ('R', 'MOV', _22[j], _23))
    for _23 in _22:
        _1e += C('R', [('ANDI', '%cC', _23, hex(gU)), ('SHR', '%cD', _23, '36'), ('ANDI', '%cD', '%cD', hex(gU)), ('XOR', '%aI', '%cC', '%cD'), ('OR', '%ci', '%ci', '%aI')])
    _1e += C('R', [('BRZ', '@U', '%ci')])
    for j, _a in enumerate(_e):
        _1e.append(gaQ('R', 'MOV', _a, _22[j]))
    _1e += C('R', [('CALL', '@cj')])
    _1e += C('R', [('SUBI', '%ca', '%ca', '1'), ('BR', '@cf')])
    _1e += [L('R', '@U')]
    _1e += C('R', [('CMP', '%ag', '%cg', '%ch'), ('BREQ', '@ad', '%ag'), ('MOV', '%ck', '%cg'), ('MOV', '%cl', '%ch'), ('RET',)])
    _1e += [L('R', '@V')]
    for j, _a in enumerate(_e):
        _1e += C('R', [('SHR', '%cC', '%bR', str(32 * j)), ('ANDI', '%cC', '%cC', hex(gU)), ('SHR', '%cD', '%bT', str(32 * j)), ('ANDI', '%cD', '%cD', hex(gU)), ('SHL', '%cD', '%cD', '36'), ('OR', _a, '%cC', '%cD')])
    _1e += C('R', [('RET',)]) + [L('R', '@cj')]
    _1e += C('R', [('MOVI', '%bR', '0'), ('MOVI', '%bT', '0')])
    for j, _23 in enumerate(_e):
        _1e += C('R', [('ANDI', '%cC', _23, hex(gU)), ('SHR', '%cD', _23, '36'), ('ANDI', '%cD', '%cD', hex(gU)), ('SHL', '%cC', '%cC', str(32 * j)), ('SHL', '%cD', '%cD', str(32 * j)), ('OR', '%bR', '%bR', '%cC'), ('OR', '%bT', '%bT', '%cD')])
    _1e += C('R', [('RET',)])
    _17 = [L('P', '@bG')] + _16 + [gaQ('R', 'RET')]
    _c = []
    for _26, _14 in (('@W', 'passing'), ('@X', 'hits'), ('@Y', 'full'), ('@Z', 'cut'), ('@aa', 'limit'), ('@ab', 'recovery'), ('@ac', 'qf'), ('@ad', 'alias')):
        _c += [L('halt', _26), gaQ('halt', 'HALT', _14)]
    _1d = _20 + [L('loop', '@f')] + _25 + _24 + _d + _1e + _17 + _c
    _8 = sum((x[5] == gG for x in _1d))
    assert _8 <= 1335
    _1d += [gaQ('Z', 'NOP') for _ in range(1335 - _8)]
    _10, pc = ({}, 0)
    for x in _1d:
        if x[1] == 'LABEL':
            _10[x[2]] = pc
        else:
            pc += 1
    _28 = {}

    def _1f(s):

        def vr(m):
            _0 = m.group(0)
            if _0 not in _28:
                _28[_0] = 'r%d' % (256 + len(_28))
            return _28[_0]
        s = re.sub('%[A-Za-z0-9_]+', vr, s)
        return str(_10[s]) if s in _10 else s
    _1d = [tuple([x[0], x[1]] + [_1f(y) for y in x[2:5]] + [x[5]]) for x in _1d if x[1] != 'LABEL']
    assert 256 + len(_28) <= gao
    assert sum((x[0] in ('step', 'stage1') for x in _1d)) == st.ops + 31
    assert sum((x[0] == 'P' for x in _1d)) == gbx(st.qwords)[1]
    assert sum((x[5] == gG for x in _1d)) == 1335
    return _1d
gaK = {}

def gbC(st=None):
    st = st or gbL()
    _2 = tuple(st.qwords)
    if _2 not in gaK:
        _5 = gaP(st)
        for _4 in _5:
            for x in _4[2:5]:
                if x.startswith('r') and x[1:].isdigit():
                    assert int(x[1:]) < gao
        _3 = ''.join(('%05d|%s|%s|%s|%s|%s|%d\n' % ((j,) + x) for j, x in enumerate(_5)))
        by = {}
        for x in _5:
            by[x[0]] = by.get(x[0], 0) + 1
        gaK[_2] = dict(records=_5, listing=_3, sha256=hashlib.sha256(_3.encode()).hexdigest(), bytes=sum((x[5] for x in _5)), bitwise=sum((x[0] in ('step', 'stage1') for x in _5)), packed=sum((x[0] == 'P' for x in _5)), control=sum((x[5] == gG for x in _5)), sections=by)
    return gaK[_2]

def gbb(pa=None):
    pa = pa or gbC()
    _a = [(_9, _f) for _9, _f in enumerate(pa['records']) if _f[0] == 'loop']
    assert [_f[1] for _, _f in _a] == ['LOAD', 'SUBI', 'STORE', 'BRNZ', 'HALT']
    assert [_9 for _9, _ in _a] == list(range(_a[0][0], _a[0][0] + 5))
    (_, _e), (_, _12), (_, _11), (_6, _5), (_, _8) = _a
    _d = _e[2]
    assert _e[3] == 'state.left'
    assert _12[2:5] == (_d, _d, '1')
    assert _11[2:4] == ('state.left', _d)
    assert _5[3] == _d and int(_5[2]) < _6
    assert _8[2] == 'batch_limit'
    assert not any((_f[1] == 'BR' and _f[2] == _5[2] and (int(_f[2]) < _9) for _9, _f in enumerate(pa['records'])))
    assert any((_f[1] == 'MOVI' and _f[2] == _d and (_f[3] == str(gac + 3000)) for _f in pa['records']))
    _10 = [(_f, pa['records'][_9 + 1]) for _9, _f in enumerate(pa['records'][:-1]) if _f[1] == 'MOV' and _f[3] == _d and (pa['records'][_9 + 1][1] == 'CALL')]
    assert len(_10) == 2
    _2 = _10[0][0][2]
    _3 = _10[0][1][2]
    assert all((_f[2] == _2 and _7[2] == _3 for _f, _7 in _10))
    _b = [(_f, pa['records'][_9 + 1]) for _9, _f in enumerate(pa['records'][:-1]) if _f[1] == 'MOVI' and _f[2] == _2 and (_f[3] == str(gac + 3001)) and (pa['records'][_9 + 1][1:3] == ('CALL', _3))]
    assert len(_b) == 1
    _13 = 3
    for _1 in range(1, _13 + 1):
        _c = _13 - _1 + 1
        assert _13 + 1 - _c == _1
        for _4 in range(1, _1 + 1):
            assert _13 - _4 + 1 - _c == _1 - _4
    _c = 3
    _14 = 0
    while _c:
        _c -= 1
        _14 += 1
        if _c:
            assert _5[1] == 'BRNZ'
        else:
            assert _8[1:3] == ('HALT', 'batch_limit')
    assert _14 == 3
    return True

def gbK(pa, s1):
    assert not any(pa[:s1])
    k = min(SC, s1)
    return (k, s1 - k + 9)

def gbJ(pa, p, pc):
    k, _0 = (min(SC, p['s1']), gb)
    for j in range(k):
        _0 &= pa[j]
    if _0 == 0:
        return 0
    pc['passing'] += 1
    if pc['passing'] > p['pmax']:
        raise gE('stage-1 checkpoint budget')
    for j in range(k, p['s1']):
        _0 &= pa[j]
    return _0
gF = 350

def gbN(pa):
    return 32 * ((39 * pa + 255) // 256) + 32 * ((gaD * pa + 255) // 256)

def gbO(pa):
    lo, hi = (0, pa // gO)
    while lo < hi:
        _2 = (lo + hi + 1) // 2
        if gbN(_2 + 1) <= pa:
            lo = _2
        else:
            hi = _2 - 1
    return lo

def gaU(n, Tp, pc, pd, Sb):
    c = gd[n]
    s1, W = (c['s1'], c['W'])
    N, D = (1 << n, s1 + W)
    L = Fraction(1 << D, Tp)
    if n == 256:
        assert gR + pd + gf < 1 << gaD
        assert gJ * 64 <= gbN(pd + 1)
        B = gaN(Tp, pd, pc, Sb)
    else:
        _e = isqrt(2 * N * gQ.numerator // gQ.denominator) + 2
        _a, _8 = (_e + gF * L + 1, gh.denominator)
        q = -(-(_a * _8) // (_8 - gh.numerator))
        B = -(-q // gR)
    cc = -(-pc * L.numerator // L.denominator)
    fb = (Tp - 1).bit_length()
    pk = 1 - Fraction((1 << SC) - 1, 1 << SC) ** gR
    _5 = n == 256
    return dict(n=n, s1=s1, W=W, D=D, Tp=Tp, fb=fb, kb=min(52 - fb, n - D), L=L, N=N, Q=B * gR, B=B, kappa=pc, Sb=Sb, c=cc, cr=-(-(KR * L.numerator) // L.denominator) if _5 else cc + Sb, tmax=pd, e2max=2 * B * gR // (1 << s1) + 64, pmax=-(-(1025 * B * pk.numerator) // (1024 * pk.denominator)) + 64 if _5 else 10 ** 9, cmax=gf if _5 else 10 ** 9)

def gbP(pa, k):
    return (-pa + k * (1 + log(pa / k))) / log(2)
gaL = {}

def gbL():
    if 256 not in gaL:
        gaL[256] = gaA(256)
    return gaL[256]

def gbv(st=None):
    return 1335

def gbt(st=None, R=gao):
    st = st or gbL()
    ph = st.ops
    _4, _6 = gbK(st.pin, gaz)
    _0 = ph + (st.spill_ops(R) if R < gao else 0) + _4 + gT
    pc = gbx(st.qwords)
    _2 = (ph + gaz - 1) * go + pc[1] * gal + gbv(st) * gG
    if R == gao:
        _1 = gbC(st)['bytes']
        assert _1 == _2
    else:
        _1 = _2
    _7 = gbO(gV - gax - _1 - R * 32 - gg - ga)
    return (ph, _4, _6, _0, _1, _7)

def gbl(pa=None):
    pa = pa or len(gbQ(256)[0].nodes)
    assert pa < 1 << 16
    _0 = pa + 1
    return (_0 + gx + gr + gw + gt, _0, pa)

def gbz(pa, pb):
    _0 = gbl()[0]
    assert _0 <= gv == 49296
    return (pa + ga + gg + gq * gu + gv, pa + ga + gg + gan + gbN(pb + 1))

def gbA(n, pb=None, Tp=None, R=gao):
    if n != 256:
        c = gd[n]
        p = gaU(n, c['Tp'], c['kappa'], 0, c['Sb'])
        p['tmax'] = 4 * (p['Q'] // int(p['L'])) + 64
        return p
    pb = pb or gI
    _9 = gbt(None, R)[5]
    if gR + _9 + gf >= 1 << gaD:
        return None
    if Tp:
        return gaU(256, Tp, pb, _9, gd[256]['Sb'])
    if _9 < 1:
        return None
    lo, hi = (1.0, float(_9 + 1))
    for _ in range(60):
        _6 = (lo + hi) / 2
        lo, hi = (_6, hi) if gbP(_6, _9 + 1) <= gaC else (lo, _6)
    ok = lambda t: gaR(t, lo, _9, pb, gd[256]['Sb'])['P_lower'] >= gaf
    a, b = (1000, 4095)
    if not ok(a):
        return None
    while b - a > 1:
        _6 = (a + b) // 2
        if ok(_6):
            a = _6
        else:
            b = _6
    return gaU(256, a, pb, _9, gd[256]['Sb'])

def gaR(Tp, q, pc, pd, Sb, pf=1.0, pg=20000, ph=2000):
    L = Fraction(1 << 122, Tp)
    c = -(-pd * L.numerator // L.denominator)
    th, Lf, cf, kr = (Tp / 2.0 ** 122, float(L), float(c), float(KR) * float(L))
    Q, B, Np = (q * Lf, q * Lf / gR, 2.0 ** 256 / pf)
    k = int(q) + 1
    while gbP(q, k) > -40:
        k += 1
    n2, _16 = (k + gR + 1, 1 / (1 - k * Q / Np))
    pi = lambda m: exp(-m * (m - 1) / (2 * Np))
    _17 = max(1.0, Q - 120 * gR * Lf)
    _9 = [_17 * i / ph for i in range(ph + 1)] + [_17 + (Q - _17) * i / pg for i in range(1, pg + 1)]
    _8, pa = (0.0, 1.0)
    for b in _9[1:]:
        pb = pi(b)
        _8 += (pa - pb) * exp(-th * max(0.0, B - b / gR))
        pa = pb
    p, ql, hq = (exp(-cf * th), Q * Lf / Np, Q * (Q - 1) / (2 * Np))
    p2 = exp(-(cf - 1) * th) * (1 + (cf - 1) * th / (1 - th))
    hh = (Q * (Q - 1) / 2 + 2.0 ** gaD * Q) / Np
    t = dict(collision=pi(Q) * _16, delay=_8 * _16, own_trail=ql, long_partner=(cf + Sb + 3000) * Q * p * (q + gR) / ((1 - p) * Np), age_cap=hq * p2, rec_cap=2 * hq * exp(-(kr - 1) * th) * (1 + (kr - 1) * th / (1 - th)), disturbance=hq * Lf * (Q + 2.0 ** gaD) / Np, finished_count=2.0 ** (-40), cut_halt=-expm1(n2 * log1p(-p)) - n2 * p * exp((n2 - 1) * log1p(-p)) + ql * (1 + (2 + pd) * exp(-pd / 2) + 2 * hq) + hq * p * (3 + 2 * pd), key_false_match=pc * (pc - 1) / 2 * (((1 << 52) + (1 << gah + gap) - 1) // (1 << gah + gap)) / ((1 << 41) * Tp), table_capacity=2.0 ** gbP(q, pc - 59), tiny=Q * 2.0 ** gaD / Np + k * k * Lf / Np + 255 * Q / Np + exp(min(700.0, -300 + (exp(5) - 1) * hh)) + 2.0 ** (-90))
    t['sum'] = sum(t.values())
    t['P_lower'] = 1 - t['sum']
    t.update(trails=q, k=k, n2=n2, p=p, p2=p2, ql=ql, hq=hq, hh=hh, shift=_16)
    return t
_B = {}

def gaN(Tp, pb, pc, Sb):
    if (Tp, pb, pc) not in _B:
        L = Fraction(1 << 122, Tp)
        B = gac
        assert B % gA == 0 and gaR(Tp, float(B * gR / L), pb, pc, Sb)['P_lower'] >= gaf
        _B[Tp, pb, pc] = B
    return _B[Tp, pb, pc]

class gE(Exception):
    pass

class gl:

    def __init__(self, n):
        self.n = n
        st = gaA(n)
        self.st, self.pin, self.step = (st, st.pin, st.step)

    def f2(self, xs):
        return gby(xs, self.n, self.st.qwords)

    def g_scalar(self, x):
        return gbi(x, self.n) ^ self.st.qint

class gz:

    def __init__(self, n, salt):
        import random
        self.n, self.st, self.pin = (n, gbL(), [0] * n)
        _1 = random.Random(salt)
        self.ip = _1.sample(range(256), n)
        self.op = _1.sample(range(256), n)
        self.ic = _1.getrandbits(256)
        self.oc = _1.getrandbits(n)
        for j in self.ip:
            self.ic &= ~(1 << j)

    def step(self, *planes):
        _0 = [gb if self.ic >> j & 1 else 0 for j in range(256)]
        for k, j in enumerate(self.ip):
            _0[j] = planes[k]
        _3 = self.st.step(*[_0[j] ^ (gb if self.st.pin[j] else 0) for j in range(256)])
        return [_3[j] ^ (gb if self.st.pin[j] else 0) ^ (gb if self.oc >> k & 1 else 0) for k, j in enumerate(self.op)]

def gbo(x, p):
    return x & (1 << p['s1']) - 1 == (1 << p['s1']) - 1 and x >> p['s1'] & (1 << p['W']) - 1 < p['Tp']

def gbf(x, p):
    return (x >> p['D'] & (1 << p['kb']) - 1) << p['fb'] | x >> p['s1'] & (1 << p['fb']) - 1

class QF:

    def __init__(self, slots):
        self.S, self.n, self.rb = (slots, 0, gap)
        self.occ, self.cont, self.shf, self.rem, self.tr = ([0] * slots for _ in range(5))

    def _start(self, home):
        b = home
        while self.shf[b]:
            b = (b - 1) % self.S
        x = b
        while b != home:
            x = (x + 1) % self.S
            while self.cont[x]:
                x = (x + 1) % self.S
            b = (b + 1) % self.S
            while not self.occ[b]:
                b = (b + 1) % self.S
        return x

    def find(self, key):
        key &= (1 << gah + gap) - 1
        _0, _1 = (key >> self.rb, key & (1 << self.rb) - 1)
        if not self.occ[_0]:
            self.occ[_0] = 1
            x = self._start(_0)
            self.occ[_0] = 0
            return (None, (_0, x, 0))
        x = self._start(_0)
        while True:
            if self.rem[x] == _1:
                return (self.tr[x], None)
            x = (x + 1) % self.S
            if not self.cont[x]:
                return (None, (_0, x, 1))

    def put(self, key, trail, at):
        _2, x, _0 = at
        _3 = key & (1 << self.rb) - 1
        assert trail < 1 << gaD and self.n < self.S - 1
        self.occ[_2], _1 = (1, (_3, trail, _0, int(x != _2)))
        while self.cont[x] or self.shf[x] or (self.occ[x] and (x != _2 or _0)):
            _1, (self.rem[x], self.tr[x], self.cont[x], self.shf[x]) = ((self.rem[x], self.tr[x], self.cont[x], 1), _1)
            x = (x + 1) % self.S
        self.rem[x], self.tr[x], self.cont[x], self.shf[x] = _1
        self.n += 1

def gbT(xs, pb, f2):
    for _ in range(pb):
        xs = f2(xs)
    return xs

def gbD(p, r, t0, t1, f2, pf=gJ):
    _d, cr = (p['N'] - 1, p['cr'])
    _12 = -(-cr // pf)
    xs = [r + t0 & _d, r + t1 & _d]
    _a, _4 = ([None, None], [None, None])
    _2 = [[xs[0]], [xs[1]]]
    for k in range(1, cr + 1):
        xs = f2(xs)
        for _9 in (0, 1):
            if _a[_9] is None:
                if k % _12 == 0:
                    _2[_9].append(xs[_9])
                if gbo(xs[_9], p):
                    _a[_9], _4[_9] = (k, xs[_9])
        if None not in _a:
            break
    else:
        raise gE('recovery length')
    _c = 0 if _a[0] >= _a[1] else 1
    _11, (_f, _10) = (_a[1 - _c], divmod(abs(_a[0] - _a[1]), _12))
    _1 = lambda i: gbT([_2[_c][i + _f]], _10, f2)[0]
    if _4[0] != _4[1] or _1(0) == _2[1 - _c][0]:
        return None
    lo, hi = (0, _11 // _12 + 1)
    while hi - lo > 1:
        _e = (lo + hi) // 2
        if _1(_e) == _2[1 - _c][_e]:
            hi = _e
        else:
            lo = _e
    x, y = (_1(lo), _2[1 - _c][lo])
    for _ in range(min(hi * _12, _11) - lo * _12):
        fx, fy = f2([x, y])
        if fx == fy:
            return (x, y)
        x, y = (fx, fy)
    return None

def gbF(pa, p, r, pd):
    n, _7, _d = (p['n'], p['N'] - 1, pa.pin)
    _12 = QF(p['tmax'] + 1)
    _2, ts, _a = ([0] * gR, list(range(gR)), gR)
    _e = gbw([r + t & _7 for t in ts], n, _d)
    pd['inserts'] += gR
    _1, _9, _6 = (0, p['Sb'], p['B'] + 3000)
    while _6:
        _e = list(pa.step(*_e))
        _1 += 1
        pd['batches'] += 1
        _c = pd['passing']
        _3 = gbJ(_e, p, pd)
        _b = pd['passing'] != _c
        if _b and _1 >= p['B']:
            return None
        while _3:
            pd['stage1_hits'] += 1
            if pd['stage1_hits'] > p['e2max']:
                raise gE('stage-1 budget')
            l = (_3 & -_3).bit_length() - 1
            _3 &= _3 - 1
            x = gbp(_e, l, _d, n)
            if gbo(x, p):
                _4 = gbf(x, p)
                pd['finished'] += 1
                t0, at = _12.find(_4)
                if t0 is not None:
                    pd['recoveries'] += 1
                    _f = gbD(p, r, t0, ts[l], pa.f2)
                    if _f is None:
                        raise gE('recovery found no pair')
                    return _f
                if _12.n >= p['tmax']:
                    raise gE('table full')
                _12.put(_4, ts[l], at)
                if _12.n >= p['tmax']:
                    raise gE('table full')
                ts[l], _a, _2[l] = (_a, _a + 1, _1)
                _e = gbI(_e, l, r + ts[l] & _7, _d, n)
                pd['inserts'] += 1
        if _b and _1 >= _9:
            _9 += p['Sb']
            for l in range(gR):
                if _1 - _2[l] >= p['c']:
                    pd['cut'] += 1
                    if pd['cut'] > p['cmax']:
                        raise gE('cut budget')
                    ts[l], _a, _2[l] = (_a, _a + 1, _1)
                    _e = gbI(_e, l, r + ts[l] & _7, _d, n)
                    pd['inserts'] += 1
        _6 -= 1
        assert _6 == p['B'] + 3000 - _1
    pd['batch_limit'] += 1
    return None

class gj(dict):

    def __missing__(self, k):
        return 0

def gbd(pa, pb, pc=256):
    return int.from_bytes(hashlib.shake_256(('%s/%s' % (pa, pb)).encode()).digest((pc + 7) // 8), 'little') & (1 << pc) - 1

def gba(pa, p, pc, pd):
    _0 = gj()
    try:
        _1 = gbF(pa, p, gbd(pc, pd, p['n']), _0)
    except gE as e:
        _0['halt'] += 1
        _1 = None
    return (_1, _0)
gX = 18
gW, gc = (2048, 21)
gaB = ('w0',)

def gbg(pa, pb):
    p = gbA(gX)
    _3, _0 = gba(pb, p, pa, 't')
    _1 = dict(target_ok=int(_3 is not None), target_batches=_0['batches'], target_halt=_0['halt'], batch_limit_no_pass=1)
    if _3 is None:
        return (None, None, _1)
    return (gbu(_3[0]), gbu(_3[1]), _1)
gaI = (1 << gc) - 1

def gbM(pa):
    return [[d & gaI for d in pa]]

def gbh(pa, tr, pc):
    _f = tr % 3
    if _f == 0:
        xs = [gbd(pa, 'u%d' % i) for i in range(gW)]
    elif _f == 1:
        r = gbd(pa, 'r')
        xs = [r + i & (1 << 256) - 1 for i in range(gW)]
    else:
        xs = None
    _5 = []
    if xs is not None:
        for b in range(gW // gR):
            pl = gbw(xs[b * gR:(b + 1) * gR], 256, pc.pin)
            _5 += gbq(list(pc.step(*pl)), 256, pc.pin)
    else:
        _3 = [gbd(pa, 'c%d' % l) for l in range(gR)]
        xs = []
        for b in range(gW // gR):
            xs += _3
            _3 = gbq(list(pc.step(*gbw(_3, 256, pc.pin))), 256, pc.pin)
            _5 += _3
    _5 = [d ^ pc.qint for d in _5]
    _b = {'source': _f}
    _c = None
    for k, _2 in enumerate(gbM(_5)):
        _a = gaB[k]
        _b['dup_' + _a] = len(_2) - len(set(_2))
        if k == 0 and _b['dup_w0']:
            _6 = {}
            for i, c in enumerate(_2):
                if c in _6 and xs[_6[c]] != xs[i]:
                    _c = (xs[_6[c]], xs[i])
                    break
                _6.setdefault(c, i)
    if _c is None:
        return (None, None, _b)
    return (gbu(_c[0]), gbu(_c[1]), _b)

def gbm(pa):
    import random
    n, _4, _1e, _d = (20, 1200, 1 << 20, 64)
    _5 = len(pa)
    if _5 < _d:
        raise ValueError('h1-law-n20 requires at least 64 trials')
    _19 = int.from_bytes(hashlib.sha256(b'b3-h1-shared-v1\x00' + b'\x00'.join((t['seed'].encode() for t in pa))).digest(), 'little')
    _8 = gz(n, _19)
    xs = [gbd(t['seed'], 'h1-start', n) for t in pa[:_d]]
    _18 = gbw(xs, n, [0] * n)
    _1c = [{x} for x in xs]
    _a = [0] * _d
    _c, _f, _1 = (set(), 0, _d)
    for _1f in range(1, _4 + 1):
        _16 = xs
        _18 = list(_8.step(*_18))
        xs = gbq(_18, n, _8.pin)[:_d]
        for i, _21 in enumerate(xs):
            if _a[i]:
                continue
            x = _16[i]
            if x not in _c:
                _c.add(x)
                _f += _21 & 15 == 15
            if _21 in _1c[i]:
                _a[i], _1 = (_1f, _1 - 1)
            else:
                _1c[i].add(_21)
        if not _1:
            break
    _a = [x or _4 + 1 for x in _a]

    def _e(values):
        return [sum((x <= 400 for x in values)), sum((400 < x <= 700 for x in values)), sum((700 < x <= 1000 for x in values)), sum((x > 1000 for x in values))]

    def _1d(index):
        _6 = random.Random(gbd(str(_19), 'h1-null-%d' % index))
        _5 = {}
        _a = [_6.randrange(_1e) for _ in range(_d)]
        _b = [{x} for x in _a]
        _8 = [0] * _d
        _2 = _3 = 0
        _1 = _d
        for _7 in range(1, _4 + 1):
            for i in range(_d):
                if _8[i]:
                    continue
                x = _a[i]
                if x not in _5:
                    _5[x] = _6.randrange(_1e)
                    _2 += 1
                    _3 += _5[x] & 15 == 15
                _9 = _5[x]
                _a[i] = _9
                if _9 in _b[i]:
                    _8[i], _1 = (_7, _1 - 1)
                else:
                    _b[i].add(_9)
            if not _1:
                break
        _8 = [x or _4 + 1 for x in _8]
        z = (_3 - _2 / 16) / (_2 * 15 / 256) ** 0.5
        return (_e(_8), z)
    _9 = [_1d(i) for i in range(64)]
    _b, _3 = (_9[:32], _9[32:])
    _12 = [sum((x[0][j] for x in _b)) / len(_b) for j in range(4)]
    _22 = [sum(((x[0][j] - _12[j]) ** 2 for x in _b)) / (len(_b) - 1) for j in range(4)]

    def _1a(bins):
        return sum(((bins[j] - _12[j]) ** 2 / max(1, _22[j]) for j in range(4)))
    _2 = _e(_a)
    _15 = _1a(_2)
    _1b = 1.25 * max((_1a(x[0]) for x in _3)) + 1e-12
    _7 = (_f - len(_c) / 16) / (len(_c) * 15 / 256) ** 0.5
    _6 = max(4, 1.25 * max((abs(x[1]) for x in _3)))
    _17 = _15 <= _1b and abs(_7) <= _6
    _14 = dict(bin0=_2[0], bin1=_2[1], bin2=_2[2], bin3=_2[3], gof=_15, gof_limit=_1b, dp_z=_7, dp_limit=_6, fresh=len(_c), dp_hits=_f, groups=_d, fit_nulls=32, calibration_nulls=32, law_pass=int(_17))
    return [(None, None, _14) for _ in range(_5)]

def gbj():

    def _7(values, widths):
        _3 = _0 = 0
        assert len(values) == len(widths)
        for _1, _2 in zip(values, widths):
            assert 0 <= _1 < 1 << _2
            _3 |= _1 << _0
            _0 += _2
        return _3
    for _e in ((2, 10, 10, 10), (8, 10, 10, 10), (36, 1, 1, 1), (gaD,), (128,)):
        _c = tuple(((1 << _d) - 1 for _d in _e))
        assert _7(_c, _e) == (1 << sum(_e)) - 1
        for _4, _d in enumerate(_e):
            _6 = list(_c)
            _6[_4] = 1 << _d
            try:
                _7(_6, _e)
            except AssertionError:
                continue
            raise AssertionError
    _a = QF(65569)
    _5 = (1 << gah + gap) - 1
    assert _5 >> gap == (1 << gah) - 1
    assert _5 & (1 << gap) - 1 == (1 << gap) - 1
    _, at = _a.find(_5)
    _a.put(_5, (1 << gaD) - 1, at)
    _8 = False
    try:
        _, at = _a.find(_5 - 1)
        _a.put(_5 - 1, 1 << gaD, at)
    except AssertionError:
        _8 = True
    _, _, _, _, _3, _b = gbt()
    _2 = gV - gax - _3 - gan - gg - ga
    _9, _ = gbz(_3, _b)
    assert _9 == _3 + gg + ga + gq * gu + gv
    assert _8 and _a.find(_5)[0] == (1 << gaD) - 1
    assert gR + _b + gf < 1 << gaD
    assert gbN(_b + 1) <= _2 < gbN(_b + 2)

def gbH(pa):
    gbj()
    _5 = gbC()
    gbb(_5)
    st = gbL()
    _8 = gbx(st.qwords)[1]
    _4 = (st.ops + 31) * go + _8 * gal + 1335 * gG
    assert (_5['bytes'], _5['bitwise'], _5['packed'], _5['control']) == (_4, st.ops + 31, _8, 1335)
    _2, _7 = (pa['experiment_id'], [])
    if _2 == 'bsrho-n18':
        _3 = gl(gX)
        for t in pa['trials']:
            a, b, _6 = gbg(t['seed'], _3)
            _7.append({'trial': t['trial'], 'message_a_hex': a.hex() if a else None, 'message_b_hex': b.hex() if b else None, 'observations': _6})
    elif _2 == 'proj-prefix-w256':
        st = gbL()
        for t in pa['trials']:
            a, b, _6 = gbh(t['seed'], t['trial'], st)
            _7.append({'trial': t['trial'], 'message_a_hex': a.hex() if a else None, 'message_b_hex': b.hex() if b else None, 'observations': _6})
    elif _2 == 'h1-law-n20':
        for t, (a, b, _6) in zip(pa['trials'], gbm(pa['trials'])):
            _7.append({'trial': t['trial'], 'message_a_hex': a, 'message_b_hex': b, 'observations': _6})
    else:
        raise ValueError('unknown experiment')
    return {'schema_version': 1, 'trials': _7}
json.dump(gbH(json.load(sys.stdin)), sys.stdout)
