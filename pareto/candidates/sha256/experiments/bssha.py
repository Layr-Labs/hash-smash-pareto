import sys,json,hashlib;from fractions import Fraction;from math import isqrt,log,log2,log1p,exp,comb;M32=0xFFFFFFFF;ROUNDS=44;UNIT=3232;LANES,ALL=256,(1<<256)- 1;GEN_C=__import__('lzma').decompress(__import__('base64').b85decode(b'004jh0RR90|NsC0{{T858!d0jQZrb3P7)k4DI%(Oj+|@K7dSX7T-$63AYF;40PN=F>p5)antOQ#kXMB}a?+8W*2vElME4mfLB`q9?Oz$F9k3e{fzzl-kYic}pWO&Cy1;{Mre{t3E6fbaU9V3{RZF_(<n(s^zCVI56`o7exQv#0s&B>a&N$Bs?yGOY!Sfb`V|f#<TqoA~$5iuA=#@OCaFJqVn3iO6mj0|mR<PiiasMqe>28E#k3D%^b!=EsigI7PL<^&C23tg_Orb;mm*-<Jq;cww$pN>dES&5=PH{IA=D;&vjwnrcSbO^XjL2lHdjkMG8b`;@YWJt2!5a;^Gx4Uaj6-wyNuj(T4-gPa;3upOQ2Q0E=lgtq@Eb+Y7|aC^Ly<rIEP3-CKYV^9$Lv#<Gu9qZhx?4DKCDy}^#ZqJd%b66J~EwXQ9v`pA{b(5ko~#dUX|Xy_8&b3SmF5_*#CTZvjyM7)k>81@iVzzc56Kh(kPyM+G+*)@~ia|gAh$>BAFjTLtUmyJ%Ae`5LKR3!K!8I#xFaBfS*asN?)g{*Xqa31es-4IN4K>plb8lGv9tQ*2q|HRrojCRWYSSqJ=e)RyC!H&q|@e1s#8di1C=Z$m770UrncJR6$=aH>>izp6$%BRC$;Y%|lY|Ac2R}8ifgfYSnaCOi({&Wm#!3&2bmZzj!URyGqJ7|JBC8XA#9LD1cBT){J5&7=rZAPjL8Ao%620c_VW!UIO%d-tZq`t_0Fixe9jEEHMGjtmix9&7}i9Rc*neq)0dxH~?)Bx}IDDeK1CZcVXuBl#pSOGi)3byh&bol&h6liw_!uQnv-Bh?<l}aCNJC4AtGNgSZt<hxfb*wtT_9t3%k?en>Wy+EKtZ8j-!QXk~H3L*vxDeER)#>%<7E7H48+Rak4P+|a*Z#c{B27L8oq-Fn)zOOMIh0U25r>BiTQVwb1%jq0B&2^hyc+mQa$bEeI3fv>vMn=K&2vNl-Khh8R9g+5_x(S?2seOjvf!o3a*?F9uN{r6=EuEj)sw4H^ISxA5Aj{7v5*vTp_&a<ZmJ5c}$#Mq0PAT4qnk?OvQsug%*xDhESHfX9jo45v71?UDzL)@okq+V^5(Fj9#SX^X&F0xB&RLF!_;c2Kek-iSvGE0Rr%$ylmh=2jM$L>_(-qac;&rQkQ;bC1uO_&5r!=8S4I}OpO%VqOOk=i;o@)CO=78~F(R&N^VejuknguM1y>q9raTZUs;4t>!8zjDC}9=?Op5Rs^rV5oqtJ~OXCvGq`{(68*eW0AMTm0jUj`qx}c6w7NiJ+;0|S9HCfB?Tp+iu=H?trug>2l)yn({BbQkkLi3E%4E!Z(uVwW4T5HZ$jBtq)<~-PUsxzu6h%!4pV*W1&rPE<e$L*w*`h3D`5lRfyrqd!%TQ3i127FW+++E?>B$I>VSlAqeRaxrqSHu?+0FNl!2%Sk;d@}92IT0APx7Pch5Ron*0*$DZbrd_o3hSaMlDgyqRW5&s!GtnG<Ew7Rc9uKCWIUjd_*H0geJIz3V=O7xOa-v1ltAHN-;p%iG`l;k8_sr~fZ(t>||1oRSK8*|Rd=LI#=^_n0k}THbm59*DPw&P}oPE|abEaUP&9uD%;argQJSF<96UYK}v|Z9(CjkigO*w|Wz;ga0bO$nshJN;a@Ac}QEbu_qQCJ?4PHv-bRq&{!Ljb*+1;dUtT9<$$4%h}kB3ZjH6|ja2?Y73vj1mrMs@Lfj$pFbO%5ScJXq5ZoMLiE9<o@;oUiy40UDfn<ITz@9PrBCvbyAmWAn-Iy^tJ;*6dns-~%3UrR%aD5M`TyJ+d=w(&G5#%ay$BfBnnmc5#?R`3+p5eRm^jC>rt|$$PY6|8n8>6%BMv(REN8#yO)QS-btKMj45+Y)oCpkTdcN>)O=LOdB58Qf7gI%DyxN^Y_P*2W?o23bPel<%`iItY$Aogs{XSan&P!IYE<2iU1w5^<wVq-EBNk0_9>(okSo$g)bX?wgNW%Z|VDVbS|Vys+`MPEmvw|+fjXjY0dilK*{gy8Z|0k<wwJSC)!3fTTH?+y38k~ezxPB6Q2S)gDN>ZGh45oR>*tnzR&Z!0fOTx=fSDvL`PS9>}b+{O8yli?kvPwdSwRBwjY_A<+{|C25O^BWx4)HH*csH$iMfldfbVC5^o6hv6k{`K%P+cBVdxmvY;8`*^J3t3zvFnAfD0S-o9dg#ljzW5BN(boNV+F^Di9-^>O>m&TX`$01m5FbSXP2Q<<Ip1)Lu+B*LHgT-U)tW5@|I8{IyA=Hx?c)Uk$aBC_$#~b>I~bJb7H3Z<6Wx1S++zX})|wyo**|AwFdPme|3a~!HS{)Z;O-oG>72X$cU+LNvkH%(S+>Q96>1ru5FK+cPZiuC!%SYk`bB_l0oehs$M%?Tc1iHxg+3nA=5;&trQ{SQ_8L7FluyM>PJwm;FOqZae)yr7E&&qMJUH4<)_p5{A!LuXwsd%%j(e=HtF?MIe(RqtHH$vtC=@++`uHMye4apc6ZR}=6q;K!g1p(x`HzWG*tr%Ibedd358tbx>Ibc3k<2;pId4l{aX5`_Gqv$y({6u`Ru4Mm-r99G!9*B}xVpM-6`~Rdnr<;ltf+qX4b*#SDI?J=te*61y7V?-sD&A=q<Uc{52=Y@-E5*ooEz1mqHgez#aFTQKK-|e1x|M@t)$1&c0&_rBAO#cnQ))5u|+;zDZmA+ckXu^*E$jHhWPFl^aA*q(IoC#I?z;}k<icqF*+siM|jRm^s`vE^x<DS3ZLY@OP&0BE>|TAzlHFC?&Y#`9_pslgGm3?w7r#0QGq8#HS_QsY@}nYO^4sYcW4IcM|ykF7ne%3t&Vd=5$lRicgQy^FKKnMGb@pF{$k8jCf<+M(1G-CriXcnoSJ=#VUXXqiKM`RK~F>9X2?VWbfr$+Zw}#Zmpaae>u@;GUs6=MqLH37Ho-r{4r=*<CYZXGGMw}YN%_Ey5-LC_y+rC%Jg>bbB$$h|%1{4E-q0}vXTz~O*D%FBvVnCOfF6EJ1fEP{`&vgTYLXdP62I8$JlL9xr8B80chbGrj$zaT4GN@f=T;SKzKIRX096~UkM}Mrkc9L%tSfI={Bu}P^Ut~Iud3N&L^)RJ@ncld$EYyV>w%ZPAeeq79mOMZg4v#$1`o~xgU4I|o^2i<`ha#qPFowerUS{u<%O~mTnc&vfPe9nBaFpV!c*a)1ozw`$=SX6bxdih7niZqO9N0px3kaBe+i4>_4|m=JIW>M8+|P-RsC7pP~!r#;4&dw!<%bPg=sa_2?ZySVjLl-lLU;3$e1e3Djr?HiRG;+?n^3?71Y+17WD_g-35si&riP4tBB!`LGWfIE918JWIP?+f;uch0;kQu7l16@^{j<WOmY?EQqG5;W6)MB!Hasb7RjaKTI(oc822}gbVE{(q^8Oi?8<a2D|0)2HInJ~YtzmG1jMf4SRA8(b6qW;E2vCQ!|3F@XfNh(u(KuHAcM4!%7Oe}e+;iIVSPwY?PWfWOC_~hef^ws>)_l!9Vy(i%tb$0deL|rVb8@l&b(@oN4G3eO`!P}UXnm02bDDV0W+jlmU6Nhl7DX>|EMA|z<5fHSRi3f_?B6667&b`;HnM*cnchycPZej9jEoiyU=obZA1e!ZhS~8T&yqCullF-V9JV;x`Kq%H#DBO55X|5D8ei=4pRu;LKuyzl^=-j49bxOSQZ_kfA6~iAu$hu9v;eMc=NKj4;2jMz2}z(=+;W{9J$t<=pRAgrTUt@P3=CVfA~P^k^(bEO+k|~xDyF*w2~>KEXhi55QJ2RJA?bjQU>Wxlfm_t-axUjbkD~@+j7{z-d{Z!%(oV-n_(9CTg*hKTS^3<gd>Dn&$SE)#W7Jzc$h~8w!~^1$6sk#ZV5eQ3qKjLSMcH{P(5;MD^?$&5mWLwZr@8-lrz(a@SH4m47P>RXd%%VIUsbNX>&s|bSwQPt*}aSc~*r5C>KZFh}hu4f=wql7iup&`AEjR8%0(H!#+ZfOsH>fB_eHAdHy<Fc4c?O{fRD@WchjpUWAKeBM*T6obVUAl9Y^xQ+KQz;SqAEy9I+b?|U+k+2hG(in16Z*8H?pJsR)?%T@8~d)|!7i!zV#b-yVZh1gKoZN&WsmXMU%A>yb@q_B$-Sy$uBD{VMjKNF<uN1tr`4=JRzK@8+)r~R2@zib$vnp#2nu~(m7QT!{fByTf}NMR~w<hP>kc?&_vkk@A~zO5`^fN^a1CXj*A<Q`)z&A=0x_NERM@jSjCCIHoE%x?#!jH;?dK#z@Z8HBn(aMs6@NDes8(Zxeuj8iC(;te5h2-t`3G`<%$RsEIHuPBM(?~gD^v}|L@e2D}{_<ZeiL~#9dvSdiNBzOu9Gp7jikTE^$i$kKrSM!j>4^vbr_fPAUENRhBpR!80(#5*$r&#bd5ci^#(z5|qmhg%jE|sW{9K~Z3o!43!5VkZ_Kl?7jtKg`k*a!5lT)@_$I%FAcAk;(;jMxNMqRI`#@c1WxW?7-(uUc?Hg5<}D*&dFE$5)yHS@K4@OK~lH4k;*kf(nkk764BN-y+C~#AI|qu?oJSb}*^aq4oW9q|T?buq@>9=|}^iECVPQ575??ml;f>7)h26XQDzSh5Sb(>TPn<5~$n0&pi~t6TpiXoLlpxJ5(4Gm`H^eypDf1DNM?zHS$>muMu^6)+L<$f7ehVE;O=$*pLl#mDL{eOUDP_IFQ(_6)b@_Iyf-)J3d2IHwJSnB_MuFg>C%IwvPuN0@g2q9xa;$fvp55pbpE$BL()pRbf)LGEtX>o>wkRi|`5ueVW<6A;30fgnhvL2tgHjOpr|fZ=6UduB%!ve2o8q68Ef&a;8r;4jZD|1BsZ1f5_ms<K=?AsdTbM)NT8-q(0UET6s3AMbqY-w~J~{idPdP%@xju$D`Pvc9TJ_LeQ^Q?!L!-+m5C(#pjz=%-_`|C2re7VOj?1I-;_oi^Ih(e!C7FiVv&7pU2%5kq~bz0ZsdP-`WgNS7HsZKOg=$Q_Q>!%KrO^RPd$*g1RNNnDDcYJ*!a4W4S=X6F}7N5bx^_-Vi>45VANQP3p6}U$JC#ta|+;HAQ}t*1dzGV5Rvm#U!~@`}C98S*<pQc<ftE_G(IU53mTe83FHxd$h=kmwr@j20CqB{vS>mp4OnPd4U!Nweq$jB2}I2Zkpv?02Yw`y&lMPa&hET94nZ^?`$hVXLd|Y1;w##@hKmodNGp{1q^{HoNfZNKfpvXM*~(oVr1tlqtxey38kOGYFi)G^^9z;pWo{e>ByN8e?Kh|aDq1eOG8J<fW1^9tF9gyev72xoalxm<}nK7tSCrn<Syg(F;|k7Ib|{pJOR}LTYX)pm_3S0pG}aDV#gBlH1d$rw=Rw(H?l#`BEpX=n2})J%nnhXT~FdGMAsB~X`p0>$}R($A^q7H4pz=DDup=wP9YVw31l>rF*6KlkQp1PWtg_lQ(<ui*K52_|01Vgywnh0nPq;5Pa15mMH8M1r9ZVFd^(*VUyMN49USOe^4_r_=@X4Oz{)P~4s=0?ZD*lB*JdsgqfX?3aoXWpP2n?5UA`nqYk-s$nJD#DJOyu?$?R=N8y2M@U@iKCk@OO8H8a<BY3Oe)fjy$cp!#bTUc2r163)Avx^P^QL(d;((bI-bk1qd0Iu#BAC)QlS4H8K-Sj8AuYl{<D9ne!u0SiHI1ba=o@Ma_nKB_F9sLhWzlnQ@3Nj?jUiuK(95FVQSf2%2ii;q_Zq}wXdRT&w%=G=ATnP^<9WB6=Lm{ux<KE&gA-0((;vp9AL#Axe_?QfVw=U*eQ&S%k)#wH1o?=P@-rFo*3{3-nc<uWb`#_r7dddJ`|H*7AiJ?mw28Th!@f@Y_LxC{Y;<c$!3Na><w0Vq}+6em9<HTTZdlW;?DGYgEW(8T?f?v?UiK4`Q~kKcdb!6VV!R!&)*__P$!fJ^mCar9cwR>2X=w<xl@!zSs)_*J*}c&qpIDrUWr-YEymzw80TGdzA?mGrm0QI6H?z4^DEyR@o7fA!M>oC13dWA&?0K2*T^88G~cXUM0@cR=~wth2D=#jxTW`M-=t)7o-#a^hAkZ@%oRVbGgE6^=-lx1`SAc1Hq8>Z*``_H<hG0t|-pWOMBQg}kh_GQ3~VwyC&-RxtRiv^#b)ZY!wkr2@=9$oQHTwU(_2H|*T;SFkGdpk&rLnyQu)ALpU388ow<Q*kK^Mh-spyd~0QskI@{9Vo*-E1WDLM>99;LrHVeHT)Jn9)b1&I({>6`_iMnx^^g1gv<U_jtng+|5rVdb=TmR>ZZ$mwh5=>z7QZ%%<88_#8t-s2I5mY<bVMgF#QN@L?8zuEQr-)WUuoAgnE4Bns+s=7Ma<KThtklw^>&{sKd63R?%emya8UwAyw?>zL{lXXuTunm|2=z)%x7Ef6NA#X^txAsbA!Y<4Y6Di8lQ5CjFOA_a5<O(HFJUk|S3MZ)f?7&vJ;<*=e-ptxS6lQf6zA`}i==7{dZixbs8Kfuf0=URN@TINP3FUwpy{-y+kypDlqU@L&*QwxyLTj~#r4i6<v<T&BYPS6dc_$i2>#x@L^|(vPp*TCNz_7jSoz<Y}sj^&hsxTVZOZX}yJWiLp7z&x1~t!xGH|KfuqKXngD##aGj)$WB?JM+maChm^=X^A`>mlHVi~n9oCYptIa#Z8fJ<rj}m2#T@ui#$x`*lGj&lTYRe|%pR^*3|;XepsBy7An3TyYkGPdJW<kLOR}rg^sUmS)@0A?tzOf*c3^Y<oVS%$o1z66Bd$~%9MX$Vw89~sa0QDy^>W#Uik9W59>Ol8GKurU-ICBNVV#N*BC1LrhHESXWNdvF#bXqXH{Y(fFdN4YPR1ab%K`$naxUyGvEIl+nfnxb3PIVYr0AiV-sVk5mZt_2oPcgtF4mXaW|nL2Y7W>0>r_6|w8h6y9$c35YRza@%8eZ?<o%g2aY%>7=cdNGy4)Ev!C$YRDKqL2%{9@p+t3;Z{rEtxyj3Q~a6|QgzO#m6c$WES&0X!q;)p=06v|HAGJgg|lNeRQgrOnwvRWQy1>1TJL*=~dm%boN;5r?h@Lh)7=hB@t<J!K}fPVSux%0>eCsoy{5vAyCdB(`Ce+~cDHimSL`g1Lplsu#MP!D0T1id$-@)(*EyW?O=S2#mg?*Dl6wiVP{W+~_ne^RF<Sth%CYQwLQAvUA5DTI!EZ@xxX`7Ncb_+}(JA+Vu=1Kg0@piT)yvx9)PUY>aZ-j^v|-g%QBhecfT*{M*KAtCB2=W1+Ih5RwuM!;TXEBtRHf7U=RYT<k-3LV{Cff0UnQ<XUPA(ClY#ltn|l}%dKRu*aKzzhxy-K{;9%j8wZ1FJ1DB5!X5^_@uz!VCEx8jqyq&My25Ux!^Q(nYJ0=!wgM+7XFAQ5vttbOLV64q=|@O*ykQsP-zwnlyOkSq&rxTEz+38s%_wc@XZ58NTiI%wa!GFdI@-iIZDFwj9P-3D%(+HzP-70dAJe#O}#hJ0kte8HNV27ID#yn8ZGyZdBppu({%@TPdt}Q4FwcA0HJ;vS?&^I?#s4#b_09@~S7M_(eOjP$KzACq4)F!^!M3Sn_Vn7ud<gX2TT2fusBzh!6I(ltR!fEB^l-7~aDA6ByAh=VQwN3lyz`l>IefvUQV6-A!weuQ2FUT`hFg=_c5I9a=8g-sjL*?UE%ZVLWtC_}Jitj>K6jV4+9Yj2dnYTu7R4shwKn_EjA#(Zm+oS$|5}n7q{$`|$VFaxso+l3SudrXz>Jucj8+n1~w|a!3(pC8N}MXmTu|#z;sB)ViK24(p<kNEVKYRdVsUJnZe!Ucg9?Q}>{GR*@dbfRKu!t#tz()^^YVo&;4fYKD&xRvz;$quXYECbQ1d<93EoWW9aDEnnP~b_>`n>PRvK_DqtNKzG-wao`;f=q`5!Lsdn;abkRvXao^)2A*JsVX0i*Ied$wBdHSJJw99B)rTTuD0EEphB|qwT4s$fZo?P$L9N<#>kE-S;rDC$=Q>^}xm(`N3A?VkuI_KvQGuAbDG9=+k7dCFqpHr2aeFD$51*y?s}=2yNNs6(47!pZ_4s>k1|mPsg|mAGJU&myma!iTGxg55(XPdkdWmmelju@jwGd?vMvKLoH42QcR?wsO0wb>P`H+Z>h_Qs6KVh-z%qbIaybTY_p~*g6u=f!3++_+6>GPeU!za1YZeToWs|%7Is{mL&p8Vd$8*YC#r%>JwS6;B4NqlMFSXwbl!>}KrzO+Z82!;jkDzhbPY;c5=7H^=u^n|;@dGVNq!r+<%nzPA46SBfBAOvY+=v-;ZP=e;TQcwcdlh#kLJpKdn>|Y+Nqm0O8BBTY!B)aKa4lJeS1P|gTxd@AvQ)}qNowK+#6TXB>XhT@)U0ZXM9d!81dfdNBP=6?z1(P1F^Zus=RzBqrnkM=VJk{(eY0zf+?kRG=QSJ_`)@&ZZuq`wH8nE<turPjc<GB-__KDzUlJAse4k*@Xw{_bpLG;36QhS9}JD{*S|A~)0_Ci+0<EHe@=B>@yUb+w=<I$8$XVgp2Wk@&vS17f&0?f_TlKAk*r<%fmQ>Fgx@+D7~=ouK8AdZBe5Nj<qKfLXDiWAew);91mYX_<hU-=Y_8<{;LE(0eW3HLQBuRhbQyGM~<Azut0--354Za*fX_|2mL)*hNN4<~YunL4`GvFSBxI|92O23vR~n7Qh~B^0IV=9eQ^csMbkTx-lYq<c)5MPFCS(MJxly(Ihm%@`!nj%Ci(%Nk_rZFu*R&8(^LY@RD>tr~7a@!$3Mt~mxd%L@@S<pmEa`~k@0XB(KeGZ(B<{cX}fkG%Ki2<ZI$eEYk!3X4huv9pF$V*|{}y+}k5?bILx098hfirY8)ToZK-%V$ptm!4CZ`WY)vaU?6!rTizK#Pt4|Qvts%cgyMtgNC@Ln#47qc3$Lv<TN73L{{f5ujR{A%<5mqk**V;G$IcItG}Ar7D$=F$-;u5O#@c73HBaXGGoLhC(sci5sPfDKJbmCmRwR8!0v9)CFrPI)GEi|7){M6Bi<lS7ajloP)2X4v4&n+y;%+qx;y0*-z@eCeoD<PM$0)8>}SIkYauCdB#W19Enubsb|>4B@hlBlkEwOassDy7YB&wN!6tB>X~qa1-?dKq8XZ8@jF!kgXu)C+alDQ{x+?!Q6R9?8k<f6-nYJ{9zp-xabVm)m@U;Hl5$yxqhY{dM;YQb1n>ZiOQOm8pg&iI-ym2`mEL&ef7LCz(_TfQ1u=JQnD0?W!@^lpU%nskbV1&qtIsB;^n9r^v6f$HjEgi6O^0JuYahDwz?BdwMYc7AQHxYFW$Q{T5BN*pcww9Js9&$8TE}DLe(#&WnwK|;EW<wawww&<NZ~p{EuK#z298;(8Y7W4&>xkx`O55e`1Oq`kg#fkA$NNr>>8lcsaRk#}z9xc#YFp@4{1X`D=Z|t}2yx(PD2(qitasuXFZghWXq?A8G6%k>CZvyzDe4b2%Irrhh$>rl`^$(zC4~TjRBxrg!DOEtL;Ly;EvFu)Q-F6g^+myPET;Zu{{`Dv=)?vb@0yNomK++yAigwQ7b;jIcbNJ1R(?GBub!=^NW!&G2A4p=De=L(Eeh6#;2j@^>2qK#V)kcEsO)GZPZ&dqW-E^uS;N=U6#nP<-l-EUU>2zwUT7CX+{$F7x0!Xl61eZnk&|co<egT8vm{K+ENNp$+{qshOQAY&fK}3mIC5v(K!|lc;zX}Mg?p)yzcInthD^nbqZzoh%MhqUCC~IMO6g&gPA@+)N(rdGaS88UmXrm(2nTZRv<#9sSWK}Hkjb7bY#60Fy3=<Xv+g=P9sMhgP%uVKN3|R%iZ-Gna$Q0Jv^=wJ%WQ5Z74y9RQ}09nAN_%jW7Az04ztN2EHb!}eCfIeaVYvdo&wR>6#w9*iFs^gg~o)YNXrtrqnvZDRsxz$Rq$&Bx6A=ZVM)LT4oT0f@jqR^6pKSwMvbNmeO6t<%=WPs3lfUh8GI+AFB`R)u{Tmo6ZZl6uO{41f#WypxR~M>wDrm`!57!Br;3vHt*weaLPqy$6#{fVB1;179I=_1xo%8j`+zD-W{No0a{491fu?Us#Q)(?1<c=zo~ax&9IhT7yi9p;$RukubUwPbt)Esu%?E}iM3pC9QTuWr<BLC4Cdo5UF9IG^Gr=4Z@I>aNEkvLWa-}sz<^W$C%4$w~1C+SV;9T%_iLjf1s#Q1ay6W05ZpaR_*VgLA?<@j!#IPjz*DE)-6a)1&ImWE$!nT!8ZDyA<hNY(iSz|MoJmwg>FvoZ<jx1_mGu^)fe0YuO^9`p0++h-Ydvy{RD7(Fe`0!;(J5GMsT|cVkqO<CDjn0g^?IyKL{R0+3jYU%%RiE++UmAdrH!a4F=5<#Qhh`8ckVqJWqHH)6SZl7{9R~V~a;Jtzya>&R7I(@F<e)ib#>5#gR!kGJKvtC4v>P5xI!zi1GR*hQEEol??;zc+8luyt&6}jy%lt#l0|T|<LG0{zhLi})TLaDZF~euol!OR;5JF8via712JYeZ}TeXt@NgCP5-mjziIOHc1u0QNIgeL&74+pVD_S)Eb*J7_xg$m#=>|}v@af{%Av%<0u@0BUun74ZdUVOLI9^IQ{wH~QW0b|^-6p-71vAn*$=0hwlsOE&+VsJ=H9!N)nUM-;)KoTs3m&hr>vr4sql{@y_(u^0@1o$*?$3WiUJdS4CUEl;gw{y957egn7Bqcs;%^`?C5TZSJNnLqqln%ydCVxQezLG`*Uk#I(esb9r7^BN&f8pwGJbGzDz%D;hymb0@k^ffrR|ULs>kL|BKqTBk8^g(=vW~IJTtgdIZ~^;bC$nbVCJsK9%ppNlUGY+`^s+_6uM!m|z!-Yg$G7g;eNTx<M<~`1AWMBRTD3Uu0nTZB1gIk-VQ_^8UPwv=`oJd&Q8xmGb{%yJ`a5hQ(G4(zRKr#s`RK`Tuor8NW9DI_XNw%1PAq9ln0#ILqZh}$+mnrukHktDHBw^JxR!$G<A3C_v&Ne)8+RyYW@#;1!w3Ljg+P7oj3Dw>Pf0;MS_x`1sH_Kw1=*HrLEYp?BiF;>dqVfkdBbkyro~N~Fh=9{K`NtuThMa(WOQ>J;~egy2|mS1aB%CVJUB#UAV4Oqon>QL+uMdYi)X}{MbM>ZXAXsiH`p3mP+hEFLTxmMCGa&U74(G1WbHw})wBcfNTq8X`KL(E&mf@*ylKgB6)-8c3n<;26X!mpEFV*Q&mIf?p$vjOxobB3UOqF<CNB7NPyeoTb-*vBZ2#G`_O6stSnjR{%jrFZw#<0$w}zwT1#kErdw>2q7}VFU4-U{;RwgG~AI4Jw<Zw-}*zTF#FXvaF1ci%l1rhF7D|5O-#tndB1Y);U_{9*d>7hu@!pRt*j#8_0Ws*CB|EycS9<>3npQ|K`U%d%@8zugZ#SR>mMV1}ou}aO|ePik+3vi9vbb+=4<jf<g6{;(Scl9~PKB;iq86&F~4#<peOZSB{^s`3~a&v5Nuc-7uks>0c;0TZeT9oV{&jqX{yBS2CTh-LA)DorlUU=fM2E*)QfIZ-Vr56W#NGoPNNTB~>_44=tU6@Z*-=AS(V!(O^vl2lRF!v;<n^iEOEcAB3$Ip7FH5OT`@ojHBG!lMfLBhn86~#L>h|<}LsRSo#K|RluBf=mc+baapZiyvVh=VLHKSqO+FaMJR-sJVz>2>mptu%78kHB$KsTM_5{J8cj_d1o9^EOAt+=UAUIVB#I!5u%2UUw1RN#^<8o*(~nLmbxq#C}2g;NXRO3vQ}YV~m{%Vi{0(6>Cu!)l8`}{>!c7j3uMs?f!;X7<?PKsha`<?%#P--cmBVR!|v=ULf)MP+|{udB5TVT|FW;1ii;49TsaIz;$N%rH&-t`-KWycEDB64#Ki~;NW}=`-u<~noXjMkZ`l^SIBedFn@uo#Wk#hYn+^9u#*c>>7CVm-0=fdiQZI&eIq5GBx^efjc$bp%Im_^$r++(2X62;YpmFg>dBO=;|p+yPG$%Gnn&)-YifA_-A%UyImk4Q$LlUk6MgUjKK|_OW}vcd9kR`+Nzv7&-aogBXd@aCa0cpV`ya53p3>)gBdW`FhrTF7SX`?3{CmSlLA`1+SMS~%>w&P?3ytrRrRG7P)fJbMHM=z;*-yk<dgTRK_sfR&2jH^>)hi3jj|uEYIoOc<iCw05C-r4CB7HTYn6zh=W1(|hP%V~x7O1BeRtZP|5+9v}R-EV%s=dDcL>1Ct01lV~3!6Q24eNC8+Rg=se>(k7QyYk%#1^ZI%!;<^4KJAafeJx}BGq+yPhP~&BJ!4kw(gb1)f~Bj<|*|tt#dd5VwJqxLV$6D4&)#^0rox}_mmIAyXvOG^6?$!Z%oVznhos3$@s2&Xgh57ir*M7BU-S(zuTn_Pl;|v!?9s0EZAVs5)B+^$lg`$yxdUN>KHNzIB&eGAF(kVw{tbO=$<p42;#DpR!jnWa@Rs#X!o{5$Y8iv(ZO<WEJ$eyep=zp_{65cGQ0T((iM9}2@tmXvefo=lKVj7(hJw02J$y6i$D~c=Mq`=loQmFGyq^&3vv_RW3yMOM1~vAB#A=s0s8zfO`KyR3%6>3Lqc*ZHX$igKm{cZa@LZQd;sni#tm&fTg-P}pQ4iTbFfn4vb<l>gRSyCQrR5b=*V$Dsz`k}|7^1e4b{FE<NlECq?5Sa5)WGo>dCya!GyN(kG!WRZN$YGWVniMZDr@Qm)H6~DNW7bucdbfu=^7U-P^(DCDYa#+STmQtA0vp<Lb~izNCytR~~GqH_IAEp+v#DT6%qTn#!Y^P+>00Pm2#Ps8E8&7EDIZ43L)lF59V(b%k*8T{Vu?HRp1buZ_Srb=3--w!_X%uc5yvGk<vz=UQ!z{<A-hWI#^MYG<}c0e&Hi$0`g~8IlFKuZBaWQ5a%x8vq;nv(Q->sYw_SkeS@!erJ}&lrz8RF}EjzJjQNU&&ig}tH?uVl48VmYr-^fI0Cbg0S?z_k$mOLo0QhJo(O9go8|T89smDi*gOC')).decode();_gc=lambda s:tuple(int(x.strip().rstrip("u"),0)for x in GEN_C.split(s+"={")[1].split("}")[0].split(","));IV,K,PERM,_X0,UCD=_gc("IV[8]"),_gc("K[RND]"),_gc("PERM[8]"),_gc("PW[8]"),_gc("UCD[96]");PAD2=bytes([128])+bytes(55)+(512).to_bytes(8,"big");_fn=lambda*xs:(x if callable(x)else x.__getitem__ for x in xs)
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
Ap=1;CIN=1;NTAIL=6 if Ap else 4;QM,XM=0x4feb2cd1,0x17b4cc0b;PRE,_Y1,_Y4,_X4=8,8,{},set(range(10,16))
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
Aa,ONE=(0,0),(0,1);_R1=(0,)*62;EXPECTED_EMITTER_INFO=(50585,884,50856,201490,0,0,39657,6731,4197,202396,16384,50856,29440,62,1228);_Y3="18052f1604c3c936410de3304e96b60f17afa31a27db28f15d229d6b2c575418";_X3="e83bea6f6bac4202afbc7ebb266163deb57278803cc9f0730a066a8dc669263a";_V5="db996058959355681f5005ec596469545e02bfd1341668a7bdb863eda0fd324c";_T5=int("48e680436fe6c7438d9ff2f78cc2ae4f2d25e035d589506a62ec0e43778f3610",16)
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
def A7(g,A,r1,r2,r3,shift):return[_U4(g,A,r1,r2,r3,shift,j)for j in range(32)]
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
	return g.addm(u,A7(g,e,6,11,25,False),*Wd),fg,0
def _rnd2(g,st,Wd):
	a,b,c,d,e,f,gg,h,prev,hg=st;t1,fg,delta=A3(g,e,f,gg,h,hg,Wd,d);ne=g.add(d,t1,ONE if delta else Aa);ab,mj=[None]*32,[None]*32
	def mb(j):
		ab[j]=g.XOR(a[j],b[j])
		if c[j]==Aa:mj[j]=g.AND(a[j],b[j])
		elif ab[j][0]and prev[j][0]and ab[j][0]!=prev[j][0]and ab[j][1]!=prev[j][1]:mj[j]=g.XOR(g.AND((ab[j][0],ab[j][1]^1),prev[j]),c[j])
		else:mj[j]=g.XOR(g.AND(ab[j],prev[j]),b[j])
		return mj[j]
	if all(x[0]==0 for x in b):
		S0=A7(g,a,2,13,22,False)
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
		if i==21:s0=A7(g,W[6],7,18,3,True);v=sum(s0[b][1]<<b for b in range(32));g.ahi+=1;W[21]=g.add2c(Y[6],s1f(W[19]),(_X0[5]+v-K[14])&M32);return
		if i>=24 and not _R1[g.ahi]:g.ahi+=1;s=g.add3(W[i-16],s0f(W[i-15]),s1f(W[i-2]),0,W[i-7][0]);W[i]=g.add(s,[Aa]+W[i-7][1:]);return
		w_m7=(Y[i-15],_Y0((-K[i-7])&M32))if i in(17,21,22)else((g.split[tuple(W[16])][0],_Y0(g.split[tuple(W[16])][1]))if i==23 else(W[i-7],));W[i]=g.addm(W[i-16],A7(g,W[i-15],7,18,3,True),*w_m7,A7(g,W[i-2],17,19,10,True),_V3=2 if i==23 else None)
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
	if Ap:a6,a7,a8,a9,e6,e7,e8,e9,prev,hg=st;T5,fg,_=A3(g,e6,e7,e8,e9,hg,(_Y0(K[r-6]-1),W[r-6]));e5=g.add(a9,T5,ONE);mj=[g.OR((ab[0],ab[1]^1),a8[j])if(QM>>j)&1 else g.AND(ab,a8[j])for j in range(32)for ab in(g.XOR(a6[j],a7[j]),)];Q=g.add(T5,mj,ONE);T4,fg,_=A3(g,e5,e6,e7,e8,fg,wd(r-5));e4=g.add(a8,T4);e3,fg=_ch3(g,[A7(g,e4,6,11,25,False),a7,W[r-4]],e7,e4,e5,e6,fg,K[r-4]-2);e2,_=_ch3(g,[a6,W[r-3],A7(g,e3,6,11,25,False)],e6,e3,e4,e5,fg,K[r-3]-2);X=g.addm(W[r-2],A7(g,W[r-4],17,19,10,True),e5,[g.OR(e2[j],e4[j])if(XM>>j)&1 else g.AND((e2[j][0],e2[j][1]^1),e4[j])for j in range(32)]);Y_out=g.addm(W[r-1],A7(g,W[r-3],17,19,10,True),e4);bw=[e3,e2,a7,a6,Q,T4,X,Y_out];out=[bw[PERM[k]]for k in range(8)];assert g.ahi==len(_R1);return g,[t for w in out for t in w]
MAX_NODES=50856;MAX_RECORDS=50599;_Q1=8
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
Au=Fraction(497,1000);Ai=Fraction(15,100000);Ad=1e-6;CMAX=7;CUT_HALT_ORDER=CMAX+1;P_MIN=0.390000001;GRAIN=10**21;STAGE1_PLANES=20;PFP=12;GC=0;GT=3;PM=2;_T4=3;HIT_OPS=2800;Ah=3800;CUT_OPS=4200;Ae=1300;_X2=39;_S4=5;_S5=4;_S2=5;Ag=36;HANDLER_CODE,_U5,RECOVERY_CODE=1250,160,94;_X1=884;REGFILE=_X1*32;COUNTERS=16384;PLANE_COPY=LANES*32;ARRAY_BYTES=(2*ROUNDS-16)*32;ARRAYS=0;KEYB=47;GROUP=256;GROUP_BYTES=KEYB*32;assert ARRAY_BYTES<=PLANE_COPY<=COUNTERS;MEM_LIMIT=1<<20;ADVICE=0;KAPPA_256=35;KR=Fraction(62,5);KCHK=8192;CHK_OPS=80;Af=100;WASM_RUN_OPERATORS=115742250;WASM_OPERATOR_FACTOR=2;WASM_EMITTER_INSTR=10331;_W3,_W2=EXPECTED_EMITTER_INFO[12],EXPECTED_EMITTER_INFO[14];SETUP_FIXED=256*3100+20000;_Z1=64+1+3*192+1000;_W1=33;_V1=21;_S0=_W1+_V1*10+2;_T0=1+2*_S0;SEARCH_EVAL_OPS=1<<48;_U2=_Z1*SEARCH_EVAL_OPS;_Y2=_T0*SEARCH_EVAL_OPS;CFG={16:dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),18:dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),256:dict(s1=20,W=102,kappa=KAPPA_256,Sb=1<<48)}
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
def _T2():Ak=1024;raw=2*160*64*32*13*13*12*Ak;assert 2*raw<SEARCH_EVAL_OPS;assert _Z1==1641 and _S0==245 and _T0==491;return raw,raw
def plan(n,kappa=None,Tp=None):
	if n!=256:c=CFG[n];p=A4(n,c["Tp"],c["kappa"],0,c["Sb"]);p["tmax"]=4*(p["Q"]//int(p["L"]))+64;return p
	kappa=kappa or KAPPA_256;tmax=machine_constants()[4]
	if Tp:return A4(256,Tp,kappa,tmax,CFG[256]["Sb"])
	lo,hi=1.0,float(tmax-59)
	for _ in range(60):mid=(lo+hi)/2;lo,hi=(mid,hi)if tail_log2(mid,tmax-59)<=-20 else(lo,mid)
	a,z=1,4097
	while z-a>1:m=(a+z)//2;a,z=(m,z)if _lossq(m,lo,tmax,kappa,CFG[256]["Sb"])["P_lower"]>=P_MIN else(a,m)
	return min((A4(256,t,kappa,tmax,CFG[256]["Sb"])for t in(a,a+1)),key=lambda p:(p["B"],p["Tp"]))
def Ay(p,pk):D=-(-p["cr"]//p["kchk"]);return p["cr"]*(pk+_X2)+p["kchk"]*CHK_OPS+17*D*(pk+_X2)+16*Af+600+len(rec().init)
def ledger(p=None,pr=None):p=p or plan(256);pr=pr or Az();_T2();ph,filt,body,code,_=machine_constants(pr);emitter=WASM_OPERATOR_FACTOR*WASM_RUN_OPERATORS+1;parts=dict(main=body*p["B"],stage1_pass=pbud(p)+GOV,slices=-(-p["B"]//p["Sb"])*Ae,stage1_hits=p["e2max"]*HIT_OPS,events=(p["tmax"]+1)*(Ah+6*(p["tmax"]+LANES+CMAX)),cuts=p["cmax"]*CUT_OPS,recovery=Ay(p,_Q4()),setup=SETUP_FIXED+emitter,offset_search=_U2,selector_search=_Y2);return dict(parts=parts,total=sum(parts.values()),plan=p,body=body,emitter=emitter)
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
		assert Ap;g=Gen(256);E=[[(g.inputs[32*(7-k)+j][0],(qint>>(32*(7-k)+j))&1)for j in range(32)]for k in range(8)];S0=lambda x:A7(g,x,2,13,22,False);S1=lambda x:A7(g,x,6,11,25,False);mj=lambda a,b,c:[g.XOR(g.AND(g.XOR(a[j],b[j]),g.XOR(b[j],c[j])),b[j])for j in range(32)];ch=lambda e,f,gv:[g.XOR(gv[j],g.AND(e[j],g.XOR(f[j],gv[j])))for j in range(32)];neg=lambda x:[(s[0],s[1]^1)for s in x];bw=[None]*8
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
