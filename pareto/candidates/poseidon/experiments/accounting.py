"""Orchard two-round-skip collision: line map, preregistered s0 stream, and the complete operation/memory accounting
(orchard-field-ram-v2) of the submitted deterministic procedure, including worst-case half-gcd recurrences.
Standard library only. As an organizer experiment it returns the certified message pair for every trial (seeds are unused:
the procedure is deterministic) and reports the computed bounds as observations."""
import sys, json, hashlib, math

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
RC0 = [0x360d7470611e473d353f628f76d110f34e71162f31003b7057538c2596426303,
       0x2bab94d7ae222d135dc3c6c5febfaa314908ac2f12ebe06fbdb74213bf63188b,
       0x150c93fef652fb1c2bf03e1a29aa871fef77e7d736766c5d0939d92753cc5dc8]
RC1 = [0x3270661e68928b3a955d55db56dc57c103cc0a60141e894e14259dce537782b2,
       0x073f116f04122e25a0b7afe4e2057299b407c370f2b5a1ccce9fb9ffc345afb3,
       0x2a32ec5c4ee5b1837affd09c1f53f5fd55c9cd2061ae93ca8ebad76fc71554d8]
MDS = [[0x0ab5e5b874a68de7b3d59fbdc8c9ead497d7a0ab23850b56323f2486d7e11b63,
        0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e,
        0x07c045d5f5e9e5a6d803952bbb364fdfa0a3b71a5fb1573519d1cf25d8e8345d],
       [0x233162630ebf9ed7f8e24f66822c2d9f3a0a464048bd770ad049cdc8d085167c,
        0x25cae2599892a8b0b36664548d60957d78f8365c85bbab07402270113e047a2e,
        0x22f5b5e1e6081c9774938717989a19579aad3d8262efd83ff84d806f685f747a],
       [0x2e29dd59c64b1037f333aa91c383346421680eabc56bc15dfee7a9944f84dbe4,
        0x1d1aab4ec1cd678892d15e7dceef1665cbeaf48b3a0624c3c771effa43263664,
        0x3bf763086a18936451e0cbead65516b975872c39b59a31f615639415f6e85ef1]]

# ---------------------------------------------------------------- line map
def inv(a): return pow(a, P - 2, P)
def mat_inv(a):
    det = (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
           + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])) % P
    adj = [[0] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            m = [[a[x][y] for y in range(3) if y != j] for x in range(3) if x != i]
            adj[j][i] = ((-1) ** (i + j) * (m[0][0] * m[1][1] - m[0][1] * m[1][0])) % P
    di = inv(det)
    return [[adj[i][j] * di % P for j in range(3)] for i in range(3)]
MI = mat_inv(MDS)
E5 = (4 * (P - 1) + 1) // 5
assert (5 * E5) % (P - 1) == 1
K = pow((1 << 65) + RC0[2], 5, P)
D0, D1 = MI[2][1] % P, (-MI[2][0]) % P
C2 = (K + sum(MI[2][j] * RC1[j] for j in range(3))) * inv(MI[2][2]) % P

def inputs_from_s(s):
    t = pow(s, E5, P)
    u = [t * D0 % P, t * D1 % P, C2]
    w = [(u[j] - RC1[j]) % P for j in range(3)]
    X = [sum(MI[i][j] * w[j] for j in range(3)) % P for i in range(3)]
    assert X[2] == K
    return (pow(X[0], E5, P) - RC0[0]) % P, (pow(X[1], E5, P) - RC0[1]) % P

def s0_stream(r, i):
    dom = b"HashSmash-Orchard-r%d-s0-v1" % r; ctr = 0
    while True:
        v = int.from_bytes(hashlib.sha256(dom + i.to_bytes(4, 'little') + ctr.to_bytes(4, 'little')).digest(), 'little')
        if v < P: return v, ctr + 1
        ctr += 1

# executed outcomes (FLINT run of the deterministic procedure): deg h per trial and the output root s1
CASES = {
    1: dict(degs=[2], s1=13834604379169323874622223502465088293112971940967906188773023811204797909611),
    2: dict(degs=[1, 1, 1, 3], s1=1598272476020044032828712062354776193750305428231857171764296402890811058530),
}

# ---------------------------------------------------------------- unit charges
LOOP = 3
CP, ZF, SC, PW, AS = 2 + LOOP, 1 + LOOP, 3 + LOOP, 4 + LOOP, 4 + LOOP
def POW(bits): return 8 * bits + 20          # square-and-multiply, 8 itemized ops per exponent bit
INV = POW(255)                               # Fermat a^(p-2)
ROOT5 = POW(255)
SHA = 20000
GU = 10
CROSS = 48
NTT_OVH = 7000

def tsize(l):
    l = max(l, 1)
    k = max(0, (l - 1).bit_length()); best = 1 << k
    if k >= 2 and (3 << (k - 2)) >= l:
        best = 3 << (k - 2)
    return best

BF = {4: 26, 2: 11, 3: 21}
TW = {4: 6, 2: 4, 3: 5}
def factors(M):
    k = 0; x = M
    while x % 2 == 0: x //= 2; k += 1
    assert x in (1, 3)
    return [4] * (k // 2) + [2] * (k % 2) + ([3] if x == 3 else [])
def T0(M):
    ops = 0; L = M
    for f in factors(M):
        m = L // f
        ops += BF[f] * (M // f) + TW[f] * m
        L = m
    return ops
_T = {}
def T(N):
    if N not in _T: _T[N] = (T0(N) if N > 1 else 0) + NTT_OVH
    return _T[N]

# ---------------------------------------------------------------- polynomial-operation charges
def mul_fft(la, lb):
    L = tsize(la + lb - 1)
    return (la + lb) * CP + (2 * L - la - lb) * ZF + 3 * T(L) + L * PW + (la + lb - 1) * SC
def mul_school(la, lb): return la * lb * (GU - 2) + (la + lb - 1) * ZF
def mul_cost(la, lb):
    if la <= 0 or lb <= 0: return 0
    return min(mul_fft(la, lb), mul_school(la, lb))
_NW = {}
def newton_cost(q):
    if q in _NW: return _NW[q]
    ops = INV; k = 1
    while k < q:
        k2 = min(2 * k, q); Lj = tsize(k2 + k - 1)
        ops += k2 * CP + (Lj - k2) * ZF + k * CP + (Lj - k) * ZF + 3 * T(Lj) + Lj * PW
        ops += (k2 - k) * SC + (Lj - (k2 - k)) * ZF + 2 * T(Lj) + Lj * PW + (k2 - k) * (SC + 1)
        k = k2
    _NW[q] = ops
    return ops
def div_classical_q(q1, lb): return INV + q1 * (lb * GU + 8) + 4 * lb
def blk(b, lb):
    Lr = tsize(max(lb - 1, 1))
    return (2 * b * CP + mul_cost(b, b) + b * CP + (b + lb) * AS + 2 * Lr * ZF + 3 * T(Lr) + Lr * PW + Lr * SC
            + (b + lb - 1) * AS + lb * AS + 10)
def div_blocked_q(q1, lb):
    b = min(q1, lb); nb = -(-q1 // b)
    return newton_cost(b) + nb * blk(b, lb) + 4 * lb      # + leading-zero scan of the remainder
def div_mem_q(q1, lb, needq):
    b = min(q1, lb); qm = q1 if needq else 0
    return qm + 2 * b + 2 * tsize(max(2 * b, lb))
def matvec_cost(L): return 2 * L * ZF + 4 * L * CP + 8 * T(L) + 4 * L * PW + 2 * L * AS + 2 * L * SC + 2 * L * 4   # + leading-zero scans of both results
def iter_cost(d):
    s = d - 1
    return (s * (INV + 20) + 2 * s * (GU * (2 * d - 1) + 8) + 2 * 2 * s * d * (GU - 2)
            + 2 * s * (d + 1) * AS + 2 * s * (2 * d) * ZF + 4 * 2 * d + 4 * (d + 1) * ZF)
def euclid_cost(n): return GU * n * (n + 1) + 8 * 2 * n + (INV + 20) * n + 4 * 2 * n + INV + 7 * (n + 1)

# ---------------------------------------------------------------- worst-case division majorant
_F = [0.0]
def Fmaj(l):
    """F(l) = max over 1 <= l' <= l of min(GU*l' + 8, blk(l', l')/l'); nondecreasing by construction"""
    while len(_F) <= l:
        k = len(_F); _F.append(max(_F[-1], min(GU * k + 8, blk(k, k) / k)))
    return _F[l]
def Dup(q1, lbm):
    """upper bound of min(classical, blocked) for quotient length <= q1 and divisor length <= lbm (both arguments may be
    block maxima: every term below is nondecreasing in q1 and in lbm)"""
    r1 = min(div_classical_q(q1, lbm), newton_cost(min(q1, lbm)) + blk(min(q1, lbm), lbm) + 4 * lbm)   # one-block region (b = q1 <= lb)
    l = min(q1, lbm)
    r2 = -(-int(q1 * Fmaj(l) * (1 + 1e-12)) // 1) + 1 + INV + 8 * l + newton_cost(l) + blk(l, l)   # many-block region (b = lb < q1); float ratio rounded up
    return max(r1, r2)

def blocks(qmax):
    """partition 0..qmax: singletons below 512, then blocks of relative width 1/256"""
    out = []; q = 0
    while q <= qmax:
        w = 1 if q < 512 else q >> 8
        out.append((q, min(qmax, q + w - 1))); q += w
    return out

_MID = {}
def MID(d):
    """max over middle-step quotient degree q <= d-1 (la <= 2d-1, lb <= 2d-1-q) of division + two M-entry products + subtractions"""
    if d in _MID: return _MID[d]
    best = 0
    for qa, qb in blocks(d - 1):
        lbm = 2 * d - 1 - qa
        if lbm < 1: continue
        c = Dup(qb + 1, lbm) + 2 * mul_cost(qb + 1, d) + 2 * (d + 1) * AS
        best = max(best, c)
    _MID[d] = best
    return best

_DM = {}
def DIVMAX(la_max, qmax):
    key = (la_max, qmax)
    if key in _DM: return _DM[key]
    best = 0
    for qa, qb in blocks(qmax):
        lbm = la_max - qa
        if lbm < 1: continue
        best = max(best, Dup(qb + 1, lbm))
    _DM[key] = best
    return best

def MM(d):
    L = tsize(d + 1)
    fft = 8 * L * CP + 12 * T(L) + L * (8 * PW + 4 * AS) + 4 * L * SC
    h = (d + 2) // 2
    school = 8 * (h * (d + 2 - h) * (GU - 2) + (d + 1) * ZF) + 4 * (d + 2) * AS
    return min(fft, school)
def copyb(d): return 2 * tsize(2 * d - 1) * CP

_HM = {}
def HM(d):
    if d in _HM: return _HM[d]
    if d <= 0: v = 20
    elif d <= CROSS: v = 20 + copyb(d) + iter_cost(d)
    else: v = 20 + copyb(d) + HM((d + 1) // 2) + matvec_cost(tsize(2 * d - 1)) + MID(d) + HM(d // 2) + MM(d)
    _HM[d] = v
    return v
def split(N):
    dred = (N + 1) // 2; d1 = (dred + 1) // 2
    if d1 >= dred: d1 = dred - 1
    return dred, d1
def HI(N):
    dred, d1 = split(N); L = tsize(N + 1)
    return 20 + HM(d1) + matvec_cost(L) + DIVMAX(N + 1, dred - 1) + HM(dred - d1) + matvec_cost(L)
_G = {}
def G(N):
    if N in _G: return _G[N]
    if N <= CROSS: v = euclid_cost(max(N, 1))
    else:
        dred, _ = split(N)
        v = 20 + HI(N) + DIVMAX(N + 1, N) + G(N - dred)
    _G[N] = v
    return v

# memory (field words)
_DMM = {}
def DIVMEM(la_max, qmax, needq):
    key = (la_max, qmax, needq)
    if key in _DMM: return _DMM[key]
    best = 0
    for qa, qb in blocks(qmax):
        lbm = la_max - qa
        if lbm < 1: continue
        best = max(best, div_mem_q(qb + 1, lbm, needq))
    _DMM[key] = best
    return best
_PM = {}
def PMM(d):
    if d in _PM: return _PM[d]
    if d <= 0: v = 2
    else:
        cap = tsize(2 * d - 1)
        if d <= CROSS: v = 2 * cap + 7 * (d + 1) + 4 * d
        else:
            d1, d2 = (d + 1) // 2, d // 2
            v = max(2 * cap + PMM(d1), 4 * cap + 4 * d1, 2 * cap + 4 * d1 + DIVMEM(2 * d - 1, d - 1, True),
                    2 * cap + 4 * d1 + d + PMM(d2), 4 * d1 + d + 4 * d2 + 2 * tsize(2 * d) + 2 * (d + 1),
                    4 * d2 + 4 * (d + 1) + 8 * tsize(d + 1) + 4 * d)
    _PM[d] = v
    return v
def PMI(N):
    dred, d1 = split(N); L = tsize(N + 1)
    return max(PMM(d1), 4 * d1 + 2 * L, DIVMEM(N + 1, dred - 1, False), PMM(dred - d1), 4 * (dred - d1) + 2 * L)
_PG = {}
def PG(N):
    if N in _PG: return _PG[N]
    if N <= CROSS: v = 0
    else:
        dred, _ = split(N)
        v = max(PMI(N), DIVMEM(N + 1, N, False), PG(N - dred))
    _PG[N] = v
    return v

# ---------------------------------------------------------------- the complete procedure
def params(r):
    n = 5 ** (6 + r); C = 216 + 21 * r
    L = tsize(2 * n - 1); L2 = tsize(n + 1)
    e0 = max(e for e in range(64) if (1 << e) < n)
    assert P >> (254 - e0) == 1 << e0 and P >> 254 == 1
    return n, C, L, L2, e0, 254 - e0

def newton_barrett(n):
    ops = 0; k = 1; sizes = []
    while k < n:
        k2 = min(2 * k, n); Lj = tsize(k2 + k - 1); sizes.append(Lj)
        ops += k2 * CP + (Lj - k2) * ZF + k * CP + (Lj - k) * ZF + 3 * T(Lj) + Lj * PW
        ops += (k2 - k) * SC + (Lj - (k2 - k)) * ZF + 2 * T(Lj) + Lj * PW + (k2 - k) * (SC + 1)
        k = k2
    return ops, sizes

def step_items(n, L, L2):
    return [
        ('copy a into W and zero-pad to L', n * CP + (L - n) * ZF),
        ('forward transform, length L', T(L)),
        ('pointwise square', L * SC),
        ('inverse transform, length L', T(L)),
        ('scale 2n coefficients by 1/L at offset b', 2 * n * SC + 1),
        ("fold A' modulo X^L2 - 1", (2 * n - L2) * AS),
        ('keep folded low n coefficients in a', n * CP),
        ('reversed top n coefficients into W, zero-pad to L', n * CP + (L - n) * ZF),
        ('forward L, pointwise by I^, inverse L', 2 * T(L) + L * PW),
        ('reversed low n coefficients, zero-pad to L2', n * CP + (L2 - n) * ZF),
        ('forward L2, pointwise by g^, inverse L2', 2 * T(L2) + L2 * PW),
        ("R = folded A' - Q g on n coefficients", n * AS),
    ]

def setup_items():
    return [
        ('MI = M^-1 by adjugate (determinant, 9 cofactors, one inversion, 9 scalings)', 200 + INV),
        ('K, D0, D1, C2 (one inversion), D0^5, D1^5, C2^5, A, B', 200 + INV),
        ('e5 = (4(p-1)+1)/5: binary long division, 256 iterations x 20, x4 for the k-search mod 5', 4 * 256 * 20 + 500),
        ('Z of order 3*2^32: candidates 2..5, each one 221-bit and two <= 34-bit powers plus comparisons', 4 * (POW(221) + 2 * POW(34) + 50)),
        ('primitive N-th roots of unity for <= 50 transform lengths (<= 34-bit exponents)', 50 * POW(34)),
        ('inverse scalars 1/N for <= 50 transform lengths', 50 * INV),
    ]

def trial_items(r, sha_calls, k):
    n, C, L, L2, e0, steps = params(r)
    nw, _ = newton_barrett(n)
    step = sum(v for _, v in step_items(n, L, L2))
    return [
        ('sha256', sha_calls * (SHA + 8)),
        ('f_interp', L2 * (1 + LOOP + 1 + 10) + L2 * (2 * C + 20) + T(L2) + (n + 1) * SC),
        ('g_monic', (2 * C + 20) + AS + INV + (n + 1) * SC + (L2 - n - 1) * ZF),
        ('newton', nw),
        ('I_hat', n * CP + (L - n) * ZF + T(L) + L * SC),
        ('g_hat', T(L2) + L2 * SC),
        ('x_init', n * ZF + 1),
        ('powering', steps * step),
        ('g_recover', T(L2)),
        ('v', AS),
        ('gcd', G(n)),
        ('roots', 4 * AS if k == 2 else (100000 + INV if k == 3 else 10)),
    ]

def memory(r):
    n, C, L, L2, e0, steps = params(r)
    _, nsizes = newton_barrett(n)
    phases = {
        'interpolation': L2,
        'Newton': L2 + n + 2 * max(nsizes),
        'powering': 2 * L + L2 + n,
        'gcd': 2 * L2 + PG(n),
    }
    const_words = 64 * 3 + 9 + 9 + 3 + 3 + 4 + 1 + 1 + 50 + 50 + 64
    peak = max(phases.values())
    b1 = peak * 32 + const_words * 32 + 512 + (1 << 20)
    b4 = peak * 32 + const_words * 32 + 512 + (4 << 20)
    return phases, peak, const_words, b1, b4

def total(r):
    import math
    n, C, L, L2, e0, steps = params(r)
    case = CASES[r]; rows = []; W = sum(v for _, v in setup_items())
    for i, k in enumerate(case['degs']):
        s0, calls = s0_stream(r, i)
        items = trial_items(r, calls, k); s = sum(v for _, v in items); W += s
        rows.append((i, s0, calls, k, items, s))
    fin = 2 * (3 * ROOT5 + 200) + 2 * (2 * C + 50)
    W += fin
    tl = math.log2(W / C)
    return dict(W=W, rows=rows, fin=fin, time_log2=tl)

def certificate(r):
    case = CASES[r]; i = len(case['degs']) - 1
    s0, _ = s0_stream(r, i); s1 = case['s1']
    A, B = inputs_from_s(s0), inputs_from_s(s1)
    assert A != B and all(x < P for x in A + B)
    enc = lambda t: (t[0].to_bytes(32, 'little') + t[1].to_bytes(32, 'little')).hex()
    return enc(A), enc(B)

if __name__ == '__main__':
    req = json.loads(sys.stdin.read())
    r = int(req['target_profile'].split('-r')[1].split('-')[0])
    ma, mb = certificate(r)
    tot = total(r); n = params(r)[0]
    phases, peak, cw, b1, b4 = memory(r)
    obs = {'gcd_bound_ops': G(n), 'total_ops_W': tot['W'], 'time_log2_x1e6': int(tot['time_log2'] * 1e6),
           'peak_words': peak, 'memory_bytes_4mib_allowance': b4}
    out = {'schema_version': 1, 'trials': []}
    for t in req['trials']:
        out['trials'].append({'trial': t['trial'], 'message_a_hex': ma, 'message_b_hex': mb, 'observations': obs})
    sys.stdout.write(json.dumps(out))
