import sys,json,hashlib;from fractions import Fraction;from math import isqrt,log,log2,log1p,exp,comb;M32=0xFFFFFFFF;ROUNDS=48;UNIT=3568;LANES,ALL=256,(1<<256)- 1;GEN_C=__import__('lzma').decompress(__import__('base64').b85decode(b'004jh0RR90|NsC0{{T858!d0jQZrb3P7)k4DI%(Oj+|@K7dSX7T-$63AYF;40PN=F>p5)antOQ#kXMB}a?+8W*2vE}wGJ<l?_rXL)vM5GM1I|}`QDm69W9Sk6}ZpB(;jpNW~0X?&Tn8P`DwFP{<mxcF#KE5xAtxvBQ+~rC#KYKQYpX9(3B%h^Xw?9^TEow@b3~5nzuP1fqHyh$FOu=0Y-2n`a7V`K%{y#vWereugF(kZa`ZTE8{~@Y1N-{ToCvi^<{24fctGvfW*1{lTAV&P^+Q~*3(Q|uPmDcj9W>i_|WYs^qdCUu{NJDUZ{|17fi%%4dlP;Q8E%az7m1?p`IWRM<CgA_;%WmH@VUg-)<Aq)-PR`?ZAaiEJZIt8V+-R<|o)2&?#}bjMPFnQ@+B)iIP$i^7(RLTv9=_O<AtLC9ds!9W+&;v&yNw{V*k8(mTuU#FTx969>;$?7o)jeX0a+%s*vlFVr6s!4B}!sG%)nj&aaRF(P?{#W{?pbyoKZamcdvy*(CZZ2vo=K_b8z_&dg(bEF&Nl9US6CB;(@KliVommj86#bbnTgmTJ=zEq+FQ3Ebw&*Q)Sn?zin-bh$?3cA39^2&xRUNQ~qJETnE;ZFvNq#Ul73$4q`EoIo`ch&dQeG9B0A?*nZ+is$myrrIkv{tp`$e1n38YbL3FK!>E$&Ogl0ngk~BY^`+ukBoaRr1LzdMK`m?s83dxm7BZ!VLWkL7)~v|2)l)doLvz%t9}ZDP_f$zL06H@PCr{SSH~>4YSJ?C*Z1jGYDTpTnR3<c`~BPn8Bdnaz#VFMV_(v1C^iwW9M;gJqJ2Hr8(J;)L85XAw4E%>`i)`^e?nB9@j3$Pwb-!I{t&JmPstD3VR=RgF*7!2F7i>F_O6l!I$}XKA32fAG%`*{4$K`M9-+nj~TiM1v%o@%8!5d9DrG%g(U~jgK~ju!x#8f-?in25<fq!)AaWS?zw5@K$`|80Xp-%p59~{(j}-j@TSgd`PvouzIjG?FIcRM4nF6S-1otQsZOOC;7V0`e)MX;a7*ZL(QhqtO|l0M^BP|Ika!-ki~y(yBNWP8yBq)*rY)DZXcLC+;=*Y>*bPIqy1jTyR4Od6Sbo|}@m_}&8&r}mmN{lG<(+|-G;I>oEm->0qtT6*TD(*oS4g}(Ffl}@K5na7xSb;jC)+-7(UQC6S0capeNOQEky_21$4f)F1+4X&_!-{B{r{#mIwp);C-GC|Y6f-t*uL30;7twB4%Wu!vG^=i4N#LZL{07bqN7#ZyIAPb5iM)ufW$OTgnXQyheB7EB#2?ZuM1@BZ7sO=fahuvg?H_<jPcedou>V4e?dq(2!F5*4%uoR43PVjPG1o9=38nS)!#t>Kf9dJl=hcB^};IZjXkEwGV_<8_&v&6Sm1;5a6n{ea(S9`Mq2?EXz7FT0f~c~eTc1$+>-w-d<erM<nY-CA;nlCEMm$?e``&eJs&RWqZ-YDV3Z#gWjU9B-+TwEpM&MFG#0$nUJYLU)-sJobze9wLip(*L+5G?<8ku@Hw4mL{otC2E5{$}m@yscgI(9JWt7Z(AnAYUFzy9kf=D4Zi0rd0Q24}zdcp-~NEN>kXFsAAB<2=vyq?;01;v-PTx(E7$hR~^;!ieC^*_%6D`2w3EkZDzj35aVNs#;Zkz=jP{Y|Uh;R=~c$o5%=PNHW}tZ1=USF^vlWfjy*(R3eFK&{weWj-<0j2h&8F7DtmK7gCglU<>rjG^#UIY&%uJ>*p<uZmJcqF-8q)M!fTj3MLDA!OHuY-FLZl+(U4B`i+83jz3KqwmlWj~L51G$VmY>rQd(dNSatVN-Gs!vSuX5pe)PQE!~n>_&W~sovD4@MV!4WL)Bl>n^(R#I7Sa@8*JUbUFZn5UKqgn*Pq^yPuVh6TUOJn>O4BpT#;7Xvd(##J6BL_f6iG@K%fFo0b9=)ULk)aup~SWNVS_qf{-`C#(&$U};03vJr`Q^L$Ds!RJ>ZbQcB%L?^-k%5mEnWtd|}#hV-YG%KSTp8gx9Q!h`W0h_XDu=PDIhi%RXM|8~oOqX#}xee5rotqBfAASJ;QdtvX`qXmIt<Df+i2vf57rp5H?_y+eLCXGp51JJysoJM~%%(rUkhQ)%!iilrwzo8=!#;>~zL!IVf(i%fi*y4K2YgN86j;1M?Xsik8xG!LUnVReZ9<F1LV3gK2vvcj(vgTKfdhSr*!qpgdx<!dvVKg;=FXQa6u!Verf<aeR;oZmb1DI;SeBktT@7)^g4{k<=?Y<-PupMS$dVAD&UQLAJSZUwFNKj)z;5}Eqc_X!CO~80g}vSf59x@ZH=ooroC?o(_$)P&;w=SC%(EfpQiCftKpk8!s+=@=+Dv-Jf7l$W_SU5>WU?n-Yfq=q9C~y{OIO)w1?(smSWxGD4>BJ?HY4hSmaG3j86=OH9cSN4WN2&r)we?UK*O{iY>25Kg*$!_uw-%oj*_-E=<oy;vLKb}D8paea2(uDwE0Emx~oz4P@sg+`<aj;2VD^QO1fAylI_{?-Vd)34u1CL%jf=<5)7$H{9Q{iF4Oi!9G|U`jyMo{0j2(+z30l1I1F;p=AqGA2yX0&AyqtxYT)B@k6bMz(OK++3`>5423GZMt8u}QbvaWMv&+IB;&2jI2IP2~;DBd>s9!7iMQN47yv|#@**Zo^%13T#+bp}~KhT$v#F+cAM*vycwlLs8_S}hX4LPtEFlUE4hXN}UL50J#6y1atu1vCW{hX<a=>1LTh?(L?Nb2F=HC|{t(8;PuPfmaJIql%zPFro%P|aldFjdujwhauzDhcY&>@|AXV#)bM1uq$-0Y>eKBS0?a3dv)^Iyqb-Myl;`q58cOXJLx0A;`4tE91yJur~|Kfa@;>TH|SL&5s1u4dXsKT>Jo0ws_t9vap3GnC<RxJflixzS(ABSeB03E=6A(Jr(q^`mni#Z2TN>Cj}>Qv@6Pr&UY4QY?D1_1n&T0l;84Lr=-7@&c_a}?}nBVf^sJK^0D|Q+=hgmV7$V3`j8MFjNURJb)`1bxfGvt@W#KPLz{+};1;47IA197$5fDy;Wv*g1AWByerKf&R4aVSCU5|IYQ?Fj&_JpvF>47ig0msbZWeM1vInd*-&}KuCDpUuJAV@UXK1tOqWQoknw<xtYkL=6`7k$psEY@5e6-$PvqHrY@syHPGRs(bJYWsa**q%?V%=kt)K{=xnhD)9kmNBn6?;s2<W+g@)z->lokc@qmRx#E9r_H$aPUKtth>jzj-MEt^I{`Ya~?u;+%C-*Ay8trdkX6+o{WdbRtAsKG1s=N6ZJb*<-m`eaIW^0JKg<5%*eFneOPnuLtGc9{-efB2iZ+QeD>SFzBaQ+*YuJbG8$xS+^ki1RK1htK)5GKL#mn+HAd1e>K7cuW2OpAPz)R{vKY4ACIE_`-*p!Q$t4sASG0p5Q&1H_WvsrIp<(AQ*2eRcC*T$AyI^vtLY(MW9Ov0^^G9k-HgU#w_oy~;ufqpb0Hsn~G4$FP;WHE@Rw%93BiOhTqGmmdiUk74fPTs@Qst=)QG>6S4fx!-m5eDJR^Owt=cYqLpfT*`X;QBYocaKj34lEEmM4Ldq-HnE1_cId#JAA{;ocBW#+en=_t`>xi8nBY?ow*KB8nH&v^lA&rhWE6I5y2db64~e@t<5idzbE6#S>Zalo2$-;I8l!mQX`8-idZfzz}6%I=bK@PxwsNyAVaw47VUu&U)wFJM9w?WdmKMf!%1%AQXR&2*xOjt=tloNsdW)yRtUPsvjI62<(A>Kf%**aVe_GD=xZdX0jqf?VW4uq8FeZ`JIm)p@~sM;yq5q{8s(mO{eG7IGQrXpr$Z`PAmIFKkY`DCq;I+FN5fnpG<xrsKDg$;~^;T$X|}tUisH>X(2AYLPwJs4<mq!EV1!QrlMcEl#z9=6@J(loGqPDn3dp5)3D`N<+mBY_^D{to4slC?t&ucDCi(0%Jwu+;2p3zronxFfp&ft;BM8pv&T5hTUe0c!MH<lUIv=lg7QdjRO&L_bEZ?wlF62Xm|S-?ZglZdP+pEB7gV(rZy0ur4>se^Q9JfX^kn_FW2Bg#;^vrQJnexf5u>NHBko#@*cLmat0X7*29{q!)VReP-bE*=bCJ1#Z{PAPB#@+`Dk{j9dD4|OpBYIfn^rt(AWYzJCC4HRvvK;(1y@81Ch0A}xQ;tTBQN2yYO@1W0WS;j?F=FXR3TCc#YT`HcC4)!ns~}VM*Mw^4k^biNv&Jf_UyWGek$qxARCB)^*(e&qFtgJF2@$($HDSggMaaS1yC{~`~{BTA_0;sTy0_73&PWQ_9eFFac#teK@Wj66X+-12tHbks<|w^-A@j5J&Qgxa!6#g1sK|5Hzq1J@mC29t!`~JYxIMk#t1(HA3fyk+t&8q+-RJWUf&*BdLRo<j?;4YGr#*}I`8-_8YCT27)T!hYHgqVFgxK9Hg2FM-#6nhzB`+zd5o(XzOM1mjU{3+fYaQc_la6s_6i`r4#eaR{8%)Wq0L58=8$jodu_}yckX2+qS<jzvR9*=PJ7e;jeq72=nOOpwo2jr?h8PyGSK$JDW=DKm#I(;<CkA&D!%N~20F?$ARh{M8FYEOUXJpwrRS*cl}mbsh?ba`KO0;ZW?wk(w(qw%#5HJSQFQ#4db@}vrq+t-8+|v%ogLpRv+cRq?H=aGDF;nFZO5LWdwRhHtd9TmpqX=y>L=cysIFIh>ovN#R@8Sh+&<$WX3g-Iv@JGRL0%4%`bP7!_?f3CCJDjFq!j!L7fYRISZ;A0BKHv?*9fx)od%lr*Ygv<7I<pBqz}t-g@)tqks9RA-tww)5nm3@Os91EhjA-*hA~QLoyjxJ@b<Wss2ja*0%pl72)5SNjIf8tBr(hCSo(Gm9VVwh{=VMUgrj@;v?ih&KtfCyJ&_|AqSexCgq`u-zh-gtGN}RF&f;Nx5U7vrCHpDuYRu?bf*DsnzqSKcQZ}uZO_XMRn5DocrMRe5FNb-x4U&|XGKye>K9en6_#zRw5#O@0YM-(4AY=PVF-k>!0@|Ey0-M1!IF=2eI|g$asKGM=J(~QRj=@91L9nW*>EQa@#HtjZjzf^S((oUqU0|Y>min!jTCV8~d9k($)Ci_qqE!AqJE)WbK?);ke*&<!)k61NlfZK$d~|9Gykt3qi+BO!Hy_;YcnUn>lYvYcql4~F#LsQWx{<m+kkz7k4O%cU2?;02;YE5z`wJF|bH8B&*XWD;f@r>>$b6!Xp_I}zhuDofsh`AkKwS+(3aYa(K)Qs6ovH!}09c+8O-}B?Ki5?g^dU7KS0ZF4Jcq`E{mTKk(T9ejf6^}P4>T3|wz70N_%=lC*QRm{Cpy%s-R3p=uW6CudL;KA_4^Qq6OZ4jX_>U>U;1S+uB#<hO5R7By;#?P$hMVs26BW*#(?1=a5nuiY@pV!Ana*UT)cw)FgzS@)c?4zbIR&eZta^9tVi?H=~W)k39oLM++9cSAuI>z-NR)a?a@Fj)US*-{1@E(0E$-D^P$gV{XwkmtVeM&M)pHjNY%Ic@+3O?VVhuK&#;RY&7L{Nx~6x339pbPbeJv7*f=tavZM^(-$*8Kuyo+K>XvswurpfZRetD5w}OFri4CZ}z1b^vfb7s+U(Tq7T@N^NZ+L^)!!EOo{?>f}?<Bo`q*Lo8sBJXeMmmIM&qBT8&t&Ohw|^bogomlKr&5-u6E}tn(YK|GRbn9xNL2U`VD5463q^A8_~-<^GXAWFC!i#R>OVNdoJ3{Ov!s<&MTj>)6<pz_UNQ#vk1$gQZ1B^p%XDtTT$cQ_vgSZ(Lc-mGo#wst`{}A!F<;2{kdGW^t~lbfPP#?j@n|C#AqAP0wm}D*5RX%R3KY{e<`{3Q=#8y>!WDwo=L?^}eTMJIz;6=Uw@UDE-PaLk+7&ed=F<zi-S44mQ$vNH7;rNPV5fs!osqnFhT%1!vvL)2gT#UHiVt2zkQ>50O-BF86Sqq%6vS6CLWp=6e46AeDaKlX#|*lZQNdS6fP?R{-WKj|$Y5!mEpR8*vpyfS#YiqpqVzEBwjQT2CY&wmi%~_j2P2*z3`&Z<RQ>l=luM8z@J{mp{c(_?vf{rCD9@Wunni|!j7?U9%=Nu^b>)|>8xkbYHZz7UJj5(wrn(h-F6)!noH&e`&P(rY^UQyH30#WW%VXiuwGH}BJXuZgh317uE@(jS?-d1vCHRGFiPqP7k(X=s){B^;YH2L!JsJqBsrK@9t?4R!NC=0pWJ4c&cLSJVxIu;QIHByr1vQ?7UP!!H%dx?2X*r;r-<@4ao|r0B&6}lj!NQ_lNkRt>yhZA$EDaozr9d1qFO~<w_bLeb=F02x-WcNEAl;@!LZbUlJw_mK<K8jM=1DYncw^Vz!j&K*yx<(Gqrl>&I11~>K~Ikjq>nljK%xY*W%(MOm-l|$T~|i#SPL~xdjzguLDIi0qP2xBRu+>Ca_;arg=M;G{?oIAu0TS|&3vFtB5bxcZ$>^ncNW(<d*rGS|D=#PaypFV)GgX=nQ!qC<};*0N58pyGFGkd65SPlwe*wK-J&rHx+7eUj6D~8$9Hn1TWH8z3}7{(tTWn2bsPhN;iGjQ2dqy5+d?F?()<%8F*KrUJO-gw!!!jdICvFB$9DFobk>(*K<`VgGi+psne*Usl4qztARPDiep;DMzS2zrSLuZf{+Zq-MwV2(?qhMj{Zi8MHvUlpwEL>ao~MdXO{@$s&YQeIvx!ycD(Gpl%){aQA&ET~4D#_gMQxIA?f=;P;m6=URWDqkHr*j}M<7fwZmO)RTWWpWPtC&i1<X1Rgvi{u_*GPy#5>gC$Pi3u)9xJ3ZQIMYd0XwpOD`SUcJdOf1@dkL&3x-N+6uyW7lUeQZDc5)I!+8Z$;L=e>eC;$p%-%7uUij8-jD~N;QeAA>|tg|#L_7C-}FPG(Z@4Al-ir2V8X!xKV~-OPl5)cwYPuz`ez{9SbkNt`~rL;lrzdEh4O);HLj`#n-ZSOnKLgO+eyQxa%`3|vcT7NtE^-l``~8RWcd)F4y-9}Y?=J6Xcd`d{l95by3Re_cBd-w<fBEmv~h=z0ld|ENE6+M1;PRrZN8e3sDxrYA)dwnRv)FcsOGHH<u9sSpM}}ocN#=IfHx?QT_*Kt+}WT%KS%Qm4i&-XxkUgN=(3EDq}VXXTw41oVxZc~XSxi48>W7a`S)y$J*VbX35^Idh<9MkMwdO%u!Km52wWVX9c#4w;M#xfyIc>7Yd+=Cqu(vhQ*=;)nV!)I`o6?2==3ZUmVhsifXhh*RCC!$Nj?_GG4ZdfMZ1->vA_$ZL_iAu-XNG2-vYOuVfR6`yK2KN&`s*FEj`~31#{gQODNC+A5eS;ZEx(ANV#5FpXAKVCb0HWLYIy>r6G{~SgH|CbQ%`fEq-=pc&KT%f;m0o)|1gsla3M2%%*0fdJZ839ts-12z}TBG4%$c7zRS6dlI^ScL1Bp`=9H<m6+hm=`&O95N|DOj++LnLRQEU6p|`GzcMAH?vj?@4}^u;Rsg;H3|NbD;3iuaiCL|0=`=L4AP(ekD9{Gd1jMT52N*8|SfApTdz^|yemopL0STBFST3#$CXI}*5mjd;3HC+<{kR|na4(wdLHE{qP!zh@rg||Ql9UPO1LBy|HYen?3o*xs6X~hCme1y-lKDw3-CR9)Fbl2Df9?cBeulJwtB<ZpMd%OqsWM)zuf_-)p#|e;@YSs+vf-X)M%Cr&1@+H#F~ylW0;C7~t;Ww<$$!!7ks?*G%f{w(f%DoLzB-YX8m@x#SDF<dXL_xA)Sh*9H|w99K+vS3gu@Iq7w$`qv?`~QeKHOZ3lLISk=Wxtg#xcw9CH4FFM&Qe@=_sr`@Kt*@vLEB;7nyXGju9qu9htED#@u2u12%lc32EI!*~Jh%%Q@13zv2*U4N?Uc)j8ga@K_qA+TyRFJJ-K^nlKp=)~Pkqp%%|AXCESq#}S4wre@gSZJ}S5og+OIX4>kO+ipVFAZa9+k1Py%XW-wJ}4{`(bW@w6boqUHvhIpi|)cC2HnqQ22>B|4&IwQxo?<gE3E2q<+P2$nRf3ur-Xy>i-Q?~fsIg)6ugn*1e-}B*F!ZkTd88zu;rVl9qn4o?fx;nnPy!MmG-56HH#zx>txTKey8t>ZBRtYdkPc`EBgId*5xwG^ysjs4TxyPa>}1veHy9~Jyj}<9*4UmB5=w%z5WS@U;6C>K@VP&T&4_gTJN-iBlB??;vx!GTR<L7iQv`Un4`3L9e`SB<TUQtP}v-CW#H|M!8m+#v!${$sp!e7F|{=5+rU-w)C$k&$)-7QbI_cteKwHZ2&Ljki_XFPkPQ|Y2)>;=h>mR9Wjwu0)yvMu=WOHs`)M$sDpiXl%HZSnfc_DM+dnClMSFeWc8v-9VIOy)&Mk5N6GCFYf%d+WQyz0C<piPtN+)|yS6?ypE#vurk<b$29uY`HkiPYHvB8bk7Ns5^fvX#bO`1N{GgB0NK?JA9R3}c2gC}Tah#0jn^0j-2<l;izxnGSaFJ2rb4)51UpRO-)(2ZSJkc+uJjKI{lC3W+DrPy8{AVR<&$5yjFk1V)G5`b#f>~d+0`<BmHj}EUr;BsNf#ebe_kR&>>rwpzWpQxDX-025Ax<i@~^QiovXoAf^ag&UT9y@x4agtJ^mePjSnGCiFVDp{=w=7irN!6)_qbBLd$_=^PwYt>=lSn$9Vc&Z7ogt`r+?4I{cnoL*h|ovsf?I(UA6(wZOMI@C7mA!+H39U8@g`GubNBMCtQM^p$}FgIt4*%iKc|z@X??-5OHadMHL`Z(XM(X$oW=@%gQ|YtfVX1V0IajM`YRPRkgi0>oJnGr33*d@56b)u4RBOQxhrW}fv}M3Poa<|+icbyu)x11LVE<hCS*Gcsj?$CFu^cbo$JyJm@JrzQKVE4%ynbI$nj%LLF6V%T1qSI;S91y$a+31&L(#u>7@ktO>zZEL)N05w6rxFjzhUQ1)Y|c)+S{~c5n{*v}MVKYq>(t?tF9p;cEtiH6#`**94#AI7zj9EK+-^B0J|H$m{Eu%*zqx*9U=7WO_e;pfLYbvfRXS;y)`0EHUkU5CK0{8a{+%hR-5hT4CxTjdBT5Z$n8r3p`_jEy@ldWsFKb)dd&Gv!;A2$hTUnU05&=TYoVvTsCG6SRKMyCeJoC%W<@ddmBj6ux}qQZgF!n(UAw}W**QvS6SJkAE{Vg)i2K&QqT}TNsB4$svfm;NWEHsP=}rCOvWj?YmU|_g`1)KXJ76pO&^_;xET-8;sd_Nt7DbgkZK)n!pr7Xh61uhYKun<H+5FH3!h^ALyV~XQKo$*J=P&vsHkTSQ)oUX5ZGOA&SH3I5)yU9F8(?1XGon;KJJ>rWe^tuT2O$`KV((h7_7mDxA4!I&n~6WQWA*h@&J@7VNzx_|FXp+%W25pJjg`L+{0mIS0PG?an2(E&CiGfd*P0)9iXBV4U-Xl2zxc<?Q%?dE-|B>L1QrJ_5yhH=L&3f=8hX0T6L~(pkSJ;k*9Ms<*3QxMasXJ_S&4GLC<EmQTjfF)Q!E>WkE8$>r?ZmaKZhj$lmBDU$r&2IGjohvZD4nMO!@hkN&gEG{|*hew-~qidA*4Gw>ToHa=kW{uU)IT3{lW0@Wm=0`bFFrP9j^Un@QwEcOKzp2&;(rJ4X92cKl_mPnm|qaA_z(SKjtP*bIhg~WzI!%PnhTK3(<r-abYgme7WgC%Nyi0*?@9+kTx(hcK|i{W`<N1}_BbGKuM_u;kG78Yg3j3E}d?zz^8(ct2DZfpRQHFnj|VBeS{Uv1F<&<myJfD=|X(ZP#sb}syHO8O_q5;AgPZo_01zrmfT1eu;&lbjBGqu5S5C_3h<?IsAZp-?Fp(D`41WLA!GfC;l)a?JR%MU5;=*Z$JNk_sRSPoaa$=?$X)U!6US9lc<0)6-h4;DmNjKcZIR(q(<5+OhV$!hKAoNJjOU*Y^kDX_@xdRJ<PQLQZsSh39uja<wWyb%|zJe9w_d6m6{MYPNPn8Uq<!zpUbw8_Qna?;S3acyZl}cZR=Q3I8Qdn*;>cpWKV<`q9u%^~&gdpZj*x(8D>eyuo%606@~LHP7HJP|{)EG5ovJs`Y}X2DNE?5*K%<v?)&M#_U-Zfvwucb|pJMHG~tG^aEm_109tk$QKIaGWd0ZtjuUAP@DPTRWWM29u~@grASznXE?hAAL?5S0CN<jP2VY#zMK(YrY#cv{drv+2DNgk%rdB<E&Y23t6VJ<hB|&%Lv@0OOEgd|zBAC+q*fSKym*h3om3FSWBZwtP#`ET@a;4_B^wrbdNg<rEoh1R2bu%8(XSy^k(h9jI;Xq)wn!R$yBKMdRn4k5G2D^53+3=WAXr6an?KAJgB`zzeVWSVm?rkCy@yyWCrhra&H6nR+aX8?THOk;o#?YVTyJ_twS+-(?-$ojmXZ{7LrW2dTreWVs2{dSJ<BreY`qBB&szbiEQA^7P7kN|j`ImP;}`Oo?e1}6HdfVt#D+5I2`7374Fg6kK51(JC8GHj1^+ig;Ytzr9aIJNjjVF}WebF+vm!7oenO)Wj7HqU_ANCVp`RN=Tgl7S$OYJm!d2WG!paxA$ikA+=b#M03Y{Y1?i?ymG6Sd0Y~7$P6Jqn|<^)1iTX6JFMvE)vvdohhDr<f_8Ym-Jk8W_~HDLv*`fr8^uC!iv0_Vuj!Tvpu|BRbGW8c{*aXT9R0~7tJce%P?B~W*S@qkL3DZ1cZ%B3O?EX+3uDlzs&|282If(R)pd_)EBxyyt$4&iSleduUhS=AUS&!my8|I1c@fK_9O=N#c}JZgF00j7{D<&{B`vLZe@7iuJB+?|qlItb~Ibn=28XZ~45!iBBCU=o)Gnk!l97XM(FSte9E4HEuL9O<!KIJac}A1qHb^hXI}qx|0L=A1z-91L-a-4S=@=JGunE!#f9)0739lXJK2QZBO5SLNYEc@u@jBisW+wI$6DnA|R)FEiAWLggm?0>#I#<1PmH9+H+!gh5ORO0%)yRZ6pGMQRJGn=vf6un5AaG}JVXsZITyd0ap8UoM&c9<uW6V(kn#5p7uM_YxvpiFgi*k#7Q69@4EJMH1Qj(G@P)w^WjaF6Atx$0rAil{mkwR4vKWa7(GUf34K1HJ{IawM`05y?<~+46|ybq>h6HRJtp9_v<)e78{D8nYT!@vt7Uzt?QMN)LSKwpm1U_8Nv)rt$<YE+GzP%)R^5o$YniG{LTQu61h8(wo?JpDs<j=Vjf`qyojw$5vGOry%}V4N67k8Elg=oI}g#OG2nGxG?dxn^QlG_Xe*gPp6RKqrOAmeH-l+AYj)n0HP9Bc_lE6|Klh{K7JUW|*y$|5EJUHbnf5u?kO-`6_9KDsN<B7%4_{=zZP@GQvc5cOU2kJ?!@*R_@T6sB<I~5=uw2^a&sAceQ6axVO!gt);Tli<C7m>9RuWSBQYR@h2%tS$Y5WvRb{oETN6e#njY#mEKtn2Wm^9m(EksUS9#S0+nA3L#oZ&$ab|pH2X#x3N>7)<B;hAsrGJ~$#?6^b(z*xc-*E4QB2$ER-;+a)5D!53jT+w48z+x+=o85RprM_V@WhWby)a`fS-mS`$MCNi93)FL>@)|EK@wGLVh+kFdxHoDAjHE*vx|%<eD9O~Ybz<uOHl!V>@xCg&HdWNX*~s?W=vaUNi)%R?PG->N5s6=PtGdoIhi#JIVL`c^D4$MomY}$_cigrx<%NsS5Go`&03&s=C(sFW=~})h&qg7)X$9l_vWmmUOkT?C6fNK9svE3tqunD9w=nA<t+-4@aN54sJi3{1@VkQf(NXgh0n<s?ZD@AD187=?myRUGofY`;;F>a@l2#Uz*>AU69z%MXoEG}zw^a{^U#R^7Zh<X*)osD?>Ili+0;G9{mj34|I4MtCvE!3@tp)A~ewH8-vy1HhH3l8sAb$^bnF1yWqTzDcoA`V6`1yMo7Qd+hik_<iKM%GP0jgV-uVik+dpONi(!$*tcxXK-OMnK-kD=!iB_)Spq{L~#6C;bVt$TKh$Ix--0@?Oy9S}Q>XzFfQpLkLI25Fkrv@_Bc@RE6VQ84T2mNmUKaPbw6%l!C-zXZlKXGy*1a}cRJ`HBXnB=8j0qJgg=<rNyAW-8AYrB~S?{Nwh+d(6%eIe+~3^09N)o^7-*H80QLT!S?aulqVNjI?$}qbAiHsQ?Favp2$yZuC1lqphn#1#c1*Kz-VMi|;*ThF7(7*5Hc9t<4U=l|Cn$)pSOp?ncn2{aV_l4ps$VWWl{x237hfcYfDZi1P0e{4TO}(Rdt$Lm4?OWtv14vH@wDw>y@rtvtLb1M#Mr+9+IZ;Gl#vWT=z~o{vtW_YI-|^ZTW`G}&l$>e+6jiEOL=80RMwz^)MV<Wp82^rdBnqc~$36f3`rU;xCDHwv~a^W+XEjjK0p&ZC~YK4w&zk$m_~7*Var1oUmQY<>Gl+aT%mtjj7wyvBNoC_%+5?Gk)ma0-pWeRRS{IkXGHUz&30>Q{P!V+Su-a%?}Y;w#hF3A2XLK>;QYm7#^JY9>z1l3o)&xt>6V(7B+5I+3Iu#oFkQF|g^~5@}e+#>y`**!VYT-d6!`^e@!JaQzsz^xdG{+)4msa{>f!Hwzx96D_93<(piBWP<qXJ+K*RQ`!%?c_IFd8ng3<nnNKmjo7uROmHL~5CahoZx=)(XD33BiD7Dw&6^$_EuKabNy?~w*Zi=<$Z07bTI{5A+8=rj;qewF4AvNqqnHVD#>s?g!#iMDLH_2<><MZh67BH}U*|cd>)#2h$bB0{JWS@Hy9(xF-3bnr%#j(`KS`B&a3~Sl0@cIc6=kF9@wh5|m;mt84Jk7V&(s3vSTyfEbM>ckOta)Dfi`96iMKj#ZIzktMA*u%11|k*8`a46QNKlEcV^-Zg*4D1S4F25{I;qrX8uU(1=e&n+SCKx1y%tnuKW813uQzhcP)$zUocWZW8_PrN4a{yy}-BC7uG4xKQ3oq_X4@``#6|halJS1J{oMlV68SKX0YRpqKC>%E3r%y-T{K+#}A*mjsMh3%*+')).decode();_gc=lambda s:tuple(int(x.strip().rstrip("u"),0)for x in GEN_C.split(s+"={")[1].split("}")[0].split(","));IV,K,PERM,_X0,UCD=_gc("IV[8]"),_gc("K[RND]"),_gc("PERM[8]"),_gc("PW[8]"),_gc("UCD[96]");PAD2=bytes([128])+bytes(55)+(512).to_bytes(8,"big");_fn=lambda*xs:(x if callable(x)else x.__getitem__ for x in xs)
def Aj(v,k):return((v>>k)|(v<<(32-k)))&M32
def words_of(x):return[(x>>(32*(7-i)))&M32 for i in range(8)]
def int_of(w):return sum(w[i]<<(32*(7-i))for i in range(8))
def _Z3(a):return Aj(a,2)^Aj(a,13)^Aj(a,22)
def An(e):return Aj(e,6)^Aj(e,11)^Aj(e,25)
def _CH(e,f,g):return(e&f)^(~e&g)
def A6(a,b,c):return(a&b)^(a&c)^(b&c)
def As(ws):
	ws=list(ws)
	for i in range(16,ROUNDS):x,y=ws[i-15],ws[i-2];ws.append((ws[i-16]+(Aj(x,7)^Aj(x,18)^(x>>3))+ws[i-7]+(Aj(y,17)^Aj(y,19)^(y>>10)))&M32)
	return ws
Ap=1;CIN=1;NTAIL=6 if Ap else 4;QM,XM=0x7c350f64,0x1d223aa4;PRE,_Y1,_Y4,_X4=8,8,{},set(range(10,16))
def _S3(w,prefix=None):
	prefix=_X0 if prefix is None else prefix;ws=list(prefix[:PRE])+[0]*(16-PRE)
	for k in range(8):ws[_Y1+k]=(w[k]-(K[_Y1+k]if _Y1+k in _X4 else 0))&M32
	for pos,v in _Y4.items():ws[pos]=v
	return ws
def Ar(w,prefix=None):
	ws=As(_S3(w,prefix));a,b,c,d,e,f,g,h=IV;A,E,T={0:a,-1:b,-2:c,-3:d},{0:e,-1:f,-2:g,-3:h},{}
	for i in range(ROUNDS):t1=(h+An(e)+_CH(e,f,g)+K[i]+ws[i])&M32;t2=(_Z3(a)+A6(a,b,c))&M32;a,b,c,d,e,f,g,h=(t1+t2)&M32,a,b,c,(d+t1)&M32,e,f,g;A[i+1],E[i+1],T[i+1]=a,e,t1
	return ws,A,E,T
def _R0(w,prefix=None):_,A,E,_=Ar(w,prefix);r=ROUNDS;return[A[r],A[r-1],A[r-2],A[r-3],E[r],E[r-1],E[r-2],E[r-3]]
def enc_words(w,prefix=None):ws,A,E,T=Ar(w,prefix);r=ROUNDS;bw=[E[r-3],E[r-2],A[r-7],A[r-6],(T[r-5]+_CH(A[r-6]^A[r-7],A[r-8],QM))&M32,T[r-4],(E[r-5]+_CH(E[r-2],XM,E[r-4])+ws[r-2])&M32,(E[r-4]+ws[r-1])&M32];return[bw[PERM[k]]for k in range(8)]
def enc_invert(enc):
	r,bw=ROUNDS,[0]*8
	for k in range(8):bw[PERM[k]]=enc[k]
	e3,e2,a7,a6,Q,T4,X,Y=bw;a5=(Q+(a6&a7&~QM)-(~a6&~a7&QM)+_Z3(a6))&M32;a4=(T4+_Z3(a5)+A6(a5,a6,a7))&M32;a3=(e3-a7+_Z3(a4)+A6(a4,a5,a6))&M32;a2=(e2-a6+_Z3(a3)+A6(a3,a4,a5))&M32;t1=(X+(e2&e3&~XM)-(e2&~e3&XM)+An(e2)+K[r-2])&M32;e1=(a5+t1)&M32;a1=(t1+_Z3(a2)+A6(a2,a3,a4))&M32;t0=(Y+An(e1)+_CH(e1,e2,e3)+K[r-1])&M32;return[(t0+_Z3(a1)+A6(a1,a2,a3))&M32,a1,a2,a3,(a4+t0)&M32,e1,e2,e3]
def _W0(x,n=256):return int_of(enc_words(words_of(x)))&((1<<n)-1)
PAD2W=tuple(int.from_bytes(PAD2[4*i:4*i+4],"big")for i in range(16));_KW2=tuple((K[i]+w)&M32 for i,w in enumerate(As(PAD2W)))
def _Q0(s):
	cv=[(u+v)&M32 for u,v in zip(IV,s)];a,b,c,d,e,f,g,h=cv
	for kw in _KW2:t1=(h+An(e)+_CH(e,f,g)+kw)&M32;t2=(_Z3(a)+A6(a,b,c))&M32;a,b,c,d,e,f,g,h=(t1+t2)&M32,a,b,c,(d+t1)&M32,e,f,g
	return int_of([(u+v)&M32 for u,v in zip(cv,[a,b,c,d,e,f,g,h])])
def _V4(o,qint):return _Q0(enc_invert(words_of(o^qint)))
def message(x):return b"".join(v.to_bytes(4,"big")for v in _S3(words_of(x)))
RP,RMASK=128,M32|(M32<<128);WM,KM=0,ROUNDS-10
def _rep(v):return v|(v<<RP)
class RecProg:
	def __init__(self):
		n=ROUNDS;self.imm,self.init=[],[];Ab,T0,T1,T2,T3,T4=0,11,12,13,14,15;ST,PB=list(range(1,9)),[9,10];W0,W1,W2,W3,WC0,WC1,WC2,WC3,E0,E1,WN=19,20,21,22,24,25,26,27,28,29,30
		def S(out,x,v,m=0):self.imm.append(v);out.append(("S",x,len(self.imm)-1,m))
		S(self.init,Ab,RMASK);S(self.init,WN,_rep(_X0[0]))
		for i in range(10,n-6):S(self.init,T0,_rep(K[i]));self.init.append(("T",KM+i,T0,2))
		_T3={i:_X0[i]for i in range(1,PRE)};_T3.update(_Y4)
		for i in sorted(_T3):S(self.init,T0,_rep(_T3[i]));self.init.append(("T",WM+i,T0,2))
		hregs=[5,6,10,11,12,15]
		for j,k in enumerate(range(2,8)):S(self.init,hregs[j],_rep((-K[_Y1+k])&M32))
		for rk,vk in zip((13,14,16,18,23,29),(K[n-6],K[n-5],K[n-4],K[n-3],XM,QM)):S(self.init,rk,_rep(vk))
		def sigma(out,dst,src,rs,shr,mask=True,dup=True):
			if dup:out+=[("<",T0,src,32),("|",T0,src,T0)]
			out+=[(">",dst,T0,rs[0]),(">",T1,T0,rs[1]),("^",dst,dst,T1)];out+=[(">",T1,src,shr)if shr else(">",T1,T0,rs[2]),("^",dst,dst,T1)]
			if mask:out.append(("&",dst,dst,Ab))
		def rnd(out,st,pi,wreg,addrk):a,b,c,d,e,f,g,h=st;P,PN=PB[pi],PB[1-pi];sigma(out,E0,e,(6,11,25),0,False);out+=[("^",T1,f,g),("&",T1,e,T1),("^",T1,g,T1)];out+=[("L",T0,addrk+KM,0),("+",E0,h,E0),("+",E0,E0,T1),("+",E0,E0,wreg),("+",E0,E0,T0)];sigma(out,h,a,(2,13,22),0,True);out+=[("^",PN,a,b),("&",T0,PN,P),("^",T0,T0,b),("+",T1,h,T0)];out+=[("+",h,d,E0),("&",h,h,Ab),("+",d,E0,T1),("&",d,d,Ab)];return[d,a,b,c,h,e,f,g],1-pi
		assert WM==0;body=[];st,pi=list(ST),0;pre=[];SH=(n-16)%4
		for k in range(SH):st,pi=rnd(pre,st,pi,WC0,10+k);pre.append(("L",WC2,1+k,0));sigma(pre,E0,WC2,(7,18,0),3,True);pre+=[("+",E0,WC3,E0),("+",WC3,WC2,WC0)];sigma(pre,WC2,W2,(17,19,0),10,False);pre+=[("+",E0,E0,WC2),("&",E0,E0,Ab),("T",16+k,E0,0)]+[("|",a,b,b)for a,b in zip((WC0,WC1,W0,W1,W2,W3),(WC1,W0,W1,W2,W3,E0))]
		stl,pil=list(st),pi
		for j,wr in enumerate((WC0,WC1,W0,W1)):stl,pil=rnd(body,stl,pil,wr,10+j)
		assert stl==st and pil==pi;body+=[("L",WN,4,0)];sigma(body,E0,WN,(7,18,0),3,True);body+=[("+",WC2,W0,E0),("L",W0,1,0)];sigma(body,E0,W0,(7,18,0),3,True);body+=[("+",E0,WC3,E0),("+",WC3,WN,W1),("+",W1,W0,WC0)];sigma(body,W0,W2,(17,19,0),10,False);body+=[("+",W0,W0,E0),("&",W0,W0,Ab),("T",16,W0,0),("|",WC0,W2,W2),("L",W2,2,0)];sigma(body,E0,W2,(7,18,0),3,True);body+=[("+",W1,W1,E0),("+",W2,W2,WC1)];sigma(body,E0,W3,(17,19,0),10,False);body+=[("+",W1,W1,E0),("&",W1,W1,Ab),("T",17,W1,0),("|",WC1,W3,W3),("L",W3,3,0)];sigma(body,E0,W3,(7,18,0),3,True);body+=[("+",W2,W2,E0),("+",W3,W3,WC2)];sigma(body,E0,W0,(17,19,0),10,False);body+=[("+",W2,W2,E0),("&",W2,W2,Ab),("T",18,W2,0)];sigma(body,E0,W1,(17,19,0),10,False);body+=[("+",W3,W3,E0),("&",W3,W3,Ab),("T",19,W3,0)];ra,rb,rc,rd,re,rf,rg,rh=st
		def t1(out,dst,hr,er,fr,gr,wi,wreg,kreg):
			sigma(out,E0,er,(6,11,25),0,False);out+=[("^",T1,fr,gr),("&",T1,er,T1),("^",T1,gr,T1)]
			if wreg is None:out.append(("L",T0,WM+wi,2));wreg=T0
			out+=[("+",E0,hr,E0),("+",E0,E0,T1),("+",E0,E0,wreg),("+",dst,E0,kreg)]
		tail=[]
		if Ap:R5,QQ,E5,R4,E4,E3,E2,XX,YY=rh,17,rd,24,25,26,WC3,PB[0],31;t1(tail,R5,rh,re,rf,rg,n-6,WC0,13);tail+=[("+",E5,rd,R5),("&",E5,E5,Ab)];t1(tail,R4,rg,E5,re,rf,n-5,WC1,14);tail+=[("+",E4,rc,R4),("&",E4,E4,Ab)];t1(tail,E0,rf,E4,E5,re,n-4,W0,16);tail+=[("+",E3,rb,E0),("&",E3,E3,Ab)];t1(tail,E0,re,E3,E4,E5,n-3,W1,18);tail+=[("+",E2,ra,E0)];tail+=[("^",T1,E4,23),("&",T1,E2,T1),("^",T1,E4,T1),("+",XX,E5,T1),("+",XX,XX,W2)];tail+=[("+",YY,E4,W3)];tail+=[("^",T0,ra,rb),("^",E0,rc,29),("&",T0,T0,E0),("^",T0,29,T0),("+",QQ,R5,T0)];cp=[("|",ST[1],rb,rb),("|",ST[0],ra,ra)]if SH else[];tail+=cp[::-1]if ra==ST[1]else cp;fb=[E3,E2,ST[1],ST[0],QQ,R4,XX,YY];self.fin=[fb[PERM[k]]for k in range(8)]
		A1=[];wregs=(WC0,WC1,W0,W1,W2,W3)
		for k in range(7,-1,-1):
			if _Y1+k in _X4:d=wregs[k-2];A1+=[("+",d,self.fin[k],hregs[k-2]),("&",d,d,Ab),("T",WM+_Y1+k,d,2)]
			else:A1.append(("T",WM+_Y1+k,self.fin[k],2))
		y0,y1=self.fin[0],self.fin[1];sigma(A1,ST[4],y0,(6,11,25),0,False,dup=True);A1+=[("+",ST[4],ST[4],y1),("&",ST[4],ST[4],Ab),("+",WC3,y1,WN)];sigma(A1,ST[0],y0,(2,13,22),0,False,dup=False);A1+=[("+",ST[0],ST[0],ST[4]),("&",ST[0],ST[0],Ab),("|",ST[1],y0,ST[2]),("|",ST[5],y0,ST[2])];self.blocks=[("S",A1+pre),("L",body,SH,n-16-SH,4),("S",tail)];self.flat=[]
		for blk in self.blocks:
			if blk[0]=="S":self.flat+=blk[1]
			else:_,bd,start,count,stepw=blk;self.flat+=[("R",0,start,0),("R",1,start+count,0)];top=len(self.flat);self.flat+=bd+[("A",0,stepw,0),("C",0,1,0),("J",top,0,0)]
		self.instr=len(self.init)+len(self.flat);self.mem,self.regs=[0]*(2*ROUNDS-16),[0]*32;self.run(self.init);self.mem0,self.regs0=list(self.mem),list(self.regs);self.ops=self.run(self.flat)
	def run(self,recs):
		r,mem,p,flag,pc,cnt=self.regs,self.mem,[0,0,0],False,0,0
		while pc<len(recs):
			op,x,y,z=recs[pc];pc+=1;cnt+=1
			if op in"^&|+><":r[x]=(r[y]^r[z]if op=="^"else r[y]&r[z]if op=="&"else r[y]|r[z]if op=="|"else r[y]+r[z]if op=="+"else r[y]>>z if op==">"else r[y]<<z)&ALL
			elif op=="S":(mem if z else r)[x]=self.imm[y]
			elif op=="L":r[x]=mem[p[z]+y]
			elif op=="T":mem[p[z]+x]=r[y]
			elif op=="R":p[x]=y
			elif op=="A":p[x]+=y
			elif op=="C":flag=p[x]<p[y]
			elif op=="J"and flag:pc=x
		return cnt
	def f(self,xs,fast=True):
		if fast:return[_W0(x)for x in xs]
		self.regs[:],self.mem[:]=self.regs0,self.mem0
		for k in range(8):self.regs[self.fin[k]]=sum(((x>>(32*(7-k)))&M32)<<(RP*l)for l,x in enumerate(xs))
		self.run(self.flat);return[sum(((self.regs[self.fin[k]]>>(RP*l))&M32)<<(32*(7-k))for k in range(8))for l in range(len(xs))]
_REC=[]
def rec():
	if not _REC:_REC.append(RecProg())
	return _REC[0]
def _V2(xs,n,qw=None):q=sum(qw[i]<<(32*i)for i in range(8))if qw else 0;return[(v^q)&((1<<n)-1)for v in rec().f(xs)]
def _Q4(qw=None):return rec().ops
Aa,ONE=(0,0),(0,1);_R1=(0,)*70;EXPECTED_EMITTER_INFO=(57623,871,57894,228852,0,0,45220,7614,4789,230548,16384,57894,29952,70,1234);_Y3="1b12edb395f6857eba84eb29182b28a3da80399e87e478ad48bf37803bbfe14d";_X3="192ff62f0303827941b85e8ec2adfe91c5a788d66016010157bff805bb8bee28";_V5="c207e8c0c4eb4664f1153c985d89037ca1c7d2429a79bd34fddddd6d3911e3dc";_T5=int("7fd81be44b62b302c8d9beea0c8abe43ab19e0d125a729edaf14e9c82d847324",16)
class Gen:
	def __init__(self,n):
		self.n,self.nodes,self.calls=n,[("c",)],0;self.ahi=0;self.inputs,self.cse=[],{}
		for j in range(n):self.nodes.append(("v",j));self.inputs.append((len(self.nodes)-1,0))
	def mk(self,op,a,b):
		self.calls+=1
		if a>b:a,b=b,a
		k=self.cse.get((op,a,b))
		if k is None:self.nodes.append((op,a,b));k=self.cse[(op,a,b)]=len(self.nodes)-1
		return k
	def _gate(self,node):
		if node<=self.n or node<len(self.nodes)-8:return None
		g=self.nodes[node];return g if g[0]in("x","a","o")else None
	def XOR(self,x,y):
		self.calls+=1
		if x[0]==0:return(y[0],y[1]^x[1])
		if y[0]==0:return(x[0],x[1]^y[1])
		if x[0]==y[0]:return(0,x[1]^y[1])
		gx,gy=self._gate(x[0]),self._gate(y[0]);inv=x[1]^y[1]
		if gx and gx[0]=="x"and y[0]in gx[1:]:return(gx[2]if gx[1]==y[0]else gx[1],inv)
		if gy and gy[0]=="x"and x[0]in gy[1:]:return(gy[2]if gy[1]==x[0]else gy[1],inv)
		if gx and gy and gx[0]==gy[0]=="x":
			cm=set(gx[1:])&set(gy[1:])
			if cm:c= min(cm);r=self.XOR((gx[2]if gx[1]==c else gx[1],0),(gy[2]if gy[1]==c else gy[1],0));return(r[0],r[1]^inv)
		return(self.mk("x",x[0],y[0]),x[1]^y[1])
	def AND(self,x,y):
		self.calls+=1
		if x[0]==0:return Aa if x[1]==0 else y
		if y[0]==0:return Aa if y[1]==0 else x
		if x[0]==y[0]:return x if x[1]==y[1]else Aa
		if x[1]==0 and y[1]==0:return(self.mk("a",x[0],y[0]),0)
		if x[1]==1 and y[1]==1:return(self.mk("o",x[0],y[0]),1)
		p,q=(x,y)if x[1]==0 else(y,x);return self.XOR(p,(self.mk("a",p[0],q[0]),0))
	def fa(self,a,b,c):
		ops=(a,b,c);cs=[t for t in ops if t[0]==0];vs=[t for t in ops if t[0]!=0];k=0
		for t in cs:k^=t[1]
		if len(vs)==3:
			for pi in range(3):
				o=[vs[j]for j in range(3)if j!=pi]
				if o[0][1]==o[1][1]:p,x,y=vs[pi],o[0],o[1];break
			u=self.XOR(x,p);return self.XOR(u,y),self.XOR(self.AND(u,self.XOR(y,p)),p)
		if len(vs)==2:
			x,y=vs;t=self.XOR(x,y);s=(t[0],t[1]^k)
			if x[1]==y[1]:
				if k==0:return s,self.AND(x,y)
				cr=self.AND((x[0],x[1]^1),(y[0],y[1]^1));return s,(cr[0],cr[1]^1)
			nt=(t[0],t[1]^1);xx=x if x[1]==nt[1]else y
			if k==0:return s,self.AND(xx,nt)
			xx=x if x[1]==t[1]else y;cr=self.AND((xx[0],xx[1]^1),(t[0],t[1]^1));return s,(cr[0],cr[1]^1)
		if len(vs)==1:x=vs[0];k1,k2=cs[0][1],cs[1][1];return(x[0],x[1]^k),(ONE if k1==k2==1 else Aa if k1==k2==0 else x)
		kk=cs[0][1]+cs[1][1]+cs[2][1];return(Aa if kk%2==0 else ONE),(ONE if kk>=2 else Aa)
	def add(self,A,B,cin=Aa):
		a,b=_fn(A,B);s,c=[],cin
		for i in range(32):
			if i==31:s.append(self.XOR(self.XOR(a(i),b(i)),c))
			else:si,c=self.fa(a(i),b(i),c);s.append(si)
		return s
	def OR(self,x,y):r=self.AND((x[0],x[1]^1),(y[0],y[1]^1));return(r[0],r[1]^1)
	def _col(self,t,u,U,oU,rev=False):
		X,A,O,pt=self.XOR,self.AND,self.OR,U[1]^u[1]
		if t[0][1]==t[1][1]==t[2][1]:(x,y,z),tm=t,(1 if t[0][1]==pt else 2)
		else:
			for zi in((2,1,0)if rev else(0,1,2)):
				if t[zi][1]==pt:r0,r1=[t[j]for j in range(3)if j!=zi];(x,y,z),tm=((r1,r0,t[zi]),0)if r0[1]!=u[1]else((r0,r1,t[zi]),0)if r1[1]!=u[1]else((r0,t[zi],r1),1);break
		if tm==1:w=X(y,U);n8=X(z,w);s=X(x,n8);n6=O(U,X(y,u));return s,(Aa if oU else X(n6,w)),X(n6,A(n8,X(x,w)))
		if tm==2:w5=X(x,y);w6=X(z,w5);s=X(U,w6);w9=X(u,w6);w10=O(U,(w9[0],w9[1]^1));w11=O(w5,X(x,z));return s,(Aa if oU else X(w6,(w10[0],w10[1]^1))),X(w10,(w11[0],w11[1]^1))
		n5=X(z,U);n9=X(x,n5);s=X(y,n9);n6=X(x,y);n8=O(U,X(z,u));n11=A((n6[0],n6[1]^1),n9);return s,(Aa if oU else X(n5,n11)),X(n8,n11)
	def add3(self,A,B,C,cin=0,d0=None,h0=None,u0=None):
		a,b,c=_fn(A,B,C);s=[None]*32
		if h0 is not None:
			sw0,u=self.fa(b(0),c(0),ONE if cin else Aa);s[0]=self.XOR(u0,sw0);w=self.XOR(h0,sw0)
			if u0[0]and w[0]and u0[0]!=w[0]and u0[1]!=w[1]:cm=self.XOR(self.AND((u0[0],u0[1]^1),w),sw0)
			else:cm=self.XOR(self.AND(u0,w),h0)
			U=self.XOR(u,cm)
		elif cin==0:
			s[0],U=self.fa(a(0),b(0),c(0))
			if d0 is not None:s[0],u=self.fa(s[0],d0,Aa);U=self.XOR(U,u)
			else:u=Aa
		elif cin==2:s[0],c0=self.fa(a(0),b(0),c(0));u,U=ONE,(c0[0],c0[1]^1)
		else:
			ops=(a(0),b(0),c(0))
			for pi in range(3):
				o=[ops[j]for j in range(3)if j!=pi]
				if o[0][1]==o[1][1]:p,x,y=ops[pi],o[0],o[1];break
			u0=self.XOR(x,p);s[0]=self.XOR(u0,(y[0],y[1]^1));u,U=p,self.OR(u0,self.XOR(y,p))
		for i in range(1,31):s[i],u,U=self._col((a(i),b(i),c(i)),u,U,i==30)
		s[31]=self.XOR(self.XOR(self.XOR(a(31),b(31)),c(31)),U);return s
	def add2c(self,A,B,cv):
		a,b=_fn(A,B);cin=1 if _tz((cv-1)&M32)>_tz(cv)else 0;cv2=(cv-cin)&M32
		if not cv2:return self.add(a,b,ONE if cin else Aa)
		k,s,c=_tz(cv2),[None]*32,ONE if cin else Aa
		for i in range(k):s[i],c=self.fa(a(i),b(i),c)
		if k==31:s[31]=self.XOR(self.XOR(a(31),b(31)),(c[0],c[1]^1));return s
		ops=(a(k),b(k),c)
		for pi in range(3):
			o=[ops[j]for j in range(3)if j!=pi]
			if o[0][1]==o[1][1]:p,x,y=ops[pi],o[0],o[1];break
		u0=self.XOR(x,p);s[k]=self.XOR(u0,(y[0],y[1]^1));u,U,C=p,self.OR(u0,self.XOR(y,p)),_Y0(cv2)
		for i in range(k+1,31):s[i],u,U=self._col((C[i],a(i),b(i)),u,U,i==30,True)
		s[31]=self.XOR(self.XOR(self.XOR(a(31),b(31)),C[31]),U);return s
	def _baseline(self,cv,vs,fb=None,cid=None):
		if len(vs)==2 and cv and fb is None:
			if cid in(20,23,24,27):return self.add2c(vs[0],vs[1],cv)
			if cid in(16,18,22):
				rem=((-K[17])&M32)if cid==18 else((4-K[19])&M32)if cid==22 else((6-_X0[7]-K[23])&M32);s=self.add2c(vs[0],vs[1],(cv-rem)&M32);out=self.add(s,_Y0(rem));sp=getattr(self,"split",None)
				if sp is not None:sp[tuple(out)]=(s,rem)
				return out
		bb=fb if fb is not None else(max(range(len(vs)),key=lambda k:(_tz((cv-k)&M32),-k))if CIN and cv else 0)
		if len(vs)==4 and bb==0 and not cv:A,B,D,C=vs;s=self.add3(A,B,C,0,D[0]);return self.add(s,[Aa]+D[1:])
		ub=0
		while len(vs)>2:c3=min(bb-ub,2);ub+=c3;vs=[self.add3(*vs[:3],c3)]+vs[3:]
		s=vs[0]
		for w in vs[1:]:c1=1 if ub<bb else 0;ub+=c1;s=self.add(s,w,ONE if c1 else Aa)
		cv=(cv-ub)&M32
		if cv:
			out=self.add(s,_Y0(cv));sp=getattr(self,"split",None)
			if sp is not None:sp[tuple(out)]=(s,cv)
			return out
		return s
	def _choice(self,op,mask):
		pick=[op[i]for i in range(len(op))if(mask>>i)&1];rest=[op[i]for i in range(len(op))if not((mask>>i)&1)];first=self.add3(*pick)
		if not rest:return first
		if len(rest)==1:return self.add(first,rest[0])
		if len(rest)==2:return self.add3(first,*rest)
		assert 0
	def addm(self,*ws,_V3=None):
		cv,vs=0,[]
		for w in ws:
			if all(x[0]==0 for x in w):cv+=sum(x[1]<<i for i,x in enumerate(w))
			else:vs.append(w)
		cv&=M32
		if not vs:return _Y0(cv)
		cid=self.ahi;self.ahi+=1;hint=_R1[cid]
		if hint and _V3 is None:op=list(vs)+([_Y0(cv)]if cv else[]);assert hint<(1<<len(op))and hint.bit_count()==3;return self._choice(op,hint)
		return self._baseline(cv,list(vs),_V3,cid)
	def xorw(self,A,B):return[self.XOR(a,b)for a,b in zip(A,B)]
def _tz(v):return 32 if v==0 else(v&-v).bit_length()-1
def _Y0(v):return[ONE if(v>>i)&1 else Aa for i in range(32)]
def _U4(g,A,r1,r2,r3,shift,j):return g.XOR(g.XOR(A[(j+r1)%32],A[(j+r2)%32]),(A[j+r3]if j+r3<32 else Aa)if shift else A[(j+r3)%32])
def _R2(g,A,r1,r2,r3,shift):return[_U4(g,A,r1,r2,r3,shift,j)for j in range(32)]
def _add_u(g,A,u,c1=0,ch1=None):
	s=[None]
	if ch1 is not None:s1,c=g.fa(A[1],ch1,ONE if c1 else Aa);s.append(s1)
	elif c1:s.append((u[1][0],u[1][1]^1));c=g.OR(A[1],u[1])
	else:s.append(u[1]);c=g.AND(A[1],(u[1][0],u[1][1]^1))
	for i in range(2,31):
		s.append(g.XOR(u[i],c));w=g.XOR(A[i],c)
		if u[i][0]and w[0]and u[i][0]!=w[0]and u[i][1]!=w[1]:c=g.XOR(g.AND((u[i][0],u[i][1]^1),w),c)
		else:c=g.XOR(g.AND(u[i],w),A[i])
	s.append(g.XOR(u[31],c));return s
def A5(g,hw,ui,u,U,cb,ch,oU):
	idx=(cb<<4)|hw[1]|(ui[1]<<1)|(u[1]<<2)|(U[1]<<3);code=UCD[64+idx]if oU else UCD[2*idx+ch]
	if not code:w6=(ui[0],ui[1]^cb);s=g.XOR(U,w6);w9=g.XOR(u,w6);w10=g.OR(U,(w9[0],w9[1]^1));w11=g.OR(ui,(hw[0],hw[1]^cb));return s,(Aa if oU else g.XOR(w6,(w10[0],w10[1]^1))),g.XOR(w10,(w11[0],w11[1]^1))
	ops=("x","a","o");sr=g.mk("x",ui[0],U[0]);rs=[hw[0],ui[0],u[0],U[0],sr]if oU and((code>>26)&1)else[ui[0],u[0],U[0],sr,g.mk("a"if ui[1]else "o",hw[0],ui[0])]
	for q in range(3):c=(code>>(8*q))&255;rs.append(g.mk(ops[c&3],rs[(c>>2)&7],rs[c>>5]))
	a3=(code>>24)&3;Ur=g.mk("x",rs[4+a3],rs[7])if a3<3 else rs[7];return(sr,ui[1]^U[1]^cb),(Aa if oU else(rs[4+((code>>26)&3)],(code>>28)&1)),(Ur,(code>>29)&1)
def _adduc(g,A,u,cv,c1=0,ch1=None):
	if not cv:return _add_u(g,A,u,c1,ch1),0
	k=_tz(cv)
	if k<=1 or k>=31:return _add_u(g,A,u,c1,ch1),cv
	dc,dh=[[[0,0],[0,0]]for _ in range(31)],[[[0,0],[0,0]]for _ in range(31)];cb30=(cv>>30)&1
	for pu in(0,1):
		for pU in(0,1):code=UCD[64+((cb30<<4)|A[30][1]|(u[30][1]<<1)|(pu<<2)|(pU<<3))];dc[30][pu][pU]=(5+((code>>27)&1))if code else 6
	for i in range(29,k,-1):
		cb=(cv>>i)&1
		for pu in(0,1):
			for pU in(0,1):
				idx=(cb<<4)|A[i][1]|(u[i][1]<<1)|(pu<<2)|(pU<<3)
				if not UCD[2*idx]:dc[i][pu][pU]=7+dc[i+1][cb][0]
				else:
					bc,bch=999,0
					for ch in(0,1):
						code=UCD[2*idx+ch]
						if code:
							tc=6+dc[i+1][(code>>28)&1][(code>>29)&1]
							if tc<bc:bc,bch=tc,ch
					dc[i][pu][pU],dh[i][pu][pU]=bc,bch
	out=[None]*32
	if ch1 is not None:out[1],c=g.fa(A[1],ch1,ONE if c1 else Aa)
	elif c1:out[1],c=(u[1][0],u[1][1]^1),g.OR(A[1],u[1])
	else:out[1],c=u[1],g.AND(A[1],(u[1][0],u[1][1]^1))
	for i in range(2,k):
		out[i]=g.XOR(u[i],c);w=g.XOR(A[i],c)
		if u[i][0]and w[0]and u[i][0]!=w[0]and u[i][1]!=w[1]:c=g.XOR(g.AND((u[i][0],u[i][1]^1),w),c)
		else:c=g.XOR(g.AND(u[i],w),A[i])
	pw=A[k][1]^c[1];cck=3 if u[k][1]==pw else 4;pUk=0 if(u[k][1]==0 and pw==0)else 1;cmk=cck+(1 if k==30 else min(dc[k+1][A[k][1]][pUk],dc[k+1][c[1]][pUk])+1);base=6*(31-k);pcu,pcc=c[1],0;bm,bc=(k,cmk)if cmk<base else(31,base)
	for i in range(k,30):
		pti,pwi=u[i][1]^pcu,A[i][1]^pcu;pcun=(pwi^pcu)if u[i][1]!=pwi else(u[i][1]^A[i][1]);cb=(cv>>i)&1;pccn=pti if i==k else(pti if pti==pcc else cb);pcu,pcc=pcun,pccn;m,pUm=i+1,pcu^pcc;cm=6*(m-k)+min(dc[m][pcu][pUm],dc[m][pcc][pUm])
		if cm<bc:bc,bm=cm,m
	if bm==31:
		for i in range(k,31):
			out[i]=g.XOR(u[i],c);w=g.XOR(A[i],c)
			if u[i][0]and w[0]and u[i][0]!=w[0]and u[i][1]!=w[1]:c=g.XOR(g.AND((u[i][0],u[i][1]^1),w),c)
			else:c=g.XOR(g.AND(u[i],w),A[i])
		out[31]=g.XOR(u[31],c);return out,cv
	if bm==k:s0=g.XOR(u[k],c);out[k]=(s0[0],s0[1]^1);Ucs=g.OR(u[k],g.XOR(A[k],c));ucs=(A[k]if dc[k+1][A[k][1]][Ucs[1]]<=dc[k+1][c[1]][Ucs[1]]else c)if k<30 else Aa;sc=k+1
	else:
		cu,cc,cw=c,Aa,_Y0(cv)
		for i in range(k,bm):
			ti=g.XOR(u[i],cu);w=g.XOR(A[i],cu)
			if u[i][0]and w[0]and u[i][0]!=w[0]and u[i][1]!=w[1]:cu=g.XOR(g.AND((u[i][0],u[i][1]^1),w),cu)
			else:cu=g.XOR(g.AND(u[i],w),A[i])
			out[i],cc=g.fa(ti,cw[i],cc)
		Ucs=g.XOR(cu,cc);ucs=cu if dc[bm][cu[1]][Ucs[1]]<=dc[bm][cc[1]][Ucs[1]]else cc;sc=bm
	for i in range(sc,31):cb=(cv>>i)&1;ch=0 if i==30 else dh[i][ucs[1]][Ucs[1]];out[i],ucs,Ucs=A5(g,A[i],u[i],ucs,Ucs,cb,ch,i==30)
	s31=g.XOR(u[31],Ucs);out[31]=(s31[0],s31[1]^((cv>>31)&1));return out,0
def A3(g,e,f,gg,h,hg,Wd,d=None):
	sp=getattr(g,"split",{});fg=[g.XOR(f[j],gg[j])for j in range(32)];hh=any(x[0]!=0 for x in h);ch1=g.XOR(f[1],g.AND((e[1][0],e[1][1]^1),fg[1]))if(hh and e[1][0]and fg[1][0]and e[1][1]!=fg[1][1])else None;u=[None if(j==1 and ch1 is not None)else g.XOR(hg[j],g.AND(e[j],fg[j]))for j in range(32)];s1=lambda j:_U4(g,e,6,11,25,False,j);cv,vs=0,[s1]
	for w in Wd:
		if all(x[0]==0 for x in w):cv+=sum(x[1]<<i for i,x in enumerate(w))
		else:vs.append(w)
	cv&=M32;hd=d is not None and any(x[0]!=0 for x in d)
	if hh and len(vs)==2:
		if not cv:t=_add_u(g,h,u,0,ch1);return g.add3(t,vs[0],vs[1],0,None,h[0],u[0]),fg,0
		p1=None if ch1 is not None else(1 if(h[1][0]and u[1][0]and h[1][1]==u[1][1])else 0);cands=[(vs[1],cv)]
		if tuple(vs[1])in sp:sr,cr=sp[tuple(vs[1])];cands.append((sr,(cv+cr)&M32))
		best=None
		for wc,cc in cands:
			for c0 in(0,1):
				for c1 in(0,1):
					for d_ in((0,1)if hd else(0,)):
						tot=c0+2*c1+d_;b1=1 if(p1 is None or c1==p1)else 0;sc=(2*_tz((cc-tot)&M32)+b1,-tot,-d_)
						if best is None or sc>best[0]:best=(sc,c0,c1,d_,wc,cc)
		_,c0,c1,dl,wb,cb=best;cv2=(cb-c0-2*c1-dl)&M32;t,rem=_adduc(g,h,u,cv2,c1,ch1);s=g.add3(t,vs[0],wb,c0,None,h[0],u[0]);return(g.add(s,_Y0(rem))if rem else s),fg,dl
	return g.addm(u,_R2(g,e,6,11,25,False),*Wd),fg,0
def _rnd2(g,st,Wd):
	a,b,c,d,e,f,gg,h,prev,hg=st;t1,fg,delta=A3(g,e,f,gg,h,hg,Wd,d);ne=g.add(d,t1,ONE if delta else Aa);ab,mj=[None]*32,[None]*32
	def mb(j):
		ab[j]=g.XOR(a[j],b[j])
		if c[j]==Aa:mj[j]=g.AND(a[j],b[j])
		elif ab[j][0]and prev[j][0]and ab[j][0]!=prev[j][0]and ab[j][1]!=prev[j][1]:mj[j]=g.XOR(g.AND((ab[j][0],ab[j][1]^1),prev[j]),c[j])
		else:mj[j]=g.XOR(g.AND(ab[j],prev[j]),b[j])
		return mj[j]
	if all(x[0]==0 for x in b):
		S0=_R2(g,a,2,13,22,False)
		for j in range(32):mb(j)
		na=g.add3(t1,S0,mj,delta)if delta else g.addm(t1,S0,mj)
	else:g.ahi+=(not delta);na=g.add3(t1,lambda j:_U4(g,a,2,13,22,False,j),mb,delta)
	return(na,a,b,c,ne,e,f,gg,ab,fg)
def _ch3(g,cs,B,e,f,gg,hg,kv):
	X,AN,OR=g.XOR,g.AND,g.OR;fg=[X(f[j],gg[j])for j in range(32)];s,R1,R2,u,U=[None]*32,[None]*32,[None]*32,ONE,Aa
	for i in range(32):
		sm=not(e[i][0]and fg[i][0]and e[i][1]!=fg[i][1]);cp=(gg[i][1]^(e[i][1]&fg[i][1]))if sm else(f[i][1]^e[i][1]^1);z,R1[i],R2[i],x,pt,oU=cs[0][i],cs[1][i],cs[2][i],B[i],U[1]^u[1],i==30;pw5,ok,b1,b2=x[1]^cp,(i in(0,31)and sm),0,0
		if sm and 0<i<31:
			for k in range(3):
				w=cs[k][i];wb=w[1];pw6=wb^pw5;ca=(wb in(cp,x[1]))and(pw6!=pt or pw6!=u[1]);cb=wb==pt and cp!=u[1]
				if ca or cb or(u==ONE and wb==U[1]==pw5!=x[1]):z,R1[i],R2[i],ok,b1,b2=w,cs[k==0][i],cs[2-(k==2)][i],1,ca,cb;break
		w5=X(hg[i],AN(e[i],fg[i]))if ok else X(gg[i]if sm else f[i],AN(e[i]if sm else(e[i][0],e[i][1]^1),fg[i]))
		if i==0:
			if ok:u0=X(z,x);s[0]=X(z,w5);c0=X(AN(u0,w5),x)if z[1]==cp else X(AN(u0,(w5[0],w5[1]^1)),z)
			else:s[0],c0=g.fa(z,x,w5)
			U=(c0[0],c0[1]^1)
		elif i==31:s[31]=X(X(z,w5)if ok else X(X(z,x),w5),U)
		elif not ok:s[i],u,U=g._col((z,x,w5),u,U,oU)
		elif b1:
			w6=X(z,w5);s[i]=X(U,w6);w11=OR(w5,X(x,z)if z[1]==cp else X(x,w6))
			if(z[1]^pw5)!=pt:w9=X(u,w6);w10=OR(U,(w9[0],w9[1]^1));u,U=(Aa if oU else X(w6,(w10[0],w10[1]^1))),X(w10,(w11[0],w11[1]^1))
			else:w9=X(u,s[i]);w10=AN((U[0],U[1]^1),w9);u,U=(Aa if oU else X(w6,w11)),X(w10,w11)
		elif b2:n5=X(z,U);n9=X(x,n5);s[i]=X(w5,n5);n8=OR(U,X(z,u));n11=AN((w5[0],w5[1]^1),n9);u,U=(Aa if oU else X(n5,n11)),X(n8,n11)
		else:n5=X(z,U);w5U=X(w5,U);s[i]=X(w5,n5);g1=OR((x[0],x[1]^1),w5);g2=AN(n5,w5U);u,U=(Aa if oU else X(w5,(g1[0],g1[1]^1))),X(g1,g2)
	return g.addm(s,R1,R2,_Y0(kv)),fg
def _W5(G=Gen):
	g=G(256);g.split={};Y=[[g.inputs[32*(7-k)+j]for j in range(32)]for k in range(8)];W=[None]*ROUNDS
	for i in range(PRE):W[i]=_Y0(_X0[i])
	for k in range(8):pos=_Y1+k;W[pos]=g.addm(Y[k],_Y0((-K[pos])&M32))if pos in _X4 else Y[k]
	for pos,val in _Y4.items():W[pos]=_Y0(val)
	wd=lambda i:(Y[i-_Y1],)if i in _X4 else(_Y0(4 if i==23 else K[i]),W[i]);z,nk9=_Y0(0),_Y0((-K[9])&M32);st=(Y[0],z,z,z,Y[0],z,z,nk9,z,nk9);r=ROUNDS;s0f=lambda A:lambda j:_U4(g,A,7,18,3,True,j);s1f=lambda A:lambda j:_U4(g,A,17,19,10,True,j)
	def _Z4(i):
		if W[i]is not None:return
		if i>=r-2:W[i]=g.add3(W[i-16],s0f(W[i-15]),W[i-7]);return
		if i==21:s0=_R2(g,W[6],7,18,3,True);v=sum(s0[b][1]<<b for b in range(32));g.ahi+=1;W[21]=g.add2c(Y[6],s1f(W[19]),(_X0[5]+v-K[14])&M32);return
		if i>=24 and not _R1[g.ahi]:g.ahi+=1;s=g.add3(W[i-16],s0f(W[i-15]),s1f(W[i-2]),0,W[i-7][0]);W[i]=g.add(s,[Aa]+W[i-7][1:]);return
		w_m7=(Y[i-15],_Y0((-K[i-7])&M32))if i in(17,21,22)else((g.split[tuple(W[16])][0],_Y0(g.split[tuple(W[16])][1]))if i==23 else(W[i-7],));W[i]=g.addm(W[i-16],_R2(g,W[i-15],7,18,3,True),*w_m7,_R2(g,W[i-2],17,19,10,True),_V3=2 if i==23 else None)
	for i in range(9,r):
		if i>=16:
			if i==19:_Z4(19);_Z4(21);s23=g.add3(s0f(W[8]),g.split[tuple(W[16])][0],s1f(W[21]),2);cv23=(4-K[23])&M32
			elif i==23:W[23]=s23;g.split[tuple(s23)]=(s23,cv23)
			else:
				_Z4(i)
				if i==31:_Z4(32)
		if i<r-NTAIL:
			st=_rnd2(g,st,wd(i))
			if i==23:s_r,cv_r=g.split[tuple(W[i])];W[i]=g.add(s_r,_Y0(cv_r))
	if Ap:a6,a7,a8,a9,e6,e7,e8,e9,prev,hg=st;T5,fg,_=A3(g,e6,e7,e8,e9,hg,(_Y0(K[r-6]-1),W[r-6]));e5=g.add(a9,T5,ONE);mj=[g.OR((ab[0],ab[1]^1),a8[j])if(QM>>j)&1 else g.AND(ab,a8[j])for j in range(32)for ab in(g.XOR(a6[j],a7[j]),)];Q=g.add(T5,mj,ONE);T4,fg,_=A3(g,e5,e6,e7,e8,fg,wd(r-5));e4=g.add(a8,T4);e3,fg=_ch3(g,[a7,W[r-4],_R2(g,e4,6,11,25,False)],e7,e4,e5,e6,fg,K[r-4]-2);e2,_=_ch3(g,[a6,W[r-3],_R2(g,e3,6,11,25,False)],e6,e3,e4,e5,fg,K[r-3]-2);X=g.addm(W[r-2],_R2(g,W[r-4],17,19,10,True),e5,[g.OR(e2[j],e4[j])if(XM>>j)&1 else g.AND((e2[j][0],e2[j][1]^1),e4[j])for j in range(32)]);Y_out=g.addm(W[r-1],_R2(g,W[r-3],17,19,10,True),e4);bw=[e3,e2,a7,a6,Q,T4,X,Y_out];out=[bw[PERM[k]]for k in range(8)];assert g.ahi==len(_R1);return g,[t for w in out for t in w]
MAX_NODES=57894;MAX_RECORDS=57637;_Q1=8
class BGen(Gen):
	def __init__(self,n,run,pas):self.n,self.run,self.pas,self.calls=n,run,pas,0;self.ahi=0;self.inputs=[(j+1,0)for j in range(n)];self.nn,self.rn,self.ncse,self._U0=n+1,0,0,0;self.recent,self.cse_k,self.cse_v=[None]*8,[0]*1024,[None]*1024
	def _gate(self,node):
		for d in range(min(8,self.rn)):
			r=self.recent[(self.rn-1-d)&7]
			if r[3]==node:return r[:3]
		return None
	def _new(self,op,a,b):
		k,self.nn=self.nn,self.nn+1
		if k>=MAX_NODES:self.run.err=1;return 0
		if self.pas==0:
			if self.run.uses[a]==255 or self.run.uses[b]==255:self.run.err=6
			self.run.uses[a]+=1;self.run.uses[b]+=1
		else:self.run.alloc(op,k,a,b)
		return k
	def mk(self,op,x,y):
		self.calls+=1
		if x>y:x,y=y,x
		a,b=x,y
		if b<=256:
			key=({"x":1,"a":2,"o":3}[op])|(a<<2)|(b<<11);p=((key*2654435761)&M32)>>22;probes=1
			while self.cse_k[p]:
				if self.cse_k[p]==key:self._U0=max(self._U0,probes);return self.cse_v[p]
				p=(p+1)&1023;probes+=1
				if probes>_Q1:self.run.err=16;return 0
			self._U0=max(self._U0,probes);self.ncse+=1
			if self.ncse>900:self.run.err=10
			s=self._new(op,a,b);self.cse_k[p],self.cse_v[p]=key,s
		else:
			for d in range(min(8,self.rn)):
				r=self.recent[(self.rn-1-d)&7]
				if r[:3]==(op,a,b):return r[3]
			s=self._new(op,a,b)
		self.recent[self.rn&7]=(op,a,b,s);self.rn+=1;return s
_M8,_M14=(1<<288)-(1<<256),(1<<480)-(1<<448);_MF=((1<<512)-(1<<384),(1<<512)-(1<<416),(1<<512)-(1<<448),_M14,0)
def _pick(f,p):
	for q in(p,*_MF):
		if f&~q:m=f&~q;return(m&-m).bit_length()-1
	return-1
def _patch(R):
	s=GEN_C.split('PT[]="')[1].split('"')[0];R=list(R);ap=[];b=0;q=lambda p:p+sum(d for x,d in ap if x<p)
	while s:
		n=int(s[0],16);s=s[1:];sp=[]
		if n>7:
			n-=8;m=int(s[0],16);s=s[1:]
			for _ in range(m):
				k=q(int(s[:5],16));F=int(s[5:8],16);s=s[8:];o,d,a,c=R[k];R[k]=o,F,a,c;e=-1
				while e!=d:k+=1;o,e,a,c=R[k];R[k]=o,e,[a,F][a==d],[c,F][c==d]
		for i in range(n):
			v=int(s[:4],16);L=int(s[4],16);N=int(s[5],16);s=s[6:]
			if i==0:b+=v;f=p=b
			else:p=f+v
			sp+=[(p,L,N)]
		t=[]
		for p,L,N in sp:
			for o,d,a,c in R[q(p):q(p)+L]:
				for r in(a,c,d):
					if r not in t:t.append(r)
		w=[]
		for p,L,N in sp:w+=[[((v&3)+1,t[v>>2&15],t[v>>6&15],t[v>>10&15])for v in[int(s[4*j:4*j+4],16)for j in range(N)]]];s=s[4*N:]
		for(p,L,N),z in reversed(list(zip(sp,w))):R[q(p):q(p)+L]=z;ap+=[(p,N-L)]
	return R
class BoundedEmitter:
	def __init__(self):self.uses,self.err,self.records=[0]*MAX_NODES,0,[]
	def emit(self,op,d,a,b):
		if len(self.records)>=MAX_RECORDS or max(d,a,b)>=1024:self.err=5;return
		self.records.append((op,d,a,b))
	def take(self,_R4=None,p=0):
		r=_R4 if _R4 is not None and self.free>>_R4&1 else _pick(self.free,p)
		if r<0:self.err=8;return 0
		self.free&=~(1<<r);return r
	def alloc(self,op,k,x,y):
		self.uses[x]-=1;self.uses[y]-=1;dx,dy=self.uses[x]==0,self.uses[y]==0;w=256+self.order[self.co][1]if self.co<len(self.order)and self.order[self.co][0]==k else None;b=~((self.pend if k<self.f0-1800 else self.pend&~_M14)&~_M8)if self.uses[k]<=3 and k<self.f1-1800 and w is None else self.pend;okx=dx and(not(b>>self.reg[x]&1)or self.reg[x]==w);oky=dy and(not(b>>self.reg[y]&1)or self.reg[y]==w);dst=self.take(w)if w is not None and self.free>>w&1 else w if(dx and self.reg[x]==w)or(dy and self.reg[y]==w)else self.reg[x]if okx else self.reg[y]if oky else None
		if dx and self.reg[x]!=dst:self.free|=1<<self.reg[x]
		if dy and self.reg[y]!=dst:self.free|=1<<self.reg[y]
		if dst is None:dst=self.take(p=b)
		if dst==w:self.pend&=~(1<<dst)
		self.emit({"x":1,"a":2,"o":3}[op],dst,self.reg[x],self.reg[y]);self.reg[k]=dst
		while self.co<len(self.order)and self.order[self.co][0]==k:self.oreg[self.order[self.co][1]]=dst;self.co+=1
		if not self.uses[k]:self.err=9;self.free|=1<<dst
	def run(self):
		g0,out0=_W5(lambda n:BGen(n,self,0));nodes,self.calls=g0.nn,g0.calls;self.onode=[x[0]for x in out0];self.oneg=[x[1]for x in out0];self.order=sorted((n,i)for i,n in enumerate(self.onode)if n)
		for n,_ in self.order:self.uses[n]+=1
		self.f0,self.f1=self.order[0][0],self.order[32][0];self.free=sum(1<<r for r in range(_X1)if r<256 or r>=512);self.pend=sum(1<<(256+i)for i,n in enumerate(self.onode)if n);self.reg={n:_Q2(n-1)for n in range(1,257)};self.oreg,self.co=[0]*256,0
		while self.co<len(self.order)and self.order[self.co][0]<=256:n,i=self.order[self.co];self.oreg[i]=_Q2(n-1);self.co+=1
		for n in range(1,257):
			if not self.uses[n]:self.free|=1<<_Q2(n-1)
		g1,out1=_W5(lambda n:BGen(n,self,1));self.calls+=g1.calls;self._U0=max(g0._U0,g1._U0);assert out1==out0 and self._U0<=_Q1;self.records=_patch(self.records);Ax=[(i,self.oreg[i])for i,n in enumerate(self.onode)if n and self.oreg[i]!=256+i];moves=0
		while Ax:
			srcs=[s for _,s in Ax];k=next((k for k,(i,s)in enumerate(Ax)if 256+i not in srcs),None)
			if k is None:s,t=Ax[0][1],self.take();self.emit(4,t,s,0);moves+=1;Ax=[(i,t if r==s else r)for i,r in Ax]
			else:i,s=Ax.pop(k);self.emit(4,256+i,s,0);moves+=1
		for i,n in enumerate(self.onode):
			if not n:self.emit(5,256+i,self.oneg[i],0)
		top=max(max(r[1:4])if r[0]<=3 else max(r[1:3])if r[0]==4 else r[1]for r in self.records)+1;q=sum(self.oneg[i]<<(32*(7-i//32)+i%32)for i in range(256)if self.onode[i]);counts=[sum(r[0]==op for r in self.records)for op in(1,2,3)];info=(len(self.records),top,nodes,self.calls,moves,self.err,*counts,4*MAX_RECORDS,COUNTERS,MAX_NODES,_W3,len(_R1),_W2);return info,q,self.records
def _S1(records):
	out=bytearray()
	for op,d,a,b in records:assert 1<=op<=3 and max(d,a,b)<1024;out+=((op-1)|(d<<2)|(a<<12)|(b<<22)).to_bytes(4,"little")
	return bytes(out)
def bounded_check(pr):info,q,records=BoundedEmitter().run();py=[({"^":1,"&":2,"|":3,"M":4,"S":5}[o],d,a,b)for o,d,a,b in pr.recs];assert info==EXPECTED_EMITTER_INFO;assert q==pr.qint==_T5 and records==py;assert hashlib.sha256(GEN_C.encode()).hexdigest()==_X3;stream=_S1(records);digest=hashlib.sha256(stream).hexdigest();assert len(stream)==4*pr.instr and digest==_Y3;return info,digest
def _alloc(g,nin,fixed,outs,tgt,free0,E):
	N=g.nodes;uses=[0]*len(N);want={}
	for _,x,y in N[nin+1:]:uses[x]+=1;uses[y]+=1
	for i,(n,_)in enumerate(outs):uses[n]+=1;want.setdefault(n,tgt[i])
	oids=sorted(want);f0,f1=oids[0],oids[32];reg=dict(fixed);free=sum(1<<r for r in free0 if r not in fixed.values())|sum(1<<r for v,r in fixed.items()if not uses[v]);pend=sum(1<<tgt[i]for i,(n,_)in enumerate(outs)if n)
	def take(w=None,p=0):nonlocal free;r=w if w is not None and free>>w&1 else _pick(free,p);free&=~(1<<r);return r
	for k in range(nin+1,len(N)):
		op,x,y=N[k];uses[x]-=1;uses[y]-=1;dying=[v for v in(x,y)if not uses[v]];w=want.get(k);p=~((pend if k<f0-1800 else pend&~_M14)&~_M8)if(uses[k]<=3 and k<f1-1800 and w is None)else pend;ok=[reg[v]for v in dying if not p>>reg[v]&1 or reg[v]==w];dst=take(w)if w is not None and free>>w&1 else w if any(reg[v]==w for v in dying)else ok[0]if ok else None
		for v in dying:
			if reg[v]!=dst:free|=1<<reg[v]
		if dst is None:dst=take(p=p)
		reg[k]=dst
		if dst==w:pend&=~(1<<w)
		E(({"x":"^","a":"&","o":"|"}[op],dst,reg[x],reg[y]))
	return sum(reg[n]!=tgt[i]for i,(n,_)in enumerate(outs)if n)
def _Q2(j):return 256+32*(7-j//32)+j%32
def Am():info,q,records=BoundedEmitter().run();assert info[4:6]==(0,0);_QM[:]=[q];return[({1:"^",2:"&",3:"|"}[op],d,a,b)for op,d,a,b in records],info[4],info[3]
class Prog:
	def __init__(self):self.recs,self.moves,self.calls=Am();self.q,self.qint,self.pin=[0]*256,_QM[0],[0]*256;self.qwords=[(self.qint>>(32*i))&M32 for i in range(8)];self.instr=self.kernel=len(self.recs);self.nregs=max(max(r[1:4])for r in self.recs)+1;self.compile()
	def run(self,pc,end,regs):
		for op,d,a,b in self.recs[pc:end]:regs[d]=regs[a]^regs[b]if op=="^"else regs[a]&regs[b]if op=="&"else regs[a]|regs[b]
		return end-pc
	def compile(self):
		ns,fs={"ALL":ALL},[]
		for a in range(0,len(self.recs),4096):exec(compile("def c(r):\n"+"".join(" r[%d]=r[%d]%sr[%d]\n"%(d,x,o,y)for o,d,x,y in self.recs[a:a+4096]),"<p>","exec"),ns);fs.append(ns["c"])
		self.ns=ns;self.fast=lambda r:[c(r)for c in fs]
	def step(self,*planes):
		regs=[0]*_X1
		for j,pl in enumerate(planes):regs[_Q2(j)]=pl
		self.fast(regs);return[regs[_Q2(j)]for j in range(len(planes))]
_TM={1<<k:sum(1<<c for c in range(256)if not c>>k&1)for k in range(8)}
def _U1(rows):
	R=list(rows)+[0]*(256-len(rows));s=128
	while s:
		m=_TM[s]
		for i in range(256):
			if not i&s:t=((R[i]>>s)^R[i+s])&m;R[i+s]^=t;R[i]^=t<<s
		s>>=1
	return R
def _V0(xs,n,pin):T=_U1(xs);return[T[j]^(ALL if pin[j]else 0)for j in range(n)]
def _T1(planes,n,pin):T=_U1([planes[j]^(ALL if pin[j]else 0)for j in range(n)]);return T[:256]
def _Z5(planes,l,pin,n):
	x=0
	for j in range(n):x|=(((planes[j]>>l)&1)^pin[j])<<j
	return x
def _W4(planes,l,x,pin,n):bit=1<<l;return[(planes[j]&~bit)|((((x>>j)&1)^pin[j])<<l)for j in range(n)]
Au=Fraction(497,1000);Ai=Fraction(15,100000);Ad=1e-6;CMAX=7;CUT_HALT_ORDER=CMAX+1;P_MIN=0.390000001;GRAIN=10**21;STAGE1_PLANES=20;PFP=12;GC=0;GT=3;PM=2;_T4=3;A7=2800;Ah=3800;A8=4200;Ae=1300;_X2=39;_S4=5;_S5=4;_S2=5;Ag=36;HANDLER_CODE,_U5,RECOVERY_CODE=1250,160,94;_X1=871;REGFILE=_X1*32;COUNTERS=16384;PLANE_COPY=LANES*32;ARRAY_BYTES=(2*ROUNDS-16)*32;ARRAYS=0;KEYB=47;GROUP=256;GROUP_BYTES=KEYB*32;assert ARRAY_BYTES<=PLANE_COPY<=COUNTERS;MEM_LIMIT=1<<20;ADVICE=0;KAPPA_256=35;KR=Fraction(62,5);KCHK=8192;A9=80;Af=100;WASM_RUN_OPERATORS=132267323;WASM_OPERATOR_FACTOR=2;WASM_EMITTER_INSTR=10332;_W3,_W2=EXPECTED_EMITTER_INFO[12],EXPECTED_EMITTER_INFO[14];SETUP_FIXED=256*3100+20000;_Z1=64+1+3*192+1000;_W1=37;_V1=25;_S0=_W1+_V1*10+2;_T0=1+2*_S0;SEARCH_EVAL_OPS=1<<48;_U2=_Z1*SEARCH_EVAL_OPS;_Y2=_T0*SEARCH_EVAL_OPS;CFG={16:dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),18:dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),256:dict(s1=20,W=102,kappa=KAPPA_256,Sb=1<<48)}
CJ,CASC=10,((10,12,7),(12,14,5),(14,16,5),(16,18,5),(18,20,6));S1U=CJ+1;GOV=sum(c[2]for c in CASC)+2;S1REC=S1U+GOV
def pcap(p,k):f=(1+Fraction(1,1<<20))*p["B"]*(1-Fraction((1<<k)-1,1<<k)**LANES)+Fraction(120*(p["c"]+p["Sb"]),1<<k);return-(-f.numerator//f.denominator)+64
def pbud(p):return sum(w*pcap(p,k)for k,_,w in CASC)
def stage1c(P,cnt):
	a=0
	for q in P[:CJ]:a|=q
	for k,e,w in CASC:
		if a==ALL:return 0
		cnt["g"]-=w
		if k==CJ and cnt["g"]<0:raise Av()
		for q in P[k:e]:a|=q
	return a^ALL
def stage1(planes,s1,pin):
	nz,pos,neg=0,[planes[j]for j in range(s1)if not pin[j]],[planes[j]for j in range(s1)if pin[j]]
	for q in pos:nz|=q
	if neg:
		a=ALL
		for q in neg:a&=q
		nz|=a^ALL
	return ALL^nz
def _Y5(lanes=LANES,eps=Ad):
	m=lanes
	while True:
		x=m/lanes
		if exp(-lanes*(x-1-log(x)))<=eps:return m
		m+=1
Aq=_Y5()
def A4(n,Tp,kappa,tmax,Sb):
	c=CFG[n];s1,W=c["s1"],c["W"];N,D=1<<n,s1+W;L=Fraction(1<<D,Tp)
	if n==256:B=_b256(Tp,tmax,kappa,Sb)
	else:ureq=isqrt(2*N*Au.numerator//Au.denominator)+2;num,den=ureq+Aq*L+1,Ai.denominator;q=-(-(num*den)//(den-Ai.numerator));B=-(-q//LANES)
	cc=-(-kappa*L.numerator//L.denominator);fb=(Tp-1).bit_length();cr=-(-(KR*L.numerator)//L.denominator)if n==256 else cc+Sb;kchk=table_bytes(tmax)//64-1 if n==256 else KCHK
	if n==256:assert kchk>=1 and(kchk+1)*64<=table_bytes(tmax)
	return dict(n=n,s1=s1,W=W,D=D,Tp=Tp,fb=fb,kb=min(KEYB-fb,n-D),L=L,N=N,Q=B*LANES,B=B,kappa=kappa,Sb=Sb,c=cc,capr=cc+Sb,cr=cr,kchk=kchk,tmax=tmax,e2max=2*B*LANES//(1<<s1)+64,cmax=CMAX if n==256 else 10**9)
def tail_log2(mean,k):return(-mean+k*(1+log(mean/k)))/log(2)
Ao=[];_QM=[0]
def Az():
	global REGFILE
	if not Ao:Ao.append(Prog());REGFILE=32*(Ao[0].nregs+5)
	return Ao[0]
def machine_constants(pr=None):pr=pr or Az();pf=S1U;code=pr.instr*_S5+rec().instr*_S2+(S1REC+GC+_T4+HANDLER_CODE+RECOVERY_CODE+_U5)*_S4;return pr.kernel,pf,pr.kernel+pf+_T4,code,(MEM_LIMIT-code-REGFILE-COUNTERS-ADVICE-ARRAYS)//GROUP_BYTES*GROUP-LANES-CMAX
def table_bytes(tmax):return-(-(tmax+LANES+CMAX)//GROUP)*GROUP_BYTES
def boundary_test(pr,p):stream=_S1([({"^":1,"&":2,"|":3}[o],d,a,b)for o,d,a,b in pr.recs]);assert len(stream)==4*pr.instr and all(max(r[1:])<1024 for r in pr.recs);_Q3=(((1<<p["kb"])-1)<<p["fb"])|(p["Tp"]-1);assert 0<_Q3+1<1<<KEYB;assert p["tmax"]+LANES+CMAX<1<<18;rp=rec();control=rp.init+rp.flat;assert len({r[0]for r in control})<=16 and all(max(r[1:])<1024 for r in control);assert table_bytes(p["tmax"])==-(-(p["tmax"]+LANES+CMAX)//GROUP)*GROUP_BYTES;return dict(body_bytes=len(stream),max_register=max(max(r[1:])for r in pr.recs),_Q3=_Q3,max_trail=p["tmax"]+LANES+CMAX-1,control_opcodes=len({r[0]for r in control}),control_max_field=max(max(r[1:])for r in control))
def _T2():Ak=1024;raw=2*160*64*32*13*13*12*Ak;assert 2*raw<SEARCH_EVAL_OPS;assert _Z1==1641 and _S0==289 and _T0==579;return raw,raw
def plan(n,kappa=None,Tp=None):
	if n!=256:c=CFG[n];p=A4(n,c["Tp"],c["kappa"],0,c["Sb"]);p["tmax"]=4*(p["Q"]//int(p["L"]))+64;return p
	kappa=kappa or KAPPA_256;tmax=machine_constants()[4]
	if Tp:return A4(256,Tp,kappa,tmax,CFG[256]["Sb"])
	lo,hi=1.0,float(tmax-59)
	for _ in range(60):mid=(lo+hi)/2;lo,hi=(mid,hi)if tail_log2(mid,tmax-59)<=-20 else(lo,mid)
	a,z=1,4097
	while z-a>1:m=(a+z)//2;a,z=(m,z)if _lossq(m,lo,tmax,kappa,CFG[256]["Sb"])["P_lower"]>=P_MIN else(a,m)
	return min((A4(256,t,kappa,tmax,CFG[256]["Sb"])for t in(a,a+1)),key=lambda p:(p["B"],p["Tp"]))
def Ay(p,pk):D=-(-p["cr"]//p["kchk"]);return p["cr"]*(pk+_X2)+p["kchk"]*A9+17*D*(pk+_X2)+16*Af+600+len(rec().init)
def ledger(p=None,pr=None):p=p or plan(256);pr=pr or Az();_T2();ph,filt,body,code,_=machine_constants(pr);emitter=WASM_OPERATOR_FACTOR*WASM_RUN_OPERATORS+1;parts=dict(main=body*p["B"],stage1_pass=pbud(p)+GOV,slices=-(-p["B"]//p["Sb"])*Ae,stage1_hits=p["e2max"]*A7,events=(p["tmax"]+1)*(Ah+6*(p["tmax"]+LANES+CMAX)),cuts=p["cmax"]*A8,recovery=Ay(p,_Q4()),setup=SETUP_FIXED+emitter,offset_search=_U2,selector_search=_Y2);return dict(parts=parts,total=sum(parts.values()),plan=p,body=body,emitter=emitter)
TB=18;FINE,COARSE=20000,2000
def _lossq(Tp,q,tmax,kappa,Sb,rate=1.0):
	D=122;L=Fraction(1<<D,Tp);c=-(-kappa*L.numerator//L.denominator);th,Lf,cf=Tp/2.0**D,float(L),float(c);Q,B,Np=q*Lf,q*Lf/LANES,2.0**256/rate;k=int(q)+1
	while tail_log2(q,k)>-40:k+=1
	n2,shift=k+LANES+CMAX,1/(1-k*Q/Np);pi=lambda m:exp(-m*(m-1)/(2*Np));split=max(1.0,Q-120*LANES*Lf);edges=[split*i/COARSE for i in range(COARSE+1)]+[split+(Q-split)*i/FINE for i in range(1,FINE+1)];delay,pa=0.0,1.0
	for b in edges[1:]:pb=pi(b);delay+=(pa-pb)*exp(-th*max(0.0,B-b/LANES));pa=pb
	p,ql,hq=exp(-cf*th),Q*Lf/Np,Q*(Q-1)/(2*Np);p2=exp(-(cf-1)*th)*(1+(cf-1)*th/(1-th));kr=float(KR)*Lf;prec=2*hq*exp(-(kr-1)*th)*(1+(kr-1)*th/(1-th));hh=(Q*(Q-1)/2+2.0**TB*Q)/Np;cuts=1-sum(comb(n2,j)*p**j*exp((n2-j)*log1p(-p))for j in range(CUT_HALT_ORDER));t=dict(no_collision=pi(Q)*shift,delay=delay*shift,partner_own_trail=ql,partner_cut_trail=(cf+Sb)*Q*p*(q+LANES)/((1-p)*Np),too_old=hq*p2,P_rec=prec,rest_of_path=hq*Lf*(Q+2.0**TB)/Np,finished_count=2.0**-40,cut_halt=cuts+ql*(1+(2+kappa)*exp(-kappa/2)+2*hq)+hq*p*(3+2*kappa),key_false_match=tmax*(tmax-1)/2*2.0**-(min(KEYB-(Tp-1).bit_length(),256-D)+log2(Tp)),table_capacity=2.0**tail_log2(q,tmax-59),misc=Q*2.0**TB/Np+k*k*Lf/Np+255*Q/Np+exp(min(700.0,-300+(exp(5)-1)*hh))+2.0**-90,passbudget=2.0**-90);t["sum"]=sum(t.values());t["P_lower"]=1-t["sum"];t.update(trails=q,k=k);return t
_B={}
def _b256(Tp,tmax,kappa,Sb):
	if(Tp,tmax,kappa)not in _B:
		L=Fraction(1<<122,Tp);lo,hi=1.0,float(tmax-59)
		for _ in range(50):mid=(lo+hi)/2;lo,hi=(mid,hi)if tail_log2(mid,tmax-59)<=-15.5 else(lo,mid)
		q_hi=lo;lo,hi=1.0,q_hi
		for _ in range(40):mid=(lo+hi)/2;lo,hi=(lo,mid)if _lossq(Tp,mid,tmax,kappa,Sb)["P_lower"]>=P_MIN else(mid,hi)
		B=-(-int(hi*L/LANES)//GRAIN)*GRAIN
		while _lossq(Tp,float(B*LANES/L),tmax,kappa,Sb)["P_lower"]<P_MIN:B+=GRAIN
		_B[(Tp,tmax,kappa)]=B
	return _B[(Tp,tmax,kappa)]
def loss(p,rate=1.0):return _lossq(p["Tp"],float(p["Q"]/p["L"]),p["tmax"],p["kappa"],p["Sb"],rate)
class Av(Exception):pass
class DigestNet:
	def __init__(self,qint):
		assert Ap;g=Gen(256);E=[[(g.inputs[32*(7-k)+j][0],(qint>>(32*(7-k)+j))&1)for j in range(32)]for k in range(8)];S0=lambda x:_R2(g,x,2,13,22,False);S1=lambda x:_R2(g,x,6,11,25,False);mj=lambda a,b,c:[g.XOR(g.AND(g.XOR(a[j],b[j]),g.XOR(b[j],c[j])),b[j])for j in range(32)];ch=lambda e,f,gv:[g.XOR(gv[j],g.AND(e[j],g.XOR(f[j],gv[j])))for j in range(32)];neg=lambda x:[(s[0],s[1]^1)for s in x];bw=[None]*8
		for k in range(8):bw[PERM[k]]=E[k]
		e3,e2,a7,a6,Q,T4,X,Y=bw;a5=g.addm(Q,[Aa if(QM>>j)&1 else g.AND(a6[j],a7[j])for j in range(32)],neg([g.AND((a6[j][0],a6[j][1]^1),(a7[j][0],a7[j][1]^1))if(QM>>j)&1 else Aa for j in range(32)]),_Y0(1),S0(a6));a4=g.addm(T4,S0(a5),mj(a5,a6,a7));a3=g.addm(e3,neg(a7),_Y0(1),S0(a4),mj(a4,a5,a6));a2=g.addm(e2,neg(a6),_Y0(1),S0(a3),mj(a3,a4,a5));t1=g.addm(X,[Aa if(XM>>j)&1 else g.AND(e2[j],e3[j])for j in range(32)],neg([g.AND(e2[j],(e3[j][0],e3[j][1]^1))if(XM>>j)&1 else Aa for j in range(32)]),_Y0((1+K[ROUNDS-2])&M32),S1(e2));e1=g.add(a5,t1);a1=g.addm(t1,S0(a2),mj(a2,a3,a4));t0=g.addm(Y,S1(e1),ch(e1,e2,e3),_Y0(K[ROUNDS-1]));st=[g.addm(t0,S0(a1),mj(a1,a2,a3)),a1,a2,a3,g.add(a4,t0),e1,e2,e3];cv=[g.addm(w,_Y0(v))for w,v in zip(st,IV)];a,b,c,d,e,f,gg,h=cv
		for kw in _KW2:t1=g.addm(h,S1(e),ch(e,f,gg),_Y0(kw));t2=g.add(S0(a),mj(a,b,c));a,b,c,d,e,f,gg,h=g.add(t1,t2),a,b,c,g.add(d,t1),e,f,gg
		dw=[g.add(x,y)for x,y in zip(cv,[a,b,c,d,e,f,gg,h])];self.out=[dw[7-i//32][i%32]for i in range(256)];ops,N={"x":"^","a":"&","o":"|"},g.nodes;last,slot,free,src,m={},list(range(257))+[0]*(len(N)-257),[],[],257
		for k in range(257,len(N)):last[N[k][1]]=last[N[k][2]]=k
		for s in self.out:last[s[0]]=len(N)
		for k in range(257,len(N)):
			o,x,y=N[k];free+=[slot[z]for z in{x,y}if last[z]==k]
			if free:slot[k]=free.pop()
			else:slot[k],m=m,m+1
			src.append(" v[%d]=v[%d]%sv[%d]"%(slot[k],slot[x],ops[o],slot[y]))
			if k not in last:free.append(slot[k])
		self.out=[(slot[s[0]],s[1])for s in self.out];ns,self.fs={},[]
		for i in range(0,len(src),4096):exec(compile("def c(v):\n"+"\n".join(src[i:i+4096])+"\n","<d>","exec"),ns);self.fs.append(ns["c"])
		self.nn=m
	def step(self,planes,k=256,a=ALL):
		v=[0]*self.nn;v[1:257]=planes
		for c in self.fs:c(v)
		return[v[s[0]]^(a if s[1]else 0)for s in self.out[:k]]
_DN=[]
def dnet():
	if not _DN:_DN.append(DigestNet(Az().qint))
	return _DN[0]
class Aw:
	def __init__(self,n):self.n,self.pr,self.pin=n,Az(),[0]*n
	def _low(self,o):return _V4(o,self.pr.qint)&((1<<self.n)-1)
	def step(self,*planes):return dnet().step(list(self.pr.step(*(list(planes)+[0]*(256-len(planes))))))[:self.n]
	def wstep(self,P):n,a,ns=self.n,(1<<256*len(P))-1,self.pr.ns;W=[sum(q[j]<<256*i for i,q in enumerate(P))for j in range(n)];ns["ALL"]=a;o=dnet().step(self.pr.step(*(W+[0]*(256-n))),n,a);ns["ALL"]=ALL;return[[(x>>256*i)&ALL for x in o]for i in range(len(P))]
	def f2(self,xs):return[self._low(o)for o in _V2(xs,256,self.pr.qwords)]
	def _Z2(self,x):return _Q0(_R0(words_of(x)))&((1<<self.n)-1)
def A0(x,p):return x&((1<<p["s1"])-1)==0 and(x>>p["s1"])&((1<<p["W"])-1)<p["Tp"]
def dp_key(x,p):return(((x>>p["D"])&((1<<p["kb"])-1))<<p["fb"])|((x>>p["s1"])&((1<<p["fb"])-1))
def walk(xs,k,f2):
	for _ in range(k):xs=f2(xs)
	return xs
def recover(p,r,t0,t1,f2,kchk=None):
	mask,cr=p["N"]-1,p["cr"];kchk=kchk or p["kchk"];D=-(-cr//kchk);xs,ls,ends=[(r+t0)&mask,(r+t1)&mask],[None,None],[None,None];ck=[[xs[0]],[xs[1]]]
	for k in range(1,cr+1):
		xs=f2(xs)
		for i in(0,1):
			if ls[i]is None:
				if k%D==0:ck[i].append(xs[i])
				if A0(xs[i],p):ls[i],ends[i]=k,xs[i]
		if None not in ls:break
	else:raise Av()
	a=0 if ls[0]>=ls[1]else 1;lb,(qd,rd)=ls[1-a],divmod(abs(ls[0]-ls[1]),D);A=lambda i:walk([ck[a][i+qd]],rd,f2)[0]
	if ends[0]!=ends[1]or A(0)==ck[1-a][0]:return None
	lo,hi=0,lb//D+1
	while hi-lo>1:mid=(lo+hi)//2;lo,hi=(lo,mid)if A(mid)==ck[1-a][mid]else(mid,hi)
	x,y=A(lo),ck[1-a][lo]
	for _ in range(min(hi*D,lb)-lo*D):
		fx,fy=f2([x,y])
		if fx==fy:
			if p["n"]==256:s0,s1=enc_invert(words_of(_W0(x))),enc_invert(words_of(_W0(y)));assert s0==s1==_R0(words_of(x))
			return x,y
		x,y=fx,fy
	return None
	for _ in range(b[1]+1):
		ya,yb=f2(xs)
		if ya==yb:
			if p["n"]==256:s0,s1=enc_invert(words_of(_W0(xs[0]))),enc_invert(words_of(_W0(xs[1])));assert s0==s1==_R0(words_of(xs[0]))
			return xs[0],xs[1]
		xs=[ya,yb]
	return None
def search(eng,p,r,cnt):
	g,x=Ac(eng,p,r,cnt),None
	try:
		while True:x=g.send(x and eng.step(*x))
	except StopIteration as e:return e.value
def Ac(eng,p,r,cnt):
	n,mask,pin=p["n"],p["N"]-1,eng.pin;table,_X5,ts,nxt=[],[0]*LANES,list(range(LANES)),LANES;planes=_V0([(r+t)&mask for t in ts],n,pin);cnt["inserts"]+=LANES;batches=0;cnt["g"]=pbud(p)if n==256 else 0
	while batches<p["B"]:
		planes=list((yield planes));batches+=1;cnt["batches"]+=1;hit=stage1c(planes,cnt)if n==256 else stage1(planes,p["s1"],pin)
		while hit:
			cnt["stage1_hits"]+=1
			if cnt["stage1_hits"]>p["e2max"]:raise Av()
			l=(hit&-hit).bit_length()-1;hit&=hit-1;x=_Z5(planes,l,pin,n)
			if A0(x,p):
				key=dp_key(x,p);cnt["finished"]+=1;w=key+1
				if w in table:
					t0=table.index(w);cnt["recoveries"]+=1;res=recover(p,r,t0,ts[l],eng.f2)
					if res is None:raise Av()
					return res
				if cnt["finished"]>p["tmax"]:raise Av()
				assert 0<w<1<<KEYB and ts[l]<p["tmax"]+LANES+p["cmax"];table+=[0]*(ts[l]+1-len(table));table[ts[l]]=w;ts[l],nxt,_X5[l]=nxt,nxt+1,batches;planes=_W4(planes,l,(r+ts[l])&mask,pin,n);cnt["inserts"]+=1
		if batches%p["Sb"]==0:
			for l in range(LANES):
				if batches-_X5[l]>=p["c"]:
					cnt["cut"]+=1
					if cnt["cut"]>p["cmax"]:raise Av()
					ts[l],nxt,_X5[l]=nxt,nxt+1,batches;planes=_W4(planes,l,(r+ts[l])&mask,pin,n);cnt["inserts"]+=1
	return None
class Counters(dict):
	def __missing__(self,k):return 0
def _U3(seed,tag,bits=256):return int.from_bytes(hashlib.shake_256(("%s/%s"%(seed,tag)).encode()).digest((bits+7)//8),"little")&((1<<bits)-1)
def attempt(eng,p,seed,tag):
	cnt=Counters()
	try:res=search(eng,p,_U3(seed,tag,p["n"]),cnt)
	except Av as e:cnt["halt"]+=1;res=None
	return res,cnt
At=16;M_T2,B_T2=256,16
def A2(trials):
	eng,p,G,C,R,cur=Aw(At),plan(At),{},{},{},{}
	def adv(i,v):
		try:cur[i]=G[i].send(v);return
		except StopIteration as e:R[i]=e.value
		except Av:C[i]["halt"]+=1
		del cur[i]
	for i,t in enumerate(trials):C[i]=Counters();G[i]=Ac(eng,p,_U3(t["seed"],"t",p["n"]),C[i]);adv(i,None)
	while cur:
		ks=list(cur)
		for i,o in zip(ks,eng.wstep([cur[i]for i in ks])):adv(i,o)
	return[e1_obs(R.get(i),C[i])for i in range(len(trials))]
def e1_obs(res,cnt):obs=dict(target_ok=int(res is not None),batches=cnt["batches"],halt=cnt["halt"]);return(None,None,obs)if res is None else(message(res[0]),message(res[1]),obs)
def Al(seed,tr,st):
	src,z=tr%3,[0]*256
	if src==0:xs=[_U3(seed,"u%d"%i)for i in range(M_T2)]
	elif src==1:r=_U3(seed,"r");xs=[(r+i)&ALL for i in range(M_T2)]
	else:
		xs,cur=[],[_U3(seed,"c%d"%l)for l in range(LANES)]
		for _ in range(M_T2//LANES):cur=_T1(list(st.step(*_V0(cur,256,st.pin))),256,st.pin);xs+=cur
	digs=[]
	for b in range(M_T2//LANES):digs+=_T1(dnet().step(list(st.step(*_V0(xs[b*LANES:(b+1)*LANES],256,st.pin)))),256,z)
	first,pair={},None
	for i,d in enumerate(digs):
		c=d&((1<<B_T2)-1)
		if c in first and xs[first[c]]!=xs[i]and pair is None:pair=(xs[first[c]],xs[i])
		first.setdefault(c,i)
	obs=dict(source=src,dup_w0=len(digs)-len(first));return(None,None,obs)if pair is None else(message(pair[0]),message(pair[1]),obs)
def serve(req):
	eid,out=req["experiment_id"],[];bounded_check(Az())
	if eid=="bssha-n16":rows=A2(req["trials"])
	elif eid=="proj-k0-w256":st=Az();rows=[Al(t["seed"],t["trial"],st)for t in req["trials"]]
	else:raise ValueError("unknown experiment")
	for t,(a,b,obs)in zip(req["trials"],rows):out.append({"trial":t["trial"],"message_a_hex":a.hex()if a else None,"message_b_hex":b.hex()if b else None,"observations":obs})
	return{"schema_version":1,"trials":out}
def selftest():
	import random;assert CUT_HALT_ORDER==CMAX+1==8;r=random.Random(3);p=Az();info,h=bounded_check(p);bt=boundary_test(p,plan(256));g,o=_W5();ref=[];m=_alloc(g,256,{j+1:_Q2(j)for j in range(256)},o,[256+i for i in range(256)],range(_X1),ref.append);enc=lambda z:_S1([({"^":1,"&":2,"|":3}[a],b,c,d)for a,b,c,d in z]);assert m==0 and _S1(_patch([({"^":1,"&":2,"|":3}[a],b,c,d)for a,b,c,d in ref]))==_S1([({"^":1,"&":2,"|":3}[a],b,c,d)for a,b,c,d in p.recs]);assert max(max(x[1:])for x in p.recs)<_X1 and all(x[0]in "^&|"for x in p.recs)
	for xs in[[r.getrandbits(256)for _ in range(256)]for _ in range(8)]+[[0]*256,[ALL]*256]:assert _T1(list(p.step(*_V0(xs,256,p.pin))),256,p.pin)==[_W0(x)^p.qint for x in xs]
	for _ in range(10000):w=[r.getrandbits(32)for _ in range(8)];assert enc_invert(enc_words(w))==_R0(w)
	regs=[0]*_X1
	for j in range(256):regs[_Q2(j)]=r.getrandbits(256)
	a=list(regs);assert p.run(0,len(p.recs),regs)==p.kernel;p.fast(a);assert[a[_Q2(j)]for j in range(256)]==[regs[_Q2(j)]for j in range(256)];cur=[r.getrandbits(256)for _ in range(256)];pl=_V0(cur,256,p.pin)
	for _ in range(4):pl=list(p.step(*pl));cur=[_W0(x)^p.qint for x in cur]
	assert _T1(pl,256,p.pin)==cur;e=Aw(At);xs=[r.getrandbits(At)for _ in range(256)];pl=_V0(xs,At,e.pin)
	for _ in range(5):pl=list(e.step(*pl));xs=[e._Z2(x)for x in xs]
	assert _T1(pl,At,e.pin)==xs;xs=[r.getrandbits(256)for _ in range(2)];f=[_W0(x)for x in xs];assert _V2(xs,256)==f==rec().f(xs,False)and _V2(xs[:1],256)==f[:1];assert rec().f([0,ALL])==[_W0(0),_W0(ALL)]and _V2(xs,256,p.qwords)==[x^p.qint for x in f];rows=[r.getrandbits(256)for _ in range(256)];assert _U1(_U1(rows))==rows;assert(_U1(rows)[5]>>9)&1==(rows[9]>>5)&1;xs=[r.getrandbits(256)for _ in range(256)];assert _T1(dnet().step(list(p.step(*_V0(xs,256,p.pin)))),256,[0]*256)==[_Q0(_R0(words_of(x)))for x in xs];q,found=plan(At),0
	r0,ends,ckok,pairs=r.getrandbits(At),{},True,0
	for t in range(400):
		xx,l=(r0+t)%q["N"],0
		while l<q["cr"]:
			xx,l=e.f2([xx])[0],l+1
			if A0(xx,q):
				if xx in ends and pairs<20:aa,bb=recover(q,r0,ends[xx],t,e.f2),recover(q,r0,ends[xx],t,e.f2,3);ckok&=aa==bb and(aa is None or(aa[0]!=aa[1]and e._Z2(aa[0])==e._Z2(aa[1])));pairs+=aa is not None
				ends.setdefault(xx,t);break
	assert ckok and pairs>0
	for s in range(6):
		z,_=attempt(e,q,"selftest/%d"%s,"t")
		if z is not None:found+=1;assert z[0]!=z[1]and e._Z2(z[0])==e._Z2(z[1])
	assert found;print(info,h,bt,p.instr,"ok",True);return True
def _R3(lg):
	print({k:(str(v)if isinstance(v,Fraction)else v)for k,v in lg["plan"].items()});print("body",lg["body"])
	for k,v in lg["parts"].items():print(k,v)
	print("N =",lg["total"]);print("time %.5f %.8f"%(log2(lg["total"]/UNIT)+5e-6,log2(lg["total"]/UNIT)))
if __name__=="__main__":
	arg=sys.argv[1]if len(sys.argv)>1 else ""
	if arg=="--selftest":sys.exit(0 if selftest()else 1)
	elif arg=="--ledger":_R3(ledger())
	elif arg=="--gen-c":sys.stdout.write(GEN_C)
	elif arg=="--loss":
		for k,v in loss(plan(256)).items():print(k,v)
	else:json.dump(serve(json.load(sys.stdin)),sys.stdout)
