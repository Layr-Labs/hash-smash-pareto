#!/usr/bin/env python3
"""Head program (proof Sections 2.2 and 3): for one first block, solve head rows 0..J-1 of the characteristic for the
chaining value cv computed from the standard IV, with a hard stop. Stdlib only.
Organizer mode (stdin = {schema_version, experiment_id, trials}): per trial, M0 from the seed, cv = compress_R(IV, M0);
asserts that the embedded witness satisfies every condition of rows -4..J-1 (value-satisfiable head) and reports cv.
The solver itself (CaDiCaL) is not in the organizer executor, so organizer trials return no pair.
Solve mode (python head.py --solve CVHEX --gsk PATH/gsk.py --seed S): one counted call, killed at CAP_S wall seconds."""
import sys, json, hashlib, subprocess, time, os, tempfile
R, J, CAP_S = 40, 23, 10
CHAR = {'-4': ('--------------------------------', '--------------------------------', None), '-3': ('--------------------------------', '--------------------------------', None), '-2': ('--------------------------------', '--------------------------------', None), '-1': ('--------------------------------', '--------------------------------', None), '0': ('------------------------------nu', '-----------------------------nuu', '-----------------------------nuu'), '1': ('--n---nnn--nn-----unn--uu-----nu', '--u--n--u-n---------nuunu------u', '--------------------------------'), '2': ('-----n-nn---u---n-nun--n-uun-u-n', 'uun--------u--n--u--uu-uu--n-n-n', '--------------------------------'), '3': ('-u-n-u---uuu-nnu-ununn--u-u-u-un', '--nu-------n-n-nn--nuun----n----', '--------------------------------'), '4': ('n----n--nnnuununu-nu-n-nn--n-n--', '---nu--------uu---u-nnuu-u-u-n--', '--------------------------------'), '5': ('-n-nn-n----u-nn-u--uunun-u-nn--u', 'unnn-n-nn-u--unn-uun--uu--u-----', '--------------------------------'), '6': ('nnuu----nn--n---n----nun----un-n', '--un--u---uun-n--uun-n-nu-nn--u-', '--------------------------------'), '7': ('n--nu-u------n-u---nnunun-nuu-uu', '--n----n-----nun----nnn--uuu-u--', '--------------------------------'), '8': ('-u---u--unn----n-n-n-n---n---u-u', 'u--u--uun--nn--nuu-uunn--u-nnu--', '--------------------------------'), '9': ('---nnuuu--u-u-n-unu--un---n-u-nu', '---------n---n---u-n----uunu---n', '-------------------------------u'), '10': ('uun---nnu-u-u--n----n-nn-n--nun-', 'u--u-nnn-n-nnn-un--n-n--u-n----u', '-----nu----------u--------------'), '11': ('-unnnu------n-unn---nn-uu-n--u-u', 'u--uu---nnn----nnnu-n-n----u-un-', '------------------------------nu'), '12': ('nnnnnn-nuu-n----unun-n--un-un-un', 'n-uu-nuuunnn-nuu--n-n-un-nn--uu-', 'unuuu-----------n--------n-n---u'), '13': ('-nu-n----n--u--uu-nn-n--unu---n-', 'n-u--u-u-u--u---n-----n--uun-n-n', '----------unnnnnnnn-------------'), '14': ('nu-un-unn--------nnnu-uu-nn---n-', 'u-n-unu--nnnn--unu--u---nu--un--', '--------------------------------'), '15': ('u-nnnnun-n-un-u--uu--nnn-n-u--un', '--uu-uu--n-u---nn-unn-n-u-nnnn-u', '--------------------------------'), '16': ('-uu-uunu--un-u-nunu--u----------', 'nuunnnnn-u--nnu-nn--u--n--n-un-u', '--------------------------------'), '17': ('---u--nu--u---n-nn-nn---uun-n---', 'nu-un-u--nnu-uu---unuuunnnnnun-n', '------n-------unnn--------------'), '18': ('--u-nu----uun--un-nuuuuunn--un--', 'u-n--n-u--n---n---n-n-n--n-----u', '------------------------------nu'), '19': ('--u--un---unuuuun-uu-nun-uu----u', '---nu-nnun--n-unuuuu-u--n-uu-n--', '--------------------------------'), '20': ('--un-n----unn--n-----nu-nnuun--n', 'unun-unn--u----n-uu-u----n--n-uu', '--------------------------------'), '21': ('u--u-n---uun--n-------uu-nunn--n', '--u--nnu--uuu-n-u--u--u-u-nn--un', '--------------------------------'), '22': ('-u---nunu-u-nnnn-n----u---n---un', 'u-un---un----u--u---n--n-uu-unnn', '--------------------------------')}
WIT = {"cv": ["4236d4bf", "1abd814d", "b5d994f1", "1c387800", "a34ac447", "3e8b2a3e", "aaca8110", "6d185d12"], "m": ["fd783713", "37fa1eaf", "9c1d5c39", "9fc4bc9a", "3110cb41", "5cf121d6", "18ea6ab4", "3a8c03ba", "b70de428", "854e243f", "9baacbe0", "d37ef7a9", "bd9f4ba1", "142019a1", "a74c39d5", "4d981480"], "mp": ["fd783714", "37fa1eaf", "9c1d5c39", "9fc4bc9a", "3110cb41", "5cf121d6", "18ea6ab4", "3a8c03ba", "b70de428", "854e243e", "9daa8be0", "d37ef7aa", "459fcbf0", "141ff9a1", "a74c39d5", "4d981480"]}
M32 = 0xffffffff
IV = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
K = [int(x, 16) for x in '428a2f98 71374491 b5c0fbcf e9b5dba5 3956c25b 59f111f1 923f82a4 ab1c5ed5 d807aa98 12835b01 243185be 550c7dc3 '
     '72be5d74 80deb1fe 9bdc06a7 c19bf174 e49b69c1 efbe4786 0fc19dc6 240ca1cc 2de92c6f 4a7484aa 5cb0a9dc 76f988da 983e5152 a831c66d '
     'b00327c8 bf597fc7 c6e00bf3 d5a79147 06ca6351 14292967 27b70a85 2e1b2138 4d2c6dfc 53380d13 650a7354 766a0abb 81c2c92e 92722c85 '
     'a2bfe8a1 a81a664b c24b8b70 c76c51a3 d192e819 d6990624 f40e3585 106aa070 19a4c116 1e376c08 2748774c 34b0bcb5 391c0cb3 4ed8aa4a '
     '5b9cca4f 682e6ff3 748f82ee 78a5636f 84c87814 8cc70208 90befffa a4506ceb bef9a3f7 c67178f2'.split()]
rr = lambda x, n: ((x >> n) | (x << (32 - n))) & M32


def expand(m, n):
    w = list(m)
    for t in range(16, n):
        w.append((rr(w[t-2], 17) ^ rr(w[t-2], 19) ^ (w[t-2] >> 10)) + w[t-7] + (rr(w[t-15], 7) ^ rr(w[t-15], 18) ^ (w[t-15] >> 3)) + w[t-16] & M32)
    return w


def rows(cv, m, n):
    """A_i, E_i for i = -4..n-1 (rows -4..-1 = the chaining value) and the state after step n-1."""
    a, b, c, d, e, f, g, h = cv
    A, E = {-1: a, -2: b, -3: c, -4: d}, {-1: e, -2: f, -3: g, -4: h}
    w = expand(m, n)
    for t in range(n):
        t1 = (h + (rr(e, 6) ^ rr(e, 11) ^ rr(e, 25)) + ((e & f) ^ (~e & g)) + K[t] + w[t]) & M32
        t2 = ((rr(a, 2) ^ rr(a, 13) ^ rr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) & M32
        h, g, f, e, d, c, b, a = g, f, e, (d + t1) & M32, c, b, a, (t1 + t2) & M32
        A[t], E[t] = a, e
    return A, E, w, [a, b, c, d, e, f, g, h]


def compress(cv, m, n):
    return [(x + y) & M32 for x, y in zip(cv, rows(cv, m, n)[3])]


OK = {'?': lambda x, y: True, '-': lambda x, y: x == y, 'x': lambda x, y: x != y, 'u': lambda x, y: x == 1 and y == 0,
      'n': lambda x, y: x == 0 and y == 1, '0': lambda x, y: x == 0 and y == 0, '1': lambda x, y: x == 1 and y == 1}


def violations(cv, m1, m2):
    A1, E1, W1, _ = rows(cv, m1, J); A2, E2, W2, _ = rows(cv, m2, J); bad = 0
    for i, (sa, se, sw) in CHAR.items():
        i = int(i)
        for s, x, y in ((sa, A1[i], A2[i]), (se, E1[i], E2[i])) + (((sw, W1[i], W2[i]),) if i >= 0 else ()):
            bad += sum(1 for k in range(32) if not OK[s[31 - k]]((x >> k) & 1, (y >> k) & 1))
    return bad


def solve(cv, gsk, seed, xml):
    """One counted head call: the game kit's encoder + CaDiCaL on rows 0..J-1 with cv pinned; wall hard stop CAP_S."""
    t0 = time.time()
    cmd = [sys.executable, gsk, 'trail', xml, '--depth', str(J - 1), '--iv', ','.join('%08x' % x for x in cv),
           '--cap', str(max(1, CAP_S - 1)), '--first', '--seed', str(seed), '--out', tempfile.mkdtemp()]
    try:
        r = json.loads(subprocess.run(cmd, capture_output=True, text=True, timeout=CAP_S).stdout.strip().splitlines()[-1])
    except (subprocess.TimeoutExpired, ValueError, IndexError):
        r = {'status': 'HALTED'}
    p = r.get('pair')
    if r.get('status') == 'SAT' and p:
        m1, m2 = [int(x, 16) for x in p['M1']], [int(x, 16) for x in p['M2']]
        if m1 != m2 and violations(cv, m1, m2) == 0:
            return m1, m2, time.time() - t0
    return None, None, time.time() - t0


def main():
    wcv, wm, wmp = ([int(x, 16) for x in WIT[k]] for k in ('cv', 'm', 'mp'))
    assert wm != wmp and violations(wcv, wm, wmp) == 0, 'witness leaves rows -4..J-1'
    if '--solve' in sys.argv:
        g = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
        cv = [int(x, 16) for x in g('--solve').split(',')]
        xml = g('--xml', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'char.xml'))
        m1, m2, s = solve(cv, g('--gsk'), int(g('--seed', '1')), xml)
        print(json.dumps({'cv': g('--solve'), 'head_found': m1 is not None, 'wall_s': round(s, 3), 'cap_s': CAP_S,
                          'M1': ['%08x' % x for x in m1] if m1 else None, 'M2': ['%08x' % x for x in m2] if m2 else None}))
        return
    req = json.load(sys.stdin); out = []
    for t in req['trials']:
        sd = hashlib.sha256(('%s|%s' % (req.get('experiment_id', ''), t['seed'])).encode()).digest()
        m0 = [int.from_bytes(hashlib.sha256(sd + bytes([i])).digest()[:4], 'big') for i in range(16)]
        cv = compress(IV, m0, R)
        out.append({'trial': t['trial'], 'message_a_hex': None, 'message_b_hex': None,
                    'observations': {'cv': ''.join('%08x' % x for x in cv), 'witness_head_rows': J, 'witness_violations': 0,
                                     'head_found': False, 'hard_stop_s': CAP_S}})
    print(json.dumps({'schema_version': 1, 'trials': out}, separators=(',', ':')))


if __name__ == '__main__':
    main()
