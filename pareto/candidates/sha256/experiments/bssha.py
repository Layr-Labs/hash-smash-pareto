import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt,log,log2,log1p,exp,comb
M32=0xFFFFFFFF
ROUNDS=58
UNIT=4408
LANES,ALL=256,(1<<256)-1
IV=(0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19)
K=(0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,
     0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
     0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,
     0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
     0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,
     0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2)
PAD2=bytes([128])+bytes(55)+(512).to_bytes(8,"big")
STATIC_SLP_SHA256="0c19492a317afde948ed5acfb878bee780a2747bd442f629e4c614287e811cb5"
STATIC_C_SHA256="fe6b2206db7cbb57cecb3b9248ddecd51f6b4a42c109ce77505ef29d7dfc9455"
STATIC_WASM_SHA256="3b3b11a3b1b70708905429cf75eec9e68a013994aeeed9827a529b94178ac006"
POLARITY_Q=int("879ed530050ccf1102735e2f7c0a6ed3a4977991f19b3ca80daff60d78a921de",16)
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
OFF=(0,0,0xdbce7a42,0xaaf3823d,0x8d41a28c,0x7f214e02,0x6423f959,0x08000000)
PREFIX_WORDS=tuple(_anchor_prefix([(K[9]-K[8])&M32,(-K[9])&M32,0,0,0,0,0,0]))
def _build_ws(w,prefix=None):
	prefix=PREFIX_WORDS if prefix is None else prefix
	ws=[0]*16
	for i in range(PRE):
		ws[i]=prefix[i]
	for k in range(8):
		ws[VARBASE+k]=(w[k]+OFF[k])&M32
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
		bw=[E[r-3],E[r-2],A[r-7],A[r-6],(T[r-5]+_MAJ(A[r-6],A[r-7],A[r-8]))&M32,T[r-4],
              (E[r-5]+((~E[r-2])&E[r-4])+ws[r-2])&M32,(E[r-4]+ws[r-1])&M32]
		return [bw[PERM[k]] for k in range(8)]
def enc_invert(enc):
	r=ROUNDS
	if TAILB:
		bw=[0]*8
		for k in range(8):
			bw[PERM[k]]=enc[k]
		e3,e2,a7,a6,Q,T4,X,Y=bw
		a5=(Q+_SIG0(a6))&M32
		a4=(T4+_SIG0(a5)+_MAJ(a5,a6,a7))&M32
		a3=(e3-a7+_SIG0(a4)+_MAJ(a4,a5,a6))&M32
		a2=(e2-a6+_SIG0(a3)+_MAJ(a3,a4,a5))&M32
		t1=(X+(e2&e3)+_SIG1(e2)+K[r-2])&M32
		e1=(a5+t1)&M32
		a1=(t1+_SIG0(a2)+_MAJ(a2,a3,a4))&M32
		t0=(Y+_SIG1(e1)+_CH(e1,e2,e3)+K[r-1])&M32
		return [(t0+_SIG0(a1)+_MAJ(a1,a2,a3))&M32,a1,a2,a3,(a4+t0)&M32,e1,e2,e3]
def f_scalar(x,n=256):
	return int_of(enc_words(words_of(x)))&((1<<n)-1)
PAD2W=tuple(int.from_bytes(PAD2[4*i:4*i+4],"big") for i in range(16))
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
	return b"".join(v.to_bytes(4,"big") for v in _build_ws(words_of(x)))
RP,RMASK=128,M32|(M32<<128)
WM,KM=0,ROUNDS
def _rep(v):
	return v|(v<<RP)
def _state5():
	a,b,c,d,e,f,g,h=IV
	for i in range(PRE):
		t1=(h+(_ror(e,6)^_ror(e,11)^_ror(e,25))+((e&f)^(~e&g))+K[i]+PREFIX_WORDS[i])&M32
		t2=((_ror(a,2)^_ror(a,13)^_ror(a,22))+((a&b)^(a&c)^(b&c)))&M32
		a,b,c,d,e,f,g,h=(t1+t2)&M32,a,b,c,(d+t1)&M32,e,f,g
	return [a,b,c,d,e,f,g,h],b^c
class RecProg:
	def __init__(self):
		n=ROUNDS
		self.imm,self.init=[],[]
		MASK,T0,T1,T2,T3,T4=0,11,12,13,14,15
		ST,PB=list(range(1,9)),[9,10]
		def S(out,x,v):
			self.imm.append(v)
			out.append(("S",x,len(self.imm)-1,0))
		self.init.append(("R",2,0,0))
		S(self.init,MASK,RMASK)
		for i in range(n):
			S(self.init,T0,_rep(K[i]))
			self.init.append(("T",KM+i,T0,2))
		constpos={i: PREFIX_WORDS[i] for i in range(PRE)}
		constpos.update(TAILMAP)
		for i in sorted(constpos):
			S(self.init,T0,_rep(constpos[i]))
			self.init.append(("T",WM+i,T0,2))
		def sigma(out,dst,src,rs,shr):
			out+=[("<",T0,src,32),("|",T0,src,T0),(">",dst,T0,rs[0]),(">",T1,T0,rs[1]),("^",dst,dst,T1)]
			out+=[(">",T1,src,shr) if shr else (">",T1,T0,rs[2]),("^",dst,dst,T1),("&",dst,dst,MASK)]
		def rnd(out,st,pi,addrw,ptr):
			a,b,c,d,e,f,g,h=st
			P,PN=PB[pi],PB[1-pi]
			sigma(out,T2,e,(6,11,25),0)
			out+=[("^",T3,f,g),("&",T3,e,T3),("^",T3,g,T3)]
			out+=[("L",T4,addrw,ptr),("L",T0,addrw+KM,ptr),("+",T4,T4,T0)]
			out+=[("+",T2,h,T2),("+",T2,T2,T3),("+",T2,T2,T4)]
			sigma(out,T3,a,(2,13,22),0)
			out+=[("^",PN,a,b),("&",T0,PN,P),("^",T0,T0,b),("+",T3,T3,T0)]
			out+=[("+",h,d,T2),("&",h,h,MASK),("+",d,T2,T3),("&",d,d,MASK)]
			return [d,a,b,c,h,e,f,g],1-pi
		assert WM==0
		pre=(n-NTAIL-PRE)%4
		st,pi=list(ST),0
		straight=[]
		for j in range(pre):
			st,pi=rnd(straight,st,pi,WM+PRE+j,2)
		body,stl,pil=[],list(st),pi
		for j in range(4):
			stl,pil=rnd(body,stl,pil,j,0)
		assert stl==st and pil==pi,"the round loop does not rename back"
		ra,rb,rc,rd,re,rf,rg,rh=st
		def t1(out,dst,hr,er,fr,gr,wi,mask=True):
			sigma(out,T2,er,(6,11,25),0)
			out+=[("^",T3,fr,gr),("&",T3,er,T3),("^",T3,gr,T3)]
			out+=[("L",T4,WM+wi,2),("L",T0,KM+wi,2),("+",T4,T4,T0)]
			out+=[("+",T2,hr,T2),("+",T2,T2,T3),("+",T2,T2,T4)]
			if mask:
				out.append(("&",dst,T2,MASK))
		tail=[]
		if TAILB:
			R5,QQ,E5,R4,E4,E3,E2,XX,YY=range(16,25)
			t1(tail,R5,rh,re,rf,rg,n-6)
			tail+=[("+",E5,rd,R5),("&",E5,E5,MASK)]
			t1(tail,R4,rg,E5,re,rf,n-5)
			tail+=[("+",E4,rc,R4),("&",E4,E4,MASK)]
			t1(tail,T2,rf,E4,E5,re,n-4,False)
			tail+=[("+",E3,rb,T2),("&",E3,E3,MASK)]
			t1(tail,T2,re,E3,E4,E5,n-3,False)
			tail+=[("+",E2,ra,T2),("&",E2,E2,MASK)]
			tail+=[("&",T3,E2,E4),("^",T3,T3,E4),("L",T4,WM+n-2,2),("+",XX,E5,T3),("+",XX,XX,T4),("&",XX,XX,MASK)]
			tail+=[("L",T4,WM+n-1,2),("+",YY,E4,T4),("&",YY,YY,MASK)]
			tail+=[("^",T0,ra,rb),("&",T0,T0,PB[pi]),("^",T0,T0,rb),("+",QQ,R5,T0),("&",QQ,QQ,MASK)]
			fb=[E3,E2,rb,ra,QQ,R4,XX,YY]
			self.fin=[fb[PERM[k]] for k in range(8)]
		head=[]
		for k in range(8):
			if OFF[k]:
				S(head,T0,_rep(OFF[k]))
				head+=[("+",self.fin[k],self.fin[k],T0),("&",self.fin[k],self.fin[k],MASK)]
			head.append(("T",WM+VARBASE+k,self.fin[k],2))
		state,pab=_state5()
		for k in range(8):
			S(head,ST[k],_rep(state[k]))
		S(head,PB[0],_rep(pab))
		A_,B_,C_,D_,E0,E1=19,20,21,22,23,24
		sched=[("L",A_,0,0),("L",B_,1,0),("L",C_,9,0),("L",D_,14,0)]
		sigma(sched,E0,B_,(7,18,0),3)
		sigma(sched,E1,D_,(17,19,0),10)
		sched+=[("+",A_,A_,E0),("+",A_,A_,C_),("+",A_,A_,E1),("&",A_,A_,MASK),("T",16,A_,0)]
		self.blocks=[("S",head),("L",sched,0,n-16,1),("S",straight),("L",body,PRE+pre,n-NTAIL-PRE-pre,4),("S",tail)]
		self.flat=[]
		for blk in self.blocks:
			if blk[0]=="S":
				self.flat+=blk[1]
			else:
				_,bd,start,count,stepw=blk
				self.flat+=[("R",0,start,0),("R",1,start+count,0)]
				top=len(self.flat)
				self.flat+=bd+[("A",0,stepw,0),("C",0,1,0),("J",top,0,0)]
		self.instr=len(self.init)+len(self.flat)
		self.mem=[0]*(2*n)
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
			if op=="^": r[x]=r[y]^r[z]
			elif op=="&": r[x]=r[y]&r[z]
			elif op=="|": r[x]=r[y]|r[z]
			elif op=="+": r[x]=(r[y]+r[z])&ALL
			elif op==">": r[x]=r[y]>>z
			elif op=="<": r[x]=(r[y]<<z)&ALL
			elif op=="S": r[x]=self.imm[y]
			elif op=="L": r[x]=mem[p[z]+y]
			elif op=="T": mem[p[z]+x]=r[y]
			elif op=="R": p[x]=y
			elif op=="A": p[x]+=y
			elif op=="C": flag=p[x]<p[y]
			elif op=="J" and flag: pc=x
		return cnt
	def _compile(self):
		def line(rc,pad,loop):
			op,x,y,z=rc
			if op in "^&|": return "%sr[%d] = r[%d] %s r[%d]"%(pad,x,y,op,z)
			if op=="+": return "%sr[%d] = r[%d] + r[%d]"%(pad,x,y,z)
			if op==">": return "%sr[%d] = r[%d] >> %d"%(pad,x,y,z)
			if op=="<": return "%sr[%d] = (r[%d] << %d) & ALL"%(pad,x,y,z)
			if op=="S": return "%sr[%d] = IM[%d]"%(pad,x,y)
			if op=="L": return "%sr[%d] = m[%s + %d]"%(pad,x,"q" if loop and z==0 else "0",y)
			return "%sm[%s + %d] = r[%d]"%(pad,"q" if loop and z==0 else "0",x,y)
		src=["def step(r, m):"]
		for blk in self.blocks:
			if blk[0]=="S":
				src+=[line(rc,"    ",False) for rc in blk[1]]
			else:
				src.append("    for q in range(%d, %d, %d):"%(blk[2],blk[2]+blk[3],blk[4]))
				src+=[line(rc,"        ",True) for rc in blk[1]]
		ns={"ALL": ALL,"IM": self.imm}
		exec(compile("\n".join(src)+"\n","<recovery>","exec"),ns)
		self.fast=ns["step"]
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
SYN={
	(0,7): ((('x',1,2),('x',0,5),('x',0,2),('x',3,6),('o',4,8),('o',5,7),('x',9,10),('x',6,10),('x',4,6)),((13,1),(11,1),(12,1))),
	(0,8): ((('x',1,2),('x',0,5),('x',3,6),('o',4,7),('x',1,6),('x',4,6),('x',6,8),('o',5,9),('x',8,12)),((10,0),(13,1),(11,1))),
	(0,16): ((('x',2,4),('x',0,5),('x',3,5),('x',1,6),('x',5,8),('a',4,7),('x',5,10),('o',6,9),('x',10,12)),((8,1),(13,0),(11,0))),
	(0,31): ((('x',2,4),('x',3,5),('a',4,6),('x',5,7),('x',0,5),('x',1,5),('o',9,10),('x',7,11),('x',0,10)),((13,0),(12,0),(8,1))),
	(1,7): ((('x',0,2),('x',4,5),('x',0,1),('x',1,6),('x',3,8),('o',5,7),('o',4,9),('x',10,11)),((8,1),(12,1),None)),
	(1,8): ((('x',0,2),('x',4,5),('x',0,1),('x',1,6),('x',3,8),('o',5,7),('o',4,9),('x',10,11)),((8,0),(12,1),None)),
	(1,16): ((('x',0,4),('x',1,5),('x',3,5),('x',1,2),('a',4,7),('o',6,8),('x',9,10),('x',2,6)),((12,1),(11,0),None)),
	(1,31): ((('x',0,4),('x',1,5),('x',3,5),('x',1,2),('a',4,7),('o',6,8),('x',9,10),('x',2,6)),((12,0),(11,0),None)),
}
class Gen:
	def __init__(self,n):
		self.n,self.nodes,self.calls=n,[("c",)],0
		self.ahi,self.chi=0,0
		self.inputs,self.cse=[],{}
		for j in range(n):
			self.nodes.append(("v",j))
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
		return (self.mk("x",x[0],y[0]),x[1]^y[1])
	def AND(self,x,y):
		self.calls+=1
		if x[0]==0:
			return ZERO if x[1]==0 else y
		if y[0]==0:
			return ZERO if y[1]==0 else x
		if x[0]==y[0]:
			return x if x[1]==y[1] else ZERO
		if x[1]==0 and y[1]==0:
			return (self.mk("a",x[0],y[0]),0)
		if x[1]==1 and y[1]==1:
			return (self.mk("o",x[0],y[0]),1)
		p,q=(x,y) if x[1]==0 else (y,x)
		return self.XOR(p,(self.mk("a",p[0],q[0]),0))
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
		if tm==2:
			gates,outputs=SYN[(int(oU),x[1]|y[1]<<1|z[1]<<2|u[1]<<3|U[1]<<4)]
			v=[(x[0],0),(y[0],0),(z[0],0),(u[0],0),(U[0],0)]
			for op,a,b in gates:
				v.append((self.XOR,self.AND,self.OR)["xao".index(op)](v[a],v[b]))
			s,carry_U,carry_u=outputs
			return (v[s[0]][0],s[1]),(None if oU else (v[carry_u[0]][0],carry_u[1])),(v[carry_U[0]][0],carry_U[1])
		X,A,O=self.XOR,self.AND,self.OR
		if tm:
			w=X(y,U); n8=X(z,w); s=X(x,n8); n6=O(U,X(y,u))
			return s,(None if oU else X(n6,w)),X(n6,A(n8,X(x,w)))
		n5=X(z,U); n9=X(x,n5); s=X(y,n9); n8=O(U,X(z,u)); n6=X(x,y); n11=A((n6[0],n6[1]^1),n9)
		return s,(None if oU else X(n5,n11)),X(n8,n11)
	def add3(self,A,B,C):
		s=[None]*32
		s[0],U=self.fa(A[0],B[0],C[0])
		u=ZERO
		for i in range(1,31):
			a,b,c=A[i],B[i],C[i]
			orders=((a,b,c),(a,c,b),(b,a,c),(b,c,a),(c,a,b),(c,b,a))
			h=_COL_HINTS[self.chi]; self.chi+=1
			key=(int(i==30),a[1]|b[1]<<1|c[1]<<2|u[1]<<3|U[1]<<4)
			if h==12 and key in SYN:
				s[i],u,U=self._col(a,b,c,u,U,2,i==30)
			else:
				h=0 if h==12 else h
				s[i],u,U=self._col(*orders[h//2],u,U,h&1,i==30)
		s[31]=self.XOR(self.XOR(self.XOR(A[31],B[31]),C[31]),U)
		return s
	def _baseline(self,cv,vs):
		if len(vs)>2:
			vs=[self.add3(*vs[:3])]+vs[3:]
		bb=max(range(len(vs)),key=lambda k: (_tz((cv-k)&M32),-k)) if CIN and cv else 0
		s=vs[0]
		for k,w in enumerate(vs[1:]):
			s=self.add(s,w,ONE if k<bb else ZERO)
		cv=(cv-bb)&M32
		return self.add(s,_constw(cv)) if cv else s
	def _choice(self,op,mask):
		pick=[op[i] for i in range(len(op)) if mask>>i&1]
		rest=[op[i] for i in range(len(op)) if not (mask>>i&1)]
		first=self.add3(*pick)
		return first if not rest else self.add(first,rest[0]) if len(rest)==1 else self.add3(first,*rest)
	def addm(self,*ws):
		cv,vs=0,[]
		for w in ws:
			if all(x[0]==0 for x in w):
				cv+=sum(x[1]<<i for i,x in enumerate(w))
			else:
				vs.append(w)
		cv&=M32
		if not vs:
			return _constw(cv)
		op=list(vs)+([_constw(cv)] if cv else [])
		if len(op)<3:
			return self._baseline(cv,vs)
		h=_ADD_HINTS[self.ahi]; self.ahi+=1
		return self._baseline(cv,vs) if h==0 else self._choice(op,h)
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
def _add_u(g,A,u,B_fix):
	s,c=[],ZERO
	for i in range(32):
		if i==0:
			s.append(u[0]); c=g.AND(A[0],B_fix()) if A[0]!=ZERO else g.AND(A[0],ZERO)
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
def _rnd2(g,st,Wd):
	a,b,c,d,e,f,gg,h,prev,hg=st
	S1=_sigma(g,e,6,11,25,False)
	fg,tt,u=[],[],[]
	for j in range(32):
		fg.append(g.XOR(f[j],gg[j]))
		tt.append(g.AND(e[j],fg[j]))
		u.append(g.XOR(hg[j],tt[j]))
	t1=_add_u(g,h,u,lambda: g.XOR(gg[0],tt[0]))
	t1=g.addm(t1,S1,*Wd)
	S0=_sigma(g,a,2,13,22,False)
	ab,mj=[],[]
	for j in range(32):
		ab.append(g.XOR(a[j],b[j]))
		if ab[j][0] and prev[j][0] and ab[j][0]!=prev[j][0] and ab[j][1]!=prev[j][1]:
			mj.append(g.XOR(g.AND((ab[j][0],ab[j][1]^1),prev[j]),c[j]))
		else:
			mj.append(g.XOR(g.AND(ab[j],prev[j]),b[j]))
	ne=g.add(d,t1)
	na=g.addm(t1,S0,mj)
	return (na,a,b,c,ne,e,f,gg,ab,fg)
def _t1hg(g,e,f,gg,h,hg,Wd,sig=True):
	fg,tt,u=[],[],[]
	for j in range(32):
		fg.append(g.XOR(f[j],gg[j]))
		tt.append(g.AND(e[j],fg[j]))
		u.append(g.XOR(hg[j],tt[j]))
	t=_add_u(g,h,u,lambda: g.XOR(gg[0],tt[0]))
	return (g.addm(t,_sigma(g,e,6,11,25,False),*Wd) if sig else g.addm(t,*Wd)),fg
def _net_u(G=Gen):
	g=G(256)
	Y=[[g.inputs[32*(7-k)+j] for j in range(32)] for k in range(8)]
	W=[None]*16
	for i in range(PRE):
		W[i]=_constw(PREFIX_WORDS[i])
	for k in range(8):
		pos=VARBASE+k
		W[pos]=g.addm(Y[k],_constw(OFF[k])) if OFF[k] else Y[k]
	for pos,val in TAILMAP.items():
		W[pos]=_constw(val)
	def wd(i):
		if VARBASE<=i<16:
			residual=(K[i]+OFF[i-VARBASE])&M32
			return (Y[i-VARBASE],_constw(residual)) if residual else (Y[i-VARBASE],)
		return (_constw(K[i]),W[i])
	v=[_constw(w) for w in IV]
	st=tuple(v)+([g.XOR(v[1][j],v[2][j]) for j in range(32)],[g.XOR(v[7][j],v[6][j]) for j in range(32)])
	for i in range(ROUNDS):
		if i>=16:
			W.append(g.addm(W[i-16],_sigma(g,W[i-15],7,18,3,True),W[i-7],_sigma(g,W[i-2],17,19,10,True)))
		if i<ROUNDS-NTAIL:
			st=_rnd2(g,st,wd(i))
	r=ROUNDS
	if TAILB:
		a6,a7,a8,a9,e6,e7,e8,e9,prev,hg=st
		T5,fg=_t1hg(g,e6,e7,e8,e9,hg,wd(r-6))
		e5=g.add(a9,T5)
		mj=[]
		for j in range(32):
			ab=g.XOR(a6[j],a7[j])
			if ab[0] and prev[j][0] and ab[0]!=prev[j][0] and ab[1]!=prev[j][1]:
				mj.append(g.XOR(g.AND((ab[0],ab[1]^1),prev[j]),a8[j]))
			else:
				mj.append(g.XOR(g.AND(ab,prev[j]),a7[j]))
		Q=g.add(T5,mj)
		T4,fg=_t1hg(g,e5,e6,e7,e8,fg,wd(r-5))
		e4=g.add(a8,T4)
		T3,fg=_t1hg(g,e4,e5,e6,e7,fg,wd(r-4))
		e3=g.add(a7,T3)
		T2,fg=_t1hg(g,e3,e4,e5,e6,fg,wd(r-3))
		e2=g.add(a6,T2)
		X=g.addm(e5,[g.AND((e2[j][0],e2[j][1]^1),e4[j]) for j in range(32)],W[r-2])
		bw=[e3,e2,a7,a6,Q,T4,X,g.add(e4,W[r-1])]
		out=[bw[PERM[k]] for k in range(8)]
		assert g.ahi==len(_ADD_HINTS) and g.chi==len(_COL_HINTS)
		return g,[t for w in out for t in w]
class BGen(Gen):
	"""Byte-exact Python mirror of the bounded C builder and allocator."""
	def __init__(self,n,run,pas):
		self.n,self.run,self.pas,self.calls=n,run,pas,0
		self.ahi=self.chi=0
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
		if k>=76034:
			self.run.err=1
			return 0
		if self.pas==0:
			if self.run.uses[a]==255 or self.run.uses[b]==255:
				self.run.err=6
			self.run.uses[a]+=1; self.run.uses[b]+=1
		else:
			self.run.alloc(op,k,a,b)
		return k
	def mk(self,op,x,y):
		self.calls+=1
		if x>y:
			x,y=y,x
		a,b=x,y
		if b<=256:
			key=({"x": 1,"a": 2,"o": 3}[op])|(a<<2)|(b<<11)
			p=((key*2654435761)&M32)>>22
			probes=1
			while self.cse_k[p]:
				self.max_probe=max(self.max_probe,probes)
				if self.cse_k[p]==key:
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
		self.uses,self.err,self.records=[0]*76034,0,[]
	def emit(self,op,d,a,b):
		if len(self.records)>=75777 or max(d,a,b)>1023:
			self.err=5
			return
		self.records.append((op,d,a,b))
	def take(self,prefer=None):
		if prefer is not None and self.free>>prefer&1:
			r=prefer
		else:
			m=self.free&~self.pend or self.free
			if not m:
				self.err=8
				return 0
			r=(m&-m).bit_length()-1
		self.free&=~(1<<r)
		return r
	def alloc(self,op,k,x,y):
		self.uses[x]-=1; self.uses[y]-=1
		dx,dy=self.uses[x]==0,self.uses[y]==0
		want=256+self.order[self.co][1] if self.co<len(self.order) and self.order[self.co][0]==k else None
		dst=None
		if want is not None:
			if self.free>>want&1:
				dst=self.take(want)
			elif dx and self.reg[x]==want:
				dst=want
			elif dy and self.reg[y]==want:
				dst=want
		if dst is None:
			if dx and (not (self.pend>>self.reg[x]&1) or self.reg[x]==want):
				dst=self.reg[x]
			elif dy and (not (self.pend>>self.reg[y]&1) or self.reg[y]==want):
				dst=self.reg[y]
		if dx and self.reg[x]!=dst:
			self.free|=1<<self.reg[x]
		if dy and self.reg[y]!=dst:
			self.free|=1<<self.reg[y]
		if dst is None:
			dst=self.take()
		if dst==want:
			self.pend&=~(1<<dst)
		self.emit({"x": 1,"a": 2,"o": 3}[op],dst,self.reg[x],self.reg[y])
		self.reg[k]=dst
		while self.co<len(self.order) and self.order[self.co][0]==k:
			self.oreg[self.order[self.co][1]]=dst
			self.co+=1
		if not self.uses[k]:
			self.err=9
			self.free|=1<<dst
	def run(self):
		g0,out0=_net_u(lambda n: BGen(n,self,0))
		nodes,self.calls=g0.nn,g0.calls
		self.onode=[x[0] for x in out0]; self.oneg=[x[1] for x in out0]
		self.order=sorted((n,i) for i,n in enumerate(self.onode) if n)
		for n,_ in self.order:
			self.uses[n]+=1
		self.free=sum(1<<r for r in range(1021) if r<256 or r>=512)
		self.pend=sum(1<<(256+i) for i,n in enumerate(self.onode) if n)
		self.reg={n: INREG(n-1) for n in range(1,257)}
		self.oreg,self.co=[0]*256,0
		while self.co<len(self.order) and self.order[self.co][0]<=256:
			n,i=self.order[self.co]; self.oreg[i]=INREG(n-1); self.co+=1
		for n in range(1,257):
			if not self.uses[n]:
				self.free|=1<<INREG(n-1)
		g1,out1=_net_u(lambda n: BGen(n,self,1))
		self.calls+=g1.calls
		self.max_probe=max(g0.max_probe,g1.max_probe)
		assert self.max_probe<=CSE_PROBE_LIMIT
		assert out1==out0
		todo=[(i,self.oreg[i]) for i,n in enumerate(self.onode) if n and self.oreg[i]!=256+i]
		moves=0
		while todo:
			srcs=[s for _,s in todo]
			k=next((k for k,(i,s) in enumerate(todo) if 256+i not in srcs),None)
			if k is None:
				s,t=todo[0][1],self.take(); self.emit(4,t,s,0); moves+=1
				todo=[(i,t if r==s else r) for i,r in todo]
			else:
				i,s=todo.pop(k); self.emit(4,256+i,s,0); moves+=1
		for i,n in enumerate(self.onode):
			if not n:
				self.emit(5,256+i,self.oneg[i],0)
		top=max(max(r[1:4]) if r[0]<=3 else max(r[1:3]) if r[0]==4 else r[1] for r in self.records)+1
		q=sum(self.oneg[i]<<(32*(7-i//32)+i%32) for i in range(256) if self.onode[i])
		counts=[sum(r[0]==op for r in self.records) for op in (1,2,3)]
		info=(len(self.records),top,nodes,self.calls,moves,self.err,*counts,len(self.records)*BODY_BYTES,16384,76034,GEN_STATE_BYTES,4061,GEN_CONSTANT_BYTES)
		return info,q,self.records
def bounded_check(pr):
	info,q,records=BoundedEmitter().run()
	expect=(75777,1021,76034,316080,0,0,59653,9582,6542,303108,16384,76034,GEN_STATE_BYTES,4061,GEN_CONSTANT_BYTES)
	py=[({"^": 1,"&": 2,"|": 3,"M": 4,"S": 5}[o],d,a,b) for o,d,a,b in pr.recs]
	a,b=packed_body(records),packed_body(py)
	assert info[:3]==expect[:3] and info[4:]==expect[4:] and q==pr.qint==POLARITY_Q and not any(pr.pin[:122]) and info[1]==pr.nregs==1021<1024 and len(a)==4*info[0]
	assert hashlib.sha256(GEN_C.encode()).hexdigest()==STATIC_C_SHA256
	assert hashlib.sha256(a).hexdigest()==STATIC_SLP_SHA256 and a==b
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
	reg=dict(fixed)
	st=dict(free=sum(1<<r for r in free0 if r not in fixed.values()),pend=sum(1<<tgt[i] for i,o in enumerate(outs) if o[0]),moves=0)
	def take(prefer=None):
		f=st["free"]
		if prefer is not None and f>>prefer&1:
			r=prefer
		else:
			m=f&~st["pend"] or f
			assert m,"out of registers"
			r=(m&-m).bit_length()-1
		st["free"]&=~(1<<r)
		return r
	def release(r):
		st["free"]|=1<<r
	for v,r in fixed.items():
		if uses[v]==0:
			release(r)
	for k in range(nin+1,len(nodes)):
		op,x,y=nodes[k]
		uses[x]-=1
		uses[y]-=1
		dying=[v for v in (x,y) if uses[v]==0]
		w,dst=want.get(k),None
		if w is not None:
			if st["free"]>>w&1:
				dst=take(w)
			elif any(reg[v]==w for v in dying):
				dst=w
		if dst is None:
			for v in dying:
				if not st["pend"]>>reg[v]&1 or reg[v]==w:
					dst=reg[v]
					break
		for v in dying:
			if reg[v]!=dst:
				release(reg[v])
		if dst is None:
			dst=take()
		reg[k]=dst
		if dst==w:
			st["pend"]&=~(1<<w)
		E(({"x": "^","a": "&","o": "|"}[op],dst,reg[x],reg[y]))
		if uses[k]==0:
			raise AssertionError("dead gate")
	todo=[(i,reg[o[0]]) for i,o in enumerate(outs) if o[0] and reg[o[0]]!=tgt[i]]
	while todo:
		srcs=[s for _,s in todo]
		k=next((k for k,(i,s) in enumerate(todo) if tgt[i] not in srcs),None)
		if k is None:
			s=todo[0][1]
			tmp=take()
			E(("M",tmp,s,0))
			st["moves"]+=1
			todo=[(j,tmp if u==s else u) for j,u in todo]
			continue
		i,s=todo.pop(k)
		E(("M",tgt[i],s,0))
		st["moves"]+=1
	for i,o in enumerate(outs):
		if o[0]==0:
			E(("S",tgt[i],1 if o[1] else 0,0))
	return st["moves"]
def INREG(j):
	return 256+32*(7-j//32)+j%32
def assemble():
	R=[]
	g,outs=_net_u()
	_QM[:]=[sum(1<<(32*(7-i//32)+i%32) for i,o in enumerate(outs) if o[0] and o[1])]
	moves=_alloc(g,256,{j+1: INREG(j) for j in range(256)},outs,[256+i for i in range(256)],range(REGISTERS),R.append)
	return R,moves,2*g.calls
def packed_body(recs):
	out=[]
	for op,d,a,b in recs:
		o={"^":1,"&":2,"|":3,"M":4,"S":5}.get(op,op);assert max(d,a,b)<1024
		assert BODY_BYTES==4 and 1<=o<=3;out.append(((o-1)|(d<<2)|(a<<12)|(b<<22)).to_bytes(4,"little"))
	return b"".join(out)
def slp_sha256(recs):return hashlib.sha256(packed_body(recs)).hexdigest()
class Prog:
	def __init__(self):
		self.recs,self.moves,self.calls=assemble()
		self.q=[0]*256
		self.qint=_QM[0]
		self.qwords=[(self.qint>>(32*i))&M32 for i in range(8)]
		self.pin=[0]*256
		self.instr=self.kernel=len(self.recs)
		self.nregs=max(max(r[1:3]) if r[0] in "NM" else max(r[1:4]) if r[0] in "^&|" else r[1] for r in self.recs)+1
		assert self.instr==75777 and self.moves==0 and self.nregs==1021
		assert slp_sha256(self.recs)==STATIC_SLP_SHA256
		self.compile()
	def run(self,pc,end,regs):
		recs,n=self.recs,0
		while pc<end:
			op,d,a,b=recs[pc]
			pc+=1
			n+=1
			if op=="^":
				regs[d]=regs[a]^regs[b]
			elif op=="&":
				regs[d]=regs[a]&regs[b]
			elif op=="|":
				regs[d]=regs[a]|regs[b]
			elif op=="N":
				regs[d]=regs[a]^ALL
			elif op=="M":
				regs[d]=regs[a]
			elif op=="S":
				regs[d]=ALL if a else 0
		return n
	def compile(self):
		f={"^": "r[%d] = r[%d] ^ r[%d]","&": "r[%d] = r[%d] & r[%d]","|": "r[%d] = r[%d] | r[%d]","N": "r[%d] = r[%d] ^ ALL","M": "r[%d] = r[%d]","S": "r[%d] = ALL if %d else 0"}
		ns,fs={"ALL": ALL},[]
		for a in range(0,len(self.recs),4096):
			exec(compile("def c(r):"+chr(10)+"".join("    "+(f[o]%((d,x,y) if o in "^&|" else (d,x)))+chr(10) for o,d,x,y in self.recs[a:a+4096]),"<program>","exec"),ns)
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
CMAX=2
P_MIN=0.390000001
GRAIN=10**24
STAGE1_PLANES=32
LOOP_OPS=3
HIT_OPS=2800
EVENT_OPS=3800
CUT_OPS=4200
SLICE_OPS=1300
RECOVER_EXTRA=47
INSTR_BYTES=36
BODY_BYTES=4
CONTROL_BYTES=5
HANDLER_CODE,SETUP_CODE,RECOVERY_CODE=1000,160,47
REGISTERS=1021
REGFILE=REGISTERS*32
COUNTERS=16384
ARRAYS=64*ROUNDS
KEYB=46
SLOT_BITS=47
MEM_LIMIT=1<<20
ADVICE=0
KAPPA_256=14
CSE_PROBE_LIMIT=8
WASM_RUN_OPERATORS=154054812
WASM_OPERATOR_FACTOR=2
WASM_EMITTER_INSTR=5070
GEN_STATE_ARRAYS=dict(recent=8*24,cse_k=1024*4,cse_v=1024*4,free=32*4,pending=32*4,W=16*32*4,V=10*32*4,Y=8*32*4,word_scratch=15*32*4,TB=11*32*4,tail_scratch=4*32*4,AW=8*4,output_arrays=6*256*4,output_polarities=256,info=15*4+32,alignment=128,scalars=13*4)
GEN_CONSTANT_ARRAYS=dict(IV=8*4,K=64*4,PW=8*4,OFF=6*4,PM=6*3,PERM=8,SYN=8*36)
GEN_STATE_BYTES=sum(GEN_STATE_ARRAYS.values())
GEN_CONSTANT_BYTES=sum(GEN_CONSTANT_ARRAYS.values())
assert GEN_STATE_BYTES==23536 and GEN_CONSTANT_BYTES==658
GEN_SCRATCH=76034+GEN_STATE_BYTES+4061+GEN_CONSTANT_BYTES+4096
SETUP_FIXED=256*3100+20000
OFFSET_SEARCH_EVALS=64+1+3*192+1000
SEARCH_EVAL_OPS=1<<48
OFFSET_EVAL_OPS=SEARCH_EVAL_OPS
OFFSET_SEARCH_OPS=OFFSET_SEARCH_EVALS*OFFSET_EVAL_OPS
SELECTOR_ADD_CHOICES=131
SELECTOR_COLUMN_CHOICES=3930
SELECTOR_SEARCH_OPS=SEARCH_EVAL_OPS
SEARCH_IMAGE_INSTR=10_000
SEARCH_LOCAL_BYTES=65_536
OFFSET_SEARCH_PEAK=SEARCH_IMAGE_INSTR*INSTR_BYTES+GEN_SCRATCH+SEARCH_LOCAL_BYTES+48
SELECTOR_SEARCH_PEAK=SEARCH_IMAGE_INSTR*INSTR_BYTES+GEN_SCRATCH+SEARCH_LOCAL_BYTES+4061
TMAX_256=116129
OTHER_CODE=1729
CFG={16: dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),
       256: dict(s1=32,W=90,kappa=KAPPA_256,Sb=1<<48)}
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
	s1,W=c["s1"],c["W"]
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
	return OTHER_CODE
def machine_constants(pr=None):
	pr=pr or prog()
	filt=stage1_ops(pr.pin,STAGE1_PLANES)
	code=pr.instr*BODY_BYTES+(filt+LOOP_OPS+other_code(pr))*CONTROL_BYTES
	return pr.kernel,filt,pr.kernel+filt+LOOP_OPS,code,TMAX_256
def phase_bytes(code,tmax):
	prog()
	table=((tmax+LANES+CMAX)*SLOT_BITS+7)//8
	setup=code+COUNTERS+REGFILE+ARRAYS+WASM_EMITTER_INSTR*INSTR_BYTES+GEN_SCRATCH
	search=code+COUNTERS+REGFILE+ARRAYS+table
	return setup,search
def search_envelopes():
	# Proof Section 3 derives these bounds from the search loop dimensions.
	gate_ops=1024
	offset_raw=2*160*64*32*13*13*12*gate_ops
	selector_raw=(2*SELECTOR_ADD_CHOICES*64*32*13*13*12*gate_ops
+SELECTOR_COLUMN_CHOICES*13*13*12*gate_ops)
	assert offset_raw<SEARCH_EVAL_OPS and selector_raw<SELECTOR_SEARCH_OPS
	return offset_raw,selector_raw
def plan(n,kappa=None,Tp=None):
	if n!=256:
		c=CFG[n]
		p=_plan(n,c["Tp"],c["kappa"],0,c["Sb"])
		p["tmax"]=4*(p["Q"]//int(p["L"]))+64
		return p
	kappa=kappa or KAPPA_256
	tmax=machine_constants()[4]
	if Tp:
		return _plan(256,Tp,kappa,tmax,CFG[256]["Sb"])
	lo,hi=1.0,float(tmax+1)
	for _ in range(60):
		mid=(lo+hi)/2
		lo,hi=(mid,hi) if tail_log2(mid,tmax+1)<=-40 else (lo,mid)
	a,z=1,4097
	while z-a>1:
		m=(a+z)//2
		a,z=(m,z) if _lossq(m,lo,tmax,kappa,CFG[256]["Sb"])["P_lower"]>=P_MIN else (a,m)
	return _plan(256,a,kappa,tmax,CFG[256]["Sb"])
def ledger(p=None,pr=None):
	p=p or plan(256)
	pr=pr or prog()
	search_envelopes()
	ph,filt,body,code,_=machine_constants(pr)
	emitter=WASM_OPERATOR_FACTOR*WASM_RUN_OPERATORS+1
	parts=dict(main=body*p["B"],
                 slices=-(-p["B"]//p["Sb"])*SLICE_OPS,
                 stage1_hits=p["e2max"]*HIT_OPS,
				 events=p["tmax"]*(EVENT_OPS+6*(p["tmax"]+LANES+CMAX)),
                 cuts=p["cmax"]*CUT_OPS,
			 recovery=(2*p["capr"]+1)*(packed_ops()+RECOVER_EXTRA)+608+len(rec().init),
			 setup=SETUP_FIXED+emitter,
			 offset_search=OFFSET_SEARCH_OPS,
			 selector_search=SELECTOR_SEARCH_OPS)
	return dict(parts=parts,total=sum(parts.values()),plan=p,body=body,emitter=emitter)
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
	t["sum"]=sum(t.values())
	t["P_lower"]=1-t["sum"]
	t.update(trails=q,k=k)
	return t
_B={}
def _b256(Tp,tmax,kappa,Sb):
	if (Tp,tmax,kappa) not in _B:
		L=Fraction(1<<122,Tp)
		lo,hi=1.0,float(tmax+1)
		for _ in range(40):
			mid=(lo+hi)/2
			lo,hi=(lo,mid) if _lossq(Tp,mid,tmax,kappa,Sb)["P_lower"]>=P_MIN else (mid,hi)
		B=-(-int(hi*L/LANES)//GRAIN)*GRAIN
		while _lossq(Tp,float(B*LANES/L),tmax,kappa,Sb)["P_lower"]<P_MIN:
			B+=GRAIN
		_B[(Tp,tmax,kappa)]=B
	return _B[(Tp,tmax,kappa)]
def loss(p,rate=1.0):
	return _lossq(p["Tp"],float(p["Q"]/p["L"]),p["tmax"],p["kappa"],p["Sb"],rate)
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
		a5=g.addm(Q,S0(a6))
		a4=g.addm(T4,S0(a5),mj(a5,a6,a7))
		a3=g.addm(e3,neg(a7),_constw(1),S0(a4),mj(a4,a5,a6))
		a2=g.addm(e2,neg(a6),_constw(1),S0(a3),mj(a3,a4,a5))
		t1=g.addm(X,[g.AND(e2[j],e3[j]) for j in range(32)],S1(e2),_constw(K[ROUNDS-2]))
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
		ops,N={"x": "^","a": "&","o": "|"},g.nodes
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
			src.append("    v[%d] = v[%d] %s v[%d]"%(slot[k],slot[x],ops[o],slot[y]))
			if k not in last:
				free.append(slot[k])
		self.out=[(slot[s[0]],s[1]) for s in self.out]
		ns,self.fs={},[]
		for i in range(0,len(src),4096):
			exec(compile("def c(v):"+chr(10)+chr(10).join(src[i:i+4096])+chr(10),"<digest>","exec"),ns)
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
		ns["ALL"]=a
		o=dnet().step(self.pr.step(*(W+[0]*(256-n))),n,a)
		ns["ALL"]=ALL
		return [[(x>>256*i)&ALL for x in o] for i in range(len(P))]
	def f2(self,xs):
		return [self._low(o) for o in packed_f(xs,256,self.pr.qwords)]
	def g_scalar(self,x):
		return digest_of_state(state_words(words_of(x)))&((1<<self.n)-1)
def is_dp(x,p):
	return x&((1<<p["s1"])-1)==0 and (x>>p["s1"])&((1<<p["W"])-1)<p["Tp"]
def dp_key(x,p):
	return (((x>>p["D"])&((1<<p["kb"])-1))<<p["fb"])|((x>>p["s1"])&((1<<p["fb"])-1))
def trail_length(p,x,f2):
	for l in range(1,p["capr"]+1):
		x=f2([x])[0]
		if is_dp(x,p):
			return l
	raise Halt("recovery length")
def recover(p,r,a,b,f2):
	mask=p["N"]-1
	if a[1]<b[1]:
		a,b=b,a
	if a[1]>p["capr"]:
		raise Halt("recovery length")
	xs=[(r+a[0])&mask,(r+b[0])&mask]
	for _ in range(a[1]-b[1]):
		xs[0]=f2([xs[0]])[0]
	if xs[0]==xs[1]:
		return None
	for _ in range(b[1]+1):
		ya,yb=f2(xs)
		if ya==yb:
			if p["n"]==256:
				s0,s1=enc_invert(words_of(f_scalar(xs[0]))),enc_invert(words_of(f_scalar(xs[1])))
				assert s0==s1==state_words(words_of(xs[0])),"encoding collision is not a state collision"
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
	n,mask,pin=p["n"],p["N"]-1,eng.pin
	table,births,ts,nxt={},[0]*LANES,list(range(LANES)),LANES
	planes=pack_lanes([(r+t)&mask for t in ts],n,pin)
	cnt["inserts"]+=LANES
	batches=0
	while batches<p["B"]:
		planes=list((yield planes))
		batches+=1
		cnt["batches"]+=1
		hit=stage1(planes,p["s1"],pin)
		while hit:
			cnt["stage1_hits"]+=1
			if cnt["stage1_hits"]>p["e2max"]:
				raise Halt("stage-1 budget")
			l=(hit&-hit).bit_length()-1
			hit&=hit-1
			x=lane_value(planes,l,pin,n)
			if is_dp(x,p):
				key,length=dp_key(x,p),batches-births[l]
				cnt["finished"]+=1
				match=next((t0 for t0,stored_key in table.items() if stored_key==key),None)
				if match is not None:
					t0=match
					cnt["recoveries"]+=1
					res=recover(p,r,(t0,trail_length(p,(r+t0)&mask,eng.f2)),(ts[l],length),eng.f2)
					if res is None:
						raise Halt("recovery found no pair")
					return res
				if len(table)>=p["tmax"]:
					raise Halt("table full")
				table[ts[l]]=key
				ts[l],nxt,births[l]=nxt,nxt+1,batches
				planes=set_lane(planes,l,(r+ts[l])&mask,pin,n)
				cnt["inserts"]+=1
		if batches%p["Sb"]==0:
			for l in range(LANES):
				if batches-births[l]>=p["c"]:
					cnt["cut"]+=1
					if cnt["cut"]>p["cmax"]:
						raise Halt("cut budget")
					ts[l],nxt,births[l]=nxt,nxt+1,batches
					planes=set_lane(planes,l,(r+ts[l])&mask,pin,n)
					cnt["inserts"]+=1
	return None
class Counters(dict):
	def __missing__(self,k):
		return 0
def derive(seed,tag,bits=256):
	return int.from_bytes(hashlib.shake_256(("%s/%s"%(seed,tag)).encode()).digest((bits+7)//8),"little")&((1<<bits)-1)
def attempt(eng,p,seed,tag):
	cnt=Counters()
	try:
		res=search(eng,p,derive(seed,tag,p["n"]),cnt)
	except Halt as e:
		cnt["halt"]+=1
		res=None
	return res,cnt
N_T3=16
M_T2,B_T2=256,16
def e1_runs(trials,eng,p,tag):
	G,C,R,cur={},{},{},{}
	def adv(i,v):
		try:
			cur[i]=G[i].send(v)
			return
		except StopIteration as e:
			R[i]=e.value
		except Halt:
			C[i]["halt"]+=1
		del cur[i]
	for i,t in enumerate(trials):
		C[i]=Counters()
		G[i]=_search(eng,p,derive(t["seed"],tag,p["n"]),C[i])
		adv(i,None)
	while cur:
		ks=list(cur)
		for i,o in zip(ks,eng.wstep([cur[i] for i in ks])):
			adv(i,o)
	return R,C
def e1_rows(trials):
	R,C=e1_runs(trials,Engine(N_T3),plan(N_T3),"t")
	return [e1_obs(R.get(i),C[i]) for i in range(len(trials))]
def e1_obs(res,cnt):
	obs=dict(target_ok=int(res is not None),batches=cnt["batches"],halt=cnt["halt"])
	return (None,None,obs) if res is None else (message(res[0]),message(res[1]),obs)
def e2_trial(seed,tr,st):
	src,z=tr%3,[0]*256
	if src==0:
		xs=[derive(seed,"u%d"%i) for i in range(M_T2)]
	elif src==1:
		r=derive(seed,"r")
		xs=[(r+i)&ALL for i in range(M_T2)]
	else:
		xs,cur=[],[derive(seed,"c%d"%l) for l in range(LANES)]
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
	eid,out=req["experiment_id"],[]
	bounded_check(prog())
	if eid=="bssha-n16":
		rows=e1_rows(req["trials"])
	elif eid=="proj-k0-w256":
		st=prog()
		rows=[e2_trial(t["seed"],t["trial"],st) for t in req["trials"]]
	else:
		raise ValueError("unknown experiment")
	for t,(a,b,obs) in zip(req["trials"],rows):
		out.append({"trial": t["trial"],"message_a_hex": a.hex() if a else None,"message_b_hex": b.hex() if b else None,"observations": obs})
	return {"schema_version": 1,"trials": out}
def text():
	return "".join("%s %d %d %d\n"%r for r in prog().recs)
def t2_truth_check():
	for (last,mask),(gates,outputs) in SYN.items():
		for row in range(32):
			v=[(row>>i)&1 for i in range(5)]
			for op,a,b in gates:
				v.append(v[a]^v[b] if op=="x" else v[a]&v[b] if op=="a" else v[a]|v[b])
			logical=[v[i]^(mask>>i&1) for i in range(5)]
			total=sum(logical[:3])+(1 if logical[4] else 2*logical[3])
			s=v[outputs[0][0]]^outputs[0][1]
			carry_U=v[outputs[1][0]]^outputs[1][1]
			if last:
				assert s==total&1 and carry_U==total>>1&1
			else:
				carry_u=v[outputs[2][0]]^outputs[2][1]
				assert total==s+2*(1 if carry_U else 2*carry_u)
	return True
def selftest():
	import random
	rnd=random.Random(3)
	pr=prog()
	bounded_check(pr)
	print("bounded records and T2:",t2_truth_check())
	reg=max(max(r[1:4]) for r in pr.recs if r[0] in "^&|")+1
	print("records",pr.instr,"moves",pr.moves,"kernel",pr.kernel,"registers used",reg,"text sha256",hashlib.sha256(text().encode()).hexdigest())
	ok=reg<=REGISTERS and pr.nregs<=REGISTERS and all(r[0] in "^&|NM" for r in pr.recs)
	t=True
	for xs in [[rnd.getrandbits(256) for _ in range(LANES)] for _ in range(8)]+[[0]*LANES,[(1<<256)-1]*LANES]:
		out=lanes_of(list(pr.step(*pack_lanes(xs,256,pr.pin))),256,pr.pin)
		t&=all(out[l]==f_scalar(xs[l])^pr.qint for l in range(LANES))
	print("2,560 lanes (10 batches), full 256-bit g = f XOR q, program vs scalar walk-B encoding of state_58:",t)
	ok&=t
	rt=True
	for _ in range(10000):
		w=[rnd.getrandbits(32) for _ in range(8)]
		rt&=enc_invert(enc_words(w))==state_words(w)
	print("explicit inverse round-trips on 10,000 random states (enc_invert(enc_words) == state_words):",rt)
	ok&=rt
	regs=[0]*REGISTERS
	for j in range(256):
		regs[INREG(j)]=rnd.getrandbits(256)
	ref=list(regs)
	n=pr.run(0,len(pr.recs),regs)
	fast=list(ref)
	pr.fast(fast)
	t=n==pr.kernel and [fast[INREG(j)] for j in range(256)]==[regs[INREG(j)] for j in range(256)]
	print("logical tuple and compiled tests",n,pr.kernel,t)
	ok&=t
	cur=[rnd.getrandbits(256) for _ in range(LANES)]
	pl=pack_lanes(cur,256,pr.pin)
	for _ in range(4):
		pl=list(pr.step(*pl))
		cur=[f_scalar(x)^pr.qint for x in cur]
	t=lanes_of(pl,256,pr.pin)==cur
	print("256 lanes chained for 4 steps:",t)
	ok&=t
	e=Engine(N_T3)
	xs=[rnd.getrandbits(N_T3) for _ in range(LANES)]
	pl=pack_lanes(xs,N_T3,e.pin)
	for _ in range(5):
		pl=list(e.step(*pl))
		xs=[e.g_scalar(x) for x in xs]
	t=lanes_of(pl,N_T3,e.pin)==xs
	print("n=%d chain, 5 steps:"%N_T3,t)
	ok&=t
	xs=[rnd.getrandbits(256) for _ in range(2)]
	ref2=[f_scalar(x) for x in xs]
	t=packed_f(xs,256)==ref2 and rec().f(xs,False)==ref2 and packed_f(xs[:1],256)==ref2[:1] and rec().f([0,ALL])==[f_scalar(0),f_scalar(ALL)]
	t&=packed_f(xs,256,pr.qwords)==[f_scalar(x)^pr.qint for x in xs]
	print("recovery %d/%d vs scalar:"%(packed_ops(),rec().instr),t)
	ok&=t
	rows=[rnd.getrandbits(256) for _ in range(256)]
	t=transpose(transpose(rows))==rows and (transpose(rows)[5]>>9)&1==(rows[9]>>5)&1
	print("transpose:",t)
	xs=[rnd.getrandbits(256) for _ in range(LANES)]
	t=lanes_of(dnet().step(list(pr.step(*pack_lanes(xs,256,pr.pin)))),256,[0]*256)==[digest_of_state(state_words(words_of(x))) for x in xs]
	print("experiments' bit-sliced digest of the padded two-block message (256 lanes) vs scalar block 1 plus block 2:",t)
	ok&=t
	ok&=t
	p,found=plan(N_T3),0
	for s in range(6):
		res,cnt=attempt(e,p,"selftest/%d"%s,"t")
		if res is not None:
			found+=1
			ok&=res[0]!=res[1] and e.g_scalar(res[0])==e.g_scalar(res[1])
	print("search n=%d: %d of 6 attempts returned a verified pair"%(N_T3,found))
	ok&=found>0
	print("selftest",bool(ok))
	return ok
def print_ledger(lg):
	print({k: (str(v) if isinstance(v,Fraction) else v) for k,v in lg["plan"].items()})
	print("operations per batch (body)",lg["body"])
	for k,v in lg["parts"].items():
		print(k,v)
	print("N =",lg["total"])
	print("time_log2 = %.5f (unrounded %.8f)"%(log2(lg["total"]/UNIT)+5e-6,log2(lg["total"]/UNIT)))
GEN_C=__import__('lzma').decompress(__import__('base64').b85decode(b'{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;8JcKtz7^Yihv|k^V$dz9v%P7dRlup+2P1W3HtFk$fG*;ku`l?ZcVbPceVE<{o&p<pA)YYdKx~2d!Ow$;|v)T2N+`;FB~YBV9NOL;s(E`D&=}ZSp1tg$470Oz*gVb;h_}3Y^*t_IiQd9yLAT3lE}xb?eH-ydI8>%5ax_tI(Mw}H864&u}AhQtHG(cgn<Q5Xo%9ou*XOeUi5N5`T4A<8t`1{rj5n`woyrk?BPw`G*lTK61^?QC>VX7PEK&hV+1Y(9d${0R9?qEcnJk(p!Aq^rem>nS*UK$cYGB?HH{HoQ2pu1-y!DFy;kTMyWc!YYT+H+35XTEkX%%*2~HR*(GtnP)#p~NB<030oaE2@7H9?6#>@+le#-tQ6`-6lyUmdPf#wB~s+_;PzzH_s7$9M7LDq^D62Ydk@jfA+lrV`enB;g4G%PrgWDX%b#8uZk$jn4lkb*~YKp@OJ4x~-F=?MX3j{EuVw0z>$K`ppftTOp%Uf7t^8pU3-A!5Z5XVa>SNFxOw0(7onY7ro8ITn-L?NVcWE((9c=k=hV($l=E*|98de1iurr5XmWrud9UI|i_S#j=em)%u8@qO8(ISaZFc+iIGEBiJguwQ!y=uMGWv$N|BmWC+|-Fc68b_al{aoSH_}pdV^o>2l0-v8FVtSxeFH4}P?&f>ednDL0fS)lBMiX_yT8JLl26mn`)`dEd@7!1GC}jGyL!dMSS*dNO8rk#n&_XwbLEK=h{F;NnZms#>e3te)jFr)=WNk#y`Fvg9RhrJ5BG{+T|{Bs!i5&oJH03_Nk+K>8Xp?MxN9bRR}cAkidpb1Gqg1<KJB(a%=wr2Gw~E{dx1(^n}BOmn-R5DSjCipVT6e@DA#R@@qCKP@J4T=IFGxj{@OsV}le<m|2n6b++Nx#({`SE=0b5ounzbLiY~-qP};cc2ks^z2xMs{4}*Rq=||1^Fa&FK9BpTl>%RYW{DHW<?1+25%4ct|hp8&8}cvLi`z3bpocI$x+lMGMc8aXKl|l_pXMCkN>_O_4<*VAVKc2g!@VO;7wvMOxU}9<OejTQ*x!a`S_90qtPDNS%HHc$O{kNY<IBpxzrl0JG;?8ABEW6q%MG*(Ki!mKQT*wB1ixss(zTB`%i#|N-Kor_bU~3ztjsB9U<BA-^wa|d778!*Ei&$VW$fkO(64T*%9Hw_d~`3^cK=7RiQ0Rb#WAXT^xf=Hfuh=_3>V`lX`T-&NX^d7_fBL-l}e~(!<%Z_eVmD!u%3!b2Mwyr|g}AcJ!A8if*^O&HhW9D>@(L2!H2Ac@TQjTI5ZK{^iHOC<?cH1s#v4bY8&cK&lX&L_%YUh|7*uA9WxO30Rs`@waiwbd&5w%(TV(e9HF=^F&53avwaELELRel=$_qlp7oNI=@Pn>BpoF;U`zp4-<1lk`nc^;14-stWK4D3S1vWBBdFIo4Gy@VXRw1BC&_fHDb7l9wSTB?xXJ3(>|k+O~uWzlYD{S6u4tmdi(w4nn4n!lN-fv12lm@RQjRuQk_F8^oG&z>EgKj*PbTXSkqUHScRZt93KP(_s7k3m;M`pqQsqLslBenCf~A%x+Y;28CW)THbv8k%AOnUtOfWCVrBmkaT2i2o0ZVOLbTx0k#VilA~rMVZ-vr>)6{#i$vy`=jfwPc#@SO{5noXkL3Uuzj5v#~GcB@4g!Wxpm2k|vayqgMF7y^RR5k2X-?_xpq5A9&oL5TeB$}$Ipxk;;%UV4)CN`k@qZq!IW?P(<EtS2uC75Kyb!dGA-!;<2d*3nVfZxJQ=J}A(s%<0wd?cvHADsK0+NO2VBn8EFnHc#z6|}6_`GADCRg1iVFLkEfV-*`9Q}-CgC&Nr8#Qnw3)KwLdMgzC}bAUxegzYuuO|j=8AW1b*Nr@;oH_tK|P02@lUaRjVU|#`JDN11d{*Hj&^+>dKbJ3(oXi~|ln_^o#^$@~7r82T%122W|)0j$ENWYqXz_V5_xn|vPbFi&tz%CO^4hW^TzqcFYw$1u8wd2ueM^eHUk^G>H%xcOD)*E7Mm|RoL*ZV7F#$-Ag8{$#c)r6b>b6!?SyT>Oc=7c12@i5P!AZA)mto_G)!@FCEW*}1B>@BqvS23*VsboJzldr<dc9(3eNI`^FZvk-mhA7ss3MF{!p`>;iS9(0OEMd`GJedtt(a$mAmJ$brr)zI>?S-AZ;IN{w%|p^9W<|NQgwy>L^tU*-aTUh_?bW{k%9@2i88=(rLPv~elo2So-4NEbs}&g0=^J?^>1KSaWK(5>%!AZKsNMO6l&5HLsbC4__8%W*+`O(PExp!BQqkU{2hxEq!SiOq2ABYN;Pbw*aHF$#nLGRR=%E4S<c$(to#W}NO@MD_X+4?3HhRzzuiLo<Dpk-o?}vt%D9}WvD#9%lhYls1x4d0NzTZ)hOfuzm%d1H>#*dhkn`LhMvkNN16sB%iY~Ut31W70JibhQNbe|XWTj?@Zs_}73;eBLSM~unovJnGoASq}#4!73tPQUJhJt2>VjP+!m^Dlzmb6)UMfXr}vZC@O_-H>N6M!kUnhY}%PYi)54EKV5BzE#inR7eh>miIx@#Z-eoV<(?Y+Qnr!6yP=U(=;1%87elXZ#qZFF3)gZmpLs^M8*kaf-WksTv2vn88B2pR0F;lT)SyuEp{lQm%>bvU~`ess!;E`i-PkLrjJ;Nj2Jv$!PZgZ)F*k#E7PQ*&KCm}N=WdjOE$L+un0RSq<q%YzX7y!6-Yk593$lD5ZV!M50R%6qr-mIeSh(0Ut~o_I6VLkvaUaeCsC#7mgk!%bO<Gh6L@xWF7!ZDlHuVBF0wv~eGtRu7#flPJh<XRTpA#FoTH`fiiqGb-&Yvmv#xx**itrr-J|>O7oiBurwmOzrpY9rpw$o#xLWy*fHf)<n4!tr%lL<Jl7>yM6X#)Pv(P%C&o8da>dqY%tI5pFgdvJhR?++P2<VgRMeuK|z<dh*@B4QmWo#;Z93oReGMLAe$*s`y&qz>wL=cA;dA^fTk}%uQE9d3IgK340Xg=M@^}=owGsj;Og5Z@+;wRDQ$?mS$peccaouoFZM~$aT*Ib^LRHp|(2X$CPH2(R*o=%e)TmIZQfyoX6DTzZ8|CYMp&o!}@smbA!qb_SX9wr(8IR)%`#Ae}kYOfTt3fmF!>>0Uc3ARLC=69$s`cg)tvDNHBk07{_GZmHYeb_IXEjPty034$x7+j;Rgii3y1gW|va>*5Q)Fvjq#iEwmfCJZeU!6u>pynZk&^$GOF%vjdRv%UVDQW0|AmW@h2bZU3la=5+)zp)j8Z5?ROM|^aJf^z_8Ew{zXNMney{pLx9|Tpq8UrIRJ(rj9CKQGjw>j6Ydq<K?11$yCR8G-~{j??X9BAzVf_fa|ufmx3FdE)R9=Gh<h(gVP;VkvHQVRe!c7EtIHX#uRL<f&0R1WK$8{gzwh;9W$a=*=kpL4;ZZRX=N#fgJZSdl6T;Qt~unRiL*NUKgl((Lpd7elRm-rJme{E_BSP@A5ULwu^z?ukIc>|N06ZCZ(ASLq&*T7lmg`{`8dmd%uqFT%&&?5u1;S%gQ_QzbW|qA_>4W~))lb6PA|du21+Vgvm6hWO%CCfauvz+uOExlrZ1E(kq@oxw1>=tHw4h&C<Mk$FP8F7v~<4z_k5g!h`r03hNB<r%Rxd0o|7bZ4V46hplA(o|^01=1h>6J9iIMug%vD<1#*=Fhr%)c4D5QmiRP*}R4|3q5R36s`Wv5FH1PDt6Sh(vA;Lc}tToafHt)xxBCw5}c!uC9c5{g65V|swD=m#K?Y!KpyxDboU-JNFQQ2sZ<ySG&GhZ7yQT%sS@cEMPRjFo;C;O@iDl+oSWbf8^|@RQt=yL53!#}0UJK2qi8#DnIFh*H+!@m4|e^X99jkKn(lV|dS%Zx2fCM<*&YH#jFM{yNe*)EFtjIcyF>wdO0Z)yLKUo2;51G%L_1XD!pksokz~hu_z>;PAPxk&d3rI+<;sSLA(#zKy09s_hf7dV#~G+B5tEpwahot5JLpZZs_A+Fm^3%mS_HL$DyaM6Pp$we(1<*483XV~PvplHd82E|Fiz-6M#@qYoyFcaah%T(_B9y_Q0rIt^1k&3lb<MvoIEAgdf@_3Xl_9?g$C{V1O3*C@cGUf_YvHXISeD?O`4%&WMxuWpbHQhB$gr4)XK<{9Y$$chwfcke20EQ-)P+jZa7B+hT57kBTL--?K@#T={bHblBq!;x7{<&cCo9X1pbo|QhnHR9GDr<^f{J6wNyh8;1C@&C}ApYtZ`N^nArg%y4Ro(k1VQ1ggZ|)*pA`(g2xvvUP~qq9J4<l!R8l$%bG^sxO$d#%Q+v<PCO)-e3>0Sf$Z_uUgvQU({s)%LRBHj0p#M0^a7%d(?0&pntq3MGRcvDuw}7u(2Fu|PeKMp-9=mt&Zc?OT;OaLZ-_~PU#JAB&Wt4tZh=yZbB3mKYhpBOI(v=70#aSfhCizagpSA@pXz@`H(w1P5p{BD6~#kAC2=tBnC`ZOC!CN&={qAh6bfV&h6bscd-ivvHdF*E8eqT{TvmrIi)eTj!Fu(-7%nL2_CwA8#dAJqqD*;Cqx2WZYJWP5Y(}mly5v|b^pwe1+vx7TJCo7UU#cKeBI-D+wj;zgN9{c<Q*vMk+gY<=cpX_UxYfhNQEOoA-ZT^>XPIMXw$~+(#KNBd<&Ag~C*rJ|E}@-dT_<){%pRB*@H83KK~}=MCUN*$pvdWXwNxn_wGFivuj2e4vt|cYV3dxeBq;;r*SzGyr^7df>otejLC~t)n6lh#rnvN>ppx#75}ePrS-4IAoY~#*mkpEp+t0-R&?Bw7K0y8Zbh1tX66&JKdhj)=l<o$q$TU69bmCR`-fgE6cPI_Wp@h*<xd%mmHY>ah#7*M!I#A2BG#g-7wt*~6s{<Mg>WoT>t)d2|y!K9ZOqXpJu$2x)z1)XMIfR}(bk(t4Z8JwCAZ%K+7ld#^A{)B~kl$sph}0%)<4?NHrzYLs+8cg`?%r04-kS(TA#;6F>j^6~ql)qj1#+Mi8yM7h0)7I7O4c0-5CwxG4VV5$&4)!v*r4IT`CY&M0CJVWlx1G8u`BcK8>hnPn`1BAgdhKR+t0$ycPV625b`GjSF<15!@qn?hn5-C8+q^<TZG+v(Wbo=vUmIyUA{2)XnRod_yw8Iq(l`X{s!H2SEh|0@mYp@Vt>ShfA-^(tra<E1oUv#sf?n&Q@vK6f!HmYqHjYHt7w;j^It8PLW#x1_~H)g0z{z?NGXHRMv)k!^0wfwJq;LB<@$4>eor=YO+=${(*gIBXJCyfM>jLVVYzg(=xJm;a=j&5ca+Z*a3+QTuc0z#idv&_Y?Wb5i07N!IYVKUU=(;TT@V4B!H28;n(C#|Nn`V0c8ZqCHUyIkGRartEqnKuY5|{w*JQHblR7t$$>F#1F@!b&2e)Awf{ketpv0v9o!Mt(G$3#PHh!QEOE)=w;Rc%_S9<$(V@HU?_13(Dzpew<Ul{IWL(?khe!~&YsirOjhrP<VNCzT!+D2lQNZBb{!OZ%&fB}l(UIZ#l(9lMDz_Cc#D6k7%U!+nTb1g5nG^S1n<ub^*xpsNrFZ3+o_cDL_vPo50NWC|d7$6Jm>Jrg)N~Ib19K6adJ{2q?`RdbwJ3l%y!F&jDDXd=|P=-mH@v^sf<i2WZQLvB!WXj29<CoJ0&sw1kT3bW1wC~PD&L=WKh-q+C8_9&CE(r~J&$CJb1tqX_;f=8t?#?htf-h|`iPcKNB7T$d<pkKN-gf3gjRLuwV58s}?GK&`&d*$D=Fp%=525Iwjexr%ZqBR#BjF<h5Sk%8F90x<`FgSSnO~{&gCVwvy&B$h$9q<^z}n+n!vzfn!&N`263kjiaAR}dTh|DX8)`U0AqHD0a3(}$E|@q%ouo+hVF`OfD262TGhi2qxp5i)igVxT$He9}pk}&NcFp+<d)kqFl^xlr)+k;g0MZ{Zl1+0Zo}P<KaR}4)Nm(|=4x9pnNxL%;`zIJ9sf*VINI{dKCHpKBcnHpVS@$;;CdSjH<B5_6@F>w4YfIYhoEzaw@-u!_Lt#f)m(N93!PpdL>g6vJKV%7jtOl`JCgnM|6Ev;ga}u7zh2!i?Oo6ij8!9-%1XZL4Qr%ZkoEQd!*g)wFx`GIB<xC&;&cEPt2X;9f$0|=BNJE9$L8Idu>zq}AkQj2tsac};OK=l?$Jq5!8Ph3&n_s0t!MxvBVmNJ%S}az~Evf8!U-)`BjJ25LYa4~drvb9i8@^9fKZ^dL;u2sDc$y<XTpXLQF1!9ffU(>#0Z*tQ*8Vz=Eo%PKFSaEkJxg+$qmJSJgkyT|?c{#~X^zuQeyD^qg<Vps%Ca4LP_v|R+XFG`!~w`12;%ND2f{WjmNn0$%qfP;(OUU)xvK*`2}zz`0c<{=x6?5PfxlAqw93e?QS?pn&BDzT_mZ;|R=8WH#4fjGexB%kx>oF4v-e0E^u>9I5w83Rs$V@9yu#&vg^=7}#SBd(+ySz4Sp(A=e)%oW?k#6h7srdWZDW_B#*0!hYgG!v+j+@M3OK}(Y(CZL9!+tdfGc&GfvW)uzZ^6?Hn)8+3hLCiea$QTe<>HDcS1MVlXj1u(f9U>jw<5$!TnK=vDJ$nW(eK4)M5e)T*EB6R#GQ)(m^YJK^>=a39*@<`n8H?3zI1j%BKr>WJq5;0?;DZlpV)uUgVK&KI#R;_#4*^G$R6VMenKNeXe0=uT#X$rxAM*r?%7aN=WlO6CD*M8Vpp4^Sm2gU|%!Jvsg78WZhYb(k^fHDLEcoQ<WI>%5%l7wyX2@LY2DKy2M<aw8K1L%KSkU=e8!6TAdP8<$>!>BtpA1lG9K6qnQuwmFIIzfiJ4u2u6eD-1*@fK?dX(ta+jHjnTJLgBEHiU(QMqYnE#yXsN&=Mj3F&oZ^(}o3iSiSqfkcRQpPGb=`Hxpm5;0$g<e^e>(id$H42R8I02m9yl~^UhDoVUUj)1TNAsEwAJxa!Yu9qKK>&3g!9)3qUxV0e>YcHxsD>c*w77ZR2=+S+b49LtrhA8tvK2yPT3EFZf-C_>1rCef9<BhI<m1{!TO_si1nxbu!~`r%CXOd9l_2{$?&|5s}>+-jPpQo4tMlz9H?k4bMhReJG_Z5+5&NXZw#eOd+tfkW{%7LP3SqUh^%vDJAA2c^jrb?-BJ-Tupb%0@1uFq`$Ssk+IlGfp@i*R7pWE`78w?f_k7dJiVWf3f}IXf*Zp$%-pWuEHKimnvXsdO-aH?8s3Dr)KD{@qmuDbc>4Z6%f33Cf=yRvR043h7s|m63$#$Ois0<%oq}eWMd+R1iBruZ31ql{{L;ScXnP~ysEu(>~Jlp)B^6)z~93^)R+ED@gB*F-LM7CSK8200^7xBwpJcbdXvEFPF>~z4wsU5K*)u0cVy02Kgnn-Ql`cd+kUL+kms{%3W{NmCLtU5)Fm)DdqU08YBP#lh+?an$Otg8A>^Ktl}^itJkk6=}A+Eo%9BIhxi#>s8}0yUpWTI$Zn$(}KCDA8!$>MdEmuu7SJu85j!fr>O`4r4W;k-;u_$AaZ|g&8xUz&x>w%3LH}((i`c47kUSoc=hD>hG_Vd_rncuh@#DhJfi%Kv}|P#wJ%3?ME-H&P(F0Ow21dp5}diN&OE)RdXzhS)vK0@<a^9&ByZ$e$OYcLCQ2P78oEV&f74V0!)-EKL}N@nL?3ByvcWV?b8NIK6xF38e|Qc*{B}i2!bhiPcX9-yH_?Tr?AI2QQ}bB)`!_N)6d-uFvI@2Ir<9sw!F-L3fM_`USTMCeL+BRW+pk?<PtCy-5ZZ%2-U;gW`7}>yAs8Jepz>{niUvOMEpYbDjP!%zJV@Bi9*TdKT;#CLHdWTBd?t|=gkJ{Uh>HAob;WW`itWIHV?<vXxXlxoX08x3&&Y^NKvZH)$KJ<VHgNsj|_uD@w|(n^mgL>ml6PuC;W9Q7>o@w*n)SK<bZqTUavA~_?8#?A3S^Q>_HGwZ*qyOchacqzA;EFcNYjd{%30kTc!E(ukv_ZYD;}`qmhpwN~yVENorS|=TFV)EDK?w)B*`O@WP01oQu9nVr5!m=sHH)*II^|Mx2?>5i}N#7J_$j0l_CkOf{{lv8G?hoe!<RjHTDN7vVEHsW(s!t!YUMi{Wm<_}3&|2wI{c1nRa+#C3zZ;tF8KO)kAPi?fw%l-$m(zGka5Y=R0=?>&mHir&jENBG+Bw_|Pv1D6lS7KBJCl_jNf6${Qmg8sU)@8?~{R{mVI!ttHI;8ahx>FktpU{GSJLBYkwF+E#z!){GdL9mEul#>if{6t@o^yZ~=OjZ~y<vbM1XROT|#7<<2_Z2WV@c_I+Sn?cwn)983Pyyg)WhDQqLr|g2C)9~l+mA;91cE=SK6^hf8nIW6E%qhY)fNTvu)hKryu%n(w6V%;VQsR5hWlRAfAw_R@pqW7QvCmb(tnTu)fA#R(>kZam^jmj61TGNO0F=)e==C)L0q-7Lfg%m#kSNRsQQaxuElW)lwv%gcCG+LYrD2lv@2yXS|Q|DIS31Tn6@yjVixM%7dw}-8{d5~`(m~n!f|FLST`s@ieK$qKPv4c$ZOOZDjT0ES=-^30P?HEY?g1xSA3cGz~ENP)E10%$%||{&ZL+2=gcioQ0?{;6>s3FPj%mM?{Fm~bp?Q02TwFFDEUavV$HIRqYg6%nc<t(gSRFnqPwyCPg9*#*JIG6sn>}1;vP&JuS%8h<uJ{4wlaAZKM&{kr&8=hcl}g~dJ-$QomC}xl%Jz~20-TzAV47MuR04U9(z{|<S3{zh?+IdHnom&qaI+(!s#K~Y?gxu#OOhBnp%5#qjtVzy3`|&LBO(%dxg>8zxJw}BY%aPatneF9O}|7#8TG}<iz|OR;OlzlG3#9SDv>li$)Am4C_@$-gwMjfuzq{m1k!nl?BaaSY->Yx)=#?GjQFkwc2kU)J#>gR~G6j+;Lg#)VuXPInEo09mlAx<$?crwJmy$oi^UE6FFkvPDH?d)ZE-S2bAo_fx$<wJRMP%gaTWJ#UM2)>mj(P0kB?<Z^EJn@q24+O&g|o+`Hd29N5eF$mzRuR(iO96<dQ;{)ADr>w}g|S@#x|SEqF~t?8(o+}Zu9K}9lt=5ww1DVm4!iER|CU_8_s_W}zoDHnRs2&z$xH`4-|NL-^iCc~$8IR-)$Io};wwosyi6cLj6fgK+v>=7`abBa2i=`;n_-C4g8!R*;D*uc6766g&H<GsUV)z$glDzoG}x-m}U75yy1>1HC%3I{>rrhlv^^OoC6s1fwar1J(w;L|66ZN=AMxy!*J>5|mnJ!sfQk1znwGU6M#_;^ve;eDI^@j9P0QG?x~oA9oLtuDkEH{sl81zHjYF$PReh;Dk;0gDw=QP=u$YuDsznJP4n-?BcaphZu^3w_;7<R9^wz8dnyc8D{2egCNEzMkq-VoFm3C;YBisDhEJ0^XJ1gH2Wa!2#`M^voLMUH(J*G!nS^#I&=F1Hva`hORcBq?)AU7Cw`Z^>BgV?m+;hWx-Ua$GUuXPQ$<uTOGnOEnxzO_4}WSTynws-Dj$d;T(7Z^`Ma0@2Nq~XgXsrZcWLDl0pCFSGAXpyeaZbKZe=$aUcss@@}0Xhyhh%z<&WBlE-atUR0tsSjlY0Ms3ajJE>(Y&%-M_-U3xk37$8?a*xKe1-VBwVM-0)oHt(E7XDgWRqek|V7;Y`3*|;X`@{|7K?k@L`5+(?00000HWk>hdd|(700GH6@1y|$rH3_YvBYQl0ssI200dcD')).decode()
def _choices(name):
	b=GEN_C.split(name+"[",1)[1].split("=",1)[1].split(";",1)[0]
	return bytes(ord(c)-65 for c in b if "A"<=c<="Z")
_ADD_HINTS,_COL_HINTS=_choices("AH"),_choices("CH")
assert len(_ADD_HINTS)==131 and len(_COL_HINTS)==3930
if __name__=="__main__":
	arg=sys.argv[1] if len(sys.argv)>1 else ""
	if arg=="--selftest":
		sys.exit(0 if selftest() else 1)
	elif arg=="--ledger":
		lg=ledger()
		print_ledger(lg)
		pr=prog()
		ph,filt,body,code,tmax=machine_constants(pr)
		print("PH",ph,"filter",filt,"body",body,"code bytes",code,"tmax",tmax,"audit replay calls",pr.calls,"records",pr.instr,"moves",pr.moves,"slp sha256",slp_sha256(pr.recs))
		s1,s2=phase_bytes(code,tmax)
		offset_raw,selector_raw=search_envelopes()
		assert OFFSET_SEARCH_PEAK<=s1 and SELECTOR_SEARCH_PEAK<=s1
		print("memory bytes",s2,"limit",MEM_LIMIT,"setup phase bytes",s1,"peak",max(s1,s2),"fits",max(s1,s2)<=MEM_LIMIT)
		print("normative C sha256",STATIC_C_SHA256,"stripped wasm sha256",STATIC_WASM_SHA256,"wasm instructions",WASM_EMITTER_INSTR,"run operators",WASM_RUN_OPERATORS)
		print("search raw bounds",offset_raw,selector_raw,"charged per envelope",SEARCH_EVAL_OPS,"offset evaluations",OFFSET_SEARCH_EVALS)
		print("search peak bytes",OFFSET_SEARCH_PEAK,SELECTOR_SEARCH_PEAK)
		print("other code instructions",other_code(pr),"recovery program records executed per call",packed_ops(),"records",rec().instr,"init records",len(rec().init),"registers",pr.nregs)
	elif arg=="--text":
		sys.stdout.write(text())
	elif arg=="--gen-c":
		sys.stdout.write(GEN_C)
	elif arg=="--loss":
		for k,v in loss(plan(256)).items():
			print(k,v)
	else:
		json.dump(serve(json.load(sys.stdin)),sys.stdout)
