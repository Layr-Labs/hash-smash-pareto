#!/usr/bin/env python3
"""Regenerate, hash, count, and execute the exact combined r24 step."""

import base64
import hashlib
import json
import sys
import zlib


MASK64 = (1 << 64) - 1
MASK256 = (1 << 256) - 1
NC = -1
O_IN, O_XOR, O_AND, O_OR, O_NOT = range(5)
NREG = 4096
RC = (
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A,
    0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
    0x8000000080008081, 0x8000000000008009, 0x000000000000008A,
    0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089,
    0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
    0x000000000000800A, 0x800000008000000A, 0x8000000080008081,
    0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
)
RHO = (
    0, 1, 62, 28, 27, 36, 44, 6, 55, 20, 3, 10, 43,
    25, 39, 41, 45, 15, 21, 8, 18, 2, 61, 56, 14,
)
KL = (
    0x0000000000000000, 0x0000000000000000, 0x2D58ECEB83B21614,
    0x0000000000000000, 0x0000000000000000, 0xFFFFFFFFFFFFFFFF,
    0x0000000000000000, 0x0000000000000000, 0x0000000000000000,
    0x0000000000000000, 0xFFFFFFFFFFFFFFFF, 0x8B563B3AE0EC8583,
    0x0000000000000000, 0x85AB1D9D707642C2, 0xE953898A3E26F4F5,
    0xFFFFFFFFFFFFFFFF, 0x8000000000000006, 0, 0, 0, 0, 0, 0, 0, 0,
)
EXPECTED_PLAN_SHA256 = "611ecb6703de3447708c17300ff7f42a290c227095b7799d2e1a9f3f668a6f69"
PLAN_B85 = "c-rln-E!kNl7*1~2vZWs0@SK*w!5b58D?W2VlOr}He%oZUG_UkTYt7}X{vf+E=JuhOCkYeCi3Jt3HrbO??3+YfB*Y`{%#g{+3Ww|_2bJw$Jf~>(-^aNZ#y4gr>kb~%yn~tvz6Xi{lgLe0x!Gq(e55{-z9r{&F-4SUIT04{#ZT`Y_lI2{O{M}3HO=__7=&PY4UPW1MD24FX>>XN$e_j?Ru?8uwb9(g1xN^w{NsN!(#6Zu=fyQpQF`20l3|j^Y$1h?9++tag^D4#9#K)?3O>D%$k-|QmN^wmZg7Ldi^skOJ7Q_eMvoY*;3-`(s^6cQp&RZRYUZ7NpWFZ?WJ0&y%*jr++Gv^a7U?i?De;jYE6+bS}R4SVFBJQktIs3l^M97f4FgpnyxUkY6>mf7cJ2>OOG;`%iN$PxR@g2O0l}I;1_+*dZn-g6X@OISBmW6+ghVOB+c4mteQ;j^6gTY1oyW^Az>mc#SA&>F{&l{w_NVg7*k@pzvkNGb@yY+upgT4@tSV`1S+r(@bN~K+~(>B3EV!j#UA13dvCD^X0mtd9xt%tNKr~JowNp}K(~zGu#Tkm0_sxw4!S`e7y=>R%eJI3b<$k`5@5J#5ukvD0Mtz-z|qd!m8|DWrUz1jtRq!m29^4<RKEyDx-O-)Tr7)YrS~NYjU_pHunwDL6DA9E#Zq@Ox)3OoCcRjNrTOmwh?A)vX=$11Wg+@)%=$;6D0ID4dT^6Tgl=7(7TH(4qEN_GoitXTu#uI^59&jE5MlOHkoagCKCr5VAFCR6T`TNen){4&@6fk)sfuouz*Q-Iu&CWv+Kzntj@q#MtF&E>6ZMdhU`2EVX2hdpdMZss>I9j@#@}JavZ4+;R<?`8k_PB&C4CpvOKSTr8eJAkBEAkaI(O<GEz*AzTE&k(LlJU?{QB&rL=&awrMMwU-0E1WZmEDN=6C*08FV{Kr`}#2DBode>tf!d;-r6N0t<Y1@G*h8nBbphDF#t{l6v4vCTF;;@S%=Uz_0774XRiAB549X)p|eM+K(XU_N?|8qAWbZ;eTywdp}Lu1J>F(_)ZbB2RGt`5wrV<{vMrecR6IYWxAcr^HNa03KqSL<Y)vAB}>%;jnn`|a#l>@Xp(#@o>K~g0@I~Y3D21RtLa9lF`4tV%VREp!YJyUn&`Xw*Dik@079Fvmz<X4BBkv5)bSz;<(H{aIANESv4!2WbnM07V&LK$m&H{JqG}9`YcAvqLf18W-}q87C39q^uRhw%XXdpH5Z$UoXnDPjkhnz&64AOyUbRcyF7>R}-F=gNu4^AxdUlVx`;n6IPdM$mtJ2x+>S&jR$v&^B_U2^IKIpmc(M#{j1H1Tj&G?`6w^t`*cDw(ro`@uCR~w2t22B0?QkwU&!dv=Uo_qR2hKrAdUv6tfeW$-X>m|XZrA3&oJ*y*ih0Nkzv50;U1&cHtWJ~eR^97aBxwOP*hR1IHU5&lh`T}S#C5tn;mJ$a_3$L)Q2Ghp0_1=5YTGjm$hg)>GsW<S3pnA38jjdG&DJ-rRDMv3*XbtIpM%E{Vp^A1BruKDOr*~ofAML4rMpJ1&8)TmuV}BWb@9!Y(x;P#W13xGS7H*y?eoXTAz$y60j{)qR(rx#4Eq3#<!uRSD7`9FRF1bQ<L<1%fTJPTl16QwVR+Yg@V+l=L&$QHQdQ+L&@}fW2Ga_+tb=ZK4FR?mkBv{3aMH*YJ@zdfw?@T)AimY+PEWNH1B#o=4k;N%nQ#*;O3g|%0J6Yfsqsj!PE>BLHt{l{lR~^Kum)5zQxj|`d2Q0m|yX$e4YEfTxg1hSNf)#Hh+z&sz>mHHbf7(NXdmdrjclc}XNoD)6`TjVa?I)b%e%x%D-FbTc;VG5f>T};j#2z^~v)k6&Te)SQ_1tz_v0pwdv|EGE1-%ZBp6l0~`m-9mIgQOy>x-XDS3ecnEz3Lt6PPc4_am;N1L^8VyE>PW%+wie?tP^=Sj@HQm)HcpxcpfqT0vD_QSGo2p@EcSt31~6lqe4ZOy7ihKW-A`E<Op6S^MbJe{p8yi|l-D648r9a&h@9ikH4$q<kIxU1!eG>AtJ47au2Qc<*CfF6eBmA67PIng*YnpP}#Cel17U&$gvZnz^j+x6iNs{mAYwQq}e@xxMLe?;&)%PsHEZ&Ddi^{gYm4NM$TNifGybeYN7J!IFpc#AQs*P~%cZTSoe1JwsWtHRb)7dt6G?QLd|JKQ$Ut*5jcxE|$kKR{GjSPhM&h%9z3VJ6Z$aO)d12>q5mqR4>^d9yM=k0p`dg4IrsE&ud@2q;b{SO|l(MPMOcyB-Jx`POE$ec_Uuv`Pb5-&cSsrck!)%Ibx9cu`<@+XdKl+K&Y!y9veEuM$iu8`OTmtI`&oo<C^)=UhDS0I9fX#JN>#U-e(7!{z&(9^Xntt(`CCjv9zm43HIht^Z556;rfyE%iVT<3UbBmc18ske?Vf#gPg0!)@QkU`6%12Ir_X)x3_<vV#n|7l4I-*d%eVLHRkww{r>du`P3ELnT|d4&(0sppB+|NxPClqr{G+i8Qy%r^=e(P%X4hIdA@x9l>g!&?&OQvb$(s#<<Z8AXdM&LE}XOX1jW(GGehl^h_3;ETP*FEUZ*U%C~T*UHM>aX<3_#_jrP{StLFwU*>d(r6&DdUv-cIL9k={E?O*@6$}WI#t&h&~{X7rDnIRW*2D7&&hf|&$x5myNX4t!Du@@@M%x>!8b1<EkiDO#6?dYx^{+wm-*+$r9;jnPFf#)|LD~6q~Y^N<b-F03%UPAbW5RWC|7|yHMo*cDXZN$~BSAlvf(CrG;=MlRu_tz_&O4{Y$d)dW~=&LVz$kS-!w6RcIY*QY>w2z^N;b}%hPL={cX)=q`kV3VXr(pAJR;HNabQnU7IZPq{GRIt|oZA$+rwwV^X68x1&oPY?bUlUmZH553UZ)ff^VV$MhA@r6VEC}BydQ=zk7<}-@+l-^yyi$XSgbjPU5J_6p0J_R1NU!3o5rC}i;Z)OHnkX-JI@V!^Kh7A+D~D?wj|#g*GE48Hph6tXPY<7p?P)|rWRtQgU}qi9^1SG`5q^DeO4Tv6pK*imdDBCfMghL!|zaY9{63b^J$iiIU7EQooW3vBFNhm!i?QtxUQ4!199h`5b8GAv?cyMMEASLbuS|E540AM_$v-Yu?WOi-?N4h|1qFZJpOGq;y<Q?+om{dJpOyu#%G#>V86{F{L1yp_(R>KJcl9IJ$~ZYq*w&@b0a&3EngAqLADm|pB00hd_m&O;}ECL{cQ-lm@~OBOeL2YJ3JpE{u}WR;oF2e`26Q=#9xP|%7>UX?yD*PQkg3LD;72=9~9Tf*u1krww9XpIfbqHSmQ_gMa%}piap8$HnqvJ@?p<s!?y#|ew*VkV8emWYK+Lg)F<VG#zofGJdGSY1brqSJpXM@0l!#Z``z+}JP2<4D=sqe-?M(m#3>K#xiHZ@A3~;U)bGfC2YevJBlpwDc|L@+saxV-J%%>T#9uxq@_(!NlPr<==cG6ciiLdMArI$QTxj2Fkk7=C_>U&Pl?UW0@sGqmd;SkB0~Ux6B9igFDj$-`NA}#vPw+SJJ`eJ5;3rR-f0M#Yu~0k!ZSeZgjCtAr7*N>Ce_NRUckJVqM4Zz%e*Q*1AUDYIVB}s#!R9!tJ~Ye3Za?W-49aQSu?FQr@fGf|H|07K=TVp=Hb#spK9A(~7@p=)^~cyp@;?k6+>Va#m}J|YHLxYCHW43FjQUiEHV?$7g<+NrR7i51dl;Kk|8jM|7xq7~H=Y-=k@X|%H}<31K;Go343T{uv3tXKaw`0e&tQf1Wn&H-un>T@aUHu@U-_au&RMymxR{<n?_$tBVYlXZCI;lI>VRsa>W`@=hKbF>_cB-E&+9Pz7}_pU|Mt{BBmN;BYR1+aJP&rlW3tBhHVwpoFn%)gQGev?NdD7fO#}Wb7GWS4z+V`))B#<u*sOgw<w8|`pcaEAda*E03!k$or(f_L7WRsq3(wR8;>Y}SZ1~%qFJ9|I$a~-8qWnw3H?|TBBmY8(JJtJ<cyES^t=I=1iNQ|wVT=Dp{xz^zg6evo4*2i*4&?Vh%?r=-6YCW1H?bOWKh_8Gg4lo+_E<TuI{%~`GvS|H@H(*deQxAgA^wH+cPV&%*sy+N{Y?I6@_z(>qw0UyvL{>iL_Tb^&+Mr&zRiX8#TWAHwLWN%*PQn?)@xc@@po>^<b0e*@|9T3TjHObA6Hyt@;@v8(^qm2+!-+q!n^WH`z>BlJ)|~J|HK#a@wGk-;6dZH2RSk>GFR+1M(xEflejtOg}Ty+;|4tAUxv@Ahavwlul0hu5y3UJG^lPyTm2YP9f(66GFT;V$sdawe$WDry{+SQz|IB!Ta<rrp2ZG-6BE}W3wunxf&awk2i4y!|Nel#7mwYb{9|ot7++g91o%>VA*jxd*tVTyLx>x$^Ih2aK51Nz$>+&IF;m_p&9Rj&;v;c%#^0R9^V_Pt2^oyAej}bm{F7IF5I25QFNiVk7vkU3epa4t#V2t?nctF+)#ISJjk)>QA*dEb-#=6Q*$eS;OVP2TeKe0hxvlu?uV<CF<RiATkMIR+ulbW^#X<ON)PL2YmZZxzo})}ZD-J7OsUO09+!GIMA^s&Q9>0JwaGl|6){FSxiN9kmkL2TiUh9QorM)NKQF&x*jYIz#@%Q?o_(#<l_8xn2!1cq5SL%W1#@=x_#6CYUPeFf$Vd2)rYp3csxv(pFKkva`iQwGpg<=(}`ChWNY`}l7rPSvQ`4{50!d0_)HxqYY$@Q(<93U;tBM!>MKcoMcgPd+&V`E-?zeC=DrLA+c@?l_oaVPa)*TBCpN8GT>X5~WzUnywcGjY<skF&UY3w{;DmV^c6N%FDiaqyy=vY!XVU;0n+kI%EXQ+0EnglD)d$<M{PGY!t4lj?=m#)r96-xLS&GrrHNMXE{CE?N19{!tvXuhI|V&Thh1WuN-A6^1hW?cDgn-$7gpH^G0w4t)NKJ`ldek<@(V7+G_S(nk0O|L#?P2JzIYAJD9`^g}S|%AqFm$oCcB8}(m0T>6NF#K$~&e8pqp@6cC0raFfHu<(^$Vw@(;C;!keT06Sd1?R}GDxblH$4B~-{2!(NrKe<raLoGEbrkpH>iQ5rb{plN^5T`hSzmfIAV{UXBkMQfJF8zZazXt^s-EL1ZTMW32fK6qaDac&)N?fHN;H<&QTCO!_o{!nx<1}S+1gy2sE&)jt8|_8cv$uQsQN?wZ^94xB@M$gp5xNil)|ZtXFP`RmFk}jv+GFsL^iBAZq<7*@VDyuaher>_)mSD))RlLUnoJJsSze!zkkK^PW{BFTqef}me)A8o8C&jR$hBX^()#7*9*c6{7(JZDF5KUgY;KWkF(5cAEq9JymH<C>#TlhQU4iK7gT%p?(0VRPd}CAKkF6gV`?1qO8r)ids*9kk&X;rBc&gN;}QIMohM<k;-7c;p#0x>AE!PuxZeZV$uAtOIoMCfchJ+Hd31dUwx}!Q1wL%%gY+lss~`2AIIsPM>Vxz{us`ROpV3y#=RGU=#|EwaoN6ZeL%p+jVhGv!TfK>CPl-RG-TP_rTtoj06Y3`l@!u-`FKf#N={D&H^aa1;{Quo9+93"
EXPECTED = {
    "P": (4292, (2518, 960, 640, 174), 20924, "a5566d20f7aeaf6ba9dd955cf965118512557672f5b83a72bd75c5aed2ef74f1"),
    "G": (0, (0, 0, 0, 0), 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    "B1": (6679, (4822, 939, 661, 257), 32561, "d8f072bc4a7205893f1e39ab7782a668a583a5f01f0c7a13662b67e4605ce8af"),
    "B2": (6633, (4820, 944, 656, 213), 32336, "b920b2758ccd1b379c585cd076708c65ca427d73889e0bf6324a40b1a4cfd14c"),
    "B3": (6645, (4818, 945, 655, 227), 32395, "cc573cdccfb0e8896359677878df745f253cc1fb1ce62f0af56a8254b36794c5"),
    "B4": (6652, (4832, 940, 660, 220), 32429, "77a490805b25f40a361a322dbef9b95337054649f218563cb577ad5eb3795486"),
    "B5": (6643, (4822, 941, 659, 221), 32385, "f98823025570035b5523e744653ab7daf7380c6731da9e643b039127ba417da3"),
    "B6": (6664, (4818, 945, 655, 246), 32487, "01b5bd129f9a7b9579a7d70db28a7f980b44c6505b46584d0ca8bef66d02e421"),
    "B7": (6722, (4840, 924, 676, 282), 32770, "d5c18e44cf473cdb1ace7d40df2caa40b230386b44e4fab61edb1767ca3135ba"),
    "B8": (6910, (4852, 818, 782, 458), 33687, "0ed1e08cc361ad502ef54894db39573efb0ddcf5d9769939da475976088d6c9b"),
    "E": (2492, (2211, 167, 89, 25), 12149, "e62607aa4e0bc72fa1f7f2ef862db9b04bb36c522cb0e9e8ff9881a2cfea671f"),
}
EXPECTED_PD = bytes.fromhex(
    "683203d84718cffd8f02f595c8f7747f0804d491418710219141000231200081"
)


def rol(x, n):
    return ((x << n) | (x >> (64 - n))) & MASK64 if n else x


def permute(a):
    for rc in RC:
        c = [a[x] ^ a[x + 5] ^ a[x + 10] ^ a[x + 15] ^ a[x + 20] for x in range(5)]
        d = [c[(x - 1) % 5] ^ rol(c[(x + 1) % 5], 1) for x in range(5)]
        b = [0] * 25
        for y in range(5):
            for x in range(5):
                i = x + 5 * y
                b[y + 5 * ((2 * x + 3 * y) % 5)] = rol(a[i] ^ d[x], RHO[i])
        for y in range(5):
            row = 5 * y
            for x in range(5):
                a[row + x] = (
                    b[row + x] ^ ((~b[row + (x + 1) % 5]) & b[row + (x + 2) % 5])
                ) & MASK64
        a[0] ^= rc


def digest_message(message):
    padded = bytearray(message)
    padded.append(0x06)
    padded.extend(b"\0" * ((-len(padded)) % 136))
    padded[-1] |= 0x80
    state = [0] * 25
    for offset in range(0, len(padded), 136):
        for lane in range(17):
            state[lane] ^= int.from_bytes(padded[offset + 8 * lane : offset + 8 * lane + 8], "little")
        permute(state)
    return b"".join(x.to_bytes(8, "little") for x in state[:4])


def message(point):
    u = [(point >> (64 * i)) & MASK64 for i in range(4)]
    lanes = list(KL[:16])
    lanes[1] = u[0]
    lanes[6] = u[1]
    lanes[11] = u[0] ^ u[1] ^ KL[11]
    lanes[4] = u[2]
    lanes[9] = u[3]
    lanes[14] = u[2] ^ u[3] ^ KL[14]
    return b"".join(x.to_bytes(8, "little") for x in lanes)


def scalar_chain(point, pd):
    lanes = list(KL)
    u = [(point >> (64 * i)) & MASK64 for i in range(4)]
    lanes[1] = u[0]
    lanes[6] = u[1]
    lanes[11] = u[0] ^ u[1] ^ KL[11]
    lanes[4] = u[2]
    lanes[9] = u[3]
    lanes[14] = u[2] ^ u[3] ^ KL[14]
    permute(lanes)
    return sum((lanes[i] ^ pd[i]) << (64 * i) for i in range(4))


class Graph:
    def __init__(self, inputs, affine_inputs=False):
        self.op = []
        self.a = []
        self.b = []
        self.k = []
        self.linear = []
        self.cons_table = {}
        self.form_nodes = {}
        for j in range(inputs):
            n = self.new_node(O_IN, 0, 0)
            if affine_inputs:
                mask = [0, 0, 0, 0]
                mask[j >> 6] = 1 << (j & 63)
                mask = tuple(mask)
                self.linear[n] = mask
                self.form_nodes[mask] = n

    def new_node(self, op, a, b):
        n = len(self.op)
        self.op.append(op)
        self.a.append(a)
        self.b.append(b)
        self.k.append(0)
        self.linear.append(None)
        return n

    def cons(self, op, a, b):
        if op != O_NOT and a > b:
            a, b = b, a
        key = (op, a, b)
        n = self.cons_table.get(key)
        if n is not None:
            return n, False
        n = self.new_node(op, a, b)
        self.cons_table[key] = n
        return n, True

    def xor(self, left, right):
        an, ap = left
        bn, bp = right
        if an == NC:
            return bn, bp ^ ap
        if bn == NC:
            return an, ap ^ bp
        if an == bn:
            return NC, ap ^ bp
        am = self.linear[an]
        bm = self.linear[bn]
        if am is not None and bm is not None:
            mask = tuple(x ^ y for x, y in zip(am, bm))
            k = self.k[an] ^ self.k[bn]
            if not any(mask):
                return NC, k ^ ap ^ bp
            n = self.form_nodes.get(mask)
            if n is not None:
                return n, k ^ ap ^ bp ^ self.k[n]
            n, _ = self.cons(O_XOR, an, bn)
            self.k[n] = k
            self.linear[n] = mask
            self.form_nodes[mask] = n
            return n, ap ^ bp
        n, _ = self.cons(O_XOR, an, bn)
        return n, ap ^ bp

    def complement(self, value):
        n, p = value
        if n == NC:
            return value
        out, created = self.cons(O_NOT, n, 0)
        if created and self.linear[n] is not None:
            self.linear[out] = self.linear[n]
            self.k[out] = self.k[n] ^ 1
        return out, p ^ 1

    def and_value(self, left, right, select):
        an, ap = left
        bn, bp = right
        if an == NC:
            return right if ap else (NC, 0)
        if bn == NC:
            return left if bp else (NC, 0)
        if an == bn:
            return left if ap == bp else (NC, 0)
        if not ap and not bp:
            return self.cons(O_AND, an, bn)[0], 0
        if ap and bp:
            return self.cons(O_OR, an, bn)[0], 1
        plain = an if not ap else bn
        other = bn if not ap else an
        if select:
            negated = self.complement((plain, 0))
            return self.cons(O_OR, negated[0], other)[0], 1
        term = self.cons(O_AND, plain, other)[0]
        return self.xor((plain, 0), (term, 0))


def term_cost(a, b):
    if a[0] == NC or b[0] == NC or a[0] == b[0]:
        return 0
    return 1 if (a[1] ^ 1) == b[1] else 2


def dynamic_row(graph, row, need):
    distinct = all(v[0] != NC for v in row) and len({v[0] for v in row}) == 5
    best = None
    for trick in range(-1, 5 if distinct else 0):
        if trick >= 0 and (not (need >> trick) & 1 or not (need >> ((trick + 1) % 5)) & 1):
            continue
        for subset in range(32):
            values = list(row)
            cost = 0
            for x in range(5):
                if (subset >> x) & 1:
                    if row[x][0] == NC:
                        cost = 1 << 29
                    else:
                        values[x] = values[x][0], values[x][1] ^ 1
                        cost += 1
            for x in range(5):
                if not (need >> x) & 1:
                    continue
                if x == trick:
                    k = (trick + 1) % 5
                    p1, p2 = values[(k + 1) % 5], values[(k + 2) % 5]
                    if (p1[1] ^ 1) == p2[1]:
                        bk = values[k][0], values[k][1] ^ (p1[1] ^ 1)
                        cost += term_cost(bk, values[(x + 2) % 5])
                    else:
                        cost += 1
                else:
                    cost += term_cost(values[(x + 1) % 5], values[(x + 2) % 5])
            candidate = cost, subset, trick
            if best is None or candidate[0] < best[0]:
                best = candidate
    _, subset, trick = best
    row = list(row)
    for x in range(5):
        if (subset >> x) & 1:
            row[x] = graph.complement(row[x])
    out = [None] * 5
    k = (trick + 1) % 5
    if trick >= 0:
        first = row[(k + 1) % 5][0], row[(k + 1) % 5][1] ^ 1
        out[k] = graph.xor(row[k], graph.and_value(first, row[(k + 2) % 5], 0))
    for x in range(5):
        if not (need >> x) & 1 or (trick >= 0 and x == k):
            continue
        first = out[k] if x == trick else row[(x + 1) % 5]
        first = first[0], first[1] ^ 1
        out[x] = graph.xor(row[x], graph.and_value(first, row[(x + 2) % 5], 0))
    return out


def target_row(graph, row, target, row_table):
    pin = sum(value[1] << x for x, value in enumerate(row))
    subset, trick_plus_one, select, _ = row_table[32 * pin + target]
    row = list(row)
    for x in range(5):
        if (subset >> x) & 1:
            row[x] = graph.complement(row[x])
    trick = trick_plus_one - 1
    k = (trick + 1) % 5
    out = [None] * 5
    if trick >= 0:
        first = row[(k + 1) % 5][0], row[(k + 1) % 5][1] ^ 1
        out[k] = graph.xor(row[k], graph.and_value(first, row[(k + 2) % 5], (select >> k) & 1))
    for x in range(5):
        if trick >= 0 and x == k:
            continue
        first = out[k] if x == trick else row[(x + 1) % 5]
        first = first[0], first[1] ^ 1
        out[x] = graph.xor(row[x], graph.and_value(first, row[(x + 2) % 5], (select >> x) & 1))
    if sum(value[1] << x for x, value in enumerate(out)) != target:
        raise AssertionError("row-table polarity mismatch")
    return out


def theta(graph, state, cnot, dnot):
    parity = [None] * 320
    delta = [None] * 320
    for x in range(5):
        for z in range(64):
            value = state[64 * x + z]
            for y in range(1, 5):
                value = graph.xor(value, state[64 * (x + 5 * y) + z])
            if cnot is not None and cnot[64 * x + z]:
                value = graph.complement(value)
            parity[64 * x + z] = value
    for x in range(5):
        for z in range(64):
            value = graph.xor(parity[64 * ((x + 4) % 5) + z], parity[64 * ((x + 1) % 5) + ((z + 63) & 63)])
            if dnot is not None and dnot[64 * x + z]:
                value = graph.complement(value)
            delta[64 * x + z] = value
    return delta


def build_prefix(plan):
    graph = Graph(256, True)
    state = [(NC, (KL[lane] >> z) & 1) for lane in range(25) for z in range(64)]
    for z in range(64):
        state[64 + z] = z, 0
        state[6 * 64 + z] = 64 + z, 0
        state[4 * 64 + z] = 128 + z, 0
        state[9 * 64 + z] = 192 + z, 0
        state[11 * 64 + z] = graph.xor(graph.xor((z, 0), (64 + z, 0)), (NC, (KL[11] >> z) & 1))
        state[14 * 64 + z] = graph.xor(graph.xor((128 + z, 0), (192 + z, 0)), (NC, (KL[14] >> z) & 1))
    for round_index in range(2):
        delta = theta(graph, state, plan[0] if round_index else None, plan[1] if round_index else None)
        new_state = list(state)
        for y_out in range(5):
            for z in range(64):
                row = []
                for x_out in range(5):
                    y = x_out
                    x = (3 * y_out + x_out) % 5
                    zz = (z - RHO[x + 5 * y]) & 63
                    row.append(graph.xor(state[64 * (x + 5 * y) + zz], delta[64 * x + zz]))
                out = dynamic_row(graph, row, 0x1F)
                for x_out in range(5):
                    new_state[64 * (x_out + 5 * y_out) + z] = out[x_out]
        for z in range(64):
            n, p = new_state[z]
            new_state[z] = n, p ^ ((RC[round_index] >> z) & 1)
        state = new_state
    if any(value[0] == NC for value in state):
        raise AssertionError("constant prefix output")
    return graph, [v[0] for v in state], bytes(v[1] for v in state)


def lazy_delta(graph, state, parity, delta, cnot, dnot, x, z):
    def get_parity(px, pz):
        index = 64 * px + pz
        if parity[index] is None:
            value = state[64 * px + pz]
            for py in range(1, 5):
                value = graph.xor(value, state[64 * (px + 5 * py) + pz])
            if cnot is not None and cnot[index]:
                value = graph.complement(value)
            parity[index] = value
        return parity[index]

    index = 64 * x + z
    if delta[index] is None:
        value = graph.xor(get_parity((x + 4) % 5, z), get_parity((x + 1) % 5, (z + 63) & 63))
        if dnot is not None and dnot[index]:
            value = graph.complement(value)
        delta[index] = value
    return delta[index]


def build_body(input_p, plan, row_table):
    graph = Graph(1600)
    state = [(q, input_p[q]) for q in range(1600)]
    out_state = list(state)
    parity = [None] * 320
    delta = [None] * 320
    for y_out in range(5):
        for z in range(64):
            row = []
            for x_out in range(5):
                y = x_out
                x = (3 * y_out + x_out) % 5
                zz = (z - RHO[x + 5 * y]) & 63
                d = lazy_delta(graph, state, parity, delta, plan[0], plan[1], x, zz)
                row.append(graph.xor(state[64 * (x + 5 * y) + zz], d))
            out = target_row(graph, row, plan[2][64 * y_out + z], row_table)
            for x_out in range(5):
                out_state[64 * (x_out + 5 * y_out) + z] = out[x_out]
    return graph, [v[0] for v in out_state], bytes(v[1] for v in out_state)


def build_end(input_p):
    graph = Graph(1600)
    state = [(q, input_p[q]) for q in range(1600)]
    parity = [None] * 320
    delta = [None] * 320
    nodes = [0] * 256
    polarity = bytearray(256)
    for z in range(64):
        row = []
        for x_out in range(5):
            x = y = x_out
            zz = (z - RHO[x + 5 * y]) & 63
            d = lazy_delta(graph, state, parity, delta, None, None, x, zz)
            row.append(graph.xor(state[64 * (x + 5 * y) + zz], d))
        out = dynamic_row(graph, row, 0x0F)
        for x_out in range(4):
            n, p = out[x_out]
            if x_out == 0:
                p ^= (RC[23] >> z) & 1
            index = 64 * x_out + z
            nodes[index] = n
            polarity[index] = p
    return graph, nodes, bytes(polarity)


def targets_to_state(target):
    state = bytearray(1600)
    for y in range(5):
        for z in range(64):
            value = target[64 * y + z]
            for x in range(5):
                state[64 * (x + 5 * y) + z] = (value >> x) & 1
    return bytes(state)


def allocate(graph, outputs, output_regs, input_regs):
    count = len(graph.op)
    input_count = len(input_regs)
    live = bytearray(count)
    output_index = [-1] * count
    reserved = bytearray(NREG)
    for j, node in enumerate(outputs):
        if node < input_count or output_index[node] >= 0:
            raise AssertionError("invalid/shared output")
        live[node] = 1
        output_index[node] = j
        reserved[output_regs[j]] = 1
    for i in range(count - 1, input_count - 1, -1):
        if live[i]:
            live[graph.a[i]] = 1
            if graph.op[i] != O_NOT:
                live[graph.b[i]] = 1
    last = [0] * count
    for i in range(input_count, count):
        if live[i]:
            last[graph.a[i]] = i
            if graph.op[i] != O_NOT:
                last[graph.b[i]] = i
    for node in outputs:
        last[node] = 65535
    reg = [0] * count
    busy = bytearray(NREG)
    for j, physical in enumerate(input_regs):
        reg[j] = physical
        if last[j]:
            busy[physical] = 1
    free_regs = [r for r in range(NREG - 1, -1, -1) if not busy[r] and not reserved[r]]
    program = []
    mix = [0, 0, 0, 0]
    for i in range(input_count, count):
        if not live[i]:
            continue
        op = graph.op[i]
        a = graph.a[i]
        b = a if op == O_NOT else graph.b[i]
        if last[a] == i:
            physical = reg[a]
            busy[physical] = 0
            if not reserved[physical]:
                free_regs.append(physical)
        if b != a and last[b] == i:
            physical = reg[b]
            busy[physical] = 0
            if not reserved[physical]:
                free_regs.append(physical)
        if output_index[i] >= 0:
            destination = output_regs[output_index[i]]
            if busy[destination]:
                raise AssertionError("fixed output register busy")
        else:
            destination = free_regs.pop()
        busy[destination] = 1
        reg[i] = destination
        encoded = 0 if op == O_XOR else 1 if op == O_AND else 2 if op == O_OR else 3
        program.append((encoded, destination, reg[a], 0 if op == O_NOT else reg[graph.b[i]]))
        mix[encoded] += 1
    return program, tuple(mix)


def pack_program(program):
    packed = bytearray()
    accumulator = 0
    bits = 0
    for op, destination, left, right in program:
        if not 0 <= op <= 3:
            raise AssertionError("instruction opcode does not fit the declared 3-bit field")
        if any(not 0 <= register < (1 << 12) for register in (destination, left, right)):
            raise AssertionError("instruction register does not fit its declared 12-bit field")
        word = op | (destination << 3) | (left << 15) | (right << 27)
        if word >= 1 << 39:
            raise AssertionError("instruction crosses its declared 39-bit boundary")
        accumulator |= word << bits
        bits += 39
        while bits >= 8:
            packed.append(accumulator & 0xFF)
            accumulator >>= 8
            bits -= 8
    if bits:
        packed.append(accumulator)
    return bytes(packed)


def check_block(name, program, mix):
    packed = pack_program(program)
    expected_count, expected_mix, expected_size, expected_hash = EXPECTED[name]
    actual = (len(program), mix, len(packed), hashlib.sha256(packed).hexdigest())
    expected = (expected_count, expected_mix, expected_size, expected_hash)
    if actual != expected:
        raise AssertionError(f"{name} regeneration mismatch: {actual!r}")


def parse_regeneration_data():
    compressed = base64.b85decode(PLAN_B85.encode("ascii"))
    data = zlib.decompress(compressed)
    if len(data) != 14344 or data[:8] != b"HS24PLN1":
        raise AssertionError("invalid regeneration data")
    if hashlib.sha256(data).hexdigest() != EXPECTED_PLAN_SHA256:
        raise AssertionError("regeneration-data hash mismatch")
    offset = 8

    def plan():
        nonlocal offset
        result = (data[offset : offset + 320], data[offset + 320 : offset + 640], data[offset + 640 : offset + 960])
        offset += 960
        return result

    prefix = plan()
    bodies = [plan() for _ in range(8)]
    cycle = data[offset : offset + 1600]
    offset += 1600
    table_bytes = data[offset : offset + 4096]
    table = [tuple(table_bytes[i : i + 4]) for i in range(0, 4096, 4)]
    return prefix, bodies, cycle, table


def regenerate_step():
    prefix_plan, body_plans, cycle, row_table = parse_regeneration_data()
    programs = {}
    graph, outputs, prefix_p = build_prefix(prefix_plan)
    programs["P"], mix = allocate(graph, outputs, list(range(256, 1856)), list(range(256)))
    check_block("P", programs["P"], mix)
    bridge = [(3, 256 + q, 256 + q, 0) for q in range(1600) if prefix_p[q] != cycle[q]]
    programs["G"] = bridge
    check_block("G", bridge, (0, 0, 0, len(bridge)))
    input_p = cycle
    for index, plan in enumerate(body_plans):
        graph, outputs, input_p = build_body(input_p, plan, row_table)
        input_base = 1856 if index & 1 else 256
        output_base = 256 if index & 1 else 1856
        program, mix = allocate(
            graph,
            outputs,
            list(range(output_base, output_base + 1600)),
            list(range(input_base, input_base + 1600)),
        )
        name = f"B{index + 1}"
        programs[name] = program
        check_block(name, program, mix)
    if input_p != cycle:
        raise AssertionError("body polarity cycle did not close")
    graph, outputs, end_p = build_end(targets_to_state(body_plans[4][2]))
    programs["E"], mix = allocate(graph, outputs, list(range(256)), list(range(1856, 3456)))
    check_block("E", programs["E"], mix)
    pd_words = [sum(end_p[64 * lane + z] << z for z in range(64)) for lane in range(4)]
    pd_bytes = b"".join(word.to_bytes(8, "little") for word in pd_words)
    if pd_bytes != EXPECTED_PD or hashlib.sha256(pd_bytes).hexdigest() != "b7c84bcab67b6b05c6b700923db8a2101f9781ed7dc895e0713020bde7284811":
        raise AssertionError("PD regeneration mismatch")
    if sum(len(program) for program in programs.values()) != 60332:
        raise AssertionError("stored instruction total mismatch")
    runs = (3, 3, 3, 3, 3, 2, 2, 2)
    executed = len(programs["P"]) + len(programs["G"]) + len(programs["E"]) + 120
    executed += sum(runs[i] * len(programs[f"B{i + 1}"]) for i in range(8))
    if executed != 147252:
        raise AssertionError("executed instruction total mismatch")
    return programs, tuple(pd_words)


def execute(program, registers, word_mask=MASK256):
    for op, destination, left, right in program:
        a = registers[left]
        b = registers[right]
        registers[destination] = (
            a ^ b if op == 0 else a & b if op == 1 else a | b if op == 2 else a ^ word_mask
        )


def execute_schedule(programs, registers, word_mask):
    execute(programs["P"], registers, word_mask)
    execute(programs["G"], registers, word_mask)
    for round_index in range(2, 23):
        body = (round_index - 2) % 8
        execute(programs[f"B{body + 1}"], registers, word_mask)
        output_base = 1856 if not (body & 1) else 256
        for z in range(64):
            if (RC[round_index] >> z) & 1:
                registers[output_base + z] ^= word_mask
    execute(programs["E"], registers, word_mask)


def execute_step(programs, pd):
    raw = hashlib.shake_256(b"hashsmash-r24-emitted-program-check-v1").digest(8 * 32)
    points = [int.from_bytes(raw[32 * i : 32 * (i + 1)], "little") for i in range(8)]
    registers = [0] * NREG
    for bit in range(256):
        registers[bit] = sum(((point >> bit) & 1) << index for index, point in enumerate(points))
    execute_schedule(programs, registers, MASK256)
    for index, point in enumerate(points):
        emitted = sum(((registers[bit] >> index) & 1) << bit for bit in range(256))
        if emitted != scalar_chain(point, pd):
            raise AssertionError("emitted program differs from scalar reference")


SEARCH_WIDTH = 22
SEARCH_DP_LOW_ZERO = 4
SEARCH_DP_COMPARE_BITS = 3
SEARCH_DP_COMPARE_LIMIT = 5
SEARCH_REPLAY_CAP = 256
SEARCH_TRAIL_LIMIT = 3000
SEARCH_TABLE_WORDS = SEARCH_TRAIL_LIMIT // 4
SEARCH_DEADLINE = 400
RECORD_KEY_BITS = 46
RECORD_ID_BITS = 17
FULL_TRAIL_LIMIT = 66720


def pack_record(endpoint, trail_id, trail_limit):
    if not 0 <= endpoint < 1 << RECORD_KEY_BITS:
        raise ValueError("record key does not fit its declared field")
    if not 0 <= trail_id < trail_limit or trail_id >= 1 << RECORD_ID_BITS:
        raise ValueError("trail identifier does not fit the selected record layout")
    record = 1 | endpoint << 1 | trail_id << (1 + RECORD_KEY_BITS)
    if record >= 1 << 64:
        raise AssertionError("record crosses its 64-bit slot")
    return record


def check_record_boundaries():
    maximum_key = (1 << RECORD_KEY_BITS) - 1
    for trail_id in (65535, 65536, FULL_TRAIL_LIMIT - 1):
        record = pack_record(maximum_key, trail_id, FULL_TRAIL_LIMIT)
        if (record >> (1 + RECORD_KEY_BITS)) != trail_id:
            raise AssertionError("trail identifier did not round-trip")
        if (record >> 1) & maximum_key != maximum_key:
            raise AssertionError("record key did not round-trip")
        for position in range(4):
            word = record << (64 * position)
            if word >= 1 << 256:
                raise AssertionError("record crosses its 256-bit table word")
            if (word >> (64 * position)) & MASK64 != record:
                raise AssertionError("record slot did not round-trip")
    for endpoint, trail_id in ((1 << RECORD_KEY_BITS, 0), (0, FULL_TRAIL_LIMIT)):
        try:
            pack_record(endpoint, trail_id, FULL_TRAIL_LIMIT)
        except ValueError:
            continue
        raise AssertionError("out-of-range packed field was accepted")


def run_reduced_search(trials, programs, pd):
    """Run the complete rho/table/replay search with a 22-bit test hook."""
    trial_count = len(trials)
    if not trial_count:
        return []
    point_mask = (1 << SEARCH_WIDTH) - 1
    lane_mask = (1 << (256 * trial_count)) - 1
    registers = [0] * NREG
    seeds = [bytes.fromhex(trial["seed"]) for trial in trials]
    rho = [0] * trial_count
    next_id = [0] * trial_count
    attempt = [-1] * trial_count
    attempt_start = [0] * trial_count
    tables = [[0] * SEARCH_TABLE_WORDS for _ in trials]
    stored = [0] * trial_count
    done = [None] * trial_count
    lane_id = [0] * (256 * trial_count)
    lane_start = [0] * (256 * trial_count)
    pending = []
    observations = [
        {
            "attempts": 0,
            "lockstep_steps": 0,
            "trails_started": 0,
            "stored_records": 0,
            "replay_evaluations": 0,
            "replay_failures": 0,
            "emitted_program_checks": 8,
        }
        for _ in trials
    ]

    def is_distinguished(point):
        return (
            point & ((1 << SEARCH_DP_LOW_ZERO) - 1) == 0
            and (point >> SEARCH_DP_LOW_ZERO) & ((1 << SEARCH_DP_COMPARE_BITS) - 1)
            < SEARCH_DP_COMPARE_LIMIT
        )

    def small_chain(point):
        return scalar_chain(point, pd) & point_mask

    def start_attempt(t, step):
        attempt[t] += 1
        observations[t]["attempts"] += 1
        rho[t] = int.from_bytes(
            hashlib.shake_256(
                b"hashsmash-r24-rho-w22-v1"
                + seeds[t]
                + attempt[t].to_bytes(4, "little")
            ).digest(4),
            "little",
        ) & point_mask
        next_id[t] = 256
        attempt_start[t] = step
        tables[t] = [0] * SEARCH_TABLE_WORDS
        stored[t] = 0
        for lane in range(256):
            global_lane = 256 * t + lane
            lane_id[global_lane] = lane
            lane_start[global_lane] = step
            pending.append((global_lane, (rho[t] + lane) & point_mask))
        observations[t]["trails_started"] += 256

    def apply_pending():
        if not pending:
            return
        changed = 0
        for global_lane, _ in pending:
            changed |= 1 << global_lane
        keep = lane_mask ^ changed
        for bit in range(SEARCH_WIDTH):
            value = 0
            for global_lane, point in pending:
                if (point >> bit) & 1:
                    value |= 1 << global_lane
            registers[bit] = (registers[bit] & keep) | value
        pending.clear()

    def probe(t, endpoint, trail_id):
        key = 1 | endpoint << 1
        record = pack_record(endpoint, trail_id, SEARCH_TRAIL_LIMIT)
        slot = endpoint & 1023
        if slot >= SEARCH_TABLE_WORDS:
            slot -= SEARCH_TABLE_WORDS
        for _ in range(SEARCH_TABLE_WORDS):
            word = tables[t][slot]
            for position in range(4):
                old = (word >> (64 * position)) & MASK64
                if old == 0:
                    tables[t][slot] = word | record << (64 * position)
                    stored[t] += 1
                    return None
                if old & ((1 << (1 + RECORD_KEY_BITS)) - 1) == key:
                    return old >> (1 + RECORD_KEY_BITS)
            slot += 1
            if slot == SEARCH_TABLE_WORDS:
                slot = 0
        raise RuntimeError("reduced table has no empty record")

    def replay(t, stored_id, current_id, current_length):
        if current_length > SEARCH_REPLAY_CAP:
            observations[t]["replay_failures"] += 1
            return None
        stored_start = (rho[t] + stored_id) & point_mask
        current_start = (rho[t] + current_id) & point_mask
        point = stored_start
        stored_length = 0
        while stored_length < SEARCH_REPLAY_CAP:
            point = small_chain(point)
            stored_length += 1
            observations[t]["replay_evaluations"] += 1
            if is_distinguished(point):
                break
        if not is_distinguished(point):
            observations[t]["replay_failures"] += 1
            return None
        left, right = stored_start, current_start
        for _ in range(abs(stored_length - current_length)):
            if stored_length > current_length:
                left = small_chain(left)
            else:
                right = small_chain(right)
            observations[t]["replay_evaluations"] += 1
        if left == right:
            observations[t]["replay_failures"] += 1
            return None
        for _ in range(min(stored_length, current_length)):
            left_image = small_chain(left)
            right_image = small_chain(right)
            observations[t]["replay_evaluations"] += 2
            if left_image == right_image:
                return left, right
            left, right = left_image, right_image
        observations[t]["replay_failures"] += 1
        return None

    for t in range(trial_count):
        start_attempt(t, 0)
    apply_pending()
    step = 0
    while any(pair is None for pair in done):
        step += 1
        if step > 4000:
            raise RuntimeError("reduced search did not return a pair")
        execute_schedule(programs, registers, lane_mask)
        for bit in range(SEARCH_WIDTH, 256):
            registers[bit] = 0

        low_nonzero = 0
        for bit in range(SEARCH_DP_LOW_ZERO):
            low_nonzero |= registers[bit]
        equal = lane_mask ^ low_nonzero
        less = 0
        for offset in range(SEARCH_DP_COMPARE_BITS - 1, -1, -1):
            plane = registers[SEARCH_DP_LOW_ZERO + offset]
            if (SEARCH_DP_COMPARE_LIMIT >> offset) & 1:
                less |= equal & (lane_mask ^ plane)
                equal &= plane
            else:
                equal &= lane_mask ^ plane

        plane_bytes = [
            registers[bit].to_bytes(32 * trial_count, "little")
            for bit in range(SEARCH_WIDTH)
        ]
        events = []
        distinguished = less
        while distinguished:
            low = distinguished & -distinguished
            events.append(low.bit_length() - 1)
            distinguished ^= low

        reset_trials = set()
        for global_lane in events:
            t = global_lane >> 8
            if done[t] is not None or t in reset_trials:
                continue
            endpoint = sum(
                ((plane_bytes[bit][global_lane >> 3] >> (global_lane & 7)) & 1) << bit
                for bit in range(SEARCH_WIDTH)
            )
            current_id = lane_id[global_lane]
            current_length = step - lane_start[global_lane]
            stored_id = probe(t, endpoint, current_id)
            if stored_id is not None and stored_id != current_id:
                pair = replay(t, stored_id, current_id, current_length)
                if pair is not None:
                    done[t] = pair
                    observations[t]["lockstep_steps"] = step - attempt_start[t]
                    observations[t]["stored_records"] = stored[t]
                    continue
            if next_id[t] == SEARCH_TRAIL_LIMIT:
                start_attempt(t, step)
                reset_trials.add(t)
                continue
            new_id = next_id[t]
            next_id[t] += 1
            observations[t]["trails_started"] += 1
            lane_id[global_lane] = new_id
            lane_start[global_lane] = step
            pending.append((global_lane, (rho[t] + new_id) & point_mask))

        for t in range(trial_count):
            if done[t] is None and t not in reset_trials and step - attempt_start[t] == SEARCH_DEADLINE:
                start_attempt(t, step)
        apply_pending()

    rows = []
    digest_mask = (1 << SEARCH_WIDTH) - 1
    for t, trial in enumerate(trials):
        left, right = done[t]
        message_left = message(left)
        message_right = message(right)
        if message_left == message_right:
            raise AssertionError("replay returned one message twice")
        digest_left = int.from_bytes(digest_message(message_left), "little")
        digest_right = int.from_bytes(digest_message(message_right), "little")
        if (digest_left ^ digest_right) & digest_mask:
            raise AssertionError("replay pair fails the 22-bit target predicate")
        rows.append(
            {
                "trial": trial["trial"],
                "message_a_hex": message_left.hex(),
                "message_b_hex": message_right.hex(),
                "observations": observations[t],
            }
        )
    return rows


def run_trial(seed_hex, pd):
    seed = bytes.fromhex(seed_hex)
    raw = hashlib.shake_256(b"hashsmash-r24-combined-projection-v1" + seed).digest(17 * 32)
    points = [int.from_bytes(raw[32 * i : 32 * (i + 1)], "little") for i in range(17)]
    projected = {}
    evaluations = 0
    for _ in range(4):
        next_points = []
        for point in points:
            image = scalar_chain(point, pd)
            evaluations += 1
            key = image & 0xFFF
            previous = projected.get(key)
            if previous is not None and previous != point:
                return message(previous).hex(), message(point).hex(), evaluations
            projected.setdefault(key, point)
            next_points.append(image)
        points = next_points
    return None, None, evaluations


def main():
    request = json.load(sys.stdin)
    experiment_id = request.get("experiment_id")
    if request.get("schema_version") != 1 or experiment_id not in {
        "proj-r24-full-width",
        "rho-r24-w22",
    }:
        raise ValueError("unexpected request")
    if request.get("target_profile") != "sha3-256-r24-prefix-v1":
        raise ValueError("unexpected target profile")
    mask_bits = 22 if experiment_id == "rho-r24-w22" else 12
    expected_event = {
        "kind": "digest-xor-mask",
        "mask_hex": ((1 << mask_bits) - 1).to_bytes(32, "little").hex(),
        "expected_hex": "00" * 32,
    }
    if request.get("event") != expected_event:
        raise ValueError("unexpected event")
    if digest_message(b"abc") != hashlib.sha3_256(b"abc").digest():
        raise AssertionError("scalar SHA3 reference failed")
    programs, pd = regenerate_step()
    execute_step(programs, pd)
    check_record_boundaries()
    if experiment_id == "rho-r24-w22":
        rows = run_reduced_search(request["trials"], programs, pd)
        json.dump({"schema_version": 1, "trials": rows}, sys.stdout, sort_keys=True, separators=(",", ":"))
        return
    rows = []
    for trial in request["trials"]:
        a, b, evaluations = run_trial(trial["seed"], pd)
        rows.append({
            "trial": trial["trial"],
            "message_a_hex": a,
            "message_b_hex": b,
            "observations": {"evaluations": evaluations, "emitted_program_checks": 8},
        })
    json.dump({"schema_version": 1, "trials": rows}, sys.stdout, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    main()
