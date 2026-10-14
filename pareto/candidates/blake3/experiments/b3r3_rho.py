"""Bit-sliced parallel collision search on BLAKE3 with rounds 0..2 (blake3-r3-prefix-v1, Pareto track).

Chain step g(x) = f(x) XOR q, f(x) = BLAKE3-r3 digest of the 64-byte message 0^32 || LE32(x) (one chunk, one
block, root), q a fixed 256-bit mask (the digest planes' polarity). 256 trails run as bit planes; the straight
line has XOR, AND and OR only: rotations are renaming, constants and NOT are folded into per-plane polarity,
and every full adder takes the operand of different polarity as pivot, so each bit costs five operations.

  python3 b3r3_rho.py --ledger          operation counts, register peak, mask weight
  python3 b3r3_rho.py --selftest N      step versus the plain compression on N points and chained steps
  python3 b3r3_rho.py --stats T         both experiments on T local trials, with an ideal control
  python3 b3r3_rho.py < request.json    organizer experiment (python-message-pairs-v1)
"""
import hashlib
import json
import struct
import sys

IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
ROUNDS = 3
FLAGS = 1 | 2 | 8          # CHUNK_START | CHUNK_END | ROOT
N_IN = 256
REGS = 1024
LANES = 256
FULL = (1 << LANES) - 1
_Q = 0
M32 = 0xFFFFFFFF


# ---------------------------------------------------------------- reference

def message(x):
    return bytes(32) + x.to_bytes(32, 'little')


def blake3_r3(msg):
    """blake3-r3-prefix-v1 digest of a 64-byte message (one chunk, one block, root)."""
    v = list(IV) + list(IV[:4]) + [0, 0, 64, FLAGS]
    m = list(struct.unpack('<16I', msg))

    def rot(x, n):
        return ((x >> n) | (x << (32 - n))) & M32

    def G(a, b, c, d, x, y):
        v[a] = (v[a] + v[b] + x) & M32; v[d] = rot(v[d] ^ v[a], 16); v[c] = (v[c] + v[d]) & M32; v[b] = rot(v[b] ^ v[c], 12)
        v[a] = (v[a] + v[b] + y) & M32; v[d] = rot(v[d] ^ v[a], 8); v[c] = (v[c] + v[d]) & M32; v[b] = rot(v[b] ^ v[c], 7)
    for _ in range(ROUNDS):
        G(0, 4, 8, 12, m[0], m[1]); G(1, 5, 9, 13, m[2], m[3]); G(2, 6, 10, 14, m[4], m[5]); G(3, 7, 11, 15, m[6], m[7])
        G(0, 5, 10, 15, m[8], m[9]); G(1, 6, 11, 12, m[10], m[11]); G(2, 7, 8, 13, m[12], m[13]); G(3, 4, 9, 14, m[14], m[15])
        m = [m[p] for p in PERM]
    return struct.pack('<8I', *(v[i] ^ v[i + 8] for i in range(8)))


def f_int(x):
    return int.from_bytes(blake3_r3(message(x)), 'little')


# ---------------------------------------------------------------- generator

class Gen:
    """SSA straight line. A logical value is ('c', bit) or ('v', node, polarity); nodes < N_IN are inputs."""

    def __init__(self):
        self.ins = []
        self.memo = {}

    def emit(self, op, a, b):
        key = (op, min(a, b), max(a, b))
        if key not in self.memo:
            self.ins.append((op, a, b))
            self.memo[key] = N_IN + len(self.ins) - 1
        return self.memo[key]

    def xor(self, a, b):
        if a[0] == 'c':
            return b if not a[1] else neg(b)
        if b[0] == 'c':
            return self.xor(b, a)
        if a[1] == b[1]:
            return ('c', a[2] ^ b[2])
        return ('v', self.emit('XOR', a[1], b[1]), a[2] ^ b[2])

    def and_(self, a, b):
        if a[0] == 'c':
            return b if a[1] else ('c', 0)
        if b[0] == 'c':
            return self.and_(b, a)
        (_, na, pa), (_, nb, pb) = a, b
        if na == nb:
            return a if pa == pb else ('c', 0)
        if pa == pb:
            return ('v', self.emit('AND' if pa == 0 else 'OR', na, nb), pa)
        if pa:
            na, nb = nb, na                      # na has polarity 0: na AND NOT nb = na XOR (na AND nb)
        return ('v', self.emit('XOR', na, self.emit('AND', na, nb)), 0)

    def flip(self, a):
        return ('v', self.emit('NOT', a[1], a[1]), a[2] ^ 1)


def neg(a):
    return ('c', a[1] ^ 1) if a[0] == 'c' else ('v', a[1], a[2] ^ 1)


def word(v):
    return [('c', (v >> i) & 1) for i in range(32)]


def build():
    """Three rounds on 256 trails; x fills message words 8..15. Returns (Gen, digest planes)."""
    g = Gen()
    m = [word(0) for _ in range(16)]
    for k in range(8):
        m[8 + k] = [('v', 32 * k + i, 0) for i in range(32)]
    v = [word(x) for x in IV] + [word(x) for x in IV[:4]] + [word(0), word(0), word(64), word(FLAGS)]

    def add(a, b):
        out = []
        carry = ('c', 0)
        for i in range(32):
            trio = [a[i], b[i], carry]
            pols = [t[2] if t[0] == 'v' else None for t in trio]
            piv = 2
            for k in range(3):
                o = [j for j in range(3) if j != k]
                if pols[o[0]] is not None and pols[o[0]] == pols[o[1]]:
                    piv = k
                    break
            x, y = [trio[j] for j in range(3) if j != piv]
            p = trio[piv]
            u = g.xor(x, p)
            out.append(g.xor(u, y))
            if i < 31:
                carry = g.xor(g.and_(u, g.xor(y, p)), p)      # maj(x, y, p)
        return out

    def xorw(a, b):
        return [g.xor(s, t) for s, t in zip(a, b)]

    def rotr(a, n):
        return [a[(i + n) % 32] for i in range(32)]

    def G(a, b, c, d, mx, my):
        v[a] = add(add(v[a], v[b]), mx)
        v[d] = rotr(xorw(v[d], v[a]), 16)
        v[c] = add(v[c], v[d])
        v[b] = rotr(xorw(v[b], v[c]), 12)
        v[a] = add(add(v[a], v[b]), my)
        v[d] = rotr(xorw(v[d], v[a]), 8)
        v[c] = add(v[c], v[d])
        v[b] = rotr(xorw(v[b], v[c]), 7)

    for _ in range(ROUNDS):
        G(0, 4, 8, 12, m[0], m[1]); G(1, 5, 9, 13, m[2], m[3]); G(2, 6, 10, 14, m[4], m[5]); G(3, 7, 11, 15, m[6], m[7])
        G(0, 5, 10, 15, m[8], m[9]); G(1, 6, 11, 12, m[10], m[11]); G(2, 7, 8, 13, m[12], m[13]); G(3, 4, 9, 14, m[14], m[15])
        m = [m[p] for p in PERM]
    out = []
    for i in range(8):
        out += xorw(v[i], v[i + 8])
    return g, out


def step_program():
    """The chain step as instructions (op, dst, a, b) on registers, and the mask q (digest-plane polarity).

    Physical digest plane j is written into register j (input plane j). The next point is the physical value,
    so the walk is g(x) = f(x) XOR q and no NOT is needed."""
    g, outs = build()
    need = set(o[1] for o in outs)
    keep = [False] * len(g.ins)
    for i in range(len(g.ins) - 1, -1, -1):
        if N_IN + i in need:
            keep[i] = True
            need.update(g.ins[i][1:])
    q = [o[2] for o in outs]
    return allocate(g, outs, keep), q


def allocate(g, outs, keep):
    """Registers: input plane j and digest plane j live in register j; temporaries use 256..REGS-1."""
    seq = [(N_IN + i,) + g.ins[i] for i in range(len(g.ins)) if keep[i]]
    last = {}
    for k, (d, op, a, b) in enumerate(seq):
        last[a] = k
        last[b] = k
    out_of = {}
    for j, o in enumerate(outs):
        if o[1] not in out_of and o[1] >= N_IN:
            out_of[o[1]] = j
    reg = {j: j for j in range(N_IN)}
    free = list(range(REGS - 1, N_IN - 1, -1))
    prog = []
    peak = 0
    for k, (d, op, a, b) in enumerate(seq):
        ra, rb = reg[a], reg[b]
        for n in {a, b}:
            if last[n] == k and n not in out_of and n >= N_IN:
                free.append(reg[n])
        if d in out_of:
            rd = out_of[d]
        else:
            if not free:
                raise SystemExit('register file exhausted')
            rd = free.pop()
        reg[d] = rd
        prog.append((op, rd, ra, rb))
        peak = max(peak, REGS - len(free))
    for j, o in enumerate(outs):
        if o[1] not in out_of or out_of[o[1]] != j:
            prog.append(('MOV', j, reg[o[1]], reg[o[1]]))
    allocate.peak = peak
    return prog


def compile_step(prog, chunk=1500):
    """A Python function r -> None executing the straight line on the register list r.

    The straight line is compiled in pieces of `chunk` instructions to bound the compiler's memory."""
    sym = {'XOR': '^', 'AND': '&', 'OR': '|'}
    parts = []
    for start in range(0, len(prog), chunk):
        lines = ['def part(r):', ' F = %d' % FULL]
        for op, d, a, b in prog[start:start + chunk]:
            if op == 'NOT':
                lines.append(f' r[{d}] = r[{a}] ^ F')
            elif op == 'MOV':
                lines.append(f' r[{d}] = r[{a}]')
            else:
                lines.append(f' r[{d}] = r[{a}] {sym[op]} r[{b}]')
        env = {}
        exec(compile('\n'.join(lines), '<step>', 'exec'), env)
        parts.append(env['part'])

    def step(r):
        for part in parts:
            part(r)
    return step


# ---------------------------------------------------------------- planes

def to_planes(points, pol, width=256):
    """Points (ints < 2^width, one per lane) -> 256 physical planes; planes >= width carry logical 0."""
    planes = []
    for j in range(N_IN):
        w = 0
        if j < width:
            for t, x in enumerate(points):
                w |= ((x >> j) & 1) << t
        planes.append(w ^ (FULL if pol[j] else 0))
    return planes


def lane_point(r, pol, t, width=256):
    x = 0
    for j in range(width):
        x |= (((r[j] >> t) & 1) ^ pol[j]) << j
    return x


# ---------------------------------------------------------------- search

class Coins:
    """The search's random words; here SHAKE-256 of a seed, a reproducible stand-in for the primitive."""

    def __init__(self, seed):
        self.xof = hashlib.shake_256(b'sha3r6-rho-coins' + seed).digest(1 << 16)
        self.pos = 0

    def word(self, bits):
        n = (bits + 7) // 8
        if self.pos + n > len(self.xof):
            self.xof = hashlib.shake_256(self.xof[-32:]).digest(1 << 16)
            self.pos = 0
        v = int.from_bytes(self.xof[self.pos:self.pos + n], 'little') & ((1 << bits) - 1)
        self.pos += n
        return v


def search(step, pol, coins, width, dbits, batches, cap, table_cap, f_point=None):
    """One attempt of the 256-lane distinguished-point search on the width-bit chain (proof.md Section 5).

    Trail i starts at R + i mod 2^width for one random word R; a point is distinguished when its dbits
    low physical planes are zero. Returns (pair or None, observations)."""
    mask = (1 << width) - 1
    base = coins.word(width)
    nxt = [LANES]
    starts = [(base + t) & mask for t in range(LANES)]
    lengths = [0] * LANES
    points = list(starts)
    table = {}
    obs = {'batches': 0, 'dps': 0, 'cut': 0, 'merges': 0, 'robin_hood': 0}
    if f_point is None:
        regs = to_planes(points, pol, width) + [0] * (REGS - N_IN)
    for _ in range(batches):
        obs['batches'] += 1
        if f_point is None:
            step(regs)
            for j in range(width, N_IN):         # reduced width: planes above width carry logical 0
                regs[j] = FULL if pol[j] else 0
            w = 0
            for j in range(dbits):
                w |= regs[j]
            hits = [t for t in range(LANES) if not (w >> t) & 1]
        else:
            points = [f_point(p) & mask for p in points]
            hits = [t for t in range(LANES) if all(((points[t] >> j) & 1) == pol[j] for j in range(dbits))]
        for t in range(LANES):
            lengths[t] += 1
        restarts = []
        for t in hits:
            x = lane_point(regs, pol, t, width) if f_point is None else points[t]
            obs['dps'] += 1
            if x in table:
                obs['merges'] += 1
                return recover(table[x], (starts[t], lengths[t]), width, f_point, obs, _Q), obs
            if len(table) >= table_cap:
                return None, obs
            table[x] = (starts[t], lengths[t])
            restarts.append(t)
        restarts += [t for t in range(LANES) if lengths[t] >= cap and t not in restarts]
        obs['cut'] += sum(1 for t in restarts if lengths[t] >= cap)
        for t in restarts:
            starts[t] = (base + nxt[0]) & mask
            nxt[0] += 1
            lengths[t] = 0
            points[t] = starts[t]
            if f_point is None:
                set_lane(regs, pol, t, starts[t], width)
    return None, obs


def set_lane(regs, pol, t, x, width):
    for j in range(width):
        bit = ((x >> j) & 1) ^ pol[j]
        regs[j] = (regs[j] & ~(1 << t)) | (bit << t)


def chain(x, n, width, f_point, q):
    mask = (1 << width) - 1
    for _ in range(n):
        x = (f_point(x) if f_point else f_int(x) ^ q) & mask
    return x


def recover(a, b, width, f_point, obs, q=0):
    """Walk two trails (start, length) ending at the same distinguished point to their merge."""
    (sa, la), (sb, lb) = a, b
    if la < lb:
        (sa, la), (sb, lb) = (sb, lb), (sa, la)
    xa = chain(sa, la - lb, width, f_point, q)
    xb = sb
    if xa == xb:
        obs['robin_hood'] += 1
        return None
    mask = (1 << width) - 1
    for _ in range(lb):
        ya = (f_point(xa) if f_point else f_int(xa) ^ q) & mask
        yb = (f_point(xb) if f_point else f_int(xb) ^ q) & mask
        if ya == yb:
            return xa, xb
        xa, xb = ya, yb
    return None


# ---------------------------------------------------------------- experiment

RHO_W = {'width': 22, 'dbits': 2, 'batches': 14, 'cap': 36, 'table_cap': 1 << 16}
PROJ_BITS = 22
PROJ_STEPS = 8
ZERO = [0] * N_IN


def rho_trial(step, qint, seed, ideal=False):
    """Experiment rho-w22: one attempt of the search at width 22 (with an ideal-function control locally)."""
    coins = Coins(seed)
    f = None
    if ideal:
        cache = {}
        oracle = Coins(b'ideal' + seed)

        def f(x):
            if x not in cache:
                cache[x] = oracle.word(RHO_W['width'])
            return cache[x]
    global _Q
    _Q = qint
    return search(step, ZERO, coins, RHO_W['width'], RHO_W['dbits'], RHO_W['batches'], RHO_W['cap'],
                  RHO_W['table_cap'], f)


def proj_trial(step, seed):
    """Experiment proj-w256: 256 lanes from random planes, PROJ_STEPS chained full-width steps; the first pair
    of distinct inputs (step-major order) whose images agree on the PROJ_BITS low bits."""
    coins = Coins(seed)
    regs = [coins.word(256) for _ in range(N_IN)] + [0] * (REGS - N_IN)
    seen = {}
    for s in range(PROJ_STEPS):
        step(regs)
        for t in range(LANES):
            key = 0
            for j in range(PROJ_BITS):
                key |= ((regs[j] >> t) & 1) << j
            if key in seen:
                return seen[key], (s, t), {'steps': s + 1}
            seen[key] = (s, t)
    return None, None, {'steps': PROJ_STEPS}


def proj_input(seed, qint, pos):
    """The input (step-s point) of lane t, recomputed from the trial's random planes with the reference."""
    s, t = pos
    coins = Coins(seed)
    regs = [coins.word(256) for _ in range(N_IN)]
    x = lane_point(regs, ZERO, t)
    for _ in range(s):
        x = f_int(x) ^ qint
    return x


def q_int(q):
    return sum(b << j for j, b in enumerate(q))


def serve():
    req = json.load(sys.stdin)
    prog, q = step_program()
    qint = q_int(q)
    step = compile_step(prog)
    out = []
    for tr in req['trials']:
        seed = bytes.fromhex(tr['seed'])
        rec = {'trial': tr['trial'], 'message_a_hex': None, 'message_b_hex': None}
        if req['experiment_id'] == 'proj-w256':
            a, b, obs = proj_trial(step, seed)
            if a:
                rec['message_a_hex'] = message(proj_input(seed, qint, a)).hex()
                rec['message_b_hex'] = message(proj_input(seed, qint, b)).hex()
        else:
            pair, obs = rho_trial(step, qint, seed)
            if pair:
                rec['message_a_hex'], rec['message_b_hex'] = message(pair[0]).hex(), message(pair[1]).hex()
        rec['observations'] = obs
        out.append(rec)
    json.dump({'schema_version': 1, 'trials': out}, sys.stdout, separators=(',', ':'))


def main():
    args = sys.argv[1:]
    if not args:
        return serve()
    prog, q = step_program()
    qint = q_int(q)
    counts = {}
    for op, *_ in prog:
        counts[op] = counts.get(op, 0) + 1
    if args[0] == '--ledger':
        print(json.dumps({'instructions': len(prog), 'by_op': counts, 'register_peak': allocate.peak,
                          'registers': REGS, 'mask_weight': sum(q)}))
    elif args[0] == '--selftest':
        import os
        n = int(args[1])
        step = compile_step(prog)
        bad = 0
        for k in range(0, n, LANES):
            xs = [int.from_bytes(os.urandom(32), 'little') for _ in range(min(LANES, n - k))]
            r = to_planes(xs + [0] * (LANES - len(xs)), ZERO) + [0] * (REGS - N_IN)
            for s in range(4):
                step(r)
                xs = [f_int(x) ^ qint for x in xs]
                bad += sum(lane_point(r, ZERO, t) != x for t, x in enumerate(xs))
        print(f'selftest: {n} points, 4 chained steps each: {bad} differences')
    elif args[0] == '--stats':
        import os
        step = compile_step(prog)
        n = int(args[1])
        res = {}
        for name in ('target', 'ideal'):
            res[name] = sum(rho_trial(step, qint, os.urandom(32), name == 'ideal')[0] is not None for _ in range(n))
        res['proj'] = sum(proj_trial(step, os.urandom(32))[0] is not None for _ in range(n))
        print(json.dumps({'trials': n, 'rho_w22_target': res['target'], 'rho_w22_ideal': res['ideal'],
                          'proj_w256': res['proj']}))


if __name__ == '__main__':
    main()
