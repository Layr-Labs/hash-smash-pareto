"""LS1, design X: distinguished-point collision search on sha3-256-r21-prefix-v1 with the design-X message embedding.

Chain function on 256-bit points u (little-endian lanes u0..u3), proof.md Section 2:
  v_x = u_x (x < 4), v_4 = XOR_(x<4) rotr(u_x, (ROT[4][2] - ROT[x][2]) mod 64);
  m(u) = 128 bytes = lanes 0..15 of the absorbed state: lane x = v_x ^ K_x, lane 10 + x = v_x ^ K_(10+x) (x = 0..4),
  lanes 5..9 all-ones, lane 15 zero; padding gives lane 16 = 0x8000000000000006.  F(u) = SHA3-256-r21(m(u)) XOR PD
  (PD a fixed 256-bit mask).  m is injective, so F(u) = F(u') with u != u' gives two distinct messages with equal digests.
This program regenerates the bit-sliced straight line of proof.md Section 3 (the same algorithm and node order as the C
generator gen4.c, with the generator's decisions PLAN: constants trial, round-1 and theta complements, the row decisions;
its packed two-address encoding must hash to PROG_SHA256), checks it against a plain implementation, and runs
  rho-w22   : the search of proof.md Section 4 at width 22 (planes 22..255 zeroed after each step), one pair per trial;
              the table keeps the trail number of each end; the replay measures the stored trail by walking it,
              keeping every GCK-th point as a checkpoint, walks the new trail once and lock-steps one segment;
  proj-w256 : eight chained full-width steps from 256 random points, first pair agreeing on the 22 low digest bits.
One Python integer holds a plane for all trials of the request (trial t in bits 256t..256t+255); trials never interact.
This is ls1.py of entry a767dfcf (Jbenisek) with the design-X embedding (consts, build, msg_of) and the rows with one
constant input (eval_selk).
"""
import sys, json, hashlib, heapq, base64, zlib

M64 = (1 << 64) - 1
RCA = [0x1, 0x8082, 0x800000000000808A, 0x8000000080008000, 0x808B, 0x80000001, 0x8000000080008081, 0x8000000000008009,
       0x8A, 0x88, 0x80008009, 0x8000000A, 0x8000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
       0x8000000000008002, 0x8000000000000080, 0x800A, 0x800000008000000A, 0x8000000080008081, 0x8000000000008080,
       0x80000001, 0x8000000080008008]
ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
NR = 21                         # rounds of the target
PLANZ = """
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
OBkZHGdvThEbiyAXyaB43tHyqkDxvwCdxuB2
"""
PLAN = zlib.decompress(base64.b64decode("".join(PLANZ.split()))).decode()   # the plan text (plan.txt with its bit fields in base64), zlib-compressed

PL = {}
_d = lambda t: base64.b64decode(t).hex()   # the bit fields of PLAN are stored in base64 (plan.txt holds them in hex)
for _ln in PLAN.strip().split("\n"):
    _t = _ln.split()
    if _t[0] == "trial": PL[_t[0]] = _t[1]
    elif _t[0] in ("F1", "G1"): PL[_t[0]] = _d(_t[1])
    elif _t[0] == "FG": PL[("FG", int(_t[1]))] = (_d(_t[2]), _d(_t[3]))
    elif _t[0] == "PHI": PL[("PHI", int(_t[1]))] = _d(_t[2])
    elif _t[0] == "DEC": PL[("DEC", int(_t[1]))] = _d(_t[2])
    elif _t[0] == "DECE": PL[("DECE", int(_t[1]))] = _d(_t[2])
    elif _t[0] == "nr": PL["optmode"] = int(_t[3])
TRIAL = int(PL["trial"])            # constants of the generator's selected trial
PROG_SHA256 = "48b51f9c40510849e7cb9189b939228c53b1ffd8a32bf7377b3632044a6085e8"
NINSTR = 123396
NREG = 2304
B35 = {}                            # LRS: first node of the last round; DIAG: lanes 0, 6, 12, 18, 24 after round NR-2
NC = -1
O_IN, O_XOR, O_AND, O_OR, O_NOT = 0, 1, 2, 3, 4


def consts(trial):
    """Constants of the generator's selected trial (design X, proof.md Section 2): lanes 5..9 all-ones, lane 15 zero, lane 16 the
    padding, lane x = c_x and lane 10 + x = c_x ^ K_x with K_x = 0x5555...55 ^ (lane 16 for x = 1); c_0..c_4 from xorshift of the
    trial number, exactly as gen4.c set_consts."""
    M = (1 << 64) - 1
    rs = (0x9E3779B97F4A7C15 * trial + 1) & M

    def xs():
        nonlocal rs
        rs ^= (rs << 13) & M; rs ^= rs >> 7; rs ^= (rs << 17) & M
        return rs
    for _ in range(10): xs()
    K = [0] * 25
    K[16] = 0x8000000000000006
    for x in range(5):
        c = xs(); k = 0x5555555555555555 ^ (K[16] if x == 1 else 0)
        K[x], K[10 + x], K[5 + x] = c, c ^ k, M
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


def row_order(T):
    """gen3.c row_order: chain bases first (X not in T, X-1 in T), then each X after the output X+1 it reads"""
    done, ordr = 0, []
    for X in range(5):
        if (T >> ((X + 4) % 5)) & 1 and not (T >> X) & 1: ordr.append(X); done |= 1 << X
    for X in range(5):
        st, Y = [], X
        while not (done >> Y) & 1:
            st.append(Y)
            if not (T >> Y) & 1: break
            Y = (Y + 1) % 5
        while st:
            Z = st.pop()
            if not (done >> Z) & 1: ordr.append(Z); done |= 1 << Z
    return ordr


def eval_selc(pat, s, T, mc):
    """the term polarities of a planned row with trick set T (gen3.c eval_row, chained form): out[X] reads out[X+1] for X in T"""
    bb = [((pat >> X) & 1) ^ ((s >> X) & 1) for X in range(5)]
    sel, ns, bit = [0] * 5, [0] * 5, 0
    for X in row_order(T):
        a, b = (ns[(X + 1) % 5] if (T >> X) & 1 else bb[(X + 1) % 5]) ^ 1, bb[(X + 2) % 5]
        if a == b: tp = a
        else: tp = (mc >> bit) & 1; bit += 1; sel[X] = tp
        ns[X] = bb[X] ^ tp
    return sel


def eval_selk(k, pat, s, T, mc):
    """the term polarities of a planned row whose input k is the constant bit k of pat (gen4.c eval_rowc): values are constants
    (node -1) or nodes with a polarity; and2 and xor fold constants as the generator does"""
    bb = []
    nid = 5
    for X in range(5):
        if X == k: bb.append((-1, (pat >> X) & 1))
        elif (s >> X) & 1: bb.append((nid, ((pat >> X) & 1) ^ 1)); nid += 1
        else: bb.append((X, (pat >> X) & 1))
    sel, ns, bit = [0] * 5, [None] * 5, 0
    for X in row_order(T):
        a = ns[(X + 1) % 5] if (T >> X) & 1 else bb[(X + 1) % 5]
        a = (a[0], a[1] ^ 1); b = bb[(X + 2) % 5]
        if a[0] < 0: t = b if a[1] else (-1, 0)
        elif b[0] < 0: t = a if b[1] else (-1, 0)
        elif a[0] == b[0]: t = a if a[1] == b[1] else (-1, 0)
        elif a[1] == b[1]: t = (nid, a[1]); nid += 1
        else: ch = (mc >> bit) & 1; bit += 1; sel[X] = ch; t = (nid, ch); nid += 1
        x = bb[X]
        if t[0] < 0: o = (x[0], x[1] ^ t[1])
        elif x[0] < 0: o = (t[0], t[1] ^ x[1])
        elif x[0] == t[0]: o = (-1, x[1] ^ t[1])
        else: o = (nid, x[1] ^ t[1]); nid += 1
        ns[X] = o
    return sel


def bits(h, n):
    v = int.from_bytes(bytes.fromhex(h), "little")
    return [(v >> i) & 1 for i in range(n)]


def build():
    g = Gen()
    for j in range(256):
        n = g.new(O_IN, 0, 0); g.lin[n] = g.fadd(1 << j, n)
    S = [[(NC, (KL[l] >> z) & 1) for z in range(64)] for l in range(25)]
    vv = [[(64 * x + z, 0) for z in range(64)] for x in range(4)] + [[None] * 64]
    for w in range(64):                                  # v_4[w] = XOR_(x<4) v_x[w + R4 - Rx]: XOR_x rotl(v_x, ROT[x][2]) = 0
        a = (NC, 0)
        for x in range(4): a = g.xorv(a, vv[x][(w + ROT[4][2] - ROT[x][2]) & 63])
        vv[4][w] = a
    for x in range(5):
        for z in range(64):
            S[x][z] = g.xorv(vv[x][z], (NC, (KL[x] >> z) & 1)); S[10 + x][z] = g.xorv(vv[x][z], (NC, (KL[10 + x] >> z) & 1))
    for r in range(NR):
        last = r == NR - 1
        if r == 1: ff, gg = list(bytes.fromhex(PL["F1"])), bits(PL["G1"], 320)           # ff: the 5-bit D masks of the 320 lanes (x, z)
        elif r >= 2: ff, gg = list(bytes.fromhex(PL[("FG", r)][0])), bits(PL[("FG", r)][1], 320)
        else: ff = gg = [0] * 320
        phi = bits(PL[("PHI", r)], 1600)
        dec = dece = None
        if PL.get("optmode", 3) >= 4 and (r >= 2 or (r == 1 and PL.get("optmode", 3) >= 5)) and not last and ("DEC", r) in PL:
            hb = bytes.fromhex(PL[("DEC", r)]); dec = [hb[2 * i] | hb[2 * i + 1] << 8 for i in range(320)]
            dece = list(bytes.fromhex(PL[("DECE", r)]))                                  # the output complements E of the 320 rows
        C = [[None] * 64 for _ in range(5)]
        D_ = [[None] * 64 for _ in range(5)]
        D2 = [[None] * 64 for _ in range(5)]                          # D2 = NOT D, built once for a lane whose mask is not 0
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
                D2[x][z] = g.notv(D_[x][z]) if ff[x * 64 + z] else D_[x][z]
        NS = [row[:] for row in S]
        nY, need = (1, 0x0F) if last else (5, 0x1F)
        for Y in range(nY):
            for z in range(64):
                b = []
                for X in range(5):
                    y, x = X, (3 * Y + X) % 5
                    zz = (z - ROT[x][y]) & 63
                    b.append(g.xorv(S[x + 5 * y][zz], D2[x][zz] if (ff[x * 64 + zz] >> y) & 1 else D_[x][zz]))
                rsel = None
                distinct = all(v[0] != NC for v in b) and len(set(v[0] for v in b)) == 5
                kc = [X for X in range(5) if b[X][0] == NC]
                onec = kc[0] if len(kc) == 1 and len(set(v[0] for v in b if v[0] != NC)) == 4 else -1
                if dec is not None and (distinct or (onec >= 0 and r == 1)):
                    dd = dec[Y * 64 + z]; best, Tm = dd & 31, (dd >> 5) & 31
                    pat = sum(v[1] << X for X, v in enumerate(b))
                    rsel = eval_selc(pat, best, Tm, dd >> 10) if distinct else eval_selk(onec, pat, best, Tm, dd >> 10)
                    for X in range(5):
                        if best >> X & 1: b[X] = g.notv(b[X])
                    for X in row_order(Tm):                          # chained row: out[X] reads the finished out[X+1] for X in Tm
                        if not need >> X & 1: continue
                        t1 = NS[(X + 1) % 5 + 5 * Y][z] if (Tm >> X) & 1 else b[(X + 1) % 5]
                        NS[X + 5 * Y][z] = g.xorv(b[X], g.and2((t1[0], t1[1] ^ 1), b[(X + 2) % 5], rsel[X]))
                    for X in range(5):                               # output complements E of the row, after its five outputs
                        if (dece[Y * 64 + z] >> X) & 1: NS[X + 5 * Y][z] = g.notv(NS[X + 5 * Y][z])
                    continue
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
        if r == 1 and not last: S = cut_pass(g, S)
        if r == NR - 2:
            B35["LRS"] = len(g.op)
            B35["DIAG"] = {S[l][z][0] for l in (0, 6, 12, 18, 24) for z in range(64) if S[l][z][0] != NC}
    out = [S[j >> 6][j & 63] for j in range(256)]
    PD = 0
    for j, v in enumerate(out):
        assert v[0] != NC and v[0] >= 256
        PD |= v[1] << j
    return g, [v[0] for v in out], PD


def cut_pass(g, S):
    """straight-line cuts of rounds 0..1 (gen3.c cut_pass; applied once after round 1, node order kept): (a) NOT(NOT x) = x and a
    second NOT of one value are one node; (b) p XOR (p AND q) = p AND NOT q, p XOR (p OR q) = NOT p AND q when the AND (OR) has no
    other use: the XOR node becomes an AND node on p and a NOT node of the other operand (the operand of that operand when it is a NOT,
    an existing live NOT node defined before the XOR, else the AND/OR node rewritten as a NOT). Returns the remapped state planes."""
    nn = len(g.op); op, a, b = g.op, g.a, g.b
    live = [False] * nn
    for row in S:
        for v in row:
            if v[0] != NC: live[v[0]] = True
    for i in range(nn - 1, 255, -1):
        if live[i]:
            live[a[i]] = True
            if op[i] != O_NOT: live[b[i]] = True
    rp = list(range(nn)); nt = {}; uc = [0] * nn
    for i in range(256, nn):
        if live[i]:
            uc[a[i]] += 1
            if op[i] != O_NOT: uc[b[i]] += 1
    for row in S:
        for v in row:
            if v[0] != NC: uc[v[0]] += 100
    for i in range(256, nn):
        if not live[i]: continue
        o = op[i]; a[i] = rp[a[i]]
        if o != O_NOT: b[i] = rp[b[i]]
        if o == O_NOT:
            x = a[i]
            if x >= 256 and op[x] == O_NOT and live[x]: rp[i] = a[x]; live[i] = False; continue
            if x in nt and live[nt[x]]: rp[i] = nt[x]; live[i] = False; continue
            nt[x] = i; continue
        if o != O_XOR: continue
        for k in range(2):
            p, j = (b[i], a[i]) if k else (a[i], b[i])
            if j < 256 or not live[j] or op[j] not in (O_AND, O_OR): continue
            if a[j] != p and b[j] != p: continue
            if uc[j] != 1: continue
            jop = op[j]
            q = b[j] if a[j] == p else a[j]
            rr, oo = (q, p) if jop == O_AND else (p, q)
            if rr >= 256 and op[rr] == O_NOT: nq = a[rr]; live[j] = False
            elif rr in nt and nt[rr] < i and live[nt[rr]]: nq = nt[rr]; live[j] = False
            else: op[j] = O_NOT; a[j] = rr; b[j] = 0; nt[rr] = j; nq = j
            op[i] = O_AND
            if jop == O_AND: a[i], b[i] = oo, nq
            else: a[i], b[i] = nq, oo
            break
    g.cons = {}
    return [[(v[0] if v[0] == NC else rp[v[0]], v[1]) for v in row] for row in S]


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
    LRS, DIAG = B35["LRS"], B35["DIAG"]
    hfree = list(range(256, NREG))                    # free registers 256.. (a heap; only allocation takes them)
    lfree = []                                        # free registers 0..255 (a heap; may hold busy or repeated entries)
    for j in range(256):
        reg[j] = j
        if last[j]: busy[j] = True
        else: lfree.append(j)
    heapq.heapify(lfree)
    code, prog, peak = {O_XOR: 0, O_AND: 1, O_OR: 2, O_NOT: 3}, [], 0
    for i in range(256, nn):
        if not live[i]: continue
        op, a = g.op[i], g.a[i]
        b = a if op == O_NOT else g.b[i]
        dy = []                                       # registers of the operands that die here
        for k, o in enumerate((a, b)):
            if k == 1 and o == a: break
            if last[o] == i:
                r = reg[o]; busy[r] = False; dy.append(r)
                heapq.heappush(lfree if r < 256 else hfree, r)
        if i in outj:
            d = outj[i]; assert not busy[d]
        else:                                         # the lowest free register this value may use (gen3.c, B35)
            ok = [r for r in dy if r >= 256 or (i < LRS and i not in DIAG) or (i >= LRS and outdef[r] >= last[i])]
            d = min(ok) if ok else None               # a dying operand's register first (destination = a)
            if d is not None: pass
            elif i >= LRS:
                d = next((r for r in range(256) if not busy[r] and outdef[r] >= last[i]), None)
            elif i not in DIAG:
                while lfree and busy[lfree[0]]: heapq.heappop(lfree)
                if lfree: d = heapq.heappop(lfree)
            if d is None:
                while busy[hfree[0]]: heapq.heappop(hfree)
                d = heapq.heappop(hfree)
        busy[d] = True; reg[i] = d; peak = max(peak, d + 1)
        prog.append((code[op], d, reg[a], 0 if op == O_NOT else reg[g.b[i]]))
    return prog, peak


def encode(prog):
    """two-address encoding, packed little-endian: bits 0-1 op, bit 2 t; t = 1: destination = a, then a and (not NOT) b;
    t = 0: d, a and (not NOT) b; registers 11 bits.  A binary instruction with destination b is written with a, b swapped."""
    out = bytearray(); acc = nb = 0
    for c, d, a, b in prog:
        assert max(d, a, b) < 2048
        if c == 3: w, k = (3 | 4 | a << 3, 14) if d == a else (3 | d << 3 | a << 14, 25)
        else:
            if d == b and d != a: a, b = b, a
            w, k = (c | 4 | a << 3 | b << 14, 25) if d == a else (c | d << 3 | a << 14 | b << 25, 36)
        acc |= w << nb; nb += k
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
    v = [(u >> (64 * i)) & M64 for i in range(4)]
    v4 = 0
    for x in range(4):
        d = (ROT[4][2] - ROT[x][2]) % 64                  # v_4 = XOR_(x<4) rotr(u_x, d_x)
        v4 ^= ((v[x] >> d) | (v[x] << (64 - d))) & M64 if d else v[x]
    v.append(v4)
    for x in range(5):
        l[x], l[10 + x] = v[x] ^ KL[x], v[x] ^ KL[10 + x]
    return b"".join(w.to_bytes(8, "little") for w in l)


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


SALT = bytes.fromhex("e2e562a80eac76f3334ca234aa7a8230")          # 16 bytes drawn once when this package was generated; prefixed to every trial seed, so no trial is a function of the public seed alone


# ---------------- rho-w22: the search of proof.md Section 4 at width W ----------------
W, H, DK, DTT, LC, U, TB = 22, 4, 3, 5, 256, 3000, 400      # a DP: bits 0..3 zero and bits 4..6, as a number, < 5; replay cap LC; no trail is cut
GCK = 16                                                    # checkpoint gap of the replay


def rho_w(trials, step, PD):
    T = len(trials)
    A = (1 << (256 * T)) - 1
    mask = (1 << W) - 1
    R = [0] * NREG
    seeds = [SALT + bytes.fromhex(t["seed"]) for t in trials]
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
        a, la, ck = sa, 0, []                          # la: evaluations of the stored trail from its start to its DP;
        while True:                                    # ck: its points a_i for i = 0, GCK, 2 GCK, ... (checkpoints)
            if la % GCK == 0: ck.append(a)
            a = f_small(a); la += 1
            if is_dp(a) or la >= LC: break
        ev = la
        if not is_dp(a):
            obs[t]['replay_evals'] += ev; return None
        d = la - lb                                    # aligned pairs (a_i, b_(i-d))
        if d >= 0:
            ia, a, b = d, ck[d // GCK], sb
            for _ in range(d % GCK): a = f_small(a)
            ev += d % GCK
        else:
            ia, a, b = 0, sa, sb
            for _ in range(-d): b = f_small(b)
            ev += -d
        if a == b:
            obs[t]['replay_evals'] += ev; return None
        nx = (ia // GCK + 1) * GCK
        while nx < la:                                 # walk b to the next checkpoint; equal there: the trails merge in this segment
            q = b
            for _ in range(nx - ia): q = f_small(q)
            ev += nx - ia
            if q == ck[nx // GCK]: break
            a, b, ia, nx = ck[nx // GCK], q, nx, nx + GCK
        r = None
        for _ in range(min(nx, la) - ia):              # lock step through one segment
            na, nb = f_small(a), f_small(b); ev += 2
            if na == nb: r = (a, b); break
            a, b = na, nb
        obs[t]['replay_evals'] += ev
        return r

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
        raw = shake(SALT + bytes.fromhex(tr["seed"]) + b"proj", 32 * 256)
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
