"""hone_layers.py - organizer experiment (python-message-pairs-v1) bearing on premise H-ONE.

The line of proof Section 1 (round-1 S-box input of lane 0 constant). F_L(T') = lane 0 of the state after rounds 2..(1 + L)
of the target permutation, started from the affine state after round 1 (L = 2: rounds 2, 3, degree 25, m = 12;
L = 3: adds partial round 4, degree 125, m = 62). For each organizer seed, a centre c is drawn uniformly from F_p
(rejection sampling of 255-bit words derived from SHA-256(seed)), g_c is the monic odd part of F_L about c (degree m), and
k(c) = deg gcd(g_c, S^((p-1)/2) - 1) is computed exactly (Kronecker-packed products over F_p, reduction modulo g_c by a
precomputed reciprocal of its reversal). To stay well inside the time limit the work is split over experiments that share
this program: 'hone-layers2a', '2b', '2c' compute L = 2 for the trials of index 0, 1, 2 mod 3 respectively (all trials
together), and 'hone-layers3a', '3b', '3c' compute L = 3 for trial indices 0-5, 6-11 and 12-17; every other trial is
reported as skipped. No message pair is claimed: every trial returns null
messages, and k(c) is reported as an observation (H-ONE asks P(1 <= k(c) <= 16) >= 0.3901; the hyperoctahedral law gives
0.39347). Each computed trial also reports `normal` (bearing on premise H-NORMAL): 1 if the remainder sequence of
(g_c, Y - 1) is normal down to deg G, that is deg(Y - 1) = m - 1 and every Euclid step lowers the degree by exactly 1 until
the remainder is 0, else 0; and `max_drop`, the largest degree drop seen.
"""
import sys, json, hashlib
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
E = (P - 1) // 2
E5 = pow(5, -1, P - 1)
inv = lambda x: pow(x % P, P - 2, P)
CONST = {"round_constants": [["0x360d7470611e473d353f628f76d110f34e71162f31003b7057538c2596426303", "0x2bab94d7ae222d135dc3c6c5febfaa314908ac2f12ebe06fbdb74213bf63188b", "0x150c93fef652fb1c2bf03e1a29aa871fef77e7d736766c5d0939d92753cc5dc8"], ["0x3270661e68928b3a955d55db56dc57c103cc0a60141e894e14259dce537782b2", "0x73f116f04122e25a0b7afe4e2057299b407c370f2b5a1ccce9fb9ffc345afb3", "0x2a32ec5c4ee5b1837affd09c1f53f5fd55c9cd2061ae93ca8ebad76fc71554d8"], ["0x270326ee039df19e651e2cfc740628ca634d24fc6e2559f22d8ccbe292efeead", "0x27c6642ac633bc66dc100fe7fcfa54918af895bce012f182a068fc37c182e274", "0x1bdfd8b01401c70ad27f57396989129d710e1fb6ab976a459ca18682e26d7ff9"], ["0x162a14c62f9a89b814b9d6a9c84dd678f4f6fb3f9054d373c832d824261a35ea", "0x2d193e0f76de586b2af6f79e3127feeaac0a1fc71e2cf0c0f79824667b5b6bec", "0x44ca3cc4a85d73b81696ef1104e674f4feff82984990ff85d0bf58dc8a4aa94"], ["0x1cbaf2b371dac6a81d0453416d3e235cb8d9e2d4f314f46f6198785f0cd6b9af", "0x1d5b2777692c205b0e6c49d061b6b5f4293c4ab038fdbbdc343e07610f3fede5", "0x2e9bdbba3dd34bffaa30535bdd749a7e06a9adb0c1e6f962f60e971b8d73b04f"], ["0x2de11886b18011ca8bd5bae36969299fde40fbe26d047b05035a13661f22418b", "0x2e07de1780b8a70d0d5b4a3f1841dcd82ab9395c449be947bc998884ba96a721", "0xf69f1854d20ca0cbbdb63dbd52dad16250440a99d6b8af3825e4c2bb74925ca"], ["0x2eb1b25417fe17670d135dc639fb09a46ce5113507f96de9816c059422dc705e", "0x115cd0a0643cfb988c24cb44c3fab48aff36c661d26cc42db8b1bdf4953bd82c", "0x26ca293f7b2c462d066d7378b999868bbb57ddf14e0f958ade801612311d04cd"], ["0x17bf1b93c4c7e01a2a830aa162412cd90f160bf9f71e967ff5209d14b24820ca", "0x35b41a7ac4f3c571a24f8456369c85dfe03c0354bd8cfd3805c86f2e7dc293c5", "0x3b1480080523c439435927994849bea964e14d3beb2dddde72ac156af435d09e"]], "mds": [["0xab5e5b874a68de7b3d59fbdc8c9ead497d7a0ab23850b56323f2486d7e11b63", "0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e", "0x7c045d5f5e9e5a6d803952bbb364fdfa0a3b71a5fb1573519d1cf25d8e8345d"], ["0x233162630ebf9ed7f8e24f66822c2d9f3a0a464048bd770ad049cdc8d085167c", "0x25cae2599892a8b0b36664548d60957d78f8365c85bbab07402270113e047a2e", "0x22f5b5e1e6081c9774938717989a19579aad3d8262efd83ff84d806f685f747a"], ["0x2e29dd59c64b1037f333aa91c383346421680eabc56bc15dfee7a9944f84dbe4", "0x1d1aab4ec1cd678892d15e7dceef1665cbeaf48b3a0624c3c771effa43263664", "0x3bf763086a18936451e0cbead65516b975872c39b59a31f615639415f6e85ef1"]]}   # rounds 0..7 of the pinned constants


SLOT = 65   # bytes per Kronecker slot: 520 bits > log2(126 * p^2) = 515.0, enough for every product here (degree <= 125)


def pack(a):
    return int.from_bytes(b''.join(x.to_bytes(SLOT, 'little') for x in a), 'little')


def unpack(C, n):
    raw = (C & ((1 << (8 * SLOT * n)) - 1)).to_bytes(n * SLOT, 'little')
    return [int.from_bytes(raw[i * SLOT:(i + 1) * SLOT], 'little') % P for i in range(n)]


def pmul(a, b):
    """product of coefficient lists (low degree first), Kronecker packing with 520-bit slots (SLOT bytes)."""
    if not a or not b:
        return []
    if a is b:
        A = pack(a); return unpack(A * A, 2 * len(a) - 1)
    return unpack(pack(a) * pack(b), len(a) + len(b) - 1)


def pmod(a, g):
    """a mod monic g."""
    a = list(a)
    dg = len(g) - 1
    for i in range(len(a) - 1, dg - 1, -1):
        c = a[i]
        if c:
            for j in range(dg + 1):
                a[i - dg + j] = (a[i - dg + j] - c * g[j]) % P
    a = a[:dg]
    while a and a[-1] == 0:
        a.pop()
    return a


def padd(a, b):
    n = max(len(a), len(b))
    out = [((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % P for i in range(n)]
    while out and out[-1] == 0:
        out.pop()
    return out


def pscal(a, c):
    return [x * c % P for x in a]


def pgcd_deg(a, b):
    """(deg gcd, normal flag, largest degree drop) of the remainder sequence a, b, a mod b, ..."""
    degs = [len(a) - 1, len(b) - 1]
    while b:
        lb = inv(b[-1])
        b = pscal(b, lb)
        a = pmod(a, b) if len(a) >= len(b) else a
        a, b = b, a
        if b:
            degs.append(len(b) - 1)
    drops = [degs[i] - degs[i + 1] for i in range(len(degs) - 1)]
    return len(a) - 1, (1 if all(x == 1 for x in drops) else 0), max(drops) if drops else 0


def reducer(g):
    """reduction modulo monic g (degree d) of polynomials of degree <= 2d - 2, by the reciprocal of the reversal of g."""
    d = len(g) - 1
    rg = g[::-1]
    R = [1]                                   # rg^-1 mod x^(d-1), rg[0] = 1
    for i in range(1, max(d - 1, 1)):
        s = 0
        for j in range(1, min(i, d) + 1):
            s += rg[j] * R[i - j]
        R.append((-s) % P)

    PR, PG = pack(R), pack(g)
    MASK = (1 << (8 * SLOT * (d - 1))) - 1

    def red(a):
        if len(a) <= d:
            return a
        a = a + [0] * (2 * d - 1 - len(a))
        qr = unpack((pack(a[::-1][:d - 1]) * PR) & MASK, d - 1)
        q = qr[::-1]
        qg = unpack(pack(q) * PG, d)
        out = [(a[i] - qg[i]) % P for i in range(d)]
        while out and out[-1] == 0:
            out.pop()
        return out
    return red


def line_poly(L):
    RC = [[int(x, 16) for x in row] for row in CONST['round_constants']]
    M = [[int(x, 16) for x in row] for row in CONST['mds']]
    CAP = 1 << 65; k = 0; i, j = 1, 2
    K5 = pow((CAP + RC[0][2]) % P, 5, P)
    mu5 = (-M[k][0] * inv(M[k][1])) % P
    a, b, e = M[i][0], M[i][1], (-(M[i][2] * K5 + RC[1][i])) % P
    c, d, f = M[j][0], M[j][1], (-(M[j][2] * K5 + RC[1][j])) % P
    det = (a * d - b * c) % P; di = inv(det)
    A0 = ((e * d - b * f) * di) % P; B0 = ((a * f - e * c) * di) % P
    slope = [(M[t][0] + M[t][1] * mu5) % P for t in range(3)]
    constk = (M[k][0] * A0 + M[k][1] * B0 + M[k][2] * K5 + RC[1][k]) % P
    assert slope[k] == 0 and slope[i] and slope[j]
    sb = [[pow(constk, 5, P)] if t == k else [0, pow(slope[t], 5, P)] for t in range(3)]
    st = [[] for _ in range(3)]
    for row in range(3):
        acc = []
        for col in range(3):
            acc = padd(acc, pscal(sb[col], M[row][col]))
        st[row] = acc
    for rr in range(2, 2 + L):
        st = [padd(x, [RC[rr][t]]) for t, x in enumerate(st)]
        for col in (range(3) if rr < 4 else range(1)):
            x = st[col]; x2 = pmul(x, x); x4 = pmul(x2, x2); st[col] = pmul(x4, x)
        new = []
        for row in range(3):
            acc = []
            for col in range(3):
                acc = padd(acc, pscal(st[col], M[row][col]))
            new.append(acc)
        st = new
    return st[0]


def taylor(F, c):
    """coefficients of F(c + s) in s (Horner on polynomials)."""
    out = []
    for coef in reversed(F):
        out = padd(pmul(out, [c, 1]) if out else [], [coef])
    return out


def kc(F, c):
    h = taylor(F, c)
    D = len(F) - 1
    g = [h[2 * j + 1] if 2 * j + 1 < len(h) else 0 for j in range((D - 1) // 2 + 1)]
    g = pscal(g, inv(g[-1]))
    # Y = S^E mod g, left-to-right
    red = reducer(g)
    y = [1]
    for bit in bin(E)[2:]:
        y = red(pmul(y, y)) if y else y
        if bit == '1':
            y = pmod([0] + y, g)
    y1 = padd(y, [P - 1])
    return pgcd_deg(list(g), y1) if y1 else (len(g) - 1, 0, 0)


def centre(seed):
    for j in range(64):
        w = int.from_bytes(hashlib.sha256(seed + bytes([j])).digest(), 'little') & ((1 << 255) - 1)
        if w < P:
            return w
    return None


def main():
    req = json.loads(sys.stdin.read())
    eid = req.get('experiment_id', '')
    part = 'abc'.index(eid[-1]) if eid[-1:] in ('a', 'b', 'c') else 0
    if eid.startswith('hone-layers3'):
        L, todo = 3, lambda idx: 6 * part <= idx < 6 * part + 6
    else:
        L, todo = 2, lambda idx: idx % 3 == part
    F = line_poly(L)
    out = []
    for idx, t in enumerate(req['trials']):
        obs = {}
        if todo(idx):
            c = centre(bytes.fromhex(t['seed']))
            if c is None:
                obs['centre_draw_failed'] = 1
            else:
                obs['k_c'], obs['normal'], obs['max_drop'] = kc(F, c)
                obs['in_range'] = 1 if 1 <= obs['k_c'] <= 16 else 0
        else:
            obs['skipped'] = 1
        out.append({'trial': t['trial'], 'message_a_hex': None, 'message_b_hex': None, 'observations': obs})
    sys.stdout.write(json.dumps({'schema_version': 1, 'trials': out}, separators=(',', ':')))


if __name__ == '__main__':
    main()
