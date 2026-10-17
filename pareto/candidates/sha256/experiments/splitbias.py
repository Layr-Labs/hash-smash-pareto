"""splitbias.py: is the splitting estimator unbiased? Measured against a known answer.

The filed tail bound rests on a route that converts a bootstrap lower bound on
E[q-hat] into a lower bound on q (proof.md Appendix D.1).  That conversion needs
one premise: that the fixed-effort multilevel product-of-ratios estimator is
unbiased for the probability it estimates, up to a small fixed-effort bias.  A
review marked the premise unsupported, correctly: the package asserted the bias
was below 0.01 bits at the filed population without ever measuring it.

This experiment measures it, on a problem whose answer is known exactly.

The toy.  A state is a tuple of K digits.  Stage k fixes digit k, which is drawn
uniformly from 2^BITS values and passes when it equals zero.  The digits are
independent, so the probability a state clears all K stages is exactly

    q = 2^(-BITS * K)

and no estimator is needed to know it.  The estimator is then run against that.

The estimator.  Exactly the scheme of Appendix D: hold a population of POP
states that cleared stages 1..k-1; to fill stage k, draw a parent uniformly with
replacement, propose a uniform digit, and keep the child when it passes.  The
stage's conditional probability is estimated by kept/proposed, and q-hat is the
product of the K stage ratios.  Each trial runs REPS independent replicates at
each of several populations.

What this shows.  Pooling the replicates at a given population gives an estimate
of E[q-hat], which is compared against the exact q.  Running several populations
shows how that difference behaves as the population grows -- the fixed-effort
bias is expected to fall like 1/POP, so the measured differences at POP = 10, 20,
40 and 80 bound what remains at the 2000 the filed study used.

Scope limits.  The toy has independent stages and a flat conditional probability,
where the real characteristic has neither; what carries over is the estimator's
own arithmetic, not the structure of the problem it is applied to.  The
populations here are far below the filed 2000, which is the point -- the bias is
largest where it is measurable -- but the extrapolation to 2000 is an
extrapolation.  This bounds the estimator's bias; it says nothing about whether
the filed study's inputs are right.

Protocol: python-message-pairs-v1 (JSON on stdin/stdout).
"""
import json
import sys
import hashlib
import math
import struct

BITS = 3                      # per-stage conditional probability 2^-BITS
STAGES = 4                    # exact answer q = 2^-(BITS*STAGES)
POPS = (10, 20, 40, 80)
REPS = 6                      # replicates per population per trial
MAXPROP = 1 << 14             # safety cap on proposals per stage


def run_once(rng_bytes, off, pop):
    """One replicate: return (log2 qhat, proposals used) or (None, used) if a stage stalls."""
    mask = (1 << BITS) - 1
    total = 0.0
    used = 0
    n = len(rng_bytes)
    for _ in range(STAGES):
        kept = 0
        proposed = 0
        while kept < pop and proposed < MAXPROP:
            b = rng_bytes[off % n]
            off += 1
            proposed += 1
            used += 1
            if (b & mask) == 0:
                kept += 1
        if kept < pop:
            return None, used, off
        total += math.log2(kept / proposed)
    return total, used, off


def main():
    request = json.load(sys.stdin)
    trials = []
    exact = -(BITS * STAGES)

    for t in request["trials"]:
        seed = t["seed"]
        raw = hashlib.shake_256(bytes.fromhex(seed) + b"splitbias").digest(1 << 16)
        off = 0
        observations = {"stages": STAGES, "bits_per_stage": BITS,
                        "exact_log2_q": exact, "reps_per_pop": REPS}
        for pop in POPS:
            acc = 0.0          # sum of qhat on the LINEAR scale, which is what E[qhat] means
            got = 0
            for _ in range(REPS):
                lg, _used, off = run_once(raw, off, pop)
                if lg is None:
                    continue
                acc += 2.0 ** (lg - exact)   # rescaled by the exact answer: unbiased => mean 1
                got += 1
            if got:
                observations["pop%d_reps" % pop] = got
                observations["pop%d_ratio_x1000" % pop] = round(1000.0 * acc / got)
        trials.append({
            "trial": t["trial"],
            "message_a_hex": None,
            "message_b_hex": None,
            "observations": observations,
        })

    json.dump({"schema_version": 1, "trials": trials}, sys.stdout)


if __name__ == "__main__":
    main()
