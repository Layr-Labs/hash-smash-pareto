# Three-round BLAKE3: generic memoryless rho, scalar cost 130.46

## 1. Claim

Target `blake3-r3-prefix-v1`: complete unkeyed BLAKE3 with exactly prefix rounds 0 through 2 in every compression, standard IV, flags and tree, full 256-bit digest. This package gives a generic Pollard-rho / Floyd collision search on the iteration map f(x) = H(enc32(x)). Time is strictly less than 2^130.46 target compressions. Memory is strictly less than 2^16 bytes, so the Pareto memory term max(0, memoryLog2Bytes - 20) is zero. Success probability exceeds 0.39 under one declared heuristic H_random. There is no preprocessing and no nonuniform advice.

## 2. Iteration map

For a 256-bit word x let enc(x) be its 32-byte little-endian encoding. H is the complete selected hash of that message: one chunk, one block, one root compression with CV = IV, counter 0, block_len 32, flags CHUNK_START|CHUNK_END|ROOT = 11, and exactly three prefix rounds. Define f(x) to be the 256-bit little-endian reading of the 32-byte digest. One evaluation of f is exactly one target compression plus at most 64 other word operations under collision-frontier-v5 with reference_operation_cost C = 638.

If f(t) = f(h) with t != h, then enc(t) and enc(h) are distinct messages whose complete digests agree on all 256 bits.

## 3. Algorithm (Floyd)

```
x0 <- uniform random 256-bit word
t <- f(x0); h <- f(f(x0)); n <- 3
while t != h:                       # phase 1
    t <- f(t); h <- f(f(h)); n <- n + 3
    if n > 3*2^128: halt failure
t <- x0                             # phase 2
loop:
    ft <- f(t); fh <- f(h)
    if ft == fh: exit loop
    t <- ft; h <- fh
if t == h: halt failure
output enc(t), enc(h)
```

Write L = mu + lambda for the first-repeat length. Phase 1 uses at most 3L evaluations and does not hit its cap when L <= 2^128. Phase 2 exits at j = mu - 1 with f(t) = f(h) = x_mu. If mu >= 1 then t != h and the outputs form a collision. Phase 2 uses at most 2L evaluations.

## 4. Success probability

Success iff L <= 2^128 and mu >= 1. Under H_random, with N = 2^256 and k = 2^128,

Pr[L <= k] >= 1 - exp(-k(k-1)/(2N)) = 1 - exp(-(1 - 2^-128)/2) >= 0.393469.

Given L = l, mu = 0 with probability at most 1/l, and Pr[L = l] <= l/N, so Pr[mu = 0 and L <= k] <= k/N = 2^-128. Hence success >= 0.393469 - 2^-128 > 0.39.

## 5. Time

Evaluations at most 5 * 2^128. Each is one compression plus at most 64 word operations at 1/638 each. Setup under 64 further operations. Total

T <= 5 * 2^128 * (1 + 64/638) + 64/638 < 5.5016 * 2^128 = 2^130.459 < 2^130.46.

All work is sequential. Parallel distinguished-point variants do not reduce total work and are not used.

## 6. Memory

The 16-word compression state, the 64-byte block buffer, the words x0, t, h, ft, fh, the counter, and the straight-line three-round compression code fit in under 2^16 bytes. No tables.

## 7. Evidence and limits

Experiment `rho-reduced` runs this Floyd algorithm on the 16-bit truncation of f and the organizer verifies each returned pair agrees on digest bits 0..15 with distinct messages. A local run gave 20 successful mask collisions matching the random-mapping prediction of about 800 evaluations. No 256-bit collision is observed or claimed. H_random is the standard random-mapping model, not a theorem about three-round BLAKE3. The attack is generic.

## 8. Pareto position

On the blake3 Pareto track with admitted rounds {3,4}, a three-round construction with normalized cost 130.46 (memory term 0) is a candidate frontier point whenever no cheaper three-round or any four-round package is already promoted.
