"""Credits: dariolina, newjordan, sraiw."""
import sys,os,json,random,time,hashlib,math,itertools
M=0xFFFFFFFF
def _kc(p):
 t=p<<96;x=int(p**(1/3)*2**32)
 while x**3>t:x-=1
 while(x+1)**3<=t:x+=1
 return x&M
K=[_kc(p)for p in[q for q in range(2,170)if all(q%d for d in range(2,q))][:39]]
IV=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]
def ror(x,k):return(x>>k|x<<32-k)&M
def S0(x):return ror(x,2)^ror(x,13)^ror(x,22)
def S1(x):return ror(x,6)^ror(x,11)^ror(x,25)
def s0(x):return ror(x,7)^ror(x,18)^x>>3
def s1(x):return ror(x,17)^ror(x,19)^x>>10
def CH(e,f,g):return e&f^~e&g&M
def MAJ(a,b,c):return a&b^a&c^b&c
H=lambda s:[int(x,16)for x in s.split()]
CV_PUB=H("aa79ff87 65c5bb49 d0a84bfd 90ccc398 fac64fb6 4ff7998a b1af5ec5 aa1ed4d5")
M_PUB=H("8334d670 3813877e f19d46d5 77556fc4 902f98c7 0500282c a4235533 9100e365 e76f5fe2 5633326d 9d603088 06a64487 a94ae11e b06304ad 43660038 d80d950f")
MP_PUB=list(M_PUB);MP_PUB[8]=0xa76f5fe2;MP_PUB[9]=0x5eb3226d;MP_PUB[10]=0xdd603088;MP_PUB[11]=0x00a467b3;MP_PUB[12]=0xa95af91e
ADVICE_BYTES=4*(8+16+16)
def expand(w,n=39):
 w=list(w)
 for i in range(16,n):w.append(w[i-16]+s0(w[i-15])+w[i-7]+s1(w[i-2])&M)
 return w
def traj(cv,w16,n=39):
 w=expand(w16,n)
 A=[cv[3],cv[2],cv[1],cv[0]];E=[cv[7],cv[6],cv[5],cv[4]]
 for r in range(n):
  a,b,c,d=A[r+3],A[r+2],A[r+1],A[r]
  e,f,g,h=E[r+3],E[r+2],E[r+1],E[r]
  t1=h+S1(e)+CH(e,f,g)+K[r]+w[r]&M
  t2=S0(a)+MAJ(a,b,c)&M
  A.append(t1+t2&M);E.append(d+t1&M)
 return A,E,w
def compress(cv,w16,n=39):
 A,E,_=traj(cv,w16,n)
 st=[A[n+3],A[n+2],A[n+1],A[n],E[n+3],E[n+2],E[n+1],E[n]]
 return[st[i]+cv[i]&M for i in range(8)]
BA,BE,BW=traj(CV_PUB,MP_PUB)[0],traj(CV_PUB,MP_PUB)[1],MP_PUB
CA,CE,CW_=traj(CV_PUB,M_PUB)[0],traj(CV_PUB,M_PUB)[1],M_PUB
Wp_,Wq_=expand(MP_PUB),expand(M_PUB)
G16=Wp_[16]
W17PUB=Wp_[17]
D8=M_PUB[8]-MP_PUB[8]&M
D9=M_PUB[9]-MP_PUB[9]&M
T8,T9=0x087FF000,0x03010000
def inF(w,D,T):return s0(w+D&M)-s0(w)&M==T
def consts(cv):
 t20=S0(cv[0])+MAJ(cv[0],cv[1],cv[2])&M
 eb=cv[3]-t20&M
 k0=-t20-cv[7]-S1(cv[4])-CH(cv[4],cv[5],cv[6])-K[0]&M
 c9=BW[9]+BA[5]&M
 cw=G16-s1(BW[14])-c9-k0+cv[6]+K[1]&M
 return cw,eb,cv[0],cv[1],cv[4],cv[5]
def fstep(x,c):
 if x&1:return s0(x)-x&M
 cw,eb,cv0,cv1,cv4,cv5=c
 e0=x+eb&M
 return cw+S0(x)+MAJ(x,cv0,cv1)+S1(e0)+CH(e0,cv4,cv5)-x&M
def recover_a1(cv,a0,u):
 t20=S0(cv[0])+MAJ(cv[0],cv[1],cv[2])&M
 e0=cv[3]+a0-t20&M
 return u+S0(a0)+MAJ(a0,cv[0],cv[1])+S1(e0)+CH(e0,cv[4],cv[5])+cv[6]+K[1]&M
def build(cv,a0,a1):
 A=[cv[3],cv[2],cv[1],cv[0],a0,a1,BA[6],BA[7],BA[8],BA[9]]
 E=[cv[7],cv[6],cv[5],cv[4]]+[None]*6
 W=[None]*16
 for r in range(6):
  a,b,c=A[r+3],A[r+2],A[r+1]
  t2=S0(a)+MAJ(a,b,c)&M
  t1=A[r+4]-t2&M
  e,f,g,h=E[r+3],E[r+2],E[r+1],E[r]
  W[r]=t1-h-S1(e)-CH(e,f,g)-K[r]&M
  E[r+4]=A[r]+t1&M
 A+=[BA[10],BA[11],BA[12],BA[13]]
 E+=[None]*4
 for k in range(10,14):E[k]=BE[k]
 for r in range(6,10):
  e,f,g,h=E[r+3],E[r+2],E[r+1],E[r]
  t1=E[r+4]-A[r]&M
  W[r]=t1-h-S1(e)-CH(e,f,g)-K[r]&M
 for r in range(10,16):W[r]=BW[r]
 return W
def second(W):
 V=list(W)
 V[8]=W[8]+D8&M;V[9]=W[9]+D9&M
 for r in range(10,16):V[r]=M_PUB[r]
 return V
def claw_pair(cv,a0,u):
 a1=recover_a1(cv,a0,u)
 W=build(cv,a0,a1)
 return W,second(W)
ROW_MASKS_16_17={16:(0x05010000,0x04010000,0x00000100,0,0x08801000,0x08800000),17:(0,0,0x80829C01,0x00029C00,0x40000000,0x40000000)}
_C1617=14195250,7866380,13109778,8915986,4460562,530956,1580562,2110988,13675058,9183762,6293010,7342604,3684364,14989364,14956556,11568690,15875084,163880,11085388,7416402,8467020,9515602,5411890,10566220,5936680,6461490,80972,8035890,9085490,2163794,12234280,21570,23620,16432690,10028114,5324364,15270476,13143091,13667885,15769645,2755085,9476659,4493365,4329491,1091635,2141229,2663469,8658963,9052691,15249459,9577485,15774259,6861869,7386669,571443,1621043,12857363,9472045,9996851,13906963,14858293,14825491,4753459,12618291,11090003,12124237,3738189,15875091,7939667,13701709,6882381
CONDS_16_17=tuple((16+(v&1),((v>>5&3,16+(v&1)-(v>>7&3),v>>9&31),)+(()if v>>14&1 else((v>>15&3,16+(v&1)-(v>>17&3),v>>19&31),)),v>>1&15)for v in _C1617)
def _build_by_bit():
 ex=list(CONDS_16_17)
 for _ in range(4):
  cs=set(ex)
  for kr1,t1,a1 in list(ex):
   for kr2,t2,a2 in list(ex):
    if kr1!=kr2 or len(t2)!=2 or a2 not in(6,9):continue
    for x,y in(t2[0],t2[1]),(t2[1],t2[0]):
     if len(t1)==2 and a1 in(6,9):
      for u,v in(t1[0],t1[1]),(t1[1],t1[0]):
       if v==x and u!=y and(kr1,(u,y),9 if a1==a2 else 6)not in cs:
        nc=kr1,(u,y),9 if a1==a2 else 6;cs.add(nc);ex.append(nc)
     elif len(t1)==1 and t1[0]==x:
      nc=kr1,(y,),a1 if a2==9 else 3^a1
      if nc not in cs:cs.add(nc);ex.append(nc)
 bb={16:[[]for _ in range(32)],17:[[]for _ in range(32)]}
 for kr,terms,allowed in ex:bb[kr][max(b for _,rw,b in terms if rw==kr)].append((terms,allowed))
 return bb
BY_BIT_16_17=_build_by_bit()
def solve_row_exact(A0,E0,W0,A1,E1,W1,r):
 ma_r,sa_r,me_r,se_r,mw_r,sw_r=ROW_MASKS_16_17[r]
 dsch=s1(W1[r-2])+W1[r-7]+s0(W1[r-15])-(s1(W0[r-2])+W0[r-7]+s0(W0[r-15]))&M
 idx=r+4
 t10=E0[idx-4]+S1(E0[idx-1])+CH(E0[idx-1],E0[idx-2],E0[idx-3])+K[r]&M
 t11=E1[idx-4]+S1(E1[idx-1])+CH(E1[idx-1],E1[idx-2],E1[idx-3])+K[r]&M
 t20=S0(A0[idx-1])+MAJ(A0[idx-1],A0[idx-2],A0[idx-3])&M
 t21=S0(A1[idx-1])+MAJ(A1[idx-1],A1[idx-2],A1[idx-3])&M
 ce0,ce1,ca0,ca1=A0[idx-4]+t10&M,A1[idx-4]+t11+dsch&M,t10+t20&M,t11+t21+dsch&M
 by_bit=BY_BIT_16_17[r];out=[];steps=[0]
 def dfs(b,w_low):
  if b==32:out.append(w_low);return
  steps[0]+=1
  mw,sw,me,se,ma,sa=mw_r>>b&1,sw_r>>b&1,me_r>>b&1,se_r>>b&1,ma_r>>b&1,sa_r>>b&1
  for bit in 0,1:
   w=w_low|bit<<b;wx1=w+dsch>>b&1
   if bit^wx1!=mw or bit&mw!=sw:continue
   ex_f=ce0+w&M;ex0,ex1=ex_f>>b&1,ce1+w>>b&1
   if ex0^ex1!=me or ex0&me!=se:continue
   ax_f=ca0+w&M;ax0,ax1=ax_f>>b&1,ca1+w>>b&1
   if ax0^ax1!=ma or ax0&ma!=sa:continue
   ok=True
   for terms,allowed in by_bit[b]:
    cidx=0
    for q,(kind,rw,cb)in enumerate(terms):
     wd=(w if kind==2 else ex_f if kind==1 else ax_f)if rw==r else W0[rw]if kind==2 else E0[rw+4]if kind==1 else A0[rw+4]
     cidx|=(wd>>cb&1)<<q
    if not allowed>>cidx&1:ok=False;break
   if ok:dfs(b+1,w)
 dfs(0,0)
 return out,steps[0]
def invert_downward(A_top,E_top,W):
 A=[0]*14+list(A_top);E=[0]*14+list(E_top)
 for r in range(13,-1,-1):
  t2=S0(A[r+3])+MAJ(A[r+3],A[r+2],A[r+1])&M;t1=A[r+4]-t2&M
  A[r]=E[r+4]-t1&M;E[r]=t1-S1(E[r+3])-CH(E[r+3],E[r+2],E[r+1])-K[r]-W[r]&M
 return[A[3],A[2],A[1],A[0],E[3],E[2],E[1],E[0]],A,E
def verify_advice_construction():
 cv0,A0_i,E0_i=invert_downward(BA[14:20],BE[14:20],MP_PUB)
 cv1,A1_i,E1_i=invert_downward(CA[14:20],CE[14:20],M_PUB)
 inv_ok=int(cv0==CV_PUB and cv1==CV_PUB and A0_i==BA[:20]and E0_i==BE[:20]and A1_i==CA[:20]and E1_i==CE[:20])
 sbits=1,2,3,9,12,13,14,19;e0_15,e1_15,a0_15,a1_15=BE[19],CE[19],BA[19],CA[19]
 me_15,se_15,ma_15,sa_15=e0_15^e1_15,e0_15&(e0_15^e1_15),a0_15^a1_15,a0_15&(a0_15^a1_15)
 dsch16=s1(M_PUB[14])+M_PUB[9]+s0(M_PUB[1])-(s1(MP_PUB[14])+MP_PUB[9]+s0(MP_PUB[1]))&M
 hits=tot_steps=g16_sz=g17_sz=base_ops=0
 for idx in range(256):
  w15=MP_PUB[15]^sum((idx>>k&1)<<sbits[k]for k in range(8));dw=w15-MP_PUB[15]&M
  ne0,ne1,na0,na1=e0_15+dw&M,e1_15+dw&M,a0_15+dw&M,a1_15+dw&M
  if ne0^ne1!=me_15 or ne0&me_15!=se_15 or na0^na1!=ma_15 or na0&ma_15!=sa_15:continue
  A0,E0,W0=BA[:19]+[na0],BE[:19]+[ne0],MP_PUB[:15]+[w15]
  A1,E1,W1=CA[:19]+[na1],CE[:19]+[ne1],M_PUB[:15]+[w15]
  g16,s16=solve_row_exact(A0,E0,W0,A1,E1,W1,16);tot_steps+=s16
  if idx==0:g16_sz=len(g16);assert G16 in g16
  for g in g16:
   w16_0,w16_1=g,g+dsch16&M
   t10=E0[16]+S1(E0[19])+CH(E0[19],E0[18],E0[17])+K[16]+w16_0&M;t20=S0(A0[19])+MAJ(A0[19],A0[18],A0[17])&M
   t11=E1[16]+S1(E1[19])+CH(E1[19],E1[18],E1[17])+K[16]+w16_1&M;t21=S0(A1[19])+MAJ(A1[19],A1[18],A1[17])&M
   g17,s17=solve_row_exact(A0+[t10+t20&M],E0+[A0[16]+t10&M],W0+[w16_0],
      A1+[t11+t21&M],E1+[A1[16]+t11&M],W1+[w16_1],17)
   tot_steps+=s17
   if idx==0 and g==G16:g17_sz=len(g17);base_ops=(s16+s17)*6;assert g17==[W17PUB]
   if g17:hits+=1
 return{"g16_fibre_size":g16_sz,"g17_fibre_size":g17_sz,"fibre_dfs_ops":base_ops,"downward_inv_ok":inv_ok,
  "advice_slice_cands":256,"advice_slice_hits":hits,"ops_per_cand":(288*256+16*tot_steps)//256}
XOR,AND,OR,NOT=0,1,2,3
ONES=(1<<256)-1
class Gen:
 def __init__(s,nin):
  s.nin=nin;s.recs=[]
 def g(s,op,a,b=None):
  s.recs.append((op,a,b));return s.nin+len(s.recs)-1
 def X(s,a,b):
  if a[0]<0 and b[0]<0:return-1,a[1]^b[1]
  if a[0]<0:return b[0],b[1]^a[1]
  if b[0]<0:return a[0],a[1]^b[1]
  if a[0]==b[0]:return-1,a[1]^b[1]
  return s.g(XOR,a[0],b[0]),a[1]^b[1]
 def NOTm(s,a):
  return s.g(NOT,a[0]),0
 def A(s,a,b,orr=False):
  if a[0]<0 or b[0]<0:
   if a[0]<0:a,b=b,a
   if(b[1]==0)!=orr:return-1,0 if not orr else 1
   return a
  if a[0]==b[0]:
   return a if a[1]==b[1]else(-1,1 if orr else 0)
  if a[1]==b[1]:
   if a[1]==0:return s.g(OR if orr else AND,a[0],b[0]),0
   return s.g(AND if orr else OR,a[0],b[0]),1
  if a[1]==1:a,b=b,a
  return s.g(OR if orr else AND,a[0],s.g(NOT,b[0])),0
 def O(s,a,b):return s.A(a,b,True)
 def full(s,a,b,c,ncy=True):
  cs=[t for t in(a,b,c)if t[0]<0];vs=[t for t in(a,b,c)if t[0]>=0]
  if len(cs)==0:
   pol=[a[1],b[1],c[1]]
   if pol[0]==pol[1]==pol[2]:p,x,y=c,a,b
   else:
    i=[k for k in range(3)if pol.count(pol[k])==1][0]
    p=(a,b,c)[i];x,y=[t for k,t in enumerate((a,b,c))if k!=i]
   u=s.X(x,p);sm=s.X(u,y)
   if not ncy:return sm,Z0
   return sm,s.X(s.A(u,s.X(y,p)),p)
  if len(cs)==1:
   x,y=vs;k=cs[0];t=s.X(x,y);p=x if x[1]==k[1]else y;sm=s.X(t,k)
   if not ncy:return sm,Z0
   if x[1]!=y[1]:return sm,s.O(p,t)if k[1]else s.A(p,(t[0],0))
   return sm,s.O(x,y)if k[1]else s.A(x,y)
  if len(cs)==2:
   k=cs[0][1]^cs[1][1];x=vs[0]
   return s.X(x,(-1,k)),x if cs[0][1]!=cs[1][1]else(-1,cs[0][1])
  return(-1,sum(t[1]for t in cs)&1),(-1,1 if sum(t[1]for t in cs)>=2 else 0)
Z0=-1,0;O1=-1,1
NREG_FIXED=224
DPREG=224
def allocate(g,out,acc,dst_bank,dpreg=None,nfixed=None):
 nin=g.nin;dpreg=DPREG if dpreg is None else dpreg;nfixed=NREG_FIXED if nfixed is None else nfixed
 outs=[]
 for j in range(32):
  node,pol=out[j];assert node>=0
  if pol:node=g.g(NOT,node)
  outs.append(node)
 accn=acc[0];assert accn>=0
 recs=g.recs;last={}
 for i,(op,a,b)in enumerate(recs):
  for t in a,b:
   if t is not None:last[t]=nin+i
 forced={outs[j]:dst_bank*32+j for j in range(32)};forced[accn]=dpreg
 for t in list(forced):last[t]=1<<60
 reg={i:i for i in range(nin)};free=[];nxt=nfixed+1;res=[]
 for i,(op,a,b)in enumerate(recs):
  nid=nin+i;dying=[]
  for t in a,b:
   if t is not None and t>=nin and last.get(t)==nid and t not in dying:dying.append(t)
  if nid in forced:d=forced[nid]
  elif dying:d=reg[dying[0]];dying=dying[1:]
  elif free:free.sort();d=free.pop(0)
  else:d=nxt;nxt+=1
  for t in dying:free.append(reg[t])
  reg[nid]=d
  res.append((op,d,reg[a],reg[b]if b is not None else 0))
 return res,acc[1],nxt
def to_source(recs,name,dpreg=None):
 dpreg=DPREG if dpreg is None else dpreg
 L=["def %s(R):"%name];ins=set();defined=set()
 for op,d,a,b in recs:
  for t in a,b:
   if t not in defined:ins.add(t)
  defined.add(d)
 for t in sorted(ins):L.append(" r%d=R[%d]"%(t,t))
 sym={XOR:"^",AND:"&",OR:"|"}
 for op,d,a,b in recs:
  if op==NOT:L.append(" r%d=r%d^M"%(d,a))
  else:L.append(" r%d=r%d%sr%d"%(d,a,sym[op],b))
 for d in sorted({d for _,d,_,_ in recs if d<64 or d==dpreg}):L.append(" R[%d]=r%d"%(d,d))
 return "\n".join(L)
def build_folded(consts5,src_bank,dst_bank,dpb):
 cw,eb,P,R,G=consts5;g=Gen(65)
 x=[(src_bank*32+j,0)for j in range(32)];nx0=g.NOTm(x[0])
 def x0p(p):return(nx0[0],1)if p else x[0]
 def mux0(od,ev,wp=-1):
  if od==ev:return od
  if ev[0]<0:return g.A(od,(x0p(od[1]^ev[1])[0],x0p(od[1]^ev[1])[1]^ev[1]),bool(ev[1]))
  if od[0]<0:
   no=1-od[1]
   return g.A(ev,(x0p(ev[1]^no)[0],x0p(ev[1]^no)[1]^no),bool(od[1]))
  y=g.X(od,ev);uo=wp!=od[1]if wp>=0 and od[1]!=ev[1]else y[1]==1
  return g.X(od if uo else ev,g.A((x0p(y[1]^int(uo))[0],x0p(y[1]^int(uo))[1]^int(uo)),y))
 xe=[Z0]+x[1:];u=[None]*32;e0=[None]*32;cy=Z0
 for j in range(32):
  u[j]=g.X(xe[j],xe[j+11&31])
  e0[j],cy=g.full(xe[j],(-1,eb>>j&1),cy,j<31)
 cwe=cw+P+1+(G&~R&~1)+((eb^G)&1 if R&1 else G&1)+(~P&1)&0xFFFFFFFF
 nxtb=[];res=[None]*32;cy=Z0
 for j in range(32):
  k7=j+7&31
  uoj=g.X(u[k7],O1)if k7 in(0,21)else u[k7]
  od=g.X(uoj,x[j+3]if j+3<32 else Z0);b=[]
  if cwe>>j&1:b.append(O1)
  b.extend(nxtb)
  if j>0 and R>>j&1:b.append(g.X(e0[j],(-1,G>>j&1)))
  b.append(g.X(u[j+2&31],xe[j+22&31]))
  b.append(g.X(g.X(e0[j+6&31],e0[j+11&31]),e0[j+25&31]))
  nxtb=[];hnx=j>0 and not P>>j&1;tgt=1 if j==0 or hnx else 2
  while len(b)>tgt:
   take=2 if len(b)==tgt+1 else 3
   sm,c2=g.full(b[0],b[1],b[2]if take==3 else Z0,j<31);b=b[take:]
   if sm!=Z0:b.append(sm)
   if j<31 and c2!=Z0:nxtb.append(c2)
  if not hnx and len(b)==2 and od[1]==0 and b[0][1]==0 and b[1][1]==1:b[0],b[1]=b[1],b[0]
  sev=b[0]if len(b)>=1 else Z0
  cev=Z0 if j==0 else(x[j][0],1)if hnx else b[1]if len(b)>=2 else Z0
  if j==0:
   res[0]=mux0((od[0],od[1]^1),sev,0);cy=g.A(od,x0p(od[1]))
  else:
   nxj=x[j][0],1
   if cev[0]>=0 and cev[1]==0:
    aj=mux0(od,sev,cy[1]);bj=mux0(nxj,cev,aj[1]^cy[1])
   else:
    bj=mux0(nxj,cev,-1);aj=mux0(od,sev,bj[1]^cy[1])
   res[j],cy=g.full(aj,bj,cy,j<31)
  if res[j][1]:res[j]=g.NOTm(res[j])
 acc=res[0]
 for j in range(1,dpb):acc=g.O(acc,res[j])
 return g,res,acc
def consts5(c):
 cw,eb,cv0,cv1,cv4,cv5=c
 return cw+(cv0&cv1)&0xFFFFFFFF,eb,cv0^cv1,cv4^cv5,cv5
def make_kernels_folded(c,dpb):
 ks=[]
 for src,dst in(0,1),(1,0):
  g,out,acc=build_folded(consts5(c),src,dst,dpb)
  recs,dppol,nreg=allocate(g,out,acc,dst,dpreg=64,nfixed=64)
  ns={"M":ONES};exec(to_source(recs,"k",dpreg=64),ns)
  ks.append(dict(recs=recs,dppol=dppol,nreg=nreg,fn=ns["k"],
    counts={o:sum(1 for r in recs if r[0]==o)for o in range(4)}))
 return ks
class GW:
 FALLBACK=575000
 AVAILABLE=False
 try:
  import wasmtime as _wt
  if os.environ.get("R39_WASM"):
   _cfg=_wt.Config();_cfg.consume_fuel=True;_eng=_wt.Engine(_cfg);_mod=_wt.Module.from_file(_eng,os.environ["R39_WASM"]);AVAILABLE=True
 except Exception:
  AVAILABLE=False
 @staticmethod
 def run(c5,src=0,dst=1,dpb=7):
  st=GW._wt.Store(GW._eng);inst=GW._wt.Instance(st,GW._mod,[]);ex=inst.exports(st);st.set_fuel(10**12)
  n=ex["gen"](st,*c5,src,dst,dpb,32768);used=10**12-st.get_fuel();raw=ex["memory"].read(st,32768,32768+5*n);recs=[]
  for i in range(n):
   w=raw[5*i+1]|raw[5*i+2]<<8|raw[5*i+3]<<16|raw[5*i+4]<<24
   recs.append((raw[5*i],w&1023,w>>10&1023,w>>20&1023))
  return used,recs
 @staticmethod
 def ops(c5):return GW.run(c5)[0]if GW.AVAILABLE else GW.FALLBACK
ONES=(1<<256)-1
M32=M;M32_2=M|M<<128
M20,M31,M39=(1<<20)-1,(1<<31)-1,(1<<39)-1
NM20=ONES^M20
M64=(1<<64)-1
M25=(1<<25)-1
DBG=False
HIGHMASK=[sum(1<<p for p in range(256)if p>>k&1)for k in range(8)]
C_LOG16=sum(r<<(5*((1<<r)-(1<<r>>7))&255)for r in range(16))
LOW128=(1<<128)-1
class Mach:
 def __init__(s):s.o=0;s.cat={};s.blk={};s.nest=0
 def bs(s):return s.o,s.nest
 def be(s,name,b,sub=False):
  d=s.o-b[0]-(s.nest-b[1])
  if sub:s.nest+=d-1;d-=1
  if d>s.blk.get(name,0):s.blk[name]=d
 def x(s,a,b):s.o+=1;return a^b
 def a(s,a,b):s.o+=1;return a&b
 def r(s,a,b):s.o+=1;return a|b
 def n(s,a):s.o+=1;return a^ONES
 def ad(s,a,b):s.o+=1;return a+b&ONES
 def sb(s,a,b):s.o+=1;return a-b&ONES
 def sl(s,a,k):s.o+=1;return a<<k&ONES
 def sr(s,a,k):s.o+=1;return a>>k
 def rl(s,a,k):s.o+=1;k%=256;return a if k==0 else(a<<k|a>>256-k)&ONES
 def rr(s,a,k):return s.rl(a,256-k%256)
 def ne(s,a,b):s.o+=1;return 1 if a!=b else 0
 def jz(s,a):s.o+=2;return a==0
 def jnz(s,a):s.o+=2;return a!=0
 def jeq(s,a,b):s.o+=2;return a==b
 def jne(s,a,b):s.o+=2;return a!=b
 def jge(s,a,b):s.o+=2;return a>=b
 def ld(s,arr,i):s.o+=3;return arr[i]
 def st(s,arr,i,v):s.o+=3;arr[i]=v
 def mv(s):s.o+=1
 def tick(s,name,t0):
  d=s.o-t0
  s.cat[name]=s.cat.get(name,0)+d
 def blkmax(s,name,d):
  if d>s.blk.get(name,0):s.blk[name]=d
def mS0(m,v):
 d=m.r(v,m.sl(v,32));return m.x(m.x(m.sr(d,2),m.sr(d,13)),m.sr(d,22))
def mS1(m,v):
 d=m.r(v,m.sl(v,32));return m.x(m.x(m.sr(d,6),m.sr(d,11)),m.sr(d,25))
def ms0(m,v):
 d=m.r(v,m.sl(v,32));return m.x(m.x(m.sr(d,7),m.sr(d,18)),m.sr(v,3))
def mMAJ(m,a,b,c):return m.r(m.a(a,b),m.a(c,m.r(a,b)))
def mCH(m,e,f,g):return m.x(m.a(e,f),m.a(m.x(e,M32),g))
def a32(m,a,b):return m.a(m.ad(a,b),M32)
def s32(m,a,b):return m.a(m.sb(a,b),M32)
class P:
 DPB=7
 MAXS=1536
 CUTP=512
 LMIN=32
 WIN=1<<26
 KTRY=32
 QCAP,QFULL=3584,3328
 WHEEL=2048
 WDIG=(14,1),(13,1),(10,1),(8,1),(7,1),(6,1),(2,1)
 GCAP=575000
 RCAP=206
 KCAP=710
 CMP1=10
 D0,KRES=82,6
def table_words(wdig=P.WDIG):return sum(sg*(1<<k)for k,sg in wdig)
class Attack:
 def __init__(s,win=P.WIN,seed=1,check=False,k4=False):
  s.k4=k4;s.k4_max=None;s.m=Mach();s.win=win;s.check=check;s.dpreg=DPREG;s.W=table_words()
  s.ks=None;s.R=[0]*512
  s.rnd=random.SystemRandom()if seed is None else random.Random(seed)
  s.st=dict(windows=0,iters=0,hits=0,matches=0,raw=0,trails=0,cuts=0,s2phases=0,s2iters=0,pairs=0,f9=0,f8=0,w17=0,parks=0,resumes=0,
    verify=0,qmax=0,opp=0,same=0,claws_distinct=0,moves=0,drops=0,waits=0)
  s.idc0=256;s.distinct=set();s.cv_id=0;s.cv_try=False;s.measure=True
  s.LA=[0]*256;s.sav=[0]*32
  s.base_setup()
 def base_setup(s):
  m=s.m;t0=m.o
  m.o+=2*2812+120
  s.K24=S0(BA[7])
  s.A7,s.A6=BA[7],BA[6]
  t25=S0(BA[8])+MAJ(BA[8],BA[7],BA[6])&M32
  s.CE5=BA[9]-t25&M32
  s.NE11=~BE[11]&M32;s.CH0=BE[11]&BE[10]
  s.CW8=BE[12]-BA[8]-S1(BE[11])-K[8]&M32;s.CW8P=s.CW8|1<<64;s.BA8P=BA[8]|1<<63
  s.C17=s1(BW[15])+BW[10]&M32
  s.C9=BW[9]+BA[5]&M32;s.C9P=s.C9|1<<64
  m.tick('run_setup',t0)
 def window_setup(s,cv=None):
  m=s.m;t0=m.o;s.m0=None;s.skip=False;tries=0
  while True:
   if cv is None or s.cv_try:
    blk=[s.rnd.getrandbits(32)for _ in range(16)];m.o+=2
    s.m0=blk;m.o+=16
    cv=compress(IV,blk);m.o+=2812
   s.cv_try=True
   ks_try=make_kernels_folded(consts(cv),P.DPB)
   gops=GW.ops(consts5(consts(cv)))
   if len(ks_try[0]['recs'])<=P.KCAP and gops<=P.GCAP and max(ks_try[0]['nreg'],ks_try[1]['nreg'])<=P.RCAP:break
   m.o+=min(gops,P.GCAP);s.st['kskip']=s.st.get('kskip',0)+1
   tries+=1;m.o+=142
   if tries>=P.KTRY:s.skip=True;return
  s.cv=cv;s.cv_id+=1
  s.c=consts(cv);m.o+=140
  cw=s.c[0]
  s.CA1=cv[6]+K[1]-cw&M32
  tg=m.o;c5=consts5(s.c);s.ks=ks_try
  m.o+=gops+8*len(s.ks[0]['recs'])
  if s.check and GW.AVAILABLE:
   assert GW.run(c5,0,1,P.DPB)[1]==[tuple(r)for r in s.ks[0]['recs']]
   assert GW.run(c5,1,0,P.DPB)[1]==[tuple(r)for r in s.ks[1]['recs']]
  s.dpreg=64;m.tick('generator',tg)
  s.tab=[0]*s.W;m.o+=4*s.W
  s.qn=0;s.qw=[0]*(P.QCAP//4+1)
  s.cur=0;s.it=0;tb=m.bs();s.s2=None;s.cut0=s.cut1=s.cut2=0;s.cut_at=P.CUTP;m.o+=5;m.be('w_s2',tb)
  for j in range(32):s.R[j]=sum(1<<l for l in range(256)if l>>j&1)if j<8 else 0
  m.o+=32
  for l in range(256):s.LA[l]=NM20|l;m.o+=3
  s.idc=s.idc0
  s.st['windows']+=1
  m.tick('window_setup',t0)
 def insert_lane(s,base,low,l,val,nbits=20):
  m=s.m;R=s.R;b=m.bs();m.o+=2
  Z=m.rl(val,l)if l is not None else val;nl=m.n(low)
  for j in range(nbits):
   t=Z if j==0 else m.rr(Z,j);p=R[base+j]
   R[base+j]=m.x(p,m.a(m.x(p,t),low))
  for j in range(nbits,32):R[base+j]=m.a(R[base+j],nl)
  m.be('insert_lane',b,True)
 def delta_lanes(s,base,G,ZI,Z):
  m=s.m;R=s.R;b=m.bs();m.o+=2
  for j in range(7):
   t=ZI if j==0 else m.rr(ZI,j);R[base+j]=m.r(R[base+j],m.a(t,G))
  Z=m.x(Z,m.rr(ZI,7))
  for j in range(7,20):
   t=Z if j==7 else m.rr(Z,j-7);R[base+j]=m.x(R[base+j],m.a(t,G))
  m.be('delta_lanes',b,True)
 def find_lane(s,mask,hi=7):
  m=s.m;bb=m.bs();m.o+=2
  low=m.a(mask,m.sb(0,mask));l=0
  for k in range(hi,3,-1):
   b=m.ne(m.a(low,HIGHMASK[k]),0)
   l=m.sl(b,k)if k==hi else m.r(l,m.sl(b,k))
  x=m.sr(low,l);y=m.sb(x,m.sr(x,7))
  l=m.r(l,m.a(m.rr(C_LOG16,m.ad(y,m.sl(y,2))),15))
  m.be('find_lane'if hi==7 else'find_lane128',bb,True)
  return low,l
 def extract(s,base,jlo,jhi,low,l,name):
  m=s.m;R=s.R;b=m.bs();m.o+=2
  Z=m.a(R[base+jhi],low)
  for j in range(jhi-1,jlo-1,-1):Z=m.r(m.rl(Z,1),m.a(R[base+j],low))
  v=m.rr(Z,l)if l is not None else Z
  m.be(name,b,True)
  return v
 def claw(s,a,b):
  m=s.m;t0=m.o;tb0=m.bs();s.st['raw']+=1
  if m.jnz(m.a(a,1)):a0,u=b,a
  else:a0,u=a,b
  m.mv()
  if s.measure and(s.cv_id,a0,u)not in s.distinct:
   s.distinct.add((s.cv_id,a0,u));s.st['claws_distinct']+=1
  if s.check:assert fstep(a0,s.c)==fstep(u,s.c)and a0%2==0 and u%2==1
  a1u=m.ad(m.ad(ms0(m,u),a0),s.CA1)
  W9=m.sb(s.C9P,a1u);z9=ms0(m,m.a(m.r(W9,m.sl(m.ad(W9,D9),128)),M32_2))
  ok=m.jeq(s32(m,m.sr(z9,128),z9),T9)
  if s.check:
   Wc=build(s.cv,a0,recover_a1(s.cv,a0,u));Wx=expand(Wc)
   assert Wc[9]==W9&M32 and Wx[16]==G16 and Wc[1]==u and ok==inF(Wc[9],D9,T9)
  m.be('claw_filter',tb0);m.tick('claw_filter',t0)
  if not ok:return 0
  s.st['f9']+=1;t1=m.o;tb1=m.bs();a1=m.a(a1u,M32)
  if s.k4 and(s.k4_max is None or s.st['f9']<=s.k4_max)and s.k4d(a0,u):s.k4_eval(a0,a1,u)
  e4=m.sb(m.ad(a0,s.BA8P),m.ad(s.K24,mMAJ(m,s.A7,s.A6,a1)))
  e5=m.ad(a1,s.CE5)
  W8=m.sb(m.sb(s.CW8P,e4),m.x(s.CH0,m.a(e5,s.NE11)));z8=ms0(m,m.a(m.r(W8,m.sl(m.ad(W8,D8),128)),M32_2))
  ok8=m.jeq(s32(m,m.sr(z8,128),z8),T8)
  if s.check:assert W8&M32==Wc[8]and ok8==inF(Wc[8],D8,T8)
  m.be('claw_f8',tb1);m.tick('claw_f8',t1)
  if not ok8:return 0
  s.st['f8']+=1;t2=m.o;tb2=m.bs();cv=s.cv
  e1=s32(m,m.sb(m.ad(cv[2],a1),mS0(m,a0)),mMAJ(m,a0,cv[0],cv[1]))
  e0=m.ad(a0,s.c[1])
  w2=s32(m,m.sb(m.sb(m.sb(m.sb(m.sb(BA[6],mS0(m,a1)),mMAJ(m,a1,a0,cv[0])),cv[5]),mS1(m,e1)),mCH(m,e1,e0,cv[4])),K[2])
  w17=a32(m,m.ad(s.C17,ms0(m,w2)),u)
  okw=m.jeq(w17,W17PUB)
  if s.check:assert w17==Wx[17]
  m.be('claw_w17',tb2);m.tick('claw_w17',t2)
  if not okw:return 0
  s.st['w17']+=1;s.st['verify']+=1
  m.o+=2*2812+400
  W1m,W2m=claw_pair(s.cv,a0,u)
  if W1m!=W2m and compress(s.cv,W1m)==compress(s.cv,W2m):
   s.st['collisions']=s.st.get('collisions',0)+1;s.pairs_found=getattr(s,'pairs_found',[])+[(list(s.cv),W1m,W2m,getattr(s,'m0',None))]
   if getattr(s,'m0',None)is not None:s.messages=getattr(s,'messages',[])+[(list(s.m0)+list(W1m),list(s.m0)+list(W2m))]
   s.success=True
   return 1
  return 0
 def qpush(s,pk):
  m=s.m;b=m.bs();m.o+=2
  wi=m.sr(s.qn,2);sh=m.a(s.qn,3)
  w=pk if m.jz(sh)else m.r(m.ld(s.qw,wi),m.sl(pk,m.sl(sh,6)))
  m.st(s.qw,wi,w);s.qn=m.ad(s.qn,1)
  m.be('qpush',b,True)
 def qpop(s,qi):
  m=s.m;b=m.bs();m.o+=2
  w=m.ld(s.qw,m.sr(qi,2));v=m.a(m.rr(w,m.sl(qi,6)),M64)
  m.be('qpop',b,True)
  return v
 def iter1(s):
  m=s.m;R=s.R;ks=s.ks;k=ks[s.cur]
  k['fn'](R);m.o+=len(k['recs']);tb=m.bs();s.cur^=1;s.it+=1;s.st['iters']+=1
  n0=R[s.dpreg];m.o+=5;dp=m.jne(n0,ONES);m.be('iter1',tb)
  if dp:
   t0=m.o
   tb=m.bs();hit=m.n(n0);s.cut0=m.r(s.cut0,hit);s.it20=m.sl(s.it,20);s.it20p=m.ad(s.it20,1<<20);G=0;m.be('hb_init',tb)
   while True:
    tb=m.bs();low,l=s.find_lane(hit);hit=m.x(hit,low);wl=m.rl(M25,l);cf=m.jnz(m.a(wl,W))if G else False;m.be('hb_sel',tb)
    if cf:
     tb=m.bs();tc=m.o;tn=m.nest;s.hit_group(G,HL);m.nest=tn+(m.o-tc-2);G=0;m.be('hb_close',tb)
    tb=m.bs()
    if G:W=m.r(W,wl);G=m.r(G,low);HL=m.r(HL,m.sl(l,nl));nl=m.ad(nl,8)
    else:W=wl;G=low;HL=l;nl=8
    assert not s.check or nl<=80;s.st['hlanes']=s.st.get('hlanes',0)+1;more=m.jnz(hit);m.be('hb_add',tb)
    if not more:break
   tb=m.bs();tc=m.o;tn=m.nest;s.hit_group(G,HL);m.nest=tn+(m.o-tc-2);m.be('hb_last',tb)
   tb=m.bs();base=s.cur*32;nd=R[s.dpreg]
   if s.check:assert nd==n0
   for j in range(20,32):R[base+j]=m.a(R[base+j],nd)
   m.be('hb_clr',tb)
   full=m.jge(s.qn,P.QFULL);m.blkmax('iter1h',8)
   m.tick('hits',t0)
   if full:s.stage2()
  tb=m.bs();cs=m.jz(m.a(s.it,P.CUTP-1));m.be('iter1c',tb)
  if cs:s.cutscan()
 def wr(s,word,w,w1,word1,rsh,st2,sh,d):
  m=s.m;m.st(s.tab,word,m.x(w,m.sl(d,sh)))
  if m.jnz(st2):m.st(s.tab,word1,m.x(w1,m.sr(d,rsh)))
 def hit_group(s,G,HL):
  m=s.m;base=s.cur*32;m.o+=2;tg=m.bs();s.st['hgroups']=s.st.get('hgroups',0)+1
  s.ZI=0
  Z=s.extract(base,P.DPB,31,G,None,'extract25')
  m.be('hb_ext',tg)
  while True:
   tv=m.bs();more=m.jge(HL,256);m.be('hb_lp',tv)
   tv=m.bs()
   if more:l=m.a(HL,255);HL=m.sr(HL,8)
   else:l=HL
   r=m.a(m.rr(Z,l),M25);m.be('hb_v',tv)
   if s.check:assert sum((s.R[base+j]>>l&1)<<j for j in range(32))==r<<P.DPB
   s.hit(l,r)
   if not more:break
  tv=m.bs();s.delta_lanes(base,G,s.ZI,Z);m.be('hb_ins',tv)
 def hit(s,l,r):
  m=s.m;s.st['hits']+=1;ta=m.bs()
  t=m.sb(m.ad(m.sl(r,3),m.ad(m.sl(r,5),m.sl(r,7))),r)
  bk=m.sr(t,15);pos=m.sb(m.ad(m.sl(bk,5),m.sl(bk,3)),bk)
  word=m.sr(pos,8);sh=m.a(pos,255);chk=m.a(r,255)
  w=m.ld(s.tab,word);v=m.sr(w,sh);w1=0;word1=0;rsh=0;st2=m.jge(sh,218)
  if st2:word1=m.ad(word,1);rsh=m.sb(256,sh);w1=m.ld(s.tab,word1);v=m.r(v,m.sl(w1,rsh))
  e=m.a(v,M39)
  lw=m.ld(s.LA,l);en0=m.ad(lw,s.it20p)
  if s.check:
   ln=s.it-((lw^NM20)>>20)
   assert 0<=ln<2048 and pos==39*(r*171008>>25)and en0==lw&M20|ln<<20
  if m.jeq(m.sr(e,31),chk)and m.jnz(e0:=m.a(e,M31)):
   m.be('hit_a',ta);tb=m.bs();s.st['matches']+=1
   ln20=m.a(en0,NM20)
   if m.jge(e0,ln20):
    pk=m.r(m.sl(m.sb(e0,ln20),20),m.a(lw,M20))
   else:
    s.wr(word,w,w1,word1,rsh,st2,sh,m.x(e0,en0))
    pk=m.r(m.sl(m.sb(en0,m.a(e0,NM20)),20),m.a(e0,M20))
   s.qpush(pk);s.st['qmax']=max(s.st['qmax'],s.qn)
   m.be('hit_m',tb)
  else:
   m.be('hit_a',ta);tb=m.bs()
   if m.jge(en0,P.LMIN<<20):
    s.wr(word,w,w1,word1,rsh,st2,sh,m.x(e,m.r(en0,m.sl(chk,31))))
   m.be('hit_n',tb)
  td=m.bs()
  nid=s.idc
  if m.jge(nid,1<<20):s.lim=0;m.o+=1;m.be('hit_c',td);s.st['stop_grp']=s.st.get('stop_grp',0)+int(s.ZI!=0);return
  s.idc=m.ad(nid,1)
  m.st(s.LA,l,m.sb(nid,s.it20p));s.st['trails']+=1
  zi=m.rl(nid,l);s.ZI=m.r(s.ZI,zi)if s.ZI else zi
  m.be('hit_c',td)
 def cut_lane(s,base,l,it20,cthr):
  m=s.m;tl=m.bs();m.o+=2
  lw=m.ld(s.LA,l)
  if m.jge(lw,cthr):
   if not m.jge(s.idc,1<<20):
    low=m.sl(1,l);nid=s.idc;s.idc=m.ad(nid,1);s.st['cuts']+=1
    m.st(s.LA,l,m.r(nid,it20));s.insert_lane(base,low,l,nid)
   else:s.lim=0;m.o+=1
  m.be('cut_lane',tl,True)
 def cutscan(s):
  m=s.m;t0=m.o;base=s.cur*32;tq=m.bs()
  regular=m.jeq(s.it,s.cut_at)and m.jne(s.idc,1<<20);G=ONES;m.mv();m.be('cut_gate',tq)
  tq=m.bs()
  if regular:
   G=m.n(m.r(s.cut0,m.r(s.cut1,s.cut2)));m.be('cut_mask',tq)
  else:
   s.cut0=s.cut1=s.cut2=0;m.o+=3;m.be('cut_reset',tq)
  tq=m.bs();s.cut2,s.cut1,s.cut0=s.cut1,s.cut0,0;m.o+=3;s.cut_at=m.ad(s.it,P.CUTP)
  scan=m.jge(s.it,P.MAXS);m.be('cut_roll',tq)
  if not scan:m.tick('cutscan',t0);return
  tq=m.bs();it20=m.x(NM20,m.sl(s.it,20));cthr=m.ad(it20,P.MAXS<<20);m.be('cut_threshold',tq)
  tq=m.bs();fast=m.jnz(regular);m.be('cut_kind',tq)
  if fast:
   while True:
    tq=m.bs();more=m.jnz(G);m.be('cut_test',tq)
    if not more:break
    tq=m.bs();low,l=s.find_lane(G);G=m.x(G,low);s.cut_lane(base,l,it20,cthr);m.be('cut_pending',tq)
  else:
   for l in range(256):
    tq=m.bs();m.o+=3;s.cut_lane(base,l,it20,cthr);m.be('cut_linear',tq)
  m.tick('cutscan',t0)
 def bank(s,src,dst):
  m=s.m;R=s.R;m.o+=3
  for j in range(32):
   if src is None:m.st(R,dst+j,m.ld(s.sav,j))
   elif dst is None:m.st(s.sav,j,m.ld(R,src+j))
   else:x=m.ld(R,src+j);m.st(R,dst+j,m.ld(s.sav,j));m.st(s.sav,j,x)
   m.o+=3
  m.blkmax('bank_sw' if src is not None and dst is not None else'bank_in' if src is None else 'bank_out',18 if src is not None and dst is not None else 12)
 def qins(s,base,low,l,val):
  m=s.m;bb=m.bs();m.o+=2
  wl=m.rl(M20,l);z=m.rl(val,l)
  if m.jz(s.QG):
   s.QW=wl;s.QZ=z;s.QG=low
  elif m.jnz(m.a(wl,s.QW)):
   s.insert_lane(base,s.QG,None,s.QZ);s.QW=wl;s.QZ=z;s.QG=low;s.st['qfl']=s.st.get('qfl',0)+1;s.st['qconf']=s.st.get('qconf',0)+1
  else:
   s.QW=m.r(s.QW,wl);s.QZ=m.r(s.QZ,z);s.QG=m.r(s.QG,low)
  s.st['qins']=s.st.get('qins',0)+1
  m.be('qins',bb,True)
 def qflush(s,base):
  m=s.m;bb=m.bs();m.o+=2
  if m.jnz(s.QG):
   s.insert_lane(base,s.QG,None,s.QZ);s.QG=0;m.o+=1;s.st['qfl']=s.st.get('qfl',0)+1
  m.be('qflush',bb,True)
 def move_lane(s,base,q,r,lowr):
  m=s.m;R=s.R;bb=m.bs();m.o+=2
  k=m.sb(r,q)
  for j in range(32):
   p=R[base+j];R[base+j]=m.x(p,m.a(m.x(p,m.rl(p,k)),lowr))
  m.be('move_lane',bb,True)
 def link(s,rec,wh,it2,d,q,v):
  m=s.m;tb=m.bs();m.o+=2
  idx=m.ad(it2,d);wi=m.sr(m.a(idx,P.WHEEL-1),4);sh=m.sl(idx,4)
  w=m.ld(wh,wi);head=m.a(m.rr(w,sh),0xFFFF)
  v=m.r(v,m.sl(head,21));ri=m.sr(q,3);rs=m.sl(q,5);rw=m.ld(rec,ri)
  m.st(rec,ri,m.x(rw,m.rl(m.x(m.a(m.rr(rw,rs),M32),v),rs)))
  m.st(wh,wi,m.x(w,m.rl(m.x(head,m.ad(q,1)),sh)))
  m.be('link',tb,True)
 def fpop(s,fs,nf):
  m=s.m;tb=m.bs();m.o+=2
  nf=m.sb(nf,1);w=m.ld(fs,m.sr(nf,5));q=m.a(m.rr(w,m.sl(nf,3)),255)
  m.be('fpop',tb,True)
  return nf,m.sl(1,q),q
 def stage2(s,final=0):
  m=s.m;R=s.R;t0=m.o;s.st['s2phases']+=1
  sv=s.cur
  tb=m.bs()
  if m.jz(s.s2 is not None):
   m.be('s2_in',tb);s.bank(sv*32,None)
   ti=m.bs();cur=0;it2=0;bact=0;live=0;occ=0;nf=128
   rec=[0]*32;wh=[0]*(P.WHEEL//16);fs=[sum(32*i+j<<8*j for j in range(32))for i in range(4)];m.o+=22;m.be('s2_init',ti)
  else:
   cur,it2,bact,live,occ,nf,rec,wh,fs=s.s2;m.o+=18;m.be('s2_in',tb);s.bank(sv*32,cur*32);s.st['resumes']+=1
  tq=m.bs();qi=0;qn=s.qn;pw=0;s.QW=0;s.QZ=0;s.QG=0;m.o+=4;m.be('s2_q',tq)
  while True:
   tw=m.bs();wi=m.sr(m.a(it2,P.WHEEL-1),4);sh=m.sl(it2,4)
   w=m.ld(wh,wi);head=m.a(m.rr(w,sh),0xFFFF)
   has_cb=m.jnz(head)
   if has_cb:m.st(wh,wi,m.x(w,m.rl(head,sh)))
   m.be('wheel_check',tw)
   if has_cb:
    while True:
     tl=m.bs()
     q=m.sb(head,1);v=m.a(m.rr(m.ld(rec,m.sr(q,3)),m.sl(q,5)),M32);head=m.sr(v,21);cB=m.a(v,M20)
     qp=m.x(q,128);lowq=m.sl(1,q);lowp=m.rl(lowq,128)
     if m.jnz(m.a(v,1<<20)):
      m.be('cb_a',tl);tl=m.bs()
      s.qins(cur*32,lowp,qp,cB);bact=m.r(bact,lowq)
      m.be('cb_in',tl)
     elif m.jz(m.a(occ,lowp)):
      m.be('cb_a',tl);tl=m.bs()
      s.qins(cur*32,lowp,qp,cB)
      occ=m.r(occ,lowp);bact=m.r(bact,m.sl(1,m.a(q,127)))
      m.be('cb_free',tl)
     elif m.jnz(nf):
      m.be('cb_a',tl);tl=m.bs()
      nf,lowr,r=s.fpop(fs,nf)
      if s.check:assert not occ>>r&1 and not occ>>r+128&1
      s.qflush(cur*32);s.move_lane(cur*32,q,r,lowr)
      lowrp=m.sl(lowr,128);s.qins(cur*32,lowrp,m.ad(r,128),cB)
      occ=m.r(m.x(occ,lowq),m.r(lowr,lowrp));bact=m.r(bact,lowr);s.st['moves']+=1
      m.be('cb_move',tl)
     else:
      m.be('cb_a',tl);tl=m.bs()
      occ=m.x(occ,lowq);live=m.sb(live,1);s.st['drops']+=1
      m.be('cb_drop',tl)
     if not m.jnz(head):break
   while True:
    tl=m.bs()
    if m.jz(pw):
     if m.jge(qi,qn):m.be('launch_t',tl);break
     pw=s.qpop(qi);qi=m.ad(qi,1)
     m.be('launch',tl);tl=m.bs()
    if m.jge(pw,P.D0<<40):
     hm=m.a(m.n(occ),m.rl(occ,128))
     if m.jnz(hm):
      m.be('l_try',tl);tl=m.bs()
      lowq,q=s.find_lane(hm)
      m.be('l_half',tl)
     elif m.jge(nf,P.KRES):
      m.be('l_try',tl);tl=m.bs()
      nf,lowq,q=s.fpop(fs,nf)
      m.be('l_f2s',tl)
     else:
      m.be('l_try',tl);s.st['waits']+=1;break
     tl=m.bs();iB=m.a(pw,M20);iA=m.a(m.sr(pw,20),M20);d=m.sr(pw,40)
     s.qins(cur*32,lowq,q,iA);occ=m.r(occ,lowq)
     s.link(rec,wh,it2,d,q,iB)
     m.be('l_single',tl)
    else:
     if not m.jge(nf,P.KRES):
      m.be('l_try',tl);s.st['waits']+=1;break
     m.be('l_try',tl);tl=m.bs();iB=m.a(pw,M20);iA=m.a(m.sr(pw,20),M20);d=m.sr(pw,40)
     nf,lowq,q=s.fpop(fs,nf)
     lowqh=m.sl(lowq,128)
     s.qins(cur*32,lowq,q,iA);occ=m.r(occ,m.r(lowq,lowqh))
     if m.jz(d):
      s.qins(cur*32,lowqh,m.ad(q,128),iB);bact=m.r(bact,lowq)
     else:
      s.link(rec,wh,it2,d,q,m.r(iB,1<<20))
     m.be('l_pair',tl)
    tl=m.bs();live=m.ad(live,1);pw=0;m.o+=1;s.st['pairs']+=1;m.be('l_end',tl)
   tb=m.bs();s.qflush(cur*32);m.be('s2_fl',tb)
   if m.jz(live):break
   tb=m.bs();sp=m.jz(pw)and m.jz(final);m.be('s2_susp',tb)
   if sp:break
   assert not s.check or s.QG==0
   k=s.ks[cur];k['fn'](R);m.o+=len(k['recs']);ts=m.bs();cur^=1;it2+=1;m.o+=2;m.be('s2_step',ts);s.st['s2iters']+=1
   tc=m.bs();base=cur*32;acc=0
   for j in range(P.CMP1):
    pl=R[base+j];dj=m.x(pl,m.rl(pl,128));acc=dj if j==0 else m.r(acc,dj)
   cand=m.a(m.n(acc),bact)
   m.be('cmp1',tc)
   if m.jnz(cand):
    tc=m.bs();acc2=0
    for j in range(P.CMP1,32):
     pl=R[base+j];dj=m.x(pl,m.rl(pl,128));acc2=dj if j==P.CMP1 else m.r(acc2,dj)
    full=m.a(cand,m.n(acc2))
    m.be('cmp2',tc)
    pp=R[(cur^1)*32];ppd=None
    while m.jnz(full):
     tm=m.bs()
     low,l=s.find_lane(full,6);full=m.x(full,low)
     low2=m.r(low,m.sl(low,128))
     if ppd is None:ppd=m.x(pp,m.rl(pp,128))
     if s.check:assert pp==R[(cur^1)*32]
     if m.jnz(m.a(ppd,low)):
      s.st['opp']+=1
      Z=s.extract((cur^1)*32,0,31,low2,l,'extract32x2')
      a=m.a(Z,M32);b=m.sr(Z,128)
      tcl=m.o;r_cl=s.claw(a,b);m.nest+=m.o-tcl
      if r_cl:s.success=True
     else:s.st['same']+=1
     bact=m.x(bact,low);occ=m.x(occ,low2);live=m.sb(live,1)
     fi=m.sr(nf,5);fsh=m.sl(nf,3);fw=m.ld(fs,fi);m.st(fs,fi,m.r(m.a(fw,m.rl(ONES^255,fsh)),m.rl(l,fsh)));nf=m.ad(nf,1)
     m.be('merge',tm)
  if s.check:assert pw==0
  tb=m.bs()
  if m.jnz(live):
   s.s2=cur,it2,bact,live,occ,nf,rec,wh,fs;m.o+=18;m.be('s2_out',tb);s.bank(cur*32,sv*32);s.st['parks']+=1
  else:
   m.be('s2_out',tb);s.s2=None;s.bank(None,sv*32)
   if s.check:assert not any(wh)
  s.qn=0;m.tick('stage2',t0)
 def run_window(s,cv=None,iters=None):
  s.success=False;s.window_setup(cv)
  if s.skip:return s.st
  s.lim=iters if iters else s.win//256
  while s.it<s.lim:
   s.iter1()
   if s.success:break
  m=s.m;tb=m.bs();go=(m.jnz(s.qn)or m.jnz(s.s2 is not None))and m.jz(s.success);m.be('w_end',tb);m.blkmax('w_end',6)
  if go:s.stage2(final=1)
  if s.k4:s.k4f()
  return s.st
GEN_EXPERIMENTS="r39-transplant-claw","r39k4-window-small"
WIN_EXP={
7365741297968335814:(834,834,32470,1724,2458,853,16,0,49,4,0,709,22176977,580672,1109),
14152957579836449138:(821,821,32624,1706,2356,843,9,0,53,8,0,688,21148082,580504,1109),
17548137956998735317:(859,859,32731,1788,2867,881,16,1,64,4,0,708,21976810,580664,1185),
11186828115432487819:(806,806,32819,1698,2867,830,10,0,60,4,1,700,21212217,580600,1109),
}
def _e1(i,sd):
 if i==0:
  A=Attack(win=1<<20,check=True);o=P.KCAP;P.KCAP=1024
  try:A.window_setup(cv=CV_PUB)
  finally:P.KCAP=o
  a0,u=BA[4],MP_PUB[1]
  assert a0%2==0 and fstep(a0,A.c)==s0(u)-u&M
  A.check=False;o0=A.m.o
  r=A.claw(a0,u);A.check=True
  W1m,W2m=A.pairs_found[0][1:3]if r==1 else(None,None)
  adv=verify_advice_construction()
  assert adv=={"g16_fibre_size":2,"g17_fibre_size":1,"fibre_dfs_ops":1944,"downward_inv_ok":1,
    "advice_slice_cands":256,"advice_slice_hits":1,"ops_per_cand":411}
  out={"claw_returned_pair":r,"passed_f9":A.st["f9"],"passed_f8":A.st["f8"],"passed_w17":A.st["w17"],
    "pair_is_advice":int(W1m==MP_PUB and W2m==M_PUB),
    "sfs_collision":int(compress(CV_PUB,MP_PUB)==compress(CV_PUB,M_PUB)and MP_PUB!=M_PUB),
    "advice_w16_is_g":int(expand(MP_PUB)[16]==G16),"advice_w17":int(expand(MP_PUB)[17]==W17PUB),
    "kernel_records":len(A.ks[0]["recs"]),"claw_ops":A.m.o-o0,"blk_census":sum(A.m.blk.values()),
    "g16_fibre_size":adv["g16_fibre_size"],"g17_fibre_size":adv["g17_fibre_size"],
    "fibre_dfs_ops":adv["fibre_dfs_ops"],"advice_slice_hits":adv["advice_slice_hits"],"ops_per_cand":adv["ops_per_cand"]}
  assert out=={"claw_returned_pair":1,"passed_f9":1,"passed_f8":1,"passed_w17":1,"pair_is_advice":1,
    "sfs_collision":1,"advice_w16_is_g":1,"advice_w17":1,"kernel_records":730,"claw_ops":6140,
    "blk_census":121,"g16_fibre_size":2,"g17_fibre_size":1,"fibre_dfs_ops":1944,
    "advice_slice_hits":1,"ops_per_cand":411}
  return out
 rnd=random.Random(sd)
 cv=[rnd.getrandbits(32)for _ in range(8)]
 a0=rnd.getrandbits(32)&~1;u=rnd.getrandbits(32)|1
 c=consts(cv)
 a1=recover_a1(cv,a0,u);W=build(cv,a0,a1);V=second(W)
 A1,E1,_=traj(cv,W);A2,E2,_=traj(cv,V)
 out={"transplant_ok":int(A1[6:20]==BA[6:20]and E1[10:20]==BE[10:20]and A2[6:20]==CA[6:20]and E2[10:20]==CE[10:20]),
  "w1_is_u":int(W[1]==u),"w16_identity":int(expand(W)[16]-G16&M==fstep(u,c)-fstep(a0,c)&M)}
 assert out=={"transplant_ok":1,"w1_is_u":1,"w16_identity":1}
 if i==1:out.update(verify_advice_construction())
 return out
_W17_HIST=[0]*256;_W18_HIST=[0]*256;_G_SEQ=[]

def k4_words(cv,a0,a1,a2,a3):
 A=[cv[3],cv[2],cv[1],cv[0],a0,a1,a2,a3,BA[8],BA[9],BA[10],BA[11]]
 E=[cv[7],cv[6],cv[5],cv[4]]+[None]*8+[BE[12],BE[13],BE[14],BE[15]];W=[None]*16
 for r in range(8):
  a,b,c=A[r+3],A[r+2],A[r+1];t1=A[r+4]-(S0(a)+MAJ(a,b,c)&M)&M
  e,f,g,h=E[r+3],E[r+2],E[r+1],E[r];W[r]=t1-h-S1(e)-CH(e,f,g)-K[r]&M;E[r+4]=A[r]+t1&M
 for r in range(8,12):
  e,f,g,h=E[r+3],E[r+2],E[r+1],E[r];t1=E[r+4]-A[r]&M;W[r]=t1-h-S1(e)-CH(e,f,g)-K[r]&M
 for r in range(12,16):W[r]=BW[r]
 return W
K4_DL=[b-a&M for a,b in zip(BW[:16],M_PUB[:16])]
def k4_second(W):return[w+d&M for w,d in zip(W,K4_DL)]
class _L:
 def __init__(s,v):s.v=v
_LZ,_LO=_L(0),_L(1)
class K4BS:
 def __init__(s,m):s.m=m
 def X(s,a,b):
  if a is _LZ:return b
  if b is _LZ:return a
  if a is _LO:return s.N(b)
  if b is _LO:return s.N(a)
  return s.m.x(a,b)
 def A(s,a,b):
  if a is _LZ or b is _LZ:return _LZ
  if a is _LO:return b
  if b is _LO:return a
  return s.m.a(a,b)
 def R(s,a,b):
  if a is _LO or b is _LO:return _LO
  if a is _LZ:return b
  if b is _LZ:return a
  return s.m.r(a,b)
 def N(s,a):
  if a is _LZ:return _LO
  if a is _LO:return _LZ
  return s.m.n(a)
 def lit(s,k):return[_LO if k>>i&1 else _LZ for i in range(32)]
 def bcast(s,c):m=s.m;return[m.sb(0,m.a(m.sr(c,i),1))for i in range(32)]
 def add(s,P,Q,cin=_LZ):
  out=[];c=cin
  for i in range(32):
   t=s.X(P[i],Q[i]);out.append(s.X(t,c))
   if i<31:c=s.R(s.A(P[i],Q[i]),s.A(t,c))
  return out
 def sub(s,P,Q):return s.add(P,[s.N(q)for q in Q],_LO)
 def s0p(s,P):return[s.X(s.X(P[(i+7)%32],P[(i+18)%32]),P[i+3]if i+3<32 else _LZ)for i in range(32)]
 def neq(s,P,T):
  acc=_LZ
  for i in range(32):acc=s.R(acc,s.X(P[i],_LO if T>>i&1 else _LZ))
  return acc
K4_C11=BA[11]-S0(BA[10])-MAJ(BA[10],BA[9],BA[8])&M;K4_CA10=BA[10]-S0(BA[9])&M
def _k4class(a3):
 E11=a3+K4_C11&M
 return dict(a3=a3,E11=E11,t16=K4_CA10-MAJ(BA[9],BA[8],a3)&M,S0a3=S0(a3),CW8=BE[12]-BA[8]-S1(E11)-K[8]&M,CE5B=BA[9]-S0(BA[8])&M,
   C17K=s1(BW[15])+BE[14]-BA[10]-S1(BE[13])-CH(BE[13],BE[12],E11)-K[10]&M,blocks=[])
_K4TM=[(16,sum(0x0000FFFF<<32*t for t in range(8))),(8,sum(0x00FF00FF<<32*t for t in range(8))),(4,sum(0x0F0F0F0F<<32*t for t in range(8))),(2,sum(0x33333333<<32*t for t in range(8))),(1,sum(0x55555555<<32*t for t in range(8)))]
def _k4new(m):
 if m:m.o+=96
 return[0]*32
def _k4acc(W,j,v,m):
 W[j&31]|=v<<32*(j>>5)
 if m:m.o+=12
def _k4tr(W,m):
 W=list(W)
 for s_,mk in _K4TM:
  for q in range(16):
   r=q//s_*2*s_+q%s_;a,b=W[r],W[r+s_];t=(a>>s_^b)&mk;W[r+s_]=b^t;W[r]=a^t<<s_&ONES
 if m:m.o+=80*22+15
 return W
W3_LIT=__import__("base64").b85decode("c-rlqzi-<{6vv;Vs11S?b%UrtkRcJ!E}6P0lYt6By%Zf%z|5RQ9)fE091rn-kQPxUFA5w@U934v|Azt^lA-F{r9g+m$k(Dsks^=c{UA+>-w*I0@yNS-e0MyN@7_^+a%b=Uw_igJAg>_U?m^m+0c89XX}|f$^dN1>05Zn$JxCiefQ*s12WdkFkTLRhAV-jM$Ufu*GDmqmNE<SMj8S$E(uNEmW0c*296`<@`;ZgJ{3l<>4&(@O4%vsCK<22g137}6L-rvjkoldx58t3p5ArMIU&tSS{oR&r;D!Hj{C(~m@9(SjT&Q;Z^SNvd|F!(j|95g{(YK36b666z=EpB{XED%P!&sJF#QSv)47AoTmL-9$gI<>d1Fc__bvl8q)nkYYt=BKn3*+I?iJo=Gq7Ry1jTYmQ%MrT4zwd$NHGaG`dPpf9)1VVoOTn{=NZ-Sq=H#Ks6K^M;2u>&0M7&Py3Yy#$Iq>59!o*9Wg@sHeIOJ@CeW&<}43o?3lDTDGpUH{EYG0`vS3bE#NEW+akrMg&`GSY5l=0gIw+kpb3$1GPiY9JJG?lyND6kjAi{9Z#O9*KM+x*zM?T)1@@%Km#9Ny(RmNs4p27Srmf;H&#=5r_pgMdYYZ#ehR6`}G^#GD-~w@BPgvG85^UJmsZ>nor>Lbi(j4|V08&nn^7n*~1>P;?f0)oK-8U6Lp5?8FMRr@J1)uFtMt<F0?5KYWA`LXyrP)#I_q+H-N_$dDikBkjq%h<%poHtcK(AtGhp$XDf&jcn<YVwoL`R}SHoqus&yt4jzWqzbI9r8$l`3c@uwOJb{M5^G{2K8Pa9B%2;(dCynmEhBBl+gCz}-Zau^G+NvUJUcu*+<5fs(dceUGO~V_QFJ{C4Wc+{3lrqBH6e8+zA``8OtvJW@Kc{HYQD@rFo@!$ZA`#PWI{;!yxe_!Bjq-yi}Yk_{|3^N$ta?Gy@>i!ai9dvqvpY-3d!WlQm^GuzMGQ0@27TOnq)}Jmu8+c1%u+d_|f)1Hk)pPo(l75;iC5_I*NULsW?!A=24@#xEyu;N?$8^^voE0QrD;E*k>8F%4$ofmJm|wHN;o9tg<qz2-!Gn95xOcr)G`A70iSXLaM;}JLb=#j)Eti=fU~lt>R+wy&de^Nkqw}_$QJR+UpLD*u?FD2VEA`2G3}#+8Ku{jPz|%94^m@XT(TmLI{yW#C3Xru~>u~=Zb5#B+xonEV!PYc?=?r4vuF8J0Zg0cwq#4!k)QYCR%#tGKjSYEBe~|yiH}(r3fK}Yz0mtpvzroVXH)X1hlL8WT{|4v-7nPPD9r#v68@22}SR5)wY%H432{TxoV25rnqW~%Yv%6EXd;jFr|q9eUz*J15_ea@y|P%l&B|Wvq@%CXl$GcHx400ET;vW%!NpUUc+QIbH~Q1aN`g{2q98m|5+Vf$5O3HC2F=cn$=`>t{xN98~`~0QZo*KjU51mQ&VE)>~Dx>L>#!PwVZzq(TtE{qKkBHRiv2EJ+X>iF8EHTfQKJ8Y6BZJ;JrvRbnBM?@m;vnlvYqwT6x6=i><$@ND?nBio9ki@p5M=^xskye{dRo9TXut91mxHoYJ$|)bD41PKW-k>F{3mkxNt=N~>r#{lXt0ro&dWl<9C5<Xaw+Nc?@d71TGJJzCa)@2y{!Tj`|))viC$DbFuFG3AkxouRCXLPKVo$JS=+rNr8g5JF7(1lcCq7X")
W3_SHA="51ebea4ae91ee10f4def51f0b7b75ba167338265b4eb0f19726d2c6646688f5a"
W3_DFS_OP,W3_L_OP,W3_PAIR_OP=8,12,9
def _w3gen(m=None,verify=True):
 import zlib,hashlib
 A8,A9,A10,A11=BA[8],BA[9],BA[10],BA[11];E12,E13=BE[12],BE[13]
 c11,cA10=K4_C11,K4_CA10
 cW10=BE[14]-A10-S1(E13)-K[10]&M
 a2b,a3b=BA[6],BA[7]
 h0=MAJ(A8,a3b,a2b)-CH(E12,a3b+c11&M,a2b+cA10-MAJ(A9,A8,a3b)&M)&M
 D10=M_PUB[10]-MP_PUB[10]&M;T10=s0(MP_PUB[10]+D10&M)-s0(MP_PUB[10])&M
 Dl=D10&0xFFFF;Dh=D10>>16
 L0=[s0(v)for v in range(256)];L1=[s0(v<<8)for v in range(256)]
 H0=[s0(v<<16)for v in range(256)];H1=[s0(v<<24)for v in range(256)]
 def gen(a3,ctr):
  E11=a3+c11&M;t=cA10-MAJ(A9,A8,a3)&M
  def half(lo,hi,st0):
   res={};stk=[(lo,0,st0[0],st0[1])]
   while stk:
    i,xx,cc,bb=stk.pop()
    if i==hi:res.setdefault((cc,bb),[]).append(xx);continue
    ctr[0]+=1
    ti=t>>i&1;a8=A8>>i&1;a7=a3>>i&1;e12=E12>>i&1;e11=E11>>i&1;hb=h0>>i&1
    for xi in 0,1:
     yi=xi^ti^cc;mj=a8&a7|xi&(a8|a7);ch=e11 if e12 else yi
     if mj^ch^bb!=hb:continue
     c2=xi&ti|cc&(xi|ti);nb=1-mj&ch|1-(mj^ch)&bb
     stk.append((i+1,xx|xi<<i,c2,nb))
   return res
  lows=half(0,16,(0,0));kw=cW10-CH(E13,E12,a3+c11&M)-cA10+MAJ(A9,A8,a3)&M
  for st,lx in lows.items():
   his=[h>>16 for hs in half(16,32,st).values()for h in hs];ctr[1]+=len(lx);ctr[2]+=len(lx)*len(his)
   for l in lx:
    u=kw-l&M;wl=u&0xFFFF;s=wl+Dl;sl=s&0xFFFF;a=L0[wl&255]^L1[wl>>8];b=L0[sl&255]^L1[sl>>8];uh=u>>16;d=Dh+(s>>16)
    for hh in his:
     if(b^H0[(q:=uh-hh+d&0xFFFF)&255]^H1[q>>8])-(a^H0[(k:=uh-hh&0xFFFF)&255]^H1[k>>8])&M==T10:yield hh<<16|l
 def reader(ctr=None):
  dz=zlib.decompressobj();src=W3_LIT;pos=[0];buf=bytearray()
  def rd(n):
   while len(buf)<n:
    data=dz.unconsumed_tail
    if not data:
     if pos[0]<len(src):data=src[pos[0]:pos[0]+64];pos[0]+=64
     else:
      tail=dz.flush()
      if tail:
       buf.extend(tail)
       if ctr is not None:ctr[0]+=len(tail)
      break
    c=dz.decompress(data,64)
    if ctr is not None:ctr[0]+=len(c)
    buf.extend(c)
   out=bytes(buf[:n]);del buf[:n];return out
  return rd
 rd_a=reader();nc=int.from_bytes(rd_a(2),'little')
 rd_b=reader(K4R);skip=2+4*nc
 while skip:
  step=64 if skip>64 else skip;rd_b(step);skip-=step
 rd_b(4);bh=[b'\x00',8];H=hashlib.sha256()if verify else None;cnt=0
 for _cls in range(nc):
  a3=int.from_bytes(rd_a(4),'little')
  if m:m.o+=4
  C=_k4class(a3);pl=_k4new(m);j=0;ctr=[0,0,0]
  for x in gen(a3,ctr):
   if bh[1]>=8:bh[0]=rd_b(1);bh[1]=0
   rej=bh[0][0]>>bh[1]&1;bh[1]+=1
   if m:m.o+=3
   if rej:continue
   if verify:H.update(b"%08x%08x"%(a3,x))
   _k4acc(pl,j,x,m);j+=1;cnt+=1
   if j==256:yield C,_k4tr(pl,m),256;pl=_k4new(m);j=0
  if m:m.o+=ctr[0]*W3_DFS_OP+ctr[1]*W3_L_OP+ctr[2]*W3_PAIR_OP
  if j:yield C,_k4tr(pl,m),j
 if verify:
  assert cnt==361638,("w3 count",cnt)
  assert H.hexdigest()==W3_SHA,("w3 sha",H.hexdigest())
_k4gen=_w3gen
K4R=[0];K4B=1023;K4_INFB=37
K4_N=0;K4_CLASS_CONST={};K4_BLOCK_CONST=[]
class _K4C:o=0
_k4c=_K4C()
_cur=None;_z=_o=M
for C,p,n in _k4gen(_k4c):
 K4_N+=n;F=(1<<n)-1;zb=ob=M
 for i in range(32):
  b=p[i]&F
  if b:zb&=~(1<<i)
  if b!=F:ob&=~(1<<i)
 K4_BLOCK_CONST.append((zb,ob))
 if C is not _cur:
  if _cur is not None:K4_CLASS_CONST[_cur['a3']]=_z,_o
  _cur=C;_z=_o=M
 _z&=zb;_o&=ob
if _cur is not None:K4_CLASS_CONST[_cur['a3']]=_z,_o
K4_RAW=K4R[0];K4_PLANE_OPS=_k4c.o
def k4_x(planes,j):return sum((planes[b]>>j&1)<<b for b in range(32))
def k4_eval(s,a0,a1,u):
 m=s.m;t0=m.o
 m.o+=12;T=s.__dict__.setdefault('k4T',{});m.tick('k4',t0)
 if(a0,u)not in T:s.k4f(((a0,u),))
 elif len(T)-getattr(s,'k4c',0)>=getattr(s,'k4B',K4B):s.k4f()
def k4x(s,q):
 m=s.m;cv=s.cv;a0,u=q;a1=m.a(m.ad(m.ad(ms0(m,u),a0),s.CA1),M32)
 e1=s32(m,m.sb(m.ad(cv[2],a1),mS0(m,a0)),mMAJ(m,a0,cv[0],cv[1]));e0=m.ad(a0,s.c[1])
 w2b=s32(m,m.sb(m.sb(m.sb(m.sb(m.sb(0,mS0(m,a1)),mMAJ(m,a1,a0,cv[0])),cv[5]),mS1(m,e1)),mCH(m,e1,e0,cv[4])),K[2])
 return a0,a1,u,w2b
Attack.k4x=k4x
def k4f(s,ks=None):
 if ks is None:
  T=getattr(s,'k4T',None);c0=getattr(s,'k4c',0)
  if T is None or c0>=len(T):return
  it=lambda:itertools.islice(T,c0,None)
 else:
  it=lambda:ks
 m=s.m;t0=m.o;m.o+=K4_INFB*K4_RAW;G=[];c=None;B=K4BS(m)
 bi=0
 X=getattr(s,'k4_maxblk',None)
 for C,p,n in _k4gen(m,False):
  if X is not None and bi>=X:break
  if C is not c or len(G)==28:
   if c is not None:
    for q in it():s.k4p(*s.k4x(q),c,G)
   G=[];c=C
  zb,ob=K4_BLOCK_CONST[bi];bi+=1;G.append((p,n,zb,ob))
 for q in it():s.k4p(*s.k4x(q),c,G)
 if ks is None:s.k4c=len(T)
 m.tick('k4',t0)
def k4p(s,a0,a1,u,w2b,C,G,BC=None):
 m=s.m;B=K4BS(m);cv=s.cv;ib=getattr(s,'k4_ib',0);tz=s.__dict__.setdefault('k4z',{}).setdefault((a0,u),[])
 if BC is None:
  P_a0A8=B.bcast(m.a(m.ad(a0,BA[8]),M32));P_a1=B.bcast(a1)
 else:
  P_a0A8,P_a1=BC
 L8=B.lit(BA[8])
 a3=C['a3'];P_or=B.bcast(m.r(a3,a1));P_and=B.bcast(m.a(a3,a1));P_a0p=B.sub(B.lit(C['CW8']),B.sub(P_a0A8,B.lit(C['S0a3'])));P_a1=B.add(P_a1,B.lit(C['CE5B']));La3=B.lit(a3);Lw=B.lit(w2b);Sl=B.lit(C['t16']-u-C['C17K']+W17PUB&M)
 zz,oo=K4_CLASS_CONST[a3]
 for planes,nl,zb,ob in G:
  zc=zz|zb;oc=oo|ob
  Xp=[_LO if oc>>i&1 else _LZ if zc>>i&1 else m.ld(planes,i)for i in range(32)]
  y=B.add(Xp,Lw);z=B.add(Xp,Sl);sy=B.s0p(y)
  acc17=_LZ
  for i in range(32):acc17=B.R(acc17,B.X(sy[i],z[i]))
  acc8=None
  if ib or s.check or s.measure:
   _t8=m.o
   E10=B.add(Xp,B.lit(C['t16']))
   MJ=[B.R(B.A(Xp[i],P_or[i]),P_and[i])for i in range(32)]
   MJ2=[B.R(B.A(L8[i],La3[i]),B.A(Xp[i],B.R(L8[i],La3[i])))for i in range(32)]
   E9=B.sub(P_a1,MJ2)
   CHp=[E10[i]if C['E11']>>i&1 else E9[i]for i in range(32)]
   W8=B.sub(B.add(P_a0p,MJ),CHp)
   W8D=list(W8);W8D[30]=B.N(W8[30]);W8D[31]=B.X(W8[31],W8[30])
   Sb=B.s0p(W8);Sa=list(Sb)
   for i in 12,13,23,24,27,28:Sa[i]=B.X(B.X(W8D[(i+7)%32],W8D[(i+18)%32]),W8D[i+3])
   Sb=B.add(Sb,B.lit(T8));acc8=_LZ
   for i in range(32):acc8=B.R(acc8,B.X(Sa[i],Sb[i]))
   m.o=_t8
  if ib:
   F=(1<<nl)-1;q=~(acc8&F if not isinstance(acc8,_L)else F*acc8.v)&F
   while q:
    j=(q&-q).bit_length()-1;q&=q-1;s.k4n=getattr(s,'k4n',0)+1
    x=k4_x(planes,j);c=C['C17K']-x-C['t16']&M;y=x,c;R=s.__dict__.setdefault('k4i',{}).setdefault((a0,u),[0,set(),0,set()]);R[0]+=1;R[1].add(y);w=c+s0(x+w2b&M)+u&M
    if s.check and R[0]%997==1:assert w==expand(k4_words(cv,a0,a1,x,a3))[17]
    if(w*2654435761&M)>>32-ib==0:R[2]+=1;R[3].add(y)
    if s.k4n%16==0:
     z=kt(k4_words(cv,a0,a1,k4_x(planes,j),a3))
     if z is not None:tz.append(z)
  hit=B.N(acc17);hm=m.a(hit,(1<<nl)-1)if not isinstance(hit,_L)else 0 if hit is _LZ else(1<<nl)-1
  s.st['k4_lanes']=s.st.get('k4_lanes',0)+nl
  if s.measure:s.st['k4_f8']=s.st.get('k4_f8',0)+nl-bin((acc8 if not isinstance(acc8,_L)else 0 if acc8 is _LZ else(1<<256)-1)&(1<<nl)-1).count('1')
  if s.check:
   for j in range(0,nl,32):
    x=k4_x(planes,j);V=k4_words(cv,a0,a1,x,a3)
    o8=not acc8>>j&1 if not isinstance(acc8,_L)else acc8 is _LZ
    me=lambda P:sum((p>>j&1 if not isinstance(p,_L)else p.v)<<i for i,p in enumerate(P))
    w17m=me(sy)+u+C['C17K']-me(E10)&M
    assert V[9]==build(cv,a0,a1)[9] and o8==(s0(V[8]+D8&M)-s0(V[8])&M==T8) and w17m==expand(V)[17] and me([acc17])==(w17m!=W17PUB)
  while m.jnz(hm):
   low=m.a(hm,m.sb(0,hm));hm=m.x(hm,low);j=low.bit_length()-1;m.o+=16
   x=k4_x(planes,j);s.st['k4_w17a']=s.st.get('k4_w17a',0)+1;m.o+=400+96
   W1m=k4_words(cv,a0,a1,x,a3)
   if s0(W1m[8]+D8&M)-s0(W1m[8])&M!=T8:continue
   s.st['k4_w17']=s.st.get('k4_w17',0)+1;m.o+=2*2812;W2m=k4_second(W1m)
   if W1m!=W2m and compress(cv,W1m)==compress(cv,W2m):
    s.st['collisions']=s.st.get('collisions',0)+1;s.success=True
    s.pairs_found=getattr(s,'pairs_found',[])+[(list(cv),W1m,W2m,getattr(s,'m0',None))]
    if getattr(s,'m0',None)is not None:s.messages=getattr(s,'messages',[])+[(list(s.m0)+list(W1m),list(s.m0)+list(W2m))]
  m.ad(0,1);m.jge(0,1)
Attack.k4_eval=k4_eval;Attack.k4f=k4f;Attack.k4p=k4p
def k4d(s,a0,u):
 t0=s.m.o;T=s.__dict__.setdefault('k4T',{});k=a0,u;s.m.o+=12;n=k not in T
 if n and len(T)<1536:T[k]=0;s.m.o+=468
 s.m.tick('k4',t0);return n
Attack.k4d=k4d
K4_EN_LB=360.880
K4_OPS_PER_CLAW=15925
def k4_budget():
 lam=-math.log(1-0.39)+2**-40;B=lam/(58959.42*K4_EN_LB*2**-32*2**-74.3238)
 return int(B)+1,int((int(B)+1)*K4_OPS_PER_CLAW*58959.42)
TP=[]
def kt(W):
 if not TP:
  for w in BW,M_PUB:x=expand(list(w[:16]));A,E=traj(CV_PUB,x,23)[:2];TP.append(([A[21],A[20],A[19],A[18],E[21],E[20],E[19],E[18]],x[16:18],A,E))
  TP.append([(TP[0][2][t+4]^TP[1][2][t+4],TP[0][3][t+4]^TP[1][3][t+4])for t in range(23)])
 o=[]
 for w,(q,p,_,_) in zip((W,k4_second(W)),TP[:2]):
  x=list(w[:16])+p;a,b,c,d,e,f,g,h=q;r=[]
  for t in range(18,23):
   x.append(s1(x[t-2])+x[t-7]+s0(x[t-15])+x[t-16]&M);t1=h+S1(e)+CH(e,f,g)+K[t]+x[t]&M;h,g,f,e,d,c,b,a=g,f,e,d+t1&M,c,b,a,t1+S0(a)+MAJ(a,b,c)&M;r.append((a,e))
  o.append(r)
 F=TP[2];v=[(p[0]^q[0],p[1]^q[1])for p,q in zip(*o)]
 if v[0]!=F[18]:return None
 return sum(bin(v[k][0]^F[18+k][0]).count('1')+bin(v[k][1]^F[18+k][1]).count('1')for k in(1,2,3,4))
K4_WIN_EXP={14672896933643966474:(221,5,0,90504,5208,0,17118583,27610200),15921217793420643850:(215,3,0,90504,5163,0,8611774,19073338),17552297034189817508:(226,4,1,90504,9744,0,8605264,24083220),1866586107145425828:(205,2,0,90504,3866,0,8612172,19666920)}
K4_PASS=441411;F=K4_PLANE_OPS+K4_INFB*K4_RAW;assert K4_OPS_PER_CLAW==math.ceil(464337752/58959.42+K4_PASS*.016203+F/58959.42),'k4 opc'
def _k4e(i,sd):
 if i>3:return None
 import gc;gc.collect();assert not[1 for o in gc.get_objects()for r in[o]+gc.get_referents(o)if r is not K4_BLOCK_CONST and(type(r)in(list,tuple,set,dict)and len(r)>>10 and type(next(iter(r)))in(int,tuple)or type(r)in(bytes,bytearray,memoryview))and len(r)>>12]
 A=Attack(win=1<<21,seed=sd,check=True,k4=True);A.k4_max=2;A.k4_ib=7;A.k4_maxblk=181;A.k4B=(i>0)*K4B or 1;A.run_window();st=A.st
 t=st["claws_distinct"],st["f9"],st["f8"],st.get("k4_lanes",0),st.get("k4_f8",0),st.get("k4_w17",0),A.m.cat.get("k4",0),A.m.o
 if sd in K4_WIN_EXP:assert t==K4_WIN_EXP[sd],('k4 win',t)
 O=Attack(win=1<<21,seed=sd,check=True);O.run_window();o=O.st;assert(o['claws_distinct'],o['f9'],o['f8'],O.m.o)==(t[0],t[1],t[2],t[7]-t[6])
 assert kt(list(BW[:16]))==0
 I=list(getattr(A,'k4i',{}).values());A.k4i={}
 Z=[z for z in A.k4z.values()if len(z)>1];n=sum(len(z)for z in Z);g=sum(map(sum,Z))/n;k=len(Z)
 TF=round(sum(len(z)*(sum(z)/len(z)-g)**2 for z in Z)/(k-1)/(sum(sum((v-sum(z)/len(z))**2 for v in z)for z in Z)/(n-k)),4)
 return{"distinct_claws":t[0],"passed_f9":t[1],"passed_f8":t[2],"k4_lanes":t[3],"k4_f8":t[4],"k4_w17":t[5],"k4_ops":t[6],"ops":t[7],"ops_off":O.m.o,"tail_F":TF,"tail_n":n,"ind_N":sum(r[0]for r in I),"ind_D":sum(len(r[1])for r in I),"ind_H":sum(r[2]for r in I),"ind_K":sum(len(r[3])for r in I),"ind_x2":round(sum((len(r[3])-len(r[1])/128)**2/(len(r[1])/128*127/128)for r in I),4)}
def serve():
 req=json.load(sys.stdin)
 eid=req["experiment_id"]
 if eid not in GEN_EXPERIMENTS:raise SystemExit("unknown experiment id")
 fn=_e1 if eid==GEN_EXPERIMENTS[0]else _k4e
 rows=[]
 for t in req["trials"]:
  obs=fn(t["trial"],int(t["seed"][:16],16))
  row={"trial":t["trial"],"message_a_hex":None,"message_b_hex":None}
  if obs:row["observations"]=obs
  rows.append(row)
 sys.stdout.write(json.dumps({"schema_version":1,"trials":rows},sort_keys=True,separators=(",",":"))+"\n")
B_WINDOWS=762275399377730730492917603366
W_BUDGET=350726972497108224219614943610625477015
def main():
 a=sys.argv[1:]
 if "--attack" in a:
  seed=int(a[a.index("--seed")+1])if "--seed" in a else None;w=0
  K4ON="--k4" in a;BW_,WB_=k4_budget()if K4ON else(B_WINDOWS,W_BUDGET)
  work=0
  while w<BW_ and work<WB_:
   A=Attack(win=P.WIN,seed=None if seed is None else seed*1000+w,check=False,k4=K4ON);assert A.k4_max is None and getattr(A,'k4_maxblk',None)is None;A.measure=False;A.run_window();w+=1;work+=A.m.o+6
   for M1,M2 in getattr(A,"messages",[]):
    print("collision","".join("%08x"%x for x in M1),"".join("%08x"%x for x in M2),flush=True);return
  print("no collision %d %d %d %d"%(w,work,BW_,WB_),flush=True);sys.exit(1)
 serve()
if __name__=="__main__":
 main()
