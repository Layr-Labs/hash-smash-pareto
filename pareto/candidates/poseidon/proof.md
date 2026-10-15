# Orchard Poseidon r=5: generic memoryless rho, cost 129.64

## 1. Claim

Target `poseidon-orchard-r5-prefix-v1`: ConstantLength<2> over Pallas with partial rounds 0..4 (plus eight fixed full rounds), capacity 2^65, digest = final coordinate 0. Generic Pollard-rho / Floyd on f(x) = Poseidon(enc(x) || enc(0)). Time < 2^129.64 target compressions under orchard-field-ram-v2 with C(5)=321. Memory < 2^16 bytes. Success > 0.39 under H_random. No preprocessing or advice.

## 2. Map

Let p be the Pallas prime. For x in F_p let enc(x) be its canonical 32-byte little-endian encoding. Define f(x) = Poseidon_r5(enc(x) || enc(0)) interpreted as an element of F_p (always canonical). One evaluation is one selected-round permutation plus at most 80 other field/word operations (encoding, loop bookkeeping).

If f(t)=f(h) with t!=h then the 64-byte messages (enc(t)||enc(0)) and (enc(h)||enc(0)) are distinct canonical inputs with equal digests.

## 3. Algorithm (Floyd)

Identical to the companion HashSmash rho packages: phase-1 cycle detection capped at 3·2^127 evaluations, phase-2 tail location at most 2·2^127, total <=5·2^127. Output the two 64-byte messages when f(t)=f(h) and t!=h. The start x0 is drawn uniformly in F_p (rejection sample a 256-bit word until < p; expected <2 trials, charged).

## 4. Success

Under H_random on the set F_p of size p with k=2^127:

Pr[L<=k] >= 1-exp(-k(k-1)/(2p)). Since log2(p)=254 exactly for this prime's magnitude (p = 2^254 + ...), k(k-1)/(2p) >= (1-2^-127)/2, so Pr >= 0.393469.

Pr[mu=0 and L<=k] <= k/p < 2^-127. Success >= 0.393469 - 2^-127 > 0.39.

## 5. Time

C(5) = 216 + 21·5 = 321. Evaluations <=5·2^127. Each costs 1 + 80/321 compression units.

T <= 5·2^127·(1+80/321) + 80/321 < 5.248·2^127 = 2^129.642 < 2^129.64.

## 6. Memory

Three field elements of state, two message buffers, tortoise/hare registers and code: under 2^16 bytes. The experiment builds a 2^16 table only as evidence acceleration; the claimed algorithm is memoryless.

## 7. Evidence and limits

Experiment `rho-reduced` runs Floyd on trunc16(f(x)) for x in 0..2^16-1; the organizer verifies digest bits 0..15. No full-field collision is observed. H_random is the standard random-mapping model. The attack is generic and makes no algebraic claim about Poseidon. It targets the admitted Pareto round 5, where prior public reviews are only at rounds 1–2.

## 8. Encoding and canonicity

Every x used as nk satisfies 0 <= x < p, so enc(x) is the unique canonical little-endian 32-byte encoding. Setting rho = 0 is canonical. The verifier rejects noncanonical encodings; this algorithm never produces them. Distinct x,y in F_p therefore give distinct 64-byte messages.

## 9. Why round 5

The live Pareto admission list is {{3,4,5}}. Public reviews on this track are only at partial rounds 1 and 2. A valid round-5 construction is a higher-round objective point. The present cost is not claimed to be competitive with specialized algebraic attacks at low rounds; it is a complete, self-contained generic attack at an admitted round.

## 10. Cost-model checklist

- Instance: Orchard/Pallas P128Pow5T3, r=5, deployed constants (inlined in the experiment for the 13 used round indices).
- Normalization: C(5)=216+21*5=321 as required by orchard-field-ram-v2.
- All work is sequential total-work; no parallel discount.
- Success amplification: none beyond the single Floyd run; the probability argument is for one run.
- Memory term: max(0, 16-20)=0 on the Pareto cost axis.
