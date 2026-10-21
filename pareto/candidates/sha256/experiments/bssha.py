"""Birthday collision search on 62-step ..."""
import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, log, log2, log1p, exp, comb

M32 = 0xFFFFFFFF
ROUNDS = 62
UNIT = 4744
LANES, ALL = 256, (1 << 256) - 1
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
K = (0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
     0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
     0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
     0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
     0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
     0x90befffa, 0xa4506ceb)
PAD2 = bytes([128]) + bytes(55) + (512).to_bytes(8, "big")

# ---- 1 scalar digest
def _ror(v, k):
	return ((v >> k) | (v << (32 - k))) & M32

def state_words(w, prefix=None):
	"""The working state a..h after ROUNDS ..."""
	ws = _build_ws(w, prefix)
	for i in range(16, ROUNDS):
		x, y = ws[i - 15], ws[i - 2]
		ws.append((ws[i - 16] + (_ror(x, 7) ^ _ror(x, 18) ^ (x >> 3)) + ws[i - 7] + (_ror(y, 17) ^ _ror(y, 19) ^ (y >> 10))) & M32)
	a, b, c, d, e, f, g, h = IV
	for i in range(ROUNDS):
		t1 = (h + (_ror(e, 6) ^ _ror(e, 11) ^ _ror(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + ws[i]) & M32
		t2 = ((_ror(a, 2) ^ _ror(a, 13) ^ _ror(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) & M32
		a, b, c, d, e, f, g, h = (t1 + t2) & M32, a, b, c, (d + t1) & M32, e, f, g
	return [a, b, c, d, e, f, g, h]

def words_of(x):
	return [(x >> (32 * (7 - i))) & M32 for i in range(8)]

def int_of(w):
	return sum(w[i] << (32 * (7 - i)) for i in range(8))

def _SIG0(a):
	return _ror(a, 2) ^ _ror(a, 13) ^ _ror(a, 22)

def _SIG1(e):
	return _ror(e, 6) ^ _ror(e, 11) ^ _ror(e, 25)

def _CH(e, f, g):
	return (e & f) ^ (~e & g)

def _MAJ(a, b, c):
	return (a & b) ^ (a & c) ^ (b & c)

# ---- layout (F01 = c, F01b = e) and tail (TAILB = walk B)
def _anchor_prefix(anchors):
	"""Prefix words W0.. that set a_1.. = ..."""
	a, b, c, d, e, f, g, h = IV
	pw = []
	for i, av in enumerate(anchors):
		t2 = (_SIG0(a) + _MAJ(a, b, c)) & M32
		t1 = (av - t2) & M32
		pw.append((t1 - h - _SIG1(e) - _CH(e, f, g) - K[i]) & M32)
		a, b, c, d, e, f, g, h = av, a, b, c, (d + t1) & M32, e, f, g
	return pw

TAILB = 1
CIN = 1
NTAIL = 6 if TAILB else 4
PERM = (6,1,7,0,5,4,2,3,)
PRE, VARBASE, TAILMAP, OFFSET = 8, 8, {}, set(range(10, 16))
PREFIX_WORDS = tuple(_anchor_prefix([(K[9] - K[8]) & M32, (-K[9]) & M32, 0, 0, 0, 0, 0, 0]))

def _build_ws(w, prefix=None):
	"""The 16 message words from the 8 walk ..."""
	prefix = PREFIX_WORDS if prefix is None else prefix
	ws = [0] * 16
	for i in range(PRE):
		ws[i] = prefix[i]
	for k in range(8):
		ws[VARBASE + k] = (w[k] - (K[VARBASE + k] if VARBASE + k in OFFSET else 0)) & M32
	for pos, v in TAILMAP.items():
		ws[pos] = v
	return ws

def _trace(w, prefix=None):
	ws = _build_ws(w, prefix)
	for i in range(16, ROUNDS):
		x, y = ws[i - 15], ws[i - 2]
		ws.append((ws[i - 16] + (_ror(x, 7) ^ _ror(x, 18) ^ (x >> 3)) + ws[i - 7] + (_ror(y, 17) ^ _ror(y, 19) ^ (y >> 10))) & M32)
	a, b, c, d, e, f, g, h = IV
	A, E, T = {0: a, -1: b, -2: c, -3: d}, {0: e, -1: f, -2: g, -3: h}, {}
	for i in range(ROUNDS):
		t1 = (h + _SIG1(e) + _CH(e, f, g) + K[i] + ws[i]) & M32
		t2 = (_SIG0(a) + _MAJ(a, b, c)) & M32
		a, b, c, d, e, f, g, h = (t1 + t2) & M32, a, b, c, (d + t1) & M32, e, f, g
		A[i + 1], E[i + 1], T[i + 1] = a, e, t1
	return ws, A, E, T

def enc_words(w, prefix=None):
	"""k=4: a_{r-4..r-7}, T1_{r-3..r}.  ..."""
	ws, A, E, T = _trace(w, prefix)
	r = ROUNDS
	if TAILB:
		bw = [E[r - 3], E[r - 2], A[r - 7], A[r - 6], (T[r - 5] + _MAJ(A[r - 6], A[r - 7], A[r - 8])) & M32, T[r - 4],
              (E[r - 5] + ((~E[r - 2]) & E[r - 4]) + ws[r - 2]) & M32, (E[r - 4] + ws[r - 1]) & M32]
		return [bw[PERM[k]] for k in range(8)]

def enc_invert(enc):
	"""The explicit inverse of enc_words ..."""
	r = ROUNDS
	if TAILB:
		bw = [0] * 8
		for k in range(8):
			bw[PERM[k]] = enc[k]
		e3, e2, a7, a6, Q, T4, X, Y = bw
		a5 = (Q + _SIG0(a6)) & M32
		a4 = (T4 + _SIG0(a5) + _MAJ(a5, a6, a7)) & M32
		a3 = (e3 - a7 + _SIG0(a4) + _MAJ(a4, a5, a6)) & M32
		a2 = (e2 - a6 + _SIG0(a3) + _MAJ(a3, a4, a5)) & M32
		t1 = (X + (e2 & e3) + _SIG1(e2) + K[r - 2]) & M32
		e1 = (a5 + t1) & M32
		a1 = (t1 + _SIG0(a2) + _MAJ(a2, a3, a4)) & M32
		t0 = (Y + _SIG1(e1) + _CH(e1, e2, e3) + K[r - 1]) & M32
		return [(t0 + _SIG0(a1) + _MAJ(a1, a2, a3)) & M32, a1, a2, a3, (a4 + t0) & M32, e1, e2, e3]

def f_scalar(x, n=256):
	"""The new map: the k=4 W-free encoding ..."""
	return int_of(enc_words(words_of(x))) & ((1 << n) - 1)

PAD2W = tuple(int.from_bytes(PAD2[4 * i:4 * i + 4], "big") for i in range(16))

def _kw2():
	ws = list(PAD2W)
	for i in range(16, ROUNDS):
		x, y = ws[i - 15], ws[i - 2]
		ws.append((ws[i - 16] + (_ror(x, 7) ^ _ror(x, 18) ^ (x >> 3)) + ws[i - 7] + (_ror(y, 17) ^ _ror(y, 19) ^ (y >> 10))) & M32)
	return tuple((K[i] + ws[i]) & M32 for i in range(ROUNDS))

_KW2 = _kw2()

def digest_of_state(s):
	"""The complete digest (256-bit integer) ..."""
	cv = [(u + v) & M32 for u, v in zip(IV, s)]
	a, b, c, d, e, f, g, h = cv
	for kw in _KW2:
		t1 = (h + (((e >> 6) | (e << 26)) ^ ((e >> 11) | (e << 21)) ^ ((e >> 25) | (e << 7))) + ((e & f) ^ (~e & g)) + kw) & M32
		t2 = (((a >> 2) | (a << 30)) ^ ((a >> 13) | (a << 19)) ^ ((a >> 22) | (a << 10))) + ((a & b) ^ (a & c) ^ (b & c))
		a, b, c, d, e, f, g, h = (t1 + t2) & M32, a, b, c, (d + t1) & M32, e, f, g
	return int_of([(u + v) & M32 for u, v in zip(cv, [a, b, c, d, e, f, g, h])])

def digest_of_g(o, qint):
	"""The complete digest from a program ..."""
	return digest_of_state(enc_invert(words_of(o ^ qint)))

def message(x):
	"""The 64-byte message of chain value x ..."""
	return b"".join(v.to_bytes(4, "big") for v in _build_ws(words_of(x)))

# ---- 2 the recovery program (two trails in one 256-bit word, rolled)
RP, RMASK = 128, M32 | (M32 << 128)
WM, KM = 0, ROUNDS

def _rep(v):
	return v | (v << RP)

def _state5():
	"""Working state after step 4 (W0..W4 ..."""
	a, b, c, d, e, f, g, h = IV
	for i in range(PRE):
		t1 = (h + (_ror(e, 6) ^ _ror(e, 11) ^ _ror(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + PREFIX_WORDS[i]) & M32
		t2 = ((_ror(a, 2) ^ _ror(a, 13) ^ _ror(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) & M32
		a, b, c, d, e, f, g, h = (t1 + t2) & M32, a, b, c, (d + t1) & M32, e, f, g
	return [a, b, c, d, e, f, g, h], b ^ c

class RecProg:
	"""init: records executed once per ..."""

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
		constpos = {i: PREFIX_WORDS[i] for i in range(PRE)}
		constpos.update(TAILMAP)
		for i in sorted(constpos):
			S(self.init, T0, _rep(constpos[i]))
			self.init.append(("T", WM + i, T0, 2))

		def sigma(out, dst, src, rs, shr):
			"""dst = (rotations of src by rs, or two ..."""
			out += [("<", T0, src, 32), ("|", T0, src, T0), (">", dst, T0, rs[0]), (">", T1, T0, rs[1]), ("^", dst, dst, T1)]
			out += [(">", T1, src, shr) if shr else (">", T1, T0, rs[2]), ("^", dst, dst, T1), ("&", dst, dst, MASK)]

		def rnd(out, st, pi, addrw, ptr):
			a, b, c, d, e, f, g, h = st
			P, PN = PB[pi], PB[1 - pi]
			sigma(out, T2, e, (6, 11, 25), 0)
			out += [("^", T3, f, g), ("&", T3, e, T3), ("^", T3, g, T3)] # Ch
			out += [("L", T4, addrw, ptr), ("L", T0, addrw + KM, ptr), ("+", T4, T4, T0)] # W' = W + K
			out += [("+", T2, h, T2), ("+", T2, T2, T3), ("+", T2, T2, T4)]
			sigma(out, T3, a, (2, 13, 22), 0)
			out += [("^", PN, a, b), ("&", T0, PN, P), ("^", T0, T0, b), ("+", T3, T3, T0)]
			out += [("+", h, d, T2), ("&", h, h, MASK), ("+", d, T2, T3), ("&", d, d, MASK)]
			return [d, a, b, c, h, e, f, g], 1 - pi
		assert WM == 0
		pre = (n - NTAIL - PRE) % 4
		st, pi = list(ST), 0
		straight = []
		for j in range(pre):
			st, pi = rnd(straight, st, pi, WM + PRE + j, 2)
		body, stl, pil = [], list(st), pi
		for j in range(4):
			stl, pil = rnd(body, stl, pil, j, 0)
		assert stl == st and pil == pi, "the round loop does not rename back"
		ra, rb, rc, rd, re, rf, rg, rh = st

		def t1(out, dst, hr, er, fr, gr, wi, mask=True):
			"""dst = T1 = h + Sigma1(e) + Ch(e,f,g) ..."""
			sigma(out, T2, er, (6, 11, 25), 0)
			out += [("^", T3, fr, gr), ("&", T3, er, T3), ("^", T3, gr, T3)]
			out += [("L", T4, WM + wi, 2), ("L", T0, KM + wi, 2), ("+", T4, T4, T0)]
			out += [("+", T2, hr, T2), ("+", T2, T2, T3), ("+", T2, T2, T4)]
			if mask:
				out.append(("&", dst, T2, MASK))
		tail = []
		if TAILB:
			R5, QQ, E5, R4, E4, E3, E2, XX, YY = range(16, 25)
			t1(tail, R5, rh, re, rf, rg, n - 6) # T1_{r-5}
			tail += [("+", E5, rd, R5), ("&", E5, E5, MASK)] # e_{r-5}
			t1(tail, R4, rg, E5, re, rf, n - 5) # T1_{r-4} (output)
			tail += [("+", E4, rc, R4), ("&", E4, E4, MASK)] # e_{r-4}
			t1(tail, T2, rf, E4, E5, re, n - 4, False) # T1_{r-3} in T2
			tail += [("+", E3, rb, T2), ("&", E3, E3, MASK)] # e_{r-3}
			t1(tail, T2, re, E3, E4, E5, n - 3, False) # T1_{r-2} in T2
			tail += [("+", E2, ra, T2), ("&", E2, E2, MASK)] # e_{r-2}
			tail += [("&", T3, E2, E4), ("^", T3, T3, E4), ("L", T4, WM + n - 2, 2), ("+", XX, E5, T3), ("+", XX, XX, T4), ("&", XX, XX, MASK)] # X (shear)
			tail += [("L", T4, WM + n - 1, 2), ("+", YY, E4, T4), ("&", YY, YY, MASK)] # Y
			tail += [("^", T0, ra, rb), ("&", T0, T0, PB[pi]), ("^", T0, T0, rb), ("+", QQ, R5, T0), ("&", QQ, QQ, MASK)] # Q
			fb = [E3, E2, rb, ra, QQ, R4, XX, YY]
			self.fin = [fb[PERM[k]] for k in range(8)]
		head = []
		for k in range(8):
			if VARBASE + k in OFFSET:
				S(head, T0, _rep((-K[VARBASE + k]) & M32))
				head += [("+", self.fin[k], self.fin[k], T0), ("&", self.fin[k], self.fin[k], MASK)]
			head.append(("T", WM + VARBASE + k, self.fin[k], 2))
		state, pab = _state5()
		for k in range(8):
			S(head, ST[k], _rep(state[k]))
		S(head, PB[0], _rep(pab))
		A_, B_, C_, D_, E0, E1 = 19, 20, 21, 22, 23, 24
		sched = [("L", A_, 0, 0), ("L", B_, 1, 0), ("L", C_, 9, 0), ("L", D_, 14, 0)]
		sigma(sched, E0, B_, (7, 18, 0), 3)
		sigma(sched, E1, D_, (17, 19, 0), 10)
		sched += [("+", A_, A_, E0), ("+", A_, A_, C_), ("+", A_, A_, E1), ("&", A_, A_, MASK), ("T", 16, A_, 0)]
		self.blocks = [("S", head), ("L", sched, 0, n - 16, 1), ("S", straight), ("L", body, PRE + pre, n - NTAIL - PRE - pre, 4), ("S", tail)]
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
		"""The working state words after ROUNDS ..."""
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
	"""The chain map g = f XOR q on up to ..."""
	q = sum(qw[i] << (32 * i) for i in range(8)) if qw else 0
	return [(v ^ q) & ((1 << n) - 1) for v in rec().f(xs)]

def packed_ops(qw=None):
	"""Records executed by one call of the ..."""
	return rec().ops

# ---- 3 bit-sliced generator
ZERO, ONE = (0, 0), (0, 1)

class Gen:

	def __init__(self, n):
		self.n, self.nodes, self.calls = n, [("c",)], 0
		self.inputs, self.cse = [], {}
		for j in range(n):
			self.nodes.append(("v", j))
			self.inputs.append((len(self.nodes) - 1, 0))

	def mk(self, op, a, b):
		self.calls += 1
		if a > b:
			a, b = b, a
		k = self.cse.get((op, a, b))
		if k is None:
			self.nodes.append((op, a, b))
			k = self.cse[(op, a, b)] = len(self.nodes) - 1
		return k

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
			return (self.mk("o", x[0], y[0]), 1) # !a & !b = !(a | b)
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
			xx = x if x[1] == t[1] else y
			cr = self.AND((xx[0], xx[1] ^ 1), (t[0], t[1] ^ 1))
			return s, (cr[0], cr[1] ^ 1)
		if len(vs) == 1:
			x = vs[0]
			k1, k2 = cs[0][1], cs[1][1]
			return (x[0], x[1] ^ k), (ONE if k1 == k2 == 1 else ZERO if k1 == k2 == 0 else x)
		kk = cs[0][1] + cs[1][1] + cs[2][1]
		return (ZERO if kk % 2 == 0 else ONE), (ONE if kk >= 2 else ZERO)

	def add(self, A, B, cin=ZERO):
		"""Ripple add of two 32-plane words ..."""
		s, c = [], cin
		for i in range(32):
			if i == 31:
				s.append(self.XOR(self.XOR(A[i], B[i]), c))
			else:
				si, c = self.fa(A[i], B[i], c)
				s.append(si)
		return s

	def OR(self, x, y):
		r = self.AND((x[0], x[1] ^ 1), (y[0], y[1] ^ 1))
		return (r[0], r[1] ^ 1)

	def _col(self, x, y, z, u, U, tm, oU):
		if tm == 2:
			g, (o0, o1, o2) = SYN[(int(oU), x[1] | y[1] << 1 | z[1] << 2 | u[1] << 3 | U[1] << 4)]
			v = [(x[0], 0), (y[0], 0), (z[0], 0), (u[0], 0), (U[0], 0)]
			for t, j, l in g:
				v.append((self.XOR, self.AND, self.OR)["xao".index(t)](v[j], v[l]))
			return (v[o0[0]][0], o0[1]), (None if oU else (v[o2[0]][0], o2[1])), (v[o1[0]][0], o1[1])
		"""Pair-carry column, template tm: x + y + z + v(u, U) = s + 2 v(u', U'), v(u, U) = U ? 1 : 2u; returns (s, u', U'), u' not built when oU."""
		X, A, O = self.XOR, self.AND, self.OR
		if tm:
			w = X(y, U); n8 = X(z, w); s = X(x, n8); n6 = O(U, X(y, u))
			return s, (None if oU else X(n6, w)), X(n6, A(n8, X(x, w)))
		n5 = X(z, U); n9 = X(x, n5); s = X(y, n9); n6 = X(x, y); n8 = O(U, X(z, u)); n11 = A((n6[0], n6[1] ^ 1), n9)
		return s, (None if oU else X(n5, n11)), X(n8, n11)

	def add3(self, A, B, C):
		"""A + B + C mod 2^32: bit 0 a full ..."""
		s = [None] * 32
		s[0], U = self.fa(A[0], B[0], C[0])
		u = ZERO
		for i in range(1, 31):
			a, b, c, best = A[i], B[i], C[i], None
			for o in ((a, b, c), (a, c, b), (b, a, c), (b, c, a), (c, a, b), (c, b, a)):
				for tm in (0, 1):
					n0 = len(self.nodes)
					self._col(*o, u, U, tm, i == 30)
					k = len(self.nodes) - n0
					for nd in self.nodes[n0:]:
						del self.cse[nd]
					del self.nodes[n0:]
					if best is None or k < best[0]:
						best = (k, o, tm)
			if (int(i == 30), a[1] | b[1] << 1 | c[1] << 2 | u[1] << 3 | U[1] << 4) in SYN:
				n0 = len(self.nodes)
				self._col(a, b, c, u, U, 2, i == 30)
				k = len(self.nodes) - n0
				for nd in self.nodes[n0:]:
					del self.cse[nd]
				del self.nodes[n0:]
				if k < best[0]:
					best = (k, (a, b, c), 2)
			s[i], u, U = self._col(*best[1], u, U, best[2], i == 30)
		s[31] = self.XOR(self.XOR(self.XOR(A[31], B[31]), C[31]), U)
		return s

	def addm(self, *ws):
		"""Sum of words mod 2^32: the fully ..."""
		cv, vs = 0, []
		for w in ws:
			if all(x[0] == 0 for x in w):
				cv += sum(x[1] << i for i, x in enumerate(w))
			else:
				vs.append(w)
		cv &= M32
		if not vs:
			return _constw(cv)
		if len(vs) > 2:
			vs = [self.add3(*vs[:3])] + vs[3:]
		bb = max(range(len(vs)), key=lambda k: (_tz((cv - k) & M32), -k)) if CIN and cv else 0
		s = vs[0]
		for k, w in enumerate(vs[1:]):
			s = self.add(s, w, ONE if k < bb else ZERO)
		cv = (cv - bb) & M32
		return self.add(s, _constw(cv)) if cv else s

	def xorw(self, A, B):
		return [self.XOR(a, b) for a, b in zip(A, B)]

SYN = {(0, 7): ((('x', 1, 2), ('x', 0, 5), ('x', 0, 2), ('x', 3, 6), ('o', 4, 8), ('o', 5, 7), ('x', 9, 10), ('x', 6, 10), ('x', 4, 6)), ((13, 1), (11, 1), (12, 1))), (0, 8): ((('x', 1, 2), ('x', 0, 5), ('x', 3, 6), ('o', 4, 7), ('x', 1, 6), ('x', 4, 6), ('x', 6, 8), ('o', 5, 9), ('x', 8, 12)), ((10, 0), (13, 1), (11, 1))), (0, 16): ((('x', 2, 4), ('x', 0, 5), ('x', 3, 5), ('x', 1, 6), ('x', 5, 8), ('a', 4, 7), ('x', 5, 10), ('o', 6, 9), ('x', 10, 12)), ((8, 1), (13, 0), (11, 0))), (0, 31): ((('x', 2, 4), ('x', 3, 5), ('a', 4, 6), ('x', 5, 7), ('x', 0, 5), ('x', 1, 5), ('o', 9, 10), ('x', 7, 11), ('x', 0, 10)), ((13, 0), (12, 0), (8, 1))), (1, 7): ((('x', 0, 2), ('x', 4, 5), ('x', 0, 1), ('x', 1, 6), ('x', 3, 8), ('o', 5, 7), ('o', 4, 9), ('x', 10, 11)), ((8, 1), (12, 1), None)), (1, 8): ((('x', 0, 2), ('x', 4, 5), ('x', 0, 1), ('x', 1, 6), ('x', 3, 8), ('o', 5, 7), ('o', 4, 9), ('x', 10, 11)), ((8, 0), (12, 1), None)), (1, 16): ((('x', 0, 4), ('x', 1, 5), ('x', 3, 5), ('x', 1, 2), ('a', 4, 7), ('o', 6, 8), ('x', 9, 10), ('x', 2, 6)), ((12, 1), (11, 0), None)), (1, 31): ((('x', 0, 4), ('x', 1, 5), ('x', 3, 5), ('x', 1, 2), ('a', 4, 7), ('o', 6, 8), ('x', 9, 10), ('x', 2, 6)), ((12, 0), (11, 0), None))}

def _tz(v):
	return 32 if v == 0 else (v & -v).bit_length() - 1

def _constw(v):
	return [ONE if (v >> i) & 1 else ZERO for i in range(32)]

def _sigma(g, A, r1, r2, r3, shift):
	out = []
	for j in range(32):
		t = g.XOR(A[(j + r1) % 32], A[(j + r2) % 32])
		out.append(g.XOR(t, (A[j + r3] if j + r3 < 32 else ZERO) if shift else A[(j + r3) % 32]))
	return out

# ---- 4 the program: one straight network, register allocation, 5-byte body records
def _add_u(g, A, u, B_fix):
	"""A + B from u = A ^ B and B[0] = ..."""
	s, c = [], ZERO
	for i in range(32):
		if i == 0:
			s.append(u[0]); c = g.AND(A[0], B_fix()) if A[0] != ZERO else g.AND(A[0], ZERO)
		elif i == 31:
			s.append(g.XOR(u[31], c))
		else:
			s.append(g.XOR(u[i], c))
			w = g.XOR(A[i], c)
			if u[i][0] and w[0] and u[i][0] != w[0] and u[i][1] != w[1]:
				c = g.XOR(g.AND((u[i][0], u[i][1] ^ 1), w), c)
			else:
				c = g.XOR(g.AND(u[i], w), A[i])
	return s

def _rnd2(g, st, Wd):
	"""One step; hg = h ^ g = f ^ g of the ..."""
	a, b, c, d, e, f, gg, h, prev, hg = st
	S1 = _sigma(g, e, 6, 11, 25, False)
	fg = [g.XOR(f[j], gg[j]) for j in range(32)]
	tt = [g.AND(e[j], fg[j]) for j in range(32)]
	u = [g.XOR(hg[j], tt[j]) for j in range(32)]
	t1 = _add_u(g, h, u, lambda: g.XOR(gg[0], tt[0]))
	t1 = g.addm(t1, S1, *Wd)
	S0 = _sigma(g, a, 2, 13, 22, False)
	ab, mj = [], []
	for j in range(32):
		ab.append(g.XOR(a[j], b[j]))
		if ab[j][0] and prev[j][0] and ab[j][0] != prev[j][0] and ab[j][1] != prev[j][1]:
			mj.append(g.XOR(g.AND((ab[j][0], ab[j][1] ^ 1), prev[j]), c[j]))
		else:
			mj.append(g.XOR(g.AND(ab[j], prev[j]), b[j]))
	ne = g.add(d, t1)
	na = g.addm(t1, S0, mj)
	return (na, a, b, c, ne, e, f, gg, ab, fg)

def _t1hg(g, e, f, gg, h, hg, Wd, sig=True):
	"""h + [Sigma1(e)] + Ch(e,f,g) + Wd with ..."""
	fg = [g.XOR(f[j], gg[j]) for j in range(32)]
	tt = [g.AND(e[j], fg[j]) for j in range(32)]
	u = [g.XOR(hg[j], tt[j]) for j in range(32)]
	t = _add_u(g, h, u, lambda: g.XOR(gg[0], tt[0]))
	return (g.addm(t, _sigma(g, e, 6, 11, 25, False), *Wd) if sig else g.addm(t, *Wd)), fg

def _net_u():
	"""All 62 steps: W[i] (i >= 16) is built ..."""
	g = Gen(256)
	Y = [[g.inputs[32 * (7 - k) + j] for j in range(32)] for k in range(8)]
	W = [None] * 16
	for i in range(PRE):
		W[i] = _constw(PREFIX_WORDS[i])
	for k in range(8):
		pos = VARBASE + k
		W[pos] = g.addm(Y[k], _constw((-K[pos]) & M32)) if pos in OFFSET else Y[k]
	for pos, val in TAILMAP.items():
		W[pos] = _constw(val)
	wd = lambda i: (Y[i - VARBASE],) if i in OFFSET else (_constw(K[i]), W[i])
	v = [_constw(w) for w in IV]
	st = tuple(v) + ([g.XOR(v[1][j], v[2][j]) for j in range(32)], [g.XOR(v[7][j], v[6][j]) for j in range(32)])
	for i in range(ROUNDS):
		if i >= 16:
			W.append(g.addm(W[i - 16], _sigma(g, W[i - 15], 7, 18, 3, True), W[i - 7], _sigma(g, W[i - 2], 17, 19, 10, True)))
		if i < ROUNDS - NTAIL:
			st = _rnd2(g, st, wd(i))
	r = ROUNDS
	if TAILB:
		a6, a7, a8, a9, e6, e7, e8, e9, prev, hg = st
		T5, fg = _t1hg(g, e6, e7, e8, e9, hg, wd(r - 6))
		e5 = g.add(a9, T5)
		mj = []
		for j in range(32):
			ab = g.XOR(a6[j], a7[j])
			if ab[0] and prev[j][0] and ab[0] != prev[j][0] and ab[1] != prev[j][1]:
				mj.append(g.XOR(g.AND((ab[0], ab[1] ^ 1), prev[j]), a8[j]))
			else:
				mj.append(g.XOR(g.AND(ab, prev[j]), a7[j]))
		Q = g.add(T5, mj)
		T4, fg = _t1hg(g, e5, e6, e7, e8, fg, wd(r - 5))
		e4 = g.add(a8, T4)
		T3, fg = _t1hg(g, e4, e5, e6, e7, fg, wd(r - 4))
		e3 = g.add(a7, T3)
		T2, fg = _t1hg(g, e3, e4, e5, e6, fg, wd(r - 3))
		e2 = g.add(a6, T2)
		X = g.addm(e5, [g.AND((e2[j][0], e2[j][1] ^ 1), e4[j]) for j in range(32)], W[r - 2]) # shear: no e2 & e3
		bw = [e3, e2, a7, a6, Q, T4, X, g.add(e4, W[r - 1])]
		out = [bw[PERM[k]] for k in range(8)]
		return g, [t for w in out for t in w]

def _alloc(g, nin, fixed, outs, tgt, free0, E):
	"""Streaming allocator (the C generator ..."""
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
		E(("M", tgt[i], s, 0))
		st["moves"] += 1
	for i, o in enumerate(outs):
		if o[0] == 0:
			E(("S", tgt[i], 1 if o[1] else 0, 0))
	return st["moves"]

def INREG(j):
	"""Register of plane j: bit j % 32 of ..."""
	return 256 + 32 * (7 - j // 32) + j % 32

def assemble():
	"""(records, moves, generator calls)"""
	R = []
	g, outs = _net_u()
	_QM[:] = [sum(1 << (32 * (7 - i // 32) + i % 32) for i, o in enumerate(outs) if o[0] and o[1])]
	moves = _alloc(g, 256, {j + 1: INREG(j) for j in range(256)}, outs, [256 + i for i in range(256)], range(REGISTERS), R.append)
	return R, moves, 2 * g.calls

class Prog:
	"""The program with its interpreter.  ..."""

	def __init__(self):
		self.recs, self.moves, self.calls = assemble()
		self.q = [0] * 256
		self.qint = _QM[0]
		self.qwords = [(self.qint >> (32 * i)) & M32 for i in range(8)]
		self.pin = [0] * 256
		self.instr = self.kernel = len(self.recs)
		self.nregs = max(max(r[1:3]) if r[0] in "NM" else max(r[1:4]) if r[0] in "^&|" else r[1] for r in self.recs) + 1
		self.compile()

	def run(self, pc, end, regs):
		"""Execute records pc..end-1; returns ..."""
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
		self.ns = ns

		def step(r):
			for c in fs:
				c(r)
		self.fast = step

	def step(self, *planes):
		"""One batch: the low n of the 256 input ..."""
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
	"""Stored input planes (low n) for up to ..."""
	T = transpose(xs)
	return [T[j] ^ (ALL if pin[j] else 0) for j in range(n)]

def lanes_of(planes, n, pin):
	"""All 256 lane values (n bits) from n ..."""
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
P_MIN = 0.390000001
GRAIN = 10 ** 24
STAGE1_PLANES = 32
LOOP_OPS = 3
HIT_OPS = 2800
EVENT_OPS = 3800
CUT_OPS = 4200
SLICE_OPS = 1300 # slice check: 256 ages
RECOVER_EXTRA = 47
INSTR_BYTES = 36
BODY_BYTES = 5
GEN_CODE = 4637
HANDLER_CODE, SETUP_CODE, RECOVERY_CODE = 1000, 160, 63
REGISTERS = 1021
REGFILE = REGISTERS * 32
COUNTERS = 16384
ARRAYS = 64 * ROUNDS
KEYB = 46
SLOTB = KEYB + 1
MEM_LIMIT = 1 << 20
ADVICE = 0
KAPPA_256 = 14
GEN_FUEL = 196136885
GEN_SCRATCH = 108362
SETUP_FIXED = 256 * 3100 + 20000
CFG = {16: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4), 18: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4),
       256: dict(s1=32, W=90, kappa=KAPPA_256, Sb=1 << 48)}

def stage1_ops(pin, s1):
	"""Operations of the stage-1 test (lanes ..."""
	npos = sum(1 for j in range(s1) if not pin[j])
	nneg = s1 - npos
	ops = max(npos - 1, 0) + max(nneg - 1, 0)
	if nneg:
		ops += 2 if npos else 1
	return ops + 1 + 2

def stage1(planes, s1, pin):
	"""Mask of lanes whose s1 low stored ..."""
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
	"""log2 of the Chernoff bound exp(-mean) ..."""
	return (-mean + k * (1 + log(mean / k))) / log(2)

_PROG = []
_QM = [0]

def prog():
	global REGFILE
	if not _PROG:
		_PROG.append(Prog())
		REGFILE = 32 * (_PROG[0].nregs + 3)
	return _PROG[0]

def other_code(pr=None):
	return HANDLER_CODE + rec().instr + RECOVERY_CODE + SETUP_CODE

def machine_constants(pr=None):
	"""(kernel ops per batch, stage-1 ops ..."""
	pr = pr or prog()
	filt = stage1_ops(pr.pin, STAGE1_PLANES)
	code = pr.instr * BODY_BYTES + (filt + LOOP_OPS + other_code(pr)) * INSTR_BYTES
	return pr.kernel, filt, pr.kernel + filt + LOOP_OPS, code, 8 * (MEM_LIMIT - code - REGFILE - COUNTERS - ADVICE - ARRAYS) // SLOTB - LANES - CMAX

def table_bytes(tmax):
	return -(-(tmax + LANES + CMAX) * SLOTB // 8)

def phase_bytes(code, tmax):
	"""(setup phase, search phase) resident ..."""
	prog()
	return code + COUNTERS + GEN_CODE * INSTR_BYTES + GEN_SCRATCH, code + COUNTERS + REGFILE + ARRAYS + table_bytes(tmax)

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
	"""Operation budget in word operations ..."""
	p = p or plan(256)
	pr = pr or prog()
	ph, filt, body, code, _ = machine_constants(pr)
	gen = 2 * GEN_FUEL + 1
	parts = dict(main=body * p["B"],
                 slices=-(-p["B"] // p["Sb"]) * SLICE_OPS,
                 stage1_hits=p["e2max"] * HIT_OPS,
                 events=p["tmax"] * (EVENT_OPS + 6 * (p["tmax"] + LANES + CMAX)),
                 cuts=p["cmax"] * CUT_OPS,
                 recovery=(2 * p["capr"] + 1) * (packed_ops() + RECOVER_EXTRA) + 608 + len(rec().init),
                 setup=SETUP_FIXED + gen)
	return dict(parts=parts, total=sum(parts.values()), plan=p, body=body, gen=gen)

TB = 17
FINE, COARSE = 20000, 2000

def _lossq(Tp, q, tmax, kappa, Sb, rate=1.0):
	"""Bounded-restart success bound with ..."""
	from math import expm1
	D = 122
	L = Fraction(1 << D, Tp)
	c = -(-kappa * L.numerator // L.denominator)
	th, Lf, cf = Tp / 2.0 ** D, float(L), float(c)
	Q, B, Np = q * Lf, q * Lf / LANES, 2.0 ** 256 / rate
	k = int(q) + 1
	while tail_log2(q, k) > -40:
		k += 1
	n2, shift = k + LANES + CMAX, 1 / (1 - k * Q / Np)
	pi = lambda m: exp(-m * (m - 1) / (2 * Np))
	split = max(1.0, Q - 120 * LANES * Lf)
	edges = [split * i / COARSE for i in range(COARSE + 1)] + [split + (Q - split) * i / FINE for i in range(1, FINE + 1)]
	delay, pa = 0.0, 1.0
	for b in edges[1:]:
		pb = pi(b)
		delay += (pa - pb) * exp(-th * max(0.0, B - b / LANES))
		pa = pb
	p, ql, hq = exp(-cf * th), Q * Lf / Np, Q * (Q - 1) / (2 * Np)
	p2 = exp(-(cf - 1) * th) * (1 + (cf - 1) * th / (1 - th))
	hh = (Q * (Q - 1) / 2 + 2.0 ** TB * Q) / Np
	cuts = 1 - sum(comb(n2, j) * p ** j * exp((n2 - j) * log1p(-p)) for j in range(CMAX + 1))
	t = dict(no_collision=pi(Q) * shift, delay=delay * shift, partner_own_trail=ql,
             partner_cut_trail=(cf + Sb) * Q * p * (q + LANES) / ((1 - p) * Np), too_old=hq * p2,
             rest_of_path=hq * Lf * (Q + 2.0 ** TB) / Np, finished_count=2.0 ** -40,
             cut_halt=cuts + ql * (1 + (2 + kappa) * exp(-kappa / 2) + 2 * hq) + hq * p * (3 + 2 * kappa),
             key_false_match=tmax * (tmax - 1) / 2 * 2.0 ** -(min(KEYB - (Tp - 1).bit_length(), 256 - D) + log2(Tp)),
             table_capacity=2.0 ** tail_log2(q, tmax - 59),
             misc=Q * 2.0 ** TB / Np + k * k * Lf / Np + 255 * Q / Np + exp(min(700.0, -300 + (exp(5) - 1) * hh)) + 2.0 ** -90)
	t["sum"] = sum(t.values())
	t["P_lower"] = 1 - t["sum"]
	t.update(trails=q, k=k)
	return t

_B = {}

def _b256(Tp, tmax, kappa, Sb):
	"""The least B (multiple of GRAIN) with ..."""
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
class DigestNet:
	"""Experiments only (not in the search ..."""

	def __init__(self, qint):
		assert TAILB
		g = Gen(256)
		E = [[(g.inputs[32 * (7 - k) + j][0], (qint >> (32 * (7 - k) + j)) & 1) for j in range(32)] for k in range(8)]
		S0 = lambda x: _sigma(g, x, 2, 13, 22, False)
		S1 = lambda x: _sigma(g, x, 6, 11, 25, False)
		mj = lambda a, b, c: [g.XOR(g.AND(g.XOR(a[j], b[j]), g.XOR(b[j], c[j])), b[j]) for j in range(32)]
		ch = lambda e, f, gv: [g.XOR(gv[j], g.AND(e[j], g.XOR(f[j], gv[j]))) for j in range(32)]
		neg = lambda x: [(s[0], s[1] ^ 1) for s in x]
		bw = [None] * 8
		for k in range(8):
			bw[PERM[k]] = E[k]
		e3, e2, a7, a6, Q, T4, X, Y = bw
		a5 = g.addm(Q, S0(a6))
		a4 = g.addm(T4, S0(a5), mj(a5, a6, a7))
		a3 = g.addm(e3, neg(a7), _constw(1), S0(a4), mj(a4, a5, a6))
		a2 = g.addm(e2, neg(a6), _constw(1), S0(a3), mj(a3, a4, a5))
		t1 = g.addm(X, [g.AND(e2[j], e3[j]) for j in range(32)], S1(e2), _constw(K[ROUNDS - 2]))
		e1 = g.add(a5, t1)
		a1 = g.addm(t1, S0(a2), mj(a2, a3, a4))
		t0 = g.addm(Y, S1(e1), ch(e1, e2, e3), _constw(K[ROUNDS - 1]))
		st = [g.addm(t0, S0(a1), mj(a1, a2, a3)), a1, a2, a3, g.add(a4, t0), e1, e2, e3]
		cv = [g.addm(w, _constw(v)) for w, v in zip(st, IV)]
		a, b, c, d, e, f, gg, h = cv
		for kw in _KW2:
			t1 = g.addm(h, S1(e), ch(e, f, gg), _constw(kw))
			t2 = g.add(S0(a), mj(a, b, c))
			a, b, c, d, e, f, gg, h = g.add(t1, t2), a, b, c, g.add(d, t1), e, f, gg
		dw = [g.add(x, y) for x, y in zip(cv, [a, b, c, d, e, f, gg, h])]
		self.out = [dw[7 - i // 32][i % 32] for i in range(256)]
		ops, N = {"x": "^", "a": "&", "o": "|"}, g.nodes
		last, slot, free, src, m = {}, list(range(257)) + [0] * (len(N) - 257), [], [], 257
		for k in range(257, len(N)):
			last[N[k][1]] = last[N[k][2]] = k
		for s in self.out:
			last[s[0]] = len(N)
		for k in range(257, len(N)):
			o, x, y = N[k]
			free += [slot[z] for z in {x, y} if last[z] == k]
			if free:
				slot[k] = free.pop()
			else:
				slot[k], m = m, m + 1
			src.append("    v[%d] = v[%d] %s v[%d]" % (slot[k], slot[x], ops[o], slot[y]))
			if k not in last:
				free.append(slot[k])
		self.out = [(slot[s[0]], s[1]) for s in self.out]
		ns, self.fs = {}, []
		for i in range(0, len(src), 4096):
			exec(compile("def c(v):" + chr(10) + chr(10).join(src[i:i + 4096]) + chr(10), "<digest>", "exec"), ns)
			self.fs.append(ns["c"])
		self.nn = m

	def step(self, planes, k=256, a=ALL):
		v = [0] * self.nn
		v[1:257] = planes
		for c in self.fs:
			c(v)
		return [v[s[0]] ^ (a if s[1] else 0) for s in self.out[:k]]

_DN = []

def dnet():
	if not _DN:
		_DN.append(DigestNet(prog().qint))
	return _DN[0]

class Engine:
	"""The width-n walk of the experiments ..."""

	def __init__(self, n):
		self.n, self.pr, self.pin = n, prog(), [0] * n

	def _low(self, o):
		return digest_of_g(o, self.pr.qint) & ((1 << self.n) - 1)

	def step(self, *planes):
		return dnet().step(list(self.pr.step(*(list(planes) + [0] * (256 - len(planes))))))[:self.n]

	def wstep(self, P):
		"""Searches side by side: search i at ..."""
		n, a, ns = self.n, (1 << 256 * len(P)) - 1, self.pr.ns
		W = [sum(q[j] << 256 * i for i, q in enumerate(P)) for j in range(n)]
		ns["ALL"] = a
		o = dnet().step(self.pr.step(*(W + [0] * (256 - n))), n, a)
		ns["ALL"] = ALL
		return [[(x >> 256 * i) & ALL for x in o] for i in range(len(P))]

	def f2(self, xs):
		return [self._low(o) for o in packed_f(xs, 256, self.pr.qwords)]

	def g_scalar(self, x):
		return digest_of_state(state_words(words_of(x))) & ((1 << self.n) - 1)

def is_dp(x, p):
	"""Mixed distinguished point: low s1 ..."""
	return x & ((1 << p["s1"]) - 1) == 0 and (x >> p["s1"]) & ((1 << p["W"]) - 1) < p["Tp"]

def dp_key(x, p):
	"""The kb bits above the window, then ..."""
	return (((x >> p["D"]) & ((1 << p["kb"]) - 1)) << p["fb"]) | ((x >> p["s1"]) & ((1 << p["fb"]) - 1))

def trail_length(p, x, f2):
	"""Recovery pass 1: steps of g from the ..."""
	for l in range(1, p["capr"] + 1):
		x = f2([x])[0]
		if is_dp(x, p):
			return l
	raise Halt("recovery length")

def recover(p, r, a, b, f2):
	"""a, b = (t, length) of two finished ..."""
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
			if p["n"] == 256:
				s0, s1 = enc_invert(words_of(f_scalar(xs[0]))), enc_invert(words_of(f_scalar(xs[1])))
				assert s0 == s1 == state_words(words_of(xs[0])), "encoding collision is not a state collision"
			return xs[0], xs[1]
		xs = [ya, yb]
	return None

def search(eng, p, r, cnt):
	"""One attempt with the fresh random ..."""
	g, x = _search(eng, p, r, cnt), None
	try:
		while True:
			x = g.send(x and eng.step(*x))
	except StopIteration as e:
		return e.value

def _search(eng, p, r, cnt):
	n, mask, pin = p["n"], p["N"] - 1, eng.pin
	table, births, ts, nxt = [], [0] * LANES, list(range(LANES)), LANES
	planes = pack_lanes([(r + t) & mask for t in ts], n, pin)
	cnt["inserts"] += LANES
	batches = 0
	while batches < p["B"]:
		planes = list((yield planes))
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
				w = key | 1 << KEYB
				if w in table:
					t0 = table.index(w)
					cnt["recoveries"] += 1
					res = recover(p, r, (t0, trail_length(p, (r + t0) & mask, eng.f2)), (ts[l], length), eng.f2)
					if res is None:
						raise Halt("recovery found no pair")
					return res
				if cnt["finished"] > p["tmax"]:
					raise Halt("table full")
				assert key >> KEYB == 0 and ts[l] < p["tmax"] + LANES + p["cmax"]
				table += [0] * (ts[l] + 1 - len(table)); table[ts[l]] = w
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
N_T3 = 16
M_T2, B_T2 = 256, 16

def e1_rows(trials):
	"""attempt() per trial, run side by side."""
	eng, p, G, C, R, cur = Engine(N_T3), plan(N_T3), {}, {}, {}, {}

	def adv(i, v):
		try:
			cur[i] = G[i].send(v)
			return
		except StopIteration as e:
			R[i] = e.value
		except Halt:
			C[i]["halt"] += 1
		del cur[i]
	for i, t in enumerate(trials):
		C[i] = Counters()
		G[i] = _search(eng, p, derive(t["seed"], "t", p["n"]), C[i])
		adv(i, None)
	while cur:
		ks = list(cur)
		for i, o in zip(ks, eng.wstep([cur[i] for i in ks])):
			adv(i, o)
	return [e1_obs(R.get(i), C[i]) for i in range(len(trials))]

def e1_obs(res, cnt):
	obs = dict(target_ok=int(res is not None), batches=cnt["batches"], halt=cnt["halt"])
	return (None, None, obs) if res is None else (message(res[0]), message(res[1]), obs)

def e2_trial(seed, tr, st):
	"""512 points at full width (uniform ..."""
	src, z = tr % 3, [0] * 256
	if src == 0:
		xs = [derive(seed, "u%d" % i) for i in range(M_T2)]
	elif src == 1:
		r = derive(seed, "r")
		xs = [(r + i) & ALL for i in range(M_T2)]
	else:
		xs, cur = [], [derive(seed, "c%d" % l) for l in range(LANES)]
		for _ in range(M_T2 // LANES):
			xs += cur
			cur = lanes_of(list(st.step(*pack_lanes(cur, 256, st.pin))), 256, st.pin)
	digs = []
	for b in range(M_T2 // LANES):
		digs += lanes_of(dnet().step(list(st.step(*pack_lanes(xs[b * LANES:(b + 1) * LANES], 256, st.pin)))), 256, z)
	first, pair = {}, None
	for i, d in enumerate(digs):
		c = d & ((1 << B_T2) - 1)
		if c in first and xs[first[c]] != xs[i] and pair is None:
			pair = (xs[first[c]], xs[i])
		first.setdefault(c, i)
	obs = dict(source=src, dup_w0=len(digs) - len(first))
	return (None, None, obs) if pair is None else (message(pair[0]), message(pair[1]), obs)

def serve(req):
	eid, out = req["experiment_id"], []
	if eid == "bssha-n16":
		rows = e1_rows(req["trials"])
	elif eid == "proj-k0-w256":
		st = prog()
		rows = [e2_trial(t["seed"], t["trial"], st) for t in req["trials"]]
	else:
		raise ValueError("unknown experiment")
	for t, (a, b, obs) in zip(req["trials"], rows):
		out.append({"trial": t["trial"], "message_a_hex": a.hex() if a else None, "message_b_hex": b.hex() if b else None, "observations": obs})
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
	print("2,560 lanes (10 batches), full 256-bit g = f XOR q, program vs scalar walk-B encoding of state_62:", t)
	ok &= t
	rt = True
	for _ in range(10000):
		w = [rnd.getrandbits(32) for _ in range(8)]
		rt &= enc_invert(enc_words(w)) == state_words(w)
	print("explicit inverse round-trips on 10,000 random states (enc_invert(enc_words) == state_words):", rt)
	ok &= rt
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
	t &= packed_f(xs, 256, pr.qwords) == [f_scalar(x) ^ pr.qint for x in xs]
	print("recovery program (%d records executed per call, %d records, interpreter and compiled form) vs scalar (bare f and g = f XOR q):" % (packed_ops(), rec().instr), t)
	ok &= t
	rows = [rnd.getrandbits(256) for _ in range(256)]
	t = transpose(transpose(rows)) == rows and (transpose(rows)[5] >> 9) & 1 == (rows[9] >> 5) & 1
	print("transpose:", t)
	xs = [rnd.getrandbits(256) for _ in range(LANES)]
	t = lanes_of(dnet().step(list(pr.step(*pack_lanes(xs, 256, pr.pin)))), 256, [0] * 256) == [digest_of_state(state_words(words_of(x))) for x in xs]
	print("experiments' bit-sliced digest of the padded two-block message (256 lanes) vs scalar block 1 plus block 2:", t)
	ok &= t
	ok &= t
	p, found = plan(N_T3), 0
	for s in range(6):
		res, cnt = attempt(e, p, "selftest/%d" % s, "t")
		if res is not None:
			found += 1
			ok &= res[0] != res[1] and e.g_scalar(res[0]) == e.g_scalar(res[1])
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
GEN_C = __import__('zlib').decompress(__import__('base64').b85decode('c-pl*Yj@MQwx8**5a+H7F}QOqKN5#bIjb;*Giw$w1ML7eD~Dw}PHWOQnb>I>p!3`Ben_&MrY&>Nxx=)2ZS9w~wzedze}5!iEc3jolX6^?r{cLd&C7h5)bpj7Pegr|i>h8G#pzis{HVKso|L)h`ukO#FT}fl9_~Y>SS;tK%VZ`xX;qyiKP)y+#LK*Nsdt&z>-loZh2;Evo*`~7M*Hce&c!m%=F4&A{2;{Zxi~M<%oXKa%m^APj~g_is6@Id&g(rPM7=Ju{E1j3RV6%;%~xez5#CjmSIB*SkuNuZY7CUiv8F>H^HsfA)zyG|OOeltx&m5<;xqx4fJ_23*W8)$)Ws|xKy_7|mdQDSl=-Phi&}Ut!$BT!?aSB&TBil*XelPk`HX;M{|99HP_cpiBZ2Z)PsDtYL4Q(8DaPU(Q2FskAw9^YnDaf+IWOw^9C(3oN<g>L+efSoogzOc9X|T|UcFi5<9s4kCGwh&MRt}f#VQ_%Yc18;d|8W??CxkQN@xlE!QOvCbphl4`qkkF5eG8tHdSwro{QLz<G!hS`}!xakOt!2F<Oo(|NOS|*%2MIo5v#X#Us(_iG9(*+NV!N<Ty}Ir3WIAj?*A|^V3nMg03C>4WJT1yvyJP{I_c0-X6VVFa_0bn*QhL?Hl2(O!>|0BOzCNVEuKGfr11M!w_W}4WrRu@6)HGu9ro+s`F2uIvud9F|cQYgU#j3YACxw972bt32ktQ3bSfK+DSSL{E;gbDt!-KM=D!$`uk9Nswz=Xv(KDnXPmzCR4O^GRJl^+W1ae({_>vF*M}-S!nDQM$6>69eo&nbU#T=u#H;+%6nOJPRk+ZF5=yQZFE=fW$IpgRDx5D~Du#|ZJvmVVylgR&&C7~xPCPn%4-D;S`1R=RD`*i1;%nEHZqN1H$PHcJ4X#?$=f!vkrUx|U#ih={Y|+`0Mw;@oi^Ak8%Gm=sFIA@&dUP8gI84N{z+Z3R=Lpm?had1;(3UU3%T2-Ym9zPU=?l(umDS=aA%U({4FJFvdyq<bl1i%7Z=(ZDIg&*%1cB!2%P007n5mbPqU})ziGt4pDgGcmiz}Gallcy{{`|XAs(0Bv^!i8LZg1s!m(QMcdxuAHg!$lk_vl5?^D%!Ig)d%2!6D`&=^aIW?*-=j&%CG`$Ime@U&O&r{ljMj^X$lb{*&ylu6EG=We6@q5fA-1@hANlJN0DH3&Xy|d>UomB+Vw6&--aKP7`LTA9XW7N{L8+BBh)VeBTcyv7dyPPg0ph`Iz9xvDZry#xMOih*FQ>{V<Sml;(sd^0MAI3s&ylJ>bGm^Jv^7OtCl4Q#m21emc&)ZbE9xWIvrqhRMTz+U;kAHJ_w;*o(WE_a*=}&bmy^%MzJolpp7PKkJfYVbTlZFiD7uEcFuTK$_@+O5$<C9QETMk7Psxk$^kSy4^A9$nyffmyvAgB<lAj8FSaoJujUEB!86j`ZA<?ubU;^AR<m>==c3T54zt=dtSnW?&mV~Wk5K?G4MH_5JyoEfHI`gQ8)6EUJ!-MYd7(dltv_$nV<E2)|cP&{fx0DemcqHM6v`j>2^bc&-^frfjH%R-7Jy`b1eZ$4CaIRZolt!eWEo9y*!8*r-Z>sJnV}c$$k=MQj)f19sn*cX4%5H*9%F8AWXe9OO+kT%*#@u7UttPNkSflw4Y^3NTbt@{k%J2JpvlAubd?7#Yxl+cm(4xi+izTYss>n=ObMjH80I4lL=u>!U&X~r#q*^ukX!N4Dw#!gA$2K<d5Tg%%ctp0c51Vo*#i}<)puH==Gz}CzvptjMIp976ud0J<pPHJO)K&p+)-woFzp-9rBzDm-rZSl5mnb;_KeMVj?=zsd#!o3qMq$UjkmE0YoD8YFUDd*}Dh+<`LG?YC4@hehi)majc;ZqnnNjZye040LK~Z-CGVl6uh&Fo%sSV4y7)xvE=JgXN?Pc>|kZku9RJ>4coPT2<Wf0xER+I)da#`l6Q$>F!!PZ>+_PrkP-gwEL9K!iA2$Cg)Q^*JgF=kR^M+25LcjJ8iUmt;p=3YcaV?8GN0s2(k<Zuw!yit2drvtMRj}P!2``SQgl>DMOOn7@dpRu&yFIm8d!>f5wpQS12%zZzk{RW4PcOdgs=?K$B!L>OaS^dAQgWuFhj}$NQ&In7^)$zPoF3%FG^U0zHIjxh;*4JQ=)_jfe`k0#NA}So7&Apw28(>dXHspM$1;1(G{2@gD)-9p|LyVc~V$*!_jQ9HOjMTYeHRevZ2wYW&QDEHP95>UP8ReQSOGum52f7mjiJL$z~unkkmZIaArbDb#!5$aG?7_%rIp;$|_PW(}0O~fFTEwzegaQ`2yIMj+v8wGbN=&9k6K-o(^<*B>Zj^hC$Tp$`yszK8zVhhFLWl2nAU&T9`GSAFOyl4HS+{Hg&Y_IF!WRKn?*RkTi{D`S>w$qZ=PT#%L21)%Uz+aHY33y2=V}LPg^@hK^XN^aEw|YY?(qc(>5fq{JN~h~Tjzv5JEIgaq@WNPPRo;eV=Y8id^~g!fce;6nEyh6pVx>8r5x25K8L`hqg>OcD_)g;>{-63D5b_28}u?PR%8g$)ibx}bGZqLuAKKsl~Br!+Lij{EzTbYN5CO;gDNY6HvWFo(+{^i&vqXLD*T#*QX|9?!w)gCRLIJE|i!KW%B$c6Hbc6M~sz9Oyo&8da5_gF$>H8v~AkItqLsn!c(l<_8S6A+XIYV3rL*?T<EZOr&$a(*gemw5;Xg(poPZw1aI{T4F3O4f_pO8t=x&ySavUa~s~xpy6I?<h}w2ILEAA%S$~5MkTx9HU>^>V|zIEr44exdUSB3i{<N%7Hf^GrQidc5n7Y@hj{p}hXPMUuq?6s0Lu@*J#-CkV9A$g&DeW=R-EUz*&l8E*ytb_!HEMH6t`r^#dxHrw3?{>ff3%Q!?=LECuT>@Lh`2?0oC*wjb4dwgKMulAKtv}+_8+@SIdF%c^mOB(YYk6X@P7SkV^#F*dTf_Iyey9z#W9%a5!XSfMpK+0<Z-QfXjl}7UA&qPk&hi#lAKTI>LD(HaCf*MA-tryjwJys2k{V3GmoWQ_u{6S>0FIO(zgtD$y0V1-%2<*LwP9mZ1e&OIt?dVB?BEuD5KIED9r<1Oyk%1!VqkY>iWtI!QWq6wgV<$)jpDQ@JczE;l9&oi8d5tiM7(=#yQ!;sUE&QC@Ipp(2bj(~(A?dO!jHhusCo4is&3j8|Zc2MLCF+L`hIBEe$h@T>}kWd_p}`fxP|-&66gcEyz-&k1~$7dCj~`;b=%0-2cBHJU0X8x<Tid@dBD3&rWeu*z!jpc&{P7>|d9@$m3CN!l&GYVj$gVY7g~dLTOh&4%%nIHG<d4)W$6M|pE;2ekLDlmIJe!a)ZkTF}~um6fVoDKosM_gYxFu_2QZYH1R}9)oJp1fZ@OC=*b<@Pv6`_6yq@^&5>|GXJQ94QJ&@Q>z<hH!Wssa1c`+<X9GNCd^l@wyE*TI~YYl7`MIo+$j@*0#)gfOO)uSq$QqFFvTe~wQ313+taX9)|@x<^s?T9Xai_L@0JCG!H}jU%}ua1OH=QXrZre{=U`3IU~#HZ!B+(yJ4N!6MyVm&!9KVigKNVc2P`9=p+C`$Ueo9~w)<@{hrCRuf#Co)3rt;QXx=C;ItcjR;u=aIYw?CaPkG`oKkUHUu8@vc*5nQ!t=aEgB<Hk)-sPx#<*C-_aextk#W1Fzm2I_s8jy^~S;s!VcJ0&bXUfgaSGDrMG%B~!HK8y$G0-)1W>#=g;m;uyUGWS(Cs4CvVVY^M9R=^-0J-S*A5;bW0^kN+Rj6?Hnnd3v5Gs(Q2MDMp5mEgV=d?D?Ur6^C*1q`y25iTc9zdReB39cNu17!`(G3&)YU_9{7Vkd3{#Bi?_1xH%T{n<!(04=64P&<(Tsx7YE-&$Rq(4$i+*erSr0ZX~ka}*UQZ5H>7gFC1-I&tI?NNQ-l^$ifIuimUWOm?caByEqW$wW!H10l?K@4A^f=*kgq85sXx=MpOVs3oE$+)C<9T_8$hQ5}`Gsq*tVPx#NQYr|jVPslCp;4G@aTc@`hQc=tX=MLDxI#+^TVuYZDPJkw8c1Ie`%k0VZGms-es08vpkRSAAep7)#D@f#kch%<wPJP5#ef^7;#ik`O5!%GuXO6EO7D85DiXd{t+!RXTclsqJnXytFXn#@FnY#nQx=!xBj+bP?H4VNJ!Q{11<x5nqE8QLnons{*WrED`~<gE5r*E2CMKVn^O*f>2fW$*+;)I-CcokYm_hROj8o0rqvkA^!Z{Ne&0%?S#TUxa`i5NAGb^0Z(y+vcP{$PC%&rDEhFJV!iar)srWj!H#1umlcU=r+2r=dbAF(6iKXDPe;4}73QzirZ(v->Nt(r0&t)Hl}9Xy}%NSwk*(BMvi+$k+&LZ4P%49S;HN5j(*5FYWdWvkX75tk8!0;fpHYVt-p?4}Ua#XE^7*8%Xr0G9&|pkdV^87qKjzQKMT{y&1{!m5BcNZ&U!fN~p9YCuvU*w;URxhGZ+f4hgTdTa%1^-L?tirP<LO)q0r{zCD(P|T~Ky2Kk03R=5R33XsHs`H8t`?nawwz8`+`5F^ep}xx4)tJ|g(+)$4O4Kkz%=Il+qBeIMY<AQRm)J8K0VP$#?iXSgZ?vTfZlMFM<cMOo6cK@M$q}o{y(VZd?&jB5!>(Drn-y0%FtwmSt;?$+FDTH8-fOTO76rG)MONu~D@xikTR7N!g78b)P|xW%L}v8a69$1Wm(m4ppD}pzD0su)&*}FA4BIGk;%slRrHUY>6+u$qr3AM_!RPQB_vrUh+`<3p!Q4(4*Ehs!KMYtU#H9<f9X1f38R9c<m_H-HeE1p3)k9GFf-dDoP{VuS(xXH70e&rlXWr;z(Xo<37U;KJ!2vJmXz38#{yxA_H?dC|DsdZIdS-K-0r3<gYC*zeN|Z&jcSb0+l4#@|RHN~)HCkEA#nxz9-|J<q)9alg)>=gWKPMgzh%H~r$E9@Tbt_F1_~V2fkU=iVFP%^hzY_r)hFE-+GllOR>~w3iTZ5bK8r{2DAt#AofwZ?iy!{Cz*)t>#S~RC8*UrFT%Fa5?{>z%6oPD&ecoi?rEX~w0SDLDw8Ma=i`LQebC{^&GSMrSJqpiGMdpvU{xvp@1&_`elX`TO&8R$iV*|>evdVyEa1}p7Y$y8yh2ckWOb&V0ze(~_VIYOfz&B}DYykK*poil6iqP;YzlZK}h#;|t;eCVMdk(}^nWYCXV(8~t{ZpQq3a8Co&?momq%^CZJx*(?00`_jGXbR@a3oF)x4I{|3FQ#~Zstaifs-)4I4(`}!AHHH6B<A=4u{FYqu%XGD-B%>pls=SG*Aks65Js1Pgzb|E^wb&2m!^Y8JfqlO-YdQ0o*U6&#o;Tbxtza=cQb)Vh;75Kiql!L+wu?D;+ImTzDfg5tFvNKx6df-$?vP#|8?uA?{L`p43XPX^4FWF998418WWIWC`?rF2!KEW!i>?|kjo>jK1em5K;c0&DEw#b6+pZ%&Y*RSLASi+f)w!C{>q~x0o7-xxq0D_Qk&};TZ#CoFkkrdYF;_&veCW>Rv#47P^b@82mI+^VLnBv_)0`vS*IG>Kdo*KDb$AJ)Z?`Fb_5mZG1Q&Koo7nMWC|5YulQ^TwY)+%Y@a)UY=|4<5WE?r!#57EIW)ok$XV?<G)ksHn|*V=$)SmLoW3?j!}QI9M+!u)=o*FnW0U2E`v-OdRq}d__m^vRj+|)<c;t-`6jrXyX&E!O4aE@1m7|V^ulBY^Y+1I>#@1eI#MUe&&%SpOKk3EKWFgLmO|kGHc=cMb+pd|Foi(QY`!K>a74dX2b7$uy<<2M((x%RY@y@QZ&o<pYcO`t-l`Qr5VUNB^R{VGj;L&%-2=uk3i;8!QUymhzuME1y@0;Y+fLCR##npF>yS5Nd{n+U#-FZj@F@t-O;F^5@dvu2urd7alcv^o_>#s317S5O#ehAyDQ0>~_>~?Nz>`t{Q>$6o!8&U!$6VymB=Np#D8h7?;_b@_S(TD)qfRv9PcJCU1pcw!U2Tm*h^&u-i*ji|A(kaqm<`mZhouMkJtE8#&bd{&7ULRrw;p!Qvu7>KGsz_HwrYh7`p~iKjDq>YZs=|uCsvwgeTtC`g&#F`Qk=mD<uN%=z#g2)1T>Ko99YM>H;m3<cUn)jSmA+Dri}B+a@o`u{OaKg~BaNc9>U%3_{)H&e;;-R31envnw0W=P*=a`~NLk~Yw@Q;%>9kckYnR%M*Ib#32a40Xqk$JM8`GVT)t-Kj%Q-%7yj4!!2+^JWPEHzfXQ$MWP#H&ch7S#p36GoTrdD6nvqUOHdiT;5`L>7N>Bi>xXkpun&38L7d$_kI<NP)h0p1<&8v13D<sHn@SkOKZBbl;*P@F!CyLo?tPc>Bh%HOTv;pmOf`Y82Q6aR>t3$k(yvYMwnQ+&abIyb~3_|%B+)o2pp6PRLj6L73x)r|R_R_C98-|n%?IvTgYOMui%fd5@fXyZh<d++8I*y8u?>z}UO-aS3QuaY_JVQa%@9`A=8oar*6>%<69_rUmKaK<iwiDQ7J0rm~7MBqNY0yEINj8zlqnvNFfUQ;RQB<LO)A`FMFM}rJ?3}n0`zVF%>UF(*fW#mtkX@ngLkQ!g+S<#kpfA1k;SDp`{v1n*J=4b-~uX}m9nnAx~n3hNI^V@GQn?uOM&oQX$D8QFakiyT053cz5QCz8`$Ihc?pB#Mp0@^r!hPyDEwvq&?kym~8X?Prsbhw6V4-Yv0?$Pf)z0)EU8a3!4xznUR_-s(*-3Ip3tqDVV6pg+szM&)a^g9EbTcevBL!0l9YyJ;G&FvA5RtN@}kpJyBYTPk+QETu*qr+W;_`%;Ayy)K^JYNl-CLG?xXV~I1FyOoSy~b(yZ*wXYr<!zd6Q@CoQ{RB!#PKy=gMXV>Pw}dW`+qHl;4UWCX10}m?Ou(wM90UL9NOFJ6&ip(d>FMNW@W0R71K`|`Jw6K$LnO%wYvDU6{}u;j`W6yt-fVlM4fS7wN4hTCls-IL2;|H=tRRjsema49MQYV^@#O!E%K=5%Q`P>EA}|DqX#-2X;#7Vjdi@K4@TODMdcBH=B_^7t@TH{H7al<o(iiQH_#=Jff&%UPE~nnDr-DU$Cab$qVQN93biBHdfl5}E<nmpWirb<f5T^zpBDA<Zw@#-K1bpTt%BB5nvQuheLgQwod@*DQru1fA4jz)=!);5fUtKFSguOKO~-nxvKc$%?g#a5ls^CYlFuiCQJS`TX*cmR=cbun*qe4N4H~@k>a=N{q+nz!zp(P}o9yrSTqFj2lz!aQqTyMEORKQVPpuL?zBk3$MPU~z8_@2C>^7y3P4<J|<PTppd5W9c#fzqR{H)2pcxlxiH~Ev3CjZWYIka?f7&Q6uasvfF>f+v!K1+ugM&C=TP+f)W_{3P{3fvT65155Im(8~)>x`jiFj?`z3*>OR(x>n<y)WS7O$6h8hu%2Bw&UrI&t&L5095iZJ{knSYvwDly?fe`I5s!DZ-E3q--p!jg0nau@rxM6j<h@OdOJq%;npK{aoJ?AtbR(9OWqeD_u5-w6+Y&|Cl(mhMtGlQUO_m2(czgVT=?jvaEPD!+7rRLc_MhrQwH;R%YMy3ZyA1m+tEP#bij<S9NGexJV>R&0y)j?eNuEeYNP~oB_Tp-o1s@v*6Y?C@%QL~gjn)P_<gMklmp-0m&zm4(|ax`Sm3c%VrZ?DwRL)oreD?ra~Zv5)+H?|^vx|k=b1GhqMQ}Ab%91g`D*g`)DbgU2x7~p?@EwyWO;^{bc{subE5lDa)_as`UKg0?`v2#A3x937r6BdFLAA>Gq^#*XD|<6J)~CHm+>(K&Td{UEm6OZ=gJYLgg6<Ax!uLml~!m$%oTK{r5T-$+6pGBQ=$qUyG2=zCsE=Yf{X?h1DsRUM7P8Rd#^1y*~bpy`9;=WGdsS3(IcPgm!$j`M+)ojjTCwglF#~Mm||N%vy|>`)KtYiQO|MOlj|l<?l+!*#d~Lor|*W;8v?aQChFS3Q>r+kKNUeAI;#qHyyR)AOn({zrv&}A2{l{m`QqAiwN7~u*|hz_VPT$a^TGbwDnnfMjiV7=1EUIBiMOi*s+QgD`jF~<*tX--%e8(U>e9Di>ixFoG}Wo8_U-DKmWierzY@b2W8kw@;elQF_K=K|-kv`NQvZPTiAV-iHG?X=tDQkrs*KVc^eP0eZEUXq+jU&Ky1mno)=iT=@o1{jG<u2y<*3o3Ds$#SV~^3!0XDZ^j;WOvBH8~1A$Hpr')).decode()   # the C generator source, zlib/base85 (python3 bssha.py --gen-c prints it)

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
