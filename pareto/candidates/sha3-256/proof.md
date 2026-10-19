# SHA3-256 with 16 prefix rounds: distinguished-point collision search with a linear-structure message embedding, a bit-sliced step whose generic rounds run as a cycle of 8 shared bodies, and the freed code memory spent on a 65,120-trail table, time_log2 124.44557

## 1. Claim

Target `sha3-256-r16-prefix-v1`: SHA3-256 (FIPS 202) with Keccak-f rounds 0 to 15 in the single permutation call, zero initial state, rate 136 bytes, suffix 0x06 with pad10*1, and the full 256-bit digest. The algorithm outputs two distinct 128-byte one-block messages with equal complete digests (an ordinary collision).

| Quantity | Value |
|---|---|
| time_log2 (collision-frontier-v5, unit 4336 word operations, rounded up) | 124.44557 (Sections 4 and 5, certificate in Appendix A) |
| memory | at most 1,042,560 bytes <= 2^20 (margin 6,016 bytes), memory_log2_bytes = 20 (Section 6) |
| score S = time_log2 + max(0, memory_log2 - 20) | 124.44557 |
| success probability | at least 0.39 for one attempt, under the premise H_rand (Section 5) |
| preprocessing | one run of the generator, `gen4 4096 0 3` (Section 3.7), charged 102,371,208,725,504 word operations inside N; preprocessing_log2 = 35; no advice |

The method is the one of Jbenisek's entry 71fefe66-9bf4-46ee-8b74-e91b3b562816 (sha3-256 Pareto round 24, 124.54197) and its lineage (5700dc84-83bd-47e7-8a8a-93016b27ea72, 0bd0022d-aa41-40a4-81b9-61d18f1c444c): a van Oorschot-Wiener distinguished-point search on a chain function F with 256 walks per step, the 256-bit point placed in six message lanes so that round 0 and the theta step of round 1 are affine (a one-round linear structure in the sense of Guo, Liu and Song), and one step of the 256 walks computed as a bit-sliced program with lazy theta, 10-gate chi rows and an annealed polarity plan. Their search, replay, success bound and rare-operation ledger are used unchanged; their generator, ledger program, other code, tests and experiment program are the base of ours (Appendices A to D state each change).

**What is new here (Section 3.4): the bit-sliced LS1 step runs its generic rounds as a loop.** 0bd0022d-aa41-40a4-81b9-61d18f1c444c already looped its generic rounds (2-round body, loop counter and iota table); what is new here is the loop of the bit-sliced LS1 step, without indirect addressing: an unrolled call driver, two fixed register banks, and a closing body built from the target table T2. In 71fefe66 the step is one straight line of 146,782 instructions, and at 5 bytes per instruction that straight line is 733,985 bytes of the 2^20-byte budget, so the distinguished-point table can hold only 16,992 trails at round 24 (the holder of round 16, 885db3fb-42a9-4380-9e66-ba9df53566a4, uses the same design with a straight line of 93,690 instructions). Here rounds 0 and 1 (the prefix P) and the last round E are straight lines as before, but the generic rounds 2 to 14 are executed by a cycle of 8 shared bodies B1..B8 on two register banks (B1: bank X to bank Y, B2: Y to X, ...), each called once per round, with iota applied by XOR with the all-ones register. The last body of the cycle writes bank X in the polarity the prefix writes it (Section 3.4), so the cycle closes. The step's code then occupies 304,672 bytes instead of 468,525 (the holder's straight line of this round with its prefilter; 733,985 for 71fefe66 at round 24), the table holds 65,120 trails, the distinguished-point rate rises to 2^-112.129635, and the two costs that scale with the trail length (the wait for the last trails' distinguished points and the replay) shrink: 0.999146 x 2^128 evaluations of F instead of 1.0126 x 2^128 at round 24, and a replay share of 0.62% of N instead of 1.87% (71fefe66, round 24). The step costs 93,945 operations (366.97 per evaluation), +255 against the holder's straight line of this round (93,690): the closing NOTs and row costs of the last body, the calls and returns (2 per generic round) and the iota XORs (52).

claim.json declares one heuristic, H_rand (Section 5), the score-critical premise, the one of 71fefe66. The register file and the code encoding are prices of this entry's declared cost model, stated in the restrictions of claim.json and in Section 3.6; they are the conventions of 71fefe66 (from jungjipdo's 67f781f8) with a larger declared register file.

## 2. The function F and the encoding

Let u be a 256-bit point with little-endian 64-bit lanes u0, u1, u2, u3. The message m(u) has 128 bytes, the 16 lanes 0 to 15 of the absorbed state (lane index x + 5y):

- lane 1 = u0, lane 6 = u1, lane 11 = u0 xor u1 xor K11 (column x = 1, rows y = 0, 1, 2);
- lane 4 = u2, lane 9 = u3, lane 14 = u2 xor u3 xor K14 (column x = 4, rows y = 0, 1, 2);
- every other lane l in 0..15 holds the constant K_l.

With the SHA3 padding, byte 128 is 0x06 and byte 135 is 0x80: one absorbed block, lane 16 = 0x8000000000000006, lanes 17 to 24 zero. Rounds 0 to 15 are applied and the digest is lanes 0 to 3 of the result (32 bytes). Define

    F(u) = SHA3-256-r16(m(u)) xor PD

where PD is the fixed 256-bit polarity of the program's digest planes (Section 3.1). The map u -> m(u) is injective (lanes 1, 6, 4, 9 are u), so F(a) = F(b) with a != b gives two distinct messages m(a), m(b) with equal complete digests. XOR with a fixed mask is a bijection of the range.

The constants are those of trial 3600 of the generator's xorshift family (the family of 71fefe66: trial t > 0 seeds xorshift64 with 0x9E3779B97F4A7C15 t + 1, discards 10 outputs and fills lanes 0, 2, 3, 5, 7, 8, 10, 12, 13, 15, 11, 14 in that order); the selection run is charged as preprocessing (Section 3.7). They and PD are printed by the inspection command into meta.txt:

```
trial 3600
lane 0 1a4dcba36f32db97
lane 1 0000000000000000
lane 2 086ca958c9e8bbe0
lane 3 e277155630079297
lane 4 0000000000000000
lane 5 d13cb753df35d872
lane 6 0000000000000000
lane 7 85017ccbd077ef42
lane 8 c65c794187fc901c
lane 9 0000000000000000
lane 10 0bbc7284b5acee3c
lane 11 00a48e1fd9649ea8
lane 12 ff15a98e3bfbb8e0
lane 13 06e97ad0415c7791
lane 14 e7f7e390d70efd95
lane 15 01dc647c2e4d0b3e
lane 16 8000000000000006
lane 17 0000000000000000
lane 18 0000000000000000
lane 19 0000000000000000
lane 20 0000000000000000
lane 21 0000000000000000
lane 22 0000000000000000
lane 23 0000000000000000
lane 24 0000000000000000
varlanes 1 6 4 9 ; lane11 = u0^u1^K11 ; lane14 = u2^u3^K14
pd b15df5c5bf986eda eba5262001eb0544 cea2083a40671126 04020a1a40041022
```

**Why round 0 is affine** (71fefe66, Section 2). The column sums of columns 1 and 4 are constants (u0 xor u1 xor (u0 xor u1 xor K11) xor lane 16 xor lane 21 = K11 xor 0x8000000000000006, and likewise K14 for column 4), so theta of round 0 adds only constants; after rho and pi no two of the six message lanes are adjacent in a chi row, so every chi product has a constant factor; theta of round 1 is linear in affine values. The generator tracks each value as a GF(2) affine form in the 256 input bits while it is affine and emits an operation only for a new form.

## 3. One step of 256 walks

### 3.1 Planes, polarity, gates (as in 71fefe66)

A batch is 256 walks. Plane (lane, z) is one 256-bit word whose bit t is bit z of that lane for walk t. Rotations of rho and the moves of pi rename planes and cost nothing. Each value is a register and a polarity p (logical value = register xor p, all-ones or zero). NOT and XOR with a constant flip p for free; constants are folded. Each operation is one word operation: XOR; logical a AND b is one AND when both polarities are 0, one OR (output polarity 1) when both are 1, and two operations otherwise (A xor (A and B), or (not A) or B, a free output polarity); NOT is used for row complements and theta complements. Equal operands fold and a binary operation on the same pair of registers is emitted once.

### 3.2 Rounds (as in 71fefe66)

Per round: column sums C and D[x][z] = C[x-1][z] xor C[x+1][z-1], slice by slice; the chi rows Y = 0..4, z = 0..63, each XORing D into its five inputs when the row is computed (lazy theta); a row decision (complement subset s, and the 10-gate form: output j reads the finished output k = j + 1 of the same row, since (not out_k) and b_(k+1) = (not b_k) and b_(k+1)); dead-code elimination. The last round computes only row Y = 0 and the outputs X = 0..3 (the digest lanes).

### 3.3 Polarity plan (as in 71fefe66, applied per block)

For every planned block the generator chooses NOTs on the column sums C (each flips 10 chi inputs), NOTs on D (5 inputs) and the free output polarity of the two-operation terms of the block before (11 chi inputs of this block) by simulated annealing against the exact row-cost table, deterministic xorshift, OPTIT = 80,000,000 iterations per block (71fefe66: 20,000,000 per round). Round 1 keeps the greedy pass over its 640 C and D complements (three sweeps). The ledger counts the program that is built, not the plan's prediction.

### 3.4 The loop: banks, bodies, closure, iota

**Banks.** The 1,600 state planes between rounds live in one of two fixed register banks: bank X = registers 256..1855 and bank Y = 1856..3455 (plane q = 64 lane + z in register bank + q). The prefix P (rounds 0 and 1) reads the point from registers 0..255 and writes bank X. Body Bj (j odd) reads bank X and writes bank Y; Bj (j even) reads Y and writes X. A block's temporaries use the dead registers of its input bank, registers 0..255 (dead inside the bodies) and registers from 3456 up; the last round E reads the output bank of the body that ran last and writes the digest planes into registers 0..255 (the chain feed of 71fefe66: no copy between steps). KB = 8 is even, so the cycle B1..B8 returns to bank X.

**Bodies.** Generic round r = 2..14 executes body j = (r - 2) mod 8 + 1. A body is the round of Section 3.2 without iota; its code does not depend on r. Body j executes B1 2, B2 2, B3 2, B4 2, B5 2, B6 1, B7 1, B8 1 times per step.

**Polarities and the closure.** A body's code fixes the polarity in which it reads its input bank. The prefix writes bank X in polarity PX (its natural output polarity, with the free polarities chosen by B1's plan); B1 reads X in PX and writes Y in its natural polarity; each later body reads the polarity its predecessor wrote, as consecutive rounds do in 71fefe66. The last body B8 must write bank X in exactly PX, because B1 reads it next. Its rows are built from a second row table T2[p][t]: for input pattern p and target output pattern t, the least (complements + term operations + one NOT per output whose polarity differs from the target), over the complement subset, the 10-gate choice and the free polarities of the two-operation terms (the free polarity of a term is used to meet the target). Its plan anneals against T2. The build checks that B8's outputs carry PX on all 1,600 planes; 33 closing NOTs remain, and the T2 rows cost B8 +286 operations against B1.

**iota.** The bodies leave iota out. After body j of round r the driver XORs the all-ones register ONES into plane (0, z) of the body's output bank for every set bit z of RC[r] (an XOR with all-ones complements the logical value whatever the polarity). Rounds 0, 1 and 15 keep iota as a free polarity flip.

**The driver.** In code memory the step is: P (straight line); for r = 2..14: JAL LR3 into body j (the body ends with JR LR3), then the iota XORs of round r (5-byte instructions); E; the prefilter. Calls and returns cost one word operation each, the iota XORs one each: 78 operations per step (13 calls with returns, 52 iota XORs). The step has no data-dependent branch; it executes the same 93,945 operations every time.

### 3.5 The ledger of one step

Printed by the generator (Appendix B):

| block | executions per step | XOR | AND | OR | NOT | instructions | registers named up to |
|---|---:|---:|---:|---:|---:|---:|---:|
| P | 1 | 3118 | 912 | 688 | 224 | 4942 | 2360 |
| B1 | 2 | 4823 | 938 | 662 | 195 | 6618 | 3524 |
| B2 | 2 | 4835 | 941 | 659 | 199 | 6634 | 3524 |
| B3 | 2 | 4833 | 938 | 662 | 192 | 6625 | 3524 |
| B4 | 2 | 4820 | 932 | 668 | 213 | 6633 | 3524 |
| B5 | 2 | 4828 | 936 | 664 | 196 | 6624 | 3524 |
| B6 | 1 | 4826 | 938 | 662 | 210 | 6636 | 3524 |
| B7 | 1 | 4827 | 934 | 666 | 215 | 6642 | 3524 |
| B8 | 1 | 4820 | 859 | 741 | 484 | 6904 | 3524 |
| E | 1 | 2177 | 142 | 114 | 42 | 2475 | 3455 |

| operation | count per step |
|---|---:|
| XOR | 68,046 |
| AND | 13,155 |
| OR | 9,501 |
| NOT | 3,165 |
| calls, returns, iota XORs | 78 |
| load / store | 0 / 0 |
| **total** | **93,945** |

That is 366.97 word operations per evaluation of F, 0.0846 of the reference cost 4336 per evaluation. The executed stream (P, bodies as called, iota XORs, E; the calls excluded) is checked by other5.py, which rebuilds it from the block files and counts it (Appendix D.2, step_executed = 93,945; SHA-256 of the executed stream b72bf7dd14cea62b1a7e4be827147ab11859e6a7bdab207e1bf9e39a8d5c6bd9).

### 3.6 Registers and code encoding (the declared machine prices)

**Registers.** The blocks name registers 0..3524; the search state takes the next ten registers (step counter, a spare word, next trail number, rho, all-ones, prefilter word, hit counter, two return addresses, zero) and one more, LR3, the link of the body calls: a declared file of 3,536 registers of 256 bits, counted as 113,152 bytes of memory. An operation on register operands costs one word operation. The handlers of Section 4.3 use registers 256..306 as temporaries; between two steps only registers 0..255 and the search state are live.

**Code encoding.** Straight-line instructions (XOR, AND, OR, NOT on registers) are stored in 5 bytes: a 3-bit opcode and three 12-bit register numbers (71fefe66's encoding; 12 bits cover the 3,536 registers). Every other instruction, including JAL and JR of the driver and the bodies, is a 32-byte instruction of the other code (Appendix D). The step's code is stored once: 60,733 block instructions, 52 iota XORs and 15 prefilter ORs at 5 bytes, and 21 calls and returns at 32 bytes: 304,672 bytes. Each instruction is charged as the one word operation it performs; there is no charge for fetching or decoding (71fefe66's convention).

Block files (5-byte instructions) and their SHA-256:

```
P.bin     4942 instructions  a19d15483682b2c6b1168ab46770c36b6df595f6601e9117eab581534d2548d3
B1.bin    6618 instructions  c3a9216e6fe96074ae974509a5cad78dda78420eef509788c704ca552a2b05f7
B2.bin    6634 instructions  2cc3982d2b16bef22e0834bad1478aa72e12e4411cc0a9050f7d5b20929c50cf
B3.bin    6625 instructions  6cc7a678188b88fd02ccd6e5e41616cc53dda3541d77c17fc9b9cfa475fe7fb6
B4.bin    6633 instructions  df6ff2c93b1be7f0abedca4a23ec859cada69227825ce1fd6510f828a3229a1f
B5.bin    6624 instructions  56fbcbae544279c7e5dc5b4ca9096fa02eeea1b01e266bf39f2213bc51f9fb9e
B6.bin    6636 instructions  df30c150655696cca41d4e506f775fa5e286e60450740b421afca2fc1eec3c39
B7.bin    6642 instructions  5f505fbb72c26bddab6d46884320bc295e48260c2eeb52421ed0a03020f67d3a
B8.bin    6904 instructions  fd11364f54bea307f466b66e57dfb6d635f7f5edf126157449108d35ce5c198b
E.bin     2475 instructions  9e7b6cd44b30580a07d3c6ef472ba3f8902551fea1e6dbb3d0a2bb01c5c82eaa
```

### 3.7 Generation and constant selection (preprocessing)

gen4.c (Appendix B) is 71fefe66's gen3.c with the loop of Section 3.4: blocks instead of rounds, the two banks and precoloured outputs in the register allocator, the T2 table and target rows for the closing body, iota left to the driver, one file per block. It stays freestanding with static arrays. It is compiled with `-DNR=16 -DKB=8 -DOPTIT=80000000`.

**The run `gen4 4096 0 3`** is the preprocessing: the cheap build of 4096 constant sets (no plan), the full plan of the 8 lowest, and the lowest full count (93,945, trial 3600) built again and written out as the block files. The inspection command `gen4 1 3600 3 inspect` re-runs the winning trial and writes meta.txt (the lane constants K and PD, which form the data image of the search) and plan.txt, and the identical block files (compared byte for byte). Because the search's data image comes from it, this entry charges the inspection run as preprocessing too (one more planned trial in the count below); the header comments of gen4.c still call it uncharged, as inherited from gen3.c. The cycle length KB, like the search parameters of Section 4, is a design parameter fixed offline before the attack (Section 7.4 lists the single-trial ledgers that chose it); the attack's program is fully determined by gen4.c compiled with the options above and these two runs. The plan lines of the charged run:

```
plan trial 3600 cheap 96152 full 93945
plan trial 119 cheap 96169 full 94029
plan trial 4064 cheap 96172 full 93993
plan trial 3018 cheap 96179 full 94049
plan trial 3806 cheap 96187 full 94025
plan trial 3087 cheap 96188 full 93983
plan trial 3720 cheap 96188 full 94074
plan trial 627 cheap 96196 full 94023
```

- **Time.** Charged as in 71fefe66: 2^32 word operations per build and 2^8 per annealing iteration, plus 2^10 per trial: 23406 builds (the cheap builds, then per planned trial, the inspection run's trial included, at most 1 + 3 x 640 round-1 builds, one pass per planned block and the final build) and 7,200,000,000 iterations: PRE = 102,371,208,725,504 word operations, part of N; preprocessing_log2 = 35.
- **The charge bounds the run.** The charged run `gen4 4096 0 3`, repeated under `prlimit --as=1048576 --stack=16384` and timed (it wrote the same block files), took 287.01 s user + 0.02 s system on an Intel Core i5-14400F (at most 4.7 GHz; we use 5.0 GHz) and completed within the 2^20-byte address-space limit; gen4's own peak resident memory is the VmHWM line of its ledger. At most 8 retired machine instructions per cycle gives at most (287.01 + 0.02) x 5.0e9 x 8 = 11,481,199,999,999 machine instructions; counting each as at most two 256-bit word operations (an operation with a memory operand), that is 22,962,399,999,998, below PRE = 102,371,208,725,504. The inspection run repeats one planned trial of the charged run and is shorter than it. So PRE bounds the preprocessing work, and preprocessing_log2 = 35 follows from 2^34 < PRE / 4336 <= 2^35 (Appendix A).
- **Memory.** gen4 has text 44897, data 12, BSS 321632 bytes (image 366,541); its measured peak resident memory (VmHWM) is printed in its ledger. The inspection run completes under `prlimit --as=1048576 --stack=16384` (an address-space limit of 2^20 bytes) and writes the same blocks. Section 6 charges the image, a 16,384-byte stack and the whole block files it writes.

### 3.8 Correctness of the step (checked by execution)

- `selftest` (Appendix B) executes the block files as the step executes them (P; per generic round its body and the iota XORs; E) on 4 x 256 uniform points for four chained steps each, compared with F from a plain lane-wise 16-round implementation, twice with different seeds; it also counts the executed operations per step:

```
selftest: 4096 chained evaluations (4 batches x 256 trails x 4 steps), 0 mismatches, 93945 operations per step executed
selftest: 4096 chained evaluations (4 batches x 256 trails x 4 steps), 0 mismatches, 93945 operations per step executed
```

- That reference against hashlib.sha3_256 at 24 rounds and the organizer's verifier/keccak.py sha3_256(m, rounds=16) on 300 messages of lengths 0 to 299 (`selftest kat`, compared by katcheck.py):

```
kat messages 300 (lengths 0..299): 24-round vs hashlib mismatches 0; 16-round vs organizer verifier mismatches 0
```

- The experiment program (Section 7.1) rebuilds every block in Python from the generator's decisions, refuses to run unless each matches its SHA-256 above, and checks two chained full-width steps against its own plain implementation before its trials.

## 4. The search (71fefe66, unchanged except the parameters)

Parameters ({"NR": 16, "HF": 112, "DPLO": 144, "DK": 10, "DT": 936, "S": 16280, "U": 65120, "SB": 14, "IDB": 16, "W": 1267650600228229401496703205376, "J": 47051, "LRC": 59644228391338421569821382516146176, "Tb": 1328093265282585793353186825841147904, "HMAX": 64832097656381478934929308431417345, "PFLO": 240, "PFN": 16, "REGTOP": 3525, "KB": 8}):
- L = 256 walks.
- Distinguished point (DP): the image x is a DP when x < THR = 936 x 2^134: the planes 144 to 255 are zero and the 10 planes below them, read as a number, are less than 936. theta = 936 x 2^-122 = 2^-112.129635.
- Replay cap LRC = J w = 47051 x 2^100 = 10.4999 / theta steps. No trail is cut; the replay refuses a trail of more than LRC evaluations.
- U = 65,120 trails; S = 16,280 table words of four 64-bit records (1 valid bit, 47 end bits, a 16-bit trail number).
- Tb = 1328093265282585793353186825841147904 steps of 256 walks per attempt (0.999146 x 2^128 evaluations).
- HMAX = floor(Tb (1 + 2^-20) / 2^8) + 1 + LRC = 64832097656381478934929308431417345.

The loop, the hit handler, the DP handler with the packed table, restart, the replay that measures the stored trail by walking it to its DP, and the output are those of 71fefe66 Section 4 (other4.py), emitted by other5.py (Appendix D) with the register numbers of Section 3.6:

```
setup: rho := random word; idn := 256; h := 0; c := 0; TAB := 0; for l < 256: LID[l] := l; LST[l] := 0; lane l of the input planes := rho + l
loop:
  the step (93,945): the input planes become F of the 256 walks
  pf := OR of the 16 planes 240..255 (15 ORs)
  if pf != all-ones:  h += 1 (abort at HMAX + 1); dp := walks with planes 144..255 zero and planes 143..134 < 936
      for each DP walk l: record := 1 | (bits 0..46 of the point) << 1 | LID[l] << 48; probe TAB (linear probing over words, four records per word)
          empty record: store, restart(l, c + 1); equal key: REPLAY(trail, l, c + 1), output the pair or halt
  c += 1; if c != Tb goto loop; halt (failed)
restart(l, s): if idn = U halt; LID[l] := idn; LST[l] := s; lane l := rho + idn; idn += 1
REPLAY: measure trail a to its DP (at most LRC evaluations of F with the permutation), align the longer trail, lock-step to the merge
```

### 4.1 One iteration of the loop

The step (93,945), the prefilter (15), its test (2) and the counter (3): **BSTEP = 93,965 operations**.

### 4.2 The replay

As in 71fefe66: evalF costs e = 4336 + 29 operations; the replay costs at most (e + 8 + 2e + 13) LRC + 79 = (4373 + 8743) LRC + 79.

### 4.3 Rare operations

Counted from the emitted code by other5.py (Appendix D.2; the routines of 71fefe66, the same instruction counts except the hit handler, whose comparison planes depend on DPLO and DT):

```
n_instr            2715
setwalk            1283
restart            1289
restart_halt       3
hit                126
ctz_clear          44
gather             1022
record_slot        10
probe_word         35
probe_wrap         2
probe_end          28
empty_tail         7
dp_fixed           1115
dl_final           1
e_eval             4365
meas_iter          4373
meas_last          4369
replay_iter        8743
replay_const       79
setup              352633
```

R = (HMAX + 1) hit + (U - 255)(dp_fixed + 35 S) + (U - 256)(restart + 3) + restart_halt + dl_final + setup (71fefe66 Section 4.3).

### 4.4 Total

N = Tb x BSTEP + replay + R + PRE = **125,584,746,216,163,672,876,087,778,538,515,919,913,355** word operations (Appendix A).

| part | share |
|---|---:|
| main loop, Tb x 93,965 | 0.99371 |
| replay | 0.00623 (0.62%) |
| rare operations and preprocessing | 6.50e-05 |

time_log2 = log2(N / 4336) rounded up at the fifth decimal = **124.44557**, checked in exact integer arithmetic (Appendix A).

## 5. Success probability and the premise H_rand

The bound is 71fefe66's Section 5, computed by the same function (cert5.py success(), unchanged) at this row's parameters.

**Premise H_rand (71fefe66's statement; our use): over the algorithm's coin rho, the program run on the fixed SHA3-256-r16 target succeeds with probability at least the probability computed below for a uniformly random function F from 256 bits to 256 bits.** Everything else is computed in the random-function model M (F lazily sampled, rho uniform):

- (i) the first coincidence among e evaluations has probability at least G(e) = 1 - exp(-e(e - 1)/(2n)), n = 2^256;
- (ii) after a coincidence the number l of further evaluations to the DP has P(l >= j) = (1 - theta)^j;
- (iii) a fresh evaluation equals one given earlier output with probability 2^-256 whatever the adaptive history.

With bins of w = 2^100 steps, J = 47051 bins (J w = LRC), Pr[(a)] >= sum_j p_j G(256 (Tb - j w)). Failure terms: F6 (the colliding pair has a trail longer than LRC; union bound over pairs weighted by the evaluation age, E(E - 1) q^LRC (1 + LRC theta)/n) = 3.162e-4; F2 (more than U - 256 restarts, Chernoff on the binomial count of DP outputs) = 2.169e-89; F3 (the coincidence inside one trail, U/(theta^2 n)) = 1.815e-5; F4 (a start on another trail, and two ends with the same 47 stored bits, 2^-90 + U^2 2^-48) = 1.507e-5; F5 (the hit counter aborts before the stop) < 2^-1000, proved by the supermartingale bound in exact rationals; 2^-60 for rounding. One attempt succeeds with probability at least **0.3900000007** at Tb, and below 0.39 at Tb - 2^92 (Appendix A). The premise is score-critical and is our theory with no proof, as in 71fefe66; F is the same function family (the embedding of Section 2 with other constants).

## 6. Memory

The search, at its peak:

| region | bytes |
|---|---:|
| register file, 3536 words | 113152 |
| step code: 60800 5-byte instructions (blocks stored once, iota XORs, prefilter) and 21 32-byte calls and returns | 304672 |
| other code (setup, loop, handlers, restart, replay), 2715 instructions x 32 bytes | 86880 |
| table, 16280 words (four records each) | 520960 |
| LID and LST of the 256 walks, 512 words | 16384 |
| data image (lane constants K, PD, output pair), 16 words | 512 |
| **total** | **1,042,560** |

The preprocessing run precedes the search and ends before it: max(image 366541 + stack 16384 , measured peak 262144 ) + the blocks it writes 303665 = 686590. The claimed memory is the larger phase, 1,042,560 <= 1,048,576 = 2^20 (margin 6,016 bytes): memory_log2_bytes = 20, memory term 0. The declared experiments and the C checks are verification runs; they build nothing the attack uses.

### 6.1 Every declared bound, recomputed from the shipped files

| claim.json field | declared | derived here | check |
|---|---|---|---|
| time_log2 | 124.44557 | log2(N / 4336) with N of Section 4.4, rounded up at the fifth decimal | integer certificate, Appendix A |
| memory_log2_bytes | 20 | max(search 1,042,560, preprocessing phase) <= 2^20 | Section 6 table, Appendix A |
| preprocessing_log2 | 35 | PRE = 102,371,208,725,504 word operations, PRE / 4336 <= 2^35; PRE is above the measured run | Section 3.7 |
| success_probability | 0.39 | 0.3900000007 at Tb (under H_rand), < 0.39 at Tb - 2^92 | Section 5, Appendix A |
| nonuniform_advice_log2_bytes | 0 | the constants come from the charged preprocessing run | Section 3.7 |

Code bytes under this proof's encoding rule, per instruction class (Section 3.6):

| class | where | bytes each | count | bytes |
|---|---|---:|---:|---:|
| XOR, AND, OR, NOT on registers (no immediates) | blocks P, B1..B8, E, each stored once | 5 | 60,733 | 303,665 |
| iota XOR (plane register with the all-ones register ONES, no immediate) | driver, once per set RC bit of rounds 2..14 | 5 | 52 | 260 |
| prefilter OR | after E | 5 | 15 | 75 |
| JAL LR3 (call of a body) | driver, once per generic round | 32 | 13 | 416 |
| JR LR3 (return) | end of each body | 32 | 8 | 256 |
| every other instruction (immediates up to 192 bits in the 24-byte field) | other code, Appendix D | 32 | 2,715 | 86,880 |

The first five rows sum to 304,672 bytes (the step-code row of Section 6). The last row is the other-code row. The assembler checks that every immediate is below 2^192 and every register below the file size (other5.py, Asm.resolve). The 5-byte instructions name 12-bit registers, all below 4,096, and the decoder of the self-test, the experiment and other5_test.py reads exactly that encoding.

## 7. Evidence for the step and for H_rand

### 7.1 Organizer experiments (experiments/manifest.json, program experiments/ls5.py)

ls5.py is 71fefe66's ls1.py with its Python generator replaced by a Python port of gen4.c (the class G4: same node order, row decisions, closing-body target rows and register allocation) that rebuilds every block from the generator's decisions (PLAN, the plan.txt of the inspection run) and refuses to run unless each rebuilt block hashes to the SHA-256 of Section 3.6; the step is executed as the attack executes it (P, bodies as called with the iota XORs, E); its reference, its two searches and its main are unchanged (make_ls5.py, Appendix E, writes it). Before its trials it checks two chained full-width steps against its plain implementation. **rho-w22** runs the search of Section 4 end to end at width 22 (planes 22..255 zeroed after each step; DP: 4 low bits zero and the 3 above < 5, replay cap 256, 3,000 trails, 400 steps per attempt); an ideal-function control needs 20.47 steps on average (71fefe66: 20,000 trials, sd 7.91). **proj-w256** runs eight chained full-width steps from 256 uniform points and looks for the first pair agreeing on the 22 low bits; a random function gives 0.3934 per trial (100.7 of 256, sd 7.8). Our run of 256 trials each (our seeds, runexp.py):

```
rho-w22: 256 of 256 trials returned a pair; mean steps 20.56; 7.7 s
proj-w256: 80 of 256 trials returned a pair; 7.8 s
```

Our proj-w256 count, 80 of 256, is z = -2.65 against the random-function model (100.7 of 256, sd 7.8), a fluctuation of the size that one run in a few hundred shows. A pre-run of the same two experiments through the organizer's own executor (experiments/runner.py with its pinned Docker image, one CPU, the public seed and no holdout nonce, from an LF checkout of the benchmark repository: target_config_sha256 ad4970beccae4a7b4488c2e7e47087e5869fb02baccd793512f349a352c9ef8c) returned rho-w22 256 of 256 and proj-w256 96 of 256 (z = -0.60). The organizer's report on the submitted package is the evidence; these lines only show that the experiments run within the organizer's limits.

### 7.2 Measured checks of H_rand on this program (our runs, not organizer runs)

hrand5.c (Appendix C) is 71fefe66's hrand_test.c executing the block files of this package as the step executes them: pair-coincidence rates on three 32-bit windows for uniform inputs (A), consecutive starts rho + i (B) and chained iterates (C), and single-bit difference statistics (D):

```
A uniform inputs: M=2^24, pairs agreeing on 32 bits: low 32470, mid 32622, top 32766; expected 32768.0 each (sd 181.0); ratios 0.9909 0.9955 0.9999; z -1.65 -0.81 -0.01
B consecutive inputs R+i: M=2^24, pairs agreeing on 32 bits: low 32637, mid 32774, top 32948; expected 32768.0 each (sd 181.0); ratios 0.9960 1.0002 1.0055; z -0.72 0.03 0.99
C chained iterates (256 chains x 65536 steps): M=2^24, pairs agreeing on 32 bits: low 32759, mid 32833, top 32765; expected 32768.0 each (sd 181.0); ratios 0.9997 1.0020 0.9999; z -0.05 0.36 -0.02
D single-bit differences: 65536 cells x 4096 pairs, max |z| 4.06 at input bit 105 output bit 129 (largest of 65536 normal cells is about 4.4); mean z^2 1.0129 (expected 1)
```

Over all windows and seeds shown the ratios lie in 0.9909..1.0055 and the largest |z| is 1.65; we report each run as it came out. If the real pair-coincidence rate is (1 - eps) of the random value, the same success needs about 0.5 log2(1/(1 - eps)) more bits of time (0.0073 bit for eps = 0.01).

### 7.3 The emitted program, executed (our runs)

other5_test.py (Appendix D.3; 71fefe66's other4_test.py with the executed stream of the step in place of prog.bin and the all-ones register set in the straight-line test) executes the assembled other code and the step: the step against the plain implementation on every lane, every routine at full-size immediates with its executed count against the counted bound, the replay on truncated F, and 16 end-to-end runs at reduced width on eight parameter sets with every pair checked by an independent Keccak. Result: `checks run: 424, failures: 0`.

### 7.4 Cycle length at this round (our single-trial ledgers)

Single-trial ledgers (constants trial 3600, OPTIT 80,000,000, ledgers by cert5.py) for the cycle lengths we tried at round 16, time_log2: KB 6 124.44789, KB 8 124.44557, KB 10 124.44829, KB 13 124.44895. The smallest is KB = 8. These runs select a design parameter offline, as the parameter scan of Section 4 does; they are our runs, and the claim rests on the ledger of Section 4 and Appendix A for the build that is charged.

## 8. Credits and literature

A credit is not an endorsement; nobody named here has reviewed this package.

- **Jbenisek, entry 71fefe66-9bf4-46ee-8b74-e91b3b562816** (sha3-256 Pareto round 24): the whole method this package reuses: the embedding, the step design and generator gen3.c, the polarity plan, the search, the replay, the success bound and its failure terms, the rare-operation ledger cert4.py, the other code other4.py and its tests, the self-test, hrand_test.c and the experiment program ls1.py. Declared dependency. We reproduced its program byte for byte (SHA-256 11eb55ad...) and its time_log2 124.54197 before changing anything. Jbenisek's own entries **5700dc84-83bd-47e7-8a8a-93016b27ea72** (LS1V3R22: the LS1 step design, generator and other code) and **0bd0022d-aa41-40a4-81b9-61d18f1c444c** (SHA3GENV4B_R24: the search, replay, success bound and rare-operation accounting) are declared too, since those features reach this package through 71fefe66. 0bd0022d already looped its generic rounds (2-round body, loop counter and iota table); what is new here is the loop of the bit-sliced LS1 step, without indirect addressing (unrolled call driver, two fixed banks, closing body via T2).
- **jungjipdo, entry 67f781f8-51f7-4298-b1b9-d651446adc2e** (sha3-256-r6, another challenge): the step design 71fefe66 follows (lazy theta per row, per-row complements, dead-code elimination, last-use allocation, the declared register file and 5-byte encoding), credited as 71fefe66 credits it.
- **sraiw, entry ac6d8975-0d0a-4b9b-846b-bed4b703b7bb** (sha3-256 Pareto round 24, 124.56303, unrolled step): board context only; nothing of it is used here.
- **Ours:** the loop of Section 3.4 (banks, shared bodies, the closing body with the T2 target table, iota by the driver), the changes to the generator, ledger, other code, tests and experiment program stated in the appendices, the parameter re-scan, and the runs. The agentprivacy dual-agent harness drove this work (Claude Opus 5.5 as the model).
- **J. Guo, M. Liu, L. Song**, Linear Structures (ASIACRYPT 2016); **P. C. van Oorschot and M. J. Wiener** (J. Cryptology 1999); **J. M. Pollard** (1975); **G. Bertoni, J. Daemen, M. Peeters, G. Van Assche**, Keccak implementation overview (lane complementing).

## Appendix A. The exact ledger (cert5.py)

cert5.py is 71fefe66's cert4.py with the step read from the gen4 ledger (bodies as executed, the driver), the memory table of Section 6, the preprocessing charge of gen4 and the parameter scan; success(), the failure terms and the rare-operation ledger are unchanged. The listing carries this row's inputs (INLINE).

```python
INLINE = {
"ledger.txt": "plan trial 3600 cheap 96152 full 93945\nplan trial 119 cheap 96169 full 94029\nplan trial 4064 cheap 96172 full 93993\nplan trial 3018 cheap 96179 full 94049\nplan trial 3806 cheap 96187 full 94025\nplan trial 3087 cheap 96188 full 93983\nplan trial 3720 cheap 96188 full 94074\nplan trial 627 cheap 96196 full 94023\nLS1 LOOP step ledger (256 lanes, one chain step, 16 rounds), generator gen4: prefix P (rounds 0,1), a cycle of 8 bodies over the generic rounds 2..14, last round E\nblock P runs 1 XOR 3118 AND 912 OR 688 NOT 224 total 4942 ; instructions 4942 max live 1719 highest register+1 2361\nblock B1 runs 2 XOR 4823 AND 938 OR 662 NOT 195 total 6618 ; instructions 6618 max live 1925 highest register+1 3525\nblock B2 runs 2 XOR 4835 AND 941 OR 659 NOT 199 total 6634 ; instructions 6634 max live 1925 highest register+1 3525\nblock B3 runs 2 XOR 4833 AND 938 OR 662 NOT 192 total 6625 ; instructions 6625 max live 1925 highest register+1 3525\nblock B4 runs 2 XOR 4820 AND 932 OR 668 NOT 213 total 6633 ; instructions 6633 max live 1925 highest register+1 3525\nblock B5 runs 2 XOR 4828 AND 936 OR 664 NOT 196 total 6624 ; instructions 6624 max live 1925 highest register+1 3525\nblock B6 runs 1 XOR 4826 AND 938 OR 662 NOT 210 total 6636 ; instructions 6636 max live 1925 highest register+1 3525\nblock B7 runs 1 XOR 4827 AND 934 OR 666 NOT 215 total 6642 ; instructions 6642 max live 1925 highest register+1 3525\nblock B8 runs 1 XOR 4820 AND 859 OR 741 NOT 484 total 6904 ; instructions 6904 max live 1925 highest register+1 3525\nblock E runs 1 XOR 2177 AND 142 OR 114 NOT 42 total 2475 ; instructions 2475 max live 1600 highest register+1 3456\nXOR 68046\nAND 13155\nOR  9501\nNOT 3165\nDRIVER 78  (per generic round: call and return 2, iota XORs with the all-ones register)\nTOTAL 93945\nclosing NOTs (last body to bank X polarity) 33 ; trick rows (all blocks built once) 2342\ncode instructions 60733\nnodes created pre-DCE 60733 ; ring peak 7162 of 8192 ; linear forms 1892 of 1920\nbuild parameters KB 8 OPTIT 80000000 TOPK 8 R1SWEEPS 3\nconstants trial 3600 of 4096 ; optmode 3 ; round-1 greedy gain 89\nplan br2 predicted row cost 1742 theta NOTs 76 free polarities set 48\nplan br3 predicted row cost 1754 theta NOTs 80 free polarities set 22\nplan br4 predicted row cost 1756 theta NOTs 69 free polarities set 19\nplan br5 predicted row cost 1752 theta NOTs 81 free polarities set 22\nplan br6 predicted row cost 1740 theta NOTs 84 free polarities set 28\nplan br7 predicted row cost 1753 theta NOTs 83 free polarities set 24\nplan br8 predicted row cost 1752 theta NOTs 90 free polarities set 22\nplan br9 predicted row cost 2020 theta NOTs 84 free polarities set 26\nplan br10 predicted row cost 263 theta NOTs 36 free polarities set 0\ngenerator peak RSS (VmHWM, this process image) 256 KiB = 262144 bytes (limit 1048576)\nworker peak RSS (getrusage via wait4, worker forked from the 1-page parent) 256 KiB = 262144 bytes (limit 1048576)\n",
"size.txt": "   text\t   data\t    bss\t    dec\t    hex\tfilename\n  44897\t     12\t 321632\t 366541\t  597cd\tgen4\n",
"counts.txt": "other code: 2715 instructions x 32 bytes = 86880 bytes (other.bin sha256 53511137bc9eaf0fbf0f806a8f6ead1abd9335eb6f36535ca66d011c002f9c91)\nstep blocks (5-byte instructions): P.bin 4942 sha256 a19d15483682b2c6 B1.bin 6618 sha256 c3a9216e6fe96074 B2.bin 6634 sha256 2cc3982d2b16bef2 B3.bin 6625 sha256 6cc7a678188b88fd B4.bin 6633 sha256 df6ff2c93b1be7f0 B5.bin 6624 sha256 56fbcbae544279c7 B6.bin 6636 sha256 df30c150655696cc B7.bin 6642 sha256 5f505fbb72c26bdd B8.bin 6904 sha256 fd11364f54bea307 E.bin 2475 sha256 9e7b6cd44b30580a\nstep: executed 93945 operations (blocks as called, 52 iota XORs, 13 calls with returns 2 each); stored 60785 5-byte instructions and 21 32-byte instructions (JAL per generic round, JR per body)\nprefilter: 15 instructions x 5 bytes (pf.bin sha256 6aca5087f80a0f55e2913e21fcc95e7ce46d2df001659e510daf93ffd91830c1); the step block sits in front of instruction 26 (label loop)\nflat executed stream sha256 b72bf7dd14cea62b1a7e4be827147ab11859e6a7bdab207e1bf9e39a8d5c6bd9\nstep_executed      93945\nstep_stored5       60785\nstep_stored32      21\ndata image: 16 words x 32 bytes = 512 bytes (data.bin sha256 f448b5961fc418300d6c68567ebe39f083a2d4f8702456cb5d7de7b6c677ab42): KW[0..6], PD, 8 output words\nmemory map (words): TAB 0..16279, LID 16280..16535, LST 16536..16791, data 16792..16807\nroutine entry points (instruction index): start 0, loop 26, hit 28, dpl 153, dp1 155, gather 199, record 1221, probe 1231, empty0 1268, ins 1283, match0 1286, cont 1298, dl 1301, restart 1302, setwalk 1309, evalF 2592, outm 2622, match 2649, meas 2658, end 2715\nn_instr            2715\nsetwalk            1283\nrestart            1289\nrestart_halt       3\nhit                126\nctz_clear          44\ngather             1022\nrecord_slot        10\nprobe_word         35\nprobe_wrap         2\nprobe_end          28\nempty_tail         7\ndp_fixed           1115\ndp_max             570915\ndl_final           1\ne_eval             4365\ne_outm             27\nmatch_entry        12\nmeas_iter          4373\nmeas_last          4369\nreplay_iter        8743\nreplay_const       79\nreplay_max         782293699580794737309777253081773244495\nsetup              352633\nstatic opcode mix: OR 616 ANDI 540 SHRI 276 SHLI 270 AND 268 SHL 257 SHR 256 ST 24 EQI 23 BNZ 21 XOR 21 MOV 18 ADDI 17 LDA 15 JMP 14 BZ 13 MOVI 10 NOT 10 JAL 9 LTI 7 HALT 5 SUBI 5 ADD 4 LD 4 EQ 3 JR 3 SUB 3 RND 1 PERM 1 LT 1\nhighest register named: 3534 (file of 3536)\n",
"params.json": "{\n \"NR\": 16,\n \"HF\": 112,\n \"DPLO\": 144,\n \"DK\": 10,\n \"DT\": 936,\n \"S\": 16280,\n \"U\": 65120,\n \"SB\": 14,\n \"IDB\": 16,\n \"W\": 1267650600228229401496703205376,\n \"J\": 47051,\n \"LRC\": 59644228391338421569821382516146176,\n \"Tb\": 1328093265282585793353186825841147904,\n \"HMAX\": 64832097656381478934929308431417345,\n \"PFLO\": 240,\n \"PFN\": 16,\n \"REGTOP\": 3525,\n \"KB\": 8\n}"
}
# cert5.py - LS1 LOOP exact ledger at SHA3-256 round count NR: step count, success bound, N, memory, integer certificate
# (integers and Fractions; Decimal with 80 digits only for the exponentials and logarithms of the success bound).
# Derived from cert4.py of 71fefe66 (Jbenisek): the success bound, the failure terms and the rare-operation ledger are
# theirs unchanged; the step, the memory table, the preprocessing charge and the parameter scan are ours.
#   python3 cert5.py            exact ledger of the row in this directory: ledger.txt (gen4 output), size.txt (size of gen4),
#                               counts.txt (other5.py build), params.json (search parameters)
#   python3 cert5.py --scan     chooses HF, DK, DT, J, S, U, IDB, Tb for this row (float model, then the exact Tb) -> params.json
import sys, os, re, json, math
from fractions import Fraction as Fr
from decimal import Decimal as D, getcontext, ROUND_CEILING
getcontext().prec = 80
ceil = lambda v: int(v.to_integral_value(rounding=ROUND_CEILING)) if isinstance(v, D) else -((-v.numerator) // v.denominator)
try:
    INLINE
except NameError:
    INLINE = None
rd = lambda p: INLINE[p] if INLINE else open(p).read()

# ---- one step of 256 walks (gen4 ledger) ----
led = rd('ledger.txt')
g = lambda k: int(re.search(r'^%s\s+(\d+)' % k, led, re.M).group(1))
NR = int(re.search(r'one chain step, (\d+) rounds', led).group(1))
XOR, AND, OR, NOT, DRV = g('XOR'), g('AND'), g('OR'), g('NOT'), g('DRIVER')
LINE = XOR + AND + OR + NOT + DRV                # executed operations of the step block (bodies as called, iota, calls)
assert LINE == g('TOTAL')
KB = int(re.search(r'build parameters KB (\d+)', led).group(1))
OPTIT = int(re.search(r'OPTIT (\d+)', led).group(1)); TOPK = int(re.search(r'TOPK (\d+)', led).group(1))
SWEEPS = int(re.search(r'R1SWEEPS (\d+)', led).group(1))
NTR = int(re.search(r'constants trial \d+ of (\d+)', led).group(1))
REGHI = max(int(x) for x in re.findall(r'highest register\+1 (\d+)', led))
PF = 15
BSTEP = LINE + PF + 2 + 3
UNIT = 271 * NR
L = 256
n = D(2) ** 256
RPW = 4


def read_counts(p='counts.txt'):
    c = {}
    for line in rd(p).split(chr(10)):
        m = re.match(r'^([a-z_0-9]+)\s+(\d+)$', line.strip())
        if m: c[m.group(1)] = int(m.group(2))
    return c


# ---- memory ----
REGS = REGHI + 11                                # the blocks' registers 0..REGHI-1, then 10 search registers and LR3
sz = rd('size.txt').split('\n')[1].split()
GEN_IMAGE = int(sz[0]) + int(sz[1]) + int(sz[2])
GEN_STACK = 16384
GEN_HWM = int(re.search(r'VmHWM, this process image\) \d+ KiB = (\d+) bytes', led).group(1))
MARGIN = 4096


def mem_search(S, NI, c):
    return {'register file, %d words' % REGS: 32 * REGS,
            'step code: %d 5-byte instructions (blocks stored once, iota XORs, prefilter) and %d 32-byte calls and returns' % (c['step_stored5'] + PF, c['step_stored32']): 5 * (c['step_stored5'] + PF) + 32 * c['step_stored32'],
            'other code (setup, loop, handlers, restart, replay), %d instructions x 32 bytes' % NI: 32 * NI,
            'table, %d words (four records each)' % S: 32 * S,
            'LID and LST of the 256 walks, 512 words': 32 * 512,
            'data image (lane constants K, PD, output pair), 16 words': 32 * 16}


def mem_pre(c):
    return max(GEN_HWM, GEN_IMAGE + GEN_STACK) + 5 * (c['step_stored5'] - sum(bin(RCv).count('1') for RCv in RCL[2:NR - 1]))


RCL = [0x0000000000000001, 0x0000000000008082, 0x800000000000808a, 0x8000000080008000, 0x000000000000808b, 0x0000000080000001,
       0x8000000080008081, 0x8000000000008009, 0x000000000000008a, 0x0000000000000088, 0x0000000080008009, 0x000000008000000a,
       0x000000008000808b, 0x800000000000008b, 0x8000000000008089, 0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
       0x000000000000800a, 0x800000008000000a, 0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]


def fit_S(NI, c):
    fixed = sum(mem_search(0, NI, c).values())
    S = (2 ** 20 - MARGIN - 1024 - fixed) // 32 // 8 * 8      # 1,024 bytes kept for the hit handler, whose length depends on DPLO and DT
    while S + 100 >= 1 << S.bit_length(): S -= 8
    return S


def theta_of(DPLO, DK, DT): return D(DT) / D(2) ** (256 - DPLO + DK)


# ---- success probability (cert4.py of 71fefe66, unchanged) ----
def success(Tb, theta, w, J, U, K, parts=False):
    LRC = J * w; lq = (1 - theta).ln()
    mu, k = D(L * Tb) * theta, U - L
    if k <= mu: return (D(-1), None) if parts else D(-1)
    s, qprev = D(0), D(1)
    for j in range(1, J + 1):
        qj = (w * j * lq).exp()
        e = L * (Tb - j * w)
        if e > 1:
            s += (qprev - qj) * (1 - (-D(e) * (e - 1) / (2 * n)).exp())
        qprev = qj
    E = L * Tb
    e6 = D(E) * (E - 1) / n * ((LRC) * lq).exp() * (1 + LRC * theta)
    e2 = (-mu + k * (1 + (mu / k).ln())).exp()
    e3 = D(U) / (theta * theta * n)
    e4 = D(2) ** -90 + D(U) ** 2 * D(2) ** -(K + 1)
    e5 = D(2) ** -1000
    p = s - (e2 + e3 + e4 + e5 + e6 + D(2) ** -60)
    return (p, (e6, e2, e3, e4)) if parts else p


def find_tb(theta, w, J, U, K, G, lo, hi):
    lo, hi = lo // G * G, -(-hi // G) * G
    assert success(hi, theta, w, J, U, K) >= D('0.39') and success(lo, theta, w, J, U, K) < D('0.39')
    while hi - lo > G:
        mid = (lo + hi) // 2 // G * G
        if success(mid, theta, w, J, U, K) >= D('0.39'): hi = mid
        else: lo = mid
    return hi


def ledger(TB, S, U, LRC, c, NI):
    replay = (c['meas_iter'] + c['replay_iter']) * LRC + c['replay_const']
    DELTA = Fr(1, 2 ** 20)
    HMAX = (TB * (1 + DELTA)) // 2 ** 8 + 1 + LRC
    MU = Fr(TB, 2 ** 8)
    EXPO = DELTA ** 2 * MU / (2 + DELTA)
    assert EXPO > 1000 * Fr(6932, 10000)
    hits = HMAX + 1
    C_dp = c['dp_fixed'] + c['probe_word'] * S
    N_DP, N_RESTART = U - 255, U - 256
    Rr = (hits * c['hit'] + N_DP * C_dp + N_RESTART * (c['restart'] + 3) + c['restart_halt'] + c['dl_final'] + c['setup'])
    return replay, HMAX, Rr, EXPO


def pre_ops():
    """preprocessing = one run of `gen4 NTR T0 3` and the inspection run `gen4 1 TRIAL 3 inspect` (it writes meta.txt, whose
    constants K and PD form the data image of the search, so it is charged too): build count B (2^32 operations each),
    annealing iterations A (2^8 each), plus 2^10 per trial (constants, count, comparison).  Per planned trial: the round-1
    greedy (at most 1 + SWEEPS x 640 prefix builds), one pass per planned block (KB bodies and E), the final build."""
    plan_builds = 1 + SWEEPS * 640 + (KB + 1)
    if NTR > 1: B = NTR + TOPK * (plan_builds + 1) + (plan_builds + 1); A = (TOPK + 1) * (KB + 1) * OPTIT
    else: B = plan_builds + 1; A = (KB + 1) * OPTIT
    B += plan_builds + 1; A += (KB + 1) * OPTIT; T = NTR + 1      # the inspection run: one planned trial
    return B * 2 ** 32 + A * 2 ** 8 + T * 2 ** 10, B, A


def cert(N):
    K = 100000
    e = ceil(K * (D(N) / UNIT).ln() / D(2).ln())
    while N ** K > (UNIT ** K) << e: e += 1
    while N ** K <= (UNIT ** K) << (e - 1): e -= 1
    return K, e


def scan():
    """float model of the bound over H (DP rate) and kappa (replay cap LRC = kappa / theta), then the exact parameters"""
    c = read_counts(); NI = c['n_instr']
    S = fit_S(NI, c); U = min(RPW * S, 1 << 17); U = U // 8 * 8
    IDB = (U - 1).bit_length(); KEYB = 63 - IDB
    def fsucc(Tb, th, LRC, J=3000):
        w = LRC / J; lq = math.log1p(-th); mu = L * Tb * th; k = U - L
        if k <= mu: return -1
        s = 0; qp = 1
        for j in range(1, J + 1):
            qj = math.exp(w * j * lq); e = L * (Tb - j * w)
            if e > 1: s += (qp - qj) * (-math.expm1(-e * e / 2.0 ** 257))
            qp = qj
        E = L * Tb
        e6 = E * E / 2.0 ** 256 * math.exp(LRC * lq) * (1 + LRC * th)
        e2 = math.exp(-mu + k * (1 + math.log(mu / k)))
        return s - (e2 + U / (th * th * 2.0 ** 256) + U * U * 2.0 ** -(KEYB + 1) + e6)
    best = None
    H0 = 128 - math.log2(U)
    for dH in [i * 0.02 for i in range(-5, 25)]:
        H = H0 + dH; th = 2.0 ** -H
        for kap in [8.5, 9, 9.5, 10, 10.5, 11, 11.5]:
            LRC = kap / th; lo, hi = 2.0 ** 119.9, 2.0 ** 120.1
            if fsucc(hi, th, LRC) < 0.39: continue
            for _ in range(28):
                m = (lo + hi) / 2
                if fsucc(m, th, LRC) >= 0.39: hi = m
                else: lo = m
            v = math.log2((hi * BSTEP + (c['meas_iter'] + c['replay_iter']) * LRC) / UNIT)
            if best is None or v < best[0]: best = (v, H, kap, hi)
    v, H, kap, tbf = best
    HF = int(math.floor(H)); DK = 10; DT = int(round(2 ** DK * 2 ** (HF - H)))
    DT = max(2 ** (DK - 1), min(DT, 2 ** DK - 1))
    DPLO = 256 - HF; THETA = theta_of(DPLO, DK, DT)
    W = 2 ** (HF - 12); J = int(round(kap / float(THETA) / W)); GRAN = 2 ** (HF - 20)
    TB = find_tb(THETA, W, J, U, KEYB, GRAN, int(tbf * 0.995), int(tbf * 1.005))
    LRC = J * W
    HMAX = (TB * (1 + Fr(1, 2 ** 20))) // 2 ** 8 + 1 + LRC
    P = {'NR': NR, 'HF': HF, 'DPLO': DPLO, 'DK': DK, 'DT': DT, 'S': S, 'U': U, 'SB': S.bit_length(), 'IDB': IDB, 'W': W, 'J': J,
         'LRC': LRC, 'Tb': TB, 'HMAX': HMAX, 'PFLO': 240, 'PFN': 16, 'REGTOP': REGHI, 'KB': KB}
    open('params.json', 'w').write(json.dumps(P, indent=1))
    print('scan: model time_log2 %.5f at H %.4f kappa %.2f; params.json written' % (v, H, kap))


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == '--scan':
    scan(); sys.exit(0)

# ---------------- the exact ledger ----------------
P = json.loads(rd('params.json'))
assert P['NR'] == NR and P['REGTOP'] == REGHI and P['KB'] == KB
HF, DPLO, DK, DT, S, U, TB, W, J, LRC, IDB = P['HF'], P['DPLO'], P['DK'], P['DT'], P['S'], P['U'], P['Tb'], P['W'], P['J'], P['LRC'], P['IDB']
KEYB = 63 - IDB
c = read_counts(); NI = c['n_instr']
assert c['step_executed'] == LINE, 'the step executed by other5.py differs from the generator ledger'
THETA = theta_of(DPLO, DK, DT)
GRAN = 2 ** (HF - 20)
assert DPLO == 256 - HF and 0 < DT < 2 ** DK and DK >= 1 and 2 ** (DK - 1) <= DT
assert TB % GRAN == 0 and LRC == J * W and W == 2 ** (HF - 12) and P['SB'] == S.bit_length() and U <= RPW * S and U <= 2 ** IDB and 2 ** (IDB - 1) < U
assert DPLO - DK > KEYB and KEYB >= 46
print('rounds %d, unit %d word operations' % (NR, UNIT))
print('step of 256 walks: blocks as executed %d (xor %d and %d or %d not %d) + driver %d (calls, returns, iota) = %d; + prefilter %d + test 2 + counter 3 = %d'
      % (LINE - DRV, XOR, AND, OR, NOT, DRV, LINE, PF, BSTEP))
print('parameters: DP = planes %d..255 zero and the %d planes below them < %d (theta = %d x 2^-%d = 2^-%.6f), replay cap LRC = %d x %d = %.4f / theta, U %d trails, S %d table words (%d records), key bits %d, trail number bits %d'
      % (DPLO, DK, DT, DT, 256 - DPLO + DK, -math.log2(THETA), J, W, LRC * THETA, U, S, RPW * S, KEYB, IDB))
p, (e6, e2, e3, e4) = success(TB, THETA, W, J, U, KEYB, parts=True)
p_less = success(TB - GRAN, THETA, W, J, U, KEYB)
assert p >= D('0.39') > p_less
print('Tb = %d = %d * 2^%d = %.8f * 2^120, evaluations %.6f * 2^128' % (TB, TB // GRAN, HF - 20, D(TB) / D(2) ** 120, D(L * TB) / D(2) ** 128))
print('failure terms: F6 %s  F2 %s  F3 %s  F4 %s  success bound %s  (2^%d steps fewer: %s)' % tuple([format(x, '.3e') for x in (e6, e2, e3, e4)] + [str(p)[:12], HF - 20, str(p_less)[:12]]))
replay, HMAX, Rr, EXPO = ledger(TB, S, U, LRC, c, NI)
assert HMAX == P['HMAX']
print('hit counter: HMAX =', HMAX, '; P[abort before the stop on success] <= exp(-%d) < 2^-1000' % (EXPO.numerator // EXPO.denominator))
print('replay: (%d + %d) LRC + %d = %d (measuring walk e + 8, lock step 2e + 13, e = %d)' % (c['meas_iter'], c['replay_iter'], c['replay_const'], replay, c['e_eval']))
assert c['e_eval'] == UNIT + 29
PRE, B, A = pre_ops()
N = TB * BSTEP + replay + Rr + PRE
print('main', TB * BSTEP, ' replay', replay, ' rare', Rr, ' preprocessing', PRE, '(builds %d, annealing iterations %d)' % (B, A))
pl = 0
while (UNIT << pl) < PRE: pl += 1
print('preprocessing_log2: 2^%d < PRE / %d <= 2^%d, declared %d' % (pl - 1, UNIT, pl, pl))
print('N =', N)
print('shares: main %.5f replay %.5f other %.2e' % (TB * BSTEP / N, replay / N, (Rr + PRE) / N))
ms = mem_search(S, NI, c)
run_total = sum(ms.values()); pre_total = mem_pre(c)
for k, v in ms.items(): print('  %9d  %s' % (v, k))
print('search memory', run_total, '; preprocessing (gen4): max(image', GEN_IMAGE, '+ stack', GEN_STACK, ', measured peak', GEN_HWM, ') + the blocks it writes', pre_total - max(GEN_HWM, GEN_IMAGE + GEN_STACK), '=', pre_total)
mem = max(run_total, pre_total)
assert mem <= 2 ** 20 - MARGIN
print('memory', mem, '<= 2^20 = 1048576 with a margin of', 2 ** 20 - mem, 'bytes (search phase', 2 ** 20 - run_total, ', preprocessing', 2 ** 20 - pre_total, '): memory_log2_bytes = 20')
K, e = cert(N)
print('certificate: %d^%d * 2^%d < N^%d <= %d^%d * 2^%d' % (UNIT, K, e - 1, K, UNIT, K, e))
print('time_log2 = %d.%05d' % divmod(e, K))
print('score = time_log2 + max(0, memory_log2 - 20) = %d.%05d' % divmod(e, K))
```

Output:

```
rounds 16, unit 4336 word operations
step of 256 walks: blocks as executed 93867 (xor 68046 and 13155 or 9501 not 3165) + driver 78 (calls, returns, iota) = 93945; + prefilter 15 + test 2 + counter 3 = 93965
parameters: DP = planes 144..255 zero and the 10 planes below them < 936 (theta = 936 x 2^-122 = 2^-112.129635), replay cap LRC = 47051 x 1267650600228229401496703205376 = 10.4999 / theta, U 65120 trails, S 16280 table words (65120 records), key bits 47, trail number bits 16
Tb = 1328093265282585793353186825841147904 = 268206299 * 2^92 = 0.99914632 * 2^120, evaluations 0.999146 * 2^128
failure terms: F6 3.162e-4  F2 2.169e-89  F3 1.815e-5  F4 1.507e-5  success bound 0.3900000007  (2^92 steps fewer: 0.3899999984)
hit counter: HMAX = 64832097656381478934929308431417345 ; P[abort before the stop on success] <= exp(-2359166430207916179638) < 2^-1000
replay: (4373 + 8743) LRC + 79 = 782293699580794737309777253081773244495 (measuring walk e + 8, lock step 2e + 13, e = 4365)
main 124794283672278174072432200090163462799360  replay 782293699580794737309777253081773244495  rare 8168844304704066345801092899475143996  preprocessing 102371208725504 (builds 23406, annealing iterations 7200000000)
preprocessing_log2: 2^34 < PRE / 4336 <= 2^35, declared 35
N = 125584746216163672876087778538515919913355
shares: main 0.99371 replay 0.00623 other 6.50e-05
     113152  register file, 3536 words
     304672  step code: 60800 5-byte instructions (blocks stored once, iota XORs, prefilter) and 21 32-byte calls and returns
      86880  other code (setup, loop, handlers, restart, replay), 2715 instructions x 32 bytes
     520960  table, 16280 words (four records each)
      16384  LID and LST of the 256 walks, 512 words
        512  data image (lane constants K, PD, output pair), 16 words
search memory 1042560 ; preprocessing (gen4): max(image 366541 + stack 16384 , measured peak 262144 ) + the blocks it writes 303665 = 686590
memory 1042560 <= 2^20 = 1048576 with a margin of 6016 bytes (search phase 6016 , preprocessing 361986 ): memory_log2_bytes = 20
certificate: 4336^100000 * 2^12444556 < N^100000 <= 4336^100000 * 2^12444557
time_log2 = 124.44557
score = time_log2 + max(0, memory_log2 - 20) = 124.44557
```

## Appendix B. The generator (gen4.c) and the self-test (selftest4.c)

The listings are the files that ran, byte for byte. Some header comments still carry the names of the 71fefe66 files they descend from (gen3.c, selftest.c and prog.bin, other4.py); the code is that of this entry.

Compiled with `gcc -O2 -static -nostdlib -ffreestanding -fno-builtin -fno-tree-loop-distribute-patterns -fno-stack-protector -fno-pie -no-pie -DNR=16 -DKB=8 -DOPTIT=80000000`; run as `gen4 4096 0 3`.

```c
/* gen3.c - LS1 step generator for sha3-256-rNR (NR prefix rounds of Keccak-f[1600]), streaming version.
 * Freestanding (no libc, static arrays only) so the measured peak resident memory is the generator's own working set.
 *
 * Chain function on physical 256-bit points u (4 lanes u0..u3):
 *   message m(u) = 128 bytes = lanes 0..15 of the absorbed state:
 *     lane 1 = u0, lane 6 = u1, lane 11 = u0^u1^K[11]   (column x=1, rows 0,1,2)
 *     lane 4 = u2, lane 9 = u3, lane 14 = u2^u3^K[14]   (column x=4, rows 0,1,2)
 *     other lanes 0..15 = constants K[l]; lane 16 = 0x8000000000000006 (SHA3 pad);
 *   F(u) = SHA3-256-rNR(m(u)) XOR PD   (PD = fixed digest polarity mask of the program).
 * Round 0 is linear in u and round-1 theta stays linear (Guo-Liu-Song 2016 linear structure).
 *
 * Representation: plane (lane,z) is one 256-bit word (bit t = walk t). A value is (node, polarity):
 * logical = physical(node) XOR p. Constants folded. Linear nodes (rounds 0 and 1) carry their GF(2) form over the
 * 256 input bits, deduplicated by form. Lazy theta: C, D per round; each chi row XORs D into its five planes.
 * Chi row: complement subset s (NOTs) and, optionally, the 10-gate form (TRICK): output j reads the finished output
 * k = j+1 instead of input k, since (NOT a_k) AND a_{k+1} = (NOT chi_k) AND a_{k+1}.
 * Polarity plan (optmode >= 1): per round, NOTs on theta parities C and on D chosen by simulated annealing against the
 * exact row-cost table; optmode >= 2 adds the free output polarity of the two-operation terms (A^(A&B) or (NOT A)|B);
 * optmode 3 adds a greedy pass over the round-1 C/D complements.
 *
 * STREAMING: nodes live in a ring of W slots that holds ONE round (rounds 0 and 1 together). When a round is built,
 * its dead nodes are removed (liveness from the state planes, or from the digest planes in the last round), every
 * value gets its last use (all uses of a value lie in its own round or, for a state plane, in the next round), the
 * registers are allocated in node order and the instructions are written to prog.bin at once. The 1,600 state planes
 * are then pinned (register and flags) and the ring is reused for the next round. The program is never held.
 * Register j (j < 256) holds input plane j and receives digest plane j (free chain feed).
 *
 * Outputs of the charged run (gen3 512 0 3): the file prog.bin (5 bytes/instr: 3-bit op, 12-bit dst, a, b) and the ledger on
 * standard output. No other file is written. The separate uncharged inspection command (gen3 1 TRIAL 3 inspect) writes
 * meta.txt and plan.txt (the decisions of the plan, read by the Python port); the attack does not run it.
 * Usage: gen3 ntrials first optmode.  ntrials > 1: the cheap build (optmode 0) of trials first..first+ntrials-1, the
 * full build (optmode) of the TOPK lowest of them, and the lowest full count wins.  The attack runs "gen3 512 0 3".
 */
typedef unsigned long u64; typedef unsigned int u32; typedef unsigned short u16; typedef unsigned char u8;
typedef long i64;

/* ---------- freestanding runtime ---------- */
__asm__(".global _start\n_start:\n xor %rbp,%rbp\n mov %rsp,%rdi\n and $-16,%rsp\n call cmain\n mov %rax,%rdi\n mov $60,%rax\n syscall\n");
static i64 sc3(i64 n, i64 a, i64 b, i64 c){ i64 r; __asm__ volatile("syscall":"=a"(r):"a"(n),"D"(a),"S"(b),"d"(c):"rcx","r11","memory"); return r; }
void *memset(void *d, int c, unsigned long n){ u8 *p=d; while(n--) *p++=(u8)c; return d; }
void *memcpy(void *d, const void *s, unsigned long n){ u8 *p=d; const u8 *q=s; while(n--) *p++=*q++; return d; }
static int fd_out = 1;
static char obuf[4096]; static int olen;
static void oflush(void){ if(olen){ sc3(1,fd_out,(i64)obuf,olen); olen=0; } }
static void oc(char c){ if(olen==4096) oflush(); obuf[olen++]=c; }
static void os(const char *s){ while(*s) oc(*s++); }
static void ou(u64 v){ char t[24]; int n=0; do{ t[n++]='0'+v%10; v/=10; }while(v); while(n) oc(t[--n]); }
static void ox(u64 v){ for(int i=60;i>=0;i-=4) oc("0123456789abcdef"[(v>>i)&15]); }
static void ox8(u8 v){ oc("0123456789abcdef"[v>>4]); oc("0123456789abcdef"[v&15]); }
static int fopen_w(const char *p){ return (int)sc3(2,(i64)p,01|0100|01000,0644); } /* O_WRONLY|O_CREAT|O_TRUNC */
static void fclose_(int fd){ sc3(3,fd,0,0); }
static void die(const char *m){ oflush(); fd_out=2; os("gen4: "); os(m); oc('\n'); oflush(); sc3(60,1,0,0); }
static int atoi_(const char *s){ int v=0; while(*s>='0'&&*s<='9') v=v*10+(*s++-'0'); return v; }

/* ---------- Keccak constants ---------- */
static const u64 RC[24]={0x0000000000000001UL,0x0000000000008082UL,0x800000000000808aUL,0x8000000080008000UL,
 0x000000000000808bUL,0x0000000080000001UL,0x8000000080008081UL,0x8000000000008009UL,0x000000000000008aUL,
 0x0000000000000088UL,0x0000000080008009UL,0x000000008000000aUL,0x000000008000808bUL,0x800000000000008bUL,
 0x8000000000008089UL,0x8000000000008003UL,0x8000000000008002UL,0x8000000000000080UL,0x000000000000800aUL,
 0x800000008000000aUL,0x8000000080008081UL,0x8000000000008080UL,0x0000000080000001UL,0x8000000080008008UL};
static const int ROT[5][5]={{0,36,3,41,18},{1,44,10,45,2},{62,6,43,15,61},{28,55,25,21,56},{27,20,39,8,14}}; /* ROT[x][y] */
#ifndef NR
#define NR 8
#endif
#ifndef TRICK
#define TRICK 1          /* 10-gate chi rows */
#endif
#ifndef LASTTRICK
#define LASTTRICK 1      /* 10-gate rows also in the last (four-output) round */
#endif
#ifndef NOTFOLD
#define NOTFOLD 0        /* NOT of a NOT node = its operand */
#endif
#ifndef OPTIT
#define OPTIT 20000000
#endif
#ifndef TOPK
#define TOPK 8           /* trials carried from the cheap selection to the full build */
#endif
#ifndef R1SWEEPS
#define R1SWEEPS 3
#endif
/* ---------- LOOP layout (gen4): the generic rounds 2..NR-2 run two shared bodies B1 (bank X -> bank Y) and B2 (Y -> X) ----------
 * build rounds br: 0,1 = prefix P (rounds 0 and 1, into bank X); 2 = B1; 3 = B2 (its outputs forced to the polarity of
 * bank X); 4 = B1 again (not emitted; only when the last generic round is B1); BRE = the last round E (into registers 0..255). */
#define NG (NR-3)
#ifndef KB
#define KB 6             /* bodies in the cycle (even: B1 X->Y, B2 Y->X, ...) */
#endif
#define BRE (KB+2)
#define NBR (KB+3)
#define XB 256
#define YB 1856
#define POOL 3456

/* ---------- node ring (one round) and pinned state planes ---------- */
#define W 8192
#define PIN 8192             /* ids PIN..PIN+1599: the 1,600 state planes of the previous round */
#define NC 0xFFFF            /* constant marker */
#define NOUSE 0xFFFF
enum { O_IN=0, O_XOR=1, O_AND=2, O_OR=3, O_NOT=4 };
#define F_OPM 7
#define F_K 8                /* physical constant of a linear node */
#define F_LIVE 16
#define F_LIN 32
#define F_ST 64              /* a state plane: its uses continue in the next round */
#define F_OUT 128            /* a digest plane */
static u8 nf[W];
static u16 na[W], nb[W], nlast[W], nreg[W], linid[W];
static int nn;
static u8 pfl[1600]; static u16 preg[1600], plast[1600]; static int npin;
static u16 pord[1600];       /* ring index of the plane's node in its own round (operand order as in node order) */
static int okey(int n){ return n>=PIN? pord[n-PIN] : n+W; }
#define CH 8192
static u16 ch[CH];           /* cons hash: ring index+1 */
#define MAXF 1920
static u64 form[MAXF][4]; static u16 formnode[MAXF]; static int nform, maxform;
#define FH 2048
static u16 fh[FH];           /* form hash: form index+1 */

typedef struct { u16 n; u8 p; } V;
static V K_(int c){ V v; v.n=NC; v.p=(u8)c; return v; }
static V MK(int n,int p){ V v; v.n=(u16)n; v.p=(u8)p; return v; }
static u8 NF(int n){ return n>=PIN? pfl[n-PIN] : nf[n]; }

static u32 hmix(u32 x){ x^=x>>16; x*=0x7feb352dU; x^=x>>15; x*=0x846ca68bU; x^=x>>16; return x; }
static int maxring;
static int newnode(int op,int a,int b){ if(nn>=W) die("ring overflow"); nf[nn]=(u8)op; na[nn]=(u16)a; nb[nn]=(u16)b; linid[nn]=0xFFFF; nlast[nn]=NOUSE;
  if(nn+1>maxring) maxring=nn+1; return nn++; }
static int cons(int op,int a,int b){
  if(op!=O_NOT && okey(a)>okey(b)){ int t=a;a=b;b=t; }
  u32 h=hmix((u32)op*0x9E3779B1u ^ (u32)a*0x85EBCA77u ^ (u32)b*0xC2B2AE3Du)&(CH-1);
  for(;;){ u16 e=ch[h]; if(!e) break; int m=e-1; if((nf[m]&F_OPM)==op && na[m]==a && nb[m]==b) return m; h=(h+1)&(CH-1); }
  int m=newnode(op,a,b); ch[h]=(u16)(m+1); return m;
}
static int isk(int n){ return (NF(n)&F_K)?1:0; }
static int islin(int n){ return (NF(n)&F_LIN)?1:0; }
static u32 fhash(const u64 *m){ return hmix((u32)(m[0]^m[0]>>32^m[1]*3^m[2]*5^m[3]*7^(m[1]>>29)^(m[3]>>31))); }
static int flookup(const u64 *m){ u32 h=fhash(m)&(FH-1); for(;;){ u16 e=fh[h]; if(!e) return -1; int f=e-1; if(form[f][0]==m[0]&&form[f][1]==m[1]&&form[f][2]==m[2]&&form[f][3]==m[3]) return f; h=(h+1)&(FH-1);} }
static int fadd(const u64 *m,int node){ if(nform>=MAXF) die("form overflow"); int f=nform++; if(nform>maxform) maxform=nform; for(int i=0;i<4;i++) form[f][i]=m[i]; formnode[f]=(u16)node;
  u32 h=fhash(m)&(FH-1); while(fh[h]) h=(h+1)&(FH-1); fh[h]=(u16)(f+1); return f; }

static long cnt_emit; /* ops created (pre-DCE) */

static V xorv(V a,V b){
  if(a.n==NC) return MK(b.n==NC?NC:b.n, b.p^a.p);
  if(b.n==NC) return MK(a.n, a.p^b.p);
  if(a.n==b.n) return K_(a.p^b.p);
  if(islin(a.n)&&islin(b.n)){
    const u64 *fa=form[linid[a.n]], *fb=form[linid[b.n]]; u64 m[4];
    for(int i=0;i<4;i++) m[i]=fa[i]^fb[i];
    int kk=isk(a.n)^isk(b.n);
    if(!(m[0]|m[1]|m[2]|m[3])) return K_(kk^a.p^b.p);
    int f=flookup(m);
    if(f>=0){ int n3=formnode[f]; return MK(n3, kk^a.p^b.p^isk(n3)); }
    int n=newnode(O_XOR,a.n<b.n?a.n:b.n,a.n<b.n?b.n:a.n); nf[n]|=F_LIN|(kk?F_K:0);
    linid[n]=(u16)fadd(m,n); cnt_emit++; return MK(n,a.p^b.p);
  }
  int before=nn; int n=cons(O_XOR,a.n,b.n); if(nn>before) cnt_emit++;
  return MK(n,a.p^b.p);
}
static V notv(V a){ /* physical complement, logical value unchanged */
  if(a.n==NC) return a;
#if NOTFOLD
  if(a.n<PIN && (nf[a.n]&F_OPM)==O_NOT && !(nf[a.n]&F_LIN)) return MK(na[a.n], a.p^1);
#endif
  int before=nn; int n=cons(O_NOT,a.n,0);
  if(nn>before){ cnt_emit++; if(islin(a.n)){ nf[n]|=F_LIN|(isk(a.n)?0:F_K); linid[n]=linid[a.n]; } }
  return MK(n,a.p^1);
}
static int curmix_sel, curmix_flag;
static V and2(V a,V b){ /* logical a AND b */
  if(a.n==NC) return a.p? b : K_(0);
  if(b.n==NC) return b.p? a : K_(0);
  if(a.n==b.n) return a.p==b.p? a : K_(0);
  int before=nn;
  if(a.p==0&&b.p==0){ int n=cons(O_AND,a.n,b.n); if(nn>before) cnt_emit++; return MK(n,0); }
  if(a.p==1&&b.p==1){ int n=cons(O_OR,a.n,b.n); if(nn>before) cnt_emit++; return MK(n,1); }
  /* A & ~B with A the pol-0 operand: A ^ (A & B), or (NOT A) OR B (the complement, output polarity 1) */
  int A=a.p==0?a.n:b.n, B=a.p==0?b.n:a.n;
  curmix_flag=1;
  if(curmix_sel){ V na_=notv(MK(A,0)); int before2=nn; int n=cons(O_OR,na_.n,B); if(nn>before2) cnt_emit++; return MK(n,1); }
  int t=cons(O_AND,A,B); if(nn>before) cnt_emit++;
  return xorv(MK(A,0),MK(t,0));
}
static V andnot(V b1,V b2){ b1.p^=1; return and2(b1,b2); } /* (~b1) & b2 */

/* cost estimate of (~b1)&b2 given polarities */
static int cost_term(V b1,V b2){ if(b1.n==NC||b2.n==NC||b1.n==b2.n) return 0; return ((b1.p^1)==b2.p)?1:2; }

/* ---------- chi row decision ---------- */
static int mixfree;          /* optmode >= 2: the output polarity of a two-operation term is free */
static int row_choose(const V *b,int needmask,int *bj_out,int *bc_out){
  int best=-1,bc=1<<30,bj=-1;
  int distinct=1; for(int X=0;X<5;X++){ if(b[X].n==NC) distinct=0; for(int Y=X+1;Y<5;Y++) if(b[X].n==b[Y].n) distinct=0; }
  int jmax=(TRICK&&distinct)?5:0;
  for(int j=-1;j<jmax;j++){
    if(j>=0){ int k=(j+1)%5; if(!((needmask>>j)&1)||!((needmask>>k)&1)) continue; if(needmask!=0x1F && !LASTTRICK) continue; }
    for(int s=0;s<32;s++){
      int c=0; V bb[5];
      for(int X=0;X<5;X++){ bb[X]=b[X]; if(s>>X&1){ if(b[X].n==NC){ c=1<<29; } else { bb[X].p^=1; c++; } } }
      for(int X=0;X<5;X++) if(needmask>>X&1){
        if(X==j){ int k=(j+1)%5; V p1=bb[(k+1)%5], p2=bb[(k+2)%5];
          if((p1.p^1)==p2.p){ int orc=((p1.p^1)==1); V bk=bb[k]; bk.p^=orc; c+=cost_term(bk,bb[(X+2)%5]); }
          else if(mixfree) c+=1;
          else c+=cost_term(bb[k],bb[(X+2)%5]);
        }
        else c+=cost_term(bb[(X+1)%5],bb[(X+2)%5]);
      }
      if(c<bc){ bc=c; best=s; bj=j; }
    }
  }
  *bj_out=bj; if(bc_out) *bc_out=bc; return best;
}
/* table for rows with five distinct variable inputs: decision by the 5-bit polarity pattern */
static signed char tS[2][2][32], tJ[2][2][32]; static int tC[2][2][32];   /* [last][mixfree][pattern] */
static void mk_tables(void){
  for(int L=0;L<2;L++) for(int mf=0;mf<2;mf++) for(int p=0;p<32;p++){
    V b[5]; for(int X=0;X<5;X++) b[X]=MK(X,(p>>X)&1);
    int sv=mixfree; mixfree=mf; int bj,bc; int s=row_choose(b,L?0x0F:0x1F,&bj,&bc); mixfree=sv;
    tS[L][mf][p]=(signed char)s; tJ[L][mf][p]=(signed char)bj; tC[L][mf][p]=bc; }
}

static int pc64(u64 v){ int c=0; while(v){ v&=v-1; c++; } return c; }
/* ---------- B2 rows with output targets (gen4) ----------
 * rowsim: the polarity semantics of one chi row of five distinct variable inputs as the build computes it, for a complement
 * subset s, a 10-gate choice j (-1: none) and the polarities fb of the free (two-operation) terms; returns the cost
 * (complements + term operations) and the five output polarities. T2: for input pattern p and target pattern t, the least
 * cost + number of outputs whose polarity differs from the target (each fixed by one NOT). */
static int rowsim(int pin,int s,int j,int fb,int *outp){
  int p[5], tp[5], op[5], c=0;
  for(int X=0;X<5;X++){ p[X]=((pin>>X)&1)^((s>>X)&1); c+=(s>>X)&1; }
  int k=(j+1)%5;
  #define TERM(A1,B2,FREE,X_) { int a_=(A1)^1, b_=(B2); if(a_==0&&b_==0){ c+=1; tp[X_]=0; } else if(a_==1&&b_==1){ c+=1; tp[X_]=1; } else { c+=2; tp[X_]=(FREE); } }
  if(j>=0){
    int mixed=((p[(k+1)%5]^1)!=p[(k+2)%5]);
    int forced= mixed? ((p[(j+2)%5]^1)^p[k]) : ((fb>>k)&1);
    TERM(p[(k+1)%5],p[(k+2)%5],forced,k); op[k]=p[k]^tp[k];
  }
  for(int X=0;X<5;X++){
    if(j>=0 && X==k) continue;
    if(X==j){ TERM(op[k],p[(X+2)%5],(fb>>X)&1,X); }
    else { TERM(p[(X+1)%5],p[(X+2)%5],(fb>>X)&1,X); }
    op[X]=p[X]^tp[X];
  }
  #undef TERM
  int o=0; for(int X=0;X<5;X++) o|=op[X]<<X; *outp=o; return c;
}
static signed char t2S[32][32], t2J[32][32], t2F[32][32]; static int T2C[32][32];
static void mk_t2(void){
  for(int p=0;p<32;p++) for(int t=0;t<32;t++){
    int bc=1<<30, bs=0, bj=-1, bf=0;
    for(int j=-1;j<(TRICK?5:0);j++) for(int s=0;s<32;s++) for(int fb=0;fb<32;fb++){
      int o; int c=rowsim(p,s,j,fb,&o); c+=pc64((u64)(o^t));
      if(c<bc){ bc=c; bs=s; bj=j; bf=fb; } }
    t2S[p][t]=(signed char)bs; t2J[p][t]=(signed char)bj; t2F[p][t]=(signed char)bf; T2C[p][t]=bc; }
}
static int pol_target, pol_nophi;     /* polopt modes: B2 (row costs against the bank-X targets), no free-polarity moves */
static u8 tgtX[1600];                 /* polarity of bank X written by the prefix: the target of B2's outputs */
static u16 tgtrow[320];               /* per row (Y*64+z): the five target bits */

/* ---------- the step ---------- */
static V S[25][64], NS[25][64], Cc[5][64], Dd[5][64];
/* ---------- polarity plan ----------
 * Per round r (2..NR-1): choose physical complements (NOT) on theta column parities C[x][z] (each toggles 10 chi
 * inputs) and on D[x][z] (each toggles 5 chi inputs, one in each of 5 rows), and the output polarity of the free
 * two-operation terms of round r-1, so that the sum over the rows of the exact row cost (table tC) plus the number of
 * these NOTs is minimal. Simulated annealing, deterministic xorshift, OPTIT iterations per round. */
static int optmode=1;
static u8 phib[NBR][200], mixb[NBR][200]; /* bit (l*64+z): output polarity choice / free-term flag of plane (l,z) */
#define GETB(a,r,l,z) ((a[r][((l)*64+(z))>>3]>>(((l)*64+(z))&7))&1)
#define TGLB(a,r,l,z) (a[r][((l)*64+(z))>>3]^=(u8)(1<<(((l)*64+(z))&7)))
#define SETB(a,r,l,z,v) (a[r][((l)*64+(z))>>3]=(u8)((a[r][((l)*64+(z))>>3]&~(1<<(((l)*64+(z))&7)))|((v)<<(((l)*64+(z))&7))))
static u8 FFb[NBR][40], GGb[NBR][40]; static u8 decided[NBR]; static int curpass;
#define GB(a,i) ((a[(i)>>3]>>((i)&7))&1)
static u8 F1[5][64], G1[5][64];
static u8 fflip[5][64], gflip[5][64];
static long pol_pred[NBR], pol_nots[NBR], pol_phi[NBR];
static u64 prs;
static double mexp(double x){ if(x<-40) return 0; double y=x/64; double e=1+y+y*y/2+y*y*y/6+y*y*y*y/24; for(int i=0;i<6;i++) e*=e; return e; }
static u64 pxs(void){ prs^=prs<<13; prs^=prs>>7; prs^=prs<<17; return prs; }

static void polopt(int r,int last){
  static u8 pS[25][64]; static u16 vrow[5][64][5]; static u8 vbit[5][64][5]; static u8 pat[320];
  for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; if(v.n==NC||islin(v.n)) return; pS[l][z]=v.p; }
  static u8 pC[5][64], pD[5][64];
  for(int x=0;x<5;x++) for(int z=0;z<64;z++){ int p=0; for(int y=0;y<5;y++) p^=pS[x+5*y][z]; pC[x][z]=(u8)p; }
  for(int x=0;x<5;x++) for(int z=0;z<64;z++) pD[x][z]=pC[(x+4)%5][z]^pC[(x+1)%5][(z+63)&63];
  for(int i=0;i<320;i++) pat[i]=0;
  for(int x=0;x<5;x++) for(int zz=0;zz<64;zz++) for(int y=0;y<5;y++){
    int Y=(2*(x-y)+10)%5, z=(zz+ROT[x][y])&63; int row=Y*64+z;
    vrow[x][zz][y]=(u16)row; vbit[x][zz][y]=(u8)(1<<y);
    if(pS[x+5*y][zz]^pD[x][zz]) pat[row]|=(u8)(1<<y);
  }
  const int *rt0=tC[0][mixfree], *rtL=tC[1][mixfree];
  #define RT(i,p) (last? ((i)<64? rtL[p]:0) : (pol_target? T2C[p][tgtrow[i]] : rt0[p]))
  static u16 fv[1600]; int nfv=0; static u8 phic[25][64]; memset(phic,0,sizeof phic);
  if(!pol_nophi) for(int l=0;l<25;l++) for(int z=0;z<64;z++) if(GETB(mixb,r-1,l,z)) fv[nfv++]=(u16)(l*64+z);
  if(pol_target) for(int Y=0;Y<5;Y++) for(int z=0;z<64;z++){ int t=0; for(int X=0;X<5;X++) t|=tgtX[(X+5*Y)*64+z]<<X; tgtrow[Y*64+z]=(u16)t; }
  long cost=0; for(int i=0;i<320;i++) cost+=RT(i,pat[i]);
  static u8 bestf[5][64], bestg[5][64]; long best=cost; int nfl=0;
  memset(fflip,0,sizeof fflip); memset(gflip,0,sizeof gflip); memcpy(bestf,fflip,sizeof fflip); memcpy(bestg,gflip,sizeof gflip);
  prs=0x2545F4914F6CDD1DUL ^ (u64)r*0x9E3779B97F4A7C15UL;
  #define TOGD(x,zz) for(int k=0;k<5;k++){ int rw=vrow[x][zz][k]; cost-=RT(rw,pat[rw]); pat[rw]^=vbit[x][zz][k]; cost+=RT(rw,pat[rw]); }
  #define TOGV(x,y,zz) { int rw=vrow[x][zz][y]; cost-=RT(rw,pat[rw]); pat[rw]^=vbit[x][zz][y]; cost+=RT(rw,pat[rw]); }
  static u8 bestp[25][64]; memcpy(bestp,phic,sizeof phic);
  double T0=1.2;
  for(long it=0; it<OPTIT; it++){
    double T=T0*mexp(-3.1780538303479458*(double)it/(double)OPTIT);
    u64 rv=pxs(); int mv=(int)(rv%3); int x=(int)((rv>>2)%5); int zz=(int)((rv>>8)&63);
    int pl=0, py=0;
    if(mv==2){ if(!nfv) mv=(int)(rv>>20)&1; else { int q=fv[(rv>>20)%nfv]; pl=q>>6; zz=q&63; x=pl%5; py=pl/5; } }
    int isg=mv;
    long c0=cost; int nf0=nfl;
    if(mv==0){ TOGD(x,zz); fflip[x][zz]^=1; nfl+= fflip[x][zz]?1:-1; }
    else if(mv==1){ int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGD(x1,zz); TOGD(x2,z2); gflip[x][zz]^=1; nfl+= gflip[x][zz]?1:-1; }
    else { int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGV(x,py,zz); TOGD(x1,zz); TOGD(x2,z2); phic[pl][zz]^=1; }
    long d=(cost+nfl)-(c0+nf0);
    int acc= d<=0;
    if(!acc){ double u=(double)((pxs()>>11)&((1UL<<53)-1))/(double)(1UL<<53); acc= u < mexp(-(double)d/T); }
    if(acc){ if(cost+nfl<best){ best=cost+nfl; memcpy(bestf,fflip,sizeof fflip); memcpy(bestg,gflip,sizeof gflip); memcpy(bestp,phic,sizeof phic); } }
    else {
      if(isg==0){ TOGD(x,zz); fflip[x][zz]^=1; nfl+= fflip[x][zz]?1:-1; }
      else if(isg==1){ int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGD(x1,zz); TOGD(x2,z2); gflip[x][zz]^=1; nfl+= gflip[x][zz]?1:-1; }
      else { int x1=(x+1)%5, x2=(x+4)%5, z2=(zz+1)&63; TOGV(x,py,zz); TOGD(x1,zz); TOGD(x2,z2); phic[pl][zz]^=1; }
    }
  }
  memcpy(fflip,bestf,sizeof fflip); memcpy(gflip,bestg,sizeof gflip);
  long n=0; for(int x=0;x<5;x++) for(int z=0;z<64;z++) n+=fflip[x][z]+gflip[x][z];
  pol_pred[r]=best-n; pol_nots[r]=n;
  long np=0; for(int l=0;l<25;l++) for(int z=0;z<64;z++) if(bestp[l][z]){ TGLB(phib,r-1,l,z); np++; }
  pol_phi[r]=np;
}

static u64 KL[25];          /* lane constants of the absorbed state (var lanes: offset) */
static u64 PD[4];
static long nnot_rows, ntrick, nforced;


/* ---------- per-round finish: dead-code removal, counts, register allocation, emission, pinning ---------- */
static long cnt[5];
#define NREG 4096
static u16 freestk[NREG]; static int nfree; static u8 regbusy[NREG], tempok[NREG];
static long live, maxlive, maxreg, ninstr;
static int fdp=-1; static u8 eb[4000]; static int el;
static int emitting;
static int outbank, inbank;  /* this block: bank written (XB, YB; -1 in E) and bank read (XB, YB; -1 in the prefix) */
static long bcnt[NBR][5], bins[NBR], blive[NBR], breg[NBR];
static long nfix;            /* NOTs that force B2's outputs to the polarity of bank X */
static void block_alloc(void){
  memset(regbusy,0,sizeof regbusy); memset(tempok,0,sizeof tempok);
  for(int r=POOL;r<NREG;r++) tempok[r]=1;
  if(inbank<0){ for(int r=0;r<256;r++) tempok[r]=1; for(int r=YB;r<YB+1600;r++) tempok[r]=1; }
  else if(outbank>=0){ for(int r=0;r<256;r++) tempok[r]=1; for(int r=inbank;r<inbank+1600;r++) tempok[r]=1; }
  else { int ob= inbank==XB? YB:XB; for(int r=inbank;r<inbank+1600;r++) tempok[r]=1; for(int r=ob;r<ob+1600;r++) tempok[r]=1; }
  nfree=0;
  for(int r=NREG-1;r>=0;r--){ if(!tempok[r]) continue; if(inbank<0 && r<256) continue; if(inbank>=0 && r>=inbank && r<inbank+1600) continue; freestk[nfree++]=(u16)r; }
  live=0; maxlive=0; maxreg=0; ninstr=0; el=0;
}
static void freereg(int r){ if(!regbusy[r]) die("free of a free register"); regbusy[r]=0; live--; if(tempok[r]) freestk[nfree++]=(u16)r; }
static void pin_state(void){
  for(int q=0;q<1600;q++){ preg[q]=0xFFFF; plast[q]=NOUSE; pfl[q]=0; }
  npin=0;
  for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; if(v.n==NC) continue;
    if(v.n>=PIN) die("state plane from an earlier round");
    if(nf[v.n]&F_LIN) die("linear state plane");
    if(nlast[v.n]==0xFFFE) die("two state planes share a node");
    int q=l*64+z; pord[q]=v.n; pfl[q]=(u8)(nf[v.n]&F_OPM); preg[q]=(u16)(outbank+q); npin++;
    nlast[v.n]=0xFFFE; S[l][z].n=(u16)(PIN+q); }
}
static void finish_round(int last,int prefix){
  int lo= prefix? 256 : 0;
  for(int i=0;i<nn;i++) nf[i]&=(u8)~(F_LIVE|F_ST|F_OUT);
  if(!last){
    for(int l=0;l<25;l++) for(int z=0;z<64;z++){ V v=S[l][z]; if(v.n==NC) die("constant state plane"); if(v.n>=PIN) die("state plane from an earlier round");
      if(nf[v.n]&F_ST) die("two state planes share a node");
      nf[v.n]|=F_LIVE|F_ST; nreg[v.n]=(u16)(outbank+l*64+z); }
  } else {
    for(int j=0;j<256;j++){ V v=S[j>>6][j&63]; if(v.n==NC||v.n>=PIN||v.n<lo) die("digest plane constant, input or old");
      if(nf[v.n]&F_OUT) die("shared digest node"); nf[v.n]|=F_LIVE|F_OUT; nreg[v.n]=(u16)j; PD[j>>6]|=(u64)v.p<<(j&63); }
  }
  for(int i=nn-1;i>=lo;i--) if(nf[i]&F_LIVE){ int op=nf[i]&F_OPM; int a=na[i], b=nb[i];
    if(a<PIN) nf[a]|=F_LIVE; if(op!=O_NOT && b<PIN) nf[b]|=F_LIVE; }
  for(int i=lo;i<nn;i++) if(nf[i]&F_LIVE) cnt[nf[i]&F_OPM]++;
  if(emitting){
    block_alloc();
    for(int i=lo;i<nn;i++) if(nf[i]&F_LIVE){ int op=nf[i]&F_OPM; int a=na[i], b=nb[i];
      if(a>=PIN) plast[a-PIN]=(u16)i; else nlast[a]=(u16)i;
      if(op!=O_NOT){ if(b>=PIN) plast[b-PIN]=(u16)i; else nlast[b]=(u16)i; } }
    if(prefix){ for(int j=0;j<256;j++){ nreg[j]=(u16)j; if(nlast[j]!=NOUSE){ regbusy[j]=1; live++; } else freestk[nfree++]=(u16)j; } if(live>maxlive) maxlive=live; }
    else { for(int q=0;q<1600;q++) if(preg[q]!=0xFFFF){ if(plast[q]==NOUSE) die("state plane without use"); regbusy[preg[q]]=1; live++; } if(live>maxlive) maxlive=live; }
    for(int i=lo;i<nn;i++){
      if(!(nf[i]&F_LIVE)) continue;
      int op=nf[i]&F_OPM; int a=na[i], b=(op==O_NOT)?a:nb[i];
      int ra= a>=PIN? preg[a-PIN] : nreg[a];
      int rb= op==O_NOT? 0 : (b>=PIN? preg[b-PIN] : nreg[b]);
      int ops[2]={a,b};
      for(int k=0;k<2;k++){ int o=ops[k]; if(k==1&&o==a) break;
        if(o>=PIN){ if(plast[o-PIN]==i){ freereg(preg[o-PIN]); preg[o-PIN]=0xFFFF; npin--; } }
        else if(!(nf[o]&(F_ST|F_OUT)) && nlast[o]==i) freereg(nreg[o]); }
      int dst;
      if(nf[i]&(F_OUT|F_ST)){ dst=nreg[i]; if(regbusy[dst]) die("output register busy"); }
      else if(nfree>0) dst=freestk[--nfree];
      else { die("out of registers"); dst=0; }
      if(!(nf[i]&(F_ST|F_OUT)) && nlast[i]==NOUSE) die("live node without use");
      regbusy[dst]=1; live++; nreg[i]=(u16)dst; if(live>maxlive) maxlive=live; if(dst+1>maxreg) maxreg=dst+1;
      int code= op==O_XOR?0: op==O_AND?1: op==O_OR?2: 3;
      u64 w=(u64)code | (u64)dst<<3 | (u64)ra<<15 | (u64)rb<<27;
      for(int k=0;k<5;k++) eb[el++]=(u8)(w>>(8*k));
      if(el>=3995){ if(fdp>=0) sc3(1,fdp,(i64)eb,el); el=0; }
      ninstr++;
    }
    if(!prefix && npin!=0) die("state plane not freed");
    if(el){ if(fdp>=0) sc3(1,fdp,(i64)eb,el); el=0; }
  }
  if(!last) pin_state();
}

static int stop_prefix; static long prefix_ops;
static void unpack_fg(int r){ for(int i=0;i<320;i++){ fflip[i/64][i%64]=GB(FFb[r],i); gflip[i/64][i%64]=GB(GGb[r],i); } }
static void pack_fg(int r){ memset(FFb[r],0,40); memset(GGb[r],0,40);
  for(int i=0;i<320;i++){ FFb[r][i>>3]|=(u8)(fflip[i/64][i%64]<<(i&7)); GGb[r][i>>3]|=(u8)(gflip[i/64][i%64]<<(i&7)); } }
static long driver_ops(void){ long d=0; for(int r=2;r<=NR-2;r++) d+=2+pc64(RC[r]); return d; }
static long nruns(int j){ return NG/KB + ((j<=NG%KB)?1:0); }           /* executions of body j per step */
static long step_ops(void){
  long t=0; for(int k=1;k<5;k++){ t+=bcnt[1][k]+bcnt[BRE][k]; for(int j=1;j<=KB;j++) t+=nruns(j)*bcnt[j+1][k]; }
  return t+driver_ops(); }
static u8 snapP[KB+1][1600], snapF[KB+1][1600]; static u16 snapO[KB+1][1600];

static void build(void){
  nn=0; nform=0; cnt_emit=0; nnot_rows=0; ntrick=0; nforced=0; npin=0; nfix=0;
  for(int k=0;k<5;k++) cnt[k]=0;
  for(int i=0;i<NBR;i++){ for(int k=0;k<5;k++) bcnt[i][k]=0; bins[i]=blive[i]=breg[i]=0; }
  memset(fh,0,sizeof fh); memset(ch,0,sizeof ch);
  for(int q=0;q<1600;q++){ preg[q]=0xFFFF; plast[q]=NOUSE; pfl[q]=0; }
  PD[0]=PD[1]=PD[2]=PD[3]=0;
  for(int j=0;j<256;j++){ int n=newnode(O_IN,0,0); u64 m[4]={0,0,0,0}; m[j>>6]=1UL<<(j&63); nf[n]|=F_LIN; linid[n]=(u16)fadd(m,n); }
  for(int l=0;l<25;l++) for(int z=0;z<64;z++) S[l][z]=K_((KL[l]>>z)&1);
  for(int z=0;z<64;z++){
    S[1][z]=MK(z,(KL[1]>>z)&1); S[6][z]=MK(64+z,(KL[6]>>z)&1);
    S[4][z]=MK(128+z,(KL[4]>>z)&1); S[9][z]=MK(192+z,(KL[9]>>z)&1);
  }
  for(int z=0;z<64;z++){
    S[11][z]=xorv(xorv(MK(z,0),MK(64+z,0)),K_((KL[11]>>z)&1));
    S[14][z]=xorv(xorv(MK(128+z,0),MK(192+z,0)),K_((KL[14]>>z)&1));
  }
  for(int r=0;r<=BRE;r++){
    int last=(r==BRE), isB=(r>=2 && r<BRE), bj_=r-1;          /* body number 1..KB */
    const u8 *tgt= (isB && bj_==KB && NG>KB)? tgtX : 0;      /* the last body closes the cycle: it writes bank X in its polarity */
    int isB2= tgt!=0;
    u64 rcv= r==0? RC[0] : r==1? RC[1] : last? RC[NR-1] : 0;
    if(last){ /* E reads the output of the last generic round's body */
      int jl=((NG-1)%KB)+1, ob=(jl&1)? YB : XB;
      for(int q=0;q<1600;q++){ S[q>>6][q&63]=MK(PIN+q,snapP[jl][q]); pord[q]=snapO[jl][q]; pfl[q]=snapF[jl][q]; preg[q]=(u16)(ob+q); plast[q]=NOUSE; }
      npin=1600;
    }
    memset(fflip,0,sizeof fflip); memset(gflip,0,sizeof gflip);
    if(r==1 && optmode>=3){ memcpy(fflip,F1,sizeof fflip); memcpy(gflip,G1,sizeof gflip); }
    if(optmode && r>=2){
      if(decided[r]) unpack_fg(r);
      else if(r==curpass){ pol_target=isB2; pol_nophi=last; polopt(r,last); pol_target=0; pol_nophi=0; pack_fg(r); decided[r]=1; return; }
    }
    if(r>=2){ nn=0; memset(ch,0,sizeof ch); }      /* the ring holds one round (rounds 0 and 1 together) */
    for(int x=0;x<5;x++){ V s=S[x][63]; for(int y=1;y<5;y++) s=xorv(s,S[x+5*y][63]); Cc[x][63]= gflip[x][63]? notv(s) : s; }
    for(int z=0;z<64;z++){
      if(z<63) for(int x=0;x<5;x++){ V s=S[x][z]; for(int y=1;y<5;y++) s=xorv(s,S[x+5*y][z]); Cc[x][z]= gflip[x][z]? notv(s) : s; }
      for(int x=0;x<5;x++){ Dd[x][z]=xorv(Cc[(x+4)%5][z],Cc[(x+1)%5][(z+63)&63]); if(fflip[x][z]) Dd[x][z]=notv(Dd[x][z]); }
    }
    int nY=last?1:5, needmask=last?0x0F:0x1F;
    for(int Y=0;Y<nY;Y++) for(int z=0;z<64;z++){
      V b[5];
      for(int X=0;X<5;X++){ int y=X, x=(3*Y+X)%5; int zz=(z-ROT[x][y]+64)&63; b[X]=xorv(S[x+5*y][zz],Dd[x][zz]); }
      int distinct=1; for(int X=0;X<5;X++){ if(b[X].n==NC) distinct=0; for(int X2=X+1;X2<5;X2++) if(b[X].n==b[X2].n) distinct=0; }
      int best,bj,fbm=0, tg=0;
      if(isB2) for(int X=0;X<5;X++) tg|=tgt[(X+5*Y)*64+z]<<X;
      if(distinct){ int p=0; for(int X=0;X<5;X++) p|=b[X].p<<X;
        if(isB2){ best=t2S[p][tg]; bj=t2J[p][tg]; fbm=t2F[p][tg]; }
        else { best=tS[last][mixfree][p]; bj=tJ[last][mixfree][p]; } }
      else best=row_choose(b,needmask,&bj,0);
      for(int X=0;X<5;X++) if(best>>X&1){ b[X]=notv(b[X]); nnot_rows++; }
      int k=(bj+1)%5;
      if(bj>=0){
        ntrick++;
        int pl=k+5*Y; V p1=b[(k+1)%5], p2=b[(k+2)%5];
        int mixed=((p1.p^1)!=p2.p), forced=-1;
        if(mixed && mixfree){ forced=(b[(bj+2)%5].p^1)^b[k].p; nforced++; }
        curmix_sel= forced>=0? forced : (isB2? (fbm>>k)&1 : mixfree? GETB(phib,r,pl,z) : 0); curmix_flag=0;
        V t=andnot(b[(k+1)%5],b[(k+2)%5]);
        SETB(mixb,r,pl,z,((mixfree && forced<0)? curmix_flag : 0)); curmix_sel=0;
        NS[pl][z]=xorv(b[k],t);
      }
      for(int X=0;X<5;X++) if(needmask>>X&1){
        if(bj>=0 && X==k) continue;
        int pl=X+5*Y;
        curmix_sel= isB2? (fbm>>X)&1 : mixfree? GETB(phib,r,pl,z) : 0; curmix_flag=0;
        V t= (X==bj)? andnot(NS[k+5*Y][z],b[(X+2)%5]) : andnot(b[(X+1)%5],b[(X+2)%5]);
        SETB(mixb,r,pl,z,(mixfree? curmix_flag : 0)); curmix_sel=0;
        NS[pl][z]=xorv(b[X],t);
      }
      if(isB2) for(int X=0;X<5;X++){ int pl=X+5*Y; if(NS[pl][z].p!=((tg>>X)&1)){ NS[pl][z]=notv(NS[pl][z]); nfix++; } }
    }
    if(!isB) for(int z=0;z<64;z++) NS[0][z].p^=(rcv>>z)&1;   /* iota of rounds 0, 1 and NR-1 (polarity); the generic rounds' iota is the driver's */
    for(int l=0;l<25;l++) for(int z=0;z<64;z++) S[l][z]=NS[l][z];
    if(r==0) continue;
    outbank= r==1? XB : isB? ((bj_&1)? YB : XB) : -1;
    inbank= r==1? -1 : isB? ((bj_&1)? XB : YB) : ((((NG-1)%KB+1)&1)? YB : XB);
    long c0[5]; for(int k=0;k<5;k++) c0[k]=cnt[k];
    if(emitting){ static char fn[16]; if(r==1){ fn[0]='P'; fn[1]='.'; fn[2]='b'; fn[3]='i'; fn[4]='n'; fn[5]=0; }
      else if(last){ fn[0]='E'; fn[1]='.'; fn[2]='b'; fn[3]='i'; fn[4]='n'; fn[5]=0; }
      else { int i=0; fn[i++]='B'; if(bj_>=10) fn[i++]=(char)('0'+bj_/10); fn[i++]=(char)('0'+bj_%10); fn[i++]='.'; fn[i++]='b'; fn[i++]='i'; fn[i++]='n'; fn[i]=0; }
      fdp=fopen_w(fn); if(fdp<0) die("open block file"); }
    finish_round(last, r==1);
    if(emitting){ fclose_(fdp); fdp=-1; bins[r]=ninstr; blive[r]=maxlive; breg[r]=maxreg; }
    for(int k=0;k<5;k++) bcnt[r][k]=cnt[k]-c0[k];
    if(r==1) for(int q=0;q<1600;q++) tgtX[q]=S[q>>6][q&63].p;
    if(isB){ for(int q=0;q<1600;q++){ snapP[bj_][q]=S[q>>6][q&63].p; snapO[bj_][q]=pord[q]; snapF[bj_][q]=pfl[q]; } }
    if(tgt){ int bad=0; for(int q=0;q<1600;q++) if(S[q>>6][q&63].p!=tgt[q]) bad++; if(bad){ fd_out=2; os("round "); ou(r); os(" mismatches "); ou(bad); oc(10); oflush(); die("block output polarity differs from its bank"); } }
    if(r==1 && stop_prefix){ prefix_ops=cnt[1]+cnt[2]+cnt[3]+cnt[4]; return; }
  }
}

static u64 rs;
static u64 xs(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
static void set_consts(int trial){
  for(int l=0;l<25;l++) KL[l]=0;
  KL[16]=0x8000000000000006UL;
  if(trial>0){ rs=0x9E3779B97F4A7C15UL*(u64)trial+1; for(int i=0;i<10;i++) xs();
    static const int fl[12]={0,2,3,5,7,8,10,12,13,15,11,14};
    for(int i=0;i<12;i++) KL[fl[i]]=xs(); }
}

static long r1gain;
static void r1greedy(void){ outbank=XB;
  /* round 1: physical complements on C and D (linear forms), kept when the live ops of rounds 0..1 drop */
  memset(F1,0,sizeof F1); memset(G1,0,sizeof G1);
  memset(phib,0,sizeof phib); memset(mixb,0,sizeof mixb); memset(decided,0,sizeof decided); curpass=99;
  stop_prefix=1; build(); long best=prefix_ops, b0=best;
  for(int sw=0;sw<R1SWEEPS;sw++){ int imp=0;
    for(int v=0;v<640;v++){ u8 *p= v<320? &F1[v/64][v%64] : &G1[(v-320)/64][v%64];
      *p^=1; build(); long c=prefix_ops;
      if(c<best){ best=c; imp=1; } else *p^=1; }
    if(!imp) break; }
  stop_prefix=0; r1gain=b0-best;
}
static void fullplan(void){
  if(optmode>=3) r1greedy();
  memset(phib,0,sizeof phib); memset(mixb,0,sizeof mixb); memset(decided,0,sizeof decided);
  memset(pol_phi,0,sizeof pol_phi); memset(pol_pred,0,sizeof pol_pred); memset(pol_nots,0,sizeof pol_nots);
  if(optmode){ for(int k=2;k<=BRE;k++){ curpass=k; build(); } }
  curpass=99;
}
static int work(int argc,char **argv);
/* The work runs in a forked child: its own signal struct starts with ru_maxrss 0, so the
   parent's wait4 rusage gives the worker's peak RSS without the high-water mark that Linux
   carries over from the shell across fork+execve. */
int cmain(long *sp){
  int argc=(int)sp[0]; char **argv=(char**)(sp+1);
  i64 pid=sc3(57,0,0,0);
  if(pid==0){ int rc=work(argc,argv); oflush(); sc3(60,rc,0,0); }
  if(pid<0) die("fork");
  struct { long ut[2], st[2]; long maxrss, rest[14]; } ru; int status=0;
  { i64 r; register i64 r10 __asm__("r10")=(i64)&ru; __asm__ volatile("syscall":"=a"(r):"a"(61L),"D"(pid),"S"((i64)&status),"d"(0L),"r"(r10):"rcx","r11","memory"); }
  for(int pass=1;pass<2;pass++){ fd_out=1;
    os("worker peak RSS (getrusage via wait4, worker forked from the 1-page parent) "); ou(ru.maxrss); os(" KiB = "); ou(ru.maxrss*1024); os(" bytes (limit 1048576)\n"); oflush(); }
  return ((status>>8)&255);
}
static void hexbytes(const u8 *p,int n){ for(int i=0;i<n;i++) ox8(p[i]); }
static long vmhwm(void){
  long hwm=-1; static char st[4096]; int fd=(int)sc3(2,(i64)"/proc/self/status",0,0);
  if(fd>=0){ long n=sc3(0,fd,(i64)st,sizeof st-1); fclose_(fd); if(n>0){ st[n]=0;
    for(long i=0;i+6<n;i++) if(st[i]=='V'&&st[i+1]=='m'&&st[i+2]=='H'&&st[i+3]=='W'&&st[i+4]=='M'){ long j=i+6,v=0; while(st[j]==' '||st[j]==9) j++; while(st[j]>='0'&&st[j]<='9') v=v*10+(st[j++]-'0'); hwm=v; break; } } }
  return hwm;
}
static int work(int argc,char **argv){
  mk_tables(); mk_t2();
  int ntr= argc>1? atoi_(argv[1]) : 1; if(ntr<1) ntr=1;
  int t0= argc>2? atoi_(argv[2]) : 0;
  if(argc>3) optmode=atoi_(argv[3]);
  int insp= argc>4 && argv[4][0]=='i';   /* uncharged inspection command only: also writes meta.txt and plan.txt */
  int om=optmode;
  int bestt=t0; long bestc=1L<<60;
  if(ntr>1){
    /* stage 1: cheap build (optmode 0) of every trial; keep the TOPK lowest counts (ties: lower trial first) */
    static long kc[TOPK]; static int kt[TOPK]; int nk=0;
    optmode=0; mixfree=0; emitting=0; curpass=99; memset(decided,0,sizeof decided);
    for(int t=t0;t<t0+ntr;t++){ set_consts(t); build(); long tot=step_ops();
      os("trial "); ou(t); os(" ops "); ou(tot); oc('\n');
      int pos=nk; while(pos>0 && kc[pos-1]>tot) pos--;
      if(pos<TOPK){ for(int i=(nk<TOPK?nk:TOPK-1);i>pos;i--){ kc[i]=kc[i-1]; kt[i]=kt[i-1]; } kc[pos]=tot; kt[pos]=t; if(nk<TOPK) nk++; } }
    oflush();
    /* stage 2: the full build (optmode) of each kept trial, counted; the lowest count wins (ties: earlier in the list) */
    optmode=om; mixfree= optmode>=2;
    for(int i=0;i<nk;i++){ set_consts(kt[i]); emitting=0; fullplan(); build(); long tot=step_ops();
      os("plan trial "); ou(kt[i]); os(" cheap "); ou(kc[i]); os(" full "); ou(tot); oc('\n'); oflush();
      if(tot<bestc){ bestc=tot; bestt=kt[i]; } }
  }
  optmode=om; mixfree= optmode>=2;
  set_consts(bestt);
  emitting=0; fullplan();
  emitting=1; build();
  long pre=cnt_emit;
  long tot=step_ops();
  long hwm=vmhwm();
  if(insp){
  fd_out=fopen_w("meta.txt");
  os("trial "); ou(bestt); oc('\n');
  for(int l=0;l<25;l++){ os("lane "); ou(l); oc(' '); ox(KL[l]); oc('\n'); }
  os("varlanes 1 6 4 9 ; lane11 = u0^u1^K11 ; lane14 = u2^u3^K14\n");
  os("pd "); for(int i=0;i<4;i++){ ox(PD[i]); oc(i<3?' ':'\n'); }
  oflush(); fclose_(fd_out);
  fd_out=fopen_w("plan.txt");
  os("trial "); ou(bestt); oc('\n');
  os("nr "); ou(NR); os(" optmode "); ou(optmode); oc('\n');
  { u8 a[40], g[40]; memset(a,0,40); memset(g,0,40); for(int i=0;i<320;i++){ a[i>>3]|=(u8)(F1[i/64][i%64]<<(i&7)); g[i>>3]|=(u8)(G1[i/64][i%64]<<(i&7)); }
    os("F1 "); hexbytes(a,40); oc('\n'); os("G1 "); hexbytes(g,40); oc('\n'); }
  for(int r=2;r<=BRE;r++){ os("FG "); ou(r); oc(' '); hexbytes(FFb[r],40); oc(' '); hexbytes(GGb[r],40); oc('\n'); }
  for(int r=0;r<=BRE;r++){ os("PHI "); ou(r); oc(' '); hexbytes(phib[r],200); oc('\n'); }
  oflush(); fclose_(fd_out);
  }
  fd_out=1;
  os("LS1 LOOP step ledger (256 lanes, one chain step, "); ou(NR); os(" rounds), generator gen4: prefix P (rounds 0,1), a cycle of "); ou(KB); os(" bodies over the generic rounds 2.."); ou(NR-2); os(", last round E\n");
  long tx[5]={0,0,0,0,0}, ci=0;
  for(int r=1;r<=BRE;r++){ long w= (r==1||r==BRE)? 1 : nruns(r-1);
    if(r==1) os("block P"); else if(r==BRE) os("block E"); else { os("block B"); ou(r-1); }
    os(" runs "); ou(w); os(" XOR "); ou(bcnt[r][1]); os(" AND "); ou(bcnt[r][2]); os(" OR "); ou(bcnt[r][3]); os(" NOT "); ou(bcnt[r][4]);
    long t=bcnt[r][1]+bcnt[r][2]+bcnt[r][3]+bcnt[r][4]; os(" total "); ou(t); os(" ; instructions "); ou(bins[r]); os(" max live "); ou(blive[r]); os(" highest register+1 "); ou(breg[r]); oc('\n');
    if(bins[r]!=t) die("instr count mismatch");
    for(int k=1;k<5;k++) tx[k]+=w*bcnt[r][k]; ci+=bins[r]; }
  os("XOR "); ou(tx[1]); oc('\n'); os("AND "); ou(tx[2]); oc('\n'); os("OR  "); ou(tx[3]); oc('\n'); os("NOT "); ou(tx[4]); oc('\n');
  os("DRIVER "); ou(driver_ops()); os("  (per generic round: call and return 2, iota XORs with the all-ones register)\n");
  os("TOTAL "); ou(tot); oc('\n');
  if(tx[1]+tx[2]+tx[3]+tx[4]+driver_ops()!=tot) die("total mismatch");
  os("closing NOTs (last body to bank X polarity) "); ou(nfix); os(" ; trick rows (all blocks built once) "); ou(ntrick); oc('\n');
  os("code instructions "); ou(ci); oc('\n');
  os("nodes created pre-DCE "); ou(pre); os(" ; ring peak "); ou(maxring); os(" of "); ou(W); os(" ; linear forms "); ou(maxform); os(" of "); ou(MAXF); oc('\n');
  os("build parameters KB "); ou(KB); os(" OPTIT "); ou(OPTIT); os(" TOPK "); ou(TOPK); os(" R1SWEEPS "); ou(R1SWEEPS); oc(10);
  os("constants trial "); ou(bestt); os(" of "); ou(ntr); os(" ; optmode "); ou(optmode); os(" ; round-1 greedy gain "); ou(r1gain); oc('\n');
  for(int r=2;r<=BRE;r++){ os("plan br"); ou(r); os(" predicted row cost "); ou(pol_pred[r]); os(" theta NOTs "); ou(pol_nots[r]); os(" free polarities set "); ou(pol_phi[r]); oc('\n'); }
  os("generator peak RSS (VmHWM, this process image) "); ou(hwm); os(" KiB = "); ou(hwm*1024); os(" bytes (limit 1048576)\n");
  oflush();
  return 0;
}
```

The self-test, compiled with `-DRR=16 -DKB=8`: `selftest kat` prints 300 known answers; `selftest run 4 [seed]` runs the chained check.

```c
/* selftest.c - checks the emitted LS1 straight line (prog.bin + meta.txt) against a plain
 * lane-wise Keccak reference written here (rounds 0..R-1, SHA3 padding, 136-byte rate).
 *   selftest kat            : prints "hexmsg digest24 digest6" for 300 deterministic messages
 *                             (lengths 0..299) for comparison with hashlib / the organizer reference
 *   selftest run [nbatch]   : nbatch x 256 random points, 4 chained steps each; counts mismatches
 *                             of the program output against F(u) = SHA3-256-r8(m(u)) ^ PD.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef uint64_t u64;
#ifndef RR
#define RR 8
#endif

static const u64 RC[24]={0x0000000000000001ULL,0x0000000000008082ULL,0x800000000000808aULL,0x8000000080008000ULL,
 0x000000000000808bULL,0x0000000080000001ULL,0x8000000080008081ULL,0x8000000000008009ULL,0x000000000000008aULL,
 0x0000000000000088ULL,0x0000000080008009ULL,0x000000008000000aULL,0x000000008000808bULL,0x800000000000008bULL,
 0x8000000000008089ULL,0x8000000000008003ULL,0x8000000000008002ULL,0x8000000000000080ULL,0x000000000000800aULL,
 0x800000008000000aULL,0x8000000080008081ULL,0x8000000000008080ULL,0x0000000080000001ULL,0x8000000080008008ULL};
static const int RHO[25]={0,1,62,28,27, 36,44,6,55,20, 3,10,43,25,39, 41,45,15,21,8, 18,2,61,56,14}; /* index x+5y */
static u64 rotl(u64 v,int r){ return r? (v<<r)|(v>>(64-r)) : v; }

static void keccakf(u64 A[25], int rounds){
  for(int r=0;r<rounds;r++){
    u64 C[5],D[5],B[25];
    for(int x=0;x<5;x++) C[x]=A[x]^A[x+5]^A[x+10]^A[x+15]^A[x+20];
    for(int x=0;x<5;x++) D[x]=C[(x+4)%5]^rotl(C[(x+1)%5],1);
    for(int i=0;i<25;i++) A[i]^=D[i%5];
    for(int x=0;x<5;x++) for(int y=0;y<5;y++) B[y+5*((2*x+3*y)%5)]=rotl(A[x+5*y],RHO[x+5*y]);
    for(int y=0;y<5;y++) for(int x=0;x<5;x++) A[x+5*y]=B[x+5*y]^((~B[(x+1)%5+5*y])&B[(x+2)%5+5*y]);
    A[0]^=RC[r];
  }
}
static void sha3_256r(const uint8_t *m, size_t len, int rounds, uint8_t out[32]){
  u64 A[25]; memset(A,0,sizeof A);
  uint8_t blk[136]; size_t off=0;
  for(;;){
    size_t rem=len-off;
    if(rem>=136){ memcpy(blk,m+off,136); off+=136; }
    else { memset(blk,0,136); memcpy(blk,m+off,rem); blk[rem]^=0x06; blk[135]^=0x80; off=len+1; }
    for(int i=0;i<17;i++){ u64 w=0; for(int k=0;k<8;k++) w|=(u64)blk[8*i+k]<<(8*k); A[i]^=w; }
    keccakf(A,rounds);
    if(off>len) break;
  }
  for(int i=0;i<32;i++) out[i]=(uint8_t)(A[i/8]>>(8*(i%8)));
}

#ifndef KB
#define KB 6
#endif
#define XB 256
#define YB 1856
static u64 KL[25], PD[4];
static uint8_t *blk[KB+2]; static long nins[KB+2];   /* 0: P, 1..KB: bodies, KB+1: E */
static long executed;
static void load(void){
  FILE *f=fopen("meta.txt","r"); if(!f){ perror("meta.txt"); exit(2); }
  char line[512];
  while(fgets(line,sizeof line,f)){
    int l; unsigned long long v,a,b,c,d;
    if(sscanf(line,"lane %d %llx",&l,&v)==2) KL[l]=v;
    else if(sscanf(line,"pd %llx %llx %llx %llx",&a,&b,&c,&d)==4){ PD[0]=a;PD[1]=b;PD[2]=c;PD[3]=d; }
  }
  fclose(f);
  for(int i=0;i<KB+2;i++){ char fn[16]; if(i==0) strcpy(fn,"P.bin"); else if(i==KB+1) strcpy(fn,"E.bin"); else sprintf(fn,"B%d.bin",i);
    f=fopen(fn,"rb"); if(!f){ perror(fn); exit(2); } fseek(f,0,SEEK_END); long n=ftell(f); fseek(f,0,SEEK_SET);
    if(n%5){ fprintf(stderr,"bad size %s\n",fn); exit(2); } nins[i]=n/5; blk[i]=malloc(n); if(fread(blk[i],1,n,f)!=(size_t)n) exit(2); fclose(f); }
}
/* message m(u): 128 bytes = lanes 0..15 */
static void msg_of(const u64 u[4], uint8_t m[128]){
  u64 L[16]; for(int i=0;i<16;i++) L[i]=KL[i];
  L[1]=u[0]; L[6]=u[1]; L[11]=u[0]^u[1]^KL[11];
  L[4]=u[2]; L[9]=u[3]; L[14]=u[2]^u[3]^KL[14];
  for(int i=0;i<128;i++) m[i]=(uint8_t)(L[i/8]>>(8*(i%8)));
}
static void Fref(const u64 u[4], u64 o[4]){
  uint8_t m[128], d[32]; msg_of(u,m); sha3_256r(m,128,RR,d);
  for(int i=0;i<4;i++){ u64 w=0; for(int k=0;k<8;k++) w|=(u64)d[8*i+k]<<(8*k); o[i]=w^PD[i]; }
}
typedef struct { u64 w[4]; } W256;
static W256 R[4096];
static void run_blk(int bi){
  const uint8_t *p=blk[bi]; executed+=nins[bi];
  for(long i=0;i<nins[bi];i++,p+=5){
    u64 w=(u64)p[0]|(u64)p[1]<<8|(u64)p[2]<<16|(u64)p[3]<<24|(u64)p[4]<<32;
    int op=w&7, d=(w>>3)&4095, a=(w>>15)&4095, b=(w>>27)&4095; W256 t;
    for(int k=0;k<4;k++){ u64 x=R[a].w[k], y=R[b].w[k];
      t.w[k]= op==0? x^y : op==1? x&y : op==2? x|y : ~x; }
    if(op>3 || d>=4096){ fprintf(stderr,"bad instr %ld\n",i); exit(3); }
    R[d]=t;
  }
}
/* one step: P, the generic rounds 2..RR-2 through the cycle of bodies (call + return + iota XORs with all-ones), E */
static void run_prog(void){
  run_blk(0);
  for(int r=2;r<=RR-2;r++){ int j=(r-2)%KB+1, ob=(j&1)? YB : XB; run_blk(j); executed+=2;
    for(int z=0;z<64;z++) if((RC[r]>>z)&1){ for(int k=0;k<4;k++) R[ob+z].w[k]^=~0ULL; executed++; } }
  run_blk(KB+1);
}
static u64 rs=0x0123456789abcdefULL;
static u64 xr(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }

int main(int argc,char **argv){
  if(argc>1 && !strcmp(argv[1],"kat")){
    for(int len=0;len<300;len++){
      uint8_t m[300],d24[32],d6[32]; for(int i=0;i<len;i++) m[i]=(uint8_t)xr();
      sha3_256r(m,len,24,d24); sha3_256r(m,len,RR,d6);
      for(int i=0;i<len;i++) printf("%02x",m[i]); printf(" ");
      for(int i=0;i<32;i++) printf("%02x",d24[i]); printf(" ");
      for(int i=0;i<32;i++) printf("%02x",d6[i]); printf("\n");
    }
    return 0;
  }
  int nb= argc>2? atoi(argv[2]) : 2;
  if(argc>3) rs=strtoull(argv[3],0,0);
  load();
  long mism=0, evals=0;
  for(int bt=0;bt<nb;bt++){
    static u64 U[256][4];
    for(int t=0;t<256;t++) for(int i=0;i<4;i++) U[t][i]=xr();
    for(int j=0;j<256;j++) for(int k=0;k<4;k++){ u64 w=0; for(int b=0;b<64;b++){ int t=64*k+b; w|=((U[t][j>>6]>>(j&63))&1)<<b; } R[j].w[k]=w; }
    for(int step=0;step<4;step++){
      run_prog();
      for(int t=0;t<256;t++){
        u64 o[4], g[4]={0,0,0,0}; Fref(U[t],o);
        for(int j=0;j<256;j++) g[j>>6]|=((R[j].w[t>>6]>>(t&63))&1)<<(j&63);
        if(memcmp(o,g,32)) { if(mism<5) fprintf(stderr,"mismatch batch %d step %d trail %d\n",bt,step,t); mism++; }
        evals++;
        memcpy(U[t],o,32);   /* chain on the reference value */
      }
    }
  }
  printf("selftest: %ld chained evaluations (%d batches x 256 trails x 4 steps), %ld mismatches, %ld operations per step executed\n",evals,nb,mism,executed/(4L*nb));
  return mism?1:0;
}
```

The generator's ledger (standard output of the charged run, the trial lines of the cheap stage left out):

```
plan trial 3600 cheap 96152 full 93945
plan trial 119 cheap 96169 full 94029
plan trial 4064 cheap 96172 full 93993
plan trial 3018 cheap 96179 full 94049
plan trial 3806 cheap 96187 full 94025
plan trial 3087 cheap 96188 full 93983
plan trial 3720 cheap 96188 full 94074
plan trial 627 cheap 96196 full 94023
LS1 LOOP step ledger (256 lanes, one chain step, 16 rounds), generator gen4: prefix P (rounds 0,1), a cycle of 8 bodies over the generic rounds 2..14, last round E
block P runs 1 XOR 3118 AND 912 OR 688 NOT 224 total 4942 ; instructions 4942 max live 1719 highest register+1 2361
block B1 runs 2 XOR 4823 AND 938 OR 662 NOT 195 total 6618 ; instructions 6618 max live 1925 highest register+1 3525
block B2 runs 2 XOR 4835 AND 941 OR 659 NOT 199 total 6634 ; instructions 6634 max live 1925 highest register+1 3525
block B3 runs 2 XOR 4833 AND 938 OR 662 NOT 192 total 6625 ; instructions 6625 max live 1925 highest register+1 3525
block B4 runs 2 XOR 4820 AND 932 OR 668 NOT 213 total 6633 ; instructions 6633 max live 1925 highest register+1 3525
block B5 runs 2 XOR 4828 AND 936 OR 664 NOT 196 total 6624 ; instructions 6624 max live 1925 highest register+1 3525
block B6 runs 1 XOR 4826 AND 938 OR 662 NOT 210 total 6636 ; instructions 6636 max live 1925 highest register+1 3525
block B7 runs 1 XOR 4827 AND 934 OR 666 NOT 215 total 6642 ; instructions 6642 max live 1925 highest register+1 3525
block B8 runs 1 XOR 4820 AND 859 OR 741 NOT 484 total 6904 ; instructions 6904 max live 1925 highest register+1 3525
block E runs 1 XOR 2177 AND 142 OR 114 NOT 42 total 2475 ; instructions 2475 max live 1600 highest register+1 3456
XOR 68046
AND 13155
OR  9501
NOT 3165
DRIVER 78  (per generic round: call and return 2, iota XORs with the all-ones register)
TOTAL 93945
closing NOTs (last body to bank X polarity) 33 ; trick rows (all blocks built once) 2342
code instructions 60733
nodes created pre-DCE 60733 ; ring peak 7162 of 8192 ; linear forms 1892 of 1920
build parameters KB 8 OPTIT 80000000 TOPK 8 R1SWEEPS 3
constants trial 3600 of 4096 ; optmode 3 ; round-1 greedy gain 89
plan br2 predicted row cost 1742 theta NOTs 76 free polarities set 48
plan br3 predicted row cost 1754 theta NOTs 80 free polarities set 22
plan br4 predicted row cost 1756 theta NOTs 69 free polarities set 19
plan br5 predicted row cost 1752 theta NOTs 81 free polarities set 22
plan br6 predicted row cost 1740 theta NOTs 84 free polarities set 28
plan br7 predicted row cost 1753 theta NOTs 83 free polarities set 24
plan br8 predicted row cost 1752 theta NOTs 90 free polarities set 22
plan br9 predicted row cost 2020 theta NOTs 84 free polarities set 26
plan br10 predicted row cost 263 theta NOTs 36 free polarities set 0
generator peak RSS (VmHWM, this process image) 256 KiB = 262144 bytes (limit 1048576)
worker peak RSS (getrusage via wait4, worker forked from the 1-page parent) 256 KiB = 262144 bytes (limit 1048576)
```

## Appendix C. The measured check of H_rand (hrand5.c)

Compiled with `-DRR=16 -DKB=8 -lm`, run in the row's directory.

```c
/* hrand5.c - hrand_test.c of 71fefe66 run on the gen4 blocks (P, B1..BKB, E as the step executes them): measured checks of
 * the premise H_rand for the chain function F.
 * Executes the emitted straight line (256 lanes per step) and counts, among M = 2^24 evaluations,
 * the pairs of images that agree on a 32-bit window (low bits 0..31, bits 128..159, top bits 224..255):
 *   A: uniform random inputs (independent images expected: C(M,2)/2^32 pairs, Poisson)
 *   B: structured inputs R + i, i < M (the start pattern of the search: consecutive integers)
 *   C: iterates: 256 chains of 65,536 chained steps from random starts (the points a walk evaluates)
 * and D: single-bit input differences: for each of the 256 input bits j, 4,096 random u, the count of output bit k
 *   flipping in F(u) ^ F(u ^ e_j), for all 65,536 (j,k) cells; reports the largest |z| (binomial 4096, 1/2).
 * Usage: hrand5 [seed]   (reads the blocks from the current directory) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
typedef uint64_t u64;
#ifndef KB
#define KB 8
#endif
#ifndef RR
#define RR 24
#endif
#define XB 256
#define YB 1856
static const u64 RC[24]={0x0000000000000001ULL,0x0000000000008082ULL,0x800000000000808aULL,0x8000000080008000ULL,
 0x000000000000808bULL,0x0000000080000001ULL,0x8000000080008081ULL,0x8000000000008009ULL,0x000000000000008aULL,
 0x0000000000000088ULL,0x0000000080008009ULL,0x000000008000000aULL,0x000000008000808bULL,0x800000000000008bULL,
 0x8000000000008089ULL,0x8000000000008003ULL,0x8000000000008002ULL,0x8000000000000080ULL,0x000000000000800aULL,
 0x800000008000000aULL,0x8000000080008081ULL,0x8000000000008080ULL,0x0000000080000001ULL,0x8000000080008008ULL};
static uint8_t *blk[KB+2]; static long nins[KB+2];
typedef struct { u64 w[4]; } W256;
static W256 R[4096];
static void load(void){
  for(int i=0;i<KB+2;i++){ char fn[16]; if(i==0) strcpy(fn,"P.bin"); else if(i==KB+1) strcpy(fn,"E.bin"); else sprintf(fn,"B%d.bin",i);
    FILE *f=fopen(fn,"rb"); if(!f){ perror(fn); exit(2); } fseek(f,0,SEEK_END); long n=ftell(f); fseek(f,0,SEEK_SET);
    nins[i]=n/5; blk[i]=malloc(n); if(fread(blk[i],1,n,f)!=(size_t)n) exit(2); fclose(f); }
}
static void run_blk(int bi){
  const uint8_t *p=blk[bi];
  for(long i=0;i<nins[bi];i++,p+=5){
    u64 w=(u64)p[0]|(u64)p[1]<<8|(u64)p[2]<<16|(u64)p[3]<<24|(u64)p[4]<<32;
    int op=w&7, d=(w>>3)&4095, a=(w>>15)&4095, b=(w>>27)&4095;
    W256 *x=&R[a],*y=&R[b],t;
    switch(op){ case 0: for(int k=0;k<4;k++) t.w[k]=x->w[k]^y->w[k]; break;
                case 1: for(int k=0;k<4;k++) t.w[k]=x->w[k]&y->w[k]; break;
                case 2: for(int k=0;k<4;k++) t.w[k]=x->w[k]|y->w[k]; break;
                default: for(int k=0;k<4;k++) t.w[k]=~x->w[k]; }
    R[d]=t;
  }
}
/* one step as the attack executes it: P, the bodies as called with the iota XORs, E */
static void run_prog(void){
  run_blk(0);
  for(int r=2;r<=RR-2;r++){ int j=(r-2)%KB+1, ob=(j&1)? YB : XB; run_blk(j);
    for(int z=0;z<64;z++) if((RC[r]>>z)&1) for(int k=0;k<4;k++) R[ob+z].w[k]^=~0ULL; }
  run_blk(KB+1);
}
static u64 sm;
static u64 rnd(void){ u64 z=(sm+=0x9E3779B97F4A7C15ULL); z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL; z=(z^(z>>27))*0x94D049BB133111EBULL; return z^(z>>31); }
/* set lane t (0..255) of the 256 input planes to point u[4] */
static void set_point(int t,const u64 u[4]){ for(int j=0;j<256;j++){ u64 bit=(u[j>>6]>>(j&63))&1; u64 m=1ULL<<(t&63); R[j].w[t>>6]=(R[j].w[t>>6]&~m)|(bit<<(t&63)); } }
static void get_point(int t,u64 o[4]){ o[0]=o[1]=o[2]=o[3]=0; for(int j=0;j<256;j++) o[j>>6]|=((R[j].w[t>>6]>>(t&63))&1)<<(j&63); }
static uint32_t window(int t,int lo){ uint32_t v=0; for(int j=0;j<32;j++) v|=(uint32_t)((R[lo+j].w[t>>6]>>(t&63))&1)<<j; return v; }
static int cmpu(const void*a,const void*b){ uint32_t x=*(const uint32_t*)a,y=*(const uint32_t*)b; return x<y?-1:x>y; }
static double pairs(uint32_t *k,long M){ qsort(k,M,4,cmpu); double p=0; long i=0; while(i<M){ long j=i; while(j<M&&k[j]==k[i]) j++; double c=j-i; p+=c*(c-1)/2; i=j; } return p; }
#define LM 24
static uint32_t *K0,*K1,*K2;
static void report(const char *name,long M){
  double E=(double)M*(M-1)/2/4294967296.0;
  double p0=pairs(K0,M),p1=pairs(K1,M),p2=pairs(K2,M);
  printf("%s: M=2^%d, pairs agreeing on 32 bits: low %.0f, mid %.0f, top %.0f; expected %.1f each (sd %.1f); ratios %.4f %.4f %.4f; z %.2f %.2f %.2f\n",
    name,LM,p0,p1,p2,E,sqrt(E),p0/E,p1/E,p2/E,(p0-E)/sqrt(E),(p1-E)/sqrt(E),(p2-E)/sqrt(E));
}
int main(int argc,char**argv){
  sm= argc>1? strtoull(argv[1],0,0) : 0x15c0ffee;
  load();
  long M=1L<<LM, S=M/256;
  K0=malloc(M*4); K1=malloc(M*4); K2=malloc(M*4);
  /* A: uniform random inputs */
  for(long s=0;s<S;s++){
    for(int j=0;j<256;j++) for(int k=0;k<4;k++) R[j].w[k]=rnd();
    run_prog();
    for(int t=0;t<256;t++){ long e=s*256+t; K0[e]=window(t,0); K1[e]=window(t,128); K2[e]=window(t,224); }
  }
  report("A uniform inputs",M);
  /* B: consecutive inputs R0 + i */
  u64 R0[4]={rnd(),rnd(),rnd(),rnd()};
  for(long s=0;s<S;s++){
    for(int t=0;t<256;t++){ u64 i=(u64)(s*256+t), u[4]; u[0]=R0[0]+i; u64 c=u[0]<R0[0]; for(int k=1;k<4;k++){ u[k]=R0[k]+c; c=c&&u[k]==0; } set_point(t,u); }
    run_prog();
    for(int t=0;t<256;t++){ long e=s*256+t; K0[e]=window(t,0); K1[e]=window(t,128); K2[e]=window(t,224); }
  }
  report("B consecutive inputs R+i",M);
  /* C: iterates of 256 chains */
  for(int j=0;j<256;j++) for(int k=0;k<4;k++) R[j].w[k]=rnd();
  for(long s=0;s<S;s++){
    run_prog();
    for(int t=0;t<256;t++){ long e=s*256+t; K0[e]=window(t,0); K1[e]=window(t,128); K2[e]=window(t,224); }
  }
  report("C chained iterates (256 chains x 65536 steps)",M);
  /* D: single-bit input differences */
  static uint32_t cnt[256][256]; memset(cnt,0,sizeof cnt);
  int NS=4096;
  for(int j=0;j<256;j++){
    for(int s=0;s<NS/128;s++){
      u64 u[128][4];
      for(int t=0;t<128;t++){ for(int k=0;k<4;k++) u[t][k]=rnd(); u64 v[4]; memcpy(v,u[t],32); set_point(t,v); v[j>>6]^=1ULL<<(j&63); set_point(128+t,v); }
      run_prog();
      for(int t=0;t<128;t++){ u64 a[4],b[4]; get_point(t,a); get_point(128+t,b); for(int k=0;k<256;k++) cnt[j][k]+=((a[k>>6]^b[k>>6])>>(k&63))&1; }
    }
  }
  double zmax=0; int jm=0,km=0; double sum=0;
  for(int j=0;j<256;j++) for(int k=0;k<256;k++){ double z=(cnt[j][k]-NS/2.0)/sqrt(NS/4.0); sum+=z*z; if(fabs(z)>zmax){ zmax=fabs(z); jm=j; km=k; } }
  printf("D single-bit differences: 65536 cells x %d pairs, max |z| %.2f at input bit %d output bit %d (largest of 65536 normal cells is about 4.4); mean z^2 %.4f (expected 1)\n",NS,zmax,jm,km,sum/65536);
  return 0;
}
```

## Appendix D. The other code (other5.py), its tests (other5_test.py) and their results

### D.1 other5.py

`params.json` of this package:

```
{"NR": 16, "HF": 112, "DPLO": 144, "DK": 10, "DT": 936, "S": 16280, "U": 65120, "SB": 14, "IDB": 16, "W": 1267650600228229401496703205376, "J": 47051, "LRC": 59644228391338421569821382516146176, "Tb": 1328093265282585793353186825841147904, "HMAX": 64832097656381478934929308431417345, "PFLO": 240, "PFN": 16, "REGTOP": 3525, "KB": 8}
```

```python
#!/usr/bin/env python3
# other4.py - the non-straight-line code of LS1 (setup, loop control, hit handler, DP handler with the packed table,
# restart, replay, final output), written as real instructions of the machine of proof.md Section 3.5,
# plus the machine (an interpreter that executes the emitted bytes) and the counting of the operations.
#
#   python3 other4.py build [meta.txt]    reads params.json (NR, S, U, SB, IDB, LRC, Tb, HMAX, DPLO, DK, DT, PFLO, PFN), writes other.bin
#                                          (the 32-byte instructions), pf.bin (the 15 prefilter ORs, 5 bytes each), data.bin
#                                          (the 16-word data image from meta.txt) and counts.txt (instruction counts and the
#                                          operation count of every routine, read from the emitted code)
#   other4_test.py                         routine tests and end-to-end runs of the emitted program (reduced width)
#
# Table: S words of 256 bits, four records of 64 bits per word (bits 64 k .. 64 k + 63); a record is
#   1 | (bits 0..KEYB-1 of the trail's end) << 1 | (trail number) << (KEYB + 1), KEYB = 63 - IDB, never zero; an empty record
#   is zero.  Every probe loads the whole word and extracts each record with charged shifts and masks; an insertion rewrites
#   the word.
# Distinguished point (DP): the point x (256-bit value, bit j = plane j) is a DP when x < THR, THR = DT << (DPLO - DK):
#   the planes DPLO..255 are zero and the DK planes below them, read as a number, are less than DT.  theta = DT 2^-(256-DPLO+DK).
#   No trail is cut: a walk runs until its DP; the replay refuses trails of more than LRC evaluations.
#
# Machine (collision-frontier-v5 256-bit word RAM, the declared register file of NREGS registers, NREGS = REGTOP + 11):
#   every instruction below costs one word operation, except PERM, which costs one unit (UNIT = 271 NR operations, the model's
#   rule: one selected-round sponge permutation is one unit).  Straight-line instructions (5 bytes: XOR AND OR NOT on
#   registers) cost one operation each.  Other instructions are 32 bytes: op(1) d(2) a(2) b(2) 0(1) imm(24, 192 bits).
#   Words are 256 bits, arithmetic is mod 2^256, shifts take amount R[b] & 255 (or an immediate), compares give 0 or 1,
#   a conditional branch tests a register for zero and is always the instruction right after the compare that set it
#   (audited below), memory M[] is word addressed with address R[a] + imm, PERM a applies Keccak-f rounds 0..NR-1 to the
#   25 lanes in R[a]..R[a+6] (lane l = bits 64 (l mod 4) .. +63 of word R[a + l div 4]).
#   The straight-line block sits in code memory in front of instruction SLPOS: it is entered by fall-through or by a
#   jump to it, has no branches, and control leaves it by fall-through into instruction SLPOS.
import sys, struct, hashlib, os, json

M256 = (1 << 256) - 1
M64 = (1 << 64) - 1
PARAMS = json.load(open(os.environ.get('LS1_PARAMS', 'params.json')))
NR = PARAMS['NR']                                  # rounds of the target
UNIT = 271 * NR                                    # the cost model's price of one NR-round permutation (word operations)
RB, RPW = 64, 4                                    # record width; records per word
RM = (1 << RB) - 1


def keyb(Pm): return RB - 1 - Pm['IDB']            # key bits of a record: 1 + KEYB + IDB = 64


def thr(Pm): return Pm['DT'] << (Pm['DPLO'] - Pm['DK'])    # the DP is x < THR (DK = 0: DT = 1)

# ---- ISA ----
XOR, AND, OR, NOT, ADD, SUB, SHL, SHR, EQ, LT, MOV = range(11)
ADDI, SUBI, SHLI, SHRI, ANDI, EQI, LTI, MOVI = range(11, 19)
LD, ST, LDA, BNZ, BZ, JMP, JAL, JR, RND, PERM, HALT = range(19, 30)
NAMES = 'XOR AND OR NOT ADD SUB SHL SHR EQ LT MOV ADDI SUBI SHLI SHRI ANDI EQI LTI MOVI LD ST LDA BNZ BZ JMP JAL JR RND PERM HALT'.split()
CMPOPS = (EQ, LT, EQI, LTI)

# ---- registers ----
REGTOP = PARAMS['REGTOP']                                             # first register above every register the blocks name
C, NXT, IDN, RHO, ONES, PF, H, LR, LR2, ZERO, LR3 = range(REGTOP, REGTOP + 11)   # state; LR3 links the body calls of the step
(L, DPM, C1, ACC, TT, REC, SLOT, TR, F, X, Y, LV, NP, NM, ONEB, V, MN, E, PTR, SS, ID, STV) = range(256, 278)
(P, Q, N, MM, LA, LB, UU, FF, PDR, X0, X1, X2, X3, TQ, FP) = range(280, 295)
Z = 295
W0 = 300                                                              # W0..W6, the 1600-bit state of evalF
NREGS = REGTOP + 11
KB = PARAMS['KB']                                  # bodies in the cycle of the generic rounds
XB, YB = 256, 1856                                 # the two state banks (planes 0..1599)


class Asm:
    def __init__(s):
        s.ins = []; s.lab = {}; s.fix = []

    def pc(s): return len(s.ins)

    def label(s, n):
        assert n not in s.lab, n
        s.lab[n] = len(s.ins)

    def e(s, op, d=0, a=0, b=0, imm=0, tgt=None):
        s.ins.append([op, d, a, b, imm])
        if tgt is not None: s.fix.append((len(s.ins) - 1, tgt))

    def resolve(s):
        for i, t in s.fix: s.ins[i][4] = s.lab[t]
        for x in s.ins: assert 0 <= x[4] < 1 << 192 and max(x[1:4]) < NREGS

    # plain instructions
    def xor(s, d, a, b): s.e(XOR, d, a, b)
    def and_(s, d, a, b): s.e(AND, d, a, b)
    def or_(s, d, a, b): s.e(OR, d, a, b)
    def not_(s, d, a): s.e(NOT, d, a)
    def add(s, d, a, b): s.e(ADD, d, a, b)
    def sub(s, d, a, b): s.e(SUB, d, a, b)
    def shl(s, d, a, b): s.e(SHL, d, a, b)
    def shr(s, d, a, b): s.e(SHR, d, a, b)
    def mov(s, d, a): s.e(MOV, d, a)
    def addi(s, d, a, i): s.e(ADDI, d, a, 0, i)
    def subi(s, d, a, i): s.e(SUBI, d, a, 0, i)
    def shli(s, d, a, i): s.e(SHLI, d, a, 0, i)
    def shri(s, d, a, i): s.e(SHRI, d, a, 0, i)
    def andi(s, d, a, i): s.e(ANDI, d, a, 0, i)
    def movi(s, d, i): s.e(MOVI, d, 0, 0, i)
    def ld(s, d, a, i): s.e(LD, d, a, 0, i)
    def st(s, a, i, b): s.e(ST, 0, a, b, i)
    def lda(s, d, i): s.e(LDA, d, 0, 0, i)
    def rnd(s, d): s.e(RND, d)
    def permute(s, a): s.e(PERM, 0, a)
    def halt(s, code): s.e(HALT, 0, 0, 0, code)
    def jmp(s, t): s.e(JMP, tgt=t)
    def jal(s, d, t): s.e(JAL, d, tgt=t)
    def jr(s, a): s.e(JR, 0, a)

    # compare + branch pairs (a branch is always right after its compare)
    def _br(s, brop, t): s.e(brop, 0, F, 0, 0, t)
    def jeq(s, a, b, t): s.e(EQ, F, a, b); s._br(BNZ, t)
    def jne(s, a, b, t): s.e(EQ, F, a, b); s._br(BZ, t)
    def jeqi(s, a, i, t): s.e(EQI, F, a, 0, i); s._br(BNZ, t)
    def jnei(s, a, i, t): s.e(EQI, F, a, 0, i); s._br(BZ, t)
    def jlt(s, a, b, t): s.e(LT, F, a, b); s._br(BNZ, t)
    def jge(s, a, b, t): s.e(LT, F, a, b); s._br(BZ, t)
    def jlti(s, a, i, t): s.e(LTI, F, a, 0, i); s._br(BNZ, t)
    def jgei(s, a, i, t): s.e(LTI, F, a, 0, i); s._br(BZ, t)


def build_state(A, MISC):
    """W0..W6 := the 1600-bit state of the one-block message m(u), u in UU (26 instructions)."""
    for i in range(7): A.lda(W0 + i, MISC + i)
    A.andi(X0, UU, M64); A.shri(X1, UU, 64); A.andi(X1, X1, M64); A.shri(X2, UU, 128); A.andi(X2, X2, M64); A.shri(X3, UU, 192)
    A.shli(TQ, X0, 64); A.xor(W0, W0, TQ)                    # lane 1  = u0
    A.shli(TQ, X1, 128); A.xor(W0 + 1, W0 + 1, TQ)           # lane 6  = u1
    A.xor(W0 + 1, W0 + 1, X2)                                # lane 4  = u2
    A.shli(TQ, X3, 64); A.xor(W0 + 2, W0 + 2, TQ)            # lane 9  = u3
    A.xor(TQ, X0, X1); A.shli(TQ, TQ, 192); A.xor(W0 + 2, W0 + 2, TQ)   # lane 11 = u0 ^ u1 ^ K11
    A.xor(TQ, X2, X3); A.shli(TQ, TQ, 128); A.xor(W0 + 3, W0 + 3, TQ)   # lane 14 = u2 ^ u3 ^ K14


def program(Pm):
    """Pm: S (table words), U (trail limit), SB (slot bits), IDB (trail number bits), LRC (replay cap), Tb, HMAX, DPLO, DK, DT,
    PFLO, PFN, WTEST (None or width)."""
    S, U, SB, LRC, Tb, HMAX = Pm['S'], Pm['U'], Pm['SB'], Pm['LRC'], Pm['Tb'], Pm['HMAX']
    DPLO, DK, DT, PFLO, PFN, WT = Pm['DPLO'], Pm['DK'], Pm['DT'], Pm['PFLO'], Pm['PFN'], Pm.get('WTEST')
    IDB = Pm['IDB']; KEYB = keyb(Pm); THR = thr(Pm)
    assert (1 << SB) <= 2 * S and S % 8 == 0 and PFLO > DPLO + 1 and U <= RPW * S and U <= 1 << IDB and (WT or DPLO - DK > KEYB)
    assert (DK == 0 and DT == 1) or (DK >= 1 and 0 < DT < 1 << DK and DPLO >= DK)
    LID, LST, MISC = S, S + 256, S + 512
    OUT = MISC + 8
    A = Asm()
    # ---------------- setup ----------------
    A.label('start')
    A.rnd(RHO); A.movi(IDN, 256); A.movi(H, 0); A.movi(C, 0); A.movi(ZERO, 0); A.not_(ONES, ZERO)
    A.movi(PTR, 0)
    A.label('clr')                                           # TAB := 0, eight words per pass
    for k in range(8): A.st(PTR, k, ZERO)
    A.addi(PTR, PTR, 8); A.jlti(PTR, S, 'clr')
    A.movi(L, 0)
    A.label('iw')                                            # for l < 256: LID[l] := l; LST[l] := 0; lane l := rho + l
    A.add(NP, RHO, L); A.st(L, LID, L); A.st(L, LST, ZERO); A.jal(LR, 'setwalk')
    A.addi(L, L, 1); A.jlti(L, 256, 'iw')
    # ---------------- the loop: the straight line (SLPOS) then the tests ----------------
    A.label('loop')
    A.jeq(PF, ONES, 'cont')                                  # prefilter test (2)
    # ---------------- hit: some walk has planes PFLO..PFLO+PFN-1 zero ----------------
    A.label('hit')
    A.addi(H, H, 1); A.jlti(H, HMAX + 1, 'h1'); A.halt(10); A.label('h1')      # hit counter and abort (F5)
    A.or_(SS, DPLO, DPLO + 1)
    for j in range(DPLO + 2, PFLO): A.or_(SS, SS, j)         # OR of the planes DPLO..PFLO-1
    A.or_(DPM, PF, SS); A.not_(DPM, DPM)                     # DPM: walks with planes DPLO..255 zero
    if DK:                                                   # keep the walks whose planes DPLO-1 .. DPLO-DK, as a number, are < DT
        bits = [(DT >> (DK - 1 - i)) & 1 for i in range(DK)]  # most significant first: plane DPLO - 1 - i
        last1 = max(i for i in range(DK) if bits[i]); first = True
        for i in range(last1 + 1):
            p = DPLO - 1 - i
            A.not_(X, p)
            if bits[i]:
                if first: A.and_(Y, DPM, X); first = False   # lt := eq and not p
                else: A.and_(X, DPM, X); A.or_(Y, Y, X)      # lt := lt or (eq and not p)
                if i < last1: A.and_(DPM, DPM, p)            # eq := eq and p
            else: A.and_(DPM, DPM, X)                        # eq := eq and not p
        A.mov(DPM, Y)                                        # DPM := lt
    A.addi(C1, C, 1)                                         # steps completed including this one
    A.label('dpl')
    A.jeqi(DPM, 0, 'cont')
    A.label('dp1')                                           # ---- one DP walk: l := lowest set bit of DPM ----
    A.movi(L, 0); A.mov(X, DPM)
    for i, sh in enumerate((128, 64, 32, 16, 8, 4, 2, 1)):
        A.andi(Y, X, (1 << sh) - 1); A.jnei(Y, 0, 'ct%d' % i); A.shri(X, X, sh); A.addi(L, L, sh); A.label('ct%d' % i)
    A.subi(Y, DPM, 1); A.and_(DPM, DPM, Y)                   # clear that bit
    A.label('gather')                                        # ACC := the 256-bit point of walk l (bit j = plane j, bit l)
    A.shr(ACC, 0, L); A.andi(ACC, ACC, 1)
    for j in range(1, 256):
        A.shr(TT, j, L); A.andi(TT, TT, 1); A.shli(TT, TT, j); A.or_(ACC, ACC, TT)
    A.label('record')                                        # REC := 1 | (end bits 0..67) << 1 | trail number << 69
    A.andi(REC, ACC, (1 << KEYB) - 1); A.shli(REC, REC, 1); A.addi(REC, REC, 1)
    A.ld(ID, L, LID); A.shli(ID, ID, KEYB + 1); A.or_(REC, REC, ID)
    A.andi(SLOT, ACC, (1 << SB) - 1); A.jlti(SLOT, S, 'sl_ok'); A.subi(SLOT, SLOT, S); A.label('sl_ok')
    A.label('probe')                                         # one table word: its four records in order
    A.ld(TR, SLOT, 0)
    for k in range(RPW):
        if k: A.shri(Y, TR, RB * k); A.andi(X, Y, RM)
        else: A.andi(X, TR, RM)
        A.jeqi(X, 0, 'empty%d' % k)
        A.xor(X, X, REC); A.andi(X, X, (1 << (KEYB + 1)) - 1); A.jeqi(X, 0, 'match%d' % k)
    A.label('pnext')
    A.addi(SLOT, SLOT, 1); A.jnei(SLOT, S, 'probe')
    A.movi(SLOT, 0); A.jmp('probe')
    for k in range(RPW):                                     # insertion into the first empty record of the word
        A.label('empty%d' % k)
        if k: A.shli(X, REC, RB * k); A.or_(TR, TR, X)
        else: A.or_(TR, TR, REC)
        A.st(SLOT, 0, TR); A.jmp('ins')
    A.label('ins')
    A.mov(LV, C1); A.jal(LR, 'restart'); A.jmp('dpl')
    for k in range(RPW):                                     # a record with the same KEYB end bits: X := its trail number
        A.label('match%d' % k)
        A.shri(X, TR, RB * k + KEYB + 1); A.andi(X, X, (1 << IDB) - 1); A.jmp('match')
    # ---------------- end of iteration ----------------
    A.label('cont')
    A.addi(C, C, 1); A.jnei(C, Tb, 'loop')                   # counter (3 with the compare and branch)
    A.label('dl')
    A.halt(12)                                               # c = Tb: the attempt failed
    # ---------------- restart(l) and the insertion of a point into lane l ----------------
    A.label('restart')                                       # in: L, LV; link LR
    A.jnei(IDN, U, 'rs1'); A.halt(11); A.label('rs1')
    A.st(L, LID, IDN); A.st(L, LST, LV); A.add(NP, RHO, IDN); A.addi(IDN, IDN, 1)
    A.label('setwalk')                                       # in: L, NP; link LR
    A.movi(ONEB, 1); A.shl(ONEB, ONEB, L); A.not_(NM, ONEB)
    A.label('sw_planes')
    for j in range(256):
        A.and_(X, j, NM)
        if j: A.shri(Y, NP, j); A.andi(Y, Y, 1)
        else: A.andi(Y, NP, 1)
        A.shl(Y, Y, L); A.or_(j, X, Y)
    A.label('sw_end')
    A.jr(LR)
    # ---------------- the evaluation of F on one point with the permutation ----------------
    A.label('evalF')                                         # in: UU; out: FF; link LR2
    build_state(A, MISC)
    A.label('ef_perm')
    A.permute(W0); A.lda(PDR, MISC + 7); A.xor(FF, W0, PDR)
    if WT: A.andi(FF, FF, (1 << WT) - 1)                     # test builds only: F truncated to the low WT bits
    A.jr(LR2)
    A.label('outm')                                          # in: UU; out: W0..W3 = the 128-byte message m(UU); link LR2
    build_state(A, MISC)
    A.jr(LR2)
    # ---------------- replay ----------------
    A.label('match')                                         # in: X (stored trail a), L (walk of trail b), C1
    A.ld(Y, L, LID); A.ld(LB, L, LST); A.sub(LB, C1, LB)     # trail b: its number and its length lb = c1 - LST[l]
    A.jgei(LB, LRC + 1, 'rfail')                             # lb > LRC: the replay refuses it
    A.add(P, RHO, X); A.add(Q, RHO, Y)
    A.mov(UU, P); A.movi(LA, 0)
    A.label('meas')                                          # la := evaluations of trail a from its start to its first DP
    A.jal(LR2, 'evalF'); A.addi(LA, LA, 1); A.jlti(FF, THR, 'measd')       # the image is a DP when FF < THR
    A.jgei(LA, LRC, 'rfail'); A.mov(UU, FF); A.jmp('meas')
    A.label('measd')
    A.jlt(LA, LB, 'advq')
    A.sub(N, LA, LB); A.mov(MM, LB)
    A.label('advp')
    A.jeqi(N, 0, 'lock'); A.mov(UU, P); A.jal(LR2, 'evalF'); A.mov(P, FF); A.subi(N, N, 1); A.jmp('advp')
    A.label('advq')
    A.sub(N, LB, LA); A.mov(MM, LA)
    A.label('advq2')
    A.jeqi(N, 0, 'lock'); A.mov(UU, Q); A.jal(LR2, 'evalF'); A.mov(Q, FF); A.subi(N, N, 1); A.jmp('advq2')
    A.label('lock')
    A.jeq(P, Q, 'rfail')
    A.label('lloop')
    A.jeqi(MM, 0, 'rfail')
    A.mov(UU, P); A.jal(LR2, 'evalF'); A.mov(FP, FF); A.mov(UU, Q); A.jal(LR2, 'evalF')
    A.jeq(FP, FF, 'found')
    A.mov(P, FP); A.mov(Q, FF); A.subi(MM, MM, 1); A.jmp('lloop')
    A.label('found')                                         # output m(p), m(q): words W0..W3 of the built states
    A.mov(UU, P); A.jal(LR2, 'outm')
    for i in range(4): A.st(ZERO, OUT + i, W0 + i)
    A.mov(UU, Q); A.jal(LR2, 'outm')
    for i in range(4): A.st(ZERO, OUT + 4 + i, W0 + i)
    A.halt(1)
    A.label('rfail')
    A.halt(13)
    A.label('end')
    A.resolve()
    return A


def audit(A):
    """every conditional branch follows the compare that sets its register; every label inside range"""
    for i, x in enumerate(A.ins):
        if x[0] in (BNZ, BZ):
            p = A.ins[i - 1]
            assert p[0] in CMPOPS and p[1] == x[2], ('branch without compare', i)
            assert x[4] < len(A.ins)
        if x[0] in (JMP, JAL): assert x[4] < len(A.ins)


# ---------------- encoding ----------------
def enc(x):
    op, d, a, b, imm = x
    return struct.pack('<BHHHB', op, d, a, b, 0) + imm.to_bytes(24, 'little')


def dec(bs):
    out = []
    for i in range(0, len(bs), 32):
        op, d, a, b, z = struct.unpack('<BHHHB', bs[i:i + 8])
        out.append((op, d, a, b, int.from_bytes(bs[i + 8:i + 32], 'little')))
    return out


def sl_bytes(prog, PFLO, PFN):
    """prog.bin + the prefilter: PF := OR of planes PFLO..PFLO+PFN-1 (PFN-1 ORs), 5-byte instructions"""
    out = bytearray(prog)
    def w(code, d, a, b): return (code | d << 3 | a << 15 | b << 27).to_bytes(5, 'little')
    out += w(2, PF, PFLO, PFLO + 1)
    for j in range(PFLO + 2, PFLO + PFN): out += w(2, PF, PF, j)
    return bytes(out)


def block_files():
    return ['P.bin'] + ['B%d.bin' % j for j in range(1, KB + 1)] + ['E.bin']


def step_layout():
    """The step as it executes: the prefix P, then for each generic round r = 2..NR-2 a call of body j = (r - 2) mod KB + 1
    (JAL LR3 into the body, the body, JR LR3 at its end) and the iota of round r (one 5-byte XOR of plane (0, z) of the
    body's output bank with the all-ones register ONES per set bit z of RC[r]), then the last round E.  Returns the list of
    (kind, payload): ('blk', name) or ('iota', r, bank)."""
    seq = [('blk', 'P.bin')]
    for r in range(2, NR - 1):
        j = (r - 2) % KB + 1
        seq.append(('blk', 'B%d.bin' % j))
        seq.append(('iota', r, YB if j % 2 else XB))
    seq.append(('blk', 'E.bin'))
    return seq


def flat_step(d='.'):
    """the executed straight-line stream of one step (5-byte instructions, the call and return excluded)"""
    blocks = {n: open(os.path.join(d, n), 'rb').read() for n in block_files()}
    out = bytearray()
    for item in step_layout():
        if item[0] == 'blk': out += blocks[item[1]]
        else:
            _, r, ob = item
            for z in range(64):
                if (RC[r] >> z) & 1: out += (0 | (ob + z) << 3 | (ob + z) << 15 | ONES << 27).to_bytes(5, 'little')
    return bytes(out)


def step_stats(d='.'):
    """stored code of the step and its executed operations"""
    sizes = {n: os.path.getsize(os.path.join(d, n)) // 5 for n in block_files()}
    iota = sum(bin(RC[r]).count('1') for r in range(2, NR - 1))
    ncall = NR - 3
    executed = sum(sizes[it[1]] for it in step_layout() if it[0] == 'blk') + iota + 2 * ncall
    stored5 = sum(sizes.values()) + iota                     # 5-byte instructions stored once
    stored32 = ncall + KB                                    # JAL per generic round, JR per body (32-byte instructions)
    return sizes, iota, ncall, executed, stored5, stored32


# ---------------- Keccak ----------------
RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808a, 0x8000000080008000, 0x000000000000808b, 0x0000000080000001,
      0x8000000080008081, 0x8000000000008009, 0x000000000000008a, 0x0000000000000088, 0x0000000080008009, 0x000000008000000a,
      0x000000008000808b, 0x800000000000008b, 0x8000000000008089, 0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
      0x000000000000800a, 0x800000008000000a, 0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]
ROTC = [0, 1, 62, 28, 27, 36, 44, 6, 55, 20, 3, 10, 43, 25, 39, 41, 45, 15, 21, 8, 18, 2, 61, 56, 14]


def rotl(v, r): return ((v << r) | (v >> (64 - r))) & M64 if r else v


def keccak_f(A, rounds):
    A = list(A)
    for r in range(rounds):
        Cc = [A[x] ^ A[x + 5] ^ A[x + 10] ^ A[x + 15] ^ A[x + 20] for x in range(5)]
        D = [Cc[(x + 4) % 5] ^ rotl(Cc[(x + 1) % 5], 1) for x in range(5)]
        A = [A[i] ^ D[i % 5] for i in range(25)]
        B = [0] * 25
        for x in range(5):
            for y in range(5): B[y + 5 * ((2 * x + 3 * y) % 5)] = rotl(A[x + 5 * y], ROTC[x + 5 * y])
        A = [B[x + 5 * y] ^ ((~B[(x + 1) % 5 + 5 * y] & M64) & B[(x + 2) % 5 + 5 * y]) for y in range(5) for x in range(5)]
        A[0] ^= RC[r]
    return A


def sha3_256_r(msg, rounds):
    A = [0] * 25
    off = 0
    while True:
        rem = len(msg) - off
        if rem >= 136: blk = msg[off:off + 136]; off += 136
        else:
            blk = bytearray(msg[off:] + bytes(136 - rem)); blk[rem] ^= 6; blk[135] ^= 0x80; off = len(msg) + 1
        for i in range(17): A[i] ^= int.from_bytes(blk[8 * i:8 * i + 8], 'little')
        A = keccak_f(A, rounds)
        if off > len(msg): break
    return b''.join(A[i].to_bytes(8, 'little') for i in range(4))


# ---------------- constants of the target from meta.txt ----------------
def read_meta(path):
    KL = [0] * 25; PD = [0] * 4
    for line in open(path):
        t = line.split()
        if t and t[0] == 'lane': KL[int(t[1])] = int(t[2], 16)
        elif t and t[0] == 'pd': PD = [int(x, 16) for x in t[1:5]]
    return KL, PD


def data_image(KL, PD):
    """16 words: KW[0..6] (lane constants of the absorbed state, the lanes of u zero), PD, then 8 output words"""
    KW = []
    for w in range(7):
        v = 0
        for i in range(4):
            l = 4 * w + i
            if l < 25: v |= KL[l] << (64 * i)
        KW.append(v)
    pd = PD[0] | PD[1] << 64 | PD[2] << 128 | PD[3] << 192
    return KW + [pd] + [0] * 8


def m_of(u, KL):
    Ls = list(KL[:16])
    u0, u1, u2, u3 = [(u >> (64 * i)) & M64 for i in range(4)]
    Ls[1] = u0; Ls[6] = u1; Ls[11] = u0 ^ u1 ^ KL[11]; Ls[4] = u2; Ls[9] = u3; Ls[14] = u2 ^ u3 ^ KL[14]
    return b''.join(x.to_bytes(8, 'little') for x in Ls)


def F_plain(u, KL, PD, rounds=NR):
    d = sha3_256_r(m_of(u, KL), rounds)
    pd = PD[0] | PD[1] << 64 | PD[2] << 128 | PD[3] << 192
    return int.from_bytes(d, 'little') ^ pd


# ---------------- the machine ----------------
def compile_sl(slb, nprog, hookW=None):
    """Python function executing the 5-byte block on a register list (the planes 0..255 and PF are the only live ends).
    hookW (test builds only): set the planes hookW..255 to zero after the first nprog instructions (the F of the program
    truncated to hookW bits, as in the organizer experiment rho-w22)."""
    src = ['def sl(R):']
    for j in range(256): src.append(' r%d=R[%d]' % (j, j))
    src.append(' r%d=R[%d]' % (ONES, ONES))                   # the all-ones register read by the iota XORs
    for i in range(0, len(slb), 5):
        if i // 5 == nprog and hookW:
            for j in range(hookW, 256): src.append(' r%d=0' % j)
        w = int.from_bytes(slb[i:i + 5], 'little')
        op, d, a, b = w & 7, (w >> 3) & 4095, (w >> 15) & 4095, (w >> 27) & 4095
        if op == 0: src.append(' r%d=r%d^r%d' % (d, a, b))
        elif op == 1: src.append(' r%d=r%d&r%d' % (d, a, b))
        elif op == 2: src.append(' r%d=r%d|r%d' % (d, a, b))
        else: src.append(' r%d=r%d^%d' % (d, a, M256))
    for j in range(256): src.append(' R[%d]=r%d' % (j, j))
    src.append(' R[%d]=r%d' % (PF, PF))
    ns = {}
    exec(compile('\n'.join(src), 'sl', 'exec'), ns)
    return ns['sl']


class VM:
    def load(s, code, sl, nsl, slpos, memwords, data, MISC, rng):
        s.code = code; s.sl = sl; s.nsl = nsl; s.slpos = slpos
        s.R = [0] * NREGS; s.M = [0] * memwords
        for i, v in enumerate(data): s.M[MISC + i] = v
        s.rng = rng; s.units = 0; s.slsteps = 0; s.halt = None
        s.cnt = [0] * (len(code) + 1)
        return s

    def run(s, pc=0, stop=None):
        code, R, M, cnt = s.code, s.R, s.M, s.cnt
        sl, slpos = s.sl, s.slpos
        while True:
            if pc == slpos and sl is not None:
                sl(R); s.slsteps += 1
            if stop is not None and pc == stop: return pc
            op, d, a, b, imm = code[pc]
            cnt[pc] += 1
            pc += 1
            if op == XOR: R[d] = R[a] ^ R[b]
            elif op == AND: R[d] = R[a] & R[b]
            elif op == OR: R[d] = R[a] | R[b]
            elif op == NOT: R[d] = R[a] ^ M256
            elif op == ADD: R[d] = (R[a] + R[b]) & M256
            elif op == SUB: R[d] = (R[a] - R[b]) & M256
            elif op == SHL: R[d] = (R[a] << (R[b] & 255)) & M256
            elif op == SHR: R[d] = R[a] >> (R[b] & 255)
            elif op == EQ: R[d] = 1 if R[a] == R[b] else 0
            elif op == LT: R[d] = 1 if R[a] < R[b] else 0
            elif op == MOV: R[d] = R[a]
            elif op == ADDI: R[d] = (R[a] + imm) & M256
            elif op == SUBI: R[d] = (R[a] - imm) & M256
            elif op == SHLI: R[d] = (R[a] << imm) & M256
            elif op == SHRI: R[d] = R[a] >> imm
            elif op == ANDI: R[d] = R[a] & imm
            elif op == EQI: R[d] = 1 if R[a] == imm else 0
            elif op == LTI: R[d] = 1 if R[a] < imm else 0
            elif op == MOVI: R[d] = imm
            elif op == LD: R[d] = M[R[a] + imm]
            elif op == ST: M[R[a] + imm] = R[b]
            elif op == LDA: R[d] = M[imm]
            elif op == BNZ:
                if R[a]: pc = imm
            elif op == BZ:
                if not R[a]: pc = imm
            elif op == JMP: pc = imm
            elif op == JAL: R[d] = pc; pc = imm
            elif op == JR: pc = R[a]
            elif op == RND: R[d] = s.rng.getrandbits(256)
            elif op == PERM:
                lanes = []
                for w in range(7):
                    v = R[a + w]
                    for i in range(4): lanes.append((v >> (64 * i)) & M64)
                lanes = keccak_f(lanes[:25], NR)
                lanes += [0, 0, 0]
                for w in range(7): R[a + w] = sum(lanes[4 * w + i] << (64 * i) for i in range(4))
                s.units += 1
            elif op == HALT:
                s.halt = imm; return None
            else: raise Exception('bad op')


# ---------------- counting ----------------
FULL = {k: PARAMS[k] for k in ('S', 'U', 'SB', 'IDB', 'LRC', 'Tb', 'HMAX', 'DPLO', 'DK', 'DT', 'PFLO', 'PFN')}


def counts(A, Pm):
    """Worst-case operation counts of every routine, from the lengths of the emitted code (an instruction is one
    operation, PERM is UNIT).  seg(a, b) = number of instructions between two labels."""
    I = A.lab
    def seg(a, b): return I[b] - I[a]
    S, U, LRC = Pm['S'], Pm['U'], Pm['LRC']
    c = {}
    c['n_instr'] = len(A.ins)
    c['setwalk'] = seg('setwalk', 'sw_end') + 1                                  # with the return
    c['restart'] = (seg('restart', 'rs1') - 1) + seg('rs1', 'setwalk') + c['setwalk']   # the cap check passes (no HALT)
    c['restart_halt'] = seg('restart', 'rs1') - 1 + 1                           # the last call: compare, branch not taken, HALT
    c['hit'] = (seg('hit', 'h1') - 1) + seg('h1', 'dpl') + 2                     # per processed hit, no DP walk
    c['ctz_clear'] = seg('dp1', 'gather')
    c['gather'] = seg('gather', 'record')
    c['record_slot'] = seg('record', 'sl_ok')
    c['probe_word'] = 1 + 7 + 8 * (RPW - 1) + 3                                  # load, four occupied non-matching records, next word
    c['probe_wrap'] = 2
    c['probe_end'] = 1 + 7 + 8 * (RPW - 2) + 4                                   # load, three records passed, the fourth: shift, mask, empty test
    c['empty_tail'] = 2 + 1 + 1 + 3                                              # shift, or, store, jump; move, call, jump back
    c['dp_fixed'] = 2 + c['ctz_clear'] + c['gather'] + c['record_slot'] + c['probe_end'] + c['probe_wrap'] + c['empty_tail']
    c['dp_max'] = c['dp_fixed'] + c['probe_word'] * S                            # at most S occupied words passed
    c['dl_final'] = seg('dl', 'restart')                                         # c = Tb: the HALT (the compare and branch are in the iteration's 3)
    c['e_eval'] = seg('evalF', 'outm') - 1 + UNIT                                # one evaluation of F with the permutation, with the return
    c['e_outm'] = seg('outm', 'match')                                           # the message builder, with the return
    e = c['e_eval']
    c['match_entry'] = 3 + seg('match', 'meas')                                  # trail number from the record (3), entry (9: with the lb test 2)
    c['meas_iter'] = e + 8                                                       # one measuring evaluation without the DP
    c['meas_last'] = e + 4                                                       # the evaluation that lands on the DP
    c['replay_iter'] = 13 + 2 * e                                                # one lock-step iteration (not found)
    # success after k lock-step iterations, la measured: 12 + (la - 1)(e + 8) + (e + 4) + 2 + 2 + n (7 + e) + 2 + 2
    #   + (k - 1)(13 + 2e) + (9 + 2e) + 67; exhaustion: ... + m (13 + 2e) + 3.  Largest at la = lb = k = LRC:
    #   (e + 8 + 13 + 2e) LRC + 12 - 4 + 2 + 2 + 2 + 2 - 13 + 9 + 67
    c['replay_const'] = c['match_entry'] - 4 + 2 + 2 + 2 + 2 - 13 + 9 + 67
    c['replay_max'] = (c['meas_iter'] + c['replay_iter']) * LRC + c['replay_const']
    c['setup'] = seg('start', 'clr') + (S // 8) * 11 + 1 + 256 * (7 + c['setwalk'])
    return c


def pf_bytes(PFLO, PFN):
    return sl_bytes(b'', PFLO, PFN)


def build_cli(argv):
    if len(argv) > 1 and argv[1] == 'build':
        meta = argv[2] if len(argv) > 2 else 'meta.txt'
        KL, PD = read_meta(meta)
        A = program(FULL); audit(A)
        other = b''.join(enc(x) for x in A.ins)
        open('other.bin', 'wb').write(other)
        open('pf.bin', 'wb').write(pf_bytes(FULL['PFLO'], FULL['PFN']))
        open('data.bin', 'wb').write(b''.join(w.to_bytes(32, 'little') for w in data_image(KL, PD)))
        c = counts(A, FULL)
        I = A.lab
        out = []
        out.append('other code: %d instructions x 32 bytes = %d bytes (other.bin sha256 %s)' % (len(A.ins), len(other), hashlib.sha256(other).hexdigest()))
        sizes, iota, ncall, executed, stored5, stored32 = step_stats()
        out.append('step blocks (5-byte instructions): ' + ' '.join('%s %d sha256 %s' % (n, sizes[n], hashlib.sha256(open(n, 'rb').read()).hexdigest()[:16]) for n in block_files()))
        out.append('step: executed %d operations (blocks as called, %d iota XORs, %d calls with returns 2 each); stored %d 5-byte instructions and %d 32-byte instructions (JAL per generic round, JR per body)' % (executed, iota, ncall, stored5, stored32))
        out.append('prefilter: %d instructions x 5 bytes (pf.bin sha256 %s); the step block sits in front of instruction %d (label loop)' %
                   (FULL['PFN'] - 1, hashlib.sha256(open('pf.bin', 'rb').read()).hexdigest(), I['loop']))
        out.append('flat executed stream sha256 %s' % hashlib.sha256(flat_step()).hexdigest())
        out.append('%-18s %d' % ('step_executed', executed))
        out.append('%-18s %d' % ('step_stored5', stored5))
        out.append('%-18s %d' % ('step_stored32', stored32))
        out.append('data image: 16 words x 32 bytes = 512 bytes (data.bin sha256 %s): KW[0..6], PD, 8 output words' % hashlib.sha256(open('data.bin', 'rb').read()).hexdigest())
        out.append('memory map (words): TAB 0..%d, LID %d..%d, LST %d..%d, data %d..%d' % (FULL['S'] - 1, FULL['S'], FULL['S'] + 255, FULL['S'] + 256, FULL['S'] + 511, FULL['S'] + 512, FULL['S'] + 527))
        out.append('routine entry points (instruction index): ' + ', '.join('%s %d' % (k, I[k]) for k in ('start', 'loop', 'hit', 'dpl', 'dp1', 'gather', 'record', 'probe', 'empty0', 'ins', 'match0', 'cont', 'dl', 'restart', 'setwalk', 'evalF', 'outm', 'match', 'meas', 'end')))
        for k, v in c.items(): out.append('%-18s %d' % (k, v))
        bybase = {}
        for x in A.ins: bybase[NAMES[x[0]]] = bybase.get(NAMES[x[0]], 0) + 1
        out.append('static opcode mix: ' + ' '.join('%s %d' % kv for kv in sorted(bybase.items(), key=lambda kv: -kv[1])))
        out.append('highest register named: %d (file of %d)' % (max(max(x[1], x[2], x[3]) for x in A.ins), NREGS))
        open('counts.txt', 'w').write(chr(10).join(out) + chr(10))
        print(chr(10).join(out))
    else:
        print(__doc__ if __doc__ else 'usage: other3.py build [meta.txt]')


if __name__ == '__main__':
    build_cli(sys.argv)
```

### D.2 Output of `python3 other5.py build meta.txt`

```
other code: 2715 instructions x 32 bytes = 86880 bytes (other.bin sha256 53511137bc9eaf0fbf0f806a8f6ead1abd9335eb6f36535ca66d011c002f9c91)
step blocks (5-byte instructions): P.bin 4942 sha256 a19d15483682b2c6 B1.bin 6618 sha256 c3a9216e6fe96074 B2.bin 6634 sha256 2cc3982d2b16bef2 B3.bin 6625 sha256 6cc7a678188b88fd B4.bin 6633 sha256 df6ff2c93b1be7f0 B5.bin 6624 sha256 56fbcbae544279c7 B6.bin 6636 sha256 df30c150655696cc B7.bin 6642 sha256 5f505fbb72c26bdd B8.bin 6904 sha256 fd11364f54bea307 E.bin 2475 sha256 9e7b6cd44b30580a
step: executed 93945 operations (blocks as called, 52 iota XORs, 13 calls with returns 2 each); stored 60785 5-byte instructions and 21 32-byte instructions (JAL per generic round, JR per body)
prefilter: 15 instructions x 5 bytes (pf.bin sha256 6aca5087f80a0f55e2913e21fcc95e7ce46d2df001659e510daf93ffd91830c1); the step block sits in front of instruction 26 (label loop)
flat executed stream sha256 b72bf7dd14cea62b1a7e4be827147ab11859e6a7bdab207e1bf9e39a8d5c6bd9
step_executed      93945
step_stored5       60785
step_stored32      21
data image: 16 words x 32 bytes = 512 bytes (data.bin sha256 f448b5961fc418300d6c68567ebe39f083a2d4f8702456cb5d7de7b6c677ab42): KW[0..6], PD, 8 output words
memory map (words): TAB 0..16279, LID 16280..16535, LST 16536..16791, data 16792..16807
routine entry points (instruction index): start 0, loop 26, hit 28, dpl 153, dp1 155, gather 199, record 1221, probe 1231, empty0 1268, ins 1283, match0 1286, cont 1298, dl 1301, restart 1302, setwalk 1309, evalF 2592, outm 2622, match 2649, meas 2658, end 2715
n_instr            2715
setwalk            1283
restart            1289
restart_halt       3
hit                126
ctz_clear          44
gather             1022
record_slot        10
probe_word         35
probe_wrap         2
probe_end          28
empty_tail         7
dp_fixed           1115
dp_max             570915
dl_final           1
e_eval             4365
e_outm             27
match_entry        12
meas_iter          4373
meas_last          4369
replay_iter        8743
replay_const       79
replay_max         782293699580794737309777253081773244495
setup              352633
static opcode mix: OR 616 ANDI 540 SHRI 276 SHLI 270 AND 268 SHL 257 SHR 256 ST 24 EQI 23 BNZ 21 XOR 21 MOV 18 ADDI 17 LDA 15 JMP 14 BZ 13 MOVI 10 NOT 10 JAL 9 LTI 7 HALT 5 SUBI 5 ADD 4 LD 4 EQ 3 JR 3 SUB 3 RND 1 PERM 1 LT 1
highest register named: 3534 (file of 3536)
```

### D.3 other5_test.py

```python
#!/usr/bin/env python3
# other5_test.py - checks of the emitted program of other5.py (other4_test.py of 71fefe66 with the step of gen4: the
# executed stream P, bodies as called, iota XORs, E; the all-ones register set in the straight-line test).
#   1. routine tests: each routine run on constructed states; its executed operations must equal the counted worst case
#   2. end-to-end runs of the whole emitted program (setup, loop, hit handler, DP handler, restart, deadlines, replay,
#      output) at reduced width: the straight line of prog.bin is truncated to W bits after every step (test hook), the
#      replay's F is truncated alike (one extra ANDI in evalF, test builds only); the output pair is checked with an
#      independent Keccak.  The totals of every run are compared with the counted bounds.
#   usage: other4_test.py [nseeds] [pyseed]   (params.json, meta.txt and prog.bin of the row in the working directory)
import random, sys, time
from other5 import *

KL, PD = read_meta('meta.txt')
prog = flat_step(); NPROG = len(prog) // 5
data = data_image(KL, PD)
FAILS = []; NCHK = [0]


def check(cond, msg):
    NCHK[0] += 1
    if not cond:
        FAILS.append(msg); print('FAIL', msg)


def mk(Pm, seed=1, with_sl=False):
    A = program(Pm); audit(A)
    code = dec(b''.join(enc(x) for x in A.ins))
    S = Pm['S']
    slb = sl_bytes(prog, Pm['PFLO'], Pm['PFN'])
    sl = compile_sl(slb, NPROG, Pm.get('WTEST')) if with_sl else None
    vm = VM().load(code, sl, len(slb) // 5, A.lab['loop'], S + 528, data, S + 512, random.Random(seed))
    return A, vm, len(slb) // 5


def nonsl_ops(vm):
    return sum(vm.cnt) - vm.units + vm.units * UNIT


def ops_of(vm, f):
    a = nonsl_ops(vm); f(); return nonsl_ops(vm) - a


# ------------------------------------------------------------------ 1. routine tests
def sl_test():
    """the straight line + prefilter as compiled from the 5-byte bytes: 2 x 256 points, every lane, 3 chained steps, against F_plain"""
    sl = compile_sl(sl_bytes(prog, 240, 16), NPROG)
    for rep_ in range(2):
        us = [random.getrandbits(256) for _ in range(256)]
        R = [0] * NREGS; R[ONES] = M256                    # the search state holds the all-ones word (setup)
        for step in range(3):
            for j in range(256): R[j] = sum(((us[l] >> j) & 1) << l for l in range(256))
            sl(R)
            for l in range(256):
                o = sum(((R[j] >> l) & 1) << j for j in range(256))
                us[l] = F_plain(us[l], KL, PD)
                if o != us[l]: check(False, 'straight line lane %d' % l); break
            else: continue
            break
        pfw = R[PF]
        check(all(((pfw >> l) & 1) == (0 if sum(((R[j] >> l) & 1) << (j - 240) for j in range(240, 256)) == 0 else 1) for l in range(256)), 'prefilter word')
    check(True, 'straight line')


def routine_tests():
    sl_test()
    Pm = dict(FULL)
    A, vm, nsl = mk(Pm)
    c = counts(A, Pm); I = A.lab; R = vm.R; END = I['end']
    S = Pm['S']; LID, LST = S, S + 256; KB = keyb(Pm); DPL, DKK = Pm['DPLO'], Pm['DK']
    # setwalk
    R[IDN] = 300; R[RHO] = 12345; R[LR] = END
    planes = [random.getrandbits(256) for _ in range(256)]
    for j in range(256): R[j] = planes[j]
    l = 201; np_ = random.getrandbits(256); R[L] = l; R[NP] = np_
    n = ops_of(vm, lambda: vm.run(I['setwalk'], stop=END))
    check(n == c['setwalk'], 'setwalk ops %d vs %d' % (n, c['setwalk']))
    ok = all(((R[j] >> l) & 1) == ((np_ >> j) & 1) and (R[j] & ~(1 << l)) == (planes[j] & ~(1 << l)) for j in range(256))
    check(ok, 'setwalk effect')
    # restart
    R[LR] = END; R[L] = 7; R[LV] = 99; R[IDN] = 4321
    n = ops_of(vm, lambda: vm.run(I['restart'], stop=END))
    check(n == c['restart'], 'restart ops %d vs %d' % (n, c['restart']))
    check(vm.M[LID + 7] == 4321 and vm.M[LST + 7] == 99 and R[IDN] == 4322, 'restart effect')
    R[IDN] = Pm['U']; R[LR] = END
    n = ops_of(vm, lambda: vm.run(I['restart'], stop=END))
    check(vm.halt == 11 and n == c['restart_halt'], 'restart halt %d %s' % (n, vm.halt))
    vm.halt = None
    # evalF and outm
    u = random.getrandbits(256); R[UU] = u; R[LR2] = END
    n = ops_of(vm, lambda: vm.run(I['evalF'], stop=END))
    check(n == c['e_eval'] and R[FF] == F_plain(u, KL, PD), 'evalF ops %d vs %d' % (n, c['e_eval']))
    R[UU] = u; R[LR2] = END
    n = ops_of(vm, lambda: vm.run(I['outm'], stop=END))
    check(n == c['e_outm'], 'outm ops %d' % n)
    check(b''.join(R[W0 + i].to_bytes(32, 'little') for i in range(4)) == m_of(u, KL), 'outm message')
    # setup
    vm2 = mk(Pm)[1]; vm2.M[0] = 5
    n = ops_of(vm2, lambda: vm2.run(0, stop=I['loop']))
    check(n == c['setup'], 'setup ops %d vs %d' % (n, c['setup']))
    check(all(vm2.M[i] == 0 for i in range(S)) and all(vm2.M[LID + i] == i and vm2.M[LST + i] == 0 for i in range(256)), 'setup effect')
    check(vm2.R[IDN] == 256 and vm2.R[C] == 0 and vm2.R[H] == 0 and vm2.R[ONES] == M256, 'setup state')
    rho = vm2.R[RHO]
    check(all(sum(((vm2.R[j] >> l) & 1) << j for j in range(256)) == (rho + l) & M256 for l in range(0, 256, 17)), 'setup lanes')
    # hit, no DP: planes DPLO..PFLO-1 nonzero
    A, vm, nsl = mk(Pm); R = vm.R
    for j in range(256): R[j] = M256
    R[PF] = 5; R[H] = 0; R[C] = 3
    n = ops_of(vm, lambda: vm.run(I['hit'], stop=I['cont']))
    check(n == c['hit'], 'hit ops %d vs %d' % (n, c['hit']))
    # hit abort
    R[H] = Pm['HMAX']; n = ops_of(vm, lambda: vm.run(I['hit'], stop=I['cont']))
    check(vm.halt == 10 and n == 4, 'hit abort %s %d' % (vm.halt, n)); vm.halt = None
    # DP handler worst path: walk 255 alone at a DP; k full words (four non-matching records each) in the probe path, then a
    # word with three non-matching records (the insertion goes to its fourth record), with and without wrap
    KM = (1 << KB) - 1
    for k, wrap in ((0, False), (5, False), (7, True)):
        A, vm, nsl = mk(Pm); R = vm.R; M = vm.M
        for j in range(256): R[j] = M256
        for j in range(DPL - DKK, 256): R[j] = M256 ^ (1 << 255)
        R[PF] = M256 ^ (1 << 255); R[ONES] = M256; R[H] = 0; R[C] = 777; R[RHO] = 31337; R[IDN] = 5000; R[LR] = END
        M[LST + 255] = 700; M[LID + 255] = 255
        SBm = Pm['SB']
        val = (S - 3) if wrap else (S + 100)                 # low SB bits of the point: slot S - 3, or S + 100 -> 100 after the subtraction
        for j in range(SBm): R[j] = (R[j] & ~(1 << 255)) | (((val >> j) & 1) << 255)
        for j in range(SBm, 40): R[j] = (R[j] & ~(1 << 255)) | (random.getrandbits(1) << 255)
        pt = sum(((R[j] >> 255) & 1) << j for j in range(256))
        slot = (S - 3) if wrap else 100
        def other_rec(i):
            while True:
                key = random.getrandbits(KB)
                if key != pt & KM: return 1 | key << 1 | (300 + i) << (KB + 1)
        for i in range(k): M[(slot + i) % S] = sum(other_rec(RPW * i + q) << (q * RB) for q in range(RPW))
        w0 = other_rec(90) | other_rec(91) << RB | other_rec(92) << (2 * RB)
        M[(slot + k) % S] = w0
        n = ops_of(vm, lambda: vm.run(I['hit'], stop=I['cont']))
        exp = c['hit'] + c['dp_fixed'] + c['restart'] + c['probe_word'] * k - (0 if wrap else c['probe_wrap']) - (1 if wrap else 0)
        check(n == exp, 'DP worst (k=%d wrap=%s) ops %d vs %d (halt %s)' % (k, wrap, n, exp, vm.halt))
        word = M[(slot + k) % S]
        rec = (word >> ((RPW - 1) * RB)) & RM
        check(word & ((1 << ((RPW - 1) * RB)) - 1) == w0 and rec == 1 | (pt & KM) << 1 | 255 << (KB + 1), 'DP record')
        check(M[LID + 255] == 5000 and M[LST + 255] == 778 and R[IDN] == 5001, 'DP restart')
    # insertion into each record of a word; a match in each of the four positions
    for pos in range(RPW):
        A, vm, nsl = mk(Pm); R = vm.R; M = vm.M
        for j in range(256): R[j] = M256
        for j in range(DPL - DKK, 256): R[j] = M256 ^ (1 << 255)
        R[PF] = M256 ^ (1 << 255); R[ONES] = M256; R[H] = 0; R[C] = 777; R[RHO] = 31337; R[IDN] = 5000; R[LR] = END
        M[LST + 255] = 700; M[LID + 255] = 255
        for j in range(Pm['SB']): R[j] = (R[j] & ~(1 << 255)) | (((S + 100) >> j) & 1) << 255
        pt = sum(((R[j] >> 255) & 1) << j for j in range(256))
        recs = [other_rec(50 + q) for q in range(pos)]
        M[100] = sum(r << (RB * q) for q, r in enumerate(recs))
        vm.run(I['hit'], stop=I['cont'])
        check((M[100] >> (RB * pos)) & RM == 1 | (pt & KM) << 1 | 255 << (KB + 1) and M[LID + 255] == 5000, 'insert at %d' % pos)
        A, vm, nsl = mk(Pm); R = vm.R; M = vm.M
        for j in range(256): R[j] = M256
        for j in range(DPL - DKK, 256): R[j] = M256 ^ (1 << 255)
        R[PF] = M256 ^ (1 << 255); R[ONES] = M256; R[H] = 0; R[C] = 777; R[RHO] = 31337; R[IDN] = 5000; R[LR] = END
        M[LST + 255] = 700; M[LID + 255] = 255
        for j in range(Pm['SB']): R[j] = (R[j] & ~(1 << 255)) | (((S + 100) >> j) & 1) << 255
        pt = sum(((R[j] >> 255) & 1) << j for j in range(256))
        recs = [other_rec(60 + q) for q in range(pos)] + [1 | (pt & KM) << 1 | 4242 << (KB + 1)]
        M[100] = sum(r << (RB * q) for q, r in enumerate(recs))
        vm.run(I['hit'], stop=I['meas'])
        check(R[X] == 4242 and R[Y] == 255 and R[LB] == 778 - 700, 'match at %d' % pos)
    # the DP mask of the hit handler: walks with the top planes zero and the DK planes below them < DT
    DT = Pm['DT']; THRm = thr(Pm); tested = [0, 0]
    for trial in range(4):
        A, vm, nsl = mk(Pm); R = vm.R
        xs = []
        for l in range(256):
            kind = random.randrange(6)
            if kind == 0: x = random.randrange(THRm)                                          # a DP
            elif kind == 1: x = random.randrange(THRm, 1 << DPL)                              # a candidate that is not a DP (x >= THR)
            elif kind == 2: x = THRm - 1 - random.randrange(3)                                # at the threshold, below
            elif kind == 3: x = THRm + random.randrange(3)                                    # at the threshold
            elif kind == 4: x = random.getrandbits(256)
            else: x = random.getrandbits(256 - 240) << 240 | random.getrandbits(240)          # 16 top planes random
            xs.append(max(x, 0) & M256)
        for j in range(256): R[j] = sum(((xs[l] >> j) & 1) << l for l in range(256))
        R[PF] = sum((1 if (xs[l] >> 240) else 0) << l for l in range(256))
        R[ONES] = M256; R[H] = 0; R[C] = 3
        vm.run(I['hit'], stop=I['dpl'])
        want = sum((1 << l) for l in range(256) if xs[l] < THRm)
        check(R[DPM] == want, 'DP mask (trial %d)' % trial)
        tested[0] += bin(want).count('1'); tested[1] += sum(1 for x in xs if (x >> DPL) == 0 and x >= THRm)
    check(tested[0] > 100 and tested[1] > 100, 'DP mask coverage %s' % tested)
    # c = Tb: the iteration's counter and compare, then the HALT
    A, vm, nsl = mk(Pm); R = vm.R
    R[C] = Pm['Tb'] - 1
    n = ops_of(vm, lambda: vm.run(I['cont']))
    check(vm.halt == 12 and n == 3 + c['dl_final'], 'Tb halt %s %d' % (vm.halt, n))
    A, vm, nsl = mk(Pm); R = vm.R
    R[C] = 5
    n = ops_of(vm, lambda: vm.run(I['cont'], stop=I['loop']))
    check(vm.halt is None and n == 3 and R[C] == 6, 'counter ops %d' % n)


def replay_tests(ntrials=60):
    """the replay on pairs of trails of the 12-bit truncation of F with a 4-bit DP (planes 8..11 zero): the measuring walk,
    alignment, lock step; pairs with the same end (found / p = q) and with different ends (exhausted: a false key match)"""
    Pm = dict(S=400, U=400, SB=9, IDB=9, LRC=200, Tb=900, HMAX=10 ** 9, DPLO=8, DK=2, DT=3, PFLO=10, PFN=2, WTEST=12)
    THRm = thr(Pm)
    mask = (1 << 12) - 1
    Ft = lambda u: F_plain(u, KL, PD) & mask
    A, vm0, nsl = mk(Pm); I = A.lab; c = counts(A, Pm); e = c['e_eval']; END = I['end']; S = Pm['S']
    seen = {1: 0, 13: 0, 'diff': 0}
    done = 0
    while done < ntrials:
        rho = random.getrandbits(256)
        trails = {}
        for a in range(256, 400):
            u = (rho + a) & M256; pts = [u]
            for i in range(Pm['LRC']):
                u = Ft(u); pts.append(u)
                if u < THRm: break
            if pts[-1] < THRm: trails[a] = pts
        ends = {}
        for a, t in trails.items(): ends.setdefault(t[-1], []).append(a)
        pairs = [(v[0], v[1]) for v in ends.values() if len(v) > 1][:3]
        keys = list(trails)
        pairs.append(tuple(random.sample(keys, 2)))
        for a, b in pairs:
            if done >= ntrials: break
            ta, tb = trails[a], trails[b]
            la, lb = len(ta) - 1, len(tb) - 1
            A, vm, nsl = mk(Pm); R = vm.R; M = vm.M
            R[RHO] = rho; R[LR2] = END; R[L] = 9; M[S + 9] = b; R[C1] = 5000; M[S + 256 + 9] = 5000 - lb; R[X] = a
            ops = ops_of(vm, lambda: vm.run(I['match']))
            n_, m_ = abs(la - lb), min(la, lb)
            p, q = (ta[n_], tb[0]) if la >= lb else (ta[0], tb[n_])
            meas = (la - 1) * (e + 8) + (e + 4)
            base = 9 + meas + 2 + 2 + n_ * (7 + e) + 2
            check(R[LA] == la and R[LB] == lb, 'replay lengths %d %d vs %d %d' % (R[LA], R[LB], la, lb))
            if ta[-1] != tb[-1]:
                k = 0
                while k < m_ and Ft(p) != Ft(q): p, q = Ft(p), Ft(q); k += 1
                if k < m_:                       # different ends cannot merge inside the trails
                    check(False, 'different ends merged')
                check(vm.halt == 13 and ops == base + (2 if p != q else 0) + (m_ * (13 + 2 * e) + 3 if p != q else 1) - (0 if p != q else 0), 'replay different ends ops %d (halt %s)' % (ops, vm.halt))
                seen['diff'] += 1
            elif p == q:
                check(vm.halt == 13 and ops == base + 2 + 1, 'replay p=q ops %d halt %s' % (ops, vm.halt)); seen[13] += 1
            else:
                k = 1
                while Ft(p) != Ft(q): p, q = Ft(p), Ft(q); k += 1
                check(vm.halt == 1, 'replay expected halt 1, got %s (la %d lb %d)' % (vm.halt, la, lb))
                pred = base + 2 + (k - 1) * (13 + 2 * e) + (9 + 2 * e) + 67
                check(ops == pred and vm.cnt[I['lloop']] == k, 'replay found ops %d vs %d (k %d)' % (ops, pred, k))
                out = M[S + 520:S + 528]
                ma = b''.join(out[x].to_bytes(32, 'little') for x in range(4)); mb = b''.join(out[4 + x].to_bytes(32, 'little') for x in range(4))
                check(ma != mb and (int.from_bytes(sha3_256_r(ma, NR), 'little') & mask) == (int.from_bytes(sha3_256_r(mb, NR), 'little') & mask), 'replay pair')
                seen[1] += 1
            check(ops <= c['replay_max'], 'replay bound')
            done += 1
    # a stored trail without a DP within LRC (checks the guard): halt 13
    A, vm, nsl = mk(dict(Pm, LRC=1)); R = vm.R; M = vm.M
    c1 = counts(A, dict(Pm, LRC=1))
    for a in range(256, 400):
        if Ft((5 + a) & M256) >= THRm:
            R[RHO] = 5; R[LR2] = END; R[L] = 9; M[S + 9] = 300; R[C1] = 10; M[S + 256 + 9] = 9; R[X] = a
            vm.run(A.lab['match']); check(vm.halt == 13 and R[LA] == 1, 'measure guard'); break
    # the length guard of the new trail: lb = LRC + 1 is refused at once (6 operations), lb = LRC goes on
    for lbv, want in ((Pm['LRC'] + 1, 13), (Pm['LRC'], None)):
        A, vm, nsl = mk(Pm); R = vm.R; M = vm.M
        R[RHO] = 5; R[LR2] = A.lab['end']; R[L] = 9; M[S + 9] = 300; R[C1] = 10 ** 6; M[S + 256 + 9] = 10 ** 6 - lbv; R[X] = 256
        n = ops_of(vm, lambda: vm.run(A.lab['match'], stop=A.lab['meas'] if want is None else None))
        check((vm.halt == 13 and n == 6) if want else (vm.halt is None and R[LB] == lbv), 'lb guard %d' % lbv)
    print('replay tests: found %d, p=q %d, different ends %d' % (seen[1], seen[13], seen['diff']))


# ------------------------------------------------------------------ 2. end-to-end
def check_pair(vm, Pm, W):
    S = Pm['S']; out = vm.M[S + 520:S + 528]
    ma = b''.join(out[i].to_bytes(32, 'little') for i in range(4)); mb = b''.join(out[4 + i].to_bytes(32, 'little') for i in range(4))
    da, db = sha3_256_r(ma, NR), sha3_256_r(mb, NR)
    mask = (1 << W) - 1
    return ma != mb and len(ma) == 128 and (int.from_bytes(da, 'little') & mask) == (int.from_bytes(db, 'little') & mask)


def e2e(name, Pm, seeds, expect=None, W=26):
    A = None; res = {}
    for sd in seeds:
        A, vm, nsl = mk(Pm, sd, True)
        t0 = time.time(); vm.run(0); dt = time.time() - t0
        c = counts(A, Pm); I = A.lab; cnt = vm.cnt
        steps = vm.slsteps
        hits = cnt[I['hit']]; dps = cnt[I['dp1']]; rest = cnt[I['rs1']]; dl = cnt[I['dl']]      # dl: 1 when Tb is reached
        # exact group checks
        calls = cnt[I['setwalk']]
        check(sum(cnt[I['setwalk']:I['sw_end'] + 1]) == (c['setwalk']) * calls, 'setwalk group %d calls' % calls)
        check(sum(cnt[I['gather']:I['record']]) == c['gather'] * dps, 'gather group')
        check(cnt[I['loop']] == steps and cnt[I['cont']] in (steps, steps - 1), 'loop counts')
        # totals against the counted bounds
        nonsl = nonsl_ops(vm)
        replay_ops = sum(cnt[I['evalF']:I['end']]) - vm.units + vm.units * UNIT
        bound = (c['setup'] + 5 * steps + hits * c['hit'] + dps * c['dp_max'] + (rest + 1) * (c['restart'] + 3)
                 + c['dl_final'] + c['restart_halt'] + c['replay_max'])
        check(nonsl <= bound, '%s seed %d: ops %d > bound %d' % (name, sd, nonsl, bound))
        # exact accounting of what is not data dependent
        base = c['setup'] + 5 * steps
        res[sd] = (vm.halt, steps, hits, dps, rest, dl, replay_ops)
        if vm.halt == 1:
            check(check_pair(vm, Pm, W), '%s seed %d: output pair invalid' % (name, sd))
        if replay_ops:
            # exact replay formula for the observed lengths
            la, lb, k = vm.R[LA], vm.R[LB], cnt[I['lloop']]
            n_, m_ = abs(la - lb), min(la, lb)
            e = c['e_eval']
            if vm.halt == 1:
                # the 3 instructions that take the trail number from the record lie before evalF (counted with the DP walk)
                pred = 9 + (la - 1) * (e + 8) + (e + 4) + 2 + 2 + n_ * (7 + e) + 2 + 2 + (k - 1) * (13 + 2 * e) + (9 + 2 * e) + 67
                check(replay_ops == pred, '%s seed %d: replay ops %d vs %d (la %d lb %d k %d)' % (name, sd, replay_ops, pred, la, lb, k))
            check(replay_ops <= (c['meas_iter'] + c['replay_iter']) * max(la, lb) + c['replay_const'], 'replay bound')
        print('%-10s seed %3d halt %2s steps %5d hits %5d dp %4d restarts %4d tb %4d replay_ops %7d  total %d' %
              (name, sd, vm.halt, steps, hits, dps, rest, dl, replay_ops, nonsl + steps * nsl))
        if expect is not None: check(vm.halt in expect, '%s seed %d: halt %s not in %s' % (name, sd, vm.halt, expect))
    return res


def main():
    ns = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
    routine_tests()
    replay_tests()
    print('routine tests done, failures so far:', len(FAILS))
    base = dict(S=3000, U=3000, SB=12, IDB=12, LRC=17 << 8, Tb=3000, HMAX=10 ** 9, DPLO=18, DK=2, DT=3, PFLO=22, PFN=4, WTEST=26)
    seeds = list(range(1, ns + 1))
    e2e('base', base, seeds, expect=(1, 13))
    # width 32, DP of 10 bits and a comparator, prefilter of 6 planes; trails of mean length ~1000 steps against a replay cap of 400:
    # a colliding trail longer than the cap is refused (halt 13)
    w32 = dict(S=3000, U=3000, SB=12, IDB=12, LRC=400, Tb=60000, HMAX=10 ** 9, DPLO=22, DK=3, DT=5, PFLO=26, PFN=6, WTEST=32)
    e2e('w32cap', w32, seeds[:3], expect=(1, 11, 12, 13), W=32)
    small = dict(base, S=400, U=400, SB=9, IDB=9, LRC=2000, Tb=4000)       # small table: long probe runs, wraps; U exhaustion possible
    e2e('smalltab', small, seeds, expect=(1, 11, 12, 13))
    abort = dict(base, HMAX=3)                                            # hit counter abort
    e2e('abort', abort, seeds[:3], expect=(10,))
    tb = dict(base, LRC=3, Tb=5)                                          # Tb reached
    e2e('tb5', tb, seeds[:2], expect=(12,))
    uex = dict(base, S=264, U=264, SB=8, IDB=9, Tb=100000)                 # trail limit reached
    e2e('u264', uex, seeds[:3], expect=(11, 1, 13))
    packed = dict(base, S=200, U=800, SB=8, IDB=10, LRC=2000, Tb=8000)     # U = 4 S: every word fills its four records
    e2e('packed', packed, seeds[:4], expect=(1, 11, 12, 13))
    nocmp = dict(base, DK=0, DT=1)                                        # no comparator (theta = 2^-H)
    e2e('nocmp', nocmp, seeds[:2], expect=(1, 13))
    print('checks run: %d, failures: %d' % (NCHK[0], len(FAILS)))
    return len(FAILS)


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
```

### D.4 Output of `python3 other5_test.py 2 7`

```
replay tests: found 47, p=q 0, different ends 13
routine tests done, failures so far: 0
base       seed   1 halt  1 steps   203 hits   203 dp  139 restarts  138 tb    0 replay_ops  765425  total 20498522
base       seed   2 halt  1 steps    89 hits    89 dp   78 restarts   77 tb    0 replay_ops  494273  total 9373204
w32cap     seed   1 halt 13 steps   445 hits   441 dp   81 restarts   80 tb    0 replay_ops       6  total 42332170
w32cap     seed   2 halt 13 steps  1499 hits  1474 dp  223 restarts  222 tb    0 replay_ops       6  total 141690276
smalltab   seed   1 halt  1 steps   203 hits   203 dp  139 restarts  138 tb    0 replay_ops  765425  total 20495223
smalltab   seed   2 halt  1 steps    89 hits    89 dp   78 restarts   77 tb    0 replay_ops  494273  total 9369666
abort      seed   1 halt 10 steps     4 hits     4 dp    0 restarts    0 tb    0 replay_ops       0  total 710136
abort      seed   2 halt 10 steps     4 hits     4 dp    2 restarts    2 tb    0 replay_ops       0  total 714875
tb5        seed   1 halt 12 steps     5 hits     5 dp    1 restarts    1 tb    1 replay_ops       0  total 806467
tb5        seed   2 halt 12 steps     5 hits     5 dp    5 restarts    5 tb    1 replay_ops       0  total 815938
u264       seed   1 halt 11 steps    19 hits    19 dp    9 restarts    8 tb    0 replay_ops       0  total 2135596
u264       seed   2 halt 11 steps    13 hits    13 dp    9 restarts    8 tb    0 replay_ops       0  total 1571918
packed     seed   1 halt  1 steps   203 hits   203 dp  139 restarts  138 tb    0 replay_ops  765425  total 20495047
packed     seed   2 halt  1 steps    89 hits    89 dp   78 restarts   77 tb    0 replay_ops  494273  total 9369497
nocmp      seed   1 halt  1 steps   177 hits   177 dp  170 restarts  169 tb    0 replay_ops  511751  total 17874466
nocmp      seed   2 halt  1 steps    89 hits    89 dp  107 restarts  106 tb    0 replay_ops  494273  total 9441324
checks run: 424, failures: 0
```

## Appendix E. make_ls5.py (writes experiments/ls5.py) and katcheck.py

```python
#!/usr/bin/env python3
"""make_ls5.py ROWDIR OUT NR: writes the organizer experiment program ls5.py for the row in ROWDIR (plan.txt, meta.txt,
params.json, the block files) from the template ls1.py of 71fefe66: its reference, its rho-w22 and proj-w256 searches and its
main are kept; its in-Python generator is replaced by ls5_gen.py (gen4.c in Python), which rebuilds the blocks from the
generator's decisions (PLAN) and must reproduce every block file byte for byte (SHA-256), and the step is executed as the
attack executes it (P, the bodies as called with the iota XORs, E)."""
import sys, os, json, hashlib

row, out, NR = sys.argv[1], sys.argv[2], int(sys.argv[3])
here = os.path.dirname(os.path.abspath(__file__))
tmpl = open(os.path.join(here, 'ls1_template.py')).read()
gen = open(os.path.join(here, 'ls5_gen.py')).read()
P = json.load(open(os.path.join(row, 'params.json')))
KB = P['KB']
names = ['P.bin'] + ['B%d.bin' % j for j in range(1, KB + 1)] + ['E.bin']
blobs = {n: open(os.path.join(row, n), 'rb').read() for n in names}
plan = open(os.path.join(row, 'plan.txt')).read().strip()
a = tmpl.index('PLAN = """'); b = tmpl.index('# ---------------- reference ----------------')
head = []
head.append('PLAN = """\n%s\n"""' % plan)
head.append('''PL = {}
for _ln in PLAN.strip().split("\\n"):
    _t = _ln.split()
    if _t[0] in ("trial", "F1", "G1"): PL[_t[0]] = _t[1]
    elif _t[0] == "FG": PL[("FG", int(_t[1]))] = (_t[2], _t[3])
    elif _t[0] == "PHI": PL[("PHI", int(_t[1]))] = _t[2]
TRIAL = int(PL["trial"])            # constants of the generator's selected trial''')
head.append('KB = %d                            # bodies in the cycle of the generic rounds' % KB)
head.append('REGTOP = %d' % P['REGTOP'])
head.append('ONES = REGTOP + 4                 # the all-ones register of the search state')
head.append('NREG = REGTOP + 11')
head.append('BLOCK_SHA256 = {%s}' % ', '.join('"%s": ("%s", %d)' % (n, hashlib.sha256(x).hexdigest(), len(x) // 5) for n, x in blobs.items()))
head.append('''

def consts(trial):
    K = [0] * 25
    K[16] = 0x8000000000000006
    if trial > 0:
        s = (0x9E3779B97F4A7C15 * trial + 1) & M64
        def xs():
            nonlocal s
            s ^= (s << 13) & M64; s ^= s >> 7; s ^= (s << 17) & M64
            return s
        for _ in range(10): xs()
        for l in (0, 2, 3, 5, 7, 8, 10, 12, 13, 15, 11, 14): K[l] = xs()
    return K


KL = consts(TRIAL)


''')
head.append(gen)
head.append('''def compile_prog(prog):
    """The step, executed instruction by instruction (opcode 0 XOR, 1 AND, 2 OR, 3 NOT); R[ONES] holds the all-ones word."""
    P = tuple(prog)

    def step(R, A):
        R[ONES] = A
        for c, d, a, b in P:
            if c == 0: R[d] = R[a] ^ R[b]
            elif c == 1: R[d] = R[a] & R[b]
            elif c == 2: R[d] = R[a] | R[b]
            else: R[d] = R[a] ^ A
    return step


''')
src = tmpl[:a] + '\n'.join(head) + tmpl[b:]
s0 = src.index('def setup():'); s1 = src.index('def to_planes(')
src = src[:s0] + '''def setup():
    for m in (b"", b"abc", bytes(135), bytes(200)):
        assert digest(m, 24) == hashlib.sha3_256(m).digest()
    blocks, PD = G4().build()
    for name, (h, n) in BLOCK_SHA256.items():
        assert len(blocks[name]) == n and hashlib.sha256(encode(blocks[name])).hexdigest() == h, name
    prog = flat_program(blocks)
    return compile_prog(prog), PD, len(prog)


''' + src[s1:]
src = src.replace('NR = 24                         # rounds of the target', 'NR = %d                         # rounds of the target' % NR)
open(out, 'w').write(src)
print('wrote', out, len(src), 'bytes')
```

```python
# katcheck.py ROUNDS KATFILE [REPO_ROOT]: compares the self-test reference (selftest kat) with hashlib and the organizer's verifier/keccak.py
import hashlib, sys
sys.path.insert(0, sys.argv[3] if len(sys.argv) > 3 else '.')   # the challenge repository root (verifier/keccak.py)
from verifier import keccak
R = int(sys.argv[1]); bad_h = bad_o = n = 0
for line in open(sys.argv[2]):
    t = line.split()
    m = bytes.fromhex(t[0]) if len(t) == 3 else b''
    d24, dR = (t[-2], t[-1])
    n += 1
    if hashlib.sha3_256(m).hexdigest() != d24: bad_h += 1
    if keccak.sha3_256(m, rounds=R).hex() != dR: bad_o += 1
print('kat messages %d (lengths 0..%d): 24-round vs hashlib mismatches %d; %d-round vs organizer verifier mismatches %d' % (n, n - 1, bad_h, R, bad_o))
```
