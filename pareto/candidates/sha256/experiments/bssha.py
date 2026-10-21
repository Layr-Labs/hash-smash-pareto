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
		bw=[E[r-3],E[r-2],A[r-7],A[r-6],(T[r-5]+((A[r-6]^A[r-7])&A[r-8]))&M32,T[r-4],
              (E[r-5]+(E[r-2]|E[r-4])+ws[r-2])&M32,(E[r-4]+ws[r-1])&M32]
		return [bw[PERM[k]] for k in range(8)]
def enc_invert(enc):
	r=ROUNDS
	if TAILB:
		bw=[0]*8
		for k in range(8):
			bw[PERM[k]]=enc[k]
		e3,e2,a7,a6,Q,T4,X,Y=bw
		a5=(Q+(a6&a7)+_SIG0(a6))&M32
		a4=(T4+_SIG0(a5)+_MAJ(a5,a6,a7))&M32
		a3=(e3-a7+_SIG0(a4)+_MAJ(a4,a5,a6))&M32
		a2=(e2-a6+_SIG0(a3)+_MAJ(a3,a4,a5))&M32
		t1=(X-(e2&~e3)+_SIG1(e2)+K[r-2])&M32
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
			out += [("^", T3, f, g), ("&", T3, e, T3), ("^", T3, g, T3)] # Ch
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
			tail += [("+", E5, rd, R5), ("&", E5, E5, MASK)] # e_{r-5}
			t1(tail,R4,rg,E5,re,rf,n-5,None,True)
			tail += [("+", E4, rc, R4), ("&", E4, E4, MASK)] # e_{r-4}
			t1(tail,T2,rf,E4,E5,re,n-4,W0,False)
			tail += [("+", E3, rb, T2), ("&", E3, E3, MASK)] # e_{r-3}
			t1(tail,T2,re,E3,E4,E5,n-3,W1,False)
			tail += [("+", E2, ra, T2), ("&", E2, E2, MASK)] # e_{r-2}
			tail += [("|", T3, E2, E4), ("+", XX, E5, T3), ("+", XX, XX, W2), ("&", XX, XX, MASK)] # X (shear)
			tail += [("+", YY, E4, W3), ("&", YY, YY, MASK)] # Y
			tail += [("^", T0, ra, rb), ("&", T0, T0, rc), ("+", QQ, R5, T0), ("&", QQ, QQ, MASK)] # Q
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
class Gen:
	def __init__(self,n):
		self.n, self.nodes, self.calls = n, [("c",)], 0
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
	def XOR(self,x,y):
		self.calls+=1
		if x[0]==0:
			return (y[0],y[1]^x[1])
		if y[0]==0:
			return (x[0],x[1]^y[1])
		if x[0]==y[0]:
			return (0,x[1]^y[1])
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
			return (self.mk("o", x[0], y[0]), 1) # !a & !b = !(a | b)
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
	def addm(self,*ws,force_bb=None):
		sp = getattr(self, "split", None)
		cv,vs=0,[]
		for w in ws:
			if all(x[0]==0 for x in w):
				cv+=sum(x[1]<<i for i,x in enumerate(w))
			else:
				vs.append(w)
		cv&=M32
		if not vs:
			return _constw(cv)
		bb=force_bb if force_bb is not None else (max(range(len(vs)),key=lambda k: (_tz((cv-k)&M32),-k)) if CIN and cv else 0)
		used_b=0
		while len(vs)>2:
			c3=min(bb-used_b,2)
			used_b+=c3
			vs=[self.add3(*vs[:3],c3)]+vs[3:]
		s=vs[0]
		for k,w in enumerate(vs[1:]):
			c1=1 if used_b<bb else 0
			used_b+=c1
			s=self.add(s,w,ONE if c1 else ZERO)
		cv=(cv-used_b)&M32
		if cv:
			out=self.add(s,_constw(cv))
			if sp is not None:
				sp[tuple(out)]=(s,cv)
			return out
		return s
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
def _net_u():
	g=Gen(256)
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
		mj=[g.AND(g.XOR(a6[j],a7[j]),a8[j]) for j in range(32)]
		Q=g.add(T5,mj,ONE)
		T4,fg,_=_t1hg(g,e5,e6,e7,e8,fg,wd(r-5))
		e4=g.add(a8,T4)
		e3=g.addm(a7,e7,_ch_direct(g,e4,e5,e6),_sigma(g,e4,6,11,25,False),*wd(r-4))
		e2=g.addm(a6,e6,_ch_direct(g,e3,e4,e5),_sigma(g,e3,6,11,25,False),*wd(r-3))
		X=g.addm(W[r-2],_sigma(g,W[r-4],17,19,10,True),e5,[g.OR(e2[j],e4[j]) for j in range(32)])
		Y_out=g.addm(W[r-1],_sigma(g,W[r-3],17,19,10,True),e4)
		bw=[e3,e2,a7,a6,Q,T4,X,Y_out]
		out=[bw[PERM[k]] for k in range(8)]
		return g,[t for w in out for t in w]
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
	R=[]
	g,outs=_net_u()
	_QM[:]=[sum(1<<(32*(7-i//32)+i%32) for i,o in enumerate(outs) if o[0] and o[1])]
	moves=_alloc(g,256,{j+1: INREG(j) for j in range(256)},outs,[256+i for i in range(256)],range(REGISTERS),R.append)
	return R,moves,2*g.calls
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
INSTR_BYTES=36
BODY_BYTES=5
GEN_CODE=4316
HANDLER_CODE,SETUP_CODE,RECOVERY_CODE=1000,160,47
REGISTERS=926
REGFILE=REGISTERS*32
COUNTERS=16384
ARRAYS=64*32
KEYB=46
SLOTB=KEYB+1
MEM_LIMIT=1<<20
ADVICE=0
KAPPA_256=13
GEN_FACTOR=200
GEN_SCRATCH=69593
SETUP_FIXED=256*3100+20000
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
	code=pr.instr*BODY_BYTES+(filt+LOOP_OPS+other_code(pr))*INSTR_BYTES
	return pr.kernel,filt,pr.kernel+filt+LOOP_OPS,code,8*(MEM_LIMIT-code-REGFILE-COUNTERS-ADVICE-ARRAYS)//SLOTB-LANES-CMAX
def table_bytes(tmax):
	return-(-(tmax+LANES+CMAX)*SLOTB//8)
def phase_bytes(code,tmax):
	prog()
	return code+COUNTERS+GEN_CODE*INSTR_BYTES+GEN_SCRATCH,code+COUNTERS+REGFILE+ARRAYS+table_bytes(tmax)
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
	ph,filt,body,code,_=machine_constants(pr)
	gen=GEN_FACTOR*(pr.calls+pr.instr)
	parts = dict(main=body * p["B"],
                 slices=-(-p["B"] // p["Sb"]) * SLICE_OPS,
                 stage1_hits=p["e2max"] * HIT_OPS,
                 events=p["tmax"] * (EVENT_OPS + 6 * (p["tmax"] + LANES + CMAX)),
                 cuts=p["cmax"] * CUT_OPS,
                 recovery=2 * p["capr"] * (packed_ops() + RECOVER_EXTRA) + 600 + len(rec().init),
                 setup=SETUP_FIXED+gen)
	return dict(parts=parts,total=sum(parts.values()),plan=p,body=body,gen=gen)
TB=17
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
		a5=g.addm(Q,[g.AND(a6[j],a7[j]) for j in range(32)],S0(a6))
		a4=g.addm(T4,S0(a5),mj(a5,a6,a7))
		a3=g.addm(e3,neg(a7),_constw(1),S0(a4),mj(a4,a5,a6))
		a2=g.addm(e2,neg(a6),_constw(1),S0(a3),mj(a3,a4,a5))
		t1=g.addm(X,neg([g.AND(e2[j],(e3[j][0],e3[j][1]^1)) for j in range(32)]),_constw((1+K[ROUNDS-2])&M32),S1(e2))
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
				w=key|1<<KEYB
				if w in table:
					t0=table.index(w)
					cnt["recoveries"] += 1
					res=recover(p,r,(t0,trail_length(p,(r+t0)&mask,eng.f2)),(ts[l],length),eng.f2)
					if res is None:
						raise Halt("recovery found no pair")
					return res
				if cnt["finished"] > p["tmax"]:
					raise Halt("table full")
				assert key >> KEYB == 0 and ts[l] < p["tmax"] + LANES + p["cmax"]
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
			xs+=cur
			cur=lanes_of(list(st.step(*pack_lanes(cur,256,st.pin))),256,st.pin)
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
def serve(req):
	eid, out = req["experiment_id"], []
	if eid == "bssha-n16":
		rows = e1_rows(req["trials"])
	elif eid == "proj-k0-w256":
		st=prog()
		rows = [e2_trial(t["seed"], t["trial"], st) for t in req["trials"]]
	else:
		raise ValueError("unknown experiment")
	for t, (a, b, obs) in zip(req["trials"], rows):
		out.append({"trial": t["trial"], "message_a_hex": a.hex() if a else None, "message_b_hex": b.hex() if b else None, "observations": obs})
	return {"schema_version": 1, "trials": out}
def text():
	return "".join("%s %d %d %d\n" % r for r in prog().recs)
def selftest():
	import random
	rnd=random.Random(3)
	pr=prog()
	reg = max(max(r[1:4]) for r in pr.recs if r[0] in "^&|") + 1
	print("records", pr.instr, "moves", pr.moves, "kernel", pr.kernel, "registers used", reg, "text sha256", hashlib.sha256(text().encode()).hexdigest())
	ok = reg <= REGISTERS and pr.nregs <= REGISTERS and all(r[0] in "^&|NM" for r in pr.recs)
	t=True
	for xs in [[rnd.getrandbits(256) for _ in range(LANES)] for _ in range(8)]+[[0]*LANES,[(1<<256)-1]*LANES]:
		out=lanes_of(list(pr.step(*pack_lanes(xs,256,pr.pin))),256,pr.pin)
		t&=all(out[l]==f_scalar(xs[l])^pr.qint for l in range(LANES))
	print("2,560 lanes (10 batches), full 256-bit g = f XOR q, program vs scalar walk-B encoding of state_40:", t)
	ok&=t
	rt=True
	for _ in range(10000):
		w=[rnd.getrandbits(32) for _ in range(8)]
		rt&=enc_invert(enc_words(w))==state_words(w)
	print("explicit inverse round-trips on 10,000 random states (enc_invert(enc_words) == state_words):", rt)
	ok&=rt
	regs=[0]*REGISTERS
	for j in range(256):
		regs[INREG(j)]=rnd.getrandbits(256)
	ref=list(regs)
	n=pr.run(0,len(pr.recs),regs)
	fast=list(ref)
	pr.fast(fast)
	t=n==pr.kernel and [fast[INREG(j)] for j in range(256)]==[regs[INREG(j)] for j in range(256)]
	print("records executed per batch by the interpreter", n, "kernel", pr.kernel, "; the compiled form gives the same 256 output planes:", t)
	ok&=t
	cur=[rnd.getrandbits(256) for _ in range(LANES)]
	pl=pack_lanes(cur,256,pr.pin)
	for _ in range(4):
		pl=list(pr.step(*pl))
		cur=[f_scalar(x)^pr.qint for x in cur]
	t=lanes_of(pl,256,pr.pin)==cur
	print("256 lanes chained for 4 steps:", t)
	ok&=t
	e=Engine(N_T3)
	xs=[rnd.getrandbits(N_T3) for _ in range(LANES)]
	pl=pack_lanes(xs,N_T3,e.pin)
	for _ in range(5):
		pl=list(e.step(*pl))
		xs=[e.g_scalar(x) for x in xs]
	t=lanes_of(pl,N_T3,e.pin)==xs
	print("n=%d chain, 5 steps:" % N_T3, t)
	ok&=t
	xs=[rnd.getrandbits(256) for _ in range(2)]
	ref2=[f_scalar(x) for x in xs]
	t=packed_f(xs,256)==ref2 and rec().f(xs,False)==ref2 and packed_f(xs[:1],256)==ref2[:1] and rec().f([0,ALL])==[f_scalar(0),f_scalar(ALL)]
	t&=packed_f(xs,256,pr.qwords)==[f_scalar(x)^pr.qint for x in xs]
	print("recovery program (%d records executed per call, %d records, interpreter and compiled form) vs scalar (bare f and g = f XOR q):" % (packed_ops(), rec().instr), t)
	ok&=t
	rows=[rnd.getrandbits(256) for _ in range(256)]
	t=transpose(transpose(rows))==rows and (transpose(rows)[5]>>9)&1==(rows[9]>>5)&1
	print("transpose:", t)
	xs=[rnd.getrandbits(256) for _ in range(LANES)]
	t=lanes_of(dnet().step(list(pr.step(*pack_lanes(xs,256,pr.pin)))),256,[0]*256)==[digest_of_state(state_words(words_of(x))) for x in xs]
	print("experiments' bit-sliced digest of the padded two-block message (256 lanes) vs scalar block 1 plus block 2:", t)
	ok&=t
	ok&=t
	p,found=plan(N_T3),0
	for s in range(6):
		res, cnt = attempt(e, p, "selftest/%d" % s, "t")
		if res is not None:
			found+=1
			ok&=res[0]!=res[1] and e.g_scalar(res[0])==e.g_scalar(res[1])
	print("search n=%d: %d of 6 attempts returned a verified pair" % (N_T3, found))
	ok&=found>0
	print("selftest", bool(ok))
	return ok
def print_ledger(lg):
	print({k: (str(v) if isinstance(v, Fraction) else v) for k, v in lg["plan"].items()})
	print("operations per batch (body)", lg["body"])
	for k, v in lg["parts"].items():
		print(k,v)
	print("N =", lg["total"])
	print("time_log2 = %.5f (unrounded %.8f)" % (log2(lg["total"] / UNIT) + 5e-6, log2(lg["total"] / UNIT)))
GEN_C = r'''
typedef unsigned char u8;typedef unsigned short u16;typedef unsigned int u32;
#define NMAX 43930
#define NREC 43673
#define RND 40
#define NST 256
#define IR(j)(256+32*(7-((j)>>5))+((j)&31))
#define NODE(s)(((s)>>1)&0x3FFFFu)
#define REG(s)((s)>>19)
#define ZERO 0u
#define ONE 1u
static u8 code[NREC][5];
__attribute__((used))static u8 counters[16384];
static u8 uses[NMAX];
static u32 fb[32],pb[32],W[16][32],WS[16][32],WCV[16],Wt[32],Wt2[32],V[10][32],ab[32],mj[32],ch[32],S0[32],S1[32],s0[32],s1[32],T1[32],T2[32],KW[32],NA[32],NE[32];
static u32 Y[8][32],X2[32],AM[32],A3[32],cse_k[1024],cse_v[1024],ncse,last_cv;
static u32 TB[11][32],FG[32],TT[32],UU[32],SG[32];
static const u32*AW[8];
static const u32 PERM[8]={6,1,7,0,5,4,2,3};
static u32 oid[NST],oix[NST],oreg[NST],onode[NST],mvi[NST],mvs[NST];
static u8 oneg[NST];
static u32 pass,nn,nin,nO,nE,co,calls,err,kk,nmov;
static struct{u32 ninst,nreg,nodes0,nodes1,nodes2,calls,err,moves,n0,n1,n2,sz_code,sz_ctr,sz_uses,sz_state;u8 q[32];}info;
static const u32 IV[8]={0x6A09E667u,0xBB67AE85u,0x3C6EF372u,0xA54FF53Au,0x510E527Fu,0x9B05688Cu,0x1F83D9ABu,0x5BE0CD19u};
static const u32 K[RND]={0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,
0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,
0x650a7354u,0x766a0abbu,0x81c2c92eu,0x92722c85u};
static const u32 PW[8]={0x3e73281cu,0x752d8ed2u,0xad19eff1u,0x7250fcebu,0xd4095422u,0x44fdb519u,0x43f22c5bu,0xd8d6aac4u};
static void emit(u32 op,u32 d,u32 a,u32 b){
if(kk>=NREC){err=5;return;}
u8*r=code[kk++];u32 w=d|(a<<10)|(b<<20);
r[0]=(u8)op;r[1]=(u8)w;r[2]=(u8)(w>>8);r[3]=(u8)(w>>16);r[4]=(u8)(w>>24);
}
static int isfree(u32 r){return (fb[r>>5]>>(r&31))&1;}
static void release(u32 r){fb[r>>5]|=1u<<(r&31);}
static u32 take(int prefer,int sh,u32 wlim){
u32 r=0,w;
if(prefer>=0&&isfree((u32)prefer)){fb[prefer>>5]&=~(1u<<(prefer&31));return (u32)prefer;}
if(sh){
for(w=0;w<wlim;w++)if(fb[w]&pb[w]){r=32*w+(u32)__builtin_ctz(fb[w]&pb[w]);break;}
if(w==wlim)w=32;
}else{
for(w=0;w<32;w++)if(fb[w]&~pb[w]){r=32*w+(u32)__builtin_ctz(fb[w]&~pb[w]);break;}
}
if(w==32)for(w=0;w<32;w++)if(fb[w]){r=32*w+(u32)__builtin_ctz(fb[w]);break;}
if(w==32){err=8;return 0;}
fb[r>>5]&=~(1u<<(r&31));
return r;
}
static u32 tgt(u32 i){return 256+i;}
static u32 mk(u32 op,u32 x,u32 y){
calls++;
if(NODE(x)>NODE(y)){u32 t=x;x=y;y=t;}
u32 a=NODE(x),b=NODE(y),ck=0,cs=0;
if(b<=nin){
ck=(op+1)|(a<<2)|(b<<11);
for(cs=(ck*2654435761u)>>22;cse_k[cs];cs=(cs+1)&1023u)if(cse_k[cs]==ck)return cse_v[cs];
if(++ncse>900){err=10;return 0;}
}
u32 id=nn++;
if(id>=NMAX){err=1;return 0;}
if(pass==0){
if(uses[a]==255||uses[b]==255){err=6;return 0;}
uses[a]++;uses[b]++;
if(ck){cse_k[cs]=ck;cse_v[cs]=id<<1;}
return id<<1;
}
u32 rx=REG(x),ry=REG(y),wlim=(id+30<oid[0])?16u:14u;
int want=-1,dst=-1;
u32 dx=--uses[a]==0,dy=--uses[b]==0;
if(co<nE&&oid[co]==id)want=(int)tgt(oix[co]);
int sh=(uses[id]<=3&&id+200<oid[32]&&want<0);
if(want>=0){
if(isfree((u32)want))dst=(int)take(want,0,0);
else{if(dx&&rx==(u32)want)dst=want;if(dy&&ry==(u32)want)dst=want;}
}
if(dst<0){
u32 px=sh?((rx>>5)<wlim&&((pb[rx>>5]>>(rx&31))&1)):!((pb[rx>>5]>>(rx&31))&1);
u32 py=sh?((ry>>5)<wlim&&((pb[ry>>5]>>(ry&31))&1)):!((pb[ry>>5]>>(ry&31))&1);
if(dx&&(px||rx==(u32)want))dst=(int)rx;
else if(dy&&(py||ry==(u32)want))dst=(int)ry;
}
if(dx&&rx!=(u32)dst)release(rx);
if(dy&&ry!=(u32)dst)release(ry);
if(dst<0)dst=(int)take(-1,sh,wlim);
if(dst==want)pb[dst>>5]&=~(1u<<(dst&31));
emit(op==0?'^':op==1?'&':'|',(u32)dst,rx,ry);
while(co<nE&&oid[co]==id)oreg[oix[co++]]=dst;
if(uses[id]==0){err=9;release((u32)dst);}
if(ck){cse_k[cs]=ck;cse_v[cs]=(id<<1)|((u32)dst<<19);}
return (id<<1)|((u32)dst<<19);
}
static u32 XOR(u32 x,u32 y){
calls++;
if(!NODE(x))return y^(x&1);
if(!NODE(y))return x^(y&1);
if(NODE(x)==NODE(y))return (x^y)&1;
return mk(0,x,y)^((x^y)&1);
}
static u32 AND(u32 x,u32 y){
calls++;
if(!NODE(x))return (x&1)==0?ZERO:y;
if(!NODE(y))return (y&1)==0?ZERO:x;
if(NODE(x)==NODE(y))return x==y?x:ZERO;
if(!(x&1)&&!(y&1))return mk(1,x,y);
if((x&1)&&(y&1))return mk(2,x,y)|1;
u32 p=(x&1)==0?x:y,q=(x&1)==0?y:x;
return XOR(p,mk(1,p,q));
}
static void fa(u32 a,u32 b,u32 c,u32*sum,u32*carry){
u32 ops[3]={a,b,c},vs[3],nv=0,k=0,nc=0,cs3[3]={0,0,0};
for(int i=0;i<3;i++){
if(!NODE(ops[i])){cs3[nc++]=ops[i]&1;k^=ops[i]&1;}else vs[nv++]=ops[i];
}
if(nv==3){
u32 p=0,x=0,y=0;
for(int pi=0;pi<3;pi++){
u32 o0=vs[pi==0?1:0],o1=vs[pi==2?1:2];
if((o0&1)==(o1&1)){p=vs[pi];x=o0;y=o1;break;}
}
u32 u=XOR(x,p);
u32 s=XOR(u,y);
u32 w=XOR(y,p);
u32 an=AND(u,w);
*sum=s;*carry=XOR(an,p);return;
}
if(nv==2){
u32 x=vs[0],y=vs[1];
u32 t=XOR(x,y);
u32 s=t^k;
if((x&1)==(y&1)){
if(k==0){*sum=s;*carry=AND(x,y);return;}
*sum=s;*carry=AND(x^1,y^1)^1;return;
}
u32 nt=t^1;
u32 xx=(x&1)==(nt&1)?x:y,xt=(x&1)==(t&1)?x:y;
if(k==0){*sum=s;*carry=AND(xx,nt);return;}
*sum=s;*carry=AND(xt^1,t^1)^1;return;
}
if(nv==1){
u32 x=vs[0],k1=cs3[0],k2=cs3[1];
*sum=x^k;*carry=(k1==1&&k2==1)?ONE:(k1==0&&k2==0)?ZERO:x;return;
}
u32 kk3=cs3[0]+cs3[1]+cs3[2];
*sum=(kk3 % 2==0)?ZERO:ONE;*carry=kk3>=2?ONE:ZERO;
}
static void constw(u32*w,u32 val){for(int i=0;i<32;i++)w[i]=(val>>i)&1u;}
static void addc(const u32*A,const u32*B,u32*out,u32 c){
for(int i=0;i<32;i++){
if(i==31)out[i]=XOR(XOR(A[i],B[i]),c);
else{u32 si;fa(A[i],B[i],c,&si,&c);out[i]=si;}
}
}
static void add(const u32*A,const u32*B,u32*out){addc(A,B,out,ZERO);}
static u32 tz(u32 v){return v?(u32)__builtin_ctz(v):32u;}
static u32 OR(u32 x,u32 y){return AND(x^1,y^1)^1;}
static void col(const u32*o,u32 u,u32 U,int tm,int oU,u32*r){
u32 x=o[0],y=o[1],z=o[2];
if(tm==1){u32 w=XOR(y,U),n8=XOR(z,w);r[0]=XOR(x,n8);u32 n6=OR(U,XOR(y,u));r[1]=oU?0:XOR(n6,w);r[2]=XOR(n6,AND(n8,XOR(x,w)));return;}
if(tm==2){u32 w5=XOR(x,y),w6=XOR(z,w5);r[0]=XOR(U,w6);u32 w9=XOR(u,w6),w10=OR(U,w9^1u),w11=OR(w5,XOR(x,z));r[1]=oU?0:XOR(w6,w10^1u);r[2]=XOR(w10,w11^1u);return;}
u32 n5=XOR(z,U),n9=XOR(x,n5);r[0]=XOR(y,n9);
u32 n6=XOR(x,y),n8=OR(U,XOR(z,u)),n11=AND(n6^1,n9);r[1]=oU?0:XOR(n5,n11);r[2]=XOR(n8,n11);
}
static void add3(const u32*A,const u32*B,const u32*C,u32*out,u32 cin){
u32 u=0,U=0,r[3],o[3];
if(cin==0)fa(A[0],B[0],C[0],&out[0],&U);
else if(cin==2){fa(A[0],B[0],C[0],&out[0],&U);u=ONE;U^=1u;}
else{
u32 ops[3]={A[0],B[0],C[0]},p=0,x=0,y=0;
for(int pi=0;pi<3;pi++){
u32 o0=ops[pi==0?1:0],o1=ops[pi==2?1:2];
if((o0&1u)==(o1&1u)){p=ops[pi];x=o0;y=o1;break;}
}
u32 u0=XOR(x,p);out[0]=XOR(u0,y^1u);u=p;U=OR(u0,XOR(y,p));
}
for(int i=1;i<31;i++){
u32 t[3]={A[i],B[i],C[i]},pt=(U^u)&1u;int tm=0;
if((t[0]&1u)==(t[1]&1u)&&(t[1]&1u)==(t[2]&1u)){
o[0]=t[0];o[1]=t[1];o[2]=t[2];tm=((t[0]&1u)==pt)?1:2;
}else{
for(int zi=0;zi<3;zi++)if((t[zi]&1u)==pt){
u32 r0=t[zi==0?1:0],r1=t[zi==2?1:2],up=(u&1u)^1u;
if((r0&1u)==up){o[0]=r1;o[1]=r0;o[2]=t[zi];tm=0;}
else if((r1&1u)==up){o[0]=r0;o[1]=r1;o[2]=t[zi];tm=0;}
else{o[0]=r0;o[1]=t[zi];o[2]=r1;tm=1;}
break;
}
}
col(o,u,U,tm,i==30,r);out[i]=r[0];u=r[1];U=r[2];
}
out[31]=XOR(XOR(XOR(A[31],B[31]),C[31]),U);
}
static void addm_fb(u32*out,const u32*const*ws,int n,int force_bb){
u32 cv=0,bb=0,used_b=0;int nv=0;
for(int k=0;k<n;k++){
int c=1;
for(int i=0;i<32;i++)if(NODE(ws[k][i])){c=0;break;}
if(c){u32 v=0;for(int i=0;i<32;i++)v|=(ws[k][i]&1u)<<i;cv+=v;}
else AW[nv++]=ws[k];
}
if(!nv){constw(out,cv);last_cv=0;return;}
if(force_bb>=0)bb=(u32)force_bb;
else if(cv)for(u32 k=1;k<(u32)nv;k++)if(tz(cv-k)>tz(cv-bb))bb=k;
while(nv>2){
u32 c3=bb-used_b;if(c3>2u)c3=2u;
used_b+=c3;
add3(AW[0],AW[1],AW[2],A3,c3);AW[0]=A3;
for(int k=1;k<nv-2;k++)AW[k]=AW[k+2];
nv-=2;
}
for(int i=0;i<32;i++)AM[i]=AW[0][i];
for(int k=1;k<nv;k++){
u32 c1=used_b<bb?1u:0u;used_b+=c1;
addc(AM,AW[k],AM,c1?ONE:ZERO);
}
cv-=used_b;last_cv=cv;
for(int i=0;i<32;i++)X2[i]=AM[i];
if(cv){constw(KW,cv);add(AM,KW,AM);}
for(int i=0;i<32;i++)out[i]=AM[i];
}
static void addm(u32*out,const u32*const*ws,int n){addm_fb(out,ws,n,-1);}
static void sigma(u32*out,const u32*A,int r1,int r2,int r3,int shift){
for(int j=0;j<32;j++){
u32 t=XOR(A[(j+r1)&31],A[(j+r2)&31]);
u32 z=shift?(j+r3<32?A[j+r3]:ZERO):A[(j+r3)&31];
out[j]=XOR(t,z);
}
}
static u32 inp(u32 j){return ((1+j)<<1)|(IR(j)<<19);}
static void outp(u32 i,u32 s){if(pass==0){onode[i]=NODE(s);oneg[i]=(u8)(s&1);}}
static void addu(const u32*A,const u32*u,u32 cin,u32*out){
u32 c=ZERO;
for(int i=0;i<32;i++){
out[i]=i?XOR(u[i],c):(u[0]^cin);
if(i==0)c=cin?OR(A[0],u[0]):AND(A[0],u[0]^1u);
else if(i<31){
u32 w=XOR(A[i],c);
if(NODE(u[i])&&NODE(w)&&NODE(u[i])!=NODE(w)&&(u[i]&1)!=(w&1))c=XOR(AND(u[i]^1,w),c);
else c=XOR(AND(u[i],w),A[i]);
}
}
}
static u32 t1hg(u32*o,const u32*e,const u32*f,const u32*g,const u32*h,const u32*hg,const u32*w0,const u32*w1,const u32*w_sp,u32 sp_cv,int has_d){
for(int j=0;j<32;j++)FG[j]=XOR(f[j],g[j]);
for(int j=0;j<32;j++)TT[j]=AND(e[j],FG[j]);
for(int j=0;j<32;j++)UU[j]=XOR(hg[j],TT[j]);
sigma(SG,e,6,11,25,0);
const u32*wd[2]={w0,w1},*vs1=0;
u32 cv=0,nvar=1,has_h=0;
for(int j=0;j<32;j++)if(NODE(h[j]))has_h=1;
for(int k=0;k<2;k++)if(wd[k]){
int c=1;
for(int i=0;i<32;i++)if(NODE(wd[k][i])){c=0;break;}
if(c){u32 v=0;for(int i=0;i<32;i++)v|=(wd[k][i]&1u)<<i;cv+=v;}
else{vs1=wd[k];nvar++;}
}
if(has_h&&cv&&nvar==2){
u32 pref_u=(NODE(h[0])&&NODE(UU[0])&&(h[0]&1u)==(UU[0]&1u))?1u:0u;
u32 b_sc=0,b_tot=~0u,b_d=~0u,b_cu=0,b_c3=0,b_cv=cv;const u32*b_w=vs1;
for(int cand=0;cand<(w_sp?2:1);cand++){
const u32*wc=cand?w_sp:vs1;u32 cvc=cand?(cv+sp_cv):cv;
for(u32 cu=0;cu<2;cu++)for(u32 c3=0;c3<3;c3++)for(u32 d_=0;d_<=(has_d?1u:0u);d_++){
u32 tot=cu+c3+d_,sc=2u*tz(cvc-tot)+(cu==pref_u?1u:0u);
if(b_tot==~0u||sc>b_sc||(sc==b_sc&&(tot<b_tot||(tot==b_tot&&d_<b_d)))){
b_sc=sc;b_tot=tot;b_d=d_;b_cu=cu;b_c3=c3;b_w=wc;b_cv=cvc;
}
}
}
addu(h,UU,b_cu,T2);
add3(T2,SG,b_w,o,b_c3);
u32 cv2=b_cv-b_cu-b_c3-b_d;
if(cv2){constw(KW,cv2);add(o,KW,o);}
return b_d;
}
addu(h,UU,0,o);
const u32*ws[4]={o,SG,w0,w1};
addm(o,ws,w1?4:3);
return 0;
}
static void rnd(const u32*w0,const u32*w1,const u32*w_sp,u32 sp_cv){
int has_d=0;
for(int j=0;j<32;j++)if(NODE(V[3][j]))has_d=1;
u32 delta=t1hg(T1,V[4],V[5],V[6],V[7],V[9],w0,w1,w_sp,sp_cv,has_d);
for(int j=0;j<32;j++)ch[j]=FG[j];
sigma(S0,V[0],2,13,22,0);
for(int j=0;j<32;j++){
ab[j]=XOR(V[0][j],V[1][j]);
if(V[2][j]==ZERO)mj[j]=AND(V[0][j],V[1][j]);
else if(NODE(ab[j])&&NODE(V[8][j])&&NODE(ab[j])!=NODE(V[8][j])&&(ab[j]&1)!=(V[8][j]&1))mj[j]=XOR(AND(ab[j]^1,V[8][j]),V[2][j]);
else mj[j]=XOR(AND(ab[j],V[8][j]),V[1][j]);
}
addc(V[3],T1,NE,delta?ONE:ZERO);
if(delta)add3(T1,S0,mj,NA,delta);
else{const u32*ws[3]={T1,S0,mj};addm(NA,ws,3);}
for(int j=0;j<32;j++){
V[3][j]=V[2][j];V[2][j]=V[1][j];V[1][j]=V[0][j];V[0][j]=NA[j];
V[7][j]=V[6][j];V[6][j]=V[5][j];V[5][j]=V[4][j];V[4][j]=NE[j];V[8][j]=ab[j];V[9][j]=ch[j];
}
}
static void ch_direct(u32*out,const u32*e,const u32*f,const u32*g){
for(int j=0;j<32;j++){
u32 fg=XOR(f[j],g[j]);
if(NODE(e[j])&&NODE(fg)&&(e[j]&1u)!=(fg&1u))out[j]=XOR(f[j],AND(e[j]^1u,fg));
else out[j]=XOR(g[j],AND(e[j],fg));
}
}
static void wmsg(int i,u32*o){
if(i<8)constw(o,PW[i]);
else if(i<10)for(int b=0;b<32;b++)o[b]=Y[i-8][b];
else{
constw(KW,0u-K[i]);
const u32*ws[2]={Y[i-8],KW};
addm(o,ws,2);
for(int b=0;b<32;b++)WS[i][b]=X2[b];
WCV[i]=last_cv;
}
}
static void trace(void){
nn=1+nin;ncse=0;
for(int k=0;k<1024;k++)cse_k[k]=0;
for(int k=0;k<16;k++)WCV[k]=0;
for(int k=0;k<8;k++)for(int b=0;b<32;b++)Y[k][b]=inp(32*(7-k)+b);
for(int i=0;i<16;i++)wmsg(i,W[i]);
for(int i=0;i<8;i++)constw(V[i],IV[i]);
for(int j=0;j<32;j++)V[8][j]=XOR(V[1][j],V[2][j]);
for(int j=0;j<32;j++)V[9][j]=XOR(V[7][j],V[6][j]);
for(int i=0;i<RND;i++){
if(i>=16&&i<RND-2){
sigma(s0,W[(i-15)&15],7,18,3,1);
sigma(s1,W[(i-2)&15],17,19,10,1);
if(i==17||i==21){
constw(Wt2,0u-K[i-7]);
const u32*ws[5]={W[(i-16)&15],s0,Y[i-15],Wt2,s1};
addm_fb(W[i&15],ws,5,-1);
}else if(i==23){
constw(Wt2,WCV[0]);
const u32*ws[5]={W[(i-16)&15],s0,WS[0],Wt2,s1};
addm_fb(W[i&15],ws,5,2);
}else{
const u32*ws[4]={W[(i-16)&15],s0,W[(i-7)&15],s1};
addm_fb(W[i&15],ws,4,-1);
}
for(int b=0;b<32;b++)WS[i&15][b]=X2[b];
WCV[i&15]=last_cv;
}else if(i>=RND-2){
sigma(s0,W[(i-15)&15],7,18,3,1);
add3(W[(i-16)&15],s0,W[(i-7)&15],W[i&15],0);
WCV[i&15]=0;
}
if(i<RND-6){
if(i>=10&&i<16)rnd(Y[i-8],0,0,0);
else{
constw(Wt,K[i]);
rnd(Wt,W[i&15],WCV[i&15]?WS[i&15]:0,WCV[i&15]);
}
}
}
enum{T5,E5,QQ,T4,E4,T3,E3,T2,E2,XX,YY};
u32(*B_)[32]=TB;
constw(Wt,K[RND-6]-1u);t1hg(B_[T5],V[4],V[5],V[6],V[7],V[9],Wt,W[(RND-6)&15],0,0,0);
for(int j=0;j<32;j++)X2[j]=FG[j];
addc(V[3],B_[T5],B_[E5],ONE);
for(int j=0;j<32;j++)mj[j]=AND(XOR(V[0][j],V[1][j]),V[2][j]);
addc(B_[T5],mj,B_[QQ],ONE);
constw(Wt,K[RND-5]);t1hg(B_[T4],B_[E5],V[4],V[5],V[6],X2,Wt,W[(RND-5)&15],0,0,0);
add(V[2],B_[T4],B_[E4]);
ch_direct(TT,B_[E4],B_[E5],V[4]);sigma(SG,B_[E4],6,11,25,0);constw(Wt,K[RND-4]);
{const u32*ws[6]={V[1],V[5],TT,SG,Wt,W[(RND-4)&15]};addm(B_[E3],ws,6);}
ch_direct(TT,B_[E3],B_[E4],B_[E5]);sigma(SG,B_[E3],6,11,25,0);constw(Wt,K[RND-3]);
{const u32*ws[6]={V[0],V[4],TT,SG,Wt,W[(RND-3)&15]};addm(B_[E2],ws,6);}
sigma(s1,W[(RND-4)&15],17,19,10,1);
for(int j=0;j<32;j++)TT[j]=OR(B_[E2][j],B_[E4][j]);
{const u32*ws[4]={W[(RND-2)&15],s1,B_[E5],TT};addm(B_[XX],ws,4);}
sigma(s1,W[(RND-3)&15],17,19,10,1);
{const u32*ws[3]={W[(RND-1)&15],s1,B_[E4]};addm(B_[YY],ws,3);}
{const u32*bw[8]={B_[E3],B_[E2],V[1],V[0],B_[QQ],B_[T4],B_[XX],B_[YY]};
for(int w=0;w<8;w++)for(int j=0;j<32;j++)outp(32*w+j,bw[PERM[w]][j]);}
}
static void sortent(void){
nE=0;
for(u32 i=0;i<nO;i++)if(onode[i]){
u32 t=nE++;
while(t&&oid[t-1]>onode[i]){oid[t]=oid[t-1];oix[t]=oix[t-1];t--;}
oid[t]=onode[i];oix[t]=i;
}
}
__attribute__((export_name("info_ptr")))u32 info_ptr(void){return (u32)(unsigned long)&info;}
__attribute__((export_name("code_ptr")))u32 code_ptr(void){return (u32)(unsigned long)code;}
__attribute__((export_name("run")))int run(void){
info.sz_code=sizeof code;info.sz_ctr=sizeof counters;info.sz_uses=sizeof uses;
info.sz_state=sizeof fb+sizeof pb+sizeof W+sizeof V+18*128+sizeof oid+sizeof oix+sizeof oreg+sizeof onode+sizeof mvi+sizeof mvs+sizeof oneg+sizeof info+sizeof Y+sizeof X2+sizeof AM+sizeof cse_k+sizeof cse_v+sizeof TB+sizeof FG+sizeof TT+sizeof UU+sizeof SG+sizeof AW+sizeof A3+256;
err=0;calls=0;kk=0;nmov=0;nin=256;nO=256;co=0;
for(u32 m=0;m<NMAX;m++)uses[m]=0;
pass=0;trace();
if(nn>NMAX){err=1;return (int)err;}
info.nodes0=nn;
sortent();
for(u32 e=0;e<nE;e++)uses[oid[e]]++;
pass=1;
for(u32 w=0;w<32;w++){fb[w]=0;pb[w]=0;}
for(u32 r=0;r<926;r++)if(r<256||r>=512)release(r);
for(u32 i=0;i<nO;i++)if(onode[i]){u32 t=tgt(i);pb[t>>5]|=1u<<(t&31);}
while(co<nE&&oid[co]<=nin){oreg[oix[co]]=IR(oid[co]-1);co++;}
for(u32 n=1;n<=nin;n++)if(!uses[n])release(IR(n-1));
trace();
{u32 nt=0;
for(u32 i=0;i<nO;i++)if(onode[i]&&oreg[i]!=tgt(i)){mvi[nt]=i;mvs[nt]=oreg[i];nt++;}
while(nt){
u32 k=nt;
for(u32 m=0;m<nt&&k==nt;m++){u32 hit=0;for(u32 n2=0;n2<nt;n2++)if(mvs[n2]==tgt(mvi[m]))hit=1;if(!hit)k=m;}
if(k==nt){
u32 s=mvs[0],tmp=take(-1,0,0);
emit('M',tmp,s,0);nmov++;
for(u32 n2=0;n2<nt;n2++)if(mvs[n2]==s)mvs[n2]=tmp;
continue;
}
u32 i=mvi[k],s=mvs[k];
for(u32 n2=k;n2+1<nt;n2++){mvi[n2]=mvi[n2+1];mvs[n2]=mvs[n2+1];}
nt--;
emit('M',tgt(i),s,0);nmov++;
}
}
for(u32 i=0;i<nO;i++)if(onode[i]&&oneg[i]){u32 b=32*(7-(i>>5))+(i&31);info.q[b>>3]|=(u8)(1u<<(b&7));}
for(u32 i=0;i<nO;i++)if(!onode[i])emit('S',tgt(i),oneg[i]?1:0,0);
info.calls=calls;info.ninst=kk;info.err=err;info.moves=nmov;
{u32 top=0;
for(u32 k=0;k<kk;k++){
u32 op=code[k][0],w=code[k][1]|(u32)code[k][2]<<8|(u32)code[k][3]<<16|(u32)code[k][4]<<24,d=w&1023u,a=(w>>10)&1023u,b=(w>>20)&1023u,m=0;
if(op=='^'||op=='&'||op=='|'){m=d>a?d:a;m=m>b?m:b;}
else if(op=='N'||op=='M')m=d>a?d:a;
else if(op=='S')m=d;
else continue;
if(m+1>top)top=m+1;
}
info.nreg=top;}
return (int)err;
}
'''
if __name__ == "__main__":
	arg = sys.argv[1] if len(sys.argv) > 1 else ""
	if arg == "--selftest":
		sys.exit(0 if selftest() else 1)
	elif arg == "--ledger":
		lg=ledger()
		print_ledger(lg)
		pr=prog()
		ph,filt,body,code,tmax=machine_constants(pr)
		print("PH", ph, "filter", filt, "body", body, "code bytes", code, "tmax", tmax, "generator calls", pr.calls, "records", pr.instr, "moves", pr.moves)
		s1,s2=phase_bytes(code,tmax)
		print("memory bytes", s2, "limit", MEM_LIMIT, "setup phase bytes", s1, "peak", max(s1, s2), "fits", max(s1, s2) <= MEM_LIMIT)
		print("other code instructions", other_code(pr), "recovery program records executed per call", packed_ops(), "records", rec().instr, "init records", len(rec().init), "registers", pr.nregs)
	elif arg == "--text":
		sys.stdout.write(text())
	elif arg == "--gen-c":
		sys.stdout.write(GEN_C)
	elif arg == "--loss":
		for k,v in loss(plan(256)).items():
			print(k,v)
	else:
		json.dump(serve(json.load(sys.stdin)),sys.stdout)
