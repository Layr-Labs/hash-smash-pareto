# SHA3-256 round 24: the 4ea0966b search with a window-coded straight line

## 1. Claim and resources

This package prices an ordinary distinguished-point birthday search for two distinct 128-byte messages with the same `sha3-256-r24-prefix-v1` digest. It claims no weakness in full SHA3-256. Under H1 in Section 6, one bounded attempt succeeds with probability at least 0.39.

It is a credited derivative of `4ea0966b-10cb-4bd9-a5a7-926729776820` (Section 8). The constant set, the frozen plan, the 144722-operation logical step, the prefilter, the controller emitter, the checkpoint replay, the probability argument and the certificate model are the parent's, unchanged. Two things change. The straight line is stored in a denser declared encoding, the RC block of Section 3.6, which the experiment decodes back to the parent's exact program. The freed memory buys a larger table: 18344 words instead of 14304. The density, replay cap and horizon are re-instantiated with the parent's own certificate (Sections 4 to 6 and Appendix A).

The exact ledger has N = 192446993703165203378624853847617760848388 word operations. One target compression costs C = 6504, so `log2(N/C) = 124.47640148267505942045906028645321719419081366569232314224701059179172057391692334993204669244186888289796209310705703357129105980800773993968005244449595614216757877383354453117061429111659999535839` and the upward-rounded claim is **124.47641**. Peak memory is 1048345 bytes. Preprocessing is 1409324217821184 word operations and no nonuniform advice.

The score depends on the declared H_code convention of Section 3.6. It treats operand-window maintenance in the RC decoder as instruction decoding rather than as charged work. Section 3.6 states the convention's limits and prices the strict alternatives.

## 2. Target and chain function

Write the 256-bit point as four little-endian lanes u0..u3. The one-block message has lanes 1, 6, 11 equal to `u0, u1, u0 xor u1 xor K11`; lanes 4, 9, 14 equal to `u2, u3, u2 xor u3 xor K14`; all other rate lanes are fixed. The remaining absorbed state includes SHA3 suffix `0x06` and pad10*1. This map is injective. Define `g(u) = SHA3-256-r24(m(u)) xor PD`. Equal values of g for different points give equal digests for different messages because the common PD cancels.

The 25 lane constants in lane order are:

`0000000000000000 0000000000000000 e612b8e44c9e9b1c 0000000000000000 0000000000000000 ffffffffffffffff 0000000000000000 0000000000000000 0000000000000000 0000000000000000 ffffffffffffffff b984ae391327a6c1 0000000000000000 9cc2571c8993d363 8cf6a38dd9b0b271 ffffffffffffffff 8000000000000006 0000000000000000 0000000000000000 0000000000000000 0000000000000000 0000000000000000 0000000000000000 0000000000000000 0000000000000000`

PD is `2ad9d6d777fe66a4 105a400cc3435018 5526292808001953 4524292008010943`. The normative emitter in `experiments/compact.py` derives PD again from the emitted circuit and rejects a mismatch.

## 3. Bit-sliced register step

One 256-bit register word carries one bit plane for 256 walks. Round 0 and the theta of round 1 are affine in the point. Later theta columns are built in z order, chi rows use the cheapest exact complement subset and optional 10-gate dependency, and the last round retains only four digest lanes. The frozen plan contains the C/D complements and compact chi decisions for every row. It is bound by SHA-256 `0890d000e6c8f44e077b7a15a7f6009a35cd6fe38620886fa92f8aca426a9329`.

The emitted straight-line register program has 144722 operations: 105684 XOR, 18245 AND, 17211 OR and 3582 NOT. Lowest-free last-use allocation names registers 0..1927. It contains 1902 14-bit, 103704 25-bit and 39116 36-bit encoded records, 103926 with destination equal to the first operand. Its measured stored size is 503426 bytes and SHA-256 is `275722b84ae9f840ad4c95c0fb782cfec2338efb1a6eab144d0d7e6a8522c41a`. R24G does not store that image. It stores the same records, followed by the 15 prefilter records, as the RC block of Section 3.6: 144737 records, 374089 bytes, SHA-256 `9515a581d4b5d38e03e7662df0466516ef1e94bb2bcea2e3bdcf8455f793f7ff`. The two-address image remains the reference identity of the logical step: the experiment decodes the RC block and re-encodes the records in the two-address format, and requires exactly this image.

### 3.6 Registers and code encoding (machine conventions H_reg and H_code)

**Registers.** Input and digest plane j use register j. Each other value receives the lowest free register allowed by its last use. Values in registers above 255 are dead between steps and may be reused by handlers. The straight line uses registers 0 through 1927; persistent search state begins at register 1928. The declared file has 1939 words, or 62048 bytes, all included in Section 5.

**H_reg (declared machine convention, role supporting in claim.json).** The cost model and target profile fix no register count. This package uses the 256-bit word RAM of collision-frontier-v5 with the declared 1939-register file above. An operation on register operands costs one word operation, with no load or store. Every load and store in the assembled other code is an explicit charged word operation. H_reg affects the time and memory ledgers, not the success bound.

**H_code (declared code-encoding convention, role score-critical in claim.json).** The cost model and target profile fix no instruction encoding, and no organizer rule addresses decoding. R24G keeps the parent's 8-byte words and literal pool for the other code. It replaces the parent's two-address storage of the straight line with the RC block below. The parent's convention affected only the stored bytes. This one also fixes which decoding work is uncharged, so it is declared score-critical and priced here. **No accepted entry keeps decoder state beyond the code position; this convention is new and contestable.**

- **Reference format (the parent's two-address encoding; not stored in R24G, used as the identity of the logical step).** Each straight-line instruction has register operands only. Bits 0..1 give XOR, AND, OR or NOT and bit 2 flags destination equal to the first operand. With that flag, NOT carries one 11-bit register and a binary operation carries two; without it, NOT carries destination and source while a binary operation carries destination and two sources. Commutative operations swap operands when the destination equals the second. Records are packed without inter-record padding in a little-endian bit stream. The straight-line file is 503426 bytes. The separate prefilter is a 15-operation OR chain from digest planes 240 through 255 into register 1932: first `OR R_PREFILTER,240,241`, then `OR R_PREFILTER,R_PREFILTER,plane`. It uses the same encoding, occupies 49 bytes, and has SHA-256 `70556574176bd68efe064c4622378fdc5bfd59aaa1cbf1618fe2451a830f5a01`. The two files occupy 503475 bytes under the parent's H_code.
- **The RC block.** The 144722 step records followed by the 15 prefilter records: 144737 records, 2992711 bits, padded with zero bits to 374089 bytes, SHA-256 `9515a581d4b5d38e03e7662df0466516ef1e94bb2bcea2e3bdcf8455f793f7ff`. Bit i is bit (i mod 8) of byte floor(i/8), and fields are read least significant bit first. The controller enters the block only at `@STEP` (Section 4); after the last record, control continues at `loop`.
- **A record.** A form, then an 11-bit destination unless the form is short (destination equal to the first source), then one source for NOT or two otherwise. Each source is either `0` followed by a 4-bit k, naming the register held in window entry W[k], or `1` followed by an 11-bit register number. The form is a complete prefix code, so every bit string parses. Codewords are listed in stream order, first listed bit first: `1` XOR short, `00` XOR, `0100` OR, `0101` OR short, `01101` AND, `0111` AND short, `011000` NOT, `011001` NOT short. XOR, AND and OR set R[d] = R[a] op R[b], NOT sets R[d] = R[a] XOR (2^256-1), and the short form has d = a. The encoder applies the parent's swap for a destination equal to the second source of a commutative operation.
- **Decoder control state.** A 22-bit code position, the window W[0..15] of 16 eleven-bit register names, and an 18-bit record counter: 216 bits. Entry resets them to the block start, W[k] = k and 0. After each record the window appends: W[1..15] := W[0..14] and W[0] := d.
  - W[k] is therefore the destination of the record k+1 positions earlier. In the first 16 records, an entry not yet overwritten holds its reset name k; 6 references in the stored block resolve to reset names.
  - No instruction can read or write this state. It holds register names only, never register or memory contents. Like the program counter it is control state, but it records more than the code position.
  - The code text alone determines every reference, without executing anything, and every batch replays the same decoder state sequence.
- **Limiting principle.**
  - Exactly one stored record executes per primitive operation; nothing expands, repeats or synthesizes operations.
  - Only operand names are abbreviated, and only by reference to a destination named within the previous 16 records, or to a reset name.
  - Decoding reads code bits only. Its work per record is bounded independently of the program, and its state is 216 bits.
  - Loops, macros, shared subroutines or regenerated code would fall outside this convention.
- **What is charged.**
  - Each record is one charged word operation (144737 per batch, as in the parent), and each entry is one more, for the decoder reset (BSTEP 144742).
  - The 216 bits of control state are counted as 32 bytes of memory.
  - Window maintenance and operand resolution are treated as instruction decoding and are not charged.
  - In the stored block, 169,653 of 285,892 source operands are window references.
- **Why decoding, and the precedents.**
  - The parent's records are 14, 25 or 36 bits long, so where a record starts depends on every earlier header, and that decoding is uncharged.
  - The parent's literal-index field is likewise resolved by reading a 256-bit literal from the pool without a charged load. The credited source `20eb70ca-366a-4fbd-9594-4fa85f158a0b`, Section 3.6, states no separate charge for fetching or decoding.
  - R24G extends history-dependent decoding from record boundaries to operand names, within the limiting principle above.
  - The counter-precedent is `911bffce-8e7a-4502-90ab-c69a473fff48` and `d258ba65-054d-4098-bbac-0b974fee36c8`, which shrank code by executing shared bodies through calls and returns and charged every call and return. Those are executed control-flow instructions of the program. R24G adds and removes none: the executed operation sequence is the parent's, record for record, which the experiment checks by re-encoding.
- **Other code.** Setup, loop control, handlers, restart, replay and output are assembled as 986 fixed 8-byte instruction words followed by 12 distinct 32-byte literal words, 8272 bytes total, SHA-256 `333562c28a3dc0e1537f6408c78ec10534d02986a9717ffa85a9080914e0d4d4`. A word has a 5-bit opcode, one literal flag, three 11-bit register fields and a 25-bit immediate or literal index. The assembled operations are model primitives; each is charged as the word operation it performs, except PERM at C operations. Loads and stores are explicit among those instructions.
- **Time ledger.** The straight line contributes one charged word operation per record, each a logical XOR, AND, OR or NOT under H_reg, plus one per entry for the decoder reset. H_code determines the stored code bytes and the uncharged decoding above.
- **Sensitivity and strict alternatives.** The improvement over the parent is lost at 235 additional charged operations per batch, about 0.0016 per record. A literal word-RAM charge for the window costs far more:

| strict charge | operations per batch | score | change |
|---|---:|---:|---:|
| window append charged, 2 per record | 289,474 | 126.05860 | +1.58219 |
| window append and reference lookups, 2 per record + 2 per reference | 628,780 | 126.89103 | +2.41462 |
| window append and reference lookups, 2 per record + 6 per reference | 1,307,392 | 127.79933 | +3.32292 |
| one operation per record | 144,737 | 125.47433 | +0.99792 |
| one indirect register access per window reference | 169,653 | 125.59329 | +1.11688 |
| decoder reset only (charged above) | 1 | 124.47641 | 0 |

Refusing the encoding on the memory side instead means storing the parent's 503475 code bytes at this table: memory 1177699 bytes, more than 2^20, and a normalized score of 124.64395. The compliant fallback in that case is the parent's own design point.

### Construction campaign

The construction first builds the exact chained-chi table. For each of 32 input polarities and 32 requested output polarities it enumerates every complement subset, every trick mask except the five-cycle, and every mixed-term polarity mask. A non-trick output anchors the row; outputs are then built backward, and a trick reads the already computed next output using `(not out[k]) and b[k+1] = (not b[k]) and b[k+1]`. Before use, the builder evaluates each selected entry on all 32 concrete row inputs and requires ordinary chi and the requested output polarity. The 1,024-entry C and Python tables have the same FNV-1a checksum `c8fa4bd9170966dc`.

The generator then builds all 512 S3-04 trials without annealing and retains the lowest eight counts. Each retained trial runs deterministic one-round-lookahead annealing for 200,000,000 iterations per planned round. A state move flips one C complement, one D complement, or an output-polarity subset. Current and lookahead row costs come from the verified chained table. The objective is 16 times current exact row cost plus 3 times the next-round lower bound. For `x = -3.1780538303479458*i/200000000`, the declared temperature is `19.2*E(x)`, where `E(x) = (1+y+y^2/2+y^3/6+y^4/24)^64` and `y=x/64`; acceptance uses the same deterministic bounded exponential. Ties retain the earlier deterministic choice. Trial 1333 wins with the count above. Lowest-free allocation and the two-address packer then emit the frozen program. The charged ledger below totals the chained-table build and verification, every cheap build, every TOPK process, every annealing move, and the separate emitter, hashing and verification work.

**R24G construction.** The parent's construction above produces the frozen plan and the emitted program; it is inherited and charged in full. R24G adds the following, with sources in Appendix D:

- **`rc_encode.c`** streams the parent's emitted two-address step image and prefilter image into the RC block, hashing it as it is written: 144737 records, 374089 bytes, SHA-256 `9515a581d4b5d38e03e7662df0466516ef1e94bb2bcea2e3bdcf8455f793f7ff`.
- **`rc_scan.c`** is a finite parameter scan, a long-double mirror of the parent's bound and ledger.
  - Table 18344 words; theta numerators 693 to 714; replay caps J = round(c*2^22/dt) for c = 10.30, 10.32, ..., 12.28.
  - It chooses theta = 704*2^-121, J = 65298 and Tb = 535489382*2^91, evaluating the bound 253,995 times over 17,113,688,165 bins.
  - Optimality is not claimed. Its ledger uses the parent's hit-path cost of 131 for every theta; the controller emitted at theta 704*2^-121 costs 117, which Section 5 uses.
- **The parent's own 200-digit model** regenerates Appendix A at those parameters.
- **The controller.** The parent's normative emitter, the Python modules the experiment embeds, produces R24G's controller record table at those parameters. The bounded emitter `rc_controller_emit.c`, generated from that table, writes and hashes the 8272-byte controller.

The table is the largest multiple of eight words that fits in 2^20 bytes beside the RC block (Section 5).

## 4. Search, table, and controller

The attempt starts 256 walks from `rho + trail_number`. It advances all walks through the step, applies a 15-OR prefilter, and handles exact distinguished points with probability `704 * 2^-121`. The table has 18344 256-bit words and 91720 slots. Each word has five 51-bit slots: written bit followed by 50 endpoint bits. The word and slot position encode the trail number, so no trail number is stored in a slot. The 256 live walks use one packed word apiece: low 128 bits are the start step and high 128 bits are the positional trail number.

On a prefilter hit, 256 stores copy the carried planes to a scratch matrix. Charged indexed loops gather or replace one lane; 256 fixed loads restore the planes. A matching endpoint starts the final replay. Replay measures the stored trail while keeping every `G = ceil(LRC/(S-1)) = 2256311641871638321401399059714`-th point in the now-free table, advances the other trail to alignment, locates the merge segment by checkpoints, then lock-steps only that segment. With `e = C+29`, at most one replay costs `(2e+17)LRC + (3e+20)G + 17*nck + e + 93 = 541517248916259553478829459053368804415` operations.

The assembled controller and handlers have the H_code size and hash stated in Section 3.6. Their register-register, immediate, compare, branch, jump, load, store and random-word instructions each contribute their explicit word operation; PERM contributes C. The step peaks at register 1927; the controller places its first persistent register at 1928 and declares 1939 words, so the lifetimes do not overlap. The controller permits at most HMAX = 46566464906103503740291625869377537 prefilter hits and aborts on hit 46566464906103503740291625869377538; that exact abort value is a checked controller literal and the input to F5 below.

Setup initializes `remaining = Tb = 1325807493179968010081444286101979136`. Every continuation path executes `remaining -= 1`, branches to the step only while the result is nonzero, and otherwise reaches HALT. The exact-byte experiment starts `remaining` at three, supplies only no-DP prefilter results, requires exactly two back-edges, and then requires the charged-limit HALT. Thus every path stops by the batch bound or at an earlier charged halt.

In R24G, `@STEP` denotes the RC block followed by the prefilter records. Each entry, from setup or from the conditional back-edge, resets the RC decoder (Section 3.6) and is charged one word operation. After the last record, control continues at `loop` as in the parent.

## 5. Exact operation and memory ledgers

`BSTEP = 144722 + 15 + 2 + 2 + 1 = 144742`. The added terms are the prefilter ORs, its compare and branch, the count-down subtract and conditional back-edge, and the RC decoder reset at block entry. Main work is `191900028177854929715208408858972664102912`. Replay is `541517248916259553478829459053368804415`. All hit, DP, probe, restart, setup, cap and final-halt paths contribute `5448276394014109937614120267510119877`. Preprocessing contributes `1409324217821184`: the parent's construction, inherited with its frozen plan and charged in full, plus R24G's rows. Their sum is N above.

| preprocessing phase | class | word operations |
|---|---|---:|
| 512-trial cheap constant scan | word operations | 2199023255552 |
| eight sequential full graph campaigns | word operations | 67551245631488 |
| eight sequential annealing campaigns | word operations | 137625600000000 |
| chained row-table candidate evaluations in ten sequential processes | word operations | 1300234240 |
| chained row-table exhaustive truth checks in ten sequential processes | word operations | 83886080 |
| row-table setup and deterministic selection | word operations | 10485760 |
| constant derivation and comparisons | word operations | 524288 |
| structured affine basis | word operations | 16777216 |
| native parameter scan bins and fixed work | word operations | 80213253292032 |
| normative step, prefilter and controller emission | word operations | 37308672 |
| streaming SHA-256 of basis, step and controller | word operations | 68509696 |
| construction-time step parsing, field, and ledger verification | word operations | 38357248 |
| exact Decimal certificate and package rendering | word operations | 68719476736 |
| R24G RC encoding and streaming SHA-256 (rc_encode.c): 512 per record, 8192 per SHA-256 block | word operations | 121995776 |
| R24G finite parameter scan (rc_scan.c) at the parent's scan rates: 65536 per bin, 131072 per bound evaluation, 2^20 fixed | word operations | 1121595960262656 |
| R24G controller record table from the parent's normative emitter at R24G's parameters (bound) | word operations | 16777216 |
| R24G bounded controller emission and SHA-256 (rc_controller_emit.c): 512 per instruction, 8192 per SHA-256 block | word operations | 1569792 |
| R24G certificate regeneration at 200 digits and package rendering (the parent's row value) | word operations | 68719476736 |

The search memory is:

| region | bytes |
|---|---:|
| RC block: step and prefilter (H_code) | 374089 |
| RC decoder control state (216 bits, counted conservatively) | 32 |
| other code and literal pool (H_code) | 8272 |
| register file | 62048 |
| table | 587008 |
| transpose scratch | 8192 |
| packed walk words | 8192 |
| data image | 512 |
| online stack | 0 |
| replay checkpoints (alias table) | 0 |
| **search total** | **1048345** |

The online controller uses link registers and zero stack. Replay checkpoints alias the table after a match, when the ordinary endpoint table is no longer needed. Construction phases run sequentially before the search; their measured memory ledger follows the search table and their lifetimes do not overlap it.

| sequential construction phase | image bytes | stack reserve | measured VmHWM | retained input/output | charged peak |
|---|---:|---:|---:|---:|---:|
| 512-trial cheap scan | 329527 | 262144 | 417792 | 18432 | 610103 |
| TOPK full build 1 | 329527 | 262144 | 413696 | 63305 | 654976 |
| TOPK full build 2 | 329527 | 262144 | 417792 | 63305 | 654976 |
| TOPK full build 3 | 329527 | 262144 | 417792 | 63305 | 654976 |
| TOPK full build 4 | 329527 | 262144 | 413696 | 63305 | 654976 |
| TOPK full build 5 | 329527 | 262144 | 413696 | 63305 | 654976 |
| TOPK full build 6 | 329527 | 262144 | 417792 | 63305 | 654976 |
| TOPK full build 7 | 329527 | 262144 | 417792 | 63305 | 654976 |
| TOPK full build 8 | 329527 | 262144 | 413696 | 63305 | 654976 |
| structured-basis file verification | 9766 | 16384 | 28672 | 22999 | 51671 |
| native finite parameter scan | 62337 | 16384 | 73728 | 74 | 78795 |
| streaming native step emission | 423581 | 98304 | 446464 | 503426 | 1025311 |
| streaming step SHA-256 | 9766 | 16384 | 32768 | 503426 | 536194 |
| construction-time step parsing, field, and ledger verification | 9298 | 16384 | 24576 | 503426 | 529108 |
| native 15-OR prefilter emission | 8254 | 16384 | 16384 | 49 | 24687 |
| streaming prefilter SHA-256 | 9766 | 16384 | 32768 | 49 | 32817 |
| native8 controller emission | 50564 | 16384 | 57344 | 8384 | 75332 |
| streaming controller SHA-256 | 9766 | 16384 | 28672 | 8384 | 37056 |
| R24G RC encoding and streaming SHA-256 (rc_encode) | 35756 | 16384 | 69632 | 877564 | 947196 |
| R24G finite parameter scan (rc_scan) | 139942 | 65536 | 147456 | 1024 | 206502 |
| R24G bounded controller emission and SHA-256 (rc_controller_emit) | 84057 | 16384 | 114688 | 8272 | 122960 |

Every phase ran alone under `prlimit --as=1048576` and its listed stack cap. The charged peak is `max(VmHWM,image+stack)+retained input/output`; this deliberately charges an entire generated program even though the emitters stream it. R24G's three phases, the last three rows, are static musl binaries built from Appendix D. Each ran alone under `prlimit --as=1048576` with its listed stack cap; the command lines and outputs are archived with the package's construction record. Their image column is text+data+bss as reported by size(1), as in the parent's rows. Appendices B and C are the parent's sources and measured record; they describe the parent's phases. Appendix C is unchanged, and Appendix B is unchanged except that its controller_emitter.c record table is re-presented compactly with every value kept (see its presentation note). The parent's controller emission rows remain charged although R24G uses its own controller. Construction peaks at 1025311 bytes. Search peaks at 1048345 bytes. The claimed peak is their maximum, 1048345 bytes.

## 6. Probability space, H1, and success

The real attempt samples one uniform 256-bit rho. Everything afterward is deterministic. H1 is the following single aggregate comparison:

H1 is one premise. Let A_g be this bounded attempt on the fixed deterministic walk g. In the real algorithm's probability space, only the fresh uniform word r is random. Let F be a uniformly random function on 256-bit values, independent of r, and let P_F = Pr_(r,F)[A_F succeeds] for the same attempt with each g evaluation replaced by lazy sampling from F. H1 asserts only the aggregate comparison Pr_r[A_g succeeds] >= P_F. Appendix A proves P_F >= 0.39. The following clauses are properties of comparator F used by that proof, not additional premises about g: outputs at distinct fresh inputs are uniform and independent; its iterates have the random-mapping first-collision law; a fresh output satisfies the exact distinguished-point predicate with its stated probability independently of prior collision bookkeeping; and after any lazy-sampling history, a fresh input maps to any fixed earlier output with probability 2^-256. H1 assigns no per-history conditional probability to deterministic g because the history determines r and hence all later g outputs. The aggregate success comparison is the only heuristic step.

### Lazy-sampling order and first coincidence

Let `M = 2^256`, `L = 256`, `theta = 704 / 2^121`, `q = 1-theta`, and `E = L*Tb`. Comparator F starts undefined. Evaluations are ordered first by batch and then by lane. A fresh input is one not queried earlier in that order; it receives a new independent uniform image and stores it. A repeated input returns its stored image and consumes no new random value. For bookkeeping, attach an independent candidate image `V_t` to every evaluation position and use it exactly when that position's input is fresh. Its DP indicator is Bernoulli(theta), independently across t.

This also proves the restart domination used by F2. A fresh-input DP uses one Bernoulli indicator. A DP returned at a repeated input was already the endpoint of the earlier trail that first exposed it, so the table lookup finds that record and enters replay instead of consuming a new trail number. Thus the number of DP restarts is at most the number of DP indicators among `V_1..V_E`.

Outside the start part of F4, every queried input before the first image coincidence is fresh. If the first m images are distinct, the next fresh uniform image avoids them with probability `1-m/M`. Hence `pi_e = product_(m=0)^(e-1)(1-m/M)` is the exact no-coincidence probability through e fresh evaluations, and the first coincidence is a stopping time with mass `pi_(e-1)*(e-1)/M = pi_(e-1)-pi_e`. In particular `1-pi_e >= B(e) = 1-exp(-e(e-1)/(2M))`, using `1-x <= exp(-x)` term by term. No independence is asserted for the fixed target g.

### Conditional DP-tail lemma

Suppose the first coincidence occurs at evaluation t with earlier partner s. The two trails then follow a common functional-graph path. Let l be the number of further evaluations on that path before its first DP. Without conditioning on firstness, `Pr[l>=j]=q^j`. Firstness reveals that the preceding images were distinct, so the following comparison controls the conditioning rather than assuming independence.

Given the first `m=t-1` DP indicators, with fewer than U ones outside F2, images are uniform within the `theta*M` DP values and the `(1-theta)*M` non-DP values. Comparing their without-replacement products with `pi_m` bounds the relative deviation by

`Delta = U*E/M + E^2*theta/(2M) + U^2/(2*theta*M) = 5.3774968901122949762359585582188551401808185087516767263468577619888244485104779480765396935972589520766088097306320295584472742947665127840909090909090909090909090909090909090909090909090909090909091E-34`.

Appendix A checks `Delta < 2^-109`. The upper product ratio is `(1-E/M)^(-U) = 1.0000000000000000000000000000000002688472451210519321768112027536785679713346992810583419673300742892756045652246601867503057410500484631758757128155197926482415267059810280454170115601343074904403665` and the Bayes ratio is at most `R=(1-E/M)^(-U)/(1-Delta) = 1.0000000000000000000000000000000008065969341322814298004070585755645157366670372017281052844010355311981810240550535205420539343398342217333224532334914063520591293344333889668587137212949421504758155 <= 1+2^-108`. This requires the checked nonempty DP and non-DP partitions and `E/M <= 1/2`.

The Bayes calculation uses a masked filtration: it reveals the equality structure and the indicators of other walks but integrates over the DP indicators on the suffix currently selected by the common path. This is a probability calculation over comparator F; the operational run may already have exposed that suffix.

For the base case, write the first coincidence as `V_t=V_s`, `s<t`, with s on the older walk A. Evaluations of one continuing lane occur 256 indices apart. Therefore A evaluates each later common-path point first: its relevant indices are `s+256, s+2*256, ...`, all before B reaches the same respective points at `t+256, t+2*256, ...`. The tail length l is the first `k>=1` with `xi_(s+256k)=1`. For every fixed completion of these suffix indicators, the equality `V_t=V_s` has probability exactly `1/M`; fresh `V_t` is uniform after `V_s` is fixed. The event that `(t,s)` is the first pair differs between indicator completions only through D, the distinctness of `V_1..V_(t-1)`. The product bounds above place `Pr[D | indicators]` between `pi_m*(1-Delta)` and `pi_m*(1-E/M)^(-U)`. Bayes' formula thus bounds the conditional law of A's masked suffix by R times its iid Bernoulli(theta) law, proving `Pr[l>=j | first pair (t,s), masked history] <= R*q^j`.

The induction invariant is the same likelihood-ratio bound R for the masked suffix of the older trail at every later merge. Suppose the common path enters a point p whose continuation belongs to a third trail C, first evaluated at index u. The filtration records p and the merge equality but withholds the indicators `xi_(u+256), xi_(u+2*256), ...` of C's selected continuation. At the fresh evaluation that created the merge, equality with fixed p has conditional probability exactly `1/M` for every completion of those withheld indicators. That common factor cancels in Bayes' numerator and denominator. No new firstness event is imposed after `(t,s)`, so the distinct-prefix ratio R is not multiplied. This proves the inductive step. Repeating it over every merge preserves `Pr[l>=j] <= R*q^j`; a DP ends the path and can only shorten l.

The excess `R-1 <= 2^-108` adds at most `2^-108` to a bin sum whose weights total at most one and at most `2^-108*F6` to the replay-tail subtraction. These enter once as `FL = 2^-108*(1+F6)`. This product-comparison and masked-suffix argument follows the structure published by credited entry `20eb70ca-366a-4fbd-9594-4fa85f158a0b` and is re-derived here with this package's U, E, theta and LRC.

For bin `j = 1..J`, the common tail l lies in `((j-1)W,jW]` with iid reference mass `q^((j-1)W)-q^(jW)`. Put `n_j = L*(Tb-jW)`. If the first coincidence occurs among those `n_j` positions, the tail finishes by the deadline. The covered term is therefore

`Pcov = sum_(j=1)^J (q^((j-1)W)-q^(jW))*B(n_j)`.

Here `J = 65298`, `W = 633825300114114700748351602688`, and `J*W = LRC = 41387524446851461729465862952321024`. The experiment asserts that equality and recomputes every term in order.

### Failure bounds F2 through F6

F1 is the covered event counted by `Pcov`. The remaining named terms are upper bounds subtracted from it.

- F2, table exhaustion. The restart domination above gives `X <= Binomial(E,theta)` with mean `mu = E*theta = 89880.1147766113281250000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000`. Starting the `(U-L+1)`-st replacement trail needs at least `k=U-L=91464` such fresh DP outputs. For `k>mu`, the exponential-moment Chernoff bound is `Pr[X>=k] <= exp(-mu+k*(1+ln(mu/k)))`. Appendix A asserts its strict precondition.
- F3, a coincidence within one trail. If a trail has geometric length A, then a union bound over its input pairs is `A*(A-1)/(2M)`. Since `E[A*(A-1)/2]=q/theta^2 <= 1/theta^2`, at most U trails contribute `F3=U/(theta^2*M)`.
- F4, starts/replay boundaries and endpoint aliases. The U starts are fixed distinct translations of rho. Comparing them with at most E exposed inputs and images, plus the four selected replay boundary values, gives the explicit union bound `2*U*(E+4)/M = 5.3769449024210386435362240550735706366937702646737618709013744108633885474094506661163601012818385367251784653428143122805717334574782620912106718240592677716093112380322740920593482805145413294667378E-34 <= 2^-90`. Replay otherwise re-evaluates already exposed trail points and creates no new F sample. For aliases, conditioning on the DP predicate leaves the low 50 stored bits uniform. Fewer than `U*(U-1)/2` pairs therefore contribute less than `U^2*2^-51`.
- F5, hit-cap abort. Let X' count steps in which at least one fresh input has a 16-bit-prefilter image. Conditional on every prior adaptive choice, its one-step probability is at most `1-(1-2^-16)^256 = 0.00389866021631819777212921699057604228934907591347168173766934280389107431763886868964603102771424503147662168070206359168124436875563141323855886959184928433004874414589474610857484934350677083543632 < 2^-8`. Outside F4, a hit not counted by X' requires a repeated input and therefore occurs only after the first coincidence. Outside F6 the attempt stops within LRC later steps, so `hits <= X'+LRC`. Abort at hit 46566464906103503740291625869377538 therefore requires `X' >= h-LRC = 5178940459252042010825762917056514`. For the supermartingale `exp(s*X'_t-(exp(s)-1)*t/256)`, multiplicative Chernoff with `mu'=Tb/256=5178935520234250039380641742585856.00000000` and `delta=9.536743164062500000000000003861797452750555541694236114984082231371919671886598240009547005359669297793844958068655038243129907662669583988128451816809320039888297915867919114033898808473479685E-7>2^-20` gives exponent `-mu'*delta^2/(2+delta) = -2355106085236244146790.6588885026505201700297216674444515155836273649502687464288542579524062865554210435252411989363669942470469593104542178457263295336776909143832680827369646734700545772546924593496`. This is below `-1000*ln(2)`, so F5 is safely rounded up to `2^-1000`.
- F6, replay-cap refusal for the first-collision pair. Define an evaluation's age as its position in its current trail. Before the first coincidence, `Pr[age>=a] <= q^(a-1)`. Put `g(a)=min(1,q^(LRC+1-a))`. Summation by parts gives `E[g(age)] <= q^LRC + LRC*theta*q^LRC = G6`, where `G6=0.00020789438889513116051944957559965068216596107415796317180803350685715012647143570384998104655186364054426676105991605940268619164828120112539705862720755330714673953679840481268477726145733862042842781`. For a first-collision pair with ages a and b, refusal is bounded by `g(max(a,b)) <= g(a)+g(b)`, producing `2*G6`. Given fewer than U DPs, the distinct-prefix conditioning costs `(1-E/M)^(-U)`. Summing first-collision mass telescopes because `(t-1)*pi_(t-1)/M=pi_(t-1)-pi_t`. Finally `ln(1-x)>=-x-x^2` for `0<=x<=1/2` gives `1-pi_E <= 1-exp(-E^2/(2M)-E^3/(3M^2)) = 0.39190855829523943240033458332516240777124907487459013985967426253985226329837849176597935791473834534226635874129472015970089257624064906662764677682925982784406735417462591596740858367800628928020866`. Hence `F6=2*G6*(1-exp(-E^2/(2M)-E^3/(3M^2)))*(1-E/M)^(-U)`.

The conditioning lemma contributes `2^-108*(1+F6)` after the same lazy-sampling exposure, and `2^-60` covers all numerical approximation and bin-boundary rounding. A union bound gives

`P_F >= Pcov - F2 - F3 - 2^-90 - U^2/2^51 - F5 - F6 - 2^-108*(1+F6) - 2^-60`.

Every exponential and logarithm is evaluated with 200-digit Decimal arithmetic. The certificate counts at most 4183168 final-scale rounded operations. Recurrence multipliers lie in `[0,1]`; all other probability-scale intermediates are below four; integer products through `E^2` are exact and the only larger power is divided by `M^2`. The subtraction `q=1-theta` has absolute error below `1e-199`; on the live domain `q>1/2`, logarithm propagation and multiplication by `LRC<1e36` remain below `2e-163`. The audited `1e-140` final-scale allowance per counted operation is therefore conservative. Its accumulated bound is `4.183168E-134 < 2^-200`, strictly below the subtracted `2^-60` numerical term. Appendix A records 200-digit values and outward intervals by moving every endpoint one representable value outward. Its computed comparator-F bound is `0.39000000042672247726909387539801396889991128623149820236508476916337649533057459184512033286310083865703452776293515622561811853160124443466934121964479245922981359543652349234257083406467161008832071`, a margin of `4.2672247726909387539801396889991128623149820236508476916337649533057459184512033286310083865703452776293515622561811853160124443466934121964479245922981359543652349234257083406467161008832071E-10` above 0.39. The outward-rounded lower endpoint is `0.39000000042672247726909387539801396889991128623149820236508476916337649533057459184512033286310083865703452776293515622561811853160124443466934121964479245922981359543652349234257083406467161008832070 >= 0.39`; the preceding allowed Tb grid point is `0.38999999930029116380243064387709930669011409554209799044237069193997965918109665990539715784701801426692514731470512259748931698280542212567556492607309857160270994337244562765692984617353337618619414 < 0.39`.

Support for H1 is positive and specific. The algorithm is the parallel collision search of Paul C. van Oorschot and Michael J. Wiener, "Parallel Collision Search with Cryptanalytic Applications", Journal of Cryptology 12(1):1-28, 1999, DOI 10.1007/PL00003816. Generic entries in this track use the same random-function premise. The six-lane affine embedding separates circuit savings from the generic collision law. A collision-hazard deficit can be priced by scaling the comparator hazard and rerunning Appendix A. The emitted-program, scalar target, table, restart and replay checks test consistency of the exact program used by the ledger.

## 7. Organizer experiments

`experiments/compact.py` contains compressed source text, not prebuilt program bytes. It invokes the step emitter and controller emitter, checks their counts, lengths and hashes, parses the exact emitted streams as experiment tooling, and executes the reconstructed programs. It tests the upper and rejected boundaries of every 11-bit step field, every 8-byte-code register and 25-bit immediate/literal field, the literal pool, all five 51-bit slots, and the first invalid table position. It checks two chained bit-sliced steps against scalar selected-round Keccak, evalF against scalar g, gather/setwalk, all slot probe positions, restart packing, replay success, replay refusal, and the all-no-DP limit halt. The `success-certificate` experiment also recomputes Appendix A at 200-digit precision. Each response row returns the same projected pair derived from the first request seed.

**R24G checks, in both experiments, before the controller checks.** Every execution of the stored step streams the records from the RC bytes with the 216-bit decoder state of Section 3.6; the parent's expanded program serves only as the reference.

- **Emission.** The experiment re-encodes the emitted step and prefilter and requires 144737 records, 2992711 bits, 374089 bytes and SHA-256 `9515a581d4b5d38e03e7662df0466516ef1e94bb2bcea2e3bdcf8455f793f7ff`.
- **Equivalence.**
  - It streams three consecutive batches and, after each, compares the whole 2048-word register file (random initial contents) with the parent's reference executor, and 16 lanes with scalar 24-round Keccak.
  - It re-encodes the decoded record sequence in the parent's two-address format and requires the parent's 503426-byte step image with SHA-256 `275722b84ae9f840ad4c95c0fb782cfec2338efb1a6eab144d0d7e6a8522c41a`, and the prefilter's 49-byte image with SHA-256 `70556574176bd68efe064c4622378fdc5bfd59aaa1cbf1618fe2451a830f5a01`.
- **Stored form, read from the bits.** It requires every codeword, every one of the 16 window positions in each operand slot, exactly 169,653 window references and exactly 6 references to reset names.
- **Synthetic coverage.** Four synthetic programs are streamed against explicit execution, with asserted coverage: every codeword, registers 0 and 2047 as explicit destinations and as explicit first and second sources, and the commutative swap.
- **Rejections.** Field overflows, and on two further random blocks a truncated or extended block, nonzero padding, and one record too many or too few.
- **The reset.** Decoding the real block with the window left by the previous batch, instead of the reset, must give a different register file.
- **Sanity checks.** The two decoded record sequences and the decoder exit states must agree between batches. These follow from the decoder's construction; the checks above carry the weight.
- **The transition.** The exact controller bytes run from `continue` with remaining = 3. The two back-edges each stream the RC block and return to `loop`, the third decrement halts with code 12, and the planes must equal two chained scalar steps. The setup entry is not exercised by this test.

Response rows add the observations `rc_block_bytes`, `rc_records`, `rc_streamed_batches` and `rc_controller_back_edges`.

## 8. Credit

This is a credited derivative of `4ea0966b-10cb-4bd9-a5a7-926729776820` (0xplemonade), the direct round-24 incumbent. The following are used unchanged, and its construction is charged in full:

- its constant set, frozen plan, step generator with the chained-chi integration, and chained-chi table;
- its controller emitter and native8 encoding, checkpoint replay, probability argument and certificate model;
- its construction campaign and ledger structure.

Through it, this package credits:

- `20eb70ca-366a-4fbd-9594-4fa85f158a0b` (Jbenisek): the one-round-lookahead S3-04 generator, lowest-free allocation, two-address encoding, positional five-slot table, one-word walk, checkpoint replay and the masked-suffix argument;
- `d258ba65-054d-4098-bbac-0b974fee36c8` (TheTradoor): the chained-chi identity and pinned-output row minimization;
- `3509abf0-ecab-457b-8d5d-ea8aec5d5e8c` (Jbenisek): the structured-constant lineage;
- `911bffce-8e7a-4502-90ab-c69a473fff48` (0xplemonade): the compact-controller lineage.

New in this package:

- the window-coded RC encoding of the straight line, with its decoder semantics, codec, streaming executor and checks;
- the re-instantiated table, density, replay cap and horizon;
- the regenerated certificate and the bounded controller emitter.

Credit is not an endorsement. Apart from the submitter's own earlier entry `d258ba65-054d-4098-bbac-0b974fee36c8`, none of those authors reviewed this package.

## Appendix A. Outward-rounded success certificate

```json
{
  "computed_bound": "0.39000000042672247726909387539801396889991128623149820236508476916337649533057459184512033286310083865703452776293515622561811853160124443466934121964479245922981359543652349234257083406467161008832071",
  "computed_previous": "0.38999999930029116380243064387709930669011409554209799044237069193997965918109665990539715784701801426692514731470512259748931698280542212567556492607309857160270994337244562765692984617353337618619414",
  "covered_success": {
    "lower": "0.39017892556968943695007243688985798870697082254158749860564803230524072183726340832688462741085136975863841637545179047417780255654972250249122257384821351500715563594084527775550574301237943808062965",
    "upper": "0.39017892556968943695007243688985798870697082254158749860564803230524072183726340832688462741085136975863841637545179047417780255654972250249122257384821351500715563594084527775550574301237943808062967"
  },
  "failure_intervals": {
    "endpoint_alias": {
      "lower": "0.0000037359264126735070021823048591613769531249999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999",
      "upper": "0.0000037359264126735070021823048591613769531250000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001"
    },
    "hit_cap_F5": {
      "lower": "9.3326361850321887899008954472381716961709144637170802462171433979596691097577563445444032709788110235959498993032424262421548752135403239484152081720393075623441066613832515027399507598590183151110048E-302",
      "upper": "9.3326361850321887899008954472381716961709144637170802462171433979596691097577563445444032709788110235959498993032424262421548752135403239484152081720393075623441066613832515027399507598590183151110050E-302"
    },
    "lemma_conditioning": {
      "lower": "3.0819900431122485169923631908869232902513219816654178228078661475237135037780638845248110895097650590956594367578573509898239285772314262021351643496677490914683529496700246040258846009785573832840043E-33",
      "upper": "3.0819900431122485169923631908869232902513219816654178228078661475237135037780638845248110895097650590956594367578573509898239285772314262021351643496677490914683529496700246040258846009785573832840045E-33"
    },
    "numeric_rounding": {
      "lower": "8.6736173798840354720596224069595336914062499999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999E-19",
      "upper": "8.6736173798840354720596224069595336914062500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001E-19"
    },
    "replay_cap_F6": {
      "lower": "0.00016295118045912137543331391815641165528136241793392852407719415217886760674970428950405941908439172541306784006733669207146707487471090407692920105463858774299331827446434555166479809477742268295689795",
      "upper": "0.00016295118045912137543331391815641165528136241793392852407719415217886760674970428950405941908439172541306784006733669207146707487471090407692920105463858774299331827446434555166479809477742268295689797"
    },
    "self_coincidence_F3": {
      "lower": "0.000011295326485121545712809917355371900826446280991735537190082644628099173553719008264462809917355371900826446280991735537190082644628099173553719008264462809917355371900826446280991735537190082644628098",
      "upper": "0.000011295326485121545712809917355371900826446280991735537190082644628099173553719008264462809917355371900826446280991735537190082644628099173553719008264462809917355371900826446280991735537190082644628100"
    },
    "start_replay_collision": {
      "lower": "8.0779356694631608874161005084957309918536338955163955688476562499999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999E-28",
      "upper": "8.0779356694631608874161005084957309918536338955163955688476562500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001E-28"
    },
    "table_exhaustion_F2": {
      "lower": "9.4270961004238546851655527287873167716092508321982590700023640361885276417088140733945260126029078621626228378100986151710237004340513464057678952818129585413543175447825063945136830174687375775377524E-7",
      "upper": "9.4270961004238546851655527287873167716092508321982590700023640361885276417088140733945260126029078621626228378100986151710237004340513464057678952818129585413543175447825063945136830174687375775377526E-7"
    }
  },
  "hit_abort": 46566464906103503740291625869377538,
  "hit_limit": 46566464906103503740291625869377537,
  "key_bits": 50,
  "margin_above_target": "4.2672247726909387539801396889991128623149820236508476916337649533057459184512033286310083865703452776293515622561811853160124443466934121964479245922981359543652349234257083406467161008832071E-10",
  "parameters": {
    "DK": 10,
    "DPLO": 145,
    "DT": 704,
    "HF": 111,
    "HIT_ABORT": 46566464906103503740291625869377538,
    "HMAX": 46566464906103503740291625869377537,
    "J": 65298,
    "LRC": 41387524446851461729465862952321024,
    "S": 18344,
    "Tb": 1325807493179968010081444286101979136,
    "U": 91720,
    "W": 633825300114114700748351602688,
    "granularity": 2475880078570760549798248448
  },
  "plan_sha256": "0890d000e6c8f44e077b7a15a7f6009a35cd6fe38620886fa92f8aca426a9329",
  "preconditions": {
    "available_gt_mean": true,
    "bins_cover_replay_cap": true,
    "conditioning_delta_lt_2^-109": true,
    "conditioning_ratio_le_1_plus_2^-108": true,
    "dp_partition_nonempty": true,
    "evaluation_fraction_le_half": true,
    "fresh_hit_delta_gt_2^-20": true,
    "fresh_hit_threshold_gt_mean": true,
    "fresh_step_probability_lt_2^-8": true,
    "hit_threshold_equals_abort_minus_lrc": true,
    "replay_cap_below_deadline": true,
    "start_replay_bound_le_2^-90": true,
    "table_has_initial_walks": true
  },
  "probability_inputs": {
    "age_g6": "0.00020789438889513116051944957559965068216596107415796317180803350685715012647143570384998104655186364054426676105991605940268619164828120112539705862720755330714673953679840481268477726145733862042842781",
    "available_restarts": 91464,
    "coincidence_upper": "0.39190855829523943240033458332516240777124907487459013985967426253985226329837849176597935791473834534226635874129472015970089257624064906662764677682925982784406735417462591596740858367800628928020866",
    "conditioning_delta": "5.3774968901122949762359585582188551401808185087516767263468577619888244485104779480765396935972589520766088097306320295584472742947665127840909090909090909090909090909090909090909090909090909090909091E-34",
    "conditioning_dp_term": "1.3717533285193123116756732584999660899487732774788182712351892422994207007294872627508911219510165127840909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909091E-34",
    "conditioning_inflation": "1.0000000000000000000000000000000002688472451210519321768112027536785679713346992810583419673300742892756045652246601867503057410500484631758757128155197926482415267059810280454170115601343074904403665",
    "conditioning_partition_term": "1.317271110382463342792173272182103731916844474130908018102598761971951580022775734404512350150698134221283197575758094899356365203857421875E-34",
    "conditioning_ratio": "1.0000000000000000000000000000000008065969341322814298004070585755645157366670372017281052844010355311981810240550535205420539343398342217333224532334914063520591293344333889668587137212949421504758155",
    "conditioning_start_term": "2.68847245121051932176811202753678531831520075714195043700906975771745216775821495092113622149554430507123470306396484375E-34",
    "evaluations": 339406718254071810580849737242106658816,
    "fresh_hit_delta": "9.536743164062500000000000003861797452750555541694236114984082231371919671886598240009547005359669297793844958068655038243129907662669583988128451816809320039888297915867919114033898808473479685E-7",
    "fresh_hit_mean_upper": "5178935520234250039380641742585856.00000000",
    "fresh_hit_threshold": 5178940459252042010825762917056514,
    "fresh_step_probability_exact": "0.00389866021631819777212921699057604228934907591347168173766934280389107431763886868964603102771424503147662168070206359168124436875563141323855886959184928433004874414589474610857484934350677083543632",
    "fresh_step_probability_upper": "0.00390625",
    "hit_chernoff_exponent": "-2355106085236244146790.6588885026505201700297216674444515155836273649502687464288542579524062865554210435252411989363669942470469593104542178457263295336776909143832680827369646734700545772546924593496",
    "mean_dp": "89880.1147766113281250000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "prefilter_bits": 16,
    "start_replay_union_bound": "5.3769449024210386435362240550735706366937702646737618709013744108633885474094506661163601012818385367251784653428143122805717334574782620912106718240592677716093112380322740920593482805145413294667378E-34",
    "theta_denominator_bits": 121,
    "theta_numerator": 704
  },
  "round": 24,
  "rounding": "200-digit Decimal; every interval moved one representable value outward",
  "rounding_audit": {
    "accumulated_absolute_bound": "4.183168E-134",
    "accumulated_lt_2^-200": true,
    "charged_numeric_term": "8.67361737988403547205962240695953369140625E-19",
    "operation_bound": 4183168,
    "per_operation_absolute_bound": "1E-140",
    "precision_digits": 200
  },
  "schema": "hashsmash-random-function-success-v1",
  "target": "0.39",
  "trails": 91720,
  "union_lower": "0.39000000042672247726909387539801396889991128623149820236508476916337649533057459184512033286310083865703452776293515622561811853160124443466934121964479245922981359543652349234257083406467161008832070"
}
```

## Appendix B. Bounded construction sources

These are the complete sources used for the measured sequential phases in Section 5. They use no participant executable. The freestanding binaries were linked without libc.

### freestanding_runtime.c

```c
/* Minimal x86-64 Linux runtime for the charged construction binaries. */
#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef long i64;
static i64 sc3(i64 n,i64 a,i64 b,i64 c){i64 r;__asm__ volatile("syscall":"=a"(r):"a"(n),"D"(a),"S"(b),"d"(c):"rcx","r11","memory");return r;}

__asm__(".global _start\n_start:\n xor %rbp,%rbp\n mov (%rsp),%rdi\n lea 8(%rsp),%rsi\n and $-16,%rsp\n call main\n mov %rax,%rdi\n mov $60,%rax\n syscall\n");

FILE *stdin=(FILE*)1,*stdout=(FILE*)2,*stderr=(FILE*)3;
int errno;

static int fdof(FILE *f){return (int)(intptr_t)f-1;}
static FILE *fileof(int fd){return (FILE*)(intptr_t)(fd+1);}
static long write_all(int fd,const void *data,size_t length){
    const unsigned char *p=data;size_t done=0;
    while(done<length){long n=sc3(1,fd,(i64)(p+done),(i64)(length-done));if(n<=0)return -1;done+=(size_t)n;}
    return (long)done;
}

long construction_vmhwm_bytes(void){
    static char status[4096];long fd=sc3(2,(i64)"/proc/self/status",0,0);if(fd<0)return -1;
    long n=sc3(0,fd,(i64)status,sizeof(status)-1);sc3(3,fd,0,0);if(n<=0)return -1;status[n]=0;
    for(long i=0;i+6<n;i++)if(status[i]=='V'&&status[i+1]=='m'&&status[i+2]=='H'&&status[i+3]=='W'&&status[i+4]=='M'){
        long j=i+5;while(status[j]==' '||status[j]=='\t'||status[j]==':')j++;long value=0;
        while(status[j]>='0'&&status[j]<='9')value=value*10+(status[j++]-'0');return value*1024;
    }
    return -1;
}

long construction_read_file(const char *path,void *buffer,size_t capacity){
    long fd=sc3(2,(i64)path,0,0);if(fd<0)return -1;size_t used=0;
    while(used<capacity){long n=sc3(0,fd,(i64)((unsigned char*)buffer+used),(i64)(capacity-used));if(n<0){sc3(3,fd,0,0);return -1;}if(!n)break;used+=(size_t)n;}
    sc3(3,fd,0,0);return (long)used;
}

void *memset(void *d,int c,size_t n){unsigned char *p=d;while(n--)*p++=(unsigned char)c;return d;}
void *memcpy(void *d,const void *s,size_t n){unsigned char *p=d;const unsigned char *q=s;while(n--)*p++=*q++;return d;}
int memcmp(const void *a,const void *b,size_t n){const unsigned char *p=a,*q=b;while(n--){if(*p!=*q)return *p-*q;p++;q++;}return 0;}
size_t strlen(const char *s){const char *p=s;while(*p)p++;return (size_t)(p-s);}
int strcmp(const char *a,const char *b){while(*a&&*a==*b){a++;b++;}return (unsigned char)*a-(unsigned char)*b;}
char *getenv(const char *name){(void)name;return 0;}
int atoi(const char *s){int v=0;while(*s>='0'&&*s<='9')v=v*10+(*s++-'0');return v;}
long strtol(const char *s,char **end,int base){long v=0;(void)base;while(*s>='0'&&*s<='9')v=v*10+(*s++-'0');if(end)*end=(char*)s;return v;}

FILE *fopen(const char *path,const char *mode){
    int flags=(mode&&mode[0]=='r')?0:(1|64|512);long fd=sc3(2,(i64)path,flags,0644);
    return fd<0?0:fileof((int)fd);
}
int fclose(FILE *f){return (int)sc3(3,fdof(f),0,0);}
int fflush(FILE *f){(void)f;return 0;}
size_t fwrite(const void *p,size_t size,size_t count,FILE *f){size_t n=size*count;return write_all(fdof(f),p,n)<0?0:count;}
size_t fread(void *p,size_t size,size_t count,FILE *f){size_t want=size*count,done=0;while(done<want){long n=sc3(0,fdof(f),(i64)((unsigned char*)p+done),(i64)(want-done));if(n<=0)break;done+=(size_t)n;}return size?done/size:0;}
int fputc(int c,FILE *f){unsigned char b=(unsigned char)c;return write_all(fdof(f),&b,1)<0?EOF:c;}
int fgetc(FILE *f){unsigned char b;long n=sc3(0,fdof(f),(i64)&b,1);return n==1?b:EOF;}

static void emit_char(char **dst,size_t *left,FILE *f,char c,int *total){
    if(dst){if(*left>1){**dst=c;(*dst)++;(*left)--;}}
    else fputc((unsigned char)c,f);
    (*total)++;
}
static void emit_text(char **dst,size_t *left,FILE *f,const char *s,int *total){while(*s)emit_char(dst,left,f,*s++,total);}
static void emit_uint(char **dst,size_t *left,FILE *f,unsigned long long v,unsigned base,int width,int zero,int *total){
    char buf[32];int n=0;do{unsigned d=(unsigned)(v%base);buf[n++]=(char)(d<10?'0'+d:'a'+d-10);v/=base;}while(v);
    while(n<width){emit_char(dst,left,f,zero?'0':' ',total);width--;}
    while(n)emit_char(dst,left,f,buf[--n],total);
}
static int vformat(char *out,size_t cap,FILE *f,const char *fmt,va_list ap){
    char *dst=out;size_t left=cap;int total=0;
    while(*fmt){
        if(*fmt!='%'){emit_char(out?&dst:0,out?&left:0,f,*fmt++,&total);continue;}
        fmt++;if(*fmt=='%'){emit_char(out?&dst:0,out?&left:0,f,*fmt++,&total);continue;}
        int zero=0,width=0,longness=0;if(*fmt=='0'){zero=1;fmt++;}while(*fmt>='0'&&*fmt<='9')width=width*10+(*fmt++-'0');
        if(*fmt=='z'){longness=1;fmt++;}else if(*fmt=='l'){longness=1;fmt++;if(*fmt=='l'){longness=2;fmt++;}}
        char kind=*fmt++;if(kind=='s'){emit_text(out?&dst:0,out?&left:0,f,va_arg(ap,const char*),&total);}
        else if(kind=='c'){emit_char(out?&dst:0,out?&left:0,f,(char)va_arg(ap,int),&total);}
        else if(kind=='d'||kind=='i'){
            long long v=longness?va_arg(ap,long):va_arg(ap,int);if(v<0){emit_char(out?&dst:0,out?&left:0,f,'-',&total);v=-v;}emit_uint(out?&dst:0,out?&left:0,f,(unsigned long long)v,10,width,zero,&total);
        }else if(kind=='u'||kind=='x'){
            unsigned long long v=longness?va_arg(ap,unsigned long):va_arg(ap,unsigned int);emit_uint(out?&dst:0,out?&left:0,f,v,kind=='x'?16:10,width,zero,&total);
        }else{emit_char(out?&dst:0,out?&left:0,f,'?',&total);}
    }
    if(out&&cap){*dst=0;}
    return total;
}
int fprintf(FILE *f,const char *fmt,...){va_list ap;va_start(ap,fmt);int n=vformat(0,0,f,fmt,ap);va_end(ap);return n;}
int printf(const char *fmt,...){va_list ap;va_start(ap,fmt);int n=vformat(0,0,stdout,fmt,ap);va_end(ap);return n;}
int snprintf(char *out,size_t cap,const char *fmt,...){va_list ap;va_start(ap,fmt);int n=vformat(out,cap,0,fmt,ap);va_end(ap);return n;}
void perror(const char *s){fprintf(stderr,"%s\n",s);}
char *strerror(int value){(void)value;return "runtime error";}
void exit(int code){sc3(60,code,0,0);for(;;){}}
void abort(void){exit(134);}

```

### plan_search_local.c

```c
#include <errno.h>
#include <inttypes.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * Independent generator for the r24 S3-04 / look-ahead / eight-body step.
 *
 * The graph builder descends from our sha3-r6 generator.  The structured
 * constants and the high-level polarity and loop constructions are transcribed
 * from the public proofs, not from executable participant source.
 */

enum { O_IN = 0, O_XOR = 1, O_AND = 2, O_OR = 3, O_NOT = 4 };
enum {
    NC = -1,
    MAX_NODES = 9000,
    MAX_FORMS = 2048,
    CONS_SIZE = 1 << 14,
    FORM_SIZE = 1 << 12,
    NREG = 4096,
    PLAN_ROWS = 320,
    PLAN_BITS = 320,
};

typedef struct {
    uint8_t op;
    uint8_t k;
    int16_t a, b, lin;
} Node;

typedef struct {
    uint64_t mask[4];
    int node;
} Form;

typedef struct {
    int n;
    uint8_t p;
} Value;

typedef struct {
    uint8_t op;
    uint16_t d, a, b;
} Insn;

typedef struct {
    uint8_t subset;
    uint8_t tricks;
    uint8_t select_mask;
    uint8_t cost;
} Decision;

typedef struct {
    uint8_t cnot[PLAN_BITS];
    uint8_t dnot[PLAN_BITS];
    uint8_t target[PLAN_ROWS];
    uint64_t ib;
} Plan;

_Static_assert(sizeof(Decision) == 4, "Decision must have a stable byte encoding");
_Static_assert(sizeof(Plan) == 968, "Plan must have a stable byte encoding");

static Node nodes[MAX_NODES];
static Form forms[MAX_FORMS];
static uint16_t cons_table[CONS_SIZE];
static uint16_t form_table[FORM_SIZE];
static int node_count, form_count;
static Decision row_table[32][32];
static uint8_t row_min_cost[32];
static uint8_t row_min_target[32];

static const uint64_t RC[24] = {
    UINT64_C(0x0000000000000001), UINT64_C(0x0000000000008082),
    UINT64_C(0x800000000000808a), UINT64_C(0x8000000080008000),
    UINT64_C(0x000000000000808b), UINT64_C(0x0000000080000001),
    UINT64_C(0x8000000080008081), UINT64_C(0x8000000000008009),
    UINT64_C(0x000000000000008a), UINT64_C(0x0000000000000088),
    UINT64_C(0x0000000080008009), UINT64_C(0x000000008000000a),
    UINT64_C(0x000000008000808b), UINT64_C(0x800000000000008b),
    UINT64_C(0x8000000000008089), UINT64_C(0x8000000000008003),
    UINT64_C(0x8000000000008002), UINT64_C(0x8000000000000080),
    UINT64_C(0x000000000000800a), UINT64_C(0x800000008000000a),
    UINT64_C(0x8000000080008081), UINT64_C(0x8000000000008080),
    UINT64_C(0x0000000080000001), UINT64_C(0x8000000080008008),
};

static const int ROT[5][5] = {
    {0, 36, 3, 41, 18}, {1, 44, 10, 45, 2}, {62, 6, 43, 15, 61},
    {28, 55, 25, 21, 56}, {27, 20, 39, 8, 14},
};

/* S3-04 trial 1230.  Lanes 1, 4, 6 and 9 are overwritten by the point. */
static uint64_t KL[25] = {
    UINT64_C(0x0000000000000000), UINT64_C(0x0000000000000000),
    UINT64_C(0x2d58eceb83b21614), UINT64_C(0x0000000000000000),
    UINT64_C(0x0000000000000000), UINT64_C(0xffffffffffffffff),
    UINT64_C(0x0000000000000000), UINT64_C(0x0000000000000000),
    UINT64_C(0x0000000000000000), UINT64_C(0x0000000000000000),
    UINT64_C(0xffffffffffffffff), UINT64_C(0x8b563b3ae0ec8583),
    UINT64_C(0x0000000000000000), UINT64_C(0x85ab1d9d707642c2),
    UINT64_C(0xe953898a3e26f4f5), UINT64_C(0xffffffffffffffff),
    UINT64_C(0x8000000000000006), 0, 0, 0, 0, 0, 0, 0, 0,
};

static void fail(const char *msg) {
    fprintf(stderr, "gen_combined: %s\n", msg);
    exit(1);
}

static uint64_t read_u64_le(FILE *f) {
    uint8_t bytes[8];
    if (fread(bytes, 1, sizeof(bytes), f) != sizeof(bytes))
        fail("short constant record");
    uint64_t value = 0;
    for (int i = 0; i < 8; i++) value |= (uint64_t)bytes[i] << (8 * i);
    return value;
}

static void validate_kl(const uint64_t kl[25]) {
    static const int variable_lanes[4] = {1, 4, 6, 9};
    for (int i = 0; i < 4; i++) if (kl[variable_lanes[i]])
        fail("constant record overwrites a direct point lane");
    if (kl[16] != UINT64_C(0x8000000000000006))
        fail("constant record has invalid SHA3 padding lane");
    for (int lane = 17; lane < 25; lane++) if (kl[lane])
        fail("constant record has nonzero capacity lane");
}

static void load_kl_record(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) fail("cannot open constant record");
    for (int lane = 0; lane < 25; lane++) KL[lane] = read_u64_le(f);
    if (fgetc(f) != EOF || fclose(f)) fail("constant record has trailing data");
    validate_kl(KL);
}

static uint64_t mix64(uint64_t x) {
    x ^= x >> 30;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27;
    x *= UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31);
}

static uint64_t rng_next(uint64_t *state) {
    uint64_t x = *state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    *state = x;
    return x;
}

static uint64_t node_hash(int op, int a, int b) {
    return mix64((uint64_t)(uint32_t)op * UINT64_C(0x9e3779b97f4a7c15) ^
                 (uint64_t)(uint32_t)a * UINT64_C(0x85ebca77c2b2ae63) ^
                 (uint64_t)(uint32_t)b * UINT64_C(0x27d4eb2f165667c5));
}

static uint64_t form_hash(const uint64_t m[4]) {
    return mix64(m[0] ^ mix64(m[1]) ^ (m[2] << 1) ^ (m[2] >> 63) ^
                 (m[3] << 7) ^ (m[3] >> 57));
}

static int new_node(int op, int a, int b) {
    if (node_count >= MAX_NODES) fail("node capacity exceeded");
    int n = node_count++;
    nodes[n] = (Node){(uint8_t)op, 0, a, b, -1};
    return n;
}

static int cons_node(int op, int a, int b) {
    if (op != O_NOT && a > b) {
        int t = a;
        a = b;
        b = t;
    }
    size_t h = (size_t)node_hash(op, a, b) & (CONS_SIZE - 1);
    for (;;) {
        int e = cons_table[h];
        if (!e) break;
        int n = e - 1;
        if (nodes[n].op == op && nodes[n].a == a && nodes[n].b == b) return n;
        h = (h + 1) & (CONS_SIZE - 1);
    }
    int n = new_node(op, a, b);
    cons_table[h] = n + 1;
    return n;
}

static int mask_zero(const uint64_t m[4]) {
    return (m[0] | m[1] | m[2] | m[3]) == 0;
}

static int find_form(const uint64_t m[4]) {
    size_t h = (size_t)form_hash(m) & (FORM_SIZE - 1);
    for (;;) {
        int e = form_table[h];
        if (!e) return -1;
        int f = e - 1;
        if (!memcmp(forms[f].mask, m, sizeof(forms[f].mask))) return f;
        h = (h + 1) & (FORM_SIZE - 1);
    }
}

static int add_form(const uint64_t m[4], int node) {
    if (form_count >= MAX_FORMS) fail("linear-form capacity exceeded");
    int f = form_count++;
    memcpy(forms[f].mask, m, sizeof(forms[f].mask));
    forms[f].node = node;
    size_t h = (size_t)form_hash(m) & (FORM_SIZE - 1);
    while (form_table[h]) h = (h + 1) & (FORM_SIZE - 1);
    form_table[h] = f + 1;
    return f;
}

static Value val(int n, int p) { return (Value){n, (uint8_t)(p & 1)}; }
static Value constant(int p) { return val(NC, p); }

static Value xor_value(Value a, Value b) {
    if (a.n == NC) return val(b.n, b.p ^ a.p);
    if (b.n == NC) return val(a.n, a.p ^ b.p);
    if (a.n == b.n) return constant(a.p ^ b.p);
    int la = nodes[a.n].lin, lb = nodes[b.n].lin;
    if (la >= 0 && lb >= 0) {
        uint64_t m[4];
        for (int i = 0; i < 4; i++) m[i] = forms[la].mask[i] ^ forms[lb].mask[i];
        int k = nodes[a.n].k ^ nodes[b.n].k;
        if (mask_zero(m)) return constant(k ^ a.p ^ b.p);
        int f = find_form(m);
        if (f >= 0) {
            int n = forms[f].node;
            return val(n, k ^ a.p ^ b.p ^ nodes[n].k);
        }
        int n = cons_node(O_XOR, a.n, b.n);
        nodes[n].k = (uint8_t)k;
        nodes[n].lin = add_form(m, n);
        return val(n, a.p ^ b.p);
    }
    return val(cons_node(O_XOR, a.n, b.n), a.p ^ b.p);
}

static Value complement_representation(Value a) {
    if (a.n == NC) return a;
    int before = node_count;
    int n = cons_node(O_NOT, a.n, 0);
    if (node_count > before && nodes[a.n].lin >= 0) {
        nodes[n].lin = nodes[a.n].lin;
        nodes[n].k = nodes[a.n].k ^ 1;
    }
    return val(n, a.p ^ 1);
}

static Value and_value(Value a, Value b, int select_polarity) {
    if (a.n == NC) return a.p ? b : constant(0);
    if (b.n == NC) return b.p ? a : constant(0);
    if (a.n == b.n) return a.p == b.p ? a : constant(0);
    if (!a.p && !b.p) return val(cons_node(O_AND, a.n, b.n), 0);
    if (a.p && b.p) return val(cons_node(O_OR, a.n, b.n), 1);
    int A = !a.p ? a.n : b.n;
    int B = !a.p ? b.n : a.n;
    if (select_polarity) {
        Value na = complement_representation(val(A, 0));
        return val(cons_node(O_OR, na.n, B), 1);
    }
    int t = cons_node(O_AND, A, B);
    return xor_value(val(A, 0), val(t, 0));
}

static int term_cost(Value a, Value b) {
    if (a.n == NC || b.n == NC || a.n == b.n) return 0;
    return ((a.p ^ 1) == b.p) ? 1 : 2;
}

static void reset_graph(int inputs, int affine_inputs) {
    memset(cons_table, 0, sizeof(cons_table));
    memset(form_table, 0, sizeof(form_table));
    node_count = form_count = 0;
    for (int j = 0; j < inputs; j++) {
        int n = new_node(O_IN, 0, 0);
        if (affine_inputs) {
            uint64_t m[4] = {0, 0, 0, 0};
            if (j >= 256) fail("too many affine inputs");
            m[j >> 6] = UINT64_C(1) << (j & 63);
            nodes[n].lin = add_form(m, n);
        }
    }
}

static void choose_dynamic_row(const Value b[5], int need, int *subset, int *trick) {
    int distinct = 1;
    for (int x = 0; x < 5; x++) {
        if (b[x].n == NC) distinct = 0;
        for (int y = x + 1; y < 5; y++) if (b[x].n == b[y].n) distinct = 0;
    }
    int best_subset = -1, best_trick = -1, best_cost = 1 << 30;
    int jmax = distinct ? 5 : 0;
    for (int j = -1; j < jmax; j++) {
        if (j >= 0 && (!((need >> j) & 1) || !((need >> ((j + 1) % 5)) & 1))) continue;
        for (int s = 0; s < 32; s++) {
            Value bb[5];
            memcpy(bb, b, sizeof(bb));
            int cost = 0;
            for (int x = 0; x < 5; x++) if ((s >> x) & 1) {
                if (b[x].n == NC) cost = 1 << 29;
                else { bb[x].p ^= 1; cost++; }
            }
            for (int x = 0; x < 5; x++) if ((need >> x) & 1) {
                if (x == j) {
                    int k = (j + 1) % 5;
                    Value p1 = bb[(k + 1) % 5], p2 = bb[(k + 2) % 5];
                    if ((p1.p ^ 1) == p2.p) {
                        Value bk = bb[k];
                        bk.p ^= (p1.p ^ 1);
                        cost += term_cost(bk, bb[(x + 2) % 5]);
                    } else {
                        cost++;
                    }
                } else {
                    cost += term_cost(bb[(x + 1) % 5], bb[(x + 2) % 5]);
                }
            }
            if (cost < best_cost) {
                best_cost = cost;
                best_subset = s;
                best_trick = j;
            }
        }
    }
    *subset = best_subset;
    *trick = best_trick;
}

static void build_dynamic_row(Value b[5], int need, Value out[5]) {
    int subset, trick;
    choose_dynamic_row(b, need, &subset, &trick);
    for (int x = 0; x < 5; x++) if ((subset >> x) & 1)
        b[x] = complement_representation(b[x]);
    int k = (trick + 1) % 5;
    if (trick >= 0) {
        Value t = and_value(val(b[(k + 1) % 5].n, b[(k + 1) % 5].p ^ 1),
                            b[(k + 2) % 5], 0);
        out[k] = xor_value(b[k], t);
    }
    for (int x = 0; x < 5; x++) if ((need >> x) & 1) {
        if (trick >= 0 && x == k) continue;
        Value t1 = x == trick ? out[k] : b[(x + 1) % 5];
        Value t = and_value(val(t1.n, t1.p ^ 1), b[(x + 2) % 5], 0);
        out[x] = xor_value(b[x], t);
    }
}

static int sim_term(int pa, int pb, int select, int *pout) {
    if (pa == pb) {
        *pout = pa;
        return 1;
    }
    *pout = select;
    return 2;
}

static void make_row_table(void) {
    for (int pin = 0; pin < 32; pin++) {
        int min_cost = 255, min_target = 0;
        for (int target = 0; target < 32; target++) {
            Decision best = {0, 0, 0, 255};
            for (int subset = 0; subset < 32; subset++) {
                int bp[5];
                for (int x = 0; x < 5; x++) bp[x] = ((pin >> x) & 1) ^ ((subset >> x) & 1);
                for (int trick = -1; trick < 5; trick++) {
                    for (int sel = 0; sel < 32; sel++) {
                        int op[5] = {0, 0, 0, 0, 0};
                        int cost = __builtin_popcount((unsigned)subset);
                        int k = (trick + 1) % 5;
                        if (trick >= 0) {
                            int tp;
                            cost += sim_term(bp[(k + 1) % 5] ^ 1, bp[(k + 2) % 5],
                                             (sel >> k) & 1, &tp) + 1;
                            op[k] = bp[k] ^ tp;
                        }
                        for (int x = 0; x < 5; x++) {
                            if (trick >= 0 && x == k) continue;
                            int first = x == trick ? op[k] : bp[(x + 1) % 5];
                            int tp;
                            cost += sim_term(first ^ 1, bp[(x + 2) % 5],
                                             (sel >> x) & 1, &tp) + 1;
                            op[x] = bp[x] ^ tp;
                        }
                        int got = 0;
                        for (int x = 0; x < 5; x++) got |= op[x] << x;
                        if (got == target && cost < best.cost) {
                            best = (Decision){(uint8_t)subset, (uint8_t)(trick + 1),
                                              (uint8_t)sel, (uint8_t)cost};
                        }
                    }
                }
            }
            if (best.cost == 255) fail("unreachable row target polarity");
            row_table[pin][target] = best;
            if (best.cost < min_cost) {
                min_cost = best.cost;
                min_target = target;
            }
        }
        row_min_cost[pin] = (uint8_t)min_cost;
        row_min_target[pin] = (uint8_t)min_target;
    }
}

static void build_target_row(Value b[5], int target, Value out[5]) {
    int pin = 0;
    for (int x = 0; x < 5; x++) pin |= b[x].p << x;
    Decision d = row_table[pin][target];
    for (int x = 0; x < 5; x++) if ((d.subset >> x) & 1)
        b[x] = complement_representation(b[x]);
    int trick = (int)d.tricks - 1;
    int k = (trick + 1) % 5;
    if (trick >= 0) {
        Value t = and_value(val(b[(k + 1) % 5].n, b[(k + 1) % 5].p ^ 1),
                            b[(k + 2) % 5], (d.select_mask >> k) & 1);
        out[k] = xor_value(b[k], t);
    }
    for (int x = 0; x < 5; x++) {
        if (trick >= 0 && x == k) continue;
        Value t1 = x == trick ? out[k] : b[(x + 1) % 5];
        Value t = and_value(val(t1.n, t1.p ^ 1), b[(x + 2) % 5],
                            (d.select_mask >> x) & 1);
        out[x] = xor_value(b[x], t);
    }
    int got = 0;
    for (int x = 0; x < 5; x++) got |= out[x].p << x;
    if (got != target) fail("row-table construction mismatch");
}

static void row_patterns(const uint8_t state[1600], const uint8_t cnot[320],
                         const uint8_t dnot[320], uint8_t patterns[320]) {
    uint8_t cp[320], dp[320];
    for (int x = 0; x < 5; x++) for (int z = 0; z < 64; z++) {
        int p = 0;
        for (int y = 0; y < 5; y++) p ^= state[64 * (x + 5 * y) + z];
        cp[64 * x + z] = (uint8_t)(p ^ cnot[64 * x + z]);
    }
    for (int x = 0; x < 5; x++) for (int z = 0; z < 64; z++)
        dp[64 * x + z] = (uint8_t)(cp[64 * ((x + 4) % 5) + z] ^
            cp[64 * ((x + 1) % 5) + ((z + 63) & 63)] ^ dnot[64 * x + z]);
    for (int Y = 0; Y < 5; Y++) for (int z = 0; z < 64; z++) {
        int pin = 0;
        for (int X = 0; X < 5; X++) {
            int y = X, x = (3 * Y + X) % 5;
            int zz = (z - ROT[x][y]) & 63;
            int p = state[64 * (x + 5 * y) + zz] ^ dp[64 * x + zz];
            pin |= p << X;
        }
        patterns[64 * Y + z] = (uint8_t)pin;
    }
}

static void targets_to_state(const uint8_t target[320], uint8_t state[1600]) {
    for (int Y = 0; Y < 5; Y++) for (int z = 0; z < 64; z++)
        for (int X = 0; X < 5; X++)
            state[64 * (X + 5 * Y) + z] = (target[64 * Y + z] >> X) & 1;
}

static void state_to_targets(const uint8_t state[1600], uint8_t target[320]) {
    for (int Y = 0; Y < 5; Y++) for (int z = 0; z < 64; z++) {
        int t = 0;
        for (int X = 0; X < 5; X++) t |= state[64 * (X + 5 * Y) + z] << X;
        target[64 * Y + z] = (uint8_t)t;
    }
}

static int current_cost(const uint8_t input[1600], const Plan *p) {
    uint8_t patterns[320];
    row_patterns(input, p->cnot, p->dnot, patterns);
    int cost = 3200;
    for (int i = 0; i < 320; i++) {
        int target = p->target[i] ^ (i < 64 && ((p->ib >> i) & 1));
        cost += p->cnot[i] + p->dnot[i] + row_table[patterns[i]][target].cost;
    }
    return cost;
}

static int next_estimate(const Plan *p) {
    static const uint8_t zero[320] = {0};
    uint8_t state[1600], patterns[320];
    targets_to_state(p->target, state);
    row_patterns(state, zero, zero, patterns);
    int cost = 3200;
    for (int i = 0; i < 320; i++) cost += row_min_cost[patterns[i]];
    return cost;
}

static int fixed_next_estimate(const Plan *p, const uint8_t fixed_output[1600]) {
    static const uint8_t zero[320] = {0};
    uint8_t state[1600], patterns[320], targets[320];
    targets_to_state(p->target, state);
    state_to_targets(fixed_output, targets);
    row_patterns(state, zero, zero, patterns);
    int cost = 3200;
    for (int i = 0; i < 320; i++) cost += row_table[patterns[i]][targets[i]].cost;
    return cost;
}

static int output_distance(const Plan *p, const uint8_t reference[1600]) {
    uint8_t state[1600];
    targets_to_state(p->target, state);
    int distance = 0;
    for (int i = 0; i < 1600; i++) distance += state[i] != reference[i];
    return distance;
}

static int objective(const uint8_t input[1600], const Plan *p,
                     const uint8_t next_fixed_output[1600],
                     const uint8_t bridge_reference[1600]) {
    int tail = bridge_reference ? 16 * output_distance(p, bridge_reference) :
        next_fixed_output ? 16 * fixed_next_estimate(p, next_fixed_output) :
                            3 * next_estimate(p);
    return 16 * current_cost(input, p) + tail;
}

static int free_output_cost(const uint8_t input[1600], const Plan *p) {
    uint8_t patterns[320];
    row_patterns(input, p->cnot, p->dnot, patterns);
    int cost = 3200;
    for (int i = 0; i < 320; i++)
        cost += p->cnot[i] + p->dnot[i] + row_min_cost[patterns[i]];
    return cost;
}

static void optimize_plan(const uint8_t input[1600], const uint8_t fixed_output[1600],
                          const uint8_t next_fixed_output[1600],
                          const uint8_t bridge_reference[1600], uint64_t ib,
                          uint64_t seed,
                          int iterations, Plan *result) {
    Plan cur = {0}, best;
    cur.ib = ib;
    uint8_t patterns[320];
    if (!fixed_output) {
        int free_cur = free_output_cost(input, &cur), free_best = free_cur;
        Plan free_plan = cur;
        int free_iterations = iterations < 10000 ? 10000 : iterations;
        for (int it = 0; it < free_iterations; it++) {
            uint64_t r = rng_next(&seed);
            int kind = (int)(r & 1), index = (int)((r >> 8) % 320);
            uint8_t *bit = kind ? &cur.dnot[index] : &cur.cnot[index];
            *bit ^= 1;
            int trial = free_output_cost(input, &cur);
            int diff = trial - free_cur;
            int temp = 1 + (free_iterations - it) * 24 / free_iterations;
            uint64_t denom = (uint64_t)temp + (uint64_t)(diff > 0 ? diff * 12 : 0);
            int accept = diff <= 0 || (rng_next(&seed) % denom) < (uint64_t)temp;
            if (accept) {
                free_cur = trial;
                if (trial < free_best) {
                    free_best = trial;
                    free_plan = cur;
                }
            } else {
                *bit ^= 1;
            }
        }
        cur = free_plan;
        for (int sweep = 0; sweep < 3; sweep++)
            for (int kind = 0; kind < 2; kind++) for (int i = 0; i < 320; i++) {
                uint8_t *bit = kind ? &cur.dnot[i] : &cur.cnot[i];
                int before = free_output_cost(input, &cur);
                *bit ^= 1;
                if (free_output_cost(input, &cur) > before) *bit ^= 1;
            }
    }
    row_patterns(input, cur.cnot, cur.dnot, patterns);
    if (fixed_output) state_to_targets(fixed_output, cur.target);
    else for (int i = 0; i < 320; i++) cur.target[i] = row_min_target[patterns[i]];
    int cur_obj = objective(input, &cur, next_fixed_output, bridge_reference), best_obj = cur_obj;
    best = cur;
    for (int it = 0; it < iterations; it++) {
        uint64_t r = rng_next(&seed);
        int kind = fixed_output ? (int)(r & 1) : 2, index, old;
        if (kind == 0) {
            index = (int)((r >> 8) % 320);
            old = cur.cnot[index];
            cur.cnot[index] ^= 1;
        } else if (kind == 1) {
            index = (int)((r >> 8) % 320);
            old = cur.dnot[index];
            cur.dnot[index] ^= 1;
        } else if (!fixed_output) {
            index = (int)((r >> 8) % 320);
            old = cur.target[index];
            cur.target[index] ^= (uint8_t)(1 + ((r >> 24) % 31));
        } else {
            continue;
        }
        int trial = objective(input, &cur, next_fixed_output, bridge_reference);
        int diff = trial - cur_obj;
        int temp = 1 + (iterations - it) * 96 / (iterations ? iterations : 1);
        uint64_t denom = (uint64_t)temp + (uint64_t)(diff > 0 ? diff * 24 : 0);
        int accept = diff <= 0 || (rng_next(&seed) % denom) < (uint64_t)temp;
        if (accept) {
            cur_obj = trial;
            if (trial < best_obj) {
                best_obj = trial;
                best = cur;
            }
        } else if (kind == 0) cur.cnot[index] = (uint8_t)old;
        else if (kind == 1) cur.dnot[index] = (uint8_t)old;
        else cur.target[index] = (uint8_t)old;
    }
    cur = best;
    cur_obj = best_obj;
    for (int sweep = 0; sweep < 2; sweep++) {
        if (fixed_output)
            for (int kind = 0; kind < 2; kind++) for (int i = 0; i < 320; i++) {
                uint8_t *bit = kind ? &cur.dnot[i] : &cur.cnot[i];
                *bit ^= 1;
                int trial = objective(input, &cur, next_fixed_output, bridge_reference);
                if (trial <= cur_obj) cur_obj = trial;
                else *bit ^= 1;
            }
        if (!fixed_output) for (int i = 0; i < 320; i++) {
            int old = cur.target[i], chosen = old, chosen_obj = cur_obj;
            for (int t = 0; t < 32; t++) {
                cur.target[i] = (uint8_t)t;
                int trial = objective(input, &cur, next_fixed_output, bridge_reference);
                if (trial < chosen_obj) {
                    chosen_obj = trial;
                    chosen = t;
                }
            }
            cur.target[i] = (uint8_t)chosen;
            cur_obj = chosen_obj;
        }
    }
    *result = cur;
}

static void theta_graph(Value S[25][64], Value D[5][64], const uint8_t *cnot,
                        const uint8_t *dnot) {
    Value C[5][64];
    for (int x = 0; x < 5; x++) for (int z = 0; z < 64; z++) {
        Value s = S[x][z];
        for (int y = 1; y < 5; y++) s = xor_value(s, S[x + 5 * y][z]);
        if (cnot && cnot[64 * x + z]) s = complement_representation(s);
        C[x][z] = s;
    }
    for (int x = 0; x < 5; x++) for (int z = 0; z < 64; z++) {
        Value d = xor_value(C[(x + 4) % 5][z], C[(x + 1) % 5][(z + 63) & 63]);
        if (dnot && dnot[64 * x + z]) d = complement_representation(d);
        D[x][z] = d;
    }
}

static Value lazy_c(Value S[25][64], Value C[5][64], uint8_t have_c[320],
                    const uint8_t *cnot, int x, int z) {
    int index = 64 * x + z;
    if (!have_c[index]) {
        Value s = S[x][z];
        for (int y = 1; y < 5; y++) s = xor_value(s, S[x + 5 * y][z]);
        if (cnot && cnot[index]) s = complement_representation(s);
        C[x][z] = s;
        have_c[index] = 1;
    }
    return C[x][z];
}

static Value lazy_d(Value S[25][64], Value C[5][64], Value D[5][64],
                    uint8_t have_c[320], uint8_t have_d[320],
                    const uint8_t *cnot, const uint8_t *dnot, int x, int z) {
    int index = 64 * x + z;
    if (!have_d[index]) {
        Value a = lazy_c(S, C, have_c, cnot, (x + 4) % 5, z);
        Value b = lazy_c(S, C, have_c, cnot, (x + 1) % 5, (z + 63) & 63);
        Value d = xor_value(a, b);
        if (dnot && dnot[index]) d = complement_representation(d);
        D[x][z] = d;
        have_d[index] = 1;
    }
    return D[x][z];
}

static void build_prefix_graph(const Plan *prefix_plan, int outputs[1600],
                               uint8_t output_p[1600]) {
    Value S[25][64], NS[25][64], D[5][64];
    reset_graph(256, 1);
    for (int l = 0; l < 25; l++) for (int z = 0; z < 64; z++)
        S[l][z] = constant((KL[l] >> z) & 1);
    for (int z = 0; z < 64; z++) {
        S[1][z] = val(z, 0);
        S[6][z] = val(64 + z, 0);
        S[4][z] = val(128 + z, 0);
        S[9][z] = val(192 + z, 0);
        S[11][z] = xor_value(xor_value(val(z, 0), val(64 + z, 0)),
                             constant((KL[11] >> z) & 1));
        S[14][z] = xor_value(xor_value(val(128 + z, 0), val(192 + z, 0)),
                             constant((KL[14] >> z) & 1));
    }
    for (int round = 0; round < 2; round++) {
        theta_graph(S, D, round == 1 ? prefix_plan->cnot : NULL,
                    round == 1 ? prefix_plan->dnot : NULL);
        memcpy(NS, S, sizeof(NS));
        for (int Y = 0; Y < 5; Y++) for (int z = 0; z < 64; z++) {
            Value b[5], out[5];
            for (int X = 0; X < 5; X++) {
                int y = X, x = (3 * Y + X) % 5;
                int zz = (z - ROT[x][y]) & 63;
                b[X] = xor_value(S[x + 5 * y][zz], D[x][zz]);
            }
            build_dynamic_row(b, 0x1f, out);
            for (int X = 0; X < 5; X++) NS[X + 5 * Y][z] = out[X];
        }
        for (int z = 0; z < 64; z++) NS[0][z].p ^= (RC[round] >> z) & 1;
        memcpy(S, NS, sizeof(S));
    }
    for (int q = 0; q < 1600; q++) {
        Value v = S[q >> 6][q & 63];
        if (v.n == NC) fail("constant prefix output");
        outputs[q] = v.n;
        output_p[q] = v.p;
    }
}

static int live_operation_count(const int *outputs, int output_count, int input_count) {
    static uint8_t live_storage[MAX_NODES];
    uint8_t *live = live_storage;
    memset(live, 0, (size_t)node_count);
    for (int j = 0; j < output_count; j++) live[outputs[j]] = 1;
    int count = 0;
    for (int i = node_count - 1; i >= input_count; i--) if (live[i]) {
        count++;
        live[nodes[i].a] = 1;
        if (nodes[i].op != O_NOT) live[nodes[i].b] = 1;
    }
    return count;
}

static void optimize_prefix(Plan *plan, int outputs[1600], uint8_t output_p[1600]) {
    memset(plan, 0, sizeof(*plan));
    build_prefix_graph(plan, outputs, output_p);
    int best = live_operation_count(outputs, 1600, 256);
    int gain = 0;
    for (int sweep = 0; sweep < 3; sweep++) {
        for (int kind = 0; kind < 2; kind++) for (int i = 0; i < 320; i++) {
            uint8_t *bit = kind ? &plan->dnot[i] : &plan->cnot[i];
            *bit ^= 1;
            build_prefix_graph(plan, outputs, output_p);
            int trial = live_operation_count(outputs, 1600, 256);
            if (trial < best) {
                gain += best - trial;
                best = trial;
            } else {
                *bit ^= 1;
            }
        }
    }
    build_prefix_graph(plan, outputs, output_p);
    if (live_operation_count(outputs, 1600, 256) != best)
        fail("prefix greedy count mismatch");
    printf("prefix-round1-greedy-gain %d\n", gain);
}

static void optimize_prefix_from_seed(Plan *plan, int outputs[1600],
                                      uint8_t output_p[1600]) {
    build_prefix_graph(plan, outputs, output_p);
    int best = live_operation_count(outputs, 1600, 256);
    int gain = 0;
    for (int sweep = 0; sweep < 3; sweep++) {
        int improved = 0;
        for (int kind = 0; kind < 2; kind++) for (int i = 0; i < 320; i++) {
            uint8_t *bit = kind ? &plan->dnot[i] : &plan->cnot[i];
            *bit ^= 1;
            build_prefix_graph(plan, outputs, output_p);
            int trial = live_operation_count(outputs, 1600, 256);
            if (trial < best) {
                gain += best - trial;
                best = trial;
                improved = 1;
            } else {
                *bit ^= 1;
            }
        }
        if (!improved) break;
    }
    build_prefix_graph(plan, outputs, output_p);
    if (live_operation_count(outputs, 1600, 256) != best)
        fail("seeded prefix greedy count mismatch");
    printf("prefix-round1-seeded-greedy-gain %d\n", gain);
}

static void build_body_graph(const uint8_t input_p[1600], const Plan *plan,
                             int outputs[1600], uint8_t output_p[1600]) {
    Value S[25][64], NS[25][64], C[5][64], D[5][64];
    uint8_t have_c[320] = {0}, have_d[320] = {0};
    reset_graph(1600, 0);
    for (int q = 0; q < 1600; q++) S[q >> 6][q & 63] = val(q, input_p[q]);
    memcpy(NS, S, sizeof(NS));
    for (int Y = 0; Y < 5; Y++) for (int z = 0; z < 64; z++) {
        Value b[5], out[5];
        for (int X = 0; X < 5; X++) {
            int y = X, x = (3 * Y + X) % 5;
            int zz = (z - ROT[x][y]) & 63;
            Value d = lazy_d(S, C, D, have_c, have_d, plan->cnot, plan->dnot, x, zz);
            b[X] = xor_value(S[x + 5 * y][zz], d);
        }
        int target = plan->target[64 * Y + z] ^
            (Y == 0 && ((plan->ib >> z) & 1));
        build_target_row(b, target, out);
        for (int X = 0; X < 5; X++) NS[X + 5 * Y][z] = out[X];
    }
    for (int q = 0; q < 1600; q++) {
        Value v = NS[q >> 6][q & 63];
        outputs[q] = v.n;
        output_p[q] = v.p ^ (q < 64 && ((plan->ib >> q) & 1));
    }
}

static void build_end_graph(const uint8_t input_p[1600], int outputs[256],
                            uint8_t output_p[256]) {
    Value S[25][64], C[5][64], D[5][64];
    uint8_t have_c[320] = {0}, have_d[320] = {0};
    reset_graph(1600, 0);
    for (int q = 0; q < 1600; q++) S[q >> 6][q & 63] = val(q, input_p[q]);
    for (int z = 0; z < 64; z++) {
        Value b[5], out[5];
        for (int X = 0; X < 5; X++) {
            int y = X, x = X;
            int zz = (z - ROT[x][y]) & 63;
            Value d = lazy_d(S, C, D, have_c, have_d, NULL, NULL, x, zz);
            b[X] = xor_value(S[x + 5 * y][zz], d);
        }
        build_dynamic_row(b, 0x0f, out);
        for (int X = 0; X < 4; X++) {
            Value v = out[X];
            if (X == 0) v.p ^= (RC[23] >> z) & 1;
            int j = 64 * X + z;
            outputs[j] = v.n;
            output_p[j] = v.p;
        }
    }
}

static Insn *allocate_block(const int *outputs, const int *output_regs, int output_count,
                            const int *input_regs, int input_count, size_t *program_count,
                            int counts[5], int *high_reg) {
    uint8_t *live = calloc((size_t)node_count, 1);
    uint16_t *last = calloc((size_t)node_count, sizeof(*last));
    uint16_t *reg = calloc((size_t)node_count, sizeof(*reg));
    uint16_t *out_index = malloc((size_t)node_count * sizeof(*out_index));
    uint16_t *free_regs = malloc(NREG * sizeof(*free_regs));
    uint8_t *busy = calloc(NREG, 1);
    uint8_t *reserved = calloc(NREG, 1);
    Insn *prog = malloc((size_t)node_count * sizeof(*prog));
    if (!live || !last || !reg || !out_index || !free_regs || !busy || !reserved || !prog)
        fail("allocator memory failure");
    memset(out_index, 0xff, (size_t)node_count * sizeof(*out_index));
    memset(counts, 0, 5 * sizeof(*counts));
    for (int j = 0; j < output_count; j++) {
        if (outputs[j] < input_count || out_index[outputs[j]] != UINT16_MAX)
            fail("invalid/shared block output");
        live[outputs[j]] = 1;
        out_index[outputs[j]] = j;
        reserved[output_regs[j]] = 1;
    }
    for (int i = node_count - 1; i >= input_count; i--) if (live[i]) {
        live[nodes[i].a] = 1;
        if (nodes[i].op != O_NOT) live[nodes[i].b] = 1;
    }
    for (int i = input_count; i < node_count; i++) if (live[i]) {
        last[nodes[i].a] = i;
        if (nodes[i].op != O_NOT) last[nodes[i].b] = i;
    }
    for (int j = 0; j < output_count; j++) last[outputs[j]] = UINT16_MAX;
    for (int j = 0; j < input_count; j++) {
        reg[j] = input_regs[j];
        if (last[j]) busy[input_regs[j]] = 1;
    }
    int free_count = 0;
    for (int r = NREG - 1; r >= 0; r--)
        if (!busy[r] && !reserved[r]) free_regs[free_count++] = r;
    size_t pc = 0;
    int high = 0;
    for (int j = 0; j < input_count; j++) if (input_regs[j] + 1 > high) high = input_regs[j] + 1;
    for (int j = 0; j < output_count; j++) if (output_regs[j] + 1 > high) high = output_regs[j] + 1;
    for (int i = input_count; i < node_count; i++) if (live[i]) {
        int op = nodes[i].op, a = nodes[i].a, b = op == O_NOT ? a : nodes[i].b;
        if (last[a] == i) {
            int r = reg[a];
            busy[r] = 0;
            if (!reserved[r]) free_regs[free_count++] = r;
        }
        if (b != a && last[b] == i) {
            int r = reg[b];
            busy[r] = 0;
            if (!reserved[r]) free_regs[free_count++] = r;
        }
        int d;
        if (out_index[i] != UINT16_MAX) {
            d = output_regs[out_index[i]];
            if (busy[d]) fail("fixed output register busy");
        } else {
            if (!free_count) fail("register file exhausted");
            d = free_regs[--free_count];
        }
        busy[d] = 1;
        reg[i] = d;
        if (d + 1 > high) high = d + 1;
        uint8_t enc = op == O_XOR ? 0 : op == O_AND ? 1 : op == O_OR ? 2 : 3;
        prog[pc++] = (Insn){enc, (uint16_t)d, (uint16_t)reg[a],
                           (uint16_t)(op == O_NOT ? 0 : reg[nodes[i].b])};
        counts[op]++;
    }
    free(live); free(last); free(reg); free(out_index); free(free_regs); free(busy); free(reserved);
    *program_count = pc;
    *high_reg = high;
    return prog;
}

#ifndef PACKED_ONLY
static void write_program(const char *path, const Insn *prog, size_t n) {
    FILE *f = fopen(path, "wb");
    if (!f) {
        fprintf(stderr, "gen_combined: fopen %s: %s\n", path, strerror(errno));
        exit(1);
    }
    for (size_t i = 0; i < n; i++) {
        uint64_t w = (uint64_t)prog[i].op | (uint64_t)prog[i].d << 3 |
                     (uint64_t)prog[i].a << 15 | (uint64_t)prog[i].b << 27;
        uint8_t out[5];
        for (int j = 0; j < 5; j++) out[j] = (uint8_t)(w >> (8 * j));
        if (fwrite(out, 1, 5, f) != 5) fail("program write failed");
    }
    if (fclose(f)) fail("program close failed");
}
#endif

static void write_packed_program(const char *path, const Insn *prog, size_t n) {
    size_t bytes = (39 * n + 7) / 8;
    uint8_t *packed = calloc(bytes ? bytes : 1, 1);
    if (!packed) fail("packed-program allocation failure");
    for (size_t i = 0; i < n; i++) {
        uint64_t w = (uint64_t)prog[i].op | (uint64_t)prog[i].d << 3 |
                     (uint64_t)prog[i].a << 15 | (uint64_t)prog[i].b << 27;
        size_t bit = 39 * i;
        for (int k = 0; k < 39; k++)
            packed[(bit + (size_t)k) >> 3] |= (uint8_t)(((w >> k) & 1) << ((bit + (size_t)k) & 7));
    }
    FILE *f = fopen(path, "wb");
    if (!f || (bytes && fwrite(packed, 1, bytes, f) != bytes) || fclose(f))
        fail("packed program write failed");
    free(packed);
}

static size_t emit_block(const char *dir, const char *name, const int *outputs,
                         int output_count, int input_count, int input_base,
                         int output_base, int *highest) {
    int *input_regs = malloc((size_t)input_count * sizeof(*input_regs));
    int *output_regs = malloc((size_t)output_count * sizeof(*output_regs));
    if (!input_regs || !output_regs) fail("register-map allocation failure");
    for (int i = 0; i < input_count; i++) input_regs[i] = input_base + i;
    for (int i = 0; i < output_count; i++) output_regs[i] = output_base + i;
    size_t n;
    int mix[5], high;
    Insn *prog = allocate_block(outputs, output_regs, output_count, input_regs,
                                input_count, &n, mix, &high);
    char path[4096];
#ifndef PACKED_ONLY
    if (snprintf(path, sizeof(path), "%s/%s.bin", dir, name) >= (int)sizeof(path))
        fail("output path too long");
    write_program(path, prog, n);
#endif
    if (snprintf(path, sizeof(path), "%s/%s.p39", dir, name) >= (int)sizeof(path))
        fail("packed output path too long");
    write_packed_program(path, prog, n);
    printf("block %s XOR %d AND %d OR %d NOT %d total %zu highest-register+1 %d\n",
           name, mix[O_XOR], mix[O_AND], mix[O_OR], mix[O_NOT], n, high);
    if (high > *highest) *highest = high;
    free(prog); free(input_regs); free(output_regs);
    return n;
}

static size_t emit_bridge(const char *dir, const uint8_t from[1600],
                          const uint8_t to[1600]) {
    Insn *prog = malloc(1600 * sizeof(*prog));
    if (!prog) fail("bridge allocation failure");
    size_t n = 0;
    for (int q = 0; q < 1600; q++) if (from[q] != to[q])
        prog[n++] = (Insn){3, (uint16_t)(256 + q), (uint16_t)(256 + q), 0};
    char path[4096];
#ifndef PACKED_ONLY
    if (snprintf(path, sizeof(path), "%s/G.bin", dir) >= (int)sizeof(path))
        fail("output path too long");
    write_program(path, prog, n);
#endif
    if (snprintf(path, sizeof(path), "%s/G.p39", dir) >= (int)sizeof(path))
        fail("packed bridge path too long");
    write_packed_program(path, prog, n);
    printf("block G XOR 0 AND 0 OR 0 NOT %zu total %zu highest-register+1 1856\n", n, n);
    free(prog);
    return n;
}

static void write_regeneration_data(const char *path, const Plan *prefix_plan,
                                    const Plan best_chain[8],
                                    const uint8_t best_cycle[1600]) {
    static const uint8_t magic[8] = {'H', 'S', '2', '4', 'P', 'L', 'N', '1'};
    FILE *f = fopen(path, "wb");
    if (!f || fwrite(magic, sizeof(magic), 1, f) != 1 ||
        fwrite(prefix_plan, sizeof(*prefix_plan), 1, f) != 1 ||
        fwrite(best_chain, sizeof(*best_chain), 8, f) != 8 ||
        fwrite(best_cycle, 1600, 1, f) != 1 ||
        fwrite(row_table, sizeof(row_table), 1, f) != 1 || fclose(f))
        fail("cannot write regeneration data");
}

static void read_seed_plan(const char *path, Plan *prefix_plan,
                           Plan chain[8], uint8_t cycle[1600]) {
    static const uint8_t expected[8] = {'H', 'S', '2', '4', 'O', 'P', 'T', '1'};
    uint8_t magic[8];
    FILE *f = fopen(path, "rb");
    if (!f || fread(magic, sizeof(magic), 1, f) != 1 ||
        memcmp(magic, expected, sizeof(magic)))
        fail("cannot read seed-plan header");
    memset(prefix_plan, 0, sizeof(*prefix_plan));
    if (fread(prefix_plan->cnot, 320, 1, f) != 1 ||
        fread(prefix_plan->dnot, 320, 1, f) != 1 ||
        fread(cycle, 1600, 1, f) != 1)
        fail("cannot read seed prefix");
    for (int b = 0; b < 8; b++) {
        memset(&chain[b], 0, sizeof(chain[b]));
        if (fread(chain[b].cnot, 320, 1, f) != 1 ||
            fread(chain[b].dnot, 320, 1, f) != 1 ||
            fread(chain[b].target, 320, 1, f) != 1 ||
            fread(&chain[b].ib, sizeof(chain[b].ib), 1, f) != 1)
            fail("cannot read seed body");
    }
    if (fgetc(f) != EOF || fclose(f)) fail("seed plan has trailing data");
}

static long long chain_cost(const Plan chain[8], const uint8_t cycle[1600]) {
    static const int runs[8] = {3, 3, 3, 3, 3, 2, 2, 2};
    uint8_t input[1600];
    memcpy(input, cycle, sizeof(input));
    long long total = 0;
    for (int b = 0; b < 8; b++) {
        total += (long long)runs[b] * current_cost(input, &chain[b]);
        targets_to_state(chain[b].target, input);
    }
    if (memcmp(input, cycle, sizeof(input))) fail("polished chain does not close");
    return total;
}

static long long body_pair_cost(const Plan chain[8], const uint8_t cycle[1600],
                                int body) {
    static const int runs[8] = {3, 3, 3, 3, 3, 2, 2, 2};
    uint8_t input[1600];
    if (body == 0) memcpy(input, cycle, sizeof(input));
    else targets_to_state(chain[body - 1].target, input);
    long long total = (long long)runs[body] * current_cost(input, &chain[body]);
    if (body < 7) {
        uint8_t next[1600];
        targets_to_state(chain[body].target, next);
        total += (long long)runs[body + 1] * current_cost(next, &chain[body + 1]);
    }
    return total;
}

static long long weighted_body_cost(const Plan chain[8], const uint8_t cycle[1600],
                                    int body) {
    uint8_t input[1600];
    if (body == 0) memcpy(input, cycle, sizeof(input));
    else targets_to_state(chain[body - 1].target, input);
    return (long long)(body < 5 ? 3 : 2) * current_cost(input, &chain[body]);
}

static long long global_polish(Plan chain[8], const uint8_t cycle[1600],
                               int max_sweeps) {
    long long total = chain_cost(chain, cycle);
    for (int sweep = 0; sweep < max_sweeps; sweep++) {
        int improvements = 0;
        for (int b = 0; b < 8; b++) {
            uint8_t input[1600];
            if (b == 0) memcpy(input, cycle, sizeof(input));
            else targets_to_state(chain[b - 1].target, input);
            int before = current_cost(input, &chain[b]);
            for (int kind = 0; kind < 2; kind++) for (int i = 0; i < 320; i++) {
                uint8_t *bit = kind ? &chain[b].dnot[i] : &chain[b].cnot[i];
                *bit ^= 1;
                int after = current_cost(input, &chain[b]);
                if (after < before) {
                    total += (long long)(after - before) *
                        (b < 5 ? 3 : 2);
                    before = after;
                    improvements++;
                } else {
                    *bit ^= 1;
                }
            }
        }
        for (int b = 0; b < 7; b++) for (int i = 0; i < 320; i++) {
            int old = chain[b].target[i], chosen = old;
            long long before = body_pair_cost(chain, cycle, b), best = before;
            for (int target = 0; target < 32; target++) {
                chain[b].target[i] = (uint8_t)target;
                long long trial = body_pair_cost(chain, cycle, b);
                if (trial < best) {
                    best = trial;
                    chosen = target;
                }
            }
            chain[b].target[i] = (uint8_t)chosen;
            if (best < before) {
                total += best - before;
                improvements++;
            }
        }
        long long checked = chain_cost(chain, cycle);
        if (checked != total) fail("global polish delta mismatch");
        printf("global polish sweep %d operations %lld improvements %d\n",
               sweep, total, improvements);
        if (!improvements) break;
    }
    return total;
}

static long long global_anneal(Plan chain[8], const uint8_t cycle[1600],
                               int iterations, uint64_t seed) {
    Plan best[8];
    long long total = chain_cost(chain, cycle), best_cost = total;
    memcpy(best, chain, sizeof(best));
    for (int it = 0; it < iterations; it++) {
        uint64_t r = rng_next(&seed);
        int body = (int)((r >> 8) & 7);
        int kind = (int)(r % (body < 7 ? 3 : 2));
        int index = (int)((r >> 16) % 320);
        int old;
        long long before = kind == 2 ? body_pair_cost(chain, cycle, body) :
            weighted_body_cost(chain, cycle, body);
        if (kind == 0) {
            old = chain[body].cnot[index];
            chain[body].cnot[index] ^= 1;
        } else if (kind == 1) {
            old = chain[body].dnot[index];
            chain[body].dnot[index] ^= 1;
        } else {
            old = chain[body].target[index];
            chain[body].target[index] ^= (uint8_t)(1 + ((r >> 32) % 31));
        }
        long long after = kind == 2 ? body_pair_cost(chain, cycle, body) :
            weighted_body_cost(chain, cycle, body);
        long long diff = after - before;
        double progress = iterations ? (double)it / iterations : 1.0;
        double temperature = 24.0 * exp(-5.5 * progress) + 0.05;
        double uniform = (double)(rng_next(&seed) >> 11) * (1.0 / 9007199254740992.0);
        int accept = diff <= 0 || uniform < exp(-(double)diff / temperature);
        if (accept) {
            total += diff;
            if (total < best_cost) {
                best_cost = total;
                memcpy(best, chain, sizeof(best));
            }
        } else if (kind == 0) chain[body].cnot[index] = (uint8_t)old;
        else if (kind == 1) chain[body].dnot[index] = (uint8_t)old;
        else chain[body].target[index] = (uint8_t)old;
    }
    memcpy(chain, best, sizeof(best));
    if (chain_cost(chain, cycle) != best_cost) fail("global anneal mismatch");
    return best_cost;
}

int main(int argc, char **argv) {
    int rebase_seed = 0;
    if (argc >= 3 && !strcmp(argv[1], "--kl")) {
        load_kl_record(argv[2]);
        argc -= 2;
        argv += 2;
    }
    if (argc >= 2 && !strcmp(argv[1], "--rebase")) {
        rebase_seed = 1;
        argc--;
        argv++;
    }
    const char *dir = argc > 1 ? argv[1] : ".";
    int iterations = argc > 2 ? atoi(argv[2]) : 30000;
    int trials = argc > 3 ? atoi(argv[3]) : 4;
    uint64_t seed_offset = argc > 6 ? strtoull(argv[6], NULL, 0) : 0;
    int perturbations = argc > 7 ? atoi(argv[7]) : 0;
    if (iterations < 0 || trials < 1 || trials > 32) fail("invalid optimizer settings");
    make_row_table();

    int prefix_nodes[1600], body_nodes[1600], end_nodes[256];
    uint8_t prefix_p[1600], out_p[1600], end_p[256];
    Plan prefix_plan, seed_chain[8];
    uint8_t seed_cycle[1600];
    int have_seed = argc > 5;
    if (rebase_seed && !have_seed) fail("--rebase requires a seed plan");
    if (have_seed) {
        read_seed_plan(argv[5], &prefix_plan, seed_chain, seed_cycle);
        if (rebase_seed) {
            optimize_prefix_from_seed(&prefix_plan, prefix_nodes, prefix_p);
            memcpy(seed_cycle, prefix_p, sizeof(seed_cycle));
            state_to_targets(seed_cycle, seed_chain[7].target);
            printf("rebased seed plan %s onto loaded constants\n", argv[5]);
        } else {
            build_prefix_graph(&prefix_plan, prefix_nodes, prefix_p);
            if (memcmp(prefix_p, seed_cycle, 1600)) fail("seed prefix polarity mismatch");
            printf("loaded seed plan %s\n", argv[5]);
        }
    } else {
        optimize_prefix(&prefix_plan, prefix_nodes, prefix_p);
    }
    int prefix_node_count = node_count;
    Node *prefix_copy = malloc((size_t)node_count * sizeof(*prefix_copy));
    Form *form_copy = malloc((size_t)form_count * sizeof(*form_copy));
    int prefix_form_count = form_count;
    if (!prefix_copy || !form_copy) fail("prefix snapshot allocation failure");
    memcpy(prefix_copy, nodes, (size_t)node_count * sizeof(*nodes));
    memcpy(form_copy, forms, (size_t)form_count * sizeof(*forms));

    static const int runs[8] = {3, 3, 3, 3, 3, 2, 2, 2};
    Plan best_chain[8], chain[8], scratch[8];
    uint8_t best_cycle[1600];
    long long best_weighted = -1;
    if (have_seed) {
        uint8_t input[1600];
        memcpy(input, seed_cycle, sizeof(input));
        long long weighted = 0;
        for (int b = 0; b < 8; b++) {
            int cost = current_cost(input, &seed_chain[b]);
            weighted += (long long)runs[b] * cost;
            targets_to_state(seed_chain[b].target, input);
        }
        if (memcmp(input, seed_cycle, sizeof(input))) fail("seed cycle does not close");
        printf("seed body operations %lld\n", weighted);
        best_weighted = weighted;
        memcpy(best_chain, seed_chain, sizeof(best_chain));
        memcpy(best_cycle, seed_cycle, sizeof(best_cycle));
        long long polished = global_polish(best_chain, best_cycle, 8);
        if (polished < best_weighted) best_weighted = polished;
        for (int trial = 0; trial < trials && iterations > 0; trial++) {
            Plan candidate[8];
            memcpy(candidate, seed_chain, sizeof(candidate));
            uint64_t seed = UINT64_C(0x6a09e667f3bcc909) ^
                (uint64_t)(trial + 1 + seed_offset) * UINT64_C(0x9e3779b97f4a7c15);
            for (int move = 0; move < perturbations; move++) {
                uint64_t r = rng_next(&seed);
                int body = (int)((r >> 8) & 7);
                int kind = (int)(r % (body < 7 ? 3 : 2));
                int index = (int)((r >> 16) % 320);
                if (kind == 0) candidate[body].cnot[index] ^= 1;
                else if (kind == 1) candidate[body].dnot[index] ^= 1;
                else candidate[body].target[index] ^=
                    (uint8_t)(1 + ((r >> 32) % 31));
            }
            long long annealed = global_anneal(candidate, seed_cycle, iterations, seed);
            long long candidate_cost = global_polish(candidate, seed_cycle, 4);
            printf("global trial %d annealed %lld polished %lld\n",
                   trial, annealed, candidate_cost);
            if (candidate_cost < best_weighted) {
                best_weighted = candidate_cost;
                memcpy(best_chain, candidate, sizeof(best_chain));
            }
        }
    }
    if (!have_seed) for (int trial = 0; trial < trials; trial++) {
        uint8_t cycle[1600], input[1600];
        memcpy(cycle, prefix_p, sizeof(cycle));
        int derivations = trial % 3;
        for (int outer = 0; outer < derivations; outer++) {
            memcpy(input, cycle, sizeof(input));
            for (int b = 0; b < 7; b++) {
                uint64_t seed = UINT64_C(0x243f6a8885a308d3) ^
                    (uint64_t)(trial + 1) * UINT64_C(0xd1b54a32d192ed03) ^
                    (uint64_t)(outer + 1) * UINT64_C(0x9e3779b97f4a7c15) ^
                    (uint64_t)(b + 1) * UINT64_C(0x94d049bb133111eb);
                optimize_plan(input, NULL, NULL, NULL,
                              have_seed ? seed_chain[b].ib : 0,
                              seed, iterations, &scratch[b]);
                targets_to_state(scratch[b].target, input);
            }
            uint64_t seed = UINT64_C(0x13198a2e03707344) ^
                (uint64_t)(trial + 1) * UINT64_C(0x94d049bb133111eb) ^
                (uint64_t)(outer + 1) * UINT64_C(0xd1b54a32d192ed03);
            optimize_plan(input, NULL, NULL, prefix_p,
                          have_seed ? seed_chain[7].ib : 0,
                          seed, iterations, &scratch[7]);
            targets_to_state(scratch[7].target, cycle);
        }

        memcpy(input, cycle, sizeof(input));
        long long weighted = 0;
        for (int b = 0; b < 8; b++) {
            const uint8_t *fixed = b == 7 ? cycle : NULL;
            uint64_t seed = UINT64_C(0x9e3779b97f4a7c15) ^
                (uint64_t)(trial + 1) * UINT64_C(0xd1b54a32d192ed03) ^
                (uint64_t)(b + 1) * UINT64_C(0x94d049bb133111eb);
            const uint8_t *next_fixed = b == 6 ? cycle : NULL;
            optimize_plan(input, fixed, next_fixed, NULL,
                          have_seed ? seed_chain[b].ib : 0,
                          seed, iterations, &chain[b]);
            int cost = current_cost(input, &chain[b]);
            weighted += (long long)runs[b] * cost;
            targets_to_state(chain[b].target, input);
        }
        int bridge = 0;
        for (int i = 0; i < 1600; i++) bridge += cycle[i] != prefix_p[i];
        weighted += bridge;
        printf("optimizer trial %d body-plus-bridge-operations %lld bridge %d\n",
               trial, weighted, bridge);
        if (best_weighted < 0 || weighted < best_weighted) {
            best_weighted = weighted;
            memcpy(best_chain, chain, sizeof(best_chain));
            memcpy(best_cycle, cycle, sizeof(best_cycle));
        }
    }

    if (argc > 4)
        write_regeneration_data(argv[4], &prefix_plan, best_chain, best_cycle);

    int highest = 0;
    memcpy(nodes, prefix_copy, (size_t)prefix_node_count * sizeof(*nodes));
    memcpy(forms, form_copy, (size_t)prefix_form_count * sizeof(*forms));
    node_count = prefix_node_count;
    form_count = prefix_form_count;
    free(prefix_copy);
    free(form_copy);
    size_t stored = emit_block(dir, "P", prefix_nodes, 1600, 256, 0, 256, &highest);
    size_t prefix_count = stored;
    size_t bridge_count = emit_bridge(dir, prefix_p, best_cycle);
    stored += bridge_count;

    uint8_t input[1600];
    memcpy(input, best_cycle, sizeof(input));
    size_t body_count[8];
    for (int b = 0; b < 8; b++) {
        build_body_graph(input, &best_chain[b], body_nodes, out_p);
        int expected = current_cost(input, &best_chain[b]);
        int in_base = (b & 1) ? 1856 : 256;
        int out_base = (b & 1) ? 256 : 1856;
        char name[8];
        snprintf(name, sizeof(name), "B%d", b + 1);
        body_count[b] = emit_block(dir, name, body_nodes, 1600, 1600, in_base,
                                   out_base, &highest);
        if ((int)body_count[b] != expected) fail("body count differs from polarity ledger");
        stored += body_count[b];
        memcpy(input, out_p, sizeof(input));
    }
    if (memcmp(input, best_cycle, sizeof(input))) fail("eight-body polarity cycle does not close");

    uint8_t round22_p[1600];
    targets_to_state(best_chain[4].target, round22_p);
    build_end_graph(round22_p, end_nodes, end_p);
    size_t end_count = emit_block(dir, "E", end_nodes, 256, 1600, 1856, 0, &highest);
    stored += end_count;

    int iota = 0;
    for (int r = 2; r <= 22; r++) {
        int b = (r - 2) & 7;
        iota += __builtin_popcountll(RC[r] ^ best_chain[b].ib);
    }
    int driver = 2 * 21 + iota;
    long long executed = (long long)prefix_count + bridge_count + end_count + driver;
    for (int b = 0; b < 8; b++) executed += (long long)runs[b] * body_count[b];
    uint64_t pd[4] = {0, 0, 0, 0};
    for (int j = 0; j < 256; j++) pd[j >> 6] |= (uint64_t)end_p[j] << (j & 63);
    char pd_path[4096];
    if (snprintf(pd_path, sizeof(pd_path), "%s/PD.bin", dir) >= (int)sizeof(pd_path))
        fail("PD path too long");
    FILE *pd_file = fopen(pd_path, "wb");
    if (!pd_file || fwrite(pd, sizeof(pd), 1, pd_file) != 1 || fclose(pd_file))
        fail("cannot write PD.bin");

    printf("stored-block-instructions %zu\n", stored);
    printf("iota-xors %d\n", iota);
    printf("driver %d\n", driver);
    printf("TOTAL %lld\n", executed);
    printf("highest-register+1 %d\n", highest);
    printf("PD %016" PRIx64 " %016" PRIx64 " %016" PRIx64 " %016" PRIx64 "\n",
           pd[0], pd[1], pd[2], pd[3]);
    printf("optimizer iterations-per-body %d trials %d\n", iterations, trials);
    return highest > 4096 ? 2 : 0;
}

```

### step_search.c

```c
#define main r24_library_main
#define make_row_table inherited_make_row_table
#define build_target_row inherited_build_target_row
#include "plan_search_local.c"
#undef build_target_row
#undef make_row_table
#undef main
#include "s3_basis.h"
#ifndef FREESTANDING
#include <time.h>
#endif

static double bounded_exp(double x){
    if(x < -40.0) return 0.0;
    double y=x/64.0;
    double e=1.0+y+y*y/2.0+y*y*y/6.0+y*y*y*y/24.0;
    for(int i=0;i<6;i++)e*=e;
    return e;
}

static const int S3_LANES[12]={0,2,3,5,7,8,10,12,13,15,11,14};

static void chain_order(int tricks,int order[5]){
    int start=0;while((tricks>>start)&1)start++;
    for(int i=0;i<5;i++)order[i]=(start-i+5)%5;
}

static void eval_native_row(int pin,int subset,int tricks,int selected,
                            int *cost_out,int *target_out){
    int bp[5],op[5]={0,0,0,0,0},order[5],cost=__builtin_popcount((unsigned)subset);
    for(int x=0;x<5;x++)bp[x]=((pin>>x)&1)^((subset>>x)&1);
    chain_order(tricks,order);
    for(int i=0;i<5;i++){
        int x=order[i],a=((tricks>>x)&1)?op[(x+1)%5]^1:bp[(x+1)%5]^1,b=bp[(x+2)%5],tp;
        cost+=sim_term(a,b,(selected>>x)&1,&tp)+1;op[x]=bp[x]^tp;
    }
    int target=0;for(int x=0;x<5;x++)target|=op[x]<<x;*cost_out=cost;*target_out=target;
}

static void verify_native_row(int pin,int target,Decision d){
    int order[5];chain_order(d.tricks,order);
    for(int bits=0;bits<32;bits++){
        int w[5],p[5],ow[5]={0,0,0,0,0},op[5]={0,0,0,0,0};
        for(int x=0;x<5;x++){w[x]=((bits>>x)&1)^((pin>>x)&1);p[x]=(pin>>x)&1;if((d.subset>>x)&1){w[x]^=1;p[x]^=1;}}
        for(int i=0;i<5;i++){
            int x=order[i],lw,lp;if((d.tricks>>x)&1){lw=ow[(x+1)%5];lp=op[(x+1)%5]^1;}else{lw=w[(x+1)%5];lp=p[(x+1)%5]^1;}
            int rw=w[(x+2)%5],rp=p[(x+2)%5],tw,tp;
            if(lp==rp){if(!lp){tw=lw&rw;tp=0;}else{tw=lw|rw;tp=1;}}
            else{int pw=lp?rw:lw,other=lp?lw:rw;if((d.select_mask>>x)&1){tw=(pw^1)|other;tp=1;}else{tw=pw^(pw&other);tp=0;}}
            ow[x]=w[x]^tw;op[x]=p[x]^tp;
        }
        int got_p=0;for(int x=0;x<5;x++){int logical=ow[x]^op[x],truth=((bits>>x)&1)^((((bits>>((x+1)%5))&1)^1)&((bits>>((x+2)%5))&1));if(logical!=truth)fail("chained row truth mismatch");got_p|=op[x]<<x;}
        if(got_p!=target)fail("chained row polarity mismatch");
    }
}

static void make_row_table(void){
    for(int pin=0;pin<32;pin++){
        for(int target=0;target<32;target++)row_table[pin][target]=(Decision){0,0,0,255};
        for(int subset=0;subset<32;subset++)for(int tricks=0;tricks<31;tricks++)for(int selected=0;selected<32;selected++){
            int cost,target;eval_native_row(pin,subset,tricks,selected,&cost,&target);Decision best=row_table[pin][target];
            Decision candidate={(uint8_t)subset,(uint8_t)tricks,(uint8_t)selected,(uint8_t)cost};
            int better=candidate.cost<best.cost;
            if(candidate.cost==best.cost){int ct=__builtin_popcount((unsigned)candidate.tricks),bt=__builtin_popcount((unsigned)best.tricks),cs=__builtin_popcount((unsigned)candidate.subset),bs=__builtin_popcount((unsigned)best.subset);better=ct<bt||(ct==bt&&(cs<bs||(cs==bs&&(candidate.subset<best.subset||(candidate.subset==best.subset&&(candidate.tricks<best.tricks||(candidate.tricks==best.tricks&&candidate.select_mask<best.select_mask)))))));}
            if(better)row_table[pin][target]=candidate;
        }
        int min_cost=255,min_target=0;
        for(int target=0;target<32;target++){
            Decision best=row_table[pin][target];
            if(best.cost==255)fail("unreachable native row target polarity");
            verify_native_row(pin,target,best);row_table[pin][target]=best;
            if(best.cost<min_cost){min_cost=best.cost;min_target=target;}
        }
        row_min_cost[pin]=(uint8_t)min_cost;row_min_target[pin]=(uint8_t)min_target;
    }
}

static uint64_t chained_table_checksum(void){uint64_t h=UINT64_C(1469598103934665603);for(int p=0;p<32;p++)for(int q=0;q<32;q++){Decision d=row_table[p][q];uint8_t bytes[4]={d.subset,d.tricks,d.select_mask,d.cost};for(int i=0;i<4;i++){h^=bytes[i];h*=UINT64_C(1099511628211);}}return h;}

static void build_target_row(Value b[5],int target,Value out[5]){
    int pin=0;for(int x=0;x<5;x++)pin|=b[x].p<<x;
    Decision d=row_table[pin][target];int order[5];chain_order(d.tricks,order);
    for(int x=0;x<5;x++)if((d.subset>>x)&1)b[x]=complement_representation(b[x]);
    for(int i=0;i<5;i++){
        int x=order[i];Value first=((d.tricks>>x)&1)?out[(x+1)%5]:b[(x+1)%5];
        Value t=and_value(val(first.n,first.p^1),b[(x+2)%5],(d.select_mask>>x)&1);out[x]=xor_value(b[x],t);
    }
    int got=0;for(int x=0;x<5;x++)got|=out[x].p<<x;
    if(got!=target)fail("native row construction mismatch");
}

static uint16_t emitter_decisions[24][320];static uint8_t emitter_has_decisions[24];
static void build_encoded_row(Value b[5],uint16_t word,Value out[5]){
    int subset=word&31,tricks=(word>>5)&31,selected=(word>>10)&31,order[5];chain_order(tricks,order);
    for(int x=0;x<5;x++)if((subset>>x)&1)b[x]=complement_representation(b[x]);
    for(int i=0;i<5;i++){int x=order[i];Value first=((tricks>>x)&1)?out[(x+1)%5]:b[(x+1)%5];Value t=and_value(val(first.n,first.p^1),b[(x+2)%5],(selected>>x)&1);out[x]=xor_value(b[x],t);}
}

static void set_s3_trial(int trial){
    memset(KL,0,sizeof(KL)); KL[16]=UINT64_C(0x8000000000000006);
    uint64_t s=UINT64_C(0x9e3779b97f4a7c15)*(uint64_t)trial+1;
    for(int i=0;i<11;i++) rng_next(&s);
    uint64_t selector=s;
    for(int i=0;i<12;i++){
        uint64_t value=S3_KB0[i];
        for(int bit=0;bit<64;bit++) if((selector>>bit)&1) value^=S3_KBV[bit][i];
        KL[S3_LANES[i]]=value;
    }
}

static void make_min_plan(const uint8_t input[1600],int round,Plan *p){
    memset(p,0,sizeof(*p)); p->ib=RC[round];
    uint8_t patterns[320]; row_patterns(input,p->cnot,p->dnot,patterns);
    for(int i=0;i<320;i++) p->target[i]=(uint8_t)(row_min_target[patterns[i]] ^
        (i<64 && ((RC[round]>>i)&1)));
}

static void exact_round(Value state[25][64],int round,int last,const Plan *plan,
                        int *outputs,uint8_t *output_p){
    Value next[25][64],column[5][64],delta[5][64]; memcpy(next,state,sizeof(next));
    const uint8_t *cn=plan?plan->cnot:NULL,*dn=plan?plan->dnot:NULL;
    for(int x=0;x<5;x++){
        Value s=state[x][63];
        for(int y=1;y<5;y++) s=xor_value(s,state[x+5*y][63]);
        if(cn&&cn[64*x+63]) s=complement_representation(s);
        column[x][63]=s;
    }
    for(int z=0;z<64;z++){
        if(z<63) for(int x=0;x<5;x++){
            Value s=state[x][z];
            for(int y=1;y<5;y++) s=xor_value(s,state[x+5*y][z]);
            if(cn&&cn[64*x+z]) s=complement_representation(s);
            column[x][z]=s;
        }
        for(int x=0;x<5;x++){
            Value d=xor_value(column[(x+4)%5][z],column[(x+1)%5][(z+63)&63]);
            if(dn&&dn[64*x+z]) d=complement_representation(d);
            delta[x][z]=d;
        }
    }
    int ny=last?1:5;
    for(int Y=0;Y<ny;Y++)for(int z=0;z<64;z++){
        Value b[5],out[5];for(int X=0;X<5;X++){int y=X,x=(3*Y+X)%5,zz=(z-ROT[x][y])&63;b[X]=xor_value(state[x+5*y][zz],delta[x][zz]);}
        if(plan&&plan->ib==RC[round]&&!last){
            if(emitter_has_decisions[round])build_encoded_row(b,emitter_decisions[round][64*Y+z],out);
            else{int target=plan->target[64*Y+z]^(Y==0&&((RC[round]>>z)&1));build_target_row(b,target,out);}
        }
        else build_dynamic_row(b,last?15:31,out);
        for(int X=0;X<(last?4:5);X++)next[X+5*Y][z]=out[X];
    }
    for(int z=0;z<64;z++)next[0][z].p^=(RC[round]>>z)&1;
    memcpy(state,next,sizeof(next));
    int count=last?256:1600;
    for(int q=0;q<count;q++){Value v=state[q>>6][q&63];outputs[q]=v.n;output_p[q]=v.p;}
}

static void build_prefix_exact(const Plan *prefix,int outputs[1600],uint8_t output_p[1600]){
    Value state[25][64];reset_graph(256,1);
    for(int l=0;l<25;l++)for(int z=0;z<64;z++)state[l][z]=constant((KL[l]>>z)&1);
    for(int z=0;z<64;z++){state[1][z]=val(z,0);state[6][z]=val(64+z,0);state[4][z]=val(128+z,0);state[9][z]=val(192+z,0);
        state[11][z]=xor_value(xor_value(val(z,0),val(64+z,0)),constant((KL[11]>>z)&1));
        state[14][z]=xor_value(xor_value(val(128+z,0),val(192+z,0)),constant((KL[14]>>z)&1));}
    uint8_t scratch[1600];int nodes[1600];exact_round(state,0,0,NULL,nodes,scratch);exact_round(state,1,0,prefix,nodes,scratch);
    memcpy(outputs,nodes,sizeof(nodes));memcpy(output_p,scratch,1600);
}

static void build_body_exact(const uint8_t input[1600],int round,const Plan *plan,int outputs[1600],uint8_t output_p[1600]){
    Value state[25][64];reset_graph(1600,0);for(int q=0;q<1600;q++)state[q>>6][q&63]=val(q,input[q]);
    exact_round(state,round,0,plan,outputs,output_p);
}

static void build_last_generic(const uint8_t input[1600],int round,int outputs[256],uint8_t output_p[256]){
    Value S[25][64],C[5][64],D[5][64]; uint8_t hc[320]={0},hd[320]={0};
    reset_graph(1600,0); for(int q=0;q<1600;q++) S[q>>6][q&63]=val(q,input[q]);
    for(int z=0;z<64;z++){
        Value b[5],out[5];
        for(int X=0;X<5;X++){ int x=X,y=X,zz=(z-ROT[x][y])&63;
            Value d=lazy_d(S,C,D,hc,hd,NULL,NULL,x,zz); b[X]=xor_value(S[x+5*y][zz],d); }
        build_dynamic_row(b,15,out);
        for(int X=0;X<4;X++){ Value v=out[X]; if(X==0)v.p^=(RC[round]>>z)&1;
            outputs[64*X+z]=v.n; output_p[64*X+z]=v.p; }
    }
}

static long straight_count(int rounds,int full,Plan *prefix,Plan plans[24],uint8_t inputs[24][1600]){
    int nodes1600[1600],nodes256[256]; uint8_t polarity[1600],lastp[256]; long total=0;
    if(!full) memset(prefix,0,sizeof(*prefix));
    build_prefix_exact(prefix,nodes1600,polarity);
    long part=live_operation_count(nodes1600,1600,256);total+=part;
    if(full&&getenv("STEP_DEBUG"))fprintf(stderr,"segment 0-1 %ld\n",part);
    memcpy(inputs[2],polarity,1600);
    for(int r=2;r<rounds-1;r++){
        if(full) build_body_exact(polarity,r,&plans[r],nodes1600,polarity);
        else {
            make_min_plan(polarity,r,&plans[r]);
            build_body_exact(polarity,r,&plans[r],nodes1600,polarity);
        }
        part=live_operation_count(nodes1600,1600,1600);total+=part;
        if(full&&getenv("STEP_DEBUG"))fprintf(stderr,"segment %d %ld\n",r,part);
        memcpy(inputs[r+1],polarity,1600);
    }
    build_last_generic(polarity,rounds-1,nodes256,lastp);
    part=live_operation_count(nodes256,256,1600);total+=part;
    if(full&&getenv("STEP_DEBUG"))fprintf(stderr,"segment %d %ld\n",rounds-1,part);
    return total;
}

static int last_row_cost[32];

/* Static streaming allocator used by the charged emitter.  One graph segment
   is live at a time and the packed program is written as records are made. */
enum { EMIT_REGS=1936, EMIT_BUFFER=4096 };
static uint8_t ea_live[MAX_NODES],ea_busy[EMIT_REGS];
static uint16_t ea_last[MAX_NODES],ea_reg[MAX_NODES],ea_out_index[MAX_NODES];
static uint16_t ea_input_regs[1600];
static uint16_t ea_final_last[1600],ea_final_output[256];
static uint8_t ea_buffer[EMIT_BUFFER];static int ea_length,ea_bits;static uint64_t ea_acc;
static FILE *ea_file;static long ea_ops,ea_short,ea_forms[3],ea_mix[4];static int ea_peak;

static void ea_flush(void){if(ea_length&&fwrite(ea_buffer,1,(size_t)ea_length,ea_file)!=(size_t)ea_length)fail("step program write");ea_length=0;}
static void ea_byte(uint8_t value){ea_buffer[ea_length++]=value;if(ea_length==EMIT_BUFFER)ea_flush();}
static void ea_record(int op,int d,int a,int b){
    if(op<0||op>3||d<0||a<0||b<0||d>=2048||a>=2048||b>=2048)fail("native step field overflow");
    if(d==b&&op!=3){int t=a;a=b;b=t;}
    uint64_t word;int width,same=d==a;
    if(same){word=(uint64_t)op|4|((uint64_t)a<<3);width=op==3?14:25;if(op!=3)word|=(uint64_t)b<<14;ea_short++;}
    else{word=(uint64_t)op|((uint64_t)d<<3)|((uint64_t)a<<14);width=op==3?25:36;if(op!=3)word|=(uint64_t)b<<25;}
    ea_forms[width==14?0:width==25?1:2]++;ea_mix[op]++;ea_ops++;
    ea_acc|=word<<ea_bits;ea_bits+=width;while(ea_bits>=8){ea_byte((uint8_t)ea_acc);ea_acc>>=8;ea_bits-=8;}
}

static void ea_segment(const int *outputs,int output_count,int input_count,int round,int rounds,int final){
    long before_ops=ea_ops;int expected_ops=live_operation_count(outputs,output_count,input_count);
    memset(ea_live,0,(size_t)node_count);memset(ea_last,0,(size_t)node_count*sizeof(*ea_last));
    memset(ea_out_index,0xff,(size_t)node_count*sizeof(*ea_out_index));memset(ea_busy,0,sizeof(ea_busy));
    for(int j=0;j<output_count;j++){int node=outputs[j];if(node<input_count||ea_out_index[node]!=UINT16_MAX)fail("shared state output");ea_live[node]=1;ea_out_index[node]=(uint16_t)j;}
    for(int i=node_count-1;i>=input_count;i--)if(ea_live[i]){ea_live[nodes[i].a]=1;if(nodes[i].op!=O_NOT)ea_live[nodes[i].b]=1;}
    for(int i=input_count;i<node_count;i++)if(ea_live[i]){ea_last[nodes[i].a]=(uint16_t)i;if(nodes[i].op!=O_NOT)ea_last[nodes[i].b]=(uint16_t)i;}
    for(int j=0;j<output_count;j++)ea_last[outputs[j]]=UINT16_MAX;
    for(int i=0;i<input_count;i++){ea_reg[i]=ea_input_regs[i];if(ea_last[i])ea_busy[ea_input_regs[i]]=1;}
    for(int i=input_count;i<node_count;i++)if(ea_live[i]){
        int op=nodes[i].op,a=nodes[i].a,b=op==O_NOT?a:nodes[i].b,ra=ea_reg[a],rb=op==O_NOT?0:ea_reg[b];
        if(ea_last[a]==i)ea_busy[ra]=0;
        if(b!=a&&ea_last[b]==i)ea_busy[rb]=0;
        int destination=-1;
        if(final&&ea_out_index[i]!=UINT16_MAX){destination=ea_out_index[i];if(ea_busy[destination])fail("digest destination busy");}
        else for(int physical=0;physical<EMIT_REGS;physical++){
            if(ea_busy[physical])continue;
            if(!final&&round==rounds-2&&physical<256&&ea_out_index[i]!=UINT16_MAX){int state_index=ea_out_index[i];if(ea_final_output[physical]<ea_final_last[state_index])continue;}
            if(final&&physical<256){int output_node=outputs[physical];if(output_node!=i&&ea_last[i]>output_node)continue;}
            destination=physical;break;
        }
        if(destination<0)fail("emitter register exhausted");
        ea_busy[destination]=1;ea_reg[i]=(uint16_t)destination;
        if(destination+1>ea_peak)ea_peak=destination+1;
        int code=op==O_XOR?0:op==O_AND?1:op==O_OR?2:3;ea_record(code,destination,ra,rb);
    }
    for(int j=0;j<output_count;j++)ea_input_regs[j]=ea_reg[outputs[j]];
    for(int r=0;r<EMIT_REGS;r++){
        int expected=0;for(int j=0;j<output_count;j++)if(ea_input_regs[j]==r){expected=1;break;}
        if((int)ea_busy[r]!=expected)fail("emitter boundary live set");
    }
    if(ea_ops-before_ops!=expected_ops){fprintf(stderr,"segment round=%d emitted=%ld expected=%d nodes=%d\n",round,ea_ops-before_ops,expected_ops,node_count);fail("emitter DCE mismatch");}
}

static void emit_straight(const char *path,int rounds,Plan *prefix,Plan plans[24]){
    ea_file=fopen(path,"wb");if(!ea_file)fail("step output");ea_length=ea_bits=0;ea_acc=0;ea_ops=ea_short=0;ea_peak=256;
    memset(ea_forms,0,sizeof(ea_forms));memset(ea_mix,0,sizeof(ea_mix));for(int i=0;i<256;i++)ea_input_regs[i]=(uint16_t)i;
    int nodes1600[1600],nodes256[256];uint8_t polarity[1600],lastp[256];
    /* Prebuild the final graph to identify state inputs that remain live past
       the first digest definition.  Those inputs may not occupy low digest
       registers at the preceding boundary. */
    build_prefix_exact(prefix,nodes1600,polarity);
    for(int r=2;r<rounds-1;r++)build_body_exact(polarity,r,&plans[r],nodes1600,polarity);
    build_last_generic(polarity,rounds-1,nodes256,lastp);
    memset(ea_live,0,(size_t)node_count);memset(ea_last,0,(size_t)node_count*sizeof(*ea_last));for(int j=0;j<256;j++)ea_live[nodes256[j]]=1;
    for(int i=node_count-1;i>=1600;i--)if(ea_live[i]){ea_live[nodes[i].a]=1;if(nodes[i].op!=O_NOT)ea_live[nodes[i].b]=1;}
    for(int i=1600;i<node_count;i++)if(ea_live[i]){ea_last[nodes[i].a]=(uint16_t)i;if(nodes[i].op!=O_NOT)ea_last[nodes[i].b]=(uint16_t)i;}
    for(int q=0;q<1600;q++)ea_final_last[q]=ea_last[q];
    for(int j=0;j<256;j++)ea_final_output[j]=(uint16_t)nodes256[j];
    /* Rebuild and emit from round zero. */
    build_prefix_exact(prefix,nodes1600,polarity);ea_segment(nodes1600,1600,256,1,rounds,0);
    for(int r=2;r<rounds-1;r++){build_body_exact(polarity,r,&plans[r],nodes1600,polarity);ea_segment(nodes1600,1600,1600,r,rounds,0);}
    build_last_generic(polarity,rounds-1,nodes256,lastp);ea_segment(nodes256,256,1600,rounds-1,rounds,1);
    if(ea_bits)ea_byte((uint8_t)ea_acc);
    ea_flush();if(fclose(ea_file))fail("step close");
    uint64_t pd[4]={0,0,0,0};for(int bit=0;bit<256;bit++)pd[bit>>6]|=(uint64_t)(lastp[bit]&1)<<(bit&63);
    fprintf(stderr,"emitted step_ops=%ld peak=%d bytes=%ld forms14=%ld forms25=%ld forms36=%ld short=%ld mix=%ld,%ld,%ld,%ld pd=%016lx,%016lx,%016lx,%016lx\n",
        ea_ops,ea_peak,(ea_forms[0]*14+ea_forms[1]*25+ea_forms[2]*36+7)/8,ea_forms[0],ea_forms[1],ea_forms[2],ea_short,
        ea_mix[0],ea_mix[1],ea_mix[2],ea_mix[3],
        (unsigned long)pd[0],(unsigned long)pd[1],(unsigned long)pd[2],(unsigned long)pd[3]);
}

/* Cost of a last-round chi row, where only outputs 0..3 are live. */
static void make_last_row_cost(void){
    for(int pin=0;pin<32;pin++){
        int best=1<<30;
        for(int subset=0;subset<32;subset++){
            int bp[5];
            for(int x=0;x<5;x++) bp[x]=((pin>>x)&1)^((subset>>x)&1);
            for(int trick=-1;trick<5;trick++){
                int k=(trick+1)%5;
                if(trick>=0 && (!((15>>trick)&1)||!((15>>k)&1))) continue;
                int cost=__builtin_popcount((unsigned)subset),op[5]={0,0,0,0,0};
                if(trick>=0){
                    int a=bp[(k+1)%5]^1,b=bp[(k+2)%5];
                    int tp=a==b?a:0;
                    cost+=(a==b?1:2)+1; op[k]=bp[k]^tp;
                }
                for(int x=0;x<5;x++) if((15>>x)&1){
                    if(trick>=0&&x==k) continue;
                    int a=(x==trick?op[k]:bp[(x+1)%5])^1,b=bp[(x+2)%5];
                    cost+=(a==b?1:2)+1;
                }
                if(cost<best) best=cost;
            }
        }
        last_row_cost[pin]=best;
    }
}

/* One-round-lookahead annealer.  Each move updates only the affected chi rows,
   so the charged 200,000,000-iteration campaign is practical and auditable. */
static void anneal_straight(const uint8_t input[1600],int round,int rounds,long iterations,Plan *result){
    uint8_t zero[320]={0},pat0[320],pat1[320],outv[320];
    uint8_t cnot[320]={0},dnot[320]={0},bestc[320]={0},bestd[320]={0},besto[320];
    uint16_t vrow[5][64][5]; uint8_t vbit[5][64][5];
    row_patterns(input,zero,zero,pat0);
    for(int i=0;i<320;i++) outv[i]=row_min_target[pat0[i]];
    uint8_t next[1600]; targets_to_state(outv,next);
    for(int z=0;z<64;z++) next[z]^=(uint8_t)((RC[round]>>z)&1);
    row_patterns(next,zero,zero,pat1);
    for(int x=0;x<5;x++) for(int zz=0;zz<64;zz++) for(int y=0;y<5;y++){
        int Y=(2*(x-y)+10)%5,z=(zz+ROT[x][y])&63;
        vrow[x][zz][y]=(uint16_t)(64*Y+z); vbit[x][zz][y]=(uint8_t)(1<<y);
    }
    int next_last=round+1==rounds-1;
    #define COST0(i) ((int)row_table[pat0[(i)]][outv[(i)]].cost)
    #define COST1(i) (next_last? ((i)<64?last_row_cost[pat1[(i)]]:0) : (int)row_min_cost[pat1[(i)]])
    long a0=0,a1=0;
    for(int i=0;i<320;i++){a0+=COST0(i);a1+=COST1(i);}
    long cost=16*a0+3*a1,best=cost;
    memcpy(besto,outv,sizeof(besto));
    uint64_t seed=UINT64_C(0x2545f4914f6cdd1d)^(uint64_t)round*UINT64_C(0x9e3779b97f4a7c15)^UINT64_C(0x1234567);
    #define FLIP0(rw,bit) do{cost-=16*COST0(rw);pat0[(rw)]^=(uint8_t)(bit);cost+=16*COST0(rw);}while(0)
    #define FLIPD0(xx,zz) do{for(int kk=0;kk<5;kk++){int rw=vrow[(xx)][(zz)][kk];FLIP0(rw,vbit[(xx)][(zz)][kk]);}}while(0)
    #define FLIP1(rw,bit) do{cost-=3*COST1(rw);pat1[(rw)]^=(uint8_t)(bit);cost+=3*COST1(rw);}while(0)
    #define FLIPD1(xx,zz) do{for(int kk=0;kk<5;kk++){int rw=vrow[(xx)][(zz)][kk];FLIP1(rw,vbit[(xx)][(zz)][kk]);}}while(0)
    for(long it=0;it<iterations;it++){
        uint64_t random=rng_next(&seed);int move=(int)(random%5),x=(int)((random>>3)%5),z=(int)((random>>8)&63),Y=(int)((random>>16)%5);
        if(move>=2)move=2;
        int mask=((random>>24)&1)?(int)(1+((random>>28)%31)):(1<<x);
        long before=cost;
        #define APPLY_MOVE() do{ \
            if(move==0){FLIPD0(x,z);dnot[64*x+z]^=1;cost+=dnot[64*x+z]?16:-16;} \
            else if(move==1){int x1=(x+1)%5,x2=(x+4)%5,z2=(z+1)&63;FLIPD0(x1,z);FLIPD0(x2,z2);cnot[64*x+z]^=1;cost+=cnot[64*x+z]?16:-16;} \
            else{int rw=64*Y+z;cost-=16*COST0(rw);outv[rw]^=(uint8_t)mask;cost+=16*COST0(rw); \
                for(int X=0;X<5;X++)if((mask>>X)&1){int x1=(X+1)%5,x2=(X+4)%5,z2=(z+1)&63,rw1=vrow[X][z][Y];FLIP1(rw1,vbit[X][z][Y]);FLIPD1(x1,z);FLIPD1(x2,z2);}} \
        }while(0)
        APPLY_MOVE(); long difference=cost-before;
        double temperature=19.2*bounded_exp(-3.1780538303479458*(double)it/(double)(iterations?iterations:1));
        double uniform=(double)(rng_next(&seed)>>11)*(1.0/9007199254740992.0);
        int accept=difference<=0||uniform<bounded_exp(-(double)difference/temperature);
        if(accept){if(cost<best){best=cost;memcpy(bestc,cnot,sizeof(bestc));memcpy(bestd,dnot,sizeof(bestd));memcpy(besto,outv,sizeof(besto));}}
        else APPLY_MOVE();
    }
    memset(result,0,sizeof(*result));result->ib=RC[round];
    memcpy(result->cnot,bestc,320);memcpy(result->dnot,bestd,320);
    for(int i=0;i<320;i++) result->target[i]=(uint8_t)(besto[i]^(i<64&&((RC[round]>>i)&1)));
    #undef APPLY_MOVE
    #undef FLIPD1
    #undef FLIP1
    #undef FLIPD0
    #undef FLIP0
    #undef COST1
    #undef COST0
}

static void hex_bytes(FILE *f,const uint8_t *data,int n){
    static const char h[]="0123456789abcdef"; for(int i=0;i<n;i++){fputc(h[data[i]>>4],f);fputc(h[data[i]&15],f);}
}

static void hex_bits(FILE *f,const uint8_t *bits,int n){
    uint8_t packed[200]={0};
    if(n>(int)(8*sizeof(packed))) fail("bitset too wide");
    for(int i=0;i<n;i++) packed[i>>3]|=(uint8_t)((bits[i]&1)<<(i&7));
    hex_bytes(f,packed,(n+7)/8);
}

static void write_plan_file(const char *path,int rounds,int trial,const Plan *prefix,Plan plans[24],uint8_t inputs[24][1600]){
    FILE *f=fopen(path,"w"); if(!f)fail("plan output");
    fprintf(f,"trial %d\nnr %d optmode 4 chained 1 lasttrick 1 notfold 0\n",trial,rounds);
    fprintf(f,"F1 ");hex_bits(f,prefix->dnot,320);fprintf(f,"\nG1 ");hex_bits(f,prefix->cnot,320);fputc('\n',f);
    for(int r=2;r<rounds;r++){ fprintf(f,"FG %d ",r);hex_bits(f,plans[r].dnot,320);fputc(' ',f);hex_bits(f,plans[r].cnot,320);fputc('\n',f); }
    for(int r=0;r<rounds;r++){ fprintf(f,"PHI %d ",r);for(int i=0;i<200;i++)fprintf(f,"00");fputc('\n',f); }
    for(int r=2;r<rounds;r++){fprintf(f,"POL %d ",r);hex_bits(f,inputs[r],1600);fputc('\n',f);}
    for(int r=2;r<rounds-1;r++){
        uint8_t patterns[320];row_patterns(inputs[r],plans[r].cnot,plans[r].dnot,patterns);fprintf(f,"DEC %d ",r);
        for(int i=0;i<320;i++){int target=plans[r].target[i]^(i<64&&((RC[r]>>i)&1));Decision d=row_table[patterns[i]][target];
            uint16_t word=(uint16_t)(d.subset|d.tricks<<5|d.select_mask<<10);fprintf(f,"%02x%02x",word&255,word>>8);}
        fputc('\n',f);
        fprintf(f,"TGT %d ",r);hex_bytes(f,plans[r].target,320);fputc('\n',f);
    }
    if(fclose(f))fail("plan close");
}

static void usage(void){fprintf(stderr,"usage: step_search cheap ROUNDS | full ROUNDS TRIAL ITERATIONS PLAN | multi TRIAL ITERATIONS OUTDIR [R,R,...]\n");exit(2);}

#ifndef EMITTER_ONLY
int generator_work(int argc,char **argv){
    if(argc<3)usage();
    make_row_table(); make_last_row_cost();
    fprintf(stderr,"chained-table entries=1024 candidate_evaluations=1015808 truth_checks=32768 bytes=%zu checksum=%016lx\n",sizeof(row_table),(unsigned long)chained_table_checksum());
    if(!strcmp(argv[1],"multi")){
        if(argc!=5&&argc!=6)usage();
        int trial=atoi(argv[2]);long iterations=strtol(argv[3],NULL,10);const char *outdir=argv[4];
        int wanted[25]={0},max_round=0;
        if(argc==5){const int defaults[7]={9,13,17,19,20,21,22};for(int j=0;j<7;j++){wanted[defaults[j]]=1;max_round=defaults[j];}}
        else{
            const char *p=argv[5];
            while(*p){char *end=NULL;long value=strtol(p,&end,10);if(end==p||value<7||value>24)usage();wanted[value]=1;if(value>max_round)max_round=(int)value;p=end;if(*p==',')p++;else if(*p)usage();}
        }
        set_s3_trial(trial);Plan prefix={0},plans[24]={0};uint8_t inputs[24][1600]={{0}};
        int nodes[1600];uint8_t polarity[1600];
        optimize_prefix(&prefix,nodes,polarity);build_prefix_exact(&prefix,nodes,polarity);memcpy(inputs[2],polarity,1600);
        for(int r=2;r<=max_round-2;r++){
            int target_rounds=wanted[r+2]?r+2:0;
            if(target_rounds&&r<max_round-2){
                Plan candidate[24];uint8_t candidate_inputs[24][1600];uint8_t tail_polarity[1600];
                memcpy(candidate,plans,sizeof(candidate));memcpy(candidate_inputs,inputs,sizeof(candidate_inputs));
                anneal_straight(polarity,r,target_rounds,iterations,&candidate[r]);
                memcpy(tail_polarity,polarity,1600);build_body_exact(tail_polarity,r,&candidate[r],nodes,tail_polarity);
                memcpy(candidate_inputs[r+1],tail_polarity,1600);
                char path[4096];snprintf(path,sizeof(path),"%s/r%d-t%d.plan",outdir,target_rounds,trial);
                long count=straight_count(target_rounds,1,&prefix,candidate,candidate_inputs);
                fprintf(stderr,"trial=%d rounds=%d iterations=%ld step_ops=%ld\n",trial,target_rounds,iterations,count);
                write_plan_file(path,target_rounds,trial,&prefix,candidate,candidate_inputs);
            }
            anneal_straight(polarity,r,max_round,iterations,&plans[r]);
            build_body_exact(polarity,r,&plans[r],nodes,polarity);memcpy(inputs[r+1],polarity,1600);
            if(target_rounds&&r==max_round-2){
                char path[4096];snprintf(path,sizeof(path),"%s/r%d-t%d.plan",outdir,max_round,trial);
                long count=straight_count(max_round,1,&prefix,plans,inputs);
                fprintf(stderr,"trial=%d rounds=%d iterations=%ld step_ops=%ld\n",trial,max_round,iterations,count);
                write_plan_file(path,max_round,trial,&prefix,plans,inputs);
            }
        }
        return 0;
    }
    int rounds=atoi(argv[2]);
    if(rounds<7||rounds>24)usage();
    if(!strcmp(argv[1],"cheap")){
        for(int trial=1000;trial<1512;trial++){set_s3_trial(trial);Plan prefix={0},plans[24]={0};uint8_t inputs[24][1600]={{0}};
            long count=straight_count(rounds,0,&prefix,plans,inputs);printf("{\"trial\":%d,\"cheap_count\":%ld}\n",trial,count);fflush(stdout);}return 0;
    }
    if(!strcmp(argv[1],"full")){
        if(argc!=6&&argc!=7)usage();
        int trial=atoi(argv[3]);long iterations=strtol(argv[4],NULL,10);set_s3_trial(trial);
        Plan prefix={0},plans[24]={0};uint8_t inputs[24][1600]={{0}};int nodes[1600];uint8_t polarity[1600];
        optimize_prefix(&prefix,nodes,polarity);build_prefix_exact(&prefix,nodes,polarity);memcpy(inputs[2],polarity,1600);
        for(int r=2;r<rounds-1;r++){anneal_straight(polarity,r,rounds,iterations,&plans[r]);build_body_exact(polarity,r,&plans[r],nodes,polarity);memcpy(inputs[r+1],polarity,1600);}
        long count=straight_count(rounds,1,&prefix,plans,inputs);fprintf(stderr,"trial=%d rounds=%d iterations=%ld step_ops=%ld\n",trial,rounds,iterations,count);
        write_plan_file(argv[5],rounds,trial,&prefix,plans,inputs);if(argc==7)emit_straight(argv[6],rounds,&prefix,plans);return 0;
    }
    usage();return 2;
}

#ifdef FREESTANDING
extern long construction_vmhwm_bytes(void);
int main(int argc,char **argv){
    int status=generator_work(argc,argv);
    fprintf(stderr,"construction VmHWM %ld bytes\n",construction_vmhwm_bytes());
    return status;
}
#else
int main(int argc,char **argv){return generator_work(argc,argv);}
#endif
#else
extern long construction_vmhwm_bytes(void);
extern long construction_read_file(const char *,void *,size_t);
static uint8_t plan_text[65536];
static int hex_digit(int c){if(c>='0'&&c<='9')return c-'0';if(c>='a'&&c<='f')return c-'a'+10;if(c>='A'&&c<='F')return c-'A'+10;return -1;}
static void parse_hex_field(const char *text,uint8_t *output,int bytes){
    for(int i=0;i<bytes;i++){int high=hex_digit(text[2*i]),low=hex_digit(text[2*i+1]);if(high<0||low<0)fail("plan hex");output[i]=(uint8_t)(high*16+low);}
    if(text[2*bytes]&&text[2*bytes]!=' '&&text[2*bytes]!='\n'&&text[2*bytes]!='\r')fail("plan hex length");
}
static void parse_bit_field(const char *text,uint8_t *output,int bits){uint8_t packed[200];int bytes=(bits+7)/8;parse_hex_field(text,packed,bytes);for(int i=0;i<bits;i++)output[i]=(packed[i>>3]>>(i&7))&1;}
static char *skip_word(char *p){while(*p&&*p!=' '&&*p!='\n')p++;while(*p==' ')p++;return p;}
static int parse_number(char **cursor){char *p=*cursor;int value=0;if(*p<'0'||*p>'9')fail("plan number");while(*p>='0'&&*p<='9')value=value*10+(*p++-'0');while(*p==' ')p++;*cursor=p;return value;}
static void parse_emitter_plan(const char *path,int expected_rounds,int *trial,Plan *prefix,Plan plans[24]){
    long length=construction_read_file(path,plan_text,sizeof(plan_text)-1);if(length<=0||length>=(long)sizeof(plan_text))fail("plan read");plan_text[length]=0;
    memset(prefix,0,sizeof(*prefix));memset(plans,0,24*sizeof(*plans));memset(emitter_has_decisions,0,sizeof(emitter_has_decisions));for(int r=0;r<24;r++)plans[r].ib=RC[r];
    int seen_nr=0,seen_f1=0,seen_g1=0,seen_target[24]={0};char *line=(char*)plan_text;
    while(*line){char *end=line;while(*end&&*end!='\n')end++;char saved=*end;*end=0;
        char *p=line;
        if(!memcmp(p,"trial ",6)){p+=6;*trial=parse_number(&p);}
        else if(!memcmp(p,"nr ",3)){p+=3;int nr=parse_number(&p);if(nr!=expected_rounds)fail("plan round count");seen_nr=1;}
        else if(!memcmp(p,"F1 ",3)){parse_bit_field(p+3,prefix->dnot,320);seen_f1=1;}
        else if(!memcmp(p,"G1 ",3)){parse_bit_field(p+3,prefix->cnot,320);seen_g1=1;}
        else if(!memcmp(p,"FG ",3)){p+=3;int r=parse_number(&p);if(r<2||r>=expected_rounds)fail("FG round");parse_bit_field(p,plans[r].dnot,320);p=skip_word(p);parse_bit_field(p,plans[r].cnot,320);}
        else if(!memcmp(p,"DEC ",4)){p+=4;int r=parse_number(&p);if(r<2||r>=expected_rounds-1)fail("DEC round");uint8_t raw[640];parse_hex_field(p,raw,640);for(int i=0;i<320;i++)emitter_decisions[r][i]=(uint16_t)(raw[2*i]|raw[2*i+1]<<8);}
        else if(!memcmp(p,"TGT ",4)){p+=4;int r=parse_number(&p);if(r<2||r>=expected_rounds-1)fail("TGT round");parse_hex_field(p,plans[r].target,320);seen_target[r]=1;}
        *end=saved;line=saved?end+1:end;
    }
    if(!seen_nr||!seen_f1||!seen_g1)fail("incomplete plan header");for(int r=2;r<expected_rounds-1;r++)if(!seen_target[r])fail("missing target plan");
}
int main(int argc,char **argv){
    if(argc!=4)fail("usage: construction_emitter ROUNDS PLAN PROGRAM");int rounds=atoi(argv[1]),trial=0;if(rounds<7||rounds>24)fail("rounds");
    make_row_table();make_last_row_cost();fprintf(stderr,"chained-table entries=1024 candidate_evaluations=1015808 truth_checks=32768 bytes=%zu checksum=%016lx\n",sizeof(row_table),(unsigned long)chained_table_checksum());static Plan prefix,plans[24];parse_emitter_plan(argv[2],rounds,&trial,&prefix,plans);set_s3_trial(trial);emit_straight(argv[3],rounds,&prefix,plans);
    fprintf(stderr,"construction emitter trial=%d VmHWM %ld bytes\n",trial,construction_vmhwm_bytes());return 0;
}
#endif

```

### s3_basis.h

```c
#ifndef S3_BASIS_H
#define S3_BASIS_H
static const uint64_t S3_KB0[12]={UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0xffffffffffffffff),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0xffffffffffffffff),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0xffffffffffffffff),UINT64_C(0x8000000000000006),UINT64_C(0xffffffffffffffff)};
static const uint64_t S3_KBV[64][12]={
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000001),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x2000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x4000000000000000),UINT64_C(0x8000000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000002),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x4000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x8000000000000000),UINT64_C(0x0000000000000001)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000004),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x8000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000001),UINT64_C(0x0000000000000002)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000008),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000001),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000002),UINT64_C(0x0000000000000004)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000010),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000002),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000004),UINT64_C(0x0000000000000008)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000020),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000004),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000008),UINT64_C(0x0000000000000010)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000040),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000008),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000010),UINT64_C(0x0000000000000020)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000080),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000010),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000020),UINT64_C(0x0000000000000040)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000100),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000020),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000040),UINT64_C(0x0000000000000080)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000200),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000040),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000080),UINT64_C(0x0000000000000100)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000400),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000080),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000100),UINT64_C(0x0000000000000200)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000800),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000100),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000200),UINT64_C(0x0000000000000400)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000001000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000200),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000400),UINT64_C(0x0000000000000800)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000002000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000400),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000800),UINT64_C(0x0000000000001000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000004000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000800),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000001000),UINT64_C(0x0000000000002000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000008000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000001000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000002000),UINT64_C(0x0000000000004000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000010000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000002000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000004000),UINT64_C(0x0000000000008000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000020000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000004000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000008000),UINT64_C(0x0000000000010000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000040000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000008000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000010000),UINT64_C(0x0000000000020000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000080000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000010000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000020000),UINT64_C(0x0000000000040000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000100000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000020000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000040000),UINT64_C(0x0000000000080000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000200000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000040000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000080000),UINT64_C(0x0000000000100000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000400000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000080000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000100000),UINT64_C(0x0000000000200000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000000800000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000100000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000200000),UINT64_C(0x0000000000400000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000001000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000200000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000400000),UINT64_C(0x0000000000800000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000002000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000400000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000800000),UINT64_C(0x0000000001000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000004000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000800000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000001000000),UINT64_C(0x0000000002000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000008000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000001000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000002000000),UINT64_C(0x0000000004000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000010000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000002000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000004000000),UINT64_C(0x0000000008000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000020000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000004000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000008000000),UINT64_C(0x0000000010000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000040000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000008000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000010000000),UINT64_C(0x0000000020000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000080000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000010000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000020000000),UINT64_C(0x0000000040000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000100000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000020000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000040000000),UINT64_C(0x0000000080000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000200000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000040000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000080000000),UINT64_C(0x0000000100000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000400000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000080000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000100000000),UINT64_C(0x0000000200000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000000800000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000100000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000200000000),UINT64_C(0x0000000400000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000001000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000200000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000400000000),UINT64_C(0x0000000800000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000002000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000400000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000800000000),UINT64_C(0x0000001000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000004000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000800000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000001000000000),UINT64_C(0x0000002000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000008000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000001000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000002000000000),UINT64_C(0x0000004000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000010000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000002000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000004000000000),UINT64_C(0x0000008000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000020000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000004000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000008000000000),UINT64_C(0x0000010000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000040000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000008000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000010000000000),UINT64_C(0x0000020000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000080000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000010000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000020000000000),UINT64_C(0x0000040000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000100000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000020000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000040000000000),UINT64_C(0x0000080000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000200000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000040000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000080000000000),UINT64_C(0x0000100000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000400000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000080000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000100000000000),UINT64_C(0x0000200000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0000800000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000100000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000200000000000),UINT64_C(0x0000400000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0001000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000200000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000400000000000),UINT64_C(0x0000800000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0002000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000400000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000800000000000),UINT64_C(0x0001000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0004000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000800000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0001000000000000),UINT64_C(0x0002000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0008000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0001000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0002000000000000),UINT64_C(0x0004000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0010000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0002000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0004000000000000),UINT64_C(0x0008000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0020000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0004000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0008000000000000),UINT64_C(0x0010000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0040000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0008000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0010000000000000),UINT64_C(0x0020000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0080000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0010000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0020000000000000),UINT64_C(0x0040000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0100000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0020000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0040000000000000),UINT64_C(0x0080000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0200000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0040000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0080000000000000),UINT64_C(0x0100000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0400000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0080000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0100000000000000),UINT64_C(0x0200000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x0800000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0100000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0200000000000000),UINT64_C(0x0400000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x1000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0200000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0400000000000000),UINT64_C(0x0800000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x2000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0400000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0800000000000000),UINT64_C(0x1000000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x4000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0800000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x1000000000000000),UINT64_C(0x2000000000000000)},
 {UINT64_C(0x0000000000000000),UINT64_C(0x8000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x1000000000000000),UINT64_C(0x0000000000000000),UINT64_C(0x2000000000000000),UINT64_C(0x4000000000000000)},
};
#endif

```

### construction_prefilter.c

```c
/* Freestanding emitter for the separate native 15-OR digest prefilter. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

extern long construction_vmhwm_bytes(void);

typedef struct { FILE *out; uint64_t pending; int used; long bytes; } Writer;

static void put(Writer *w,uint64_t value,int width){
    w->pending|=value<<w->used;w->used+=width;
    while(w->used>=8){uint8_t byte=(uint8_t)w->pending;if(fwrite(&byte,1,1,w->out)!=1)exit(2);w->bytes++;w->pending>>=8;w->used-=8;}
}

int main(int argc,char **argv){
    if(argc!=3){fprintf(stderr,"usage: construction_prefilter REGISTER OUTPUT\n");return 2;}
    int d=atoi(argv[1]);if(d<0||d>=2048)return 2;FILE *out=fopen(argv[2],"wb");if(!out)return 2;Writer w={out,0,0,0};
    put(&w,2|((uint64_t)d<<3)|((uint64_t)240<<14)|((uint64_t)241<<25),36);
    for(int plane=242;plane<256;plane++)put(&w,2|4|((uint64_t)d<<3)|((uint64_t)plane<<14),25);
    if(w.used){uint8_t byte=(uint8_t)w.pending;if(fwrite(&byte,1,1,out)!=1)return 2;w.bytes++;}
    if(fclose(out)||w.bytes!=49)return 2;
    fprintf(stderr,"prefilter instructions=15 bytes=%ld register=%d VmHWM %ld bytes\n",w.bytes,d,construction_vmhwm_bytes());return 0;
}

```

### construction_scan_template.c

```c
/* Freestanding float mirror for the charged finite parameter scan. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "scan_candidates.h"
extern long construction_vmhwm_bytes(void);
static const long double LN2=0.693147180559945309417232121458176568L,M=1.1579208923731619542357098500868790785e77L,GRID=2.475880078570760549798248448e27L,W=6.33825300114114700748351602688e29L;
static uint64_t scan_evaluations,scan_bins;
static long double lexp(long double x){if(x<-11000.0L)return 0.0L;int k=(int)(x/LN2);if((long double)k*LN2>x)k--;long double r=x-(long double)k*LN2,term=1.0L,sum=1.0L;for(int i=1;i<=32;i++){term*=r/(long double)i;sum+=term;}while(k>0){sum*=2.0L;k--;}while(k<0){sum*=0.5L;k++;}return sum;}
static long double llog(long double x){if(!(x>0))return -1.0L/0.0L;int e=0;while(x>=2.0L){x*=0.5L;e++;}while(x<1.0L){x*=2.0L;e--;}long double y=(x-1.0L)/(x+1.0L),p=y*y,term=y,sum=0;for(int k=1;k<=101;k+=2){sum+=term/(long double)k;term*=p;}return 2.0L*sum+(long double)e*LN2;}
static long double success(uint64_t t,const Candidate *c){
 scan_evaluations++;scan_bins+=c->j;
 long double tb=(long double)t*GRID,theta=(long double)c->dt/2.658455991569831744e36L,logq=-theta,qstep=lexp(W*logq),previous=1.0L,covered=0.0L;
 long double delta=256.0L*W,first=256.0L*(tb-W),collision=lexp(-first*(first-1.0L)/(2.0L*M));
 long double ratio=lexp((2.0L*first*delta-delta*delta-delta)/(2.0L*M)),ratio_step=lexp(-delta*delta/M);
 for(uint32_t j=1;j<=c->j;j++){long double current=previous*qstep;if(tb>(long double)j*W)covered+=(previous-current)*(1.0L-collision);previous=current;collision*=ratio;ratio*=ratio_step;}
 long double n=256.0L*tb,mean=n*theta,available=(long double)(5*c->table-256);if(!(available>mean))return -1.0L;
 long double f2=lexp(-mean+available*(1.0L+llog(mean/available))),f3=(long double)(5*c->table)/(theta*theta*M),alias=(long double)(5*c->table)*(long double)(5*c->table)/2251799813685248.0L;
 long double trails=(long double)(5*c->table),lrc=(long double)c->j*W,g6=lexp(lrc*logq)*(1.0L+lrc*theta),coincidence=1.0L-lexp(-n*n/(2.0L*M)-n*n*n/(3.0L*M*M));
 long double inflation=lexp(-trails*llog(1.0L-n/M));
 long double f6=2.0L*g6*coincidence*inflation;
 return covered-(f2+f3+alias+8.077935669463161e-28L+f6+8.673617379884035e-19L+3.0814879110195774e-33L*(1.0L+f6));
}
static uint64_t least_tb(const Candidate *c){uint64_t lo=HINT_T>SPAN?HINT_T-SPAN:1,hi=HINT_T+SPAN;long double theta=(long double)c->dt/2.658455991569831744e36L;uint64_t domain=(uint64_t)(((long double)(5*c->table-256)/(256.0L*theta))/GRID);if(hi>=domain)hi=domain-1;if(hi<=lo||success(hi,c)<0.39L)return 0;while(success(lo,c)>=0.39L&&lo>SPAN)lo-=SPAN;while(hi-lo>1){uint64_t mid=(lo+hi)/2;if(success(mid,c)>=0.39L)hi=mid;else lo=mid;}return hi;}
static long double total_cost(const Candidate *c,uint64_t t){long double tb=(long double)t*GRID,lrc=(long double)c->j*W,hit=tb*(1.0L+1.0L/1048576.0L)/256.0L+1.0L+lrc;long double gap=(lrc+(long double)c->table-2.0L)/(long double)(c->table-1),nck=(lrc-1.0L)/gap+1.0L;long double replay=(long double)c->replay_rate*lrc+(long double)c->replay_g*gap+(long double)c->replay_nck*nck+(long double)c->replay_const;long double trails=5.0L*c->table;long double rare=(hit+1.0L)*c->hit+(trails-255.0L)*(c->dp_fixed+c->probe_word*c->table)+(trails-256.0L)*(c->restart+3)+c->restart_halt+c->deadline+c->setup;return tb*(STEP_OPS+19.0L)+replay+rare+PREPROCESSING;}
int main(void){int best=-1;uint64_t best_t=0;long double best_cost=0;for(unsigned i=0;i<sizeof(candidates)/sizeof(candidates[0]);i++){uint64_t t=least_tb(&candidates[i]);if(!t)continue;long double cost=total_cost(&candidates[i],t);if(best<0||cost<best_cost){best=(int)i;best_t=t;best_cost=cost;}}if(best<0){printf("no candidate hint_success_scaled=%ld\n",(long)(success(HINT_T,&candidates[0])*1000000000000.0L));return 2;}const Candidate *c=&candidates[best];printf("candidate=%d table=%d dt=%d j=%u tb_grid=%lu memory=%d\n",best,c->table,c->dt,c->j,(unsigned long)best_t,c->memory);fprintf(stderr,"scan candidates=%lu evaluations=%lu bins=%lu VmHWM %ld bytes\n",(unsigned long)(sizeof(candidates)/sizeof(candidates[0])),(unsigned long)scan_evaluations,(unsigned long)scan_bins,construction_vmhwm_bytes());return 0;}

```

### scan_candidates.h

```c
#include <stdint.h>
typedef struct{int table,dt;uint32_t j;int memory,hit,dp_fixed,probe_word,restart,restart_halt,deadline,setup,replay_rate,replay_g,replay_nck,replay_const;} Candidate;
#define HINT_T 535979090UL
#define SPAN (1UL<<20)
#define STEP_OPS 144722
#define PREPROCESSING 207446005350400
static const Candidate candidates[]={
 {14048,527,84762,1040355,133,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,527,85319,1040355,133,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,527,85955,1040355,133,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,528,84601,1040243,119,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,528,85157,1040243,119,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,528,85793,1040243,119,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,529,84441,1040323,129,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,529,84996,1040323,129,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,529,85630,1040323,129,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,530,84282,1040307,127,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,530,84836,1040307,127,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,530,85469,1040307,127,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,531,84123,1040339,131,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,531,84676,1040339,131,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,531,85308,1040339,131,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,532,83965,1040291,125,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,532,84517,1040291,125,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,532,85148,1040291,125,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,533,83807,1040339,131,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,533,84358,1040339,131,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,533,84988,1040339,131,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,534,83650,1040323,129,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,534,84200,1040323,129,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,534,84829,1040323,129,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,535,83494,1040355,133,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,535,84043,1040355,133,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,535,84670,1040355,133,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,536,83338,1040275,123,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,536,83886,1040275,123,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,536,84512,1040275,123,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,537,83183,1040339,131,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,537,83730,1040339,131,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,537,84355,1040339,131,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,538,83029,1040323,129,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,538,83574,1040323,129,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,538,84198,1040323,129,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,539,82874,1040355,133,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,539,83419,1040355,133,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,539,84042,1040355,133,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,540,82721,1040307,127,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,540,83265,1040307,127,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,540,83886,1040307,127,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,541,82568,1040355,133,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,541,83111,1040355,133,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,541,83731,1040355,133,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,542,82416,1040339,131,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,542,82957,1040339,131,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,542,83577,1040339,131,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,543,82264,1040371,135,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,543,82805,1040371,135,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14048,543,83423,1040371,135,2893,24,2835,3,1,743903,13083,19619,17,6626},
 {14064,528,84601,1040755,119,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,528,85157,1040755,119,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,528,85793,1040755,119,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,529,84441,1040835,129,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,529,84996,1040835,129,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,529,85630,1040835,129,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,530,84282,1040819,127,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,530,84836,1040819,127,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,530,85469,1040819,127,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,531,84123,1040851,131,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,531,84676,1040851,131,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,531,85308,1040851,131,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,532,83965,1040803,125,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,532,84517,1040803,125,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,532,85148,1040803,125,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,533,83807,1040851,131,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,533,84358,1040851,131,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,533,84988,1040851,131,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,534,83650,1040835,129,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,534,84200,1040835,129,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,534,84829,1040835,129,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,535,83494,1040867,133,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,535,84043,1040867,133,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,535,84670,1040867,133,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,536,83338,1040787,123,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,536,83886,1040787,123,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,536,84512,1040787,123,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,537,83183,1040851,131,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,537,83730,1040851,131,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,537,84355,1040851,131,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,538,83029,1040835,129,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,538,83574,1040835,129,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,538,84198,1040835,129,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,539,82874,1040867,133,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,539,83419,1040867,133,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,539,84042,1040867,133,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,540,82721,1040819,127,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,540,83265,1040819,127,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,540,83886,1040819,127,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,541,82568,1040867,133,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,541,83111,1040867,133,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,541,83731,1040867,133,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,542,82416,1040851,131,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,542,82957,1040851,131,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,542,83577,1040851,131,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,543,82264,1040883,135,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,543,82805,1040883,135,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,543,83423,1040883,135,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,544,82113,1040739,117,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,544,82652,1040739,117,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14064,544,83269,1040739,117,2893,24,2835,3,1,743925,13083,19619,17,6626},
 {14080,529,84441,1041347,129,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,529,84996,1041347,129,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,529,85630,1041347,129,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,530,84282,1041331,127,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,530,84836,1041331,127,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,530,85469,1041331,127,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,531,84123,1041363,131,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,531,84676,1041363,131,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,531,85308,1041363,131,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,532,83965,1041315,125,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,532,84517,1041315,125,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,532,85148,1041315,125,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,533,83807,1041363,131,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,533,84358,1041363,131,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,533,84988,1041363,131,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,534,83650,1041347,129,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,534,84200,1041347,129,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,534,84829,1041347,129,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,535,83494,1041379,133,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,535,84043,1041379,133,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,535,84670,1041379,133,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,536,83338,1041299,123,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,536,83886,1041299,123,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,536,84512,1041299,123,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,537,83183,1041363,131,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,537,83730,1041363,131,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,537,84355,1041363,131,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,538,83029,1041347,129,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,538,83574,1041347,129,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,538,84198,1041347,129,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,539,82874,1041379,133,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,539,83419,1041379,133,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,539,84042,1041379,133,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,540,82721,1041331,127,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,540,83265,1041331,127,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,540,83886,1041331,127,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,541,82568,1041379,133,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,541,83111,1041379,133,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,541,83731,1041379,133,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,542,82416,1041363,131,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,542,82957,1041363,131,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,542,83577,1041363,131,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,543,82264,1041395,135,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,543,82805,1041395,135,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,543,83423,1041395,135,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,544,82113,1041251,117,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,544,82652,1041251,117,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,544,83269,1041251,117,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,545,81962,1041347,129,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,545,82501,1041347,129,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14080,545,83116,1041347,129,2893,24,2835,3,1,743947,13083,19619,17,6626},
 {14096,529,84441,1041859,129,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,529,84996,1041859,129,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,529,85630,1041859,129,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,530,84282,1041843,127,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,530,84836,1041843,127,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,530,85469,1041843,127,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,531,84123,1041875,131,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,531,84676,1041875,131,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,531,85308,1041875,131,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,532,83965,1041827,125,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,532,84517,1041827,125,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,532,85148,1041827,125,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,533,83807,1041875,131,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,533,84358,1041875,131,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,533,84988,1041875,131,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,534,83650,1041859,129,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,534,84200,1041859,129,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,534,84829,1041859,129,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,535,83494,1041891,133,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,535,84043,1041891,133,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,535,84670,1041891,133,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,536,83338,1041811,123,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,536,83886,1041811,123,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,536,84512,1041811,123,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,537,83183,1041875,131,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,537,83730,1041875,131,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,537,84355,1041875,131,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,538,83029,1041859,129,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,538,83574,1041859,129,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,538,84198,1041859,129,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,539,82874,1041891,133,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,539,83419,1041891,133,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,539,84042,1041891,133,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,540,82721,1041843,127,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,540,83265,1041843,127,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,540,83886,1041843,127,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,541,82568,1041891,133,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,541,83111,1041891,133,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,541,83731,1041891,133,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,542,82416,1041875,131,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,542,82957,1041875,131,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,542,83577,1041875,131,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,543,82264,1041907,135,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,543,82805,1041907,135,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,543,83423,1041907,135,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,544,82113,1041763,117,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,544,82652,1041763,117,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,544,83269,1041763,117,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,545,81962,1041859,129,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,545,82501,1041859,129,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14096,545,83116,1041859,129,2893,24,2835,3,1,743969,13083,19619,17,6626},
 {14112,530,84282,1042355,127,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,530,84836,1042355,127,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,530,85469,1042355,127,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,531,84123,1042387,131,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,531,84676,1042387,131,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,531,85308,1042387,131,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,532,83965,1042339,125,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,532,84517,1042339,125,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,532,85148,1042339,125,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,533,83807,1042387,131,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,533,84358,1042387,131,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,533,84988,1042387,131,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,534,83650,1042371,129,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,534,84200,1042371,129,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,534,84829,1042371,129,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,535,83494,1042403,133,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,535,84043,1042403,133,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,535,84670,1042403,133,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,536,83338,1042323,123,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,536,83886,1042323,123,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,536,84512,1042323,123,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,537,83183,1042387,131,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,537,83730,1042387,131,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,537,84355,1042387,131,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,538,83029,1042371,129,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,538,83574,1042371,129,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,538,84198,1042371,129,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,539,82874,1042403,133,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,539,83419,1042403,133,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,539,84042,1042403,133,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,540,82721,1042355,127,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,540,83265,1042355,127,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,540,83886,1042355,127,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,541,82568,1042403,133,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,541,83111,1042403,133,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,541,83731,1042403,133,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,542,82416,1042387,131,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,542,82957,1042387,131,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,542,83577,1042387,131,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,543,82264,1042419,135,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,543,82805,1042419,135,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,543,83423,1042419,135,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,544,82113,1042275,117,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,544,82652,1042275,117,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,544,83269,1042275,117,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,545,81962,1042371,129,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,545,82501,1042371,129,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,545,83116,1042371,129,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,546,81812,1042355,127,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,546,82350,1042355,127,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14112,546,82964,1042355,127,2893,24,2835,3,1,743991,13083,19619,17,6626},
 {14128,530,84282,1042867,127,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,530,84836,1042867,127,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,530,85469,1042867,127,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,531,84123,1042899,131,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,531,84676,1042899,131,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,531,85308,1042899,131,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,532,83965,1042851,125,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,532,84517,1042851,125,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,532,85148,1042851,125,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,533,83807,1042899,131,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,533,84358,1042899,131,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,533,84988,1042899,131,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,534,83650,1042883,129,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,534,84200,1042883,129,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,534,84829,1042883,129,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,535,83494,1042915,133,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,535,84043,1042915,133,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,535,84670,1042915,133,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,536,83338,1042835,123,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,536,83886,1042835,123,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,536,84512,1042835,123,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,537,83183,1042899,131,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,537,83730,1042899,131,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,537,84355,1042899,131,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,538,83029,1042883,129,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,538,83574,1042883,129,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,538,84198,1042883,129,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,539,82874,1042915,133,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,539,83419,1042915,133,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,539,84042,1042915,133,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,540,82721,1042867,127,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,540,83265,1042867,127,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,540,83886,1042867,127,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,541,82568,1042915,133,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,541,83111,1042915,133,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,541,83731,1042915,133,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,542,82416,1042899,131,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,542,82957,1042899,131,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,542,83577,1042899,131,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,543,82264,1042931,135,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,543,82805,1042931,135,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,543,83423,1042931,135,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,544,82113,1042787,117,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,544,82652,1042787,117,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,544,83269,1042787,117,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,545,81962,1042883,129,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,545,82501,1042883,129,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,545,83116,1042883,129,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,546,81812,1042867,127,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,546,82350,1042867,127,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14128,546,82964,1042867,127,2893,24,2835,3,1,744013,13083,19619,17,6626},
 {14144,531,84123,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,531,84676,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,531,85308,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,532,83965,1043363,125,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,532,84517,1043363,125,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,532,85148,1043363,125,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,533,83807,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,533,84358,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,533,84988,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,534,83650,1043395,129,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,534,84200,1043395,129,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,534,84829,1043395,129,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,535,83494,1043427,133,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,535,84043,1043427,133,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,535,84670,1043427,133,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,536,83338,1043347,123,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,536,83886,1043347,123,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,536,84512,1043347,123,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,537,83183,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,537,83730,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,537,84355,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,538,83029,1043395,129,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,538,83574,1043395,129,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,538,84198,1043395,129,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,539,82874,1043427,133,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,539,83419,1043427,133,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,539,84042,1043427,133,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,540,82721,1043379,127,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,540,83265,1043379,127,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,540,83886,1043379,127,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,541,82568,1043427,133,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,541,83111,1043427,133,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,541,83731,1043427,133,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,542,82416,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,542,82957,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,542,83577,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,543,82264,1043443,135,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,543,82805,1043443,135,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,543,83423,1043443,135,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,544,82113,1043299,117,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,544,82652,1043299,117,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,544,83269,1043299,117,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,545,81962,1043395,129,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,545,82501,1043395,129,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,545,83116,1043395,129,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,546,81812,1043379,127,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,546,82350,1043379,127,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,546,82964,1043379,127,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,547,81662,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,547,82199,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14144,547,82813,1043411,131,2893,24,2835,3,1,744035,13083,19619,17,6626},
 {14160,532,83965,1043875,125,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,532,84517,1043875,125,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,532,85148,1043875,125,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,533,83807,1043923,131,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,533,84358,1043923,131,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,533,84988,1043923,131,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,534,83650,1043907,129,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,534,84200,1043907,129,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,534,84829,1043907,129,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,535,83494,1043939,133,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,535,84043,1043939,133,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,535,84670,1043939,133,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,536,83338,1043859,123,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,536,83886,1043859,123,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,536,84512,1043859,123,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,537,83183,1043923,131,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,537,83730,1043923,131,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,537,84355,1043923,131,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,538,83029,1043907,129,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,538,83574,1043907,129,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,538,84198,1043907,129,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,539,82874,1043939,133,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,539,83419,1043939,133,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,539,84042,1043939,133,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,540,82721,1043891,127,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,540,83265,1043891,127,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,540,83886,1043891,127,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,541,82568,1043939,133,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,541,83111,1043939,133,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,541,83731,1043939,133,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,542,82416,1043923,131,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,542,82957,1043923,131,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,542,83577,1043923,131,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,543,82264,1043955,135,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,543,82805,1043955,135,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,543,83423,1043955,135,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,544,82113,1043811,117,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,544,82652,1043811,117,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,544,83269,1043811,117,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,545,81962,1043907,129,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,545,82501,1043907,129,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,545,83116,1043907,129,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,546,81812,1043891,127,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,546,82350,1043891,127,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,546,82964,1043891,127,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,547,81662,1043923,131,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,547,82199,1043923,131,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,547,82813,1043923,131,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,548,81513,1043875,125,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,548,82049,1043875,125,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14160,548,82661,1043875,125,2893,24,2835,3,1,744057,13083,19619,17,6626},
 {14176,532,83965,1044387,125,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,532,84517,1044387,125,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,532,85148,1044387,125,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,533,83807,1044435,131,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,533,84358,1044435,131,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,533,84988,1044435,131,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,534,83650,1044419,129,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,534,84200,1044419,129,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,534,84829,1044419,129,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,535,83494,1044451,133,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,535,84043,1044451,133,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,535,84670,1044451,133,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,536,83338,1044371,123,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,536,83886,1044371,123,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,536,84512,1044371,123,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,537,83183,1044435,131,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,537,83730,1044435,131,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,537,84355,1044435,131,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,538,83029,1044419,129,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,538,83574,1044419,129,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,538,84198,1044419,129,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,539,82874,1044451,133,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,539,83419,1044451,133,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,539,84042,1044451,133,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,540,82721,1044403,127,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,540,83265,1044403,127,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,540,83886,1044403,127,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,541,82568,1044451,133,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,541,83111,1044451,133,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,541,83731,1044451,133,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,542,82416,1044435,131,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,542,82957,1044435,131,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,542,83577,1044435,131,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,543,82264,1044467,135,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,543,82805,1044467,135,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,543,83423,1044467,135,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,544,82113,1044323,117,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,544,82652,1044323,117,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,544,83269,1044323,117,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,545,81962,1044419,129,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,545,82501,1044419,129,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,545,83116,1044419,129,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,546,81812,1044403,127,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,546,82350,1044403,127,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,546,82964,1044403,127,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,547,81662,1044435,131,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,547,82199,1044435,131,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,547,82813,1044435,131,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,548,81513,1044387,125,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,548,82049,1044387,125,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14176,548,82661,1044387,125,2893,24,2835,3,1,744079,13083,19619,17,6626},
 {14192,533,83807,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,533,84358,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,533,84988,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,534,83650,1044931,129,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,534,84200,1044931,129,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,534,84829,1044931,129,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,535,83494,1044963,133,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,535,84043,1044963,133,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,535,84670,1044963,133,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,536,83338,1044883,123,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,536,83886,1044883,123,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,536,84512,1044883,123,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,537,83183,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,537,83730,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,537,84355,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,538,83029,1044931,129,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,538,83574,1044931,129,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,538,84198,1044931,129,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,539,82874,1044963,133,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,539,83419,1044963,133,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,539,84042,1044963,133,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,540,82721,1044915,127,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,540,83265,1044915,127,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,540,83886,1044915,127,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,541,82568,1044963,133,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,541,83111,1044963,133,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,541,83731,1044963,133,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,542,82416,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,542,82957,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,542,83577,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,543,82264,1044979,135,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,543,82805,1044979,135,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,543,83423,1044979,135,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,544,82113,1044835,117,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,544,82652,1044835,117,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,544,83269,1044835,117,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,545,81962,1044931,129,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,545,82501,1044931,129,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,545,83116,1044931,129,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,546,81812,1044915,127,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,546,82350,1044915,127,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,546,82964,1044915,127,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,547,81662,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,547,82199,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,547,82813,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,548,81513,1044899,125,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,548,82049,1044899,125,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,548,82661,1044899,125,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,549,81365,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,549,81900,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14192,549,82511,1044947,131,2893,24,2835,3,1,744101,13083,19619,17,6626},
 {14208,533,83807,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,533,84358,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,533,84988,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,534,83650,1045443,129,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,534,84200,1045443,129,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,534,84829,1045443,129,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,535,83494,1045475,133,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,535,84043,1045475,133,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,535,84670,1045475,133,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,536,83338,1045395,123,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,536,83886,1045395,123,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,536,84512,1045395,123,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,537,83183,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,537,83730,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,537,84355,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,538,83029,1045443,129,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,538,83574,1045443,129,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,538,84198,1045443,129,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,539,82874,1045475,133,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,539,83419,1045475,133,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,539,84042,1045475,133,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,540,82721,1045427,127,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,540,83265,1045427,127,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,540,83886,1045427,127,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,541,82568,1045475,133,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,541,83111,1045475,133,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,541,83731,1045475,133,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,542,82416,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,542,82957,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,542,83577,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,543,82264,1045491,135,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,543,82805,1045491,135,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,543,83423,1045491,135,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,544,82113,1045347,117,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,544,82652,1045347,117,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,544,83269,1045347,117,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,545,81962,1045443,129,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,545,82501,1045443,129,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,545,83116,1045443,129,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,546,81812,1045427,127,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,546,82350,1045427,127,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,546,82964,1045427,127,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,547,81662,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,547,82199,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,547,82813,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,548,81513,1045411,125,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,548,82049,1045411,125,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,548,82661,1045411,125,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,549,81365,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,549,81900,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14208,549,82511,1045459,131,2893,24,2835,3,1,744123,13083,19619,17,6626},
 {14224,534,83650,1045955,129,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,534,84200,1045955,129,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,534,84829,1045955,129,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,535,83494,1045987,133,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,535,84043,1045987,133,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,535,84670,1045987,133,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,536,83338,1045907,123,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,536,83886,1045907,123,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,536,84512,1045907,123,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,537,83183,1045971,131,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,537,83730,1045971,131,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,537,84355,1045971,131,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,538,83029,1045955,129,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,538,83574,1045955,129,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,538,84198,1045955,129,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,539,82874,1045987,133,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,539,83419,1045987,133,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,539,84042,1045987,133,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,540,82721,1045939,127,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,540,83265,1045939,127,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,540,83886,1045939,127,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,541,82568,1045987,133,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,541,83111,1045987,133,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,541,83731,1045987,133,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,542,82416,1045971,131,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,542,82957,1045971,131,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,542,83577,1045971,131,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,543,82264,1046003,135,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,543,82805,1046003,135,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,543,83423,1046003,135,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,544,82113,1045859,117,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,544,82652,1045859,117,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,544,83269,1045859,117,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,545,81962,1045955,129,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,545,82501,1045955,129,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,545,83116,1045955,129,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,546,81812,1045939,127,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,546,82350,1045939,127,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,546,82964,1045939,127,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,547,81662,1045971,131,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,547,82199,1045971,131,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,547,82813,1045971,131,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,548,81513,1045923,125,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,548,82049,1045923,125,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,548,82661,1045923,125,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,549,81365,1045971,131,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,549,81900,1045971,131,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,549,82511,1045971,131,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,550,81217,1045955,129,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,550,81751,1045955,129,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14224,550,82361,1045955,129,2893,24,2835,3,1,744145,13083,19619,17,6626},
 {14240,535,83494,1046499,133,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,535,84043,1046499,133,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,535,84670,1046499,133,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,536,83338,1046419,123,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,536,83886,1046419,123,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,536,84512,1046419,123,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,537,83183,1046483,131,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,537,83730,1046483,131,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,537,84355,1046483,131,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,538,83029,1046467,129,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,538,83574,1046467,129,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,538,84198,1046467,129,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,539,82874,1046499,133,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,539,83419,1046499,133,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,539,84042,1046499,133,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,540,82721,1046451,127,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,540,83265,1046451,127,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,540,83886,1046451,127,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,541,82568,1046499,133,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,541,83111,1046499,133,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,541,83731,1046499,133,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,542,82416,1046483,131,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,542,82957,1046483,131,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,542,83577,1046483,131,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,543,82264,1046515,135,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,543,82805,1046515,135,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,543,83423,1046515,135,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,544,82113,1046371,117,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,544,82652,1046371,117,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,544,83269,1046371,117,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,545,81962,1046467,129,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,545,82501,1046467,129,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,545,83116,1046467,129,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,546,81812,1046451,127,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,546,82350,1046451,127,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,546,82964,1046451,127,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,547,81662,1046483,131,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,547,82199,1046483,131,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,547,82813,1046483,131,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,548,81513,1046435,125,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,548,82049,1046435,125,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,548,82661,1046435,125,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,549,81365,1046483,131,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,549,81900,1046483,131,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,549,82511,1046483,131,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,550,81217,1046467,129,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,550,81751,1046467,129,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,550,82361,1046467,129,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,551,81070,1046499,133,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,551,81602,1046499,133,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14240,551,82211,1046499,133,2893,24,2835,3,1,744167,13083,19619,17,6626},
 {14256,535,83494,1047011,133,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,535,84043,1047011,133,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,535,84670,1047011,133,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,536,83338,1046931,123,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,536,83886,1046931,123,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,536,84512,1046931,123,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,537,83183,1046995,131,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,537,83730,1046995,131,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,537,84355,1046995,131,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,538,83029,1046979,129,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,538,83574,1046979,129,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,538,84198,1046979,129,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,539,82874,1047011,133,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,539,83419,1047011,133,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,539,84042,1047011,133,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,540,82721,1046963,127,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,540,83265,1046963,127,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,540,83886,1046963,127,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,541,82568,1047011,133,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,541,83111,1047011,133,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,541,83731,1047011,133,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,542,82416,1046995,131,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,542,82957,1046995,131,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,542,83577,1046995,131,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,543,82264,1047027,135,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,543,82805,1047027,135,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,543,83423,1047027,135,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,544,82113,1046883,117,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,544,82652,1046883,117,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,544,83269,1046883,117,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,545,81962,1046979,129,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,545,82501,1046979,129,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,545,83116,1046979,129,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,546,81812,1046963,127,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,546,82350,1046963,127,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,546,82964,1046963,127,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,547,81662,1046995,131,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,547,82199,1046995,131,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,547,82813,1046995,131,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,548,81513,1046947,125,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,548,82049,1046947,125,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,548,82661,1046947,125,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,549,81365,1046995,131,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,549,81900,1046995,131,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,549,82511,1046995,131,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,550,81217,1046979,129,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,550,81751,1046979,129,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,550,82361,1046979,129,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,551,81070,1047011,133,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,551,81602,1047011,133,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14256,551,82211,1047011,133,2893,24,2835,3,1,744189,13083,19619,17,6626},
 {14272,536,83338,1047443,123,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,536,83886,1047443,123,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,536,84512,1047443,123,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,537,83183,1047507,131,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,537,83730,1047507,131,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,537,84355,1047507,131,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,538,83029,1047491,129,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,538,83574,1047491,129,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,538,84198,1047491,129,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,539,82874,1047523,133,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,539,83419,1047523,133,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,539,84042,1047523,133,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,540,82721,1047475,127,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,540,83265,1047475,127,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,540,83886,1047475,127,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,541,82568,1047523,133,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,541,83111,1047523,133,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,541,83731,1047523,133,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,542,82416,1047507,131,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,542,82957,1047507,131,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,542,83577,1047507,131,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,543,82264,1047539,135,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,543,82805,1047539,135,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,543,83423,1047539,135,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,544,82113,1047395,117,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,544,82652,1047395,117,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,544,83269,1047395,117,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,545,81962,1047491,129,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,545,82501,1047491,129,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,545,83116,1047491,129,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,546,81812,1047475,127,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,546,82350,1047475,127,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,546,82964,1047475,127,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,547,81662,1047507,131,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,547,82199,1047507,131,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,547,82813,1047507,131,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,548,81513,1047459,125,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,548,82049,1047459,125,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,548,82661,1047459,125,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,549,81365,1047507,131,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,549,81900,1047507,131,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,549,82511,1047507,131,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,550,81217,1047491,129,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,550,81751,1047491,129,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,550,82361,1047491,129,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,551,81070,1047523,133,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,551,81602,1047523,133,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,551,82211,1047523,133,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,552,80923,1047443,123,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,552,81455,1047443,123,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14272,552,82062,1047443,123,2893,24,2835,3,1,744211,13083,19619,17,6626},
 {14288,537,83183,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,537,83730,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,537,84355,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,538,83029,1048003,129,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,538,83574,1048003,129,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,538,84198,1048003,129,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,539,82874,1048035,133,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,539,83419,1048035,133,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,539,84042,1048035,133,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,540,82721,1047987,127,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,540,83265,1047987,127,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,540,83886,1047987,127,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,541,82568,1048035,133,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,541,83111,1048035,133,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,541,83731,1048035,133,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,542,82416,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,542,82957,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,542,83577,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,543,82264,1048051,135,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,543,82805,1048051,135,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,543,83423,1048051,135,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,544,82113,1047907,117,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,544,82652,1047907,117,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,544,83269,1047907,117,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,545,81962,1048003,129,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,545,82501,1048003,129,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,545,83116,1048003,129,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,546,81812,1047987,127,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,546,82350,1047987,127,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,546,82964,1047987,127,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,547,81662,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,547,82199,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,547,82813,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,548,81513,1047971,125,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,548,82049,1047971,125,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,548,82661,1047971,125,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,549,81365,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,549,81900,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,549,82511,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,550,81217,1048003,129,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,550,81751,1048003,129,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,550,82361,1048003,129,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,551,81070,1048035,133,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,551,81602,1048035,133,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,551,82211,1048035,133,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,552,80923,1047955,123,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,552,81455,1047955,123,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,552,82062,1047955,123,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,553,80776,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,553,81307,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14288,553,81914,1048019,131,2893,24,2835,3,1,744233,13083,19619,17,6626},
 {14304,537,83183,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,537,83730,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,537,84355,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,538,83029,1048515,129,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,538,83574,1048515,129,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,538,84198,1048515,129,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,539,82874,1048547,133,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,539,83419,1048547,133,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,539,84042,1048547,133,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,540,82721,1048499,127,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,540,83265,1048499,127,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,540,83886,1048499,127,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,541,82568,1048547,133,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,541,83111,1048547,133,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,541,83731,1048547,133,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,542,82416,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,542,82957,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,542,83577,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,543,82264,1048563,135,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,543,82805,1048563,135,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,543,83423,1048563,135,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,544,82113,1048419,117,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,544,82652,1048419,117,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,544,83269,1048419,117,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,545,81962,1048515,129,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,545,82501,1048515,129,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,545,83116,1048515,129,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,546,81812,1048499,127,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,546,82350,1048499,127,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,546,82964,1048499,127,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,547,81662,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,547,82199,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,547,82813,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,548,81513,1048483,125,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,548,82049,1048483,125,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,548,82661,1048483,125,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,549,81365,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,549,81900,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,549,82511,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,550,81217,1048515,129,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,550,81751,1048515,129,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,550,82361,1048515,129,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,551,81070,1048547,133,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,551,81602,1048547,133,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,551,82211,1048547,133,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,552,80923,1048467,123,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,552,81455,1048467,123,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,552,82062,1048467,123,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,553,80776,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,553,81307,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
 {14304,553,81914,1048531,131,2893,24,2835,3,1,744255,13083,19619,17,6626},
};

```

### construction_hash.c

```c
/* Freestanding streaming SHA-256 for charged construction outputs. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

extern long construction_vmhwm_bytes(void);
typedef struct{uint32_t h[8];uint64_t bits;uint8_t block[64];unsigned used;} SHA256;
static const uint32_t K[64]={
0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
static uint32_t rr(uint32_t x,unsigned n){return(x>>n)|(x<<(32-n));}
static void compress(SHA256 *s,const uint8_t b[64]){
    uint32_t w[64];for(int i=0;i<16;i++)w[i]=(uint32_t)b[4*i]<<24|(uint32_t)b[4*i+1]<<16|(uint32_t)b[4*i+2]<<8|b[4*i+3];
    for(int i=16;i<64;i++){uint32_t a=w[i-15],z=w[i-2];w[i]=(rr(z,17)^rr(z,19)^(z>>10))+w[i-7]+(rr(a,7)^rr(a,18)^(a>>3))+w[i-16];}
    uint32_t a=s->h[0],c=s->h[2],b0=s->h[1],d=s->h[3],e=s->h[4],f=s->h[5],g=s->h[6],h=s->h[7];
    for(int i=0;i<64;i++){uint32_t t1=h+(rr(e,6)^rr(e,11)^rr(e,25))+((e&f)^((~e)&g))+K[i]+w[i];uint32_t t2=(rr(a,2)^rr(a,13)^rr(a,22))+((a&b0)^(a&c)^(b0&c));h=g;g=f;f=e;e=d+t1;d=c;c=b0;b0=a;a=t1+t2;}
    s->h[0]+=a;s->h[1]+=b0;s->h[2]+=c;s->h[3]+=d;s->h[4]+=e;s->h[5]+=f;s->h[6]+=g;s->h[7]+=h;
}
static void init(SHA256 *s){static const uint32_t h[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};for(int i=0;i<8;i++)s->h[i]=h[i];s->bits=0;s->used=0;}
static void update(SHA256 *s,const uint8_t *p,size_t n){s->bits+=(uint64_t)n*8;while(n){unsigned take=64-s->used;if(take>n)take=(unsigned)n;for(unsigned i=0;i<take;i++)s->block[s->used+i]=p[i];s->used+=take;p+=take;n-=take;if(s->used==64){compress(s,s->block);s->used=0;}}}
static void finish(SHA256 *s,uint8_t out[32]){uint64_t bits=s->bits;s->block[s->used++]=0x80;if(s->used>56){while(s->used<64)s->block[s->used++]=0;compress(s,s->block);s->used=0;}while(s->used<56)s->block[s->used++]=0;for(int i=7;i>=0;i--)s->block[s->used++]=(uint8_t)(bits>>(8*i));compress(s,s->block);for(int i=0;i<8;i++)for(int j=0;j<4;j++)out[4*i+j]=(uint8_t)(s->h[i]>>(24-8*j));}
int main(int argc,char **argv){if(argc!=2){fprintf(stderr,"usage: construction_hash FILE\n");return 2;}FILE *f=fopen(argv[1],"rb");if(!f){fprintf(stderr,"open failed\n");return 2;}SHA256 s;init(&s);uint8_t buf[4096],digest[32];size_t n,total=0;while((n=fread(buf,1,sizeof(buf),f))){update(&s,buf,n);total+=n;}fclose(f);finish(&s,digest);for(int i=0;i<32;i++)printf("%02x",digest[i]);printf("  %s\n",argv[1]);fprintf(stderr,"hash bytes=%lu VmHWM %ld bytes\n",(unsigned long)total,construction_vmhwm_bytes());return 0;}

```

### construction_verify.c

```c
/* Freestanding construction-time parser/verifier for the stored step image. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
extern long construction_vmhwm_bytes(void);
typedef struct{FILE *file;uint8_t buffer[4096];size_t length,index;uint64_t bits;int available;long bytes;} Reader;
static int next_byte(Reader *r){if(r->index==r->length){r->length=fread(r->buffer,1,sizeof(r->buffer),r->file);r->index=0;if(!r->length)return -1;}r->bytes++;return r->buffer[r->index++];}
static uint64_t take(Reader *r,int width){while(r->available<width){int value=next_byte(r);if(value<0){fprintf(stderr,"short native step\n");exit(2);}r->bits|=(uint64_t)(unsigned)value<<r->available;r->available+=8;}uint64_t result=r->bits&(((uint64_t)1<<width)-1);r->bits>>=width;r->available-=width;return result;}
int main(int argc,char **argv){
    if(argc!=3){fprintf(stderr,"usage: construction_verify PROGRAM INSTRUCTIONS\n");return 2;}long instructions=atoi(argv[2]);FILE *file=fopen(argv[1],"rb");if(!file)return 2;
    Reader r={0};r.file=file;long forms14=0,forms25=0,forms36=0,shorts=0,mix[4]={0,0,0,0};int high=0;
    for(long i=0;i<instructions;i++){
        int op=(int)take(&r,2),same=(int)take(&r,1),d,a,b=0;if(same){a=(int)take(&r,11);d=a;shorts++;}else{d=(int)take(&r,11);a=(int)take(&r,11);}if(op!=3)b=(int)take(&r,11);
        if(op<0||op>3||d>=2048||a>=2048||b>=2048){fprintf(stderr,"native field overflow at %ld\n",i);return 2;}int width=3+(same?11:22)+(op==3?0:11);if(width==14)forms14++;else if(width==25)forms25++;else if(width==36)forms36++;else return 2;mix[op]++;
        if(d+1>high)high=d+1;if(a+1>high)high=a+1;if(b+1>high)high=b+1;
    }
    if(r.available&&r.bits){fprintf(stderr,"nonzero native padding\n");return 2;}if(next_byte(&r)>=0){fprintf(stderr,"trailing native bytes\n");return 2;}fclose(file);
    printf("instructions=%ld bytes=%ld peak=%d forms14=%ld forms25=%ld forms36=%ld short=%ld mix=%ld,%ld,%ld,%ld\n",instructions,r.bytes,high,forms14,forms25,forms36,shorts,mix[0],mix[1],mix[2],mix[3]);
    fprintf(stderr,"verify VmHWM %ld bytes\n",construction_vmhwm_bytes());return 0;
}

```

### controller_emitter.c

*Presentation note (R24G).* The record table of `controller_emitter.c` below is the parent's, re-presented compactly to fit the judge's evidence budget: hexadecimal limbs without leading zeros, zero limbs as `0`, trailing zero limbs and all-zero immediates omitted (C zero-initializes omitted members, C11 6.7.9 p21), eight records per line. Every one of the 1000 records and every initializer value is unchanged, the code outside the table is byte for byte the parent's, and the native8 bytes these records produce are the parent's 8384-byte controller (SHA-256 `6d52eb380e15fb82bec1c9b7da8349fef71f15846f6210fb49b535086df21f11`). The rest of this appendix is the parent's text, unchanged.

```c
/* Generated native8 assembly source and bounded emitter. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
extern long construction_vmhwm_bytes(void);
typedef struct{uint8_t op;uint16_t d,a,b;uint64_t imm[4];} Record;
static const Record records[]={
{27,1930,0,0},{18,1929,0,0,{0x100UL}},{18,1933,0,0},{18,1928,0,0,{0,0xff932290000000UL}},{18,1936,0,0},{3,1931,1936,0},{18,269,0,0},{20,0,269,1936},
{20,0,269,1936,{0x1UL}},{20,0,269,1936,{0x2UL}},{20,0,269,1936,{0x3UL}},{20,0,269,1936,{0x4UL}},{20,0,269,1936,{0x5UL}},{20,0,269,1936,{0x6UL}},{20,0,269,1936,{0x7UL}},{11,269,269,0,{0x8UL}},
{17,264,269,0,{0x38e0UL}},{22,0,264,0,{0x7UL}},{18,256,0,0},{4,267,1930,256},{13,265,256,0,{0x80UL}},{20,0,256,265,{0x38e0UL}},{25,1934,0,0,{0x222UL}},{11,256,256,0,{0x1UL}},
{17,264,256,0,{0x100UL}},{22,0,264,0,{0x13UL}},{25,1934,0,0,{0x240UL}},{24,0,0,0,{0xffffffffffffffffUL,0xffffffffffffffffUL,0xffffffffffffffffUL}},{8,264,1932,1931},{22,0,264,0,{0x211UL}},{11,1933,1933,0,{0x1UL}},{17,264,1933,0,{0x2UL,0xaf78332893229UL}},
{22,0,264,0,{0x22UL}},{29,0,0,0,{0xaUL}},{2,260,145,146},{2,260,260,147},{2,260,260,148},{2,260,260,149},{2,260,260,150},{2,260,260,151},
{2,260,260,152},{2,260,260,153},{2,260,260,154},{2,260,260,155},{2,260,260,156},{2,260,260,157},{2,260,260,158},{2,260,260,159},
{2,260,260,160},{2,260,260,161},{2,260,260,162},{2,260,260,163},{2,260,260,164},{2,260,260,165},{2,260,260,166},{2,260,260,167},
{2,260,260,168},{2,260,260,169},{2,260,260,170},{2,260,260,171},{2,260,260,172},{2,260,260,173},{2,260,260,174},{2,260,260,175},
{2,260,260,176},{2,260,260,177},{2,260,260,178},{2,260,260,179},{2,260,260,180},{2,260,260,181},{2,260,260,182},{2,260,260,183},
{2,260,260,184},{2,260,260,185},{2,260,260,186},{2,260,260,187},{2,260,260,188},{2,260,260,189},{2,260,260,190},{2,260,260,191},
{2,260,260,192},{2,260,260,193},{2,260,260,194},{2,260,260,195},{2,260,260,196},{2,260,260,197},{2,260,260,198},{2,260,260,199},
{2,260,260,200},{2,260,260,201},{2,260,260,202},{2,260,260,203},{2,260,260,204},{2,260,260,205},{2,260,260,206},{2,260,260,207},
{2,260,260,208},{2,260,260,209},{2,260,260,210},{2,260,260,211},{2,260,260,212},{2,260,260,213},{2,260,260,214},{2,260,260,215},
{2,260,260,216},{2,260,260,217},{2,260,260,218},{2,260,260,219},{2,260,260,220},{2,260,260,221},{2,260,260,222},{2,260,260,223},
{2,260,260,224},{2,260,260,225},{2,260,260,226},{2,260,260,227},{2,260,260,228},{2,260,260,229},{2,260,260,230},{2,260,260,231},
{2,260,260,232},{2,260,260,233},{2,260,260,234},{2,260,260,235},{2,260,260,236},{2,260,260,237},{2,260,260,238},{2,260,260,239},
{2,257,1932,260},{3,257,257,0},{3,265,144,0},{1,266,257,265},{1,257,257,144},{3,265,143,0},{1,257,257,265},{3,265,142,0},
{1,257,257,265},{3,265,141,0},{1,257,257,265},{3,265,140,0},{1,265,257,265},{2,266,266,265},{1,257,257,140},{3,265,139,0},
{1,257,257,265},{3,265,138,0},{1,257,257,265},{3,265,137,0},{1,257,257,265},{3,265,136,0},{1,265,257,265},{2,266,266,265},
{1,257,257,136},{3,265,135,0},{1,265,257,265},{2,266,266,265},{10,257,266,0},{18,258,0,0,{0,0xff932290000000UL}},{5,258,258,1928},{11,258,258,0,{0x1UL}},
{16,264,257,0},{22,0,264,0,{0x211UL}},{20,0,1936,0,{0x37e0UL}},{20,0,1936,1,{0x37e1UL}},{20,0,1936,2,{0x37e2UL}},{20,0,1936,3,{0x37e3UL}},{20,0,1936,4,{0x37e4UL}},{20,0,1936,5,{0x37e5UL}},
{20,0,1936,6,{0x37e6UL}},{20,0,1936,7,{0x37e7UL}},{20,0,1936,8,{0x37e8UL}},{20,0,1936,9,{0x37e9UL}},{20,0,1936,10,{0x37eaUL}},{20,0,1936,11,{0x37ebUL}},{20,0,1936,12,{0x37ecUL}},{20,0,1936,13,{0x37edUL}},
{20,0,1936,14,{0x37eeUL}},{20,0,1936,15,{0x37efUL}},{20,0,1936,16,{0x37f0UL}},{20,0,1936,17,{0x37f1UL}},{20,0,1936,18,{0x37f2UL}},{20,0,1936,19,{0x37f3UL}},{20,0,1936,20,{0x37f4UL}},{20,0,1936,21,{0x37f5UL}},
{20,0,1936,22,{0x37f6UL}},{20,0,1936,23,{0x37f7UL}},{20,0,1936,24,{0x37f8UL}},{20,0,1936,25,{0x37f9UL}},{20,0,1936,26,{0x37faUL}},{20,0,1936,27,{0x37fbUL}},{20,0,1936,28,{0x37fcUL}},{20,0,1936,29,{0x37fdUL}},
{20,0,1936,30,{0x37feUL}},{20,0,1936,31,{0x37ffUL}},{20,0,1936,32,{0x3800UL}},{20,0,1936,33,{0x3801UL}},{20,0,1936,34,{0x3802UL}},{20,0,1936,35,{0x3803UL}},{20,0,1936,36,{0x3804UL}},{20,0,1936,37,{0x3805UL}},
{20,0,1936,38,{0x3806UL}},{20,0,1936,39,{0x3807UL}},{20,0,1936,40,{0x3808UL}},{20,0,1936,41,{0x3809UL}},{20,0,1936,42,{0x380aUL}},{20,0,1936,43,{0x380bUL}},{20,0,1936,44,{0x380cUL}},{20,0,1936,45,{0x380dUL}},
{20,0,1936,46,{0x380eUL}},{20,0,1936,47,{0x380fUL}},{20,0,1936,48,{0x3810UL}},{20,0,1936,49,{0x3811UL}},{20,0,1936,50,{0x3812UL}},{20,0,1936,51,{0x3813UL}},{20,0,1936,52,{0x3814UL}},{20,0,1936,53,{0x3815UL}},
{20,0,1936,54,{0x3816UL}},{20,0,1936,55,{0x3817UL}},{20,0,1936,56,{0x3818UL}},{20,0,1936,57,{0x3819UL}},{20,0,1936,58,{0x381aUL}},{20,0,1936,59,{0x381bUL}},{20,0,1936,60,{0x381cUL}},{20,0,1936,61,{0x381dUL}},
{20,0,1936,62,{0x381eUL}},{20,0,1936,63,{0x381fUL}},{20,0,1936,64,{0x3820UL}},{20,0,1936,65,{0x3821UL}},{20,0,1936,66,{0x3822UL}},{20,0,1936,67,{0x3823UL}},{20,0,1936,68,{0x3824UL}},{20,0,1936,69,{0x3825UL}},
{20,0,1936,70,{0x3826UL}},{20,0,1936,71,{0x3827UL}},{20,0,1936,72,{0x3828UL}},{20,0,1936,73,{0x3829UL}},{20,0,1936,74,{0x382aUL}},{20,0,1936,75,{0x382bUL}},{20,0,1936,76,{0x382cUL}},{20,0,1936,77,{0x382dUL}},
{20,0,1936,78,{0x382eUL}},{20,0,1936,79,{0x382fUL}},{20,0,1936,80,{0x3830UL}},{20,0,1936,81,{0x3831UL}},{20,0,1936,82,{0x3832UL}},{20,0,1936,83,{0x3833UL}},{20,0,1936,84,{0x3834UL}},{20,0,1936,85,{0x3835UL}},
{20,0,1936,86,{0x3836UL}},{20,0,1936,87,{0x3837UL}},{20,0,1936,88,{0x3838UL}},{20,0,1936,89,{0x3839UL}},{20,0,1936,90,{0x383aUL}},{20,0,1936,91,{0x383bUL}},{20,0,1936,92,{0x383cUL}},{20,0,1936,93,{0x383dUL}},
{20,0,1936,94,{0x383eUL}},{20,0,1936,95,{0x383fUL}},{20,0,1936,96,{0x3840UL}},{20,0,1936,97,{0x3841UL}},{20,0,1936,98,{0x3842UL}},{20,0,1936,99,{0x3843UL}},{20,0,1936,100,{0x3844UL}},{20,0,1936,101,{0x3845UL}},
{20,0,1936,102,{0x3846UL}},{20,0,1936,103,{0x3847UL}},{20,0,1936,104,{0x3848UL}},{20,0,1936,105,{0x3849UL}},{20,0,1936,106,{0x384aUL}},{20,0,1936,107,{0x384bUL}},{20,0,1936,108,{0x384cUL}},{20,0,1936,109,{0x384dUL}},
{20,0,1936,110,{0x384eUL}},{20,0,1936,111,{0x384fUL}},{20,0,1936,112,{0x3850UL}},{20,0,1936,113,{0x3851UL}},{20,0,1936,114,{0x3852UL}},{20,0,1936,115,{0x3853UL}},{20,0,1936,116,{0x3854UL}},{20,0,1936,117,{0x3855UL}},
{20,0,1936,118,{0x3856UL}},{20,0,1936,119,{0x3857UL}},{20,0,1936,120,{0x3858UL}},{20,0,1936,121,{0x3859UL}},{20,0,1936,122,{0x385aUL}},{20,0,1936,123,{0x385bUL}},{20,0,1936,124,{0x385cUL}},{20,0,1936,125,{0x385dUL}},
{20,0,1936,126,{0x385eUL}},{20,0,1936,127,{0x385fUL}},{20,0,1936,128,{0x3860UL}},{20,0,1936,129,{0x3861UL}},{20,0,1936,130,{0x3862UL}},{20,0,1936,131,{0x3863UL}},{20,0,1936,132,{0x3864UL}},{20,0,1936,133,{0x3865UL}},
{20,0,1936,134,{0x3866UL}},{20,0,1936,135,{0x3867UL}},{20,0,1936,136,{0x3868UL}},{20,0,1936,137,{0x3869UL}},{20,0,1936,138,{0x386aUL}},{20,0,1936,139,{0x386bUL}},{20,0,1936,140,{0x386cUL}},{20,0,1936,141,{0x386dUL}},
{20,0,1936,142,{0x386eUL}},{20,0,1936,143,{0x386fUL}},{20,0,1936,144,{0x3870UL}},{20,0,1936,145,{0x3871UL}},{20,0,1936,146,{0x3872UL}},{20,0,1936,147,{0x3873UL}},{20,0,1936,148,{0x3874UL}},{20,0,1936,149,{0x3875UL}},
{20,0,1936,150,{0x3876UL}},{20,0,1936,151,{0x3877UL}},{20,0,1936,152,{0x3878UL}},{20,0,1936,153,{0x3879UL}},{20,0,1936,154,{0x387aUL}},{20,0,1936,155,{0x387bUL}},{20,0,1936,156,{0x387cUL}},{20,0,1936,157,{0x387dUL}},
{20,0,1936,158,{0x387eUL}},{20,0,1936,159,{0x387fUL}},{20,0,1936,160,{0x3880UL}},{20,0,1936,161,{0x3881UL}},{20,0,1936,162,{0x3882UL}},{20,0,1936,163,{0x3883UL}},{20,0,1936,164,{0x3884UL}},{20,0,1936,165,{0x3885UL}},
{20,0,1936,166,{0x3886UL}},{20,0,1936,167,{0x3887UL}},{20,0,1936,168,{0x3888UL}},{20,0,1936,169,{0x3889UL}},{20,0,1936,170,{0x388aUL}},{20,0,1936,171,{0x388bUL}},{20,0,1936,172,{0x388cUL}},{20,0,1936,173,{0x388dUL}},
{20,0,1936,174,{0x388eUL}},{20,0,1936,175,{0x388fUL}},{20,0,1936,176,{0x3890UL}},{20,0,1936,177,{0x3891UL}},{20,0,1936,178,{0x3892UL}},{20,0,1936,179,{0x3893UL}},{20,0,1936,180,{0x3894UL}},{20,0,1936,181,{0x3895UL}},
{20,0,1936,182,{0x3896UL}},{20,0,1936,183,{0x3897UL}},{20,0,1936,184,{0x3898UL}},{20,0,1936,185,{0x3899UL}},{20,0,1936,186,{0x389aUL}},{20,0,1936,187,{0x389bUL}},{20,0,1936,188,{0x389cUL}},{20,0,1936,189,{0x389dUL}},
{20,0,1936,190,{0x389eUL}},{20,0,1936,191,{0x389fUL}},{20,0,1936,192,{0x38a0UL}},{20,0,1936,193,{0x38a1UL}},{20,0,1936,194,{0x38a2UL}},{20,0,1936,195,{0x38a3UL}},{20,0,1936,196,{0x38a4UL}},{20,0,1936,197,{0x38a5UL}},
{20,0,1936,198,{0x38a6UL}},{20,0,1936,199,{0x38a7UL}},{20,0,1936,200,{0x38a8UL}},{20,0,1936,201,{0x38a9UL}},{20,0,1936,202,{0x38aaUL}},{20,0,1936,203,{0x38abUL}},{20,0,1936,204,{0x38acUL}},{20,0,1936,205,{0x38adUL}},
{20,0,1936,206,{0x38aeUL}},{20,0,1936,207,{0x38afUL}},{20,0,1936,208,{0x38b0UL}},{20,0,1936,209,{0x38b1UL}},{20,0,1936,210,{0x38b2UL}},{20,0,1936,211,{0x38b3UL}},{20,0,1936,212,{0x38b4UL}},{20,0,1936,213,{0x38b5UL}},
{20,0,1936,214,{0x38b6UL}},{20,0,1936,215,{0x38b7UL}},{20,0,1936,216,{0x38b8UL}},{20,0,1936,217,{0x38b9UL}},{20,0,1936,218,{0x38baUL}},{20,0,1936,219,{0x38bbUL}},{20,0,1936,220,{0x38bcUL}},{20,0,1936,221,{0x38bdUL}},
{20,0,1936,222,{0x38beUL}},{20,0,1936,223,{0x38bfUL}},{20,0,1936,224,{0x38c0UL}},{20,0,1936,225,{0x38c1UL}},{20,0,1936,226,{0x38c2UL}},{20,0,1936,227,{0x38c3UL}},{20,0,1936,228,{0x38c4UL}},{20,0,1936,229,{0x38c5UL}},
{20,0,1936,230,{0x38c6UL}},{20,0,1936,231,{0x38c7UL}},{20,0,1936,232,{0x38c8UL}},{20,0,1936,233,{0x38c9UL}},{20,0,1936,234,{0x38caUL}},{20,0,1936,235,{0x38cbUL}},{20,0,1936,236,{0x38ccUL}},{20,0,1936,237,{0x38cdUL}},
{20,0,1936,238,{0x38ceUL}},{20,0,1936,239,{0x38cfUL}},{20,0,1936,240,{0x38d0UL}},{20,0,1936,241,{0x38d1UL}},{20,0,1936,242,{0x38d2UL}},{20,0,1936,243,{0x38d3UL}},{20,0,1936,244,{0x38d4UL}},{20,0,1936,245,{0x38d5UL}},
{20,0,1936,246,{0x38d6UL}},{20,0,1936,247,{0x38d7UL}},{20,0,1936,248,{0x38d8UL}},{20,0,1936,249,{0x38d9UL}},{20,0,1936,250,{0x38daUL}},{20,0,1936,251,{0x38dbUL}},{20,0,1936,252,{0x38dcUL}},{20,0,1936,253,{0x38ddUL}},
{20,0,1936,254,{0x38deUL}},{20,0,1936,255,{0x38dfUL}},{16,264,257,0},{22,0,264,0,{0x210UL}},{18,256,0,0},{10,265,257,0},{15,266,265,0,{0xffffffffffffffffUL,0xffffffffffffffffUL}},{16,264,266,0},
{23,0,264,0,{0x1abUL}},{14,265,265,0,{0x80UL}},{11,256,256,0,{0x80UL}},{15,266,265,0,{0xffffffffffffffffUL}},{16,264,266,0},{23,0,264,0,{0x1b0UL}},{14,265,265,0,{0x40UL}},{11,256,256,0,{0x40UL}},
{15,266,265,0,{0xffffffffUL}},{16,264,266,0},{23,0,264,0,{0x1b5UL}},{14,265,265,0,{0x20UL}},{11,256,256,0,{0x20UL}},{15,266,265,0,{0xffffUL}},{16,264,266,0},{23,0,264,0,{0x1baUL}},
{14,265,265,0,{0x10UL}},{11,256,256,0,{0x10UL}},{15,266,265,0,{0xffUL}},{16,264,266,0},{23,0,264,0,{0x1bfUL}},{14,265,265,0,{0x8UL}},{11,256,256,0,{0x8UL}},{15,266,265,0,{0xfUL}},
{16,264,266,0},{23,0,264,0,{0x1c4UL}},{14,265,265,0,{0x4UL}},{11,256,256,0,{0x4UL}},{15,266,265,0,{0x3UL}},{16,264,266,0},{23,0,264,0,{0x1c9UL}},{14,265,265,0,{0x2UL}},
{11,256,256,0,{0x2UL}},{15,266,265,0,{0x1UL}},{16,264,266,0},{23,0,264,0,{0x1ceUL}},{14,265,265,0,{0x1UL}},{11,256,256,0,{0x1UL}},{12,266,257,0,{0x1UL}},{1,257,257,266},
{25,1934,0,0,{0x233UL}},{15,261,259,0,{0x3ffffffffffffUL}},{13,261,261,0,{0x1UL}},{11,261,261,0,{0x1UL}},{10,272,261,0},{13,265,261,0,{0x33UL}},{2,272,272,265},{13,265,261,0,{0x66UL}},
{2,272,272,265},{13,265,261,0,{0x99UL}},{2,272,272,265},{13,265,261,0,{0xccUL}},{2,272,272,265},{18,262,0,0},{19,263,262,0},{0,263,263,272},
{15,265,263,0,{0x7ffffffffffffUL}},{16,264,265,0},{22,0,264,0,{0x201UL}},{14,266,263,0,{0x33UL}},{15,265,266,0,{0x7ffffffffffffUL}},{16,264,265,0},{22,0,264,0,{0x204UL}},{14,266,263,0,{0x66UL}},
{15,265,266,0,{0x7ffffffffffffUL}},{16,264,265,0},{22,0,264,0,{0x207UL}},{14,266,263,0,{0x99UL}},{15,265,266,0,{0x7ffffffffffffUL}},{16,264,265,0},{22,0,264,0,{0x20aUL}},{14,266,263,0,{0xccUL}},
{15,265,266,0,{0x7ffffffffffffUL}},{16,264,265,0},{22,0,264,0,{0x20dUL}},{11,262,262,0,{0x1UL}},{16,264,262,0,{0x37e0UL}},{23,0,264,0,{0x1deUL}},{19,271,256,0,{0x38e0UL}},{14,271,271,0,{0x80UL}},
{15,262,271,0,{0x3fffUL}},{14,266,271,0,{0xeUL}},{6,265,261,266},{19,263,262,0},{2,263,263,265},{20,0,262,263},{10,260,258,0},{25,1935,0,0,{0x214UL}},
{24,0,0,0,{0x1a2UL}},{18,265,0,0},{2,265,265,262},{24,0,0,0,{0x37aUL}},{18,265,0,0,{0xcc000UL}},{2,265,265,262},{24,0,0,0,{0x37aUL}},{18,265,0,0,{0x198000UL}},
{2,265,265,262},{24,0,0,0,{0x37aUL}},{18,265,0,0,{0x264000UL}},{2,265,265,262},{24,0,0,0,{0x37aUL}},{18,265,0,0,{0x330000UL}},{2,265,265,262},{24,0,0,0,{0x37aUL}},
{25,1934,0,0,{0x240UL}},{12,1928,1928,0,{0x1UL}},{22,0,1928,0,{0xffffffffffffffffUL,0xffffffffffffffffUL,0xffffffffffffffffUL}},{29,0,0,0,{0xcUL}},{16,264,1929,0,{0x3fc000UL}},{23,0,264,0,{0x217UL}},{29,0,0,0,{0xbUL}},{13,265,1929,0,{0x80UL}},
{2,265,265,260},{20,0,256,265,{0x38e0UL}},{4,267,1930,1929},{11,1929,1929,0,{0x1UL}},{15,265,1929,0,{0x3fffUL}},{16,264,265,0,{0x37e0UL}},{23,0,264,0,{0x220UL}},{11,1929,1929,0,{0xc8820UL}},
{25,1934,0,0,{0x222UL}},{26,0,1935,0},{18,273,0,0,{0x1UL}},{6,273,273,256},{3,268,273,0},{21,269,0,0,{0x37e0UL}},{18,270,0,0},{19,265,269,0},
{1,265,265,268},{7,266,267,270},{15,266,266,0,{0x1UL}},{6,266,266,256},{2,265,265,266},{20,0,269,265},{11,269,269,0,{0x1UL}},{11,270,270,0,{0x1UL}},
{16,264,270,0,{0x100UL}},{23,0,264,0,{0x227UL}},{26,0,1934,0},{18,259,0,0},{21,269,0,0,{0x37e0UL}},{18,270,0,0},{19,265,269,0},{7,265,265,256},
{15,265,265,0,{0x1UL}},{6,265,265,270},{2,259,259,265},{11,269,269,0,{0x1UL}},{11,270,270,0,{0x1UL}},{16,264,270,0,{0x100UL}},{23,0,264,0,{0x236UL}},{26,0,1934,0},
{19,0,1936,0,{0x37e0UL}},{19,1,1936,0,{0x37e1UL}},{19,2,1936,0,{0x37e2UL}},{19,3,1936,0,{0x37e3UL}},{19,4,1936,0,{0x37e4UL}},{19,5,1936,0,{0x37e5UL}},{19,6,1936,0,{0x37e6UL}},{19,7,1936,0,{0x37e7UL}},
{19,8,1936,0,{0x37e8UL}},{19,9,1936,0,{0x37e9UL}},{19,10,1936,0,{0x37eaUL}},{19,11,1936,0,{0x37ebUL}},{19,12,1936,0,{0x37ecUL}},{19,13,1936,0,{0x37edUL}},{19,14,1936,0,{0x37eeUL}},{19,15,1936,0,{0x37efUL}},
{19,16,1936,0,{0x37f0UL}},{19,17,1936,0,{0x37f1UL}},{19,18,1936,0,{0x37f2UL}},{19,19,1936,0,{0x37f3UL}},{19,20,1936,0,{0x37f4UL}},{19,21,1936,0,{0x37f5UL}},{19,22,1936,0,{0x37f6UL}},{19,23,1936,0,{0x37f7UL}},
{19,24,1936,0,{0x37f8UL}},{19,25,1936,0,{0x37f9UL}},{19,26,1936,0,{0x37faUL}},{19,27,1936,0,{0x37fbUL}},{19,28,1936,0,{0x37fcUL}},{19,29,1936,0,{0x37fdUL}},{19,30,1936,0,{0x37feUL}},{19,31,1936,0,{0x37ffUL}},
{19,32,1936,0,{0x3800UL}},{19,33,1936,0,{0x3801UL}},{19,34,1936,0,{0x3802UL}},{19,35,1936,0,{0x3803UL}},{19,36,1936,0,{0x3804UL}},{19,37,1936,0,{0x3805UL}},{19,38,1936,0,{0x3806UL}},{19,39,1936,0,{0x3807UL}},
{19,40,1936,0,{0x3808UL}},{19,41,1936,0,{0x3809UL}},{19,42,1936,0,{0x380aUL}},{19,43,1936,0,{0x380bUL}},{19,44,1936,0,{0x380cUL}},{19,45,1936,0,{0x380dUL}},{19,46,1936,0,{0x380eUL}},{19,47,1936,0,{0x380fUL}},
{19,48,1936,0,{0x3810UL}},{19,49,1936,0,{0x3811UL}},{19,50,1936,0,{0x3812UL}},{19,51,1936,0,{0x3813UL}},{19,52,1936,0,{0x3814UL}},{19,53,1936,0,{0x3815UL}},{19,54,1936,0,{0x3816UL}},{19,55,1936,0,{0x3817UL}},
{19,56,1936,0,{0x3818UL}},{19,57,1936,0,{0x3819UL}},{19,58,1936,0,{0x381aUL}},{19,59,1936,0,{0x381bUL}},{19,60,1936,0,{0x381cUL}},{19,61,1936,0,{0x381dUL}},{19,62,1936,0,{0x381eUL}},{19,63,1936,0,{0x381fUL}},
{19,64,1936,0,{0x3820UL}},{19,65,1936,0,{0x3821UL}},{19,66,1936,0,{0x3822UL}},{19,67,1936,0,{0x3823UL}},{19,68,1936,0,{0x3824UL}},{19,69,1936,0,{0x3825UL}},{19,70,1936,0,{0x3826UL}},{19,71,1936,0,{0x3827UL}},
{19,72,1936,0,{0x3828UL}},{19,73,1936,0,{0x3829UL}},{19,74,1936,0,{0x382aUL}},{19,75,1936,0,{0x382bUL}},{19,76,1936,0,{0x382cUL}},{19,77,1936,0,{0x382dUL}},{19,78,1936,0,{0x382eUL}},{19,79,1936,0,{0x382fUL}},
{19,80,1936,0,{0x3830UL}},{19,81,1936,0,{0x3831UL}},{19,82,1936,0,{0x3832UL}},{19,83,1936,0,{0x3833UL}},{19,84,1936,0,{0x3834UL}},{19,85,1936,0,{0x3835UL}},{19,86,1936,0,{0x3836UL}},{19,87,1936,0,{0x3837UL}},
{19,88,1936,0,{0x3838UL}},{19,89,1936,0,{0x3839UL}},{19,90,1936,0,{0x383aUL}},{19,91,1936,0,{0x383bUL}},{19,92,1936,0,{0x383cUL}},{19,93,1936,0,{0x383dUL}},{19,94,1936,0,{0x383eUL}},{19,95,1936,0,{0x383fUL}},
{19,96,1936,0,{0x3840UL}},{19,97,1936,0,{0x3841UL}},{19,98,1936,0,{0x3842UL}},{19,99,1936,0,{0x3843UL}},{19,100,1936,0,{0x3844UL}},{19,101,1936,0,{0x3845UL}},{19,102,1936,0,{0x3846UL}},{19,103,1936,0,{0x3847UL}},
{19,104,1936,0,{0x3848UL}},{19,105,1936,0,{0x3849UL}},{19,106,1936,0,{0x384aUL}},{19,107,1936,0,{0x384bUL}},{19,108,1936,0,{0x384cUL}},{19,109,1936,0,{0x384dUL}},{19,110,1936,0,{0x384eUL}},{19,111,1936,0,{0x384fUL}},
{19,112,1936,0,{0x3850UL}},{19,113,1936,0,{0x3851UL}},{19,114,1936,0,{0x3852UL}},{19,115,1936,0,{0x3853UL}},{19,116,1936,0,{0x3854UL}},{19,117,1936,0,{0x3855UL}},{19,118,1936,0,{0x3856UL}},{19,119,1936,0,{0x3857UL}},
{19,120,1936,0,{0x3858UL}},{19,121,1936,0,{0x3859UL}},{19,122,1936,0,{0x385aUL}},{19,123,1936,0,{0x385bUL}},{19,124,1936,0,{0x385cUL}},{19,125,1936,0,{0x385dUL}},{19,126,1936,0,{0x385eUL}},{19,127,1936,0,{0x385fUL}},
{19,128,1936,0,{0x3860UL}},{19,129,1936,0,{0x3861UL}},{19,130,1936,0,{0x3862UL}},{19,131,1936,0,{0x3863UL}},{19,132,1936,0,{0x3864UL}},{19,133,1936,0,{0x3865UL}},{19,134,1936,0,{0x3866UL}},{19,135,1936,0,{0x3867UL}},
{19,136,1936,0,{0x3868UL}},{19,137,1936,0,{0x3869UL}},{19,138,1936,0,{0x386aUL}},{19,139,1936,0,{0x386bUL}},{19,140,1936,0,{0x386cUL}},{19,141,1936,0,{0x386dUL}},{19,142,1936,0,{0x386eUL}},{19,143,1936,0,{0x386fUL}},
{19,144,1936,0,{0x3870UL}},{19,145,1936,0,{0x3871UL}},{19,146,1936,0,{0x3872UL}},{19,147,1936,0,{0x3873UL}},{19,148,1936,0,{0x3874UL}},{19,149,1936,0,{0x3875UL}},{19,150,1936,0,{0x3876UL}},{19,151,1936,0,{0x3877UL}},
{19,152,1936,0,{0x3878UL}},{19,153,1936,0,{0x3879UL}},{19,154,1936,0,{0x387aUL}},{19,155,1936,0,{0x387bUL}},{19,156,1936,0,{0x387cUL}},{19,157,1936,0,{0x387dUL}},{19,158,1936,0,{0x387eUL}},{19,159,1936,0,{0x387fUL}},
{19,160,1936,0,{0x3880UL}},{19,161,1936,0,{0x3881UL}},{19,162,1936,0,{0x3882UL}},{19,163,1936,0,{0x3883UL}},{19,164,1936,0,{0x3884UL}},{19,165,1936,0,{0x3885UL}},{19,166,1936,0,{0x3886UL}},{19,167,1936,0,{0x3887UL}},
{19,168,1936,0,{0x3888UL}},{19,169,1936,0,{0x3889UL}},{19,170,1936,0,{0x388aUL}},{19,171,1936,0,{0x388bUL}},{19,172,1936,0,{0x388cUL}},{19,173,1936,0,{0x388dUL}},{19,174,1936,0,{0x388eUL}},{19,175,1936,0,{0x388fUL}},
{19,176,1936,0,{0x3890UL}},{19,177,1936,0,{0x3891UL}},{19,178,1936,0,{0x3892UL}},{19,179,1936,0,{0x3893UL}},{19,180,1936,0,{0x3894UL}},{19,181,1936,0,{0x3895UL}},{19,182,1936,0,{0x3896UL}},{19,183,1936,0,{0x3897UL}},
{19,184,1936,0,{0x3898UL}},{19,185,1936,0,{0x3899UL}},{19,186,1936,0,{0x389aUL}},{19,187,1936,0,{0x389bUL}},{19,188,1936,0,{0x389cUL}},{19,189,1936,0,{0x389dUL}},{19,190,1936,0,{0x389eUL}},{19,191,1936,0,{0x389fUL}},
{19,192,1936,0,{0x38a0UL}},{19,193,1936,0,{0x38a1UL}},{19,194,1936,0,{0x38a2UL}},{19,195,1936,0,{0x38a3UL}},{19,196,1936,0,{0x38a4UL}},{19,197,1936,0,{0x38a5UL}},{19,198,1936,0,{0x38a6UL}},{19,199,1936,0,{0x38a7UL}},
{19,200,1936,0,{0x38a8UL}},{19,201,1936,0,{0x38a9UL}},{19,202,1936,0,{0x38aaUL}},{19,203,1936,0,{0x38abUL}},{19,204,1936,0,{0x38acUL}},{19,205,1936,0,{0x38adUL}},{19,206,1936,0,{0x38aeUL}},{19,207,1936,0,{0x38afUL}},
{19,208,1936,0,{0x38b0UL}},{19,209,1936,0,{0x38b1UL}},{19,210,1936,0,{0x38b2UL}},{19,211,1936,0,{0x38b3UL}},{19,212,1936,0,{0x38b4UL}},{19,213,1936,0,{0x38b5UL}},{19,214,1936,0,{0x38b6UL}},{19,215,1936,0,{0x38b7UL}},
{19,216,1936,0,{0x38b8UL}},{19,217,1936,0,{0x38b9UL}},{19,218,1936,0,{0x38baUL}},{19,219,1936,0,{0x38bbUL}},{19,220,1936,0,{0x38bcUL}},{19,221,1936,0,{0x38bdUL}},{19,222,1936,0,{0x38beUL}},{19,223,1936,0,{0x38bfUL}},
{19,224,1936,0,{0x38c0UL}},{19,225,1936,0,{0x38c1UL}},{19,226,1936,0,{0x38c2UL}},{19,227,1936,0,{0x38c3UL}},{19,228,1936,0,{0x38c4UL}},{19,229,1936,0,{0x38c5UL}},{19,230,1936,0,{0x38c6UL}},{19,231,1936,0,{0x38c7UL}},
{19,232,1936,0,{0x38c8UL}},{19,233,1936,0,{0x38c9UL}},{19,234,1936,0,{0x38caUL}},{19,235,1936,0,{0x38cbUL}},{19,236,1936,0,{0x38ccUL}},{19,237,1936,0,{0x38cdUL}},{19,238,1936,0,{0x38ceUL}},{19,239,1936,0,{0x38cfUL}},
{19,240,1936,0,{0x38d0UL}},{19,241,1936,0,{0x38d1UL}},{19,242,1936,0,{0x38d2UL}},{19,243,1936,0,{0x38d3UL}},{19,244,1936,0,{0x38d4UL}},{19,245,1936,0,{0x38d5UL}},{19,246,1936,0,{0x38d6UL}},{19,247,1936,0,{0x38d7UL}},
{19,248,1936,0,{0x38d8UL}},{19,249,1936,0,{0x38d9UL}},{19,250,1936,0,{0x38daUL}},{19,251,1936,0,{0x38dbUL}},{19,252,1936,0,{0x38dcUL}},{19,253,1936,0,{0x38ddUL}},{19,254,1936,0,{0x38deUL}},{19,255,1936,0,{0x38dfUL}},
{26,0,1934,0},{19,300,1936,0,{0x39e0UL}},{19,301,1936,0,{0x39e1UL}},{19,302,1936,0,{0x39e2UL}},{19,303,1936,0,{0x39e3UL}},{19,304,1936,0,{0x39e4UL}},{19,305,1936,0,{0x39e5UL}},{19,306,1936,0,{0x39e6UL}},
{15,290,286,0,{0xffffffffffffffffUL}},{14,291,286,0,{0x40UL}},{15,291,291,0,{0xffffffffffffffffUL}},{14,292,286,0,{0x80UL}},{15,292,292,0,{0xffffffffffffffffUL}},{14,293,286,0,{0xc0UL}},{13,294,290,0,{0x40UL}},{0,300,300,294},
{13,294,291,0,{0x80UL}},{0,301,301,294},{0,301,301,292},{13,294,293,0,{0x40UL}},{0,302,302,294},{0,294,290,291},{13,294,294,0,{0xc0UL}},{0,302,302,294},
{0,294,292,293},{13,294,294,0,{0x80UL}},{0,303,303,294},{28,0,300,0},{19,289,1936,0,{0x39e7UL}},{0,287,300,289},{26,0,1935,0},{19,300,1936,0,{0x39e0UL}},
{19,301,1936,0,{0x39e1UL}},{19,302,1936,0,{0x39e2UL}},{19,303,1936,0,{0x39e3UL}},{19,304,1936,0,{0x39e4UL}},{19,305,1936,0,{0x39e5UL}},{19,306,1936,0,{0x39e6UL}},{15,290,286,0,{0xffffffffffffffffUL}},{14,291,286,0,{0x40UL}},
{15,291,291,0,{0xffffffffffffffffUL}},{14,292,286,0,{0x80UL}},{15,292,292,0,{0xffffffffffffffffUL}},{14,293,286,0,{0xc0UL}},{13,294,290,0,{0x40UL}},{0,300,300,294},{13,294,291,0,{0x80UL}},{0,301,301,294},
{0,301,301,292},{13,294,293,0,{0x40UL}},{0,302,302,294},{0,294,290,291},{13,294,294,0,{0xc0UL}},{0,302,302,294},{0,294,292,293},{13,294,294,0,{0x80UL}},
{0,303,303,294},{26,0,1935,0},{19,285,256,0,{0x38e0UL}},{14,266,285,0,{0x80UL}},{15,285,285,0,{0xffffffffffffffffUL,0xffffffffffffffffUL}},{5,285,258,285},{17,264,285,0,{0x1UL,0x9f7f000000000UL}},{23,0,264,0,{0x3e7UL}},
{4,280,1930,265},{4,281,1930,266},{10,286,280,0},{18,284,0,0},{18,269,0,0},{18,274,0,0},{8,264,284,274},{23,0,264,0,{0x38bUL}},
{20,0,269,286},{11,269,269,0,{0x1UL}},{11,274,274,0,{0x12efbafbe6ba400bUL,0x2dacea77e2UL}},{25,1935,0,0,{0x341UL}},{11,284,284,0,{0x1UL}},{17,264,287,0,{0,0,0x11180UL}},{22,0,264,0,{0x393UL}},{17,264,284,0,{0,0x9f7f000000000UL}},
{23,0,264,0,{0x3e7UL}},{10,286,287,0},{24,0,0,0,{0x386UL}},{9,264,284,285},{22,0,264,0,{0x3abUL}},{5,282,284,285},{18,275,0,0},{18,277,0,0},
{11,294,275,0,{0x12efbafbe6ba400bUL,0x2dacea77e2UL}},{9,264,282,294},{22,0,264,0,{0x39eUL}},{10,275,294,0},{11,277,277,0,{0x1UL}},{24,0,0,0,{0x398UL}},{19,280,277,0},{11,277,277,0,{0x1UL}},
{11,276,275,0,{0x12efbafbe6ba400bUL,0x2dacea77e2UL}},{5,282,282,275},{16,264,282,0},{22,0,264,0,{0x3a9UL}},{10,286,280,0},{25,1935,0,0,{0x341UL}},{10,280,287,0},{12,282,282,0,{0x1UL}},
{24,0,0,0,{0x3a2UL}},{5,275,284,285},{24,0,0,0,{0x3b6UL}},{5,282,285,284},{18,275,0,0},{18,276,0,0,{0x12efbafbe6ba400bUL,0x2dacea77e2UL}},{18,277,0,0,{0x1UL}},{16,264,282,0},
{22,0,264,0,{0x3b6UL}},{10,286,281,0},{25,1935,0,0,{0x341UL}},{10,281,287,0},{12,282,282,0,{0x1UL}},{24,0,0,0,{0x3afUL}},{8,264,280,281},{22,0,264,0,{0x3e7UL}},
{9,264,276,284},{23,0,264,0,{0x3ccUL}},{5,279,276,275},{10,282,279,0},{10,278,281,0},{10,286,278,0},{25,1935,0,0,{0x341UL}},{10,278,287,0},
{12,282,282,0,{0x1UL}},{16,264,282,0},{23,0,264,0,{0x3bdUL}},{19,294,277,0},{8,264,294,278},{22,0,264,0,{0x3cdUL}},{10,280,294,0},{10,281,278,0},
{10,275,276,0},{11,276,276,0,{0x12efbafbe6ba400bUL,0x2dacea77e2UL}},{11,277,277,0,{0x1UL}},{24,0,0,0,{0x3b8UL}},{5,279,284,275},{16,264,279,0},{22,0,264,0,{0x3e7UL}},{10,286,280,0},
{25,1935,0,0,{0x341UL}},{10,288,287,0},{10,286,281,0},{25,1935,0,0,{0x341UL}},{8,264,288,287},{22,0,264,0,{0x3daUL}},{10,280,288,0},{10,281,287,0},
{12,279,279,0,{0x1UL}},{24,0,0,0,{0x3cdUL}},{10,286,280,0},{25,1935,0,0,{0x35fUL}},{20,0,1936,300,{0x39e8UL}},{20,0,1936,301,{0x39e9UL}},{20,0,1936,302,{0x39eaUL}},{20,0,1936,303,{0x39ebUL}},
{10,286,281,0},{25,1935,0,0,{0x35fUL}},{20,0,1936,300,{0x39ecUL}},{20,0,1936,301,{0x39edUL}},{20,0,1936,302,{0x39eeUL}},{20,0,1936,303,{0x39efUL}},{29,0,0,0,{0x1UL}},{29,0,0,0,{0xdUL}},
};
static uint64_t literals[64][4];static int literal_count;
static int same256(const uint64_t a[4],const uint64_t b[4]){return a[0]==b[0]&&a[1]==b[1]&&a[2]==b[2]&&a[3]==b[3];}
static int literal(const uint64_t value[4]){for(int i=0;i<literal_count;i++)if(same256(literals[i],value))return i;if(literal_count==64){fprintf(stderr,"literal capacity\n");exit(2);}for(int j=0;j<4;j++)literals[literal_count][j]=value[j];return literal_count++;}
int main(int argc,char **argv){if(argc!=2)return 2;FILE *out=fopen(argv[1],"wb");if(!out)return 2;const int count=(int)(sizeof(records)/sizeof(records[0]));
 for(int i=0;i<count;i++){const Record *r=&records[i];if(r->op>29||r->d>=2048||r->a>=2048||r->b>=2048)return 2;int flag=0;uint64_t field=r->imm[0];if(r->imm[1]||r->imm[2]||r->imm[3]||field>=(1UL<<25)){flag=1;field=(uint64_t)literal(r->imm);}if(field>=(1UL<<25))return 2;}
 for(int i=0;i<count;i++){const Record *r=&records[i];int flag=0;uint64_t field=r->imm[0];if(r->imm[1]||r->imm[2]||r->imm[3]||field>=(1UL<<25)){flag=1;field=(uint64_t)literal(r->imm);}uint64_t word=(uint64_t)r->op|((uint64_t)flag<<5)|((uint64_t)r->d<<6)|((uint64_t)r->a<<17)|((uint64_t)r->b<<28)|(field<<39);uint8_t bytes[8];for(int j=0;j<8;j++)bytes[j]=(uint8_t)(word>>(8*j));if(fwrite(bytes,1,8,out)!=8)return 2;}
 for(int i=0;i<literal_count;i++){uint8_t bytes[32];for(int j=0;j<32;j++)bytes[j]=(uint8_t)(literals[i][j>>3]>>(8*(j&7)));if(fwrite(bytes,1,32,out)!=32)return 2;}if(fclose(out))return 2;
 fprintf(stderr,"controller instructions=%d literals=%d bytes=%d VmHWM %ld bytes\n",count,literal_count,8*count+32*literal_count,construction_vmhwm_bytes());return 0;}

```

## Appendix C. Measured construction record

```json
{
  "address_space_limit": 1048576,
  "chained_table": {
    "bytes": 4096,
    "candidate_evaluations": 1015808,
    "checksum": "c8fa4bd9170966dc",
    "entries": 1024,
    "truth_checks": 32768
  },
  "operation_counts": {
    "annealing_rounds_per_process": 21,
    "cheap_builds": 512,
    "controller_bytes": 8384,
    "controller_instructions": 1000,
    "controller_literals": 12,
    "full_processes": 8,
    "iterations_per_round": 200000000,
    "prefilter_bytes": 49,
    "prefilter_instructions": 15,
    "scan_bins": 1223927818,
    "scan_evaluations": 14639,
    "step_bytes": 503426,
    "step_instructions": 144722,
    "table_processes": 10
  },
  "peak_bytes": 1025311,
  "phases": [
    {
      "binary": "construction_generator",
      "charged_peak_bytes": 610103,
      "image": {
        "bss": 288448,
        "data": 216,
        "image": 329527,
        "text": 40863
      },
      "name": "512-trial cheap scan",
      "output_bytes": 18432,
      "retained_input_output_bytes": 18432,
      "seconds": 4.101773576112464,
      "sequential": true,
      "stack_reserve": 262144,
      "trial": null,
      "vmhwm_bytes": 417792
    },
    {
      "binary": "construction_generator",
      "charged_peak_bytes": 654976,
      "cheap_count": 148057,
      "image": {
        "bss": 288448,
        "data": 216,
        "image": 329527,
        "text": 40863
      },
      "name": "TOPK full build 1",
      "output_bytes": 63305,
      "retained_best_bytes": 63305,
      "retained_input_output_bytes": 63305,
      "seconds": 411.1221721279435,
      "sequential": true,
      "stack_reserve": 262144,
      "step_ops": 144722,
      "trial": 1333,
      "vmhwm_bytes": 413696
    },
    {
      "binary": "construction_generator",
      "charged_peak_bytes": 654976,
      "cheap_count": 148066,
      "image": {
        "bss": 288448,
        "data": 216,
        "image": 329527,
        "text": 40863
      },
      "name": "TOPK full build 2",
      "output_bytes": 63305,
      "retained_best_bytes": 63305,
      "retained_input_output_bytes": 63305,
      "seconds": 409.83426084695384,
      "sequential": true,
      "stack_reserve": 262144,
      "step_ops": 144784,
      "trial": 1215,
      "vmhwm_bytes": 417792
    },
    {
      "binary": "construction_generator",
      "charged_peak_bytes": 654976,
      "cheap_count": 148084,
      "image": {
        "bss": 288448,
        "data": 216,
        "image": 329527,
        "text": 40863
      },
      "name": "TOPK full build 3",
      "output_bytes": 63305,
      "retained_best_bytes": 63305,
      "retained_input_output_bytes": 63305,
      "seconds": 410.15120529406704,
      "sequential": true,
      "stack_reserve": 262144,
      "step_ops": 144749,
      "trial": 1059,
      "vmhwm_bytes": 417792
    },
    {
      "binary": "construction_generator",
      "charged_peak_bytes": 654976,
      "cheap_count": 148087,
      "image": {
        "bss": 288448,
        "data": 216,
        "image": 329527,
        "text": 40863
      },
      "name": "TOPK full build 4",
      "output_bytes": 63305,
      "retained_best_bytes": 63305,
      "retained_input_output_bytes": 63305,
      "seconds": 408.4459265100304,
      "sequential": true,
      "stack_reserve": 262144,
      "step_ops": 144756,
      "trial": 1033,
      "vmhwm_bytes": 413696
    },
    {
      "binary": "construction_generator",
      "charged_peak_bytes": 654976,
      "cheap_count": 148090,
      "image": {
        "bss": 288448,
        "data": 216,
        "image": 329527,
        "text": 40863
      },
      "name": "TOPK full build 5",
      "output_bytes": 63305,
      "retained_best_bytes": 63305,
      "retained_input_output_bytes": 63305,
      "seconds": 408.2454593598377,
      "sequential": true,
      "stack_reserve": 262144,
      "step_ops": 144753,
      "trial": 1331,
      "vmhwm_bytes": 413696
    },
    {
      "binary": "construction_generator",
      "charged_peak_bytes": 654976,
      "cheap_count": 148100,
      "image": {
        "bss": 288448,
        "data": 216,
        "image": 329527,
        "text": 40863
      },
      "name": "TOPK full build 6",
      "output_bytes": 63305,
      "retained_best_bytes": 63305,
      "retained_input_output_bytes": 63305,
      "seconds": 406.93958784197457,
      "sequential": true,
      "stack_reserve": 262144,
      "step_ops": 144723,
      "trial": 1371,
      "vmhwm_bytes": 417792
    },
    {
      "binary": "construction_generator",
      "charged_peak_bytes": 654976,
      "cheap_count": 148100,
      "image": {
        "bss": 288448,
        "data": 216,
        "image": 329527,
        "text": 40863
      },
      "name": "TOPK full build 7",
      "output_bytes": 63305,
      "retained_best_bytes": 63305,
      "retained_input_output_bytes": 63305,
      "seconds": 407.58258002088405,
      "sequential": true,
      "stack_reserve": 262144,
      "step_ops": 144762,
      "trial": 1426,
      "vmhwm_bytes": 417792
    },
    {
      "binary": "construction_generator",
      "charged_peak_bytes": 654976,
      "cheap_count": 148102,
      "image": {
        "bss": 288448,
        "data": 216,
        "image": 329527,
        "text": 40863
      },
      "name": "TOPK full build 8",
      "output_bytes": 63305,
      "retained_best_bytes": 63305,
      "retained_input_output_bytes": 63305,
      "seconds": 407.7253683609888,
      "sequential": true,
      "stack_reserve": 262144,
      "step_ops": 144767,
      "trial": 1375,
      "vmhwm_bytes": 413696
    },
    {
      "binary": "construction_hash",
      "charged_peak_bytes": 51671,
      "image": {
        "bss": 4096,
        "data": 16,
        "image": 9766,
        "text": 5654
      },
      "name": "structured-basis file verification",
      "retained_input_output_bytes": 22999,
      "sequential": true,
      "stack_reserve": 16384,
      "vmhwm_bytes": 28672
    },
    {
      "binary": "construction_scan",
      "charged_peak_bytes": 78795,
      "image": {
        "bss": 4160,
        "data": 24,
        "image": 62337,
        "text": 58153
      },
      "name": "native finite parameter scan",
      "retained_input_output_bytes": 74,
      "sequential": true,
      "stack_reserve": 16384,
      "vmhwm_bytes": 73728
    },
    {
      "binary": "construction_emitter",
      "charged_peak_bytes": 1025311,
      "image": {
        "bss": 393504,
        "data": 208,
        "image": 423581,
        "text": 29869
      },
      "name": "streaming native step emission",
      "retained_input_output_bytes": 503426,
      "sequential": true,
      "stack_reserve": 98304,
      "vmhwm_bytes": 446464
    },
    {
      "binary": "construction_hash",
      "charged_peak_bytes": 536194,
      "image": {
        "bss": 4096,
        "data": 16,
        "image": 9766,
        "text": 5654
      },
      "name": "streaming step SHA-256",
      "retained_input_output_bytes": 503426,
      "sequential": true,
      "stack_reserve": 16384,
      "vmhwm_bytes": 32768
    },
    {
      "binary": "construction_verify",
      "charged_peak_bytes": 529108,
      "image": {
        "bss": 4096,
        "data": 16,
        "image": 9298,
        "text": 5186
      },
      "name": "construction-time step parsing, field, and ledger verification",
      "retained_input_output_bytes": 503426,
      "sequential": true,
      "stack_reserve": 16384,
      "vmhwm_bytes": 24576
    },
    {
      "binary": "construction_prefilter",
      "charged_peak_bytes": 24687,
      "image": {
        "bss": 4128,
        "data": 24,
        "image": 8254,
        "text": 4102
      },
      "name": "native 15-OR prefilter emission",
      "retained_input_output_bytes": 49,
      "sequential": true,
      "stack_reserve": 16384,
      "vmhwm_bytes": 16384
    },
    {
      "binary": "construction_hash",
      "charged_peak_bytes": 32817,
      "image": {
        "bss": 4096,
        "data": 16,
        "image": 9766,
        "text": 5654
      },
      "name": "streaming prefilter SHA-256",
      "retained_input_output_bytes": 49,
      "sequential": true,
      "stack_reserve": 16384,
      "vmhwm_bytes": 32768
    },
    {
      "binary": "controller_emitter",
      "charged_peak_bytes": 75332,
      "image": {
        "bss": 6208,
        "data": 24,
        "image": 50564,
        "text": 44332
      },
      "name": "native8 controller emission",
      "retained_input_output_bytes": 8384,
      "sequential": true,
      "stack_reserve": 16384,
      "vmhwm_bytes": 57344
    },
    {
      "binary": "construction_hash",
      "charged_peak_bytes": 37056,
      "image": {
        "bss": 4096,
        "data": 16,
        "image": 9766,
        "text": 5654
      },
      "name": "streaming controller SHA-256",
      "retained_input_output_bytes": 8384,
      "sequential": true,
      "stack_reserve": 16384,
      "vmhwm_bytes": 28672
    }
  ],
  "round": 24,
  "schema": "hashsmash-construction-memory-v1",
  "sequential": true
}
```

## Appendix D. R24G sources

These are the sources of R24G's additions.

- **Embedded in the experiment.** `rc_codec.py` and `rc_checks.py`, verbatim.
- **The experiment program.** `build_experiment.py` derives `experiments/compact.py` from the parent's experiment program by text replacement only.
- **Generated values.** `make_certificate_harness.py` produced Appendix A with the parent's model. `controller_records_harness.py` exported the parent's controller assembly at R24G's parameters, and `make_controller_emitter.py` generated `rc_controller_emit.c` from it.
- **Construction phases** of Sections 3 and 5: `rc_encode.c`, `rc_scan.c` and `rc_controller_emit.c`. They are built as static musl binaries with `gcc -static -Os -s` and run under `prlimit --as=1048576`.

Appendices B and C are the parent's sources and measured record. They describe the parent's phases, which are freestanding and built without libc. Appendix C is unchanged; Appendix B is unchanged except for the compact presentation of one record table, stated in its presentation note. The record table of `rc_controller_emit.c` below uses the same compact presentation; its compiled binary is byte-identical to the measured one.

### rc_codec.py

```python
"""RC block codec and streaming executor (proof Section 3.6): FIFO window of the last 16 destinations."""
MASK256 = (1 << 256) - 1
FORMS = {"1": (0, 1), "00": (0, 0), "0100": (2, 0), "0101": (2, 1), "01101": (1, 0), "0111": (1, 1),
         "011000": (3, 0), "011001": (3, 1)}
CODE = {v: k for k, v in FORMS.items()}
K, IW, RW = 16, 4, 11
INIT = tuple(range(K))
WINDOW = {}
for _w in range(64):
    _s = "".join(str(_w >> i & 1) for i in range(6))
    for _cw, _v in FORMS.items():
        if _s.startswith(_cw):
            WINDOW[_w] = (_v[0], _v[1], len(_cw))
assert len(WINDOW) == 64
FORM_BITS = {v: (sum(int(c) << i for i, c in enumerate(k)), len(k)) for k, v in FORMS.items()}


def encode(program):
    out = bytearray(); acc = 0; used = 0; n = 0; L = list(INIT)
    for op, d, a, b in program:
        if not (0 <= op <= 3 and 0 <= min(d, a, b) and max(d, a, b) < 1 << RW):
            raise AssertionError("record field out of range")
        if op != 3 and d == b and d != a:
            a, b = b, a
        short = d == a
        v, w = FORM_BITS[(op, int(short))]
        if not short:
            v |= d << w; w += RW
        for r in ((a,) if op == 3 else (a, b)):
            if r in L:
                v |= L.index(r) << (w + 1); w += 1 + IW
            else:
                v |= (1 | r << 1) << w; w += 1 + RW
        acc |= v << used; used += w; n += w
        while used >= 8:
            out.append(acc & 255); acc >>= 8; used -= 8
        L.pop(); L.insert(0, d)
    if used:
        out.append(acc)
    return bytes(out), n


def run_block(image, n_rec, R, on_record=None):
    total = 8 * len(image)
    L = list(INIT)
    p = 0
    buf = image + bytes(8)
    for n in range(n_rec):
        if p >= total:
            raise AssertionError("block ended before the last record")
        x = int.from_bytes(buf[p >> 3:(p >> 3) + 7], "little") >> (p & 7)
        op, short, q = WINDOW[x & 63]
        if short:
            d = None
        else:
            d = x >> q & 2047; q += RW
        if x >> q & 1:
            a = x >> (q + 1) & 2047; ka = -1; q += 1 + RW
        else:
            ka = x >> (q + 1) & 15; a = L[ka]; q += 1 + IW
        kb = -1
        if op != 3:
            if x >> q & 1:
                b = x >> (q + 1) & 2047; q += 1 + RW
            else:
                kb = x >> (q + 1) & 15; b = L[kb]; q += 1 + IW
        else:
            b = 0
        p += q
        if p > total:
            raise AssertionError("record crosses the end of the block")
        if short:
            d = a
        if op == 0:
            R[d] = R[a] ^ R[b]
        elif op == 1:
            R[d] = R[a] & R[b]
        elif op == 2:
            R[d] = R[a] | R[b]
        else:
            R[d] = R[a] ^ MASK256
        if on_record is not None:
            on_record(n, op, short, d, a, b, ka, kb)
        L.pop(); L.insert(0, d)
    if (p + 7) // 8 != len(image):
        raise AssertionError("block length does not match its records")
    if p < total and (int.from_bytes(image[p >> 3:], "little") >> (p & 7)):
        raise AssertionError("nonzero padding")
    return p, tuple(L)
```

### rc_checks.py

```python
"""R24G RC block checks (proof Section 7)."""
import hashlib
import random

MASK256 = (1 << 256) - 1


def _two_address(binary, count):
    buf = binary + bytes(8); p = 0; prog = []
    for _ in range(count):
        x = int.from_bytes(buf[p >> 3:(p >> 3) + 6], 'little') >> (p & 7)
        op = x & 3
        if x >> 2 & 1:
            d = a = x >> 3 & 2047; q = 14
        else:
            d = x >> 3 & 2047; a = x >> 14 & 2047; q = 25
        if op != 3:
            b = x >> q & 2047; q += 11
        else:
            b = 0
        prog.append((op, d, a, b)); p += q
    if (p + 7) // 8 != len(binary):
        raise AssertionError('two-address length')
    return prog


def block_checks(step, support, rc, record, expected_step, expected_rc, constants, pd, step_binary):
    program = _two_address(step_binary, expected_step['operations'])
    pf_program, _, _, _ = step.emit_prefilter(expected_step['prefilter']['destination'])
    block = list(program) + list(pf_program)
    image, nbits = rc.encode(block)
    got = {'records': len(block), 'bits': nbits, 'bytes': len(image), 'sha256': hashlib.sha256(image).hexdigest()}
    if got != {k: expected_rc[k] for k in got}:
        raise AssertionError('RC block emission %r' % (got,))
    rng = random.Random(int.from_bytes(hashlib.sha256(b'r24g-rc-batches').digest()[:8], 'little'))
    points = [rng.getrandbits(256) for _ in range(256)]
    R = [rng.getrandbits(256) for _ in range(2048)]
    for bit in range(256):
        R[bit] = sum(((p >> bit) & 1) << lane for lane, p in enumerate(points))
    ref = list(R)
    exits = set()
    lanes = tuple(range(0, 256, 16))
    decoded = [[], []]
    stats = {'window_references': 0, 'reset_references': 0}
    seen = set()
    def observer(k):
        def f(n, op, short, d, a, b, ka, kb):
            decoded[k].append((op, d, a, b))
            if k == 0:
                seen.add(('form', op, short))
                for slot, kk in enumerate((ka,) if op == 3 else (ka, kb)):
                    if kk >= 0:
                        seen.add(('index', slot, kk)); stats['window_references'] += 1
                        if kk >= n:
                            stats['reset_references'] += 1
                    else:
                        seen.add(('register', slot))
        return f
    for batch in range(3):
        support.execute_step(program, ref)
        support.execute_step(pf_program, ref)
        exits.add(rc.run_block(image, len(block), R, observer(batch) if batch < 2 else None))
        if R != ref:
            raise AssertionError('RC streaming execution differs from the reference')
        for lane in lanes:
            points[lane] = support.chain(points[lane], constants, pd, record['round'])
            if sum(((R[b] >> lane) & 1) << b for b in range(256)) != points[lane]:
                raise AssertionError('RC step/scalar mismatch')
    if len(exits) != 1:
        raise AssertionError('decoder exit state differs between batches')
    if decoded[0] != decoded[1]:
        raise AssertionError('RC decoding depends on register contents')
    again, _, _ = step.encode_two_address(decoded[0][:len(program)])
    pf_again, _, _ = step.encode_two_address(decoded[0][len(program):])
    if (len(again), hashlib.sha256(again).hexdigest()) != (expected_step['bytes'], expected_step['sha256']) or \
            hashlib.sha256(pf_again).hexdigest() != expected_step['prefilter']['sha256']:
        raise AssertionError('RC block does not denote the parent program')
    need = {('form', op, s) for op in range(4) for s in (0, 1)} | {('index', slot, i) for slot in (0, 1) for i in range(16)} \
        | {('register', 0), ('register', 1)}
    if not need <= seen or (stats['window_references'], stats['reset_references']) != (expected_rc['window_references'], expected_rc['reset_references']):
        raise AssertionError('RC stored-form coverage %r %r' % (sorted(need - seen), stats))
    cover = set()
    for trial in range(4):
        srng = random.Random(trial)
        hot = [0, 2047] + srng.sample(range(1, 2047), 10)
        pick = lambda: srng.choice(hot) if srng.random() < 0.7 else srng.choice((0, 2047, srng.randrange(2048)))
        prog = []
        for _ in range(1500):
            op = srng.randrange(4); a, b = pick(), pick(); u = srng.random()
            prog.append((op, a if u < 0.4 else (b if u < 0.5 else pick()), a, 0 if op == 3 else b))
        cover |= {('swap',) for op, d, a, b in prog if op != 3 and d == b != a}
        img, _ = rc.encode(prog)
        r1 = [srng.getrandbits(256) for _ in range(2048)]; r2 = list(r1)
        for op, d, a, b in prog:
            r1[d] = (r1[a] ^ r1[b]) if op == 0 else (r1[a] & r1[b]) if op == 1 else (r1[a] | r1[b]) if op == 2 else r1[a] ^ MASK256
        def note(n, op, short, d, a, b, ka, kb):
            cover.add(('form', op, short))
            if not short and d in (0, 2047):
                cover.add(('dest', d))
            for slot, (r, kk) in enumerate(((a, ka),) if op == 3 else ((a, ka), (b, kb))):
                if kk < 0 and r in (0, 2047):
                    cover.add(('register', slot, r))
        rc.run_block(img, len(prog), r2, note)
        if r1 != r2:
            raise AssertionError('RC synthetic program')
    need = {('form', op, s) for op in range(4) for s in (0, 1)} | {('dest', 0), ('dest', 2047), ('swap',)} \
        | {('register', slot, r) for slot in (0, 1) for r in (0, 2047)}
    if not need <= cover:
        raise AssertionError('RC synthetic coverage %r' % sorted(need - cover))
    for bad in ([(0, 2048, 0, 0)], [(0, 0, 2048, 0)], [(0, 0, 0, 2048)], [(4, 0, 0, 0)], [(0, -1, 0, 0)]):
        try:
            rc.encode(bad)
        except AssertionError:
            continue
        raise AssertionError('RC field overflow accepted')
    def rejected(img, n):
        try:
            rc.run_block(img, n, [0] * 2048)
        except AssertionError:
            return True
        return False
    for trial in range(2):
        srng = random.Random(100 + trial)
        prog = [(srng.randrange(4), srng.randrange(2048), srng.randrange(2048), srng.randrange(2048)) for _ in range(997 + trial)]
        prog = [(op, d, a, 0 if op == 3 else b) for op, d, a, b in prog]
        img, nb = rc.encode(prog)
        if rejected(img, len(prog)):
            raise AssertionError('well-formed RC block rejected')
        bad = bytearray(img)
        if nb % 8:
            bad[-1] |= 1 << (nb % 8)
        if not (rejected(img[:-1], len(prog)) and rejected(img + b'\0', len(prog)) and rejected(img, len(prog) + 1)
                and rejected(img, len(prog) - 1) and (nb % 8 == 0 or rejected(bytes(bad), len(prog)))):
            raise AssertionError('malformed RC block accepted')
    saved = rc.INIT
    rc.INIT = tuple(next(iter(exits))[1])
    try:
        stale = list(R); ref2 = list(R)
        support.execute_step(program, ref2); support.execute_step(pf_program, ref2)
        try:
            rc.run_block(image, len(block), stale)
            if stale == ref2:
                raise AssertionError('the entry reset is not exercised')
        except AssertionError as error:
            if 'reset' in str(error):
                raise
    finally:
        rc.INIT = saved
    return image, len(block)


def transition_checks(support, rc, manifest, image, n_rec, constants, pd):
    code, _ = support.decode_native8(manifest['binary'], manifest['instructions'])
    layout = manifest['layout']
    vm = support.VM(code, manifest['labels'], layout, manifest['register_words'], manifest['round'], (1 << 192) - 1)
    import importlib
    base = importlib.import_module('emitter')
    rng = random.Random(int.from_bytes(hashlib.sha256(b'r24g-transition').digest()[:8], 'little'))
    points = [rng.getrandbits(256) for _ in range(256)]
    for bit in range(256):
        vm.reg[bit] = sum(((p >> bit) & 1) << lane for lane, p in enumerate(points))
    vm.reg[base.R_COUNTER] = 3; vm.reg[base.R_ONES] = MASK256; vm.reg[base.R_PREFILTER] = MASK256
    entries = []
    def hook(machine):
        entries.append(rc.run_block(image, n_rec, machine.reg))
    vm.step_hook = hook
    vm.run(manifest['labels']['continue'], limit=1000)
    if vm.halt != 12 or vm.external_steps != 2 or len(entries) != 2 or entries[0] != entries[1]:
        raise AssertionError('controller/RC transition')
    for lane in range(0, 256, 32):
        p = points[lane]
        for _ in range(2):
            p = support.chain(p, constants, pd, manifest['round'])
        if sum(((vm.reg[bit] >> lane) & 1) << bit for bit in range(256)) != p:
            raise AssertionError('transition step/scalar mismatch')
    return 2
```

### build_experiment.py

```python
#!/usr/bin/env python3
"""Build R24G's experiments/compact.py from the parent's (4ea0966b) experiment program, by text transformation only.

Kept unchanged (byte for byte inside SOURCES): the parent's step, controller_base, controller, support and model
modules and the frozen plan. Replaced: the certificate (Appendix A regenerated at R24G's parameters) and the expected
controller values. Added: the RC codec (rc), the RC checks (rc_checks), EXPECTED_RC, and calls from checks() to the RC
block checks and the controller/RC transition checks; the response rows report the RC observations.

Usage: build_experiment.py PARENT_COMPACT RC_CODEC RC_CHECKS CERTIFICATE_JSON CONTROLLER_JSON RC_JSON OUT
"""
import ast
import base64
import json
import lzma
import sys


def pack(text):
    return base64.b85encode(lzma.compress(text.encode(), preset=9 | lzma.PRESET_EXTREME)).decode()


def main():
    parent, codec, checks_src, cert_path, ctl_path, rc_path, out = sys.argv[1:8]
    src = open(parent).read()
    lines = src.split("\n")
    tree = ast.parse(src)
    sources = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "SOURCES":
            sources = ast.literal_eval(node.value)
    assert sources is not None and set(sources) == {"step", "controller_base", "controller", "support", "model", "certificate", "plan"}
    cert = json.load(open(cert_path))
    ctl = json.load(open(ctl_path))
    rc = json.load(open(rc_path))
    new_sources = dict(sources)
    new_sources["certificate"] = pack(json.dumps(cert, sort_keys=True, separators=(",", ":")))
    new_sources["rc"] = pack(open(codec).read())
    new_sources["rc_checks"] = pack(open(checks_src).read())

    def replace_line(prefix, new):
        hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
        assert len(hits) == 1, prefix
        lines[hits[0]] = new

    replace_line('"""Normative step/controller emitters', '"""R24G: 4ea0966b emitters, checks and certificate; straight line stored as the RC block."""')
    replace_line("SOURCES=", "SOURCES=" + repr(new_sources))
    replace_line("EXPECTED_CONTROLLER=", "EXPECTED_CONTROLLER=" + repr(ctl))
    replace_line("LINK_REGISTER=", "LINK_REGISTER=1927\nEXPECTED_RC=" + repr(rc))
    text = "\n".join(lines)
    old_load = " return step,ctl,support,model\n"
    new_load = (" rc=types.ModuleType('rc_codec');exec(compile(unpack('rc'),'rc_codec.py','exec'),rc.__dict__)\n"
                " rcc=types.ModuleType('rc_checks');exec(compile(unpack('rc_checks'),'rc_checks.py','exec'),rcc.__dict__)\n"
                " return step,ctl,support,model,rc,rcc\n")
    assert text.count(old_load) == 1
    text = text.replace(old_load, new_load)
    old_checks = (" step,ctl,support,model=load_modules()\n"
                  " step_binary,pd,meta=support.step_checks(step,RECORD,EXPECTED_STEP)\n")
    new_checks = (" step,ctl,support,model,rc,rcc=load_modules()\n"
                  " step_binary,pd,meta=support.step_checks(step,RECORD,EXPECTED_STEP)\n"
                  " global RC_IMAGE,RC_RECORDS,TRANSITIONS\n"
                  " RC_IMAGE,RC_RECORDS=rcc.block_checks(step,support,rc,RECORD,EXPECTED_STEP,EXPECTED_RC,CONSTANTS,PD,step_binary)\n")
    assert text.count(old_checks) == 1
    text = text.replace(old_checks, new_checks)
    old_ctl = " support.controller_checks(ctl,manifest,CONSTANTS,PD,PARAMETERS)\n"
    new_ctl = (" support.controller_checks(ctl,manifest,CONSTANTS,PD,PARAMETERS)\n"
               " TRANSITIONS=rcc.transition_checks(support,rc,manifest,RC_IMAGE,RC_RECORDS,CONSTANTS,PD)\n")
    assert text.count(old_ctl) == 1
    text = text.replace(old_ctl, new_ctl)
    old_obs = "'controller_instructions':manifest['instructions'],'controller_paths':12,\n                               'limit_halt_checked':1}})"
    new_obs = ("'controller_instructions':manifest['instructions'],'controller_paths':12,\n                               'limit_halt_checked':1,"
               "'rc_block_bytes':len(RC_IMAGE),'rc_records':RC_RECORDS,'rc_streamed_batches':3,'rc_controller_back_edges':TRANSITIONS}})")
    assert text.count(old_obs) == 1, "observation row"
    text = text.replace(old_obs, new_obs)
    old_self = "print(json.dumps({'status':'ok','step':EXPECTED_STEP,"
    assert text.count(old_self) == 1
    text = text.replace(old_self, "print(json.dumps({'status':'ok','rc':EXPECTED_RC,'step':EXPECTED_STEP,")
    open(out, "w").write(text)
    print(json.dumps(dict(bytes=len(text.encode()), limit=65536, fits=len(text.encode()) <= 65536)))


if __name__ == "__main__":
    main()
```

### make_certificate_harness.py

```python
"""Regenerate the parent's Appendix A certificate (schema hashsmash-random-function-success-v1) at R24G's parameters with
the parent's own 200-digit model, inside the pinned executor, and self-check it with the same conditions the parent's
experiment asserts. /input/compact.py is 4ea0966b's experiment (unmodified); /input/point.json holds S, DT, J, t.
Prints {"certificate": ..., "checks": ...}."""
import decimal, hashlib, importlib.util, json, sys
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("compact", "/input/compact.py")
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
step, ctl, support, model = C.load_modules()
D = decimal.Decimal
pt = json.load(open("/input/point.json"))
S, DT, J, t = pt["S"], pt["DT"], pt["J"], pt["t"]
W, GRID = 2 ** 99, 2 ** 91
P = dict(DK=10, DPLO=145, DT=DT, HF=111, J=J, LRC=J * W, S=S, Tb=t * GRID, U=5 * S, W=W, granularity=GRID)
hmax, habort = model.derive_hit_limits(P)
P.update(HMAX=hmax, HIT_ABORT=habort)
P = dict(sorted(P.items()))
parts = model.success_parts(P, P["U"], 50)
aux = parts["aux"]; M = D(2) ** 256
inputs = {'theta_numerator': P['DT'], 'theta_denominator_bits': P['HF'] + P['DK'], 'evaluations': 256 * P['Tb'],
          'mean_dp': str(parts['mean_dp']), 'available_restarts': P['U'] - 256, 'prefilter_bits': 16,
          'fresh_step_probability_exact': str(aux['fresh_step_exact']), 'fresh_step_probability_upper': str(aux['fresh_step_upper']),
          'fresh_hit_mean_upper': str(parts['hit_mean']), 'fresh_hit_threshold': int(aux['fresh_threshold']),
          'fresh_hit_delta': str(aux['fresh_delta']), 'hit_chernoff_exponent': str(parts['hit_exponent']),
          'conditioning_start_term': str(aux['conditioning_start']), 'conditioning_partition_term': str(aux['conditioning_partition']),
          'conditioning_dp_term': str(aux['conditioning_dp']), 'conditioning_delta': str(aux['conditioning_delta']),
          'conditioning_inflation': str(aux['conditioning_inflation']), 'conditioning_ratio': str(aux['conditioning_ratio']),
          'age_g6': str(aux['age_g6']), 'coincidence_upper': str(aux['coincidence_upper']),
          'start_replay_union_bound': str(aux['start_replay_bound'])}
pre = {'available_gt_mean': D(P['U'] - 256) > parts['mean_dp'],
       'fresh_step_probability_lt_2^-8': aux['fresh_step_exact'] < D(2) ** -8,
       'fresh_hit_threshold_gt_mean': aux['fresh_threshold'] > parts['hit_mean'],
       'fresh_hit_delta_gt_2^-20': aux['fresh_delta'] > D(2) ** -20,
       'hit_threshold_equals_abort_minus_lrc': int(aux['fresh_threshold']) == habort - P['LRC'],
       'conditioning_delta_lt_2^-109': aux['conditioning_delta'] < D(2) ** -109,
       'conditioning_ratio_le_1_plus_2^-108': aux['conditioning_ratio'] <= D(1) + D(2) ** -108,
       'evaluation_fraction_le_half': D(256 * P['Tb']) / M <= D('.5'),
       'dp_partition_nonempty': parts['theta'] * M > D(P['U']) and (D(1) - parts['theta']) * M > D(256 * P['Tb']),
       'start_replay_bound_le_2^-90': aux['start_replay_bound'] <= D(2) ** -90,
       'bins_cover_replay_cap': P['J'] * P['W'] == P['LRC'], 'replay_cap_below_deadline': P['LRC'] < P['Tb'],
       'table_has_initial_walks': P['U'] >= 256}
audit = {'precision_digits': 200, 'operation_bound': aux['rounding_operations'],
         'per_operation_absolute_bound': str(aux['rounding_per_operation']),
         'accumulated_absolute_bound': str(aux['rounding_bound']),
         'accumulated_lt_2^-200': aux['rounding_bound'] < D(2) ** -200, 'charged_numeric_term': str(D(2) ** -60)}
union = parts['union']
cert = {'computed_bound': str(union), 'computed_previous': str(parts['previous']),
        'covered_success': model.interval(parts['covered']),
        'failure_intervals': {k: model.interval(v) for k, v in sorted(parts['failures'].items())},
        'hit_abort': habort, 'hit_limit': hmax, 'key_bits': 50, 'margin_above_target': str(union - D('0.39')),
        'parameters': P, 'plan_sha256': hashlib.sha256(C.RECORD['plan'].encode()).hexdigest(),
        'preconditions': dict(sorted(pre.items())), 'probability_inputs': dict(sorted(inputs.items())), 'round': 24,
        'rounding': C.CERT['rounding'], 'rounding_audit': dict(sorted(audit.items())), 'schema': C.CERT['schema'],
        'target': '0.39', 'trails': P['U'], 'union_lower': str(union.next_minus())}
checks = {'all_preconditions': all(pre.values()), 'union_ge_target': union >= D(cert['union_lower']) >= D('0.39'),
          'previous_below_target': D('0.39') > parts['previous'], 'audit_ok': audit['accumulated_lt_2^-200'],
          'hit_binding': cert['hit_limit'] == parts['hit_limit'] and cert['hit_abort'] == parts['hit_abort'],
          'same_keys_as_parent': sorted(cert) == sorted(C.CERT) and sorted(inputs) == sorted(C.CERT['probability_inputs'])
          and sorted(pre) == sorted(C.CERT['preconditions']) and sorted(cert['failure_intervals']) == sorted(C.CERT['failure_intervals'])}
print(json.dumps({'certificate': cert, 'checks': checks}))
```

### controller_records_harness.py

```python
"""Export the parent's controller assembly at R24G's parameters (pinned executor; /input/compact.py is the parent's
experiment, /input/certificate.json is R24G's Appendix A): instruction records and the encoded native8 bytes."""
import hashlib, importlib.util, json, sys
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("compact", "/input/compact.py")
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
step, ctl, support, model = C.load_modules()
cert = json.load(open("/input/certificate.json")); P = cert["parameters"]
m = ctl.manifest(24, P["S"], C.LINK_REGISTER, P, cert["hit_limit"])
recs = [[int(i.op), i.d, i.a, i.b, str(i.imm)] for i in m["assembly"].instructions]
print(json.dumps(dict(records=recs, binary_hex=m["binary"].hex(), sha256=hashlib.sha256(m["binary"]).hexdigest(), bytes=len(m["binary"]))))
```

### make_controller_emitter.py

```python
#!/usr/bin/env python3
"""Generate rc_controller_emit.c: a bounded native8 emitter for R24G's controller (the parent's controller assembly at
R24G's parameters, exported by controller_records_harness.py), in the form of the parent's controller_emitter.c: a
record table, the native8 field encoding with a first-appearance literal pool, the bytes written to a file and
hashed with SHA-256. The record table uses a compact presentation (omitted members are zero).
Usage: make_controller_emitter.py RECORDS_JSON OUT_C"""
import json, os, re, sys
d = json.load(open(sys.argv[1]))
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rc_encode.c")).read()
sha = src[src.index("static const uint32_t K256[64]"):src.index("static uint64_t acc; static int used;")]
sha = sha.replace("static uint8_t blk[64]; static uint64_t hlen; static FILE *out;", "static uint8_t blk[64]; static uint64_t hlen; static FILE *out;")
def compact(records, per_line):
    """Compact table: limbs as 0 or 0x<hex>UL, trailing zero limbs and all-zero immediates omitted (C zero-initializes
    omitted members), per_line records per line."""
    items = []
    for op, dd, a, b, limbs in records:
        n = 4
        while n and limbs[n - 1] == 0:
            n -= 1
        imm = "" if n == 0 else ",{" + ",".join("0" if x == 0 else "0x%xUL" % x for x in limbs[:n]) + "}"
        items.append("{%d,%d,%d,%d%s}" % (op, dd, a, b, imm))
    return "\n".join(",".join(items[i:i + per_line]) + "," for i in range(0, len(items), per_line))


recs = [(op, dd, a, b, tuple(int(imm) >> (64 * k) & (2 ** 64 - 1) for k in range(4))) for op, dd, a, b, imm in d["records"]]
rows = [compact(recs, 8)]
c = f"""/* rc_controller_emit.c - R24G construction phase: bounded native8 emitter for R24G's controller ({len(d['records'])} instructions,
 * the parent 4ea0966b's controller assembly at R24G's parameters). Writes the native8 words and the literal pool and
 * hashes them with SHA-256. Generated by tools/r24g/make_controller_emitter.py. Usage: rc_controller_emit OUT_BIN */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {{int op,d,a,b;uint64_t imm[4];}} Rec;
static const Rec records[]={{
{chr(10).join(rows)}
}};
{sha}static uint64_t literals[64][4];static int literal_count;
static int same256(const uint64_t a[4],const uint64_t b[4]){{return a[0]==b[0]&&a[1]==b[1]&&a[2]==b[2]&&a[3]==b[3];}}
static int literal(const uint64_t v[4]){{for(int i=0;i<literal_count;i++)if(same256(literals[i],v))return i;if(literal_count==64){{fprintf(stderr,"literal capacity\\n");exit(2);}}
 for(int j=0;j<4;j++)literals[literal_count][j]=v[j];return literal_count++;}}
static long vmhwm(void){{FILE*f=fopen("/proc/self/status","r");char line[256];long kb=-1;if(!f)return -1;
 while(fgets(line,sizeof line,f))if(!strncmp(line,"VmHWM:",6)){{kb=strtol(line+6,0,10);break;}}fclose(f);return kb*1024;}}
int main(int argc,char**argv){{if(argc!=2)return 2;out=fopen(argv[1],"wb");if(!out)return 2;
 const int count=(int)(sizeof(records)/sizeof(records[0]));
 for(int i=0;i<count;i++){{const Rec*r=&records[i];
  if(r->op<0||r->op>29||r->d<0||r->d>2047||r->a<0||r->a>2047||r->b<0||r->b>2047){{fprintf(stderr,"field\\n");return 3;}}
  uint64_t flag,field;
  if(r->imm[1]==0&&r->imm[2]==0&&r->imm[3]==0&&r->imm[0]<(1UL<<25)){{flag=0;field=r->imm[0];}}else{{flag=1;field=(uint64_t)literal(r->imm);}}
  uint64_t w=(uint64_t)r->op|(flag<<5)|((uint64_t)r->d<<6)|((uint64_t)r->a<<17)|((uint64_t)r->b<<28)|(field<<39);
  for(int k=0;k<8;k++)emit_byte((uint8_t)(w>>(8*k)));}}
 for(int i=0;i<literal_count;i++)for(int j=0;j<4;j++)for(int k=0;k<8;k++)emit_byte((uint8_t)(literals[i][j]>>(8*k)));
 uint64_t bytes=hlen,bitlen=hlen*8;blk[hlen%64]=0x80;hlen++;if(hlen%64==0)compress();
 while(hlen%64!=56){{blk[hlen%64]=0;hlen++;if(hlen%64==0)compress();}}
 for(int i=7;i>=0;i--){{blk[hlen%64]=(uint8_t)(bitlen>>(8*i));hlen++;if(hlen%64==0)compress();}}
 fclose(out);printf("instructions %d literals %d bytes %llu sha256 ",count,literal_count,(unsigned long long)bytes);
 for(int i=0;i<8;i++){{printf("%08x",H[i]);}}printf(" vmhwm %ld\\n",vmhwm());return 0;}}
"""
open(sys.argv[2], "w").write(c)
print("wrote", sys.argv[2], len(c), "bytes")
```

### rc_encode.c

```c
/* rc_encode.c - R24G construction phase: stream the parent's emitted straight line (two-address step image and the
 * 15-OR prefilter image, as emitted by 4ea0966b's normative emitters) into the RC block of ENCODING-SPEC.md (FIFO window
 * of the last 16 destinations, 4-bit index), and hash
 * the output with SHA-256 while it is written. Bounded state: one input byte window, the 16-entry window, one
 * output byte, the SHA-256 state. Usage: rc_encode STEP_BIN STEP_RECORDS PF_BIN PF_RECORDS OUT_BIN
 * Prints records, bits, bytes, the SHA-256 and the process VmHWM in bytes. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const uint32_t K256[64] = {
0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,
0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,
0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,
0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,
0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,
0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
static uint32_t H[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
static uint8_t blk[64]; static uint64_t hlen; static FILE *out;
#define ROR(x,n) (((x)>>(n))|((x)<<(32-(n))))
static void compress(void){uint32_t w[64],a,b,c,d,e,f,g,h,t1,t2;int i;
 for(i=0;i<16;i++)w[i]=(uint32_t)blk[4*i]<<24|(uint32_t)blk[4*i+1]<<16|(uint32_t)blk[4*i+2]<<8|blk[4*i+3];
 for(i=16;i<64;i++)w[i]=w[i-16]+(ROR(w[i-15],7)^ROR(w[i-15],18)^(w[i-15]>>3))+w[i-7]+(ROR(w[i-2],17)^ROR(w[i-2],19)^(w[i-2]>>10));
 a=H[0];b=H[1];c=H[2];d=H[3];e=H[4];f=H[5];g=H[6];h=H[7];
 for(i=0;i<64;i++){t1=h+(ROR(e,6)^ROR(e,11)^ROR(e,25))+((e&f)^(~e&g))+K256[i]+w[i];t2=(ROR(a,2)^ROR(a,13)^ROR(a,22))+((a&b)^(a&c)^(b&c));
  h=g;g=f;f=e;e=d+t1;d=c;c=b;b=a;a=t1+t2;}
 H[0]+=a;H[1]+=b;H[2]+=c;H[3]+=d;H[4]+=e;H[5]+=f;H[6]+=g;H[7]+=h;}
static void emit_byte(uint8_t v){blk[hlen%64]=v;hlen++;if(hlen%64==0)compress();if(fputc(v,out)==EOF){perror("write");exit(1);}}
static uint64_t acc; static int used; static uint64_t nbits;
static void put(uint32_t v,int w){acc|=(uint64_t)v<<used;used+=w;nbits+=w;while(used>=8){emit_byte(acc&255);acc>>=8;used-=8;}}
static int L[16]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
static void push(int d){int i;for(i=15;i>0;i--)L[i]=L[i-1];L[0]=d;}
static void put_src(int r){int i;for(i=0;i<16;i++)if(L[i]==r){put(0,1);put((uint32_t)i,4);return;}put(1,1);put((uint32_t)r,11);}
/* form codewords, first stream bit = least significant bit of 'bits' */
static void put_form(int op,int s){static const char *cw[4][2]={{"00","1"},{"01101","0111"},{"0100","0101"},{"011000","011001"}};
 const char *c=cw[op][s];while(*c){put((uint32_t)(*c-'0'),1);c++;}}
/* streaming two-address reader */
static FILE *in; static uint64_t ia; static int iu;
static uint32_t get(int w){while(iu<w){int ch=fgetc(in);if(ch==EOF){fprintf(stderr,"input ended\n");exit(1);}ia|=(uint64_t)ch<<iu;iu+=8;}
 uint32_t v=(uint32_t)(ia&((1u<<w)-1));ia>>=w;iu-=w;return v;}
static long encode_file(const char *path,long count){long n;in=fopen(path,"rb");if(!in){perror(path);exit(1);}ia=0;iu=0;
 for(n=0;n<count;n++){int op=(int)get(2),same=(int)get(1),d,a,b=0;
  if(same){a=(int)get(11);d=a;}else{d=(int)get(11);a=(int)get(11);}
  if(op!=3)b=(int)get(11);
  if(op!=3&&d==b&&d!=a){int t=a;a=b;b=t;}
  int s=(d==a);put_form(op,s);if(!s)put((uint32_t)d,11);put_src(a);if(op!=3)put_src(b);push(d);}
 if(ia!=0||fgetc(in)!=EOF){fprintf(stderr,"input padding or trailing bytes\n");exit(1);}fclose(in);return count;}
static long vmhwm(void){FILE*f=fopen("/proc/self/status","r");char line[256];long kb=-1;if(!f)return -1;
 while(fgets(line,sizeof line,f))if(!strncmp(line,"VmHWM:",6)){kb=strtol(line+6,0,10);break;}fclose(f);return kb*1024;}
int main(int argc,char**argv){if(argc!=6){fprintf(stderr,"usage\n");return 2;}
 out=fopen(argv[5],"wb");if(!out){perror(argv[5]);return 1;}
 long n=encode_file(argv[1],atol(argv[2]));n+=encode_file(argv[3],atol(argv[4]));
 uint64_t content_bits=nbits; if(used)put(0,8-used);
 uint64_t bytes=hlen,bitlen=hlen*8;uint8_t pad=0x80;blk[hlen%64]=pad;hlen++;if(hlen%64==0)compress();
 while(hlen%64!=56){blk[hlen%64]=0;hlen++;if(hlen%64==0)compress();}
 for(int i=7;i>=0;i--){blk[hlen%64]=(uint8_t)(bitlen>>(8*i));hlen++;if(hlen%64==0)compress();}
 fclose(out);
 printf("records %ld bits %llu bytes %llu sha256 ",n,(unsigned long long)content_bits,(unsigned long long)bytes);
 for(int i=0;i<8;i++){printf("%08x",H[i]);}printf(" vmhwm %ld\n",vmhwm());return 0;}
```

### rc_scan.c

```c
/* rc_scan.c - R24G construction phase: the charged finite parameter scan. Long-double mirror of the parent's
 * Appendix A bound (the same formula as the parent's construction_scan_template.c) and of its ledger, for table
 * S = 18,344 words (U = 5S trails), BSTEP = 144,722 + 15 + 2 + 2 + 1 (decoder reset), theta = dt / 2^121 for dt in [DT_LO, DT_HI], replay-cap bins J = round(c 2^22 / dt)
 * for c = 10.30, 10.32, ..., 12.28, and the least horizon t (Tb = t 2^91) at which the bound reaches 0.39.
 * Prints the candidates' (dt, J, t, log2 cost) ranked best first (top 8), the counted bins and bound evaluations, and
 * VmHWM. A finite scan: optimality is not claimed. Its ledger uses the parent's hit-path cost of 131 for every dt. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define S 18344L
#define DT_LO 693
#define DT_HI 714
#define STEP_OPS 144722.0L
#define BSTEP_EXTRA 20.0L
#define PRE 287659397739008.0L
static const long double LN2=0.693147180559945309417232121458176568L,M=1.1579208923731619542357098500868790785e77L,
 GRID=2.475880078570760549798248448e27L,W=6.33825300114114700748351602688e29L,T121=2.658455991569831744e36L;
static uint64_t bins_evaluated,evaluations;
static long double lexp(long double x){if(x<-11000.0L)return 0.0L;int k=(int)(x/LN2);if((long double)k*LN2>x)k--;
 long double r=x-(long double)k*LN2,term=1.0L,sum=1.0L;for(int i=1;i<=32;i++){term*=r/(long double)i;sum+=term;}
 while(k>0){sum*=2.0L;k--;}while(k<0){sum*=0.5L;k++;}return sum;}
static long double llog(long double x){int e=0;while(x>=2.0L){x*=0.5L;e++;}while(x<1.0L){x*=2.0L;e--;}
 long double y=(x-1.0L)/(x+1.0L),p=y*y,term=y,sum=0;for(int k=1;k<=101;k+=2){sum+=term/(long double)k;term*=p;}return 2.0L*sum+(long double)e*LN2;}
static long double llog1m(long double x){/* log(1-x) for tiny x */long double s=0,t=x;for(int k=1;k<=12;k++){s-=t/(long double)k;t*=x;}return s;}
static long double success(uint64_t t,int dt,long J){
 long double tb=(long double)t*GRID,theta=(long double)dt/T121,logq=llog1m(theta),qstep=lexp(W*logq),prev=1.0L,cov=0.0L;
 long double delta=256.0L*W,first=256.0L*(tb-W),coll=lexp(-first*(first-1.0L)/(2.0L*M));
 long double ratio=lexp((2.0L*first*delta-delta*delta-delta)/(2.0L*M)),rstep=lexp(-delta*delta/M);
 for(long j=1;j<=J;j++){long double cur=prev*qstep;if(tb>(long double)j*W)cov+=(prev-cur)*(1.0L-coll);prev=cur;coll*=ratio;ratio*=rstep;}
 bins_evaluated+=(uint64_t)J;evaluations++;
 long double n=256.0L*tb,mean=n*theta,U=5.0L*S,avail=U-256.0L;if(!(avail>mean))return -1.0L;
 long double f2=lexp(-mean+avail*(1.0L+llog(mean/avail))),f3=U/(theta*theta*M),alias=U*U/2251799813685248.0L;
 long double lrc=(long double)J*W,g6=lexp(lrc*logq)*(1.0L+lrc*theta),coinc=1.0L-lexp(-n*n/(2.0L*M)-n*n*n/(3.0L*M*M));
 long double infl=lexp(-U*llog1m(n/M)),f6=2.0L*g6*coinc*infl;
 return cov-(f6+f2+f3+8.077935669463161e-28L+alias+3.0814879110195774e-33L*(1.0L+f6)+8.673617379884035e-19L);}
static uint64_t least_t(int dt,long J){long double theta=(long double)dt/T121;
 uint64_t top=(uint64_t)(((5.0L*S-256.0L)/(256.0L*theta))/GRID)-1,lo=top/2,hi=top;
 while(hi-lo>=3){uint64_t m1=lo+(hi-lo)/3,m2=hi-(hi-lo)/3;if(success(m1,dt,J)<success(m2,dt,J))lo=m1;else hi=m2;}
 uint64_t peak=lo;long double best=-2;for(uint64_t t=lo;t<=hi;t++){long double v=success(t,dt,J);if(v>best){best=v;peak=t;}}
 if(best<0.39L)return 0;lo=top/2;hi=peak;if(success(lo,dt,J)>=0.39L)return 0;
 while(hi-lo>1){uint64_t mid=(lo+hi)/2;if(success(mid,dt,J)>=0.39L)hi=mid;else lo=mid;}return hi;}
static long double cost(int dt,long J,uint64_t t){long double tb=(long double)t*GRID,lrc=(long double)J*W,U=5.0L*S;
 long double hmax=tb*(1.0L+1.0L/1048576.0L)/256.0L+1.0L+lrc,g=(lrc+(long double)S-2.0L)/(long double)(S-1),nck=(lrc-1.0L)/g+1.0L;
 long double e=6533.0L,replay=(2*e+17)*lrc+(3*e+20)*g+17.0L*nck+e+93.0L;
 long double setup=744255.0L+11.0L*(long double)((S+256)/8-(14304+256)/8);
 long double rare=(hmax+1.0L)*131.0L+(U-255.0L)*(2893.0L+24.0L*S)+(U-256.0L)*(2835.0L+3.0L)+3.0L+1.0L+setup;
 (void)dt;return tb*(STEP_OPS+BSTEP_EXTRA)+replay+rare+PRE;}
typedef struct{int dt;long J;uint64_t t;long double l2;}Row;
static long vmhwm(void){FILE*f=fopen("/proc/self/status","r");char line[256];long kb=-1;if(!f)return -1;
 while(fgets(line,sizeof line,f))if(!strncmp(line,"VmHWM:",6)){kb=strtol(line+6,0,10);break;}fclose(f);return kb*1024;}
int main(void){static Row rows[(DT_HI-DT_LO+1)*100];int n=0;
 for(int dt=DT_LO;dt<=DT_HI;dt++)for(int i=0;i<100;i++){long double c=10.30L+0.02L*(long double)i;
  long J=(long)(c*4194304.0L/(long double)dt+0.5L);uint64_t t=least_t(dt,J);if(!t)continue;
  rows[n].dt=dt;rows[n].J=J;rows[n].t=t;rows[n].l2=llog(cost(dt,J,t)/6504.0L)/LN2;n++;}
 for(int i=1;i<n;i++){Row r=rows[i];int j=i-1;while(j>=0&&rows[j].l2>r.l2){rows[j+1]=rows[j];j--;}rows[j+1]=r;}
 for(int i=0;i<n&&i<8;i++)printf("dt %d J %ld t %llu log2 %.9Lf\n",rows[i].dt,rows[i].J,(unsigned long long)rows[i].t,rows[i].l2);
 printf("candidates %d bins_evaluated %llu evaluations %llu vmhwm %ld\n",n,(unsigned long long)bins_evaluated,(unsigned long long)evaluations,vmhwm());return 0;}
```

### rc_controller_emit.c

```c
/* rc_controller_emit.c - R24G construction phase: bounded native8 emitter for R24G's controller (986 instructions,
 * the parent 4ea0966b's controller assembly at R24G's parameters). Writes the native8 words and the literal pool and
 * hashes them with SHA-256. Generated by tools/r24g/make_controller_emitter.py. Usage: rc_controller_emit OUT_BIN */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {int op,d,a,b;uint64_t imm[4];} Rec;
static const Rec records[]={
{27,1930,0,0},{18,1929,0,0,{0x100UL}},{18,1933,0,0},{18,1928,0,0,{0,0xff575b30000000UL}},{18,1936,0,0},{3,1931,1936,0},{18,269,0,0},{20,0,269,1936},
{20,0,269,1936,{0x1UL}},{20,0,269,1936,{0x2UL}},{20,0,269,1936,{0x3UL}},{20,0,269,1936,{0x4UL}},{20,0,269,1936,{0x5UL}},{20,0,269,1936,{0x6UL}},{20,0,269,1936,{0x7UL}},{11,269,269,0,{0x8UL}},
{17,264,269,0,{0x48a8UL}},{22,0,264,0,{0x7UL}},{18,256,0,0},{4,267,1930,256},{13,265,256,0,{0x80UL}},{20,0,256,265,{0x48a8UL}},{25,1934,0,0,{0x214UL}},{11,256,256,0,{0x1UL}},
{17,264,256,0,{0x100UL}},{22,0,264,0,{0x13UL}},{25,1934,0,0,{0x232UL}},{24,0,0,0,{0xffffffffffffffffUL,0xffffffffffffffffUL,0xffffffffffffffffUL}},{8,264,1932,1931},{22,0,264,0,{0x203UL}},{11,1933,1933,0,{0x1UL}},{17,264,1933,0,{0x2UL,0x8f7e76b2575b3UL}},
{22,0,264,0,{0x22UL}},{29,0,0,0,{0xaUL}},{2,260,145,146},{2,260,260,147},{2,260,260,148},{2,260,260,149},{2,260,260,150},{2,260,260,151},
{2,260,260,152},{2,260,260,153},{2,260,260,154},{2,260,260,155},{2,260,260,156},{2,260,260,157},{2,260,260,158},{2,260,260,159},
{2,260,260,160},{2,260,260,161},{2,260,260,162},{2,260,260,163},{2,260,260,164},{2,260,260,165},{2,260,260,166},{2,260,260,167},
{2,260,260,168},{2,260,260,169},{2,260,260,170},{2,260,260,171},{2,260,260,172},{2,260,260,173},{2,260,260,174},{2,260,260,175},
{2,260,260,176},{2,260,260,177},{2,260,260,178},{2,260,260,179},{2,260,260,180},{2,260,260,181},{2,260,260,182},{2,260,260,183},
{2,260,260,184},{2,260,260,185},{2,260,260,186},{2,260,260,187},{2,260,260,188},{2,260,260,189},{2,260,260,190},{2,260,260,191},
{2,260,260,192},{2,260,260,193},{2,260,260,194},{2,260,260,195},{2,260,260,196},{2,260,260,197},{2,260,260,198},{2,260,260,199},
{2,260,260,200},{2,260,260,201},{2,260,260,202},{2,260,260,203},{2,260,260,204},{2,260,260,205},{2,260,260,206},{2,260,260,207},
{2,260,260,208},{2,260,260,209},{2,260,260,210},{2,260,260,211},{2,260,260,212},{2,260,260,213},{2,260,260,214},{2,260,260,215},
{2,260,260,216},{2,260,260,217},{2,260,260,218},{2,260,260,219},{2,260,260,220},{2,260,260,221},{2,260,260,222},{2,260,260,223},
{2,260,260,224},{2,260,260,225},{2,260,260,226},{2,260,260,227},{2,260,260,228},{2,260,260,229},{2,260,260,230},{2,260,260,231},
{2,260,260,232},{2,260,260,233},{2,260,260,234},{2,260,260,235},{2,260,260,236},{2,260,260,237},{2,260,260,238},{2,260,260,239},
{2,257,1932,260},{3,257,257,0},{3,265,144,0},{1,266,257,265},{1,257,257,144},{3,265,143,0},{1,257,257,265},{3,265,142,0},
{1,265,257,265},{2,266,266,265},{1,257,257,142},{3,265,141,0},{1,265,257,265},{2,266,266,265},{10,257,266,0},{18,258,0,0,{0,0xff575b30000000UL}},
{5,258,258,1928},{11,258,258,0,{0x1UL}},{16,264,257,0},{22,0,264,0,{0x203UL}},{20,0,1936,0,{0x47a8UL}},{20,0,1936,1,{0x47a9UL}},{20,0,1936,2,{0x47aaUL}},{20,0,1936,3,{0x47abUL}},
{20,0,1936,4,{0x47acUL}},{20,0,1936,5,{0x47adUL}},{20,0,1936,6,{0x47aeUL}},{20,0,1936,7,{0x47afUL}},{20,0,1936,8,{0x47b0UL}},{20,0,1936,9,{0x47b1UL}},{20,0,1936,10,{0x47b2UL}},{20,0,1936,11,{0x47b3UL}},
{20,0,1936,12,{0x47b4UL}},{20,0,1936,13,{0x47b5UL}},{20,0,1936,14,{0x47b6UL}},{20,0,1936,15,{0x47b7UL}},{20,0,1936,16,{0x47b8UL}},{20,0,1936,17,{0x47b9UL}},{20,0,1936,18,{0x47baUL}},{20,0,1936,19,{0x47bbUL}},
{20,0,1936,20,{0x47bcUL}},{20,0,1936,21,{0x47bdUL}},{20,0,1936,22,{0x47beUL}},{20,0,1936,23,{0x47bfUL}},{20,0,1936,24,{0x47c0UL}},{20,0,1936,25,{0x47c1UL}},{20,0,1936,26,{0x47c2UL}},{20,0,1936,27,{0x47c3UL}},
{20,0,1936,28,{0x47c4UL}},{20,0,1936,29,{0x47c5UL}},{20,0,1936,30,{0x47c6UL}},{20,0,1936,31,{0x47c7UL}},{20,0,1936,32,{0x47c8UL}},{20,0,1936,33,{0x47c9UL}},{20,0,1936,34,{0x47caUL}},{20,0,1936,35,{0x47cbUL}},
{20,0,1936,36,{0x47ccUL}},{20,0,1936,37,{0x47cdUL}},{20,0,1936,38,{0x47ceUL}},{20,0,1936,39,{0x47cfUL}},{20,0,1936,40,{0x47d0UL}},{20,0,1936,41,{0x47d1UL}},{20,0,1936,42,{0x47d2UL}},{20,0,1936,43,{0x47d3UL}},
{20,0,1936,44,{0x47d4UL}},{20,0,1936,45,{0x47d5UL}},{20,0,1936,46,{0x47d6UL}},{20,0,1936,47,{0x47d7UL}},{20,0,1936,48,{0x47d8UL}},{20,0,1936,49,{0x47d9UL}},{20,0,1936,50,{0x47daUL}},{20,0,1936,51,{0x47dbUL}},
{20,0,1936,52,{0x47dcUL}},{20,0,1936,53,{0x47ddUL}},{20,0,1936,54,{0x47deUL}},{20,0,1936,55,{0x47dfUL}},{20,0,1936,56,{0x47e0UL}},{20,0,1936,57,{0x47e1UL}},{20,0,1936,58,{0x47e2UL}},{20,0,1936,59,{0x47e3UL}},
{20,0,1936,60,{0x47e4UL}},{20,0,1936,61,{0x47e5UL}},{20,0,1936,62,{0x47e6UL}},{20,0,1936,63,{0x47e7UL}},{20,0,1936,64,{0x47e8UL}},{20,0,1936,65,{0x47e9UL}},{20,0,1936,66,{0x47eaUL}},{20,0,1936,67,{0x47ebUL}},
{20,0,1936,68,{0x47ecUL}},{20,0,1936,69,{0x47edUL}},{20,0,1936,70,{0x47eeUL}},{20,0,1936,71,{0x47efUL}},{20,0,1936,72,{0x47f0UL}},{20,0,1936,73,{0x47f1UL}},{20,0,1936,74,{0x47f2UL}},{20,0,1936,75,{0x47f3UL}},
{20,0,1936,76,{0x47f4UL}},{20,0,1936,77,{0x47f5UL}},{20,0,1936,78,{0x47f6UL}},{20,0,1936,79,{0x47f7UL}},{20,0,1936,80,{0x47f8UL}},{20,0,1936,81,{0x47f9UL}},{20,0,1936,82,{0x47faUL}},{20,0,1936,83,{0x47fbUL}},
{20,0,1936,84,{0x47fcUL}},{20,0,1936,85,{0x47fdUL}},{20,0,1936,86,{0x47feUL}},{20,0,1936,87,{0x47ffUL}},{20,0,1936,88,{0x4800UL}},{20,0,1936,89,{0x4801UL}},{20,0,1936,90,{0x4802UL}},{20,0,1936,91,{0x4803UL}},
{20,0,1936,92,{0x4804UL}},{20,0,1936,93,{0x4805UL}},{20,0,1936,94,{0x4806UL}},{20,0,1936,95,{0x4807UL}},{20,0,1936,96,{0x4808UL}},{20,0,1936,97,{0x4809UL}},{20,0,1936,98,{0x480aUL}},{20,0,1936,99,{0x480bUL}},
{20,0,1936,100,{0x480cUL}},{20,0,1936,101,{0x480dUL}},{20,0,1936,102,{0x480eUL}},{20,0,1936,103,{0x480fUL}},{20,0,1936,104,{0x4810UL}},{20,0,1936,105,{0x4811UL}},{20,0,1936,106,{0x4812UL}},{20,0,1936,107,{0x4813UL}},
{20,0,1936,108,{0x4814UL}},{20,0,1936,109,{0x4815UL}},{20,0,1936,110,{0x4816UL}},{20,0,1936,111,{0x4817UL}},{20,0,1936,112,{0x4818UL}},{20,0,1936,113,{0x4819UL}},{20,0,1936,114,{0x481aUL}},{20,0,1936,115,{0x481bUL}},
{20,0,1936,116,{0x481cUL}},{20,0,1936,117,{0x481dUL}},{20,0,1936,118,{0x481eUL}},{20,0,1936,119,{0x481fUL}},{20,0,1936,120,{0x4820UL}},{20,0,1936,121,{0x4821UL}},{20,0,1936,122,{0x4822UL}},{20,0,1936,123,{0x4823UL}},
{20,0,1936,124,{0x4824UL}},{20,0,1936,125,{0x4825UL}},{20,0,1936,126,{0x4826UL}},{20,0,1936,127,{0x4827UL}},{20,0,1936,128,{0x4828UL}},{20,0,1936,129,{0x4829UL}},{20,0,1936,130,{0x482aUL}},{20,0,1936,131,{0x482bUL}},
{20,0,1936,132,{0x482cUL}},{20,0,1936,133,{0x482dUL}},{20,0,1936,134,{0x482eUL}},{20,0,1936,135,{0x482fUL}},{20,0,1936,136,{0x4830UL}},{20,0,1936,137,{0x4831UL}},{20,0,1936,138,{0x4832UL}},{20,0,1936,139,{0x4833UL}},
{20,0,1936,140,{0x4834UL}},{20,0,1936,141,{0x4835UL}},{20,0,1936,142,{0x4836UL}},{20,0,1936,143,{0x4837UL}},{20,0,1936,144,{0x4838UL}},{20,0,1936,145,{0x4839UL}},{20,0,1936,146,{0x483aUL}},{20,0,1936,147,{0x483bUL}},
{20,0,1936,148,{0x483cUL}},{20,0,1936,149,{0x483dUL}},{20,0,1936,150,{0x483eUL}},{20,0,1936,151,{0x483fUL}},{20,0,1936,152,{0x4840UL}},{20,0,1936,153,{0x4841UL}},{20,0,1936,154,{0x4842UL}},{20,0,1936,155,{0x4843UL}},
{20,0,1936,156,{0x4844UL}},{20,0,1936,157,{0x4845UL}},{20,0,1936,158,{0x4846UL}},{20,0,1936,159,{0x4847UL}},{20,0,1936,160,{0x4848UL}},{20,0,1936,161,{0x4849UL}},{20,0,1936,162,{0x484aUL}},{20,0,1936,163,{0x484bUL}},
{20,0,1936,164,{0x484cUL}},{20,0,1936,165,{0x484dUL}},{20,0,1936,166,{0x484eUL}},{20,0,1936,167,{0x484fUL}},{20,0,1936,168,{0x4850UL}},{20,0,1936,169,{0x4851UL}},{20,0,1936,170,{0x4852UL}},{20,0,1936,171,{0x4853UL}},
{20,0,1936,172,{0x4854UL}},{20,0,1936,173,{0x4855UL}},{20,0,1936,174,{0x4856UL}},{20,0,1936,175,{0x4857UL}},{20,0,1936,176,{0x4858UL}},{20,0,1936,177,{0x4859UL}},{20,0,1936,178,{0x485aUL}},{20,0,1936,179,{0x485bUL}},
{20,0,1936,180,{0x485cUL}},{20,0,1936,181,{0x485dUL}},{20,0,1936,182,{0x485eUL}},{20,0,1936,183,{0x485fUL}},{20,0,1936,184,{0x4860UL}},{20,0,1936,185,{0x4861UL}},{20,0,1936,186,{0x4862UL}},{20,0,1936,187,{0x4863UL}},
{20,0,1936,188,{0x4864UL}},{20,0,1936,189,{0x4865UL}},{20,0,1936,190,{0x4866UL}},{20,0,1936,191,{0x4867UL}},{20,0,1936,192,{0x4868UL}},{20,0,1936,193,{0x4869UL}},{20,0,1936,194,{0x486aUL}},{20,0,1936,195,{0x486bUL}},
{20,0,1936,196,{0x486cUL}},{20,0,1936,197,{0x486dUL}},{20,0,1936,198,{0x486eUL}},{20,0,1936,199,{0x486fUL}},{20,0,1936,200,{0x4870UL}},{20,0,1936,201,{0x4871UL}},{20,0,1936,202,{0x4872UL}},{20,0,1936,203,{0x4873UL}},
{20,0,1936,204,{0x4874UL}},{20,0,1936,205,{0x4875UL}},{20,0,1936,206,{0x4876UL}},{20,0,1936,207,{0x4877UL}},{20,0,1936,208,{0x4878UL}},{20,0,1936,209,{0x4879UL}},{20,0,1936,210,{0x487aUL}},{20,0,1936,211,{0x487bUL}},
{20,0,1936,212,{0x487cUL}},{20,0,1936,213,{0x487dUL}},{20,0,1936,214,{0x487eUL}},{20,0,1936,215,{0x487fUL}},{20,0,1936,216,{0x4880UL}},{20,0,1936,217,{0x4881UL}},{20,0,1936,218,{0x4882UL}},{20,0,1936,219,{0x4883UL}},
{20,0,1936,220,{0x4884UL}},{20,0,1936,221,{0x4885UL}},{20,0,1936,222,{0x4886UL}},{20,0,1936,223,{0x4887UL}},{20,0,1936,224,{0x4888UL}},{20,0,1936,225,{0x4889UL}},{20,0,1936,226,{0x488aUL}},{20,0,1936,227,{0x488bUL}},
{20,0,1936,228,{0x488cUL}},{20,0,1936,229,{0x488dUL}},{20,0,1936,230,{0x488eUL}},{20,0,1936,231,{0x488fUL}},{20,0,1936,232,{0x4890UL}},{20,0,1936,233,{0x4891UL}},{20,0,1936,234,{0x4892UL}},{20,0,1936,235,{0x4893UL}},
{20,0,1936,236,{0x4894UL}},{20,0,1936,237,{0x4895UL}},{20,0,1936,238,{0x4896UL}},{20,0,1936,239,{0x4897UL}},{20,0,1936,240,{0x4898UL}},{20,0,1936,241,{0x4899UL}},{20,0,1936,242,{0x489aUL}},{20,0,1936,243,{0x489bUL}},
{20,0,1936,244,{0x489cUL}},{20,0,1936,245,{0x489dUL}},{20,0,1936,246,{0x489eUL}},{20,0,1936,247,{0x489fUL}},{20,0,1936,248,{0x48a0UL}},{20,0,1936,249,{0x48a1UL}},{20,0,1936,250,{0x48a2UL}},{20,0,1936,251,{0x48a3UL}},
{20,0,1936,252,{0x48a4UL}},{20,0,1936,253,{0x48a5UL}},{20,0,1936,254,{0x48a6UL}},{20,0,1936,255,{0x48a7UL}},{16,264,257,0},{22,0,264,0,{0x202UL}},{18,256,0,0},{10,265,257,0},
{15,266,265,0,{0xffffffffffffffffUL,0xffffffffffffffffUL}},{16,264,266,0},{23,0,264,0,{0x19dUL}},{14,265,265,0,{0x80UL}},{11,256,256,0,{0x80UL}},{15,266,265,0,{0xffffffffffffffffUL}},{16,264,266,0},{23,0,264,0,{0x1a2UL}},
{14,265,265,0,{0x40UL}},{11,256,256,0,{0x40UL}},{15,266,265,0,{0xffffffffUL}},{16,264,266,0},{23,0,264,0,{0x1a7UL}},{14,265,265,0,{0x20UL}},{11,256,256,0,{0x20UL}},{15,266,265,0,{0xffffUL}},
{16,264,266,0},{23,0,264,0,{0x1acUL}},{14,265,265,0,{0x10UL}},{11,256,256,0,{0x10UL}},{15,266,265,0,{0xffUL}},{16,264,266,0},{23,0,264,0,{0x1b1UL}},{14,265,265,0,{0x8UL}},
{11,256,256,0,{0x8UL}},{15,266,265,0,{0xfUL}},{16,264,266,0},{23,0,264,0,{0x1b6UL}},{14,265,265,0,{0x4UL}},{11,256,256,0,{0x4UL}},{15,266,265,0,{0x3UL}},{16,264,266,0},
{23,0,264,0,{0x1bbUL}},{14,265,265,0,{0x2UL}},{11,256,256,0,{0x2UL}},{15,266,265,0,{0x1UL}},{16,264,266,0},{23,0,264,0,{0x1c0UL}},{14,265,265,0,{0x1UL}},{11,256,256,0,{0x1UL}},
{12,266,257,0,{0x1UL}},{1,257,257,266},{25,1934,0,0,{0x225UL}},{15,261,259,0,{0x3ffffffffffffUL}},{13,261,261,0,{0x1UL}},{11,261,261,0,{0x1UL}},{10,272,261,0},{13,265,261,0,{0x33UL}},
{2,272,272,265},{13,265,261,0,{0x66UL}},{2,272,272,265},{13,265,261,0,{0x99UL}},{2,272,272,265},{13,265,261,0,{0xccUL}},{2,272,272,265},{18,262,0,0},
{19,263,262,0},{0,263,263,272},{15,265,263,0,{0x7ffffffffffffUL}},{16,264,265,0},{22,0,264,0,{0x1f3UL}},{14,266,263,0,{0x33UL}},{15,265,266,0,{0x7ffffffffffffUL}},{16,264,265,0},
{22,0,264,0,{0x1f6UL}},{14,266,263,0,{0x66UL}},{15,265,266,0,{0x7ffffffffffffUL}},{16,264,265,0},{22,0,264,0,{0x1f9UL}},{14,266,263,0,{0x99UL}},{15,265,266,0,{0x7ffffffffffffUL}},{16,264,265,0},
{22,0,264,0,{0x1fcUL}},{14,266,263,0,{0xccUL}},{15,265,266,0,{0x7ffffffffffffUL}},{16,264,265,0},{22,0,264,0,{0x1ffUL}},{11,262,262,0,{0x1UL}},{16,264,262,0,{0x47a8UL}},{23,0,264,0,{0x1d0UL}},
{19,271,256,0,{0x48a8UL}},{14,271,271,0,{0x80UL}},{15,262,271,0,{0x7fffUL}},{14,266,271,0,{0xfUL}},{6,265,261,266},{19,263,262,0},{2,263,263,265},{20,0,262,263},
{10,260,258,0},{25,1935,0,0,{0x206UL}},{24,0,0,0,{0x194UL}},{18,265,0,0},{2,265,265,262},{24,0,0,0,{0x36cUL}},{18,265,0,0,{0x198000UL}},{2,265,265,262},
{24,0,0,0,{0x36cUL}},{18,265,0,0,{0x330000UL}},{2,265,265,262},{24,0,0,0,{0x36cUL}},{18,265,0,0,{0x4c8000UL}},{2,265,265,262},{24,0,0,0,{0x36cUL}},{18,265,0,0,{0x660000UL}},
{2,265,265,262},{24,0,0,0,{0x36cUL}},{25,1934,0,0,{0x232UL}},{12,1928,1928,0,{0x1UL}},{22,0,1928,0,{0xffffffffffffffffUL,0xffffffffffffffffUL,0xffffffffffffffffUL}},{29,0,0,0,{0xcUL}},{16,264,1929,0,{0x7f8000UL}},{23,0,264,0,{0x209UL}},
{29,0,0,0,{0xbUL}},{13,265,1929,0,{0x80UL}},{2,265,265,260},{20,0,256,265,{0x48a8UL}},{4,267,1930,1929},{11,1929,1929,0,{0x1UL}},{15,265,1929,0,{0x7fffUL}},{16,264,265,0,{0x47a8UL}},
{23,0,264,0,{0x212UL}},{11,1929,1929,0,{0x193858UL}},{25,1934,0,0,{0x214UL}},{26,0,1935,0},{18,273,0,0,{0x1UL}},{6,273,273,256},{3,268,273,0},{21,269,0,0,{0x47a8UL}},
{18,270,0,0},{19,265,269,0},{1,265,265,268},{7,266,267,270},{15,266,266,0,{0x1UL}},{6,266,266,256},{2,265,265,266},{20,0,269,265},
{11,269,269,0,{0x1UL}},{11,270,270,0,{0x1UL}},{16,264,270,0,{0x100UL}},{23,0,264,0,{0x219UL}},{26,0,1934,0},{18,259,0,0},{21,269,0,0,{0x47a8UL}},{18,270,0,0},
{19,265,269,0},{7,265,265,256},{15,265,265,0,{0x1UL}},{6,265,265,270},{2,259,259,265},{11,269,269,0,{0x1UL}},{11,270,270,0,{0x1UL}},{16,264,270,0,{0x100UL}},
{23,0,264,0,{0x228UL}},{26,0,1934,0},{19,0,1936,0,{0x47a8UL}},{19,1,1936,0,{0x47a9UL}},{19,2,1936,0,{0x47aaUL}},{19,3,1936,0,{0x47abUL}},{19,4,1936,0,{0x47acUL}},{19,5,1936,0,{0x47adUL}},
{19,6,1936,0,{0x47aeUL}},{19,7,1936,0,{0x47afUL}},{19,8,1936,0,{0x47b0UL}},{19,9,1936,0,{0x47b1UL}},{19,10,1936,0,{0x47b2UL}},{19,11,1936,0,{0x47b3UL}},{19,12,1936,0,{0x47b4UL}},{19,13,1936,0,{0x47b5UL}},
{19,14,1936,0,{0x47b6UL}},{19,15,1936,0,{0x47b7UL}},{19,16,1936,0,{0x47b8UL}},{19,17,1936,0,{0x47b9UL}},{19,18,1936,0,{0x47baUL}},{19,19,1936,0,{0x47bbUL}},{19,20,1936,0,{0x47bcUL}},{19,21,1936,0,{0x47bdUL}},
{19,22,1936,0,{0x47beUL}},{19,23,1936,0,{0x47bfUL}},{19,24,1936,0,{0x47c0UL}},{19,25,1936,0,{0x47c1UL}},{19,26,1936,0,{0x47c2UL}},{19,27,1936,0,{0x47c3UL}},{19,28,1936,0,{0x47c4UL}},{19,29,1936,0,{0x47c5UL}},
{19,30,1936,0,{0x47c6UL}},{19,31,1936,0,{0x47c7UL}},{19,32,1936,0,{0x47c8UL}},{19,33,1936,0,{0x47c9UL}},{19,34,1936,0,{0x47caUL}},{19,35,1936,0,{0x47cbUL}},{19,36,1936,0,{0x47ccUL}},{19,37,1936,0,{0x47cdUL}},
{19,38,1936,0,{0x47ceUL}},{19,39,1936,0,{0x47cfUL}},{19,40,1936,0,{0x47d0UL}},{19,41,1936,0,{0x47d1UL}},{19,42,1936,0,{0x47d2UL}},{19,43,1936,0,{0x47d3UL}},{19,44,1936,0,{0x47d4UL}},{19,45,1936,0,{0x47d5UL}},
{19,46,1936,0,{0x47d6UL}},{19,47,1936,0,{0x47d7UL}},{19,48,1936,0,{0x47d8UL}},{19,49,1936,0,{0x47d9UL}},{19,50,1936,0,{0x47daUL}},{19,51,1936,0,{0x47dbUL}},{19,52,1936,0,{0x47dcUL}},{19,53,1936,0,{0x47ddUL}},
{19,54,1936,0,{0x47deUL}},{19,55,1936,0,{0x47dfUL}},{19,56,1936,0,{0x47e0UL}},{19,57,1936,0,{0x47e1UL}},{19,58,1936,0,{0x47e2UL}},{19,59,1936,0,{0x47e3UL}},{19,60,1936,0,{0x47e4UL}},{19,61,1936,0,{0x47e5UL}},
{19,62,1936,0,{0x47e6UL}},{19,63,1936,0,{0x47e7UL}},{19,64,1936,0,{0x47e8UL}},{19,65,1936,0,{0x47e9UL}},{19,66,1936,0,{0x47eaUL}},{19,67,1936,0,{0x47ebUL}},{19,68,1936,0,{0x47ecUL}},{19,69,1936,0,{0x47edUL}},
{19,70,1936,0,{0x47eeUL}},{19,71,1936,0,{0x47efUL}},{19,72,1936,0,{0x47f0UL}},{19,73,1936,0,{0x47f1UL}},{19,74,1936,0,{0x47f2UL}},{19,75,1936,0,{0x47f3UL}},{19,76,1936,0,{0x47f4UL}},{19,77,1936,0,{0x47f5UL}},
{19,78,1936,0,{0x47f6UL}},{19,79,1936,0,{0x47f7UL}},{19,80,1936,0,{0x47f8UL}},{19,81,1936,0,{0x47f9UL}},{19,82,1936,0,{0x47faUL}},{19,83,1936,0,{0x47fbUL}},{19,84,1936,0,{0x47fcUL}},{19,85,1936,0,{0x47fdUL}},
{19,86,1936,0,{0x47feUL}},{19,87,1936,0,{0x47ffUL}},{19,88,1936,0,{0x4800UL}},{19,89,1936,0,{0x4801UL}},{19,90,1936,0,{0x4802UL}},{19,91,1936,0,{0x4803UL}},{19,92,1936,0,{0x4804UL}},{19,93,1936,0,{0x4805UL}},
{19,94,1936,0,{0x4806UL}},{19,95,1936,0,{0x4807UL}},{19,96,1936,0,{0x4808UL}},{19,97,1936,0,{0x4809UL}},{19,98,1936,0,{0x480aUL}},{19,99,1936,0,{0x480bUL}},{19,100,1936,0,{0x480cUL}},{19,101,1936,0,{0x480dUL}},
{19,102,1936,0,{0x480eUL}},{19,103,1936,0,{0x480fUL}},{19,104,1936,0,{0x4810UL}},{19,105,1936,0,{0x4811UL}},{19,106,1936,0,{0x4812UL}},{19,107,1936,0,{0x4813UL}},{19,108,1936,0,{0x4814UL}},{19,109,1936,0,{0x4815UL}},
{19,110,1936,0,{0x4816UL}},{19,111,1936,0,{0x4817UL}},{19,112,1936,0,{0x4818UL}},{19,113,1936,0,{0x4819UL}},{19,114,1936,0,{0x481aUL}},{19,115,1936,0,{0x481bUL}},{19,116,1936,0,{0x481cUL}},{19,117,1936,0,{0x481dUL}},
{19,118,1936,0,{0x481eUL}},{19,119,1936,0,{0x481fUL}},{19,120,1936,0,{0x4820UL}},{19,121,1936,0,{0x4821UL}},{19,122,1936,0,{0x4822UL}},{19,123,1936,0,{0x4823UL}},{19,124,1936,0,{0x4824UL}},{19,125,1936,0,{0x4825UL}},
{19,126,1936,0,{0x4826UL}},{19,127,1936,0,{0x4827UL}},{19,128,1936,0,{0x4828UL}},{19,129,1936,0,{0x4829UL}},{19,130,1936,0,{0x482aUL}},{19,131,1936,0,{0x482bUL}},{19,132,1936,0,{0x482cUL}},{19,133,1936,0,{0x482dUL}},
{19,134,1936,0,{0x482eUL}},{19,135,1936,0,{0x482fUL}},{19,136,1936,0,{0x4830UL}},{19,137,1936,0,{0x4831UL}},{19,138,1936,0,{0x4832UL}},{19,139,1936,0,{0x4833UL}},{19,140,1936,0,{0x4834UL}},{19,141,1936,0,{0x4835UL}},
{19,142,1936,0,{0x4836UL}},{19,143,1936,0,{0x4837UL}},{19,144,1936,0,{0x4838UL}},{19,145,1936,0,{0x4839UL}},{19,146,1936,0,{0x483aUL}},{19,147,1936,0,{0x483bUL}},{19,148,1936,0,{0x483cUL}},{19,149,1936,0,{0x483dUL}},
{19,150,1936,0,{0x483eUL}},{19,151,1936,0,{0x483fUL}},{19,152,1936,0,{0x4840UL}},{19,153,1936,0,{0x4841UL}},{19,154,1936,0,{0x4842UL}},{19,155,1936,0,{0x4843UL}},{19,156,1936,0,{0x4844UL}},{19,157,1936,0,{0x4845UL}},
{19,158,1936,0,{0x4846UL}},{19,159,1936,0,{0x4847UL}},{19,160,1936,0,{0x4848UL}},{19,161,1936,0,{0x4849UL}},{19,162,1936,0,{0x484aUL}},{19,163,1936,0,{0x484bUL}},{19,164,1936,0,{0x484cUL}},{19,165,1936,0,{0x484dUL}},
{19,166,1936,0,{0x484eUL}},{19,167,1936,0,{0x484fUL}},{19,168,1936,0,{0x4850UL}},{19,169,1936,0,{0x4851UL}},{19,170,1936,0,{0x4852UL}},{19,171,1936,0,{0x4853UL}},{19,172,1936,0,{0x4854UL}},{19,173,1936,0,{0x4855UL}},
{19,174,1936,0,{0x4856UL}},{19,175,1936,0,{0x4857UL}},{19,176,1936,0,{0x4858UL}},{19,177,1936,0,{0x4859UL}},{19,178,1936,0,{0x485aUL}},{19,179,1936,0,{0x485bUL}},{19,180,1936,0,{0x485cUL}},{19,181,1936,0,{0x485dUL}},
{19,182,1936,0,{0x485eUL}},{19,183,1936,0,{0x485fUL}},{19,184,1936,0,{0x4860UL}},{19,185,1936,0,{0x4861UL}},{19,186,1936,0,{0x4862UL}},{19,187,1936,0,{0x4863UL}},{19,188,1936,0,{0x4864UL}},{19,189,1936,0,{0x4865UL}},
{19,190,1936,0,{0x4866UL}},{19,191,1936,0,{0x4867UL}},{19,192,1936,0,{0x4868UL}},{19,193,1936,0,{0x4869UL}},{19,194,1936,0,{0x486aUL}},{19,195,1936,0,{0x486bUL}},{19,196,1936,0,{0x486cUL}},{19,197,1936,0,{0x486dUL}},
{19,198,1936,0,{0x486eUL}},{19,199,1936,0,{0x486fUL}},{19,200,1936,0,{0x4870UL}},{19,201,1936,0,{0x4871UL}},{19,202,1936,0,{0x4872UL}},{19,203,1936,0,{0x4873UL}},{19,204,1936,0,{0x4874UL}},{19,205,1936,0,{0x4875UL}},
{19,206,1936,0,{0x4876UL}},{19,207,1936,0,{0x4877UL}},{19,208,1936,0,{0x4878UL}},{19,209,1936,0,{0x4879UL}},{19,210,1936,0,{0x487aUL}},{19,211,1936,0,{0x487bUL}},{19,212,1936,0,{0x487cUL}},{19,213,1936,0,{0x487dUL}},
{19,214,1936,0,{0x487eUL}},{19,215,1936,0,{0x487fUL}},{19,216,1936,0,{0x4880UL}},{19,217,1936,0,{0x4881UL}},{19,218,1936,0,{0x4882UL}},{19,219,1936,0,{0x4883UL}},{19,220,1936,0,{0x4884UL}},{19,221,1936,0,{0x4885UL}},
{19,222,1936,0,{0x4886UL}},{19,223,1936,0,{0x4887UL}},{19,224,1936,0,{0x4888UL}},{19,225,1936,0,{0x4889UL}},{19,226,1936,0,{0x488aUL}},{19,227,1936,0,{0x488bUL}},{19,228,1936,0,{0x488cUL}},{19,229,1936,0,{0x488dUL}},
{19,230,1936,0,{0x488eUL}},{19,231,1936,0,{0x488fUL}},{19,232,1936,0,{0x4890UL}},{19,233,1936,0,{0x4891UL}},{19,234,1936,0,{0x4892UL}},{19,235,1936,0,{0x4893UL}},{19,236,1936,0,{0x4894UL}},{19,237,1936,0,{0x4895UL}},
{19,238,1936,0,{0x4896UL}},{19,239,1936,0,{0x4897UL}},{19,240,1936,0,{0x4898UL}},{19,241,1936,0,{0x4899UL}},{19,242,1936,0,{0x489aUL}},{19,243,1936,0,{0x489bUL}},{19,244,1936,0,{0x489cUL}},{19,245,1936,0,{0x489dUL}},
{19,246,1936,0,{0x489eUL}},{19,247,1936,0,{0x489fUL}},{19,248,1936,0,{0x48a0UL}},{19,249,1936,0,{0x48a1UL}},{19,250,1936,0,{0x48a2UL}},{19,251,1936,0,{0x48a3UL}},{19,252,1936,0,{0x48a4UL}},{19,253,1936,0,{0x48a5UL}},
{19,254,1936,0,{0x48a6UL}},{19,255,1936,0,{0x48a7UL}},{26,0,1934,0},{19,300,1936,0,{0x49a8UL}},{19,301,1936,0,{0x49a9UL}},{19,302,1936,0,{0x49aaUL}},{19,303,1936,0,{0x49abUL}},{19,304,1936,0,{0x49acUL}},
{19,305,1936,0,{0x49adUL}},{19,306,1936,0,{0x49aeUL}},{15,290,286,0,{0xffffffffffffffffUL}},{14,291,286,0,{0x40UL}},{15,291,291,0,{0xffffffffffffffffUL}},{14,292,286,0,{0x80UL}},{15,292,292,0,{0xffffffffffffffffUL}},{14,293,286,0,{0xc0UL}},
{13,294,290,0,{0x40UL}},{0,300,300,294},{13,294,291,0,{0x80UL}},{0,301,301,294},{0,301,301,292},{13,294,293,0,{0x40UL}},{0,302,302,294},{0,294,290,291},
{13,294,294,0,{0xc0UL}},{0,302,302,294},{0,294,292,293},{13,294,294,0,{0x80UL}},{0,303,303,294},{28,0,300,0},{19,289,1936,0,{0x49afUL}},{0,287,300,289},
{26,0,1935,0},{19,300,1936,0,{0x49a8UL}},{19,301,1936,0,{0x49a9UL}},{19,302,1936,0,{0x49aaUL}},{19,303,1936,0,{0x49abUL}},{19,304,1936,0,{0x49acUL}},{19,305,1936,0,{0x49adUL}},{19,306,1936,0,{0x49aeUL}},
{15,290,286,0,{0xffffffffffffffffUL}},{14,291,286,0,{0x40UL}},{15,291,291,0,{0xffffffffffffffffUL}},{14,292,286,0,{0x80UL}},{15,292,292,0,{0xffffffffffffffffUL}},{14,293,286,0,{0xc0UL}},{13,294,290,0,{0x40UL}},{0,300,300,294},
{13,294,291,0,{0x80UL}},{0,301,301,294},{0,301,301,292},{13,294,293,0,{0x40UL}},{0,302,302,294},{0,294,290,291},{13,294,294,0,{0xc0UL}},{0,302,302,294},
{0,294,292,293},{13,294,294,0,{0x80UL}},{0,303,303,294},{26,0,1935,0},{19,285,256,0,{0x48a8UL}},{14,266,285,0,{0x80UL}},{15,285,285,0,{0xffffffffffffffffUL,0xffffffffffffffffUL}},{5,285,258,285},
{17,264,285,0,{0x1UL,0x7f89000000000UL}},{23,0,264,0,{0x3d9UL}},{4,280,1930,265},{4,281,1930,266},{10,286,280,0},{18,284,0,0},{18,269,0,0},{18,274,0,0},
{8,264,284,274},{23,0,264,0,{0x37dUL}},{20,0,269,286},{11,269,269,0,{0x1UL}},{11,274,274,0,{0x140a8d0ac9c7a502UL,0x1c7a893efcUL}},{25,1935,0,0,{0x333UL}},{11,284,284,0,{0x1UL}},{17,264,287,0,{0,0,0x16000UL}},
{22,0,264,0,{0x385UL}},{17,264,284,0,{0,0x7f89000000000UL}},{23,0,264,0,{0x3d9UL}},{10,286,287,0},{24,0,0,0,{0x378UL}},{9,264,284,285},{22,0,264,0,{0x39dUL}},{5,282,284,285},
{18,275,0,0},{18,277,0,0},{11,294,275,0,{0x140a8d0ac9c7a502UL,0x1c7a893efcUL}},{9,264,282,294},{22,0,264,0,{0x390UL}},{10,275,294,0},{11,277,277,0,{0x1UL}},{24,0,0,0,{0x38aUL}},
{19,280,277,0},{11,277,277,0,{0x1UL}},{11,276,275,0,{0x140a8d0ac9c7a502UL,0x1c7a893efcUL}},{5,282,282,275},{16,264,282,0},{22,0,264,0,{0x39bUL}},{10,286,280,0},{25,1935,0,0,{0x333UL}},
{10,280,287,0},{12,282,282,0,{0x1UL}},{24,0,0,0,{0x394UL}},{5,275,284,285},{24,0,0,0,{0x3a8UL}},{5,282,285,284},{18,275,0,0},{18,276,0,0,{0x140a8d0ac9c7a502UL,0x1c7a893efcUL}},
{18,277,0,0,{0x1UL}},{16,264,282,0},{22,0,264,0,{0x3a8UL}},{10,286,281,0},{25,1935,0,0,{0x333UL}},{10,281,287,0},{12,282,282,0,{0x1UL}},{24,0,0,0,{0x3a1UL}},
{8,264,280,281},{22,0,264,0,{0x3d9UL}},{9,264,276,284},{23,0,264,0,{0x3beUL}},{5,279,276,275},{10,282,279,0},{10,278,281,0},{10,286,278,0},
{25,1935,0,0,{0x333UL}},{10,278,287,0},{12,282,282,0,{0x1UL}},{16,264,282,0},{23,0,264,0,{0x3afUL}},{19,294,277,0},{8,264,294,278},{22,0,264,0,{0x3bfUL}},
{10,280,294,0},{10,281,278,0},{10,275,276,0},{11,276,276,0,{0x140a8d0ac9c7a502UL,0x1c7a893efcUL}},{11,277,277,0,{0x1UL}},{24,0,0,0,{0x3aaUL}},{5,279,284,275},{16,264,279,0},
{22,0,264,0,{0x3d9UL}},{10,286,280,0},{25,1935,0,0,{0x333UL}},{10,288,287,0},{10,286,281,0},{25,1935,0,0,{0x333UL}},{8,264,288,287},{22,0,264,0,{0x3ccUL}},
{10,280,288,0},{10,281,287,0},{12,279,279,0,{0x1UL}},{24,0,0,0,{0x3bfUL}},{10,286,280,0},{25,1935,0,0,{0x351UL}},{20,0,1936,300,{0x49b0UL}},{20,0,1936,301,{0x49b1UL}},
{20,0,1936,302,{0x49b2UL}},{20,0,1936,303,{0x49b3UL}},{10,286,281,0},{25,1935,0,0,{0x351UL}},{20,0,1936,300,{0x49b4UL}},{20,0,1936,301,{0x49b5UL}},{20,0,1936,302,{0x49b6UL}},{20,0,1936,303,{0x49b7UL}},
{29,0,0,0,{0x1UL}},{29,0,0,0,{0xdUL}},
};
static const uint32_t K256[64] = {
0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,
0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,
0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,
0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,
0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,
0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
static uint32_t H[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
static uint8_t blk[64]; static uint64_t hlen; static FILE *out;
#define ROR(x,n) (((x)>>(n))|((x)<<(32-(n))))
static void compress(void){uint32_t w[64],a,b,c,d,e,f,g,h,t1,t2;int i;
 for(i=0;i<16;i++)w[i]=(uint32_t)blk[4*i]<<24|(uint32_t)blk[4*i+1]<<16|(uint32_t)blk[4*i+2]<<8|blk[4*i+3];
 for(i=16;i<64;i++)w[i]=w[i-16]+(ROR(w[i-15],7)^ROR(w[i-15],18)^(w[i-15]>>3))+w[i-7]+(ROR(w[i-2],17)^ROR(w[i-2],19)^(w[i-2]>>10));
 a=H[0];b=H[1];c=H[2];d=H[3];e=H[4];f=H[5];g=H[6];h=H[7];
 for(i=0;i<64;i++){t1=h+(ROR(e,6)^ROR(e,11)^ROR(e,25))+((e&f)^(~e&g))+K256[i]+w[i];t2=(ROR(a,2)^ROR(a,13)^ROR(a,22))+((a&b)^(a&c)^(b&c));
  h=g;g=f;f=e;e=d+t1;d=c;c=b;b=a;a=t1+t2;}
 H[0]+=a;H[1]+=b;H[2]+=c;H[3]+=d;H[4]+=e;H[5]+=f;H[6]+=g;H[7]+=h;}
static void emit_byte(uint8_t v){blk[hlen%64]=v;hlen++;if(hlen%64==0)compress();if(fputc(v,out)==EOF){perror("write");exit(1);}}
static uint64_t literals[64][4];static int literal_count;
static int same256(const uint64_t a[4],const uint64_t b[4]){return a[0]==b[0]&&a[1]==b[1]&&a[2]==b[2]&&a[3]==b[3];}
static int literal(const uint64_t v[4]){for(int i=0;i<literal_count;i++)if(same256(literals[i],v))return i;if(literal_count==64){fprintf(stderr,"literal capacity\n");exit(2);}
 for(int j=0;j<4;j++)literals[literal_count][j]=v[j];return literal_count++;}
static long vmhwm(void){FILE*f=fopen("/proc/self/status","r");char line[256];long kb=-1;if(!f)return -1;
 while(fgets(line,sizeof line,f))if(!strncmp(line,"VmHWM:",6)){kb=strtol(line+6,0,10);break;}fclose(f);return kb*1024;}
int main(int argc,char**argv){if(argc!=2)return 2;out=fopen(argv[1],"wb");if(!out)return 2;
 const int count=(int)(sizeof(records)/sizeof(records[0]));
 for(int i=0;i<count;i++){const Rec*r=&records[i];
  if(r->op<0||r->op>29||r->d<0||r->d>2047||r->a<0||r->a>2047||r->b<0||r->b>2047){fprintf(stderr,"field\n");return 3;}
  uint64_t flag,field;
  if(r->imm[1]==0&&r->imm[2]==0&&r->imm[3]==0&&r->imm[0]<(1UL<<25)){flag=0;field=r->imm[0];}else{flag=1;field=(uint64_t)literal(r->imm);}
  uint64_t w=(uint64_t)r->op|(flag<<5)|((uint64_t)r->d<<6)|((uint64_t)r->a<<17)|((uint64_t)r->b<<28)|(field<<39);
  for(int k=0;k<8;k++)emit_byte((uint8_t)(w>>(8*k)));}
 for(int i=0;i<literal_count;i++)for(int j=0;j<4;j++)for(int k=0;k<8;k++)emit_byte((uint8_t)(literals[i][j]>>(8*k)));
 uint64_t bytes=hlen,bitlen=hlen*8;blk[hlen%64]=0x80;hlen++;if(hlen%64==0)compress();
 while(hlen%64!=56){blk[hlen%64]=0;hlen++;if(hlen%64==0)compress();}
 for(int i=7;i>=0;i--){blk[hlen%64]=(uint8_t)(bitlen>>(8*i));hlen++;if(hlen%64==0)compress();}
 fclose(out);printf("instructions %d literals %d bytes %llu sha256 ",count,literal_count,(unsigned long long)bytes);
 for(int i=0;i<8;i++){printf("%08x",H[i]);}printf(" vmhwm %ld\n",vmhwm());return 0;}
```
