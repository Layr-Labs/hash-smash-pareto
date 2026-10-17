#!/usr/bin/env python3
"""r39 joint entry (sha256-r39-prefix-v1): ONE-FILE program and sandbox experiments.  Credits: sraiw 38912d66 (construction), dariolina (row-16 claw).
Sections (in this order): [1] scalar reference (the published Table 23 pair = the 160-byte advice, the transplant, F8/F9, the claw map);
[2] the 256-lane bit-sliced walk step as a straight program of 5-byte records, folded variant, allocator; [3] the generator GEN_C (freestanding C) and its
charge; [4] THE PROGRAM (counted machine Mach, stage 1, stage 2, claw filters, Attack); [5] sandbox driver for the declared experiments.
Command line (anything else reads the organizer request on stdin):
  python3 r39joint.py --gen-c            print the generator source (compile it as in proof.md, Appendix B)
  python3 r39joint.py --windows N [--seed S] [--check]   run N full windows of 2^26 evaluations (about 80 s each), print exact counts
"""
import sys, os, json, random, time, hashlib

# ====================================================================================================
# [1] scalar reference, the advice, the construction
# ====================================================================================================
M = 0xFFFFFFFF
K = [int(x, 16) for x in """428a2f98 71374491 b5c0fbcf e9b5dba5 3956c25b 59f111f1 923f82a4 ab1c5ed5 d807aa98 12835b01 243185be 550c7dc3 72be5d74 80deb1fe 9bdc06a7 c19bf174 e49b69c1 efbe4786 0fc19dc6 240ca1cc 2de92c6f 4a7484aa 5cb0a9dc 76f988da 983e5152 a831c66d b00327c8 bf597fc7 c6e00bf3 d5a79147 06ca6351 14292967 27b70a85 2e1b2138 4d2c6dfc 53380d13 650a7354 766a0abb 81c2c92e""".split()]
IV = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
def ror(x, k): return ((x >> k) | (x << (32 - k))) & M
def S0(x): return ror(x, 2) ^ ror(x, 13) ^ ror(x, 22)
def S1(x): return ror(x, 6) ^ ror(x, 11) ^ ror(x, 25)
def s0(x): return ror(x, 7) ^ ror(x, 18) ^ (x >> 3)
def s1(x): return ror(x, 17) ^ ror(x, 19) ^ (x >> 10)
def CH(e, f, g): return (e & f) ^ (~e & g & M)
def MAJ(a, b, c): return (a & b) ^ (a & c) ^ (b & c)
H = lambda s: [int(x, 16) for x in s.split()]

# ---- the ADVICE: the published Table 23 pair (chaining value, M, M'): 8 + 16 + 16 words = 160 bytes
CV_PUB = H("b21e3e63 d12deef2 71a28861 1c40a0d4 15bb07fb b326f54c 020b80dd 0e6446c1")
M_PUB = H("5ee50e16 b5a4f02b a58b289e f713de5d 3b96d2db 215da7e2 3674669a 2ca65d8d e99c40e3 172e9a20 02e88746 07021c8f e8c6e622 b06304c1 43660040 4891771f")
MP_PUB = H("5ee50e16 b5a4f02b a58b289e f713de5d 3b96d2db 215da7e2 3674669a 2ca65d8d a99c40e3 1fae8a20 42e88746 01003fbb e8d6fe22 b06304c1 43660040 4891771f")
ADVICE_BYTES = 4 * (8 + 16 + 16)

def expand(w, n=39):
    w = list(w)
    for i in range(16, n): w.append((w[i-16] + s0(w[i-15]) + w[i-7] + s1(w[i-2])) & M)
    return w

def traj(cv, w16, n=39):
    """A[0..n+3], E[0..n+3] with A[3-j]=cv[j], E[3-j]=cv[4+j]; returns (A, E, W)"""
    w = expand(w16, n)
    A = [cv[3], cv[2], cv[1], cv[0]]; E = [cv[7], cv[6], cv[5], cv[4]]
    for r in range(n):
        a, b, c, d = A[r+3], A[r+2], A[r+1], A[r]
        e, f, g, h = E[r+3], E[r+2], E[r+1], E[r]
        t1 = (h + S1(e) + CH(e, f, g) + K[r] + w[r]) & M
        t2 = (S0(a) + MAJ(a, b, c)) & M
        A.append((t1 + t2) & M); E.append((d + t1) & M)
    return A, E, w

def compress(cv, w16, n=39):
    """39-step compression with feed-forward: 8 output words (the organizer's reduced SHA-256 on one block)"""
    A, E, _ = traj(cv, w16, n)
    st = [A[n+3], A[n+2], A[n+1], A[n], E[n+3], E[n+2], E[n+1], E[n]]
    return [(st[i] + cv[i]) & M for i in range(8)]

# trajectories of the published pair (index 0 of the construction = M', as in r39_rival/verify_transplant.py)
BA, BE, BW = traj(CV_PUB, MP_PUB)[0], traj(CV_PUB, MP_PUB)[1], MP_PUB
CA, CE, CW_ = traj(CV_PUB, M_PUB)[0], traj(CV_PUB, M_PUB)[1], M_PUB
Wp_, Wq_ = expand(MP_PUB), expand(M_PUB)
G16 = Wp_[16]          # the row-16 word g (published W16 of M')
W17PUB = Wp_[17]       # the row-17 target
D8 = (M_PUB[8] - MP_PUB[8]) & M
D9 = (M_PUB[9] - MP_PUB[9]) & M
T8, T9 = 0x087FF000, 0x03010000   # published schedule-difference targets behind F8, F9 (see inF)
def inF(w, D, T): return ((s0((w + D) & M) - s0(w)) & M) == T

def consts(cv):
    """per-window (per first block) constants of the walk map F_step: (cw, eb, cv0, cv1, cv4, cv5)"""
    t20 = (S0(cv[0]) + MAJ(cv[0], cv[1], cv[2])) & M
    eb = (cv[3] - t20) & M
    k0 = (-t20 - cv[7] - S1(cv[4]) - CH(cv[4], cv[5], cv[6]) - K[0]) & M
    c9 = (BW[9] + BA[5]) & M
    cw = (G16 - s1(BW[14]) - c9 - k0 + cv[6] + K[1]) & M
    return (cw, eb, cv[0], cv[1], cv[4], cv[5])

def fstep(x, c):
    """the walk map: x even -> F_even(x); x odd -> sigma0(x) - x"""
    if x & 1: return (s0(x) - x) & M
    cw, eb, cv0, cv1, cv4, cv5 = c
    e0 = (x + eb) & M
    return (cw + S0(x) + MAJ(x, cv0, cv1) + S1(e0) + CH(e0, cv4, cv5) - x) & M

def recover_a1(cv, a0, u):
    t20 = (S0(cv[0]) + MAJ(cv[0], cv[1], cv[2])) & M
    e0 = (cv[3] + a0 - t20) & M
    return (u + S0(a0) + MAJ(a0, cv[0], cv[1]) + S1(e0) + CH(e0, cv[4], cv[5]) + cv[6] + K[1]) & M

def build(cv, a0, a1):
    """W0..W15 of the first message (the M' side): A[4]=a0, A[5]=a1, A[6..9], E[10..13], W10..W15 = published"""
    A = [cv[3], cv[2], cv[1], cv[0], a0, a1, BA[6], BA[7], BA[8], BA[9]]
    E = [cv[7], cv[6], cv[5], cv[4]] + [None] * 6
    W = [None] * 16
    for r in range(6):
        a, b, c = A[r+3], A[r+2], A[r+1]
        t2 = (S0(a) + MAJ(a, b, c)) & M
        t1 = (A[r+4] - t2) & M
        e, f, g, h = E[r+3], E[r+2], E[r+1], E[r]
        W[r] = (t1 - h - S1(e) - CH(e, f, g) - K[r]) & M
        E[r+4] = (A[r] + t1) & M
    A += [BA[10], BA[11], BA[12], BA[13]]
    E += [None] * 4
    for k in range(10, 14): E[k] = BE[k]
    for r in range(6, 10):
        e, f, g, h = E[r+3], E[r+2], E[r+1], E[r]
        t1 = (E[r+4] - A[r]) & M
        W[r] = (t1 - h - S1(e) - CH(e, f, g) - K[r]) & M
    for r in range(10, 16): W[r] = BW[r]
    return W

def second(W):
    """the partner message: W8, W9 shifted by the published differences, W10..W15 the published ones of M"""
    V = list(W)
    V[8] = (W[8] + D8) & M; V[9] = (W[9] + D9) & M
    for r in range(10, 16): V[r] = M_PUB[r]
    return V

def claw_pair(cv, a0, u):
    """from a claw (a0 even, u odd, F(a0)=F(u)): the message pair (first block fixed by cv) or None"""
    a1 = recover_a1(cv, a0, u)
    W = build(cv, a0, a1)
    return W, second(W)

def side_ok(W):
    """W8 in F8, W9 in F9 (the exact 2^-9.808 side conditions)"""
    return inF(W[8], D8, T8) and inF(W[9], D9, T9)

# ====================================================================================================
# [2] bit-sliced 256-lane walk step (5-byte records), allocator
# ====================================================================================================
XOR, AND, OR, NOT = 0, 1, 2, 3
ONES = (1 << 256) - 1

class Gen:
    def __init__(s, nin):
        s.nin = nin; s.recs = []            # recs[i] = (op, a, b): node id nin+i
    def g(s, op, a, b=None):
        s.recs.append((op, a, b)); return s.nin + len(s.recs) - 1
    def X(s, a, b):
        if a[0] < 0 and b[0] < 0: return (-1, a[1] ^ b[1])
        if a[0] < 0: return (b[0], b[1] ^ a[1])
        if b[0] < 0: return (a[0], a[1] ^ b[1])
        if a[0] == b[0]: return (-1, a[1] ^ b[1])
        return (s.g(XOR, a[0], b[0]), a[1] ^ b[1])
    def NOTm(s, a):                          # materialise the complement as a positive-polarity node
        return (s.g(NOT, a[0]), 0)
    def A(s, a, b, orr=False):               # AND (or OR when orr) of the TRUE values
        if a[0] < 0 or b[0] < 0:
            if a[0] < 0: a, b = b, a         # b const
            if (b[1] == 0) != orr: return (-1, 0 if not orr else 1)   # AND with 0 -> 0 ; OR with 1 -> 1
            return a
        if a[0] == b[0]:
            return a if a[1] == b[1] else (-1, 1 if orr else 0)
        if a[1] == b[1]:
            if a[1] == 0: return (s.g(OR if orr else AND, a[0], b[0]), 0)
            return (s.g(AND if orr else OR, a[0], b[0]), 1)           # De Morgan, result complemented
        if a[1] == 1: a, b = b, a            # a positive, b complemented: materialise b
        return (s.g(OR if orr else AND, a[0], s.g(NOT, b[0])), 0)
    def O(s, a, b): return s.A(a, b, True)
    def full(s, a, b, c, ncy=True):
        """full adder (sum, carry); with ncy False the carry is not built (carry out of the top bit: no dead gates)"""
        cs = [t for t in (a, b, c) if t[0] < 0]; vs = [t for t in (a, b, c) if t[0] >= 0]
        if len(cs) == 0:
            pol = [a[1], b[1], c[1]]
            if pol[0] == pol[1] == pol[2]: p, x, y = c, a, b
            else:
                i = [k for k in range(3) if pol.count(pol[k]) == 1][0]
                p = (a, b, c)[i]; x, y = [t for k, t in enumerate((a, b, c)) if k != i]
            u = s.X(x, p)
            if not ncy: return s.X(u, y), Z0
            v = s.X(y, p)
            return s.X(u, y), s.X(s.A(u, v), p)
        if len(cs) == 1:
            x, y = vs; k = cs[0]
            return s.X(s.X(x, y), k), ((s.O(x, y) if k[1] else s.A(x, y)) if ncy else Z0)
        if len(cs) == 2:
            k = cs[0][1] ^ cs[1][1]; x = vs[0]
            return s.X(x, (-1, k)), (x if cs[0][1] != cs[1][1] else (-1, cs[0][1]))
        return (-1, sum(t[1] for t in cs) & 1), (-1, 1 if sum(t[1] for t in cs) >= 2 else 0)

Z0 = (-1, 0); O1 = (-1, 1)
def rotr(w, n): return [w[(j + n) % 32] for j in range(32)]
def shr(w, n): return [w[j + n] if j + n < 32 else Z0 for j in range(32)]
def xor3(g, a, b, c): return [g.X(g.X(a[j], b[j]), c[j]) for j in range(32)]
def add(g, a, b, cin=Z0):
    out = []; c = cin
    for j in range(32):
        sm, c = g.full(a[j], b[j], c, j < 31); out.append(sm)
    return out
def csa(g, a, b, c):
    sm = []; cy = [Z0]
    for j in range(32):
        s_, c_ = g.full(a[j], b[j], c[j], j < 31); sm.append(s_); cy.append(c_)
    return sm, cy[:32]

# register map of the program image
BANK = (0, 32)                     # bank A = registers 0..31, bank B = 32..63 (ping-pong)
CREG = {n: 64 + 32 * i for i, n in enumerate(("cw", "eb", "P", "R", "G"))}   # 160 constant planes: registers 64..223 (cw holds c_walk + (cv0 & cv1))
NREG_FIXED = 224
DPREG = 224                        # register of the DP summary plane

def mux(g, x0, odd, t):
    """x0 ? odd : t = t ^ (x0 & y) = odd ^ (~x0 & y) with y = odd ^ t; the form whose AND has two operands of equal polarity is used"""
    y = g.X(odd, t)
    if y[0] >= 0 and y[1] == 1 and x0[0] >= 0: return g.X(odd, g.A((x0[0], x0[1] ^ 1), y))
    return g.X(t, g.A(x0, y))

def kbuild(src_bank, dst_bank, dpb):
    """records of F_step for x in bank src_bank, results into bank dst_bank, DP summary n0 = OR of the low dpb result planes"""
    nin = NREG_FIXED
    g = Gen(nin)
    x = [(src_bank * 32 + j, 0) for j in range(32)]
    C = {n: [(CREG[n] + j, 0) for j in range(32)] for n in CREG}
    odd = xor3(g, rotr(x, 7), rotr(x, 18), shr(x, 3))
    s0x = xor3(g, rotr(x, 2), rotr(x, 13), rotr(x, 22))
    maj = [g.A(x[j], C["P"][j]) for j in range(32)]             # MAJ(x,a,b) = (x & (a^b)) + (a & b): the two parts are disjoint, (a & b) is folded into cw
    e0 = add(g, x, C["eb"])
    s1e = xor3(g, rotr(e0, 6), rotr(e0, 11), rotr(e0, 25))
    ch = [g.X(g.A(e0[j], C["R"][j]), C["G"][j]) for j in range(32)]
    s1_, c1_ = csa(g, C["cw"], s0x, maj)
    s2_, c2_ = csa(g, s1_, c1_, s1e)
    s3_, c3_ = csa(g, s2_, c2_, ch)
    t = add(g, s3_, c3_)
    pre = [mux(g, x[0], odd[j], t[j]) for j in range(32)]            # x odd -> sigma0(x), else the even sum
    tmp = add(g, [(p[0], p[1] ^ 1) for p in pre], x)                              # pre - x = ~(~pre + x)
    out = [(p[0], p[1] ^ 1) for p in tmp]
    acc = out[0]
    for j in range(1, dpb): acc = g.O(acc, out[j])
    return g, out, acc

def allocate(g, out, acc, dst_bank, dpreg=None, nfixed=None):
    """streaming allocator: returns (records [(op,dst,a,b)], dp_polarity, n_regs); output planes land in bank dst_bank"""
    nin = g.nin; n = len(g.recs)
    dpreg = DPREG if dpreg is None else dpreg; nfixed = NREG_FIXED if nfixed is None else nfixed
    # output nodes needing a NOT (complemented plane) get one extra record
    outs = []
    for j in range(32):
        node, pol = out[j]
        assert node >= 0
        if pol: node = g.g(NOT, node)
        outs.append(node)
    accn = acc[0]; assert accn >= 0
    recs = g.recs; N = len(recs)
    last = {}
    for i, (op, a, b) in enumerate(recs):
        for t in (a, b):
            if t is not None: last[t] = nin + i
    forced = {outs[j]: dst_bank * 32 + j for j in range(32)}; forced[accn] = dpreg
    for t in list(forced): last[t] = 1 << 60
    reg = {i: i for i in range(nin)}
    free = []; nxt = nfixed + 1
    res = []
    for i, (op, a, b) in enumerate(recs):
        nid = nin + i
        # free operands dying here (temps only)
        dying = []
        for t in (a, b):
            if t is not None and t >= nin and last.get(t) == nid and t not in dying: dying.append(t)
        if nid in forced: d = forced[nid]
        elif dying: d = reg[dying[0]]; dying = dying[1:]
        elif free: free.sort(); d = free.pop(0)
        else: d = nxt; nxt += 1
        for t in dying: free.append(reg[t])
        if nid in forced and nid not in (a, b):
            pass
        reg[nid] = d
        res.append((op, d, reg[a], reg[b] if b is not None else 0))
        if nid in forced:
            pass
    return res, acc[1], nxt

def to_source(recs, name, dpreg=None):
    dpreg = DPREG if dpreg is None else dpreg
    L = ["def %s(R):" % name]
    ins = set(); defined = set()
    for op, d, a, b in recs:
        for t in (a, b):
            if t not in defined: ins.add(t)
        defined.add(d)
    for t in sorted(ins): L.append(" r%d=R[%d]" % (t, t))
    sym = {XOR: "^", AND: "&", OR: "|"}
    for op, d, a, b in recs:
        if op == NOT: L.append(" r%d=r%d^M" % (d, a))
        else: L.append(" r%d=r%d%sr%d" % (d, a, sym[op], b))
    outs = sorted({d for _, d, _, _ in recs if d < 64 or d == dpreg})
    for d in outs: L.append(" R[%d]=r%d" % (d, d))
    return "\n".join(L)

def build_folded(consts5, src_bank, dst_bank, dpb):
    """the same program with the five constants (cw+Q, eb, P, R, G) of the first block folded in as constant bits"""
    g = Gen(65)                           # inputs: bank A 0..31, bank B 32..63, register 64 reserved for the DP summary
    x = [(src_bank * 32 + j, 0) for j in range(32)]
    Cc = {n: [(-1, (v >> j) & 1) for j in range(32)] for n, v in zip(("cw", "eb", "P", "R", "G"), consts5)}
    odd = xor3(g, rotr(x, 7), rotr(x, 18), shr(x, 3))
    s0x = xor3(g, rotr(x, 2), rotr(x, 13), rotr(x, 22))
    maj = [g.A(x[j], Cc["P"][j]) for j in range(32)]
    e0 = add(g, x, Cc["eb"])
    s1e = xor3(g, rotr(e0, 6), rotr(e0, 11), rotr(e0, 25))
    ch = [g.X(g.A(e0[j], Cc["R"][j]), Cc["G"][j]) for j in range(32)]
    s1_, c1_ = csa(g, Cc["cw"], s0x, maj)
    s2_, c2_ = csa(g, s1_, c1_, s1e)
    s3_, c3_ = csa(g, s2_, c2_, ch)
    t = add(g, s3_, c3_)
    pre = [mux(g, x[0], odd[j], t[j]) for j in range(32)]
    tmp = add(g, [(p[0], p[1] ^ 1) for p in pre], x)
    out = [(p[0], p[1] ^ 1) for p in tmp]
    acc = out[0]
    for j in range(1, dpb): acc = g.O(acc, out[j])
    return g, out, acc

def consts5(c):
    cw, eb, cv0, cv1, cv4, cv5 = c
    return ((cw + (cv0 & cv1)) & 0xFFFFFFFF, eb, cv0 ^ cv1, cv4 ^ cv5, cv5)

def make_kernels_folded(c, dpb):
    ks = []
    for src, dst in ((0, 1), (1, 0)):
        g, out, acc = build_folded(consts5(c), src, dst, dpb)
        recs, dppol, nreg = allocate(g, out, acc, dst, dpreg=64, nfixed=64)
        ns = {"M": ONES}
        exec(to_source(recs, "k", dpreg=64), ns)
        ks.append(dict(recs=recs, dppol=dppol, nreg=nreg, fn=ns["k"],
                       counts={o: sum(1 for r in recs if r[0] == o) for o in range(4)}))
    return ks

def make_kernels(dpb):
    """two straight programs (A->B and B->A), each a list of 5-byte records, plus compiled Python executors"""
    ks = []
    for src, dst in ((0, 1), (1, 0)):
        g, out, acc = kbuild(src, dst, dpb)
        recs, dppol, nreg = allocate(g, out, acc, dst)
        ns = {"M": ONES}
        exec(to_source(recs, "k"), ns)
        ks.append(dict(recs=recs, dppol=dppol, nreg=nreg, fn=ns["k"],
                       counts={o: sum(1 for r in recs if r[0] == o) for o in range(4)}))
    return ks

# ---- helpers shared with the tests: scalar <-> planes, constant planes
def to_planes(vals):
    return [sum(((vals[l] >> j) & 1) << l for l in range(len(vals))) for j in range(32)]
def from_planes(pl, lane):
    return sum(((pl[j] >> lane) & 1) << j for j in range(32))
def const_planes(c):
    """the 160 constant planes of a first block from (cw, eb, cv0, cv1, cv4, cv5): all-ones/all-zeros per bit"""
    cw, eb, cv0, cv1, cv4, cv5 = c
    P = cv0 ^ cv1; Q = cv0 & cv1; R = cv4 ^ cv5; G = cv5
    cw = (cw + Q) & 0xFFFFFFFF
    out = {}
    for n, v in (("cw", cw), ("eb", eb), ("P", P), ("R", R), ("G", G)):
        out[n] = [ONES if (v >> j) & 1 else 0 for j in range(32)]
    return out


# ====================================================================================================
# [3] generator source and its charge
# ====================================================================================================

GEN_C = r'''// r39 joint, Lane A: the in-program GENERATOR of the folded 256-lane walk step, compact version (freestanding C, no libc, no malloc).
// OUR OWN code (a C port of Gen/build_folded/allocate of kern39.py; gen39.c was the first, larger version).  Given the five per-first-block
// constants it emits one straight program of 5-byte records (XOR/AND/OR/NOT of 256-bit registers, 3 x 10-bit register fields) for x in bank
// src -> bank dst:  byte 0 = op (0 XOR, 1 AND, 2 OR, 3 NOT); bytes 1..4 = dst | a << 10 | b << 20 (little endian).
// registers: bank A 0..31, bank B 32..63, DP summary 64, temporaries 65...
#include <stdint.h>
#define MAXN 1200
typedef int S;                                   // signal: node*2 + polarity; constants: -2 (0) and -1 (1)
static int nin, nrec, nreg_, dppol_;
static uint8_t gop[MAXN]; static int16_t ga[MAXN], gb[MAXN], last[MAXN], regof[MAXN], forced[MAXN]; static uint8_t isfree[400];
static S x[32], o1[32], o2[32], o3[32], e0[32], s0x[32], odd[32], mj[32], ch[32], sa[32], ca[32], sb[32], cb[32], sc[32], cc[32], tt[32], pre[32], res[32];
#define NN(s) ((s) >> 1)
#define PL(s) ((s) & 1)
static S K(int v) { return v - 2; }
static int emit(int op, int a, int b) { gop[nrec] = op; ga[nrec] = a; gb[nrec] = b; return nin + nrec++; }
static S X(S a, S b) {
  int na = NN(a), nb = NN(b);
  if (na < 0 && nb < 0) return K(PL(a) ^ PL(b));
  if (na < 0) return b ^ PL(a);
  if (nb < 0) return a ^ PL(b);
  if (na == nb) return K(PL(a) ^ PL(b));
  return emit(0, na, nb) * 2 + (PL(a) ^ PL(b));
}
static S AO(S a, S b, int orr) {
  if (NN(a) < 0 || NN(b) < 0) { if (NN(a) < 0) { S t = a; a = b; b = t; } return ((PL(b) == 0) != (orr != 0)) ? K(orr) : a; }
  if (NN(a) == NN(b)) return PL(a) == PL(b) ? a : K(orr);
  if (PL(a) == PL(b)) return emit((PL(a) ? !orr : orr) ? 2 : 1, NN(a), NN(b)) * 2 + PL(a);
  if (PL(a)) { S t = a; a = b; b = t; }
  int nb = emit(3, NN(b), 0);
  return emit(orr ? 2 : 1, NN(a), nb) * 2;
}
static void full(S a, S b, S c, S *sum, S *cy, int ncy) {
  S v[3], k[3]; int nv = 0, nc = 0, in[3];
  in[0] = a; in[1] = b; in[2] = c;
  for (int i = 0; i < 3; i++) { if (NN(in[i]) < 0) k[nc++] = in[i]; else v[nv++] = in[i]; }
  if (nc == 0) {                                  // pivot adder: five gates
    int p = (PL(a) == PL(b)) ? 2 : (PL(a) == PL(c)) ? 1 : 0;
    S x1 = in[p == 0 ? 1 : 0], y1 = in[p == 2 ? 1 : 2];
    S u = X(x1, in[p]), w;
    if (!ncy) { *sum = X(u, y1); *cy = K(0); return; }
    w = X(y1, in[p]);
    *sum = X(u, y1); *cy = X(AO(u, w, 0), in[p]);
  } else if (nc == 1) { *sum = X(X(v[0], v[1]), k[0]); *cy = ncy ? AO(v[0], v[1], PL(k[0])) : K(0); }
  else if (nc == 2) { *sum = X(v[0], K(PL(k[0]) ^ PL(k[1]))); *cy = (PL(k[0]) != PL(k[1])) ? v[0] : K(PL(k[0])); }
  else { int s = PL(k[0]) + PL(k[1]) + PL(k[2]); *sum = K(s & 1); *cy = K(s >= 2); }
}
static void rotsh(S *o, const S *w, int n, int sh) { for (int j = 0; j < 32; j++) o[j] = sh ? (j + n < 32 ? w[j + n] : K(0)) : w[(j + n) & 31]; }
static void sig3(S *o, const S *w, int a, int b, int c, int sh) {      // o = rot a ^ rot b ^ (rot or shift) c
  rotsh(o1, w, a, 0); rotsh(o2, w, b, 0); rotsh(o3, w, c, sh);
  for (int j = 0; j < 32; j++) o[j] = X(X(o1[j], o2[j]), o3[j]);
}
static void csa(S *so, S *co, const S *a, const S *b, const S *c) {
  S cy[32]; cy[0] = K(0);
  for (int j = 0; j < 32; j++) { S s, k; full(a[j], b[j], c[j], &s, &k, j < 31); so[j] = s; if (j < 31) cy[j + 1] = k; }
  for (int j = 0; j < 32; j++) co[j] = cy[j];
}
static void addw(S *o, const S *a, const S *b, S cin) { S c = cin; for (int j = 0; j < 32; j++) { S s; full(a[j], b[j], c, &s, &c, j < 31); o[j] = s; } }
static S bitc(uint32_t v, int j) { return K((v >> j) & 1); }

int gen(uint32_t cw, uint32_t eb, uint32_t P, uint32_t R, uint32_t G, int src, int dst, int dpb, uint8_t *out) {
  nin = 65; nrec = 0;
  S cwv[32], cebv[32], cpv[32], crv[32], cgv[32];
  for (int j = 0; j < 32; j++) { x[j] = (src * 32 + j) * 2; cwv[j] = bitc(cw, j); cebv[j] = bitc(eb, j); cpv[j] = bitc(P, j); crv[j] = bitc(R, j); cgv[j] = bitc(G, j); }
  sig3(odd, x, 7, 18, 3, 1);
  sig3(s0x, x, 2, 13, 22, 0);
  for (int j = 0; j < 32; j++) mj[j] = AO(x[j], cpv[j], 0);
  addw(e0, x, cebv, K(0));
  sig3(res, e0, 6, 11, 25, 0);                                             // res = Sigma1(e0)
  for (int j = 0; j < 32; j++) ch[j] = X(AO(e0[j], crv[j], 0), cgv[j]);
  csa(sa, ca, cwv, s0x, mj);
  csa(sb, cb, sa, ca, res);
  csa(sc, cc, sb, cb, ch);
  addw(tt, sc, cc, K(0));
  for (int j = 0; j < 32; j++) {                                           // mux x0 ? odd : t, then complemented: pre - x = ~(~pre + x)
    S y = X(odd[j], tt[j]);
    pre[j] = ((NN(y) >= 0 && PL(y) == 1) ? X(odd[j], AO(x[0] ^ 1, y, 0)) : X(tt[j], AO(x[0], y, 0))) ^ 1;
  }
  addw(res, pre, x, K(0));
  S acc; int outn[32];
  for (int j = 0; j < 32; j++) res[j] ^= 1;
  acc = res[0];
  for (int j = 1; j < dpb; j++) acc = AO(acc, res[j], 1);
  for (int j = 0; j < 32; j++) { outn[j] = NN(res[j]); if (PL(res[j])) outn[j] = emit(3, outn[j], 0); }
  int accn = NN(acc), total = nin + nrec;
  for (int i = 0; i < total; i++) { last[i] = -1; forced[i] = -1; }
  for (int i = 0; i < nrec; i++) { last[ga[i]] = nin + i; if (gop[i] != 3) last[gb[i]] = nin + i; }
  for (int j = 0; j < 32; j++) { forced[outn[j]] = dst * 32 + j; last[outn[j]] = 30000; }
  forced[accn] = 64; last[accn] = 30000;
  for (int i = 0; i < nin; i++) regof[i] = i;
  for (int i = 0; i < 400; i++) isfree[i] = 0;
  int nxt = 65;
  for (int i = 0; i < nrec; i++) {
    int nid = nin + i, a = ga[i], b = gop[i] != 3 ? gb[i] : -1, dy[2], nd = 0, d, k0 = 0;
    if (a >= nin && last[a] == nid) dy[nd++] = a;
    if (b >= nin && b != a && last[b] == nid) dy[nd++] = b;
    if (forced[nid] >= 0) d = forced[nid];
    else if (nd) { d = regof[dy[0]]; k0 = 1; }
    else { d = -1; for (int r = 65; r < nxt; r++) if (isfree[r]) { d = r; break; } if (d >= 0) isfree[d] = 0; else d = nxt++; }
    for (int k = k0; k < nd; k++) isfree[regof[dy[k]]] = 1;
    regof[nid] = d;
    uint32_t w = (uint32_t)d | ((uint32_t)regof[a] << 10) | ((uint32_t)(b >= 0 ? regof[b] : 0) << 20);
    uint8_t *q = out + 5 * i;
    q[0] = gop[i]; q[1] = w; q[2] = w >> 8; q[3] = w >> 16; q[4] = w >> 24;
  }
  nreg_ = nxt; dppol_ = PL(acc);
  return nrec;
}
int g_nreg(void) { return nreg_; }
int g_dppol(void) { return dppol_; }
'''
class GW:
    """charge of the generator: wasm operators executed (wasmtime fuel) when a compiled module is given in R39_WASM, else the halt cap"""
    FALLBACK = 575000          # the generator halts after 575000 operators (GCAP); measured over 200 first blocks: mean 523.6k, max 543k
    AVAILABLE = False
    try:
        import wasmtime as _wt
        if os.environ.get("R39_WASM"):
            _cfg = _wt.Config(); _cfg.consume_fuel = True; _eng = _wt.Engine(_cfg); _mod = _wt.Module.from_file(_eng, os.environ["R39_WASM"]); AVAILABLE = True
    except Exception:
        AVAILABLE = False
    @staticmethod
    def run(c5, src=0, dst=1, dpb=7):
        st = GW._wt.Store(GW._eng); inst = GW._wt.Instance(st, GW._mod, []); ex = inst.exports(st); st.set_fuel(10 ** 12)
        n = ex["gen"](st, *c5, src, dst, dpb, 32768); used = 10 ** 12 - st.get_fuel(); raw = ex["memory"].read(st, 32768, 32768 + 5 * n); recs = []
        for i in range(n):
            w = raw[5*i+1] | raw[5*i+2] << 8 | raw[5*i+3] << 16 | raw[5*i+4] << 24
            recs.append((raw[5*i], w & 1023, (w >> 10) & 1023, (w >> 20) & 1023))
        return used, recs
    @staticmethod
    def ops(c5): return GW.run(c5)[0] if GW.AVAILABLE else GW.FALLBACK

# ====================================================================================================
# [4] THE PROGRAM
# ====================================================================================================
ONES = (1 << 256) - 1
M32 = M
M20, M12, M40, M25 = (1 << 20) - 1, (1 << 12) - 1, (1 << 40) - 1, (1 << 25) - 1
DBG = False
HIGHMASK = [sum(1 << p for p in range(256) if (p >> k) & 1) for k in range(8)]

class Mach:
    """counted word RAM: every method is one charged primitive (a load/store is charged 3: index shift, base add, access)"""
    def __init__(s): s.o = 0; s.cat = {}; s.blk = {}; s.nest = 0
    def bs(s): return (s.o, s.nest)
    def be(s, name, b, sub=False):
        d = (s.o - b[0]) - (s.nest - b[1])          # instructions of this block itself (callees counted once, at their own definition)
        if sub: s.nest += (s.o - b[0]) - 2              # a subroutine: its body is charged to the caller's census only as call + return
        if d > s.blk.get(name, 0): s.blk[name] = d
    def x(s, a, b): s.o += 1; return a ^ b
    def a(s, a, b): s.o += 1; return a & b
    def r(s, a, b): s.o += 1; return a | b
    def n(s, a): s.o += 1; return a ^ ONES
    def ad(s, a, b): s.o += 1; return (a + b) & ONES
    def sb(s, a, b): s.o += 1; return (a - b) & ONES
    def sl(s, a, k): s.o += 1; return (a << k) & ONES
    def sr(s, a, k): s.o += 1; return a >> k
    def rl(s, a, k): s.o += 1; k %= 256; return a if k == 0 else ((a << k) | (a >> (256 - k))) & ONES
    def rr(s, a, k): return s.rl(a, 256 - (k % 256))
    def ne(s, a, b): s.o += 1; return 1 if a != b else 0
    def jz(s, a): s.o += 2; return a == 0
    def jnz(s, a): s.o += 2; return a != 0
    def jeq(s, a, b): s.o += 2; return a == b
    def jne(s, a, b): s.o += 2; return a != b
    def jge(s, a, b): s.o += 2; return a >= b
    def ld(s, arr, i): s.o += 3; return arr[i]
    def st(s, arr, i, v): s.o += 3; arr[i] = v
    def mv(s): s.o += 1
    def tick(s, name, t0):
        d = s.o - t0
        s.cat[name] = s.cat.get(name, 0) + d
    def blkmax(s, name, d):          # static instruction census: ops of one straight-line pass of a code block
        if d > s.blk.get(name, 0): s.blk[name] = d

def mS0(m, v):
    d = m.r(v, m.sl(v, 32)); return m.a(m.x(m.x(m.sr(d, 2), m.sr(d, 13)), m.sr(d, 22)), M32)
def mS1(m, v):
    d = m.r(v, m.sl(v, 32)); return m.a(m.x(m.x(m.sr(d, 6), m.sr(d, 11)), m.sr(d, 25)), M32)
def ms0(m, v):
    d = m.r(v, m.sl(v, 32)); return m.a(m.x(m.x(m.sr(d, 7), m.sr(d, 18)), m.sr(v, 3)), M32)
def ms1(m, v):
    d = m.r(v, m.sl(v, 32)); return m.a(m.x(m.x(m.sr(d, 17), m.sr(d, 19)), m.sr(v, 10)), M32)
def mMAJ(m, a, b, c): return m.r(m.a(a, b), m.a(c, m.r(a, b)))
def mCH(m, e, f, g): return m.x(m.a(e, f), m.a(m.x(e, M32), g))
def a32(m, a, b): return m.a(m.ad(a, b), M32)
def s32(m, a, b): return m.a(m.sb(a, b), M32)

class P:
    """the single concrete schedule"""
    DPB = 7                  # DP: low 7 bits of the new point zero
    MAXS = 2048              # cut a trail older than this (scan every CUTP iterations)
    CUTP = 1024
    WIN = 1 << 26            # walk evaluations per first block
    QCAP, QFULL = 4096, 4032 # queue of pairs (8 bytes each)
    NSLOT = 128              # stage-2 pair slots: lanes (p, p+128)
    WHEEL = 4096             # timing wheel for the delayed launches (16-bit buckets)
    WDIG = ((15, 1), (12, -1), (10, -1))     # table words W = 2^15 - 2^12 - 2^10 = 27648: r*W by three shifts and two adds
    WDIG_FOLD = ((14, 1), (13, 1), (10, 1), (9, 1))   # folded variant: W = 26112 words (the generator's code image takes 60 KB of the budget): r*W by four shifts and three adds
    GCAP = 575000            # the generator halts after 575000 wasm operators (measured over 200 first blocks: mean 523.6k, sd 8.0k, max 543k); charged, next first block
    RCAP = 206               # registers a generated kernel may use (the declared file has 256: 50 are left for the scalar handlers)
    KCAP = 1030              # capacity of one generated kernel image (records); a first block with a longer kernel is skipped
    CMP1 = 12                # first-stage planes of the pair comparison

def table_words(wdig=P.WDIG): return sum(sg * (1 << k) for k, sg in wdig)

class Attack:
    def __init__(s, win=P.WIN, wdig=P.WDIG, seed=1, check=False, shadow=False, fold=False):
        s.m = Mach(); s.win = win; s.check = check; s.shadow_on = shadow; s.fold = fold; s.dpreg = DPREG
        s.wdig = P.WDIG_FOLD if (fold and wdig is P.WDIG) else wdig; s.W = table_words(s.wdig)
        s.ks = None if fold else make_kernels(P.DPB); s.R = [0] * 512
        s.rnd = random.Random(seed)
        s.st = dict(windows=0, iters=0, hits=0, matches=0, raw=0, trails=0, cuts=0, s2phases=0, s2iters=0, pairs=0, f9=0, f8=0, w17=0,
                    verify=0, qmax=0, opp=0, same=0, claws_distinct=0)
        s.distinct = set(); s.cv_id = 0; s.cv_try = False
        s.LA = [0] * 256; s.sav = [0] * 32
        s.base_setup()
    # ------------------------------------------------------------------ run-level constants from the 160-byte advice
    def base_setup(s):
        m = s.m; t0 = m.o
        m.o += 2 * 2812 + 120               # two compressions expand the advice into the base trajectory; ~120 ops for the constants below
        s.K24 = S0(BA[7])                   # Sigma0(A7)
        s.A7, s.A6 = BA[7], BA[6]
        t25 = (S0(BA[8]) + MAJ(BA[8], BA[7], BA[6])) & M32
        s.CE5 = (BA[9] - t25) & M32         # e5 = a1 + A9 - t2_5
        s.NE11 = (~BE[11]) & M32; s.CH0 = BE[11] & BE[10]
        s.CW8 = (BE[12] - BA[8] - S1(BE[11]) - K[8]) & M32     # W8 = CW8 - e4 - CH(E11, E10, e5)
        s.C17 = (s1(BW[15]) + BW[10]) & M32
        s.C9 = (BW[9] + BA[5]) & M32
        m.tick('run_setup', t0)
    # ------------------------------------------------------------------ one first block
    def window_setup(s, cv=None):
        m = s.m; t0 = m.o; s.m0 = None                                   # M0 unknown when the chaining value is given
        while True:
            if cv is None or s.cv_try:
                blk = [s.rnd.getrandbits(32) for _ in range(16)]; m.o += 2      # the first block: two random words
                s.m0 = blk; m.o += 16                                            # keep the first block M0 (16 stores)
                cv = compress(IV, blk); m.o += 2812                              # one target compression
            s.cv_try = True
            if not s.fold: break
            ks_try = make_kernels_folded(consts(cv), P.DPB)
            gops = GW.ops(consts5(consts(cv)))
            if len(ks_try[0]['recs']) <= P.KCAP and gops <= P.GCAP and max(ks_try[0]['nreg'], ks_try[1]['nreg']) <= P.RCAP: break
            m.o += min(gops, P.GCAP); s.st['kskip'] = s.st.get('kskip', 0) + 1                  # image too long or generator halted: next first block
        s.cv = cv; s.cv_id += 1
        s.c = consts(cv); m.o += 140                                             # t2_0, e0 base, k0, c9, c_walk: straight line
        cw = s.c[0]
        s.CA1 = (cv[6] + K[1] - cw) & M32                                        # a1 = sigma0(u) + a0 + CA1 on a claw
        if s.fold:
            # the generator runs in the attack: one generation (executed wasm operators, gen39.wasm under wasmtime fuel) emits the
            # bank A -> B program with the five constants folded in; the bank B -> A program is the same records with the bank
            # bits of every register field swapped (a relocation pass of 8 operations per record)
            tg = m.o
            c5 = consts5(s.c)
            s.ks = ks_try
            m.o += gops + 8 * len(s.ks[0]['recs'])
            if s.check and GW.AVAILABLE:
                assert GW.run(c5, 0, 1, P.DPB)[1] == [tuple(r) for r in s.ks[0]['recs']]
                assert GW.run(c5, 1, 0, P.DPB)[1] == [tuple(r) for r in s.ks[1]['recs']]
            s.dpreg = 64; m.tick('generator', tg)
        else:
            cp = const_planes(s.c); m.o += 160 * 3                            # plane = 0 - ((c >> j) & 1): three operations
            for n, base in CREG.items():
                for j in range(32): s.R[base + j] = cp[n][j]
        s.W = table_words(s.wdig)
        s.tab = [0] * s.W; m.o += 4 * s.W                                        # clear: store, pointer add, compare, branch per word
        s.qn = 0; s.qw = [0] * (P.QCAP // 4 + 1)
        s.cur = 0; s.it = 0
        # 256 trails, ids 0..255 (x0 = id): planes 0..7 are the lane-bit patterns, the others 0
        for j in range(32): s.R[j] = (sum(1 << l for l in range(256) if (l >> j) & 1) if j < 8 else 0)
        m.o += 32
        for l in range(256): s.LA[l] = l; m.o += 3
        s.idc = 256
        s.shadow = list(range(256)) if s.shadow_on else None
        s.st['windows'] += 1
        m.tick('window_setup', t0)
    # ------------------------------------------------------------------ lane primitives (subroutines: call + return = 2 operations)
    def insert_lane(s, base, low, l, val, nbits=20):
        m = s.m; R = s.R; b = m.bs(); m.o += 2
        Z = m.rl(val, l); nl = m.n(low)
        for j in range(nbits):
            t = m.rr(Z, j); p = R[base + j]
            R[base + j] = m.x(p, m.a(m.x(p, t), low))
        for j in range(nbits, 32): R[base + j] = m.a(R[base + j], nl)
        m.be('insert_lane', b, True)
    def find_lane(s, mask):
        m = s.m; bb = m.bs(); m.o += 2
        low = m.a(mask, m.sb(0, mask)); l = 0
        for k in range(7, -1, -1):
            b = m.ne(m.a(low, HIGHMASK[k]), 0)
            l = m.sl(b, k) if k == 7 else (m.r(l, m.sl(b, k)) if k else m.r(l, b))
        m.be('find_lane', bb, True)
        return low, l
    def extract(s, base, jlo, jhi, low, l, name):
        m = s.m; R = s.R; b = m.bs(); m.o += 2
        Z = m.a(R[base + jhi], low)
        for j in range(jhi - 1, jlo - 1, -1): Z = m.r(m.rl(Z, 1), m.a(R[base + j], low))
        v = m.rr(Z, l)
        m.be(name, b, True)
        return v
    # ------------------------------------------------------------------ the claw: exact filters
    def claw(s, a, b):
        m = s.m; t0 = m.o; tb0 = m.bs(); s.st['raw'] += 1
        if m.jnz(m.a(a, 1)): a0, u = b, a
        else: a0, u = a, b
        m.mv()
        if (s.cv_id, a0, u) not in s.distinct:                           # bookkeeping of the experiment, not part of the program
            s.distinct.add((s.cv_id, a0, u)); s.st['claws_distinct'] += 1
        if s.check: assert fstep(a0, s.c) == fstep(u, s.c) and a0 % 2 == 0 and u % 2 == 1
        a1 = a32(m, a32(m, ms0(m, u), a0), s.CA1)
        W9 = s32(m, s.C9, a1)
        ok = m.jeq(s32(m, ms0(m, a32(m, W9, D9)), ms0(m, W9)), T9)
        if s.check:
            Wc = build(s.cv, a0, recover_a1(s.cv, a0, u)); Wx = expand(Wc)
            assert Wc[9] == W9 and Wx[16] == G16 and Wc[1] == u and ok == inF(Wc[9], D9, T9)
        m.be('claw_filter', tb0); m.tick('claw_filter', t0)
        if not ok: return 0
        s.st['f9'] += 1; t1 = m.o; tb1 = m.bs()
        e4 = s32(m, a32(m, a0, BA[8]), a32(m, s.K24, mMAJ(m, s.A7, s.A6, a1)))
        e5 = a32(m, a1, s.CE5)
        W8 = s32(m, s32(m, s.CW8, e4), m.x(s.CH0, m.a(e5, s.NE11)))
        ok8 = m.jeq(s32(m, ms0(m, a32(m, W8, D8)), ms0(m, W8)), T8)
        if s.check: assert W8 == Wc[8] and ok8 == inF(Wc[8], D8, T8)
        m.be('claw_f8', tb1); m.tick('claw_f8', t1)
        if not ok8: return 0
        s.st['f8'] += 1; t2 = m.o; tb2 = m.bs(); cv = s.cv
        e1 = s32(m, s32(m, a32(m, cv[2], a1), mS0(m, a0)), mMAJ(m, a0, cv[0], cv[1]))
        e0 = a32(m, a0, s.c[1])
        w2 = s32(m, s32(m, s32(m, s32(m, s32(m, BA[6], mS0(m, a1)), mMAJ(m, a1, a0, cv[0])), cv[5]), mS1(m, e1)), mCH(m, e1, e0, cv[4]))
        w2 = s32(m, w2, K[2])
        w17 = a32(m, a32(m, s.C17, ms0(m, w2)), u)
        okw = m.jeq(w17, W17PUB)
        if s.check: assert w17 == Wx[17]
        m.be('claw_w17', tb2); m.tick('claw_w17', t2)
        if not okw: return 0
        s.st['w17'] += 1; s.st['verify'] += 1
        m.o += 2 * 2812 + 400                  # build W0..W15 of the pair, compress both messages (2 units), compare
        W1m, W2m = claw_pair(s.cv, a0, u)
        if W1m != W2m and compress(s.cv, W1m) == compress(s.cv, W2m):
            s.st['collisions'] = s.st.get('collisions', 0) + 1; s.pairs_found = getattr(s, 'pairs_found', []) + [(list(s.cv), W1m, W2m, getattr(s, 'm0', None))]
            if getattr(s, 'm0', None) is not None: s.messages = getattr(s, 'messages', []) + [(list(s.m0) + list(W1m), list(s.m0) + list(W2m))]   # the two 128-byte messages
            s.success = True
            return 1
        return 0
    # ------------------------------------------------------------------ queue of matched pairs (8 bytes each, four per word)
    def qpush(s, pk):
        m = s.m; b = m.bs(); m.o += 2
        wi = m.sr(s.qn, 2); sh = m.sl(m.a(s.qn, 3), 6)
        w = m.ld(s.qw, wi)
        w = m.x(w, m.a(m.x(w, m.sl(pk, sh)), m.sl((1 << 64) - 1, sh)))
        m.st(s.qw, wi, w); s.qn = m.ad(s.qn, 1)
        m.be('qpush', b, True)
    def qpop(s, qi):
        m = s.m; b = m.bs(); m.o += 2
        w = m.ld(s.qw, m.sr(qi, 2)); v = m.a(m.sr(w, m.sl(m.a(qi, 3), 6)), (1 << 64) - 1)
        m.be('qpop', b, True)
        return v
    # ------------------------------------------------------------------ stage 1: one iteration of 256 lanes
    def iter1(s):
        m = s.m; R = s.R; ks = s.ks; k = ks[s.cur]
        k['fn'](R); m.o += len(k['recs']); s.cur ^= 1; s.it += 1; s.st['iters'] += 1
        n0 = R[s.dpreg]; m.o += 5                       # loop: counter increment, compare, branch (3); cut-scan countdown and branch (2)
        if s.shadow is not None: s.chk_iter()
        if m.jne(n0, ONES):
            t0 = m.o
            hit = m.n(n0)
            while True:
                low, l = s.find_lane(hit); hit = m.x(hit, low)
                s.hit(low, l)
                if m.jz(hit): break
            full = m.jge(s.qn, P.QFULL)                    # queue-full test after an iteration with hits
            m.tick('hits', t0)
            if full: s.stage2()
        if s.it % P.CUTP == 0: s.cutscan()
    def hit(s, low, l):
        m = s.m; R = s.R; base = s.cur * 32; s.st['hits'] += 1; ta = m.bs()
        r = s.extract(base, P.DPB, 31, low, l, 'extract25')
        t = m.sl(r, s.wdig[0][0]) if s.wdig[0][1] > 0 else m.sb(0, m.sl(r, s.wdig[0][0]))
        for kk, sg in s.wdig[1:]: t = m.ad(t, m.sl(r, kk)) if sg > 0 else m.sb(t, m.sl(r, kk))
        word = m.sr(t, 25); f = m.a(t, M25); sub = m.sr(m.ad(m.sl(f, 2), m.sl(f, 1)), 25); chk = m.a(r, 255)
        sh = m.ad(m.sl(sub, 5), m.sl(sub, 3))
        w = m.ld(s.tab, word); e = m.a(m.sr(w, sh), M40)
        match = m.jeq(m.sr(e, 32), chk) and m.jnz(m.a(e, M32))
        m.be('hit_a', ta); tb = m.bs()
        lw = m.ld(s.LA, l); idv = m.a(lw, M20); ln = m.sb(s.it, m.sr(lw, 20))
        en = m.r(m.r(idv, m.sl(ln, 20)), m.sl(chk, 32))
        w2 = m.x(w, m.a(m.x(w, m.sl(en, sh)), m.sl(M40, sh))); m.st(s.tab, word, w2)
        m.be('hit_b', tb)
        if match:
            tc = m.bs(); s.st['matches'] += 1
            pk = m.r(m.sl(m.a(e, M32), 32), m.a(en, M32)); s.qpush(pk)
            if s.qn > s.st['qmax']: s.st['qmax'] = s.qn
            m.be('hit_match', tc)
        td = m.bs()
        nid = s.idc; s.idc = m.ad(nid, 1)                        # next trail id
        m.jge(nid, 1 << 20); assert nid < (1 << 20)      # halt if the id space of a window is exhausted
        m.st(s.LA, l, m.r(nid, m.sl(s.it, 20))); s.st['trails'] += 1
        s.insert_lane(base, low, l, nid)
        if s.shadow is not None: s.shadow[l] = nid
        m.be('hit_c', td)
    def cutscan(s):
        m = s.m; t0 = m.o; base = s.cur * 32
        for l in range(256):
            tl = m.bs()
            lw = m.ld(s.LA, l); age = m.sb(s.it, m.sr(lw, 20)); m.o += 3          # + loop control
            if m.jge(age, P.MAXS):
                low = m.sl(1, l); nid = s.idc; s.idc = m.ad(nid, 1); s.st['cuts'] += 1
                m.st(s.LA, l, m.r(nid, m.sl(s.it, 20))); s.insert_lane(base, low, l, nid)
                if s.shadow is not None: s.shadow[l] = nid
            m.be('cut_lane', tl)
        m.tick('cutscan', t0)
    # ------------------------------------------------------------------ stage 2: pairs in lane pairs (p, p+128), continuous refill
    def stage2(s):
        m = s.m; R = s.R; t0 = m.o; s.st['s2phases'] += 1
        sv = s.cur
        for j in range(32): s.sav[j] = R[sv * 32 + j]
        m.o += 64
        cur = 0; it2 = 0; qi = 0; bact = 0; live = 0
        free = list(range(P.NSLOT - 1, -1, -1)); bid = {}; nxt = {}; wh = [0] * (P.WHEEL // 16)
        qn = s.qn
        while True:
            # launch queued pairs into free slots
            while True:
                m.o += 4                                       # free-stack not empty and queue not exhausted: two compares, two branches
                if not (free and qi < qn): break
                tl = m.bs()
                m.o += 4; p = free.pop()                       # pop the free-slot stack
                pk = s.qpop(qi); qi += 1; m.o += 1
                x1 = m.sr(pk, 32); x2 = m.a(pk, M32)
                i1, l1 = m.a(x1, M20), m.sr(x1, 20); i2, l2 = m.a(x2, M20), m.sr(x2, 20)
                if m.jge(l1, l2): iA, lA, iB, lB = i1, l1, i2, l2
                else: iA, lA, iB, lB = i2, l2, i1, l1
                m.o += 2
                d = m.sb(lA, lB)
                low = m.sl(1, p)
                s.insert_lane(cur * 32, low, p, iA)
                if m.jz(d):
                    s.insert_lane(cur * 32, m.sl(low, 128), p + 128, iB); bact = m.r(bact, low)
                else:
                    idx = m.a(m.ad(it2, d), P.WHEEL - 1); wi = m.sr(idx, 4); sh = m.sl(m.a(idx, 15), 4)      # wheel push
                    w = m.ld(wh, wi); head = m.a(m.sr(w, sh), 0xFFFF)
                    m.st(bid, p, iB); m.st(nxt, p, head)
                    m.st(wh, wi, m.x(w, m.a(m.x(w, m.sl(m.ad(p, 1), sh)), m.sl(0xFFFF, sh))))
                live += 1; m.o += 1; s.st['pairs'] += 1                  # live-pair counter
                if DBG: s.info = getattr(s, 'info', {}); s.info[p] = (iA, lA, iB, lB, it2, d)
                m.be('launch', tl)
            if m.jz(live): break
            if DBG and it2 == 4000:
                print('stuck', [(p, s.info[p], (bact >> p) & 1) for p in range(128) if p not in free and p in s.info]); raise SystemExit
            if DBG and it2 % 200 == 0: print('s2 it2', it2, 'live', live, 'qi', qi, 'qn', qn, 'free', len(free), 'bact', bin(bact).count('1'), flush=True)
            # launches due now
            tw = m.bs(); idx = m.a(it2, P.WHEEL - 1); wi = m.sr(idx, 4); sh = m.sl(m.a(idx, 15), 4)
            w = m.ld(wh, wi); head = m.a(m.sr(w, sh), 0xFFFF)
            if m.jnz(head): m.st(wh, wi, m.x(w, m.sl(head, sh)))
            m.be('wheel_check', tw)
            while m.jnz(head):
                tl = m.bs()
                p = m.sb(head, 1); iB = m.ld(bid, p); head = m.ld(nxt, p)
                lowp = m.sl(1, p)
                s.insert_lane(cur * 32, m.sl(lowp, 128), p + 128, iB); bact = m.r(bact, lowp)
                m.be('launchB', tl)
            k = s.ks[cur]; k['fn'](R); m.o += len(k['recs']); cur ^= 1; it2 += 1; m.o += 3; s.st['s2iters'] += 1
            # compare the two lanes of every pair: first CMP1 planes, then the rest for the candidates
            tc = m.bs(); base = cur * 32; acc = 0
            for j in range(P.CMP1):
                pl = R[base + j]; dj = m.x(pl, m.rl(pl, 128)); acc = dj if j == 0 else m.r(acc, dj)
            cand = m.a(m.n(acc), bact)
            m.be('cmp1', tc)
            if m.jnz(cand):
                tc = m.bs(); acc2 = 0
                for j in range(P.CMP1, 32):
                    pl = R[base + j]; dj = m.x(pl, m.rl(pl, 128)); acc2 = dj if j == P.CMP1 else m.r(acc2, dj)
                full = m.a(cand, m.n(acc2))
                m.be('cmp2', tc)
                while m.jnz(full):
                    tm = m.bs()
                    low, l = s.find_lane(full); full = m.x(full, low)
                    pp = R[(cur ^ 1) * 32]
                    if m.jnz(m.a(m.x(pp, m.rl(pp, 128)), low)):          # opposite parity of the predecessors
                        s.st['opp'] += 1
                        low2 = m.r(low, m.sl(low, 128))
                        Z = s.extract((cur ^ 1) * 32, 0, 31, low2, l, 'extract32x2')
                        a = m.a(Z, M32); b = m.a(m.sr(Z, 128), M32)
                        tcl = m.o; r_cl = s.claw(a, b); m.nest += m.o - tcl
                        if r_cl: s.success = True                    # success: the window stops after this merge
                    else: s.st['same'] += 1
                    bact = m.x(bact, low); m.o += 4; free.append(l); live -= 1; m.o += 1
                    m.be('merge', tm)
        # restore the stage-1 lanes
        for j in range(32): R[sv * 32 + j] = s.sav[j]
        m.o += 64; s.qn = 0; m.tick('stage2', t0)
    # ------------------------------------------------------------------ check-mode shadow (not part of the program)
    def chk_iter(s):
        R = s.R; base = s.cur * 32
        for l in range(256):
            s.shadow[l] = fstep(s.shadow[l], s.c)
        if s.it < 3 or s.it % 200 == 0:
            for l in range(256):
                v = from_planes([R[base + j] for j in range(32)], l)
                assert v == s.shadow[l], (s.it, l, hex(v), hex(s.shadow[l]))
        n0 = R[s.dpreg]
        for l in range(256):
            assert (((n0 >> l) & 1) == 0) == ((s.shadow[l] & ((1 << P.DPB) - 1)) == 0)
    # ------------------------------------------------------------------ one window
    def run_window(s, cv=None, iters=None):
        s.success = False; s.window_setup(cv)
        for _ in range(iters if iters else s.win // 256):
            s.iter1()
            if s.success: break
        if s.qn and not s.success: s.stage2()
        return s.st


# ====================================================================================================
# [5] sandbox driver (organizer request on stdin)
# ====================================================================================================
GEN_EXPERIMENTS = ("r39-transplant-claw", "r39-window-small")

def _e1(i, sd):
    """r39-transplant-claw.  Trial 0: the published Table 23 pair through the claw() path of the program (folded variant, all filters, the final
    two-compression check).  Trials 1..255: a random chaining value, a random even a0 and odd u -> the claw equation, the transplant of the
    published trajectory on both messages, and the row-16 identity W16 - g = F(u) - F(a0)."""
    if i == 0:
        A = Attack(win=1 << 20, check=True, fold=True)
        A.window_setup(cv=CV_PUB)
        o0 = A.m.o
        r = A.claw(MP_PUB[1], BA[4])                      # the two predecessors of the published pair: u = W1 (odd), a0 = A[4] (even)
        W1m, W2m = A.pairs_found[0][1:3] if r == 1 else (None, None)
        return {"claw_returned_pair": r, "passed_f9": A.st["f9"], "passed_f8": A.st["f8"], "passed_w17": A.st["w17"],
                "pair_is_published": int(W1m == MP_PUB and W2m == M_PUB),
                "sfs_collision": int(compress(CV_PUB, MP_PUB) == compress(CV_PUB, M_PUB) and MP_PUB != M_PUB),
                "published_w16_is_g": int(expand(MP_PUB)[16] == G16), "published_w17": int(expand(MP_PUB)[17] == W17PUB),
                "kernel_records": len(A.ks[0]["recs"]), "claw_ops": A.m.o - o0}
    rnd = random.Random(sd)
    cv = [rnd.getrandbits(32) for _ in range(8)]
    a0 = rnd.getrandbits(32) & ~1; u = rnd.getrandbits(32) | 1
    c = consts(cv)
    a1 = recover_a1(cv, a0, u); W = build(cv, a0, a1); V = second(W)
    A1, E1, _ = traj(cv, W); A2, E2, _ = traj(cv, V)
    return {"transplant_ok": int(A1[6:20] == BA[6:20] and E1[10:20] == BE[10:20] and A2[6:20] == CA[6:20] and E2[10:20] == CE[10:20]),
            "w1_is_u": int(W[1] == u), "w16_identity": int(((expand(W)[16] - G16) & M) == ((fstep(u, c) - fstep(a0, c)) & M))}

def _e2(i, sd):
    """r39-window-small.  Trial 0: one window of the program (folded variant, every parameter of P unchanged, check mode) on a random first block,
    cut to 2^22 walk evaluations (16384 iterations of 256 lanes) instead of 2^26.  Every claw is checked against the construction."""
    if i != 0: return None
    A = Attack(win=1 << 22, seed=sd, check=True, fold=True)
    A.run_window()
    st = A.st
    return {"iterations": st["iters"], "dp_hits": st["hits"], "matches": st["matches"], "stage2_iterations": st["s2iters"], "raw_claws": st["raw"],
            "opposite_parity": st["opp"], "distinct_claws": st["claws_distinct"], "passed_f9": st["f9"], "passed_f8": st["f8"], "passed_w17": st["w17"],
            "kernel_records": len(A.ks[0]["recs"]), "ops": A.m.o, "generator_ops": A.m.cat.get("generator", 0)}

def serve():
    req = json.load(sys.stdin)
    eid = req["experiment_id"]
    if eid not in GEN_EXPERIMENTS: raise SystemExit("unknown experiment id")
    fn = _e1 if eid == GEN_EXPERIMENTS[0] else _e2
    rows = []
    for t in req["trials"]:
        obs = fn(t["trial"], int(t["seed"][:16], 16))
        row = {"trial": t["trial"], "message_a_hex": None, "message_b_hex": None}
        if obs: row["observations"] = obs
        rows.append(row)
    sys.stdout.write(json.dumps({"schema_version": 1, "trials": rows}, sort_keys=True, separators=(",", ":")) + "\n")

def main():
    a = sys.argv[1:]
    if "--gen-c" in a: sys.stdout.write(GEN_C); return
    if "--windows" in a:
        nwin = int(a[a.index("--windows") + 1]); seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 1; res = []
        for w in range(nwin):
            A = Attack(win=P.WIN, seed=seed * 1000 + w, check="--check" in a, fold="--nofold" not in a)
            t = time.time(); A.run_window()
            st = dict(A.st); st.update(ops=A.m.o, cat=dict(A.m.cat), blk=dict(A.m.blk), sec=time.time() - t, kernel_len=len(A.ks[0]["recs"]),
                                       kernel_nreg=max(A.ks[0]["nreg"], A.ks[1]["nreg"]), distinct_claws=len(A.distinct), seed=seed * 1000 + w)
            res.append(st)
            print("window %d: %d distinct claws, %d operations, %.1f per claw" % (w, st["distinct_claws"], st["ops"], st["ops"] / max(1, st["distinct_claws"])), flush=True)
        if "--out" in a: json.dump(res, open(a[a.index("--out") + 1], "w"))
        return
    if "--attack" in a:                                       # the attack: windows until a success, then print the two messages
        seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 1; w = 0
        while True:
            A = Attack(win=P.WIN, seed=seed * 1000 + w, check=False, fold=True); A.run_window(); w += 1
            for M1, M2 in getattr(A, "messages", []):
                print("collision", "".join("%08x" % x for x in M1), "".join("%08x" % x for x in M2), flush=True); return
    serve()

if __name__ == "__main__":
    main()
