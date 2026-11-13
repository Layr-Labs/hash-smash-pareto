"""Credits: dariolina, newjordan, sraiw."""
import sys,os,json,random,time,hashlib,math
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
 c9=BW[9]+BA[5]+K4_HD&M
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
CONDS_16_17=lambda:[(16+(v&1),((v>>5&3,16+(v&1)-(v>>7&3),v>>9&31),)+(()if v>>14&1 else((v>>15&3,16+(v&1)-(v>>17&3),v>>19&31),)),v>>1&15)for v in _C1617]
def _build_by_bit():
 ex=CONDS_16_17()
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
BY_BIT_16_17=[]
def solve_row_exact(A0,E0,W0,A1,E1,W1,r):
 ma_r,sa_r,me_r,se_r,mw_r,sw_r=ROW_MASKS_16_17[r]
 dsch=s1(W1[r-2])+W1[r-7]+s0(W1[r-15])-(s1(W0[r-2])+W0[r-7]+s0(W0[r-15]))&M
 idx=r+4
 t10=E0[idx-4]+S1(E0[idx-1])+CH(E0[idx-1],E0[idx-2],E0[idx-3])+K[r]&M
 t11=E1[idx-4]+S1(E1[idx-1])+CH(E1[idx-1],E1[idx-2],E1[idx-3])+K[r]&M
 t20=S0(A0[idx-1])+MAJ(A0[idx-1],A0[idx-2],A0[idx-3])&M
 t21=S0(A1[idx-1])+MAJ(A1[idx-1],A1[idx-2],A1[idx-3])&M
 ce0,ce1,ca0,ca1=A0[idx-4]+t10&M,A1[idx-4]+t11+dsch&M,t10+t20&M,t11+t21+dsch&M
 by_bit=(BY_BIT_16_17 or BY_BIT_16_17.append(_build_by_bit())or BY_BIT_16_17)[0][r];out=[];steps=[0]
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
  ks.append(dict(recs=recs,dppol=dppol,nreg=nreg,fn=ns.pop("k"),
    counts={o:sum(1 for r in recs if r[0]==o)for o in range(4)}))
 return ks
class GW:
 AVAILABLE=False
 ops=staticmethod(lambda c:575000)
ONES=(1<<256)-1
M32=M;M32_2=M|M<<128
M20,M31,M40,ML=(1<<20)-1,(1<<31)-1,(1<<40)-1,2047<<20
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
 WIN=1<<26
 KTRY=32
 DTRY=8192
 QCAP,QFULL=3584,3328
 WHEEL=2048
 WDIG=(13,1),(12,1),(11,1),(10,1),(7,1),(5,1)
 GCAP=575000
 RCAP=206
 KCAP=679
 KCAP0=710
 SCREEN=1
 CMP1=10
 D0,KRES=82,6
def table_words(wdig=P.WDIG):return sum(sg*(1<<k)for k,sg in wdig)
def k4_scr(cv):
 cw_,eb_,P_,R_=consts5(consts(cv))[:4]
 return 3*bin(R_&0x00F27618).count('1')+2*bin(R_&0x7F0D89E6).count('1')+2*(eb_>>1&1)+(eb_>>2&1)+(P_>>31&1)-bin(P_&0x1FFFFFFE).count('1')
class Attack:
 def __init__(s,win=P.WIN,seed=1,check=False,k4=False,screen=None):
  s.screen=P.SCREEN if screen is None else screen;s.k4=k4;s.k4_max=None;s.m=Mach();s.win=win;s.check=check;s.dpreg=DPREG;s.W=table_words()
  s.ks=None;s.R=[0]*256
  s.rnd=random.SystemRandom()if seed is None else random.Random(seed)
  s.st=dict(windows=0,iters=0,hits=0,matches=0,raw=0,trails=0,cuts=0,s2phases=0,s2iters=0,pairs=0,f9=0,f8=0,w17=0,parks=0,resumes=0,
    verify=0,qmax=0,opp=0,same=0,claws_distinct=0,moves=0,drops=0,waits=0)
  s.idc0=256;s.distinct=set();s.cv_id=0;s.cv_try=False;s.measure=True
  s.LA=[0]*256;s.sav=[0]*32
  s.base_setup()
 def base_setup(s):
  m=s.m;t0=m.o
  m.o+=2*2812+120
  s.C9=BW[9]+BA[5]+K4_HD&M32;s.C9P=s.C9|1<<64
  m.tick('run_setup',t0)
 def window_setup(s,cv=None):
  m=s.m;t0=m.o;s.m0=None;s.skip=False;tries=0;drops=0
  while True:
   drawn=cv is None or s.cv_try
   if drawn:
    blk=[s.rnd.getrandbits(32)for _ in range(16)];m.o+=2
    s.m0=blk;m.o+=16
    cv=compress(IV,blk);m.o+=2812
   s.cv_try=True
   if drawn and s.screen:
    t_=m.o;m.o+=4;S=k4_scr(cv);m.o+=183
    if S>5:m.o+=3
    if s.check:s.__dict__.setdefault('scr',[]).append((S,m.o-t_))
    if S>5:
     s.st['ddraws']=s.st.get('ddraws',0)+1;drops+=1
     if drops>=P.DTRY:s.skip=True;return
     continue
   ks_try=make_kernels_folded(consts(cv),P.DPB)
   gops=GW.ops(consts5(consts(cv)))
   if len(ks_try[0]['recs'])<=(P.KCAP if s.screen else P.KCAP0)and gops<=P.GCAP and max(ks_try[0]['nreg'],ks_try[1]['nreg'])<=P.RCAP:break
   m.o+=min(gops,P.GCAP);s.st['kskip']=s.st.get('kskip',0)+1
   tries+=1;m.o+=142
   if tries>=P.KTRY:s.skip=True;return
  s.cv=cv;s.cv_id+=1
  s.c=consts(cv);m.o+=140
  cw=s.c[0]
  s.CA1=cv[6]+K[1]-cw&M32
  tg=m.o;c5=consts5(s.c);s.ks=ks_try
  m.o+=gops+8*len(s.ks[0]['recs'])
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
   a1c=recover_a1(s.cv,a0,u);Wk=k4_words(s.cv,a0,a1c,*K4_Q[0][3]);Wx=expand(Wk)
   assert W9&M32==BW[9]+BA[5]+K4_HD-a1c&M==Wk[9]and Wx[16]==G16 and Wk[1]==u and ok==inF(Wk[9],D9,T9)
  m.be('claw_filter',tb0);m.tick('claw_filter',t0)
  if not ok:return 0
  s.st['f9']+=1;a1=m.a(a1u,M32)
  if s.k4 and(s.k4_max is None or s.st['f9']<=s.k4_max)and s.k4d(a0,u):s.k4_eval(a0,a1,u)
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
  bk=m.sr(m.ad(m.ad(m.sl(r,6),m.sl(r,5)),r),15);pos=m.ad(m.sl(bk,5),m.sl(bk,3))
  word=m.sr(pos,8);sh=m.a(pos,255);chk=m.a(r,511)
  w=m.ld(s.tab,word);v=m.sr(w,sh);w1=0;word1=0;rsh=0;st2=m.jge(sh,217)
  if st2:word1=m.ad(word,1);rsh=m.sb(256,sh);w1=m.ld(s.tab,word1);v=m.r(v,m.sl(w1,rsh))
  e=m.a(v,M40)
  lw=m.ld(s.LA,l);en0=m.ad(lw,s.it20p)
  if s.check:
   ln=s.it-((lw^NM20)>>20)
   assert 0<=ln<2048 and pos==40*(r*97>>15)and en0==lw&M20|ln<<20
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
   if m.jge(m.a(en0,ML),m.a(e,ML)):
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
  if s.k4 and s.__dict__.get('k4D'):m=s.m;o=m.o;c=dict(m.cat);s.k4f(s.k4D);m.o=o;m.cat=c
  return s.st
GEN_EXPERIMENTS="r39-transplant-claw","r39k4-window-small"
def _e1(i,sd):
 if i==0:
  adv=verify_advice_construction()
  assert adv=={"g16_fibre_size":2,"g17_fibre_size":1,"fibre_dfs_ops":1944,"downward_inv_ok":1,
    "advice_slice_cands":256,"advice_slice_hits":1,"ops_per_cand":411}
  Q=[g[3]for g in K4_Q];W=[k4_words(CV_PUB,BA[4],BA[5],*q)for q in Q];A0,E0,_=traj(CV_PUB,MP_PUB,16);A1,E1,_=traj(CV_PUB,M_PUB,16);T=[]
  for w in W:
   a,e,_=traj(CV_PUB,w,16);b,f,_=traj(CV_PUB,k4_second(w),16)
   T.append(int(all(a[r]^b[r]==A0[r]^A1[r]and e[r]^f[r]==E0[r]^E1[r]for r in range(20))and a[8:20]==A0[8:20]and e[12:20]==E0[12:20]))
  out={"sfs_collision":int(compress(CV_PUB,MP_PUB)==compress(CV_PUB,M_PUB)and MP_PUB!=M_PUB),"advice_w16_is_g":int(expand(MP_PUB)[16]==G16),
    "advice_w17":int(expand(MP_PUB)[17]==W17PUB),"fibre":FIB,"fibre_shift":K4_HD,"groups":len(Q),"classes":sum(len(g[1])for g in K4_Q),
    "sample_valid":sum(h4ok(*q)for q in Q),"sample_w9_shifted":sum(w[9]==BW[9]+K4_HD&M for w in W),"sample_w16_one_value":len({expand(w)[16]for w in W}),
    "sample_trail":sum(T),"g16_fibre_size":adv["g16_fibre_size"],"g17_fibre_size":adv["g17_fibre_size"],"fibre_dfs_ops":adv["fibre_dfs_ops"],
    "advice_slice_hits":adv["advice_slice_hits"],"ops_per_cand":adv["ops_per_cand"]}
  assert out=={"advice_slice_hits":1,"advice_w16_is_g":1,"advice_w17":1,"classes":728,"fibre":1019866814,"fibre_dfs_ops":1944,"fibre_shift":97451488,"g16_fibre_size":2,"g17_fibre_size":1,"groups":200,"ops_per_cand":411,"sample_trail":200,"sample_valid":200,"sample_w16_one_value":1,"sample_w9_shifted":200,"sfs_collision":1}
  return out
 rnd=random.Random(sd)
 cv=[rnd.getrandbits(32)for _ in range(8)]
 a0=rnd.getrandbits(32)&~1;u=rnd.getrandbits(32)|1
 c=consts(cv)
 a1=recover_a1(cv,a0,u);W=k4_words(cv,a0,a1,*K4_Q[sd%len(K4_Q)][3]);V=k4_second(W)
 A1,E1,_=traj(cv,W);A2,E2,_=traj(cv,V)
 out={"transplant_ok":int(A1[8:20]==BA[8:20]and E1[12:20]==BE[12:20]and A2[8:20]==CA[8:20]and E2[12:20]==CE[12:20]),
  "w1_is_u":int(W[1]==u),"w16_identity":int(expand(W)[16]-G16&M==fstep(u,c)-fstep(a0,c)&M)}
 assert out=={"transplant_ok":1,"w1_is_u":1,"w16_identity":1}
 if i==1:out.update(verify_advice_construction())
 return out

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
   if i<31:c=s.R(P[i],c)if Q[i]is _LO else s.R(s.A(P[i],Q[i]),s.A(t,c))
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
K4_NG,K4_NC,K4_NB,K4_IND=200,728,300,50
FIB=0x3cc9eebe;K4_CUBE=0xf74400da;K4_E11A=BA[7]+K4_C11&M
K4_HD=FIB-MAJ(BA[8],BA[7],BA[6])+CH(BE[12],K4_E11A,BA[6]+K4_CA10-MAJ(BA[9],BA[8],BA[7])&M)&M
K4_W11C=BE[15]-BA[11]-K4_C11-S1(BE[14])-CH(BE[14],BE[13],BE[12])-K[11]&M;K4_T11=s0(BW[11]+K4_DL[11]&M)-s0(BW[11])&M
_K4CAP=(2,13,7),(9,26,7),(15,19,7),(3,14,6),(10,27,6),(16,20,6)
_K4LV=[[[j for j,(a,b,c)in enumerate(_K4CAP)if c>>s&1 and a<i<=b]for i in range(33)]for s in range(3)]
K4_STOP=160
def _k4st(i,st,x,K,T,A7,E1,L,o):
 s,cy,bw,b10,cv=st;g=s-1;cp=dict(zip(_K4LV[s][i],cv));o.o+=K4_STOP*(L.bit_length()+255>>8)
 Y=T^L*(x^cy);mj=(A7|L*x)if BA[8]>>i&1 else A7&L*x;ch=E1 if BE[12]>>i&1 else Y
 ok=L^mj^ch^L*(bw^FIB>>i&1);W=K^L*(x^b10)
 for j in _K4LV[s][i]:
  if _K4CAP[j][1]==i:c=cp.pop(j);ok&=W if(1^c,1^c,c,c^g,c^g,1^c^g)[j]else L^W
 if i==30:ok&=(L^W if s else W)&(L^Y^E1)
 if i==31 and s:ok&=W if g else L^W
 V=[L if x&cy else T if x|cy else 0,(L^mj)&ch|(L^mj^ch)&L*bw,L if x&b10 else L^K if x|b10 else 0]
 nj=[j for j in _K4LV[s][i+1]if j not in cp]
 if nj:V.append(W)
 P=[(ok,0)]if ok else[]
 for t,v in enumerate(V):P=[(q,b|e<<t)for p,b in P for q,e in((p&v,1),(p&~v,0))if q]
 R=[]
 for p,b in P:
  if nj:cp[nj[0]]=b>>3
  R.append(((s,b&1,b>>1&1,b>>2&1,tuple(cp[j]for j in _K4LV[s][i+1])),p))
 return R
def _k4fe(C,o):
 L=(1<<len(C))-1;V=[(c['C17K']-s1(BW[15])-c['t16']&M,c['t16'],c['a3'],c['E11'])for c in C]
 PL=[[sum((v[q]>>b&1)<<l for l,v in enumerate(V))for q in range(4)]for b in range(32)];o.o+=128*len(C)
 F=[0]*33;F[32]={(s,a,b,c,()):L for s in range(3)for a in(0,1)for b in(0,1)for c in(0,1)}
 for i in range(31,-1,-1):
  D={}
  for s in range(3):
   n=len(_K4LV[s][i])
   for v in range(8<<n):
    st=s,v&1,v>>1&1,v>>2&1,tuple(v>>3+j&1 for j in range(n));a=0
    for x in 0,1:
     for ns,p in _k4st(i,st,x,*PL[i],L,o):a|=p&F[i+1].get(ns,0)
    if a:D[st]=a
  F[i]=D
 return F,V
def _k4lf(F,V,l,d,o):
 K,T,A,E=V[l];Mm={};S=[(0,(s,0,0,0,()),0)for s in range(3)if F[0].get((s,0,0,0,()),0)>>l&1]
 while S:
  i,st,p=S.pop();o.o+=8
  if i==d:yield p;continue
  q=Mm.get((i,st))
  if q is None:q=Mm[i,st]=[(ns,x)for x in(0,1)for ns,_ in _k4st(i,st,x,K>>i&1,T>>i&1,A>>i&1,E>>i&1,1,o)if F[i+1].get(ns,0)>>l&1]
  for ns,x in q:S.append((i+1,ns,p|x<<i))
def _k4cls():
 C=[];m=0
 while 1:
  a3=(K4_E11A^m)-K4_C11&M
  if inF(K4_W11C-a3&M,K4_DL[11],K4_T11):C.append(_k4class(a3))
  m=m-K4_CUBE&K4_CUBE
  if not m:return sorted(C,key=lambda c:(c['t16']-c['C17K']&M,c['a3']))
class _K4C:o=0
_k4c=_K4C();K4_Q=[]
def _k4fin(k,cs,pf,sm,o):
 p=sorted(pf);B=[]
 for i in range(0,len(p),256):
  W=_k4new(o)
  for j,v in enumerate(p[i:i+256]):_k4acc(W,j,v,o)
  B.append((_k4tr(W,o)[:18],len(p[i:i+256])))
 K4_Q.append((k,cs,B,sm))
def _k4build(o):
 C=_k4cls();g=None;cs=[]
 for lo in range(0,len(C),256):
  F,V=_k4fe(C[lo:lo+256],o)
  for l,c in enumerate(C[lo:lo+256]):
   k=c['t16']-c['C17K']&M
   if k!=g:
    if cs:_k4fin(g,cs,pf,sm,o)
    g=k;cs=[];pf=set();sm=None
   e=0
   for p in _k4lf(F,V,l,18,o):pf.add(p);e=1
   if e:
    cs.append(c['a3'])
    if sm is None:sm=next(_k4lf(F,V,l,32,o)),c['a3']
  F=V=None
 if cs:_k4fin(g,cs,pf,sm,o)
_k4build(_k4c)
assert len({g[0]for g in K4_Q})==len(K4_Q)==K4_NG and sum(len(g[1])for g in K4_Q)==K4_NC and sum(len(g[2])for g in K4_Q)==K4_NB,'k4 list'
K4_SETUP=_k4c.o+2**30;K4_T10=s0(BW[10]+K4_DL[10]&M)-s0(BW[10])&M
K4_CLASS_CONST={}
def h4ok(a2,a3):c=_k4class(a3);return int(MAJ(BA[8],a3,a2)-CH(BE[12],c['E11'],a2+c['t16']&M)&M==FIB and inF(c['C17K']-s1(BW[15])-c['t16']-a2&M,K4_DL[10],K4_T10)and not(a2+c['t16']^c['E11'])>>30&1)
def _k4ind():
 f=_k4ind.__dict__
 if'X'not in f:
  X=f['X']=[];o=_K4C()
  for k,cs,_,_ in K4_Q[::K4_IND]:
   C=[_k4class(a)for a in cs];F,V=_k4fe(C,o)
   for l,c in enumerate(C):
    G=[];z=n=M;e=sorted(_k4lf(F,V,l,32,o))
    for i in range(0,len(e),256):
     W=_k4new(None)
     for j,v in enumerate(e[i:i+256]):_k4acc(W,j,v,None)
     P=_k4tr(W,None);r=len(e[i:i+256]);R=(1<<r)-1;zb=ob=M
     for b in range(32):
      if P[b]&R:zb&=~(1<<b)
      if P[b]&R!=R:ob&=~(1<<b)
     G.append((P,r,zb,ob));z&=zb;n&=ob
     if len(G)==28:X.append((c,G));G=[]
    if G:X.append((c,G))
    K4_CLASS_CONST[c['a3']]=z,n
 return f['X']
def k4_x(planes,j):return sum((planes[b]>>j&1)<<b for b in range(32))
def k4_eval(s,a0,a1,u):
 s.k4q(a0,u)
 if s.check or s.measure:
  m=s.m;o=m.o;c=dict(m.cat);z=dict(s.st)
  if s.check and s.st['f9']<2:
   for g in K4_Q:
    n=s.st.get('k4_w17a',0);q=s.st.get('k4s',0);p=m.o;s.k4q(a0,u,(g[0],expand(k4_words(s.cv,a0,a1,*g[3]),18)[17]));q=s.st['k4s']-q;p=m.o-p-843-403*len(g[2])-711*q
    assert s.st['k4_w17a']>n and p%563==0 and 563*q<=p<=563*q*len(g[1]),'k4 plant'
   s.st=z
  s.__dict__.setdefault('k4D',[]).append((a0,u));m.o=o;m.cat=c
def k4q(s,a0,u,T=None):
 m=s.m;cv=s.cv;t0=m.o;m.o+=624;a0,a1,u,w=s.k4x((a0,u));tg=T[1]if T else W17PUB
 WB=[m.sb(0,m.a(m.sr(w,i),1))for i in range(18)]
 for kd,cs,B,_ in K4_Q:
  if T and T[0]!=kd:continue
  m.o+=10;r=m.a(m.sb(m.sb(m.ad(kd,tg),u),w),M32);RB=[m.sb(0,m.a(m.sr(r,i),1))for i in range(32)]
  for P,n in B:
   y=[];c=k=acc=None
   for i in range(18):
    p=m.ld(P,i);t=m.x(p,WB[i]);y.append(t if c is None else m.x(t,c))
    if i<17:c=m.a(p,WB[i])if c is None else m.r(m.a(p,WB[i]),m.a(t,c))
   for i in range(32):
    t=m.x(y[i],RB[i]);v=t if k is None else m.x(t,k)
    if i<31:k=m.a(y[i],RB[i])if k is None else m.r(m.a(y[i],RB[i]),m.a(t,k))
    if i<14:y.append(m.x(m.x(v,y[i+7]),y[i+3]))
    else:
     e=m.x(y[(i+7)%32],y[i-14]);e=m.x(e,y[i+3])if i<29 else e;e=m.x(v,e);acc=e if acc is None else m.r(acc,e)
   m.o+=9;h=m.a(m.n(acc),m.sb(m.sl(1,n),1));s.st['k4q']=s.st.get('k4q',0)+n
   while m.jnz(h):
    lo=m.a(h,m.sb(0,h));h=m.x(h,lo);j=lo.bit_length()-1;m.o+=706;x=sum((q>>j&1)<<b for b,q in enumerate(y));s.st['k4s']=s.st.get('k4s',0)+1
    assert s0(x)==x+r&M;x=x-w&M;w9=BW[9]+BA[5]+K4_HD-a1&M
    for a3 in cs:
     m.o+=563;W=k4_words(cv,a0,a1,x,a3)
     if W[9]!=w9 or expand(W,18)[17]!=tg or not inF(W[10],K4_DL[10],K4_T10):continue
     s.st['k4_w17a']=s.st.get('k4_w17a',0)+1
     if T:break
     for b in cs:
      m.o+=560;W1m=k4_words(cv,a0,a1,x,b)
      if W1m[9]!=w9 or expand(W1m,18)[17]!=W17PUB or s0(W1m[8]+D8&M)-s0(W1m[8])&M!=T8:continue
      s.st['k4_w17']=s.st.get('k4_w17',0)+1;m.o+=2*2812;W2m=k4_second(W1m)
      if W1m!=W2m and compress(cv,W1m)==compress(cv,W2m):
       s.st['collisions']=s.st.get('collisions',0)+1;s.success=True
       if getattr(s,'m0',None)is not None:s.messages=getattr(s,'messages',[])+[(list(s.m0)+list(W1m),list(s.m0)+list(W2m))]
     break
 m.tick('k4',t0)
def k4x(s,q):
 m=s.m;cv=s.cv;a0,u=q;a1=m.a(m.ad(m.ad(ms0(m,u),a0),s.CA1),M32)
 e1=s32(m,m.sb(m.ad(cv[2],a1),mS0(m,a0)),mMAJ(m,a0,cv[0],cv[1]));e0=m.ad(a0,s.c[1])
 w2b=s32(m,m.sb(m.sb(m.sb(m.sb(m.sb(0,mS0(m,a1)),mMAJ(m,a1,a0,cv[0])),cv[5]),mS1(m,e1)),mCH(m,e1,e0,cv[4])),K[2])
 return a0,a1,u,w2b
Attack.k4x=k4x
def k4f(s,ks):
 m=s.m;t0=m.o
 for C,G in _k4ind():
  for q in ks:s.k4p(*s.k4x(q),C,G)
 m.tick('k4',t0)
def k4p(s,a0,a1,u,w2b,C,G):
 m=s.m;B=K4BS(m);cv=s.cv;ib=getattr(s,'k4_ib',0)
 a3=C['a3'];Lw=B.lit(w2b);Sl=B.lit(C['t16']-u-C['C17K']+W17PUB&M);f8=ib or s.check or s.measure
 if f8:
  _t8=m.o;P_a0A8=B.bcast(m.a(m.ad(a0,BA[8]),M32));P_a1=B.bcast(a1);L8=B.lit(BA[8])
  P_or=B.bcast(m.r(a3,a1));P_and=B.bcast(m.a(a3,a1));P_a0p=B.sub(B.lit(C['CW8']),B.sub(P_a0A8,B.lit(C['S0a3'])));P_a1=B.add(P_a1,B.lit(C['CE5B']));La3=B.lit(a3);m.o=_t8
 zz,oo=K4_CLASS_CONST[a3]
 for planes,nl,zb,ob in G:
  zc=zz|zb;oc=oo|ob
  Xp=[_LO if oc>>i&1 else _LZ if zc>>i&1 else m.ld(planes,i)for i in range(32)]
  y=B.add(Xp,Lw);z=B.add(Xp,Sl);sy=B.s0p(y)
  acc17=_LZ
  for i in range(32):acc17=B.R(acc17,B.X(sy[i],z[i]))
  acc8=None
  if f8:
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
    if(w*2654435761&M)>>32-ib==0:R[2]+=1;R[3].add(y)
Attack.k4_eval=k4_eval;Attack.k4f=k4f;Attack.k4p=k4p;Attack.k4q=k4q
def k4d(s,a0,u):
 t0=s.m.o;T=s.__dict__.setdefault('k4T',{});k=a0,u;s.m.o+=12;n=k not in T and len(T)<944
 if n:T[k]=0;s.m.o+=468
 s.m.tick('k4',t0);return n
Attack.k4d=k4d
K4_EN_LB=10671.5
K4_OPS_PER_CLAW=10352
def k4_budget():
 lam=(-math.log(1-0.39)+2**-40)/(1-.071833);B=lam/(57003.18*K4_EN_LB*2**-32*2**-74.4783)
 return int(B)+1,int((int(B)+1)*K4_OPS_PER_CLAW*57003.18)
K4_WIN_EXP={14672896933643966474:(233,7,0,436800,2,0,1019221,11504962),15921217793420643850:(222,11,0,624000,5,0,1454268,13875066),17552297034189817508:(256,4,0,249600,2,0,584630,13031225),1866586107145425828:(232,1,0,62400,0,0,144113,11245985)}
K4_PASS=733+sum(110+403*len(g[2])for g in K4_Q);assert K4_PASS==143633 and K4_OPS_PER_CLAW>=590047946/57003.18 and K4_OPS_PER_CLAW>=589493660/57003.18 and K4_SETUP==1107473556 and 94.0681-math.log2(k4_budget()[1]/2812+K4_SETUP/2812+2**43+2**42/2812)>=0 and 32*(table_words()+P.QCAP//4+1+18*sum(len(g[2])for g in K4_Q))+348233<=2**20,'k4 opc'
def _k4e(i,sd):
 if i>3:return None
 A=Attack(win=1<<21,seed=sd,check=True,k4=True,screen=0);A.k4_ib=7;A.run_window();st=A.st
 t=st["claws_distinct"],st["f9"],0,st.get("k4q",0),st.get("k4s",0),st.get("k4_w17",0),A.m.cat.get("k4",0),A.m.o
 if sd in K4_WIN_EXP:assert t==K4_WIN_EXP[sd],('k4 win',sd,t)
 if i<2:O=Attack(win=1<<21,seed=sd,check=True,screen=0);O.run_window();o=O.st;assert(o['claws_distinct'],o['f9'],o['f8'],O.m.o)==(t[0],t[1],t[2],t[7]-t[6])
 I=[(len(r[1]),len(r[3]))for r in A.k4i.values()]
 v=sum(d for d,k in I),sum(k for d,k in I),round(sum((k-d/128)**2/(d/128*127/128)for d,k in I),4),len(I)
 E=((59256,437,6.5188,7),(67492,518,7.9839,10),(17882,142,0.7772,4),(1872,7,4.0067,1));R=_k4e.__dict__.setdefault('R',[]);R+=[v];d,q,x=[sum(e[j]for e in R)for j in range(3)]
 assert v==E[i]and(len(R)<4 or d>=96821 and(q-d/128)**2<6.58*d/128 and x<40.29),('k4 diag',v)
 if i==0:
  Z=Attack(win=1<<21,seed=sd,check=True,k4=True,screen=1);Z.run_window();L=Z.scr
  assert not Z.skip and k4_scr(Z.cv)<=5 and L and all(c==187+3*(S>5)for S,c in L)and Z.st.get('ddraws',0)==sum(S>5 for S,c in L),('k4 screen',len(L))
 return{"distinct_claws":t[0],"passed_f9":t[1],"k4_lanes":t[3],"k4_surv":t[4],"k4_w17":t[5],"k4_ops":t[6],"ops":t[7],"ops_off":t[7]-t[6],"k4_setup":K4_SETUP,"ind_D":v[0],"ind_K":v[1],"ind_x2":v[2],"ind_claws":v[3]}
def serve():
 req=json.load(sys.stdin)
 eid=req["experiment_id"]
 if eid[:9]=="r39-mate-":return exec(open(__file__).read().split("'"*3)[1],{"L":sys.modules[__name__],"Q_":req})
 if eid not in GEN_EXPERIMENTS:raise SystemExit("unknown experiment id")
 fn=_e1 if eid==GEN_EXPERIMENTS[0]else _k4e
 rows=[]
 for t in req["trials"]:
  obs=fn(t["trial"],int(t["seed"][:16],16))
  row={"trial":t["trial"],"message_a_hex":None,"message_b_hex":None}
  if obs:row["observations"]=obs
  rows.append(row)
 sys.stdout.write(json.dumps({"schema_version":1,"trials":rows},sort_keys=True,separators=(",",":"))+"\n")
def main():
 a=sys.argv[1:]
 if "--attack" in a:
  seed=int(a[a.index("--seed")+1])if "--seed" in a else None;w=0
  BW_,WB_=k4_budget()
  work=0
  while w<BW_ and work<WB_:
   A=0;A=Attack(win=P.WIN,seed=None if seed is None else seed*1000+w,check=False,k4=True);assert A.k4_max is None and getattr(A,'k4_maxblk',None)is None;A.measure=False;A.run_window();w+=1;work+=A.m.o+6
   for M1,M2 in getattr(A,"messages",[]):
    print("collision","".join("%08x"%x for x in M1),"".join("%08x"%x for x in M2),flush=True);return
  print("no collision %d %d %d %d"%(w,work,BW_,WB_),flush=True);sys.exit(1)
 serve()
r'''import sys,json,random,math,struct
M=0xffffffff
class Sw:
    def __init__(w,L):
        w.L=L;w.m=int.from_bytes((M).to_bytes(8,"little")*L,"little");w.o=int.from_bytes((1).to_bytes(8,"little")*L,"little")
    def bc(w,c):return(c&M)*w.o
    def rnd(w,rng):return rng.getrandbits(64*w.L)&w.m
    def S1(w,e):return((e>>6|e<<26)^(e>>11|e<<21)^(e>>25|e<<7))&w.m
    def S0(w,a):return((a>>2|a<<30)^(a>>13|a<<19)^(a>>22|a<<10))&w.m
    def s1(w,u):return((u>>17|u<<15)^(u>>19|u<<13)^(u>>10))&w.m
    def s0(w,v):return((v>>7|v<<25)^(v>>18|v<<14)^(v>>3))&w.m
    def neg(w,z):return((z&w.m)^w.m)+w.o
    def zero(w,x):
        f=(((x+w.m)>>32)&w.o)^w.o;out=[]
        while f:lo=f&-f;out.append((lo.bit_length()-1)>>6);f^=lo
        return out
    def get(w,x,i):return(x>>(64*i))&M
Z=Sw(1);S0,S1,s0,s1=Z.S0,Z.S1,Z.s0,Z.s1
def CH(e,f,g):return(e&f)^(~e&g&M)
def MJ(a,b,c):return(a&b)^(a&c)^(b&c)
def cr(n):
    x=1<<(n.bit_length()//3+1)
    while 1:
        y=(2*x+n//(x*x))//3
        if y>=x:return x
        x=y
K=[cr(p<<96)&M for p in[p for p in range(2,168)if all(p%q for q in range(2,p))]]
NR=39
CV=[int(x,16)for x in "aa79ff87 65c5bb49 d0a84bfd 90ccc398 fac64fb6 4ff7998a b1af5ec5 aa1ed4d5".split()]
MX=[int(x,16)for x in("8334d670 3813877e f19d46d5 77556fc4 902f98c7 0500282c a4235533 9100e365 "
"a76f5fe2 5eb3226d dd603088 00a467b3 a95af91e b06304ad 43660038 d80d950f").split()]
DL=[0]*8+[0x40000000,0xf7801000,0xc0000000,0x0601dcd4,0xffefe800,0,0,0]
MY=[(a+b)&M for a,b in zip(MX,DL)]
PIN={16:0x9776869e,17:0x771adf7e}
T8,T9,MASK8,MASK9=0x087ff000,0x03010000,0xCC19E60C,0xF9983C0F
CA={18:"=u"+"="*30}
CE={18:"0=======0=====100==000=0=======0",19:"============u=============n=====",
20:"======uu=======u================",22:"=u"+"="*30,23:"=0"+"="*30}
LIN=[(0,17,16,0,18,16,0),(0,17,24,0,18,24,0),(0,17,26,0,18,26,0),(0,17,30,0,18,30,0),
(0,18,10,0,17,21,0),(0,18,7,0,18,19,1),(0,18,9,0,18,18,1),(1,17,5,1,18,5,0),
(1,17,19,1,18,19,0)]
def cell(s):
    m=v=d=0
    for i,c in enumerate(s):
        b=1<<(31-i);m|=b*(c in "01un");v|=b*(c in "1u");d|=b*(c in "un")
    return(m,v,M,d)
EQ=cell("="*32);CAr={t:cell(CA.get(t,"="*32))for t in range(18,24)};CEr={t:cell(CE.get(t,"="*32))for t in range(18,24)}
NF={t:bin(CEr[t][0]).count("1")for t in CEr}
def trace(cv,w,nr):
    W=list(w)
    for i in range(16,nr):W.append((s1(W[i-2])+W[i-7]+s0(W[i-15])+W[i-16])&M)
    A=[cv[3],cv[2],cv[1],cv[0]];E=[cv[7],cv[6],cv[5],cv[4]]
    for i in range(nr):
        e=(A[i]+E[i]+S1(E[i+3])+CH(E[i+3],E[i+2],E[i+1])+K[i]+W[i])&M
        A.append((e-A[i]+S0(A[i+3])+MJ(A[i+3],A[i+2],A[i+1]))&M);E.append(e)
    return A,E,W
def compress(cv,w):
    A,E,_=trace(cv,w,NR)
    return[(x+y)&M for x,y in zip(cv,A[-1:-5:-1]+E[-1:-5:-1])]
def dok(c,D):
    m,v,dm,d=c;cs=1
    for b in range(32):
        ns=0;db=(D>>b)&1
        for cin in(0,1):
            if(cs>>cin)&1:
                for xb in(0,1):
                    if(m>>b)&1 and xb!=(v>>b)&1:continue
                    if(dm>>b)&1 and db^cin!=(d>>b)&1:continue
                    ns|=1<<((xb&db)|(xb&cin)|(db&cin))
        cs=ns
        if not cs:return False
    return True
class St:pass
def cp(s):
    n=St();n.xa,n.xe,n.xw,n.ya,n.ye,n.yw=s.xa[:],s.xe[:],s.xw[:],s.ya[:],s.ye[:],s.yw[:];return n
def wd(s,u):return s1(s.yw[u-2])-s1(s.xw[u-2])+s.yw[u-7]-s.xw[u-7]+DL[u-16]+s0(s.yw[u-15])-s0(s.xw[u-15])
def consts(s,t):
    xa,xe,ya,ye=s.xa,s.xe,s.ya,s.ye;i=t+4
    rx=xa[i-4]+xe[i-4]+S1(xe[i-1])+CH(xe[i-1],xe[i-2],xe[i-3])
    ry=ya[i-4]+ye[i-4]+S1(ye[i-1])+CH(ye[i-1],ye[i-2],ye[i-3])
    cx=-xa[i-4]+S0(xa[i-1])+MJ(xa[i-1],xa[i-2],xa[i-3])
    cy=-ya[i-4]+S0(ya[i-1])+MJ(ya[i-1],ya[i-2],ya[i-3])
    d=wd(s,t);de=ry-rx+d
    return cx&M,(rx+K[t])&M,de&M,(de+cy-cx)&M,d&M,cy&M
def setrow(s,t,ex):
    cx,rx,de,da,d,cy=consts(s,t);i=t+4
    s.xe[i]=ex;s.xw[t]=(ex-rx)&M;s.xa[i]=(ex+cx)&M
    s.ye[i]=(ex+de)&M;s.yw[t]=(s.xw[t]+d)&M;s.ya[i]=(s.ye[i]+cy)&M
def cok(c,x,y):return(x&c[0])==c[1]and((x^y)&c[2])==c[3]
def rowok(s,t):
    i=t+4
    if not(cok(CAr[t],s.xa[i],s.ya[i])and cok(CEr[t],s.xe[i],s.ye[i])and cok(EQ,s.xw[t],s.yw[t])):return False
    g=lambda k,r:(s.xa if k==0 else s.xe)[r+4]
    return t!=18 or all(((g(k1,r1)>>b1)^(g(k2,r2)>>b2))&1==df for k1,r1,b1,k2,r2,b2,df in LIN)
def rowokv(s,t,xw,ex,ax,yw,ye,ay):
    if not(cok(CAr[t],ax,ay)and cok(CEr[t],ex,ye)and cok(EQ,xw,yw)):return False
    if t!=18:return True
    for k1,r1,b1,k2,r2,b2,df in LIN:
        v1=(ax if k1==0 else ex)if r1==18 else(s.xa if k1==0 else s.xe)[r1+4]
        v2=(ax if k2==0 else ex)if r2==18 else(s.xa if k2==0 else s.xe)[r2+4]
        if((v1>>b1)^(v2>>b2))&1!=df:return False
    return True
def look1(s,t,ex,ax,ye,ay):
    i=t+5
    d=wd(s,t+1)&M
    if d:return False
    rx=s.xa[i-4]+s.xe[i-4]+S1(ex)+CH(ex,s.xe[i-2],s.xe[i-3])
    ry=s.ya[i-4]+s.ye[i-4]+S1(ye)+CH(ye,s.ye[i-2],s.ye[i-3])
    cx=-s.xa[i-4]+S0(ax)+MJ(ax,s.xa[i-2],s.xa[i-3])
    cy=-s.ya[i-4]+S0(ay)+MJ(ay,s.ya[i-2],s.ya[i-3])
    de=ry-rx+d
    return dok(CAr[t+1],(de+cy-cx)&M)and dok(CEr[t+1],de&M)
def wd2(s,t,xw,yw):return(s1(yw)-s1(xw)+s.yw[t-5]-s.xw[t-5]+DL[t-14]+s0(s.yw[t-13])-s0(s.xw[t-13]))&M
def cands(s,t,nb,sw,rng):
    cx,rx,de,da,dw,cy=consts(s,t)
    if dw:return[]
    mA,vA,_,dA=CAr[t];mE,vE,_,dE=CEr[t];nx=t<23;m=sw.m
    xa,xe,ya,ye=s.xa,s.xe,s.ya,s.ye;i=t+4;bc=sw.bc;S0v,S1v=sw.S0,sw.S1
    DE,CX,DA,NM,VE,DEc,MA,VA,DAc=bc(de),bc(cx),bc(da),bc(~mE),bc(vE),bc(dE),bc(mA),bc(vA),bc(dA)
    if nx:
        CD=bc(ya[i-3]+ye[i-3]-xa[i-3]-xe[i-3]+wd(s,t+1));CN=bc(xa[i-3]-ya[i-3])
        xe1,xe2,ye1,ye2,xa1,xa2,ya1,ya2=[bc(z)for z in(xe[i-1],xe[i-2],ye[i-1],ye[i-2],xa[i-1],xa[i-2],ya[i-1],ya[i-2])]
    good=[]
    for _ in range(nb):
        ex=(sw.rnd(rng)&NM)|VE;ey=(ex+DE)&m;ax=(ex+CX)&m;ay=(ax+DA)&m
        bad=(ex^ey^DEc)|((ax&MA)^VA)|(ax^ay^DAc)
        if nx:
            deu=(CD+S1v(ey)+(ye2^(ey&(ye1^ye2)))+sw.neg(S1v(ex)+(xe2^(ex&(xe1^xe2)))))&m
            bad|=(deu+S0v(ay)+((ay&(ya1|ya2))|(ya1&ya2))+sw.neg(S0v(ax)+((ax&(xa1|xa2))|(xa1&xa2)))+CN)&m
        good+=[sw.get(ex,q)for q in sw.zero(bad)]
    out=[]
    for ex in good:
        axv=(ex+cx)&M;yev=(ex+de)&M;xwv=(ex-rx)&M;ywv=(xwv+dw)&M;ayv=(yev+cy)&M
        if not rowokv(s,t,xwv,ex,axv,ywv,yev,ayv):continue
        if nx and not look1(s,t,ex,axv,yev,ayv):continue
        if t<22 and wd2(s,t,xwv,ywv):continue
        out.append(ex)
    return out
def start():
    s=St();s.xa=[0]*43;s.xe=[0]*43;s.ya=[0]*43;s.ye=[0]*43
    s.xw=MX[:]+[0]*(NR-16);s.yw=MY[:]+[0]*(NR-16)
    Ax,Ex,_=trace(CV,MX,NR);Ay,Ey,_=trace(CV,MY,NR)
    for r in range(15,20):s.xa[r],s.xe[r],s.ya[r],s.ye[r]=Ax[r],Ex[r],Ay[r],Ey[r]
    for t in(16,17):setrow(s,t,PIN[t])
    return s
CFG={18:(512,8),19:(2048,8),20:(2048,8),21:(128,4),22:(256,6),23:(4,1)}
NP=800
def smc(rng):
    P=[start()]*NP;ks=[];l2=0.0;SW={}
    for t in range(18,24):
        L,nb=CFG[t];sw=SW.setdefault(L,Sw(L));pool=[]
        for pi,p in enumerate(P):
            for ex in cands(p,t,nb,sw,rng):pool.append((pi<<32)|ex)
        ks.append(len(pool))
        if not pool:return None,ks,None
        l2+=math.log2(len(pool)/(NP*nb*L))-NF[t]
        P2=[]
        for _ in range(NP):
            e=pool[rng.randrange(len(pool))];s2=cp(P[e>>32]);setrow(s2,t,e&M);P2.append(s2)
        P=P2
    return P,ks,l2
def inF(i,T,w):return((s0((w+DL[i])&M)-s0(w))&M)==T
def members(mask,i,T):
    out=[];sub=0
    while True:
        if inF(i,T,sub):out.append(sub)
        sub=(sub-mask)&mask
        if sub==0:return out
def finals(s,sw,x8,x9):
    m=sw.m;bc=sw.bc;S0v,S1v,s0v,s1v=sw.S0,sw.S1,sw.s0,sw.s1
    if not hasattr(sw,"kp"):sw.kp=(bc(DL[8]),bc(DL[9]),[bc(K[t])for t in range(NR)])
    kb8,kb9,kb=sw.kp
    xw=[bc(v)for v in s.xw[:24]]+[0]*(NR-24);yw=[bc(v)for v in s.yw[:24]]+[0]*(NR-24)
    xw[8]=x8;xw[9]=x9;yw[8]=(x8+kb8)&m;yw[9]=(x9+kb9)&m
    a,b,c,d=[bc(s.xa[i])for i in(27,26,25,24)];e,f,g,h=[bc(s.xe[i])for i in(27,26,25,24)]
    A,B,C,D=[bc(s.ya[i])for i in(27,26,25,24)];E,F,G,H=[bc(s.ye[i])for i in(27,26,25,24)]
    for t in range(24,NR):
        xw[t]=(s1v(xw[t-2])+xw[t-7]+s0v(xw[t-15])+xw[t-16])&m
        yw[t]=(s1v(yw[t-2])+yw[t-7]+s0v(yw[t-15])+yw[t-16])&m
        k=kb[t]
        t1=h+S1v(e)+(g^(e&(f^g)))+k+xw[t];t2=S0v(a)+((a&(b|c))|(b&c))
        h,g,f,e,d,c,b,a=g,f,e,(d+t1)&m,c,b,a,(t1+t2)&m
        t1=H+S1v(E)+(G^(E&(F^G)))+k+yw[t];t2=S0v(A)+((A&(B|C))|(B&C))
        H,G,F,E,D,C,B,A=G,F,E,(D+t1)&m,C,B,A,(t1+t2)&m
    return sw.zero((a^A)|(b^B)|(c^C)|(d^D)|(e^E)|(f^F)|(g^G)|(h^H))
def verify(s,w8,w9):
    xw=s.xw[:];xw[8]=w8;xw[9]=w9
    for t in range(23,15,-1):xw[t-16]=(xw[t]-s1(xw[t-2])-xw[t-7]-s0(xw[t-15]))&M
    w=xw[:16];A={r:s.xa[r+4]for r in range(12,16)};E={r:s.xe[r+4]for r in range(12,16)}
    for i in range(15,-1,-1):
        A[i-4]=(E[i]-A[i]+S0(A[i-1])+MJ(A[i-1],A[i-2],A[i-3]))&M
        E[i-4]=(E[i]-A[i-4]-S1(E[i-1])-CH(E[i-1],E[i-2],E[i-3])-K[i]-w[i])&M
    cv=[A[-1],A[-2],A[-3],A[-4],E[-1],E[-2],E[-3],E[-4]]
    return compress(cv,w)==compress(cv,[(a+b)&M for a,b in zip(w,DL)]),(A[0]&1)*2+(w[1]&1)
def known_answer():
    s=start();Ex=trace(CV,MX,NR)[1]
    for t in range(18,24):
        setrow(s,t,Ex[t+4])
        if not rowok(s,t):return 0
    return int(finals(s,Sw(1),MX[8],MX[9])==[0]and verify(s,MX[8],MX[9])[0])
NCH,NB,LF=20,80,2048
EXP_S="""
9638,3208,2872,12729,9321,3200|-61.612326|463|108,122,121,112
9748,3226,2655,12784,9677,3200|-61.640930|461|113,116,124,108
9502,3180,3090,12586,9217,3200|-61.572412|483|129,127,117,110
9514,3160,3060,12815,9898,3200|-61.464915|434|103,116,103,112
9556,3214,2903,12655,10262,3200|-61.476125|455|117,107,117,114
9687,3180,2906,12705,10145,3200|-61.481189|473|120,111,124,118
9519,3229,2992,12833,9513,3200|-61.520627|428|102,107,111,108
9652,3304,3253,12766,9514,3200|-61.354223|464|100,135,118,111
9531,3261,3055,12788,9788,3200|-61.438475|475|129,113,113,120
9561,3241,2980,13044,9783,3200|-61.450818|448|118,118,110,102
9675,3231,2916,12852,9797,3200|-61.488828|418|96,110,106,106
9619,3166,3035,12484,9392,3200|-61.571637|463|118,109,125,111
9429,3127,3056,12637,9934,3200|-61.509837|478|120,113,121,124
9560,3230,2880,12927,8804,3200|-61.670234|455|119,122,114,100
"""
def _exp_decode(t):
    out={}
    for i,ln in enumerate(t.strip().splitlines()):
        ks,l2,hs,cs=ln.split("|")
        out["r39-tail-%02d"%(i+1)]=([int(x)for x in ks.split(",")],float(l2),int(hs),[int(x)for x in cs.split(",")])
    return out
EXP=_exp_decode(EXP_S)
QDECL=-74.54
def verify_smc_stats(qdecl=None):
    c18=len(cands(start(),18,32,Sw(2048),random.Random(12345)))
    if not EXP:
        return c18
    L18,NB18=CFG[18];n=len(EXP)
    assert c18==206 and abs(c18/65536-sum(v[0][0]for v in EXP.values())/(n*NP*L18*NB18))<0.0003
    qlin=[(2.0**v[1])*(v[2]/float(NCH*NB*LF))for v in EXP.values()]
    qlog=[math.log2(q)for q in qlin]
    m_lin=sum(qlin)/n
    sd_lin=math.sqrt(sum((q-m_lin)**2 for q in qlin)/(n-1))
    lcb_lin=math.log2(m_lin-2.650308*sd_lin/math.sqrt(n))
    m_log=sum(qlog)/n
    lcb_log=m_log-2.650308*math.sqrt(sum((x-m_log)**2 for x in qlog)/(n-1))/math.sqrt(n)
    lcb999=math.log2(m_lin-3.852*sd_lin/math.sqrt(n))
    tcls=[sum(v[3][k]for v in EXP.values())for k in range(4)]
    assert sum(tcls)==sum(v[2]for v in EXP.values())
    assert lcb_lin>qdecl and lcb_log>qdecl and lcb999>qdecl
    q01=[(2.0**v[1])*(4.0*v[3][1]/float(NCH*NB*LF))for v in EXP.values()]
    m01=sum(q01)/n;sd01=math.sqrt(sum((q-m01)**2 for q in q01)/(n-1))
    assert math.log2(m01-2.650308*sd01/math.sqrt(n))>qdecl
    return c18
def main():
    req=json.loads(sys.stdin.read());eid=req.get("experiment_id","");tr=req["trials"]
    qdecl=QDECL if EXP else None
    pat8=members(MASK8,8,T8);pat9=members(MASK9,9,T9);c18=verify_smc_stats(qdecl)
    P,ks,l2=smc(random.Random(tr[0]["seed"]));r=random.Random(tr[0]["seed"]+"m");mv=0
    for _ in range(3000):
        w=r.getrandbits(32);u=r.getrandbits(32)
        for i,mk,T in((8,MASK8,T8),(9,MASK9,T9)):
            mv+=inF(i,T,w)!=inF(i,T,(w&mk)|(u&~mk&M))
    kat=known_answer()
    assert kat==1 and mv==0 and len(pat8)==1152 and len(pat9)==2080
    obs=[dict({"np":NP,"kat":kat,"n_f8":len(pat8),"n_f9":len(pat9),"mask_viol":mv,"log2_carrier":round(l2,6),
    "calib_c18":c18,"lin_lcb_ok":1},**{"k%d"%t:k for t,k in zip(range(18,24),ks)})]
    sw=Sw(LF);n8=sw.bc(~MASK8);n9=sw.bc(~MASK9);tcls=[0]*4
    for j in range(1,NCH+1):
        r=random.Random(tr[j]["seed"]);cls=[0]*4;v=0
        for b in range(NB):
            s=P[((j-1)*NB+b)%NP]
            x8=int.from_bytes(struct.pack("<%dQ"%LF,*r.choices(pat8,k=LF)),"little")|(sw.rnd(r)&n8)
            x9=int.from_bytes(struct.pack("<%dQ"%LF,*r.choices(pat9,k=LF)),"little")|(sw.rnd(r)&n9)
            for q in finals(s,sw,x8,x9):
                ok,c=verify(s,sw.get(x8,q),sw.get(x9,q));v+=ok;cls[c]+=1
        assert v==sum(cls)
        for k in range(4):tcls[k]+=cls[k]
        obs.append({"n":NB*LF,"hits":sum(cls),"verified":v,"c00":cls[0],"c01":cls[1],"c10":cls[2],"c11":cls[3]})
    if eid in EXP:
        assert(ks,round(l2,6),sum(o["hits"]for o in obs[1:]),tcls)==EXP[eid]
    out=[dict({"trial":j,"message_a_hex":None,"message_b_hex":None},**({"observations":obs[j]}if j<len(obs)else{}))for j in range(len(tr))]
    sys.stdout.write(json.dumps({"schema_version":1,"trials":out},separators=(",",":")))
import zlib,base64,hashlib,array
N=NR;AX,EX,_=trace(CV,MX,N);AY,EY,_=trace(CV,MY,N);DA=[(AX[t+4]^AY[t+4],EX[t+4]^EY[t+4])for t in range(N)]
z=zlib.decompress(base64.b85decode(b'c-j+>5RYKJz<Q0Hg`I_Q2jfAp4PqNucd)Kud%^aC@d)EC#tDoQ7!nv#z;p&f3J(Jh12YItV4lG6fZ+)W{{_Pn6$TXsP9TJdqw_(K;Q+${7%jvg#K6+P(!j>R#=zLX*nrO8*0HTar$Bd+RgYB<p9bIJEfcm((4C;GVr5}v!MB62k57P4fH{G=1x!z1Zi#V-aS&?|7mzKGEnrt*j{)(;9iaRI_85A&PiF_zeJN<}tHAC)u?JAT2YU<v8H7<@'));G=[int.from_bytes(z[i:i+2],'big')*8 for i in range(0,400,2)]
def kw(c,a):
 A=[c[3],c[2],c[1],c[0],*a,*AX[8:12]];E=c[7:3:-1]+[0]*8+EX[12:16];W=MX[:]
 for i in range(12):
  if i<8:t=A[i+4]-S0(A[i+3])-MJ(A[i+3],A[i+2],A[i+1])&M;E[i+4]=A[i]+t&M
  else:t=E[i+4]-A[i]&M
  W[i]=t-E[i]-S1(E[i+3])-CH(E[i+3],E[i+2],E[i+1])-K[i]&M
 return W
def fd(c,w):
 x=trace(c,w,N);y=trace(c,[p+q&M for p,q in zip(w,DL)],N)
 for t in range(N):
  if(x[0][t+4]^y[0][t+4],x[1][t+4]^y[1][t+4])!=DA[t]:return t
 return N
Q=[];_cp=compress
def compress(c,w):Q.append((c,w));return _cp(c,w)
X_='1c2a4d979b83f580e8ffd12af6d85dedce0d28face1d716f69df3db191be5c1d464b972346b49615ab16e26befa211256274119cd93e1b096490685638d7af01f48c9f76d12faabfad0a281898b9e60d230a61bd'
def main(q):
 e=q.get('experiment_id','');tr=q['trials'];assert sum(G)==9701592 and known_answer()==1 and verify_smc_stats(QDECL)==206
 R=random.Random;P,ks,l2=smc(R(tr[0]['seed']));g=R(tr[0]['seed']+'g');C=[];X=[];gs=[]
 for _ in range(4):
  u=g.randrange(9701592);i=0
  while u>=G[i]:u-=G[i];i+=1
  c=L.K4_Q[i][1];o=L._K4C();F,V=L._k4fe([L._k4class(a)for a in c],o);x=array.array('I');y=bytearray()
  for l in range(len(c)):n=len(x);x.extend(L._k4lf(F,V,l,32,o));y+=bytes([l])*(len(x)-n)
  assert len(x)==G[i];C+=[c];X+=[(x,y)];gs+=[i]
 p8=members(MASK8,8,T8);p9=members(MASK9,9,T9);w=Sw(LF);n8=w.bc(~MASK8);n9=w.bc(~MASK9)
 pk=lambda v:int.from_bytes(struct.pack('<%dQ'%LF,*v),'little');h=f=m=0;dv={};cl={};cc=[0]*4;W3=[]
 for j in range(1,7):
  r=R(tr[j]['seed'])
  for b in range(80):
   s=cp(P[((j-1)*80+b)%NP]);k=r.randrange(4);x,y=X[k];q=r.randrange(len(x));a2,a3=x[q],C[k][y[q]];v=kw([0]*8,(0,0,a2,a3))
   s.xw[10],s.xw[11]=v[10],v[11];s.yw[10],s.yw[11]=v[10]+DL[10]&M,v[11]+DL[11]&M
   x8=pk(r.choices(p8,k=LF))|(w.rnd(r)&n8);x9=pk(r.choices(p9,k=LF))|(w.rnd(r)&n9)
   for l in finals(s,w,x8,x9):
    Q.clear();v=verify(s,w.get(x8,l),w.get(x9,l));assert v[0];cc[v[1]]+=1;c,mw=Q[0];W3+=[mw[3]];A=trace(c,mw,N)[0][4:8]
    assert A[2:]==[a2,a3]and kw(c,A)==mw and fd(c,mw)==N;h+=1;cl[s.xw[18]]=cl.get(s.xw[18],0)+1
    for b3 in C[k]:
     if b3!=a3 and L.h4ok(a2,b3):
      m+=1;u=kw(c,(*A[:2],a2,b3))
      if inF(8,T8,u[8]):f+=1;d=fd(c,u);assert d>17;dv[d]=dv.get(d,0)+1
 t=sum(n for d,n in dv.items()if d>19);assert t==0
 o=dict(log2_carrier=round(l2,6),ks=ks,groups=gs,hits=h,mates=m,mates_f8=f,first_deviation_row={str(d):n for d,n in sorted(dv.items())},through19=t,carrier_w18_clusters=len(cl),cluster_sum_sq=sum(n*n for n in cl.values()),cluster_sizes=sorted(cl.values()),cls=cc,w3=W3)
 o['digest']=hashlib.sha256(json.dumps(o,sort_keys=True).encode()).hexdigest()[:16]
 if X_:k=int(e[9:])-1;assert o['digest'][:12]==X_[12*k:12*k+12]
 v={x:y for x,y in o.items()if type(y)in(int,float)};v['digest48']=int(o['digest'][:12],16)
 print(json.dumps({'schema_version':1,'trials':[{'trial':j,'message_a_hex':None,'message_b_hex':None,**({'observations':v}if j<1 else{})}for j in range(len(tr))]}))
main(Q_)
'''
if __name__=="__main__":
 main()
