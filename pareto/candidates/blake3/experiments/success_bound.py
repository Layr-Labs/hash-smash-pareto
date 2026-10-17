"""Exact random-function success bound of proof Section P, certified in the
organizer's executor (experiment blake3-r7-success-bound-v1).

Administrative arithmetic only: 60-digit decimals rounded outward (every
exponential and quotient is rounded in the direction that weakens the bound)
and exact rationals where no transcendental function is involved. The run
ignores the organizer seeds, certifies the bound once and reports the same
loss terms in every trial row; it returns no message pairs. Parameters are
those of proof Section 2.1; the structure is the integrated detection-delay
argument (Steps 1-6 of Section P). The administrative tool
tools/check_success_bound_c5.py imports this file to reproduce the numbers.
"""
import json
import math
import sys
from decimal import Decimal as Dm, getcontext, localcontext, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction as F

getcontext().prec = 60
LANES, NB = 256, 256
N = 2 ** NB
THETA = F(23, 2 ** 116)          # distinguished density: 111 zero bits and a five-bit window below 23
L = 1 / THETA
D, WBITS, WLIM, S1, K, IDL = 111, 5, 23, 16, 47, 1 << 17
U = 98400
R = -(-12 * L.numerator // L.denominator)          # ceil(12 L)
B = 1045778 * 2 ** 100                             # horizon (Section 2.1): least multiple of 2^100 certified
E2MAX = 3 * LANES * B // 2 ** S1                   # stage-2 budget
FINE, COARSE = 20000, 2000
TAIL_LOG2 = -40
EXPERIMENT = "blake3-r7-success-bound-v1"


def up(x):
    return x * (1 + Dm("1e-40")) + Dm("1e-58")


def dn(x):
    return x * (1 - Dm("1e-40")) - Dm("1e-58")


def fd(x, upper):
    with localcontext() as cx:
        cx.rounding = ROUND_CEILING if upper else ROUND_FLOOR
        return Dm(x.numerator) / Dm(x.denominator)


def ex_up(x):
    """Upper bound on exp(x) for rational x."""
    return up(fd(x, True).exp())


def upm(x):
    """x plus a positive margin (an upper bound for either sign)."""
    return x + abs(x) * Dm("1e-40") + Dm("1e-58")


def chernoff_k(q):
    """Least k with e^-q (e q / k)^k <= 2^TAIL_LOG2: the log of the left side is
    bounded above by -q_lo + k (1 + ln(q_up / k)) plus a margin, and compared
    with the exact threshold lowered by a margin."""
    qu, qd = fd(q, True), fd(q, False)
    bound = Dm(2).ln() * TAIL_LOG2
    k = int(q) + 1
    while upm(-qd + k * (1 + upm((qu / k).ln()))) > bound - abs(bound) * Dm("1e-40"):
        k += 1
    return k


def certify(B=B, U=U, R=R, theta=THETA, k_bits=K, idl=IDL):
    """Lower bound on the success probability for a uniformly random function."""
    Q = LANES * B
    Np = N - N * theta                                  # number of plain (non-distinguished) values
    assert Np.denominator == 1
    Np = int(Np)
    Lq = 1 / theta
    q = Q * theta                                       # mean number of distinguished fresh values
    k = chernoff_k(q)                                   # P(N1 >= k) <= 2^-40
    assert k < U, "table capacity must exceed the certified count of distinguished values"
    shift = fd(1 / (1 - F(k * Q, Np)), True)            # Pi_(t-k) <= shift Pi_(t-1)
    lam = lambda m: F(m * (m - 1), 2 * Np)
    pi_up = lambda m: up((-fd(lam(m), False)).exp())
    pi_lo = lambda m: dn((-fd(lam(m) + F((m - 1) * m * (2 * m - 1), 6) / F(Np) ** 2, True)).exp())
    split = max(1, Q - 150 * LANES * (Lq.numerator // Lq.denominator + 1))
    edges = [split * i // COARSE for i in range(COARSE + 1)] + [split + (Q - split) * i // FINE for i in range(1, FINE + 1)]
    delay, pa = Dm(0), pi_up(edges[0])
    for a, b in zip(edges, edges[1:]):
        pb = pi_lo(b)
        remaining = max(0, B - (-(-b // LANES)))
        delay += (pa - pb) * ex_up(-theta * remaining)
        pa = pi_up(b)
    delay = up(delay) * shift
    p = ex_up(-R * theta)                               # (1 - theta)^R <= e^{-R theta}
    p2 = ex_up(-(R - 1) * theta) * fd(1 + (R - 1) * theta, True)
    PP = F(Q * (Q - 1), 2 * Np)
    terms = {
        "no_duplicate": pi_up(Q) * shift,
        "detection_delay": delay,
        "own_trail": fd(F(Q) * Lq / Np, True),
        "long_earlier_trail": up(fd(F(R * Q) / Np, True) * p * (fd(q, True) + LANES) / (1 - p)),
        "later_trail_age": fd(PP, True) * p2,
        "disturbed_suffix": fd(PP * Lq * (Q + idl) / Np, True),
        "same_batch_pair": fd(F(255 * Q, Np), True),
        "start_hit": fd(F(Q * idl, N), True),
        "distinguished_class_duplicate": fd(F(k * k) * Lq / N, True),
        "count_tail_N1": Dm(2) ** TAIL_LOG2,
        "false_key": fd(F(k * U, 2 ** k_bits), True),
        "stage2_budget_and_rounding": Dm(2) ** -90,
    }
    total = sum(terms.values())
    lower = 1 - total
    return dict(terms=terms, total=total, lower=lower, k=k, q=q, Q=Q)


def to_float(d, upper):
    """Nearest double, then stepped so that it bounds the decimal d in the stated direction."""
    f = float(d)
    if upper and Dm(f) < d:
        f = math.nextafter(f, math.inf)
    if not upper and Dm(f) > d:
        f = math.nextafter(f, -math.inf)
    return f


def observations(r):
    """Bounded numeric observations: losses rounded up, the bound rounded down."""
    obs = {name: to_float(v.quantize(Dm("1e-12"), rounding=ROUND_CEILING), True) for name, v in r["terms"].items()}
    obs["success_lower_bound"] = to_float(r["lower"].quantize(Dm("1e-12"), rounding=ROUND_FLOOR), False)
    obs["certified_at_least_0_39"] = bool(r["lower"] >= Dm("0.39"))
    obs["chernoff_k"] = r["k"]
    obs["horizon_B_over_2_100"] = B // 2 ** 100
    assert len(obs) <= 16
    return obs


def main():
    request = json.load(sys.stdin)
    event = request.get("event", {})
    if (request.get("schema_version") != 1 or request.get("experiment_id") != EXPERIMENT
            or request.get("target_profile") != "blake3-r7-prefix-v1"
            or event.get("kind") != "digest-xor-mask" or len(event.get("mask_hex", "")) != 64
            or request.get("max_message_bytes", 0) < 64):
        raise ValueError("Unexpected organizer request")
    r = certify()
    assert r["lower"] >= Dm("0.39"), "the bound does not certify"
    obs = observations(r)
    rows = [dict(trial=t["trial"], message_a_hex=None, message_b_hex=None, observations=obs)
            for t in request["trials"]]
    json.dump(dict(schema_version=1, trials=rows), sys.stdout, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    main()
