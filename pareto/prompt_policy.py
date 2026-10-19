# Pareto-only prompt overlay for mathematical collision research.

from contextlib import contextmanager
from pathlib import Path

from verifier.io import canonical_json_bytes, sha256_bytes


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "pareto/judge/prompts"
STRATEGY_DIR = ROOT / "pareto/judge/strategies"
POLICY_DIR = ROOT / "pareto/judge/policies"
LANGUAGE_PROFILE_ID = "pareto-theoretical-collision-v1"


def qualification_policy_sha256() -> str:
    # Bind the effective Pareto prompt set without changing scalar policy files.
    shared = [ROOT / "judge" / name for name in (
        "paired_review.py", "lanes.py", "schema_validation.py", "prompts.py",
        "role_committee.py", "rescore.py", "output.py",
    )]
    shared += [ROOT / "schemas" / name for name in (
        "review-lanes-v1.schema.json", "claim-frontier-v3.schema.json",
        "experiment-manifest-v1.schema.json", "review-rescore-v2.schema.json",
    )]
    files = (
        shared
        + sorted(POLICY_DIR.glob("*.md"))
        + sorted(PROMPT_DIR.glob("*.md"))
        + sorted(STRATEGY_DIR.glob("*.md"))
        + [Path(__file__)]
    )
    return sha256_bytes(canonical_json_bytes({
        str(path.relative_to(ROOT)): sha256_bytes(path.read_bytes())
        for path in files
    }))


@contextmanager
def active_prompt_policy():
    # Route the existing judge loaders to Pareto copies for this bounded call.
    from judge import bedrock_adapter, lanes, openai_adapter, prompts

    bindings = (
        (prompts, "PROMPT_DIR", PROMPT_DIR),
        (prompts, "STRATEGY_DIR", STRATEGY_DIR),
        (lanes, "PROMPT_DIR", PROMPT_DIR),
        (openai_adapter, "OUTPUT_CONTRACT", PROMPT_DIR / "openai-responses-json-v1.md"),
        (bedrock_adapter, "SOL_OUTPUT_CONTRACT", PROMPT_DIR / "bedrock-sol-json-v1.md"),
    )
    previous = [(module, name, getattr(module, name)) for module, name, _ in bindings]
    try:
        for module, name, value in bindings:
            setattr(module, name, value)
        yield
    finally:
        for module, name, value in reversed(previous):
            setattr(module, name, value)
