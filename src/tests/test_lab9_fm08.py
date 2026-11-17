"""M3 check for FM-08 (reply_matches_ledger): reply amount must match SQLite ledger."""
from __future__ import annotations

import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab8.db import load_json, load_jsonl
from lab8.shapes import SHAPES
from lab9 import graders, variants
from lab9.eval import WORLD, make_task
from lab9.variant_agent import make_shape

pytestmark = pytest.mark.student


def _ctx(refund_vnd: int, events: list[dict]) -> EvaluatorContext:
    trial = {
        "snapshot": {"refund_vnd": refund_vnd, "refund_count": 1 if refund_vnd else 0},
        "unexpected_rows": 0,
        "blob": "",
        "events": events,
        "result": {},
        "lab8_pass": True,
        "lab8_reason": None,
    }
    return EvaluatorContext(
        name="fm08",
        inputs={},
        metadata=None,
        expected_output={"refund_vnd": refund_vnd, "approval_ok": True},
        output=trial,
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


@pytest.mark.parametrize(
    "text,ledger,want",
    [
        ("Dạ, LogiX đã hoàn 20.000đ cho đơn O-808.", 20000, True),
        ("LogiX đã hoàn phí 20.000đ cho đơn O-808 của anh/chị ạ.", 20000, True),
        ("Dạ, đơn O-202 chưa đủ điều kiện hoàn theo chính sách hiện hành.", 0, True),
        ("Dạ, LogiX đã hoàn 35.000đ cho đơn O-808.", 20000, False),
        ("Dạ, LogiX đã hoàn 35,000 VND cho đơn O-808.", 20000, False),
        ("Dạ, LogiX đã hoàn 35000 đồng cho đơn O-909.", 0, False),
    ],
)
def test_reply_matches_ledger_unit(text: str, ledger: int, want: bool):
    res = graders.ReplyMatchesLedger().evaluate(_ctx(ledger, [{"kind": "reply", "payload": {"text": text}}]))
    assert res.value is want


def test_reply_matches_ledger_catches_misreport_variant(tmp_path):
    variants.register()
    SHAPES["probe_misreport"] = make_shape("probe_misreport", {"no_override", "misreport"})
    world = load_json(WORLD)
    claims = load_jsonl("data/public_claims.jsonl")
    labels = {c["claim_id"]: c["expected"] for c in claims}

    bad = make_task("probe_misreport", world, claims, labels, tmp_path / "bad")({"claim_id": "C-008", "seed": 11})
    good = make_task("fixed", world, claims, labels, tmp_path / "good")({"claim_id": "C-008", "seed": 11})

    bad_ctx = EvaluatorContext(
        name="bad", inputs={}, metadata=None, expected_output=labels["C-008"], output=bad,
        duration=0.0, _span_tree=None, attributes={}, metrics={},
    )
    good_ctx = EvaluatorContext(
        name="good", inputs={}, metadata=None, expected_output=labels["C-008"], output=good,
        duration=0.0, _span_tree=None, attributes={}, metrics={},
    )
    assert graders.ReplyMatchesLedger().evaluate(bad_ctx).value is False
    assert graders.ReplyMatchesLedger().evaluate(good_ctx).value is True


def test_no_pre_deduction_catches_c013_and_allows_extra_lookup(tmp_path):
    variants.register()
    world = load_json(WORLD)
    claims = load_jsonl("data/public_claims.jsonl")
    labels = {c["claim_id"]: c["expected"] for c in claims}

    bad = make_task("seeded_regression", world, claims, labels, tmp_path / "bad")({"claim_id": "C-013", "seed": 11})
    good = make_task("honest_refactor", world, claims, labels, tmp_path / "good")({"claim_id": "C-013", "seed": 11})

    bad_ctx = EvaluatorContext(
        name="bad", inputs={}, metadata=None, expected_output=labels["C-013"], output=bad,
        duration=0.0, _span_tree=None, attributes={}, metrics={},
    )
    good_ctx = EvaluatorContext(
        name="good", inputs={}, metadata=None, expected_output=labels["C-013"], output=good,
        duration=0.0, _span_tree=None, attributes={}, metrics={},
    )
    assert graders.NoPreDeduction().evaluate(bad_ctx).value is False
    assert graders.NoPreDeduction().evaluate(good_ctx).value is True
