import sys,json,hashlib;from fractions import Fraction;from math import isqrt,log,log2,log1p,exp,comb;M32=0xFFFFFFFF;ROUNDS=51;UNIT=3820;LANES,ALL=256,(1<<256)-1;GEN_C=__import__('lzma').decompress(__import__('base64').b85decode(b'004jh0RR90|NsC0{{T858!d0jQZrb3P7)k4DI%(Oj+|@K7dSX7T-$63AYF;40PN=F>p5)antOQ#kXMB}a?+8W*2vR99sHDa?1Cu7xanAvsFIdTSPqsfk}8-TKpd6ad&D)-+!{zWG+gHl$j82-N|Ri3N4lFPa$4JKge1Vq{ZDNc-vofJjly813NC(^jkUq{<mSSiZ*-jHE*`KckC3}v$ER-7b>397_4MGy0JyuI+r2^GuG0Nt<ZV_?9<W?nC4A(w=GC#DoLED4^q6Q$me1*LAZK*iCM>fQjLPJB;y4^8!m0%N(**A;w&TUhT+1P$nb!K%RiD<oboGs!>uK2yiumLD2;m(az9Yv}O1i)<wv_;nq(^9T)(#=B06m67h4IusMNa@sG-$GY*NuXe6B6Mc_zM1gP>s#Q+)m>}YBCSS)Nq_1X?W+2Pa~^vziC%6-wAxdc(GjSiu8DUfFfD)h%;3jAHA-;%*mS4Sru4|tv)nt{H=`D7c_8F(@vh}i(7EKxR~b?)vG`Z{3I(FvX#E8XjXtpruAb#pK>Ef^iGGy`X9O|-9g{ipCSLd;ovWq1N5yB08BeLZ1skO*K~e85du$imjegc>5P1~$vrYBtrJ%%lJ252!4AE>k0^i<M^tI9XivmY)@_3yE-z{PnI)R>sz6QxK0zhzB`ZJ0a<mbUNM^Ecxw|ehz91{c!emJlLYn7sbop3@M{BznpCIK|VZ|5JAQAR#^#!HSGQ&@jzZgzXNJ+vDA$Wgo6d@R&Ayj9@U@r4|QCMV&U(xulu^Fq97%-RwrG$!juuXk)1{VzLKlPLGOsAQt9Rbm=KRMOBf(!6@MeJq$xtmrwfJ~>V%Q~7kwts=m{e8H}C(djZzlMdFsoH>E-%5O>9vL@2W!X&#bYnU7p6QeD3y$ZzUxYtn7ox<4Z~#+aa~`QmPuNTanBuVO!(ckXHHNCyF3uPnEUhMgRK5xKYFV%HLw6!O)c`C~@BiZ4&a9-;;2n<C#d!HPRm}zMS?(8RxMqNoAd^B8(2;B_WB^G_UEb}R0sO0IZ0^H`EMLFkAVd|pq9+`U{@&TGymn#mO&czA?2<20p9h_VKdu&KqU?fw>qxFbe>4_h2jO}B<A(dxP<b?^@_Oxn!7*AHfevWY#jqw=z^luqqK}nw3uS`2c*i70OwROuH6?opH28V;s|k4Z*xo1Pnt>mt6trqZMyMiQ8`!aQ0cr8*imkRA4L`Oc>KIVF6-aq6W!;V3Rvga1{W@}t3yH>kF|?yC7@3gtD?zGY$>=#Wq|JQ2aFTX0fq`TO*ZN!aXLBq!6z9;S>KkInuDA#;LIiIyd@K)T&tKL6e~NuwQ5$T*W%k4IfoWtJ=s|>LMp6wQvu}6WP^>vd$I<je^P}n33nNg+0dQzL!FK)KnOBJXa#Zh+ABo|DqM2UD;(F6ItU7iFz>i^uKvLQD(^ol_83clDZIbW2NqFA^m~Af}3K2R!jvs4FUBUqv2<7`G$c_2|uul5w4g>$c5D&)Dx?-7HZCe^_&(F^ZHRt?#V`w~@Pbht0lylB)6xlN>llY&}w7&Q;(shj4?{44f<i5YCg&))w>RqC-15>B3=guCsOJ5MHif87+gYp_*6$>;WO}j#B(FJH*<8iVa#quK9UGYwTL)+Pb4oqID=mf12-XJd+e~a5&eS={v3d=57hola30dPY8wQ7u~FZeO42tyB-`sK*oN>U(U{Ou6$uhk&Yy8XRS30G4!o|`CWUlcdYeRmxt9sGXTRIXVul1uUH5rz?enK<8sPKfnvEG8_6IS+Ld5wFv@y@OQw!4Qp2!jxS$V{L_h9@Tz^)xgaHX&)5(tGIXCPcj+eT_;FqYUQM*5nc)c1v61stM7_>3jhlueaVsfTs45G0Gb3v-~JOW&Gtt_cba&v1(i@2F#$c4Cz?u^il7KlQX?Fo$pVy;5*RqeY^G(ZXmSx2HqMh|hyKYeIIwbH;6tkKM?yNvVhMQI|73xn$D?8^;!wrUzRMGrVd{@4tbRuO=||n0(@#8uY!DaVBB;F5X5-79lxcM=oK*as2f|82*65DVf?7pE&he?2QA&|5epe^FM)zsyI2~PO{PR}B349P0q4;QaQ>)Dq*D|KWsTuQsoDv}@y6Qgp_BG}2gGeuhgDTMWkQ{}sF+#UploK!}Fl<TjhLL8R=5{<Ep{MPD?qma=T8n#qi{RFu%xb>{?37e%0mdZ!eWXk}@^3=5cIKt5P|_!cnE$u#3p7>nFn0(l%r%z|J4go$+DdK%B^mOmlvUljy-1^up`gH13RH`-eB7?&pftUvEQIR2{oU2f)aDto@vF%20S9m;L@Z1+vP#_*VTM+#XpC~LR)W3KtF;X~$|=t``&9pfw61~Ns15zdGq+0FV@r7#rc-<ftX?xXnuejM5+*Cl8Yo3z#}pcoDV*g<W|Z;w?-p?oyPF>wsKQ2;K(vLCdWEE7A<1M7`@iiPA1Ha8{Q(50ASTsV;>IT|T?~8}_KBt}X|AsOed4o!sSpL^8vg*17v(E8wXdA6&pB}r)`#Q0#}w|-^Z=IO2-8!konj`2nIh{aHiB^@F8V!^_58rHypU}^^Cugx4bw=3KjV~9Q%Yrlyj<v>;_AwRo?O!&*Ji&C+NkB<#ljg-@{k^uYU&Ha?@j&N8EOhv=3y)W4$AT>ZE^?z9D}T6kEgI6;1s#&6Ltzy&8l5BCfw%!pKzi$%DkGZO#@w7<7Za3BZ5*2Hf`GT5VQEiBso|$&LbJ>NIm#`j3@LtL%r8iep_*p1f!YH427}l-iQt*M>Bzn#HgN}E;M3Jrp|QcR*vYZAQ5CAxH9We7jheZt>5fzM?owO#o}@#Hb5cX-embZ1h+iPAgyEkReYvdqx*qGgeUIpTqK!=i(?@|ey*`6V2=A}_|bEg%>T@zqX^6T+Ch$u>t{Wb-yO|h75>Lxwt&h;jPvwjYboY|niBACDJ{^Tc%DgdT<|5GXcY(J^et$%@8_Vl*TRt=P7q5VK5qU1YqEdE6pk*|okb%Ag8#r>2;I1m#V_3J0bV!R_`T+$g;DRn$JIp~LmHNOg0;ai8E=k-<lk^-1fmPcJ7Di+eP!L8lULT;HkgGb;w2eH68jFh(Ef`E6|EbeKQ8A*u7J`);2In)3rM{vi{|Lxz>3ul>svjSpfDCCzMB+*>CjS-RgMK?<^EL_Kx4%dyKYDp_n*0j0(z`_h?J$NbXl`<O)DKWCfv_+rW4d0kC%?=V#_8}=Ar$#m6PFXG@&wlSre(Z>5O8|msU$`@wD4G)Jl{{Jk1e1QX-~+gTRwo<sZhqG<wBoZL}B=O>j0kU27p!kVc%EPE6L9_M~Y9FUn0+;iFTpdK;dRL~R*G$KNOYYY&$zdE&0ctH<0zj|~sg)+t{pmQ4wfmiD4+lNR6;s&(LVvCj?$vVuj+V(HaW@3xyU@7Ga;4`_<8AZj!J<ON>n@B;QiW^G#990X#6DB@plEV_yce<qJ4r#zX>Zg}p=zmHoiUy^o%DKl{DQM|&`l@PP+6B*goOQJd8dx|0%x8Lr(g7B(B0tZxM5>62C!StRIK{if2L`M`|S?^Yg78nZ{Oq@Qll>rR1YxNWxX}3RxFAw2=Nb|_i=Bmr<5|B<X6den=??}ah2&n4d6yT&z!2<%8!zwX%c~Xg4CE;<R+D4*T?kmjX>9lFV)phvAe}!AALp^c?XPk@Ao4^nejdT&1@SR7w{2Z|P-7vL77(MTQ+nS&nX#Y_!n2xZ@vZ#kW_X}QEm=)(oSlE!KA=ZbY*ulM)Z~OV(3($~KFO=-6EKG0UPCGfV{NosY3~cTWAoeMr9al2x_!46#%zuFO>lP=s>NZm;fVKxG^5c=zw4G5H>lnMV2ONBZjg^~uZvEkL3#+xkVd~=t>wfZyS5XkkLU7J@F3qEu(mrCe!_CGX`8PU)?aA;pmwo-lQ#EE}DU<h-e8O?ld+KMD@P)*HTr4z28o4r-qM!J;cAtLZiIID?!jF=QE-t-Wl!>~7y!nLPL&!=PCE8iRr;$BrD^zH&mSS>jRtSA8F_NbpooY+f0{@C{G55=_9b0n-q-hCegw!4>V+od})89Os0e3(BQ9Sc{m;@6Vw#t)BAYcJN47uVd0^QWaoX0+dt2G?=w%l{{=XZIVoiHx--SM8c97W_Us!l@mRx}oi0E|fiC=biB3!snctFf2|R&ALtlvF8Nk&YguCkjI{VN~?kv#jdg>gPQBZQlr~A2!r009F+#nCd4l#NMy7uJg47+wcgD$RKOmP$8)5Pl7D<!ZajwDgE<f*3%!ns$_IxlnTk;$^*sl5Dw}E8XEDP<3u=Ar6}Z+wM@nPrq;P{0W`Tj)1UOI$<h!g!K1!ulBl@-9otmb5_ZY636yAYr*lD^Iu!HG|36}jZn<d=tbF!v$E&@f$Do?G2W6y66jp~$^EJ1L;z;Ix(xP0?rF4YFm0q|Irp#e|b;DgEK%nB2pU?8y=;g>^$k|V&YTQ<Whrndi&B9db^Z~wfZt>c(6guQrO+s}fBg+kt&Gh+UED<=YNE+$QWJ)lp?oh{t0@s;qt-Dv6Z>lFu2K~tG!={{>iwP1nf(HW%SsF!3{ZZHNyReo%SU|LVcdH$1+9&iR=MSpVGkvZOO(5xz5eCKcc)xnnmA2#49)dn;8hgO<phxC%cj4R0fyNa-pEW8|obFE5v$6LH2Bw2tVv`4B0dUYjNJB|_S(G6m;qmeXmUkDWvkO<sr&*>FW|Eak84_D1Fod`?wUG{q+0QP?={)k}CY%jZ@09TNZYSxtn<$2d!MJ|sI5m!d%zw1haP`712J(M}tp~(MTKcxx54FwpH{<7ox2;GO`=pZx7+2%o*0r-pe;yET8kR!ka^ASq8Xv{E{5X&6t@`}O7<gX*e1z8%v7@%15l1Q{6e{D7L-^%0*?D)y<dM0)>Y37l9OVtz<6BAg@Wx-X6>rFGVx<{po+r2eE$swN0IC1T*t_{Uf1V^Lqqe4`zskX3U_xfrzHXiHAD97|EEtqQR4>x(78)I+ONZsw*8|%<G5iOuQ#NCxRHmIMp3`vNH2MI%u8;d3Lu`VF<X-yLi*O%hr3M8itsQ>?IKn)?#q9wUnH)J-gw#Xy#gy_u(7^g9t2*6!+FdE1-q3&Iuj}<jAN94KXROtFqqG4FL-@ZzFR1Peq#N)nC$uPxz8xVaJrztgca&G^NwJ$SJ@HyHG?b;O`q9z|AgX#1pg#iozV}kUv00Lj$>ES@z}Qd){B&uA*0rtPC^Rlm@Uto%+zQGG6z6JP$~6~xNE0jnxAM0*8x)p!@dD7Y|0=m2aLI0<4XU8|FRWjhOLR-vfCe6cul3GQ%{jxpqJ?|D!^-qz471diKb)5uS<nhbLI&tFd@+MetSHB6aH9{W?!Mv&4s{{i9)fQ6aE_e|Y2GkK5b3Ev+w6yM>c+I16ce<y%v=1%b#M&YSj5oNL1Df1?)(k-H#`{Wu^~z=JxrH*er<@jv_S+J&`F|z1;uiIt7p4gpH>8PytAqCx|L=;xyma$h^7pz98c!yfQe9DeYsS)DY}@vMT2<b&L|B2(5EwBiw`4NKN?;$S#xWZ{L%1qjUY4`H)R{?mW*RRaPIuRIS<Jh+pp~9p|^zD<bffNUC;Z*3Jx>zL8)o(Ik;Fx#n7Nu+do%j{Uir(+;J1$%2=mfBt%276Lt)fbY03r$frY|m0ozFCjvikE7<q`!lU&EIawS(+47)5_(r!jq$VMZmXKf-QZ>|!(BuP}7Z#4mU$H1mML5dKUa@q&0c*@pCVt`Dd@c$wO|@j(E!eVtD&2o@n95#18W1;Op<9(REu+VbOe`rL_ay@T1*lkM9b_r0fQTa$d#cMvx~{qY^~bYenElT$qiPWeq${UNyz{hz9EJuFOSjgud#M>7eszkB1Pe=4FhE<-GF(5{5aIambHQw<LbXx{HPo4$POO<lXcpS;cTwVIN8b;ck>HBkg~Bw-)2^MV(AbtPUPn^?fj;-6QoPCByitVpI#Ogpf%`^&<RRens#xA@eP;NF9vhT&M^A${J>%vuD9wDtjPe&qL*0)5k0hg`__^_12})kq*-N*aOvLa^^;n)uiY6Qi(F~c^;C>Q(Of@{uL!R^ko$DyXy$_j#KlJ;0fQR=&sZo2XH3tlWYHAxD7{yJXH*z@G-1q&nM53aII`4@yfa)zw6Nw1AX8&O{uM}U(VQ8E0m=fWZ0InX~{VhFHC8+aWiST0&vy}!$GfIha+EkY4-lf_3LOkw%l}X1iSyC6<ZCKW0jNbF9>j3aLb|y)K{^D<I$J1fu8|s#<Z4<|`gB*?vz6Qc!&>6;VY&zmR1(eL))k_Wzcj^H5Wb4p&121G}Rs)}ZKatLHI;S&{PYw2f7D3Q#O}ssJsR!h*fJ^XWQcKUIO0>U#TPIo}@waJ5?Wy6|FdE?}nMU}~>gtxotN~qmr&COz#y=!5ZV*L}>mo_q%@b#R3Lf8&i}t@JZlTLaWg<vs4w%%_^mJQ78}5rzCkS)yaF)#iCUb+0knc67&l^5ffStsn^Dc8)9rj6C7QC!$&(!&qv6=D1wix@|M+PtXVk8YLk0{2nPUdGi%alo?`RG9qYi)7}s?CYe!>oS{#^RAo(0=fs*E4Bn2jd!BveRen@$&_9S7*>!pPNqgHL5<wl@DTRnlN*w3Wf`8+;-QbnO=Wm&g`QlH!hCe<9>+S?X%TwPlp~UQ*y{Dd7ZH)Da=Ii{<WqW$S}I`0WItQo@uSapDkHu>{GlQ5Q$eQlbotjlK{?l=|;(%Xp?NugUYzui0$}uQ~vv}rV?DsMANwpLmZISUBXEzrj^KT_c$+09zFV*#YHj?6G*UCr33_DjisXY5?^wIjO(^@QUMz7E5C9zejN-HSgiQ;q#CdYNeYRfI0NWZZ+?nHz=r{3*DFR8Ys}Na={VyY<U(LyrhhU~GZ!xkpmoA@O}Uhlo55s-`<dYZb~^ki`~6$|&{hmoP)d<C?Q*JY{^Mqns&la1Q)6{VHMOnyF6xnA36;*>%;K_3tZ?_-Rm-~V@V&~hQI+KofTrF*)VQ)h)e<@zSCw%lZpqb$RY`=}4F|$fY65I|5+CI#N)o0$LwH%!1WycUs+;eej2w^-I^*oDARoi~)o%e1I@r2;5n`>ou$J^!1~MNCkiof@jLq@i1iG~0C>!1dN@`xY4#bv`P?^zQOfOvtUB}XwcDilud=EO@%ak=BA8Wg9nv;l=H<Ag}YbMdl(eGeZF-oHJK%+l*F1G7LUs<gZYm&0Y<jkU`!}1&#UZoz9&hB;*$J@`Y6m>Kyp_|yFnPI!{bI0f3c_@VI)qkiVw5`?RD9^zjJ!XT6GEP#N`_tyB)W1NN7N&v+tNDtciTQt-AU!kD)Lx*_su63<+cxEtsCx_)GPd9lnW<=jQQe^=RBUn|o!e{J4;YklKT`(0BK_U7Z7!tuSmaSBgseulq<X}IWfoOZtN+Wya+uQq`a-DV6C0=>(o#;KJGlk`kvYPGi8^X$x_Bw=O-yf;T;``(eb%xRuETHv2puBIdHRWZdETw)?_=Q+iZh!E)T~Z!_WV}#CfA*uRecgdxD!@q&;*$1X|d=4p=!If9ZA8g0~P8+T&Fgn=6L9V&u=KuJgKjEkg9o{<y7w3RK$W;uux9xZ&wSS|0DoFZDa!txOO&Xgjv^vo3Rs=yxc|zYZ)SJ9f$PNrQrw`@F50cJbiM1e)yO`4or-NyzbEnAW6OAg{?56afR)7Q?UU++yk1B-@-InW4=lNDpG*AMXzIKy$(}f?{3R}@w@0k_9?asX2SZ=Rg2tM9TXnNPo%D7H5=D`OcMjgaU?PUmiItjiYVh+39HLT(%nm{ObX#e-XO5=9c>NiC;|Fb9Ukt0o5ctmuGOG0*238&6&TPu@%(2T=aoKThQpQnzhwNex(-n=T7=u%ak>_@Z@_BNn$g2eb7v*al|Tmx6vU@WAQrr@4M4fj?4{$d!0RZGUAXP1n+Gvpf#77{9~QFMEoAv<TvJidC{UK%unyod{7n#OW{ihyUaa9$&N6T~Rza}#HAQ{}T(oTF=ZsRHfc0P_a+lY?Dpe|8#01MbMwT|<p>ols290O%>djd;zoC5Zi~)RL(({~Nl*`c-`ehh|0XZ%xMfNpCBqz1l!k{osutL|7o|pa+;r3zLf{4Cmp^;y_c+xpEko$13&R`cgjkmGYQr*e9wGP+OU_FcmIIkG1kPl^-IKFwhb<R>{svBy1@5fB44#^E=+B*(6HpyL)@&KtDn&sDvq;JkPU{DL5xuwvGM2AOHt%C2j-JU!HtK^yVDs>WcgU~_sPWHi-(Ti5CpOXow(=eVCF@DW8mdLDS{0dIB;DythqGInzGBgKpVtXGqQUp+HVo!0}3UpmS5esiMVvA{AtU)-kvr7T2fs6E<+ME$Bp@%Mzxkpvz$_kv#G3Sy$*pQCPcb?@bBkL2IkQkd}QE0%d?$V6avVDg8Z-!;onz)Ct(}pC>ELuwQvbzA|wS&A)8RdUsCIqMCN7ft<Fsr-cDh--NQLK|0DNlWyUq@z9P!iHpKe5couYss_Mcwjm-a`axv`AbtSz>!S0SLw2akqW=O-XMvEOBZJRD`VaLwFtH(+>M(#p}}14|pRs@uMMV3{U+lqka;VvuuYUEV{c>9;A2ZH2ye7G-lF9V?;#Bi*QGPHAF%r>Ns&}(V+@yRa+mE1QS3k7!SvM@<qnvuBf8HAlSL&A@{bGa>#YOk4)5xh^W?)C>2OFQ4}{Y9dFHJT-{~;{S3bsQ}x6x!vUq4<)`5Ue1d|m$Yy6ZX3-{te!r*SDow^D;`v=C3A`{xWukn%XF7d)Bb~EjZ6uWQUB>NY7RhF$p+d2Xd5%~CvzljXyqo}jES1R^WGJErR&}8YeTrmKueB22o&=c4r~gQYr)M~EnmyL)re#I8a|ts8M!z*ewZ&4ZtDhxkKA1(AF~cl}sY^ldX>=tb1h;(n?%HWF>q!aRVvJKFmI_ZJ>+3n787=5Dp36{VK4mMjk`C~O1I9epb}ea7;+9$YlV2bmRC4vnLySoIoL1{Z#qFJ_8_P*&6w$vI@ZtUXT8?ht{+VGMY`o0;Tj&ycDT($L{{Lp?`qP>9C)<*;5Al<Ib`b*NgaU};kSNy%hPMwx+6T)lLBEO{5seuL0SS_oi=8f<I&j+2IOwv!!a#TJ6>OK-ste&*DWTp<_it#eWXn*Ygr+PdBu)2@g<MTm*$!j8%rqF;K-t_bR6}~<pXSdqIH{{)htr)=yV^t-Dg?p0SEz&%X@Af8X{WH!E_F6y0s@1a?$pxh7*ch7K#q`dF`2~hCqCG0h7}(IoB)b&SX!;^6})%~05l6<x)Ov@^x!RT?)F;8$Q^^=406Q@W_cFnnSR2v-p$dsD4pEfLdZ#op)>YK(q;V&uTkf}#v84FMeCv)Ly}$(Gyb^VJld$%{O0EG*UtUO>e0gJJ>6%5VnLh?=CPnbE08q~E`$}#iUKR;3wo8qqJTNId)Vb&eI1g9i4s%Psx%n9vJGUheb!%V#cyOKxU4t01+!ya#EJG1H~XHFf+d#V$Cq+H`nZ&I+hW&mxzhHVw*%dGxvjU)qj{xtab_~s6IJwd02SrkXf;%PC&)N#e<%}}U2hUVWP6f6W_eZn2+@A`u>5u*E;|2okk4|l{fbL>g3fB<4TR*2ul+IRWGY;HT0d`Emc&g>$nOmH?E+}WR`3x_?yOg|qLQ-9I?KvPU8tLOZ#_7vl?*WQ9n~t%U+7{{LbA0jCG2u<C(5V{4XZ4FKk>L+fAUj}YU{gO@b5X=YL+0}@MI^KQE`6uh{Y8cc3V+AdhFUGB3c_wbk===QlcA~>2%%_?ZbW)_DUcSi#y^uw`_1CP%=pknj4q1Z_dnIvU_nkkSx5Jnza3OkcYk_muV3l^we49+H}~Ga(ErlwS*k#b?S`#O0Nf^a9BEdy%?8p;(1luu(wJO2A01y!c!v-ikuH#XY@meH`ixK2!BKWDy356IGcxn9Wva7P0w=S9el=;7_Ja9)@(X!l4rf&VHtc8^!*hu4%F4(R27heQ{}doOsg*MRgs%uLzURNuUJ`>tHo1UkXn)^+Hd*0H}Zx|gg5oRep%fm*nEAMZxdH4;_cZG6k#>E_@5`ei_vxbBnC&2D6&VAE*5QQZJXI=^T^rs2uDViGl8ln*f}$?;I>DJk*^OhqhU0;jD0zQMo{Lv%5Tb&lWP)lA$crpiRcUHHY8ug>(?Pdiy<!(E^4q7Y|uBcZo*mEov{J9o8#PK9)~a|ns{%Q{LHhY6IH*4abP~Kcj7^|jjM-G7COm}F3LwjWU9JuZx7m|RTN8V{hq+LMaZBR6R%o3_@Uh+P-hcxV)Jv#l&4-(sEW+(Vn66cS1VYzmpmM6BFcLoAE*OTcFky2f66Ab^4K*<fWwB{r?+fRV*bCPN!B{M?08<!o#$1<aD<&3KPFca=F7<=3=hq}wpKa%8RvxDhXRe@==-L^SlG@jWd_5Dz4)a7j$vKizjcP)%CY@}t2eg+5a&35Lft13$V&&*tq-)?vBM~ey*=y@aUpt3kT?=fD?vKT(%7-?{CRRU)=ErfWV_cWxc0xkW8&mOsR;#wTH|8>-omO)o=8tSQmA3Ii(a)Mfh7brz)HGHMm5!_1fS7Youg=l00|5H-n4a(Am|Sj<@JHYyoQt6V<m>M2gbkGZqm$#77GU}34KWn2~}QX+YR4mRfe`_;*GM9^*WhEbavPX@h|?Qd0jik#6ej!=Fh#d=!y>bnFqa1^8+&y?vg-&8Io%rr(S#1^%|lLUwXk{Yzo&OFXIRLQPwV7c5w&UKFKI-Z+*P#Yggmt9qH)(i;Z(w$4uyl`!4?Pm}t~eiahVrM&x3kCdW3kN{>QHWaJijZi28=g90GbWJDFow87)~bk2w8W&%oVTWI0P+V=7*p<NXFOQy*`*#Q`jdcGT_C*AJD9yM0NvYe6)acr%{^ug=u%!7Z-o@}>~kF=zk62X3GK$yV+0qf;hBfUb#yA}L&htTqf!=;A~SRtC;GFM{@MflZ_HhJBi`~EvNx8H#d?QPRlL{f7_+|#|DCnmnh;q!cmoRGl(GZoFOTK3$$5<=);fwj8-81U4yTVHGQ_&BHY6VvNl&dZdl#8$#T5dNnY4J*L;zVY*DpZZtjqu{+^P~A`UVC1fFJ^OQNrv0Dp?+A3aBk1lVzo5e1!I%uzPP5POx}bbEtA7`@)@(^rGINwl{e6Lnx>9<qG*K68_@0rPVS}Im&c@AOJ=GQaZa%x--hn=`^xktDUNX|U!h-guRTKZ_jXeks;lC!ksIH+ltYPVHXUCFC1zz}zo2P=iYz3NXN6Wx9t#+NJlPOE-rYCf0#&t4!{LYVYu{33o%tp;-^0%4Ttad6FGxaRe6^;u@gu!a^)m&DJ??YzPYl~4YRtu)bC%|r|VWo2k5Mf+X^B>awA66>qp8m8{`SF|r4xi3N@nw;z>G+6ys-XG2nP_2VX>++SEIUGYhh?R3>VPpJUsfq~X%<XKm^eDc3pnSjuP_*g%gME=6q{O4RV7~jl0;mKNhSn{l}a;s(bED4O3XvktDbE^eBP&A>6Ei`CB2(WvXY4gTZ?kn)=_d%Xckg$!u{jKQ<knM2jgc?QoiUQ&o&;V_fUF~0p#z7N=fYswuBIT;Gc-*qx1%EqEk_%4`MmoH7vp2`l)W-PJZ?^5lOb*-@CH7OP~mcm%zAp0xf{zOrBlxYGtA?Nc0!7c*KaG8(0AIVfuS*0An&RF-H_ZmIwaIHz5~Rh39h89*S)HS9Ym<pB>@T(cV&g?Q=%_^pI?s%NxQusuI)hfwnUyMG#gpRl*n^`G%)2{~M@+JjiVDTvFb-+PsNhE0$dKtrJzZTm|*^bQM7sh#eH7o3zT$g_jc>-X}KCg)=~p>49DwYJwX3;A}jB!~u<2lZ5zDkaHdA+9;MRElnQ@m8KM;(XU)}$#OS)w#RO8|Mi<p8hH1adPI7(zlYj1))Pf@7v|S>7b<BfzQ?V6`1jcq8LEI#O&mPjC`gCVmx)d3V`Wv-M<~5X97c?aWH6lO5}#nqWrha{MMN%N?1@&nnlsIK^k@2fL38lc7_9e1n2CP+4{P@s^S_}q@<)@O3<jl3x0aA*R@RK=Fc_jl;gvbteg2~bp$*o5NbP-5R$9~a<PwBmL$`*GT>iT~aE^F}6bse;wUVcm;4!j)@B|Nv(Qqz9rJaEN;vmJWSWcHx;m^lyS3=4*+BCFBTS>${Ar#~69eSD01+Msrc^-z=Xvu?dN{bO?2;L(``iba8u29Rkr8e-p>}#d5BV_z7hDv5AWQ+De_Avk-pxr+&CWLQ4nMlVB8J$yBHmPJL(F1M}hf&<Fr#z0d+Q77hh7Y@Ps^vgH{Lk`9VvbU9z_QlQHI1t|Thp*SKE|%DY2-kUKb39)1)5`Z%brFD1I0Q=(5e%PQ&hE!A{@M!no&Paa|!G<YKNkxb1O&DzDQ_*Q*ay>*s#lOSB<2i_lcm6nH%$~$WwC+QEt9U8uF@cQK2L=q$cG;L^XL;x1{j3hYckEhYt=)@caps^K?$wgl(XG9iKX2YJjndyxW!30z-arWG3;g1a5~geO8At|J@ItypsgC%iL)Az~d7(6(rl1ZAMp}Nr2a6hY);eWx%%&1kdqz)4VaFm?Uv!9@!3Y59M{*l!43?ojPW70*L<5!xe3eYUdb34~vH86<}Quv=Cz-iYN!-P<mRi_YD?^i#oBS>CXrAT~eCVuU08Q$He@p);i2*SPGz0Bh;C{0T7DfdC+E_smlm3Qo)D!Ua=9q-MKi%91nJs(m6)3%pS+kdStR>rCkHkY6lodulDj&y|OvK);eV=EkC)sIl&gjX3y(TyWR(67q9BiBUHhiL^VMY<|$@xs-v|#l90S?<^6g0ox%h11-z1iVJWWIO?towuOZw8?}j6`6zd@Se!AV)LL%8id2OpXE7R{9=7C{9A0X2~E@h%FY%XjuO>nEMBfmCSLrC`7hPRgM9YR5VkvRWyM90RlbTj@>aUPJ(RXafinx3uUU24L9Dgy+*%x~SviZNh<rdKijAE~tRTVbD?Zs<DWyKsJXw7nf(iZ)hi%WN83ODRuXdvRbfBefo(^d(i6+l=l>pdUu>QX{7S)hI!k')).decode();_gc=lambda s:tuple(int(x.strip().rstrip("u"),0)for x in GEN_C.split(s+"={")[1].split("}")[0].split(","));IV,K,PERM,_X0,UCD=_gc("IV[8]"),_gc("K[RND]"),_gc("PERM[8]"),_gc("PW[8]"),_gc("UCD[96]");PAD2=bytes([128])+bytes(55)+(512).to_bytes(8,"big");_fn=lambda*xs:(x if callable(x)else x.__getitem__ for x in xs)
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
Ap=1;CIN=1;NTAIL=6 if Ap else 4;QM,XM=0x267df92d,0x695de245;PRE,_Y1,_Y4,_X4=8,8,{},set(range(10,16))
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
Aa,ONE=(0,0),(0,1);_R1=(0,)*76;EXPECTED_EMITTER_INFO=(62908,864,63182,249738,0,0,49405,8212,5291,251700,16384,63182,30336,76,1327);_Y3="6d2e286886cfc4ed9a2ab4d8e63def27f4cb3f7ca2149687585d6139c59b499c";_X3="da38bfcc171fab7f227267b71bf3dd66c96c1567e32873e78db7d81165435227";_V5="63fd8ce7eaaf7af708a0cbe75efea6021a0129854bed95b6213067698182b3bd";_T5=int("dd2d64bc33b582c9835b4f409183c8324b04392a77f1a6270385707a7febef1e",16)
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
	a,b,c,d,e,f,gg,h,AA,hg=st;t1,fg,delta=A3(g,e,f,gg,h,hg,Wd,d);ne=g.add(d,t1,ONE if delta else Aa);ab,mj=[None]*32,[None]*32
	def mb(j):
		ab[j]=g.XOR(a[j],b[j])
		if c[j]==Aa:mj[j]=g.AND(a[j],b[j])
		elif ab[j][0]and AA[j][0]and ab[j][0]!=AA[j][0]and ab[j][1]!=AA[j][1]:mj[j]=g.XOR(g.AND((ab[j][0],ab[j][1]^1),AA[j]),c[j])
		else:mj[j]=g.XOR(g.AND(ab[j],AA[j]),b[j])
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
	if Ap:a6,a7,a8,a9,e6,e7,e8,e9,AA,hg=st;T5,fg,_=A3(g,e6,e7,e8,e9,hg,(_Y0(K[r-6]-1),W[r-6]));e5=g.add(a9,T5,ONE);mj=[g.OR((ab[0],ab[1]^1),a8[j])if(QM>>j)&1 else g.AND(ab,a8[j])for j in range(32)for ab in(g.XOR(a6[j],a7[j]),)];Q=g.add(T5,mj,ONE);T4,fg,_=A3(g,e5,e6,e7,e8,fg,wd(r-5));e4=g.add(a8,T4);e3,fg=_ch3(g,[a7,W[r-4],_R2(g,e4,6,11,25,False)],e7,e4,e5,e6,fg,K[r-4]-2);e2,_=_ch3(g,[W[r-3],a6,_R2(g,e3,6,11,25,False)],e6,e3,e4,e5,fg,K[r-3]-2);X=g.addm(W[r-2],_R2(g,W[r-4],17,19,10,True),e5,[g.OR(e2[j],e4[j])if(XM>>j)&1 else g.AND((e2[j][0],e2[j][1]^1),e4[j])for j in range(32)]);Y_out=g.addm(W[r-1],_R2(g,W[r-3],17,19,10,True),e4);bw=[e3,e2,a7,a6,Q,T4,X,Y_out];out=[bw[PERM[k]]for k in range(8)];assert g.ahi==len(_R1);return g,[t for w in out for t in w]
MAX_NODES=63182;MAX_RECORDS=62925;_Q1=8
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
Au=Fraction(497,1000);Ai=Fraction(15,100000);Ad=1e-6;CMAX=7;CUT_HALT_ORDER=CMAX+1;P_MIN=0.390000001;GRAIN=10**21;STAGE1_PLANES=20;PFP=12;GC=0;GT=3;PM=2;_T4=3;A7=2800;Ah=3800;A8=4200;Ae=1300;_X2=39;_S4=5;_S5=4;_S2=5;Ag=36;HANDLER_CODE,_U5,RECOVERY_CODE=1250,160,94;_X1=864;REGFILE=_X1*32;COUNTERS=16384;PLANE_COPY=LANES*32;ARRAY_BYTES=(2*ROUNDS-16)*32;ARRAYS=0;KEYB=47;GROUP=256;GROUP_BYTES=KEYB*32;assert ARRAY_BYTES<=PLANE_COPY<=COUNTERS;MEM_LIMIT=1<<20;ADVICE=0;KAPPA_256=35;KR=Fraction(62,5);KCHK=8192;A9=80;Af=100;WASM_RUN_OPERATORS=145781757;WASM_OPERATOR_FACTOR=2;WASM_EMITTER_INSTR=10332;_W3,_W2=EXPECTED_EMITTER_INFO[12],EXPECTED_EMITTER_INFO[14];SETUP_FIXED=256*3100+20000;_Z1=64+1+3*192+1000;_W1=40;_V1=28;_S0=_W1+_V1*10+2;_T0=1+2*_S0;SEARCH_EVAL_OPS=1<<48;_U2=_Z1*SEARCH_EVAL_OPS;_Y2=_T0*SEARCH_EVAL_OPS;CFG={16:dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),18:dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),256:dict(s1=20,W=102,kappa=KAPPA_256,Sb=1<<48)}
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
def _T2():Ak=1024;raw=2*160*64*32*13*13*12*Ak;assert 2*raw<SEARCH_EVAL_OPS;assert _Z1==1641 and _S0==322 and _T0==645;return raw,raw
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
