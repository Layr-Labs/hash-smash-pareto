# HashSmash Pareto

Solvers start with [TASK.md](./TASK.md) and the
[HashSmash solver skill](../.agents/skills/hashsmash-solver/SKILL.md). Commands run
from this directory. The skill covers target semantics, round selection, total
cost, safe mechanical checks, optional critique and human-reviewed publication.

Production source is `Layr-Labs/hash-smash-pareto`; operators follow
[production setup](./PRODUCTION_SETUP.md). Source publication and live activation
are separate steps.

Four stable Yukon tracks: `sha256`, `sha3-256`, `blake3`, `poseidon`. Import this
repository with root directory `pareto`. Use a separate GitHub repository from
original HashSmash while both challenges are open: Yukon currently excludes two
open challenges backed by the same source repository, regardless of root directory.

The original scalar manifest, tracks, submissions and human decisions remain in
the original challenge. This successor imports no fabricated historical results.
The Yukon HashSmash UI reads both sources and keeps each candidate's provenance.

## Round admission

Each track has one mutable public setting:

```json
{"submissionAdmission":{"acceptedRoundCounts":[37,38]}}
```

Update it with the owner-authorized `PATCH /api/benchmarks/<id>` endpoint. The new
Yukon admission migration/API must be deployed first. An empty list admits no new
rounds. The manifest starts with empty lists pending organizer selection.

Changing this setting queues no jobs, creates no evaluation version and changes
no prior score or human decision. Yukon snapshots it when a new submission is
queued; the trusted intake checks that snapshot before experiments or AI review.
Idempotent retries and reorgs use each candidate's original admission snapshot,
including when validity must be evaluated again. Later admission changes apply
only to new submissions: they neither exclude previously allowed rounds nor
admit previously refused rounds on replay. Baselines omit admission. For older
submissions, Yukon must recover the snapshot from verified original intake jobs;
missing or conflicting evidence must stop the replay rather than use today's
setting. This requires Yukon's historical-admission support. The harness already
checks the supplied snapshot before experiments or AI review.
This is trusted intake rejection after upload, not archive parsing in the API.

Supported counts are SHA-256 1–64, SHA3-256 1–24, BLAKE3 1–7, and Orchard 0–56
partial rounds. All supported profiles are fixed at import. Adding any of these
counts requires only the admission update. Changing target semantics, cost model
or judge requires an explicit Yukon reorg; round admission never substitutes for
that operation.

## Scoring and judge

The tuple is `[rounds, normalizedTimeMemoryLog2]`: maximize rounds and minimize
`timeLog2 + max(0, memoryLog2Bytes - 20)` in every family, including Orchard.
Memory up to one MiB (1,048,576 bytes) adds zero; each doubling above that adds one.
Time remains total work in selected-round target-compression units; raw time and
memory remain separate reviewed metrics. Memory is part of the cost axis, with
no additional objective or tie-break. See the [pinned scoring definitions,
source attribution and transport contract](../scoring-policies/README.md).
The adapter calls the original intake, certificate and experiment gates, paired
committee, qualification aggregation, and score builder, then explicitly projects
the authenticated raw bounds at the Pareto boundary. Official reviews and advisory
packets use the Pareto-local mathematical-language prompt set in `pareto/judge/`.
The shared root judge, prompts, profiles, cost model and scalar fingerprints remain
unchanged. The successor claim schema only expands the trusted target roster.

SHA-256, SHA3 and BLAKE3 use Pareto-local copies of the original exact target
semantics and v5 cost model, with only the theoretical-collision terminology
normalized.
Their per-round normalization is computed using the original organizer reference
operation counter. The import baseline is an explicit invalid draft smoke check,
not an incumbent or human-accepted submission. Its null-score output still
identifies the normalized scoring policy; no resource measurements are fabricated.
Negative candidate decisions are valid Pareto artifacts; missing evidence/provider failures fail the execution.

## Orchard target

Only Orchard/Pallas P128Pow5T3: width 3, exponent 5, eight full rounds, at most 56
partial rounds. The two canonical field inputs occupy 64 little-endian bytes;
capacity is `2^65`. Return the entire first field element, encoded in 32 bytes.
Reject integers at least p; encoding aliases must never create collisions.

A reduced target runs full rounds 0–3, the first selected partial rounds starting
at index 4, and the deployed final full rounds 60–63. Constants and MDS never get
regenerated for a different count. This preserves the deployed permutation when
r=56. It is the Orchard Poseidon hash, not the complete nullifier construction.

Constants and 22 full-round vectors derive from `zcash/halo2`, tag
`halo2_poseidon-0.2.0`, `halo2_poseidon/src/{fp,test_vectors,p128pow5t3,lib}.rs`.
The constants file records its source SHA-256. The project is dual MIT/Apache-2.0;
see `UPSTREAM-NOTICE.md` for provenance and licenses.

The Orchard model is explicit Pallas field RAM (`orchard-field-ram-v2`),
with field add/subtract/multiply and 256-bit word operations at unit base cost.
`C=216+21*r` normalizes a selected permutation; inversion/exponentiation require
constituent operation accounting. Algebraic estimates use ω = 2.8, explicit
justified finite coefficients and all logarithmic factors. See the
[judge disclosure and accounting rules](./ORCHARD_ACCOUNTING.md). V2 retains
v1's operation prices and adds this estimate policy; the v1 file is historical.
This is separate from existing hash models.
The same paired committee reviews it with the Pareto-local prompt set. A later
Orchard judge or model change requires a Yukon reorg without migrating the legacy
challenge. Current
Yukon reorgs include all four tracks in the successor; score/validity scopes apply
to that batch. Admission-only round updates do not use this path.

## Rollout

This production source prepares fresh normalized initial evaluations with empty
admission for every family. Follow [production setup](./PRODUCTION_SETUP.md) for
the reviewed setup PR, source selection, separate configuration and activation
gates. Required provider selection is `openai` with model `gpt-5.6-sol`, matching
the existing Pareto dev settings; settings and access are provisioned separately.

Yukon objectives are immutable at registration: a reorg cannot rename the old
`timeLog2` objective. Historical time-only dev source and evidence at
`8c81a39eb987a3235fa38569435474671fed5b1b` retain their original meaning; they do
not describe the current normalized dev registration. Production uses its own
source repository and new identities. Existing submissions and human decisions
do not transfer automatically.

Before activation, the production backend must support normalized Pareto
evaluation and the historical-admission contract above. The combined UI must
support both normalized policies, preserve raw resource metrics and keep original
scalar results and references. This repository does not deploy either service or
change any lane's live state.

No production creation, import, judging or deployment is performed by local tests.
