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
def pop32_swar(x):
 x-=x>>1&0x55555555
 x=(x&0x33333333)+(x>>2&0x33333333)
 x=(x+(x>>4))&0x0f0f0f0f
 x+=x>>8;x+=x>>16
 return x&63
def k4_scr(cv):
 cw_,eb_,P_,R_=consts5(consts(cv))[:4]
 return 3*pop32_swar(R_&0x00F27618)+2*pop32_swar(R_&0x7F0D89E6)+2*(eb_>>1&1)+(eb_>>2&1)+(P_>>31&1)-pop32_swar(P_&0x1FFFFFFE)
WMAX_CAP=556000000
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
K4_S=[]
for gi,g in enumerate(K4_Q):
 if g[2][0][1]!=256:
  for PP,n in g[2]:
   for j in range(n):K4_S.append((gi,sum((PP[b]>>j&1)<<b for b in range(18))))
K4_P=[]
for q in range(0,len(K4_S),256):
 Z=K4_S[q:q+256];PP=[sum((x>>b&1)<<j for j,(g,x)in enumerate(Z))for b in range(18)];GG=[]
 for j,(g,x)in enumerate(Z):
  if not GG or GG[-1][1]!=g:GG.append([j+1,g])
  else:GG[-1][0]=j+1
 K4_P.append((PP,len(Z),tuple(map(tuple,GG))))
K4_Q=[(k,c,B if B[0][1]==256 else(),s)for k,c,B,s in K4_Q];assert sum(bool(g[2])for g in K4_Q)==110 and len(K4_P)==34
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
def _k4rb(m,G,tg,u,w,fold=False):
 R=[0]*32;l=0
 for e,g in G:
  base=K4_KQ[g] if fold else m.ad(K4_Q[g][0],tg)
  m.o+=10;r=m.a(m.sb(m.sb(base,u),w),M32);q=((1<<(e-l))-1)<<l;m.o+=4
  for b in range(32):
   m.o+=3
   if r>>b&1:R[b]|=q
  l=e
 return R
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
 s.cap(145000,'g11');s.k4q(a0,u)
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
   _,bi,j=z;P,n=K4_Q[gi][2][bi];m.o+=10;r=m.a(m.sb(m.sb(m.ad(T[0],tg),u),w),M32);RB=[m.sb(0,m.a(m.sr(r,i),1))for i in range(32)];J=[(P,1<<j,RB,gi,r)]
  else:
   _,pi,j=z;P,n,G=K4_P[pi];RB=_k4rb(m,G,tg,u,w);r=K4_Q[gi][0]+tg-u-w&M;m.o+=16;J=[(P,1<<j,RB,gi,r)]
 else:
  for gi,g in enumerate(K4_Q):
   Bs=g[2]
   if not Bs:continue
   kq=K4_KQ[gi];m.o+=10;r=m.a(m.sb(m.sb(kq,u),w),M32);RB=[m.sb(0,m.a(m.sr(r,i),1))for i in range(32)]
   J += [(P,(1<<n)-1,RB,gi,r)for P,n in Bs]
  for P,n,G in K4_P:m.o+=10;J.append((P,(1<<n)-1,_k4rb(m,G,tg,u,w,True),G,None))
 for P,LM,RB,G,r in J:
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
    if not T and i>=22 and not m.jnz(m.a(m.n(acc),LM)):break
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
 if s.check and not T:s.st['k4_old_fixed_shadow']=s.st.get('k4_old_fixed_shadow',0)+143633;s.st['k4_new_actual']=s.st.get('k4_new_actual',0)+m.o-t0
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
K4_EN_LB=10809.525521563191
R_LB=0.9921709
K4_DIV=3421676948137525266914850497/5378217134720286959578644480000
K4_OPS_PER_CLAW=10061
def k4_budget(cap=WMAX_CAP,r=R_LB):
 lam=math.nextafter(-math.log(0.61),math.inf)/(1-K4_DIV);B=lam/(57003.18*K4_EN_LB*2**-32*2**-74.4594)
 bw=math.ceil(B/r);return bw,int(bw*(cap+6))
K4_WIN_EXP={14672896933643966474:(59,1,0,62400,0,0,109188,6050860),15921217793420643850:(16,0,0,0,0,0,0,4882577),17552297034189817508:(28,0,0,0,0,0,0,5020878),1866586107145425828:(10,0,0,0,0,0,0,3661839)}
K4_PASS=143633;K4_PASS_COMPACT=733+110*110+210*403+102*114+34*403;assert K4_PASS_COMPACT==122793 and K4_PASS_COMPACT<=K4_PASS;assert K4_OPS_PER_CLAW>=573465000/57003.18 and K4_SETUP==1107474556 and 93.8495-math.log2(k4_budget()[1]/2812+K4_SETUP/2812+2**43)>=0 and 32*(table_words()+P.QCAP//4+1+18*210+18*34+512)+348941<=2**20,'k4 opc'
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
 E=((11264,89,0.0115,1),(0,0,0,0),(0,0,0,0),(0,0,0,0));R=_k4e.__dict__.setdefault('R',[]);R+=[v];d,q,x=[sum(e[j]for e in R)for j in range(3)]
 assert v==E[i],('k4 diag',v)
 if i==0:
  Z=Attack(win=1<<16,seed=sd,check=True,k4=True,screen=1);Z.run_window();L=Z.scr
  assert not Z.skip and k4_scr(Z.cv)<=5 and L and all(c==69+3*(S>5)for S,c in L)and Z.st.get('ddraws',0)==sum(S>5 for S,c in L),('k4 screen',len(L))
 if i!=1:
  c=K4_Q[sd%200][1];o=_K4C();F,V=_k4fe([_k4class(a)for a in c],o);N=[(z,c[l])for l in range(len(c))for z in _k4lf(F,V,l,32,o)];r=random.Random(sd);g=r.getrandbits;C=A.cv;X=_k4e.__dict__.setdefault('X',[0]*3);x=X[:]
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
H8_EXP={2600209493401801829:(59,2,22906,22906,292280740,6068431),10907755097612878284:(44,0,0,0,0,5422581)}
def _h8w(sd):
 A=Attack(win=1<<20,seed=sd,k4=True);A.k4_ib=7;S=[];_stamp(A,S);A.run_window();I=getattr(A,'k4i',{});N=[(I[a,u][0]if(a,u)in I else 0,w)for a,u,w in S]
 v=A.st['claws_distinct'],len(S),sum(n for n,w in N),sum(n for n,w in N if w<=7714620),sum(n*n for n,w in N),A.m.o;assert sd not in H8_EXP or v==H8_EXP[sd],('h8 exact',sd,v);return v
def _h8(i,sd):
 o=_e1(i,sd)
 if i not in H8T:return o
 v=_h8w(sd);R=_h8.__dict__.setdefault('R',[]);R+=[v]
 if len(R)==len(H8T):
  C,F,N=[sum(x[j]for x in R)for j in range(3)];n=len(R);F=max(F,1)
  z=(F-0.0159143*C)/(0.01829*C)**.5,(N/F-6838.16)/(15510000.0/F+1202.0)**.5
  assert max(map(abs,z))<=3,('h8 band',z,R)
 o.update(zip(('h8_C','h8_F','h8_N4','h8_Y4','h8_Q4','h8_ops'),v));return o
R39M=b'c-oa)eSg}xvi_e>L9?fc9R#&(12#lChbFY$ZJL|DoHi{#!Zo%@Xm|@4u+wxu`+Y{T!6Dl{=XN)?B+raSqtVQ0B!=VJbRHEK$%1`fOebvaO@ir|jlJlGEu#6-j|%UE5f9RT1%Ko%7R8V2MxhvlgJQ2YoD8F0Pg}Dy9c{&R<xHG4*OjptPNK?SJ{|Y^Nfa(L?VVnUrfJ1td!u0#jlw<s@N8QK-t-9`|Ic`em%a}!e7!Lbqvd>}`TOtmLl9IS=aT?m=acK~J6f(Q*I`5h?hm7dR<i+prtgDyh4PUDBizu_!sFxGLwIy#*7Pf?a4u_H)yyi@>Uy4l0RrBZfCs1t@94-ffPxCQsK#AYGvzmK<S8tOh2@sQ5=ixjCBUjcqM9pfR$6<EOx>@x$gAVy`ojtw6D}&;p&GYU&B~)r!fW8(Z*lMGn|?))(nhBD;d~0PSWf&vXqpz62m-`RA~q$2X>+=aM5jx-aWfo+#X(~<6@&fqfId{b*(}7=XrpNbv(Oublk4b4)5{!GYI<{UB}VA2n9dn6RM(g|>X{8UEXK#jG=)P9<6YsK__&7RG(Q^bBWDYPEx7nrK@AU%$AU@=ULaB@Z?upN*hVq5aDM=i{2A_FLxUv9yFWCK^>e!A?e}TY_I*72cuFXLu1!c3vEWBX+T_uAUc9hM9D1rmz)4_<(9FZQG<oqtiw|R+K+rlI6q92SXG$8QDHciLt>}RK?C8j?VSL5GbY7elhm+21Q!GM}uS3mbyyobj;*Cby?D?JiewY6~)Aeq*aQ;D9ZsFv!=wQ8RF|c%kj0tkj^Xl$k;M9w?s$cE*ZMPU0o@4h1LD4mQ-?v<+IPm<MJ?Php_FzzVUB@f-xi_eWezoX%JPhohx>s4uutYVzTX=W*7aeJPj%C?Ft!@-8hg(j)4(;G>VAq0bv0krMYXjd#kLJL2{Cd%-8iwhZe$lf{t6H_JqRR~<v})DjUSZFx*9O%=Xcnts-!jcwPz-{aVHu87Gz`zK)%#Y_bF1FK<zcaJ)GWjHf}(BJYKCDs#lSHFw`vUb^exk;XQE?t51mrSh;2jtW3YvF$Ka~yZ(EI;!2>_A31AQoLWf%EKMek>=xAQ4pUoU}iNt(AoN4ba+36X&y7>KE{NS~Q5xezz&8fK|<8{>Pb?ya&dib;O$zh*d_OA8uts|c<tg_+M2ZOYGOY%g;lN0W?YsLwRuP`yziSep%(gJy>u_u;$r9H8CXc<2XCvDYc2=!0BK?OxTHqCpCyTHu-TjncbBA<J#U>X_Na`~5#63jI7Y%tS8)!1@%21#@@1H*@^Kz`hjZ=I<&(^hTt-n6A~W)99WR2#i@R?rk7*$4!l0XnRn_Te&~HMwb%Bbzv3R2ipwRS}a-gppzzm_ca)LM*xk*?_TFi9i?yIp0I((|m`M<v5&sQK&$QeQ75wULNYr@q_3eY7%VE;L8bo;VRd}muLub4Fpk0t)ez&EB1~BdZGPZNEW0lO}%;2nu{M%L$;l?$lGZVOFzn07;O!Ml&Su+dD70|wErud!ucyg>0?C$yAyS>YV?XfU1GuS@x3h;zW$Vgg4gv!&0n!Ko6JcVU&Ls*fJxU=iRJpJNsuoaPXV9!r86v>UA;u_dbb2eM<rfOn|Q6Olj$zDU^Q1AtIO~-<&(>&(d{<d@>^ZjYw}r@PaDQ@mj}gTF%(*>Gwhby^gwigcgaGZ@F1$l=w+%G$A`BB2#$yy;I}qo2+NWX0)$pd11?4tSxeDqDH=48W;;U+H<Mm$u{Qgnv~D_{&BMh)%99wSPd$;7@%e`hUI#up$qZ4<lFSeRuGJ~?M!DK3a~k5Noa%Nkz14hnDwP}h7K~XS{HDJUT#2i{6&Eyx#5Gw6qZ#ytc6xja+s7$L0H6;zXbP5?go4M@{KfGxngJtQ6mR`UP!eve2o({s;rlZ|aSJsx{OKebPL|;YGRT7l{VPxhc<`6tlf{EviCWy>5BmB8y@{I#El>pruZV$87Ro<QrV*-{hkoUa7U5=AKFvWjjgh0q3~x0>GqvU?;v+mub5e;thDS&bEP+Zw)r6|aS}gFj)95n1!}PsY?<8$c()NVfn`ze*+0#1E7TbuC0!RtAr1eskwK%Pn(hv1+Ic>yJIz7W1>xb4<`kj_lSytn$nyTGofv|bOA{q2}48y@Vl28snaxYny{5FRoD%lWIEHJoX+3uDwIQhmxl0~joQd(y6ZKiLm5a1>vNpX`cZj!@I%PdK8lMSvPi*nX6R-G(zwd~R|lW#M9E2Kn}lPyw`LrTjmNs*EbQXu3MM6lPPm?!0VTnaYo;m7;$n1-geu##AXEC{I~2upra_G8(CKR<!JkRd$wC(|{NW1$SQ{g};TV6nhs0pLV#7BU%2y%}~z7&qmdMO~qVF&F{)rc|z>Y$?eO2|fw4rXW;6i9$>9OF`PIP*Vi(tfzeX(m24JY{T(=pS*w&K5VW>HZQ&cxDPul8!cs3Fgl>7I+XISmY7B~;lR*6OPOXV2Rbck`MI5a4%5$J{&V|1O9#Nx5$XEQvb`1~Z`=>O;w_suXt*AAe~YN67y>}bQt!-5c6T#}(KErFB874AkeYU_-Euak?Mk0^f~cBoZc-Kga-Rzk45U4iP^{0H{LcC&!v~l`#5?*{6e~H`unA$zJjinm9cEr4rSn8A0KlgmVE{1+^CAGTWc_5|pe6^>$Q!Qz#3)(f6&IQpODXY<n4p|!n4<xrp_Z*E`K~Ov6lQT{Zs?f1bj-h?WA4&16&)CRZN*dRugpyD&mi}|G0`OO(R6yt)3qgqy^%EZu)1Bz*tpR$0TaP4#aJ0@X(5yrrdA09A%g_MX|tKB>Bg2RWmcGv>{)8cQgv3Ck1g4@Q<x<$mKMp2(`Ax&^~j2C`yzxyAtdQ~N_*H^u%~t_$dnEt$s=<m6)niLkG_&c(^FSuX4(t|%nSp35NhO#;&tkSqH;C$K~y3i6qUKX^+BjvIUl5|8`A?0r2S))K3k+Io*hHE-m#QwGS?|fl$#j0*s8^PENBU}xSHcOTeYdBE!4_tPGS)qnO1Ww7BW%tU%9+y-zV_Ck6gqG$%qxzkcglsBBIkaJHZyP#m?Wc&uw<v_OZERpId111rl1Y#|$sXnqGk?Uw@9<^1V{8K)uE-)u>)UOO0|8)1o~&C1U9mmr`Xar#ezj)v~lvckCR_2_Xa6>P9gRIYw<_%p89vyd~-$>UbxfDLO#Aml6Lx#c#XbeAh$oI^P|?irBMwJ)H(Je?&xkxuCqSg7O#+X<ecG9!>rJ`8)mLbGsQP(x08S_5E?vi)H2HQdSZ&Jf+hXDzppp0{VCrCRdO?f<AoQf7jBlKDSWu;wujyTE3pfeo~xRB1@s2oMOGMv=GY)%hf~{Fxf|eU!kJw(Cu}F@@NtUYZS5|n0Oxreicg?UGYFnJRm#`msp=Gxj?}NQS<l%q^g4x6!&FuLzf_92}v{o87oK>_hk`=<Xm+?GAxM>Flj#rt8}Mt@<M2oi9GN?;?A;l^gWd6AVQ{5d+}-;HZ+rPm5UhS^(q%+BveCFDOgk0OHc)T8Zc~v=tmxJrL6D@wgP|Q3bq)z%Uq-`r7z=o!rd|6zeK@`H6_y48p$pm!Q~Q>n5jZO+bE;3$eSZ<hYS`fey7zgQ$w~z<#1b0a_vdhE<>`lcz20ty+lpg`3D5qx{R~LyRSRV*ucfC9dEX9C!ZP8MA*YMTM26?kJ`Vgy&X-~Jhx}AGSko-(hJN}$1_ij{5*9h^R8&cRBOv;E0JY-Dsr@8r_DF7gU~h%MWTx0sEv#kg_BpWWgbbZa+5haC5trEupKHRBeX5^hQ>{Y**c|wG_zV`HJ#EwnvG2!k_Z=+dr|@)`&w$pFQBzb{N2Ozi{|YD%Gn&5!l)R{k6*-(pIdGpB_&8<&)^aS*dyb;Sc{KeDi{dpd&^OzoiU_{&tU3i)9Fa%r)4U2$Yzg|H5Y0Fx?K;-<IEm=9HO$>-p__e@|*gDRHowXBKv@ButtEozFh=V&%%oH=_F*g3r251jLedtgP6)_dTnlzUufqShm-yxm@l8d!r%aUVQz<zvyta1^PwQj4jp;Wd58MA<p$z01@@>Hose?(U1(-H<0dUIN<mzh*&r4saepB$%#9LU5Yr=5&fReGN*l6IZ0qqgIBsoCZe1oqq$6L;#D)-`B+fV-_rv)@8+(ge24rGd*`elQ*{3v`%9~T@)=;9$y1{q7kz2o12Lz!}xlANs1MyUN^g$SnofSS9P7u*S!7-h&!(vzE@W{_Uao{*kz~5s>PS1rb<4_@+*&A=+MbRAIiS6Ca_OOiBmD`!n;2|Lkrz`z5N-j#|HszjhN13s@X|dh*9d_Gy@h2n^1RrbZYF83rCGEIO6PU<fZHx)l0c`P8z~nCgi6od3u>)fco<!^dms+&gDS-j<or(OS#V#6L>00Eu2vR}RN4ibZv+S8>%G|73r3Kk-%2O70lYxf62Bj3%OLoFeQ`qG1$hO%l_L{xPK>wEPj&zYkhJZ<<(rq%PRg)1W<ws;erWeyjnP5~U$}o~+O}2PRhL_~<k_}$+2=7+h_SMRbxVTYq1YG$w0)%~SaCJ@2`&RbVZAPY$zFxZeeXalClb5GsC(`sA$aKI$$_8L6JfUh@P>Qf^8LLL7MZ6T5s%v!kMt0Z+!Pi$>dtZBX^;&h9<U4Fphpm0><--Ye_;UY5cK8O;euWI<DJJM8YYA1;PSXx$W4^=8QKVsp=3P->)xUa)r+;-qX|}6VJj1Ito`b7bcwU2{2kqwSjjpy5t8hLXBv_wohppw}jAfoo=D(EQt~0$|yHDrYVsME#Q*30jC*+KF)iy-UTREL?GEbZ7mhsA3P)ERO;uK|`x>f8xcfBs1y&;3%PJzO|0eYI|CjKOglqi;aH9=YBZa!0-WuH`$Qp9DIDK4iQqGGYVgNjO7rK$<JtWwp4+*ZhKg<Pgob$Okos{NJdP&$~1t1ikiGYx92-BIWYyDYQbWtlb4l3b7S(Ma~>>c2V%TgziGoVK)JlJ>cNXqL1!GDj#%1-P9|*OQ(%S**i(8i}Q0L9-q2#!0~Yo2Vcc%pml^7OkuAgrq7Tm5#>PjEl}MH;zJ{FQY%G9z9*kYJqi%G&jnc|4PZQ!uiP?cK(u`y%MIuY@B@|G%B<&FM1!v-rioptyws*G7Yfm)S)M4-E^62;j{{k#zVQrD>ZIfX6?bQSq~g=+$1m@Lvgd<)@{Njb62ZY3EQ!mTdUV|*tX$X2C(@9=U5XI-oXZfQUPb5CbPI>;Ka;D*4?Z+HRhT;hh43kHa8z^2YrJvbN~wUX8@bqz^)N?jj$c)v+KCd7Td1bF0Ve=mJQC+zU3R7<D?gWAYr=Hr1&??nwdkdW9UGyRv%=iM%K9vu{m|cI?!oEb%W5kUCp68oICD=T_@hbAm?i2oJNilJjl%jx=Z53p)^CIl^eNf)Xe&WZ93rHOgraFZnY}7#9=a^tHgV~R%1#W8MalmP1AzZY2@hJs#3p10exFExivhDbk1=6NRKV&mSfj3aQsQB%Xy=YNa}=$Nde~$5jJd_uydT-Rl~tO58DRkvQPRmNVwp<P6DzBTPlKsk+^lYo|l^AV9YisxV03KrmY5K5*o)?ErZ5m+N5ljYv$F3*Q~lyReAPGDpOU%woSq|>6o@kT?3H0u9Xv7)xgO$u<K4bVU|*K)23k?#5m^Lp<$aY2%(h2#+3pSil(&1Rm+5vq8kNTX!7P#7|(h^=ud-Ci?V<-+fEGGX!3X$5LIv+3Wh4Z9xxhCa2-jP21Ulc>}J7mMl_nF*9Z0<=zx}pcJ}6$TaLWpsQlb8gT3b(4)%1IXmufCd+h@IgcO(U>0LG$O}$7PnK~o5n+1Zz9R&Xo!sC4_tcu7FQCb<j@cy)Yawf`kyHd4tp0$S^R}Tgi`LR17j0EjKWEzb-g7yh%mQ9&ld9H4f2_yrir+3CGALI)j&a$hzu5aRCbluoq;Q_@$@eCBsUxGI6&bWizn(PITK*OO~h%0H-HSA<f?%usV+y{4Fz%p31@?tsG=oA<KZ=zb@R#x6<DW~OyHo<Q35ZxS7H@bd={UYvp6pDA4IovNWE5_j=9S7@&8l4TlP|}8h2EyUlD_#Ff!d)UTy%wGAwk(%PA=;En>`@=YBQ@wRCh%5)Y?D}vJIIi}YIkJ`svjPj#YaSle}n>%#mMh(F=c-erEFGeRl3}As3^bKQkKV+00Nhah3U0qK~h4a{Itd2VJR-l?;Dn4#S+m_EIsN;QgvPT342xr#^e{gMg9nzcr}Gqw{!c8DU?SMTmLP?_f#_om#DzyDl+CTXlyW2F&<0hmI{@M<8cdyq8c#G2H#N=8)eBc|9@!97-Zx$7#y?ETm+~;)dGBctOEp{sX#h}oQMscpMQftmT)$L+<F_TOP=?mVW0KAMOd>LHm5gK_2zRgDV&S*56#vkYhUhWose|;%GzIdlTLc`6qhTs)};)fu3BH^8~Cc;R`n;lS%~Cb5E~UTOKDiBII8rWYHF+c2Y&f`>A3pg>)Su>kKP+^uK)M<-h1==pf$5E?#`Efpub%P&#%0be+7E`<hST_`o8{bvij}5Iolste`tT)aP#Z$(Pw+~x;FS$(!c!p(Yu(`{_*K@ap8XYBe+}lw71RorGNaWKmWeE{_Sn8bfG=_e*ED#aesDsIGO*Cb7;Kz<jw!_GAMnx{`&H0=JtR8qdo93U-n7!_2+r@=jz$Jmo@XYTEDOdZ+^TMJbrf1zYTx;T=qWh|MQ_fzJL3=J()*`-+$;@(;a#re(yQe*8autRqsCh<NWAn^rm&9FaP;R>y!EQ-$yIwP5tO!2gpdhmUrdymtgNZ!-l*Sa?l@MALxh9?)HJgN%+I`uEy;er?H;A3W8fM@&b&!|01uyz-Y2Vj~!y}oCY`LRT#fhZ&>o;hq~~FdE}<t@qAHf%cuJlb;pA;F-J}#5_DaKwi=roE#+U`XhA}_ErEsH*+g>NLI-=GqCUtik8Gy9Ga@R>&CK?~P5D<BZsab85L4Y(_hSYDq_I{vGt)~kbSDO>kxjKTE8S(+D%suRO$i{M>?Y3B!D}&jA*u37R$?*4oVBGT{h2szVZWJeDxwXG=Y{u_=IZ&g%|2=8QV+5Iev?|Hs-9i>0G4bhT=v94*f%-%s@A~hhav6^`hhVB1Iq}_0iwXV8{)R+An2QJKd^1LUbRBY9Q3Q6Q4fQvV-8Gi)eJ8PoPKC?m_k0NTZRuXzdrDIH5?G7n(Gg2!ybfvKLmZNZ+cam^AM4rZTbf8F8bBFjXRv7?^j*i*Q_E?tNDTD2j;*-I2l+6g>OAFt+t7jFx}jvt9Y<TRW~imNDcc3RWm8j#zrFj=Fr`{+U6VGAGEV?79u@6tC<c3^cy?`nA|q98ttxXS<OU9ZyKALMVAb#8%Vkb=x%5tSgxs>T4`esNv1o}hEUwe!<7RBU5Kg1;Uww}g9CPOpf{trxa%Ase#GAKpxey3vDffnZr$KjSDjKk-scLsT=hXbim#e!vQ<!${DT(FN$(C8nDPVU0Giigr>%4VgV8)8CA*}@_2RD%(^TGJDf0Q@lrOqhVr*`2FOS7*EV9P3EZ@yxiFhpf;;i!4?!8A7biO%7wfELO!S?(W`%INv=#18p1$jLR=`5K7ka296P4#9hq%W$-r*`oB0WDB6f2u)Gv)iLB(=sqc46cI57$hoT9MLk7{fq`0I%gw_Ri_Y5QWDCVc1GmS6;7F=m`#`<n}izK2@cGB2n{cdZnlu<P#!{fGe=}8Yjq(PcXJ(_B)E^7v3JLnUHqtlE~6tzXigkKiDd0hiG;eFtGnQ1cAH&CSv7V%fch;)W#;*}+QHHD;Qhh#vsdhJrLzO|D+q||MhwK5?%b`gk!d1|r>CzDp_*STn*BGM$^V|4e5Q=~T<OmDtv;nP&)w}if2mFs7V5k})4n50K@^0n&hzsNoE+SW`OX=`C1ei)ic7?L&ATU`arM2417yz<ap$hfP5{+OQ0g{U0**{NB)XVuFbO4dkSf{Djr4LH=UuUq)fJW1{U!A^$$h0G2)uB?N`lEMSB|C_J7RXL%`5)Rbm&9gGbG#vMRpHbdbq6bPcUb(y94L`1)QsACq`0RH%X)1;R61>ulOS<H`d5XY!jT)hyZM)XJr><Ju@1#?ZKpWC@Ae>?KOQiUW@nC`o)5Jj@NMal&H*H+n8J(*#o=bbY;IOrB=smbdj`@Qk97-88)<_|KqhZM$&PPDTR05yrI6{&{`l6urTT<(L3F)@JEu<tO3@s#5Wf?aqph4{$g4;7dg@POn8>;<g9XIBjpAz`c`(;vpA;SmO?V59ky^<(PaukPa)DHAX<2ANrx$o0pSEfGQHf$E5HwCupl}?R|G4`WstHL$-sOfc?_7`?gL^Ng=2*7bUy??uGx@@1lho;2!=lP<cPw1KFrcEoQpZGIpbu{q{B>{PQo@{qiMDf*9&%o-xY})`Y~0w5M%Z34ID9GgW-G;VQ;<~deLw?=^^hZeqfDj0nAyRr3C`_FwnM~=|5R?gC4GLxGN%-ve8>}r{|BBiwM?7?bx9}X+sYK?Je%qcn=kMNgVUG*(+^<hxgz%?RN(Ps~+)&CB9gghiT^^7+!~q=%6do?L=j9<KbXeqo0yhg5`L&(58$?^=`vtA?W;0uY?mB<?DLoCX5vYO_%v~nKHQSHE!ugU|QI58;I$6HV3)>Iuy7HaoIzddU)HQM+q&3;<wb=eUgJ!<|TL2`7*m-&ZHVY%J95VKV!<A5)w;N8|P0QYV1D`4xSH72d#e}bUfI+rRdBb{gw=ezZ(bZcj?zS>gt-G*@fPd+tS72{Ug)(NpF6aemC>H_s4QxFUdY5ncTQ9KdLvsD^HBeB(zXO+TOV*lZv9ObE<c9MAHk`#V@YNY#L0O{_tct`^rf*J)W*gGRS?kB$3}Pe{q!^1t}*-%K0TJr+MpaNa6BOMhnTHHMK99cI%Y2FV6m-{NdKwr%QM_xQ!`Mrv#1uJoIj5V?g0Xj9>fd&2N~Uk_e6sDq){MWu7Tns#V{F`su;99xN2d!gt1vB!4}AnllPfG7Gf?ilae8Rf-NLKC4VKZ3k<Cbaz)*>ClJ3V!t;5h-Dt$$g0PI!Kk#{lswbO+NdPHAuyN|(cG%~aj@`j!m-zb<5<9e95gt~0?bC|hbkU4zO#cdHWA)+*z<Z=Z3hi`#bDFe&ov$%g6gynp{%4$0-@DU4Eg&Jm&*I&r~Y#%a3KAQ=D0ub6B8ms;rBhg@PD-y05|'

if __name__=="__main__":
 main()
