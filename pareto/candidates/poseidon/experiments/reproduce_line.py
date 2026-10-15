"""Organizer-executed reproduction of the r = 3 two-round-skip line map.

Deterministic, standard library only. From the deployed Orchard (halo2_poseidon
0.2.0) MDS and the round-0 and round-1 constants it re-derives the line
(a0, a1) + lambda (b0, b1) described in proof.md, checks the identities that
make the round-0 and round-1 S-boxes drop out (D_2 = 0, C_0 = C_1 = 0), checks
the leading-coefficient degree recurrence through the nine remaining nonlinear
layers, and maps the two gcd roots X = r and X = 1 reported in proof.md to
messages. The organizer host recomputes the r = 3 digests of the returned pair.
The same pair is returned for every trial because the procedure reads no
randomness; the seeds are ignored on purpose.
"""
import json
import sys

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
MDS = [
    [0xab5e5b874a68de7b3d59fbdc8c9ead497d7a0ab23850b56323f2486d7e11b63, 0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e, 0x7c045d5f5e9e5a6d803952bbb364fdfa0a3b71a5fb1573519d1cf25d8e8345d],
    [0x233162630ebf9ed7f8e24f66822c2d9f3a0a464048bd770ad049cdc8d085167c, 0x25cae2599892a8b0b36664548d60957d78f8365c85bbab07402270113e047a2e, 0x22f5b5e1e6081c9774938717989a19579aad3d8262efd83ff84d806f685f747a],
    [0x2e29dd59c64b1037f333aa91c383346421680eabc56bc15dfee7a9944f84dbe4, 0x1d1aab4ec1cd678892d15e7dceef1665cbeaf48b3a0624c3c771effa43263664, 0x3bf763086a18936451e0cbead65516b975872c39b59a31f615639415f6e85ef1],
]
RC = [
    [0x360d7470611e473d353f628f76d110f34e71162f31003b7057538c2596426303, 0x2bab94d7ae222d135dc3c6c5febfaa314908ac2f12ebe06fbdb74213bf63188b, 0x150c93fef652fb1c2bf03e1a29aa871fef77e7d736766c5d0939d92753cc5dc8],
    [0x3270661e68928b3a955d55db56dc57c103cc0a60141e894e14259dce537782b2, 0x73f116f04122e25a0b7afe4e2057299b407c370f2b5a1ccce9fb9ffc345afb3, 0x2a32ec5c4ee5b1837affd09c1f53f5fd55c9cd2061ae93ca8ebad76fc71554d8],
]
ROOT_R = 13768782537159585682094643193913549826095386322623631211636205761512609213242
ROOT_S = 1
FULL_AFTER_SKIP = [True, True, False, False, False, True, True, True, True]  # rounds 2,3,4,5,6,60,61,62,63


def inv(x):
    return pow(x, P - 2, P)


def fifth_root(x):
    return pow(x, pow(5, -1, P - 1), P)


def line():
    K = pow((1 << 65) + RC[0][2], 5, P)
    b0, b1 = MDS[2][1], (-MDS[2][0]) % P
    r0 = (-RC[1][0] - K * MDS[0][2]) % P
    r1 = (-RC[1][1] - K * MDS[1][2]) % P
    det = (MDS[0][0] * MDS[1][1] - MDS[0][1] * MDS[1][0]) % P
    assert det != 0
    a0 = (r0 * MDS[1][1] - r1 * MDS[0][1]) * inv(det) % P
    a1 = (MDS[0][0] * r1 - MDS[1][0] * r0) * inv(det) % P
    D = [(b0 * MDS[i][0] + b1 * MDS[i][1]) % P for i in range(3)]
    Cc = [(a0 * MDS[i][0] + a1 * MDS[i][1] + K * MDS[i][2] + RC[1][i]) % P for i in range(3)]
    assert b0 != 0 and b1 != 0
    assert D[2] == 0 and Cc[0] == 0 and Cc[1] == 0 and D[0] != 0 and D[1] != 0
    return a0, a1, b0, b1, D


def degree_check(D):
    L = [(pow(D[0], 5, P) * MDS[i][0] + pow(D[1], 5, P) * MDS[i][1]) % P for i in range(3)]
    for full in FULL_AFTER_SKIP:
        s = [pow(x, 5, P) for x in L] if full else [pow(L[0], 5, P), 0, 0]
        L = [sum(MDS[i][j] * s[j] for j in range(3)) % P for i in range(3)]
        assert all(x != 0 for x in L)
    return L[0]


def message(X, a0, a1, b0, b1):
    lam = fifth_root(X % P)
    s0 = (a0 + lam * b0) % P
    s1 = (a1 + lam * b1) % P
    nk = (fifth_root(s0) - RC[0][0]) % P
    rho = (fifth_root(s1) - RC[0][1]) % P
    return nk.to_bytes(32, "little") + rho.to_bytes(32, "little")


def main():
    request = json.loads(sys.stdin.read())
    a0, a1, b0, b1, D = line()
    lead = degree_check(D)
    assert lead == 22422092890086069301514433790408465908103586438175633615990032743912502134023
    ma = message(ROOT_R, a0, a1, b0, b1)
    mb = message(ROOT_S, a0, a1, b0, b1)
    assert ma != mb
    out = {"schema_version": 1, "trials": []}
    for t in request["trials"]:
        out["trials"].append({"trial": t["trial"], "message_a_hex": ma.hex(), "message_b_hex": mb.hex(),
                               "observations": {"line_identities_checked": 1, "degree_leading_nonzero_layers": 9}})
    sys.stdout.write(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
