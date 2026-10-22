import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, log, exp, expm1, log1p
gU = 4294967295
IV = (1779033703, 3144134277, 1013904242, 2773480762, 1359893119, 2600822924, 528734635, 1541459225)
gas = 6
gaG = 1262
gaa = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
gp = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15), (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
gR, gb = (256, (1 << 256) - 1)
gn = 11
gK = (2147483648, 0, 2147483648, 0, 2147483648, 0, 0, 0)
gM = sum((w << 32 * i for i, w in enumerate(gK)))
gL = b''.join((w.to_bytes(4, 'little') for w in gK))

def gaW(v, k):
    return (v >> k | v << 32 - k) & gU

def gbf(m, pb=gas, pc=gn, pd=64, pe=0):
    v = list(IV) + list(IV[:4]) + [pe & gU, pe >> 32, pd, pc]
    m = list(m)
    for _ in range(pb):
        for j, (a, b, c, d) in enumerate(gp):
            x, y = (m[2 * j], m[2 * j + 1])
            v[a] = v[a] + v[b] + x & gU
            v[d] = gaW(v[d] ^ v[a], 16)
            v[c] = v[c] + v[d] & gU
            v[b] = gaW(v[b] ^ v[c], 12)
            v[a] = v[a] + v[b] + y & gU
            v[d] = gaW(v[d] ^ v[a], 8)
            v[c] = v[c] + v[d] & gU
            v[b] = gaW(v[b] ^ v[c], 7)
        m = [m[i] for i in gaa]
    return [v[i] ^ v[i + 8] for i in range(8)]

def gbj(x, n, pc=gM):
    kw = [pc >> 32 * i & gU for i in range(8)]
    d = gbf(kw + [x >> 32 * i & gU for i in range(8)])
    return sum((d[i] << 32 * i for i in range(8))) & (1 << n) - 1

def gbv(x):
    return gL + x.to_bytes(32, 'little')
gab, gac = (36, 7)
gar = sum((1 << gab * i for i in range(gac)))
gS = 1 << gab

class gaF:

    def __init__(self):
        self.lines, self.ops, self.k = ([], 0, 0)

    def emit(self, expr):
        self.k += 1
        _0 = 't%d' % self.k
        self.lines.append('%s=%s' % (_0, expr))
        self.ops += 1
        return _0

    def mask(self, a):
        return ('v', self.emit('%s&%d' % (a[1], gar * gU)), gU)

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
            _0 = ('v', self.emit('%s+%d' % (_0[1], gar * c)), _0[2] + c)
        return _0

    def xor(self, a, b):
        if a[0] == 'c' and b[0] == 'c':
            return ('c', a[1] ^ b[1])
        if a[0] == 'c':
            a, b = (b, a)
        if b[0] == 'c':
            if b[1] == 0:
                return a
            return ('v', self.emit('%s^%d' % (a[1], gar * b[1])), (1 << max(a[2].bit_length(), b[1].bit_length())) - 1)
        return ('v', self.emit('%s^%s' % (a[1], b[1])), (1 << max(a[2].bit_length(), b[2].bit_length())) - 1)

    def ror(self, a, r):
        if a[0] == 'c':
            return ('c', gaW(a[1], r))
        s1 = self.emit('%s>>%d' % (a[1], r))
        h = self.emit('%s&%d' % (s1, gar * ((1 << 32 - r) - 1)))
        s2 = self.emit('%s<<%d' % (a[1], 32 - r))
        lw = self.emit('%s&%d' % (s2, gar * ((1 << r) - 1 << 32 - r)))
        return ('v', self.emit('%s|%s' % (h, lw)), gU)

def gbd(qw):
    tr = gaF()
    v = [('c', w) for w in IV] + [('c', w) for w in IV[:4]] + [('c', 0), ('c', 0), ('c', 64), ('c', gn)]
    m = [('c', w) for w in gK] + [('v', 'i%d' % i, gU) for i in range(8, 16)]
    for _ in range(gas):
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
        m = [m[i] for i in gaa]
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
gaK = {}

def gby(qw):
    qw = tuple(qw)
    if qw not in gaK:
        gaK[qw] = gbd(qw)
    return gaK[qw]

def gbz(xs, n, qw):
    _4 = [sum(((x >> 32 * i & gU) << gab * l for l, x in enumerate(xs))) for i in range(8)]
    _3 = gby(qw)[0](*_4)
    _2 = (1 << n) - 1
    return [sum(((_3[i] >> gab * l & gU) << 32 * i for i in range(8))) & _2 for l in range(len(xs))]
gaH, gY = ((0, 0), (0, 1))

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
            return gaH if x[1] == 0 else y
        if y[0] == 0:
            return gaH if y[1] == 0 else x
        if x[0] == y[0]:
            return x if x[1] == y[1] else gaH
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
            return ((x[0], x[1] ^ k), gY if k1 == k2 == 1 else gaH if k1 == k2 == 0 else x)
        kk = cs[0][1] + cs[1][1] + cs[2][1]
        return (gaH if kk % 2 == 0 else gY, gY if kk >= 2 else gaH)

    def add(self, A, B):
        s, c = ([], gaH)
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
        s, u = ([s0], gaH)
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

def gaZ(*W):
    return all((any((t[0] != 0 for t in w)) for w in W))

def gaX(A, r):
    return [A[(i + r) % 32] for i in range(32)]

def gaP(v):
    return [gY if v >> i & 1 else gaH for i in range(32)]

def gbT(n):
    g = gB(n)
    _e = gaP(0)
    m = [gaP(w) for w in gK] + [[g.inputs[32 * i + b] if 32 * i + b < n else gaH for b in range(32)] for i in range(8)]
    v = [gaP(w) for w in IV] + [gaP(w) for w in IV[:4]] + [_e, _e, gaP(64), gaP(gn)]
    for _ in range(gas):
        for j, (a, b, c, d) in enumerate(gp):
            x, y = (m[2 * j], m[2 * j + 1])
            v[a] = g.add3(v[a], v[b], x) if gaZ(v[a], v[b], x) else g.add(g.add(v[a], v[b]), x)
            v[d] = gaX(g.xorw(v[d], v[a]), 16)
            v[c] = g.add(v[c], v[d])
            v[b] = gaX(g.xorw(v[b], v[c]), 12)
            v[a] = g.add3(v[a], v[b], y) if gaZ(v[a], v[b], y) else g.add(g.add(v[a], v[b]), y)
            v[d] = gaX(g.xorw(v[d], v[a]), 8)
            v[c] = g.add(v[c], v[d])
            v[b] = gaX(g.xorw(v[b], v[c]), 7)
        m = [m[i] for i in gaa]
    return (g, [s for i in range(8) for s in g.xorw(v[i], v[i + 8])])

class gaB:

    def __init__(self, n=256):
        g, _16 = gbT(n)
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

def gba(st):
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

def gbG(st, pb, pc):
    _6 = [0] * (max((c[1] for c in pb)) + 1)
    _6[:st.n] = pc
    for nm, d, ra, rb in pb:
        va = _6[ra] if ra >= 0 else 0
        vb = gb if st.opsym[nm][1] else _6[rb] if rb >= 0 else 0
        o = st.opsym[nm][0]
        _6[d] = va ^ vb if o == '^' else va & vb if o == '&' else va | vb
    return _6[:st.n]

def gaY():
    _2, s = ({}, 128)
    while s:
        m = 0
        for c in range(256):
            if not c & s:
                m |= 1 << c
        _2[s] = m
        s >>= 1
    return _2
gaN = gaY()

def gbU(pa):
    R = list(pa) + [0] * (256 - len(pa))
    s = 128
    while s:
        m = gaN[s]
        for i in range(256):
            if not i & s:
                t = (R[i] >> s ^ R[i + s]) & m
                R[i + s] ^= t
                R[i] ^= t << s
        s >>= 1
    return R

def gbx(xs, n, pc):
    T = gbU(xs)
    return [T[j] ^ (gb if pc[j] else 0) for j in range(n)]

def gbr(pa, n, pc):
    T = gbU([pa[j] ^ (gb if pc[j] else 0) for j in range(n)])
    return T[:256]

def gbq(pa, l, pc, n):
    x = 0
    for j in range(n):
        x |= (pa[j] >> l & 1 ^ pc[j]) << j
    return x

def gbK(pa, l, x, pd, n):
    _0 = 1 << l
    return [pa[j] & ~_0 | (x >> j & 1 ^ pd[j]) << l for j in range(n)]
gQ = Fraction(497, 1000)
gh = Fraction(15, 100000)
gag = 0.390000001
gA = 10 ** 24
gf = 1
gaz = 32
gaA = (11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 32)
gZ = Fraction(1, 256)
gT = 4
gD = 2800
gk = 3800
gaw = 2048
gi = 4200
gav = 4000
KR, gJ = (Fraction(62, 5), 8192)
gaj, gak = (64, 128)
ge, gaf, gan = (80, 100, 8000)
gG = 36
gam = 5
gu = 36
go = 4
gay = 0
gq = 2400
gC, gat, gal = (625, 35, 110)
gap = 786
gao = gap * 32
gg = 5248
gaE, gm, gaq, gai, gO = (17, 3, 36, 16, 7)
gV = 1048576
gax = 0
ga = 32
gaD = -40
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
gae = 1 << 40
gad = 1324806723946000000000000000000000000
gd = {18: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4), 20: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4), 256: dict(s1=32, W=90, kappa=gI, Sb=1 << 48)}

def gaR(pa, op, d='-', a='-', b='-', pf=gG):
    return (pa, op, str(d), str(a), str(b), pf)

def gaU(pa):
    _3, _2 = pa.split('=', 1)
    for op in ('<<', '>>', '&', '^', '+', '|'):
        if op in _2:
            a, b = _2.split(op, 1)
            return (_3, op, a, int(b) if b.isdigit() else b)
    raise ValueError('bad packed instruction: ' + pa)

def gaT(qw):
    import heapq
    pc = gby(qw)
    _10 = [gaU(x) for x in pc[3]]
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
        _3.append(gaR('P', {'+': 'ADD', '^': 'XOR', '&': 'AND', '|': 'OR', '<<': 'SHL', '>>': 'SHR'}[op], 'r%d' % d, 'r%d' % ra, str(rb) if op in ('<<', '>>') else 'r%d' % rb, gam))
    _b = [gaR('K', 'LOADI', 'r%d' % _5[x], x[0], hex(x[1])) for x in _4]
    assert _d <= gap
    return (_b, _3, _d, [_14[x] for x in pc[4]])

def gaQ(st):
    import re
    _5, _30 = gba(st)
    assert _30 == 773
    _7 = gad + 3000
    _20 = 3001
    _b = _7 - (1 << 48) + 1
    _2a = gbM(gaz)
    _2b = gbA(gad, gaz)
    _1d = ['%%d%d' % _e for _e in range(len(_2b))]
    _1f = {'%b': 'r773', '%c': 'r774'}
    _1f.update({_16: 'r%d' % (775 + _e) for _e, _16 in enumerate(_1d)})
    _2d = [gaR('step', {'^': 'XOR', '&': 'AND', '|': 'OR'}[st.opsym[n][0]], 'r%d' % d, 'r%d' % a, 'r%d' % b, go) for n, d, a, b in _5]

    def L(section, name):
        return gaR(section, 'LABEL', name, pf=0)

    def C(section, rows):
        return [gaR(section, *x) for x in rows]
    _4 = '%a'
    _29 = [gaR('stage1', 'AND', _4, 'r0', 'r1', go)]
    _29 += [gaR('stage1', 'AND', _4, _4, 'r%d' % j, go) for j in range(2, _2a[0])]
    _29 += C('S', [('BRZ', '@e', _4)])
    for _e, (_2c, _2e) in enumerate(zip(_2a, _2a[1:])):
        _29 += C('S', [('SUBI', _1d[_e], _1d[_e], '1'), ('BRLT', '@X', _1d[_e])])
        if _e == 0:
            _29 += C('S', [('CMP', '%aq', '%b', '%c'), ('BRGT', '@cl', '%aq'), ('CALL', '@i')])
            _29 += [L('S', '@cl')]
        _29 += [gaR('stage1', 'AND', _4, _4, 'r%d' % j, go) for j in range(_2c, _2e)]
        _29 += [gaR('S', 'BRZ' if _2e < gaz else 'BRNZ', '@e' if _2e < gaz else '@p', _4)]
    _29 += [L('loop', '@e'), gaR('loop', 'LOAD', '%b', 'state.left'), gaR('loop', 'SUBI', '%b', '%b', '1'), gaR('loop', 'STORE', 'state.left', '%b'), gaR('loop', 'BRNZ', '@f', '%b'), gaR('loop', 'HALT', 'batch_limit')]
    _25 = [L('U', '@g')]
    _25 += C('U', [('RANDOM', '%af'), ('MOVI', '%b', str(_7)), ('MOVI', '%ag', '256'), ('MOVI', '%ah', '0'), ('MOVI', '%ai', '157929268353700637817382812564'), ('MOVI', '%c', str(_b)), ('MOVI', '%aj', '0'), ('STORE', 'state.random', '%af'), ('STORE', 'state.left', '%b'), ('STORE', 'state.next_trail', '%ag'), ('STORE', 'state.table_count', '%ah'), ('STORE', 'state.hit_left', '%ai'), ('STORE', 'state.cut_count', '%aj'), ('MOVI', '%ak', '0')])
    _25 += [gaR('U', 'MOVI', _16, str(_13)) for _16, _13 in zip(_1d, _2b)]
    _25 += [L('U', '@h')]
    _25 += C('U', [('MOV', '%al', '%ak'), ('CALL', '@am'), ('MOVI', '%an', str(_7 + 1)), ('CALL', '@o'), ('ADD', '%ao', '%af', '%ak'), ('CALL', '@ap'), ('ADDI', '%ak', '%ak', '1'), ('CMP', '%aq', '%ak', '256'), ('BRLT', '@h', '%aq'), ('BR', '@f')])
    _25 += [L('U', '@i')]
    _25 += C('U', [('CMP', '%aq', '%b', str(_20)), ('BRLE', '@ab', '%aq'), ('CALL', '@k'), ('SUBI', '%c', '%c', str(1 << 48)), ('CMP', '%aq', '%c', str(_20)), ('BRGE', '@j', '%aq'), ('MOVI', '%c', str(_20)), ('RET',)])
    _25 += [L('U', '@j'), gaR('U', 'RET'), L('U', '@k')]
    _25 += C('U', [('MOVI', '%ak', '0')]) + [L('U', '@ar')]
    _25 += C('U', [('CALL', '@as'), ('SUB', '%at', '%an', '%b'), ('CMP', '%aq', '%at', '59640067113176259019800653293565657'), ('BRLT', '@l', '%aq'), ('LOAD', '%aj', 'state.cut_count'), ('ADDI', '%aj', '%aj', '1'), ('STORE', 'state.cut_count', '%aj'), ('CMP', '%aq', '%aj', '1'), ('BRGT', '@aa', '%aq'), ('LOAD', '%ag', 'state.next_trail'), ('MOV', '%au', '%ag'), ('ADDI', '%ag', '%ag', '1'), ('STORE', 'state.next_trail', '%ag'), ('MOV', '%al', '%au'), ('CALL', '@am'), ('MOV', '%an', '%b'), ('CALL', '@o'), ('LOAD', '%af', 'state.random'), ('ADD', '%ao', '%af', '%au'), ('CALL', '@ap')])
    _25 += [L('U', '@l')]
    _25 += C('U', [('ADDI', '%ak', '%ak', '1'), ('CMP', '%aq', '%ak', '256'), ('BRLT', '@ar', '%aq'), ('RET',)]) + [L('U', '@ap')]
    _25 += C('U', [('MOV', '%av', '%ao'), ('MOVI', '%aw', '0'), ('MOVI', '%ax', '1'), ('SHL', '%ax', '%ax', '%ak'), ('NOT', '%ay', '%ax')])
    _25 += [L('U', '@m')]
    _25 += C('U', [('SHR', '%az', '%av', '%aw'), ('ANDI', '%az', '%az', '1'), ('SHL', '%az', '%az', '%ak'), ('LOAD', '%aA', 'R[%aw]'), ('AND', '%aA', '%aA', '%ay'), ('OR', '%aA', '%aA', '%az'), ('STORE', 'R[%aw]', '%aA'), ('ADDI', '%aw', '%aw', '1'), ('CMP', '%aq', '%aw', '256'), ('BRLT', '@m', '%aq'), ('RET',)])
    _25 += [L('U', '@n')]
    _25 += C('U', [('MOV', '%bk', '%ak'), ('MOVI', '%bu', 'active_trails'), ('CALL', '@C'), ('RET',)]) + [L('U', '@am')]
    _25 += C('U', [('MOV', '%bk', '%ak'), ('MOVI', '%bu', 'active_trails'), ('CALL', '@D'), ('RET',)]) + [L('U', '@as')]
    _25 += C('U', [('SHR', '%aB', '%ak', '1'), ('LOAD', '%aC', 'birth_words[%aB]'), ('ANDI', '%aD', '%ak', '1'), ('SHL', '%aE', '%aD', '7'), ('SHR', '%an', '%aC', '%aE'), ('ANDI', '%an', '%an', hex((1 << 128) - 1)), ('RET',)])
    _25 += [L('U', '@o')]
    _25 += C('U', [('SHR', '%aB', '%ak', '1'), ('ANDI', '%aD', '%ak', '1'), ('SHL', '%aE', '%aD', '7'), ('MOVI', '%aF', hex((1 << 128) - 1)), ('SHL', '%aF', '%aF', '%aE'), ('NOT', '%aG', '%aF'), ('LOAD', '%aC', 'birth_words[%aB]'), ('AND', '%aC', '%aC', '%aG'), ('SHL', '%aH', '%an', '%aE'), ('OR', '%aC', '%aC', '%aH'), ('STORE', 'birth_words[%aB]', '%aC'), ('RET',)])
    _d = [L('H', '@p')]
    _d += C('H', [('MOVI', '%ak', '0')]) + [L('H', '@aI')]
    _d += C('H', [('SHR', '%aK', _4, '%ak'), ('ANDI', '%aK', '%aK', '1'), ('BRZ', '@aN', '%aK'), ('LOAD', '%ai', 'state.hit_left'), ('SUBI', '%ai', '%ai', '1'), ('STORE', 'state.hit_left', '%ai'), ('BRLT', '@Y', '%ai'), ('MOVI', '%aL', '0'), ('MOVI', '%aw', '32')]) + [L('H', '@aJ')]
    _d += C('H', [('LOAD', '%aA', 'R[%aw]'), ('SHR', '%aK', '%aA', '%ak'), ('ANDI', '%aK', '%aK', '1'), ('SHL', '%aK', '%aK', '%aw'), ('OR', '%aL', '%aL', '%aK'), ('ADDI', '%aw', '%aw', '1'), ('CMP', '%aq', '%aw', '122'), ('BRLT', '@aJ', '%aq'), ('SHR', '%aM', '%aL', '32'), ('ANDI', '%aM', '%aM', hex((1 << 90) - 1)), ('CMP', '%aq', '%aM', '1783'), ('BRGE', '@aN', '%aq')])
    _d += [L('H', '@q')]
    _d += C('H', [('LOAD', '%aA', 'R[%aw]'), ('SHR', '%aK', '%aA', '%ak'), ('ANDI', '%aK', '%aK', '1'), ('SHL', '%aK', '%aK', '%aw'), ('OR', '%aL', '%aL', '%aK'), ('ADDI', '%aw', '%aw', '1'), ('CMP', '%aq', '%aw', '163'), ('BRLT', '@q', '%aq'), ('SHR', '%aO', '%aL', '122'), ('SHL', '%aO', '%aO', '11'), ('ANDI', '%aM', '%aM', '2047'), ('OR', '%aO', '%aO', '%aM'), ('CALL', '@s'), ('BRNZ', '@r', '%aP'), ('LOAD', '%ah', 'state.table_count'), ('CMP', '%aq', '%ah', '116282'), ('BRGE', '@Z', '%aq'), ('CALL', '@n'), ('MOV', '%aQ', '%al'), ('MOV', '%aR', '%aQ'), ('CALL', '@aS'), ('ADDI', '%ah', '%ah', '1'), ('STORE', 'state.table_count', '%ah'), ('CMP', '%aq', '%ah', '116282'), ('BRGE', '@Z', '%aq'), ('LOAD', '%ag', 'state.next_trail'), ('MOV', '%au', '%ag'), ('ADDI', '%ag', '%ag', '1'), ('STORE', 'state.next_trail', '%ag'), ('MOV', '%al', '%au'), ('CALL', '@am'), ('MOV', '%an', '%b'), ('CALL', '@o'), ('LOAD', '%af', 'state.random'), ('ADD', '%ao', '%af', '%au'), ('CALL', '@ap'), ('BR', '@aN')])
    _d += [L('H', '@r')]
    _d += C('H', [('MOV', '%bx', '%cm'), ('CALL', '@n'), ('MOV', '%bz', '%al'), ('CALL', '@bv'), ('HALT', 'recovery_returned')]) + [L('H', '@aN')]
    _d += C('H', [('ADDI', '%ak', '%ak', '1'), ('CMP', '%aq', '%ak', '256'), ('BRLT', '@aI', '%aq'), ('BR', '@e')])
    q = [L('H', '@s')]
    q += C('H', [('ANDI', '%cn', '%aO', hex((1 << 52) - 1)), ('SHR', '%co', '%cn', '36'), ('ANDI', '%cp', '%cn', hex((1 << 36) - 1)), ('MOVI', '%aY', str(8 * 116283)), ('MOV', '%bk', '%co'), ('CALL', '@aZ'), ('SHR', '%aH', '%ba', '36'), ('ANDI', '%aH', '%aH', '1'), ('BRZ', '@aU', '%aH'), ('CALL', '@u'), ('MOV', '%bk', '%bm')]) + [L('H', '@aT')]
    q += C('H', [('SUBI', '%aY', '%aY', '1'), ('BRLT', '@ad', '%aY'), ('CALL', '@aZ'), ('ANDI', '%aH', '%ba', hex((1 << 36) - 1)), ('CMP', '%aq', '%aH', '%cp'), ('BREQ', '@aV', '%aq'), ('CALL', '@x'), ('CALL', '@aZ'), ('SHR', '%aH', '%ba', '37'), ('ANDI', '%aH', '%aH', '1'), ('BRNZ', '@aT', '%aH')]) + [L('H', '@aU')]
    q += C('H', [('MOVI', '%aP', '0'), ('RET',)]) + [L('H', '@aV')]
    q += C('H', [('MOVI', '%bu', 'table_trails'), ('CALL', '@C'), ('MOV', '%cm', '%al'), ('MOVI', '%aP', '1'), ('RET',)]) + [L('H', '@aS')]
    q += C('H', [('ANDI', '%cn', '%aO', hex((1 << 52) - 1)), ('SHR', '%co', '%cn', '36'), ('ANDI', '%cq', '%cn', hex((1 << 36) - 1)), ('MOVI', '%aY', str(8 * 116283)), ('MOV', '%bk', '%co'), ('CALL', '@aZ'), ('SHR', '%cr', '%ba', '36'), ('ANDI', '%cr', '%cr', '1'), ('BRNZ', '@aW', '%cr'), ('ORI', '%ba', '%ba', hex(1 << 36)), ('CALL', '@A'), ('CALL', '@u'), ('MOV', '%bk', '%bm'), ('MOVI', '%bb', '0'), ('BR', '@t')]) + [L('H', '@aW')]
    q += C('H', [('CALL', '@u'), ('MOV', '%bk', '%bm')]) + [L('H', '@aX')]
    q += C('H', [('SUBI', '%aY', '%aY', '1'), ('BRLT', '@ad', '%aY'), ('CALL', '@x'), ('CALL', '@aZ'), ('SHR', '%aH', '%ba', '37'), ('ANDI', '%aH', '%aH', '1'), ('BRNZ', '@aX', '%aH'), ('MOVI', '%bb', '1')])
    q += [L('H', '@t')]
    q += C('H', [('MOVI', '%cs', '1'), ('CMP', '%aq', '%bk', '%co'), ('BRNE', '@bc', '%aq'), ('MOVI', '%cs', '0')]) + [L('H', '@bc')]
    q += C('H', [('SUBI', '%aY', '%aY', '1'), ('BRLT', '@ad', '%aY'), ('CALL', '@aZ'), ('MOV', '%ct', '%ba'), ('MOVI', '%bu', 'table_trails'), ('CALL', '@C'), ('MOV', '%cu', '%al'), ('SHR', '%cv', '%ct', '37'), ('ANDI', '%cv', '%cv', '1'), ('SHR', '%cw', '%ct', '38'), ('OR', '%cx', '%cv', '%cw'), ('SHR', '%cy', '%ct', '36'), ('ANDI', '%cy', '%cy', '1'), ('CMP', '%aq', '%bk', '%co'), ('BRNE', '@bd', '%aq'), ('BRNZ', '@bd', '%bb'), ('MOVI', '%cy', '0')]) + [L('H', '@bd')]
    q += C('H', [('OR', '%cx', '%cx', '%cy'), ('ANDI', '%cz', '%ct', hex(1 << 36)), ('SHL', '%ba', '%bb', '37'), ('SHL', '%aH', '%cs', '38'), ('OR', '%ba', '%ba', '%aH'), ('OR', '%ba', '%ba', '%cq'), ('OR', '%ba', '%ba', '%cz'), ('CALL', '@A'), ('MOV', '%al', '%aR'), ('MOVI', '%bu', 'table_trails'), ('CALL', '@D'), ('BRZ', '@be', '%cx'), ('ANDI', '%cq', '%ct', hex((1 << 36) - 1)), ('MOV', '%bb', '%cv'), ('MOVI', '%cs', '1'), ('MOV', '%aR', '%cu'), ('CALL', '@x'), ('BR', '@bc')]) + [L('H', '@be'), gaR('H', 'RET')]
    q += [L('H', '@u')]
    q += C('H', [('MOV', '%bl', '%co')]) + [L('H', '@bf')]
    q += C('H', [('SUBI', '%aY', '%aY', '1'), ('BRLT', '@ad', '%aY'), ('MOV', '%bk', '%bl'), ('CALL', '@aZ'), ('SHR', '%aH', '%ba', '38'), ('BRZ', '@bg', '%aH'), ('MOV', '%bk', '%bl'), ('CALL', '@y'), ('MOV', '%bl', '%bk'), ('BR', '@bf')]) + [L('H', '@bg')]
    q += C('H', [('MOV', '%bn', '%bl')]) + [L('H', '@bh')]
    q += C('H', [('CMP', '%aq', '%bl', '%co'), ('BREQ', '@w', '%aq'), ('MOV', '%bk', '%bn'), ('CALL', '@x'), ('MOV', '%bn', '%bk')]) + [L('H', '@bi')]
    q += C('H', [('SUBI', '%aY', '%aY', '1'), ('BRLT', '@ad', '%aY'), ('MOV', '%bk', '%bn'), ('CALL', '@aZ'), ('SHR', '%aH', '%ba', '37'), ('ANDI', '%aH', '%aH', '1'), ('BRZ', '@bj', '%aH'), ('CALL', '@x'), ('MOV', '%bn', '%bk'), ('BR', '@bi')]) + [L('H', '@bj')]
    q += C('H', [('MOV', '%bk', '%bl'), ('CALL', '@x'), ('MOV', '%bl', '%bk')])
    q += [L('H', '@v')]
    q += C('H', [('SUBI', '%aY', '%aY', '1'), ('BRLT', '@ad', '%aY'), ('MOV', '%bk', '%bl'), ('CALL', '@aZ'), ('SHR', '%aH', '%ba', '36'), ('ANDI', '%aH', '%aH', '1'), ('BRNZ', '@bh', '%aH'), ('CALL', '@x'), ('MOV', '%bl', '%bk'), ('BR', '@v')])
    q += [L('H', '@w')]
    q += C('H', [('MOV', '%bm', '%bn'), ('RET',), ('HALT', 'qf_scan_bound')])
    q += [L('H', '@x')]
    q += C('H', [('ADDI', '%bk', '%bk', '1'), ('CMP', '%aq', '%bk', '116283'), ('BRLT', '@bo', '%aq'), ('MOVI', '%bk', '0')]) + [L('H', '@bo'), gaR('H', 'RET')]
    q += [L('H', '@y')]
    q += C('H', [('BRNZ', '@z', '%bk'), ('MOVI', '%bk', '116282'), ('RET',)])
    q += [L('H', '@z')]
    q += C('H', [('SUBI', '%bk', '%bk', '1'), ('RET',)]) + [L('H', '@aZ')]
    q += C('H', [('SHL', '%bq', '%bk', '5'), ('SHL', '%aH', '%bk', '2'), ('ADD', '%bq', '%bq', '%aH'), ('SHL', '%aH', '%bk', '1'), ('ADD', '%bq', '%bq', '%aH'), ('ADD', '%bq', '%bq', '%bk'), ('SHR', '%aB', '%bq', '8'), ('ANDI', '%aE', '%bq', '255'), ('LOAD', '%aC', 'K[%aB]'), ('SHR', '%ba', '%aC', '%aE'), ('CMP', '%aq', '%aE', '217'), ('BRLE', '@bp', '%aq'), ('ADDI', '%aB', '%aB', '1'), ('LOAD', '%cA', 'K[%aB]'), ('SUB', '%cB', '256', '%aE'), ('SHL', '%cA', '%cA', '%cB'), ('OR', '%ba', '%ba', '%cA')]) + [L('H', '@bp')]
    q += C('H', [('ANDI', '%ba', '%ba', hex((1 << 39) - 1)), ('RET',)])
    q += [L('H', '@A')]
    q += C('H', [('SHL', '%bq', '%bk', '5'), ('SHL', '%aH', '%bk', '2'), ('ADD', '%bq', '%bq', '%aH'), ('SHL', '%aH', '%bk', '1'), ('ADD', '%bq', '%bq', '%aH'), ('ADD', '%bq', '%bq', '%bk'), ('SHR', '%aB', '%bq', '8'), ('ANDI', '%aE', '%bq', '255'), ('CMP', '%aq', '%aE', '217'), ('BRGT', '@B', '%aq'), ('MOVI', '%aF', hex((1 << 39) - 1)), ('SHL', '%aF', '%aF', '%aE'), ('NOT', '%aG', '%aF'), ('LOAD', '%aC', 'K[%aB]'), ('AND', '%aC', '%aC', '%aG'), ('SHL', '%aH', '%ba', '%aE'), ('OR', '%aC', '%aC', '%aH'), ('STORE', 'K[%aB]', '%aC'), ('RET',)])
    q += [L('H', '@B')]
    q += C('H', [('SUB', '%br', '256', '%aE'), ('MOVI', '%aF', '1'), ('SHL', '%aF', '%aF', '%br'), ('SUBI', '%aF', '%aF', '1'), ('AND', '%aH', '%ba', '%aF'), ('SHL', '%aH', '%aH', '%aE'), ('LOAD', '%aC', 'K[%aB]'), ('MOV', '%aG', '%aF'), ('SHL', '%aG', '%aG', '%aE'), ('NOT', '%aG', '%aG'), ('AND', '%aC', '%aC', '%aG'), ('OR', '%aC', '%aC', '%aH'), ('STORE', 'K[%aB]', '%aC'), ('ADDI', '%aB', '%aB', '1'), ('SHR', '%aH', '%ba', '%br'), ('SUB', '%bs', '39', '%br'), ('MOVI', '%aF', '1'), ('SHL', '%aF', '%aF', '%bs'), ('SUBI', '%aF', '%aF', '1'), ('NOT', '%aG', '%aF'), ('LOAD', '%aC', 'K[%aB]'), ('AND', '%aC', '%aC', '%aG'), ('OR', '%aC', '%aC', '%aH'), ('STORE', 'K[%aB]', '%aC'), ('RET',)])
    q += [L('H', '@C')]
    q += C('H', [('SHL', '%bq', '%bk', '4'), ('ADD', '%bq', '%bq', '%bk'), ('SHR', '%aB', '%bq', '8'), ('ANDI', '%aE', '%bq', '255'), ('LOAD', '%aC', 'm[%bu+%aB]'), ('SHR', '%al', '%aC', '%aE'), ('CMP', '%aq', '%aE', '239'), ('BRLE', '@bt', '%aq'), ('ADDI', '%aB', '%aB', '1'), ('LOAD', '%cA', 'm[%bu+%aB]'), ('SUB', '%cB', '256', '%aE'), ('SHL', '%cA', '%cA', '%cB'), ('OR', '%al', '%al', '%cA')]) + [L('H', '@bt')]
    q += C('H', [('ANDI', '%al', '%al', hex((1 << 17) - 1)), ('RET',)])
    q += [L('H', '@D')]
    q += C('H', [('SHL', '%bq', '%bk', '4'), ('ADD', '%bq', '%bq', '%bk'), ('SHR', '%aB', '%bq', '8'), ('ANDI', '%aE', '%bq', '255'), ('CMP', '%aq', '%aE', '239'), ('BRGT', '@E', '%aq'), ('MOVI', '%aF', hex((1 << 17) - 1)), ('SHL', '%aF', '%aF', '%aE'), ('NOT', '%aG', '%aF'), ('LOAD', '%aC', 'm[%bu+%aB]'), ('AND', '%aC', '%aC', '%aG'), ('SHL', '%aH', '%al', '%aE'), ('OR', '%aC', '%aC', '%aH'), ('STORE', 'm[%bu+%aB]', '%aC'), ('RET',)])
    q += [L('H', '@E')]
    q += C('H', [('SUB', '%br', '256', '%aE'), ('MOVI', '%aF', '1'), ('SHL', '%aF', '%aF', '%br'), ('SUBI', '%aF', '%aF', '1'), ('AND', '%aH', '%al', '%aF'), ('SHL', '%aH', '%aH', '%aE'), ('LOAD', '%aC', 'm[%bu+%aB]'), ('MOV', '%aG', '%aF'), ('SHL', '%aG', '%aG', '%aE'), ('NOT', '%aG', '%aG'), ('AND', '%aC', '%aC', '%aG'), ('OR', '%aC', '%aC', '%aH'), ('STORE', 'm[%bu+%aB]', '%aC'), ('ADDI', '%aB', '%aB', '1'), ('SHR', '%aH', '%al', '%br'), ('SUB', '%bs', '17', '%br'), ('MOVI', '%aF', '1'), ('SHL', '%aF', '%aF', '%bs'), ('SUBI', '%aF', '%aF', '1'), ('NOT', '%aG', '%aF'), ('LOAD', '%aC', 'm[%bu+%aB]'), ('AND', '%aC', '%aC', '%aG'), ('OR', '%aC', '%aC', '%aH'), ('STORE', 'm[%bu+%aB]', '%aC'), ('RET',)])
    _d += q
    _14, _19, _1c, _1b = gaT(st.qwords)
    assert _1c < gap
    _f = ['r%d' % (len(_14) + j) for j in range(8)]
    _18 = ['r%d' % x for x in _1b]
    _27 = [f'%F{j}' for j in range(8)]
    _23 = [L('R', '@bv')] + _14
    _23 += C('R', [('LOAD', '%af', 'state.random'), ('ADD', '%bw', '%af', '%bx'), ('ADD', '%by', '%af', '%bz'), ('MOVI', '%bA', '0'), ('MOVI', '%bB', '-1'), ('MOVI', '%bC', '-1'), ('MOVI', '%bD', '4513774610616367259799365849855'), ('STORE', 'C0[0]', '%bw'), ('STORE', 'C1[0]', '%by'), ('MOVI', '%bE', '1')])
    _23 += [L('R', '@G')]
    for j, _a in enumerate(_f):
        _23 += C('R', [('SHR', '%cC', '%bw', str(32 * j)), ('ANDI', '%cC', '%cC', hex(gU)), ('SHR', '%cD', '%by', str(32 * j)), ('ANDI', '%cD', '%cD', hex(gU)), ('SHL', '%cD', '%cD', '36'), ('OR', _a, '%cC', '%cD')])
    _23 += [L('R', '@H')]
    _23 += C('R', [('CMP', '%aq', '%bA', '36976841610169280592276405042010708'), ('BRGE', '@ac', '%aq'), ('CALL', '@bF'), ('ADDI', '%bA', '%bA', '1')])
    for j, _28 in enumerate(_18):
        _23.append(gaR('R', 'MOV', _27[j], _28))
    for j, _a in enumerate(_f):
        _23.append(gaR('R', 'MOV', _a, _27[j]))
    for _12 in (0, 1):
        sh = str(36 * _12)
        _23 += C('R', [('SHR', '%cE', _27[0], sh), ('ANDI', '%cE', '%cE', hex(gU)), ('XORI', '%cE', '%cE', hex(gU)), ('BRNZ', '@cI%d' % _12, '%cE'), ('SHR', '%cF', _27[1], sh), ('ANDI', '%cF', '%cF', hex(gU)), ('SHR', '%cG', _27[2], sh), ('ANDI', '%cG', '%cG', hex(gU)), ('SHR', '%cH', _27[3], sh), ('ANDI', '%cH', '%cH', hex((1 << 26) - 1)), ('SHL', '%cG', '%cG', '32'), ('SHL', '%cH', '%cH', '64'), ('OR', '%aM', '%cF', '%cG'), ('OR', '%aM', '%aM', '%cH'), ('CMP', '%aq', '%aM', '1783'), ('BRGE', '@cI%d' % _12, '%aq'), ('CMP', '%aq', f'%cM{_12}', '-1'), ('BRNE', '@cI%d' % _12, '%aq'), ('MOV', f'%cM{_12}', '%bA'), ('MOVI', '%aL', '0')])
        for j, _28 in enumerate(_27):
            _23 += C('R', [('SHR', '%cL', _28, sh), ('ANDI', '%cL', '%cL', hex(gU)), ('SHL', '%cL', '%cL', str(32 * j)), ('OR', '%aL', '%aL', '%cL')])
        _23 += C('R', [('MOV', f'%cN{_12}', '%aL')])
        _23 += [L('R', '@cI%d' % _12)]
    _23 += C('R', [('SUBI', '%bD', '%bD', '1'), ('BRNZ', '@I', '%bD'), ('MOVI', '%bD', '4513774610616367259799365849855')])
    for _12 in (0, 1):
        _23 += C('R', [('MOVI', '%aL', '0')])
        for j, _28 in enumerate(_27):
            _23 += C('R', [('SHR', '%cL', _28, str(36 * _12)), ('ANDI', '%cL', '%cL', hex(gU)), ('SHL', '%cL', '%cL', str(32 * j)), ('OR', '%aL', '%aL', '%cL')])
        _23.append(gaR('R', 'STORE', 'C%d[%%bE]' % _12, '%aL'))
    _23 += C('R', [('ADDI', '%bE', '%bE', '1')])
    _23 += [L('R', '@I')]
    _23 += C('R', [('CMP', '%aq', '%bB', '-1'), ('BREQ', '@H', '%aq'), ('CMP', '%aq', '%bC', '-1'), ('BREQ', '@H', '%aq'), ('CMP', '%aq', '%cJ', '%cK'), ('BRNE', '@ae', '%aq'), ('SUB', '%bJ', '%bB', '%bC'), ('MOVI', '%bP', '0'), ('BRGE', '@bG', '%bJ'), ('SUB', '%bJ', '%bC', '%bB'), ('MOVI', '%bP', '1')]) + [L('R', '@bG')]
    _23 += C('R', [('MOVI', '%bR', 'C0'), ('MOVI', '%bT', 'C1'), ('BRZ', '@bH', '%bP'), ('MOVI', '%bR', 'C1'), ('MOVI', '%bT', 'C0')]) + [L('R', '@bH')]
    _23 += C('R', [('MOV', '%bI', '%bJ'), ('CALL', '@P'), ('MOV', '%bK', '%bL'), ('MOV', '%bM', '%bN'), ('MOV', '%bO', '%bC'), ('BRZ', '@J', '%bP'), ('MOV', '%bO', '%bB')])
    _23 += [L('R', '@J')]
    _23 += C('R', [('LOAD', '%bQ', 'm[%bR+%bK]'), ('LOAD', '%bS', 'm[%bT]'), ('MOV', '%bU', '%bM'), ('CALL', '@R'), ('CMP', '%aq', '%bQ', '%bS'), ('BREQ', '@ae', '%aq')])
    _23 += C('R', [('MOV', '%bI', '%bO'), ('CALL', '@P'), ('MOVI', '%bV', '0'), ('ADDI', '%L', '%bL', '1')]) + [L('R', '@N')]
    _23 += C('R', [('SUB', '%aH', '%L', '%bV'), ('CMP', '%aq', '%aH', '1'), ('BRLE', '@O', '%aq'), ('ADD', '%M', '%L', '%bV'), ('SHR', '%M', '%M', '1'), ('ADD', '%bW', '%M', '%bK'), ('LOAD', '%bX', 'm[%bR+%bW]'), ('LOAD', '%bY', 'm[%bT+%M]'), ('MOV', '%bQ', '%bX'), ('MOV', '%bU', '%bM'), ('CALL', '@R'), ('CMP', '%aq', '%bQ', '%bY'), ('BREQ', '@K', '%aq'), ('MOV', '%bV', '%M'), ('BR', '@N')])
    _23 += [L('R', '@K'), gaR('R', 'MOV', '%L', '%M'), gaR('R', 'BR', '@N'), L('R', '@O')]
    _23 += C('R', [('ADD', '%bW', '%bV', '%bK'), ('LOAD', '%bQ', 'm[%bR+%bW]'), ('LOAD', '%bS', 'm[%bT+%bV]'), ('MOV', '%bU', '%bM'), ('CALL', '@R'), ('MOV', '%bZ', '4513774610616367259799365849855'), ('CALL', '@ca'), ('RET',)])
    _23 += [L('R', '@P')]
    _23 += C('R', [('MOVI', '%bL', '0'), ('MOVI', '%bN', '0'), ('MOVI', '%cc', '255')]) + [L('R', '@cb')]
    _23 += C('R', [('SHL', '%bN', '%bN', '1'), ('SHR', '%aK', '%bI', '%cc'), ('ANDI', '%aK', '%aK', '1'), ('OR', '%bN', '%bN', '%aK'), ('CMP', '%aq', '%bN', '4513774610616367259799365849855'), ('BRLT', '@Q', '%aq'), ('SUB', '%bN', '%bN', '4513774610616367259799365849855'), ('MOVI', '%aK', '1'), ('SHL', '%aK', '%aK', '%cc'), ('OR', '%bL', '%bL', '%aK')])
    _23 += [L('R', '@Q')]
    _23 += C('R', [('SUBI', '%cc', '%cc', '1'), ('BRGE', '@cb', '%cc'), ('RET',)])
    _23 += [L('R', '@R')]
    _23 += C('R', [('CALL', '@U')]) + [L('R', '@cd')]
    _23 += C('R', [('BRZ', '@S', '%bU'), ('CALL', '@bF')])
    for j, _28 in enumerate(_18):
        _23.append(gaR('R', 'MOV', _27[j], _28))
    for j, _a in enumerate(_f):
        _23.append(gaR('R', 'MOV', _a, _27[j]))
    _23 += C('R', [('SUBI', '%bU', '%bU', '1'), ('BR', '@cd')])
    _23 += [L('R', '@S'), gaR('R', 'CALL', '@T'), gaR('R', 'RET'), L('R', '@U')]
    for j, _a in enumerate(_f):
        _23 += C('R', [('SHR', '%cL', '%bQ', str(32 * j)), ('ANDI', _a, '%cL', hex(gU))])
    _23 += C('R', [('RET',)]) + [L('R', '@T')]
    _23 += C('R', [('MOVI', '%bQ', '0')])
    for j, _28 in enumerate(_f):
        _23 += C('R', [('ANDI', '%cL', _28, hex(gU)), ('SHL', '%cL', '%cL', str(32 * j)), ('OR', '%bQ', '%bQ', '%cL')])
    _23 += C('R', [('RET',)]) + [L('R', '@ca')]
    _23 += C('R', [('CALL', '@W')]) + [L('R', '@ce')]
    _23 += C('R', [('BRZ', '@ac', '%bZ'), ('MOV', '%cf', '%bQ'), ('MOV', '%cg', '%bS'), ('CALL', '@bF'), ('MOVI', '%ch', '0')])
    for j, _28 in enumerate(_18):
        _23.append(gaR('R', 'MOV', _27[j], _28))
    for _28 in _27:
        _23 += C('R', [('ANDI', '%cC', _28, hex(gU)), ('SHR', '%cD', _28, '36'), ('ANDI', '%cD', '%cD', hex(gU)), ('XOR', '%aH', '%cC', '%cD'), ('OR', '%ch', '%ch', '%aH')])
    _23 += C('R', [('BRZ', '@V', '%ch')])
    for j, _a in enumerate(_f):
        _23.append(gaR('R', 'MOV', _a, _27[j]))
    _23 += C('R', [('CALL', '@ci')])
    _23 += C('R', [('SUBI', '%bZ', '%bZ', '1'), ('BR', '@ce')])
    _23 += [L('R', '@V')]
    _23 += C('R', [('CMP', '%aq', '%cf', '%cg'), ('BREQ', '@ae', '%aq'), ('MOV', '%cj', '%cf'), ('MOV', '%ck', '%cg'), ('RET',)])
    _23 += [L('R', '@W')]
    for j, _a in enumerate(_f):
        _23 += C('R', [('SHR', '%cC', '%bQ', str(32 * j)), ('ANDI', '%cC', '%cC', hex(gU)), ('SHR', '%cD', '%bS', str(32 * j)), ('ANDI', '%cD', '%cD', hex(gU)), ('SHL', '%cD', '%cD', '36'), ('OR', _a, '%cC', '%cD')])
    _23 += C('R', [('RET',)]) + [L('R', '@ci')]
    _23 += C('R', [('MOVI', '%bQ', '0'), ('MOVI', '%bS', '0')])
    for j, _28 in enumerate(_f):
        _23 += C('R', [('ANDI', '%cC', _28, hex(gU)), ('SHR', '%cD', _28, '36'), ('ANDI', '%cD', '%cD', hex(gU)), ('SHL', '%cC', '%cC', str(32 * j)), ('SHL', '%cD', '%cD', str(32 * j)), ('OR', '%bQ', '%bQ', '%cC'), ('OR', '%bS', '%bS', '%cD')])
    _23 += C('R', [('RET',)])
    _1a = [L('P', '@bF')] + _19 + [gaR('R', 'RET')]
    _c = []
    for _2f, _16 in (('@X', 'passing'), ('@Y', 'hits'), ('@Z', 'full'), ('@aa', 'cut'), ('@ab', 'limit'), ('@ac', 'recovery'), ('@ad', 'qf'), ('@ae', 'alias')):
        _c += [L('halt', _2f), gaR('halt', 'HALT', _16)]
    _22 = _25 + [L('loop', '@f')] + _2d + _29 + _d + _23 + _1a + _c
    _8 = sum((x[5] == gG for x in _22))
    assert _8 <= 1335
    _22 += [gaR('Z', 'NOP') for _ in range(1335 - _8)]
    _11, pc = ({}, 0)
    for x in _22:
        if x[1] == 'LABEL':
            _11[x[2]] = pc
        else:
            pc += 1
    _33 = dict(_1f)
    _31 = {int(_32[1:]) for _32 in _33.values()}
    _17 = [256]

    def _24(s):

        def vr(m):
            _0 = m.group(0)
            if _0 not in _33:
                while _17[0] in _31:
                    _17[0] += 1
                _33[_0] = 'r%d' % _17[0]
                _31.add(_17[0])
                _17[0] += 1
            return _33[_0]
        s = re.sub('%[A-Za-z0-9_]+', vr, s)
        return str(_11[s]) if s in _11 else s
    _22 = [tuple([x[0], x[1]] + [_24(y) for y in x[2:5]] + [x[5]]) for x in _22 if x[1] != 'LABEL']
    assert max((int(_32[1:]) for _32 in _33.values())) < gap
    assert sum((x[0] in ('step', 'stage1') for x in _22)) == st.ops + 31
    assert sum((x[0] == 'P' for x in _22)) == gby(st.qwords)[1]
    assert sum((x[5] == gG for x in _22)) == 1335
    return _22
gaL = {}

def gbE(st=None):
    st = st or gbO()
    _2 = tuple(st.qwords)
    if _2 not in gaL:
        _5 = gaQ(st)
        for _4 in _5:
            for x in _4[2:5]:
                if x.startswith('r') and x[1:].isdigit():
                    assert int(x[1:]) < gap
        _3 = ''.join(('%05d|%s|%s|%s|%s|%s|%d\n' % ((j,) + x) for j, x in enumerate(_5)))
        by = {}
        for x in _5:
            by[x[0]] = by.get(x[0], 0) + 1
        gaL[_2] = dict(records=_5, listing=_3, sha256=hashlib.sha256(_3.encode()).hexdigest(), bytes=sum((x[5] for x in _5)), bitwise=sum((x[0] in ('step', 'stage1') for x in _5)), packed=sum((x[0] == 'P' for x in _5)), control=sum((x[5] == gG for x in _5)), sections=by)
    return gaL[_2]

def gbc(pa=None):
    pa = pa or gbE()
    _b = [(_a, _14) for _a, _14 in enumerate(pa['records']) if _14[0] == 'loop']
    assert [_14[1] for _, _14 in _b] == ['LOAD', 'SUBI', 'STORE', 'BRNZ', 'HALT']
    assert [_a for _a, _ in _b] == list(range(_b[0][0], _b[0][0] + 5))
    (_, _10), (_, _19), (_, _18), (_6, _5), (_, _9) = _b
    _e = _10[2]
    assert _10[3] == 'state.left'
    assert _19[2:5] == (_e, _e, '1')
    assert _18[2:4] == ('state.left', _e)
    assert _5[3] == _e and int(_5[2]) < _6
    assert _9[2] == 'batch_limit'
    assert not any((_14[1] == 'BR' and _14[2] == _5[2] and (int(_14[2]) < _a) for _a, _14 in enumerate(pa['records'])))
    assert any((_14[1] == 'MOVI' and _14[2] == _e and (_14[3] == str(gad + 3000)) for _14 in pa['records']))
    assert _e == 'r773'
    _11 = 'r774'
    assert any((_14[1] == 'MOVI' and _14[2] == _11 and (_14[3] == str(gad + 3001 - (1 << 48))) for _14 in pa['records']))
    assert not any(('state.next_left' in _14[2:5] for _14 in pa['records']))
    _7 = gbA(gad, gaz)
    for _a, _f in enumerate(_7):
        _15 = 'r%d' % (775 + _a)
        assert any((_14[1] == 'MOVI' and _14[2] == _15 and (_14[3] == str(_f)) for _14 in pa['records']))
        _12 = [(_14, pa['records'][_13 + 1]) for _13, _14 in enumerate(pa['records'][:-1]) if _14[1:5] == ('SUBI', _15, _15, '1')]
        assert len(_12) == 1 and _12[0][1][1] == 'BRLT' and (_12[0][1][3] == _15)
        assert not any((_14[1] in ('LOAD', 'STORE') and _15 in _14[2:5] for _14 in pa['records']))
    _17 = [_14 for _14 in pa['records'] if _14[0] in ('stage1', 'S')]
    assert sum((_14[0] == 'stage1' and _14[1] == 'AND' for _14 in _17)) == 31
    assert sum((_14[1] == 'BRLT' for _14 in _17)) == len(_7)
    assert gbM(gaz) == list(gaA)
    _16 = [(_14, pa['records'][_a + 1]) for _a, _14 in enumerate(pa['records'][:-1]) if _14[1] == 'MOV' and _14[3] == _e and (pa['records'][_a + 1][1] == 'CALL')]
    assert len(_16) == 2
    _2 = _16[0][0][2]
    _3 = _16[0][1][2]
    assert all((_14[2] == _2 and _8[2] == _3 for _14, _8 in _16))
    _c = [(_14, pa['records'][_a + 1]) for _a, _14 in enumerate(pa['records'][:-1]) if _14[1] == 'MOVI' and _14[2] == _2 and (_14[3] == str(gad + 3001)) and (pa['records'][_a + 1][1:3] == ('CALL', _3))]
    assert len(_c) == 1
    _1a = 3
    for _1 in range(1, _1a + 1):
        _d = _1a - _1 + 1
        assert _1a + 1 - _d == _1
        for _4 in range(1, _1 + 1):
            assert _1a - _4 + 1 - _d == _1 - _4
    _d = 3
    _1b = 0
    while _d:
        _d -= 1
        _1b += 1
        if _d:
            assert _5[1] == 'BRNZ'
        else:
            assert _9[1:3] == ('HALT', 'batch_limit')
    assert _1b == 3
    return True

def gbM(s1):
    return sorted({min(k, s1) for k in gaA})

def gbN(pa, s1):
    assert not any(pa[:s1])
    ks = gbM(s1)
    return (ks[0], [b - a + 3 + (3 if _2 == 0 else 0) for _2, (a, b) in enumerate(zip(ks, ks[1:]))])

def gbA(pa, s1):
    _1 = []
    for _2 in gbM(s1)[:-1]:
        _3 = 1 - Fraction((1 << _2) - 1, 1 << _2) ** gR
        _0 = (1 + gZ) * pa * _3
        _1.append(-(-_0.numerator // _0.denominator) + 64)
    return tuple(_1)

def gbL(pa, p, pc):
    ks, _0, j = (gbM(p['s1']), gb, 0)
    for _1, _5 in enumerate(ks):
        while j < _5:
            _0 &= pa[j]
            j += 1
        if _0 == 0:
            return 0
        if _1 + 1 < len(ks):
            _4 = 'passing%d' % _1
            pc[_4] += 1
            if pc[_4] > p['pmax'][_1]:
                raise gE('stage-1 checkpoint budget')
    return _0
gF = 350

def gbQ(pa):
    _0 = gaq + gm
    return 32 * ((_0 * pa + 255) // 256) + 32 * ((gaE * pa + 255) // 256)

def gbR(pa):
    lo, hi = (0, pa // gO)
    while lo < hi:
        _2 = (lo + hi + 1) // 2
        if gbQ(_2 + 1) <= pa:
            lo = _2
        else:
            hi = _2 - 1
    return lo

def gaV(n, Tp, pc, pd, Sb):
    c = gd[n]
    s1, W = (c['s1'], c['W'])
    N, D = (1 << n, s1 + W)
    L = Fraction(1 << D, Tp)
    if n == 256:
        assert gR + pd + gf < 1 << gaE
        assert gJ * 64 <= gbQ(pd + 1)
        B = gaO(Tp, pd, pc, Sb)
    else:
        _e = isqrt(2 * N * gQ.numerator // gQ.denominator) + 2
        _b, _9 = (_e + gF * L + 1, gh.denominator)
        q = -(-(_b * _9) // (_9 - gh.numerator))
        B = -(-q // gR)
    cc = -(-pc * L.numerator // L.denominator)
    fb = (Tp - 1).bit_length()
    _6 = n == 256
    return dict(n=n, s1=s1, W=W, D=D, Tp=Tp, fb=fb, kb=min(52 - fb, n - D), L=L, N=N, Q=B * gR, B=B, kappa=pc, Sb=Sb, c=cc, cr=-(-(KR * L.numerator) // L.denominator) if _6 else cc + Sb, tmax=pd, e2max=2 * B * gR // (1 << s1) + 64, pmax=gbA(B, s1) if _6 else tuple((10 ** 9 for _ in gbM(s1)[:-1])), cmax=gf if _6 else 10 ** 9)
gaM = {}

def gbO():
    if 256 not in gaM:
        gaM[256] = gaB(256)
    return gaM[256]

def gbw(st=None):
    return 1335

def gbu(st=None, R=gap):
    st = st or gbO()
    ph = st.ops
    _4, _6 = gbN(st.pin, gaz)
    _0 = ph + (st.spill_ops(R) if R < gap else 0) + _4 + gT
    pc = gby(st.qwords)
    _2 = (ph + gaz - 1) * go + pc[1] * gam + gbw(st) * gG
    if R == gap:
        _1 = gbE(st)['bytes']
        assert _1 == _2
    else:
        _1 = _2
    _7 = gbR(gV - gax - _1 - R * 32 - gg - ga)
    return (ph, _4, _6, _0, _1, _7)

def gbm(pa=None):
    pa = pa or len(gbT(256)[0].nodes)
    assert pa < 1 << 16
    _0 = pa + 1
    return (_0 + gx + gr + gw + gt, _0, pa)

def gbB(pa, pb):
    _0 = gbm()[0]
    assert _0 <= gv == 49296
    return (pa + ga + gg + gq * gu + gv, pa + ga + gg + gao + gbQ(pb + 1))

def gbC(n, pb=None, Tp=None, R=gap):
    if n != 256:
        c = gd[n]
        p = gaV(n, c['Tp'], c['kappa'], 0, c['Sb'])
        p['tmax'] = 4 * (p['Q'] // int(p['L'])) + 64
        return p
    pb = pb or gI
    _9 = gbu(None, R)[5]
    if gR + _9 + gf >= 1 << gaE:
        return None
    if Tp:
        return gaV(256, Tp, pb, _9, gd[256]['Sb'])
    if _9 < 1:
        return None
    lo, hi = (1.0, float(_9 + 1))
    for _ in range(60):
        _6 = (lo + hi) / 2
        lo, hi = (_6, hi) if gbS(_6, _9 + 1) <= gaD else (lo, _6)
    ok = lambda t: gaS(t, lo, _9, pb, gd[256]['Sb'])['P_lower'] >= gag
    a, b = (1000, 4095)
    if not ok(a):
        return None
    while b - a > 1:
        _6 = (a + b) // 2
        if ok(_6):
            a = _6
        else:
            b = _6
    return gaV(256, a, pb, _9, gd[256]['Sb'])
_B = {}

class gE(Exception):
    pass

class gl:

    def __init__(self, n):
        self.n = n
        st = gaB(n)
        self.st, self.pin, self.step = (st, st.pin, st.step)

    def f2(self, xs):
        return gbz(xs, self.n, self.st.qwords)

    def g_scalar(self, x):
        return gbj(x, self.n) ^ self.st.qint

class gz:

    def __init__(self, n, salt):
        import random
        self.n, self.st, self.pin = (n, gbO(), [0] * n)
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

def gbp(x, p):
    return x & (1 << p['s1']) - 1 == (1 << p['s1']) - 1 and x >> p['s1'] & (1 << p['W']) - 1 < p['Tp']

def gbg(x, p):
    return (x >> p['D'] & (1 << p['kb']) - 1) << p['fb'] | x >> p['s1'] & (1 << p['fb']) - 1

class QF:

    def __init__(self, slots):
        self.S, self.n, self.rb = (slots, 0, gaq)
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
        key &= (1 << gai + gaq) - 1
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
        assert trail < 1 << gaE and self.n < self.S - 1
        self.occ[_2], _1 = (1, (_3, trail, _0, int(x != _2)))
        while self.cont[x] or self.shf[x] or (self.occ[x] and (x != _2 or _0)):
            _1, (self.rem[x], self.tr[x], self.cont[x], self.shf[x]) = ((self.rem[x], self.tr[x], self.cont[x], 1), _1)
            x = (x + 1) % self.S
        self.rem[x], self.tr[x], self.cont[x], self.shf[x] = _1
        self.n += 1

def gbW(xs, pb, f2):
    for _ in range(pb):
        xs = f2(xs)
    return xs

def gbF(p, r, t0, t1, f2, pf=gJ):
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
                if gbp(xs[_9], p):
                    _a[_9], _4[_9] = (k, xs[_9])
        if None not in _a:
            break
    else:
        raise gE('recovery length')
    _c = 0 if _a[0] >= _a[1] else 1
    _11, (_f, _10) = (_a[1 - _c], divmod(abs(_a[0] - _a[1]), _12))
    _1 = lambda i: gbW([_2[_c][i + _f]], _10, f2)[0]
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

def gbH(pa, p, r, pd):
    n, _7, _d = (p['n'], p['N'] - 1, pa.pin)
    _12 = QF(p['tmax'] + 1)
    _2, ts, _a = ([0] * gR, list(range(gR)), gR)
    _e = gbx([r + t & _7 for t in ts], n, _d)
    pd['inserts'] += gR
    _1, _9, _6 = (0, p['Sb'], p['B'] + 3000)
    while _6:
        _e = list(pa.step(*_e))
        _1 += 1
        pd['batches'] += 1
        _c = pd['passing']
        _3 = gbL(_e, p, pd)
        _b = pd['passing'] != _c
        if _b and _1 >= p['B']:
            return None
        while _3:
            pd['stage1_hits'] += 1
            if pd['stage1_hits'] > p['e2max']:
                raise gE('stage-1 budget')
            l = (_3 & -_3).bit_length() - 1
            _3 &= _3 - 1
            x = gbq(_e, l, _d, n)
            if gbp(x, p):
                _4 = gbg(x, p)
                pd['finished'] += 1
                t0, at = _12.find(_4)
                if t0 is not None:
                    pd['recoveries'] += 1
                    _f = gbF(p, r, t0, ts[l], pa.f2)
                    if _f is None:
                        raise gE('recovery found no pair')
                    return _f
                if _12.n >= p['tmax']:
                    raise gE('table full')
                _12.put(_4, ts[l], at)
                if _12.n >= p['tmax']:
                    raise gE('table full')
                ts[l], _a, _2[l] = (_a, _a + 1, _1)
                _e = gbK(_e, l, r + ts[l] & _7, _d, n)
                pd['inserts'] += 1
        if _b and _1 >= _9:
            _9 += p['Sb']
            for l in range(gR):
                if _1 - _2[l] >= p['c']:
                    pd['cut'] += 1
                    if pd['cut'] > p['cmax']:
                        raise gE('cut budget')
                    ts[l], _a, _2[l] = (_a, _a + 1, _1)
                    _e = gbK(_e, l, r + ts[l] & _7, _d, n)
                    pd['inserts'] += 1
        _6 -= 1
        assert _6 == p['B'] + 3000 - _1
    pd['batch_limit'] += 1
    return None

class gj(dict):

    def __missing__(self, k):
        return 0

def gbe(pa, pb, pc=256):
    return int.from_bytes(hashlib.shake_256(('%s/%s' % (pa, pb)).encode()).digest((pc + 7) // 8), 'little') & (1 << pc) - 1

def gbb(pa, p, pc, pd):
    _0 = gj()
    try:
        _1 = gbH(pa, p, gbe(pc, pd, p['n']), _0)
    except gE as e:
        _0['halt'] += 1
        _1 = None
    return (_1, _0)
gX = 18
gW, gc = (2048, 21)
gaC = ('w0',)

def gbh(pa, pb):
    p = gbC(gX)
    _3, _0 = gbb(pb, p, pa, 't')
    _1 = dict(target_ok=int(_3 is not None), target_batches=_0['batches'], target_halt=_0['halt'], batch_limit_no_pass=1)
    if _3 is None:
        return (None, None, _1)
    return (gbv(_3[0]), gbv(_3[1]), _1)
gaJ = (1 << gc) - 1

def gbP(pa):
    return [[d & gaJ for d in pa]]

def gbi(pa, tr, pc):
    _f = tr % 3
    if _f == 0:
        xs = [gbe(pa, 'u%d' % i) for i in range(gW)]
    elif _f == 1:
        r = gbe(pa, 'r')
        xs = [r + i & (1 << 256) - 1 for i in range(gW)]
    else:
        xs = None
    _5 = []
    if xs is not None:
        for b in range(gW // gR):
            pl = gbx(xs[b * gR:(b + 1) * gR], 256, pc.pin)
            _5 += gbr(list(pc.step(*pl)), 256, pc.pin)
    else:
        _3 = [gbe(pa, 'c%d' % l) for l in range(gR)]
        xs = []
        for b in range(gW // gR):
            xs += _3
            _3 = gbr(list(pc.step(*gbx(_3, 256, pc.pin))), 256, pc.pin)
            _5 += _3
    _5 = [d ^ pc.qint for d in _5]
    _b = {'source': _f}
    _c = None
    for k, _2 in enumerate(gbP(_5)):
        _a = gaC[k]
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
    return (gbv(_c[0]), gbv(_c[1]), _b)

def gbn(pa):
    import random
    n, _4, _1e, _d = (20, 1200, 1 << 20, 64)
    _5 = len(pa)
    if _5 < _d:
        raise ValueError('h1-law-n20 requires at least 64 trials')
    _19 = int.from_bytes(hashlib.sha256(b'b3-h1-shared-v1\x00' + b'\x00'.join((t['seed'].encode() for t in pa))).digest(), 'little')
    _8 = gz(n, _19)
    xs = [gbe(t['seed'], 'h1-start', n) for t in pa[:_d]]
    _18 = gbx(xs, n, [0] * n)
    _1c = [{x} for x in xs]
    _a = [0] * _d
    _c, _f, _1 = (set(), 0, _d)
    for _1f in range(1, _4 + 1):
        _16 = xs
        _18 = list(_8.step(*_18))
        xs = gbr(_18, n, _8.pin)[:_d]
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
        _6 = random.Random(gbe(str(_19), 'h1-null-%d' % index))
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

def gbk():

    def _7(values, widths):
        _3 = _0 = 0
        assert len(values) == len(widths)
        for _1, _2 in zip(values, widths):
            assert 0 <= _1 < 1 << _2
            _3 |= _1 << _0
            _0 += _2
        return _3
    for _e in ((2, 10, 10, 10), (8, 10, 10, 10), (36, 1, 1, 1), (gaE,), (128,)):
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
    _5 = (1 << gai + gaq) - 1
    assert _5 >> gaq == (1 << gai) - 1
    assert _5 & (1 << gaq) - 1 == (1 << gaq) - 1
    _, at = _a.find(_5)
    _a.put(_5, (1 << gaE) - 1, at)
    _8 = False
    try:
        _, at = _a.find(_5 - 1)
        _a.put(_5 - 1, 1 << gaE, at)
    except AssertionError:
        _8 = True
    _, _, _, _, _3, _b = gbu()
    _2 = gV - gax - _3 - gao - gg - ga
    _9, _ = gbB(_3, _b)
    assert _9 == _3 + gg + ga + gq * gu + gv
    assert _8 and _a.find(_5)[0] == (1 << gaE) - 1
    assert gR + _b + gf < 1 << gaE
    assert gbQ(_b + 1) <= _2 < gbQ(_b + 2)

def gbJ(pa):
    gbk()
    _5 = gbE()
    gbc(_5)
    st = gbO()
    _8 = gby(st.qwords)[1]
    _4 = (st.ops + 31) * go + _8 * gam + 1335 * gG
    assert (_5['bytes'], _5['bitwise'], _5['packed'], _5['control']) == (_4, st.ops + 31, _8, 1335)
    _2, _7 = (pa['experiment_id'], [])
    if _2 == 'bsrho-n18':
        _3 = gl(gX)
        for t in pa['trials']:
            a, b, _6 = gbh(t['seed'], _3)
            _7.append({'trial': t['trial'], 'message_a_hex': a.hex() if a else None, 'message_b_hex': b.hex() if b else None, 'observations': _6})
    elif _2 == 'proj-prefix-w256':
        st = gbO()
        for t in pa['trials']:
            a, b, _6 = gbi(t['seed'], t['trial'], st)
            _7.append({'trial': t['trial'], 'message_a_hex': a.hex() if a else None, 'message_b_hex': b.hex() if b else None, 'observations': _6})
    elif _2 == 'h1-law-n20':
        for t, (a, b, _6) in zip(pa['trials'], gbn(pa['trials'])):
            _7.append({'trial': t['trial'], 'message_a_hex': a, 'message_b_hex': b, 'observations': _6})
    else:
        raise ValueError('unknown experiment')
    return {'schema_version': 1, 'trials': _7}
json.dump(gbJ(json.load(sys.stdin)), sys.stdout)
