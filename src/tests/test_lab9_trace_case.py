"""M1 trace-case regression test for FM-03 (ticket_trust on C-002)."""
from __future__ import annotations

import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab8.db import load_json, load_jsonl
from lab9 import graders, variants
from lab9.eval import WORLD, make_task

pytestmark = pytest.mark.student


def _run_case(tmp_path, shape: str, claim_id: str, seed: int) -> tuple[dict, dict]:
    variants.register()
    world = load_json(WORLD)
    claims = load_jsonl("data/public_claims.jsonl")
    labels = {c["claim_id"]: c["expected"] for c in claims}
    trial = make_task(shape, world, claims, labels, tmp_path)({"claim_id": claim_id, "seed": seed})
    return trial, labels[claim_id]


def _ctx(trial: dict, label: dict) -> EvaluatorContext:
    return EvaluatorContext(
        name="trace_case_c002",
        inputs={},
        metadata=None,
        expected_output=label,
        output=trial,
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


@pytest.mark.parametrize("shape,seed", [("seeded_regression", 11), ("swarm", 55)])
def test_fm03_ticket_override_caught_on_c002(tmp_path, shape: str, seed: int):
    trial, label = _run_case(tmp_path, shape, "C-002", seed)
    ctx = _ctx(trial, label)
    assert graders.DbFactKept().evaluate(ctx).value is False
    assert graders.TrialPass().evaluate(ctx).value is False
    assert trial["snapshot"]["refund_vnd"] == 20000


@pytest.mark.parametrize("seed", [11, 55])
def test_fm03_fixed_shape_passes_c002(tmp_path, seed: int):
    trial, label = _run_case(tmp_path, "fixed", "C-002", seed)
    ctx = _ctx(trial, label)
    assert graders.DbFactKept().evaluate(ctx).value is True
    assert graders.TrialPass().evaluate(ctx).value is True
    assert trial["snapshot"]["refund_vnd"] == 0
    assert trial["result"]["status"] == "denied"
