# Tuple-124 (k=8) 4-Family Shared-Prefix 39-Round SHA-256 Ordinary Collision Construction
# Builds on ePrint 2026/1120 Table 23 and Yukon prior art (d3a46ae6, 04f61e00, 0bb19cb2, 820db8f6).
import sys, json, math, random, struct, hashlib

M = 0xFFFFFFFF
ONES = (1 << 256) - 1
M32, M32_2 = M, M | (M << 128)
M20, M25, M31, M40, ML = (1 << 20) - 1, (1 << 25) - 1, (1 << 31) - 1, (1 << 40) - 1, 2047 << 20
NM20, M64 = ONES ^ M20, (1 << 64) - 1

def _kc(p):
  t = p << 96; x = int(p ** (1 / 3) * (1 << 32))
  while x ** 3 > t: x -= 1
  while (x + 1) ** 3 <= t: x += 1
  return x & M

K = [_kc(p) for p in [q for q in range(2, 170) if all(q % d for d in range(2, q))][:39]]
IV = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
def ror(x, k): return ((x >> k) | (x << (32 - k))) & M
def S0(x): return ror(x, 2) ^ ror(x, 13) ^ ror(x, 22)
def S1(x): return ror(x, 6) ^ ror(x, 11) ^ ror(x, 25)
def s0(x): return ror(x, 7) ^ ror(x, 18) ^ (x >> 3)
def s1(x): return ror(x, 17) ^ ror(x, 19) ^ (x >> 10)
def CH(e, f, g): return (e & f) ^ ((~e) & g & M)
def MAJ(a, b, c): return (a & b) ^ (a & c) ^ (b & c)
def _hw(s): return [int(x, 16) for x in s.split()]

# 160-byte published 39-round SFS collision pair (ePrint 2026/1120 Table 23 / d3a46ae6)
CV_PUB = _hw("aa79ff87 65c5bb49 d0a84bfd 90ccc398 fac64fb6 4ff7998a b1af5ec5 aa1ed4d5")
M_PUB = _hw(
  "8334d670 3813877e f19d46d5 77556fc4 902f98c7 0500282c a4235533 9100e365 "
  "e76f5fe2 5633326d 9d603088 06a64487 a94ae11e b06304ad 43660038 d80d950f"
)
_mpx = list(M_PUB)
_mpx[8:13] = [0xa76f5fe2, 0x5eb3226d, 0xdd603088, 0x00a467b3, 0xa95af91e]

# 60-byte Tuple-124 (k=8) transplant advice (total nonuniform advice = 220 B)
T124_E = (0x95dbb2a8, 0x2c210e77, 0x1e3b4ffd, 0xff00d825)
T124_A = (0x203c1b5a, 0x58bd2ecb, 0xf5a01075, 0xcc8ef209)
T124_W = (0x576d201f, 0x306524bd, 0xc3662028, 0xd80db51f)
FIB, E11_BASE, K4_CUBE = 0x28b7f117, 0x08226d10, 0xf74400ca

def expand(w, n=39):
  w = list(w)
  for i in range(16, n): w.append((w[i - 16] + s0(w[i - 15]) + w[i - 7] + s1(w[i - 2])) & M)
  return w

def expand_w17(w): return (w[1] + s0(w[2]) + w[10] + s1(w[15])) & M

def traj(cv, w16, n=39):
  w = expand(w16, n); A = [cv[3], cv[2], cv[1], cv[0]]; E = [cv[7], cv[6], cv[5], cv[4]]
  for r in range(n):
    t1 = (E[r] + S1(E[r + 3]) + CH(E[r + 3], E[r + 2], E[r + 1]) + K[r] + w[r]) & M
    t2 = (S0(A[r + 3]) + MAJ(A[r + 3], A[r + 2], A[r + 1])) & M
    A.append((t1 + t2) & M); E.append((A[r] + t1) & M)
  return A, E, w

def compress(cv, w16, n=39):
  A, E, _ = traj(cv, w16, n)
  st = [A[n + 3], A[n + 2], A[n + 1], A[n], E[n + 3], E[n + 2], E[n + 1], E[n]]
  return [(st[i] + cv[i]) & M for i in range(8)]

BA, BE, _ = traj(CV_PUB, _mpx)
CA, CE, _ = traj(CV_PUB, M_PUB)
Wp_ = expand(_mpx)
G16, W17PUB = Wp_[16], Wp_[17]
K4_DL = [(M_PUB[i] - _mpx[i]) & M for i in range(16)]
D8, D9, D10, D11 = K4_DL[8], K4_DL[9], K4_DL[10], K4_DL[11]
T8, T9, T10, T11 = 0x087ff000, 0x03010000, 0x087ff000, 0x1fff41a0

def inF(w, D, T): return ((s0((w + D) & M) - s0(w)) & M) == T
def k4_second(w): return [(w[i] + K4_DL[i]) & M for i in range(16)]

# Derived Tuple-124 constants (computed deterministically from advice)
T124_C9 = (T124_E[1] - T124_A[1] - S1(T124_E[0]) - K[9] - (T124_A[1] - S0(T124_A[0])) + FIB) & M
K4_C11 = (T124_A[3] - S0(T124_A[2]) - MAJ(T124_A[2], T124_A[1], T124_A[0])) & M
K4_CA10 = (T124_A[2] - S0(T124_A[1])) & M
K4_W11C = (T124_E[3] - T124_A[3] - K4_C11 - S1(T124_E[2]) - CH(T124_E[2], T124_E[1], T124_E[0]) - K[11]) & M
R2_MASK = 0x08b81020 # E1[13] ^ E2[13] fixed bits on E[11] required for exact round-10 reconvergence
W9C = (
  T124_A[0], (T124_A[1] - S0(T124_A[0])) & M, (T124_A[2] - S0(T124_A[1])) & M, K4_C11,
  T124_A[1] & T124_A[0], T124_A[1] ^ T124_A[0],
  (T124_E[1] - T124_A[1] - S1(T124_E[0]) - K[9]) & M, T124_E[0], (~T124_E[0]) & M,
)

def consts(cv):
  t20 = (S0(cv[0]) + MAJ(cv[0], cv[1], cv[2])) & M; eb = (cv[3] - t20) & M
  k0 = (-t20 - cv[7] - S1(cv[4]) - CH(cv[4], cv[5], cv[6]) - K[0]) & M
  cw = (G16 - s1(T124_W[2]) - T124_C9 - k0 + cv[6] + K[1]) & M
  return cw, eb, cv[0], cv[1], cv[4], cv[5]

def fstep(x, c):
  if x & 1: return (s0(x) - x) & M
  cw, eb, cv0, cv1, cv4, cv5 = c; e0 = (x + eb) & M
  return (cw + S0(x) + MAJ(x, cv0, cv1) + S1(e0) + CH(e0, cv4, cv5) - x) & M

def recover_a1(cv, a0, u):
  t20 = (S0(cv[0]) + MAJ(cv[0], cv[1], cv[2])) & M; e0 = (cv[3] + a0 - t20) & M
  return (u + S0(a0) + MAJ(a0, cv[0], cv[1]) + S1(e0) + CH(e0, cv[4], cv[5]) + cv[6] + K[1]) & M

def kw(cv, a0, a1, a2, a3):
  A = [cv[3], cv[2], cv[1], cv[0], a0, a1, a2, a3, *T124_A]
  E = [cv[7], cv[6], cv[5], cv[4], 0, 0, 0, 0, 0, 0, 0, 0, *T124_E]
  W = [0] * 12 + list(T124_W)
  for r in range(8):
    t1 = (A[r + 4] - S0(A[r + 3]) - MAJ(A[r + 3], A[r + 2], A[r + 1])) & M
    W[r] = (t1 - E[r] - S1(E[r + 3]) - CH(E[r + 3], E[r + 2], E[r + 1]) - K[r]) & M
    E[r + 4] = (A[r] + t1) & M
  for r in range(8, 12):
    t1 = (E[r + 4] - A[r]) & M
    W[r] = (t1 - E[r] - S1(E[r + 3]) - CH(E[r + 3], E[r + 2], E[r + 1]) - K[r]) & M
  return W

def h4ok(a2, a3):
  e11 = (a3 + K4_C11) & M
  if (e11 & R2_MASK) != (E11_BASE & R2_MASK): return 0
  if not inF((K4_W11C - a3) & M, D11, T11): return 0
  t16 = (K4_CA10 - MAJ(T124_A[1], T124_A[0], a3)) & M; e10 = (a2 + t16) & M
  if (e10 ^ e11) >> 30 & 1: return 0
  if ((MAJ(T124_A[0], a3, a2) - CH(T124_E[0], e11, e10)) & M) != FIB: return 0
  w10 = (T124_E[2] - T124_A[2] - e10 - S1(T124_E[1]) - CH(T124_E[1], T124_E[0], e11) - K[10]) & M
  return int(inF(w10, D10, T10))

# --- Exact ALL-48 4-Family Chunked Builder (<= 512 classes/family, Phase-S peak 584,292 B < 1 MiB) ---
def _k4class(a3):
  E11 = (a3 + K4_C11) & M; t16 = (K4_CA10 - MAJ(T124_A[1], T124_A[0], a3)) & M
  C17K = (s1(T124_W[3]) + T124_E[2] - T124_A[2] - S1(T124_E[1]) - CH(T124_E[1], T124_E[0], E11) - K[10]) & M
  return dict(a3=a3, E11=E11, t16=t16, C17K=C17K)

_K4TM = [
  (16, sum(0x0000FFFF << (32 * t) for t in range(8))), (8, sum(0x00FF00FF << (32 * t) for t in range(8))),
  (4, sum(0x0F0F0F0F << (32 * t) for t in range(8))), (2, sum(0x33333333 << (32 * t) for t in range(8))),
  (1, sum(0x55555555 << (32 * t) for t in range(8))),
]

def _k4tr(W, o):
  W = list(W)
  for s_, mk in _K4TM:
    for q in range(16):
      r = q // s_ * 2 * s_ + q % s_; a, b = W[r], W[r + s_]; t = ((a >> s_) ^ b) & mk
      W[r + s_] = b ^ t; W[r] = a ^ ((t << s_) & ONES)
  o[0] += 80 * 22 + 15
  return W

_K4CAP = ((2, 13, 7), (9, 26, 7), (15, 19, 7), (3, 14, 6), (10, 27, 6), (16, 20, 6))
_K4LV = [[[j for j, (a, b, c) in enumerate(_K4CAP) if (c >> s) & 1 and a < i <= b] for i in range(33)] for s in range(3)]
K4_STOP = 160

def _k4st(i, st, x, K_, T_, A7, E1, L, o):
  s, cy, bw, b10, cv = st; g = s - 1; cp = dict(zip(_K4LV[s][i], cv))
  if o is not None: o[0] += K4_STOP * ((L.bit_length() + 255) >> 8)
  Y = T_ ^ (L * (x ^ cy))
  mj = (A7 | (L * x)) if (T124_A[0] >> i) & 1 else (A7 & (L * x))
  ch = E1 if (T124_E[0] >> i) & 1 else Y
  ok = L ^ mj ^ ch ^ (L * (bw ^ ((FIB >> i) & 1))); W = K_ ^ (L * (x ^ b10))
  for j in _K4LV[s][i]:
    if _K4CAP[j][1] == i:
      c = cp.pop(j); ok &= W if (1 ^ c, 1 ^ c, c, c ^ g, c ^ g, 1 ^ c ^ g)[j] else (L ^ W)
  if i == 30: ok &= (L ^ W if s else W) & (L ^ Y ^ E1)
  if i == 31 and s: ok &= W if g else (L ^ W)
  V = [
    L if (x & cy) else (T_ if (x | cy) else 0),
    ((L ^ mj) & ch) | ((L ^ mj ^ ch) & (L * bw)),
    L if (x & b10) else ((L ^ K_) if (x | b10) else 0),
  ]
  nj = [j for j in _K4LV[s][i + 1] if j not in cp]
  if nj: V.append(W)
  P_ = [(ok, 0)] if ok else []
  for t, v in enumerate(V): P_ = [(q, b | (e << t)) for p, b in P_ for q, e in ((p & v, 1), (p & ~v, 0)) if q]
  R = []
  for p, b in P_:
    if nj: cp[nj[0]] = b >> 3
    R.append(((s, b & 1, (b >> 1) & 1, (b >> 2) & 1, tuple(cp[j] for j in _K4LV[s][i + 1])), p))
  return R

def _k4build_all48():
  o = [0]; by_f = {}; m = 0
  while True:
    a3 = ((E11_BASE | m) - K4_C11) & M
    if inF((K4_W11C - a3) & M, D11, T11):
      c = _k4class(a3); kap = (c["t16"] - c["C17K"]) & M
      by_f.setdefault(kap & 0x003FFFFF, []).append((kap, c))
    m = (m - K4_CUBE) & K4_CUBE
    if not m: break
  fam_lo22 = tuple(sorted(by_f)); assert len(fam_lo22) == 4
  raw_groups = []; fam_blks = []
  # Process ONE family (512 candidate classes = 64 B mask) at a time; free F before DFS and trans before transpose
  for lo22 in fam_lo22:
    Cf = sorted(by_f[lo22], key=lambda t: (t[0], t[1]["a3"]))
    L = (1 << len(Cf)) - 1
    V = [((c["C17K"] - s1(T124_W[3]) - c["t16"]) & M, c["t16"], c["a3"], c["E11"]) for _, c in Cf]
    PL = [[sum(((v[q] >> b) & 1) << l for l, v in enumerate(V)) for q in range(4)] for b in range(32)]
    o[0] += 128 * len(Cf)
    F = [None] * 33; F[32] = {(s, a, b, c, ()): L for s in range(3) for a in (0, 1) for b in (0, 1) for c in (0, 1)}
    trans = [{} for _ in range(18)]
    for i in range(31, -1, -1):
      D = {}; Fi1 = F[i + 1]; rec = i < 18
      if rec: Ti = trans[i]
      K_, T_, A7, E1 = PL[i]
      for s in range(3):
        n = len(_K4LV[s][i])
        for v in range(8 << n):
          st = (s, v & 1, (v >> 1) & 1, (v >> 2) & 1, tuple((v >> (3 + j)) & 1 for j in range(n)))
          t0_ = [(ns, p & Fi1[ns]) for ns, p in _k4st(i, st, 0, K_, T_, A7, E1, L, o) if ns in Fi1 and (p & Fi1[ns])]
          t1_ = [(ns, p & Fi1[ns]) for ns, p in _k4st(i, st, 1, K_, T_, A7, E1, L, o) if ns in Fi1 and (p & Fi1[ns])]
          a = 0
          for _, pm in t0_: a |= pm
          for _, pm in t1_: a |= pm
          if a:
            D[st] = a
            if rec: Ti[st] = (t0_, t1_)
      F[i] = D
    active = 0
    for s in range(3): active |= F[0].get((s, 0, 0, 0, ()), 0)
    gmasks = []; i = 0
    while i < len(Cf):
      j = i; kap = Cf[i][0]
      while j < len(Cf) and Cf[j][0] == kap: j += 1
      cs = []; gm = 0; l0 = None
      for l in range(i, j):
        if (active >> l) & 1:
          cs.append(Cf[l][1]["a3"]); gm |= 1 << l
          if l0 is None: l0 = l
      if cs:
        K_, T_, A_, E_ = V[l0]
        st = next((s, 0, 0, 0, ()) for s in range(3) if (F[0].get((s, 0, 0, 0, ()), 0) >> l0) & 1)
        p32 = 0
        for bi_ in range(32):
          for x in (0, 1):
            for ns, _ in _k4st(bi_, st, x, (K_ >> bi_) & 1, (T_ >> bi_) & 1, (A_ >> bi_) & 1, (E_ >> bi_) & 1, 1, o):
              if (F[bi_ + 1].get(ns, 0) >> l0) & 1: p32 |= x << bi_; st = ns; break
            else: continue
            break
        gmasks.append(gm); raw_groups.append((kap, tuple(cs), (p32, Cf[l0][1]["a3"])))
      i = j
    init = {}
    for s in range(3):
      st = (s, 0, 0, 0, ()); q = F[0].get(st, 0)
      if q: init[st] = q
    F = None
    pf = []; stack = [(0, 0, init)]
    while stack:
      bi, pref, sm = stack.pop(); o[0] += 8
      if bi == 18:
        lm = 0
        for mk in sm.values(): lm |= mk
        for gm in gmasks: assert lm & gm
        pf.append(pref); continue
      Ti = trans[bi]; n0 = {}; n1 = {}
      for st, mk in sm.items():
        t0_, t1_ = Ti[st]
        for ns, pm in t0_:
          q = mk & pm
          if q: n0[ns] = n0.get(ns, 0) | q
        for ns, pm in t1_:
          q = mk & pm
          if q: n1[ns] = n1.get(ns, 0) | q
      if n1: stack.append((bi + 1, pref | (1 << bi), n1))
      if n0: stack.append((bi + 1, pref, n0))
    trans = None; B = []
    for idx in range(0, len(pf), 256):
      W_ = [0] * 32; o[0] += 96; chunk = pf[idx : idx + 256]
      for j, v in enumerate(chunk): W_[j & 31] |= v << (32 * (j >> 5)); o[0] += 12
      B.append((tuple(_k4tr(W_, o)[:18]), len(chunk)))
    fam_blks.append(tuple(B))
  raw_groups.sort(key=lambda g: g[0])
  mid_d1 = tuple(sorted({g[0] & 0x1FC00000 for g in raw_groups}))
  top_d2 = tuple(sorted({g[0] & 0xE0000000 for g in raw_groups}))
  assert len(mid_d1) == 3 and len(top_d2) == 4
  fam_gidx = [[[-1] * 4 for _ in range(3)] for _ in range(4)]
  for gi, (kap, cs, sm) in enumerate(raw_groups):
    fi = fam_lo22.index(kap & 0x003FFFFF); d1i = mid_d1.index(kap & 0x1FC00000); d2i = top_d2.index(kap & 0xE0000000)
    assert ((fam_lo22[fi] + mid_d1[d1i] + top_d2[d2i]) & M) == kap
    fam_gidx[fi][d1i][d2i] = gi
  K4_FAM_ = tuple((fam_lo22[fi], (fam_lo22[fi] + W17PUB) & M, fam_blks[fi], tuple(tuple(r) for r in fam_gidx[fi])) for fi in range(4))
  return tuple(raw_groups), K4_FAM_, fam_lo22, mid_d1, top_d2, o[0]

K4_Q, K4_FAM, FAM_LO22, MID_D1, TOP_D2, _K4_BUILD_OPS = _k4build_all48()
K4_NG, K4_NC = len(K4_Q), sum(len(g[1]) for g in K4_Q)
K4_BLKS, K4_UPREF = sum(len(f[2]) for f in K4_FAM), sum(sum(n for _, n in f[2]) for f in K4_FAM)
K4_S = [NM20 | l for l in range(256)]

# --- Folded Bit-Sliced Walk Kernel Generator (exact match to d3a46ae6 / 04f61e00) ---
OP_XOR, OP_AND, OP_OR, OP_NOT = 0, 1, 2, 3
Z0, O1 = (-1, 0), (-1, 1)

class Gen:
  def __init__(s, nin): s.nin = nin; s.recs = []
  def add(s, op, a, b=-1): nid = s.nin + len(s.recs); s.recs.append((op, a, b)); return nid
  def X(s, a, b):
    if a[0] < 0 and b[0] < 0: return (-1, a[1] ^ b[1])
    if a[0] < 0: return (b[0], b[1] ^ a[1])
    if b[0] < 0: return (a[0], a[1] ^ b[1])
    if a[0] == b[0]: return (-1, a[1] ^ b[1])
    return (s.add(OP_XOR, a[0], b[0]), a[1] ^ b[1])
  def NOTm(s, a): return (s.add(OP_NOT, a[0]), 0)
  def A(s, a, b, orr=0):
    if a[0] < 0 or b[0] < 0:
      if a[0] < 0: a, b = b, a
      return (-1, 1 if orr else 0) if ((b[1] == 0) != bool(orr)) else a
    if a[0] == b[0]: return a if a[1] == b[1] else (-1, 1 if orr else 0)
    if a[1] == b[1]:
      op = (OP_OR if orr else OP_AND) if a[1] == 0 else (OP_AND if orr else OP_OR)
      return (s.add(op, a[0], b[0]), a[1])
    if a[1] == 1: a, b = b, a
    nb = s.add(OP_NOT, b[0])
    return (s.add(OP_OR if orr else OP_AND, a[0], nb), 0)
  def O(s, a, b): return s.A(a, b, 1)
  def full(s, a, b, c, ncy):
    cs = [v for v in (a, b, c) if v[0] < 0]; vs = [v for v in (a, b, c) if v[0] >= 0]
    if len(cs) == 0:
      if a[1] == b[1] == c[1]: p, x, y = c, a, b
      else:
        arr = (a, b, c)
        idx = 0 if (a[1] != b[1] and a[1] != c[1]) else (1 if (b[1] != a[1] and b[1] != c[1]) else 2)
        p = arr[idx]; x, y = [arr[k] for k in range(3) if k != idx]
      u = s.X(x, p); sm = s.X(u, y)
      return (sm, Z0) if not ncy else (sm, s.X(s.A(u, s.X(y, p)), p))
    if len(cs) == 1:
      x, y = vs; k = cs[0]; t = s.X(x, y); p = x if x[1] == k[1] else y; sm = s.X(t, k)
      if not ncy: return sm, Z0
      cy = (s.O(p, t) if k[1] else s.A(p, (t[0], 0))) if x[1] != y[1] else (s.O(x, y) if k[1] else s.A(x, y))
      return sm, cy
    if len(cs) == 2:
      k = cs[0][1] ^ cs[1][1]; x = vs[0]
      return s.X(x, (-1, k)), (x if cs[0][1] != cs[1][1] else (-1, cs[0][1]))
    sm_v = cs[0][1] + cs[1][1] + cs[2][1]
    return (-1, sm_v & 1), (-1, 1 if sm_v >= 2 else 0)

def build_folded(c5v, src_bank, dst_bank, dpb):
  cw, eb, Pv, Rv, Gv = c5v; g = Gen(65)
  x = [(src_bank * 32 + j, 0) for j in range(32)]; nx0 = g.NOTm(x[0]); xe = [Z0] + x[1:]
  u = [None] * 32; e0 = [None] * 32; cy = Z0
  for j in range(32):
    u[j] = g.X(xe[j], xe[(j + 11) & 31])
    e0[j], cy = g.full(xe[j], (-1, (eb >> j) & 1), cy, j < 31)
  x0p = lambda p: (nx0[0], 1) if p else x[0]
  def mux0(od, ev, wp):
    if od == ev: return od
    if ev[0] < 0: xp = x0p(od[1] ^ ev[1]); return g.A(od, (xp[0], xp[1] ^ ev[1]), ev[1])
    if od[0] < 0: no = 1 - od[1]; xp = x0p(ev[1] ^ no); return g.A(ev, (xp[0], xp[1] ^ no), od[1])
    y = g.X(od, ev); uo = (wp != od[1]) if (wp >= 0 and od[1] != ev[1]) else (y[1] == 1)
    xp = x0p(y[1] ^ uo); return g.X(od if uo else ev, g.A((xp[0], xp[1] ^ uo), y))
  cwe = (cw + Pv + 1 + (Gv & ~Rv & ~1) + (((eb ^ Gv) & 1) if (Rv & 1) else (Gv & 1)) + (~Pv & 1)) & M
  nxtb = []; res = [None] * 32; cy = Z0
  for j in range(32):
    k7 = (j + 7) & 31; uoj = g.X(u[k7], O1) if k7 in (0, 21) else u[k7]
    od = g.X(uoj, x[j + 3] if j + 3 < 32 else Z0); b = []
    if (cwe >> j) & 1: b.append(O1)
    b.extend(nxtb)
    if j > 0 and ((Rv >> j) & 1): b.append(g.X(e0[j], (-1, (Gv >> j) & 1)))
    b.append(g.X(u[(j + 2) & 31], xe[(j + 22) & 31]))
    b.append(g.X(g.X(e0[(j + 6) & 31], e0[(j + 11) & 31]), e0[(j + 25) & 31]))
    nxtb = []; hnx = j > 0 and not ((Pv >> j) & 1); tgt = 1 if (j == 0 or hnx) else 2
    while len(b) > tgt:
      take = 2 if len(b) == tgt + 1 else 3
      sm, c2 = g.full(b[0], b[1], b[2] if take == 3 else Z0, j < 31); b = b[take:]
      if sm != Z0: b.append(sm)
      if j < 31 and c2 != Z0: nxtb.append(c2)
    if not hnx and len(b) == 2 and od[1] == 0 and b[0][1] == 0 and b[1][1] == 1: b[0], b[1] = b[1], b[0]
    sev = b[0] if len(b) >= 1 else Z0
    cev = Z0 if j == 0 else ((x[j][0], 1) if hnx else (b[1] if len(b) >= 2 else Z0))
    if j == 0: res[0] = mux0((od[0], od[1] ^ 1), sev, 0); cy = g.A(od, x0p(od[1]))
    else:
      nxj = (x[j][0], 1)
      if cev[0] >= 0 and cev[1] == 0: aj = mux0(od, sev, cy[1]); bj = mux0(nxj, cev, aj[1] ^ cy[1])
      else: bj = mux0(nxj, cev, -1); aj = mux0(od, sev, bj[1] ^ cy[1])
      res[j], cy = g.full(aj, bj, cy, j < 31)
    if res[j][1]: res[j] = g.NOTm(res[j])
  acc = res[0]
  for j in range(1, dpb): acc = g.O(acc, res[j])
  return g, res, acc

def allocate(g, outs, acc, dst_bank, dpreg=64):
  out_nids = [g.add(OP_NOT, r[0]) if r[1] else r[0] for r in outs]; accn = acc[0]
  n = g.nin + len(g.recs); last = [-1] * n; forced = [-1] * n
  reg = [i if i < g.nin else -1 for i in range(n)]
  for i, (_, ta, tb) in enumerate(g.recs):
    if ta >= 0: last[ta] = g.nin + i
    if tb >= 0: last[tb] = g.nin + i
  for j, nid in enumerate(out_nids): forced[nid] = dst_bank * 32 + j; last[nid] = 10 ** 9
  forced[accn] = dpreg; last[accn] = 10 ** 9; freelist = []; nxt = 65; out_recs = []
  for i, (op, ta, tb) in enumerate(g.recs):
    nid = g.nin + i; dying = []
    if ta >= g.nin and last[ta] == nid: dying.append(ta)
    if tb >= g.nin and last[tb] == nid and tb != ta: dying.append(tb)
    if forced[nid] >= 0: d = forced[nid]
    elif dying: d = reg[dying.pop(0)]
    elif freelist: freelist.sort(); d = freelist.pop(0)
    else: d = nxt; nxt += 1
    for dy in dying: freelist.append(reg[dy])
    reg[nid] = d; out_recs.append((op, d, reg[ta], reg[tb] if tb >= 0 else 0))
  return out_recs, acc[1], nxt

def to_source(recs, name):
  ops = ("^", "&", "|"); lines = [f"def {name}(R):"]
  for op, d, a, b in recs:
    lines.append(f" R[{d}]=R[{a}]^M" if op == OP_NOT else f" R[{d}]=R[{a}]{ops[op]}R[{b}]")
  return "\n".join(lines)

def c5(c):
  cw, eb, cv0, cv1, cv4, cv5 = c
  return (cw + (cv0 & cv1)) & M, eb, cv0 ^ cv1, cv4 ^ cv5, cv5

def make_kernels_folded(c, dpb):
  ks = []
  for src, dst in ((0, 1), (1, 0)):
    g, out, acc = build_folded(c5(c), src, dst, dpb)
    recs, dppol, nreg = allocate(g, out, acc, dst, dpreg=64)
    ns = {"M": ONES}; exec(to_source(recs, "k"), ns)
    ks.append(dict(recs=recs, dppol=dppol, nreg=nreg, fn=ns.pop("k")))
  return ks

# --- 256-Bit Word Machine and Attack Simulator ---
HIGHMASK = [sum(1 << p for p in range(256) if (p >> k) & 1) for k in range(8)]
C_LOG16 = sum(r << ((5 * ((1 << r) - ((1 << r) >> 7))) & 255) for r in range(16))

class Mach:
  def __init__(s): s.o = 0; s.cat = {}
  def x(s, a, b): s.o += 1; return a ^ b
  def a(s, a, b): s.o += 1; return a & b
  def r(s, a, b): s.o += 1; return a | b
  def n(s, a): s.o += 1; return a ^ ONES
  def ad(s, a, b): s.o += 1; return (a + b) & ONES
  def sb(s, a, b): s.o += 1; return (a - b) & ONES
  def sl(s, a, k): s.o += 1; return (a << k) & ONES
  def sr(s, a, k): s.o += 1; return a >> k
  def rl(s, a, k): s.o += 1; k %= 256; return a if k == 0 else ((a << k) | (a >> (256 - k))) & ONES
  def rr(s, a, k): return s.rl(a, 256 - (k % 256))
  def ne(s, a, b): s.o += 1; return 1 if a != b else 0
  def jz(s, a): s.o += 2; return a == 0
  def jnz(s, a): s.o += 2; return a != 0
  def jeq(s, a, b): s.o += 2; return a == b
  def jne(s, a, b): s.o += 2; return a != b
  def jge(s, a, b): s.o += 2; return a >= b
  def ld(s, arr, i): s.o += 3; return arr[i]
  def st(s, arr, i, v): s.o += 3; arr[i] = v
  def mv(s): s.o += 1
  def tick(s, name, t0): s.cat[name] = s.cat.get(name, 0) + (s.o - t0)

def mS0(m, v): d = m.r(v, m.sl(v, 32)); return m.x(m.x(m.sr(d, 2), m.sr(d, 13)), m.sr(d, 22))
def mS1(m, v): d = m.r(v, m.sl(v, 32)); return m.x(m.x(m.sr(d, 6), m.sr(d, 11)), m.sr(d, 25))
def ms0(m, v): d = m.r(v, m.sl(v, 32)); return m.x(m.x(m.sr(d, 7), m.sr(d, 18)), m.sr(v, 3))
def mCH(m, e, f, g): return m.x(m.a(e, f), m.a(m.x(e, M32), g))
def s32(m, a, b): return m.a(m.sb(a, b), M32)

class P:
  DPB, MAXS, CUTP, WIN = 7, 1536, 512, 1 << 26
  KTRY, DTRY, QCAP, QFULL, WHEEL = 32, 8192, 640, 384, 2048
  WDIG = ((5, 1), (7, 1), (10, 1), (11, 1), (12, 1), (13, 1))
  GCAP, RCAP, KCAP, KCAP0, SCREEN, CMP1, D0, KRES = 575000, 206, 679, 710, 1, 10, 82, 6

def table_words(wdig=P.WDIG): return sum(sg * (1 << k) for k, sg in wdig)

def pop32_swar(x):
  x -= (x >> 1) & 0x55555555; x = (x & 0x33333333) + ((x >> 2) & 0x33333333)
  x = (x + (x >> 4)) & 0x0f0f0f0f; x += x >> 8; x += x >> 16
  return x & 63

def k4_scr(cv):
  _, eb_, P_, R_ = c5(consts(cv))[:4]
  return (3 * pop32_swar(R_ & 0x00F27618) + 2 * pop32_swar(R_ & 0x7F0D89E6)
          + 2 * ((eb_ >> 1) & 1) + ((eb_ >> 2) & 1) + ((P_ >> 31) & 1) - pop32_swar(P_ & 0x1FFFFFFE))

K4_PASS_WC = 748 + 4 * 295 + 52 * (308 + 3 * 71 + 12 * 31)
K4_GUARD_G11, K4_GUARD_G13, K4_GUARD_G14, K4_GUARD_G15 = 55000, 55000, 55000, 62000
WMAX_CAP = 470000000

class CapStop(Exception): pass

class Attack:
  def __init__(s, win=P.WIN, seed=1, check=False, k4=False, screen=None, wmax=1 << 60):
    s.wmax = wmax; s.screen = P.SCREEN if screen is None else screen; s.k4 = k4
    s.m = Mach(); s.win = win; s.check = check; s.dpreg = 64; s.W = table_words()
    s.ks = None; s.R = [0] * 256; s.rnd = random.Random(seed)
    s.st = dict(f9=0, f8=0, claws_distinct=0); s.idc0 = 256; s.distinct = set()
    s.cv_id = 0; s.cv_try = False; s.measure = True; s.LA = [0] * 256; s.sav = [0] * 32
    s.C9 = T124_C9; s.C9P = s.C9 | (1 << 64); s.gR = None; s.gl = 0; s.gk = ""
    s.k4D = []; s.m0 = None; s.found = None; s.success = False; s._k4C = None; s.ws_ops = 0

  def ws(s, cv=None):
    m = s.m; t0 = m.o; s.m0 = None; s.skip = False; tries = drops = 0
    while True:
      drawn = cv is None or s.cv_try
      if drawn:
        blk = [s.rnd.getrandbits(32) for _ in range(16)]; m.o += 18; s.m0 = blk
        cv = compress(IV, blk); m.o += 2812
      s.cv_try = True
      if drawn and s.screen:
        t_ = m.o; m.o += 4; S = k4_scr(cv); m.o += 65
        if S > 5: m.o += 3
        if s.check: s.__dict__.setdefault("scr", []).append((S, m.o - t_))
        if S > 5:
          s.st["ddraws"] = s.st.get("ddraws", 0) + 1; drops += 1
          if drops >= P.DTRY: s.skip = True; return
          continue
      ks_try = make_kernels_folded(consts(cv), P.DPB); gops = P.GCAP
      kcap = P.KCAP if s.screen else P.KCAP0
      if len(ks_try[0]["recs"]) <= kcap and max(ks_try[0]["nreg"], ks_try[1]["nreg"]) <= P.RCAP: break
      m.o += gops + 142; tries += 1
      if tries >= P.KTRY: s.skip = True; return
    s.cv = cv; s.cv_id += 1; s.c = consts(cv); m.o += 140
    s.CA1 = (cv[6] + K[1] - s.c[0]) & M32; s.ks = ks_try; m.o += gops + 8 * len(s.ks[0]["recs"])
    s.tab = [0] * s.W; m.o += 4 * s.W; s.qn = 0; s.qw = [0] * (P.QCAP // 4 + 1)
    s.cur = 0; s.it = 0; s.s2 = None; s.cut0 = s.cut1 = s.cut2 = 0; s.cut_at = P.CUTP; m.o += 5
    for j in range(32): s.R[j] = sum(1 << l for l in range(256) if (l >> j) & 1) if j < 8 else 0
    m.o += 32
    if s.win > (1 << 21):
      for l in range(256): s.LA[l] = K4_S[l]; m.o += 2
    else:
      for l in range(256): s.LA[l] = NM20 | l; m.o += 3
    s.idc = s.idc0; s._k4C = None; s.ws_ops = m.o; m.tick("window_setup", t0)

  def il(s, base, low, l, val, nbits=20):
    m = s.m; R = s.R; m.o += 2
    Z = m.rl(val, l) if l is not None else val; nl = m.n(low)
    for j in range(nbits):
      t = Z if j == 0 else m.rr(Z, j); p = R[base + j]; R[base + j] = m.x(p, m.a(m.x(p, t), low))
    for j in range(nbits, 32): R[base + j] = m.a(R[base + j], nl)

  def ex(s, base, jlo, jhi, low, l):
    m = s.m; R = s.R; m.o += 2; Z = m.a(R[base + jhi], low)
    for j in range(jhi - 1, jlo - 1, -1): Z = m.r(m.rl(Z, 1), m.a(R[base + j], low))
    return m.rr(Z, l) if l is not None else Z

  def k4d(s, a, u):
    t0 = s.m.o; o = 0
    if s._k4C is None: s._k4C = ([0] * 1536, [0] * 6, 0); o = 6172
    keys, bmp, cnt = s._k4C; p = (a << 32) | u; x = a ^ u; h = ((x << 10) + (x << 9)) >> 32; o += 7; n = 0
    while True:
      o += 9; z = h >> 8; b = h & 255
      if not ((bmp[z] >> b) & 1):
        o += 2; n = int(cnt < 944)
        if n: keys[h] = p; bmp[z] |= 1 << b; s._k4C = (keys, bmp, cnt + 1); o += 12
        break
      o += 5
      if keys[h] == p: n = 0; break
      h += 1; o += 3
      if h == 1536: h = 0; o += 1
    s.m.o += o; s.m.tick("k4", t0); return n

  def k4_eval(s, a0, a1, u):
    m = s.m; t0 = m.o
    try: s.cap(K4_GUARD_G11, "g11"); s.k4q(a0, a1, u); s.k4D.append((a0, u))
    finally: m.tick("k4", t0)

  def k4q(s, a0, a1, u):
    m = s.m; s.st["k4q"] = s.st.get("k4q", 0) + K4_UPREF; m.o += 624
    cv0, cv1, cv2, cv4, cv5 = s.cv[0], s.cv[1], s.cv[2], s.cv[4], s.cv[5]
    a0c0 = m.x(a0, cv0); z = m.a(a0, cv0); maj0 = m.x(z, m.a(cv1, a0c0))
    e1 = s32(m, m.sb(m.ad(cv2, a1), mS0(m, a0)), maj0); e0 = m.ad(a0, s.c[1]); maj1 = m.x(z, m.a(a1, a0c0))
    w = s32(m, m.sb(m.sb(m.sb(m.sb(m.sb(0, mS0(m, a1)), maj1), cv5), mS1(m, e1)), mCH(m, e1, e0, cv4)), K[2]) & M32
    WB = []
    for i in range(18): m.o += 3; WB.append(ONES if (w >> i) & 1 else 0)
    for lo22, lo22_w17, blks, gidx in K4_FAM:
      m.o += 13; r0 = (lo22_w17 - u - w) & M; buf0 = []
      for q in range(22): m.o += 3; buf0.append(ONES if (r0 >> q) & 1 else 0)
      r1_val = buf1 = None; r2_val = [None, None, None]; buf2 = [None, None, None]
      for P_, nlanes in blks:
        LM = (1 << nlanes) - 1; y = [0] * 32; c = k = acc = 0
        for i in range(18):
          p = m.ld(P_, i); t = m.x(p, WB[i]); y[i] = t if i == 0 else m.x(t, c)
          if i < 17: c = m.a(p, WB[i]) if i == 0 else m.r(m.a(p, WB[i]), m.a(t, c))
        for i in range(22):
          bi_ = buf0[i]; t = m.x(y[i], bi_); v = t if i == 0 else m.x(t, k)
          k = m.a(y[i], bi_) if i == 0 else m.r(m.a(y[i], bi_), m.a(t, k))
          if i < 14: y[18 + i] = m.x(m.x(v, y[i + 7]), y[i + 3])
          else:
            e = m.x(v, m.x(m.x(y[(i + 7) & 31], y[i - 14]), y[i + 3]))
            acc = e if i == 14 else m.r(acc, e)
        if not m.jnz(m.a(m.n(acc), LM)): m.o += 4; continue
        if r1_val is None:
          r1_val = []; buf1 = []
          for d1_off in MID_D1:
            m.o += 3; rv = (r0 + d1_off) & M; r1_val.append(rv); b1 = []
            for q in range(7): m.o += 3; b1.append(ONES if (rv >> (22 + q)) & 1 else 0)
            buf1.append(b1)
        k22, acc22 = k, acc
        for d1 in range(3):
          k1, acc1 = k22, acc22; alive = True; b1 = buf1[d1]
          for i in range(22, 29):
            bi_ = b1[i - 22]; t = m.x(y[i], bi_); v = m.x(t, k1)
            k1 = m.r(m.a(y[i], bi_), m.a(t, k1))
            acc1 = m.r(acc1, m.x(v, m.x(m.x(y[(i + 7) & 31], y[i - 14]), y[i + 3])))
            if (i == 25 or i == 28) and not m.jnz(m.a(m.n(acc1), LM)): alive = False; break
          if not alive: continue
          if r2_val[d1] is None:
            r2_val[d1] = []; buf2[d1] = []
            for d2_off in TOP_D2:
              m.o += 3; rv = (r1_val[d1] + d2_off) & M; r2_val[d1].append(rv); b2 = []
              for q in range(3): m.o += 3; b2.append(ONES if (rv >> (29 + q)) & 1 else 0)
              buf2[d1].append(b2)
          for d2 in range(4):
            k2, acc2 = k1, acc1; b2 = buf2[d1][d2]
            for i in range(29, 32):
              bi_ = b2[i - 29]; t = m.x(y[i], bi_); v = m.x(t, k2)
              if i < 31: k2 = m.r(m.a(y[i], bi_), m.a(t, k2))
              acc2 = m.r(acc2, m.x(v, m.x(y[(i + 7) & 31], y[i - 14])))
            h2 = m.a(m.n(acc2), LM); m.o += 6
            while m.jnz(h2):
              s.cap(K4_GUARD_G13, "g13")
              lo = h2 & -h2; j = lo.bit_length() - 1; h2 ^= lo; m.o += 3; x = 0
              for b_ in range(32):
                if (y[b_] >> j) & 1: x |= 1 << b_
              m.o += 127; s.st["k4s"] = s.st.get("k4s", 0) + 1
              if s.check: assert s0(x) == ((x + r2_val[d1][d2]) & M)
              a2 = (x - w) & M; w9 = (T124_C9 - a1) & M
              pU = a2 | W9C[0]; pV = a2 & W9C[0]; pP9 = (a1 + W9C[1]) & M; pP10 = (a2 + W9C[2]) & M; m.o += 4
              cs = K4_Q[gidx[d1][d2]][1]
              for a3 in cs:
                s.cap(K4_GUARD_G14, "g14")
                e11 = (a3 + W9C[3]) & M; e10 = (pP10 - (W9C[4] ^ (a3 & W9C[5]))) & M
                e9 = (pP9 - ((a3 & pU) | pV)) & M
                pw9 = (W9C[6] - e9 - ((e11 & W9C[7]) | (e10 & W9C[8]))) & M; m.o += 20
                if pw9 != w9: continue
                m.o += 563; W = kw(s.cv, a0, a1, a2, a3)
                if W[9] != w9 or expand_w17(W) != W17PUB or not inF(W[10], D10, T10): continue
                s.st["k4_w17a"] = s.st.get("k4_w17a", 0) + 1
                for b3 in cs:
                  s.cap(K4_GUARD_G15, "g15"); m.o += 560; Wm = kw(s.cv, a0, a1, a2, b3)
                  if Wm[9] != w9 or expand_w17(Wm) != W17PUB or not inF(Wm[8], D8, T8): continue
                  s.st["k4_w17"] = s.st.get("k4_w17", 0) + 1; m.o += 2 * 2812
                  if compress(s.cv, Wm) == compress(s.cv, k4_second(Wm)):
                    s.found = (s.m0, Wm, k4_second(Wm)); s.success = True
                break

  def claw(s, a, b):
    m = s.m; t0 = m.o
    if m.jnz(m.a(a, 1)): a0, u = b, a
    else: a0, u = a, b
    m.mv()
    if s.measure and (s.cv_id, a0, u) not in s.distinct:
      s.distinct.add((s.cv_id, a0, u)); s.st["claws_distinct"] += 1
    if s.check: assert fstep(a0, s.c) == fstep(u, s.c) and (a0 & 1) == 0 and (u & 1) == 1
    a1u = m.ad(m.ad(ms0(m, u), a0), s.CA1); W9 = m.sb(s.C9P, a1u)
    z9 = ms0(m, m.a(m.r(W9, m.sl(m.ad(W9, D9), 128)), M32_2))
    ok = m.jeq(s32(m, m.sr(z9, 128), z9), T9)
    if s.check:
      a1c = recover_a1(s.cv, a0, u); Wk = kw(s.cv, a0, a1c, *K4_Q[0][2]); Wx = expand(Wk, 18)
      assert (W9 & M32) == ((T124_C9 - a1c) & M) == Wk[9] and Wx[16] == G16 and Wk[1] == u and ok == inF(Wk[9], D9, T9)
    m.tick("claw_filter", t0)
    if not ok: return 0
    s.st["f9"] += 1; a1 = m.a(a1u, M32)
    if s.k4 and s.k4d(a0, u): s.k4_eval(a0, a1, u)
    return int(s.success)

  def wr(s, word, w, w1, word1, rsh, st2, sh, d):
    m = s.m; m.st(s.tab, word, m.x(w, m.sl(d, sh))); m.o += 2
    if st2: m.st(s.tab, word1, m.x(w1, m.sr(d, rsh)))

  def hit(s, l, r):
    m = s.m; m.o += 11; bk = (r + (r << 5) + (r << 6)) >> 15; pos = (bk << 5) + (bk << 3)
    word = pos >> 8; sh = pos & 255; chk = r & 511
    w = m.ld(s.tab, word); v = m.sr(w, sh); w1 = word1 = rsh = 0; m.o += 2; st2 = sh >= 217
    if st2: m.o += 2; word1 = word + 1; rsh = 256 - sh; w1 = m.ld(s.tab, word1); v = m.r(v, m.sl(w1, rsh))
    e = m.a(v, M40); lw = m.ld(s.LA, l); en0 = m.ad(lw, s.it20p); m.o += 3
    match = (e >> 31) == chk; e0 = 0
    if match: e0 = m.a(e, M31); match = m.jnz(e0)
    if match:
      ln20 = m.a(en0, NM20)
      if m.jge(e0, ln20): pk = m.r(m.sl(m.sb(e0, ln20), 20), m.a(lw, M20))
      else:
        s.wr(word, w, w1, word1, rsh, st2, sh, m.x(e0, en0))
        pk = m.r(m.sl(m.sb(en0, m.a(e0, NM20)), 20), m.a(e0, M20))
      wi = s.qn >> 2; sh_ = s.qn & 3; m.o += 4
      if sh_ == 0: w_ = pk
      else: m.o += 1; w_ = m.r(m.ld(s.qw, wi), m.sl(pk, sh_ << 6))
      m.st(s.qw, wi, w_); s.qn += 1; m.o += 1
    elif m.jge(m.a(en0, ML), m.a(e, ML)):
      s.wr(word, w, w1, word1, rsh, st2, sh, m.x(e, m.r(en0, m.sl(chk, 31))))
    nid = s.idc; m.o += 2
    if nid >= (1 << 20): s.lim = 0; m.o += 1; return
    s.idc = nid + 1; m.o += 1; m.st(s.LA, l, m.sb(nid, s.it20p))
    zi = m.rl(nid, l); s.ZI = m.r(s.ZI, zi) if s.ZI else zi

  def hg(s, G, HL):
    m = s.m; base = s.cur * 32; m.o += 2; s.ZI = 0; Z = s.ex(base, 7, 31, G, None)
    while True:
      more = m.jge(HL, 256)
      if more: l = HL & 255; HL = m.sr(HL, 8); m.o += 1
      else: l = HL
      s.hit(l, m.a(m.rr(Z, l), M25))
      if not more: break
    ZI_ = s.ZI
    for j in range(7): t = ZI_ if j == 0 else m.rr(ZI_, j); s.R[base + j] = m.r(s.R[base + j], m.a(t, G))
    Z = m.x(Z, m.rr(ZI_, 7))
    for j in range(7, 20): t = Z if j == 7 else m.rr(Z, j - 7); s.R[base + j] = m.x(s.R[base + j], m.a(t, G))

  def cl(s, base, l, it20, cthr):
    m = s.m; m.o += 2; lw = m.ld(s.LA, l)
    if m.jge(lw, cthr):
      m.o += 2
      if s.idc < (1 << 20):
        low = m.sl(1, l); nid = s.idc; s.idc = nid + 1; m.o += 1
        m.st(s.LA, l, m.r(nid, it20)); s.il(base, low, l, nid)
      else: s.lim = 0; m.o += 1

  def _find_lane(s, fZ, topk):
    m = s.m; fA = m.a(fZ, m.sb(0, fZ)); fL = 0
    for fK in range(topk, 3, -1):
      fb = m.ne(m.a(fA, HIGHMASK[fK]), 0)
      fL = m.sl(fb, fK) if fK == topk else m.r(fL, m.sl(fb, fK))
    fX = m.sr(fA, fL); fY = m.sb(fX, m.sr(fX, 7))
    return fA, m.r(fL, m.a(m.rr(C_LOG16, m.ad(fY, m.sl(fY, 2))), 15))

  def cutscan(s):
    m = s.m; base = s.cur * 32; m.o += 2; regular = s.it == s.cut_at
    if regular: m.o += 2; regular = s.idc != (1 << 20)
    G = ONES; m.o += 1
    if regular: G = m.n(m.r(s.cut0, m.r(s.cut1, s.cut2)))
    else: s.cut0 = s.cut1 = s.cut2 = 0; m.o += 3
    s.cut2, s.cut1, s.cut0 = s.cut1, s.cut0, 0; s.cut_at = s.it + 512; m.o += 6
    if s.it < 1536: return
    it20 = m.x(NM20, m.sl(s.it, 20)); cthr = m.ad(it20, 1536 << 20); m.o += 2
    if regular:
      while m.jnz(G): low, l = s._find_lane(G, 7); G = m.x(G, low); s.cl(base, l, it20, cthr)
    else:
      for l in range(256): m.o += 3; s.cl(base, l, it20, cthr)

  def bank(s, src, dst):
    m = s.m; m.o += 3
    for j in range(32):
      if src is None: m.st(s.R, dst + j, m.ld(s.sav, j))
      elif dst is None: m.st(s.sav, j, m.ld(s.R, src + j))
      else: x = m.ld(s.R, src + j); m.st(s.R, dst + j, m.ld(s.sav, j)); m.st(s.sav, j, x)
      m.o += 3

  def qins(s, base, low, l, val):
    m = s.m; m.o += 2; wl = m.rl(M20, l); z = m.rl(val, l)
    if m.jz(s.QG): s.QW, s.QZ, s.QG = wl, z, low
    elif m.jnz(m.a(wl, s.QW)): s.il(base, s.QG, None, s.QZ); s.QW, s.QZ, s.QG = wl, z, low
    else: s.QW = m.r(s.QW, wl); s.QZ = m.r(s.QZ, z); s.QG = m.r(s.QG, low)

  def stage2(s, final=0):
    m = s.m; R = s.R; t0 = m.o; sv = s.cur
    if m.jz(s.s2 is not None):
      if final != 2: s.bank(sv * 32, None)
      cur = it2 = bact = live = occ = 0; nf = 128; rec = [0] * 32; wh = [0] * (P.WHEEL // 16)
      fs = [sum((32 * i + j) << (8 * j) for j in range(32)) for i in range(4)]; m.o += 22
    else:
      cur, it2, bact, live, occ, nf, rec, wh, fs = s.s2; m.o += 18
      s.bank(sv * 32 if final != 2 else None, cur * 32)
    qi = 0; qn = s.qn; pw = 0; s.QW = s.QZ = s.QG = 0; m.o += 4
    while True:
      s.cap(15424, "g3")
      wi = m.sr(m.a(it2, P.WHEEL - 1), 4); sh = m.sl(it2, 4); w = m.ld(wh, wi); head = m.a(m.rr(w, sh), 0xFFFF)
      if m.jnz(head):
        m.st(wh, wi, m.x(w, m.rl(head, sh)))
        while True:
          s.cap(12352, "g4")
          q = m.sb(head, 1); v = m.a(m.rr(m.ld(rec, m.sr(q, 3)), m.sl(q, 5)), M32)
          head = m.sr(v, 21); cB = m.a(v, M20); qp = m.x(q, 128); lowq = m.sl(1, q); lowp = m.rl(lowq, 128)
          if m.jnz(m.a(v, 1 << 20)): s.qins(cur * 32, lowp, qp, cB); bact = m.r(bact, lowq)
          elif m.jz(m.a(occ, lowp)):
            s.qins(cur * 32, lowp, qp, cB); occ = m.r(occ, lowp); bact = m.r(bact, m.sl(1, m.a(q, 127)))
          elif m.jnz(nf):
            pN = m.sb(nf, 1); pW = m.ld(fs, m.sr(pN, 5)); r = m.a(m.rr(pW, m.sl(pN, 3)), 255)
            nf = pN; lowr = m.sl(1, r)
            if m.jnz(s.QG): s.il(cur * 32, s.QG, None, s.QZ); s.QG = 0; m.o += 1
            k_ = m.sb(r, q)
            for j_ in range(32): p_ = R[cur * 32 + j_]; R[cur * 32 + j_] = m.x(p_, m.a(m.x(p_, m.rl(p_, k_)), lowr))
            lowrp = m.sl(lowr, 128); s.qins(cur * 32, lowrp, m.ad(r, 128), cB)
            occ = m.r(m.x(occ, lowq), m.r(lowr, lowrp)); bact = m.r(bact, lowr)
          else: occ = m.x(occ, lowq); live = m.sb(live, 1)
          if not m.jnz(head): break
      while True:
        s.cap(15424, "g5")
        if m.jz(pw):
          if m.jge(qi, qn): break
          pw = m.a(m.rr(m.ld(s.qw, m.sr(qi, 2)), m.sl(qi, 6)), M64); qi = m.ad(qi, 1)
        if m.jge(pw, P.D0 << 40):
          hm = m.a(m.n(occ), m.rl(occ, 128))
          if m.jnz(hm): lowq, q = s._find_lane(hm, 7)
          elif m.jge(nf, P.KRES):
            pN = m.sb(nf, 1); q = m.a(m.rr(m.ld(fs, m.sr(pN, 5)), m.sl(pN, 3)), 255); nf = pN; lowq = m.sl(1, q)
          else: break
          iB = m.a(pw, M20); iA = m.a(m.sr(pw, 20), M20); d = m.sr(pw, 40)
          s.qins(cur * 32, lowq, q, iA); occ = m.r(occ, lowq)
          idx = m.ad(it2, d); lwi = m.sr(m.a(idx, P.WHEEL - 1), 4); lsh = m.sl(idx, 4)
          lw_ = m.ld(wh, lwi); hd = m.a(m.rr(lw_, lsh), 0xFFFF); v_ = m.r(iB, m.sl(hd, 21))
          ri = m.sr(q, 3); rs = m.sl(q, 5); rw = m.ld(rec, ri)
          m.st(rec, ri, m.x(rw, m.rl(m.x(m.a(m.rr(rw, rs), M32), v_), rs)))
          m.st(wh, lwi, m.x(lw_, m.rl(m.x(hd, m.ad(q, 1)), lsh)))
        else:
          if not m.jge(nf, P.KRES): break
          iB = m.a(pw, M20); iA = m.a(m.sr(pw, 20), M20); d = m.sr(pw, 40)
          pN = m.sb(nf, 1); q = m.a(m.rr(m.ld(fs, m.sr(pN, 5)), m.sl(pN, 3)), 255)
          nf = pN; lowq = m.sl(1, q); lowqh = m.sl(lowq, 128)
          s.qins(cur * 32, lowq, q, iA); occ = m.r(occ, m.r(lowq, lowqh))
          if m.jz(d): s.qins(cur * 32, lowqh, m.ad(q, 128), iB); bact = m.r(bact, lowq)
          else:
            v_ = m.r(iB, 1 << 20); idx = m.ad(it2, d); lwi = m.sr(m.a(idx, P.WHEEL - 1), 4); lsh = m.sl(idx, 4)
            lw_ = m.ld(wh, lwi); hd = m.a(m.rr(lw_, lsh), 0xFFFF); v_ = m.r(v_, m.sl(hd, 21))
            ri = m.sr(q, 3); rs = m.sl(q, 5); rw = m.ld(rec, ri)
            m.st(rec, ri, m.x(rw, m.rl(m.x(m.a(m.rr(rw, rs), M32), v_), rs)))
            m.st(wh, lwi, m.x(lw_, m.rl(m.x(hd, m.ad(q, 1)), lsh)))
        live = m.ad(live, 1); pw = 0; m.o += 1
      if m.jnz(s.QG): s.il(cur * 32, s.QG, None, s.QZ); s.QG = 0; m.o += 1
      if m.jz(live): break
      if m.jz(pw) and m.jz(final): break
      k = s.ks[cur]; k["fn"](R); m.o += len(k["recs"]); cur ^= 1; it2 += 1; m.o += 2
      base = cur * 32; acc = 0
      for j in range(P.CMP1): pl = R[base + j]; dj = m.x(pl, m.rl(pl, 128)); acc = dj if j == 0 else m.r(acc, dj)
      cand = m.a(m.n(acc), bact)
      if m.jnz(cand):
        acc2 = 0
        for j in range(P.CMP1, 32): pl = R[base + j]; dj = m.x(pl, m.rl(pl, 128)); acc2 = dj if j == P.CMP1 else m.r(acc2, dj)
        full = m.a(cand, m.n(acc2)); pp = R[(cur ^ 1) * 32]; ppd = None
        while m.jnz(full):
          s.cap(17000, "g6"); low, l = s._find_lane(full, 6); full = m.x(full, low); low2 = m.r(low, m.sl(low, 128))
          if ppd is None: ppd = m.x(pp, m.rl(pp, 128))
          if m.jnz(m.a(ppd, low)):
            Z = s.ex((cur ^ 1) * 32, 0, 31, low2, l)
            if s.claw(m.a(Z, M32), m.sr(Z, 128)): s.success = True
          bact = m.x(bact, low); occ = m.x(occ, low2); live = m.sb(live, 1)
          fi = m.sr(nf, 5); fsh = m.sl(nf, 3); fw = m.ld(fs, fi)
          m.st(fs, fi, m.r(m.a(fw, m.rl(ONES ^ 255, fsh)), m.rl(l, fsh))); nf = m.ad(nf, 1)
    s.cap(13376, "g7")
    if m.jnz(live): s.s2 = (cur, it2, bact, live, occ, nf, rec, wh, fs); m.o += 18; s.bank(cur * 32, sv * 32)
    else:
      s.s2 = None
      if final != 2: s.bank(None, sv * 32)
    s.qn = 0; m.tick("stage2", t0)

  def iter1(s):
    m = s.m; R = s.R; k = s.ks[s.cur]; k["fn"](R); m.o += len(k["recs"]); s.cur ^= 1; s.it += 1
    n0 = R[s.dpreg]; m.o += 5
    if m.jne(n0, ONES):
      t0 = m.o; hit = m.n(n0); s.cut0 = m.r(s.cut0, hit); s.it20 = m.sl(s.it, 20); s.it20p = m.ad(s.it20, 1 << 20)
      G = W = HL = G2 = W2 = HL2 = nl = nl2 = 0; m.o += 4
      while True:
        low, l = s._find_lane(hit, 7); hit = m.x(hit, low); wl = m.rl(M25, l)
        cf = m.jnz(m.a(wl, W)) if G else False
        if cf:
          if m.jnz(m.a(wl, W2)) if m.jnz(G2) else False:
            s.cap(13129, "g1"); s.hg(G, HL)
            G, W, HL, nl = G2, W2, HL2, nl2; W2, G2, HL2, nl2 = wl, low, l, 8; m.o += 8
          else: W2 = m.r(W2, wl); G2 = m.r(G2, low); HL2 = m.r(HL2, m.sl(l, nl2)); nl2 = m.ad(nl2, 8)
          if not m.jnz(hit): break
          continue
        if G: W = m.r(W, wl); G = m.r(G, low); HL = m.r(HL, m.sl(l, nl)); nl = m.ad(nl, 8)
        else: W, G, HL, nl = wl, low, l, 8
        if not m.jnz(hit): break
      s.cap(13129, "g1"); s.hg(G, HL)
      if m.jnz(G2): s.cap(13129, "g1"); s.hg(G2, HL2)
      base = s.cur * 32; nd = R[s.dpreg]
      for j in range(20, 32): R[base + j] = m.a(R[base + j], nd)
      full = m.jge(s.qn, P.QFULL); m.tick("hits", t0)
      if full: s.stage2()
    if (not (s.it & 1)) and m.jz(m.a(s.it, P.CUTP - 1)): s.cap(76864, "g2"); s.cutscan()

  def cap(s, R, k=""):
    m = s.m; w = s.wmax
    if w:
      m.o += 2
      if s.gR is not None: assert m.o - s.gl <= s.gR, (s.gk, k, m.o - s.gl, s.gR)
      s.gl = m.o; s.gR = R; s.gk = k
    if w and m.o + R > w: s.st["k4_capped"] = 1; raise CapStop

  def run_window(s, cv=None, iters=None):
    s.success = False; s.ws(cv); s.gR = None
    if s.skip: return s.st
    s.lim = iters if iters else s.win // 256
    try:
      while s.it < s.lim:
        if s.it % 16 == 0: s.cap(15424, "g8")
        s.iter1()
        if s.success: break
      m = s.m; go = (m.jnz(s.qn) or m.jnz(s.s2 is not None)) and m.jz(s.success)
      if go: s.cap(15424, "g9"); s.stage2(final=1)
      if s.win > (1 << 21) and not s.success:
        s.lim = (s.lim * 5) // 4
        while s.it < s.lim and not s.success:
          if s.it % 16 == 0: s.cap(15424, "g8")
          s.iter1()
        go = (m.jnz(s.qn) or m.jnz(s.s2 is not None)) and m.jz(s.success)
        if go: s.cap(15424, "g9"); s.stage2(final=2)
      s.cap(11328, "g10")
    except CapStop: pass
    assert s.wmax is None or s.m.o <= s.wmax
    return s.st

# --- Exact Integer Ledger, Itemized Memory, and Import-Time Structural Assertions ---
G48_W = (
  31536, 107136, 66096, 222336, 378432, 1285632, 793152, 2668032,
  189216, 642816, 396576, 1334016, 80056, 279344, 168352, 588208,
  778320, 2656560, 1632336, 5524848, 382224, 1306784, 801808, 2719776,
  15768, 53568, 33048, 111168, 189216, 642816, 396576, 1334016,
  94608, 321408, 198288, 667008, 166264, 562560, 344664, 1167056,
  1564992, 5318016, 3275328, 11037120, 770016, 2616832, 1610720, 5431168,
)
K4_SETUP = _K4_BUILD_OPS + (1 << 30) + 6512
K4_SETUP_PRICED = 1100000000
K4_MEM = (
  32 * (table_words() + (P.QCAP // 4 + 1) + 18 * K4_BLKS + 256 + 256 + 196 + 129 + 104)
  + 10240 + 4111 * 36 + 2592 * 36 + 4448 + (K4_NG * 16 + K4_NC * 4 + 296)
  + (12288 + 192 + 3076) + 11609 + 32768
)
K4_DIV = 262995543937473 / 53687091200000000
R_LB, EN_LB = 0.939300, 4407641
K4_BW = 15847314634418022685126
K4_N_TOTAL = K4_BW * (WMAX_CAP + 6) + K4_SETUP_PRICED + 2812 * (1 << 43)
CLAIM_TIME_LOG2 = 91.097362

assert (K4_NG, K4_NC, K4_BLKS, K4_UPREF) == (48, 1088, 52, 12928)
assert sum(G48_W) == 62955816
assert table_words() == 15520 and K4_MEM == 883201 and K4_MEM <= (1 << 20)
assert K4_SETUP <= K4_SETUP_PRICED
assert K4_PASS_WC + 1000 < K4_GUARD_G11 and K4_PASS_WC + 583 + 1000 < K4_GUARD_G14 and K4_PASS_WC + 6184 + 1000 < K4_GUARD_G15
assert math.log2(K4_N_TOTAL / 2812) <= CLAIM_TIME_LOG2
assert all(h4ok(*g[2]) for g in K4_Q)

# --- SMC Tail, Mate, and Cross-Claw Engine (100% plain readable Python) ---
class Sw:
  def __init__(w, L):
    w.L = L; w.m = int.from_bytes(M.to_bytes(8, "little") * L, "little")
    w.o = int.from_bytes((1).to_bytes(8, "little") * L, "little")
  def bc(w, c): return (c & M) * w.o
  def rnd(w, rng): return rng.getrandbits(64 * w.L) & w.m
  def S1(w, e): return (((e >> 6) | (e << 26)) ^ ((e >> 11) | (e << 21)) ^ ((e >> 25) | (e << 7))) & w.m
  def S0(w, a): return (((a >> 2) | (a << 30)) ^ ((a >> 13) | (a << 19)) ^ ((a >> 22) | (a << 10))) & w.m
  def s1(w, u): return (((u >> 17) | (u << 15)) ^ ((u >> 19) | (u << 13)) ^ (u >> 10)) & w.m
  def s0(w, v): return (((v >> 7) | (v << 25)) ^ ((v >> 18) | (v << 14)) ^ (v >> 3)) & w.m
  def neg(w, z): return ((z & w.m) ^ w.m) + w.o
  def zero(w, x):
    f = (((x + w.m) >> 32) & w.o) ^ w.o; out = []
    while f: lo = f & -f; out.append((lo.bit_length() - 1) >> 6); f ^= lo
    return out
  def get(w, x, i): return (x >> (64 * i)) & M

PIN = {16: 0x9776869e, 17: 0x771adf7e}
MASK8, MASK9 = 0xCC19E60C, 0xF9983C0F
_CA_TXT = {18: "=u" + "=" * 30}
_CE_TXT = {
  18: "0=======0=====100==000=0=======0", 19: "============u=============n=====",
  20: "======uu=======u================", 22: "=u" + "=" * 30, 23: "=0" + "=" * 30,
}
_LIN = (
  (0, 17, 16, 0, 18, 16, 0), (0, 17, 24, 0, 18, 24, 0), (0, 17, 26, 0, 18, 26, 0),
  (0, 17, 30, 0, 18, 30, 0), (0, 18, 10, 0, 17, 21, 0), (0, 18, 7, 0, 18, 19, 1),
  (0, 18, 9, 0, 18, 18, 1), (1, 17, 5, 1, 18, 5, 0), (1, 17, 19, 1, 18, 19, 0),
)
DA_TAIL = [(BA[t + 4] ^ CA[t + 4], BE[t + 4] ^ CE[t + 4]) for t in range(39)]

def _cell(s):
  m = v = d = 0
  for i, c in enumerate(s):
    b = 1 << (31 - i); m |= b * (c in "01un"); v |= b * (c in "1u"); d |= b * (c in "un")
  return (m, v, M, d)

_EQ = _cell("=" * 32)
_CAr = {t: _cell(_CA_TXT.get(t, "=" * 32)) for t in range(18, 24)}
_CEr = {t: _cell(_CE_TXT.get(t, "=" * 32)) for t in range(18, 24)}
_NF = {t: bin(_CEr[t][0]).count("1") for t in _CEr}

def _fd_tail(cv, w):
  x = traj(cv, w, 39); y = traj(cv, k4_second(w), 39)
  for t in range(16, 39):
    if (x[0][t + 4] ^ y[0][t + 4], x[1][t + 4] ^ y[1][t + 4]) != DA_TAIL[t]: return t
  return 39

def _xd(w):
  w = list(w)
  w[1] = (W17PUB - s1(w[15]) - w[10] - s0(w[2])) & M
  w[0] = (G16 - s1(w[14]) - w[9] - s0(w[1])) & M
  A = {r: BA[r + 4] for r in range(12, 16)}; E = {r: BE[r + 4] for r in range(12, 16)}
  for i in range(15, -1, -1):
    A[i - 4] = (E[i] - A[i] + S0(A[i - 1]) + MAJ(A[i - 1], A[i - 2], A[i - 3])) & M
    E[i - 4] = (E[i] - A[i - 4] - S1(E[i - 1]) - CH(E[i - 1], E[i - 2], E[i - 3]) - K[i] - w[i]) & M
  cv = [A[-1], A[-2], A[-3], A[-4], E[-1], E[-2], E[-3], E[-4]]
  At, Et, _ = traj(cv, w, 21); Bt, Ft, _ = traj(cv, k4_second(w), 21)
  f = lambda t: (At[t] ^ Bt[t]) == (BA[t] ^ CA[t]) and (Et[t] ^ Ft[t]) == (BE[t] ^ CE[t])
  return int(f(22)) * (1 + int(f(23)))

def _members(mask, D, T):
  out = []; sub = 0
  while True:
    if inF(sub, D, T): out.append(sub)
    sub = (sub - mask) & mask
    if sub == 0: return out

def _build_group_dp(gi):
  cs = K4_Q[gi][1]; C = [_k4class(a3) for a3 in cs]; L = (1 << len(C)) - 1
  V = [((c["C17K"] - s1(T124_W[3]) - c["t16"]) & M, c["t16"], c["a3"], c["E11"]) for c in C]
  PL = [[sum(((v[q] >> b) & 1) << l for l, v in enumerate(V)) for q in range(4)] for b in range(32)]
  F = [None] * 33; F[32] = {(s, a, b, c, ()): L for s in range(3) for a in (0, 1) for b in (0, 1) for c in (0, 1)}
  for i in range(31, -1, -1):
    D = {}; Fi1 = F[i + 1]
    for s in range(3):
      n = len(_K4LV[s][i])
      for v in range(8 << n):
        st = (s, v & 1, (v >> 1) & 1, (v >> 2) & 1, tuple((v >> (3 + j)) & 1 for j in range(n))); acc = 0
        for x in (0, 1):
          for ns, p in _k4st(i, st, x, *PL[i], L, None): acc |= p & Fi1.get(ns, 0)
        if acc: D[st] = acc
    F[i] = D
  cls_counts = []; cls_dps = []
  for l in range(len(C)):
    K_, T_, A_, E_ = V[l]; dp = [{} for _ in range(33)]
    for st, mk in F[32].items():
      if (mk >> l) & 1: dp[32][st] = 1
    for i in range(31, -1, -1):
      for st, mk in F[i].items():
        if not ((mk >> l) & 1): continue
        tot = 0
        for x in (0, 1):
          for ns, _ in _k4st(i, st, x, (K_ >> i) & 1, (T_ >> i) & 1, (A_ >> i) & 1, (E_ >> i) & 1, 1, None):
            tot += dp[i + 1].get(ns, 0)
        if tot: dp[i][st] = tot
    cls_counts.append(sum(dp[0].get((s, 0, 0, 0, ()), 0) for s in range(3))); cls_dps.append(dp)
  tot_g = sum(cls_counts); assert tot_g == G48_W[gi]
  def sample(rng):
    u = rng.randrange(tot_g); l = 0
    while u >= cls_counts[l]: u -= cls_counts[l]; l += 1
    K_, T_, A_, E_ = V[l]; dp = cls_dps[l]; st = None
    for s in range(3):
      c = dp[0].get((s, 0, 0, 0, ()), 0)
      if u < c: st = (s, 0, 0, 0, ()); break
      u -= c
    a2 = 0
    for i in range(32):
      for x in (0, 1):
        for ns, _ in _k4st(i, st, x, (K_ >> i) & 1, (T_ >> i) & 1, (A_ >> i) & 1, (E_ >> i) & 1, 1, None):
          c = dp[i + 1].get(ns, 0)
          if u < c: a2 |= x << i; st = ns; break
          u -= c
        else: continue
        break
    return a2, cs[l]
  return cs, sample

class _St: pass
def _cp(s):
  n = _St(); n.xa, n.xe, n.xw = s.xa[:], s.xe[:], s.xw[:]; n.ya, n.ye, n.yw = s.ya[:], s.ye[:], s.yw[:]; return n
def _wd(s, u):
  return s1(s.yw[u - 2]) - s1(s.xw[u - 2]) + s.yw[u - 7] - s.xw[u - 7] + K4_DL[u - 16] + s0(s.yw[u - 15]) - s0(s.xw[u - 15])
def _sconsts(s, t):
  xa, xe, ya, ye = s.xa, s.xe, s.ya, s.ye; i = t + 4
  rx = xa[i - 4] + xe[i - 4] + S1(xe[i - 1]) + CH(xe[i - 1], xe[i - 2], xe[i - 3])
  ry = ya[i - 4] + ye[i - 4] + S1(ye[i - 1]) + CH(ye[i - 1], ye[i - 2], ye[i - 3])
  cx = -xa[i - 4] + S0(xa[i - 1]) + MAJ(xa[i - 1], xa[i - 2], xa[i - 3])
  cy = -ya[i - 4] + S0(ya[i - 1]) + MAJ(ya[i - 1], ya[i - 2], ya[i - 3])
  d = _wd(s, t); de = ry - rx + d
  return cx & M, (rx + K[t]) & M, de & M, (de + cy - cx) & M, d & M, cy & M
def _setrow(s, t, ex):
  cx, rx, de, _, d, cy = _sconsts(s, t); i = t + 4
  s.xe[i] = ex; s.xw[t] = (ex - rx) & M; s.xa[i] = (ex + cx) & M
  s.ye[i] = (ex + de) & M; s.yw[t] = (s.xw[t] + d) & M; s.ya[i] = (s.ye[i] + cy) & M
def _dok(c, D):
  m, v, dm, d = c; cs = 1
  for b in range(32):
    ns = 0; db = (D >> b) & 1
    for cin in (0, 1):
      if (cs >> cin) & 1:
        for xb in (0, 1):
          if ((m >> b) & 1) and xb != ((v >> b) & 1): continue
          if ((dm >> b) & 1) and (db ^ cin) != ((d >> b) & 1): continue
          ns |= 1 << ((xb & db) | (xb & cin) | (db & cin))
    cs = ns
    if not cs: return False
  return True
def _cok(c, x, y): return (x & c[0]) == c[1] and ((x ^ y) & c[2]) == c[3]
def _rowokv(s, t, xw, ex, ax, yw, ye, ay):
  if not (_cok(_CAr[t], ax, ay) and _cok(_CEr[t], ex, ye) and _cok(_EQ, xw, yw)): return False
  if t != 18: return True
  for k1, r1, b1, k2, r2, b2, df in _LIN:
    v1 = (ax if k1 == 0 else ex) if r1 == 18 else (s.xa if k1 == 0 else s.xe)[r1 + 4]
    v2 = (ax if k2 == 0 else ex) if r2 == 18 else (s.xa if k2 == 0 else s.xe)[r2 + 4]
    if (((v1 >> b1) ^ (v2 >> b2)) & 1) != df: return False
  return True
def _look1(s, t, ex, ax, ye, ay):
  i = t + 5; d = _wd(s, t + 1) & M
  if d: return False
  rx = s.xa[i - 4] + s.xe[i - 4] + S1(ex) + CH(ex, s.xe[i - 2], s.xe[i - 3])
  ry = s.ya[i - 4] + s.ye[i - 4] + S1(ye) + CH(ye, s.ye[i - 2], s.ye[i - 3])
  cx = -s.xa[i - 4] + S0(ax) + MAJ(ax, s.xa[i - 2], s.xa[i - 3])
  cy = -s.ya[i - 4] + S0(ay) + MAJ(ay, s.ya[i - 2], s.ya[i - 3])
  de = ry - rx + d
  return _dok(_CAr[t + 1], (de + cy - cx) & M) and _dok(_CEr[t + 1], de & M)
def _cands(s, t, nb, sw, rng):
  cx, rx, de, da, dw, cy = _sconsts(s, t)
  if dw: return []
  mA, vA, _, dA = _CAr[t]; mE, vE, _, dE = _CEr[t]; nx = t < 23; m = sw.m
  xa, xe, ya, ye = s.xa, s.xe, s.ya, s.ye; i = t + 4; bc = sw.bc; S0v, S1v = sw.S0, sw.S1
  DE, CX, DA, NM, VE, DEc, MA, VA, DAc = bc(de), bc(cx), bc(da), bc(~mE), bc(vE), bc(dE), bc(mA), bc(vA), bc(dA)
  if nx:
    CD = bc(ya[i - 3] + ye[i - 3] - xa[i - 3] - xe[i - 3] + _wd(s, t + 1)); CN = bc(xa[i - 3] - ya[i - 3])
    xe1, xe2, ye1, ye2, xa1, xa2, ya1, ya2 = [bc(z) for z in (xe[i - 1], xe[i - 2], ye[i - 1], ye[i - 2], xa[i - 1], xa[i - 2], ya[i - 1], ya[i - 2])]
  good = []
  for _ in range(nb):
    ex = (sw.rnd(rng) & NM) | VE; ey = (ex + DE) & m; ax = (ex + CX) & m; ay = (ax + DA) & m
    bad = (ex ^ ey ^ DEc) | ((ax & MA) ^ VA) | (ax ^ ay ^ DAc)
    if nx:
      deu = (CD + S1v(ey) + (ye2 ^ (ey & (ye1 ^ ye2))) + sw.neg(S1v(ex) + (xe2 ^ (ex & (xe1 ^ xe2))))) & m
      bad |= (deu + S0v(ay) + ((ay & (ya1 | ya2)) | (ya1 & ya2)) + sw.neg(S0v(ax) + ((ax & (xa1 | xa2)) | (xa1 & xa2))) + CN) & m
    good += [sw.get(ex, q) for q in sw.zero(bad)]
  out = []
  for ex in good:
    axv = (ex + cx) & M; yev = (ex + de) & M; xwv = (ex - rx) & M; ywv = (xwv + dw) & M; ayv = (yev + cy) & M
    if not _rowokv(s, t, xwv, ex, axv, ywv, yev, ayv): continue
    if nx and not _look1(s, t, ex, axv, yev, ayv): continue
    if t < 22 and ((s1(ywv) - s1(xwv) + s.yw[t - 5] - s.xw[t - 5] + K4_DL[t - 14] + s0(s.yw[t - 13]) - s0(s.xw[t - 13])) & M): continue
    out.append(ex)
  return out
def _smc_start(w12_15=None):
  s = _St(); s.xa = [0] * 43; s.xe = [0] * 43; s.ya = [0] * 43; s.ye = [0] * 43
  mx = _mpx[:]
  if w12_15 is not None: mx[12:16] = list(w12_15)
  s.xw = mx + [0] * 23; s.yw = [(a + b) & M for a, b in zip(mx, K4_DL)] + [0] * 23
  for r in range(15, 20): s.xa[r], s.xe[r], s.ya[r], s.ye[r] = BA[r], BE[r], CA[r], CE[r]
  for t in (16, 17): _setrow(s, t, PIN[t])
  return s

_SMC_CFG = {18: (512, 8), 19: (2048, 8), 20: (2048, 8), 21: (128, 4), 22: (256, 6), 23: (4, 1)}
def _smc(rng, w12_15=None, np_=100):
  Pt = [_smc_start(w12_15)] * np_; l2 = 0.0; SW = {}
  for t in range(18, 24):
    L, nb = _SMC_CFG[t]; sw = SW.setdefault(L, Sw(L)); pool = []
    for pi, p in enumerate(Pt):
      for ex in _cands(p, t, nb, sw, rng): pool.append((pi << 32) | ex)
    if not pool: return None, None
    l2 += math.log2(len(pool) / (np_ * nb * L)) - _NF[t]; P2 = []
    for _ in range(np_):
      e = pool[rng.randrange(len(pool))]; s2 = _cp(Pt[e >> 32]); _setrow(s2, t, e & M); P2.append(s2)
    Pt = P2
  return Pt, l2

def _finals(s, sw, x8, x9):
  m = sw.m; bc = sw.bc; S0v, S1v, s0v, s1v = sw.S0, sw.S1, sw.s0, sw.s1
  if not hasattr(sw, "kp"): sw.kp = (bc(D8), bc(D9), [bc(K[t]) for t in range(39)])
  kb8, kb9, kb = sw.kp
  xw = [bc(v) for v in s.xw[:24]] + [0] * 15; yw = [bc(v) for v in s.yw[:24]] + [0] * 15
  xw[8], xw[9] = x8, x9; yw[8], yw[9] = (x8 + kb8) & m, (x9 + kb9) & m
  a, b, c, d = [bc(s.xa[i]) for i in (27, 26, 25, 24)]; e, f, g, h = [bc(s.xe[i]) for i in (27, 26, 25, 24)]
  A, B, C, D = [bc(s.ya[i]) for i in (27, 26, 25, 24)]; E, F, G, H = [bc(s.ye[i]) for i in (27, 26, 25, 24)]
  for t in range(24, 39):
    xw[t] = (s1v(xw[t - 2]) + xw[t - 7] + s0v(xw[t - 15]) + xw[t - 16]) & m
    yw[t] = (s1v(yw[t - 2]) + yw[t - 7] + s0v(yw[t - 15]) + yw[t - 16]) & m; k = kb[t]
    t1 = h + S1v(e) + (g ^ (e & (f ^ g))) + k + xw[t]; t2 = S0v(a) + ((a & (b | c)) | (b & c))
    h, g, f, e, d, c, b, a = g, f, e, (d + t1) & m, c, b, a, (t1 + t2) & m
    t1 = H + S1v(E) + (G ^ (E & (F ^ G))) + k + yw[t]; t2 = S0v(A) + ((A & (B | C)) | (B & C))
    H, G, F, E, D, C, B, A = G, F, E, (D + t1) & m, C, B, A, (t1 + t2) & m
  return sw.zero((a ^ A) | (b ^ B) | (c ^ C) | (d ^ D) | (e ^ E) | (f ^ F) | (g ^ G) | (h ^ H))

def _verify_smc_hit(s, w8, w9):
  xw = s.xw[:]; xw[8], xw[9] = w8, w9
  for t in range(23, 15, -1): xw[t - 16] = (xw[t] - s1(xw[t - 2]) - xw[t - 7] - s0(xw[t - 15])) & M
  w = xw[:16]; A = {r: s.xa[r + 4] for r in range(12, 16)}; E = {r: s.xe[r + 4] for r in range(12, 16)}
  for i in range(15, -1, -1):
    A[i - 4] = (E[i] - A[i] + S0(A[i - 1]) + MAJ(A[i - 1], A[i - 2], A[i - 3])) & M
    E[i - 4] = (E[i] - A[i - 4] - S1(E[i - 1]) - CH(E[i - 1], E[i - 2], E[i - 3]) - K[i] - w[i]) & M
  cv = [A[-1], A[-2], A[-3], A[-4], E[-1], E[-2], E[-3], E[-4]]
  return compress(cv, w) == compress(cv, k4_second(w)), (A[0] & 1) * 2 + (w[1] & 1), cv, w, (A[0], A[1], A[2], A[3])

# --- Experiment Runners ---
def _planted_check_all48(cv_base, seed):
  rng = random.Random(seed); found = 0
  for kap, cs, (a2, a3) in K4_Q:
    a0 = rng.getrandbits(32) & ~1; a1 = rng.getrandbits(32); W0 = kw(cv_base, a0, a1, a2, a3)
    c_ = consts(cv_base); e0 = (a0 + c_[1]) & M
    e1 = (cv_base[2] + a1 - S0(a0) - MAJ(a0, cv_base[0], cv_base[1])) & M
    w2b = (-S0(a1) - MAJ(a1, a0, cv_base[0]) - cv_base[5] - S1(e1) - CH(e1, e0, cv_base[4]) - K[2]) & M
    u_target = (kap + W17PUB + a2 - s0((a2 + w2b) & M)) & M
    cv_p = list(cv_base); cv_p[6] = (cv_base[6] + W0[1] - u_target) & M
    Wp = kw(cv_p, a0, a1, a2, a3)
    assert Wp[1] == u_target and expand_w17(Wp) == W17PUB and Wp[9] == ((T124_C9 - a1) & M)
    A = Attack(win=1 << 16, seed=1, check=True, k4=True, screen=0, wmax=1 << 60)
    A.cv = cv_p; A.c = consts(cv_p); A.k4q(a0, a1, u_target)
    assert A.st.get("k4_w17a", 0) >= 1; found += 1
  return found

def _run_transplant(req):
  rows = []
  for t in req["trials"]:
    i = t["trial"]; sd = int(t["seed"][:16], 16); obs = None
    if i == 0:
      sfs_ok = int(compress(CV_PUB, _mpx) == compress(CV_PUB, M_PUB) and _mpx != M_PUB)
      assert sfs_ok == 1 and expand(_mpx, 18)[16] == G16 and expand(_mpx, 18)[17] == W17PUB
      A0, E0, _ = traj(CV_PUB, _mpx, 16); A1, E1, _ = traj(CV_PUB, M_PUB, 16)
      valid = w9_ok = tr_ok = 0; w16s = set()
      for kap, cs, (a2, a3) in K4_Q:
        assert h4ok(a2, a3) == 1; valid += 1
        w = kw(CV_PUB, BA[4], BA[5], a2, a3)
        if w[9] == ((T124_C9 - BA[5]) & M): w9_ok += 1
        w16s.add(expand(w, 18)[16])
        a, e, _ = traj(CV_PUB, w, 16); b, f, _ = traj(CV_PUB, k4_second(w), 16)
        assert a[16:20] == A0[16:20] and e[16:20] == E0[16:20] and b[16:20] == A1[16:20] and f[16:20] == E1[16:20]
        tr_ok += 1
      assert valid == 48 and w9_ok == 48 and tr_ok == 48 and len(w16s) == 1
      planted = _planted_check_all48(CV_PUB, sd); assert planted == 48
      obs = {
        "sfs_collision": sfs_ok, "groups": K4_NG, "classes": K4_NC, "blocks": K4_BLKS,
        "unique_pref": K4_UPREF, "sample_valid": valid, "sample_w9_ok": w9_ok,
        "sample_trail": tr_ok, "sample_w16_one": len(w16s), "planted_48": planted,
        "k4_mem_bytes": K4_MEM, "k4_pass_wc": K4_PASS_WC,
      }
    else:
      rng = random.Random(sd); cv = [rng.getrandbits(32) for _ in range(8)]
      a0 = rng.getrandbits(32) & ~1; u = rng.getrandbits(32) | 1
      c = consts(cv); a1 = recover_a1(cv, a0, u); gi = sd % K4_NG; a2, a3 = K4_Q[gi][2]
      W = kw(cv, a0, a1, a2, a3); V = k4_second(W)
      A1, E1, Wx = traj(cv, W, 18); A2, E2, Vx = traj(cv, V, 18)
      assert W[1] == u and W[9] == ((T124_C9 - a1) & M)
      assert (fstep(a0, c) == fstep(u, c)) == (Wx[16] == G16)
      assert A1[16:20] == BA[16:20] and E1[16:20] == BE[16:20]
      assert A2[16:20] == CA[16:20] and E2[16:20] == CE[16:20]
      assert ((Vx[16] - Wx[16]) & M) == D9 and ((Vx[17] - Wx[17]) & M) == D10
      if i <= 3: obs = {"group": gi, "w1_ok": 1, "w9_ok": 1, "transplant_ok": 1}
    row = {"trial": i, "message_a_hex": None, "message_b_hex": None}
    if obs: row["observations"] = obs
    rows.append(row)
  return rows

def _stamp(A, SL):
  c_orig = A.cap; e_orig = A.k4_eval; r = [0]
  def cp(R, k=""):
    x = c_orig(R, k)
    if A.m.o + R > r[0]: r[0] = A.m.o + R
    return x
  def ev(a0, a1, u): x = e_orig(a0, a1, u); SL.append((a0, u, r[0])); return x
  A.cap = cp; A.k4_eval = ev

def _run_window_small(req):
  rows = []
  for t in req["trials"]:
    i = t["trial"]; sd = int(t["seed"][:16], 16); obs = None
    if i <= 3:
      win = (1 << 20) if i == 0 else (1 << 19)
      A = Attack(win=win, seed=sd, check=True, k4=True, screen=0, wmax=1 << 60); SL = []
      if i == 1: _stamp(A, SL)
      A.run_window(); st = A.st
      obs = {
        "distinct_claws": st["claws_distinct"], "passed_f9": st["f9"],
        "k4_lanes": st.get("k4q", 0), "k4_surv": st.get("k4s", 0), "k4_w17": st.get("k4_w17", 0),
        "k4_ops": A.m.cat.get("k4", 0), "ops": A.m.o, "k4_setup": K4_SETUP, "k4_mem": K4_MEM,
      }
      if i == 0:
        O = Attack(win=win, seed=sd, check=True, k4=False, screen=0, wmax=1 << 60); O.run_window()
        assert (O.st["claws_distinct"], O.st["f9"], O.m.o) == (st["claws_distinct"], st["f9"], A.m.o - A.m.cat.get("k4", 0))
        Z = Attack(win=1 << 16, seed=sd, check=True, k4=True, screen=1, wmax=1 << 60); Z.run_window()
        Lscr = Z.__dict__.get("scr", [])
        assert not Z.skip and k4_scr(Z.cv) <= 5 and Lscr and all(c == 69 + 3 * (S > 5) for S, c in Lscr) and Z.st.get("ddraws", 0) == sum(S > 5 for S, _ in Lscr)
        pl = _planted_check_all48(A.cv, sd); assert pl == 48
        obs["off_inv_ok"] = 1; obs["screen_ok"] = 1; obs["planted_48"] = pl
      if i == 1:
        stamps = sorted(x[2] for x in SL)
        W = stamps[len(stamps) // 2] if stamps else max(A.ws_ops + 20000, (A.ws_ops + A.m.o) // 2)
        C = Attack(win=win, seed=sd, check=False, k4=True, screen=0, wmax=W); CL = []; ck_orig = C.k4_eval
        def ck4(a0, a1, u, orig=ck_orig, out=CL): r = orig(a0, a1, u); out.append((a0, u)); return r
        C.k4_eval = ck4; C.run_window()
        assert C.m.o <= W and CL == [(a, u) for a, u, stp in SL if stp <= W]
        obs["stamp_claws"] = len(SL); obs["stamp_kept"] = len(CL); obs["stamp_ok"] = 1
    row = {"trial": i, "message_a_hex": None, "message_b_hex": None}
    if obs: row["observations"] = obs
    rows.append(row)
  return rows

def _draw_group(rng):
  u_g = rng.randrange(sum(G48_W)); gi = 0
  while u_g >= G48_W[gi]: u_g -= G48_W[gi]; gi += 1
  return gi

def _run_mate(req):
  eid = req["experiment_id"]; p8 = _members(MASK8, D8, T8); p9 = _members(MASK9, D9, T9)
  LF, NB = 2048, 40; sw = Sw(LF); n8, n9 = sw.bc(~MASK8), sw.bc(~MASK9)
  pk = lambda v: int.from_bytes(struct.pack("<%dQ" % LF, *v), "little")
  seed0 = req["trials"][0]["seed"]
  # Single SMC carrier shared identically by Tuple-124 and PUB (same xa, xe, ya, ye, xw[16:24], yw[16:24], l2)
  P_k, l2_k = _smc(random.Random(f"{eid}|smc|{seed0}"), T124_W)
  assert P_k is not None
  grng = random.Random(f"{eid}|grp|{seed0}")
  gi = _draw_group(grng); cs, samp = _build_group_dp(gi)
  gi2 = _draw_group(grng); _, samp2 = (cs, samp) if gi2 == gi else _build_group_dp(gi2)

  rk = random.Random(f"{eid}|k|{seed0}"); hk = cls01_k = mates = mates_f8 = t19 = 0
  h_dig = hashlib.sha256(); hits_cv = []
  for b in range(NB):
    s2 = _cp(P_k[b]); a2, a3 = samp(rk); v = kw([0] * 8, 0, 0, a2, a3)
    s2.xw[10], s2.xw[11] = v[10], v[11]; s2.yw[10], s2.yw[11] = (v[10] + D10) & M, (v[11] + D11) & M
    x8 = pk(rk.choices(p8, k=LF)) | (sw.rnd(rk) & n8); x9 = pk(rk.choices(p9, k=LF)) | (sw.rnd(rk) & n9)
    for l in _finals(s2, sw, x8, x9):
      ok, cl, cv, mw, A4 = _verify_smc_hit(s2, sw.get(x8, l), sw.get(x9, l))
      assert ok and A4[2] == a2 and A4[3] == a3 and kw(cv, *A4) == mw and _fd_tail(cv, mw) == 39
      hk += 1; cls01_k += int(cl == 1); h_dig.update(struct.pack("<8I16I", *(cv + mw))); hits_cv.append(cv)
      for b3 in cs:
        if b3 != a3 and h4ok(a2, b3):
          mates += 1; um = kw(cv, A4[0], A4[1], a2, b3)
          if inF(um[8], D8, T8):
            mates_f8 += 1; d = _fd_tail(cv, um); assert d >= 18
            if d > 19:
              dd = (b3 - a3) & M; assert ((s0((mw[3] + dd) & M) - s0(mw[3]) - dd) & M) != 0; t19 += 1
  xa18 = xu18 = xa20 = xu20 = xc_n = 0
  for hi, cv in enumerate(hits_cv):
    for arm in (0, 1):
      r = random.Random(f"{eid}|xc|{seed0}|{hi}|{arm}")
      u_cv = [r.getrandbits(32) for _ in range(8)] if arm else cv
      for _ in range(32):
        b2, b3 = samp2(r)
        W9 = r.choice(p9) | (r.getrandbits(32) & ~MASK9); a1 = (kw(cv, 0, 0, b2, b3)[9] - W9) & M
        W8 = r.choice(p8) | (r.getrandbits(32) & ~MASK8); k8 = kw(cv, 0, a1, b2, b3)[8]
        w = kw(u_cv, (k8 - ((W8 & ~1) | (k8 & 1))) & M, a1, b2, b3)
        d = _xd(w)
        if arm == 0: xa18 += int(d > 0); xa20 += int(d > 1)
        else: xu18 += int(d > 0); xu20 += int(d > 1)
    xc_n += 32
  obs0 = {
    "group": gi, "xc_group": gi2, "hits": hk, "cls01": cls01_k, "mates": mates, "mates_f8": mates_f8,
    "through19": t19, "xc_n": xc_n, "xa18": xa18, "xu18": xu18, "xa20": xa20, "xu20": xu20,
    "l2": round(l2_k, 6), "digest48": int.from_bytes(h_dig.digest()[:6], "big"),
  }
  if hk > 0: obs0["log2_tail"] = round(l2_k + math.log2(hk / (NB * LF)), 6)

  rp = random.Random(f"{eid}|p|{seed0}"); hp = cls01_p = 0; p_dig = hashlib.sha256()
  for b in range(NB):
    s = _cp(P_k[b]); s.xw[12:16] = _mpx[12:16]; s.yw[12:16] = M_PUB[12:16]
    x8 = pk(rp.choices(p8, k=LF)) | (sw.rnd(rp) & n8); x9 = pk(rp.choices(p9, k=LF)) | (sw.rnd(rp) & n9)
    for l in _finals(s, sw, x8, x9):
      ok, cl, cv, mw, _ = _verify_smc_hit(s, sw.get(x8, l), sw.get(x9, l)); assert ok
      hp += 1; cls01_p += int(cl == 1); p_dig.update(struct.pack("<8I16I", *(cv + mw)))
  obs1 = {"hits": hp, "cls01": cls01_p, "l2": round(l2_k, 6), "digest48": int.from_bytes(p_dig.digest()[:6], "big")}
  if hp > 0: obs1["log2_tail"] = round(l2_k + math.log2(hp / (NB * LF)), 6)

  rows = []
  for t in req["trials"]:
    idx = t["trial"]; row = {"trial": idx, "message_a_hex": None, "message_b_hex": None}
    if idx == 0: row["observations"] = obs0
    elif idx == 1: row["observations"] = obs1
    rows.append(row)
  return rows

def main():
  req = json.load(sys.stdin); eid = req["experiment_id"]
  if eid == "r39-transplant-claw": rows = _run_transplant(req)
  elif eid == "r39k4-window-small": rows = _run_window_small(req)
  elif eid.startswith("r39-mate-"): rows = _run_mate(req)
  else: raise SystemExit(f"unknown experiment id: {eid}")
  sys.stdout.write(json.dumps({"schema_version": 1, "trials": rows}, sort_keys=True, separators=(",", ":")))

if __name__ == "__main__": main()
