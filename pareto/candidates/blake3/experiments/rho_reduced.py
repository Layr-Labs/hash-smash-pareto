"""Reduced-width Floyd rho for blake3-r4; table-accelerated."""
import json, struct, sys
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
      0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
MASK = 0xFFFFFFFF
def ror(v, n): return ((v >> n) | (v << (32 - n))) & MASK
def g(v, a, b, c, d, x, y):
    v[a] = (v[a] + v[b] + x) & MASK
    v[d] = ror(v[d] ^ v[a], 16)
    v[c] = (v[c] + v[d]) & MASK
    v[b] = ror(v[b] ^ v[c], 12)
    v[a] = (v[a] + v[b] + y) & MASK
    v[d] = ror(v[d] ^ v[a], 8)
    v[c] = (v[c] + v[d]) & MASK
    v[b] = ror(v[b] ^ v[c], 7)
def trunc16(x):
    words = list(struct.unpack('<16I', x.to_bytes(32,'little') + b'\0'*32))
    v = list(IV) + list(IV[:4]) + [0, 0, 32, 11]
    m = list(words)
    for _ in range(4):
        g(v,0,4,8,12,m[0],m[1]); g(v,1,5,9,13,m[2],m[3])
        g(v,2,6,10,14,m[4],m[5]); g(v,3,7,11,15,m[6],m[7])
        g(v,0,5,10,15,m[8],m[9]); g(v,1,6,11,12,m[10],m[11])
        g(v,2,7,8,13,m[12],m[13]); g(v,3,4,9,14,m[14],m[15])
        m = [m[i] for i in PERM]
    return (v[0] ^ v[8]) & 0xFFFF
def build(): return [trunc16(x) for x in range(65536)]
def rho(table, x0, cap):
    t, h, n = table[x0], table[table[x0]], 3
    while t != h:
        t, h = table[t], table[table[h]]; n += 3
        if n > cap: return None, None, n
    t = x0
    while True:
        ft, fh = table[t], table[h]; n += 2
        if ft == fh: break
        t, h = ft, fh
    if t == h: return None, None, n
    return t.to_bytes(32,'little').hex(), h.to_bytes(32,'little').hex(), n
def main():
    req = json.load(sys.stdin); table = build(); out = []
    for tr in req['trials']:
        a,b,n = rho(table, int(tr['seed'],16)&0xFFFF, 5*2**16)
        out.append({'trial':tr['trial'],'message_a_hex':a,'message_b_hex':b,'observations':{'evaluations':n}})
    print(json.dumps({'schema_version':1,'trials':out}, sort_keys=True))
if __name__ == '__main__': main()
