"""LS1: distinguished-point collision search on sha3-256-r20-prefix-v1 with a linear-structure message embedding.

Chain function on 256-bit points u (little-endian lanes u0..u3):
  m(u) = 128 bytes = lanes 0..15 of the absorbed state: lane 1 = u0, lane 6 = u1, lane 11 = u0^u1^K11,
  lane 4 = u2, lane 9 = u3, lane 14 = u2^u3^K14, the other lanes 0..15 the constants K below; padding gives lane 16 =
  0x8000000000000006.  F(u) = SHA3-256-r20(m(u)) XOR PD (PD a fixed 256-bit mask).  m is injective, so F(u) = F(u') with
  u != u' gives two distinct messages with equal complete digests.
This program regenerates the bit-sliced straight line of proof.md Section 3 (the same algorithm and node order as the C
generator gen3.c, with the generator's decisions PLAN: constants trial, round-1 and theta complements, free term
polarities; its 5-byte encoding must hash to PROG_SHA256), checks it against a plain 20-round implementation, and runs
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
NR = 20                         # rounds of the target
PLAN = """
trial 192
nr 20 optmode 3 trick 1 lasttrick 1 notfold 0
F1 420c12006c81a00281008802004001012004888218245a40000000a1011002000010100081118000
G1 00800000000008200000002000000480008000002000200020000000000000000000000400000010
FG 2 0000000a0e5100000804008018200000430a40000448100080103502004008040442048004042008 00c0c40300840000000080020008040000000404900c04800009000201000080004b202041000100
FG 3 001e0100c84a000410500082010002808003008838000800a401292a000100210040002160010080 044d0061441010102040010200021802018042140000408000200510000000120801480064300408
FG 4 0004201102004002208601000421221005000084c000800020086000082200200428000801000080 800085410200400022000011310202055100080080002208481e2000140a08200091081000804208
FG 5 000410010e0000018000000020800024600008004040001001084890000102000040000001010080 4610580202508000010400000000620a40034004200416a1020008001a138420029303024a022062
FG 6 410020480000802504c000411008000080220402010300100400800044000c002120464000100100 00004110020180140110000010000000010000008008000022020022608c00222000210200200012
FG 7 80000010014002036000820504000120200021004000001280201400480108018414c11200208100 07110010004132040a52000040880800020202842542b21010400008000401c41c03440408080040
FG 8 890402420880000800024c100000087100b00900008840000500001010a010000011211080001005 4600012080000001a00024826420000020040812208e2280000118000400a25020084010440a8000
FG 9 50580008700200002c202000020002020800211004200b246009012000002000e0140008000000a0 00430c001041008586400a69880a204088002405002808982008000488244200010000001c21a000
FG 10 14000200002401a08420208041240000000000024025180000a0c00000902c001220280264458809 000500080000000040404c11080000200104001003280130a10480a0408021100808800800804001
FG 11 10010030024000011000050000042000007060080100418100010049201000400002100002110000 00a000050004810012081400c248022c000508000222418410010010040020010000560000010086
FG 12 90200000021901006408080400114000d002210000004102002000c0204001048000a05035004020 000001000460004100058080084010040102200100010000022000010008404449e100000c800034
FG 13 002104400000000801080044000300080000000401000044090883000a40100480200048d2204c00 88038880412040240021000180128108a2802000100005002008802000029144a000419990005060
FG 14 00040c09200a0a0a104000a400012202451808488b008c0000010100180008000221000122190082 01824202084011508160401193a00010008042802048604010400840000080090008000088108004
FG 15 09240080024030400000c000f0000806008090800041001000088080402029403200000800041800 00100300010021001800003008012000218100120020201800801000a24280e512c8800280008014
FG 16 00110000224340028000a201280000402b0100400040800400040040002000088008018182040140 000058020c2030001200018801120048044010140041304010100848294100081800048000040404
FG 17 008010600020020103040060020200414c8010200040002000240800001000402250044408000020 008081000000e0000006210801c2201090411104a0420300010100022000018021088800a100a040
FG 18 101010080000018000010c4020000040000100411200000511001001022002000000011010040200 900a22084100224480201300404c07000008014040225822004c100100022c140542000002004024
FG 19 00000000000000000000000000000000000000000000000000008000000000040000000200000000 80000200804801014400800000000028000800000400008000002004002200001000800444060000
PHI 0 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 1 0000000000000000000808000000000000010000000000040000000000000080100000000000000000000000000004008000000000000000008000000000000000000000000000000000000000000000000000000000000000020000000000080000000004100000000000000000000000000000000200000000000000000100000000010000000000040000000000000000008000800000100000000000000000000000000000000000000000100100800000000000000000200000000000200000000000000000
PHI 2 0000000000000000000005400000000000000000000000000040000000000000000000000000000000600000000000200000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000800000000000000000000000000000000000002000000000000040000000000000080000000000200090000000000000000004000001008000000000004000001000000000000001000000000000000000000018000000008000000000120000000200000000000000
PHI 3 0000000000000000040804000000000000000000000008000000000000000200000020000000000000000000000000000000000000200000000000020000000000000000000000000020000000000000000000000000000000000000000000020000000000000100000000000000000000008000000200000000004000000000000001000000008001000000000000000000400000000000000200000000000000000208000000000000000080004018000000000000000000000000000020000000000000040000
PHI 4 0000000000000000000000000800000000000080000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000004000000000000200000800000000000000000000000000000000000000280000000000000000000000000040001000010000000000000000000000001000080000000000000000000000000000000000000100000000040000000000000002000000000000000000040000000002000800000000000000000000400000000000000000000000
PHI 5 0000000800000000800000000004000000000200000000000000000000000080000000000000000000800000000000000000000000000000020000000000000000000000000000101000000100000000000000000000000000000000000000000000000000000002000000001000000000000000080000000200000000000000000000000020000000000000000000000000002002000000000000000000040000000000000000000000202000100000000000000100000000000040000000000000000000000000
PHI 6 000000000000008000002000000000000010010000000000800000100000000000000000000000000000000000000000000000004040000040c000000000400000000000000000000000000000000000000000000000400000004000000000000000002010000000000000000000000000000000000000000000000200000000000004000000002008000000000000000000000000000100000000000000000000000000000000000a00000000000000000000000000000000000000000001000000000400000000
PHI 7 0000000000000000000100000000000000000020000000101000000000000400000000004800000001000000000804000400000000000000000000000000000000001000000000000000000000000002000000000000000000000000004000000000000000000000008004000000000000000000000000000000000000000000010000000000000008020000804000000000004000000000000000000000000002000000020000000008008000000000000000008000000000000000000000000000000000000460
PHI 8 0000000000000000000000000000000000000000000000000000008000000004000008000000000000000000000000000000000000080000000000200000040000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000000000000000000000000004000008000000000000000000000000000000000000000000000000000000000000000000000008000000001000404000000000008000000000000000000000000040000000000100000000000
PHI 9 0000000000800000000080000000000000000000400002000000000000020000000000000000000800000000000000010000800000000000000000008000000000000100000008000000000000010000000000000000000001000000000000000000000000000044000000000000000000000000400000000400800000000000800000000000000000000000000000000000000000000002000000080000000000200000000000000000000000001000000200000000000808100000040000000000000200000000
PHI 10 0000100040000000000000000000000000000002000000000048000000000000000100000040400000000000000001000000000090000000000000000000000001000000000000000004800020000000000000000000000000000000000000000040100000000000000000000000000000000100000000000000002004000000000000000000000000002000000000000000000002400000000001000000000000000800000000800800000000000000000000000010000000000000000000000000000002000000
PHI 11 0200000014000000000000000000000000000000000800001000100000000000000200010100000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000028000008200000000000001000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000800000000004000000000000004000000000
PHI 12 0000000000000000000000000010000000008000020000000010000000000000000000000000040000000000000000000000000000000000000000000000000000000000400000000000000000000000000000800000000000000000000000000000000000020000000000000000000000000000000000000000020000000000000000000000100010000000000001000000000000000000000000000040000000000000000000000040000000000040400000000800000000100000000000000000000000008000
PHI 13 20040000000000000000000000000000000000000000000000000000000000004000000000000000000010010000000000040000000000000000000000000000c0000000001000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000030000008000000000000000000000000040000100000000020000000000010400000000000000000000000000000000000000008000000000000000000100080000000100000000000000000000008000000000000
PHI 14 0001000000000000000000100000010020000000000000000000000000000000000000000000000000000000000000000000000000010000000820000000000000000000000000000000000000000000000000100000000000000000000000000000004000000000000001000000000000000000000000000000000000000000040000000000000000400000000000000000000000000040000000000000000000000000000000000000000000000000000000000028000000220000008000100000010000000000
PHI 15 0000000000000080000000000000000000000000000000002000010000000000000000000000000000000000000000000000000002000000000000001000000000000000000000a00000000000000000940000000020000000220000000000000000000000000000000008000800000000000000000000000000000002002000002000000000000400000800000000000000000000000000000000000000000000000000000000000000000000000000080000000100000000000000000000000000400000000000
PHI 16 0000000000000000000000000000000000000001000400000000000000000000000080000000000004000800000000000000000000000000200000000000800000000000004000000000000000000000000200400000000010000000000000000000000000000002000004000000000000008000000000000000000000000100000000000000000000000000000080000000000000000000020000000000000000000000010000000000000100000000000000000000080000001000400400000000800000000000
PHI 17 0000000002000000000000010000080000000000000000000000000000000000000000800000000000000000000000100000000000004000000000080000000000000000000000000000000000000080004000000000000000000000000000000000000000000000100000000000000000000000080000000000000080000000000000000000000008000000000000000000000000000000000000000000000000000000002000000000000000000008000000000000040000000000000000010000000004000000
PHI 18 0000000000000000000000000000000000000000000000000600000000000000000000401000000000000800000000000000000000800000000010000000000000000000000000000000002000000000001001000000000000000000000000000000000000000020400800000000001000000000000000000000000000000000000000000000000000800010080000000200000000000000000000000000100004000000000000000000000000000000000040000000000000000000000000000000000000000040
PHI 19 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
"""
PL = {}
for _ln in PLAN.strip().split("\n"):
    _t = _ln.split()
    if _t[0] in ("trial", "F1", "G1"): PL[_t[0]] = _t[1]
    elif _t[0] == "FG": PL[("FG", int(_t[1]))] = (_t[2], _t[3])
    elif _t[0] == "PHI": PL[("PHI", int(_t[1]))] = _t[2]
TRIAL = int(PL["trial"])            # constants of the generator's selected trial
PROG_SHA256 = "c03cd324f688d0cb50f5b580ae1558db57322f87c0c1acd18519fe084aa87b00"
NINSTR = 120245
NREG = 2304
NC = -1
O_IN, O_XOR, O_AND, O_OR, O_NOT = 0, 1, 2, 3, 4


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


# ---------------- generator (same algorithm and node order as gen.c) ----------------
class Gen:
    def __init__(self):
        self.op, self.a, self.b, self.k, self.lin = [], [], [], [], []
        self.form, self.fidx, self.cons = [], {}, {}

    def new(self, op, a, b):
        self.op.append(op); self.a.append(a); self.b.append(b); self.k.append(0); self.lin.append(-1)
        return len(self.op) - 1

    def consn(self, op, a, b):
        if op != O_NOT and a > b: a, b = b, a
        key = (op, a, b)
        n = self.cons.get(key)
        if n is None:
            n = self.new(op, a, b); self.cons[key] = n
        return n

    def fadd(self, m, node):
        f = len(self.form); self.form.append((m, node)); self.fidx[m] = f
        return f

    def xorv(self, a, b):
        if a[0] == NC: return (b[0], b[1] ^ a[1])
        if b[0] == NC: return (a[0], a[1] ^ b[1])
        if a[0] == b[0]: return (NC, a[1] ^ b[1])
        la, lb = self.lin[a[0]], self.lin[b[0]]
        if la >= 0 and lb >= 0:
            m = self.form[la][0] ^ self.form[lb][0]
            kk = self.k[a[0]] ^ self.k[b[0]]
            if m == 0: return (NC, kk ^ a[1] ^ b[1])
            f = self.fidx.get(m)
            if f is not None:
                n3 = self.form[f][1]
                return (n3, kk ^ a[1] ^ b[1] ^ self.k[n3])
            n = self.new(O_XOR, min(a[0], b[0]), max(a[0], b[0]))
            self.k[n] = kk; self.lin[n] = self.fadd(m, n)
            return (n, a[1] ^ b[1])
        return (self.consn(O_XOR, a[0], b[0]), a[1] ^ b[1])

    def notv(self, a):
        if a[0] == NC: return a
        before = len(self.op)
        n = self.consn(O_NOT, a[0], 0)
        if len(self.op) > before and self.lin[a[0]] >= 0:
            self.lin[n] = self.lin[a[0]]; self.k[n] = self.k[a[0]] ^ 1
        return (n, a[1] ^ 1)

    def and2(self, a, b, sel=0):
        """logical a AND b; a mixed-polarity term is A ^ (A & B) (polarity 0) or, with sel, (NOT A) | B (polarity 1)"""
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


def cost_term(b1, b2):
    if b1[0] == NC or b2[0] == NC or b1[0] == b2[0]: return 0
    return 1 if (b1[1] ^ 1) == b2[1] else 2


def row_choose(b, need):
    """the row decision of gen3.c: complement subset s and 10-gate position j (-1: none), first cheapest"""
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
                        else: c += 1                                   # mixed term k: its output polarity is free
                    else: c += cost_term(bb[(X + 1) % 5], bb[(X + 2) % 5])
            if c < bc: bc, best, bj = c, s, j
    return best, bj


TAB = {}
for _L in (0, 1):
    for _p in range(32):
        TAB[(_L, _p)] = row_choose([(X, (_p >> X) & 1) for X in range(5)], 0x0F if _L else 0x1F)


def bits(h, n):
    v = int.from_bytes(bytes.fromhex(h), "little")
    return [(v >> i) & 1 for i in range(n)]


def build():
    g = Gen()
    for j in range(256):
        n = g.new(O_IN, 0, 0); g.lin[n] = g.fadd(1 << j, n)
    S = [[(NC, (KL[l] >> z) & 1) for z in range(64)] for l in range(25)]
    for z in range(64):
        S[1][z] = (z, (KL[1] >> z) & 1); S[6][z] = (64 + z, (KL[6] >> z) & 1)
        S[4][z] = (128 + z, (KL[4] >> z) & 1); S[9][z] = (192 + z, (KL[9] >> z) & 1)
    for z in range(64):
        S[11][z] = g.xorv(g.xorv((z, 0), (64 + z, 0)), (NC, (KL[11] >> z) & 1))
        S[14][z] = g.xorv(g.xorv((128 + z, 0), (192 + z, 0)), (NC, (KL[14] >> z) & 1))
    for r in range(NR):
        last = r == NR - 1
        if r == 1: ff, gg = bits(PL["F1"], 320), bits(PL["G1"], 320)
        elif r >= 2: ff, gg = bits(PL[("FG", r)][0], 320), bits(PL[("FG", r)][1], 320)
        else: ff = gg = [0] * 320
        phi = bits(PL[("PHI", r)], 1600)
        C = [[None] * 64 for _ in range(5)]
        D_ = [[None] * 64 for _ in range(5)]
        for x in range(5):
            s = S[x][63]
            for y in range(1, 5): s = g.xorv(s, S[x + 5 * y][63])
            C[x][63] = g.notv(s) if gg[x * 64 + 63] else s
        for z in range(64):
            if z < 63:
                for x in range(5):
                    s = S[x][z]
                    for y in range(1, 5): s = g.xorv(s, S[x + 5 * y][z])
                    C[x][z] = g.notv(s) if gg[x * 64 + z] else s
            for x in range(5):
                D_[x][z] = g.xorv(C[(x + 4) % 5][z], C[(x + 1) % 5][(z + 63) & 63])
                if ff[x * 64 + z]: D_[x][z] = g.notv(D_[x][z])
        NS = [row[:] for row in S]
        nY, need = (1, 0x0F) if last else (5, 0x1F)
        for Y in range(nY):
            for z in range(64):
                b = []
                for X in range(5):
                    y, x = X, (3 * Y + X) % 5
                    zz = (z - ROT[x][y]) & 63
                    b.append(g.xorv(S[x + 5 * y][zz], D_[x][zz]))
                if all(v[0] != NC for v in b) and len(set(v[0] for v in b)) == 5:
                    best, bj = TAB[(int(last), sum(v[1] << X for X, v in enumerate(b)))]
                else:
                    best, bj = row_choose(b, need)
                for X in range(5):
                    if best >> X & 1: b[X] = g.notv(b[X])
                k = (bj + 1) % 5
                if bj >= 0:                                          # 10-gate row: output bj reads output k
                    p1, p2 = b[(k + 1) % 5], b[(k + 2) % 5]
                    sel = ((b[(bj + 2) % 5][1] ^ 1) ^ b[k][1]) if (p1[1] ^ 1) != p2[1] else 0
                    NS[k + 5 * Y][z] = g.xorv(b[k], g.and2((p1[0], p1[1] ^ 1), p2, sel))
                for X in range(5):
                    if need >> X & 1:
                        if bj >= 0 and X == k: continue
                        t1 = NS[k + 5 * Y][z] if X == bj else b[(X + 1) % 5]     # not y and z == not chi_y and z
                        t = g.and2((t1[0], t1[1] ^ 1), b[(X + 2) % 5], phi[(X + 5 * Y) * 64 + z])
                        NS[X + 5 * Y][z] = g.xorv(b[X], t)
        for z in range(64):
            NS[0][z] = (NS[0][z][0], NS[0][z][1] ^ ((RCA[r] >> z) & 1))
        S = NS
    out = [S[j >> 6][j & 63] for j in range(256)]
    PD = 0
    for j, v in enumerate(out):
        assert v[0] != NC and v[0] >= 256
        PD |= v[1] << j
    return g, [v[0] for v in out], PD


def allocate(g, outn):
    nn = len(g.op)
    live = [False] * nn
    for n in outn: live[n] = True
    for i in range(nn - 1, 255, -1):
        if live[i]:
            live[g.a[i]] = True
            if g.op[i] != O_NOT: live[g.b[i]] = True
    last = [0] * nn
    for i in range(256, nn):
        if live[i]:
            last[g.a[i]] = i
            if g.op[i] != O_NOT: last[g.b[i]] = i
    outj = {}
    for j, n in enumerate(outn): last[n] = 0xFFFF; outj[n] = j
    outdef = list(outn)
    reg = [0] * nn
    busy = [False] * NREG
    free = list(range(NREG - 1, 255, -1))
    for j in range(256):
        reg[j] = j
        if last[j]: busy[j] = True
    code, prog, peak = {O_XOR: 0, O_AND: 1, O_OR: 2, O_NOT: 3}, [], 0
    for i in range(256, nn):
        if not live[i]: continue
        op, a = g.op[i], g.a[i]
        b = a if op == O_NOT else g.b[i]
        for k, o in enumerate((a, b)):
            if k == 1 and o == a: break
            if last[o] == i:
                r = reg[o]; busy[r] = False
                if r >= 256: free.append(r)
        if i in outj:
            d = outj[i]; assert not busy[d]
        elif free:
            d = free.pop()
        else:
            d = next(r for r in range(256) if not busy[r] and outdef[r] >= last[i])
        busy[d] = True; reg[i] = d; peak = max(peak, d + 1)
        prog.append((code[op], d, reg[a], 0 if op == O_NOT else reg[g.b[i]]))
    return prog, peak


def encode(prog):
    out = bytearray()
    for c, d, a, b in prog:
        out += (c | d << 3 | a << 15 | b << 27).to_bytes(5, "little")
    return bytes(out)


def compile_prog(prog):
    """The straight line, executed instruction by instruction (opcode 0 XOR, 1 AND, 2 OR, 3 NOT)."""
    P = tuple(prog)

    def step(R, A):
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
    g, outn, PD = build()
    prog, peak = allocate(g, outn)
    assert hashlib.sha256(encode(prog)).hexdigest() == PROG_SHA256 and len(prog) == NINSTR and peak <= NREG
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
W, H, LC, U, TB = 22, 4, 128, 3000, 400


def rho_w(trials, step, PD):
    T = len(trials)
    A = (1 << (256 * T)) - 1
    mask = (1 << W) - 1
    R = [0] * NREG
    seeds = [bytes.fromhex(t["seed"]) for t in trials]
    rho, nid, att, astart = [0] * T, [0] * T, [-1] * T, [0] * T
    table = [dict() for _ in range(T)]
    done = [None] * T
    obs = [dict(steps=0, trails=0, dead=0, attempts=0, stored=0, replay_evals=0) for _ in range(T)]
    lid, lst = [0] * (256 * T), [0] * (256 * T)
    due, pend = {}, []

    def f_small(u):
        return F_ref(u, PD) & mask

    def new_attempt(t, c):
        att[t] += 1; obs[t]['attempts'] += 1
        rho[t] = int.from_bytes(shake(seeds[t] + att[t].to_bytes(4, 'little'), 8), 'little') & mask
        table[t].clear(); nid[t] = 256; astart[t] = c
        for l in range(256):
            g = 256 * t + l
            lid[g] = l; lst[g] = c
            due.setdefault(c + LC, []).append((g, l, att[t]))
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
        a, la = sa, 0                                  # la: evaluations of the stored trail from its start to its DP
        while True:
            a = f_small(a); la += 1
            if a & ((1 << H) - 1) == 0 or la >= LC: break
        obs[t]['replay_evals'] += la
        if a & ((1 << H) - 1): return None
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
        dpm = A ^ anyv
        img = [R[j].to_bytes(32 * T, "little") for j in range(W)]          # byte image of the planes 0..W-1 of this step
        events = []
        while dpm:
            low = dpm & -dpm
            events.append((low.bit_length() - 1, 1))
            dpm ^= low
        for g, ident, at in due.pop(c, []):
            if lid[g] == ident and att[g >> 8] == at: events.append((g, 2))
        events.sort()
        seen, fresh = set(), set()
        for g, kind in events:
            t = g >> 8
            if g in seen or done[t] is not None or t in fresh: continue
            seen.add(g)
            if kind == 1:
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
            else:
                obs[t]['dead'] += 1
            if nid[t] >= U:
                new_attempt(t, c); fresh.add(t); continue
            i = nid[t]; nid[t] += 1; obs[t]['trails'] += 1
            lid[g] = i; lst[g] = c
            due.setdefault(c + LC, []).append((g, i, att[t]))
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
