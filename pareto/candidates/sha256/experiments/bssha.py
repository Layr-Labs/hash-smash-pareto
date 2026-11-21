import sys,json,hashlib;from fractions import Fraction;from math import isqrt,log,log2,log1p,exp,comb;M32=0xFFFFFFFF;ROUNDS=59;UNIT=4492;LANES,ALL=256,(1<<256)-1;GEN_C=__import__('lzma').decompress(__import__('base64').b85decode(b'004jh0RR90|NsC0{{T858!d0jQZrb3P7)k4DI%(Oj+|@K7dSX7T-$63AYF;40PN=F>p5)antOQ#kXMB}a?+8W*2vems-kKHw>7$9P)q7*U{+o=n09`Kz8y4yM$`W|B6y*V7(PZRfD4Gus-|4Q6O3k@fC~+NoO5#04OI8FB<CWKXXZeV*(0~2(Ja8`+kQy87<~bc*nvc`@-FogG~LiJo0%{6v8)zT()E8+;C<|B<ljGP{aya$px@2+zyWAt`QtFE9bwxMH&G2nm;|?j_$<9hUw%LN(oGXtPIqd84#8Sv5<68DjQ-lOk&zp_Bi48@2|rnaq;=J&)#?6foj(bi=I8FdhKfoF=y)wg<Gqo|(#<I%nY!zh2j&%{F(}4nz{19To1~(1v5k}PUB+_zs%KHA`z(O6badtZDwF)B_aF}SA|?JppUOQI-evM&+RDvZJXO_U%Y&%>(+;$l7xW?7%90|ELO@3rTXJ5JO~em|WpNRyWt3pTCf!)MPPHubO_`0{8mz+#Cqy5$wDz9|?Lq@jb|gF6p162i{d<gsm-vMZ`V!6~Za-)D-qnSUk+6osW7~|2XaoS{?Z&(WKzwa~-pes(qKDj(yeE(XRU>6B)<9Z8GU)70oN28QS0S(xh3I94vbF_4WY;8ObUt0G4KmplE~-BP<CLlg->Ub-isjC^9~j$dEBsXpDrGO`?#0|Za}E?=v1yI=OrxN!$KI0!S!;>j=x!**I8$+V!1G6|iEt6=KOHSBPSlT^XxJA_!^IHe6cu!}PxBofkR|98tMTO)Ok-$7=gIbhO`ry$`k?&tJPZ-oyD>+uP0jIECW}Wx=dpfvVj29>O}JIx-4mLZN6&u4Pr>2d2tD$@z+lJ1vI}9R|MT3ME(oeSex&*j04zuzwM$vbu&LV@hiUHM_x#CMa3gxEAU1?lqS_C8-xpQNkw{4u0LM#pI&xDkVL#BNCeN5E)h#tP((GmvkZFr49Z^mc>D>8AS}GbTzYowMRa8$tt$0nuP1Irio9{!m*ZP^STE>b4c|a5+Ti-!Y{e{>Gi+F*BDoTbS5~&Y6I%Qv<I$eX*6YBBy|4EE7I%eA{Hb^fsY9OVVc-MGA3HK!IkoTrxKtC21YB0%8X{ARgv)oYY^g+xIdS`g_V<ztg7+}<^Y~mgRpGsbci*D!xCcY)+XiId?Ze9o&W^I5g3Kf$G{3bLO*8)ywTZ^3`V}C{eTovpOSS_1pp1t^R<`$O>dN93XY6K?q!m&79fT>Gw?|hcz5>8klL56lOg)YfdhQaJ88%V&R)oeQFUU}-LOE`+woat%D5ry3RSqBgFK!)cS2Ob0cM?NZMDZ6RpiTHpA)-G&yYJh+vWbq0|=gP?!Vu|$tPW)s)w=;7jw!c0$6i7;=!xD@d_oB=(^EHqF7241F1fw`22yCOOVzI_>vgaqU#b=`^6_<t(2?gXJ*zcVPB;Qu9=$;*OMzNNUFzv+K)qo+G?i5~6um;1~p4mxBAn(3bS3YbnmfK+{fmOsm4Pt>XLZ94ko_5fD){E_Ser<h8ygkvthjTt+AeLTXebARnYv)0YvEqMDQ;W0h2qP$bPx!-pi)w~cloEEEP#O2~f!cc?rG4Ud$dq+?$M4rjgF@tACFMa9forL7K!fk32tL!jl&NPTItrQ!pAQ~#q2h+&@%lR#Wc|#rd_I+fKlT@m0IchykZ(C}UoAOD)hKe@W1Fg08_u~^V@f>Ema-&Um^RDU0}7@V!JSS=MZ7p%q9mYcSmQlHdLrr@SGMFK7}}==o!I-USeU|%LS><{XZR!uK?4>?D-4eB_rg;&$}TtgAKbvkMfunA<Q*qS18S;sor2UH`H4_7{&<ANJEDI{(spt@2%7*YL&}P)-mfd^42mr#_uIm~R-owa?s-}V8|+LJWq5<0zuq)++E9-RKJ>JCjR{X99i3G+LN4{WiZI6$+bO3%pI$nB{ZHW_V^<XKo<MKsH2nyyA?I*Ty#Y^;TQA98c44Yq@9$;!D!#msjW`=+p<PccF>IP^vE#C%{Xk<ERT7dDt5ohzoaB~H`F7rGG!D9JGH=4}$}Sc6LtwF8w)Y|FmS-q!st!j~26X)h#|-wd*m-bnoK}KKE_QVvi3wcR_gyu5C%U%b7+yCnEd^A0o?@0Ziv5KsoV=K6i<x^Hn2{W27+CFKY~J_^Ypu*838aF%h2S+2RORqgSBT<(XVly<?^|*%@vD9(giW~!+<391ZB(3byC^0td0}2CY?Z8VS6B`&5+97^a~OVjlBY~_=)fV<4>dJCl(lVtqDO-}$tDf7pL_i|F!{%iFNZz+2c%G{<jd5Y$6T$Bpy;ERMr8yCxh@m$K{B0*COThwBEt5X-(mh~%?d)q1PUyN^+038!TePl++4p}IUNfRGam=^sCayN7k@fM$zb*LcRLZ?C`ryDSEU+l#`~B`R)xj-6TP)p#{2PW+bs%o5csCibn;aZbScyAKGZ9#JQIf6b)*g^+%K!892oOO9h@B|tZ!wKV*Mg4b=~)hmfa*!Xi~qk=V-2q;tr2x%VJ|C<sm+RD8jD%s`#RsFZZ0X30TyPd|Bf?7ck-@_8z2ye$;DVv4xfxhs~epO%(#zl=8hgfoHz_Hw5wOY+oyGe_Aa;azJ%<2$^^UkQP8rQ$`Lg-+<Qv_FQr!fv6}1+{GP8_c9hGEslLs&&|d@E%DywnF&eN1iz7Qm(-L6aH4s(x?rWDlpH`oha{5J7K(^K`S;kS%UIS&Pd`@rv7Vh#UDU|3S#J*&u6dsx%LM^Mc!)k1`t#+sEDkOuy*3Sz2dMsguMH{L^jdxQU66WhD?GzbC9noJ3IZ(Hol%<Cbxg5X*Qf0()b4FM@7?>~VEu&s>Bz}L$dC9rlv7+WAhhpa%gVFZRZLci7Ll=nbkB#|-51^H)v*=;yZA5W&O?^I`$#n!p8iayR(O<qvB1Qsi9%Q5lvhJ3QJtcISOz?<65XAOWr*Jkq=It&>6H3s{ekZ;jshP~<;NsI<-ykS5wV$UJJS1{^{Z<SlmIC4K<zyfO)pKDYInG!y~OBBWx#0sRV_zxGT!^5m0`D&(Mu|u;OhKC{d7Kj;OlbgtgB5fZ@1e*pq`&y@2y?~XvbE=fPdE|Dpn&h5fzxMBx$yqeD$pimv=hX9a#|J&W&5QJN_t8a*@-@y3!(Y$|9}PLQJ6}^@YGRXz_Mtr~-BaUi71})U>p+`)mUsI20#xi?1lF!OjsY8c6C(s^#L-Re6NOZAVECl)$L$&Luy%Pgn%JMBKu5-r5DM_j1;>+M+T`#4l~_ifQp>dC)dJET0}heFAz%T4|i6QR(o4^-_$2LF(BZPAhrS7K_SM<ZH+~G~`Yu$0SLKmPx*H-YsW&DV)06<0QhxCrp@SsX9)3`<wG|LrLDV(<@E#xJ-6a9=H8Q`w5ts2ZlehFA}Rl+)ukT=7H`zTaUc!lLCvln4l|?xaj><pLp)fih^}$8SZ&lf9!d6`Vb5ft9m?`_QsWuqj@1m2ri#5<LxlWpkC6(eb|bW`jQ@Nm3ExAa4?I%b4z90D*21{k;#&$SX9hmtD^T!=?f{5Pgwv28xZu`T&VJw6=C|p?=?8w%70mIrED101BF+LYL@(y_N>Np-Eq{R9|Ekd2e~xXn=R@Sn=?}Bkh5bo{KqQs-D6&VxDg<ERg22Xc7{pyh|m|*NGa{UtRjUd0YZI^5cnpFe?VV`$$j_q(Nt$TxUJr=DkIKAvcg=EiZJjQ@ZNwSEZPH0o;9kJ94!%e>+v|%sMN38mSGq}eurjMO*bE){f!(=DeX&Wa(}};3rwvXumG5C9G?KEsqY!knV>}IbuKt~!!m4Z__-DHq*`hL_r*b#Ja*faS9KcDR=k+EY-;yBmcBDBjIik!hy%7`BT5q=9fsdWd!k4eUXQ$KoUb4q$N>%d2fwR>_S^331N#Yp6Wh8W9E$+;bLiaSX2nPm^#{~+mV+w{t@s#!{oi4Yu<tdoL*dy`v@6qEs2mRn(Eq*AFyXJVEV6CQ#!^(FSJjtOnLE^Na+AHUVY5z830vxsS=)ZA2kG17WAiS>PcM+n)$QG|QEr0H<~)X@z_P#NChX00);k=k73IPSCA2b?!1L#jV$#rXFO2NF7ST3;aQTH)e*Kt86^r~8FZosNO#_nWVs?@$lNEGM&nHc5`JFtY!h^0URp5a#ek03{U*5Kvo4x`>bP}2><SWmZ8Tzq!q2=L-<)@kR50R&XxWZ)Lum<-6^b!|ZFrIT357BeDANF<G_FCyOiTCibe8qU)Yh#9dC>bH2&*5cW0B|fW7sldu%9qSY$qM(6?+CsAMfR^UA!bYTedHFkF4m3T|8s_B(RTgxv2gu}G#DVA$1$<$D_eU$^8im$ZfX*>N-FPWqc{CXT*@h8A*7PWCs4>|%U)-VUG5wmzpfT{{iZ-W{;Q;40MYDf8@mEWRXt?NF-;oY+I&UEh?wC=TNmP)!1;Jlv=-zAW42sw^TxPD%}LqC<znznLPKs<^U&kExeE2IIma7Mrh36{k4aa7$LEC4m>f;YMTRl87i*-|$!Hpj(NX*XJNDjRg8F~-3_%0B`xP0u|0uvgE_%<1-`)GkRFC_RYp1WgRr&htK{9Cr)NU=3Oz}3-sIGR7POYPLLm=52j-ko+$O<!gC<i2e>}Wl!D*)8@Et|+eh=@cHh}DM@Bm9C^#adPV+11$w8PeJ=v(x!zC>#m5tlZ?0;TT2<Gti_ux;g&db5L!J{>|}&r-T~ETIDFal*2*d1i3~{ZXu`^dLdEaDaD{xL(mIj^Uld_U4`#;0xR+9?B-{tGrfMjEM=;pft}{(^+;6Ml?v|(TdLNqxiEP=AzHr0(cpBf|Id$77HkU_w*&R^b{*g|7XNI>NR(Ev8LP-rJOujChqe3WX5xqW?-TC_gatAOW0DoD(-bl)I7W5o)w@*8{t<nEjpTG6R*qBMdJ|)Ri!8SsL+?Rvnk&gW0b`E9!&9mI>^Ad!Ns+;9Q^RIs<s^&e>l0K#^rB>Q9le}dalVB`^OYX}@?Zr!(eUct6l1f9!>ry+ZL+|c3m=uo4?dSy@D&SUCDq*d414_KD+>8CYi8y-xVo+;QQR%~c&0lGp0HdCQb&jb%Loy5Fj%pqq_%xs&J6YmL$Yy`oOdg|#^qg|?KyFGZs?jVcrE`}@9zCPiXaGAJ<>B^IlDDP9O8N09;IHDXXFq*P@ZU06dK2$)eTG`8;?hV26?)4UU<aF#tj3*@{m9I^y6SDkWO_-`*q~Y5Dr~ihKvIy0*Zucou@~vrRmiRYz0?rasmx3flqDGd>dGV%(p4!Zw^X3zUY}7$Nbi}`>kYn4)x`s#sO*Z)`g|YF}Pf65K{tqLH8@_8{8M$TG{7lla|$&Ulx7t$mdM^!e`aF?FC;*8Kf!Q_(vLdz{3>;)Bo&aUzP)q|I38X0uy06M0|4U5(YnCNiYyrq(FuUgC~J)12|(2&}7@7mxZ_pYKJ}aUyJzZuh%v@scWn3Dz};C6f9r+u&1*0_YoBnH54)Yt`g$3z4sNbnnk+<hWiIju*Nd>Jt*y)Y6s^DvE7HTck0M!47lJz?h_*<oK+BBj3#mr>->SOXzByKImnCkz7)qA(=gyh#UG|LdTZgelCB-u0mZb>gV2cBR$xoHLZ5pdpP603SJ<eYz22&l<8RLL|LkS^mFFuN$n+fb2xJy5G@`up<Fuq}uieC^8UJK7OLuGFQx<D^XR(b}U_e{A-hHNV+C7}SW`fj3;n_41F3nJtLEH(PIC>+87nUw!*v-Qt8-Z{*zHi6Cg$24%a{L(Ar1yHU1;*SMsKH%kLK-JarbYExp(#8yBfmLX?#d}8U(>?BtM<w=vsS}7UE&pIW?Wt__o=BD(+)W9iknnX(cBG4o&C2Sz1ah`E@zL6HC4BV_LM@ljSND}@a>bj`z6)a_(stjaN0|xxb&61!4V@IoOjk!P<d28^&YVjnYP$8yDw*4T1L{kr$>!i_T&;su$3!JK$U~nhwaR#N{!6YD9U=kd&*ot7cqT}!YMzqDIxAo@xel&yga|uyNM=CVRhPCCd2ghTkK||1HW2^(b}gfCCV&l>gyodI@M4XLCBm{T(=u4)=bU4rzxr=K5;XYs??sf0Mki4v|Ig_%>vO_k`lF*ad_IOLO)$J_S#PW5U2%cn;1@}2!A@hO?fA>$hz8yr%R_(g9o@OG9M$W>I?R7IZu~c37Vt(_&7`ULUVNRm4J)pe4}A#odl&KA!;OVfc_aHL933mQ2SSW9yA~$lix1E(Em~g5LDh+;Tfn+gziUU@%~*K4CSuIihUSA(Z1ogz07QFv~Ep{<K^PJ@#Cfy$hQj%``4>Uk(*-v-Ftxw@BoFkJpRE#vn^s(#jcFy#>s{;Xq0+GEE{dlRt@~HnL-U8hqOZOT4~zD)%ORu#$n5WaPO-P|5uljjay|*v4vjXDJ+f@qU=7kK4>g)uvqCSagFj;-fE%P4OMS-?jeXJ{tXjltT9lt+A_cx96^KeFEr*WS^z2DkRZ;tPeIWQ?xuf&iEmmMkL*o|Qfgu2HqKFP^nxZv2_scqnXc#)$PJzCF8F>xYLv0be8Xh~j8Y3dx=xXOG>hXk$vqD!RRJB1Ylkwdh|+l}8-YQ&>mI2H)o2x4HtsJN0|zh0YN+a?0q9HzC0H1}1DlweJcS2kWPoZ}Rqh=9$?3Ue;B>aNqEIeJ0Jlx{SUV`m3&n!X$`BlFR7<8XN+>F)E4`;JYSqdWt4yPBnMS7*fvHSL$etBN&c3zH%X<kq^UVLtL%coPDe@eD5pIlBXZQ)5=AIX1KMlO2eM}5z;+scOH*euECHci~j&Dvh{~(h8N{ZX;C_&736xMJS+?$#CjLL*(ydnSGyuTDMAG04Ce)>3e1h3;n68jc4&&Uw1F)J)vaX!#f!DjU?bXl@r-}=zlb9MQoySX=bdo`2-BI#e~*^&AI=M3XHt-sFO*cSKo(A_O}m5^8#8qI%HZmPH?jOM*p-k270xs_md>R6ia?14j^rvq&_YyMt!Zgs~;di{T{pB?xU_M2SE`y@%QX?R9^{$eE&>Ves&%<0>t7xkJdF{E&z5{3bg!_iKBh^CQAqR493A0rzDbTt*m-<LgnZ{}q3PGQijP9mc_#@`yp{epNDt_E$&WK|XrTB2=zC(22sfM2tiZB`9cPXo)ECmwEs@i*O-{b<*Em*ZpxhQ327Abi>Q!+6>MuqNhWgqv?z-~t>oXDO6aO;ASA3}UIr@aD1&@n@K$?3=>kczYee#@#MhyUK(+Bj<9_C^RhgXXDJi97jawF$mN!%Efvl*R<*QhcS>pwf>OdNKKnw=C@N}RV#EPYq;-Z1HgVWa6ax=v%qrclAh9s<Fybe&A<J7ocmLkLcM~}SRH?91v}Ld-7*-?VLk>I6yjr!ZS5FeCc11g{d8eIxgo>+=AS@~OWLYXpT)mIwG5!$Q(!7bjE;h+hd!!V`PUYu6DO9eoW|!@2kdrhhvdSusC8)c;vW9lzbg7>)^Q0cX!*JMX!<vqMU@df*&g9BWl~lA%>NtQD21?La_QcKz$->%n_2KQs{KG-0CCstdhwjs05_#V3N!HigOi#H3gMdoj?218XxqxnC)J}622uQi+exzWR;nE%JGH{PbrTOMX2U91N#CBa6VB9<zLUk8fXAVNsmL73w@zqow?*H^u-|?rdG_vwuLj;|HX)lMV7w$&8GtJ}c4Z$y&cW75A27v*;=i7E`!!^c{21puj_B{{Hw`{;D(Va3Y(pI9dTI3F;4)*Jh|l|8qVCs;SAU9?kFc!;#MWApUpv!xnR@RTN0xzFz^}0F#V{8xRGi(EQhepU5~b)P8gRbP5=ixe?~k4zu&H}6I{vi^HzSrltRVkz0CsC72|4xqjjT~Q0uybsvP2f4{j(wuh_0}a5sc2Ml*t`aiZVTq%bs2fFT}S`t*NA{+hF}k%vZk}ux3CSA)HinMMWkE{75A^1$(W;1!ute5ZOBJQs&cw^x@~Z2;4#Xj$t)=t+(jRkXPLif5(qyVMkVpcAq#52pQoq-1ix8yq8SL3z(RwO6oSYgW)fzUnX|vYIJc5tmoh?)Te71PsFT%+NNN5VqkYpJEGv027=X%)wC3=akD@+nkbfx#S>i#6dyAUuSf-bJydab%8pzLoNC&rKJxQOM=ZH`YNF{8$QGeL33lZY`>3*j9i<J|o13?<nPm-H8)m2RyRZz)GkkIhN8o5R$#FT@x^gerwKnPYx9*!D04XrlVHLdec=?gYO{p{nIU==CMLJMOfbFtMzU<oaxaud)ARy#`Xlo!Kc1A)Ll>jo-LV({H=?RSQ*Xr8s=&3A7hizNjm+DAY8o!S<`(U7H2gfJn<fd2jZ0;L5Q@BkjbD)4?{F9mTPm-Pu<yFznD~x#~L%>pBiIbd<4u6dnR<T_U4mKOi3!uE08xx4>_w~;0dwFZ9ZCHCCJ_gd0$*8;ZaASFm%_@g%>$<$Nf{u9F8)brtao`y@&?jafx*xF#zSs~M(tA}BFofjLOyR=|oGDCwc%mIN$&B5jTSBJy?Bi1?>vmB`hrYn_;;J~!KM_g@R9VC@m7lwdreYTSEUi=3r^sXj==^>0!MsNc#Nxn$TCqVncHdK1{!^ANrOkxG>U6Acu4&RZLDIj|43yKgoWBPw5k~27EExl!A^gGCjkw5Ij$YFs-yR~NJCEXD2C(ejak+!;9(hj6=IAv9)_Zh9ataon9jBK3IVv|)hGIszzC$~lsHo0Hu-cW0l@!5HQMM=f33$1c2+N3w^V{o2R#A`s3%n|4KRA7e1_GP94%<bT2!zeR&b><*O3;r3``pcM5Xx0s^RPWrsZ9MLy9AVq!MRYtB9HXgWP3WckfhQ+!wS7V3O)1J5}tyusZ}zLXG@W!&{055;CudvN(ZKVsdtibFXFa`poTZ+P4d-uME<?XaaQ~uCI3`^?p#S?xHVN__ixOiVxbULzl#j`F5L!$rHX*9yYU60R(1w2lPA?+(N^APB7L_N{*E9iIIjTT`i`v8WwbQyrh~60({>D^P3G&CLx6TV^L*@?9H(>wZq@Dz^4CXSHXg3qcnZ25&{z>R&Q$BN2?_g(8|<S*$bL%pK@S6GyqhlVL@N_RKRMZER4q&IW3Nj^Qo!0)nG^C#kpKn@&No4Gos>mWehjmd%)IgJb~%lVGnPf4em`+Z=qq~x-t8SQ5(23=ArY&RF*xz>qfE4wFATrCLT%<u&yM7Ck&#qrD{e>Z`EP~q_1ZJ+NpNhE3}dQ$*($a;NITb%`k2^?Ud&bk2nl7`-X3MElY5!qIPf^eoBC~y<TEMyh8oeq0k7{)jWJ{pvGm>v3C0SycGU)popF_bbF$?U5QB#|Y^pe;21&Q5c1TEOw(CY}RG1O`Z;<v}G>zcP`ZTJC3^SX8ZHoPcTBRWn%J9nzsXfjOE-8W2F=ISF2D^l}+sx!6bg~Roc|S%QqWt0+yWj<GFFNKMBu)D@<K#_EAY}OgD^QY%)zdDvtHQ-3jlPe<=zVI{riggj5kHr!^HF-1W=>|zRNh!C7$6jO{H$!&tzZQ8z9F?oUgexJPZcX`kQ(VU_7niPHbR=g4`3qQ%XaU~&$j}|tHVZxG_0)mT1XsouVK<=oT;A|ikT>X{_`~O;%?4CAiUoIhOpg<EMP$f@hjB>^fHpuj4h)df&eji>s|PQm;oLe3#-DfYqCvB$=qKEmFBMalDx0rIXv!WXE;4#l0#rgTdz9xbd1tce?Gll5}d~pw*Ei0`l$w*NIHm%Xt$RUU{oK0`FB+ss)QExasoC*5I@uJ=@_3)-OSZzpDI%cm0A{<FS<(MQ}0GH_z;h~7IL6=+#Z_37nbVh9OFs*b5z_ZKP|VIVBdGcPW`*KV80m8(=sIY`>^h6HQd2+SPA(~yVJ>YuKOKyr_|9IYT*EKYy-f(_To7Q3}ZFSy{hVWj*sz=&Z+ItJr*`W4ZyYPqg4kzclo`TDLCR33%r>7(qAk00pA@8!`tTR-T7YURlkldSYpSH7n`O~ymX#>vK#HF=wkrikijYW$sMbriUiX{BQOh-5{z*TX}sr7LyM_F(b|_Wnj7r;F2i@Jx>W!J{09|3n;b{g>@Q=UBqWbcDY+Y$s~R0OPoPW-@NfHhtHjt|K=k^?ltksd)s9J=Fm~oI!0boqt57(>&>56<|0jhXNn;-=`w)hmvh?wOmiJ|)aN`n3T6sjyNzZD$137Q(?sR$dX{e8~;!1FXSs@K&anVf~V+g?y2Q8*kP9sk$R?=6Qss9DpcMt;Kd)Tt^&@v}5aZ0zmy}^ElhErlLt%E<*3-~SfEeNx>{VZiQToIx>%Q;TM8F8Sc7Zu6poHP93DMK@`+Fj7B{N{*qWa2S>Iv6@>DV)CPM7GcN&p0Hhv6ok$Nkkwb0H}jDdEvcU7Ko)WgA)$b_THq{H<98%hqvUGQ=wgUedyzoY^L?qa5V`;mTK_n(v&!><RCn(_?^`-)Dm)~&9%872PLAzOoQ$TWY2cS#!VPa^bF(2`>Wk1mgTvhegosKw~&qZN85=3XK$DL+m}Y6yDA-1(5Zg02aNtvK=}}nZK@QR(~F<%N2P%YsFP_>W*ECRbd0--grfCQdq1?Fdm>XCg&6Z+YDmoj1$H>Pt{Fjb3rs|e$r^{8v`dA;Z%Fd?I0wbygwdmaV>_cB3?Fm;(C@OkkK_A!_gC38lm}qu{&)Q3G;wcJ$JoVT6W|Y;TKqZ^3Ae;_IegVAD{jWC39`~Ql_#S%1iSdBns0B(SBJqDzQcY8QssULLkei-<u$etXzEYuOIV9*okk+M2UZ*P-}!JSo03nRYL39B%L%(&v6+}2u=qJXq}6es;qi<ZmoE-+-qp!foukp%V@@P(hfx79;l~dyKo)MZ@G&&QlJQmN1o`3L8SCjZOArF&UakiGMQrD;Ht<mcG5tb`Rq8X_wbNe;<3eMwwl)Z94?}|;ha=s+7_&m6o=pJ4Qso-Yr3ba95G0h8Y9K7YaVPLtj77`R_}qYTRu2Ve17lIl6Ti^}ee$cFPPbKmVL(wR-t5^@vpbry`*9oZ`%{DJiE-p)J&UDLlwru?!7aj6N6oiWmx0f1jBArU1T@n;gtRSzw-bUrH`v6^ud`bcEEQL;g4YqLiPOLMu?kbY1I-+f>@+*NkrukPZoxY>1e_C&Z~+M1m~f|+5{R^oC*b$>nmaxo;<m+fALM4+3}iIc{!3)<{Wq?-hk89`!@1nPkv{#F%2d)$#~YcWKsob|UJ+~x-32FGqw%~S$^<A7Yx90>fz44!G(QA7CYN{$5r29RLHG}Ng~L?Vm3`0P32aA8zo8#<eym?<LQ1mx6QDCS9?%VZ@TYg%r&`1gAV2@I40fz#__6s$&Wet7(5!nD(gE^K%6+%~jnPhlP?UQD_AlAkwmi_NWU9L5L%%JuxvUQ^ffMRE<a}eS3Hz7vBlfFr8iJ8DuJPsA9M*9b$jR_E^~(ETl)`qjM*l+k@{fF1_atCMw@mcT^zH!~+jo(?MKlfRfLA5_8t^T89M71Nu_m7n*5NO_AxAnMH1}?l_dW4#5@&+FPJG4{vuCeUf*fynjz7PKk&WW&0sqm;;ji^se1M_!5OQR<-S0qbdF34u_iVMe(~P(!nSVri-%CbJti8586iA{7z-2@XB&Z+i3G<FJ?sy)Ei5L43&X%G>kRU8K9`-Zhq8M-|lY0NXlHZMrK)<JBklg&j5;Z70@%+^55H;C-4icO)bguRZ+cb;yWHwyjg@W%LwVlvQ1KP`6<W@bR6~?)M5%OgSD;@fj80{yLN|aV{4ue*ovqHwEIe&u@e~;Fwp0!c1f6=7ro0|DeP=&D?wQ1tp=3-%h_IP08(SE<{;~Jh9+#EVn_j%s%115MjH^=&1nZ13|`U-hX4He$+rULx6C@9Djj%$EzG3ipMy3cb<dO{eBCVOW{(ns7u+I%+kdX9zt)F%0aARWY?S~HZ+pi=P*{3=oPD5{=m+a7V7Vz$c}$k=NwAlMY_u*6k638|ZkX%bzn4t+S`bp#vAOTH<J9n7^_M#K}9_{*tSEm&PG(!;`{mNTz+?b{XsGK!9x5sck7(lXPe66T@XGjTJwXR5x5+zfJSDm&#P!}Lpzbj;}3L8<v$OZ3ZIQ_KpEM3&0Nudc7eeH1RxNUFpk;5#bV#;c836qdUPI=y64_h@0SKsFR?1Z+*5O8(Csu<*Lp*pdQ9>73D%WjInfrPFDErtI1&IX>2)MUGdWShp76m~o|0!G<qTP>uRUOpMP$<?mDlqd5gy>fFFAOt_;EXQatKrE8%CHrSuViGPIC@kgVsC{|TS1QON(ykV91<%ME;?PIt$8OpZOAR83*W9zJR9~!=jQaw{tOuZ|8XmCRPva2y<o?tbc%+C6T-X5s0rmcX5qICwPs}Gya=M3#b+1!Lex`c$OGyNP#G&-0vjbxkGl79;GM+T3|y(}A6>AiY<>gu9LHf1qI6^etqhbKlGWa!NH@91QZsCgru6|!Pj2b$x64L&12>yo(Zq|`R6PA*5`S9;m<5l2csHjZkog{-D8XayTSVPukv;%epFymhdhQ33#W>*L9FeO%gr@O$(mA4YwMvu__*Azg;v@hteEP#8M&=3_FLHt7`9+q|mp%M!oKrsDo$lWfJLZF6ycJ<m(Va$e?b#tr=WN>|&SqL9LzPv_zyp|1l*d!H!Jq=$2zlvpkM0!M<s2r2tjBzZrNw2~tAQ<F*dbouhVv~4Tbf;9uryCJ}m8U~kB&Wk0XG@j&Qz~c6>ven!H(7Kx3o|3-fKt6|Zd_=t;w8#p}7uhFAaOgmh<2jkrB=)049Nav>Fci`KqOG-`7e%-<!}?w9I2u;9j=#QMI<i7feDssXMo{}S6cyP%>Pn5xa^@y1blJSsGwf(x2{PgYV2`Q708>6U1qH?I86$DGmbS-_WW+j^j`=!&2X>Q2HqJN%s|E~eu~J=KAV32ZQ<P~!pixXI!#OJT#X7`aHq+2qHcnw8dH<_}_@f216tQU>9oaJtYKk|4_kR&R16&+<y0>@!t`ssA9K)M@jGMTQ*gTIG@IhyR_kAq!C)ubEC;O*ob&)Ju_DL~dghv*F!k|oY^}+9o({I7IufgpMzxqpxSDPrE2w4V)tv`M1&VpiQJ>rl~UAG>Nj-xszuMW?YWp{x-q#p$q{|HBcF1FD6Dhy+4y{z}ud8oUy*K928is0uBsf;(Gj!a+fwdIGYfJ&fXCfb?R&eQMx2^4I!Z*iC&p=~^bl>%F2XJ<{jh5!E^&IJG')).decode();_gc=lambda s:tuple(int(x.strip().rstrip("u"),0)for x in GEN_C.split(s+"={")[1].split("}")[0].split(","));IV,K,PERM,_X0,UCD=_gc("IV[8]"),_gc("K[RND]"),_gc("PERM[8]"),_gc("PW[8]"),_gc("UCD[96]");PAD2=bytes([128])+bytes(55)+(512).to_bytes(8,"big");_fn=lambda*xs:(x if callable(x)else x.__getitem__ for x in xs)
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
Ap=1;CIN=1;NTAIL=6 if Ap else 4;QM,XM=0xf28ae6fe,0xaf916655;PRE,_Y1,_Y4,_X4=8,8,{},set(range(10,16))
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
def AG(v):return v|(v<<RP)
class RecProg:
	def __init__(self):
		n=ROUNDS;self.imm,self.init=[],[];Ab,T0,T1,T2,T3,T4=0,11,12,13,14,15;ST,PB=list(range(1,9)),[9,10];W0,W1,W2,W3,WC0,WC1,WC2,WC3,E0,E1,WN=19,20,21,22,24,25,26,27,28,29,30
		def S(out,x,v,m=0):self.imm.append(v);out.append(("S",x,len(self.imm)-1,m))
		S(self.init,Ab,RMASK);S(self.init,WN,AG(_X0[0]))
		for i in range(10,n-6):S(self.init,T0,AG(K[i]));self.init.append(("T",KM+i,T0,2))
		_T3={i:_X0[i]for i in range(1,PRE)};_T3.update(_Y4)
		for i in sorted(_T3):S(self.init,T0,AG(_T3[i]));self.init.append(("T",WM+i,T0,2))
		AC=[5,6,10,11,12,15]
		for j,k in enumerate(range(2,8)):S(self.init,AC[j],AG((-K[_Y1+k])&M32))
		for rk,vk in zip((13,14,16,18,23,29),(K[n-6],K[n-5],K[n-4],K[n-3],XM,QM)):S(self.init,rk,AG(vk))
		def sigma(out,dst,src,rs,shr,mask=True,dup=True):
			if dup:out+=[("<",T0,src,32),("|",T0,src,T0)]
			out+=[(">",dst,T0,rs[0]),(">",T1,T0,rs[1]),("^",dst,dst,T1)];out+=[(">",T1,src,shr)if shr else(">",T1,T0,rs[2]),("^",dst,dst,T1)]
			if mask:out.append(("&",dst,dst,Ab))
		def rnd(out,st,pi,AB,addrk):a,b,c,d,e,f,g,h=st;P,PN=PB[pi],PB[1-pi];sigma(out,E0,e,(6,11,25),0,False);out+=[("^",T1,f,g),("&",T1,e,T1),("^",T1,g,T1)];out+=[("L",T0,addrk+KM,0),("+",E0,h,E0),("+",E0,E0,T1),("+",E0,E0,AB),("+",E0,E0,T0)];sigma(out,h,a,(2,13,22),0,True);out+=[("^",PN,a,b),("&",T0,PN,P),("^",T0,T0,b),("+",T1,h,T0)];out+=[("+",h,d,E0),("&",h,h,Ab),("+",d,E0,T1),("&",d,d,Ab)];return[d,a,b,c,h,e,f,g],1-pi
		assert WM==0;body=[];st,pi=list(ST),0;pre=[];SH=(n-16)%4
		for k in range(SH):st,pi=rnd(pre,st,pi,WC0,10+k);pre.append(("L",WC2,1+k,0));sigma(pre,E0,WC2,(7,18,0),3,True);pre+=[("+",E0,WC3,E0),("+",WC3,WC2,WC0)];sigma(pre,WC2,W2,(17,19,0),10,False);pre+=[("+",E0,E0,WC2),("&",E0,E0,Ab),("T",16+k,E0,0)]+[("|",a,b,b)for a,b in zip((WC0,WC1,W0,W1,W2,W3),(WC1,W0,W1,W2,W3,E0))]
		stl,pil=list(st),pi
		for j,wr in enumerate((WC0,WC1,W0,W1)):stl,pil=rnd(body,stl,pil,wr,10+j)
		assert stl==st and pil==pi;body+=[("L",WN,4,0)];sigma(body,E0,WN,(7,18,0),3,True);body+=[("+",WC2,W0,E0),("L",W0,1,0)];sigma(body,E0,W0,(7,18,0),3,True);body+=[("+",E0,WC3,E0),("+",WC3,WN,W1),("+",W1,W0,WC0)];sigma(body,W0,W2,(17,19,0),10,False);body+=[("+",W0,W0,E0),("&",W0,W0,Ab),("T",16,W0,0),("|",WC0,W2,W2),("L",W2,2,0)];sigma(body,E0,W2,(7,18,0),3,True);body+=[("+",W1,W1,E0),("+",W2,W2,WC1)];sigma(body,E0,W3,(17,19,0),10,False);body+=[("+",W1,W1,E0),("&",W1,W1,Ab),("T",17,W1,0),("|",WC1,W3,W3),("L",W3,3,0)];sigma(body,E0,W3,(7,18,0),3,True);body+=[("+",W2,W2,E0),("+",W3,W3,WC2)];sigma(body,E0,W0,(17,19,0),10,False);body+=[("+",W2,W2,E0),("&",W2,W2,Ab),("T",18,W2,0)];sigma(body,E0,W1,(17,19,0),10,False);body+=[("+",W3,W3,E0),("&",W3,W3,Ab),("T",19,W3,0)];ra,rb,rc,rd,re,rf,rg,rh=st
		def t1(out,dst,hr,er,fr,gr,wi,AB,kreg):
			sigma(out,E0,er,(6,11,25),0,False);out+=[("^",T1,fr,gr),("&",T1,er,T1),("^",T1,gr,T1)]
			if AB is None:out.append(("L",T0,WM+wi,2));AB=T0
			out+=[("+",E0,hr,E0),("+",E0,E0,T1),("+",E0,E0,AB),("+",dst,E0,kreg)]
		tail=[]
		if Ap:R5,QQ,E5,R4,E4,E3,E2,XX,YY=rh,17,rd,24,25,26,WC3,PB[0],31;t1(tail,R5,rh,re,rf,rg,n-6,WC0,13);tail+=[("+",E5,rd,R5),("&",E5,E5,Ab)];t1(tail,R4,rg,E5,re,rf,n-5,WC1,14);tail+=[("+",E4,rc,R4),("&",E4,E4,Ab)];t1(tail,E0,rf,E4,E5,re,n-4,W0,16);tail+=[("+",E3,rb,E0),("&",E3,E3,Ab)];t1(tail,E0,re,E3,E4,E5,n-3,W1,18);tail+=[("+",E2,ra,E0)];tail+=[("^",T1,E4,23),("&",T1,E2,T1),("^",T1,E4,T1),("+",XX,E5,T1),("+",XX,XX,W2)];tail+=[("+",YY,E4,W3)];tail+=[("^",T0,ra,rb),("^",E0,rc,29),("&",T0,T0,E0),("^",T0,29,T0),("+",QQ,R5,T0)];cp=[("|",ST[1],rb,rb),("|",ST[0],ra,ra)]if SH else[];tail+=cp[::-1]if ra==ST[1]else cp;fb=[E3,E2,ST[1],ST[0],QQ,R4,XX,YY];self.fin=[fb[PERM[k]]for k in range(8)]
		A1=[];AM=(WC0,WC1,W0,W1,W2,W3)
		for k in range(7,-1,-1):
			if _Y1+k in _X4:d=AM[k-2];A1+=[("+",d,self.fin[k],AC[k-2]),("&",d,d,Ab),("T",WM+_Y1+k,d,2)]
			else:A1.append(("T",WM+_Y1+k,self.fin[k],2))
		y0,y1=self.fin[0],self.fin[1];sigma(A1,ST[4],y0,(6,11,25),0,False,dup=True);A1+=[("+",ST[4],ST[4],y1),("&",ST[4],ST[4],Ab),("+",WC3,y1,WN)];sigma(A1,ST[0],y0,(2,13,22),0,False,dup=False);A1+=[("+",ST[0],ST[0],ST[4]),("&",ST[0],ST[0],Ab),("|",ST[1],y0,ST[2]),("|",ST[5],y0,ST[2])];self.blocks=[("S",A1+pre),("L",body,SH,n-16-SH,4),("S",tail)];self.flat=[]
		for blk in self.blocks:
			if blk[0]=="S":self.flat+=blk[1]
			else:_,bd,start,count,AP=blk;self.flat+=[("R",0,start,0),("R",1,start+count,0)];top=len(self.flat);self.flat+=bd+[("A",0,AP,0),("C",0,1,0),("J",top,0,0)]
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
Aa,ONE=(0,0),(0,1);_R1=(0,)*90;EXPECTED_EMITTER_INFO=(76996,871,77275,303808,0,0,60523,9959,6514,308072,16384,77275,31360,90,1562);_Y3="cd1d417ecbedec4a1d5178d753a279a1edd304ccdd026b33415f304075a383b1";_X3="7f612d7fa1eb4d22f9230623404dc5ac5850f2df6630d0a8c23b324dc991bb0e";_V5="646a9f3bec816cfc12d075ec0a26d8d2e1932164b5ccbadd68db30683f892984";_T5=int("4f1b82835e75599b85f700e790a37b0d36ac4f906707c7c205ff3cc7201aaa98",16)
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
		p1=None if ch1 is not None else(1 if(h[1][0]and u[1][0]and h[1][1]==u[1][1])else 0);AF=[(vs[1],cv)]
		if tuple(vs[1])in sp:sr,cr=sp[tuple(vs[1])];AF.append((sr,(cv+cr)&M32))
		AK=None
		for wc,cc in AF:
			for c0 in(0,1):
				for c1 in(0,1):
					for d_ in((0,1)if hd else(0,)):
						tot=c0+2*c1+d_;b1=1 if(p1 is None or c1==p1)else 0;sc=(2*_tz((cc-tot)&M32)+b1,-tot,-d_)
						if AK is None or sc>AK[0]:AK=(sc,c0,c1,d_,wc,cc)
		_,c0,c1,dl,wb,cb=AK;cv2=(cb-c0-2*c1-dl)&M32;t,rem=_adduc(g,h,u,cv2,c1,ch1);s=g.add3(t,vs[0],wb,c0,None,h[0],u[0]);return(g.add(s,_Y0(rem))if rem else s),fg,dl
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
	if Ap:a6,a7,a8,a9,e6,e7,e8,e9,AA,hg=st;T5,fg,_=A3(g,e6,e7,e8,e9,hg,(_Y0(K[r-6]-1),W[r-6]));e5=g.add(a9,T5,ONE);mj=[g.OR((ab[0],ab[1]^1),a8[j])if(QM>>j)&1 else g.AND(ab,a8[j])for j in range(32)for ab in(g.XOR(a6[j],a7[j]),)];Q=g.add(T5,mj,ONE);T4,fg,_=A3(g,e5,e6,e7,e8,fg,wd(r-5));e4=g.add(a8,T4);e3,fg=_ch3(g,[a7,W[r-4],_R2(g,e4,6,11,25,False)],e7,e4,e5,e6,fg,K[r-4]-2);e2,_=_ch3(g,[a6,W[r-3],_R2(g,e3,6,11,25,False)],e6,e3,e4,e5,fg,K[r-3]-2);X=g.addm(W[r-2],_R2(g,W[r-4],17,19,10,True),e5,[g.OR(e2[j],e4[j])if(XM>>j)&1 else g.AND((e2[j][0],e2[j][1]^1),e4[j])for j in range(32)]);Y_out=g.addm(W[r-1],_R2(g,W[r-3],17,19,10,True),e4);bw=[e3,e2,a7,a6,Q,T4,X,Y_out];out=[bw[PERM[k]]for k in range(8)];assert g.ahi==len(_R1);return g,[t for w in out for t in w]
MAX_NODES=77275;MAX_RECORDS=77018;_Q1=8
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
def AH(f,p):
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
		r=_R4 if _R4 is not None and self.free>>_R4&1 else AH(self.free,p)
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
def AI(g,nin,fixed,outs,tgt,free0,E):
	N=g.nodes;uses=[0]*len(N);AO={}
	for _,x,y in N[nin+1:]:uses[x]+=1;uses[y]+=1
	for i,(n,_)in enumerate(outs):uses[n]+=1;AO.setdefault(n,tgt[i])
	oids=sorted(AO);f0,f1=oids[0],oids[32];reg=dict(fixed);free=sum(1<<r for r in free0 if r not in fixed.values())|sum(1<<r for v,r in fixed.items()if not uses[v]);pend=sum(1<<tgt[i]for i,(n,_)in enumerate(outs)if n)
	def take(w=None,p=0):nonlocal free;r=w if w is not None and free>>w&1 else AH(free,p);free&=~(1<<r);return r
	for k in range(nin+1,len(N)):
		op,x,y=N[k];uses[x]-=1;uses[y]-=1;dying=[v for v in(x,y)if not uses[v]];w=AO.get(k);p=~((pend if k<f0-1800 else pend&~_M14)&~_M8)if(uses[k]<=3 and k<f1-1800 and w is None)else pend;ok=[reg[v]for v in dying if not p>>reg[v]&1 or reg[v]==w];dst=take(w)if w is not None and free>>w&1 else w if any(reg[v]==w for v in dying)else ok[0]if ok else None
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
Au=Fraction(497,1000);Ai=Fraction(15,100000);Ad=1e-6;CMAX=7;CUT_HALT_ORDER=CMAX+1;P_MIN=0.390000001;GRAIN=10**21;STAGE1_PLANES=20;PFP=12;GC=0;GT=3;PM=2;_T4=3;A7=2800;Ah=3800;A8=4200;Ae=1300;_X2=39;_S4=5;_S5=4;_S2=5;Ag=36;HANDLER_CODE,_U5,RECOVERY_CODE=1250,160,94;_X1=871;REGFILE=_X1*32;COUNTERS=16384;PLANE_COPY=LANES*32;ARRAY_BYTES=(2*ROUNDS-16)*32;ARRAYS=0;KEYB=47;GROUP=256;GROUP_BYTES=KEYB*32;assert ARRAY_BYTES<=PLANE_COPY<=COUNTERS;MEM_LIMIT=1<<20;ADVICE=0;KAPPA_256=35;KR=Fraction(62,5);KCHK=8192;A9=80;Af=100;WASM_RUN_OPERATORS=179323853;WASM_OPERATOR_FACTOR=2;WASM_EMITTER_INSTR=10332;_W3,_W2=EXPECTED_EMITTER_INFO[12],EXPECTED_EMITTER_INFO[14];SETUP_FIXED=256*3100+20000;_Z1=64+1+3*192+1000;_W1=46;_V1=36;_S0=_W1+_V1*10+2;_T0=1+2*_S0;SEARCH_EVAL_OPS=1<<48;_U2=_Z1*SEARCH_EVAL_OPS;_Y2=_T0*SEARCH_EVAL_OPS;CFG={16:dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),18:dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),256:dict(s1=20,W=102,kappa=KAPPA_256,Sb=1<<48)}
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
def _T2():Ak=1024;raw=2*160*64*32*13*13*12*Ak;assert 2*raw<SEARCH_EVAL_OPS;assert _Z1==1641 and _S0==408 and _T0==817;return raw,raw
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
def AJ():
	if not _DN:_DN.append(DigestNet(Az().qint))
	return _DN[0]
class Aw:
	def __init__(self,n):self.n,self.pr,self.pin=n,Az(),[0]*n
	def _low(self,o):return _V4(o,self.pr.qint)&((1<<self.n)-1)
	def step(self,*planes):return AJ().step(list(self.pr.step(*(list(planes)+[0]*(256-len(planes))))))[:self.n]
	def wstep(self,P):n,a,ns=self.n,(1<<256*len(P))-1,self.pr.ns;W=[sum(q[j]<<256*i for i,q in enumerate(P))for j in range(n)];ns["ALL"]=a;o=AJ().step(self.pr.step(*(W+[0]*(256-n))),n,a);ns["ALL"]=ALL;return[[(x>>256*i)&ALL for x in o]for i in range(len(P))]
	def f2(self,xs):return[self._low(o)for o in _V2(xs,256,self.pr.qwords)]
	def _Z2(self,x):return _Q0(_R0(words_of(x)))&((1<<self.n)-1)
def A0(x,p):return x&((1<<p["s1"])-1)==0 and(x>>p["s1"])&((1<<p["W"])-1)<p["Tp"]
def AE(x,p):return(((x>>p["D"])&((1<<p["kb"])-1))<<p["fb"])|((x>>p["s1"])&((1<<p["fb"])-1))
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
				key=AE(x,p);cnt["finished"]+=1;w=key+1
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
At=16;AL,B_T2=256,16
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
	return[AD(R.get(i),C[i])for i in range(len(trials))]
def AD(res,cnt):obs=dict(target_ok=int(res is not None),batches=cnt["batches"],halt=cnt["halt"]);return(None,None,obs)if res is None else(message(res[0]),message(res[1]),obs)
def Al(seed,tr,st):
	src,z=tr%3,[0]*256
	if src==0:xs=[_U3(seed,"u%d"%i)for i in range(AL)]
	elif src==1:r=_U3(seed,"r");xs=[(r+i)&ALL for i in range(AL)]
	else:
		xs,cur=[],[_U3(seed,"c%d"%l)for l in range(LANES)]
		for _ in range(AL//LANES):cur=_T1(list(st.step(*_V0(cur,256,st.pin))),256,st.pin);xs+=cur
	digs=[]
	for b in range(AL//LANES):digs+=_T1(AJ().step(list(st.step(*_V0(xs[b*LANES:(b+1)*LANES],256,st.pin)))),256,z)
	first,pair={},None
	for i,d in enumerate(digs):
		c=d&((1<<B_T2)-1)
		if c in first and xs[first[c]]!=xs[i]and pair is None:pair=(xs[first[c]],xs[i])
		first.setdefault(c,i)
	obs=dict(source=src,dup_w0=len(digs)-len(first));return(None,None,obs)if pair is None else(message(pair[0]),message(pair[1]),obs)
def AQ(req):
	eid,out=req["experiment_id"],[];bounded_check(Az())
	if eid=="bssha-n16":rows=A2(req["trials"])
	elif eid=="proj-k0-w256":st=Az();rows=[Al(t["seed"],t["trial"],st)for t in req["trials"]]
	else:raise ValueError("unknown experiment")
	for t,(a,b,obs)in zip(req["trials"],rows):out.append({"trial":t["trial"],"message_a_hex":a.hex()if a else None,"message_b_hex":b.hex()if b else None,"observations":obs})
	return{"schema_version":1,"trials":out}
def selftest():
	import random;assert CUT_HALT_ORDER==CMAX+1==8;r=random.Random(3);p=Az();info,h=bounded_check(p);bt=boundary_test(p,plan(256));g,o=_W5();ref=[];m=AI(g,256,{j+1:_Q2(j)for j in range(256)},o,[256+i for i in range(256)],range(_X1),ref.append);enc=lambda z:_S1([({"^":1,"&":2,"|":3}[a],b,c,d)for a,b,c,d in z]);assert m==0 and _S1(_patch([({"^":1,"&":2,"|":3}[a],b,c,d)for a,b,c,d in ref]))==_S1([({"^":1,"&":2,"|":3}[a],b,c,d)for a,b,c,d in p.recs]);assert max(max(x[1:])for x in p.recs)<_X1 and all(x[0]in "^&|"for x in p.recs)
	for xs in[[r.getrandbits(256)for _ in range(256)]for _ in range(8)]+[[0]*256,[ALL]*256]:assert _T1(list(p.step(*_V0(xs,256,p.pin))),256,p.pin)==[_W0(x)^p.qint for x in xs]
	for _ in range(10000):w=[r.getrandbits(32)for _ in range(8)];assert enc_invert(enc_words(w))==_R0(w)
	regs=[0]*_X1
	for j in range(256):regs[_Q2(j)]=r.getrandbits(256)
	a=list(regs);assert p.run(0,len(p.recs),regs)==p.kernel;p.fast(a);assert[a[_Q2(j)]for j in range(256)]==[regs[_Q2(j)]for j in range(256)];cur=[r.getrandbits(256)for _ in range(256)];pl=_V0(cur,256,p.pin)
	for _ in range(4):pl=list(p.step(*pl));cur=[_W0(x)^p.qint for x in cur]
	assert _T1(pl,256,p.pin)==cur;e=Aw(At);xs=[r.getrandbits(At)for _ in range(256)];pl=_V0(xs,At,e.pin)
	for _ in range(5):pl=list(e.step(*pl));xs=[e._Z2(x)for x in xs]
	assert _T1(pl,At,e.pin)==xs;xs=[r.getrandbits(256)for _ in range(2)];f=[_W0(x)for x in xs];assert _V2(xs,256)==f==rec().f(xs,False)and _V2(xs[:1],256)==f[:1];assert rec().f([0,ALL])==[_W0(0),_W0(ALL)]and _V2(xs,256,p.qwords)==[x^p.qint for x in f];rows=[r.getrandbits(256)for _ in range(256)];assert _U1(_U1(rows))==rows;assert(_U1(rows)[5]>>9)&1==(rows[9]>>5)&1;xs=[r.getrandbits(256)for _ in range(256)];assert _T1(AJ().step(list(p.step(*_V0(xs,256,p.pin)))),256,[0]*256)==[_Q0(_R0(words_of(x)))for x in xs];q,found=plan(At),0
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
	else:json.dump(AQ(json.load(sys.stdin)),sys.stdout)
