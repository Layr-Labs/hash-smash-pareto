#!/usr/bin/env python3
"""budget40.py - shared-budget time_log2 of the r40 two-block bound (proof Section 6).
Block 1: 254-bit walk, P(T1<=t) = 1 - exp(-lam0 (t/2^a0)^2), a0 = 123.90702 - 1/2 log2 3.
Block 2: per-unit success rate 2^-b0c with b0c = b0 - 74.3238 + 91: the H4 closing event
(91 bits) takes the place of the carried 74.3238-bit tail inside b0 = 116.54377499.
One driver runs the walk, every usable walk collision feeds block 2; the program solves
log2 W for total success 0.39 and adds the psi mask log2(1 + 1/2896). Standard library.
"""
import math

p_succ   = 0.39
lam0     = -math.log(1 - p_succ)            # -ln 0.61
base_walk= 123.90702                        # df1f1cd1 board-best R40 walk floor
a0       = base_walk - 0.5*math.log2(3)     # 3/4-usable -> -1/2 log2 3
b0       = 116.54377499198934               # carried block-2 per-unit rate b0
H4bits   = 91.0                             # H4: closing tail holds with prob >= 2^-91 (worst row)
b0_closed= b0 - 74.3238 + H4bits            # H4 closing event replaces the carried 74.3238-bit tail (Luna J-280 item 2)
mask     = math.log2(1 + 1/2896)            # psi mask: +1 word op / 2896 per evaluation


def success(lw, a0, b0c, n=20000):
    W = 2.0**lw; A = 2.0**a0; B = 2.0**b0c
    hi = min(W, 12.0*A)                      # T1 mass is concentrated near 2^a0
    s = 0.0
    for i in range(n):
        t0 = hi*i/n; t1 = hi*(i+1)/n; tm = 0.5*(t0+t1)
        F0 = 1 - math.exp(-lam0*(t0/A)**2)
        F1 = 1 - math.exp(-lam0*(t1/A)**2)
        p2 = 1 - math.exp(-lam0*max(W-tm, 0.0)/B)
        s += (F1 - F0)*(1.0/3 + 2.0/3*p2)
    if W > hi:                              # remaining T1 mass (negligible) ~ all closed late
        rem = math.exp(-lam0*(hi/A)**2)
        p2 = 1 - math.exp(-lam0*max(W-hi, 0.0)/B)
        s += rem*(1.0/3 + 2.0/3*p2)
    return s

def solve(a0, b0c, lo, hi):
    for _ in range(80):
        mid = 0.5*(lo+hi)
        if success(mid, a0, b0c) < p_succ: lo = mid
        else: hi = mid
    return hi

# shared budget with the H4 closing event in the success integral
# the closing event replaces the carried 74.3238-bit tail
lw_new = solve(a0, b0_closed, a0-2, max(a0, b0_closed)+8)

t_new = lw_new + mask


import json, sys
def serve():
    req = json.load(sys.stdin)
    obs = {"p_success_x1e6": int(round(p_succ * 1e6)), "h4_tail_bits": H4bits,
           "log2_work_x1e6": int(math.ceil(lw_new * 1e6)), "time_log2_x1e6": int(math.ceil(t_new * 1e6)),
           "time_log2_claim_x1e3": int(math.ceil(t_new * 1e3))}
    assert obs["time_log2_claim_x1e3"] == 130754
    rows = [{"trial": t["trial"], "message_a_hex": None, "message_b_hex": None, "observations": obs} for t in req["trials"]]
    json.dump({"schema_version": 1, "trials": rows}, sys.stdout)

if __name__ == "__main__":
    serve()
