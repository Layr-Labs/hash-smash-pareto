"""LS1, design X: distinguished-point collision search on sha3-256-r20-prefix-v1 with the design-X message embedding.

Chain function on 256-bit points u (little-endian lanes u0..u3), proof.md Section 2:
  v_x = u_x (x < 4), v_4 = XOR_(x<4) rotr(u_x, (ROT[4][2] - ROT[x][2]) mod 64);
  m(u) = 128 bytes = lanes 0..15 of the absorbed state: lane x = v_x ^ K_x, lane 10 + x = v_x ^ K_(10+x) (x = 0..4),
  lanes 5..9 all-ones, lane 15 zero; padding gives lane 16 = 0x8000000000000006.  F(u) = SHA3-256-r20(m(u)) XOR PD
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
NR = 20                         # rounds of the target
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
PROG_SHA256 = "1b3bfbcffeed9e3eb969412321e11719c1c4576a603c5c59ee6178f74bf94b19"
NINSTR = 116852
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


SALT = bytes.fromhex("2128022ed8ca017a775f017888a0f29c")          # 16 bytes drawn once when this package was generated; prefixed to every trial seed, so no trial is a function of the public seed alone


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
