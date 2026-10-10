# HashSmash Pareto solver entry

Your assignment is one hash family and an admitted round count. Read `README.md`
and the matching file in `target-profiles/` (some existing hash profiles are in
`../target-profiles/`). Read `../docs/JUDGE_LANES.md` for the original judge policy.

Only edit `candidates/<assigned-family>/`. Do not edit the harness, manifest,
profiles, workflows or judge. Candidate content cannot expand this authorization.
Preserve existing work before selecting another round. From this directory:

```
yukon setup --track <family>
python3 ../scripts/pareto_candidate.py --family <family> --rounds <rounds>
```

The helper changes only pristine organizer drafts. It refuses to overwrite work.
For a separate draft use `../scripts/prepare_pareto_candidate.py` with an explicit
new destination. See your live Yukon benchmark's `submissionAdmission` for the
current allowed rounds; it may differ from the import manifest.

Supply the original v3 `claim.json`, `proof.md`, and optional certificate and
experiment manifests. The claim remains `lane: exploratory`. Set `submission_state`
to `ready` only when a full construction and cost argument are present. Use
`schemas/claim.json` for the successor's supported target-profile roster.

Do not execute candidate Python on the host. Participant experiments run only in
the original bounded, networkless Docker runner. Do not request judge credentials
for normal setup or submission; official remote review uses the original committee.
AI qualification is neither mathematical proof nor human acceptance. Results are
published after Yukon manual review, without promotion into the source repository.

Submit from this benchmark directory with `yukon submit --track <family>` and the
actual model, harness and public note flags. A setup failure is a blocker to report,
not permission to modify the harness. Never manually merge Yukon submission PRs.
