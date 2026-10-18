"""Exact random-function success bound of proof Section 6 for the P56 single-trail search (declared experiment
poseidon-orchard-r56-success-bound-v1).

Arithmetic only: 60-digit decimals with every exponential, quotient and product rounded in the direction that
weakens the bound. The lemma is the single-trail distinguished-point bound (structure of the public r23 and r48
entries of Jbenisek, re-derived in the proof): for a uniformly random function on N = p points and any start,
    success >= 1 - exp(-n (n + 1) / 2N) - n / N - e^-KD - n d / N - (S theta_hi + 1) e^-H - e^-TAB,
with theta_lo = (D - 2^128) / N, theta_hi = D / (N - 2^128), D = (2^126 + 1) T the number of distinguished field
elements (p = 2^254 + c with T <= c < 2^128), d >= KD / theta_lo (a multiple of U), gmax >= H / theta_lo, S = n + d,
and the table term e^-TAB bounding P(Binomial(S, theta_hi) > MCAP) by the Chernoff form exp(-mu) (e mu / a)^a with
a = MCAP + 1 > mu = S theta_hi. The run ignores the organizer seeds, certifies once and reports the same terms in
every trial row; it returns no message pairs. The parameters below are the literals of the submitted program.
"""
import json
import math
import sys
from decimal import Decimal as Dm, getcontext, ROUND_CEILING, ROUND_FLOOR

getcontext().prec = 60
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
# ---- parameters of the submitted program (proof Section 4.1); selected offline as proof Section 1 describes
PARAMS = dict(U=16, T=54556, MCAP=27997, KD=Dm("10"), H=Dm("20"), TAB=13, K=133553654)
EXPERIMENT = "poseidon-orchard-r56-success-bound-v1"


def up(x):
    """Upper bound of a nonnegative quantity. For a negative quantity use up_neg: multiplying a negative number
    by (1 + eps) moves it away from zero, which would be a lower bound, not an upper one."""
    assert x >= 0, "up is for nonnegative quantities; use up_neg"
    return x * (1 + Dm("1e-45")) + Dm("1e-58")


def up_neg(x):
    """Upper bound of a quantity that is at most zero: move it towards zero."""
    assert x <= 0, "up_neg is for nonpositive quantities"
    return x * (1 - Dm("1e-45")) + Dm("1e-58")


def dn(x):
    return x * (1 - Dm("1e-45")) - Dm("1e-58")


def exp_up(x):
    """Upper bound of exp(x) for x <= 0 (the decimal exp is correctly rounded; widen by one ulp-scale factor)."""
    return up(x.exp())


def ceil_div(a, b):
    return -(-a // b)


def derive(p):
    """Integer parameters from (U, T, KD, H): D, theta bounds, d, gmax, n, S."""
    N = P
    D = (2 ** 126 + 1) * p["T"]
    assert p["T"] <= P % 2 ** 128 < 2 ** 128, "T must not exceed p mod 2^128"
    # the table packs a distinguished value's low part into a 16-bit side field (proof Section 5)
    assert p["T"] < 2 ** 16, "T must stay below 2^16 so that the stored low part is exact"
    th_lo = (Dm(D) - Dm(2 ** 128)) / Dm(N)                 # lower bound of the per-step DP probability (rounded down below)
    th_hi = Dm(D) / (Dm(N) - Dm(2 ** 128))
    th_lo_d = dn(th_lo)
    th_hi_u = up(th_hi)
    d = int((p["KD"] / th_lo_d).to_integral_value(rounding=ROUND_CEILING))
    d += (-d) % p["U"]
    gmax = int((p["H"] / th_lo_d).to_integral_value(rounding=ROUND_CEILING))
    n = p["K"] * 2 ** 100
    S = n + d
    assert S % p["U"] == 0 and S < 2 ** 128
    return dict(D=D, th_lo=th_lo_d, th_hi=th_hi_u, d=d, gmax=gmax, n=n, S=S, N=N)


def table_term(S, th_hi, MCAP):
    """ln P(Binomial(S, th_hi) > MCAP) <= -mu + a (1 + ln(mu / a)), a = MCAP + 1, mu = S th_hi < a; returned as an
    upper bound of the probability (the bound is increasing in mu, so mu is rounded up)."""
    a = Dm(MCAP + 1)
    mu = up(Dm(S) * th_hi)
    assert mu < a, "table mean must stay below MCAP + 1"
    ln_ratio = up_neg((mu / a).ln())       # negative; moved towards zero, which raises the returned bound
    expo = -mu + a * (1 + ln_ratio)
    return exp_up(expo)


def certify(p):
    q = derive(p)
    n, d, S, N = Dm(q["n"]), Dm(q["d"]), Dm(q["S"]), Dm(q["N"])
    t_norepeat = exp_up(up_neg(-(n * (n + 1)) / (2 * N)))   # the argument is moved towards zero
    t_start = up(n / N)
    t_detect = exp_up(-p["KD"])
    t_short = up(n * d / N)
    t_gap = up((up(S * q["th_hi"]) + 1) * exp_up(-p["H"]))
    t_table = table_term(q["S"], q["th_hi"], p["MCAP"])
    assert t_table <= exp_up(-Dm(p["TAB"])), "table term exceeds e^-TAB"
    loss = up(t_norepeat + t_start + t_detect + t_short + t_gap + t_table)
    bound = dn(1 - loss)
    return dict(bound=bound, t_norepeat=t_norepeat, t_start=t_start, t_detect=t_detect, t_short=t_short, t_gap=t_gap,
                t_table=t_table, **q)


def to_float(x):
    """Report the certified bound rounded down, so the reported value never overstates it."""
    q = Dm(x).quantize(Dm("1e-15"), rounding=ROUND_FLOOR)
    f = float(q)
    return f if Dm(repr(f)) <= q else math.nextafter(f, 0.0)


def main():
    request = json.load(sys.stdin)
    mask = ((1 << 256) - 1).to_bytes(32, "little").hex()
    event = dict(kind="digest-xor-mask", mask_hex=mask, expected_hex=bytes(32).hex())
    if (request["schema_version"] != 1 or request["experiment_id"] != EXPERIMENT
            or request["target_profile"] != "poseidon-orchard-r56-prefix-v1" or request["event"] != event):
        raise ValueError("unexpected organizer request")
    c = certify(PARAMS)
    certified = 1 if c["bound"] >= Dm("0.39") else 0

    def ceil15(x):
        """Report a loss term rounded up, so the reported row never understates the term."""
        q = Dm(x).quantize(Dm("1e-15"), rounding=ROUND_CEILING)
        f = float(q)
        return f if Dm(repr(f)) >= q else math.nextafter(f, 1.0)

    obs = dict(bound_floor=to_float(c["bound"]), certified=certified,
               t_norepeat=ceil15(c["t_norepeat"]),
               t_start_log2=float(c["t_start"].ln() / Dm(2).ln()), t_detect=ceil15(c["t_detect"]),
               t_short=ceil15(c["t_short"]), t_gap=ceil15(c["t_gap"]),
               t_table_log2=float(c["t_table"].ln() / Dm(2).ln()),
               k=PARAMS["K"], d_log2=float(Dm(c["d"]).ln() / Dm(2).ln()), gmax_log2=float(Dm(c["gmax"]).ln() / Dm(2).ln()),
               S_log2=float(Dm(c["S"]).ln() / Dm(2).ln()), T=PARAMS["T"], MCAP=PARAMS["MCAP"], U=PARAMS["U"])
    rows = [dict(trial=t["trial"], message_a_hex=None, message_b_hex=None, observations=obs) for t in request["trials"]]
    json.dump(dict(schema_version=1, trials=rows), sys.stdout, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    main()
