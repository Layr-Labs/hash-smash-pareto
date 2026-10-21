import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt,log,log2,log1p,exp,comb
M32=0xFFFFFFFF
ROUNDS=40
UNIT=2896
LANES,ALL=256,(1<<256)-1
IV=(0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19)
K=(0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,
     0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
     0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,
     0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85)
PAD2 = bytes([128]) + bytes(55) + (512).to_bytes(8, "big")
def _ror(v,k):
	return ((v>>k)|(v<<(32-k)))&M32
def state_words(w,prefix=None):
	ws=_build_ws(w,prefix)
	for i in range(16,ROUNDS):
		x,y=ws[i-15],ws[i-2]
		ws.append((ws[i-16]+(_ror(x,7)^_ror(x,18)^(x>>3))+ws[i-7]+(_ror(y,17)^_ror(y,19)^(y>>10)))&M32)
	a,b,c,d,e,f,g,h=IV
	for i in range(ROUNDS):
		t1=(h+(_ror(e,6)^_ror(e,11)^_ror(e,25))+((e&f)^(~e&g))+K[i]+ws[i])&M32
		t2=((_ror(a,2)^_ror(a,13)^_ror(a,22))+((a&b)^(a&c)^(b&c)))&M32
		a,b,c,d,e,f,g,h=(t1+t2)&M32,a,b,c,(d+t1)&M32,e,f,g
	return [a,b,c,d,e,f,g,h]
def words_of(x):
	return [(x>>(32*(7-i)))&M32 for i in range(8)]
def int_of(w):
	return sum(w[i]<<(32*(7-i)) for i in range(8))
def _SIG0(a):
	return _ror(a,2)^_ror(a,13)^_ror(a,22)
def _SIG1(e):
	return _ror(e,6)^_ror(e,11)^_ror(e,25)
def _CH(e,f,g):
	return (e&f)^(~e&g)
def _MAJ(a,b,c):
	return (a&b)^(a&c)^(b&c)
def _anchor_prefix(anchors):
	a,b,c,d,e,f,g,h=IV
	pw=[]
	for i,av in enumerate(anchors):
		t2=(_SIG0(a)+_MAJ(a,b,c))&M32
		t1=(av-t2)&M32
		pw.append((t1-h-_SIG1(e)-_CH(e,f,g)-K[i])&M32)
		a,b,c,d,e,f,g,h=av,a,b,c,(d+t1)&M32,e,f,g
	return pw
TAILB=1
CIN=1
NTAIL=6 if TAILB else 4
PERM=(6,1,7,0,5,4,2,3,)
QM,XM=0x74a40866,0x46eb57e6
PRE,VARBASE,TAILMAP,OFFSET=8,8,{},set(range(10,16))
PREFIX_WORDS=tuple(_anchor_prefix([(K[9]-K[8])&M32,(-K[9])&M32,0,0,0,0,0,0]))
def _build_ws(w,prefix=None):
	prefix=PREFIX_WORDS if prefix is None else prefix
	ws=[0]*16
	for i in range(PRE):
		ws[i]=prefix[i]
	for k in range(8):
		ws[VARBASE+k]=(w[k]-(K[VARBASE+k] if VARBASE+k in OFFSET else 0))&M32
	for pos,v in TAILMAP.items():
		ws[pos]=v
	return ws
def _trace(w,prefix=None):
	ws=_build_ws(w,prefix)
	for i in range(16,ROUNDS):
		x,y=ws[i-15],ws[i-2]
		ws.append((ws[i-16]+(_ror(x,7)^_ror(x,18)^(x>>3))+ws[i-7]+(_ror(y,17)^_ror(y,19)^(y>>10)))&M32)
	a,b,c,d,e,f,g,h=IV
	A,E,T={0: a,-1: b,-2: c,-3: d},{0: e,-1: f,-2: g,-3: h},{}
	for i in range(ROUNDS):
		t1=(h+_SIG1(e)+_CH(e,f,g)+K[i]+ws[i])&M32
		t2=(_SIG0(a)+_MAJ(a,b,c))&M32
		a,b,c,d,e,f,g,h=(t1+t2)&M32,a,b,c,(d+t1)&M32,e,f,g
		A[i+1],E[i+1],T[i+1]=a,e,t1
	return ws,A,E,T
def enc_words(w,prefix=None):
	ws,A,E,T=_trace(w,prefix)
	r=ROUNDS
	if TAILB:
		bw=[E[r-3],E[r-2],A[r-7],A[r-6],(T[r-5]+_CH(A[r-6]^A[r-7],A[r-8],QM))&M32,T[r-4],
              (E[r-5]+_CH(E[r-2],XM,E[r-4])+ws[r-2])&M32,(E[r-4]+ws[r-1])&M32]
		return [bw[PERM[k]] for k in range(8)]
def enc_invert(enc):
	r=ROUNDS
	if TAILB:
		bw=[0]*8
		for k in range(8):
			bw[PERM[k]]=enc[k]
		e3,e2,a7,a6,Q,T4,X,Y=bw
		a5=(Q+(a6&a7&~QM)-(~a6&~a7&QM)+_SIG0(a6))&M32
		a4=(T4+_SIG0(a5)+_MAJ(a5,a6,a7))&M32
		a3=(e3-a7+_SIG0(a4)+_MAJ(a4,a5,a6))&M32
		a2=(e2-a6+_SIG0(a3)+_MAJ(a3,a4,a5))&M32
		t1=(X+(e2&e3&~XM)-(e2&~e3&XM)+_SIG1(e2)+K[r-2])&M32
		e1=(a5+t1)&M32
		a1=(t1+_SIG0(a2)+_MAJ(a2,a3,a4))&M32
		t0=(Y+_SIG1(e1)+_CH(e1,e2,e3)+K[r-1])&M32
		return [(t0+_SIG0(a1)+_MAJ(a1,a2,a3))&M32,a1,a2,a3,(a4+t0)&M32,e1,e2,e3]
def f_scalar(x,n=256):
	return int_of(enc_words(words_of(x)))&((1<<n)-1)
PAD2W = tuple(int.from_bytes(PAD2[4 * i:4 * i + 4], "big") for i in range(16))
def _kw2():
	ws=list(PAD2W)
	for i in range(16,ROUNDS):
		x,y=ws[i-15],ws[i-2]
		ws.append((ws[i-16]+(_ror(x,7)^_ror(x,18)^(x>>3))+ws[i-7]+(_ror(y,17)^_ror(y,19)^(y>>10)))&M32)
	return tuple((K[i]+ws[i])&M32 for i in range(ROUNDS))
_KW2=_kw2()
def digest_of_state(s):
	cv=[(u+v)&M32 for u,v in zip(IV,s)]
	a,b,c,d,e,f,g,h=cv
	for kw in _KW2:
		t1=(h+(((e>>6)|(e<<26))^((e>>11)|(e<<21))^((e>>25)|(e<<7)))+((e&f)^(~e&g))+kw)&M32
		t2=(((a>>2)|(a<<30))^((a>>13)|(a<<19))^((a>>22)|(a<<10)))+((a&b)^(a&c)^(b&c))
		a,b,c,d,e,f,g,h=(t1+t2)&M32,a,b,c,(d+t1)&M32,e,f,g
	return int_of([(u+v)&M32 for u,v in zip(cv,[a,b,c,d,e,f,g,h])])
def digest_of_g(o,qint):
	return digest_of_state(enc_invert(words_of(o^qint)))
def message(x):
	return b"".join(v.to_bytes(4, "big") for v in _build_ws(words_of(x)))
RP,RMASK=128,M32|(M32<<128)
WM,KM=0,30
def _rep(v):
	return v|(v<<RP)
class RecProg:
	def __init__(self):
		n=ROUNDS
		self.imm,self.init=[],[]
		MASK,T0,T1,T2,T3,T4=0,11,12,13,14,15
		ST,PB=list(range(1,9)),[9,10]
		W0,W1,W2,W3,WC0,WC1,WC2,WC3,E0,E1,WN=19,20,21,22,24,25,26,27,28,29,30
		def S(out,x,v):
			self.imm.append(v)
			out.append(("S", x, len(self.imm) - 1, 0))
		self.init.append(("R", 2, 0, 0))
		S(self.init,MASK,RMASK)
		S(self.init,WN,_rep(PREFIX_WORDS[0]))
		for i in range(10,n-6):
			S(self.init,T0,_rep(K[i]))
			self.init.append(("T", KM + i, T0, 2))
		constpos={i: PREFIX_WORDS[i] for i in range(1,PRE)}
		constpos.update(TAILMAP)
		for i in sorted(constpos):
			S(self.init,T0,_rep(constpos[i]))
			self.init.append(("T", WM + i, T0, 2))
		def sigma(out,dst,src,rs,shr,mask=True,dup=True):
			if dup:
				out += [("<", T0, src, 32), ("|", T0, src, T0)]
			out += [(">", dst, T0, rs[0]), (">", T1, T0, rs[1]), ("^", dst, dst, T1)]
			out += [(">", T1, src, shr) if shr else (">", T1, T0, rs[2]), ("^", dst, dst, T1)]
			if mask:
				out.append(("&", dst, dst, MASK))
		def rnd(out,st,pi,wreg,addrk):
			a,b,c,d,e,f,g,h=st
			P,PN=PB[pi],PB[1-pi]
			sigma(out,T2,e,(6,11,25),0,False)
			out += [("^", T3, f, g), ("&", T3, e, T3), ("^", T3, g, T3)]
			out += [("L", T0, addrk + KM, 0), ("+", T2, h, T2), ("+", T2, T2, T3), ("+", T2, T2, wreg), ("+", T2, T2, T0)]
			sigma(out,T3,a,(2,13,22),0,True)
			out += [("^", PN, a, b), ("&", T0, PN, P), ("^", T0, T0, b), ("+", T3, T3, T0)]
			out += [("+", h, d, T2), ("&", h, h, MASK), ("+", d, T2, T3), ("&", d, d, MASK)]
			return [d,a,b,c,h,e,f,g],1-pi
		assert WM==0
		body = [("L", W1, 1, 0)]
		sigma(body,E0,W1,(7,18,0),3,True)
		sigma(body,E1,W2,(17,19,0),10,False)
		body += [("+", W0, WN, E0), ("+", W0, W0, WC3), ("+", W0, W0, E1), ("&", W0, W0, MASK), ("T", 16, W0, 0)]
		body += [("L", W2, 2, 0), ("L", WC0, 10, 0)]
		sigma(body,E0,W2,(7,18,0),3,True)
		sigma(body,E1,W3,(17,19,0),10,False)
		body += [("+", W1, W1, E0), ("+", W1, W1, WC0), ("+", W1, W1, E1), ("&", W1, W1, MASK), ("T", 17, W1, 0)]
		body += [("L", W3, 3, 0), ("L", WC1, 11, 0)]
		sigma(body,E0,W3,(7,18,0),3,True)
		sigma(body,E1,W0,(17,19,0),10,False)
		body += [("+", W2, W2, E0), ("+", W2, W2, WC1), ("+", W2, W2, E1), ("&", W2, W2, MASK), ("T", 18, W2, 0)]
		body += [("L", WN, 4, 0), ("L", WC2, 12, 0), ("L", WC3, 13, 0)]
		sigma(body,E0,WN,(7,18,0),3,True)
		sigma(body,E1,W1,(17,19,0),10,False)
		body += [("+", W3, W3, E0), ("+", W3, W3, WC2), ("+", W3, W3, E1), ("&", W3, W3, MASK), ("T", 19, W3, 0)]
		st,pi=list(ST),0
		stl,pil=list(st),pi
		for j,wr in enumerate((WC0,WC1,WC2,WC3)):
			stl,pil=rnd(body,stl,pil,wr,10+j)
		assert stl == st and pil == pi, "the round loop does not rename back"
		ra,rb,rc,rd,re,rf,rg,rh=st
		def t1(out,dst,hr,er,fr,gr,wi,wreg=None,mask=True):
			sigma(out,T2,er,(6,11,25),0,False)
			out += [("^", T3, fr, gr), ("&", T3, er, T3), ("^", T3, gr, T3)]
			if wreg is None:
				out.append(("L", T4, WM + wi, 2))
				wreg=T4
			S(out,T0,_rep(K[wi]))
			out += [("+", T2, hr, T2), ("+", T2, T2, T3), ("+", T2, T2, wreg), ("+", T2 if mask else dst, T2, T0)]
			if mask:
				out.append(("&", dst, T2, MASK))
		tail=[]
		if TAILB:
			R5,QQ,E5,R4,E4,E3,E2,XX,YY=16,17,18,24,25,26,WC3,28,31
			t1(tail,R5,rh,re,rf,rg,n-6,None,False)
			tail += [("+", E5, rd, R5), ("&", E5, E5, MASK)]
			t1(tail,R4,rg,E5,re,rf,n-5,None,True)
			tail += [("+", E4, rc, R4), ("&", E4, E4, MASK)]
			t1(tail,T2,rf,E4,E5,re,n-4,W0,False)
			tail += [("+", E3, rb, T2), ("&", E3, E3, MASK)]
			t1(tail,T2,re,E3,E4,E5,n-3,W1,False)
			tail += [("+", E2, ra, T2), ("&", E2, E2, MASK)]
			S(tail,T0,_rep(XM))
			tail += [("^", T3, E4, T0), ("&", T3, E2, T3), ("^", T3, E4, T3), ("+", XX, E5, T3), ("+", XX, XX, W2), ("&", XX, XX, MASK)]
			tail += [("+", YY, E4, W3), ("&", YY, YY, MASK)]
			S(tail,T1,_rep(QM))
			tail += [("^", T0, ra, rb), ("^", T2, rc, T1), ("&", T0, T0, T2), ("^", T0, T1, T0), ("+", QQ, R5, T0), ("&", QQ, QQ, MASK)]
			fb=[E3,E2,rb,ra,QQ,R4,XX,YY]
			self.fin=[fb[PERM[k]] for k in range(8)]
		head=[]
		for k in range(8):
			if VARBASE+k in OFFSET:
				S(head,T0,_rep((-K[VARBASE+k])&M32))
				dst_reg=W2 if k==6 else (W3 if k==7 else self.fin[k])
				head += [("+", dst_reg, self.fin[k], T0), ("&", dst_reg, dst_reg, MASK)]
				head.append(("T", WM + VARBASE + k, dst_reg, 2))
			else:
				head.append(("T", WM + VARBASE + k, self.fin[k], 2))
		y0,y1=self.fin[0],self.fin[1]
		sigma(head,ST[4],y0,(6,11,25),0,False,dup=True)
		head += [("+", ST[4], ST[4], y1), ("&", ST[4], ST[4], MASK)]
		sigma(head,ST[0],y0,(2,13,22),0,False,dup=False)
		head += [("+", ST[0], ST[0], ST[4]), ("&", ST[0], ST[0], MASK)]
		head += [("|", ST[1], y0, ST[2]), ("|", ST[5], y0, ST[2]), ("|", PB[0], y0, ST[2])]
		self.blocks = [("S", head), ("L", body, 0, n - 16, 4), ("S", tail)]
		self.flat=[]
		for blk in self.blocks:
			if blk[0] == "S":
				self.flat+=blk[1]
			else:
				_,bd,start,count,stepw=blk
				self.flat += [("R", 0, start, 0), ("R", 1, start + count, 0)]
				top=len(self.flat)
				self.flat += bd + [("A", 0, stepw, 0), ("C", 0, 1, 0), ("J", top, 0, 0)]
		self.instr=len(self.init)+len(self.flat)
		self.mem=[0]*64
		self.regs=[0]*32
		self.run(self.init)
		self.mem0,self.regs0=list(self.mem),list(self.regs)
		self.ops=self.run(self.flat)
		self._compile()
	def run(self,recs):
		r,mem,p,flag,pc,cnt=self.regs,self.mem,[0,0,0],False,0,0
		while pc<len(recs):
			op,x,y,z=recs[pc]
			pc+=1
			cnt+=1
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
		def line(rc,pad,loop):
			op,x,y,z=rc
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
	def f(self,xs,fast=True):
		r,m=list(self.regs0),list(self.mem0)
		for k in range(8):
			r[self.fin[k]]=sum(((x>>(32*(7-k)))&M32)<<(RP*l) for l,x in enumerate(xs))
		if fast:
			self.fast(r,m)
		else:
			self.regs[:],self.mem[:]=r,m
			self.run(self.flat)
			r=self.regs
		return [sum(((r[self.fin[k]]>>(RP*l))&M32)<<(32*(7-k)) for k in range(8)) for l in range(len(xs))]
_REC=[]
def rec():
	if not _REC:
		_REC.append(RecProg())
	return _REC[0]
def packed_f(xs,n,qw=None):
	q=sum(qw[i]<<(32*i) for i in range(8)) if qw else 0
	return [(v^q)&((1<<n)-1) for v in rec().f(xs)]
def packed_ops(qw=None):
	return rec().ops
ZERO,ONE=(0,0),(0,1)
_ADD_HINTS=(0,)*33+(7,)+(0,)*26
EXPECTED_EMITTER_INFO=(43647,926,43904,185446,0,0,34228,5791,3628,174588,16384,43905,25856,60,256)
STATIC_SLP_SHA256="885c76492ea4caa497752afad7ae041f334bb55f1b776df41e7a50ae68f9b338"
STATIC_C_SHA256="0bfc40dec4de742c08e93e5b50f9ef55d4bef313f1ab3ad6d3c3c0cb882f0a4d"
STATIC_WASM_SHA256="4f506054fd8068c50ea61b21af8ead13d193660f82657f948ba16a75839e943b"
POLARITY_Q=int("e7309a100cc5bf67eea64df025e3b2545785e20fdeb3df8208948c9c227bb195",16)
class Gen:
	def __init__(self,n):
		self.n, self.nodes, self.calls = n, [("c",)], 0
		self.ahi=0
		self.inputs,self.cse=[],{}
		for j in range(n):
			self.nodes.append(("v", j))
			self.inputs.append((len(self.nodes)-1,0))
	def mk(self,op,a,b):
		self.calls+=1
		if a>b:
			a,b=b,a
		k=self.cse.get((op,a,b))
		if k is None:
			self.nodes.append((op,a,b))
			k=self.cse[(op,a,b)]=len(self.nodes)-1
		return k
	def _gate(self,node):
		if node<=self.n or node<len(self.nodes)-8:
			return None
		g=self.nodes[node]
		return g if g[0] in ("x","a","o") else None
	def XOR(self,x,y):
		self.calls+=1
		if x[0]==0:
			return (y[0],y[1]^x[1])
		if y[0]==0:
			return (x[0],x[1]^y[1])
		if x[0]==y[0]:
			return (0,x[1]^y[1])
		gx,gy=self._gate(x[0]),self._gate(y[0])
		inv=x[1]^y[1]
		if gx and gx[0]=="x" and y[0] in gx[1:]:
			return (gx[2] if gx[1]==y[0] else gx[1],inv)
		if gy and gy[0]=="x" and x[0] in gy[1:]:
			return (gy[2] if gy[1]==x[0] else gy[1],inv)
		if gx and gy and gx[0]==gy[0]=="x":
			common=set(gx[1:])&set(gy[1:])
			if common:
				c=next(iter(common))
				left=gx[2] if gx[1]==c else gx[1]
				right=gy[2] if gy[1]==c else gy[1]
				r=self.XOR((left,0),(right,0))
				return (r[0],r[1]^inv)
		return (self.mk("x", x[0], y[0]), x[1] ^ y[1])
	def AND(self,x,y):
		self.calls+=1
		if x[0]==0:
			return ZERO if x[1]==0 else y
		if y[0]==0:
			return ZERO if y[1]==0 else x
		if x[0]==y[0]:
			return x if x[1]==y[1] else ZERO
		if x[1]==0 and y[1]==0:
			return (self.mk("a", x[0], y[0]), 0)
		if x[1]==1 and y[1]==1:
			return (self.mk("o", x[0], y[0]), 1)
		p,q=(x,y) if x[1]==0 else (y,x)
		return self.XOR(p, (self.mk("a", p[0], q[0]), 0))
	def fa(self,a,b,c):
		ops=(a,b,c)
		cs=[t for t in ops if t[0]==0]
		vs=[t for t in ops if t[0]!=0]
		k=0
		for t in cs:
			k^=t[1]
		if len(vs)==3:
			for pi in range(3):
				o=[vs[j] for j in range(3) if j!=pi]
				if o[0][1]==o[1][1]:
					p,x,y=vs[pi],o[0],o[1]
					break
			u=self.XOR(x,p)
			return self.XOR(u,y),self.XOR(self.AND(u,self.XOR(y,p)),p)
		if len(vs)==2:
			x,y=vs
			t=self.XOR(x,y)
			s=(t[0],t[1]^k)
			if x[1]==y[1]:
				if k==0:
					return s,self.AND(x,y)
				cr=self.AND((x[0],x[1]^1),(y[0],y[1]^1))
				return s,(cr[0],cr[1]^1)
			nt=(t[0],t[1]^1)
			xx=x if x[1]==nt[1] else y
			if k==0:
				return s,self.AND(xx,nt)
			xx=x if x[1]==t[1] else y
			cr=self.AND((xx[0],xx[1]^1),(t[0],t[1]^1))
			return s,(cr[0],cr[1]^1)
		if len(vs)==1:
			x=vs[0]
			k1,k2=cs[0][1],cs[1][1]
			return (x[0],x[1]^k),(ONE if k1==k2==1 else ZERO if k1==k2==0 else x)
		kk=cs[0][1]+cs[1][1]+cs[2][1]
		return (ZERO if kk%2==0 else ONE),(ONE if kk>=2 else ZERO)
	def add(self,A,B,cin=ZERO):
		s,c=[],cin
		for i in range(32):
			if i==31:
				s.append(self.XOR(self.XOR(A[i],B[i]),c))
			else:
				si,c=self.fa(A[i],B[i],c)
				s.append(si)
		return s
	def OR(self,x,y):
		r=self.AND((x[0],x[1]^1),(y[0],y[1]^1))
		return (r[0],r[1]^1)
	def _col(self,x,y,z,u,U,tm,oU):
		X,A,O=self.XOR,self.AND,self.OR
		if tm==1:
			w=X(y,U); n8=X(z,w); s=X(x,n8); n6=O(U,X(y,u))
			return s,(None if oU else X(n6,w)),X(n6,A(n8,X(x,w)))
		if tm==2:
			w5=X(x,y); w6=X(z,w5); s=X(U,w6); w9=X(u,w6)
			w10=O(U,(w9[0],w9[1]^1)); w11=O(w5,X(x,z))
			return s,(None if oU else X(w6,(w10[0],w10[1]^1))),X(w10,(w11[0],w11[1]^1))
		n5=X(z,U); n9=X(x,n5); s=X(y,n9); n6=X(x,y); n8=O(U,X(z,u)); n11=A((n6[0],n6[1]^1),n9)
		return s,(None if oU else X(n5,n11)),X(n8,n11)
	def add3(self,A,B,C,cin=0):
		s=[None]*32
		if cin==0:
			s[0],U=self.fa(A[0],B[0],C[0])
			u=ZERO
		elif cin==2:
			s[0],c0=self.fa(A[0],B[0],C[0])
			u,U=ONE,(c0[0],c0[1]^1)
		else:
			ops=(A[0],B[0],C[0])
			for pi in range(3):
				o=[ops[j] for j in range(3) if j!=pi]
				if o[0][1]==o[1][1]:
					p,x,y=ops[pi],o[0],o[1]
					break
			u0=self.XOR(x,p)
			s[0]=self.XOR(u0,(y[0],y[1]^1))
			u,U=p,self.OR(u0,self.XOR(y,p))
		for i in range(1,31):
			t=(A[i],B[i],C[i])
			pt=U[1]^u[1]
			if t[0][1]==t[1][1]==t[2][1]:
				o,tm=t,(1 if t[0][1]==pt else 2)
			else:
				for zi in range(3):
					if t[zi][1]==pt:
						r0,r1=[t[j] for j in range(3) if j!=zi]
						if r0[1]==(u[1]^1):
							o,tm=(r1,r0,t[zi]),0
						elif r1[1]==(u[1]^1):
							o,tm=(r0,r1,t[zi]),0
						else:
							o,tm=(r0,t[zi],r1),1
						break
			s[i],u,U=self._col(*o,u,U,tm,i==30)
		s[31]=self.XOR(self.XOR(self.XOR(A[31],B[31]),C[31]),U)
		return s
	def _baseline(self,cv,vs,force_bb=None):
		bb=force_bb if force_bb is not None else (max(range(len(vs)),key=lambda k: (_tz((cv-k)&M32),-k)) if CIN and cv else 0)
		used_b=0
		while len(vs)>2:
			c3=min(bb-used_b,2)
			used_b+=c3
			vs=[self.add3(*vs[:3],c3)]+vs[3:]
		s=vs[0]
		for w in vs[1:]:
			c1=1 if used_b<bb else 0
			used_b+=c1
			s=self.add(s,w,ONE if c1 else ZERO)
		cv=(cv-used_b)&M32
		if cv:
			out=self.add(s,_constw(cv))
			sp=getattr(self,"split",None)
			if sp is not None:
				sp[tuple(out)]=(s,cv)
			return out
		return s
	def _choice(self,op,mask):
		pick=[op[i] for i in range(len(op)) if (mask>>i)&1]
		rest=[op[i] for i in range(len(op)) if not ((mask>>i)&1)]
		first=self.add3(*pick)
		if not rest:
			return first
		if len(rest)==1:
			return self.add(first,rest[0])
		if len(rest)==2:
			return self.add3(first,*rest)
		raise AssertionError("unsupported selector arity")
	def addm(self,*ws,force_bb=None):
		cv,vs=0,[]
		for w in ws:
			if all(x[0]==0 for x in w):
				cv+=sum(x[1]<<i for i,x in enumerate(w))
			else:
				vs.append(w)
		cv&=M32
		if not vs:
			return _constw(cv)
		call_id=self.ahi
		self.ahi+=1
		hint=_ADD_HINTS[call_id]
		if hint and force_bb is None:
			op=list(vs)+([_constw(cv)] if cv else [])
			assert hint<(1<<len(op)) and hint.bit_count()==3
			return self._choice(op,hint)
		return self._baseline(cv,list(vs),force_bb)
	def xorw(self,A,B):
		return [self.XOR(a,b) for a,b in zip(A,B)]
def _tz(v):
	return 32 if v==0 else (v&-v).bit_length()-1
def _constw(v):
	return [ONE if (v>>i)&1 else ZERO for i in range(32)]
def _sigma(g,A,r1,r2,r3,shift):
	out=[]
	for j in range(32):
		t=g.XOR(A[(j+r1)%32],A[(j+r2)%32])
		out.append(g.XOR(t,(A[j+r3] if j+r3<32 else ZERO) if shift else A[(j+r3)%32]))
	return out
def _add_u(g,A,u,cin=0):
	s,c=[],ZERO
	for i in range(32):
		if i==0:
			if cin:
				s.append((u[0][0],u[0][1]^1)); c=g.OR(A[0],u[0])
			else:
				s.append(u[0]); c=g.AND(A[0],(u[0][0],u[0][1]^1))
		elif i==31:
			s.append(g.XOR(u[31],c))
		else:
			s.append(g.XOR(u[i],c))
			w=g.XOR(A[i],c)
			if u[i][0] and w[0] and u[i][0]!=w[0] and u[i][1]!=w[1]:
				c=g.XOR(g.AND((u[i][0],u[i][1]^1),w),c)
			else:
				c=g.XOR(g.AND(u[i],w),A[i])
	return s
def _t1hg(g,e,f,gg,h,hg,Wd,d=None):
	sp = getattr(g, "split", {})
	fg=[g.XOR(f[j],gg[j]) for j in range(32)]
	tt=[g.AND(e[j],fg[j]) for j in range(32)]
	u=[g.XOR(hg[j],tt[j]) for j in range(32)]
	S1=_sigma(g,e,6,11,25,False)
	cv,vs=0,[S1]
	for w in Wd:
		if all(x[0]==0 for x in w):
			cv+=sum(x[1]<<i for i,x in enumerate(w))
		else:
			vs.append(w)
	cv&=M32
	has_h=any(x[0]!=0 for x in h)
	has_d=d is not None and any(x[0]!=0 for x in d)
	if has_h and cv and len(vs)==2:
		pref_u=1 if (h[0][0] and u[0][0] and h[0][1]==u[0][1]) else 0
		cands=[(vs[1],cv)]
		if tuple(vs[1]) in sp:
			s_raw,cv_rem=sp[tuple(vs[1])]
			cands.append((s_raw,(cv+cv_rem)&M32))
		best=None
		for w_cand,cv_cand in cands:
			for cin_u in (0,1):
				for c3 in (0,1,2):
					for d_ in ((0,1) if has_d else (0,)):
						tot=cin_u+c3+d_
						score=(2*_tz((cv_cand-tot)&M32)+int(cin_u==pref_u),-tot,-d_)
						if best is None or score>best[0]:
							best=(score,cin_u,c3,d_,w_cand,cv_cand)
		_,cin_u,c3,delta,w_best,cv_best=best
		t=_add_u(g,h,u,cin_u)
		s=g.add3(t,vs[0],w_best,c3)
		cv2=(cv_best-cin_u-c3-delta)&M32
		return (g.add(s,_constw(cv2)) if cv2 else s),fg,delta
	t=_add_u(g,h,u,0)
	return g.addm(t,S1,*Wd),fg,0
def _rnd2(g,st,Wd):
	a,b,c,d,e,f,gg,h,prev,hg=st
	t1,fg,delta=_t1hg(g,e,f,gg,h,hg,Wd,d)
	S0=_sigma(g,a,2,13,22,False)
	ab,mj=[],[]
	for j in range(32):
		ab.append(g.XOR(a[j],b[j]))
		if c[j]==ZERO:
			mj.append(g.AND(a[j],b[j]))
		elif ab[j][0] and prev[j][0] and ab[j][0]!=prev[j][0] and ab[j][1]!=prev[j][1]:
			mj.append(g.XOR(g.AND((ab[j][0],ab[j][1]^1),prev[j]),c[j]))
		else:
			mj.append(g.XOR(g.AND(ab[j],prev[j]),b[j]))
	ne=g.add(d,t1,ONE if delta else ZERO)
	na=g.add3(t1,S0,mj,delta) if delta else g.addm(t1,S0,mj)
	return (na,a,b,c,ne,e,f,gg,ab,fg)
def _ch_direct(g,e,f,gg):
	ch=[]
	for j in range(32):
		fg_j=g.XOR(f[j],gg[j])
		if e[j][0] and fg_j[0] and e[j][1]!=fg_j[1]:
			ch.append(g.XOR(f[j],g.AND((e[j][0],e[j][1]^1),fg_j)))
		else:
			ch.append(g.XOR(gg[j],g.AND(e[j],fg_j)))
	return ch
def _net_u(G=Gen):
	g=G(256)
	g.split={}
	Y=[[g.inputs[32*(7-k)+j] for j in range(32)] for k in range(8)]
	W=[None]*16
	for i in range(PRE):
		W[i]=_constw(PREFIX_WORDS[i])
	for k in range(8):
		pos=VARBASE+k
		W[pos]=g.addm(Y[k],_constw((-K[pos])&M32)) if pos in OFFSET else Y[k]
	for pos,val in TAILMAP.items():
		W[pos]=_constw(val)
	wd=lambda i: (Y[i-VARBASE],) if i in OFFSET else (_constw(K[i]),W[i])
	v=[_constw(w) for w in IV]
	st=tuple(v)+([g.XOR(v[1][j],v[2][j]) for j in range(32)],[g.XOR(v[7][j],v[6][j]) for j in range(32)])
	r=ROUNDS
	for i in range(r):
		if i>=16 and i<r-2:
			w_m7=(Y[i-15],_constw((-K[i-7])&M32)) if i in (17,21) else ((g.split[tuple(W[16])][0],_constw(g.split[tuple(W[16])][1])) if i==23 else (W[i-7],))
			fb=2 if i==23 else None
			W.append(g.addm(W[i-16],_sigma(g,W[i-15],7,18,3,True),*w_m7,_sigma(g,W[i-2],17,19,10,True),force_bb=fb))
		elif i>=r-2:
			W.append(g.add3(W[i-16],_sigma(g,W[i-15],7,18,3,True),W[i-7]))
		if i<r-NTAIL:
			st=_rnd2(g,st,wd(i))
	if TAILB:
		a6,a7,a8,a9,e6,e7,e8,e9,prev,hg=st
		T5,fg,_=_t1hg(g,e6,e7,e8,e9,hg,(_constw(K[r-6]-1),W[r-6]))
		e5=g.add(a9,T5,ONE)
		mj=[g.OR((ab[0],ab[1]^1),a8[j]) if (QM>>j)&1 else g.AND(ab,a8[j]) for j in range(32) for ab in (g.XOR(a6[j],a7[j]),)]
		Q=g.add(T5,mj,ONE)
		T4,fg,_=_t1hg(g,e5,e6,e7,e8,fg,wd(r-5))
		e4=g.add(a8,T4)
		e3=g.addm(a7,e7,_ch_direct(g,e4,e5,e6),_sigma(g,e4,6,11,25,False),*wd(r-4))
		e2=g.addm(a6,e6,_ch_direct(g,e3,e4,e5),_sigma(g,e3,6,11,25,False),*wd(r-3))
		X=g.addm(W[r-2],_sigma(g,W[r-4],17,19,10,True),e5,[g.OR(e2[j],e4[j]) if (XM>>j)&1 else g.AND((e2[j][0],e2[j][1]^1),e4[j]) for j in range(32)])
		Y_out=g.addm(W[r-1],_sigma(g,W[r-3],17,19,10,True),e4)
		bw=[e3,e2,a7,a6,Q,T4,X,Y_out]
		out=[bw[PERM[k]] for k in range(8)]
		assert g.ahi==len(_ADD_HINTS)
		return g,[t for w in out for t in w]

MAX_NODES=43905
MAX_RECORDS=43647
CSE_PROBE_LIMIT=8

class BGen(Gen):
	def __init__(self,n,run,pas):
		self.n,self.run,self.pas,self.calls=n,run,pas,0
		self.ahi=0
		self.inputs=[(j+1,0) for j in range(n)]
		self.nn,self.rn,self.ncse,self.max_probe=n+1,0,0,0
		self.recent,self.cse_k,self.cse_v=[None]*8,[0]*1024,[None]*1024
	def _gate(self,node):
		for d in range(min(8,self.rn)):
			r=self.recent[(self.rn-1-d)&7]
			if r[3]==node:
				return r[:3]
		return None
	def _new(self,op,a,b):
		k,self.nn=self.nn,self.nn+1
		if k>=MAX_NODES:
			self.run.err=1
			return 0
		if self.pas==0:
			if self.run.uses[a]==255 or self.run.uses[b]==255:
				self.run.err=6
			self.run.uses[a]+=1
			self.run.uses[b]+=1
		else:
			self.run.alloc(op,k,a,b)
		return k
	def mk(self,op,x,y):
		self.calls+=1
		if x>y:
			x,y=y,x
		a,b=x,y
		if b<=256:
			key=({"x":1,"a":2,"o":3}[op])|(a<<2)|(b<<11)
			p=((key*2654435761)&M32)>>22
			probes=1
			while self.cse_k[p]:
				if self.cse_k[p]==key:
					self.max_probe=max(self.max_probe,probes)
					return self.cse_v[p]
				p=(p+1)&1023
				probes+=1
				if probes>CSE_PROBE_LIMIT:
					self.run.err=16
					return 0
			self.max_probe=max(self.max_probe,probes)
			self.ncse+=1
			if self.ncse>900:
				self.run.err=10
			s=self._new(op,a,b)
			self.cse_k[p],self.cse_v[p]=key,s
		else:
			for d in range(min(8,self.rn)):
				r=self.recent[(self.rn-1-d)&7]
				if r[:3]==(op,a,b):
					return r[3]
			s=self._new(op,a,b)
		self.recent[self.rn&7]=(op,a,b,s)
		self.rn+=1
		return s

class BoundedEmitter:
	def __init__(self):
		self.uses,self.err,self.records=[0]*MAX_NODES,0,[]
	def emit(self,op,d,a,b):
		if len(self.records)>=MAX_RECORDS or max(d,a,b)>=1024:
			self.err=5
			return
		self.records.append((op,d,a,b))
	def take(self,prefer=None,p=0):
		if prefer is not None and self.free>>prefer&1:
			r=prefer
		else:
			m=self.free&~p or self.free
			if not m:
				self.err=8
				return 0
			r=(m&-m).bit_length()-1
		self.free&=~(1<<r)
		return r
	def alloc(self,op,k,x,y):
		self.uses[x]-=1
		self.uses[y]-=1
		dx,dy=self.uses[x]==0,self.uses[y]==0
		want=256+self.order[self.co][1] if self.co<len(self.order) and self.order[self.co][0]==k else None
		borrow=~(self.pend if k<self.f0-30 else self.pend&((1<<448)-1)) if self.uses[k]<=3 and k<self.f1-200 and want is None else self.pend
		dst=None
		if want is not None:
			if self.free>>want&1:
				dst=self.take(want)
			elif dx and self.reg[x]==want:
				dst=want
			elif dy and self.reg[y]==want:
				dst=want
		if dst is None:
			if dx and (not (borrow>>self.reg[x]&1) or self.reg[x]==want):
				dst=self.reg[x]
			elif dy and (not (borrow>>self.reg[y]&1) or self.reg[y]==want):
				dst=self.reg[y]
		if dx and self.reg[x]!=dst:
			self.free|=1<<self.reg[x]
		if dy and self.reg[y]!=dst:
			self.free|=1<<self.reg[y]
		if dst is None:
			dst=self.take(p=borrow)
		if dst==want:
			self.pend&=~(1<<dst)
		self.emit({"x":1,"a":2,"o":3}[op],dst,self.reg[x],self.reg[y])
		self.reg[k]=dst
		while self.co<len(self.order) and self.order[self.co][0]==k:
			self.oreg[self.order[self.co][1]]=dst
			self.co+=1
		if not self.uses[k]:
			self.err=9
			self.free|=1<<dst
	def run(self):
		g0,out0=_net_u(lambda n:BGen(n,self,0))
		nodes,self.calls=g0.nn,g0.calls
		self.onode=[x[0] for x in out0]
		self.oneg=[x[1] for x in out0]
		self.order=sorted((n,i) for i,n in enumerate(self.onode) if n)
		for n,_ in self.order:
			self.uses[n]+=1
		self.f0,self.f1=self.order[0][0],self.order[32][0]
		self.free=sum(1<<r for r in range(REGISTERS) if r<256 or r>=512)
		self.pend=sum(1<<(256+i) for i,n in enumerate(self.onode) if n)
		self.reg={n:INREG(n-1) for n in range(1,257)}
		self.oreg,self.co=[0]*256,0
		while self.co<len(self.order) and self.order[self.co][0]<=256:
			n,i=self.order[self.co]
			self.oreg[i]=INREG(n-1)
			self.co+=1
		for n in range(1,257):
			if not self.uses[n]:
				self.free|=1<<INREG(n-1)
		g1,out1=_net_u(lambda n:BGen(n,self,1))
		self.calls+=g1.calls
		self.max_probe=max(g0.max_probe,g1.max_probe)
		assert out1==out0 and self.max_probe<=CSE_PROBE_LIMIT
		todo=[(i,self.oreg[i]) for i,n in enumerate(self.onode) if n and self.oreg[i]!=256+i]
		moves=0
		while todo:
			srcs=[s for _,s in todo]
			k=next((k for k,(i,s) in enumerate(todo) if 256+i not in srcs),None)
			if k is None:
				s,t=todo[0][1],self.take()
				self.emit(4,t,s,0)
				moves+=1
				todo=[(i,t if r==s else r) for i,r in todo]
			else:
				i,s=todo.pop(k)
				self.emit(4,256+i,s,0)
				moves+=1
		for i,n in enumerate(self.onode):
			if not n:
				self.emit(5,256+i,self.oneg[i],0)
		top=max(max(r[1:4]) if r[0]<=3 else max(r[1:3]) if r[0]==4 else r[1] for r in self.records)+1
		q=sum(self.oneg[i]<<(32*(7-i//32)+i%32) for i in range(256) if self.onode[i])
		counts=[sum(r[0]==op for r in self.records) for op in (1,2,3)]
		info=(len(self.records),top,nodes,self.calls,moves,self.err,*counts,4*MAX_RECORDS,COUNTERS,MAX_NODES,GEN_STATE_BYTES,len(_ADD_HINTS),GEN_CONSTANT_BYTES)
		return info,q,self.records

def _encode_body(records):
	out=bytearray()
	for op,d,a,b in records:
		assert 1<=op<=3 and max(d,a,b)<1024
		out+=((op-1)|(d<<2)|(a<<12)|(b<<22)).to_bytes(4,"little")
	return bytes(out)

def bounded_check(pr):
	info,q,records=BoundedEmitter().run()
	py=[({"^":1,"&":2,"|":3,"M":4,"S":5}[o],d,a,b) for o,d,a,b in pr.recs]
	assert info==EXPECTED_EMITTER_INFO
	assert q==pr.qint==POLARITY_Q and records==py
	assert hashlib.sha256(GEN_C.encode()).hexdigest()==STATIC_C_SHA256
	stream=_encode_body(records)
	digest=hashlib.sha256(stream).hexdigest()
	assert len(stream)==4*pr.instr and digest==STATIC_SLP_SHA256
	return info,digest

def _alloc(g,nin,fixed,outs,tgt,free0,E):
	nodes=g.nodes
	uses=[0]*len(nodes)
	for k in range(nin+1,len(nodes)):
		uses[nodes[k][1]]+=1
		uses[nodes[k][2]]+=1
	want={}
	for i,o in enumerate(outs):
		if o[0]:
			uses[o[0]]+=1
			want.setdefault(o[0],tgt[i])
	oids=sorted(want)
	f0,f1=oids[0],oids[32]
	reg=dict(fixed)
	st=dict(free=sum(1<<r for r in free0 if r not in fixed.values()),pend=sum(1<<tgt[i] for i,o in enumerate(outs) if o[0]),moves=0)
	def take(prefer=None,p=0):
		f = st["free"]
		if prefer is not None and f>>prefer&1:
			r=prefer
		else:
			m=f&~p or f
			assert m, "out of registers"
			r=(m&-m).bit_length()-1
		st["free"] &= ~(1 << r)
		return r
	def release(r):
		st["free"] |= 1 << r
	for v,r in fixed.items():
		if uses[v]==0:
			release(r)
	for k in range(nin+1,len(nodes)):
		op,x,y=nodes[k]
		uses[x]-=1
		uses[y]-=1
		dying=[v for v in (x,y) if uses[v]==0]
		w,dst=want.get(k),None
		p = ~(st["pend"] if k < f0 - 30 else st["pend"] & ((1 << 448) - 1)) if (uses[k] <= 3 and k < f1 - 200 and w is None) else st["pend"]
		if w is not None:
			if st["free"] >> w & 1:
				dst=take(w)
			elif any(reg[v]==w for v in dying):
				dst=w
		if dst is None:
			for v in dying:
				if not p>>reg[v]&1 or reg[v]==w:
					dst=reg[v]
					break
		for v in dying:
			if reg[v]!=dst:
				release(reg[v])
		if dst is None:
			dst=take(p=p)
		reg[k]=dst
		if dst==w:
			st["pend"] &= ~(1 << w)
		E(({"x": "^", "a": "&", "o": "|"}[op], dst, reg[x], reg[y]))
		if uses[k]==0:
			raise AssertionError("dead gate")
	todo=[(i,reg[o[0]]) for i,o in enumerate(outs) if o[0] and reg[o[0]]!=tgt[i]]
	while todo:
		srcs=[s for _,s in todo]
		k=next((k for k,(i,s) in enumerate(todo) if tgt[i] not in srcs),None)
		if k is None:
			s=todo[0][1]
			tmp=take()
			E(("M", tmp, s, 0))
			st["moves"] += 1
			todo=[(j,tmp if u==s else u) for j,u in todo]
			continue
		i,s=todo.pop(k)
		E(("M", tgt[i], s, 0))
		st["moves"] += 1
	for i,o in enumerate(outs):
		if o[0]==0:
			E(("S", tgt[i], 1 if o[1] else 0, 0))
	return st["moves"]
def INREG(j):
	return 256+32*(7-j//32)+j%32
def assemble():
	info,q,records=BoundedEmitter().run()
	assert info[4:6]==(0,0)
	_QM[:]=[q]
	R=[({1:"^",2:"&",3:"|"}[op],d,a,b) for op,d,a,b in records]
	return R,info[4],info[3]
class Prog:
	def __init__(self):
		self.recs,self.moves,self.calls=assemble()
		self.q=[0]*256
		self.qint=_QM[0]
		self.qwords=[(self.qint>>(32*i))&M32 for i in range(8)]
		self.pin=[0]*256
		self.instr=self.kernel=len(self.recs)
		self.nregs = max(max(r[1:3]) if r[0] in "NM" else max(r[1:4]) if r[0] in "^&|" else r[1] for r in self.recs) + 1
		self.compile()
	def run(self,pc,end,regs):
		recs,n=self.recs,0
		while pc<end:
			op,d,a,b=recs[pc]
			pc+=1
			n+=1
			if op == "^":
				regs[d]=regs[a]^regs[b]
			elif op == "&":
				regs[d]=regs[a]&regs[b]
			elif op == "|":
				regs[d]=regs[a]|regs[b]
			elif op == "N":
				regs[d]=regs[a]^ALL
			elif op == "M":
				regs[d]=regs[a]
			elif op == "S":
				regs[d]=ALL if a else 0
		return n
	def compile(self):
		f = {"^": "r[%d] = r[%d] ^ r[%d]", "&": "r[%d] = r[%d] & r[%d]", "|": "r[%d] = r[%d] | r[%d]", "N": "r[%d] = r[%d] ^ ALL", "M": "r[%d] = r[%d]", "S": "r[%d] = ALL if %d else 0"}
		ns, fs = {"ALL": ALL}, []
		for a in range(0,len(self.recs),4096):
			exec(compile("def c(r):" + chr(10) + "".join("    " + (f[o] % ((d, x, y) if o in "^&|" else (d, x))) + chr(10) for o, d, x, y in self.recs[a:a + 4096]), "<program>", "exec"), ns)
			fs.append(ns["c"])
		self.ns=ns
		def step(r):
			for c in fs:
				c(r)
		self.fast=step
	def step(self,*planes):
		regs=[0]*REGISTERS
		for j,pl in enumerate(planes):
			regs[INREG(j)]=pl
		self.fast(regs)
		return [regs[INREG(j)] for j in range(len(planes))]
def _tmasks():
	res,s={},128
	while s:
		m=0
		for c in range(256):
			if not c&s:
				m|=1<<c
		res[s]=m
		s>>=1
	return res
_TM=_tmasks()
def transpose(rows):
	R=list(rows)+[0]*(256-len(rows))
	s=128
	while s:
		m=_TM[s]
		for i in range(256):
			if not i&s:
				t=((R[i]>>s)^R[i+s])&m
				R[i+s]^=t
				R[i]^=t<<s
		s>>=1
	return R
def pack_lanes(xs,n,pin):
	T=transpose(xs)
	return [T[j]^(ALL if pin[j] else 0) for j in range(n)]
def lanes_of(planes,n,pin):
	T=transpose([planes[j]^(ALL if pin[j] else 0) for j in range(n)])
	return T[:256]
def lane_value(planes,l,pin,n):
	x=0
	for j in range(n):
		x|=(((planes[j]>>l)&1)^pin[j])<<j
	return x
def set_lane(planes,l,x,pin,n):
	bit=1<<l
	return [(planes[j]&~bit)|((((x>>j)&1)^pin[j])<<l) for j in range(n)]
LAMBDA=Fraction(497,1000)
CUTLOSS=Fraction(15,100000)
TAIL_AGES=1e-6
CMAX=6
P_MIN=0.390000001
GRAIN=10**21
STAGE1_PLANES=20
LOOP_OPS=3
HIT_OPS=2800
EVENT_OPS=3800
CUT_OPS=4200
SLICE_OPS=1300
RECOVER_EXTRA=39
INSTR_BYTES=5
BODY_BYTES=4
REC_RECORD_BYTES=5
GEN_INSTR_BYTES=36
HANDLER_CODE,SETUP_CODE,RECOVERY_CODE=1000,160,47
REGISTERS=926
REGFILE=REGISTERS*32
COUNTERS=16384
ARRAYS=64*32
KEYB=48
SLOTB=KEYB
MEM_LIMIT=1<<20
ADVICE=0
KAPPA_256=13
WASM_RUN_OPERATORS=92_997_536
WASM_OPERATOR_FACTOR=2
WASM_EMITTER_INSTR=5979
GEN_STATE_ARRAYS=dict(recent=8*16,cse_k=1024*4,cse_v=1024*4,free=32*4,pending=32*4,
	W=16*32*4,WS=16*32*4,WCV=16*4,V=10*32*4,Y=8*32*4,word_scratch=14*32*4,
	X2_AM_A3=3*32*4,TB=11*32*4,tail_scratch=4*32*4,AW=8*4,
	output_arrays=6*256*4,output_polarities=256,info=15*4+32,scalars=17*4,alignment=128)
GEN_CONSTANT_ARRAYS=dict(IV=8*4,K=40*4,PW=8*4,PERM=8*4)
GEN_STATE_BYTES=sum(GEN_STATE_ARRAYS.values())
GEN_CONSTANT_BYTES=sum(GEN_CONSTANT_ARRAYS.values())
assert GEN_STATE_BYTES==25856 and GEN_CONSTANT_BYTES==256
GEN_SCRATCH=MAX_NODES+GEN_STATE_BYTES+len(_ADD_HINTS)+GEN_CONSTANT_BYTES+4096
SETUP_FIXED=256*3100+20000
OFFSET_SEARCH_EVALS=64+1+3*192+1000
SELECTOR_THREE_WORD_SITES=32
SELECTOR_FOUR_WORD_SITES=15
SELECTOR_ALTERNATIVES=SELECTOR_THREE_WORD_SITES+SELECTOR_FOUR_WORD_SITES*(4+6)
SELECTOR_SEARCH_EVALS=1+2*SELECTOR_ALTERNATIVES
SEARCH_EVAL_OPS=1<<48
OFFSET_SEARCH_OPS=OFFSET_SEARCH_EVALS*SEARCH_EVAL_OPS
SELECTOR_SEARCH_OPS=SELECTOR_SEARCH_EVALS*SEARCH_EVAL_OPS
SEARCH_IMAGE_INSTR=10_000
SEARCH_LOCAL_BYTES=65_536
OFFSET_SEARCH_PEAK=SEARCH_IMAGE_INSTR*GEN_INSTR_BYTES+GEN_SCRATCH+SEARCH_LOCAL_BYTES+48
SELECTOR_SEARCH_PEAK=SEARCH_IMAGE_INSTR*GEN_INSTR_BYTES+GEN_SCRATCH+SEARCH_LOCAL_BYTES+len(_ADD_HINTS)
CFG={16: dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),18: dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),
       256: dict(s1=20,W=102,kappa=KAPPA_256,Sb=1<<48)}
def stage1_ops(pin,s1):
	npos=sum(1 for j in range(s1) if not pin[j])
	nneg=s1-npos
	ops=max(npos-1,0)+max(nneg-1,0)
	if nneg:
		ops+=2 if npos else 1
	return ops+1+2
def stage1(planes,s1,pin):
	nz=0
	pos=[planes[j] for j in range(s1) if not pin[j]]
	neg=[planes[j] for j in range(s1) if pin[j]]
	if pos:
		acc=pos[0]
		for q in pos[1:]:
			acc|=q
		nz|=acc
	if neg:
		acc=neg[0]
		for q in neg[1:]:
			acc&=q
		nz|=acc^ALL
	return ALL^nz
def inflight_m(lanes=LANES,eps=TAIL_AGES):
	m=lanes
	while True:
		x=m/lanes
		if exp(-lanes*(x-1-log(x)))<=eps:
			return m
		m+=1
INFLIGHT=inflight_m()
def _plan(n,Tp,kappa,tmax,Sb):
	c=CFG[n]
	s1, W = c["s1"], c["W"]
	N,D=1<<n,s1+W
	L=Fraction(1<<D,Tp)
	if n==256:
		B=_b256(Tp,tmax,kappa,Sb)
	else:
		ureq=isqrt(2*N*LAMBDA.numerator//LAMBDA.denominator)+2
		num,den=ureq+INFLIGHT*L+1,CUTLOSS.denominator
		q=-(-(num*den)//(den-CUTLOSS.numerator))
		B=-(-q//LANES)
	cc=-(-kappa*L.numerator//L.denominator)
	fb=(Tp-1).bit_length()
	return dict(n=n,s1=s1,W=W,D=D,Tp=Tp,fb=fb,kb=min(KEYB-fb,n-D),L=L,N=N,Q=B*LANES,B=B,kappa=kappa,Sb=Sb,
                c=cc,capr=cc+Sb,tmax=tmax,e2max=2*B*LANES//(1<<s1)+64,
                cmax=CMAX if n==256 else 10**9)
def tail_log2(mean,k):
	return (-mean+k*(1+log(mean/k)))/log(2)
_PROG=[]
_QM=[0]
def prog():
	global REGFILE
	if not _PROG:
		_PROG.append(Prog())
		REGFILE=32*(_PROG[0].nregs+3)
	return _PROG[0]
def other_code(pr=None):
	return HANDLER_CODE+rec().instr+RECOVERY_CODE+SETUP_CODE
def machine_constants(pr=None):
	pr=pr or prog()
	filt=stage1_ops(pr.pin,STAGE1_PLANES)
	code=pr.instr*BODY_BYTES+rec().instr*REC_RECORD_BYTES+(filt+LOOP_OPS+HANDLER_CODE+RECOVERY_CODE+SETUP_CODE)*INSTR_BYTES
	return pr.kernel,filt,pr.kernel+filt+LOOP_OPS,code,8*(MEM_LIMIT-code-REGFILE-COUNTERS-ADVICE-ARRAYS)//SLOTB-LANES-CMAX
def table_bytes(tmax):
	return-(-(tmax+LANES+CMAX)*SLOTB//8)

def boundary_test(pr,p):
	stream=_encode_body([({"^":1,"&":2,"|":3}[o],d,a,b) for o,d,a,b in pr.recs])
	assert len(stream)==4*pr.instr and all(max(r[1:])<1024 for r in pr.recs)
	max_key=(((1<<p["kb"])-1)<<p["fb"])|(p["Tp"]-1)
	assert 0<max_key+1<1<<KEYB
	assert p["tmax"]+LANES+CMAX<1<<18
	rp=rec()
	control=rp.init+rp.flat
	assert len({r[0] for r in control})<=16 and all(max(r[1:])<1024 for r in control)
	assert table_bytes(p["tmax"])==-(-(p["tmax"]+LANES+CMAX)*SLOTB//8)
	return dict(body_bytes=len(stream),max_register=max(max(r[1:]) for r in pr.recs),max_key=max_key,
		max_trail=p["tmax"]+LANES+CMAX-1,control_opcodes=len({r[0] for r in control}),control_max_field=max(max(r[1:]) for r in control))
def phase_bytes(code,tmax):
	prog()
	setup=code+COUNTERS+REGFILE+ARRAYS+WASM_EMITTER_INSTR*GEN_INSTR_BYTES+GEN_SCRATCH
	search=code+COUNTERS+REGFILE+ARRAYS+table_bytes(tmax)
	return setup,search
def search_envelopes():
	gate_ops=1024
	raw=2*160*64*32*13*13*12*gate_ops
	assert 2*raw<SEARCH_EVAL_OPS
	assert OFFSET_SEARCH_EVALS==1641 and SELECTOR_ALTERNATIVES==182 and SELECTOR_SEARCH_EVALS==365
	return raw,raw
def plan(n,kappa=None,Tp=None):
	if n!=256:
		c=CFG[n]
		p = _plan(n, c["Tp"], c["kappa"], 0, c["Sb"])
		p["tmax"] = 4 * (p["Q"] // int(p["L"])) + 64
		return p
	kappa=kappa or KAPPA_256
	tmax=machine_constants()[4]
	if Tp:
		return _plan(256, Tp, kappa, tmax, CFG[256]["Sb"])
	lo,hi=1.0,float(tmax-59)
	for _ in range(60):
		mid=(lo+hi)/2
		lo,hi=(mid,hi) if tail_log2(mid,tmax-59)<=-20 else (lo,mid)
	a,z=1,4097
	while z-a>1:
		m=(a+z)//2
		a, z = (m, z) if _lossq(m, lo, tmax, kappa, CFG[256]["Sb"])["P_lower"] >= P_MIN else (a, m)
	return _plan(256, a, kappa, tmax, CFG[256]["Sb"])
def ledger(p=None,pr=None):
	p=p or plan(256)
	pr=pr or prog()
	search_envelopes()
	ph,filt,body,code,_=machine_constants(pr)
	emitter=WASM_OPERATOR_FACTOR*WASM_RUN_OPERATORS+1
	parts = dict(main=body * p["B"],
                 slices=-(-p["B"] // p["Sb"]) * SLICE_OPS,
                 stage1_hits=p["e2max"] * HIT_OPS,
                 events=(p["tmax"]+1) * (EVENT_OPS + 6 * (p["tmax"] + LANES + CMAX)),
                 cuts=p["cmax"] * CUT_OPS,
                 recovery=2 * p["capr"] * (packed_ops() + RECOVER_EXTRA) + 600 + len(rec().init),
			 setup=SETUP_FIXED+emitter,
			 offset_search=OFFSET_SEARCH_OPS,
			 selector_search=SELECTOR_SEARCH_OPS)
	return dict(parts=parts,total=sum(parts.values()),plan=p,body=body,emitter=emitter)
TB=18
FINE,COARSE=20000,2000
def _lossq(Tp,q,tmax,kappa,Sb,rate=1.0):
	from math import expm1
	D=122
	L=Fraction(1<<D,Tp)
	c=-(-kappa*L.numerator//L.denominator)
	th,Lf,cf=Tp/2.0**D,float(L),float(c)
	Q,B,Np=q*Lf,q*Lf/LANES,2.0**256/rate
	k=int(q)+1
	while tail_log2(q,k)>-40:
		k+=1
	n2,shift=k+LANES+CMAX,1/(1-k*Q/Np)
	pi=lambda m: exp(-m*(m-1)/(2*Np))
	split=max(1.0,Q-120*LANES*Lf)
	edges=[split*i/COARSE for i in range(COARSE+1)]+[split+(Q-split)*i/FINE for i in range(1,FINE+1)]
	delay,pa=0.0,1.0
	for b in edges[1:]:
		pb=pi(b)
		delay+=(pa-pb)*exp(-th*max(0.0,B-b/LANES))
		pa=pb
	p,ql,hq=exp(-cf*th),Q*Lf/Np,Q*(Q-1)/(2*Np)
	p2=exp(-(cf-1)*th)*(1+(cf-1)*th/(1-th))
	hh=(Q*(Q-1)/2+2.0**TB*Q)/Np
	cuts=1-sum(comb(n2,j)*p**j*exp((n2-j)*log1p(-p)) for j in range(CMAX+1))
	t=dict(no_collision=pi(Q)*shift,delay=delay*shift,partner_own_trail=ql,
             partner_cut_trail=(cf+Sb)*Q*p*(q+LANES)/((1-p)*Np),too_old=hq*p2,
             rest_of_path=hq*Lf*(Q+2.0**TB)/Np,finished_count=2.0**-40,
             cut_halt=cuts+ql*(1+(2+kappa)*exp(-kappa/2)+2*hq)+hq*p*(3+2*kappa),
             key_false_match=tmax*(tmax-1)/2*2.0**-(min(KEYB-(Tp-1).bit_length(),256-D)+log2(Tp)),
             table_capacity=2.0**tail_log2(q,tmax-59),
             misc=Q*2.0**TB/Np+k*k*Lf/Np+255*Q/Np+exp(min(700.0,-300+(exp(5)-1)*hh))+2.0**-90)
	t["sum"] = sum(t.values())
	t["P_lower"] = 1 - t["sum"]
	t.update(trails=q,k=k)
	return t
_B={}
def _b256(Tp,tmax,kappa,Sb):
	if (Tp,tmax,kappa) not in _B:
		L=Fraction(1<<122,Tp)
		lo,hi=1.0,float(tmax-59)
		for _ in range(50):
			mid=(lo+hi)/2
			lo,hi=(mid,hi) if tail_log2(mid,tmax-59)<=-15.5 else (lo,mid)
		q_hi=lo
		lo,hi=1.0,q_hi
		for _ in range(40):
			mid=(lo+hi)/2
			lo, hi = (lo, mid) if _lossq(Tp, mid, tmax, kappa, Sb)["P_lower"] >= P_MIN else (mid, hi)
		B=-(-int(hi*L/LANES)//GRAIN)*GRAIN
		while _lossq(Tp, float(B * LANES / L), tmax, kappa, Sb)["P_lower"] < P_MIN:
			B+=GRAIN
		_B[(Tp,tmax,kappa)]=B
	return _B[(Tp,tmax,kappa)]
def loss(p,rate=1.0):
	return _lossq(p["Tp"], float(p["Q"] / p["L"]), p["tmax"], p["kappa"], p["Sb"], rate)
class Halt(Exception):
	pass
class DigestNet:
	def __init__(self,qint):
		assert TAILB
		g=Gen(256)
		E=[[(g.inputs[32*(7-k)+j][0],(qint>>(32*(7-k)+j))&1) for j in range(32)] for k in range(8)]
		S0=lambda x: _sigma(g,x,2,13,22,False)
		S1=lambda x: _sigma(g,x,6,11,25,False)
		mj=lambda a,b,c: [g.XOR(g.AND(g.XOR(a[j],b[j]),g.XOR(b[j],c[j])),b[j]) for j in range(32)]
		ch=lambda e,f,gv: [g.XOR(gv[j],g.AND(e[j],g.XOR(f[j],gv[j]))) for j in range(32)]
		neg=lambda x: [(s[0],s[1]^1) for s in x]
		bw=[None]*8
		for k in range(8):
			bw[PERM[k]]=E[k]
		e3,e2,a7,a6,Q,T4,X,Y=bw
		a5=g.addm(Q,[ZERO if (QM>>j)&1 else g.AND(a6[j],a7[j]) for j in range(32)],neg([g.AND((a6[j][0],a6[j][1]^1),(a7[j][0],a7[j][1]^1)) if (QM>>j)&1 else ZERO for j in range(32)]),_constw(1),S0(a6))
		a4=g.addm(T4,S0(a5),mj(a5,a6,a7))
		a3=g.addm(e3,neg(a7),_constw(1),S0(a4),mj(a4,a5,a6))
		a2=g.addm(e2,neg(a6),_constw(1),S0(a3),mj(a3,a4,a5))
		t1=g.addm(X,[ZERO if (XM>>j)&1 else g.AND(e2[j],e3[j]) for j in range(32)],neg([g.AND(e2[j],(e3[j][0],e3[j][1]^1)) if (XM>>j)&1 else ZERO for j in range(32)]),_constw((1+K[ROUNDS-2])&M32),S1(e2))
		e1=g.add(a5,t1)
		a1=g.addm(t1,S0(a2),mj(a2,a3,a4))
		t0=g.addm(Y,S1(e1),ch(e1,e2,e3),_constw(K[ROUNDS-1]))
		st=[g.addm(t0,S0(a1),mj(a1,a2,a3)),a1,a2,a3,g.add(a4,t0),e1,e2,e3]
		cv=[g.addm(w,_constw(v)) for w,v in zip(st,IV)]
		a,b,c,d,e,f,gg,h=cv
		for kw in _KW2:
			t1=g.addm(h,S1(e),ch(e,f,gg),_constw(kw))
			t2=g.add(S0(a),mj(a,b,c))
			a,b,c,d,e,f,gg,h=g.add(t1,t2),a,b,c,g.add(d,t1),e,f,gg
		dw=[g.add(x,y) for x,y in zip(cv,[a,b,c,d,e,f,gg,h])]
		self.out=[dw[7-i//32][i%32] for i in range(256)]
		ops, N = {"x": "^", "a": "&", "o": "|"}, g.nodes
		last,slot,free,src,m={},list(range(257))+[0]*(len(N)-257),[],[],257
		for k in range(257,len(N)):
			last[N[k][1]]=last[N[k][2]]=k
		for s in self.out:
			last[s[0]]=len(N)
		for k in range(257,len(N)):
			o,x,y=N[k]
			free+=[slot[z] for z in {x,y} if last[z]==k]
			if free:
				slot[k]=free.pop()
			else:
				slot[k],m=m,m+1
			src.append("    v[%d] = v[%d] %s v[%d]" % (slot[k], slot[x], ops[o], slot[y]))
			if k not in last:
				free.append(slot[k])
		self.out=[(slot[s[0]],s[1]) for s in self.out]
		ns,self.fs={},[]
		for i in range(0,len(src),4096):
			exec(compile("def c(v):" + chr(10) + chr(10).join(src[i:i + 4096]) + chr(10), "<digest>", "exec"), ns)
			self.fs.append(ns["c"])
		self.nn=m
	def step(self,planes,k=256,a=ALL):
		v=[0]*self.nn
		v[1:257]=planes
		for c in self.fs:
			c(v)
		return [v[s[0]]^(a if s[1] else 0) for s in self.out[:k]]
_DN=[]
def dnet():
	if not _DN:
		_DN.append(DigestNet(prog().qint))
	return _DN[0]
class Engine:
	def __init__(self,n):
		self.n,self.pr,self.pin=n,prog(),[0]*n
	def _low(self,o):
		return digest_of_g(o,self.pr.qint)&((1<<self.n)-1)
	def step(self,*planes):
		return dnet().step(list(self.pr.step(*(list(planes)+[0]*(256-len(planes))))))[:self.n]
	def wstep(self,P):
		n,a,ns=self.n,(1<<256*len(P))-1,self.pr.ns
		W=[sum(q[j]<<256*i for i,q in enumerate(P)) for j in range(n)]
		ns["ALL"] = a
		o=dnet().step(self.pr.step(*(W+[0]*(256-n))),n,a)
		ns["ALL"] = ALL
		return [[(x>>256*i)&ALL for x in o] for i in range(len(P))]
	def f2(self,xs):
		return [self._low(o) for o in packed_f(xs,256,self.pr.qwords)]
	def g_scalar(self,x):
		return digest_of_state(state_words(words_of(x)))&((1<<self.n)-1)
def is_dp(x,p):
	return x & ((1 << p["s1"]) - 1) == 0 and (x >> p["s1"]) & ((1 << p["W"]) - 1) < p["Tp"]
def dp_key(x,p):
	return (((x >> p["D"]) & ((1 << p["kb"]) - 1)) << p["fb"]) | ((x >> p["s1"]) & ((1 << p["fb"]) - 1))
def trail_length(p,x,f2):
	for l in range(1, p["capr"] + 1):
		x=f2([x])[0]
		if is_dp(x,p):
			return l
	raise Halt("recovery length")
def recover(p,r,a,b,f2):
	mask = p["N"] - 1
	if a[1]<b[1]:
		a,b=b,a
	if a[1] > p["capr"]:
		raise Halt("recovery length")
	xs=[(r+a[0])&mask,(r+b[0])&mask]
	for _ in range(a[1]-b[1]):
		xs[0]=f2([xs[0]])[0]
	if xs[0]==xs[1]:
		return None
	for _ in range(b[1]+1):
		ya,yb=f2(xs)
		if ya==yb:
			if p["n"] == 256:
				s0,s1=enc_invert(words_of(f_scalar(xs[0]))),enc_invert(words_of(f_scalar(xs[1])))
				assert s0 == s1 == state_words(words_of(xs[0])), "encoding collision is not a state collision"
			return xs[0],xs[1]
		xs=[ya,yb]
	return None
def search(eng,p,r,cnt):
	g,x=_search(eng,p,r,cnt),None
	try:
		while True:
			x=g.send(x and eng.step(*x))
	except StopIteration as e:
		return e.value
def _search(eng,p,r,cnt):
	n, mask, pin = p["n"], p["N"] - 1, eng.pin
	table,births,ts,nxt=[],[0]*LANES,list(range(LANES)),LANES
	planes=pack_lanes([(r+t)&mask for t in ts],n,pin)
	cnt["inserts"] += LANES
	batches=0
	while batches < p["B"]:
		planes=list((yield planes))
		batches+=1
		cnt["batches"] += 1
		hit = stage1(planes, p["s1"], pin)
		while hit:
			cnt["stage1_hits"] += 1
			if cnt["stage1_hits"] > p["e2max"]:
				raise Halt("stage-1 budget")
			l=(hit&-hit).bit_length()-1
			hit&=hit-1
			x=lane_value(planes,l,pin,n)
			if is_dp(x,p):
				key,length=dp_key(x,p),batches-births[l]
				cnt["finished"] += 1
				w=key+1
				if w in table:
					t0=table.index(w)
					cnt["recoveries"] += 1
					res=recover(p,r,(t0,trail_length(p,(r+t0)&mask,eng.f2)),(ts[l],length),eng.f2)
					if res is None:
						raise Halt("recovery found no pair")
					return res
				if cnt["finished"] > p["tmax"]:
					raise Halt("table full")
				assert 0<w<1<<KEYB and ts[l] < p["tmax"] + LANES + p["cmax"]
				table+=[0]*(ts[l]+1-len(table)); table[ts[l]]=w
				ts[l],nxt,births[l]=nxt,nxt+1,batches
				planes=set_lane(planes,l,(r+ts[l])&mask,pin,n)
				cnt["inserts"] += 1
		if batches % p["Sb"] == 0:
			for l in range(LANES):
				if batches - births[l] >= p["c"]:
					cnt["cut"] += 1
					if cnt["cut"] > p["cmax"]:
						raise Halt("cut budget")
					ts[l],nxt,births[l]=nxt,nxt+1,batches
					planes=set_lane(planes,l,(r+ts[l])&mask,pin,n)
					cnt["inserts"] += 1
	return None
class Counters(dict):
	def __missing__(self,k):
		return 0
def derive(seed,tag,bits=256):
	return int.from_bytes(hashlib.shake_256(("%s/%s" % (seed, tag)).encode()).digest((bits + 7) // 8), "little") & ((1 << bits) - 1)
def attempt(eng,p,seed,tag):
	cnt=Counters()
	try:
		res = search(eng, p, derive(seed, tag, p["n"]), cnt)
	except Halt as e:
		cnt["halt"] += 1
		res=None
	return res,cnt
N_T3=16
M_T2,B_T2=256,16
RF_W,RF_DP_BITS,RF_GROUPS,RF_LANES,RF_CAP,RF_BIN,RF_REF=20,5,128,2,2048,512,48
def e1_rows(trials):
	eng,p,G,C,R,cur=Engine(N_T3),plan(N_T3),{},{},{},{}
	def adv(i,v):
		try:
			cur[i]=G[i].send(v)
			return
		except StopIteration as e:
			R[i]=e.value
		except Halt:
			C[i]["halt"] += 1
		del cur[i]
	for i,t in enumerate(trials):
		C[i]=Counters()
		G[i] = _search(eng, p, derive(t["seed"], "t", p["n"]), C[i])
		adv(i,None)
	while cur:
		ks=list(cur)
		for i,o in zip(ks,eng.wstep([cur[i] for i in ks])):
			adv(i,o)
	return [e1_obs(R.get(i),C[i]) for i in range(len(trials))]
def e1_obs(res,cnt):
	obs = dict(target_ok=int(res is not None), batches=cnt["batches"], halt=cnt["halt"])
	return (None,None,obs) if res is None else (message(res[0]),message(res[1]),obs)
def e2_trial(seed,tr,st):
	src,z=tr%3,[0]*256
	if src==0:
		xs = [derive(seed, "u%d" % i) for i in range(M_T2)]
	elif src==1:
		r = derive(seed, "r")
		xs=[(r+i)&ALL for i in range(M_T2)]
	else:
		xs, cur = [], [derive(seed, "c%d" % l) for l in range(LANES)]
		for _ in range(M_T2//LANES):
			cur=lanes_of(list(st.step(*pack_lanes(cur,256,st.pin))),256,st.pin)
			xs+=cur
	digs=[]
	for b in range(M_T2//LANES):
		digs+=lanes_of(dnet().step(list(st.step(*pack_lanes(xs[b*LANES:(b+1)*LANES],256,st.pin)))),256,z)
	first,pair={},None
	for i,d in enumerate(digs):
		c=d&((1<<B_T2)-1)
		if c in first and xs[first[c]]!=xs[i] and pair is None:
			pair=(xs[first[c]],xs[i])
		first.setdefault(c,i)
	obs=dict(source=src,dup_w0=len(digs)-len(first))
	return (None,None,obs) if pair is None else (message(pair[0]),message(pair[1]),obs)
def _rf_bin(step):
	return 4 if step is None else min((step-1)//RF_BIN,3)
def _rf_reference(seed):
	import random
	rng=random.Random(seed)
	mask=(1<<RF_W)-1
	roots=[rng.randrange(mask+1) for _ in range(RF_GROUPS)]
	states=[[r,(r+1)&mask] for r in roots];seen=[set(x) for x in states]
	trail=[[0,1] for _ in roots];nxt=[2]*RF_GROUPS;slots=[[] for _ in roots]
	mapping={};stop=[None]*RF_GROUPS;steps=[0]*RF_GROUPS;glob=set();dp=fresh=0
	for _ in range(RF_CAP//RF_LANES):
		for g in range(RF_GROUPS):
			for lane in range(RF_LANES):
				if stop[g] is not None:continue
				steps[g]+=1;x=states[g][lane]
				new=x not in glob
				if new:glob.add(x);fresh+=1
				if x not in mapping:mapping[x]=rng.randrange(mask+1)
				y=mapping[x];isdp=(y&((1<<RF_DP_BITS)-1))==0
				if new and isdp:dp+=1
				if y in seen[g]:stop[g]=steps[g];continue
				seen[g].add(y)
				if isdp:
					t=trail[g][lane];word=(y>>RF_DP_BITS)+1
					if len(slots[g])<=t:slots[g]+=[0]*(t+1-len(slots[g]))
					slots[g][t]=word;z=(roots[g]+nxt[g])&mask;trail[g][lane]=nxt[g];nxt[g]+=1
					if z in seen[g]:stop[g]=steps[g]
					else:seen[g].add(z);states[g][lane]=z
				else:states[g][lane]=y
	bins=[0]*5
	for x in stop:bins[_rf_bin(x)]+=1
	return bins,dp,fresh
def rf_model_rows(trials,st):
	assert len(trials)>=RF_GROUPS
	mask=(1<<RF_W)-1
	roots=[derive(trials[g]["seed"],"rf20/%d"%trials[g]["trial"],RF_W) for g in range(RF_GROUPS)]
	states=[]
	seen=[]
	trail=[]
	nxt=[]
	slots=[]
	steps=[0]*RF_GROUPS
	stop=[None]*RF_GROUPS
	for r in roots:
		states += [r,(r+1)&mask]
		seen.append({r,(r+1)&mask})
		trail.append([0,1])
		nxt.append(2)
		slots.append([])
	dp=fresh=inserts=matches=0;glob=set()
	pl=pack_lanes(states,256,st.pin)
	for _ in range((RF_CAP+RF_LANES-1)//RF_LANES):
		yy=lanes_of(list(st.step(*pl)),256,st.pin)
		for g in range(RF_GROUPS):
			for lane in range(RF_LANES):
				i=RF_LANES*g+lane
				if stop[g] is not None or steps[g]>=RF_CAP:
					states[i]=0
					continue
				steps[g]+=1
				x=states[i];new=x not in glob
				if new:glob.add(x);fresh+=1
				y=yy[i]&mask
				isdp=(y&((1<<RF_DP_BITS)-1))==0
				if new and isdp:dp+=1
				if isdp:
					word=(y>>RF_DP_BITS)+1
					assert 0<word<1<<(RF_W-RF_DP_BITS+1)
					if word in slots[g]:
						matches+=1
				if y in seen[g]:
					stop[g]=steps[g]
					states[i]=0
					continue
				seen[g].add(y)
				if isdp:
					t=trail[g][lane]
					if len(slots[g])<=t:
						slots[g] += [0]*(t+1-len(slots[g]))
					slots[g][t]=word
					inserts+=1
					z=(roots[g]+nxt[g])&mask
					trail[g][lane]=nxt[g]
					nxt[g]+=1
					if z in seen[g]:
						stop[g]=steps[g]
						states[i]=0
					else:
						seen[g].add(z)
						states[i]=z
				else:
					states[i]=y
		pl=pack_lanes(states,256,st.pin)
		if all(x is not None for x in stop):
			break
	bins=[0]*5
	for x in stop:
		bins[_rf_bin(x)]+=1
	hold=int.from_bytes(hashlib.sha256("".join("%s/%s;"%(t["seed"],t["trial"]) for t in trials[RF_GROUPS:]).encode()).digest()[:8],"little")
	null=[_rf_reference(derive(str(hold),"e%d"%i,64)) for i in range(RF_REF)]
	sums=[sum(x[0][j] for x in null) for j in range(5)];expect=[x/RF_REF for x in sums]
	stat=lambda b,e:sum((x-y)**2/y for x,y in zip(b,e))
	chi2=stat(bins,expect)
	nchi=[stat(x[0],[(s-v)/(RF_REF-1) for s,v in zip(sums,x[0])]) for x in null]
	px=(1+sum(x>=chi2 for x in nchi))/(RF_REF+1)
	p=1/(1<<RF_DP_BITS)
	z=lambda d,f:(d-p*f)/(p*(1-p)*f)**0.5
	dp_z=z(dp,fresh);pz=(1+sum(abs(z(d,f))>=abs(dp_z) for _,d,f in null))/(RF_REF+1)
	assert all(e>=5 for e in expect) and px>=.05 and pz>=.05
	assert matches<=sum(x is not None for x in stop)
	stats=dict(w=RF_W,groups=RF_GROUPS,ens=RF_REF,hold=hold&0xffffffff,b0=bins[0],b1=bins[1],b2=bins[2],b3=bins[3],b4=bins[4],
		x2=round(chi2,6),px=round(px,6),dp=dp,fresh=fresh,z=round(dp_z,6),pz=round(pz,6))
	rows=[]
	for i in range(len(trials)):
		obs={"included":int(i<RF_GROUPS)}
		if i==0:
			obs.update(stats)
		rows.append((None,None,obs))
	return rows
def serve(req):
	eid, out = req["experiment_id"], []
	bounded_check(prog())
	if eid == "bssha-n16":
		rows = e1_rows(req["trials"])
	elif eid == "proj-k0-w256":
		st=prog()
		rows = [e2_trial(t["seed"], t["trial"], st) for t in req["trials"]]
	elif eid == "rf-model-r20":
		rows=rf_model_rows(req["trials"],prog())
	else:
		raise ValueError("unknown experiment")
	for t, (a, b, obs) in zip(req["trials"], rows):
		out.append({"trial": t["trial"], "message_a_hex": a.hex() if a else None, "message_b_hex": b.hex() if b else None, "observations": obs})
	return {"schema_version": 1, "trials": out}
def text():
	return "".join("%s %d %d %d\n" % r for r in prog().recs)
def selftest():
	import random
	r=random.Random(3);p=prog();info,h=bounded_check(p);bt=boundary_test(p,plan(256))
	g,o=_net_u();ref=[]
	m=_alloc(g,256,{j+1:INREG(j) for j in range(256)},o,[256+i for i in range(256)],range(REGISTERS),ref.append)
	enc=lambda z:_encode_body([({"^":1,"&":2,"|":3}[a],b,c,d) for a,b,c,d in z])
	assert m==0 and enc(ref)==enc(p.recs)
	assert max(max(x[1:]) for x in p.recs)<REGISTERS and all(x[0] in "^&|" for x in p.recs)
	for xs in [[r.getrandbits(256) for _ in range(256)] for _ in range(8)]+[[0]*256,[ALL]*256]:
		assert lanes_of(list(p.step(*pack_lanes(xs,256,p.pin))),256,p.pin)==[f_scalar(x)^p.qint for x in xs]
	for _ in range(10000):
		w=[r.getrandbits(32) for _ in range(8)];assert enc_invert(enc_words(w))==state_words(w)
	regs=[0]*REGISTERS
	for j in range(256):regs[INREG(j)]=r.getrandbits(256)
	a=list(regs);assert p.run(0,len(p.recs),regs)==p.kernel;p.fast(a)
	assert [a[INREG(j)] for j in range(256)]==[regs[INREG(j)] for j in range(256)]
	cur=[r.getrandbits(256) for _ in range(256)];pl=pack_lanes(cur,256,p.pin)
	for _ in range(4):
		pl=list(p.step(*pl));cur=[f_scalar(x)^p.qint for x in cur]
	assert lanes_of(pl,256,p.pin)==cur
	e=Engine(N_T3);xs=[r.getrandbits(N_T3) for _ in range(256)]
	pl=pack_lanes(xs,N_T3,e.pin)
	for _ in range(5):
		pl=list(e.step(*pl));xs=[e.g_scalar(x) for x in xs]
	assert lanes_of(pl,N_T3,e.pin)==xs
	xs=[r.getrandbits(256) for _ in range(2)];f=[f_scalar(x) for x in xs]
	assert packed_f(xs,256)==f==rec().f(xs,False) and packed_f(xs[:1],256)==f[:1]
	assert rec().f([0,ALL])==[f_scalar(0),f_scalar(ALL)] and packed_f(xs,256,p.qwords)==[x^p.qint for x in f]
	rows=[r.getrandbits(256) for _ in range(256)];assert transpose(transpose(rows))==rows
	assert (transpose(rows)[5]>>9)&1==(rows[9]>>5)&1
	xs=[r.getrandbits(256) for _ in range(256)]
	assert lanes_of(dnet().step(list(p.step(*pack_lanes(xs,256,p.pin)))),256,[0]*256)==[digest_of_state(state_words(words_of(x))) for x in xs]
	q,found=plan(N_T3),0
	for s in range(6):
		z,_=attempt(e,q,"selftest/%d"%s,"t")
		if z is not None:found+=1;assert z[0]!=z[1] and e.g_scalar(z[0])==e.g_scalar(z[1])
	assert found
	print(info,h,bt,p.instr,"ok",True)
	return True
def print_ledger(lg):
	print({k: (str(v) if isinstance(v, Fraction) else v) for k, v in lg["plan"].items()})
	print("body",lg["body"])
	for k, v in lg["parts"].items():
		print(k,v)
	print("N =", lg["total"])
	print("time %.5f %.8f"%(log2(lg["total"]/UNIT)+5e-6,log2(lg["total"]/UNIT)))
GEN_C=__import__('lzma').decompress(__import__('base64').b85decode(b'{Wp48S^xk9=GL@E0stWa761SMbT8$j;6#ZSpIrbt9!f+7EcWv7Lz|0s4)@dlRYKFC%Ru5;*dPDz@ko%eHoL=sDmUb#(BDY$sOdRsL4LgFV@TvGnBm&qgMo4zu5ydt#a_wlag8km7c3&3P#27C*NI2Qu}m1VM^g_ikpdyw(SygoG^QlmXBy}zDzE9kX}eHZfcWEW>;&MgGxg>pE@&f{?}Y<&)F2CP0Ef$BIg3hGOcsR8v=+nK=WL&0wRKirzPC=viDgl{g4zTs0k8+);>b!urzPQf_pw)dT1M7$)+p>{=-;3a#Br<()JaRQB7&-M&QYah`?CgTdxV_TnvRW87xB})6G-jSS_p9Bdg3TQU0E283|AJB@dH9|x4%7YDK%te`loSOEkFV)J}64iKW7HNgsCeW&pQ83%AYFK9O%>Jv{%6Gtv=Y-5rj;w<HuqFjIBBgHHbxdiPvcD8;x~g0VW(m??*bW4aCV)GeOxpAKicyAdSdaJ9<@hg{pk6Ed$MW$c-k0Z}<ySj-MUI;T0kl{tFUHgEMh`uXq;Bjp!YLCPNI(<qpI~e^8}$3j{vkmU`R-u?HKe+i^ro@LYML244bZ8@ig$vtUdh2NnT20px$vVFON;DK!6L%o1VCk%G}j`MrC{=#C?dQ5G+ecdl%-;c;$MS*>Y9R~07s_q!iADWk)WnZ5B4s?_14BY;xBaQa<n>C3;G*1JE!Wd9x#ZTNhm8v*3uv7zXB;?fkfTpiFbxFnvz#!H3;{*gRyP3f6zd-KsGS>pHM1|cFeD)^V~O@;{Mgp`@UU$obsz327?Ul_FBk&3gnmx&6m5x^Qgk76!^cM@;Kfm}N}Ep={;CTv*KG0d(PM$}E=D{5=G$oSgr{1&lIiZH-w8J~mD`R6iMF5JI08esNLL$WYFr7r!g6^l-v&lhOgoTbtpGv33{h$0H(BK*#`ZT2vrHMS-PZIiXLCGxh{OV#o-xbSb9Q6x1y_Sd@dumgLv%jC!pKtP1O#=WBW$VJCofe~843oh}T)d!oqHWkrgfx`PkMy}&nCs6|RP&J*}GDN}-QJW#M@hLy~cz30zBOC>t?~YEJE3&88h+MpqOH2VODQgd?361=>FtrGgrtr}5k^+4fqA#zSMINY37zioKYVLyeAPa%Du&k&1h)2i>V6yK0gFJWj&7a~DKd&dvDco)OO8weo^cx2fqinr>=!sWLN3qYrH*6|J>SOfi1ZaZe!8UU7_g!04ev%3)1R4@S6grC(1bxvO)V0GFHEA))tdy;x&2HmLp6HYIb{+c8Ovl{CEUQ<$y$KjGNku{oy$GKZQLrnln@xx)ltkd+G{xWP933~j{}jz-_HOJj7o>D(P=5qv=(I2Rdc_u^tads!A5Jb3DV*+sjT=^RqWyxK)Ztq*EYx5xPt<O3+!X&gv_2)di*{5F>N}Zi=!<x`Kl+7Kz7YKD1i$V44w1Qg?n9gFbNYNOfc9(w{?5}oTg8)wi|!_RB<8;TZCtV`P`}#L=PvDjBx3~eX4LXa%fLCnp`#zV&9w)d$@OI-^kEy$oA1qtsTeFYJuF|)0@>uQfUw64&N9gXs>?$GfF8fR5?#YoIGk4hDZG&E=gP@sf?+DjE8b-CFx8|iSxRH?Js61WxToP}UAdFqT6v~6%*jy#BG3_zuc5X>9XaxcwCU^9!~j0fB?Z&o@pU%Ot_;g%ck3=e(QabqWl*xIIHb7^r0ic6Kt{A7P$0}K!3GOU#`4w3P8nr15-u?p%bW4tg7naI6$)V=6buc5$d@&yvdd+6izU94jo%I;BBD_4^PVw<^I<o`4P)TE+-Wb&)EC*)hKRbSf~z4WQ+&m&m!@Y#?C_o<zPd84mMyp(S=UWRTW{I8M><DoM)gA0NVqnAZ?rqEuVJp}aSn&YFKkcQ7PNCP{1Sz2uDsl)&N<14oqK-OQ?NOp4~v4>#JEgH>K?jHWzu-LUK^!>PmTSOmt^d}Xy-nH8V8q23f8`Q3gE)*#T>;<tcqdzBe$^C0k1~AVuf{o>zf-&p!=zRO=T{noaCL33KnQ8OLpIALdqgATBEvoBu~w>GY{=5HaxWv4@SOMVSNS!j;^AB1wEfS-;!N<dRqEYzPOWtEz*fwQaR#(8<b~7nDO=@GQ}BtZG*LGY3cReI*qtCre&6&NC^TXRI&1t;lcMhmI7j<9Mg{rfIu{kvJq(f{)<{qMy{|he-xiJaeA3Mno%gD3;`4aoQ5&_uF}nfsQ6o=z0jV+sElZ>$l}d_#zjx;S5_m^LG7`%n7h<%Lt{+_H%@OBnj+(=trYOUv7tfb%ChD9SEB>d2L~~2RL9s2C7fD^gp^u%^|9wtugtlrh!@H7FvgaWI)Ufpaq3YgA;>iUtiWp`8>1bxA^?1uUGv_teo?qng2d7P$)}7Qt8425VK-V^Wl1M$NNF{OHTdlXL$62W<iClmy5mJ7I}iQV-QlM`P5a=cP1wzYyr_V>kpxT@J@k^>$LagG=H=g~WjuVMNi(*AM!W=U8ZEH=7Qwmv)ZGrIlVpkYYq3ZQA($vFo6@&u2;X&gQ`%x2rfPnj+CiMRa+Fm2A>Y4=<v)lDv(*#Vk8T8Gy*SF}p;?F!Pb;cGB7$QBz+}CeB*5(wRprwLp)ityY;KWa{*dCpi(5<_BMnqgS!NF#JwK7vD#5x3-p7=Ch!Lg7#46`xmU8mzitC+Cq#~Bt*Xq2{h*uVsNRa*Z<)CCdv}i!{Rrwr@tX}wiSv)Eq`w^^-gDj|)n@}s>LZ4=LpI19zn?Gbe8gS70=R;VZHZg7eGo#I4Z8DK~LQz!}*O1#Xr6|3IDN<0wk*@Z%&bB1tqT|0HXs>^l^6mVy>&sR5442uo*yMPUVd<F?<_*fZ_lRaSVy~Pnc&VvyEakB)bMRKnJaLr*wAQONHizJElRYRWnnebEitR6bRJ|qD80s8a+QY|-njtBMaIr&^%l<Vl8jnk#@XV8`X8!3BW_}n(6ty8ozUA?rCSnJPPb92;ri8KPxHH*-5q}vGC4}#R#>CP~n1pUl?3=Q?OnoM|cJOhcqj~MstPrQXxKdBwc`Mx~vHtw`*o?mEIVFM0sY??h{@1iN9qsvF+9Te_NAk9kiCr?W4TyyEL3|H{_WS5#osm*RHN)hsdDDzmSyls<T;{6R>SdRU2qW=uY#)D3HMDuwq8W-ROv(RzPu9EyvBvSu1w<ErMlf%Zhy+vw+gr97+7BN<%KRxUIvINMXTT9kT+*C6W5*_NLw$95J)o-6U4LJn@MN-X6mL4j<(gq0=D@pwoq(OrThjn@j{Apskvr?arJf|>b}9waHSC2=KFSo@pa3Sc_H9QO)-_`TauJnS=mOYrJk<&(tLJgV>V(o8d)<((q1Ttja7Jig)Yw;x(!R8i0ALMlZtJN|6X07N6&u6o1Jg^PV>o4aku~<9|61OhaX>UYDiK52GAP>T8v3C{jhI>Pc+n2>o-z%WTdG;}$&fSJnf*w)tmq##sw{2psPD`l8wd<SsO^?AwxYa%${5xwD{GnC=z@Ej6zuNxc<&&hL}aq5P+~`fE56^=P*Gpj79z`6RJ9qPwIeucidLGp3?17>H_X@r7;LN9Pm?>VN&rYM2yTG`(@^=;k`cqE^{}t5F@;JEfLcPlTehi`S8d|ZmCCvDxGnXqL+dg&rs;)JP2&UH*4eM`EBU-WFh7QIoKIB2e|Y#t*>~?D2)QG63iq+3;q9Nbh{+}ID{1p?8+B~0S19Yu$kRWZTm+r7%U!m;f?k%(lPnn5THz{(#jg|Ml6CBN8;#aB^fXC8cEp!@s<)Dk52{Z^t58j?fp-(q^pADIdyH$q<@U#|NI;V#Icg(rZIL4s6tF@+N0`u-#AL9cyzz?nRlpwVow}IuAT*X5noHpOj7_J=I9Vh$Ih4z<=CS~VM2+P38UfnAR>O1&^X6sdPLyplF?n#FtB6|FM$x!Sccz&g7{kh)($Sx8niNc_1&X3l1$tN|(Yw}N5~kr9OCQ9D->Ch12c-?8ec4&`hl(`?!~r9+C`wU;vU1IO#*kD=Nu=ohq29CY?j~zt3)%B{3|>)na2Q^cv1K^RfcZH42T$rp{0jBXvm`Yr{CSCJEKO}}Br8@n1hrh3^TK{woTJ&jps`y-cOF#NGxODXED#2p8avriAVbth@x#M{nT=J{xd9~amv5|7!+0YPfLtC$7w^WGRRtor5QGT!X5<3wxYYETBjgv$g2SKa+~oidmIZJ!i`;r++L*`qnzj-L2m@^iySy=%o?IBrr4LuC8W_U~O(u>NsTnPUg{rPNpjv%49qAW|st?gBE{7)K;2;E)bB*^;q|?WONn9kD%6|0S_IB;tpfLk9<B{VDYerR?*ygUY;lEUUs3gCFyft@De_wl4e2=v!RwSIjGE@RNw3|Jw<T$bHpWChv(Vt4~CJk^ly9uy6c293D*+t&*)8~ARR|N@u$c2EdbFvV~5kdjxwkp;YBE8E82HmA_d#RFfXVSAe3r6Zp00?r~69tO#aLFAyl#ZATz!8aDZR3iswOigNLocZ8L6kb1t`P(55Ph<@L|B+HWdK!L8!AHt+-sz)v!#!`8TN`NKWBjI5rkS7i?XZLJ<x7kR!y65+9(s7My6bN)>Pl<y|y-kA4Q@}0L&)RZ$N>M>}F-X|6xGKm({#6C&r8351J278)jo|nSGS<^oIPpJs$E6kRjme*(mb^)<waVgttmMfwkkk>K(mb_rt1*+%lC#xTba-G@FPV@l(hlCT}?;0&GIqfZx!E!siCX1wBT!z;YXxi->Ai{d&ew!K>(;C9oaBkP-PpFsi5o!H^=&OFyPIEu<Lt_UAoV7q0^)tsOP2_jYrX=AiTcs12f0vffXiAaSfLjB-RDQn7KGo%W+ucUr{5ai4myAIOA-p3J)2VR;TV458KOgTY`3(O;nY8ggX+i&HNR_tRo1(a}G2z7PTVvPT9C&>UX_H;4zr+emZ0z6#~SBMmQS8xu3NQLV$$_ms!04cE8YL(b1_wLD}oB=ed#b-HE{wc)wZ?fd-fryYn@)K~D@z{Abev_KI7?*$`_B-k5n0AXn^F4%^Dx3~^cezI>It9t;V?eFr&80=Sd9xFubq%=|U5f_uUv_&pz16?5M`)Zp<Kki^a%6R4~=;t@D--~w9b((H!+z;N-$h&u~Au|dnFSJ8GOt}yb18wL>F_Pp7a&Vadt4JSL<l@C&JArr#QP=63k;#kFySX`M@A&&jHSG|TpkQ9`y-`vdO2IM$y2J##<Rw8mIJLU#vVVIewjjwk1S5P#f{dA%q0{p2w4*(o#2{wZk5Kzw$n6aPj-n3iVX6>OxO!ViJPLUNFu;vFfoHfjBkPU9WO1w$nsX(jQg$hgJd8}q5(-hYG{g~=3(*C;6m9|W+yeNyZ##HFOEa49A+!xui{<IDC;79SUd<P<uz5gt)n*To1~$@qGLP=%a;Aph3Z~rT=h0Vq7?k<!)np%gLyHPJ8&B+8*&{Mi?PRT(lT8HEBNW(qG@B3$jLdyyc`|F?t#c?ng@=>IP^`Y1S+@I#4^pc20?aDk5rf_lIe@4NCCI5<+fn;Ccl+=>bHKUJ{)G3scHw34g`m8}exj*<8qahp?bUE$L8NQ<JNrQQrLY_{N2rofN(Vqsa+)uEQQCWW<W;^KyUyVP8i^wqsFs2c1pW#f{V14g4Q{^+BN~+|_xddM4q0+*7A816M*;;{a*H$?ChiNgF9r>HE>0LXv{Vjg)$uK;^P5RinD-pI(SWb8Vpud+!Brs_1c*vp)znfq-Q;zICi2sGhc=Wm{m3@1P}|AaUz-6l*`-NG@uDtk#0S}ndRjY~)uw>zI&Ok6vAEJ-9^=&pFRqc>uM<+?5W;(gp3rwUV;SF$!pYdSBgN{q#o3R^sTv*uGMEsX-Yta$aO7qc^6#hfYM~-xawUd!XbgwKyOo`Sk!808AZfs8EP9g;kz*`g+@wXL(h0qC<Gr@**6TH{tfu?@Y%LGVLjN&x)H(&tWiO*fcb)!kL2ql@r_iZ$zlP*;TzXB`b<0C1wbM4@tS_ri68AE{Ku^0qTMUwoM~z3Lu~(^$xNeA_W3(iTmG`DQ^5sq<J$wnBVeO3S4O;^!U5W#26|+TZUTqkLhg>7!P?V+fdYsmS`S2Ks5s`e=vr+1oraY=8(Xl)!u@!~6{Xd#aXNLeMPu{q>bNba_N?yzoTWK5QcxCn|?453e$S`ylwU7@mbC2kEeXAX$6N5)Gbz`}jPPuTdoEo{-A;){)b8~`YS6P}me%^AV&e4}dQ1i`iwOiARZ`YVCD0p-7CqR+w_g9S3%1ys=1tJwx%s%RDde*as1Cx1ply<dTK7H>|41><mR7ou8<#e5oRYd{oA^Lch(=>89aQu)RJby;V8@;|>kyboU-#Rq)9xe|DF|thUPG-LzlDMC-KUdE5M)jqwd2mL`<Q!#HNU;t5z<Q!WWhiJL3&fKD$(aC_nyPw_plP)`L~vdecOK3S6xfaa!{^Nv_ezFx%!eOkbx+*i%$d*z7}-zt7~rU`(%Ul(3;6`NFSTwou_7o!Uv4=0cP63D25AIX=#k0dI&KlbV-X;G+skZI`$<@(Oe&Imgr;Bts*Tnb81Hci!tunVaCVH(JHvtEFE-XfXSyC>IQ_5CQk69haFqdKsB8rik!!7m^$^xT`mPq96}O0nA!!nBZZ)Rj>z^@yjjY$V*Rkv1KjQJZ;U>G<a`6#=4SjZPER8u47a={MbsW=vz~b&j7`9>aBzVwQ4wSyFSnxHDc6pVamb(?9$^ljMNKg{6-lqv6&SG)p+BBm^UU&01dmEzUrymGjxBn_7!WjUz1^hPpfp{73AX*`1DuMURQ=KgKEPf_a6YWTrk(LvZgn>fy8MyD}JRN29F-%ivn5fB&9V^m6(<iN=H|Grn0+G=gJ^P}5a!+jGC-y+|a%Zh~AmFbBve1=_T^(tk{^tCI7Qi{Dwywa1U^DiWJ)G=^vh2fyP$xCt%aPbLten8iHiV@gSb~B5e0h^bJ=f&6eF)@Tp++p#*F5hq3UgW@jv$L-BR{};9SixLa9A^yB8eSffklH^{C*x*2XjNnj*hA<UG($3f_cNJ_O1<BCyq_ty;xneGzO~;J~Qj;Bo%r-tY!h)hqLtON$!%wJ}8>+Z-?xTpN=4PJt5eRhC(A7d|qflOn6ib(@X0zT*H{CCz{YhYt^XFZHt+x1KreQwXT*R{#{cH9DukOyKx@%^kb=wk6dA9%HP4_fjdY2Q0;Jc(JzFHQR6x&=4Eq%(>YTp<w4Ki8uXi%Ny+~P2SEQg%8DWL?7X4<e+F6P2akxD$O({47Xmhl=?u!?{6?mHc~}Vq^M?(Cq7U#*An((@X_L}rM*4ilA+~o!ds>>Kni%t$bicj<361+g_x<7g34Pjr2rM23;06j26*+47knlkzo?fY6Fu3HiR{VE<BE^3@^z%1+H$dwI00tD*8akP0bvfj}-TM^?-p2#afXbj@1MJ_T&G+510=g_xKK+1r>QgIo9>AeJDm@7Qitbo%tq$23xzthk)~q`*#kdUnUJxF*&AcM|FDn@6cy&!8ZzU`J5uH*Uq%*WIZj}XE=mBj2ck#;)xd#`+^HiTtjjbEKBsz%QW5D7WOCG>LP%tu(N;B623eF<yIU1>#!-#iFRdI_>OQlv(&6H9uD}4j<cIKm+)dkSb*g_QnQeUT=bA$1W7;dcCSBJ5ic%p)vQ8lu1>@c7sF*UCL3S3KI+T<E2EKRoa?tcx{WC!s6{2=6~@37|K?cPg!^qO|e#@J3ZZpFMU1<ph`Y0Li<BdufEBt-KmuR%Vp-n(nz=FyWj%c;IzGx7y9Yv4l=+&F2J+tb;4fa7R?#Rdw@l(%uW9a|6yh&;lFoL^>^xJOXfmw~o-y)>W&#?H|zqpBV3!ZFnx(7{4L>^Bk{!n5uRDur_ay);k;x=yu5LZKBZOUl<K-e@95`i_3KshgM;=wjGKptDrUdSnvLc}~O@)N+?Z3(K(`Ng<)G#9zHCSqpCZ+s7tZp(&P54Hpqu8z5bw*|aC!`QNs!1Rgit)ZB-1VAq{KgLBu6fJus=a5ML6(gICQr8zKroZvV*toJ5yv5&1OHm;9UWHwch!?|xEd&K}Uaw&H=)_^W8P5=M^P><gA(>$Td00Fx(iirULOyL4rvBYQl0ssI200dcD')).decode()
if __name__ == "__main__":
	arg = sys.argv[1] if len(sys.argv) > 1 else ""
	if arg == "--selftest":
		sys.exit(0 if selftest() else 1)
	elif arg == "--ledger":
		lg=ledger()
		print_ledger(lg)
		pr=prog()
		ph,filt,body,code,tmax=machine_constants(pr)
		print("audit",ph,filt,body,code,tmax,pr.calls,pr.instr,pr.moves)
		s1,s2=phase_bytes(code,tmax)
		offset_raw,selector_raw=search_envelopes()
		assert OFFSET_SEARCH_PEAK<=s1 and SELECTOR_SEARCH_PEAK<=s1
		print("mem",s2,MEM_LIMIT,s1,max(s1,s2),max(s1,s2)<=MEM_LIMIT)
		print("wasm",STATIC_C_SHA256,STATIC_WASM_SHA256,WASM_EMITTER_INSTR,WASM_RUN_OPERATORS)
		print("envelopes",offset_raw,selector_raw,SEARCH_EVAL_OPS,OFFSET_SEARCH_EVALS,SELECTOR_SEARCH_EVALS)
		print("searchmem",OFFSET_SEARCH_PEAK,SELECTOR_SEARCH_PEAK)
		print("recovery",other_code(pr),packed_ops(),rec().instr,len(rec().init),pr.nregs)
		print("emitter",bounded_check(pr),"q=%064x"%pr.qint)
	elif arg == "--text":
		sys.stdout.write(text())
	elif arg == "--gen-c":
		sys.stdout.write(GEN_C)
	elif arg == "--loss":
		for k,v in loss(plan(256)).items():
			print(k,v)
	else:
		json.dump(serve(json.load(sys.stdin)),sys.stdout)
