"""40-round SHA-256 bit-sliced Walk-B birthday collision search & verifier.

Self-contained Python stdlib implementation for target sha256-r40-prefix-v1:
- 64-byte two-block message family with 8-word constant prefix W[0..7] cancelling K[8], K[9]
- 43,548-gate 0-NOT, 0-mixed-polarity, 0-MOV Walk-B bit-sliced kernel (860 data regs + 3 ptrs)
- 3-template 32/32 polarity-universal 276-gate add3 + bit-0 add5/add6 fusion + ALL_ONES polarity-wave steering
- 1,249-op 2-lane SIMD Walk-B recovery evaluator (verified 256/256 against bit-sliced stream)
- Exact 80-digit outward-rounded Lemma 2 + Gamma(2f+3) multi-hit 37-bit key proof (>= 0.390000001) & ledger
- Deterministic organizer python-message-pairs-v1 experiments (w=16 bounded DP & w=14 projection)
"""
from collections import defaultdict
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
import hashlib
import heapq
import itertools
import json
import math
import struct
import sys

MASK = 0xFFFFFFFF
ROUNDS = 40
C_REF = 2896

IV = (
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
)

K = (
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
)

# Unique 8-word constant prefix W[0..7] forcing state after step 7 to
# st8 = (0, 0, 0, 0, 0, 0, -K[9], K[9] - K[8]) so K[8] and K[9] cancel identically.
PREFIX_W = (
    0x3e73281c, 0x752d8ed2, 0xad19eff1, 0x7250fceb,
    0xd4095422, 0x44fdb519, 0x43f22c5b, 0xd8d6aac4,
)
ST8 = (0, 0, 0, 0, 0, 0, (-K[9]) & MASK, (K[9] - K[8]) & MASK)
E_FLIP_MASKS = {
    17: 0x04000000, 18: 0x00008000, 19: 0x00001000, 20: 0x00400000,
    21: 0x00000080, 25: 0x00000010, 32: 0x04000002, 33: 0x00900000,
    34: 0x00020000, 35: 0x00110000,
}
A_FLIP_MASKS = {
    17: 0x00040000, 22: 0x00000010, 26: 0x00000800, 28: 0x00002000,
    29: 0x80000000, 30: 0x00000008, 31: 0x00000080, 32: 0x01000000,
}
S1_FLIP_MASKS = {37: 0x00000002}

PAD_BLOCK_64 = b"\x80" + bytes(55) + (512).to_bytes(8, "big")


def rotr32(x, n):
    return ((x >> n) | (x << (32 - n))) & MASK

def S0_32(x):
    return rotr32(x, 2) ^ rotr32(x, 13) ^ rotr32(x, 22)

def S1_32(x):
    return rotr32(x, 6) ^ rotr32(x, 11) ^ rotr32(x, 25)

def s0_32(x):
    return rotr32(x, 7) ^ rotr32(x, 18) ^ (x >> 3)

def s1_32(x):
    return rotr32(x, 17) ^ rotr32(x, 19) ^ (x >> 10)

def Ch32(e, f, g):
    return (e & f) ^ ((~e & MASK) & g)

def Maj32(a, b, c):
    return (a & b) ^ (a & c) ^ (b & c)


def compress_r40(cv, block):
    w = list(struct.unpack(">16I", block))
    for i in range(16, ROUNDS):
        w.append((s1_32(w[i - 2]) + w[i - 7] + s0_32(w[i - 15]) + w[i - 16]) & MASK)
    a, b, c, d, e, f, g, h = cv
    for i in range(ROUNDS):
        t1 = (h + S1_32(e) + Ch32(e, f, g) + K[i] + w[i]) & MASK
        t2 = (S0_32(a) + Maj32(a, b, c)) & MASK
        a, b, c, d, e, f, g, h = (t1 + t2) & MASK, a, b, c, (d + t1) & MASK, e, f, g
    return tuple((cv[j] + x) & MASK for j, x in enumerate((a, b, c, d, e, f, g, h)))


def sha256_r40(msg):
    ml = len(msg)
    padded = msg + b"\x80" + b"\x00" * ((55 - ml) % 64) + (8 * ml).to_bytes(8, "big")
    cv = IV
    for off in range(0, len(padded), 64):
        cv = compress_r40(cv, padded[off : off + 64])
    return struct.pack(">8I", *cv)


def y_to_msg64(y_words):
    w8_15 = [y_words[0] & MASK, y_words[1] & MASK] + [
        (y_words[k] - K[8 + k]) & MASK for k in range(2, 8)
    ]
    return struct.pack(">16I", *(list(PREFIX_W) + w8_15))


def walk_b_inverse_to_digest(co, QM, XM, x_cv, y_cv):
    e37, e38, a33, a34, Q34, t1_35, X38, Y39 = co
    q_corr = (((a34 ^ a33) & QM) - QM) & MASK
    a35 = (Q34 + q_corr + (a34 & a33) + S0_32(a34)) & MASK
    a36 = (t1_35 + S0_32(a35) + Maj32(a35, a34, a33)) & MASK
    t1_36 = (e37 - a33) & MASK
    a37 = (t1_36 + S0_32(a36) + Maj32(a36, a35, a34)) & MASK
    t1_37 = (e38 - a34) & MASK
    a38 = (t1_37 + S0_32(a37) + Maj32(a37, a36, a35)) & MASK
    x_corr = ((((~e38) & MASK) & XM) - XM + x_cv) & MASK
    t1_38 = (X38 + x_corr + S1_32(e38) + (e38 & e37) + K[38]) & MASK
    e39 = (a35 + t1_38) & MASK
    a39 = (t1_38 + S0_32(a38) + Maj32(a38, a37, a36)) & MASK
    t1_39 = (Y39 + y_cv + S1_32(e39) + Ch32(e39, e38, e37) + K[39]) & MASK
    a40 = (t1_39 + S0_32(a39) + Maj32(a39, a38, a37)) & MASK
    e40 = (a36 + t1_39) & MASK
    cv1 = tuple((IV[j] + x) & MASK for j, x in enumerate((a40, a39, a38, a37, e40, e39, e38, e37)))
    cv2 = compress_r40(cv1, PAD_BLOCK_64)
    return struct.pack(">8I", *cv2)


class WalkBCircuit:
    """Zero-NOT, zero-mixed-polarity 256-lane bit-sliced 40-round Walk-B builder."""

    def __init__(self):
        self.n_inputs = 257  # 256 state planes (1..256) + ALL_ONES constant register (257)
        self.ALL_ONES_WID = 257
        self.gates = []
        self.cse = {}
        self.xor_def = {}
        self.next_wid = 258
        self.mixed_and = 0
        self.mixed_or = 0

    def _gate(self, op, a, b):
        if a > b:
            a, b = b, a
        key = (op, a, b)
        if key in self.cse:
            return self.cse[key]
        wid = self.next_wid
        self.next_wid += 1
        self.gates.append((op, a, b))
        self.cse[key] = wid
        if op == "XOR":
            self.xor_def[wid] = (a, b)
        return wid

    def flip_pol(self, r):
        if r <= 1:
            return r
        wid = self._gate("XOR", r >> 1, self.ALL_ONES_WID)
        return (wid << 1) | ((r & 1) ^ 1)

    def _has_xor(self, a, b):
        if a <= 1 or b <= 1 or a == b or a == (b ^ 1):
            return True
        wa, wb = a >> 1, b >> 1
        if wa > wb:
            wa, wb = wb, wa
        return ("XOR", wa, wb) in self.cse

    def has_assoc_xor(self, a, b):
        if self._has_xor(a, b):
            return True
        if b >= 2 and (b >> 1) in self.xor_def:
            u, v = self.xor_def[b >> 1]
            if self._has_xor(a, u << 1) or self._has_xor(a, v << 1):
                return True
        if a >= 2 and (a >> 1) in self.xor_def:
            u, v = self.xor_def[a >> 1]
            if self._has_xor(b, u << 1) or self._has_xor(b, v << 1):
                return True
        return False

    def XOR(self, a, b):
        if a == 0: return b
        if b == 0: return a
        if a == 1: return b ^ 1
        if b == 1: return a ^ 1
        if a == b: return 0
        if a == (b ^ 1): return 1
        inv = (a ^ b) & 1
        wa, wb = a >> 1, b >> 1
        if wa > wb:
            wa, wb = wb, wa
        if ("XOR", wa, wb) in self.cse:
            return (self.cse[("XOR", wa, wb)] << 1) | inv
        if wb in self.xor_def:
            u, v = self.xor_def[wb]
            k1 = ("XOR", min(wa, u), max(wa, u))
            if k1 in self.cse:
                return (self._gate("XOR", self.cse[k1], v) << 1) | inv
            k2 = ("XOR", min(wa, v), max(wa, v))
            if k2 in self.cse:
                return (self._gate("XOR", self.cse[k2], u) << 1) | inv
        if wa in self.xor_def:
            u, v = self.xor_def[wa]
            k1 = ("XOR", min(wb, u), max(wb, u))
            if k1 in self.cse:
                return (self._gate("XOR", self.cse[k1], v) << 1) | inv
            k2 = ("XOR", min(wb, v), max(wb, v))
            if k2 in self.cse:
                return (self._gate("XOR", self.cse[k2], u) << 1) | inv
        return (self._gate("XOR", wa, wb) << 1) | inv

    def AND(self, a, b):
        if a == 0 or b == 0: return 0
        if a == 1: return b
        if b == 1: return a
        if a == b: return a
        if a == (b ^ 1): return 0
        if (a & 1) and (b & 1):
            return (self._gate("OR", a >> 1, b >> 1) << 1) | 1
        if not (a & 1) and not (b & 1):
            return self._gate("AND", a >> 1, b >> 1) << 1
        self.mixed_and += 1
        if a & 1:
            return self.XOR(b, self._gate("AND", a >> 1, b >> 1) << 1)
        return self.XOR(a, self._gate("AND", a >> 1, b >> 1) << 1)

    def OR(self, a, b):
        if a == 1 or b == 1: return 1
        if a == 0: return b
        if b == 0: return a
        if a == b: return a
        if a == (b ^ 1): return 1
        if (a & 1) and (b & 1):
            return (self._gate("AND", a >> 1, b >> 1) << 1) | 1
        if not (a & 1) and not (b & 1):
            return self._gate("OR", a >> 1, b >> 1) << 1
        self.mixed_or += 1
        if a & 1:
            return self.XOR(a ^ 1, self._gate("AND", a >> 1, b >> 1) << 1) ^ 1
        return self.XOR(b ^ 1, self._gate("AND", a >> 1, b >> 1) << 1) ^ 1

    def mux(self, sel, t_in, f_in):
        if sel == 0: return f_in
        if sel == 1: return t_in
        if t_in == f_in: return t_in
        d = self.XOR(t_in, f_in)
        if d == 0: return f_in
        if d == 1: return self.XOR(f_in, sel)
        if (sel & 1) == (d & 1):
            return self.XOR(f_in, self.AND(sel, d))
        return self.XOR(t_in, self.AND(sel ^ 1, d))

    def const_word(self, val): return [1 if ((val >> i) & 1) else 0 for i in range(32)]
    def rotr(self, w, n): return [w[(i + n) % 32] for i in range(32)]
    def shr(self, w, n): return [w[i + n] if i + n < 32 else 0 for i in range(32)]
    def xor3_word(self, a, b, c): return [self.XOR(self.XOR(a[i], b[i]), c[i]) for i in range(32)]
    def S0(self, x): return self.xor3_word(self.rotr(x, 2), self.rotr(x, 13), self.rotr(x, 22))
    def S1(self, x): return self.xor3_word(self.rotr(x, 6), self.rotr(x, 11), self.rotr(x, 25))
    def s0(self, x): return self.xor3_word(self.rotr(x, 7), self.rotr(x, 18), self.shr(x, 3))
    def s1(self, x): return self.xor3_word(self.rotr(x, 17), self.rotr(x, 19), self.shr(x, 10))
    def Ch(self, e, f, g): return [self.mux(e[i], f[i], g[i]) for i in range(32)]

    def Maj(self, a, b, c):
        if all(x == 0 for x in c):
            return [self.AND(a[i], b[i]) for i in range(32)]
        return [self.mux(self.XOR(b[i], c[i]), a[i], b[i]) for i in range(32)]

    def ha(self, a, b):
        if a == 0: return b, 0
        if b == 0: return a, 0
        if a == 1: return b ^ 1, b
        if b == 1: return a ^ 1, a
        s = self.XOR(a, b)
        if (a & 1) == (b & 1):
            return s, self.AND(a, b)
        if (a & 1) == 0:
            return s, self.AND(a, s ^ 1)
        return s, self.AND(b, s ^ 1)

    def ha1(self, a, b):
        if a == 0: return b ^ 1, b
        if b == 0: return a ^ 1, a
        if a == 1: return b, 1
        if b == 1: return a, 1
        t = self.XOR(a, b)
        if (a & 1) == (b & 1):
            return t ^ 1, self.OR(a, b)
        if (a & 1) == 1:
            return t ^ 1, self.OR(a, t)
        return t ^ 1, self.OR(b, t)

    def ha_assoc(self, a, b):
        if a == 0: return b, 0
        if b == 0: return a, 0
        if a == 1: return b ^ 1, b
        if b == 1: return a ^ 1, a
        if not self.has_assoc_xor(a, b):
            return self.ha(a, b)
        s = self.XOR(a, b)
        if (a & 1) == ((s ^ 1) & 1):
            return s, self.AND(a, s ^ 1)
        return s, self.XOR(a, self.AND(a, s))

    def ha1_assoc(self, a, b):
        if a == 0: return b ^ 1, b
        if b == 0: return a ^ 1, a
        if a == 1: return b, 1
        if b == 1: return a, 1
        if not self.has_assoc_xor(a, b):
            return self.ha1(a, b)
        s = self.XOR(a, b)
        if (a & 1) == (s & 1):
            return s ^ 1, self.OR(a, s)
        return s ^ 1, self.XOR(a, self.AND(a ^ 1, s))

    def _ha_assoc_cost(self, a, b, cin):
        if not self.has_assoc_xor(a, b):
            return 2
        pb = b & 1
        return (1 if pb == 1 else 2) if cin == 0 else (1 if pb == 0 else 2)

    def _acw_cost(self, cv):
        cv &= MASK
        if cv == 0: return 0
        tz = (cv & -cv).bit_length() - 1
        return 0 if tz == 31 else 2 * (31 - tz) - 1

    def fa(self, a, b, c):
        if a == 0: return self.ha(b, c)
        if b == 0: return self.ha(a, c)
        if c == 0: return self.ha(a, b)
        if a == 1: return self.ha1(b, c)
        if b == 1: return self.ha1(a, c)
        if c == 1: return self.ha1(a, b)
        if self.has_assoc_xor(a, b):
            t = self.XOR(a, b)
            return self.XOR(t, c), self.mux(t, c, a)
        if self.has_assoc_xor(a, c):
            t = self.XOR(a, c)
            return self.XOR(t, b), self.mux(t, b, a)
        if self.has_assoc_xor(b, c):
            t = self.XOR(b, c)
            return self.XOR(t, a), self.mux(t, a, b)
        if (a & 1) == (b & 1):
            p, u, v = (a, b, c) if (a & 1) == (c & 1) else (c, a, b)
        elif (a & 1) == (c & 1):
            p, u, v = b, a, c
        else:
            p, u, v = a, b, c
        t1 = self.XOR(p, u)
        t2 = self.XOR(p, v)
        return self.XOR(t1, v), self.XOR(p, self.AND(t1, t2))

    def add2(self, a, b, cin=0):
        out, c = [0]*32, cin
        for i in range(32):
            if i < 31: out[i], c = self.fa(a[i], b[i], c)
            else: out[i] = self.XOR(self.XOR(a[i], b[i]), c)
        return out

    def add_const_word(self, w, cv):
        cv &= MASK
        if cv == 0: return w
        out = list(w)
        first1 = (cv & -cv).bit_length() - 1
        out[first1] = w[first1] ^ 1
        c = w[first1]
        for i in range(first1 + 1, 32):
            if i == 31:
                out[31] = self.XOR(w[31], c) ^ ((cv >> 31) & 1)
            else:
                out[i], c = self.ha1(w[i], c) if ((cv >> i) & 1) else self.ha(w[i], c)
        return out

    def pair_col(self, x, y, z, u, U, need_u1=True):
        if u == 0 and U == 0:
            s, c = self.fa(x, y, z)
            return s, (c if need_u1 else 0), c
        if u == 1 and U == 0:
            s, c = self.fa(x, y, z)
            return s, (1 if need_u1 else 0), c ^ 1
        if U == 1:
            if (x & 1) == (y & 1): a, b, c = z, x, y
            elif (x & 1) == (z & 1): a, b, c = y, x, z
            else: a, b, c = x, y, z
            w1 = self.XOR(a, b)
            return self.XOR(w1, c) ^ 1, (a if need_u1 else 0), self.OR(w1, self.XOR(a, c))
        if x <= 1 or y <= 1 or z <= 1:
            if (x & 1) == (y & 1): a, b, c = z, x, y
            elif (x & 1) == (z & 1): a, b, c = y, x, z
            else: a, b, c = x, y, z
            w5 = self.XOR(a, b); w6 = self.XOR(c, w5); s = self.XOR(U, w6); w9 = self.XOR(u, w6)
            gA = self.OR(U, w9 ^ 1); gB = self.OR(w5, self.XOR(a, c))
            return s, (self.XOR(w6, gA ^ 1) if need_u1 else 0), self.XOR(gA, gB ^ 1)
        pu, pU = u & 1, U & 1
        ops = (x, y, z)
        for a, b, c in itertools.permutations(ops):
            pa, pb, pc = a & 1, b & 1, c & 1
            if not self.has_assoc_xor(a, b):
                continue
            if pU == (pc ^ pu) and pb != (pc ^ pU):
                w1 = self.XOR(c, u); gA = self.OR(U, w1); w2 = self.XOR(a, b); w3 = self.XOR(c, U)
                s = self.XOR(w2, w3); w4 = self.XOR(a, w3); gB = self.OR(w2, w4 ^ 1)
                return s, (self.XOR(w3 ^ 1, gB) if need_u1 else 0), self.XOR(gA ^ 1, gB)
            if pU == (1 ^ pu ^ pa ^ pb ^ pc) and pb == pc:
                w5 = self.XOR(a, b); w6 = self.XOR(c, w5); s = self.XOR(U, w6); w9 = self.XOR(u, w6)
                gA = self.OR(U, w9 ^ 1); gB = self.OR(w5, self.XOR(a, c))
                return s, (self.XOR(w6, gA ^ 1) if need_u1 else 0), self.XOR(gA, gB ^ 1)
        for a, b, c in itertools.permutations(ops):
            pa, pb, pc = a & 1, b & 1, c & 1
            if pU == (pc ^ pu) and pb != (pc ^ pU):
                w1 = self.XOR(c, u); gA = self.OR(U, w1); w2 = self.XOR(a, b); w3 = self.XOR(c, U)
                s = self.XOR(w2, w3); w4 = self.XOR(a, w3); gB = self.OR(w2, w4 ^ 1)
                return s, (self.XOR(w3 ^ 1, gB) if need_u1 else 0), self.XOR(gA ^ 1, gB)
            if pU == (pc ^ pu) and pa == pb:
                w1 = self.XOR(c, u); gA = self.OR(U, w1); w3 = self.XOR(c, U)
                w4 = self.XOR(a, w3); w5 = self.XOR(b, w3); s = self.XOR(w4, b); gB = self.AND(w4, w5)
                return s, (self.XOR(w3, gB) if need_u1 else 0), self.XOR(gA, gB)
            if pU == (1 ^ pu ^ pa ^ pb ^ pc) and pb == pc:
                w5 = self.XOR(a, b); w6 = self.XOR(c, w5); s = self.XOR(U, w6); w9 = self.XOR(u, w6)
                gA = self.OR(U, w9 ^ 1); gB = self.OR(w5, self.XOR(a, c))
                return s, (self.XOR(w6, gA ^ 1) if need_u1 else 0), self.XOR(gA, gB ^ 1)
        raise RuntimeError("unreachable")

    def add3(self, A, B, C, cin=0):
        out = [0]*32
        u, U = (0, 0) if cin == 0 else ((0, 1) if cin == 1 else (1, 0))
        for i in range(32):
            if i < 31: out[i], u, U = self.pair_col(A[i], B[i], C[i], u, U, need_u1=(i < 30))
            else: out[i] = self.XOR(self.XOR(A[i], B[i]), self.XOR(C[i], U))
        return out

    def add2_hch(self, h, ch, cin=0):
        out = [0]*32
        out[0], c = self.ha_assoc(h[0], ch[0]) if cin == 0 else self.ha1_assoc(h[0], ch[0])
        for i in range(1, 32):
            if i < 31: out[i], c = self.fa(h[i], ch[i], c)
            else: out[i] = self.XOR(self.XOR(h[i], ch[i]), c)
        return out

    def add2_hch_fused_add3(self, h, ch, S1, Ww, cu=0, cu1=0, c3=0):
        if c3 == 0:
            s_hc0, c_hc1 = self.ha_assoc(h[0], ch[0]) if cu == 0 else self.ha1_assoc(h[0], ch[0])
            out0, c_a1 = self.fa(s_hc0, S1[0], Ww[0])
            u1, U1 = c_hc1, self.XOR(c_hc1, c_a1)
            hc = [0]*32; hc[0] = s_hc0
            hc[1], c = self.ha_assoc(h[1], ch[1]) if cu1 == 0 else self.ha1_assoc(h[1], ch[1])
            for i in range(2, 32):
                if i < 31: hc[i], c = self.fa(h[i], ch[i], c)
                else: hc[i] = self.XOR(self.XOR(h[i], ch[i]), c)
            out = [0]*32; out[0] = out0; u, U = u1, U1
            for i in range(1, 32):
                if i < 31: out[i], u, U = self.pair_col(hc[i], S1[i], Ww[i], u, U, need_u1=(i < 30))
                else: out[i] = self.XOR(self.XOR(hc[i], S1[i]), self.XOR(Ww[i], U))
            return out
        return self.add3(self.add2_hch(h, ch, cin=cu), S1, Ww, cin=c3)

    def add4_fused(self, A, B, C, D, cin3=0, cin2=0, cin2_b1=0):
        if cin3 == 0:
            s3_0, c_a1 = self.fa(A[0], B[0], C[0])
            out0, c_d1 = self.ha(s3_0, D[0]) if cin2 == 0 else self.ha1(s3_0, D[0])
            u, U = c_a1, self.XOR(c_a1, c_d1)
            s3 = [0]*32; s3[0] = s3_0
            for i in range(1, 32):
                if i < 31: s3[i], u, U = self.pair_col(A[i], B[i], C[i], u, U, need_u1=(i < 30))
                else: s3[i] = self.XOR(self.XOR(A[i], B[i]), self.XOR(C[i], U))
            out = [0]*32; out[0] = out0
            out[1], c = self.ha(s3[1], D[1]) if cin2_b1 == 0 else self.ha1(s3[1], D[1])
            for i in range(2, 32):
                if i < 31: out[i], c = self.fa(s3[i], D[i], c)
                else: out[i] = self.XOR(self.XOR(s3[i], D[i]), c)
            return out
        return self.add2(self.add3(A, B, C, cin=cin3), D, cin=cin2)

    def add5_fused(self, A, B, C, D, E, c1=0, c2=0, s1_mask=0):
        if c1 == 0 and c2 == 0:
            s1_0, c_a1 = self.fa(A[0], B[0], C[0])
            if s1_mask & 1: s1_0 = self.flip_pol(s1_0)
            out0, c_b1 = self.fa(s1_0, D[0], E[0])
            u, U = c_a1, self.XOR(c_a1, c_b1)
            s1 = [0]*32; s1[0] = s1_0
            for i in range(1, 32):
                if i < 31: s1[i], u, U = self.pair_col(A[i], B[i], C[i], u, U, need_u1=(i < 30))
                else: s1[i] = self.XOR(self.XOR(A[i], B[i]), self.XOR(C[i], U))
                if (s1_mask >> i) & 1: s1[i] = self.flip_pol(s1[i])
            out = [0]*32; out[0] = out0; u2, U2 = 0, 0
            for i in range(1, 32):
                if i < 31: out[i], u2, U2 = self.pair_col(s1[i], D[i], E[i], u2, U2, need_u1=(i < 30))
                else: out[i] = self.XOR(self.XOR(s1[i], D[i]), self.XOR(E[i], U2))
            return out
        s1 = self.add3(A, B, C, c1)
        if s1_mask: s1 = [self.flip_pol(s1[j]) if ((s1_mask >> j) & 1) else s1[j] for j in range(32)]
        return self.add3(s1, D, E, c2)

    def add6_fused(self, A, B, C, D, E, F):
        s1_0, c_a1 = self.fa(A[0], B[0], C[0])
        s2_0, c_b1 = self.fa(s1_0, D[0], E[0])
        out0, c_f1 = self.ha(s2_0, F[0])
        u, U = c_a1, self.XOR(c_a1, c_b1)
        s1 = [0]*32; s1[0] = s1_0
        for i in range(1, 32):
            if i < 31: s1[i], u, U = self.pair_col(A[i], B[i], C[i], u, U, need_u1=(i < 30))
            else: s1[i] = self.XOR(self.XOR(A[i], B[i]), self.XOR(C[i], U))
        u2, U2 = 0, c_f1
        s2 = [0]*32; s2[0] = s2_0
        for i in range(1, 32):
            if i < 31: s2[i], u2, U2 = self.pair_col(s1[i], D[i], E[i], u2, U2, need_u1=(i < 30))
            else: s2[i] = self.XOR(self.XOR(s1[i], D[i]), self.XOR(E[i], U2))
        out = [0]*32; out[0] = out0
        out[1], c = self.ha(s2[1], F[1])
        for i in range(2, 32):
            if i < 31: out[i], c = self.fa(s2[i], F[i], c)
            else: out[i] = self.XOR(self.XOR(s2[i], F[i]), c)
        return out

    def add_many(self, words, const_val=0):
        ws, cv = [], const_val & MASK
        for w in words:
            if all(b in (0, 1) for b in w):
                cv = (cv + sum((1 << i) for i in range(32) if w[i] == 1)) & MASK
            else: ws.append(w)
        if not ws: return self.const_word(cv)
        if len(ws) == 1: return self.add_const_word(ws[0], cv)
        if len(ws) == 2:
            if cv == 0: return self.add2(ws[0], ws[1], 0)
            b = min((0, 1), key=lambda x: self._acw_cost((cv - x) & MASK))
            return self.add_const_word(self.add2(ws[0], ws[1], b), (cv - b) & MASK)
        if len(ws) == 3:
            if cv == 0: return self.add3(ws[0], ws[1], ws[2], 0)
            b = min((0, 1, 2), key=lambda x: self._acw_cost((cv - x) & MASK))
            return self.add_const_word(self.add3(ws[0], ws[1], ws[2], b), (cv - b) & MASK)
        if len(ws) == 4:
            if cv == 0: return self.add4_fused(ws[0], ws[1], ws[2], ws[3], 0, 0, 0)
            cands = [(0, c2, b1, 429) for c2 in (0, 1) for b1 in (0, 1)] + [(c3, c2, 0, 430) for c3 in (1, 2) for c2 in (0, 1)]
            c3, c2, b1, _ = min(cands, key=lambda t: t[3] + self._acw_cost((cv - t[0] - t[1] - 2*t[2]) & MASK))
            return self.add_const_word(self.add4_fused(ws[0], ws[1], ws[2], ws[3], c3, c2, b1), (cv - c3 - c2 - 2*b1) & MASK)
        if len(ws) == 5:
            return self.add_many([self.add3(ws[0], ws[1], ws[2], 0), ws[3], ws[4]], cv)
        return self.add_many([self.add3(ws[0], ws[1], ws[2], 0)] + ws[3:], cv)

    def build(self):
        W = [None]*40
        W_split = {}
        for i in range(8): W[i] = self.const_word(PREFIX_W[i])
        Y = [[(1 + k*32 + b) << 1 for b in range(32)] for k in range(8)]
        W[8] = Y[0]; W[9] = Y[1]
        for k in range(2, 8):
            W_split[8 + k] = (Y[k], (-K[8 + k]) & MASK)

        def ensure_W(i):
            if W[i] is not None: return W[i]
            if 10 <= i <= 15:
                vw, c = W_split[i]; W[i] = self.add_const_word(vw, c); return W[i]
            w_m2 = ensure_W(i - 2); w_m15 = ensure_W(i - 15)
            t_m7 = None if (i <= 23 and (i - 7) in W_split) else ensure_W(i - 7)
            t_m16 = None if (i <= 23 and (i - 16) in W_split) else ensure_W(i - 16)
            raw_terms = [self.s1(w_m2), t_m7, self.s0(w_m15), t_m16]
            cv = 0; var_args = []
            for idx, term in enumerate(raw_terms):
                src_i = (i - 7) if idx == 1 else ((i - 16) if idx == 3 else None)
                if i <= 23 and src_i is not None and src_i in W_split:
                    vw, c = W_split[src_i]; var_args.append(vw); cv = (cv + c) & MASK
                elif all(b in (0, 1) for b in term):
                    cv = (cv + sum((1 << b) for b in range(32) if term[b] == 1)) & MASK
                else: var_args.append(term)
            if cv != 0 and len(var_args) >= 2:
                if len(var_args) == 2:
                    b = min((0, 1), key=lambda x: self._acw_cost((cv - x) & MASK))
                    vw = self.add2(var_args[0], var_args[1], b); rem = (cv - b) & MASK
                elif len(var_args) == 3:
                    b = min((0, 1, 2), key=lambda x: self._acw_cost((cv - x) & MASK))
                    vw = self.add3(var_args[0], var_args[1], var_args[2], b); rem = (cv - b) & MASK
                else:
                    cands = [(0, c2, b1, 429) for c2 in (0, 1) for b1 in (0, 1)] + [(c3, c2, 0, 430) for c3 in (1, 2) for c2 in (0, 1)]
                    c3, c2, b1, _ = min(cands, key=lambda t: t[3] + self._acw_cost((cv - t[0] - t[1] - 2*t[2]) & MASK))
                    vw = self.add4_fused(var_args[0], var_args[1], var_args[2], var_args[3], c3, c2, b1); rem = (cv - c3 - c2 - 2*b1) & MASK
                if rem != 0: W_split[i] = (vw, rem); W[i] = self.add_const_word(vw, rem)
                else: W[i] = vw
            else: W[i] = self.add_many(var_args, cv)
            return W[i]

        a, b, c, d, e, f, g, h = [self.const_word(x) for x in ST8]

        def apply_flip(word, r_idx, table=E_FLIP_MASKS):
            fm = table.get(r_idx, 0)
            return word if fm == 0 else [self.flip_pol(word[j]) if ((fm >> j) & 1) else word[j] for j in range(32)]

        for i in range(8, 34):
            ch_w = self.Ch(e, f, g); s1_e = self.S1(e)
            if i >= 16: ensure_W(i)
            wi_options = []
            if W[i] is not None: wi_options.append((W[i], K[i]))
            if i in W_split: wi_options.append((W_split[i][0], (K[i] + W_split[i][1]) & MASK))
            best_opt = None
            for wi_var, cv_base in wi_options:
                cv_t1 = cv_base; var_t1 = []
                for w in (h, ch_w, s1_e, wi_var):
                    if all(bit in (0, 1) for bit in w): cv_t1 = (cv_t1 + sum((1 << bit) for bit in range(32) if w[bit] == 1)) & MASK
                    else: var_t1.append(w)
                has_hch = (len(var_t1) == 4 and sum(1 for bit in range(32) if self.has_assoc_xor(var_t1[0][bit], var_t1[1][bit])) >= 8)
                can_delta = (not all(bit in (0, 1) for bit in d)) and (len(var_t1) >= 2)
                if has_hch:
                    deltas = (0, 1) if can_delta else (0,)
                    cands = []
                    for dl in deltas:
                        for cu in (0, 1):
                            c0 = self._ha_assoc_cost(var_t1[0][0], var_t1[1][0], cu)
                            for cu1 in (0, 1):
                                c1 = self._ha_assoc_cost(var_t1[0][1], var_t1[1][1], cu1)
                                cands.append((c0 + c1 - 2 + self._acw_cost((cv_t1 - cu - 2*cu1 - dl) & MASK), cu, cu1, 0, dl))
                            for c3 in (1, 2):
                                cands.append((c0 + 2 + self._acw_cost((cv_t1 - cu - c3 - dl) & MASK), cu, 0, c3, dl))
                    sc, cu, cu1, c3, best_delta = min(cands)
                    opt = (sc, True, var_t1, cv_t1, cu, cu1, c3, best_delta)
                else:
                    best_delta = 0
                    if can_delta and cv_t1 != 0:
                        mc = 2 if len(var_t1) >= 3 else 1
                        c0 = min(self._acw_cost((cv_t1 - ci) & MASK) for ci in range(mc + 1))
                        c1 = min(self._acw_cost((cv_t1 - 1 - ci) & MASK) for ci in range(mc + 1))
                        if c1 < c0: best_delta = 1
                        sc = min(c0, c1)
                    else:
                        mc = 2 if len(var_t1) >= 3 else (1 if len(var_t1) == 2 else 0)
                        sc = min(self._acw_cost((cv_t1 - ci) & MASK) for ci in range(mc + 1))
                    opt = (sc, False, var_t1, cv_t1, 0, 0, 0, best_delta)
                if best_opt is None or opt[0] < best_opt[0]: best_opt = opt
            _, has_hch, var_t1, cv_t1, cu, cu1, c3, best_delta = best_opt
            if has_hch:
                t1_raw = self.add2_hch_fused_add3(var_t1[0], var_t1[1], var_t1[2], var_t1[3], cu, cu1, c3)
                rem = (cv_t1 - cu - 2*cu1 - c3 - best_delta) & MASK
                t1 = self.add_const_word(t1_raw, rem) if rem != 0 else t1_raw
            else:
                t1 = self.add_many(var_t1, (cv_t1 - best_delta) & MASK)
            e_new = apply_flip(self.add_many([d, t1], best_delta), i + 1, E_FLIP_MASKS)
            a_new = apply_flip(self.add_many([t1, self.S0(a), self.Maj(a, b, c)], best_delta), i + 1, A_FLIP_MASKS)
            a, b, c, d, e, f, g, h = a_new, a, b, c, e_new, e, f, g

        a34, a33, a32, a31, e34, e33, e32, e31 = a, b, c, d, e, f, g, h

        def make_t1_tail(h_w, e_w, f_w, g_w, r_idx):
            ch_w = self.Ch(e_w, f_w, g_w); s1_e = self.S1(e_w); wi_var, cv = ensure_W(r_idx), K[r_idx]
            cands = []
            for cu in (0, 1):
                c0 = self._ha_assoc_cost(h_w[0], ch_w[0], cu)
                for cu1 in (0, 1):
                    c1 = self._ha_assoc_cost(h_w[1], ch_w[1], cu1)
                    cands.append((c0 + c1 - 2 + self._acw_cost((cv - cu - 2*cu1) & MASK), cu, cu1, 0))
                for c3 in (1, 2):
                    cands.append((c0 + 2 + self._acw_cost((cv - cu - c3) & MASK), cu, 0, c3))
            _, cu, cu1, c3 = min(cands)
            t1_raw = self.add2_hch_fused_add3(h_w, ch_w, s1_e, wi_var, cu, cu1, c3)
            rem = (cv - cu - 2*cu1 - c3) & MASK
            return self.add_const_word(t1_raw, rem) if rem != 0 else t1_raw

        def make_e_direct(d_w, h_w, e_w, f_w, g_w, r_idx):
            ch_w = self.Ch(e_w, f_w, g_w); s1_e = self.S1(e_w); wi_var, cv = ensure_W(r_idx), K[r_idx]
            c1, c2 = min(((a1, a2) for a1 in (0, 1, 2) for a2 in (0, 1, 2)),
                         key=lambda p: (0 if p == (0, 0) else 2) + self._acw_cost((cv - p[0] - p[1]) & MASK))
            s2 = self.add5_fused(d_w, s1_e, wi_var, h_w, ch_w, c1, c2, S1_FLIP_MASKS.get(r_idx, 0))
            rem = (cv - c1 - c2) & MASK
            return self.add_const_word(s2, rem) if rem != 0 else s2

        t1_34 = make_t1_tail(e31, e34, e33, e32, 34)
        e35 = apply_flip(self.add2(a31, t1_34), 35)
        QM = 0; mj34_part = [0]*32
        for j in range(32):
            dj = self.XOR(a34[j], a33[j])
            if (dj & 1) == (a32[j] & 1): mj34_part[j] = self.AND(dj, a32[j])
            else: QM |= (1 << j); mj34_part[j] = self.OR(dj ^ 1, a32[j])
        Q34 = self.add2(t1_34, mj34_part)

        t1_35 = make_t1_tail(e32, e35, e34, e33, 35)
        e36 = apply_flip(self.add2(a32, t1_35), 36)
        e37 = apply_flip(make_e_direct(a33, e33, e36, e35, e34, 36), 37, E_FLIP_MASKS)
        e38 = apply_flip(make_e_direct(a34, e34, e37, e36, e35, 37), 38, E_FLIP_MASKS)

        XM = 0; ne38_e36 = [0]*32
        for j in range(32):
            uj = e38[j] ^ 1
            if (uj & 1) == (e36[j] & 1): ne38_e36[j] = self.AND(uj, e36[j])
            else: XM |= (1 << j); ne38_e36[j] = self.OR(e38[j], e36[j])

        X38 = self.add6_fused(e35, ne38_e36, self.s1(W[36]), W[31], self.s0(W[23]), W[22])
        Y39 = self.add5_fused(e36, self.s1(W[37]), W[32], self.s0(W[24]), W[23], 0, 0)

        self.QM, self.XM, self.x_cv, self.y_cv = QM, XM, 0, 0
        return [e37, e38, a33, a34, Q34, t1_35, X38, Y39]


def compile_and_allocate(ckt, outs):
    used = set()
    stack = [r >> 1 for w in outs for r in w if r >= 2]
    while stack:
        wid = stack.pop()
        if wid >= 258 and wid not in used:
            used.add(wid)
            _, a, b = ckt.gates[wid - 258]
            stack.append(a); stack.append(b)
    live_sorted = sorted(used)
    remap = {i: i for i in range(1, 258)}
    raw_gates = []
    for idx, wid in enumerate(live_sorted):
        op, a, b = ckt.gates[wid - 258]
        remap[wid] = 258 + idx
        raw_gates.append((op, remap[a], remap[b]))
    out_wids = [remap[r >> 1] for w in outs for r in w]
    out_pols = [r & 1 for w in outs for r in w]
    n_gates = len(raw_gates)

    # Reverse-DAG (Dual) One-Shot Black Pebbling:
    # Schedule backward from outputs to inputs minimizing net cutwidth delta (-1, 0, +1),
    # breaking ties by -idx (latest-round completion first), then reverse to obtain a valid topological order.
    out_deg = [0] * n_gates
    preds_of_wire = defaultdict(list)
    for idx, (_, a, b) in enumerate(raw_gates):
        preds_of_wire[a].append(idx)
        if b != a: preds_of_wire[b].append(idx)
        if a >= 258: out_deg[a - 258] += 1
        if b >= 258 and b != a: out_deg[b - 258] += 1

    opened = [False] * (258 + n_gates)
    for ow in out_wids: opened[ow] = True
    opened[257] = True

    def prio(idx):
        _, a, b = raw_gates[idx]
        add = (0 if opened[a] else 1) + (0 if (b == a or opened[b]) else 1)
        return (add - 1, -idx)

    ready = []; in_ready = set()
    for idx in range(n_gates):
        if out_deg[idx] == 0:
            heapq.heappush(ready, (prio(idx), idx)); in_ready.add(idx)
    rev_order = []; sched = [False] * n_gates
    while ready:
        p, idx = heapq.heappop(ready)
        if sched[idx]: continue
        cp = prio(idx)
        if cp != p: heapq.heappush(ready, (cp, idx)); continue
        sched[idx] = True; rev_order.append(idx)
        _, a, b = raw_gates[idx]
        for x in ((a, b) if b != a else (a,)):
            if not opened[x]:
                opened[x] = True
                for g in preds_of_wire[x]:
                    if not sched[g] and g in in_ready:
                        heapq.heappush(ready, (prio(g), g))
            if x >= 258:
                out_deg[x - 258] -= 1
                if out_deg[x - 258] == 0:
                    in_ready.add(x - 258); heapq.heappush(ready, (prio(x - 258), x - 258))
    order = rev_order[::-1]

    sched_remap = {i: i for i in range(1, 258)}
    for new_i, old_i in enumerate(order): sched_remap[258 + old_i] = 258 + new_i
    gates = [(raw_gates[old_i][0], sched_remap[raw_gates[old_i][1]], sched_remap[raw_gates[old_i][2]]) for old_i in order]
    new_out_wids = [sched_remap[ow] for ow in out_wids]

    last_use = {}
    for idx, (_, a, b) in enumerate(gates): last_use[a] = idx; last_use[b] = idx
    last_use[257] = n_gates
    out_target_reg = {}
    for oi, ow in enumerate(new_out_wids): last_use[ow] = n_gates; out_target_reg[ow] = oi
    reg_of = {i: i - 1 for i in range(1, 257)}; reg_of[257] = 256
    in_use = set(range(257)); free_regs = []; free_home = set(); max_reg = 256
    home_birth = {oi: ow - 258 for oi, ow in enumerate(new_out_wids)}
    dies_at = [[] for _ in range(n_gates)]
    for w, lu in last_use.items():
        if lu < n_gates: dies_at[lu].append(w)

    stream = []; moves = 0
    for idx, (op, a, b) in enumerate(gates):
        wid = 258 + idx; ra, rb = reg_of[a], reg_of[b]
        for w in dies_at[idx]:
            r = reg_of[w]
            if r in in_use:
                in_use.remove(r)
                if r < 256: free_home.add(r)
                elif r > 256: free_regs.append(r)
        if wid in out_target_reg:
            tgt = out_target_reg[wid]
            if tgt not in in_use: dst = tgt; free_home.discard(tgt)
            else:
                moves += 1
                if free_regs: free_regs.sort(); dst = free_regs.pop(0)
                else: max_reg += 1; dst = max_reg
        else:
            w_die = last_use[wid]; borrowed = None
            for hr in sorted(free_home):
                if w_die <= home_birth[hr]: borrowed = hr; break
            if borrowed is not None: dst = borrowed; free_home.remove(borrowed)
            elif free_regs: free_regs.sort(); dst = free_regs.pop(0)
            else: max_reg += 1; dst = max_reg
        in_use.add(dst); reg_of[wid] = dst; stream.append((op, dst, ra, rb))
    return stream, max_reg + 1, moves, out_pols


def encode_body_4b(stream):
    op_code = {"XOR": 0, "AND": 1, "OR": 2}
    buf = bytearray(len(stream) * 4)
    for idx, (op, dst, ra, rb) in enumerate(stream):
        word = (op_code[op] << 30) | (dst << 20) | (ra << 10) | rb
        struct.pack_into("<I", buf, idx * 4, word)
    return bytes(buf)


def exec_body_4b(body_bytes, in_planes, n_data_regs):
    m = (1 << 256) - 1
    regs = [0] * n_data_regs
    for i in range(256): regs[i] = in_planes[i]
    regs[256] = m
    for (word,) in struct.iter_unpack("<I", body_bytes):
        oc = word >> 30
        dst = (word >> 20) & 0x3FF
        ra = (word >> 10) & 0x3FF
        rb = word & 0x3FF
        if oc == 0: regs[dst] = regs[ra] ^ regs[rb]
        elif oc == 1: regs[dst] = regs[ra] & regs[rb]
        else: regs[dst] = regs[ra] | regs[rb]
    return regs[:256]


def exp_upper(x):
    with localcontext() as ctx:
        ctx.prec = 80
        if x >= 0:
            ctx.rounding = ROUND_CEILING
            s = Decimal(1); term = Decimal(1)
            nt = max(90, int(x) * 4 + 60)
            for k in range(1, nt):
                term = (term * x) / Decimal(k); s += term
            ratio = x / Decimal(nt)
            return s + (term * ratio) / (Decimal(1) - ratio)
        # x < 0: 1 / exp_lower(-x)
        ctx.rounding = ROUND_FLOOR
        ax = -x; s = Decimal(1); term = Decimal(1)
        for k in range(1, 90):
            term = (term * ax) / Decimal(k); s += term
        ctx.rounding = ROUND_CEILING
        return Decimal(1) / s


def gamma_tail_upper(shape, x_dec):
    with localcontext() as ctx:
        ctx.prec = 80
        ctx.rounding = ROUND_CEILING
        s_val = Decimal(1); term = Decimal(1)
        for j in range(1, shape):
            term = (term * x_dec) / Decimal(j)
            s_val += term
        return exp_upper(-x_dec) * s_val


def compute_certified_ledger(klen=43548, n_data_regs=860):
    rec_records, rec_ops_step, ctrl_records = 480, 1249, 1350
    kbits, n_chk = 37, 191
    Tp, KAPPA, Ktot_num, Ktot_den = 2704, 40, 172, 10
    B_units = 1323675789799161
    body_bytes = klen * 4
    code_bytes = body_bytes + rec_records * 5 + ctrl_records * 5
    regfile_bytes = (n_data_regs + 3) * 32
    work_bytes = 16384 + n_chk * 64
    group_bytes = kbits * 32
    groups = (1048576 - (code_bytes + regfile_bytes + work_bytes)) // group_bytes
    table_bytes = groups * group_bytes
    slots = groups * 256
    tmax = slots - 256
    search_mem = code_bytes + regfile_bytes + work_bytes + table_bytes

    B = B_units * (10**21)
    m = 256
    S = Decimal(1 << 256)
    D_pow = Decimal(1 << 122)
    L = D_pow / Decimal(Tp)
    K_tot = Decimal(Ktot_num) / Decimal(Ktot_den)

    with localcontext() as ctx:
        ctx.prec = 80
        ctx.rounding = ROUND_FLOOR
        mB = Decimal(m * B)
        term1 = (mB * mB) / (Decimal(2) * S)
        ctx.rounding = ROUND_CEILING
        term2 = (Decimal(m * m * B) * L) / S
        ctx.rounding = ROUND_FLOOR
        I_lo = term1 - term2
        p_base_lo = Decimal(1) - exp_upper(-I_lo)

        ctx.rounding = ROUND_CEILING
        mu_hi = (mB * Decimal(Tp)) / D_pow
        diff_t = Decimal(tmax) - mu_hi
        ctx.rounding = ROUND_FLOOR
        ce_lo = (diff_t * diff_t) / (Decimal(2) * (mu_hi + diff_t / Decimal(3)))
        p_ovf_hi = exp_upper(-ce_lo)

        ctx.rounding = ROUND_CEILING
        p_age_hi = Decimal(2) * (Decimal(1) + Decimal(KAPPA)) * exp_upper(-Decimal(KAPPA))
        # Exclude 3-way 37-bit key collisions (p_triple_hi) and any false 37-bit key match on the
        # true colliding pair (p_coll_key_hi); on their complement, all f false-matching pairs and
        # the true colliding pair are pairwise vertex-disjoint with mutually independent trail lengths.
        p_triple_hi = Decimal(tmax * (tmax - 1) * (tmax - 2)) / Decimal(6 * (1 << (2 * kbits)))
        p_coll_key_hi = Decimal(2 * tmax) / Decimal(1 << kbits)
        lam_hi = Decimal(tmax * (tmax - 1)) / Decimal(2 * (1 << kbits))
        g_prev = gamma_tail_upper(3, K_tot)
        p_rec_hi = g_prev
        lam_pow = Decimal(1); fact = Decimal(1)
        for f in range(1, 35):
            lam_pow *= lam_hi; fact *= Decimal(f)
            g_cur = gamma_tail_upper(2 * f + 3, K_tot)
            diff_g = g_cur - g_prev
            if diff_g > 0:
                p_rec_hi += diff_g * (lam_pow / fact)
            g_prev = g_cur
        p_rec_hi += (lam_pow * lam_hi) / (fact * Decimal(35))

        levels = [(10, 7), (12, 5), (14, 5), (16, 5), (18, 6)]
        U_cap = 0
        for j, deb in levels:
            q_pow = (Decimal(1) - Decimal(1) / Decimal(1 << j)) ** 256
            P_j_hi = Decimal(1) - q_pow + Decimal("1e-12")
            U_cap += deb * int((Decimal(B) * P_j_hi).to_integral_value(rounding=ROUND_CEILING))
        P_20_hi = Decimal(1) - (Decimal(1) - Decimal(1) / Decimal(1 << 20)) ** 256 + Decimal("1e-12")
        s2_cap = int((Decimal(B) * P_20_hi).to_integral_value(rounding=ROUND_CEILING))
        # 683 bit-sliced groups x 37 bit planes (~120 ops/group = 81,960 <= 100,000 ops/DP)
        s2_ops = s2_cap * 25 + tmax * 100000

        p_fail_hi = p_ovf_hi + p_age_hi + p_rec_hi + p_triple_hi + p_coll_key_hi + Decimal("1e-12")
        ctx.rounding = ROUND_FLOOR
        P_F_lo = p_base_lo - p_fail_hi

        cr = int((K_tot * L).to_integral_value(rounding=ROUND_CEILING)) + 100
        D_stride = (cr + n_chk - 1) // n_chk
        probes = math.ceil(math.log2(n_chk + 1)) + 2
        rec_ops = (cr + probes * D_stride) * (rec_ops_step + 25) + n_chk * 8 + 10000
        setup_ops = 600_000_000
        N = B * (klen + 14) + (U_cap + 30) + (s2_ops + tmax * 40) + rec_ops + setup_ops

        ctx.prec = 100
        log2_dec = (Decimal(N) / Decimal(C_REF)).ln() / Decimal(2).ln()
        k_claim = int((log2_dec * Decimal(100000)).to_integral_value(rounding=ROUND_CEILING))

    return {
        "klen": klen, "n_data_regs": n_data_regs, "search_mem": search_mem,
        "code_bytes": code_bytes, "regfile_bytes": regfile_bytes, "table_bytes": table_bytes,
        "kbits": kbits, "n_chk": n_chk, "groups": groups, "slots": slots, "tmax": tmax,
        "Tp": Tp, "KAPPA": KAPPA, "K_tot": str(K_tot), "B": B, "N": N,
        "P_F_lo": str(P_F_lo)[:18], "log2_exact": f"{log2_dec:.12f}", "time_log2": k_claim / 100000.0,
    }


M32_2L = 0x00000000FFFFFFFF | (0x00000000FFFFFFFF << 128)


def _pack2(a, b):
    return (a & MASK) | ((b & MASK) << 128)


def _unpack2(x):
    return x & MASK, (x >> 128) & MASK


def walk_b_2lane_simd(y_pair, qm, xm, pd_words):
    # Exact 2-lane SIMD 256-bit word-RAM Walk-B recovery evaluator (lane 0 in bits 0..31,
    # lane 1 in bits 128..159), counting every arithmetic word-RAM op (exact = 1,249 ops/step).
    ops = 0
    m256 = (1 << 256) - 1
    def ADD(u, v): nonlocal ops; ops += 1; return (u + v) & m256
    def XOR(u, v): nonlocal ops; ops += 1; return u ^ v
    def AND(u, v): nonlocal ops; ops += 1; return u & v
    def OR(u, v): nonlocal ops; ops += 1; return u | v
    def SHL(u, k): nonlocal ops; ops += 1; return (u << k) & m256
    def SHR(u, k): nonlocal ops; ops += 1; return u >> k
    def dup64(x): return OR(x, SHL(x, 32))
    def S0_f(x64): return AND(XOR(XOR(SHR(x64, 2), SHR(x64, 13)), SHR(x64, 22)), M32_2L)
    def S1_f(x64): return AND(XOR(XOR(SHR(x64, 6), SHR(x64, 11)), SHR(x64, 25)), M32_2L)
    def s0_f(x, x64): return AND(XOR(XOR(SHR(x64, 7), SHR(x64, 18)), SHR(x, 3)), M32_2L)
    def s1_f(x, x64): return AND(XOR(XOR(SHR(x64, 17), SHR(x64, 19)), SHR(x, 10)), M32_2L)
    def S0_2(x): return S0_f(dup64(x))
    def S1_2(x): return S1_f(dup64(x))

    kp = [_pack2(K[i], K[i]) for i in range(40)]
    pref = [_pack2(PREFIX_W[i], PREFIX_W[i]) for i in range(8)]
    off_neg = [0, 0] + [_pack2((-K[i]) & MASK, (-K[i]) & MASK) for i in range(10, 16)]
    w = [0] * 38; w64 = [None] * 38
    for i in range(8): w[i] = pref[i]
    w[8] = y_pair[0]; w[9] = y_pair[1]
    for i in range(10, 16): w[i] = AND(ADD(y_pair[i - 8], off_neg[i - 8]), M32_2L)
    def get_w64(idx):
        if w64[idx] is None: w64[idx] = dup64(w[idx])
        return w64[idx]
    c_sched = {i: _pack2((PREFIX_W[i - 16] + s0_32(PREFIX_W[i - 15])) & MASK,
                         (PREFIX_W[i - 16] + s0_32(PREFIX_W[i - 15])) & MASK) for i in range(16, 23)}
    for i in range(16, 23):
        w[i] = AND(ADD(ADD(s1_f(w[i - 2], get_w64(i - 2)), w[i - 7]), c_sched[i]), M32_2L)
    w[23] = AND(ADD(ADD(ADD(s1_f(w[21], get_w64(21)), w[16]), s0_f(w[8], get_w64(8))), pref[7]), M32_2L)
    for i in range(24, 38):
        w[i] = AND(ADD(ADD(ADD(s1_f(w[i - 2], get_w64(i - 2)), w[i - 7]), s0_f(w[i - 15], get_w64(i - 15))), w[i - 16]), M32_2L)

    a9 = w[8]; e9 = w[8]; w8_64 = get_w64(8)
    t1_9 = AND(ADD(S1_f(w8_64), w[9]), M32_2L); e10 = t1_9
    a10 = AND(ADD(t1_9, S0_f(w8_64)), M32_2L)
    t1_10 = AND(ADD(ADD(AND(e10, e9), S1_2(e10)), y_pair[2]), M32_2L); e11 = t1_10
    a11 = AND(ADD(ADD(t1_10, S0_2(a10)), AND(a10, a9)), M32_2L)
    fg = XOR(e10, e9); ch11 = XOR(e9, AND(e11, fg))
    t1_11 = AND(ADD(ADD(ch11, S1_2(e11)), y_pair[3]), M32_2L); e12 = t1_11
    bc = XOR(a10, a9); ab = XOR(a11, a10); maj11 = XOR(a10, AND(bc, ab))
    a12 = AND(ADD(ADD(t1_11, S0_2(a11)), maj11), M32_2L)
    a, b, c, d, e, f, g, h = a12, a11, a10, a9, e12, e11, e10, e9; prev_ab = ab
    for i in range(12, 34):
        fg = XOR(f, g); ch = XOR(g, AND(e, fg))
        t1 = ADD(ADD(ADD(h, ch), S1_2(e)), y_pair[i - 8]) if i <= 15 else ADD(ADD(ADD(ADD(h, ch), S1_2(e)), w[i]), kp[i])
        e_new = AND(ADD(d, t1), M32_2L)
        ab = XOR(a, b); maj = XOR(b, AND(prev_ab, ab))
        a_new = AND(ADD(ADD(t1, S0_2(a)), maj), M32_2L)
        prev_ab = ab; a, b, c, d, e, f, g, h = a_new, a, b, c, e_new, e, f, g
    a34, a33, a32, a31, e34, e33, e32, e31 = a, b, c, d, e, f, g, h
    ch34 = XOR(e32, AND(e34, XOR(e33, e32)))
    t1_34 = ADD(ADD(ADD(ADD(e31, ch34), S1_2(e34)), w[34]), kp[34])
    e35 = AND(ADD(a31, t1_34), M32_2L)
    qm_p = _pack2(qm, qm); d34 = XOR(a34, a33); mj34_a = AND(d34, a32); mj34_o = OR(XOR(d34, M32_2L), a32)
    mj34 = XOR(mj34_a, AND(XOR(mj34_a, mj34_o), qm_p))
    Q34 = AND(ADD(t1_34, mj34), M32_2L)
    ch35 = XOR(e33, AND(e35, XOR(e34, e33)))
    t1_35 = AND(ADD(ADD(ADD(ADD(e32, ch35), S1_2(e35)), w[35]), kp[35]), M32_2L)
    e36 = AND(ADD(a32, t1_35), M32_2L)
    ch36 = XOR(e34, AND(e36, XOR(e35, e34)))
    e37 = AND(ADD(ADD(ADD(ADD(ADD(a33, e33), ch36), S1_2(e36)), w[36]), kp[36]), M32_2L)
    ch37 = XOR(e35, AND(e37, XOR(e36, e35)))
    e38 = AND(ADD(ADD(ADD(ADD(ADD(a34, e34), ch37), S1_2(e37)), w[37]), kp[37]), M32_2L)
    xm_p = _pack2(xm, xm); xa = AND(XOR(e38, M32_2L), e36); xo = OR(e38, e36)
    ne38_e36 = XOR(xa, AND(XOR(xa, xo), xm_p))
    X38 = AND(ADD(ADD(ADD(ADD(ADD(e35, ne38_e36), s1_f(w[36], get_w64(36))), w[31]), s0_f(w[23], get_w64(23))), w[22]), M32_2L)
    Y39 = AND(ADD(ADD(ADD(ADD(e36, s1_f(w[37], get_w64(37))), w[32]), s0_f(w[24], get_w64(24))), w[23]), M32_2L)
    raw = [e37, e38, a33, a34, Q34, t1_35, X38, Y39]
    return [XOR(raw[k], _pack2(pd_words[k], pd_words[k])) for k in range(8)], ops


def selftest():
    ckt = WalkBCircuit()
    outs = ckt.build()
    stream, n_regs, moves, out_pols = compile_and_allocate(ckt, outs)
    assert len(stream) == 43548, len(stream)
    assert ckt.mixed_and == 0 and ckt.mixed_or == 0
    assert n_regs == 860 and n_regs + 3 <= 1024
    assert moves == 0
    body = encode_body_4b(stream)
    body_sha = hashlib.sha256(body).hexdigest()
    pd_words = [sum((out_pols[wi * 32 + b] << b) for b in range(32)) for wi in range(8)]

    # Deterministic 256-lane verification against complete 64-byte 2-block 40-round SHA-256
    # AND exact 256/256 bit-for-bit verification of 1,249-op 2-lane SIMD Walk-B RecProg.
    in_planes = [0] * 256
    y_all = []
    st = 0x123456789ABCDEF0
    for lane in range(256):
        yw = []
        for _ in range(8):
            st = (st * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
            yw.append((st >> 32) & MASK)
        y_all.append(yw)
        for wi in range(8):
            v = yw[wi]
            for b in range(32):
                if (v >> b) & 1:
                    in_planes[wi * 32 + b] |= (1 << lane)
    out_planes = exec_body_4b(body, in_planes, n_regs)
    rec_ops = 0
    for p in range(128):
        l0, l1 = 2 * p, 2 * p + 1
        y_pair = [_pack2(y_all[l0][wi], y_all[l1][wi]) for wi in range(8)]
        simd_out, rec_ops = walk_b_2lane_simd(y_pair, ckt.QM, ckt.XM, pd_words)
        assert rec_ops == 1249, rec_ops
        for lane, slot in ((l0, 0), (l1, 1)):
            co_raw = [sum((((out_planes[wi * 32 + b] >> lane) & 1) << b) for b in range(32)) for wi in range(8)]
            co_simd = [_unpack2(simd_out[wi])[slot] for wi in range(8)]
            assert co_raw == co_simd, f"RecProg mismatch at lane {lane}"
            co = [co_raw[wi] ^ pd_words[wi] for wi in range(8)]
            dig_ckt = walk_b_inverse_to_digest(co, ckt.QM, ckt.XM, ckt.x_cv, ckt.y_cv)
            dig_ref = sha256_r40(y_to_msg64(y_all[lane]))
            assert dig_ckt == dig_ref, f"lane {lane} mismatch"
    led = compute_certified_ledger(len(stream), n_regs)
    assert Decimal(led["P_F_lo"]) >= Decimal("0.390000001")
    assert led["search_mem"] <= 1048576
    return {"ok": True, "body_sha256": body_sha, "rec_ops": rec_ops, "ledger": led}


def sha256_r40_y_fast(y_words):
    # Exact 2-block 40-round SHA-256 on y_to_msg64(y_words), skipping constant rounds 0..7 via ST8!
    k_loc = K
    w = [
        PREFIX_W[0], PREFIX_W[1], PREFIX_W[2], PREFIX_W[3],
        PREFIX_W[4], PREFIX_W[5], PREFIX_W[6], PREFIX_W[7],
        y_words[0] & MASK, y_words[1] & MASK,
        (y_words[2] - k_loc[10]) & MASK, (y_words[3] - k_loc[11]) & MASK,
        (y_words[4] - k_loc[12]) & MASK, (y_words[5] - k_loc[13]) & MASK,
        (y_words[6] - k_loc[14]) & MASK, (y_words[7] - k_loc[15]) & MASK,
    ]
    w_append = w.append
    for i in range(16, 40):
        x = w[i - 15]; y = w[i - 2]
        s0 = ((x >> 7 | x << 25) ^ (x >> 18 | x << 14) ^ (x >> 3)) & MASK
        s1 = ((y >> 17 | y << 15) ^ (y >> 19 | y << 13) ^ (y >> 10)) & MASK
        w_append((s1 + w[i - 7] + s0 + w[i - 16]) & MASK)
    a, b, c, d, e, f, g, h = ST8
    for i in range(8, 40):
        s1 = ((e >> 6 | e << 26) ^ (e >> 11 | e << 21) ^ (e >> 25 | e << 7)) & MASK
        t1 = (h + s1 + ((e & f) ^ (~e & g)) + k_loc[i] + w[i]) & MASK
        s0 = ((a >> 2 | a << 30) ^ (a >> 13 | a << 19) ^ (a >> 22 | a << 10)) & MASK
        t2 = (s0 + ((a & b) ^ (a & c) ^ (b & c))) & MASK
        h = g; g = f; f = e; e = (d + t1) & MASK
        d = c; c = b; b = a; a = (t1 + t2) & MASK
    h0 = (IV[0] + a) & MASK; h1 = (IV[1] + b) & MASK; h2 = (IV[2] + c) & MASK; h3 = (IV[3] + d) & MASK
    h4 = (IV[4] + e) & MASK; h5 = (IV[5] + f) & MASK; h6 = (IV[6] + g) & MASK; h7 = (IV[7] + h) & MASK
    # Block 2: fixed PAD_BLOCK_64
    a, b, c, d, e, f, g, h = h0, h1, h2, h3, h4, h5, h6, h7
    for i in range(40):
        s1 = ((e >> 6 | e << 26) ^ (e >> 11 | e << 21) ^ (e >> 25 | e << 7)) & MASK
        t1 = (h + s1 + ((e & f) ^ (~e & g)) + k_loc[i] + PAD_W[i]) & MASK
        s0 = ((a >> 2 | a << 30) ^ (a >> 13 | a << 19) ^ (a >> 22 | a << 10)) & MASK
        t2 = (s0 + ((a & b) ^ (a & c) ^ (b & c))) & MASK
        h = g; g = f; f = e; e = (d + t1) & MASK
        d = c; c = b; b = a; a = (t1 + t2) & MASK
    return (
        (h0 + a) & MASK, (h1 + b) & MASK, (h2 + c) & MASK, (h3 + d) & MASK,
        (h4 + e) & MASK, (h5 + f) & MASK, (h6 + g) & MASK, (h7 + h) & MASK,
    )


PAD_W = list(struct.unpack(">16I", PAD_BLOCK_64))
for _i in range(16, 40):
    PAD_W.append((s1_32(PAD_W[_i - 2]) + PAD_W[_i - 7] + s0_32(PAD_W[_i - 15]) + PAD_W[_i - 16]) & MASK)
PAD_W = tuple(PAD_W)


def run_reduced_dp_trial(seed_bytes, width_bits, max_evals, dp_bits):
    # Deterministic birthday walk on the exact 64-byte W[0..7]-prefix message family,
    # targeting collisions on the low width_bits of complete 2-block 40-round SHA-256.
    mask_w = (1 << width_bits) - 1
    dp_mask = (1 << dp_bits) - 1
    y0 = list(struct.unpack(">8I", seed_bytes[:32]))
    table = {}
    start = list(y0)
    cur = list(y0)
    steps = 0
    restarts = 0
    for ev in range(max_evals):
        nxt = sha256_r40_y_fast(cur)
        key = nxt[7] & mask_w
        steps += 1
        if (key & dp_mask) == 0:
            if key in table:
                s_old, len_old = table[key]
                a_st, a_len = list(s_old), len_old
                b_st, b_len = list(start), steps
                while a_len > b_len:
                    a_st = sha256_r40_y_fast(a_st); a_len -= 1
                while b_len > a_len:
                    b_st = sha256_r40_y_fast(b_st); b_len -= 1
                while a_len > 0:
                    na = sha256_r40_y_fast(a_st); nb = sha256_r40_y_fast(b_st)
                    if (na[7] & mask_w) == (nb[7] & mask_w):
                        ma, mb = y_to_msg64(a_st), y_to_msg64(b_st)
                        if ma != mb:
                            return ma, mb, ev + 1
                        break
                    a_st, b_st = na, nb
                    a_len -= 1
            else:
                table[key] = (list(start), steps)
            restarts += 1
            start = [(y0[j] ^ ((restarts * 0x9E3779B9 + j * 0x85EBCA6B) & MASK)) for j in range(8)]
            cur = list(start)
            steps = 0
        else:
            cur = nxt
    return None, None, max_evals


def run_projection_trial(seed_bytes, width_bits, budget):
    mask_w = (1 << width_bits) - 1
    y0 = list(struct.unpack(">8I", seed_bytes[:32]))
    seen = {}
    cur = list(y0)
    for ev in range(budget):
        nxt = sha256_r40_y_fast(cur)
        key = nxt[7] & mask_w
        if key in seen:
            ma, mb = y_to_msg64(seen[key]), y_to_msg64(cur)
            if ma != mb:
                return ma, mb, ev + 1
        else:
            seen[key] = list(cur)
        cur = nxt
    return None, None, budget


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--selftest":
            print(json.dumps(selftest(), sort_keys=True))
            return
        if sys.argv[1] == "--ledger":
            print(json.dumps(compute_certified_ledger(), indent=2, sort_keys=True))
            return

    req = json.loads(sys.stdin.read())
    exp_id = req.get("experiment_id", "")
    trials_out = []
    if exp_id == "sha256-r40-walkb-bounded-w16-v1":
        st = selftest()
        assert st["ok"] is True
        for t in req["trials"]:
            seed = bytes.fromhex(t["seed"])
            ma, mb, evs = run_reduced_dp_trial(seed, width_bits=16, max_evals=160, dp_bits=1)
            trials_out.append({
                "trial": t["trial"],
                "message_a_hex": ma.hex() if ma is not None else None,
                "message_b_hex": mb.hex() if mb is not None else None,
                "observations": {"evals": evs},
            })
    else:
        # sha256-r40-walkb-projection-w14-v1: budget = 127 gives P_model = 1 - exp(-127^2 / (2*2^14)) = 0.3887
        for t in req["trials"]:
            seed = bytes.fromhex(t["seed"])
            ma, mb, evs = run_projection_trial(seed, width_bits=14, budget=127)
            trials_out.append({
                "trial": t["trial"],
                "message_a_hex": ma.hex() if ma is not None else None,
                "message_b_hex": mb.hex() if mb is not None else None,
                "observations": {"evals": evs},
            })
    json.dump({"schema_version": 1, "trials": trials_out}, sys.stdout, sort_keys=True)


if __name__ == "__main__":
    main()
