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
registers are not memory-addressable); the endpoint table (64-bit slots: a
47-bit key and a 17-bit start identifier, four per word) and lane metadata
are memory, reached only by charged indirect loads and stores. It is
serialized into a byte image (4-byte three-operand kernel words behind an
8-byte KERNEL header, 8-byte control, 40-byte constant formats); every
program is decoded from its image before execution
and the round trip is asserted. A block interpreter executes the decoded
program and counts every priced operation. Checks performed:
  * kernel: a static check that the register-allocated listing computes the
    gate DAG for every input, and an exhaustive check of every gate rule
    (XOR, AND/OR with polarities, pivot full adder, ripple-carry words);
  * fixtures: the program and the scalar reference agree, under lane-wise test
    functions, on twelve control-flow cases with asserted outcomes;
  * probes: at the full-width parameters, measured operation counts of every
    handler equal the closed-form ledger formulas of proof.md;
  * trials: a 16-bit projected search on the selected target, executed by the
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
PD = 0x556AAB8650F00B0204EEFD1AF8507C4DAD1A08A430A609D996866A637669004D
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
        if p[0] == 0 and self.effpol(q) != self.effpol(r):
            # Constant pivot k with variable operands of different polarity:
            # sum = q ^ r ^ k and, with t = q ^ r, carry = maj(q, r, k) is
            # q & r = xx & ~t (k = 0) or q | r = xx ^ (~xx & other) (k = 1),
            # where xx is the operand whose polarity equals that of ~t; both
            # AND inputs then have equal polarity, so no complement is needed
            # (the rule of 76ab339a's generator, re-implemented from its text).
            t = self.xor(q, r)
            k = p[1]
            nt = (t[0], t[1] ^ 1)
            xx, other = (q, r) if self.effpol(q) == self.effpol(nt) else (r, q)
            if k == 0:
                return (t[0], t[1]), self.and_(xx, nt)
            return (t[0], t[1] ^ 1), self.xor(xx, self.and_((xx[0], xx[1] ^ 1), other))
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
        if r is None:
            # Reuse a dying operand's register unless it is an output's home
            # register below 256 (those stay reserved for their outputs).
            cand = [s for s in dying if reg_of[s] >= 256]
            if cand:
                r = reg_of[cand[0]]
                dying.remove(cand[0])
            elif free:
                r = free.pop()
            else:
                r, next_reg = next_reg, next_reg + 1
        listing.append((opc, r, reg_of[a], None if b is None else reg_of[b]))
        reg_of[dst] = r
        for s in dying:
            (reserved.add if reg_of[s] < 256 else free.append)(reg_of[s])
    gates = {k: sum(op[0] == k for op in ops) for k in ("XOR", "AND", "OR", "NOT")}
    assert gates == dict(XOR=37924, AND=2653, OR=5397, NOT=0)
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
                   capacity, start_limit, rho, stage1_bits=16, stage2_limit):
    """Scalar reference state machine."""
    # Distinguished: low dp_bits bits zero and the five-bit window at bits
    # dp_bits..dp_bits+4 below 23 (density 23/32 * 2^-dp_bits); key: bits
    # from dp_bits+5. A batch in which some lane has its low
    # min(stage1_bits, dp_bits) bits zero is a stage-1 hit; the run halts
    # (code 9) when the number of such batches exceeds stage2_limit.
    assert 0 < dp_bits and dp_bits + 5 + key_bits <= width and 0 < key_bits
    assert lanes <= start_limit <= 1 << width
    mask = (1 << width) - 1
    dp_mask = (1 << dp_bits) - 1
    s1_mask = (1 << min(stage1_bits, dp_bits)) - 1
    key_mask = (1 << key_bits) - 1

    def distinguished(u):
        return u & dp_mask == 0 and (u >> dp_bits) & 31 < 23
    states = [(rho + i) & mask for i in range(lanes)]
    ids = list(range(lanes))
    births = [0] * lanes
    next_id = lanes
    table = {}
    stats = dict(search_evaluations=0, recovery_evaluations=0,
                 final_evaluations=0, cuts=0, insertions=0, restarts=0,
                 max_age=0, reason=0, stage2=0)

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
            if distinguished(old_endpoint):
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
        if any(u & s1_mask == 0 for u in outputs):
            stats['stage2'] += 1
            if stats['stage2'] > stage2_limit:
                return finish(9)
        flags = [distinguished(u) for u in outputs]
        for lane in range(lanes):
            stats['max_age'] = max(stats['max_age'], batch - births[lane])
            if not flags[lane]:
                continue
            key = (outputs[lane] >> (dp_bits + 5)) & key_mask
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
            if not flags[lane] and batch - births[lane] >= cap:
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
REGIONS = ("setup", "loop", "stage2", "kernel", "diag", "epscan", "key", "table",
           "restart", "cut", "recovery", "term")
CTRL = ("ZERO ONE ONES C3 C23 C31 C256 M17 KM DPM PD BMAX RCAP ULIM IDL E2LIM WM RHO NID "
        "CNT B NEXTCUT EVT H2 D ND LANE KEY E S NOTLANE T0 T1 T2 T3 T4 T5 RR EIDX ID1 "
        "ID2 L1 L2 X Y A BV FA FB CN MINL MINB").split()


def build_program(p, kregs):
    """Emit the machine program for parameters p (see proof.md, Section M)."""
    w, d, k, U = p["w"], p["d"], p["k"], p["U"]
    diag = w < 256
    assert 1 < d and d + 5 + k <= w <= 256 and k <= 47 and p["IDL"] <= 1 << 17
    R = {n: kregs + i for i, n in enumerate(CTRL if diag else [c for c in CTRL if c != "WM"])}
    # Table entry: one 64-bit slot per entry holding the key in bits 0..k-1 and
    # the start identifier in bits 47..63; four slots per 256-bit word.
    keyw = -(-U // 4)
    KEYB, BIRB, LIDB = 0, keyw, keyw + 256
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
    consts = dict(ZERO=0, ONE=1, ONES=M256, C3=3, C23=23, C31=31, C256=256, M17=0x1FFFF,
                  KM=(1 << k) - 1, DPM=(1 << d) - 1, PD=PD, BMAX=p["B"], RCAP=p["R"],
                  ULIM=U, IDL=p["IDL"], E2LIM=p["E2MAX"] + 1)
    s1 = min(16, d)
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
    for n in ("NID", "CNT", "B", "LANE", "H2"):
        x3("MOV", n, "ZERO", None)
    lab("IL")
    e("LDI", R["RR"], 0)
    e("JMP", "RESTART")
    lab("RET0")
    e("ADDI", R["LANE"], R["LANE"], 1)
    e("BNE", R["LANE"], R["C256"], "IL")
    x3("MOV", "NEXTCUT", "RCAP", None)
    # EVT = min(NEXTCUT, BMAX): the next batch after which an event (age-cap
    # scan or horizon stop) must be considered.
    x3("MOV", "EVT", "RCAP", None)
    e("BLT", R["RCAP"], R["BMAX"], "LOOP")
    x3("MOV", "EVT", "BMAX", None)
    # Main loop; B counts the current batch (incremented after the kernel,
    # before any handler reads it).
    lab("LOOP")
    region[0] = "kernel"
    e("KERNEL")
    region[0] = "diag"
    for j in range(w, 256):
        e("XOR", j, j, j)
    region[0] = "loop"
    e("ADDI", R["B"], R["B"], 1)
    # Stage 1: lanes whose planes 0..s1-1 are all zero (bit 0 in D).
    e("OR", R["D"], 0, 1)
    for j in range(2, s1):
        e("OR", R["D"], R["D"], j)
    e("BNE", R["D"], R["ONES"], "S2")
    lab("EPD")
    e("BNE", R["B"], R["EVT"], "LOOP")
    # Event after batch B: age-cap scan if B >= NEXTCUT, horizon stop if B = BMAX.
    region[0] = "cut"
    e("BGE", R["B"], R["NEXTCUT"], "CUTB")
    lab("CUTD")
    e("BEQ", R["B"], R["BMAX"], "FAIL6")
    e("JMP", "LOOP")
    # Stage 2 (a batch with a stage-1 hit): count it against the budget, then
    # complete the distinguished test with planes s1..d-1 and the window.
    region[0] = "stage2"
    lab("S2")
    e("ADDI", R["H2"], R["H2"], 1)
    e("BGE", R["H2"], R["E2LIM"], "FAIL9")
    for j in range(s1, d):
        e("OR", R["D"], R["D"], j)
    # Window planes d..d+4 as a 5-bit value v: not distinguished if v >= 23,
    # that is bit4 and (bit3 or (bit2 and bit1 and bit0)).
    e("AND", R["T0"], d + 1, d)
    e("AND", R["T0"], R["T0"], d + 2)
    e("OR", R["T0"], R["T0"], d + 3)
    e("AND", R["T0"], R["T0"], d + 4)
    x3("OR", "D", "D", "T0")
    e("BNE", R["D"], R["ONES"], "EPB")
    e("JMP", "EPD")
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
        x3("SHR", "T0", d + 5 + j, "LANE")
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
    x3("AND", "T4", "T2", "KM")
    e("BEQ", R["T4"], R["KEY"], "MATCH")
    e("ADDI", R["EIDX"], R["EIDX"], 1)
    e("JMP", "SC")
    lab("NOM")
    e("BEQ", R["CNT"], R["ULIM"], "FAIL4")
    e("ADDI", R["T1"], R["LANE"], LIDB)
    x3("LD", "T5", "T1", None)
    e("SHLI", R["T5"], R["T5"], 47)
    x3("OR", "T5", "T5", "KEY")
    e("SHRI", R["T1"], R["CNT"], 2)
    e("ADDI", R["T1"], R["T1"], KEYB)
    x3("LD", "T2", "T1", None)
    x3("AND", "T3", "CNT", "C3")
    e("SHLI", R["T3"], R["T3"], 6)
    x3("SHL", "T4", "T5", "T3")
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
    x3("MOV", "EVT", "NEXTCUT", None)
    e("BLT", R["NEXTCUT"], R["BMAX"], "CUTD")
    x3("MOV", "EVT", "BMAX", None)
    e("JMP", "CUTD")
    # Recovery after a key match at entry EIDX for lane LANE.
    region[0] = "recovery"
    lab("MATCH")
    e("SHRI", R["ID1"], R["T2"], 47)
    x3("AND", "ID1", "ID1", "M17")
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
    e("SHRI", R["T0"], R["Y"], d)          # five-bit window below 23?
    x3("AND", "T0", "T0", "C31")
    e("BGE", R["T0"], R["C23"], "RC")
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
    for n in (2, 3, 4, 5, 6, 8, 9):
        lab("FAIL%d" % n)
        e("HALT", n)
    code = [(op, tuple(labels[a] if isinstance(a, str) else a for a in args), reg)
            for op, args, reg in code]
    return dict(code=code, labels=labels, nregs=kregs + len(R), nmem=LIDB + 256, ones=R["ONES"],
                regs=R, entry=0)


def code_bytes(prog, klen, per_instruction=None):
    """Declared encoding: kernel 4 bytes per instruction behind an 8-byte KERNEL
    header; control 8; LDI 40."""
    n = sum(op != "KERNEL" for op, _, _ in prog["code"])
    if per_instruction is not None:
        return per_instruction * (klen + n + 1)
    return 4 * klen + sum(40 if op == "LDI" else 8 for op, _, _ in prog["code"])


SHORT = ("XOR", "AND", "OR", "NOT", "MOV")
LONG = SHORT + ("ADD", "ADDI", "SUB", "SHL", "SHR", "SHLI", "SHRI", "LD", "ST", "BEQ",
                "BNE", "BLT", "BGE", "JMP", "RAND", "COMP", "OUT", "HALT", "KERNEL")
BRANCH = ("BEQ", "BNE", "BLT", "BGE", "JMP")
IMM = ("ADDI", "SHLI", "SHRI", "HALT", "KERNEL")
KOPS = ("XOR", "AND", "OR")


def kernel_forms(listing, ones):
    """Register-only three-operand forms: NOT d,a = XOR d,a,ONES; MOV d,a = OR d,a,a."""
    return [("XOR", d, a, ones) if opc == "NOT" else ("OR", d, a, a) if opc == "MOV"
            else (opc, d, a, b) for opc, d, a, b in listing]


def encode(prog, listing):
    """Serialize the program image (proof.md Section 3.2).

    8-byte control format: opcode 16.. | r1<<8 | r2<<18 | r3<<28 | imm24<<38;
    the KERNEL instruction carries the block length in imm24 and is followed
    by that many 4-byte kernel words: opcode 1..3 | d<<2 | a<<12 | b<<22
    (three-operand XOR/AND/OR only; NOT d,a is XOR d,a,ONES, MOV d,a is
    OR d,a,a). 40-byte LDI format: opcode 64 | r1<<8 | imm256<<18. Branch
    targets are byte offsets into the image."""
    offsets, pos = [], 0
    for op, _, _ in prog["code"]:
        offsets.append(pos)
        pos += 8 + 4 * len(listing) if op == "KERNEL" else 40 if op == "LDI" else 8
    out = bytearray()
    for op, args, _ in prog["code"]:
        if op == "KERNEL":
            out += (16 + LONG.index("KERNEL") | len(listing) << 38).to_bytes(8, "little")
            for opc, d, a, b in kernel_forms(listing, prog["ones"]):
                assert 0 <= d < 1024 and 0 <= a < 1024 and 0 <= b < 1024
                out += (1 + KOPS.index(opc) | d << 2 | a << 12 | b << 22).to_bytes(4, "little")
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
        if op == 16 + LONG.index("KERNEL"):
            v = int.from_bytes(image[pos:pos + 8], "little")
            count, pos = v >> 38, pos + 8
            start = pos
            for _ in range(count):
                w = int.from_bytes(image[pos:pos + 4], "little")
                raw.append((pos if pos == start else None, "K",
                            (KOPS[(w & 3) - 1], w >> 2 & 1023, w >> 12 & 1023, w >> 22 & 1023)))
                pos += 4
            raw[-count] = (start - 8, "K", raw[-count][2])
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
                 RAND=1, JMP=0, HALT=0, KERNEL=0)
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
    assert code == norm and decoded == kernel_forms(listing, prog["ones"])
    assert len(image) == code_bytes(prog, len(listing))
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
                cost[reg] += klen + 1 if op == "KERNEL" else COST.get(op, 1)
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
        self.stage2_block = self.block_of[prog["labels"]["S2"]]

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
                    cuts=counts[self.cut_block], stage2=counts[self.stage2_block],
                    insertions=r[R["CNT"]], starts=r[R["NID"]], ops=dict(ops), r=r)


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
    keys = ("reason", "insertions", "cuts", "stage2")
    ok = all(run[k] == s[k] for k in keys) and run["pair"] == pair
    ok = ok and run["starts"] == s["allocated_starts"]
    ok = ok and run["batches"] * 256 == s["search_evaluations"]
    ok = ok and run["ops"].get("compressions", 0) == s["recovery_evaluations"] + s["final_evaluations"]
    if not ok:
        raise AssertionError("machine and reference disagree: %r %r %r" % (run, pair, s))


def fixtures(klen, kregs):
    base = dict(w=13, d=3, k=4, U=8, R=4, B=4, IDL=2048, E2MAX=1000)
    rho = 256
    cases = [  # (overrides, parameter changes, expected reason)
        ({256: 8, 257: 8}, {}, 1),
        ({256: 8, 257: 8 | 4096}, {}, 2),
        ({256: 257, 257: 8}, {}, 3),
        ({256: 8}, dict(U=0), 4),
        ({256: 3, 3: 16}, dict(R=2, B=3), 6),
        ({}, dict(R=1, B=5), 6),
        ({256: 8, 257: 16 | 256}, dict(U=1), 4),   # second endpoint has a different key
        ({}, dict(R=1, B=2, IDL=300), 5),
        ({256: 8, 300: 8}, {}, 1),
        ({256: 5, 5: 7, 7: 8, 257: 9, 9: 8}, {}, 1),
        ({256: 8}, dict(E2MAX=0), 9),                # stage-1 hit budget exhausted
        ({256: 8, 300: 8}, dict(E2MAX=1), 1),        # one stage-2 batch allowed
        ({256: 184}, {}, 6),                         # stage-1 hit with window 23: not distinguished
    ]
    for over, change, want in cases:
        p = dict(base, **change)
        fn = lambda u, o=over: o.get(u, u | 1)
        mach = Machine(load(p, kregs, KLIST)[0], klen)
        run = mach.run(lanewise(fn), lambda u, f=fn: f(u) ^ PD, rho)
        pair, s = bounded_search(fn, width=p["w"], dp_bits=p["d"], key_bits=p["k"],
                                 lanes=256, batches=p["B"], cap=p["R"], capacity=p["U"],
                                 start_limit=p["IDL"], rho=rho, stage2_limit=p["E2MAX"])
        agree(run, pair, s)
        assert run["reason"] == want, (over, run["reason"])
    return len(cases)


KLIST = None
BGRAIN = 1045778                                  # B = BGRAIN x 2^100 (proof Section 2.1)
FULL = dict(w=256, d=111, k=47, U=98400, R=-(-12 * 2 ** 116 // 23), B=BGRAIN * 2 ** 100,
            IDL=1 << 17, E2MAX=3 * BGRAIN * 2 ** 92)   # E2MAX = 3 Q / 2^16


def formulas(p, klen):
    """Closed-form operation counts of the program text (proof.md, Section L)."""
    d, k, nmem = p["d"], p["k"], -(-p["U"] // 4) + 512
    s1 = min(16, d)
    rs = {0: 1292, 1: 1294, 2: 1295}
    # Per batch: KERNEL header 1 + kernel + ADDI 1 + (s1 - 1) ORs + BNE 2 + BNE 2.
    # Stage 2: ADDI 1 + BGE 2 + (d - s1) ORs + 5 window operations (incl. the OR into D)
    # + BNE 2 (+ JMP 1 on a miss). Event: BGE 2 + BEQ 2 + JMP 1.
    return dict(batch=klen + s1 + 5, stage2=d - s1 + 10, stage2_miss=d - s1 + 11, event=5,
                setup=17 + 2 + 4 * nmem + 5 + 256 * (5 + rs[0]) + 4,
                epscan=1795, key=1 + 4 * k, insert=20, per_entry=13, restart=rs,
                cut_scan=2566, cut_min=256, cut_each=3, rec_fixed=1046, rec_step=76,
                align_step=69, pair_step=138, found=268, term=3, min_update=1,
                terminal=13 * p["U"] + 5, match_extra=12)


def probes(klen, kregs):
    """Measure handler costs at the full-width parameters with test functions."""
    f = formulas(FULL, klen)
    L = 2 ** (FULL["d"] + 5)      # distinguished (window 0) with distinct keys (l + 1)
    rho = (1 << 200) + 12345
    mach = Machine(load(FULL, kregs, KLIST)[0], klen)
    plain = lambda u: u | 1
    comp = lambda fn: (lambda u: fn(u) ^ PD)
    run = mach.run(lanewise(plain), comp(plain), rho, stop_after=3)
    o = run["ops"]
    assert o["kernel"] == 3 * (klen + 1) and o["loop"] == 3 * (f["batch"] - klen - 1)
    assert o["setup"] + o["restart"] == f["setup"], (o, f["setup"])
    # A stage-1 hit that is not distinguished (window value 23): stage-2 miss path.
    miss = (23 << FULL["d"]) | (1 << 200)
    fn = lambda u: miss if u == rho else u | 1
    o = mach.run(lanewise(fn), comp(fn), rho, stop_after=1)["ops"]
    assert o.get("stage2", 0) == f["stage2_miss"] and o.get("epscan", 0) == 0, o.get("stage2")
    for n in range(4):  # n endpoints in batch one, table counts 0..n-1
        over = {(rho + l) & M256: (l + 1) * L for l in range(n)}
        fn = lambda u, o=over: o.get(u, u | 1)
        o = mach.run(lanewise(fn), comp(fn), rho, stop_after=1)["ops"]
        assert o.get("epscan", 0) == (f["epscan"] if n else 0)
        assert o.get("stage2", 0) == (f["stage2"] if n else 0), (n, o.get("stage2"), f["stage2"])
        assert o.get("key", 0) == n * f["key"]
        assert o.get("table", 0) == n * f["insert"] + f["per_entry"] * n * (n - 1) // 2
        assert o["restart"] - 256 * f["restart"][0] == n * f["restart"][1]
    cutp = dict(FULL, R=1)
    mc = Machine(load(cutp, kregs, KLIST)[0], klen)
    run = mc.run(lanewise(plain), comp(plain), rho, stop_after=1)
    o = run["ops"]
    assert run["cuts"] == 256 and o["cut"] == f["event"] + f["cut_scan"] + 256 * f["cut_each"], o["cut"]
    assert o["restart"] == 256 * (f["restart"][0] + f["restart"][2])
    # Lane 0 ends at batch 1; at batch 2 the other 255 lanes are cut and the
    # running minimum is updated once (lane 0's birth 1 < 2).
    fn = lambda u: L if u == rho else u | 1
    mc = Machine(load(dict(FULL, R=2), kregs, KLIST)[0], klen)
    run = mc.run(lanewise(fn), comp(fn), rho, stop_after=2)
    assert run["cuts"] == 255
    assert run["ops"]["cut"] == f["event"] + f["cut_scan"] + f["min_update"] + 255 * f["cut_each"], run["ops"]["cut"]
    # Capacity terminal: U = 1, two endpoints with distinct keys in batch one.
    fn = lambda u: L if u == rho else 2 * L if u == (rho + 1) & M256 else u | 1
    mu = Machine(load(dict(FULL, U=1), kregs, KLIST)[0], klen)
    run = mu.run(lanewise(fn), comp(fn), rho)
    assert run["reason"] == 4
    assert run["ops"]["table"] == f["insert"] + 13 * 1 + 5
    # Recovery with stored length l1 and current length l2 (direct chains).
    for l1, l2 in ((1, 1), (2, 3), (3, 1), (4, 4)):
        def chain(start, length, tag):
            # Intermediate points with the low d bits zero but window value 23:
            # not distinguished, exercising the window test of the recovery loop.
            pts = [start] + [(tag << 120) | (i << (FULL["d"] + 6)) | (23 << FULL["d"])
                             for i in range(1, length)]
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


def slice_trial(kern, nregs, ones, seed, n, batches):
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
             for j in range(n)] + high + [0] * (nregs - 256)
        r[ones] = M256
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
    assert pd == PD and len(listing) == 45974 and kregs == 771
    prog, image = load(FULL, kregs, listing)
    kern = compile_kernel(decode(image)[1])  # the decoded image's kernel
    rows = []
    for i, t in enumerate(request["trials"]):
        seed = bytes.fromhex(t["seed"])
        pair, code = slice_trial(kern, prog["nregs"], prog["ones"], seed, n, batches)
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
    mask_hex = (0xFFFF).to_bytes(32, "little").hex()
    event = dict(kind="digest-xor-mask", mask_hex=mask_hex, expected_hex=bytes(32).hex())
    if (request["schema_version"] != 1
            or request["experiment_id"] != "blake3-r7-bounded-machine-w16-v3"
            or request["target_profile"] != "blake3-r7-prefix-v1"
            or request["event"] != event or request["max_message_bytes"] < 64):
        raise ValueError("Unexpected organizer request")
    listing, kregs, pd = build_listing()
    klen = len(listing)
    assert pd == PD and klen == 45974 and kregs == 771
    global KLIST
    KLIST = listing
    full, image = load(FULL, kregs, listing)
    assert full["nregs"] <= NREG  # every statically named word fits the declared file
    kern = compile_kernel(decode(image)[1])  # execute the decoded image's kernel
    nrules = check_rules()
    nfix = fixtures(klen, kregs)
    f = probes(klen, kregs)
    text = repr(listing).encode()
    p = dict(w=16, d=3, k=8, U=256, R=2, B=48, IDL=4096, E2MAX=4608)
    wm = (1 << 16) - 1
    table = [digest_int(u) for u in range(1 << 16)]
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
        pair, s = bounded_search(step, width=16, dp_bits=3, key_bits=8, lanes=256,
                                 batches=p["B"], cap=p["R"], capacity=p["U"],
                                 start_limit=p["IDL"], rho=rho, stage2_limit=p["E2MAX"])
        agree(run, pair, s)
        # One full-width random batch; eight lanes checked against scalar BLAKE3.
        r = [int.from_bytes(hashlib.sha256(seed + bytes([j])).digest(), "little")
             for j in range(256)] + [0] * (full["nregs"] - 256)
        r[full["ones"]] = M256
        lanes = tuple(seed[:8])  # eight seed-chosen lanes
        ins = [sum(((r[j] >> l) & 1) << j for j in range(256)) for l in lanes]
        kern(r)
        for l, u in zip(lanes, ins):
            if sum(((r[j] >> l) & 1) << j for j in range(256)) != digest_int(u) ^ PD:
                raise AssertionError("full-width kernel lane mismatch")
        o = run["ops"]
        obs = dict(reason=run["reason"], batches=run["batches"], insertions=run["insertions"],
                   cuts=run["cuts"], stage2=run["stage2"], starts=run["starts"],
                   compressions=o.get("compressions", 0),
                   kernel_lanes_checked=4 * (checked[0] - before) + len(lanes))
        extra = [
            dict(kernel_ops=klen, kernel_registers=kregs, fixtures_passed=nfix + nrules,
                 control_registers=full["nregs"] - kregs,
                 control_instructions=len(full["code"]) - 1,
                 code_bytes=code_bytes(full, klen), data_words=full["nmem"]),
            dict(batch_ops=f["batch"], stage2_ops=f["stage2"], setup_ops=f["setup"], epscan_ops=f["epscan"],
                 key_ops=f["key"], insert_ops=f["insert"], per_entry_ops=f["per_entry"],
                 restart_ops=f["restart"][2]),
            dict(cut_scan_ops=f["cut_scan"], cut_each_ops=f["cut_each"], event_ops=f["event"],
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
