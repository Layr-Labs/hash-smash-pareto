"""SHA3-256 r24 collision search: the inherited looped step of c9a7e62c in our declared machine.

Run only in the organizer's isolated executor. The step is inherited and credited (the section marked below,
proof 3.4 and 10): its blocks are rebuilt from the decisions their entry publishes and refused unless each
hashes to the SHA-256 their proof prints. Ours: the machine, the control program, the ledger, the bound and
its checker, the experiments (proof 3, M, L, P). No trail is cut.
"""
import hashlib
import base64
import json
import zlib
from decimal import Decimal as Dm, getcontext, localcontext, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction as Fr
import sys
from collections import defaultdict

getcontext().prec = 60
M256 = (1 << 256) - 1
M64 = (1 << 64) - 1
# ---- INHERITED, AND CREDITED: the step of c9a7e62c (mitchuski), on Jbenisek's 71fefe66 and 0bd0022d and
# jungjipdo's 67f781f8. Their published program, lines 20-510, renamed only where a name clashes (proof 3.4).
RCA = [0x1, 0x8082, 0x800000000000808A, 0x8000000080008000, 0x808B, 0x80000001, 0x8000000080008081, 0x8000000000008009,
       0x8A, 0x88, 0x80008009, 0x8000000A, 0x8000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
       0x8000000000008002, 0x8000000000000080, 0x800A, 0x800000008000000A, 0x8000000080008081, 0x8000000000008080,
       0x80000001, 0x8000000080008008]
ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
NR = 24                         # rounds of the target

# Their decisions, as published; the SHA-256 of the restored text is asserted and every block it
# builds is then checked against the SHA-256 their proof prints.
PLANZ = (
    "c-rk)OLCk*4BgKu`UsL*U~vIE+2sltdy%RnPPu&liarek3@|Wus=P4c@<4yo(tA(pW=?OfKigj^*8rzKuZcLl{C)fV^7NeY=^hhiU<3iE84wT=04iunTYw}purM@4Al74z`T;;<dqD6f`-TQ|Y<GIVq>aPi+0}QfbT410`-eoSmh#9PD>h;-hC72PKCfUm-DnL$4e=2`v<U@L>B(xwg8|{jFesB16&*#Q%b^d^@lsPU#I3I@HeCM{sK(sPDL^3)u16tr%Y$WW)+c*tbz;_=5}BISi7`sDImHA?4H*X|P7T`_vlu#%5*_OeVQ$=p#$)!_cr7TiPeiEg+uY;?eb9~oj+ux^^{*54NLm}{ro@S_Tp`iK(WpaGObc(Ut2XadHW4>MYsS!>0ausL%sFOxd=l$Mi@8}PM_wE)>Ihr|;%nQ|RP6NtDkRYzZKI$h"
    "+9|R5$;`+Gz8V!#yc|FM?tmjSF&?rx*c)=d-Nm9}9<*5}F>~bMGCG*ls-aG^M2g13QG-QqTT@VR7>jO;Ni;#Eh)Vr1<_DrW6=<&ybDG^)XZeecDQXsyPb?ZR?O3Xsn|G;T5kasRwiv92L==QxqdF;A0x9WcvB6_;5?r1s{Ie)XDrmSfjx~uCTc@m0&|!&zJSxUQBDP}LY=}8f+1!*AP!unN=t%mA9f!(69;iYWZV1<vMZ{9(xdSLk;>qRjNsT=*Vb74jXE7mDhZ=yv3yl#e($@oZGn*nRb~l@(_K50H-W2(Qd%z{k%CIy+)dK>xqoW@waHAKKWNk!3Lwv4UItyG(om2$j+0+?JhOU+f8}sDK?9>RgPC7y=g2t8VI?57U?GG{pgY^NDsHE;q4tH_L4;fo`Nb*o%Myo2=ryt+GCrI#heX7f8!O>39_KZ$<"
    "3n<b!m)h;CR0TTMwSK4aO{45dq1W+B(wE8gCHPo`v}9^>D7ok+p6-)?tJZPJt9sa&W)o%R{nFV;23ly8Ey7pU-+$7&QXu%sDjPt~NTO}6(9u&O?utZKrpfv;JfAEpMxB<Nt}eN*tYZQ4bSmRvUYBQZe{QAgP|7CsxVKUMcM;=sbvapT!F?jb88JMnmiq!^z<1;)&Wq$+PqHJ2-cupuHd?B5SyANd4Gy~l&fiXsxOAR8ea)GL%==NG-34cp@*U{m0!O@5i1`*yX_=Nf9nr+JcH+WD|3OH~O=9IyhSBm)dqv22i}vYqlw7q-o7r-g_8oR^uBO!g<GFd>zXYxUCN~w89f!%`XNN-@CmlXQT%Z!PNZL3X;ntZ{;@5yfC$QnSm`m??JXSuYxXV!{Wr~*Epn*wx;?WAmg_h>)b@EfbPJX@Se>z_N0Te2ne*"
)
PLAN = zlib.decompress(base64.b85decode(PLANZ)).decode()
assert hashlib.sha256(PLAN.encode()).hexdigest() == (
    "237c1d80c9ad9775bae8b385307a8865db6974f5189ba7097bfb4cf2f101d22d")

PL = {}
for _ln in PLAN.strip().split("\n"):
    _t = _ln.split()
    if _t[0] in ("trial", "F1", "G1"): PL[_t[0]] = _t[1]
    elif _t[0] == "FG": PL[("FG", int(_t[1]))] = (_t[2], _t[3])
    elif _t[0] == "PHI": PL[("PHI", int(_t[1]))] = _t[2]
TRIAL = int(PL["trial"])            # constants of the generator's selected trial
KB = 8                            # bodies in the cycle of the generic rounds
REGTOP = 3525
KONES = REGTOP + 4                 # the all-ones register of the search state
# name, SHA-256 of the generator's file and length, as their proof prints
BLOCK_SHA256 = {r.split(",")[0] + ".bin": (r.split(",")[1], int(r.split(",")[2])) for r in (
    "P,a19d15483682b2c6b1168ab46770c36b6df595f6601e9117eab581534d2548d3,4942 B1,c3a9216e6fe96074ae974509a5cad78dda78420eef509788c704ca552a2b05f7,6618 B2,2cc3982d2b16bef22e0834bad1478aa72e12e4411cc0a9050f7d5b20929c50cf,6634 B3,6cc7a678188b88fd02ccd6e5e41616cc53dda3541d77c17fc9b9cfa475fe7fb6,6625 "
    "B4,df6ff2c93b1be7f0abedca4a23ec859cada69227825ce1fd6510f828a3229a1f,6633 B5,56fbcbae544279c7e5dc5b4ca9096fa02eeea1b01e266bf39f2213bc51f9fb9e,6624 B6,df30c150655696cca41d4e506f775fa5e286e60450740b421afca2fc1eec3c39,6636 B7,5f505fbb72c26bddab6d46884320bc295e48260c2eeb52421ed0a03020f67d3a,6642 "
    "B8,fd11364f54bea307f466b66e57dfb6d635f7f5edf126157449108d35ce5c198b,6904 E,9e7b6cd44b30580a07d3c6ef472ba3f8902551fea1e6dbb3d0a2bb01c5c82eaa,2475").split()}


def consts(trial):
    K = [0] * 25
    K[16] = 0x8000000000000006
    if trial > 0:
        s = (0x9E3779B97F4A7C15 * trial + 1) & M64
        def xs():
            nonlocal s
            s ^= (s << 13) & M64; s ^= s >> 7; s ^= (s << 17) & M64
            return s
        for _ in range(10): xs()
        for l in (0, 2, 3, 5, 7, 8, 10, 12, 13, 15, 11, 14): K[l] = xs()
    return K


KL = consts(TRIAL)



# ---------------- generator: gen4.c in Python (same node order, decisions from PLAN, same register allocation) ----------------
W_, PIN = 8192, 8192
XB, YB, POOL, NREGG = 256, 1856, 3456, 4096
O_IN, O_XOR, O_AND, O_OR, O_NOT = 0, 1, 2, 3, 4
NC = 0xFFFF
NG = NR - 3
BRE = KB + 2


def bits(h, n):
    v = int.from_bytes(bytes.fromhex(h), "little")
    return [(v >> i) & 1 for i in range(n)]


def cost_term(b1, b2):
    if b1[0] == NC or b2[0] == NC or b1[0] == b2[0]: return 0
    return 1 if (b1[1] ^ 1) == b2[1] else 2


def row_choose(b, need):
    distinct = all(v[0] != NC for v in b) and len(set(v[0] for v in b)) == 5
    best, bc, bj = -1, 1 << 30, -1
    for j in range(-1, 5 if distinct else 0):
        if j >= 0 and not ((need >> j) & 1 and (need >> ((j + 1) % 5)) & 1): continue
        for s in range(32):
            c = 0; bb = list(b)
            for X in range(5):
                if s >> X & 1:
                    if b[X][0] == NC: c = 1 << 29
                    else: bb[X] = (b[X][0], b[X][1] ^ 1); c += 1
            for X in range(5):
                if need >> X & 1:
                    if X == j:
                        k = (j + 1) % 5; p1, p2 = bb[(k + 1) % 5], bb[(k + 2) % 5]
                        if (p1[1] ^ 1) == p2[1]: c += cost_term((bb[k][0], bb[k][1] ^ (p1[1] ^ 1)), bb[(X + 2) % 5])
                        else: c += 1
                    else: c += cost_term(bb[(X + 1) % 5], bb[(X + 2) % 5])
            if c < bc: bc, best, bj = c, s, j
    return best, bj


TAB = {(L, p): row_choose([(X, (p >> X) & 1) for X in range(5)], 0x0F if L else 0x1F) for L in (0, 1) for p in range(32)}


def rowsim(pin, s, j, fb):
    p = [((pin >> X) & 1) ^ ((s >> X) & 1) for X in range(5)]
    c = bin(s).count("1"); tp = [0] * 5; op = [0] * 5; k = (j + 1) % 5
    def term(a1, b2, free, X):
        a_ = a1 ^ 1
        if a_ == 0 and b2 == 0: tp[X] = 0; return 1
        if a_ == 1 and b2 == 1: tp[X] = 1; return 1
        tp[X] = free; return 2
    if j >= 0:
        mixed = (p[(k + 1) % 5] ^ 1) != p[(k + 2) % 5]
        c += term(p[(k + 1) % 5], p[(k + 2) % 5], ((p[(j + 2) % 5] ^ 1) ^ p[k]) if mixed else ((fb >> k) & 1), k); op[k] = p[k] ^ tp[k]
    for X in range(5):
        if j >= 0 and X == k: continue
        if X == j: c += term(op[k], p[(X + 2) % 5], (fb >> X) & 1, X)
        else: c += term(p[(X + 1) % 5], p[(X + 2) % 5], (fb >> X) & 1, X)
        op[X] = p[X] ^ tp[X]
    return c, sum(op[X] << X for X in range(5))


T2 = {}
def t2(p, t):
    """the closing body's row decision: least cost + output polarity misses, first in the order of gen4.c mk_t2"""
    v = T2.get((p, t))
    if v is None:
        bc = 1 << 30
        for j in range(-1, 5):
            for s in range(32):
                for fb in range(32):
                    c, o = rowsim(p, s, j, fb); c += bin(o ^ t).count("1")
                    if c < bc: bc, v = c, (s, j, fb)
        T2[(p, t)] = v
    return v


class G4:
    """one streaming build of gen4.c (the emitting build): blocks P, B1..BKB, E"""
    def __init__(self):
        self.form, self.fidx = [], {}
        self.pord = [0] * 1600; self.pfl = [0] * 1600
        self.blocks = {}

    def reset_ring(self):
        self.op, self.a, self.b, self.k, self.lin = [], [], [], [], []
        self.cons = {}

    def new(self, op, a, b):
        self.op.append(op); self.a.append(a); self.b.append(b); self.k.append(0); self.lin.append(-1)
        return len(self.op) - 1

    def okey(self, n): return self.pord[n - PIN] if n >= PIN else n + W_

    def consn(self, op, a, b):
        if op != O_NOT and self.okey(a) > self.okey(b): a, b = b, a
        key = (op, a, b)
        n = self.cons.get(key)
        if n is None: n = self.new(op, a, b); self.cons[key] = n
        return n

    def islin(self, n): return n < PIN and self.lin[n] >= 0
    def kof(self, n): return self.k[n] if n < PIN else 0

    def xorv(self, a, b):
        if a[0] == NC: return (b[0], b[1] ^ a[1])
        if b[0] == NC: return (a[0], a[1] ^ b[1])
        if a[0] == b[0]: return (NC, a[1] ^ b[1])
        if self.islin(a[0]) and self.islin(b[0]):
            m = self.form[self.lin[a[0]]][0] ^ self.form[self.lin[b[0]]][0]
            kk = self.k[a[0]] ^ self.k[b[0]]
            if m == 0: return (NC, kk ^ a[1] ^ b[1])
            f = self.fidx.get(m)
            if f is not None:
                n3 = self.form[f][1]
                return (n3, kk ^ a[1] ^ b[1] ^ self.k[n3])
            n = self.new(O_XOR, min(a[0], b[0]), max(a[0], b[0]))
            self.k[n] = kk; self.lin[n] = len(self.form); self.form.append((m, n)); self.fidx[m] = self.lin[n]
            return (n, a[1] ^ b[1])
        return (self.consn(O_XOR, a[0], b[0]), a[1] ^ b[1])

    def notv(self, a):
        if a[0] == NC: return a
        before = len(self.op)
        n = self.consn(O_NOT, a[0], 0)
        if len(self.op) > before and self.islin(a[0]): self.lin[n] = self.lin[a[0]]; self.k[n] = self.k[a[0]] ^ 1
        return (n, a[1] ^ 1)

    def and2(self, a, b, sel):
        if a[0] == NC: return b if a[1] else (NC, 0)
        if b[0] == NC: return a if b[1] else (NC, 0)
        if a[0] == b[0]: return a if a[1] == b[1] else (NC, 0)
        if a[1] == 0 and b[1] == 0: return (self.consn(O_AND, a[0], b[0]), 0)
        if a[1] == 1 and b[1] == 1: return (self.consn(O_OR, a[0], b[0]), 1)
        A, B = (a[0], b[0]) if a[1] == 0 else (b[0], a[0])
        if sel:
            na = self.notv((A, 0))
            return (self.consn(O_OR, na[0], B), 1)
        t = self.consn(O_AND, A, B)
        return self.xorv((A, 0), (t, 0))

    def finish(self, S, last, prefix, inbank, outbank, preg):
        nn = len(self.op); lo = 256 if prefix else 0
        live = [False] * nn; st = [False] * nn; reg = [0] * nn; outn = {}
        if not last:
            for q in range(1600):
                n = S[q >> 6][q & 63][0]; assert n != NC and n < PIN and not st[n]
                st[n] = True; live[n] = True; reg[n] = outbank + q
        else:
            for j in range(256):
                n = S[j >> 6][j & 63][0]; assert n != NC and lo <= n < PIN and n not in outn
                outn[n] = j; live[n] = True; reg[n] = j
        for i in range(nn - 1, lo - 1, -1):
            if live[i]:
                if self.a[i] < PIN: live[self.a[i]] = True
                if self.op[i] != O_NOT and self.b[i] < PIN: live[self.b[i]] = True
        tempok = [False] * NREGG
        for r in range(POOL, NREGG): tempok[r] = True
        if inbank < 0: rng = list(range(256)) + list(range(YB, YB + 1600))
        elif outbank >= 0: rng = list(range(256)) + list(range(inbank, inbank + 1600))
        else: ob = YB if inbank == XB else XB; rng = list(range(inbank, inbank + 1600)) + list(range(ob, ob + 1600))
        for r in rng: tempok[r] = True
        free = [r for r in range(NREGG - 1, -1, -1) if tempok[r] and not (inbank < 0 and r < 256) and not (inbank >= 0 and inbank <= r < inbank + 1600)]
        busy = [False] * NREGG
        nlast = [None] * nn; plast = [None] * 1600
        for i in range(lo, nn):
            if live[i]:
                a, b = self.a[i], self.b[i]
                if a >= PIN: plast[a - PIN] = i
                else: nlast[a] = i
                if self.op[i] != O_NOT:
                    if b >= PIN: plast[b - PIN] = i
                    else: nlast[b] = i
        preg = list(preg)
        if prefix:
            for j in range(256):
                reg[j] = j
                if nlast[j] is not None: busy[j] = True
                else: free.append(j)
        else:
            for q in range(1600):
                if preg[q] is not None: assert plast[q] is not None; busy[preg[q]] = True
        prog = []
        code = {O_XOR: 0, O_AND: 1, O_OR: 2, O_NOT: 3}
        def freereg(r):
            busy[r] = False
            if tempok[r]: free.append(r)
        for i in range(lo, nn):
            if not live[i]: continue
            op, a = self.op[i], self.a[i]
            b = a if op == O_NOT else self.b[i]
            ra = preg[a - PIN] if a >= PIN else reg[a]
            rb = 0 if op == O_NOT else (preg[b - PIN] if b >= PIN else reg[b])
            for kk, o in enumerate((a, b)):
                if kk == 1 and o == a: break
                if o >= PIN:
                    if plast[o - PIN] == i: freereg(preg[o - PIN]); preg[o - PIN] = None
                elif not (st[o] or o in outn) and nlast[o] == i: freereg(reg[o])
            if st[i] or i in outn: d = reg[i]; assert not busy[d]
            else: d = free.pop()
            busy[d] = True; reg[i] = d
            prog.append((code[op], d, ra, rb))
        if not last:
            for q in range(1600):
                n = S[q >> 6][q & 63][0]
                self.pord[q] = n; self.pfl[q] = self.op[n]
                S[q >> 6][q & 63] = (PIN + q, S[q >> 6][q & 63][1])
        return prog

    def build(self):
        self.reset_ring()
        for j in range(256):
            n = self.new(O_IN, 0, 0); self.lin[n] = len(self.form); self.form.append((1 << j, n)); self.fidx[1 << j] = self.lin[n]
        S = [[(NC, (KL[l] >> z) & 1) for z in range(64)] for l in range(25)]
        for z in range(64):
            S[1][z] = (z, (KL[1] >> z) & 1); S[6][z] = (64 + z, (KL[6] >> z) & 1)
            S[4][z] = (128 + z, (KL[4] >> z) & 1); S[9][z] = (192 + z, (KL[9] >> z) & 1)
        for z in range(64):
            S[11][z] = self.xorv(self.xorv((z, 0), (64 + z, 0)), (NC, (KL[11] >> z) & 1))
            S[14][z] = self.xorv(self.xorv((128 + z, 0), (192 + z, 0)), (NC, (KL[14] >> z) & 1))
        preg = [None] * 1600; snap = {}; tgtX = None
        for r in range(BRE + 1):
            last = r == BRE; isB = 2 <= r < BRE; bj_ = r - 1
            close = isB and bj_ == KB and NG > KB
            rcv = RCA[0] if r == 0 else RCA[1] if r == 1 else RCA[NR - 1] if last else 0
            if last:
                jl = (NG - 1) % KB + 1; ob = YB if jl & 1 else XB
                pol, pord, pfl = snap[jl]
                S = [[(PIN + l * 64 + z, pol[l * 64 + z]) for z in range(64)] for l in range(25)]
                self.pord = list(pord); self.pfl = list(pfl); preg = [ob + q for q in range(1600)]
            if r == 1: ff, gg = bits(PL["F1"], 320), bits(PL["G1"], 320)
            elif r >= 2: ff, gg = bits(PL[("FG", r)][0], 320), bits(PL[("FG", r)][1], 320)
            else: ff = gg = [0] * 320
            phi = bits(PL[("PHI", r)], 1600)
            if r >= 2: self.reset_ring()
            C = [[None] * 64 for _ in range(5)]; D_ = [[None] * 64 for _ in range(5)]
            for x in range(5):
                s = S[x][63]
                for y in range(1, 5): s = self.xorv(s, S[x + 5 * y][63])
                C[x][63] = self.notv(s) if gg[x * 64 + 63] else s
            for z in range(64):
                if z < 63:
                    for x in range(5):
                        s = S[x][z]
                        for y in range(1, 5): s = self.xorv(s, S[x + 5 * y][z])
                        C[x][z] = self.notv(s) if gg[x * 64 + z] else s
                for x in range(5):
                    D_[x][z] = self.xorv(C[(x + 4) % 5][z], C[(x + 1) % 5][(z + 63) & 63])
                    if ff[x * 64 + z]: D_[x][z] = self.notv(D_[x][z])
            NS = [row[:] for row in S]
            nY, need = (1, 0x0F) if last else (5, 0x1F)
            for Y in range(nY):
                for z in range(64):
                    b = []
                    for X in range(5):
                        y, x = X, (3 * Y + X) % 5
                        zz = (z - ROT[x][y]) & 63
                        b.append(self.xorv(S[x + 5 * y][zz], D_[x][zz]))
                    fbm = 0; tg = 0
                    if close: tg = sum(tgtX[(X + 5 * Y) * 64 + z] << X for X in range(5))
                    if all(v[0] != NC for v in b) and len(set(v[0] for v in b)) == 5:
                        p = sum(v[1] << X for X, v in enumerate(b))
                        if close: best, bj, fbm = t2(p, tg)
                        else: best, bj = TAB[(int(last), p)]
                    else:
                        best, bj = row_choose(b, need)
                    for X in range(5):
                        if best >> X & 1: b[X] = self.notv(b[X])
                    k = (bj + 1) % 5
                    if bj >= 0:
                        p1, p2 = b[(k + 1) % 5], b[(k + 2) % 5]
                        if (p1[1] ^ 1) != p2[1]: sel = (b[(bj + 2) % 5][1] ^ 1) ^ b[k][1]
                        else: sel = ((fbm >> k) & 1) if close else phi[(k + 5 * Y) * 64 + z]
                        NS[k + 5 * Y][z] = self.xorv(b[k], self.and2((p1[0], p1[1] ^ 1), p2, sel))
                    for X in range(5):
                        if need >> X & 1:
                            if bj >= 0 and X == k: continue
                            t1 = NS[k + 5 * Y][z] if X == bj else b[(X + 1) % 5]
                            sel = ((fbm >> X) & 1) if close else phi[(X + 5 * Y) * 64 + z]
                            NS[X + 5 * Y][z] = self.xorv(b[X], self.and2((t1[0], t1[1] ^ 1), b[(X + 2) % 5], sel))
                    if close:
                        for X in range(5):
                            if NS[X + 5 * Y][z][1] != (tg >> X) & 1: NS[X + 5 * Y][z] = self.notv(NS[X + 5 * Y][z])
            if not isB:
                for z in range(64): NS[0][z] = (NS[0][z][0], NS[0][z][1] ^ ((rcv >> z) & 1))
            S = NS
            if r == 0: continue
            outbank = XB if r == 1 else ((YB if bj_ & 1 else XB) if isB else -1)
            inbank = -1 if r == 1 else ((XB if bj_ & 1 else YB) if isB else ((YB if ((NG - 1) % KB + 1) & 1 else XB)))
            name = "P.bin" if r == 1 else "E.bin" if last else "B%d.bin" % bj_
            self.blocks[name] = self.finish(S, last, r == 1, inbank, outbank, preg)
            if not last: preg = [outbank + q for q in range(1600)]
            if r == 1: tgtX = [S[q >> 6][q & 63][1] for q in range(1600)]
            if isB: snap[bj_] = ([S[q >> 6][q & 63][1] for q in range(1600)], list(self.pord), list(self.pfl))
            if close: assert all(S[q >> 6][q & 63][1] == tgtX[q] for q in range(1600))
        PD = 0
        for j in range(256): PD |= S[j >> 6][j & 63][1] << j
        return self.blocks, PD


def kencode(prog):
    out = bytearray()
    for c, d, a, b in prog:
        out += (c | d << 3 | a << 15 | b << 27).to_bytes(5, "little")
    return bytes(out)


def digest(msg, rounds=NR):
    """r24 is the complete round count, so the target is the full SHA3-256 and the library is the reference."""
    assert rounds == 24
    return hashlib.sha3_256(msg).digest()


def msg_of(u):
    l = [KL[i] for i in range(16)]
    u0, u1, u2, u3 = [(u >> (64 * i)) & M64 for i in range(4)]
    l[1], l[6], l[11], l[4], l[9], l[14] = u0, u1, u0 ^ u1 ^ KL[11], u2, u3, u2 ^ u3 ^ KL[14]
    return b"".join(v.to_bytes(8, "little") for v in l)


def F_ref(u, PD):
    return int.from_bytes(digest(msg_of(u)), "little") ^ PD


# ---------------- build_blocks and checks ----------------
def build_blocks():
    """Their builder, then their gate: no block is accepted unless it has their published length and hashes
    to the SHA-256 their proof prints for the generator's file."""
    blocks, PD = G4().build()
    for name, (h, n) in BLOCK_SHA256.items():
        assert len(blocks[name]) == n and hashlib.sha256(kencode(blocks[name])).hexdigest() == h, name
    return blocks, PD


# ---- END OF THE INHERITED SECTION

# ---- scalar reference
def bounded_search(step, *, width, dp_bits, key_bits, lanes, batches, lrc,
                   capacity, start_limit, rho, stage1_bits=32, stage2_limit):
    """Scalar reference state machine."""
    # Distinguished: low dp_bits zero; key from dp_bits+4.
    assert 0 < dp_bits and dp_bits + 4 + key_bits <= width and 0 < key_bits
    assert lanes <= start_limit <= 1 << width
    mask = (1 << width) - 1
    dp_mask = (1 << dp_bits) - 1
    s1_mask = (1 << min(stage1_bits, dp_bits)) - 1
    key_mask = (1 << key_bits) - 1

    def distinguished(u):
        return u & dp_mask == 0
    states = [(rho + i) & mask for i in range(lanes)]
    ids = list(range(lanes))
    births = [0] * lanes
    next_id = lanes
    table = {}
    stats = dict(search_evaluations=0, recovery_evaluations=0,
                 final_evaluations=0, insertions=0, restarts=0,
                 max_age=0, reason=0, stage2=0)

    def finish(reason, pair=None):
        stats['reason'] = reason
        stats['allocated_starts'] = next_id
        stats['stored_endpoints'] = len(table)
        return pair, stats

    def restart(lane, batch):
        nonlocal next_id
        if next_id >= start_limit:
            return False
        ids[lane] = next_id
        states[lane] = (rho + next_id) & mask
        births[lane] = batch
        next_id += 1
        stats['restarts'] += 1
        return True

    def recover(old_id, current_id, current_length, endpoint):
        if current_length >= lrc:
            return 8, None                   # the replay refuses a live trail at or beyond the cap
        first = (rho + old_id) & mask
        old_endpoint = first
        length = 0
        for length in range(1, lrc + 1):
            old_endpoint = step(old_endpoint)
            stats['recovery_evaluations'] += 1
            if distinguished(old_endpoint):
                break
        else:
            return 8, None
        if old_endpoint != endpoint:
            return 2, None
        second = (rho + current_id) & mask
        a, b = first, second
        for _ in range(max(0, length - current_length)):
            a = step(a)
            stats['recovery_evaluations'] += 1
        for _ in range(max(0, current_length - length)):
            b = step(b)
            stats['recovery_evaluations'] += 1
        if a == b:
            return 3, None
        for _ in range(min(length, current_length)):
            na, nb = step(a), step(b)
            stats['recovery_evaluations'] += 2
            if na == nb:
                stats['final_evaluations'] += 2
                if a != b and step(a) == step(b):
                    return 1, (a, b)
                return 8, None
            a, b = na, nb
        return 8, None

    for batch in range(1, batches + 1):
        outputs = [step(u) for u in states]
        stats['search_evaluations'] += lanes
        states[:] = outputs
        if any(u & s1_mask == 0 for u in outputs):
            stats['stage2'] += 1
            if stats['stage2'] > stage2_limit:
                return finish(9)
        flags = [distinguished(u) for u in outputs]
        for lane in range(lanes):
            stats['max_age'] = max(stats['max_age'], batch - births[lane])
            if not flags[lane]:
                continue
            key = (outputs[lane] >> (dp_bits + 4)) & key_mask
            if key in table:
                reason, pair = recover(table[key], ids[lane],
                                       batch - births[lane], outputs[lane])
                return finish(reason, pair)
            if len(table) >= capacity:
                return finish(4)
            table[key] = ids[lane]
            stats['insertions'] += 1
            if not restart(lane, batch):
                return finish(5)
    return finish(6)


# ---- machine program
# A register instruction costs its base operations; LD/ST charged; COMP adds 64.
COST = dict(BEQ=2, BNE=2, BLT=2, BGE=2, COMP=64, OUT=2)
# Our control registers follow those the blocks name (0..3524). ONES is fifth, landing on KONES, the
# all-ones register the blocks read; LR links the body calls.
CTRL = ("ZERO ONE C3 C256 ONES M17 KM DPM PD BMAX LRC ULIM IDL E2LIM WM RHO NID "
        "CNT B H2 D ND LANE KEY E S NOTLANE T0 T1 T2 T3 T4 T5 RR EIDX ID1 "
        "ID2 L1 L2 X Y A BV FA FB CN MINL LR").split()
NREG = REGTOP + len(CTRL)      # the declared register file, 32 bytes a register in the memory ledger
STEP_WORDS = 60733             # five-byte words stored once: their ten blocks
STEP_OPS = 147303              # operations the step executes per batch, their figure
PD = None                      # the inherited output polarity, set when the blocks are built


def build_program(p, kregs):
    """Emit the machine program for parameters p (see proof.md, Section M)."""
    w, d, k, U = p["w"], p["d"], p["k"], p["U"]
    diag = w < 256
    assert 1 < d and d + 4 + k <= w <= 256 and k <= 47 and p["IDL"] <= 1 << 17
    R = {n: kregs + i for i, n in enumerate(CTRL if diag else [c for c in CTRL if c != "WM"])}
    # Table entry: a 64-bit slot, key low, identifier from bit 47.
    keyw = -(-U // 4)
    KEYB, BIRB, LIDB = 0, keyw, keyw + 256
    code, labels, region = [], {}, ["setup"]

    def e(op, *args):
        code.append((op, args, region[0]))

    def lab(name):
        labels[name] = len(code)

    def r(name):
        return R[name] if isinstance(name, str) else name

    def x3(op, dst, a, b):
        e(op, r(dst), r(a), r(b))

    def proj(name):
        if diag:
            region[0], old = "diag", region[0]
            x3("AND", name, name, "WM")
            region[0] = old

    # Setup: constants, randomness, cleared memory, lanes.
    consts = dict(ZERO=0, ONE=1, ONES=M256, C3=3, C256=256, M17=0x1FFFF,
                  KM=(1 << k) - 1, DPM=(1 << d) - 1, PD=PD, BMAX=p["B"], LRC=p["LRC"],
                  ULIM=U, IDL=p["IDL"], E2LIM=p["E2MAX"] + 1)
    s1 = min(32, d)
    if diag:
        consts["WM"] = (1 << w) - 1
    for name, value in consts.items():
        e("LDI", R[name], value)
    e("RAND", R["RHO"])
    proj("RHO")
    x3("MOV", "T1", "ZERO", None)
    e("LDI", R["T2"], LIDB + 256)
    lab("ZL")
    e("ST", R["T1"], R["ZERO"])
    e("ADDI", R["T1"], R["T1"], 1)
    e("BNE", R["T1"], R["T2"], "ZL")
    for n in ("NID", "CNT", "B", "LANE", "H2"):
        x3("MOV", n, "ZERO", None)
    lab("IL")
    e("LDI", R["RR"], 0)
    e("JMP", "RESTART")
    lab("RET0")
    e("ADDI", R["LANE"], R["LANE"], 1)
    e("BNE", R["LANE"], R["C256"], "IL")
    e("ADDI", R["B"], R["ZERO"], 1)
    # Main loop.
    lab("LOOP")
    region[0] = "kernel"
    e("KERNEL")
    region[0] = "diag"
    for j in range(w, 256):
        e("XOR", j, j, j)
    region[0] = "loop"
    # Stage 1: lanes with planes 0..s1-1 zero (bit 0 in D).
    e("OR", R["D"], 0, 1)
    for j in range(2, s1):
        e("OR", R["D"], R["D"], j)
    e("BNE", R["D"], R["ONES"], "S2")
    lab("EPD")
    e("BEQ", R["B"], R["BMAX"], "FAIL6")
    e("ADDI", R["B"], R["B"], 1)
    e("JMP", "LOOP")
    # Stage 2 (a stage-1 hit): count it, then test planes s1..d-1.
    region[0] = "stage2"
    lab("S2")
    e("ADDI", R["H2"], R["H2"], 1)
    e("BGE", R["H2"], R["E2LIM"], "FAIL9")
    for j in range(s1, d):
        e("OR", R["D"], R["D"], j)
    e("BNE", R["D"], R["ONES"], "EPB")
    e("JMP", "EPD")
    # Endpoint batch: ascending lanes with a zero bit in D.
    region[0] = "epscan"
    lab("EPB")
    x3("NOT", "ND", "D", None)
    x3("MOV", "LANE", "ZERO", None)
    lab("EPL")
    x3("SHR", "T0", "ND", "LANE")
    x3("AND", "T0", "T0", "ONE")
    e("BEQ", R["T0"], R["ZERO"], "EPN")
    region[0] = "key"
    x3("MOV", "KEY", "ZERO", None)
    for j in range(k):
        x3("SHR", "T0", d + 4 + j, "LANE")
        x3("AND", "T0", "T0", "ONE")
        e("SHLI", R["T0"], R["T0"], j)
        x3("OR", "KEY", "KEY", "T0")
    region[0] = "table"
    x3("MOV", "EIDX", "ZERO", None)
    lab("SC")
    e("BEQ", R["EIDX"], R["CNT"], "NOM")
    e("SHRI", R["T1"], R["EIDX"], 2)
    e("ADDI", R["T1"], R["T1"], KEYB)
    x3("LD", "T2", "T1", None)
    x3("AND", "T3", "EIDX", "C3")
    e("SHLI", R["T3"], R["T3"], 6)
    x3("SHR", "T2", "T2", "T3")
    x3("AND", "T4", "T2", "KM")
    e("BEQ", R["T4"], R["KEY"], "MATCH")
    e("ADDI", R["EIDX"], R["EIDX"], 1)
    e("JMP", "SC")
    lab("NOM")
    e("BEQ", R["CNT"], R["ULIM"], "FAIL4")
    e("ADDI", R["T1"], R["LANE"], LIDB)
    x3("LD", "T5", "T1", None)
    e("SHLI", R["T5"], R["T5"], 47)
    x3("OR", "T5", "T5", "KEY")
    e("SHRI", R["T1"], R["CNT"], 2)
    e("ADDI", R["T1"], R["T1"], KEYB)
    x3("LD", "T2", "T1", None)
    x3("AND", "T3", "CNT", "C3")
    e("SHLI", R["T3"], R["T3"], 6)
    x3("SHL", "T4", "T5", "T3")
    x3("OR", "T2", "T2", "T4")
    e("ST", R["T1"], R["T2"])
    e("ADDI", R["CNT"], R["CNT"], 1)
    e("LDI", R["RR"], 1)
    e("JMP", "RESTART")
    region[0] = "epscan"
    lab("RET1")
    lab("EPN")
    e("ADDI", R["LANE"], R["LANE"], 1)
    e("BNE", R["LANE"], R["C256"], "EPL")
    e("JMP", "EPD")
    # Restart lane LANE at identifier NID, birth B; RR picks the return.
    region[0] = "restart"
    lab("RESTART")
    e("BEQ", R["NID"], R["IDL"], "FAIL5")
    e("ADDI", R["T1"], R["LANE"], LIDB)
    e("ST", R["T1"], R["NID"])
    e("ADDI", R["T1"], R["LANE"], BIRB)
    e("ST", R["T1"], R["B"])
    x3("ADD", "S", "RHO", "NID")
    proj("S")
    e("ADDI", R["NID"], R["NID"], 1)
    x3("SHL", "T0", "ONE", "LANE")
    x3("NOT", "NOTLANE", "T0", None)
    for j in range(256):
        e("SHRI", R["T0"], R["S"], j)
        x3("AND", "T0", "T0", "ONE")
        x3("SHL", "T0", "T0", "LANE")
        e("AND", j, j, R["NOTLANE"])
        e("OR", j, j, R["T0"])
    e("BEQ", R["RR"], R["ZERO"], "RET0")
    e("JMP", "RET1")
    # Recovery after a key match at EIDX for lane LANE.
    region[0] = "recovery"
    lab("MATCH")
    e("SHRI", R["ID1"], R["T2"], 47)
    x3("AND", "ID1", "ID1", "M17")
    e("ADDI", R["T1"], R["LANE"], LIDB)
    x3("LD", "ID2", "T1", None)
    e("ADDI", R["T1"], R["LANE"], BIRB)
    x3("LD", "T2", "T1", None)
    x3("SUB", "L2", "B", "T2")
    e("BGE", R["L2"], R["LRC"], "FAIL8")     # the replay refuses a live trail at or beyond the cap
    x3("MOV", "E", "ZERO", None)
    for j in range(256):
        x3("SHR", "T0", j, "LANE")
        x3("AND", "T0", "T0", "ONE")
        e("SHLI", R["T0"], R["T0"], j)
        x3("OR", "E", "E", "T0")
    x3("ADD", "X", "RHO", "ID1")
    proj("X")
    x3("MOV", "L1", "ZERO", None)

    def step(dst, src):
        x3("COMP", dst, src, None)
        x3("XOR", dst, dst, "PD")
        proj(dst)

    lab("RC")
    e("BEQ", R["L1"], R["LRC"], "FAIL8")      # the replay refuses a stored trail longer than the replay cap
    step("Y", "X")
    e("ADDI", R["L1"], R["L1"], 1)
    x3("MOV", "X", "Y", None)
    x3("AND", "T0", "Y", "DPM")
    e("BNE", R["T0"], R["ZERO"], "RC")
    e("BNE", R["Y"], R["E"], "FAIL2")
    x3("ADD", "A", "RHO", "ID1")
    proj("A")
    x3("ADD", "BV", "RHO", "ID2")
    proj("BV")
    e("BLT", R["L1"], R["L2"], "AL2")
    for tag, hi, lo, reg in (("AA", "L1", "L2", "A"), ("AB", "L2", "L1", "BV")):
        if tag == "AB":
            lab("AL2")
        x3("SUB", "CN", hi, lo)
        x3("MOV", "MINL", lo, None)
        lab(tag)
        e("BEQ", R["CN"], R["ZERO"], "AD")
        step(reg, reg)
        x3("SUB", "CN", "CN", "ONE")
        e("JMP", tag)
    lab("AD")
    e("BEQ", R["A"], R["BV"], "FAIL3")
    lab("PL")
    e("BEQ", R["MINL"], R["ZERO"], "FAIL8")
    step("FA", "A")
    step("FB", "BV")
    e("BEQ", R["FA"], R["FB"], "FOUND")
    x3("MOV", "A", "FA", None)
    x3("MOV", "BV", "FB", None)
    x3("SUB", "MINL", "MINL", "ONE")
    e("JMP", "PL")
    lab("FOUND")
    e("BEQ", R["A"], R["BV"], "FAIL8")
    step("FA", "A")
    step("FB", "BV")
    e("BNE", R["FA"], R["FB"], "FAIL8")
    region[0] = "term"
    e("OUT", R["A"], R["BV"])
    e("HALT", 1)
    for n in (2, 3, 4, 5, 6, 8, 9):
        lab("FAIL%d" % n)
        e("HALT", n)
    code = [(op, tuple(labels[a] if isinstance(a, str) else a for a in args), reg)
            for op, args, reg in code]
    return dict(code=code, labels=labels, nregs=kregs + len(R), nmem=LIDB + 256, ones=R["ONES"],
                regs=R, entry=0)


BODY_NAMES = ["B%d.bin" % j for j in range(1, KB + 1)]
BODY_OF = [(r - 2) % KB + 1 for r in range(2, NR - 1)]          # the body each generic round runs
IOTA_OF = [[z for z in range(64) if (RCA[r] >> z) & 1] for r in range(2, NR - 1)]


def geometry(blocks):
    """What the step stores and executes (proof 3.4)."""
    nP, nE = len(blocks["P.bin"]), len(blocks["E.bin"])
    nb = {j: len(blocks["B%d.bin" % j]) for j in range(1, KB + 1)}
    niota = sum(len(i) for i in IOTA_OF)
    # The iota XORs are control words: as kernel words each group would need a header. At 8 bytes they cost
    # 66 bytes more and save 21 traversals per batch, so a batch traverses two headers (proof 3.4).
    inline = 16 + 5 * (nP + nE) + 8 * (len(BODY_OF) + niota)
    trailing = sum(8 + 5 * nb[j] + 8 for j in range(1, KB + 1))
    ops = nP + nE + niota + sum(nb[j] for j in BODY_OF) + 2 * len(BODY_OF)
    # exec_bytes: code a batch traverses, bodies fetched as often as called (proof L.6).
    return dict(words=nP + nE + sum(nb.values()), iota_words=niota, headers=2 + KB,
                calls=len(BODY_OF) + KB, inline=inline, trailing=trailing,
                bytes=inline + trailing, ops=ops, header_ops=2,
                exec_bytes=inline + sum(8 + 5 * nb[j] for j in BODY_OF))


def code_bytes(prog, geo):
    """Declared encoding: kernel 5 bytes behind a header, control 8, loads 40 (proof 3.2)."""
    return geo["bytes"] + sum(0 if op == "KERNEL" else 40 if op == "LDI" else 8
                              for op, _, _ in prog["code"])     # the step's headers are in geo


SHORT = ("XOR", "AND", "OR", "NOT", "MOV")
LONG = SHORT + ("ADD", "ADDI", "SUB", "SHL", "SHR", "SHLI", "SHRI", "LD", "ST", "BEQ",
                "BNE", "BLT", "BGE", "JMP", "RAND", "COMP", "OUT", "HALT", "KERNEL", "JAL", "JR")
BRANCH = ("BEQ", "BNE", "BLT", "BGE", "JMP")
IMM = ("ADDI", "SHLI", "SHRI", "HALT", "KERNEL")
KOPS = ("XOR", "AND", "OR")


def kernel_forms(block):
    """Their block words in our kernel form: opcode 3 is our XOR against KONES."""
    return [("XOR", d, a, b) if c == 0 else ("AND", d, a, b) if c == 1 else
            ("OR", d, a, b) if c == 2 else ("XOR", d, a, KONES) for c, d, a, b in block]


OB = {j: (YB if j % 2 else XB) for j in range(1, KB + 1)}      # the bank body j writes


def iota_forms(i, j):
    """Round constant i: an XOR with the all-ones register, leaving the stored polarity and the cycle
    closed."""
    return [("XOR", OB[j] + z, OB[j] + z, KONES) for z in IOTA_OF[i]]


def kword(opc, d, a, b):
    assert 0 <= d < 4096 and 0 <= a < 4096 and 0 <= b < 4096
    return (1 + KOPS.index(opc) | d << 2 | a << 14 | b << 26).to_bytes(5, "little")


def khead(count):
    return (16 + LONG.index("KERNEL") | count << 38).to_bytes(8, "little")


def cword(op, regs, imm):
    regs = list(regs) + [0] * (3 - len(regs))
    assert all(0 <= r < 4096 for r in regs) and 0 <= imm < 1 << 20
    return (16 + LONG.index(op) | regs[0] << 8 | regs[1] << 20 | regs[2] << 32
            | imm << 44).to_bytes(8, "little")


def body_offsets(prog, blocks, geo):
    """Where each body's first word lands: a trailing region, so a call target is an absolute byte offset
    in the 20-bit immediate."""
    pos = 0
    for op, _, _ in prog["code"]:
        pos += geo["inline"] if op == "KERNEL" else 40 if op == "LDI" else 8
    at = {}
    for j in range(1, KB + 1):
        at[j] = pos + 8
        pos += 8 + 5 * len(blocks["B%d.bin" % j]) + 8
    return at


def encode(prog, blocks):
    """Serialize the program image; the three formats are proof Section 3.2. Branch and call targets are
    absolute byte offsets into the image."""
    geo = geometry(blocks)
    lr = prog["regs"]["LR"]
    at = body_offsets(prog, blocks, geo)
    offsets, pos = [], 0
    for op, _, _ in prog["code"]:
        offsets.append(pos)
        pos += geo["inline"] if op == "KERNEL" else 40 if op == "LDI" else 8
    out = bytearray()
    for op, args, _ in prog["code"]:
        if op == "KERNEL":
            out += khead(len(blocks["P.bin"]))
            for f in kernel_forms(blocks["P.bin"]):
                out += kword(*f)
            for i, j in enumerate(BODY_OF):
                out += cword("JAL", [lr], at[j])
                for _op, d, aa, b in iota_forms(i, j):
                    out += cword("XOR", [d, aa, b], 0)
            out += khead(len(blocks["E.bin"]))
            for f in kernel_forms(blocks["E.bin"]):
                out += kword(*f)
            continue
        if op == "LDI":
            out += (64 | args[0] << 8 | args[1] << 20).to_bytes(40, "little")
            continue
        args = [x for x in args if x is not None]
        imm = 0
        if op in BRANCH:
            imm = offsets[args.pop()]
        elif op in IMM:
            imm = args.pop()
        out += cword(op, args, imm)
    assert len(out) == pos
    for j in range(1, KB + 1):                       # the trailing body subroutines
        out += khead(len(blocks["B%d.bin" % j]))
        for f in kernel_forms(blocks["B%d.bin" % j]):
            out += kword(*f)
        out += cword("JR", [lr], 0)
    assert len(out) == pos + geo["trailing"] == code_bytes(prog, geo)
    return bytes(out)


def decode(image):
    """Decode an image into (code, blocks, calls); the inverse of encode."""
    items, pos = [], 0
    while pos < len(image):
        op = image[pos]
        if op == 16 + LONG.index("KERNEL"):
            v = int.from_bytes(image[pos:pos + 8], "little")
            count = v >> 38
            at, pos = pos, pos + 8
            words = []
            for _ in range(count):
                w = int.from_bytes(image[pos:pos + 5], "little")
                words.append((KOPS[(w & 3) - 1], w >> 2 & 4095, w >> 14 & 4095, w >> 26 & 4095))
                pos += 5
            items.append(("K", words, at))
        elif op == 64:
            v = int.from_bytes(image[pos:pos + 40], "little")
            items.append(("LDI", (v >> 8 & 4095, v >> 20), pos))
            pos += 40
        else:
            v = int.from_bytes(image[pos:pos + 8], "little")
            items.append((LONG[op - 16], (v >> 8 & 4095, v >> 20 & 4095, v >> 32 & 4095, v >> 44), pos))
            pos += 8
    k0 = next(n for n, it in enumerate(items) if it[0] == "K")
    blocks, calls, n = {}, [], k0
    blocks["P.bin"] = items[n][1]
    n += 1
    iota = []
    for i in range(len(BODY_OF)):                      # JAL, then the round's iota XORs
        assert items[n][0] == "JAL", items[n][0]
        calls.append((items[n][1][0], items[n][1][3]))
        n += 1
        grp = []
        for _z in IOTA_OF[i]:
            assert items[n][0] == "XOR", items[n][0]
            grp.append(("XOR",) + tuple(items[n][1][:3]))
            n += 1
        iota.append(grp)
    assert items[n][0] == "K"
    blocks["E.bin"] = items[n][1]
    step_end = n + 1
    tail = len(items)
    for j_ in range(KB, 0, -1):                        # the trailing bodies, read from the end
        assert items[tail - 1][0] == "JR", items[tail - 1][0]
        calls.append((items[tail - 1][1][0], None))
        blocks["B%d.bin" % j_] = items[tail - 2][1]
        tail -= 2
    code, nn, index = [], 0, {}
    seq = items[:k0] + [("STEP", (), items[k0][2])] + items[step_end:tail]
    for kind, payload, at in seq:
        index[at] = nn
        nn += 1
    nargs = dict(XOR=3, AND=3, OR=3, ADD=3, SUB=3, SHL=3, SHR=3, NOT=2, MOV=2, LD=2,
                 ST=2, COMP=2, OUT=2, ADDI=2, SHLI=2, SHRI=2, BEQ=2, BNE=2, BLT=2, BGE=2,
                 RAND=1, JMP=0, HALT=0, JAL=1, JR=1)
    for kind, payload, at in seq:
        if kind == "STEP":
            code.append(("KERNEL", ()))
        elif kind == "LDI":
            code.append(("LDI", payload))
        else:
            args = list(payload[:nargs[kind]])
            if kind in BRANCH:
                args.append(index[payload[3]])
            elif kind in IMM:
                args.append(payload[3])
            code.append((kind, tuple(args)))
    for i_ in range(len(BODY_OF)):                     # the iota groups, in round order
        blocks["I%d" % i_] = iota[i_]
    return code, blocks, calls


def load(p, kregs, blocks):
    """Build, serialize and decode; the interpreter runs the decoded image (L.5)."""
    geo = geometry(blocks)
    prog = build_program(p, kregs)
    image = encode(prog, blocks)
    code, dec, calls = decode(image)
    norm = [(op, tuple(x for x in a if x is not None)) for op, a, _ in prog["code"]]
    assert code == norm
    for name in ["P.bin", "E.bin"] + BODY_NAMES:
        assert dec[name] == kernel_forms(blocks[name]), name
    for i in range(len(BODY_OF)):
        assert dec["I%d" % i] == iota_forms(i, BODY_OF[i]), i
    lr = prog["regs"]["LR"]
    at = body_offsets(prog, blocks, geo)
    assert calls[:len(BODY_OF)] == [(lr, at[j]) for j in BODY_OF]
    assert calls[len(BODY_OF):] == [(lr, None)] * KB
    assert max(at.values()) < 1 << 20 and len(image) == code_bytes(prog, geo)
    prog = dict(prog, code=[(op, a, reg) for (op, a), (_, _, reg) in zip(code, prog["code"])])
    return prog, image


class Machine:
    """Block interpreter: per-block static costs times execution counts."""

    def __init__(self, prog, kops):
        code = prog["code"]
        starts = {0} | {i + 1 for i, (op, _, _) in enumerate(code)
                        if op in ("BEQ", "BNE", "BLT", "BGE", "JMP", "HALT", "KERNEL")}
        starts |= set(prog["labels"].values())
        starts = sorted(s for s in starts if s < len(code))
        self.block_of = {s: i for i, s in enumerate(starts)}
        self.costs, src = [], ["def make(E, M):", " fs = []"]
        cmp = dict(BEQ="==", BNE="!=", BLT="<", BGE=">=")
        for bi, s in enumerate(starts):
            end = starts[bi + 1] if bi + 1 < len(starts) else len(code)
            cost = defaultdict(int)
            src.append(" def f(r, m):")
            nxt = None
            for i in range(s, end):
                op, a, reg = code[i]
                cost[reg] += kops if op == "KERNEL" else COST.get(op, 1)
                if op == "COMP":
                    cost["compressions"] += 1
                line = {
                    "XOR": "r[{0}]=r[{1}]^r[{2}]", "AND": "r[{0}]=r[{1}]&r[{2}]",
                    "OR": "r[{0}]=r[{1}]|r[{2}]", "NOT": "r[{0}]=r[{1}]^M",
                    "MOV": "r[{0}]=r[{1}]", "ADD": "r[{0}]=(r[{1}]+r[{2}])&M",
                    "ADDI": "r[{0}]=(r[{1}]+{2})&M", "SUB": "r[{0}]=(r[{1}]-r[{2}])&M",
                    "SHL": "r[{0}]=(r[{1}]<<r[{2}])&M", "SHR": "r[{0}]=r[{1}]>>r[{2}]",
                    "SHLI": "r[{0}]=(r[{1}]<<{2})&M", "SHRI": "r[{0}]=r[{1}]>>{2}",
                    "LDI": "r[{0}]={1}", "LD": "r[{0}]=m[r[{1}]]", "ST": "m[r[{0}]]=r[{1}]",
                    "RAND": "r[{0}]=E.rand", "COMP": "r[{0}]=E.comp(r[{1}])",
                    "OUT": "E.out=(r[{0}],r[{1}])", "KERNEL": "E.kern(r)",
                    "HALT": "E.halt={0}",
                }.get(op)
                if line:
                    src.append("  " + line.format(*a))
                if op in cmp:
                    nxt = "%d if r[%d]%sr[%d] else %d" % (self.block_of[a[2]], a[0], cmp[op],
                                                           a[1], bi + 1)
                elif op == "JMP":
                    nxt = str(self.block_of[a[0]])
                elif op == "HALT":
                    nxt = "-1"
            src.append("  return " + (nxt or str(bi + 1)))
            src.append(" fs.append(f)")
            self.costs.append(dict(cost))
        src.append(" return fs")
        scope = {}
        exec(compile("\n".join(src), "<machine>", "exec"), scope)
        self.make = scope["make"]
        self.prog = prog
        self.kernel_block = self.block_of[next(i for i, c in enumerate(code) if c[0] == "KERNEL")]
        self.stage2_block = self.block_of[prog["labels"]["S2"]]

    def run(self, kern, comp, rand, stop_after=None):
        env = type("Env", (), {})()
        env.kern, env.comp, env.rand, env.out, env.halt = kern, comp, rand, None, None
        fs = self.make(env, M256)
        r, m = [0] * self.prog["nregs"], [0] * self.prog["nmem"]
        counts = [0] * len(fs)
        b, kb = 0, self.kernel_block
        while b >= 0:
            if b == kb and stop_after is not None and counts[kb] >= stop_after:
                break
            counts[b] += 1
            b = fs[b](r, m)
        ops = defaultdict(int)
        for c, cost in zip(counts, self.costs):
            for reg, v in cost.items():
                ops[reg] += c * v
        R = self.prog["regs"]
        return dict(reason=env.halt, pair=env.out, batches=counts[kb],
                    stage2=counts[self.stage2_block],
                    insertions=r[R["CNT"]], starts=r[R["NID"]], ops=dict(ops), r=r)


def flat_decoded(dec):
    """One batch's executed stream, from the decoded blocks."""
    out = list(dec["P.bin"])
    for i, j in enumerate(BODY_OF):
        out += dec["B%d.bin" % j] + dec["I%d" % i]
    return out + list(dec["E.bin"])


def compile_forms(forms):
    """Execute those words: what the image computes, word for word."""
    P = tuple((("XOR", "AND", "OR").index(o), d, a, b) for o, d, a, b in forms)

    def step(r):
        for c, d, a, b in P:
            if c == 0:
                r[d] = r[a] ^ r[b]
            elif c == 1:
                r[d] = r[a] & r[b]
            else:
                r[d] = r[a] | r[b]
    return step


def lanewise(fn):
    """Test kernel: apply fn independently to each of the 256 lanes."""
    def kern(r):
        planes = r[:256]
        outs = []
        for lane in range(256):
            u = 0
            for j in range(256):
                u |= ((planes[j] >> lane) & 1) << j
            outs.append(fn(u))
        r[:256] = [sum(((outs[l] >> j) & 1) << l for l in range(256)) for j in range(256)]
    return kern


def agree(run, pair, s):
    keys = ("reason", "insertions", "stage2")
    ok = all(run[k] == s[k] for k in keys) and run["pair"] == pair
    ok = ok and run["starts"] == s["allocated_starts"]
    ok = ok and run["batches"] * 256 == s["search_evaluations"]
    ok = ok and run["ops"].get("compressions", 0) == s["recovery_evaluations"] + s["final_evaluations"]
    if not ok:
        raise AssertionError("machine and reference disagree: %r %r %r" % (run, pair, s))


def fixtures(kregs):
    """Every termination against the reference (proof L.5): 1 a pair, 2 the stored endpoint unreached, 3 the
    trails meet at once, 4 the table full, 5 no identifier, 6 the horizon, 8 a replay guard, 9 the budget."""
    base = dict(w=12, d=3, k=4, U=8, B=4, LRC=4, IDL=2048, E2MAX=1000)
    rho = 256
    cases = [  # (overrides, parameter changes, expected reason)
        ({256: 8, 257: 8}, {}, 1),
        ({256: 8, 257: 8 | 2048}, {}, 2),
        ({256: 257, 257: 8}, {}, 3),
        ({256: 8}, dict(U=0), 4),
        ({256: 8, 257: 16 | 128}, dict(U=1), 4),   # second endpoint has a different key
        ({}, dict(B=3), 6),                        # no lane is ever distinguished
        ({256: 8, 257: 136, 258: 264}, dict(IDL=258, U=4), 5),  # distinct keys; the third restart has no id
        ({256: 8, 300: 8}, {}, 1),
        ({256: 5, 5: 7, 7: 8, 257: 9, 9: 8}, {}, 1),
        ({256: 5, 5: 8, 257: 9, 9: 8}, dict(LRC=1), 8),        # the stored trail is longer than the replay cap
        ({256: 17, 17: 19, 19: 21, 21: 8, 257: 8}, {}, 8),     # the LIVE trail reaches the cap, stored is 1
        ({256: 5, 5: 7, 7: 9, 9: 11, 11: 13, 13: 8, 512: 16},  # STORED walk hits the cap, live age 1
         dict(B=8), 8),
        ({256: 8}, dict(E2MAX=0), 9),                # stage-1 hit budget exhausted
        ({256: 8, 300: 8}, dict(E2MAX=1), 1),        # one stage-2 batch allowed
    ]
    for over, change, want in cases:
        p = dict(base, **change)
        fn = lambda u, o=over: o.get(u, u | 1)
        g = geometry(STUB)
        mach = Machine(load(p, kregs, STUB)[0], g["ops"] + g["header_ops"])
        run = mach.run(lanewise(fn), lambda u, f=fn: f(u) ^ PD, rho)
        pair, s = bounded_search(fn, width=p["w"], dp_bits=p["d"], key_bits=p["k"],
                                 lanes=256, batches=p["B"], lrc=p["LRC"], capacity=p["U"],
                                 start_limit=p["IDL"], rho=rho, stage2_limit=p["E2MAX"],
                                 )
        agree(run, pair, s)
        assert run["reason"] == want, (over, change, run["reason"])
    return len(cases)


# One-word blocks: fixtures and probes exercise the control, not the step.
STUB = dict({"B%d.bin" % j: [(0, 0, 0, KONES)] for j in range(1, KB + 1)},
            **{"P.bin": [(0, 0, 0, KONES)], "E.bin": [(0, 0, 0, KONES)]})
# Deployed parameters, proof 2.1; the stage-2 budget is proof P step 5's 32 Q/2^32.
BMUL = 1047331                 # B = BMUL * 2^100, the least horizon certified at 0.39 on the grid
UCAP = 67456                   # the least capacity the bound admits, not the most the memory allows
LRCV = 21 * 2 ** 111           # replay cap, 10.5 / theta
FULL = dict(w=256, d=112, k=47, U=UCAP, B=BMUL * 2 ** 100, LRC=LRCV,
            IDL=1 << 17, E2MAX=32 * BMUL * 2 ** 76)           # 32 Q/2^32 (proof P, step 5)


def formulas(p, kops):
    """Closed-form operation counts of the program text (proof Section L)."""
    d, k, nmem = p["d"], p["k"], -(-p["U"] // 4) + 512
    s1 = min(32, d)
    rs = {0: 1292, 1: 1293}
    # Per batch: the step (kops operations), then (s1-1) ORs + BNE 2 + 4 control; nothing is cut.
    # Stage 2: ADDI 1 + BGE 2 + (d-s1) ORs + BNE 2 (+ JMP 1 on a miss).
    return dict(batch=kops + s1 + 5, stage2=d - s1 + 5, stage2_miss=d - s1 + 6,
                setup=15 + 2 + 4 * nmem + 5 + 256 * (5 + rs[0]) + 1,   # 14 constant loads and RAND
                epscan=1795, key=1 + 4 * k, insert=20, per_entry=13, restart=rs,
                rec_fixed=1048, rec_step=72,
                align_step=69, pair_step=138, found=268, term=3,
                terminal=13 * p["U"] + 5, match_extra=12)


def wiring(p, full, blocks):
    """The image's constants and record packing (proof M.3)."""
    loads = {a[0]: a[1] for op, a, _ in full["code"] if op == "LDI"}
    R = full["regs"]
    for name, want in (("BMAX", p["B"]), ("LRC", p["LRC"]), ("ULIM", p["U"]), ("IDL", p["IDL"]),
                       ("E2LIM", p["E2MAX"] + 1), ("PD", PD), ("DPM", (1 << p["d"]) - 1),
                       ("KM", (1 << p["k"]) - 1), ("ONES", M256)):
        assert loads[R[name]] == want, name
    for n_ in ["P.bin", "E.bin"] + BODY_NAMES:
        assert max(max(w[1:]) for w in blocks[n_]) < REGTOP, n_   # no block touches a control register
    sh = next(a[2] for op, a, _ in full["code"] if op == "SHLI" and a[0] == R["T5"])
    idn, key = p["IDL"] - 1, (1 << p["k"]) - 1
    rec = (idn << sh) | key
    assert p["k"] <= sh and rec < 1 << 64 and rec >> sh == idn and rec & key == key
    return dict(constants=len(loads), record_shift=sh, record_bits=rec.bit_length(),
                id_bits=idn.bit_length(), identifiers_above_65536=max(0, p["IDL"] - 65536))


def probes(kregs):
    """Handler costs at the deployed parameters."""
    G = geometry(STUB)
    kops = G["ops"] + G["header_ops"]
    f = formulas(FULL, kops)
    L = 2 ** (FULL["d"] + 4)      # distinguished, with distinct keys (l + 1)
    rho = (1 << 200) + 12345
    mach = Machine(load(FULL, kregs, STUB)[0], kops)
    plain = lambda u: u | 1
    comp = lambda fn: (lambda u: fn(u) ^ PD)
    run = mach.run(lanewise(plain), comp(plain), rho, stop_after=3)
    o = run["ops"]
    assert o["kernel"] == 3 * kops and o["loop"] == 3 * (f["batch"] - kops)
    assert o["setup"] + o["restart"] == f["setup"], (o, f["setup"])
    for n in range(4):  # n endpoints in batch one, table counts 0..n-1
        over = {(rho + l) & M256: (l + 1) * L for l in range(n)}
        fn = lambda u, o=over: o.get(u, u | 1)
        o = mach.run(lanewise(fn), comp(fn), rho, stop_after=1)["ops"]
        assert o.get("epscan", 0) == (f["epscan"] if n else 0)
        assert o.get("stage2", 0) == (f["stage2"] if n else 0), (n, o.get("stage2"), f["stage2"])
        assert o.get("key", 0) == n * f["key"]
        assert o.get("table", 0) == n * f["insert"] + f["per_entry"] * n * (n - 1) // 2
        assert o["restart"] - 256 * f["restart"][0] == n * f["restart"][1]
    # A stage-1 hit with no distinguished lane (plane 40 set): the miss path, charged E2MAX times.
    fn = lambda u: (1 << 40) if u == rho else u | 1
    o = mach.run(lanewise(fn), comp(fn), rho, stop_after=1)["ops"]
    assert o.get("stage2", 0) == f["stage2_miss"] and o.get("epscan", 0) == 0, o
    # The replay cap: two trails of two evaluations against a cap of one are refused (8).
    mid, mid2 = 15 << FULL["d"], 13 << FULL["d"]
    over = {rho & M256: mid, mid: L, (rho + 1) & M256: mid2, mid2: L}
    fn = lambda u, o=over: o.get(u, u | 1)
    mr = Machine(load(dict(FULL, LRC=1), kregs, STUB)[0], kops)
    run = mr.run(lanewise(fn), comp(fn), rho)
    assert run["reason"] == 8, run["reason"]
    assert run["ops"]["compressions"] <= 1 + 1, run["ops"]["compressions"]
    # Capacity terminal: U = 1, two endpoints with distinct keys in batch one.
    fn = lambda u: L if u == rho else 2 * L if u == (rho + 1) & M256 else u | 1
    mu = Machine(load(dict(FULL, U=1), kregs, STUB)[0], kops)
    run = mu.run(lanewise(fn), comp(fn), rho)
    assert run["reason"] == 4
    assert run["ops"]["table"] == f["insert"] + 13 * 1 + 5
    # Recovery with stored length l1 and current length l2 (direct chains).
    for l1, l2 in ((1, 1), (2, 3), (3, 1), (4, 4)):   # all within the replay cap
        def chain(start, length, tag):
            pts = [start] + [(tag << 120) | (i << (FULL["d"] + 5)) | 1 for i in range(1, length)]
            return {pts[i]: pts[i + 1] for i in range(length - 1)}, pts[-1]
        o1, end1 = chain(rho & M256, l1, 1)
        o2, end2 = chain((rho + 1) & M256, l2, 2)
        over = {**o1, **o2}
        over[end1] = over[end2] = 5 * L
        fn = lambda u, o=over: o.get(u, u | 1)
        run = mach.run(lanewise(fn), comp(fn), rho)
        o = run["ops"]
        stored, m = (l2 if l2 < l1 else l1), min(l1, l2)
        want = (f["rec_fixed"] + stored * f["rec_step"] + abs(l1 - l2) * f["align_step"]
                + (m - 1) * f["pair_step"] + f["found"])
        assert run["reason"] == 1 and o["term"] == f["term"]
        assert o["compressions"] == stored + abs(l1 - l2) + 2 * m + 2
        assert o["recovery"] == want, (l1, l2, o["recovery"], want)
        assert o["table"] == f["insert"] + f["match_extra"]  # one insertion, match at entry 0
    return f


TARGET = "sha3-256-r24-prefix-v1"
MAIN_ID = "sha3-256-r24-looped-machine-v1"
BOUND_ID = "sha3-256-r24-looped-bound-v1"
# Projected end-to-end parameters: the deployed predicate at width 16, LRC at the deployed 10.5 / theta.
PROJ = dict(w=16, d=3, k=9, U=256, B=48, LRC=84, IDL=4096, E2MAX=4608)   # LRC/L 10.5 as deployed
TAIL_LOG2 = -40


def _up(x):
    return x * (1 + Dm("1e-40")) + Dm("1e-58")


def _dn(x):
    return x * (1 - Dm("1e-40")) - Dm("1e-58")


def _fd(x, upper):
    """Decimal enclosure of a rational, rounded in the stated direction."""
    with localcontext() as cx:
        cx.rounding = ROUND_CEILING if upper else ROUND_FLOOR
        return Dm(x.numerator) / Dm(x.denominator)


def _ex(x):
    return _up(_fd(x, True).exp())


def _chernoff_k(q):
    """Least k with e^-q (e q / k)^k <= 2^TAIL_LOG2."""
    qu, qd = _fd(q, True), _fd(q, False)
    limit = Dm(2).ln() * TAIL_LOG2
    k = int(q) + 1
    while _up(-qd + k * (1 + (qu / k).ln())) > limit * (1 - Dm("1e-40")):
        k += 1
    return k


def certify():
    """Exact bound of proof Section P at the frozen parameters."""
    theta = Fr(1, 2 ** FULL["d"])
    L = 1 / theta
    B, U, LRC, K, IDL = FULL["B"], FULL["U"], FULL["LRC"], FULL["k"], FULL["IDL"]
    N = 1 << 256
    Q = 256 * B
    # The bound assumes the deployed parameters; tie them to the program.
    assert FULL["w"] == 256 and FULL["d"] == 112 and K == 47
    assert theta == Fr(1, 2 ** 112) and LRC == 21 * 2 ** 111 and U == UCAP
    assert FULL["E2MAX"] == 32 * Q // 2 ** 32   # the budget proof P step 5 needs
    Np = N - N * theta
    assert Np.denominator == 1
    Np = int(Np)
    q = Q * theta
    k = _chernoff_k(q)
    assert k < U, "the table capacity must exceed the certified count of distinguished values"
    shift = _fd(1 / (1 - Fr(k * Q, Np)), True)
    lam = lambda m: Fr(m * (m - 1), 2 * Np)
    pi_up = lambda m: _up((-_fd(lam(m), False)).exp())
    pi_lo = lambda m: _dn((-_fd(lam(m) + Fr((m - 1) * m * (2 * m - 1), 6) / Fr(Np) ** 2, True)).exp())
    fine, coarse = 20000, 2000
    split = max(1, Q - 150 * 256 * (L.numerator // L.denominator + 1))
    edges = ([split * i // coarse for i in range(coarse + 1)]
             + [split + (Q - split) * i // fine for i in range(1, fine + 1)])
    delay, pa = Dm(0), pi_up(edges[0])
    for a, b in zip(edges, edges[1:]):
        pb = pi_lo(b)
        delay += (pa - pb) * _ex(-theta * max(0, B - (-(-b // 256))))
        pa = pi_up(b)
    delay = _up(delay) * shift
    PP = Fr(Q * (Q - 1), 2 * Np)
    terms = {
        "no_duplicate": pi_up(Q) * shift,
        "detection_delay": delay,
        "own_trail": _fd(Fr(Q) * L / Np, True),
        # the live guard refuses at LRC, so an accepted pair has live age at most LRC - 1
        "replay_refusal": _fd(Fr(Q * (Q - 1), N), True) * _ex(-Fr(LRC - 1) * theta)
                          * _fd(1 + Fr(LRC - 1) * theta, True),
        "disturbed_suffix": _fd(PP * L * (Q + IDL) / Np, True),
        "same_batch_pair": _fd(Fr(255 * Q, Np), True),
        "start_hit": _fd(Fr(Q * IDL, N), True),
        "distinguished_class_duplicate": _fd(Fr(k * k) * L / N, True),
        "count_tail_N1": Dm(2) ** TAIL_LOG2,
        "false_key": _fd(Fr(k * U, 2 ** K), True),
        "stage2_budget_and_rounding": Dm(2) ** -90,
    }
    lower = 1 - sum(terms.values())
    return lower, terms, k


def _q15(x, up_):
    return str(Dm(x).quantize(Dm("1e-15"), rounding=ROUND_CEILING if up_ else ROUND_FLOOR))


def bound_main(request):
    event = dict(kind="digest-xor-mask", mask_hex="ff" * 32, expected_hex="00" * 32)
    if (request["schema_version"] != 1 or request["experiment_id"] != BOUND_ID
            or request["target_profile"] != TARGET or request["event"] != event):
        raise ValueError("Unexpected organizer request")
    lower, terms, k = certify()
    obs = dict(certified=1 if lower >= Dm("0.39") else 0, chernoff_k=k, U=FULL["U"], trails_cut=0,
               bound_floor=float(_q15(lower, False)), margin=float(_q15(lower - Dm("0.39"), False)),
               loss_sum=float(_q15(1 - lower, True)))
    for n in ("no_duplicate", "detection_delay", "replay_refusal", "own_trail", "disturbed_suffix", "false_key"):
        obs[n] = float(_q15(terms[n], True))
    rows = [dict(trial=t["trial"], message_a_hex=None, message_b_hex=None, observations=obs)
            for t in request["trials"]]
    json.dump(dict(schema_version=1, trials=rows), sys.stdout, sort_keys=True, separators=(",", ":"))


def main():
    request = json.load(sys.stdin)
    if request.get("experiment_id") == BOUND_ID:
        return bound_main(request)
    event = dict(kind="digest-xor-mask", expected_hex=bytes(32).hex(),
                 mask_hex=((1 << 16) - 1).to_bytes(32, "little").hex())   # the low 16 planes agree
    if (request["schema_version"] != 1 or request["experiment_id"] != MAIN_ID
            or request["target_profile"] != TARGET or request["event"] != event
            or request["max_message_bytes"] < 128):
        raise ValueError("Unexpected organizer request")
    global PD
    blocks, PD = build_blocks()                      # their builder and their block-hash gate
    kregs = REGTOP
    geo = geometry(blocks)
    assert (geo["words"], geo["iota_words"], geo["ops"], geo["headers"], geo["calls"], geo["header_ops"]) \
        == (STEP_WORDS, 78, STEP_OPS, 10, 29, 2), geo
    nfix = fixtures(kregs)
    f = probes(kregs)
    full, image = load(FULL, kregs, blocks)
    wire = wiring(FULL, full, blocks)
    assert full["nregs"] <= NREG and code_bytes(full, geo) == len(image)
    kern = compile_forms(flat_decoded(decode(image)[1]))  # the decoded image's blocks are what runs
    wm = (1 << PROJ["w"]) - 1
    table = [int.from_bytes(hashlib.sha3_256(msg_of(u)).digest(), "little") for u in range(1 << PROJ["w"])]
    gs = geometry(STUB)
    mach = Machine(load(PROJ, kregs, STUB)[0], gs["ops"] + gs["header_ops"])
    checked = [0]

    def checked_kernel(r):
        sel = ((checked[0] * 37) % 256, (checked[0] * 101 + 7) % 256, 0, 255)
        ins = [sum(((r[j] >> l) & 1) << j for j in range(256)) for l in sel]
        kern(r)
        for l, u in zip(sel, ins):
            if sum(((r[j] >> l) & 1) << j for j in range(256)) != table[u] ^ PD:
                raise AssertionError("kernel lane mismatch")
        checked[0] += 1

    rows = []
    for t in request["trials"]:
        seed = bytes.fromhex(t["seed"])
        rho = int.from_bytes(hashlib.sha256(seed).digest(), "little") & wm
        before = checked[0]
        run = mach.run(checked_kernel, lambda u: table[u], rho)
        step = lambda u: (table[u] ^ PD) & wm
        pair, st = bounded_search(step, width=PROJ["w"], dp_bits=PROJ["d"], key_bits=PROJ["k"], lanes=256,
                                  batches=PROJ["B"], lrc=PROJ["LRC"], capacity=PROJ["U"],
                                  start_limit=PROJ["IDL"], rho=rho, stage2_limit=PROJ["E2MAX"])
        agree(run, pair, st)
        # One full-width batch of random points, four seed-chosen lanes against the library digest.
        r = [int.from_bytes(hashlib.sha256(seed + bytes([j])).digest(), "little") for j in range(256)]
        r += [0] * (full["nregs"] - 256)
        r[full["ones"]] = M256
        sel = tuple(seed[:4])
        ins = [sum(((r[j] >> l) & 1) << j for j in range(256)) for l in sel]
        kern(r)
        for l, u in zip(sel, ins):
            if sum(((r[j] >> l) & 1) << j for j in range(256)) != F_ref(u, PD):
                raise AssertionError("full-width kernel lane mismatch")
        o = run["ops"]
        obs = dict(reason=run["reason"], batches=run["batches"], insertions=run["insertions"],
                   stage2=run["stage2"], starts=run["starts"], compressions=o.get("compressions", 0),
                   lanes_checked=4 * (checked[0] - before) + len(sel))
        extra = [
            dict(step_ops=geo["ops"] + geo["header_ops"], step_words=geo["words"],
                 step_headers=geo["headers"],
                 step_calls=geo["calls"], step_bytes=geo["bytes"], kernel_registers=kregs,
                 declared_registers=NREG, fixtures=nfix),
            dict(batch_ops=f["batch"], stage2_ops=f["stage2"], stage2_miss_ops=f["stage2_miss"],
                 setup_ops=f["setup"], epscan_ops=f["epscan"], key_ops=f["key"], insert_ops=f["insert"],
                 per_entry_ops=f["per_entry"]),
            dict(rec_fixed_ops=f["rec_fixed"], rec_step_ops=f["rec_step"], align_step_ops=f["align_step"],
                 pair_step_ops=f["pair_step"], found_ops=f["found"], term_ops=f["term"],
                 restart0_ops=f["restart"][0], restart1_ops=f["restart"][1]),
            dict(image_bytes=len(image), code_bytes=code_bytes(full, geo), data_words=full["nmem"],
                 control_instructions=len(full["code"]) - 1, control_registers=full["nregs"] - kregs,
                 control_loads=sum(op == "LDI" for op, _, _ in full["code"]),
                 terminal_ops=f["terminal"], trails_cut=0),
            dict(**wire, call_target_max=max(body_offsets(full, blocks, geo).values()),
                 output_polarity=PD, image_sha256=int.from_bytes(hashlib.sha256(image).digest(), "big")),
            # the deployed constants and the source they came from, so a stale report is not taken for a
            # fresh one; every value is a number, as the organizer's observation rule requires
            dict(deployed_b=FULL["B"], deployed_u=FULL["U"], deployed_lrc=FULL["LRC"],
                 deployed_e2max=FULL["E2MAX"], deployed_d=FULL["d"], deployed_k=FULL["k"],
                 step_exec_bytes=geo["exec_bytes"],
                 src_sha256=int.from_bytes(hashlib.sha256(open(__file__, "rb").read()).digest(), "big")),
        ]
        if t["trial"] < len(extra):
            obs.update(extra[t["trial"]])
        rows.append(dict(trial=t["trial"],
                         message_a_hex=msg_of(pair[0]).hex() if pair else None,
                         message_b_hex=msg_of(pair[1]).hex() if pair else None,
                         observations=obs))
    json.dump(dict(schema_version=1, trials=rows), sys.stdout, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    main()
