#!/usr/bin/env python3

"""Bounded generator for a 145,974-operation r24 step: 911bffce's frozen plan with chained 10-gate
chi rows and one flipped D complement; everything else is that entry's, unchanged."""

import base64, hashlib, json, sys, zlib

MASK64 = (1 << 64) - 1

PLAN_DATA = 'c-rk;+m0N$4Sk=ls80|nmYVgN%Wf73;(f>usCzfSBF;K+{QpQxBBdksjP1Y<&<%8Bz0*^pk|>foJfuqX>Emzt{YD(a%kLjImhHp8KmF^&FTZZGefs#@<)0gE@AH2?`S;&HeEP?S_rGl6<p<hmKPZH7=q3Dm{VBv0I7nckNOJuWm_ty#{w-VrY1l*g&esOz|MerGfB5A`+5)YY%XjhS?L#uR_{`_!haWfI+IKywFxRfGa!Szaf7H8C(l!Ry|I|j<%a{6%DAb$FFGWl$m#)`Ti^!?|9*J}7EY)@ri0hr@lFOX0`YK)3mV00|G2=GG-d~-dsL2Y~*tNCe#ddS=kWhJU5)S|Kr-&)ra*?5D8a7ij;4Jfevu@!#e~Os<hQhQ@o<(Z5q++E>L$4`@sy220qlC}Q3|r~Y49{Ywt+tpAD<}zn)ga^ZJ+vvSHc!@TLT{osZoBH0P-dyW&#mLPiD_QXi<st0uR5HX$g;|<uNb>tJHAGnH1|Yb<D183gVJjgldd;vKFX8d$fE1FSNhj2ad}fr3g3NY{$G|l(Syjz4<cuL5IN;R<lG-b&h#L1o*qO_eGoa1$B>gBBp&gD#3O!?c*H#($=hu3hU-iWOO{NfaCv@(1wr;n^KgS$T~oSB%!q|8A<*#h^Iv}2zW?-}pKo-ZVitOu<sQw#PqW;kS>n?y_h=S*n&lqNvOmpok7h|vv)rRuPEWJkqgnK6mU}eI@ifa_rjyS!|32;V%=7QlF3&{&KJD_%^zYLy&s6_D?efg^@6#^NWdA<x^33+{(=N|+|32;V%=hooF8s{*@6#^NeE&Y}^33<|(=N|^|L*Mar$7I3<E@;k$Vaf#QR88>a@`IC)PqXr@^?F#RQ{E}C$_fI&bN#+E`ds0wLT8JrhYGtv3y+rS&k2#tbMjIlJ#B36qCjJ^>M|nl{T`sYgGmwW67o6pJ9&vNokftxZMMD>M~^bu0B4s@yfN69X&fsJA0MvR8%=#A^udL>7dLnU#~~#E1-_;dJ04L<+xQj)spQjnu^IKqYu<cwj1l1rOl<auk)pL$jqNN<Yi2^d06ag$G9lloQt08xHL|+xc{izklL}lV0O%QXr;)NXw0SjUi9yNl40KN6HLRul8pKE@wNI-OyE~&SF=m&PseemxcE}{@!=b>w!I2-(2&vlNcJ6{->fp2o!$3D!H3{LO@?v7*VzBY)}DEiGx~aAILB4>WzVAKGJb4pN5PNLuf@ha^Q;f_d2bs`r#bXfL*+DEx0U^j(uAq9MU%;FQ*GhC5f;5G_*7{x=Chf{80vNf`xRfP_nA-IdaD>#bWzvnKE|mq7`Lp$O|n5yX_l5{ufAkMTjEueqq&7G*I3O!O&$St+bKzki`%-3x|pttVurl8b^(@uJvqp23GVG)RvD0y!Ig9|s{r)6+QgSKk85eUUwvr;q?Gxmqs_HKtsU<?hXF^W?WsA(1W^&@nO$c9d%jG&Teo&(@YX|v7_=7Gt_N(%<Th8VveB4__pb^e2jEI&EHO2RVpt|8SSqSRAG*M1=3#@#1D1VRCs-z^?=tU9Q|KuNn|<Elq+`4g#`1wB*CEIC$EIHuJQoSRr)^$`*`?aSVR(^K0N%>-t~xw|A2+V!l<-@1x6IpVgo4i>VZeBq%kI9o!dxEhI1IZue4ZiPbe-y~U-#qPLk`%HWnPmf569Xd-feqATbYg=)=^g;lGQ?zhd)_hwD_jLI&|5@A@~@wAw@$7_jTp?5lzk$=oPU6A=GiF!k}!<V5;iMzYDM*>d~dTW3u0Und9<B)+8_#ANG@H_;Xg67pB7=LA1May?+NcRB(NVD1fdSIZwV!XvliQ8j&f&b&N<h9(VHra}tm(qAMCyS|lFK3!*Exw%zTM3<yEDj=&nL9cbvl)#Q=Sm<%CAsWSxEla1r-D*%I3aI*yV@%gGw@L5@&7|Rh4kvxx$ZtAd_Y#AwBV}L(jsw@M#lgU}eiQwXHduRD)zFjizpV9o`+Fy)zPeizb`8h)un7`YzXA{m^m!&F=8WcZ_XIu+m3de+@fsJt@<CD=RIlQ?}*Q|lTZ!29TV?YM4&bqU?16ycuwnoO-kS=6kg%w5tDqRoGY87p<WH7vhsf6&!bGYRpXYh<N0p2juC>qe|Yvv}@<*`<rW$!S@3WNLRCRLglg1eP5GRn*HMEE+483u?_9^u$TtR@tTjyhDe6TqxT1R5rg1xD&}YkkH9$!&tAC-8f52WJyICLQiZd>b`8qtx-8!wjqL{vIZfg^05;bM*;Yuw5Meo|h$n^C}`%a<4Pwqw55V(wG=`Xy@)C)ET{9!SIj)0(_Z8iz^JpglKkUn|}r<GdnSlq@6G{_96)1E}Ii%9C>M1+ZY2+z&sQn)uBlN=Dpo%(HRyr*a|~cS8;^jys+0~;i|v}+JSfQ&pC0VHN+~7BFb(IatGKm2y1I)pTl(8=i(AC{*Iw#q6#|ORTg-vbLY8;by%NA7@>|KD?BgkZ=xBVg^V~?W%d^m=|VvQ;7TCCAa45dzwHptv@!C?z*JR7sH=q&SbL?2q<PLB3T9OpOk1y&2)Kxh1khgf6PyitR9<s(n<_iI6zVGK5aG#2GKkbA@_8~IU^xn?I9r=_`C#2BcvP3!g#wJ@?Guc#LsAz3%H55e0n0-05kez`jT1!WfKa2OPK3!h)>5-AH%{Z805vX8VC(!Z4XRf6u8@$2yQVpbC17C@**P-86C`1!7}24@5*pDFnH6M65a}&3iU>&==ACJVECJZZ+7vP;WE04a03N7@DIUpXhdijGI;8F}&kEf<5@~1q0`^M~1~S&rfT7-GK1<@to)}Vx-6r#4axZKu&8&|-1Wydo<T%3`I%ATH;YUVD6RX*(`MxK<Sp4YompRGCtb~z1S;659MXS2LO;BfWzOH(vL8A}B!a=yDX%4T4jhA5mAb=0Et!pe6)WU`s44yWu3wdoKExC9`cU(%VSn~H0c>r;)a#m5XHWGkMy|xX43^2mqcbm={f!zH{0^XMz&9x)}rXjFQ72TI6h>aPbp_FME;Bqw&vK{>C5qK^4Cu3N}pRu0U+w0`^bOv@|eMfjfTz#_^G6R=8k(HPSdmgrJ?nVO1R1ZmJ$9<{)t+iTY90_W{35qFa2(LX9hBkLzTwKG<Od>2{;SuJL)mtJS-CqJE=0by!I5SQF1;}tz#}-2dhTV0VW=6|4hdM8rlWPt07#Y?J`hq8|3N?2lgtXMpdwok6_H~9DTHpH7nUyLeoGNo&Fe|V-pa;AbN_Z{=9iS&#AU<Ovx`g3iwR(fpTA+x_maNyii(bzPdR@XU!m@^Wi_l@!Ga+ZB0$W-Y26aPKrJ-6*P#;M;NPJ#OuE^RjGWCBvmvnEEgk@_2`zd3d)|wr|ZXb_2g+l4IC!PchMw;0e%;_fCc_iBo-#w|gG}rPdiAx7nuFh1Q$m<9x$?BpA7k#Tn=h|q8_kCuvhbLdOFbkR49+t^@fqi%b4JDf0RA8Hc84@gyy3US$E*F3$x!q2Sz^t*3>xr%|TP>_}GM8pQ;x$ZSvXhp2kZ%$7U1fwop9_RlUJ^%VqFKjW*1|~uSx>O#f;-dMmTfH<(I_nWQweOW=nPwE0;PQSPtUHd0*_=|fmtmq+_r5-fy#d#ZO$j}!~FX2dF^w?Grb&XKsSXjL#=Oxl>2?BUUp!kmw8(XlX>^88cs~#XH3|^r}Da00(%7~4-w4<tjju1K-C27S7ER|Cril^ZGV7b$KAT(LPZ6(b&{7|w~`nY#+RCWwJ*j8H*6V^?fi9kppoE~Yc)bdLvLUbWl5fBFi7RO?onBq?FM7{x~N6s90_Z(sZCvh`U4xJmf#tys+;pc=OjlwnTmZA-zU~w^J1p7G501+)m?p2>M`mZo@Z8lc>NGy#~&Eth5_Z3(p46+2OnxZmMs~u;@h+gtlw<W)Y(&!J?hwIAb@jc?ZI@8TRv(E+>IXUF&0NjyvdT!Dx;W;?LD>j7H6v$na`$C6K=L@LR6dOWXYP?zLbTsUc08j2>n3}e=w?U3+yednNN{Tka`JS+k+kDHQLD&(%tseuKgY6Q;`RgNKo^t_nS<v=L(Z?K#3@XloEa+!Bp<N!wVBsvY7rLmqD0Va$eyynjcuk<M7|>^tLW)c5#`WRwDnG)#Nq#T^E83$-i4-UfL-zz{4OfL%kW^l}+TusH25!*rs7*z0U4>7<Jnm24glx#T6Ohw9ccYCDreu=_{pa?j(8C2YX$d8aCzJe9v*<<*)DF{d}c^Cw}?q56f%kN|SPxw&fA9dUZUT+gwb~<!apKmmn*Zt1|VVc6FcH7BDJTZ_Z#<$<`A<8eZQ0?cLuE!9Vk0<m-Q%-@PrbH~-=rm|y#R?)BR6R370w&c|EB`78USH>Bj7vA!tlYh6u!9=G$Lk?wr$>%?V|P!>sOnLU4l-i7#$(O<KESX%2B$H5l#@?XL{!x;'
def _public_plan(path=None):
 records = {}
 text = zlib.decompress(base64.b85decode(PLAN_DATA)).decode()
 for raw in text.splitlines():
  fields = raw.split()
  if not fields: continue
  kind = fields[0]
  if kind in {'trial','F1','G1'}: records[kind] = fields[1]
  elif kind in {'FG','PHI','DEC','IB','ONOT'}: records[(kind,int(fields[1]))] = fields[2:] if len(fields)>3 else fields[2]
  elif kind == 'LOOP': records[kind] = tuple(map(int,fields[1:]))
  elif kind == 'nr': records['nr'],records['optmode'] = int(fields[1]),int(fields[3])
 if records.get('nr') != 24 or records.get('LOOP') != (8,72): raise AssertionError('bad frozen plan')
 return records

MASK256 = (1 << 256) - 1

NC = -1

O_IN, O_XOR, O_AND, O_OR, O_NOT = range(5)

NREG = 4096

RC = (1, 32898, 9223372036854808714, 9223372039002292224, 32907, 2147483649, 9223372039002292353, 9223372036854808585, 138, 136, 2147516425, 2147483658, 2147516555, 9223372036854775947, 9223372036854808713, 9223372036854808579, 9223372036854808578, 9223372036854775936, 32778, 9223372039002259466, 9223372039002292353, 9223372036854808704, 2147483649, 9223372039002292232)

RHO = (0, 1, 62, 28, 27, 36, 44, 6, 55, 20, 3, 10, 43, 25, 39, 41, 45, 15, 21, 8, 18, 2, 61, 56, 14)

KL = (0, 0, 3267622025928250900, 0, 0, 18446744073709551615, 0, 0, 0, 0, 18446744073709551615, 10040277543336838531, 0, 9631824790095807170, 16812933060745426165, 18446744073709551615, 9223372036854775814, 0, 0, 0, 0, 0, 0, 0, 0)

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
            a, b = (b, a)
        key = (op, a, b)
        n = self.cons_table.get(key)
        if n is not None:
            return (n, False)
        n = self.new_node(op, a, b)
        self.cons_table[key] = n
        return (n, True)

    def xor(self, left, right):
        an, ap = left
        bn, bp = right
        if an == NC:
            return (bn, bp ^ ap)
        if bn == NC:
            return (an, ap ^ bp)
        if an == bn:
            return (NC, ap ^ bp)
        am = self.linear[an]
        bm = self.linear[bn]
        if am is not None and bm is not None:
            mask = tuple((x ^ y for x, y in zip(am, bm)))
            k = self.k[an] ^ self.k[bn]
            if not any(mask):
                return (NC, k ^ ap ^ bp)
            n = self.form_nodes.get(mask)
            if n is not None:
                return (n, k ^ ap ^ bp ^ self.k[n])
            n, _ = self.cons(O_XOR, an, bn)
            self.k[n] = k
            self.linear[n] = mask
            self.form_nodes[mask] = n
            return (n, ap ^ bp)
        n, _ = self.cons(O_XOR, an, bn)
        return (n, ap ^ bp)

    def complement(self, value):
        n, p = value
        if n == NC:
            return value
        out, created = self.cons(O_NOT, n, 0)
        if created and self.linear[n] is not None:
            self.linear[out] = self.linear[n]
            self.k[out] = self.k[n] ^ 1
        return (out, p ^ 1)

    def and_value(self, left, right, select):
        an, ap = left
        bn, bp = right
        if an == NC:
            return right if ap else (NC, 0)
        if bn == NC:
            return left if bp else (NC, 0)
        if an == bn:
            return left if ap == bp else (NC, 0)
        if not ap and (not bp):
            return (self.cons(O_AND, an, bn)[0], 0)
        if ap and bp:
            return (self.cons(O_OR, an, bn)[0], 1)
        plain = an if not ap else bn
        other = bn if not ap else an
        if select:
            negated = self.complement((plain, 0))
            return (self.cons(O_OR, negated[0], other)[0], 1)
        term = self.cons(O_AND, plain, other)[0]
        return self.xor((plain, 0), (term, 0))

def term_cost(a, b):
    if a[0] == NC or b[0] == NC or a[0] == b[0]:
        return 0
    return 1 if a[1] ^ 1 == b[1] else 2

def dynamic_row(graph, row, need):
    distinct = all((v[0] != NC for v in row)) and len({v[0] for v in row}) == 5
    best = None
    for trick in range(-1, 5 if distinct else 0):
        if trick >= 0 and (not need >> trick & 1 or not need >> (trick + 1) % 5 & 1):
            continue
        for subset in range(32):
            values = list(row)
            cost = 0
            for x in range(5):
                if subset >> x & 1:
                    if row[x][0] == NC:
                        cost = 1 << 29
                    else:
                        values[x] = (values[x][0], values[x][1] ^ 1)
                        cost += 1
            for x in range(5):
                if not need >> x & 1:
                    continue
                if x == trick:
                    k = (trick + 1) % 5
                    p1, p2 = (values[(k + 1) % 5], values[(k + 2) % 5])
                    if p1[1] ^ 1 == p2[1]:
                        bk = (values[k][0], values[k][1] ^ (p1[1] ^ 1))
                        cost += term_cost(bk, values[(x + 2) % 5])
                    else:
                        cost += 1
                else:
                    cost += term_cost(values[(x + 1) % 5], values[(x + 2) % 5])
            candidate = (cost, subset, trick)
            if best is None or candidate[0] < best[0]:
                best = candidate
    _, subset, trick = best
    row = list(row)
    for x in range(5):
        if subset >> x & 1:
            row[x] = graph.complement(row[x])
    out = [None] * 5
    k = (trick + 1) % 5
    if trick >= 0:
        first = (row[(k + 1) % 5][0], row[(k + 1) % 5][1] ^ 1)
        out[k] = graph.xor(row[k], graph.and_value(first, row[(k + 2) % 5], 0))
    for x in range(5):
        if not need >> x & 1 or (trick >= 0 and x == k):
            continue
        first = out[k] if x == trick else row[(x + 1) % 5]
        first = (first[0], first[1] ^ 1)
        out[x] = graph.xor(row[x], graph.and_value(first, row[(x + 2) % 5], 0))
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
            value = graph.xor(parity[64 * ((x + 4) % 5) + z], parity[64 * ((x + 1) % 5) + (z + 63 & 63)])
            if dnot is not None and dnot[64 * x + z]:
                value = graph.complement(value)
            delta[64 * x + z] = value
    return delta

def build_prefix(plan):
    graph = Graph(256, True)
    state = [(NC, KL[lane] >> z & 1) for lane in range(25) for z in range(64)]
    for z in range(64):
        state[64 + z] = (z, 0)
        state[6 * 64 + z] = (64 + z, 0)
        state[4 * 64 + z] = (128 + z, 0)
        state[9 * 64 + z] = (192 + z, 0)
        state[11 * 64 + z] = graph.xor(graph.xor((z, 0), (64 + z, 0)), (NC, KL[11] >> z & 1))
        state[14 * 64 + z] = graph.xor(graph.xor((128 + z, 0), (192 + z, 0)), (NC, KL[14] >> z & 1))
    for round_index in range(2):
        delta = theta(graph, state, plan[0] if round_index else None, plan[1] if round_index else None)
        new_state = list(state)
        for y_out in range(5):
            for z in range(64):
                row = []
                for x_out in range(5):
                    y = x_out
                    x = (3 * y_out + x_out) % 5
                    zz = z - RHO[x + 5 * y] & 63
                    row.append(graph.xor(state[64 * (x + 5 * y) + zz], delta[64 * x + zz]))
                out = dynamic_row(graph, row, 31)
                for x_out in range(5):
                    new_state[64 * (x_out + 5 * y_out) + z] = out[x_out]
        for z in range(64):
            n, p = new_state[z]
            new_state[z] = (n, p ^ RC[round_index] >> z & 1)
        state = new_state
    if any((value[0] == NC for value in state)):
        raise AssertionError('constant prefix output')
    return (graph, [v[0] for v in state], bytes((v[1] for v in state)))

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
        value = graph.xor(get_parity((x + 4) % 5, z), get_parity((x + 1) % 5, z + 63 & 63))
        if dnot is not None and dnot[index]:
            value = graph.complement(value)
        delta[index] = value
    return delta[index]

def allocate(graph, outputs, output_regs, input_regs):
    count = len(graph.op)
    input_count = len(input_regs)
    live = bytearray(count)
    output_index = [-1] * count
    reserved = bytearray(NREG)
    for j, node in enumerate(outputs):
        if node < input_count or output_index[node] >= 0:
            raise AssertionError('invalid/shared output')
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
    free_regs = [r for r in range(NREG - 1, -1, -1) if not busy[r] and (not reserved[r])]
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
                raise AssertionError('fixed output register busy')
        else:
            destination = free_regs.pop()
        busy[destination] = 1
        reg[i] = destination
        encoded = 0 if op == O_XOR else 1 if op == O_AND else 2 if op == O_OR else 3
        program.append((encoded, destination, reg[a], 0 if op == O_NOT else reg[graph.b[i]]))
        mix[encoded] += 1
    return (program, tuple(mix))

def _hex_bits(text, count):
    value = int.from_bytes(bytes.fromhex(text), 'little')
    return bytes((value >> bit & 1 for bit in range(count)))

def _row_choice(row, need):
    """Return the cheapest complement subset and 10-gate position."""
    distinct = all((value[0] != NC for value in row)) and len({value[0] for value in row}) == 5
    winner = None
    for trick in range(-1, 5 if distinct else 0):
        if trick >= 0 and (not need >> trick & 1 or not need >> (trick + 1) % 5 & 1):
            continue
        for subset in range(32):
            values = list(row)
            cost = 0
            for x in range(5):
                if subset >> x & 1:
                    if row[x][0] == NC:
                        cost = 1 << 29
                    else:
                        values[x] = (values[x][0], values[x][1] ^ 1)
                        cost += 1
            for x in range(5):
                if not need >> x & 1:
                    continue
                if x == trick:
                    k = (trick + 1) % 5
                    left = values[(k + 1) % 5]
                    right = values[(k + 2) % 5]
                    if left[1] ^ 1 == right[1]:
                        substitute = (values[k][0], values[k][1] ^ (left[1] ^ 1))
                        cost += term_cost(substitute, values[(x + 2) % 5])
                    else:
                        cost += 1
                else:
                    cost += term_cost(values[(x + 1) % 5], values[(x + 2) % 5])
            candidate = (cost, subset, trick)
            if winner is None or candidate[0] < winner[0]:
                winner = candidate
    return (winner[1], winner[2])

def _selected_terms(pattern, subset, trick, compact):
    """Expand compact mixed-term polarity bits into one bit per output."""
    polarity = [pattern >> x & 1 ^ subset >> x & 1 for x in range(5)]
    selected = [0] * 5
    output_polarity = [0] * 5
    bit = 0
    k = (trick + 1) % 5
    for x in range(5):
        if x == trick:
            continue
        left = polarity[(x + 1) % 5] ^ 1
        right = polarity[(x + 2) % 5]
        term = left if left == right else compact >> bit & 1
        if left != right:
            selected[x] = term
            bit += 1
        output_polarity[x] = polarity[x] ^ term
    if trick >= 0:
        left = output_polarity[k] ^ 1
        right = polarity[(trick + 2) % 5]
        if left != right:
            selected[trick] = compact >> bit & 1
    return selected

def _emit_planned_row(graph, row, subset, trick, selected, need=31):
    values = list(row)
    for x in range(5):
        if subset >> x & 1:
            values[x] = graph.complement(values[x])
    output = [None] * 5
    k = (trick + 1) % 5
    if trick >= 0:
        first = (values[(k + 1) % 5][0], values[(k + 1) % 5][1] ^ 1)
        term = graph.and_value(first, values[(k + 2) % 5], selected[k])
        output[k] = graph.xor(values[k], term)
    for x in range(5):
        if not need >> x & 1 or (trick >= 0 and x == k):
            continue
        first = output[k] if x == trick else values[(x + 1) % 5]
        first = (first[0], first[1] ^ 1)
        term = graph.and_value(first, values[(x + 2) % 5], selected[x])
        output[x] = graph.xor(values[x], term)
    return output


# ---- Chained 10-gate rows (this derivative). The identity ~out[k] & b[k+1] == ~b[k] & b[k+1] holds for every
# position, so a row may compute several outputs from already-computed outputs; the chain is resolved from a
# plainly computed position backwards. The table below is the least cost over complement subset, trick set
# and mixed-term polarities for every (input pattern, output polarity vector), built once and verified
# against chi on every input value before use. Rows are built from it with the frozen plan's output vector
# pinned, so the polarity flow into the next round is unchanged.

PLAN_DELTA = {9: (177,)}   # D complement flipped in the closing body's round (index 64*x+z: x=2, z=49)

def _chain_order(tricks):
    start = next((x for x in range(5) if not tricks >> x & 1))
    return [(start - i) % 5 for i in range(5)]

def _row_cost(pattern, subset, tricks, selected):
    pol = [(pattern >> x & 1) ^ (subset >> x & 1) for x in range(5)]
    cost = bin(subset).count('1')
    q = [None] * 5
    for x in _chain_order(tricks):
        lit = (q[(x + 1) % 5] ^ 1) if tricks >> x & 1 else (pol[(x + 1) % 5] ^ 1)
        other = pol[(x + 2) % 5]
        if lit == other:
            cost += 1
            term = other
        else:
            cost += 2
            term = selected >> x & 1
        q[x] = pol[x] ^ term
    return (cost, sum((q[x] << x for x in range(5))))

def _row_check(pattern, subset, tricks, selected, bits):
    """Execute the construction on concrete bits through the polarity interpretation; return chi outputs."""
    w = [(bits >> x & 1) ^ (pattern >> x & 1) for x in range(5)]
    pol = [pattern >> x & 1 for x in range(5)]
    for x in range(5):
        if subset >> x & 1:
            w[x] ^= 1
            pol[x] ^= 1
    ow, op = [None] * 5, [None] * 5
    for x in _chain_order(tricks):
        if tricks >> x & 1:
            lw, lp = ow[(x + 1) % 5], op[(x + 1) % 5] ^ 1
        else:
            lw, lp = w[(x + 1) % 5], pol[(x + 1) % 5] ^ 1
        rw, rp = w[(x + 2) % 5], pol[(x + 2) % 5]
        if lp == rp:
            tw, tp = (lw & rw, 0) if lp == 0 else (lw | rw, 1)
        else:
            pw, ow_ = (lw, rw) if lp == 0 else (rw, lw)
            tw, tp = ((pw ^ 1) | ow_, 1) if selected >> x & 1 else (pw ^ (pw & ow_), 0)
        ow[x], op[x] = w[x] ^ tw, pol[x] ^ tp
    return [ow[x] ^ op[x] for x in range(5)], sum((op[x] << x for x in range(5)))

_CHAIN_TABLE = None

def _chained_table():
    global _CHAIN_TABLE
    if _CHAIN_TABLE is None:
        table = {}
        for pattern in range(32):
            for subset in range(32):
                for tricks in range(31):
                    for selected in range(32):
                        cost, q = _row_cost(pattern, subset, tricks, selected)
                        key = (pattern, q)
                        cand = (cost, bin(tricks).count('1'), bin(subset).count('1'), subset, tricks, selected)
                        if key not in table or cand < table[key]:
                            table[key] = cand
        if len(table) != 1024:
            raise AssertionError('chained row table is incomplete')
        for (pattern, q), (cost, _, _, subset, tricks, selected) in table.items():
            for bits in range(32):
                b = [bits >> x & 1 for x in range(5)]
                truth = [b[x] ^ (b[(x + 1) % 5] ^ 1) & b[(x + 2) % 5] for x in range(5)]
                values, qq = _row_check(pattern, subset, tricks, selected, bits)
                if values != truth or qq != q:
                    raise AssertionError('chained row construction does not compute chi')
        _CHAIN_TABLE = table
    return _CHAIN_TABLE

def _emit_row_chained(graph, row, subset, tricks, selected):
    values = list(row)
    for x in range(5):
        if subset >> x & 1:
            values[x] = graph.complement(values[x])
    output = [None] * 5
    for x in _chain_order(tricks):
        first = output[(x + 1) % 5] if tricks >> x & 1 else values[(x + 1) % 5]
        first = (first[0], first[1] ^ 1)
        term = graph.and_value(first, values[(x + 2) % 5], selected >> x & 1)
        output[x] = graph.xor(values[x], term)
    return output

def _public_body(input_p, cnot, dnot, decisions, folded_iota, output_not=None, pinned=None, record=None):
    graph = Graph(1600)
    state = [(plane, input_p[plane]) for plane in range(1600)]
    output_state = list(state)
    parity = [None] * 320
    delta = [None] * 320
    for y_out in range(5):
        for z in range(64):
            row = []
            for x_out in range(5):
                y = x_out
                x = (3 * y_out + x_out) % 5
                zz = z - RHO[x + 5 * y] & 63
                d = lazy_delta(graph, state, parity, delta, cnot, dnot, x, zz)
                row.append(graph.xor(state[64 * (x + 5 * y) + zz], d))
            pattern = sum((value[1] << x for x, value in enumerate(row)))
            if pinned is None:
                decision = decisions[64 * y_out + z]
                subset = decision & 31
                trick = (decision >> 5 & 7) - 1
                selected = _selected_terms(pattern, subset, trick, decision >> 8)
                built = _emit_planned_row(graph, row, subset, trick, selected)
            else:
                subset, tricks, selected = _chained_table()[pattern, pinned[64 * y_out + z]][3:]
                built = _emit_row_chained(graph, row, subset, tricks, selected)
            if record is not None:
                record.append(sum((built[x][1] << x for x in range(5))))
            for x_out in range(5):
                value = built[x_out]
                if output_not is not None and output_not[64 * y_out + z] >> x_out & 1:
                    value = graph.complement(value)
                output_state[64 * (x_out + 5 * y_out) + z] = value
    for z in range(64):
        node, polarity = output_state[z]
        output_state[z] = (node, polarity ^ folded_iota >> z & 1)
    return (graph, [value[0] for value in output_state], bytes((value[1] for value in output_state)))

def _public_end(input_p, cnot, dnot, phi):
    graph = Graph(1600)
    state = [(plane, input_p[plane]) for plane in range(1600)]
    parity = [None] * 320
    delta = [None] * 320
    nodes = [0] * 256
    polarities = bytearray(256)
    for z in range(64):
        row = []
        for x_out in range(5):
            x = y = x_out
            zz = z - RHO[x + 5 * y] & 63
            d = lazy_delta(graph, state, parity, delta, cnot, dnot, x, zz)
            row.append(graph.xor(state[64 * (x + 5 * y) + zz], d))
        subset, trick = _row_choice(row, 15)
        values = list(row)
        for x in range(5):
            if subset >> x & 1:
                values[x] = (values[x][0], values[x][1] ^ 1)
        selected = [phi[64 * x + z] for x in range(5)]
        if trick >= 0:
            k = (trick + 1) % 5
            left = values[(k + 1) % 5]
            right = values[(k + 2) % 5]
            selected[k] = values[(trick + 2) % 5][1] ^ 1 ^ values[k][1] if left[1] ^ 1 != right[1] else 0
        built = _emit_planned_row(graph, row, subset, trick, selected, 15)
        for x_out in range(4):
            node, polarity = built[x_out]
            if x_out == 0:
                polarity ^= RC[23] >> z & 1
            index = 64 * x_out + z
            nodes[index] = node
            polarities[index] = polarity
    return (graph, nodes, bytes(polarities))

def reproduce_public_step(plan_path='step-plan.txt'):
    plan = _public_plan(plan_path)
    f1 = _hex_bits(plan['F1'], 320)
    g1 = _hex_bits(plan['G1'], 320)
    graph, outputs, prefix_p = build_prefix((g1, f1, bytes(320)))
    programs = {}
    programs['P'], prefix_mix = allocate(graph, outputs, list(range(256, 1856)), list(range(256)))
    body_counts = []
    body_mixes = []
    input_p = prefix_p
    round22_p = None
    folded = []
    for body in range(8):
        round_index = body + 2
        fg = plan['FG', round_index]
        dnot = _hex_bits(fg[0], 320)
        cnot = _hex_bits(fg[1], 320)
        raw = bytes.fromhex(plan['DEC', round_index])
        decisions = [raw[2 * index] | raw[2 * index + 1] << 8 for index in range(320)]
        iota = int(plan['IB', body], 16)
        folded.append(iota)
        output_not = None
        if body == 7:
            output_not = bytes.fromhex(plan['ONOT', round_index])
        pinned = []
        _public_body(input_p, cnot, dnot, decisions, iota, output_not, record=pinned)
        for index in PLAN_DELTA.get(round_index, ()):
            dnot = bytes((bit ^ (1 if i == index else 0) for i, bit in enumerate(dnot)))
        graph, outputs, output_p = _public_body(input_p, cnot, dnot, decisions, iota, output_not, pinned=pinned)
        input_base = 1856 if body & 1 else 256
        output_base = 256 if body & 1 else 1856
        program, mix = allocate(graph, outputs, list(range(output_base, output_base + 1600)), list(range(input_base, input_base + 1600)))
        programs[f'B{body + 1}'] = program
        body_counts.append(len(program))
        body_mixes.append(mix)
        input_p = output_p
        if body == 4:
            round22_p = output_p
    if input_p != prefix_p:
        raise AssertionError('the eight-body polarity cycle does not close')
    fg = plan['FG', 23]
    phi = _hex_bits(plan['PHI', 23], 1600)
    graph, outputs, end_p = _public_end(round22_p, _hex_bits(fg[1], 320), _hex_bits(fg[0], 320), phi)
    programs['E'], end_mix = allocate(graph, outputs, list(range(256)), list(range(1856, 3456)))
    pd = tuple((sum((end_p[64 * lane + bit] << bit for bit in range(64))) for lane in range(4)))
    runs = (3, 3, 3, 3, 3, 2, 2, 2)
    iota_ops = sum(((RC[round_index] ^ folded[(round_index - 2) % 8]).bit_count() for round_index in range(2, 23)))
    calls_and_returns = 42
    executed = len(programs['P']) + len(programs['E']) + iota_ops + calls_and_returns
    executed += sum((runs[index] * body_counts[index] for index in range(8)))
    prog_instructions = len(programs['P']) + len(programs['E']) + 21 + iota_ops
    body_instructions = sum(body_counts) + 8
    result = {'prefix': len(programs['P']), 'prefix_mix': prefix_mix, 'bodies': body_counts, 'body_mixes': body_mixes, 'end': len(programs['E']), 'end_mix': end_mix, 'iota': iota_ops, 'calls_and_returns': calls_and_returns, 'executed': executed, 'prog_instructions': prog_instructions, 'body_instructions': body_instructions, 'stored_instructions': prog_instructions + body_instructions, 'pd': pd}
    return (programs, result)

def emit_public_binaries(programs, plan_path='step-plan.txt'):
    """Pack the two static step blocks in the declared 39-bit format."""
    plan = _public_plan(plan_path)
    folded = [int(plan['IB', body], 16) for body in range(8)]
    body_words = []
    offsets = []
    for body in range(8):
        offsets.append(len(body_words))
        body_words.extend(programs[f'B{body + 1}'])
        body_words.append((5, 0, 3528, 0))
    prog_words = list(programs['P'])
    for round_index in range(2, 23):
        body = (round_index - 2) % 8
        offset = offsets[body]
        prog_words.append((4, 3528, offset & 4095, offset >> 12))
        output_base = 1856 if not body & 1 else 256
        difference = RC[round_index] ^ folded[body]
        for bit in range(64):
            if difference >> bit & 1:
                prog_words.append((3, output_base + bit, output_base + bit, 0))
    prog_words.extend(programs['E'])
    if len(prog_words) != 6811 or len(body_words) != 53064:
        raise AssertionError('packed block instruction count mismatch')

    def pack39(words):
        output = bytearray()
        accumulator = 0
        bits = 0
        for opcode, destination, left, right in words:
            if opcode >= 8 or max(destination, left, right) >= 4096:
                raise AssertionError('packed instruction field overflow')
            accumulator |= (opcode | destination << 3 | left << 15 | right << 27) << bits
            bits += 39
            while bits >= 8:
                output.append(accumulator & 255)
                accumulator >>= 8
                bits -= 8
        if bits:
            output.append(accumulator)
        return bytes(output)
    return (pack39(prog_words), pack39(body_words))

EXPECTED_PROG = 'de85b18a14cfd66b9916d350a5e72fef6225cc57fdb4e06fa32539de58bbf6de'
EXPECTED_BODY = 'fc869df5cba74abcf373ae4b112f236c423f798320820f8d460bf8c18f37a33b'
def generate():
 programs,result = reproduce_public_step()
 prog,body = emit_public_binaries(programs)
 if len(prog)!=33204 or hashlib.sha256(prog).hexdigest()!=EXPECTED_PROG: raise AssertionError('prog mismatch')
 if len(body)!=258687 or hashlib.sha256(body).hexdigest()!=EXPECTED_BODY: raise AssertionError('body mismatch')
 if result['executed']!=145974 or result['stored_instructions']!=59875: raise AssertionError('ledger mismatch')
 return prog,body,result
def main():
 prog,body,result = generate()
 if len(sys.argv)==2:
  from pathlib import Path
  out=Path(sys.argv[1]); out.mkdir(parents=True,exist_ok=True); (out/'prog.bin').write_bytes(prog); (out/'body.bin').write_bytes(body)
 print(json.dumps({'prog_sha256':hashlib.sha256(prog).hexdigest(),'body_sha256':hashlib.sha256(body).hexdigest(),**result},sort_keys=True))

# build_package.py prepends the standalone step generator and replaces CONTROL_DATA.
CONTROL_DATA = 'c-rmVXLMEN*2VF;({n-y$<iwULI)d7u~+Phz4xxzd#}V^KoBb+b`iyb1(n`=w`0Su*n2PBoh**`jw^GnyvB_2elQ=%82qxI{p^}^bpH>{=axc!Rm@rL3GoHN^0NbfR(tNeQuz}VrHNdAC7?7BBV;`ZJSXtn!1Dsn54<4oLgFQ*N$nmgB3@qPK5F|F`@hmfYn+W=0lok8N|L#y;%8Q>J+%_L{#sABZ`2Me_R58RY@3q<R8l)SJ$-Ao-!0MGZ_w-CkgUJy^6$&YS5Z+izjPiyKeOx4u<ct=T6+bG?W^_Wi&rn{wxnw6sG>iO-<B+2wfuXAcurn205|aCpL$+$W8gOheskcr1b%Da0|Orv_~5{A3w%i6w+DVl;CBXoSKxOCeox@{27X`QLj%7*@L_>J5cq?E4-fpIz#k6$k-#4fd_>@n1^#&8PXzvC;3ETnD)6TRe<tuzfsYP+OyFY!9~b!ez$XMgG4M%&PY!%a;8O#i7WnkQX9PYo@L7S+4t!4Fa|53j`24^Z1imovMS(vX_;Z0jANUJ_zZm#SfxjI1;=o@C{MEo;3;gxK-w1q3;BN;0R^V?3{!ZZU2L4{)?+5-t;2#FQH1LlC|2XhZ0{=Ad&jSBE@GpcX>HCj7{{AdCNx#(l^Wx-s_5Lr(q{|oc5o(54Bc$W^m*XdT{B-$#a`|Gtd`>3af@uEz<ovIz=luIN`273I`S)q?_4kqMzqTRQpPrr>b$*xRB(v4~>n26|`iS1YuLRWo*Qrt42~P(YtvnrjjPhJytnxfyobr5Nyz&BIg7QLOqVghOlJa6;vhoZtMR^G@Re2*|n)37jO;_F+n4!E3n5n!8FiUwkFk5*AFh{uobCsum%u~KHFkg9kk}puc3b0UlQ(%$u%JdKA&4A~WHwT_q-U4_*c@^-Y@|M6$%3A?1D{l=fR^A49MR{A`Rpsq~*Oa#hURT}$ctd$dV2Scofj5<}2E3(wb>MB~YXI*kUlVv&c_-jK<(+}|m3IL?P~H{zP<c0Csq(dekCd+se5|}X@QLzufKQdL3w)-0J>YZY>jPgX-vIbh`G&w($~OYOR=zRtjq*)^Z<TKfe5ZUf;Ctnp13xJ50sN?Z3*aZ^TLM2T-wOCe`PRU%%C`Z2Q@$<myYkeQDX;l|Kido6A$|R&yl474Px+4N>qzB00eQ-I2J)5f0u(6U6)04`TlykV`R+im@;%bmm&*4{U&kun3uvT#Z=h89K0ssT`vPUk_e)<#E8ia|SAGCcq5MF=lpmCSSAH<CvhqXH*ZIm11y)gh7|>Mt;XtMGBY<Ygj|7@4KMH7}{Ai#`c`u-)@?(Hj%8vzFD?bisqx^WFt@0CqcFIo#+ABW^=%D;$pri6rfK`>B3aqC5G+=e*rvqy!KLc1(`I$f`<!1q%m7fiCQGO24Rr$F<H|6I6Ybie;SX=o8KzHRA0_!Nh2v}G7#lU*Xdjsn$uLd?yehILl@=Jk@lwSsHto(9d6XjO`n<~E&*i89Vz~;)Y26`yJ2G~ORwZN9j`v6-h?+a|L{5oJ8<^6zdmG=j>Q+|E=@<;gqU<c(l06mr82<)i*CSWJ!Hv>B>zXjMu`K`dN$_E0wDIWyvu6!`Chw|HiJ(Uju_ELU3u($F%fPIwT3GA!<E?__9cLVz?zXv!#`Mtn_%I^aXQa%(oSo!_HA<BmVhbn&nI86D2z~Rb=14k%-2sl#t!@yC>9|4Y5{wUB(`3T?`<&Oc!Dt{a}PWcnS@yeeBPEbA)I8pgiz)8xV22NJ~3~-9_QNXFnM+2uR9|N4Od@OK=@^QeK%Etp|DW3qGt$ZSIj`B&sxymO4=P928oUeQ;aDnn^z=g`E0~aZu0bHznCeT~?ETCHXY~T{*bAU^g&jl`1J`cED`F!9C<qLo-l`jOYQoabdTKTiUHOij@u2ud#&`0?TKwsrA0@o>j3FxQ%WuU+E#lZE-UjYUve-*ev`D?(9%3lX=QvL>Tv+^atEy~{nZdLvkFi`p1z#!%C0E3mk3*4ssJz$9P_kr7$e*oN}{6pYQ<x7FPlz#-=t^8x)9_60^_bUGsxKH_Kz)<C%1NSTc0vM+JOW*<JUjYv){~8#s{2SmQ<=+AiEB_97MEUo?qso5(MkxOgcue_Ez~jn)2A)v<3-F}!UxAUze*>OU{yXrr@@2p?#OwO}KrwlKAnGqN#d`d*<xfZaZ<p|2^OMg<tg?K5L&*;{F81-O$@1Agqq>gsTfzRT)BJ`9^Xn1JuSXr`M~-iu<~JgkU+Z9gt;6}z^RG_x8yU>6Nie@A(fm-q`Hc?dR}{>zD41VaJ?A$em|tEnzr0|6x%Hgi)L?!&!TfT9`6cz7->hJMNiaX=jWT|JWM2DxnwVj>|LR0`Kv{m0`=9&QpN~>$ev&WeA9$vTJNqgvcJEF+r%BR8Js+1{zE?e$A5_of=l#XyD+=`QM=MP9PZTDF=^FU&&*IeoIKG7|I=_qS^85W~c7A7k{O)}HnZINGzXj{>)xhg#H<0Z52Q~2ebA$EIYvA=4u)edv&rfmxtabMMX!icOm<(WLet%^BZCOE5R=a(@>HaBGzaI-~u3vHgjIO_&n(MDv_QM5!gvk9dFUe8kS1$7VcjKVn9m4weVts$fsrmgRwlF*X8M(pu)s+o9KDopEee>U`f#=_=LB@~z?vmN1(evT|`w0k3OOIUkr|XmT;o1JW5g*?_p`p6By#C9{{Hy+WokXuM)T}}F`FRQL^K1M6IlON#nd6%9`)jSU`%m`%8r}aYbM*SR-=I<+fA;wT&45Mn^C`-G%h>i6lqcnhcn_c3C@EKWn3b1*{sr6qipIg~pW;M*f<{tv{WRh~QJ6_e60wf5jNkp~_Sbr%@1GfY|1VX)AF`i+L0?}t_SuW;x3T(si0t{*nx7vF<@u4Tk55A%-@@AWPxAGxe1BC?<6;gux#|0#{|CpX>t8%R7W6rmxU)XTa@<*;W4Z3E&#^pr*5_EhJL_|-z@7CuR_M<994m5XeU25ovp&Z%?yS$T5_i_;SR;4V=UAyb>vOEJJL_|-%$@Z)*2JClIacn@`W&lpXMK*DJL_|7C3n{6*vjs#&#`~Gvp&aGac6ywHFalwj#av|KF6B5vp&a~yR$yWTDY@5$Ew^}pJOfES)XIA+*zMvt=(ClV{P17pJQ#^S)XI=+*zMv?cG_QV;$UCpJN@}S)XI8y0bpVR&!^4j;-#_`W#!so%K1kraS9%tdl$IbF8yF>vOD&JL_|-t2^s+teZRQb8Ibl*5}yT?yS$T?(VG5v31;8pJVH~vp&bxb7y^yt?$nI9NWO1^*OeoJL_|7BX`#4*v9Ux&#_J1S)XH@y0bpVHgjivj&1JF`W)-w&iWkN!kzUwwxv7kb8IVj*5}yP?yS$TZQNO(W81p3KF79mXMK)s@6P%h+rgdnIo8vi^*OeqJL_|7CwJE8*v{^(&#_(HS)XIOy0bpVc5`Qaj_vNw`W)NCo%K1kr#tI&Y%h1#=h)uvtk1E1+*zMv`?|9}$M$n)eU9z#&iWiXz@7CucAz`!bL=2@*5}y4?yS$TL)=-PV~4u4KF1DoXMK(x?#}ugJHnmyId-Hw>vQZVch=|F(eA9zv0m=1&#`0NS)XIay0bpVj&o;yjvepL`W!pKo%K0(qC4wz>?C*A=h(^atk1Di+*zMvr@FH~$4+x+eU6>(&iWiX!=3dxcBVV)bL=d4*5}yS?yS$TbKF^<W9PcFKF7{;XMK*H@6P%hyTG0GId-8t>vQZPch=|F#qO-nvEJ^i&#`KE*5}wI?yS$TOWj$YW0$$JKF2P1XMK)c;m-OTyV9NYId+vh>vQaCch=|FHSVm>v1{E~pJRR8S)XHl-C3Vw*SWJk$NIUmKF9jIvp&bJcV~T$4RB|Dj@{tS`W(B_o%K0(lRN8k>}Ge?=h!Xotk1Dq-C3Vw1KnAlV}smTpJRjFS)XIKxwAgUhPbmn$8L9LeU9DX&iWj?)1CD>c9%QrbL?(+*5}wg?yS$Td)--|WB0kUKF5Z-vp&b}cV~T$4RdFGjy>Sc`W$=Eo%K03+@19~_K-X4bL?Sv*5}wG?yS$TN8MSUV<X&IpJR`?vp&ZjcV~T$J>ky!9DCB8^*J`uo%K2PlsoHl>}hw_=h!putk1Dg?yS$T(eA9zu`%wf&#|%Ytk1D=?yS$T@$Rh8u?g<1&#{T_tk1DY?yS$T$?mMru_^AX&#|fQtk1D&?yS$T>F%u0u^H~H&#{^Atk1Do?yS$T+3u{*u{rLn&#}4gtk1D|?yS$T`R=UGu?6m|&#{H>tk1DU?yS$TXWdz!W6!y>KF6MSXMK*n;LiFSd(oZsIrfq}>vQa7ch=|FVt3Z(*emX=&#_nCS)XICxwAgUUUz4Gj=kZ|`W##0&iWjC)1CD>_Le*AbL?$**5}we?yS$TcimZ^WAC}MKF8j7XMK)+;LiFS`_P^BIkwcD^*Q#DJL_}oV|Ui)*eC9+&#_P4S)XH{xwAgUK6ht*j(y?I`W*Yxo%K2Pl{@Qm>}z+{=h!#ytk1D;-C3Vw-?_6s$G&%GeUAO$&iWkt(Vg`<_LDp7bL?k#*5}wS?yS$TU)@=sW52nxKF5A{XMK(>b7y@{_<TSo|JP+k^(5ZeeKhkf?qisDbsx*ToBKHCYq^hSzP9@W;$>}<ma4yL+|IoR**|6Nl6G?W_P%^ITfTkLUM}Ckm!CwIFYTDLRr5oqq*KySJb&KN=g;Pc&Pivre66>a<9Cqr>ymVl<JW9oJ2`$wwSVd`etVyx9-r=?u1Qxlev6tTpsueretu3Q=O<dF$FB_^A$mUVpX>LZ>-V4Q_pe{S;q{f#eSuXick=vjepQl_RPptf7rFlTPaHP-KOM#&{UUk3JFjUnw^Tfzm{*y)c>XlgGHI&rUllF%^O@QHU?VcWk`_se;NLH6wL&|{|2Er~T%Jpp|I-ZrFZ(au{#I%Wv(MLGNR}_IS-&{G+4=V;%jY-K%V(M^t$lv9SzY>^fw_O}_(#V#(^T)jM$LSFNw9yf=KH5AX(9Jdiw535mG#;`m4DCv89>G_DoT%EWqkgz^FQ4`&Fiv%MmE&>(^~JJ`tJX9|Hw6Dw{I9fzgx@sMaQ?f@89V74zB0^-H$BqpAVj3QcvNX6HHd#CBYQsT@y_0S-;~K&3{@j|LMW}X9V+~Nj%#Zv2DmYdkyh#`XM|l'
CONTROL_SHA256 = '7ced52e4d8394cde8d7eb8ce95dff3d9d27622312e57a7e6489fe685c0d8c2e2'

import random

PD_WORDS = (0x12ABA10BCB8967D2, 0x649C982060850444, 0x6C545EF4B4771820, 0x094046D494721825)
S = 18_360
SCRATCH = S
LID = S + 256
LST = LID + 256
DATA = LST + 256
R_COUNTER, R_NEXT_ID, R_RHO, R_ONES, R_PREFILTER, R_HITS = range(3529, 3535)
R_LINK, R_LINK2, R_ZERO = 3535, 3536, 3537
R_LANE, R_C1, R_ACC, R_RECORD, R_SLOT, R_WORD = 256, 258, 259, 261, 262, 263
R_POINT, R_X, R_TMP, R_REPEATED, R_U, R_F = 267, 265, 260, 272, 286, 287
W0 = 300
LABEL = {"probe":472,"insert":496,"restart":526,"setwalk":539,"gather":556,"eval_f":826,"match":883,"replay_fail":948}


def rol64(x, n):
    return ((x << n) | (x >> (64 - n))) & MASK64 if n else x


def keccak24(a):
    for rc in RC:
        c = [a[x] ^ a[x+5] ^ a[x+10] ^ a[x+15] ^ a[x+20] for x in range(5)]
        d = [c[(x-1)%5] ^ rol64(c[(x+1)%5], 1) for x in range(5)]
        b = [0] * 25
        for y in range(5):
            for x in range(5):
                i = x + 5*y
                b[y + 5*((2*x + 3*y)%5)] = rol64(a[i] ^ d[x], RHO[i])
        for y in range(5):
            for x in range(5):
                i = x + 5*y
                a[i] = (b[i] ^ ((~b[(x+1)%5 + 5*y]) & b[(x+2)%5 + 5*y])) & MASK64
        a[0] ^= rc


def message_for(u):
    q = [(u >> (64*i)) & MASK64 for i in range(4)]
    lanes = list(KL[:16])
    lanes[1], lanes[6], lanes[11] = q[0], q[1], q[0] ^ q[1] ^ KL[11]
    lanes[4], lanes[9], lanes[14] = q[2], q[3], q[2] ^ q[3] ^ KL[14]
    return b"".join(x.to_bytes(8,"little") for x in lanes)


def chain(u):
    lanes = list(KL)
    m = message_for(u)
    for i in range(16): lanes[i] = int.from_bytes(m[8*i:8*i+8],"little")
    keccak24(lanes)
    return sum((lanes[i] ^ PD_WORDS[i]) << (64*i) for i in range(4))


def unpack39(data, count):
    out=[]; acc=bits=at=0
    for _ in range(count):
        while bits < 39:
            acc |= data[at] << bits; bits += 8; at += 1
        w=acc & ((1<<39)-1); acc >>= 39; bits -= 39
        out.append((w&7,(w>>3)&4095,(w>>15)&4095,(w>>27)&4095))
    return out


def execute_packed_step(prog_data, body_data, points):
    prog=unpack39(prog_data,6811); body=unpack39(body_data,53064)
    regs=[0]*4096; ones=(1<<len(points))-1
    for bit in range(256): regs[bit]=sum(((p>>bit)&1)<<lane for lane,p in enumerate(points))
    trace=pc=0
    def logic(word):
        nonlocal trace
        op,d,a,b=word
        if op==0: regs[d]=regs[a]^regs[b]
        elif op==1: regs[d]=regs[a]&regs[b]
        elif op==2: regs[d]=regs[a]|regs[b]
        elif op==3: regs[d]=regs[a]^ones
        else: raise AssertionError("nonlogical word")
        trace += 1
    while pc < len(prog):
        op,d,a,b=prog[pc]
        if op <= 3: logic(prog[pc]); pc += 1; continue
        if op != 4 or d != 3528: raise AssertionError("bad prog control word")
        regs[d]=pc+1; trace += 1; target=a | (b<<12)
        while True:
            word=body[target]; target += 1
            if word[0]==5:
                if word[2] != 3528 or regs[word[2]] != pc+1: raise AssertionError("bad return")
                trace += 1; break
            logic(word)
        pc += 1
    result=[sum(((regs[bit]>>lane)&1)<<bit for bit in range(256)) for lane in range(len(points))]
    if trace != 145974: raise AssertionError("step trace count")
    return result,trace


def decode_control():
    raw=zlib.decompress(base64.b85decode(CONTROL_DATA))
    if len(raw)!=949*32 or hashlib.sha256(raw).hexdigest()!=CONTROL_SHA256: raise AssertionError("controller bytes")
    out=[]
    for i in range(949):
        x=raw[32*i:32*i+32]
        if x[7]: raise AssertionError("reserved controller byte")
        out.append((x[0],int.from_bytes(x[1:3],"little"),int.from_bytes(x[3:5],"little"),int.from_bytes(x[5:7],"little"),int.from_bytes(x[8:],"little")))
    return out


class Controller:
    def __init__(self, code):
        self.code=code; self.r=[0]*3540; self.m=[0]*(DATA+16); self.pc=0; self.halt=None; self.ops=0; self.eval_hook=None
        lanes=list(KL)
        for w in range(7): self.m[DATA+w]=sum(lanes[4*w+k]<<(64*k) for k in range(min(4,25-4*w)))
        self.m[DATA+7]=sum(PD_WORDS[k]<<(64*k) for k in range(4))
    def step(self):
        if self.pc==LABEL["eval_f"] and self.eval_hook is not None:
            self.r[R_F]=self.eval_hook(self.r[R_U]) & MASK256; self.pc=self.r[R_LINK2]; self.ops += 6533; return
        op,d,a,b,imm=self.code[self.pc]; self.pc += 1; r=self.r
        if op==0:r[d]=r[a]^r[b]
        elif op==1:r[d]=r[a]&r[b]
        elif op==2:r[d]=r[a]|r[b]
        elif op==3:r[d]=r[a]^MASK256
        elif op==4:r[d]=(r[a]+r[b])&MASK256
        elif op==5:r[d]=(r[a]-r[b])&MASK256
        elif op==6:r[d]=(r[a]<<(r[b]&255))&MASK256
        elif op==7:r[d]=r[a]>>(r[b]&255)
        elif op==8:r[d]=int(r[a]==r[b])
        elif op==9:r[d]=int(r[a]<r[b])
        elif op==10:r[d]=r[a]
        elif op==11:r[d]=(r[a]+imm)&MASK256
        elif op==12:r[d]=(r[a]-imm)&MASK256
        elif op==13:r[d]=(r[a]<<(imm&255))&MASK256
        elif op==14:r[d]=r[a]>>(imm&255)
        elif op==15:r[d]=r[a]&imm
        elif op==16:r[d]=int(r[a]==imm)
        elif op==17:r[d]=int(r[a]<imm)
        elif op==18:r[d]=imm
        elif op==19:r[d]=self.m[r[a]+imm]
        elif op==20:self.m[r[a]+imm]=r[b]
        elif op==21:r[d]=imm
        elif op==22:
            if r[a]:self.pc=imm
        elif op==23:
            if not r[a]:self.pc=imm
        elif op==24:self.pc=imm
        elif op==25:r[d]=self.pc;self.pc=imm
        elif op==26:self.pc=r[a]
        elif op==27:r[d]=0
        elif op==28:
            state=[(r[W0+i//4]>>(64*(i%4)))&MASK64 for i in range(25)];keccak24(state)
            for w in range(7):r[W0+w]=sum(state[4*w+k]<<(64*k) for k in range(min(4,25-4*w)))
            self.ops += 6503
        elif op==29:self.halt=imm
        else:raise AssertionError("bad controller opcode")
        self.ops += 1
    def run(self,start,stops=(),limit=1000000):
        self.pc=start; n=0
        while self.halt is None and self.pc not in stops:
            if n>=limit:raise AssertionError("controller step limit")
            self.step();n+=1
        return self.pc


def tnum(i):
    if not 0<=i<91800: raise ValueError("trail boundary")
    return (i%S) | ((51*(i//S))<<15)


def exercise_controller(code):
    c=Controller(code)
    point=0x123456789ABCDEF
    c.r[R_U]=point;c.r[R_LINK2]=949;c.run(LABEL["eval_f"],(949,))
    if c.r[R_F]!=chain(point):raise AssertionError("controller evalF")
    record=1|(0x12345<<1); repeated=sum(record<<(51*k) for k in range(5))
    c=Controller(code);c.r[R_SLOT]=0;c.r[R_REPEATED]=repeated;c.m[0]=record<<(51*3)
    c.run(LABEL["probe"],(LABEL["match"],))
    if c.r[R_X] != (51*3)<<15:raise AssertionError("probe slot")
    c=Controller(code);c.r[R_SLOT]=0;c.r[R_REPEATED]=repeated;c.run(LABEL["probe"],(LABEL["insert"],),500000)
    if c.r[R_SLOT]!=S:raise AssertionError("probe boundary")
    c=Controller(code);c.r[R_NEXT_ID]=S-1;c.r[R_LANE]=5;c.r[R_TMP]=7;c.r[R_RHO]=9;c.r[R_LINK2]=949;c.run(LABEL["restart"],(949,))
    if c.m[LID+5]!=S-1 or c.m[LST+5]!=7 or c.r[R_NEXT_ID]!=(51<<15):raise AssertionError("restart")
    c.r[R_LINK]=949;c.r[R_LANE]=5;c.run(LABEL["gather"],(949,))
    if c.r[R_ACC] != 9+S-1:raise AssertionError("restart point")
    if tnum(91799) != 18359 | ((51*4)<<15):raise AssertionError("last trail")
    try:tnum(91800)
    except ValueError:pass
    else:raise AssertionError("first rejected trail")
    c=Controller(code);c.r[R_LANE]=0;c.r[R_C1]=1;c.r[R_RHO]=0;c.r[R_X]=2;c.m[LID]=3;c.m[LST]=0;c.eval_hook=lambda u:5;c.run(LABEL["match"],limit=10000)
    if c.halt!=1:raise AssertionError("recovery success")
    left=b"".join(c.m[DATA+8+i].to_bytes(32,"little") for i in range(4));right=b"".join(c.m[DATA+12+i].to_bytes(32,"little") for i in range(4))
    if left!=message_for(2) or right!=message_for(3):raise AssertionError("recovered messages")
    c=Controller(code);c.r[R_LANE]=0;c.r[R_C1]=1;c.r[R_X]=2;c.m[LID]=3;c.m[LST]=0;c.eval_hook=lambda u:u;c.run(LABEL["match"],limit=10000)
    if c.halt!=13:raise AssertionError("false match failure")


def projection(seed_hex):
    raw=hashlib.shake_256(b"hashsmash-r24-reviewed-projection-v2"+bytes.fromhex(seed_hex)).digest(17*32)
    points=[int.from_bytes(raw[32*i:32*i+32],"little") for i in range(17)];seen={};evaluations=0
    for _ in range(4):
        nxt=[]
        for p in points:
            image=chain(p);evaluations+=1;key=image&4095;old=seen.get(key)
            if old is not None and old!=p:return message_for(old).hex(),message_for(p).hex(),evaluations
            seen.setdefault(key,p);nxt.append(image)
        points=nxt
    return None,None,evaluations


def organizer_main():
    req=json.load(sys.stdin);event={"kind":"digest-xor-mask","mask_hex":"ff0f"+"00"*30,"expected_hex":"00"*32}
    if req.get("schema_version")!=1 or req.get("experiment_id")!="step-controller-recovery" or req.get("target_profile")!="sha3-256-r24-prefix-v1" or req.get("event")!=event:raise ValueError("request")
    prog,body,result=generate();rng=random.Random(0xB04CDAA4);points=[rng.getrandbits(256) for _ in range(8)]
    emitted,trace=execute_packed_step(prog,body,points)
    if emitted != [chain(p) for p in points]:raise AssertionError("packed step differs from scalar")
    code=decode_control();exercise_controller(code)
    rows=[]
    for trial in req["trials"]:
        a,b,e=projection(trial["seed"]);rows.append({"trial":trial["trial"],"message_a_hex":a,"message_b_hex":b,"observations":{"evaluations":e,"step_trace":trace,"controller_paths":7}})
    json.dump({"schema_version":1,"trials":rows},sys.stdout,sort_keys=True,separators=(",",":"))
if __name__=="__main__":organizer_main()
