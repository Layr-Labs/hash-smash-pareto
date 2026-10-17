"""BLAKE3 r7 bounded-restart machine: complete program, interpreter, checks.

Run only in the organizer's isolated executor. Provenance: the bitsliced
kernel generator is this repository's generator/bitslice.py (blob 086d2924)
and generator/blake3_kernel.py (blob b4e9866f), as embedded in the earlier
blake3_kernel_check.py; helpers unused here were removed, generation logic is
unchanged. The scalar BLAKE3 and bounded_search reference state machine come
from the earlier bounded_restart.py diagnostic (search logic unchanged).

The machine program (Section M of proof.md) is emitted for any parameter set.
The machine has a declared file of NREG = 1,024 registers of 256 bits, named
statically by instructions (its bytes are included in the memory bound but
registers are not memory-addressable); the table and lane metadata
are memory, reached only by charged indirect loads and stores. It is serialized into a byte image (5-byte kernel, 8-byte control, 40-byte
constant formats); every program is decoded from its image before execution
and the round trip is asserted. A block interpreter executes the decoded
program and counts every priced operation. Checks performed:
  * kernel: a static check that the register-allocated listing computes the
    gate DAG for every input, and an exhaustive check of every gate rule
    (XOR, AND/OR with polarities, pivot full adder, ripple-carry words);
  * fixtures: the program and the scalar reference agree, under lane-wise test
    functions, on ten control-flow cases with asserted outcomes;
  * probes: at the full-width parameters, measured operation counts of every
    handler equal the closed-form ledger formulas of proof.md;
  * trials: a 14-bit projected search on the selected target, executed by the
    complete program and by the reference, must agree on every outcome field;
    sampled kernel lanes are compared with scalar BLAKE3 on all 256 bits.
Counts are participant observations. No full-width probability is inferred.
"""
import hashlib
import json
import sys
from collections import defaultdict

M256 = (1 << 256) - 1
M32 = 0xFFFFFFFF
ZERO_H = (0, 0)
PD = 0x6BB321F265B2E13C7D821A3D58156F9AD7B24EC8D0FC0F0E088E963E14A7DBC1
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
      0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
GSCHED = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
          (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))


# ------------------------------------------------ bitsliced kernel generator
class Net:
    """Constant-folding Boolean DAG with stored polarities (see provenance)."""

    def __init__(self):
        self.nodes = [("CONST", None, None, 0, 0)]
        self.opc = [None]
        self.src = [(None, None)]
        self.stored = [0]
        self.index = {}
        self.notword = {}

    def _new(self, kind, a, b, pa, pb, opc, srcs, stored):
        self.nodes.append((kind, a, b, pa, pb))
        self.opc.append(opc)
        self.src.append(srcs)
        self.stored.append(stored)
        return len(self.nodes) - 1

    def var(self, name):
        key = ("VAR", name)
        if key not in self.index:
            self.index[key] = self._new("VAR", name, None, 0, 0, None, (None, None), 0)
        return (self.index[key], 0)

    def effpol(self, h):
        return h[1] ^ self.stored[h[0]]

    def complement(self, nid):
        c = self.notword.get(nid)
        if c is None:
            c = self._new("NOT", nid, None, 0, 0, "NOT", (nid, None), self.stored[nid] ^ 1)
            self.notword[nid] = c
        return c

    def xor(self, x, y):
        (a, pa), (b, pb) = x, y
        if a == 0:
            return (b, pb ^ pa)
        if b == 0:
            return (a, pa ^ pb)
        if a == b:
            return (0, pa ^ pb)
        if a > b:
            a, b = b, a
        key = ("XOR", a, b)
        nid = self.index.get(key)
        if nid is None:
            nid = self._new("XOR", a, b, 0, 0, "XOR", (a, b), self.stored[a] ^ self.stored[b])
            self.index[key] = nid
        return (nid, pa ^ pb)

    def and_(self, x, y):
        (a, pa), (b, pb) = x, y
        if a == 0:
            return y if pa else ZERO_H
        if b == 0:
            return x if pb else ZERO_H
        if a == b:
            return x if pa == pb else ZERO_H
        if a > b:
            a, b, pa, pb = b, a, pb, pa
        key = ("AND", a, b, pa, pb)
        nid = self.index.get(key)
        if nid is not None:
            return (nid, 0)
        ea, eb = pa ^ self.stored[a], pb ^ self.stored[b]
        wa, wb = a, b
        if ea != eb:
            if b in self.notword and a not in self.notword:
                wb = self.complement(b)
                eb ^= 1
            else:
                wa = self.complement(a)
                ea ^= 1
        nid = self._new("AND", a, b, pa, pb, "AND" if ea == 0 else "OR", (wa, wb), ea)
        self.index[key] = nid
        return (nid, 0)

    def full_adder(self, a, b, c):
        pa, pb, pc = self.effpol(a), self.effpol(b), self.effpol(c)
        if c[0] == 0:
            p, q, r = c, a, b
        elif a[0] == 0:
            p, q, r = a, b, c
        elif b[0] == 0:
            p, q, r = b, a, c
        elif pb == pc:
            p, q, r = a, b, c
        elif pa == pc:
            p, q, r = b, a, c
        else:
            p, q, r = c, a, b
        xq, xr = self.xor(q, p), self.xor(r, p)
        return self.xor(xq, r), self.xor(p, self.and_(xq, xr))

    def add(self, u, v):
        out, c = [], ZERO_H
        for i in range(len(u)):
            if i + 1 < len(u):
                s, c = self.full_adder(u[i], v[i], c)
            else:
                s = self.xor(self.xor(u[i], v[i]), c)
            out.append(s)
        return out

    def add_many(self, words):
        consts = [w for w in words if all(h[0] == 0 for h in w)]
        rest = [w for w in words if not all(h[0] == 0 for h in w)]
        acc = None
        for w in consts:
            acc = w if acc is None else self.add(acc, w)
        while rest:
            if acc is None:
                acc = rest.pop(0)
                continue
            p0 = self.effpol(acc[0])
            k = next((i for i, w in enumerate(rest) if self.effpol(w[0]) == p0), 0)
            acc = self.add(acc, rest.pop(k))
        return acc


def rotr(u, k):
    return [u[(i + k) % len(u)] for i in range(len(u))]


def const_word(value):
    return [(0, (value >> i) & 1) for i in range(32)]


def build_listing():
    """Kernel: planes of u in registers 0..255 -> planes of f(u) = D(u) ^ PD."""
    net = Net()
    m = [const_word(0) for _ in range(16)]
    for j in range(8):
        m[8 + j] = [net.var(("x", j, i)) for i in range(32)]
    v = ([const_word(w) for w in IV] + [const_word(w) for w in IV[:4]]
         + [const_word(0), const_word(0), const_word(64), const_word(11)])
    for _ in range(7):
        for gi, (a, b, c, d) in enumerate(GSCHED):
            x, y = m[2 * gi], m[2 * gi + 1]
            v[a] = net.add_many([v[a], v[b], x])
            v[d] = rotr([net.xor(p, q) for p, q in zip(v[d], v[a])], 16)
            v[c] = net.add(v[c], v[d])
            v[b] = rotr([net.xor(p, q) for p, q in zip(v[b], v[c])], 12)
            v[a] = net.add_many([v[a], v[b], y])
            v[d] = rotr([net.xor(p, q) for p, q in zip(v[d], v[a])], 8)
            v[c] = net.add(v[c], v[d])
            v[b] = rotr([net.xor(p, q) for p, q in zip(v[b], v[c])], 7)
        m = [m[i] for i in PERM]
    outputs = []
    for i in range(8):
        outputs.extend(net.xor(p, q) for p, q in zip(v[i], v[i + 8]))
    # Linearise reachable nodes in creation (topological) order.
    reach, stack = set(), [n for n, _ in outputs if n]
    while stack:
        n = stack.pop()
        if n not in reach:
            reach.add(n)
            stack.extend(s for s in net.src[n] if s is not None)
    order = sorted(reach)
    ops = [(net.opc[n], n) + net.src[n] for n in order if net.opc[n] is not None]
    inputs = [n for n in order if net.opc[n] is None]
    assert [net.nodes[n][1] for n in inputs] == [("x", j, i) for j in range(8) for i in range(32)]
    assert not any(net.stored[n] for n in inputs)
    pd = sum(((p ^ net.stored[n]) if n else p) << i for i, (n, p) in enumerate(outputs))
    # In-place register allocation (allocate(spill_reserved=True) of the source).
    last_use, out_nodes = {}, {}
    for i, (_, _, a, b) in enumerate(ops):
        for s in (a, b):
            if s is not None:
                last_use[s] = i
    for i, (nid, _) in enumerate(outputs):
        if nid:
            out_nodes.setdefault(nid, i)
    reg_of = {n: i for i, n in enumerate(inputs)}
    free, reserved, next_reg, listing = [], set(), 256, []
    for i, (opc, dst, a, b) in enumerate(ops):
        dying = [s for s in (a, b) if s is not None and last_use.get(s) == i and s not in out_nodes]
        want, r = out_nodes.get(dst), None
        if want is not None and want in reserved:
            r = want
            reserved.discard(want)
        if r is None and dying:
            r = reg_of[dying.pop(0)]
        elif r is None:
            if free:
                r = free.pop()
            elif reserved:
                r = max(reserved)
                reserved.discard(r)
            else:
                r, next_reg = next_reg, next_reg + 1
        listing.append((opc, r, reg_of[a], None if b is None else reg_of[b]))
        reg_of[dst] = r
        for s in dying:
            (reserved.add if reg_of[s] < 256 else free.append)(reg_of[s])
    gates = {k: sum(op[0] == k for op in ops) for k in ("XOR", "AND", "OR", "NOT")}
    assert gates == dict(XOR=37898, AND=2511, OR=5539, NOT=163)
    nops = len(listing)
    pending = {i: reg_of[n] for i, (n, _) in enumerate(outputs) if reg_of[n] != i}
    temp, used_temp = next_reg, 0
    while pending:
        sources = set(pending.values())
        safe = next((d for d in pending if d not in sources), None)
        if safe is not None:
            listing.append(("MOV", safe, pending.pop(safe), None))
        else:
            victim = next(iter(pending))
            listing.append(("MOV", temp, victim, None))
            used_temp = 1
            pending = {d: temp if s == victim else s for d, s in pending.items()}
    # Static proof that the allocated listing computes the DAG for every input:
    # track which DAG node each word holds and check every operand reference.
    held = {i: n for i, n in enumerate(inputs)}
    for (opc, dst, a, b), (lopc, r, ra, rb) in zip(ops, listing):
        assert lopc == opc and held[ra] == a and (b is None) == (rb is None)
        assert b is None or held[rb] == b
        held[r] = dst
    for opc, r, ra, _ in listing[nops:]:
        assert opc == "MOV"
        held[r] = held[ra]
    assert all(held[i] == n for i, (n, _) in enumerate(outputs))
    return listing, temp + used_temp, pd


def check_rules():
    """Exhaustively check every gate-construction rule on all operand classes.

    Words are evaluated bit-parallel: one lane per input assignment. Truth of
    a handle (node, pol) is word(node) XOR stored(node) XOR pol."""
    def evaluate(net, assign, M):
        val = [0] * len(net.nodes)
        for n in range(1, len(net.nodes)):
            opc, (a, b) = net.opc[n], net.src[n]
            if opc is None:
                val[n] = assign[net.nodes[n][1]] ^ (M if net.stored[n] else 0)
            elif opc == "XOR":
                val[n] = val[a] ^ val[b]
            elif opc == "AND":
                val[n] = val[a] & val[b]
            elif opc == "OR":
                val[n] = val[a] | val[b]
            else:
                val[n] = val[a] ^ M
        return lambda h: val[h[0]] ^ (M if net.stored[h[0]] ^ h[1] else 0)

    net, M = Net(), 0xFF
    a, b, c = net.var("a"), net.var("b"), net.var("c")
    base = [(0, 0), (0, 1), a, b, c, net.and_(a, (b[0], 1)), net.xor(a, c),
            net.and_((a[0], 1), (c[0], 1)), net.and_(b, c)]
    pool = base + [(n, p ^ 1) for n, p in base]
    gates = [(x, y, net.xor(x, y), net.and_(x, y)) for x in pool for y in pool]
    adders = [(x, y, z) + net.full_adder(x, y, z) for x in pool for y in pool for z in pool]
    t = evaluate(net, dict(a=0xF0, b=0xCC, c=0xAA), M)
    for x, y, xo, an in gates:
        assert t(xo) == t(x) ^ t(y) and t(an) == t(x) & t(y)
    for x, y, z, sm, cy in adders:
        assert t(sm) == t(x) ^ t(y) ^ t(z)
        assert t(cy) == (t(x) & t(y)) | (t(x) & t(z)) | (t(y) & t(z))
    # Ripple-carry words: all 4-bit operand pairs (256 lanes), with inverted,
    # polarity-flipped and constant operands.
    net, M = Net(), (1 << 256) - 1
    u = [net.var(("u", i)) for i in range(4)]
    v = [net.var(("v", i)) for i in range(4)]
    assign = {("u", i): sum(((l >> i) & 1) << l for l in range(256)) for i in range(4)}
    assign.update({("v", i): sum(((l >> (4 + i)) & 1) << l for l in range(256)) for i in range(4)})
    one = (0, 1)
    cases = [(u, v, lambda U, V: U + V), ([(n, p ^ 1) for n, p in u], v, lambda U, V: (15 - U) + V),
             ([net.xor(h, one) for h in v], u, lambda U, V: (15 - V) + U)]
    for k in range(16):
        cases.append((u, [(0, (k >> i) & 1) for i in range(4)], lambda U, V, k=k: U + k))
        cases.append(("many", k, None))
    built = []
    for x, y, fn in cases:
        if x == "many":
            k = y
            built.append((net.add_many([u, [(0, (k >> i) & 1) for i in range(4)], v]),
                          lambda U, V, k=k: U + V + k))
        else:
            built.append((net.add(x, y), fn))
    t = evaluate(net, assign, M)
    for word, fn in built:
        got = [sum(((t(h) >> l) & 1) << i for i, h in enumerate(word)) for l in range(256)]
        assert got == [fn(l & 15, l >> 4) & 15 for l in range(256)]
    return len(gates) + len(adders) + len(built)


def compile_kernel(listing, chunk=1500):
    """Compile the listing in small chunks (bounded compiler memory)."""
    form = dict(XOR="r[%d]=r[%d]^r[%d]", AND="r[%d]=r[%d]&r[%d]", OR="r[%d]=r[%d]|r[%d]",
                NOT="r[%d]=r[%d]^%d", MOV="r[%d]=r[%d]")
    parts = []
    for s in range(0, len(listing), chunk):
        body = ["def part(r):"]
        for opc, d, a, b in listing[s:s + chunk]:
            args = (d, a, b) if opc in ("XOR", "AND", "OR") else (d, a, M256) if opc == "NOT" else (d, a)
            body.append(" " + form[opc] % args)
        scope = {}
        exec(compile("\n".join(body), "<kernel>", "exec"), scope)
        parts.append(scope["part"])

    def kern(r):
        for part in parts:
            part(r)
    return kern


# ---------------------------------------------------------- scalar BLAKE3 r7
def digest_int(u):
    """LE256 of the 7-round BLAKE3 digest of M(u) = 0^32 || LE256(u)."""
    m = [0] * 8 + [(u >> (32 * j)) & M32 for j in range(8)]
    v = list(IV) + list(IV[:4]) + [0, 0, 64, 11]
    for _ in range(7):
        for gi, (a, b, c, d) in enumerate(GSCHED):
            for x, (r1, r2) in ((m[2 * gi], (16, 12)), (m[2 * gi + 1], (8, 7))):
                v[a] = (v[a] + v[b] + x) & M32
                t = v[d] ^ v[a]
                v[d] = ((t >> r1) | (t << (32 - r1))) & M32
                v[c] = (v[c] + v[d]) & M32
                t = v[b] ^ v[c]
                v[b] = ((t >> r2) | (t << (32 - r2))) & M32
        m = [m[i] for i in PERM]
    return sum((v[i] ^ v[i + 8]) << (32 * i) for i in range(8))


def message(u):
    return bytes(32) + u.to_bytes(32, "little")


# ------------------------------------------------- scalar reference machine
def bounded_search(step, *, width, dp_bits, key_bits, lanes, batches, cap,
                   capacity, start_limit, rho):
    """Scalar reference state machine (unchanged from bounded_restart.py)."""
    assert 0 < dp_bits < width and 0 < key_bits <= width - dp_bits
    assert lanes <= start_limit <= 1 << width
    mask = (1 << width) - 1
    dp_mask = (1 << dp_bits) - 1
    key_mask = (1 << key_bits) - 1
    states = [(rho + i) & mask for i in range(lanes)]
    ids = list(range(lanes))
    births = [0] * lanes
    next_id = lanes
    table = {}
    stats = dict(search_evaluations=0, recovery_evaluations=0,
                 final_evaluations=0, cuts=0, insertions=0, restarts=0,
                 max_age=0, reason=0)

    def finish(reason, pair=None):
        stats['reason'] = reason
        stats['allocated_starts'] = next_id
        stats['stored_endpoints'] = len(table)
        return pair, stats

    def restart(lane, batch):
        nonlocal next_id
        if next_id >= start_limit:
            return False
        ids[lane] = next_id
        states[lane] = (rho + next_id) & mask
        births[lane] = batch
        next_id += 1
        stats['restarts'] += 1
        return True

    def recover(old_id, current_id, current_length, endpoint):
        first = (rho + old_id) & mask
        old_endpoint = first
        length = 0
        for length in range(1, cap + 1):
            old_endpoint = step(old_endpoint)
            stats['recovery_evaluations'] += 1
            if old_endpoint & dp_mask == 0:
                break
        else:
            return 8, None
        if old_endpoint != endpoint:
            return 2, None
        second = (rho + current_id) & mask
        a, b = first, second
        for _ in range(max(0, length - current_length)):
            a = step(a)
            stats['recovery_evaluations'] += 1
        for _ in range(max(0, current_length - length)):
            b = step(b)
            stats['recovery_evaluations'] += 1
        if a == b:
            return 3, None
        for _ in range(min(length, current_length)):
            na, nb = step(a), step(b)
            stats['recovery_evaluations'] += 2
            if na == nb:
                stats['final_evaluations'] += 2
                if a != b and step(a) == step(b):
                    return 1, (a, b)
                return 8, None
            a, b = na, nb
        return 8, None

    for batch in range(1, batches + 1):
        outputs = [step(u) for u in states]
        stats['search_evaluations'] += lanes
        states[:] = outputs
        distinguished = [u & dp_mask == 0 for u in outputs]
        for lane in range(lanes):
            stats['max_age'] = max(stats['max_age'], batch - births[lane])
            if not distinguished[lane]:
                continue
            key = (outputs[lane] >> dp_bits) & key_mask
            if key in table:
                reason, pair = recover(table[key], ids[lane],
                                       batch - births[lane], outputs[lane])
                return finish(reason, pair)
            if len(table) >= capacity:
                return finish(4)
            table[key] = ids[lane]
            stats['insertions'] += 1
            if not restart(lane, batch):
                return finish(5)
        for lane in range(lanes):
            if not distinguished[lane] and batch - births[lane] >= cap:
                stats['cuts'] += 1
                if not restart(lane, batch):
                    return finish(5)
    return finish(6)


# --------------------------------------------------------- machine program
# Register-file machine: an instruction on registers costs its base operation(s);
# LD/ST are the charged transfers to memory; COMP adds 64 operations of block
# assembly to its compression unit.
NREG = 1024
COST = dict(BEQ=2, BNE=2, BLT=2, BGE=2, COMP=64, OUT=2)
REGIONS = ("setup", "loop", "kernel", "diag", "epscan", "key", "table",
           "restart", "cut", "recovery", "term")
CTRL = ("ZERO ONE ONES C3 C15 C256 M16 KM DPM PD BMAX RCAP ULIM IDL WM RHO NID "
        "CNT B NEXTCUT D ND LANE KEY E S NOTLANE T0 T1 T2 T3 T4 T5 RR EIDX ID1 "
        "ID2 L1 L2 X Y A BV FA FB CN MINL MINB").split()


def build_program(p, kregs):
    """Emit the machine program for parameters p (see proof.md, Section M)."""
    w, d, k, U = p["w"], p["d"], p["k"], p["U"]
    diag = w < 256
    assert 1 < d and d + k <= w <= 256 and k <= 64 and p["IDL"] <= 1 << 16
    R = {n: kregs + i for i, n in enumerate(CTRL if diag else [c for c in CTRL if c != "WM"])}
    keyw, idw = -(-U // 4), -(-U // 16)
    KEYB, IDB, BIRB, LIDB = 0, keyw, keyw + idw, keyw + idw + 256
    code, labels, region = [], {}, ["setup"]

    def e(op, *args):
        code.append((op, args, region[0]))

    def lab(name):
        labels[name] = len(code)

    def r(name):
        return R[name] if isinstance(name, str) else name

    def x3(op, dst, a, b):
        e(op, r(dst), r(a), r(b))

    def proj(name):
        if diag:
            region[0], old = "diag", region[0]
            x3("AND", name, name, "WM")
            region[0] = old

    # Setup: constants, randomness, zeroed memory, initial lanes.
    consts = dict(ZERO=0, ONE=1, ONES=M256, C3=3, C15=15, C256=256, M16=0xFFFF,
                  KM=(1 << k) - 1, DPM=(1 << d) - 1, PD=PD, BMAX=p["B"], RCAP=p["R"],
                  ULIM=U, IDL=p["IDL"])
    if diag:
        consts["WM"] = (1 << w) - 1
    for name, value in consts.items():
        e("LDI", R[name], value)
    e("RAND", R["RHO"])
    proj("RHO")
    x3("MOV", "T1", "ZERO", None)
    e("LDI", R["T2"], LIDB + 256)
    lab("ZL")
    e("ST", R["T1"], R["ZERO"])
    e("ADDI", R["T1"], R["T1"], 1)
    e("BNE", R["T1"], R["T2"], "ZL")
    for n in ("NID", "CNT", "B", "LANE"):
        x3("MOV", n, "ZERO", None)
    lab("IL")
    e("LDI", R["RR"], 0)
    e("JMP", "RESTART")
    lab("RET0")
    e("ADDI", R["LANE"], R["LANE"], 1)
    e("BNE", R["LANE"], R["C256"], "IL")
    e("ADDI", R["B"], R["ZERO"], 1)
    x3("MOV", "NEXTCUT", "RCAP", None)
    # Main loop.
    lab("LOOP")
    region[0] = "kernel"
    e("KERNEL")
    region[0] = "diag"
    for j in range(w, 256):
        e("XOR", j, j, j)
    region[0] = "loop"
    e("OR", R["D"], 0, 1)
    for j in range(2, d):
        e("OR", R["D"], R["D"], j)
    e("BNE", R["D"], R["ONES"], "EPB")
    lab("EPD")
    e("BGE", R["B"], R["NEXTCUT"], "CUTB")
    lab("CUTD")
    e("BEQ", R["B"], R["BMAX"], "FAIL6")
    e("ADDI", R["B"], R["B"], 1)
    e("JMP", "LOOP")
    # Endpoint batch: ascending lanes with a zero bit in D.
    region[0] = "epscan"
    lab("EPB")
    x3("NOT", "ND", "D", None)
    x3("MOV", "LANE", "ZERO", None)
    lab("EPL")
    x3("SHR", "T0", "ND", "LANE")
    x3("AND", "T0", "T0", "ONE")
    e("BEQ", R["T0"], R["ZERO"], "EPN")
    region[0] = "key"
    x3("MOV", "KEY", "ZERO", None)
    for j in range(k):
        x3("SHR", "T0", d + j, "LANE")
        x3("AND", "T0", "T0", "ONE")
        e("SHLI", R["T0"], R["T0"], j)
        x3("OR", "KEY", "KEY", "T0")
    region[0] = "table"
    x3("MOV", "EIDX", "ZERO", None)
    lab("SC")
    e("BEQ", R["EIDX"], R["CNT"], "NOM")
    e("SHRI", R["T1"], R["EIDX"], 2)
    e("ADDI", R["T1"], R["T1"], KEYB)
    x3("LD", "T2", "T1", None)
    x3("AND", "T3", "EIDX", "C3")
    e("SHLI", R["T3"], R["T3"], 6)
    x3("SHR", "T2", "T2", "T3")
    x3("AND", "T2", "T2", "KM")
    e("BEQ", R["T2"], R["KEY"], "MATCH")
    e("ADDI", R["EIDX"], R["EIDX"], 1)
    e("JMP", "SC")
    lab("NOM")
    e("BEQ", R["CNT"], R["ULIM"], "FAIL4")
    for field, base, sh, m in (("KEY", KEYB, 2, "C3"), ("T5", IDB, 4, "C15")):
        if field == "T5":
            e("ADDI", R["T1"], R["LANE"], LIDB)
            x3("LD", "T5", "T1", None)
        e("SHRI", R["T1"], R["CNT"], sh)
        e("ADDI", R["T1"], R["T1"], base)
        x3("LD", "T2", "T1", None)
        x3("AND", "T3", "CNT", m)
        e("SHLI", R["T3"], R["T3"], 8 - sh)
        x3("SHL", "T4", field, "T3")
        x3("OR", "T2", "T2", "T4")
        e("ST", R["T1"], R["T2"])
    e("ADDI", R["CNT"], R["CNT"], 1)
    e("LDI", R["RR"], 1)
    e("JMP", "RESTART")
    region[0] = "epscan"
    lab("RET1")
    lab("EPN")
    e("ADDI", R["LANE"], R["LANE"], 1)
    e("BNE", R["LANE"], R["C256"], "EPL")
    e("JMP", "EPD")
    # Restart lane LANE at identifier NID with birth B; RR selects the return.
    region[0] = "restart"
    lab("RESTART")
    e("BEQ", R["NID"], R["IDL"], "FAIL5")
    e("ADDI", R["T1"], R["LANE"], LIDB)
    e("ST", R["T1"], R["NID"])
    e("ADDI", R["T1"], R["LANE"], BIRB)
    e("ST", R["T1"], R["B"])
    x3("ADD", "S", "RHO", "NID")
    proj("S")
    e("ADDI", R["NID"], R["NID"], 1)
    x3("SHL", "T0", "ONE", "LANE")
    x3("NOT", "NOTLANE", "T0", None)
    for j in range(256):
        e("SHRI", R["T0"], R["S"], j)
        x3("AND", "T0", "T0", "ONE")
        x3("SHL", "T0", "T0", "LANE")
        e("AND", j, j, R["NOTLANE"])
        e("OR", j, j, R["T0"])
    e("BEQ", R["RR"], R["ZERO"], "RET0")
    e("BEQ", R["RR"], R["ONE"], "RET1")
    e("JMP", "RET2")
    # Age-cap scan, entered only when B >= NEXTCUT.
    region[0] = "cut"
    lab("CUTB")
    x3("MOV", "MINB", "B", None)
    x3("MOV", "LANE", "ZERO", None)
    lab("CL")
    e("ADDI", R["T1"], R["LANE"], BIRB)
    x3("LD", "T2", "T1", None)
    x3("SUB", "T3", "B", "T2")
    e("BLT", R["T3"], R["RCAP"], "CK")
    lab("CUTR")
    e("LDI", R["RR"], 2)
    e("JMP", "RESTART")
    lab("RET2")
    x3("MOV", "T2", "B", None)
    lab("CK")
    e("BGE", R["T2"], R["MINB"], "CN_")
    x3("MOV", "MINB", "T2", None)
    lab("CN_")
    e("ADDI", R["LANE"], R["LANE"], 1)
    e("BNE", R["LANE"], R["C256"], "CL")
    x3("ADD", "NEXTCUT", "MINB", "RCAP")
    e("JMP", "CUTD")
    # Recovery after a key match at entry EIDX for lane LANE.
    region[0] = "recovery"
    lab("MATCH")
    e("SHRI", R["T1"], R["EIDX"], 4)
    e("ADDI", R["T1"], R["T1"], IDB)
    x3("LD", "T2", "T1", None)
    x3("AND", "T3", "EIDX", "C15")
    e("SHLI", R["T3"], R["T3"], 4)
    x3("SHR", "T2", "T2", "T3")
    x3("AND", "ID1", "T2", "M16")
    e("ADDI", R["T1"], R["LANE"], LIDB)
    x3("LD", "ID2", "T1", None)
    e("ADDI", R["T1"], R["LANE"], BIRB)
    x3("LD", "T2", "T1", None)
    x3("SUB", "L2", "B", "T2")
    x3("MOV", "E", "ZERO", None)
    for j in range(256):
        x3("SHR", "T0", j, "LANE")
        x3("AND", "T0", "T0", "ONE")
        e("SHLI", R["T0"], R["T0"], j)
        x3("OR", "E", "E", "T0")
    x3("ADD", "X", "RHO", "ID1")
    proj("X")
    x3("MOV", "L1", "ZERO", None)

    def step(dst, src):
        x3("COMP", dst, src, None)
        x3("XOR", dst, dst, "PD")
        proj(dst)

    lab("RC")
    e("BEQ", R["L1"], R["RCAP"], "FAIL8")
    step("Y", "X")
    e("ADDI", R["L1"], R["L1"], 1)
    x3("MOV", "X", "Y", None)
    x3("AND", "T0", "Y", "DPM")
    e("BNE", R["T0"], R["ZERO"], "RC")
    e("BNE", R["Y"], R["E"], "FAIL2")
    x3("ADD", "A", "RHO", "ID1")
    proj("A")
    x3("ADD", "BV", "RHO", "ID2")
    proj("BV")
    e("BLT", R["L1"], R["L2"], "AL2")
    for tag, hi, lo, reg in (("AA", "L1", "L2", "A"), ("AB", "L2", "L1", "BV")):
        if tag == "AB":
            lab("AL2")
        x3("SUB", "CN", hi, lo)
        x3("MOV", "MINL", lo, None)
        lab(tag)
        e("BEQ", R["CN"], R["ZERO"], "AD")
        step(reg, reg)
        x3("SUB", "CN", "CN", "ONE")
        e("JMP", tag)
    lab("AD")
    e("BEQ", R["A"], R["BV"], "FAIL3")
    lab("PL")
    e("BEQ", R["MINL"], R["ZERO"], "FAIL8")
    step("FA", "A")
    step("FB", "BV")
    e("BEQ", R["FA"], R["FB"], "FOUND")
    x3("MOV", "A", "FA", None)
    x3("MOV", "BV", "FB", None)
    x3("SUB", "MINL", "MINL", "ONE")
    e("JMP", "PL")
    lab("FOUND")
    e("BEQ", R["A"], R["BV"], "FAIL8")
    step("FA", "A")
    step("FB", "BV")
    e("BNE", R["FA"], R["FB"], "FAIL8")
    region[0] = "term"
    e("OUT", R["A"], R["BV"])
    e("HALT", 1)
    for n in (2, 3, 4, 5, 6, 8):
        lab("FAIL%d" % n)
        e("HALT", n)
    code = [(op, tuple(labels[a] if isinstance(a, str) else a for a in args), reg)
            for op, args, reg in code]
    return dict(code=code, labels=labels, nregs=kregs + len(R), nmem=LIDB + 256,
                regs=R, entry=0)


def code_bytes(prog, klen, per_instruction=None):
    """Declared encoding: kernel register-only 5 bytes; control 8; LDI 40."""
    n = sum(op != "KERNEL" for op, _, _ in prog["code"])
    if per_instruction is not None:
        return per_instruction * (klen + n)
    return 5 * klen + sum(40 if op == "LDI" else 8 for op, _, _ in prog["code"]
                          if op != "KERNEL")


SHORT = ("XOR", "AND", "OR", "NOT", "MOV")
LONG = SHORT + ("ADD", "ADDI", "SUB", "SHL", "SHR", "SHLI", "SHRI", "LD", "ST", "BEQ",
                "BNE", "BLT", "BGE", "JMP", "RAND", "COMP", "OUT", "HALT")
BRANCH = ("BEQ", "BNE", "BLT", "BGE", "JMP")
IMM = ("ADDI", "SHLI", "SHRI", "HALT")


def encode(prog, listing):
    """Serialize the program image (proof.md Section 3.2).

    5-byte kernel format: opcode 1..5 | r1<<8 | r2<<18 | r3<<28 (38 bits).
    8-byte control format: opcode 16.. | r1<<8 | r2<<18 | r3<<28 | imm24<<38.
    40-byte LDI format: opcode 64 | r1<<8 | imm256<<18. Branch targets are
    byte offsets into the image. The kernel listing is inlined at KERNEL."""
    offsets, pos = [], 0
    for op, _, _ in prog["code"]:
        offsets.append(pos)
        pos += 5 * len(listing) if op == "KERNEL" else 40 if op == "LDI" else 8
    out = bytearray()
    for op, args, _ in prog["code"]:
        if op == "KERNEL":
            for opc, d, a, b in listing:
                out += (1 + SHORT.index(opc) | d << 8 | a << 18 | (b or 0) << 28).to_bytes(5, "little")
            continue
        if op == "LDI":
            out += (64 | args[0] << 8 | args[1] << 18).to_bytes(40, "little")
            continue
        args = [x for x in args if x is not None]
        imm = 0
        if op in BRANCH:
            imm = offsets[args.pop()]
        elif op in IMM:
            imm = args.pop()
        regs = args + [0] * (3 - len(args))
        assert all(0 <= r < 1024 for r in regs) and 0 <= imm < 1 << 24
        out += (16 + LONG.index(op) | regs[0] << 8 | regs[1] << 18 | regs[2] << 28
                | imm << 38).to_bytes(8, "little")
    assert len(out) == pos
    return bytes(out)


def decode(image):
    """Decode an image into (code, kernel listing); the inverse of encode."""
    raw, pos = [], 0
    while pos < len(image):
        op = image[pos]
        if 1 <= op <= 5:
            v = int.from_bytes(image[pos:pos + 5], "little")
            opc = SHORT[op - 1]
            raw.append((pos, "K", (opc, v >> 8 & 1023, v >> 18 & 1023,
                                   v >> 28 & 1023 if opc in ("XOR", "AND", "OR") else None)))
            pos += 5
        elif op == 64:
            v = int.from_bytes(image[pos:pos + 40], "little")
            raw.append((pos, "LDI", (v >> 8 & 1023, v >> 18)))
            pos += 40
        else:
            v = int.from_bytes(image[pos:pos + 8], "little")
            raw.append((pos, LONG[op - 16], (v >> 8 & 1023, v >> 18 & 1023, v >> 28 & 1023,
                                            v >> 38)))
            pos += 8
    index, code, listing, n = {}, [], [], 0
    for at, op, f in raw:
        if op == "K":
            if not listing:
                index[at] = n
                n += 1
            listing.append(f)
        else:
            index[at] = n
            n += 1
    nargs = dict(XOR=3, AND=3, OR=3, ADD=3, SUB=3, SHL=3, SHR=3, NOT=2, MOV=2, LD=2,
                 ST=2, COMP=2, OUT=2, ADDI=2, SHLI=2, SHRI=2, BEQ=2, BNE=2, BLT=2, BGE=2,
                 RAND=1, JMP=0, HALT=0)
    seen = False
    for at, op, f in raw:
        if op == "K":
            if not seen:
                code.append(("KERNEL", ()))
                seen = True
        elif op == "LDI":
            code.append(("LDI", f))
        else:
            args = list(f[:nargs[op]])
            if op in BRANCH:
                args.append(index[f[3]])
            elif op in IMM:
                args.append(f[3])
            code.append((op, tuple(args)))
    return code, listing


def load(p, kregs, listing):
    """Build, serialize and decode; the interpreter runs the decoded image."""
    prog = build_program(p, kregs)
    image = encode(prog, listing)
    code, decoded = decode(image)
    norm = [(op, tuple(x for x in a if x is not None)) for op, a, _ in prog["code"]]
    assert code == norm and decoded == listing and len(image) == code_bytes(prog, len(listing))
    prog = dict(prog, code=[(op, a, reg) for (op, a), (_, _, reg) in zip(code, prog["code"])])
    return prog, image


class Machine:
    """Block interpreter: per-block static costs times execution counts."""

    def __init__(self, prog, klen):
        code = prog["code"]
        starts = {0} | {i + 1 for i, (op, _, _) in enumerate(code)
                        if op in ("BEQ", "BNE", "BLT", "BGE", "JMP", "HALT", "KERNEL")}
        starts |= set(prog["labels"].values())
        starts = sorted(s for s in starts if s < len(code))
        self.block_of = {s: i for i, s in enumerate(starts)}
        self.costs, src = [], ["def make(E, M):", " fs = []"]
        cmp = dict(BEQ="==", BNE="!=", BLT="<", BGE=">=")
        for bi, s in enumerate(starts):
            end = starts[bi + 1] if bi + 1 < len(starts) else len(code)
            cost = defaultdict(int)
            src.append(" def f(r, m):")
            nxt = None
            for i in range(s, end):
                op, a, reg = code[i]
                cost[reg] += klen if op == "KERNEL" else COST.get(op, 1)
                if op == "COMP":
                    cost["compressions"] += 1
                line = {
                    "XOR": "r[{0}]=r[{1}]^r[{2}]", "AND": "r[{0}]=r[{1}]&r[{2}]",
                    "OR": "r[{0}]=r[{1}]|r[{2}]", "NOT": "r[{0}]=r[{1}]^M",
                    "MOV": "r[{0}]=r[{1}]", "ADD": "r[{0}]=(r[{1}]+r[{2}])&M",
                    "ADDI": "r[{0}]=(r[{1}]+{2})&M", "SUB": "r[{0}]=(r[{1}]-r[{2}])&M",
                    "SHL": "r[{0}]=(r[{1}]<<r[{2}])&M", "SHR": "r[{0}]=r[{1}]>>r[{2}]",
                    "SHLI": "r[{0}]=(r[{1}]<<{2})&M", "SHRI": "r[{0}]=r[{1}]>>{2}",
                    "LDI": "r[{0}]={1}", "LD": "r[{0}]=m[r[{1}]]", "ST": "m[r[{0}]]=r[{1}]",
                    "RAND": "r[{0}]=E.rand", "COMP": "r[{0}]=E.comp(r[{1}])",
                    "OUT": "E.out=(r[{0}],r[{1}])", "KERNEL": "E.kern(r)",
                    "HALT": "E.halt={0}",
                }.get(op)
                if line:
                    src.append("  " + line.format(*a))
                if op in cmp:
                    nxt = "%d if r[%d]%sr[%d] else %d" % (self.block_of[a[2]], a[0], cmp[op],
                                                           a[1], bi + 1)
                elif op == "JMP":
                    nxt = str(self.block_of[a[0]])
                elif op == "HALT":
                    nxt = "-1"
            src.append("  return " + (nxt or str(bi + 1)))
            src.append(" fs.append(f)")
            self.costs.append(dict(cost))
        src.append(" return fs")
        scope = {}
        exec(compile("\n".join(src), "<machine>", "exec"), scope)
        self.make = scope["make"]
        self.prog = prog
        self.kernel_block = self.block_of[next(i for i, c in enumerate(code) if c[0] == "KERNEL")]
        self.cut_block = self.block_of[prog["labels"]["CUTR"]]

    def run(self, kern, comp, rand, stop_after=None):
        env = type("Env", (), {})()
        env.kern, env.comp, env.rand, env.out, env.halt = kern, comp, rand, None, None
        fs = self.make(env, M256)
        r, m = [0] * self.prog["nregs"], [0] * self.prog["nmem"]
        counts = [0] * len(fs)
        b, kb = 0, self.kernel_block
        while b >= 0:
            if b == kb and stop_after is not None and counts[kb] >= stop_after:
                break
            counts[b] += 1
            b = fs[b](r, m)
        ops = defaultdict(int)
        for c, cost in zip(counts, self.costs):
            for reg, v in cost.items():
                ops[reg] += c * v
        R = self.prog["regs"]
        return dict(reason=env.halt, pair=env.out, batches=counts[kb],
                    cuts=counts[self.cut_block], insertions=r[R["CNT"]],
                    starts=r[R["NID"]], ops=dict(ops), r=r)


def lanewise(fn):
    """Test kernel: apply fn independently to each of the 256 lanes."""
    def kern(r):
        planes = r[:256]
        outs = []
        for lane in range(256):
            u = 0
            for j in range(256):
                u |= ((planes[j] >> lane) & 1) << j
            outs.append(fn(u))
        r[:256] = [sum(((outs[l] >> j) & 1) << l for l in range(256)) for j in range(256)]
    return kern


def agree(run, pair, s):
    keys = ("reason", "insertions", "cuts")
    ok = all(run[k] == s[k] for k in keys) and run["pair"] == pair
    ok = ok and run["starts"] == s["allocated_starts"]
    ok = ok and run["batches"] * 256 == s["search_evaluations"]
    ok = ok and run["ops"].get("compressions", 0) == s["recovery_evaluations"] + s["final_evaluations"]
    if not ok:
        raise AssertionError("machine and reference disagree: %r %r %r" % (run, pair, s))


def fixtures(klen, kregs):
    base = dict(w=12, d=3, k=8, U=8, R=4, B=4, IDL=2048)
    rho = 256
    cases = [  # (overrides, parameter changes, expected reason)
        ({256: 8, 257: 8}, {}, 1),
        ({256: 8, 257: 8 | 2048}, {}, 2),
        ({256: 257, 257: 8}, {}, 3),
        ({256: 8}, dict(U=0), 4),
        ({256: 3, 3: 16}, dict(R=2, B=3), 6),
        ({}, dict(R=1, B=5), 6),
        ({256: 8, 257: 16}, dict(U=1), 4),
        ({}, dict(R=1, B=2, IDL=300), 5),
        ({256: 8, 300: 8}, {}, 1),
        ({256: 5, 5: 7, 7: 8, 257: 9, 9: 8}, {}, 1),
    ]
    for over, change, want in cases:
        p = dict(base, **change)
        fn = lambda u, o=over: o.get(u, u | 1)
        mach = Machine(load(p, kregs, KLIST)[0], klen)
        run = mach.run(lanewise(fn), lambda u, f=fn: f(u) ^ PD, rho)
        pair, s = bounded_search(fn, width=p["w"], dp_bits=p["d"], key_bits=p["k"],
                                 lanes=256, batches=p["B"], cap=p["R"], capacity=p["U"],
                                 start_limit=p["IDL"], rho=rho)
        agree(run, pair, s)
        assert run["reason"] == want, (over, run["reason"])
    return len(cases)


KLIST = None
FULL = dict(w=256, d=113, k=64, U=40000, R=20 * 2 ** 113 + 4, B=146 * 2 ** 113 + 2,
            IDL=65536)


def formulas(p, klen):
    """Closed-form operation counts of the program text (proof.md, Section L)."""
    d, k, nmem = p["d"], p["k"], -(-p["U"] // 4) + -(-p["U"] // 16) + 512
    rs = {0: 1292, 1: 1294, 2: 1295}
    return dict(batch=klen + d + 7, setup=15 + 2 + 4 * nmem + 4 + 256 * (5 + rs[0]) + 2,
                epscan=1795, key=1 + 4 * k, insert=26, per_entry=13, restart=rs,
                cut_scan=2564, cut_min=256, cut_each=3, rec_fixed=1051, rec_step=72,
                align_step=69, pair_step=138, found=268, term=3, min_update=1,
                terminal=13 * p["U"] + 5, match_extra=12)


def probes(klen, kregs):
    """Measure handler costs at the full-width parameters with test functions."""
    f = formulas(FULL, klen)
    L = 2 ** 113
    rho = (1 << 200) + 12345
    mach = Machine(load(FULL, kregs, KLIST)[0], klen)
    plain = lambda u: u | 1
    comp = lambda fn: (lambda u: fn(u) ^ PD)
    run = mach.run(lanewise(plain), comp(plain), rho, stop_after=3)
    o = run["ops"]
    assert o["kernel"] == 3 * klen and o["loop"] == 3 * (f["batch"] - klen)
    assert o["setup"] + o["restart"] == f["setup"], (o, f["setup"])
    for n in range(4):  # n endpoints in batch one, table counts 0..n-1
        over = {(rho + l) & M256: (l + 1) * L for l in range(n)}
        fn = lambda u, o=over: o.get(u, u | 1)
        o = mach.run(lanewise(fn), comp(fn), rho, stop_after=1)["ops"]
        assert o.get("epscan", 0) == (f["epscan"] if n else 0)
        assert o.get("key", 0) == n * f["key"]
        assert o.get("table", 0) == n * f["insert"] + f["per_entry"] * n * (n - 1) // 2
        assert o["restart"] - 256 * f["restart"][0] == n * f["restart"][1]
    cutp = dict(FULL, R=1)
    mc = Machine(load(cutp, kregs, KLIST)[0], klen)
    run = mc.run(lanewise(plain), comp(plain), rho, stop_after=1)
    o = run["ops"]
    assert run["cuts"] == 256 and o["cut"] == f["cut_scan"] + 256 * f["cut_each"]
    assert o["restart"] == 256 * (f["restart"][0] + f["restart"][2])
    # Lane 0 ends at batch 1; at batch 2 the other 255 lanes are cut and the
    # running minimum is updated once (lane 0's birth 1 < 2).
    fn = lambda u: L if u == rho else u | 1
    mc = Machine(load(dict(FULL, R=2), kregs, KLIST)[0], klen)
    run = mc.run(lanewise(fn), comp(fn), rho, stop_after=2)
    assert run["cuts"] == 255
    assert run["ops"]["cut"] == f["cut_scan"] + f["min_update"] + 255 * f["cut_each"]
    # Capacity terminal: U = 1, two endpoints with distinct keys in batch one.
    fn = lambda u: L if u == rho else 2 * L if u == (rho + 1) & M256 else u | 1
    mu = Machine(load(dict(FULL, U=1), kregs, KLIST)[0], klen)
    run = mu.run(lanewise(fn), comp(fn), rho)
    assert run["reason"] == 4
    assert run["ops"]["table"] == f["insert"] + 13 * 1 + 5
    # Recovery with stored length l1 and current length l2 (direct chains).
    for l1, l2 in ((1, 1), (2, 3), (3, 1), (4, 4)):
        def chain(start, length, tag):
            pts = [start] + [(tag << 120) + 2 * i + 1 for i in range(1, length)]
            return {pts[i]: pts[i + 1] for i in range(length - 1)}, pts[-1]
        o1, end1 = chain(rho & M256, l1, 1)
        o2, end2 = chain((rho + 1) & M256, l2, 2)
        over = {**o1, **o2}
        over[end1] = over[end2] = 5 * L
        fn = lambda u, o=over: o.get(u, u | 1)
        run = mach.run(lanewise(fn), comp(fn), rho)
        o = run["ops"]
        stored, m = (l2 if l2 < l1 else l1), min(l1, l2)
        want = (f["rec_fixed"] + stored * f["rec_step"] + abs(l1 - l2) * f["align_step"]
                + (m - 1) * f["pair_step"] + f["found"])
        assert run["reason"] == 1 and o["term"] == f["term"]
        assert o["compressions"] == stored + abs(l1 - l2) + 2 * m + 2
        assert o["recovery"] == want, (l1, l2, o["recovery"], want)
        assert o["table"] == f["insert"] + f["match_extra"]  # one insertion, match at entry 0
    return f


SLICE = {"blake3-r7-slice-first-collision-w20-v1": (20, 5),
         "blake3-r7-slice-first-collision-w24-v1": (24, 12)}


def slice_trial(kern, kregs, seed, n, batches):
    """First repeat among 256 lane walks on one n-bit slice of f (proof Section H).

    g(u) = f(c | u) mod 2^n for u < 2^n, where c is a seed-derived point with
    its low n bits cleared. Lanes start at consecutive values r + l and are
    serialized in batch and lane order, as in the search. Returns the colliding
    inputs if the first event is an output equal to an earlier output, or
    None if it is an output equal to a start (or no event occurs)."""
    mask = (1 << n) - 1
    c = int.from_bytes(hashlib.sha256(b"slice" + seed).digest(), "little") & (M256 ^ mask)
    first = int.from_bytes(hashlib.sha256(b"start" + seed).digest(), "little") & mask
    inputs = [(first + l) & mask for l in range(256)]
    starts, seen = set(inputs), {}
    high = [M256 if (c >> j) & 1 else 0 for j in range(n, 256)]
    for _ in range(batches):
        r = [int("".join("1" if (u >> j) & 1 else "0" for u in reversed(inputs)), 2)
             for j in range(n)] + high + [0] * (kregs - 256)
        kern(r)
        bits = ["{:0256b}".format(r[j])[::-1] for j in range(n - 1, -1, -1)]
        outs = [int("".join(b[l] for b in bits), 2) for l in range(256)]
        for x, y in zip(inputs, outs):
            if y in seen:
                return (c | seen[y], c | x), 1
            if y in starts:
                return None, 2
            seen[y] = x
        inputs = outs
    return None, 3


def slice_main(request):
    n, batches = SLICE[request["experiment_id"]]
    event = dict(kind="digest-xor-mask", mask_hex=((1 << n) - 1).to_bytes(32, "little").hex(),
                 expected_hex=bytes(32).hex())
    if request["event"] != event or request["max_message_bytes"] < 64:
        raise ValueError("Unexpected organizer request")
    listing, kregs, pd = build_listing()
    assert pd == PD and len(listing) == 46113 and kregs == 776
    image = load(FULL, kregs, listing)[1]
    kern = compile_kernel(decode(image)[1])  # the decoded image's kernel
    rows = []
    for i, t in enumerate(request["trials"]):
        seed = bytes.fromhex(t["seed"])
        pair, code = slice_trial(kern, kregs, seed, n, batches)
        if pair and i < 8:  # spot-check returned pairs against scalar BLAKE3
            assert (digest_int(pair[0]) ^ digest_int(pair[1])) & ((1 << n) - 1) == 0
        rows.append(dict(trial=t["trial"],
                         message_a_hex=message(pair[0]).hex() if pair else None,
                         message_b_hex=message(pair[1]).hex() if pair else None,
                         observations=dict(outcome=code)))
    json.dump(dict(schema_version=1, trials=rows), sys.stdout,
              sort_keys=True, separators=(",", ":"))


def main():
    request = json.load(sys.stdin)
    if (request["schema_version"] == 1 and request["experiment_id"] in SLICE
            and request["target_profile"] == "blake3-r7-prefix-v1"):
        return slice_main(request)
    mask_hex = (0x3FFF).to_bytes(32, "little").hex()
    event = dict(kind="digest-xor-mask", mask_hex=mask_hex, expected_hex=bytes(32).hex())
    if (request["schema_version"] != 1
            or request["experiment_id"] != "blake3-r7-bounded-machine-w14-v1"
            or request["target_profile"] != "blake3-r7-prefix-v1"
            or request["event"] != event or request["max_message_bytes"] < 64):
        raise ValueError("Unexpected organizer request")
    listing, kregs, pd = build_listing()
    klen = len(listing)
    assert pd == PD and klen == 46113 and kregs == 776
    global KLIST
    KLIST = listing
    full, image = load(FULL, kregs, listing)
    assert full["nregs"] <= NREG  # every statically named word fits the declared file
    kern = compile_kernel(decode(image)[1])  # execute the decoded image's kernel
    nrules = check_rules()
    nfix = fixtures(klen, kregs)
    f = probes(klen, kregs)
    text = repr(listing).encode()
    p = dict(w=14, d=4, k=9, U=256, R=2, B=48, IDL=4096)
    wm = (1 << 14) - 1
    table = [digest_int(u) for u in range(1 << 14)]
    mach = Machine(load(p, kregs, KLIST)[0], klen)
    checked = [0]

    def checked_kernel(r):
        sel = ((checked[0] * 37) % 256, (checked[0] * 101 + 7) % 256, 0, 255)
        ins = [sum(((r[j] >> l) & 1) << j for j in range(256)) for l in sel]
        kern(r)
        for l, u in zip(sel, ins):
            out = sum(((r[j] >> l) & 1) << j for j in range(256))
            if out != table[u] ^ PD:
                raise AssertionError("kernel lane mismatch")
        checked[0] += 1

    rows = []
    for t in request["trials"]:
        seed = bytes.fromhex(t["seed"])
        rho = int.from_bytes(hashlib.sha256(seed).digest(), "little") & wm
        before = checked[0]
        run = mach.run(checked_kernel, lambda u: table[u], rho)
        step = lambda u: (table[u] ^ PD) & wm
        pair, s = bounded_search(step, width=14, dp_bits=4, key_bits=9, lanes=256,
                                 batches=p["B"], cap=p["R"], capacity=p["U"],
                                 start_limit=p["IDL"], rho=rho)
        agree(run, pair, s)
        # One full-width random batch; eight lanes checked against scalar BLAKE3.
        r = [int.from_bytes(hashlib.sha256(seed + bytes([j])).digest(), "little")
             for j in range(256)] + [0] * (kregs - 256)
        lanes = tuple(seed[:8])  # eight seed-chosen lanes
        ins = [sum(((r[j] >> l) & 1) << j for j in range(256)) for l in lanes]
        kern(r)
        for l, u in zip(lanes, ins):
            if sum(((r[j] >> l) & 1) << j for j in range(256)) != digest_int(u) ^ PD:
                raise AssertionError("full-width kernel lane mismatch")
        o = run["ops"]
        obs = dict(reason=run["reason"], batches=run["batches"], insertions=run["insertions"],
                   cuts=run["cuts"], starts=run["starts"],
                   compressions=o.get("compressions", 0),
                   kernel_lanes_checked=4 * (checked[0] - before) + len(lanes),
                   diag_ops=o.get("diag", 0),
                   control_ops=sum(v for g, v in o.items()
                                   if g not in ("kernel", "diag", "compressions")))
        extra = [
            dict(kernel_ops=klen, kernel_registers=kregs, fixtures_passed=nfix + nrules,
                 control_registers=full["nregs"] - kregs,
                 control_instructions=len(full["code"]) - 1,
                 code_bytes=code_bytes(full, klen), data_words=full["nmem"]),
            dict(batch_ops=f["batch"], setup_ops=f["setup"], epscan_ops=f["epscan"],
                 key_ops=f["key"], insert_ops=f["insert"], per_entry_ops=f["per_entry"],
                 restart_ops=f["restart"][2]),
            dict(cut_scan_ops=f["cut_scan"], cut_each_ops=f["cut_each"],
                 rec_fixed_ops=f["rec_fixed"], rec_step_ops=f["rec_step"],
                 align_step_ops=f["align_step"], pair_step_ops=f["pair_step"],
                 found_ops=f["found"]),
            dict(kernel_listing_sha256=int.from_bytes(hashlib.sha256(text).digest(), "big"),
                 output_polarity=pd, code_bytes_36=code_bytes(full, klen, 36),
                 cut_min_updates=f["cut_min"], term_ops=f["term"],
                 image_bytes=len(image),
                 image_sha256=int.from_bytes(hashlib.sha256(image).digest(), "big")),
        ]
        if t["trial"] < len(extra):
            obs.update(extra[t["trial"]])
        rows.append(dict(trial=t["trial"],
                         message_a_hex=message(pair[0]).hex() if pair else None,
                         message_b_hex=message(pair[1]).hex() if pair else None,
                         observations=obs))
    json.dump(dict(schema_version=1, trials=rows), sys.stdout,
              sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    main()
