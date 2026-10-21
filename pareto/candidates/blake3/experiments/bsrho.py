import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, log, exp, expm1, log1p
gS = 4294967295
IV = (1779033703, 3144134277, 1013904242, 2773480762, 1359893119, 2600822924, 528734635, 1541459225)
gap = 5
gaD = 1054
gX = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
gp = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15), (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
gP, gb = (256, (1 << 256) - 1)
gn = 11
gI = (2147483648, 0, 2147483648, 0, 2147483648, 0, 0, 0)
gK = sum((w << 32 * i for i, w in enumerate(gI)))
gJ = b''.join((w.to_bytes(4, 'little') for w in gI))

def gaT(v, k):
    return (v >> k | v << 32 - k) & gS

def gbb(m, pb=gap, pc=gn, pd=64, pe=0):
    v = list(IV) + list(IV[:4]) + [pe & gS, pe >> 32, pd, pc]
    m = list(m)
    for _ in range(pb):
        for j, (a, b, c, d) in enumerate(gp):
            x, y = (m[2 * j], m[2 * j + 1])
            v[a] = v[a] + v[b] + x & gS
            v[d] = gaT(v[d] ^ v[a], 16)
            v[c] = v[c] + v[d] & gS
            v[b] = gaT(v[b] ^ v[c], 12)
            v[a] = v[a] + v[b] + y & gS
            v[d] = gaT(v[d] ^ v[a], 8)
            v[c] = v[c] + v[d] & gS
            v[b] = gaT(v[b] ^ v[c], 7)
        m = [m[i] for i in gX]
    return [v[i] ^ v[i + 8] for i in range(8)]

def gbf(x, n, pc=gK):
    kw = [pc >> 32 * i & gS for i in range(8)]
    d = gbb(kw + [x >> 32 * i & gS for i in range(8)])
    return sum((d[i] << 32 * i for i in range(8))) & (1 << n) - 1

def gbr(x):
    return gJ + x.to_bytes(32, 'little')
gY, gZ = (36, 7)
gao = sum((1 << gY * i for i in range(gZ)))
gQ = 1 << gY

class gaC:

    def __init__(self):
        self.lines, self.ops, self.k = ([], 0, 0)

    def emit(self, expr):
        self.k += 1
        _0 = 't%d' % self.k
        self.lines.append('%s=%s' % (_0, expr))
        self.ops += 1
        return _0

    def mask(self, a):
        return ('v', self.emit('%s&%d' % (a[1], gao * gS)), gS)

    def add(self, *xs):
        c = sum((x[1] for x in xs if x[0] == 'c')) & gS
        vs = [x for x in xs if x[0] == 'v']
        if not vs:
            return ('c', c)
        _0 = vs[0]
        for v in vs[1:]:
            while _0[2] + v[2] >= gQ:
                if _0[2] >= v[2]:
                    _0 = self.mask(_0)
                else:
                    v = self.mask(v)
            _0 = ('v', self.emit('%s+%s' % (_0[1], v[1])), _0[2] + v[2])
        if c:
            if _0[2] + c >= gQ:
                _0 = self.mask(_0)
            _0 = ('v', self.emit('%s+%d' % (_0[1], gao * c)), _0[2] + c)
        return _0

    def xor(self, a, b):
        if a[0] == 'c' and b[0] == 'c':
            return ('c', a[1] ^ b[1])
        if a[0] == 'c':
            a, b = (b, a)
        if b[0] == 'c':
            if b[1] == 0:
                return a
            return ('v', self.emit('%s^%d' % (a[1], gao * b[1])), (1 << max(a[2].bit_length(), b[1].bit_length())) - 1)
        return ('v', self.emit('%s^%s' % (a[1], b[1])), (1 << max(a[2].bit_length(), b[2].bit_length())) - 1)

    def ror(self, a, r):
        if a[0] == 'c':
            return ('c', gaT(a[1], r))
        s1 = self.emit('%s>>%d' % (a[1], r))
        h = self.emit('%s&%d' % (s1, gao * ((1 << 32 - r) - 1)))
        s2 = self.emit('%s<<%d' % (a[1], 32 - r))
        lw = self.emit('%s&%d' % (s2, gao * ((1 << r) - 1 << 32 - r)))
        return ('v', self.emit('%s|%s' % (h, lw)), gS)

def gaZ(qw):
    tr = gaC()
    v = [('c', w) for w in IV] + [('c', w) for w in IV[:4]] + [('c', 0), ('c', 0), ('c', 64), ('c', gn)]
    m = [('c', w) for w in gI] + [('v', 'i%d' % i, gS) for i in range(8, 16)]
    for _ in range(gap):
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
        m = [m[i] for i in gX]
    _e = []
    for i in range(8):
        z = tr.xor(tr.xor(v[i], v[i + 8]), ('c', qw[i]))
        if z[2] > gS:
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
gaH = {}

def gbu(qw):
    qw = tuple(qw)
    if qw not in gaH:
        gaH[qw] = gaZ(qw)
    return gaH[qw]

def gbv(xs, n, qw):
    _4 = [sum(((x >> 32 * i & gS) << gY * l for l, x in enumerate(xs))) for i in range(8)]
    _3 = gbu(qw)[0](*_4)
    _2 = (1 << n) - 1
    return [sum(((_3[i] >> gY * l & gS) << 32 * i for i in range(8))) & _2 for l in range(len(xs))]
gaE, gW = ((0, 0), (0, 1))

class gz:

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
            return gaE if x[1] == 0 else y
        if y[0] == 0:
            return gaE if y[1] == 0 else x
        if x[0] == y[0]:
            return x if x[1] == y[1] else gaE
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
            return ((x[0], x[1] ^ k), gW if k1 == k2 == 1 else gaE if k1 == k2 == 0 else x)
        kk = cs[0][1] + cs[1][1] + cs[2][1]
        return (gaE if kk % 2 == 0 else gW, gW if kk >= 2 else gaE)

    def add(self, A, B):
        s, c = ([], gaE)
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
        s, u = ([s0], gaE)
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

def gaW(*W):
    return all((any((t[0] != 0 for t in w)) for w in W))

def gaU(A, r):
    return [A[(i + r) % 32] for i in range(32)]

def gaM(v):
    return [gW if v >> i & 1 else gaE for i in range(32)]

def gbN(n):
    g = gz(n)
    _e = gaM(0)
    m = [gaM(w) for w in gI] + [[g.inputs[32 * i + b] if 32 * i + b < n else gaE for b in range(32)] for i in range(8)]
    v = [gaM(w) for w in IV] + [gaM(w) for w in IV[:4]] + [_e, _e, gaM(64), gaM(gn)]
    for _ in range(gap):
        for j, (a, b, c, d) in enumerate(gp):
            x, y = (m[2 * j], m[2 * j + 1])
            v[a] = g.add3(v[a], v[b], x) if gaW(v[a], v[b], x) else g.add(g.add(v[a], v[b]), x)
            v[d] = gaU(g.xorw(v[d], v[a]), 16)
            v[c] = g.add(v[c], v[d])
            v[b] = gaU(g.xorw(v[b], v[c]), 12)
            v[a] = g.add3(v[a], v[b], y) if gaW(v[a], v[b], y) else g.add(g.add(v[a], v[b]), y)
            v[d] = gaU(g.xorw(v[d], v[a]), 8)
            v[c] = g.add(v[c], v[d])
            v[b] = gaU(g.xorw(v[b], v[c]), 7)
        m = [m[i] for i in gX]
    return (g, [s for i in range(8) for s in g.xorw(v[i], v[i + 8])])

class gay:

    def __init__(self, n=256):
        g, _16 = gbN(n)
        self.n, self.pin, self.gen_calls, self.hits = (n, [0] * n, g.calls, g.hits)
        assert all((_16[j][0] != 0 for j in range(n)))
        self.q = [_16[j][1] for j in range(n)]
        self.qint = sum((b << j for j, b in enumerate(self.q)))
        self.qwords = [self.qint >> 32 * i & gS for i in range(8)]
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

    def spill_ops(self, R):
        from bisect import bisect_left
        _0 = 10 ** 10
        _d = {}
        for k, (_, a, b) in enumerate(self.lines):
            for v in (a, b):
                if v not in ('0', '#'):
                    _d.setdefault(v, []).append(k)
        _b = set(self.outs)

        def _a(v, k):
            u = _d.get(v)
            if u:
                i = bisect_left(u, k)
                if i < len(u):
                    return u[i]
            return 10 ** 9 if v in _b else _0
        _c, _7, _4 = ({'i%d' % j for j in range(self.n)}, set(), 0)
        if len(_c) > R:
            for v in sorted(_c, key=lambda y: -_a(y, 0))[:len(_c) - R]:
                _c.discard(v)
                _7.add(v)
        for k, (nm, a, b) in enumerate(self.lines):
            _8 = [v for v in {a, b} if v not in ('0', '#')]
            for v in _8:
                if v not in _c:
                    _4 += 1
                    while len(_c) >= R:
                        w = max((y for y in _c if y not in _8), key=lambda y: _a(y, k))
                        _c.discard(w)
                        if w not in _7 and _a(w, k) < _0:
                            _4 += 1
                            _7.add(w)
                    _c.add(v)
            for v in _8:
                if _a(v, k + 1) >= _0:
                    _c.discard(v)
            while len(_c) >= R:
                w = max(_c, key=lambda y: _a(y, k + 1))
                _c.discard(w)
                if w not in _7 and _a(w, k + 1) < _0:
                    _4 += 1
                    _7.add(w)
            _c.add(nm)
        return _4

def gaX(st):
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

def gbB(st, pb, pc):
    _6 = [0] * (max((c[1] for c in pb)) + 1)
    _6[:st.n] = pc
    for nm, d, ra, rb in pb:
        va = _6[ra] if ra >= 0 else 0
        vb = gb if st.opsym[nm][1] else _6[rb] if rb >= 0 else 0
        o = st.opsym[nm][0]
        _6[d] = va ^ vb if o == '^' else va & vb if o == '&' else va | vb
    return _6[:st.n]

def gaV():
    _2, s = ({}, 128)
    while s:
        m = 0
        for c in range(256):
            if not c & s:
                m |= 1 << c
        _2[s] = m
        s >>= 1
    return _2
gaK = gaV()

def gbO(pa):
    R = list(pa) + [0] * (256 - len(pa))
    s = 128
    while s:
        m = gaK[s]
        for i in range(256):
            if not i & s:
                t = (R[i] >> s ^ R[i + s]) & m
                R[i + s] ^= t
                R[i] ^= t << s
        s >>= 1
    return R

def gbt(xs, n, pc):
    T = gbO(xs)
    return [T[j] ^ (gb if pc[j] else 0) for j in range(n)]

def gbn(pa, n, pc):
    T = gbO([pa[j] ^ (gb if pc[j] else 0) for j in range(n)])
    return T[:256]

def gbm(pa, l, pc, n):
    x = 0
    for j in range(n):
        x |= (pa[j] >> l & 1 ^ pc[j]) << j
    return x

def gbF(pa, l, x, pd, n):
    _0 = 1 << l
    return [pa[j] & ~_0 | (x >> j & 1 ^ pd[j]) << l for j in range(n)]
gO = Fraction(497, 1000)
gh = Fraction(15, 100000)
gad = 0.390000001
gy = 10 ** 24
gf = 1
gax, SC = (32, 12)
gR = 4
gB = 2800
gk = 3800
gau = 2048
gi = 4200
gat = 4000
KR, gH = (Fraction(62, 5), 8192)
gag, gah = (64, 128)
ge, gac, gak = (80, 100, 8000)
gE = 36
gaj = 5
gu = 36
go = 5
gaw = 0
gq = 2400
gA, gar, gai = (625, 35, 110)
gam = 775
gal = gam * 32
gg = 5248
gaB, gm, gan, gaf, gM = (17, 3, 36, 16, 7)
gT = 1048576
gav = 0
ga = 32
gaA = -40
gG = 20
gs = 200
gw = 2400
gr = 256
gv = 2048
gt = 68
gas = 256 * 3100 + 20000
gL = 64692944896
gab = 1 << 40
gaa = 1324811873788000000000000000000000000
gd = {18: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4), 20: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4), 256: dict(s1=32, W=90, kappa=gG, Sb=1 << 48)}

def gaO(pa, op, d='-', a='-', b='-', pf=gE):
    return (pa, op, str(d), str(a), str(b), pf)

def gaR(pa):
    _3, _2 = pa.split('=', 1)
    for op in ('<<', '>>', '&', '^', '+', '|'):
        if op in _2:
            a, b = _2.split(op, 1)
            return (_3, op, a, int(b) if b.isdigit() else b)
    raise ValueError('bad packed instruction: ' + pa)

def gaQ(qw):
    import heapq
    pc = gbu(qw)
    _10 = [gaR(x) for x in pc[3]]
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
        _3.append(gaO('P', {'+': 'ADD', '^': 'XOR', '&': 'AND', '|': 'OR', '<<': 'SHL', '>>': 'SHR'}[op], 'r%d' % d, 'r%d' % ra, str(rb) if op in ('<<', '>>') else 'r%d' % rb, gaj))
    _b = [gaO('K', 'LOADI', 'r%d' % _5[x], x[0], hex(x[1])) for x in _4]
    assert _d <= gam
    return (_b, _3, _d, [_14[x] for x in pc[4]])

def gaN(st):
    import re
    _5, _24 = gaX(st)
    assert _24 == 773
    _22 = [gaO('step', {'^': 'XOR', '&': 'AND', '|': 'OR'}[st.opsym[n][0]], 'r%d' % d, 'r%d' % a, 'r%d' % b, go) for n, d, a, b in _5]

    def L(section, name):
        return gaO(section, 'LABEL', name, pf=0)

    def C(section, rows):
        return [gaO(section, *x) for x in rows]
    _4 = '%a'
    _21 = [gaO('stage1', 'AND', _4, 'r0', 'r1', go)]
    _21 += [gaO('stage1', 'AND', _4, _4, 'r%d' % j, go) for j in range(2, SC)]
    _21 += C('S', [('BRZ', '@d', _4), ('LOAD', '%ae', 'state.passing_left'), ('SUBI', '%ae', '%ae', '1'), ('STORE', 'state.passing_left', '%ae'), ('BRLT', '@W', '%ae')])
    _21 += [gaO('stage1', 'AND', _4, _4, 'r%d' % j, go) for j in range(SC, gax)]
    _21 += C('S', [('LOAD', '%e', 'state.batch'), ('LOAD', '%af', 'state.next_limit'), ('CMP', '%ag', '%e', '%af'), ('BRLT', '@b', '%ag'), ('CALL', '@i')])
    _21 += [L('S', '@b'), gaO('S', 'BRNZ', '@c', _4)]
    _21 += [L('loop', '@d'), gaO('loop', 'LOAD', '%e', 'state.batch'), gaO('loop', 'ADDI', '%e', '%e', '1'), gaO('loop', 'STORE', 'state.batch', '%e'), gaO('loop', 'BR', '@f')]
    _1d = [L('U', '@g')]
    _1d += C('U', [('RANDOM', '%ah'), ('MOVI', '%e', '0'), ('MOVI', '%ai', '256'), ('MOVI', '%aj', '0'), ('MOVI', '%ae', '80354184746460387503307058140284243'), ('MOVI', '%ak', '157929882262706756591796875064'), ('MOVI', '%al', str(1 << 48)), ('MOV', '%af', '%al'), ('MOVI', '%am', '0'), ('STORE', 'state.random', '%ah'), ('STORE', 'state.batch', '%e'), ('STORE', 'state.next_trail', '%ai'), ('STORE', 'state.table_count', '%aj'), ('STORE', 'state.passing_left', '%ae'), ('STORE', 'state.hit_left', '%ak'), ('STORE', 'state.next_slice', '%al'), ('STORE', 'state.next_limit', '%af'), ('STORE', 'state.cut_count', '%am'), ('MOVI', '%an', '0')])
    _1d += [L('U', '@h')]
    _1d += C('U', [('MOV', '%ao', '%an'), ('CALL', '@ap'), ('MOV', '%aq', '%e'), ('CALL', '@o'), ('ADD', '%ar', '%ah', '%an'), ('CALL', '@as'), ('ADDI', '%an', '%an', '1'), ('CMP', '%ag', '%an', '256'), ('BRLT', '@h', '%ag'), ('BR', '@f')])
    _1d += [L('U', '@i')]
    _1d += C('U', [('LOAD', '%e', 'state.batch'), ('CMP', '%ag', '%e', '1324811873788000000000000000000000000'), ('BRGE', '@aa', '%ag'), ('CALL', '@k'), ('LOAD', '%al', 'state.next_slice'), ('ADDI', '%al', '%al', str(1 << 48)), ('STORE', 'state.next_slice', '%al'), ('MOV', '%af', '%al'), ('STORE', 'state.next_limit', '%af'), ('CMP', '%ag', '%af', '1324811873788000000000000000000000000'), ('BRLE', '@j', '%ag'), ('MOVI', '%af', '1324811873788000000000000000000000000'), ('STORE', 'state.next_limit', '%af'), ('RET',), ('HALT', 'late_limit')])
    _1d += [L('U', '@j'), gaO('U', 'RET'), L('U', '@k')]
    _1d += C('U', [('MOVI', '%an', '0')]) + [L('U', '@at')]
    _1d += C('U', [('CALL', '@au'), ('SUB', '%av', '%e', '%aq'), ('CMP', '%ag', '%av', '59740584080220938108036272372150319'), ('BRLT', '@l', '%ag'), ('LOAD', '%am', 'state.cut_count'), ('ADDI', '%am', '%am', '1'), ('STORE', 'state.cut_count', '%am'), ('CMP', '%ag', '%am', '1'), ('BRGT', '@Z', '%ag'), ('LOAD', '%ai', 'state.next_trail'), ('MOV', '%aw', '%ai'), ('ADDI', '%ai', '%ai', '1'), ('STORE', 'state.next_trail', '%ai'), ('MOV', '%ao', '%aw'), ('CALL', '@ap'), ('MOV', '%aq', '%e'), ('CALL', '@o'), ('LOAD', '%ah', 'state.random'), ('ADD', '%ar', '%ah', '%aw'), ('CALL', '@as')])
    _1d += [L('U', '@l')]
    _1d += C('U', [('ADDI', '%an', '%an', '1'), ('CMP', '%ag', '%an', '256'), ('BRLT', '@at', '%ag'), ('RET',)]) + [L('U', '@as')]
    _1d += C('U', [('MOV', '%ax', '%ar'), ('MOVI', '%ay', '0'), ('MOVI', '%az', '1'), ('SHL', '%az', '%az', '%an'), ('NOT', '%aA', '%az')])
    _1d += [L('U', '@m')]
    _1d += C('U', [('SHR', '%aB', '%ax', '%ay'), ('ANDI', '%aB', '%aB', '1'), ('SHL', '%aB', '%aB', '%an'), ('LOAD', '%aC', 'R[%ay]'), ('AND', '%aC', '%aC', '%aA'), ('OR', '%aC', '%aC', '%aB'), ('STORE', 'R[%ay]', '%aC'), ('ADDI', '%ay', '%ay', '1'), ('CMP', '%ag', '%ay', '256'), ('BRLT', '@m', '%ag'), ('RET',)])
    _1d += [L('U', '@n')]
    _1d += C('U', [('MOV', '%bm', '%an'), ('MOVI', '%bw', 'active_trails'), ('CALL', '@B'), ('RET',)]) + [L('U', '@ap')]
    _1d += C('U', [('MOV', '%bm', '%an'), ('MOVI', '%bw', 'active_trails'), ('CALL', '@C'), ('RET',)]) + [L('U', '@au')]
    _1d += C('U', [('SHR', '%aD', '%an', '1'), ('LOAD', '%aE', 'birth_words[%aD]'), ('ANDI', '%aF', '%an', '1'), ('SHL', '%aG', '%aF', '7'), ('SHR', '%aq', '%aE', '%aG'), ('ANDI', '%aq', '%aq', hex((1 << 128) - 1)), ('RET',)])
    _1d += [L('U', '@o')]
    _1d += C('U', [('SHR', '%aD', '%an', '1'), ('ANDI', '%aF', '%an', '1'), ('SHL', '%aG', '%aF', '7'), ('MOVI', '%aH', hex((1 << 128) - 1)), ('SHL', '%aH', '%aH', '%aG'), ('NOT', '%aI', '%aH'), ('LOAD', '%aE', 'birth_words[%aD]'), ('AND', '%aE', '%aE', '%aI'), ('SHL', '%aJ', '%aq', '%aG'), ('OR', '%aE', '%aE', '%aJ'), ('STORE', 'birth_words[%aD]', '%aE'), ('RET',)])
    _b = [L('H', '@c')]
    _b += C('H', [('MOVI', '%an', '0')]) + [L('H', '@aK')]
    _b += C('H', [('SHR', '%aM', _4, '%an'), ('ANDI', '%aM', '%aM', '1'), ('BRZ', '@aP', '%aM'), ('LOAD', '%ak', 'state.hit_left'), ('SUBI', '%ak', '%ak', '1'), ('STORE', 'state.hit_left', '%ak'), ('BRLT', '@X', '%ak'), ('MOVI', '%aN', '0'), ('MOVI', '%ay', '32')]) + [L('H', '@aL')]
    _b += C('H', [('LOAD', '%aC', 'R[%ay]'), ('SHR', '%aM', '%aC', '%an'), ('ANDI', '%aM', '%aM', '1'), ('SHL', '%aM', '%aM', '%ay'), ('OR', '%aN', '%aN', '%aM'), ('ADDI', '%ay', '%ay', '1'), ('CMP', '%ag', '%ay', '122'), ('BRLT', '@aL', '%ag'), ('SHR', '%aO', '%aN', '32'), ('ANDI', '%aO', '%aO', hex((1 << 90) - 1)), ('CMP', '%ag', '%aO', '1780'), ('BRGE', '@aP', '%ag')])
    _b += [L('H', '@p')]
    _b += C('H', [('LOAD', '%aC', 'R[%ay]'), ('SHR', '%aM', '%aC', '%an'), ('ANDI', '%aM', '%aM', '1'), ('SHL', '%aM', '%aM', '%ay'), ('OR', '%aN', '%aN', '%aM'), ('ADDI', '%ay', '%ay', '1'), ('CMP', '%ag', '%ay', '163'), ('BRLT', '@p', '%ag'), ('SHR', '%aQ', '%aN', '122'), ('SHL', '%aQ', '%aQ', '11'), ('ANDI', '%aO', '%aO', '2047'), ('OR', '%aQ', '%aQ', '%aO'), ('CALL', '@r'), ('BRNZ', '@q', '%aR'), ('LOAD', '%aj', 'state.table_count'), ('CMP', '%ag', '%aj', '116111'), ('BRGE', '@Y', '%ag'), ('CALL', '@n'), ('MOV', '%aS', '%ao'), ('MOV', '%aT', '%aS'), ('CALL', '@aU'), ('ADDI', '%aj', '%aj', '1'), ('STORE', 'state.table_count', '%aj'), ('CMP', '%ag', '%aj', '116111'), ('BRGE', '@Y', '%ag'), ('LOAD', '%ai', 'state.next_trail'), ('MOV', '%aw', '%ai'), ('ADDI', '%ai', '%ai', '1'), ('STORE', 'state.next_trail', '%ai'), ('MOV', '%ao', '%aw'), ('CALL', '@ap'), ('MOV', '%aq', '%e'), ('CALL', '@o'), ('LOAD', '%ah', 'state.random'), ('ADD', '%ar', '%ah', '%aw'), ('CALL', '@as'), ('BR', '@aP')])
    _b += [L('H', '@q')]
    _b += C('H', [('MOV', '%bz', '%cn'), ('CALL', '@n'), ('MOV', '%bB', '%ao'), ('CALL', '@bx'), ('HALT', 'recovery_returned')]) + [L('H', '@aP')]
    _b += C('H', [('ADDI', '%an', '%an', '1'), ('CMP', '%ag', '%an', '256'), ('BRLT', '@aK', '%ag'), ('BR', '@d')])
    q = [L('H', '@r')]
    q += C('H', [('ANDI', '%co', '%aQ', hex((1 << 52) - 1)), ('SHR', '%cp', '%co', '36'), ('ANDI', '%cq', '%co', hex((1 << 36) - 1)), ('MOVI', '%ba', str(8 * 116112)), ('MOV', '%bm', '%cp'), ('CALL', '@bb'), ('SHR', '%aJ', '%bc', '36'), ('ANDI', '%aJ', '%aJ', '1'), ('BRZ', '@aW', '%aJ'), ('CALL', '@t'), ('MOV', '%bm', '%bo')]) + [L('H', '@aV')]
    q += C('H', [('SUBI', '%ba', '%ba', '1'), ('BRLT', '@ac', '%ba'), ('CALL', '@bb'), ('ANDI', '%aJ', '%bc', hex((1 << 36) - 1)), ('CMP', '%ag', '%aJ', '%cq'), ('BREQ', '@aX', '%ag'), ('CALL', '@w'), ('CALL', '@bb'), ('SHR', '%aJ', '%bc', '37'), ('ANDI', '%aJ', '%aJ', '1'), ('BRNZ', '@aV', '%aJ')]) + [L('H', '@aW')]
    q += C('H', [('MOVI', '%aR', '0'), ('RET',)]) + [L('H', '@aX')]
    q += C('H', [('MOVI', '%bw', 'table_trails'), ('CALL', '@B'), ('MOV', '%cn', '%ao'), ('MOVI', '%aR', '1'), ('RET',)]) + [L('H', '@aU')]
    q += C('H', [('ANDI', '%co', '%aQ', hex((1 << 52) - 1)), ('SHR', '%cp', '%co', '36'), ('ANDI', '%cr', '%co', hex((1 << 36) - 1)), ('MOVI', '%ba', str(8 * 116112)), ('MOV', '%bm', '%cp'), ('CALL', '@bb'), ('SHR', '%cs', '%bc', '36'), ('ANDI', '%cs', '%cs', '1'), ('BRNZ', '@aY', '%cs'), ('ORI', '%bc', '%bc', hex(1 << 36)), ('CALL', '@z'), ('CALL', '@t'), ('MOV', '%bm', '%bo'), ('MOVI', '%bd', '0'), ('BR', '@s')]) + [L('H', '@aY')]
    q += C('H', [('CALL', '@t'), ('MOV', '%bm', '%bo')]) + [L('H', '@aZ')]
    q += C('H', [('SUBI', '%ba', '%ba', '1'), ('BRLT', '@ac', '%ba'), ('CALL', '@w'), ('CALL', '@bb'), ('SHR', '%aJ', '%bc', '37'), ('ANDI', '%aJ', '%aJ', '1'), ('BRNZ', '@aZ', '%aJ'), ('MOVI', '%bd', '1')])
    q += [L('H', '@s')]
    q += C('H', [('MOVI', '%ct', '1'), ('CMP', '%ag', '%bm', '%cp'), ('BRNE', '@be', '%ag'), ('MOVI', '%ct', '0')]) + [L('H', '@be')]
    q += C('H', [('SUBI', '%ba', '%ba', '1'), ('BRLT', '@ac', '%ba'), ('CALL', '@bb'), ('MOV', '%cu', '%bc'), ('MOVI', '%bw', 'table_trails'), ('CALL', '@B'), ('MOV', '%cv', '%ao'), ('SHR', '%cw', '%cu', '37'), ('ANDI', '%cw', '%cw', '1'), ('SHR', '%cx', '%cu', '38'), ('OR', '%cy', '%cw', '%cx'), ('SHR', '%cz', '%cu', '36'), ('ANDI', '%cz', '%cz', '1'), ('CMP', '%ag', '%bm', '%cp'), ('BRNE', '@bf', '%ag'), ('BRNZ', '@bf', '%bd'), ('MOVI', '%cz', '0')]) + [L('H', '@bf')]
    q += C('H', [('OR', '%cy', '%cy', '%cz'), ('ANDI', '%cA', '%cu', hex(1 << 36)), ('SHL', '%bc', '%bd', '37'), ('SHL', '%aJ', '%ct', '38'), ('OR', '%bc', '%bc', '%aJ'), ('OR', '%bc', '%bc', '%cr'), ('OR', '%bc', '%bc', '%cA'), ('CALL', '@z'), ('MOV', '%ao', '%aT'), ('MOVI', '%bw', 'table_trails'), ('CALL', '@C'), ('BRZ', '@bg', '%cy'), ('ANDI', '%cr', '%cu', hex((1 << 36) - 1)), ('MOV', '%bd', '%cw'), ('MOVI', '%ct', '1'), ('MOV', '%aT', '%cv'), ('CALL', '@w'), ('BR', '@be')]) + [L('H', '@bg'), gaO('H', 'RET')]
    q += [L('H', '@t')]
    q += C('H', [('MOV', '%bn', '%cp')]) + [L('H', '@bh')]
    q += C('H', [('SUBI', '%ba', '%ba', '1'), ('BRLT', '@ac', '%ba'), ('MOV', '%bm', '%bn'), ('CALL', '@bb'), ('SHR', '%aJ', '%bc', '38'), ('BRZ', '@bi', '%aJ'), ('MOV', '%bm', '%bn'), ('CALL', '@x'), ('MOV', '%bn', '%bm'), ('BR', '@bh')]) + [L('H', '@bi')]
    q += C('H', [('MOV', '%bp', '%bn')]) + [L('H', '@bj')]
    q += C('H', [('CMP', '%ag', '%bn', '%cp'), ('BREQ', '@v', '%ag'), ('MOV', '%bm', '%bp'), ('CALL', '@w'), ('MOV', '%bp', '%bm')]) + [L('H', '@bk')]
    q += C('H', [('SUBI', '%ba', '%ba', '1'), ('BRLT', '@ac', '%ba'), ('MOV', '%bm', '%bp'), ('CALL', '@bb'), ('SHR', '%aJ', '%bc', '37'), ('ANDI', '%aJ', '%aJ', '1'), ('BRZ', '@bl', '%aJ'), ('CALL', '@w'), ('MOV', '%bp', '%bm'), ('BR', '@bk')]) + [L('H', '@bl')]
    q += C('H', [('MOV', '%bm', '%bn'), ('CALL', '@w'), ('MOV', '%bn', '%bm')])
    q += [L('H', '@u')]
    q += C('H', [('SUBI', '%ba', '%ba', '1'), ('BRLT', '@ac', '%ba'), ('MOV', '%bm', '%bn'), ('CALL', '@bb'), ('SHR', '%aJ', '%bc', '36'), ('ANDI', '%aJ', '%aJ', '1'), ('BRNZ', '@bj', '%aJ'), ('CALL', '@w'), ('MOV', '%bn', '%bm'), ('BR', '@u')])
    q += [L('H', '@v')]
    q += C('H', [('MOV', '%bo', '%bp'), ('RET',), ('HALT', 'qf_scan_bound')])
    q += [L('H', '@w')]
    q += C('H', [('ADDI', '%bm', '%bm', '1'), ('CMP', '%ag', '%bm', '116112'), ('BRLT', '@bq', '%ag'), ('MOVI', '%bm', '0')]) + [L('H', '@bq'), gaO('H', 'RET')]
    q += [L('H', '@x')]
    q += C('H', [('BRNZ', '@y', '%bm'), ('MOVI', '%bm', '116111'), ('RET',)])
    q += [L('H', '@y')]
    q += C('H', [('SUBI', '%bm', '%bm', '1'), ('RET',)]) + [L('H', '@bb')]
    q += C('H', [('SHL', '%bs', '%bm', '5'), ('SHL', '%aJ', '%bm', '2'), ('ADD', '%bs', '%bs', '%aJ'), ('SHL', '%aJ', '%bm', '1'), ('ADD', '%bs', '%bs', '%aJ'), ('ADD', '%bs', '%bs', '%bm'), ('SHR', '%aD', '%bs', '8'), ('ANDI', '%aG', '%bs', '255'), ('LOAD', '%aE', 'K[%aD]'), ('SHR', '%bc', '%aE', '%aG'), ('CMP', '%ag', '%aG', '217'), ('BRLE', '@br', '%ag'), ('ADDI', '%aD', '%aD', '1'), ('LOAD', '%cB', 'K[%aD]'), ('SUB', '%cC', '256', '%aG'), ('SHL', '%cB', '%cB', '%cC'), ('OR', '%bc', '%bc', '%cB')]) + [L('H', '@br')]
    q += C('H', [('ANDI', '%bc', '%bc', hex((1 << 39) - 1)), ('RET',)])
    q += [L('H', '@z')]
    q += C('H', [('SHL', '%bs', '%bm', '5'), ('SHL', '%aJ', '%bm', '2'), ('ADD', '%bs', '%bs', '%aJ'), ('SHL', '%aJ', '%bm', '1'), ('ADD', '%bs', '%bs', '%aJ'), ('ADD', '%bs', '%bs', '%bm'), ('SHR', '%aD', '%bs', '8'), ('ANDI', '%aG', '%bs', '255'), ('CMP', '%ag', '%aG', '217'), ('BRGT', '@A', '%ag'), ('MOVI', '%aH', hex((1 << 39) - 1)), ('SHL', '%aH', '%aH', '%aG'), ('NOT', '%aI', '%aH'), ('LOAD', '%aE', 'K[%aD]'), ('AND', '%aE', '%aE', '%aI'), ('SHL', '%aJ', '%bc', '%aG'), ('OR', '%aE', '%aE', '%aJ'), ('STORE', 'K[%aD]', '%aE'), ('RET',)])
    q += [L('H', '@A')]
    q += C('H', [('SUB', '%bt', '256', '%aG'), ('MOVI', '%aH', '1'), ('SHL', '%aH', '%aH', '%bt'), ('SUBI', '%aH', '%aH', '1'), ('AND', '%aJ', '%bc', '%aH'), ('SHL', '%aJ', '%aJ', '%aG'), ('LOAD', '%aE', 'K[%aD]'), ('MOV', '%aI', '%aH'), ('SHL', '%aI', '%aI', '%aG'), ('NOT', '%aI', '%aI'), ('AND', '%aE', '%aE', '%aI'), ('OR', '%aE', '%aE', '%aJ'), ('STORE', 'K[%aD]', '%aE'), ('ADDI', '%aD', '%aD', '1'), ('SHR', '%aJ', '%bc', '%bt'), ('SUB', '%bu', '39', '%bt'), ('MOVI', '%aH', '1'), ('SHL', '%aH', '%aH', '%bu'), ('SUBI', '%aH', '%aH', '1'), ('NOT', '%aI', '%aH'), ('LOAD', '%aE', 'K[%aD]'), ('AND', '%aE', '%aE', '%aI'), ('OR', '%aE', '%aE', '%aJ'), ('STORE', 'K[%aD]', '%aE'), ('RET',)])
    q += [L('H', '@B')]
    q += C('H', [('SHL', '%bs', '%bm', '4'), ('ADD', '%bs', '%bs', '%bm'), ('SHR', '%aD', '%bs', '8'), ('ANDI', '%aG', '%bs', '255'), ('LOAD', '%aE', 'm[%bw+%aD]'), ('SHR', '%ao', '%aE', '%aG'), ('CMP', '%ag', '%aG', '239'), ('BRLE', '@bv', '%ag'), ('ADDI', '%aD', '%aD', '1'), ('LOAD', '%cB', 'm[%bw+%aD]'), ('SUB', '%cC', '256', '%aG'), ('SHL', '%cB', '%cB', '%cC'), ('OR', '%ao', '%ao', '%cB')]) + [L('H', '@bv')]
    q += C('H', [('ANDI', '%ao', '%ao', hex((1 << 17) - 1)), ('RET',)])
    q += [L('H', '@C')]
    q += C('H', [('SHL', '%bs', '%bm', '4'), ('ADD', '%bs', '%bs', '%bm'), ('SHR', '%aD', '%bs', '8'), ('ANDI', '%aG', '%bs', '255'), ('CMP', '%ag', '%aG', '239'), ('BRGT', '@D', '%ag'), ('MOVI', '%aH', hex((1 << 17) - 1)), ('SHL', '%aH', '%aH', '%aG'), ('NOT', '%aI', '%aH'), ('LOAD', '%aE', 'm[%bw+%aD]'), ('AND', '%aE', '%aE', '%aI'), ('SHL', '%aJ', '%ao', '%aG'), ('OR', '%aE', '%aE', '%aJ'), ('STORE', 'm[%bw+%aD]', '%aE'), ('RET',)])
    q += [L('H', '@D')]
    q += C('H', [('SUB', '%bt', '256', '%aG'), ('MOVI', '%aH', '1'), ('SHL', '%aH', '%aH', '%bt'), ('SUBI', '%aH', '%aH', '1'), ('AND', '%aJ', '%ao', '%aH'), ('SHL', '%aJ', '%aJ', '%aG'), ('LOAD', '%aE', 'm[%bw+%aD]'), ('MOV', '%aI', '%aH'), ('SHL', '%aI', '%aI', '%aG'), ('NOT', '%aI', '%aI'), ('AND', '%aE', '%aE', '%aI'), ('OR', '%aE', '%aE', '%aJ'), ('STORE', 'm[%bw+%aD]', '%aE'), ('ADDI', '%aD', '%aD', '1'), ('SHR', '%aJ', '%ao', '%bt'), ('SUB', '%bu', '17', '%bt'), ('MOVI', '%aH', '1'), ('SHL', '%aH', '%aH', '%bu'), ('SUBI', '%aH', '%aH', '1'), ('NOT', '%aI', '%aH'), ('LOAD', '%aE', 'm[%bw+%aD]'), ('AND', '%aE', '%aE', '%aI'), ('OR', '%aE', '%aE', '%aJ'), ('STORE', 'm[%bw+%aD]', '%aE'), ('RET',)])
    _b += q
    _10, _14, _17, _16 = gaQ(st.qwords)
    assert _17 < gam
    _c = ['r%d' % (len(_10) + j) for j in range(8)]
    _13 = ['r%d' % x for x in _16]
    _1f = [f'%E{j}' for j in range(8)]
    _1b = [L('R', '@bx')] + _10
    _1b += C('R', [('LOAD', '%ah', 'state.random'), ('ADD', '%by', '%ah', '%bz'), ('ADD', '%bA', '%ah', '%bB'), ('MOVI', '%bC', '0'), ('MOVI', '%bD', '-1'), ('MOVI', '%bE', '-1'), ('MOVI', '%bF', '4521382095915158890012510848479'), ('STORE', 'C0[0]', '%by'), ('STORE', 'C1[0]', '%bA'), ('MOVI', '%bG', '1')])
    _1b += [L('R', '@F')]
    for j, _9 in enumerate(_c):
        _1b += C('R', [('SHR', '%cD', '%by', str(32 * j)), ('ANDI', '%cD', '%cD', hex(gS)), ('SHR', '%cE', '%bA', str(32 * j)), ('ANDI', '%cE', '%cE', hex(gS)), ('SHL', '%cE', '%cE', '36'), ('OR', _9, '%cD', '%cE')])
    _1b += [L('R', '@G')]
    _1b += C('R', [('CMP', '%ag', '%bC', '37039162129736981626982488870733198'), ('BRGE', '@ab', '%ag'), ('CALL', '@bH'), ('ADDI', '%bC', '%bC', '1')])
    for j, _20 in enumerate(_13):
        _1b.append(gaO('R', 'MOV', _1f[j], _20))
    for j, _9 in enumerate(_c):
        _1b.append(gaO('R', 'MOV', _9, _1f[j]))
    for _f in (0, 1):
        sh = str(36 * _f)
        _1b += C('R', [('SHR', '%cF', _1f[0], sh), ('ANDI', '%cF', '%cF', hex(gS)), ('XORI', '%cF', '%cF', hex(gS)), ('BRNZ', '@cJ%d' % _f, '%cF'), ('SHR', '%cG', _1f[1], sh), ('ANDI', '%cG', '%cG', hex(gS)), ('SHR', '%cH', _1f[2], sh), ('ANDI', '%cH', '%cH', hex(gS)), ('SHR', '%cI', _1f[3], sh), ('ANDI', '%cI', '%cI', hex((1 << 26) - 1)), ('SHL', '%cH', '%cH', '32'), ('SHL', '%cI', '%cI', '64'), ('OR', '%aO', '%cG', '%cH'), ('OR', '%aO', '%aO', '%cI'), ('CMP', '%ag', '%aO', '1780'), ('BRGE', '@cJ%d' % _f, '%ag'), ('CMP', '%ag', f'%cN{_f}', '-1'), ('BRNE', '@cJ%d' % _f, '%ag'), ('MOV', f'%cN{_f}', '%bC'), ('MOVI', '%aN', '0')])
        for j, _20 in enumerate(_1f):
            _1b += C('R', [('SHR', '%cM', _20, sh), ('ANDI', '%cM', '%cM', hex(gS)), ('SHL', '%cM', '%cM', str(32 * j)), ('OR', '%aN', '%aN', '%cM')])
        _1b += C('R', [('MOV', f'%cO{_f}', '%aN')])
        _1b += [L('R', '@cJ%d' % _f)]
    _1b += C('R', [('SUBI', '%bF', '%bF', '1'), ('BRNZ', '@H', '%bF'), ('MOVI', '%bF', '4521382095915158890012510848479')])
    for _f in (0, 1):
        _1b += C('R', [('MOVI', '%aN', '0')])
        for j, _20 in enumerate(_1f):
            _1b += C('R', [('SHR', '%cM', _20, str(36 * _f)), ('ANDI', '%cM', '%cM', hex(gS)), ('SHL', '%cM', '%cM', str(32 * j)), ('OR', '%aN', '%aN', '%cM')])
        _1b.append(gaO('R', 'STORE', 'C%d[%%bG]' % _f, '%aN'))
    _1b += C('R', [('ADDI', '%bG', '%bG', '1')])
    _1b += [L('R', '@H')]
    _1b += C('R', [('CMP', '%ag', '%bD', '-1'), ('BREQ', '@G', '%ag'), ('CMP', '%ag', '%bE', '-1'), ('BREQ', '@G', '%ag'), ('CMP', '%ag', '%cK', '%cL'), ('BRNE', '@ad', '%ag'), ('SUB', '%bL', '%bD', '%bE'), ('MOVI', '%bR', '0'), ('BRGE', '@bI', '%bL'), ('SUB', '%bL', '%bE', '%bD'), ('MOVI', '%bR', '1')]) + [L('R', '@bI')]
    _1b += C('R', [('MOVI', '%bT', 'C0'), ('MOVI', '%bV', 'C1'), ('BRZ', '@bJ', '%bR'), ('MOVI', '%bT', 'C1'), ('MOVI', '%bV', 'C0')]) + [L('R', '@bJ')]
    _1b += C('R', [('MOV', '%bK', '%bL'), ('CALL', '@O'), ('MOV', '%bM', '%bN'), ('MOV', '%bO', '%bP'), ('MOV', '%bQ', '%bE'), ('BRZ', '@I', '%bR'), ('MOV', '%bQ', '%bD')])
    _1b += [L('R', '@I')]
    _1b += C('R', [('LOAD', '%bS', 'm[%bT+%bM]'), ('LOAD', '%bU', 'm[%bV]'), ('MOV', '%bW', '%bO'), ('CALL', '@Q'), ('CMP', '%ag', '%bS', '%bU'), ('BREQ', '@ad', '%ag')])
    _1b += C('R', [('MOV', '%bK', '%bQ'), ('CALL', '@O'), ('MOVI', '%bX', '0'), ('ADDI', '%K', '%bN', '1')]) + [L('R', '@M')]
    _1b += C('R', [('SUB', '%aJ', '%K', '%bX'), ('CMP', '%ag', '%aJ', '1'), ('BRLE', '@N', '%ag'), ('ADD', '%L', '%K', '%bX'), ('SHR', '%L', '%L', '1'), ('ADD', '%bY', '%L', '%bM'), ('LOAD', '%bZ', 'm[%bT+%bY]'), ('LOAD', '%ca', 'm[%bV+%L]'), ('MOV', '%bS', '%bZ'), ('MOV', '%bW', '%bO'), ('CALL', '@Q'), ('CMP', '%ag', '%bS', '%ca'), ('BREQ', '@J', '%ag'), ('MOV', '%bX', '%L'), ('BR', '@M')])
    _1b += [L('R', '@J'), gaO('R', 'MOV', '%K', '%L'), gaO('R', 'BR', '@M'), L('R', '@N')]
    _1b += C('R', [('ADD', '%bY', '%bX', '%bM'), ('LOAD', '%bS', 'm[%bT+%bY]'), ('LOAD', '%bU', 'm[%bV+%bX]'), ('MOV', '%bW', '%bO'), ('CALL', '@Q'), ('MOV', '%cb', '4521382095915158890012510848479'), ('CALL', '@cc'), ('RET',)])
    _1b += [L('R', '@O')]
    _1b += C('R', [('MOVI', '%bN', '0'), ('MOVI', '%bP', '0'), ('MOVI', '%ce', '255')]) + [L('R', '@cd')]
    _1b += C('R', [('SHL', '%bP', '%bP', '1'), ('SHR', '%aM', '%bK', '%ce'), ('ANDI', '%aM', '%aM', '1'), ('OR', '%bP', '%bP', '%aM'), ('CMP', '%ag', '%bP', '4521382095915158890012510848479'), ('BRLT', '@P', '%ag'), ('SUB', '%bP', '%bP', '4521382095915158890012510848479'), ('MOVI', '%aM', '1'), ('SHL', '%aM', '%aM', '%ce'), ('OR', '%bN', '%bN', '%aM')])
    _1b += [L('R', '@P')]
    _1b += C('R', [('SUBI', '%ce', '%ce', '1'), ('BRGE', '@cd', '%ce'), ('RET',)])
    _1b += [L('R', '@Q')]
    _1b += C('R', [('CALL', '@T')]) + [L('R', '@cf')]
    _1b += C('R', [('BRZ', '@R', '%bW'), ('CALL', '@bH')])
    for j, _20 in enumerate(_13):
        _1b.append(gaO('R', 'MOV', _1f[j], _20))
    for j, _9 in enumerate(_c):
        _1b.append(gaO('R', 'MOV', _9, _1f[j]))
    _1b += C('R', [('SUBI', '%bW', '%bW', '1'), ('BR', '@cf')])
    _1b += [L('R', '@R'), gaO('R', 'CALL', '@S'), gaO('R', 'RET'), L('R', '@T')]
    for j, _9 in enumerate(_c):
        _1b += C('R', [('SHR', '%cM', '%bS', str(32 * j)), ('ANDI', _9, '%cM', hex(gS))])
    _1b += C('R', [('RET',)]) + [L('R', '@S')]
    _1b += C('R', [('MOVI', '%bS', '0')])
    for j, _20 in enumerate(_c):
        _1b += C('R', [('ANDI', '%cM', _20, hex(gS)), ('SHL', '%cM', '%cM', str(32 * j)), ('OR', '%bS', '%bS', '%cM')])
    _1b += C('R', [('RET',)]) + [L('R', '@cc')]
    _1b += C('R', [('CALL', '@V')]) + [L('R', '@cg')]
    _1b += C('R', [('BRZ', '@ab', '%cb'), ('MOV', '%ch', '%bS'), ('MOV', '%ci', '%bU'), ('CALL', '@bH'), ('MOVI', '%cj', '0')])
    for j, _20 in enumerate(_13):
        _1b.append(gaO('R', 'MOV', _1f[j], _20))
    for _20 in _1f:
        _1b += C('R', [('ANDI', '%cD', _20, hex(gS)), ('SHR', '%cE', _20, '36'), ('ANDI', '%cE', '%cE', hex(gS)), ('XOR', '%aJ', '%cD', '%cE'), ('OR', '%cj', '%cj', '%aJ')])
    _1b += C('R', [('BRZ', '@U', '%cj')])
    for j, _9 in enumerate(_c):
        _1b.append(gaO('R', 'MOV', _9, _1f[j]))
    _1b += C('R', [('CALL', '@ck')])
    _1b += C('R', [('SUBI', '%cb', '%cb', '1'), ('BR', '@cg')])
    _1b += [L('R', '@U')]
    _1b += C('R', [('CMP', '%ag', '%ch', '%ci'), ('BREQ', '@ad', '%ag'), ('MOV', '%cl', '%ch'), ('MOV', '%cm', '%ci'), ('RET',)])
    _1b += [L('R', '@V')]
    for j, _9 in enumerate(_c):
        _1b += C('R', [('SHR', '%cD', '%bS', str(32 * j)), ('ANDI', '%cD', '%cD', hex(gS)), ('SHR', '%cE', '%bU', str(32 * j)), ('ANDI', '%cE', '%cE', hex(gS)), ('SHL', '%cE', '%cE', '36'), ('OR', _9, '%cD', '%cE')])
    _1b += C('R', [('RET',)]) + [L('R', '@ck')]
    _1b += C('R', [('MOVI', '%bS', '0'), ('MOVI', '%bU', '0')])
    for j, _20 in enumerate(_c):
        _1b += C('R', [('ANDI', '%cD', _20, hex(gS)), ('SHR', '%cE', _20, '36'), ('ANDI', '%cE', '%cE', hex(gS)), ('SHL', '%cD', '%cD', str(32 * j)), ('SHL', '%cE', '%cE', str(32 * j)), ('OR', '%bS', '%bS', '%cD'), ('OR', '%bU', '%bU', '%cE')])
    _1b += C('R', [('RET',)])
    _15 = [L('P', '@bH')] + _14 + [gaO('R', 'RET')]
    _a = []
    for _23, _12 in (('@W', 'passing'), ('@X', 'hits'), ('@Y', 'full'), ('@Z', 'cut'), ('@aa', 'limit'), ('@ab', 'recovery'), ('@ac', 'qf'), ('@ad', 'alias')):
        _a += [L('halt', _23), gaO('halt', 'HALT', _12)]
    _1a = _1d + [L('loop', '@f')] + _22 + _21 + _b + _1b + _15 + _a
    _7 = sum((x[5] == gE for x in _1a))
    assert _7 <= 1335
    _1a += [gaO('Z', 'NOP') for _ in range(1335 - _7)]
    _e, pc = ({}, 0)
    for x in _1a:
        if x[1] == 'LABEL':
            _e[x[2]] = pc
        else:
            pc += 1
    _25 = {}

    def _1c(s):

        def vr(m):
            _0 = m.group(0)
            if _0 not in _25:
                _25[_0] = 'r%d' % (256 + len(_25))
            return _25[_0]
        s = re.sub('%[A-Za-z0-9_]+', vr, s)
        return str(_e[s]) if s in _e else s
    _1a = [tuple([x[0], x[1]] + [_1c(y) for y in x[2:5]] + [x[5]]) for x in _1a if x[1] != 'LABEL']
    assert 256 + len(_25) <= gam
    assert sum((x[0] in ('step', 'stage1') for x in _1a)) == st.ops + 31
    assert sum((x[0] == 'P' for x in _1a)) == gbu(st.qwords)[1]
    assert sum((x[5] == gE for x in _1a)) == 1335
    return _1a
gaI = {}

def gbz(st=None):
    st = st or gbI()
    _2 = tuple(st.qwords)
    if _2 not in gaI:
        _5 = gaN(st)
        for _4 in _5:
            for x in _4[2:5]:
                if x.startswith('r') and x[1:].isdigit():
                    assert int(x[1:]) < gam
        _3 = ''.join(('%05d|%s|%s|%s|%s|%s|%d\n' % ((j,) + x) for j, x in enumerate(_5)))
        by = {}
        for x in _5:
            by[x[0]] = by.get(x[0], 0) + 1
        gaI[_2] = dict(records=_5, listing=_3, sha256=hashlib.sha256(_3.encode()).hexdigest(), bytes=sum((x[5] for x in _5)), bitwise=sum((x[0] in ('step', 'stage1') for x in _5)), packed=sum((x[0] == 'P' for x in _5)), control=sum((x[5] == gE for x in _5)), sections=by)
    return gaI[_2]

def gbH(pa, s1):
    assert not any(pa[:s1])
    k = min(SC, s1)
    return (k, s1 - k + 9)

def gbG(pa, p, pc):
    k, _0 = (min(SC, p['s1']), gb)
    for j in range(k):
        _0 &= pa[j]
    if _0 == 0:
        return 0
    pc['passing'] += 1
    if pc['passing'] > p['pmax']:
        raise gC('stage-1 checkpoint budget')
    for j in range(k, p['s1']):
        _0 &= pa[j]
    return _0
gD = 350

def gbK(pa):
    return 32 * ((39 * pa + 255) // 256) + 32 * ((gaB * pa + 255) // 256)

def gbL(pa):
    lo, hi = (0, pa // gM)
    while lo < hi:
        _2 = (lo + hi + 1) // 2
        if gbK(_2 + 1) <= pa:
            lo = _2
        else:
            hi = _2 - 1
    return lo

def gaS(n, Tp, pc, pd, Sb):
    c = gd[n]
    s1, W = (c['s1'], c['W'])
    N, D = (1 << n, s1 + W)
    L = Fraction(1 << D, Tp)
    if n == 256:
        assert gP + pd + gf < 1 << gaB
        assert gH * 64 <= gbK(pd + 1)
        B = gaL(Tp, pd, pc, Sb)
    else:
        _e = isqrt(2 * N * gO.numerator // gO.denominator) + 2
        _a, _8 = (_e + gD * L + 1, gh.denominator)
        q = -(-(_a * _8) // (_8 - gh.numerator))
        B = -(-q // gP)
    cc = -(-pc * L.numerator // L.denominator)
    fb = (Tp - 1).bit_length()
    pk = 1 - Fraction((1 << SC) - 1, 1 << SC) ** gP
    _5 = n == 256
    return dict(n=n, s1=s1, W=W, D=D, Tp=Tp, fb=fb, kb=min(52 - fb, n - D), L=L, N=N, Q=B * gP, B=B, kappa=pc, Sb=Sb, c=cc, cr=-(-(KR * L.numerator) // L.denominator) if _5 else cc + Sb, tmax=pd, e2max=2 * B * gP // (1 << s1) + 64, pmax=-(-(1025 * B * pk.numerator) // (1024 * pk.denominator)) + 64 if _5 else 10 ** 9, cmax=gf if _5 else 10 ** 9)

def gbM(pa, k):
    return (-pa + k * (1 + log(pa / k))) / log(2)
gaJ = {}

def gbI():
    if 256 not in gaJ:
        gaJ[256] = gay(256)
    return gaJ[256]

def gbs(st=None):
    return 1335

def gbq(st=None, R=gam):
    st = st or gbI()
    ph = st.ops
    _4, _6 = gbH(st.pin, gax)
    _0 = ph + (st.spill_ops(R) if R < gam else 0) + _4 + gR
    pc = gbu(st.qwords)
    _2 = (ph + gax - 1) * go + pc[1] * gaj + gbs(st) * gE
    if R == gam:
        _1 = gbz(st)['bytes']
        assert _1 == _2
    else:
        _1 = _2
    _7 = gbL(gT - gav - _1 - R * 32 - gg - ga)
    return (ph, _4, _6, _0, _1, _7)

def gbi(pa=None):
    pa = pa or len(gbN(256)[0].nodes)
    assert pa < 1 << 16
    _0 = pa + 1
    return (_0 + gw + gr + gv + gt, _0, pa)

def gbh(pa):
    return gbK(pa + 1) + gal + gg

def gbw(pa, pb):
    _0 = gbi()[0]
    return (pa + ga + gg + gq * gu + _0, pa + ga + gg + gal + gbK(pb + 1))

def gbx(n, pb=None, Tp=None, R=gam):
    if n != 256:
        c = gd[n]
        p = gaS(n, c['Tp'], c['kappa'], 0, c['Sb'])
        p['tmax'] = 4 * (p['Q'] // int(p['L'])) + 64
        return p
    pb = pb or gG
    _9 = gbq(None, R)[5]
    if gP + _9 + gf >= 1 << gaB:
        return None
    if Tp:
        return gaS(256, Tp, pb, _9, gd[256]['Sb'])
    if _9 < 1:
        return None
    lo, hi = (1.0, float(_9 + 1))
    for _ in range(60):
        _6 = (lo + hi) / 2
        lo, hi = (_6, hi) if gbM(_6, _9 + 1) <= gaA else (lo, _6)
    ok = lambda t: gaP(t, lo, _9, pb, gd[256]['Sb'])['P_lower'] >= gad
    a, b = (1000, 4095)
    if not ok(a):
        return None
    while b - a > 1:
        _6 = (a + b) // 2
        if ok(_6):
            a = _6
        else:
            b = _6
    return gaS(256, a, pb, _9, gd[256]['Sb'])

def gbo(p=None, st=None, R=gam):
    p = p or gbx(256, None, None, R)
    st = st or gbI()
    ph, _5, _9, _1, _2, _ = gbq(st, R)
    _3 = gs * (2 * st.gen_calls + st.ops)
    pk = gbu(st.qwords)[1]
    _a = -(-p['cr'] // gH)
    _8 = p['cr'] * (pk + gag) + gH * ge + 17 * _a * (pk + gah) + 16 * gac + gak
    _4 = dict(main=_1 * (p['B'] + 3000), stage1_rest=p['pmax'] * _9, slices=-(-p['B'] // p['Sb']) * gat, stage1_hits=p['e2max'] * gB, events=p['tmax'] * (gk + gau * (p['tmax'] + 1)), cuts=p['cmax'] * gi, recovery=_8, setup=gas + _3, key_choice=gL, planner=gab)
    return dict(parts=_4, total=sum(_4.values()), plan=p, body=_1, gen=_3)

def gaP(Tp, q, pc, pd, Sb, pf=1.0, pg=20000, ph=2000):
    L = Fraction(1 << 122, Tp)
    c = -(-pd * L.numerator // L.denominator)
    th, Lf, cf, kr = (Tp / 2.0 ** 122, float(L), float(c), float(KR) * float(L))
    Q, B, Np = (q * Lf, q * Lf / gP, 2.0 ** 256 / pf)
    k = int(q) + 1
    while gbM(q, k) > -40:
        k += 1
    n2, _16 = (k + gP + 1, 1 / (1 - k * Q / Np))
    pi = lambda m: exp(-m * (m - 1) / (2 * Np))
    _17 = max(1.0, Q - 120 * gP * Lf)
    _9 = [_17 * i / ph for i in range(ph + 1)] + [_17 + (Q - _17) * i / pg for i in range(1, pg + 1)]
    _8, pa = (0.0, 1.0)
    for b in _9[1:]:
        pb = pi(b)
        _8 += (pa - pb) * exp(-th * max(0.0, B - b / gP))
        pa = pb
    p, ql, hq = (exp(-cf * th), Q * Lf / Np, Q * (Q - 1) / (2 * Np))
    p2 = exp(-(cf - 1) * th) * (1 + (cf - 1) * th / (1 - th))
    hh = (Q * (Q - 1) / 2 + 2.0 ** gaB * Q) / Np
    t = dict(collision=pi(Q) * _16, delay=_8 * _16, own_trail=ql, long_partner=(cf + Sb + 3000) * Q * p * (q + gP) / ((1 - p) * Np), age_cap=hq * p2, rec_cap=2 * hq * exp(-(kr - 1) * th) * (1 + (kr - 1) * th / (1 - th)), disturbance=hq * Lf * (Q + 2.0 ** gaB) / Np, finished_count=2.0 ** (-40), cut_halt=-expm1(n2 * log1p(-p)) - n2 * p * exp((n2 - 1) * log1p(-p)) + ql * (1 + (2 + pd) * exp(-pd / 2) + 2 * hq) + hq * p * (3 + 2 * pd), key_false_match=pc * (pc - 1) / 2 * (((1 << 52) + (1 << gaf + gan) - 1) // (1 << gaf + gan)) / ((1 << 41) * Tp), table_capacity=2.0 ** gbM(q, pc - 59), tiny=Q * 2.0 ** gaB / Np + k * k * Lf / Np + 255 * Q / Np + exp(min(700.0, -300 + (exp(5) - 1) * hh)) + 2.0 ** (-90))
    t['sum'] = sum(t.values())
    t['P_lower'] = 1 - t['sum']
    t.update(trails=q, k=k, n2=n2, p=p, p2=p2, ql=ql, hq=hq, hh=hh, shift=_16)
    return t
_B = {}

def gaL(Tp, pb, pc, Sb):
    if (Tp, pb, pc) not in _B:
        L = Fraction(1 << 122, Tp)
        B = gaa
        assert B % gy == 0 and gaP(Tp, float(B * gP / L), pb, pc, Sb)['P_lower'] >= gad
        _B[Tp, pb, pc] = B
    return _B[Tp, pb, pc]

def gbp(p, pb=1.0):
    return gaP(p['Tp'], float(p['Q'] / p['L']), p['tmax'], p['kappa'], p['Sb'], pb)

class gC(Exception):
    pass

class gl:

    def __init__(self, n):
        self.n = n
        st = gay(n)
        self.st, self.pin, self.step = (st, st.pin, st.step)

    def f2(self, xs):
        return gbv(xs, self.n, self.st.qwords)

    def g_scalar(self, x):
        return gbf(x, self.n) ^ self.st.qint

class gx:

    def __init__(self, n, salt):
        import random
        self.n, self.st, self.pin = (n, gbI(), [0] * n)
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

def gbl(x, p):
    return x & (1 << p['s1']) - 1 == (1 << p['s1']) - 1 and x >> p['s1'] & (1 << p['W']) - 1 < p['Tp']

def gbc(x, p):
    return (x >> p['D'] & (1 << p['kb']) - 1) << p['fb'] | x >> p['s1'] & (1 << p['fb']) - 1

class QF:

    def __init__(self, slots):
        self.S, self.n, self.rb = (slots, 0, gan)
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
        key &= (1 << gaf + gan) - 1
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
        assert trail < 1 << gaB and self.n < self.S - 1
        self.occ[_2], _1 = (1, (_3, trail, _0, int(x != _2)))
        while self.cont[x] or self.shf[x] or (self.occ[x] and (x != _2 or _0)):
            _1, (self.rem[x], self.tr[x], self.cont[x], self.shf[x]) = ((self.rem[x], self.tr[x], self.cont[x], 1), _1)
            x = (x + 1) % self.S
        self.rem[x], self.tr[x], self.cont[x], self.shf[x] = _1
        self.n += 1

def gbQ(xs, pb, f2):
    for _ in range(pb):
        xs = f2(xs)
    return xs

def gbA(p, r, t0, t1, f2, pf=gH):
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
                if gbl(xs[_9], p):
                    _a[_9], _4[_9] = (k, xs[_9])
        if None not in _a:
            break
    else:
        raise gC('recovery length')
    _c = 0 if _a[0] >= _a[1] else 1
    _11, (_f, _10) = (_a[1 - _c], divmod(abs(_a[0] - _a[1]), _12))
    _1 = lambda i: gbQ([_2[_c][i + _f]], _10, f2)[0]
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

def gbC(pa, p, r, pd):
    n, _6, _c = (p['n'], p['N'] - 1, pa.pin)
    _11 = QF(p['tmax'] + 1)
    _2, ts, _9 = ([0] * gP, list(range(gP)), gP)
    _d = gbt([r + t & _6 for t in ts], n, _c)
    pd['inserts'] += gP
    _1, _8 = (0, p['Sb'])
    while _1 < p['B'] + 3000:
        _d = list(pa.step(*_d))
        _1 += 1
        pd['batches'] += 1
        _b = pd['passing']
        _3 = gbG(_d, p, pd)
        _a = pd['passing'] != _b
        if _a and _1 >= p['B']:
            return None
        while _3:
            pd['stage1_hits'] += 1
            if pd['stage1_hits'] > p['e2max']:
                raise gC('stage-1 budget')
            l = (_3 & -_3).bit_length() - 1
            _3 &= _3 - 1
            x = gbm(_d, l, _c, n)
            if gbl(x, p):
                _4 = gbc(x, p)
                pd['finished'] += 1
                t0, at = _11.find(_4)
                if t0 is not None:
                    pd['recoveries'] += 1
                    _e = gbA(p, r, t0, ts[l], pa.f2)
                    if _e is None:
                        raise gC('recovery found no pair')
                    return _e
                if _11.n >= p['tmax']:
                    raise gC('table full')
                _11.put(_4, ts[l], at)
                if _11.n >= p['tmax']:
                    raise gC('table full')
                ts[l], _9, _2[l] = (_9, _9 + 1, _1)
                _d = gbF(_d, l, r + ts[l] & _6, _c, n)
                pd['inserts'] += 1
        if _a and _1 >= _8:
            _8 += p['Sb']
            for l in range(gP):
                if _1 - _2[l] >= p['c']:
                    pd['cut'] += 1
                    if pd['cut'] > p['cmax']:
                        raise gC('cut budget')
                    ts[l], _9, _2[l] = (_9, _9 + 1, _1)
                    _d = gbF(_d, l, r + ts[l] & _6, _c, n)
                    pd['inserts'] += 1
    return None

class gj(dict):

    def __missing__(self, k):
        return 0

def gba(pa, pb, pc=256):
    return int.from_bytes(hashlib.shake_256(('%s/%s' % (pa, pb)).encode()).digest((pc + 7) // 8), 'little') & (1 << pc) - 1

def gaY(pa, p, pc, pd):
    _0 = gj()
    try:
        _1 = gbC(pa, p, gba(pc, pd, p['n']), _0)
    except gC as e:
        _0['halt'] += 1
        _1 = None
    return (_1, _0)
gV = 18
gU, gc = (2048, 21)
gaz = ('w0',)

def gbd(pa, pb):
    p = gbx(gV)
    _3, _0 = gaY(pb, p, pa, 't')
    _1 = dict(target_ok=int(_3 is not None), target_batches=_0['batches'], target_halt=_0['halt'])
    if _3 is None:
        return (None, None, _1)
    return (gbr(_3[0]), gbr(_3[1]), _1)
gaG = (1 << gc) - 1

def gbJ(pa):
    return [[d & gaG for d in pa]]

def gbe(pa, tr, pc):
    _f = tr % 3
    if _f == 0:
        xs = [gba(pa, 'u%d' % i) for i in range(gU)]
    elif _f == 1:
        r = gba(pa, 'r')
        xs = [r + i & (1 << 256) - 1 for i in range(gU)]
    else:
        xs = None
    _5 = []
    if xs is not None:
        for b in range(gU // gP):
            pl = gbt(xs[b * gP:(b + 1) * gP], 256, pc.pin)
            _5 += gbn(list(pc.step(*pl)), 256, pc.pin)
    else:
        _3 = [gba(pa, 'c%d' % l) for l in range(gP)]
        xs = []
        for b in range(gU // gP):
            xs += _3
            _3 = gbn(list(pc.step(*gbt(_3, 256, pc.pin))), 256, pc.pin)
            _5 += _3
    _5 = [d ^ pc.qint for d in _5]
    _b = {'source': _f}
    _c = None
    for k, _2 in enumerate(gbJ(_5)):
        _a = gaz[k]
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
    return (gbr(_c[0]), gbr(_c[1]), _b)

def gbj(pa):
    import random
    n, _4, _1e, _d = (20, 1200, 1 << 20, 64)
    _5 = len(pa)
    if _5 < _d:
        raise ValueError('h1-law-n20 requires at least 64 trials')
    _19 = int.from_bytes(hashlib.sha256(b'b3-h1-shared-v1\x00' + b'\x00'.join((t['seed'].encode() for t in pa))).digest(), 'little')
    _8 = gx(n, _19)
    xs = [gba(t['seed'], 'h1-start', n) for t in pa[:_d]]
    _18 = gbt(xs, n, [0] * n)
    _1c = [{x} for x in xs]
    _a = [0] * _d
    _c, _f, _1 = (set(), 0, _d)
    for _1f in range(1, _4 + 1):
        _16 = xs
        _18 = list(_8.step(*_18))
        xs = gbn(_18, n, _8.pin)[:_d]
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
        _6 = random.Random(gba(str(_19), 'h1-null-%d' % index))
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

def gbg():
    _6 = QF(65569)
    _4 = (1 << gaf + gan) - 1
    _, at = _6.find(_4)
    _6.put(_4, (1 << gaB) - 1, at)
    _5 = False
    try:
        _, at = _6.find(_4 - 1)
        _6.put(_4 - 1, 1 << gaB, at)
    except AssertionError:
        _5 = True
    _, _, _, _, _3, _7 = gbq()
    _2 = gT - gav - _3 - gal - gg - ga
    assert _5 and _6.find(_4)[0] == (1 << gaB) - 1
    assert gP + _7 + gf < 1 << gaB
    assert gbK(_7 + 1) <= _2 < gbK(_7 + 2)

def gbE(pa):
    gbg()
    _5 = gbz()
    st = gbI()
    _8 = gbu(st.qwords)[1]
    _4 = (st.ops + 31) * go + _8 * gaj + 1335 * gE
    assert (_5['bytes'], _5['bitwise'], _5['packed'], _5['control']) == (_4, st.ops + 31, _8, 1335)
    _2, _7 = (pa['experiment_id'], [])
    if _2 == 'bsrho-n18':
        _3 = gl(gV)
        for t in pa['trials']:
            a, b, _6 = gbd(t['seed'], _3)
            _7.append({'trial': t['trial'], 'message_a_hex': a.hex() if a else None, 'message_b_hex': b.hex() if b else None, 'observations': _6})
    elif _2 == 'proj-prefix-w256':
        st = gbI()
        for t in pa['trials']:
            a, b, _6 = gbe(t['seed'], t['trial'], st)
            _7.append({'trial': t['trial'], 'message_a_hex': a.hex() if a else None, 'message_b_hex': b.hex() if b else None, 'observations': _6})
    elif _2 == 'h1-law-n20':
        for t, (a, b, _6) in zip(pa['trials'], gbj(pa['trials'])):
            _7.append({'trial': t['trial'], 'message_a_hex': a, 'message_b_hex': b, 'observations': _6})
    else:
        raise ValueError('unknown experiment')
    return {'schema_version': 1, 'trials': _7}
json.dump(gbE(json.load(sys.stdin)), sys.stdout)
