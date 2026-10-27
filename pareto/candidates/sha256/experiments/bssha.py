import sys;import json;import hashlib;from fractions import Fraction;from math import isqrt,log,log2,log1p,exp,comb;M32=0xFFFFFFFF;ROUNDS=64;UNIT=4912;LANES,ALL=256,(1<<256)- 1;GEN_C=__import__('lzma').decompress(__import__('base64').b85decode(b'{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;AH_Lsa*g%9!f+7EcWv7Lz|0s4)@dlRYKFC%Ru5;*dPDz@ko%eHoL=sDmUb#(BDY$sOdRsL4LgFV@TvGnbwas+C<1Mr+3*293@tHWMn0>O*93U<+}DG-!@7#jcm6l2tLd6DOE`Nf(a#m{ijBZ_t1mjhQv00=HR95^KP~!J)8e0)d1z6cQ5ew6N1H8vMs7C>%qDWnWQZI#8D`R%(&5N1<>o@hH)UmN8ZqCzl+|rHTuN~FZdF63LUuYg~$vx_{wD&j?dQORs?i|lS>~vN*1u(rNeFlDmK$&MorjI@rj!NK+k2FQO65jxaAb;QfISPD0l!?`84-5x9N56&R2CQC@{jJ{$T<i{)FT&O@-gGT=;A#cHmEingMIi-5IF0VgL&plfV|qQGWF~OSNTo65SrI?O?QW{%ySpO-Y8sVxxQYI423yT(3wuB@c1HMcHRHNEv&Jq~wtIAHU0A6O&+S*3HnP0y8qY=%zH~7}zJ^SsJ5$@(8c1u8B@|F9z^AecX|Yrq@tr4M(naLuuNiMgN@U-=FYes(Q6Hfh_T^YuDl}@#6#H`t90|^TR$^E$`j_f9#4F#=Z?<5+zvlAdV<7!9`KuPyk)yAK%Ep(t8=9;Y5{&x6=7Bz98?1xc&{grDxmIxhBS$`S5t!UT6uJ_?R6JVwrk@VxEK#-b)1@m>TS(S97=?I5EoCZpzc>rK84nLY))6G4OH~4IG^?;2K$XrJLG#<$rw28`kVx+mfHbADf-aH1+jGK15K+MYi!VQJ2VGMoyO>3)B!2UvHQ)<xByiAxTP>Z{}<4E&!NhreX7&?U>wTXYomCck;S7(>eFXibWqAQrS_x0S_6wOlxssZ709OT`F2}to?FKBi|wV$QA34_+>^XEBGG26^>@(>K;09X9`#gJ&IYhiOEON3?fw&j|fs&4qpPcpY}234koypFfxk30DN$ci>D<Tb>XRODFV8t_bo`~sYLwD_UUm<JJtZij2=g?rr`4=_0l2h5rpDvHcpyt(zjRbe#ai5jA<B5>UGPke~ncYs#9M`Zz0aYc5)M)&n4^1-t1mpA4Dx~@@Xg)?R7GfpECwAKs#=WF=}LLZ?zjisEFN3|7|)X$U}|CRV^=)r6%h=nK=HCc3gdO<h?hvtwus}oNpI@&pZyYXA#y$kWfpo6?*N?CxwQxCGaZYGaiUQNLP>fM3%J^n&Y`c)IvMl7eaYIMNIROy5abk%mT}^Qx&2mq+$k_Xu`QL1+FEGgtVBZN4Gi+|5!SI*$4Ky?ExJn_(pmstSWg3pVY!8;h`YBaJO^Jb72w|v7jU`-&u5uYA;{p6A9ryZrFHH{l<WOA%*85X#kkl(;f0<y=VYy*TOIz9YA=w&T;{@B7Nk386Z5uG^;`V_xTOPFH+`=ix!qfmP#M&U*WGhma_SPCwSh-#p#&(b$p6+!4RACM7^1k-VhOSEH1sZMB@6w;kO7VTObYIB00Nij6EvHBGgvV6vV6oFJ(Su_YD>mWy0zi%?!^;b!9h3)wpC+7E#$iZK)(~-6W9ydDyKvUwc->;dggUkF#B(U2Fb&rN|VED1ne8y3l7D;&>(c>u|aMYHm`=5QiAnlP(a!_bllr9Irp$tb?+)SWhf{)Xy12X&!?N)=ZZ`0iB3>p?AIO!Q`Dnug+%S{cDX7-Z=}hDMx0kvTqljTl@G9pY6KQ0b$4&XbGlJw&oFE6{pdtZlpL{jiBfIt%r9V*|<w4yXiMigG0;3MmlAc@%Nh1C)+)A9{h(bnMF{}`&)P+jO%F*L49-KJ)lje*jzr!`R=t>4-PR?i%mDu3W1K3tU-Y_Gl=_(@aRaj%0fP?5htA!{;9bF_}bi7Fu|XX<#t|Pu<Q`kkKEc3Jd(*8Jj6jHGHs52JyPw-I_-MV)P;UWoHv}nARc*$sZ)d12pQSrHBnu9UVoT-SM-|BZU;$t(ZP^?LDVYz`l~XV@c2HpXMn<=5#caXIHxF$^W#>5-&ZbGD*RGT@}R21M~15!QWZV_RCwIsITWw_xMt<NCzJD<e3H&i5j&!s+RYdNxi&gz_{DB&5Z;s&+wJb~j@@l^ZPYu&DTvK{imOtdKjFqzZb?AP-WdP3ahtLy3H8PdA*hUbsU%sxAla)~0@{s@5%J-HO|SFC|8ghZt>sn%KTF$YGxZKATyoMW@u&v=O*Vo;E;|AOU`L+_?GnAF`aZian3_c~9{XxG=F|lgQNOgmo1EskVY+*k2qKPD40XyV@V0f4@y_^@ZZRI(3#7Z(!7`60d$-*l{BG)S-F8Ek@uEITW`Vp$jM|+b>6<OVwodmYUOscQSdPSZ0M&d{6HG-IQby$GSlZ;N99FU_DOS`@uL=ogrKSHD2gQSt6%5?{S+JsWjIr!Vci*1qd7{ueAmJxPuD#RyA(J;>mw+R&93J5d95(C^-)!eZ(MC8*su`XqRSe~(%*e!tb5|oCp<wJWBZ}@cW;+Rs{A+%0gT6=HpgI3sBSbwI^5Br=*)+4)WNXw`$P#mnx_C%P*W0nE`Z~E!I}NNOe+yiIf6NtVM=WlHLKz&n78JI9%WBYmer;>O^MGN`hd24nD93BXyT5=}I%q-<Xxe3jM{xceuwPJ0w#i-q*eo5orQvwQ00a!Jl5yXdz$nul52-#b(*E!&;b%)X9d&{Wv9!o#t3@eG)euRVVDMvltzNbOwVsO1vfrI>>*<bBcP?!G%A5~s1OJ-Y9x&s$?vm*t10e~LuuSxNr-fDGENr){9q`6C!JYhKgt7r3KAzAK6mnbB{as1xtPi=<xn#miTu2_h;JhK#Wy>Y^o@it|p-KHoh2qSPp%HU$Fhzj*0VknI1Uv7<MF;{nsOc8!F!qA^F$>Ktix9VGon`iED0|rJMYfesI?noG13S0h?nnpN%^GP*S$C9IW8FDm?~}qAM>Nq!vbRhO1Cx2R_lf|aAh1)1)kWJN{XxA(<qkfp6<#1aE3Z@-8Q!Z<=?$-Isb7x2&U!zn&lvy!jGe`^1ENk0#y0F`kWd-IFgc<vbDj*}kN5ygx(;lz$-r(>Jn=q{LRvsFZRw<#0s$S1wV(_rccp~*Cs;)W2j;m5E$un0t=IV`>LUF^y*3&HyzmaxN+bva9J_tzGoaN7s`LKqXN<@&Dp_BSd)po5{S`}*|IisvxcW&hB~m4Oj69u~aXNk}rn7v_9+s>?ga%u92!{3#55AXVa5yeX3!gaitr`G6+Qpk=tRa6K+a|gYy<DAKaGCo?uWbk6H`Kvi%^oNxMcSqL3GNQ92F|PDfVOGP8-*B-)&ZQ<VeN!F%px$0@iJevy(PEM6ox8e=+=;=(7T}u%CKPdyeFpKrMX}l{O|gz3Ud88jGxzt!;oMLs$YQC24UT2+*P+7MCz<&Yc%rWmV*&Mig><|k$vR7@WoP2!0eQ${HV=C#y>;W9wsmKm~xJd5Qx-~38G$?jr+2Kh^HL|ssRFzp0`W;bv5X;7n__wj(Tpft2=36<+&-~O2+O0Dq6PFGE`)F3Qi^ue0)7bb-?RX3ee=?M_P+LN9dXAN3oMU@h!20rx*}xu`)Xz1UdZJHYpIt%ak3!o|&x4!YT^e+})n+U)e<Et1dj(Sm_&R2b0DkB4{&zUlu3M_!;(|Jl#O*?m+CXg^6y;$~SOSA=<>5h5Pm2>wqnBcx^T&!oh6fl2I8LEP#Wakk`HzEZdBR%JA2lKr%o-<v?-_F|I;Be$E(DNf?UDA~ez#GVqF%YbcHBGQ!MW9_yEu>fG$|VhfCGPxyJ845>7=oq_@-=N#f8jOgUJ^HrwT5Y#5o#st=`60$FUf(uN0L!SB6Yvuz)%6_7$-*e}m?8^EQ18Cy05#SY30vn7J#j+OxH>^r&0<xjEE3+j&;^+pa9Le4V<l3&me!sqqQR&7Q0k_tFl1XUn0n$(+>$}zXYo1(MF{HHFE3f|`Mnw(Yb8C2@mxE*m@R>`}kMY`@j{g+u*7(WVXCVnMgfa0-swa2PiR@%_oi}OTfQ$)AuvM||UP<^>S<{r(Au2QS5ocn%vAC}Kt^Mq$!ax@L(pqz+SWXwMXQpXF7Etlekc0@!-h|}*3_U=QTx10}TkP);VJJU2^RpBG=1Tuw<(at_%#%mE!*SI)+8f%edJj5yqWkch3Mtq+>9YD54VPR8aGt%r4pH3w0j@*@|JtPZ0Yr$=kW-^@5ZvA{9Wn#<P3x?@&QNAE>hXZ@bCa~mmrX7yehh;rGm^s9HisPoKa)u2CH%t1yCi;5&AW|ZN=_M-2Ovg9cBw#wCg1#+4{m?;QCXJ%{=Xm@0v0<5zbkY+kdFnw)Q;NasB__9N*WP|XJ;dU5XPs?X08epNlzC9ooX?$C5{+u>+gr@2%nHenJK7Wb{J+IPAh@jl=N2ZAm9&`V>bbhS~U|#C!h6+CPA*My2$q`Y7=IeI8yC87grSKXn`Lk=n7VW#%n*FvT@2_CUL4eTmKf`R3(@Gqu=Y-UlZWS*PM>*ED&gerqGhObV$#%?b>}+GKpr;ln2=|x`|eQcErW6xUkv%-SDn}z>jsdx3T*nmTAi~XM30AEN_uG$##WOaaWJ_ebu<4+)dnKBijwkJxIA#ZIP}lV}Ri;gQ|Si71(3MaL%^1y{K9Gtj`HW(sS-8tAH{itKJ@g>}sn_sVPl<vhKZ|vWwv=Vw!_&RM=hL&eW0(<@j`(Lgc20Yzr(;6Zh|9+LMS<&2W;v2D98ud=83l*}OzO2xXm(aK8V%iLs6jg2~2MHAwI%`fXCoXQYY%N1ZXGhZ%pYUME1riv%aB>9z+qg)`rgQ;c@R1Ao+F*tszA-K>sn>G6><044t$j-En47LO2($mLGq_M7z5+D)AJRJrB1Qkl%0ds;;Upc`WLOs@9RxMx-9dpV?GO2|KO|5dvNOwg~FnX>>v2c?Y02yXt9C<5<V+CUjhbffOATb6Ku@{Y3%c_5Qr6q+hyqxpJIfHrh%uKj1XHt8IqUean{wo|2xkF<qZ?m&T>Y_*Ed^O7Hu4yQDjVY|2L=3L-CU~K9ZCu`mdouuCHh>W<7iA*|o&z{W6x>n4Q(=e#6`}nl@5}^iX=&}p&6j)7C9g4y(9BedSKaNnyU_JJ)YpIr0{;B<Wlbh~(3p$qKrysH>wtKY?@df<ur*)Xoe9D8zXH|7-e=4B>ytY?AfGDG!%Y<6v*{!l1i11|?)0dWgaV0zBg(*Go!O3<AWKJRp2Z~S;gKb9^s?`$+w0ERNY0V$ZtwsJ?BG>r-`FE>FOf;?KjSk)SU!iZHXp=_(pIkgD1hqr+*b5}dPX}T53nQDuyz~tRl7O&6vicFB4O@5gkur2tl$&MlgGosolmkCLC%az8N?kh8Ax^dA86Ya4)^5DkLAX3js#L^nW~#d8?(Wp8T943^**Y$ElMT@l;N9p|83k!P1%}ZKFb@Xh$^uDXYU2h8eysJ$J36L6Ti^;J0(Vx8@!2N4b#t;WymaV9dYqu*c!fa!ZF>$-`3yziPx~iddpOnbjpvfu(4u=)wEu{GF4~u<j2U-QEjZoI<_}j4-?yt{I}jgGx-@Luw4FCm5iHfJz3%8Y`KF->q^r3z;u(>DSNHasXO3#tI~TOL{vFK5Djw7#$;oMt>0ZsMN4e!g%Bzm`Iae(EM~uTZI&_yy{Bl~|`>l}s{hyye?h<|#83uAjV|PcrU1CSh^sEqt3IAJPs6k{fm~FA|qi4Bo*hB$W2OSidGJpd_JprY{;dK%nAG7er*Sj4Oh^bkf5@gKPE;In%Mc9ELPe#{mGZRCsdJjvw5}X<;yy{HulP7@mc|&Y5j(;vR+T{f=<dg(}Ym!=(G`i6al(~Yb=^Jn_Ze0Emn23(QBLs=d2`~4L8Xs}Q9i@<Stfxx6X~wmLkl-ero*#FVD_VZ-hrwZt9wl0x^0zvg!(`-#DWt?fW|L;mItiY3C3lFUIK>cn_DW9Mm3~KMd1rY#|BiQ;zs$<?*9o&Z(#rBH0?N?{r;<{)XbeKWAZUt9NGpK)cb1Wp6!VuD#N`1j3R>OW5o-%VzR~t=v(l}o<V%tcOau?5zs*Ph$+`8OmnbpHahPJmq0R0qFk48omRq#<K@hU<@V2(*ztG(E@!>}d_39{yY;VDfBNt&*98kn{O_00V#{z!yxjnz~qg_-dj-{uKV;TSfRG!BO)VoH*#_R^NPS3t|#|#{`@_dh?`q8R9jVyRO$?yyaIIiIeRf{(2p1{BIa14j6rU9=VSje#iyEYX-Q89YV7?>&jqx|Q&rZ|6K{nmPCL#bN%_f$39Yh#LlsD4E*0Laxkx!hB?l6}5ONaA?k2WTKVu+C1g1Sc!zhkMe(NByS4YFKP@w+cE%0>RONN{KnWqf7|nIaPSVu->B_lZ1u7)9|-c__V8>_Y4eEOYs@j4VYj5E?l!lHkL#<>}osvMb(T<HcgYShRZ?aOJ*sv$xbY9p&AM+o!x>!zI+?n3p9cq2x@zceB`WIhlkdT`(~Ef5mEjCi#KB?WLYPCgEA{shZW!37MG-agX?aDB*n2C?U|?7k0S3*p~-Gk=Dgf+)6L%L3*wC!2gTpr)nQFdWG5Dr&?x$vtwH|*gvDerI+kRtJ0LC&eUmd#G1q@b9cR4ftz9HbwS6ytz`p}+Tm;KV*$?Jja`RtjwI}jC?{oOzi?8+a<586<94~x^K*A&kYeKa`T=l!Hy0%v$^2F~2Q4`GwP3?M-MAx;y5-a4J59HyUSscu#=h#Ps+A;qHv#!bzXuU&#PY27TY_U@2Cr#-HHRs>Ag#uWDv;*0P8>#IAvLLYy!NLi8B3y64M?VPB3r6(2nq};&V-C?j1U*F>jbUcKc#64((e0a`2Frf{4f`vEnSJ!pZ|y!M_FS`~NWQa`yD<5b<Ed7w3D6>{&V;FW7X#vin}=Bk*$j|Hkw$&j|L1tAieMd(L3ZG#Avtae<g#Mqy$~h~X^#r~hquJTFyO&D+!8@y+vEEkz7&mMhufdvD9Z>S=a=}asH_U(w|%%N?5`_8``psNI3nJV-}_tzt|Q)40>GSH#zr>JZNX)2g_P)k6d@7|+w&EQs?!vwsJsdEhFC*fypQr?HI89{>#628K2`d$!8*nRXxC#?RCE+CrxPD{4<(gEpcz9MZUa9G4=Z5zN>!FaRp6(^ci58_;QFl&W|ClJKrNJ`v9TqNPk5P>1v(WpUe++iyt;>vQ_V^roar2xL(2%;9%fJxXaQ<9u7!{Y)NfJXDmvkowGLj$ENxBsbYhWS;GSERwS-dF;=oLYXOLJPS#&0@O=3U(2{Cz`70YExhe^}e&Uw(SmN{2iyTXD+l|Jxr7!zyu1}Bm5&ku|-w7?GZ1h`gs%@Ic1h!v|V2}c)fQyqsIE9$drTU%3<gIkIGA5ps&B!4MgsI&IxV1__aUa<dQnqtpj2w&svj4;FzGXLCG#{=lLlqoQZLAyVt_8B2+E1qc>Ct#208VWoR$KH}z&JmMen!2dedl2Y74AZ&YG%(+3l4<oiH(Eb>)ykAlw`@U|w8Cf*_ukC*JI7*YaVVY)ef^rNh+&!rir8Z46}6*j4OpKPq8HK8W3U*Ajor|WRi~5v;}#B{n}Jb3gPM-S^ywab4C6@YRU$O(rG{{XLavC~M-Cxp*lz42cvJ-YlBl6Ugvd)sn^9>gzMYI8CsfBE>*$hg$sZMI?Z0Nun}tqZe#s!DdCBjf0!4(J6fdJ{fGxUDY<II{W5&l-kT6-kTT(97A&KY{s*vP8-_rLswasAxJB<v;y%r#*2_B**VgJ!XsPx)_d6&e|43r~YpF-u@D2gl;U0#@5p0bLPSOXS#=$mE-i_W+SL6gRqmVtVuFQn!^%4g1XiVQr#(|YwJw`W(`JW6T7xgMIPC?7>c(bJxb@7*5g1L-R{e|m!C@0i2<AMq#@_>?^obAj81{v?Apx8Y3jkterM?$+U$kZ4R;$xK(-$Ksd9=F$|IiCY(nMfaj(?p+BEbIO<V4;wrAb#(3skbs!;;d~oy8P*vT;9{yNVXf!O!7+*;01oXbwuMDc{d?+WRDll~hw2(xP1;lBz_$jV<tSu~B-P}aqE{UwC<neyrdDp5nBDUd3Orp|*+3Lih^-oAnwKd{H!@Lba-m!IS0`d24Kn2ksMd|8q?nsWm>lL%%a))HdqOvbeQ=1lkHC5D={{{XyYtri99K??P0^|#Yht9x>NuICTmlmf?IS#F6)YyBQR{-#;=z(whxPQq>y9A|B)}S7cN$Z5L(Pi&^C%7dYXt+f<u%GPY|+x?3HP0KWXeLOp1v{-F0lWgNH?<Iv(pj%c3*OjLRO0i(?7d;?J-?w1aKXZ69TOCAttyQR`-pvcX5Ln-juuqCv0^VctBPNhtygyt*45Npio)XI`WFTQ~OeXcY#9(>ZM+2s}ur93Xa#PjLCOZg)F-R2mY$Qp1QL3Q@Ry*<wxLVDc}MS{A<qyEYBGlCJ6d%iu{@It=PfG@V=O<kx5R@wW)Ad*3;M(#uimg?a8rrh_VcKYu2k>bx9M_Rdb)uGYR0dP~gWX&B6-(Qb*Dp8%cZF$7I2~xC0NVym~-ERItq_9|+*ALbkhD)x1%tIGGhXa!rULomt?E<D#nFGC_vlU*fu-L)chr(J&!R1s9JHIqB&{g>|RRt+^%w_|kArbw+n*dGHpxh5CbTZ3#D3cZbZ1sS+8(65IEMo>S8S_l}b~#?TLN#KS>&NZR<rnn@b+JI?3{hxUp)dO4#zTRV!r$$wEbjQEkoYb%Yu&S9DZ%Ow{$%fpz?&a3e{im{cc)pPZ%0LK@3V4-Vz=%Y1je+|)=GH+A@_O=75R}6F-`E?lHja<>Jo9?Ml1p7(hnXcV9MsRIijL$GTB`|odpn5<@Fwv4t-F|t>Tf(j9cB@M||E9Fr9_XUR1_&f|EoU(EfDZgAiFUJNx<pwlLD|0h$zhv5?vZx{eJn^?#P!o+hgivjNh6gAn$IOu!EguEgvh&%gl-$cC`q!s!d#tsT9v`e{d1k*VIj)1Zk2QZFYSID342Uc&L0d?k*i(GV=f}GJwLi8MH#L5;Jco9JK^-S+2VM^S3OI>fGSYQVK*Mus*5eM(2-IfQbcGxd|0N6v!4Lyb0c}9h7->a`%g&O<)ecc)#9jI`NyiE1pi}i4&i#VOh<<pnHrU+v%GeZim<gA$b65EA$?zru!B(g>1KoC{=Y>-hZU?*NE;LDBI)W~^6pW!iV~k0?47_3D^5-u=Cvl!e=y6Plh3t|Shs&bEh-2`Yyp~a9yj4SIgpSO3yUd894azQ4|RrAH}HHT?}<RK;7Q3Yf0!}h5X#TT(8DLNRQ5S$%NYE6X<z<=a8VFoySu@c%Qx>Tw2*6o={0R#U4(z`WZ1$JMwIYIzrIe+*_tS52W~lOgw1^&vzIczel<^I0q#iF+I;NTTjN|gf?Lp{`gO4$6X|S9caL~&p30Nl62`}(CR3(?8Z)b&a*;A-169ZDRCr;GLTerr5JbN)4u&I_1nT&%YwSEXTUY!1J?;bnjG#_a<C<B4dxGISZ~d$qI4x>jW;&3z9S>;>i_?YtUsoM!#5m<KCp?Z4S5PV#y=oIYdko2DNpHMKGTjhcIdT?+J~Mm;Kg--SEOA2px1SmJEfP$pia+jhn_^X5BcpXV+(TlHxX)^p2DdMD)HCR(`j|TZirQ%Q6n7WVf&<MsW=i<Nh&==3H>R21sK8{zt$PKLw;Wehck;0L*|KMN-cVaf8$hSAbklY}f74DNFS}UPl7NnH$;YT%olNbejop5*INE|f?;9LW6h`a%Xt?6h?u(fuH5j+WK+!C1=J2i|Q|u7}Gcc&<P^5DZQZF<{6kJ%;C!lMXr2@2?OE(J$ky$nnhD8?l{+Dpf@ADJ($7I&mEHbus1Q=|}2!;4Q<vO@5t*ccPX{LZOza=7~BnR5v?BIl0`qIfe#7FBeR7V9+o>3i60?eDJm{M8lh-u$*KP;d$samKtu9nBqByh{)8rUx8rc6uO5PfpP0dOsbJ7X@)rtEJ|FmH<ZBV?79399oWtJX1-*SWA3HK$v<;#54!X}f>0To)gaxtG`yS<ES5H%7}~zX63WaZ9QQvxpD+XstY8h2i-m2jwY(9+91C?NMR$Ajak1#MtAaEMpHEDNWg_9tl5++%X#M5Z-b`+URnL_^RX3YLjo+1eUF#`0dGm-tub~o@f_4w{dwyhP){9`kFM}+KLA_^=c+&N*x@=FTz4a6S?yTaRbC|GdM-<OWcu{?4cc~f8x~5f<Xa@gegI~mTeSl<LXg%GXjHvX<3${l^q69#n08`wx)3!kdTKQK|lhr${qt9+O7+m#%ZHb=HO>{n3ZB0_L2zvo#`aRM~4RzPuyH!f8Mn|&kbGXh7(ErQUMs~EBW|-6^<rg`f)0mc)dJr>s;{KnE{r<#VJ>F1K2Q6Xp(-+d=BDY%67uW7!Ra47>pZP3{y0cFA7LA?2n%iMdk_W5ARHq@t*F_&Qu*D;P&;x73x;9k@&tmu?)$KL9yGWdrumTJVH@~kJ><1MPbFxNNr3GRc|PRnZF(_tws;2pfw<ahKLkinnhfQX?4=4Ox{lRUUa&uP*IIaO;vZ(PghQ0Pd^um$7l!_zh6cLBp$`6P4MFVX~hbewp)X@GY|0cz2k|WQl&`)hRbTVc90O{k_03h>~Fsb`gB6HZD4K+YC?$tc<5xqDD&{y3E6{f$VmU9Sh5qu^qrh^)VHO4zIwRK_D9kD{hrPBD75m`$?WV-y>C=G$1{4-HvF8N_oF%_$5=}s&dB)^fUFQtB5%BAZ~+Itj>ugU+L?Q4icvV;dpFMvqu_&hXWBlU3R5Mc(h6}dol{4Elu5$+=wsUCytn|*%j0NZ@d9u_#pcx69uk5kxw83i76OEnt5L9z^+|cauVqu*ZtRJpN`OzCpgzlGYJ{G;mS)f?#EZT*Xq!fgIocQH>Ldi^%<Q8Syc@tZ^n3Sn5!aFSCRq%<)t=WM20D@n4A<QBp<bX*_t3nP8|Jk`1>snlR&v?;c%&&%E6lf%LZVcy8YgoSrk^)W&W2W!c^1}DvCJ>Ed<``<>toXk1KdCY-c;5xAErcY4d1YLqg35jVo_D-ZLd=*!k1*56O%-JtTqxO)=*aabQ{*oITjvCQwvEeU11@*>2sR<ge?2a`t>?J*yKxsm)QH&`$$@bmX@`XJ-3)XF(F2jiekENU@-%D1+_6=JQ*2N_pVO%tmziSVq;)L+&Q@*p&tH&WxAh+>41MVBc`rle~IDk>e3C7PjJ5JCxV}_Q|vVno%RNwk~%d&p=TkWGKWI)B@HD!XRufynI167S2V}^O4P6}CtHC3&w6`8qcO!mIceOC_kf)ehcxH0>-D{4jI~2G{l~CJUchaw+4Y9?^Db$_{C_28?*xk9HK{jfM!8FbCx)>BjQas$nFPG2vQHm+svVbFRcEL~eS|!N`g6AFWPCkVn5K_$-=9^&k8tvb8OQG|P;H!KN%AKjpEqmrd3H>7ldM%Nn*By6V+PqkCgw9bdd{B{H!uP{;aa(E?tO&}RF4>!Jb2p*6{j39N0sZ9s|kK`E3tJAVd<|`IeUDxDSZ%WqWjr(Uf6_Hf@q^FXpZ>7HWN?w5_xI1=$RmH?V|3<MI^d@(bHn}JTw?68V4N!c(u_xWp-rAdXF;{TvDX<c|N@363G_xlJO(jJp^-IY-s)@a=!41;|jKOh@{svbh{wjrw#=wH1^xXQd%@O&BnL}1au|j;JB;~U}G)AzUaE3Jl}XWo4g`MU#=aqiAUN!w&~)2+8t{E00000Ic>y94aVE|00G5Eg318^<b%+vvBYQl0ssI200dcD')).decode();_gc=lambda s:tuple(int(x.strip().rstrip("u"),0)for x in GEN_C.split(s+"={")[1].split("}")[0].split(","));IV,K,PERM,PREFIX_WORDS,UCD=_gc("IV[8]"),_gc("K[RND]"),_gc("PERM[8]"),_gc("PW[8]"),_gc("UCD[96]");PAD2=bytes([128])+bytes(55)+(512).to_bytes(8,"big")
def _ror(v,k):return((v>>k)|(v<<(32-k)))&M32
def words_of(x):return[(x>>(32*(7-i)))&M32 for i in range(8)]
def int_of(w):return sum(w[i]<<(32*(7-i))for i in range(8))
def _SIG0(a):return _ror(a,2)^_ror(a,13)^_ror(a,22)
def _SIG1(e):return _ror(e,6)^_ror(e,11)^_ror(e,25)
def _CH(e,f,g):return(e&f)^(~e&g)
def _MAJ(a,b,c):return(a&b)^(a&c)^(b&c)
def _exp40(ws):
	ws=list(ws)
	for i in range(16,ROUNDS):x,y=ws[i- 15],ws[i- 2];ws.append((ws[i- 16]+(_ror(x,7)^_ror(x,18)^(x>>3))+ws[i- 7]+(_ror(y,17)^_ror(y,19)^(y>>10)))&M32)
	return ws
TAILB=1;CIN=1;NTAIL=6 if TAILB else 4;QM,XM=0x0772d77a,0xa2c126f1;PRE,VARBASE,TAILMAP,OFFSET=8,8,{},set(range(10,16))
def _build_ws(w,prefix=None):
	prefix=PREFIX_WORDS if prefix is None else prefix;ws=list(prefix[:PRE])+[0]*(16-PRE)
	for k in range(8):ws[VARBASE+k]=(w[k]-(K[VARBASE+k]if VARBASE+k in OFFSET else 0))&M32
	for pos,v in TAILMAP.items():ws[pos]=v
	return ws
def _trace(w,prefix=None):
	ws=_exp40(_build_ws(w,prefix));a,b,c,d,e,f,g,h=IV;A,E,T={0:a,- 1:b,- 2:c,- 3:d},{0:e,- 1:f,- 2:g,- 3:h},{}
	for i in range(ROUNDS):t1=(h+_SIG1(e)+_CH(e,f,g)+K[i]+ws[i])&M32;t2=(_SIG0(a)+_MAJ(a,b,c))&M32;a,b,c,d,e,f,g,h=(t1+t2)&M32,a,b,c,(d+t1)&M32,e,f,g;A[i+1],E[i+1],T[i+1]=a,e,t1
	return ws,A,E,T
def state_words(w,prefix=None):_,A,E,_=_trace(w,prefix);r=ROUNDS;return[A[r],A[r- 1],A[r- 2],A[r- 3],E[r],E[r- 1],E[r- 2],E[r- 3]]
def enc_words(w,prefix=None):ws,A,E,T=_trace(w,prefix);r=ROUNDS;bw=[E[r- 3],E[r- 2],A[r- 7],A[r- 6],(T[r- 5]+_CH(A[r- 6]^A[r- 7],A[r- 8],QM))&M32,T[r- 4],(E[r- 5]+_CH(E[r- 2],XM,E[r- 4])+ws[r- 2])&M32,(E[r- 4]+ws[r- 1])&M32];return[bw[PERM[k]]for k in range(8)]
def enc_invert(enc):
	r,bw=ROUNDS,[0]*8
	for k in range(8):bw[PERM[k]]=enc[k]
	e3,e2,a7,a6,Q,T4,X,Y=bw;a5=(Q+(a6&a7&~QM)-(~a6&~a7&QM)+_SIG0(a6))&M32;a4=(T4+_SIG0(a5)+_MAJ(a5,a6,a7))&M32;a3=(e3-a7+_SIG0(a4)+_MAJ(a4,a5,a6))&M32;a2=(e2-a6+_SIG0(a3)+_MAJ(a3,a4,a5))&M32;t1=(X+(e2&e3&~XM)-(e2&~e3&XM)+_SIG1(e2)+K[r- 2])&M32;e1=(a5+t1)&M32;a1=(t1+_SIG0(a2)+_MAJ(a2,a3,a4))&M32;t0=(Y+_SIG1(e1)+_CH(e1,e2,e3)+K[r- 1])&M32;return[(t0+_SIG0(a1)+_MAJ(a1,a2,a3))&M32,a1,a2,a3,(a4+t0)&M32,e1,e2,e3]
def f_scalar(x,n=256):return int_of(enc_words(words_of(x)))&((1<<n)- 1)
PAD2W=tuple(int.from_bytes(PAD2[4*i:4*i+4],"big")for i in range(16));_KW2=tuple((K[i]+w)&M32 for i,w in enumerate(_exp40(PAD2W)))
def digest_of_state(s):
	cv=[(u+v)&M32 for u,v in zip(IV,s)];a,b,c,d,e,f,g,h=cv
	for kw in _KW2:t1=(h+_SIG1(e)+_CH(e,f,g)+kw)&M32;t2=(_SIG0(a)+_MAJ(a,b,c))&M32;a,b,c,d,e,f,g,h=(t1+t2)&M32,a,b,c,(d+t1)&M32,e,f,g
	return int_of([(u+v)&M32 for u,v in zip(cv,[a,b,c,d,e,f,g,h])])
def digest_of_g(o,qint):return digest_of_state(enc_invert(words_of(o^qint)))
def message(x):return b"".join(v.to_bytes(4,"big")for v in _build_ws(words_of(x)))
RP,RMASK=128,M32|(M32<<128);WM,KM=0,ROUNDS-10
def _rep(v):return v|(v<<RP)
class RecProg:
	def __init__(self):
		n=ROUNDS;self.imm,self.init=[],[];MASK,T0,T1,T2,T3,T4=0,11,12,13,14,15;ST,PB=list(range(1,9)),[9,10];W0,W1,W2,W3,WC0,WC1,WC2,WC3,E0,E1,WN=19,20,21,22,24,25,26,27,28,29,30
		def S(out,x,v):self.imm.append(v);out.append(("S",x,len(self.imm)- 1,0))
		S(self.init,MASK,RMASK);S(self.init,WN,_rep(PREFIX_WORDS[0]))
		for i in range(10,n- 6):S(self.init,T0,_rep(K[i]));self.init.append(("T",KM+i,T0,2))
		constpos={i:PREFIX_WORDS[i]for i in range(1,PRE)};constpos.update(TAILMAP)
		for i in sorted(constpos):S(self.init,T0,_rep(constpos[i]));self.init.append(("T",WM+i,T0,2))
		hregs=[5,6,10,11,12,15]
		for j,k in enumerate(range(2,8)):S(self.init,hregs[j],_rep((-K[VARBASE+k])&M32))
		for rk,vk in zip((13,14,16,18,23,29),(K[n- 6],K[n- 5],K[n- 4],K[n- 3],XM,QM)):S(self.init,rk,_rep(vk))
		def sigma(out,dst,src,rs,shr,mask=True,dup=True):
			if dup:out+=[("<",T0,src,32),("|",T0,src,T0)]
			out+=[(">",dst,T0,rs[0]),(">",T1,T0,rs[1]),("^",dst,dst,T1)];out+=[(">",T1,src,shr)if shr else(">",T1,T0,rs[2]),("^",dst,dst,T1)]
			if mask:out.append(("&",dst,dst,MASK))
		def rnd(out,st,pi,wreg,addrk):a,b,c,d,e,f,g,h=st;P,PN=PB[pi],PB[1-pi];sigma(out,E0,e,(6,11,25),0,False);out+=[("^",T1,f,g),("&",T1,e,T1),("^",T1,g,T1)];out+=[("L",T0,addrk+KM,0),("+",E0,h,E0),("+",E0,E0,T1),("+",E0,E0,wreg),("+",E0,E0,T0)];sigma(out,h,a,(2,13,22),0,True);out+=[("^",PN,a,b),("&",T0,PN,P),("^",T0,T0,b),("+",T1,h,T0)];out+=[("+",h,d,E0),("&",h,h,MASK),("+",d,E0,T1),("&",d,d,MASK)];return[d,a,b,c,h,e,f,g],1-pi
		assert WM==0;body=[];st,pi=list(ST),0;stl,pil=list(st),pi
		for j,wr in enumerate((WC0,WC1,W0,W1)):stl,pil=rnd(body,stl,pil,wr,10+j)
		assert stl==st and pil==pi,"the round loop does not rename back";body+=[("L",WN,4,0)];sigma(body,E0,WN,(7,18,0),3,True);body+=[("+",WC2,W0,E0),("L",W0,1,0)];sigma(body,E0,W0,(7,18,0),3,True);body+=[("+",E0,WC3,E0),("+",WC3,WN,W1),("+",W1,W0,WC0)];sigma(body,W0,W2,(17,19,0),10,False);body+=[("+",W0,W0,E0),("&",W0,W0,MASK),("T",16,W0,0),("|",WC0,W2,W2),("L",W2,2,0)];sigma(body,E0,W2,(7,18,0),3,True);body+=[("+",W1,W1,E0),("+",W2,W2,WC1)];sigma(body,E0,W3,(17,19,0),10,False);body+=[("+",W1,W1,E0),("&",W1,W1,MASK),("T",17,W1,0),("|",WC1,W3,W3),("L",W3,3,0)];sigma(body,E0,W3,(7,18,0),3,True);body+=[("+",W2,W2,E0),("+",W3,W3,WC2)];sigma(body,E0,W0,(17,19,0),10,False);body+=[("+",W2,W2,E0),("&",W2,W2,MASK),("T",18,W2,0)];sigma(body,E0,W1,(17,19,0),10,False);body+=[("+",W3,W3,E0),("&",W3,W3,MASK),("T",19,W3,0)];ra,rb,rc,rd,re,rf,rg,rh=st
		def t1(out,dst,hr,er,fr,gr,wi,wreg,kreg):
			sigma(out,E0,er,(6,11,25),0,False);out+=[("^",T1,fr,gr),("&",T1,er,T1),("^",T1,gr,T1)]
			if wreg is None:out.append(("L",T0,WM+wi,2));wreg=T0
			out+=[("+",E0,hr,E0),("+",E0,E0,T1),("+",E0,E0,wreg),("+",dst,E0,kreg)]
		tail=[]
		if TAILB:R5,QQ,E5,R4,E4,E3,E2,XX,YY=8,17,4,24,25,26,WC3,PB[0],31;t1(tail,R5,rh,re,rf,rg,n- 6,WC0,13);tail+=[("+",E5,rd,R5),("&",E5,E5,MASK)];t1(tail,R4,rg,E5,re,rf,n- 5,WC1,14);tail+=[("+",E4,rc,R4),("&",E4,E4,MASK)];t1(tail,E0,rf,E4,E5,re,n- 4,W0,16);tail+=[("+",E3,rb,E0),("&",E3,E3,MASK)];t1(tail,E0,re,E3,E4,E5,n- 3,W1,18);tail+=[("+",E2,ra,E0)];tail+=[("^",T1,E4,23),("&",T1,E2,T1),("^",T1,E4,T1),("+",XX,E5,T1),("+",XX,XX,W2)];tail+=[("+",YY,E4,W3)];tail+=[("^",T0,ra,rb),("^",E0,rc,29),("&",T0,T0,E0),("^",T0,29,T0),("+",QQ,R5,T0)];fb=[E3,E2,rb,ra,QQ,R4,XX,YY];self.fin=[fb[PERM[k]]for k in range(8)]
		head=[];wregs=(WC0,WC1,W0,W1,W2,W3)
		for k in range(7,- 1,- 1):
			if VARBASE+k in OFFSET:dst_reg=wregs[k- 2];head+=[("+",dst_reg,self.fin[k],hregs[k- 2]),("&",dst_reg,dst_reg,MASK)];head.append(("T",WM+VARBASE+k,dst_reg,2))
			else:head.append(("T",WM+VARBASE+k,self.fin[k],2))
		y0,y1=self.fin[0],self.fin[1];sigma(head,ST[4],y0,(6,11,25),0,False,dup=True);head+=[("+",ST[4],ST[4],y1),("&",ST[4],ST[4],MASK),("+",WC3,y1,WN)];sigma(head,ST[0],y0,(2,13,22),0,False,dup=False);head+=[("+",ST[0],ST[0],ST[4]),("&",ST[0],ST[0],MASK)];head+=[("|",ST[1],y0,ST[2]),("|",ST[5],y0,ST[2])];self.blocks=[("S",head),("L",body,0,n- 16,4),("S",tail)];self.flat=[]
		for blk in self.blocks:
			if blk[0]=="S":self.flat+=blk[1]
			else:_,bd,start,count,stepw=blk;self.flat+=[("R",0,start,0),("R",1,start+count,0)];top=len(self.flat);self.flat+=bd+[("A",0,stepw,0),("C",0,1,0),("J",top,0,0)]
		self.instr=len(self.init)+len(self.flat);self.mem,self.regs=[0]*(2*ROUNDS-16),[0]*32;self.run(self.init);self.mem0,self.regs0=list(self.mem),list(self.regs);self.ops=self.run(self.flat)
	def run(self,recs):
		r,mem,p,flag,pc,cnt=self.regs,self.mem,[0,0,0],False,0,0
		while pc<len(recs):
			op,x,y,z=recs[pc];pc+=1;cnt+=1
			if op=="^":r[x]=r[y]^r[z]
			elif op=="&":r[x]=r[y]&r[z]
			elif op=="|":r[x]=r[y]|r[z]
			elif op=="+":r[x]=(r[y]+r[z])&ALL
			elif op==">":r[x]=r[y]>>z
			elif op=="<":r[x]=(r[y]<<z)&ALL
			elif op=="S":r[x]=self.imm[y]
			elif op=="L":r[x]=mem[p[z]+y]
			elif op=="T":mem[p[z]+x]=r[y]
			elif op=="R":p[x]=y
			elif op=="A":p[x]+=y
			elif op=="C":flag=p[x]<p[y]
			elif op=="J"and flag:pc=x
		return cnt
	def f(self,xs,fast=True):
		if fast:return[f_scalar(x)for x in xs]
		self.regs[:],self.mem[:]=self.regs0,self.mem0
		for k in range(8):self.regs[self.fin[k]]=sum(((x>>(32*(7-k)))&M32)<<(RP*l)for l,x in enumerate(xs))
		self.run(self.flat);return[sum(((self.regs[self.fin[k]]>>(RP*l))&M32)<<(32*(7-k))for k in range(8))for l in range(len(xs))]
_REC=[]
def rec():
	if not _REC:_REC.append(RecProg())
	return _REC[0]
def packed_f(xs,n,qw=None):q=sum(qw[i]<<(32*i)for i in range(8))if qw else 0;return[(v^q)&((1<<n)- 1)for v in rec().f(xs)]
def packed_ops(qw=None):return rec().ops
ZERO,ONE=(0,0),(0,1);_ADD_HINTS=(0,)*100;EXPECTED_EMITTER_INFO=(85831,905,86088,337946,0,0,67508,11008,7315,343324,16384,86123,32000,100,736);STATIC_SLP_SHA256="d0f6bcaf9928b7c638acbd5166375a3c5672c3c618ab19cc063f7effe139cce6";STATIC_C_SHA256="2857150bda4ec40fc8701e91fc587055649456fa8bbc63a19e5e29fbbac1363b";STATIC_WASM_SHA256="aef4d7a384e1c122ae4f200be11766607c6d860a2f92e26bc5597fae5bc6af1c";POLARITY_Q=int("22273a6c5e8abef676dc5de11e7bc9e3468ac54393e15c2405e9e8acbfb29d63",16)
class Gen:
	def __init__(self,n):
		self.n,self.nodes,self.calls=n,[("c",)],0;self.ahi=0;self.inputs,self.cse=[],{}
		for j in range(n):self.nodes.append(("v",j));self.inputs.append((len(self.nodes)- 1,0))
	def mk(self,op,a,b):
		self.calls+=1
		if a>b:a,b=b,a
		k=self.cse.get((op,a,b))
		if k is None:self.nodes.append((op,a,b));k=self.cse[(op,a,b)]=len(self.nodes)- 1
		return k
	def _gate(self,node):
		if node<=self.n or node<len(self.nodes)- 8:return None
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
			common=set(gx[1:])&set(gy[1:])
			if common:c=next(iter(common));left=gx[2]if gx[1]==c else gx[1];right=gy[2]if gy[1]==c else gy[1];r=self.XOR((left,0),(right,0));return(r[0],r[1]^inv)
		return(self.mk("x",x[0],y[0]),x[1]^y[1])
	def AND(self,x,y):
		self.calls+=1
		if x[0]==0:return ZERO if x[1]==0 else y
		if y[0]==0:return ZERO if y[1]==0 else x
		if x[0]==y[0]:return x if x[1]==y[1]else ZERO
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
		if len(vs)==1:x=vs[0];k1,k2=cs[0][1],cs[1][1];return(x[0],x[1]^k),(ONE if k1==k2==1 else ZERO if k1==k2==0 else x)
		kk=cs[0][1]+cs[1][1]+cs[2][1];return(ZERO if kk%2==0 else ONE),(ONE if kk>=2 else ZERO)
	def add(self,A,B,cin=ZERO):
		s,c=[],cin
		for i in range(32):
			if i==31:s.append(self.XOR(self.XOR(A[i],B[i]),c))
			else:si,c=self.fa(A[i],B[i],c);s.append(si)
		return s
	def OR(self,x,y):r=self.AND((x[0],x[1]^1),(y[0],y[1]^1));return(r[0],r[1]^1)
	def _col(self,t,u,U,oU,rev=False):
		X,A,O,pt=self.XOR,self.AND,self.OR,U[1]^u[1]
		if t[0][1]==t[1][1]==t[2][1]:(x,y,z),tm=t,(1 if t[0][1]==pt else 2)
		else:
			for zi in((2,1,0)if rev else(0,1,2)):
				if t[zi][1]==pt:r0,r1=[t[j]for j in range(3)if j!=zi];(x,y,z),tm=((r1,r0,t[zi]),0)if r0[1]!=u[1]else((r0,r1,t[zi]),0)if r1[1]!=u[1]else((r0,t[zi],r1),1);break
		if tm==1:w=X(y,U);n8=X(z,w);s=X(x,n8);n6=O(U,X(y,u));return s,(ZERO if oU else X(n6,w)),X(n6,A(n8,X(x,w)))
		if tm==2:w5=X(x,y);w6=X(z,w5);s=X(U,w6);w9=X(u,w6);w10=O(U,(w9[0],w9[1]^1));w11=O(w5,X(x,z));return s,(ZERO if oU else X(w6,(w10[0],w10[1]^1))),X(w10,(w11[0],w11[1]^1))
		n5=X(z,U);n9=X(x,n5);s=X(y,n9);n6=X(x,y);n8=O(U,X(z,u));n11=A((n6[0],n6[1]^1),n9);return s,(ZERO if oU else X(n5,n11)),X(n8,n11)
	def add3(self,A,B,C,cin=0,d0=None,h0=None,u0=None):
		s=[None]*32
		if h0 is not None:
			sw0,u=self.fa(B[0],C[0],ONE if cin else ZERO);s[0]=self.XOR(u0,sw0);w=self.XOR(h0,sw0)
			if u0[0]and w[0]and u0[0]!=w[0]and u0[1]!=w[1]:cm=self.XOR(self.AND((u0[0],u0[1]^1),w),sw0)
			else:cm=self.XOR(self.AND(u0,w),h0)
			U=self.XOR(u,cm)
		elif cin==0:
			s[0],U=self.fa(A[0],B[0],C[0])
			if d0 is not None:s[0],u=self.fa(s[0],d0,ZERO);U=self.XOR(U,u)
			else:u=ZERO
		elif cin==2:s[0],c0=self.fa(A[0],B[0],C[0]);u,U=ONE,(c0[0],c0[1]^1)
		else:
			ops=(A[0],B[0],C[0])
			for pi in range(3):
				o=[ops[j]for j in range(3)if j!=pi]
				if o[0][1]==o[1][1]:p,x,y=ops[pi],o[0],o[1];break
			u0=self.XOR(x,p);s[0]=self.XOR(u0,(y[0],y[1]^1));u,U=p,self.OR(u0,self.XOR(y,p))
		for i in range(1,31):s[i],u,U=self._col((A[i],B[i],C[i]),u,U,i==30)
		s[31]=self.XOR(self.XOR(self.XOR(A[31],B[31]),C[31]),U);return s
	def add2c(self,A,B,cv):
		cin=1 if _tz((cv- 1)&M32)>_tz(cv)else 0;cv2=(cv-cin)&M32
		if not cv2:return self.add(A,B,ONE if cin else ZERO)
		k,s,c=_tz(cv2),[None]*32,ONE if cin else ZERO
		for i in range(k):s[i],c=self.fa(A[i],B[i],c)
		if k==31:s[31]=self.XOR(self.XOR(A[31],B[31]),(c[0],c[1]^1));return s
		ops=(A[k],B[k],c)
		for pi in range(3):
			o=[ops[j]for j in range(3)if j!=pi]
			if o[0][1]==o[1][1]:p,x,y=ops[pi],o[0],o[1];break
		u0=self.XOR(x,p);s[k]=self.XOR(u0,(y[0],y[1]^1));u,U,C=p,self.OR(u0,self.XOR(y,p)),_constw(cv2)
		for i in range(k+1,31):s[i],u,U=self._col((C[i],A[i],B[i]),u,U,i==30,True)
		s[31]=self.XOR(self.XOR(self.XOR(A[31],B[31]),C[31]),U);return s
	def _baseline(self,cv,vs,force_bb=None,call_id=None):
		if len(vs)==2 and cv and force_bb is None:
			if call_id in(20,23,24,27):return self.add2c(vs[0],vs[1],cv)
			if call_id in(16,18,22):
				rem=((-K[17])&M32)if call_id==18 else((4-K[19])&M32)if call_id==22 else((6-PREFIX_WORDS[7]-K[23])&M32);s=self.add2c(vs[0],vs[1],(cv-rem)&M32);out=self.add(s,_constw(rem));sp=getattr(self,"split",None)
				if sp is not None:sp[tuple(out)]=(s,rem)
				return out
		bb=force_bb if force_bb is not None else(max(range(len(vs)),key=lambda k:(_tz((cv-k)&M32),-k))if CIN and cv else 0)
		if len(vs)==4 and bb==0 and not cv:A,B,D,C=vs;s=self.add3(A,B,C,0,D[0]);return self.add(s,[ZERO]+D[1:])
		used_b=0
		while len(vs)>2:c3=min(bb-used_b,2);used_b+=c3;vs=[self.add3(*vs[:3],c3)]+vs[3:]
		s=vs[0]
		for w in vs[1:]:c1=1 if used_b<bb else 0;used_b+=c1;s=self.add(s,w,ONE if c1 else ZERO)
		cv=(cv-used_b)&M32
		if cv:
			out=self.add(s,_constw(cv));sp=getattr(self,"split",None)
			if sp is not None:sp[tuple(out)]=(s,cv)
			return out
		return s
	def _choice(self,op,mask):
		pick=[op[i]for i in range(len(op))if(mask>>i)&1];rest=[op[i]for i in range(len(op))if not((mask>>i)&1)];first=self.add3(*pick)
		if not rest:return first
		if len(rest)==1:return self.add(first,rest[0])
		if len(rest)==2:return self.add3(first,*rest)
		raise AssertionError("unsupported selector arity")
	def addm(self,*ws,force_bb=None):
		cv,vs=0,[]
		for w in ws:
			if all(x[0]==0 for x in w):cv+=sum(x[1]<<i for i,x in enumerate(w))
			else:vs.append(w)
		cv&=M32
		if not vs:return _constw(cv)
		call_id=self.ahi;self.ahi+=1;hint=_ADD_HINTS[call_id]
		if hint and force_bb is None:op=list(vs)+([_constw(cv)]if cv else[]);assert hint<(1<<len(op))and hint.bit_count()==3;return self._choice(op,hint)
		return self._baseline(cv,list(vs),force_bb,call_id)
	def xorw(self,A,B):return[self.XOR(a,b)for a,b in zip(A,B)]
def _tz(v):return 32 if v==0 else(v&-v).bit_length()- 1
def _constw(v):return[ONE if(v>>i)&1 else ZERO for i in range(32)]
def _sigma(g,A,r1,r2,r3,shift):
	out=[]
	for j in range(32):t=g.XOR(A[(j+r1)%32],A[(j+r2)%32]);out.append(g.XOR(t,(A[j+r3]if j+r3<32 else ZERO)if shift else A[(j+r3)%32]))
	return out
def _add_u(g,A,u,c1=0,ch1=None):
	s=[None]
	if ch1 is not None:s1,c=g.fa(A[1],ch1,ONE if c1 else ZERO);s.append(s1)
	elif c1:s.append((u[1][0],u[1][1]^1));c=g.OR(A[1],u[1])
	else:s.append(u[1]);c=g.AND(A[1],(u[1][0],u[1][1]^1))
	for i in range(2,31):
		s.append(g.XOR(u[i],c));w=g.XOR(A[i],c)
		if u[i][0]and w[0]and u[i][0]!=w[0]and u[i][1]!=w[1]:c=g.XOR(g.AND((u[i][0],u[i][1]^1),w),c)
		else:c=g.XOR(g.AND(u[i],w),A[i])
	s.append(g.XOR(u[31],c));return s
def _col_uc(g,h_w,u_in,ucs,Ucs,cb,ch,oU):
	idx=(cb<<4)|h_w[1]|(u_in[1]<<1)|(ucs[1]<<2)|(Ucs[1]<<3);code=UCD[64+idx]if oU else UCD[2*idx+ch]
	if not code:w6=(u_in[0],u_in[1]^cb);s=g.XOR(Ucs,w6);w9=g.XOR(ucs,w6);w10=g.OR(Ucs,(w9[0],w9[1]^1));w11=g.OR(u_in,(h_w[0],h_w[1]^cb));return s,(ZERO if oU else g.XOR(w6,(w10[0],w10[1]^1))),g.XOR(w10,(w11[0],w11[1]^1))
	ops=("x","a","o");s_raw=g.mk("x",u_in[0],Ucs[0]);is_w0=oU and((code>>26)&1);raws=[h_w[0],u_in[0],ucs[0],Ucs[0],s_raw]if is_w0 else[u_in[0],ucs[0],Ucs[0],s_raw,g.mk("a"if u_in[1]else "o",h_w[0],u_in[0])]
	for q in range(3):c=(code>>(8*q))&255;raws.append(g.mk(ops[c&3],raws[(c>>2)&7],raws[c>>5]))
	a3=(code>>24)&3;U_raw=g.mk("x",raws[4+a3],raws[7])if a3<3 else raws[7];return(s_raw,u_in[1]^Ucs[1]^cb),(ZERO if oU else(raws[4+((code>>26)&3)],(code>>28)&1)),(U_raw,(code>>29)&1)
def _adduc(g,A,u,cv,c1=0,ch1=None):
	if not cv:return _add_u(g,A,u,c1,ch1),0
	k=_tz(cv)
	if k<=1 or k>=31:return _add_u(g,A,u,c1,ch1),cv
	dp_c,dp_ch=[[[0,0],[0,0]]for _ in range(31)],[[[0,0],[0,0]]for _ in range(31)];cb30=(cv>>30)&1
	for pu in(0,1):
		for pU in(0,1):code=UCD[64+((cb30<<4)|A[30][1]|(u[30][1]<<1)|(pu<<2)|(pU<<3))];dp_c[30][pu][pU]=(5+((code>>27)&1))if code else 6
	for i in range(29,k,- 1):
		cb=(cv>>i)&1
		for pu in(0,1):
			for pU in(0,1):
				idx=(cb<<4)|A[i][1]|(u[i][1]<<1)|(pu<<2)|(pU<<3)
				if not UCD[2*idx]:dp_c[i][pu][pU]=7+dp_c[i+1][cb][0]
				else:
					bc,bch=999,0
					for ch in(0,1):
						code=UCD[2*idx+ch]
						if code:
							tc=6+dp_c[i+1][(code>>28)&1][(code>>29)&1]
							if tc<bc:bc,bch=tc,ch
					dp_c[i][pu][pU],dp_ch[i][pu][pU]=bc,bch
	out=[None]*32
	if ch1 is not None:out[1],c=g.fa(A[1],ch1,ONE if c1 else ZERO)
	elif c1:out[1],c=(u[1][0],u[1][1]^1),g.OR(A[1],u[1])
	else:out[1],c=u[1],g.AND(A[1],(u[1][0],u[1][1]^1))
	for i in range(2,k):
		out[i]=g.XOR(u[i],c);w=g.XOR(A[i],c)
		if u[i][0]and w[0]and u[i][0]!=w[0]and u[i][1]!=w[1]:c=g.XOR(g.AND((u[i][0],u[i][1]^1),w),c)
		else:c=g.XOR(g.AND(u[i],w),A[i])
	pw=A[k][1]^c[1];cck=3 if u[k][1]==pw else 4;pUk=0 if(u[k][1]==0 and pw==0)else 1;cmk=cck+(1 if k==30 else min(dp_c[k+1][A[k][1]][pUk],dp_c[k+1][c[1]][pUk])+1);base=6*(31-k);pcu,pcc=c[1],0;bm,bc=(k,cmk)if cmk<base else(31,base)
	for i in range(k,30):
		pti,pwi=u[i][1]^pcu,A[i][1]^pcu;pcun=(pwi^pcu)if u[i][1]!=pwi else(u[i][1]^A[i][1]);cb=(cv>>i)&1;pccn=pti if i==k else(pti if pti==pcc else cb);pcu,pcc=pcun,pccn;m,pUm=i+1,pcu^pcc;cm=6*(m-k)+min(dp_c[m][pcu][pUm],dp_c[m][pcc][pUm])
		if cm<bc:bc,bm=cm,m
	if bm==31:
		for i in range(k,31):
			out[i]=g.XOR(u[i],c);w=g.XOR(A[i],c)
			if u[i][0]and w[0]and u[i][0]!=w[0]and u[i][1]!=w[1]:c=g.XOR(g.AND((u[i][0],u[i][1]^1),w),c)
			else:c=g.XOR(g.AND(u[i],w),A[i])
		out[31]=g.XOR(u[31],c);return out,cv
	if bm==k:s0=g.XOR(u[k],c);out[k]=(s0[0],s0[1]^1);Ucs=g.OR(u[k],g.XOR(A[k],c));ucs=(A[k]if dp_c[k+1][A[k][1]][Ucs[1]]<=dp_c[k+1][c[1]][Ucs[1]]else c)if k<30 else ZERO;sc=k+1
	else:
		cu,cc,cw=c,ZERO,_constw(cv)
		for i in range(k,bm):
			ti=g.XOR(u[i],cu);w=g.XOR(A[i],cu)
			if u[i][0]and w[0]and u[i][0]!=w[0]and u[i][1]!=w[1]:cu=g.XOR(g.AND((u[i][0],u[i][1]^1),w),cu)
			else:cu=g.XOR(g.AND(u[i],w),A[i])
			out[i],cc=g.fa(ti,cw[i],cc)
		Ucs=g.XOR(cu,cc);ucs=cu if dp_c[bm][cu[1]][Ucs[1]]<=dp_c[bm][cc[1]][Ucs[1]]else cc;sc=bm
	for i in range(sc,31):cb=(cv>>i)&1;ch=0 if i==30 else dp_ch[i][ucs[1]][Ucs[1]];out[i],ucs,Ucs=_col_uc(g,A[i],u[i],ucs,Ucs,cb,ch,i==30)
	s31=g.XOR(u[31],Ucs);out[31]=(s31[0],s31[1]^((cv>>31)&1));return out,0
def _t1hg(g,e,f,gg,h,hg,Wd,d=None):
	sp=getattr(g,"split",{});fg=[g.XOR(f[j],gg[j])for j in range(32)];has_h=any(x[0]!=0 for x in h);ch1=g.XOR(f[1],g.AND((e[1][0],e[1][1]^1),fg[1]))if(has_h and e[1][0]and fg[1][0]and e[1][1]!=fg[1][1])else None;tt=[None if(j==1 and ch1 is not None)else g.AND(e[j],fg[j])for j in range(32)];u=[None if(j==1 and ch1 is not None)else g.XOR(hg[j],tt[j])for j in range(32)];S1=_sigma(g,e,6,11,25,False);cv,vs=0,[S1]
	for w in Wd:
		if all(x[0]==0 for x in w):cv+=sum(x[1]<<i for i,x in enumerate(w))
		else:vs.append(w)
	cv&=M32;has_d=d is not None and any(x[0]!=0 for x in d)
	if has_h and len(vs)==2:
		if not cv:t=_add_u(g,h,u,0,ch1);return g.add3(t,vs[0],vs[1],0,None,h[0],u[0]),fg,0
		pref1=None if ch1 is not None else(1 if(h[1][0]and u[1][0]and h[1][1]==u[1][1])else 0);cands=[(vs[1],cv)]
		if tuple(vs[1])in sp:s_raw,cv_rem=sp[tuple(vs[1])];cands.append((s_raw,(cv+cv_rem)&M32))
		best=None
		for w_cand,cv_cand in cands:
			for c0 in(0,1):
				for c1 in(0,1):
					for d_ in((0,1)if has_d else(0,)):
						tot=c0+2*c1+d_;b1=1 if(pref1 is None or c1==pref1)else 0;score=(2*_tz((cv_cand-tot)&M32)+b1,-tot,-d_)
						if best is None or score>best[0]:best=(score,c0,c1,d_,w_cand,cv_cand)
		_,c0,c1,delta,w_best,cv_best=best;cv2=(cv_best-c0- 2*c1-delta)&M32;t,rem=_adduc(g,h,u,cv2,c1,ch1);s=g.add3(t,vs[0],w_best,c0,None,h[0],u[0]);return(g.add(s,_constw(rem))if rem else s),fg,delta
	return g.addm(u,S1,*Wd),fg,0
def _rnd2(g,st,Wd):
	a,b,c,d,e,f,gg,h,prev,hg=st;t1,fg,delta=_t1hg(g,e,f,gg,h,hg,Wd,d);S0=_sigma(g,a,2,13,22,False);ab,mj=[],[]
	for j in range(32):
		ab.append(g.XOR(a[j],b[j]))
		if c[j]==ZERO:mj.append(g.AND(a[j],b[j]))
		elif ab[j][0]and prev[j][0]and ab[j][0]!=prev[j][0]and ab[j][1]!=prev[j][1]:mj.append(g.XOR(g.AND((ab[j][0],ab[j][1]^1),prev[j]),c[j]))
		else:mj.append(g.XOR(g.AND(ab[j],prev[j]),b[j]))
	ne=g.add(d,t1,ONE if delta else ZERO);na=g.add3(t1,S0,mj,delta)if delta else g.addm(t1,S0,mj);return(na,a,b,c,ne,e,f,gg,ab,fg)
def _ch3(g,cs,B,e,f,gg,hg,kv):
	X,AN,OR=g.XOR,g.AND,g.OR;fg=[X(f[j],gg[j])for j in range(32)];s,R1,R2,u,U=[None]*32,[None]*32,[None]*32,ONE,ZERO
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
			if(z[1]^pw5)!=pt:w9=X(u,w6);w10=OR(U,(w9[0],w9[1]^1));u,U=(ZERO if oU else X(w6,(w10[0],w10[1]^1))),X(w10,(w11[0],w11[1]^1))
			else:w9=X(u,s[i]);w10=AN((U[0],U[1]^1),w9);u,U=(ZERO if oU else X(w6,w11)),X(w10,w11)
		elif b2:n5=X(z,U);n9=X(x,n5);s[i]=X(w5,n5);n8=OR(U,X(z,u));n11=AN((w5[0],w5[1]^1),n9);u,U=(ZERO if oU else X(n5,n11)),X(n8,n11)
		else:n5=X(z,U);w5U=X(w5,U);s[i]=X(w5,n5);g1=OR((x[0],x[1]^1),w5);g2=AN(n5,w5U);u,U=(ZERO if oU else X(w5,(g1[0],g1[1]^1))),X(g1,g2)
	return g.addm(s,R1,R2,_constw(kv)),fg
def _net_u(G=Gen):
	g=G(256);g.split={};Y=[[g.inputs[32*(7-k)+j]for j in range(32)]for k in range(8)];W=[None]*ROUNDS
	for i in range(PRE):W[i]=_constw(PREFIX_WORDS[i])
	for k in range(8):pos=VARBASE+k;W[pos]=g.addm(Y[k],_constw((-K[pos])&M32))if pos in OFFSET else Y[k]
	for pos,val in TAILMAP.items():W[pos]=_constw(val)
	wd=lambda i:(Y[i-VARBASE],)if i in OFFSET else(_constw(4 if i==23 else K[i]),W[i]);z,nk9=_constw(0),_constw((-K[9])&M32);st=(Y[0],z,z,z,Y[0],z,z,nk9,z,nk9);r=ROUNDS
	def make_w(i):
		if W[i]is not None:return
		if i>=r- 2:W[i]=g.add3(W[i- 16],_sigma(g,W[i- 15],7,18,3,True),W[i- 7]);return
		w_m7=(Y[i- 15],_constw((-K[i- 7])&M32))if i in(17,21,22)else((g.split[tuple(W[16])][0],_constw(g.split[tuple(W[16])][1]))if i==23 else(W[i- 7],));W[i]=g.addm(W[i- 16],_sigma(g,W[i- 15],7,18,3,True),*w_m7,_sigma(g,W[i- 2],17,19,10,True),force_bb=2 if i==23 else None)
	for i in range(9,r):
		if i>=16:
			if i==19:make_w(19);make_w(21);s23=g.add3(_sigma(g,W[8],7,18,3,True),g.split[tuple(W[16])][0],_sigma(g,W[21],17,19,10,True),2);cv23=(4-K[23])&M32
			elif i==23:W[23]=s23;g.split[tuple(s23)]=(s23,cv23)
			else:
				make_w(i)
				if i==31:make_w(32)
		if i<r-NTAIL:
			st=_rnd2(g,st,wd(i))
			if i==23:s_r,cv_r=g.split[tuple(W[i])];W[i]=g.add(s_r,_constw(cv_r))
	if TAILB:a6,a7,a8,a9,e6,e7,e8,e9,prev,hg=st;T5,fg,_=_t1hg(g,e6,e7,e8,e9,hg,(_constw(K[r- 6]- 1),W[r- 6]));e5=g.add(a9,T5,ONE);mj=[g.OR((ab[0],ab[1]^1),a8[j])if(QM>>j)&1 else g.AND(ab,a8[j])for j in range(32)for ab in(g.XOR(a6[j],a7[j]),)];Q=g.add(T5,mj,ONE);T4,fg,_=_t1hg(g,e5,e6,e7,e8,fg,wd(r- 5));e4=g.add(a8,T4);e3,fg=_ch3(g,[W[r- 4],a7,_sigma(g,e4,6,11,25,False)],e7,e4,e5,e6,fg,K[r- 4]- 2);e2,_=_ch3(g,[W[r- 3],a6,_sigma(g,e3,6,11,25,False)],e6,e3,e4,e5,fg,K[r- 3]- 2);X=g.addm(W[r- 2],_sigma(g,W[r- 4],17,19,10,True),e5,[g.OR(e2[j],e4[j])if(XM>>j)&1 else g.AND((e2[j][0],e2[j][1]^1),e4[j])for j in range(32)]);Y_out=g.addm(W[r- 1],_sigma(g,W[r- 3],17,19,10,True),e4);bw=[e3,e2,a7,a6,Q,T4,X,Y_out];out=[bw[PERM[k]]for k in range(8)];assert g.ahi==len(_ADD_HINTS);return g,[t for w in out for t in w]
MAX_NODES=86123;MAX_RECORDS=85831;CSE_PROBE_LIMIT=8
class BGen(Gen):
	def __init__(self,n,run,pas):self.n,self.run,self.pas,self.calls=n,run,pas,0;self.ahi=0;self.inputs=[(j+1,0)for j in range(n)];self.nn,self.rn,self.ncse,self.max_probe=n+1,0,0,0;self.recent,self.cse_k,self.cse_v=[None]*8,[0]*1024,[None]*1024
	def _gate(self,node):
		for d in range(min(8,self.rn)):
			r=self.recent[(self.rn- 1-d)&7]
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
				if self.cse_k[p]==key:self.max_probe=max(self.max_probe,probes);return self.cse_v[p]
				p=(p+1)&1023;probes+=1
				if probes>CSE_PROBE_LIMIT:self.run.err=16;return 0
			self.max_probe=max(self.max_probe,probes);self.ncse+=1
			if self.ncse>900:self.run.err=10
			s=self._new(op,a,b);self.cse_k[p],self.cse_v[p]=key,s
		else:
			for d in range(min(8,self.rn)):
				r=self.recent[(self.rn- 1-d)&7]
				if r[:3]==(op,a,b):return r[3]
			s=self._new(op,a,b)
		self.recent[self.rn&7]=(op,a,b,s);self.rn+=1;return s
class BoundedEmitter:
	def __init__(self):self.uses,self.err,self.records=[0]*MAX_NODES,0,[]
	def emit(self,op,d,a,b):
		if len(self.records)>=MAX_RECORDS or max(d,a,b)>=1024:self.err=5;return
		self.records.append((op,d,a,b))
	def take(self,prefer=None,p=0):
		if prefer is not None and self.free>>prefer&1:r=prefer
		else:
			m=self.free&~p or self.free&~((1<<512)-(1<<448))or self.free&~((1<<480)-(1<<448))or self.free
			if not m:self.err=8;return 0
			r=(m&-m).bit_length()- 1
		self.free&=~(1<<r);return r
	def alloc(self,op,k,x,y):
		self.uses[x]-=1;self.uses[y]-=1;dx,dy=self.uses[x]==0,self.uses[y]==0;want=256+self.order[self.co][1]if self.co<len(self.order)and self.order[self.co][0]==k else None;M8,M14=(1<<288)-(1<<256),(1<<480)-(1<<448);borrow=~((self.pend if k<self.f0- 260 else self.pend&~M14)&~M8)if self.uses[k]<=3 and k<self.f1- 260 and want is None else self.pend;dst=None
		if want is not None:
			if self.free>>want&1:dst=self.take(want)
			elif dx and self.reg[x]==want:dst=want
			elif dy and self.reg[y]==want:dst=want
		if dst is None:
			if dx and(not(borrow>>self.reg[x]&1)or self.reg[x]==want):dst=self.reg[x]
			elif dy and(not(borrow>>self.reg[y]&1)or self.reg[y]==want):dst=self.reg[y]
		if dx and self.reg[x]!=dst:self.free|=1<<self.reg[x]
		if dy and self.reg[y]!=dst:self.free|=1<<self.reg[y]
		if dst is None:dst=self.take(p=borrow)
		if dst==want:self.pend&=~(1<<dst)
		self.emit({"x":1,"a":2,"o":3}[op],dst,self.reg[x],self.reg[y]);self.reg[k]=dst
		while self.co<len(self.order)and self.order[self.co][0]==k:self.oreg[self.order[self.co][1]]=dst;self.co+=1
		if not self.uses[k]:self.err=9;self.free|=1<<dst
	def run(self):
		g0,out0=_net_u(lambda n:BGen(n,self,0));nodes,self.calls=g0.nn,g0.calls;self.onode=[x[0]for x in out0];self.oneg=[x[1]for x in out0];self.order=sorted((n,i)for i,n in enumerate(self.onode)if n)
		for n,_ in self.order:self.uses[n]+=1
		self.f0,self.f1=self.order[0][0],self.order[32][0];self.free=sum(1<<r for r in range(REGISTERS)if r<256 or r>=512);self.pend=sum(1<<(256+i)for i,n in enumerate(self.onode)if n);self.reg={n:INREG(n- 1)for n in range(1,257)};self.oreg,self.co=[0]*256,0
		while self.co<len(self.order)and self.order[self.co][0]<=256:n,i=self.order[self.co];self.oreg[i]=INREG(n- 1);self.co+=1
		for n in range(1,257):
			if not self.uses[n]:self.free|=1<<INREG(n- 1)
		g1,out1=_net_u(lambda n:BGen(n,self,1));self.calls+=g1.calls;self.max_probe=max(g0.max_probe,g1.max_probe);assert out1==out0 and self.max_probe<=CSE_PROBE_LIMIT;todo=[(i,self.oreg[i])for i,n in enumerate(self.onode)if n and self.oreg[i]!=256+i];moves=0
		while todo:
			srcs=[s for _,s in todo];k=next((k for k,(i,s)in enumerate(todo)if 256+i not in srcs),None)
			if k is None:s,t=todo[0][1],self.take();self.emit(4,t,s,0);moves+=1;todo=[(i,t if r==s else r)for i,r in todo]
			else:i,s=todo.pop(k);self.emit(4,256+i,s,0);moves+=1
		for i,n in enumerate(self.onode):
			if not n:self.emit(5,256+i,self.oneg[i],0)
		top=max(max(r[1:4])if r[0]<=3 else max(r[1:3])if r[0]==4 else r[1]for r in self.records)+1;q=sum(self.oneg[i]<<(32*(7-i//32)+i%32)for i in range(256)if self.onode[i]);counts=[sum(r[0]==op for r in self.records)for op in(1,2,3)];info=(len(self.records),top,nodes,self.calls,moves,self.err,*counts,4*MAX_RECORDS,COUNTERS,MAX_NODES,GEN_STATE_BYTES,len(_ADD_HINTS),GEN_CONSTANT_BYTES);return info,q,self.records
def _encode_body(records):
	out=bytearray()
	for op,d,a,b in records:assert 1<=op<=3 and max(d,a,b)<1024;out+=((op- 1)|(d<<2)|(a<<12)|(b<<22)).to_bytes(4,"little")
	return bytes(out)
def bounded_check(pr):info,q,records=BoundedEmitter().run();py=[({"^":1,"&":2,"|":3,"M":4,"S":5}[o],d,a,b)for o,d,a,b in pr.recs];assert info==EXPECTED_EMITTER_INFO;assert q==pr.qint==POLARITY_Q and records==py;assert hashlib.sha256(GEN_C.encode()).hexdigest()==STATIC_C_SHA256;stream=_encode_body(records);digest=hashlib.sha256(stream).hexdigest();assert len(stream)==4*pr.instr and digest==STATIC_SLP_SHA256;return info,digest
def _alloc(g,nin,fixed,outs,tgt,free0,E):
	N=g.nodes;uses=[0]*len(N);want={}
	for _,x,y in N[nin+1:]:uses[x]+=1;uses[y]+=1
	for i,(n,_)in enumerate(outs):uses[n]+=1;want.setdefault(n,tgt[i])
	oids=sorted(want);f0,f1=oids[0],oids[32];M8,M14,M1415=(1<<288)-(1<<256),(1<<480)-(1<<448),(1<<512)-(1<<448);reg=dict(fixed);free=sum(1<<r for r in free0 if r not in fixed.values())|sum(1<<r for v,r in fixed.items()if not uses[v]);pend=sum(1<<tgt[i]for i,(n,_)in enumerate(outs)if n)
	def take(w=None,p=0):nonlocal free;m=1<<w if w is not None and free>>w&1 else(free&~p or free&~M1415 or free&~M14 or free);r=(m&-m).bit_length()- 1;free&=~(1<<r);return r
	for k in range(nin+1,len(N)):
		op,x,y=N[k];uses[x]-=1;uses[y]-=1;dying=[v for v in(x,y)if not uses[v]];w=want.get(k);p=~((pend if k<f0- 260 else pend&~M14)&~M8)if(uses[k]<=3 and k<f1- 260 and w is None)else pend;dst=take(w)if(w is not None and free>>w&1)else w if any(reg[v]==w for v in dying)else next((reg[v]for v in dying if not p>>reg[v]&1 or reg[v]==w),None)
		for v in dying:
			if reg[v]!=dst:free|=1<<reg[v]
		if dst is None:dst=take(p=p)
		reg[k]=dst
		if dst==w:pend&=~(1<<w)
		E(({"x":"^","a":"&","o":"|"}[op],dst,reg[x],reg[y]))
	return sum(reg[n]!=tgt[i]for i,(n,_)in enumerate(outs)if n)
def INREG(j):return 256+32*(7-j//32)+j%32
def assemble():info,q,records=BoundedEmitter().run();assert info[4:6]==(0,0);_QM[:]=[q];return[({1:"^",2:"&",3:"|"}[op],d,a,b)for op,d,a,b in records],info[4],info[3]
class Prog:
	def __init__(self):self.recs,self.moves,self.calls=assemble();self.q,self.qint,self.pin=[0]*256,_QM[0],[0]*256;self.qwords=[(self.qint>>(32*i))&M32 for i in range(8)];self.instr=self.kernel=len(self.recs);self.nregs=max(max(r[1:4])for r in self.recs)+1;self.compile()
	def run(self,pc,end,regs):
		for op,d,a,b in self.recs[pc:end]:regs[d]=regs[a]^regs[b]if op=="^"else regs[a]&regs[b]if op=="&"else regs[a]|regs[b]
		return end-pc
	def compile(self):
		ns,fs={"ALL":ALL},[]
		for a in range(0,len(self.recs),4096):exec(compile("def c(r):\n"+"".join(" r[%d]=r[%d]%sr[%d]\n"%(d,x,o,y)for o,d,x,y in self.recs[a:a+4096]),"<p>","exec"),ns);fs.append(ns["c"])
		self.ns=ns;self.fast=lambda r:[c(r)for c in fs]
	def step(self,*planes):
		regs=[0]*REGISTERS
		for j,pl in enumerate(planes):regs[INREG(j)]=pl
		self.fast(regs);return[regs[INREG(j)]for j in range(len(planes))]
def _tmasks():
	res,s={},128
	while s:
		m=0
		for c in range(256):
			if not c&s:m|=1<<c
		res[s]=m;s>>=1
	return res
_TM=_tmasks()
def transpose(rows):
	R=list(rows)+[0]*(256-len(rows));s=128
	while s:
		m=_TM[s]
		for i in range(256):
			if not i&s:t=((R[i]>>s)^R[i+s])&m;R[i+s]^=t;R[i]^=t<<s
		s>>=1
	return R
def pack_lanes(xs,n,pin):T=transpose(xs);return[T[j]^(ALL if pin[j]else 0)for j in range(n)]
def lanes_of(planes,n,pin):T=transpose([planes[j]^(ALL if pin[j]else 0)for j in range(n)]);return T[:256]
def lane_value(planes,l,pin,n):
	x=0
	for j in range(n):x|=(((planes[j]>>l)&1)^pin[j])<<j
	return x
def set_lane(planes,l,x,pin,n):bit=1<<l;return[(planes[j]&~bit)|((((x>>j)&1)^pin[j])<<l)for j in range(n)]
LAMBDA=Fraction(497,1000);CUTLOSS=Fraction(15,100000);TAIL_AGES=1e-6;CMAX=7;CUT_HALT_ORDER=CMAX+1;P_MIN=0.390000001;GRAIN=10**21;STAGE1_PLANES=20;LOOP_OPS=3;HIT_OPS=2800;EVENT_OPS=3800;CUT_OPS=4200;SLICE_OPS=1300;RECOVER_EXTRA=76;INSTR_BYTES=5;BODY_BYTES=4;REC_RECORD_BYTES=5;GEN_INSTR_BYTES=36;HANDLER_CODE,SETUP_CODE,RECOVERY_CODE=1000,160,47;REGISTERS=905;REGFILE=REGISTERS*32;COUNTERS=16384;ARRAYS=(2*ROUNDS-16)*32;KEYB=48;SLOTB=KEYB;MEM_LIMIT=1<<20;ADVICE=0;KAPPA_256=13;WASM_RUN_OPERATORS=167_369_809;WASM_OPERATOR_FACTOR=2;WASM_EMITTER_INSTR=8897;GEN_STATE_ARRAYS=dict(recent=8*16,cse_k=1024*4,cse_v=1024*4,free=32*4,pending=32*4,W=64*32*4,WS=16*32*4,WCV=16*4,V=10*32*4,Y=8*32*4,word_scratch=14*32*4,X2_AM_A3=3*32*4,TB=11*32*4,tail_scratch=4*32*4,AW=8*4,output_arrays=6*256*4,output_polarities=256,info=15*4+32,scalars=17*4,alignment=128);GEN_CONSTANT_ARRAYS=dict(IV=8*4,K=64*4,PW=8*4,PERM=8*4,UCD=96*4);GEN_STATE_BYTES=sum(GEN_STATE_ARRAYS.values());GEN_CONSTANT_BYTES=sum(GEN_CONSTANT_ARRAYS.values());assert GEN_STATE_BYTES==32000 and GEN_CONSTANT_BYTES==736;GEN_SCRATCH=MAX_NODES+GEN_STATE_BYTES+len(_ADD_HINTS)+GEN_CONSTANT_BYTES+4096;SETUP_FIXED=256*3100+20000;OFFSET_SEARCH_EVALS=64+1+3*192+1000;SELECTOR_THREE_WORD_SITES=51;SELECTOR_FOUR_WORD_SITES=41;SELECTOR_ALTERNATIVES=SELECTOR_THREE_WORD_SITES+SELECTOR_FOUR_WORD_SITES*10+2;SELECTOR_SEARCH_EVALS=1+2*SELECTOR_ALTERNATIVES;SEARCH_EVAL_OPS=1<<48;OFFSET_SEARCH_OPS=OFFSET_SEARCH_EVALS*SEARCH_EVAL_OPS;SELECTOR_SEARCH_OPS=SELECTOR_SEARCH_EVALS*SEARCH_EVAL_OPS;SEARCH_IMAGE_INSTR=10_000;SEARCH_LOCAL_BYTES=65_536;OFFSET_SEARCH_PEAK=SEARCH_IMAGE_INSTR*GEN_INSTR_BYTES+GEN_SCRATCH+SEARCH_LOCAL_BYTES+48;SELECTOR_SEARCH_PEAK=SEARCH_IMAGE_INSTR*GEN_INSTR_BYTES+GEN_SCRATCH+SEARCH_LOCAL_BYTES+len(_ADD_HINTS);CFG={16:dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),18:dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),256:dict(s1=20,W=102,kappa=KAPPA_256,Sb=1<<48)}
def stage1_ops(pin,s1):
	npos=sum(1 for j in range(s1)if not pin[j]);nneg=s1-npos;ops=max(npos- 1,0)+max(nneg- 1,0)
	if nneg:ops+=2 if npos else 1
	return ops+1+2
def stage1(planes,s1,pin):
	nz=0;pos=[planes[j]for j in range(s1)if not pin[j]];neg=[planes[j]for j in range(s1)if pin[j]]
	if pos:
		acc=pos[0]
		for q in pos[1:]:acc|=q
		nz|=acc
	if neg:
		acc=neg[0]
		for q in neg[1:]:acc&=q
		nz|=acc^ALL
	return ALL^nz
def inflight_m(lanes=LANES,eps=TAIL_AGES):
	m=lanes
	while True:
		x=m/lanes
		if exp(-lanes*(x- 1-log(x)))<=eps:return m
		m+=1
INFLIGHT=inflight_m()
def _plan(n,Tp,kappa,tmax,Sb):
	c=CFG[n];s1,W=c["s1"],c["W"];N,D=1<<n,s1+W;L=Fraction(1<<D,Tp)
	if n==256:B=_b256(Tp,tmax,kappa,Sb)
	else:ureq=isqrt(2*N*LAMBDA.numerator//LAMBDA.denominator)+2;num,den=ureq+INFLIGHT*L+1,CUTLOSS.denominator;q=-(-(num*den)//(den-CUTLOSS.numerator));B=-(-q//LANES)
	cc=-(-kappa*L.numerator//L.denominator);fb=(Tp- 1).bit_length();return dict(n=n,s1=s1,W=W,D=D,Tp=Tp,fb=fb,kb=min(KEYB-fb,n-D),L=L,N=N,Q=B*LANES,B=B,kappa=kappa,Sb=Sb,c=cc,capr=cc+Sb,tmax=tmax,e2max=2*B*LANES//(1<<s1)+64,cmax=CMAX if n==256 else 10**9)
def tail_log2(mean,k):return(-mean+k*(1+log(mean/k)))/log(2)
_PROG=[];_QM=[0]
def prog():
	global REGFILE
	if not _PROG:_PROG.append(Prog());REGFILE=32*(_PROG[0].nregs+3)
	return _PROG[0]
def other_code(pr=None):return HANDLER_CODE+rec().instr+RECOVERY_CODE+SETUP_CODE
def machine_constants(pr=None):pr=pr or prog();filt=stage1_ops(pr.pin,STAGE1_PLANES);code=pr.instr*BODY_BYTES+rec().instr*REC_RECORD_BYTES+(filt+LOOP_OPS+HANDLER_CODE+RECOVERY_CODE+SETUP_CODE)*INSTR_BYTES;return pr.kernel,filt,pr.kernel+filt+LOOP_OPS,code,8*(MEM_LIMIT-code-REGFILE-COUNTERS-ADVICE-ARRAYS)//SLOTB-LANES-CMAX
def table_bytes(tmax):return-(-(tmax+LANES+CMAX)*SLOTB//8)
def boundary_test(pr,p):stream=_encode_body([({"^":1,"&":2,"|":3}[o],d,a,b)for o,d,a,b in pr.recs]);assert len(stream)==4*pr.instr and all(max(r[1:])<1024 for r in pr.recs);max_key=(((1<<p["kb"])- 1)<<p["fb"])|(p["Tp"]- 1);assert 0<max_key+1<1<<KEYB;assert p["tmax"]+LANES+CMAX<1<<18;rp=rec();control=rp.init+rp.flat;assert len({r[0]for r in control})<=16 and all(max(r[1:])<1024 for r in control);assert table_bytes(p["tmax"])==-(-(p["tmax"]+LANES+CMAX)*SLOTB//8);return dict(body_bytes=len(stream),max_register=max(max(r[1:])for r in pr.recs),max_key=max_key,max_trail=p["tmax"]+LANES+CMAX- 1,control_opcodes=len({r[0]for r in control}),control_max_field=max(max(r[1:])for r in control))
def phase_bytes(code,tmax):prog();setup=code+COUNTERS+REGFILE+ARRAYS+WASM_EMITTER_INSTR*GEN_INSTR_BYTES+GEN_SCRATCH;search=code+COUNTERS+REGFILE+ARRAYS+table_bytes(tmax);return setup,search
def search_envelopes():gate_ops=1024;raw=2*160*64*32*13*13*12*gate_ops;assert 2*raw<SEARCH_EVAL_OPS;assert OFFSET_SEARCH_EVALS==1641 and SELECTOR_ALTERNATIVES==463 and SELECTOR_SEARCH_EVALS==927;return raw,raw
def plan(n,kappa=None,Tp=None):
	if n!=256:c=CFG[n];p=_plan(n,c["Tp"],c["kappa"],0,c["Sb"]);p["tmax"]=4*(p["Q"]//int(p["L"]))+64;return p
	kappa=kappa or KAPPA_256;tmax=machine_constants()[4]
	if Tp:return _plan(256,Tp,kappa,tmax,CFG[256]["Sb"])
	lo,hi=1.0,float(tmax- 59)
	for _ in range(60):mid=(lo+hi)/2;lo,hi=(mid,hi)if tail_log2(mid,tmax- 59)<=- 20 else(lo,mid)
	a,z=1,4097
	while z-a>1:m=(a+z)//2;a,z=(m,z)if _lossq(m,lo,tmax,kappa,CFG[256]["Sb"])["P_lower"]>=P_MIN else(a,m)
	return _plan(256,a,kappa,tmax,CFG[256]["Sb"])
def ledger(p=None,pr=None):p=p or plan(256);pr=pr or prog();search_envelopes();ph,filt,body,code,_=machine_constants(pr);emitter=WASM_OPERATOR_FACTOR*WASM_RUN_OPERATORS+1;parts=dict(main=body*p["B"],slices=-(-p["B"]//p["Sb"])*SLICE_OPS,stage1_hits=p["e2max"]*HIT_OPS,events=(p["tmax"]+1)*(EVENT_OPS+6*(p["tmax"]+LANES+CMAX)),cuts=p["cmax"]*CUT_OPS,recovery=2*p["capr"]*(packed_ops()+RECOVER_EXTRA)+600+len(rec().init),setup=SETUP_FIXED+emitter,offset_search=OFFSET_SEARCH_OPS,selector_search=SELECTOR_SEARCH_OPS);return dict(parts=parts,total=sum(parts.values()),plan=p,body=body,emitter=emitter)
TB=18;FINE,COARSE=20000,2000
def _lossq(Tp,q,tmax,kappa,Sb,rate=1.0):
	from math import expm1;D=122;L=Fraction(1<<D,Tp);c=-(-kappa*L.numerator//L.denominator);th,Lf,cf=Tp/2.0**D,float(L),float(c);Q,B,Np=q*Lf,q*Lf/LANES,2.0**256/rate;k=int(q)+1
	while tail_log2(q,k)>- 40:k+=1
	n2,shift=k+LANES+CMAX,1/(1-k*Q/Np);pi=lambda m:exp(-m*(m- 1)/(2*Np));split=max(1.0,Q- 120*LANES*Lf);edges=[split*i/COARSE for i in range(COARSE+1)]+[split+(Q-split)*i/FINE for i in range(1,FINE+1)];delay,pa=0.0,1.0
	for b in edges[1:]:pb=pi(b);delay+=(pa-pb)*exp(-th*max(0.0,B-b/LANES));pa=pb
	p,ql,hq=exp(-cf*th),Q*Lf/Np,Q*(Q- 1)/(2*Np);p2=exp(-(cf- 1)*th)*(1+(cf- 1)*th/(1-th));hh=(Q*(Q- 1)/2+2.0**TB*Q)/Np;cuts=1-sum(comb(n2,j)*p**j*exp((n2-j)*log1p(-p))for j in range(CUT_HALT_ORDER));t=dict(no_collision=pi(Q)*shift,delay=delay*shift,partner_own_trail=ql,partner_cut_trail=(cf+Sb)*Q*p*(q+LANES)/((1-p)*Np),too_old=hq*p2,rest_of_path=hq*Lf*(Q+2.0**TB)/Np,finished_count=2.0**- 40,cut_halt=cuts+ql*(1+(2+kappa)*exp(-kappa/2)+2*hq)+hq*p*(3+2*kappa),key_false_match=tmax*(tmax- 1)/2*2.0**-(min(KEYB-(Tp- 1).bit_length(),256-D)+log2(Tp)),table_capacity=2.0**tail_log2(q,tmax- 59),misc=Q*2.0**TB/Np+k*k*Lf/Np+255*Q/Np+exp(min(700.0,- 300+(exp(5)- 1)*hh))+2.0**- 90);t["sum"]=sum(t.values());t["P_lower"]=1-t["sum"];t.update(trails=q,k=k);return t
_B={}
def _b256(Tp,tmax,kappa,Sb):
	if(Tp,tmax,kappa)not in _B:
		L=Fraction(1<<122,Tp);lo,hi=1.0,float(tmax- 59)
		for _ in range(50):mid=(lo+hi)/2;lo,hi=(mid,hi)if tail_log2(mid,tmax- 59)<=- 15.5 else(lo,mid)
		q_hi=lo;lo,hi=1.0,q_hi
		for _ in range(40):mid=(lo+hi)/2;lo,hi=(lo,mid)if _lossq(Tp,mid,tmax,kappa,Sb)["P_lower"]>=P_MIN else(mid,hi)
		B=-(-int(hi*L/LANES)//GRAIN)*GRAIN
		while _lossq(Tp,float(B*LANES/L),tmax,kappa,Sb)["P_lower"]<P_MIN:B+=GRAIN
		_B[(Tp,tmax,kappa)]=B
	return _B[(Tp,tmax,kappa)]
def loss(p,rate=1.0):return _lossq(p["Tp"],float(p["Q"]/p["L"]),p["tmax"],p["kappa"],p["Sb"],rate)
class Halt(Exception):pass
class DigestNet:
	def __init__(self,qint):
		assert TAILB;g=Gen(256);E=[[(g.inputs[32*(7-k)+j][0],(qint>>(32*(7-k)+j))&1)for j in range(32)]for k in range(8)];S0=lambda x:_sigma(g,x,2,13,22,False);S1=lambda x:_sigma(g,x,6,11,25,False);mj=lambda a,b,c:[g.XOR(g.AND(g.XOR(a[j],b[j]),g.XOR(b[j],c[j])),b[j])for j in range(32)];ch=lambda e,f,gv:[g.XOR(gv[j],g.AND(e[j],g.XOR(f[j],gv[j])))for j in range(32)];neg=lambda x:[(s[0],s[1]^1)for s in x];bw=[None]*8
		for k in range(8):bw[PERM[k]]=E[k]
		e3,e2,a7,a6,Q,T4,X,Y=bw;a5=g.addm(Q,[ZERO if(QM>>j)&1 else g.AND(a6[j],a7[j])for j in range(32)],neg([g.AND((a6[j][0],a6[j][1]^1),(a7[j][0],a7[j][1]^1))if(QM>>j)&1 else ZERO for j in range(32)]),_constw(1),S0(a6));a4=g.addm(T4,S0(a5),mj(a5,a6,a7));a3=g.addm(e3,neg(a7),_constw(1),S0(a4),mj(a4,a5,a6));a2=g.addm(e2,neg(a6),_constw(1),S0(a3),mj(a3,a4,a5));t1=g.addm(X,[ZERO if(XM>>j)&1 else g.AND(e2[j],e3[j])for j in range(32)],neg([g.AND(e2[j],(e3[j][0],e3[j][1]^1))if(XM>>j)&1 else ZERO for j in range(32)]),_constw((1+K[ROUNDS- 2])&M32),S1(e2));e1=g.add(a5,t1);a1=g.addm(t1,S0(a2),mj(a2,a3,a4));t0=g.addm(Y,S1(e1),ch(e1,e2,e3),_constw(K[ROUNDS- 1]));st=[g.addm(t0,S0(a1),mj(a1,a2,a3)),a1,a2,a3,g.add(a4,t0),e1,e2,e3];cv=[g.addm(w,_constw(v))for w,v in zip(st,IV)];a,b,c,d,e,f,gg,h=cv
		for kw in _KW2:t1=g.addm(h,S1(e),ch(e,f,gg),_constw(kw));t2=g.add(S0(a),mj(a,b,c));a,b,c,d,e,f,gg,h=g.add(t1,t2),a,b,c,g.add(d,t1),e,f,gg
		dw=[g.add(x,y)for x,y in zip(cv,[a,b,c,d,e,f,gg,h])];self.out=[dw[7-i//32][i%32]for i in range(256)];ops,N={"x":"^","a":"&","o":"|"},g.nodes;last,slot,free,src,m={},list(range(257))+[0]*(len(N)- 257),[],[],257
		for k in range(257,len(N)):last[N[k][1]]=last[N[k][2]]=k
		for s in self.out:last[s[0]]=len(N)
		for k in range(257,len(N)):
			o,x,y=N[k];free+=[slot[z]for z in{x,y}if last[z]==k]
			if free:slot[k]=free.pop()
			else:slot[k],m=m,m+1
			src.append("    v[%d] = v[%d] %s v[%d]"%(slot[k],slot[x],ops[o],slot[y]))
			if k not in last:free.append(slot[k])
		self.out=[(slot[s[0]],s[1])for s in self.out];ns,self.fs={},[]
		for i in range(0,len(src),4096):exec(compile("def c(v):"+chr(10)+chr(10).join(src[i:i+4096])+chr(10),"<digest>","exec"),ns);self.fs.append(ns["c"])
		self.nn=m
	def step(self,planes,k=256,a=ALL):
		v=[0]*self.nn;v[1:257]=planes
		for c in self.fs:c(v)
		return[v[s[0]]^(a if s[1]else 0)for s in self.out[:k]]
_DN=[]
def dnet():
	if not _DN:_DN.append(DigestNet(prog().qint))
	return _DN[0]
class Engine:
	def __init__(self,n):self.n,self.pr,self.pin=n,prog(),[0]*n
	def _low(self,o):return digest_of_g(o,self.pr.qint)&((1<<self.n)- 1)
	def step(self,*planes):return dnet().step(list(self.pr.step(*(list(planes)+[0]*(256-len(planes))))))[:self.n]
	def wstep(self,P):n,a,ns=self.n,(1<<256*len(P))- 1,self.pr.ns;W=[sum(q[j]<<256*i for i,q in enumerate(P))for j in range(n)];ns["ALL"]=a;o=dnet().step(self.pr.step(*(W+[0]*(256-n))),n,a);ns["ALL"]=ALL;return[[(x>>256*i)&ALL for x in o]for i in range(len(P))]
	def f2(self,xs):return[self._low(o)for o in packed_f(xs,256,self.pr.qwords)]
	def g_scalar(self,x):return digest_of_state(state_words(words_of(x)))&((1<<self.n)- 1)
def is_dp(x,p):return x&((1<<p["s1"])- 1)==0 and(x>>p["s1"])&((1<<p["W"])- 1)<p["Tp"]
def dp_key(x,p):return(((x>>p["D"])&((1<<p["kb"])- 1))<<p["fb"])|((x>>p["s1"])&((1<<p["fb"])- 1))
def trail_length(p,x,f2):
	for l in range(1,p["capr"]+1):
		x=f2([x])[0]
		if is_dp(x,p):return l
	raise Halt("recovery length")
def recover(p,r,a,b,f2):
	mask=p["N"]- 1
	if a[1]<b[1]:a,b=b,a
	if a[1]>p["capr"]:raise Halt("recovery length")
	xs=[(r+a[0])&mask,(r+b[0])&mask]
	for _ in range(a[1]-b[1]):xs[0]=f2([xs[0]])[0]
	if xs[0]==xs[1]:return None
	for _ in range(b[1]+1):
		ya,yb=f2(xs)
		if ya==yb:
			if p["n"]==256:s0,s1=enc_invert(words_of(f_scalar(xs[0]))),enc_invert(words_of(f_scalar(xs[1])));assert s0==s1==state_words(words_of(xs[0])),"encoding collision is not a state collision"
			return xs[0],xs[1]
		xs=[ya,yb]
	return None
def search(eng,p,r,cnt):
	g,x=_search(eng,p,r,cnt),None
	try:
		while True:x=g.send(x and eng.step(*x))
	except StopIteration as e:return e.value
def _search(eng,p,r,cnt):
	n,mask,pin=p["n"],p["N"]- 1,eng.pin;table,births,ts,nxt=[],[0]*LANES,list(range(LANES)),LANES;planes=pack_lanes([(r+t)&mask for t in ts],n,pin);cnt["inserts"]+=LANES;batches=0
	while batches<p["B"]:
		planes=list((yield planes));batches+=1;cnt["batches"]+=1;hit=stage1(planes,p["s1"],pin)
		while hit:
			cnt["stage1_hits"]+=1
			if cnt["stage1_hits"]>p["e2max"]:raise Halt("stage-1 budget")
			l=(hit&-hit).bit_length()- 1;hit&=hit- 1;x=lane_value(planes,l,pin,n)
			if is_dp(x,p):
				key,length=dp_key(x,p),batches-births[l];cnt["finished"]+=1;w=key+1
				if w in table:
					t0=table.index(w);cnt["recoveries"]+=1;res=recover(p,r,(t0,trail_length(p,(r+t0)&mask,eng.f2)),(ts[l],length),eng.f2)
					if res is None:raise Halt("recovery found no pair")
					return res
				if cnt["finished"]>p["tmax"]:raise Halt("table full")
				assert 0<w<1<<KEYB and ts[l]<p["tmax"]+LANES+p["cmax"];table+=[0]*(ts[l]+1-len(table));table[ts[l]]=w;ts[l],nxt,births[l]=nxt,nxt+1,batches;planes=set_lane(planes,l,(r+ts[l])&mask,pin,n);cnt["inserts"]+=1
		if batches%p["Sb"]==0:
			for l in range(LANES):
				if batches-births[l]>=p["c"]:
					cnt["cut"]+=1
					if cnt["cut"]>p["cmax"]:raise Halt("cut budget")
					ts[l],nxt,births[l]=nxt,nxt+1,batches;planes=set_lane(planes,l,(r+ts[l])&mask,pin,n);cnt["inserts"]+=1
	return None
class Counters(dict):
	def __missing__(self,k):return 0
def derive(seed,tag,bits=256):return int.from_bytes(hashlib.shake_256(("%s/%s"%(seed,tag)).encode()).digest((bits+7)//8),"little")&((1<<bits)- 1)
def attempt(eng,p,seed,tag):
	cnt=Counters()
	try:res=search(eng,p,derive(seed,tag,p["n"]),cnt)
	except Halt as e:cnt["halt"]+=1;res=None
	return res,cnt
N_T3=16;M_T2,B_T2=256,16
def e1_rows(trials):
	eng,p,G,C,R,cur=Engine(N_T3),plan(N_T3),{},{},{},{}
	def adv(i,v):
		try:cur[i]=G[i].send(v);return
		except StopIteration as e:R[i]=e.value
		except Halt:C[i]["halt"]+=1
		del cur[i]
	for i,t in enumerate(trials):C[i]=Counters();G[i]=_search(eng,p,derive(t["seed"],"t",p["n"]),C[i]);adv(i,None)
	while cur:
		ks=list(cur)
		for i,o in zip(ks,eng.wstep([cur[i]for i in ks])):adv(i,o)
	return[e1_obs(R.get(i),C[i])for i in range(len(trials))]
def e1_obs(res,cnt):obs=dict(target_ok=int(res is not None),batches=cnt["batches"],halt=cnt["halt"]);return(None,None,obs)if res is None else(message(res[0]),message(res[1]),obs)
def e2_trial(seed,tr,st):
	src,z=tr%3,[0]*256
	if src==0:xs=[derive(seed,"u%d"%i)for i in range(M_T2)]
	elif src==1:r=derive(seed,"r");xs=[(r+i)&ALL for i in range(M_T2)]
	else:
		xs,cur=[],[derive(seed,"c%d"%l)for l in range(LANES)]
		for _ in range(M_T2//LANES):cur=lanes_of(list(st.step(*pack_lanes(cur,256,st.pin))),256,st.pin);xs+=cur
	digs=[]
	for b in range(M_T2//LANES):digs+=lanes_of(dnet().step(list(st.step(*pack_lanes(xs[b*LANES:(b+1)*LANES],256,st.pin)))),256,z)
	first,pair={},None
	for i,d in enumerate(digs):
		c=d&((1<<B_T2)- 1)
		if c in first and xs[first[c]]!=xs[i]and pair is None:pair=(xs[first[c]],xs[i])
		first.setdefault(c,i)
	obs=dict(source=src,dup_w0=len(digs)-len(first));return(None,None,obs)if pair is None else(message(pair[0]),message(pair[1]),obs)
def serve(req):
	eid,out=req["experiment_id"],[];bounded_check(prog())
	if eid=="bssha-n16":rows=e1_rows(req["trials"])
	elif eid=="proj-k0-w256":st=prog();rows=[e2_trial(t["seed"],t["trial"],st)for t in req["trials"]]
	else:raise ValueError("unknown experiment")
	for t,(a,b,obs)in zip(req["trials"],rows):out.append({"trial":t["trial"],"message_a_hex":a.hex()if a else None,"message_b_hex":b.hex()if b else None,"observations":obs})
	return{"schema_version":1,"trials":out}
def text():return "".join("%s %d %d %d\n"%r for r in prog().recs)
def selftest():
	import random;assert CUT_HALT_ORDER==CMAX+1==8;r=random.Random(3);p=prog();info,h=bounded_check(p);bt=boundary_test(p,plan(256));g,o=_net_u();ref=[];m=_alloc(g,256,{j+1:INREG(j)for j in range(256)},o,[256+i for i in range(256)],range(REGISTERS),ref.append);enc=lambda z:_encode_body([({"^":1,"&":2,"|":3}[a],b,c,d)for a,b,c,d in z]);assert m==0 and enc(ref)==enc(p.recs);assert max(max(x[1:])for x in p.recs)<REGISTERS and all(x[0]in "^&|"for x in p.recs)
	for xs in[[r.getrandbits(256)for _ in range(256)]for _ in range(8)]+[[0]*256,[ALL]*256]:assert lanes_of(list(p.step(*pack_lanes(xs,256,p.pin))),256,p.pin)==[f_scalar(x)^p.qint for x in xs]
	for _ in range(10000):w=[r.getrandbits(32)for _ in range(8)];assert enc_invert(enc_words(w))==state_words(w)
	regs=[0]*REGISTERS
	for j in range(256):regs[INREG(j)]=r.getrandbits(256)
	a=list(regs);assert p.run(0,len(p.recs),regs)==p.kernel;p.fast(a);assert[a[INREG(j)]for j in range(256)]==[regs[INREG(j)]for j in range(256)];cur=[r.getrandbits(256)for _ in range(256)];pl=pack_lanes(cur,256,p.pin)
	for _ in range(4):pl=list(p.step(*pl));cur=[f_scalar(x)^p.qint for x in cur]
	assert lanes_of(pl,256,p.pin)==cur;e=Engine(N_T3);xs=[r.getrandbits(N_T3)for _ in range(256)];pl=pack_lanes(xs,N_T3,e.pin)
	for _ in range(5):pl=list(e.step(*pl));xs=[e.g_scalar(x)for x in xs]
	assert lanes_of(pl,N_T3,e.pin)==xs;xs=[r.getrandbits(256)for _ in range(2)];f=[f_scalar(x)for x in xs];assert packed_f(xs,256)==f==rec().f(xs,False)and packed_f(xs[:1],256)==f[:1];assert rec().f([0,ALL])==[f_scalar(0),f_scalar(ALL)]and packed_f(xs,256,p.qwords)==[x^p.qint for x in f];rows=[r.getrandbits(256)for _ in range(256)];assert transpose(transpose(rows))==rows;assert(transpose(rows)[5]>>9)&1==(rows[9]>>5)&1;xs=[r.getrandbits(256)for _ in range(256)];assert lanes_of(dnet().step(list(p.step(*pack_lanes(xs,256,p.pin)))),256,[0]*256)==[digest_of_state(state_words(words_of(x)))for x in xs];q,found=plan(N_T3),0
	for s in range(6):
		z,_=attempt(e,q,"selftest/%d"%s,"t")
		if z is not None:found+=1;assert z[0]!=z[1]and e.g_scalar(z[0])==e.g_scalar(z[1])
	assert found;print(info,h,bt,p.instr,"ok",True);return True
def print_ledger(lg):
	print({k:(str(v)if isinstance(v,Fraction)else v)for k,v in lg["plan"].items()});print("body",lg["body"])
	for k,v in lg["parts"].items():print(k,v)
	print("N =",lg["total"]);print("time %.5f %.8f"%(log2(lg["total"]/UNIT)+5e-6,log2(lg["total"]/UNIT)))
if __name__=="__main__":
	arg=sys.argv[1]if len(sys.argv)>1 else ""
	if arg=="--selftest":sys.exit(0 if selftest()else 1)
	elif arg=="--ledger":lg=ledger();print_ledger(lg);pr=prog();ph,filt,body,code,tmax=machine_constants(pr);print("audit",ph,filt,body,code,tmax,pr.calls,pr.instr,pr.moves);s1,s2=phase_bytes(code,tmax);offset_raw,selector_raw=search_envelopes();assert OFFSET_SEARCH_PEAK<=s1 and SELECTOR_SEARCH_PEAK<=s1;print("mem",s2,MEM_LIMIT,s1,max(s1,s2),max(s1,s2)<=MEM_LIMIT);print("wasm",STATIC_C_SHA256,STATIC_WASM_SHA256,WASM_EMITTER_INSTR,WASM_RUN_OPERATORS);print("envelopes",offset_raw,selector_raw,SEARCH_EVAL_OPS,OFFSET_SEARCH_EVALS,SELECTOR_SEARCH_EVALS);print("searchmem",OFFSET_SEARCH_PEAK,SELECTOR_SEARCH_PEAK);print("recovery",other_code(pr),packed_ops(),rec().instr,len(rec().init),pr.nregs);print("emitter",bounded_check(pr),"q=%064x"%pr.qint)
	elif arg=="--text":sys.stdout.write(text())
	elif arg=="--gen-c":sys.stdout.write(GEN_C)
	elif arg=="--loss":
		for k,v in loss(plan(256)).items():print(k,v)
	else:json.dump(serve(json.load(sys.stdin)),sys.stdout)
