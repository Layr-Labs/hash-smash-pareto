#!/usr/bin/env python3
"""Round-39 SHA-256 prefix collision experiment (r39-claw-vow, r39-tail-sfs) & traced cost ledger."""
import hashlib
import json
import math
import struct
import sys

MASK32 = 0xFFFFFFFF

K39 = (
 0x428A2F98,0x71374491,0xB5C0FBCF,0xE9B5DBA5,0x3956C25B,0x59F111F1,0x923F82A4,0xAB1C5ED5,
 0xD807AA98,0x12835B01,0x243185BE,0x550C7DC3,0x72BE5D74,0x80DEB1FE,0x9BDC06A7,0xC19BF174,
 0xE49B69C1,0xEFBE4786,0x0FC19DC6,0x240CA1CC,0x2DE92C6F,0x4A7484AA,0x5CB0A9DC,0x76F988DA,
 0x983E5152,0xA831C66D,0xB00327C8,0xBF597FC7,0xC6E00BF3,0xD5A79147,0x06CA6351,0x14292967,
 0x27B70A85,0x2E1B2138,0x4D2C6DFC,0x53380D13,0x650A7354,0x766A0ABB,0x81C2C92E,
)

D8 = 0x40000000
T8 = 0x087FF000
TARGET_W16 = 0xBCA1C321
TARGET_W17 = 0x71E9BA98

ACTIVE_MASK_F8 = 0xCC19E60C
INACTIVE_MASK_F8 = (~ACTIVE_MASK_F8) & MASK32
ACTIVE_BITS_F8 = tuple(b for b in range(32) if (ACTIVE_MASK_F8 >> b) & 1)

ACTIVE_MASK_F9 = 0xF9983C0F
INACTIVE_MASK_F9 = (~ACTIVE_MASK_F9) & MASK32
ACTIVE_BITS_F9 = tuple(b for b in range(32) if (ACTIVE_MASK_F9 >> b) & 1)

BASE_A0 = (
 0x1C40A0D4,0x71A28861,0xD12DEEF2,0xB21E3E63,0xEA3FF0B4,0x48C79FA7,0x7E0F7259,0xB9BE31D6,
 0x9F0216F0,0x583F3EC8,0x73A03068,0xCAEEFA06,0x29F1C95E,0xC76D0D7B,0x24B9A00A,0xCA0AECD2,
 0x5829BCDB,0xBF5E1F93,0xBD4F5653,0x269F8F4F,
)
BASE_E0 = (
 0x0E6446C1,0x020B80DD,0xB326F54C,0x15BB07FB,0xADEE5184,0x873FAA9C,0x33A865AE,0x114B346F,
 0x3895B86B,0x49D8EBCF,0x3BBB3CC6,0x0A20C41F,0x94DFB329,0xAC230E77,0x9E3B6FE9,0xFF00F821,
 0xBC4A3994,0xA87DBD19,0x9CCA05A1,0xD2C3EC33,
)
BASE_A1 = BASE_A0[:12] + (
 0x69F1C95E,0xCFE71C5B,0x24B9A00A,0xCA0AECD2,0x5CE9BCDB,0x96179B98,0xFD4B5673,0x36998E6F,
)
BASE_E1 = BASE_E0[:12] + (
 0xD4DFB329,0xA49B1E57,0x3F1B2103,0xB708F921,0xF8883994,0x82412611,0x9CCA05A1,0xC2C3EC33,
)
BASE_W0 = (
 0x5EE50E16,0xB5A4F02B,0xA58B289E,0xF713DE5D,0x3B96D2DB,0x215DA7E2,0x3674669A,0x2CA65D8D,
 0xA99C40E3,0x1FAE8A20,0x42E88746,0x01003FBB,0xE8D6FE22,0xB06304C1,0x43660040,0x4891771F,
)
BASE_W1 = BASE_W0[:8] + (
 0xE99C40E3,0x172E9A20,0x02E88746,0x07021C8F,0xE8C6E622,0xB06304C1,0x43660040,0x4891771F,
)

ROW_MASKS = {
 16: (0x05010000,0x04010000,0x00000100,0,0x08801000,0x08800000),
 17: (0,0,0x80829C01,0x00029C00,0x40000000,0x40000000),
 18: (0x40000000,0x40000000,0,0,0,0),
 19: (0,0,0x00080020,0x00080000,0,0),
 20: (0,0,0x03010000,0x03010000,0,0),
 21: (0,0,0,0,0,0),
 22: (0,0,0x40000000,0x40000000,0,0),
 23: (0,0,0,0,0,0),
 24: (0,0,0,0,0x03010000,0),
 25: (0,0,0,0,0,0),
 26: (0,0,0,0,0x40000000,0),
}

CONDS_16_18_23 = (
 (16,((1,16,13),(1,16,27)),9),(16,((0,16,4),(0,16,15)),6),(16,((0,16,5),(0,16,25)),9),
 (16,((0,16,6),(0,16,17)),9),(16,((0,16,8),(0,14,8)),9),(16,((0,16,13),(0,16,1)),6),
 (16,((0,16,15),(0,16,3)),9),(16,((0,16,27),(0,16,4)),6),(16,((1,16,21),(1,16,26)),9),
 (16,((0,16,17),(0,14,17)),9),(16,((0,16,3),(0,16,12)),9),(16,((0,16,5),(0,16,14)),6),
 (16,((0,16,28),(0,16,7)),6),(16,((1,16,28),(1,14,28)),10),(16,((0,16,28),(0,14,28)),6),
 (16,((1,16,3),(1,16,22)),9),(16,((0,16,30),(0,15,30)),6),(16,((1,16,0),(1,15,0)),4),
 (16,((2,16,19),(2,16,21)),6),(16,((2,16,21),(2,16,14)),9),(16,((2,16,25),(2,16,16)),6),
 (16,((2,16,25),(2,16,18)),9),(16,((1,16,10),(1,15,10)),9),(16,((2,16,29),(2,16,20)),6),
 (16,((1,16,11),(1,15,11)),4),(16,((1,16,12),(1,15,12)),9),(16,((2,16,30),(2,16,0)),6),
 (16,((1,16,15),(1,15,15)),9),(16,((1,16,17),(1,15,17)),9),(16,((2,16,2),(2,16,4)),9),
 (16,((1,16,23),(1,15,23)),4),(16,((2,16,10),),1),(16,((2,16,14),),2),
 (16,((1,16,31),(1,15,31)),9),(16,((2,16,2),(2,16,19)),9),(16,((2,16,31),(2,16,10)),6),
 (16,((2,16,1),(2,16,29)),6),
 (17,((1,17,6),(1,17,25)),9),(17,((1,17,7),(1,17,26)),6),(17,((1,17,16),(1,17,30)),6),
 (17,((0,17,5),(0,16,5)),6),(17,((1,17,13),(1,17,18)),9),(17,((1,17,8),(1,15,8)),10),
 (17,((0,17,8),(0,16,8)),9),(17,((1,17,20),(1,17,2)),9),(17,((1,17,22),(1,17,4)),6),
 (17,((1,17,18),(1,17,5)),6),(17,((0,17,16),(0,15,16)),9),(17,((0,17,17),(0,16,17)),9),
 (17,((1,17,24),(1,17,29)),9),(17,((0,17,18),(0,16,18)),6),(17,((1,17,25),(1,17,30)),9),
 (17,((1,17,26),(1,17,13)),6),(17,((1,17,27),(1,17,14)),6),(17,((1,17,28),(1,17,1)),9),
 (17,((1,17,30),(1,17,3)),9),(17,((0,17,24),(0,15,24)),9),(17,((1,17,4),(1,17,18)),6),
 (17,((1,17,5),(1,17,19)),9),(17,((0,17,26),(0,15,26)),9),(17,((1,17,28),(1,16,28)),10),
 (17,((0,17,28),(0,16,28)),9),(17,((1,17,4),(1,17,9)),9),(17,((1,17,5),(1,17,24)),9),
 (17,((2,17,28),(2,17,21)),9),(17,((2,17,0),(2,17,23)),6),(17,((2,17,5),(2,17,7)),6),
 (17,((0,17,30),(0,16,30)),9),(17,((2,17,19),(2,17,15)),9),(17,((2,17,9),(2,17,26)),6),
 (17,((2,17,2),(2,17,13)),6),
 (18,((1,18,0),(1,16,0)),5),(18,((1,18,8),(1,17,8)),5),(18,((0,18,10),(0,18,21)),9),
 (18,((1,18,10),(1,16,10)),5),(18,((1,18,11),(1,16,11)),5),(18,((1,18,12),(1,16,12)),5),
 (18,((1,18,15),(1,16,15)),5),(18,((0,18,16),(0,17,16)),9),(18,((1,18,17),(1,16,17)),10),
 (18,((0,18,19),(0,18,7)),6),(18,((1,18,23),(1,16,23)),5),(18,((0,18,24),(0,17,24)),9),
 (18,((0,18,26),(0,17,26)),9),(18,((0,18,9),(0,18,18)),6),(18,((1,18,31),(1,16,31)),5),
 (18,((1,18,5),(1,17,5)),9),(18,((1,18,19),(1,17,19)),9),
 (23,((1,23,30),(1,21,30)),5),
)

VOW_F89_TRAILS = (
 (1,0x78A6A594,  4,0x2205F491,  6,0x1FBDFE80,0xBB8EF11C,0xCF777515),
 (2,0xBA57BE4A, 41,0xAB3AA220, 48,0xCE856980,0xF1690B2E,0xCE390A4D),
 (3,0xA7DAD2A7, 15,0x6CDAA51B, 48,0x6CF48D80,0xF6C822E4,0xA7DAD2A7),
 (1,0x24C71722, 52,0x18B24B66, 34,0x81CBFC00,0x3BBC547C,0xBF7355B5),
 (2,0x43D67626, 44,0xD8231DCF, 63,0x1B814B00,0x9EED826A,0x54D5C427),
 (0,0x14A1D393, 64,0xD1925349, 56,0xE9740E00,0xEB9FBF5C,0x647329EF),
 (2,0x8718774B, 71,0x0FF99F6B, 47,0xBACAC300,0x54DDDA08,0x8F6AC667),
 (0,0x03EBEA56, 63,0xE1392C08, 83,0xF2F5FB00,0xF5EC92A6,0xEBA190D3),
 (2,0xCF11A335, 68,0x2922CEA5, 83,0xB2DDFF80,0xB5087F2A,0x3F847AA9),
 (2,0x2E193E3E, 84,0xAB132FC6, 69,0x47BCB100,0x523AC884,0x394AF1BD),
 (3,0x292D71ED, 71,0x39CCE80C, 89,0x206E2000,0xDA1D15CC,0x39044B47),
 (1,0xD79EF3D9,  8,0xC8232F2A, 90,0x1A5FAA00,0xD374B048,0x80D8EE79),
 (3,0xD2DD4EF5, 90,0xC93E564C, 93,0x4EFDEE00,0x039CF3E8,0x2227B355),
 (2,0xE410811E, 48,0xD68688D3, 94,0x29E98080,0xE410811E,0xDB6E6F3F),
 (3,0xD4D0EA29, 91,0x49243F9B, 95,0x16E03600,0x694448FE,0x408F3479),
 (1,0xFDF5D4C2,102,0x309F94EE, 67,0xCE89B300,0x8215A562,0x898846DB),
)

PAIR_CLAW_SFS = (
 ("7400325643055dfb12e61202f92aaa6b490bf4f8180753d45f96cae3b1fe3668",0x629A0912,0x88C00352),
 ("995ef2d6a10b72f65fa62e6a751e09aabb2b390c9bbb97ef51dcf07add7303cb",0xC8A1B07C,0xFF8B9EF5),
 ("5c4cdb971f9f64c7caccdf2a07d4d86447217ae2dcf52e0aeda0cbadbd6a1f29",0xD5650F74,0xD8AE6222),
 ("b7bd6941a34a4245f2f798dc7656d3bcac96a89eba764691bcd9cfa222c07e41",0xD3FE49AC,0xEF7647DC),
 ("ae63287161bdaba5265848e984a9052da9c7f5ca49419ebf840d3339b2faf303",0x677E3F40,0x6CBCA4BD),
 ("842a793402e247670d652240642e3fb997b95267938ead18a31d04c19989d0ea",0xF5CDC8B2,0xEDF3E648),
 ("710422c38baf779eb014c2ee09e4186bc8575d78fde19f29b044dfb73a041bda",0x6B3D57B0,0x08BAFFFE),
 ("0063162eecd4c142c1ff3bf9552ba2c4064c7ca505e7589e5776bed9d8570b0c",0x749D6340,0xA9E643FD),
 ("56e88ffdbb1cae13f9a5597837283e2664aa9f157c86fd9f5f45422e6608741a",0x9EE6C2AA,0x7BB90315),
 ("abf425ab4b08ea957a364bc0deded5a7b387f3d906a67fe0e69548edd3c6b6b7",0x3AFAC092,0x3DE7BF0D),
 ("a412acf85b5657fc52c62a5a15fac7258f69ed2ad8f0e2855f1e69478805b14d",0xC72091F2,0xBCAAA514),
 ("f03ad0d723b27ed35a405846460e12ae2691f7261b59d0dcd22fe549be672de5",0xDF338394,0x9FB83C8E),
 ("c4348deaa6c7ddd5b9fe9678503d5bb80d85768c6e63be1439c356e54d824d8b",0xC0BDD378,0x29C62801),
 ("c26ae7c543fadfa58f58184208d0ba13579245e880d7260203e1da81119e22f4",0xC1A61296,0xD980C2CA),
 ("260ac19896830359ab67c5aa8fa09c4441d276e63620cf6e93a390ecbe4329f1",0x3CD757A4,0xEEDA1DCC),
 ("395fd61f5d8d7fd391f6801798e35b7adda5b7ad03ce48979ee58c6f93957e3d",0x6E69B390,0x5DD38683),
 ("d2255bc0c45e8a6f47799d00fd7d52afae2edd7548e33d38cb5a1852216def7e",0xBBBFD4FA,0x7CBE41D1),
)

def ror32(x,n):
 x &= MASK32
 return ((x >> n) | ((x << (32 - n)) & MASK32)) & MASK32

def S0(x):
 return ror32(x,2) ^ ror32(x,13) ^ ror32(x,22)

def S1(x):
 return ror32(x,6) ^ ror32(x,11) ^ ror32(x,25)

def s0(x):
 x &= MASK32
 return ror32(x,7) ^ ror32(x,18) ^ (x >> 3)

def s1(x):
 x &= MASK32
 return ror32(x,17) ^ ror32(x,19) ^ (x >> 10)

def CH(x,y,z):
 return ((x & y) ^ ((~x & MASK32) & z)) & MASK32

def MAJ(x,y,z):
 return ((x & y) ^ (x & z) ^ (y & z)) & MASK32

D9 = (BASE_W1[9] - BASE_W0[9]) & MASK32
T9 = (s0(BASE_W1[9]) - s0(BASE_W0[9])) & MASK32

def in_F8(w):
 return ((s0((w + D8) & MASK32) - s0(w)) & MASK32) == T8

def in_F9(w):
 return ((s0((w + D9) & MASK32) - s0(w)) & MASK32) == T9

def enumerate_active_f8_f9():
 """Exhaustively enumerates all 2^14 active states of in_F8 and 2^17 active states of in_F9,
 and verifies the 6,144-mask Lipmaa-Moriai borrow-transition exhaustion over all 2^32 words."""
 f8_active = []
 active_w = 0
 inv_bad = 0
 for idx in range(1 << 14):
  if idx:
   active_w ^= 1 << ACTIVE_BITS_F8[(idx & -idx).bit_length() - 1]
  ok = in_F8(active_w)
  if in_F8(active_w ^ 1) != ok or in_F8(active_w ^ INACTIVE_MASK_F8) != ok:
   inv_bad += 1
  if ok:
   f8_active.append(active_w)

 lm_compat = []
 for k in range(12,24):
  low_dw = ((1 << (min(k,22) - 11)) - 1) << 12
  for hi in range(512):
   dw = low_dw | (hi << 23)
   S = s0(dw)
   b = S ^ T9
   if (b & 1) == 0 and (((b ^ (b >> 1)) & (~S & 0x7FFFFFFF)) == 0):
    lm_compat.append((k,dw))
 if lm_compat != [(12,0x08801000),(13,0x19803000)]:
  inv_bad += 1

 f9_active = []
 active_w = 0
 for idx in range(1 << 17):
  if idx:
   active_w ^= 1 << ACTIVE_BITS_F9[(idx & -idx).bit_length() - 1]
  ok = in_F9(active_w)
  if in_F9(active_w ^ INACTIVE_MASK_F9) != ok:
   inv_bad += 1
  if ok:
   f9_active.append(active_w)
 return f8_active,f9_active,inv_bad

def init_walk_params(cv,target_g=TARGET_W16):
 t2_0 = (S0(cv[0]) + MAJ(cv[0],cv[1],cv[2])) & MASK32
 e0_base = (cv[3] - t2_0) & MASK32
 k0 = (-t2_0 - cv[7] - S1(cv[4]) - CH(cv[4],cv[5],cv[6]) - K39[0]) & MASK32
 c9_0 = (BASE_W0[9] + BASE_A0[5]) & MASK32
 c_walk = (target_g - s1(BASE_W0[14]) - c9_0 - k0 + cv[6] + K39[1]) & MASK32
 return {
  "cv": tuple(cv), "e0_base": e0_base, "k0": k0, "c9_0": c9_0, "c_walk": c_walk,
  "target_g": target_g, "c0_xor_c1": cv[0] ^ cv[1], "c0_and_c1": cv[0] & cv[1],
 }

def F_step(x,wp):
 x &= MASK32
 if x & 1:
  return (s0(x) - x) & MASK32
 cv = wp["cv"]
 e0 = (x + wp["e0_base"]) & MASK32
 return (wp["c_walk"] + S0(x) + MAJ(x,cv[0],cv[1]) + S1(e0) + CH(e0,cv[4],cv[5]) - x) & MASK32

def recover_a1(a0,u,wp):
 cv = wp["cv"]
 e0 = (a0 + wp["e0_base"]) & MASK32
 return (u + S0(a0) + MAJ(a0,cv[0],cv[1]) + S1(e0) + CH(e0,cv[4],cv[5]) + cv[6] + K39[1]) & MASK32

def closed_form_w8_w9_w17(cv,a0,u,wp):
 """Closed-form evaluation of (a1, W2, W8, W9, W17) from a claw (a0, u)."""
 a1 = recover_a1(a0,u,wp)
 t2_5 = (S0(BASE_A0[8]) + MAJ(BASE_A0[8],BASE_A0[7],BASE_A0[6])) & MASK32
 e5 = (a1 + BASE_A0[9] - t2_5) & MASK32
 t2_4 = (S0(BASE_A0[7]) + MAJ(BASE_A0[7],BASE_A0[6],a1)) & MASK32
 e4 = (a0 + BASE_A0[8] - t2_4) & MASK32
 w8 = (BASE_E0[12] - BASE_A0[8] - e4 - S1(BASE_E0[11]) - CH(BASE_E0[11],BASE_E0[10],e5) - K39[8]) & MASK32
 w9 = (BASE_E0[13] - BASE_A0[9] - e5 - S1(BASE_E0[12]) - CH(BASE_E0[12],BASE_E0[11],BASE_E0[10]) - K39[9]) & MASK32
 e0 = (a0 + wp["e0_base"]) & MASK32
 e1 = (cv[2] + a1 - S0(a0) - MAJ(a0,cv[0],cv[1])) & MASK32
 t2_2 = (S0(a1) + MAJ(a1,a0,cv[0])) & MASK32
 t1_2 = (BASE_A0[6] - t2_2) & MASK32
 w2 = (t1_2 - cv[5] - S1(e1) - CH(e1,e0,cv[4]) - K39[2]) & MASK32
 w17 = (s1(BASE_W0[15]) + BASE_W0[10] + s0(w2) + u) & MASK32
 return a1,w2,w8,w9,w17

def build_variant(cv,a0,a1):
 """Reconstructs 2-block state (A, E, W) from (cv, a0, a1) by inverting steps 0..15."""
 A = [list(BASE_A0) + [0] * 23,list(BASE_A1) + [0] * 23]
 E = [list(BASE_E0) + [0] * 23,list(BASE_E1) + [0] * 23]
 W = [list(BASE_W0) + [0] * 23,list(BASE_W1) + [0] * 23]
 for m in range(2):
  for j in range(4):
   A[m][3 - j] = cv[j] & MASK32
   E[m][3 - j] = cv[4 + j] & MASK32
  A[m][4],A[m][5] = a0 & MASK32,a1 & MASK32
  for i in range(6):
   idx = i + 4
   t2 = (S0(A[m][idx - 1]) + MAJ(A[m][idx - 1],A[m][idx - 2],A[m][idx - 3])) & MASK32
   t1 = (A[m][idx] - t2) & MASK32
   E[m][idx] = (A[m][idx - 4] + t1) & MASK32
  for i in range(16):
   idx = i + 4
   t1 = (E[m][idx] - A[m][idx - 4]) & MASK32
   W[m][i] = (t1 - E[m][idx - 4] - S1(E[m][idx - 1]) - CH(E[m][idx - 1],E[m][idx - 2],E[m][idx - 3]) - K39[i]) & MASK32
 return A,E,W

def step_pair(A,E,W,r):
 if r >= 16:
  for m in range(2):
   W[m][r] = (s1(W[m][r - 2]) + W[m][r - 7] + s0(W[m][r - 15]) + W[m][r - 16]) & MASK32
 idx = r + 4
 for m in range(2):
  a,b,c,d = A[m][idx - 1],A[m][idx - 2],A[m][idx - 3],A[m][idx - 4]
  e,f,g,h = E[m][idx - 1],E[m][idx - 2],E[m][idx - 3],E[m][idx - 4]
  t1 = (h + S1(e) + CH(e,f,g) + K39[r] + W[m][r]) & MASK32
  E[m][idx] = (d + t1) & MASK32
  A[m][idx] = (t1 + S0(a) + MAJ(a,b,c)) & MASK32

def sha256_r39_compress(cv_words,msg_words):
 """Independent 39-step SHA-256 compression with Davies-Meyer feed-forward."""
 w = list(msg_words[:16])
 for r in range(16,39):
  w.append((s1(w[r - 2]) + w[r - 7] + s0(w[r - 15]) + w[r - 16]) & MASK32)
 a,b,c,d,e,f,g,h = (x & MASK32 for x in cv_words)
 for r in range(39):
  t1 = (h + S1(e) + CH(e,f,g) + K39[r] + w[r]) & MASK32
  t2 = (S0(a) + MAJ(a,b,c)) & MASK32
  h,g,f,e,d,c,b,a = g,f,e,(d + t1) & MASK32,c,b,a,(t1 + t2) & MASK32
 return tuple((x + y) & MASK32 for x,y in zip(cv_words,(a,b,c,d,e,f,g,h)))

def solve_row_exact(A,E,W,r):
 """Exact bit-by-bit solver for row r in {16, 17, 18} matching bench_t23.c."""
 ma_r,sa_r,me_r,se_r,mw_r,sw_r = ROW_MASKS[r]
 dsch = ((s1(W[1][r - 2]) + W[1][r - 7]) - (s1(W[0][r - 2]) + W[0][r - 7])) & MASK32
 if r == 23:
  dsch = (dsch + T8) & MASK32
 else:
  dsch = (dsch + s0(W[1][r - 15]) - s0(W[0][r - 15])) & MASK32
 idx = r + 4
 t1_0 = (E[0][idx - 4] + S1(E[0][idx - 1]) + CH(E[0][idx - 1],E[0][idx - 2],E[0][idx - 3]) + K39[r]) & MASK32
 t1_1 = (E[1][idx - 4] + S1(E[1][idx - 1]) + CH(E[1][idx - 1],E[1][idx - 2],E[1][idx - 3]) + K39[r]) & MASK32
 t2_0 = (S0(A[0][idx - 1]) + MAJ(A[0][idx - 1],A[0][idx - 2],A[0][idx - 3])) & MASK32
 t2_1 = (S0(A[1][idx - 1]) + MAJ(A[1][idx - 1],A[1][idx - 2],A[1][idx - 3])) & MASK32
 ce0 = (A[0][idx - 4] + t1_0) & MASK32
 ce1 = (A[1][idx - 4] + t1_1 + dsch) & MASK32
 ca0 = (t1_0 + t2_0) & MASK32
 ca1 = (t1_1 + t2_1 + dsch) & MASK32

 by_bit = [[] for _ in range(32)]
 for kr,terms,allowed in CONDS_16_18_23:
  if kr == r:
   mb = max(b for _,rw,b in terms if rw == r)
   by_bit[mb].append((terms,allowed))

 out = []

 def dfs(b,w_low):
  if b == 32:
   out.append(w_low)
   return
  mw = (mw_r >> b) & 1
  sw = (sw_r >> b) & 1
  me = (me_r >> b) & 1
  se = (se_r >> b) & 1
  ma = (ma_r >> b) & 1
  sa = (sa_r >> b) & 1
  for bit in (0,1):
   w = w_low | (bit << b)
   wx1 = ((w + dsch) >> b) & 1
   if (bit ^ wx1) != mw or (bit & mw) != sw:
    continue
   ex_full = (ce0 + w) & MASK32
   ex0 = (ex_full >> b) & 1
   ex1 = ((ce1 + w) >> b) & 1
   if (ex0 ^ ex1) != me or (ex0 & me) != se:
    continue
   ax_full = (ca0 + w) & MASK32
   ax0 = (ax_full >> b) & 1
   ax1 = ((ca1 + w) >> b) & 1
   if (ax0 ^ ax1) != ma or (ax0 & ma) != sa:
    continue
   ok = True
   for terms,allowed in by_bit[b]:
    cidx = 0
    for q,(kind,rw,cb) in enumerate(terms):
     if rw == r:
      word = w if kind == 2 else (ex_full if kind == 1 else ax_full)
     else:
      word = W[0][rw] if kind == 2 else (E[0][rw + 4] if kind == 1 else A[0][rw + 4])
     cidx |= ((word >> cb) & 1) << q
    if not ((allowed >> cidx) & 1):
     ok = False
     break
   if ok:
    dfs(b + 1,w)

 dfs(0,0)
 return out

S1_BASIS = [S1(1 << b) for b in range(32)]

def solve_gf2_subspace(mask_eqs):
 pivots = {}
 for mask,rhs in mask_eqs:
  m = mask
  r = rhs & 1
  while m:
   lsb = (m & -m).bit_length() - 1
   if lsb in pivots:
    pm,pr = pivots[lsb]
    m ^= pm
    r ^= pr
   else:
    pivots[lsb] = (m,r)
    break
  if m == 0 and r != 0:
   return None
 p_cols = sorted(pivots.keys())
 for idx,c in enumerate(p_cols):
  pm,pr = pivots[c]
  for c2 in p_cols[idx + 1 :]:
   if (pm >> c2) & 1:
    pm2,pr2 = pivots[c2]
    pm ^= pm2
    pr ^= pr2
  pivots[c] = (pm,pr)
 x0 = 0
 for c,(pm,pr) in pivots.items():
  if pr:
   x0 |= 1 << c
 free_vars = [b for b in range(32) if b not in pivots]
 basis = []
 for f in free_vars:
  v = 1 << f
  for c,(pm,pr) in pivots.items():
   if (pm >> f) & 1:
    v |= 1 << c
  basis.append(v)
 return x0,basis

def build_row_subspaces():
 """Constructs exact GF(2) affine subspaces for E[0][r+4] at rows 19..22,
 including both d24_25 in {0,1} carry branches at row 20."""
 subs_by_r = {}
 for r in (19,20,21,22):
  nr = r + 1
  me_r,se_r = ROW_MASKS[r][2],ROW_MASKS[r][3]
  me_1,se_1 = ROW_MASKS[r - 1][2],ROW_MASKS[r - 1][3]
  me_2,se_2 = ROW_MASKS[r - 2][2],ROW_MASKS[r - 2][3]
  ma_m3,sa_m3 = ROW_MASKS[r - 3][0],ROW_MASKS[r - 3][1]
  me_m3,se_m3 = ROW_MASKS[r - 3][2],ROW_MASKS[r - 3][3]
  da_m3 = (sa_m3 - (ma_m3 ^ sa_m3)) & MASK32
  de_m3 = (se_m3 - (me_m3 ^ se_m3)) & MASK32
  me_nr,se_nr = ROW_MASKS[nr][2],ROW_MASKS[nr][3]
  de_nr = (se_nr - (me_nr ^ se_nr)) & MASK32
  ch_bits = [b for b in range(32) if ((me_1 | me_2) >> b) & 1]
  M_s1 = S1(me_r)
  s1_bits = [b for b in range(32) if (M_s1 >> b) & 1]
  base_eqs = [(1 << b,(se_r >> b) & 1) for b in range(32) if (me_r >> b) & 1]
  if r == 19:
   base_eqs.append((1 << 16,1))
  dch_branches = ((0,0x00010000),(1,0x01010000)) if r == 20 else ((0,0),)
  for d24_25,dch_mr in dch_branches:
   row_subs = []
   for ch_mask in range(1 << len(ch_bits)):
    dch = dch_mr
    eqs_ch = list(base_eqs)
    for idx,b in enumerate(ch_bits):
     bit_val = (ch_mask >> idx) & 1
     eqs_ch.append((1 << b,bit_val))
     if (me_1 >> b) & 1 and bit_val == 1:
      dch = (dch + (1 if ((se_1 >> b) & 1) else -1) * (1 << b)) & MASK32
     elif (me_2 >> b) & 1 and bit_val == 0:
      dch = (dch + (1 if ((se_2 >> b) & 1) else -1) * (1 << b)) & MASK32
    req_ds1 = (de_nr - da_m3 - de_m3 - dch) & MASK32
    target_2y = (req_ds1 + M_s1) & MASK32
    for s1_mask in range(1 << len(s1_bits)):
     y_val = sum((1 << b) for idx,b in enumerate(s1_bits) if (s1_mask >> idx) & 1)
     if ((2 * y_val) & MASK32) != target_2y:
      continue
     eqs = list(eqs_ch)
     for idx,b in enumerate(s1_bits):
      bit_v = (s1_mask >> idx) & 1
      m_row = sum((1 << j) for j in range(32) if (S1_BASIS[j] >> b) & 1)
      eqs.append((m_row,bit_v))
     res = solve_gf2_subspace(eqs)
     if res is not None:
      row_subs.append(res)
   if r == 20:
    subs_by_r[(20,d24_25)] = row_subs
   if d24_25 == 0:
    subs_by_r[r] = row_subs
 return subs_by_r

def set_row_state(A,E,W,r,w0):
 A = [list(A[0]),list(A[1])]
 E = [list(E[0]),list(E[1])]
 W = [list(W[0]),list(W[1])]
 dsch = ((s1(W[1][r - 2]) + W[1][r - 7]) - (s1(W[0][r - 2]) + W[0][r - 7])) & MASK32
 if r == 23:
  dsch = (dsch + T8) & MASK32
 else:
  dsch = (dsch + s0(W[1][r - 15]) - s0(W[0][r - 15])) & MASK32
 W[0][r] = w0
 W[1][r] = (w0 + dsch) & MASK32
 idx = r + 4
 for m in range(2):
  a,b,c,d = A[m][idx - 1],A[m][idx - 2],A[m][idx - 3],A[m][idx - 4]
  e,f,g,h = E[m][idx - 1],E[m][idx - 2],E[m][idx - 3],E[m][idx - 4]
  t1 = (h + S1(e) + CH(e,f,g) + K39[r] + W[m][r]) & MASK32
  E[m][idx] = (d + t1) & MASK32
  A[m][idx] = (t1 + S0(a) + MAJ(a,b,c)) & MASK32
 return A,E,W

def lookahead_ok(A,E,W,r):
 nr = r + 1
 dsch = ((s1(W[1][nr - 2]) + W[1][nr - 7]) - (s1(W[0][nr - 2]) + W[0][nr - 7])) & MASK32
 if nr == 23:
  dsch = (dsch + T8) & MASK32
 else:
  dsch = (dsch + s0(W[1][nr - 15]) - s0(W[0][nr - 15])) & MASK32
 idx = nr + 4
 t1_0 = (E[0][idx - 4] + S1(E[0][idx - 1]) + CH(E[0][idx - 1],E[0][idx - 2],E[0][idx - 3]) + K39[nr]) & MASK32
 t1_1 = (E[1][idx - 4] + S1(E[1][idx - 1]) + CH(E[1][idx - 1],E[1][idx - 2],E[1][idx - 3]) + K39[nr]) & MASK32
 ce0 = (A[0][idx - 4] + t1_0) & MASK32
 ce1 = (A[1][idx - 4] + t1_1 + dsch) & MASK32
 me_nr,se_nr = ROW_MASKS[nr][2],ROW_MASKS[nr][3]
 de = (se_nr - (me_nr ^ se_nr)) & MASK32
 if ((ce0 - ce1) & MASK32) != de:
  return False
 t2_0 = (S0(A[0][idx - 1]) + MAJ(A[0][idx - 1],A[0][idx - 2],A[0][idx - 3])) & MASK32
 t2_1 = (S0(A[1][idx - 1]) + MAJ(A[1][idx - 1],A[1][idx - 2],A[1][idx - 3])) & MASK32
 ca0 = (t1_0 + t2_0) & MASK32
 ca1 = (t1_1 + t2_1 + dsch) & MASK32
 ma_nr,sa_nr = ROW_MASKS[nr][0],ROW_MASKS[nr][1]
 da = (sa_nr - (ma_nr ^ sa_nr)) & MASK32
 return ((ca0 - ca1) & MASK32) == da

def invert_rollout_to_sfs(A,E,W):
 """Inverts a step-23..38 rollout collision downward to a 39-step SFS colliding pair."""
 A = [list(A[0]),list(A[1])]
 E = [list(E[0]),list(E[1])]
 W = [list(W[0]),list(W[1])]
 for m in range(2):
  for r in range(23,15,-1):
   W[m][r - 16] = (W[m][r] - s1(W[m][r - 2]) - W[m][r - 7] - s0(W[m][r - 15])) & MASK32
  t1_9 = (E[m][13] - A[m][9]) & MASK32
  E[m][9] = (t1_9 - W[m][9] - S1(E[m][12]) - CH(E[m][12],E[m][11],E[m][10]) - K39[9]) & MASK32
  t2_5 = (S0(A[m][8]) + MAJ(A[m][8],A[m][7],A[m][6])) & MASK32
  A[m][5] = (E[m][9] - (A[m][9] - t2_5)) & MASK32
  t1_8 = (E[m][12] - A[m][8]) & MASK32
  E[m][8] = (t1_8 - W[m][8] - S1(E[m][11]) - CH(E[m][11],E[m][10],E[m][9]) - K39[8]) & MASK32
  t2_4 = (S0(A[m][7]) + MAJ(A[m][7],A[m][6],A[m][5])) & MASK32
  A[m][4] = (E[m][8] - (A[m][8] - t2_4)) & MASK32
  for i in range(7,3,-1):
   idx = i + 4
   t1_i = (E[m][idx] - A[m][idx - 4]) & MASK32
   E[m][idx - 4] = (t1_i - W[m][i] - S1(E[m][idx - 1]) - CH(E[m][idx - 1],E[m][idx - 2],E[m][idx - 3]) - K39[i]) & MASK32
  for i in range(3,-1,-1):
   idx = i + 4
   t2_i = (S0(A[m][idx - 1]) + MAJ(A[m][idx - 1],A[m][idx - 2],A[m][idx - 3])) & MASK32
   t1_i = (A[m][idx] - t2_i) & MASK32
   A[m][idx - 4] = (E[m][idx] - t1_i) & MASK32
   E[m][idx - 4] = (t1_i - W[m][i] - S1(E[m][idx - 1]) - CH(E[m][idx - 1],E[m][idx - 2],E[m][idx - 3]) - K39[i]) & MASK32
 cv = [A[0][3 - j] for j in range(4)] + [E[0][3 - j] for j in range(4)]
 return cv,A[0][4],A[0][5],W[0][1]

def w9_even_a0_bit(w9):
 """Returns the exact parity bit (W8[0] & 1) required for the inverted SFS state to have even a0."""
 t1_9 = (BASE_E0[13] - BASE_A0[9]) & MASK32
 e9 = (t1_9 - w9 - S1(BASE_E0[12]) - CH(BASE_E0[12],BASE_E0[11],BASE_E0[10]) - K39[9]) & MASK32
 t2_5 = (S0(BASE_A0[8]) + MAJ(BASE_A0[8],BASE_A0[7],BASE_A0[6])) & MASK32
 a5 = (e9 - (BASE_A0[9] - t2_5)) & MASK32
 t1_8_no_w8 = (BASE_E0[12] - BASE_A0[8] - S1(BASE_E0[11]) - CH(BASE_E0[11],BASE_E0[10],e9) - K39[8]) & MASK32
 t2_4 = (S0(BASE_A0[7]) + MAJ(BASE_A0[7],BASE_A0[6],a5)) & MASK32
 return (t1_8_no_w8 - (BASE_A0[8] - t2_4)) & 1

LANES = 7
PITCH = 36
C_BLOCK = 2812
REGISTERS = 64
INSTR_BYTES = 36

def broadcast36(val32):
 v,acc = val32 & MASK32,0
 for l in range(LANES):
  acc |= v << (l * PITCH)
 return acc

PACK_MASK32 = broadcast36(MASK32)
PACK_LSB = broadcast36(1)
FULL_WORD_MASK = (1 << 256) - 1

def pack_lanes(words):
 acc = 0
 for l,w in enumerate(words):
  acc |= (w & MASK32) << (l * PITCH)
 return acc

def unpack_lanes(packed):
 return [((packed >> (l * PITCH)) & MASK32) for l in range(LANES)]

class Tracer:
 def __init__(self):
  self.ops,self.next_id = [],0
 def reg(self,name=None):
  r = self.next_id
  self.next_id += 1
  return r
 def _emit(self,op,a,b):
  dst = self.reg()
  self.ops.append((op,dst,a,b))
  return dst
 def bxor(self,a,b): return self._emit("xor",a,b)
 def band(self,a,b): return self._emit("and",a,b)
 def bor(self,a,b): return self._emit("or",a,b)
 def shl(self,a,s): return self._emit("shl",a,s)
 def shr(self,a,s): return self._emit("shr",a,s)
 def add(self,a,b): return self._emit("add",a,b)
 def sub(self,a,b): return self._emit("sub",a,b)
 def bxor_c(self,a,c32): return self._emit("xor_c",a,c32 & MASK32)
 def band_c(self,a,c32): return self._emit("and_c",a,c32 & MASK32)
 def add_c(self,a,c32): return self._emit("add_c",a,c32 & MASK32)

def build_traced_step(fold_maj=True,include_dp=False):
 tr = Tracer()
 x,e0_base,c_walk,c5 = tr.reg("x"),tr.reg("e0_base"),tr.reg("c_walk"),tr.reg("c5")
 if fold_maj:
  c0_xor_c1,c0_and_c1,c4_xor_c5 = tr.reg("c0_xor_c1"),tr.reg("c0_and_c1"),tr.reg("c4_xor_c5")
  in_regs = (x,e0_base,c_walk,c5,c0_xor_c1,c0_and_c1,c4_xor_c5)
 else:
  c0,c1,c4 = tr.reg("c0"),tr.reg("c1"),tr.reg("c4")
  in_regs = (x,e0_base,c_walk,c5,c0,c1,c4)
 def ror_p(v,n):
  return tr.bor(tr.band_c(tr.shr(v,n),(1 << (32 - n)) - 1),tr.band_c(tr.shl(v,32 - n),((1 << n) - 1) << (32 - n)))
 def shr_p(v,n):
  return tr.band_c(tr.shr(v,n),(1 << (32 - n)) - 1)
 s0_x = tr.bxor(tr.bxor(ror_p(x,7),ror_p(x,18)),shr_p(x,3))
 S0_x = tr.bxor(tr.bxor(ror_p(x,2),ror_p(x,13)),ror_p(x,22))
 maj_x = tr.bxor(tr.band(x,c0_xor_c1),c0_and_c1) if fold_maj else tr.bxor(tr.bxor(tr.band(x,c0),tr.band(x,c1)),tr.band(c0,c1))
 e0 = tr.add(x,e0_base)
 S1_e0 = tr.bxor(tr.bxor(ror_p(e0,6),ror_p(e0,11)),ror_p(e0,25))
 ch_e0 = tr.bxor(c5,tr.band(e0,c4_xor_c5)) if fold_maj else tr.bxor(c5,tr.band(e0,tr.bxor(c4,c5)))
 even_pre = tr.band_c(tr.add(tr.add(c_walk,S0_x),tr.add(maj_x,tr.add(S1_e0,ch_e0))),MASK32)
 p = tr.band_c(x,1)
 m = tr.add_c(p,MASK32)
 blended = tr.bxor(s0_x,tr.band(m,tr.bxor(s0_x,even_pre)))
 neg_x = tr.add_c(tr.bxor_c(x,MASK32),1)
 out = tr.band_c(tr.add(blended,neg_x),MASK32)
 if include_dp:
  dp_word = tr.band_c(tr.bxor_c(tr.add_c(tr.band_c(out,0x7F),0x7F),0x80),0x80)
  return tr.ops,in_regs,out,dp_word
 return tr.ops,in_regs,out

def allocate(ops,in_regs,out_reg,extra_out_reg=None):
 reg_ops = {"xor","and","or","add","sub"}
 last_use = {r: 0 for r in in_regs}
 for idx,(op,dst,a,b) in enumerate(ops):
  last_use[dst] = last_use[a] = idx
  if op in reg_ops:
   last_use[b] = idx
 last_use[out_reg] = len(ops)
 if extra_out_reg is not None:
  last_use[extra_out_reg] = len(ops)
 phys,free,pinned = {},list(range(REGISTERS - 1,-1,-1)),set(in_regs[1:])
 for r in in_regs:
  phys[r] = free.pop()
 in_phys,peak_live,alloc_ops = [phys[r] for r in in_regs],len(in_regs),[]
 for idx,(op,dst,a,b) in enumerate(ops):
  pa,pb = phys[a],(phys[b] if op in reg_ops else b)
  for r in (a,b if op in reg_ops else None):
   if r is not None and r not in pinned and last_use.get(r,-1) == idx and r in phys:
    free.append(phys.pop(r))
  pd = free.pop()
  phys[dst] = pd
  peak_live = max(peak_live,REGISTERS - len(free))
  alloc_ops.append((op,pd,pa,pb))
 if extra_out_reg is not None:
  return alloc_ops,in_phys,phys[out_reg],phys[extra_out_reg],peak_live
 return alloc_ops,in_phys,phys[out_reg],peak_live

def spill_ops(peak_live,n_regs=REGISTERS):
 return 0 if peak_live <= n_regs else 2 * (peak_live - n_regs)

def run_allocated(alloc_ops,in_phys,out_phys,x_packed,wp,fold_maj=True,dp_phys=None):
 rf,cv = [0] * REGISTERS,wp["cv"]
 vals = [x_packed,broadcast36(wp["e0_base"]),broadcast36(wp["c_walk"]),broadcast36(cv[5])]
 if fold_maj:
  vals.extend([broadcast36(wp["c0_xor_c1"]),broadcast36(wp["c0_and_c1"]),broadcast36(cv[4] ^ cv[5])])
 else:
  vals.extend([broadcast36(cv[0]),broadcast36(cv[1]),broadcast36(cv[4])])
 for p,v in zip(in_phys,vals):
  rf[p] = v
 for op,pd,pa,pb in alloc_ops:
  va = rf[pa]
  if op == "xor": rf[pd] = va ^ rf[pb]
  elif op == "and": rf[pd] = va & rf[pb]
  elif op == "or": rf[pd] = va | rf[pb]
  elif op == "shl": rf[pd] = (va << pb) & FULL_WORD_MASK
  elif op == "shr": rf[pd] = va >> pb
  elif op == "add": rf[pd] = (va + rf[pb]) & FULL_WORD_MASK
  elif op == "sub": rf[pd] = (va - rf[pb]) & FULL_WORD_MASK
  elif op == "xor_c": rf[pd] = va ^ broadcast36(pb)
  elif op == "and_c": rf[pd] = va & broadcast36(pb)
  elif op == "add_c": rf[pd] = (va + broadcast36(pb)) & FULL_WORD_MASK
 return (rf[out_phys],rf[dp_phys]) if dp_phys is not None else rf[out_phys]

def stage1_dp_mask(x_packed,dp_bits=7):
 dp_mask = (1 << dp_bits) - 1
 return sum((1 << l) for l in range(LANES) if ((x_packed >> (l * PITCH)) & dp_mask) == 0)

def swar_dp_word_to_mask(dp_word):
 return sum((1 << l) for l in range(LANES) if (dp_word >> (l * PITCH + 7)) & 1)

def recover_1pair_simd7(sa,sb,la,lb,wp,alloc_ops,in_phys,out_phys):
 a,b,l_a,l_b,batches,found = sa & MASK32,sb & MASK32,la,lb,0,None
 while l_a != l_b:
  y_step = run_allocated(alloc_ops,in_phys,out_phys,a if l_a > l_b else b,wp) & MASK32
  batches += 1
  if l_a > l_b:
   a,l_a = y_step,l_a - 1
  else:
   b,l_b = y_step,l_b - 1
 while a != b and l_a > 0:
  out_ab = run_allocated(alloc_ops,in_phys,out_phys,(a & MASK32) | ((b & MASK32) << PITCH),wp)
  batches += 1
  fa,fb = out_ab & MASK32,(out_ab >> PITCH) & MASK32
  if fa == fb:
   if (a ^ b) & 1:
    found = (b,a) if (a & 1) else (a,b)
   break
  a,b,l_a = fa,fb,l_a - 1
 return found,batches

def recover_7pairs_packed(pairs,wp,alloc_ops,in_phys,out_phys):
 assert 1 <= len(pairs) <= LANES
 pad = [0] * (LANES - len(pairs))
 a_lanes,b_lanes = [p[0] for p in pairs] + pad,[p[1] for p in pairs] + pad
 la_lanes,lb_lanes = [p[2] for p in pairs] + pad,[p[3] for p in pairs] + pad
 batches = 0
 while True:
  need,step_x,which = False,[0] * LANES,[0] * LANES
  for l in range(len(pairs)):
   if la_lanes[l] > lb_lanes[l]:
    step_x[l],which[l],need = a_lanes[l],1,True
   elif lb_lanes[l] > la_lanes[l]:
    step_x[l],which[l],need = b_lanes[l],2,True
  if not need:
   break
  nxt = unpack_lanes(run_allocated(alloc_ops,in_phys,out_phys,pack_lanes(step_x),wp))
  batches += 1
  for l in range(len(pairs)):
   if which[l] == 1:
    a_lanes[l],la_lanes[l] = nxt[l],la_lanes[l] - 1
   elif which[l] == 2:
    b_lanes[l],lb_lanes[l] = nxt[l],lb_lanes[l] - 1
 found = [None] * len(pairs)
 active = [l for l in range(len(pairs)) if a_lanes[l] != b_lanes[l] and la_lanes[l] > 0]
 while active:
  fa = unpack_lanes(run_allocated(alloc_ops,in_phys,out_phys,pack_lanes(a_lanes),wp))
  fb = unpack_lanes(run_allocated(alloc_ops,in_phys,out_phys,pack_lanes(b_lanes),wp))
  batches += 2
  still = []
  for l in active:
   if fa[l] == fb[l]:
    if (a_lanes[l] ^ b_lanes[l]) & 1:
     found[l] = (b_lanes[l],a_lanes[l]) if (a_lanes[l] & 1) else (a_lanes[l],b_lanes[l])
   else:
    a_lanes[l],b_lanes[l],la_lanes[l] = fa[l],fb[l],la_lanes[l] - 1
    if la_lanes[l] > 0:
     still.append(l)
  active = still
 return found,batches

def run_live_reduced_vow(wp,seed_state,n_slots=256,dp_bits=3,max_steps=64,n_walks=640,table=None,gen_id=1):
 dp_mask,slot_mask = (1 << dp_bits) - 1,n_slots - 1
 if table is None:
  table = [0] * n_slots
 raw_claws,distinct_claws,dp_hits,val_matches,st = [],set(),0,0,seed_state & 0xFFFFFFFFFFFFFFFF
 for _ in range(n_walks):
  v,st = splitmix64(st)
  sa = x = v & 0xFFFF
  for step_i in range(1,max_steps + 1):
   x = F_step(x,wp) & 0xFFFF
   if (x & dp_mask) == 0:
    dp_hits += 1
    slot = (x >> dp_bits) & slot_mask
    prev_packed = table[slot]
    meta_new = ((step_i & 0x7FF) << 19) | ((sa & 1) << 18) | (gen_id & 0x3FFFF)
    table[slot] = ((sa & MASK32) << 64) | (meta_new << 32) | (x & MASK32)
    if prev_packed != 0:
     prev_sa = (prev_packed >> 64) & MASK32
     prev_meta = (prev_packed >> 32) & MASK32
     prev_x = prev_packed & MASK32
     prev_step = (prev_meta >> 19) & 0x7FF
     prev_gen = prev_meta & 0x3FFFF
     if prev_gen == (gen_id & 0x3FFFF) and prev_x == x and prev_step != step_i:
      val_matches += 1
      a,b,la,lb = prev_sa,sa,prev_step,step_i
      for _ in range(abs(la - lb)):
       if la > lb:
        a,la = F_step(a,wp) & 0xFFFF,la - 1
       else:
        b,lb = F_step(b,wp) & 0xFFFF,lb - 1
      for _ in range(la):
       if a == b:
        break
       fa,fb = F_step(a,wp) & 0xFFFF,F_step(b,wp) & 0xFFFF
       if fa == fb:
        if (a ^ b) & 1:
         pair_c = (b,a) if (a & 1) else (a,b)
         raw_claws.append(pair_c)
         distinct_claws.add(pair_c)
        break
       a,b = fa,fb
    break
 return raw_claws,distinct_claws,dp_hits,val_matches

def splitmix64(state):
 z = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
 z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
 z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
 return z ^ (z >> 31),(state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF

def derive_cv(seed_int):
 st,cv = seed_int & 0xFFFFFFFFFFFFFFFF,[]
 for _ in range(8):
  v,st = splitmix64(st)
  cv.append(v & MASK32)
 return cv,st

def ledger():
 ops_fold,in_f,out_f = build_traced_step(fold_maj=True,include_dp=False)
 alloc_f,_,_,peak_f = allocate(ops_fold,in_f,out_f)
 ops_nofold,in_nf,out_nf = build_traced_step(fold_maj=False,include_dp=False)
 alloc_nf,_,_,_ = allocate(ops_nofold,in_nf,out_nf)
 ops_s1,in_s1,out_s1,dp_s1 = build_traced_step(fold_maj=True,include_dp=True)
 alloc_s1,_,_,_,peak_s1 = allocate(ops_s1,in_s1,out_s1,dp_s1)
 ops_s1_nf,in_s1_nf,out_s1_nf,dp_s1_nf = build_traced_step(fold_maj=False,include_dp=True)
 alloc_s1_nf,_,_,_,_ = allocate(ops_s1_nf,in_s1_nf,out_s1_nf,dp_s1_nf)
 step_ops,stage1_traced_ops = len(alloc_f),len(alloc_s1)
 stage1_ops,stage1_ops_unpacked,loop_ops = 5,27,2
 stage2_ctrl_ops_simd7,stage2_ctrl_ops_stream7 = 8,29
 main_batch_ops,main_batch_ops_unpacked = step_ops + stage1_ops + loop_ops,step_ops + stage1_ops_unpacked + loop_ops
 rec_batch_ops_simd7,rec_batch_ops_stream7 = step_ops + loop_ops + stage2_ctrl_ops_simd7,step_ops + loop_ops + stage2_ctrl_ops_stream7
 tot_evals,main_batches,dp_hits = 268435704,38347958,2092676
 val_matches,raw_claws,distinct_claws,min_win = 330778,162983,135412,33772
 rec_batches_simd7,rec_batches_stream7 = 27708681,10568425
 main_b_per_claw,rec7_b_per_claw,recs_b_per_claw = main_batches / distinct_claws,rec_batches_simd7 / distinct_claws,rec_batches_stream7 / distinct_claws
 dp_hit_ops_per_hit,recover_a1_ops_per_raw_claw = 42.0,34.0
 dp_hit_ops,recover_a1_ops = (dp_hits / distinct_claws) * dp_hit_ops_per_hit,(raw_claws / distinct_claws) * recover_a1_ops_per_raw_claw
 staged_filter_ops = 14.0 + (65.0 / 4096.0) * 64.0 + (585.0 / 524288.0) * (7968.0 / 4294967296.0)
 cv_refresh_ops = (C_BLOCK + 260.0) / (distinct_claws / 4.0)
 non_kernel_ops = dp_hit_ops + recover_a1_ops + staged_filter_ops + cv_refresh_ops
 ops_per_claw_simd7 = main_b_per_claw * main_batch_ops + rec7_b_per_claw * rec_batch_ops_simd7 + non_kernel_ops
 ops_per_claw_simd7_unpacked = main_b_per_claw * main_batch_ops_unpacked + rec7_b_per_claw * rec_batch_ops_simd7 + non_kernel_ops
 ops_per_claw_simd7_unpacked_min_win = ops_per_claw_simd7_unpacked * ((distinct_claws / 4.0) / min_win)
 ops_per_claw_stream7 = main_b_per_claw * main_batch_ops + recs_b_per_claw * rec_batch_ops_stream7 + non_kernel_ops
 ops_per_claw_stream7_unpacked = main_b_per_claw * main_batch_ops_unpacked + recs_b_per_claw * rec_batch_ops_stream7 + non_kernel_ops
 log2_p89,log2_p17 = math.log2(585.0 / 524288.0),-32.0
 log2_tail18_lcb99,log2_tail18_mean_log2,log2_tail18_log2_mean = -75.4278,-75.3583,-75.3398
 log2_tail18_lcb99_linear = -75.4116
 log2_tail18_live16_lcb99,log2_tail18_live16_lcb99_linear = -75.6713,-75.6340
 log2_tail18_conservative_floor = -75.7000
 log2_p_claw,log2_p_claw_live16 = log2_p89 + log2_p17 + log2_tail18_lcb99,log2_p89 + log2_p17 + log2_tail18_live16_lcb99
 log2_p_claw_floor = log2_p89 + log2_p17 + log2_tail18_conservative_floor
 lam_39 = -math.log(0.61)
 log2_n_claws,log2_n_claws_live16 = math.log2(lam_39) - log2_p_claw,math.log2(lam_39) - log2_p_claw_live16
 log2_n_claws_floor = math.log2(lam_39) - log2_p_claw_floor
 time_log2_simd7 = log2_n_claws + math.log2(ops_per_claw_simd7 / C_BLOCK)
 time_log2_simd7_unpacked = log2_n_claws + math.log2(ops_per_claw_simd7_unpacked / C_BLOCK)
 time_log2_simd7_unpacked_min_win = log2_n_claws + math.log2(ops_per_claw_simd7_unpacked_min_win / C_BLOCK)
 time_log2_stream7 = log2_n_claws + math.log2(ops_per_claw_stream7 / C_BLOCK)
 time_log2_stream7_unpacked = log2_n_claws + math.log2(ops_per_claw_stream7_unpacked / C_BLOCK)
 time_log2_simd7_live16 = log2_n_claws_live16 + math.log2(ops_per_claw_simd7 / C_BLOCK)
 time_log2_simd7_unpacked_live16 = log2_n_claws_live16 + math.log2(ops_per_claw_simd7_unpacked / C_BLOCK)
 time_log2_simd7_unpacked_min_win_live16 = log2_n_claws_live16 + math.log2(ops_per_claw_simd7_unpacked_min_win / C_BLOCK)
 time_log2_stream7_live16 = log2_n_claws_live16 + math.log2(ops_per_claw_stream7 / C_BLOCK)
 time_log2_stream7_unpacked_live16 = log2_n_claws_live16 + math.log2(ops_per_claw_stream7_unpacked / C_BLOCK)
 time_log2_simd7_floor = log2_n_claws_floor + math.log2(ops_per_claw_simd7 / C_BLOCK)
 time_log2_simd7_unpacked_floor = log2_n_claws_floor + math.log2(ops_per_claw_simd7_unpacked / C_BLOCK)
 time_log2_simd7_unpacked_min_win_floor = log2_n_claws_floor + math.log2(ops_per_claw_simd7_unpacked_min_win / C_BLOCK)
 time_log2_stream7_floor = log2_n_claws_floor + math.log2(ops_per_claw_stream7 / C_BLOCK)
 time_log2_stream7_unpacked_floor = log2_n_claws_floor + math.log2(ops_per_claw_stream7_unpacked / C_BLOCK)
 claimed_time_log2,memory_log2_bytes = 120.46,20
 dp_table_bytes,code_bytes,reg_bytes,scratch_bytes = 65536 * 12,512 * INSTR_BYTES,REGISTERS * 32,16384
 total_mem_bytes = dp_table_bytes + code_bytes + reg_bytes + scratch_bytes
 return {
  "machine_model": {
   "lanes": LANES, "pitch_bits": PITCH, "registers": REGISTERS, "c_block_ops": C_BLOCK,
   "step_ops_folded": step_ops, "step_ops_unfolded": len(alloc_nf),
   "stage1_traced_ops_folded": stage1_traced_ops, "stage1_traced_ops_unfolded": len(alloc_s1_nf),
   "peak_live_regs": max(peak_f, peak_s1), "spill_ops_64": spill_ops(max(peak_f, peak_s1), REGISTERS),
   "stage1_ops_swar": stage1_ops, "stage1_ops_unpacked": stage1_ops_unpacked, "loop_ops": loop_ops,
   "stage2_ctrl_ops_simd7": stage2_ctrl_ops_simd7, "stage2_ctrl_ops_stream7": stage2_ctrl_ops_stream7,
   "main_batch_ops": main_batch_ops, "main_batch_ops_unpacked": main_batch_ops_unpacked,
   "rec_batch_ops_simd7": rec_batch_ops_simd7, "rec_batch_ops_stream7": rec_batch_ops_stream7,
  },
  "vow_64k_benchmark": {
   "n_slots": 65536, "dp_bits": 7, "max_steps": 2048, "total_walk_evals": tot_evals,
   "main_7lane_batches": main_batches, "dp_hits": dp_hits, "val_matches": val_matches,
   "raw_claws": raw_claws, "distinct_claws": distinct_claws, "min_window_distinct_claws": min_win,
   "f89_joint_passes": 157,
   "w17_byte_matches_b0_b1_b2_b3": [517, 486, 525, 526], "w17_expected_byte_matches": round(distinct_claws / 256.0, 2),
   "w17_16bit_prefix_matches": 4, "w17_low4_given_f89": [13, 157],
   "main_batches_per_distinct_claw": round(main_b_per_claw, 4), "rec_batches_simd7_per_distinct_claw": round(rec7_b_per_claw, 4),
   "rec_batches_stream7_per_distinct_claw": round(recs_b_per_claw, 4),
   "dp_hit_ops_per_hit": dp_hit_ops_per_hit, "recover_a1_ops_per_raw_claw": recover_a1_ops_per_raw_claw,
   "dp_hit_ops_per_distinct_claw": round(dp_hit_ops, 4), "recover_a1_ops_per_distinct_claw": round(recover_a1_ops, 4),
   "staged_filter_ops_per_distinct_claw": round(staged_filter_ops, 4), "cv_refresh_ops_per_distinct_claw": round(cv_refresh_ops, 4),
   "non_kernel_ops_per_distinct_claw": round(non_kernel_ops, 4),
   "ops_per_distinct_claw_simd7": round(ops_per_claw_simd7, 2), "ops_per_distinct_claw_simd7_unpacked": round(ops_per_claw_simd7_unpacked, 2),
   "ops_per_distinct_claw_simd7_unpacked_min_win": round(ops_per_claw_simd7_unpacked_min_win, 2),
   "ops_per_distinct_claw_stream7": round(ops_per_claw_stream7, 2), "ops_per_distinct_claw_stream7_unpacked": round(ops_per_claw_stream7_unpacked, 2),
   "sha256_equiv_per_claw_simd7": round(ops_per_claw_simd7 / C_BLOCK, 4),
   "sha256_equiv_per_claw_simd7_unpacked": round(ops_per_claw_simd7_unpacked / C_BLOCK, 4),
   "sha256_equiv_per_claw_simd7_unpacked_min_win": round(ops_per_claw_simd7_unpacked_min_win / C_BLOCK, 4),
   "sha256_equiv_per_claw_stream7": round(ops_per_claw_stream7 / C_BLOCK, 4),
   "sha256_equiv_per_claw_stream7_unpacked": round(ops_per_claw_stream7_unpacked / C_BLOCK, 4),
  },
  "probability_model": {
   "log2_p8_p9_exact": round(log2_p89, 6), "log2_p17_conditional_uniformity": log2_p17,
   "log2_tail18_point_mean_log2": log2_tail18_mean_log2, "log2_tail18_point_log2_mean": log2_tail18_log2_mean,
   "log2_tail18_student_t_lcb99": log2_tail18_lcb99, "log2_tail18_student_t_lcb99_linear": log2_tail18_lcb99_linear,
   "log2_tail18_live16_lcb99": log2_tail18_live16_lcb99, "log2_tail18_live16_lcb99_linear": log2_tail18_live16_lcb99_linear,
   "log2_tail18_conservative_floor": log2_tail18_conservative_floor,
   "log2_p_claw_conservative": round(log2_p_claw, 6), "log2_p_claw_live16_lcb99": round(log2_p_claw_live16, 6),
   "log2_p_claw_floor": round(log2_p_claw_floor, 6),
   "target_success_prob": 0.39,
   "log2_n_distinct_claws": round(log2_n_claws, 6), "log2_n_distinct_claws_live16": round(log2_n_claws_live16, 6),
   "log2_n_distinct_claws_floor": round(log2_n_claws_floor, 6),
  },
  "memory_breakdown": {
   "dp_table_bytes": dp_table_bytes, "code_bytes": code_bytes, "register_file_bytes": reg_bytes,
   "scratch_and_advice_bytes": scratch_bytes, "total_resident_bytes": total_mem_bytes,
   "memory_log2_bytes": memory_log2_bytes,
  },
  "headline": {
   "computed_time_log2_simd7": round(time_log2_simd7, 4), "computed_time_log2_simd7_unpacked": round(time_log2_simd7_unpacked, 4),
   "computed_time_log2_simd7_unpacked_min_win": round(time_log2_simd7_unpacked_min_win, 4),
   "computed_time_log2_stream7": round(time_log2_stream7, 4), "computed_time_log2_stream7_unpacked": round(time_log2_stream7_unpacked, 4),
   "computed_time_log2_simd7_live16": round(time_log2_simd7_live16, 4),
   "computed_time_log2_simd7_unpacked_live16": round(time_log2_simd7_unpacked_live16, 4),
   "computed_time_log2_simd7_unpacked_min_win_live16": round(time_log2_simd7_unpacked_min_win_live16, 4),
   "computed_time_log2_stream7_live16": round(time_log2_stream7_live16, 4),
   "computed_time_log2_stream7_unpacked_live16": round(time_log2_stream7_unpacked_live16, 4),
   "computed_time_log2_simd7_floor": round(time_log2_simd7_floor, 4),
   "computed_time_log2_simd7_unpacked_floor": round(time_log2_simd7_unpacked_floor, 4),
   "computed_time_log2_simd7_unpacked_min_win_floor": round(time_log2_simd7_unpacked_min_win_floor, 4),
   "computed_time_log2_stream7_floor": round(time_log2_stream7_floor, 4),
   "computed_time_log2_stream7_unpacked_floor": round(time_log2_stream7_unpacked_floor, 4),
   "claimed_time_log2": claimed_time_log2, "memory_log2_bytes": memory_log2_bytes, "score": claimed_time_log2,
  },
 }

ACTIVE_TRIALS,GATE_TRIAL,RETURNED_TRIALS = 16,16,17
SHA256_IV = (
 0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,
 0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19,
)

def verify_claw_sfs_tuple(cv_hex,a0,a1):
 cv = list(struct.unpack(">8I",bytes.fromhex(cv_hex)))
 wp = init_walk_params(cv)
 A,E,W = build_variant(cv,a0,a1)
 u = W[0][1]
 bad = 0
 if (a0 & 1) != 0 or (u & 1) != 1 or F_step(a0,wp) != F_step(u,wp) or recover_a1(a0,u,wp) != a1:
  bad += 1
 if not (in_F8(W[0][8]) and in_F9(W[0][9])) or w9_even_a0_bit(W[0][9]) != (W[0][8] & 1):
  bad += 1
 for r in range(39):
  step_pair(A,E,W,r)
 for r in (16,17,18):
  ma,sa,me,se,mw,sw = ROW_MASKS[r]
  idx = r + 4
  if (A[0][idx] ^ A[1][idx]) != ma or (A[0][idx] & ma) != sa or (E[0][idx] ^ E[1][idx]) != me or (E[0][idx] & me) != se or (W[0][r] ^ W[1][r]) != mw or (W[0][r] & mw) != sw:
   bad += 1
 if W[0][16] != TARGET_W16 or W[0][17] != TARGET_W17:
  bad += 1
 out0,out1 = sha256_r39_compress(cv,W[0][:16]),sha256_r39_compress(cv,W[1][:16])
 if out0 != out1 or W[0][:16] == W[1][:16]:
  bad += 1
 assert bad == 0
 return struct.pack(">8I16I",*(cv + W[0][:16])),struct.pack(">8I16I",*(cv + W[1][:16])),bad

def run_claw_vow_experiment(req):
 ops_f,in_f,out_f = build_traced_step(fold_maj=True,include_dp=False)
 alloc_f,phys_in_f,phys_out_f,peak_f = allocate(ops_f,in_f,out_f)
 ops_s1,in_s1,out_s1,dp_s1 = build_traced_step(fold_maj=True,include_dp=True)
 alloc_s1,phys_in_s1,phys_out_s1,phys_dp_s1,peak_s1 = allocate(ops_s1,in_s1,out_s1,dp_s1)
 assert peak_f == 14 and peak_s1 == 14 and len(ops_f) == 67 and len(ops_s1) == 71

 vow_cvs = {c_idx: (cv_c,init_walk_params(cv_c)) for c_idx in range(4) for cv_c,_ in (derive_cv(0x20260329 + c_idx * 0x100000 + 7 * 0x10000),)}
 u_tab = {((((u_odd >> 7) | (u_odd << 25)) ^ ((u_odd >> 18) | (u_odd << 14)) ^ (u_odd >> 3)) - u_odd) & MASK32: u_odd for u_odd in range(1,524288,2)}
 u_get = u_tab.get

 exp_id = req.get("experiment_id","r39-claw-vow")
 tot_bad = tot_live_raw = tot_live_distinct = tot_live_f8 = tot_live_f9 = tot_live_w17_low4 = tot_full32_claws = tot_bijection_verified = 0
 shared_packed_dp_table = [0] * 256
 cv_distinct_counts,out = [],[]
 for tr in req["trials"]:
  t = int(tr["trial"])
  rec = dict(trial=t,message_a_hex=None,message_b_hex=None)
  if t > GATE_TRIAL:
   out.append(rec)
   continue

  stream = hashlib.shake_256((exp_id + "|" + tr["seed"]).encode()).digest(64 + 16 * LANES * 4 + 64 * 8)
  m0_words = list(struct.unpack(">16I",stream[:64]))
  cv = list(sha256_r39_compress(SHA256_IV,m0_words))
  wp = init_walk_params(cv)

  if t == GATE_TRIAL:
   f8_active,f9_active,inv_bad = enumerate_active_f8_f9()
   gate_bad = inv_bad + (1 if (len(f8_active) != 1152 or len(f9_active) != 2080) else 0)
   c2_base = [row for row in VOW_F89_TRAILS if row[0] == 2]
   c2_trails = c2_base[:6] + c2_base[:1]
   _,wp_c2 = vow_cvs[2]
   found_7,_ = recover_7pairs_packed([(r_i[1],r_i[3],r_i[2],r_i[4]) for r_i in c2_trails],wp_c2,alloc_f,phys_in_f,phys_out_f)
   if any(found_7[i] != (c2_trails[i][6],c2_trails[i][7]) for i in range(7)):
    gate_bad += 1
   mean_c = sum(cv_distinct_counts) / float(len(cv_distinct_counts)) if cv_distinct_counts else 0.0
   var_c = sum((c - mean_c) ** 2 for c in cv_distinct_counts) / float(len(cv_distinct_counts) - 1) if len(cv_distinct_counts) > 1 else 999.0
   disp_ratio = var_c / mean_c if mean_c > 0 else 999.0
   f8_rate = tot_live_f8 / float(tot_live_distinct) if tot_live_distinct > 0 else 0.0
   f9_rate = tot_live_f9 / float(tot_live_distinct) if tot_live_distinct > 0 else 0.0
   w17_rate = tot_live_w17_low4 / float(tot_live_distinct) if tot_live_distinct > 0 else 0.0
   dedup_ratio = tot_live_distinct / float(tot_live_raw) if tot_live_raw > 0 else 0.0
   gates_ok = (
    tot_bad == 0 and gate_bad == 0 and len(cv_distinct_counts) == ACTIVE_TRIALS and tot_live_distinct >= 380
    and 0.80 <= dedup_ratio <= 0.96 and tot_full32_claws >= 8 and tot_bijection_verified == (ACTIVE_TRIALS + tot_full32_claws)
    and 0.025 <= f8_rate <= 0.120 and 0.002 <= f9_rate <= 0.040 and 0.025 <= w17_rate <= 0.115 and disp_ratio <= 2.2
   )
   if gates_ok:
    _,_,W_gate = build_variant(cv,m0_words[0] & 0xFFFFFFFE,m0_words[1])
    rec["message_a_hex"] = struct.pack(">32I",*(m0_words + W_gate[0][:16])).hex()
    rec["message_b_hex"] = struct.pack(">32I",*(m0_words + W_gate[1][:16])).hex()
   rec["observations"] = dict(
    gate_trial=1,exhaustive_f8_active=len(f8_active),exhaustive_f9_active=len(f9_active),
    pooled_live_raw_claws=tot_live_raw,pooled_live_distinct_claws=tot_live_distinct,
    pooled_full32_claws=tot_full32_claws,pooled_bijection_verified=tot_bijection_verified,
    pooled_f8_hits=tot_live_f8,pooled_f9_hits=tot_live_f9,pooled_w17_low4_hits=tot_live_w17_low4,
    inter_cv_disp_ratio=round(disp_ratio,4),gates_ok=int(gates_ok),mismatches=tot_bad + gate_bad + (0 if gates_ok else 1),
   )
   out.append(rec)
   continue

  bad,off,lanes_checked,stage1_dp_hits = 0,64,0,0
  for _ in range(16):
   lanes_in = list(struct.unpack(">7I",stream[off : off + 28]))
   off += 28
   out_packed,dp_word = run_allocated(alloc_s1,phys_in_s1,phys_out_s1,pack_lanes(lanes_in),wp,dp_phys=phys_dp_s1)
   packed_out = unpack_lanes(out_packed)
   mask_ref,mask_swar = stage1_dp_mask(out_packed,7),swar_dp_word_to_mask(dp_word)
   if mask_swar != mask_ref or ((dp_word != 0) != (mask_ref != 0)):
    bad += 1
   for l in range(LANES):
    x = lanes_in[l]
    y_scalar = F_step(x,wp)
    if packed_out[l] != y_scalar:
     bad += 1
    if (mask_swar >> l) & 1:
     stage1_dp_hits += 1
    if (x & 1) == 0:
     a0,e0,w0 = x,(x + wp["e0_base"]) & MASK32,(x + wp["k0"]) & MASK32
     t1_0 = (cv[7] + S1(cv[4]) + CH(cv[4],cv[5],cv[6]) + K39[0] + w0) & MASK32
     if ((t1_0 + S0(cv[0]) + MAJ(cv[0],cv[1],cv[2])) & MASK32) != a0 or ((cv[3] + t1_0) & MASK32) != e0:
      bad += 1
    elif ((y_scalar + x) & MASK32) != s0(x):
     bad += 1
    lanes_checked += 1

  seed_vow = int.from_bytes(stream[:8],"big")
  live_raw,live_distinct,live_dp_hits,live_val_matches = run_live_reduced_vow(wp,seed_vow,table=shared_packed_dp_table,gen_id=t + 1)
  ref_raw,ref_distinct,ref_dp_hits,ref_val_matches = run_live_reduced_vow(wp,seed_vow,table=None,gen_id=1)
  if live_raw != ref_raw or live_distinct != ref_distinct or live_dp_hits != ref_dp_hits or live_val_matches != ref_val_matches:
   bad += 1
  f8_hits_t = f9_hits_t = w17_low4_t = 0
  for idx_c,(a0_c,u_c) in enumerate(sorted(live_distinct)):
   a1_c,_,w8_c,w9_c,w17_c = closed_form_w8_w9_w17(cv,a0_c,u_c,wp)
   if (a0_c & 1) != 0 or (u_c & 1) != 1 or w9_even_a0_bit(w9_c) != (w8_c & 1):
    bad += 1
   if idx_c == 0:
    A_chk,E_chk,W_chk = build_variant(cv,a0_c,a1_c)
    for r_step in range(24):
     step_pair(A_chk,E_chk,W_chk,r_step)
    w17_ref = (W_chk[0][17] - W_chk[0][1] + u_c) & MASK32
    cv_inv,a0_inv,a1_inv,w1_inv = invert_rollout_to_sfs(A_chk,E_chk,W_chk)
    if W_chk[0][8] != w8_c or W_chk[0][9] != w9_c or w17_ref != w17_c or cv_inv != list(cv) or a0_inv != a0_c or a1_inv != a1_c or w1_inv != W_chk[0][1]:
     bad += 1
    else:
     tot_bijection_verified += 1
   if in_F8(w8_c):
    f8_hits_t += 1
   if in_F9(w9_c):
    f9_hits_t += 1
   if (w17_c & 0xF) == (TARGET_W17 & 0xF):
    w17_low4_t += 1

  tot_live_raw += len(live_raw)
  tot_live_distinct += len(live_distinct)
  tot_live_f8 += f8_hits_t
  tot_live_f9 += f9_hits_t
  tot_live_w17_low4 += w17_low4_t
  cv_distinct_counts.append(len(live_distinct))

  c_walk,e0_base,c0_xor_c1,c0_and_c1 = wp["c_walk"],wp["e0_base"],wp["c0_xor_c1"],wp["c0_and_c1"]
  c4,c5 = cv[4],cv[5]
  c4_xor_c5,st_32,full32_t,last_full32 = c4 ^ c5,seed_vow,0,None
  for _ in range(24576):
   st_32 = (st_32 + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
   a0_e = st_32 & 0xFFFFFFFE
   s0_a = (((a0_e >> 2) | (a0_e << 30)) ^ ((a0_e >> 13) | (a0_e << 19)) ^ ((a0_e >> 22) | (a0_e << 10))) & MASK32
   maj_a,e0 = (a0_e & c0_xor_c1) ^ c0_and_c1,(a0_e + e0_base) & MASK32
   s1_e = (((e0 >> 6) | (e0 << 26)) ^ ((e0 >> 11) | (e0 << 21)) ^ ((e0 >> 25) | (e0 << 7))) & MASK32
   ch_e = ((e0 & c4_xor_c5) ^ c5) & MASK32
   u_hit = u_get((c_walk + s0_a + maj_a + s1_e + ch_e - a0_e) & MASK32)
   if u_hit is not None:
    full32_t += 1
    last_full32 = (a0_e,u_hit)
    a1_hit = recover_a1(a0_e,u_hit,wp)
    A_h,E_h,W_h = build_variant(cv,a0_e,a1_hit)
    for rs in range(24):
     step_pair(A_h,E_h,W_h,rs)
    cv_h,a0_h,a1_h,w1_h = invert_rollout_to_sfs(A_h,E_h,W_h)
    if F_step(a0_e,wp) != F_step(u_hit,wp) or (a0_e & 1) != 0 or (u_hit & 1) != 1 or W_h[0][16] != TARGET_W16 or W_h[0][1] != u_hit or cv_h != list(cv) or a0_h != a0_e or a1_h != a1_hit or w1_h != u_hit or w9_even_a0_bit(W_h[0][9]) != (W_h[0][8] & 1):
     bad += 1
    else:
     tot_bijection_verified += 1
  tot_full32_claws += full32_t

  c_idx,sa,la,sb,lb,dp_exp,a0_exp,u_exp = VOW_F89_TRAILS[t]
  cv_vow,wp_vow = vow_cvs[c_idx]
  xa,xb = sa,sb
  for step_i in range(la):
   xa = F_step(xa,wp_vow)
   if step_i + 1 < la and (xa & 0x7F) == 0:
    bad += 1
  for step_i in range(lb):
   xb = F_step(xb,wp_vow)
   if step_i + 1 < lb and (xb & 0x7F) == 0:
    bad += 1
  if xa != dp_exp or xb != dp_exp or (dp_exp & 0x7F) != 0 or la == lb:
   bad += 1

  found_1pair,rec_batches_vow = recover_1pair_simd7(sa,sb,la,lb,wp_vow,alloc_f,phys_in_f,phys_out_f)
  if found_1pair != (a0_exp,u_exp):
   bad += 1
  a1_vow,_,w8_vow,w9_vow,w17_vow = closed_form_w8_w9_w17(cv_vow,a0_exp,u_exp,wp_vow)
  A_v,E_v,W_v = build_variant(cv_vow,a0_exp,a1_vow)
  for r_step in range(18):
   step_pair(A_v,E_v,W_v,r_step)
  if F_step(a0_exp,wp_vow) != F_step(u_exp,wp_vow) or (a0_exp & 1) != 0 or (u_exp & 1) != 1 or W_v[0][1] != u_exp or W_v[0][16] != TARGET_W16 or W_v[0][17] != w17_vow or not (in_F8(w8_vow) and in_F9(w9_vow)) or w9_even_a0_bit(w9_vow) != (w8_vow & 1):
   bad += 1

  if len(live_distinct) < 15:
   bad += 1
  tot_bad += bad

  if bad == 0:
   a0_var,u_var = last_full32 if last_full32 is not None else sorted(live_distinct)[0]
   a1_var = recover_a1(a0_var,u_var,wp)
   _,_,W_var = build_variant(cv,a0_var,a1_var)
   rec["message_a_hex"] = struct.pack(">32I",*(m0_words + W_var[0][:16])).hex()
   rec["message_b_hex"] = struct.pack(">32I",*(m0_words + W_var[1][:16])).hex()

  rec["observations"] = dict(
   lanes_checked=lanes_checked,step_ops_folded=len(ops_f),stage1_traced_ops=len(ops_s1),
   peak_live_regs=max(peak_f,peak_s1),stage1_dp_hits=stage1_dp_hits,live_vow_dp_hits=live_dp_hits,
   live_vow_raw_claws=len(live_raw),live_vow_distinct_claws=len(live_distinct),live_vow_f8_hits=f8_hits_t,
   live_vow_f9_hits=f9_hits_t,live_vow_w17_low4_hits=w17_low4_t,live_full32_claws=full32_t,
   vow_rec_batches_simd7=rec_batches_vow,mismatches=bad,
  )
  out.append(rec)
 return dict(schema_version=1,trials=out)

def run_tail_sfs_experiment(req):
 A = [list(BASE_A0) + [0] * 23,list(BASE_A1) + [0] * 23]
 E = [list(BASE_E0) + [0] * 23,list(BASE_E1) + [0] * 23]
 W = [list(BASE_W0) + [0] * 23,list(BASE_W1) + [0] * 23]
 g16 = solve_row_exact(A,E,W,16)
 assert g16 == [0xBCA1C121,0xBCA1C321]
 s16 = set_row_state(A,E,W,16,TARGET_W16)
 g17 = solve_row_exact(*s16,17)
 assert g17 == [TARGET_W17]
 s17 = set_row_state(*s16,17,TARGET_W17)
 g18 = solve_row_exact(*s17,18)
 w18_valid = [s for w18 in g18 for s in (set_row_state(*s17,18,w18),) if ((s[1][0][22] >> 16) & 1) == 0]
 assert len(g18) == 16384 and len(w18_valid) == 12288

 subs = build_row_subspaces()
 assert len(subs[(20,0)]) == 4 and len(subs[(20,1)]) == 4
 sub_frac = {rw: sum(1 << len(bas) for _,bas in subs[rw]) / (2.0 ** 32) for rw in (19,20,21,22)}
 p18_exact = len(w18_valid) / (2.0 ** 32)
 f8_active,f9_active,inv_bad = enumerate_active_f8_f9()
 assert inv_bad == 0 and len(f8_active) == 1152 and len(f9_active) == 2080

 const26 = (s0(BASE_W1[11]) - s0(BASE_W0[11]) + BASE_W1[10] - BASE_W0[10]) & MASK32
 req_ds1_24 = (0x40000000 - const26) & MASK32
 req_mid = (req_ds1_24 >> 6) & 0x7F
 valid_hi = bytearray(65536)
 for hi in range(65536):
  w = hi << 16
  w1 = (w + T9) & MASK32
  if (w1 ^ w) in (0x03010000,0x0D010000) and ((((s1(w1) - s1(w)) >> 6) - req_mid) & 0x7F) in (0,1,0x7F):
   valid_hi[hi] = 1
 c17 = (TARGET_W17 - s1(BASE_W0[15]) - BASE_W0[10]) & MASK32
 assert (c17 & 1) == 1 and sum(valid_hi) == 2304

 exp_id = req.get("experiment_id","r39-tail-sfs")
 tot_bad = tot_live_inverted = tot_ds1_all = tot_ds1_odd = 0
 est_q_list,out = [],[]
 for tr in req["trials"]:
  t = int(tr["trial"])
  rec = dict(trial=t,message_a_hex=None,message_b_hex=None)
  if t > GATE_TRIAL:
   out.append(rec)
   continue

  if t == GATE_TRIAL:
   ref_cv_hex,ref_a0,ref_a1 = PAIR_CLAW_SFS[GATE_TRIAL]
   m1_0,m1_1,bad_ref = verify_claw_sfs_tuple(ref_cv_hex,ref_a0,ref_a1)
   mean_q = sum(est_q_list) / float(len(est_q_list)) if est_q_list else 0.0
   sd_q = ((sum((q - mean_q) ** 2 for q in est_q_list) / float(len(est_q_list) - 1)) ** 0.5 if len(est_q_list) > 1 else 999.0)
   log2_mean_q = math.log2(mean_q) if mean_q > 0 else -999.0
   lcb99_lin_q = mean_q - 2.602 * (sd_q / (len(est_q_list) ** 0.5)) if len(est_q_list) > 1 else 0.0
   lcb99_lin_log2_q = math.log2(lcb99_lin_q) if lcb99_lin_q > 0 else -999.0
   lqs = [math.log2(q) for q in est_q_list if q > 0]
   mean_log2_q = sum(lqs) / float(len(lqs)) if lqs else -999.0
   sd_log2_q = ((sum((x - mean_log2_q) ** 2 for x in lqs) / float(len(lqs) - 1)) ** 0.5 if len(lqs) > 1 else 999.0)
   lcb99_log2_q = mean_log2_q - 2.602 * (sd_log2_q / (len(lqs) ** 0.5)) if len(lqs) > 1 else -999.0
   ds1_u_odd_rate = tot_ds1_odd / float(tot_ds1_all) if tot_ds1_all > 0 else 0.0
   gates_ok = (
    tot_bad == 0 and bad_ref == 0 and len(est_q_list) == ACTIVE_TRIALS and len(lqs) == ACTIVE_TRIALS
    and tot_live_inverted >= 120 and 0.46 <= ds1_u_odd_rate <= 0.54
    and -76.0 <= log2_mean_q <= -74.5 and lcb99_log2_q >= -75.95 and lcb99_lin_log2_q >= -75.95
   )
   if gates_ok:
    rec["message_a_hex"] = m1_0.hex()
    rec["message_b_hex"] = m1_1.hex()
   rec["observations"] = dict(
    gate_trial=1,replicates=len(est_q_list),nonzero_replicates=len(lqs),
    total_live_inverted=tot_live_inverted,ds1_u_odd_rate=round(ds1_u_odd_rate,4),
    pooled_log2_mean_q=round(log2_mean_q,4),mean_log2_q=round(mean_log2_q,4),
    lcb99_log2_q=round(lcb99_log2_q,4),lcb99_lin_log2_q=round(lcb99_lin_log2_q,4),
    gates_ok=int(gates_ok),mismatches=tot_bad + bad_ref + (0 if gates_ok else 1),
   )
   out.append(rec)
   continue

  ref_cv_hex,ref_a0,ref_a1 = PAIR_CLAW_SFS[t]
  m1_0,m1_1,bad = verify_claw_sfs_tuple(ref_cv_hex,ref_a0,ref_a1)

  st = int.from_bytes(hashlib.shake_256((exp_id + "|" + tr["seed"]).encode()).digest(8),"big")
  F8_pool,F9_pool = [],[]
  for _ in range(512):
   v,st = splitmix64(st)
   F8_pool.append(f8_active[v % 1152] | ((v >> 16) & INACTIVE_MASK_F8))
   v2,st = splitmix64(st)
   F9_pool.append(f9_active[v2 % 2080] | ((v2 >> 16) & INACTIVE_MASK_F9))
  S0_F9_pool = [s0(w9) for w9 in F9_pool]
  W8bit_F9_pool = [w9_even_a0_bit(w9) for w9 in F9_pool]

  N_part,M_draws,T_roll = 192,384,1536
  target_rollouts = N_part * T_roll

  cur = []
  for _ in range(N_part):
   v,st = splitmix64(st)
   cur.append(w18_valid[v % len(w18_valid)])
  p_prod = p18_exact

  for rw in (19,20,21,22):
   idx = rw + 4
   nxt_pool = []
   for d_i in range(M_draws):
    As,Es,Ws = cur[d_i % len(cur)]
    t1_0 = (Es[0][idx - 4] + S1(Es[0][idx - 1]) + CH(Es[0][idx - 1],Es[0][idx - 2],Es[0][idx - 3]) + K39[rw]) & MASK32
    ce0 = (As[0][idx - 4] + t1_0) & MASK32
    v,st = splitmix64(st)
    r_subs = subs[(20,((Es[0][23] >> 24) & 3) - ((Es[0][22] >> 24) & 3))] if rw == 20 else subs[rw]
    x0,bas = r_subs[v % len(r_subs)]
    ex0,rnd = x0,v >> 4
    for bvec in bas:
     if rnd & 1:
      ex0 ^= bvec
     rnd >>= 1
    if rw == 19 and (((ex0 >> 24) & 3) - ((Es[0][22] >> 24) & 3)) not in (0,1):
     continue
    if rw == 21 and ((ex0 ^ Es[0][24]) & 0x40000000) != 0:
     continue
    s_nxt = set_row_state(As,Es,Ws,rw,(ex0 - ce0) & MASK32)
    if lookahead_ok(*s_nxt,rw):
     nxt_pool.append(s_nxt)
   p_prod *= sub_frac[rw] * (len(nxt_pool) / float(M_draws))
   if nxt_pool:
    for i_sh in range(len(nxt_pool) - 1,0,-1):
     vs,st = splitmix64(st)
     j_sh = vs % (i_sh + 1)
     nxt_pool[i_sh],nxt_pool[j_sh] = nxt_pool[j_sh],nxt_pool[i_sh]
    cur = nxt_pool

  particles = []
  for p_i in range(N_part):
   As,Es,Ws = cur[p_i % len(cur)]
   idx = 27
   t1_0 = (Es[0][idx - 4] + S1(Es[0][idx - 1]) + CH(Es[0][idx - 1],Es[0][idx - 2],Es[0][idx - 3]) + K39[23]) & MASK32
   ce0 = (As[0][idx - 4] + t1_0) & MASK32
   v,st = splitmix64(st)
   ex0 = (v & MASK32) & ~(1 << 30)
   s23 = set_row_state(As,Es,Ws,23,(ex0 - ce0) & MASK32)
   w0_p = s23[2][0]
   base_w24 = (s1(w0_p[22]) + w0_p[17]) & MASK32
   ck_p = tuple((w0_p[k + 16] - s1(w0_p[k + 14]) - w0_p[k + 9]) & MASK32 for k in range(7,0,-1))
   particles.append((s23[0],s23[1],s23[2],base_w24,ck_p))
  p_prod *= 0.5
  Ap,Ep,Wp,_,ck_0 = particles[0]
  Ap,Ep,Wp = [list(Ap[0]),list(Ap[1])],[list(Ep[0]),list(Ep[1])],[list(Wp[0]),list(Wp[1])]
  w8_p0 = (F8_pool[0] & ~1) | W8bit_F9_pool[0]
  Wp[0][8],Wp[1][8] = w8_p0,(w8_p0 + D8) & MASK32
  Wp[0][9],Wp[1][9] = F9_pool[0],(F9_pool[0] + D9) & MASK32
  wk_0 = w8_p0
  for c_val in ck_0[:-1]:
   wk_0 = (c_val - s0(wk_0)) & MASK32
  u_p0 = (ck_0[-1] - s0(wk_0)) & MASK32
  u_flip = (ck_0[-1] - s0(wk_0 ^ (1 << 18))) & MASK32
  cv_p,a0_p,a1_p,u_inv0 = invert_rollout_to_sfs(Ap,Ep,Wp)
  Af,Ef,Wf = build_variant(cv_p,a0_p,a1_p)
  for rs in range(16,24):
   step_pair(Af,Ef,Wf,rs)
  if (a0_p & 1) != 0 or u_p0 != u_inv0 or u_p0 != Wf[0][1] or ((u_flip & 1) ^ (u_p0 & 1)) != 1 or Af[0][6:28] != Ap[0][6:28] or Af[1][6:28] != Ap[1][6:28] or Ef[0][10:28] != Ep[0][10:28] or Ef[1][10:28] != Ep[1][10:28] or Wf[0][8:24] != Wp[0][8:24] or Wf[1][8:24] != Wp[1][8:24] or invert_rollout_to_sfs(Af,Ef,Wf) != (cv_p,a0_p,a1_p,Wf[0][1]):
   bad += 1

  smc_hits = 0
  for As,Es,Ws,base_w24,ck_p in particles:
   for _ in range(T_roll):
    st = (st + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = ((st ^ (st >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    v = z ^ (z >> 31)
    i9 = (v >> 9) & 511
    w8 = (F8_pool[v & 511] & ~1) | W8bit_F9_pool[i9]
    w24_0 = (base_w24 + S0_F9_pool[i9] + w8) & MASK32
    if not valid_hi[w24_0 >> 16] or ((s1((w24_0 + T9) & MASK32) - s1(w24_0)) & MASK32) != req_ds1_24:
     continue
    tot_ds1_all += 1
    wk_r = w8
    for c_val in ck_p:
     wk_r = (c_val - s0(wk_r)) & MASK32
    u_r = wk_r
    if (u_r & 1) == 0:
     continue
    tot_ds1_odd += 1
    w9 = F9_pool[i9]
    A_r,E_r,W_r = [list(As[0]),list(As[1])],[list(Es[0]),list(Es[1])],[list(Ws[0]),list(Ws[1])]
    W_r[0][8],W_r[1][8] = w8,(w8 + D8) & MASK32
    W_r[0][9],W_r[1][9] = w9,(w9 + D9) & MASK32
    for r_step in range(24,39):
     step_pair(A_r,E_r,W_r,r_step)
    if A_r[0][39:43] == A_r[1][39:43] and E_r[0][39:43] == E_r[1][39:43]:
     smc_hits += 1
     cv_live,a0_live,a1_live,u_live = invert_rollout_to_sfs(A_r,E_r,W_r)
     _,_,W_inv = build_variant(cv_live,a0_live,a1_live)
     out0,out1 = sha256_r39_compress(cv_live,W_inv[0][:16]),sha256_r39_compress(cv_live,W_inv[1][:16])
     if out0 != out1 or W_inv[0][:16] == W_inv[1][:16] or (a0_live & 1) != 0 or (u_live & 1) != 1 or u_live != u_r or not (in_F8(w8) and in_F9(w9)):
      bad += 1
     else:
      tot_live_inverted += 1

  q_est = 2.0 * p_prod * (smc_hits / float(target_rollouts))
  est_q_list.append(q_est)
  tot_bad += bad

  if bad == 0:
   rec["message_a_hex"] = m1_0.hex()
   rec["message_b_hex"] = m1_1.hex()
  rec["observations"] = dict(
   row16_exact_count=len(g16),row17_exact_count=len(g17),row18_valid_count=len(w18_valid),
   smc_particles=N_part,smc_rollouts=target_rollouts,smc_hits=smc_hits,
   log2_q_est=round(math.log2(q_est),4) if q_est > 0 else 0.0,
   claw_verified=int(bad == 0),sfs_collision_verified=int(bad == 0),mismatches=bad,
  )
  out.append(rec)
 return dict(schema_version=1,trials=out)

def run_request(req):
 exp_id = req.get("experiment_id","r39-tail-sfs")
 if exp_id == "r39-claw-vow":
  return run_claw_vow_experiment(req)
 return run_tail_sfs_experiment(req)

def selftest():
 led = ledger()
 assert led["machine_model"]["step_ops_folded"] == 67 and led["machine_model"]["step_ops_unfolded"] == 71
 assert led["machine_model"]["stage1_traced_ops_folded"] == 71 and led["machine_model"]["stage1_traced_ops_unfolded"] == 75
 assert led["machine_model"]["peak_live_regs"] == 14 and led["machine_model"]["spill_ops_64"] == 0
 assert led["memory_breakdown"]["total_resident_bytes"] < (1 << 20)
 for cv_hex,a0,a1 in PAIR_CLAW_SFS:
  m0,m1,bad = verify_claw_sfs_tuple(cv_hex,a0,a1)
  assert bad == 0 and len(m0) == 96 and len(m1) == 96 and m0 != m1
 sm = b'{"domain":"hashsmash-experiments-v1","holdout_nonce":null,"seed":"hashsmash-public-seed-v1","target_config_sha256":"76b4a93ecdbedd7590adb35005834807e1769475c675e4e0ed5af8c0e955419e"}'
 for exp_id in ("r39-claw-vow","r39-tail-sfs"):
  t_req = [dict(trial=i,seed=hashlib.sha256(sm + f'["{exp_id}",{i}]'.encode()).hexdigest()) for i in range(256)]
  res = run_request(dict(schema_version=1,experiment_id=exp_id,trials=t_req))
  assert len(res["trials"]) == 256 and sum(r["message_a_hex"] is not None for r in res["trials"]) == RETURNED_TRIALS
  assert len({r["message_a_hex"] for r in res["trials"][:RETURNED_TRIALS]}) == RETURNED_TRIALS
  assert all(r["observations"]["mismatches"] == 0 for r in res["trials"][:RETURNED_TRIALS])
 print("SELFTEST OK: 67/71-op packed kernels, exhaustive F8/F9 active-bit proof, 16-CV live vOW + full32 claw search, and 16-trial fixed-budget SMC + SFS gate verified.")

def main():
 if "--selftest" in sys.argv or "selftest" in sys.argv:
  selftest()
  return
 if "--ledger" in sys.argv or "ledger" in sys.argv:
  print(json.dumps(ledger(), indent=2))
  return

 req = json.loads(sys.stdin.read())
 sys.stdout.write(json.dumps(run_request(req),separators=(",",":")))

if __name__ == "__main__":
 main()
