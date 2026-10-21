"""Birthday collision search on 64-step ..."""
import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, log, log2, log1p, exp, comb

M32 = 0xFFFFFFFF
ROUNDS = 64
UNIT = 4912
LANES, ALL = 256, (1 << 256) - 1
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
K = (0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
     0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
     0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
     0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
     0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
     0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2)
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
	"""All 64 steps: W[i] (i >= 16) is built ..."""
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
GEN_FUEL = 204922583
GEN_SCRATCH = 111904
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
	print("2,560 lanes (10 batches), full 256-bit g = f XOR q, program vs scalar walk-B encoding of state_64:", t)
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
GEN_C = __import__('zlib').decompress(__import__('base64').b85decode('c-pl*Yj@MQwx8**5a+H7F}QOqKN5#bIjb;*Giw$w1ML7eD~Dw}PHWOQnb>I>p!3`Ben_&MrY&>Nxx=)2ZS9w~wzedze}5!iEc3jolX6^?r{cLd&C7h5)bpj7Pegr|i>h8G#pzis{HVKso|L)hhWk~WFT}fl9_~Y>SS;tK%VZ`xX;qyiKP)y+#LK*Nsdt&z>-loZh2;Evo*`~7M*Hce&c!m%=F4&A{2;{Zxi~M<%oXKa%m^APj~g_is6@Id&g(rPM7=Ju{E1j3RV6%;%~xez5#CjmSIB*SkuNuZY7CUiv8F>H^HsfA)zyG|OOeltx&m5<;xqx4fJ_23*W8)$)Ws|xKy_7|mdQDSl=-Phi&}Ut!$BT!?aSB&TBil*XelPk`HX;M{|99HP_cpiBZ2Z)PsDtYL4Q(8DaPU(Q2FskAw9^YnDaf+IWOw^9C(3oN<g>L+efSoogzOc9X|T|UcFi5<9s4kCGwh&MRt}f#VQ_%Yc18;d|8W??CxkQN@xlE!QOvCbphl4`qkkF5qG<B+*G|idJa`#AWhZV*FS-UG!XBO(Q-`r=eM2Dj_9D>JQjg39*Is*?28W8K7A@8$ANk(JrIF(oCeXGpN={ebnW180F?;hT?Q}Uzf}YG_UI*pDX4za^gl;$-w1DI%5PpD3Ax$>>#vIp6eMsMhA7i$7>x#dpFSmZy)4pIoqzh&>4060fjt`>Y%X6`L)i`D5IQtXXoEvkm{kkXPSRoEk6f`(>3irpQrVi*--psuRf&R{edaVf<Mf@UQpsth%9Sb~>(uA;m-n2$K2+%urY*)k4r4|1gX(nnN~M7!Uge*rz?&bc!i6rBP;$k1xoKfMem0a+;e7E@F?7u7$%zu+Ws8w)URGpt;?d!IU}#6fuSaiRL5nyLU%Re!d#>k3Zs_`MaMhwdFUCVKJ)ki!E_DuOi_Vrb(v+WF6ed?u&K}5lsXDdLquT(%VIr0V{(1vHN1&ED{D9wrwtNX*ZVHaCoXsyxUvQ?YtQKDh33RP$006ewgH+0sR8pmW8y#TEkt~8C2sBq;KC$n>OueKOZI3cY6nqv)@dxQyT*0KC%y+2u=iil5z02;Q*FWlZdn?zweD<u{J3NXb%m>fAM=ye&kNLwWeDNX*4ly4|?<n$nFEHPK=0)Hho?~9Vh=ZT{htCM+*^&4BC)r<J?V$b35L|{L9{O?OPx>)->dBxNhJA_oG|Ie5noTgD_tR*cCd^bn>SlhF5|REyN;x6;z8_3tKM66Pq%w>0F~N^xua_i@U;1$nr5?fi;KAZ3%?VHBWxa70tlYhOz=faY(YQyLVsD(Mazar3bewtJgw&MDemap1lZXAZ+s_DVK1uVi7k4r5O#o_~b(xx%B{It>KhFDp)+Ncpq!-3vk`NbJ>Lt*DG|>f>#N&iH>c>GI$%qCbi36E+yJOOk=LLQ*BiYhP)bC9)=B}H2UOEX#{wV47Wk~g2H%q!fM4Zad@B4iobibGOyo3kc&t>Y%fN+Lm;B!17j-ns{Wk{u?ZsaAsAPSk+ZsH{=jYuprKkNIfFTdye8DmZSbdtx3WC>)_?S=%O`C%FZamx3)StJwYS^|<7%m?$`e&6f*L~9ayc@Qy934@V%*cUmH{Upq!ByGz)09;<ovW0Q47m^G?n0jfJDm#*ym!(84%*Sz(gggpqKg*JkMyDJ5d3VBk1T<h@IZ4)wlc*c;2*zO+_hQM`l4U*5N4hj>UYbuP6T+H=5hy<=nW46y1QRt<J=u#V{?2Lg>w7argS;2`pj@IJ`Qtbrvo(OCfC%Ze=SN_2Ok*5+{V4PaCJZOzG-6$b!34&HXU{kug95YAqJ05Qlp>=JdDMkVe2h6sI7uDxb?;s=5uNE&JUyU*0IJYm0k6>jB9wZyEW!2c-2*@L2y1DTolYM=29Ja|)=-C0Pe+A44(3(h;|%uhEr%Wo-dV-Yd;u7TQWw`)@^z`R#sxoiurg>@$}ZK0?OHzs^jBJ3jCYD^0^u;pyF@XVd(nY)dr9HR2!D5$DmZ~eqG-0lmic*}R2B}a@3#YpH&8H*!Rn0gbu!I6$j4%tPx2+{mhb@E;Plr6RyDVxx;^pWfo2*hI;x|hs{x7lg9GtrN0C<zEXBZx*<hdno4_uhgQMdOV32-<a1GMOj~#(b0Qxl`6@M-;L&^e3is;rD!Xd6tpD0={N?4n|Z1)(5beShpqJ#*65cYS(-DJO;+Ra3?iN;2Hk7aH~%T}1t6__J~FD=udu{-5?QdoAwQEss{%Cl)}LS1sQq0y%0{_$fq&=m7tLLAG{?}o;ehymx9191t-W*|0@)I7y-W<p7IbYcH+p!-5BF=ac-DpD@ffQfd1p$L(`M<AW~0@#+0nUj7qC8b0iuxSvU4s>}W{B9J6LDcKY6@}eCj2TCaSv4961z9m#m^Gdstav~T6pl<bb+qm{#Khh}4gn#+G>v8X_%U&#8y`Q$C=?Xc_q=9srMES@$_j2mMdLSyj##Pm17-AU5XxJ4x6sn0#GNFF;ISgHiZ%fW3Fb$U`1Xyr1*xuS5O%i^-cwzH3*CnpBDAQaufozBsBO^b3(CMVNkpg=VqHf{Ag6-XgS#cPljTMgHaNWKg4RiiR<;j;=D6aV($E+??(bXDflZA!O(hGc4J@0(94?R0Q(;t|&8f8*JDLP~JO`%_hU(DlsE*Y9w53to)nPMC2xg9Pp!=k1R8@Ws2Jw|_3^)erDDZ)3`l_y&A28U4z&5vlSvCZ<Kia%8k<R^22mBk*vX+ZWYrSyL4z^ioiLtyi>^EF#yc-+u<{IA3ZFo0>hI_4%`wAT39J6*UFZCE0mF$Mw7&xts?cvy$Hpl_%(ZLNcmajWntTnEdf)8*;XiefD;^Ds@3Op^rvc&QOEI<7A&^5e)C10X7WAF7@ah~61f3zWFqk~`sCk|jx+>#*|<B^`yYNGZBMtGwR;{xuUm>o3>$)9QjRMTfPdL_OMuD$Mjc=NV%$1-wXEeFQuZN$Gs=aQ_Z1+r;CE)is7gXqQR;6Q8xcMy8R;gFF5mO1bXz!o$BE(>N`gu~ZA{bdmp``R?<Xy=L8+$4??WefcBZqaC>ZlKF0z+*Q}K{EhmbzfmOoj`P{L|5Pz^bTNO>*<?Wh8AcoZ5fe+jVu1R-m+1$D2!+l5L_@9kom*0HBM3LB<a{uJSQ0^kE+#7<+5bC+?X(QzNk2`{tEq|Pj=;s3#@WQdBLHDiZIGdM;d|Z0R{XYb{8BwP_)f4UV$+lBpBjpXUYSJ1dEZwvnm*t8B9~?!_^#oPsP956<2~hC-7BX*x-%tLtY^WWMW#^XsVoSRB+VrxloKQ6sHTrDyzkVW}t^)JRTCp!^2}HX}9>Q#ix*l%>w%Bf$RV@8^%}Si298<$eVi{<;|rX(B8XJ0<5432OW%PL2DmYR;qHP%<!JxYhmTahD=JRrAY{T45~#FfVyg+OhEO*ljnumFKlbnZ!~(z{G$#woRuR@t!|jzw3w~IK}>a!V_CSFFkiLWrp7DpU=#&m-1g>kr%VJ2RHaKUQKF-gmUu?N6sOeGswKQ^Ps2`GbKcC;%X$l<4WI?RTNV%oLz<Q}H^J5{O}$H+)?mq<gEd8i#i>RGUln-l6v;~(rG{(=``~&Et_^z}u#9-N{zNx=O{3@7?zhDp@-m$Uh6C6vFm;uod84@KAmD$CYbb%N#Tx=W<%!4qumf+qLONnulRJF0X1{lloYM|^m!tBPr&^=O0Y(58!<d3rw$=7&Kr$X@9s69{wNJU9DK|S`)yf0YsN71|gu>*+K-bWjS;0w#KZj6s#WVDrK+TSYX{Nz;6uf@}<f7kyP!;eCfE#pGp~Bs35`C9Is6dh)AfTE=MD<gg)7m(HA>ChC`{oN6upL`^0C@t6SZ!mt9sy}YH%#!Wt>d*=y!-h2S9QMDb7NO_-9WlQ-wi!CjNNW<?L>~cyu@3R{zxrxUty7xu7Bl1>ba3hxg5A%NPRbSV@e~pNA-PIdX(wvObC#W*@3IU!F?r_xd)@rxcgKFF?@vzI&GnfS|}pwDh=w0x$yxf<C5NWWQ;@_`dTK>Add)#k+J7WsUV<+k!b~mMq#qWS<q4#3g0lKk^TSR3N0aQjro?Qe5G`2AbmybKaFa)1-_wsyAdCPf(6QeWR{W>9};9jA_}+Fiq$a}18$UxV_o(siQBNg(y6B^z3Y{#NcdW{-d62yk$zG0u<!D}nEy4v=oza`SzMBjoS*QtU$i{-ls)GZJZB7vK0TyqKBY}vhxb+U6Wmrs7<w<7n0#u^WA?8d@MiOK+X2p*{E8D`2FcemPBn9nnzLLA=S*ZYhvm%`UnocG8**9CtZ+(8!xAGx9aDTWyBgdWV)2V9`dD0<Vt~aHQw&YqbupA7#F!U+#Eyvn#6|3a&)7FjnGEbpQzn<UYRYu9exk~D@O;W6aS9_rgF6Lsr?ij>eOh@jBwsom4Npfvc*Mt+ty+IXTt*NIoFXNw$s6ggn?h6<?<AgF2fzaZTn;pVhE<1TtN^0<2K#yV{|J@~s{-O6ec#Xk%56ZY0ZD~mU;hB+o>)En?H<1Bu@$J*Gp!^mYCnNBy^K})3&ra~F|UH^5^q2#XzfBJ)Pc#U&MP|X-(n2g%C5%bYfM;$`YK~rV_rK>I}9Z%QNs)|*SA=S+T3lh*-<-OV$W;@lvEA7Ux;12>6R+Eg$}fmBZ}QpL<GJiN31IMnxMhBn_piIyJq=rR$S%4)Pe%FF0Y2Xpg=2nufcX$6x<pYS*7Q#C~41Z;b8L#!Y^q<J*VFgnbGG^7zDyxN*B0&#^BAP;0=F2r{51SY@^JHv%STZDuR?&1WAFH65I|2pTlq5qu)z$2mhxBb30vJ-w><)FkqDsmoCh9*g$+{h|j!X{)_<g;b$aQ4?*b*x|AD14ey0Zj}F}j_!SABd83a-$4UxWpx<%@2fU!8r9*K0`v6DX#6D@L#BFTpnay<u#8Zr@1qqWWQ5MbK8KKllqLFt{jmE#$Xk{%ITcc%tua~t>uXl=AYZ3kboOn1OwtOicm(rEjtu#&Gj}vx42Dv1^bV51&egte7V)0eZ6ux(`)2-2N4Q{$?bnj+`oFsw;(%$;;_9u{J&yYB1(VU)KI|G9$JL@$2FKdEw_R+fHRlGE_G*ic1X{vT+*m|Mn$FAU`RKbT{$upXdw(@rE@ywazy2ABAAAvEXb^b$Upce^d<MvJK1ztfLth8e#Q-!S_i1rxPHAYPP#l!dJ2#tC)E7Se*g3XC`&aAzQ_R^qE8lF-Z!`>0_p@)J*a>AdNK|g9iFCPrJ8T0SKJq=L1`w$B?XY3d1f|yPV*t?;kDVQrStXK~=j3Cp#nBx7ZE~F`_l16VjxMQPz_=;_inBxP))(9)Yh9+-zUy)=}`hZSdOLV3{7+nGqwof9^Q)eV!nhqNAjADOzuk?z0ZbXL_hp(LGa{eaX%>*JLwhg~3PG`w(%Rgj`UrLqwDh)WT&WcIhKBKTFzprNh*R7+z!(rz$L~cvTUv;8#RE@7{OhAgEFj2uH00IdJGe&PiE|0YOAk}yRg$L1~@Sn9;0P(&!gVr$y-SU<TQov{XE02x@RG*#Z=7m32ZLVi*CE_Q<eBsZldF80fM*AXIeP~ESp*~<8@F#_Z`4pw%D-m&JooZ<Rw7NN@P#ca@kJH-Q5mcbZP<Ix0o+%lVDO4oA;<F*t@(SIseeMLZA#RLA@Me$>-#EPH&;<J<XSL_hD47Or_RaMshbGo>`q~%`(>DtqDG<4$YZUg6O_m$(AJ`34$?GxRU#`_Ta;7QZkvBq6Sh+T*Wz5_*6hk0ajyf8?+S?kjW!X9#TYIe$TeFlr``$_X)E7UWg*Y2F#lnZ+)oaCWyJl8))|mG1!wA<@#M8yhot=}EJEKHMn>rK5JG;(4+jRTfmGEI#vee&)J^EHz@#8UoN8ckO(ASnOD&8@EJ(l<#Gw2q-Z<1F7UX`&HSKl@6+Cn__W2dKd=OGQm4DLySYx4c?(H&ZtRsqZ5Y5hs9zsAs5IAdP;fo!WnwQGa3+qtc=JJqJF&sHUENC}usP$R*dZ&)I0+}W$$!w7LjBLZXtQa*n0y=wr1W&k`KIIaBGhphZyYoWPGr$~pHQ(O;phN`5llBUYjRi3JPeTWr=t7o9P8meomB3%`ks!&&j8rPAkh*brt3M=}mf=qsJ{b+kVt4`TRYF}!;ZbUB?J0{|B@pDXe1T9B~A1@kxsTeU;`bs%2#*bsf$6*060Wg@3G>X=$@2#Nu7otFmzlP@!U`_+m=Dn6@ryYGDWsP&*Dot9Y(^l!MU1~R8b7d+XC{FK=241{uOm{+7d-^>t=lHnsRylPeM0fT(Icdn9ol-|aWgOKRK0rVwJZ_?!T76N^5~&dB-Ah;G+a7wS8=K=}hHWo4-|fWg;oh2z^V?7acz3*O=$A>BcQ8w1LHk6EWXb|Uar!Lo=KTpi;ZX4_f472%qc=k9qtshX{3C8I$jULuYM%H^@nuiy+z^Z46C}P@qe+NQV~WvDz_Ef=Gv;?%oqzs)yT>l;XxsuX0a7mk{&y{*jT7PSy_;8Hi{H1ef4X*i_w)e2O6IVKtqq@lydQROrpt(~6C*&~1LKRq8N2)?jscbi*f+2ef&2J6%s}rlR!yX9I$ETAO{JuhpnGJ9FdVub4Kma*knxWA?rUFkty_AQkv~zU5q2m*YJ8bzMO()Gy@!Zhc|L^3qM_}WqYVhW?&alb2K|m<S{}jAZ@<B84j~Ue$DppG0AD~s3O^q{xZ>kSaixwPJCB}ya_~tEXyf=9?!s)^N)n_-UiI0h;c+z5;To<zJmC1dN5A{@ev4FS)S!ptPLulJvq6z}8`w*?CJgCOH2SXihK|(J?+kEmjc#rXZN5LQ`9B0Tw?{NuAsA#r{<q(#amV0At-%Y84tEXW2Y+kuqJMkvd^LEQaCj4+VT;eefbZt_8mHmE&8bwJYSO_?oCYmUeFJ_I$Jclb{%u}8#j7Un|Fsx`yO>y;*;e+odo|V)9UohAXm6`mXaM@~VbqG4m8p_eOh0Mlho+AouaiyJ>f+N@ta=eT(i<MO`j&MOb;fzsI$5-yP{is5#jVPs6AkmE0;U*nMDH!vBi7Tk$fKGs>%6S3*yG5K9_VzWSp~~C*72r37-=6Cl}G%UyZUsu)*tQGsKAkUDy(kYK$k!UVnEM5Rpq6rtnn}%SB|EO!eezP)Q({5)o*^e04YC}$t>^u4WCbbTGY$GIpFa49EmHm3R+KTI_53)`Mf-J9?;`UaXSTk9Mz(rE53&U!rnz-xhe@a9qX;iX6%r=AJltN`uyihKA#9iY1-<g-NetIn`U}>Z`!dmXz<c&)TVWkf|05G!pgsIvcKbVkr?bz`f*c>hG!Knt->-twMz6T-xOyTg<Ys@K)V~V+mt>w*$;k`KYZ2XDQ<2TFPh@<vnK!IrB#32<WEkT{5uQg(9*?W(B#L<4HW#Si+e}<EFESTeJ`y-brrJX(_@t@a8rOiU>53JHs7ACGlrhQWW@(Bki+RppTf`dzJQN65sdd8dgBD!j;A+1lcDzjP|3&mXb}9~nXkn5?rBHj*xc~G1rq#xA5y~$&f<K;FJcrs((btH?HIj>TaVPmWs|+K`YBB=d0&LwYj1^B_?QcySYT8e;eDEU1>yWfhi9H};iH$rA%5y>PXz1ciQp|y8O-A?`!xf-W%&7RM+5EC0W-dGXbW8OAe9OW<TSVUNzvt~krL3Agb1Z=hF(2ouUmJ--=hZ-V#z1r_q8fe4t$SaDvwN0^0}a3fyY{jp|w)h*6A^tepwI9W%QO=m$anNH@EnlXV!d(a#qyV1sVzEtI6Y2N6cs;h%KMKD?!GQ<r!YmF%rqoiS9$mA%<q^6J+zfuVLAI{5(@%;MOy|#I>Hz;06hw!90BRkXm71#>WsiyLq*=MEyRVD@T|T;$$S|b{9)mTA>9oSJ0J~W^_7gE10NGi7I&P7G*V_M2T|<G8$M6a86Yd-4Yk<y|(0JA3KES7g>MJ?Dzskk9?|MlJZ|7DXhOkQs_BIKI@NRifsYSQo6fQQx*3_J;!NJuA4Zy-*^HR@0}%{z8g|+2-F^#sA~sLsp5$Kgam!)tSZ>?lBcCI{mBTN67*Ln)NHNii)+)>I^{uR)AkF8g?YBk2m5QQ3~|{vjz)A1j4Eg)-mVU)T6VYVL#p>-+m25!*ZO&=OW%g6_uHP+RHvrex2tDbCYomaN(^6&fzMWj2X^7xLo!Z!d;Szi{R7e`A{kKC465+1b_P|cGD>sMs}Q`lvAqIp*KzIY_D(}uH%<1$qp3>M=qV1AqehFW%$W;~Jw`hR*xY_OrdC>rWd9cqdg4t')).decode()   # the C generator source, zlib/base85 (python3 bssha.py --gen-c prints it)

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
