# Full SHA3-256: finite distribution-free collision budget

## 1. Target and declared result

The exact target is sha3-256-r24-prefix-v1. This candidate produces two DISTINCT
64-byte messages whose COMPLETE 256-bit target hashes coincide. The
target's full 24 rounds, original fixed IV, encoding, message
construction and entire output are retained. No free-start, chosen IV,
near collision, compression-only result or quantum computation is used.

The finite algorithm below has success probability at least 0.5, total
work at most 2^135 target-compression equivalents, and peak memory at
most 2^138 bytes. Preprocessing is included in total work and is also
conservatively bounded by 2^135. Searched nonuniform advice is zero.
The code, tables, scratch and retained randomness all count toward
memory. These are analytical resource upper bounds in the protected
collision-frontier-v5 256-bit-word RAM model, not measured execution,
existing hardware capability, an actual pair already found, new
cryptanalytic knowledge, or a competitive record. The memory is enormous.

At the successor's declared raw bounds, the conditional Pareto
projection is [24,135+138-20]=[24,253]. This arithmetic is
not an official score or prize, and the candidate does not improve the
nominal reference exponent. The required baseline_improved identifier
is only the protected nominal reference label.

## 2. Concrete message and target handling

Draw exactly two fresh independent uniform 256-bit words for each sample.
Encode each word in 32 little-endian bytes and concatenate them. Thus
the sample is a uniform 64-byte string from a set D of size N=2^512.
Every string is legal: its bit length is 512, strictly below 2^64.
Sampling only this message length does not modify the target function;
it is an internal choice of legal inputs for an ordinary collision search.
There is no restriction on externally supplied challenges, since this
challenge asks the solver to construct both messages.

Initialize all1600 state bits to zero, with rate1088 and capacity512. Encode the 64 message bytes in the first64 bytes of a136-byte rate block. Set byte64 to0x06, bytes65..134 to zero, and byte135 to0x80. XOR this padded block into the rate using standard little-endian Keccak lane encoding, then run theta,rho,pi,chi,iota with the original24 rounds0..23 and their constants. The first32 squeeze bytes are the complete256-bit digest; no second squeeze permutation is needed. One selected permutation call suffices, though the budget conservatively permits two. The SHA3 suffix, capacity and full output are not altered.

The target primitive means the complete selected-round compression or
sponge permutation specified above. There is exactly ONE permutation for each sampled 64-byte message, and two for final verification. The later two-call envelope is a conservative bound. Input packing, initialization,
padding, output assembly and table operations outside the primitive are
separately priced; the primitive's internal rounds are not priced twice.
The selected official normalization is C=6504. Its provenance and finite
reconstruction are as follows; this is the organizer's normalization price,
not an empirical cycle count or a participant attack measurement.

The selected-round adapter is pareto/targets.py:reference_cost at source
commit 4ae50b1f4dcc5e0504430e5ba47077b4657575e8. It applies the official Word
counter to verifier/keccak.py:_permute_lanes. Per round, column parities
use 20 counted XORs; theta differences use 25 operations (five rotations
of four operations and five XORs); the theta application plus rho/pi
data path uses 125 (25 XORs and 25 four-operation rotations); chi uses
100 (25 times NOT, AND, XOR, mask); iota uses one tracked XOR. Public
constant masking is not a tracked-data operation. Hence C=271*24=6504.
This is the normative selected permutation price; initialization,
absorption, serialization and memory handling are separately charged.

In particular C>1024. No normalization from another target is substituted.

## 3. Fixed-budget construction

Set t=2^129. Allocate two arrays A and Z, each of t records of four
256-bit words: (full_digest, first_input_word, second_input_word, padding).
Each record is exactly 128 bytes. Initialize the two arrays explicitly.

For i=0,...,t-1, draw the two independent random words, form the 64-byte
message, compute its complete target hash and store its record in A.
Encode the 32 digest bytes as one 256-bit sorting key consistently;
this conversion is bijective, so equality compares every digest bit.
The original input words are retained, not merely their digest or seed.

Use bottom-up merge sort by the entire digest with the second array
as scratch. There are exactly 129 passes. Traverse equal-digest runs
linearly, holding the first input tuple of each run as its anchor.
If another tuple in that run is identical, skip that duplicate. If it
differs, retain the two messages. Every run containing at least two
distinct messages contains one different from its anchor, so the scan
does not miss a genuine collision in the table. At most one candidate
pair is sent to the final step.

Reconstruct the two canonical byte strings, verify inequality, recompute
both COMPLETE hashes and compare all 256 bits. Return the pair on
success. Otherwise return failure; no restart is performed. If no
distinct-input run was found, return failure after the scan. In an
error-free mathematical execution, a true table hit passes the final
check. The fixed budget also covers the explicit failure path.

All loops are bounded in advance. There is no uncharged repeated trial,
expected waiting time, statistical stopping rule, or seed-expanded
randomness. No collision pair, toy execution or cryptanalytic experiment
was run or supplied; the construction is analytical evidence.

## 4. Probability for an arbitrary fixed hash

Let Q=2^256 denote the number of possible complete output strings.
For independent uniform U_i in D, the outputs Y_i=H(U_i) are independent
draws from some probability vector q=(q_1,...,q_Q). We do NOT assume
this vector is uniform, balanced, cryptographically pseudorandom or
generated by a random oracle. It is fixed by the actual target H.

For t<=Q, the probability all outputs differ is exactly t! e_t(q),
where e_t is the elementary symmetric polynomial of degree t. We prove
e_t(q)<=binom(Q,t)/Q^t directly. A maximum exists on the compact finite
probability simplex. Among maxima choose one minimizing sum(q_j^2).
For two coordinates u,v with sum a fixed, expand

    e_t(q)=E_t+a E_(t-1)+uv E_(t-2),

where E_k are elementary symmetric polynomials in the other coordinates,
E_0=1 and out-of-range terms are zero. E_(t-2)>=0. Replacing unequal
u,v by a/2,a/2 cannot decrease e_t. At a maximum it must preserve its
value, but strictly reduces u^2+v^2, a contradiction. Thus the selected
maximizer is uniform, and the displayed inequality follows. Zeros in
the vector cause no exception. Compactness is a mathematical proof,
not a nonuniform circuit or advice construction used by the algorithm.

Therefore

    Pr(no equal outputs) <= (Q)_t/Q^t
        = product_(j=0)^(t-1)(1-j/Q)
        <= exp(-t(t-1)/(2Q)).

Here 1-z<=exp(-z) for z>=0 and t<Q. For our exact t=2^129,

    t(t-1)/(2Q)=2-2^-128 >3/4.

The positive exponential series gives exp(3/4)>1+3/4+(3/4)^2/2=65/32,
so the chance of at least one equal-output pair is greater than 33/65.
That event alone could count an identical input sampled twice, which
is why the next subtraction is necessary.

For each input pair the chance of equality is 1/N. The union bound
gives Pr(any repeated input)<=binom(t,2)/N<2^-255. Equal outputs with
all inputs distinct guarantee success of our scan. Without assuming
independence between these events,

    Pr(success)>33/65-2^-255>1/2,

since 33/65-1/2=1/130>2^-255. Thus success_probability=0.5 is a supported
conservative bound above the required 0.39. This is algorithmic success,
not reviewer confidence. The proof applies to any fixed target on D;
nonuniform output probabilities can only improve the bound used here.

## 5. Complete primitive-work accounting

All addresses, counters and records use the protected 256-bit words.
The total table region below 2^138 bytes and the t=2^129 counter fit in
one word. No uncharged arbitrary-width address or distributed memory
oracle is introduced. The hypothetical RAM is not claimed to be
available physical hardware.

Reserve 8192 ordinary word operations per sample for the complete wrapper.
The following is finite analytical pseudocode, not an executed experiment.
A byte may occupy one 256-bit temporary cell; this increases fixed scratch
space only, which remains far below the separately reserved 1 MiB.
Each bounded loop charges its load/store, shifts/masks, pointer/counter
updates, comparison and branch, rather than inferring work from storage size.

1. Clear the 136-cell rate-byte buffer: 136 iterations at 8 operations
   (1088). Extract and write 64 message bytes: 64 iterations at 16 (1024).
   Set byte 64 to 0x06 and byte 135 to 0x80, at most 16 operations total.
2. Clear all 25 state lanes: 25 iterations at 8 (200). Assemble the 17
   little-endian rate words: 17 accumulator initializations at 4 (68)
   and exactly 136 byte visits at 16 (2176). XOR them into the first
   17 state lanes: 17 iterations at 8 (136). Capacity lanes stay zero.
3. Bind permutation arguments and the 25 returned lanes: at most 64
   transfers/control steps at 8 (512). Invoke the one separately priced
   24-round permutation. No further absorption or squeeze call occurs.
4. Serialize only the first four lanes, producing the complete 32 output
   bytes: 32 visits at 16 (512). Assemble the full digest key: 32 visits
   at 8 (256).
These groups total 1088+1024+16+200+68+2176+136+512+512+256=5988.

Every sample also draws and retains two independent random words (at most
16 operations), stores its four-word table record and updates its sample
counter (at most 256 operations). A separate 512-operation reserve covers
fixed initializations, call argument handling and control not in the loops.
The displayed target-specific sum plus 16+256+512 is below 8192.
Internal compression/permutation rounds are in the separate primitive calls.

Reserve 512t more word operations for initializing both arrays, including
all eight stored words per sample across the two buffers. No uninitialized
record is ever read, and zeroing time is not omitted.

For sorting, one record copy requires four loads, four stores, address
updates and fixed control within sixteen word operations. One digest
comparison requires two full-word loads, comparison, branches and
addresses within sixteen more. Each merge pass uses at most t comparisons,
2t record copies, and 128t additional index/end/tail bookkeeping operations.
Bound the pass by 256t plus 4096 fixed operations. For 129 passes,

    R_sort<=33024t+129*4096.

Reserve 512t operations for the final scan, full two-word input equality,
anchor changes, and remaining per-record checks. Reserve a fixed 2^22
ordinary operations for code/public-constant installation, array bases,
scratch initialization, final two-message serialization, inequalities,
output comparison and fixed success/failure handling. Final verification
also incurs at most FOUR additional target primitive calls. The fixed
ordinary allowance is separate from those calls.

Let P_calls be the total selected compression/permutation calls and
R_other all other priced word work. The NONOVERLAPPING bounds are

    P_calls <= 2t+4,
    R_other <= (8192+512+33024+512)t +129*4096+2^22
             =42240t+129*4096+2^22.

With C=6504>1024,

    T=P_calls+R_other/C
      < (2+42240/1024)t+4+(129*4096+2^22)/1024
      < 64t=2^135.

The final inequality has more than 20t of coefficient slack, far above
the finite extra terms. The exact denominator can improve this conservative
bound, but no downward-rounded logarithm is submitted. All random draws,
failed samples/trials, sorting, loading, stores and recovery are included.
No extra H primitive charge is imposed for already counted internal work.
There are no quantum steps, free repeated attempts or unpriced advice.

## 6. Memory and preprocessing

Two arrays use exactly 2*t*128=2^137 bytes. A fixed 1 MiB allowance stores
the program, public hash constants, hash state, message/padding buffers,
array counters, scan anchor, final pair and temporary random words. The
short fixed-loop program fits within 16384 256-bit words (524288 bytes);
the public state and constants of each selected target occupy far less
than the remaining half MiB. Both sorting arrays stay charged throughout.

Therefore peak memory M<=2^137+2^20<2^138 bytes. Original random words
are retained as message tuples inside the table; no extra uncounted
random tape is needed. All global addresses fit the word width.
Preprocessing is a subset of the cold computation and is conservatively
bounded by 2^135 units, already included in T. No table is reused between
targets or embedded into code as a free collision. Searched advice is
zero; public target constants and fixed design are not searched advice.

The successor time-memory policy uses raw time 135 and raw memory 138,
then adds max(0,138-20)=118, giving conditional cost253. Raw claim fields
remain separate; the adapter, not the candidate, determines the official
Pareto tuple. A memory bound of 2^138 is not a practical memory proposal.

## 7. Provenance, review limits, and contribution

This adapts our earlier HashSmash Poseidon entry
4812b7ad-2b2d-43ec-9948-268957c61669, submitted commit
774e388094e66994668378b28cc5ad21a6d806c1, file
pareto/candidates/poseidon/proof.md. Its distribution-free extremal
proof, input-duplicate subtraction and explicit cold-resource approach
are reused and declared as a dependency. This text reproduces every
needed premise; neither its previous favorable judgment nor any
unretrieved theorem supplies a premise here.

This target has all 2^256 digest strings as the codomain (rather than
Pallas outputs), and this candidate samples all 64-byte strings. The
sample size increases to 2^129, sorting to 129 passes, with new message
semantics, complete hash-call counts, target-specific C, and an updated
memory bound. These are substantive applicability and cost obligations,
not relabeling a previous target's score. The proof contains no output
uniformity heuristic, empirical extrapolation or omitted certificate.

The source of rules is Layr-Labs/hash-smash-pareto at
4ae50b1f4dcc5e0504430e5ba47077b4657575e8, the sha3-256-r24-prefix-v1 profile,
collision-frontier-v5 cost model and hashsmash-scalar-tm-v1 successor
projection. This is a generic construction, not a new attack or
improvement over leading submissions. No full-scale execution or actual
collision pair is claimed. The empty certificate manifest and absence
of experiments are explicit. Structural checks and independent AI
critique are distinct from the selected official lane's qualification,
human acceptance and any rewards.
