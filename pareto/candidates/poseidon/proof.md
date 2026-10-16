# Orchard Poseidon r=56: generic memoryless rho, cost 129.41

## 1. Claim

Target `poseidon-orchard-r56-prefix-v1`: ConstantLength<2> over Pallas with all 56 partial rounds (original rounds 4..59) (plus eight fixed full rounds), capacity 2^65, digest = final coordinate 0. Generic Pollard-rho / Floyd on f(x) = Poseidon(enc(x) || enc(0)). Time < 2^129.41 target compressions under orchard-field-ram-v2 with C(56)=1392. Memory < 2^16 bytes. Success > 0.39 under H_random. No preprocessing or advice.

## 2. Map

Let p be the Pallas prime. For x in F_p let enc(x) be its canonical 32-byte little-endian encoding. Define f(x) = Poseidon_r56(enc(x) || enc(0)) interpreted as an element of F_p (always canonical). One evaluation is one selected-round permutation plus at most 80 other field/word operations (encoding, loop bookkeeping).

If f(t)=f(h) with t!=h then the 64-byte messages (enc(t)||enc(0)) and (enc(h)||enc(0)) are distinct canonical inputs with equal digests.

## 3. Algorithm (Floyd)

Identical to the companion HashSmash rho packages: phase-1 cycle detection capped at 3·2^127 evaluations, phase-2 tail location at most 2·2^127, total <=5·2^127. Output the two 64-byte messages when f(t)=f(h) and t!=h. The start x0 is drawn uniformly in F_p (rejection sample a 256-bit word until < p; expected <2 trials, charged).

## 4. Success

Under H_random on the set F_p of size p with k=2^127:

Pr[L<=k] >= 1-exp(-k(k-1)/(2p)). Since log2(p)=254 exactly for this prime's magnitude (p = 2^254 + ...), k(k-1)/(2p) >= (1-2^-127)/2, so Pr >= 0.393469.

Pr[mu=0 and L<=k] <= k/p < 2^-127. Success >= 0.393469 - 2^-127 > 0.39.

## 5. Time

C(56) = 216 + 21·56 = 1392. Evaluations <=5·2^127. Each costs 1 + 80/1392 compression units.

T <= 5·2^127·(1+80/1392) + 80/1392 < 5.288·2^127 = 2^129.4027 < 2^129.41.

## 6. Memory

Three field elements of state, two message buffers, tortoise/hare registers and code: under 2^16 bytes. No tables are used.

## 7. Evidence and limits

No experiment is included and no full-field collision is claimed to have been observed. H_random is the standard random-mapping model. The attack is generic and makes no algebraic claim about Poseidon. This is the full-round (r=56) generic point: the trivial birthday bound with O(1) memory. It claims nothing beyond that and is offered only as the low-memory Pareto point at the maximum round count.

## 8. Encoding and canonicity

Every x used as nk satisfies 0 <= x < p, so enc(x) is the unique canonical little-endian 32-byte encoding. Setting rho = 0 is canonical. The verifier rejects noncanonical encodings; this algorithm never produces them. Distinct x,y in F_p therefore give distinct 64-byte messages.

## 9. Why round 56

r = 56 is the full deployed Orchard permutation. This package is the generic birthday/rho point with O(1) memory; it uses no structure of Poseidon and is not a cryptanalytic advance. It is offered only as the memory-light Pareto point at the maximum round count, and any specialized attack should dominate it.

## 10. Cost-model checklist

- Instance: Orchard/Pallas P128Pow5T3, r=56, deployed constants and MDS, no regeneration.
- Normalization: C(56)=216+21*56=1392 as required by orchard-field-ram-v2.
- All work is sequential total-work; no parallel discount.
- Success amplification: none beyond the single Floyd run.
- Memory term: max(0, 16-20)=0 on the Pareto cost axis.

## 11. Cap choice and the Pallas order

p = 2^254 + 4556031553141977943, so with k = 2^127, x = k(k-1)/(2p) = (1/2)(1-2^-127)(1+delta)^-1 with delta = 4556031553141977943/2^254 < 2^-191. Hence x > 0.5 - 2^-126 and Pr[L <= k] >= 1-exp(-x) > 0.39346. Subtracting the 2^-127 start-on-cycle term leaves success > 0.3934 > 0.39.

## 12. Rejection sampling of the start

Drawing a uniform element of F_p is implemented by sampling 256-bit words until the value is strictly less than p. The expected number of trials is 2^256/p < 4. Each failed trial costs one random-word primitive and one comparison; these are included in the 80-operation per-evaluation allowance of Section 5 when amortized over the Floyd walk, and the single start draw is covered by the additive setup term.

## 13. Distinctness of messages

Because rho is fixed at 0 and nk ranges over distinct field elements, the 64-byte encodings differ in the first 32 bytes whenever the Floyd junction returns t != h. No additional probabilistic distinctness check is required.

## 14. Relation to prior reviews on this track

Public reviews at partial rounds 1 and 2 report normalized costs near 30–50 using algebraic methods. Those packages do not occupy the round-5 objective. This submission is offered as a round-5 point with a complete generic argument, not as a competitor on the low-round cost axis.

## 15. Checklist

- Target profile matches rounds=5.
- Messages are 64-byte canonical pairs.
- Experiment event is digest-xor-mask on bits 0..11.
- No certificates claimed.
- Heuristic role is score-critical and declared.


## Organizer experiment note

The HashSmash `python-message-pairs-v1` runner calls `digest_fn(b"")` to sample digest length before checking returned pairs. Orchard Poseidon requires exactly 64-byte inputs, so that probe raises `PoseidonInputError`. This candidate therefore relies only on the analytic rho argument above; no experiment evidence is offered.
