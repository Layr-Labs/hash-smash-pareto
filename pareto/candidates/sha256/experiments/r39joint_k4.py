"""Credits: dariolina, newjordan, sraiw."""
import sys,os,json,random,time,hashlib,math,zlib,base64
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
 ops=staticmethod(lambda c:575000)
ONES=(1<<256)-1
M32=M;M32_2=M|M<<128
M20,M31,M40,ML=(1<<20)-1,(1<<31)-1,(1<<40)-1,2047<<20
NM20=ONES^M20
M64=(1<<64)-1
M25=(1<<25)-1
HIGHMASK=[sum(1<<p for p in range(256)if p>>k&1)for k in range(8)]
C_LOG16=sum(r<<(5*((1<<r)-(1<<r>>7))&255)for r in range(16))
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
def s32(m,a,b):return m.a(m.sb(a,b),M32)
class P:
 DPB=7
 MAXS=1536
 CUTP=512
 WIN=1<<26
 KTRY=32
 DTRY=8192
 QCAP,QFULL=640,384
 WHEEL=2048
 WDIG=(5,1),(7,1),(10,1),(11,1),(12,1),(13,1)
 GCAP=575000
 RCAP=206
 KCAP=679
 KCAP0=710
 SCREEN=1
 CMP1=10
 D0,KRES=82,6
def table_words(wdig=P.WDIG):return sum(sg*(1<<k)for k,sg in wdig)
def pop32_swar(x):
 x-=x>>1&0x55555555
 x=(x&0x33333333)+(x>>2&0x33333333)
 x=(x+(x>>4))&0x0f0f0f0f
 x+=x>>8;x+=x>>16
 return x&63
def k4_scr(cv):
 cw_,eb_,P_,R_=consts5(consts(cv))[:4]
 return 3*pop32_swar(R_&0x00F27618)+2*pop32_swar(R_&0x7F0D89E6)+2*(eb_>>1&1)+(eb_>>2&1)+(P_>>31&1)-pop32_swar(P_&0x1FFFFFFE)
WMAX_CAP=582000000
class CapStop(Exception):pass
class Attack:
 def __init__(s,win=P.WIN,seed=1,check=False,k4=False,screen=None,wmax=1<<60):
  s.wmax=wmax;s.screen=P.SCREEN if screen is None else screen;s.k4=k4;s.k4_max=None;s.m=Mach();s.win=win;s.check=check;s.dpreg=DPREG;s.W=table_words()
  s.ks=None;s.R=[0]*256
  s.rnd=random.SystemRandom()if seed is None else random.Random(seed)
  s.st=dict(f9=0,f8=0,claws_distinct=0)

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
    t_=m.o;m.o+=4;S=k4_scr(cv);m.o+=65
    if S>5:m.o+=3
    if s.check:s.__dict__.setdefault('scr',[]).append((S,m.o-t_))
    if S>5:
     s.st['ddraws']=s.st.get('ddraws',0)+1;drops+=1
     if drops>=P.DTRY:s.skip=True;return
     continue
   ks_try=make_kernels_folded(consts(cv),P.DPB)
   gops=GW.ops(consts5(consts(cv)))
   if len(ks_try[0]['recs'])<=(P.KCAP if s.screen else P.KCAP0)and gops<=P.GCAP and max(ks_try[0]['nreg'],ks_try[1]['nreg'])<=P.RCAP:break
   m.o+=min(gops,P.GCAP)
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
  m=s.m;t0=m.o;tb0=m.bs()
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
  k['fn'](R);m.o+=len(k['recs']);tb=m.bs();s.cur^=1;s.it+=1
  n0=R[s.dpreg];m.o+=5;dp=m.jne(n0,ONES);m.be('iter1',tb)
  if dp:
   t0=m.o
   tb=m.bs();hit=m.n(n0);s.cut0=m.r(s.cut0,hit);s.it20=m.sl(s.it,20);s.it20p=m.ad(s.it20,1<<20);G=0;m.be('hb_init',tb)
   while True:
    tb=m.bs();low,l=s.find_lane(hit);hit=m.x(hit,low);wl=m.rl(M25,l);cf=m.jnz(m.a(wl,W))if G else False;m.be('hb_sel',tb)
    if cf:
     s.cap(13129,'g1')
     tb=m.bs();tc=m.o;tn=m.nest;s.hit_group(G,HL);m.nest=tn+(m.o-tc-2);G=0;m.be('hb_close',tb)
    tb=m.bs()
    if G:W=m.r(W,wl);G=m.r(G,low);HL=m.r(HL,m.sl(l,nl));nl=m.ad(nl,8)
    else:W=wl;G=low;HL=l;nl=8
    assert not s.check or nl<=80;more=m.jnz(hit);m.be('hb_add',tb)
    if not more:break
   s.cap(13129,'g1')
   tb=m.bs();tc=m.o;tn=m.nest;s.hit_group(G,HL);m.nest=tn+(m.o-tc-2);m.be('hb_last',tb)
   tb=m.bs();base=s.cur*32;nd=R[s.dpreg]
   if s.check:assert nd==n0
   for j in range(20,32):R[base+j]=m.a(R[base+j],nd)
   m.be('hb_clr',tb)
   full=m.jge(s.qn,P.QFULL);m.blkmax('iter1h',8)
   m.tick('hits',t0)
   if full:s.stage2()
  tb=m.bs();cs=m.jz(m.a(s.it,P.CUTP-1));m.be('iter1c',tb)
  if cs:s.cap(76864,'g2');s.cutscan()
 def wr(s,word,w,w1,word1,rsh,st2,sh,d):
  m=s.m;m.st(s.tab,word,m.x(w,m.sl(d,sh)))
  if m.jnz(st2):m.st(s.tab,word1,m.x(w1,m.sr(d,rsh)))
 def hit_group(s,G,HL):
  m=s.m;base=s.cur*32;m.o+=2;tg=m.bs()
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
  m=s.m;ta=m.bs()
  bk=m.sr(m.ad(m.ad(r,m.sl(r,5)),m.sl(r,6)),15);pos=m.ad(m.sl(bk,5),m.sl(bk,3))
  word=m.sr(pos,8);sh=m.a(pos,255);chk=m.a(r,511)
  w=m.ld(s.tab,word);v=m.sr(w,sh);w1=0;word1=0;rsh=0;st2=m.jge(sh,217)
  if st2:word1=m.ad(word,1);rsh=m.sb(256,sh);w1=m.ld(s.tab,word1);v=m.r(v,m.sl(w1,rsh))
  e=m.a(v,M40)
  lw=m.ld(s.LA,l);en0=m.ad(lw,s.it20p)
  if s.check:
   ln=s.it-((lw^NM20)>>20)
   assert 0<=ln<2048 and pos==40*(r*97>>15)and en0==lw&M20|ln<<20
  if m.jeq(m.sr(e,31),chk)and m.jnz(e0:=m.a(e,M31)):
   m.be('hit_a',ta);tb=m.bs()
   ln20=m.a(en0,NM20)
   if m.jge(e0,ln20):
    pk=m.r(m.sl(m.sb(e0,ln20),20),m.a(lw,M20))
   else:
    s.wr(word,w,w1,word1,rsh,st2,sh,m.x(e0,en0))
    pk=m.r(m.sl(m.sb(en0,m.a(e0,NM20)),20),m.a(e0,M20))
   s.qpush(pk)
   m.be('hit_m',tb)
  else:
   m.be('hit_a',ta);tb=m.bs()
   if m.jge(m.a(en0,ML),m.a(e,ML)):
    s.wr(word,w,w1,word1,rsh,st2,sh,m.x(e,m.r(en0,m.sl(chk,31))))
   m.be('hit_n',tb)
  td=m.bs()
  nid=s.idc
  if m.jge(nid,1<<20):s.lim=0;m.o+=1;m.be('hit_c',td);return
  s.idc=m.ad(nid,1)
  m.st(s.LA,l,m.sb(nid,s.it20p))
  zi=m.rl(nid,l);s.ZI=m.r(s.ZI,zi)if s.ZI else zi
  m.be('hit_c',td)
 def cut_lane(s,base,l,it20,cthr):
  m=s.m;tl=m.bs();m.o+=2
  lw=m.ld(s.LA,l)
  if m.jge(lw,cthr):
   if not m.jge(s.idc,1<<20):
    low=m.sl(1,l);nid=s.idc;s.idc=m.ad(nid,1)
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
   s.insert_lane(base,s.QG,None,s.QZ);s.QW=wl;s.QZ=z;s.QG=low
  else:
   s.QW=m.r(s.QW,wl);s.QZ=m.r(s.QZ,z);s.QG=m.r(s.QG,low)

  m.be('qins',bb,True)
 def qflush(s,base):
  m=s.m;bb=m.bs();m.o+=2
  if m.jnz(s.QG):
   s.insert_lane(base,s.QG,None,s.QZ);s.QG=0;m.o+=1
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
  m=s.m;R=s.R;t0=m.o
  sv=s.cur
  tb=m.bs()
  if m.jz(s.s2 is not None):
   m.be('s2_in',tb);s.bank(sv*32,None)
   ti=m.bs();cur=0;it2=0;bact=0;live=0;occ=0;nf=128
   rec=[0]*32;wh=[0]*(P.WHEEL//16);fs=[sum(32*i+j<<8*j for j in range(32))for i in range(4)];m.o+=22;m.be('s2_init',ti)
  else:
   cur,it2,bact,live,occ,nf,rec,wh,fs=s.s2;m.o+=18;m.be('s2_in',tb);s.bank(sv*32,cur*32)
  tq=m.bs();qi=0;qn=s.qn;pw=0;s.QW=0;s.QZ=0;s.QG=0;m.o+=4;m.be('s2_q',tq)
  while True:
   s.cap(15424,'g3')
   tw=m.bs();wi=m.sr(m.a(it2,P.WHEEL-1),4);sh=m.sl(it2,4)
   w=m.ld(wh,wi);head=m.a(m.rr(w,sh),0xFFFF)
   has_cb=m.jnz(head)
   if has_cb:m.st(wh,wi,m.x(w,m.rl(head,sh)))
   m.be('wheel_check',tw)
   if has_cb:
    while True:
     s.cap(12352,'g4')
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
      occ=m.r(m.x(occ,lowq),m.r(lowr,lowrp));bact=m.r(bact,lowr)
      m.be('cb_move',tl)
     else:
      m.be('cb_a',tl);tl=m.bs()
      occ=m.x(occ,lowq);live=m.sb(live,1)
      m.be('cb_drop',tl)
     if not m.jnz(head):break
   while True:
    s.cap(15424,'g5')
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
      m.be('l_try',tl);break
     tl=m.bs();iB=m.a(pw,M20);iA=m.a(m.sr(pw,20),M20);d=m.sr(pw,40)
     s.qins(cur*32,lowq,q,iA);occ=m.r(occ,lowq)
     s.link(rec,wh,it2,d,q,iB)
     m.be('l_single',tl)
    else:
     if not m.jge(nf,P.KRES):
      m.be('l_try',tl);break
     m.be('l_try',tl);tl=m.bs();iB=m.a(pw,M20);iA=m.a(m.sr(pw,20),M20);d=m.sr(pw,40)
     nf,lowq,q=s.fpop(fs,nf)
     lowqh=m.sl(lowq,128)
     s.qins(cur*32,lowq,q,iA);occ=m.r(occ,m.r(lowq,lowqh))
     if m.jz(d):
      s.qins(cur*32,lowqh,m.ad(q,128),iB);bact=m.r(bact,lowq)
     else:
      s.link(rec,wh,it2,d,q,m.r(iB,1<<20))
     m.be('l_pair',tl)
    tl=m.bs();live=m.ad(live,1);pw=0;m.o+=1;m.be('l_end',tl)
   tb=m.bs();s.qflush(cur*32);m.be('s2_fl',tb)
   if m.jz(live):break
   tb=m.bs();sp=m.jz(pw)and m.jz(final);m.be('s2_susp',tb)
   if sp:break
   assert not s.check or s.QG==0
   k=s.ks[cur];k['fn'](R);m.o+=len(k['recs']);ts=m.bs();cur^=1;it2+=1;m.o+=2;m.be('s2_step',ts)
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
     s.cap(13376,'g6')
     tm=m.bs()
     low,l=s.find_lane(full,6);full=m.x(full,low)
     low2=m.r(low,m.sl(low,128))
     if ppd is None:ppd=m.x(pp,m.rl(pp,128))
     if s.check:assert pp==R[(cur^1)*32]
     if m.jnz(m.a(ppd,low)):

      Z=s.extract((cur^1)*32,0,31,low2,l,'extract32x2')
      a=m.a(Z,M32);b=m.sr(Z,128)
      tcl=m.o;r_cl=s.claw(a,b);m.nest+=m.o-tcl
      if r_cl:s.success=True

     bact=m.x(bact,low);occ=m.x(occ,low2);live=m.sb(live,1)
     fi=m.sr(nf,5);fsh=m.sl(nf,3);fw=m.ld(fs,fi);m.st(fs,fi,m.r(m.a(fw,m.rl(ONES^255,fsh)),m.rl(l,fsh)));nf=m.ad(nf,1)
     m.be('merge',tm)
  s.cap(13376,'g7')
  if s.check:assert pw==0
  tb=m.bs()
  if m.jnz(live):
   s.s2=cur,it2,bact,live,occ,nf,rec,wh,fs;m.o+=18;m.be('s2_out',tb);s.bank(cur*32,sv*32)
  else:
   m.be('s2_out',tb);s.s2=None;s.bank(None,sv*32)
   if s.check:assert not any(wh)
  s.qn=0;m.tick('stage2',t0)
 def cap(s,R,k=''):
  m=s.m;w=s.wmax
  if w:
   m.o+=2
   if s.gR is not None:assert m.o-s.gl<=s.gR
   s.gl=m.o;s.gR=R;s.gk=k;s.st['gops']=s.st.get('gops',0)+2
  if w and m.o+R>w:s.st['k4_capped']=1;raise CapStop
 def run_window(s,cv=None,iters=None):
  s.success=False;s.window_setup(cv);s.gR=None
  if s.skip:return s.st
  s.lim=iters if iters else s.win//256
  try:
   while s.it<s.lim:
    if s.it%16==0:s.cap(15424,'g8')
    s.iter1()
    if s.success:break
   m=s.m;tb=m.bs();go=(m.jnz(s.qn)or m.jnz(s.s2 is not None))and m.jz(s.success);m.be('w_end',tb);m.blkmax('w_end',6)
   if go:s.cap(15424,'g9');s.stage2(final=1)
   if s.win>1<<21 and not s.success:
    s.lim=s.lim*5//4
    while s.it<s.lim and not s.success:
     if s.it%16==0:s.cap(15424,'g8')
     s.iter1()
    go=(m.jnz(s.qn)or m.jnz(s.s2 is not None))and m.jz(s.success)
    if go:s.cap(15424,'g9');s.stage2(final=1)
   s.cap(11328,'g10')
  except CapStop:pass
  assert s.wmax is None or s.m.o<=s.wmax,'cap'
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
  assert out=={"advice_slice_hits":1,"advice_w16_is_g":1,"advice_w17":1,"classes":936,"fibre":1019863230,"fibre_dfs_ops":1944,"fibre_shift":97447904,"g16_fibre_size":2,"g17_fibre_size":1,"groups":240,"ops_per_cand":411,"sample_trail":240,"sample_valid":240,"sample_w16_one_value":1,"sample_w9_shifted":240,"sfs_collision":1}
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
K4_NG,K4_NC,K4_NB,K4_IND=240,936,430,50
FIB=0x3cc9e0be;K4_CUBE=0xf74400da;K4_E11A=BA[7]+K4_C11&M
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
K4_S=[]
for gi,g in enumerate(K4_Q):
 ff=g[2][0][1]==256
 for bi,(PP,n) in enumerate(g[2]):
  if not ff or n!=256:
   for j in range(n):K4_S.append((gi,sum((PP[b]>>j&1)<<b for b in range(18))))
K4_P=[]
for q in range(0,len(K4_S),256):
 Z=K4_S[q:q+256];PP=[sum((x>>b&1)<<j for j,(g,x)in enumerate(Z))for b in range(18)];GG=[]
 for j,(g,x)in enumerate(Z):
  if not GG or GG[-1][1]!=g:GG.append([j+1,g])
  else:GG[-1][0]=j+1
 K4_P.append((PP,len(Z),tuple(map(tuple,GG))))
K4_Q=[(k,c,tuple(Z for Z in B if Z[1]==256)if B[0][1]==256 else(),s)for k,c,B,s in K4_Q];assert sum(bool(g[2])for g in K4_Q)==140 and len(K4_P)==51 and sum(len(g[2])for g in K4_Q)==280
K4_KQ=[(g[0]+W17PUB)&M for g in K4_Q];_k4c.o+=5*len(K4_Q)
def _k4loc(gi):
 x=K4_Q[gi][3][0]&0x3ffff
 for bi,(P,n)in enumerate(K4_Q[gi][2]):
  for j in range(n):
   if x==sum((P[b]>>j&1)<<b for b in range(18)):return 0,bi,j
 for pi,(P,n,G)in enumerate(K4_P):
  l=0
  for e,g in G:
   if g==gi:
    for j in range(l,e):
     if x==sum((P[b]>>j&1)<<b for b in range(18)):return 1,pi,j
   l=e
 raise AssertionError('k4 loc')
class _MS:
 __slots__=('r','seg','buf','n')
 def __init__(s,r=None,seg=None):s.r=r;s.seg=seg;s.buf=[None]*32;s.n=0
def _k4rb(m,G,tg,u,w,fold=False):
 S=[];l=0
 for e,g in G:
  base=K4_KQ[g] if fold else m.ad(K4_Q[g][0],tg)
  m.o+=10;r=m.a(m.sb(m.sb(base,u),w),M32);q=((1<<(e-l))-1)<<l;m.o+=4
  S.append((q,r))
  l=e
 return S
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
 s.cap(K4_PASS,'g11');s.k4q(a0,u)
 if s.check or s.measure:
  m=s.m;o=m.o;c=dict(m.cat);z=dict(s.st)
  if s.check and s.st['f9']<2:
   _w=s.wmax;s.wmax=None
   for g in K4_Q:
    n=s.st.get('k4_w17a',0);q=s.st.get('k4s',0);s.k4q(a0,u,(g[0],expand(k4_words(s.cv,a0,a1,*g[3]),18)[17]));q=s.st['k4s']-q
    assert s.st['k4_w17a']>n and q==1,'k4 plant'
   s.st=z;s.wmax=_w
  s.__dict__.setdefault('k4D',[]).append((a0,u));m.o=o;m.cat=c
def k4q(s,a0,u,T=None):
 m=s.m;cv=s.cv;t0=m.o;m.o+=624;a0,a1,u,w=s.k4x((a0,u));tg=T[1]if T else W17PUB
 WB=[m.sb(0,m.a(m.sr(w,i),1))for i in range(18)]
 J=[]
 if T:
  gi=next(i for i,g in enumerate(K4_Q)if g[0]==T[0]);z=_k4loc(gi)
  if z[0]==0:
   _,bi,j=z;P,n=K4_Q[gi][2][bi];m.o+=10;r=m.a(m.sb(m.sb(m.ad(T[0],tg),u),w),M32);J=[(P,1<<j,_MS(r=r),gi,r)]
  else:
   _,pi,j=z;P,n,G=K4_P[pi];S=_k4rb(m,G,tg,u,w);r=K4_Q[gi][0]+tg-u-w&M;m.o+=16;J=[(P,1<<j,_MS(seg=S),gi,r)]
 else:
  for gi,g in enumerate(K4_Q):
   Bs=g[2]
   if not Bs:continue
   kq=K4_KQ[gi];m.o+=10;r=m.a(m.sb(m.sb(kq,u),w),M32);MS=_MS(r=r)
   J += [(P,(1<<n)-1,MS,gi,r)for P,n in Bs]
  for P,n,G in K4_P:m.o+=10;J.append((P,(1<<n)-1,_MS(seg=_k4rb(m,G,tg,u,w,True)),G,None))
 for P,LM,MS,G,r in J:
   y=[];c=k=acc=None;nb=MS.n;buf=MS.buf
   for i in range(18):
    p=m.ld(P,i);t=m.x(p,WB[i]);y.append(t if c is None else m.x(t,c))
    if i<17:c=m.a(p,WB[i])if c is None else m.r(m.a(p,WB[i]),m.a(t,c))
   for i in range(32):
    if i>=nb:
     if MS.seg is None:
      for q in range(nb,i+1):buf[q]=m.sb(0,m.a(m.sr(MS.r,q),1))
     else:
      for q in range(nb,i+1):
       v=0
       for qq,rr in MS.seg:m.o+=3;v|=qq if rr>>q&1 else 0
       buf[q]=v
     nb=i+1
    t=m.x(y[i],buf[i]);v=t if k is None else m.x(t,k)
    if i<31:k=m.a(y[i],buf[i])if k is None else m.r(m.a(y[i],buf[i]),m.a(t,k))
    if i<14:y.append(m.x(m.x(v,y[i+7]),y[i+3]))
    else:
     e=m.x(y[(i+7)%32],y[i-14]);e=m.x(e,y[i+3])if i<29 else e;e=m.x(v,e);acc=e if acc is None else m.r(acc,e)
    if not T and i>=22 and not m.jnz(m.a(m.n(acc),LM)):break
   MS.n=nb
   m.o+=9;h=m.a(m.n(acc),LM);s.st['k4q']=s.st.get('k4q',0)+LM.bit_count()
   while m.jnz(h):
    s.cap(145000,'g13')
    lo=m.a(h,m.sb(0,h));h=m.x(h,lo);j=lo.bit_length()-1
    if not isinstance(G,int):
     for e,gi in G:
      m.o+=3
      if j<e:break
     r=K4_Q[gi][0]+tg-u-w&M;m.o+=6
    else:gi=G
    cs=K4_Q[gi][1];m.o+=706;x=sum((q>>j&1)<<b for b,q in enumerate(y));s.st['k4s']=s.st.get('k4s',0)+1
    assert s0(x)==x+r&M;x=x-w&M;w9=BW[9]+BA[5]+K4_HD-a1&M
    for a3 in cs:
     s.cap(145000,'g14')
     m.o+=563;W=k4_words(cv,a0,a1,x,a3)
     if W[9]!=w9 or expand(W,18)[17]!=tg or not inF(W[10],K4_DL[10],K4_T10):continue
     s.st['k4_w17a']=s.st.get('k4_w17a',0)+1
     if T:break
     for b in cs:
      s.cap(151000,'g15')
      m.o+=560;W1m=k4_words(cv,a0,a1,x,b)
      if W1m[9]!=w9 or expand(W1m,18)[17]!=W17PUB or s0(W1m[8]+D8&M)-s0(W1m[8])&M!=T8:continue
      s.st['k4_w17']=s.st.get('k4_w17',0)+1;m.o+=2*2812;W2m=k4_second(W1m)
      if W1m!=W2m and compress(cv,W1m)==compress(cv,W2m):
       s.st['collisions']=s.st.get('collisions',0)+1;s.success=True
       if getattr(s,'m0',None)is not None:s.messages=getattr(s,'messages',[])+[(list(s.m0)+list(W1m),list(s.m0)+list(W2m))]
     break
 if s.check and not T:s.st['k4_old_fixed_shadow']=s.st.get('k4_old_fixed_shadow',0)+200423;s.st['k4_new_actual']=s.st.get('k4_new_actual',0)+m.o-t0
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
K4_EN_LB=13951.897494770211
R_LB=0.945854198767
K4_DIV=332634742808497727891862043090867/434810569403877151706270838816768000
K4_OPS_PER_CLAW=10061
def k4_budget(cap=WMAX_CAP,r=R_LB):
 lam=math.nextafter(-math.log(0.61),math.inf)/(1-K4_DIV);B=lam/(57003.18*K4_EN_LB*2**-32*2**-74.4594)
 bw=math.ceil(B/r);return bw,int(bw*(cap+6))
K4_WIN_EXP={14672896933643966474:(63,1,0,84600,0,0,142919,5889100),15921217793420643850:(14,0,0,0,0,0,0,3190746),17552297034189817508:(22,0,0,0,0,0,0,7447156),1866586107145425828:(16,0,0,0,0,0,0,3718932)}
K4_PASS=200423;K4_PASS_COMPACT=733+110*140+403*280+114*196+403*51;K4_MEM=32*(table_words()+P.QCAP//4+1+18*331+512)+334813;assert table_words()==15520 and K4_PASS_COMPACT==171870 and K4_PASS_COMPACT<=K4_PASS;assert K4_OPS_PER_CLAW>=573465000/57003.18 and K4_SETUP==1120815490 and 93.6164-math.log2(k4_budget()[1]/2812+K4_SETUP/2812+2**43)>=0 and K4_MEM==1043645 and K4_MEM+4931==1048576,'k4 opc'
def _xd(w):
 w[1]=W17PUB-s1(w[15])-w[10]-s0(w[2])&M;w[0]=G16-s1(w[14])-w[9]-s0(w[1])&M;c=invert_downward(BA[14:20],BE[14:20],w)[0];A,E,_=traj(c,w,21);B,F,_=traj(c,k4_second(w),21);f=lambda t:A[t]^B[t]==BA[t]^CA[t]and E[t]^F[t]==BE[t]^CE[t]
 return f(22)*(1+f(23))
def _stamp(A,SL):
 c=A.cap;e=A.k4_eval;r=[0]
 def cp(R,k=''):x=c(R,k);r[0]=max(r[0],A.m.o+R);return x
 def ev(a0,a1,u):x=e(a0,a1,u);SL.append((a0,u,r[0]));return x
 A.cap=cp;A.k4_eval=ev

def _k4e(i,sd):
 if i>3:return None
 A=Attack(win=(1<<20 if i<1 else 1<<19),seed=sd,check=True,k4=True,screen=0);A.k4_ib=7
 SL=[]
 if i==1:_stamp(A,SL)


 A.run_window();st=A.st
 t=st["claws_distinct"],st["f9"],0,st.get("k4q",0),st.get("k4s",0),st.get("k4_w17",0),A.m.cat.get("k4",0),A.m.o
 if sd in K4_WIN_EXP:assert t==K4_WIN_EXP[sd],('k4 win',sd,t)
 if i<1:O=Attack(win=1<<16,seed=sd,check=True,screen=0);O.run_window();B=Attack(win=1<<16,seed=sd,check=True,k4=True,screen=0);B.run_window();o=O.st;b=B.st;assert(o['claws_distinct'],o['f9'],o['f8'],O.m.o)==(b['claws_distinct'],b['f9'],b['f8'],B.m.o-B.m.cat.get('k4',0)-b.get('k4q',0)//31200)
 if i==1:
  stamps=sorted(x[2]for x in SL);W=stamps[len(stamps)//2]if stamps else A.m.o//2
  C=Attack(win=1<<20,seed=sd,k4=True,screen=0,check=False,wmax=W);CL=[]
  _ck=C.k4_eval
  def _ck4(a0,a1,u,_ck=_ck,CL=CL):
   r=_ck(a0,a1,u);CL.append((a0,u));return r
  C.k4_eval=_ck4;C.run_window()
  if C.st.get('k4_capped'):assert C.st.get('k4_capped')and C.wmax-65536<C.m.o<=C.wmax,'cap'
  else:assert C.m.o<=C.wmax,'cap'
  assert CL==[(a,u)for a,u,st in SL if st<=W],'stamp exact'
 I=[(len(r[1]),len(r[3]))for r in getattr(A,'k4i',{}).values()]
 v=sum(d for d,k in I),sum(k for d,k in I),round(sum((k-d/128)**2/(d/128*127/128)for d,k in I),4),len(I)
 E=((57936,438,0.4763,1),(0,0,0,0),(0,0,0,0),(0,0,0,0));R=_k4e.__dict__.setdefault('R',[]);R+=[v];d,q,x=[sum(e[j]for e in R)for j in range(3)]
 assert v==E[i],('k4 diag',v)
 if i==0:
  Z=Attack(win=1<<16,seed=sd,check=True,k4=True,screen=1);Z.run_window();L=Z.scr
  assert not Z.skip and k4_scr(Z.cv)<=5 and L and all(c==69+3*(S>5)for S,c in L)and Z.st.get('ddraws',0)==sum(S>5 for S,c in L),('k4 screen',len(L))
 if i!=1:
  c=K4_Q[sd%K4_NG][1];o=_K4C();F,V=_k4fe([_k4class(a)for a in c],o);N=[(z,c[l])for l in range(len(c))for z in _k4lf(F,V,l,32,o)];r=random.Random(sd);g=r.getrandbits;C=A.cv;X=_k4e.__dict__.setdefault('X',[0]*3);x=X[:]
  for a0,u in getattr(A,'k4D',[]):
   a1=recover_a1(C,a0,u)
   for _ in range(1000):
    w=k4_words(C,a0,a1,*r.choice(N))
    if inF(w[8],D8,T8):
     X[0]+=1;X[1]+=_xd(w)>0
     while 1:
      a2,a3=r.choice(N);W9=W8=1
      while not inF(W9,D9,T9):W9=g(32)
      while not inF(W8,D8,T8):W8=g(32)
      b1=k4_words(C,0,0,a2,a3)[9]-W9&M;k=k4_words(C,0,b1,a2,a3)[8];W8^=k-W8&1;y=k4_words(C,k-W8&M,b1,a2,a3)
      if y[1]&1:break
     X[2]+=_xd(y)>0
  if i==3:assert(X[1]-X[2])**2<=4.5*X[0]
 return{"distinct_claws":t[0],"passed_f9":t[1],"k4_lanes":t[3],"k4_surv":t[4],"k4_w17":t[5],"k4_ops":t[6],"ops":t[7],"ops_off":t[7]-t[6],"k4_setup":K4_SETUP,"ind_D":v[0],"ind_K":v[1],"ind_x2":v[2],"ind_claws":v[3],**({"stamp_claws":len(SL),"stamp_kept":len(CL),"stamp_W":W}if i==1 else{"xr_n":X[0]-x[0],"xr18":X[1]-x[1],"xv18":X[2]-x[2]})}
def serve():
 req=json.load(sys.stdin)
 eid=req["experiment_id"]
 if eid[:9]=="r39-mate-":return exec(zlib.decompress(base64.b85decode(R39M)),{"L":sys.modules[__name__],"Q_":req})
 if eid not in GEN_EXPERIMENTS:raise SystemExit("unknown experiment id")
 fn=_h8 if eid==GEN_EXPERIMENTS[0]else _k4e
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
   A=Attack(win=P.WIN,seed=None if seed is None else seed*1000+w,check=False,k4=True,wmax=WMAX_CAP);assert A.k4_max is None and getattr(A,'k4_maxblk',None)is None;A.measure=False;A.run_window();assert A.m.o<=WMAX_CAP;w+=1;work+=A.m.o+6
   for M1,M2 in getattr(A,"messages",[]):
    print("collision","".join("%08x"%x for x in M1),"".join("%08x"%x for x in M2),flush=True);return
  print("no collision %d %d %d %d"%(w,work,BW_,WB_),flush=True);sys.exit(1)
 serve()
H8T=[2,3]
H8_EXP={2600209493401801829:(51,0,0,0,0,5908541),10907755097612878284:(54,1,46656,46656,2176782336,5718047)}
def _h8w(sd):
 A=Attack(win=1<<20,seed=sd,k4=True);A.k4_ib=7;S=[];_stamp(A,S);A.run_window();I=getattr(A,'k4i',{});N=[(I[a,u][0]if(a,u)in I else 0,w)for a,u,w in S]
 v=A.st['claws_distinct'],len(S),sum(n for n,w in N),sum(n for n,w in N if w<=7714620),sum(n*n for n,w in N),A.m.o;assert sd not in H8_EXP or v==H8_EXP[sd],('h8 exact',sd,v);return v
def _h8(i,sd):
 o=_e1(i,sd)
 if i not in H8T:return o
 v=_h8w(sd);R=_h8.__dict__.setdefault('R',[]);R+=[v]
 if len(R)==len(H8T):
  C,F,N=[sum(x[j]for x in R)for j in range(3)];n=len(R);F=max(F,1)
  z=(F-0.0159143*C)/(0.01829*C)**.5,(N/F-39790.0)/(525074370.0/F+1202.0)**.5
  assert max(map(abs,z))<=3,('h8 band',z,R)
 o.update(zip(('h8_C','h8_F','h8_N4','h8_Y4','h8_Q4','h8_ops'),v));return o
R39M=b'c$}4cZF|}{v+#F*g`2%gq#&py+hF4;XDK1=Zj;<;({0oGa#+8SP+o%#*e&gEf3A@XIB9p!dD5$vG}36K(P(Bg62r-Swn()kPso>KHYE#x8qFqT;-~i{Nf*m7ty~D24T`@?IQEl7yI!{|S`-hoet$R}ru{xzlXKjzXxh4QF3z2GV<Lvrv@uxBCjB5!;{>4#+(>6d!6FCaVVaKP1AKJ8&pYeJ>?b_-zvHQ~1R+|J5Vsd`x?D_ASiQhU>&8q~E~XJ$lg0FITdysqca6I^g$W14G(k<{Xx%u+)pcW{P_7wTlX%x3ice0OoA~&cH}NeL7?UNYO5B7}3zs{fXifZm2mZ+k-}uMJI>on8U^<kTtx8<hF<R~+fgvpSJuFX7SZlL9K4vDql_gu2^rG|_8OX2p$g7i+)@F5l%mH_Ga>6VqF+-K~GU_zGLu>MNkNXws@GX35JDz@x7c;abnOyjRKnP_uXmN6)bLeaa2s3B4Ooi)#Y}^mWu{LOrXJSyT51^vq&*$+pLTEf|1jDpHj;D9&J;HT{PfnWH8QhBTtfFbfn$4D}B7GO9K$#48L(EQ2U<rp9S1&4`#q}C7>|9fF%}7E?!o=ssH6@=L*Nl8_B#=v31-k0KMll(XonWB2I>5K+M_j$DUSQee;!ot0pd?#<HGoB{hWHi*)ljtx7ibEs$OJn+M$<?0dGSK8F<dEFz<^=7K>R4HO<%k~*-?g}Nk!9!11&!h*;Yuiil${Eue=d%xIpvcW4no~7usO9(B|53>dtprZQ)PvV#En+T6j3n{P7sgpFha@hjRTKW6!Hxz7x7#>3$IIaGIiwuqK9<8MHj`{gyo#SS_t-hGq~LwiZ#}GJ-***)$A8-L|xWA2y9a(A12<pk>>ZuLaB>m~m)ozR%*wh|GgVG9M39guTke%`XU{154M9sM(^LZZX|zwPJ0+?8s<Frq*hiW^)i4noaq@w!)T1O-i}NL(Mn1ZkoET*^JUyZ<^Xc<-l(>2j(E=ni&T==gmlqq9)a;WoeZ9Mza;@ns1x_z-F-)(56leKhg}n*`!prw8)~7ZPLL3-VgfpT)5ObvT82P466PJ%?2%tGL;SYP}-y{3L^s=4B|m-0Tljum5WcpMSd;VuAEN-VDs1E99`Uy({t=quKu_b-&nIvGrQGlT1`79tktGjtHu0i(2BoT-dp6oO)fguZ!Gz>1<k0{8Vm~Zx*QW^yIp4YnzT!3c4pg_-lb=iZby7$R{KCK4{8VE;7F(6E8U)gQK9}+$|x0rQd$&+pa+E6?E_KzTb2uAD!&J$!s)iza{0@avKi;)VGypj4+Pzh>imyO;UY>{i?Al4gjq7hM8UYBV36)$MLS5hFdcZ$ESX|b0iZ>g1hxog+lCft6*O$ZwjjFzSrWtm!z2vKrs_<B0HeU9*i#xH9*<E1I$$DJA`-MB*Lz4pSnqhcoWu)1ja3sZka|LA^&xg98xb5K+3bL_<@5kMs}hJU53m!J0MMdRXhk$3D{?_1T<N_PatM-_96R04LVQcx64vd2wL>W>D&;Or_liOC6n}TRy%J9E|AbSyJOh+qI7Qvw!c9GwdbknJmeUj+u!B8Tx3~B%8I>;lFh=2utjTl%%=jqA!z4v(TyU&JqbZww+*yi*p^xsc&OKa%wB^+jDk01)K&<IuP~BQbxZ%pxJrb^5F278EspmO8S=W-~ru>@nYk1yIV^Cw%Vu3pD(5v;}bInlC9oBRY*SfEZEP;fpgn7931{!{JhcKLqrge66i0iVWYYH98J}&+&vIG*Y66S$5!%lCD81EKc>yRG#sHAQ-nJ?lbk^F>#LRDXsczpS8hv%ZKmTwhNM)Iv93Rk4#)>*r5w(AV0xXTx^9nD54B&Sli$%;f15{b|W6TuX_f<3!*F4;9r1a+c7pwp9+09P3}3A2S34yT~|DPgjeHXNWZIXMZ3Q(TpXQ8mkgN3CSLiRwu6r;(Ng&jk1_0BDD^X*!%P<6X<B+%yVq!{PLqK+!LoPm_(@i6{%IQGhp)!e}-qQW;#)v@j9VMA_%*EY-qfYoX8laT4!V<^5tAZ++ynJ@=DDEzw-<`Kh>05q74H%qP=E7Q<&vri~nmITZ7?NE(^%wmp(GvbadsD$NUcUchsJI|b>fq_mDuviBIlft1abuwUx3loh2~QPJ}11+eASPS4#X>>t=uMLle*x-4efVj*_ZBu!94Qt9;gB#TMzlRTCakfWDFmg9AXBCQz}ZIOx0cZYSut7WlDuNjhA*f8DK+dPpeFH+qD0nSBU;O2YWyo6iiiA;HsO589L^)2CRiewg$F8<u+iA;HsDx_T0w-m1_%1cN^p2!p^?T{iNmmtMX6pKY(Uu3mtCmvx|y&!0j)!w)%C<PM50EpsRnAgKhLaG-e%&QlY$4Q(nW^3q<#L~?UGqT7?6qCp&5eaiqT7@l-rQ8fX5oeBEv(ytP&gu*39w0tcqByHbg3uoLq(D)u8s!SDz^_FGRG}6KwGb3ZAq$`!GLrAz@oETGK#0&~o)0=NyUlSmbh!fRN~<hp>)B{4L&f;j7DLcyw*%$`WC<v%9WeATY-(98t&Q3!syZ%L_ui_#Bb&$>Vf<v<-ifh42_jz`kwqJ(>jU|b5LAoDNi2DZ-9^ptc59eE6U@@UjT?^<LU(Ay$O4Wl0h|Qy(1?=-ha$(g%7lmpQlH6IBw$3=lYo<G04nqRk4wB~#Y(PqwkB~#{EXyllE=i)C3k*ei=RQ&6K2F2$>TB$vNg%qKTUi%P!nmF71#eZP|(CHCXk;=F0mb(;tY-)3nqXy0NJyWJ>?~n%+ywV*AIW%5C26!{AoX2^)nnGv|<JKSA5I&XCfN>i;4z@k7u(HEB2OT_Kwpct(p6sTw`*Z3<p~Dw8u;-YpEfW6c$=3&ZI($vqCsQM-;iOE>ps+Fdyl&LX{QbtS}#IvOUpjiu_D!Bwvy$)KQV!X|X*mK*$wBUhJoW!d`>@thb`A(AAjtNL@)mi?-4SwV=_IK(8admF9fCQw#}1`C6KyY+cx(v~CtQ2y$S9(mFHtHYlw#y<~$_ai@CxX(aU@nFb^&LOf3t<@$-HRExPTh6J&RNr$XDq)(!bP@Bt{^vJ3Qke*OG%b8{(J?6SI5s3_x{GUvo6NJz_2%T%XBG+sMrE5yy%PQJwk92RyX@^{1kPkg_+6&1=hkWRe(@rRY5JfR2L5RXkCXp|bACsO;S1O5AGU+IwN}`UM<urp$+dYNOiX~RoQ}>iXgjAJlJ8{QO_Yx4c4fe93WicaJ%t;<IlE<86J|mgWN$xX}`&_s|h`vgX|10=!Pp$b=3;opiKC!FVt7vz#StR2}&}qNqln2Tw&jd==4T$f-(pN7p@a99$iF0YsPJ6gIar{gcx;L_rgW{>3c5rn9r!YT)%G)@<J?({fgOHz9FFN@4LkDk=pWXWT?P({3x$oGiMe$Og?rH6stx%lf8p>mSi{iYB@|fM`F~=C!l63>(XtGU)YbcX#vMS1AcALpISd9S&u@NYWm$hrUk{c8uAA0lICigkU8^~5=cGoYognnVbDD&ASQ!O)}Rb>{}x|fOo@USM_WG&BgaYi2SE-sX;8#0g=_z|#s8?A%-ScZcD8D{NgtG(Oc<ngNHF=Xpi$;rr}l&x2_XbnX_UkQ}QtHNQ}Inj?S-b!iV70K5tlE*9J=PO+H)Ft<&KM%N1l=nZPq{o~~q`fwhBp$UZ1tQ~Yf5d`lqx8a3e~}`PwnX{wu-j#5$j~7l@AG*Ho^RpOC0mP&8@KJ%0E8~z)manz$=BlI(-Uw->tv*t?T&EW59Hzo&TvjAC%ya;{F6G{!D1~+XJ(Udirdl(EDFOT)4V9>P!^pGN<I1Q<T4Lm)g2tz;qc8`xLtBXul~3MKWfLLq|!ZmCF4lQWSm$Sf<=f^!-71gr95jR#w}uC2mv8(Hc1mh_y-w;K@i~zVo!?UlTdEvc161qZoz)<=<>=LCBpTbF&DH!o$HU{+xPuw9|a{qV9&`k5Z$v^puCf{xc=Bk;xvi}{&Jk6b8@{#=NLQl*=(%h(=wDgB=g6?nk#hx-R}owapsRL4)n4+-p_}}$2!LwDNNcZ*;b6>DT0RbL|JSCC~w`0%h@z0ql7?O(X=tI3Al)9jAwUzkNg5%UL8$?qjQYwmuGGYL%-ttDU@{NWij|z0HzC99&q2GD)*!DoP>*Tj;`DoV)q_)wkytIgFy)5if<>8a2WlSxZ*n@xPn2Cxm>&9^b8Hjdx%7AFAoxm&>GCT41`ESzLtRvA>K=zNjwSSMS>=NG9p9r9tN%SkdrI}2&1XEIk;{xpW&WNvJ7y$w11&o(KJAVd>y*PRro4As1UUMWQPxiQ-2J;L9!;9MKW8(@W9UhWWY&6S0s6C$l(jO3~RVl*skoopZICIK*^dMjOGWpova(9xj;dPPS0J-lXm*_+_gPSz--Dh;S*uLe1~DPjRK2|0-KBipgNjYv}`R+?Mfo7q#l=H0&aMFWx@^Y<iBW`|Dqvu=~|x1EGJvLwkI;%$t473R&5kmU^{bJgEG4|3T$aw<h=-qB#q*jhPTl(#AR%jo3J50N8YlK`)$+spPNDm>m})u)1qzuZ{7CD8F@usZ=3#Ww@<js4N#vTQN=MiVJjp(Oo)%jj0`UpKp9|EIfyWVVcnjS*$U-byu5^$@9^?Rcq1_i)Xq(rxL1AzuA#eI6j#yU_705qNYe70lnZI=rKzu?U=xCshifO0^m}qg1|)`P011dMR0&13l;P?`0SQW3E#-=I%EW6)u!n2t)h+5((b?@QMKCWD>;S<|6}{Yaf#Az(R}y?pUXe4>Bd4TGUXqSbC3IR4l)y5<t)VE~4CLQ}V-?)K#2Xaeb|K7mdx|$GzU|=+8r+`Y4Z6F1g*WK__BB>ViB-H94sw)`wMEu)b7nG5CgWd9Zr5A6UE4pevrd>v>I}EHs|W6hn|kUPqSmcmtT(8q-EvERWi5aZYkE#cd|MP|wPtuvtuEZX;qOkbXcYfTqo2dvFg`g%2o%e+nt-UXSB?~KqfaUeA!6{EAt??-n$~-QS~tA93RMGgU4^Ov84?w$2IM+~s_W}*s5)E;7sA2Nxgt@Qk?Fbt7z$ls1H1?DeSqX~JX(ly`Je8=*76z*6V!33S7rE!*U;K!kd*>3n$FhKzCTUY@uKj=3b(-NWl#MimwEr<6_lKrUgoAXL!N8OE~$z~6|<qcdBOeV&QQqvWpZ)jS{{6Dh-$eMB3*l7E!RRYta90XO)g)O^E1IIF(?7osM5Q+>R*e4gM*6Q)GeZOY7uU=IAOfSZDQ-30g!I$P1a~KuJh)`XzCkAEy6f7V}vnYv0DaUgSu;)CSY3zv74<{3EQByPB%uAZ5Y!D1NV*_gi)(vo0JosS(ND1ri5|RY7(2X61Lgm2ICvU(l?CTK!7l~2V=Bio6I0OYXWu?uq|d1+p?`aw$U_fW^N4K*f3hqmMO2;rr9JqX9nRmfYkUYZ}Jj)tI4>zF-&tKiP9}`qhdF$mKr*@Da@!v0i79U3Eg7MvNuKx#!d-iOwF9Z%$W^*vkA9tV5g<)#5S2;nmMOU-r5-4+Azus;!N?aX>y|L)F3)HVeGAD6R?dvwr(1n>l>p9GpB^<CeVc*Dz>S^;x-x4X|ZM&vEj2Hxo#OPa|8b+*X6naA>cY7a)S|WThK8z48Sgp+%T!dtc_t<8$}cTQ($hzZnl6yI$%pduuM+umR(wL!?G-HZ472@>}G)o%hs&eO<)>pHi=GQKHLCd)9uoVnJw1TTS`>r-7AO;Or2G1g9A2)Yg!XXH}w{=ZN0=aliC(wx2$5pV9IjQVA>Q0P6@YQ+T7+XVp(ztwu0WGTsI170lFL{g~0g&Hky376le2(6o<1YM(Nh!+#V-}WITO*3P>ACx){z;@jPHWoW=>lQlUuSm)s{LOvHFvJRdmNzy&RI>K-g~yPo>Pas4^v(ZO>xtTF5fq#i`<pIwZSEiO609vO^heu~B%6KHpzVDc0pe1!1$+}gXj66GmMErTm>PkY^SQEwRy(<oWieliLBN$RHwdWhn1EZ_tp!)VMBa84+qY)a+Idvy*f5EK|L-i$Tg$pkU38zu%<q0p(ln=4?`);ch&qMb8~T)t$MJe@JibEc9?@8$|uG(Sn=MJh=PPMh-d?gt49nf0P+ntHRIEGGzVab4=|yxQK)Rb%CkmvUKNpy|=&)zLY#j(`lt$FxBy)hpV=csLa<;thIq1lPg%2*KU(3&rir?(3t=mq+Jk>Z<#vjy>pLb|>8Zv8)tHfxaP@*asRgMgZU!(~6cv5+<>dhee8@7CqEuQ+#y9_s?_`4w}{(uy7m(drV1BqSSe#X~N@{Bh~YZeb4f`a?*!Usv*qo<Pc;}vpXTH_V`bRl);c@ce^1;Ia7V8Aw8lbd$n!*r{U=h%jEwswlo|k!c|MCd+z8TmQY?r?CrO7-wVkAT<8T0IYn5%U-z-YDA;%+g<A?#!H&le+qM;;qCHUdL`;kZJ(444{~yvap-e3UW%$L^Ng~RAAqA8@kpXDE6@g+3B^FawUVq9Sb9g(0(taDNN1k8D!+->S5;qNU?<e<A^cM?1uUv}DcTVSq^lqL;ov_pSM0%f|2A!~T+7T}5+(-xNw)07*q*s)Cs{GSw7JHSi0*285wN$u;YDA5|G7DW59ESh-@e0qyv%#xY{@eZS@3p^zzt8{t@sNBPSpOM_qwX{Qj`QE<&6jWAY|P0$y*~Lfx}Q$J{x)BBe_XZlS9jF_TPFMd@sIbslm7PJ*MD1m{Lkvgt9Pg8e?LqA9$4X*@W;#L%eMx8<3HS1gZxW(nSMFi{C@TB-EZji?Qh5Lt=3;}zK;I;*Yp0-2YPINyb1r?yX;yYf1jAE)9+W`dUt>I{yI)y#`Nu<Rrc-vKaBs+*Q1+y^7gcrKEt0scRqwypY$0&pUy90rhgf?KL7V7Sl`_}Gd6eK;CP%ZpN%Ke%&uA4vriAx<JY(8$!VXzzy9<(irybDzFz(DS(s-1<M+|U$w|jB{xU@E?$dbUtWE>#!{+nRnKl029l!ozvcFF(bmN?NkN?2+>(-n4-@#0*H!uHud-wG$n|-&MHQJip&Nrj9x7tLjG>#^<@Y&}-FJ6XpKDqw<_wzUNWOIQR;n|;mo%SF8=l3)IX|?YE-hBRQeQNiu|Ni}noqhPyxjc6cF?L?bCw=9&x?kO4TRvVn42E}y_{e&C%Av#nH?4S5GFqb$-p8tkI`W;4e5NB`>A2J*M?N{~+_+Yoart5=bX#p*zE4r_@_IKe<MLqkQAJmOK31uxC=f6@w%VzHS2b`V+C99f|I@>p>V*T(cnlA4yjm(xS8)H>PKBzFCo>6#Cq5#r%QM&hT~Pg>-UZ3S79bW|R6XMvL?~46ceV$b5T5Q}C*Kv_dF^5Q`jb37K0A@iA`bj$zp2Ti42-4RnfW$HGMDXOMGij`ryV!-wr8JoH^j@zTZqQ>!};zw_vGyn4E^mc0t!XEeVNh^=Mqr4>5IbwkFAzYjh4+V%huz#WjC!TX!%^{gH~V;Xv+vJ)6(@p%cOA>SS&DDEAj^cH3o4^IWq^8>4VTPf-r7|+%%(sAGLyzMFSq`Hnj{rwDs8F1|0-`s};m8Gxmdl(KIc;#UmrsEow6}YVwdWY7GWdk3zp`w<r%;7>A}E@x#jJzHkvZo*Lsi(J0X<CK_U9i)hSfl^_-+8mG+?q-hh4wMq~;)oGmZJw$JDqUky<VcDE$%r4WifI4))r*0Ar4q7Ez(57jY+ZaH-M2qX3Xxu2bVJ6Y+(j+)%Fu-jSwL>TVaEcy4iem8~?~V@RY#uL$lX#l;htVN9Jj71A5D)HQx)}Q7<j`|UR{9kdf^o`Col|LKAD`m|JRW-|9{G<>5lj|v3Gfc33lP}DB#xs)4`b&}Jb~2??+&rk1?jwj&t3AX%R&`bS&DM}dpj_AI74^O)0ZdWl{@s>%eqXRVGRbUh2p&N#^}Fwhu{D>GjZPNzcIQ9J7?qr6h_7%My|}r_g~1D*3XxYx<_W%$%Hhv4f#cfe;mTr2F0lWa9jY4@qX0O^TxQXyyFZzStHI;*kF>*c!18x2Qmg{e1@@;*JO7Ia>wAXD4aUDX*)kif`pn`w<g@sb8c$FMeuY7cvlnd(5q;3OKfBE>cz1|-dot2+mFCDvB`TIJ8O7te}0CYsU;v%j($ia>`d)a*~S%ZKH9#wS+$?o4)tS`#@r7_=<xV?^!D)i`58G{VREQ`=5dIfdod6bcvQF&-@ZHHSbjrw%jSI4VfkP0R{u+B^@%bA3ne^X_5xM#y!3eS@};^mNz{c1LSO0(A6>qz1^D^pm4}^?SUkBzxxv`UNG@*Nk>@=8RGne$_?-B<$lM2ybls8X=I(>%IV&+*BWcRu<uN6)l?<|~Xg;IG>p#Xkv696V<kbT$RhyS;;f{q-uX>@H$s$uGO3N%UAE8Afyq^ujI6-rZj0Cu@8&uq$<LcDHPG&!8XaAxdtYt}BcTus@?TMyoZyVt__7?~{E3uE@N;Q&MWQ@0Yn~Z@)N<`sY=Y*jPUbj~h%n8Y4E#3n3qh1s4WbNu6L}Ir_aRNpX6oS#VAfUbz_KwTjo)E6&s*KD@hoggqn5?BXk|uWoG0IEl9%#LWy#P%-Cmg$q^_J&}a4bi<1rUmBpcD$>(dFA_cjWC}s%nA$O!&Gaa^AQ%W+UWt66o8vtl9*qEn)dXf{r?Fn|rYOL9zPU?v4vK9$CU|QF{P5k&uI4?)Vj*u$B|8+{hErN{%urhL_5d$5f6nA~K#4ts28Lo+JpKSw$zz-gT1-(19}%4Z{?{F{2;)i^VWrh{bFPSC<@aYe$I~CFE`~Th0@4myr8mnuvS&wOE`8`Kz%w=?^S1AcNr|N&8W}8v5yQHtjEFYw;~f7bwE*M?*?xi!_eVeq{JNN$(f4<=s8AMM{cc^w-SlhvQ|E#*0LSB*vH&fPS)^^pgiQ-y_w%>^vOr4}<&0!>@573c62PBq9vSS{EO6T+wFkVKlspll0IN#d)cb-22>YBKWObBU(=837Qe;sy~YJM8E|lZp2f0jKR2ZA7`ougyjW-jEUUz+avgu8;V`K?cqAxu0e^O3ofq^H+`4!qfr|^HO9S)_PNk@@8x8bdMQ2SzS%yYCsK?bg|J?$-)U`)5+&-j_2OrXnuX7!!{@`=Vdt+y*Y~iq6z<~DkL7fZcNRAE;O9o_ZC<$53;my-gKOH?N2>8XcD_ivyS2PuPvpAZfPSVPZhx&mDm!14CDyb6Hi{_V?pIK$Up!Zq8I+Y4DE-t*)3lGa*y=PixAEqu=~R`Ga(q_oN>Ip>62`9W)j!%wk80XStJIbCk6l^L$l7(~vt3`7=d1y~Bxq#S(MPNLgKb7u6<!&Z+U-<{x&~<ni`a)dY)y;6-N+)e#?EKg_i7?Kp^&R_nO7IkH~n@YRiB0WZN=xlI|75Z65q0RUVi^SD=CFEpT{W2!zmh0Qx${6-<{P~G7am{ld}6%R^e6)nq^^sdguwAAKlBM&#XhRT8G(km-9K@!XPI;SG4&8IxX$0Z-+^EA5Z-LDqbYR+4Qi@$kxSdyWdpyu>FM`PU0l-@8Z7SzmK!SwtPde0|q7F(GmJ~I17?^v64C|Ic%@K4+q+pV<v_7+jso^iQ@qBmo6~&zGGaG&hXnluKYi1q&_$'

if __name__=="__main__":
 main()
