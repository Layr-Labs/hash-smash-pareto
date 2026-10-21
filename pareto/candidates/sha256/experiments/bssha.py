"""Birthday collision search on 63-step ..."""
import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, log, log2, log1p, exp, comb

M32 = 0xFFFFFFFF
ROUNDS = 63
UNIT = 4828
LANES, ALL = 256, (1 << 256) - 1
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
K = (0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
     0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
     0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
     0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
     0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
     0x90befffa, 0xa4506ceb, 0xbef9a3f7)
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
	"""All 63 steps: W[i] (i >= 16) is built ..."""
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
GEN_FUEL = 200555597
GEN_SCRATCH = 110128
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
	print("2,560 lanes (10 batches), full 256-bit g = f XOR q, program vs scalar walk-B encoding of state_63:", t)
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
GEN_C = __import__('zlib').decompress(__import__('base64').b85decode('c-pl*Yj@MQwx8**5a+H7F}QOqKN5#bIjb;*Giw$w1ML7eD~Dw}PHWOQnb>I>p!3`Ben_&MrY&>Nxx=)2ZS9w~wzedze}5!iEc3jolX6^?r{cLd&C7h5)bpj7Pegr|i>h8G#pzis{HVKso|L)h2K!Z=FT}fl9_~Y>SS;tK%VZ`xX;qyiKP)y+#LK*Nsdt&z>-loZh2;Evo*`~7M*Hce&c!m%=F4&A{2;{Zxi~M<%oXKa%m^APj~g_is6@Id&g(rPM7=Ju{E1j3RV6%;%~xez5#CjmSIB*SkuNuZY7CUiv8F>H^HsfA)zyG|OOeltx&m5<;xqx4fJ_23*W8)$)Ws|xKy_7|mdQDSl=-Phi&}Ut!$BT!?aSB&TBil*XelPk`HX;M{|99HP_cpiBZ2Z)PsDtYL4Q(8DaPU(Q2FskAw9^YnDaf+IWOw^9C(3oN<g>L+efSoogzOc9X|T|UcFi5<9s4kCGwh&MRt}f#VQ_%Yc18;d|8W??CxkQN@xlE!QOvCbphl4`qkkF5r=*0H&t(so<mhPicHnp*FS-UG!XBO(Q-`r=eM2Dj_9D>JQjg39*Is*?28W8K7A@8$ANk(JrIF(oCeXGpN={ebnW180F?;hT?Q}Uzf}YG_UI*pDX4za^gl;$-w1DI%5PpD3Ax$>>#vIp6eMsMhA7i$7>x#dpFSmZy)4pIoqzh&>4060fjt`>Y%X6`L)i`D5IQtXXoEvkm{kkXPSRoEk6f`(>3irpQrVi*--psuRf&R{edaVf<Mf@UQpsth%9Sb~>(uA;m-n2$K2+%urY*)k4r4|1gX(nnN~M7!Uge*rz?&bc!i6rBP;$k1xoKfMem0a+;e7E@F?7u7$%zu+Ws8w)URGpt;?d!IU}#6fuSaiRL5nyLU%Re!d#>k3Zs_`MaMhwdFUCVKJ)ki!E_DuOi_Vrb(v+WF6ed?u&K}5lsXDdLquT(%VIr0V{(1vHN1&ED{D9wrwtNX*ZVHaCoXsyxUvQ?YtQKDh33RP$006ewgH+0sR8pmW8y#TEkt~8C2sBq;KC$n>OueKOZI3cY6nqv)@dxQyT*0KC%y+2u=iil5z02;Q*FWlZdn?zweD<u{J3NXb%m>fAM=ye&kNLwWeDNX*4ly4|?<n$nFEHPK=0)8&evWzhA`X7)A3h_PXGh-ipJab^wS)FALvR_2c<9H8Kk3KVsV9S82;K(sX_R@BG@D>P@2Al?O_-^E)Xn@TB_jQalyXAweLtAQeiC9nNo5x0V}c*YUN1=)zx3lEN<D)2!$8JSniHPL%X;H1Sh;)mfD1p(qj8Tg#ojni<%FR6={WPc38^WQ{d6K3CJ*~*x1SN#e3Is2FYaRAn*h`}>oPSjOJtT&ew_FHtV@!GNiU4UBq1)c)JvcPX`%}%iN^_Z)Q^Kak`WC=5(hHtcE_Y6&kOusMzW=osNb7p%w0G4ymS(f{87^D%aH25ZkBX|h&Yv@-}n1G=zcHlc?l1?pUc#j0pSeCz~^{E97RC@%8*J&-N;LNK@>8t-NZ{$8j)CLe%AL{Uw+T`Gsc?u=_HR6$r8w<+YJdm^TRX-;*{@ovq&b)wFD$Fm=ET={l3@riPj|a@*rZI5(XpjurG2X`$?EdN!pfq0JyxEWeek8FC-a)F!j<bRdysZFH4D9n2+Nm33(LKewHO6jZQcA^X`Q82x!2*a+0hUCs8-x5sbqu?!}U=CChrAk929&yfmLoCWJK!BT#-$GDB@Y2`0UrQ{&h7W?BY$FYrO3L^1NmaXw}X0ObH;(q+$&z|0u$IQ05a=o3sBPR41(`U`^zj04Y@aXbd4WuZm;0vsnrLml#>3zzs9bCPh9I^yfzy<#Fd)2VoRKtTXhp^pMyqX9%E^=esyyV<)3zUL9v(#krWK7I^d2yv{T4kMk83UwUJt6;|&?A==qJrumNik<laFb<_IuCe6nQfG~eeC%Ll(5{qSstwz<ehBEVw73}K6x9SmV3K!<Vlelj18en?LXr{w?krV60*OS?Y=tfJ^E|0699G|N2M}YRU>bwf8R6?>ns<<o#WJ7dOVTaj0k*->uLrDZZbfx_;=u#WG*Wa_M@3fy67dHI;?IsEuNqj2ff2L8Km#^`$iIW5;|*YteuNMW(#MY-flL7UH6Rs#E-*vN0!WJD))=-Su1}vRLN7{KkG^d87>IP4CsU$?2!Rmxcf{Rfznj|4M6`*<MtYBBZbr*in9&uOBZDt3)1k3D<#|$AcEgcvu{FxGX=_4Va<ZY(rX~LIV>Qqe=UzhW$`S8|#+8Tx=a&O<3CU(4Hjvaj#c*aqNp*B#&v2moLi{jgJIX3jF4KUCc7Wjrk-tYEo%sUTmX4W|elsPdL>;hc5S|Wnc_jR96ox_6>&g{{+CGdKM~PWA8VChhF<O{4o*%4uKn)a*Og442?l`Q(-arlkA*eKsW%>9qaibd_KgP%t6xH{<W^kpqHM+_QZbC)lH-?T_sq_P7^lK2lTX?t7(xk-QBZ%O!BC(1B|AYkdqey)F##@0@*E9&bTL|x|uE2%vLktmGRMJ;r=?&C2X!HeT;F%;MR0^@KBPEbiLF>UC657dfqY4`wUUWh0q(m#*hv0HtaZYJyj2-v)E$P6f#+#;+1=I$X&0!9gN9d_A63^z;T8te{0zICC(+9(IXm(UbYJS?%sO{>o872fX$2ib^QZ=e7KL>;ON;U=@19cSmKs0?-SIiF>Y(rq1Tfi(Eg4!Q#-k3<|ey0Qe4QN@*#ig}gIA{mkthB^fUK;irt~B0_jdybm@8&kVn?b|9*2sMY4secHyOx)F42(*4!)*+l*2ea5>`NQufc5C$rWecC9WB-xS4+VMI3u(s@elFvUk?SIkYHJ2`2m(6etYN|-oTPC(VDUM`m8w5Z?iwz1hUaVFoF{YFeq-xkc;t1PiZw#`vW7qQHOB>cTdcYnuX*~H3F*XGa9`T-v-xScRsv%+qq*Ixv!Q3<MTG+U!rqKR?`C6G$5A<vavz*VsvmIwt+hcz2R`k$N<Y6_yu4K8UU9Cvn|5m>!1Fz2#S4e8g!iVL~L#nM~SipetEZOG*LIu<r3hro2H-{0JFNUu$xXGx>TYoa0_||u&?#>%`8I;w3fDv$ic=He_U_bC|MLnGzkbUm<!1K;n*6dD0Px_>?od-jFU&zYNm2ovRrOV7&>2699Vyae$Xeoa>WH!xuU$_&_YERWu_yIK=ptE{tvqgjvXl4<`}QQ7!MK*@w7AL0Yrku$l+NP49g6rDfHoL4!)=2U+s!3L7o%%DlcsC#`htw5Ck$Yt!p$@PBtnyYWQ3zMi+|Hg<+M|;z2XeLogl>3FG16(UP=VeAVJpNW*3Uef2<g0GbWsD{(~qMjYhLJ&y9`(hg|vT`2)p(1e2yMzo-{4=XEGxl(3$Pw%y`a$`d#CDhU+ggpk;q6t7<HBcs?df{pF!t58eHR?ASy=4AT2OG}Hk)~ER%x+rD*5DwfI>@ms+)S9ST5VI~m3J_Tf-r7-^SM(d0tKqlC6_4CQAtZYqhN|tYHHOIUbd%Ur>r?|=ILd<1<?l3g5E6)2!kO_OPZTtYnG<oB~5Fv<j%pGqQT-+qk^vrJa&rYC5=);wu60eJqFi?Jq}n#JWqe38@;B{b8Pq9Vh(wkP6NXMY!;Zh%Fw(~Tyzldzr{6_K-S_7fu8cjV}96yw_PC}v8>4*K3cQiyGYJy2ffQt`N~tR(c=Ik0E=NvK`Yy8`!paKkF$<_mhIXn+s~Anov&);foW83rE5ZAa$=xs=*+C(q{5#=D7xYqdQPBb$HFwzU^@!lzX5X5??0#t_yxcXx~fp&?lp<NOCVGrNe>WEO(LTDDb8taoWGFnFRXp@1q|4ZEj@rd0Y$8~F<g&;G@=_O_|?|&S}fjueEq9BU+cNCE4ywW-JtJ=o*Tw)H@J2pM_pdxO-X;GmbkC5$Vu0~av}BHNTpm3+%BZP8@e&2k=vvCzAHV-baf^KNXYEK)!^X1lFHnJQE1$KDuWolLIs_+P(>{i5p|UYb;R8GfRk}a?>aI@A`N{llV^}egu}?#bEQ-eP{YWyf<mJ(+2Sl{DGY^g7}Ci8e{hAC5VppAOH;m5x;2o#BKDs~wc7&U&|Te#4?)2KWk51Z$%zjMG9eL#+iJz?n2P~7O2x4*`;^3OSYPSXQ<dKJN>wC$ty*uZcDG2ssCn3T`CrWc8esH{)ut>i$w$slc-k*o9(&53a|)g_hD4tp(lnparmn;Ls`&|St0D}&7fnn)HRmz=*A95I`MK=?=S+UZ2{41?>lvq-xkt@eE`@U@GMdBk=87+rqxB8BtY=m@rKMqs5uuJLzL{MOZVa*b#T0!ku1qn&;)yASChocz$`E4A3qE2;#DC%<cEM-to2E<#_N6J4%Ud;NI$A$bWjlC2<&ijrk)Xky0=ZLK$b>$vycm)%osNd5BOpBDW6M^pKO!z82n9}&lGWsmbl6QHs*86LPp$*tfdMWD8bHIULo!wX(R_pbJp6wI%Y{_|age@mXaMClpwxh*La?uY0CP{Q9{zR@U-j4u)asd5k`=X|z?xphs{DoGb)lG7L3N2YAQZHAp%UuAWK`!B9rkZAhHYh6WAZg7tU`U2v8yq!9j6_J5|yZ7hM4PHtVC_@HrVW_9WJqFHUdhjhTSj3F5YfS72HAxTFDW`ZYd%H-;yI%m3vLlVBF2GuZCT-d^anua$ssffm)YWLtapz6}{JBJ1h!rjf<?(^H!9!XSQ&#`2^vYw4t8UZ-~t36DSM<VJ@W$+&*LQ=27s5zn|0Z2N<?d=ET|FVoMc4N-Kh-z)J~khl0=HH}28zrMQFt(}TI4F0OBg)qWVTN{CArW;<*kJ~PB;-Y|bgfcfw<lB<WH^aWkYji842!lg%t?gRXC1kb$D$D(5;g)Go-xq<^;(9zN%xcz;Aqi$lKG*sd?w)D*AIs@V<M%03Y$&@IIX77wpY9-OgJE%tEUu(3omW!>?vcA{LTBp}LMXa@m{(nw991vT+l#fg4%Ij8|Ch*4zJ0OExl3zNZ9DXwbHVm=&DrXAcJJ{*gXtxG8-8H&*vqDZ1!2)S-eR%s5NU~>09JFXoPp+MT!IYhKn*EnGK{@+qUGXYjnpv8uW3Dt+J2Py(Q1fF~@KLJZL$Bl+%|}~#yY_hIOmbb}`k;@%7}7fbAv4g61haAbru71^pbb{qv6896Ru4pb4C@*rrv2jKdvk<FJ(`v2etE&>L_25J-bH(9P$vyfDU4z72>8%LK_WTfPs*SlwV;;|2HcGK_u!resNH>tg_<+=3w1$Erv>cYP|+03l^0g52OCC^X<tn7{!|yz6jVv0Hyzxu(LQ{|Hb~6z0b*-}6=6e@H@mM$vMGHur>-SBQy`2k0SVhD5$LHik}pjMjd(_}zr0s^#XUEo!-~UKPIEbb6YpjMkr3O4UlpgbWVhuXvc)f@N_~|EoK|PWq;8*4*puH^v;XVXQQzUP^BE$yrQ|O;Q8}u{S2ZRe#ZZ{2;1K|U1cVu*w;`8DT78geJb}W4Xi)gi+ADx~Uz|bf7=vzk%LOUmv;CDvM*^zPPIL3ZAE-9hGqw`(vthpQ=heJ&)McZ65v)Egq@hqBtq%Az!oqxtQt_3DxUx<)w0~ON98#za$En9@?d=FE&||1Oi#yMhjL8%#l3wxI5NdgaZrDC|0@)BZ#vyn!NQZA6UUO)I{gJcUb7+)IgEsr-dXqyF>o|RFjE3o(1&<VnT+uZO`^P5B4fhZ12CC%s81FCF>Kr-K6!6F!At<a|o6|C8ZX1drkSj+W4PWhTjo7kmosF%%)`+cHN}hf1B!1qDpUgs>4Vz-&L-6XgVz*s0D?4jU`}bjlYbxUDV&=}yNy?p3BBV{73FDnzXP<4leeO#5uq#>W@53H_pRD-t7{H@%kP+x>OBWUI7{4A%{B{|1i{CfNs{yadSc|Lg8h33Wp8B!VQ@Znz24V*HB*8WL{`cq(EljI`<?yurq}E?!Xe^vDFZ?LBRiWCo!P)KH*4UkDQ`Tpzk~X9SOeUz2V9qxzku~n@)$U=0xS|mOvH>X{Kl0u+06{YV9uAyV{_8_lez3LB+@w>a!^|nJ2RcJlQddb+<>@L<RlPpM3c}ShP+bkxHC2(WicD3gt3r+INL9qDf>ebSeN{mwKe&Fhy`EL4>?5@=HD5QPmx>(|@woUoCOd+bBg2mujlNWjm@0jx92euqG2-K}fS3RnOh+0;Yt{Ew(EJNgpv7Oqa|ke}fobzz%d^vtK9I7;Id7FFt<q_$bk;7l8?U)C6%Q1rcSi#+UN)vXA*((89+z``+<2>;x)Gu~`<<LL<jzj1BcU>m>I@$pAQK)p(M_$ssAq{(i1hBIEAnj*z0-}&@d3lO7n|>PV)k%vO~(0cC<44Y-Zk{gB+EOPrLmxWB1ST00iig37I*Xh1fOlF_?5p~!NbuTq4iPfttS2vHy32(7-TiidZzfACv|R!Mex}X->cCi#OE-@=qBJ;!KxYaJFU(?|GwR0mvuC5ftLWOmjM5}me9tDaQEKLE3n1y+t)u`yS;mQfL|qZ*u&O_Pd?rcJ2=y2MAwNCpzeY3#o&xx{u0LkO9Sj1Sc$-Wd=X}#cNwcD(ls3|(!Hiq(n-)gGDH{-U5^GC>KMp)M||tGFS^z(J<G_SDANc#6d*Oe%(J2`<Nn@5#I8IaLSxa;cFfTR1YY;@ay5f~$1p9A;ODpBU^a)4ho56m*HM74o*;#v4<B6d@uRp>M~|IH&ptW$3<k7u{0w(tHf<#dQX{YW?9=c#8tHHi*B%~l{N1D9eR{J+Dl}@)Lvp7{eel_!$h!^frCSq*^e7sASA0W9>gjg|IJZVOH-<LfAJ_aJf|}bS8m$lvG9mxlZ`8PB@S@h>g+_<F2JwTxHF(j#J$SwvJWV*fiO;abXJEj0^Lvfc@ZaWCDo!=&;3iIk7N@=ezlq~(yaxX^ub$#n6ZijG48dJYtj%mI``W!4Yl)7JEjhHe)hjdrefThHMa;@nNh_wGH1b2!$B);^rfYTaX)9K}0v+iM4_kf9x`;aCylR~+T2Clq^@8G7WzmU-c~SvW3^<}Umg^Dg>00Db&6jmv)>iCsWJeElI?}9y<s0jGQy+}94~xnp{>)u{x?Agyc577NNIVr*H*TOyAOkU=C!VVE(p1)Xn2sw)(?#L2IuvS0u=Ub6zg&QnpUPyGcm9S?CO<9e<=-4|czlk;6<P(Yr!*b&e)@b~o;nZc!KJvJ0zQsvQP36NLjhs$BCuSQgqx1_R%J7G$lVX>4Jm#8^Ch281fw)<_0n$QC(lhYy|y>)SQ<2V=>=-jI!VFERDNOQ-#6Lc@wrG0_9*?hsYS!H3YS)4nV(uEdWdg|vx~wmR5qa94cTo<ADiq4zsVoIYVs5}w~H4|@%UMjfAP|)KW_3TCr$pH1#@WW;xK6P<K+ele$>UiBYl<*GmO5MR-w8I+3~rt$`!aNz#cFQbuOE4Pu3Yj&tS6RgBQr*bfr(>XL?`2$D0Vo`wqQvf^Ems8=uM0djP29V|+9Se&ftnVte<rBXMkQc;5mEe!dT>;RR=LKH?WKiXCZp-1T;h-ovd&>f*A=URnK=CYQV~LhiM<!YX{sg-<Lns*UhI&Afte{-VP(Pq^^WOW_bd^|dF0b@N2<mZuEn@s|CXf!;Fw{I;Wk_UV8bUpce|E_skjg#~h&+xw*Ga@0r(=t@F_(l$e{p0C%fJL2!r0|~L@lkodm6(|S3!7r6Zrf2wEP_V#bt;En;DQoNW7)`&d2j((*%dAUUQs|poe9kj#K14YyYU=`xg!0wo@u?$bv=GFWPv4aw<H+(1FX<SG<mW{9q2v%lGxZ6w`QF#CY(9RTsV{Kr8D8RAPiJt0gwJ3ezIsTlurK3d2%O!#T3VuhAJ3H|ObKx^5_7wYr7Nw_f|x7lN=q|39kmrqRHsB0Ja&t+8c(9cIRqIEECx8Is)=ri3-(@Ha<Y#d!t;x)zh-uP0i#Dg)h|i;ua6Yg-ySLS93-Fh$1ugVfMzM(-KeRGd!nA>v?te1oZN3b0gLy}5>MX^sW${_k4)6HgQrw+M1MAdK6F+U?0Cu3Qknit1WpP1%M)t0*7L=+>1v(wAhK!ug~P%;+vbD)wN-|=>>EcTx&}rSv=VPu2UIP)+w~#U`><`tr<ZH}Jk+Ic!_@n2&uOYtQ|;T;Gc6NMGkzt8FUG)UtHJ}j@a-WPC%rv?3Z(u4=@XF*sA>jPcvm}vs#F=JIp|dgUfbAS0k-S7c6EEFA+4Jxd*ablrD^mO2g*^SMOEg^g~lGEodaxczZ_F5Ekv^a3vFuN^Z')).decode()   # the C generator source, zlib/base85 (python3 bssha.py --gen-c prints it)

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
