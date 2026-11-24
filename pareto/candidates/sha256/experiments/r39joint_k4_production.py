import sys,os,json,random,time,hashlib,math,zlib,base64,lzma
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
DPREG=224
def consts5(c):
 cw,eb,cv0,cv1,cv4,cv5=c
 return cw+(cv0&cv1)&0xFFFFFFFF,eb,cv0^cv1,cv4^cv5,cv5
_G=b'c-nPWO>Z2>5$*1o*(G;&#4#;X<W699j}4fINV)MK0fG8JQjik=1>1lH0VB!wE?0tc;Zl|kIs~u{Uwu#j-{T*U1Lcp4&p~qa+5aJM-mB_aE+v};cKf5M`qitC?lm7AJ+Q_Y`%dxx`lA1{i}#&;=4qDcm$8d%ZD_2^vOF(xi@(8|UD$YXYRchT`QX8w2OrP==1g|?&PT=!?!NcY?9N?N4DY`8;U}MbeBTU4KfO78cF}Gw-a5gbiS@m9{cRnZXs?-*Qypg4%okrh*3~`t^mHlk_cT1-b6@Dt7jZCeM|<wsa$d}@+iy=)-CVb)U&}C*aVr$~9%nav8J|<Ui^qQCi!OE@^tKL~w!%sg|2*}h8NN@=K~p~_zCCBC^nyyh^45<Z#p78tyNUy{|2Bv9XJ?{$7fL^lwhLoyx~?taf6QTJN^iXDyo-yYXs4aeF!1>_9&_yN)aSBJ#R~%ZIBej%2IxB4d29Ws3$I~3?BeBVbn{&&u7twf;6HYD4l0AM3;2Te7{fpOwX$PZVz-EkTNUBr_~Th9#<s-79)+Uxuf+k-V(!Q4bl9ZDXnj3zD}P~Hkw&V3*u|cE{v8>&P<3R~-h^RjcY*fZJjy;SQVH<E16lrAR(GB7RFJ0v%8RZog&eh3@55H*v*~`N#^8jw$^iJ>*JQtsjGRL+I(k9rwoHdp?L1G2uZ@4~Qi$s~Iv?S0dbPosnw(k3^8AWwk?!AGhc!kI+vYI54p-c?y|^FVkPt~enCQUl#fJ1Y?bfX&xzM?M7%urOI<zfT%#uX$uG)2iGwgT_#nUiBs4Z+8zkSdevX>~>b!!0;b20O#2^B;peg_GBNwc-J@tFBCK8u*Q<U(_|1aw5Ski@#ojOtUKr9#D$iW*d3DTz=lOUC<NYdk%}><$0=G*rw-p#XXFuB2zmKzL<)R|@XZv|YN8r@RCj@OC)!n<&p2F;4eq_-L)TMwEo;H<8j{z|>E~$70W&e9vfY#wREsZciKRK9wxr00hwmVs9JNft|GlLeq{TgZb%{Nr>G|9KQk8WEGR6<xCx+1SI34Klq$TRZ1F*%!Y(H#h}NxBsXlRC=kd-m%Kxg6AYr>7viqAM}$#2X2;%11}vhGS|`V#H%d=r3ED^3Emx&8cI=TXHXA>)9ibSBU9=B@>IcnnY}C=SeIXAko+_}y4loU)W91J~!)RAeWu2+I;|suyHnF_(O0k3VGyL1}2CZzP=dxF_p3SXBa!}f!+AQPG|CPS|>#rG6m+|Dsm3eA`Y}~gcHBWz$yezP%dG>jByOP24|B0RfTP1T?+O;&1wxFLdv#mJ_hlS}C5X$6L3-9I$0aRZA`B+e3qS3g5SY%oyO7?jjO82Lukyd_t1wrZ8<61|~Mt%p;2-Xj9x8V*uS%gw>s2O3IsiNG7x5&Z7%(uT-&b2+t#iX59lA?G;D)D>Dq<}|Z0&l8)rGazao|ULx)k`+uE|AVsUC~Rs-BOn!AU>n}c&c_vpm-H(=>ac{-WkMy)e01N?$<r~=NfMoKMFNNVUwu!M%WbeD;l--taJxR5|jja>8cfna3N5i7pWhIi7&&rFZ!Zlz{c@A5rBtEt>#BNK?JJ|nZd5smKqmnjT0Kfr3#p8bA6YX=PBn9XgNcUoJgMaC(AwT>%T}>sqY01wA6d2O<p5<W~t9sODnIGk-x-55@G+6-e?}wODp$2z*yD++53}f#EWwVXbmAM?j!U3_?of6wIxT9X|&lH_}hMT&E#B(HAb0?)-ZB@f;UD*dXT?D5UO{AYx$q@?qcpv_uMy}!O^<Y2cO?AUs#(j1e<->IzoTgW>bBjAkciEY>=yLxdcl`vgFbd79gln-W{$gp0$>|Z;eJ<W4_WFbFG5Z8Z)f{EmiM0%aIa%M_$p#X@ell^$<IqmH*1%0;j-cZnk*?0`b1{7)S@Z*$$d^C`*=$&SRd#D0XmValOD&aBv{^L)<>-(~{{9|M=wHmW!VUZP7r+$S`l@P-r(|Rv#U5xSV6t15P@k&*Y|c(gCrbr2G4?p9jalx%9I3Mp!jH8nZm2x1F!pHYuy7(g_6hK%uI#A9#Dv;Pe6yUEZ<%tssgNSS}ER=|SWv+FHC6L~OxRe$>)>)640G0^1M^%nT<lY{KGm%ie~_(mRaHe>m$F@@C?5V_7BGd;%rLTz+pfOr>XflWO1_G1}sdkzgmTQd0KfFPTZ{N=<wmwGNE9BX4>W!h&*}rJGDWR~=1*LtbA5l5x!;hnB~Moc-qapd%>{k$;)s54qT&I<4izk@X4D=MHwt$C=F*35*tKH1E>Mkfo46M18?;Fca|mg<6g=%2EgpnpB-Rt5delXiT)hks>)~&dS#GWosjgp*U!?e9cPvnsYCkZ1q{=bI#0fm2YvbJ!GpdC$R9P&iFca>BtN>bbn;VBVB(aeJPssqH^b6R2f^MqjcU&vu2mlc@H#u31e$IfsWsa&@M~iM7n7jOD`?|5521(<^'
_P=b'c-oCuS#P6A5PtWsATJTDdm<pmNG2U=q}hq~WgJEO5XB-EN5_i~umC4mqnY2n^;LIcoJ2btDF(Xh`l`B)ewf~iFW<ikdVHV$EqxJ)P@Iplb<#A>ttuxYCs)tTd|s4AJD<CaD2vjgRi`<lH%b3db5^UYk+WFSE{LewibSOHdsQk!43e{CyH#cGx_aC5qFS}Py4149YgM|M(EAi<Sq~%&l#o$8JITzCuYD&eb0_83i5BoF5XmfvpHli6Qkrch7TA1BdWs_fO#hJ#DM9zKn%?+@`#}Cnv=Tq|hEza7p4|Wl!x(VUI&*o#*Mwg*Tv64v{Fba6^#*uVTeE3-0297WMWPp7D3;RqP9(`WnC^q2tXh&%JBoxm0T`?U-eDeY>aBpcf*8y$Ner;uOY=P|!qOeAWP>IH=+pZnUL3)J|NMb&P}BAi`LVZyq26HNjQ^p}hJhvZahTd;*Gu@~A})W|JLPGT=iPd3qLqm<+e_X9Vx&UrJX5S%rzn{(^GJEiv5KRY|Jc8gzBznI21*3D4bIqBYdHf#KE@)WpV)Ypwm4{b2Id*Yldb5)US_Zmgn-SGoI=i4tbRr6ojNHO%02hAptG#nm8}aAtC*Ar@r(^31EjHZR>Tn`8w@J}6pku)8&xN*at#>-u1;jZ+&kHvJ-D6NdQr3C_np{##(o@0a$xW4jd(nY|3-iTA=vTTp2T?c|He-Nql0BHO|+6(LzYLaQM~t}t?WSGv5!{f6gzusP%BoyGstkC$UV;X(7dU;6)hvSa$)XPxQMCnJ?|}^Dckgxq0>$oq6!(6frF|-F9BYnj&Pdb^rsY1k(euT5TmthC(`oS+_gJipC?#tb{n!ei0$bl0p4lgi9XvuBDj%ZUjZI{iBc0y13ZJ#_xnF@=imN%`17j_!;29zCt0tn3@2qFs$DCREE9Rt&eNn^iF{kD1-A`RJ{O(J`xb&`vp}1OG|ksLk_?OZ(<vGUl-dqnimZU%0*);&9+T^}kwez#E(UPRL2`tg*JYI}fjlI-*)oo(L#n#vWlGzT&BX~8$W&cd@BtS?wrziAjewVuesE5WEG)4sZm0|Hg%P#lR{r>@%_@X#o<~W?O%q1;aUl|0ep|rBp$6m$#Le0moqJrc(2TtF0|pYRi4Dac=izwyfhT@OnqvlAW67=_9n`Lirgb%i*Q*Myudf)?LjEWwg$8nviiv{6)=H80qq1wIj>tHm`QQ+d-$5^nT!V`8eNir$@Av-TVWPbOC%?kxvxREima>mT>U}0B3YI+KUmMNVq%3HOLSvug(zuD1VTW4dsA_IWj+pT~g+4ac>hECE6T=@9{G2sa-MU^xBJs7Ywl23?uIL20YvHr842E#EDrPWtLTPK#eZgkQoIj4nvRq&{iTRPnn3ImYW%Aq`*`h=INMST3vVs#l-4*M6{#>ndmAhG0Hf?h$nmRKne#mv6>#|p&QgJ8l#jP~N(L&Pb>0VuunoiDK%gbky%IW)4iDTna!tkWkp_l6}-T7O0YumU>G^ob`H#-fb;}Qze&93v^Di`WSyl$y@+0m=YrBpAr+*i3?RWC>5<ASO;@w(7g<*3s{K*bg6-mUd-BCV>mtKU7V?J(b!l?*;H=b*?#6Pd`GnDeQudNqdy{m=?n1S{B+iykycFWOb|bxSiMc1iQ=mMRaQc3wG=EKD~^Jz0$gMnDSe-BsF;WD+c6vq1h-&=|3+yxz3q#lbuEJcOBY|Iv@f9a13L$r(;tOaYISKlq?I3%&T`0==X9#Q-}+ZvwyLAUHkOO-}h(%-{l^-82yzn@VqPmgsWXUM#QA0}qE%$?SD}Hx9<`?dh-k(_eu%c3qV|-BLdU@OyeN^4n8v{ko&aso#Awf7GzLHbp(-688T9tUk--_%j&{Fx8T=>}IRav6%9iU46#D=!-D$ST*mVx#XI(T8fS^pCg>~xIQ<1`O){HRM$hy1h0zmPEworQ$TjoGu5@+pU84^9G5rxNZh~SfI96^IPg~c&(l%{BovWxhydtdg#7-V%t{+yF)hEE!0C_hvS+kz{ip1twGP$kj%|qAMJqWzOPZW<Um`l~gpinD|0&jrhpW`PAyQ7WHd!f}V9eB&QrV}Sv5D?EC}?EMLVIrdyCnUD@HF$wbL(n-gvj6N3_BA$rZ<}t3jM)_&Bo4~U|<|s$RvPhsj|?v7s3cE+@p-0;UQh6JY0*9K7-g?i+a1IF`j3~M!oQDuSb6)1B(QA8QOmIdw=rqNJlL0%V_W3R96uzBpe7a+~z`wxl?knb-CCHT^lL=$QCN@5vM4Z)4p<geZS+n*ezvmgz;g<1=&`xjBA(G=_E^Ot2=aLs6`YZvr6IwF^FWz^Yz{g#e*BuTS{sU(HoiR8)o1<DmTfJXa*GqMr$H{nP_zJ;s&O_^oS_6$KI8UK=)5jEa*CcDY|E~Ra%(l%w5^^RyR8|-R#Auf4U32T+sie%z9R;eJ<^u((bUT8Kx)0M9)hwviuDl_W4THCHbvy{<g`l4r3fObIbs`lHqDW*9ESA{dGWoG(eEu!mzT?s1{p6^Ye$733HFQy0Ev1s|zn$^@C1cWG&B)vL;H5^dt%lrFbr-0Wp6r-I{s=F2oJZ#}izAI=*RF45Z^=@Gw#x;&S2r985>6X7n$7rSVM'
try:import wasmtime as T
except:T=0
V=bool(T)
class GW:
 wt=T
 if wt:
  cfg=wt.Config();cfg.consume_fuel=True;eng=wt.Engine(cfg)
  mod=wt.Module(eng,zlib.decompress(base64.b85decode(_G)))
 def run(c,src,dst,dpb):
  st=GW.wt.Store(GW.eng);q=GW.wt.Instance(st,GW.mod,[]).exports(st);F=10**12;st.set_fuel(F)
  n=q["gen"](st,*c,src,dst,dpb,32768);fuel=F-st.get_fuel();b=q["memory"].read(st,32768,32768+5*n);r=[]
  for i in range(n):
   w=b[5*i+1]|b[5*i+2]<<8|b[5*i+3]<<16|b[5*i+4]<<24;r.append((b[5*i],w&1023,w>>10&1023,w>>20&1023))
  return fuel,r,q["g_nreg"](st),q["g_dppol"](st)
 def ops(c):assert GW.last and GW.last[0]==c;return GW.last[1]
def _kernel_fn(r):
 L=["def k(R):"];ins=set();d=set()
 for o,z,a,b in r:
  for x in a,b:
   if x not in d:ins.add(x)
  d.add(z)
 for x in sorted(ins):L.append(" r%d=R[%d]"%(x,x))
 for o,z,a,b in r:L.append(" r%d=r%d%s"%(z,a,"^M"if o==3 else("^","&","|")[o]+"r%d"%b))
 for z in sorted({z for _,z,_,_ in r if z<64 or z==64}):L.append(" R[%d]=r%d"%(z,z))
 n={"M":(1<<256)-1};exec("\n".join(L),n);return n["k"]
def make_kernels_folded(c,dpb):
 c5=consts5(c);ks=[];fu=[]
 for src,dst in(0,1),(1,0):
  f,r,n,p=GW.run(c5,src,dst,dpb);fu.append(f);ks.append(dict(recs=r,dppol=p,nreg=n,fn=_kernel_fn(r),counts={o:sum(x[0]==o for x in r)for o in range(4)}))
 assert fu[0]==fu[1];GW.last=c5,fu[0];return ks
if not T:exec(zlib.decompress(base64.b85decode(_P)),globals());GW.ops=lambda c:575000
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
WMAX_CAP=549798025
class CapStop(Exception):pass
class Attack:
 def __init__(s,win=P.WIN,seed=1,check=False,k4=False,screen=None,wmax=1<<60):
  s.wmax=wmax;s.screen=P.SCREEN if screen is None else screen;s.k4=k4;s.k4_max=None;s.m=Mach();s.win=win;s.check=check;s.dpreg=DPREG;s.W=table_words()
  s.ks=None;s.R=[0]*256
  s.rnd=random.SystemRandom()if seed is None else random.Random(seed)
  s.st=dict(f9=0,f8=0,claws_distinct=0)
  s.idc0=256;s.distinct=set();s.cv_id=0;s.cv_try=False;s.measure=True
  s.LA=K4_S;s.sav=[0]*32
  s.bsu()
 def bsu(s):
  m=s.m;t0=m.o
  m.o+=2*2812+120
  s.C9=BW[9]+BA[5]+K4_HD&M32;s.C9P=s.C9|1<<64
  m.tick('run_setup',t0)
 def ws(s,cv=None):
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
  if s.win>1<<21:
   for l in range(256):s.LA[l]=NM20|l;m.o+=3
  else:
   for l in range(256):s.LA[l]=NM20|l;m.o+=3
  s.idc=s.idc0
  m.tick('window_setup',t0)
 def il(s,base,low,l,val,nbits=20):
  m=s.m;R=s.R;b=m.bs();m.o+=2
  Z=m.rl(val,l)if l is not None else val;nl=m.n(low)
  for j in range(nbits):
   t=Z if j==0 else m.rr(Z,j);p=R[base+j]
   R[base+j]=m.x(p,m.a(m.x(p,t),low))
  for j in range(nbits,32):R[base+j]=m.a(R[base+j],nl)
  m.be('insert_lane',b,True)
 def ex(s,base,jlo,jhi,low,l,name):
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
 def iter1(s):
  m=s.m;R=s.R;ks=s.ks;k=ks[s.cur]
  k['fn'](R);m.o+=len(k['recs']);tb=m.bs();s.cur^=1;s.it+=1
  n0=R[s.dpreg];m.o+=5;dp=m.jne(n0,ONES);m.be('iter1',tb)
  if dp:
   t0=m.o
   tb=m.bs();hit=m.n(n0);s.cut0=m.r(s.cut0,hit);s.it20=m.sl(s.it,20);s.it20p=m.ad(s.it20,1<<20);G=0;m.be('hb_init',tb)
   G2=0;W2=0;HL2=0;nl2=0;m.o+=4
   while True:
    tb=m.bs()
    fB=m.bs();fZ=hit
    fA=m.a(fZ,m.sb(0,fZ));fL=0
    for fK in range(7,3,-1):
     fb=m.ne(m.a(fA,HIGHMASK[fK]),0)
     fL=m.sl(fb,fK)if fK==7 else m.r(fL,m.sl(fb,fK))
    fX=m.sr(fA,fL);fY=m.sb(fX,m.sr(fX,7))
    fL=m.r(fL,m.a(m.rr(C_LOG16,m.ad(fY,m.sl(fY,2))),15))
    m.be('find_lane',fB,True);low,l=fA,fL
    hit=m.x(hit,low);wl=m.rl(M25,l);cf=m.jnz(m.a(wl,W))if G else False;m.be('hb_sel',tb)
    if cf:
     if(m.jnz(m.a(wl,W2))if m.jnz(G2)else False):
      s.cap(13129,'g1')
      tb=m.bs();tc=m.o;tn=m.nest;s.hg(G,HL);m.nest=tn+(m.o-tc-2);m.be('hb_close',tb)
      G=G2;W=W2;HL=HL2;nl=nl2;m.o+=4
      tb=m.bs();W2=wl;G2=low;HL2=l;nl2=8;m.o+=4
     else:
      tb=m.bs();W2=m.r(W2,wl);G2=m.r(G2,low);HL2=m.r(HL2,m.sl(l,nl2));nl2=m.ad(nl2,8)
     assert not s.check or nl2<=80;m.be('hb_add2',tb)
     if not m.jnz(hit):break
     continue
    tb=m.bs()
    if G:W=m.r(W,wl);G=m.r(G,low);HL=m.r(HL,m.sl(l,nl));nl=m.ad(nl,8)
    else:W=wl;G=low;HL=l;nl=8
    assert not s.check or nl<=80;more=m.jnz(hit);m.be('hb_add',tb)
    if not more:break
   s.cap(13129,'g1')
   tb=m.bs();tc=m.o;tn=m.nest;s.hg(G,HL);m.nest=tn+(m.o-tc-2);m.be('hb_last',tb)
   if m.jnz(G2):
    s.cap(13129,'g1')
    tb=m.bs();tc=m.o;tn=m.nest;s.hg(G2,HL2);m.nest=tn+(m.o-tc-2);m.be('hb_last2',tb)
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
 def hg(s,G,HL):
  m=s.m;base=s.cur*32;m.o+=2;tg=m.bs()
  s.ZI=0
  Z=s.ex(base,P.DPB,31,G,None,'extract25')
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
  tv=m.bs();ZI_=s.ZI;b_=m.bs()
  for j_ in range(7):
   t_=ZI_ if j_==0 else m.rr(ZI_,j_);s.R[base+j_]=m.r(s.R[base+j_],m.a(t_,G))
  Z=m.x(Z,m.rr(ZI_,7))
  for j_ in range(7,20):
   t_=Z if j_==7 else m.rr(Z,j_-7);s.R[base+j_]=m.x(s.R[base+j_],m.a(t_,G))
  m.be('delta_lanes',b_,True);m.be('hb_ins',tv)
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
   b_=m.bs();wi_=m.sr(s.qn,2);sh_=m.a(s.qn,3)
   w_=pk if m.jz(sh_)else m.r(m.ld(s.qw,wi_),m.sl(pk,m.sl(sh_,6)))
   m.st(s.qw,wi_,w_);s.qn=m.ad(s.qn,1);m.be('qpush',b_,True)
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
 def cl(s,base,l,it20,cthr):
  m=s.m;tl=m.bs();m.o+=2
  lw=m.ld(s.LA,l)
  if m.jge(lw,cthr):
   if not m.jge(s.idc,1<<20):
    low=m.sl(1,l);nid=s.idc;s.idc=m.ad(nid,1)
    m.st(s.LA,l,m.r(nid,it20));s.il(base,low,l,nid)
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
    tq=m.bs()
    fB=m.bs();fZ=G
    fA=m.a(fZ,m.sb(0,fZ));fL=0
    for fK in range(7,3,-1):
     fb=m.ne(m.a(fA,HIGHMASK[fK]),0)
     fL=m.sl(fb,fK)if fK==7 else m.r(fL,m.sl(fb,fK))
    fX=m.sr(fA,fL);fY=m.sb(fX,m.sr(fX,7))
    fL=m.r(fL,m.a(m.rr(C_LOG16,m.ad(fY,m.sl(fY,2))),15))
    m.be('find_lane',fB,True);low,l=fA,fL
    G=m.x(G,low);s.cl(base,l,it20,cthr);m.be('cut_pending',tq)
  else:
   for l in range(256):
    tq=m.bs();m.o+=3;s.cl(base,l,it20,cthr);m.be('cut_linear',tq)
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
   s.il(base,s.QG,None,s.QZ);s.QW=wl;s.QZ=z;s.QG=low
  else:
   s.QW=m.r(s.QW,wl);s.QZ=m.r(s.QZ,z);s.QG=m.r(s.QG,low)
  m.be('qins',bb,True)
 def stage2(s,final=0):
  m=s.m;R=s.R;t0=m.o
  sv=s.cur
  tb=m.bs()
  if m.jz(s.s2 is not None):
   m.be('s2_in',tb)
   if final!=2:s.bank(sv*32,None)
   ti=m.bs();cur=0;it2=0;bact=0;live=0;occ=0;nf=128
   rec=[0]*32;wh=[0]*(P.WHEEL//16);fs=[sum(32*i+j<<8*j for j in range(32))for i in range(4)];m.o+=22;m.be('s2_init',ti)
  else:
   cur,it2,bact,live,occ,nf,rec,wh,fs=s.s2;m.o+=18;m.be('s2_in',tb)
   if final!=2:s.bank(sv*32,cur*32)
   else:s.bank(None,cur*32)
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
      pT=m.bs()
      pN=m.sb(nf,1);pW=m.ld(fs,m.sr(pN,5));pQ=m.a(m.rr(pW,m.sl(pN,3)),255)
      m.be('fpop',pT,True);nf,lowr,r=pN,m.sl(1,pQ),pQ
      if s.check:assert not occ>>r&1 and not occ>>r+128&1
      qZ=m.bs()
      if m.jnz(s.QG):
       s.il(cur*32,s.QG,None,s.QZ);s.QG=0;m.o+=1
      m.be('qflush',qZ,True)
      bb_=m.bs();k_=m.sb(r,q)
      for j_ in range(32):
       p_=s.R[cur*32+j_];s.R[cur*32+j_]=m.x(p_,m.a(m.x(p_,m.rl(p_,k_)),lowr))
      m.be('move_lane',bb_,True)
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
     b_=m.bs();w_=m.ld(s.qw,m.sr(qi,2));pw=m.a(m.rr(w_,m.sl(qi,6)),M64);m.be('qpop',b_,True);qi=m.ad(qi,1)
     m.be('launch',tl);tl=m.bs()
    if m.jge(pw,P.D0<<40):
     hm=m.a(m.n(occ),m.rl(occ,128))
     if m.jnz(hm):
      m.be('l_try',tl);tl=m.bs()
      fB=m.bs();fZ=hm
      fA=m.a(fZ,m.sb(0,fZ));fL=0
      for fK in range(7,3,-1):
       fb=m.ne(m.a(fA,HIGHMASK[fK]),0)
       fL=m.sl(fb,fK)if fK==7 else m.r(fL,m.sl(fb,fK))
      fX=m.sr(fA,fL);fY=m.sb(fX,m.sr(fX,7))
      fL=m.r(fL,m.a(m.rr(C_LOG16,m.ad(fY,m.sl(fY,2))),15))
      m.be('find_lane',fB,True);lowq,q=fA,fL
      m.be('l_half',tl)
     elif m.jge(nf,P.KRES):
      m.be('l_try',tl);tl=m.bs()
      pT=m.bs()
      pN=m.sb(nf,1);pW=m.ld(fs,m.sr(pN,5));pQ=m.a(m.rr(pW,m.sl(pN,3)),255)
      m.be('fpop',pT,True);nf,lowq,q=pN,m.sl(1,pQ),pQ
      m.be('l_f2s',tl)
     else:
      m.be('l_try',tl);break
     tl=m.bs();iB=m.a(pw,M20);iA=m.a(m.sr(pw,20),M20);d=m.sr(pw,40)
     s.qins(cur*32,lowq,q,iA);occ=m.r(occ,lowq)
     v=iB;tb=m.bs();idx=m.ad(it2,d);wi=m.sr(m.a(idx,P.WHEEL-1),4);sh=m.sl(idx,4);w=m.ld(wh,wi);head=m.a(m.rr(w,sh),0xFFFF);v=m.r(v,m.sl(head,21));ri=m.sr(q,3);rs=m.sl(q,5);rw=m.ld(rec,ri);m.st(rec,ri,m.x(rw,m.rl(m.x(m.a(m.rr(rw,rs),M32),v),rs)));m.st(wh,wi,m.x(w,m.rl(m.x(head,m.ad(q,1)),sh)));m.be('link',tb,True)
     m.be('l_single',tl)
    else:
     if not m.jge(nf,P.KRES):
      m.be('l_try',tl);break
     m.be('l_try',tl);tl=m.bs();iB=m.a(pw,M20);iA=m.a(m.sr(pw,20),M20);d=m.sr(pw,40)
     pT=m.bs()
     pN=m.sb(nf,1);pW=m.ld(fs,m.sr(pN,5));pQ=m.a(m.rr(pW,m.sl(pN,3)),255)
     m.be('fpop',pT,True);nf,lowq,q=pN,m.sl(1,pQ),pQ
     lowqh=m.sl(lowq,128)
     s.qins(cur*32,lowq,q,iA);occ=m.r(occ,m.r(lowq,lowqh))
     if m.jz(d):
      s.qins(cur*32,lowqh,m.ad(q,128),iB);bact=m.r(bact,lowq)
     else:
      v=m.r(iB,1<<20);tb=m.bs();idx=m.ad(it2,d);wi=m.sr(m.a(idx,P.WHEEL-1),4);sh=m.sl(idx,4);w=m.ld(wh,wi);head=m.a(m.rr(w,sh),0xFFFF);v=m.r(v,m.sl(head,21));ri=m.sr(q,3);rs=m.sl(q,5);rw=m.ld(rec,ri);m.st(rec,ri,m.x(rw,m.rl(m.x(m.a(m.rr(rw,rs),M32),v),rs)));m.st(wh,wi,m.x(w,m.rl(m.x(head,m.ad(q,1)),sh)));m.be('link',tb,True)
     m.be('l_pair',tl)
    tl=m.bs();live=m.ad(live,1);pw=0;m.o+=1;m.be('l_end',tl)
   tb=m.bs()
   qZ=m.bs()
   if m.jnz(s.QG):
    s.il(cur*32,s.QG,None,s.QZ);s.QG=0;m.o+=1
   m.be('qflush',qZ,True)
   m.be('s2_fl',tb)
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
     fB=m.bs();fZ=full
     fA=m.a(fZ,m.sb(0,fZ));fL=0
     for fK in range(6,3,-1):
      fb=m.ne(m.a(fA,HIGHMASK[fK]),0)
      fL=m.sl(fb,fK)if fK==6 else m.r(fL,m.sl(fb,fK))
     fX=m.sr(fA,fL);fY=m.sb(fX,m.sr(fX,7))
     fL=m.r(fL,m.a(m.rr(C_LOG16,m.ad(fY,m.sl(fY,2))),15))
     m.be('find_lane128',fB,True);low,l=fA,fL
     full=m.x(full,low)
     low2=m.r(low,m.sl(low,128))
     if ppd is None:ppd=m.x(pp,m.rl(pp,128))
     if s.check:assert pp==R[(cur^1)*32]
     if m.jnz(m.a(ppd,low)):
      Z=s.ex((cur^1)*32,0,31,low2,l,'extract32x2')
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
   m.be('s2_out',tb);s.s2=None
   if final!=2:s.bank(None,sv*32)
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
  s.success=False;s.ws(cv);s.gR=None
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
    if go:s.cap(15424,'g9');s.stage2(final=2)
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
  assert out=={"advice_slice_hits":1,"advice_w16_is_g":1,"advice_w17":1,"classes":851,"fibre":1019863230,"fibre_dfs_ops":1944,"fibre_shift":97447904,"g16_fibre_size":2,"g17_fibre_size":1,"groups":188,"ops_per_cand":411,"sample_trail":188,"sample_valid":188,"sample_w16_one_value":1,"sample_w9_shifted":188,"sfs_collision":1}
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
W9C=(BA[8],(BA[9]-S0(BA[8]))&M,(BA[10]-S0(BA[9]))&M,(BA[11]-S0(BA[10])-MAJ(BA[10],BA[9],BA[8]))&M,BA[9]&BA[8],BA[9]^BA[8],(BE[13]-BA[9]-S1(BE[12])-K[9])&M,BE[12],BE[12]^M)
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
K4_NG,K4_NC,K4_NB,K4_IND=188,851,358,50
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
K4_DROP=frozenset([253519481, 253519483, 254830201, 257713641, 257713643, 257713657, 257713659, 257713769, 257713771, 257713785, 257713787, 259024379, 259024489, 259024491, 259024505, 259024507, 320628201, 320628203, 320628217, 320628219, 320628329, 320628331, 320628345, 320628347, 321938939, 321939049, 321939051, 321939065, 321939067, 1327261307, 1331455593, 1331455595, 1331455609, 1331455611, 1332766329, 1332766331, 1394370153, 1394370155, 1394370169, 1394370171, 1395680891, 3478939241, 3478939243, 3478939257, 3478939259, 3480249977, 3480249979, 3541853801, 3541853803, 3541853817, 3541853819, 3543164537])
K4_Q=[g for g in K4_Q if g[0] not in K4_DROP]
pass
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
K4_Q=[(k,c,tuple(Z for Z in B if Z[1]==256)if B[0][1]==256 else(),s)for k,c,B,s in K4_Q]
K4_S[:]=[NM20|l for l in range(256)]
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
K4_SETUP=_k4c.o+2**30+768;K4_T10=s0(BW[10]+K4_DL[10]&M)-s0(BW[10])&M
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
 s.cap(145083,'g11');s.k4q(a0,u)
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
    if not T and i>=21 and not m.jnz(m.a(m.n(acc),LM)):break
   MS.n=nb
   m.o+=9;h=m.a(m.n(acc),LM);s.st['k4q']=s.st.get('k4q',0)+LM.bit_count()
   while m.jnz(h):
    s.cap(145046,'g13')
    lo=m.a(h,m.sb(0,h));h=m.x(h,lo);j=lo.bit_length()-1
    if not isinstance(G,int):
     for e,gi in G:
      m.o+=3
      if j<e:break
     r=K4_Q[gi][0]+tg-u-w&M;m.o+=6
    else:gi=G
    cs=K4_Q[gi][1];m.o+=706;x=sum((q>>j&1)<<b for b,q in enumerate(y));s.st['k4s']=s.st.get('k4s',0)+1
    assert s0(x)==x+r&M;x=x-w&M;w9=BW[9]+BA[5]+K4_HD-a1&M
    pU=m.r(x,W9C[0]);pV=m.a(x,W9C[0]);pP9=m.ad(a1,W9C[1]);pP10=m.ad(x,W9C[2])
    for a3 in cs:
     s.cap(144900,'g14')
     e11=m.ad(a3,W9C[3]);e10=m.sb(pP10,m.x(W9C[4],m.a(a3,W9C[5])));e9=m.sb(pP9,m.r(m.a(a3,pU),pV))
     pw9=m.a(m.sb(m.sb(W9C[6],e9),m.r(m.a(e11,W9C[7]),m.a(e10,W9C[8]))),M)
     if s.check:assert pw9==k4_words(cv,a0,a1,x,a3)[9],'w9 prefilter'
     if m.jne(pw9,w9):continue
     m.o+=563;W=k4_words(cv,a0,a1,x,a3)
     if W[9]!=w9 or expand(W,18)[17]!=tg or not inF(W[10],K4_DL[10],K4_T10):continue
     s.st['k4_w17a']=s.st.get('k4_w17a',0)+1
     if T:break
     for b in cs:
      s.cap(151344,'g15')
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
 a0c0=m.x(a0,cv[0])
 maj0=m.x(a0,m.a(a0c0,m.x(a0,cv[1])))
 e1=s32(m,m.sb(m.ad(cv[2],a1),mS0(m,a0)),maj0);e0=m.ad(a0,s.c[1])
 maj1=m.x(a0,m.a(m.x(a1,a0),a0c0))
 w2b=s32(m,m.sb(m.sb(m.sb(m.sb(m.sb(0,mS0(m,a1)),maj1),cv[5]),mS1(m,e1)),mCH(m,e1,e0,cv[4])),K[2])
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
R_LB=.9420320865863083
K4_DIV=332634742808497727891862043090867/434810569403877151706270838816768000
K4_OPS_PER_CLAW=10061
def k4_budget(cap=WMAX_CAP,r=R_LB):
 b=76093837964208903894824;return b,b*(cap+6)
K4_WIN_EXP={14672896933643966474:(63,1,0,71660,0,0,119765,5843307-258518*V),15921217793420643850:(14,0,0,0,0,0,0,3177615-257031*V),17552297034189817508:(22,0,0,0,0,0,0,7432944-1957500*V),1866586107145425828:(16,0,0,0,0,0,0,3701419-507393*V)}
K4_PASS=200423;K4_PASS_COMPACT=144223;K4_MEM=1043930
assert(len(K4_Q),sum(len(g[1])for g in K4_Q))==(K4_NG,K4_NC)
assert sum(len(g[2])for g in K4_Q)==240 and len(K4_P)==40 and sum(len(z[2])for z in K4_P)==155
assert K4_PASS_COMPACT<=K4_PASS
assert K4_SETUP==1120815998 and table_words()==15520 and K4_MEM<=1<<20
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
 if sd in K4_WIN_EXP:assert t==K4_WIN_EXP[sd]
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
 E=((14784,133,2.6724,1),(0,0,0,0),(0,0,0,0),(0,0,0,0));R=_k4e.__dict__.setdefault('R',[]);R+=[v];d,q,x=[sum(e[j]for e in R)for j in range(3)]
 assert v==E[i]
 if i==0:
  Z=Attack(win=1<<16,seed=sd,check=True,k4=True,screen=1);Z.run_window();L=Z.scr
  assert not Z.skip and k4_scr(Z.cv)<=5 and L and all(c==69+3*(S>5)for S,c in L)and Z.st.get('ddraws',0)==sum(S>5 for S,c in L)
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
 if eid[:9]=="r39-mate-":K4_Q[:]=[];_k4build(_K4C());return exec(lzma.decompress(base64.b85decode(R39M)),{"L":sys.modules[__name__],"Q_":req})
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
 if'--attack'in a:
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
H8_EXP={2600209493401801829:(51,0,0,0,0,5880446-277490*V),10907755097612878284:(54,1,11392,11392,129777664,5662767-275068*V)}
def _h8w(sd):
 A=Attack(win=1<<20,seed=sd,k4=True);A.k4_ib=7;S=[];_stamp(A,S);A.run_window();I=getattr(A,'k4i',{});N=[(I[a,u][0]if(a,u)in I else 0,w)for a,u,w in S]
 v=A.st['claws_distinct'],len(S),sum(n for n,w in N),sum(n for n,w in N if w<=7714620),sum(n*n for n,w in N),A.m.o;assert sd not in H8_EXP or v==H8_EXP[sd];return v
def _h8(i,sd):
 o=_e1(i,sd)
 if i not in H8T:return o
 v=_h8w(sd);R=_h8.__dict__.setdefault('R',[]);R+=[v]
 if len(R)==len(H8T):
  C,F,N=[sum(x[j]for x in R)for j in range(3)];n=len(R);F=max(F,1)
  z=(F-0.0159143*C)/(0.01829*C)**.5,(N/F-39790.0)/(525074370.0/F+1202.0)**.5
  assert max(map(abs,z))<=3,('h8band',z,R)
 o.update(zip(('h8_C','h8_F','h8_N4','h8_Y4','h8_Q4','h8_ops'),v));return o
R39M=b'{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;5#!K+g$)On@VT6Qap3_!89yu@y5)oxa5jgy0FtI1T_5w6&^Iq^MTRT8*z>ZB^kMUA&J1!Hw85prz<%Aq2K|D)Qif7BJi5yT*d>9T5f1<Y@K>ce+CWx&Vs@14OPR=f&hR04S%Mano*-*Q1S|r^J%Vr)j=PBEH4t0E}%ir!O7IghwTPXJ~g1+mf$$}n)r~y==!z%RxT*;%M|x~O#SVpq!LjHv=)UsON^=yi6oLSYrjY1x<CE!qe|7Bb@A8`B^wwfb>Sx{+0dD>GOQiTm@)d8hzsrz&b@W1GWL!KSas;vrd3q(HqoUe{2!0?y3DwvOZkp9$%dxF=(@_bBFM+2D&{3L8;MF38kKpn58SRg)r<{px~X-^FYcQqIkMy{Ke1@4=sLuOVNrN--VU$Yoa_@Aqda-10SW5GSKxX$kzY~p`x%007N}b@VhOrdl-S*au=`t%eqQx%cn$^k9E)JTABIB+rvv9~1`<UPa%t^|v@H8bKbwusmNco3J9l5kl6Bp4s6nD^+-t?-6@-W=ty4PmY2tRFx<N<C0la4~jX`d^+aE<klwxE*;Jq3I){(>k=kSXxuWy_BKK|2cvRFC>VUdZ9@UfhF#+?Ern_NL+Jsn^=>I^BCQAK*K?j`qqHL19neeW5Y*)i~04#W^Cr`L?lGzzAe$<lCQwK+;Fdo=u31ZUNm<F)^31QkS=IZuAFTz;@qk%OTN4$$rC0z>LU>uy?II=v_dvZVI&v0uF?eb_Y=M2|I)`n99x6$n8e9*>Lc7fF9A(D!F1DtF0v^b0*22G!Q#6^`;d4hfdaL-Nw&J=+Cg2ORNKa8YPh7lluR17tsHtOX8u`rx}JxdrE@Y0m+njNqy#P6n)7Ngen&tq~N3iZ{)a&cRe>w#aKD>Wns|SqjeC^|VATg`QhP6d?XlaC~o=X5(<>xV?}3?CFqkT&PGzFaShK{y<!ax5}_gvajC3o_QWl4l>hHDb+Tcex3Y9l~CJF4vIc!=_hDcaeg=D5<86VIFM~dBQiwZgV{sOABY2Do7Es#-LqSZ<1c^G$ST%%?+)sX-Dkhj)=mrI$b0kcL^TvoGB-Xc1Pzzl$Fla74CAdUMeWC@F_n9Umg=8OSaOlxqj<QHIcLfe={uK|Acw09Jx@Hzh-QhU|NRgawNa@n$)NdlT7m$QhKq`Zx5dHIPA#IAyre5E73s;{RMAIxTuI0l798y6>rbKN(Q|$Ms-dRN=lO!q4m~Jo$mM~B$-h{42f~4Yg?;U)4>wj<B2zayqI3Ah3BK<Mv#HFo>Gn+Rw$7$lDsL<S57|yL6W;h2*h?l}*3<->MJ7H4Qk1b-;~=oIChx%;C>=mdwv2b)R=E^)<R#5{Ni_uFl{q!OHKDD$KhD<s#k<>boKE8;Hm&g5gldri*lF+H`QrHd#9W7UQ85Jrx~Rc6B*MB@t_cI-PK{0Ps=w?m@?u*PksoCMj5#A}8yWOIjxJC2X#n8bz$l+ft<wCQ=I`E$)_T6nFh!G{!N1($L+^ssV{xvfS&@c^YJ~EImlv9Q6J{ife0H&dQMju*A))*IP3x1V!yro37l6e3mb^$mO4KRg&D5~%K~R#MW|vW)*>BcRg1yaxWkUk{9V9ExWW91}YGn51fvqd{uUZlHXnv}(DcgkDms;FQ35!(B^6003LZIFoe;xL`W%Q|rQ0`LEEwU(Z5RoubwBL1Ynu&`+Qk+_S7|g`){!$!dLAZco{HP*R&fv??C)BdnDRu?d3(Y(w5K^V_AUd<D6ZHdR1a%*0dcJnvU4i*wDG0`Z6ybt`44ZD64URG&956yj|KN|YMg>JUaB)s8e1#-C2B#(a)K_4d8+J7Ji?o>{uQ>@Io}EF?`xrFD+?pP5>_>F$e@qYG*1;A4(98Ww&`FS}Mz~T*J9x(MgHKpb6;F1jEfuw4RvXqPOZyLjX7$8I#O7d$;(cKt!Qq<AXn0vVkavuiQ!X5DbfEV3Uj?Ah>Y?H6TYCtB)ut633(VB1(VzY2PPsQSAM29xA+pYwv4m}e<Q5Ig*gbQKo#ltjgG5+x`LH@GHPDW3u)MyH&fUps7UtfJOC7zw`R6UQZx|-7D+p7!`0!vK>lejk|1N(Q<8y7<Fh&4`Qd*Ln!f~9PU{^7ktXAJNKxa*WsbM7x{V+oscOIaj;6C>UcX?eS2|ESyg3lTD0b*K-<SXPem2b8gz1Bz3m2A7^a1~zsLl1~F?hFdtBsN{uO_|Xa)V3zl3WE^d!F?EkS5W?~TP=i}e848Ttvm*)7yWXj@^xxHPs4X~&gYYdt$3x({Am62UFB0v(*W{yJ@(eE33J-h;0zl>Ro-usSEE%ZD~~<;pJo+&rvN}9fmgAJUaKK`MnspxLLARCCw7eq%@QnZ(RPt*dU78s?;&!<kz~#UDLy|UBUzjZqp+Inhh%G4N2561(<AEWYX{-P%s-q?ZiR1AwA23UuMlH*$7?}+lOBwvJI}D%dg+-{i?1qF{sl;#=DUHiGO1$hHnuQ=r@yFWw^yjm{&6S~3Ssp~3nr91ZzWfl4CS6OqRX~|QhVBBdgC=KGTGF-J%h$S$R3Om{zYgIOF;C>Ohk5vNr}8<&^u3CkRLSyBPv5~9@0HTIO6~h2Lv6mJRm0(LH9ddnqSCmD{HAa`cF+$(sUvNapHGFyMR#Nm5{i^3w+i73g)rxBR6ek=n(JuH;@_0|87em8a`o9dgj}=m*4^WLt>^X6!DzZ-wf_FrMZxk|K;byy+r}6$FyLtq6cW<l^J)pB{SUsW7Hn((xx4AjUwV#t1}kQG&O|ds_dM3*<-|+SaKyr17neP?x2JmI)*3DQpzo_M#L3m5^(F$ssR5KD=)yk3;~WV6^{i;?Ez&yJSIW)fr>|B_LY(Ei@YN76b7$Z&nR)8zDD2ruu%}&_6MZi(jFmqYszB*{oAyO@Iz=&0-JHEH_lO|GB76pGOFL|vt=P4YF#yZBMFi6qTRSmNvHAJ3TMPYursZpn42<pH|&+R13h=mai_>O6(woOB+VoOlq#5hzLJc7NFE5pm@OPvXTz`^;5}p!Rw?p)NF=z8F4l=0grsz0ku+zq>=MwKFdM=l<Q{A|C<>H_g_Z$g4c5_29vMquNTp`O#atyU>=?3r_?a7_Uc@#LBz#a>|C);822i&u&t5g5wu_=7nWR-OZoPr7HtUK9(8pZYP}$QmxidS?i@m(I<ntanIHZ>s@W)gV<DqE)?~`z#B(1n!?tt9nx^r0R5rRaDrbTQ_um6?eit6r}D2h1E=7>U>AB05dXpQ(vNZ>ITX<=gzuxjOazR=jmji%9~&xX(@arZ91r~5kd;`a5(?~zR%7l0cXe_;Y${u3`dBp6|6Lr+xfejX?dJn(roFtNlec41%pe*m}{jGH*_clWxBI4<baO|kKP8lYcxwX{%^S^=<tad%TQo*^GFV5JJ;?9q0?+pT|vG6W;_5e`h7CuCZUEyf~Mrp%+-=zhE3bq<%>P1C##C@{tL<rPEXD4_7t+mvTQ&I_`RZqZcS%ME|Yfx7bD1>k>yyyJP$j7{$9FVxI0x?=wYPIpdbZ2d^7ZUf*RJcxfHckFWjDR(uf?S0@8Q8WPR|FZ4}t-~%eTy=neCnV)otG}tvefHK0>z(J&1c)hl{c?hP^ADCzov_ceygXxrp7?;gKzbfDXbx>hXE+kH=i7(mNDLhIu&9_*Qv4*d<GAz!pG=_J0$|8k3^7{VxwB!|wFIC~s-yGO4=y~<_DTdudIH5(5bJ9TV63YY{*Z2Ez>S2zodec%qD%%C&p96oQ*r{Phr8Ek4L3~H?3#<Y&w7+lTwXI0-sF0Oo03136#cTUt-Znf(TJ~+V<Ry`gr{;Q#<J>RIl5r|#JZ2`ZF#f5Bjy?^x>VxbSuG+rZlWCH7sMY<&CJ7WEEHdA>iB;9ARX;bn}AehkX^=)wuGkHan1(!uy!es@1buI-Ntsd16m>OR)GF)*Gc+NakJv(GV5|ji$WTDwm?40xuyA8knQXwx)*H)Up_fX#0=<M*yJdT-5tH`Jjbvcol=gPLR(j9W=w6k*q0%e9D4z9L%HbZrbs8hL6%Bm8>!d9quf6pm{dCR?e;^kY^fjE{Jv`LQ@O~#VA?<_oB+n4rr@iIQZKl&PoL6nc{sKJ{<hf1g*=KWJyLGwfa`dL>^B=30*V+nqtO+tX0br-eTqzueSY3$;GYOw7=3jL7lC?bvdRr5`V-v07J>Toi=j1@f9CEQ-0bKL`{m>+r@#3*^HuDdwpmaK1RXHVC23Tz4rZa*6%93*yc1SB80uIoTHvimp89+%ZXU_Q0<t7y9Yk{k?e&g8@Yhmvp;EYr(KGMdXJBPf=6bvmN!!MkbrzEw5=U0;tt*DL&=Ok1<1=>m^_&~fGermnMFbzAV%Rm><!yr@8$St1WN5ree<LpArP4xa#VGTv&jn&V9=XK+c=>iA^iCEjcI^wBWR|romz-3wLFshxLPeiic_rjQx-<qU{Z^v4o{4h}(XZllk@a0Hnw$9!>-+tN6`>^(knF{_>zJZ$Fn@Ke-H+>sV|D;LJ38-+GBJQOgY=X?bf`Dd%&!w$#k`I4i{;~8Uw#}Tq{jeBDrS!z%XOny^X~ze81Sg=PY^5JVFf8&k|zi{*r%i4{hW}dxiPL$ZXSGznt1UkvTgf;l>wv@uCv;TBm4yE6Gk)&oOLSn>$*mgnKU*QB6k@+S<xs599-C{uc+2ORhF9B)|qTPN?L7#WDMX%>EKkI%_P)OW<Q*833S}nSdp=UK#9PP`4G$=8`X2=BMo?x00kf9;1UuxC%t_XxA71G2>8#&w*KQTt!BW*P{-qvuJlQcWl2I31iasN7cwzK=6O)z$XUt)ZaMwA#nQ;L0zhycU!xgb#@aO*=AT+g#{m_6Y^`EC<8fNKqg^x^^0uZtvJQ3RS$s&y6rr3b=xJy64fPPmeS=%H>3e%jif^syWgL!})a@>Hy&V;ft<tj%e4*e3<1(i<Jc(zA_hO9}>!Es(_yD*R@h0m(HEJlhEiPnk+KRGEZQrhS(d=cYUvFIv3`j)IVjX?2==U~iiEEedST({+bfeJEXw+57E*z-4`B<el-K-)<?qh#BpFY9v6Oaazs()i;RG=Aq+>bixaWAUB{|g#qP_is1X|qJ1mM7<Fus4AiW?$3dueNC!vRJ0%575mtjsj{-{DCGFC50zU7@<fs){uz;1RqJfQXx-!V{=5_wen03P1G`V&vVm}yn1XO5UQH7*aeBKQ6;oK`3Ubon3D6&Z(A>HUZK7r(JCBVERu#$YwymHVv|^ksuRL`Az_Ky&cPTx)SyC3aP>V6JS@iDX+?a})6;xMy^OnB=Xn!MyJ4e_@n<%}Z#j)@qqmU$)g`WZmG$xrhdw9i%^`iJO_-(rSG%L3ku2T=$vmM2qFVo-v@|ao7J*<HdJ$YU`91cf7m*?pzIKo*&dpQ51N??69U*l{u+FQ|f8}8((v&L^492<sqlG4EL`V|%>$%M0CP#}8hjjQDylgfc=<UiH;Y8SRBM*U|K<pm0zI~%k5b@*x32u(chL0wxL<HP}1r04|!hYkNzUE<UUz(S50@FgrpS-uko8qcJd|yt8_N@S|xc%vh@7@29(AS-99~6n#k3w~;Ua}rK6_6uX{rV+$``d*O0_Cl|4T|=O9!_)}^@Hjcw6wxIOw8V7bHYJy@+9WVgIMxKIgf=Oiml%S>A@st*`2!S_3Uv<gP4yUpFe!@iO~y4JZRz5>W$POzITf^906f;zv%sZ&K5`602>#27K0@|WUwp-PqqP}L82&D5P9HJYRvE8o_mPnh4E`4kG}!<Y)t7#c91>-H@+^J;;sAQr>wi3TtN*Tn4OKIeRkO0PaO+PePZ};j^YFn=i2~p1t2lV>5QJ|*RHuT>58v&U7y<qrU9@H1oR9m2NQefalG$8W-S&5POXm_2j|h{ycI$zf>wU@h&wd*&1#AU=5)$m+ryFs$?sZTW{P(%CARcFl+Amp2`3=z5H#Vd;9;T?xJ*eF3Ei+GUqfB@?U&ZD%De+V#)JN-|9>)O*Qcl^5KZ8+pwHu-1A<C(AC6Yfjn3m#xfK1s!P>f<1KGE!rYB`s#j!r3HPRQl7<B^A#scN^S#&5NUwMhzxNZkFljBMox7x*g8bsTAR~;2VhFc#SgM}8L%Q8-Ol^kNsph#!6J=irJM7xmuaV+QNQS;0u{TOM$)zKkvR29#VYm##sZfW<=3}a@gnB=V?8z4@#S!ir$XE<<xQ?|YAeSK#mU>*223A9iZQNi%yW5;wqUNexbr{Tc*_pGZLR&2mo<Yr}{_*j~8EVhpFi*=%t2{hDQ+ujsnF~VMKH)`wU+RTz_YT1Y9l?G)ffh(oho|vP=Uu7$n`>kqNqotX%W_Gewj2v$zltv+1Lx4OF$R1S@1zjbS89)9<(gF3y5yHp%_FINZ#Ff<ne{>)I)B?3f^(O~7kiYDu6Bk;)4QTe#sPvw}mDk7-Ko8x5)+}W#;JNXCtVxb4L{XJ~4Ll>`g3zyk4}nb3D}k-rt}2Ms1XMiA!lNu$&F%@pOa(v;Q+WO=nZRpg!taZ&ggPe=#yURg!VQKYsf9*hv@+h>`3-!PL=)j2p6;ehom&;0xD6mKAz{CPb4r*v`sS<1NTS?aB{!{=JK8|z8Tp+~jXf0WGN&yAbyYJUW7olwB}xl=CRQ|OD%jIAPb7>Sm9v0GCAXIjq_H=8m^x;NLaum1F%ZzJ`=pzO3q!C<9Hl$xQO62-a*g`;;qbAczb1WY_(t1FS->w5a#r;zK}gv%H(}{N!d9DMOS}YEUUfU`_ADv9s6Ue7eo<p(ZA|MnO0y%XlG{R@C=8$L%(ixHcI7MA_T#c$@-w_gDos^>l{N31M~P{@l^#Wt&(dJCI2f^EmSmmH$avi@lNG0;Mg72>^{sQnsji=soumS%dpK_|slm0*F*x!|kRF~CtZDs*>V%rRTZTP(@$#ie&8eTIF;lC<Yd<Vi+juf2k#s7=%NJbE0`CMY_?>G5B^{!SsFB3LlsHUnkf<6r`f7XMGj2>fOzE!aH0{FfA#FSb7Lk?F)}Ea;@uX~2lOtpXsI9)di{SYxa1KaDWik$`#5TDxI8kdNzF%m?S#d>X??mj*6Q&3wOXi-LBuVVVu-fvn`B_SHb?<*G6Z9BGrR|}nRPw}1wb=zvjMOVMn0(*n?9vA8&s%&+(4hD#kFjh>v8PCWR_}*3yB-W|pzUb`z+C{kK-%1>mf73yZV3<I{WoRgz=6qX?_HPud8LQQ{qM!2`#k%C=e9XCfCiL~@lQ?*K;%cbbIZGNt(c&5xC(WkA~x#@_{{??btHeNZZ&{btTmhCzuOlhOir7Kizt54`!q6>EpYB}<1uiGhuh_i+fu}AG&!i3PMe0HsXiDu{FH_eZDl#wJpnS3jt;8HQrrka-fK;~G;pv>e{8xl--xhS+}2nh#d;uVs%rse(W)*^O+AmswFSyP*w6WNAE%HB7eap_A)5#a#8>7StS~gd6sA*70u!1z+M5q>`sw7&0T+;<QTQ&vnFIip`~>{)F%fjl&q-=lp1&dV(k96BVcS5lYN~~gS62M0;+rZ6TS+lS9QbjLy~J#j+Yq*oA`qxW!<}qW?Q$M+k3H``zixUlcb6E%NZnyocxh(yvpe;;9djusmDi=(35aQelvrEUMkwy0jVk|+7{A1&PE16F5v5y)QeB!h|IKb5W`C?Cr@i%vspCuS&oVu8Zia8uj1$}D)KOAR$=}QIa7nL={G1)wfV^Lq?v8GcD;j;nNMp84!`YQH>Kbv(@3bSST$%h?RL!6{#P#Tfxs&kzlwhQZk*m*@XM1W+X<=67@Gh)AA`Q%b7!#5H;Jy}19oNOMk&YmuAL`)$BZV{|xQQe2i@#W&hRDSKMwnuzR;o$wVBfFSA2<Pdj(pl`Vw}n#*#^RF>ns^v+hyJ#tQi8HA@=Q>VjtBpU?YJ2)d9xV@|W*{F><W4{YAh#ltEw7%mAO|ec?QUi`Z;9g5}~UzCLtObVuG3ymxaJiqSxU+9AyGJYrB-NPBaf4JKQml6#*~>5&)eLH+b7xn=}#up@%C?9Q|+AzL*T(=2&8xoTJM+#6dMsBPfA)=OZcScI2?ieQ0&4D%c^r>gj6bCVbuYRqDGibK#Q(fM;+SwCf312StHCY4(}*GsVq=pcDvX2_)xS0s{;wRvRU*%XZP-=A^MG@z4Wu3D*WhbEWV^Vavbnn^a+^b@}_x;`YI=LB=;Wg9n2KMZwDRSF|9d;}$z)akM3sXD9AAH|kTJ#O;ThrWcUtUn_X`Dd#;J1)o0)8SJj2BlzAx`VzAgPB@k_$K3>pfwIEQ#~no%ub{ZxS3J@`v@-2CxLI!L_&c_KJv?II!~HrhV&dFdFR|WuC!G?25oRX8?>`h{P&^#HX47llroJ+vie2eRD6zuCULv1Co7UT;gGVPH0%9SuN6Q|eikwRs6arhdBc(=rh$@ee`pegM!Q43G<!@9sTuM7D-_(RA~Uo57ALa}%sd_$0NYe7p5E3q;wE8DOGPO^W#aRHt;&-<Wcioxxyjd9Lb#QZKQ3KUy%^ymi4AUDF3(7*jg!IO(}ynaYXR>34<IY_OK3)v9$tXhhQnLZ?e>6UfGS;PKWis)9V3yFB6^%21ch|3&#QlA6VD)Rt2J!^mLTd<kuw!Ne?y5+m;q~f%zNM@AS83eapIqPh;%oWn3m0)T9x;FJ1!sHb!@c%b;T{()or1-R6UmGiVkDF04m>oS~pL5=4aupQ3fPhoU`WNIWKi2C%)VTF#Y|HZ8e)Q&AY3>E|DvvK_8*no59<}TaZCwer(88D=y_}-ExFM;%<T<CIA2cF1>+1x`UW?00H+kv~~ahr3Y_dvBYQl0ssI200dcD'
if __name__=="__main__":
 main()
