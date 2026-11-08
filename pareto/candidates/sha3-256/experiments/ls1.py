"""LS1, design X: distinguished-point collision search on sha3-256-r24-prefix-v1 with the design-X message embedding.

Chain function on 256-bit points u (little-endian lanes u0..u3), proof.md Section 2:
  v_x = u_x (x < 4), v_4 = XOR_(x<4) rotr(u_x, (ROT[4][2] - ROT[x][2]) mod 64);
  m(u) = 128 bytes = lanes 0..15 of the absorbed state: lane x = v_x ^ K_x, lane 10 + x = v_x ^ K_(10+x) (x = 0..4),
  lanes 5..9 all-ones, lane 15 zero; padding gives lane 16 = 0x8000000000000006.  F(u) = SHA3-256-r24(m(u)) XOR PD
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
NR = 24                         # rounds of the target
PLANZ = """
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
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
PROG_SHA256 = "e7026c2132536e2359d14a7de85c181edbf2bb014484e45f86cdec2059971434"
NINSTR = 143003
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


SALT = bytes.fromhex("69c720652fb025a85ce30163ed74a7b4")          # 16 bytes drawn once when this package was generated; prefixed to every trial seed, so no trial is a function of the public seed alone


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
