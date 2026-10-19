"""LS5 (LS1 LOOP): distinguished-point collision search on sha3-256-rNN-prefix-v1 with a linear-structure message embedding.

Chain function on 256-bit points u (little-endian lanes u0..u3):
  m(u) = 128 bytes = lanes 0..15 of the absorbed state: lane 1 = u0, lane 6 = u1, lane 11 = u0^u1^K11,
  lane 4 = u2, lane 9 = u3, lane 14 = u2^u3^K14, the other lanes 0..15 the constants K below; padding gives lane 16 =
  0x8000000000000006.  F(u) = SHA3-256-rNN(m(u)) XOR PD (PD a fixed 256-bit mask).  m is injective, so F(u) = F(u') with
  u != u' gives two distinct messages with equal complete digests.
This program regenerates in Python the blocks of the generator gen4.c (proof.md Appendix B; same algorithm, node order and
register allocation): the prefix P (rounds 0 and 1), the KB bodies of the cycle over the generic rounds and the last round E,
from the generator's decisions PLAN, and refuses to run unless every block hashes to the SHA-256 of the generator's file.
It executes the step as the attack executes it (P; for each generic round r its body and the iota XORs of round r with the
all-ones register; E), checks it against a plain implementation, and runs (the searches of ls1.py of 71fefe66, unchanged)
  rho-w22   : the search of proof.md Section 4 at width 22 (planes 22..255 zeroed after each step), one pair per trial;
              the table keeps the trail number of each end; the replay measures the stored trail by walking it;
  proj-w256 : eight chained full-width steps from 256 random points, first pair agreeing on the 22 low digest bits.
One Python integer holds a plane for all trials of the request (trial t in bits 256t..256t+255); trials never interact.
"""
import sys, json, hashlib

M64 = (1 << 64) - 1
RCA = [0x1, 0x8082, 0x800000000000808A, 0x8000000080008000, 0x808B, 0x80000001, 0x8000000080008081, 0x8000000000008009,
       0x8A, 0x88, 0x80008009, 0x8000000A, 0x8000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
       0x8000000000008002, 0x8000000000000080, 0x800A, 0x800000008000000A, 0x8000000080008081, 0x8000000000008080,
       0x80000001, 0x8000000080008008]
ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
NR = 19                         # rounds of the target
PLAN = """
trial 3600
nr 19 optmode 3
F1 1304108006401011100050a28000283404840922081000000202000124000010020000100090048c
G1 00210000002000000000000000021000000000000200000000000000000000000000000000000000
FG 2 68000000044000100980028020001020000000421000000001000c0200000000021401b008200180 20000003800400000849010100000101081802844018004020086200021404a20001801001003409
FG 3 0010022002001000000234a401010000000104011000a00331008000000140220100000830400420 0204840020001000930418200c080200000480221390001438080004041000000204010001060100
FG 4 000400000000381200000000000402008008c81408a0400100008000125000500010004008000a04 04020000004810006004220801010010a81401020400280000800033020000400208200800020000
FG 5 180048011002c2068000800100400821020400080000000c00080014000802000000000080080012 4040244414a00302c8880880221808c04500010820103000300802000200c0082000021000400000
FG 6 814a022208041120002a500c240800003802040000600020a14040000c0010000042000400013100 0400081088400400000000c490010000080880400020c10801280001090200810080004020482400
FG 7 000000882000048800410800010401002211000000024028000008400010008040b0040001030400 0884000c00285094c1401901a00110020200000c104000002000814100800101a804401120408003
FG 8 20004082000040400820440000100001000200000281008420884000846504104800404000202018 8404000601008180212408000000001088001e800a02c11900808091200881000001001133000543
FG 9 04007240100000420200008801000108242002023260008002011002022000080000000694504042 0000440000000680010804c0000141000300100010002001004022180201000038130210c04b1030
FG 10 034102800150220000402040000000000289000080800018000208010200228204002000406800c2 2000000042000000400410102891442801404082000010480001180801004000b400001480001080
FG 11 2080002050208000380880011001001000002000002000000002000400a000000104200005008000 0064004000400240400208060400220200890c000000420102004028802501110422c00480011902
FG 12 00000000000000080002000000000000200000000001000000000000000000000408000000008000 00801000004000060000004000280840400000000200000002010406230800509020441040080141
PHI 0 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 1 0004000000a00000200200000000000400000081000000008000000000000000000000000000000002020000204000000004100000006004000000321000020000000000080004200008000000000000000000000000400000000000000000000000000000000000000000000002008000000000000000002000000000000800000000000000002400000000040200010000000000000000000000000100000000400000000000600802000010000000000000080040000000000002000000000000000000080000
PHI 2 0000000000840000000000000000000000100000000000200000000000000000000000000000000000000000000000000000000000200000000040000000000000000000100000000000000000000000002000000000000000000000004000200000080000000000000000000000020000000000002000000000000000000000000000000000001000000000000000000000000000000000000080000000000000000100000080000200000000000000000000040000000008000000800000000000000008000000
PHI 3 0000000000000000800000000000000000000000080000000000000000200000000000000000000000000000100000000000000004000000000002004100000000000000000000000000000000000000000000000001000000000000000000000420010000200000000000000000000000000000800008000010000000000000000000000001000000000000000000001000000000000000000080000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 4 0000000000008000000000000000000008000000000000000008001000000000000001000000000000000000000001000000000000040400000a00000000008000000000000000000000000000000004010000000000000000000000000000000000000000000000000000000000210000000000080004000002000000000080200000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000080000000000000000000000000000000000000000000000000
PHI 5 0400000000000000008000000200010000000411000000000004020000000000000000000000000000000000008000000000100000000081200000000000002000000000000400000200000000000000000000000000000000000020001000000000000000000000000000000000000000000000000000000000000000040000000008000000000000000000000000001000000000000002000040004000000000000000040000000000000000000002000000000000000000000000000000200000000000000000
PHI 6 0000000020000000000000000000000000000000000080000200000000100000000000020200000000000000000000000000000002000100000000000000000000000000000000000000080000000000020000000000000000000000000000000000000000040000000401020000008004000000000000000000000008000000000000000000010000000000000000000000000000008000000000000000000000200000000000000080080000000000000001000000000000000002000000000000000000000000
PHI 7 0000000000000004000000000000000000000080000000000000000000000000000000000000000000000000000000020000200040000040000000000400000000000000080000000000000000000000000010010000000000000000000008000000000000000000000000000000000000000000000000800008000000000000000000000000000000002002000000400000000000000000000001000000000000000040000020000000000000000010000000000000000000000000000000400000400000000000
PHI 8 0000004000000000000000000000000000000000000000000000000000000000000000000000000000000040000000000000000000000001100000002000000000000404000000200000000000000000000000000000000000000000000280080000000040000000000000000008000000000000000000000000000000000040000000000000000000000400000800200000000000800000000000000000000000000000001000080000000200000800000002000000000000000000200000000000000000000080
PHI 9 0000000000200000000000000000000000000000000000000000000000000000000000000000000000000080000000000000000000000000400000000000000100000800000002000000000000000402000400008000000000000000000000001000000000000000000000000800100000020000000000040000000000000000000000000001000000000000000000000000408000000004000000000000000000010000000000000000000000000000000000000000400000000000000000000000100000000000
PHI 10 0000000000000000000000000000000002000040800000040000000000000000000000000000000000000000000000000000040000000000000000000000000000000800000000000000000000000040000000000000000000000100000080000000000000000000100000000000000000000000000040000080000000012001000000000000800400080000001000000000000000000000400000000000000000000000000000000000000000000000000000000000000000010000000000000000000004000000
PHI 11 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 12 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
"""
PL = {}
for _ln in PLAN.strip().split("\n"):
    _t = _ln.split()
    if _t[0] in ("trial", "F1", "G1"): PL[_t[0]] = _t[1]
    elif _t[0] == "FG": PL[("FG", int(_t[1]))] = (_t[2], _t[3])
    elif _t[0] == "PHI": PL[("PHI", int(_t[1]))] = _t[2]
TRIAL = int(PL["trial"])            # constants of the generator's selected trial
KB = 10                            # bodies in the cycle of the generic rounds
REGTOP = 3525
ONES = REGTOP + 4                 # the all-ones register of the search state
NREG = REGTOP + 11
BLOCK_SHA256 = {"P.bin": ("a19d15483682b2c6b1168ab46770c36b6df595f6601e9117eab581534d2548d3", 4942), "B1.bin": ("c3a9216e6fe96074ae974509a5cad78dda78420eef509788c704ca552a2b05f7", 6618), "B2.bin": ("2cc3982d2b16bef22e0834bad1478aa72e12e4411cc0a9050f7d5b20929c50cf", 6634), "B3.bin": ("6cc7a678188b88fd02ccd6e5e41616cc53dda3541d77c17fc9b9cfa475fe7fb6", 6625), "B4.bin": ("df6ff2c93b1be7f0abedca4a23ec859cada69227825ce1fd6510f828a3229a1f", 6633), "B5.bin": ("56fbcbae544279c7e5dc5b4ca9096fa02eeea1b01e266bf39f2213bc51f9fb9e", 6624), "B6.bin": ("df30c150655696cca41d4e506f775fa5e286e60450740b421afca2fc1eec3c39", 6636), "B7.bin": ("5732f09627c6701fd42569718a19a673ceb4c0157431dbdf511a9131d8d4d5ff", 6642), "B8.bin": ("fad4af12cf3b656a94797d13a766ac5b390e2f24d899f6469bbd6aa9175edc9d", 6633), "B9.bin": ("b051abbd77b8fe91d30cefbc68a47bca4bf25e2aeba00e8c968a65702bfd82e3", 6633), "B10.bin": ("3925b3b3805d29c85796f72cd8cf149430057cc74ff48eb9dfc18bdbb5108afa", 6911), "E.bin": ("9f0549aa2376853cef5d5a7ef3a82b12f35fc7441b4f308529318a457ab708d7", 2479)}


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


def encode(prog):
    out = bytearray()
    for c, d, a, b in prog:
        out += (c | d << 3 | a << 15 | b << 27).to_bytes(5, "little")
    return bytes(out)


def flat_program(blk):
    """the executed stream of one step: P; for r = 2..NR-2 body (r - 2) mod KB + 1 and the iota of round r (plane (0, z) of
    the body's output bank XORed with the all-ones register for every set bit z of RC[r]); E"""
    prog = list(blk["P.bin"])
    for r in range(2, NR - 1):
        j = (r - 2) % KB + 1
        prog += blk["B%d.bin" % j]
        ob = YB if j % 2 else XB
        for z in range(64):
            if (RCA[r] >> z) & 1: prog.append((0, ob + z, ob + z, ONES))
    prog += blk["E.bin"]
    return prog



def compile_prog(prog):
    """The step, executed instruction by instruction (opcode 0 XOR, 1 AND, 2 OR, 3 NOT); R[ONES] holds the all-ones word."""
    P = tuple(prog)

    def step(R, A):
        R[ONES] = A
        for c, d, a, b in P:
            if c == 0: R[d] = R[a] ^ R[b]
            elif c == 1: R[d] = R[a] & R[b]
            elif c == 2: R[d] = R[a] | R[b]
            else: R[d] = R[a] ^ A
    return step


# ---------------- reference ----------------
def _perm_src():
    """Keccak-f rounds as straight Python source (theta, rho, pi, chi, iota per round; lanes a0..a24)."""
    L = ["def perm(a, rounds):", " " + ",".join("a%d" % i for i in range(25)) + " = a", " for rc in RCA[:rounds]:"]
    for x in range(5): L.append("  c%d = a%d ^ a%d ^ a%d ^ a%d ^ a%d" % (x, x, x + 5, x + 10, x + 15, x + 20))
    for x in range(5): L.append("  d%d = c%d ^ (((c%d << 1) | (c%d >> 63)) & M64)" % (x, (x + 4) % 5, (x + 1) % 5, (x + 1) % 5))
    for x in range(5):
        for y in range(5):
            r = ROT[x][y]; i = x + 5 * y; o = y + 5 * ((2 * x + 3 * y) % 5)
            L.append("  v = a%d ^ d%d; b%d = %s" % (i, x, o, "(((v << %d) | (v >> %d)) & M64)" % (r, 64 - r) if r else "v"))
    for y in range(5):
        for x in range(5):
            L.append("  a%d = b%d ^ (~b%d & b%d)" % (x + 5 * y, x + 5 * y, (x + 1) % 5 + 5 * y, (x + 2) % 5 + 5 * y))
    L.append("  a0 ^= rc")
    L.append(" a[:] = [" + ",".join("a%d" % i for i in range(25)) + "]")
    L.append(" return a")
    return "\n".join(L)


exec(compile(_perm_src(), "perm", "exec"))


def digest(msg, rounds=NR):
    blk = bytearray(136 * (len(msg) // 136 + 1)); blk[:len(msg)] = msg
    blk[len(msg)] ^= 6; blk[-1] ^= 0x80
    st = [0] * 25
    for o in range(0, len(blk), 136):
        for i in range(17): st[i] ^= int.from_bytes(blk[o + 8 * i:o + 8 * i + 8], "little")
        perm(st, rounds)
    return b"".join(st[i].to_bytes(8, "little") for i in range(4))


def msg_of(u):
    l = [KL[i] for i in range(16)]
    u0, u1, u2, u3 = [(u >> (64 * i)) & M64 for i in range(4)]
    l[1], l[6], l[11], l[4], l[9], l[14] = u0, u1, u0 ^ u1 ^ KL[11], u2, u3, u2 ^ u3 ^ KL[14]
    return b"".join(v.to_bytes(8, "little") for v in l)


def F_ref(u, PD):
    return int.from_bytes(digest(msg_of(u)), "little") ^ PD


# ---------------- setup and checks ----------------
def setup():
    for m in (b"", b"abc", bytes(135), bytes(200)):
        assert digest(m, 24) == hashlib.sha3_256(m).digest()
    blocks, PD = G4().build()
    for name, (h, n) in BLOCK_SHA256.items():
        assert len(blocks[name]) == n and hashlib.sha256(encode(blocks[name])).hexdigest() == h, name
    prog = flat_program(blocks)
    return compile_prog(prog), PD, len(prog)


def to_planes(points, T):
    """points[t][l] (256-bit) -> 256 planes with bit 256 t + l."""
    planes = [0] * 256
    for t in range(T):
        for l, u in enumerate(points[t]):
            g = 256 * t + l
            j = 0
            while u:
                if u & 1: planes[j] |= 1 << g
                u >>= 1; j += 1
    return planes


def lane_value(R, g, width=256):
    v = 0
    for j in range(width):
        v |= ((R[j] >> g) & 1) << j
    return v


def check_step(step, PD):
    import random
    rnd = random.Random(1)
    pts = [[rnd.getrandbits(256) for _ in range(256)]]
    R = [0] * NREG
    R[:256] = to_planes(pts, 1)
    A = (1 << 256) - 1
    cur = pts[0]
    for _ in range(2):
        step(R, A)
        cur = [F_ref(u, PD) for u in cur]
        for l in range(0, 256, 15):
            assert lane_value(R, l) == cur[l]


def shake(data, n):
    return hashlib.shake_256(data).digest(n)


# ---------------- rho-w22: the search of proof.md Section 4 at width W ----------------
W, H, DK, DTT, LC, U, TB = 22, 4, 3, 5, 256, 3000, 400      # a DP: bits 0..3 zero and bits 4..6, as a number, < 5; replay cap LC; no trail is cut


def rho_w(trials, step, PD):
    T = len(trials)
    A = (1 << (256 * T)) - 1
    mask = (1 << W) - 1
    R = [0] * NREG
    seeds = [bytes.fromhex(t["seed"]) for t in trials]
    rho, nid, att, astart = [0] * T, [0] * T, [-1] * T, [0] * T
    table = [dict() for _ in range(T)]
    done = [None] * T
    obs = [dict(steps=0, trails=0, attempts=0, stored=0, replay_evals=0) for _ in range(T)]
    lid, lst = [0] * (256 * T), [0] * (256 * T)
    pend = []

    def f_small(u):
        return F_ref(u, PD) & mask

    def is_dp(x):
        return x & ((1 << H) - 1) == 0 and (x >> H) & ((1 << DK) - 1) < DTT

    def new_attempt(t, c):
        att[t] += 1; obs[t]['attempts'] += 1
        rho[t] = int.from_bytes(shake(seeds[t] + att[t].to_bytes(4, 'little'), 8), 'little') & mask
        table[t].clear(); nid[t] = 256; astart[t] = c
        for l in range(256):
            g = 256 * t + l
            lid[g] = l; lst[g] = c
            pend.append((g, (rho[t] + l) & mask))
        obs[t]['trails'] += 256

    def apply_pending():
        if not pend: return
        clr = 0
        for g, _ in pend: clr |= 1 << g
        for j in range(W):
            st = 0
            for g, x in pend:
                if (x >> j) & 1: st |= 1 << g
            R[j] = (R[j] & ~clr & A) | st
        del pend[:]

    def replay(sa, sb, lb, t):
        if lb > LC: return None                        # the new trail is longer than the cap
        a, la = sa, 0                                  # la: evaluations of the stored trail from its start to its DP
        while True:
            a = f_small(a); la += 1
            if is_dp(a) or la >= LC: break
        obs[t]['replay_evals'] += la
        if not is_dp(a): return None
        a, b = sa, sb
        for _ in range(abs(la - lb)):
            if la > lb: a = f_small(a)
            else: b = f_small(b)
        obs[t]['replay_evals'] += abs(la - lb)
        if a == b: return None
        for _ in range(min(la, lb) + 1):
            na, nb = f_small(a), f_small(b)
            obs[t]['replay_evals'] += 2
            if na == nb: return a, b
            a, b = na, nb
        return None

    for t in range(T): new_attempt(t, 0)
    apply_pending()
    c = 0
    while any(d is None for d in done):
        c += 1
        if c > 4000: raise RuntimeError("no pair")
        step(R, A)
        for j in range(W, 256): R[j] = 0               # width reduction (this experiment only)
        anyv = 0
        for j in range(H): anyv |= R[j]
        dpm = A ^ anyv                                  # walks with the low H bits zero
        eq, lt = dpm, 0                                 # then the DK bits above them, as a number, < DTT (bit-parallel, most significant first)
        for i in range(DK):
            p = R[H + DK - 1 - i]
            if (DTT >> (DK - 1 - i)) & 1: lt |= eq & (A ^ p); eq &= p
            else: eq &= A ^ p
        dpm = lt
        img = [R[j].to_bytes(32 * T, "little") for j in range(W)]          # byte image of the planes 0..W-1 of this step
        events = []
        while dpm:
            low = dpm & -dpm
            events.append(low.bit_length() - 1)
            dpm ^= low
        seen, fresh = set(), set()
        for g in events:
            t = g >> 8
            if g in seen or done[t] is not None or t in fresh: continue
            seen.add(g)
            x = sum(((img[j][g >> 3] >> (g & 7)) & 1) << j for j in range(W))
            ln = c - lst[g]
            tb = table[t]
            if x in tb:
                ida = tb[x]
                if ida != lid[g]:
                    r = replay((rho[t] + ida) & mask, (rho[t] + lid[g]) & mask, ln, t)
                    if r is not None:
                        done[t] = r; obs[t]['steps'] = c - astart[t]; obs[t]['stored'] = len(tb)
                        continue
            else:
                tb[x] = lid[g]
            if nid[t] >= U:
                new_attempt(t, c); fresh.add(t); continue
            i = nid[t]; nid[t] += 1; obs[t]['trails'] += 1
            lid[g] = i; lst[g] = c
            pend.append((g, (rho[t] + i) & mask))
        for t in range(T):
            if done[t] is None and c - astart[t] >= TB: new_attempt(t, c)
        apply_pending()
    return done, obs


# ---------------- proj-w256: chained full-width steps, 22-bit agreement ----------------
def proj_w(trials, step, PD, steps=8, bits=22):
    T = len(trials)
    A = (1 << (256 * T)) - 1
    pts = []
    for tr in trials:
        raw = shake(bytes.fromhex(tr["seed"]) + b"proj", 32 * 256)
        pts.append([int.from_bytes(raw[32 * l:32 * l + 32], "little") for l in range(256)])
    R = [0] * NREG
    R[:256] = to_planes(pts, T)
    from array import array
    allkeys = []                            # allkeys[s][g]: the 22 low image bits of lane g at step s

    def point(t, l, s):                     # input of step s on lane l (reference chain from the start point)
        u = pts[t][l]
        for _ in range(s): u = F_ref(u, PD)
        return u

    for s in range(steps):
        step(R, A)
        cols = [bin(R[j] | (1 << (256 * T)))[:2:-1] for j in range(bits)]   # bit g of plane j = cols[j][g]
        allkeys.append(array("I", (int("".join(c[g] for c in reversed(cols)), 2) for g in range(256 * T))))
        del cols
    done = [None] * T
    for t in range(T):
        st = {}
        for s in range(steps):
            ks = allkeys[s]
            for l in range(256):
                key = ks[256 * t + l]
                o = st.get(key)
                if o is None:
                    st[key] = (l, s)
                else:
                    a, b = point(t, o[0], o[1]), point(t, l, s)
                    if a != b:
                        done[t] = (a, b, s); break
            if done[t] is not None: break
    return done


def main():
    step, PD, nins = setup()
    check_step(step, PD)
    req = json.load(sys.stdin)
    if req["schema_version"] != 1 or req["target_profile"] != "sha3-256-r%d-prefix-v1" % NR:
        raise ValueError("unexpected organizer target")
    mask = ((1 << 22) - 1).to_bytes(32, "little")
    if req["event"] != {"kind": "digest-xor-mask", "mask_hex": mask.hex(), "expected_hex": "00" * 32}:
        raise ValueError("unexpected organizer event")
    trials = req["trials"]
    out = []
    if req["experiment_id"] == "rho-w22":
        done, obs = rho_w(trials, step, PD)
        for t, tr in enumerate(trials):
            a, b = done[t]
            ma, mb = msg_of(a), msg_of(b)
            assert ma != mb and (int.from_bytes(digest(ma), "little") ^ int.from_bytes(digest(mb), "little")) & ((1 << W) - 1) == 0
            out.append({"trial": tr["trial"], "message_a_hex": ma.hex(), "message_b_hex": mb.hex(), "observations": obs[t]})
    elif req["experiment_id"] == "proj-w256":
        done = proj_w(trials, step, PD)
        for t, tr in enumerate(trials):
            if done[t] is None:
                out.append({"trial": tr["trial"], "message_a_hex": None, "message_b_hex": None})
            else:
                a, b, s = done[t]
                out.append({"trial": tr["trial"], "message_a_hex": msg_of(a).hex(), "message_b_hex": msg_of(b).hex(), "observations": {"step": s}})
    else:
        raise ValueError("unknown experiment")
    json.dump({"schema_version": 1, "trials": out}, sys.stdout, separators=(",", ":"), sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
