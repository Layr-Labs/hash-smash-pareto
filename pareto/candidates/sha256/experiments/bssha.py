import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt,log,log2,log1p,exp,comb
M32=0xFFFFFFFF
ROUNDS=48
UNIT=3568
LANES,ALL=256,(1<<256)-1
IV=(0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19)
K=(0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,
     0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
     0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,
     0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
     0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,
     0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2)
PAD2=bytes([128])+bytes(55)+(512).to_bytes(8,"big")
STATIC_SLP_SHA256="5e7eea11ee1c28af5ea4310ef7a594db15f99cc5c902780177e12c23497d6070"
STATIC_C_SHA256="f15f4db83048620ea5ba2f1f275545af6ba63172050564746b3b33564bda038c"
STATIC_WASM_SHA256="0e4515291410d87746f82b92445cfb1f38c989dac998ce8ce1f257f2d52c2b83"
POLARITY_Q=int("76b5e9e44b62b302c8d9beea0c8abe43ab19e0d1d68685edaf14e9c82d847324",16)
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
OFF=(0,0,0xdbce7a42,0xaaf3823d,0x8d41a28c,0x7f214e02,0x6423f959,0x3e640e8c)
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
		if k>=58337:
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
	"""Byte-exact Python mirror executed before every declared experiment."""
	def __init__(self):
		self.uses,self.err,self.records=[0]*58337,0,[]
	def emit(self,op,d,a,b):
		if len(self.records)>=58080 or max(d,a,b)>1023:
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
		info=(len(self.records),top,nodes,self.calls,moves,self.err,*counts,290400,16384,58337,GEN_STATE_BYTES,3131,GEN_CONSTANT_BYTES)
		return info,q,self.records
def bounded_check(pr):
	info,q,records=BoundedEmitter().run()
	expect=(58080,1021,58337,244952,0,0,45648,7557,4875,290400,16384,58337,GEN_STATE_BYTES,3131,GEN_CONSTANT_BYTES)
	py=[({"^": 1,"&": 2,"|": 3,"M": 4,"S": 5}[o],d,a,b) for o,d,a,b in pr.recs]
	def enc(rs):
		return b"".join(bytes((o,(w:=d|a<<10|b<<20)&255,w>>8&255,w>>16&255,w>>24)) for o,d,a,b in rs)
	a,b=enc(records),enc(py)
	assert info==expect and q==pr.qint==POLARITY_Q and not any(pr.pin[:122])
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
def slp_sha256(recs):
	h=hashlib.sha256()
	for op,d,a,b in recs:
		fields=d|(a<<10)|(b<<20)
		h.update(bytes(({"^": 1,"&": 2,"|": 3,"M": 4,"S": 5}[op],fields&255,(fields>>8)&255,(fields>>16)&255,fields>>24)))
	return h.hexdigest()
class Prog:
	def __init__(self):
		self.recs,self.moves,self.calls=assemble()
		self.q=[0]*256
		self.qint=_QM[0]
		self.qwords=[(self.qint>>(32*i))&M32 for i in range(8)]
		self.pin=[0]*256
		self.instr=self.kernel=len(self.recs)
		self.nregs=max(max(r[1:3]) if r[0] in "NM" else max(r[1:4]) if r[0] in "^&|" else r[1] for r in self.recs)+1
		assert self.instr==58080 and self.moves==0 and self.nregs==1021
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
BODY_BYTES=5
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
WASM_RUN_OPERATORS=121326634
WASM_OPERATOR_FACTOR=2
WASM_EMITTER_INSTR=5142
GEN_STATE_ARRAYS=dict(recent=8*24,cse_k=1024*4,cse_v=1024*4,free=32*4,pending=32*4,W=16*32*4,V=10*32*4,Y=8*32*4,word_scratch=15*32*4,TB=11*32*4,tail_scratch=4*32*4,AW=8*4,output_arrays=6*256*4,output_polarities=256,info=15*4+32,alignment=128,scalars=12*4)
GEN_CONSTANT_ARRAYS=dict(IV=8*4,K=64*4,PW=8*4,OFF=6*4,PM=6*3,PERM=8,SYN=8*36)
GEN_STATE_BYTES=sum(GEN_STATE_ARRAYS.values())
GEN_CONSTANT_BYTES=sum(GEN_CONSTANT_ARRAYS.values())
assert GEN_STATE_BYTES==23532 and GEN_CONSTANT_BYTES==658
GEN_SCRATCH=58337+GEN_STATE_BYTES+3131+GEN_CONSTANT_BYTES+4096
SETUP_FIXED=256*3100+20000
OFFSET_SEARCH_EVALS=64+1+3*192+1000
SEARCH_EVAL_OPS=1<<48
OFFSET_EVAL_OPS=SEARCH_EVAL_OPS
OFFSET_SEARCH_OPS=OFFSET_SEARCH_EVALS*OFFSET_EVAL_OPS
SELECTOR_ADD_CHOICES=101
SELECTOR_COLUMN_CHOICES=3030
SELECTOR_SEARCH_OPS=SEARCH_EVAL_OPS
SEARCH_IMAGE_INSTR=10_000
SEARCH_LOCAL_BYTES=65_536
OFFSET_SEARCH_PEAK=SEARCH_IMAGE_INSTR*INSTR_BYTES+GEN_SCRATCH+SEARCH_LOCAL_BYTES+48
SELECTOR_SEARCH_PEAK=SEARCH_IMAGE_INSTR*INSTR_BYTES+GEN_SCRATCH+SEARCH_LOCAL_BYTES+3131
TMAX_256=109082
OTHER_CODE=1729
CFG={16: dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),20: dict(s1=4,W=0,Tp=1,kappa=12,Sb=4),22: dict(s1=4,W=0,Tp=1,kappa=12,Sb=4),
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
	code=pr.instr*BODY_BYTES+(filt+LOOP_OPS+other_code(pr))*INSTR_BYTES
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
class GEngine:
	def __init__(self,n,salt):
		import random
		self.n,self.pr=n,prog();self.pin=[0]*n;self.mask=(1<<n)-1;r=random.Random(salt);self.ip=r.sample(range(256),n);self.op=r.sample(range(256),n);self.ic=r.getrandbits(256);self.oc=r.getrandbits(n)
		for j in self.ip:self.ic&=~(1<<j)
	def embed(self,x):
		y=self.ic
		for k,j in enumerate(self.ip):y|=((x>>k)&1)<<j
		return y
	def project(self,x):return sum((((x>>j)&1)^((self.oc>>k)&1))<<k for k,j in enumerate(self.op))
	def step(self,*P):
		I=[ALL if self.ic>>j&1 else 0 for j in range(256)]
		for k,j in enumerate(self.ip):I[j]=P[k]
		O=self.pr.step(*[I[j]^(ALL if self.pr.pin[j] else 0) for j in range(256)])
		return [(O[j]^(ALL if self.pr.pin[j] else 0)^(ALL if self.oc>>k&1 else 0)) for k,j in enumerate(self.op)]
	def wstep(self,P):
		n,a,ns=self.n,(1<<256*len(P))-1,self.pr.ns;I=[a if self.ic>>j&1 else 0 for j in range(256)]
		for k,j in enumerate(self.ip):I[j]=sum(q[k]<<256*i for i,q in enumerate(P))
		ns["ALL"]=a;O=self.pr.step(*[I[j]^(a if self.pr.pin[j] else 0) for j in range(256)]);ns["ALL"]=ALL
		return [[(((O[j]>>256*i)&ALL)^(ALL if self.pr.pin[j] else 0)^(ALL if self.oc>>k&1 else 0)) for k,j in enumerate(self.op)] for i in range(len(P))]
	def f2(self,xs):return [self.project(f_scalar(self.embed(x))^self.pr.qint) for x in xs]
	def g_scalar(self,x):return self.project(f_scalar(self.embed(x))^self.pr.qint)
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
def h1_rows(trials,n=20):
	import random
	cap,N,groups,nulls=(1200 if n==20 else 1700),1<<n,64,64;p=plan(n);m=len(trials);theta=1/16
	d=b"h1-shared-v2"+(b"\0" if n==20 else b"/22\0");salt=int.from_bytes(hashlib.sha256(d+b"\0".join(t["seed"].encode() for t in trials)).digest(),"little");eng=GEngine(n,salt)
	tt=trials[:16] if n==20 else [];R=e1_runs(tt,eng,p,"h1-table")[0] if tt else {}
	xs=[derive(t["seed"],"h1-start",n) for t in trials[:groups]];P=pack_lanes(xs,n,[0]*n);assert eng.f2(xs)==lanes_of(list(eng.step(*P)),n,eng.pin)[:groups];seen=[{x} for x in xs];first=[0]*groups;fresh=set();hits=0;active=groups
	for step in range(1,cap+1):
		old=xs;P=list(eng.step(*P));xs=lanes_of(P,n,[0]*n)[:groups]
		for i,v in enumerate(xs):
			if first[i]:continue
			x=old[i]
			if x not in fresh:fresh.add(x);hits+=is_dp(v,p)
			if v in seen[i]:first[i]=step;active-=1
			else:seen[i].add(v)
		if not active:break
	for i in range(groups):
		if not first[i]:first[i]=cap+1
	a,b,c=(400,700,1000) if n==20 else (550,950,1400)
	def hist(F):return [sum(t<=a for t in F),sum(a<t<=b for t in F),sum(b<t<=c for t in F),sum(t>c for t in F)]
	def sim(k):
		r=random.Random(derive(str(salt),"h1-null-%d"%k));mp={};X=[r.randrange(N) for _ in range(groups)];S=[{x} for x in X];F=[0]*groups;fr=dh=0;left=groups
		for step in range(1,cap+1):
			for i in range(groups):
				if F[i]:continue
				x=X[i]
				if x not in mp:mp[x]=r.randrange(N);fr+=1;dh+=is_dp(mp[x],p)
				y=mp[x];X[i]=y
				if y in S[i]:F[i]=step;left-=1
				else:S[i].add(y)
			if not left:break
		for i in range(groups):
			if not F[i]:F[i]=cap+1
		z=(dh-fr*theta)/(fr*theta*(1-theta))**.5
		return hist(F),z
	Q=[sim(k) for k in range(nulls)];cal,val=Q[:32],Q[32:];mu=[sum(q[0][j] for q in cal)/len(cal) for j in range(4)];va=[sum((q[0][j]-mu[j])**2 for q in cal)/(len(cal)-1) for j in range(4)]
	def gof(B):return sum((B[j]-mu[j])**2/max(1,va[j]) for j in range(4))
	bins=hist(first);gs=gof(bins);gl=max(gof(q[0]) for q in val)*1.25+1e-12;dz=(hits-len(fresh)*theta)/(len(fresh)*theta*(1-theta))**.5;dl=max(4,max(abs(q[1]) for q in val)*1.25);ok=gs<=gl and abs(dz)<=dl;succ=sum(i in R for i in range(len(tt)));rows=[]
	for i in range(m):
		obs=dict(width=n,first_step=first[i] if i<groups else -1,bin0=bins[0],bin1=bins[1],bin2=bins[2],bin3=bins[3],gof=gs,gof_limit=gl,dp_z=dz,dp_limit=dl,fresh=len(fresh),dp_hits=hits,groups=groups,nulls=nulls,table_successes=succ,law_pass=int(ok))
		rows.append((None,None,obs))
	return rows
def serve(req):
	eid,out=req["experiment_id"],[]
	bounded_check(prog())
	if eid=="bssha-n16":
		rows=e1_rows(req["trials"])
	elif eid=="proj-k0-w256":
		st=prog()
		rows=[e2_trial(t["seed"],t["trial"],st) for t in req["trials"]]
	elif eid=="h1-law-n20":
		rows=h1_rows(req["trials"])
	elif eid=="h1-law-n22":
		rows=h1_rows(req["trials"],22)
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
	print("bounded setup checks every emitted record; all T2 truth rows:",t2_truth_check())
	reg=max(max(r[1:4]) for r in pr.recs if r[0] in "^&|")+1
	print("records",pr.instr,"moves",pr.moves,"kernel",pr.kernel,"registers used",reg,"text sha256",hashlib.sha256(text().encode()).hexdigest())
	ok=reg<=REGISTERS and pr.nregs<=REGISTERS and all(r[0] in "^&|NM" for r in pr.recs)
	t=True
	for xs in [[rnd.getrandbits(256) for _ in range(LANES)] for _ in range(8)]+[[0]*LANES,[(1<<256)-1]*LANES]:
		out=lanes_of(list(pr.step(*pack_lanes(xs,256,pr.pin))),256,pr.pin)
		t&=all(out[l]==f_scalar(xs[l])^pr.qint for l in range(LANES))
	print("2,560 lanes (10 batches), full 256-bit g = f XOR q, program vs scalar walk-B encoding of state_48:",t)
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
	print("records executed per batch by the interpreter",n,"kernel",pr.kernel,"; the compiled form gives the same 256 output planes:",t)
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
	print("recovery program (%d records executed per call, %d records, interpreter and compiled form) vs scalar (bare f and g = f XOR q):"%(packed_ops(),rec().instr),t)
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
GEN_C=__import__('lzma').decompress(__import__('base64').b85decode(b'{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;7-gOZ(RTvihv|k^V$dz9v%P7dRlup+2P1W3HtFk$fG*;ku`l?ZcVbPceVEw@jG+6?tmN$O&>Qw&3^b0Fl9x~J5-rfnP~dm-yHwFdpKKJz9-8FihWwco%C-x@<HbJ6V^4DKQG9SuA~GorzFhT&{h}Ck8ckjWm+5pM?94`It3zQV(*`^G{29>KL(d!rXehpV|>2=9BIS$+CVVax}_&;SvN9C`Fq#jaif0}dZ!}5P0oofO;)dz+T$qPF*?b51%ayvE#G$n)ihGwwf);ALApG<QOP>MW)h!#&9w^c&c#X>_GrtzfD+zPm;|@;g2?A3j%aRqLJ~F2Jj<o7biC}kbDFoK#`&x3KqW32BT;}<)0a9*8<z!2N9kv+;018SNEXGK-f+171t|a3ei6^uv?&whc{;P(`eiU-@hQ7_Gk+F1+aefe3pBS19yc)FW>H|W>izYMqFN@qa~N@z!Q=!q>oGSE-;r;vl}*=j+-JSz7sIpg`@!{Mp~I%Nio-0L9wEzVEym{c;{g8OXTx7_Xp@!S*x$8p&vIi8GVW4}>*d_*kc#xC7nzl*^5*;%(^xPC<UM0ZV53#RSde>$bo?n|x~d*IvBMLQ;Q(PyX&sd_Ah~+#kA!-y4sHu5Oe)kTl(vX&P$a`J)!+Q#mEA1#+}Oq>@eztdIfiQof0KW}vCs~uap;f0?vuPWB}!bl!ryD~6219Fx{8-=Muw=750zpke(0~>4%YN**f+RzIbF~x1QV<WBz6GM#B{yXs8}I=J8f}4CxnDrC@h>BW7A0%y*&7wAB(?;Kj&(oW=5z!djBB6-8ErLbtexL4YsEJoog!h=^8|`o<=hyQ;l9W8{kSzK%sZo4H+Wc03wUWYKP6bY+3jd@>8C{kA9`5`e;&^a}j)3(x2K!?&RuGN&#@roanM($OhsHV3IB}oZVH$)@ehwhX+bTmb0nhjFH!L5H2Ias!9W)F_ND?6y2Po3&)=M%z?W3{>tJsNaLc%j1G-*n^L``l@!^Kh6}7(r||cu2Ebz~n{CxIF9a7eJn}@XgG4x!l2Huph@~5IJKFKIx#j~$<wxY~XO~W0OPe@(JP<7_X#F&_=6=qeMPKU=77<khM@K-L9?(El1KS2mkXoKaAGXyGSf!?al~700rq@w@H^BAUoEtM|hCt3r1sMq>^Ghf_)P{WwIEsuvsm_%>r*d46V|m^T<--GZW=9+(*+il^&Z?=~xw9wcu)9vq`nP3w0&yF#6#lJc&>hZ7An{1>6j<X;p;sETbEdj=vYW(KUrL1m1M`~*G06h7>vrTG1Fr49_Hvd-Ra{Gg9-=49<U%4im>wus@8h09Rl!uk@=Q3}jI&5Xw#+KBxJwn1Nt`K1N$6Z|+hZJ8Ht%!mmn!FUP(C6NT{uclepd0@Pm~yaXaZh>v?lDoFV3GBuG&#mmKqlqSB;9W503q@dwpJnSYaVJ<#!>LSYdeKRxDSgMn1Ciq2VzOIdt6#HJG?;h2d8sn(2zT()+#EqDN|lb1Dwr9&1e?7g|vzN;gTMl>aB0h5UzzeGuBOXS=ix@c>iYXm_`TyD;GwGSfl|k9wpHFbtJBt-eOXJo$^#wHvM}pOh0rP@`>6OkyQa5d%7ea6<yk(4}(zFW3x<-MqFIOg42jzy)yPeT0J8d1a8iwRjM3(S>54yWJ{c)d+qY7ZFNE*TFY2df|OMX=XK-Vv?O-t08q7L7*xllL*D^)3{;u>NygTGUbQPF?obehBwujKq;Dyz;w|!$h|SCO*`T#)U4dNwIvFR<QUt>Hb1p6O==F;AUj;RLri>}jY@CIb>FQ_H(TNP9$9d7BK$>BfYf?w=3qU$bXg6NOU|SlCh73m2&+$p$ns0@lJhF~Oi&ueV-_2*i89v4>aVe|a{bc(3aDx0N@}z<`LnG8M)&-Y2q+F-YjPFKfj7iT4lXKIVPYk3c_DhCpVDggu6zYki%W_qtczJU9kZ`#-mYR#n|hT6`5%fJdajvk{kJ#R62urTM$!>#M`w+Q^9!m`1BkbQUPMNfSnrDs+ys-7H%eTNlmPkwsSwKsjFA8io4X5Ib>uJr9KMd{QV^4Yii@4sCg2W)1S#o1ls$qA??D`x&RW4G=-VLpU-XM*^bhi}=EDfQB@phk2`YHzE29@BO!hK^OVmnkhkQ|8a|<NYs%sAZG9+SOiVgAP_?@^DE`dhrRW&HR)$VzXuD~00;nlDi^f&r#eRMlSg<NNrA0VnEgyPZ=eS-9sH*_vMsyKCB4@39xwaf2Pp18jN+_i_|#HpjqO+<pjm?iawP$+TQnfR6)=9#I$ldcR#Fm%g-a@(J^a8VXed2v?Rx!;9G-Rid?6}lpgc}d<IC6W;;cqP7(<3M1`?FZuBV610d4YDp)vW>xGCeC0Zggd5SR!gaL{as|{_t-cGBtU#v)d1e<tSo|sNFfgHxm<!+J0Y>`mK=xp@=1>1p*sI?Y=Iy!p7_1fJ-F&%AYB33d`!X0BS;5$%A>VoAaw+`y6Fe=#0>P;8Q}}B|0ZM$AwRx0`CN_6TohR)1^$UwYpz(q0Rt>^4|Y5Doq~j*0`#hNa1inoLs>JgB0L_I;%bSfx#MJPq3#G%e$+;H?D{6|Zm-3*T`qfMWu=$jaq)2oLgk+JlZSzP)ddlVQ%mpvws^&9tsa?e6&QtOJa6ACAFC<s9&j)DSt|H>A_{aqxUMtII~@0zP@kU;`f)OW!tZ%oGD5ble<nx}T~6p%GQ+~7j-un4{yAB_Dg-{|vJ~X!K2@t)GT5gO$TvQ&XBzn4;n?e$VQ?SOGgyoFcHdls{mR|tLxr9B;XVjCa@j7fgwNd-6Z?`^&%;*z1*pX%2zsn^IBA&^U^K+`z+(Y9p}jCtXPQC}AnC%4KxIce^+%g~CdsRrf*p68v=?%w{<?eH%MWVCXX9p_LOs{e{q_%uq|^M6Po#m7Vnx1VOrhzwaisQhPlql70Qt@WvtdPWe`a`4_OR&MYl)QZ12-wGUsgV-7f^1QVp-%VF(9@y6dhgL>$LAOw0Jjx=xM`KCp`In7lV<35n^~o2w-Wd{k~MYc8Q!L1Su}AnX{*3+)0p~F@l5_$ToRHHq3TD>$XRgm4PaH25o4-DXuC_GsoA04e(f-ClbLmH721C{o`9FnDF?yaJ7yUHOA9}N<2i4e$$xwjN<C#Q3>JhPXQFcGFbiogSM)IpbPfg5)5l|QXCf^Dl4rM&fhL$5H4~Ki>+ff3htbv$tYJ)*ow;P)iL7tB?1+PZD<>{i>F^J88%jyM9$)PFa0R-q6&$HGQqI;mwBqbjmj9}HSmLJUfiC!@KEI&VBjt6uTZeGKZNCHGE<jC;s|)1ZNK^>c2qOQ0iN=l1zGf?5iBm2)n3IOe}}_Z|2<dhe|Y?0@SJgwR7N|rKchddYP&2N$$&{J{c}L~ostHG@`l8O%@;pH9o~Tb+0!Q&zruU1j-fw$nb&5!3&#2^araiXoMpaJ>f`hj#vT0X$yY5!!0ct%hyCw@*BN&DT!h`Fi7Kc)GlUbt^ZV|3927Stso*Kn1Na98e?g04dT-#?{zVzrWP-$d;!+<m6wEu8sfNJkjp;7G5&7RV*u@LTzwoir-<%AnDj|8L@Dz`BA#cp0ytXAv@oBPmzug}O(^|UMr1(uvWNoLI64V)Z&d&a+BSg5Zd5ZZSLq*Tx{T@&-!J5bf$tZx=%!#ISAI=UZ^#+FAYfQ1Dl|te(4l&ceciAs(QNhrz6_S_F#52zf8K3P~cEThnASMXp?zY$QaILv>Xeusdd|aD#f9xyHNcDmBTYv*{>T|aIw<kq3vpu~HT0lBulmnSWCWIM3f^-X?!-rk-sE>@vgyKv)IVEY{-ykM^JSDp-^48%3LKz74gPJ7}_s<$J2qmXviUGdD3x+fZQOKaQi+4FvdkWZm(ox<}7@1xpM%EG>gz@hrNvY@`v}b{2qBsl9|GAkx*oMtaU>=2z^X8}&wdlTROL{0p^vs6^mE_8UQqH?wNhGyl=_(?EwCq`n_}DlcEbkiqYX1t)c1|hIzL&tvSMpy5pO<R`&h%F&y`OBAbEa5u^7v;<>Avy{t`;k_bH75;tX@^Sdnp1>osAO4Ax^hSge*zmeFwAou_wrmhhEREF?0^U6@wbgQ%@JYv;g2VnY5#~ndqsI=2rtmmtxbh{OhzNIx9H1X<87_muj}hT=(8zKjCdBB<JpcpExRT%rr&x@h9`yywVt#&0TqPtU2_aHR4%;Lip28_$-Oz#&`VURQyCa-aG09Aq7sp!uY_k`Ys!gKDm-_N+*o7HNcHXC#cKWZGqWz#{C{SS2fz)*-L9ijUA!~qn(uQ@rbd5<fcD^Bl{{rOv}k?mo*8KTwRB^3DXP{kv7EzbC|10ge6`z)?Vzh?R|Y}y$69TKoU=nOjH~~l1v4?0=0U_TCd=B07tab&RGU<ON10nL=H=5Qn}%|i6;(oO=_t}a4jO^y(alX>O1^sQx(-5Y>jj?@Si_5eUv3NJ<j!YVg@}z+OA%(IwlI+DjEI^!GhKL?sM}0LcIaqp8Sr7B~Dy}bpOFx*@DE(miCI8e6F7Z+Dg|vF*|u++10m)tDUYx2~i_@+nJ^mhHX6O1IKpQ%UI|m%nZdw(rna%W6C)i9W;5Q291ndtBr$(Kb{GVJ5$4m6RM_TtV4~8Tq%XBO5~!~s$<+t>ajl9IhbQW7F*ce7CK>x7ceL{Hj3P~j8Gun`maS!R@1HojEuktKn%%cs8XD^88`ks<>Bu}SojLVlqa;AT+qxfIB^_Y3kFvUiU@P-{m3EZ(|{|(mXdT`qBUIDH!_YtgxZ#&amqmJ60PZ|oo5#cVkBToY!Jd}3$kL%;o~N?7ol8~K1j=T7`R>MO*ovFo$ZgzjvMfN+_Z1fuAnIwxT0J;)i#BHq8@BX15N8lgCPE#Px#QXiV8Mfd9`zWKDlFC=Y*nMZB(O}t<Kp<Ak{QR#wuMO;wub?cXd_k91U7OL&z3DzLio;Flw$sFTiQv9yjf#X3dKj)*&6n13=$HdqnwQSIWES<4WeNK#j}8VG)A_Pe9y_;;U-~Xjj`+OuoHQm-p&RwI5dPA&gK-<?d<gtP)q|f#&Rh+G3wj3bubU1C->-RG?+0{g#XDcni~@ZgA>Sspw3nY2$LRGbPNGeXpv1^(hDse-&L7)l5UE$253eEIOaSC62Ll{fvvMh6D-$gDVL5rrR9)R=y>9Wa+5yoz!WHLDu+aUZeQ8f^8H2z%STeoJK_%zuwSWem-yLO~|yuJ35Q%FWB6-^1M@OE+|j#k8d$sE1L|9uZg9m?oL%Ba!h{-&V|(o*}oSkT$BwXp{q0$GqxU|Oqr$&2&Z6j%%y*Hu$$W1LyF}+i+;)zjc%nEBrPdy{e-wUUiWTl>%};MZ3@Y%uzi`_fpNz6&Nzwd)p@^}NReO|Pt~IMUyHR1vO(h62NuG0_+6OiMJSXx5@|a(Q1di3mLuK+B#G#>(MgLLP6eWI#7{63%OYviD!Co4NCDkiclQS}#lcy0tcCzE<!35NE+cvT)wvcZ<}ndOWEdTCydf2z6HDtIo_|2L*)x$KP4A~`5}@ar(FRo|nK{RkC>OtmLEmSruam-8{}C3AUjxyflL;R10@EhM^W~su$PECAM|mzwPpjmr)c?4Zw(Ec-0(gh8p#O7K=HKIN7pmfE^{({Zt~zzPo@O4nbjUp-&kD%)RFOR`W3DEGhLzGbp(#3VZevmwg}cnU;s_)j=hC_kgMAtIwN|~xtcVbF=Hx64?T#bpU&EDgb;EQj>ebr0^Fs8KBzw}WN>blQRyTQNNCrZI<*Gv_6uP2AG$MGg-g!AQQsMOU4jQc$3eT$Is6-2yqFg4ACwc=nJQY;!7JF_#;(Z&}Pm?`b0^b{S<rHpuXhq!={8+0zvi~7c@Znf{ES&zQCmg2zL^39mQ5m3~+lMQz*I|`quLBn~fuiTbyc8{!X@Nt*AXEYIIT4blJONGB5t>MS+rFZkH#?@g6WVu?Y^GLI6{;x@1kc4g>#w-l{#?%I%t=8A_bx_KvvmcG$yPd2oIYs{822)XNa}Q0pi9vqS<vs(w#a|xcaNpi%$el&@6dQ3yrDr^s<4Hh+66BOw2Wi7bw#(xx8b{V8AN`n$f^Q(To%4uF-eJNZOw4P+@FN}S`m9F6|9-<r}gvo@?Ezastp+6)6_q|MP3Rttv|VApCVQ6ME-f;tiYl2HAaP*!eyd2EE%D&7@C5vLtsd_;I6w0NvF7H&#nSaUAVk_%w+My&F<X?oOQOXqU_=rLNU)g06>J9hM(U#^qi~ViNr=KrpCZ!a=j8z7GmASnOO(l;Un{Olz^%H+kfNj{s>J<{bBerX%at_ZK2AmPapHv&z5Dvpc*n*`MQ^t4AY(SGGpz@S(Yo>bNR5Dp1&oiPcO;PwSJ>)N*;ebFge(HZ)V*kVQt-9k{rNSgq1xwN^w}zN+EMG!_9B2(ZsG}lnx(l&|GwtG~7b5x_9`Fmyr4=!aoocg~#z>Mu`1!T{VwgX|MC0n44^zrYmHu)ZDIfW3^H3P>B~wj$bozrAhYA<vo*{;#2QBwzfDaixR50G)d+NfQqQR*h_@f`W_f$D%Dj$@kcGMew1f;A~cFU{>9@facw|FS&qmcTEz{3Fz0(YUZNqWJe>Szo?QuxS;%+<F8%{|gfalxwiTD*>h23GP6!b}9dDU=ztz8aBJGusnrtc^LoImH5_7waanr<P!&fPpmn#)EkS+p-CJ}U=x@7Q0(;4Ncuzl0JOf}QJ_X*Fn&`IiF=POKxFw*XBo@q0_F3FUy!@rYY7Gbx!=Pcx>GaJx?R%xjN{LkA)Mn5YM4P?=WwW%z%>!?h=2U4D0{>a5NN>DB(5QRHaB!Z&K*b)D}U<+;jC${!Dr8d9Zy5;v<k4`q|P5-d*<{e?-xgoU{@1)UiqP;1DOT7o5>If|=&3-Q6R?(tuEo}c(Z8JLL`jOzPCSth`1Nak=EacX3MMj<GTdvHWH+AjzLJVO{Z?XgAclk=C3d~HLE=_3xXj_>6xSO2{mv5|e9(r6aqihCgO71VrNC{`c=lGM+Y@pjm?Eol?I5gQ-A8Ei};X+umNyCsB)%JY_u%?v|)7;&}ImSG9dzV|yrUlmB5d8MDbgs(oArbT-MPXj;&Esnc`wRS44!gAN{V6oFaux)teU@L+1>PogYvpC`V#my&$>3yYk!|=hn{ml|Y^RL@I*Z3m0SWLb?1+n*2wEwKPJRLJ5$AZqNh$sS+urFVVVbrvy>sAQ+%bRg)Pb??dV--M$nLXLbd1CX=&d=HRf{(c)kf8?$ji+%=d6zFCWQ@}kz#O;ZkK$)eL;>OEQopm99mg*jRtd{ROl(8e3%BM=mAgRkcd210Qw%7A`HH#LB_+Z5PTr8l_VMQ1>whTkHIOChTtV8^II54jMhiCr&S*29*?_zc7tlHuJHe;H_9-YlGoX$1`9n=qJYog5z~XA)?IJBQt<fG9sEQaf5GWdHTEPx&9F1Oc1A*{y8Sqwh)j+N_=$!l_>mcEnH)RH8V8{LdCo?(+ft9EAM@195>)es6!IPyxvSXxIDru)C&L;7M%UCL@_Sw+GMk+=x7Yd40};&ff=@j$2nZ5zvh4lJ?;quY9ScK^|F7mccWZgG5arQIR<eyZ1hOX;GjY^og=MRz+nUL>i?=Hg-N1^a6+sah`)z%wm7Fo@$)?5xon(*rWPaEgYdXmz7BsfrNNYLS^wvYF0jK1LAC;K)zu7}5ll5+vy24d3f`!Z54n+Q$9El8y-u=pzfZ;`n!@~HXh}#Occ_g(S>V+E>kfSKp64W3qHfl3gtzaWYUrZRlDazr(H3j2ph{>6=bw(vlh7`Xk9*<bTwIru8QL1P9!{*@M*p%8h?0-v(;3F#s{7CH8gmS}mdB;wtS{UPAq4x49EIS#qj>r%s4f8yl?x)}XaI;@nP^#0A0_p1<YWXYj6Y4MEnP*P)D#b``2<ne7ltPh_7<~(k88R505qd(H_>~r=h!pm4AH&Zrm7RKiukpKcAl$b~U@lAFChM7@9wn@IMz2i)JjSS$R!AxLJ0ia9E!{;)V`9wx(8A9=!nH!i@|D-EeV7L!&L=+gP|phi(t}B7&*{sELOu3oe0<G;xzfMG*ol-?{U1yLR!4sE!f9ax<+BPc!;xe<FII|lg%)jxAK6_;N~KbONwMoY5|8t^e$uzps($3Y7hfrdsG?>j1}|oLEFK@S%mAd}sNRCFZ;8aQ-pHKsrZW>kF8EsCJZR_wAT#vlLxR~yImT^!VR%)hm1-_x&xn*hLOlyFAfQe1<*$z=o5afw!{3H~<{2f#r|o*7NgefT-A$hh6k!yk<p7epgY=?O;k=mkDTHh9tt8(FM(MPO?hd@Nles<JU|e{P)U_GBQqe9i^wAUU7QrCZBKQg{q#g*F&E!8?3z!RXRnuV=SsV}-ZLm6s&fn8TmUMwuujcsFSND`qvseRRU<<kYF@4O9_JI+6UEt2SHhXfdiobQt-~vGzD8lq?W%{S32^WQyd(t(f!;}|)S+bto<$tBwIpcaC`_ybHfvghjvIAMh`?3;y8Z(pxGWGhpaw_Bx`%DX|g74Y>M19j!3h^AF7lh~9%iI89C2tCU%L?s2Mh$BOVW1jdD)yFvy2VV^nk<4auo<j!#g>re6L=Hyj9+!ux@VCA3CT~20=&Z^Ei#O8O`EZ7XP-$ad)pW@2h0JqdBee)ik;UYX(NgbH|}raNbR3yR3w%zJo-@eCva-tMcYH&;LQ#L!NujH8-klROhK(^2hAX3BG9priMZ6;Huyfxa6r@2NI7Z9!S!sOfO?gD2~l&Ujf*%LG`*jH%<S40=^{ImFooY`317I>eX5*$=v_DgJ|H4amAzs(pTXkVm;r(Y1aaOw*sn{D-zhf2!G)og(6saMN=YQ%lCfUe>%VLqG)ahQ`*7&Sixyq`-~y;^2|RD)`Z*>V2~VlS#r|-sjLg?lS(Hf%Mgw;T5|z^($QfqjZiW`8j)A;!%7?!4x*OdDRh*%hR4iqo7_5QMgo^wg(A_DKiQKK@G(@#`<Hy*k-ca0jh`e3kj<Ty5(pSZa2Vy{g{SFaA6JeafZWHTH=<#kbh|9Ya21K}Ud&OG?a;)Fyb6|14E1d6#V>t9x%7n_(1oqTm*#ph9Y4z6-D1mb*@T1KYdHEk&C5YhUDQZ@C<Y%@2$ej3E)XaK!lmB^Mgf^;bLCue`%5jMuIS<E~(8x0cWhl-_RFls6T*V8HYwT;}azl{Gv23NazYmeGPMQtitkaU~fD`UVeE(hKx3dh04EuwtyDMcPIZ<L9y}>ncDUC8vsPS_=<X1TW;{<+YE=;FZ=0@R|40@kXZY>ue3ib@w0_Xq$#tC#Gb*!Y=00E0R&7A=N2*%`dvBYQl0ssI200dcD')).decode()
def _choices(name):
	b=GEN_C.split(name+"[",1)[1].split("=",1)[1].split(";",1)[0]
	return bytes(ord(c)-65 for c in b if "A"<=c<="Z")
_ADD_HINTS,_COL_HINTS=_choices("AH"),_choices("CH")
assert len(_ADD_HINTS)==101 and len(_COL_HINTS)==3030
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
