"""SHA-256 r43 bounded-restart machine with the tail-truncated walk f = B(S) XOR PD: complete program,
interpreter, checks (proof Sections 1-3, M, L, H)."""
import hashlib
import json
import re
import sys
from collections import defaultdict

M256 = (1 << 256) - 1
M32 = 0xFFFFFFFF
ZERO_H = (0, 0)
PD = 0x94D57C9CC1F00700283B762B87039C33E327C5AF3D4ED99F4823D1B238705132   # output polarity of the kernel planes
GATES = dict(XOR=43229, AND=4473, OR=6824, NOT=0)                        # gate split of the kernel DAG
KLEN, KREGS = 54526, 907                       # kernel instructions (gates and output moves), registers
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
   0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
K = (0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
   0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
   0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
   0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
   0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
   0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
   0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
   0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2)
PREFIX = (0x03F777B3, 0xEEC88896, 0xE8EBDB1C, 0x1B70C247, 0x177C95E3)
ROUNDS = 43
TAIL = True
OUT_ORDER = ("e4", "e3", "a8", "a7", "Q", "T1", "X", "Y")


# ------------------------------------------------ bitsliced kernel generator
class Net:
  """Constant-folding Boolean DAG with stored polarities (see provenance)."""

  def __init__(self):
    self.nodes = [("CONST", None, None, 0, 0)]
    self.opc = [None]
    self.src = [(None, None)]
    self.stored = [0]
    self.index = {}
    self.notword = {}

  def _new(self, kind, a, b, pa, pb, opc, srcs, stored):
    self.nodes.append((kind, a, b, pa, pb))
    self.opc.append(opc)
    self.src.append(srcs)
    self.stored.append(stored)
    return len(self.nodes) - 1

  def var(self, name):
    key = ("VAR", name)
    if key not in self.index:
      self.index[key] = self._new("VAR", name, None, 0, 0, None, (None, None), 0)
    return (self.index[key], 0)

  def effpol(self, h):
    return h[1] ^ self.stored[h[0]]

  def complement(self, nid):
    c = self.notword.get(nid)
    if c is None:
      c = self._new("NOT", nid, None, 0, 0, "NOT", (nid, None), self.stored[nid] ^ 1)
      self.notword[nid] = c
    return c

  def has_assoc(self, a, b):
    return self.opc[b] == "XOR" and any(("XOR", min(a, w), max(a, w)) in self.index for w in self.src[b])

  def _xor(self, x, y):
    (a, pa), (b, pb) = x, y
    if a == 0 or b == 0:
      return (a | b, pa ^ pb)
    if a == b:
      return (0, pa ^ pb)
    if a > b:
      a, b = b, a
    key = ("XOR", a, b)
    nid = self.index.get(key)
    if nid is None:
      nid = self._new("XOR", a, b, 0, 0, "XOR", (a, b), self.stored[a] ^ self.stored[b])
      self.index[key] = nid
    return (nid, pa ^ pb)

  def xor(self, x, y):
    (a, pa), (b, pb) = x, y
    if a == 0 or b == 0 or a == b or ("XOR", min(a, b), max(a, b)) in self.index:
      return self._xor(x, y)
    for s, ps, t, pt in ((a, pa, b, pb), (b, pb, a, pa)):
      if self.opc[t] == "XOR":
        u, v = self.src[t]
        if ("XOR", min(s, u), max(s, u)) in self.index:
          return self._xor(self._xor((s, ps), (u, pt)), (v, 0))
        if ("XOR", min(s, v), max(s, v)) in self.index:
          return self._xor(self._xor((s, ps), (v, pt)), (u, 0))
    return self._xor(x, y)

  def and_(self, x, y):
    (a, pa), (b, pb) = x, y
    if a == 0:
      return y if pa else ZERO_H
    if b == 0:
      return x if pb else ZERO_H
    if a == b:
      return x if pa == pb else ZERO_H
    if a > b:
      a, b, pa, pb = b, a, pb, pa
    key = ("AND", a, b, pa, pb)
    nid = self.index.get(key)
    if nid is not None:
      return (nid, 0)
    ea, eb = pa ^ self.stored[a], pb ^ self.stored[b]
    wa, wb = a, b
    if ea != eb:
      if b in self.notword and a not in self.notword:
        wb, eb = self.complement(b), eb ^ 1
      else:
        wa, ea = self.complement(a), ea ^ 1
    nid = self._new("AND", a, b, pa, pb, "AND" if ea == 0 else "OR", (wa, wb), ea)
    self.index[key] = nid
    return (nid, 0)

  def mux(self, s, x, y):
    t = self.xor(x, y)
    return self.xor(y, self.and_(s, t)) if self.effpol(s) == self.effpol(t) else self.xor(x, self.and_((s[0], s[1] ^ 1), t))

  def maj(self, x, y, z):
    return self.mux(self.xor(y, z), x, y)

  def full_adder(self, a, b, c):
    if a[0] and b[0] and c[0]:
      if self.has_assoc(b[0], a[0]) and not self.has_assoc(a[0], b[0]):
        a, b = b, a
      if self.has_assoc(a[0], b[0]):
        u = self.xor(a, b)
        return self.xor(u, c), self.mux(u, c, a)
    pa, pb, pc = self.effpol(a), self.effpol(b), self.effpol(c)
    p, q, r = ((c, a, b) if c[0] == 0 else (a, b, c) if a[0] == 0 else (b, a, c) if b[0] == 0
          else (a, b, c) if pb == pc else (b, a, c) if pa == pc else (c, a, b))
    if p[0] == 0 and q[0] and r[0]:
      if self.has_assoc(r[0], q[0]) and not self.has_assoc(q[0], r[0]):
        q, r = r, q
      if self.has_assoc(q[0], r[0]):
        t, k = self.xor(q, r), p[1]
        nt = (t[0], t[1] ^ 1)
        if k == 0 and self.effpol(q) == self.effpol(nt):
          return t, self.and_(q, nt)
        if k == 1 and self.effpol(q) != self.effpol(nt):
          na = self.and_((q[0], q[1] ^ 1), nt)
          return nt, (na[0], na[1] ^ 1)
    if p[0] == 0 and self.effpol(q) != self.effpol(r):
      t, k = self.xor(q, r), p[1]
      nt = (t[0], t[1] ^ 1)
      xx, other = (q, r) if self.effpol(q) == self.effpol(nt) else (r, q)
      if k == 0:
        return t, self.and_(xx, nt)
      na = self.and_((other[0], other[1] ^ 1), nt)
      return nt, (na[0], na[1] ^ 1)
    xq, xr = self.xor(q, p), self.xor(r, p)
    return self.xor(xq, r), self.xor(p, self.and_(xq, xr))

  def add(self, u, v, cin=ZERO_H):
    out, c = [], cin
    for i in range(len(u)):
      if i + 1 < len(u):
        s, c = self.full_adder(u[i], v[i], c)
      else:
        s = self.xor(self.xor(u[i], v[i]), c)
      out.append(s)
    return out

  def add_many(self, words):
    consts = [w for w in words if all(h[0] == 0 for h in w)]
    rest = [w for w in words if not all(h[0] == 0 for h in w)]
    nbits = len(words[0])
    mask = (1 << nbits) - 1
    cval = sum(sum(h[1] << i for i, h in enumerate(w)) for w in consts) & mask
    if not rest:
      return [(0, (cval >> i) & 1) for i in range(nbits)]
    best_pair, best_score = None, 0
    for i in range(len(rest)):
      for j in range(i + 1, len(rest)):
        score = sum(self.has_assoc(rest[i][bit][0], rest[j][bit][0])
              or self.has_assoc(rest[j][bit][0], rest[i][bit][0]) for bit in range(nbits))
        if score > best_score:
          best_score, best_pair = score, (i, j)
    max_cin = len(rest) - 1
    best_b, best_tz = 0, -1
    for b in range(max_cin + 1):
      rem = (cval - b) & mask
      tz = nbits if rem == 0 else (rem & -rem).bit_length() - 1
      if tz > best_tz:
        best_tz, best_b = tz, b
    cval = (cval - best_b) & mask
    if best_pair is not None:
      i, j = best_pair
      w2, w1 = rest.pop(j), rest.pop(i)
      r0 = w1[0] if self.has_assoc(w2[0][0], w1[0][0]) and not self.has_assoc(w1[0][0], w2[0][0]) else w2[0]
      cin = (0, 1) if (best_b == max_cin or (best_b > 0 and self.effpol(r0) == 0)) else ZERO_H
      best_b -= cin[1]
      rest.insert(0, self.add(w1, w2, cin))
    acc = [(0, (cval >> i) & 1) for i in range(nbits)] if cval else None
    while rest:
      if acc is None:
        acc = rest.pop(0)
        continue
      cin = (0, 1) if best_b > 0 and not all(h[0] == 0 for h in acc) else ZERO_H
      best_b -= cin[1]
      p0 = self.effpol(acc[0]) ^ cin[1]
      k = next((i for i, w in enumerate(rest) if self.effpol(w[0]) == p0), 0)
      acc = self.add(acc, rest.pop(k), cin)
    return acc

def rotr(u, k):
  return [u[(i + k) % len(u)] for i in range(len(u))]


def const_word(value):
  return [(0, (value >> i) & 1) for i in range(32)]


def shr(u, k):
  return [u[i + k] if i + k < len(u) else ZERO_H for i in range(len(u))]


def build_listing():
  """Kernel: planes of u (registers 0..255) -> planes of f(u) = B(S(u)) ^ PD, word OUT_ORDER[j] at planes
  32j..32j+31 (proof M.1). TAIL = False builds the untruncated S(u) ^ PD (lever measurement only)."""
  net = Net()
  x3 = lambda p, q, r: [net.xor(net.xor(a, b), c) for a, b, c in zip(p, q, r)]
  W = [const_word(w) for w in PREFIX]
  for j in range(8):
    W.append([net.var(("x", j, i)) for i in range(32)])
  W += [const_word(0x80000000), const_word(0), const_word(416)]
  a, b, c, d, e, f, g, h = [const_word(w) for w in IV]
  R, keep = ROUNDS, {}
  for t in range(R):
    if t >= 16:
      x, y = W[t - 15], W[t - 2]
      s0 = x3(rotr(x, 7), rotr(x, 18), shr(x, 3))
      s1 = x3(rotr(y, 17), rotr(y, 19), shr(y, 10))
      W.append(net.add_many([W[t - 16], s0, W[t - 7], s1]))
    if TAIL and t == R - 1:  # Y
      keep["Y"] = net.add(h, W[t])
      break
    if TAIL and t == R - 2:  # X
      ch = [net.mux(e[i], f[i], g[i]) for i in range(32)]
      keep["X"] = net.add_many([h, ch, W[t]])
      a, b, c, d, e, f, g, h = None, a, b, c, None, e, f, g
      continue
    S1 = x3(rotr(e, 6), rotr(e, 11), rotr(e, 25))
    ch = [net.mux(e[i], f[i], g[i]) for i in range(32)]
    t1 = net.add_many([h, S1, ch, const_word(K[t]), W[t]])
    if not TAIL or t < R - 6:
      S0 = x3(rotr(a, 2), rotr(a, 13), rotr(a, 22))
      mj = [net.maj(a[i], b[i], c[i]) for i in range(32)]
      t2 = net.add(S0, mj)
      an = net.add(t1, t2)
    elif t == R - 6:  # Q
      mj = [net.maj(a[i], b[i], c[i]) for i in range(32)]
      keep["a7"], keep["a8"] = a, b
      an = keep["Q"] = net.add(t1, mj)
    elif t == R - 5:
      an = keep["T1"] = t1
    else:
      an = None
    en = net.add(d, t1)
    if TAIL and t in (R - 4, R - 3):
      keep["e%d" % (R - t)] = en
    a, b, c, d, e, f, g, h = an, a, b, c, en, e, f, g
  if not TAIL:
    keep = dict(zip("abcdefgh", (a, b, c, d, e, f, g, h)))
  outputs = []
  for word in [keep[n] for n in (OUT_ORDER if TAIL else "abcdefgh")]:
    outputs.extend(word)
  reach, stack = set(), [n for n, _ in outputs if n]
  while stack:
    n = stack.pop()
    if n not in reach:
      reach.add(n)
      stack.extend(s for s in net.src[n] if s is not None)
  order = sorted(reach)
  ops = [(net.opc[n], n) + net.src[n] for n in order if net.opc[n] is not None]
  inputs = [n for n in order if net.opc[n] is None]
  assert [net.nodes[n][1] for n in inputs] == [("x", j, i) for j in range(8) for i in range(32)]
  assert not any(net.stored[n] for n in inputs)
  pd = sum(((p ^ net.stored[n]) if n else p) << i for i, (n, p) in enumerate(outputs))
  last_use, out_nodes = {}, {}
  for i, (_, _, a, b) in enumerate(ops):
    for s in (a, b):
      if s is not None:
        last_use[s] = i
  for i, (nid, _) in enumerate(outputs):
    if nid:
      out_nodes.setdefault(nid, i)
  out_at = {out_nodes[dst]: idx for idx, (_, dst, _, _) in enumerate(ops) if dst in out_nodes}
  reg_of = {n: i for i, n in enumerate(inputs)}
  free, reserved, next_reg, listing = [], set(), 256, []
  for i, (opc, dst, a, b) in enumerate(ops):
    dying = [s for s in (a, b) if s is not None and last_use.get(s) == i and s not in out_nodes]
    want, r = out_nodes.get(dst), None
    if want is not None and want in reserved:
      r = want
      reserved.discard(want)
    if r is None:
      cand = [s for s in dying if reg_of[s] >= 256]
      if cand:
        r = reg_of[cand[0]]
        dying.remove(cand[0])
      elif free:
        r = free.pop()
      elif reserved and dst not in out_nodes and any(last_use.get(dst, i) < out_at.get(h, 0) for h in reserved):
        r = max(h for h in reserved if last_use.get(dst, i) < out_at.get(h, 0))
        reserved.discard(r)
      else:
        r, next_reg = next_reg, next_reg + 1
    listing.append((opc, r, reg_of[a], None if b is None else reg_of[b]))
    reg_of[dst] = r
    for s in dying:
      (reserved.add if reg_of[s] < 256 else free.append)(reg_of[s])
  gates = {k: sum(op[0] == k for op in ops) for k in ("XOR", "AND", "OR", "NOT")}
  assert GATES is None or gates == GATES, gates
  nops = len(listing)
  pending = {i: reg_of[n] for i, (n, _) in enumerate(outputs) if reg_of[n] != i}
  temp, used_temp = next_reg, 0
  while pending:
    sources = set(pending.values())
    safe = next((d for d in pending if d not in sources), None)
    if safe is not None:
      listing.append(("MOV", safe, pending.pop(safe), None))
    else:
      victim = next(iter(pending))
      listing.append(("MOV", temp, victim, None))
      used_temp = 1
      pending = {d: temp if s == victim else s for d, s in pending.items()}
  held = {i: n for i, n in enumerate(inputs)}
  for (opc, dst, a, b), (lopc, r, ra, rb) in zip(ops, listing):
    assert lopc == opc and held[ra] == a and (b is None) == (rb is None)
    assert b is None or held[rb] == b
    held[r] = dst
  for opc, r, ra, _ in listing[nops:]:
    assert opc == "MOV"
    held[r] = held[ra]
  assert all(held[i] == n for i, (n, _) in enumerate(outputs))
  return listing, temp + used_temp, pd


def check_rules():
  """Check every gate-construction rule exhaustively on all operand classes (bit-parallel truth tables)."""
  def evaluate(net, assign, M):
    val = [0] * len(net.nodes)
    for n in range(1, len(net.nodes)):
      opc, (a, b) = net.opc[n], net.src[n]
      if opc is None:
        val[n] = assign[net.nodes[n][1]] ^ (M if net.stored[n] else 0)
      elif opc == "XOR":
        val[n] = val[a] ^ val[b]
      elif opc == "AND":
        val[n] = val[a] & val[b]
      elif opc == "OR":
        val[n] = val[a] | val[b]
      else:
        val[n] = val[a] ^ M
    return lambda h: val[h[0]] ^ (M if net.stored[h[0]] ^ h[1] else 0)

  net, M = Net(), 0xFF
  a, b, c = net.var("a"), net.var("b"), net.var("c")
  base = [(0, 0), (0, 1), a, b, c, net.and_(a, (b[0], 1)), net.xor(a, c),
      net.and_((a[0], 1), (c[0], 1)), net.and_(b, c)]
  pool = base + [(n, p ^ 1) for n, p in base]
  gates = [(x, y, net.xor(x, y), net.and_(x, y)) for x in pool for y in pool]
  adders = [(x, y, z) + net.full_adder(x, y, z) for x in pool for y in pool for z in pool]
  muxes = [(s_, x, y, net.mux(s_, x, y)) for s_ in pool for x in pool for y in pool]
  t = evaluate(net, dict(a=0xF0, b=0xCC, c=0xAA), M)
  for x, y, xo, an in gates:
    assert t(xo) == t(x) ^ t(y) and t(an) == t(x) & t(y)
  for x, y, z, sm, cy in adders:
    assert t(sm) == t(x) ^ t(y) ^ t(z)
    assert t(cy) == (t(x) & t(y)) | (t(x) & t(z)) | (t(y) & t(z))
  for s_, x, y, m in muxes:                      # the Ch rule: s ? x : y
    assert t(m) == ((t(s_) & t(x)) | (~t(s_) & t(y))) & M
  net, M = Net(), (1 << 256) - 1
  u = [net.var(("u", i)) for i in range(4)]
  v = [net.var(("v", i)) for i in range(4)]
  assign = {("u", i): sum(((l >> i) & 1) << l for l in range(256)) for i in range(4)}
  assign.update({("v", i): sum(((l >> (4 + i)) & 1) << l for l in range(256)) for i in range(4)})
  one = (0, 1)
  cases = [(u, v, lambda U, V: U + V), ([(n, p ^ 1) for n, p in u], v, lambda U, V: (15 - U) + V),
       ([net.xor(h, one) for h in v], u, lambda U, V: (15 - V) + U)]
  for k in range(16):
    cases.append((u, [(0, (k >> i) & 1) for i in range(4)], lambda U, V, k=k: U + k))
    cases.append(("many", k, None))
  built = []
  for x, y, fn in cases:
    if x == "many":
      k = y
      built.append((net.add_many([u, [(0, (k >> i) & 1) for i in range(4)], v]),
             lambda U, V, k=k: U + V + k))
    else:
      built.append((net.add(x, y), fn))
  t = evaluate(net, assign, M)
  for word, fn in built:
    got = [sum(((t(h) >> l) & 1) << i for i, h in enumerate(word)) for l in range(256)]
    assert got == [fn(l & 15, l >> 4) & 15 for l in range(256)]
  return len(gates) + len(adders) + len(muxes) + len(built)


def compile_kernel(listing, chunk=2000):
  """Compile the listing in small chunks (bounded compiler memory) using local variables."""
  import gc
  gc.collect()
  form = dict(XOR="r%d=r%d^r%d", AND="r%d=r%d&r%d", OR="r%d=r%d|r%d",
        NOT="r%d=r%d^M256", MOV="r%d=r%d")
  live = set(range(256))
  live_outs = {}
  bounds = list(range(0, len(listing), chunk))
  for s in reversed(bounds):
    end = min(s + chunk, len(listing))
    live_outs[s] = set(live)
    for opc, d, a, b in reversed(listing[s:end]):
      live.discard(d)
      if a is not None:
        live.add(a)
      if b is not None:
        live.add(b)
  parts = []
  for s in bounds:
    end = min(s + chunk, len(listing))
    sub = listing[s:end]
    written = set()
    rbw = []
    for opc, d, a, b in sub:
      for src in (a, b):
        if src is not None and src not in written:
          written.add(src)
          rbw.append(src)
      written.add(d)
    wb = sorted(written & live_outs[s])
    body = ["def part(r, M256=M256):"]
    for i in rbw:
      body.append(f" r{i}=r[{i}]")
    for opc, d, a, b in sub:
      args = (d, a, b) if opc in ("XOR", "AND", "OR") else (d, a)
      body.append(" " + (form[opc] % args))
    for d in wb:
      body.append(f" r[{d}]=r{d}")
    scope = {"M256": M256}
    exec(compile("\n".join(body), "<kernel>", "exec"), scope)
    parts.append(scope["part"])

  def kern(r):
    for part in parts:
      part(r)
  return kern


# ------------------------------------------------------- scalar SHA-256 reference (ROUNDS steps)
class Words:
  """32-bit word ops on packed 64-bit fields (one per point; ones=1: plain ints); results masked."""

  def __init__(self, ones=1):
    self.one, self.m = ones, M32 * ones

  def k(self, c):
    return c * self.one

  def add(self, *xs):
    return sum(xs) & self.m

  def sub(self, x, y):
    return (x + self.k(1 << 32) - y) & self.m

  def rot(self, x, n):
    return ((x >> n) | (x << (32 - n))) & self.m

  def S0(self, x):
    return self.rot(x, 2) ^ self.rot(x, 13) ^ self.rot(x, 22)

  def S1(self, x):
    return self.rot(x, 6) ^ self.rot(x, 11) ^ self.rot(x, 25)

  def maj(self, x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)

  def ch(self, x, y, z):
    return (x & y) ^ ((x ^ self.m) & z)

  def t2(self, x, y, z):
    return self.add(self.S0(x), self.maj(x, y, z))


WD = Words()


def steps(o, msg, rounds, tail=False):
  """FIPS 180-4 steps 0..rounds-1 of (P, msg, padding): the state, or (tail) the kernel's output words."""
  W = [o.k(w) for w in PREFIX] + list(msg) + [o.k(0x80000000), o.k(0), o.k(416)]
  for t in range(16, max(16, rounds)):
    x, y = W[t - 15], W[t - 2]
    W.append(o.add(W[t - 16], o.rot(x, 7) ^ o.rot(x, 18) ^ ((x >> 3) & o.m), W[t - 7],
            o.rot(y, 17) ^ o.rot(y, 19) ^ ((y >> 10) & o.m)))
  a, b, c, d, e, f, g, h = [o.k(w) for w in IV]
  R, out = rounds, {}
  for t in range(R - 1 if tail else R):
    if tail and t == R - 2:
      out["X"] = o.add(h, o.ch(e, f, g), W[t])
      a, b, c, d, e, f, g, h = None, a, b, c, None, e, f, g
      continue
    t1 = o.add(h, o.S1(e), o.ch(e, f, g), o.k(K[t]), W[t])
    an = o.add(t1, o.t2(a, b, c)) if not tail or t < R - 6 else None
    if tail and t == R - 6:
      out["a7"], out["a8"] = a, b
      an = out["Q"] = o.add(t1, o.maj(a, b, c))
    if tail and t == R - 5:
      an = out["T1"] = t1
    en = o.add(d, t1)
    if tail and t in (R - 4, R - 3):
      out["e%d" % (R - t)] = en
    a, b, c, d, e, f, g, h = an, a, b, c, en, e, f, g
  if not tail:
    return (a, b, c, d, e, f, g, h)
  out["Y"] = o.add(h, W[R - 1])
  return tuple(out[n] for n in OUT_ORDER)


def state_words(u, rounds=None):
  """Working state (a, ..., h) after step rounds - 1 (default ROUNDS - 1) of the one padded block of M(u)."""
  return steps(WD, [(u >> (32 * j)) & M32 for j in range(8)], ROUNDS if rounds is None else rounds)


def tail_words(u):
  """The output words computed by the truncated step loop (the kernel's own composition)."""
  return steps(WD, [(u >> (32 * j)) & M32 for j in range(8)], ROUNDS, tail=True)


def tail_map(S, o=WD):
  """The map B of proof Section 1.2: final state S = (a, ..., h) -> the output words in OUT_ORDER."""
  A, Bq, Cq, Dq, E, F, G, H = S
  R, sub, t2 = ROUNDS, o.sub, o.t2
  T1_1 = sub(A, t2(Bq, Cq, Dq))
  a5 = sub(E, T1_1)
  a6 = sub(F, sub(Bq, t2(Cq, Dq, a5)))
  a7 = sub(G, sub(Cq, t2(Dq, a5, a6)))
  a8 = sub(H, sub(Dq, t2(a5, a6, a7)))
  w = dict(e4=H, e3=G, a8=a8, a7=a7, Q=sub(a6, o.S0(a7)), T1=sub(a5, t2(a6, a7, a8)),
       X=sub(sub(sub(F, o.k(K[R - 2])), o.S1(G)), a6),
       Y=sub(sub(sub(T1_1, o.k(K[R - 1])), o.S1(F)), o.ch(F, G, H)))
  return tuple(w[n] for n in OUT_ORDER)


def tail_inverse(O, o=WD):
  """Inverse of tail_map: the output words -> the final working state (a, ..., h)."""
  w = dict(zip(OUT_ORDER, O))
  R, add, sub, t2 = ROUNDS, o.add, o.sub, o.t2
  a8, a7, H, G = w["a8"], w["a7"], w["e4"], w["e3"]
  a6 = add(w["Q"], o.S0(a7))
  a5 = add(w["T1"], t2(a6, a7, a8))
  Dq = add(sub(H, a8), t2(a5, a6, a7))
  Cq = add(sub(G, a7), t2(Dq, a5, a6))
  F = add(w["X"], o.k(K[R - 2]), o.S1(G), a6)
  Bq = add(sub(F, a6), t2(Cq, Dq, a5))
  T1_1 = add(w["Y"], o.k(K[R - 1]), o.S1(F), o.ch(F, G, H))
  return (add(T1_1, t2(Bq, Cq, Dq)), Bq, Cq, Dq, add(a5, T1_1), F, G, H)


def tail_program():
  """B as straight-line 256-bit word operations (proof 3.1): register 0 = packed S, result in register 1."""
  prog = []

  def op(o, a=None, b=None, imm=None):
    prog.append((o, len(prog) + 2, a, b, imm))
    return len(prog) + 1
  m32, k1, k2 = op("LDI", imm=M32), op("LDI", imm=K[ROUNDS - 1]), op("LDI", imm=K[ROUNDS - 2])
  A, Bq, Cq, Dq, E, F, G, H = [op("AND", 0, m32)] + [op("AND", op("SHRI", 0, imm=32 * j), m32) for j in range(1, 8)]
  sub = lambda x, y: op("AND", op("SUB", x, y), m32)

  def sig(x, *r):
    rot = lambda k: op("OR", op("SHRI", x, imm=k), op("SHLI", x, imm=32 - k))
    return op("AND", op("XOR", op("XOR", rot(r[0]), rot(r[1])), rot(r[2])), m32)
  maj = lambda x, y, z: op("OR", op("AND", x, y), op("AND", z, op("OR", x, y)))
  t2 = lambda x, y, z: op("ADD", sig(x, 2, 13, 22), maj(x, y, z))
  T1_1 = sub(A, t2(Bq, Cq, Dq))
  a5 = sub(E, T1_1)
  a6 = sub(F, sub(Bq, t2(Cq, Dq, a5)))
  a7 = sub(G, sub(Cq, t2(Dq, a5, a6)))
  a8 = sub(H, sub(Dq, t2(a5, a6, a7)))
  w = dict(e4=H, e3=G, a8=a8, a7=a7, Q=sub(a6, sig(a7, 2, 13, 22)), T1=sub(a5, t2(a6, a7, a8)),
       X=sub(op("SUB", op("SUB", F, k2), sig(G, 6, 11, 25)), a6),
       Y=sub(op("SUB", op("SUB", T1_1, k1), sig(F, 6, 11, 25)), op("XOR", H, op("AND", F, op("XOR", G, H)))))
  acc = w[OUT_ORDER[0]]
  for j, n in enumerate(OUT_ORDER[1:], 1):
    acc = op("OR", acc, op("SHLI", w[n], imm=32 * j))
  prog.append(("MOV", 1, acc, None, None))
  return prog


def run_tail_program(prog, s):
  """Execute the B program on the packed state s with 256-bit word semantics."""
  r = {0: s}
  for o, d, a, b, imm in prog:
    x, y = r.get(a), r.get(b)
    r[d] = {"LDI": lambda: imm, "AND": lambda: x & y, "OR": lambda: x | y, "XOR": lambda: x ^ y,
        "ADD": lambda: (x + y) & M256, "SUB": lambda: (x - y) & M256, "SHRI": lambda: x >> imm,
        "SHLI": lambda: (x << imm) & M256, "MOV": lambda: x}[o]()
  return r[1]


def state_words_canonical(u):
  """The state after all 64 steps via hashlib.sha256 of M(u), feed-forward undone; pins the explicit
  reference's encoding, padding and feed-forward (proof Section 1.3)."""
  d = hashlib.sha256(message(u)).digest()
  return tuple((int.from_bytes(d[4 * j:4 * j + 4], "big") - IV[j]) & M32 for j in range(8))


def walk_int(u):
  """B(S(u)), word j at bits 32j..; equal values iff equal digests (Lemma 0)."""
  return sum(w << (32 * j) for j, w in enumerate(tail_map(state_words(u))))


def walk_table(us):
  """walk_int for every u in us at once: the same steps and B on packed 64-bit fields (Words)."""
  import struct
  us = list(us)
  n = len(us)
  pack = lambda vals: int.from_bytes(struct.pack("<%dQ" % n, *vals), "little")
  o = Words(pack([1] * n))
  words = tail_map(steps(o, [pack([(u >> (32 * j)) & M32 for u in us]) for j in range(8)], ROUNDS), o)
  out = [0] * n
  for j, v in enumerate(words):
    for i, x in enumerate(struct.unpack("<%dQ" % n, v.to_bytes(8 * n, "little"))):
      out[i] |= x << (32 * j)
  return out


def message(u):
  """M(u) = P || x: the five big-endian prefix words, then the eight big-endian words of u (52 bytes)."""
  return b"".join(w.to_bytes(4, "big") for w in PREFIX) + b"".join(
    ((u >> (32 * j)) & M32).to_bytes(4, "big") for j in range(8))


def digest_mask(n):
  """Mask 'low n bits of digest word 7 agree': output word 0 is e_{R-4} = h = S(u)[7] (proof 1.3)."""
  return (bytes(28) + ((1 << n) - 1).to_bytes(4, "big")).hex()


# ------------------------------------------------- scalar reference machine
def bounded_search(step, *, width, dp_bits, key_bits, lanes, batches, cap,
          capacity, start_limit, rho, stage1_bits=32, stage2_limit, win=11):
  """Scalar reference state machine."""
  assert 0 < dp_bits and dp_bits + 4 + key_bits <= width and 0 < key_bits and win in (11, 16)
  assert lanes <= start_limit <= 1 << width
  mask = (1 << width) - 1
  dp_mask = (1 << dp_bits) - 1
  s1_mask = (1 << min(stage1_bits, dp_bits)) - 1
  key_mask = (1 << key_bits) - 1

  def distinguished(u):
    return u & dp_mask == 0 and (u >> dp_bits) & 15 < win
  states = [(rho + i) & mask for i in range(lanes)]
  ids = list(range(lanes))
  births = [0] * lanes
  next_id = lanes
  table = {}
  stats = dict(search_evaluations=0, recovery_evaluations=0,
         final_evaluations=0, cuts=0, insertions=0, restarts=0,
         max_age=0, reason=0, stage2=0)

  def finish(reason, pair=None):
    stats['reason'] = reason
    stats['allocated_starts'] = next_id
    stats['stored_endpoints'] = len(table)
    return pair, stats

  def restart(lane, batch):
    nonlocal next_id
    if next_id >= start_limit:
      return False
    ids[lane] = next_id
    states[lane] = (rho + next_id) & mask
    births[lane] = batch
    next_id += 1
    stats['restarts'] += 1
    return True

  def recover(old_id, current_id, current_length, endpoint):
    first = (rho + old_id) & mask
    old_endpoint = first
    length = 0
    for length in range(1, cap + 1):
      old_endpoint = step(old_endpoint)
      stats['recovery_evaluations'] += 1
      if distinguished(old_endpoint):
        break
    else:
      return 8, None
    if old_endpoint != endpoint:
      return 2, None
    second = (rho + current_id) & mask
    a, b = first, second
    for _ in range(max(0, length - current_length)):
      a = step(a)
      stats['recovery_evaluations'] += 1
    for _ in range(max(0, current_length - length)):
      b = step(b)
      stats['recovery_evaluations'] += 1
    if a == b:
      return 3, None
    for _ in range(min(length, current_length)):
      na, nb = step(a), step(b)
      stats['recovery_evaluations'] += 2
      if na == nb:
        stats['final_evaluations'] += 2
        if a != b and step(a) == step(b):
          return 1, (a, b)
        return 8, None
      a, b = na, nb
    return 8, None

  for batch in range(1, batches + 1):
    outputs = [step(u) for u in states]
    stats['search_evaluations'] += lanes
    states[:] = outputs
    if any(u & s1_mask == 0 for u in outputs):
      stats['stage2'] += 1
      if stats['stage2'] > stage2_limit:
        return finish(9)
    flags = [distinguished(u) for u in outputs]
    for lane in range(lanes):
      stats['max_age'] = max(stats['max_age'], batch - births[lane])
      if not flags[lane]:
        continue
      key = (outputs[lane] >> (dp_bits + 4)) & key_mask
      if key in table:
        reason, pair = recover(table[key], ids[lane],
                    batch - births[lane], outputs[lane])
        return finish(reason, pair)
      if len(table) >= capacity:
        return finish(4)
      table[key] = ids[lane]
      stats['insertions'] += 1
      if not restart(lane, batch):
        return finish(5)
    for lane in range(lanes):
      if not flags[lane] and batch - births[lane] >= cap:
        stats['cuts'] += 1
        if not restart(lane, batch):
          return finish(5)
  return finish(6)


# --------------------------------------------------------- machine program
NREG = 1024
TAIL_OPS = len(tail_program())                    # word operations of the map B, charged with every COMP
TAIL_CODE = sum(40 if o == "LDI" else 8 for o, *_ in tail_program())   # its code bytes (image formats)


def tail_regs(prog):
  """Peak number of live words of the B program: its scratch registers (proof Section 3.1)."""
  last = {s: i for i, op in enumerate(prog) for s in op[2:4] if s is not None}
  live, peak = {0}, 1
  for i, op in enumerate(prog):
    live = {x for x in live | {op[1]} if last.get(x, -1) > i or x == op[1]}
    peak = max(peak, len(live))
  return peak


TAIL_REGS = tail_regs(tail_program()) + 1   # and the result register
COST = dict(BEQ=2, BNE=2, BLT=2, BGE=2, COMP=64 + TAIL_OPS, OUT=2)
REGIONS = ("setup", "loop", "stage2", "kernel", "diag", "epscan", "key", "table",
      "restart", "cut", "recovery", "term")
CTRL = ("ZERO ONE ONES C3 C11 C15 C256 M17 KM DPM PD BMAX RCAP ULIM IDL E2LIM WM RHO NID "
    "CNT B NEXTCUT H2 D ND LANE KEY E S NOTLANE T0 T1 T2 T3 T4 T5 RR EIDX ID1 "
    "ID2 L1 L2 X Y A BV FA FB CN MINL MINB").split()


def build_program(p, kregs):
  """Emit the machine program for parameters p (see proof.md, Section M)."""
  w, d, k, U = p["w"], p["d"], p["k"], p["U"]
  win = p.get("win", 11)
  assert win in (11, 16)
  diag = w < 256
  assert 1 < d and d + 4 + k <= w <= 256 and k <= 47 and p["IDL"] <= 1 << 17
  R = {n: kregs + i for i, n in enumerate(CTRL if diag else [c for c in CTRL if c != "WM"])}
  keyw = -(-U // 4)
  KEYB, BIRB, LIDB = 0, keyw, keyw + 256
  code, labels, region = [], {}, ["setup"]

  def e(op, *args):
    code.append((op, args, region[0]))

  def lab(name):
    labels[name] = len(code)

  def r(name):
    return R[name] if isinstance(name, str) else name

  def x3(op, dst, a, b):
    e(op, r(dst), r(a), r(b))

  def proj(name):
    if diag:
      region[0], old = "diag", region[0]
      x3("AND", name, name, "WM")
      region[0] = old

  consts = dict(ZERO=0, ONE=1, ONES=M256, C3=3, C11=11, C15=15, C256=256, M17=0x1FFFF,
         KM=(1 << k) - 1, DPM=(1 << d) - 1, PD=PD, BMAX=p["B"], RCAP=p["R"],
         ULIM=U, IDL=p["IDL"], E2LIM=p["E2MAX"] + 1)
  s1 = min(32, d)
  if diag:
    consts["WM"] = (1 << w) - 1
  for name, value in consts.items():
    e("LDI", R[name], value)
  e("RAND", R["RHO"])
  proj("RHO")
  x3("MOV", "T1", "ZERO", None)
  e("LDI", R["T2"], LIDB + 256)
  lab("ZL")
  e("ST", R["T1"], R["ZERO"])
  e("ADDI", R["T1"], R["T1"], 1)
  e("BNE", R["T1"], R["T2"], "ZL")
  for n in ("NID", "CNT", "B", "LANE", "H2"):
    x3("MOV", n, "ZERO", None)
  lab("IL")
  e("LDI", R["RR"], 0)
  e("JMP", "RESTART")
  lab("RET0")
  e("ADDI", R["LANE"], R["LANE"], 1)
  e("BNE", R["LANE"], R["C256"], "IL")
  e("ADDI", R["B"], R["ZERO"], 1)
  x3("MOV", "NEXTCUT", "RCAP", None)
  lab("LOOP")
  region[0] = "kernel"
  e("KERNEL")
  region[0] = "diag"
  for j in range(w, 256):
    e("XOR", j, j, j)
  region[0] = "loop"
  e("OR", R["D"], 0, 1)
  for j in range(2, s1):
    e("OR", R["D"], R["D"], j)
  e("BNE", R["D"], R["ONES"], "S2")
  lab("EPD")
  e("BGE", R["B"], R["NEXTCUT"], "CUTB")
  lab("CUTD")
  e("BEQ", R["B"], R["BMAX"], "FAIL6")
  e("ADDI", R["B"], R["B"], 1)
  e("JMP", "LOOP")
  region[0] = "stage2"
  lab("S2")
  e("ADDI", R["H2"], R["H2"], 1)
  e("BGE", R["H2"], R["E2LIM"], "FAIL9")
  for j in range(s1, d):
    e("OR", R["D"], R["D"], j)
  if win < 16:
    e("AND", R["T0"], d + 1, d)
    e("OR", R["T0"], R["T0"], d + 2)
    e("AND", R["T0"], R["T0"], d + 3)
    x3("OR", "D", "D", "T0")
  e("BNE", R["D"], R["ONES"], "EPB")
  e("JMP", "EPD")
  region[0] = "epscan"
  lab("EPB")
  x3("NOT", "ND", "D", None)
  x3("MOV", "LANE", "ZERO", None)
  lab("EPL")
  x3("SHR", "T0", "ND", "LANE")
  x3("AND", "T0", "T0", "ONE")
  e("BEQ", R["T0"], R["ZERO"], "EPN")
  region[0] = "key"
  x3("MOV", "KEY", "ZERO", None)
  for j in range(k):
    x3("SHR", "T0", d + 4 + j, "LANE")
    x3("AND", "T0", "T0", "ONE")
    e("SHLI", R["T0"], R["T0"], j)
    x3("OR", "KEY", "KEY", "T0")
  region[0] = "table"
  x3("MOV", "EIDX", "ZERO", None)
  lab("SC")
  e("BEQ", R["EIDX"], R["CNT"], "NOM")
  e("SHRI", R["T1"], R["EIDX"], 2)
  e("ADDI", R["T1"], R["T1"], KEYB)
  x3("LD", "T2", "T1", None)
  x3("AND", "T3", "EIDX", "C3")
  e("SHLI", R["T3"], R["T3"], 6)
  x3("SHR", "T2", "T2", "T3")
  x3("AND", "T4", "T2", "KM")
  e("BEQ", R["T4"], R["KEY"], "MATCH")
  e("ADDI", R["EIDX"], R["EIDX"], 1)
  e("JMP", "SC")
  lab("NOM")
  e("BEQ", R["CNT"], R["ULIM"], "FAIL4")
  e("ADDI", R["T1"], R["LANE"], LIDB)
  x3("LD", "T5", "T1", None)
  e("SHLI", R["T5"], R["T5"], 47)
  x3("OR", "T5", "T5", "KEY")
  e("SHRI", R["T1"], R["CNT"], 2)
  e("ADDI", R["T1"], R["T1"], KEYB)
  x3("LD", "T2", "T1", None)
  x3("AND", "T3", "CNT", "C3")
  e("SHLI", R["T3"], R["T3"], 6)
  x3("SHL", "T4", "T5", "T3")
  x3("OR", "T2", "T2", "T4")
  e("ST", R["T1"], R["T2"])
  e("ADDI", R["CNT"], R["CNT"], 1)
  e("LDI", R["RR"], 1)
  e("JMP", "RESTART")
  region[0] = "epscan"
  lab("RET1")
  lab("EPN")
  e("ADDI", R["LANE"], R["LANE"], 1)
  e("BNE", R["LANE"], R["C256"], "EPL")
  e("JMP", "EPD")
  region[0] = "restart"
  lab("RESTART")
  e("BEQ", R["NID"], R["IDL"], "FAIL5")
  e("ADDI", R["T1"], R["LANE"], LIDB)
  e("ST", R["T1"], R["NID"])
  e("ADDI", R["T1"], R["LANE"], BIRB)
  e("ST", R["T1"], R["B"])
  x3("ADD", "S", "RHO", "NID")
  proj("S")
  e("ADDI", R["NID"], R["NID"], 1)
  x3("SHL", "T0", "ONE", "LANE")
  x3("NOT", "NOTLANE", "T0", None)
  for j in range(256):
    e("SHRI", R["T0"], R["S"], j)
    x3("AND", "T0", "T0", "ONE")
    x3("SHL", "T0", "T0", "LANE")
    e("AND", j, j, R["NOTLANE"])
    e("OR", j, j, R["T0"])
  e("BEQ", R["RR"], R["ZERO"], "RET0")
  e("BEQ", R["RR"], R["ONE"], "RET1")
  e("JMP", "RET2")
  region[0] = "cut"
  lab("CUTB")
  x3("MOV", "MINB", "B", None)
  x3("MOV", "LANE", "ZERO", None)
  lab("CL")
  e("ADDI", R["T1"], R["LANE"], BIRB)
  x3("LD", "T2", "T1", None)
  x3("SUB", "T3", "B", "T2")
  e("BLT", R["T3"], R["RCAP"], "CK")
  lab("CUTR")
  e("LDI", R["RR"], 2)
  e("JMP", "RESTART")
  lab("RET2")
  x3("MOV", "T2", "B", None)
  lab("CK")
  e("BGE", R["T2"], R["MINB"], "CN_")
  x3("MOV", "MINB", "T2", None)
  lab("CN_")
  e("ADDI", R["LANE"], R["LANE"], 1)
  e("BNE", R["LANE"], R["C256"], "CL")
  x3("ADD", "NEXTCUT", "MINB", "RCAP")
  e("JMP", "CUTD")
  region[0] = "recovery"
  lab("MATCH")
  e("SHRI", R["ID1"], R["T2"], 47)
  x3("AND", "ID1", "ID1", "M17")
  e("ADDI", R["T1"], R["LANE"], LIDB)
  x3("LD", "ID2", "T1", None)
  e("ADDI", R["T1"], R["LANE"], BIRB)
  x3("LD", "T2", "T1", None)
  x3("SUB", "L2", "B", "T2")
  x3("MOV", "E", "ZERO", None)
  for j in range(256):
    x3("SHR", "T0", j, "LANE")
    x3("AND", "T0", "T0", "ONE")
    e("SHLI", R["T0"], R["T0"], j)
    x3("OR", "E", "E", "T0")
  x3("ADD", "X", "RHO", "ID1")
  proj("X")
  x3("MOV", "L1", "ZERO", None)

  def step(dst, src):
    x3("COMP", dst, src, None)
    x3("XOR", dst, dst, "PD")
    proj(dst)

  lab("RC")
  e("BEQ", R["L1"], R["RCAP"], "FAIL8")
  step("Y", "X")
  e("ADDI", R["L1"], R["L1"], 1)
  x3("MOV", "X", "Y", None)
  x3("AND", "T0", "Y", "DPM")
  e("BNE", R["T0"], R["ZERO"], "RC")
  if win < 16:
    e("SHRI", R["T0"], R["Y"], d)          # four-bit window below 11?
    x3("AND", "T0", "T0", "C15")
    e("BGE", R["T0"], R["C11"], "RC")
  e("BNE", R["Y"], R["E"], "FAIL2")
  x3("ADD", "A", "RHO", "ID1")
  proj("A")
  x3("ADD", "BV", "RHO", "ID2")
  proj("BV")
  e("BLT", R["L1"], R["L2"], "AL2")
  for tag, hi, lo, reg in (("AA", "L1", "L2", "A"), ("AB", "L2", "L1", "BV")):
    if tag == "AB":
      lab("AL2")
    x3("SUB", "CN", hi, lo)
    x3("MOV", "MINL", lo, None)
    lab(tag)
    e("BEQ", R["CN"], R["ZERO"], "AD")
    step(reg, reg)
    x3("SUB", "CN", "CN", "ONE")
    e("JMP", tag)
  lab("AD")
  e("BEQ", R["A"], R["BV"], "FAIL3")
  lab("PL")
  e("BEQ", R["MINL"], R["ZERO"], "FAIL8")
  step("FA", "A")
  step("FB", "BV")
  e("BEQ", R["FA"], R["FB"], "FOUND")
  x3("MOV", "A", "FA", None)
  x3("MOV", "BV", "FB", None)
  x3("SUB", "MINL", "MINL", "ONE")
  e("JMP", "PL")
  lab("FOUND")
  e("BEQ", R["A"], R["BV"], "FAIL8")
  step("FA", "A")
  step("FB", "BV")
  e("BNE", R["FA"], R["FB"], "FAIL8")
  region[0] = "term"
  e("OUT", R["A"], R["BV"])
  e("HALT", 1)
  for n in (2, 3, 4, 5, 6, 8, 9):
    lab("FAIL%d" % n)
    e("HALT", n)
  code = [(op, tuple(labels[a] if isinstance(a, str) else a for a in args), reg)
      for op, args, reg in code]
  return dict(code=code, labels=labels, nregs=kregs + len(R), nmem=LIDB + 256, ones=R["ONES"],
        regs=R, entry=0)


def code_bytes(prog, klen, per_instruction=None):
  """Declared encoding: kernel 4 bytes per instruction behind an 8-byte KERNEL
  header; control 8; LDI 40."""
  n = sum(op != "KERNEL" for op, _, _ in prog["code"])
  if per_instruction is not None:
    return per_instruction * (klen + n + 1)
  return 4 * klen + sum(40 if op == "LDI" else 8 for op, _, _ in prog["code"])


SHORT = ("XOR", "AND", "OR", "NOT", "MOV")
LONG = SHORT + ("ADD", "ADDI", "SUB", "SHL", "SHR", "SHLI", "SHRI", "LD", "ST", "BEQ",
        "BNE", "BLT", "BGE", "JMP", "RAND", "COMP", "OUT", "HALT", "KERNEL")
BRANCH = ("BEQ", "BNE", "BLT", "BGE", "JMP")
IMM = ("ADDI", "SHLI", "SHRI", "HALT", "KERNEL")
KOPS = ("XOR", "AND", "OR")


def kernel_forms(listing, ones):
  """Register-only three-operand forms: NOT d,a = XOR d,a,ONES; MOV d,a = OR d,a,a."""
  return [("XOR", d, a, ones) if opc == "NOT" else ("OR", d, a, a) if opc == "MOV"
      else (opc, d, a, b) for opc, d, a, b in listing]


def encode(prog, listing):
  """Serialize the program image; the three formats are proof Section 3.2. Branch targets are byte
  offsets into the image."""
  offsets, pos = [], 0
  for op, _, _ in prog["code"]:
    offsets.append(pos)
    pos += 8 + 4 * len(listing) if op == "KERNEL" else 40 if op == "LDI" else 8
  out = bytearray()
  for op, args, _ in prog["code"]:
    if op == "KERNEL":
      out += (16 + LONG.index("KERNEL") | len(listing) << 38).to_bytes(8, "little")
      for opc, d, a, b in kernel_forms(listing, prog["ones"]):
        assert 0 <= d < 1024 and 0 <= a < 1024 and 0 <= b < 1024
        out += (1 + KOPS.index(opc) | d << 2 | a << 12 | b << 22).to_bytes(4, "little")
      continue
    if op == "LDI":
      out += (64 | args[0] << 8 | args[1] << 18).to_bytes(40, "little")
      continue
    args = [x for x in args if x is not None]
    imm = 0
    if op in BRANCH:
      imm = offsets[args.pop()]
    elif op in IMM:
      imm = args.pop()
    regs = args + [0] * (3 - len(args))
    assert all(0 <= r < 1024 for r in regs) and 0 <= imm < 1 << 24
    out += (16 + LONG.index(op) | regs[0] << 8 | regs[1] << 18 | regs[2] << 28
        | imm << 38).to_bytes(8, "little")
  assert len(out) == pos
  return bytes(out)


def decode(image):
  """Decode an image into (code, kernel listing); the inverse of encode."""
  raw, pos = [], 0
  while pos < len(image):
    op = image[pos]
    if op == 16 + LONG.index("KERNEL"):
      v = int.from_bytes(image[pos:pos + 8], "little")
      count, pos = v >> 38, pos + 8
      start = pos
      for _ in range(count):
        w = int.from_bytes(image[pos:pos + 4], "little")
        raw.append((pos if pos == start else None, "K",
              (KOPS[(w & 3) - 1], w >> 2 & 1023, w >> 12 & 1023, w >> 22 & 1023)))
        pos += 4
      raw[-count] = (start - 8, "K", raw[-count][2])
    elif op == 64:
      v = int.from_bytes(image[pos:pos + 40], "little")
      raw.append((pos, "LDI", (v >> 8 & 1023, v >> 18)))
      pos += 40
    else:
      v = int.from_bytes(image[pos:pos + 8], "little")
      raw.append((pos, LONG[op - 16], (v >> 8 & 1023, v >> 18 & 1023, v >> 28 & 1023,
                      v >> 38)))
      pos += 8
  index, code, listing, n = {}, [], [], 0
  for at, op, f in raw:
    if op == "K":
      if not listing:
        index[at] = n
        n += 1
      listing.append(f)
    else:
      index[at] = n
      n += 1
  nargs = dict(XOR=3, AND=3, OR=3, ADD=3, SUB=3, SHL=3, SHR=3, NOT=2, MOV=2, LD=2,
         ST=2, COMP=2, OUT=2, ADDI=2, SHLI=2, SHRI=2, BEQ=2, BNE=2, BLT=2, BGE=2,
         RAND=1, JMP=0, HALT=0, KERNEL=0)
  seen = False
  for at, op, f in raw:
    if op == "K":
      if not seen:
        code.append(("KERNEL", ()))
        seen = True
    elif op == "LDI":
      code.append(("LDI", f))
    else:
      args = list(f[:nargs[op]])
      if op in BRANCH:
        args.append(index[f[3]])
      elif op in IMM:
        args.append(f[3])
      code.append((op, tuple(args)))
  return code, listing


def load(p, kregs, listing):
  """Build, serialize and decode; the interpreter runs the decoded image."""
  prog = build_program(p, kregs)
  image = encode(prog, listing)
  code, decoded = decode(image)
  norm = [(op, tuple(x for x in a if x is not None)) for op, a, _ in prog["code"]]
  assert code == norm and decoded == kernel_forms(listing, prog["ones"])
  assert len(image) == code_bytes(prog, len(listing))
  prog = dict(prog, code=[(op, a, reg) for (op, a), (_, _, reg) in zip(code, prog["code"])])
  return prog, image


class Machine:
  """Block interpreter: per-block static costs times execution counts."""

  def __init__(self, prog, klen):
    code = prog["code"]
    starts = {0} | {i + 1 for i, (op, _, _) in enumerate(code)
            if op in ("BEQ", "BNE", "BLT", "BGE", "JMP", "HALT", "KERNEL")}
    starts |= set(prog["labels"].values())
    starts = sorted(s for s in starts if s < len(code))
    self.block_of = {s: i for i, s in enumerate(starts)}
    self.costs, src = [], ["def make(E, M):", " fs = []"]
    cmp = dict(BEQ="==", BNE="!=", BLT="<", BGE=">=")
    for bi, s in enumerate(starts):
      end = starts[bi + 1] if bi + 1 < len(starts) else len(code)
      cost = defaultdict(int)
      src.append(" def f(r, m):")
      top, nxt = len(src), None
      for i in range(s, end):
        op, a, reg = code[i]
        cost[reg] += klen + 1 if op == "KERNEL" else COST.get(op, 1)
        if op == "COMP":
          cost["compressions"] += 1
        line = {
          "XOR": "r[{0}]=r[{1}]^r[{2}]", "AND": "r[{0}]=r[{1}]&r[{2}]",
          "OR": "r[{0}]=r[{1}]|r[{2}]", "NOT": "r[{0}]=r[{1}]^M",
          "MOV": "r[{0}]=r[{1}]", "ADD": "r[{0}]=(r[{1}]+r[{2}])&M",
          "ADDI": "r[{0}]=(r[{1}]+{2})&M", "SUB": "r[{0}]=(r[{1}]-r[{2}])&M",
          "SHL": "r[{0}]=(r[{1}]<<r[{2}])&M", "SHR": "r[{0}]=r[{1}]>>r[{2}]",
          "SHLI": "r[{0}]=(r[{1}]<<{2})&M", "SHRI": "r[{0}]=r[{1}]>>{2}",
          "LDI": "r[{0}]={1}", "LD": "r[{0}]=m[r[{1}]]", "ST": "m[r[{0}]]=r[{1}]",
          "RAND": "r[{0}]=E.rand", "COMP": "r[{0}]=E.comp(r[{1}])",
          "OUT": "E.out=(r[{0}],r[{1}])", "KERNEL": "E.kern(r)",
          "HALT": "E.halt={0}",
        }.get(op)
        if line:
          src.append("  " + line.format(*a))
        if op in cmp:
          nxt = "%d if r[%d]%sr[%d] else %d" % (self.block_of[a[2]], a[0], cmp[op],
                              a[1], bi + 1)
        elif op == "JMP":
          nxt = str(self.block_of[a[0]])
        elif op == "HALT":
          nxt = "-1"
      src.append("  return " + (nxt or str(bi + 1)))
      body = src[top:]
      if "E.kern" not in "".join(body):   # registers in locals inside a block (speed only)
        rx = re.compile(r"r\[(\d+)\]")
        used = sorted({int(x) for x in rx.findall("".join(body))})
        w = sorted({int(x) for x in re.findall(r"^  r\[(\d+)\]=", "\n".join(body), re.M)})
        src[top:] = (["  x%d=r[%d]" % (i, i) for i in used] + [rx.sub(r"x\1", x) for x in body[:-1]]
               + ["  r[%d]=x%d" % (i, i) for i in w] + [rx.sub(r"x\1", body[-1])])
      src.append(" fs.append(f)")
      self.costs.append(dict(cost))
    src.append(" return fs")
    scope = {}
    exec(compile("\n".join(src), "<machine>", "exec"), scope)
    self.make = scope["make"]
    self.prog = prog
    self.kernel_block = self.block_of[next(i for i, c in enumerate(code) if c[0] == "KERNEL")]
    self.cut_block = self.block_of[prog["labels"]["CUTR"]]
    self.stage2_block = self.block_of[prog["labels"]["S2"]]

  def run(self, kern, comp, rand, stop_after=None):
    env = type("Env", (), {})()
    env.kern, env.comp, env.rand, env.out, env.halt = kern, comp, rand, None, None
    fs = self.make(env, M256)
    r, m = [0] * self.prog["nregs"], [0] * self.prog["nmem"]
    counts = [0] * len(fs)
    b, kb = 0, self.kernel_block
    while b >= 0:
      if b == kb and stop_after is not None and counts[kb] >= stop_after:
        break
      counts[b] += 1
      b = fs[b](r, m)
    ops = defaultdict(int)
    for c, cost in zip(counts, self.costs):
      for reg, v in cost.items():
        ops[reg] += c * v
    R = self.prog["regs"]
    return dict(reason=env.halt, pair=env.out, batches=counts[kb],
          cuts=counts[self.cut_block], stage2=counts[self.stage2_block],
          insertions=r[R["CNT"]], starts=r[R["NID"]], ops=dict(ops), r=r)


def lanewise(fn):
  """Test kernel: apply fn independently to each of the 256 lanes."""
  def kern(r):
    planes = r[:256]
    outs = []
    for lane in range(256):
      u = 0
      for j in range(256):
        u |= ((planes[j] >> lane) & 1) << j
      outs.append(fn(u))
    r[:256] = [sum(((outs[l] >> j) & 1) << l for l in range(256)) for j in range(256)]
  return kern


def agree(run, pair, s):
  keys = ("reason", "insertions", "cuts", "stage2")
  ok = all(run[k] == s[k] for k in keys) and run["pair"] == pair
  ok = ok and run["starts"] == s["allocated_starts"]
  ok = ok and run["batches"] * 256 == s["search_evaluations"]
  ok = ok and run["ops"].get("compressions", 0) == s["recovery_evaluations"] + s["final_evaluations"]
  if not ok:
    raise AssertionError("machine and reference disagree: %r %r %r" % (run, pair, s))


def fixtures(klen, kregs):
  base = dict(w=12, d=3, k=4, U=8, R=4, B=4, IDL=2048, E2MAX=1000)
  rho = 256
  cases = [  # (overrides, parameter changes, expected reason)
    ({256: 8, 257: 8}, {}, 1),
    ({256: 8, 257: 8 | 2048}, {}, 2),
    ({256: 257, 257: 8}, {}, 3),
    ({256: 8}, dict(U=0), 4),
    ({256: 3, 3: 16}, dict(R=2, B=3), 6),
    ({}, dict(R=1, B=5), 6),
    ({256: 8, 257: 16 | 128}, dict(U=1), 4),   # second endpoint has a different key
    ({}, dict(R=1, B=2, IDL=300), 5),
    ({256: 8, 300: 8}, {}, 1),
    ({256: 5, 5: 7, 7: 8, 257: 9, 9: 8}, {}, 1),
    ({256: 8}, dict(E2MAX=0), 9),                # stage-1 hit budget exhausted
    ({256: 8, 300: 8}, dict(E2MAX=1), 1),        # one stage-2 batch allowed
    ({256: 88, 257: 88}, dict(win=16), 1),
    ({256: 88, 257: 88 | 2048}, dict(win=16), 2),
    ({256: 8, 257: 136}, dict(win=16, U=1), 4),   # 136 = 8 | 128: a different key, capacity 1
    ({256: 88, 300: 88}, dict(win=16, E2MAX=1), 1),
  ]
  for over, change, want in cases:
    p = dict(base, **change)
    fn = lambda u, o=over: o.get(u, u | 1)
    mach = Machine(load(p, kregs, STUB)[0], klen)
    run = mach.run(lanewise(fn), lambda u, f=fn: f(u) ^ PD, rho)
    pair, s = bounded_search(fn, width=p["w"], dp_bits=p["d"], key_bits=p["k"],
                 lanes=256, batches=p["B"], cap=p["R"], capacity=p["U"],
                 start_limit=p["IDL"], rho=rho, stage2_limit=p["E2MAX"],
                 win=p.get("win", 11))
    agree(run, pair, s)
    assert run["reason"] == want, (over, run["reason"])
  return len(cases)


STUB = [("XOR", 0, 0, 0)]   # kernel block of the fixture/probe images (see the note in fixtures)
BMUL = 1048069                                  # B = BMUL * 2^100; E2MAX = 3 Q / 2^32 = 3 BMUL * 2^76
FULL = dict(w=256, d=112, k=47, U=71316, R=10 * 2 ** 112, B=BMUL * 2 ** 100,
      IDL=1 << 17, E2MAX=3 * BMUL * 2 ** 76, win=16)


def formulas(p, klen):
  """Closed-form operation counts of the program text (proof.md, Section L)."""
  d, k, nmem = p["d"], p["k"], -(-p["U"] // 4) + 512
  s1 = min(32, d)
  win_ops = 4 if p.get("win", 11) < 16 else 0     # the window test of stage 2 (3 ops and the OR into D)
  rec_win = 4 if p.get("win", 11) < 16 else 0     # the window test of a recovery step (SHRI, AND, BGE 2)
  rs = {0: 1292, 1: 1294, 2: 1295}
  return dict(batch=klen + s1 + 8, stage2=d - s1 + 5 + win_ops, stage2_miss=d - s1 + 6 + win_ops,
        setup=17 + 2 + 4 * nmem + 5 + 256 * (5 + rs[0]) + 2,
        epscan=1795, key=1 + 4 * k, insert=20, per_entry=13, restart=rs,
        cut_scan=2564, cut_min=256, cut_each=3, rec_fixed=1046, rec_step=8 + COST["COMP"] + rec_win,
        align_step=5 + COST["COMP"], pair_step=10 + 2 * COST["COMP"], found=12 + 4 * COST["COMP"], term=3, min_update=1,
        terminal=13 * p["U"] + 5, match_extra=12)


def probes(klen, kregs):
  """Measure handler costs at the full-width parameters with test functions."""
  f = formulas(FULL, klen)
  L = 2 ** (FULL["d"] + 4)      # distinguished (window 0) with distinct keys (l + 1)
  rho = (1 << 200) + 12345
  mach = Machine(load(FULL, kregs, STUB)[0], klen)
  plain = lambda u: u | 1
  comp = lambda fn: (lambda u: fn(u) ^ PD)
  run = mach.run(lanewise(plain), comp(plain), rho, stop_after=3)
  o = run["ops"]
  assert o["kernel"] == 3 * (klen + 1) and o["loop"] == 3 * (f["batch"] - klen - 1)
  assert o["setup"] + o["restart"] == f["setup"], (o, f["setup"])
  for n in range(4):  # n endpoints in batch one, table counts 0..n-1
    over = {(rho + l) & M256: (l + 1) * L for l in range(n)}
    fn = lambda u, o=over: o.get(u, u | 1)
    o = mach.run(lanewise(fn), comp(fn), rho, stop_after=1)["ops"]
    assert o.get("epscan", 0) == (f["epscan"] if n else 0)
    assert o.get("stage2", 0) == (f["stage2"] if n else 0), (n, o.get("stage2"), f["stage2"])
    assert o.get("key", 0) == n * f["key"]
    assert o.get("table", 0) == n * f["insert"] + f["per_entry"] * n * (n - 1) // 2
    assert o["restart"] - 256 * f["restart"][0] == n * f["restart"][1]
  cutp = dict(FULL, R=1)
  mc = Machine(load(cutp, kregs, STUB)[0], klen)
  run = mc.run(lanewise(plain), comp(plain), rho, stop_after=1)
  o = run["ops"]
  assert run["cuts"] == 256 and o["cut"] == f["cut_scan"] + 256 * f["cut_each"]
  assert o["restart"] == 256 * (f["restart"][0] + f["restart"][2])
  fn = lambda u: L if u == rho else u | 1
  mc = Machine(load(dict(FULL, R=2), kregs, STUB)[0], klen)
  run = mc.run(lanewise(fn), comp(fn), rho, stop_after=2)
  assert run["cuts"] == 255
  assert run["ops"]["cut"] == f["cut_scan"] + f["min_update"] + 255 * f["cut_each"]
  fn = lambda u: L if u == rho else 2 * L if u == (rho + 1) & M256 else u | 1
  mu = Machine(load(dict(FULL, U=1), kregs, STUB)[0], klen)
  run = mu.run(lanewise(fn), comp(fn), rho)
  assert run["reason"] == 4
  assert run["ops"]["table"] == f["insert"] + 13 * 1 + 5
  for l1, l2 in ((1, 1), (2, 3), (3, 1), (4, 4)):
    def chain(start, length, tag):
      low = (11 << FULL["d"]) if FULL.get("win", 11) < 16 else 1
      pts = [start] + [(tag << 120) | (i << (FULL["d"] + 5)) | low for i in range(1, length)]
      return {pts[i]: pts[i + 1] for i in range(length - 1)}, pts[-1]
    o1, end1 = chain(rho & M256, l1, 1)
    o2, end2 = chain((rho + 1) & M256, l2, 2)
    over = {**o1, **o2}
    over[end1] = over[end2] = 5 * L
    fn = lambda u, o=over: o.get(u, u | 1)
    run = mach.run(lanewise(fn), comp(fn), rho)
    o = run["ops"]
    stored, m = (l2 if l2 < l1 else l1), min(l1, l2)
    want = (f["rec_fixed"] + stored * f["rec_step"] + abs(l1 - l2) * f["align_step"]
        + (m - 1) * f["pair_step"] + f["found"])
    assert run["reason"] == 1 and o["term"] == f["term"]
    assert o["compressions"] == stored + abs(l1 - l2) + 2 * m + 2
    assert o["recovery"] == want, (l1, l2, o["recovery"], want)
    assert o["table"] == f["insert"] + f["match_extra"]  # one insertion, match at entry 0
  return f


TARGET = "sha256-r%d-prefix-v1" % ROUNDS
MAIN_ID = "sha256-r%d-bounded-machine-w16-v1" % ROUNDS
CHECK_ID = "sha256-r%d-machine-checks-v1" % ROUNDS
SLICE = {"sha256-r%d-slice-first-collision-w20-v1" % ROUNDS: (20, 5),
     "sha256-r%d-slice-first-collision-w22-v1" % ROUNDS: (22, 6),
     **{"sha256-r%d-slice-first-collision-w22-rep%d-v1" % (ROUNDS, i): (22, 6) for i in (1, 2, 3)}}


def slice_trial(kern, nregs, ones, seed, n, batches):
  """First repeat among 256 lane walks on the n-bit slice g(u) = f(c | u) mod 2^n (proof Section H): the
  colliding inputs with code 1, or None with code 2 (start hit) or 3 (no event)."""
  mask = (1 << n) - 1
  c = int.from_bytes(hashlib.sha256(b"slice" + seed).digest(), "little") & (M256 ^ mask)
  first = int.from_bytes(hashlib.sha256(b"start" + seed).digest(), "little") & mask
  inputs = [(first + l) & mask for l in range(256)]
  starts, seen = set(inputs), {}
  high = [M256 if (c >> j) & 1 else 0 for j in range(n, 256)]
  zeros = [0] * (nregs - 256)
  fmt = f"0{n}b"
  for _ in range(batches):
    in_bits = [format(u, fmt) for u in reversed(inputs)]
    r = [int("".join(col), 2) for col in reversed(list(zip(*in_bits)))] + high + zeros
    r[ones] = M256
    kern(r)
    bits = [f"{r[j]:0256b}"[::-1] for j in range(n - 1, -1, -1)]
    outs = [int("".join(col), 2) for col in zip(*bits)]
    for x, y in zip(inputs, outs):
      if y in seen:
        return (c | seen[y], c | x), 1
      if y in starts:
        return None, 2
      seen[y] = x
    inputs = outs
  return None, 3


def slice_main(request):
  n, batches = SLICE[request["experiment_id"]]
  event = dict(kind="digest-xor-mask", mask_hex=digest_mask(n), expected_hex=bytes(32).hex())
  if request["event"] != event or request["max_message_bytes"] < 64:
    raise ValueError("Unexpected organizer request")
  listing, kregs, pd = build_listing()
  assert pd == PD and len(listing) == KLEN and kregs == KREGS
  prog, image = load(FULL, kregs, listing)
  kern = compile_kernel(decode(image)[1])  # the decoded image's kernel
  rows = []
  for i, t in enumerate(request["trials"]):
    seed = bytes.fromhex(t["seed"])
    pair, code = slice_trial(kern, prog["nregs"], prog["ones"], seed, n, batches)
    if pair and i < 8:  # spot-check returned pairs against scalar SHA-256
      assert (walk_int(pair[0]) ^ walk_int(pair[1])) & ((1 << n) - 1) == 0
      assert (state_words(pair[0])[7] ^ state_words(pair[1])[7]) & ((1 << n) - 1) == 0
    rows.append(dict(trial=t["trial"],
             message_a_hex=message(pair[0]).hex() if pair else None,
             message_b_hex=message(pair[1]).hex() if pair else None,
             observations=dict(outcome=code)))
  json.dump(dict(schema_version=1, trials=rows), sys.stdout,
       sort_keys=True, separators=(",", ":"))


def checks_main(request):
  """Experiment CHECK_ID: every static and closed-form check (no search, no pairs)."""
  listing, kregs, pd = build_listing()
  klen = len(listing)
  assert pd == PD and klen == KLEN and kregs == KREGS
  checks = [0, (1 << 256) - 1] + [(0xA5A5A5A5 << (32 * j)) for j in range(8)]
  checks += [int.from_bytes(hashlib.sha256(b"enc" + bytes([i])).digest(), "big") for i in range(64)]
  tp = tail_program()
  for u in checks:
    S = state_words(u)
    O = tail_map(S)
    assert state_words(u, 64) == state_words_canonical(u), u
    assert O == tail_words(u) and tail_inverse(O) == S, u
    assert run_tail_program(tp, sum(w << (32 * j) for j, w in enumerate(S))) == walk_int(u), u
    assert len(message(u)) == 52
  assert walk_table(checks) == [walk_int(u) for u in checks]
  full, image = load(FULL, kregs, listing)
  assert full["nregs"] == KREGS + 50 <= NREG - TAIL_REGS   # kernel, control and the B scratch fit the file
  nrules = check_rules()
  nfix = fixtures(klen, kregs)
  f = probes(klen, kregs)
  text = repr(listing).encode()
  extra = [
    dict(kernel_ops=klen, kernel_registers=kregs, fixtures_passed=nfix + nrules, encoding_checks=len(checks),
       control_registers=full["nregs"] - kregs, control_instructions=len(full["code"]) - 1,
       code_bytes=code_bytes(full, klen), data_words=full["nmem"], tail_ops=TAIL_OPS,
       tail_regs=TAIL_REGS, tail_code_bytes=TAIL_CODE),
    dict(batch_ops=f["batch"], stage2_ops=f["stage2"], setup_ops=f["setup"], epscan_ops=f["epscan"],
       key_ops=f["key"], insert_ops=f["insert"], per_entry_ops=f["per_entry"], restart_ops=f["restart"][2]),
    dict(cut_scan_ops=f["cut_scan"], cut_each_ops=f["cut_each"], rec_fixed_ops=f["rec_fixed"],
       rec_step_ops=f["rec_step"], align_step_ops=f["align_step"], pair_step_ops=f["pair_step"],
       found_ops=f["found"]),
    dict(kernel_listing_sha256=int.from_bytes(hashlib.sha256(text).digest(), "big"), output_polarity=pd,
       code_bytes_36=code_bytes(full, klen, 36), cut_min_updates=f["cut_min"], term_ops=f["term"],
       image_bytes=len(image), image_sha256=int.from_bytes(hashlib.sha256(image).digest(), "big")),
  ]
  rows = [dict(trial=t["trial"], message_a_hex=None, message_b_hex=None,
         observations=extra[t["trial"]] if t["trial"] < len(extra) else dict(checked=1))
      for t in request["trials"]]
  json.dump(dict(schema_version=1, trials=rows), sys.stdout, sort_keys=True, separators=(",", ":"))


def main():
  request = json.load(sys.stdin)
  if (request["schema_version"] == 1 and request["experiment_id"] in SLICE
      and request["target_profile"] == TARGET):
    return slice_main(request)
  if request["schema_version"] == 1 and request["experiment_id"] == CHECK_ID and request["target_profile"] == TARGET:
    return checks_main(request)
  event = dict(kind="digest-xor-mask", mask_hex=digest_mask(16), expected_hex=bytes(32).hex())
  if (request["schema_version"] != 1 or request["experiment_id"] != MAIN_ID
      or request["target_profile"] != TARGET
      or request["event"] != event or request["max_message_bytes"] < 64):
    raise ValueError("Unexpected organizer request")
  listing, kregs, pd = build_listing()
  klen = len(listing)
  assert pd == PD and klen == KLEN and kregs == KREGS
  full, image = load(FULL, kregs, listing)
  kern = compile_kernel(decode(image)[1])  # execute the decoded image's kernel
  p = dict(w=16, d=3, k=9, U=256, R=3, B=48, IDL=4096, E2MAX=4608, win=16)
  wm = (1 << 16) - 1
  table = walk_table(range(1 << 16))
  for u in range(0, 1 << 16, 4099):
    assert table[u] == walk_int(u), u
  mach = Machine(load(p, kregs, STUB)[0], klen)
  checked = [0]

  def checked_kernel(r):
    sel = ((checked[0] * 37) % 256, (checked[0] * 101 + 7) % 256, 0, 255)
    ins = [sum(((r[j] >> l) & 1) << j for j in range(256)) for l in sel]
    kern(r)
    for l, u in zip(sel, ins):
      if sum(((r[j] >> l) & 1) << j for j in range(256)) != table[u] ^ PD:
        raise AssertionError("kernel lane mismatch")
    checked[0] += 1

  rows = []
  for t in request["trials"]:
    seed = bytes.fromhex(t["seed"])
    rho = int.from_bytes(hashlib.sha256(seed).digest(), "little") & wm
    before = checked[0]
    run = mach.run(checked_kernel, lambda u: table[u], rho)
    step = lambda u: (table[u] ^ PD) & wm
    pair, s = bounded_search(step, width=16, dp_bits=3, key_bits=9, lanes=256,
                 batches=p["B"], cap=p["R"], capacity=p["U"],
                 start_limit=p["IDL"], rho=rho, stage2_limit=p["E2MAX"],
                 win=p["win"])
    agree(run, pair, s)
    r = [int.from_bytes(hashlib.sha256(seed + bytes([j])).digest(), "little")
       for j in range(256)] + [0] * (full["nregs"] - 256)
    r[full["ones"]] = M256
    lanes = tuple(seed[:8])  # eight seed-chosen lanes
    ins = [sum(((r[j] >> l) & 1) << j for j in range(256)) for l in lanes]
    kern(r)
    for l, w in zip(lanes, walk_table(ins)):
      if sum(((r[j] >> l) & 1) << j for j in range(256)) != w ^ PD:
        raise AssertionError("full-width kernel lane mismatch")
    o = run["ops"]
    rows.append(dict(trial=t["trial"],
             message_a_hex=message(pair[0]).hex() if pair else None,
             message_b_hex=message(pair[1]).hex() if pair else None,
             observations=dict(reason=run["reason"], batches=run["batches"],
                      insertions=run["insertions"], cuts=run["cuts"], stage2=run["stage2"],
                      starts=run["starts"], compressions=o.get("compressions", 0),
                      kernel_lanes_checked=4 * (checked[0] - before) + len(lanes))))
  json.dump(dict(schema_version=1, trials=rows), sys.stdout, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
  main()
