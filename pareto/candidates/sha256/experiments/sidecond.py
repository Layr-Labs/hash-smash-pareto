"""sidecond.py: side-condition rate verification for 39-step SHA-256 claw attack.

Organizer experiment verifying the side-condition probabilities p8 and p9 that
enter the per-claw success probability.  For each trial, the experiment samples
2^14 random W8 (resp. W9) values and checks how many satisfy the exact sigma0
difference condition imposed by the characteristic.

The characteristic requires:
  sigma0(W8x + D8) - sigma0(W8x) == DS8   (mod 2^32)
  sigma0(W9x + D9) - sigma0(W9x) == DS9   (mod 2^32)

The modular differences are derived from the filed dense base (b1):
  D8  = Wy[8] - W[8]      = 0x40000000
  DS8 = s0(Wy[8]) - s0(W[8]) = 0x087ff000
  D9  = Wy[9] - W[9]      = 0xf7801000
  DS9 = s0(Wy[9]) - s0(W[9]) = 0x03010000

Each (D, DS) pair defines a single exact modular condition.  Exhaustive counts
over all 2^32 values by rowstat.c confirm p8 = 2^-3.830 and p9 = 2^-5.978.
This experiment independently samples 2^14 values per trial to verify those
rates are reproducible (expected ~1150 hits for p8, ~260 for p9).

Protocol: python-message-pairs-v1 (JSON on stdin/stdout).
"""
import json
import sys
import hashlib
import math
import struct

M32 = 0xFFFFFFFF

D8 = 0x40000000
DS8 = 0x087ff000
D9 = 0xf7801000
DS9 = 0x03010000


def main():
    request = json.load(sys.stdin)
    trials = []
    n_sample = 1 << 14

    for t in request["trials"]:
        seed = t["seed"]
        rng = hashlib.shake_256(bytes.fromhex(seed) + b"sidecond")
        raw = rng.digest(n_sample * 4)
        words = struct.unpack(f">{n_sample}I", raw)

        pass8 = 0
        pass9 = 0

        for w in words:
            w8p = (w + D8) & M32
            s0_w = ((w >> 7) | (w << 25)) ^ ((w >> 18) | (w << 14)) ^ (w >> 3)
            s0_w &= M32
            s0_w8p = ((w8p >> 7) | (w8p << 25)) ^ ((w8p >> 18) | (w8p << 14)) ^ (w8p >> 3)
            s0_w8p &= M32
            if (s0_w8p - s0_w) & M32 == DS8:
                pass8 += 1

            w9p = (w + D9) & M32
            s0_w9p = ((w9p >> 7) | (w9p << 25)) ^ ((w9p >> 18) | (w9p << 14)) ^ (w9p >> 3)
            s0_w9p &= M32
            if (s0_w9p - s0_w) & M32 == DS9:
                pass9 += 1

        # Observations must be a bounded map of simple ids to finite numeric
        # values (runner.py gate).  The modular differences are reported as
        # plain integers, and a log2 rate is reported only when its count is
        # nonzero, so no non-numeric value can ever be emitted.
        observations = {
            "n_sample": n_sample,
            "pass_w8": pass8,
            "pass_w9": pass9,
            "D8": D8,
            "DS8": DS8,
            "D9": D9,
            "DS9": DS9,
        }
        if pass8 > 0:
            observations["log2_p8"] = round(math.log2(pass8 / n_sample), 4)
        if pass9 > 0:
            observations["log2_p9"] = round(math.log2(pass9 / n_sample), 4)

        trials.append({
            "trial": t["trial"],
            "message_a_hex": None,
            "message_b_hex": None,
            "observations": observations,
        })

    json.dump({"schema_version": 1, "trials": trials}, sys.stdout)


if __name__ == "__main__":
    main()
