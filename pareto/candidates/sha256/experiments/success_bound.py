"""Exact random-function success bound of proof Section P for the frozen parameters (declared experiment
sha256-r56-success-bound-v1). Arithmetic only, no search, no pairs: 60-digit decimals rounded to weaken the
bound, exact rationals elsewhere, the terms of proof Section P in order; one certification reported in every
trial row."""
import json
import sys
from decimal import Decimal as Dm, getcontext, localcontext, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction as F

getcontext().prec = 60
EXPERIMENT = "sha256-r56-success-bound-v1"
TARGET = "sha256-r56-prefix-v1"
LANES, N = 256, 2 ** 256
THETA = F(1, 2 ** 112)                 # distinguished density: 112 zero planes, no window
L = 1 / THETA
K, IDL = 47, 1 << 17                   # key bits; reserved start identifiers
U = 71316                              # table capacity (memory budget)
R = 10 * 2 ** 112                      # per-trail age cap, 10 L
B = 1048069 * 2 ** 100                 # batch horizon
FINE, COARSE, TAIL_LOG2 = 20000, 2000, -40


def up(x):
  return x * (1 + Dm("1e-40")) + Dm("1e-58")


def dn(x):
  return x * (1 - Dm("1e-40")) - Dm("1e-58")


def fd(x, upper):
  """Decimal enclosure of a rational, rounded in the stated direction."""
  with localcontext() as cx:
    cx.rounding = ROUND_CEILING if upper else ROUND_FLOOR
    return Dm(x.numerator) / Dm(x.denominator)


def ex_up(x):
  return up(fd(x, True).exp())


def chernoff_k(q):
  """Least k with e^-q (e q / k)^k <= 2^TAIL_LOG2."""
  qu, qd = fd(q, True), fd(q, False)
  limit = Dm(2).ln() * TAIL_LOG2
  k = int(q) + 1
  while up(-qd + k * (1 + (qu / k).ln())) > limit * (1 - Dm("1e-40")):
    k += 1
  return k


def certify():
  Q = LANES * B
  Np = N - N * THETA                                  # plain-class size, an integer
  assert Np.denominator == 1
  Np = int(Np)
  q = Q * THETA
  k = chernoff_k(q)
  assert k < U, "table capacity must exceed the certified count of distinguished values"
  shift = fd(1 / (1 - F(k * Q, Np)), True)
  lam = lambda m: F(m * (m - 1), 2 * Np)
  pi_up = lambda m: up((-fd(lam(m), False)).exp())
  pi_lo = lambda m: dn((-fd(lam(m) + F((m - 1) * m * (2 * m - 1), 6) / F(Np) ** 2, True)).exp())
  split = max(1, Q - 150 * LANES * (L.numerator // L.denominator + 1))
  edges = ([split * i // COARSE for i in range(COARSE + 1)]
       + [split + (Q - split) * i // FINE for i in range(1, FINE + 1)])
  delay, pa = Dm(0), pi_up(edges[0])
  for a, b in zip(edges, edges[1:]):
    pb = pi_lo(b)
    delay += (pa - pb) * ex_up(-THETA * max(0, B - (-(-b // LANES))))
    pa = pi_up(b)
  delay = up(delay) * shift
  p = ex_up(-R * THETA)
  p2 = ex_up(-(R - 2) * THETA) * fd(1 + (R - 1) * THETA, True)   # (1-theta)^(R-2) <= e^(-(R-2)theta)
  PP = F(Q * (Q - 1), 2 * Np)
  terms = {
    "no_duplicate": pi_up(Q) * shift,
    "detection_delay": delay,
    "own_trail": fd(F(Q) * L / Np, True),
    "long_earlier_trail": up(fd(F(R * Q) / Np, True) * p * (fd(q, True) + LANES) / (1 - p)),
    "later_trail_age": fd(PP, True) * p2,
    "disturbed_suffix": fd(PP * L * (Q + IDL) / Np, True),
    "same_batch_pair": fd(F(255 * Q, Np), True),
    "start_hit": fd(F(Q * IDL, N), True),
    "distinguished_class_duplicate": fd(F(k * k) * L / N, True),
    "count_tail_N1": Dm(2) ** TAIL_LOG2,
    "false_key": fd(F(k * U, 2 ** K), True),
    "stage2_budget_and_rounding": Dm(2) ** -90,
  }
  lower = 1 - sum(terms.values())
  return lower, terms, k, Q // R


def down15(x):
  q = Dm(x).quantize(Dm("1e-15"), rounding=ROUND_FLOOR)
  f = float(q)
  return f if Dm(repr(f)) <= q else float(q - Dm("1e-15"))


def up15(x):
  q = Dm(x).quantize(Dm("1e-15"), rounding=ROUND_CEILING)
  f = float(q)
  return f if Dm(repr(f)) >= q else float(q + Dm("1e-15"))


def main():
  request = json.load(sys.stdin)
  event = dict(kind="digest-xor-mask", mask_hex="ff" * 32, expected_hex="00" * 32)
  if (request["schema_version"] != 1 or request["experiment_id"] != EXPERIMENT
      or request["target_profile"] != TARGET or request["event"] != event):
    raise ValueError("unexpected organizer request")
  lower, terms, k, cuts = certify()
  obs = dict(bound_floor=down15(lower), certified=1 if lower >= Dm("0.39") else 0,
        margin=down15(lower - Dm("0.39")), chernoff_k=k, max_cuts=cuts, U=U,
        no_duplicate=up15(terms["no_duplicate"]), detection_delay=up15(terms["detection_delay"]),
        own_trail=up15(terms["own_trail"]), long_earlier_trail=up15(terms["long_earlier_trail"]),
        later_trail_age=up15(terms["later_trail_age"]),
        disturbed_suffix=up15(terms["disturbed_suffix"]), false_key=up15(terms["false_key"]),
        loss_sum=up15(1 - lower))
  rows = [dict(trial=t["trial"], message_a_hex=None, message_b_hex=None, observations=obs)
      for t in request["trials"]]
  json.dump(dict(schema_version=1, trials=rows), sys.stdout, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
  main()
