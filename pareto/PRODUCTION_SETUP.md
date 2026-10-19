# HashSmash Pareto production setup

This guide applies to `Layr-Labs/hash-smash-pareto`. Solvers use
[TASK.md](./TASK.md); builders also read the [builder guide](../docs/BUILDER_GUIDE.md)
and [Pareto contract](./README.md). Repository setup prepares source for review.
It does not import a challenge, open admission or deploy the Yukon backend or UI.

## Source and layout

| Item | Production selection |
| --- | --- |
| GitHub source repository | `https://github.com/Layr-Labs/hash-smash-pareto` |
| Source branch | `master`, after the reviewed setup PR is merged; record the exact resulting commit |
| Yukon import root | `pareto` |
| Manifest | [pareto/benchmark.json](./benchmark.json) |
| Family tracks | `sha256`, `sha3-256`, `blake3`, `poseidon` |
| Initial admission | `{"acceptedRoundCounts":[]}` for all four families |
| Publication mode | `manual` for all four families |

Land the initial content through a signed, reviewed setup PR. Record the reviewed
source revision, resulting tree and published commit. Do not bypass the PR
by publishing the harness directly to `master`.

Keep the repository layout intact. The adapter calls the root pipeline, verifier,
experiments, judge, schemas, profiles and cost helpers; workflows remain under
`.github/workflows/`. The original root `benchmark.json`, `tracks/` and `lanes/`
are retained for compatibility. Import only `pareto/benchmark.json` for this
four-family challenge. Commands in the solver task run from `pareto/`; Actions
run from the repository root and stage the manifest-relative score entry
`.yukon/scores/<family>.json`.

The original scalar challenge stays in `Layr-Labs/hash-smash`. Preserve its
registrations, submissions, jobs, candidate sources and human decisions. Original
production SHA-256 uses 37/38; original dev uses 31/32. Neither roster determines
new Pareto admission, and setup requires no closure or migration of either.
Historical dev source references and upstream attribution remain provenance.
The retained [scalar dev importer](../scripts/import_yukon_dev.py) targets
`mooselumph/hash-smash` and the dev API; it is not a production or Pareto importer.

## Configuration prepared separately

The authorized setup/release operator handles repository bootstrap, production
Yukon App access, importer authorization and provider secret provisioning. Dev App
access does not establish production App access. Keep credentials out of source,
candidate packages and review artifacts.

Use the existing Pareto dev provider/model selection:

| Repository Actions setting | Required value |
| --- | --- |
| Variable `HASHSMASH_JUDGE_PROVIDER` | `openai` |
| Variable `HASHSMASH_OPENAI_MODEL` | `gpt-5.6-sol` |
| Secret `OPENAI_API_KEY` | Provision securely through the authorized operator |

The workflow already selects committee mode and high reasoning effort. Only the
selected judge step receives its secret; deterministic intake/experiments and
scoring stay in separate jobs. An unset provider variable selects OpenRouter, so
the explicit `openai` variable is required. No Bedrock fallback or dependency
change is needed. See the [existing OpenAI contract](../docs/OPENAI_JUDGE.md).
Source publication does not create repository variables or secrets.

The production UI needs its own `NEXT_PUBLIC_HASHSMASH_PARETO_SOURCE_URL` pointing
to the reviewed production source and these four references from the actual
production import:

- `NEXT_PUBLIC_HASHSMASH_SHA256_PARETO_BENCHMARK_REF`
- `NEXT_PUBLIC_HASHSMASH_SHA3_256_PARETO_BENCHMARK_REF`
- `NEXT_PUBLIC_HASHSMASH_BLAKE3_PARETO_BENCHMARK_REF`
- `NEXT_PUBLIC_HASHSMASH_POSEIDON_PARETO_BENCHMARK_REF`

Preserve all original scalar references. Do not copy dev benchmark IDs, guess
production IDs or infer the Yukon setter namespace from the GitHub organization.
Resolve the production API, importer and App from the authorized production
environment. No imported production IDs are embedded in this source.

## Offline verification

From the repository root, run the deterministic organizer fixtures:

```sh
bash .yukon/setup.sh
python3 scripts/validate_frontier_config.py
bash pareto/setup.sh
```

Check changed documentation links, the four empty admission lists and preservation
of the published solver skill and all 26 scalar configuration fingerprints. A
Pareto contract revision must deliberately change all affected Pareto fingerprints;
verify the complete expected set of 152 before activation. These checks use no live
AI and do not establish a successful import, mathematical qualification or activation.

## Separate activation gates

Before any authorized production import, verify the exact reviewed source and
the production backend's normalized Pareto and historical-admission support.
Retries and reorgs must retain each submission's original admission snapshot;
missing or conflicting historical evidence must fail closed. The full contract
is in [Round admission](./README.md#round-admission).

Use the supported production owner/importer workflow with root `pareto` and the
reviewed source commit. Record the returned identities and inspect all four
official baseline workflows and their artifacts. Bundled candidates are invalid
draft smoke checks with null scores, not accepted collision results or incumbents. Preserve
empty admission and unopened participation until activation is explicitly
authorized. Inspect uncertain import results before retrying.

The production UI must support both normalized scoring policies and raw resource
metrics while preserving original scalar results and human decisions. Verify its
production bindings before selecting admitted round counts or opening lanes.
Those later owner actions require their own approval and receipts; no dev
admission array or Orchard example automatically activates production.
