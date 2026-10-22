"""LS1: distinguished-point collision search on sha3-256-r11-prefix-v1 with a linear-structure message embedding.

Chain function on 256-bit points u (little-endian lanes u0..u3):
  m(u) = 128 bytes = lanes 0..15 of the absorbed state: lane 1 = u0, lane 6 = u1, lane 11 = u0^u1^K11,
  lane 4 = u2, lane 9 = u3, lane 14 = u2^u3^K14, the other lanes 0..15 the constants K below; padding gives lane 16 =
  0x8000000000000006.  F(u) = SHA3-256-r11(m(u)) XOR PD (PD a fixed 256-bit mask).  m is injective, so F(u) = F(u') with
  u != u' gives two distinct messages with equal complete digests.
This program regenerates the bit-sliced straight line of proof.md Section 3 (the same algorithm and node order as the C
generator gen3.c, with the generator's decisions PLAN: constants trial (its values listed below), round-1 and theta complements, free term
polarities; its packed two-address encoding must hash to PROG_SHA256), checks it against a plain 11-round implementation, and runs
  rho-w22   : the search of proof.md Section 4 at width 22 (planes 22..255 zeroed after each step), one pair per trial;
              the table keeps the trail number of each end; the replay measures the stored trail by walking it,
              keeping every GCK-th point as a checkpoint, walks the new trail once and lock-steps one segment;
  proj-w256 : eight chained full-width steps from 256 random points, first pair agreeing on the 22 low digest bits.
One Python integer holds a plane for all trials of the request (trial t in bits 256t..256t+255); trials never interact.
"""
import sys, json, hashlib, heapq, base64

M64 = (1 << 64) - 1
RCA = [0x1, 0x8082, 0x800000000000808A, 0x8000000080008000, 0x808B, 0x80000001, 0x8000000080008081, 0x8000000000008009,
       0x8A, 0x88, 0x80008009, 0x8000000A, 0x8000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
       0x8000000000008002, 0x8000000000000080, 0x800A, 0x800000008000000A, 0x8000000080008081, 0x8000000000008080,
       0x80000001, 0x8000000080008008]
ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
NR = 11                         # rounds of the target
PLAN = """
trial 1214
nr 11 optmode 4 trick 1 lasttrick 1 notfold 0
F1 GEQIAUAoJBQACAgABAAA0QAAAIAIABBIIhAAJAAyAAAAAAABEQAAAA==
G1 AAAAAAAAAAQBIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==
FG 2 AAAAAgAAIKAAggAAAIADAICBAAAAAQAAAAQAQAgBCYACQgAICaQFAA== CAABAAAFQIABAAiIAKBMAgAIABIiBBAwAgBgQAAAAgAAgBEACEAAAw==
FG 3 gAAAAAAAAAACAAAAAAAAAgAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAQ== AAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAA==
FG 4 AAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAgAAEAAAAAAAAgAAFAAAA== AAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAA==
FG 5 AAAQAgAAAAAAAAAABAACAAAAIAAAAAAAAAAAAAAAABAAAAACAAAAAA== AAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==
FG 6 ACAAAAAAAAAAAAAQQAQAAAAAAAAAACAAAAAAAgAAAIAAAAEAAAAAAA== AAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAA==
FG 7 AAACAgCAAAABAAAAAAAEAAAAAAAAAACAAAACAAIAAAAAADBBAKAAAA== AAAAAAAABAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAA==
FG 8 AAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAACEAAAAAAAAAAAAIIAIAAA== AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAA==
FG 9 AAAAAAAAAAAAAAAAAAAAAgAQAAAAAAQABSAQAAAACAAAAAAAAAAAAA== AAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAABAAAA==
FG 10 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA== AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==
PHI 0 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
PHI 1 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
PHI 2 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
PHI 3 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
PHI 4 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
PHI 5 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
PHI 6 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
PHI 7 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
PHI 8 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
PHI 9 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
PHI 10 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
DEC 2 AAEEAQABFAIwACAAgACAACAGAAFABYAAwAeABcAEAAIAAYEAoARgBEAAQAACAEAAAAEAAcAHMAAAAoAFIACABgAAAAAAAgABwAQAASAFAABABiAAgAUgAAACEAGABTAAIABgBEEAAAGAAIAAAgEEAQABAAEgAAABAASAAAQCIAAiACAAggCAAEAAAAJAAEAAgAaIAAABAAIAAiAAAACAAIAAAQIAAiQAAAJAAJAAQABAAAABQABAAEgAAgJAAIAAAAFgBEAAgAZAAAACQAAAAAACgAACBEAGIgBAAAgEQABABYQAAAIEAQAEAAQgAAABAAEAAgAAEAEIAiAAQAbgBSAAgAAAAeAGAAJAADAAIAZAAIAGQAAAARABIAbgBYgAAAGgBIAAQABgByAAIAYEASQAQADgBSAFEALgBYAABAJEACAFIAAAAgwCEAIgACAAIgAAAkEFggCAAIAAcAQgBkAAIAAAAoAAAQKABiAAQACABSAAIAAAACAAAAKABiAAAAJQAAABQAAAAgACQAYgAAABIAVAACAAIACQAKAEggAgBSAGQADgBUAAAAJIBhACgAwAAcAEQAAAAQAEKAAAAgAAwASEAAAAIABgBwAB4AVgBOAGgABABUEAQAAwAEAAQAAwACIAAAEgAFEAQACAAAAHoAQgBuAFAAcABIAAAAECAQAEQABAAIAFQAVAAIIAgABAAEAAQARAACAAAQJAAIAAQAAgAEAFgAWABSAAAAIAAYAA4AZAAGAEAAIAAIAAAgGABTAAIABIAMAEgAAAASAAoAdAAAABQAAkAAAEQAAgAAACIQAEAoEAIABgBAACEAGABQAOKQBAAEAAwASAAA==
DEC 3 IgAIAkAAQAUABwAACAIIAUAAgAAhAEAAAAIIAkAGYAcAAgACIAAABwgBIADgBQACgAAABIAAgAWgBEAAYAcAAgACYARABQACAAFABSAAgAAAAoAGYAegBEAAAgJABoAAIADgBgABoARAACAFggAAAQIBCAIAASAAKAAAAoIAgADAB4AAIAAiAIAAAAGCAAAAIAAABAICQAAAAUAAAAEAAUEAUAAAB4AFwAQAAUAAoAcgAIAGIAAgAAABQABAAAACRAAAAQACAAGCAAACAAKAAIAAQQAgAEAAQABAACAFgAAAAQABAAFAAAAEUAYAAgAHAAIAAQAEgAAoBSAAAAKABqAEAAFAAAAAAAIAAQAOQAAgAIAFgAAAASAAIAAgACkAgAZAAAACAAEqAAgCQAABAYAAAAIAAUAAIABAAAABAAIAAsAEAAGEAAICAAEgBQACgABIBgAAggBDAIAAQADgBYAA4AWAAEAAQABAACAAAAFABjAAggCgBAAB4AYwAEIAgAAAAIAAoAQIAkAAAAKAACAAAAcgBgABKAAAAcAEQAyAAAAKIADABKAHgAAgBmAE4AUAASAAgAAAAgABAAJAABAAAAFEAAACAAKAACgAAAGAAOAFgAZAAEEAQAAAAoAFQAVAACAAAAEwAAABAgIAAQgBQAWABSEABAEgAKAHgAAwAEAFgACgB0AAAAJAACAA4AVABgACEAKAAAAAAAIAAcAHAAIAAbAEIAAgBkAAQACAAIAAAAEiAAgCwAegBCAFQQCAACAAAQEgAAACgABAAAgCQgAgBYEAAAECAcAE4AWCAEIAAAFgByAAIAAAAQABAAGAAEAFAAIAAgAHQACAAA==
DEC 4 IAAAAGAEQQUAAgACIAXgBSAGgAYgAAABgACCAJAAIAAAAoAGgAAABAABwAcAAAACIAAgAEAG4AYABIAAQABAACIAAAcAAUAAgAAAAAACQAUAAeAFBAJAAEAAIAAhAIAAQABgBIAAQAUgAGAHAAIxAAABIABAAGAEAAJQAAACEAEAAgAEwAQAAsAEIAAgAOAGQQBIAOAFIACAACgAAAEEAQACgABgBAABAAEgBgABAAKAAEAAAALgBQQBQAAgAEAAEAIgAOAFwARABQACIAVAAAACAAHABAACQABAAGAEAAFAAOAFQACAABACAASAAGAHIACAACAGggAQAgABQAAABAACAABAACAFQAAAAoAAQAAAASAFiAAgAAAAKAAgAOAFIAABAgACQQACASAAAAFgBDAAgAAIAgACAAIAAgABgACABSAA4AXABMEEBAJAAAAAgAbABKAHAAEhAAgCgAAEB0EAAAEAAYAAggABAoAAgAAIAiEAIAVAAAABQAYAAQABAAFAACAAIAagBCAAgAAAAYAGUAYAAoQAQABAAGAN4AWAAAACoAfgBQAAAASgB4AMIAAAAeAFgABAAJAAAAHgBcAEgABgBOAGAgHgBQAEAAEkAMAH4AYAACAAIACgB4AAIAWABoAAgABAAAAAMACQACAAgAAYAoAFAALABGAHIgAAAiAAkAAAAAACQAAgAEAGAAJAAEAA4AWEBgACAARAAEAAMAAAAQIBAQGAAFAAAQIAAoAGAAIAAgEBQAAAAiAAgAYUAgABQAAAAgABQQAAAiAAgAAwAIAA4AWABQACYAQCAQAAQAAAAkAGAAFgB4AAAAEAAQABIQAAAkAGAAIAAg==
DEC 5 AAJQAEIAAAEAAgABgABABgACIABAADAAYARCAIIAAAEgACAACAIAAkAAEAIAAIAAAAIgDEAAAAQgBgACgABAABABIAAAAgEBoAeAAAACgAVABUAGAAEAAiAAQAbgBUAGAALgBUAAgAVAAEAFgAAAAgACBAIAAkQAgAZAAIAAYATgBUAAAAGAAKAHBAEAB4IAQAAAAeAFQgAAARACgAUgAIIAgAWAAAACIACAADAAAAEBAoIAggAgADAAIABgBAABIAUQAgABIAWgBwABAAKAAAAB4AUCAQAAgACAAEAAIACgBFAAAAFAAMAHIAUgAIAAAAEAAQACAAIAAQACAQAAAsAHYAcgAAACIACABVAAQAAoAEAAUACgByAAAAEgBkAA4AUAAAACAAHABEAAAAEwAAAEgABABSAAAAICAYAFQQAEAgABoASAACAAIABABQQBAAJgB0AFgAAgAAACQgAkBSgA4AWABiAAIAVABuAGYAQAAgAB4AbABKAEgAAgAEAAQAAAAiAAgACgBAIBAAAAB4AFgAAgAAAHAAfgBUAFAAGABUAAUAAAAgIBEAEgBSAAAALAB4AAgAZAAEAAIABABQIBQAYABCAAAAEiAEAAAQJAAAACAAegBwACAAIgAKAEAAKABgABAAJgBIAFoAeAAAECgADgBaAHBAGAAMAHAAIAAQACgAAoAIQAIAAAAuAFgAUgAAABSADAB+AFIAAAAiAAgACABcAEQAUAAoEAAAJAAEAFgABAAKAEBAEAACAAAAEEAYAFwAcABAACAAJQBoAFQADBBIYAIACAAAAHAARABgAHJABgBCAAQAAAAkAAKAAAAhACgAAgAFAAAAAAAQ==
DEC 6 gAAgBYgAJAAAB2AHAAJQAAAAAAFAAEAAQAAgAAAHQQAgAAAHAAQAAUgAQAAEAhAChgAgACAAAAIkAIAAgAYgADAAIABCACAAYAfABCAA4AWAACAAggAAAQACIACAAMAEIgAgAOAGIACgBAABQACAAEAAIAUgAEAGIAaAACAAAAIAAgABAAJgByIAQABAAAACIAAQAcAEQAAAAiAA4AYAAQAAgACAAAAHoASAAGAEgAWBAAABAAJAAEAAAAFQAEAGAAGIACAAAAEEAjAAYAdAACAAQAAABAACAQHgBcAHIAUAAmAHQACCAKAEIAAABEAAQQCgBEAGAAQAACAAMADgBUEAAgFAAIAAAAkkAIEAAAIAAiAAEAIAAUAAAQFEAIAFoAcAAoAFBAIAAgABIAWAAAACQgAEAQAAwARAAEAAoAcAASIAkADgBkAAgAXgBoAAgAAAAgABAAIAAhABAACAAIAFoAfAB4AGIAAAAkAAgAAAAqAEAAEhAAACQACAAAAAgABAACAGIAAgAAAB4AVAAEAAAAHgBSAFiABABkAAAAFgBAACQAAAAQABgABAAOAFQAUgBeAFIABAAEAAAAHgBYAAAAJAAAgCAAKAAAABSACQAAABAAIAAUAAAAGAAEAAQAAAAoAGgAAAAgABBAIgAEAAIgBAAAgCQQAgAOAGIADABKAHoATgBSAF4AVAAKAEAAEgADAAiAAAAiAACAFABUAFQAACAQABAAFAACAAggDgBSAAQQDABIAGAAIAAggBQACBAMAHgAAAAkEAAAAAAEEAoASgBEAFgAUgAMAEgAAgAAACAAEgADAAYAQgBSAAoASABYAGgACCAEAAYAQAAg==
DEC 7 AAEgAAACgAAgBSAAQAAAASAAgAYgAIAABAGCACAAQACAAAAEwAfgBgABgACAAAACJACAAEAAAAJAAEAAIAAAAkAAQAAgAAgBgQCAAAABAAEAAQABAAHAB4AFAAFQBgAAIAAAAgABggAAAkgAIABAACAAgABgBKAEIAAAACAFAgGAAIEAgADgBQAHQABAACAAoASQAAABIACQAAABYARAACAAgAAAAkAAEgEAAgABQAaAAEAGAQKEAEAAgAAgAIAAQAVAAEAAAAIgBUAFAAIgACAGgADABIQAIAAAAUEAgAAAAkAAIACAAGAHQAAgACAAAAIAAgABQACBAIAAYASgBFAAgABAAAABCAEAACAAQAYAAQgCIABAAIIAIABAABABIABBAEAAQAYEAoAAgABAAAACgABgB4AFAAFAAAACAQJADAABQABAAEAFAAIBAaAEAAIAAkQAAQJABkAAgAAQAUAAAAFAAEEAiACgBwACAAdAAAACgACAAAAHMABAAIAAYAQgAIAAAAFAAKAH4AUgBQABQAZQAOAF4AUEAUAAIAAgAIAGAAJABgAHQADABAAEIQBQAAABgAAAAQABQgAAAQgBKAAABIAAQAZAAEAAgAZABVAAYAchAIAAAAfgBUAAAAGgB0EA4AXBBEAAIAAQAUAAIAXgBQACgAVABoAAAAAAAYAGAAGABUAAMACAAAAHAAcgAEAAgAYIASAA4AYAAeAFQACgByAAAABABSEAQAAAAoAGAAIAAoAAAAdABYAAMAAgBSAACAIAARABgABgBAABIACgB4AAIACABQABoARgBOAFgABAAEAAQADgBQABAASgBIAAAAIgBgACoAQAAg==
DEC 8 QABABmAHQAAgAIAAgAAAASAAIAaAAAACAAEAAkAAQgAwAAABIABABQACgAAAARACYAQgAIAAQAAQAgAHAAIAAgICYAfABIAAwATABCQAgABABgEBYAQgBAgCYAQAAjEAIACAAEAAAAFABgABAAHABwABgACgB2AHAAIIAgAEIAAAAQACIACBAIAAIACABkAAAAEAASQAUACAAAACQABAAGAHAAIEAQABAAIgBSAAAAIABEAAAgIgAGANgAAAB6AEAARCAAABBALgBeAGAAIAB4AFgABAAMAHAAFAAEAAQABABWAEgAVAAEAAIAACAQACIAYAAIAAgAACAUEAoAeAAMAEQABCAAgBAAEgBkAGggBAAOAFgAAEAYAAoAQQAQABiACABeAFgAAgAEAFAAEABwgCgACEAAAHgAAMAgABQABIAEEAAAAwAEAAgAAAAUAAQABEAAABAAEAAAABAAEAAiAAgAUAAoAAIQAgAGAHAAIAAoAGIQAAAQAB4AWAAAAAgAAAAYAAQAAAACAGAAEgAEAAgACBAIAAgABAAIAAIAWAAAgC4AYAACAGIQAgBoAAAAEgBSAAgACAACAAAAIgAOAFgAagBEQAUAAABwACQACAACAAAAEAB+AFgAACAUEAoAQAAkAGgAVABgABBAIgBoAAgACABiAAQAAkAAACAAEAAUAAiAAQAQQBCAEAASAGIAUEAgAC4AYAAUEAYAQAAEAAIADgBUAAgAAAAQACYAQoBQACgAAAAgAEwAdgBwAHAAEgAGAEkAChBIAAQgAiAAACCAGAAAACIACAAAECgADgBYAGAAGAAOAFAAIQAkAGAAIAAiAAAAKAAAQCIAZAAA==
DEC 9 QACAAIgAIADgBQABIAAgAIAAQADgBYgAIABAAAACgQAkAGAHUAABAQACIAAAAkAAIABAAAACgQBABQIBiAAAAQACIACAACAGAAQAAggCAAEAAsAEgAAgAAAEIAYAAiAAgQAAAYIFAAEEAkAASABAAAACFAJgBwABgABAACAAAAEIAiQA4AUAAAAEAAkgAKAEIQBAAEAAIAAAAgQBIAAABCAAgAVAAIAFEAFAACAAIQAAAQgBAAAgBnAEAAFAAIAAgABBAEAGgADAByAFhABgB0AFQAZAAIAGgABAACAAIACABYAAYAQgAMAHwARIAEEAAAJAAMAHAgJABYQAgAVABSAAiACABoAAAAAgAAACAAQAAjAAYAcABAQBAAIAASAAYAcAByAAkABAAIAAUAAgAAACAAGQAAACAAEAAUAAoAfgBYAAAAGAAKEEgAAEAgACAAIAAQACgACCAEQAAAIABAABQQBAAAAAAAEABIAAAAFAAEAFAAFAACAAQACgB1AAIAAABMAEAALAB4IAQAAAAkAAAALABwIBIABAADAAIABABqAEggAAAoQAQAAAAQACAABABTAAYAQgACAFQACAAIAAAAVAAEAAIACUAKAEgACAAAABAAEAAqAEgAAAAoAAYAcAAgACCAKQACAAQAAEBwACAAIgBiAAIAVAAFAAAAEEAQACAAEAAQECIAAgACAAQAAhAAAEQAABAQABggAAAlAAAAFAABACgAAgAEAAIAUAAoAAIAAgAAQBQABAAAAEQgBCAAICQAAkAIEAAAACAgABQAAkAAABQgCAAAAHAAGgBwACgACgBxACIAbAB0AAAAGABkIAIAAAAqAEgAAAAg==
"""
PL = {}
_d = lambda t: base64.b64decode(t).hex()   # the bit fields of PLAN are stored in base64 (plan.txt holds them in hex)
for _ln in PLAN.strip().split("\n"):
    _t = _ln.split()
    if _t[0] == "trial": PL[_t[0]] = _t[1]
    elif _t[0] in ("F1", "G1"): PL[_t[0]] = _d(_t[1])
    elif _t[0] == "FG": PL[("FG", int(_t[1]))] = (_d(_t[2]), _d(_t[3]))
    elif _t[0] == "PHI": PL[("PHI", int(_t[1]))] = _d(_t[2])
    elif _t[0] == "DEC": PL[("DEC", int(_t[1]))] = _d(_t[2])
    elif _t[0] == "nr": PL["optmode"] = int(_t[3])
TRIAL = int(PL["trial"])            # constants of the generator's selected trial
PROG_SHA256 = "9d0054960b9726617ff5584901efce4d811569e014d0ced99597be4c53401937"
NINSTR = 59324
NREG = 2304
B35 = {}                            # LRS: first node of the last round; DIAG: lanes 0, 6, 12, 18, 24 after round NR-2
NC = -1
O_IN, O_XOR, O_AND, O_OR, O_NOT = 0, 1, 2, 3, 4


def consts(trial):
    """Constants of the generator's selected trial (structured set S3-04 of proof.md Section 2: the free lanes solve the
    704 round-0 chi neighbour conditions); the values are those gen3 sets for this trial, listed here."""
    K = [0] * 25
    K[16] = 0x8000000000000006
    for l, v in [(0, 0x0000000000000000), (2, 0xb8191f77d89d59d3), (3, 0x0000000000000000), (5, 0xffffffffffffffff), (7, 0x0000000000000000), (8, 0x0000000000000000), (10, 0xffffffffffffffff), (11, 0x6e0647ddf6275672), (12, 0x0000000000000000), (13, 0x770323eefb13ab3a), (14, 0x23f3704413b15316), (15, 0xffffffffffffffff)]: K[l] = v
    return K


KL = consts(TRIAL)


# ---------------- generator (same algorithm and node order as gen.c) ----------------
class Gen:
    def __init__(self):
        self.op, self.a, self.b, self.k, self.lin = [], [], [], [], []
        self.form, self.fidx, self.cons = [], {}, {}

    def new(self, op, a, b):
        self.op.append(op); self.a.append(a); self.b.append(b); self.k.append(0); self.lin.append(-1)
        return len(self.op) - 1

    def consn(self, op, a, b):
        if op != O_NOT and a > b: a, b = b, a
        key = (op, a, b)
        n = self.cons.get(key)
        if n is None:
            n = self.new(op, a, b); self.cons[key] = n
        return n

    def fadd(self, m, node):
        f = len(self.form); self.form.append((m, node)); self.fidx[m] = f
        return f

    def xorv(self, a, b):
        if a[0] == NC: return (b[0], b[1] ^ a[1])
        if b[0] == NC: return (a[0], a[1] ^ b[1])
        if a[0] == b[0]: return (NC, a[1] ^ b[1])
        la, lb = self.lin[a[0]], self.lin[b[0]]
        if la >= 0 and lb >= 0:
            m = self.form[la][0] ^ self.form[lb][0]
            kk = self.k[a[0]] ^ self.k[b[0]]
            if m == 0: return (NC, kk ^ a[1] ^ b[1])
            f = self.fidx.get(m)
            if f is not None:
                n3 = self.form[f][1]
                return (n3, kk ^ a[1] ^ b[1] ^ self.k[n3])
            n = self.new(O_XOR, min(a[0], b[0]), max(a[0], b[0]))
            self.k[n] = kk; self.lin[n] = self.fadd(m, n)
            return (n, a[1] ^ b[1])
        return (self.consn(O_XOR, a[0], b[0]), a[1] ^ b[1])

    def notv(self, a):
        if a[0] == NC: return a
        before = len(self.op)
        n = self.consn(O_NOT, a[0], 0)
        if len(self.op) > before and self.lin[a[0]] >= 0:
            self.lin[n] = self.lin[a[0]]; self.k[n] = self.k[a[0]] ^ 1
        return (n, a[1] ^ 1)

    def and2(self, a, b, sel=0):
        """logical a AND b; a mixed-polarity term is A ^ (A & B) (polarity 0) or, with sel, (NOT A) | B (polarity 1)"""
        if a[0] == NC: return b if a[1] else (NC, 0)
        if b[0] == NC: return a if b[1] else (NC, 0)
        if a[0] == b[0]: return a if a[1] == b[1] else (NC, 0)
        if a[1] == 0 and b[1] == 0: return (self.consn(O_AND, a[0], b[0]), 0)
        if a[1] == 1 and b[1] == 1: return (self.consn(O_OR, a[0], b[0]), 1)
        A, B = (a[0], b[0]) if a[1] == 0 else (b[0], a[0])
        if sel:
            na = self.notv((A, 0))
            return (self.consn(O_OR, na[0], B), 1)
        t = self.consn(O_AND, A, B)
        return self.xorv((A, 0), (t, 0))


def cost_term(b1, b2):
    if b1[0] == NC or b2[0] == NC or b1[0] == b2[0]: return 0
    return 1 if (b1[1] ^ 1) == b2[1] else 2


def row_choose(b, need):
    """the row decision of gen3.c: complement subset s and 10-gate position j (-1: none), first cheapest"""
    distinct = all(v[0] != NC for v in b) and len(set(v[0] for v in b)) == 5
    best, bc, bj = -1, 1 << 30, -1
    for j in range(-1, 5 if distinct else 0):
        if j >= 0 and not ((need >> j) & 1 and (need >> ((j + 1) % 5)) & 1): continue
        for s in range(32):
            c = 0; bb = list(b)
            for X in range(5):
                if s >> X & 1:
                    if b[X][0] == NC: c = 1 << 29
                    else: bb[X] = (b[X][0], b[X][1] ^ 1); c += 1
            for X in range(5):
                if need >> X & 1:
                    if X == j:
                        k = (j + 1) % 5; p1, p2 = bb[(k + 1) % 5], bb[(k + 2) % 5]
                        if (p1[1] ^ 1) == p2[1]: c += cost_term((bb[k][0], bb[k][1] ^ (p1[1] ^ 1)), bb[(X + 2) % 5])
                        else: c += 1                                   # mixed term k: its output polarity is free
                    else: c += cost_term(bb[(X + 1) % 5], bb[(X + 2) % 5])
            if c < bc: bc, best, bj = c, s, j
    return best, bj


TAB = {}
for _L in (0, 1):
    for _p in range(32):
        TAB[(_L, _p)] = row_choose([(X, (_p >> X) & 1) for X in range(5)], 0x0F if _L else 0x1F)


def row_order(T):
    """gen3.c row_order: chain bases first (X not in T, X-1 in T), then each X after the output X+1 it reads"""
    done, ordr = 0, []
    for X in range(5):
        if (T >> ((X + 4) % 5)) & 1 and not (T >> X) & 1: ordr.append(X); done |= 1 << X
    for X in range(5):
        st, Y = [], X
        while not (done >> Y) & 1:
            st.append(Y)
            if not (T >> Y) & 1: break
            Y = (Y + 1) % 5
        while st:
            Z = st.pop()
            if not (done >> Z) & 1: ordr.append(Z); done |= 1 << Z
    return ordr


def eval_selc(pat, s, T, mc):
    """the term polarities of a planned row with trick set T (gen3.c eval_row, chained form): out[X] reads out[X+1] for X in T"""
    bb = [((pat >> X) & 1) ^ ((s >> X) & 1) for X in range(5)]
    sel, ns, bit = [0] * 5, [0] * 5, 0
    for X in row_order(T):
        a, b = (ns[(X + 1) % 5] if (T >> X) & 1 else bb[(X + 1) % 5]) ^ 1, bb[(X + 2) % 5]
        if a == b: tp = a
        else: tp = (mc >> bit) & 1; bit += 1; sel[X] = tp
        ns[X] = bb[X] ^ tp
    return sel


def bits(h, n):
    v = int.from_bytes(bytes.fromhex(h), "little")
    return [(v >> i) & 1 for i in range(n)]


def build():
    g = Gen()
    for j in range(256):
        n = g.new(O_IN, 0, 0); g.lin[n] = g.fadd(1 << j, n)
    S = [[(NC, (KL[l] >> z) & 1) for z in range(64)] for l in range(25)]
    for z in range(64):
        S[1][z] = (z, (KL[1] >> z) & 1); S[6][z] = (64 + z, (KL[6] >> z) & 1)
        S[4][z] = (128 + z, (KL[4] >> z) & 1); S[9][z] = (192 + z, (KL[9] >> z) & 1)
    for z in range(64):
        S[11][z] = g.xorv(g.xorv((z, 0), (64 + z, 0)), (NC, (KL[11] >> z) & 1))
        S[14][z] = g.xorv(g.xorv((128 + z, 0), (192 + z, 0)), (NC, (KL[14] >> z) & 1))
    for r in range(NR):
        last = r == NR - 1
        if r == 1: ff, gg = bits(PL["F1"], 320), bits(PL["G1"], 320)
        elif r >= 2: ff, gg = bits(PL[("FG", r)][0], 320), bits(PL[("FG", r)][1], 320)
        else: ff = gg = [0] * 320
        phi = bits(PL[("PHI", r)], 1600)
        dec = None
        if PL.get("optmode", 3) >= 4 and r >= 2 and not last and ("DEC", r) in PL:
            hb = bytes.fromhex(PL[("DEC", r)]); dec = [hb[2 * i] | hb[2 * i + 1] << 8 for i in range(320)]
        C = [[None] * 64 for _ in range(5)]
        D_ = [[None] * 64 for _ in range(5)]
        for x in range(5):
            s = S[x][63]
            for y in range(1, 5): s = g.xorv(s, S[x + 5 * y][63])
            C[x][63] = g.notv(s) if gg[x * 64 + 63] else s
        for z in range(64):
            if z < 63:
                for x in range(5):
                    s = S[x][z]
                    for y in range(1, 5): s = g.xorv(s, S[x + 5 * y][z])
                    C[x][z] = g.notv(s) if gg[x * 64 + z] else s
            for x in range(5):
                D_[x][z] = g.xorv(C[(x + 4) % 5][z], C[(x + 1) % 5][(z + 63) & 63])
                if ff[x * 64 + z]: D_[x][z] = g.notv(D_[x][z])
        NS = [row[:] for row in S]
        nY, need = (1, 0x0F) if last else (5, 0x1F)
        for Y in range(nY):
            for z in range(64):
                b = []
                for X in range(5):
                    y, x = X, (3 * Y + X) % 5
                    zz = (z - ROT[x][y]) & 63
                    b.append(g.xorv(S[x + 5 * y][zz], D_[x][zz]))
                rsel = None
                if all(v[0] != NC for v in b) and len(set(v[0] for v in b)) == 5 and dec is not None:
                    dd = dec[Y * 64 + z]; best, Tm = dd & 31, (dd >> 5) & 31
                    rsel = eval_selc(sum(v[1] << X for X, v in enumerate(b)), best, Tm, dd >> 10)
                    for X in range(5):
                        if best >> X & 1: b[X] = g.notv(b[X])
                    for X in row_order(Tm):                          # chained row: out[X] reads the finished out[X+1] for X in Tm
                        if not need >> X & 1: continue
                        t1 = NS[(X + 1) % 5 + 5 * Y][z] if (Tm >> X) & 1 else b[(X + 1) % 5]
                        NS[X + 5 * Y][z] = g.xorv(b[X], g.and2((t1[0], t1[1] ^ 1), b[(X + 2) % 5], rsel[X]))
                    continue
                elif all(v[0] != NC for v in b) and len(set(v[0] for v in b)) == 5:
                    best, bj = TAB[(int(last), sum(v[1] << X for X, v in enumerate(b)))]
                else:
                    best, bj = row_choose(b, need)
                for X in range(5):
                    if best >> X & 1: b[X] = g.notv(b[X])
                k = (bj + 1) % 5
                if bj >= 0:                                          # 10-gate row: output bj reads output k
                    p1, p2 = b[(k + 1) % 5], b[(k + 2) % 5]
                    sel = ((b[(bj + 2) % 5][1] ^ 1) ^ b[k][1]) if (p1[1] ^ 1) != p2[1] else 0
                    if rsel is not None: sel = rsel[k]
                    NS[k + 5 * Y][z] = g.xorv(b[k], g.and2((p1[0], p1[1] ^ 1), p2, sel))
                for X in range(5):
                    if need >> X & 1:
                        if bj >= 0 and X == k: continue
                        t1 = NS[k + 5 * Y][z] if X == bj else b[(X + 1) % 5]     # not y and z == not chi_y and z
                        t = g.and2((t1[0], t1[1] ^ 1), b[(X + 2) % 5], phi[(X + 5 * Y) * 64 + z] if rsel is None else rsel[X])
                        NS[X + 5 * Y][z] = g.xorv(b[X], t)
        for z in range(64):
            NS[0][z] = (NS[0][z][0], NS[0][z][1] ^ ((RCA[r] >> z) & 1))
        S = NS
        if r == NR - 2:
            B35["LRS"] = len(g.op)
            B35["DIAG"] = {S[l][z][0] for l in (0, 6, 12, 18, 24) for z in range(64) if S[l][z][0] != NC}
    out = [S[j >> 6][j & 63] for j in range(256)]
    PD = 0
    for j, v in enumerate(out):
        assert v[0] != NC and v[0] >= 256
        PD |= v[1] << j
    return g, [v[0] for v in out], PD


def allocate(g, outn):
    nn = len(g.op)
    live = [False] * nn
    for n in outn: live[n] = True
    for i in range(nn - 1, 255, -1):
        if live[i]:
            live[g.a[i]] = True
            if g.op[i] != O_NOT: live[g.b[i]] = True
    last = [0] * nn
    for i in range(256, nn):
        if live[i]:
            last[g.a[i]] = i
            if g.op[i] != O_NOT: last[g.b[i]] = i
    outj = {}
    for j, n in enumerate(outn): last[n] = 0xFFFF; outj[n] = j
    outdef = list(outn)
    reg = [0] * nn
    busy = [False] * NREG
    LRS, DIAG = B35["LRS"], B35["DIAG"]
    hfree = list(range(256, NREG))                    # free registers 256.. (a heap; only allocation takes them)
    lfree = []                                        # free registers 0..255 (a heap; may hold busy or repeated entries)
    for j in range(256):
        reg[j] = j
        if last[j]: busy[j] = True
        else: lfree.append(j)
    heapq.heapify(lfree)
    code, prog, peak = {O_XOR: 0, O_AND: 1, O_OR: 2, O_NOT: 3}, [], 0
    for i in range(256, nn):
        if not live[i]: continue
        op, a = g.op[i], g.a[i]
        b = a if op == O_NOT else g.b[i]
        dy = []                                       # registers of the operands that die here
        for k, o in enumerate((a, b)):
            if k == 1 and o == a: break
            if last[o] == i:
                r = reg[o]; busy[r] = False; dy.append(r)
                heapq.heappush(lfree if r < 256 else hfree, r)
        if i in outj:
            d = outj[i]; assert not busy[d]
        else:                                         # the lowest free register this value may use (gen3.c, B35)
            ok = [r for r in dy if r >= 256 or (i < LRS and i not in DIAG) or (i >= LRS and outdef[r] >= last[i])]
            d = min(ok) if ok else None               # a dying operand's register first (destination = a)
            if d is not None: pass
            elif i >= LRS:
                d = next((r for r in range(256) if not busy[r] and outdef[r] >= last[i]), None)
            elif i not in DIAG:
                while lfree and busy[lfree[0]]: heapq.heappop(lfree)
                if lfree: d = heapq.heappop(lfree)
            if d is None:
                while busy[hfree[0]]: heapq.heappop(hfree)
                d = heapq.heappop(hfree)
        busy[d] = True; reg[i] = d; peak = max(peak, d + 1)
        prog.append((code[op], d, reg[a], 0 if op == O_NOT else reg[g.b[i]]))
    return prog, peak


def encode(prog):
    """two-address encoding, packed little-endian: bits 0-1 op, bit 2 t; t = 1: destination = a, then a and (not NOT) b;
    t = 0: d, a and (not NOT) b; registers 11 bits.  A binary instruction with destination b is written with a, b swapped."""
    out = bytearray(); acc = nb = 0
    for c, d, a, b in prog:
        assert max(d, a, b) < 2048
        if c == 3: w, k = (3 | 4 | a << 3, 14) if d == a else (3 | d << 3 | a << 14, 25)
        else:
            if d == b and d != a: a, b = b, a
            w, k = (c | 4 | a << 3 | b << 14, 25) if d == a else (c | d << 3 | a << 14 | b << 25, 36)
        acc |= w << nb; nb += k
        while nb >= 8: out.append(acc & 255); acc >>= 8; nb -= 8
    if nb: out.append(acc)
    return bytes(out)


def compile_prog(prog):
    """The straight line, executed instruction by instruction (opcode 0 XOR, 1 AND, 2 OR, 3 NOT)."""
    P = tuple(prog)

    def step(R, A):
        for c, d, a, b in P:
            if c == 0: R[d] = R[a] ^ R[b]
            elif c == 1: R[d] = R[a] & R[b]
            elif c == 2: R[d] = R[a] | R[b]
            else: R[d] = R[a] ^ A
    return step


# ---------------- reference ----------------
def _perm_src():
    """Keccak-f rounds as straight Python source (theta, rho, pi, chi, iota per round; lanes a0..a24)."""
    L = ["def perm(a, rounds):", " " + ",".join("a%d" % i for i in range(25)) + " = a", " for rc in RCA[:rounds]:"]
    for x in range(5): L.append("  c%d = a%d ^ a%d ^ a%d ^ a%d ^ a%d" % (x, x, x + 5, x + 10, x + 15, x + 20))
    for x in range(5): L.append("  d%d = c%d ^ (((c%d << 1) | (c%d >> 63)) & M64)" % (x, (x + 4) % 5, (x + 1) % 5, (x + 1) % 5))
    for x in range(5):
        for y in range(5):
            r = ROT[x][y]; i = x + 5 * y; o = y + 5 * ((2 * x + 3 * y) % 5)
            L.append("  v = a%d ^ d%d; b%d = %s" % (i, x, o, "(((v << %d) | (v >> %d)) & M64)" % (r, 64 - r) if r else "v"))
    for y in range(5):
        for x in range(5):
            L.append("  a%d = b%d ^ (~b%d & b%d)" % (x + 5 * y, x + 5 * y, (x + 1) % 5 + 5 * y, (x + 2) % 5 + 5 * y))
    L.append("  a0 ^= rc")
    L.append(" a[:] = [" + ",".join("a%d" % i for i in range(25)) + "]")
    L.append(" return a")
    return "\n".join(L)


exec(compile(_perm_src(), "perm", "exec"))


def digest(msg, rounds=NR):
    blk = bytearray(136 * (len(msg) // 136 + 1)); blk[:len(msg)] = msg
    blk[len(msg)] ^= 6; blk[-1] ^= 0x80
    st = [0] * 25
    for o in range(0, len(blk), 136):
        for i in range(17): st[i] ^= int.from_bytes(blk[o + 8 * i:o + 8 * i + 8], "little")
        perm(st, rounds)
    return b"".join(st[i].to_bytes(8, "little") for i in range(4))


def msg_of(u):
    l = [KL[i] for i in range(16)]
    u0, u1, u2, u3 = [(u >> (64 * i)) & M64 for i in range(4)]
    l[1], l[6], l[11], l[4], l[9], l[14] = u0, u1, u0 ^ u1 ^ KL[11], u2, u3, u2 ^ u3 ^ KL[14]
    return b"".join(v.to_bytes(8, "little") for v in l)


def F_ref(u, PD):
    return int.from_bytes(digest(msg_of(u)), "little") ^ PD


# ---------------- setup and checks ----------------
def setup():
    for m in (b"", b"abc", bytes(135), bytes(200)):
        assert digest(m, 24) == hashlib.sha3_256(m).digest()
    g, outn, PD = build()
    prog, peak = allocate(g, outn)
    assert hashlib.sha256(encode(prog)).hexdigest() == PROG_SHA256 and len(prog) == NINSTR and peak <= NREG
    return compile_prog(prog), PD, len(prog)


def to_planes(points, T):
    """points[t][l] (256-bit) -> 256 planes with bit 256 t + l."""
    planes = [0] * 256
    for t in range(T):
        for l, u in enumerate(points[t]):
            g = 256 * t + l
            j = 0
            while u:
                if u & 1: planes[j] |= 1 << g
                u >>= 1; j += 1
    return planes


def lane_value(R, g, width=256):
    v = 0
    for j in range(width):
        v |= ((R[j] >> g) & 1) << j
    return v


def check_step(step, PD):
    import random
    rnd = random.Random(1)
    pts = [[rnd.getrandbits(256) for _ in range(256)]]
    R = [0] * NREG
    R[:256] = to_planes(pts, 1)
    A = (1 << 256) - 1
    cur = pts[0]
    for _ in range(2):
        step(R, A)
        cur = [F_ref(u, PD) for u in cur]
        for l in range(0, 256, 15):
            assert lane_value(R, l) == cur[l]


def shake(data, n):
    return hashlib.shake_256(data).digest(n)


# ---------------- rho-w22: the search of proof.md Section 4 at width W ----------------
W, H, DK, DTT, LC, U, TB = 22, 4, 3, 5, 256, 3000, 400      # a DP: bits 0..3 zero and bits 4..6, as a number, < 5; replay cap LC; no trail is cut
GCK = 16                                                    # checkpoint gap of the replay


def rho_w(trials, step, PD):
    T = len(trials)
    A = (1 << (256 * T)) - 1
    mask = (1 << W) - 1
    R = [0] * NREG
    seeds = [bytes.fromhex(t["seed"]) for t in trials]
    rho, nid, att, astart = [0] * T, [0] * T, [-1] * T, [0] * T
    table = [dict() for _ in range(T)]
    done = [None] * T
    obs = [dict(steps=0, trails=0, attempts=0, stored=0, replay_evals=0) for _ in range(T)]
    lid, lst = [0] * (256 * T), [0] * (256 * T)
    pend = []

    def f_small(u):
        return F_ref(u, PD) & mask

    def is_dp(x):
        return x & ((1 << H) - 1) == 0 and (x >> H) & ((1 << DK) - 1) < DTT

    def new_attempt(t, c):
        att[t] += 1; obs[t]['attempts'] += 1
        rho[t] = int.from_bytes(shake(seeds[t] + att[t].to_bytes(4, 'little'), 8), 'little') & mask
        table[t].clear(); nid[t] = 256; astart[t] = c
        for l in range(256):
            g = 256 * t + l
            lid[g] = l; lst[g] = c
            pend.append((g, (rho[t] + l) & mask))
        obs[t]['trails'] += 256

    def apply_pending():
        if not pend: return
        clr = 0
        for g, _ in pend: clr |= 1 << g
        for j in range(W):
            st = 0
            for g, x in pend:
                if (x >> j) & 1: st |= 1 << g
            R[j] = (R[j] & ~clr & A) | st
        del pend[:]

    def replay(sa, sb, lb, t):
        if lb > LC: return None                        # the new trail is longer than the cap
        a, la, ck = sa, 0, []                          # la: evaluations of the stored trail from its start to its DP;
        while True:                                    # ck: its points a_i for i = 0, GCK, 2 GCK, ... (checkpoints)
            if la % GCK == 0: ck.append(a)
            a = f_small(a); la += 1
            if is_dp(a) or la >= LC: break
        ev = la
        if not is_dp(a):
            obs[t]['replay_evals'] += ev; return None
        d = la - lb                                    # aligned pairs (a_i, b_(i-d))
        if d >= 0:
            ia, a, b = d, ck[d // GCK], sb
            for _ in range(d % GCK): a = f_small(a)
            ev += d % GCK
        else:
            ia, a, b = 0, sa, sb
            for _ in range(-d): b = f_small(b)
            ev += -d
        if a == b:
            obs[t]['replay_evals'] += ev; return None
        nx = (ia // GCK + 1) * GCK
        while nx < la:                                 # walk b to the next checkpoint; equal there: the trails merge in this segment
            q = b
            for _ in range(nx - ia): q = f_small(q)
            ev += nx - ia
            if q == ck[nx // GCK]: break
            a, b, ia, nx = ck[nx // GCK], q, nx, nx + GCK
        r = None
        for _ in range(min(nx, la) - ia):              # lock step through one segment
            na, nb = f_small(a), f_small(b); ev += 2
            if na == nb: r = (a, b); break
            a, b = na, nb
        obs[t]['replay_evals'] += ev
        return r

    for t in range(T): new_attempt(t, 0)
    apply_pending()
    c = 0
    while any(d is None for d in done):
        c += 1
        if c > 4000: raise RuntimeError("no pair")
        step(R, A)
        for j in range(W, 256): R[j] = 0               # width reduction (this experiment only)
        anyv = 0
        for j in range(H): anyv |= R[j]
        dpm = A ^ anyv                                  # walks with the low H bits zero
        eq, lt = dpm, 0                                 # then the DK bits above them, as a number, < DTT (bit-parallel, most significant first)
        for i in range(DK):
            p = R[H + DK - 1 - i]
            if (DTT >> (DK - 1 - i)) & 1: lt |= eq & (A ^ p); eq &= p
            else: eq &= A ^ p
        dpm = lt
        img = [R[j].to_bytes(32 * T, "little") for j in range(W)]          # byte image of the planes 0..W-1 of this step
        events = []
        while dpm:
            low = dpm & -dpm
            events.append(low.bit_length() - 1)
            dpm ^= low
        seen, fresh = set(), set()
        for g in events:
            t = g >> 8
            if g in seen or done[t] is not None or t in fresh: continue
            seen.add(g)
            x = sum(((img[j][g >> 3] >> (g & 7)) & 1) << j for j in range(W))
            ln = c - lst[g]
            tb = table[t]
            if x in tb:
                ida = tb[x]
                if ida != lid[g]:
                    r = replay((rho[t] + ida) & mask, (rho[t] + lid[g]) & mask, ln, t)
                    if r is not None:
                        done[t] = r; obs[t]['steps'] = c - astart[t]; obs[t]['stored'] = len(tb)
                        continue
            else:
                tb[x] = lid[g]
            if nid[t] >= U:
                new_attempt(t, c); fresh.add(t); continue
            i = nid[t]; nid[t] += 1; obs[t]['trails'] += 1
            lid[g] = i; lst[g] = c
            pend.append((g, (rho[t] + i) & mask))
        for t in range(T):
            if done[t] is None and c - astart[t] >= TB: new_attempt(t, c)
        apply_pending()
    return done, obs


# ---------------- proj-w256: chained full-width steps, 22-bit agreement ----------------
def proj_w(trials, step, PD, steps=8, bits=22):
    T = len(trials)
    A = (1 << (256 * T)) - 1
    pts = []
    for tr in trials:
        raw = shake(bytes.fromhex(tr["seed"]) + b"proj", 32 * 256)
        pts.append([int.from_bytes(raw[32 * l:32 * l + 32], "little") for l in range(256)])
    R = [0] * NREG
    R[:256] = to_planes(pts, T)
    from array import array
    allkeys = []                            # allkeys[s][g]: the 22 low image bits of lane g at step s

    def point(t, l, s):                     # input of step s on lane l (reference chain from the start point)
        u = pts[t][l]
        for _ in range(s): u = F_ref(u, PD)
        return u

    for s in range(steps):
        step(R, A)
        cols = [bin(R[j] | (1 << (256 * T)))[:2:-1] for j in range(bits)]   # bit g of plane j = cols[j][g]
        allkeys.append(array("I", (int("".join(c[g] for c in reversed(cols)), 2) for g in range(256 * T))))
        del cols
    done = [None] * T
    for t in range(T):
        st = {}
        for s in range(steps):
            ks = allkeys[s]
            for l in range(256):
                key = ks[256 * t + l]
                o = st.get(key)
                if o is None:
                    st[key] = (l, s)
                else:
                    a, b = point(t, o[0], o[1]), point(t, l, s)
                    if a != b:
                        done[t] = (a, b, s); break
            if done[t] is not None: break
    return done


def main():
    step, PD, nins = setup()
    check_step(step, PD)
    req = json.load(sys.stdin)
    if req["schema_version"] != 1 or req["target_profile"] != "sha3-256-r%d-prefix-v1" % NR:
        raise ValueError("unexpected organizer target")
    mask = ((1 << 22) - 1).to_bytes(32, "little")
    if req["event"] != {"kind": "digest-xor-mask", "mask_hex": mask.hex(), "expected_hex": "00" * 32}:
        raise ValueError("unexpected organizer event")
    trials = req["trials"]
    out = []
    if req["experiment_id"] == "rho-w22":
        done, obs = rho_w(trials, step, PD)
        for t, tr in enumerate(trials):
            a, b = done[t]
            ma, mb = msg_of(a), msg_of(b)
            assert ma != mb and (int.from_bytes(digest(ma), "little") ^ int.from_bytes(digest(mb), "little")) & ((1 << W) - 1) == 0
            out.append({"trial": tr["trial"], "message_a_hex": ma.hex(), "message_b_hex": mb.hex(), "observations": obs[t]})
    elif req["experiment_id"] == "proj-w256":
        done = proj_w(trials, step, PD)
        for t, tr in enumerate(trials):
            if done[t] is None:
                out.append({"trial": tr["trial"], "message_a_hex": None, "message_b_hex": None})
            else:
                a, b, s = done[t]
                out.append({"trial": tr["trial"], "message_a_hex": msg_of(a).hex(), "message_b_hex": msg_of(b).hex(), "observations": {"step": s}})
    else:
        raise ValueError("unknown experiment")
    json.dump({"schema_version": 1, "trials": out}, sys.stdout, separators=(",", ":"), sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
