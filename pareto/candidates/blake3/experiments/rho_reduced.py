"""Reduced-width Floyd rho for blake3-r3 (proof.md Section 3)."""
import json, sys
sys.path.insert(0, "../../..")
# Use inlined 3-round compress to avoid host path issues in executor
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

def compress(cv, words, counter, block_len, flags, rounds=3):
    v = list(cv) + list(IV[:4]) + [counter & MASK, counter >> 32, block_len, flags]
    m = list(words)
    for _ in range(rounds):
        g(v, 0, 4, 8, 12, m[0], m[1]); g(v, 1, 5, 9, 13, m[2], m[3])
        g(v, 2, 6, 10, 14, m[4], m[5]); g(v, 3, 7, 11, 15, m[6], m[7])
        g(v, 0, 5, 10, 15, m[8], m[9]); g(v, 1, 6, 11, 12, m[10], m[11])
        g(v, 2, 7, 8, 13, m[12], m[13]); g(v, 3, 4, 9, 14, m[14], m[15])
        m = [m[i] for i in PERM]
    return tuple(v[i] ^ v[i + 8] for i in range(8)) + tuple(v[i + 8] ^ cv[i] for i in range(8))

def blake3_r3(data):
    words = list(__import__('struct').unpack('<16I', data.ljust(64, b'\0')[:64]))
    out = compress(IV, words, 0, len(data), 1 | 2 | 8, 3)
    return b''.join(w.to_bytes(4, 'little') for w in out[:8])

def enc(x): return x.to_bytes(32, 'little')
def f(x): return int.from_bytes(blake3_r3(enc(x))[:2], 'little')

def rho(x0, cap):
    t, h, n = f(x0), f(f(x0)), 3
    while t != h:
        t, h = f(t), f(f(h)); n += 3
        if n > cap: return None, None, n
    t = x0
    while True:
        ft, fh = f(t), f(h); n += 2
        if ft == fh: break
        t, h = ft, fh
    if t == h: return None, None, n
    return enc(t).hex(), enc(h).hex(), n

def main():
    req = json.load(sys.stdin); out = []
    for tr in req['trials']:
        a, b, n = rho(int(tr['seed'], 16) & 0xFFFF, 5 * 2**16)
        out.append({'trial': tr['trial'], 'message_a_hex': a, 'message_b_hex': b,
                    'observations': {'evaluations': n}})
    print(json.dumps({'schema_version': 1, 'trials': out}, sort_keys=True))

if __name__ == '__main__':
    main()
