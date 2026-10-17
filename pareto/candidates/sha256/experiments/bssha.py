"""Birthday collision search on 50-step SHA-256 (sha256-r50, one block): 256 bit-sliced lanes, a ROLLED program, distinguished points.
M(x) = PREFIX || x (20-byte prefix, 32-byte big-endian x, 52 bytes): W0..W4 = prefix, W5..W12 = x, W13 = 0x80000000, W14 = 0, W15 = 0x1A0.  f(x) = the working state
after 50 steps (standard IV) as a 256-bit integer, i.e. the digest minus the IV word by word (no feed-forward; dariolina's 744875ec); the walk is g(x) = f(x)
(the state planes are fed back as stored, polarity upright); g(x) = g(y) iff the digests are equal.
Credit: pivot full adder and mask walk after jungjipdo's 6ae36351, register-file convention after 67f781f8, walk on the digest minus the IV and the zero-state
prefix after dariolina's 744875ec; search, handlers, recovery, ledger and Lemma 2 ours.
"""
import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, log, log2, log1p, exp, comb

M32 = 0xFFFFFFFF
ROUNDS = 50
UNIT = 3736
LANES, ALL = 256, (1 << 256) - 1
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
K = (0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
     0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
     0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
     0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
     0x19a4c116, 0x1e376c08)
PREFIX = bytes.fromhex("0000000000000000000000000000000000000000")
PREFIX_WORDS = tuple(int.from_bytes(PREFIX[4 * i:4 * i + 4], "big") for i in range(5))      # message words W0..W4
TAIL = (0x80000000, 0, 0x1A0)

# ---- 1 scalar digest
def _ror(v, k):
  return ((v >> k) | (v << (32 - k))) & M32

def state_words(w, prefix=PREFIX_WORDS):
  """The working state a..h after ROUNDS steps (no feed-forward)."""
  ws = list(prefix) + list(w) + list(TAIL)
  for i in range(16, ROUNDS):
    x, y = ws[i - 15], ws[i - 2]
    ws.append((ws[i - 16] + (_ror(x, 7) ^ _ror(x, 18) ^ (x >> 3)) + ws[i - 7] + (_ror(y, 17) ^ _ror(y, 19) ^ (y >> 10))) & M32)
  a, b, c, d, e, f, g, h = IV
  for i in range(ROUNDS):
    t1 = (h + (_ror(e, 6) ^ _ror(e, 11) ^ _ror(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + ws[i]) & M32
    t2 = ((_ror(a, 2) ^ _ror(a, 13) ^ _ror(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) & M32
    a, b, c, d, e, f, g, h = (t1 + t2) & M32, a, b, c, (d + t1) & M32, e, f, g
  return [a, b, c, d, e, f, g, h]

def digest_words(w, prefix=PREFIX_WORDS):
  return [(u + v) & M32 for u, v in zip(IV, state_words(w, prefix))]

def words_of(x):
  return [(x >> (32 * (7 - i))) & M32 for i in range(8)]

def int_of(w):
  return sum(w[i] << (32 * (7 - i)) for i in range(8))

def f_scalar(x, n=256):
  return int_of(state_words(words_of(x))) & ((1 << n) - 1)

IVINT = int_of(IV)
H31 = sum(0x80000000 << (32 * i) for i in range(8))

def add_iv(v):
  """The digest of a state (the IV added to each of the eight words, modulo 2^32)."""
  return ((v & (ALL ^ H31)) + (IVINT & (ALL ^ H31))) ^ ((v ^ IVINT) & H31)

def message(x):
  return PREFIX + x.to_bytes(32, "big")

# ---- 2 the recovery program (two trails in one 256-bit word, rolled)
# Records (op, x, y, z), 36 bytes: ^ & | + r[x] = r[y] op r[z]; > < shift by z; S set from IMM[y]; L load; T store; R A C J pointer set, add, compare, branch.
# Lane l (0, 1) holds each 32-bit word in bits 128 l .. 128 l + 31, so a rotation is a doubled word and right shifts.
RP, RMASK = 128, M32 | (M32 << 128)
WM, KM = 0, ROUNDS

def _rep(v):
  return v | (v << RP)

def _state5():
  """Working state after step 4 (W0..W4 are the constant prefix, so it is a constant) and b XOR c of it (the 'previous a XOR b' of step 5)."""
  a, b, c, d, e, f, g, h = IV
  for i in range(5):
    t1 = (h + (_ror(e, 6) ^ _ror(e, 11) ^ _ror(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + PREFIX_WORDS[i]) & M32
    t2 = ((_ror(a, 2) ^ _ror(a, 13) ^ _ror(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) & M32
    a, b, c, d, e, f, g, h = (t1 + t2) & M32, a, b, c, (d + t1) & M32, e, f, g
  return [a, b, c, d, e, f, g, h], b ^ c

class RecProg:
  """init: records executed once per recovery.  Per call: store the 8 input words, set the state after step 4, the schedule loop, the leading steps, the round loop."""

  def __init__(self):
    n = ROUNDS
    self.imm, self.init = [], []
    MASK, T0, T1, T2, T3, T4 = 0, 11, 12, 13, 14, 15
    ST, PB = list(range(1, 9)), [9, 10]

    def S(out, x, v):
      self.imm.append(v)
      out.append(("S", x, len(self.imm) - 1, 0))
    self.init.append(("R", 2, 0, 0))
    S(self.init, MASK, RMASK)
    for i in range(n):
      S(self.init, T0, _rep(K[i]))
      self.init.append(("T", KM + i, T0, 2))
    for i in list(range(5)) + [13, 14, 15]:
      S(self.init, T0, _rep((PREFIX_WORDS + (0,) * 8 + TAIL)[i]))
      self.init.append(("T", WM + i, T0, 2))

    def sigma(out, dst, src, rs, shr):
      """dst = (rotations of src by rs, or two rotations and src >> shr) & MASK; T0, T1 scratch."""
      out += [("<", T0, src, 32), ("|", T0, src, T0), (">", dst, T0, rs[0]), (">", T1, T0, rs[1]), ("^", dst, dst, T1)]
      out += [(">", T1, src, shr) if shr else (">", T1, T0, rs[2]), ("^", dst, dst, T1), ("&", dst, dst, MASK)]

    def rnd(out, st, pi, addrw, ptr):
      a, b, c, d, e, f, g, h = st
      P, PN = PB[pi], PB[1 - pi]
      sigma(out, T2, e, (6, 11, 25), 0)
      out += [("^", T3, f, g), ("&", T3, e, T3), ("^", T3, g, T3)]                  # Ch
      out += [("L", T4, addrw, ptr), ("L", T0, addrw + KM, ptr), ("+", T4, T4, T0)]   # W' = W + K
      out += [("+", T2, h, T2), ("+", T2, T2, T3), ("+", T2, T2, T4)]
      sigma(out, T3, a, (2, 13, 22), 0)
      out += [("^", PN, a, b), ("&", T0, PN, P), ("^", T0, T0, b), ("+", T3, T3, T0)]
      out += [("+", h, d, T2), ("&", h, h, MASK), ("+", d, T2, T3), ("&", d, d, MASK)]
      return [d, a, b, c, h, e, f, g], 1 - pi
    assert WM == 0
    pre = (n - 5) % 4
    st, pi = list(ST), 0
    straight = []
    for j in range(pre):
      st, pi = rnd(straight, st, pi, WM + 5 + j, 2)
    body, stl, pil = [], list(st), pi
    for j in range(4):
      stl, pil = rnd(body, stl, pil, j, 0)
    assert stl == st and pil == pi, "the round loop does not rename back"
    self.fin = list(st)
    head = [("T", WM + 5 + k, self.fin[k], 2) for k in range(8)]
    state, pab = _state5()
    for k in range(8):
      S(head, ST[k], _rep(state[k]))
    S(head, PB[0], _rep(pab))
    A_, B_, C_, D_, E0, E1 = 19, 20, 21, 22, 23, 24
    sched = [("L", A_, 0, 0), ("L", B_, 1, 0), ("L", C_, 9, 0), ("L", D_, 14, 0)]
    sigma(sched, E0, B_, (7, 18, 0), 3)
    sigma(sched, E1, D_, (17, 19, 0), 10)
    sched += [("+", A_, A_, E0), ("+", A_, A_, C_), ("+", A_, A_, E1), ("&", A_, A_, MASK), ("T", 16, A_, 0)]
    self.blocks = [("S", head), ("L", sched, 0, n - 16, 1), ("S", straight), ("L", body, 5 + pre, n - 5 - pre, 4)]
    self.flat = []
    for blk in self.blocks:
      if blk[0] == "S":
        self.flat += blk[1]
      else:
        _, bd, start, count, stepw = blk
        self.flat += [("R", 0, start, 0), ("R", 1, start + count, 0)]
        top = len(self.flat)
        self.flat += bd + [("A", 0, stepw, 0), ("C", 0, 1, 0), ("J", top, 0, 0)]
    self.instr = len(self.init) + len(self.flat)
    self.mem = [0] * (2 * n)
    self.regs = [0] * 32
    self.run(self.init)
    self.mem0, self.regs0 = list(self.mem), list(self.regs)
    self.ops = self.run(self.flat)
    self._compile()

  def run(self, recs):
    r, mem, p, flag, pc, cnt = self.regs, self.mem, [0, 0, 0], False, 0, 0
    while pc < len(recs):
      op, x, y, z = recs[pc]
      pc += 1
      cnt += 1
      if op == "^": r[x] = r[y] ^ r[z]
      elif op == "&": r[x] = r[y] & r[z]
      elif op == "|": r[x] = r[y] | r[z]
      elif op == "+": r[x] = (r[y] + r[z]) & ALL
      elif op == ">": r[x] = r[y] >> z
      elif op == "<": r[x] = (r[y] << z) & ALL
      elif op == "S": r[x] = self.imm[y]
      elif op == "L": r[x] = mem[p[z] + y]
      elif op == "T": mem[p[z] + x] = r[y]
      elif op == "R": p[x] = y
      elif op == "A": p[x] += y
      elif op == "C": flag = p[x] < p[y]
      elif op == "J" and flag: pc = x
    return cnt

  def _compile(self):
    def line(rc, pad, loop):
      op, x, y, z = rc
      if op in "^&|": return "%sr[%d] = r[%d] %s r[%d]" % (pad, x, y, op, z)
      if op == "+": return "%sr[%d] = r[%d] + r[%d]" % (pad, x, y, z)
      if op == ">": return "%sr[%d] = r[%d] >> %d" % (pad, x, y, z)
      if op == "<": return "%sr[%d] = (r[%d] << %d) & ALL" % (pad, x, y, z)
      if op == "S": return "%sr[%d] = IM[%d]" % (pad, x, y)
      if op == "L": return "%sr[%d] = m[%s + %d]" % (pad, x, "q" if loop and z == 0 else "0", y)
      return "%sm[%s + %d] = r[%d]" % (pad, "q" if loop and z == 0 else "0", x, y)
    src = ["def step(r, m):"]
    for blk in self.blocks:
      if blk[0] == "S":
        src += [line(rc, "    ", False) for rc in blk[1]]
      else:
        src.append("    for q in range(%d, %d, %d):" % (blk[2], blk[2] + blk[3], blk[4]))
        src += [line(rc, "        ", True) for rc in blk[1]]
    ns = {"ALL": ALL, "IM": self.imm}
    exec(compile("\n".join(src) + "\n", "<recovery>", "exec"), ns)
    self.fast = ns["step"]

  def f(self, xs, fast=True):
    """The working state words after ROUNDS steps (the digest minus the IV, word by word) of up to two chain values, as 256-bit integers."""
    r, m = list(self.regs0), list(self.mem0)
    for k in range(8):
      r[self.fin[k]] = sum(((x >> (32 * (7 - k))) & M32) << (RP * l) for l, x in enumerate(xs))
    if fast:
      self.fast(r, m)
    else:
      self.regs[:], self.mem[:] = r, m
      self.run(self.flat)
      r = self.regs
    return [sum(((r[self.fin[k]] >> (RP * l)) & M32) << (32 * (7 - k)) for k in range(8)) for l in range(len(xs))]

_REC = []

def rec():
  if not _REC:
    _REC.append(RecProg())
  return _REC[0]

def packed_f(xs, n, qw=None):
  return [v & ((1 << n) - 1) for v in rec().f(xs)]

def packed_ops(qw=None):
  """Records executed by one call of the recovery program."""
  return rec().ops

# ---- 3 bit-sliced generator
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
    p, q = (x, y) if x[1] == 0 else (y, x)
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

# ---- 4 the program: one straight network, register allocation, 5-byte body records
# Program = ONE straight segment (no loop): the message schedule W16..W49 and the steps 0..49 unrolled, K and the constant message words folded into the gates, no loads, no stores, no
# feed-forward.  Records (op, d, a, b): ^ & | xor/and/or; N not; M move; S set (0 or all ones).  Every record is a register-to-register operation of the main-loop body: an opcode and three
# 10-bit register fields, BODY_BYTES = 5 bytes, no immediate (a cost-model price, proof 3.1).  Data registers 0..1020 of 256 bits (three pointer registers after them: 1,024 in all).
def _add_u(g, A, u, B_fix):
  """A + B from u = A ^ B and B[0] = B_fix() (carry out of bit i = A[i] ^ (u[i] & (A[i] ^ c))); B[0] is built only when A[0] is not the constant 0."""
  s, c = [], ZERO
  for i in range(32):
    if i == 0:
      s.append(u[0]); c = g.AND(A[0], B_fix()) if A[0] != ZERO else g.AND(A[0], ZERO)
    elif i == 31:
      s.append(g.XOR(u[31], c))
    else:
      s.append(g.XOR(u[i], c))
      c = g.XOR(g.AND(u[i], g.XOR(A[i], c)), A[i])
  return s

def _rnd2(g, st, Wd):
  """One step; hg = h ^ g = f ^ g of the previous step, so h ^ Ch = hg ^ (e & (f ^ g)) and Ch is not built.  Wd = K + W (a word)."""
  a, b, c, d, e, f, gg, h, prev, hg = st
  S1 = _sigma(g, e, 6, 11, 25, False)
  fg = [g.XOR(f[j], gg[j]) for j in range(32)]
  tt = [g.AND(e[j], fg[j]) for j in range(32)]
  u = [g.XOR(hg[j], tt[j]) for j in range(32)]
  t1 = _add_u(g, h, u, lambda: g.XOR(gg[0], tt[0]))
  t1 = g.add(g.add(t1, S1), Wd)
  S0 = _sigma(g, a, 2, 13, 22, False)
  ab, mj = [], []
  for j in range(32):
    ab.append(g.XOR(a[j], b[j]))
    mj.append(g.XOR(g.AND(ab[j], prev[j]), b[j]))
  t2 = g.add(S0, mj)
  ne = g.add(d, t1)
  na = g.add(t1, t2)
  return (na, a, b, c, ne, e, f, gg, ab, fg)

def _net_u():
  """All 50 steps: W[i] (i >= 16) is built right before step i, Wd = K[i] + W[i]; the state after step 49 is the output."""
  g = Gen(256)
  W = [_constw(w) for w in PREFIX_WORDS] + [[g.inputs[32 * (7 - i) + j] for j in range(32)] for i in range(8)] + [_constw(w) for w in TAIL]
  v = [_constw(w) for w in IV]
  st = tuple(v) + ([g.XOR(v[1][j], v[2][j]) for j in range(32)], [g.XOR(v[7][j], v[6][j]) for j in range(32)])
  for i in range(ROUNDS):
    if i >= 16:
      t = g.add(W[i - 16], _sigma(g, W[i - 15], 7, 18, 3, True))
      t = g.add(t, W[i - 7])
      W.append(g.add(t, _sigma(g, W[i - 2], 17, 19, 10, True)))
    st = _rnd2(g, st, g.add(_constw(K[i]), W[i]))
  return g, [t for w in st[:8] for t in w]

def _alloc(g, nin, fixed, outs, tgt, free0, E):
  """Streaming allocator (the C generator does the same in two passes): a result takes the register of an operand that dies at the gate (not a pending target), else the lowest
    free one that is not a pending target; an output node takes its target register when it can."""
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
  st = dict(free=sum(1 << r for r in free0 if r not in fixed.values()), pend=sum(1 << tgt[i] for i, o in enumerate(outs) if o[0]), moves=0)

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

  for v, r in fixed.items():
    if uses[v] == 0:
      release(r)
  for k in range(nin + 1, len(nodes)):
    op, x, y = nodes[k]
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
    if uses[k] == 0:
      raise AssertionError("dead gate")
  todo = [(i, reg[o[0]]) for i, o in enumerate(outs) if o[0] and reg[o[0]] != tgt[i]]
  while todo:
    srcs = [s for _, s in todo]
    k = next((k for k, (i, s) in enumerate(todo) if tgt[i] not in srcs), None)
    if k is None:
      s = todo[0][1]
      tmp = take()
      E(("M", tmp, s, 0))
      st["moves"] += 1
      todo = [(j, tmp if u == s else u) for j, u in todo]
      continue
    i, s = todo.pop(k)
    if outs[i][1]:
      E(("N", tgt[i], s, 0))
    else:
      E(("M", tgt[i], s, 0))
      st["moves"] += 1
  for i, o in enumerate(outs):
    if o[0] and reg[o[0]] == tgt[i] and o[1]:
      E(("N", tgt[i], tgt[i], 0))
  for i, o in enumerate(outs):
    if o[0] == 0:
      E(("S", tgt[i], 1 if o[1] else 0, 0))
  return st["moves"]

def INREG(j):
  """Register of plane j: bit j % 32 of state word 7 - j // 32 (a = 0 .. h = 7), kept in registers 256 + 32 k + bit."""
  return 256 + 32 * (7 - j // 32) + j % 32

def assemble():
  """(records, moves, generator calls)"""
  R = []
  g, outs = _net_u()
  moves = _alloc(g, 256, {j + 1: INREG(j) for j in range(256)}, outs, [256 + i for i in range(256)], range(REGISTERS), R.append)
  return R, moves, 2 * g.calls

class Prog:
  """The program with its interpreter.  kernel = records executed per batch."""

  def __init__(self):
    self.recs, self.moves, self.calls = assemble()
    self.q = [0] * 256
    self.qint = 0
    self.qwords = [(self.qint >> (32 * i)) & M32 for i in range(8)]
    self.pin = [0] * 256
    self.instr = self.kernel = len(self.recs)
    self.nregs = max(max(r[1:3]) if r[0] in "NM" else max(r[1:4]) if r[0] in "^&|" else r[1] for r in self.recs) + 1
    self.compile()

  def run(self, pc, end, regs):
    """Execute records pc..end-1; returns the number of records executed."""
    recs, n = self.recs, 0
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
      elif op == "N":
        regs[d] = regs[a] ^ ALL
      elif op == "M":
        regs[d] = regs[a]
      elif op == "S":
        regs[d] = ALL if a else 0
    return n

  def compile(self):
    f = {"^": "r[%d] = r[%d] ^ r[%d]", "&": "r[%d] = r[%d] & r[%d]", "|": "r[%d] = r[%d] | r[%d]", "N": "r[%d] = r[%d] ^ ALL", "M": "r[%d] = r[%d]", "S": "r[%d] = ALL if %d else 0"}
    ns, fs = {"ALL": ALL}, []
    for a in range(0, len(self.recs), 4096):
      exec(compile("def c(r):" + chr(10) + "".join("    " + (f[o] % ((d, x, y) if o in "^&|" else (d, x))) + chr(10) for o, d, x, y in self.recs[a:a + 4096]), "<program>", "exec"), ns)
      fs.append(ns["c"])

    def step(r):
      for c in fs:
        c(r)
    self.fast = step

  def step(self, *planes):
    """One batch: the low n of the 256 input planes in (the rest 0), the n output planes (g = f XOR q) out."""
    regs = [0] * REGISTERS
    for j, pl in enumerate(planes):
      regs[INREG(j)] = pl
    self.fast(regs)
    return [regs[INREG(j)] for j in range(len(planes))]

# ---- lane transposition, packing, extraction
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

# ---- 5 plan, ledger and success bound (Lemma 2 of the proof, Section 4)
LAMBDA = Fraction(497, 1000)
CUTLOSS = Fraction(15, 100000)
TAIL_AGES = 1e-6
CMAX = 2
EPS = 1e-3
P_MIN = 0.390000001
HZ = 257 / 2
GRAIN = 10 ** 24
STAGE1_PLANES = 32
LOOP_OPS = 3
HIT_OPS = 2800
EVENT_OPS = 3800
CUT_OPS = 4200
SLICE_OPS = 1300                   # slice check: 256 ages
RECOVER_EXTRA = 64
INSTR_BYTES = 36
BODY_BYTES = 5
GEN_CODE = 2800
HANDLER_CODE, SETUP_CODE, RECOVERY_CODE = 1000, 160, 47
REGISTERS = 1021
REGFILE = REGISTERS * 32
COUNTERS = 16384
ARRAYS = 64 * ROUNDS
KEYB = 40
ENTRY = 22
MEM_LIMIT = 1 << 20
ADVICE = 0
KAPPA_256 = 16
GEN_FACTOR = 200
GEN_SCRATCH = 87347
SETUP_FIXED = 256 * 3100 + 20000
CFG = {18: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4),
       256: dict(s1=32, W=90, kappa=KAPPA_256, Sb=1 << 48)}

def stage1_ops(pin, s1):
  """Operations of the stage-1 test (lanes whose s1 low stored planes are zero), plus compare and branch."""
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
  else:
    ureq = isqrt(2 * N * LAMBDA.numerator // LAMBDA.denominator) + 2
    num, den = ureq + INFLIGHT * L + 1, CUTLOSS.denominator
    q = -(-(num * den) // (den - CUTLOSS.numerator))
    B = -(-q // LANES)
  cc = -(-kappa * L.numerator // L.denominator)
  fb = (Tp - 1).bit_length()
  return dict(n=n, s1=s1, W=W, D=D, Tp=Tp, fb=fb, kb=min(KEYB - fb, n - D), L=L, N=N, Q=B * LANES, B=B, kappa=kappa, Sb=Sb,
                c=cc, capr=cc + Sb, tmax=tmax, e2max=2 * B * LANES // (1 << s1) + 64,
                cmax=CMAX if n == 256 else 10 ** 9)

def tail_log2(mean, k):
  """log2 of the Chernoff bound exp(-mean) (e mean / k)^k on P(count >= k), k > mean."""
  return (-mean + k * (1 + log(mean / k))) / log(2)

_PROG = []

def prog():
  global REGFILE
  if not _PROG:
    _PROG.append(Prog())
    REGFILE = 32 * (_PROG[0].nregs + 3)
  return _PROG[0]

def other_code(pr=None):
  return HANDLER_CODE + rec().instr + RECOVERY_CODE + SETUP_CODE

def machine_constants(pr=None):
  """(kernel ops per batch, stage-1 ops, body ops per batch, code bytes, tmax): body = kernel + stage 1 + loop; code = the body records once at 5 bytes, every other instruction once at 36 bytes."""
  pr = pr or prog()
  filt = stage1_ops(pr.pin, STAGE1_PLANES)
  code = pr.instr * BODY_BYTES + (filt + LOOP_OPS + other_code(pr)) * INSTR_BYTES
  return pr.kernel, filt, pr.kernel + filt + LOOP_OPS, code, (MEM_LIMIT - code - REGFILE - COUNTERS - ADVICE - ARRAYS) // ENTRY

def phase_bytes(code, tmax):
  """(setup phase, search phase) resident bytes.  Setup: code, counters, generator image (GEN_CODE instructions of 36 bytes) and scratch.  Search: code, counters, register file, W' array, table."""
  prog()
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
  lo, hi = 1.0, float(tmax + 1)
  for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= -40 else (lo, mid)
  a, z = 1, 4097
  while z - a > 1:
    m = (a + z) // 2
    a, z = (m, z) if _lossq(m, lo, tmax, kappa, CFG[256]["Sb"])["P_lower"] >= P_MIN else (a, m)
  return _plan(256, a, kappa, tmax, CFG[256]["Sb"])

def ledger(p=None, pr=None):
  """Operation budget in word operations (exact integers); units are operations / 3736 (C of sha256-r50)."""
  p = p or plan(256)
  pr = pr or prog()
  ph, filt, body, code, _ = machine_constants(pr)
  gen = GEN_FACTOR * (pr.calls + pr.instr)
  parts = dict(main=body * p["B"],
                 slices=-(-p["B"] // p["Sb"]) * SLICE_OPS,
                 stage1_hits=p["e2max"] * HIT_OPS,
                 events=p["tmax"] * (EVENT_OPS + 3 * p["tmax"]),
                 cuts=p["cmax"] * CUT_OPS,
                 recovery=p["capr"] * (packed_ops() + RECOVER_EXTRA) + 600 + len(rec().init),
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
  while tail_log2(q, k) > log(EPS, 2) - 1e-6:
    k += 1
  nmax = k - 1 + LANES                                  # lottery blocks
  z = _zq(q, uc, uh, nmax)
  l2n = float(L * L / (1 << 256)) * rate                # L^2 / N, scaled
  kap = (2 * q * uc + HZ * uc * uc + 2 * q * (uc - uh)) * l2n
  w = 1.0
  for _ in range(100):
    w = exp(w * kap)                                  # ln w = w kap
  w *= 1 + 2.0 ** -40
  s0 = q * q / 2
  th = l2n * (w * (s0 - z - CMAX * (q * uc + min(q * (uc - uh), z / (LANES + 1) + q * float(Sb / L)))) - (w - 1) * s0)
  p, hq, ql, n2 = exp(-kappa), s0 * l2n, q * l2n, k + LANES + CMAX
  cuts = 1 - sum(comb(n2, j) * p ** j * exp((n2 - j) * log1p(-p)) for j in range(CMAX + 1))
  cuts += ql * (1 + (2 + kappa) * exp(-kappa / 2) + 2 * hq) + hq * p * (3 + 2 * kappa)
  t = dict(main=exp(-th), finished_count=EPS, trail_sums=EPS, cut_halt=cuts,
             collision_on_path=uc * q * l2n, key_false_match=tmax * (tmax - 1) / 2 * 2.0 ** -(min(KEYB - (Tp - 1).bit_length(), 134) + log(Tp, 2)),
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

# ---- 6 search and recovery
class Halt(Exception):
  pass

# ---- 6b the chain engine
class Engine:
  """The chain function g = f XOR q of the width-n search: step(planes) runs the program on n planes, f2(xs) is the recovery circuit, g_scalar the scalar form."""

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
  assert key < 1 << KEYB and t < 1 << 16 and length < 1 << 120
  return key | (t << KEYB) | (length << (KEYB + 16))

def unpack_entry(e):
  return e & ((1 << KEYB) - 1), (e >> KEYB) & 0xFFFF, e >> (KEYB + 16)

def recover(p, r, a, b, f2):
  """a, b = (t, length) of two finished trails with the same end.  Returns (x, y), x != y, f(x) = f(y), or None."""
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
  """One attempt with the fresh random word r: the pair (x, y) or None.  Raises Halt at a budget."""
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

# ---- 7 organizer experiments
N_T3 = 18
N_T1 = 12
M_T2, B_T2 = 512, 18
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
  digs = [add_iv(d) for d in digs]
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

# ---- 8 self test and command line
def text():
  return "".join("%s %d %d %d\n" % r for r in prog().recs)

def selftest():
  import random
  rnd = random.Random(3)
  pr = prog()
  reg = max(max(r[1:4]) for r in pr.recs if r[0] in "^&|") + 1
  print("records", pr.instr, "moves", pr.moves, "kernel", pr.kernel, "registers used", reg, "text sha256", hashlib.sha256(text().encode()).hexdigest())
  ok = reg <= REGISTERS and pr.nregs <= REGISTERS and all(r[0] in "^&|NM" for r in pr.recs)
  t = True
  for xs in [[rnd.getrandbits(256) for _ in range(LANES)] for _ in range(8)] + [[0] * LANES, [(1 << 256) - 1] * LANES]:
    out = lanes_of(list(pr.step(*pack_lanes(xs, 256, pr.pin))), 256, pr.pin)
    t &= all(out[l] == f_scalar(xs[l]) ^ pr.qint for l in range(LANES))
  print("2,560 lanes (10 batches), full 256-bit g = f XOR q, program vs scalar 50-step compression:", t)
  ok &= t
  regs = [0] * REGISTERS
  for j in range(256):
    regs[INREG(j)] = rnd.getrandbits(256)
  ref = list(regs)
  n = pr.run(0, len(pr.recs), regs)
  fast = list(ref)
  pr.fast(fast)
  t = n == pr.kernel and [fast[INREG(j)] for j in range(256)] == [regs[INREG(j)] for j in range(256)]
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
  xs = [rnd.getrandbits(256) for _ in range(2)]
  ref2 = [f_scalar(x) for x in xs]
  t = packed_f(xs, 256) == ref2 and rec().f(xs, False) == ref2 and packed_f(xs[:1], 256) == ref2[:1] and rec().f([0, ALL]) == [f_scalar(0), f_scalar(ALL)]
  print("recovery program (%d records executed per call, %d records, interpreter and compiled form) vs scalar:" % (packed_ops(), rec().instr), t)
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

# ---- 9 the circuit generator in C
# The generator of sections 3 and 4 in freestanding C (WebAssembly, 16 pages = 1,048,576 bytes of guest memory); it emits the records of `--text` exactly (proof 3.6).
GEN_C = r'''/* Freestanding C generator of the straight 256-lane 50-step SHA-256 program (bssha.py: Gen, the network, the allocator, the 5-byte records).  No libc, no malloc.  The network is built
   twice: pass 0 counts the uses of every node and records the outputs; pass 1 emits.  A gate is a new node every time; a signal is neg bit 0, node bits 1-18, register from bit 19.
   A record is 5 bytes: opcode, then d | a << 10 | b << 20 (little endian, 10-bit register fields). */
typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32;
#define NMAX 73687
#define NREC 73563
#define RND 50
#define NST 256
#define IR(j) (256 + 32 * (7 - ((j) >> 5)) + ((j) & 31))
#define NODE(s) (((s) >> 1) & 0x3FFFFu)
#define REG(s) ((s) >> 19)
#define ZERO 0u
#define ONE 1u
static u8 code[NREC][5];
__attribute__((used)) static u8 counters[16384];
static u8 uses[NMAX];
static u32 fb[32], pb[32], W[16][32], Wt[32], V[10][32], ab[32], mj[32], ch[32], S0[32], S1[32], s0[32], s1[32], T1[32], T2[32], KW[32], NA[32], NE[32];
static u32 oid[NST], oix[NST], oreg[NST], onode[NST], mvi[NST], mvs[NST];
static u8 oneg[NST];
static u32 pass, nn, nin, nO, nE, co, calls, err, kk, nmov;
static struct { u32 ninst, nreg, nodes0, nodes1, nodes2, calls, err, moves, n0, n1, n2, sz_code, sz_ctr, sz_uses, sz_state; u8 q[32]; } info;
static const u32 IV[8] = {0x6A09E667u,0xBB67AE85u,0x3C6EF372u,0xA54FF53Au,0x510E527Fu,0x9B05688Cu,0x1F83D9ABu,0x5BE0CD19u};
static const u32 K[RND] = {0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,
  0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
  0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,
  0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u,0xa2bfe8a1u,0xa81a664bu,0xc24b8b70u,0xc76c51a3u,0xd192e819u,0xd6990624u,0xf40e3585u,0x106aa070u,
  0x19a4c116u,0x1e376c08u};
static const u32 PW[5] = {0x00000000u,0x00000000u,0x00000000u,0x00000000u,0x00000000u};
static void emit(u32 op, u32 d, u32 a, u32 b) {
  if (kk >= NREC) { err = 5; return; }
  u8 *r = code[kk++]; u32 w = d | (a << 10) | (b << 20);
  r[0] = (u8)op; r[1] = (u8)w; r[2] = (u8)(w >> 8); r[3] = (u8)(w >> 16); r[4] = (u8)(w >> 24);
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
static u32 tgt(u32 i) { return 256 + i; }
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
  u32 rx = REG(x), ry = REG(y);
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
  while (co < nE && oid[co] == id) oreg[oix[co++]] = dst;
  if (uses[id] == 0) { err = 9; release((u32)dst); }
  return (id << 1) | ((u32)dst << 19);
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
static u32 inp(u32 j) { return ((1 + j) << 1) | (IR(j) << 19); }
static void outp(u32 i, u32 s) { if (pass == 0) { onode[i] = NODE(s); oneg[i] = (u8)(s & 1); } }
/* A + B from u = A ^ B and B[0]: carry out of bit i = A[i] ^ (u[i] & (A[i] ^ c)). */
static void addu(const u32 *A, const u32 *u, u32 g0, u32 t0, u32 *out) {
  u32 c = ZERO;
  for (int i = 0; i < 32; i++) {
    out[i] = i ? XOR(u[i], c) : u[0];
    if (i == 0) c = A[0] != ZERO ? AND(A[0], XOR(g0, t0)) : AND(A[0], ZERO);
    else if (i < 31) c = XOR(AND(u[i], XOR(A[i], c)), A[i]);
  }
}
/* one step on V[0..7] = a..h, V[8] = previous a ^ b, V[9] = h ^ g; Wd = K + W.  h ^ Ch = V[9] ^ (e & (f ^ g)) and the V[9] of the next step is this f ^ g, so Ch is not built. */
static void rnd(const u32 *Wd) {
  sigma(S1, V[4], 6, 11, 25, 0);
  for (int j = 0; j < 32; j++) ch[j] = XOR(V[5][j], V[6][j]);
  for (int j = 0; j < 32; j++) ab[j] = AND(V[4][j], ch[j]);
  for (int j = 0; j < 32; j++) mj[j] = XOR(V[9][j], ab[j]);
  addu(V[7], mj, V[6][0], ab[0], T1);
  add(T1, S1, T1); add(T1, Wd, T1);
  sigma(S0, V[0], 2, 13, 22, 0);
  for (int j = 0; j < 32; j++) { ab[j] = XOR(V[0][j], V[1][j]); mj[j] = XOR(AND(ab[j], V[8][j]), V[1][j]); }
  add(S0, mj, T2);
  add(V[3], T1, NE); add(T1, T2, NA);
  for (int j = 0; j < 32; j++) {
    V[3][j] = V[2][j]; V[2][j] = V[1][j]; V[1][j] = V[0][j]; V[0][j] = NA[j];
    V[7][j] = V[6][j]; V[6][j] = V[5][j]; V[5][j] = V[4][j]; V[4][j] = NE[j]; V[8][j] = ab[j]; V[9][j] = ch[j];
  }
}
static void wmsg(int i, u32 *o) {                              /* message words W0..W15 of M(x) */
  if (i < 5) constw(o, PW[i]);
  else if (i < 13) for (int b = 0; b < 32; b++) o[b] = inp(32 * (12 - i) + b);
  else constw(o, i == 13 ? 0x80000000u : i == 14 ? 0u : 0x1A0u);
}
static void trace(void) {
  nn = 1 + nin;
  for (int i = 0; i < 16; i++) wmsg(i, W[i]);                  /* W is a ring of 16 words, slot i & 15 */
  for (int i = 0; i < 8; i++) constw(V[i], IV[i]);
  for (int j = 0; j < 32; j++) V[8][j] = XOR(V[1][j], V[2][j]);
  for (int j = 0; j < 32; j++) V[9][j] = XOR(V[7][j], V[6][j]);
  for (int i = 0; i < RND; i++) {
    if (i >= 16) {
      sigma(s0, W[(i - 15) & 15], 7, 18, 3, 1);
      add(W[(i - 16) & 15], s0, T1); add(T1, W[(i - 7) & 15], T1);
      sigma(s1, W[(i - 2) & 15], 17, 19, 10, 1);
      add(T1, s1, W[i & 15]);
    }
    constw(KW, K[i]); add(KW, W[i & 15], Wt);
    rnd(Wt);
  }
  for (int w = 0; w < 8; w++) for (int j = 0; j < 32; j++) outp(32 * w + j, V[w][j]);
}
static void sortent(void) {                                   /* entries by node id, stable */
  nE = 0;
  for (u32 i = 0; i < nO; i++) if (onode[i]) {
    u32 t = nE++;
    while (t && oid[t - 1] > onode[i]) { oid[t] = oid[t - 1]; oix[t] = oix[t - 1]; t--; }
    oid[t] = onode[i]; oix[t] = i;
  }
}
__attribute__((export_name("info_ptr"))) u32 info_ptr(void) { return (u32)(unsigned long)&info; }
__attribute__((export_name("code_ptr"))) u32 code_ptr(void) { return (u32)(unsigned long)code; }
__attribute__((export_name("run"))) int run(void) {
  info.sz_code = sizeof code; info.sz_ctr = sizeof counters; info.sz_uses = sizeof uses;
  info.sz_state = sizeof fb + sizeof pb + sizeof W + sizeof V + 18 * 128 + sizeof oid + sizeof oix + sizeof oreg + sizeof onode + sizeof mvi + sizeof mvs + sizeof oneg + sizeof info + 256;
  err = 0; calls = 0; kk = 0; nmov = 0; nin = 256; nO = 256; co = 0;
  for (u32 m = 0; m < NMAX; m++) uses[m] = 0;
  pass = 0; trace();
  if (nn > NMAX) { err = 1; return (int)err; }
  info.nodes0 = nn;
  sortent();
  for (u32 e = 0; e < nE; e++) uses[oid[e]]++;
  pass = 1;
  for (u32 w = 0; w < 32; w++) { fb[w] = 0; pb[w] = 0; }
  for (u32 r = 0; r < 1021; r++) if (r < 256 || r >= 512) release(r);
  for (u32 i = 0; i < nO; i++) if (onode[i]) { u32 t = tgt(i); pb[t >> 5] |= 1u << (t & 31); }
  while (co < nE && oid[co] <= nin) { oreg[oix[co]] = IR(oid[co] - 1); co++; }
  for (u32 n = 1; n <= nin; n++) if (!uses[n]) release(IR(n - 1));
  trace();
  { u32 nt = 0;                                                /* parallel move: a target is written after every read of its register */
    for (u32 i = 0; i < nO; i++) if (onode[i] && oreg[i] != tgt(i)) { mvi[nt] = i; mvs[nt] = oreg[i]; nt++; }
    while (nt) {
      u32 k = nt;
      for (u32 m = 0; m < nt && k == nt; m++) { u32 hit = 0; for (u32 n2 = 0; n2 < nt; n2++) if (mvs[n2] == tgt(mvi[m])) hit = 1; if (!hit) k = m; }
      if (k == nt) {
        u32 s = mvs[0], tmp = take(-1);
        emit('M', tmp, s, 0); nmov++;
        for (u32 n2 = 0; n2 < nt; n2++) if (mvs[n2] == s) mvs[n2] = tmp;
        continue;
      }
      u32 i = mvi[k], s = mvs[k];
      for (u32 n2 = k; n2 + 1 < nt; n2++) { mvi[n2] = mvi[n2 + 1]; mvs[n2] = mvs[n2 + 1]; }
      nt--;
      if (oneg[i]) emit('N', tgt(i), s, 0); else { emit('M', tgt(i), s, 0); nmov++; }
    }
  }
  for (u32 i = 0; i < nO; i++) if (onode[i] && oreg[i] == tgt(i) && oneg[i]) emit('N', tgt(i), tgt(i), 0);
  for (u32 i = 0; i < nO; i++) if (!onode[i]) emit('S', tgt(i), oneg[i] ? 1 : 0, 0);
  info.calls = calls; info.ninst = kk; info.err = err; info.moves = nmov;
  { u32 top = 0;
    for (u32 k = 0; k < kk; k++) {
      u32 op = code[k][0], w = code[k][1] | (u32)code[k][2] << 8 | (u32)code[k][3] << 16 | (u32)code[k][4] << 24, d = w & 1023u, a = (w >> 10) & 1023u, b = (w >> 20) & 1023u, m = 0;
      if (op == '^' || op == '&' || op == '|') { m = d > a ? d : a; m = m > b ? m : b; }
      else if (op == 'N' || op == 'M') m = d > a ? d : a;
      else if (op == 'S') m = d;
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
    print("other code instructions", other_code(pr), "recovery program records executed per call", packed_ops(), "records", rec().instr, "init records", len(rec().init), "registers", pr.nregs)
  elif arg == "--text":
    sys.stdout.write(text())
  elif arg == "--gen-c":
    sys.stdout.write(GEN_C)
  elif arg == "--loss":
    for k, v in loss(plan(256)).items():
      print(k, v)
  else:
    json.dump(serve(json.load(sys.stdin)), sys.stdout)
