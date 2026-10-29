"""LS1: distinguished-point collision search on sha3-256-r23-prefix-v1 with a linear-structure message embedding.

Chain function on 256-bit points u (little-endian lanes u0..u3):
  m(u) = 128 bytes = lanes 0..15 of the absorbed state (design X, after mpjunior92 11565cb4): lanes x and 10+x carry
  v_x XOR K, v_0..v_3 = u0..u3, v_4 = XOR_(x<4) rotr(u_x, (39 - ROT[x][2]) mod 64); lanes 5..9 and 15 the constants K below;
  padding gives lane 16 = 0x8000000000000006.  F(u) = SHA3-256-r23(m(u)) XOR PD (PD a fixed 256-bit mask).  m is injective, so F(u) = F(u') with
  u != u' gives two distinct messages with equal complete digests.
This program regenerates the bit-sliced straight line of proof.md Section 3 (the same algorithm and node order as the C
generator gen3.c, with the generator's decisions PLAN: constants trial (its values listed below), round-1 and theta complements, free term
polarities; its packed two-address encoding must hash to PROG_SHA256), checks it against a plain 23-round implementation, and runs
  rho-w22   : the search of proof.md Section 4 at width 22 (planes 22..255 zeroed after each step), one pair per trial;
              the table keeps the trail number of each end; the replay measures the stored trail by walking it,
              keeping every GCK-th point as a checkpoint, walks the new trail once and lock-steps one segment;
  proj-w256 : eight chained full-width steps from 256 random points, first pair agreeing on the 22 low digest bits.
One Python integer holds a plane for all trials of the request (trial t in bits 256t..256t+255); trials never interact.
"""
import sys, json, hashlib, heapq, base64, zlib

M64 = (1 << 64) - 1
RCA = [0x1, 0x8082, 0x800000000000808A, 0x8000000080008000, 0x808B, 0x80000001, 0x8000000080008081, 0x8000000000008009,
       0x8A, 0x88, 0x80008009, 0x8000000A, 0x8000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
       0x8000000000008002, 0x8000000000000080, 0x800A, 0x800000008000000A, 0x8000000080008081, 0x8000000000008080,
       0x80000001, 0x8000000080008008]
ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
NR = 23                         # rounds of the target
PLAN = zlib.decompress(base64.b64decode("""
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
wAtc
""")).decode()   # the plan text, zlib-compressed, base64
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
    elif _t[0] in ("R1OV", "R1E"): PL[_t[0]] = _d(_t[1])
    elif _t[0] == "nr": PL["optmode"] = int(_t[3])
TRIAL = int(PL["trial"])            # constants of the generator's selected trial
PROG_SHA256 = "847d1d673642aed7e61f9de0662966daeeb37091141f97aa3558ebbb2c06a009"
NINSTR = 136662
NREG = 2304
B35 = {}                            # LRS: first node of the last round; DIAG: lanes 0, 6, 12, 18, 24 after round NR-2
NC = -1
O_IN, O_XOR, O_AND, O_OR, O_NOT = 0, 1, 2, 3, 4


def consts(trial):
    """Constants of the generator's selected trial (structured set S3-04 of proof.md Section 2: the free lanes solve the
    704 round-0 chi neighbour conditions); the values are those gen3 sets for this trial, listed here."""
    K = [0] * 25
    K[16] = 0x8000000000000006
    for l, v in [(0, 0xe7f61a326551f37e), (1, 0x4893e125f5b84f18), (2, 0x5685826a2aaff986), (3, 0x4a6602d9a5de07f5), (4, 0x13340fdb6c9ee6ba), (5, 0xffffffffffffffff), (6, 0xffffffffffffffff), (7, 0xffffffffffffffff), (8, 0xffffffffffffffff), (9, 0xffffffffffffffff), (10, 0xb2a34f673004a62b), (11, 0x9dc6b470a0ed1a4b), (12, 0x03d0d73f7ffaacd3), (13, 0x1f33578cf08b52a0), (14, 0x46615a8e39cbb3ef), (15, 0x0000000000000000)]: K[l] = v
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


def bits(h, n):
    v = int.from_bytes(bytes.fromhex(h), "little")
    return [(v >> i) & 1 for i in range(n)]


def build():
    g = Gen()
    for j in range(256):
        n = g.new(O_IN, 0, 0); g.lin[n] = g.fadd(1 << j, n)
    S = [[(NC, (KL[l] >> z) & 1) for z in range(64)] for l in range(25)]
    for x in range(4):                                   # design X: lanes x and 10+x = u_x XOR K
        for z in range(64):
            S[x][z] = (64 * x + z, (KL[x] >> z) & 1); S[10 + x][z] = (64 * x + z, (KL[10 + x] >> z) & 1)
    for z in range(64):                                  # lanes 4 and 14 = v_4 XOR K, v_4 = XOR_(x<4) rotr(u_x, (39 - ROT[x][2]) mod 64)
        v = (NC, 0)
        for x in range(4): v = g.xorv(v, (64 * x + ((z + (39 - ROT[x][2]) % 64) & 63), 0))
        S[4][z] = g.xorv(v, (NC, (KL[4] >> z) & 1)); S[14][z] = g.xorv(v, (NC, (KL[14] >> z) & 1))
    r1ov = list(bytes.fromhex(PL["R1OV"])) if "R1OV" in PL else [0xFF] * 320     # round-1 row search decisions (design X)
    r1e = list(bytes.fromhex(PL["R1E"])) if "R1E" in PL else [0] * 320
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
                if all(v[0] != NC for v in b) and len(set(v[0] for v in b)) == 5 and dec is not None:
                    dd = dec[Y * 64 + z]; best, Tm = dd & 31, (dd >> 5) & 31
                    rsel = eval_selc(sum(v[1] << X for X, v in enumerate(b)), best, Tm, dd >> 10)
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
                    if r == 1 and r1ov[Y * 64 + z] != 0xFF: best, bj = r1ov[Y * 64 + z] & 31, (r1ov[Y * 64 + z] >> 5) - 1
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
                if r == 1 and r1e[Y * 64 + z]:                    # round-1 output complements of the row search (design X)
                    for X in range(5):
                        if (r1e[Y * 64 + z] >> X) & 1: NS[X + 5 * Y][z] = g.notv(NS[X + 5 * Y][z])
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
    u0, u1, u2, u3 = [(u >> (64 * i)) & M64 for i in range(4)]
    rotr = lambda v, s: ((v >> s) | (v << (64 - s))) & M64 if s else v
    v = [u0, u1, u2, u3]; v.append(rotr(u0, (39 - ROT[0][2]) % 64) ^ rotr(u1, (39 - ROT[1][2]) % 64) ^ rotr(u2, (39 - ROT[2][2]) % 64) ^ rotr(u3, (39 - ROT[3][2]) % 64))
    for x in range(5): l[x] ^= v[x]; l[10 + x] ^= v[x]
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


SALT = bytes.fromhex("e53818f4def251a1cd8da6de07fdcd21")          # 16 bytes drawn once when this package was generated; prefixed to every trial seed, so no trial is a function of the public seed alone


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
