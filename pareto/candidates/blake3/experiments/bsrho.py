import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, log, exp, expm1, log1p
gS = 4294967295
IV = (1779033703, 3144134277, 1013904242, 2773480762, 1359893119, 2600822924, 528734635, 1541459225)
gao = 7
gaC = 1470
gX = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
gp = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15), (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
gP, gb = (256, (1 << 256) - 1)
gn = 11
gI = (2147483648, 0, 2147483648, 0, 2147483648, 0, 0, 0)
gK = sum((w << 32 * i for i, w in enumerate(gI)))
gJ = b''.join((w.to_bytes(4, 'little') for w in gI))

def gaU(v, k):
    return (v >> k | v << 32 - k) & gS

def gbc(m, rounds=gao, flags=gn, blen=64, counter=0):
    v = list(IV) + list(IV[:4]) + [counter & gS, counter >> 32, blen, flags]
    m = list(m)
    for _ in range(rounds):
        for j, (a, b, c, d) in enumerate(gp):
            x, y = (m[2 * j], m[2 * j + 1])
            v[a] = v[a] + v[b] + x & gS
            v[d] = gaU(v[d] ^ v[a], 16)
            v[c] = v[c] + v[d] & gS
            v[b] = gaU(v[b] ^ v[c], 12)
            v[a] = v[a] + v[b] + y & gS
            v[d] = gaU(v[d] ^ v[a], 8)
            v[c] = v[c] + v[d] & gS
            v[b] = gaU(v[b] ^ v[c], 7)
        m = [m[i] for i in gX]
    return [v[i] ^ v[i + 8] for i in range(8)]

def gbg(x, n, key=gK):
    kw = [key >> 32 * i & gS for i in range(8)]
    d = gbc(kw + [x >> 32 * i & gS for i in range(8)])
    return sum((d[i] << 32 * i for i in range(8))) & (1 << n) - 1

def gbs(x):
    return gJ + x.to_bytes(32, 'little')
gY, gZ = (36, 7)
gan = sum((1 << gY * i for i in range(gZ)))
gQ = 1 << gY

class gaB:

    def __init__(self):
        self.lines, self.ops, self.k = ([], 0, 0)

    def emit(self, expr):
        self.k += 1
        _0 = 't%d' % self.k
        self.lines.append('%s=%s' % (_0, expr))
        self.ops += 1
        return _0

    def mask(self, a):
        return ('v', self.emit('%s&%d' % (a[1], gan * gS)), gS)

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
            _0 = ('v', self.emit('%s+%d' % (_0[1], gan * c)), _0[2] + c)
        return _0

    def xor(self, a, b):
        if a[0] == 'c' and b[0] == 'c':
            return ('c', a[1] ^ b[1])
        if a[0] == 'c':
            a, b = (b, a)
        if b[0] == 'c':
            if b[1] == 0:
                return a
            return ('v', self.emit('%s^%d' % (a[1], gan * b[1])), (1 << max(a[2].bit_length(), b[1].bit_length())) - 1)
        return ('v', self.emit('%s^%s' % (a[1], b[1])), (1 << max(a[2].bit_length(), b[2].bit_length())) - 1)

    def ror(self, a, r):
        if a[0] == 'c':
            return ('c', gaU(a[1], r))
        s1 = self.emit('%s>>%d' % (a[1], r))
        h = self.emit('%s&%d' % (s1, gan * ((1 << 32 - r) - 1)))
        s2 = self.emit('%s<<%d' % (a[1], 32 - r))
        lw = self.emit('%s&%d' % (s2, gan * ((1 << r) - 1 << 32 - r)))
        return ('v', self.emit('%s|%s' % (h, lw)), gS)

def gba(qw):
    tr = gaB()
    v = [('c', w) for w in IV] + [('c', w) for w in IV[:4]] + [('c', 0), ('c', 0), ('c', 64), ('c', gn)]
    m = [('c', w) for w in gI] + [('v', 'i%d' % i, gS) for i in range(8, 16)]
    for _ in range(gao):
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
gaI = {}

def gbv(qw):
    qw = tuple(qw)
    if qw not in gaI:
        gaI[qw] = gba(qw)
    return gaI[qw]

def gbw(xs, n, qw):
    _4 = [sum(((x >> 32 * i & gS) << gY * l for l, x in enumerate(xs))) for i in range(8)]
    _3 = gbv(qw)[0](*_4)
    _2 = (1 << n) - 1
    return [sum(((_3[i] >> gY * l & gS) << 32 * i for i in range(8))) & _2 for l in range(len(xs))]
gaD, gW = ((0, 0), (0, 1))

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
            return gaD if x[1] == 0 else y
        if y[0] == 0:
            return gaD if y[1] == 0 else x
        if x[0] == y[0]:
            return x if x[1] == y[1] else gaD
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
            return ((x[0], x[1] ^ k), gW if k1 == k2 == 1 else gaD if k1 == k2 == 0 else x)
        kk = cs[0][1] + cs[1][1] + cs[2][1]
        return (gaD if kk % 2 == 0 else gW, gW if kk >= 2 else gaD)

    def add(self, A, B):
        s, c = ([], gaD)
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
        s, u = ([s0], gaD)
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

def gaX(*W):
    return all((any((t[0] != 0 for t in w)) for w in W))

def gaV(A, r):
    return [A[(i + r) % 32] for i in range(32)]

def gaN(v):
    return [gW if v >> i & 1 else gaD for i in range(32)]

def gbO(n):
    g = gz(n)
    _e = gaN(0)
    m = [gaN(w) for w in gI] + [[g.inputs[32 * i + b] if 32 * i + b < n else gaD for b in range(32)] for i in range(8)]
    v = [gaN(w) for w in IV] + [gaN(w) for w in IV[:4]] + [_e, _e, gaN(64), gaN(gn)]
    for _ in range(gao):
        for j, (a, b, c, d) in enumerate(gp):
            x, y = (m[2 * j], m[2 * j + 1])
            v[a] = g.add3(v[a], v[b], x) if gaX(v[a], v[b], x) else g.add(g.add(v[a], v[b]), x)
            v[d] = gaV(g.xorw(v[d], v[a]), 16)
            v[c] = g.add(v[c], v[d])
            v[b] = gaV(g.xorw(v[b], v[c]), 12)
            v[a] = g.add3(v[a], v[b], y) if gaX(v[a], v[b], y) else g.add(g.add(v[a], v[b]), y)
            v[d] = gaV(g.xorw(v[d], v[a]), 8)
            v[c] = g.add(v[c], v[d])
            v[b] = gaV(g.xorw(v[b], v[c]), 7)
        m = [m[i] for i in gX]
    return (g, [s for i in range(8) for s in g.xorw(v[i], v[i + 8])])

class gax:

    def __init__(self, n=256):
        g, _16 = gbO(n)
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

def gaY(st):
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

def gbC(st, code, planes):
    _6 = [0] * (max((c[1] for c in code)) + 1)
    _6[:st.n] = planes
    for nm, d, ra, rb in code:
        va = _6[ra] if ra >= 0 else 0
        vb = gb if st.opsym[nm][1] else _6[rb] if rb >= 0 else 0
        o = st.opsym[nm][0]
        _6[d] = va ^ vb if o == '^' else va & vb if o == '&' else va | vb
    return _6[:st.n]

def gaW():
    _2, s = ({}, 128)
    while s:
        m = 0
        for c in range(256):
            if not c & s:
                m |= 1 << c
        _2[s] = m
        s >>= 1
    return _2
gaL = gaW()

def gbP(rows):
    R = list(rows) + [0] * (256 - len(rows))
    s = 128
    while s:
        m = gaL[s]
        for i in range(256):
            if not i & s:
                t = (R[i] >> s ^ R[i + s]) & m
                R[i + s] ^= t
                R[i] ^= t << s
        s >>= 1
    return R

def gbu(xs, n, pin):
    T = gbP(xs)
    return [T[j] ^ (gb if pin[j] else 0) for j in range(n)]

def gbo(planes, n, pin):
    T = gbP([planes[j] ^ (gb if pin[j] else 0) for j in range(n)])
    return T[:256]

def gbn(planes, l, pin, n):
    x = 0
    for j in range(n):
        x |= (planes[j] >> l & 1 ^ pin[j]) << j
    return x

def gbG(planes, l, x, pin, n):
    _0 = 1 << l
    return [planes[j] & ~_0 | (x >> j & 1 ^ pin[j]) << l for j in range(n)]
gO = Fraction(497, 1000)
gh = Fraction(15, 100000)
gac = 0.390000001
gy = 10 ** 24
gf = 1
gaw, SC = (32, 12)
gR = 4
gB = 2800
gk = 3800
gat = 2048
gi = 4200
gas = 4000
KR, gH = (Fraction(62, 5), 8192)
gaf, gag = (64, 128)
ge, gab, gaj = (80, 100, 8000)
gE = 36
gai = 5
gu = 36
go = 4
gav = 0
gq = 2400
gA, gaq, gah = (625, 35, 110)
gal = 775
gak = gal * 32
gg = 5248
gaA, gm, gam, gae, gM = (17, 3, 29, 16, 4)
gT = 1048576
gau = 0
ga = 32
gaz = -40
gG = 20
gs = 200
gw = 2400
gr = 256
gv = 2048
gt = 68
gar = 256 * 3100 + 20000
gL = 241 * (1 << 28)
gaa = 1 << 40
gd = {18: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4), 20: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4), 256: dict(s1=32, W=90, kappa=gG, Sb=1 << 48)}

def gaP(section, op, d='-', a='-', b='-', size=gE):
    return (section, op, str(d), str(a), str(b), size)

def gaS(line):
    _3, _2 = line.split('=', 1)
    for op in ('<<', '>>', '&', '^', '+', '|'):
        if op in _2:
            a, b = _2.split(op, 1)
            return (_3, op, a, int(b) if b.isdigit() else b)
    raise ValueError('bad packed instruction: ' + line)

def gaR(qw):
    import heapq
    pc = gbv(qw)
    _10 = [gaS(x) for x in pc[3]]
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
        _3.append(gaP('P', {'+': 'ADD', '^': 'XOR', '&': 'AND', '|': 'OR', '<<': 'SHL', '>>': 'SHR'}[op], 'r%d' % d, 'r%d' % ra, str(rb) if op in ('<<', '>>') else 'r%d' % rb, gai))
    _b = [gaP('K', 'LOADI', 'r%d' % _5[x], x[0], hex(x[1])) for x in _4]
    assert _d <= gal
    return (_b, _3, _d, [_14[x] for x in pc[4]])

def gaO(st):
    import re
    _5, _24 = gaY(st)
    assert _24 == 773
    _22 = [gaP('step', {'^': 'XOR', '&': 'AND', '|': 'OR'}[st.opsym[n][0]], 'r%d' % d, 'r%d' % a, 'r%d' % b, go) for n, d, a, b in _5]

    def L(section, name):
        return gaP(section, 'LABEL', name, size=0)

    def C(section, rows):
        return [gaP(section, *x) for x in rows]
    _4 = '%a'
    _21 = [gaP('stage1', 'AND', _4, 'r0', 'r1', go)]
    _21 += [gaP('stage1', 'AND', _4, _4, 'r%d' % j, go) for j in range(2, SC)]
    _21 += C('S', [('BRZ', '@d', _4), ('LOAD', '%ad', 'state.passing_left'), ('SUBI', '%ad', '%ad', '1'), ('STORE', 'state.passing_left', '%ad'), ('BRLT', '@V', '%ad')])
    _21 += [gaP('stage1', 'AND', _4, _4, 'r%d' % j, go) for j in range(SC, gaw)]
    _21 += C('S', [('LOAD', '%e', 'state.batch'), ('LOAD', '%ae', 'state.next_limit'), ('CMP', '%af', '%e', '%ae'), ('BRLT', '@b', '%af'), ('CALL', '@i')])
    _21 += [L('S', '@b'), gaP('S', 'BRNZ', '@c', _4)]
    _21 += [L('loop', '@d'), gaP('loop', 'LOAD', '%e', 'state.batch'), gaP('loop', 'ADDI', '%e', '%e', '1'), gaP('loop', 'STORE', 'state.batch', '%e'), gaP('loop', 'BR', '@f')]
    _1d = [L('U', '@g')]
    _1d += C('U', [('RANDOM', '%ag'), ('MOVI', '%e', '0'), ('MOVI', '%ah', '256'), ('MOVI', '%ai', '0'), ('MOVI', '%ad', '80368537913363358574902020023491743'), ('MOVI', '%aj', '157958092292666435241699218814'), ('MOVI', '%ak', str(1 << 48)), ('MOV', '%ae', '%ak'), ('MOVI', '%al', '0'), ('STORE', 'state.random', '%ag'), ('STORE', 'state.batch', '%e'), ('STORE', 'state.next_trail', '%ah'), ('STORE', 'state.table_count', '%ai'), ('STORE', 'state.passing_left', '%ad'), ('STORE', 'state.hit_left', '%aj'), ('STORE', 'state.next_slice', '%ak'), ('STORE', 'state.next_limit', '%ae'), ('STORE', 'state.cut_count', '%al'), ('MOVI', '%am', '0')])
    _1d += [L('U', '@h')]
    _1d += C('U', [('MOV', '%an', '%am'), ('CALL', '@ao'), ('MOV', '%ap', '%e'), ('CALL', '@o'), ('ADD', '%aq', '%ag', '%am'), ('CALL', '@ar'), ('ADDI', '%am', '%am', '1'), ('CMP', '%af', '%am', '256'), ('BRLT', '@h', '%af'), ('BR', '@f')])
    _1d += [L('U', '@i')]
    _1d += C('U', [('LOAD', '%e', 'state.batch'), ('CMP', '%af', '%e', '1325048516671000000000000000000000000'), ('BRGE', '@Z', '%af'), ('CALL', '@k'), ('LOAD', '%ak', 'state.next_slice'), ('ADDI', '%ak', '%ak', str(1 << 48)), ('STORE', 'state.next_slice', '%ak'), ('MOV', '%ae', '%ak'), ('STORE', 'state.next_limit', '%ae'), ('CMP', '%af', '%ae', '1325048516671000000000000000000000000'), ('BRLE', '@j', '%af'), ('MOVI', '%ae', '1325048516671000000000000000000000000'), ('STORE', 'state.next_limit', '%ae'), ('RET',), ('HALT', 'late_limit')])
    _1d += [L('U', '@j'), gaP('U', 'RET'), L('U', '@k')]
    _1d += C('U', [('MOVI', '%am', '0')]) + [L('U', '@as')]
    _1d += C('U', [('CALL', '@at'), ('SUB', '%au', '%e', '%ap'), ('CMP', '%af', '%au', '54033658365240482638366140661802626'), ('BRLT', '@l', '%af'), ('LOAD', '%al', 'state.cut_count'), ('ADDI', '%al', '%al', '1'), ('STORE', 'state.cut_count', '%al'), ('CMP', '%af', '%al', '1'), ('BRGT', '@Y', '%af'), ('LOAD', '%ah', 'state.next_trail'), ('MOV', '%av', '%ah'), ('ADDI', '%ah', '%ah', '1'), ('STORE', 'state.next_trail', '%ah'), ('MOV', '%an', '%av'), ('CALL', '@ao'), ('MOV', '%ap', '%e'), ('CALL', '@o'), ('LOAD', '%ag', 'state.random'), ('ADD', '%aq', '%ag', '%av'), ('CALL', '@ar')])
    _1d += [L('U', '@l')]
    _1d += C('U', [('ADDI', '%am', '%am', '1'), ('CMP', '%af', '%am', '256'), ('BRLT', '@as', '%af'), ('RET',)]) + [L('U', '@ar')]
    _1d += C('U', [('MOV', '%aw', '%aq'), ('MOVI', '%ax', '0'), ('MOVI', '%ay', '1'), ('SHL', '%ay', '%ay', '%am'), ('NOT', '%az', '%ay')])
    _1d += [L('U', '@m')]
    _1d += C('U', [('SHR', '%aA', '%aw', '%ax'), ('ANDI', '%aA', '%aA', '1'), ('SHL', '%aA', '%aA', '%am'), ('LOAD', '%aB', 'R[%ax]'), ('AND', '%aB', '%aB', '%az'), ('OR', '%aB', '%aB', '%aA'), ('STORE', 'R[%ax]', '%aB'), ('ADDI', '%ax', '%ax', '1'), ('CMP', '%af', '%ax', '256'), ('BRLT', '@m', '%af'), ('RET',)])
    _1d += [L('U', '@n')]
    _1d += C('U', [('MOV', '%bl', '%am'), ('MOVI', '%bs', 'active_trails'), ('CALL', '@A'), ('RET',)]) + [L('U', '@ao')]
    _1d += C('U', [('MOV', '%bl', '%am'), ('MOVI', '%bs', 'active_trails'), ('CALL', '@B'), ('RET',)]) + [L('U', '@at')]
    _1d += C('U', [('SHR', '%aC', '%am', '1'), ('LOAD', '%aD', 'birth_words[%aC]'), ('ANDI', '%aE', '%am', '1'), ('SHL', '%aF', '%aE', '7'), ('SHR', '%ap', '%aD', '%aF'), ('ANDI', '%ap', '%ap', hex((1 << 128) - 1)), ('RET',)])
    _1d += [L('U', '@o')]
    _1d += C('U', [('SHR', '%aC', '%am', '1'), ('ANDI', '%aE', '%am', '1'), ('SHL', '%aF', '%aE', '7'), ('MOVI', '%aG', hex((1 << 128) - 1)), ('SHL', '%aG', '%aG', '%aF'), ('NOT', '%aH', '%aG'), ('LOAD', '%aD', 'birth_words[%aC]'), ('AND', '%aD', '%aD', '%aH'), ('SHL', '%aI', '%ap', '%aF'), ('OR', '%aD', '%aD', '%aI'), ('STORE', 'birth_words[%aC]', '%aD'), ('RET',)])
    _b = [L('H', '@c')]
    _b += C('H', [('MOVI', '%am', '0')]) + [L('H', '@aJ')]
    _b += C('H', [('SHR', '%aL', _4, '%am'), ('ANDI', '%aL', '%aL', '1'), ('BRZ', '@aO', '%aL'), ('LOAD', '%aj', 'state.hit_left'), ('SUBI', '%aj', '%aj', '1'), ('STORE', 'state.hit_left', '%aj'), ('BRLT', '@W', '%aj'), ('MOVI', '%aM', '0'), ('MOVI', '%ax', '32')]) + [L('H', '@aK')]
    _b += C('H', [('LOAD', '%aB', 'R[%ax]'), ('SHR', '%aL', '%aB', '%am'), ('ANDI', '%aL', '%aL', '1'), ('SHL', '%aL', '%aL', '%ax'), ('OR', '%aM', '%aM', '%aL'), ('ADDI', '%ax', '%ax', '1'), ('CMP', '%af', '%ax', '122'), ('BRLT', '@aK', '%af'), ('SHR', '%aN', '%aM', '32'), ('ANDI', '%aN', '%aN', hex((1 << 90) - 1)), ('CMP', '%af', '%aN', '1968'), ('BRGE', '@aO', '%af')])
    _b += [L('H', '@p')]
    _b += C('H', [('LOAD', '%aB', 'R[%ax]'), ('SHR', '%aL', '%aB', '%am'), ('ANDI', '%aL', '%aL', '1'), ('SHL', '%aL', '%aL', '%ax'), ('OR', '%aM', '%aM', '%aL'), ('ADDI', '%ax', '%ax', '1'), ('CMP', '%af', '%ax', '163'), ('BRLT', '@p', '%af'), ('SHR', '%aP', '%aM', '122'), ('SHL', '%aP', '%aP', '11'), ('ANDI', '%aN', '%aN', '2047'), ('OR', '%aP', '%aP', '%aN'), ('CALL', '@r'), ('BRNZ', '@q', '%aQ'), ('LOAD', '%ai', 'state.table_count'), ('CMP', '%af', '%ai', '128231'), ('BRGE', '@X', '%af'), ('CALL', '@n'), ('MOV', '%aR', '%an'), ('MOV', '%aS', '%aR'), ('CALL', '@aT'), ('ADDI', '%ai', '%ai', '1'), ('STORE', 'state.table_count', '%ai'), ('CMP', '%af', '%ai', '128231'), ('BRGE', '@X', '%af'), ('LOAD', '%ah', 'state.next_trail'), ('MOV', '%av', '%ah'), ('ADDI', '%ah', '%ah', '1'), ('STORE', 'state.next_trail', '%ah'), ('MOV', '%an', '%av'), ('CALL', '@ao'), ('MOV', '%ap', '%e'), ('CALL', '@o'), ('LOAD', '%ag', 'state.random'), ('ADD', '%aq', '%ag', '%av'), ('CALL', '@ar'), ('BR', '@aO')])
    _b += [L('H', '@q')]
    _b += C('H', [('MOV', '%bx', '%cl'), ('CALL', '@n'), ('MOV', '%bz', '%an'), ('CALL', '@bv'), ('HALT', 'recovery_returned')]) + [L('H', '@aO')]
    _b += C('H', [('ADDI', '%am', '%am', '1'), ('CMP', '%af', '%am', '256'), ('BRLT', '@aJ', '%af'), ('BR', '@d')])
    q = [L('H', '@r')]
    q += C('H', [('ANDI', '%cm', '%aP', hex((1 << 45) - 1)), ('SHR', '%cn', '%cm', '29'), ('ANDI', '%co', '%cm', hex((1 << 29) - 1)), ('MOVI', '%aZ', str(8 * 128232)), ('MOV', '%bl', '%cn'), ('CALL', '@ba'), ('SHR', '%aI', '%bb', '29'), ('ANDI', '%aI', '%aI', '1'), ('BRZ', '@aV', '%aI'), ('CALL', '@t'), ('MOV', '%bl', '%bn')]) + [L('H', '@aU')]
    q += C('H', [('SUBI', '%aZ', '%aZ', '1'), ('BRLT', '@ab', '%aZ'), ('CALL', '@ba'), ('ANDI', '%aI', '%bb', hex((1 << 29) - 1)), ('CMP', '%af', '%aI', '%co'), ('BREQ', '@aW', '%af'), ('CALL', '@w'), ('CALL', '@ba'), ('SHR', '%aI', '%bb', '30'), ('ANDI', '%aI', '%aI', '1'), ('BRNZ', '@aU', '%aI')]) + [L('H', '@aV')]
    q += C('H', [('MOVI', '%aQ', '0'), ('RET',)]) + [L('H', '@aW')]
    q += C('H', [('MOVI', '%bs', 'table_trails'), ('CALL', '@A'), ('MOV', '%cl', '%an'), ('MOVI', '%aQ', '1'), ('RET',)]) + [L('H', '@aT')]
    q += C('H', [('ANDI', '%cm', '%aP', hex((1 << 45) - 1)), ('SHR', '%cn', '%cm', '29'), ('ANDI', '%cp', '%cm', hex((1 << 29) - 1)), ('MOVI', '%aZ', str(8 * 128232)), ('MOV', '%bl', '%cn'), ('CALL', '@ba'), ('SHR', '%cq', '%bb', '29'), ('ANDI', '%cq', '%cq', '1'), ('BRNZ', '@aX', '%cq'), ('ORI', '%bb', '%bb', hex(1 << 29)), ('CALL', '@z'), ('CALL', '@t'), ('MOV', '%bl', '%bn'), ('MOVI', '%bc', '0'), ('BR', '@s')]) + [L('H', '@aX')]
    q += C('H', [('CALL', '@t'), ('MOV', '%bl', '%bn')]) + [L('H', '@aY')]
    q += C('H', [('SUBI', '%aZ', '%aZ', '1'), ('BRLT', '@ab', '%aZ'), ('CALL', '@w'), ('CALL', '@ba'), ('SHR', '%aI', '%bb', '30'), ('ANDI', '%aI', '%aI', '1'), ('BRNZ', '@aY', '%aI'), ('MOVI', '%bc', '1')])
    q += [L('H', '@s')]
    q += C('H', [('MOVI', '%cr', '1'), ('CMP', '%af', '%bl', '%cn'), ('BRNE', '@bd', '%af'), ('MOVI', '%cr', '0')]) + [L('H', '@bd')]
    q += C('H', [('SUBI', '%aZ', '%aZ', '1'), ('BRLT', '@ab', '%aZ'), ('CALL', '@ba'), ('MOV', '%cs', '%bb'), ('MOVI', '%bs', 'table_trails'), ('CALL', '@A'), ('MOV', '%ct', '%an'), ('SHR', '%cu', '%cs', '30'), ('ANDI', '%cu', '%cu', '1'), ('SHR', '%cv', '%cs', '31'), ('OR', '%cw', '%cu', '%cv'), ('SHR', '%cx', '%cs', '29'), ('ANDI', '%cx', '%cx', '1'), ('CMP', '%af', '%bl', '%cn'), ('BRNE', '@be', '%af'), ('BRNZ', '@be', '%bc'), ('MOVI', '%cx', '0')]) + [L('H', '@be')]
    q += C('H', [('OR', '%cw', '%cw', '%cx'), ('ANDI', '%cy', '%cs', hex(1 << 29)), ('SHL', '%bb', '%bc', '30'), ('SHL', '%aI', '%cr', '31'), ('OR', '%bb', '%bb', '%aI'), ('OR', '%bb', '%bb', '%cp'), ('OR', '%bb', '%bb', '%cy'), ('CALL', '@z'), ('MOV', '%an', '%aS'), ('MOVI', '%bs', 'table_trails'), ('CALL', '@B'), ('BRZ', '@bf', '%cw'), ('ANDI', '%cp', '%cs', hex((1 << 29) - 1)), ('MOV', '%bc', '%cu'), ('MOVI', '%cr', '1'), ('MOV', '%aS', '%ct'), ('CALL', '@w'), ('BR', '@bd')]) + [L('H', '@bf'), gaP('H', 'RET')]
    q += [L('H', '@t')]
    q += C('H', [('MOV', '%bm', '%cn')]) + [L('H', '@bg')]
    q += C('H', [('SUBI', '%aZ', '%aZ', '1'), ('BRLT', '@ab', '%aZ'), ('MOV', '%bl', '%bm'), ('CALL', '@ba'), ('SHR', '%aI', '%bb', '31'), ('BRZ', '@bh', '%aI'), ('MOV', '%bl', '%bm'), ('CALL', '@x'), ('MOV', '%bm', '%bl'), ('BR', '@bg')]) + [L('H', '@bh')]
    q += C('H', [('MOV', '%bo', '%bm')]) + [L('H', '@bi')]
    q += C('H', [('CMP', '%af', '%bm', '%cn'), ('BREQ', '@v', '%af'), ('MOV', '%bl', '%bo'), ('CALL', '@w'), ('MOV', '%bo', '%bl')]) + [L('H', '@bj')]
    q += C('H', [('SUBI', '%aZ', '%aZ', '1'), ('BRLT', '@ab', '%aZ'), ('MOV', '%bl', '%bo'), ('CALL', '@ba'), ('SHR', '%aI', '%bb', '30'), ('ANDI', '%aI', '%aI', '1'), ('BRZ', '@bk', '%aI'), ('CALL', '@w'), ('MOV', '%bo', '%bl'), ('BR', '@bj')]) + [L('H', '@bk')]
    q += C('H', [('MOV', '%bl', '%bm'), ('CALL', '@w'), ('MOV', '%bm', '%bl')])
    q += [L('H', '@u')]
    q += C('H', [('SUBI', '%aZ', '%aZ', '1'), ('BRLT', '@ab', '%aZ'), ('MOV', '%bl', '%bm'), ('CALL', '@ba'), ('SHR', '%aI', '%bb', '29'), ('ANDI', '%aI', '%aI', '1'), ('BRNZ', '@bi', '%aI'), ('CALL', '@w'), ('MOV', '%bm', '%bl'), ('BR', '@u')])
    q += [L('H', '@v')]
    q += C('H', [('MOV', '%bn', '%bo'), ('RET',), ('HALT', 'qf_scan_bound')])
    q += [L('H', '@w')]
    q += C('H', [('ADDI', '%bl', '%bl', '1'), ('CMP', '%af', '%bl', '128232'), ('BRLT', '@bp', '%af'), ('MOVI', '%bl', '0')]) + [L('H', '@bp'), gaP('H', 'RET')]
    q += [L('H', '@x')]
    q += C('H', [('BRNZ', '@y', '%bl'), ('MOVI', '%bl', '128231'), ('RET',)])
    q += [L('H', '@y')]
    q += C('H', [('SUBI', '%bl', '%bl', '1'), ('RET',)]) + [L('H', '@ba')]
    q += C('H', [('ANDI', '%aE', '%bl', '7'), ('SHR', '%aC', '%bl', '3'), ('LOAD', '%aD', 'K[%aC]'), ('SHL', '%aF', '%aE', '5'), ('SHR', '%bb', '%aD', '%aF'), ('ANDI', '%bb', '%bb', hex(gS)), ('RET',)])
    q += [L('H', '@z')]
    q += C('H', [('ANDI', '%aE', '%bl', '7'), ('SHR', '%aC', '%bl', '3'), ('SHL', '%aF', '%aE', '5'), ('MOVI', '%aG', hex(gS)), ('SHL', '%aG', '%aG', '%aF'), ('NOT', '%aH', '%aG'), ('LOAD', '%aD', 'K[%aC]'), ('AND', '%aD', '%aD', '%aH'), ('SHL', '%aI', '%bb', '%aF'), ('OR', '%aD', '%aD', '%aI'), ('STORE', 'K[%aC]', '%aD'), ('RET',)])
    q += [L('H', '@A')]
    q += C('H', [('SHL', '%br', '%bl', '4'), ('ADD', '%br', '%br', '%bl'), ('SHR', '%aC', '%br', '8'), ('ANDI', '%aF', '%br', '255'), ('LOAD', '%aD', 'm[%bs+%aC]'), ('SHR', '%an', '%aD', '%aF'), ('CMP', '%af', '%aF', '239'), ('BRLE', '@bq', '%af'), ('ADDI', '%aC', '%aC', '1'), ('LOAD', '%cz', 'm[%bs+%aC]'), ('SUB', '%cA', '256', '%aF'), ('SHL', '%cz', '%cz', '%cA'), ('OR', '%an', '%an', '%cz')]) + [L('H', '@bq')]
    q += C('H', [('ANDI', '%an', '%an', hex((1 << 17) - 1)), ('RET',)])
    q += [L('H', '@B')]
    q += C('H', [('SHL', '%br', '%bl', '4'), ('ADD', '%br', '%br', '%bl'), ('SHR', '%aC', '%br', '8'), ('ANDI', '%aF', '%br', '255'), ('CMP', '%af', '%aF', '239'), ('BRGT', '@C', '%af'), ('MOVI', '%aG', hex((1 << 17) - 1)), ('SHL', '%aG', '%aG', '%aF'), ('NOT', '%aH', '%aG'), ('LOAD', '%aD', 'm[%bs+%aC]'), ('AND', '%aD', '%aD', '%aH'), ('SHL', '%aI', '%an', '%aF'), ('OR', '%aD', '%aD', '%aI'), ('STORE', 'm[%bs+%aC]', '%aD'), ('RET',)])
    q += [L('H', '@C')]
    q += C('H', [('SUB', '%bt', '256', '%aF'), ('MOVI', '%aG', '1'), ('SHL', '%aG', '%aG', '%bt'), ('SUBI', '%aG', '%aG', '1'), ('AND', '%aI', '%an', '%aG'), ('SHL', '%aI', '%aI', '%aF'), ('LOAD', '%aD', 'm[%bs+%aC]'), ('MOV', '%aH', '%aG'), ('SHL', '%aH', '%aH', '%aF'), ('NOT', '%aH', '%aH'), ('AND', '%aD', '%aD', '%aH'), ('OR', '%aD', '%aD', '%aI'), ('STORE', 'm[%bs+%aC]', '%aD'), ('ADDI', '%aC', '%aC', '1'), ('SHR', '%aI', '%an', '%bt'), ('SUB', '%bu', '17', '%bt'), ('MOVI', '%aG', '1'), ('SHL', '%aG', '%aG', '%bu'), ('SUBI', '%aG', '%aG', '1'), ('NOT', '%aH', '%aG'), ('LOAD', '%aD', 'm[%bs+%aC]'), ('AND', '%aD', '%aD', '%aH'), ('OR', '%aD', '%aD', '%aI'), ('STORE', 'm[%bs+%aC]', '%aD'), ('RET',)])
    _b += q
    _10, _14, _17, _16 = gaR(st.qwords)
    assert _17 < gal
    _c = ['r%d' % (len(_10) + j) for j in range(8)]
    _13 = ['r%d' % x for x in _16]
    _1f = [f'%D{j}' for j in range(8)]
    _1b = [L('R', '@bv')] + _10
    _1b += C('R', [('LOAD', '%ag', 'state.random'), ('ADD', '%bw', '%ag', '%bx'), ('ADD', '%by', '%ag', '%bz'), ('MOVI', '%bA', '0'), ('MOVI', '%bB', '-1'), ('MOVI', '%bC', '-1'), ('MOVI', '%bD', '4089461448541149809056031153604'), ('STORE', 'C0[0]', '%bw'), ('STORE', 'C1[0]', '%by'), ('MOVI', '%bE', '1')])
    _1b += [L('R', '@E')]
    for j, _9 in enumerate(_c):
        _1b += C('R', [('SHR', '%cB', '%bw', str(32 * j)), ('ANDI', '%cB', '%cB', hex(gS)), ('SHR', '%cC', '%by', str(32 * j)), ('ANDI', '%cC', '%cC', hex(gS)), ('SHL', '%cC', '%cC', '36'), ('OR', _9, '%cB', '%cC')])
    _1b += [L('R', '@F')]
    _1b += C('R', [('CMP', '%af', '%bA', '33500868186449099235787007210317628'), ('BRGE', '@aa', '%af'), ('CALL', '@bF'), ('ADDI', '%bA', '%bA', '1')])
    for j, _20 in enumerate(_13):
        _1b.append(gaP('R', 'MOV', _1f[j], _20))
    for j, _9 in enumerate(_c):
        _1b.append(gaP('R', 'MOV', _9, _1f[j]))
    for _f in (0, 1):
        sh = str(36 * _f)
        _1b += C('R', [('SHR', '%cD', _1f[0], sh), ('ANDI', '%cD', '%cD', hex(gS)), ('XORI', '%cD', '%cD', hex(gS)), ('BRNZ', '@cH%d' % _f, '%cD'), ('SHR', '%cE', _1f[1], sh), ('ANDI', '%cE', '%cE', hex(gS)), ('SHR', '%cF', _1f[2], sh), ('ANDI', '%cF', '%cF', hex(gS)), ('SHR', '%cG', _1f[3], sh), ('ANDI', '%cG', '%cG', hex((1 << 26) - 1)), ('SHL', '%cF', '%cF', '32'), ('SHL', '%cG', '%cG', '64'), ('OR', '%aN', '%cE', '%cF'), ('OR', '%aN', '%aN', '%cG'), ('CMP', '%af', '%aN', '1968'), ('BRGE', '@cH%d' % _f, '%af'), ('CMP', '%af', f'%cL{_f}', '-1'), ('BRNE', '@cH%d' % _f, '%af'), ('MOV', f'%cL{_f}', '%bA'), ('MOVI', '%aM', '0')])
        for j, _20 in enumerate(_1f):
            _1b += C('R', [('SHR', '%cK', _20, sh), ('ANDI', '%cK', '%cK', hex(gS)), ('SHL', '%cK', '%cK', str(32 * j)), ('OR', '%aM', '%aM', '%cK')])
        _1b += C('R', [('MOV', f'%cM{_f}', '%aM')])
        _1b += [L('R', '@cH%d' % _f)]
    _1b += C('R', [('SUBI', '%bD', '%bD', '1'), ('BRNZ', '@G', '%bD'), ('MOVI', '%bD', '4089461448541149809056031153604')])
    for _f in (0, 1):
        _1b += C('R', [('MOVI', '%aM', '0')])
        for j, _20 in enumerate(_1f):
            _1b += C('R', [('SHR', '%cK', _20, str(36 * _f)), ('ANDI', '%cK', '%cK', hex(gS)), ('SHL', '%cK', '%cK', str(32 * j)), ('OR', '%aM', '%aM', '%cK')])
        _1b.append(gaP('R', 'STORE', 'C%d[%%bE]' % _f, '%aM'))
    _1b += C('R', [('ADDI', '%bE', '%bE', '1')])
    _1b += [L('R', '@G')]
    _1b += C('R', [('CMP', '%af', '%bB', '-1'), ('BREQ', '@F', '%af'), ('CMP', '%af', '%bC', '-1'), ('BREQ', '@F', '%af'), ('CMP', '%af', '%cI', '%cJ'), ('BRNE', '@ac', '%af'), ('SUB', '%bJ', '%bB', '%bC'), ('MOVI', '%bP', '0'), ('BRGE', '@bG', '%bJ'), ('SUB', '%bJ', '%bC', '%bB'), ('MOVI', '%bP', '1')]) + [L('R', '@bG')]
    _1b += C('R', [('MOVI', '%bR', 'C0'), ('MOVI', '%bT', 'C1'), ('BRZ', '@bH', '%bP'), ('MOVI', '%bR', 'C1'), ('MOVI', '%bT', 'C0')]) + [L('R', '@bH')]
    _1b += C('R', [('MOV', '%bI', '%bJ'), ('CALL', '@N'), ('MOV', '%bK', '%bL'), ('MOV', '%bM', '%bN'), ('MOV', '%bO', '%bC'), ('BRZ', '@H', '%bP'), ('MOV', '%bO', '%bB')])
    _1b += [L('R', '@H')]
    _1b += C('R', [('LOAD', '%bQ', 'm[%bR+%bK]'), ('LOAD', '%bS', 'm[%bT]'), ('MOV', '%bU', '%bM'), ('CALL', '@P'), ('CMP', '%af', '%bQ', '%bS'), ('BREQ', '@ac', '%af')])
    _1b += C('R', [('MOV', '%bI', '%bO'), ('CALL', '@N'), ('MOVI', '%bV', '0'), ('ADDI', '%J', '%bL', '1')]) + [L('R', '@L')]
    _1b += C('R', [('SUB', '%aI', '%J', '%bV'), ('CMP', '%af', '%aI', '1'), ('BRLE', '@M', '%af'), ('ADD', '%K', '%J', '%bV'), ('SHR', '%K', '%K', '1'), ('ADD', '%bW', '%K', '%bK'), ('LOAD', '%bX', 'm[%bR+%bW]'), ('LOAD', '%bY', 'm[%bT+%K]'), ('MOV', '%bQ', '%bX'), ('MOV', '%bU', '%bM'), ('CALL', '@P'), ('CMP', '%af', '%bQ', '%bY'), ('BREQ', '@I', '%af'), ('MOV', '%bV', '%K'), ('BR', '@L')])
    _1b += [L('R', '@I'), gaP('R', 'MOV', '%J', '%K'), gaP('R', 'BR', '@L'), L('R', '@M')]
    _1b += C('R', [('ADD', '%bW', '%bV', '%bK'), ('LOAD', '%bQ', 'm[%bR+%bW]'), ('LOAD', '%bS', 'm[%bT+%bV]'), ('MOV', '%bU', '%bM'), ('CALL', '@P'), ('MOV', '%bZ', '4089461448541149809056031153604'), ('CALL', '@ca'), ('RET',)])
    _1b += [L('R', '@N')]
    _1b += C('R', [('MOVI', '%bL', '0'), ('MOVI', '%bN', '0'), ('MOVI', '%cc', '255')]) + [L('R', '@cb')]
    _1b += C('R', [('SHL', '%bN', '%bN', '1'), ('SHR', '%aL', '%bI', '%cc'), ('ANDI', '%aL', '%aL', '1'), ('OR', '%bN', '%bN', '%aL'), ('CMP', '%af', '%bN', '4089461448541149809056031153604'), ('BRLT', '@O', '%af'), ('SUB', '%bN', '%bN', '4089461448541149809056031153604'), ('MOVI', '%aL', '1'), ('SHL', '%aL', '%aL', '%cc'), ('OR', '%bL', '%bL', '%aL')])
    _1b += [L('R', '@O')]
    _1b += C('R', [('SUBI', '%cc', '%cc', '1'), ('BRGE', '@cb', '%cc'), ('RET',)])
    _1b += [L('R', '@P')]
    _1b += C('R', [('CALL', '@S')]) + [L('R', '@cd')]
    _1b += C('R', [('BRZ', '@Q', '%bU'), ('CALL', '@bF')])
    for j, _20 in enumerate(_13):
        _1b.append(gaP('R', 'MOV', _1f[j], _20))
    for j, _9 in enumerate(_c):
        _1b.append(gaP('R', 'MOV', _9, _1f[j]))
    _1b += C('R', [('SUBI', '%bU', '%bU', '1'), ('BR', '@cd')])
    _1b += [L('R', '@Q'), gaP('R', 'CALL', '@R'), gaP('R', 'RET'), L('R', '@S')]
    for j, _9 in enumerate(_c):
        _1b += C('R', [('SHR', '%cK', '%bQ', str(32 * j)), ('ANDI', _9, '%cK', hex(gS))])
    _1b += C('R', [('RET',)]) + [L('R', '@R')]
    _1b += C('R', [('MOVI', '%bQ', '0')])
    for j, _20 in enumerate(_c):
        _1b += C('R', [('ANDI', '%cK', _20, hex(gS)), ('SHL', '%cK', '%cK', str(32 * j)), ('OR', '%bQ', '%bQ', '%cK')])
    _1b += C('R', [('RET',)]) + [L('R', '@ca')]
    _1b += C('R', [('CALL', '@U')]) + [L('R', '@ce')]
    _1b += C('R', [('BRZ', '@aa', '%bZ'), ('MOV', '%cf', '%bQ'), ('MOV', '%cg', '%bS'), ('CALL', '@bF'), ('MOVI', '%ch', '0')])
    for j, _20 in enumerate(_13):
        _1b.append(gaP('R', 'MOV', _1f[j], _20))
    for _20 in _1f:
        _1b += C('R', [('ANDI', '%cB', _20, hex(gS)), ('SHR', '%cC', _20, '36'), ('ANDI', '%cC', '%cC', hex(gS)), ('XOR', '%aI', '%cB', '%cC'), ('OR', '%ch', '%ch', '%aI')])
    _1b += C('R', [('BRZ', '@T', '%ch')])
    for j, _9 in enumerate(_c):
        _1b.append(gaP('R', 'MOV', _9, _1f[j]))
    _1b += C('R', [('CALL', '@ci')])
    _1b += C('R', [('SUBI', '%bZ', '%bZ', '1'), ('BR', '@ce')])
    _1b += [L('R', '@T')]
    _1b += C('R', [('CMP', '%af', '%cf', '%cg'), ('BREQ', '@ac', '%af'), ('MOV', '%cj', '%cf'), ('MOV', '%ck', '%cg'), ('RET',)])
    _1b += [L('R', '@U')]
    for j, _9 in enumerate(_c):
        _1b += C('R', [('SHR', '%cB', '%bQ', str(32 * j)), ('ANDI', '%cB', '%cB', hex(gS)), ('SHR', '%cC', '%bS', str(32 * j)), ('ANDI', '%cC', '%cC', hex(gS)), ('SHL', '%cC', '%cC', '36'), ('OR', _9, '%cB', '%cC')])
    _1b += C('R', [('RET',)]) + [L('R', '@ci')]
    _1b += C('R', [('MOVI', '%bQ', '0'), ('MOVI', '%bS', '0')])
    for j, _20 in enumerate(_c):
        _1b += C('R', [('ANDI', '%cB', _20, hex(gS)), ('SHR', '%cC', _20, '36'), ('ANDI', '%cC', '%cC', hex(gS)), ('SHL', '%cB', '%cB', str(32 * j)), ('SHL', '%cC', '%cC', str(32 * j)), ('OR', '%bQ', '%bQ', '%cB'), ('OR', '%bS', '%bS', '%cC')])
    _1b += C('R', [('RET',)])
    _15 = [L('P', '@bF')] + _14 + [gaP('R', 'RET')]
    _a = []
    for _23, _12 in (('@V', 'passing'), ('@W', 'hits'), ('@X', 'full'), ('@Y', 'cut'), ('@Z', 'limit'), ('@aa', 'recovery'), ('@ab', 'qf'), ('@ac', 'alias')):
        _a += [L('halt', _23), gaP('halt', 'HALT', _12)]
    _1a = _1d + [L('loop', '@f')] + _22 + _21 + _b + _1b + _15 + _a
    _7 = sum((x[5] == gE for x in _1a))
    assert _7 <= 1335
    _1a += [gaP('Z', 'NOP') for _ in range(1335 - _7)]
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
    assert 256 + len(_25) <= gal
    assert sum((x[5] == go for x in _1a)) == st.ops + 31
    assert sum((x[5] == gai for x in _1a)) == gbv(st.qwords)[1]
    assert sum((x[5] == gE for x in _1a)) == 1335
    return _1a
gaJ = {}

def gbA(st=None):
    st = st or gbJ()
    _2 = tuple(st.qwords)
    if _2 not in gaJ:
        _5 = gaO(st)
        for _4 in _5:
            for x in _4[2:5]:
                if x.startswith('r') and x[1:].isdigit():
                    assert int(x[1:]) < gal
        _3 = ''.join(('%05d|%s|%s|%s|%s|%s|%d\n' % ((j,) + x) for j, x in enumerate(_5)))
        by = {}
        for x in _5:
            by[x[0]] = by.get(x[0], 0) + 1
        gaJ[_2] = dict(records=_5, listing=_3, sha256=hashlib.sha256(_3.encode()).hexdigest(), bytes=sum((x[5] for x in _5)), bitwise=sum((x[5] == go for x in _5)), packed=sum((x[5] == gai for x in _5)), control=sum((x[5] == gE for x in _5)), sections=by)
    return gaJ[_2]

def gbI(pin, s1):
    assert not any(pin[:s1])
    k = min(SC, s1)
    return (k, s1 - k + 9)

def gbH(planes, p, cnt):
    k, _0 = (min(SC, p['s1']), gb)
    for j in range(k):
        _0 &= planes[j]
    if _0 == 0:
        return 0
    cnt['passing'] += 1
    if cnt['passing'] > p['pmax']:
        raise gC('stage-1 checkpoint budget')
    for j in range(k, p['s1']):
        _0 &= planes[j]
    return _0
gD = 350

def gbL(slots):
    return 32 * ((slots + 7) // 8) + 32 * ((gaA * slots + 255) // 256)

def gbM(available):
    lo, hi = (0, available // gM)
    while lo < hi:
        _2 = (lo + hi + 1) // 2
        if gbL(_2 + 1) <= available:
            lo = _2
        else:
            hi = _2 - 1
    return lo

def gaT(n, Tp, kappa, tmax, Sb):
    c = gd[n]
    s1, W = (c['s1'], c['W'])
    N, D = (1 << n, s1 + W)
    L = Fraction(1 << D, Tp)
    if n == 256:
        assert gP + tmax + gf < 1 << gaA
        assert gH * 64 <= gbL(tmax + 1)
        B = gaM(Tp, tmax, kappa, Sb)
    else:
        _e = isqrt(2 * N * gO.numerator // gO.denominator) + 2
        _a, _8 = (_e + gD * L + 1, gh.denominator)
        q = -(-(_a * _8) // (_8 - gh.numerator))
        B = -(-q // gP)
    cc = -(-kappa * L.numerator // L.denominator)
    fb = (Tp - 1).bit_length()
    pk = 1 - Fraction((1 << SC) - 1, 1 << SC) ** gP
    _5 = n == 256
    return dict(n=n, s1=s1, W=W, D=D, Tp=Tp, fb=fb, kb=min(52 - fb, n - D), L=L, N=N, Q=B * gP, B=B, kappa=kappa, Sb=Sb, c=cc, cr=-(-(KR * L.numerator) // L.denominator) if _5 else cc + Sb, tmax=tmax, e2max=2 * B * gP // (1 << s1) + 64, pmax=-(-(1025 * B * pk.numerator) // (1024 * pk.denominator)) + 64 if _5 else 10 ** 9, cmax=gf if _5 else 10 ** 9)

def gbN(mean, k):
    return (-mean + k * (1 + log(mean / k))) / log(2)
gaK = {}

def gbJ():
    if 256 not in gaK:
        gaK[256] = gax(256)
    return gaK[256]

def gbt(st=None):
    return 1335

def gbr(st=None, R=gal):
    st = st or gbJ()
    ph = st.ops
    _4, _6 = gbI(st.pin, gaw)
    _0 = ph + (st.spill_ops(R) if R < gal else 0) + _4 + gR
    pc = gbv(st.qwords)
    _2 = (ph + gaw - 1) * go + pc[1] * gai + gbt(st) * gE
    if R == gal:
        _1 = gbA(st)['bytes']
        assert _1 == _2
    else:
        _1 = _2
    _7 = gbM(gT - gau - _1 - R * 32 - gg - ga)
    return (ph, _4, _6, _0, _1, _7)

def gbj(nodes=None):
    nodes = nodes or len(gbO(256)[0].nodes)
    assert nodes < 1 << 16
    _0 = nodes + 1
    return (_0 + gw + gr + gv + gt, _0, nodes)

def gbi(tmax):
    return gbL(tmax + 1) + gak + gg

def gbx(code, tmax):
    _0 = gbj()[0]
    return (code + ga + gg + gq * gu + _0, code + ga + gg + gak + gbL(tmax + 1))

def gby(n, kappa=None, Tp=None, R=gal):
    if n != 256:
        c = gd[n]
        p = gaT(n, c['Tp'], c['kappa'], 0, c['Sb'])
        p['tmax'] = 4 * (p['Q'] // int(p['L'])) + 64
        return p
    kappa = kappa or gG
    _9 = gbr(None, R)[5]
    if gP + _9 + gf >= 1 << gaA:
        return None
    if Tp:
        return gaT(256, Tp, kappa, _9, gd[256]['Sb'])
    if _9 < 1:
        return None
    lo, hi = (1.0, float(_9 + 1))
    for _ in range(60):
        _6 = (lo + hi) / 2
        lo, hi = (_6, hi) if gbN(_6, _9 + 1) <= gaz else (lo, _6)
    ok = lambda t: gaQ(t, lo, _9, kappa, gd[256]['Sb'])['P_lower'] >= gac
    a, b = (1000, 4095)
    if not ok(a):
        return None
    while b - a > 1:
        _6 = (a + b) // 2
        if ok(_6):
            a = _6
        else:
            b = _6
    return gaT(256, a, kappa, _9, gd[256]['Sb'])

def gbp(p=None, st=None, R=gal):
    p = p or gby(256, None, None, R)
    st = st or gbJ()
    ph, _5, _9, _1, _2, _ = gbr(st, R)
    _3 = gs * (2 * st.gen_calls + st.ops)
    pk = gbv(st.qwords)[1]
    _a = -(-p['cr'] // gH)
    _8 = p['cr'] * (pk + gaf) + gH * ge + 17 * _a * (pk + gag) + 16 * gab + gaj
    _4 = dict(main=_1 * (p['B'] + 3000), stage1_rest=p['pmax'] * _9, slices=-(-p['B'] // p['Sb']) * gas, stage1_hits=p['e2max'] * gB, events=p['tmax'] * (gk + gat * (p['tmax'] + 1)), cuts=p['cmax'] * gi, recovery=_8, setup=gar + _3, key_choice=gL, planner=gaa)
    return dict(parts=_4, total=sum(_4.values()), plan=p, body=_1, gen=_3)

def gaQ(Tp, q, tmax, kappa, Sb, rate=1.0, fine=20000, coarse=2000):
    L = Fraction(1 << 122, Tp)
    c = -(-kappa * L.numerator // L.denominator)
    th, Lf, cf, kr = (Tp / 2.0 ** 122, float(L), float(c), float(KR) * float(L))
    Q, B, Np = (q * Lf, q * Lf / gP, 2.0 ** 256 / rate)
    k = int(q) + 1
    while gbN(q, k) > -40:
        k += 1
    n2, _16 = (k + gP + 1, 1 / (1 - k * Q / Np))
    pi = lambda m: exp(-m * (m - 1) / (2 * Np))
    _17 = max(1.0, Q - 120 * gP * Lf)
    _9 = [_17 * i / coarse for i in range(coarse + 1)] + [_17 + (Q - _17) * i / fine for i in range(1, fine + 1)]
    _8, pa = (0.0, 1.0)
    for b in _9[1:]:
        pb = pi(b)
        _8 += (pa - pb) * exp(-th * max(0.0, B - b / gP))
        pa = pb
    p, ql, hq = (exp(-cf * th), Q * Lf / Np, Q * (Q - 1) / (2 * Np))
    p2 = exp(-(cf - 1) * th) * (1 + (cf - 1) * th / (1 - th))
    hh = (Q * (Q - 1) / 2 + 2.0 ** gaA * Q) / Np
    t = dict(collision=pi(Q) * _16, delay=_8 * _16, own_trail=ql, long_partner=(cf + Sb + 3000) * Q * p * (q + gP) / ((1 - p) * Np), age_cap=hq * p2, rec_cap=2 * hq * exp(-(kr - 1) * th) * (1 + (kr - 1) * th / (1 - th)), disturbance=hq * Lf * (Q + 2.0 ** gaA) / Np, finished_count=2.0 ** (-40), cut_halt=-expm1(n2 * log1p(-p)) - n2 * p * exp((n2 - 1) * log1p(-p)) + ql * (1 + (2 + kappa) * exp(-kappa / 2) + 2 * hq) + hq * p * (3 + 2 * kappa), key_false_match=tmax * (tmax - 1) / 2 * (((1 << 52) + (1 << gae + gam) - 1) // (1 << gae + gam)) / ((1 << 41) * Tp), table_capacity=2.0 ** gbN(q, tmax - 59), tiny=Q * 2.0 ** gaA / Np + k * k * Lf / Np + 255 * Q / Np + exp(min(700.0, -300 + (exp(5) - 1) * hh)) + 2.0 ** (-90))
    t['sum'] = sum(t.values())
    t['P_lower'] = 1 - t['sum']
    t.update(trails=q, k=k, n2=n2, p=p, p2=p2, ql=ql, hq=hq, hh=hh, shift=_16)
    return t
_B = {}

def gaM(Tp, tmax, kappa, Sb):
    if (Tp, tmax, kappa) not in _B:
        L = Fraction(1 << 122, Tp)
        lo, hi = (1.0, float(tmax + 1))
        for _ in range(40):
            _5 = (lo + hi) / 2
            lo, hi = (lo, _5) if gaQ(Tp, _5, tmax, kappa, Sb)['P_lower'] >= gac else (_5, hi)
        B = -(-int(hi * L / gP) // gy) * gy
        B += 2 * gy
        while gaQ(Tp, float(B * gP / L), tmax, kappa, Sb)['P_lower'] < gac:
            B += gy
        _B[Tp, tmax, kappa] = B
    return _B[Tp, tmax, kappa]

def gbq(p, rate=1.0):
    return gaQ(p['Tp'], float(p['Q'] / p['L']), p['tmax'], p['kappa'], p['Sb'], rate)

class gC(Exception):
    pass

class gl:

    def __init__(self, n):
        self.n = n
        st = gax(n)
        self.st, self.pin, self.step = (st, st.pin, st.step)

    def f2(self, xs):
        return gbw(xs, self.n, self.st.qwords)

    def g_scalar(self, x):
        return gbg(x, self.n) ^ self.st.qint

class gx:

    def __init__(self, n, salt):
        import random
        self.n, self.st, self.pin = (n, gbJ(), [0] * n)
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

def gbm(x, p):
    return x & (1 << p['s1']) - 1 == (1 << p['s1']) - 1 and x >> p['s1'] & (1 << p['W']) - 1 < p['Tp']

def gbd(x, p):
    return (x >> p['D'] & (1 << p['kb']) - 1) << p['fb'] | x >> p['s1'] & (1 << p['fb']) - 1

class QF:

    def __init__(self, slots):
        self.S, self.n, self.rb = (slots, 0, gam)
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
        key &= (1 << gae + gam) - 1
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
        assert trail < 1 << gaA and self.n < self.S - 1
        self.occ[_2], _1 = (1, (_3, trail, _0, int(x != _2)))
        while self.cont[x] or self.shf[x] or (self.occ[x] and (x != _2 or _0)):
            _1, (self.rem[x], self.tr[x], self.cont[x], self.shf[x]) = ((self.rem[x], self.tr[x], self.cont[x], 1), _1)
            x = (x + 1) % self.S
        self.rem[x], self.tr[x], self.cont[x], self.shf[x] = _1
        self.n += 1

def gbR(xs, count, f2):
    for _ in range(count):
        xs = f2(xs)
    return xs

def gbB(p, r, t0, t1, f2, kchk=gH):
    _d, cr = (p['N'] - 1, p['cr'])
    _12 = -(-cr // kchk)
    xs = [r + t0 & _d, r + t1 & _d]
    _a, _4 = ([None, None], [None, None])
    _2 = [[xs[0]], [xs[1]]]
    for k in range(1, cr + 1):
        xs = f2(xs)
        for _9 in (0, 1):
            if _a[_9] is None:
                if k % _12 == 0:
                    _2[_9].append(xs[_9])
                if gbm(xs[_9], p):
                    _a[_9], _4[_9] = (k, xs[_9])
        if None not in _a:
            break
    else:
        raise gC('recovery length')
    _c = 0 if _a[0] >= _a[1] else 1
    _11, (_f, _10) = (_a[1 - _c], divmod(abs(_a[0] - _a[1]), _12))
    _1 = lambda i: gbR([_2[_c][i + _f]], _10, f2)[0]
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

def gbD(eng, p, r, cnt):
    n, _6, _c = (p['n'], p['N'] - 1, eng.pin)
    _11 = QF(p['tmax'] + 1)
    _2, ts, _9 = ([0] * gP, list(range(gP)), gP)
    _d = gbu([r + t & _6 for t in ts], n, _c)
    cnt['inserts'] += gP
    _1, _8 = (0, p['Sb'])
    while _1 < p['B'] + 3000:
        _d = list(eng.step(*_d))
        _1 += 1
        cnt['batches'] += 1
        _b = cnt['passing']
        _3 = gbH(_d, p, cnt)
        _a = cnt['passing'] != _b
        if _a and _1 >= p['B']:
            return None
        while _3:
            cnt['stage1_hits'] += 1
            if cnt['stage1_hits'] > p['e2max']:
                raise gC('stage-1 budget')
            l = (_3 & -_3).bit_length() - 1
            _3 &= _3 - 1
            x = gbn(_d, l, _c, n)
            if gbm(x, p):
                _4 = gbd(x, p)
                cnt['finished'] += 1
                t0, at = _11.find(_4)
                if t0 is not None:
                    cnt['recoveries'] += 1
                    _e = gbB(p, r, t0, ts[l], eng.f2)
                    if _e is None:
                        raise gC('recovery found no pair')
                    return _e
                if _11.n >= p['tmax']:
                    raise gC('table full')
                _11.put(_4, ts[l], at)
                if _11.n >= p['tmax']:
                    raise gC('table full')
                ts[l], _9, _2[l] = (_9, _9 + 1, _1)
                _d = gbG(_d, l, r + ts[l] & _6, _c, n)
                cnt['inserts'] += 1
        if _a and _1 >= _8:
            _8 += p['Sb']
            for l in range(gP):
                if _1 - _2[l] >= p['c']:
                    cnt['cut'] += 1
                    if cnt['cut'] > p['cmax']:
                        raise gC('cut budget')
                    ts[l], _9, _2[l] = (_9, _9 + 1, _1)
                    _d = gbG(_d, l, r + ts[l] & _6, _c, n)
                    cnt['inserts'] += 1
    return None

class gj(dict):

    def __missing__(self, k):
        return 0

def gbb(seed, tag, bits=256):
    return int.from_bytes(hashlib.shake_256(('%s/%s' % (seed, tag)).encode()).digest((bits + 7) // 8), 'little') & (1 << bits) - 1

def gaZ(eng, p, seed, tag):
    _0 = gj()
    try:
        _1 = gbD(eng, p, gbb(seed, tag, p['n']), _0)
    except gC as e:
        _0['halt'] += 1
        _1 = None
    return (_1, _0)
gV = 18
gU, gc = (2048, 21)
gay = ('w0', 'w3', 'w7', 'xor8', 'sum8', 'p01', 'p23')

def gbe(seed, eng):
    p = gby(gV)
    _3, _0 = gaZ(eng, p, seed, 't')
    _1 = dict(target_ok=int(_3 is not None), target_batches=_0['batches'], target_halt=_0['halt'])
    if _3 is None:
        return (None, None, _1)
    return (gbs(_3[0]), gbs(_3[1]), _1)
gaH = (1 << gc) - 1
gaF = sum((gaH << 32 * i for i in range(8)))
gaG = sum((1 << 32 * i for i in range(8)))

def gbK(digs):
    m = gaH
    _1 = [d ^ d >> 128 for d in digs]
    _1 = [d ^ d >> 64 for d in _1]
    return [[d & m for d in digs], [d >> 96 & m for d in digs], [d >> 224 & m for d in digs], [(d ^ d >> 32) & m for d in _1], [(d & gaF) * gaG >> 224 & m for d in digs], [(d & 2047 | (d >> 32 & 2047) << 11) & m for d in digs], [(d >> 64 & 2047 | (d >> 107 & 2047) << 11) & m for d in digs]]

def gbf(seed, tr, st256):
    _f = tr % 3
    if _f == 0:
        xs = [gbb(seed, 'u%d' % i) for i in range(gU)]
    elif _f == 1:
        r = gbb(seed, 'r')
        xs = [r + i & (1 << 256) - 1 for i in range(gU)]
    else:
        xs = None
    _5 = []
    if xs is not None:
        for b in range(gU // gP):
            pl = gbu(xs[b * gP:(b + 1) * gP], 256, st256.pin)
            _5 += gbo(list(st256.step(*pl)), 256, st256.pin)
    else:
        _3 = [gbb(seed, 'c%d' % l) for l in range(gP)]
        xs = []
        for b in range(gU // gP):
            xs += _3
            _3 = gbo(list(st256.step(*gbu(_3, 256, st256.pin))), 256, st256.pin)
            _5 += _3
    _5 = [d ^ st256.qint for d in _5]
    _b = {'source': _f}
    _c = None
    for k, _2 in enumerate(gbK(_5)):
        _a = gay[k]
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
    return (gbs(_c[0]), gbs(_c[1]), _b)

def gbk(trials):
    import random
    n, _4, _1e, _d = (20, 1200, 1 << 20, 64)
    _5 = len(trials)
    if _5 < _d:
        raise ValueError('h1-law-n20 requires at least 64 trials')
    _19 = int.from_bytes(hashlib.sha256(b'b3-h1-shared-v1\x00' + b'\x00'.join((t['seed'].encode() for t in trials))).digest(), 'little')
    _8 = gx(n, _19)
    xs = [gbb(t['seed'], 'h1-start', n) for t in trials[:_d]]
    _18 = gbu(xs, n, [0] * n)
    _1c = [{x} for x in xs]
    _a = [0] * _d
    _c, _f, _1 = (set(), 0, _d)
    for _1f in range(1, _4 + 1):
        _16 = xs
        _18 = list(_8.step(*_18))
        xs = gbo(_18, n, _8.pin)[:_d]
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
        _6 = random.Random(gbb(str(_19), 'h1-null-%d' % index))
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

def gbh():
    _6 = QF(65569)
    _4 = (1 << gae + gam) - 1
    _, at = _6.find(_4)
    _6.put(_4, (1 << gaA) - 1, at)
    _5 = False
    try:
        _, at = _6.find(_4 - 1)
        _6.put(_4 - 1, 1 << gaA, at)
    except AssertionError:
        _5 = True
    _, _, _, _, _3, _7 = gbr()
    _2 = gT - gau - _3 - gak - gg - ga
    assert _5 and _6.find(_4)[0] == (1 << gaA) - 1
    assert gP + _7 + gf < 1 << gaA
    assert gbL(_7 + 1) <= _2 < gbL(_7 + 2)

def gbF(req):
    gbh()
    _4 = gbA()
    assert (_4['bytes'], _4['bitwise'], _4['packed'], _4['control']) == (233038, 44297, 1558, 1335)
    _2, _6 = (req['experiment_id'], [])
    if _2 == 'bsrho-n18':
        _3 = gl(gV)
        for t in req['trials']:
            a, b, _5 = gbe(t['seed'], _3)
            _6.append({'trial': t['trial'], 'message_a_hex': a.hex() if a else None, 'message_b_hex': b.hex() if b else None, 'observations': _5})
    elif _2 == 'proj-prefix-w256':
        st = gbJ()
        for t in req['trials']:
            a, b, _5 = gbf(t['seed'], t['trial'], st)
            _6.append({'trial': t['trial'], 'message_a_hex': a.hex() if a else None, 'message_b_hex': b.hex() if b else None, 'observations': _5})
    elif _2 == 'h1-law-n20':
        for t, (a, b, _5) in zip(req['trials'], gbk(req['trials'])):
            _6.append({'trial': t['trial'], 'message_a_hex': a, 'message_b_hex': b, 'observations': _5})
    else:
        raise ValueError('unknown experiment')
    return {'schema_version': 1, 'trials': _6}
json.dump(gbF(json.load(sys.stdin)), sys.stdout)
