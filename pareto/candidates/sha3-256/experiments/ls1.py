"""LS1: distinguished-point collision search on sha3-256-r11-prefix-v1 with a linear-structure message embedding.

Chain function on 256-bit points u (little-endian lanes u0..u3):
  m(u) = 128 bytes = lanes 0..15 of the absorbed state: lane 1 = u0, lane 6 = u1, lane 11 = u0^u1^K11,
  lane 4 = u2, lane 9 = u3, lane 14 = u2^u3^K14, the other lanes 0..15 the constants K below; padding gives lane 16 =
  0x8000000000000006.  F(u) = SHA3-256-r11(m(u)) XOR PD (PD a fixed 256-bit mask).  m is injective, so F(u) = F(u') with
  u != u' gives two distinct messages with equal complete digests.
This program regenerates the bit-sliced straight line of proof.md Section 3 (the same algorithm and node order as the C
generator gen3.c, with the generator's decisions PLAN: constants trial (its values listed below), round-1 and theta complements, free term
polarities; its packed 39-bit encoding must hash to PROG_SHA256), checks it against a plain 11-round implementation, and runs
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
NR = 11                         # rounds of the target
PLAN = """
trial 1214
nr 11 optmode 4 trick 1 lasttrick 1 notfold 0
F1 184408014028241400080800040000d1000000800800104822100024003200000000000111000000
G1 00000000000000040120000000000000000000000000000000000000000000000000000000000000
FG 2 40a0020040080008422000040040210000004004001040001008100400042000000080c000908000 9840020404a1160008000002000088200204540000000430003642200020028a0030010000004352
FG 3 10000000000010008000000000000000020000040200400000000000000040000000800000104000 00004000002400000000000000000000000000000000000000000010000800000000000000000000
FG 4 20000000000000000000010040000400000040000000008020000000001000200040000000001000 00000000000000000000000046000000000000000000000000000000000000000000000088000000
FG 5 00000000002000040800000004000045000020104000080000000000000000000002008000000000 00000000000000000000010000000000000000000000002000000000000000000000000000000000
FG 6 00000000010000040000028000000000000000000010010000000010000020000000900808000010 00000000000000000000000008000100000000000000080000000000000000000000040000000100
FG 7 00000080000000000000020000000900040000000840000000a0a000000000000000000000000000 00000000000000000000004000000000000000000000000000004000000000000000000000000000
FG 8 00000000000000002000000000000004000010008000000000000040010000000000000000200000 00100000000000000000000000000000000000000000000000000800000000000000000000000000
FG 9 00000000002800022000200000000000000008000000001001000200000400000000000000800020 00000000000000000000000000000000040000000000000000100001000000080080000000000000
FG 10 00000000000000000000000000000000000000000000000000000000000000000000000000000000 00000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 0 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 1 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 2 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 3 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 4 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 5 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 6 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 7 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 8 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 9 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
PHI 10 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
DEC 2 8000100180004000a0006000800070006200a00080006000a00080006000a0008000600041008000400040005000a000040060008000200060008400000160006000900000004100300000012000a200a001200041004000a00025006000a50022007200000160006000880060000000a000a0004400200060008000a0008000a0008200200060000400610040000101a0000000400060006000800000004000a000a000a000800240004100600080008000200048008000a8004100a40020002800a800a40020004000b000a0000000a0004000200050004000400084008000410080007000610000018000a000000062008200a2004000a000b00040002000800020002000a000a0000800300000000001400001018000a001a4002100a8006000800082008a00a800400300008c000400a4004000200061004000a0000000a000a003200061000001a003000061006600420066004000a0006000380080004000200080008000080041006400a3002000200024006000000180002900810040008000800040000001600020008000400060008a00600060006000a0006000000141008000490060034000600080008800a00040006000400020000001400020004100200030000000a0008000800068000000840060038900000030008800a1002000800080002400a1004000200040002000800044002000a0000001800020006200900080002400200062006400a0002000400040003000000160008000440060004003a0004000a000200060002000a000640042006400a000400030006100490040012800400070008000860041001000300020006000a00020008400480042002100a0004000a0008000a10020000401600060010001400020006000
DEC 3 2100600010016000a0004000b800300040008000a000a400a00064006000a8002000a0006000820088004200a0000800a00040008800600084000201900060008000690020002000600040000000400020006000680020026300040004012000a00020008200800040006400600060006400a000a40060008400600042000401200380004100200244004000a000400060006000320028006100a0002000a800b40020006000a1004000a8004000680060002000a10040000200410001018000610040006000000124008000a000300082000001b00020002000a0002000400000002000400060002800880050003000a00044004100a1000000600020004000600020004000a000300044008200000140006400a00000008800a20040004400620020004000200040005000a000440080006100a00020002000280054004000400000014000b000a000400020007000a000a0004000400064006800810028004000620024006200a0002000b2000000a0004000220040000000a0004000a30080008000a000200080009000600082002000b000a000010144002000200020008000a8008800700088004100a0002800a000620070000000200048008400300040002000810080008800a000600000002000a0006000a00004006000a000a00080004000a200200001016200a000b40000012000a000480060004000a400a00024004000800040008800600040000001900080004000400088004000a00080008000400061008000040180002000a0006400600042006000a0009000a1008000a0006000a40080034000800060006000b00062006000a80060014200a000800062006000000060006000000184006000600020004000a800a1002000a400a000
DEC 4 60006100a000240030002100200000003000a000000162001001200062008000a80080004000820020004000a00060003000a80030006000000040008000600028008000400062006000240000013000000182008000600060002000400080004000b000200041002500200040006500400000017400600021002000a20020004000800080000001040170002000a100400020007000600040002000400080004200010020008400210080006000a00030002000620020002000800080004000a800400022004000b0000100a000200084002000000040008400400060006000200062008000610000002000600060002000a2008000a000800060000001300028000000400040004000400082008800000020008000a00081000000a0000001a000600041000000a00041002000600060008000a8002100000180002000000164008000300040006800200040002000b40060008200210020001000b0006200400020002000800080005000a1000001a200a00022006000840024008000200340006100800042008000600010003000a00084003000a000940020006200280020008000b000400020006100a20000004000440020018000400000008200600044002101400084008000a00044008000a0002000890060006001a400a0008000200068003000400060008200a00040000001400041004100a0009000a0004000600030004000a8006000a0006100a000a800800000000000410020004000a8004c0060002000600040008000700061005200200080004000000162008000a80020007000200060034c0040008000300040004000600028006400a00000014100a000410000016000620062004000a0002000200060006000b0008000a0004000
DEC 5 2000800000004200a400000080000000840088008000a0008000a000600020038000820000019000200080006800040130002000600060000001680024000000620040036000800080006000a200a400410082008000a000a800640080000401a000a0006100a40020002000200060002000810061002000a000a800320070003200400080006200a000400080000000a00084008000a800a003a000200160022000820000014000a40060008100a0004100a000200064004000680040003000a0002000400020016000000020004100080121002800880040008800a00020006000a000400040004800000080008000400080008200200022006000a0006000000168004200410040000001280080004000800020008100800040002800300000012200820020008000400090008000a00044008000400000012100840060003000a80010018000280064002000810062008000800040008000a000210049004800700048004100840040006000620062002000a00028008000a0002800a0003000000040008200410040016100a000220060008000420040004000a000600060003000a00042008000900084002000a000400062008000600020002400a400000040006000000060006200b000440082006200a00062008000a4006200a80020006000400020004000a000a000a000000164006000a200000001000000a0002000600040004000200030000001820040006000a2000001620062008000a000220062002200b00000002000680000006000200024004200a00040004000a0000001410082004200200040002000300040004000a800400064004c002000a800300040008400a0000000400041008400940041004000a000a000200040008400
DEC 6 a000080020008003400040008800a00062005000b00020004000300080006400a000600060008000600080006000400080008200040062006200a4002000600000016200a0000001800080004000400060008000a40080004000400062004000410060004000500060006400a400380060004000280040006400000120000000a800a0008400b0002000600028006000a000a0003800620080006000410040008000a0006000240020006400a00021008000a000080030006200a000a000500080028800000140000800620080008001400140000100620000002000a0000001a80042004100300080008000a000400080006000a0000401600022008000200060003000a0006000a0016200a0002000400040008000800040006000410040006000200040006000400060002800a00050006200400080004000b0002000100060003000a000a8008002a0008200300040000000400060000001a0008400620061003000400020000000b0004000240060002000400360000001a900410020008000000130004100a000a200a00062002400240161005100800040004100000090006000a0004100a80088006000800070006200800084000800a0008000200040002000810030004000a80062002000600078003000600020006100a00041008000800040000001040180004000ac0040006000800088004000210000014000b00100012002800020008000000020008000a800a000610020000800a000a000200080006000840080002000300020000000800029006100a400a000200060006000a800a000200060006000a00041008000a80042003000a000200080004000800060006000a0004000450040008000410040006300810061006000a0002000
DEC 7 22004000800060004100610080008800800030002000620080005200a00020006000200040006000500084000000800062008000a00040006000300040008000a000a00060008000880022006000a00020007000620020006400280020002000b0000000a0006100200080004000a000a00121006200a00040006000800064004000010020038400a8002000a400200040008400600040006a00200080004100a0003000400020002a003000a0002000900080036000b0004000a000220060007000000162002000a00060008000a000410001004400000140004000600080008100a002a0013000a00020000000b200a00161003000800044002000640020004000a000200020006000400040006000a800400080008000600060002000400060000101a800600128008000200060004000090050006000a0002000a0000000a000a000a800a0006100a2008002a00040007800a00021002000800000004000a0000001600040003000b8008000a00060002000400020030000820022008800a001a3001001000191002000300062002000800040006200400040008a000400a000a0006000800040006500a000500062002000a80001012000700000016000200060006003800020008000400000006000a0004000a800410060006200200060004000200120006800a800700020008000a00040004100410000002000480040008200400068004000000020004000000040002200a000600064004000200020003000800020003000a30080006000800028004000880084006000a2008100a4006000500060006000600008008000a00020004500b0000101600090000001610020006100a000a000600002000000a1006000210084008000200060004000
DEC 8 a0009000a00060008100a000300040008000000130006000200062006400610040006000280084006200840050008000a00080000100ac00a000a000a800a000210040002000a0004002610060002100400048004000800028008000400060006400000148001000a000600061006000a4002100a80026004000b000400082004800a000a000880060006800a000a00040001000200045006000800060004000a800610041002000a8005000200090004000600040002000200040000001800240004100a0008000200080006100620020002000000160003000a00040004000600040004000620060006000a0008000200048006000a0004000200080004800020061006000600040006000200070008400600020004100100150001001a400600030008000800020008000a000a8006000620020000001a00061002100a100800040004000a000000101012000a80060006000200040002000600000012003000080008000a50021016400a400a0008400a4006200a100610020005000410060002000610060004000200041004100b40080009000a4004000a00082004000410050000201a0003000a0004100610061006100a0008000600040004000a400a000620030002000a000600020008200600040002000410020006200000048003000a800600000004100840050008000a00000014000000060002100a00090004000720020008400800020004c00a0006000a0008000000040004000200008004000900000016000a0008000200080008400a000490080000200a80060004000a0008000b00050007200a000a000200080000001220020004000800080006000400020000001a0004001a00000015400a1008000a80020006100000040034001
DEC 9 4100a100000140001000a400a0036800200070006600480080008000200082004000a000400062004100a0008000a0006000200060008000500040008000300080002000500020004000600080006000410040003000a00021006000b2008a00400060038c0090004100400040006400800081004000a000a80044004400a00080004000300000000000a200a0002000a8002000880060006000a2004000200021004000b000410024008003600040002000a000a00080001001420041004200a00040006000a20062006000a000a000420062000200600080008000800020006000a000a000410001008800800060002100440020008400a00000015000200081002000840020004000200060004000b000a40020006000600061008100600030002000600081000800490020002000700040004000800000006000240002008400680062002000a000a00088002000400000016100b800a8004000a4008800400028005000400384006400a000200300000001a000300060003000a0004100a00080004100a00008008000280060006000800060003000b0008000210000012100a800200060006800800020008800a0016000800041002000a00080006800640060002100200065004100a8000200210040006400a20000004000410060004200000040006100800068004100200070002000800220002000800000012000a00060000000600080008100a80021008600a4002000a0000000640022008000640020004000a0004200a0001001a0004000a8006000600320000001400000013000a000810020006100a0006000800040006000200080002000a2005000840041006100200040002000600080008000880044006000a8004000410020006000
"""
PL = {}
for _ln in PLAN.strip().split("\n"):
    _t = _ln.split()
    if _t[0] in ("trial", "F1", "G1"): PL[_t[0]] = _t[1]
    elif _t[0] == "FG": PL[("FG", int(_t[1]))] = (_t[2], _t[3])
    elif _t[0] == "PHI": PL[("PHI", int(_t[1]))] = _t[2]
    elif _t[0] == "DEC": PL[("DEC", int(_t[1]))] = _t[2]
    elif _t[0] == "nr": PL["optmode"] = int(_t[3])
TRIAL = int(PL["trial"])            # constants of the generator's selected trial
PROG_SHA256 = "bfc207c1594ed6eb29c6c14fe4dc5de72fc9f233ba1b48371961fa3eb16f123c"
NINSTR = 59518
NREG = 2304
NC = -1
O_IN, O_XOR, O_AND, O_OR, O_NOT = 0, 1, 2, 3, 4


def consts(trial):
    """Constants of the generator's selected trial (structured set S3-04 of proof.md Section 2: the free lanes solve the
    704 round-0 chi neighbour conditions); the values are those gen3 sets for this trial, listed here."""
    K = [0] * 25
    K[16] = 0x8000000000000006
    for l, v in [(0, 0x0000000000000000), (2, 0xb8191f77d89d59d3), (3, 0x0000000000000000), (5, 0xffffffffffffffff), (7, 0x0000000000000000), (8, 0x0000000000000000), (10, 0xffffffffffffffff), (11, 0x6e0647ddf6275672), (12, 0x0000000000000000), (13, 0x770323eefb13ab3a), (14, 0x23f3704413b15316), (15, 0xffffffffffffffff)]: K[l] = v
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


def eval_sel(pat, s, j, mc):
    """the term polarities of a planned row (gen3.c eval_row): inputs of polarity pat, complement subset s, 10-gate position j"""
    bb = [((pat >> X) & 1) ^ ((s >> X) & 1) for X in range(5)]
    sel, ns, bit, k = [0] * 5, [0] * 5, 0, (j + 1) % 5
    for X in range(5):
        if X == j: continue
        a, b = bb[(X + 1) % 5] ^ 1, bb[(X + 2) % 5]
        if a == b: tp = a
        else: tp = (mc >> bit) & 1; bit += 1; sel[X] = tp
        ns[X] = bb[X] ^ tp
    if j >= 0:
        a, b = ns[k] ^ 1, bb[(j + 2) % 5]
        if a != b: sel[j] = (mc >> bit) & 1
    return sel


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
        dec = None
        if PL.get("optmode", 3) >= 4 and r >= 2 and not last and ("DEC", r) in PL:
            hb = bytes.fromhex(PL[("DEC", r)]); dec = [hb[2 * i] | hb[2 * i + 1] << 8 for i in range(320)]
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
                rsel = None
                if all(v[0] != NC for v in b) and len(set(v[0] for v in b)) == 5 and dec is not None:
                    dd = dec[Y * 64 + z]; best, bj = dd & 31, ((dd >> 5) & 7) - 1
                    rsel = eval_sel(sum(v[1] << X for X, v in enumerate(b)), best, bj, dd >> 8)
                elif all(v[0] != NC for v in b) and len(set(v[0] for v in b)) == 5:
                    best, bj = TAB[(int(last), sum(v[1] << X for X, v in enumerate(b)))]
                else:
                    best, bj = row_choose(b, need)
                for X in range(5):
                    if best >> X & 1: b[X] = g.notv(b[X])
                k = (bj + 1) % 5
                if bj >= 0:                                          # 10-gate row: output bj reads output k
                    p1, p2 = b[(k + 1) % 5], b[(k + 2) % 5]
                    sel = ((b[(bj + 2) % 5][1] ^ 1) ^ b[k][1]) if (p1[1] ^ 1) != p2[1] else 0
                    if rsel is not None: sel = rsel[k]
                    NS[k + 5 * Y][z] = g.xorv(b[k], g.and2((p1[0], p1[1] ^ 1), p2, sel))
                for X in range(5):
                    if need >> X & 1:
                        if bj >= 0 and X == k: continue
                        t1 = NS[k + 5 * Y][z] if X == bj else b[(X + 1) % 5]     # not y and z == not chi_y and z
                        t = g.and2((t1[0], t1[1] ^ 1), b[(X + 2) % 5], phi[(X + 5 * Y) * 64 + z] if rsel is None else rsel[X])
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
    out = bytearray(); acc = nb = 0                   # instruction i is bits 39 i .. 39 i + 38, little-endian, packed
    for c, d, a, b in prog:
        acc |= (c | d << 3 | a << 15 | b << 27) << nb; nb += 39
        while nb >= 8: out.append(acc & 255); acc >>= 8; nb -= 8
    if nb: out.append(acc)
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
