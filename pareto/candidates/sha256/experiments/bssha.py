import sys;import json;import hashlib;from fractions import Fraction;from math import isqrt,log,log2,log1p,exp,comb;M32=0xFFFFFFFF;ROUNDS=46;UNIT=3400;LANES,ALL=256,(1<<256)-1;GEN_C=__import__('lzma').decompress(__import__('base64').b85decode(b'{Wp48S^xk9=GL@E0stWa761SMbT8$j;A!9_;avba9!f+7EcWv7Lz|0s4)@dlRYKFC%Ru5;*dPDz@ko%eHoL=sDmUb#(BDY$sOdRsL4LgFV@TvGnH@iF;j73?6o^?j7#itiQmRCHN#=kKGtXi4|7YQFq^$XEWwHfiN!TMGV_ysE(0nbBHW0;RPmOQ;N94HyhnCU&0XF#T_#k2)svyw#oHJ`M2)K?EH<sl5qh{b6#Zk=ieMgC&=GmvE&(Ehs=V`B{ey+D$h~%fO@-260<mWlvx(rfxzvq@(jBy|fgzv15k`Oov>rc)y&27)WAM;nk6qQujok~gWkGKT8cw6}s5z%#~hyA&7_O@TO;t*=YJpm<t3cK?+n8a41C5JVYPH@Q+v}N!QLFyXpf|+5=`H4&N-jB`<&YmJ-4@P2yLO2RRrbe4HUXBuP$?0Y>n4i3Q@2Zk$RAx%%rTm<UIz*lO4ksBwsh<9$Bd&zYVs)4sNQ8j=kQ^Yjx%(M7eu8dFQK)MdL9-8tr)(baLW|^c#ztrw<-xYZ%${p3lQV|Wzw*GnzW8jQj=K3c=g0a)SK617r+-lEX#Ycm?WCk3lN1;}zj}}uGjh*ovXPzPsz{+JREtpQ9Yw21Zl<35p<C{19z;Zj_U_kqBa?P0%kX?f+ozu8fVUKYC@!`y)i2kh8-PJ+f9pEF1;%;n-!z~A%&ic@09*G~CMxKZr(DPOth>8s&O?DuAhy{N+nDV@&kqr;jCUSu0D4gL6Wmg?`fp}0C&EGDy4bqk-9ixFW`4M-EyN3FIG}EBas%5^LI*!Z8FiU3#I)|%eMX!{1Dg)XCjcJ>&kD%qE)Wl0*&akoifEU+HD=<W)mH7ltEpy9n@nmh^^gETOS4LeV4uiyk~5-_FTaWSrmV1Fc5KJ2#EwXeQ3VxTw+M=k)K{^x$w-5uCeF&Hm6zeU8{TN4X00?r-aHK^Rg4adrlQ02jfy%pHMT<S$z=|{kR=plgSj=3maAEXg!&yXO~0A1aj^oh8R*;lX7T(3QL@wa{Uq5l9T`UVPS1J=@cBb^4y&oHP9^!IGLZ`ugsh_FvN_b}-u@EWZ`yQ6FExK(+|`O2A|$}L8vvx{<HJxHq&(|+$1N!J%U2>IzqfNhSX@+~v_C8!{dt{~zVAgzWv&$0K%qZ^j|-CQ9GHl(zP_gjF>3M3P;fW_649I98GB1Jcyy;a-d3ZJ9nmlA<N7vy8}j8+`S_ZGM&U)~?)q2e{M8x7sm9RZuFc=)L1HV>PIPF8Lg}nQ_}C@u$slQ0Iu9Sy#Z{^VC7-V|Nh8iiesNDv%*wAvCmhmk5AyV)g0ZzeXz%IAAOG0BAA+IZKF4fQ>CVK6BKF+(>KBp$W#V5~c$nHVS(<quEdb*aF4c`AJ1TN()z4Ep&Y}&A<nENh;AsUKhiA%H;1~23Ki}EM?K6}#J6fUxp|Wd!NV%<wWfaomO6v{0PZ}H>hY}ytQcr;VlitBfvjYfVk><VpzQlZoCeTd~XC-EeN+|?W>)FOsfl+@Uo>n>AJ%zJCrCXR6n30$LZGJT``qK;>&@Dp5Djhj4;BieD+%Vxqupd$<NK8$bY76BNM#)(EvUepX4f(ry`P}N>EDqqicr`PT+B&dE!{=1@(=<BFZrq5eMc;;6QA4qdQQ2E8?0P1^{+^z6AaH9I%cah1KMbYkz)VLB65xM2MXt=|_yol=4N~y_vXeN5haA6^O<~NHX=lZUXdttbPr(M5@pZv=dT9o5uN420tK`+HM`DC&#Aoj$jdEN;dp&Vn<tw56P{9BzI?yRN5r|LnO#6#M*nsu>uR{<^jfB+npo(R8Y3>3A1x-?2fI1*q^JQLvQN7c3LFkIIGZd-vITOry16!2&wv9S@e>xmC-}HOC;+ErcHp$O|dqmEAEelvCb?Ls(Z~<h(9bMF{gY)I>l6bAvte_G{$@&>HJ(DL^GwVQW4&tole;YP^_JxCH=X1zLyYZyj3&2lMkJfni%jZs3`F#-#-QxRM?GR}zb)d58e`&p?;V9gHPf2Mh^999Z4oSd!vvPI1wy>!R^BBX7DtPGmllbfp3j%vRi}Y8+q4h3t3aO%0<e~>OUA|+wtA&5!M5(hME6E{c9X{@zLMY{|)W@xo>-(l!|33n95-Qy)`1*Xv_i&Cye<MnDD}~f9s={=ymN^$ZWl&?A;NLD5czGS{-&DWeC37-JkPw>DC$|Ap24?%c0hRaQ9>{sIRhavszs_}+&}1)Ve*~yn48(YxG9HZcp3&(hkqlMO@Q0T<El;DFRz1eQt&q$ims9KS8H6?h^+ZIYCa3jWSf-Eq>&7M1FYEF1Jn5dN%Wsn9FA_^Sf6bKJo>U~rVwbVXUI4IJs&@bsbS1!>@le^_NZ4Z|2+7R+Pn)W#J`q6@1M971UJ2c&A)>0s5&*ePxhKr%+8PTQz5mp0n7lcXc;Ryl)Z)+GzS=e|2HbCD__in_^;P>Nh<uU56min$)bG1Z_^k3Q5J8TYjD3N!j<W*epVr;feNjm^BkMJ=V~A$_PF(e25~y_eX9ruK@yoW~-$%+^m7pr1WON@wb{L#mtu3=SC<+urctw|;Sl3*Ro!qB8m;juN8j4zBhnXf>l9*Bfc7Q=52v>3E|BD;!6qc|f7)Ez=W9D;2E9n6tM(i&KaN$`zc-|I$&!%C06NjiGK_zC<j8n|(6;9zcE15YBlJ1*b(~gCFMA`E@xK3x|2z>@t?pz>(;J|~!o{KuUO-)5A);}eS&jV`QRKSISMbXKpry1BJR_o)8?D`KBm>zQ|c-x**uFJ>@#8QubCuW`j`Dt((rOL7Z2%<tyl&l*ndj>Bj=rsLcruh_t{UQJUtmdqZze@|!az)6;by-|2mQbGIMk+45&s`Sgx=Q_=^0X3prtn!Hg1TH1^`eJpuSFq9mAKf9c_6s_Z|p>Q3{K15B#N^)teVZC`qOvT&^vZNhcea5CKfAPL-$Ec{k}*)wrHvWsOhMK9)D3s%7<}<0byl6K^?UgOGjS>c5^V<TMU8*FLBlQJ5fZiFx9=Tie$F|jygJ_D|!dHMgDSF52x7aKiUgPjrPO~bNwTxK|ubKBVSUO7|FM{gUAOa`^ypuS+T-;m-5rkL{m;=k5J|wI{~A0>$l*E^)%@IX3eLWjt1+7JAYW#Z}!H}Z(@S34UxK&Ppc=BHDA_g+&$((rE|r&pu^l_>AunKYO{VYgL<`bdp#EL!ia{3o?+N`;}USVpJ{Iq$|Z49mWWL7U#<yT(NL#}jRa83*-VhRrMnLR^}KdRPPuHssgX{6CL!!(Z4(O_8i&cE=M0bhEhf&M;!R&X6y_iut3(jqW#KM^lYihV$3wT6jQSM*C*nRvl~{^&2-eqe=%+kR)Ns@(P8oz0ev{MJ?dPoB0TouN*$gPL<Io*GU%?2|$U65|S99m(ZabwcWwSj1T@t~Bb(D=KnkjdOHU4tFhV!%1Fd2?jTRG!47lkpuPsZk}e{m+R4&S_#^GQd`1~I`LvR-?h`6A93&fd^6f8efHM(6ODBZ?zKrodMvE_RYn_UY80LvLa^3=+L<riX~6?I=8j7DceOH=q2&%G0uxr$h|gW5K0;;YzRT299^5qzL~DDk1;T@4wDAX<?;j&Ht$CwVsbK8U9wO24c{v!tQN*KW`sqRk2NXd%`H32)P!aifik_;Cx-Irgyo7nPnC)){b}~@C^r)lE?ihAdeh@-KBy6kd-J60$?Ws<?LOg@R((9EmbVCVp8wv6PhATM6LXx{=zHR>g=(rvsD)7Mer!2ekq8Fk@J~pPjYG@B8#~+n11rJ$Zx3hS<>~Q7tSbaoXT8KQfZcnTFFr`ES`R|dYXEjbU++fIiDxjg6^oSlZWTF$uhK}t<0J6cTAC3zS{fVvbw*3vrr++&xtNvLdm14xN<8kKF<?F-Gm?KT>g}io0qi|7l=K4+aYvGg7FHk`8J{Ef+!|7PTctmUc!N4&hC5jsk<fqlPZ}NJ}~qj;UYDEx?K#WEIa9dJ5hhc5OS)!2961%q>H5+>-5yf%wu83$oz!Pm-XHC`1m(D`q)jvYh7VBXlDjhcV1A(-KtZRJmHRxP_RQ*6^(^N?X%*}RCTHT4E~)F(*rE3rjD#spz2f+@MEVWKL6^#JEZ09{r(0)Mu0;@xyO>6nbcdqz@w3PKl?~*r$0-+f=x(FlQoH3sQnR&YNZ!DjPdRjJu0GoQ^l72+Zd#PtH(as&m1_2KDN|qm$&2r*esi+>kkjl_FO*r9AgT6{%RNIMrI*{*80Y?+kk(R$dND6xwXQC5QjZ8pB;9mhTmP<Uk#NhLQEW0yE+x9$pc=C7lpth%bb5Sz?xf^js!ozzlZjEnV7MqejShNXyG^v(({MYXhdfY@-c9Lnr^g&XJE4UOS)%^N?!=;FD?f0i+{~H91rG6yRJv9W1#?)u^w8#=xo8tgC<)jL;df;?XBo{6lJ2GN%RzJnx}P{^0ez|jJ%~wr_)fHMx?|NXLgh$(>~6h#~e3gck4-7V%#i0tE;JH_nq5iY8KnW-D6yUnhsi*BLU3zE$N&LG`;^OY)T7cac%M9z8ZM<_AE76Ht#0wk;AAW96H=DJ6L#f)tpQ!+F(y=iz*sU8v&vuHmc%j`kb?N`n>zW#_pRn<$`F}i|MLIa~Av_sYM+pvOIi%IJf;(suD@ci(BizA@TxQqn1C>y{+#&kdg$e6^^k{gPQ~5o<e`nDa79{6!>~!>sGMN1!*YRwv>Fc58AS*@E41M%AUN5cc(j)61BU{oI_f5C8`WJK1bG^?b&hk)H5+&=D)dmsv}Xj8OgCF&m}85NR9$?29acT+rMY}Lx!UYK9|vz0frlOa@8^$1q1uP>coG)dgK2GPti2gWaq6n<0qL(YLLJF-K{SYH%6-Btm<j@tW?5toOsOV8;UyP?w63h;s&_`Fu-o`@pBU7&CjOU*<@Bq`h?}{K<UU*OfKOElv1vS0Hdr)c_)D(o(e?mY>K&xAaH!MTnCd@sP7<s<_P5BtsINqI{-AmLdL&HVW&XG2D*X4Qkp#44+#iMi?3N}Tvw-($(|FO11TB_9noB<Kyd?Iz3P#f(g&Axq8V|o6a}!D0n`n)znA|<5pm!@l)NEkVH@ALgUS;w6ut2m50EJ?bQ;Kaq8Ks+Wl5xaAcpkwJo${9Vr|7?J0a<XhUt?OOb6CEl8}hLsXJWn`a8NX6cC~aM$n6XyZwbd+Rdd;H)jVXXXx#%otl$U^S1i7LUy;|iV=W|jTHFv<2<>YAS*VK$APgrB~rp}?4)2CTbqPH%#61y+sa*MZt}Y^ZL2l^gJ0PENGOIuuRoFgXrzej9I^QW;58?cKBOFWsRtMQP9;gbtRvx4Nl+^=JCs?J2{7UmsH=uvvgV7mDS<NitcSDKdBe9O?qpQJr!f0E`1mU5*L>1*D5Bbj^5@EKJALVndtdsIPRE*0@S{-t>l2(%k!Blvc7+(dUS^&X4eJOGdYi`8i<x+fBYKr)1um>zDs<?P_FF8_jWpIE8o^7*9n9OBqKye-Bah_5tU4<MFxk>XjQ>OTbNNj)wrBW(O|wFk&i`kmkMnVGkjaeGg^B<(&1si=1uHUFjP$6fWagbJ-@xv&J8{MW3A24~=_J9CSCu%tQvN%Y=qG{uLvS%=`S1OAXl}vT02u~vaq~w{+{aE0`!t;}+FEDd;KQIWtux=_5AeD2Rqc8L)Q4kIF+m`;J?_z3z6k7<H{RU}9($AC*;?P>>-cDr#o=I$IIxG;9(~-wwR1ctQmOX&?X3*HdD6%mQJ<f{E!-P0F80lGYCD)c!T1`TPE+pO3k{G5oR}_AM;M3@Q;1;Hs`PNY=CIj>5c91-T{)1Zg@NYu{XY!sU!7;~$+3k<v&PksFB5WCW(t|I<Hh+xy(b8at72;vi3_0YniKC!GdrVxO3_uy_=s+_J!z^k*!?bc9OW+7Vs|Z54@eb=Nb+Bxn~FOsEC(OBTqS|4=wtDye$kskf24)GCZS#|75Rb#a@P0U`*cgt5xcUV`k7>s_(8zM&Cs(Brt1?O0NLRNYeQM_{ZBBvQD)CHZlaM(eZVxL|7{PR){kDGTq`@->4lUWF8ruTm6oI!$gvn8>+RwUh2``>6VLZ~i-)GKEq(Ec%qn5T{u4ucpNLloMjffWLW!d0>EjzIKtBpUGv@Gh&aw3c;7#p?8r;G4%U5j&vcY``)x49?jPM`)EShnqqcGkdw=aepskF~_AJD@c5ezBMn9Cxlm#oH)$vcG2D*2WuaYi#lhYF@rD1>+~iuYQXz?~MS7Ne4h$VlH}7t#4>V4GY<evfQMSbJ_(de6WrU;hSTDcm@72jV{ZQ8E#?RB-79sa}R>QkEaQWsL?(z!#Q%GAD2!IN(jdT1EAI(>5lVik+f2;apNGlSYb+zAm-%rThZ_7YO^h=8Em|@w2J(xG>xB(&T0^3m`^i=}{=I3+xofu<&qs1a@h)AZg^FwSPpK)!<N}>I8_f4cX^Oz2_E==z}e$9;=gLpZ}hie~K>~P35hqJiay(+YtuFN!ZowQHVYx5@E(U&NnRMv^ZQ9+Qjf12kG^PhBqzX6>cf0Mu?rqC07g1A<fpc`CwR3XWU)eal%hi?8mq!0v_g=M0#}I?egur!vAW0#mwt#2$}|au-v8PVR7RWz=m;*I|t-G`{vz9_R!C7w(#ywm;=p9l##sXz*}=IJc{EGSU}#N)xJF2e%z1d4+zcFBAPVlH4)W=L4h16zaAGk=?$oK^R4@im*By*8Yc&^5ip{5Id|?NI0mBEf*Re3>Bd#;$z)yBk(tp}vuIy;B+rvC=r9OiFB07dd>YOb_*V#cz?QVHoz<GdK)v$C;vyUH{vKUvaDD{jNUL}groyD+1-9Ri_!sskWf%-k4KNw|y3myR&GeaK`qqcJv|ox(W`c?H{^f+xosE|FI7L9Q<p&9as$2u?HzK1?OE24Zc7NV`u0Rygz=3?&7w<D%CRuo5kEfcz<uZm_plC~iaTh_Vw&a-~mh|uQo{i%S!cDaZlUkdh9b;L_<HCQ+R&501+cveGIx#rlFxlZZq!;sKkl9d38!byGZeKvfvejR$0051<^$QnY<KRcs5CL+Cgbsw-CgDV5ND&iIrTmTrBF_UOnMHUTU+k?GO^flKkCHxB7S8IrxLiQqY>Q~TNcMjFiIBNx!QC#sbO`r?y!#9sMzbP~NhBdo(3)Pl?9NthNtH5ThV8ZahO&oz>E^9L4FrA#*QVEh_$0JUTpeZ{583Zd2{T}DE96;fl07xX9lsd0HpG8Op4dUCU`a#-^{f=pw+FqgX7s?MuXr3e8deBfp+qwL=Z=@Apfb)(p~(!{R@!B_O$8Ue%>2k&4?751Td|mtqKs+)KrxzG!22alL!(aH(=gyLA;ZQ!<a9nJS#B?b(|Il_3d?E}2{+pHKQ;jaS34aM@mp_J9CA1?4d?&L0!2(6kn^qkr0D?{dDq#*qV6P%@aq!<bK})b&V}odEeX64IgQrNmV<KmN!&@`fx>A-)$@qinAdAW^@5N~Sm$3eHQN2(>iY;0nb=h8lcNS@ieZ#u{O;U>OJYU;_ktWjBAMRTMa`lnBup(c0a5@GCTKQ-32{I_wO>c!T`&646n$Eat+F<x_i?P#-O6l%yGRqI91+=38VyQ^Q;gQR*zSLrHEA)$d1M0pFhf;V&87nPVO^(rpiF9lHD@d_Knjlw7$GT?{TUR=f0Bq|X^AKcz&F%ZPu8^o<neOevybdO(NIt0B6fmjPWhCh_|1+7acKy_6d1;pQSs7ae1x^NLyA)*`GKx252}wY+=@wHyy$m$Y!4_ekrKPph;{YbQ&P2^DYYr1ci4o#5%oRo19&LH*#4-7)kx59haB$e62xQE59>JMU}$f}@s7#?u0Y68S9E^sdG>RK%YNZer}xB^qgM8ZIBEvCPrPAu;9EU2EU(ShHOS})bbkp^zq(d)i{t%920&UeP$w%%&Kw7lh7S_@NETtK{EBW>SG+&uM_1U~xaLm^nLda^qveK4kNu>r1E))Rl{l+H<+kHMh3Y(0LS=q_-d%sywABc7Lt5ZYAJ;>iJup5aMdoTsD`dqfVeOfMW0Qq2HWD^}@T1~O8Chg$i_wUW;`~#yMBGe*1oSsyelwp@e~+Yu;VeO|(W!Z5Z7x-Wc;Q{@+}puX9W~C`sFe{``2y8Mg-;DH>pcc&&pI9WlQ0$6d6OkU17L<(q63RrmAv-_{)S=CMl0Fs^FdeOplR>Id?dy!g(6#$7+5~0VnnJsCgh^kUsz83BspKAJ}iEQWF*$oxBAxPCkY>fdM8@y0((ttiLz4aBMXc;&rXKFM%5D>5Tg1^|9CJJT2MC4Y?)Gexfqo?^#l>^Y+i0ESzq27VD#SIP7;|e1--y1fKk_6S<gS0rxn#`mf)p%Id5^m?wUIMWO>&1*WgufSpp#kx>=1I)aelQ+peR(vkrqZz`FiZsE8s8&-%j9K^`-Kno!Om-VXn_I*u&(t{xQNl{yIn$N^C>JJ26`*5Vk->ob=`6QJ9jHCFNQpL(6FiNc|ZU)U6JaH)mqBj0|yHr;t}jM43p#fQz8lT9U(9jn}Gh$uC!Sdlk_gwP)sMmDkH*gVcV+9NKIUHMZxZHk)LQQ2LAMP3;dRnqS}S~ZyUG|1l2@Rc6}IkoIyKShXXE4gQWEj4!K*=G!(mEhN%4tAE%fOlc2U4*rVfpoKVK33HGREkO`X`2%H<A~&0Ixq@{^IQj%WkHJu3Tc=bZF%FIs);SPS89mOCCQ(+2f4_c8hNwSL8t=~?OZq);|i|#I-e`D3`?jM>lbg!cGM4e>x%+ongdXvfdKNH|0~iTRVu~wn?VKxjEJ|=GUY}QlBzav&E7|68{;N!O}tZ01Q`rIY(E?8)G)3A!Y6spg`<{z-I|<zsBGQ`lAW0cGoala+*8X)_vu~3%@y81Pf&xrNJRKjusLDb_8x-&X7sXIB~g1n)-8*Wurt~@CjYVKP1z`_CW*#j1)9BlThHAYfaB6K{hD#2+&U#Z$ppgvHfy6vMf@nAr`p>~sH@pXi&)elgo)CHES)E%!H3!n8g%R#VPFChsD|&3&?3hOhZKnWGhS8WtC0+BK81N;_n*o_VAcS|BPrZltRz)>aLBza6n6wB(^+e;-RweYR;9h)nVLl^%@J|#&@jc`IGeWY2OsxXL?bb0MkRT8lW?a0u<!vX)pwrq9tby7^M!HYW7E3;SDu0$yd*d`^(tH>xx3ji5P{&-WZH5^Em%83fr*&$_$Yy1hDdQ+<=uqY-|syJY?1_vcrUi|EC5%#lF8BhN3{=@7qna1C7!#rS8uh}AO*|wrI;DCy*mrBt!*8F!-E>N%x`#5^I6Q{Ykm(TI_P!e$rml$WeEdbo9$j9v@6WwPN5Je*BMFX^plY~Pw+u-u+>bW347?()XcH?=EnrQOiK8G8Gb2N%>n2J5%dvnHVS2>(mk@ZZW`d1m!`H39sdb;kQ=yr(D~~pIr@?{3409a8U#jldnx0mD<O<gCNFw=>i9$9BT8WpfJYW)xw)0bPw2!t3|xK`rNy_y2?nAJUeiB%Gyn7zclWHO2HL_b)Q46HRh_?oXmCHY98h}4vCj3Pv*WVT|HuNA$OdBcDXB;e6hdNn4VHRtr<DHs)0LFx%>!83R|YDo#+bgia#K}{faB)=SLJDF%EmJ(qpwyg5dR;R#CdY@wTh~NpFa4VLE91G)tUI^I#+>gEr-S|2NYc_4E=}tRBrhgv`f?{Z~TN#uTlgraX+1)=)l0nyTW&vK3<m{>=<ZL$k=eHF)f>sU|L4XW-#*rLa&{nnu6`~ym_NQf%lXjICmiI1{3jj$;t%zS71|pb*2`~o8)kBAIX!}p+^?Hq0RQ^@7{I^^ATGFwcDGCyrl@mw0N+|OnkBS%vfF8j*<|s?SC}QcZu@ZC+@=o(ZJ6$sQ<T&T^Mh^juD4tolJ7BGK(J9kD|G3_|tk&J#7-$SPegKg6Jskhi${TyXiCW4It0!PT>gwsP1dxE>r~^zpD?d;DMCNTSEO0i=Kmo?iB20{~JZzALjP(`mt~<M1?}54$U)J$o>k!pY${$WsCh7C#eZKBw9&}8H~p4N~dUhG*lBm_m9j@=_ohEhe~!gcC%k#rha=lcT7B(x%HsxfZajBpZc&{6lv&ccEywoJC3i|{pHjjl3(%yC`G$LozaR`%bq<)fcE8N+kHXUvT_jXr8!6ciCPt$I#lC4W)7<nRQYPOnOl!)p_)uI72W`j(^?{^p0jJ12qaKSddv*%vz(Rv_tcSKE3QlkmfjTsbBkFH?E5)f7F{PUO?)*DU>UB^cwezl<iqn``~vILYPr+VB6b?ZXH2G)f}lP~zfCrF)F*?t(j$JPzfo!@Fy$IE_beD($xO9U)n_`xh`9yw1nar~Uff2h(6hHL#gejfDI$CHN2zYsfY$N6&r>A~%NeMNlcqXx%BNa^CL}mblaIN8&T6gCC~pTt@z;KZn3`E_nEIy<aqR_g4X(Ljqh{JS{qYBw$c=8&>TMKBWuYQp-+nApw1a06U2Hru)Ot`CpU;B{KNijIbrzUyb8SJ-q5rMUBsN;zz&M&(1d<_}W)(7|L-k#Jzenovu#ZP{#E{b5zj^U694FTBm*fO5!J4i^(`2f~*7<lcPLw;}A~rqk=L-J|m0}IeyyiG0tPuqYrX9Dp0_hv7+XWKVmcy5;4)yS74+@a%hwZ{MAl~IO3Sg@bYP-V;(P!_^CJ<1gW!LFmHEO~mVCbS=={Oe%l3?Ucz?+G$JGL=1DoC2*m^O#E(OsCF@Ry6?v_Ou*zT5Ok;e9O%Y@M`vu7hv#?}idcvWp!81imvSY~4EEQcHxRM_*YNlI*Y^-pURG<upy8(Z@hl8~UA^96#r?BU^&IDLTRgL$^JRAY=KMS?jRo%*(-Bz)05}>of`yrhgJdki;$tS4NOQR5VF%zU>ev)%Am&P2~@=`LKbxCz#p3w64n6Vp1Ekm(Mh){;^sYj8L_pNqF-kB`6@gS}q1ya=K)|;lgfEA>3Au^HYAdM!#$}tQWUyU>Zle+qZ}A5VAeC<qPgruJ0>Hc1UJx?Ahu#%RoEbp^AgS>aMg<D&7ep`OZ=FV(s_2+M&0{U9njk>f|vO$R4PE>M%n^n}5J4or<H=j~931du50uL}e1s+cd3_D%IYV#|$Em{aoTPtv>bB0~#?1Qr*);&^Wruo&{P|_33Dd{W1-6tZ^Cn=*)YIegxRS7AHh8o?G0S{2&dy3<z$4dX&Hg8-gD<8ODJ#Rxus~c?t*x`}QU07ul%O2T;-VF9=vdd%WS9rgM)`Lh{@Gky8QOej34a*A-ex$^|C`5^kXZfQ+cBTiHyRVJgv#<OgznN?;Zhujj3RiE{!hCcho<`|kEz_gAy%xQK3-N%ZO)yEV&TR+nycfLOYE@S{I1jQxZgUlY&k*|C%537L+kALO!Lj}<{BQ=%eXM1c)}t5uX}#@yaYv=)(t4fhDnKvCs#@W^E#G{l`d{h4c8_lHy<SnhbK#6Gc)MNH`VtF0KgL|uCPSN&Ej8A|Bs)U_y1LXe|{iCp%lF~oS@IqaN;B|&%vlGc7LiuFc?)_Fwv@k-C2PriW+mH8PqQ~?<7Ep$vlx5{b-|98@)*kT}rAfb>MP#qj3+0@5~`#Z?87m`=~QY9n;YUqPXoaBkE$u!<rsSRGeiO6$`h@EtPNp=5BsW0&I6aF1^d-wc`r<=}Owc^Ivfp2*QU9r}<%btqcdENS8QWh@8R>k!>w>AZ%tvhi+llLwM{WdWc>O7^m!%J%HaW-sx0VX$9IjTfw!g&^Ov;$jbCv4FtzgJ<zF1&O%An0nEa;mIgADp2t%)r*c#tudP&tq<zFNk1a(k?xN4zVWdJH$&Z%Mo;TP{DpQ1A{F0*eW*_A1-}av3o^SyVMfO8uHutnq{l~Jn6pSeOeJv8s)d$);^T@9x;jVn?-hgwU^N@DBw156>+#i>~0X@JH$9<iWeGC3|m!&1Y_;7R;^|3@);0p7#BP*t2bjbf^%}4iFLwe@?+xtk`(~+Nzu+6QAs)gNv@PRb74r4b-=?M!|~CBTgje2qWW#zS}}MI+Lq;<M1hw-r9jwex+{-&*If`b(menym+(cqDA!#OJKgqi!exz630ka&{xH>C%cPtNE3=WJ`OAgjH)<4M00000bQSlfJo}r*00I3;;nM*CS9q<*vBYQl0ssI200dcD')).decode();_gc=lambda s:tuple(int(x.strip().rstrip("u"),0)for x in GEN_C.split(s+"={")[1].split("}")[0].split(","));IV,K,PERM,PREFIX_WORDS,UCD=_gc("IV[8]"),_gc("K[RND]"),_gc("PERM[8]"),_gc("PW[8]"),_gc("UCD[96]");PAD2=bytes([128])+bytes(55)+(512).to_bytes(8,"big");_fn=lambda*xs:(x if callable(x)else x.__getitem__ for x in xs)
def _ror(v,k):return((v>>k)|(v<<(32-k)))&M32
def words_of(x):return[(x>>(32*(7-i)))&M32 for i in range(8)]
def int_of(w):return sum(w[i]<<(32*(7-i))for i in range(8))
def _SIG0(a):return _ror(a,2)^_ror(a,13)^_ror(a,22)
def _SIG1(e):return _ror(e,6)^_ror(e,11)^_ror(e,25)
def _CH(e,f,g):return(e&f)^(~e&g)
def _MAJ(a,b,c):return(a&b)^(a&c)^(b&c)
def _exp40(ws):
	ws=list(ws)
	for i in range(16,ROUNDS):x,y=ws[i-15],ws[i-2];ws.append((ws[i-16]+(_ror(x,7)^_ror(x,18)^(x>>3))+ws[i-7]+(_ror(y,17)^_ror(y,19)^(y>>10)))&M32)
	return ws
TAILB=1;CIN=1;NTAIL=6 if TAILB else 4;QM,XM=0xf66f2195,0x39a64ee5;PRE,VARBASE,TAILMAP,OFFSET=8,8,{},set(range(10,16))
def _build_ws(w,prefix=None):
	prefix=PREFIX_WORDS if prefix is None else prefix;ws=list(prefix[:PRE])+[0]*(16-PRE)
	for k in range(8):ws[VARBASE+k]=(w[k]-(K[VARBASE+k]if VARBASE+k in OFFSET else 0))&M32
	for pos,v in TAILMAP.items():ws[pos]=v
	return ws
def _trace(w,prefix=None):
	ws=_exp40(_build_ws(w,prefix));a,b,c,d,e,f,g,h=IV;A,E,T={0:a,-1:b,-2:c,-3:d},{0:e,-1:f,-2:g,-3:h},{}
	for i in range(ROUNDS):t1=(h+_SIG1(e)+_CH(e,f,g)+K[i]+ws[i])&M32;t2=(_SIG0(a)+_MAJ(a,b,c))&M32;a,b,c,d,e,f,g,h=(t1+t2)&M32,a,b,c,(d+t1)&M32,e,f,g;A[i+1],E[i+1],T[i+1]=a,e,t1
	return ws,A,E,T
def state_words(w,prefix=None):_,A,E,_=_trace(w,prefix);r=ROUNDS;return[A[r],A[r-1],A[r-2],A[r-3],E[r],E[r-1],E[r-2],E[r-3]]
def enc_words(w,prefix=None):ws,A,E,T=_trace(w,prefix);r=ROUNDS;bw=[E[r-3],E[r-2],A[r-7],A[r-6],(T[r-5]+_CH(A[r-6]^A[r-7],A[r-8],QM))&M32,T[r-4],(E[r-5]+_CH(E[r-2],XM,E[r-4])+ws[r-2])&M32,(E[r-4]+ws[r-1])&M32];return[bw[PERM[k]]for k in range(8)]
def enc_invert(enc):
	r,bw=ROUNDS,[0]*8
	for k in range(8):bw[PERM[k]]=enc[k]
	e3,e2,a7,a6,Q,T4,X,Y=bw;a5=(Q+(a6&a7&~QM)-(~a6&~a7&QM)+_SIG0(a6))&M32;a4=(T4+_SIG0(a5)+_MAJ(a5,a6,a7))&M32;a3=(e3-a7+_SIG0(a4)+_MAJ(a4,a5,a6))&M32;a2=(e2-a6+_SIG0(a3)+_MAJ(a3,a4,a5))&M32;t1=(X+(e2&e3&~XM)-(e2&~e3&XM)+_SIG1(e2)+K[r-2])&M32;e1=(a5+t1)&M32;a1=(t1+_SIG0(a2)+_MAJ(a2,a3,a4))&M32;t0=(Y+_SIG1(e1)+_CH(e1,e2,e3)+K[r-1])&M32;return[(t0+_SIG0(a1)+_MAJ(a1,a2,a3))&M32,a1,a2,a3,(a4+t0)&M32,e1,e2,e3]
def f_scalar(x,n=256):return int_of(enc_words(words_of(x)))&((1<<n)-1)
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
		def S(out,x,v):self.imm.append(v);out.append(("S",x,len(self.imm)-1,0))
		S(self.init,MASK,RMASK);S(self.init,WN,_rep(PREFIX_WORDS[0]))
		for i in range(10,n-6):S(self.init,T0,_rep(K[i]));self.init.append(("T",KM+i,T0,2))
		constpos={i:PREFIX_WORDS[i]for i in range(1,PRE)};constpos.update(TAILMAP)
		for i in sorted(constpos):S(self.init,T0,_rep(constpos[i]));self.init.append(("T",WM+i,T0,2))
		hregs=[5,6,10,11,12,15]
		for j,k in enumerate(range(2,8)):S(self.init,hregs[j],_rep((-K[VARBASE+k])&M32))
		for rk,vk in zip((13,14,16,18,23,29),(K[n-6],K[n-5],K[n-4],K[n-3],XM,QM)):S(self.init,rk,_rep(vk))
		def sigma(out,dst,src,rs,shr,mask=True,dup=True):
			if dup:out+=[("<",T0,src,32),("|",T0,src,T0)]
			out+=[(">",dst,T0,rs[0]),(">",T1,T0,rs[1]),("^",dst,dst,T1)];out+=[(">",T1,src,shr)if shr else(">",T1,T0,rs[2]),("^",dst,dst,T1)]
			if mask:out.append(("&",dst,dst,MASK))
		def rnd(out,st,pi,wreg,addrk):a,b,c,d,e,f,g,h=st;P,PN=PB[pi],PB[1-pi];sigma(out,E0,e,(6,11,25),0,False);out+=[("^",T1,f,g),("&",T1,e,T1),("^",T1,g,T1)];out+=[("L",T0,addrk+KM,0),("+",E0,h,E0),("+",E0,E0,T1),("+",E0,E0,wreg),("+",E0,E0,T0)];sigma(out,h,a,(2,13,22),0,True);out+=[("^",PN,a,b),("&",T0,PN,P),("^",T0,T0,b),("+",T1,h,T0)];out+=[("+",h,d,E0),("&",h,h,MASK),("+",d,E0,T1),("&",d,d,MASK)];return[d,a,b,c,h,e,f,g],1-pi
		assert WM==0;body=[];st,pi=list(ST),0;pre=[];SH=(n-16)%4
		for k in range(SH):st,pi=rnd(pre,st,pi,WC0,10+k);pre.append(("L",WC2,1+k,0));sigma(pre,E0,WC2,(7,18,0),3,True);pre+=[("+",E0,WC3,E0),("+",WC3,WC2,WC0)];sigma(pre,WC2,W2,(17,19,0),10,False);pre+=[("+",E0,E0,WC2),("&",E0,E0,MASK),("T",16+k,E0,0)]+[("|",a,b,b)for a,b in zip((WC0,WC1,W0,W1,W2,W3),(WC1,W0,W1,W2,W3,E0))]
		stl,pil=list(st),pi
		for j,wr in enumerate((WC0,WC1,W0,W1)):stl,pil=rnd(body,stl,pil,wr,10+j)
		assert stl==st and pil==pi;body+=[("L",WN,4,0)];sigma(body,E0,WN,(7,18,0),3,True);body+=[("+",WC2,W0,E0),("L",W0,1,0)];sigma(body,E0,W0,(7,18,0),3,True);body+=[("+",E0,WC3,E0),("+",WC3,WN,W1),("+",W1,W0,WC0)];sigma(body,W0,W2,(17,19,0),10,False);body+=[("+",W0,W0,E0),("&",W0,W0,MASK),("T",16,W0,0),("|",WC0,W2,W2),("L",W2,2,0)];sigma(body,E0,W2,(7,18,0),3,True);body+=[("+",W1,W1,E0),("+",W2,W2,WC1)];sigma(body,E0,W3,(17,19,0),10,False);body+=[("+",W1,W1,E0),("&",W1,W1,MASK),("T",17,W1,0),("|",WC1,W3,W3),("L",W3,3,0)];sigma(body,E0,W3,(7,18,0),3,True);body+=[("+",W2,W2,E0),("+",W3,W3,WC2)];sigma(body,E0,W0,(17,19,0),10,False);body+=[("+",W2,W2,E0),("&",W2,W2,MASK),("T",18,W2,0)];sigma(body,E0,W1,(17,19,0),10,False);body+=[("+",W3,W3,E0),("&",W3,W3,MASK),("T",19,W3,0)];ra,rb,rc,rd,re,rf,rg,rh=st
		def t1(out,dst,hr,er,fr,gr,wi,wreg,kreg):
			sigma(out,E0,er,(6,11,25),0,False);out+=[("^",T1,fr,gr),("&",T1,er,T1),("^",T1,gr,T1)]
			if wreg is None:out.append(("L",T0,WM+wi,2));wreg=T0
			out+=[("+",E0,hr,E0),("+",E0,E0,T1),("+",E0,E0,wreg),("+",dst,E0,kreg)]
		tail=[]
		if TAILB:R5,QQ,E5,R4,E4,E3,E2,XX,YY=rh,17,rd,24,25,26,WC3,PB[0],31;t1(tail,R5,rh,re,rf,rg,n-6,WC0,13);tail+=[("+",E5,rd,R5),("&",E5,E5,MASK)];t1(tail,R4,rg,E5,re,rf,n-5,WC1,14);tail+=[("+",E4,rc,R4),("&",E4,E4,MASK)];t1(tail,E0,rf,E4,E5,re,n-4,W0,16);tail+=[("+",E3,rb,E0),("&",E3,E3,MASK)];t1(tail,E0,re,E3,E4,E5,n-3,W1,18);tail+=[("+",E2,ra,E0)];tail+=[("^",T1,E4,23),("&",T1,E2,T1),("^",T1,E4,T1),("+",XX,E5,T1),("+",XX,XX,W2)];tail+=[("+",YY,E4,W3)];tail+=[("^",T0,ra,rb),("^",E0,rc,29),("&",T0,T0,E0),("^",T0,29,T0),("+",QQ,R5,T0)];cp=[("|",ST[1],rb,rb),("|",ST[0],ra,ra)]if SH else[];tail+=cp[::-1]if ra==ST[1]else cp;fb=[E3,E2,ST[1],ST[0],QQ,R4,XX,YY];self.fin=[fb[PERM[k]]for k in range(8)]
		head=[];wregs=(WC0,WC1,W0,W1,W2,W3)
		for k in range(7,- 1,- 1):
			if VARBASE+k in OFFSET:d=wregs[k-2];head+=[("+",d,self.fin[k],hregs[k-2]),("&",d,d,MASK),("T",WM+VARBASE+k,d,2)]
			else:head.append(("T",WM+VARBASE+k,self.fin[k],2))
		y0,y1=self.fin[0],self.fin[1];sigma(head,ST[4],y0,(6,11,25),0,False,dup=True);head+=[("+",ST[4],ST[4],y1),("&",ST[4],ST[4],MASK),("+",WC3,y1,WN)];sigma(head,ST[0],y0,(2,13,22),0,False,dup=False);head+=[("+",ST[0],ST[0],ST[4]),("&",ST[0],ST[0],MASK),("|",ST[1],y0,ST[2]),("|",ST[5],y0,ST[2])];self.blocks=[("S",head+pre),("L",body,SH,n-16-SH,4),("S",tail)];self.flat=[]
		for blk in self.blocks:
			if blk[0]=="S":self.flat+=blk[1]
			else:_,bd,start,count,stepw=blk;self.flat+=[("R",0,start,0),("R",1,start+count,0)];top=len(self.flat);self.flat+=bd+[("A",0,stepw,0),("C",0,1,0),("J",top,0,0)]
		self.instr=len(self.init)+len(self.flat);self.mem,self.regs=[0]*(2*ROUNDS-16),[0]*32;self.run(self.init);self.mem0,self.regs0=list(self.mem),list(self.regs);self.ops=self.run(self.flat)
	def run(self,recs):
		r,mem,p,flag,pc,cnt=self.regs,self.mem,[0,0,0],False,0,0
		while pc<len(recs):
			op,x,y,z=recs[pc];pc+=1;cnt+=1
			if op in"^&|+><":r[x]=(r[y]^r[z]if op=="^"else r[y]&r[z]if op=="&"else r[y]|r[z]if op=="|"else r[y]+r[z]if op=="+"else r[y]>>z if op==">"else r[y]<<z)&ALL
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
def packed_f(xs,n,qw=None):q=sum(qw[i]<<(32*i)for i in range(8))if qw else 0;return[(v^q)&((1<<n)-1)for v in rec().f(xs)]
def packed_ops(qw=None):return rec().ops
ZERO,ONE=(0,0),(0,1);_ADD_HINTS=(0,)*66;EXPECTED_EMITTER_INFO=(54115,871,54372,215030,0,0,42451,7194,4470,216460,16384,54372,29696,66,664);STATIC_SLP_SHA256="dd7f323a19388a21206256755344dab64eae201edd1f284ff72881832afe7764";STATIC_C_SHA256="5a4853e5972d304fa6ef1c0dbcc61b5b3f81e906ddd1048ca06d5667e197f292";STATIC_WASM_SHA256="009eac25e3efd11e5a78724c19a3e425ba9610bb64c307496b1f4bd97df8e52c";POLARITY_Q=int("a3593570a9bf76591b696921a6471672f8579133a165d61c7f45820dfea59588",16)
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
		if tm==1:w=X(y,U);n8=X(z,w);s=X(x,n8);n6=O(U,X(y,u));return s,(ZERO if oU else X(n6,w)),X(n6,A(n8,X(x,w)))
		if tm==2:w5=X(x,y);w6=X(z,w5);s=X(U,w6);w9=X(u,w6);w10=O(U,(w9[0],w9[1]^1));w11=O(w5,X(x,z));return s,(ZERO if oU else X(w6,(w10[0],w10[1]^1))),X(w10,(w11[0],w11[1]^1))
		n5=X(z,U);n9=X(x,n5);s=X(y,n9);n6=X(x,y);n8=O(U,X(z,u));n11=A((n6[0],n6[1]^1),n9);return s,(ZERO if oU else X(n5,n11)),X(n8,n11)
	def add3(self,A,B,C,cin=0,d0=None,h0=None,u0=None):
		a,b,c=_fn(A,B,C);s=[None]*32
		if h0 is not None:
			sw0,u=self.fa(b(0),c(0),ONE if cin else ZERO);s[0]=self.XOR(u0,sw0);w=self.XOR(h0,sw0)
			if u0[0]and w[0]and u0[0]!=w[0]and u0[1]!=w[1]:cm=self.XOR(self.AND((u0[0],u0[1]^1),w),sw0)
			else:cm=self.XOR(self.AND(u0,w),h0)
			U=self.XOR(u,cm)
		elif cin==0:
			s[0],U=self.fa(a(0),b(0),c(0))
			if d0 is not None:s[0],u=self.fa(s[0],d0,ZERO);U=self.XOR(U,u)
			else:u=ZERO
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
		if not cv2:return self.add(a,b,ONE if cin else ZERO)
		k,s,c=_tz(cv2),[None]*32,ONE if cin else ZERO
		for i in range(k):s[i],c=self.fa(a(i),b(i),c)
		if k==31:s[31]=self.XOR(self.XOR(a(31),b(31)),(c[0],c[1]^1));return s
		ops=(a(k),b(k),c)
		for pi in range(3):
			o=[ops[j]for j in range(3)if j!=pi]
			if o[0][1]==o[1][1]:p,x,y=ops[pi],o[0],o[1];break
		u0=self.XOR(x,p);s[k]=self.XOR(u0,(y[0],y[1]^1));u,U,C=p,self.OR(u0,self.XOR(y,p)),_constw(cv2)
		for i in range(k+1,31):s[i],u,U=self._col((C[i],a(i),b(i)),u,U,i==30,True)
		s[31]=self.XOR(self.XOR(self.XOR(a(31),b(31)),C[31]),U);return s
	def _baseline(self,cv,vs,fb=None,cid=None):
		if len(vs)==2 and cv and fb is None:
			if cid in(20,23,24,27):return self.add2c(vs[0],vs[1],cv)
			if cid in(16,18,22):
				rem=((-K[17])&M32)if cid==18 else((4-K[19])&M32)if cid==22 else((6-PREFIX_WORDS[7]-K[23])&M32);s=self.add2c(vs[0],vs[1],(cv-rem)&M32);out=self.add(s,_constw(rem));sp=getattr(self,"split",None)
				if sp is not None:sp[tuple(out)]=(s,rem)
				return out
		bb=fb if fb is not None else(max(range(len(vs)),key=lambda k:(_tz((cv-k)&M32),-k))if CIN and cv else 0)
		if len(vs)==4 and bb==0 and not cv:A,B,D,C=vs;s=self.add3(A,B,C,0,D[0]);return self.add(s,[ZERO]+D[1:])
		ub=0
		while len(vs)>2:c3=min(bb-ub,2);ub+=c3;vs=[self.add3(*vs[:3],c3)]+vs[3:]
		s=vs[0]
		for w in vs[1:]:c1=1 if ub<bb else 0;ub+=c1;s=self.add(s,w,ONE if c1 else ZERO)
		cv=(cv-ub)&M32
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
		assert 0
	def addm(self,*ws,force_bb=None):
		cv,vs=0,[]
		for w in ws:
			if all(x[0]==0 for x in w):cv+=sum(x[1]<<i for i,x in enumerate(w))
			else:vs.append(w)
		cv&=M32
		if not vs:return _constw(cv)
		cid=self.ahi;self.ahi+=1;hint=_ADD_HINTS[cid]
		if hint and force_bb is None:op=list(vs)+([_constw(cv)]if cv else[]);assert hint<(1<<len(op))and hint.bit_count()==3;return self._choice(op,hint)
		return self._baseline(cv,list(vs),force_bb,cid)
	def xorw(self,A,B):return[self.XOR(a,b)for a,b in zip(A,B)]
def _tz(v):return 32 if v==0 else(v&-v).bit_length()-1
def _constw(v):return[ONE if(v>>i)&1 else ZERO for i in range(32)]
def _sigb(g,A,r1,r2,r3,shift,j):return g.XOR(g.XOR(A[(j+r1)%32],A[(j+r2)%32]),(A[j+r3]if j+r3<32 else ZERO)if shift else A[(j+r3)%32])
def _sigma(g,A,r1,r2,r3,shift):return[_sigb(g,A,r1,r2,r3,shift,j)for j in range(32)]
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
def _col_uc(g,hw,ui,u,U,cb,ch,oU):
	idx=(cb<<4)|hw[1]|(ui[1]<<1)|(u[1]<<2)|(U[1]<<3);code=UCD[64+idx]if oU else UCD[2*idx+ch]
	if not code:w6=(ui[0],ui[1]^cb);s=g.XOR(U,w6);w9=g.XOR(u,w6);w10=g.OR(U,(w9[0],w9[1]^1));w11=g.OR(ui,(hw[0],hw[1]^cb));return s,(ZERO if oU else g.XOR(w6,(w10[0],w10[1]^1))),g.XOR(w10,(w11[0],w11[1]^1))
	ops=("x","a","o");sr=g.mk("x",ui[0],U[0]);rs=[hw[0],ui[0],u[0],U[0],sr]if oU and((code>>26)&1)else[ui[0],u[0],U[0],sr,g.mk("a"if ui[1]else "o",hw[0],ui[0])]
	for q in range(3):c=(code>>(8*q))&255;rs.append(g.mk(ops[c&3],rs[(c>>2)&7],rs[c>>5]))
	a3=(code>>24)&3;Ur=g.mk("x",rs[4+a3],rs[7])if a3<3 else rs[7];return(sr,ui[1]^U[1]^cb),(ZERO if oU else(rs[4+((code>>26)&3)],(code>>28)&1)),(Ur,(code>>29)&1)
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
	if ch1 is not None:out[1],c=g.fa(A[1],ch1,ONE if c1 else ZERO)
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
	if bm==k:s0=g.XOR(u[k],c);out[k]=(s0[0],s0[1]^1);Ucs=g.OR(u[k],g.XOR(A[k],c));ucs=(A[k]if dc[k+1][A[k][1]][Ucs[1]]<=dc[k+1][c[1]][Ucs[1]]else c)if k<30 else ZERO;sc=k+1
	else:
		cu,cc,cw=c,ZERO,_constw(cv)
		for i in range(k,bm):
			ti=g.XOR(u[i],cu);w=g.XOR(A[i],cu)
			if u[i][0]and w[0]and u[i][0]!=w[0]and u[i][1]!=w[1]:cu=g.XOR(g.AND((u[i][0],u[i][1]^1),w),cu)
			else:cu=g.XOR(g.AND(u[i],w),A[i])
			out[i],cc=g.fa(ti,cw[i],cc)
		Ucs=g.XOR(cu,cc);ucs=cu if dc[bm][cu[1]][Ucs[1]]<=dc[bm][cc[1]][Ucs[1]]else cc;sc=bm
	for i in range(sc,31):cb=(cv>>i)&1;ch=0 if i==30 else dh[i][ucs[1]][Ucs[1]];out[i],ucs,Ucs=_col_uc(g,A[i],u[i],ucs,Ucs,cb,ch,i==30)
	s31=g.XOR(u[31],Ucs);out[31]=(s31[0],s31[1]^((cv>>31)&1));return out,0
def _t1hg(g,e,f,gg,h,hg,Wd,d=None):
	sp=getattr(g,"split",{});fg=[g.XOR(f[j],gg[j])for j in range(32)];hh=any(x[0]!=0 for x in h);ch1=g.XOR(f[1],g.AND((e[1][0],e[1][1]^1),fg[1]))if(hh and e[1][0]and fg[1][0]and e[1][1]!=fg[1][1])else None;u=[None if(j==1 and ch1 is not None)else g.XOR(hg[j],g.AND(e[j],fg[j]))for j in range(32)];s1=lambda j:_sigb(g,e,6,11,25,False,j);cv,vs=0,[s1]
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
		_,c0,c1,dl,wb,cb=best;cv2=(cb-c0-2*c1-dl)&M32;t,rem=_adduc(g,h,u,cv2,c1,ch1);s=g.add3(t,vs[0],wb,c0,None,h[0],u[0]);return(g.add(s,_constw(rem))if rem else s),fg,dl
	return g.addm(u,_sigma(g,e,6,11,25,False),*Wd),fg,0
def _rnd2(g,st,Wd):
	a,b,c,d,e,f,gg,h,prev,hg=st;t1,fg,delta=_t1hg(g,e,f,gg,h,hg,Wd,d);ne=g.add(d,t1,ONE if delta else ZERO);ab,mj=[None]*32,[None]*32
	def mb(j):
		ab[j]=g.XOR(a[j],b[j])
		if c[j]==ZERO:mj[j]=g.AND(a[j],b[j])
		elif ab[j][0]and prev[j][0]and ab[j][0]!=prev[j][0]and ab[j][1]!=prev[j][1]:mj[j]=g.XOR(g.AND((ab[j][0],ab[j][1]^1),prev[j]),c[j])
		else:mj[j]=g.XOR(g.AND(ab[j],prev[j]),b[j])
		return mj[j]
	if all(x[0]==0 for x in b):
		S0=_sigma(g,a,2,13,22,False)
		for j in range(32):mb(j)
		na=g.add3(t1,S0,mj,delta)if delta else g.addm(t1,S0,mj)
	else:g.ahi+=(not delta);na=g.add3(t1,lambda j:_sigb(g,a,2,13,22,False,j),mb,delta)
	return(na,a,b,c,ne,e,f,gg,ab,fg)
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
	wd=lambda i:(Y[i-VARBASE],)if i in OFFSET else(_constw(4 if i==23 else K[i]),W[i]);z,nk9=_constw(0),_constw((-K[9])&M32);st=(Y[0],z,z,z,Y[0],z,z,nk9,z,nk9);r=ROUNDS;s0f=lambda A:lambda j:_sigb(g,A,7,18,3,True,j);s1f=lambda A:lambda j:_sigb(g,A,17,19,10,True,j)
	def make_w(i):
		if W[i]is not None:return
		if i>=r-2:W[i]=g.add3(W[i-16],s0f(W[i-15]),W[i-7]);return
		if i==21:s0=_sigma(g,W[6],7,18,3,True);v=sum(s0[b][1]<<b for b in range(32));g.ahi+=1;W[21]=g.add2c(Y[6],s1f(W[19]),(PREFIX_WORDS[5]+v-K[14])&M32);return
		if i>=24 and not _ADD_HINTS[g.ahi]:g.ahi+=1;s=g.add3(W[i-16],s0f(W[i-15]),s1f(W[i-2]),0,W[i-7][0]);W[i]=g.add(s,[ZERO]+W[i-7][1:]);return
		w_m7=(Y[i-15],_constw((-K[i-7])&M32))if i in(17,21,22)else((g.split[tuple(W[16])][0],_constw(g.split[tuple(W[16])][1]))if i==23 else(W[i-7],));W[i]=g.addm(W[i-16],_sigma(g,W[i-15],7,18,3,True),*w_m7,_sigma(g,W[i-2],17,19,10,True),force_bb=2 if i==23 else None)
	for i in range(9,r):
		if i>=16:
			if i==19:make_w(19);make_w(21);s23=g.add3(s0f(W[8]),g.split[tuple(W[16])][0],s1f(W[21]),2);cv23=(4-K[23])&M32
			elif i==23:W[23]=s23;g.split[tuple(s23)]=(s23,cv23)
			else:
				make_w(i)
				if i==31:make_w(32)
		if i<r-NTAIL:
			st=_rnd2(g,st,wd(i))
			if i==23:s_r,cv_r=g.split[tuple(W[i])];W[i]=g.add(s_r,_constw(cv_r))
	if TAILB:a6,a7,a8,a9,e6,e7,e8,e9,prev,hg=st;T5,fg,_=_t1hg(g,e6,e7,e8,e9,hg,(_constw(K[r-6]-1),W[r-6]));e5=g.add(a9,T5,ONE);mj=[g.OR((ab[0],ab[1]^1),a8[j])if(QM>>j)&1 else g.AND(ab,a8[j])for j in range(32)for ab in(g.XOR(a6[j],a7[j]),)];Q=g.add(T5,mj,ONE);T4,fg,_=_t1hg(g,e5,e6,e7,e8,fg,wd(r-5));e4=g.add(a8,T4);e3,fg=_ch3(g,[_sigma(g,e4,6,11,25,False),a7,W[r-4]],e7,e4,e5,e6,fg,K[r-4]-2);e2,_=_ch3(g,[a6,W[r-3],_sigma(g,e3,6,11,25,False)],e6,e3,e4,e5,fg,K[r-3]-2);X=g.addm(W[r-2],_sigma(g,W[r-4],17,19,10,True),e5,[g.OR(e2[j],e4[j])if(XM>>j)&1 else g.AND((e2[j][0],e2[j][1]^1),e4[j])for j in range(32)]);Y_out=g.addm(W[r-1],_sigma(g,W[r-3],17,19,10,True),e4);bw=[e3,e2,a7,a6,Q,T4,X,Y_out];out=[bw[PERM[k]]for k in range(8)];assert g.ahi==len(_ADD_HINTS);return g,[t for w in out for t in w]
MAX_NODES=54372;MAX_RECORDS=54115;CSE_PROBE_LIMIT=8
class BGen(Gen):
	def __init__(self,n,run,pas):self.n,self.run,self.pas,self.calls=n,run,pas,0;self.ahi=0;self.inputs=[(j+1,0)for j in range(n)];self.nn,self.rn,self.ncse,self.mp=n+1,0,0,0;self.recent,self.cse_k,self.cse_v=[None]*8,[0]*1024,[None]*1024
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
			key=({"x":1,"a":2,"o":3}[op])|(a<<2)|(b<<11);p=((key*2654435761)&M32)>>22;prb=1
			while self.cse_k[p]:
				if self.cse_k[p]==key:self.mp=max(self.mp,prb);return self.cse_v[p]
				p=(p+1)&1023;prb+=1
				if prb>CSE_PROBE_LIMIT:self.run.err=16;return 0
			self.mp=max(self.mp,prb);self.ncse+=1
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
class BoundedEmitter:
	def __init__(self):self.uses,self.err,self.records=[0]*MAX_NODES,0,[]
	def emit(self,op,d,a,b):
		if len(self.records)>=MAX_RECORDS or max(d,a,b)>=1024:self.err=5;return
		self.records.append((op,d,a,b))
	def take(self,pf=None,p=0):
		r=pf if pf is not None and self.free>>pf&1 else _pick(self.free,p)
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
		g0,out0=_net_u(lambda n:BGen(n,self,0));nodes,self.calls=g0.nn,g0.calls;self.onode=[x[0]for x in out0];self.oneg=[x[1]for x in out0];self.order=sorted((n,i)for i,n in enumerate(self.onode)if n)
		for n,_ in self.order:self.uses[n]+=1
		self.f0,self.f1=self.order[0][0],self.order[32][0];self.free=sum(1<<r for r in range(REGISTERS)if r<256 or r>=512);self.pend=sum(1<<(256+i)for i,n in enumerate(self.onode)if n);self.reg={n:INREG(n-1)for n in range(1,257)};self.oreg,self.co=[0]*256,0
		while self.co<len(self.order)and self.order[self.co][0]<=256:n,i=self.order[self.co];self.oreg[i]=INREG(n-1);self.co+=1
		for n in range(1,257):
			if not self.uses[n]:self.free|=1<<INREG(n-1)
		g1,out1=_net_u(lambda n:BGen(n,self,1));self.calls+=g1.calls;self.mp=max(g0.mp,g1.mp);assert out1==out0 and self.mp<=CSE_PROBE_LIMIT;todo=[(i,self.oreg[i])for i,n in enumerate(self.onode)if n and self.oreg[i]!=256+i];moves=0
		while todo:
			srcs=[s for _,s in todo];k=next((k for k,(i,s)in enumerate(todo)if 256+i not in srcs),None)
			if k is None:s,t=todo[0][1],self.take();self.emit(4,t,s,0);moves+=1;todo=[(i,t if r==s else r)for i,r in todo]
			else:i,s=todo.pop(k);self.emit(4,256+i,s,0);moves+=1
		for i,n in enumerate(self.onode):
			if not n:self.emit(5,256+i,self.oneg[i],0)
		top=max(max(r[1:4])if r[0]<=3 else max(r[1:3])if r[0]==4 else r[1]for r in self.records)+1;q=sum(self.oneg[i]<<(32*(7-i//32)+i%32)for i in range(256)if self.onode[i]);counts=[sum(r[0]==op for r in self.records)for op in(1,2,3)];info=(len(self.records),top,nodes,self.calls,moves,self.err,*counts,4*MAX_RECORDS,COUNTERS,MAX_NODES,GEN_STATE_BYTES,len(_ADD_HINTS),GEN_CONSTANT_BYTES);return info,q,self.records
def _encode_body(records):
	out=bytearray()
	for op,d,a,b in records:assert 1<=op<=3 and max(d,a,b)<1024;out+=((op-1)|(d<<2)|(a<<12)|(b<<22)).to_bytes(4,"little")
	return bytes(out)
def bounded_check(pr):info,q,records=BoundedEmitter().run();py=[({"^":1,"&":2,"|":3,"M":4,"S":5}[o],d,a,b)for o,d,a,b in pr.recs];assert info==EXPECTED_EMITTER_INFO;assert q==pr.qint==POLARITY_Q and records==py;assert hashlib.sha256(GEN_C.encode()).hexdigest()==STATIC_C_SHA256;stream=_encode_body(records);digest=hashlib.sha256(stream).hexdigest();assert len(stream)==4*pr.instr and digest==STATIC_SLP_SHA256;return info,digest
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
_TM={1<<k:sum(1<<c for c in range(256)if not c>>k&1)for k in range(8)}
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
LAMBDA=Fraction(497,1000);CUTLOSS=Fraction(15,100000);TAIL_AGES=1e-6;CMAX=7;CUT_HALT_ORDER=CMAX+1;P_MIN=0.390000001;GRAIN=10**21;STAGE1_PLANES=20;LOOP_OPS=3;HIT_OPS=2800;EVENT_OPS=3800;CUT_OPS=4200;SLICE_OPS=1300;RECOVER_EXTRA=76;INSTR_BYTES=5;BODY_BYTES=4;REC_RECORD_BYTES=5;GEN_INSTR_BYTES=36;HANDLER_CODE,SETUP_CODE,RECOVERY_CODE=1000,160,94;REGISTERS=871;REGFILE=REGISTERS*32;COUNTERS=16384;ARRAYS=(2*ROUNDS-16)*32;KEYB=48;SLOTB=KEYB;MEM_LIMIT=1<<20;ADVICE=0;KAPPA_256=35;KR=Fraction(63,5);KCHK=8192;CHK_OPS=80;PROBE_OPS=100;WASM_RUN_OPERATORS=111312814;WASM_OPERATOR_FACTOR=2;WASM_EMITTER_INSTR=9467;GEN_STATE_BYTES,GEN_CONSTANT_BYTES=EXPECTED_EMITTER_INFO[12],EXPECTED_EMITTER_INFO[14];SETUP_FIXED=256*3100+20000;OFFSET_SEARCH_EVALS=64+1+3*192+1000;SELECTOR_THREE_WORD_SITES=35;SELECTOR_FOUR_WORD_SITES=23;SELECTOR_ALTERNATIVES=SELECTOR_THREE_WORD_SITES+SELECTOR_FOUR_WORD_SITES*10+2;SELECTOR_SEARCH_EVALS=1+2*SELECTOR_ALTERNATIVES;SEARCH_EVAL_OPS=1<<48;OFFSET_SEARCH_OPS=OFFSET_SEARCH_EVALS*SEARCH_EVAL_OPS;SELECTOR_SEARCH_OPS=SELECTOR_SEARCH_EVALS*SEARCH_EVAL_OPS;CFG={16:dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),18:dict(s1=2,W=0,Tp=1,kappa=12,Sb=4),256:dict(s1=20,W=102,kappa=KAPPA_256,Sb=1<<48)}
def stage1_ops(pin,s1):p=sum(not x for x in pin[:s1]);n=s1-p;return max(p-1,0)+max(n-1,0)+((2 if p else 1)if n else 0)+3
def stage1(planes,s1,pin):
	nz,pos,neg=0,[planes[j]for j in range(s1)if not pin[j]],[planes[j]for j in range(s1)if pin[j]]
	for q in pos:nz|=q
	if neg:
		a=ALL
		for q in neg:a&=q
		nz|=a^ALL
	return ALL^nz
def inflight_m(l=LANES,e=TAIL_AGES):
	m=l
	while exp(-l*(m/l-1-log(m/l)))>e:m+=1
	return m
INFLIGHT=inflight_m()
def _plan(n,Tp,kappa,tmax,Sb):
	c=CFG[n];s1,W=c["s1"],c["W"];N,D=1<<n,s1+W;L=Fraction(1<<D,Tp)
	if n==256:B=_b256(Tp,tmax,kappa,Sb)
	else:ureq=isqrt(2*N*LAMBDA.numerator//LAMBDA.denominator)+2;num,den=ureq+INFLIGHT*L+1,CUTLOSS.denominator;q=-(-(num*den)//(den-CUTLOSS.numerator));B=-(-q//LANES)
	cc=-(-kappa*L.numerator//L.denominator);fb=(Tp-1).bit_length();cr=-(-(KR*L.numerator)//L.denominator)if n==256 else cc+Sb;kchk=table_bytes(tmax)//64-1 if n==256 else KCHK
	if n==256:assert kchk>=1 and(kchk+1)*64<=table_bytes(tmax)
	return dict(n=n,s1=s1,W=W,D=D,Tp=Tp,fb=fb,kb=min(KEYB-fb,n-D),L=L,N=N,Q=B*LANES,B=B,kappa=kappa,Sb=Sb,c=cc,capr=cc+Sb,cr=cr,kchk=kchk,tmax=tmax,e2max=2*B*LANES//(1<<s1)+64,cmax=CMAX if n==256 else 10**9)
def tail_log2(mean,k):return(-mean+k*(1+log(mean/k)))/log(2)
_PROG=[];_QM=[0]
def prog():
	global REGFILE
	if not _PROG:_PROG.append(Prog());REGFILE=32*(_PROG[0].nregs+3)
	return _PROG[0]
def machine_constants(pr=None):pr=pr or prog();filt=stage1_ops(pr.pin,STAGE1_PLANES);code=pr.instr*BODY_BYTES+rec().instr*REC_RECORD_BYTES+(filt+LOOP_OPS+HANDLER_CODE+RECOVERY_CODE+SETUP_CODE)*INSTR_BYTES;return pr.kernel,filt,pr.kernel+filt+LOOP_OPS,code,8*(MEM_LIMIT-code-REGFILE-COUNTERS-ADVICE-ARRAYS)//SLOTB-LANES-CMAX
def table_bytes(tmax):return-(-(tmax+LANES+CMAX)*SLOTB//8)
def boundary_test(pr,p):st=_encode_body([({"^":1,"&":2,"|":3}[o],d,a,b)for o,d,a,b in pr.recs]);mk=(((1<<p["kb"])-1)<<p["fb"])|(p["Tp"]-1);rp=rec();ct=rp.init+rp.flat;assert len(st)==4*pr.instr and 0<mk+1<1<<KEYB and p["tmax"]+LANES+CMAX<1<<18 and len({r[0]for r in ct})<=16 and all(max(r[1:])<1024 for r in pr.recs+ct);return dict(body_bytes=len(st),max_register=max(max(r[1:])for r in pr.recs),max_key=mk,max_trail=p["tmax"]+LANES+CMAX-1,control_opcodes=len({r[0]for r in ct}),control_max_field=max(max(r[1:])for r in ct))
def search_envelopes():gate_ops=1024;raw=2*160*64*32*13*13*12*gate_ops;assert 2*raw<SEARCH_EVAL_OPS;assert OFFSET_SEARCH_EVALS==1641 and SELECTOR_ALTERNATIVES==267 and SELECTOR_SEARCH_EVALS==535;return raw,raw
def plan(n,kappa=None,Tp=None):
	if n!=256:c=CFG[n];p=_plan(n,c["Tp"],c["kappa"],0,c["Sb"]);p["tmax"]=4*(p["Q"]//int(p["L"]))+64;return p
	kappa=kappa or KAPPA_256;tmax=machine_constants()[4]
	if Tp:return _plan(256,Tp,kappa,tmax,CFG[256]["Sb"])
	lo,hi=1.0,float(tmax-59)
	for _ in range(60):mid=(lo+hi)/2;lo,hi=(mid,hi)if tail_log2(mid,tmax-59)<=-20 else(lo,mid)
	a,z=1,4097
	while z-a>1:m=(a+z)//2;a,z=(m,z)if _lossq(m,lo,tmax,kappa,CFG[256]["Sb"])["P_lower"]>=P_MIN else(a,m)
	return min((_plan(256,t,kappa,tmax,CFG[256]["Sb"])for t in(a,a+1)),key=lambda p:(p["B"],p["Tp"]))
def rec_ops(p,pk):D=-(-p["cr"]//p["kchk"]);return p["cr"]*(pk+RECOVER_EXTRA)+p["kchk"]*CHK_OPS+17*D*(pk+RECOVER_EXTRA)+16*PROBE_OPS+600+len(rec().init)
def ledger(p=None,pr=None):p=p or plan(256);pr=pr or prog();search_envelopes();ph,filt,body,code,_=machine_constants(pr);emitter=WASM_OPERATOR_FACTOR*WASM_RUN_OPERATORS+1;parts=dict(main=body*p["B"],slices=-(-p["B"]//p["Sb"])*SLICE_OPS,stage1_hits=p["e2max"]*HIT_OPS,events=(p["tmax"]+1)*(EVENT_OPS+6*(p["tmax"]+LANES+CMAX)),cuts=p["cmax"]*CUT_OPS,recovery=rec_ops(p,packed_ops()),setup=SETUP_FIXED+emitter,offset_search=OFFSET_SEARCH_OPS,selector_search=SELECTOR_SEARCH_OPS);return dict(parts=parts,total=sum(parts.values()),plan=p,body=body,emitter=emitter)
TB=18;FINE,COARSE=20000,2000
def _lossq(Tp,q,tmax,kappa,Sb,rate=1.0):
	D=122;L=Fraction(1<<D,Tp);c=-(-kappa*L.numerator//L.denominator);th,Lf,cf=Tp/2.0**D,float(L),float(c);Q,B,Np=q*Lf,q*Lf/LANES,2.0**256/rate;k=int(q)+1
	while tail_log2(q,k)>-40:k+=1
	n2,shift=k+LANES+CMAX,1/(1-k*Q/Np);pi=lambda m:exp(-m*(m-1)/(2*Np));split=max(1.0,Q-120*LANES*Lf);edges=[split*i/COARSE for i in range(COARSE+1)]+[split+(Q-split)*i/FINE for i in range(1,FINE+1)];delay,pa=0.0,1.0
	for b in edges[1:]:pb=pi(b);delay+=(pa-pb)*exp(-th*max(0.0,B-b/LANES));pa=pb
	p,ql,hq=exp(-cf*th),Q*Lf/Np,Q*(Q-1)/(2*Np);p2=exp(-(cf-1)*th)*(1+(cf-1)*th/(1-th));kr=float(KR)*Lf;prec=2*hq*exp(-(kr-1)*th)*(1+(kr-1)*th/(1-th));hh=(Q*(Q-1)/2+2.0**TB*Q)/Np;cuts=1-sum(comb(n2,j)*p**j*exp((n2-j)*log1p(-p))for j in range(CUT_HALT_ORDER));t=dict(no_collision=pi(Q)*shift,delay=delay*shift,partner_own_trail=ql,partner_cut_trail=(cf+Sb)*Q*p*(q+LANES)/((1-p)*Np),too_old=hq*p2,P_rec=prec,rest_of_path=hq*Lf*(Q+2.0**TB)/Np,finished_count=2.0**-40,cut_halt=cuts+ql*(1+(2+kappa)*exp(-kappa/2)+2*hq)+hq*p*(3+2*kappa),key_false_match=tmax*(tmax-1)/2*2.0**-(min(KEYB-(Tp-1).bit_length(),256-D)+log2(Tp)),table_capacity=2.0**tail_log2(q,tmax-59),misc=Q*2.0**TB/Np+k*k*Lf/Np+255*Q/Np+exp(min(700.0,-300+(exp(5)-1)*hh))+2.0**-90);t["sum"]=sum(t.values());t["P_lower"]=1-t["sum"];t.update(trails=q,k=k);return t
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
class Halt(Exception):pass
class DigestNet:
	def __init__(self,qint):
		assert TAILB;g=Gen(256);E=[[(g.inputs[32*(7-k)+j][0],(qint>>(32*(7-k)+j))&1)for j in range(32)]for k in range(8)];S0=lambda x:_sigma(g,x,2,13,22,False);S1=lambda x:_sigma(g,x,6,11,25,False);mj=lambda a,b,c:[g.XOR(g.AND(g.XOR(a[j],b[j]),g.XOR(b[j],c[j])),b[j])for j in range(32)];ch=lambda e,f,gv:[g.XOR(gv[j],g.AND(e[j],g.XOR(f[j],gv[j])))for j in range(32)];neg=lambda x:[(s[0],s[1]^1)for s in x];bw=[None]*8
		for k in range(8):bw[PERM[k]]=E[k]
		e3,e2,a7,a6,Q,T4,X,Y=bw;a5=g.addm(Q,[ZERO if(QM>>j)&1 else g.AND(a6[j],a7[j])for j in range(32)],neg([g.AND((a6[j][0],a6[j][1]^1),(a7[j][0],a7[j][1]^1))if(QM>>j)&1 else ZERO for j in range(32)]),_constw(1),S0(a6));a4=g.addm(T4,S0(a5),mj(a5,a6,a7));a3=g.addm(e3,neg(a7),_constw(1),S0(a4),mj(a4,a5,a6));a2=g.addm(e2,neg(a6),_constw(1),S0(a3),mj(a3,a4,a5));t1=g.addm(X,[ZERO if(XM>>j)&1 else g.AND(e2[j],e3[j])for j in range(32)],neg([g.AND(e2[j],(e3[j][0],e3[j][1]^1))if(XM>>j)&1 else ZERO for j in range(32)]),_constw((1+K[ROUNDS-2])&M32),S1(e2));e1=g.add(a5,t1);a1=g.addm(t1,S0(a2),mj(a2,a3,a4));t0=g.addm(Y,S1(e1),ch(e1,e2,e3),_constw(K[ROUNDS-1]));st=[g.addm(t0,S0(a1),mj(a1,a2,a3)),a1,a2,a3,g.add(a4,t0),e1,e2,e3];cv=[g.addm(w,_constw(v))for w,v in zip(st,IV)];a,b,c,d,e,f,gg,h=cv
		for kw in _KW2:t1=g.addm(h,S1(e),ch(e,f,gg),_constw(kw));t2=g.add(S0(a),mj(a,b,c));a,b,c,d,e,f,gg,h=g.add(t1,t2),a,b,c,g.add(d,t1),e,f,gg
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
	if not _DN:_DN.append(DigestNet(prog().qint))
	return _DN[0]
class Engine:
	def __init__(self,n):self.n,self.pr,self.pin=n,prog(),[0]*n
	def _low(self,o):return digest_of_g(o,self.pr.qint)&((1<<self.n)-1)
	def step(self,*planes):return dnet().step(list(self.pr.step(*(list(planes)+[0]*(256-len(planes))))))[:self.n]
	def wstep(self,P):n,a,ns=self.n,(1<<256*len(P))-1,self.pr.ns;W=[sum(q[j]<<256*i for i,q in enumerate(P))for j in range(n)];ns["ALL"]=a;o=dnet().step(self.pr.step(*(W+[0]*(256-n))),n,a);ns["ALL"]=ALL;return[[(x>>256*i)&ALL for x in o]for i in range(len(P))]
	def f2(self,xs):return[self._low(o)for o in packed_f(xs,256,self.pr.qwords)]
	def g_scalar(self,x):return digest_of_state(state_words(words_of(x)))&((1<<self.n)-1)
def is_dp(x,p):return x&((1<<p["s1"])-1)==0 and(x>>p["s1"])&((1<<p["W"])-1)<p["Tp"]
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
				if is_dp(xs[i],p):ls[i],ends[i]=k,xs[i]
		if None not in ls:break
	else:raise Halt()
	a=0 if ls[0]>=ls[1]else 1;lb,(qd,rd)=ls[1-a],divmod(abs(ls[0]-ls[1]),D);A=lambda i:walk([ck[a][i+qd]],rd,f2)[0]
	if ends[0]!=ends[1]or A(0)==ck[1-a][0]:return None
	lo,hi=0,lb//D+1
	while hi-lo>1:mid=(lo+hi)//2;lo,hi=(lo,mid)if A(mid)==ck[1-a][mid]else(mid,hi)
	x,y=A(lo),ck[1-a][lo]
	for _ in range(min(hi*D,lb)-lo*D):
		fx,fy=f2([x,y])
		if fx==fy:
			if p["n"]==256:s0,s1=enc_invert(words_of(f_scalar(x))),enc_invert(words_of(f_scalar(y)));assert s0==s1==state_words(words_of(x))
			return x,y
		x,y=fx,fy
	return None
	for _ in range(b[1]+1):
		ya,yb=f2(xs)
		if ya==yb:
			if p["n"]==256:s0,s1=enc_invert(words_of(f_scalar(xs[0]))),enc_invert(words_of(f_scalar(xs[1])));assert s0==s1==state_words(words_of(xs[0]))
			return xs[0],xs[1]
		xs=[ya,yb]
	return None
def search(eng,p,r,cnt):
	g,x=_search(eng,p,r,cnt),None
	try:
		while True:x=g.send(x and eng.step(*x))
	except StopIteration as e:return e.value
def _search(eng,p,r,cnt):
	n,mask,pin=p["n"],p["N"]-1,eng.pin;table,births,ts,nxt=[],[0]*LANES,list(range(LANES)),LANES;planes=pack_lanes([(r+t)&mask for t in ts],n,pin);cnt["inserts"]+=LANES;batches=0
	while batches<p["B"]:
		planes=list((yield planes));batches+=1;cnt["batches"]+=1;hit=stage1(planes,p["s1"],pin)
		while hit:
			cnt["stage1_hits"]+=1
			if cnt["stage1_hits"]>p["e2max"]:raise Halt()
			l=(hit&-hit).bit_length()-1;hit&=hit-1;x=lane_value(planes,l,pin,n)
			if is_dp(x,p):
				key=dp_key(x,p);cnt["finished"]+=1;w=key+1
				if w in table:
					t0=table.index(w);cnt["recoveries"]+=1;res=recover(p,r,t0,ts[l],eng.f2)
					if res is None:raise Halt()
					return res
				if cnt["finished"]>p["tmax"]:raise Halt()
				assert 0<w<1<<KEYB and ts[l]<p["tmax"]+LANES+p["cmax"];table+=[0]*(ts[l]+1-len(table));table[ts[l]]=w;ts[l],nxt,births[l]=nxt,nxt+1,batches;planes=set_lane(planes,l,(r+ts[l])&mask,pin,n);cnt["inserts"]+=1
		if batches%p["Sb"]==0:
			for l in range(LANES):
				if batches-births[l]>=p["c"]:
					cnt["cut"]+=1
					if cnt["cut"]>p["cmax"]:raise Halt()
					ts[l],nxt,births[l]=nxt,nxt+1,batches;planes=set_lane(planes,l,(r+ts[l])&mask,pin,n);cnt["inserts"]+=1
	return None
class Counters(dict):
	def __missing__(self,k):return 0
def derive(seed,tag,bits=256):return int.from_bytes(hashlib.shake_256(("%s/%s"%(seed,tag)).encode()).digest((bits+7)//8),"little")&((1<<bits)-1)
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
		c=d&((1<<B_T2)-1)
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
	r0,ends,ckok,pairs=r.getrandbits(N_T3),{},True,0
	for t in range(400):
		xx,l=(r0+t)%q["N"],0
		while l<q["cr"]:
			xx,l=e.f2([xx])[0],l+1
			if is_dp(xx,q):
				if xx in ends and pairs<20:aa,bb=recover(q,r0,ends[xx],t,e.f2),recover(q,r0,ends[xx],t,e.f2,3);ckok&=aa==bb and(aa is None or(aa[0]!=aa[1]and e.g_scalar(aa[0])==e.g_scalar(aa[1])));pairs+=aa is not None
				ends.setdefault(xx,t);break
	assert ckok and pairs>0
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
	elif arg=="--ledger":print_ledger(ledger())
	elif arg=="--gen-c":sys.stdout.write(GEN_C)
	elif arg=="--loss":
		for k,v in loss(plan(256)).items():print(k,v)
	else:json.dump(serve(json.load(sys.stdin)),sys.stdout)
