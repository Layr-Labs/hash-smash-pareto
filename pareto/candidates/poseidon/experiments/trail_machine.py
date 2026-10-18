"""Trail machine for the Orchard Poseidon r56 collision search (declared experiment program, P56).

Contents: the Pallas field and the deployed Orchard constants (embedded); a re-implementation of the
organizer's reference digest (verifier/poseidon.py), checked against three organizer test vectors;
the input line on which the first two full rounds are affine (two-round bypass, Bariant-Bouvier-
Leurent-Perrin, ToSC 2022); the equivalent-form step program of 808 field operations (sparse partial
rounds of Grassi et al., USENIX Security 2021, with the lane scaling and hidden-lane basis described
in the public r48 entry 7f88498e of Jbenisek, re-implemented here); the complete search program of
proof Section 4 as an instruction listing executed by a counting interpreter; deterministic
control-flow fixtures; and the organizer-trial loop, which runs the listing on the real step program
at a reduced output width and returns message pairs whose digests agree on the low width bits.
The organizer runner verifies the returned pairs with its own digest. All randomness of a trial is
derived from the organizer's trial seed. No probability is inferred from the trial frequencies.
"""
import base64
import hashlib
import json
import sys

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
CAP = 1 << 65
ROUNDS = 56
EXPERIMENT = "poseidon-orchard-r56-trail-machine-w11-v1"
WIDTH = 11
# The submitted full-width parameters (proof Section 4.1). The structural counts reported below are those of the
# submitted program: unrolling, table capacity and the resulting image and register-file sizes.
FULL = dict(U=16, MCAP=27997, T=54556)
# Deployed halo2_poseidon 0.2.0 P128Pow5T3 constants (pareto/orchard-pallas-constants.json): 64 rows of three
# round constants, then the 3 x 3 MDS, each a 32-byte big-endian word; sha256 of the 6,432 bytes starts 4d1e1a57.
_B64 = ("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")
_RAW = base64.b64decode(_B64)
assert len(_RAW) == 32 * (64 * 3 + 9) and hashlib.sha256(_RAW).hexdigest().startswith("4d1e1a57")
_W = [int.from_bytes(_RAW[32 * i:32 * i + 32], "big") for i in range(64 * 3 + 9)]
RC = [tuple(_W[3 * r:3 * r + 3]) for r in range(64)]
MDS = [tuple(_W[192 + 3 * i:192 + 3 * i + 3]) for i in range(3)]
INV5 = pow(5, -1, P - 1)
M254 = (1 << 254) - 1
M128 = (1 << 128) - 1
HI = ((1 << 256) - 1) ^ M128


def inv(a):
    return pow(a, P - 2, P)


def root5(a):
    return pow(a, INV5, P)


# ---------------------------------------------------------------- reference digest (organizer semantics)
def permute(state, rounds=ROUNDS):
    s = list(state)
    for idx in (*range(4), *range(4, 4 + rounds), *range(60, 64)):
        s = [(x + c) % P for x, c in zip(s, RC[idx])]
        for col in (range(3) if idx < 4 or idx >= 60 else range(1)):
            s[col] = pow(s[col], 5, P)
        s = [sum(c * x for c, x in zip(row, s)) % P for row in MDS]
    return s


def digest_int(m0, m1, rounds=ROUNDS):
    return permute([m0, m1, CAP], rounds)[0]


# organizer digests (verifier/poseidon.py at r = 56) of (1, 2), (0, 0) and (p - 1, 12345), little-endian hex
_TV = {(1, 2): "4ce3bd9407dc758983c62390ce00463beb82796eb0d40a0398993cb4eca55535",
       (0, 0): "7a515983cec6c21e27c2f24fbc31c54d698400d33300ebc7f4677cb71b529403",
       (P - 1, 12345): "c19db44945c5e58109f002197cbf981817dec320900365402b22ff8350dba538"}
for (a_, b_), h_ in _TV.items():
    assert digest_int(a_, b_) == int.from_bytes(bytes.fromhex(h_), "little"), "reference digest mismatch"


# ---------------------------------------------------------------- the input line
def line():
    """Round 0 maps (m0, m1) to U = (m0 + c00)^5, V = (m1 + c01)^5 and the constant K; the round-1 S-box
    input is affine in (U, V). On (U, V) = (U0 + a tau, V0 + b tau) its lane 0 is constant and lanes 1, 2 are
    d_i tau, so after the round-1 S-boxes the state is A + W B with W = tau^5."""
    k0 = pow((CAP + RC[0][2]) % P, 5, P)
    base = [(MDS[i][2] * k0 + RC[1][i]) % P for i in range(3)]
    a, b = MDS[0][1], (-MDS[0][0]) % P
    det = (MDS[1][0] * MDS[2][1] - MDS[2][0] * MDS[1][1]) % P
    u0 = (-base[1] * MDS[2][1] + base[2] * MDS[1][1]) * inv(det) % P
    v0 = (-MDS[1][0] * base[2] + MDS[2][0] * base[1]) * inv(det) % P
    for i in (1, 2):
        assert (MDS[i][0] * u0 + MDS[i][1] * v0 + base[i]) % P == 0
    return a, b, u0, v0


LA, LB, LU0, LV0 = line()


def message_elems(w):
    tau = root5(w)
    return (root5((LU0 + LA * tau) % P) - RC[0][0]) % P, (root5((LV0 + LB * tau) % P) - RC[0][1]) % P


def message_bytes(w):
    m0, m1 = message_elems(w)
    return m0.to_bytes(32, "little") + m1.to_bytes(32, "little")


def after_round1(m0, m1):
    return permute_rounds([m0, m1, CAP], (0, 1))


def permute_rounds(state, idxs):
    s = list(state)
    for idx in idxs:
        s = [(x + c) % P for x, c in zip(s, RC[idx])]
        for col in (range(3) if idx < 4 or idx >= 60 else range(1)):
            s[col] = pow(s[col], 5, P)
        s = [sum(c * x for c, x in zip(row, s)) % P for row in MDS]
    return s


# ---------------------------------------------------------------- the step program (808 field operations)
def build_step(rounds=ROUNDS):
    """Straight-line program of ADD/MUL on named registers computing x := F(x) = digest(message(x + rho0)) / OUTSCALE.
    Lanes are held divided by known scales; the two hidden lanes of the partial rounds are held in a basis that
    absorbs the linear layer. Returns (prog, constants, E0, OUTSCALE)."""
    A = after_round1(*message_elems(0))
    A1 = after_round1(*message_elems(1))
    B = [(A1[i] - A[i]) % P for i in range(3)]
    assert all(B)
    # proof Section 2: on the line the state after round 1 is A + W B; checked at fixed points
    for w_ in (2, 3, 5, P - 1, (P - 1) // 2):
        assert after_round1(*message_elems(w_)) == [(A[i] + w_ * B[i]) % P for i in range(3)]
    prog, kval = [], {}

    def k(v):
        name = "k%d" % len(kval)
        kval[name] = v % P
        return name

    def op(o, d, s, t):
        prog.append((o, d, s, t))

    def pow5(d, s):
        op("MUL", "sq", s, s)
        op("MUL", "sq", "sq", "sq")
        op("MUL", d, "sq", s)

    def lin_norm(sig, cnext, src, dst):
        lam = []
        for i in range(3):
            g = [MDS[i][j] * sig[j] % P for j in range(3)]
            assert g[0]
            gi = inv(g[0])
            op("MUL", "t1", src[1], k(g[1] * gi))
            op("MUL", "t2", src[2], k(g[2] * gi))
            op("ADD", dst[i], src[0], "t1")
            op("ADD", dst[i], dst[i], "t2")
            if cnext is not None:
                op("ADD", dst[i], dst[i], k(cnext[i] * gi))
            lam.append(g[0])
        return lam

    Y, Z = ["y0", "y1", "y2"], ["z0", "z1", "z2"]
    E0 = [(A[i] + RC[2][i]) * inv(B[i]) % P for i in range(3)]
    for i in range(3):
        op("ADD", Y[i], "x", "e%d" % i)
    sig = [pow(B[i], 5, P) for i in range(3)]
    for i in range(3):
        pow5(Z[i], Y[i])
    lam = lin_norm(sig, RC[3], Z, Y)
    sig = [pow(v, 5, P) for v in lam]
    for i in range(3):
        pow5(Z[i], Y[i])
    G = [[MDS[i][j] * sig[j] % P for j in range(3)] for i in range(3)]
    g0 = inv(G[0][0])
    op("MUL", "t1", Z[1], k(G[0][1] * g0))
    op("MUL", "t2", Z[2], k(G[0][2] * g0))
    op("ADD", "h0", Z[0], "t1")
    op("ADD", "h0", "h0", "t2")
    M22 = [[MDS[1][1], MDS[1][2]], [MDS[2][1], MDS[2][2]]]
    M22r = [[1, 0], [0, 1]]
    for _ in range(rounds):
        M22r = [[(M22[i][0] * M22r[0][j] + M22[i][1] * M22r[1][j]) % P for j in range(2)] for i in range(2)]
    Pm = []
    for i in range(2):
        v = [(M22r[i][0] * G[1][j] + M22r[i][1] * G[2][j]) % P for j in range(3)]
        assert v[0]
        nu = inv(v[0])
        op("MUL", "t1", Z[1], k(v[1] * nu))
        op("MUL", "t2", Z[2], k(v[2] * nu))
        op("ADD", "h%d" % (1 + i), Z[0], "t1")
        op("ADD", "h%d" % (1 + i), "h%d" % (1 + i), "t2")
        Pm.append([nu * M22r[i][0] % P, nu * M22r[i][1] % P])
    dp = (Pm[0][0] * Pm[1][1] - Pm[0][1] * Pm[1][0]) % P
    assert dp
    dpi = inv(dp)
    Q = [[Pm[1][1] * dpi % P, (-Pm[0][1]) * dpi % P], [(-Pm[1][0]) * dpi % P, Pm[0][0] * dpi % P]]
    lam0, gamma, q = G[0][0], 0, [0, 0]
    for rr in range(rounds):
        c = RC[4 + rr]
        op("ADD", "u", "h0", k((gamma + c[0]) * inv(lam0)))
        pow5("x5", "u")
        l5 = pow(lam0, 5, P)
        q = [(q[0] + c[1]) % P, (q[1] + c[2]) % P]
        alpha = MDS[0][0] * l5 % P
        beta = [(MDS[0][1] * Q[0][j] + MDS[0][2] * Q[1][j]) % P for j in range(2)]
        gamma = (MDS[0][1] * q[0] + MDS[0][2] * q[1]) % P
        Qn = [[(MDS[1 + i][1] * Q[0][j] + MDS[1 + i][2] * Q[1][j]) % P for j in range(2)] for i in range(2)]
        q = [(MDS[1 + i][1] * q[0] + MDS[1 + i][2] * q[1]) % P for i in range(2)]
        dt = (Qn[0][0] * Qn[1][1] - Qn[0][1] * Qn[1][0]) % P
        assert alpha and dt
        di = inv(dt)
        v = [MDS[1][0] * l5 % P, MDS[2][0] * l5 % P]
        w = [(Qn[1][1] * v[0] - Qn[0][1] * v[1]) * di % P, (-Qn[1][0] * v[0] + Qn[0][0] * v[1]) * di % P]
        ai = inv(alpha)
        op("MUL", "t1", "h1", k(beta[0] * ai))
        op("MUL", "t2", "h2", k(beta[1] * ai))
        op("ADD", "h0", "x5", "t1")
        op("ADD", "h0", "h0", "t2")
        op("MUL", "t1", "x5", k(w[0]))
        op("ADD", "h1", "h1", "t1")
        op("MUL", "t2", "x5", k(w[1]))
        op("ADD", "h2", "h2", "t2")
        lam0, Q = alpha, Qn
    c = RC[60]
    op("ADD", Y[0], "h0", k((gamma + c[0]) * inv(lam0)))
    sig = [pow(lam0, 5, P)]
    assert Q[0][1] == 0 and Q[1][0] == 0 and Q[0][0] and Q[1][1]
    for i in range(2):
        gi = inv(Q[i][i])
        op("ADD", Y[1 + i], "h%d" % (1 + i), k((q[i] + c[1 + i]) * gi))
        sig.append(pow(Q[i][i], 5, P))
    for rd in (60, 61, 62):
        for i in range(3):
            pow5(Z[i], Y[i])
        lam = lin_norm(sig, RC[rd + 1], Z, Y)
        sig = [pow(v, 5, P) for v in lam]
    for i in range(3):
        pow5(Z[i], Y[i])
    G0 = [MDS[0][j] * sig[j] % P for j in range(3)]
    gi = inv(G0[0])
    op("MUL", "t1", Z[1], k(G0[1] * gi))
    op("MUL", "t2", Z[2], k(G0[2] * gi))
    op("ADD", "x", Z[0], "t1")
    op("ADD", "x", "x", "t2")
    return prog, kval, E0, G0[0]


STEP, KVAL, E0, OUTSCALE = build_step()
STEP_OPS = len(STEP)
STEP_ADD = sum(1 for o in STEP if o[0] == "ADD")
STEP_MUL = STEP_OPS - STEP_ADD
NCONST = len(KVAL)
STEP_REGS = sorted({r for o in STEP for r in o[1:]})
assert STEP_OPS == 136 + 12 * ROUNDS == 808 and STEP_ADD == 330 and NCONST == 327
_IDX = {r: i for i, r in enumerate(STEP_REGS)}
_CODE = tuple((o == "MUL", _IDX[d], _IDX[s], _IDX[t]) for o, d, s, t in STEP)
STEP_SHA = hashlib.sha256(repr(STEP).encode()).hexdigest()


def make_F(rho0):
    """F(x) = digest(message(x + rho0)) / OUTSCALE by executing every operation of STEP once."""
    R = [0] * len(STEP_REGS)
    for name, v in KVAL.items():
        R[_IDX[name]] = v
    for i in range(3):
        R[_IDX["e%d" % i]] = (E0[i] + rho0) % P
    ix = _IDX["x"]

    def F(x):
        R[ix] = x
        for m, d, s, t in _CODE:
            R[d] = R[s] * R[t] % P if m else (R[s] + R[t]) % P
        return R[ix]
    return F


# ---------------------------------------------------------------- the search program (proof Section 4)
# Registers (control): names below; step registers: STEP_REGS. Constants live in memory words and are
# loaded once per attempt. Instruction formats: STEP words 4 bytes (3 register fields of 9 bits and a
# 1-bit opcode); control instructions 8 bytes (opcode, up to three 9-bit register fields, 32-bit immediate).
CTRL_REGS = ["r", "rho", "I", "CNT", "END", "dlow", "f", "g", "p", "v", "xh", "idx", "o", "wq", "a", "sw", "sh",
             "c", "HP", "HIDX", "va", "aidx", "L", "q", "vs", "sidx", "t", "lo", "hi", "m", "j", "A", "B", "nA", "nB",
             "W", "e", "x0r", "racc", "rbase", "rex", "rbit", "mout"]
# constant registers (loaded from the constant area): M254, M128, HI, TW, BS, GM, MCAPR, TAB0, TAB1, SIDE, SIDEND,
# C32, ZERO, CU, E0_0..E0_2, LA, LB, LU0, LV0, INV5R, c00, c01, OUT0 (output area), and the NCONST step constants
CONST_REGS = ["M254", "M128", "HIR", "TW", "BS", "GM", "MCAPR", "TAB0", "TAB1", "SIDE", "SIDEND", "C32", "ZERO", "CU",
              "E00", "E01", "E02", "LAR", "LBR", "LU0R", "LV0R", "INV5R", "C00", "C01", "OUT0", "ONE"]


def build_program(U):
    """Instruction listing with labels. Each tuple is one instruction; 'STEP' stands for the 808 step words."""
    L = []
    lab = {}

    def emit(*ins):
        L.append(ins)

    def label(name):
        lab[name] = len(L)
    # constant loads: step constants k0..k(NCONST-1) then the control constants, from the constant area
    for i, name in enumerate(list(KVAL) + CONST_REGS):
        emit("LOADI", name, i)                      # load constant word i into its register
    emit("RAND", "r"); emit("AND", "rho", "r", "M254")
    emit("RAND", "r"); emit("AND", "x", "r", "M254")
    emit("MOV", "x0r", "x"); emit("STORE", "TAB0", "x")
    for i in range(3):
        emit("ADD", "e%d" % i, "E0%d" % i, "rho")
    emit("MOVI", "I", 0); emit("MOVI", "CNT", 0); emit("MOV", "END", "TAB1"); emit("MOV", "a", "SIDE")
    label("zero")
    emit("STORE", "a", "ZERO"); emit("ADD", "a", "a", "C32"); emit("CMPLT", "g", "a", "SIDEND"); emit("BR", "g", "zero")
    label("block")
    for s in range(U):
        label("slot%d" % s)
        emit("STEP")
        emit("AND", "dlow", "x", "M128"); emit("CMPLT", "f", "dlow", "TW"); emit("BR", "f", "dp%d" % s)
        label("next%d" % s)
    emit("ADD", "I", "I", "CU"); emit("CMPLT", "g", "I", "BS"); emit("BR", "g", "block"); emit("HALT", 1)
    for s in range(U):
        label("dp%d" % s)
        emit("ADDI", "idx", "I", s + 1); emit("AND", "xh", "x", "HIR"); emit("MOV", "p", "TAB1")
        label("scan%d" % s)                           # bound first: only stored entries [TAB1, END) are examined
        emit("CMPLT", "g", "p", "END"); emit("BR", "g", "body%d" % s)
        emit("CMPLT", "c", "CNT", "MCAPR"); emit("BR", "c", "ins%d" % s); emit("HALT", 2)
        label("body%d" % s)
        emit("LOAD", "v", "p"); emit("AND", "v", "v", "HIR"); emit("CMPEQ", "f", "v", "xh"); emit("BR", "f", "low%d" % s)
        label("adv%d" % s)
        emit("ADD", "p", "p", "C32"); emit("JMP", "scan%d" % s)
        label("low%d" % s)
        emit("SUB", "o", "p", "TAB1"); emit("SHRI", "wq", "o", 9); emit("SHLI", "wq", "wq", 5); emit("ADD", "a", "SIDE", "wq")
        emit("LOAD", "sw", "a"); emit("ANDI", "sh", "o", 480); emit("SHRI", "sh", "sh", 1); emit("SHR", "sw", "sw", "sh")
        emit("ANDI", "sw", "sw", 65535); emit("CMPEQ", "f", "sw", "dlow"); emit("BR", "f", "hit%d" % s); emit("JMP", "adv%d" % s)
        label("ins%d" % s)
        emit("OR", "v", "xh", "idx"); emit("STORE", "END", "v"); emit("SUB", "o", "END", "TAB1"); emit("ADD", "END", "END", "C32")
        emit("SHRI", "wq", "o", 9); emit("SHLI", "wq", "wq", 5); emit("ADD", "a", "SIDE", "wq"); emit("LOAD", "sw", "a")
        emit("ANDI", "sh", "o", 480); emit("SHRI", "sh", "sh", 1); emit("SHL", "v", "dlow", "sh"); emit("OR", "sw", "sw", "v")
        emit("STORE", "a", "sw"); emit("ADDI", "CNT", "CNT", 1); emit("JMP", "next%d" % s)
        label("hit%d" % s)
        emit("MOV", "HP", "p"); emit("MOV", "HIDX", "idx"); emit("JMP", "recover")
    # ---- recovery (proof Section 5): repeat of entry HP (stored index aidx) at index HIDX
    label("recover")
    emit("LOAD", "va", "HP"); emit("AND", "aidx", "va", "M128"); emit("SUB", "L", "HIDX", "aidx")
    emit("CMPEQ", "f", "HP", "TAB1"); emit("BR", "f", "fromstart")
    # previous stored entry: value = (word AND HI) OR its 16-bit side field, index = word AND M128
    emit("SUB", "q", "HP", "C32"); emit("LOAD", "vs", "q"); emit("AND", "sidx", "vs", "M128"); emit("AND", "A", "vs", "HIR")
    emit("SUB", "o", "q", "TAB1"); emit("SHRI", "wq", "o", 9); emit("SHLI", "wq", "wq", 5); emit("ADD", "a", "SIDE", "wq")
    emit("LOAD", "sw", "a"); emit("ANDI", "sh", "o", 480); emit("SHRI", "sh", "sh", 1); emit("SHR", "sw", "sw", "sh")
    emit("ANDI", "sw", "sw", 65535); emit("OR", "A", "A", "sw"); emit("JMP", "target")
    label("fromstart")
    emit("MOV", "A", "x0r"); emit("MOVI", "sidx", 0)
    label("target")
    emit("ADD", "t", "sidx", "L")                    # target index t = s + L (integer addition of indices)
    # bisection over the start word and every stored entry [TAB1, END) for the entry with the largest index <= t
    # (all stored indices are below the repeat index b, and t < b); lo and hi are word addresses, hi exclusive
    emit("MOV", "lo", "TAB0"); emit("MOV", "hi", "END")
    label("bis")
    emit("ADD", "m", "lo", "hi"); emit("SHRI", "m", "m", 6); emit("SHLI", "m", "m", 5)         # middle word address
    emit("CMPEQ", "f", "m", "lo"); emit("BR", "f", "bisdone")                                   # hi - lo <= 32: done
    emit("LOAD", "v", "m"); emit("AND", "v", "v", "M128"); emit("CMPLE", "f", "v", "t"); emit("BR", "f", "bislo")
    emit("MOV", "hi", "m"); emit("JMP", "bis")
    label("bislo")
    emit("MOV", "lo", "m"); emit("JMP", "bis")
    label("bisdone")
    # entry lo holds the start (TAB0) or a stored DP with index <= t: reconstruct (x_e, e) into (x, j)
    emit("CMPEQ", "f", "lo", "TAB0"); emit("BR", "f", "wstart")
    emit("LOAD", "vs", "lo"); emit("AND", "j", "vs", "M128"); emit("AND", "x", "vs", "HIR")
    emit("SUB", "o", "lo", "TAB1"); emit("SHRI", "wq", "o", 9); emit("SHLI", "wq", "wq", 5); emit("ADD", "a", "SIDE", "wq")
    emit("LOAD", "sw", "a"); emit("ANDI", "sh", "o", 480); emit("SHRI", "sh", "sh", 1); emit("SHR", "sw", "sw", "sh")
    emit("ANDI", "sw", "sw", 65535); emit("OR", "x", "x", "sw"); emit("JMP", "walk")
    label("wstart")
    emit("MOV", "x", "x0r"); emit("MOVI", "j", 0)
    label("walk")                                     # walk from (x, j) to index t, at most GM steps
    emit("MOVI", "e", 0)
    label("wloop")
    emit("CMPLT", "g", "j", "t"); emit("BR", "g", "wstep"); emit("JMP", "lock0")
    label("wstep")
    emit("CMPLT", "g", "e", "GM"); emit("BR", "g", "wgo"); emit("HALT", 4)
    label("wgo")
    emit("STEP"); emit("ADDI", "j", "j", 1); emit("ADDI", "e", "e", 1); emit("JMP", "wloop")
    label("lock0")
    emit("MOV", "B", "x"); emit("CMPEQ", "f", "A", "B"); emit("BR", "f", "halt3"); emit("MOVI", "j", 0)
    label("lock")
    emit("CMPLT", "g", "j", "GM"); emit("BR", "g", "lockgo"); emit("HALT", 5)
    label("lockgo")
    emit("MOV", "x", "A"); emit("STEP"); emit("MOV", "nA", "x"); emit("MOV", "x", "B"); emit("STEP"); emit("MOV", "nB", "x")
    emit("CMPEQ", "f", "nA", "nB"); emit("BR", "f", "found")
    emit("MOV", "A", "nA"); emit("MOV", "B", "nB"); emit("ADDI", "j", "j", 1); emit("JMP", "lock")
    label("halt3")
    emit("HALT", 3)
    label("found")                                    # A != B with F(A) = F(B): the two messages

    def root5_inline(dst, src, tag):
        """x^INV5 by right-to-left square and multiply, emitted as ordinary instructions of the machine: three
        to set up, eight per exponent bit for either bit value (the zero-bit case jumps over the multiply), three
        to leave the loop and one to place the result. INV5 has 254 bits, so a call is 3 + 8 * 254 + 4 = 2,039
        operations and twelve instructions of code."""
        emit("MOV", "racc", "ONE"); emit("MOV", "rbase", src); emit("MOV", "rex", "INV5R")
        label("r5loop" + tag)
        emit("CMPLT", "g", "ZERO", "rex"); emit("BR", "g", "r5body" + tag); emit("JMP", "r5done" + tag)
        label("r5body" + tag)
        emit("ANDI", "rbit", "rex", 1); emit("BR", "rbit", "r5mul" + tag); emit("JMP", "r5sq" + tag)
        label("r5mul" + tag)
        emit("MUL", "racc", "racc", "rbase")
        label("r5sq" + tag)
        emit("MUL", "rbase", "rbase", "rbase"); emit("SHRI", "rex", "rex", 1); emit("JMP", "r5loop" + tag)
        label("r5done" + tag)
        emit("MOV", dst, "racc")

    for reg, out in (("A", 0), ("B", 2)):
        emit("ADD", "W", reg, "rho")                  # W = A + rho0 (field addition)
        root5_inline("t", "W", "tau" + reg)           # tau = W^(1/5)
        emit("MUL", "mout", "LAR", "t"); emit("ADD", "mout", "mout", "LU0R")
        root5_inline("mout", "mout", "u" + reg); emit("SUB", "mout", "mout", "C00")
        emit("ADDI", "a", "OUT0", 32 * out); emit("STORE", "a", "mout")
        emit("MUL", "mout", "LBR", "t"); emit("ADD", "mout", "mout", "LV0R")
        root5_inline("mout", "mout", "v" + reg); emit("SUB", "mout", "mout", "C01")
        emit("ADDI", "a", "OUT0", 32 * (out + 1)); emit("STORE", "a", "mout")
    emit("HALT", 0)
    return L, lab


MESSAGE_OPS = 6 * (3 + 8 * INV5.bit_length() + 4) + 16     # six fifth roots plus the surrounding arithmetic


def code_bytes(prog, U):
    """Image size: four bytes per step word (three 9-bit register fields and one opcode bit) and eight bytes per
    control instruction. Every instruction the listing can execute is counted, the fifth-root loops included."""
    nstep = sum(1 for ins in prog if ins[0] == "STEP")
    nctrl = len(prog) - nstep
    return nstep * STEP_OPS * 4 + nctrl * 8, nstep, nctrl


class Machine:
    """Executes the listing. Every executed instruction is one word operation except STEP, which is STEP_OPS field
    operations. Field ADD/SUB/MUL act modulo p; index arithmetic (ADDI, SUB of indices, comparisons) acts on
    256-bit integers, and the registers holding indices never exceed 2^128."""

    def __init__(self, prog, lab, consts, mem_layout, stepfn, randfn):
        self.prog, self.lab, self.consts, self.lay = prog, lab, consts, mem_layout
        self.stepfn, self.randfn = stepfn, randfn
        self.trail_pcs = {i for i in range(lab["block"], lab["dp0"]) if prog[i][0] == "STEP"}
        self.walk_pc = lab["wgo"]
        self.dp_pcs = {lab["dp%d" % s] for s in range(len([k for k in lab if k.startswith("dp")]))}
        self.scan_pcs = {lab["scan%d" % s] for s in range(len(self.dp_pcs))}

    def run(self, max_ops=None):
        R = {name: 0 for name in CTRL_REGS + CONST_REGS + STEP_REGS}
        mem = {}
        ops = {"ctrl": 0, "load": 0, "store": 0, "rand": 0, "step": 0}
        stat = {"trail_steps": 0, "dp_events": 0, "scanned": 0, "walk_steps": 0, "lock_steps": 0}
        pc, code = 0, None
        while True:
            ins = self.prog[pc]
            op = ins[0]
            if pc in self.dp_pcs:
                stat["dp_events"] += 1
            if pc in self.scan_pcs:
                stat["scanned"] += 1
            if op == "STEP":
                R["x"] = self.stepfn(R["x"])
                ops["step"] += 1
                if pc in self.trail_pcs:
                    stat["trail_steps"] += 1
                elif pc == self.walk_pc:
                    stat["walk_steps"] += 1
                else:
                    stat["lock_steps"] += 1
                pc += 1
                continue
            pc += 1
            ops["ctrl"] += 1
            if op == "LOADI":
                R[ins[1]] = self.consts[ins[2]]
                ops["load"] += 1; ops["ctrl"] -= 1
            elif op == "LOAD":
                R[ins[1]] = mem.get(R[ins[2]], 0)
                ops["load"] += 1; ops["ctrl"] -= 1
            elif op == "STORE":
                mem[R[ins[1]]] = R[ins[2]]
                ops["store"] += 1; ops["ctrl"] -= 1
            elif op == "RAND":
                R[ins[1]] = self.randfn()
                ops["rand"] += 1; ops["ctrl"] -= 1
            elif op == "AND":
                R[ins[1]] = R[ins[2]] & R[ins[3]]
            elif op == "ANDI":
                R[ins[1]] = R[ins[2]] & ins[3]
            elif op == "OR":
                R[ins[1]] = R[ins[2]] | R[ins[3]]
            elif op == "ADD":                         # field addition (operands below p)
                R[ins[1]] = (R[ins[2]] + R[ins[3]]) % P
            elif op == "SUB":                         # field subtraction; for addresses and indices the result is nonnegative
                R[ins[1]] = (R[ins[2]] - R[ins[3]]) % P
            elif op == "MUL":
                R[ins[1]] = R[ins[2]] * R[ins[3]] % P
            elif op == "ADDI":
                R[ins[1]] = R[ins[2]] + ins[3]
            elif op == "MOV":
                R[ins[1]] = R[ins[2]]
            elif op == "MOVI":
                R[ins[1]] = ins[2]
            elif op == "SHRI":
                R[ins[1]] = R[ins[2]] >> ins[3]
            elif op == "SHLI":
                R[ins[1]] = (R[ins[2]] << ins[3]) & ((1 << 256) - 1)
            elif op == "SHR":
                R[ins[1]] = R[ins[2]] >> R[ins[3]]
            elif op == "SHL":
                R[ins[1]] = (R[ins[2]] << R[ins[3]]) & ((1 << 256) - 1)
            elif op == "CMPLT":
                R[ins[1]] = 1 if R[ins[2]] < R[ins[3]] else 0
            elif op == "CMPLE":
                R[ins[1]] = 1 if R[ins[2]] <= R[ins[3]] else 0
            elif op == "CMPEQ":
                R[ins[1]] = 1 if R[ins[2]] == R[ins[3]] else 0
            elif op == "BR":
                if R[ins[1]]:
                    pc = self.lab[ins[2]]
            elif op == "JMP":
                pc = self.lab[ins[1]]
            elif op == "HALT":
                code = ins[1]
                break
            else:
                raise ValueError(op)
            if max_ops is not None and ops["ctrl"] > max_ops:
                raise RuntimeError("operation limit")
        total = ops["ctrl"] + ops["load"] + ops["store"] + ops["rand"] + ops["step"] * STEP_OPS
        out = None
        if code == 0:
            base = R["OUT0"]
            out = [mem[base + 32 * i] for i in range(4)]
        return dict(code=code, ops=ops, total=total, inserted=R["CNT"], trail_index=R["I"], out=out, stat=stat,
                    lock_rounds=R["j"] if code in (0, 5) else 0, regs=R)


def layout(U, MCAP):
    """Memory layout (byte addresses, 32-byte words): start word, table, side array, output, constants."""
    TAB0 = 0
    TAB1 = 32
    SIDE = TAB1 + 32 * MCAP
    nside = -(-MCAP // 16)
    SIDEND = SIDE + 32 * nside
    OUT0 = SIDEND
    CONST = OUT0 + 4 * 32
    return dict(TAB0=TAB0, TAB1=TAB1, SIDE=SIDE, SIDEND=SIDEND, OUT0=OUT0, CONST=CONST, nside=nside)


def constants(p, lay):
    """Constant words in load order: the step constants, then the control constants."""
    vals = list(KVAL.values())
    ctl = dict(M254=M254, M128=M128, HIR=HI, TW=p["T"], BS=p["S"], GM=p["gmax"], MCAPR=p["MCAP"], TAB0=lay["TAB0"],
               TAB1=lay["TAB1"], SIDE=lay["SIDE"], SIDEND=lay["SIDEND"], C32=32, ZERO=0, CU=p["U"],
               E00=E0[0], E01=E0[1], E02=E0[2], LAR=LA, LBR=LB, LU0R=LU0, LV0R=LV0, INV5R=INV5, C00=RC[0][0], C01=RC[0][1],
               OUT0=lay["OUT0"], ONE=1)
    return vals + [ctl[n] for n in CONST_REGS]


def memory_bytes(U, MCAP):
    lay = layout(U, MCAP)
    prog, lab = build_program(U)
    cb, nstep, nctrl = code_bytes(prog, U)
    nconst = NCONST + len(CONST_REGS)
    nreg = len(CTRL_REGS) + len(CONST_REGS) + len(STEP_REGS)
    data = lay["CONST"] + 32 * nconst
    return dict(code=cb, data=data, registers=32 * nreg, total=cb + data + 32 * nreg, nstep=nstep, nctrl=nctrl, nreg=nreg)


# ---------------------------------------------------------------- reference search (plain model of the algorithm)
def reference_search(F, x0, p, is_dp):
    """The algorithm of proof Section 4 written plainly: one trail, distinguished points, recovery."""
    x, stored, idx = x0, {}, []           # stored: value -> index; idx: list of (index, value) in order
    for i in range(1, p["S"] + 1):
        x = F(x)
        if is_dp(x):
            if x in stored:
                a, b = stored[x], i
                Lc = b - a
                prev = [(k, v) for (k, v) in idx if k < a]
                s, xs = prev[-1] if prev else (0, x0)
                t = s + Lc
                cand = [(k, v) for (k, v) in [(0, x0)] + idx if k <= t]
                e, xe = cand[-1]
                if t - e > p["gmax"]:
                    return 4, None
                y = xe
                for _ in range(t - e):
                    y = F(y)
                if y == xs:
                    return 3, None
                A, B = xs, y
                for _ in range(p["gmax"]):
                    nA, nB = F(A), F(B)
                    if nA == nB:
                        return 0, (A, B)
                    A, B = nA, nB
                return 5, None
            if len(stored) >= p["MCAP"]:
                return 2, None
            stored[x] = i
            idx.append((i, x))
    return 1, None


# ---------------------------------------------------------------- fixtures (synthetic functions, deterministic)
def run_machine(p, stepfn, randfn, consts_override=None):
    lay = layout(p["U"], p["MCAP"])
    prog, lab = build_program(p["U"])
    consts = constants(p, lay)
    if consts_override:
        for k_, v_ in consts_override.items():
            consts[NCONST + CONST_REGS.index(k_)] = v_
    m = Machine(prog, lab, consts, lay, stepfn, randfn)
    return m.run()


def fixtures():
    """Deterministic fixtures: the machine and the plainly written reference must agree on every case, and each
    case pins the termination code it is named for. The maps with a tail (not permutations) are the ones that
    reach the success path and the recovery halts; an affine permutation of a prime field has no tail, so on such
    a map the start always lies on the cycle and the attempt halts with code 3."""
    results = []

    def affine(mod, mul, add):
        return lambda x: (x * mul + add) % mod

    def tabled(d, mod):
        return lambda x: d[x % mod]
    # 0 -> 1 -> 2 -> 3 -> 4 -> 2: a tail of two into a cycle of three
    short = {0: 1, 1: 2, 2: 3, 3: 4, 4: 2}
    # 0 .. 63 with f(i) = i + 1 and f(63) = 5: a tail of five into a cycle of fifty-nine, so that with a
    # threshold of six the only stored points are the first five and the walk to the target index is long
    long_ = {i: i + 1 for i in range(63)}
    long_[63] = 5
    cases = [
        # (name, map, x0, T, S, gmax, MCAP, U, expected code)
        ("success", tabled(short, 5), 0, 5, 64, 9, 8, 1, 0),
        ("success_long", tabled(long_, 64), 0, 6, 128, 58, 8, 1, 0),
        ("budget", affine(251, 5, 3), 7, 32, 4, 400, 64, 4, 1),
        ("table", affine(251, 5, 3), 7, 200, 600, 400, 2, 4, 2),
        ("startcycle", affine(7, 1, 0), 3, 8, 100, 50, 8, 4, 3),
        ("walkcap", tabled(long_, 64), 0, 6, 128, 10, 8, 1, 4),
        ("lockcap", tabled(short, 5), 0, 5, 64, 0, 8, 1, 5),
        ("permutation", affine(1021, 7, 11), 5, 128, 1200, 800, 64, 4, 3),
        ("permutation2", affine(4093, 13, 29), 101, 16, 2400, 1600, 64, 4, 3),
    ]
    for name, f, x0, T, S, gmax, MCAP, U, exp in cases:
        S = -(-S // U) * U
        p = dict(U=U, T=T, S=S, gmax=gmax, MCAP=MCAP)
        seq = iter([0, x0])
        r = run_machine(p, f, lambda: next(seq), {"M254": (1 << 256) - 1})
        code, pair = reference_search(f, x0, p, lambda v: (v & M128) < T)
        ok = r["code"] == code == exp
        if code == 0:
            A, B = r["regs"]["A"], r["regs"]["B"]
            ok = ok and (A, B) == pair and A != B and f(A) == f(B)
        results.append((name, r["code"], code, exp, ok))
    return results


# ---------------------------------------------------------------- organizer trials at reduced width
def width_params(w, U):
    """Reduced-width parameters: the same algorithm with N = 2^w; the random-function budget n_w, DP threshold
    T_w = N / 8, d_w = ceil(9.5 / theta), gmax_w = ceil(19.5 / theta), table capacity 64. These are experiment
    parameters, not a probability claim."""
    import math
    N = 1 << w
    theta = 1 / 8
    T = N // 8
    # the side array packs a distinguished value's low part into 16 bits, so the threshold must stay below 2^16
    assert T < 1 << 16, "reduced-width threshold must stay below 2^16"
    n = math.ceil(math.sqrt(2 * N * math.log(1 / 0.61)))
    d = math.ceil(9.5 / theta)
    S = -(-(n + d) // U) * U
    return dict(U=U, T=T, S=S, gmax=math.ceil(19.5 / theta), MCAP=64, N=N)


def trial(seed_hex, w, U):
    """One organizer trial: rho0 and x0 from the seed; the real step program at output width w; returns the
    machine result and the message pair (digests agree on the low w bits) when the search succeeds."""
    seed = bytes.fromhex(seed_hex)
    words = [int.from_bytes(hashlib.sha256(seed + bytes([i])).digest(), "little") for i in range(2)]
    seq = iter(words)
    p = width_params(w, U)
    mask = (1 << w) - 1

    def randfn():
        return next(seq)
    # the width-w walk: x_w -> (STEP(x_w) * OUTSCALE mod p) mod 2^w with e_i = E0_i + rho0; rho0 is the first coin
    rho0 = words[0] & mask
    F = make_F(rho0)
    memo = {}

    def stepfn(x):
        v = memo.get(x)
        if v is None:
            v = memo[x] = (F(x) * OUTSCALE % P) & mask
        return v
    r = run_machine(p, stepfn, randfn, {"M254": mask})
    # the same search written plainly, on the same map and the same start, must reach the same termination
    code_ref, pair_ref = reference_search(stepfn, words[1] & mask, p, lambda v: v < p["T"])
    r["matches_reference"] = 1 if code_ref == r["code"] and (
        code_ref != 0 or (r["regs"]["A"], r["regs"]["B"]) == pair_ref) else 0
    pair = None
    if r["code"] == 0:
        A, B = r["regs"]["A"], r["regs"]["B"]
        wa, wb = (A + rho0) % P, (B + rho0) % P
        pair = (message_bytes(wa), message_bytes(wb))
        # the machine's own output words are the message elements; they must equal message_bytes
        out = r["out"]
        assert out[0].to_bytes(32, "little") + out[1].to_bytes(32, "little") == pair[0]
        assert out[2].to_bytes(32, "little") + out[3].to_bytes(32, "little") == pair[1]
        da, db = digest_int(*message_elems(wa)), digest_int(*message_elems(wb))
        assert (da ^ db) & mask == 0 and pair[0] != pair[1]
    return r, pair, p


def step_checks(seed_hex, n=2):
    """Checks that STEP times OUTSCALE equals the reference digest of message(x + rho0) at seed-derived points."""
    seed = bytes.fromhex(seed_hex)
    ok = 0
    for i in range(n):
        x = int.from_bytes(hashlib.sha256(seed + b"x" + bytes([i])).digest(), "little") % P
        rho0 = int.from_bytes(hashlib.sha256(seed + b"r" + bytes([i])).digest(), "little") % P
        F = make_F(rho0)
        ok += (F(x) * OUTSCALE % P == digest_int(*message_elems((x + rho0) % P)))
    return ok


def main():
    request = json.load(sys.stdin)
    mask_hex = ((1 << WIDTH) - 1).to_bytes(32, "little").hex()
    event = dict(kind="digest-xor-mask", mask_hex=mask_hex, expected_hex=bytes(32).hex())
    if (request["schema_version"] != 1 or request["experiment_id"] != EXPERIMENT
            or request["target_profile"] != "poseidon-orchard-r56-prefix-v1"
            or request["event"] != event or request["max_message_bytes"] < 64):
        raise ValueError("unexpected organizer request")
    fx = fixtures()
    nfix = sum(1 for f in fx if f[4])
    mb = memory_bytes(FULL["U"], FULL["MCAP"])
    rows = []
    seen = 0
    for t in request["trials"]:
        r, pair, p = trial(t["seed"], WIDTH, FULL["U"])
        sc = step_checks(t["seed"], 1)
        obs = dict(code=r["code"], trail_steps=r["stat"]["trail_steps"], walk_steps=r["stat"]["walk_steps"],
                   lock_rounds=r["lock_rounds"], inserted=r["inserted"], steps_executed=r["ops"]["step"],
                   control_ops=r["ops"]["ctrl"], mem_ops=r["ops"]["load"] + r["ops"]["store"],
                   total_ops=r["total"], step_checks=sc, matches_reference=r["matches_reference"])
        extra = [dict(step_ops=STEP_OPS, step_add=STEP_ADD, step_mul=STEP_MUL, step_constants=NCONST),
                 dict(step_registers=len(STEP_REGS), control_registers=len(CTRL_REGS) + len(CONST_REGS),
                      control_instructions=mb["nctrl"], code_bytes=mb["code"]),
                 dict(step_copies=mb["nstep"], register_file=mb["nreg"], memory_bytes=mb["total"],
                      fixtures_passed=nfix, fixtures_total=len(fx)),
                 dict(step_sha256_high=int(STEP_SHA[:16], 16), message_ops=MESSAGE_OPS, width=WIDTH, S_w=p["S"])]
        if seen < len(extra):
            obs.update(extra[seen])
        seen += 1
        assert len(obs) <= 16
        rows.append(dict(trial=t["trial"], message_a_hex=pair[0].hex() if pair else None,
                         message_b_hex=pair[1].hex() if pair else None, observations=obs))
    json.dump(dict(schema_version=1, trials=rows), sys.stdout, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    main()
