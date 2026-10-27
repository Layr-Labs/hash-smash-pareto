# UTF-8; organizer-executed experiment only. Do not run on the host.
import base64
import hashlib
import json
import sys
import zlib

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
BLOB = 'c-lpq+0G=raYWx`u64nE@v9hukz|s0mH<lz3>bcQpQx^G8OE=fZ>cVlnGq*Q&j0@TufPBI-~2!J-~aZHf7;*v`Hw&U_V54xC;U%t!F%bU#du23o@>4>joX{Y7;Y}7$Jo-%F@(H&sJ-T~Q=P4(mP7vY7ao$9ty#R=Nhx{E)py=)*L&7A%dyNbY^NL3Stqo+eD#uIUbp2q#(EwSYuGd2b6ZV!#hum-`9w?8Z1l)CdOzKJZoTnr4>M1niTBz3ZI3^H{mV0;#9&%HZOk-Qwppw5|Eo6NweJ}C@n9{)63>|B#KK^FpPG9gX{F~~dcKVMh7wacsajaw?kOiR{xs(*q3_(oO{-emd!KpNym#kP?XGuHET^;UF6Y!0N9GBam)`L*#r5)1du~t6yq%f1jkC;qySv9)i+{(%aB^zr1V($~Jgvr)Ha}GY>$I)q;;G!-c+Wa7^FQ`pC(U&3Ip&{t>ASIDwp-4NKRWXe?&)`5t7XPvcg(u>36WJA$wC{9hUprNzn9MfEx$e%GZ*6S!94X_d!B8M8PoJ0!-;n_YN0nPb#9BJ=>g6Az4ILq)nu`3YHHe;Ys9jqH=BDD_twWPmkP;u24*4myhmnCiE@jU>#@&(JkETA%JkIHRx*C6&yyoB#juSvj+#o%RoMLC<Poj)RaaYQKMyHo8`V&3RLY7sX|o*`K9tjX;XTg1Bh69f4E%|bTel8M&5GG9-|_5a6hiLNnO_^xL#esM=J}*t_ZmJ=@<I#o%ywIxqmRm4d0W%&XKuZ&)O&9;ZHjD#({`CoaqznJmPCaVTOp6@YtdeX(f6hfy@x6IOv;&b*0SuL%erd4P;*^QhfnKto=x)=Hr;V23(&%uJ@SH#K9u{dI6slDY!q#Xk-}WOoSn?<Op5>dDd8@yYAAh$8Zu3g={bt8#J8Ihug7!x2y0jm9(YDE+G>>OoAsnh@}xV;Txar}J?9vsESt@GiqAuCoBRT0kixdG8Te}1d7b3u)KLwk1e=r(A9C|Z^%Qgiaha)Z`;O<VxKb^V%80%3GLJ&FOw)#GrP2J6FNMye_?gtf4s{k<i88O}vp}(K5A;RJn_eGiVA+cb%GXxm({FAxR`k@UsN`!b^-GyGFGl+*IKGFR<=a=<r6rb^&d7bN$>7^qYt`;_d7-jr9p;A>XffreqT2qgxV~;&s))^^qL4OnFk?c{tL+qPY?SJ}l>cnBUQJ;-eU{45Og`^IU6g3uHid~W@|1E%sf}gcl=?+*HY;0r`+Yr+Q1@szp}<?k_^G(OVi_Uu&BWW}S#m{@=PX0Z%2G;SJ+HHp^M9u!L9sTw{2*F*zALnM8!{M5Bd*}gS{M@SNfF^VVVpEtLBJACwNmQL%J9+4l9Id{S5^GSjd?!<fy1LBzi8KyLS~p%?({7#HfT?uk&YZYOga&FXrBSiM01Z`2i<ZGD^qXI_#H2gg@t7GPzI?l+E`1Cf#ouKz%e@O`V(z_u+ruh2Cq$<8wMM1@e=~GQ%|#YJ>pAa=2lN%i0=)QDr(l=YN2IvKyXnomK8Ok&9D=?Hno(ewL`Phq7CnL6nIhfi=|m99)9Liw+(&A9gwKY$XSN!te<ye`P7?A@r%6BW{XCs=pXiuPf~KNXWQSBTQSgAM&I6j=p3U=GL=U!N`yPzG*UzNN@5w~Ts<NXIAt3U#z*9CJgj9si@EoNI?tW_Qc!akHR5qeV+La?R9l!q4$~~)zJ4+IXHr-+TJ8piQz8q6uhQ<F2b7Gw_SvtuBcY+~H+@-Z?-haIomL88N-%_Z(e0%M+BaT|fF;_2x4;MSW&|dJFF40OYuvDQK3$H!5*q#~7Pm!%Y)bvMF&r8RLq4o`L6mA-tUJ(vxu%6%w_0)HwQa`AbUhDgzV1?q;7~Xqh0f5Jdz_e(LSRx^n07(x&-Ieqz+P<QIP~nv?|9lk14{$5?9fRYcFFTtoUCD^Wrinp-^rf#Jlk-7Ts1xGKK%nMNVs^7sWAFobHPvsqr-FV-jr%X%DrRq5oI>uM_;cXQH8MX+d#5#1}cy^I7M-a7;T~Bz@FBbs^$Z0qw)fD)z(gF9??g~a=r}|8w7&**$53G@;VmF7+7XF^2CiX)0MQfZxpbAZ)J~h`CrFd&-*S;w@v!laEgX7Kuxq;M&qrwaX_bI6-l2wa<Y_1PRsIVRv>%|F5c-fT*MK$KprWgjLtB=m0`yfu_W9+ROc~s_728YN+kFgRP;{~I?D#|`8A)F)<eZ7ZF&%7AqfQrYcPOA|2L|k7y`a?ZpU6Kjr(l0mJSaEBdnd8Yj`NMJ97e6uh9e48}POJpfy9Pt#(7hjSu=f1SU!Je}!3X?buV`)yg<`bmZ(DM{d&|lqH?k7}Y?`py+8KThBia;vunA%1QEs)6rjp$5dVk_z;FcB6adXr=J=^?BX+{3~IkGQ9_RnWnf(aeNi<5*u30nd^8RmnRlQF%uFLACp4Uj$~R8kQhH?)NyMm}*`*kZf#Vr@j7%X-*HzIIqC6{@)V7B-X`vKw=}^YcRBJwbY(W*F%$%tj=9X}wBI=jg!pNE4iR?q(>d>`;PIMEy+#e6xr7p}8aWpy~Gp(eS(^(d&jKs|xg)HDU?}5I7lL+xr^k7DxXBd=?g0ONthN;2^njI)O78)EdN9>^60pHboVQxN#wyyE^oJ0Q#9NvQ2B7(k*G&Z*L0c{~a%)&t+2NW`H#BdKLZ;Uh3ZL3$vwdI%iN9mX?6O|6VL0UMQbx#!i82O?Ni#nGYpl4llxKAm^3O_W?2jcRMkQ06HSRRJ6z-XeAB~;_A1~+v?sTKhyfo8(F71@B2nF*TdyFMgUxQ`*MtXR+nRfMIlbOe;F7eyo&29cp6)csKBhVxT1q1)?*d(vx1u3}UxgLm{|8eKsu@xDZNYxJzp1qk-G;ks0K46pfu29)}k<VEK;R&0x6cY@2DCZ^<JOfFamhdq?n&)Hf?vRc^R+_3A!ha>%g{WSdZkZ~9_>&sV3c>G>ZOdfL)4FiujHC4MOjXqunS{LVoJE&yb=x*j1DaLnzH~<jf8=aD4El^KZOWBhU6t(*CWw<EaB&DKW^vV)%KubvV4FSt5dJ>5e77u4YcS|HpD<k84HT?vEV9WZ^6BViK)iN<~Z1~U-sF>~28=XiA9ux7&(~!Gis9?ve@A@Qkq*p~9CFvarWJC(yT%ANdfNwKCilhWufe#5(|3Z0qdot8#K&bsZgy_9GhQ`8RU>HUqDww2|SazZrxua3hWUXEtN^O(av-&Tm67Q`Eg$um5M<lIc@JFd*=LPRz{R1K{R8hmh292_5`u+g(M{R*l%A(IeXyjL;69%&*Qfo%OP=ON^CWDxa18f^qan~$PS1f-?oyvhReBc(Dsz#YB!Nez?WFju=<+%0;7!BG<sOcr-LJ?tw-xvhavYJ!|kr4vq@s$Xu=o%rdytR>lS|m)1_}<WZ5(olEpI}ojePvQRGRsUIcpf_=Yg|-!k<FQyKzxNl#eZ^hsw2XzXcLx{QQgl&0+Ms+H6#@+ih~AAssfipLR=HAz*tOZ0K+rcld?IP-`gqv94Nz``%rBJ2Z+ZaodH+^&>>y;V`c@)gt^h)*voAgc2;i`g7SVHXy!;X0LB}31&8Ha>G_c)BjoFz7NUs3O`=aqtyHoNtHrBIEj|MhTQTL>@!lQJyEGFqe$#uX2KkC$h)!;#!ZzaF6og%r2x!D_XvmeUge{W_*V4~Zw>Kj#2`%L>E=cJ3+37HtGw26&9l>4&H2)M!KnrONhGpmtIX`0D0pq0iAIB&l5?>CioMr|?>`W4~X)s@ZqZGmfAy?H&WCqa-{T<@QN%US5&tQef5M)+}naoaJ=3{}v(0&5~Nzt$59h;xpy<s`QXq6>ek9gCob8CBrW=Fgm>;q;Rf;G-tai|1LtS9uUorsMpQG6i1c7XW62pbS2su=Z9^9yx^VM!5vyv#!}_fZWM!ki{#O1!r~Xn~y~Q&SlTs}E}-^ay*TsW;L5GIeC0?|7!N4~eY1N&uE*L67LvXh3KQ?dHpaPAZ5adH#liDAK=&DW0EqfzVOhi~+NVB&+~k2N{KsF(nw3&kO?;1HC-uRe3gmhVJq{{yv1-+^BKkXZh`c3ywfx733}-aub@AAL*;G-+<4V_dvN#W<CFQdL*Ek3}o)6%-6_~q~DD>!`K_uRB+VpLJf(qm9%BXxL4=5MtpaAs-cxkOQoBaIBT2&@*zD-vdbUgDqbFqEBw?j>T7GGaB8wX1JZWk8boFyRMBP}JqrB7L7=TDrBHwbHWqFjLNH^|w#vB&x&6f;s@YCOfV}fTR0CqP6^KqO##|9r5nIUpUirLNh#Eel=?8!q*V{s~59p%;epClDuju}4*`O?gPAPd1XegjG5(Y$!;ib@RmF>ILli}~#DaAcnp<`>0Fy8g4-KIjE!xR?6%|q!D5&`glQ=ZWnaJcnfdsl&y?Svd22L<x+1W7U}>c>PoI(soX$dFb=96NOkuJ=g0pnh+#Bd1^ohsC~)h9;1qmaH)=DYT@PAi&a<Ee|h9{(}{7H0}4S@a|n{_uv+sMG%`X0mcG6DZS%sggd~%s0AR1^m?`f-z-MOUH-Mz6H#$|3`k5fkqzUOgOhj==m9mmwxA=lSt?jE_-&S(-nv9TV$QqK8L`{mb0=~!jieG)GIE3n)Q&5`88h!au-~OMKQ<W1hEPHB8eT4S6r^gQd2NckD0I-4tO;*I;{h1Sy=$;*mAMuFzya*cNel0Q7$NRKQIT3SZ4^bJ>bjBZ^e9u(?aJ(ZSF@zaKCxZK-~_^#v$d~?k5|e~CmK5Cn1zqWaln1Zon+LN)HAg^3-5-7Z1Et0)ZemQgO#6ywWJO$LDpH;oW@9Uj&Vh&<RX${R0ppdDP4g{z3t1{un}~UdmL!fvO>CrF?%~Sr}n*B{2r-DME@wP9c^hdMc_{%#JvX6XQjC?oPu^k`n-6+c7yikka61t?$Qbc&+OcEH!qF|FPNB4eS-t-x9M7)(~u9*<5q7%qNw6R(y~Sd*t{N8FM{3La0=74ZHK^ow|Y8dUP-o3zYxb{4@ZYX#9Yi3ien_S0bznB!<-J_foT^!@#i0WJ;?dB<tVoR9?Px~>EVq@F@@}|O@1m{ks<&H4o%TC(9P!|>KhE?PH@;1u4xTC7+7*tj5WgaiO+EU3YCz9?4S&4W}3i$f}kDsiJq(qX=(?suwD^uL#~l1#v#ujZUR};sOmt5g13k>*kbq+at|PHM@R{i)V!<#A)pnDlHe{bK?FTY2~;WnK~=*f?9#5Eot_N~U<P|>ha_!H7(q!#N|-WhP07Ye(ZZC>KJQIz<oiH0*?av?PcTS27-fPbS#1KI3IO0kZ_xSxPb}Px+NKWq_8Hpe={@Mw^4-(OI%^PgQD~PrYqyq0<PoUP-Ec3kupB?)F!WN<5Vbqncp%olJNy*crURqRcmi1xeLuai;MI}>Kd3<ZCM3IdX~>yjL3c=I&;Bn9LR=#d0Zt=2)X3H*X}H>9?jqzTd?O<)IN!!}5Cs^z)0K71Z^UH5(PMgLny?aoExa3WFgqA4#b!R@DycLKwVsA)lC>N!>aVCsk-$iUX0UQlMMu4n7oPMxmT`F$%_|#Dl{RI)icW=&=@_?t+b6XyL>N2hgiJ?zC;^`_2q*-dZrViF;Y3$PBRpz9i_-Oq{18z-wXbtP_-~P_A-FLNj7-ccz6A>3f}@V5V;sUQ)2Aq=@XmkH(hu3T6%`?1QR`w~G|@q7%8e<252I_zBQ#vdx`$|?qR{ah)qQ>p2Y<nj+RLOUo5waLd6WeV0HnkAi+Q>&(<~3-Gce4VnrtxQODicO&gFImTILT6>$YT?jVu_D|8T@!v><jMHgm9@89{=So<6C;8mW_Te-Y0n`>h9Ca}3^;4{@bUN7dQDg=9K1T16WZO3-Kj5H5;i*3z+fAgos%y&7{ni9vS}`}=0K$YFt{1)^_9d2&jM>13663xN3`ra+R)mEZ{aPvM?5wbjhJF%|SQ3(7Ayj0s&ra)fjV9e*zYTtAi4Cj562Vj!_cUJLV=W?-&Nqc+9iS>W=>6K@%2<t!cfegz>BhHZl4s7ZrkY9%K&avs2}jcYOz^S^Z@cI*l`m@ukIuy)dY{l`m9WKP=@fuW1=n3x;~N;*_QMfshOkUM7VHr|G1G|f~Yl)S_<r<49t1V#(|JYu7#S*hpf*$5ffHUSq8(q@{4^sF#R7vvbfqlUKe@k>bnB-*`&!3TarBp^i5*%4<2Eeot@U`7-B(^oB`8FcD9xtZjKf)j)DTsjqk%>W!E*ce;g3LoTt#A;~IxJ=tDrYhsUo0Ch&uuTD(NPvt4-Rmgu#@ek?$9L;9cEQgu9Jc|lz}e;#o)2FGV$Fd^nl|aU)Oc%n1#AOOpi-RCG0TBHl3yk<6!g%EsDVgJ=cn&JX{4XZaJ&j}#xgM;Sq~Z(Cjn?LLMlo?L({&HR~Uf-MU_r{*I1{cJ;|(TW|qj|tX8SqHpvh=YXm1dzRnBksz@6YYd$)~zVzBJq|&??3Wf`3VP%;mFew*`aJDp$mZ2G^yo9*r)R_)S0b^p;XJ*09SpiKXk)OqgdgD20Dh!=FW^#%8bkC5(mx2VcPCRU+X75gfc$m4s#rmQ=?{V>fe41cPSg%gs9UX=O)!@cWQ@dOptzJ4{d%K6=gUJA!Bv&kZcPf+D35nvq=p|7KxZA8n{@j^}+KOR0(PqT?O_#2n$AqupW2Doi_j2aq>X0>&*|9O5*)cL?ft7(uS4w~cYxli!!lD*kblCb8V@RTOo;v6{rZrSz*=mrzFk7MqW-(JNPRPG=Al9A9LrIBSHIYr4c0~?}6VYnU=!;HZp=C-KYswj=J=g)0IqG|`1!x0Zh&duMv$hYB1pMpjNJqRt(#4jY5H1xrvSrtP8|Eu&dl`_BxOT4blG#AK1l~?<o;$LVJv!|GrDOZ(HOs#iO+E`01n`V6@1&{?JWvyfOuaFWoe-o`>a3j!qM9y#TpgTZ(QzWMNO2;O@(}#tJqRi@xy**zML>HDQ@gQo&5@te)Uv_%T+oF^%9J_;{4gLX`1^+sHmV+Yz?{5D#H~nvU=4aml;iP5=h|zN9{kF^6V^^wT0j7|{Sr6o&gTMVfF8fybZP<vAO?%+MQjN2hk2#7Dh#H4svS=hg|*u6p<zC}U>wGOvNp{InfAaa$C&{GbkN{KW9^%A5<rc7NSGOL)DhV4q#KeNlrBRyy6_@&8J8HSvawo}P;$a^(mB*w3Iq&@4xwRxc@98Cy|VhfF*g}eDUuqg;nFP@#FrWZL0Z?|_0a(_U>$`vkjFRuhvi^o1d9pUy8gsU9APOugShgdBrI*5X57zcZ=rE!&ToJ3B9MD%2n=^m)V3~A0?j7K?!_2euR5XDNfQZ!h2J{Fz+Vz*MA7;A2^`a+I}2zV?x&qd!hzH(%^an;Lk#5N;f+W~Mh%rgd8`4j@F^A-0O&m9nD6Ae@L~-KBIH@+iL^Z|du<;N&xIBy6)-z--TNLUNze)0={b2NtCJt;n@$YhJodurNb8gqjSNu*{26;CuLh~z?;HpU$vR~BMgC%#MVn;EWOuB%=v)DQhz|E@?`>WSI+@ooGEVibPZbFuO}YkgcvmBZ0qhtuaZ;z!+M<Cm5I}OkBp2p=bUKgx|MpanRnUr@22Jt#4uwbE4TBOPI%s9F3Mny}>4Ai%162mpO8LnFRzl)M0V6*Q$MS@BFKUdWjVG~d(}z!m`>aCr$T}M13iNdTTljPrKLi<(33zut(=V8-i$h>#(e<|j9_cz#pj@;uNIx(z(#d!)o6y(P(S%@{_MZs=3YNMdMP7zlbi;{0ziv8ehW{wNBhkNw>icf_qEqy3#kdcgh(AFHh`JPbD1Dbw2s5tJg(o3G1d%r%h{X<`zV{3PiL9-1U63SH9NpdEi#kXkgjM*Bg~>X#ygV*nos6DGoL74#ax@-Krw}0VstOPlG6L@!XJHg!^LL%NgrKl+buF(IVmT<IJ7VAUL6%7tqh*$dY=Ry(VO%!d;={3~>Id`Mc(e09r~t8zE(gN*yVDfymQIe-tyAWMX+t5$Rb<n_9}r8nEUoJB2-=#=hc3(QM9t`$=eu2n?oo*oC<Mdt*-4<llQxi5F;jk+d`_S9ZR{~<_Z2QZovzYZ-&fv<!(%`D9J`Xy=(45z8Fk7W!iiz)Ksq$s(LpPC7PX;F8|k9A_g)@v8A<unye<gmkaevh>l#wj**nvfbkViyIt;qQhg^cUg8|dOL_4=GsHC`IE#0JIr73A%0yojd1V65r9}^myb%ve;$sA5dp6#awlw(G2$Xp@g=8;&2a1W-BZlcdA+@dpc-RA8G#e~$c1*}(5?@j)EOF25|@T${sK|5T!;;hWZD-0-l?cRZ&tJ`Bt9*P8+&@gXWptG_u(l%XZ<)&!PI-#{CEnT;4I3<4q`k>SZY2$^B24V%!p|4nDU%G5T!6ERvtGLd%E`c%Zh)Qj`N|A|;)1o#SaM7WiU5GS&uVX_l5D{G(uAHs<&C_(rE<=FN<>!c<WmJ!}`J^eOpDVj6Uqny9gs%V2M7$)1c8pHfIg`#RqBdq@kw=iFOEKO>?Mfh{Q*FYaU*5S#2Z4Rx%k1m$RA;t2SvBkpZ|u)WgO1q^snoehea<gw1Sjdd%?#$CnhYaK-F49b>DM9obK6RHwl4jI2=i2{@bHv$CY_dzRlf0uw)I{yl)mU6GCLxZ8`NJ?q7nDj%}nUBEV66BmGI@OgDGO{cY*kfwX~r-F{+l=F50^k4JJws|ElY`S_>^JY%(87XQaz@4E%0vvVM0VsDuFBsGBwDZb}@ES2rE6tzo(pO%F%j2(h6%kZLG9)%0d|fv$FzJK;9ypsC~G1<-jm&pX(lLoMC2bJPK6GYSu}b)9aWUpg(=pPCsI%o7sXB&CSzGf={F?XJU|`0N~4RsC~AmPZlnBi;VJUQWYeymwJ-*fCh(&#nU+b9K*u=I8bY7UGx=>jwA_{!(eGcRXG96)5kCVO74Z`)!gmv8SV|B$u|}5n2^r(!JXRfM`dawEsI^xD8jfU7(N);wfHlWf-bJTRC(+k^$f8UPj!rcRmaG8wE*-_MSPmZse?sqU$&j$p?)`)go2}PTrwz9WL@GR2a2Ewmqp0Ncri->lt+bR?sb-O6gVrq>XTb>j_M_3H~r0VKM2a>QF?&mr1Mbwx3-0QY(yyxaj=5B%PKcw}Xy{H|WZ|sA}4ll?R9Wd^U}Ab5l14-`#j7QI`%Hiqo;#v&r1L_C>2e9`QQ%*S5AoDffe{@B!qF)F!SN-y7-?&?2oO2MEyAzs_jdHOI|{E|qAj5}&_x@SM-}{)C_-V{K6w^QQ+uA1b}V&AQQgkk+XC^}rviO&-;zP^A%qm*~2LkFP|U7`pcN#tJZN8cah(h?8sZ4vd%_3i)@GFO=}?Jh39JLQcaVbc@gfT-V<?H;W{81>NOWB-CY$OH~ow9Hk%uVUnsJ2I`At^P0)i00yG}`_~y$Ctb`ER*`v<>$C>a&0&yXh|g31G$83;%`m{L^Y6PMf7k6(Ea$xtk$8*5+adI<kzy&!r45k`lQWUPHUZ3}YFS7A>U?B|)Or0qv!}fQa`c*|RbN%zm>_y3B|6{$a8%(VN>SHziVhwY-`3?1?Tq~S>tFx!=Rf`X?}G5*1300>_>)dZy&?g`<c-Kn%Y>p-Lq_VC?yh8AHfp*Z3WL45o8lo-LxdEXEgj|JGP)Ppwl-DqCoeid&<2Zcbg3}w1fFKo=YRew&c@nwuE$s^i$lU8PZO@Q4!f^9LrPIEjKgE%^vH|}@UfTbzg_tZCbKLDEjr$zbC{>0Er~QU!M<QRk1At%*S~E+-?b?~B~%jO%g9wX9xC25lP-nu3hlWNf>Hy{BuT0tjDy}5SrK%TZ%3WH!++@&m!yMI__&4f2vAX)By<f7ou}vwR7cw_X%9Ke))+IAfLwGQ^Xnt%i#6Fzdx(f<&Y0O`p=m%yl42VV0@g;d(0zWw`4sx{ymj9Dm#%A2<>-bU0>!XsG2QS7U|2Z?aHK{5iYl~Jc1Em04&5@<Mc7t;chFSt&7$tI7raIXPUgA<+!lsN;@((!otDw(NVQA?=+%)TpF`pO-~R)5Il0L'
RAW = zlib.decompress(base64.b85decode(BLOB.encode()))
PARAMS = json.loads(RAW)
RC = tuple(tuple(int(v,16) for v in row) for row in PARAMS["round_constants"])
MDS = tuple(tuple(int(v,16) for v in row) for row in PARAMS["mds"])
INDICES = tuple(range(4)) + tuple(range(4,60)) + tuple(range(60,64))


def digest(nk,rho):
    s = [nk,rho,1<<65]
    for i in INDICES:
        s[0] = (s[0]+RC[i][0])%P
        s[1] = (s[1]+RC[i][1])%P
        s[2] = (s[2]+RC[i][2])%P
        s[0] = pow(s[0],5,P)
        if i<4 or i>=60:
            s[1] = pow(s[1],5,P)
            s[2] = pow(s[2],5,P)
        s = [sum(MDS[j][k]*s[k] for k in range(3))%P for j in range(3)]
    return s[0]


def trial(seed):
    rho = int.from_bytes(hashlib.shake_256(bytes.fromhex(seed)).digest(32),"little") & ((1<<254)-1)
    count = 0
    def step(x):
        nonlocal count
        count += 1
        if count > 54:
            raise RuntimeError("cap")
        return digest(x,rho) & 127
    try:
        power = lam = 1
        tortoise = 0
        hare = step(0)
        while tortoise != hare:
            if power == lam:
                tortoise = hare
                power *= 2
                lam = 0
            hare = step(hare)
            lam += 1
        a = b = 0
        for _ in range(lam):
            b = step(b)
        prev_a = prev_b = None
        while a != b:
            prev_a,prev_b = a,b
            a = step(a)
            b = step(b)
        if prev_a is None or prev_a == prev_b:
            return None
        if (digest(prev_a,rho) & 127) != (digest(prev_b,rho) & 127):
            return None
        enc = lambda x: (x.to_bytes(32,"little")+rho.to_bytes(32,"little")).hex()
        return enc(prev_a),enc(prev_b)
    except RuntimeError:
        return None


def fullwidth_trail(seed):
    material = hashlib.shake_256(bytes.fromhex(seed) + b"fullwidth").digest(64)
    rho = int.from_bytes(material[:32], "little") & ((1 << 254) - 1)
    x = int.from_bytes(material[32:], "little") & ((1 << 254) - 1)
    seen = {}
    for _ in range(20):
        y = digest(x, rho)
        key = y & 255
        if key in seen and seen[key] != x:
            a = (seen[key].to_bytes(32, "little") + rho.to_bytes(32, "little")).hex()
            b = (x.to_bytes(32, "little") + rho.to_bytes(32, "little")).hex()
            return a, b
        seen[key] = x
        x = y
    return None


def main():
    req = json.load(sys.stdin)
    out=[]
    for item in req["trials"]:
        if req["experiment_id"] == "truncated-brent7":
            pair = trial(item["seed"])
        elif req["experiment_id"] == "fullwidth-trail8":
            pair = fullwidth_trail(item["seed"])
        else:
            raise ValueError("unknown experiment")
        out.append({"trial":item["trial"],"message_a_hex":pair[0] if pair else None,"message_b_hex":pair[1] if pair else None})
    json.dump({"schema_version":1,"trials":out},sys.stdout,separators=(',',':'))

if __name__ == "__main__":
    main()
